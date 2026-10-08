# 모핑 진입점 전수와 격리 설계 4안 — A · A′ · B · C

> 관련 Issue: #281
> 기반 문서: [[215-1-w10-f-design-decision-review-snapshot]]
> **성격**: 조사·비교 문서. 채택 결정은 #281 본문이 소유한다.

## 배경 및 동기

RW 축이 먼저 갔고, 그 착지점이 모핑 축의 선택지를 규정한다.

#280 이 세우려던 `RwGate`(경로 키 게이트)는 철회됐다. RW 는 **세션 격리 + 전용 스레드 감금** 두 벌로 착지했다 — `DashRwSession` 이 공유를 걷고 `DashRwActor` 가 실행 지점을 스레드 1개로 확정한다. 게이트는 그 감금이 워커·GUI 양축을 한 벌로 덮으므로 폐기됐다(`eaa77a6`). `ThreadingContract` 7절의 "세 기제는 중복이 아니다" 박스가 그것을 규범으로 적었다.

**그래서 RW 가 실증한 것은 아래 B 형(감금)이고, A′ 형(감금 없는 인스턴스 격리)은 이 레포에 선례가 없다.** RW 도 감금을 벗지 못한 이유는 벤더 문서 근거 부재였다 — 등급 2 판정을 유지한 채 스레드 1개로 봉인했다(사내 소스 실측: `DashOpti_ReaderWriter` @ `f5d4c59`).

모핑은 그 문서 근거를 소스 감사로 직접 만들 수 있었다(2026-08-21, `DashOpti_Morphing`). **결론부터: 모핑 코드 자체는 깨끗하고, 배포본은 VTK SMP 전역을 통해 요건 ③이 깨진다.** 원인이 한 지점(`vtkSMPTools::LocalScope` 5곳)에 모여 있어 수정 범위가 작다.

본 문서는 셋을 한 자리에 모은다 — **진입점 전수** · **확인 요건 3개와 감사 결과** · **설계 4안**.

> **좌표 기준**
> - GUI: `refactor/async-execution` @ `eaa77a6`. **#290 병합은 완료됐다** — `feat/rw-actor` 4커밋을 rebase 로 흡수(`d875d02`·`393d7bc`·`17aed65`·`b837552`)하고 귀결 정리 1커밋(`eaa77a6`)을 붙였다. 본 문서의 모든 행 번호를 이 커밋에서 재실측했다.
> - 모핑 DLL: `DashOpti_Morphing` — **배포 0.0.4 의 실체는 `origin/Parallel-Processing` @ `6e13f45`** 다. `dev` @ `0392c14` 가 아니다(아래 "배포본 식별").
> - VTK: `DashOpti_Deps/vtk-9.4` (= `external/vtk-9.4`)

## 핵심 질문

1. 모핑 DLL 을 만지는 진입점은 전부 어디이고, 각각 어느 스레드·어느 인스턴스에서 도는가
2. RW 처럼 갈 수 있는가. 갈 수 있다면 감금까지 필요한가, 인스턴스 격리만으로 되는가
3. 그 판정에 필요한 확인은 무엇이고, 각각이 어느 안에서 필수인가 — **소스 감사로 답이 나왔다**

---

## 진입점 전수

### 게이트 호출부 — `MorphingGate::tryClaim()` 7곳

`MorphingGate::tryClaim` 로 grep 하면 21곳이다. 정의 1곳(`MorphingGate.cpp:32`)과 `tests/` 13곳을 빼면 프로덕션 호출부가 7곳이다.

| 진입점 | 위치 | 소유 함수 | 스레드 | #281 처분 |
|---|---|---|---|---|
| **1** | `controller/DashManager.cpp:510` | `RunMorphingForPreview:506` | GUI | 무접촉 (후속 과제) |
| **1b** | 같은 파일 `:561` | `RunLinearMorphingForPreview:559` | GUI | 무접촉 (후속 과제) |
| **2** | 같은 파일 `:497` | `RunVolumeMorphing:492` | GUI | 삭제 — Claim 이 호출부로 승격되어 래퍼 소멸 |
| **3** | 같은 파일 `:1013` | `PrepareDoeMorphingBatch:995` | GUI (준비) → 워커 (실행) | 무접촉 (#276 소관) |
| **4** | 같은 파일 `:912` | `MorphFromDoeDirectory:910` | — | **dead 삭제** (호출부 0건) |
| **5-Opt** | `view/DashOptimizerWidget.cpp:1481` | `onPreviewButtonClicked:1327` | GUI | 워커 이관 (Phase D) |
| **5-MR** | `view/DashModelRunnerWidget.cpp:1538` | `performMorphingAndAddToFileTable:1529` | GUI | 워커 이관 (Phase E) |

진입점 2 의 유일 호출부는 `view/DashGeometryParameterWidget.cpp:1364` 다(실측 확인). 그래서 QC 를 워커로 올리면 래퍼가 통째로 소멸한다.

### 사용자 행위 → 진입점 매핑

| 사용자 행위 | 진입점 | 지금 GUI 가 멈추는가 | 1회 모핑 횟수 | #281 |
|---|---|---|---|---|
| 3D 뷰 **실시간 형상 프리뷰** — 기즈모 드래그 · 스핀박스 값 변경 | 1 · 1b | 입력마다 1회분 (**길이 미측정**) | 1 | 무접촉 (후속 과제) |
| Geometry Parameter 탭 → **Save Design Variable** (메시 QC) | 2 | **멈춘다** — 모핑 2회 도는 동안 | 2 (Lower/Upper) | **Phase C** |
| Optimizer 탭 → **Preview 버튼** (산출 파일 생성 + 렌더) | 5-Opt | **멈춘다** — 템플릿 수만큼 | 템플릿 개수 | **Phase D** |
| ModelRunner 탭 → **Generate Input File** (소스 = Morphing) | 5-MR | **멈춘다** | 1 | **Phase E** |
| Analysis Launcher → **DOE 배치 실행** | 3 | **준비 구간만 멈춘다** | 샘플 수 | 무접촉 (#276) |

> **"프리뷰" 가 두 개다.** 첫 줄은 3D 뷰에 반투명 형상을 그리는 **실시간 프리뷰**(`MorphingPreview` · `UpdatePreviewMorphing`)이고, 셋째 줄은 Optimizer 탭의 **Preview 버튼**(산출 파일을 만들고 렌더)이다. 이름만 같고 다른 기능이다. 후속 과제로 미룬 것은 첫 줄뿐이고, 셋째 줄은 본 티켓 Phase D 다.

> **DOE 배치는 절반만 워커다.** 샘플 루프는 `morphingSerialPool` 워커지만 **준비 구간(`PrepareDoeMorphingBatch`)은 GUI 스레드**에서 스냅샷 DeepCopy 와 `.dat` 파싱을 한다. `model/DashJobRunner.cpp:2258` 이 그것을 "워커화 후 남는 유일한 GUI 정지원" 으로 적고 `:2268` 이 소요 시간을 `Morphing batch prepare took N ms on the GUI thread` 로 로그에 남긴다.

### DLL 실행 지점 — `Witness` 요구 4함수

`ThreadingContract` 게이트 절이 규정한다. 증명 없이 부르는 코드는 컴파일되지 않는다.

| 함수 | 선언 |
|---|---|
| `DashMorphingEngine::ExecuteMorphing` | `controller/DashMorphingEngine.h:40` |
| `DashMorphingEngine::RunVolumeMorphing` | 같은 파일 `:48` |
| `DashMorphingDoeExecutor::RunOneSample` | `controller/DashMorphingDoeExecutor.h:47` |
| `DashMorphingDoeExecutor::ExecuteOneSample` | 같은 파일 `:52` |

`ExecuteOneSampleConditionOnly`(`:70`)는 DLL 을 타지 않아 증명 대상이 아니다.

### 엔진 인스턴스 소유 현황

```
DashMR::OperatorMorph 인스턴스
├── DashManager::m_morphingEngine          프리뷰(1·1b) + QC(2) 가 공유  ← 문제 지점
│                                          QC 가 :1288 에서 빌려 쓴다
├── DashMorphingDoeExecutor::m_engine      배치(3). 배치 내 샘플들이 공유
└── 5-Opt · 5-MR                           이미 호출당 격리 — 아래 참조
```

**프리뷰와 QC 의 엔진 공유가 격리 설계의 첫 대상이다.** `ThreadingContract` 4절이 이미 per-Job 인스턴스를 규정했으나 배치·프리뷰 2 소유자만 열거하고 QC 축이 빠져 있다. #281 Phase B3 이 그것을 집는다.

**5-Opt·5-MR 은 이미 호출당 엔진을 뜬다.** `createMorphOperator`(`model/geometry/DashMorphingUtils.cpp:189`)가 만드는 `OperatorMorph` 는 `performMorphingAndExport` 의 **null 체크에만** 쓰이고, 실제 실행은 그 함수가 본문에서 새로 만드는 지역 `DashMorphingDoeExecutor`(`:289`)가 한다 — executor 가 `m_engine` 을 값 멤버로 소유하므로 호출마다 새 엔진이다. 즉 이 두 진입점은 A′ 가 요구하는 격리를 **오늘 이미 만족한다.** #281 Phase B1 이 그 죽은 인자 2개를 시그니처에서 지운다.

### 프리뷰 축의 호출 밀도

프리뷰가 다른 진입점과 다른 이유는 **호출 빈도**다.

| 경로 | 호출부 |
|---|---|
| `UpdatePreviewMorphing` | 13곳 — 기즈모 콜백 3(`DashHandlePickingInteraction.cpp:2033`·`:2057`·`:2353`) + 스핀박스 `valueChanged` 10(`DashGeometryParameterWidget.cpp`) |
| `MorphingPreview` | 7곳. 모핑을 타는 것은 `DashGeometryParameterWidget.cpp:794`·`:862`·`:888` 3곳이고, 나머지 4곳은 `MorphingPreview(false, …)` 로 끄기만 한다 |
| `PreviewCheck` | 소비 3곳 (`DashGeometryParameterWidget.cpp:1550`·`:1645`·`:1697`) |

기즈모를 끌면 마우스 이동마다 요청이 난다. 이 축을 큐잉 기반으로 바꾸면 **요청 병합·디바운스·결과 세대 폐기**가 함께 필요해진다 — 나머지 진입점(버튼 1회 = 실행 1회)에는 없는 문제다.

---

## 확인 요건과 감사 결과 (2026-08-21 · `DashOpti_Morphing` 소스 실측)

물음은 하나다 — **모핑 실행마다 `OperatorMorph` 를 새로 만들어 쓰면 실행들이 서로 간섭하지 않는가.**

### 배포본 식별 — `dev` 가 아니다

```
dev                          0392c14  Feat/morph engine draft (#121)
v0.0.4rc                     48378d7  10/20 수정된 병렬처리 코드          = dev + 1
origin/Parallel-Processing   3a1cf25  feat: Add configurable WendlandC2
                             6e13f45  feat: add custom marching plane     ← 배포 0.0.4 의 실체
```

`external/DashOptiMorphing-0.0.4/include` 의 **공개 헤더 16개가 `6e13f45` 와 전부 바이트 일치**한다(CRLF 정규화 후 diff 0, 재검증 완료). `6e13f45` 로 좁히는 것은 `Handle/MarchingPlaneBound.h` 다 — 그 커밋이 추가한 파일이고 직전 `3a1cf25` 에는 없는데 배포본에는 있다. `WendlandFactory.h`(= `CreateWendlandC2Kernel`)의 존재는 `dev` 라인을 배제하는 근거이지 커밋을 특정하는 근거가 아니다.

> **식별 범위의 한계** — 일치를 확인한 것은 공개 헤더뿐이다. `RBFMorphOp.hpp` 는 내부 헤더라 배포본에 없고, `DashOptiMorphing.dll` 바이너리를 그 커밋의 빌드 산물과 대조하지는 않았다. 아래 ③ 판정은 "배포본이 `6e13f45` 소스로 빌드됐다" 를 전제한다.

**두 라인의 판정이 갈리므로 어느 쪽을 보는지가 중요하다.**

### 요건 3개와 판정

| # | 요건 | 왜 묻는가 | `dev` `0392c14` | **배포 0.0.4** `6e13f45` |
|---|---|---|---|---|
| ① | 프로세스 전역 가변 상태 없음 | 있으면 인스턴스를 나눠도 그 전역을 통해 이어진다. 직렬화로는 레이스만 막히고 실행 간 누수는 안 막힌다 — 이전 실행의 값이 다음 결과에 섞이면 크래시 없는 오답이라 제일 위험하다 | **통과** | **조건부 통과** — 순차 실행에서는 누수 없음 |
| ② | `thread_local`·스레드 친화 자원 없음 | 없어야 인스턴스를 워커에서 만들고 쓸 수 있다. `QThreadPool` 은 스레드를 교체하고 GUI 프리뷰와 번갈아 쓰므로, 직렬화해도 스레드 신원은 계속 바뀐다 | **통과** | **통과** |
| ③ | 다른 인스턴스를 두 스레드에서 동시에 `Morph()` 해도 됨 | 프리뷰가 GUI 스레드에 남고 게이트가 없으면 GUI × 워커 동시 실행이 정상 경로가 된다 | **통과** | **실패** |

②는 경험적으로도 이미 통과 중이었다 — 배치 모핑이 `morphingSerialPool` 워커에서 DLL 을 부르고(`model/DashJobRunner.cpp:1406`) 프리뷰는 GUI 스레드에서 부르므로, 두 스레드가 번갈아 쓰는 상태가 지금 프로덕션이다.

③은 ①·②와 달리 **직렬 풀로 미룰 수 있는** 질문이다. `morphingSerialPool` 은 `maxThreadCount = 1`(`controller/async/ThreadPools.cpp:14`)이라 워커끼리 동시 실행이 없고, 나중에 값 한 줄로 풀 수 있다. 단 **프리뷰가 GUI 스레드에 남고 게이트가 없으면 미룰 수 없다** — 직렬 풀은 워커끼리만 막지 GUI 진입점을 못 막기 때문이다. 그래서 ③은 A′ 에서만 필수가 된다.

### ③ 실패의 실체 — `vtkSMPTools::LocalScope`

배포 라인의 `RBFMorphOp.hpp` 가 `LocalScope` 을 **5곳**(`:412`·`:433`·`:457`·`:482`·`:517`)에서 부른다. `dev` 에는 0건이고 `vtkSMPTools::For` 를 직접 부른다 — 즉 **병렬처리 커밋(`48378d7`)이 전역 쓰기를 새로 들여왔다.**

```cpp
// VTK 9.4  SMP/Common/vtkSMPToolsAPI.h:78-93
template <typename Config, typename T>
void LocalScope(Config const& config, T&& lambda)
{
  const Config oldConfig(*this);   // 프로세스 전역 싱글턴의 현재 설정을 포착
  *this << config;                 // 전역을 덮어쓴다
  try { lambda(); } catch (...) { *this << oldConfig; throw; }
  *this << oldConfig;              // 복원
}
```

`vtkSMPToolsAPI` 는 `GetInstance()` 싱글턴(`:42`)이고 헤더에 `std::atomic`·뮤텍스·`thread_local` 이 0건이다. `operator<<`(`:245`)는 enum 대입이 아니라 `Initialize()`·`SetBackend()`·`SetNestedParallelism()` 3함수 호출이고, 셋 다 out-of-line 이라 헤더로는 부작용 범위를 확정할 수 없다. 직접 노출된 멤버는 `:256` `ActivatedBackend`(enum) · `:261` `DesiredNumberOfThread`(int) 다.

**값 발산이 원인이 아니다.** 5 호출부가 모두 `Config{numThreads, "STDThread", true}` 를 넘기고, GUI 의 두 설정 지점(`controller/DashMorphingEngine.cpp:53` · `model/geometry/DashMorphingUtils.cpp:195`)이 모두 `SetSolverNumberOfThreads(16)` 이라 인스턴스 간 config 가 동일하다. 깨지는 것은 순서와 동시성이다.

| # | 파손 | 기제 |
|---|---|---|
| 1 | **데이터 레이스** | `operator<<` 의 쓰기와 `For` 의 `ActivatedBackend` 읽기(`:99`)가 무동기다. 값이 같아도 UB이고, out-of-line 3함수의 내부 상태까지 걸린다 |
| 2 | **복원 순서 역전** | 먼저 진입한 A 가 먼저 나가면 아직 도는 B 밑에서 전역이 **기본 config 로 돌아간다** |
| 3 | **설정 누출** | 나중에 진입한 B 가 A 의 config 를 `oldConfig` 로 포착하므로, 마지막 종료가 기본값을 복원하지 않고 `{16, "STDThread", true}` 를 남긴다 |

**인스턴스가 독립이어도 이 전역을 통해 이어진다.** 배포 0.0.4 에서 A′ 는 성립하지 않는다.

### 함께 드러난 것 — MKL Pardiso 가 실제로 실행 경로에 있다

`MT_DIRECT` 솔버는 `Eigen::PardisoLDLT<SparseMat>`(`OperatorRBFMorph.cpp:12` `#include <Eigen/PardisoSupport>` · `:157`)이고, GUI 의 두 설정 지점이 모두 `SetSolverMethod(MT_DIRECT)` 다. 빌드도 MKL 을 필수로 건다 — `DashOptiMorphing/CMakeLists.txt:64` `find_package(MKL CONFIG REQUIRED)` · `:76` `MKL::MKL` · `:91` `copy_intel_mkl_dlls`. **`bin/` 의 MKL DLL 은 딸려온 것이 아니라 빌드가 의도적으로 복사한 것이고, 코드가 쓴다.**

`omp_*`·`mkl_*`·`setNbThreads`·`EIGEN_USE_MKL` 토큰이 0건인 것은 사실이지만, 그것은 **코드가 MKL 스레드 수를 쓰지 않는다**는 뜻이지 MKL 을 안 쓴다는 뜻이 아니다. 귀결은 둘이다.

- **MKL/OpenMP 스레드 수는 프로세스 전역이고 기본값으로 남는다.** 동시 `Morph()` 는 Pardiso 팀 2벌을 전폭으로 띄워 **oversubscription** 이 된다. 성능 문제이지 오염은 아니다.
- **Eigen 래퍼 쪽 공유 상태는 없다.** `m_pt`·`m_iparm`·`m_perm` 이 전부 인스턴스 멤버이고 `static` 은 무상태 디스패치 2개뿐이다(`external/eigen-3.4.0/Eigen/src/PardisoSupport/PardisoSupport.h:46`·`:58`). Pardiso 호출은 평범한 직렬 `for` 안에 있어(`OperatorRBFMorph.cpp:219-258`) SMP 병렬 구역과 겹치지도 않는다.

남는 물음은 **MKL Pardiso 자체가 서로 다른 핸들에 대한 동시 호출을 허용하는가** 다. 바이너리라 소스로 확정할 수 없어 아래 "남는 유보" 로 넘긴다. `SetSolverNumberOfThreads` 로는 이 축을 제어할 수 없다 — 그 값이 솔버에 닿지 않는다(다음 항).

### 통과한 항목 — 모핑 코드 자체는 깨끗하다

| 확인 | 결과 |
|---|---|
| `thread_local` | 두 라인 다 **0건** |
| 동기화 primitive | 실사용 0건. 유일한 흔적이 `RBFMorphOp.hpp:6` 의 미사용 `#include <mutex>`("필요할 수 있음" 주석 동반) — 방어가 없다는 뜻이지 그 자체가 문제는 아니다 |
| namespace-scope 가변 전역 | **0건** (`using SparseMat` 은 타입 별칭) |
| 함수 로컬 `static` 가변 | `KernelFunctionRegistry::GetInstance`(`Operator/KernelFunctionRegistry.h:18`) 1건뿐 |
| **registry 도달 여부** | **미도달 확정** — `CreateWendlandC2Kernel` 은 `std::make_unique<WendlandC2WithRadius>(radius)` 한 줄이다(`WendlandFactory.cpp:27-30`). registry 는 우리 경로에서 완전히 dead 이므로 그 무동기 `unordered_map` 은 위험이 아니다 |
| `OperatorMorphImpl` | 전부 값 멤버 — `kernelFn` · `usePolynominal` · `numThreads` · `numMathModels` · `method` · `mathModels`(`OperatorRBFMorph.cpp:194-204`) |
| `SetSolverNumberOfThreads` | 대입 자체는 인스턴스 멤버(`mImpl->numThreads`)다. 다만 **유효 소비자가 `LocalScope` 의 Config 하나뿐**이라 그 효과는 전역 쓰기다. 솔버 쪽 인자(`CreateSolver(method, numThreads)`, `:247`)는 **빈 `preComputeCallback` 람다에 캡처되고 끝난다**(`:158-159`) — Pardiso 스레드 수에 반영되지 않는다 |
| `vtkSMPThreadLocal` | `RBFMorphOp.hpp:29`. 병렬 구역 내부 TLS 로 `For` 종료 시 수확되므로 호출 간 잔류 없음 |

**부수 해소** — `SetKernelFunction` 은 `kernelFn->GetCallable()` 로 `std::function` 을 **값 복사**하고(`OperatorRBFMorph.cpp:278`) 람다가 반경을 값 캡처한다(`WendlandFactory.cpp:9` `const double R = mRadius`). 따라서 `DashMorphingUtils.cpp:192-193` 의 지역 `unique_ptr` 커널 댕글링 의심은 **무해**하다 — 정리 대상이지 버그가 아니다.

### 남는 유보

| 항목 | 상태 |
|---|---|
| `vtkSMPThreadPool` 동시 `For` | 싱글턴(`SMP/STDThread/vtkSMPThreadPool.h:172`)이지만 `std::unique_lock<std::mutex>`(`:158`)을 들어 동시 `For` 를 설계상 지원하는 것으로 **보인다.** 확정하지 않았다 |
| MKL Pardiso 동시 호출 | 서로 다른 핸들에 대한 동시 호출 허용 여부를 소스로 확정할 수 없다(바이너리). Eigen 래퍼 쪽 공유 상태는 없음이 확인됐다 |
| MKL/OpenMP oversubscription | 동시 `Morph()` 시 성능 격하가 예상되나 미측정. `SetSolverNumberOfThreads` 로는 제어 불가 |

#280 의 RW 감사도 VTK 전역을 유보로 남겼고, 오늘 이미 모핑 워커가 VTK·MKL 을 만지므로 셋 다 **신규 위험이 아니다** — A′ 가 새로 여는 것은 "동시" 뿐이다.

### 수정안 — ③을 여는 방법

원인이 한 지점이라 범위가 작다. 다만 **VTK 9.4 의 SMP API 에는 `For` 단위 스레드 수 인자가 없다** — 전역 config 를 거치는 길뿐이다. 따라서 어느 안을 택하든 `SetSolverNumberOfThreads` 는 SMP 루프 제어력을 잃는다(솔버 쪽에는 애초에 닿지 않았다).

| 안 | 내용 | 대가 |
|---|---|---|
| **A. 시동 시 1회 설정** (권장) | `LocalScope` 5곳을 걷고 SMP config(`{N, "STDThread", true}`)를 프로세스 시동 시 GUI 스레드에서 한 번만 설정 | 동시 쓰기가 사라진다. **SMP 스레드 수가 프로세스 전역이 된다** — 인스턴스별 제어 상실 |
| B. `dev` 방식 복귀 | `vtkSMPTools::For` 직접 호출 | A 와 같은 제어 상실. 추가로 STDThread backend·nested parallelism 지정도 잃어 **VTK 기본 backend 로 돈다** |
| C. 현행 유지 | — | 모핑에 프로세스 전역 배타가 영구히 필요하다. `MorphingGate` 존치 |

**A 와 B 의 차이는 스레드 수 제어가 아니라 backend 고정 여부다.** 병렬처리 커밋이 의도한 것 중 A 가 지키는 것은 backend·nested 설정이고, 잃는 것은 인스턴스별 스레드 수다 — 오늘 두 설정 지점이 모두 `16` 이라 실질 손실이 없다. A 면 ③이 통과하고 A′ 가 열린다. 수정 범위는 `RBFMorphOp.hpp` 5줄 + 초기화 1곳이다.

### 요건 × 설계안 필요 매트릭스

| 요건 | A (현행) | **A′** | B | C |
|---|---|---|---|---|
| ① 프로세스 전역 가변 상태 없음 | 현행 전제 | **필수** | **필수** | **필수** |
| ② `thread_local`·스레드 친화 없음 | 현행 전제 | **필수** | 불요 (감금이 해결) | 불요 |
| ③ 다른 인스턴스 동시 실행 안전 | 불요 (게이트) | **필수** | 불요 (한 스레드) | 불요 |

"현행 전제" = 지금도 그 가정 위에서 돌고 있어 새 위험이 아니라는 뜻이다. **actor(B·C)가 지워주는 것은 ②뿐이다** — ①은 감금과 무관하게 남는다.

---

## 설계 4안

### 표 1 — 진입점이 어디서 도는가

| 진입점 | 지금 | A | A′ | B | C |
|---|---|---|---|---|---|
| **1·1b** 실시간 프리뷰 | GUI · **공유 엔진** | GUI · 자기 엔진 | GUI · 자기 엔진 | **actor 큐** (blocking) | **actor 큐** (비블로킹) |
| **2** QC | GUI · 프리뷰 엔진 차용 | **워커** · 자기 엔진 | **워커** · 자기 엔진 | actor 큐 | actor 큐 |
| **5-Opt** Preview 버튼 | GUI · per-call 인스턴스 | **워커** | **워커** | actor 큐 | actor 큐 |
| **5-MR** Generate | GUI · per-call 인스턴스 | **워커** | **워커** | actor 큐 | actor 큐 |
| **3** DOE 배치 | 준비 GUI · 샘플 워커 | 동일 | 동일 (+ 풀 병렬 가능) | 샘플이 actor 큐 | 샘플이 actor 큐 |
| **4** dead | — | 삭제 | 삭제 | 삭제 | 삭제 |

**4안이 아니라 2배치 × 2변종이다.** A 와 A′ 는 진입점 배치가 **완전히 같고** 배제 기제만 다르다. B 와 C 도 배치는 같고 **프리뷰의 호출 형태**만 다르다. 진입점별로 갈리는 것은 **프리뷰 하나뿐**이고, 나머지 넷은 "워커냐 actor 큐냐" 2갈래로만 움직인다.

### 표 2 — 기제가 존재하는가

| 기제 | 지금 | A | A′ | B | C |
|---|---|---|---|---|---|
| `MorphingGate` | 증명형 (`Witness` 4함수) | 유지 | **철거** | 축소 존치 | **철거** |
| `morphingSerialPool` | `maxThreadCount = 1` | 1 | **N** | 1 (배제 역할 상실) | 1 (동일) |
| `DashMorphingActor` | 없음 | 없음 | 없음 | **신설** | **신설** |
| 엔진 인스턴스 분리 | 프리뷰·QC 공유 | Phase B3 | 동일 | 동일 | 동일 |

**엔진 인스턴스 분리는 4안 공통이다.** A 의 Phase B3 이 하는 일이고 어느 안으로 가도 필요하다 — A 로 착수하면 다른 안의 선행이 함께 쌓인다.

B·C 에서 `morphingSerialPool` 은 살아남지만 **배제 근거를 잃는다** — actor 스레드가 이미 직렬화하므로, 풀은 DLL 을 안 타는 부분(파일 IO · 파싱)을 돌리는 자리로만 남는다.

### 표 3 — 게이트가 하던 네 가지 몫

게이트가 헷갈리는 이유는 한 객체가 넷을 겸하기 때문이다.

| 게이트의 몫 | A | A′ | B | C |
|---|---|---|---|---|
| ⒜ **배제** — 동시 DLL 진입 금지 | 게이트 | **인스턴스 격리**가 대신 | actor 감금이 대신 | actor 감금이 대신 |
| ⒝ **거부** — 진행 중 새 요청 | 게이트 | **불요** (동시 허용) | **게이트 존치** — 프리뷰가 큐에서 대기하면 안 되므로 | latest-wins 병합 |
| ⒞ **표시** — `busy()` 소비자 3곳 | 게이트 | 진행 상태 소스 신설 | 게이트 | 진행 상태 소스 신설 |
| ⒟ **중복 실행 방지** | 게이트 + 버튼 비활성 | 버튼 비활성 | 게이트 | 요청 병합 |

`busy()` 소비자 3곳 = `DashMainWindow:1943`(스피너·상태바) · `DashGeometryParameterWidget:102`(탭 비활성) · `DashAnalysisLauncherWidget:73`(Start 버튼).

**B 에서만 게이트가 반쯤 남는다.** actor 가 ⒜ 를 가져가지만 ⒝ 를 못 가져간다 — 큐잉은 거부가 아니라 대기이고, 프리뷰가 배치 샘플 뒤에서 대기하면 GUI 가 그만큼 멈춘다. C 는 프리뷰를 비블로킹으로 만들어 그 문제를 없애므로 게이트가 완전히 사라진다.

### 한 줄 요약

| 안 | 프리뷰 | 배제를 무엇이 하는가 | 게이트 | 감사 결과 |
|---|---|---|---|---|
| **A** | GUI 동기 | 게이트 | 증명형 유지 | **즉시 가능** |
| **A′** | GUI 동기 | **인스턴스 격리** | 철거 | **요건 ③ 실패 — DLL 수정 선행** |
| **B** | actor 큐 · 대기 | actor 감금 | 프리뷰 거부용으로 축소 | 통과 |
| **C** | actor 큐 · 비동기 | actor 감금 | 철거 | 통과 |

**감사가 판을 바꿨다.** A′ 는 배포 0.0.4 에서 그대로는 성립하지 않고 모핑 DLL 수정이 선행이다. B·C 는 감사를 통과한다 — actor 감금이 `LocalScope` 의 동시 호출을 애초에 만들지 않기 때문이다.

### 용어 — actor 큐 vs 스레드 풀

| | 직렬 풀 (`morphingSerialPool`, max=1) | actor (전용 `QThread`) |
|---|---|---|
| **누가 큐에 서나** | 워커 Job 만. **GUI 동기 호출은 풀 밖** | **전원** — GUI 호출도 마샬링되어 같은 큐에 선다 |
| GUI 진입점 배제 | **못 한다** | **한다** |
| 스레드 신원 | **바뀐다** (유휴 스레드 만료 후 재생성) | **고정** |
| 직렬화 단위 | **Job 전체** — A 가 끝나야 B 시작 | **호출 1건** — DLL 호출만 배타 |
| 실행 위치 | task 전부가 워커에서 | DLL 호출만 actor 에서 |

첫 줄이 결정적이다 — **풀은 워커끼리만 직렬화하고 actor 는 GUI 포함 전원을 직렬화한다.** `MorphingGate` 가 존재하는 이유가 "풀이 못 덮는 GUI 진입점" 이고 actor 는 그 구멍을 없앤다. 셋째 줄은 요건 ②와 연결된다 — 풀은 스레드가 교체되므로 `thread_local` 이 있으면 깨지고 actor 는 고정이라 무관해진다.

넷째 줄에 함정이 있다. actor 는 **호출 단위**로 직렬화하므로 A 의 `SetInitialConfiguration` → `Morph()` 사이에 B 의 호출이 끼어든다. 인스턴스가 다르면 상태가 각자 pimpl 에 쌓여 안전하지만 **인스턴스를 공유하면 2콜 프로토콜이 깨진다.** 즉 **actor 도 per-instance 를 요구한다** — 감금이 인스턴스 분리를 대신하지 못한다.

### 용어 — blocking vs 비블로킹

```
blocking (B)      호출자 ──[요청]──▶ actor 스레드
                        ◀─[결과]───   호출자는 이 동안 정지
                  호출부 코드 0줄 변경. 동기 함수처럼 보인다

비블로킹 (C)      호출자 ──[요청]──▶ actor 스레드     호출자는 즉시 반환
                        ◀─[시그널]──  완료 슬롯이 결과를 받는다
                  호출부 전면 재작성. 반환값 쓰던 코드가 콜백 구조로
```

| | blocking (B) | 비블로킹 (C) |
|---|---|---|
| 호출부 변경 | **0줄** — rw-actor 가 택한 이유 | 프리뷰 호출부 **16곳 치환** |
| GUI 프리즈 | **있다** — 큐 앞의 작업만큼 | 없다 |
| 요청 누적 | **안 쌓인다** — GUI 가 블록돼 새 입력을 못 받는다 | **쌓인다** |
| 스톨 표시 | 없음 | **생긴다** — 병합·디바운스 필요 |
| 결과 세대 | 문제 없음 | **생긴다** — 늦게 온 결과 폐기 필요 |
| 취소 | 불가 | latest-wins 로 앞선 요청 폐기 |

**시간 축 문제 넷을 B·C 가 나눠 갖는다** — B 는 프리즈만, C 는 나머지 셋만. A·A′ 는 큐를 안 만들어 넷 다 없다.

### A — 현행 계획 (#281 본문)

모핑 3진입(2 · 5-Opt · 5-MR)만 `morphingSerialPool` 워커로 올리고, `MorphingGate` 는 증명형 그대로 둔다. 프리뷰는 GUI 스레드에 남아 공유 엔진을 쓴다(Phase B3 이 QC 만 떼어낸다).

확인 요건이 없어 **지금 바로 착수 가능**한 유일한 안이다. 대가는 게이트 배관이 그대로 남는 것 — 215-1 이 열거한 #281 결함 ⑴(토큰 스코프) · ⑶(`Reservation` 수명) · ⑹(Claim 해제 시점)이 전부 여기서 나온다.

### A′ — 인스턴스 격리만 (actor 없음)

**넷 중 가장 좋지만 지금은 성립하지 않는다.** 요건 ③이 배포 0.0.4 에서 실패하고, 그 해소가 우리 레포 밖 작업이다.

구조는 이렇다. 프리뷰가 자기 엔진 인스턴스를 들고 GUI 스레드에서 계속 돈다. QC · Optimizer · ModelRunner · 배치는 각자 인스턴스로 워커에서 돈다. **게이트가 없다.**

```
지금  프리뷰 ─ 게이트 거부 ─ 워커 모핑          동시 실행이 애초에 없다
A′    프리뷰 ────────────── 워커 모핑          동시 실행이 정상 경로다
      GUI 스레드 / 인스턴스 P   워커 스레드 / 인스턴스 W
```

좋은 이유는 셋이다. actor 라는 새 클래스가 없다. 프리뷰가 큐에 안 서니 시간 축 문제 넷이 아예 생기지 않고 — B 가 지는 프리즈도, C 가 지는 스톨 표시 · 큐 누적 · 결과 세대도 없다 —, Follow-up ⑴ 의 요청 병합·디바운스도 불필요해진다. 코드도 늘지 않는다 — **A′ = A + 게이트 철거 + 풀 병렬화**이고, 프리뷰가 엔진을 단독 소유하는 것은 이미 Phase B3 이 하는 일이며 5-Opt·5-MR 은 이미 호출당 격리다.

막는 것은 `vtkSMPTools::LocalScope` 5곳이다. 그것이 VTK 전역 싱글턴을 무동기로 write-restore 하므로, 프리뷰(GUI 스레드)와 워커가 동시에 `Morph()` 하면 인스턴스가 독립이어도 그 전역을 통해 깨진다. 따라서 A′ 는 **모핑 DLL 수정(위 "수정안" A)이 선행**이다. 수정 범위가 `RBFMorphOp.hpp` 5줄 + 초기화 1곳이라 작지만, 우리 손에 일정이 없다.

### B — actor · 프리뷰 동기

`DashMorphingActor` 를 세워 모든 모핑 호출을 전용 스레드 하나에 감금한다. 프리뷰는 `BlockingQueuedConnection` 으로 마샬링되어 호출부가 안 바뀐다.

②를 **답하지 않고 무의미하게 만드는** 것이 이 안의 이점이고, **RW 축이 정확히 이 형으로 착지했다**(`b837552` actor 이주 · `eaa77a6` 게이트 폐기). 배관 선례와 규범이 이미 있어 신설 비용이 넷 중 가장 예측 가능하다.

문제는 거부가 **대기**로 바뀌는 것이다.

```
지금        배치 중 프리뷰 → tryClaim 실패 → 조용히 return (직전 형상 잔류)
B           배치 중 프리뷰 → 앞선 샘플이 끝날 때까지 GUI 정지
```

대기 길이 = 앞선 모핑 1건의 시간. **100ms 면 대기가 거부보다 낫고, 5초면 못 쓴다.** #281 Phase B3 의 계측 항목이 정확히 이 값이다. 감당이 안 되면 게이트를 프리뷰 거부용으로 남겨야 하므로 `actor + 게이트` 병행이 된다.

RW 축의 경험이 하나 더 있다 — 감금은 병목을 없앤 게 아니라 **옮긴다.** `DashRwThread` 점유 경합이 #281 Phase D·E 의 계측 항목으로 남아 있고, 모핑 actor 도 같은 것을 만든다.

### C — actor · 프리뷰 비블로킹

B 에 프리뷰 비동기화를 더한다. 프리뷰가 요청만 넣고 반환하며 완료 슬롯이 그린다. 그러면 게이트가 **완전히** 사라진다.

| 게이트 몫 | C 에서의 대체 |
|---|---|
| ⒜ 배제 | actor 감금이 구조로 |
| ⒝ 거부 | latest-wins 병합 — 거부할 것이 없다 |
| ⒞ 표시 (`busy()` 소비자 3곳) | 진행 상태 소스 |
| ⒟ 중복 실행 방지 | 병합이 같은 요청을 하나로 접는다 |

대신 #281 이 한 번 덜어낸 프리뷰 축을 도로 넣는 것이다. 딸려오는 것 — `requestPreviewUpdate` 단일 진입점 신설 · 호출부 16곳 치환(`UpdatePreviewMorphing` 13 + 모핑 타는 `MorphingPreview` 3) · 요청 병합·디바운스 · 결과 세대 폐기 · `m_morphingPreviewGeometry` 쓰기 경계(`DashManager.cpp:553`·`:555`, mapper 입력 live 객체라 완료 슬롯 소유여야 함) · `PreviewCheck` 동기 계약 재정의.

### 오염과 지연은 다른 축이다

①이 참이고 프리뷰가 자기 인스턴스를 들면 **데이터 오염은 어느 안에서도 없다.** 큐잉은 순서를 정할 뿐 상태를 섞지 않는다. 남는 것은 시간 축 문제 넷이고, 인스턴스 분리도 actor 감금도 이 넷을 건드리지 않는다.

| 축 | 인스턴스 분리 | actor 감금 | 어느 안이 지는가 | 해결책 |
|---|---|---|---|---|
| 데이터 오염 | **해결** | 보조 | 없음 | — |
| GUI 프리즈 | 아니오 | 아니오 | **B** | 프리뷰 호출을 비블로킹으로 (= C) |
| 스톨 표시 | 아니오 | 아니오 | **C** | latest-wins 병합 |
| 큐 무한 성장 | 아니오 | 아니오 | **C** | 디바운스 |
| 결과 세대 | 아니오 | 아니오 | **C** | 세대 태그 후 폐기 |

A′ 는 큐 자체를 안 만들어 넷 다 발생하지 않는다.

### 배치 병렬화는 어느 안에서도 별건이다

A′ 로 가도 DOE 배치를 바로 병렬로 못 돌린다. `DashMorphingDoeExecutor::m_engine` 이 executor 멤버인데 배치가 executor 하나를 샘플들이 공유한다(`batch.executor` 를 값 캡처). 샘플을 병렬로 돌리려면 샘플마다 executor·엔진을 떠야 하고, 그것은 "같은 인스턴스 동시 실행" 을 피하는 별도 작업이다.

B·C 는 스레드가 하나라 병렬화가 **영구히 닫힌다.** 스레드를 늘리면 감금이 깨져 ②가 되돌아온다. 둘은 양립하지 않는다.

---

## 종합 정리

| 안 | 실현 가능성 | 기대 효과 | 우선순위 |
|---|---|---|---|
| **A** | **즉시 착수 가능** | 창이 안 어는 것까지. 게이트 배관과 결함 3건 존치 | **1 — 지금 착수** |
| **A′** | 모핑 DLL 수정 선행 (`LocalScope` 5곳) | 게이트 배관 소멸 · 결함 3건 소멸 · 병렬화 열림 · 신설 코드 0 · Follow-up ⑴ 불요 | **2 — 수정 후 전환** |
| C | actor 신설 + 프리뷰 축 재편입 | 게이트 완전 소멸 | 3 |
| B | actor 신설 (RW 선례 있음) | 게이트 축소. 프리뷰 대기 문제가 남는다 | 4 |

**감사 전 판단(A′ 1순위)에서 순서가 바뀌었다.** 요건 ③ 실패가 우리 레포 밖 수정에 걸려 있어 A′ 를 기다리며 멈출 이유가 없다.

**A 로 착수하고 DLL 수정이 오면 A′ 로 전환하는 것이 답이다.** 두 안의 차이가 **삭제이지 추가가 아니기** 때문에 전환 비용이 낮다 — A′ = A + 게이트 철거 + 풀 병렬화이고, 프리뷰가 엔진을 단독 소유하는 것은 A 의 Phase B3 이 이미 한다. 즉 **A 를 하는 동안 A′ 의 선행이 함께 쌓인다.**

B·C 는 감사를 통과하고 B 에는 RW 선례까지 있지만, actor 를 새로 만들어야 하고 배치 병렬화를 영구히 닫는다. `LocalScope` 수정이 5줄인 것과 비교하면 대가가 크다. 다만 **DLL 수정 요청이 거절되거나 무기한 지연되면 B 가 정해가 된다** — 그때는 게이트 영구 존치(C 안 유지)와 actor 신설을 비교하는 문제로 바뀐다.

## 다음 단계

- [x] ~~요건 3개를 모핑 DLL 팀에 문의~~ — 소스 감사로 직접 확인 완료 (2026-08-21)
- [ ] **모핑 팀에 `LocalScope` 수정 요청** — `RBFMorphOp.hpp` 의 `LocalScope` 5곳(`:412`·`:433`·`:457`·`:482`·`:517`)을 걷고 SMP config 를 시동 시 1회 설정으로. 근거는 `vtkSMPToolsAPI` 가 무동기 전역 싱글턴이라는 것. **인스턴스별 SMP 스레드 수 상실이 수반됨을 함께 알린다** — 현재 두 설정 지점이 모두 `16` 이라 실질 손실은 없다
- [ ] **모핑 팀에 확인 2건** — ⑴ MKL Pardiso 를 서로 다른 핸들로 동시 호출해도 되는가 ⑵ `CreateSolver` 의 `numThread` 가 빈 람다에 캡처되고 끝나는 것(`OperatorRBFMorph.cpp:158-159`)이 의도인가. ⑴이 아니오면 `LocalScope` 수정만으로는 ③이 열리지 않는다
- [ ] **배포 라인 정리 요청** — 배포 0.0.4 가 `origin/Parallel-Processing` 빌드인데 `dev` 에 병합돼 있지 않다. `dev` 에는 `WendlandFactory` 가 없어 GUI 가 못 쓴다
- [ ] **#281 을 A 안으로 착수** — 감사 결과가 A 를 막지 않는다. Phase B3(프리뷰 엔진 단독 소유)이 A′ 의 선행이므로 전환 준비가 함께 쌓인다
- [ ] `DashMorphingUtils.cpp:192-193` 의 지역 `unique_ptr` 커널 정리 — 댕글링은 아니나(값 복사 확인) 오해 소지. Phase B1 이 그 경로를 삭제한다
- [ ] Phase B3 의 프리뷰·QC 1회 모핑 시간 계측 — B 를 택할 경우의 대기 감당 판정 입력
- [ ] DLL 수정이 오면 — #281 본문의 게이트 서술과 `ThreadingContract` 7절 "세 기제는 중복이 아니다" 박스를 A′ 기준으로 갱신하고(감금 옆에 "격리만" 1행 추가), 배치 샘플 병렬화를 후속 티켓으로 등재
