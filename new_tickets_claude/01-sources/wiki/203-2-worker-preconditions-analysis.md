# DashGUI2 워커 투입 선결 조건 상세 분석 — 공유 상태 5건의 실측·실패 시나리오·처방 (서브태스크 d 상세 설계)

> 원본: 사전조사 Issue #203 — 본문을 이 페이지로 이관한 뒤 Issue 삭제 (2026-08-24). **본 페이지가 정본**
> 파생 문서: [203-1-worker-precondition-concepts-qa](203-1-worker-precondition-concepts-qa.md)

> 연관 Issue: #64\
> 기반 문서: [194-1-async-execution-patterns](194-1-async-execution-patterns.md) 5-3절 — 한 문단짜리 목록이던 선결 조건 5건을 본 문서가 **별도 과제 수준**으로 전개 (W10 서브태스크 d 의 설계 명세)\
> 자매 문서: [201-1-qprocess-antipattern-catalog](201-1-qprocess-antipattern-catalog.md) (외부 프로세스 축 — 본 문서와 무관하게 병행 가능) · [193-1-async-execution-models](193-1-async-execution-models.md)\
> 분석 시점: 2026-07-15, 브랜치 `dev` 워킹트리\
> 발단: 검토의견 — "5-3절 선결 조건 5건은 더 구체적으로 별도의 과제로 면밀히 분석·처방된 다음에 (워커 투입에) 접근해야 한다"\
> **재검증: 2026-07-28, commit `4388c57` (dev) — 아래 "재검증 개정" 절이 현재 상태의 정정본이며, 이하 원 분석(2026-07-15)은 설계 기록으로 보존한다.**

---

## 재검증 개정 (2026-07-28, commit `4388c57` · dev)

> 본문(2026-07-15)은 설계 기록으로 그대로 둔다. 그 사이 코드가 이동했으므로 D1~D5 전건을 현재 코드에 재대조했다. 본 절이 현재 상태의 정정본이고, 각 D 절 실측에도 `[재검증 2026-07-28]` 노트를 병기했다.

### 현재 상태 요약

| # | 선결 조건 | 원 위험 | **현재 상태** | 한 줄 근거 |
|:--:|---|:--:|---|---|
| D1 | 싱글톤 lazy-init | 중 | **미해소** | 앵커 3개 불변, 처방 A(선-초기화)·B(magic static) 미적용 |
| D2 | 모핑 공유 상태 | 최고 | **부분해소** | `DashMorphingEngine` 추출·`ExecuteMorphing` 파라미터화 완료 — 단 단일 엔진 인스턴스 공유 잔존 → 경합 원천 미제거. **위험 등급 최고 유지** |
| D3 | 컨텍스트 규약 | 높음 | **미해소** | `getOrLoad` dangling(`emplace`+`raw` 반환) 그대로, `try_emplace` 안전핀 미적용 |
| D4 | cout rdbuf 스왑 | 높음 | **미해소** | 예외 시 복원 스킵 → dangling streambuf 그대로 |
| D5 | GUI·VTK 규칙 | 높음 | **미해소** | `Execute`가 live `interaction`·`context` 포인터 수령, 메인스레드 가드 0 |

**잠재 버그 2건 재확인** — D3 `getOrLoad` dangling · D4 rdbuf 예외 복원 누락 둘 다 현재 dev 코드에 **그대로 존재(수리 안 됨)**. 착수 순서 `D4 → D1 → D2 → D3 → D5`는 유효하되, D2 는 "제거"가 아니라 "완성"(추출은 됐고 인스턴스 분리가 남음)으로 성격이 바뀜.

### 원문 실측 정정 (앵커 이동·사실 수정)

- **D2 (변화 최대)** — 공유 3멤버가 `DashManager` → 신규 클래스 **`DashMorphingEngine`**(`controller/DashMorphingEngine.{h,cpp}`)으로 추출됨. `DashManager`는 `std::unique_ptr<DashMorphingEngine> m_morphingEngine`(`DashManager.h:118`) 소유·`GetMorphingEngine()`(`:179`) 노출·인스턴스 생성 `DashManager.cpp:65`. 멤버 현위치: `m_morphingOperator`(`DashMorphingEngine.h:42`, **여전히 raw 포인터** — `// TODO: switch to unique_ptr`)·`m_morphingKernel`(`:43`)·`m_morphingKernelRadius`(`:45`). `ExecuteMorphing`은 순수 시그니처 `(vtkPoints* originalPoints, vtkPolyData* targetHandles, const std::vector<vtkIdType>& fixedIds)`(`DashMorphingEngine.cpp:61`)로 전환 — 본문은 `SetTargetHandles → Morph → GetMorphedPoints`만. config 앞부분(kernel 재생성·`SetKernelFunction`·`SetInitialConfiguration`)은 `MorphingConfiguration()`(`:38-58`)으로 분리돼 `SetInitialHandles()`에서 호출. radius write는 전용 setter `SetMorphingKernelRadius()`(`:13-21`, 유효성 가드 추가)로 집약. **호출자 3곳 → 6곳**: `DashManager.cpp:480`·`:521`(프리뷰 full/linear), `DashMorphingDoeExecutor.cpp:660`·`:688`(배치 linear/full), `DashGeometryParameterWidget.cpp:1692`·`:1715`(위젯). → 본문 3절의 `DashManager.h:116/117/74`, `DashManager.cpp:314-357/530/566/306/310` 등 앵커는 전부 무효.
- **D3** — 캐시 컨테이너는 `std::map`이 아니라 **`std::unordered_map`**(`Registry.h:54`). dangling 결론은 불변(두 컨테이너 모두 `emplace` 중복키 시 요소 construct→destroy 허용). `getOrLoad`(`:22-47`)·`updateActor`(`:76-106`)·`applyFeValuesToContext`(`DashJobRunner.cpp:521-549`) 앵커 불변. `MorphFromDoeSamples`의 `getOrLoad` 호출은 `DashManager.cpp:918`(함수 시작 `:892`).
- **D1** — `Mgr()` 호출 341 → **290회**(파일 28 불변), `Instance()` 177/32 불변. 앵커 불변(`DashManager.cpp:212-219`, `DashProjectManager.cpp:13-18`, Registry `:10-13`). 추가 관찰: `DashProjectManager`는 `atexit/Destroy`가 **없어**(누수형) `DashManager`(있음)와 생명주기가 비대칭. `Destroy()`는 `.cpp`가 아니라 헤더 인라인(`DashManager.h:68-70`).
- **D4** — cout 로깅 앵커 `DashManager.cpp:813/823` → **`:844`**(`MorphFromDoeDirectory`). 스왑 블록은 `DashAnalysisModelContext.cpp:305-316` 그대로(try `:274`/catch `:337`). 처방 A 전제 **실측 확정**: 형제 저장소 `DashOpti_ReaderWriterAlpha`의 DashRW 헤더·소스에 로그 억제 API(verbose/suppress/quiet/loglevel/SetLogger) **전무**. `AnalysisReader::Update()`는 `noexcept` 아님 — 실제 throw 원(`ExternalDataTable`의 `out_of_range`) 확인, 예외 경로는 가설이 아닌 실증.
- **D5** — `MorphFromDoeSamples` `:882-918` → **`:892-940`**, `MorphFromDoeDirectory` `:841-865` → **`:815-889`**. `updateActor` 불변(`:76-106`). `DashMorphingDoeExecutor::Execute` 시그니처(`DashMorphingDoeExecutor.h:28-37`)에 `DashHandlePickingInteraction* interaction`·`DashAnalysisModelContext* analysisContext`·`DashRW::AnalysisModel*`가 **명시적 파라미터로 존재**(전부 live 포인터). 게다가 executor 내부가 `DashManager::Mgr()` 싱글톤(`GetRenderWindow`·`GetHandlePickingInteraction`·`GetMorphingEngine`·`GetInputVTU`/`GetLinearizedVTU`)에 직접 접근 — 시그니처 밖 강결합. 스냅샷/DeepCopy 분리 미도입(기존 DeepCopy는 VTK 정밀도·백업 목적이지 스레드 분리용 아님).

### D2 재평가 — "부분해소"의 의미

추출·파라미터화로 **한 호출 내부의 config+morph 원자성**은 정리됐다. 그러나 **호출자 간 단일 엔진 인스턴스 공유**는 그대로다. 프리뷰(메인)와 배치(워커)가 같은 `m_morphingEngine`을 쓰는 한:

- `MorphingConfiguration()`의 `m_morphingKernel = CreateWendlandC2Kernel(...)`(`DashMorphingEngine.cpp:54`) 재할당이, 워커의 `Morph()` 중 operator가 raw(`m_morphingOperator`)로 잡은 이전 커널을 delete → **UAF 여전**.
- 메인 `SetTargetHandles` ↔ 워커 `Morph` 인터리브 → **조용히 틀린 결과 여전**.

→ **위험 등급 최고 유지.** 잔여 처방이 명확해졌다: 처방 A의 정신(상태 격리)을 완성하려면 엔진 인스턴스를 **프리뷰용 / 배치(Job)용으로 분리**(또는 per-Job 소유)해야 한다. 원 검증 기준 "`DashManager`에서 멤버 소멸(grep 0)"은 이미 충족(추출 완료)됐으므로, 검증 기준을 "**단일 `DashMorphingEngine` 인스턴스가 프리뷰·배치에 공유되지 않음**"으로 갱신한다(3-4절 재검증 노트 참조).

## 0. 목적과 범위

기반 문서 5-3절의 판정("이것 없이 스레드부터 넣으면 프리즈가 레이스로 바뀐다")을 과제화한다. 5건 각각에 대해:

1. **실측 현황** — 지금 코드가 정확히 어떻게 생겼나 (라인 앵커)
2. **실패 시나리오** — 두 번째 스레드가 등장하는 순간 무엇이 어떻게 깨지나 (구체 인터리빙)
3. **처방** — 대안 비교 후 선택 + 기각 사유
4. **검증 기준** — 완료를 무엇으로 확인하나

**범위 경계**: 본 선결 조건은 **워커 축(서브태스크 e — WorkerJob·직렬 풀)의 게이트**다. 외부 프로세스 축(서브태스크 a~c — ProcessJob·폴링 제거·데몬 비동기화)은 스레드를 만들지 않으므로 본 문서 완료를 기다릴 필요 없이 즉시 착수 가능 (기반 문서 5-3절 개정 5 재확인).

**분석 중 신규 발견 2건**: 조사 과정에서 "멀티스레드가 되면 깨질 것"이 아니라 **지금도 깨져 있는** 잠재 버그를 2건 발견했다 — D3 의 getOrLoad dangling 반환 경로, D4 의 예외 시 rdbuf 복원 누락. 둘 다 단일 스레드 + 정상 경로에서는 발현하지 않아 숨어 있었다. 4절·5절에 기술.

## 1. 결론 먼저

| # | 선결 조건 | 실패 모드 (워커 투입 시) | 위험 등급 | 처방 요약 | 규모 |
|:---:|---|---|:---:|---|:---:|
| D1 | 싱글톤 lazy-init 안전화 | 이중 생성·미완성 객체 관찰 | 중 | 메인스레드 선-초기화 + magic static 전환 | 소 |
| D2 | 모핑 공유 상태 분리 | **조용히 틀린 모핑 결과** + UAF 크래시 | **최고** | operator·kernel 을 Job 로컬 소유로 이전 | 중 |
| D3 | 컨텍스트 접근 규약 | 이중 파싱·dangling 컨텍스트·변이 레이스 | 높음 | per-key 단일 로드 + RW 직렬 워커 소유 규약 | 중~대 |
| D4 | 전역 cout rdbuf 스왑 제거 | 영구 로그 유실·dangling rdbuf 크래시 | 높음 | 스왑 삭제 — 전역 1회 억제로 대체 | **소 (즉시 가능)** |
| D5 | GUI·VTK 객체 규칙 | 워커의 위젯/렌더러 접근 = Qt 계약 위반 크래시 | 높음 | 절단 3규칙의 타입 화이트리스트 구체화 | 규약 |

권장 착수 순서: **D4 → D1 → D2 → D3 → D5**(D5 는 규약이므로 e 와 동시 적용). D4·D1 은 서로 독립이고 소형이라 워커 계획과 무관하게 지금 고쳐도 순수 이득이다.

## 2. D1 — 싱글톤 lazy-init 안전화

### 2-0. 문제 요약

싱글톤 `DashManager`·`DashProjectManager`가 락 없는 lazy-init(널 검사 → 생성 → 발행을 동기화 없이)으로 인스턴스를 만든다. 단일 스레드에서는 첫 호출이 곧 유일한 생성이라 무해하지만, 워커 스레드가 이 싱글톤을 처음 건드리는 순간 문제가 된다: 메인과 워커가 동시에 `nullptr`을 관찰해 **인스턴스를 두 번 생성**(상태 분열·누수)하거나, 생성자 완료 전에 발행된 **미완성 객체를 읽거나**, `atexit(Destroy)`를 이중 등록해 종료 시 이중 해제한다. 호출 지점이 수백 곳(`Mgr()` 290회 · `Instance()` 177회)이라 "워커에서 첫 호출이 절대 일어나지 않게" 코드 리뷰만으로 보장하는 것은 비현실적이고, 메인스레드 선-초기화 같은 구조적 장치가 필요하다.

### 2-1. 실측

> **[재검증 2026-07-28]** 미해소. 앵커 불변, 처방 A·B 모두 미적용. `Mgr()` 호출 341→290(파일 28 불변). `DashProjectManager`는 `atexit/Destroy` 부재(생명주기 비대칭). 상세: "재검증 개정" 절.

```cpp
// DashManager.cpp:212-219
DashManager* DashManager::Mgr(){
    if(m_instance==nullptr){            // 락 없는 check
        m_instance = new DashManager(); // 락 없는 생성·발행
        atexit(Destroy);
    }
    return m_instance;
}
// DashProjectManager.cpp:13-18 — 동형
```

- 호출 밀도: `DashManager::Mgr()` **341회 / 28파일**, `DashProjectManager::Instance()` **177회 / 32파일** (2026-07-15 grep). 어느 호출 지점이 "첫 호출"이 될지 정적으로 통제 불가능한 규모.
- 대조 선례가 같은 코드베이스에 있다: `DashAnalysisModelContextRegistry::Instance()` 는 **magic static** (`DashAnalysisModelContextRegistry.cpp:10-13`, 주석 "thread-safe since C++11") — C++11 이후 컴파일러가 초기화 직렬화를 보장한다.

### 2-2. 실패 시나리오

워커 스레드의 작업 함수가 (직접 또는 깊은 호출 체인 안에서) `Mgr()` 를 첫 호출하는 경우:

1. **이중 생성** — 메인과 워커가 동시에 `m_instance==nullptr` 를 관찰 → 인스턴스 2개 생성, 한쪽 누수 + 이후 두 스레드가 서로 다른 인스턴스를 참조 (상태 분열).
2. **미완성 발행** — `m_instance` 대입이 생성자 완료보다 먼저 관찰될 수 있음(비원자 포인터, 메모리 순서 미보장) → 다른 스레드가 초기화 중인 객체의 멤버를 읽음.
3. `atexit(Destroy)` 이중 등록 → 종료 시 이중 해제.

호출 밀도 341+177 회 규모에서 "워커에서 절대 첫 호출이 안 되게 한다"를 코드 리뷰만으로 보장하는 것은 비현실적 — 구조적 장치가 필요하다.

### 2-3. 처방

| 방식 | 장점 | 단점 | 네이티브 | 판정 |
|---|---|---|:---:|---|
| A. 메인스레드 선-초기화 — `main()` 에서 `Mgr()`·`Instance()` 명시 1회 호출 | 한 줄, 즉시 적용, 이후 모든 호출은 읽기 전용 | "새 싱글톤 추가 시 등록 누락" 휴먼 에러 여지 | — | **채택 (1차)** |
| B. magic static 전환 — `static DashManager inst; return &inst;` | 언어가 보장, Registry 와 동형 수렴 | `atexit(Destroy)` 수동 소멸 순서와 충돌 검토 필요 (정적 소멸 순서로 이동), heap 포인터 전제 코드(`Destroy`) 손질 | O | **채택 (2차, additive)** |
| C. `std::call_once` / 초기화 뮤텍스 | 기존 형태 유지 | 매 호출 오버헤드 또는 이중 체크 복잡도 — A+B 로 충분한데 코드만 는다 | O | 기각 |

A 를 먼저(비용 0에 가까움), B 는 `Destroy`/atexit 정리와 함께. 보조 장치로 생성자에 `Q_ASSERT(QThread::currentThread() == qApp->thread())` 1줄 — 규약 위반을 디버그 빌드에서 즉사시킨다.

### 2-4. 검증

- [ ] `main()` 초기에 두 싱글톤 선-초기화 호출 존재
- [ ] 생성자 메인스레드 assert 존재
- [ ] (B 적용 시) `atexit`/`Destroy` 경로 제거·정적 소멸로 일원화

## 3. D2 — 모핑 공유 상태 분리 (위험 최고 등급)

### 3-0. 문제 요약

모핑 실행 상태(operator·kernel·radius)가 **단일 엔진 인스턴스**로 공유돼 있다. 프리뷰(메인)와 배치 DOE(워커)가 같은 엔진 위에서 `config → morph` 시퀀스를 인터리브하면, 워커가 만드는 케이스가 **크래시 없이 조용히 틀린 형상**으로 산출되고(후속 FE 해석까지 오염되며 재현이 비결정적이라 추적 최난도), kernel 재할당이 실행 중인 이전 kernel을 파괴해 **UAF 크래시**가 난다. `DashMorphingEngine` 추출·`ExecuteMorphing` 파라미터화로 한 호출 내부의 원자성은 정리됐지만, 프리뷰·배치가 여전히 하나의 엔진을 공유하는 한 경합의 원천은 그대로 남는다 — 그래서 **위험 등급은 최고를 유지**하며, 잔여 과제는 엔진 인스턴스를 프리뷰용/배치용으로 분리하는 것이다.

### 3-1. 실측

> **[재검증 2026-07-28]** 부분해소. 공유 상태가 신규 클래스 `DashMorphingEngine`으로 **추출**되고 `ExecuteMorphing`이 **파라미터화**됨 → 이하 `DashManager.h/.cpp` 앵커와 "비원자 6단계 시퀀스" 서술은 무효. 단 단일 엔진 인스턴스 공유는 잔존해 UAF·조용히 틀린 결과 벡터가 남음(위험 등급 최고 유지). 현재 앵커·잔여 경합·갱신된 검증 기준: "재검증 개정" 절.

싱글톤 `DashManager` 멤버 3개가 모핑 실행 상태를 이룬다:

| 멤버 | 선언 | 변이 지점 |
|---|---|---|
| `DashMR::OperatorMorph* m_morphingOperator` | `DashManager.h:116` | 생성 `MorphingConfiguration()` (`:306` — 내부 16스레드 솔버, `:310`), 매 실행 5단계 변이 |
| `std::unique_ptr<IKernelFunction> m_morphingKernel` | `DashManager.h:117` | **매 실행 재할당** (`:330`) |
| `double m_morphingKernelRadius` | `DashManager.h:74` | 위젯 설정 경로 write (`:566`), 매 실행 read (`:330`) |

`ExecuteMorphing` (`DashManager.cpp:314-357`) 은 이 공유 멤버 위에서 **비원자 6단계 시퀀스**를 수행한다: kernel 재생성(`:330`) → `SetKernelFunction`(`:331`) → `SetInitialConfiguration`(`:333`) → `SetTargetHandles`(`:334`) → `Morph`(`:337`) → `GetMorphedPoints`(`:338`).

호출자 3곳 (현재 전부 메인 스레드):

1. `DashManager.cpp:530` — 인터랙티브 프리뷰 경로 (**워커 이전 대상 아님** — 메인 잔류)
2. `DashMorphingDoeExecutor.cpp:643` — 배치 DOE (**워커 이전 1순위** — 기반 문서 5-4절 순위 1)
3. `DashGeometryParameterWidget.cpp:1694` — 위젯 직접 호출

### 3-2. 실패 시나리오

배치(워커)와 프리뷰(메인)가 공존하는 순간 — 사용자가 밤새 배치를 걸어두고 프리뷰를 만지는 평범한 시나리오:

```
워커(배치 케이스 k):  SetInitialConfiguration(A) → SetTargetHandles(A') → ...
메인(프리뷰):                                   SetTargetHandles(B') →  Morph()
워커:                 Morph()   ← initial=A, target=B' 조합으로 실행
```

1. **조용히 틀린 결과** — 크래시 없이 케이스 k 의 VTU 가 잘못된 형상으로 생성돼 후속 FE 해석까지 오염. 디버깅 난도 최상 (재현 비결정적, 산출물만 보면 원인 추적 불가). 이것이 D2 를 최고 등급으로 두는 이유다.
2. **UAF 크래시** — 메인의 `m_morphingKernel = CreateWendlandC2Kernel(...)` 재할당(`:330`)이 워커가 `Morph()` 실행 중 참조하는 이전 커널을 파괴 (`unique_ptr` 대입 = 이전 객체 즉시 delete).
3. **radius 반입력 오염** — 배치 도중 위젯에서 radius 변경(`:566`) 시 이후 케이스만 새 radius 로 실행 — 한 배치 안에 두 설정이 섞임 (스냅샷 규율 위반, 기반 문서 6-5절).

### 3-3. 처방

| 방식 | 장점 | 단점 | 판정 |
|---|---|---|---|
| A. **Job 로컬 소유** — 실행마다 operator·kernel 을 Job 이 생성·소유·파괴. radius 는 시작 시점 스냅샷 파라미터 | 공유 상태 소멸 = 레이스 원천 제거. `ExecuteMorphing` 이 순수 함수화 | operator 생성 비용 — 단 kernel 은 이미 "매 실행 재생성(cheap)" 주석(`:329`)이 선례고, operator 생성도 설정 3줄(`:306-310`) | **채택** |
| B. 직렬 워커 스레드-로컬 1개 재사용 | 생성 비용 상각 | 프리뷰(메인)와 배치(워커)가 **여전히 다른 인스턴스여야** 안전 — 결국 A 와 동일 결론 + 수명 관리만 복잡 | A 로 흡수 |
| C. `m_morphingOperator` 를 mutex 로 보호 | 코드 변경 최소 | 프리뷰가 배치 케이스 완료까지 블록 — **제거하려는 프리즈를 락으로 재도입**. 목표(응답성) 역행 | 기각 |

부수 규칙: `DashMR::OperatorMorph` 는 스레드 안전성 등급 2(비재진입 — 기반 문서 5-2절, 내부 16스레드 병렬이므로 단일 호출자 전제)로 취급 — 모핑 직렬 풀(maxThreadCount=1)에서만 실행. Job 로컬 소유(A)와 직렬 풀은 상호 보완이다: A 가 상태 격리, 직렬 풀이 DLL 등급 2 계약 준수.

### 3-4. 검증

- [ ] `DashManager` 에서 `m_morphingOperator`·`m_morphingKernel` 멤버 소멸 (grep 0건)
- [ ] `ExecuteMorphing` 시그니처에 radius 포함(파라미터화) — 전역 상태 read 0
- [ ] 호출자 3곳 모두 새 시그니처로 이행, 프리뷰·배치가 각자의 인스턴스 사용

> **[재검증 2026-07-28] 검증 기준 갱신** — 위 첫 두 항목("멤버 소멸"·"시그니처 파라미터화")은 `DashMorphingEngine` 추출로 **이미 충족**. 잔여 기준을 아래로 대체한다:
> - [ ] 단일 `DashMorphingEngine` 인스턴스(`DashManager::m_morphingEngine`)가 프리뷰(메인)·배치(Job)에 **공유되지 않음** — 각 실행 경로가 자기 엔진 소유 (또는 per-Job 생성)
> - [ ] `m_morphingOperator` raw 포인터 → 소유 스마트포인터 전환(현 `// TODO: switch to unique_ptr`), `m_morphingKernel` 재할당이 실행 중 operator 참조와 겹치지 않음

## 4. D3 — DashAnalysisModelContext 접근 규약

### 4-0. 문제 요약

`DashAnalysisModelContext` 캐시에는 내부 동기화가 전혀 없고, `getOrLoad`가 수 초짜리 파싱을 락 밖에서 수행한 뒤 `emplace` + raw 포인터 반환으로 캐시에 넣는다. 워커가 등장하면 세 가지가 깨진다: 두 스레드가 같은 경로를 **이중 파싱**하고, 경합 시 늦은 쪽의 `emplace`가 키 중복으로 요소를 생성했다 즉시 파괴하는 바람에 **이미 파괴된 컨텍스트를 가리키는 dangling 포인터가 반환**되며(단일 스레드에서는 경합이 없어 안 터지지만 코드 형태로는 이미 심어진 지뢰), 배치가 `setFeConditionValue`로 캐시를 변이하는 동안 메인 위젯이 같은 인스턴스의 파트 트리를 순회하는 **읽기-변이 레이스**가 UB를 낸다. 로드 경합은 코드로, 심층 접근은 소유권 규약(RW 직렬 풀 전담)으로 나눠 처방해야 한다.

### 4-1. 실측

> **[재검증 2026-07-28]** 미해소. `getOrLoad` dangling 경로 현존 — 현재도 `emplace`(`:43`)+`raw` 반환(`:46`)으로 `try_emplace` 안전핀 미적용. 앵커 불변(`:22-47`). 컨테이너는 `std::map`이 아니라 `std::unordered_map`(`Registry.h:54`)이나 결론 불변. 상세: "재검증 개정" 절.

**레지스트리** (`DashAnalysisModelContextRegistry.cpp`):

- `Instance()` 는 magic static (안전, `:10-13`). `m_mutex` 는 **맵 조작만** 보호 (`get:16`, `getOrLoad:25,42`).
- `getOrLoad` (`:22-47`) 구조: 락→캐시 확인→**언락**→`loadAnalysisModelFromFile` (수 초 파싱, 락 밖)→락→`emplace`.
- `updateActor` (`:76-106`) — 같은 클래스가 렌더러·액터 조작(메인 전용 작업)까지 담당. `m_activeFilePath`·`m_activeActor` 는 뮤텍스 밖.

**컨텍스트** (`DashAnalysisModelContext`): 내부 동기화 **0건** (mutex/atomic grep 무). 같은 캐시 인스턴스를 다수 소비자가 공유:

- 읽기: 위젯 10여 곳이 `getOrLoad`/`activeContext` 경유 파트·메시 조회
- **변이**: `DashJobRunner::applyFeValuesToContext` (`DashJobRunner.cpp:521-549`) — 배치가 케이스마다 `setFeConditionValue` 로 캐시 인스턴스를 변이 후 export. `MorphFromDoeSamples` 도 같은 컨텍스트 대상 (`DashManager.cpp:903-921`)

### 4-2. 실패 시나리오

1. **이중 파싱** — 두 스레드가 같은 경로로 동시 `getOrLoad` → 둘 다 캐시 miss → 같은 파일을 두 번 파싱 (수 초 × 2) .
2. **dangling 컨텍스트 반환 (신규 발견 — 현재도 잠재)** — 위 경합에서 늦은 쪽의 `emplace` 는 키 중복으로 삽입 실패하는데, `std::map::emplace` 는 실패 시에도 인자로부터 요소를 **일단 생성했다가 즉시 파괴**할 수 있다 (표준 허용 동작). 이때 `std::move(ctx)` 로 소유권이 임시 요소로 넘어가 파괴되고, 그 전에 떠 둔 `raw` (`:40`) 는 **파괴된 컨텍스트를 가리킨 채 반환**된다. 단일 스레드에서는 경합 자체가 없어 발현하지 않지만, 코드 형태로는 이미 심어져 있는 지뢰다.
3. **읽기-변이 레이스** — 배치(워커)가 `setFeConditionValue` 로 변이하는 동안 메인의 위젯이 같은 인스턴스의 파트 트리를 순회 — 내부 동기화가 없으므로 컨테이너 리해시/재할당 중 읽기 = UB.
4. **워커발 렌더러 접근** — 워커의 `getOrLoad` 가 어딘가에서 `setActiveContext`→`updateActor` 로 이어지면 렌더러 조작이 워커에서 실행 (D5 위반과 결합).

### 4-3. 처방

두 층으로 나눈다 — **로드 경합**은 코드로, **접근 규약**은 소유권으로.

로드 경합 (getOrLoad 수리):

| 방식 | 장점 | 단점 | 판정 |
|---|---|---|---|
| A. per-key 로드 1회 보장 — 캐시 값을 `shared_future<Context*>` 로: 첫 스레드가 promise 를 걸고 락 밖 파싱, 경합 스레드는 같은 future 대기 | 이중 파싱·dangling 원천 제거, 파싱 중 락 비점유 유지 | future 배관 추가 | **채택** |
| B. 파싱까지 락 안으로 | 코드 최소 | 수 초 파싱 동안 전 캐시 접근 블록 — 워커 여럿이면 직렬화 병목, 메인이 `get` 만 해도 걸림 | 기각 |
| C. `try_emplace` 로 교체만 | dangling 만 수리 (move 미발생 보장) | 이중 파싱은 잔존 — 단 **A 이전의 즉효 안전핀으로 1줄 가치** | A 전 단계로 채택 |

접근 규약 (컨텍스트 소유권):

- **"컨텍스트 심층 접근은 RW 직렬 풀에서만"** — read(`Update()`)·변이(`setFeConditionValue`)·export 전부 RW 풀 큐로. `DashRW`/`dash::rw` 의 등급 2 취급(기반 문서 5-2절)과 같은 풀이라 일석이조.
- 메인(위젯·렌더링)은 **읽기 전용 스냅샷**만 — 표시용 요약(파트 이름 목록·메시 통계 등)을 값 복사 구조체로 시그널 전달. 무거운 원본 객체는 메인에 넘기지 않는다.
- `updateActor` 계열(렌더러 조작)은 레지스트리에서 분리 검토 — 최소한 "메인스레드 전용" assert 부착 (D5 규칙의 적용 지점).

### 4-4. 검증

- [ ] `try_emplace` 즉시 적용 (안전핀)
- [ ] `getOrLoad` 동시 호출 시 파싱 1회 보장 (로그로 확인 가능 — `[Registry] Loading` 이 경로당 1회)
- [ ] 컨텍스트 심층 API 호출 지점 전수 목록화 → RW 풀 경유로 이행
- [ ] `updateActor` 에 메인스레드 assert

## 5. D4 — 전역 std::cout rdbuf 스왑 제거 (즉시 착수 권장)

### 5-0. 문제 요약

`.dat` 파싱 동안 로그를 죽이려고 `std::cout`/`std::cerr`의 rdbuf를 지역 널스트림으로 갈아끼웠다가 파싱 후 복원하는데, 이 스왑이 **프로세스 전역 상태**를 건드린다는 것이 문제다. `reader.Update()`가 예외를 던지면(이 블록은 애초에 try-catch로 감싸여 throw를 상정한 코드다) 복원 두 줄을 건너뛰고 catch로 점프하고, 스택 해제로 지역 널스트림이 파괴되면서 `std::cout`은 **파괴된 streambuf를 가리킨 채** 남아 이후 프로세스 어디서든 cout 출력이 UB가 된다 — 워커와 무관하게 **지금도 단일 스레드에서 발현 가능한 잠재 버그**다. 워커가 붙으면 save/restore 인터리빙으로 **전 프로세스 로그가 영구 유실**되고 타 스레드의 정당한 출력까지 삼킨다. 다른 4건과 의존성이 없고 규모가 가장 작아 즉시 착수를 권장한다.

### 5-1. 실측

> **[재검증 2026-07-28]** 미해소. 스왑·예외 시 복원 누락 현존(`DashAnalysisModelContext.cpp:305-316`, try `:274`/catch `:337`). cout 로깅 앵커 `:813/823`→`:844`. DashRW 로그 억제 API 부재 실측 확정(처방 A 전제 성립), `Update()`의 실제 throw 원 확인. 상세: "재검증 개정" 절.

```cpp
// DashAnalysisModelContext.cpp:305-316 (try 블록 내부)
std::streambuf* coutBuf = std::cout.rdbuf();
std::streambuf* cerrBuf = std::cerr.rdbuf();
std::ostringstream nullStream;              // 지역 변수
std::cout.rdbuf(nullStream.rdbuf());        // 프로세스 전역 상태 변이
std::cerr.rdbuf(nullStream.rdbuf());
bool updateResult = reader.Update();        // 수 초 파싱, throw 가능
std::cout.rdbuf(coutBuf);                   // 복원
std::cerr.rdbuf(cerrBuf);
```

### 5-2. 실패 시나리오

1. **(신규 발견 — 현재 단일 스레드에서도 잠재 버그)** `reader.Update()` 가 throw 하면 (이 함수 전체가 try-catch 로 감싸여 있어 throw 를 상정한 코드다 — `:337` catch) 복원 두 줄을 건너뛰고 catch 로 점프한다. 스택 해제로 `nullStream` 이 파괴되고, `std::cout` 은 **파괴된 streambuf 를 가리킨 채** 남는다 — 이후 프로세스 어디서든 cout 출력 시 UB. 이 코드베이스는 cout 로깅이 실제로 있으므로 (`DashManager.cpp:813, 823` 등) 도달 가능하다.
2. **(워커 투입 시)** 두 스레드 동시 로드의 save/restore 인터리빙: T1 저장(원본)→T2 저장(**널스트림을 "원본"으로 저장**)→T1 복원(원본)→T2 복원(T2가 저장한 널스트림) → 파싱이 끝났는데 cout 이 영구히 (곧 파괴될) 널스트림을 향함 — 전 프로세스 로그 유실 + 1번과 같은 dangling.
3. 부수 효과 — 스왑 구간 동안 **다른 스레드의 정당한 cout 출력까지 삼킨다** (전역이므로).

### 5-3. 처방

| 방식 | 장점 | 단점 | 네이티브 | 판정 |
|---|---|---|:---:|---|
| A. DashRW 플러그인 로그 억제 API 사용 | 원인 지점에서 해결, 전역 상태 무접촉 | API 존재 여부 확인 필요 (벤더/헤더 조사 선행) | O | **1순위 확인** |
| B. 앱 시작 시 전역 1회 널 싱크 고정 (복원 없음) | GUI 앱에서 cout 은 어차피 콘솔 부재 — 스왑·복원 자체를 없앰. 정적 수명 싱크라 dangling 불가 | cout 기반 디버그 로그(`DashManager.cpp:813` 등)도 함께 사라짐 → qDebug 이행 필요 | △ | **A 부재 시 채택** |
| C. RAII 가드 + 전역 뮤텍스로 스왑 유지 | 기존 의도 보존 | 예외 안전은 해결되나 "타 스레드 출력 삼킴" 부작용 잔존, 락 추가 | X | 기각 |

D4 는 다른 4건과 의존성이 없고 규모가 가장 작으며 **이미 잠재 버그**이므로, 워커 계획과 무관하게 즉시 착수를 권장한다.

### 5-4. 검증

- [ ] `rdbuf(` grep 이 `model/`·`controller/` 에서 0건
- [ ] .dat 파싱 실패(예외) 유도 후에도 콘솔/로그 출력 정상

## 6. D5 — GUI·VTK 객체 규칙

### 6-0. 문제 요약

배치 모핑 실행 경로(`MorphFromDoeSamples` → `DashMorphingDoeExecutor::Execute`)가 이미 `DashHandlePickingInteraction*`·살아있는 컨텍스트 포인터 등 **GUI·VTK 객체를 직접 입력으로 받고**, executor 내부는 `DashManager::Mgr()` 싱글톤의 렌더러·인터랙터에 직접 접근한다. 이 경로를 그대로 워커로 옮기면 워커가 QWidget·VTK 렌더링 계층을 건드리게 되어, **Qt 계약(QWidget 계열은 메인스레드 전용)과 VTK 계약(파이프라인 객체는 스레드 간 공유 금지)을 위반**하는 크래시가 난다. 여기서 위반 대상은 코드 한 줄이 아니라 **규칙**이므로, D5의 산출물은 수정 diff가 아니라 집행 가능한 규약(입력 스냅샷 화이트리스트·실행 중 무접촉·출력 소유권 이전)과 메인스레드 가드 assert다.

### 6-1. 실측 — 워커 이전 대상 경로에 이미 들어와 있는 GUI/VTK 접점

> **[재검증 2026-07-28]** 미해소. `MorphFromDoeSamples` `:892-940`, `MorphFromDoeDirectory` `:815-889`, `updateActor` 불변. `DashMorphingDoeExecutor::Execute`가 live `DashHandlePickingInteraction*`·`DashAnalysisModelContext*`를 명시 파라미터로 받고, 내부에서 `DashManager::Mgr()` 싱글톤에 직접 접근. 메인스레드 가드 0. 상세: "재검증 개정" 절.

| 접점 | 위치 | 문제 |
|---|---|---|
| `DashHandlePickingInteraction*` 가 배치 executor 에 주입 | `DashManager::MorphFromDoeSamples` (`DashManager.cpp:882-918`) → `DashMorphingDoeExecutor::Execute` | 피킹 상호작용 객체(렌더러·인터랙터 결합)가 배치 실행의 입력 — 이대로 워커에 옮기면 워커가 VTK 인터랙션 계층을 참조 |
| 레지스트리의 렌더러 조작 | `DashAnalysisModelContextRegistry::updateActor` (`:76-106`) | 로드 경로(`getOrLoad`)와 렌더 경로가 한 클래스 — 워커발 호출 위험 (D3 과 결합) |
| 배치 산출 VTK 객체 | `DashMorphingDoeExecutor`·`MorphFromDoeDirectory` (`DashManager.cpp:841-865`) 의 `vtkUnstructuredGrid` 생성·Write | 워커 생성 객체를 메인의 렌더 파이프라인에 그대로 꽂으면 공유 위반 |

Qt 계약(QWidget 계열 메인스레드 전용)과 VTK 계약(파이프라인 객체 스레드 간 공유 금지 — 참조 카운트만 원자적)은 코드가 아니라 **규칙**이므로, D5 의 산출물은 수정 diff 가 아니라 **집행 가능한 규약 + 가드**다.

### 6-2. 처방 — 절단 3규칙(기반 문서 6-4절)의 타입 수준 구체화

1. **입력 스냅샷의 화이트리스트** — 워커 함수 파라미터 구조체에 허용되는 타입을 명시: 값 타입(QString/double/QJsonObject/컨테이너)·`DeepCopy` 된 `vtkPolyData`/`vtkPoints`. **금지**: `QWidget*` 계열, `vtk*Renderer/Window/Interactor/Widget` 계열, `DashHandlePickingInteraction*`, 살아있는 컨텍스트 포인터. → `MorphFromDoeSamples` 의 경우 interaction 에서 실제 필요한 것(핸들 poly·고정점 ID)만 시작 시점에 DeepCopy 추출해 넘긴다.
2. **실행 중 무접촉** — 워커 본문은 스냅샷과 자기 생성 객체만. 진행·로그는 시그널로만 (직접 위젯 append 금지).
3. **출력 소유권 이전** — 워커 생성 VTK 객체는 `vtkSmartPointer` 로 시그널에 실어 메인으로 넘기고, 메인 슬롯에서만 mapper/actor/렌더러에 연결. 워커는 전달 후 참조를 놓는다.

가드 장치: 렌더러·인터랙션 조작 함수 진입부에 메인스레드 assert (`updateActor`, `Redraw`, `GetRenderWindow` 등 `DashManager` 렌더 계열) — 규약 위반을 디버그 빌드에서 즉시 노출.

### 6-3. 검증

- [ ] 워커 진입 함수(WorkerJob 대상)의 파라미터에 금지 타입 0건 (코드 리뷰 체크리스트 항목화)
- [ ] `DashManager` 렌더 계열 + `updateActor` 에 메인스레드 assert
- [ ] 배치 모핑 워커화(기반 문서 5-4절 순위 1) 시 interaction 주입이 스냅샷 추출로 대체됨

## 7. 순서·게이트·백로그 반영

의존 구조:

```
D4 (독립, 즉시)     ─┐
D1 (독립, 소형)     ─┼→ [게이트] → 서브태스크 e (WorkerJob + 직렬 풀 2종)
D2 (모핑 풀 전제 정리) ─┤              └ D5 규약은 e 의 모든 Job 에 동시 적용
D3 (RW 풀 전제 정리)  ─┘
```

- **게이트 규칙**: e 착수 전 D1~D4 완료 + D5 규약 문서화·assert 부착 확인. 기반 문서 5-3절의 순서 강제(d → e)를 5건 각각의 완료 기준으로 구체화한 것.
- **즉시 착수 가능 (워커 무관 순수 이득)**: D4 전체, D3 의 `try_emplace` 안전핀, D1 의 선-초기화 1줄 — 셋 다 현재 동작을 바꾸지 않으면서 잠재 버그를 닫는다.
- **백로그 영향**: 기반 문서 7절 서브태스크 d 의 내용이 본 문서로 구체화됐다 — 티켓 분할 시 d 를 D1~D5 로 쪼갤 근거. 신규 작업 항목 추가 없음 (기존 d 의 전개).

## 8. 참고 자료

- 내부: [194-1-async-execution-patterns](194-1-async-execution-patterns.md) 5-2절(DLL 스레드 안전성 3등급)·5-3절(원 목록)·6-4절(절단 3규칙)·7절(서브태스크 d·e) / [201-1-qprocess-antipattern-catalog](201-1-qprocess-antipattern-catalog.md) (외부 축 — 본 게이트와 무관하게 병행)
- 외부: C++ 표준 — magic static 초기화 직렬화(C++11), `std::map::emplace` 실패 시 인자 소비 미보장(`try_emplace` 와의 차이) / Qt 문서 — QObject 스레드 어피니티, QWidget 메인스레드 제약 / VTK 문서 — 스레드 안전성 (참조 카운트 원자성 vs 파이프라인 비공유)
