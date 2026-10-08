# vcpkg 이행 — 코드 수정 지점

> 조사: 2026-09-10 · 대상 커밋 `323870d` · GUI 저장소 기준

## Responsibility

- **이 문서가 소유하는 것**: vcpkg 배포가 확정됐을 때 **GUI 저장소 안에서** 바꿔야 하는
  코드·빌드 수정 지점의 목록과 그 판정 근거.
- **이 문서가 소유하지 않는 것**: 이행 단계·일정·외부 모듈 재빌드 (→
  [vcpkg-migration-scope.md](vcpkg-migration-scope.md)), 빌드 환경 요구사항 (→
  [scratchpad/build-environment.md](scratchpad/build-environment.md)).

## Must-Know Rules

1. **morphing 은 개명이 아니다.** `DashMR::OperatorMorph` 의 setter 파이프라인
   (`SetKernelFunction` → `SetInitialConfiguration` → `SetTargetHandles` → `Morph`)에 대응하는
   API 가 `mesh-ops` 에 없다. 호출부 7파일을 재작성한다.
2. **mesh-ops 로 넘기는 handle polydata 는 `"SupportRadius"` point-data array(1 성분, point 수
   길이, 유한·양수)를 필수로 요구한다.** 없으면 `HandleConfiguration::create()` 가
   `ErrorCode::InvalidArgument` 로 실패한다. GUI 는 현재 전역 kernel radius 단일값만 들고 있다.
3. **preprocessor 공개 표면은 `inputIdx` 색인 모델을 버리고 파일 경로를 인자로 받는다.**
   `IPreprocessorWrapper` 의 8개 메서드가 전부 시그니처를 잃는다.
4. **preprocessor 반환 타입은 JSON 문자열이 아니라 타입 구조체다.** `std::string` →
   `dash::core::Result<AnalysisInfo>` 등. GUI 의 preprocessor 출력 JSON 파싱 29곳이 소멸한다.
5. **`preprocessor` · `mesh-ops` 를 레지스트리에서 받으면 VTK 9.3 과 Qt6 가 함께 딸려온다.**
   두 포트 모두 공개 API 가 `vtkSmartPointer` 를 넘기고 `vcpkg-vtk` 를 default-feature 로
   갖는다. `vtk[qt]` 는 `qtbase`(Qt6)를 요구한다. **§1 · §2 · §3 은 한 배포다.**
6. **Qt6 전환은 앱 단독으로 완결된다.** 컴파일을 깨는 필수 수정은 3곳, 나머지 ~30곳은
   기계적이며 Qt5 에서도 컴파일된다.
7. **VTK 는 9.4 → 9.3 하향이다.** 앱 코드에서 사라지는 심볼은 `vtkGenerateIds` 하나다.
8. **`mesh-ops` 를 매니페스트에 넣으면 최상위 `overrides` 가 필요해진다.** 포트가 소비자에게
   `intel-mkl` 핀을 요구한다. 현재 GUI 매니페스트의 "overrides 없음" 정책과 충돌하며, 추가
   시점에 바이너리 캐시가 무효화되므로 캐시 워밍이 선행돼야 한다.
9. **GUI 의 `features` · `overrides` 는 메타 저장소 `DashOpti/vcpkg.json` 과 일치해야 한다.**
   어긋나면 ABI 해시가 달라져 `--only-binarycaching` 개발자에게 하드 실패가 된다.

## Related Docs

- [vcpkg 이행 작업 분량](vcpkg-migration-scope.md) — 단계·일정·외부 모듈 재빌드
- [빌드 환경 요구사항](scratchpad/build-environment.md)

---

## 1. mesh-ops — morphing code 수정

`external/DashOptiMorphing-0.0.4` (`DashMR`) → vcpkg `mesh-ops` (`dash::mesh`).

레지스트리 포트 `mesh-ops 2026-09-07.0` 은 `DashOpti_MeshOps@97bf939` 를 가리키고, 그 커밋은
RBF morphing 공개 API(`#5`)를 포함한다. **`external/mesh-ops` 스냅샷에는 morphing 이 없다** —
Jacobian 만 있다. 즉 GUI 는 아직 이 API 를 한 줄도 쓰고 있지 않다.

> 핀된 `97bf939` 는 `origin/dev` 에만 있고 `origin/main` 에는 없다 (main 팁은 `c654dc2`,
> 2026-08-23). portfile 자신이 선언한 "핀된 REF 는 항상 main 에 있다" 는 불변식이 깨져 있다.
> commit 이 ref 에서 도달 가능하므로 `vcpkg_from_git` 은 성공하지만, main 이 방치되면 포트가
> 조용히 재현 불가능해진다. 레지스트리 쪽에 정정 요청 대상.

### 1.1 패러다임 차이 — 개명으로 처리되지 않는 이유

| 축 | 구 `DashMR` | 신 `dash::mesh` |
|---|---|---|
| 구성 방식 | 가변 객체 + setter 순서 의존 | 불변 값 4단계: `IHandleSet` → `HandleConfiguration` → `MorphingConfiguration` → `MorphingOperator` |
| 처방 지정 | `SetTargetHandles(vtkPolyData*)` — 절대 위치 | `HandleConfiguration::capture(after, before)` — diff |
| kernel | `IKernelFunction` 주입 (`CreateWendlandC2Kernel(radius)`) | 주입 지점 없음. 반경은 **handle 마다** `"SupportRadius"` array |
| solver | `SetSolverMethod` · `SetSolverNumberOfThreads(16)` | 노출 없음 (내부 PARDISO/MKL) |
| 고정점 | 호출자가 수동 복원 | `ApplyOptions::fixed_label` — 대상 grid 의 point-data array |
| 오류 | `bool` / 무반환 | `dash::core::Result<T>` |
| 재사용 | 없음 | `configuration()->displacement(other_motion)` 1줄 |

`Morph(vtkPoints*)` + `GetMorphedPoints()` 의 자리는 `operator()(std::span<const Vec3>)` 가
받는다. 클램프 없는 순수 변위장 평가라서, **GUI 의 기존 수동 고정점 복원 루프를 그대로 두면
동작이 보존된다** — `ApplyOptions` 경로로 옮기는 것은 선택이다.

### 1.2 수정 지점

| 파일 | 지점 | 성격 |
|---|---|---|
| [controller/DashMorphingEngine.h](../controller/DashMorphingEngine.h) | 전방 선언 2, 멤버 2 | 재작성 |
| [controller/DashMorphingEngine.cpp](../controller/DashMorphingEngine.cpp) | `MorphingConfiguration()` 전체, `ExecuteMorphing()` | **재작성** — 클래스의 존재 이유가 setter 시퀀스 캡슐화였다 |
| [model/geometry/DashMorphingUtils.h](../model/geometry/DashMorphingUtils.h) | `createMorphOperator()`, `performMorphingAndExport()` 시그니처 | 재작성 |
| [model/geometry/DashMorphingUtils.cpp](../model/geometry/DashMorphingUtils.cpp) | `createMorphOperator()` (187-195) | **삭제** — 신 API 에 대응 개념이 없다 |
| [model/DashModelRunner.cpp](../model/DashModelRunner.cpp) | 2169 | 호출부 |
| [model/DashOptimizer.cpp](../model/DashOptimizer.cpp) | 1479 | 호출부 (raw `new`, 누수 경로) |
| [controller/DashMorphingDoeExecutor.cpp](../controller/DashMorphingDoeExecutor.cpp) | include 2 | 개명 |
| [controller/DashMorphingController.cpp](../controller/DashMorphingController.cpp) | 46, 91 `MarchingPlaneBound` | **대응 없음** — §1.4 |

`DashMR::` 사용은 14곳 / 7파일이다.

### 1.3 handle polydata 에 `SupportRadius` 를 실어야 한다

GUI 의 handle 은 `DashHandlePickingInteraction::GetMorphingHandles()` 가 내는 `vtkPolyData`
이고, 15곳에서 소비된다. 이 polydata 는 `STATUS` · `LOCALNORMAL` · `SELECTION` array 를 갖지만
반경 array 는 없다 — 반경은 `DashMorphingEngine::m_morphingKernelRadius` 단일 double 이다.

`HandleConfiguration::create(vtkSmartPointer<vtkPolyData>)` 가 임의 handle 의 진입점이며
`"SupportRadius"` 를 필수로 요구하므로, **전역 반경을 point 수만큼 채운 array 를 추가하는 것이
최소 변경**이다. handle 별 반경은 그 뒤에 열리는 기능이다.

### 1.4 `MarchingPlaneBound` 는 대응 API 가 없다

`DashMorphingController.cpp:91` 이 쓰는 `MarchingPlaneBound` 는 `DashOptiMorphing` 이 제공하는
`vtkPolyDataAlgorithm` 파생 클래스다. `mesh-ops` 공개 표면(`BoxHandles` · `GroupHandles` ·
`sample_handles()`)에 등가물이 없다.

세 가지 처리 중 하나를 골라야 한다. **판단 전까지 `DashOptiMorphing` 을 제거할 수 없다.**

1. GUI 로 소스 이관 — `libs/DashGizmo` 선례를 따른다.
2. `mesh-ops` 에 상류 요청.
3. `sample_handles()` 로 대체 가능한지 검토 (기능 등가성 미확인).

---

## 2. preprocessor code 수정

`external/DashOptiPreprocessor-1.2.2` (`DashPR`) + `external/preprocessor` 스냅샷 → vcpkg
`preprocessor` (`dash::pr`).

GUI 는 이미 [IPreprocessorWrapper](../model/preprocessor/wrapper/IPreprocessorWrapper.h) 로
추상화돼 있고, **Abaqus 는 신 패키지의 호환 어댑터 `DashOptiPreprocessorAdaptor` 를, Ansys 는
legacy `DashPR::DashOptiPreprocessor` 를 쓴다.** 두 경로가 공존 중이다.

### 2.1 upstream 은 통합 공개 표면으로 재편됐다

`DashOpti_Preprocessor@2003d97` (origin/main) 의 설치 헤더는 `DashOptiPreprocessor.hpp` ·
`PluginLoader.hpp` · `Types.hpp` 셋뿐이다. `IContext` · `ModuleBuilder` 와 어댑터는 `source/`
로 내려가 **설치되지 않는다** — 즉 `external/preprocessor` 스냅샷이 의존하는
`Preprocessor/Common/DashOptiPreprocessorAdaptor.hpp` 는 vcpkg 산출물에 없다.

| 축 | 구 (양쪽 모두) | 신 `dash::pr` |
|---|---|---|
| 파일 지정 | `SetInputFilePathes(begin, end)` + `inputIdx` | 메서드마다 `const std::filesystem::path& file` |
| 응답 지정 | `std::string_view keyString` (JSON 텍스트) | `TimeSelector` · `DomainSelector` · `ResponseSelector` 불투명 토큰 |
| 반환 | `std::string` (JSON) / `vtkSmartPointer` | `Result<AnalysisInfo>`, `Result<std::vector<TimeStepEntry>>`, `Result<std::vector<DomainEntry>>`, `Result<std::vector<ResponseEntry>>` |
| 행렬 출력 | 없음 | `GetFieldOutput(...) -> Result<FieldOutputData>`, 다중 시점 `[T,N,C]` overload |
| 취소 | 없음 | `Cancel()` |
| 실행 모델 | in-process DLL | out-of-process worker |

### 2.2 수정 지점

| 파일 | 규모 | 성격 |
|---|---|---|
| [wrapper/IPreprocessorWrapper.h](../model/preprocessor/wrapper/IPreprocessorWrapper.h) | 8 메서드 | 인터페이스 재정의 — `inputIdx` 제거, 반환 타입 교체 |
| [wrapper/AbaqusPreprocessorWrapper.h](../model/preprocessor/wrapper/AbaqusPreprocessorWrapper.h) | 전체 | 어댑터 → 파사드. Abaqus 루트 탐색 로직은 유지 |
| [wrapper/AnsysPreprocessorWrapper.h](../model/preprocessor/wrapper/AnsysPreprocessorWrapper.h) | 전체 | `DashPR::` → `dash::pr::`. `useMotion` 분기는 로더 선택으로 유지 |
| [model/DashAnalysisLauncher.cpp](../model/DashAnalysisLauncher.cpp) | 4671줄, 생성 3곳 + 호출부 | 호출부 대량 |
| [preprocessor/DashResultXmlWriter.cpp](../model/preprocessor/DashResultXmlWriter.cpp) | 1162줄 | JSON 파싱 → 구조체 접근 |
| [preprocessor/DashResponseInitializer.cpp](../model/preprocessor/DashResponseInitializer.cpp) | 353줄 | 〃 |
| [preprocessor/DashResultProcessor.cpp](../model/preprocessor/DashResultProcessor.cpp) | 344줄 | 〃 |
| [preprocessor/PreprocessorQueryHelpers.h](../model/preprocessor/PreprocessorQueryHelpers.h) | 49줄 | **삭제** — term object 를 손으로 짓던 것을 selector 가 대체 |
| [enterprise/ILJIN_TensionlinkRule.cpp](../model/extensions/enterprise/ILJIN_TensionlinkRule.cpp) | 721줄 | 호출부 + JSON 파싱 |
| [enterprise/LGE_SpringRule.cpp](../model/extensions/enterprise/LGE_SpringRule.cpp) | 386줄 | 〃 |

**호출 지점 88곳 / 9파일, `QJsonDocument::fromJson` 29곳.** 네 축 중 가장 큰 작업이다.

`PreprocessorQueryHelpers.h` 가 다루던 `"substep"` / `"mode_index"` 키 분기와 Motion 의
`"state_id"` 는 `TimeSelector` 안으로 들어간다. **MODAL 에서 `modeIndex` 가 아닌 `substep` 을
넘겨야 한다는 현재의 함정이 API 수준에서 사라진다.**

### 2.3 포트 등록 완료 (2026-09-10) — 남은 것은 solver 버전 커버리지

`preprocessor` 는 레지스트리 `origin/main` 에 등록됐다 (`46e3915`, `2026-09-10.0`,
`versions/p-/preprocessor.json` · `baseline.json` 모두). 메타 저장소도 `vcpkg.json` ·
`repos.json` 에 `features: ["test"]` 로 멤버로 넣었다. [vcpkg-migration-scope.md](vcpkg-migration-scope.md)
§5 의 *"upstream 저장소가 없다"* 와 이 문서 이전 판의 *"포트 없음"* 은 **둘 다 해소됐다.**

포트는 세 플러그인을 모두 켜고 빌드한다 (`-DDASH_PR_WITH_ABAQUS=ON`,
`-DDASH_PR_WITH_ANSYS_MECHANICAL=ON`, `-DDASH_PR_WITH_ANSYS_MOTION=ON`). Motion 은 실체가
있다 — `source/AnsysMotion/` 의 `MotionContext.cpp` 1583줄 + `/clr` 브리지이고,
`AnsysMotion::config_json_text()` 가 `<root>/Motion/bin` 을 가리켜 Mechanical
(`aisol/bin/winx64`)과 다르다. **`PluginLoader.hpp` 의 "플러그인은 master plan Phase 5 에서
들어온다" 주석은 stale 하다** — 코드가 아니라 주석을 믿으면 안 된다.

**남은 확인 항목은 버전 커버리지다.** 포트가 만드는 플러그인 DLL 은 고정 목록이고, 워커는
`Preprocessor_<Tool>_V<version>.dll` 을 solver 루트의 버전으로 유도한다.

| 툴 | 빌드되는 버전 |
|---|---|
| Ansys Mechanical | `251` · `261` |
| Ansys Motion | `261` |
| Abaqus | `2020` (기본. `2024` 는 opt-in) |

고객 설치본이 이 목록 밖이면 `SetPlugin` 이후 첫 질의가 `NotFound` 로 실패한다. legacy
`DashOptiPreprocessor-1.2.2` 가 덮던 버전 범위와 대조하기 전에는 legacy 를 지울 수 없다.

---

## 3. Qt6 + VTK 버전 변경에 의한 수정 지점

`external/Qt-5.15.16` → vcpkg `qtbase` 6.x, `external/vtk-9.4` → vcpkg `vtk 9.3.0-pv5.12.0`.

### 3.1 앱 코드 (재검증 2026-09-10)

| 작업 | 곳 | 파일 | 판정 |
|---|---|---|---|
| `QtConcurrent::run(this, &C::m)` → `run(&C::m, this)` | 1 | 1 | **필수** — Qt6 에서 제거된 overload |
| `QFontDatabase db;` → static 호출 | 1 | 1 | **필수** — [view/DashOcctViewWidget.cpp:92](../view/DashOcctViewWidget.cpp#L92) |
| `.values().toVector()` → `.values()` | 1 | 1 | **필수** — Qt6 는 `QVector == QList` |
| `vtkGenerateIds` → `vtkIdFilter` | 1 | 1 | **필수** — VTK 9.3 에 없다. [controller/DashHandlePickingInteraction.cpp:295](../controller/DashHandlePickingInteraction.cpp#L295) |
| `QTextStream::setCodec("UTF-8")` → `setEncoding(...)` | 13 | 8 | 기계적 |
| `globalPos()` → `globalPosition().toPoint()` | 14 | ~8 | 기계적 (deprecated, 컴파일은 통과) |
| `QVariant::type()` → `typeId()` | 4 | 2 | 기계적 |
| `AA_EnableHighDpiScaling` 삭제 | 2 | 2 | 기계적 |

**필수 4곳 + 기계적 33곳.** 기계적 수정은 전부 Qt5 에서도 컴파일되므로 이행 전에 미리 넣을 수
있다.

### 3.2 수정 불필요 (재확인)

`SIGNAL()/SLOT()` · `QRegExp` · `QTextCodec` · `QStringRef` · `QDesktopWidget` ·
`Qt::MidButton` · `QSignalMapper` · `u8"` 리터럴이 **전부 0건**이다. `QAxObject` 5곳은 vcpkg
`qtactiveqt` 로 API 동일하게 온다.

`/Zc:char8_t-`([CMakeLists.txt:151](../CMakeLists.txt#L151))은 `u8"` 이 0건이므로 제거해도
무해할 전망이다. 제거 후 재컴파일로 확인한다.

### 3.3 VTK COMPONENTS 정정

현재 목록([CMakeLists.txt:250](../CMakeLists.txt#L250))은 통짜 VTK 설치라 우연히 동작한다.
vcpkg 는 요청한 컴포넌트 타깃만 주므로 링크와 `vtk_module_autoinit` 이 실패한다.

- **추가**: `FiltersGeneral`(`vtkClipDataSet`·`vtkCurvatures`),
  `FiltersPoints`(`vtkPoissonDiskSampler`), `FiltersVerdict`(`vtkMeshQuality`)
- **제거**: `jsoncpp`(vcpkg 는 `VTK_USE_EXTERNAL=ON` 이라 타깃 자체가 없다), `IOOCCT`,
  `RenderingQt`, `RenderingGL2PSOpenGL2`, `FiltersParallel`, `RenderingContextOpenGL2` (미사용)
- 목록에 `FiltersCore` · `FiltersExtraction` · `FiltersGeometry` 가 중복 기재돼 있다

---

## 4. 그 외 추가로 필요한 수정 지점

### 4.1 spdlog / fmt 상호 배제가 소멸한다

[vcpkg-migration-scope.md](vcpkg-migration-scope.md) §0 의 제약은 `DashOptiPreprocessor.dll` 과
`DashOptiMorphing.dll` 이 `fmt` v11 쌍을 implicit import 하기 때문에 생긴다. `bin/` 에 놓이는
사본 자체는 `external/additional/` 에서 온다 — CMakeLists 의 "Override additional" POST_BUILD
단계가 마지막에 덮어쓴다 ([build-environment.md 3절](scratchpad/build-environment.md)).

**§1 · §2 가 완료되면 v11 을 import 하는 주체가 없어진다.** 그 시점에 `external/additional`
override 블록은 존재 이유를 잃고 함께 삭제되며(§4.4), 제약이 소멸한다. 역으로 둘 중 하나만
옮기면 남은 DLL 이 계속 v11 을 요구하므로 제약이 그대로다 — **§1 과 §2 는 배포 시점을 함께
잡아야 한다.**

### 4.2 매니페스트 — baseline 범과 overrides 정책 충돌

`vcpkg-configuration.json` 의 레지스트리 baseline 은 `d64551f`(doe 머지 커밋)에 고정돼 있다.
`preprocessor` 는 그 뒤 `46e3915` 에 등록됐으므로 **baseline 을 `46e3915` 로 올려야 한다.**
같은 파일의 `packages` 배열은 현재 `cae-launcher` · `core-lib` 둘뿐이라, 소비할 패키지
(`preprocessor` · `mesh-ops` · `doe`)를 모두 추가해야 한다 — 빠지면 기본 레지스트리에서 찾다가
실패한다.

`vcpkg.json` 의 features 는 메타 저장소와 맞춘다: `preprocessor` · `doe` 는 `["test"]`,
`mesh-ops` 는 명시 없음(default).

`ports/mesh-ops/portfile.cmake` 는 소비자에게 `intel-mkl` 2023.2.0 핀을 요구하고, 메타 저장소
`vcpkg.json` 은 `opencascade 7.9.3#1` override 를 갖는다. GUI `vcpkg.json` 의 `$comment` 는
"overrides 없다" 를 정책으로 선언한다.

- `mesh-ops` 추가 시 GUI 최상위 매니페스트에 override 를 넣어야 한다 (포트 매니페스트의
  override 는 vcpkg 가 무시한다).
- override 추가는 전이 의존의 ABI 해시를 바꿔 **바이너리 캐시를 무효화한다.** 캐시 워밍이
  선행되지 않으면 `--only-binarycaching` 개발자에게 하드 실패다.
- **확인 필요**: 메타 `vcpkg.json` 에 현재 `intel-mkl` override 가 없다. 메타
  `docs/integration-surface-checklist.md` 는 유지 대상으로 적고 있어 두 문서가 어긋난다.

### 4.3 `doe` — 포트는 등록돼 있다. 막는 것은 spdlog 다

포트는 `DashOpti_Registry` `origin/main` 에 완전히 등록돼 있다 — `ports/doe/`,
`versions/d-/doe.json`(`2026-09-07.0`), `baseline.json` 항목까지 갖췄다. 그 머지 커밋
`d64551f` 는 **GUI `vcpkg-configuration.json` 이 이미 핀한 baseline 과 같은 커밋**이다.
따라서 baseline 을 올릴 필요가 없고, GUI 쪽 배관은 `vcpkg-configuration.json` 의 `packages`
배열과 `vcpkg.json` 의 `dependencies` 에 `"doe"` 를 넣는 것이 전부다.

막고 있는 것은 [vcpkg-migration-scope.md](vcpkg-migration-scope.md) §0 의 spdlog/fmt 충돌이다.
포트가 핀한 `DashOpti_DOE@fb0cc6f` 는 여전히 `spdlog::spdlog` 를 링크하므로
`DOE_DOE.dll` → `spdlog.dll` → `fmt.dll`(v12) 를 끌어오고, `external/` 의 legacy Preprocessor ·
Morphing 이 implicit import 하는 v11 쌍과 `bin/` 에서 충돌한다. 어느 쪽이 이겨도 EXE 가 시작되지
않는다.

해소 경로가 둘이고 **어느 쪽이든 하나면 된다**:

1. 상류 1줄 — `spdlog::spdlog` → `spdlog::spdlog_header_only`. 그 뒤 포트 REF 범.
2. §1 · §2 완료 — legacy DLL 두 개가 사라지면 v11 쌍이 없어져 충돌 자체가 소멸한다 (§4.1).

GUI 쪽 작업은 순수 개명 4패스이며 시그니처 변경 0건으로, 그 문서 §0b 의 판정이 유효하다.
다만 개명은 포트를 실제로 소비한 뒤에만 컴파일되므로 §3 처럼 미리 넣어 둘 수 없다.

### 4.4 CMakeLists.txt

| 작업 | 성격 |
|---|---|
| `Qt5` → `Qt6` (`find_package` 2회, `Qt5::` 링크, `Qt5_BIN_DIR`, UiTools) | 소 |
| `windeployqt` 경로 → `tools/Qt6/bin`, PATH 패치 로직 정정 (2곳) | 중 |
| `find_package(... HINTS ${EXTERNAL_DIR}/...)` 제거 — Morphing/DOE/Preprocessor/reader-writer/mesh-ops/VTK/OCCT | 삭제 |
| `mesh-ops` 의 `VTK_LIBRARIES` 보존 해킹 (314-317) | 재검토 — vcpkg 경로에서도 재현되는지 확인 |
| DLL 복사 `foreach` 루프 전부 + `external/additional` 오버라이드 | 삭제 |
| `cmake/stdext_compat.h` + `/FI` (2 타깃) | 삭제 — Qt 5.15 전용 shim |
| `/Zc:char8_t-` | 삭제 (§3.2) |
| `target_include_directories` 의 `external/preprocessor/include` · `external/reader-writer/include` | 삭제 — 임포트 타깃이 대신한다 |
| `external/eigen-3.4.0` 직접 include | vcpkg `eigen3` 로 전환 시 3.4.0 핀 필요 (baseline 5.0.1) |

`libs/DashGizmo` 는 앱과 같은 VTK 로 함께 빌드되므로 **수정 대상이 아니다.** `VTK_LIBRARIES`
를 물려받는 구조라 9.3 하향이 자동 반영된다.

### 4.5 유리하게 작용하는 것

- GUI 는 `DashRwActor` 에서 이미 `dash::core::Result` 를 쓴다 — `mesh-ops` · `preprocessor` 의
  `Result` 관용구가 새 개념이 아니다.
- `reader-writer` 는 레지스트리 포트가 이미 `vtk >= 9.3.0-pv5.12.0#4` 를 요구하므로 재빌드
  대상이 아니다.
- `external/reader-writer/bin/_bundled-extras` 419개 DLL, OCCT 3rdparty 6종 복사 블록이 소멸한다.

## 5. legacy 삭제 — `external/DashOptiMorphing-0.0.4` · `DashOptiPreprocessor-1.2.2`

**두 패키지의 제거가 이행의 목표 상태다.** 둘 다 사라져야 §4.1 의 `fmt` v11 쌍이 없어지고,
그 시점에 `doe` 의 유일한 blocker 도 함께 소멸한다. 하나만 지우면 아무것도 해소되지 않는다.

| | `DashOptiMorphing-0.0.4` | `DashOptiPreprocessor-1.2.2` |
|---|---|---|
| 앱 코드 소비 면 | 14곳 / 7파일 (§1.2) | **4줄 / 1파일** — `AnsysPreprocessorWrapper.h` 뿐 |
| CMakeLists | `find_package` 293-294, 링크 351, DLL 복사 447-457 | `find_package` 297-298, 링크 353, DLL 복사 473-483 |
| 대체 공급원 | vcpkg `mesh-ops` `2026-09-07.0` | vcpkg `preprocessor` `2026-09-10.0` |

> `DashPR::Utils::` · `DashPR::AnalysisFileDefines::` 35곳은 **legacy 패키지가 아니다.**
> [model/preprocessor/DashUtils.h](../model/preprocessor/DashUtils.h) 와
> [model/AnalysisFileDefines.h](../model/AnalysisFileDefines.h) 의 GUI 자체 정의이며 네임스페이스
> 이름만 같다. 삭제 대상이 아니고 개명할 이유도 없다.

### 삭제 선행 조건

`DashOptiMorphing` — 2건. 둘 다 GUI 저장소 안에서 끝난다.

1. §1.2 의 호출부 재작성 + §1.3 의 `SupportRadius` array.
2. `MarchingPlaneBound` 이관. 이 클래스는 surface 를 잘라 단면 중심점과 `SectionID` ·
   `Bounds` · `LocalToGlobal` array 를 내는 자족적인 `vtkPolyDataAlgorithm` 이다
   (`DashMorphingController.cpp:91-120`). `libs/DashGizmo` 선례대로 `libs/` 로 소스를 옮기는
   것이 가장 짧다 — `mesh-ops` 상류 요청을 기다릴 이유가 없다.

`DashOptiPreprocessor` — 2건. 포트 등록은 2026-09-10 에 끝났다 (§2.3).

1. §2.2 의 호출부 재작성 88곳. **선택이 아니다** — 설치 표면에서 어댑터
   (`DashOptiPreprocessorAdaptor`)가 빠졌으므로 현재의 `AbaqusPreprocessorWrapper.h` 는 vcpkg
   패키지에 대고 컴파일되지 않는다.
2. solver 버전 커버리지 대조 (§2.3 표).

### 순서 — 쪼갤 수 없다

`preprocessor` 를 레지스트리에서 받는 순간 `vcpkg-vtk` default-feature 가 **VTK 9.3** 을
끌어오고, 그 `qt` feature 가 **Qt6** 를 끌어온다. 두 포트 모두 공개 API 로
`vtkSmartPointer` 를 넘기므로 앱은 같은 VTK 를 링크해야 하고, `external/vtk-9.4` 와 병존할 수
없다. `default-features:false` 로 피하는 길도 없다 — 두 portfile 이 모두 금지한다.

따라서 **§1 · §2 · §3 과 두 legacy 삭제가 전부 한 배포**다. 지금 독립적으로 착수할 수 있는
것은 두 가지뿐이다.

- §3 의 기계적 수정 33곳 — Qt5 · VTK 9.4 에서도 컴파일된다.
- `MarchingPlaneBound` 를 `libs/` 로 이관 — GUI 저장소 안에서 끝난다.

`doe`(§4.3)는 이 배포 뒤에 자동으로 열린다. 그 전에 넣으려면 상류 1줄 수정이 필요하다.
