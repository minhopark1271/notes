# DashOpti_GUI 작업 목록 (재작성) — 모듈별

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> 기준: `dev` @ `b08a91b3` (2026-10-05). 원천: Projects #16 미종결 이슈 113건 · 결함 색인 201건 · 위키 설계 문서 · 현행 코드 대조. 틀·형식·과정은 `00-plan.md`.
> 작업 단위: 모듈 1 · 기제 1 · 동작 변경과 리팩터 혼합 금지. 종류 PR / DEC(결정) / INV(실측 선행) / EXT(외부 저장소) / CLOSE(기존 이슈 닫기 제안). 규모 S/M/L 는 추정. 태그 A~G 는 구 분류 축(데이터 무결성 · 실행 모델 · 데이터 모델·식별자 · UI 표준화 · 코드 구조 · 개발 인프라 · 출고 품질).

## 1. 집계

| MOD | 모듈 | 항목 | PR | DEC | INV | EXT | CLOSE | S | M | L |
|---|---|---|---|---|---|---|---|---|---|---|
| MOR | Geometry Parameterization — Morphing | 23 | 13 | 3 | 2 | 0 | 5 | 18 | 5 | 0 |
| CAD | Geometry Parameterization — CAD | 15 | 11 | 2 | 1 | 1 | 0 | 13 | 2 | 0 |
| CON | Condition Parameterization | 11 | 10 | 1 | 0 | 0 | 0 | 9 | 2 | 0 |
| DOE | DOE Sampler | 18 | 15 | 2 | 0 | 0 | 1 | 10 | 7 | 0 |
| LCH | Analysis Launcher — Launcher·배치·Direct | 34 | 20 | 5 | 1 | 1 | 7 | 28 | 5 | 1 |
| PRE | Analysis Launcher — Preprocess·결과 처리 | 32 | 24 | 3 | 4 | 0 | 1 | 18 | 10 | 4 |
| BLD | Model Builder | 20 | 18 | 1 | 1 | 0 | 0 | 13 | 7 | 0 |
| RUN | Model Runner | 33 | 31 | 2 | 0 | 0 | 0 | 24 | 9 | 0 |
| ANA | Results Analyzer | 23 | 21 | 1 | 1 | 0 | 0 | 17 | 5 | 1 |
| OPT | Optimizer | 24 | 23 | 1 | 0 | 0 | 0 | 22 | 2 | 0 |
| PRJ | Project · Set · Assets · Module Tree · 셸 | 36 | 25 | 6 | 0 | 0 | 5 | 19 | 11 | 1 |
| REN | VTK 씬 · 렌더링 | 13 | 11 | 2 | 0 | 0 | 0 | 10 | 3 | 0 |
| EXE | 실행 기반 | 22 | 11 | 4 | 1 | 0 | 6 | 14 | 8 | 0 |
| PER | 영속화 · 식별자 | 11 | 5 | 5 | 0 | 0 | 1 | 7 | 4 | 0 |
| UIC | UI 공통 | 25 | 18 | 5 | 1 | 0 | 1 | 15 | 7 | 3 |
| DEV | 개발 환경 · 빌드 · CI · 출고 | 24 | 13 | 5 | 1 | 5 | 0 | 19 | 5 | 0 |
| **합계** | | **364** | 269 | 48 | 13 | 7 | 27 | 256 | 92 | 10 |

태그 분포 (항목당 복수): A 138 · B 69 · C 69 · D 77 · E 106 · F 30 · G 16

## 2. 모듈별 작업 목록

### MOR — Geometry Parameterization — Morphing

> 기준 코드: dev @ b08a91b3. 열린 PR **#654**(핸들 상태기 · mesh-ops sampling · `Morphing.handles` v1 · MeshOps 0.5.0)가 `view/DashGeometryParameterWidget.*`·`controller/DashHandlePickingInteraction.*`·`controller/DashMorphingController.*`·`viewmodel/DashGeometryParameterPresentationModel.*`·`view/overlay/DashMorphingSettings.*`·`controller/DashMorphingDoeExecutor.cpp`·`model/geometry/DashMorphingUtils.*` 를 크게 바꾼다. 이 파일들을 만지는 항목은 전부 **#654 머지 후 착수**가 안전하고, 선행에 `PR #654` 로 적었다.
>
> 그 위에 쌓인 열린 PR **#655**(`refactor/430-handle-sets-render`, base #654, +6,722/−6,994, "Closes #430 · Closes #322 · Part of #427 · Refs #332")가 렌더·피킹·편집을 entry 상태로 통합하고 `m_handleGeometry`·`GizmoGroup`·`DashHandleImport`·`DashSampledHandleTree`·구 피킹 경로를 삭제한다 — 변경 파일 71개로 MOR 변경 범위 파일 대부분을 다시 쓴다. 아래 항목의 `선행` 은 #654 가 아니라 **#655** 머지 기준이고, 좌표는 머지 후 재측정이 필요한 곳에 표시했다. 충돌란의 열린 PR 은 D-1 `build_deps.py --apply` 가 파일 교집합으로 자동 기입한다.
>
> 원천별 claims 는 `02-claims/MOR.md`. #281 의 열린 PR 은 없다 — 잔여 판정은 이슈 본문 Phase 표 대 현행 코드로 했다.

#### MOR-01 · QC 결과 다이얼로그의 `processEvents` 를 걷고 `finished` 대기를 `setResults` 앞에 세운다
- 종류: PR | 규모: S | 태그: B · bug
- 목표: `DashMeshQualityDialog::setResults` 의 `processEvents(AllEvents, 100)` 를 삭제하고, 호출부가 `qCoro(dialog, finished)` awaitable 을 `setResults` 전에 만들어 둔다. 결과 표시 중 Esc/닫기가 코루틴을 영구 suspend 시키고 `qcDialog_` 가 non-null 로 굳어 Set Design Variable 이 세션 내내 "already running" 이 되는 경로가 사라진다.
- 완료 기준: (1) `view/dialog/DashMeshQualityDialog.cpp` 에 `processEvents` 0건 — MOR 영역 view pE 0 (2) `disconnect(cancelOnClose)` 와 `co_await` 사이에 시그널이 발화해도 결정이 수신된다 — "Analysis Complete" 직후 Esc → `qcDialog_` 가 비고 다음 클릭이 동작 (3) Step 1/2 → 2/2 진행 텍스트가 여전히 갱신된다
- 변경 범위: `view/dialog/DashMeshQualityDialog.cpp` · `view/DashGeometryParameterWidget.cpp` (`onSaveDesignVariableClicked` `:1456-1463`)
- 선행: -
- 충돌: PR #654 (`view/DashGeometryParameterWidget.cpp` 259/310 변경 — 같은 함수 구간은 아님) · B2 교집합: DashGeometryParameterWidget.cpp → DEV-10 MOR-02 MOR-03 MOR-17 MOR-22 MOR-23 UIC-20 · DashMeshQualityDialog.cpp → UIC-12 UIC-13 · PR #655(DashGeometryParameterWidget.cpp)
- 흡수: #512-1 · #512-2 · #512-3 · #455(MOR 몫) · #463(MOR 몫) · MOR-c15, MOR-c16, MOR-c17 · MOR-c79, MOR-c86 (← PRJ-c48, EXE-c23)
- 비고: 자동 테스트는 `tests/` 하네스에 Widgets 가 없어 불가(`tests/CMakeLists.txt:33`). 수동 시나리오 1건("결과 표시 직후 Esc → 재클릭 동작")을 PR 본문에 기록한다. #463 확산의 MOR 몫 — QC 진행 텍스트·취소(`cancelOnClose`)·프리뷰 세대 폐기(`previewStop_`)는 이미 있고, 남은 결함이 이 항목. 가드 형식은 EXE-07 · 09

#### MOR-02 · Constraints(고정 영역) 을 이름·셀 id 로 저장하고 Set 재진입 시 표와 오버레이를 복원한다
- 종류: PR | 규모: M | 태그: A, C · bug
- 목표: Set 저장이 `Morphing.constraints` 를 쓰지 않아 재진입·Set 전환 시 Constraints 표와 Non-design 영역이 사라지고, 그 상태에서 다시 Set 을 누르면 고정 영역이 빈 집합으로 덮여 DOE-Morphing 이 Non-design 없이 도는 비대칭을 없앤다. PR #654 가 세운 `Morphing.handles` v1 과 `DashFixedRegion` 위에 fixed 영역을 라벨(그룹 이름 + surface 셀 id)로 영속하고, 로드가 그룹별로 `appendConstraintTable` → 기존 시각화 사슬을 탄다. 구 형식(`AllFixedVolumeIds` 만 있는 VTP · `constraints[].node_ids`)은 PR #654 정책대로 변환하지 않는다.
- 완료 기준: (1) Constraints 지정 → Set → 모듈 재진입/Set 전환 후 표 행·오버레이·`fixedRegions` 가 같다 (2) 재진입 뒤 다시 Set 을 눌러도 고정 영역 수가 유지된다 (3) `test_handle_state`(또는 `TestFixedRegion`) 에 라벨 왕복 1건
- 변경 범위: `controller/DashHandleState.{h,cpp}`·`DashHandleStateJson.cpp`·`DashHandleDefinition.{h,cpp}`·`DashHandleRuntime.{h,cpp}` (PR #654·#655 신설) · `controller/DashFixedRegion.{h,cpp}` · `view/DashGeometryParameterWidget.cpp` (`loadMorphingFromJson`·`appendConstraintTable`·Set 수집) · `controller/DashHandlePickingInteraction.{h,cpp}` (`m_constraintSurfaceIds` 노출 — #655 에서 살아남지만 파일이 3,267 → 약 1,560줄로 줄어 `:3121`·`:3198` 좌표는 **머지 후 재측정**) · `tests/`
- 선행: PR #655
- 충돌: MOR-03 (같은 수집 경로) · MOR-15 · B2 교집합: DashGeometryParameterWidget.cpp → DEV-10 MOR-01 MOR-17 MOR-22 MOR-23 UIC-20 · DashHandlePickingInteraction.cpp → MOR-04 MOR-06 MOR-13 MOR-17 MOR-23 · DashHandlePickingInteraction.h → MOR-04 MOR-06 MOR-07 MOR-23 · DashHandleDefinition.cpp → MOR-05 MOR-17 · DashHandleDefinition.h → MOR-05 MOR-17 · DashHandleStateJson.cpp → MOR-05 MOR-17 · DashHandleState.cpp → MOR-06 · PR #654(DashFixedRegion.cpp·DashFixedRegion.h·DashGeometryParameterWidget.cpp·DashHandlePickingInteraction.cpp·DashHandlePickingInteraction.h·DashHandleState.cpp·DashHandleState.h·DashHandleStateJson.cpp)
- 흡수: #563 · MOR-D10 · MOR-c18, MOR-c19, MOR-c20, MOR-c23, MOR-c56
- 비고: #563 "기대" 의 스키마(JSON 이름·그룹 id + VTP 병렬 배열)는 PR #654 이후 VTP 가 없으므로 그대로 쓰지 않는다 — `DashFixedRegion` 에 PR #654 가 남긴 스펙 댓글(#563) 기준으로 설계한다. `referenceModel.uuid` 불일치 시 복원 건너뛰기는 유지

#### MOR-03 · Hide 상태 행도 Set 수집에 포함되게 표시 상태와 소속을 분리한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `updateConstraintVisualization` 이 Show 행만 `SetVisibleConstraintIds` 에 넘기고 그 함수가 `m_constraintSurfaceIds` 를 덮어쓰므로 Hide 상태로 Set 을 누르면 Non-design 이 축소 저장된다. Show/Hide 는 오버레이에만 관여하고, Set 수집은 표 전체 행을 쓴다.
- 완료 기준: (1) 행 하나를 Hide 한 채 Set → `fixedRegions`/고정 id 수가 Show 때와 같다 (2) 오버레이는 Hide 행을 그리지 않는다
- 변경 범위: `view/DashGeometryParameterWidget.cpp` (`updateConstraintVisualization:2957` — #655 가 `fixedRegionsChanged()` 3줄을 추가) · `controller/DashHandlePickingInteraction.{h,cpp}` (`SetVisibleConstraintIds:3198` 를 표시 전용으로, 소속은 별 setter). 두 좌표 모두 **머지 후 재측정**
- 선행: PR #655
- 충돌: MOR-02 (같은 함수 — MOR-02 에 합쳐도 됨, 단 동작 변경 2건을 한 PR 에 싣는 셈) · B2 교집합: DashGeometryParameterWidget.cpp → DEV-10 MOR-01 MOR-17 MOR-22 MOR-23 UIC-20 · DashHandlePickingInteraction.cpp → MOR-04 MOR-06 MOR-13 MOR-17 MOR-23 · DashHandlePickingInteraction.h → MOR-04 MOR-06 MOR-07 MOR-23 · PR #654(DashGeometryParameterWidget.cpp·DashHandlePickingInteraction.cpp·DashHandlePickingInteraction.h)
- 흡수: #563 부수 · MOR-c22
- 비고: -

#### MOR-04 · `m_nonDesignSurfaceIds` 와 `UpdateNonDesignFromUG()` 사문 코드를 지운다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: 유일 writer `UpdateNonDesignFromUG()` 호출부가 0 이라 항상 빈 집합인 `m_nonDesignSurfaceIds` 와 그 소비 분기 3곳을 삭제한다. 같은 성격의 사문 `DashMorphingUtils::applySurfaceExtraction`(정의만 있고 호출 0)도 함께 지운다. 실질 Non-design 소스는 Constraints 표 하나임을 코드가 말하게 한다.
- 완료 기준: (1) `UpdateNonDesignFromUG`·`m_nonDesignSurfaceIds`·`applySurfaceExtraction` grep 0건 (2) 빌드·`test_handle_cloud`·`test_fixed_region` 통과 (3) 고정 id 산출 결과 무변경
- 변경 범위: `controller/DashHandlePickingInteraction.{h,cpp}` (`:3121-3190`, `:1552`, `:1637`, `:3017`, `.h:207`·`:216`·`:279` — **머지 후 재측정**) · `model/geometry/DashMorphingUtils.{h,cpp}` (`.cpp:405`·`.h:67`)
- 선행: PR #655 (같은 파일 −1,707줄. `UpdateNonDesignFromUG`·`m_nonDesignSurfaceIds` 는 #655 무접촉으로 살아남는다)
- 충돌: MOR-02 · MOR-15 · B2 교집합: DashHandlePickingInteraction.cpp → MOR-03 MOR-06 MOR-13 MOR-17 MOR-23 · DashHandlePickingInteraction.h → MOR-03 MOR-06 MOR-07 MOR-23 · PR #654(DashHandlePickingInteraction.cpp·DashHandlePickingInteraction.h·DashMorphingUtils.cpp·DashMorphingUtils.h)
- 흡수: #563 부수 · #281-A(dead writer 몫) · MOR-c21, MOR-c89
- 비고: 동작 불변이라 MOR-02 와 섞지 않는다. `applySurfaceExtraction` 의 짝 `savePartAsVtu` 는 RUN-c56 소관

#### MOR-05 · Box(FFD) 핸들 생성 UI 를 되살릴지 정한다
- 종류: DEC | 규모: S | 태그: E, D · feature
- 목표: PR #655 가 GUI 의 shell 격자 box 생성 경로를 대체가 아니라 **삭제**했다 — `onGenerateBoxHandles`·`setHandlesBoxhandle`·`applyGenerateHandlesAsBox`·`GenerateAndShowBoxHandles`·`m_pendingBoxHandles`·`BoxHandleInfo`·Hexahedron 설정 페이지(`getHexaGridParams`·`generateHexaBoxHandlesRequested`·.ui) 전부. Box 엔트리는 JSON 으로만 들어오고 baseline 편집은 미지원(`transformed()` 거부)이다. #577 은 "복원이 아니라 mesh-ops `BoxHandles` FFD 신규(DV = 면 오프셋 `set_faces`, 기즈모 릴리즈 1회 반영)" 로 노선만 정해 두었다. 그 UI 를 실제로 만들지, 만든다면 mesh-ops lattice 가 내부까지 채우고 축당 분할 수가 하나(`num_subdivisions`)인 제약을 어디까지 수용할지 정한다.
- 완료 기준: 결정 기록 — (1) Volume → Hexahedron 생성 UI 신설 여부와 근거 (2) 신설이면 lattice·`num_subdivisions` 수용 범위, `gridX/Y/Z` UI 축소 여부, Box baseline 편집 처분 (3) 불요면 #499-1 · #577 의 닫기 사유
- 변경 범위: 결정이 "신설" 이면 후속 feature PR M — `view/overlay/DashMorphingSettings.{h,cpp}`·`ui/overlay/DashMorphingSettings.ui`(Hexahedron 페이지 재신설) · `controller/DashHandleDefinition.{h,cpp}`·`DashHandleStateJson.cpp`(Box 엔트리 생성·영속) · `view/overlay/DashMorphingBar.cpp:27`(Volume 목록) · `tests/TestHandleState.cpp`
- 선행: PR #655 (삭제 범위가 확정되는 시점)
- 충돌: B2 교집합: DashMorphingBar.cpp → DEV-10 MOR-14 UIC-07 · DashMorphingSettings.cpp → MOR-12 MOR-23 UIC-22 · DashHandleDefinition.cpp → MOR-02 MOR-17 · DashHandleDefinition.h → MOR-02 MOR-17 · DashHandleStateJson.cpp → MOR-02 MOR-17 · DashMorphingSettings.h → MOR-12 UIC-22 · PR #654(DashHandleStateJson.cpp·DashMorphingBar.cpp·DashMorphingSettings.cpp·DashMorphingSettings.h·TestHandleState.cpp)
- 흡수: #499-1 · #577 · MOR-c26, MOR-c90
- 비고: mesh-ops 에 shell/축별 옵션을 요청하는 쪽이면 EXT 가 선행. 결정이 "신설" 이면 #577 의 완료 기준(면 드래그 → Done → DV 표 face 행 → 범위 → 프리뷰 → Save → DOE · Set 재열기 후 유지)이 그대로 후속 PR 의 완료 기준이 된다

#### MOR-06 · marching plane 단면 핸들을 mesh-ops `section_frames` + `SectionFrameHandles` 로 대체하고 `libs/DashMarchingPlane` 을 삭제한다
- 종류: PR | 규모: M | 태그: E, F · refactor
- 목표: 남은 기제는 **절단기 교체**다 — PR #655 가 pending `MarchingPlaneData` → `SectionFrameHandles::create({.frame = f, …})` 생성까지 이미 넣었고, 자르는 쪽은 그대로 `MarchingPlaneBound`(vtkPolyDataAlgorithm, 상류 미머지 브랜치 출처, #655 무접촉)다. `onGenerateMarchingPlaneHandleRequested` 가 `marchingPlane->GetOutput()` 대신 `dash::mesh::section_frames(surface, start, end, N)` 를 쓰게 바꾸고, `MarchingPlaneData` pending 과 `libs/DashMarchingPlane`·`add_subdirectory`·ALIAS·install 항목을 제거한다. 끝 단면 skip 은 호출자가 목록에서 지운다.
- 완료 기준: (1) `libs/DashMarchingPlane` 디렉터리·`MarchingPlaneBound`·`MarchingPlaneData`·`m_pendingMarchingPlanes` grep 0건, `CMakeLists.txt` 에서 `DashMarchingPlane` 0건 (2) Volume 모드 Generate → Done 이 만드는 `SectionFrameHandles` set 의 단면 수·프레임이 교체 전과 같다 (3) Release·Debug 빌드·기동
- 변경 범위: `controller/DashMorphingController.{h,cpp}` (`:44`, `:76-203`) · `controller/DashHandlePickingInteraction.{h,cpp}` (`.h:42`·`:94-97`·`:332`, `Finalize` VOLUME 분기, `UpdateMarchingPlaneMarkers`) · `controller/DashHandleState*.cpp` · `CMakeLists.txt` (`:370-371`·`:404`·`:413`) · `libs/DashMarchingPlane/` 삭제 · `tests/`
- 선행: PR #655 (`SectionFrameHandles` 생성 경로가 거기 있다)
- 충돌: MOR-05 · MOR-07 (같은 `CMakeLists.txt` 블록) · MOR-15 · B2 교집합: CMakeLists.txt → DEV-11 DEV-21 DEV-24 DEV-25 UIC-02 · DashHandlePickingInteraction.cpp → MOR-02 MOR-03 MOR-04 MOR-13 MOR-17 MOR-23 · DashHandlePickingInteraction.h → MOR-02 MOR-03 MOR-04 MOR-23 · DashHandleState.cpp → MOR-02 · DashMorphingController.cpp → MOR-21 · DashMorphingController.h → MOR-21 · PR #658(CMakeLists.txt) · PR #654(CMakeLists.txt·DashHandlePickingInteraction.cpp·DashHandlePickingInteraction.h·DashHandleState.cpp·DashMorphingController.cpp·DashMorphingController.h)
- 흡수: #499-2 · #331-3 · MOR-c27, MOR-c42
- 비고: 단면당 중심점 1개 → 격자로 바뀌는 결과 차이는 PR #655 가 이미 만든 변화다. #331-3(상류 환원)은 이 대체로 불요. 규모는 파일 6개 + libs 삭제라 M 유지

#### MOR-07 · `libs/DashGizmo` 를 앱 소스 트리로 옮겨 단일 빌드로 만든다
- 종류: PR | 규모: M | 태그: F, E · refactor
- 목표: 독립 static 타깃 + `DashGizmo::DashGizmo` ALIAS 로 링크하던 Gizmo 소스를 `controller/gizmo/`(또는 `libs/` 밖 glob 범위) 로 옮겨 `DashOptGUI` 하나로 컴파일한다. `add_subdirectory`·ALIAS·`libs/DashGizmo/CMakeLists.txt`·install TARGETS 항목이 사라진다. 원본 `DashOpti_Gizmo` 와의 재동기화 정책(fork 유지 / 원본 아카이브 / GUI 정본 승격)을 README 에 기록한다.
- 완료 기준: (1) `libs/DashGizmo` 부재, 링크 목록에 `DashGizmo.lib` 부재, unresolved external 0 (2) `CMakeLists.txt` 에 `DashGizmo` ALIAS·`add_subdirectory` 0건 (3) Release·Debug 빌드·기동, 기즈모 조작 무회귀
- 변경 범위: `CMakeLists.txt` (`:366-368`·`:403`·`:413`) · `libs/DashGizmo/{include,src}/DashGizmo.{h,cpp}` 이동 (PR #655 가 `GizmoGroup.{h,cpp}` 를 삭제하므로 대상은 2파일) · `libs/DashGizmo/README.md` · include 경로 2파일(`controller/DashGizmoPlane.h`·`controller/DashHandlePickingInteraction.h` — `.cpp` 에는 include 없음) + 머지 후 신설 includer `controller/DashHandleGizmoEditor.cpp`
- 선행: PR #655 (`DashGizmo.h` +169/−74 · `DashGizmo.cpp` +497/−331 · `libs/DashGizmo/CMakeLists.txt` 수정 — 머지 전에 파일을 옮기면 #655 리베이스 비용이 생긴다)
- 충돌: MOR-06 (`CMakeLists.txt` 인접 블록) · B2 교집합: CMakeLists.txt → DEV-11 DEV-21 DEV-24 DEV-25 UIC-02 · DashHandlePickingInteraction.h → MOR-02 MOR-03 MOR-04 MOR-23 · README.md → DEV-01 DEV-02 DEV-12 DEV-21 DEV-24 · DashGizmo.cpp → MOR-08 · DashGizmo.h → MOR-08 · GizmoGroup.cpp → MOR-08 · GizmoGroup.h → MOR-08 · PR #658(CMakeLists.txt) · PR #654(CMakeLists.txt·DashHandlePickingInteraction.h)
- 흡수: #331-1 · MOR-c40
- 비고: VTK COMPONENTS(`CommonComputationalGeometry`·`CommonMath`·`CommonTransforms`)는 루트에 이미 있다(`:302`·`:306`). 서브 CMakeLists 의 `find_package(VTK)` 재호출 함정은 단일 빌드로 소멸

#### MOR-08 · 이관된 Gizmo 소스의 표기 관례를 저장소 규칙에 맞춘다
- 종류: PR | 규모: S | 태그: G, E · refactor
- 목표: 원본 레이아웃 보존을 위해 미뤘던 `_position` 식 선행 밑줄 등 표기를 `.clang-format`·`.clang-tidy`(#321 Done) 규칙으로 정리한다. MOR-07 로 `libs/` 가 사라지면 "원본 diff 대응" 예외 근거도 함께 사라진다. PR #655 의 "기즈모 서식" 커밋은 clang-format 만 적용했고 `_position`·`_euler_angles`·`_object_scale`·`_screen_pixels`·`_range_min` 식 표기는 그대로다.
- 완료 기준: (1) `scripts/hooks/run-format-checks.sh` 가 이동된 2파일(`DashGizmo.{h,cpp}`)을 통과 (2) 동작 무변경 — 기즈모 수동 시나리오 (3) 결정 기록: 규칙 적용 여부(예외 유지면 그 근거)
- 변경 범위: `DashGizmo.{h,cpp}` (MOR-07 이후 위치 — `GizmoGroup.{h,cpp}` 는 PR #655 가 삭제)
- 선행: MOR-07
- 충돌: B2 교집합: PR #655(DashGizmo.cpp·DashGizmo.h·GizmoGroup.cpp·GizmoGroup.h)
- 흡수: #331-2 · MOR-c41
- 비고: -

#### MOR-09 · #322 닫기 — PR #655 가 `GizmoGroup` 을 삭제해 정리할 컨테이너가 없어진다
- 종류: CLOSE | 규모: S | 태그: E
- 목표: 닫기 사유 기록. `_members`·`_active`·`_savedState` 병렬 컨테이너와 `removeMember` 리인덱싱·`setChecked` 재진입 오염은 PR #655 가 `libs/DashGizmo/{include/GizmoGroup.h,src/GizmoGroup.cpp}` 를 통째로 삭제하고 `libs/DashGizmo/CMakeLists.txt` 에서 `src/GizmoGroup.cpp` 를 빼면서 함께 사라진다. 핸들 기즈모는 `DashHandleGizmoEditor` 가 entry 단위로 만든다. PR 본문이 "Closes #322" 로 못박았다.
- 완료 기준: 닫기 사유 — PR #655 머지 확인 후 닫는다 · 머지 후 `git grep GizmoGroup` 0건 · 머지가 깨지면 MOR-c38 을 PR 항목(규모 M)으로 되살린다
- 변경 범위: -
- 선행: PR #655
- 충돌: -
- 흡수: #322 · MOR-c38, MOR-c39 · MOR-c80 (← REN-c31, #322 몫)
- 비고: `_recalculateCentroid` 의 평균 방향 roll 소실·`GetRangeMin/Max` 우회·`_members` raw 포인터 수명 계약은 #322 not-to-be 로 범위 밖이었고 타입 삭제로 소멸한다. `external/DashGizmo` 사본은 gitignore 대상이라 처리 불요

#### MOR-10 · DV-Geometry `source` 가 없는 GP 세트의 배치·단건 동작을 하나로 정한다
- 종류: DEC | 규모: S | 태그: A, C
- 목표: 같은 세트에 대해 DOE 배치(`DashMorphingDoeExecutor::plan`)는 WARN 후 Target Component 만 검증하고 진행하고, Optimizer·ModelRunner(`validateMorphingTarget` "names no part")는 거부한다. 하드 실패(세트 재저장 유도) 또는 진행(그러면 `source` 를 채우는 마이그레이션 유무) 중 하나로 결정하고 세 경로를 맞춘다.
- 완료 기준: 결정 기록 — (1) 선택지와 근거 (2) 세 호출부(`DashMorphingDoeExecutor.cpp:404-421` · `DashModelRunner.cpp:2291` · `DashOptimizer.cpp:1532`) 의 목표 동작 (3) 결정이 "진행" 이면 마이그레이션 여부(PR #654 의 "구 Set 변환 없음" 정책과 정합)
- 변경 범위: 결정 후 PR 은 `controller/DashMorphingDoeExecutor.cpp` 1줄 (+ RUN·OPT 각 1줄 — 접점)
- 선행: -
- 충돌: PR #654 (`DashMorphingDoeExecutor.cpp` 18/60) · #434 (part 를 Set 상태로 — 4단계가 이 검사를 없앤다, `:383` TODO) · B2 교집합: DashMorphingDoeExecutor.cpp → LCH-13 MOR-11
- 흡수: #557 · MOR-c43, MOR-c44
- 비고: #434 4단계가 먼저 오면 이 결정은 소멸한다 — PRJ(#434) 진척을 확인한 뒤 결정한다

#### MOR-11 · 모핑 반경 기본값 10.0 의 소유자를 하나로 하고 대역 사용을 WARN 으로 남긴다
- 종류: PR | 규모: M | 태그: A, E · refactor
- 목표: `.ui` 스핀박스 · `DashGeometryParameter::m_morphingRadius` · `kDefaultMorphingKernelRadius` · `DashMorphingDoeExecutor::m_kernelRadius` · ModelRunner/Optimizer 의 `toDouble(10.0)` 여섯 곳이 각자 들고 있는 10.0 을 소유자 1곳(`DashGeometryParameter` · 도메인 상수 · 또는 PR #654 가 세운 상태기 `DashHandleSetup::radius()` 중 하나)에서 읽게 하고, `Morphing.radius` 를 읽는 함수 3개를 값 타입 하나 + `FromJson` 하나로 모아 같은 파서·같은 대역·같은 WARN 을 쓰게 한다. 값 자체(10.0)는 바꾸지 않는다.
- 완료 기준: (1) 리터럴 `10.0` 이 반경 의미로 남은 곳 1 — 건수는 PR #654 머지 후 재측정 (2) `radius` 키 없는 JSON 으로 DOE·Runner·Optimizer 실행 시 WARN 1줄 (3) `.ui` 값은 `setValue` 로 대체하거나 소유자와 같음을 테스트로 고정
- 변경 범위: `ui/DashGeometryParameterWidget.ui:130` · `model/DashGeometryParameter.{h,cpp}` (`.h:93`·`.cpp:212`) · `controller/DashMorphingBasis.h:31-35` · `controller/DashMorphingDoeExecutor.{h,cpp}` (`.h:97`·`.cpp:338`) · `view/DashGeometryParameterWidgetHandles.cpp` (PR #654 신설 — `persistHandleSetup` 이 `morphing["radius"] = handleSetup()->radius()` 로 쓴다) · `model/DashModelRunner.cpp:2344` (RUN 접점) · `model/DashOptimizer.cpp:1462` (OPT 접점)
- 선행: PER-10 (초기값 정책 — 있으면 따른다; 없어도 #423 초안 정책으로 착수 가능) · PR #654 (`Morphing.radius` 쓰기 정본이 하나 늘어 6곳 집계가 바뀐다)
- 충돌: PR #654 (`e82b7ba` 반경 변경 시 상태 재구축 — `DashGeometryParameterWidget`·`DashModelRunner.cpp`·`DashOptimizer.cpp` 수정) · B2 교집합: DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashGeometryParameter.cpp → PRJ-09 UIC-20 · DashMorphingDoeExecutor.cpp → LCH-13 MOR-10 · DashGeometryParameterWidget.ui → UIC-10 · DashGeometryParameterWidgetHandles.cpp → MOR-22 · DashMorphingDoeExecutor.h → LCH-13 · PR #655(DashGeometryParameterWidget.ui·DashGeometryParameterWidgetHandles.cpp)
- 흡수: #423 (모핑 반경 사례) · MOR-c45
- 비고: #423 의 1·2 단계(전수 조사·정책 문서)는 횡단이라 PER 로 넘겼다(MOR-c46). 이 항목은 3 단계 첫 사례

#### MOR-12 · Morphing Settings 의 Generate 분기를 `isVisible()` 캐스케이드에서 현재 페이지 키로 바꾼다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `m_generateButton` 클릭 람다가 설정 위젯의 `isVisible()` 을 순서대로 검사해 신호를 고르는 구조를 — dev 는 7단, PR #654 가 cylinder·PR #655 가 hexahedron 분기를 지워 머지 후 5단(automatic · parametric×2 · physics · marching) — `swapSettingsWidget` 이 세우는 현재 페이지 enum 하나로 분기하게 한다. 페이지를 추가해도 캐스케이드 순서가 계약이 되지 않는다.
- 완료 기준: (1) 람다 안 `isVisible()` 0건 (2) 남은 모드 전부 × Generate 가 같은 신호를 낸다 (3) 빌드·기동
- 변경 범위: `view/overlay/DashMorphingSettings.{h,cpp}` (`:111-160`, `swapSettingsWidget` — 좌표는 머지 후 재측정)
- 선행: PR #655 (같은 파일 −213/−110: Advanced·Hexahedron 제거)
- 충돌: MOR-05 (Hexahedron 페이지) · B2 교집합: DashMorphingSettings.cpp → MOR-23 UIC-22 · DashMorphingSettings.h → UIC-22 · PR #654(DashMorphingSettings.cpp·DashMorphingSettings.h)
- 흡수: MOR-D3 · MOR-c49
- 비고: 머지 후 분기 5단에서 재측정하고 착수한다. MOR-05 결정이 "Hexahedron 신설" 이면 페이지가 하나 늘어 이 항목이 먼저 오는 쪽이 싸다

#### MOR-13 · `MODE_PHYSICS` 를 `SetInteractionMode` 의 switch 에 넣는다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: 툴바 Physics 버튼이 `MODE_PHYSICS` 를 세우지만 switch 에 case 가 없어 `default: break` 로 떨어져 픽킹 방식이 직전 모드에서 이월된다. 의도한 `PickingMode`(File Import 페이지는 픽킹 없음 → `MODE_CLICK` + `m_boxWidget->Off()` 추정)를 명시한다.
- 완료 기준: (1) Constraints(박스) → Physics 로 전환하면 박스 위젯이 꺼진다 (2) Physics → Manual 왕복 무회귀
- 변경 범위: `controller/DashHandlePickingInteraction.cpp:1308-1346` — PR #655 가 `SetInteractionMode` 를 `:928` 로 옮기고 파일을 −1,707줄 바꾸므로 **머지 후 재측정**
- 선행: -
- 충돌: B2 교집합: DashHandlePickingInteraction.cpp → MOR-02 MOR-03 MOR-04 MOR-06 MOR-17 MOR-23 · PR #655(DashHandlePickingInteraction.cpp) · PR #654(DashHandlePickingInteraction.cpp)
- 흡수: MOR-U1 · MOR-c61
- 비고: 어느 픽킹 모드가 맞는지는 1줄 결정. 확정 전이면 `MODE_CLICK` 으로 두고 PR 에 기록

#### MOR-14 · 툴바 Prev/Next 의 처분을 정한다 — 버튼 제거 또는 Undo/Redo 구현
- 종류: DEC | 규모: S | 태그: D, G
- 목표: `DashMorphingBar` 의 `stepPrevClicked`/`stepNextClicked` 는 emit 만 하고 수신처가 없다. `DashMainWindow::onEditUndo/onEditRedo` 의 TODO 와 짝이다. (a) 버튼·시그널·`.ui` 항목을 지운다, (b) 모핑 편집 undo 스택을 설계한다 중 하나를 정한다.
- 완료 기준: 결정 기록. (a) 면 후속 PR S — `view/overlay/DashMorphingBar.{h,cpp}`·`ui/DashMorphingBar.ui`·`DashMainWindow` `ResetMorphingBar` 분기. (b) 면 별도 설계 항목
- 변경 범위: `view/overlay/DashMorphingBar.{h,cpp}` (`.h:44-45`·`.cpp:67-68`) · `ui/` 대응 · `view/DashMainWindow.cpp:4800-4810` (PRJ 접점)
- 선행: -
- 충돌: B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashMorphingBar.cpp → DEV-10 MOR-05 UIC-07 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp·DashMorphingBar.cpp) · PR #652(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: MOR-U2 · MOR-c62
- 비고: 출고 품질(G) 관점에서 (a) 가 값싸다. Edit 메뉴 Undo/Redo 자체의 처분은 PRJ 몫

#### MOR-15 · #430 닫기 — PR #655 가 interaction 의 핸들 소유를 해제했다
- 종류: CLOSE | 규모: S | 태그: E, C
- 목표: 닫기 사유 기록. #430 의 "PR 2" 가 PR #655 다 — `m_handleGeometry` 를 삭제하고 렌더를 set 의 `handle_output_port()`·`control_output_port()` 에 직접 붙이며(`DashHandleEntryRenderer`), `DashHandleImport`·`DashSampledHandleTree`·구 피킹 경로(약 1,900줄)와 `.cpp:1409` TODO 를 지운다. 원문의 VTP 읽기 5곳·쓰기 2곳 일원화는 PR #654 가 VTP 자체를 없애 소멸했고, `DashHandleData` 타입 신설은 `DashHandleDefinition` + `DisplacementPolicy` 가 대신한다. PR 본문이 "Closes #430" 이다.
- 완료 기준: 닫기 사유 — PR #655 머지 확인 후 닫는다 · 머지 후 `git grep m_handleGeometry` 0건 · 잔여를 MOR-23(INV)으로 분리했음을 명시 · 머지가 깨지면 MOR-c33 을 PR 항목(규모 L)으로 되살린다
- 변경 범위: -
- 선행: PR #655
- 충돌: -
- 흡수: #430 · MOR-D4 · MOR-c33, MOR-c34, MOR-c50 · MOR-c80 (← REN-c31, #430 몫)
- 비고: L 사유였던 "빌드 가능한 분할선이 보이지 않는다" 는 #655 가 해소했다. HDVS ⓒ-2·ⓓ·ⓕ 의 잔여(`UpdateSurfaceGeometry` 분해 · `.h:36` TODO · view/viewmodel 직접 쓰기 · `DashMorphingSettings` 표면 배열 2곳)는 MOR-23 이 받는다

#### MOR-16 · 모핑 서비스에 동결·실행 소요 시간 계측을 넣는다
- 종류: PR | 규모: S | 태그: B · perf
- 목표: `DashMorphingService::submitFreeze`/`submitMorph` 가 요청 단위로 동결 시간과 실행 시간을 따로 재서 DEBUG 로그에 남긴다. 레인당 고정 `코어/2` 예산의 동적 재배정과 프리뷰 응답성 판단의 입력이 된다(#313 이후 모핑 1회 비용 미측정).
- 완료 기준: (1) 프리뷰 1회·QC 1회·DOE 샘플 1회의 로그에 `freeze ms`·`morph ms` 가 핸들 수와 함께 남는다 (2) `test_morphing_service` 무회귀
- 변경 범위: `controller/DashMorphingService.cpp` (`:140-182`) · 필요 시 `controller/DashMorphingRun.cpp`
- 선행: -
- 충돌: PR #654 (`DashMorphingService.h` +9줄)
- 흡수: #281 Follow-up ⑷ (#408 이월) · MOR-c12
- 비고: 계측값이 나오면 예산 재배정은 별 항목(DEC)으로 올린다

#### MOR-17 · PR #655 머지 후 레거시 핸들 경로의 정본 결함 3건을 재판정한다 — 이름 미저장 · θ 왕복 · 범위값 정본
- 종류: INV | 규모: S | 태그: A, C · bug
- 목표: 현행 dev 에서 유효한 MOR-D5(핸들 이름 writer 0 — `HandleNames` 배열 읽기만 있음), MOR-D6(θ 는 벡터로만 저장, 표시는 Euler 역산), MOR-D9(저장이 트리 셀 스핀박스를 읽음)를 바꾸는 것은 #654 가 아니라 **PR #655** 다 — entry `displayName` JSON 영속(D5), θy/θz 두 각 + `withAngle()` + `eulerAnglesRoundTripAndPole` 테스트 + 행의 θ 입력 셀 삭제(D6), `DashHandleTree` 의 `committed` 프로퍼티·행 제자리 갱신(D9). 머지된 코드에서 세 결함이 어느 경로에 남는지 실측하고, 남으면 각각 PR S 를 연다.
- 완료 기준: 실측 결과 — (1) 이름·θ·범위 각각 정본 위치와 영속 여부 표 (2) 잔존 결함별 후속 항목 또는 "해소" 근거 커밋
- 변경 범위: 조사 대상 `view/DashGeometryParameterWidget.cpp` (`:1148-1200`·`:345`·`:564`·`:2387-2420`) · `controller/DashHandlePickingInteraction.cpp:1978-2000` · `controller/DashHandleDefinition.{h,cpp}` · `controller/DashHandleStateJson.cpp` · `view/common/DashHandleTree.cpp` — 좌표는 모두 **머지 전 기준**이고 #655 에서 이동·삭제된다
- 선행: PR #655
- 충돌: B2 교집합: DashGeometryParameterWidget.cpp → DEV-10 MOR-01 MOR-02 MOR-03 MOR-22 MOR-23 UIC-20 · DashHandlePickingInteraction.cpp → MOR-02 MOR-03 MOR-04 MOR-06 MOR-13 MOR-23 · DashHandleDefinition.cpp → MOR-02 MOR-05 · DashHandleDefinition.h → MOR-02 MOR-05 · DashHandleStateJson.cpp → MOR-02 MOR-05 · PR #654(DashGeometryParameterWidget.cpp·DashHandlePickingInteraction.cpp·DashHandleStateJson.cpp)
- 흡수: MOR-D5 · MOR-D6 · MOR-D9 · MOR-c51, MOR-c52, MOR-c55
- 비고: D6 의 처방은 PR #655 가 세운 구조(direction = Rz(θz)·Ry(θy)·X, 한 칸 편집은 `withAngle()` 로 그 축만, 기즈모 링은 두 각을 함께 바꿀 수 있다)에서 남는 레거시 경로만 대상으로 정한다

#### MOR-18 · #281 닫기 — 모핑 축 진입점 이관은 끝났고 잔여는 OPT 측 펌핑 2곳뿐
- 종류: CLOSE | 규모: S | 태그: B, E
- 목표: 닫기 사유 기록. Phase A(dead code)·B1(값 경계)·B2(전용 세션 → 불변 문서)·B3(엔진 격리)·C(QC 코루틴)·E(ModelRunner 코루틴) 전부 dev 에 있고, `MorphingGate`·`WorkerJob`·`morphingSerialPool` 전제는 #408 이 폐기했다. 프리뷰 축(Follow-up ⑴)·DLL `LocalScope`(⑶)·`onDeleteHandles` 재-arm(⑤) 도 해소. 남는 것은 `view/DashOptimizerWidget.cpp:1698`·`:1724` 의 `processEvents` 2곳과 모핑 중 Preview 버튼 사전 비활성 — OPT-04 · OPT-22.
- 완료 기준: 닫기 사유 — 위 Phase 별 근거 좌표(`02-claims/MOR.md` c01~c14) · 잔여를 OPT 로 이관했음을 명시 · RW 경합 계측(⑵)은 EXE
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #281 · 281-1 wiki · MOR-c01~c05, MOR-c07, MOR-c08, MOR-c09, MOR-c11, MOR-c13, MOR-c14, MOR-c77 · MOR-c82 (← EXE-c47)
- 비고: 배정표에서 #281 을 MOR 담당에서 빼고 OPT 접점(`onPreviewButtonClicked` 펌핑)으로 옮기는 것을 제안

#### MOR-19 · #427 닫기 — 추적 전용 부모, 격리 몫은 끝났다
- 종류: CLOSE | 규모: S | 태그: E
- 목표: 닫기 사유 기록. 서브 #428·#429 Done, 배치가 화면 상태를 되돌리던 원복 코드는 없다(`DashDoeBatchChain.cpp:230` "No restore", `DashMorphingDoeExecutor` 에 interaction 참조 0). #281 몫(B1·B2) 완결. 남은 서브 #430 은 MOR-15, 렌더러 축 #316·#318·#319 는 REN 항목으로 각자 추적한다.
- 완료 기준: 닫기 사유 + 잔여 서브의 새 항목 ID. 닫기 사유에 (1) 원복 코드가 dev 에 없다는 판정(`controller/DashDoeBatchChain.cpp:230` "generation is immutable. No restore") — PR #655 본문이 "원복 코드 삭제는 #427 마무리 몫" 으로 남긴 항을 이것으로 해소 (2) #430 은 PR #655 머지로 닫힘 (3) 렌더러 액터 소유권 축(#318 · #319)은 REN 항목으로 분리 제안 — 을 적는다
- 변경 범위: -
- 선행: PR #655 (#430 close) · REN-01~REN-10 (#319 → REN-01~04 · #318 → REN-05~10 축의 닫힘 — #316 은 OPT)
- 충돌: -
- 흡수: #427 · MOR-c36, MOR-c37
- 비고: 렌더러 축까지 #427 완료 기준에 묶어 두면 REN 10항목이 끝날 때까지 닫지 못한다 — 그 축을 #427 에서 떼는 제안을 닫기 코멘트에 함께 적는다

#### MOR-20 · #332 닫기 — PR #654 가 2번(sampling 치환)을 실행하고 1번(per-handle 반경)을 결정으로 종결했다
- 종류: CLOSE | 규모: S | 태그: E
- 목표: 닫기 사유 기록. `selectHandlesGreedyByUnit`·`wendlandC2`·Eigen include 제거와 `sample_handles` 정책 래퍼(`DashHandleSampling`)는 PR #654 In review. per-handle `SupportRadius` 는 "반경은 Set 전체에 하나, set 안 값은 파생" 으로 결정(#332 1번 종결 댓글). #327(K 클램프)도 같은 PR 이 닫는다.
- 완료 기준: PR #655 머지 확인 후 닫기 — #332 는 "PR 2(interaction 의 핸들 소유 해제, #430) 병합 시 닫는다"(#332 댓글 10-04)이고 그 PR 2 가 #655 다. 머지가 깨지면 c31 을 PR 항목으로 되살린다 · 머지 후 `git grep Eigen -- controller/` 0건
- 변경 범위: -
- 선행: PR #655
- 충돌: -
- 흡수: #332 · #305(MOR 몫 — 죽은 `#include <Eigen/Dense>`) · MOR-c30, MOR-c31, MOR-c32 · MOR-c78 (← ANA-c08)
- 비고: `DashNonDesignUtils.cpp:292` `TODO(#332-2)` 는 PR #654 가 그 함수를 지운다. PR #654 diff 가 `controller/DashHandlePickingInteraction.cpp:2` 의 `#include <Eigen/Dense>`(사용 0, ANA-c08 이관) 도 지운다 — 머지가 깨지면 1줄 PR

#### MOR-21 · `DashMorphingController` 의 남은 생성 알고리즘을 프리뷰 액터에서 떼어 자유 함수로 만든다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: PR #654(greedy·automatic·cylinder −396줄) · MOR-05(box) · MOR-06(marching plane) 뒤에도 `DashMorphingController` 는 parametric 선택(`onGenerateCurvatureHandles`·`onGenerateDistanceHandles`)·physics 클러스터(`createCluster`·`readCSVFile`)와 프리뷰 액터 3종(`createPhysicsPreviewForRow`·`visualizeClusterSamples`·marching plane 프리뷰)을 함께 든다. 순수 계산을 `DashNonDesignUtils` 형(싱글턴 0건 자유 함수)으로 떼고 컨트롤러는 입력 수집·프리뷰 표시만 남긴다.
- 완료 기준: (1) 분리된 TU 에 `DashManager::Mgr()`·`vtkActor`·`vtkRenderer` include 0건 (2) 컨트롤러 `DashManager::Mgr()` 16 → 프리뷰 표시 몫만 (3) parametric·physics Generate 결과 무회귀 + 분리 함수 단위 테스트 2건
- 변경 범위: `controller/DashMorphingController.{h,cpp}` · 신설 `controller/DashHandleGenerators.{h,cpp}`(가칭) · `tests/`
- 선행: PR #655 · MOR-06 · MOR-05 (DEC — "Box UI 신설" 로 결정되면 생성기가 하나 늘어 범위를 다시 잰다)
- 충돌: B2 교집합: PR #654(DashMorphingController.cpp·DashMorphingController.h)
- 흡수: Handle-Data-View-Separation "인접 혼합체" · MOR-c76
- 비고: 선행 뒤 잔여 규모를 다시 잰다 — 1,561줄 중 얼마가 남는지에 따라 S 로 줄 수 있다. 직접 renderer 조작 집계도 머지 후 전부 바뀐다(#655 가 Visualizer −476 · Interaction −1,707 · MorphingController −146 · DashGizmo 재작성) — dev 실측은 controller 21곳(MorphingController 11 · Interaction 6 · Visualizer 4) + `libs/DashGizmo/src/DashGizmo.cpp` 10곳이고, 매니저 경유화는 #318 범위 제외 유지라 머지 후 별 S 후보

#### MOR-22 · 모핑 설정 JSON 쓰기 3곳을 공용 파일 헬퍼로 옮긴다
- 종류: PR | 규모: S | 태그: A · refactor
- 목표: 세 곳이 각자 들고 있는 파일 입출력을 PER-02 의 `DashSaveSystem` 헬퍼(공용 진입점 — `read/writeJsonFile`, QSaveFile 원자 쓰기 · 길이 검사 · 사유 반환) 호출로 바꾼다 — (a) `setupMorphingTab` 의 `applyRadius` 람다(위젯, `QFile` 직쓰기 RMW `Morphing.radius`, PR #654·#655 무접촉) (b) `DashGeometryParameterWidget::persistHandleSetup()`(PR #654 신설, `QFile` 읽기 → `Morphing.handles/radius` 교체 → 자체 `QSaveFile`) (c) PM `saveMorphingSettings`(PR #654 가 자체 `QSaveFile` + 길이 검사 + `commit()` 로 바꾼 코드). 포맷 불변.
- 완료 기준: (1) 세 함수에 `QFile`·`QSaveFile`·`QJsonDocument::fromJson` 직접 호출 0 (2) 읽기 전용 경로에서 Set·반경 변경이 실패해도 기존 파일 바이트가 같고, 헬퍼가 돌려준 사유가 기존 로그 경로에 남는다 (3) `test_handle_state`(JSON) 무회귀
- 변경 범위: `viewmodel/DashGeometryParameterPresentationModel.cpp` (`saveMorphingSettings` :337-402) · `view/DashGeometryParameterWidget.cpp` (`setupMorphingTab` applyRadius :683-712) · `view/DashGeometryParameterWidgetHandles.cpp` (`persistHandleSetup` — PR #654 신설). 좌표는 머지 후 재측정
- 선행: PER-02 · PR #655 (세 함수 모두 머지 대상 — `Morphing.handles` v1 쓰기 · `e82b7ba` 반경 재구축)
- 충돌: MOR-02 (PM 저장 경로) · MOR-11 (`applyRadius`·`persistHandleSetup` 이 같은 반경을 쓴다 — 소유자가 옮겨가면 이 쓰기도 따라간다, 순서 조율) · B2 교집합: DashGeometryParameterWidget.cpp → DEV-10 MOR-01 MOR-03 MOR-17 MOR-23 UIC-20 · DashGeometryParameterPresentationModel.cpp → MOR-23 · PR #654(DashGeometryParameterPresentationModel.cpp·DashGeometryParameterWidget.cpp·DashGeometryParameterWidgetHandles.cpp)
- 흡수: #479(MOR 몫) · #478(MOR 몫) · #480(MOR 몫 — PER-04 뒤 버전 키 자동) · MOR-c83 (← PER-c22, 3곳)
- 비고: 동작 변경은 넣지 않는다 — 통지는 헬퍼가 돌려준 사유를 기존 로그 경로에 싣는 데까지다. PER-c22 의 세 번째 지점 `model/DashDesignVariableModel.cpp:saveToJsonFiles` 는 공용 모델(호출 CON·DOE·CAD 위젯, MOR 위젯 0)이라 여기 넣지 않는다 — 소속 결정(B2, CON-08 · DOE-10 이 같은 파일) 뒤 그 모듈의 헬퍼 이행 항목으로. `model/DashGeometryParameter.cpp:saveMorphingTarget` 은 이미 QSaveFile(PER-c07)

#### MOR-23 · PR #655 머지 후 핸들 데이터·액터 경계의 잔여를 재판정한다
- 종류: INV | 규모: S | 태그: E · refactor
- 목표: PR #655 가 `m_handleGeometry` 와 구 피킹 경로를 지우고 `Finalize` 를 264 → 104줄로 줄였지만 `UpdateSurfaceGeometry:229-530`(302줄)는 무접촉이고 `.h:36` TODO("separate handle data and gizmo functions")도 남는다. 머지된 코드에서 (a) `UpdateSurfaceGeometry` 의 데이터 산출 ↔ 액터 생성 분해가 아직 필요한지 (b) `.h:36` TODO 가 가리키는 분리가 끝났는지 (c) `view/overlay/DashMorphingSettings.cpp:1125`·`:1312` 의 표면 배열 직접 접근 2곳과 view/viewmodel 의 `SetComponent` 직접 쓰기가 남는지 실측하고, 남으면 각각 PR S 를 연다.
- 완료 기준: 실측 결과 — (1) 세 지점의 잔존 여부와 머지 후 좌표 (2) 잔존분의 후속 항목 ID 또는 "해소" 근거 (3) `.h:36` TODO 처분(삭제 또는 후속 항목 번호로 갱신)
- 변경 범위: 조사 대상 `controller/DashHandlePickingInteraction.{h,cpp}` · `view/overlay/DashMorphingSettings.cpp` · `view/DashGeometryParameterWidget.cpp`·`DashGeometryParameterWidgetEditing.cpp` · `viewmodel/DashGeometryParameterPresentationModel.cpp`
- 선행: PR #655
- 충돌: B2 교집합: DashGeometryParameterWidget.cpp → DEV-10 MOR-01 MOR-02 MOR-03 MOR-17 MOR-22 UIC-20 · DashHandlePickingInteraction.cpp → MOR-02 MOR-03 MOR-04 MOR-06 MOR-13 MOR-17 · DashHandlePickingInteraction.h → MOR-02 MOR-03 MOR-04 MOR-06 MOR-07 · DashMorphingSettings.cpp → MOR-05 MOR-12 UIC-22 · DashGeometryParameterPresentationModel.cpp → MOR-22 · PR #654(DashGeometryParameterPresentationModel.cpp·DashGeometryParameterWidget.cpp·DashHandlePickingInteraction.cpp·DashHandlePickingInteraction.h·DashMorphingSettings.cpp)
- 흡수: Handle-Data-View-Separation ⓒ-2·ⓓ·ⓕ · MOR-c70, MOR-c71, MOR-c72, MOR-c74
- 비고: MOR-15(#430 CLOSE) 에서 분리한 잔여. `UpdateSurfaceGeometry` 분해가 필요하다는 결론이면 동작 불변 리팩터 PR 하나로 끝난다

### CAD — Geometry Parameterization — CAD

> dev @ b08a91b3. 열린 PR 7건(#658 #656 #655 #654 #652 #651 · #530 은 재업로드 노선이라 머지 대기 대상이 아니다 — 05-final/decisions.md 2 · 10 항) 중 CAD 관련 파일을 만지는 것 4건: #651(#616 — DashJobRunner.{h,cpp} · DashJobRunnerAnsysJournal.cpp · DashMainWindow.cpp · tests/CMakeLists.txt) · #652(#604 — DashJobRunner.h · DashMainWindow.{h,cpp} · DashManager.{h,cpp} · tests/CMakeLists.txt) · #654(#332 — DashMainWindow.cpp · DashManager.cpp · tests/CMakeLists.txt) · #655(#430 · #322 — DashMainWindow.cpp +1/-10 · tests/CMakeLists.txt +18/-18). #658 · #656 은 CAD 접촉 0. #249 자체의 열린 PR 은 없다.
> #655 의 `DashMainWindow.cpp` hunk 3곳은 전부 모핑 블록(`handleSubItemSelection` · `initializeMorphingController` · `setupMorphingBar`)이라 CAD 항목의 **선행**은 아니다 — 단순 충돌은 D-1 의 `build_deps.py --apply` 가 파일 교집합으로 기입한다.

#### CAD-01 · NX 파사드 완료 통지를 요청 태그 왕복 대칭 4종으로 일반화하고 m_batchMode 를 제거한다
- 종류: PR | 규모: M | 태그: B, E · refactor
- 목표: `enqueueLoadPrt`/`enqueueUpdatePrtGeometry` 가 `NxCadRequester {Interactive, Batch}`(클래스 내부 `Q_ENUM`) 를 받아 `commandId` 를 `"<verb>|<tag>|<stp>"` 로 싣고, 완료·실패를 `loadPrtCompleted/Failed` · `updatePrtGeometryCompleted/Failed(requester, stpPath[, message])` 대칭 4종으로 항상 방출한다. `nxCadParametersJson` 에도 `currentCommandId()` 에서 분해한 태그를 얹는다. 방출 억제(`m_batchMode`·`setBatchMode`·배치 전용 시그널 2종·`emitFailure`)는 삭제하고 판단은 구독자 필터로 옮긴다. 태그·경로를 얻을 수 없는 통지(빈 `outputStpPath`, 진행 커맨드 없는 JSON)는 귀속 없이 로그만 남긴다.
- 완료 기준: 1~3 은 **NX 불요**(빌드 · grep · CAD-11 TU), 4~5 는 **NX 게이트**(실기 수동)
  1. `git grep -E "m_batchMode|setBatchMode|updatePrtGeometryBatch|batchCompleted|batchFailed|emitFailure" -- '*.cpp' '*.h'` 0건 (주석 포함)
  2. 파사드에 모드 의존 방출 분기 0 · `commandId` 의 경로 필드를 버리는 지점 0 · `DashMainWindow` 에 `updatePrtGeometryFailed` 구독 존재 · 요청 6곳 각각의 완료·실패가 태그·경로로 짝지어진다 (RUN-D15 · OPT-D19)
  3. `onStpCaseFailed` 가 `onStpCaseCompleted` 와 같은 가드를 쓴다 — `requester == Batch && stpPath == m_stpBatch.current.stpPath` · 데몬 사망 1회당 Failed 케이스 1건(`drainCommands` 가 올리는 in-flight+큐 N건 중 현행 케이스 것만 계상) — CAD-11 TU + `tests/daemon_stub.cpp` 로 확인 (#249 "구독자 필터 규약" · AC 8항)
  4. (NX 게이트) DOE wbpj 배치 1회에서 콘솔 `Cannot queue arguments` 0건 · 케이스별 모달·미리보기 0회 — LCH-29 가 **제거**면 이 기준과 Phase 3 이 함께 소멸
  5. (NX 게이트) NX 환경 수동 회귀 5케이스(기하 파라미터 미리보기 · Optimizer 미리보기 · Model Runner 파일테이블 · load/update 실패 모달 각 1회 · loadPrt 후 파라미터 표 갱신) 회귀 없음
- 변경 범위: controller/DashSolverNxCad.h · controller/DashSolverNxCad.cpp · view/DashGeometryParameterCADWidget.cpp · view/DashMainWindow.cpp · view/DashModelRunnerWidget.cpp · view/DashOptimizerWidget.cpp · model/DashJobRunner.h · model/DashJobRunnerAnsysJournal.cpp
- 선행: LCH-29 (wbpj 경로 처분 — Phase 3 의 존폐를 정한다)
- 충돌: PR #651 · #652 · #654 · #655(DashMainWindow.cpp · DashJobRunner.h · DashJobRunnerAnsysJournal.cpp) · CAD-02 · CAD-06 · CAD-08(DashSolverNxCad) · CAD-07(DashMainWindow 구독 블록) · LCH-06 · LCH-07 · LCH-14 · LCH-27 (DashJobRunnerAnsysJournal) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashGeometryParameterCADWidget.cpp → 공유 10건(deps.md 5절) · DashJobRunner.h → LCH-02 LCH-10 LCH-12 · DashJobRunnerAnsysJournal.cpp → UIC-19 · DashSolverNxCad.cpp → CAD-03 CAD-15 · DashSolverNxCad.h → CAD-03
- 흡수: #249 · CAD-D3 · CAD-D7 · CAD-D8 · OPT-D19(본체) · #457(D19 태그 왕복 몫) · RUN-D15 · CAD-c01, c02, c03, c04, c05, c06, c07, c08, c09, c16, c38, c53 · CAD-c35(`JobType` · DashSolverNxCad.h:73-74 주석 몫 — 나머지 4건은 CAD-06) · CAD-c39, c41, c42, c44 (← RUN-c32, OPT-c10, OPT-c37, EXE-c42)
- 비고: 이슈 본문 설계(방안 A · 대칭 4종 · `|` 구분자 · `Q_ENUM`)를 그대로 쓴다. 분할 불가 — 시그니처 변경이 구독 9곳을 동시에 깨므로 한 커밋. 파일 8개지만 순변경 ~100줄, 비용의 대부분은 NX 수동 회귀. **LCH-29 조건** — `제거` 면 Phase 3(오케스트레이터 재배선)·`Batch` 태그·완료 기준 3·4 가 소멸하고 본 항목은 대화형 4종 대칭 + 태그(S) 로 줄어든다. 매니페스트가 "사장 예정·불개입" 으로 적은 경로의 수정분을 그만큼 뺀다. `현행 유지`·`동결` 이면 지금 범위 그대로(M). **소비자(랜딩 뒤 후속)** — OPT-D19(#457) 의 태그 왕복 몫은 본 항목이 흡수하고 Optimizer 위젯 측 소비자 전환(자기 요청 구독 · 부모 탐색 제거)은 OPT-22 · RUN-09 는 ModelRunner 의 `stpPath` 문자열 비교를 태그 비교로 바꾸는 몫만 본 항목 뒤에 둔다(RUN-09 본문이 괄호 조건으로 적어 파서가 선행으로 읽지 않는다). CAD-06 의 `JobType`·헤더 주석 2곳은 본 항목이 같은 블록을 고치므로 여기서 함께 지운다(검토 #16). CAD-D3 의 "표가 먼저, 형상이 나중" 순서 보장은 태그 상관까지만 — 합류점 설계는 별도 결정으로 남긴다.

#### CAD-02 · 파사드 상태의 수명을 명령 경계에 맞춘다 — prt 출처 배치 오염 · JSON 버퍼
- 종류: PR | 규모: S | 태그: A, C · bug
- 목표: `enqueueUpdatePrtGeometry` 가 `m_originalPrtPath` 를 덮어쓰지 않게 해 "마지막에 Load 한 .prt" 의미를 `enqueueLoadPrt` 에만 둔다 — 호출 3곳(배치 `startNextStpCase` · Optimizer `onPreviewButtonClicked` 의 `configs/` 복사본 · ModelRunner `onGenerateInputFileClicked` 의 `getViewSourceConfigsDir()` 복사본) 어느 것도 `lastLoadedPrtPath()` 를 바꾸지 않는다. `m_jsonAccumBuffer` 를 커맨드 완료·실패 시 비운다.
- 완료 기준: 1 · 3 은 **NX 불요**(grep · CAD-11 TU), 2 는 **NX 게이트**(실기 수동)
  1. `controller/DashSolverNxCad.cpp:enqueueUpdatePrtGeometry` 에 `m_originalPrtPath` 쓰기 0건 (쓰기는 `enqueueLoadPrt` 1곳)
  2. (NX 게이트) wbpj DOE 배치 1회 / Optimizer 프리뷰 1회 / ModelRunner 프리뷰 1회 — 각각 뒤에 `lastLoadedPrtPath()` 가 마지막 Load 한 `.prt` 와 같다 (CADWidget [Preview] 가 그 prt 로 간다)
  3. 실패한 커맨드 뒤 `m_jsonAccumBuffer` 가 비어 있다 — `commandFailed` 를 직접 emit 하는 단위 테스트로 확인 (CAD-11 TU 에 1건 추가 — 선후 무관)
- 변경 범위: controller/DashSolverNxCad.cpp (필요 시 .h)
- 선행: LCH-29 (wbpj 경로 처분 — 완료 기준 2 의 배치 1회가 소멸할 수 있다)
- 충돌: CAD-01 · CAD-06 · CAD-08 (같은 파일) · B2 교집합: DashSolverNxCad.cpp → CAD-03 CAD-15
- 흡수: CAD-c10, c12
- 비고: 둘 다 "명령 단위로 끝나야 할 상태가 파사드 전역에 남는" 한 개념(#249 범위 밖 절) — 검토 #4 의 `c12` 분리(CAD-02b) 제안은 **기각**(00-plan 1-2 개념적 응집: 기제가 둘이어도 "파사드 전역 상태의 수명" 한 덩어리로 읽힌다). CAD-01 과 같은 브랜치에 넣지 않는다 — CAD-01 은 동작 불변 리팩터. **LCH-29 조건** — `제거` 면 완료 기준 2 의 배치 항이 빠지고 Optimizer·ModelRunner 2경로만 남는다(목표·수정분은 그대로, 불개입 경로 몫만 제외).

#### CAD-03 · Set 진입 시 세션 캐시 재적용이 저장된 체크·범위를 덮지 않게 한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `setModel` 의 진입 순서를 "저장 JSON 1회 로드 → 세션 캐시는 이름 매칭 병합" 으로 바꾼다. 병합은 **캐시·데몬 경로 전용 함수**(예 `mergeNxCadParameterJson`)로 두고 `applyNxCadParameterJson` 자체는 교체로 유지한다 — 그 함수는 `loadFromJson:397` 도 호출하므로 병합으로 바꾸면 "파일이 정본" 의미가 깨진다(Set 재진입 시 파일값이 메모리의 미저장 편집에 밀린다). 병합은 기존 행의 `isChecked`·`lower`·`upper` 를 이름으로 보존하고(없는 이름만 추가·사라진 이름만 제거), MainWindow 와 위젯이 각각 부르던 `setProjectDirectory`→`loadFromJson` 2회를 1회로 줄인다. 프로젝트 전환에서 세션 전역 2곳을 비운다 — `DashManager::m_lastNxCadParameterJson` 과 파사드 `DashSolverNxCad::m_originalPrtPath`(clear 0곳이라 다른 프로젝트의 [Preview]·DV 승격 복사가 이전 프로젝트 `.prt` 로 간다).
- 완료 기준: 1 은 **NX 게이트**(실기 수동), 2~4 는 **NX 불요**(로그 · grep · CAD-11 TU)
  1. (NX 게이트) `.prt` 를 Load 한 세션에서 승격된 Set 을 재선택해도 체크 상태와 Lower/Upper 가 저장값과 같다
  2. 다른 프로젝트를 연 뒤 CAD Set 진입 시 이전 프로젝트의 파라미터 행이 뜨지 않는다
  3. Set 진입당 `loadFromJson` 호출 1회 (로그 `Loaded settings from` 1건)
  4. `applyNxCadParameterJson` 은 교체 그대로 — `loadFromJson` 왕복에서 파일값이 정본이다(CAD-11 TU) · 프로젝트 전환 뒤 `lastLoadedPrtPath()` 가 빈 문자열
- 변경 범위: view/DashGeometryParameterCADWidget.cpp · model/DashGeometryParameterCAD.cpp (병합 함수 신설) · controller/DashManager.cpp (캐시 초기화 1곳) · controller/DashSolverNxCad.h · controller/DashSolverNxCad.cpp (`m_originalPrtPath` reset 1곳) · view/DashMainWindow.cpp:handleGeometryParameterSelection (중복 `setProjectDirectory` 제거)
- 선행: -
- 충돌: CAD-04 · CAD-05 · CAD-07 (CADWidget.cpp) · PR #652 · #654 (DashManager.cpp · DashMainWindow.cpp) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashGeometryParameterCADWidget.cpp → 공유 10건(deps.md 5절) · DashManager.cpp → CAD-06 DOE-19 EXE-06 PRJ-03 PRJ-04 PRJ-06 PRJ-14 REN-07 · DashGeometryParameterCAD.cpp → CAD-06 CAD-09 PRJ-09 UIC-20 · DashSolverNxCad.cpp → CAD-01 CAD-02 CAD-06 CAD-08 CAD-15 · DashSolverNxCad.h → CAD-01 CAD-06 · PR #655(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: CAD-D4 · CAD-c21, c22, c23, c52
- 비고: 대안 — 캐시 적용을 "모델이 비었을 때만" 으로 한정하면 더 작지만, Load 직후 Set 재진입에서 데몬의 Part·Dependent 갱신을 잃는다. 병합안 권장. 초기화 지점 2곳 모두 #560 이 CAD Set 목록을 지운 프로젝트 전환 경로(`DashProject::clearAllSets` 호출부 — `model/DashProject.cpp:84`)와 같은 곳. 검토 #5 의 3분할(CAD-03a 병합 / CAD-03b 전환 초기화) 제안은 **기각** — "세션 캐시가 저장값·프로젝트 경계를 넘지 않게 한다" 한 개념이고 파일이 넷·모듈 접점이 PRJ 라는 것은 분할 사유가 아니다(00-plan 1-2). 검토 #15(파사드 `m_originalPrtPath`)는 c23 과 같은 기제라 본 항목에 합쳤다 — 파사드 쪽은 1줄 reset 이므로 규모 S 유지. PRJ 접점: 전환 훅 자리는 PRJ-c64 계열 함수와 겹칠 수 있다.

#### CAD-04 · DV 승격의 범위값 정본을 모델로 단일화한다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `collectCadDvRows` 가 셀 스핀박스(`cellWidget(visualRow, 3/4)`) 대신 모델을 이름 매칭으로 읽어 lower/upper/defaultText 를 모은다. 표 접근 방식을 "체크는 표(이름 매칭) · 값은 모델" 둘로 줄여 정렬 방어 3갈래(이름 · 시각 행 · 캡처 행)를 없앤다. 모델은 이미 `valueChanged` → `setIndependentParameterBounds` 로 동기되므로 저장값은 불변.
- 완료 기준:
  1. `collectCadDvRows` 에 `cellWidget` 호출 0
  2. 헤더 클릭으로 정렬한 뒤 승격한 DV-Geometry 의 `min/max` 가 각 이름의 모델값과 일치 (단위 테스트 — CAD-11)
- 변경 범위: view/DashGeometryParameterCADWidget.cpp (`collectCadDvRows` · 필요 시 `onCadApplyAddValues` 도 모델 경유)
- 선행: CAD-11 (현행 동작을 고정한 TU 가 먼저 — 본 항목이 그 기대값을 갱신한다)
- 충돌: CAD-03 · CAD-05 · CAD-07 (같은 파일, CAD-05 와 같은 함수) · CAD-11 (tests/TestGeometryParameterCad.cpp 기대값 갱신) · B2 교집합: DashGeometryParameterCADWidget.cpp → 공유 10건(deps.md 5절)
- 흡수: CAD-D12 · CAD-D6 · CAD-c25, c28 · CAD-c51 (← UIC-c58)
- 비고: CAD-D6 의 세 갈래는 정적으로 각각 내부 정합이 성립한다(QTableWidget 정렬이 persistent index 로 cellWidget 을 옮기고, 람다 캡처 행은 `m_params` 인덱스). 결함의 실체는 접근 방식의 다중화라 정본 단일화로 닫는다.

#### CAD-05 · 현재값(value)을 저장·복원하고 meta.default 에 쓴다
- 종류: PR | 규모: S | 태그: A, C · bug
- 목표: `toSettingsJsonObject` 의 `Independent Parameter.Value` 에 `upper` 대신 `CADParameterRow::value`(데몬 현재값)를 쓰고, `collectCadDvRows` 의 `defaultText` 를 모델 3열(=lower) 이 아니라 `value` 에서 채워 `DV-Geometry.meta.default` 가 현재값이 되게 한다. 로드 쪽(`applyNxCadParameterJson` — `Value` 를 현재값으로 읽고 `Lower/Upper` 로 범위 복구)은 그대로.
- 완료 기준: 2 · 3 은 **NX 불요**(CAD-11 TU · grep), 1 은 **NX 게이트**(데몬 현재값이 필요)
  1. (NX 게이트) 승격 후 JSON: `Independent Parameter.Value[i] == 데몬 Value[i]` · `DV-Geometry.<name>.meta.default == 그 값`
  2. 저장 → 재로드 왕복에서 `value`·`lower`·`upper` 셋이 보존 (단위 테스트 — CAD-11)
  3. 하류 1곳의 입력 변경이 의도대로다 — `journalLaunchConfig` 의 `indParamInitials`(wbpj Journal 비샘플 파라미터 초기값)가 upper 가 아니라 현재값을 받는다 (TU 또는 생성된 Journal 설정 JSON 1건 비교)
- 변경 범위: model/DashGeometryParameterCAD.cpp (`toSettingsJsonObject`, 필요 시 `value` 접근자) · view/DashGeometryParameterCADWidget.cpp (`collectCadDvRows`) · viewmodel/DashGeometryParameterCADPresentationModel.h (주석)
- 선행: CAD-04 (`collectCadDvRows` 를 먼저 모델 기반으로) · CAD-11 (현행 왕복 TU 선행 — 본 항목이 기대값 갱신) · LCH-29 (wbpj 경로 처분 — 완료 기준 3 의 존폐)
- 충돌: CAD-03 · CAD-04 · CAD-07 (CADWidget.cpp) · CAD-06 (Model .cpp) · CAD-11 (tests/TestGeometryParameterCad.cpp 기대값 갱신) · B2 교집합: DashGeometryParameterCADWidget.cpp → 공유 10건(deps.md 5절) · DashGeometryParameterCAD.cpp → CAD-09 PRJ-09 UIC-20
- 흡수: CAD-D10 · CAD-D11 · CAD-c26, c27
- 비고: 저장 포맷의 의미 변경(Value: upper → 현재값). 기존 파일은 `Lower/Upper` 키가 있어 범위 복원엔 영향 없고, `value` 만 옛 upper 로 읽혀 재승격 전까지 `meta.default` 가 낡는다 — 마이그레이션 불요. **하류 동작 변경 1건(의도된 것)** — `model/DashJobRunnerAnsysJournal.cpp:100-110 journalLaunchConfig` 가 `initIndParam["Value"]` 를 비샘플 파라미터 초기값으로 읽으므로 wbpj Journal 의 초기값 배열이 upper→현재값으로 바뀐다(**접점 LCH**). `viewmodel/DashSurrogateModelCommon.cpp:148-176 buildCadConfigJson`(Optimizer·ModelRunner)은 Name/Part 만 읽고 값은 DV 에서 받아 무영향. **LCH-29 조건** — `제거` 면 하류 영향이 사라져 완료 기준 3 이 소멸한다. PER 과 접점(저장 포맷)이나 파일은 CAD 소유.

#### CAD-06 · CAD 영역 죽은 코드 6건을 제거한다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: 호출·연결 0인 선언·정의 4건을 지운다 — `DashGeometryParameterCAD::saveSettings`(no-op) · `m_lastLoadedStpPath`/`lastLoadedStpPath()` · `DashGeometryParameterCADWidget::onDirChanged` · `DashManager::applyLastNxCadParameterJsonToGeometryModels`. `DashSolverNxCad::JobType` 과 `DashSolverNxCad.h:73-74` 의 "commandId encodes JobType" 주석은 CAD-01 이 같은 블록을 재작성하므로 **CAD-01 몫**(검토 #16).
- 완료 기준:
  1. 위 4 심볼 `git grep` 0건
  2. 빌드 통과 · 동작 불변
- 변경 범위: controller/DashSolverNxCad.h · controller/DashSolverNxCad.cpp · model/DashGeometryParameterCAD.h · model/DashGeometryParameterCAD.cpp · view/DashGeometryParameterCADWidget.h · view/DashGeometryParameterCADWidget.cpp · controller/DashManager.h · controller/DashManager.cpp
- 선행: -
- 충돌: CAD-01 · CAD-02 · CAD-08 (DashSolverNxCad) · CAD-03 · CAD-05 (Model · Widget) · PR #652 · #654 (DashManager) · B2 교집합: DashGeometryParameterCADWidget.cpp → 공유 10건(deps.md 5절) · DashManager.cpp → DOE-19 EXE-06 PRJ-03 PRJ-04 PRJ-06 PRJ-14 REN-07 · DashGeometryParameterCAD.cpp → CAD-09 PRJ-09 UIC-20 · DashSolverNxCad.cpp → CAD-15 · DashManager.h → PRJ-03 PRJ-04 PRJ-06 PRJ-19
- 흡수: CAD-U3 · CAD-c11 · CAD-c35(4건 몫 — `JobType`·헤더 주석은 CAD-01)
- 비고: 파일 8개라 규칙상 M 이나 삭제만이라 반나절. `DashSolverNxCad.{h,cpp}` 는 `lastLoadedStpPath` 때문에 남는다 — 선행이 아니라 충돌 관계(CAD-01 과 순차). 색인 U3 의 `getContext`·`getLoadedFilePath`·`setModel` 오버로드는 a03efe0b 에서 이미 제거됐다.

#### CAD-07 · 진행 표시 짝을 맞춘다 — 프리뷰 시작 호출 · STEP 로드 실패 시 정지
- 종류: PR | 규모: S | 태그: D · bug
- 목표: CADWidget `enqueuePreview` 가 요청 직전에 `startNxCadStatusAnimation("NX CAD updating geometry")` 을 걸어 ModelRunner·Optimizer 프리뷰와 같은 짝을 갖게 한다. `DashOcctViewWidget::loadStepFile` 의 중도 반환 4곳(뷰 미생성 · 파일 부재 · STEP 읽기 실패 · OneShape null)에 실패 통지(반환값 또는 `stepFileLoadFailed`)를 두고 MainWindow 가 그때 `stopProjectLoadStatusAnimation` 을 부른다.
- 완료 기준: 2 는 **NX 불요**(손상 `.stp` 직접 Load 로 재현), 1 은 **NX 게이트**(실기 수동)
  1. (NX 게이트) [Lower/Upper Preview] 클릭 직후 상태바에 "NX CAD updating geometry…" 가 돌고 완료 시 "NX CAD geometry updated." 로 끝난다
  2. 손상된 `.stp` 를 Load(또는 `.prt` 완료 후 OCCT 읽기 실패)하면 "Loading …" 이 남지 않는다 — `loadStepFile` 중도 반환 4곳 전부가 실패를 통지한다
- 변경 범위: view/DashGeometryParameterCADWidget.cpp · view/DashMainWindow.cpp · view/DashOcctViewWidget.h · view/DashOcctViewWidget.cpp
- 선행: -
- 충돌: PR #651 · #652 · #654 (DashMainWindow.cpp) · CAD-01 (MainWindow 의 NX 구독 블록) · CAD-03 · CAD-04 · CAD-05 (CADWidget.cpp) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashGeometryParameterCADWidget.cpp → 공유 10건(deps.md 5절) · DashOcctViewWidget.cpp → CAD-12 CAD-14 · PR #655(DashMainWindow.cpp)
- 흡수: #464 · CAD-D9 · CAD-D1(잔여) · #463(CAD 몫) · CAD-c18, c19 · CAD-c49, c50 (← EXE-c44, EXE-c23)
- 비고: CAD-D1 의 본체(성공 경로 미정지)는 해소돼 있다 — `stepFileLoaded` → `stopProjectLoadStatusAnimation` (DashMainWindow::ensureOcctViewerCreated, 25b9994c). 검토 #10 의 2분할(07a D9 / 07b D1 잔여) 제안은 **기각** — "진행 표시의 시작·정지 짝" 한 개념이고 둘 다 같은 스피너의 한쪽 끝이다(00-plan 1-2). **규약 연결**: CADWidget → MainWindow 도달은 위젯 시그널을 MainWindow 가 구독하는 쪽으로 — view→view 부모 탐색(`findMainWindow` 선례)을 늘리지 않는다. 같은 규약을 PRJ-25(부모 역참조 12곳 → 시그널, 목록에 CADWidget 은 **미포함**)와 OPT-22(`nxPreviewRequested`)가 쓰므로 **시그널명은 OPT-22 와 맞춘다**(`nxPreviewRequested`). PRJ-25 가 먼저 랜딩하면 그 형식을 따르고, 본 항목이 먼저면 PRJ-25 가 CADWidget 을 목록에 더하지 않는다(선행 관계는 아니다 — 파일이 다르다). "상태 고정 기입(Enqueued)" 은 #440(LCH) 소관, 여기서 다루지 않는다. 진행 표시 규약은 EXE-07 — #463 확산의 CAD 몫.

#### CAD-08 · 프리뷰 temp .prt 를 정리한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: 프리뷰마다 데몬이 `{temp}/{base}_{upper|lower}_preview_{seq}.prt` 를 남기고 어느 경로도 지우지 않는 누적을 끊는다. GUI 단독 해법 — `enqueueLoadPrt` 의 정리 글로빙에 `*_lower_preview*.prt`·`*_upper_preview*.prt` 를 더한다.
- 완료 기준: 2 는 **NX 불요**(글로빙 패턴·대상 디렉터리 검토), 1 은 **NX 게이트**(프리뷰 실행 필요)
  1. (NX 게이트) 프리뷰 N회 후 다음 `.prt` Load 시 temp 의 `*_preview_*.prt` 가 0개
  2. DOE 배치 산출 `{outputBaseDir}/{runKey}/{runKey}.prt` 는 건드리지 않는다 (temp 밖)
- 변경 범위: controller/DashSolverNxCad.cpp
- 선행: -
- 충돌: CAD-01 · CAD-02 · CAD-06 (같은 파일) · B2 교집합: DashSolverNxCad.cpp → CAD-03 CAD-15
- 흡수: CAD-D16 · CAD-c33
- 비고: 대안은 프리뷰 요청에서 `--no-cleanup` 을 떼어 데몬 정리 분기(`main.py:274-275`)에 맡기는 것 — 데몬 측 동작 실측이 필요해 글로빙 확장을 택한다. 매니페스트 문서가 D16 을 "사장 경로로 격리" 로 묶었으나 프리뷰는 정규 CAD 동선이다.

#### CAD-09 · .prt 보관본 삭제와 Set↔.prt 결합 미저장의 처분을 결정한다
- 종류: DEC | 규모: S | 태그: A, C
- 목표: Project-Manifest-CAD-Path-Disposition(2026-09-18 방침)이 D15(재Load 가 승격 보관본 삭제)·D17(Set 별 `.prt` 미저장)을 "후속작업 13(미래 CAD 경로) 동반 유보 · 사장 경로로 격리" 로 기록했다. 새 작업 목록이 그 결정을 승계할지, 아니면 최소 수선을 지금 할지 정한다.
- 완료 기준: 결정 기록 — (a) 유보 승계: 후속작업 13 의 `cadSource {uuid, path}` 설계에 D15·D17 을 입력으로 넘기고 본 목록에선 항목 없음. **(a) 를 고르면 추적 위치를 함께 지정해야 한다** — 현재 03-items 전체에 후속작업 13(미래 CAD 경로 — Meshing·Match NSET·deck 등록) 추적 항목이 0이라 D15·D17 이 어디에도 남지 않는다(검토 #13). 지정 후보: CAD 에 추적 항목 1건(CLOSE/EXT 형식) 신설 또는 PRJ 매니페스트 후속 항목에 D15·D17 입력 등재 / (b) 최소 수선: `loadPrt` 출력 STEP 위치를 `configs/` 밖(모듈 폴더)으로 옮겨 보관본과 base 충돌을 끊고(D15), Set JSON 에 `prt` 경로 1필드를 기록해 재진입 시 Load 없이 프리뷰 가능하게(D17) — 선택 시 PR 2건(S·S)으로 분할
- 변경 범위: (b) 선택 시 view/DashMainWindow.cpp:openFileInViewport · view/DashGeometryParameterCADWidget.cpp:syncDvFromCheckedCadParameters · viewmodel/DashGeometryParameterCADPresentationModel.cpp:mergeSettingsRoot · model/DashGeometryParameterCAD.cpp
- 선행: -
- 충돌: (b) 선택 시 CAD-03 · CAD-05 · CAD-07 · PR #651 · #652 · #654 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashGeometryParameterCADWidget.cpp → 공유 10건(deps.md 5절) · DashGeometryParameterCAD.cpp → CAD-06 PRJ-09 UIC-20 · DashGeometryParameterCADPresentationModel.cpp → CAD-13 · PR #655(DashMainWindow.cpp)
- 흡수: CAD-D15 · CAD-D17 · CAD-c32, c34
- 비고: D15 의 삭제 주체는 데몬(`main.py:214·330-338` `_cleanup_temp`)이라 (b) 의 GUI 측 수선은 경로 분리뿐이다. D17 은 PRJ 의 Set identity(Project-Manifest-Set-Identity-And-Decision-Revisions D29~D31) 와 접점 — (b) 를 고르면 PRJ 에 `cadSource` 키 합의가 필요하다. 검토 #15 의 파사드 `m_originalPrtPath` 전환 reset 은 본 DEC 의 입력이 아니라 CAD-03 의 수정분으로 넣었다 — c23 과 같은 기제라 결정을 기다릴 이유가 없다.

#### CAD-10 · 데몬: NX 표현식 적용 실패를 stdout [ERROR] 로 올린다
- 종류: EXT | 규모: S | 태그: A · bug
- 목표: DashOpti_CadNx `nx_helpers.py:update_expressions` 가 이름별 실패를 ListingWindow 에만 쓰고 삼키는 것을 예외 전파(또는 실패 목록 수집 후 `RuntimeError`)로 바꿔 `main.py` 가 `[GUI] [ERROR]` 를 찍게 한다. GUI 는 기존 `[ERROR]` 매칭으로 `commandFailed` → `loadPrtFailed`/배치 실패로 받는다 — GUI 변경 0.
- 완료 기준: 외부 저장소 PR — PRT 에 없는 이름을 DV 로 올려 프리뷰하면 GUI 에 실패 모달이 뜨고 STEP 이 성공으로 등록되지 않는다 · DOE 배치는 그 케이스를 실패로 계상한다
- 변경 범위: (GUI 없음) DashOpti_CadNx `source/.../nx_helpers.py` · `main.py` — 위키 좌표 d71a17d
- 선행: -
- 충돌: -
- 흡수: CAD-D14 · CAD-c30
- 비고: 부분 실패(일부 이름만 없음) 를 전체 실패로 볼지, 적용된 이름만 반영하고 경고로 둘지는 데몬 측 결정 — GUI 쪽은 어느 쪽이든 `[ERROR]` 유무로만 판정한다. CAD-U4 의 "판정이 로그 포맷" 은 EXE-12 소관(범위밖)이며 본 항목은 그 계약 위에서 움직인다. CAD-D14 가 EXE-12 흡수 목록에도 올라 있다(03-items/EXE.md 대응표 "CAD-10 과 중복 기록 — Phase B 병합" 미이행) — **실작업은 본 항목 단일**이고 EXE-12 는 "데몬 4종 준수 표" 에서 본 항목을 참조만 해야 한다. `보류: EXE 몫`(EXE-12 흡수 목록·대응표에서 CAD-D14 제거).

#### CAD-11 · CAD 모델·PM 의 JSON 왕복과 파사드 commandId 해석에 자동 테스트를 둔다
- 종류: PR | 규모: S | 태그: F · refactor
- 목표: NX 없이 도는 단위 테스트 1 TU 를 추가해 **현행 동작을 기대값으로 고정한다** — `DashGeometryParameterCAD::applyNxCadParameterJson`/`toSettingsJsonObject`/`toNxCadConfigJson` 왕복(데몬 JSON → 저장 JSON → 재로드, 현행 `Independent Parameter.Value == upper`) · `DashGeometryParameterCADPresentationModel::buildDvGeometryJson`/`mergeSettingsRoot` · `DashSolverNxCad` 의 `commandCompleted`/`commandFailed`/`outputLine` 을 직접 emit 해 방출 시그널·`commandId`(현행 `"<verb>:<stp>"`)·버퍼 상태를 `QSignalSpy` 로 검증.
- 완료 기준:
  1. `tests/CMakeLists.txt` 에 `test_geometry_parameter_cad` 등록 · `ctest` 통과
  2. 현행 저장 왕복과 `commandId` 규약이 기대값으로 고정된다 — 후행 항목(CAD-01 태그·대칭 4종 / CAD-02 버퍼 경계 / CAD-04 모델 정본 / CAD-05 현재값 / CAD-13 헬퍼 쓰기)이 각자 기대값을 갱신·추가한다
- 변경 범위: tests/CMakeLists.txt · tests/TestGeometryParameterCad.cpp (신규)
- 선행: -
- 충돌: CAD-01 · CAD-02 · CAD-04 · CAD-05 · CAD-13 (tests/TestGeometryParameterCad.cpp — 각자 기대값 갱신) · DEV-19 (tests/CMakeLists.txt 등록 헬퍼 — 먼저 오면 그 형식으로 등록) · B2 교집합: tests/CMakeLists.txt → 공유 12건(deps.md 5절) · PR #655(tests/CMakeLists.txt) · PR #654(tests/CMakeLists.txt) · PR #652(tests/CMakeLists.txt) · PR #651(tests/CMakeLists.txt)
- 흡수: CAD-U5 · #489(CAD 몫) · CAD-c36 · CAD-c47, c48 (← UIC-c57, DEV-c24)
- 비고: **선행 없이 먼저 랜딩한다** — 종전 `선행: CAD-01 · CAD-04 · CAD-05` 는 완료 기준 순환이었다(CAD-02 완료2 · CAD-04 완료2 · CAD-05 완료2 · CAD-13 완료3 이 "CAD-11 TU 로 확인" 인데 그 셋이 CAD-11 의 선행 → 선행 항목의 완료를 후행이 증명). 선행 그래프상 순환은 아니어서 `check_coverage.py`·`build_deps.py` 가 잡지 못했다(검토 #8). 현행 동작을 고정한 TU 를 먼저 두고 CAD-01·02·04·05·13 이 기대값을 갱신하는 순서로 끊는다. `DashSolverNxCad` 생성자는 `DashManager` 를 건드리지 않는다(`tryStartIfConfigured` 만 접근) — 테스트에서 직접 생성 가능. 시그널은 public 멤버라 테스트가 `emit` 할 수 있다. 전송 계층(`[FINISHED]`/`[ERROR]` 판정)은 test_process_runtime + daemon_stub 이 이미 덮는다.

#### CAD-12 · OCCT 뷰의 프리뷰 덮어쓰기 처분을 정한다 — 단일 형상 뷰 유지 vs 원본 복귀 경로
- 종류: DEC | 규모: S | 태그: D, E
- 목표: `DashOcctViewWidget::loadStepFile` 은 `m_context->RemoveAll` 뒤 형상 하나만 올린다. CAD 위젯 Lower/Upper 프리뷰와 Optimizer 프리뷰 `.stp` 가 Load 한 `.prt` 의 STEP 을 덮고 되돌릴 UI 가 없다(원본은 `configs/{prtBase}.stp` 재 Load 또는 NX loadPrt 재실행). #316·#318 은 이 지점을 VTK 소유권 모델 밖(별도 씬)으로 뺐다. (a) 단일 형상 뷰 유지 — 결함 아님으로 기록 (b) 원본 STEP 경로를 기억해 "Show original" 복귀 1동작 (c) 원본·프리뷰 병치(투명도) 중 하나를 정한다.
- 완료 기준: 결정 기록 — 선택지·사유. (b)/(c) 면 후속 PR S (view/DashOcctViewWidget.{h,cpp} · view/DashMainWindow.cpp:previewStepFile)
- 변경 범위: - (결정 후: view/DashOcctViewWidget.cpp:loadStepFile :176-229 · clearView :376 · view/DashMainWindow.cpp:previewStepFile :3224 · onNxPreviewStepReady :3247 · onNxLoadPrtStepReady :3203)
- 선행: -
- 충돌: CAD-07 · CAD-14 (DashOcctViewWidget) · PR #651 · #652 · #654 (DashMainWindow.cpp) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · PR #655(DashMainWindow.cpp)
- 흡수: #316(.stp 덮어쓰기 — 범위 제외 명시) · #318(부류 2 ⑩ OCCT) · CAD-c40, c43 (← OPT-c08, REN-c17)
- 비고: OCCT 뷰는 공유 VTK renderer 가 아니라 REN 소유자 태그 모델의 대상이 아니다. (a) 가 가장 싸고 현행 사용 흐름(프리뷰를 보려고 누른다)과 맞는다.

#### CAD-13 · DV 승격 JSON 쓰기를 공용 파일 헬퍼로 옮긴다
- 종류: PR | 규모: S | 태그: A · refactor
- 목표: `saveDvGeometry` 의 read-modify-write(`QFile` 읽기 → `mergeSettingsRoot` → `QFile` 직쓰기 Truncate) 를 PER-02 가 공용 진입점으로 승격하는 **DashSaveSystem 헬퍼**(`persistence/DashSaveSystem` 의 read/writeJsonFile — QSaveFile 원자 쓰기 · 길이 검사 · Result 사유 반환) 호출로 바꾼다. 포맷·병합 규칙 불변. 실패 사유를 호출자(CADWidget `syncDvFromCheckedCadParameters`)가 로그·통지한다.
- 완료 기준: (1) viewmodel/DashGeometryParameterCADPresentationModel.cpp 에 `QFile` 0건 (2) 읽기 전용 경로에서 승격 실패 시 기존 파일 바이트 동일 + 통지 (3) CAD-11 왕복 테스트 통과
- 변경 범위: viewmodel/DashGeometryParameterCADPresentationModel.cpp (`saveDvGeometry` :55-77) · view/DashGeometryParameterCADWidget.cpp (사유 소비 1곳)
- 선행: PER-02(DashSaveSystem 헬퍼 승격) · CAD-05 (저장 의미 변경을 먼저 — 같은 함수에서 동작 변경과 리팩터를 섞지 않는다) · CAD-11 (현행 왕복 TU 선행)
- 충돌: CAD-04 · CAD-05 (같은 함수) · CAD-03 (CADWidget) · CAD-11 (tests/TestGeometryParameterCad.cpp) · B2 교집합: DashGeometryParameterCADWidget.cpp → 공유 10건(deps.md 5절) · DashGeometryParameterCADPresentationModel.cpp → CAD-09
- 흡수: #479(CAD 몫) · #478(CAD 몫) · #480(CAD 몫 — PER-04 뒤 버전 키 자동) · CAD-c45 (← PER-c23)
- 비고: PER-c08 RMW 13지점 중 1건. `variant` 키 기록(PER-c10)은 그대로 — 버전 키와의 관계는 PER-03 결정. 05-final/decisions.md 3항 — PER-02 는 `utils/DashJsonFile` 신설을 버리고 기존 `DashSaveSystem::read/writeJsonFile` 승격으로 확정됐다. 선행은 그대로 PER-02.

#### CAD-14 · OCCT 뷰 마우스 좌표에 DPR 을 반영한다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: `mousePressEvent`/`mouseMoveEvent` 가 논리 좌표 `event->x()/y()` 를 OCCT(`WNT_Window` — 물리 px 창)의 `StartRotation`·`Rotation`·`Pan` 에 그대로 넘겨 DPR≠1 에서 회전 피벗과 팬 거리가 어긋난다. `event->position() * devicePixelRatioF()` 로 물리 px 로 바꿔 넘기고 `m_lastMousePos` 도 같은 단위로 든다.
- 완료 기준: (1) 150%·200% 모니터에서 회전 피벗이 커서 아래 점과 일치하고 팬이 커서를 따라간다 (2) 100% 에서 현행과 동일 (3) 배율이 다른 모니터로 창을 옮긴 뒤에도 (1) — UIC-02 실기 환경
- 변경 범위: view/DashOcctViewWidget.cpp (`mousePressEvent` :452-462 · `mouseMoveEvent` :464-488)
- 선행: -
- 충돌: CAD-07 · CAD-12 (같은 파일)
- 흡수: #447 R1 · CAD-c46 (← UIC-c30)
- 비고: Qt6 는 `highDpiScaleFactorRoundingPolicy` 기본 PassThrough 라 150% 에서 지금 발현. `wheelEvent` 는 좌표를 쓰지 않아 대상 밖. `resizeEvent` 의 `MustBeResized` 는 OCCT 가 창 크기를 직접 읽어 영향 없음.

#### CAD-15 · 데몬 사망 시 실패 통지 fan-out 을 실측하고 합산 정책을 정한다
- 종류: INV | 규모: S | 태그: B, D · bug
- 목표: `DashExtensionProcess::drainCommands` 가 in-flight 1건 + 큐 N건을 각각 `commandFailed` 로 동기 emit 하고(:280-285) 파사드가 그대로 `loadPrtFailed` 로 올려 `DashMainWindow` 모달이 N회 뜨는지, 모달이 동기 emit 루프 안에서 이벤트 루프를 세워 남은 통지를 지연시키는지 실측한다. 배치 측 오계상(CAD-c53)과 같은 뿌리이므로 결과를 CAD-01 의 구독자 필터 설계 입력으로 넘긴다.
- 완료 기준: 실측 결과 — `tests/daemon_stub.cpp` + `test_process_runtime` 으로 "큐 2건 + 기동 실패" 를 재현해 (1) `commandFailed` 방출 횟수 (2) 대화형 경로에서 모달이 몇 번 뜨는지(수동 1회) (3) 합산 정책 선택 — 첫 통지만 모달·나머지는 로그 / 요청 태그별 1회 / 현행 유지(#249 가 축소 범위 밖으로 명시) — 를 기록한다. NX 불요(스텁으로 재현)
- 변경 범위: (조사만) controller/DashExtensionProcess.cpp:drainCommands · controller/DashSolverNxCad.cpp:emitFailure · view/DashMainWindow.cpp(loadPrtFailed 람다) · tests/daemon_stub.cpp · tests/TestProcessRuntime.cpp
- 선행: -
- 충돌: CAD-01 (결과가 구독자 필터 설계에 들어간다 — 본 항목이 먼저) · EXE-12 (같은 계약 문서 · tests/TestProcessRuntime.cpp) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashSolverNxCad.cpp → CAD-02 CAD-03 CAD-06 CAD-08 · TestProcessRuntime.cpp → EXE-11 · DashExtensionProcess.cpp → EXE-11 · daemon_stub.cpp → EXE-11 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #652(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: #249(범위 밖 절 — 모달 N회) · CAD-c15
- 비고: 검토 #14. fan-out 자체는 코드로 성립하나 모달 횟수·순서는 모달이 중첩 이벤트 루프를 세우는지에 달려 실측이 필요하다. "현행 유지" 로 끝나면 CLOSE 사유만 남기고 PR 없이 닫는다. EXE-12 가 "비정상 종료 = 진행·대기 명령 전부 실패" 를 계약으로 고정하므로 방출 횟수 자체는 바꾸지 않고 **소비자 측 합산**만 정한다.

### CON — Condition Parameterization

> 기준 dev @ b08a91b3. 원자 항목은 02-claims/CON.md — 28건 중 유효 19건(c01 c03 c04 c05 c07 c08 c09 c14 c15 c16 c18 c20 c21 c22 c23 c24 c25 c26 c28)을 개념별로 11개 항목으로 묶었다. 해소됨 5건(D2 D6 D10 D11 D12)·범위밖 4건(D13→ANA · U5 RW 몫→EXE · #645 복사 실패→PRJ · c27 DV 모델 소유권→DOE)은 항목 없음. CON-08 은 결번(DOE-10 병합, B2).
> 진행 중 PR 과의 접점: 열린 PR 6건(#658 #656 #655 #654 #652 #651) 중 CON 파일과 겹치는 것은 **4건** — #651 #652 #654 #655 가 전부 `view/DashMainWindow.cpp` 와 `tests/CMakeLists.txt` 를 고친다. #656 은 겹침 0, #658 은 `tests/rw/FakeRwModule.h` 뿐(CON-09 범위에서 제외됨). #530 은 머지하지 않으므로 충돌에서 뺀다(decisions ②). CON 고유 파일(위젯·모델·viewmodel·`.ui`)을 직접 고치는 열린 PR 은 없다.
> #655 는 CON 항목의 **선행이 아니다** — MainWindow hunk 가 `handleSubItemSelection`(:1333)·`initializeMorphingController`(:2190)·`setupMorphingBar`(:2405) 에만 있어 CON-03(`addReferenceFile`·`copyFileIntoProject`)·CON-05(`handleConditionParameterizationSelection`)·CON-06(`unbindSetWidgets`) 과 함수가 겹치지 않는다. 단순 충돌만 등록(decisions ④).
> Phase B1 흡수(범위밖 이관, CON-c22~c25): PRJ-c19 → CON-04 · PER-c24 → CON-11(신규) · EXE-c43 CON 몫 → CON-07(D9)·해소됨(D11) · UIC-c57 CON 몫 → CON-09.

#### CON-01 · 저장된 체크 상태를 행 재구축 뒤에 적용해 첫 진입에서도 복원되게 한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `loadFromJson` 을 "설정 읽기(핀·source 힌트·체크 키 집합)" 와 "행에 체크 적용" 으로 나누고, 적용을 `rebuildFromDocument` 의 `endResetModel()` 앞에서 실행한다. 적용 단계는 **IOController 없이 호출할 수 있는 seam** 으로 노출한다(`applyDvConditionSection(const QJsonObject&)` 또는 설정 경로 setter) — 그래야 테스트에서 돈다. 지금은 세 호출처가 전부 행 생성 전에 돌아 첫 진입이 전부 해제로 보이고, 그 상태의 [Set Design Variable] 이 `DV-Condition` 을 `{}` 로 덮는다.
- 완료 기준: (1) 새 세션 첫 진입에서 FE 탭 체크가 JSON 의 `boolean` 과 일치한다 (2) 그 직후 [Set Design Variable] 이 기존 DV 를 보존한다 (3) `TestConditionParameterization` 에 "재구축 뒤 체크 복원" 케이스 추가(gen4 키로 1행만 묶이는지 포함) — 적용 단계를 `DashProjectManager` 스텁 없이 직접 부를 수 있어야 한다
- 변경 범위: model/DashConditionParameterization.h · model/DashConditionParameterization.cpp · tests/TestConditionParameterization.cpp
- 선행: -
- 충돌: CON-02 (같은 `rebuildFromDocument`) · CON-05 (같은 모델 파일) · CON-09 (같은 테스트 파일) · B2 교집합: DashConditionParameterization.cpp → CON-06 PRJ-09 UIC-20 · TestConditionParameterization.cpp → CON-11 · DashConditionParameterization.h → CON-06
- 흡수: CON-D7 · CON-c07
- 비고: 핀 해석(`resolveReferenceDeck`)은 deck 로드 전에 `m_referenceModel`·`m_dvSourceHints` 를 써야 하므로 "읽기" 는 지금 시점을 유지한다. stale uuid 재바인딩의 QSaveFile 쓰기는 적용 단계로 옮긴다. 편집 commit 마다 재구축이 도니 파싱 결과를 멤버로 캐시할지 구현에서 정한다. **seam 이 필요한 근거**(검토 #9) — `tests/TestConditionParameterization.cpp:94-104` 가 `DashProjectManager::Instance()`→nullptr · `getConfigFilePath`→`{}` 로 스텁하므로 `setProjectDirectory`(:30-50)·`setSetName`(:60-78) 이 조기 반환하고 `loadFromJson` 이 아예 돌지 않는다. CON-09·CON-11 의 완료 기준이 이 seam 에 걸린다. **최소 대안** — "읽기/적용 분리 + 멤버 캐시" 대신 `refreshFromLoadedAnalysis` 가 `rebuildFromDocument` 직후 `loadFromJson()` 을 1회 더 부르는 안(:125-146, 편집 commit 경로는 existing 행이 `isChecked` 를 보존하므로 불필요)을 구현에서 함께 재고한다.

#### CON-02 · 행 재구축이 사라진 조건과 다른 source 의 행을 버린다
- 종류: PR | 규모: S | 태그: A, C · bug
- 목표: `rebuildFromDocument` 가 현재 세대의 조건 이름 집합 밖에 있는 행과 현재 deck 파일명이 아닌 source 의 행을 제거한다. 남는 행의 `isChecked` 는 지금처럼 보존한다. Set↔deck 1:1(#603) 이후 다른 source 행이 남을 정당한 이유가 없다.
- 완료 기준: (1) 조건이 빠진 deck 으로 재구축하면 그 행이 표에서 사라진다 (2) 핀이 다른 파일로 재해석돼도 이전 파일 행이 남지 않는다 (3) 테스트 케이스 — 조건 2개 deck → 1개 deck 재로드 후 `rowCount()==1`
- 변경 범위: model/DashConditionParameterization.cpp · tests/TestConditionParameterization.cpp
- 선행: -
- 충돌: CON-01 (같은 함수) · CON-09 · B2 교집합: DashConditionParameterization.cpp → CON-05 CON-06 PRJ-09 UIC-20 · TestConditionParameterization.cpp → CON-11
- 흡수: CON-D3 · CON-c03
- 비고: 하류 `DashAnalysisLauncher` 가 DV 별 `source` 로 참조 파일을 모으는 설계는 JSON 쪽 계약이라 영향 없음.

#### CON-03 · 덮어쓴 기준 deck 을 표시 중인 Condition 위젯이 다시 읽는다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `DashMainWindow::addReferenceFile` 의 `registry.load` **성공 직후**에, 표시 중인 Condition 위젯의 핀 deck 파일명이 방금 덮어쓴 파일과 같으면 `refreshFromFile` 을 다시 부른다(`refreshConditionWidgetFor` 1줄). 위젯 쪽은 `refreshFromFile` 이 재로드 전에 `clearFeConditionHighlight()` 를 부르게 하는 1줄만 바꾼다.
- 완료 기준: (1) Add File 로 같은 이름의 다른 deck 을 덮어쓰면 열려 있는 Condition 표가 새 조건 목록으로 바뀐다 (2) 다른 deck 을 핀한 Set 은 영향 없음 (3) 덮어쓰기 중 선택돼 있던 하이라이트가 남지 않는다 (4) 훅이 `QFile::copy` **뒤**에 돈다 — 구 파일을 다시 파싱하지 않는다
- 변경 범위: view/DashMainWindow.cpp · view/DashConditionParameterizationWidget.cpp
- 선행: CON-02 (유령 행을 먼저 없애야 새 내용만 보인다) · PRJ-21 (복사 원자화가 먼저 들어가면 훅이 그 성공 분기에 얹힌다 — 순서만, 기능 의존 아님)
- 충돌: 열린 PR #651 #652 #654 #655 (`view/DashMainWindow.cpp`) · CON-04 CON-06 CON-07 (위젯 파일) · PRJ-21 (#645 — 복사 실패 복원, 같은 함수군) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashConditionParameterizationWidget.cpp → CON-05 CON-12 DOE-19 UIC-19 UIC-20
- 흡수: #645 (CON 몫) · #645-1 (PRJ-20 이 CLOSE 로 넘긴 집행분) · CON-c18
- 비고: **훅 위치 교정**(검토 #1 · decisions ⑦) — `discardLoadedReferenceFile`(:2727) 은 `QFile::remove`(:2715)·`QFile::copy`(:2718) 보다 **앞**에 돌아 거기서 `refreshFromFile` 을 부르면 구 파일을 다시 파싱하거나 삭제와 경쟁한다. 새 내용이 로드되는 자리는 호출자의 `co_await addReferenceFile`(:2694) → `registry.load`(:2766) 뒤다. "public 진입점 노출" 문구는 삭제 — `refreshFromFile`·`pinnedDeckFileName` 이 이미 public(`view/DashConditionParameterizationWidget.h:41,45`)이고 `clearFeConditionHighlight` 는 private 이라 위젯 변경은 `refreshFromFile` 안 1줄로 끝난다(헤더 무변경). **PRJ-20 과의 관계** — 같은 #645-1 을 PRJ 가 PRJ-20 으로 항목화했으나 decisions ⑦ 이 **CON-03 에 남기기로 확정**했고 PRJ-20 은 CLOSE 다(PRJ 헤더 변경 불요 → 실질 1파일). 충돌란에서 `PRJ-20` 을 뺐다. 대안은 레지스트리에 `invalidated(filePath)`/`documentChanged` 를 쓰는 것 — 레지스트리가 invalidate 후 load 를 첫 로드로 보아 `documentChanged` 를 내지 않고(REN) CON 모델은 #565 로 방송 구독을 걷었으므로, 통지 책임은 덮어쓰기를 집행한 MainWindow 다.

#### CON-04 · 프로젝트 전환 뒤 해제된 조건 모델 역참조를 QPointer 로 막는다
- 종류: PR | 규모: S | 태그: A, E · bug
- 목표: `DashConditionParameterizationWidget::mModel` 과 `DashFeConditionValueDelegate::m_dataModel` 을 `QPointer<DashConditionParameterization>` 으로 바꾼다 — **이 2곳뿐**. `clearAllSets` 가 모델을 지우면 둘 다 null 이 되어 기존 `!mModel`/`!m_dataModel` 가드가 그대로 작동한다.
- 완료 기준: (1) 프로젝트 A → B 전환 뒤 Condition Set 클릭·표 셀 더블클릭·DV JSON 외부 변경에서 크래시·ASan 보고 없음 (2) 변경은 헤더 2개의 멤버 선언뿐 — 가드를 새로 넣지 않는다
- 변경 범위: view/DashConditionParameterizationWidget.h · view/delegate/DashFeConditionValueDelegate.h
- 선행: -
- 충돌: CON-03 CON-06 CON-07 (위젯 헤더) · PRJ-01 (#551 — 7개 위젯을 한 PR 로 묶으면 이 항목은 그쪽에 흡수) · UIC-19 (같은 위젯 — 설계 충돌이 아니라 순서만, 아래 비고) · B2 교집합: DashConditionParameterizationWidget.h → CON-05
- 흡수: #551 (CON 몫) · #551 별개 1 (PRJ-c19 이관) · CON-c20 · CON-c22
- 비고: #551 not-to-be 가 적은 "delegate 는 QPointer 로 해결되지 않는다" 는 2-인자 `setModel` 이 null 을 조기 반환하기 때문인데(PRJ-c19 가 같은 지적), delegate 포인터 자체를 QPointer 로 두면 그 경로와 무관하게 null 이 된다. 리셋 계약 명문화는 #431(PRJ-02). **`GetProject` 가드 신설은 기각**(검토 #4 · decisions ⑦) — `DashProjectManager::GetProject()` 는 ctor 에서 1회 `new` 하고 재할당이 없어(`controller/DashProjectManager.cpp:26-28`·`:45-48`) 항상 non-null 이고, 같은 파일에서 바로 그 가드를 **삭제**하는 UIC-19 의 완료 기준을 깬다. 규모·변경 범위를 QPointer 2곳으로 줄였다. `setModel` 안의 실제 무가드 역참조(`mModel->getSettingsJsonPath()` — qobject_cast 실패 시 · `getIOController()->getConfigsDirectory()` :369-371)는 setModel 경로를 합치는 **CON-06** 이 같은 줄에서 다룬다. **PRJ-01(전환 전 전 위젯 `setModel(nullptr)`)이 먼저 랜딩하면 이 항목은 CLOSE** — 1-인자 경로가 delegate 까지 null 로 만든다(PRJ-01 비고와 교차).

#### CON-05 · `setProjectDirectory` 의 중복 호출과 무시되는 인자를 걷어낸다 (PRJ-08 계약의 CON 적용분)
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: CON 모델의 설정 읽기를 한 번만 돌게 한다 — (a) Set 선택 경로의 중복 1곳(위젯 2-인자 `setModel`:321)을 지우고 `handleConditionParameterizationSelection`(:1436) 만 남긴다 (b) `renameSet`(`model/DashProject.cpp:1756`) 의 `setSetName` + `setProjectDirectory` 2중 읽기에서 뒤 호출을 지운다(`setSetName` 이 이미 경로를 다시 짜고 `loadFromJson` 을 부른다) (c) 2-인자 `setModel(model, projectPath)` 의 `Q_UNUSED(projectPath)` 인자와 호출부(`view/DashMainWindow.cpp:1438`)의 인수를 삭제한다. **시그니처 처분(유지·개명·삭제)은 PRJ-08 이 9클래스 공통으로 정하고, 이 항목은 그 적용분이다.**
- 완료 기준: (1) Set 선택 1회에 `loadFromJson` 이 1회 (2) Set 이름 변경 1회에 `loadFromJson` 이 1회 (3) 위젯 `setModel` 에 `Q_UNUSED` 0 (4) 동작 불변 — 핀 해석·체크 복원 결과 동일
- 변경 범위: view/DashConditionParameterizationWidget.h · view/DashConditionParameterizationWidget.cpp · view/DashMainWindow.cpp · model/DashProject.cpp (+ PRJ-08 이 개명·인자 삭제를 정하면 `model/DashConditionParameterization.h/.cpp`)
- 선행: CON-01 (설정 읽기/적용 분리 뒤에 호출 수를 줄여야 체크 복원이 안 깨진다) · PRJ-08 (Set 모델 공통 계약 — 아래 비고의 역순 조건)
- 충돌: 열린 PR #651 #652 #654 #655 (`view/DashMainWindow.cpp`) · PR #651 #652 (`model/DashProject.cpp`) · CON-06 (MainWindow·위젯) · PRJ-08 (`setProjectDirectory` 계약) · PRJ 의 `model/DashProject.cpp` 항목 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · DashConditionParameterizationWidget.cpp → CON-03 CON-07 CON-12 DOE-19 UIC-19 UIC-20 · DashConditionParameterization.cpp → CON-02 PRJ-09 UIC-20 · DashConditionParameterizationWidget.h → CON-04 CON-07
- 흡수: CON-D1 · CON-c01 · CON-c28 (`Q_UNUSED(projectPath)`)
- 비고: **PRJ-08 이 계약, 이 항목이 적용**(decisions ⑦) — 다른 Set 모델 8종(+ `DashModelRunnerMCU::setProjectDirectory(userPath, projectPath)` 2-인자 변종)도 같은 관례라 개명/인자 처분을 CON 혼자 정하면 어긋난다. **역순 허용** — decisions ⑧ 이 지적한 Set 모델 공통 베이스 부재로 PRJ-34(DEC) → PRJ-08 이 늦어져 이 항목이 블록되면, (a)(b)(c) 만 CON 에서 먼저 내고 시그니처는 PRJ-08 이 일반화할 때 맞춘다. 그때도 `setProjectDirectory` 심볼 삭제는 완료 기준에 넣지 않는다. 숫자 정정(검토 #3) — 호출은 5곳이고 Set 선택 시 읽기는 2회다(1-인자 `setModel`:392 는 nullptr 로만 호출돼 도달 불가 — CON-06 이 그 오버로드를 지울 때 함께 사라진다). 파일 4개라 M 이지만 작업량은 반나절.

#### CON-06 · 도달 불가 경로와 드리프트한 선언을 제거한다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: (a) `setModel` 진입점을 2-인자 하나로 합치고 null 을 리셋(연결 해제·delegate null·표 비움)으로 처리, 1-인자 오버로드와 그 안의 `dataChanged→updateUI`·`dataLoaded→onModelDataLoaded` 연결 블록, 수신처 0곳인 `dataLoaded` 시그널을 제거 (b) `directoryChanged` 가 연결되지 않는 userPath 디렉토리 감시, `onDvJsonChanged` 의 `else` 분기, `onDirChanged`, `updateDvWatcher` 별칭을 제거 (c) `.ui` 의 5열 선언을 모델 7열과 맞추거나 열 선언을 지우고 주석으로 정본(모델)을 가리킨다.
- 완료 기준: (1) `DashConditionParameterizationWidget` 에 public `setModel` 이 하나 (2) `QFileSystemWatcher::directories()` 가 항상 비어 있다 (3) Set 삭제 경로(`unbindSetWidgets`)에서 표가 비고 delegate 가 에디터를 열지 않는다 (4) `.ui` 열 수 == `columnCount()`
- 변경 범위: view/DashConditionParameterizationWidget.h · view/DashConditionParameterizationWidget.cpp · ui/DashConditionParameterizationWidget.ui · model/DashConditionParameterization.h · model/DashConditionParameterization.cpp · view/DashMainWindow.cpp (`unbindSetWidgets` 호출 1줄)
- 선행: CON-04 (QPointer 로 바꾼 뒤 리셋 경로를 정리해야 두 번 손대지 않는다) · PRJ-02 (리셋 계약 DEC — (a) 가 "null = 표 비움" 으로 동작을 바꾸므로 계약을 먼저 받는다)
- 충돌: CON-03 CON-05 CON-07 · 열린 PR #651 #652 #654 #655 (`view/DashMainWindow.cpp`) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashConditionParameterizationWidget.cpp → CON-12 DOE-19 UIC-19 UIC-20 · DashConditionParameterization.cpp → CON-01 CON-02 PRJ-09 UIC-20 · DashConditionParameterization.h → CON-01
- 흡수: CON-U1 · CON-U3 · CON-D4 · CON-c14 · CON-c15 · CON-c04
- 비고: 세 결함 모두 "정본이 아닌 선언·경로" 라 한 개념으로 묶었다. **분할 지적(검토 #5)은 기각** — 1-인자 오버로드는 `nullptr` 로만 호출되는 도달 불가 경로이고, 그것을 지우려면 2-인자가 null 을 받아야 하므로 (a) 의 동작 변경은 (b)(c) 와 같은 "죽은 선언·경로 제거" 개념의 귀결이다. 00-plan 1-2 "개념적 응집" 기준으로 개념이 하나면 동작 변경·리팩터가 섞여도 유지한다. 대신 검토가 지적한 의존은 받았다 — 선행에 PRJ-02 추가. MainWindow 변경은 `unbindSetWidgets` 호출 1줄뿐이라 열린 PR 4건이 길어지면 그 1줄만 뒤로 떼어 내는 순서 조정으로 흡수한다(항목 분할은 하지 않는다). `setParent(this)` 로 공용 DV 모델 소유권을 빼앗는 줄(:331, CON-c27)은 여기 넣지 않았다 — **보류: DOE 몫**(소유자 결정이 `DashDesignVariableModel` 소관). `saveSettings` 빈 슬롯과 미사용 `JsonKeys` 네임스페이스도 같은 파일에 있으나 원천 밖이라 언급만 한다.

#### CON-07 · DV 저장 뒤 자기 쓰기 억제를 실제로 작동하게 한다
- 종류: PR | 규모: S | 태그: B, D · bug
- 목표: `m_blockDvWatcher` 를 동기 구간에서 되돌리는 방식(큐로 오는 `fileChanged` 를 못 막는다)을 **횟수 무관 설계**로 바꾼다 — 자기 쓰기 직후 `updateDvWatchers()` 로 감시를 재등록하고, 배달된 `fileChanged` 는 마지막으로 쓴 바이트(또는 mtime·크기)와 같으면 리로드를 생략한다. 같은 줄에서 `syncDvFromCheckedFeConditions` 의 성공 모달 `QMessageBox::information` 을 `DashNotify::info` 로 바꾼다(UIC-17 이 추가하는 변형).
- 완료 기준: (1) [Set Design Variable] 1회에 `loadFromJsons` 가 1회(저장 직후 명시 리로드)만 돈다 (2) DV-Condition 탭 셀 편집 1회에 워처 리로드 0회 (3) 외부 편집기로 JSON 을 바꾸면 리로드 1회 — 단 **원자 저장(rename) 편집기에서 감시가 끊기는 기존 한계는 그대로다**(`QFileSystemWatcher` 가 inode 를 잃는다), 재등록 시점이 자기 쓰기 뒤뿐이므로 (4) CON 영역 직접 `QMessageBox` 0
- 변경 범위: view/DashConditionParameterizationWidget.h · view/DashConditionParameterizationWidget.cpp
- 선행: CON-11 (`saveDvCondition` 이 `QSaveFile` 로 바뀌면 같은 파일의 `fileChanged` 패턴이 달라진다 — 아래 비고) · UIC-17 (`DashNotify::info`)
- 충돌: CON-03 CON-04 CON-06 (같은 위젯) · B2 교집합: DashConditionParameterizationWidget.cpp → CON-05 CON-12 DOE-19 UIC-19 UIC-20 · DashConditionParameterizationWidget.h → CON-05
- 흡수: CON-D9 · CON-c09 · CON-c21 · CON-c24 (EXE-c43 CON 몫 — D9 전용)
- 비고: **"1회 무시 토큰" 안을 버린 이유**(검토 #6) — 무시 횟수가 플랫폼·쓰기 프리미티브에 따라 달라진다. 현행 `saveDvCondition`(`QIODevice::Truncate` 직쓰기, `viewmodel/DashConditionParameterizationPresentationModel.cpp:135-142`)은 1~2회를 내고, CON-11 이 `QSaveFile`(rename) 로 바꾸면 macOS 에서 감시가 끊겨 0회가 될 수 있어 토큰이 남아 **다음 외부 변경을 삼킨다**. 감시 대상이 바로 `saveDvCondition` 이 쓰는 `mModel->getSettingsJsonPath()` 와 같은 파일이라 둘은 직결이다. 따라서 CON-11 을 선행으로 두고 횟수에 의존하지 않는 설계로 간다. 횟수 실측이 필요하면 CON-11 랜딩 뒤 플랫폼별 `fileChanged` 횟수 INV 를 따로 낸다. CAD 위젯(`DashGeometryParameterCADWidget`)이 같은 플래그 패턴을 쓰므로 CAD 가 같은 설계를 재사용할 수 있다. `QMessageBox` → `DashNotify::info` 는 같은 함수 1줄이라 UIC-17 뒤 이 항목이 함께 처리한다(검토 #7, UIC 대응표의 "CON 1").

#### CON-09 · dvKey 채번과 gen1~gen4 체크 바인딩에 회귀 테스트를 붙인다
- 종류: PR | 규모: S | 태그: F · refactor
- 목표: `TestConditionParameterization` 에 (a) dvKey 3규칙 — 엔트리 1개는 맨이름, Abaqus 다수 엔트리는 `{name}_e{N}`, flat 다수 필드는 `{name}_{param}` (b) DV-Condition 의 gen1(이름)·gen2(uuid)·gen3(uuid+entry_ptr)·gen4(uuid+entry_ptr+param) 엔트리가 각각 어느 행을 체크하는지 (c) 이름으로만 묶였는데 저장 uuid 가 다르면 파일의 uuid 가 재기록되는지 를 추가한다.
- 완료 기준: (1) 케이스 3군 통과 (2) 기존 10케이스 영향 없음
- 변경 범위: tests/TestConditionParameterization.cpp
- 선행: CON-01 (IOController 없이 설정 JSON 을 행에 적용하는 seam 이 생긴다 — CON-01 목표·비고에 명시) · EXE-21 (flat 조건 픽스처를 `tests/rw/FakeRwModule.h` 에 만드는 쪽)
- 충돌: CON-01 CON-02 (같은 테스트 파일) · B2 교집합: TestConditionParameterization.cpp → CON-11
- 흡수: CON-U5 (CON 몫) · CON-c16 · CON-c25 (UIC-c57 CON 몫)
- 비고: **픽스처 몫은 EXE-21**(decisions ⑦ · 검토 #8) — 구 완료 기준 (2) "FakeRwModule 로 flat 조건을 만들 수 있다" 를 삭제하고 `tests/rw/FakeRwModule.h` 를 변경 범위에서 뺐다. 공용 픽스처이고 흉내낼 대상(`DashRwDocument` flat 스키마 분해)이 EXE 소관이며 이 항목은 픽스처를 **쓰는** 쪽이다. 이로써 `FakeRwModule.h` 충돌(EXE-21 · 열린 PR #658)도 소멸한다. 태그는 `docs` 오분류를 `refactor` 로 정정(EXE-21 과 동일). flat 분해·요약 행·Discrete/Categorical 분류 자체의 테스트도 EXE 몫 — CON-c17.

#### CON-10 · Value 인라인 편집의 영속 정책을 정한다
- 종류: DEC | 규모: S | 태그: A, C
- 목표: 세대 모델 도입 뒤 Value 편집은 레지스트리의 메모리 세대만 바꾸고 프로젝트 재로드에서 사라진다. 세 안 중 하나를 기록한다 — (A) 세션 한정으로 못박고 표·툴팁에 "저장되지 않음" 표시 (B) `ConditionParameter_Set{N}.json` 에 `{uuid, entry_ptr, param, value}` 덮어쓰기 절을 두고 로드 직후 `toMutable→edit→seal→publish` 로 재적용 (C) 편집 시 deck 파일 자체를 `exportSolverInput` 으로 다시 쓴다 (content uuid·원장 스탬프 갱신 수반).
- 완료 기준: 결정 기록 — 선택안, 하류(DOE 주입·Launcher 참조 파일·Model Runner `inputFileName`)에 미치는 영향, 후속 PR 범위
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: CON-D5 · CON-c05
- 비고: (B) 가 가장 자연스럽지만 PER 의 저장 포맷 규칙과 PRJ 의 Set 원장(`DashSetReferenceModel`)에 걸친다. (C) 는 #617 의 "덮어쓰기 = invalidate" 흐름과 충돌한다.

#### CON-11 · `saveDvCondition` 의 읽기-병합-직쓰기를 공용 JSON 헬퍼로 이행한다
- 종류: PR | 규모: S | 태그: A · refactor
- 목표: `DashConditionParameterizationPresentationModel::saveDvCondition` 이 `QFile` 로 기존 파일을 읽어 `DV-Condition` 절을 합친 뒤 `QIODevice::Truncate` 직쓰기하는 경로(RMW · `write` 길이 무검사)를 **PER-02 가 공용 진입점으로 승격하는 `DashSaveSystem` 헬퍼**(`readJsonFile`/`writeJsonFile` — QSaveFile · `Result` 반환)로 바꾼다. 쓰기 중 크래시·디스크 풀에서 `FE Condition` 등 기존 절이 함께 소실되지 않는다. 동작 불변.
- 완료 기준: (1) `viewmodel/DashConditionParameterizationPresentationModel.cpp` 에 `QFile` 직쓰기 0 (2) 쓰기 실패(읽기 전용 경로) 시 기존 파일 바이트 동일 + WARN 에 사유 (3) `ConditionParameter_<Set>.json` 저장→로드→재저장 동일 — 케이스 1건 (PER-05 왕복 헬퍼가 랜딩해 있으면 그것으로, 아니면 이 TU 안에서 비교)
- 변경 범위: viewmodel/DashConditionParameterizationPresentationModel.cpp · tests/TestConditionParameterization.cpp (왕복 케이스) · tests/CMakeLists.txt (`test_condition_parameterization` 타깃에 PM `.cpp` 추가)
- 선행: PER-02 · CON-01 (왕복 케이스가 설정 JSON 을 행에 적용하는 seam 을 쓴다)
- 충돌: CON-09 (같은 테스트 파일) · 열린 PR #651 #652 #654 #655 (`tests/CMakeLists.txt`) · PER-02 · PER-05 · UIC-17 · DEV 의 `tests/CMakeLists.txt` 항목 · B2 교집합: tests/CMakeLists.txt → 공유 12건(deps.md 5절) · TestConditionParameterization.cpp → CON-02
- 흡수: #479 · #478 · #480 (CON 몫, PER-c24 이관) · CON-c23
- 비고: **문구 교정(decisions ③)** — PER-02 는 `utils/DashJsonFile` 신설이 아니라 `persistence/DashSaveSystem::read/writeJsonFile` 승격으로 확정됐다. API 이름도 `readObject/writeObject` → `readJsonFile/writeJsonFile`. **`tests/CMakeLists.txt` 추가 근거(검토 #10)** — `test_condition_parameterization` 타깃(`tests/CMakeLists.txt:616-623`)의 소스가 모델·`DashSetReferenceModel`·registry.h·`DashRwDocument`·`DashRwActor`·`DashRwDocumentHandle` 뿐이고 `viewmodel/DashConditionParameterizationPresentationModel.cpp` 가 없어, 왕복 케이스를 이 TU 에 두려면 링크를 늘려야 한다. 대안 — PM 을 링크하지 않고 PER-02 의 `TestJsonFile` 에 케이스를 두면 `tests/CMakeLists.txt` 충돌 10건을 피할 수 있다. 구현에서 택일하고, 후자를 고르면 완료 기준 (3) 과 변경 범위에서 CMakeLists 를 뺀다. `loadFromJson` 의 재바인딩 write-back 은 이미 QSaveFile. 버전 키는 PER-04 뒤 헬퍼가 자동 기록 — 여기서 따로 하지 않는다. `DashDesignVariableModel::saveToJsonFiles` 는 DOE-17 (B2 — 소속 DOE). **2차 반영(C' 2차)** — `선행: PER-05` 제거 (PER 검토 #9: 왕복 게이트를 선행으로 걸면 bug fix 가 인프라 PR 을 기다린다. 왕복 케이스는 모듈 완료 기준에만 두고 선행으로 걸지 않는다 — DOE-17 과 같은 처리). `충돌` 의 PER-05 는 같은 테스트 파일을 만지므로 유지.

#### CON-12 · FE 표의 체크 토글을 모델에 바로 써서 재구축에 잃지 않게 한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: col 0 의 `itemChanged` 가 헤더 체크박스만 갱신하는 자리에서 `mModel->setData(index(modelRow,0), state, Qt::CheckStateRole)` 로 write-through 하고, `syncDvFromCheckedFeConditions` 선두의 역동기화 루프를 지운다. 지금은 토글이 `QTableWidgetItem` 에만 머물다가 `modelReset` → `populateFeConditionTable` 이 모델의 `CheckStateRole` 로 다시 그려 저장 전 토글이 조용히 사라진다.
- 완료 기준: (1) 체크 → Value 셀 편집(`commitEntryValue` 가 reset 을 낸다) 뒤에도 체크가 남는다 (2) 헤더 전체 체크/해제도 모델에 반영된다 (3) [Set Design Variable] 결과가 전과 같다 — `collectCheckedFeRows` 가 `getCheckedParameters()` 를 쓰므로 write-through 만으로 충분하다
- 변경 범위: view/DashConditionParameterizationWidget.cpp
- 선행: CON-01 (모델 체크의 의미 — 저장된 체크를 재구축 뒤 적용하는 계약 — 이 먼저 서야 write-through 가 그 값과 싸우지 않는다)
- 충돌: CON-03 CON-04 CON-06 CON-07 (같은 위젯) · B2 교집합: DashConditionParameterizationWidget.cpp → CON-05 DOE-19 UIC-19 UIC-20
- 흡수: CON-c26
- 비고: 검토 #11 신설. 좌표 — `itemChanged` 핸들러 `:166-170`(헤더만) · `modelReset`→`populateFeConditionTable` 연결 `:297-302` · 재취득 `:510-518` · 버튼 때만 도는 역동기화 루프 `:566-577` · reset 원천 `model/DashConditionParameterization.cpp:458`. CON-c18(덮어쓰기 재로드) 도 같은 소실을 일으키므로 CON-03 뒤에 랜딩하면 그 경로까지 덮인다. `blockSignals(true)` 로 그리는 `populateFeConditionTable` 안에서는 `itemChanged` 가 안 나므로 write-through 가 재귀하지 않는다.

### DOE — DOE Sampler

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> 기준 dev @ b08a91b3. 열린 PR 7건 중 머지 대상 6건 (#651 #652 #654 #655 #656 #658 — 05-final/decisions.md ⑩). DOE 항목과 파일이 겹치는 것: #652(DashDoeSampler.cpp/.h · DashProject.cpp · DashMainWindow.cpp · DashManager.cpp/.h · DashJobRunnerAnsysMotion.cpp · tests/CMakeLists.txt) · #651(DashProject.cpp/.h · DashMainWindow.cpp · DashAnalysisLauncherConfig.cpp/.h · TestAnalysisLauncherConfig.cpp · tests/CMakeLists.txt) · #654(DashMainWindow.cpp · DashManager.cpp · tests/CMakeLists.txt) · #655(DashMainWindow.cpp · tests/CMakeLists.txt). #656 · #658 은 DOE 변경 파일과 교집합 0 — 선행·충돌 없음 (2차 반영 판정, 01-sources/open_prs.md 파일 목록 대조).
> PR #530 은 머지하지 않는다 (C-2 결정 ② — base 가 스쿼시돼 dev 머지 불가). 공통부는 PER-07 이 다시 올리고 T27 홉 기록부는 DOE-16 이 dev 파일명 기준으로 재작성한다. 따라서 #530 은 충돌 대상이 아니다.

> #615 번호·기본 참조·자동 선택의 후속 개정은 팀 논의용 계획이다. 아래 기존 동작 제안은 확정된 setId 출처 계약과 구분하고 자동 선택 여부는 별도 결정한다.

#### DOE-02 · Resample 의 Reference Set 기본값을 직전 Set 으로 하고 DOE Table 없는 Set 을 후보에서 뺀다
- 종류: PR | 규모: S | 태그: D · feature
- 목표: Reference Set 콤보 후보를 "DOE Table(samples)이 있는 다른 DoeSampler Set" 으로 좁히고, 기본 선택을 `Resample(N-1)`(N=1 이면 `Init`)로 한다. 사용자는 바꿀 수 있다.
- 완료 기준: `Resample2` 진입 시 콤보 기본값 `DoeSampler_Resample1`, `Resample1` 은 `DoeSampler_Init` · samples 없는 Set 은 후보에 없음 · 기본값 Set 이 없으면 번호가 가장 큰 후보
- 변경 범위: model/DashDoeSampler.cpp (getAvailableReferenceSets — `DashDoeTableFile::hasDoeTableSamples` 필터) · view/DashDoeSamplerResampleWidget.cpp (refreshReferenceSetCombo) · model/preprocessor/DashDoeTableFile.cpp/.h(직전 Set 헬퍼, DOE-01 의 번호 파싱 공용)
- 선행: PRJ-33 (`ResampleN` 번호 헬퍼 — DOE 에서 이관)
- 충돌: PR #652 (DashDoeSampler.cpp) · B2 교집합: DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashDoeSamplerResampleWidget.cpp → DOE-20 UIC-20 · DashDoeTableFile.cpp → PER-02
- 흡수: #615-4 · DOE-c04
- 비고: 콤보 표기는 현행대로 `completeBaseName`(`DoeSampler_ResampleN`) 을 유지한다 — `referenceSetJsonPathFor(displayName + ".json")` 가 그 표기로 경로를 복원한다(DashDoeSamplerResampleWidget.cpp:154-168). Set 이름만 보이게 바꾸려면 경로 복원을 UserRole 로 옮기는 별건

#### DOE-03 · Resample prior 가 비활성 케이스를 Launcher Cases 의 `active` 로 거른다
- 종류: PR | 규모: M | 태그: A, C · bug
- 목표: `collectReferencePoints`·`getNextIterationForReferenceSet`·`runSpaceFillingResample` 이 DOE Table 의 `samples[].active`(항상 true) 대신 `AnalysisLauncher_*.json` 의 `Launcher Cases[<DoeSamplerSet>][runKey].active` 를 읽는다. `// TODO(#615)` 2곳을 걷는다.
- 완료 기준: Launcher 에서 비활성화한 케이스가 Resample prior·iteration 계산에서 빠진다 · Launcher Set 이 없거나 기록이 없으면 전부 활성(현행과 동일) · Init 재실행(새 `tableId`) 뒤 옛 Launcher 기록은 prior 에 영향 없음 · 읽기 함수 단위 테스트 (configs 디렉터리 고정물)
- 변경 범위: model/DashDoeSampler.cpp · model/preprocessor/DashAnalysisLauncherConfig.cpp/.h(참조 DOE Set 의 active 집계 — `readCases` 재사용 + Launcher json 열거) · tests/TestAnalysisLauncherConfig.cpp
- 선행: -
- 충돌: PR #651 (DashAnalysisLauncherConfig.cpp/.h) · PR #652 (DashDoeSampler.cpp) · B2 교집합: DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashAnalysisLauncherConfig.cpp → DOE-16 LCH-16 PRE-14 PRE-15 PRE-27 PRE-32 · TestAnalysisLauncherConfig.cpp → DOE-16 LCH-16 PRE-14 PRE-15 PRE-32 · DashAnalysisLauncherConfig.h → LCH-16 PRE-15 PRE-27 PRE-32
- 흡수: #615-6 · DOE-c06
- 비고: 결정 동반 — (1) 참조 DOE Set 을 스냅샷한 Launcher Set 이 여럿이면 어느 active 를 쓰나. 제안: 하나라도 active=true 면 포함, 기록 전무면 포함(기본 true). (2) 참조 Table 의 `tableId` 와 일치하는 케이스 기록만 본다 — `active` 만 보면 Init 재실행 전에 기록된 케이스가 새 Table 의 같은 runKey 에 붙어 다른 Table 의 값을 판정에 쓴다. 판독기는 `DashLauncherRuns::isCurrentCase` + `active` 조합을 재사용한다 — `resolveDoneRuns` 는 Done + resultFiles 조건까지 들어 prior 판정엔 과하다

#### DOE-05 · DOE Sampler 진입 시 `loadSettings` 를 1회로 만든다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: `setProjectDirectory`·`setSetName` 에서 `loadSettings()` 호출을 떼고, 위젯이 시그널 연결을 마친 뒤 1회만 부른다. `setProjectDirectory(path)` 의 미사용 인자를 정리한다. 설정·DV 표 복원 결과는 동일.
- 완료 기준: 트리 클릭 1회에 `DashDoeConfigManager::loadSettings` 1회 · `DashDesignVariableModel::loadFromJsons` 1회 · 표 재구축 1회 (로그로 확인) · 프로젝트 열기·Set 전환·재진입에서 purpose/method/options/선택 Set/parameterization 복원 동일 · DashDoeSamplerWidget.cpp 의 "signal might not be connected yet" 주석 소멸
- 변경 범위: model/DashDoeSampler.cpp/.h · view/DashDoeSamplerWidgetBase.cpp · view/DashDoeSamplerWidget.cpp · view/DashMainWindow.cpp (handleDoeSamplerSelectionForVariant) · model/DashProject.cpp (addDoeSampler)
- 선행: -
- 충돌: PR #652 (DashDoeSampler.cpp/.h · DashProject.cpp · DashMainWindow.cpp) · PRJ-33 · PRJ-24 · DOE-07 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · DashDoeSampler.h → DOE-08 DOE-11 DOE-12 LCH-14 · DashDoeSamplerWidget.cpp → DOE-06 DOE-09 DOE-11 DOE-13 UIC-20 · DashDoeSamplerWidgetBase.cpp → ANA-07 DOE-11 PRJ-25 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp·DashProject.cpp)
- 흡수: DOE-D1 · DOE-c10, DOE-c34 · LCH-c57(DOE-c53)
- 비고: `DashDoeSamplerWidget::populateJsonFiles` 끝의 "setModel 은 loadSettings 를 연결 전에 돌리므로 여기서도 복원" 경로도 함께 정리

#### DOE-06 · Probabilistic 모드의 Min/Max 편집을 모델·DV JSON 에 되쓴다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: Probabilistic 표의 Min/Max 스핀박스와 CSV Upload 의 Min/Max 가 General 과 같이 `DashDesignVariableModel` 3·4열 → DV JSON 으로 저장된다. σ 확장값(override)은 지금처럼 샘플링에만 쓴다.
- 완료 기준: Probabilistic 에서 Min 편집 → Set 재진입 후 값 유지 · CSV Upload 의 Min/Max 가 DV JSON 에 반영 · General 모드·override 계산 불변
- 변경 범위: view/DashDoeSamplerWidget.cpp (updateTableForSamplingMode Probabilistic 분기 · applyDvTableCsv)
- 선행: -
- 충돌: DOE-13 (같은 함수) · B2 교집합: DashDoeSamplerWidget.cpp → DOE-05 DOE-09 DOE-11 UIC-20
- 흡수: DOE-D2 · DOE-c11 · LCH-c58(DOE-c54)
- 비고: Min/Max 체크 해제(쌍 미사용) 상태의 저장 규칙은 구현 시 확정 — 제안: 값은 저장, 사용 여부는 저장하지 않음(현행과 같음)

#### DOE-07 · 샘플링 워커에 DV 값 스냅샷을 넘기고 결과 기록을 GUI 스레드로 옮긴다
- 종류: PR | 규모: M | 태그: B, A · refactor
- 목표: `onRunButtonClicked` 가 DV 행(name·type·min·max·cases·source·column)과 Probabilistic override 를 값 구조체로 떠서 `QtConcurrent::run` 에 넘기고, 워커는 샘플 JSON 만 반환한다. 워커 본체(스냅샷 → 샘플 JSON)는 `DashProjectManager` 비의존 TU(`model/DashDoeSampling.{h,cpp}`)로 떼고 `DashDoeSampler` 는 호출만 한다 — 지금 `runAnalysisInThread` 가 `DashProjectManager::Instance()->GetIOController()->getUserPath()` 를 부르기 때문. `saveResultsAsDvTable`(파일 쓰기)은 `onAnalysisCompleted` 에서 GUI 스레드로 돈다. `m_setIdsSnapshot` 선례를 일반화한다.
- 완료 기준: `runAnalysisInThread` 본문과 그 호출 트리에 `m_designVariableModel` 접근 0 · 새 TU 에 `DashProjectManager`·`DashIOController` 포함 0 (경로는 호출부가 인자로 준다) · `DoeSampler_{Set}.json` 쓰기가 GUI 스레드에서만 일어남 · override 는 스냅샷 행에 동봉되어 인덱스 불일치가 구조상 불가 · 5 method 의 샘플 출력 동일 · 스냅샷 입력으로 위젯 없이 도는 샘플링 단위 테스트 1건 (tests/TestDoeSampler.cpp 신규 — 새 TU 만 링크, seed 고정 5 method — #489 DOE 몫)
- 변경 범위: model/DashDoeSampling.h · model/DashDoeSampling.cpp (신규 — 샘플링 본체) · model/DashDoeSampler.cpp/.h · model/DashDoeConfigManager.cpp/.h (saveResultsAsDvTable 이 모델 포인터 대신 스냅샷을 받음) · tests/TestDoeSampler.cpp (신규) · tests/CMakeLists.txt
- 선행: -
- 충돌: PR #652 (DashDoeSampler.cpp/.h) · DOE-05 · DOE-09 · DOE-16 (`saveResultsAsDvTable` 서명) · B2 교집합: DashDoeSampler.cpp → 공유 15건(deps.md 5절) · tests/CMakeLists.txt → 공유 12건(deps.md 5절) · DashDoeSampler.h → DOE-08 DOE-11 DOE-12 LCH-14 · DashDoeConfigManager.cpp → DOE-11 DOE-17 · DashDoeConfigManager.h → DOE-11 · PR #655(tests/CMakeLists.txt) · PR #654(tests/CMakeLists.txt) · PR #651(tests/CMakeLists.txt)
- 흡수: DOE-D4 · DOE-D22(DOE 측) · DOE-c12, DOE-c14, DOE-c17 · LCH-c60(DOE-c56) · EXE-c41(DOE-D4·D22 몫, DOE-c62) · #489(DOE 몫) · DEV-c24(DOE-c63)
- 비고: 본체 분리는 테스트 가능성이 근거다 — tests/ 는 Qt Core only 소형 실행 파일이고 controller 는 `controller/async/*` 만 링크한다(tests/CMakeLists.txt:46-57). GUI 싱글턴을 끌어오는 `DashDoeSampler` 를 그대로 링크할 수 없어, 분리 없이는 #489 DOE 몫 테스트가 불가하다. 실행 모델 표준(EXE)이 Job 타입을 정하면 그 위에 올린다 — 선행으로 두지는 않는다

#### DOE-08 · Purpose→Method 대응표를 한 곳에 두고 콤보가 그 표에서 채워지게 한다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `{purpose, method, options}` 정적 표 1개를 `getPurposeOptions`·`onSetButtonClicked`·생성자 기본값이 공유하고, `.ui` 의 purposeCombo 정적 항목을 지운다. 콤보가 표에서 채워지므로 "표에 없는 purpose" 분기는 구조상 사라진다.
- 완료 기준: purpose 문자열 리터럴 1곳 · 5 purpose 각각 [Set] → 현행과 같은 method/options · 표의 method 이름이 `DashDoeSamplerWidget::setupMethodData` 의 5 이름과 같아 콤보 선택이 유지된다 · `ui/DashDoeSamplerWidget.ui` purposeCombo 항목 0개
- 변경 범위: model/DashDoeSampler.cpp/.h · ui/DashDoeSamplerWidget.ui
- 선행: -
- 충돌: PR #652 (DashDoeSampler.cpp/.h) · DOE-05 · DOE-07 · B2 교집합: DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashDoeSampler.h → DOE-11 DOE-12 LCH-14
- 흡수: DOE-D3 · DOE-U5(ui 항목) · DOE-c13, DOE-c23 · LCH-c59(DOE-c55)
- 비고: method 이름 리터럴은 뷰에도 있다 — `setupMethodData` 의 5 method + options(view/DashDoeSamplerWidget.cpp:892-917). `onSetButtonClicked` 의 recommendedMethod 가 그 이름과 맞아야 콤보가 선택되므로 완료 기준에 일치 조건만 둔다. 뷰 표 자체의 통합은 별건. 표를 `DashDoeSamplerPresentationModel` 로 옮기지는 않는다 — 소비자 3곳이 모두 model 층이고 `model/` 은 `viewmodel/` 을 포함하지 않는다(현행 0건). `resampleMethodCatalog()` 선례는 소비자가 뷰 1곳인 카탈로그다

#### DOE-09 · 제약식의 변수 토큰을 행 번호가 아닌 변수 이름으로 영속한다
- 종류: PR | 규모: M | 태그: A, C · bug
- 목표: 저장되는 "Constraint equation" 은 변수 이름(`displayName`, DOE Table headers 와 동일) 식이다. `v{n}` 은 입력 편의로 위젯이 커밋 시 현재 표의 Symbol→Name 으로 전개한다. 실행·Resample 의 인덱스 치환 3곳을 이름 기반으로 바꾼다.
- 완료 기준: 식 저장 후 DV 행 추가·삭제·Set 변경을 거쳐도 JSON 의 식이 같은 변수를 가리킴(`v{n}` 이 JSON 에 없음) · cases 빈 discrete 행이 있어도 치환 대상이 표와 일치 · `v1`/`v10` 접두 문제 소멸 · Resample 이 Init 제약을 그대로 적용
- 변경 범위: view/DashDoeSamplerWidget.cpp (constrainedFuncEdit 커밋 전개) · model/DashDoeSampler.cpp (runAnalysisInThread 2곳 · runSpaceFillingResample 1곳)
- 선행: -
- 충돌: DOE-07 (runAnalysisInThread) · DOE-13 · PR #652 · B2 교집합: DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashDoeSamplerWidget.cpp → DOE-05 DOE-06 DOE-11 UIC-20
- 흡수: DOE-D26 · DOE-c20 · LCH-c63(DOE-c59)
- 비고: 구 파일의 `v{n}` 식은 변환하지 않는다 — 열면 그대로 보이고 사용자가 재입력 (하위호환 분기 금지). OPT-D24 가 같은 기제 — OPT 접점

#### DOE-10 · Geometry/Condition JSON 판별을 DashDoeSelection 의 파일명 규칙으로 통일한다
- 종류: PR | 규모: S | 태그: E · refactor, bug
- 목표: `DashDesignVariableModel::parseJsonFile`·`saveToJsonFiles` 의 `contains("Geometry")`/`contains("Condition")` 을 `DashDoeSelection` 의 접두 규칙(`GeometryParameter_`/`ConditionParameter_`, `DashProject::restoreExistingModules` 의 표와 동일)으로 바꾸고, 어느 접두에도 맞지 않는 파일은 경고를 남기고 건너뛴다 (조용한 `DV-Condition` 기본 제거 — CON-D8).
- 완료 기준: DOE 영역에 `contains("Geometry")`·`contains("Condition")` 0곳 · 접두 불일치 파일명으로 `loadFromJsons` 하면 변수 0건 + WARN 1줄 · 앱이 만든 파일명(`GeometryParameter_`/`ConditionParameter_`)만 있는 프로젝트에서 DV 적재·저장 결과 동일 · 접두→절 대응이 한 함수에만 있다 · 접두 규칙 단위 테스트 (tests/test_doe_selection.cpp 확장)
- 변경 범위: model/DashDesignVariableModel.h · model/DashDesignVariableModel.cpp · tests/test_doe_selection.cpp
- 선행: -
- 충돌: DOE-17 (`saveToJsonFiles` 헬퍼 이행 — 본 항목 먼저) · B2 교집합: test_doe_selection.cpp → DOE-12 DOE-16 PER-07
- 흡수: DOE-D6(DOE 잔존분) · DOE-c16 · CON-D8 · CON-c08 (CON-08 병합, B2)
- 비고: 태그에 `bug` 를 병기한 이유 — 조용한 `DV-Condition` 폴백(DashDesignVariableModel.cpp:294-300 · :437-442) 제거는 CON-D8 의 조용한 실패를 고치는 동작 변경이다. 손으로 고친 파일명이 있는 프로젝트는 변수 0건 + WARN 으로 달라지므로 "결과 동일" 조건을 앱 생성 파일명으로 한정했다. `model/DashDesignVariableModel` 소속은 B2 에서 DOE 로 확정(1-1 표). CON-08(같은 두 함수, 같은 기제)을 여기로 병합. CON·CAD 위젯이 각각 `mDesignVariableModel->setParent(this)` 로 공용 모델의 부모를 빼앗는 줄(CON-08 비고 · CON-c27)은 소유권 기제라 DOE-19 로 갈랐다. LCH 측 2곳은 이미 DashDoeSelection 사용(해소)

#### DOE-11 · DOE Sampler 의 호출부 없는 함수를 지운다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: 호출부 0 인 `DashDoeSampler::isDfsxmlWithMorphing`·`getPlottingData`(+`DashDoeConfigManager::getPlottingData`)·`getUserProjectFolderPath`·`DashDoeSamplerWidgetBase::getDvTablePath`·`DashDoeSamplerWidget::refreshJsonFiles` 를 삭제한다.
- 완료 기준: 위 심볼 부재 · 빌드·테스트 통과 · #652 머지 후 재집계에서 호출부 0 함수 추가분 없음
- 변경 범위: model/DashDoeSampler.cpp/.h · model/DashDoeConfigManager.cpp/.h · view/DashDoeSamplerWidgetBase.cpp/.h · view/DashDoeSamplerWidget.cpp/.h
- 선행: PR #652 머지 (writeCaseDat·JobRunner 제거 뒤 잔여 확정)
- 충돌: DOE-05 · DOE-07 · DOE-08 · DOE-12 · B2 교집합: DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashDoeSampler.h → LCH-14 · DashDoeSamplerWidget.cpp → DOE-06 DOE-09 DOE-13 UIC-20 · DashDoeConfigManager.cpp → DOE-16 DOE-17 · DashDoeSamplerWidgetBase.cpp → ANA-07 PRJ-25 · DashDoeConfigManager.h → DOE-16 · DashDoeSamplerWidgetBase.h → PRJ-25
- 흡수: DOE-U4(DOE 측) · DOE-c21
- 비고: 파일 8개지만 삭제만 — 반나절

#### DOE-12 · `extractDfsxmlMorphingInfo` 를 DashDoeSampler 인스턴스 없이 쓰는 자유 함수로 옮긴다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: `DashJobRunnerAnsysMotion.cpp` 가 헬퍼 하나를 위해 `DashDoeSampler`(#652 뒤에는 DV 모델 생성)를 임시 생성하는 역의존을 끊는다 — `DashDoeSelection` 이 이미 가진 `Morphing|{deck}|{part}` 파서 `morphingPartName`(part 만 반환, .cpp:378-395)을 `{deck, part}` 반환으로 확장해 그것을 쓰고, `DfsxmlMorphingInfo` 를 따라 옮긴다 (경로 해석은 호출부가 IOController 로). 같은 라벨 파서를 둘로 늘리지 않는다.
- 완료 기준: `DashDoeSampler::extractDfsxmlMorphingInfo`·`DfsxmlMorphingInfo` 부재 · `Morphing|` 파싱이 `DashDoeSelection` 한 함수에만 있다 · `DashJobRunnerAnsysMotion.cpp` 에 `DashDoeSampler` 포함·생성 0 · 파싱 단위 테스트
- 변경 범위: model/DashDoeSampler.cpp/.h · model/DashDoeSelection.cpp/.h · model/DashJobRunnerAnsysMotion.cpp · tests/test_doe_selection.cpp
- 선행: -
- 충돌: PR #652 (DashDoeSampler.cpp/.h · DashJobRunnerAnsysMotion.cpp) · PER-07 (DashDoeSelection.cpp/.h) · DOE-11 · B2 교집합: DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절) · DashDoeSampler.h → DOE-05 DOE-07 DOE-08 LCH-14 · DashDoeSelection.cpp → DOE-16 PER-02 · test_doe_selection.cpp → DOE-10 DOE-16 · DashDoeSelection.h → DOE-16
- 흡수: DOE-c25

#### DOE-13 · Probabilistic 체크박스 쌍 연동 람다 4벌을 하나로 합친다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `updateTableForSamplingMode` 의 Min↔Max·Mean↔Std 연동 람다 4개(같은 경고 문구 4회, ~130줄)를 쌍 인자를 받는 헬퍼 1개로 바꾼다. 동작 불변.
- 완료 기준: 쌍 해제 연동·전부 해제 시 경고 후 되돌림 동작 동일 · 경고 문구 1곳 · 함수 길이 감소
- 변경 범위: view/DashDoeSamplerWidget.cpp
- 선행: -
- 충돌: DOE-06 · DOE-09 (같은 파일) · B2 교집합: DashDoeSamplerWidget.cpp → DOE-05 DOE-11 UIC-20
- 흡수: DOE-c29

#### DOE-14 · DOE Table 의 `samples[]` / `rawSamples[]` 중 정본을 정한다
- 종류: DEC | 규모: S | 태그: C, A
- 목표: 두 형태는 주소 방식만 다른 게 아니라 **내용**이 다르다 — `samples[].values` 는 매핑값(discrete 인덱스→case 문자열, categorical 인덱스→범주; DashDoeConfigManager.cpp:180-230), `rawSamples` 는 샘플러 원시 출력(`cachedSamples` — 인덱스 그대로 + `key`·`partName`). 결정 대상 1순위는 "mapped vs raw 의미 차이와 역매핑 가능성(`columns`·DV cases 로 되돌릴 수 있나)" 이고, 그 다음이 정본 선택이다.
- 완료 기준: 결정 기록 — 정본 1개와 역매핑 규정, 다른 쪽의 쓰기 중단 시점, 소비자별 전환 항목(LCH·PRE·ANA)과 순서, Journal 합성 Table 처분(LCH), 구 파일 읽기 규칙(재기록 없음)
- 변경 범위: - (결정)
- 선행: -
- 충돌: -
- 흡수: DOE-D5 · DOE-c15 · LCH-c61(DOE-c57 — LCH 소비 3곳 접점)
- 비고: 소비자 — 작성자 3 (`DashDoeConfigManager::saveResultsAsDvTable:294`·`saveResampledSamples:391` · `DashJobRunnerAnsysJournal.cpp:729` 가 1샘플 Table 을 `rawSamples` 만으로 합성) · rawSamples 독자 2 (`DashAnalysisLaunchExecutor.cpp:195` "raw (un-mapped) values" 주석 · `DashJobRunnerAnsysJournal.cpp:113`) · samples 독자 8 (`DashMorphingDoeExecutor.cpp:128` · `DashJobRunner.cpp:358` 메모리 내 active 병합 · `DashAnalysisLaunchExecutor.cpp:123`·`:176` · `DashLauncherRuns.cpp:31`·`:130` · `DashDoeCasesWidget.cpp:167` · `DashDataLoader.cpp:65`·`:127` · `DashResultsAnalyzerWidget.cpp:930`) · 스냅샷(`kSnapshotKeys`)은 둘 다 운반. 양안 — (a) raw 1벌 + 읽기 시 매핑 (b) mapped 1벌 + 역매핑. 종전 제안("samples 정본 + rawSamples 쓰기 중단")은 역매핑 규정 없이는 손실이라 (b) 의 전제 조건으로 내렸다. Code-Map D5 의 "`.wbpj` 만 후자" 는 낡음. 포맷 변경이라 PER 접점

#### DOE-15 · #649 를 추적 부모로 닫는다
- 종류: CLOSE | 규모: - | 태그: E
- 목표: 실작업 없는 후속 추적 부모.
- 완료 기준: 닫기 사유 — 서브이슈 8건이 모듈 항목으로 흡수됨: #615 → PRJ-33(DOE-01 이관)·DOE-02·03 / #604 #616 #639 #646 → LCH / #643 → PRE / #645 #650 → PRJ
- 변경 범위: -
- 선행: 서브이슈 전부의 항목화 (Phase B 확인)
- 충돌: -
- 흡수: #649 · DOE-c09

#### DOE-16 · DOE Table에 실제 입력 출처를 기록하고 Launcher 스냅샷으로 전파한다
- 종류: PR | 규모: M | 태그: C, A · feature
- 목표: #368 공통 계약으로 생성 DOE Set의 setId, 실제 Geometry·Condition Set의 setId, 선택 정보와 deck 출처를 DOE Table에 기록한다. 현재 DOE Set의 ID를 유지하면서 기존 UI에서 상류 참조를 바꿀 수 있다. Resample은 실제 사용한 참조 Table 출처를 읽어 기록하고 `kSnapshotKeys`가 필요한 출처 필드를 스냅샷으로 운반한다.
- 완료 기준: ① Init·Resample에 실제 사용한 개별 Set·선택·deck 출처 기록 ② 입력 선택 변경만으로 기존 Table 출처 불변 ③ 재샘플링 결과 덮어쓰기 시 출처도 갱신 ④ 필수 출처 누락 Table을 이름·경로로 추론하지 않고 재생성 안내 ⑤ test_doe_selection의 기록·판독과 TestAnalysisLauncherConfig의 스냅샷 전달 검증. 기존 Set ID 발급·복원 유지.
- 변경 범위: model/DashDoeSelection.cpp/.h · model/DashDoeConfigManager.cpp/.h · model/DashDoeSampler.cpp · model/preprocessor/DashAnalysisLauncherConfig.cpp (kSnapshotKeys 출처 필드) · tests/test_doe_selection.cpp · tests/TestAnalysisLauncherConfig.cpp
- 선행: PER-07
- 충돌: DOE-03 · DOE-07 (`saveResultsAsDvTable` 서명) · DOE-17 (같은 함수) · LCH-16 · PRE-14 · PRE-15 · PRE-27 · PRE-32 (출처 판독 소비자 — 순서는 DOE-16 먼저) · B2 교집합: DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashDoeConfigManager.cpp → DOE-11 · DashDoeSelection.cpp → DOE-12 PER-02 · test_doe_selection.cpp → DOE-10 DOE-12 · DashDoeConfigManager.h → DOE-11 · DashDoeSelection.h → DOE-12 · PR #652(DashDoeSampler.cpp) · PR #651(DashAnalysisLauncherConfig.cpp·TestAnalysisLauncherConfig.cpp)
- 흡수: #368 Phase 1(T27 DOE 홉) · PM4 T27 · DOE-c31 · LCH-c35(DOE-c52) · DOE-c64 · PER-06 ①(`kSnapshotKeys` allowlist — C-2 결정 ⑤ 로 DOE 귀속)
- 비고: 조합 ID를 생성·복사하지 않는다. 런처 스냅샷 전달은 DOE-16, 소비·결과 XML 기록은 PRE-32. #615의 Resample 번호·자동 선택 규칙은 추가 개정 계획으로 남으며 이번 출처 계약만으로 확정하지 않는다. 테스트는 Qt Core로 분리 가능한 공통부·설정 왕복을 사용한다.

#### DOE-17 · DOE Sampler 의 JSON 쓰기 4곳을 공용 파일 헬퍼로 이행한다
- 종류: PR | 규모: S | 태그: A · refactor
- 목표: `DashDoeConfigManager::saveResultsAsDvTable`·`saveResampledSamples`(QFile Truncate + QTextStream, 쓴 길이 미검사)와 `DashDoeSampler::saveSettings`(RMW, `open` 반환 무검사)의 직쓰기를 PER-02 의 `DashSaveSystem` 헬퍼(공용 진입점 — `writeJsonFile`, QSaveFile 원자 쓰기 + `Result` 사유)로, 선행 읽기 3곳을 `readJsonFile` 로 바꾼다. 동작 불변.
- 완료 기준: (1) model/DashDoeConfigManager.cpp · model/DashDoeSampler.cpp 의 JSON 쓰기에 `QFile` 0 (2) 쓰기 실패가 로그와 반환값으로 드러난다 (3) 수동 확인 — Set 저장 → 재진입 → 재저장 뒤 `DoeSampler_<Set>.json` 바이트 동일
- 변경 범위: model/DashDoeConfigManager.cpp · model/DashDoeSampler.cpp · model/DashDesignVariableModel.cpp (`saveToJsonFiles` — 소속 DOE 확정분)
- 선행: PER-02 (헬퍼) · DOE-10 (`saveToJsonFiles` 절 판정 변경을 먼저)
- 충돌: DOE-05 (`saveSettings`·`loadSettings`) · DOE-07 (`saveResultsAsDvTable`) · DOE-16 · DOE-10 (`saveToJsonFiles`) · PR #652 (DashDoeSampler.cpp) · B2 교집합: DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashDoeConfigManager.cpp → DOE-11
- 흡수: #479(DOE 몫) · #478(DOE 몫) · #480(DOE 몫 — 버전 키는 헬퍼 경유로 자동, PER-04) · PER-c25(DOE-c61) · PER-c22(`DashDesignVariableModel::saveToJsonFiles` 몫 — B2 소속 결정, MOR-22 비고 참조)
- 비고: (3) 을 자동 테스트로 두지 않은 근거 — 쓰기 경로가 `DashDoeConfigManager`·`DashDoeSampler` 본체이고 둘 다 `DashProjectManager` 싱글턴에 의존해 Qt Core only 인 tests/ 에 링크되지 않는다(model/DashDoeConfigManager.cpp:5-6 · DashDoeSampler.cpp:711-724 · tests/CMakeLists.txt:46-57). 헬퍼 치환은 본체를 쪼갤 사유가 아니므로 PER-05 픽스처 대신 수동 확인으로 낮춘다. `선행: PER-05` 는 제거 — 게이트는 선행이 아니다(PER 검토 #9). 읽기 측 사본 2곳(`DashDoeSampler.cpp:28-40` 익명 `loadJsonRoot` — Resample 경로 입구 · `DashDoeConfigManager::loadSettings:59`)도 같이 이행한다 — PER-c03 ⑦⑧ 에 그 2곳이 올라 있고(2차 확인) 치환 몫은 본 항목이다. `saveToJsonFiles` 는 DV JSON 2종(Geometry·Condition)을 전체 재기록 — 헬퍼 치환만, 절 판정은 DOE-10. DOE Table 전체 재기록 2곳은 유지 — 기존 tableId는 실행 스냅샷 식별로 유지하고 출처 계약은 PER-06·PER-07을 따른다. `saveDoeToCsv` 는 JSON 이 아니라 대상 밖

#### DOE-18 · `Selected Design Variables` 를 SI-4(setId + name 병기) 로 통일할지 정한다
- 종류: DEC | 규모: S | 태그: C
- 목표: `DashDoeSelection::writeSelectedSets` 는 `{set: 이름}` 만 쓰고, 같은 파일의 `parameterization`(T20)·`columns` 는 setId + `name` 병기(SI-4)다. 발화 조건 중 Set rename 은 Geometry 고정명·Condition 참조파일명 고정으로 소멸했으나 **동명 재생성**(Condition Set 삭제 후 같은 reference file 로 재생성 = 같은 이름·새 setId)은 남아 있다 — PM4 T29 가 이를 검증 항목으로 명시한다. (a) 현행 유지 — `Selected Design Variables` 는 편집 상태(선택)라 동명 재생성 뒤 새 Set 을 가리키는 것이 의도이고, 동결 기록은 `parameterization`·`columns` 가 setId 로 든다 (b) SI-4 통일 — `writeSelectedSets`/`readSelectedSets` 한 쌍 수정, 구 기록은 round-trip(재기록 없음) 중 택한다.
- 완료 기준: 결정 기록 — (b) 면 후속 S PR 범위 (model/DashDoeSelection.cpp · tests/test_doe_selection.cpp; 소비 5곳은 `readSelectedSets` 경유라 무변경)
- 변경 범위: (결정만)
- 선행: -
- 충돌: PER-07 (DashDoeSelection) · DOE-16
- 흡수: #562-3 · #443 SI-4(DOE 몫) · PRJ-c09(DOE-c60)
- 비고: PRJ 가 "통일 여부는 DOE 결정" 으로 넘김. 판단 재료 — 발화 조건은 rename 소멸 뒤에도 동명 재생성이 남는다(Project-Manifest-4-Ticket-Slicing.md:222 · DashDoeSelection.cpp:122-135 · DashProject.cpp:463). (a) 의 "선택은 편집 상태" 논거가 서면 DEC 가 닫히고 최소 변경이 된다

#### DOE-19 · 공용 `DashDesignVariableModel` 의 소유자를 DashManager 로 못박고 소비자의 `setParent` 탈취를 없앤다
- 종류: PR | 규모: S | 태그: E · bug
- 목표: `DashManager` 가 부모 없이 만드는 공용 DV 모델(`DashManager.cpp:81`)에 소유자를 준다 — `new DashDesignVariableModel(this)`. 그 모델을 받아 쓰는 CON·CAD 위젯이 `setParent(this)` 로 소유권을 가져가는 2줄(`DashConditionParameterizationWidget.cpp:331` · `DashGeometryParameterCADWidget.cpp:310`)을 지운다. 먼저 파괴되는 위젯이 공용 인스턴스를 지워 남은 소비자와 `GetDesignVariableModel()` 이 대상 잃은 포인터를 드는 상태가 사라진다.
- 완료 기준: 공용 DV 모델 생성에 부모 있음 · 코드베이스에 `mDesignVariableModel->setParent` 0곳 · CON 위젯을 닫은 뒤 CAD 위젯에서 DV 적재·저장 정상 (수동) · 앱 종료 시 모델 파괴 1회
- 변경 범위: controller/DashManager.cpp · view/DashConditionParameterizationWidget.cpp · view/DashGeometryParameterCADWidget.cpp
- 선행: -
- 충돌: CON-03 · CON-05 · CON-06 · CON-07 · CON-12 · CAD-01 · CAD-03 · CAD-04 · CAD-05 · CAD-06 · CAD-07 · CAD-09 · CAD-13 · UIC-19 · PRJ-03 · PRJ-04 · PRJ-06 · PRJ-14 · EXE-06 · REN-07 · PR #652 · PR #654 (controller/DashManager.cpp — 둘 다 DV 모델 줄도 dtor 도 건드리지 않아 순서 무관) · B2 교집합: DashConditionParameterizationWidget.cpp → UIC-20
- 흡수: CON-c27 · Code-Map CON 3-1 · DOE-c66
- 비고: 소유자를 `DashManager` 로 둔 근거 — 모델은 ctor 에서 1회 생성되고 CON·CAD 두 위젯이 같은 인스턴스를 공유한다(`GetDesignVariableModel` 소비 6곳). 위젯 쪽으로 소유를 몰면 다른 위젯이 수명을 잃으므로 공유 소유자가 쥐는 쪽만 성립한다. dtor(`:103-123`)는 데몬 4종만 만지므로 부모를 주면 QObject 가 지운다. MOR(`DashGeometryParameterWidget.cpp:105`)·DOE(`DashDoeSampler.cpp:142`)는 각자 부모를 둔 별 인스턴스라 무관. DOE 귀속 근거 — `DashDesignVariableModel` 소속이 B2 에서 DOE(1-1 표). JSON 접두 판정(DOE-10)과는 다른 개념이라 나눴다. CON·CAD 접점

#### DOE-20 · Resample 의 Search Min/Max 셀에 숫자·범위 검증을 둔다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: `mResampleDvTable` 의 Search Min(4열)·Max(5열) 을 아이템 델리게이트(선례 `view/delegate/DashFeConditionValueDelegate.cpp:102-109` — `QDoubleValidator`)로 받아 비수치 입력을 편집 중에 막고, 참조 Set 의 설계 공간(`getDesignSpaceRange`) 밖 값과 min ≥ max 를 커밋 때 되돌리며 허용 범위를 셀 툴팁으로 보인다. 지금은 `toDouble` 실패·역전 쌍이 조용히 ROI override 에서 빠져 전 설계 공간으로 되돌아간다(`onResampleRunClicked:298-309` 의 `if (okMin && okMax)`).
- 완료 기준: 비수치 입력이 셀에 커밋되지 않는다 · min ≥ max 또는 설계 공간 밖 값은 되돌려지고 사유 통지 1회 · 셀 툴팁에 참조 Set 의 `[min, max]` 표시 · prefill 과 override 전달 동작 불변 (파싱 가드 `okMin && okMax` 는 남긴다)
- 변경 범위: view/delegate/DashDoeSearchRangeDelegate.h · view/delegate/DashDoeSearchRangeDelegate.cpp (신규) · view/DashDoeSamplerResampleWidget.cpp
- 선행: -
- 충돌: DOE-02 (같은 파일 — 콤보·prefill 인접) · B2 교집합: DashDoeSamplerResampleWidget.cpp → UIC-20
- 흡수: #487(표 셀 DOE 2곳) · UIC-c41(b) · DOE-c65
- 비고: UIC-21 의 `applyNumericRange(QLineEdit*, …)` 는 쓸 수 없다 — 표 셀은 `QTableWidgetItem::text()` 파싱이라 델리게이트가 필요한 다른 기제다(UIC 검토 #10 이 `범위밖` 으로 갈라 DOE 로 넘김). 델리게이트를 공용(`view/common`)으로 빼지 않은 이유 — 지금 사용처가 이 표 하나고, 같은 기제의 OPT 몫 1곳이 자기 항목으로 서면 그때 UIC 로 올린다(단일 사용처 추상화 금지). 허용 범위의 출처는 prefill 과 같은 `getDesignSpaceRange`(참조 Table 의 min/max, `populateDvTableFromReferenceSet:226-241`) 라 셀 UserRole 에 실어 전달한다

### LCH — Analysis Launcher — Launcher·배치·Direct

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> 기준 dev @ b08a91b3. 열린 PR 7건 중 **머지 대상 6건**(#651 #652 #654 #655 #656 #658) — #530 은 재업로드 노선이라 머지 대상이 아니다 (C-2 ② · ⑩).
> LCH 파일을 건드리는 PR — **#651(#616) · #652(#604)**: `model/DashJobRunner.h/.cpp` · `DashJobRunnerAnsysMotion.cpp` · `DashJobRunnerAnsysJournal.cpp` · `DashJobRunnerFeSafe.cpp` · `model/DashAnalysisLauncher.*` · `view/DashAnalysisLauncherWidget*` 를 고치므로 그 파일을 만지는 항목은 두 PR 머지를 선행으로 둔다 · **#654 · #655**: `controller/DashDoeBatchChain.*`(+#654 `controller/DashMorphingDoeExecutor.cpp` — LCH-13 충돌에 기재) · **#656 · #658**: `model/DashAnalysisLauncher.cpp`(·`.h`).
> **#656 · #658 은 선행이 아니다** — 두 PR 의 `DashAnalysisLauncher.cpp` hunk 가 전부 PRE 결과 경로다(#656 = `loadResultKeys`·`previewNaturalFrequency`·`requestVtkGeometry` 의 TimeSteps 파싱·질의 직렬화·모달 Name 공용화 / #658 = `requestVtkPreview` 의 `sub_result`·`previewNaturalFrequency` 의 eigenvalue). LCH 겹침 항목은 LCH-15(`preprocessInputsChanged`·`connectLaunchExecutor`) 1건뿐이고 작업 자리가 겹치지 않으므로 단순 동시 수술 — 충돌란 기입은 D-1 의 `build_deps.py --apply` 가 파일 교집합으로 자동 처리한다.
> 종결 계약 (전 항목 공통 전제): `emitEnqueued` 이후 활성 키 전부가 `caseStatusUpdated(key, Done|Failed*|Cancelled)` 에 이르러야 `DashAnalysisLaunchExecutor` 의 런 추적이 끝나고 Start 가 풀린다.
> C' 2차 반영(2026-10-06)의 카드 신설 이력은 유지한다. LCH-33은 현재 출처 검증 계약으로 개정했고 LCH-34는 기록 실패 안내를 담당한다. LCH-29의 PRJ 원장 조항은 그대로다.

#### LCH-01 · Target Part 를 읽는 동안 Start 를 막고, 로드 실패 시 저장된 target 을 보존한다
- 종류: PR | 규모: S | 태그: D, A · bug
- 목표: `fillTargetPartCombo` 가 `co_await` 하는 동안 Start 버튼을 비활성으로 두고, 로드가 끝난 뒤에만 Start 와 콤보를 되살린다. RW 로드 실패(`!loaded`)면 `setTargetComponent` 를 호출하지 않는다.
- 완료 기준: (1) 탭 진입 직후 Start 가 비활성이고 콤보가 채워진 뒤 활성 (2) 로드 실패 상태로 탭 진입 뒤 `AnalysisLauncher_<Set>.json` 의 `target_component` 가 이전 값 그대로 (3) 정상 로드 시 저장값이 콤보에 선택된다
- 변경 범위: `view/DashAnalysisLauncherWidgetLauncher.cpp` (`updateLauncherTabFromModel` · `fillTargetPartCombo` · `setLauncherIdle`), `view/DashAnalysisLauncherWidget.h`
- 선행: PR #651·#652 머지 (같은 파일)
- 충돌: LCH-17 (같은 파일 Start 람다) · B2 교집합: DashAnalysisLauncherWidgetLauncher.cpp → LCH-08 LCH-10 LCH-15 LCH-16 LCH-28 LCH-29 LCH-33 · DashAnalysisLauncherWidget.h → PRE-05 PRE-23
- 흡수: #639 · LCH-c30, LCH-c31
- 비고: `setLauncherIdle` 에 "콤보 채우는 중" 조건을 더하는 것으로 충분. 세대 검사(`m_targetPartsGeneration`)는 이미 있다

#### LCH-02 · Enqueued 이후 종결 상태 없이 빠져나가는 경로를 전부 종결 상태로 닫는다
- 종류: PR | 규모: M | 태그: B · bug
- 목표: (a) `runDoeJobs` 의 `!prep.ansysReady` 와 Motion 의 소스 dat 추출 실패·부재는 `emitEnqueued` 이전 사전 검증으로 옮겨 `jobFailed` 로 끝낸다 — 사전 검증은 `.dat` 템플릿만 대상으로 하고, `prepareMorphingBatch:638-648` 이 `!ctx.isInp` 로 dfsxml 에도 걸던 MAPDL 초기화는 함께 제거한다(269-1 후속 "dfsxml 의 불필요한 MAPDL 초기화") (b) 모핑 뒤 프로젝트 닫힘·`ioCtrl` 없음(`resumeAfterMorph` false)은 활성 키 전부 "Cancelled" 방출 (c) 치환 폴백의 `!ansysReady continue`·템플릿 읽기 실패, Abaqus 배치 진입 실패 2곳은 `failActiveCases` 로 (d) JSON 에만 쓰고 시그널을 안 내는 **18곳**을 닫는다 — Failed 16곳은 `writeCaseStatus` 를 `emit caseStatusUpdated` 로 **치환**(기록은 executor `onCaseStatusUpdated:243` 이 하므로 이중 기록 0), Motion `:652` Done(`.dfr` resultFiles)·Mechanical Running 2곳(`submitMorphedAnsysMechanicalJobs:358` · `runTemplateFallback:480`)은 emit 을 추가하고 러너 기록은 LCH-07 이 걷는다.
- 완료 기준: (1) 4 경로(#580)를 강제 유발하면 Start 가 풀리고 표에 Failed/Cancelled 또는 `analysisFailed` (2) `runDoeJobs`·`runAnsysMotionMorphingDoe`·`runTemplateFallback`·`submitMorphed*` 에 Enqueued 이후 상태 없는 `co_return`/`return`/`continue` 가 0 (3) 러너의 `writeCaseStatus(..., "Running"|"Failed"|"Done")` 호출마다 같은 키의 `caseStatusUpdated` 가 함께 있다 — grep 으로 확인 (4) MAPDL 미설정 환경에서 dfsxml 배치가 종전처럼 실행된다 (5) 정상 DOE 5경로 회귀 없음
- 변경 범위: `model/DashJobRunner.cpp` (`runDoeJobs` · `prepareMorphingBatch` · `resumeAfterMorph`), `model/DashJobRunnerAnsysMotion.cpp` (`runAnsysMotionMorphingDoe` · `startNextMotionLauncher`), `model/DashJobRunnerAnsysMechanical.cpp` (`submitMorphedAnsysMechanicalJobs` · `runTemplateFallback`), `model/DashJobRunnerAbaqus.cpp` (`submitMorphedAbaqusJobs`), `model/DashJobRunner.h`
- 선행: PR #651 머지 (`failActiveCases` 재사용), PR #652 머지
- 충돌: LCH-03 · LCH-04 · LCH-07 · LCH-13 (같은 TU) · B2 교집합: DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절) · DashJobRunner.cpp → LCH-14 PRJ-09 UIC-20 · DashJobRunner.h → CAD-01 LCH-06 LCH-10 LCH-12 LCH-14 · DashJobRunnerAbaqus.cpp → UIC-19 · DashJobRunnerAnsysMechanical.cpp → UIC-19
- 흡수: #580 · 269-1 "시그널이 빠진 실패 — 후속" · 269-1 후속 "dfsxml 의 불필요한 MAPDL 초기화" · LCH-c02, LCH-c03, LCH-c04, LCH-c05, LCH-c07
- 비고: (a)·(c) 가 동작 변경 — (a) `.dat` 템플릿도 MAPDL 미설정을 모핑 전에 거부하고(dfsxml 은 MAPDL 과 무관해 제외), (c) 는 `runTemplateFallback` 의 "입력 파일만 생성" 모드(WARN `:385-386`)를 폐지해 미설정이면 `.dat` 도 Failed 가 된다. 둘 다 PR 본문에 명시

#### LCH-03 · 취소가 motion-launcher 대기 큐까지 비우게 한다
- 종류: PR | 규모: S | 태그: B · bug
- 목표: `cancelAllRuns` 가 `m_motionLauncherQueue` 를 비우고 대기 중이던 키마다 "Cancelled" 를 방출한다. `startNextMotionLauncher` 는 취소 뒤 큐잉된 호출에서 아무것도 시작하지 않는다.
- 완료 기준: (1) dfsxml 케이스 3개 이상 실행 중 Stop → 진행 1건 Cancelled, 대기분 전부 Cancelled, 다음 프로세스가 뜨지 않는다 (2) Start 버튼이 풀린다
- 변경 범위: `model/DashJobRunner.cpp` (`cancelAllRuns`), `model/DashJobRunnerAnsysMotion.cpp` (`startNextMotionLauncher`)
- 선행: PR #651 머지 (`DashJobRunner.cpp`) · PR #652 머지 (`DashJobRunnerAnsysMotion.cpp`)
- 충돌: LCH-02 · LCH-04 · LCH-05 · LCH-10 · LCH-12 · B2 교집합: DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절) · DashJobRunner.cpp → LCH-07 LCH-13 LCH-14 PRJ-09 UIC-20
- 흡수: #439 · DOE-D23 · LCH-c09 · DOE-c50(LCH-c85) · EXE-c33(LCH-c90)
- 비고: Direct 큐(PR #652 러너)도 같은 큐를 쓰므로 Direct Stop 에도 적용된다

#### LCH-04 · motion-launcher 가 `.dfr` 을 위조하지 않고 Failed 로 끝낸다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: exit 0 인데 `{runKey}.dfr` 이 없으면 하드코딩 XML 생성·Done 대신 Failed 를 기록·방출한다.
- 완료 기준: (1) `.dfr` 부재 케이스가 Failed 로 표시되고 run 폴더에 생성된 `.dfr` 이 없다 (2) Preprocess 가 그 케이스를 읽지 않는다 (3) `runMotionLauncher` 에 `<DFRInfo>` 리터럴이 없다
- 변경 범위: `model/DashJobRunnerAnsysMotion.cpp` (`runMotionLauncher` finished 람다)
- 선행: PR #652 머지
- 충돌: LCH-03 · LCH-05 · LCH-10 · B2 교집합: DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절)
- 흡수: DOE-D15 · LCH-c39 · DOE-c44(LCH-c79)

#### LCH-05 · motion-launcher 완료 판정을 `finished` 람다 하나로 단일화한다
- 종류: PR | 규모: S | 태그: B · refactor
- 목표: `monitorMotionLauncherOutput` 은 stdout 을 로그로만 남기고 상태를 올리지 않는다. Done/Failed 판정은 `finished` 람다만 한다.
- 완료 기준: (1) `monitorMotionLauncherOutput` 에 `caseStatusUpdated`·`recordMotionDone` 호출이 없다 (2) 정상·실패 케이스에서 상태가 1회만 방출된다 (로그로 확인)
- 변경 범위: `model/DashJobRunnerAnsysMotion.cpp` (`monitorMotionLauncherOutput` · `runMotionLauncher`)
- 선행: LCH-04
- 충돌: LCH-03 · LCH-10 · LCH-12 · B2 교집합: DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절) · PR #652(DashJobRunnerAnsysMotion.cpp)
- 흡수: DOE-D16 · LCH-c40 · DOE-c45(LCH-c80) · EXE-c42(DOE-D16 몫, LCH-c96)
- 비고: LCH-10 이 motion-launcher 호출을 MBD 단일 호출로 바꾸면 이 함수가 사라질 수 있다 — 그때는 LCH-10 에 흡수

#### LCH-06 · 배치 종결을 키 집계 한 갈래로 통일하고 `jobFinished` 를 없앤다
- 종류: PR | 규모: S | 태그: B · refactor
- 목표: `DashJobRunner::jobFinished` 시그널과 그 방출 2곳(wbpj DOE·Direct wbpj), executor 의 `jobFinished → analysisFinished` 직결을 제거한다. `launchAnsysJournal` 의 `jobFailed` 는 활성 키 전부 Failed 를 이미 방출하므로 함께 제거한다.
- 완료 기준: (1) wbpj DOE 완료 시 `analysisFinished` 가 1회 (2) Journal 실패 시 `analysisFailed` 가 `analysisFinished` 뒤에 따라오지 않는다 (3) `jobFinished` 심볼 0건
- 변경 범위: `model/DashJobRunner.h`, `model/DashJobRunnerAnsysJournal.cpp` (`onAnsysJournalCompleted` · `launchAnsysJournal` · `launchAnsysJournalDirect`), `model/DashAnalysisLaunchExecutor.cpp`
- 선행: LCH-29 (`jobFinished` 방출 2곳이 전부 wbpj Journal 경로다) · PR #652 머지 (Direct 러너가 `jobStarted` 만 구독함을 diff 에서 확인 — 머지 뒤 소비자는 executor 뿐)
- 충돌: LCH-07 · B2 교집합: DashAnalysisLaunchExecutor.cpp → LCH-14 LCH-16 LCH-28 LCH-34 PRJ-09 UIC-20 · DashJobRunner.h → CAD-01 LCH-02 LCH-10 LCH-12 LCH-14 · DashJobRunnerAnsysJournal.cpp → CAD-01 LCH-14 LCH-27 UIC-19 · PR #651(DashJobRunner.h·DashJobRunnerAnsysJournal.cpp)
- 흡수: DOE-D21 · LCH-c41 · DOE-c49(LCH-c84) · EXE-c42(DOE-D21 몫, LCH-c96)
- 비고: LCH-29 가 wbpj 경로 **제거**로 결정되면 이 항목은 소멸 — `jobFinished` 시그널 자체가 Journal TU 삭제 PR 에 흡수된다. **동결**·**현행 유지**면 그대로 — `analysisFinished` 2회는 `setLauncherIdle(true)`·표 재구축 2회로 무해하므로 우선순위만 낮춘다

#### LCH-07 · 케이스 상태 기록을 executor 단일 라이터로 모은다
- 종류: PR | 규모: L | 태그: E, A · refactor
- 목표: 러너는 `caseStatusUpdated(key, status, analysisType, resultFiles)` 만 방출하고 `writeCaseStatus`·`recordMotionDone` 을 호출하지 않는다. `DashAnalysisLaunchExecutor::onCaseStatusUpdated` 가 유일하게 `DashAnalysisLauncherConfig::writeCaseStatus` 를 부른다(Direct 는 `launcherConfigPath` 가 비어 기록 없음 — 현행 유지).
- 완료 기준: (1) `model/DashJobRunner*.cpp` 에 `DashAnalysisLauncherConfig::writeCaseStatus` 호출 0 (2) 케이스 1건 Done 당 런처 JSON 기록 1회 (워처 `fileChanged` 1회) (3) Done 의 `resultFiles` 가 종전과 같이 기록된다 (Ansys `producedResultFiles` · Abaqus/fe-safe `<runKey>.odb` · Motion `<runKey>.dfr` · Journal 재귀 `.rst`)
- 변경 범위: `model/DashJobRunner.h/.cpp`, `model/DashJobRunnerAbaqus.cpp`, `model/DashJobRunnerAnsysMechanical.cpp`, `model/DashJobRunnerAnsysMotion.cpp`, `model/DashJobRunnerAnsysJournal.cpp`, `model/DashJobRunnerFeSafe.cpp`, `model/DashAnalysisLaunchExecutor.h/.cpp`
- 선행: LCH-02 (누락 방출을 먼저 채워야 기록을 걷어도 상태가 남는다), LCH-06, PR #651·#652 머지
- 충돌: LCH-03 · LCH-04 · LCH-05 · LCH-13 · LCH-14 · B2 교집합: DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절) · DashAnalysisLaunchExecutor.cpp → LCH-16 LCH-28 LCH-34 PRJ-09 UIC-20 · DashJobRunner.cpp → PRJ-09 UIC-20 · DashJobRunner.h → CAD-01 LCH-10 LCH-12 · DashJobRunnerAnsysJournal.cpp → CAD-01 LCH-27 LCH-29 UIC-19 · DashJobRunnerFeSafe.cpp → LCH-18 LCH-30 PRJ-14 UIC-19 · DashAnalysisLaunchExecutor.h → LCH-16 LCH-34 · DashJobRunnerAbaqus.cpp → UIC-19 · DashJobRunnerAnsysMechanical.cpp → UIC-19
- 흡수: DOE-D10 · LCH-c42 · LCH-c11(이중 기록분) · DOE-c39(LCH-c74)
- 비고: L 사유 — 한 클래스의 TU 6개가 같은 시그널 계약을 공유해 경로별로 가르면 중간 상태에서 기록이 두 벌/한 벌 섞인다. 시그널에 `resultFiles` 인자를 더하는 것이 핵심 설계 결정

#### LCH-08 · 실행 중에는 케이스 표를 워처로 재구축하지 않는다
- 종류: PR | 규모: S | 태그: B · perf
- 목표: `DashDoeCasesWidget` 이 실행 중(`analysisStarted` ~ `analysisFinished/Failed`)에는 `fileChanged` 를 무시하고 시그널(`updateCaseStatus`·`updateCaseLog`)로만 셀을 갱신한다. 종료 시 1회 `updateFromDvTable` (현행 `analysisFinished` 연결 유지).
- 완료 기준: (1) N 케이스 실행 동안 `updateFromDvTable` 호출이 0, 종료 뒤 1 (2) 실행 중 체크박스·Log 열이 유지되고 Mechanical·Abaqus·fe-safe·Motion 케이스의 Running 전이가 실행 중 표에 보인다 (3) 실행 밖에서 JSON 을 바꾸면 종전처럼 재구축된다
- 변경 범위: `view/DashDoeCasesWidget.cpp/.h` (`setRunning(bool)` 또는 동등), `view/DashAnalysisLauncherWidgetLauncher.cpp` (`connectLaunchExecutor`)
- 선행: LCH-02 (Mechanical DOE 는 Running 을 어디서도 방출하지 않아 지금은 워처 재구축으로만 보인다 — 재구축을 끄면 Done 까지 Enqueued 로 남는다), PR #651·#652 머지
- 충돌: LCH-01 · LCH-14 · LCH-17 (같은 파일) · B2 교집합: DashAnalysisLauncherWidgetLauncher.cpp → LCH-10 LCH-15 LCH-16 LCH-28 LCH-29 LCH-33 · DashDoeCasesWidget.cpp → LCH-09 LCH-34 · DashDoeCasesWidget.h → LCH-34
- 흡수: #441-a · DOE-D7 · LCH-c11 · DOE-c36(LCH-c71) · EXE-c43(DOE-D7 몫, LCH-c93)
- 비고: #441 증분 화면 갱신의 개선안이며 파일 저장·읽기 비용까지 해결됐다고 간주하지 않는다. #444 저장 경계는 LCH-32에서 비용을 확인해 필요한 경우에만 분리한다. 두 작업은 공유 적용 지점을 조율한다.

#### LCH-09 · 앱 재시작 뒤 "Running" 으로 남은 케이스의 처리 정책을 정한다
- 종류: DEC | 규모: S | 태그: B, A
- 목표: 재시작 후 런처 JSON 에 Running 이 남은 케이스를 (a) 자동 재개 (b) "Interrupted" 로 표시하고 Start 시 재실행 (c) 현행(표시만 Running, Start 가 Done 아닌 것을 재실행) 중 무엇으로 할지 결정한다.
- 완료 기준: 결정 기록 — 선택지·근거·후속 PR 범위. (b) 면 `DashDoeCasesWidget::updateFromDvTable` 의 표시 규칙 + 로드 시 상태 치환 지점(`DashAnalysisLauncher::refreshLaunchTarget` 또는 `DashLauncherRuns`) 명시
- 변경 범위: (결정만) 후속 후보 `view/DashDoeCasesWidget.cpp`, `model/preprocessor/DashLauncherRuns.cpp`
- 선행: LCH-32 (저장 경계·상태 기록 개선 확인)
- 충돌: B2 교집합: DashDoeCasesWidget.cpp → LCH-08 LCH-14 LCH-34 · DashLauncherRuns.cpp → PRE-32
- 흡수: #441-b · LCH-c12
- 비고: 자동 재개는 외부 프로세스 재부착 제약을 확인해야 하며 (b)가 최소 변경 후보다. #444 저장 경계 개선 후 그 기록을 사용하는 #441 복구를 적용한다.

#### LCH-10 · dfsxml 실행의 모델 종속 규칙을 GUI 에서 걷어 MBD 단일 호출로 줄인다
- 종류: PR | 규모: M | 태그: E, B · feature
- 목표: Target Part "CBLOCK" 고정·density 7816.9·`--unit m -b 19`·VTU 대기 → motion-writer → motion-launcher 2단 큐를 GUI 에서 제거하고, run 마다 DashOptiMBD 를 한 번 호출해 템플릿 경로·VTU 경로·DOE 값·출력 폴더만 넘긴다. Target Part 는 MBD 가 템플릿에서 읽거나 Set json 에서 받는다.
- 완료 기준: (1) `CBLOCK`·`7816.9` 리터럴 0건 (2) run 폴더에 `.dfsxml`·`.dfmm`·`.dfg` 가 생기고 Done 기록의 `resultFiles` 는 `.dfr` (3) LGE 예제 외 dfsxml 모델 1건으로 실행 성공
- 변경 범위: `model/DashJobRunnerAnsysMotion.cpp` (`runAnsysMotionMorphingDoe` · `runMotionWriter` · `runMotionLauncher` — 서브커맨드 리터럴 `:136`·`:220` 을 기존 `DashExt::Cmd::MBD_*` 상수 사용으로 치환), `model/DashJobRunner.h`, `view/DashAnalysisLauncherWidgetLauncher.cpp` (`fillTargetPartCombo` dfsxml 분기), `controller/DashExtensionProcess.h` (`:58-59` 상수 주석의 인자 규격 갱신 — 상수 자체는 이미 있다)
- 선행: LCH-31 (CLI·JSON 계약), LCH-11 (MBD 쪽이 먼저 받아야 한다), PR #651·#652 머지
- 충돌: LCH-03 · LCH-04 · LCH-05 · LCH-12 · LCH-13 · B2 교집합: DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절) · DashAnalysisLauncherWidgetLauncher.cpp → LCH-01 LCH-08 LCH-15 LCH-16 LCH-17 LCH-28 LCH-29 LCH-33 · DashJobRunner.h → CAD-01 LCH-02 LCH-06 LCH-07 LCH-14 · DashExtensionProcess.h → EXE-11 EXE-12
- 흡수: #647-a · #647-c · LCH-c26, LCH-c28
- 비고: GUI 가 넘기는 인터페이스(CLI 인자·JSON) 는 LCH-31 DEC 의 산출물이다 — 되돌리기 비용이 큰 결정이라 LCH-10·LCH-11 착수 전에 기록한다

#### LCH-11 · DashOptiMBD AnsysMotion 이 run 마다 dfsxml·dfmm·dfg 를 만들고 모델 종속 규칙을 수용한다
- 종류: EXT | 규모: M | 태그: B · feature
- 목표: DashOptiMBD 의 `motion-writer`/`motion-launcher` 를 하나의 진입점으로 묶어 템플릿 경로·VTU·DOE 값·출력 폴더를 받고, `.dfsxml`·`.dfmm`·`.dfg` 를 생성한 뒤 솔버를 돌린다. Target Part·밀도·단위 등 모델 종속 값은 Python 쪽 설정으로 옮긴다.
- 완료 기준: 외부 저장소 PR — LCH-31 이 정한 계약대로 구현 + LGE 예제와 다른 모델 1건의 실행 로그
- 변경 범위: DashOptiMBD (GUI 쪽은 추적만)
- 선행: LCH-31 (계약)
- 충돌: -
- 흡수: #647-b · #647-c · LCH-c27, LCH-c28

#### LCH-12 · dfsxml 경로의 동기 대기와 `processEvents` 14곳을 비동기로 바꾼다
- 종류: PR | 규모: M | 태그: B · refactor
- 목표: `waitForVtuFileComplete` 폴링(배치 `co_await` 뒤라 파일은 이미 써져 있다 — 존재 검사로 대체), `runMotionWriter` 의 `waitForFinished(500)` 루프, 샘플 루프의 `processEvents` 7곳을 제거한다. 외부 프로세스 대기는 `QProcess` 시그널 또는 `qCoro(process).waitForFinished()` 로.
- 완료 기준: (1) `model/DashJobRunner*.cpp` 에 `processEvents`·`msleep` 0건 (2) dfsxml 배치 실행 중 UI 가 응답하고 [Start] 재클릭이 거부된다 (3) 케이스 결과·상태가 종전과 같다
- 변경 범위: `model/DashJobRunnerAnsysMotion.cpp`, `model/DashJobRunner.h`
- 선행: LCH-10 (단일 호출로 줄어든 뒤 하면 대기 지점이 1곳이 된다), LCH-03
- 충돌: LCH-04 · LCH-05 · B2 교집합: DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절) · DashJobRunner.h → CAD-01 LCH-02 LCH-06 LCH-07 LCH-14 · PR #652(DashJobRunner.h·DashJobRunnerAnsysMotion.cpp) · PR #651(DashJobRunner.h)
- 흡수: DOE-D11 · LCH-c43 · #458-b(dfsxml 몫) · DOE-c40(LCH-c75) · RUN-c10(LCH-c87) · EXE-c46(LCH-c97) · EXE-c39(`msleep(100)` 3곳, LCH-c91) · EXE-c43(DOE-D11 몫, LCH-c93)
- 비고: LCH-10 을 먼저 하면 `waitForVtuFileComplete`·`runMotionWriter` 가 사라져 이 항목은 프로세스 1개의 비동기 대기로 줄어든다. 순서를 바꾸면 M→L. #458-b 의 "dfsxml 1·2단계 ProcessJob 수렴" 은 그 1개 대기를 EXE 의 ProcessJob 으로 두는 것 — #458 담당은 EXE, 여기선 dfsxml 몫만

#### LCH-13 · 모핑 실행기가 run 폴더 기준 경로를 직접 받게 한다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `DashMorphingDoeExecutor::plan/Execute`·`runDoeBatchForSet` 의 `referenceDatName` 인자를 `runsBaseDir`(절대경로) 로 바꾸고 `QDir(moduleDir).filePath(referenceDatName)` 조립을 지운다. 러너는 `ctx.outputRoot` 를 그 이름으로 넘긴다.
- 완료 기준: (1) executor 에 `moduleDir` 조립이 없다 (2) run 폴더 위치가 `<outputRoot>/<runKey>` 로 종전과 같다 (3) `TestDoeBatchChain` 통과
- 변경 범위: `controller/DashMorphingDoeExecutor.cpp/.h`, `model/DashJobRunner.cpp` (`morphFromTemplate`), `model/DashJobRunnerAnsysMotion.cpp` (`runAnsysMotionMorphingDoe`)
- 선행: PR #651 머지 (`DashJobRunner.cpp`) · PR #652 머지
- 충돌: LCH-02 · LCH-07 · LCH-10 · B2 교집합: DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절) · DashJobRunner.cpp → LCH-03 LCH-14 PRJ-09 UIC-20 · DashMorphingDoeExecutor.cpp → MOR-10 MOR-11 · DashMorphingDoeExecutor.h → MOR-11 · PR #654(DashMorphingDoeExecutor.cpp)
- 흡수: DOE-D13 · LCH-c44 · DOE-c42(LCH-c77)

#### LCH-14 · JobRunner·케이스 표의 죽은 코드와 유명무실 인자를 지운다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `DashJobRunner::isFeSafePostEnabled`, `setDesignVariableModel`/`m_designVariableModel`, `MotionLauncherTask.logDir`, `launchAnsysJournal` 의 `connLog` 빈 연결, `DashDoeCasesWidget::setDirectLauncherCases` 를 삭제하고 `runDoeJobs(QStringList templateFilePaths)` 를 `QString templatePath` 로 좁힌다. `DashDoeSampler::extractDfsxmlMorphingInfo` 는 멤버 상태를 쓰지 않으므로 static 으로 바꿔, Motion 의 임시 `DashDoeSampler sampler;` 모델 생성과 중복 `GetIOController()` 가드(`runAnsysMotionMorphingDoe:462-468`)를 없앤다.
- 완료 기준: (1) 위 심볼 0건 (2) `DashJobRunner*.cpp` 에 `DashDoeSampler` 인스턴스 생성 0건 (3) 빌드·`ctest` 통과 (4) 동작 변경 없음
- 변경 범위: `model/DashJobRunner.h/.cpp`, `model/DashJobRunnerFeSafe.cpp`, `model/DashJobRunnerAnsysJournal.cpp`, `model/DashJobRunnerAnsysMotion.cpp`, `model/DashAnalysisLaunchExecutor.cpp`, `view/DashDoeCasesWidget.cpp/.h`, `model/DashDoeSampler.h/.cpp` (DOE 접점 — `extractDfsxmlMorphingInfo` static 화 1줄)
- 선행: PR #651 머지 (`DashJobRunner.h/.cpp`·`DashJobRunnerFeSafe.cpp`·`DashJobRunnerAnsysJournal.cpp`) · PR #652 머지 (`setDirectLauncherCases`·`setDesignVariableModel` 의 호출부를 그 PR 이 지운다)
- 충돌: LCH-07 · LCH-08 · B2 교집합: DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절) · DashAnalysisLaunchExecutor.cpp → LCH-06 LCH-16 LCH-28 LCH-34 PRJ-09 UIC-20 · DashJobRunner.cpp → LCH-02 LCH-03 LCH-13 PRJ-09 UIC-20 · DashJobRunner.h → CAD-01 LCH-02 LCH-06 LCH-10 LCH-12 · DashJobRunnerAnsysJournal.cpp → CAD-01 LCH-06 LCH-27 LCH-29 UIC-19 · DashDoeSampler.h → DOE-05 DOE-07 DOE-08 DOE-11 DOE-12 · DashJobRunnerFeSafe.cpp → LCH-18 LCH-30 PRJ-14 UIC-19 · DashDoeCasesWidget.cpp → LCH-09 LCH-34 · DashDoeCasesWidget.h → LCH-34
- 흡수: DOE-U4(잔여 1) · DOE-U5(`connLog`) · LCH-c54, LCH-c55, LCH-c56 · DOE-c22(LCH-c66) · DOE-c24(LCH-c67)
- 비고: LCH-10 이 dfsxml 경로를 MBD 단일 호출로 재작성하면 `extractDfsxmlMorphingInfo` 호출 자체가 사라진다 — LCH-10 이 먼저면 그쪽에 흡수

#### LCH-15 · 실행이 끝나면 Preprocess 탭이 새 결과 기준으로 입력을 다시 찾는다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `analysisFinished` 에서 `m_inputsResolved` 를 내려 Preprocess 입력을 무효화한다(대안: `resultFiles` 의 mtime 을 비교 기록에 포함). 다음 Preprocess 탭 진입 또는 현재 탭이 Preprocess 면 즉시 `refreshPreprocessTab` 이 새 `resultFiles` 로 목록을 채운다.
- 완료 기준: (1) Re-run 뒤 Preprocess 탭의 부품·하중 목록이 새 결과 기준 (2) 결과가 바뀌지 않은 Set 재진입은 종전처럼 재탐색을 생략한다
- 변경 범위: `view/DashAnalysisLauncherWidgetLauncher.cpp` (`connectLaunchExecutor`), `model/DashAnalysisLauncher.cpp` (`preprocessInputsChanged`)
- 선행: PR #651·#652 머지 · PRE-02 (#433 종료 검토 — `model/DashAnalysisLauncher.cpp` 진행 중)
- 충돌: #433 (In progress) · LCH-01 · LCH-17 · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashAnalysisLauncherWidgetLauncher.cpp → LCH-08 LCH-10 LCH-16 LCH-28 LCH-29 LCH-33 · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp)
- 흡수: #646-1 · LCH-c32
- 비고: PRE 접점 — `preprocessInputsChanged` 는 결과 경로. 기제는 "비교 조건이 없다" 가 아니다 — `:293` 이 run 기록(`run.dir`+`run.resultFiles`)을 이미 비교하지만, Re-run 이 같은 이름의 결과 파일을 다시 만들면 기록이 동일해 재탐색을 건너뛰고 `readerSession_` 의 옛 내용이 남는다. `refreshPreprocessTab` 은 Set 선택(`DashAnalysisLauncherWidget.cpp:285`)과 탭 전환(`:878`) 양쪽에서 불린다

#### LCH-16 · Re-run 이 새 결과가 Done 이 된 뒤에만 이전 결과를 버린다
- 종류: PR | 규모: M | 태그: A · bug
- 목표: `discardResults` 의 즉시 삭제를 "보류" 로 바꾼다 — Start 시 이전 `resultFiles` 를 `*.prev` 로 옮기고 케이스 상태만 초기화, 케이스 Done 시 `.prev` 삭제, Failed/Cancelled/프로젝트 닫힘, 그리고 `analysisFailed`(실행 거부·Stop) 시 `.prev` 를 되돌리고 종전 Done 상태·`resultFiles` 를 복구한다.
- 완료 기준: (1) Re-run 실패 케이스의 이전 결과 파일과 Done 상태가 남는다 (2) Re-run 성공 케이스에 `.prev` 가 남지 않는다 (3) Stop 뒤에도 이전 결과가 복구된다 (4) MAPDL 미설정·"No active cases" 등 사전 거부 뒤에도 이전 결과와 Done 상태가 보존된다 (5) `producedResultFiles` 의 mtime 비교가 `.prev` 에 영향받지 않는다
- 변경 범위: `model/DashAnalysisLaunchExecutor.cpp/.h` (`discardResults` · `onCaseStatusUpdated` · `cancelAllRuns`), `model/preprocessor/DashAnalysisLauncherConfig.cpp/.h` (`clearCaseResults` 대신 보류 상태), `view/DashAnalysisLauncherWidgetLauncher.cpp` (Start 람다), `tests/TestAnalysisLauncherConfig.cpp`
- 선행: LCH-07 (기록 주체가 executor 하나여야 Done/Failed 시점 훅이 한 곳), PR #651·#652 머지
- 충돌: LCH-01 · LCH-17 · LCH-15 · B2 교집합: DashAnalysisLauncherWidgetLauncher.cpp → LCH-08 LCH-10 LCH-28 LCH-29 LCH-33 · DashAnalysisLaunchExecutor.cpp → LCH-06 LCH-14 LCH-28 LCH-34 PRJ-09 UIC-20 · DashAnalysisLauncherConfig.cpp → DOE-03 DOE-16 PRE-14 PRE-15 PRE-27 PRE-32 · TestAnalysisLauncherConfig.cpp → DOE-03 DOE-16 PRE-14 PRE-15 PRE-32 · DashAnalysisLauncherConfig.h → DOE-03 PRE-15 PRE-27 PRE-32 · DashAnalysisLaunchExecutor.h → LCH-34
- 흡수: #646-2 · LCH-c33
- 비고: run 폴더를 재사용하므로 MAPDL 은 같은 이름의 `.rst` 를 덮어쓴다 — 이름 변경(`.prev`) 없이는 보존이 불가능하다. 새 run 폴더 번호를 쓰는 대안은 출력 레이아웃·Preprocess 조인(`DashLauncherRuns`) 을 바꾸므로 택하지 않는다. Start 람다가 `discardResults`(`:161`) 를 `runDoeAsync`(`:175`) **앞에** 부르므로 사전 검증 거부(`jobFailed` 4곳 · executor "No active cases")가 나면 이미 지운 결과를 되돌릴 지점이 없다 — 대안으로 `discardResults` 를 `runAccepted` 뒤로 옮기면 복구 경로 자체가 줄어든다

#### LCH-17 · Start 확인창에서 Skip 의 뜻을 알린다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: 확인창 본문을 "Re-run: 이전 결과 파일을 지우고 다시 실행 · Skip: 결과가 있는 케이스는 건너뛰고 나머지만 실행" 으로 바꾸고 Skip 버튼에 툴팁을 단다.
- 완료 기준: 확인창 본문·툴팁에 Skip 의 의미가 보인다
- 변경 범위: `view/DashAnalysisLauncherWidgetLauncher.cpp` (Start 람다)
- 선행: PR #651·#652 머지
- 충돌: LCH-01 · LCH-15 · LCH-16 · B2 교집합: DashAnalysisLauncherWidgetLauncher.cpp → LCH-08 LCH-10 LCH-28 LCH-29 LCH-33
- 흡수: #646-3 · LCH-c34

#### LCH-18 · fe-safe ODB 원본 복원을 실측하고 실패 사유 기록을 확인한다
- 종류: INV | 규모: S | 태그: A, B · bug
- 목표: PR #651 머지 뒤 fe-safe 설치 환경에서 A.inp·B.inp Done → .stli Start 를 돌려 run 폴더에 `A.odb`·`B.odb` 가 놓이고 fe-safe 가 `C.odb` 를 내는지 실측한다 (ODB 미발견 시의 사유 기록·Stale ODB 배제는 LCH-30 이 담당).
- 완료 기준: 실측 결과 기록 — 통과면 LCH-30 뒤 #648 닫기, 실패면 지점(`DashJobRunnerFeSafe.cpp:runFeSafeDoe` · `DashFeSafeOdbSources`) 과 후속 PR 범위
- 변경 범위: (조사) `model/DashJobRunnerFeSafe.cpp`, `model/preprocessor/DashFeSafeOdbSources.h` (PR #651 신설)
- 선행: PR #651 머지
- 충돌: B2 교집합: DashJobRunnerFeSafe.cpp → LCH-07 LCH-14 LCH-30 PRJ-14 UIC-19 · DashFeSafeOdbSources.h → LCH-30
- 흡수: #648 기대 1(실측 몫) · LCH-c29 · DOE-c41(LCH-c76)
- 비고: #648 본문이 "정확한 실패 지점은 아직 파악하지 못했다" 라 실측 없이는 닫을 수 없다. PR #651 은 출처 **위치**만 고친다 — 기대 2(탐색 경로 사유 기록)와 DOE-D12 의 "현재 DOE 것인지 안 본다" 는 LCH-30

#### LCH-19 · Direct Launch 의 .stli 실행·여러 파일 큐잉 지원 여부를 정한다
- 종류: DEC | 규모: S | 태그: B
- 목표: PR #652 가 범위 밖으로 둔 두 기능을 (a) 지원 안 함 (b) .stli 만 (c) 둘 다 중 하나로 확정한다. (b)/(c) 면 ODB 출처 지정 UI 와 `DashDirectLaunchStaging` 의 큐 확장을 후속 PR 로 적는다.
- 완료 기준: 결정 기록
- 변경 범위: (결정만) 후속 후보 `controller/DashDirectLaunchRunner.cpp`, `view/dialog/DashDirectLaunchDialog.cpp`
- 선행: PR #651·#652 머지
- 충돌: B2 교집합: DashDirectLaunchDialog.cpp → RUN-30
- 흡수: #604 잔여 · LCH-c19

#### LCH-20 · #456 닫기 — 정규 경로 [Start] 는 이미 워커·시그널 구동이다
- 종류: CLOSE | 규모: S | 태그: B
- 목표: 닫기 사유 기록.
- 완료 기준: 닫기 사유 — `runDoeJobs` 가 코루틴으로 모핑을 `DashMorphingService::background()` 에 `co_await`(#564 d8be33a4 · #586), 솔버 제출은 cae-launcher 비동기, 정규 경로 `processEvents` 0. `generateInputCases` 부재(#570). 잔여 동기 대기는 dfsxml 경로뿐이며 #456 이 비범위로 명시한 것 → LCH-12
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #456 · DOE-D9 · LCH-c01 · DOE-c38(LCH-c73) · EXE-c43(DOE-D9 몫, LCH-c93)

#### LCH-21 · #502 닫기 — 라디오 단일 선택 전제가 사라졌고 범위 밖으로 확정됐다
- 종류: CLOSE | 규모: S | 태그: B
- 목표: 닫기 사유 기록.
- 완료 기준: 닫기 사유 — #601 이후 Analysis Launcher Set 은 파일 1개에 pin 되어 "여러 해석파일 = 여러 Set" 이 됐고 `DashReferenceFileWidget`·라디오가 삭제됐다(#617). PM4 가 "T26 루프 — 착수하지 않는다(2026-09-22)" 로 확정
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #502 · PM4 G8 "T26 루프" · LCH-c15 · DOE-c32(LCH-c69)

#### LCH-22 · #438 닫기 — 추적 전용 부모
- 종류: CLOSE | 규모: S | 태그: B
- 목표: 닫기 사유 기록.
- 완료 기준: 닫기 사유 — 자식 전부 처분: #439 → LCH-03 · #440 → LCH-23 · #441 → LCH-08·LCH-09 · #442 → LCH-24
- 변경 범위: -
- 선행: LCH-03 · LCH-08 · LCH-09
- 충돌: -
- 흡수: #438 · LCH-c14

#### LCH-23 · #440 닫기 — PR #652 가 Direct 표의 상태 배선을 해소한다
- 종류: CLOSE | 규모: S | 태그: D
- 목표: 닫기 사유 기록.
- 완료 기준: 닫기 사유 — PR #652 가 Direct Set 위젯을 지우고 새 Dialog 표가 러너 중계 시그널을 구독(본문 "Output Cases 상태가 Enqueued 에서 바뀌지 않음 → 수정"). 머지 뒤 닫는다
- 변경 범위: -
- 선행: PR #652 머지
- 충돌: -
- 흡수: #440 · DOE-U2 · LCH-c10, LCH-c18 · DOE-c35(U2 몫, LCH-c70) · EXE-c44(DOE-U2 몫, LCH-c94) · UIC-c56(DOE-U2 몫, LCH-c95)

#### LCH-24 · #442 기록 — GitHub 에서 이미 닫힘
- 종류: CLOSE | 규모: S | 태그: C
- 목표: 보드 잔존분 정리.
- 완료 기준: 보드에서 제거 (범위 정리로 닫힌 이슈)
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #442 · LCH-c13

#### LCH-25 · #604 닫기 — PR #652 머지로 종결, 잔여는 LCH-14·LCH-19
- 종류: CLOSE | 규모: S | 태그: B, D
- 목표: 닫기 사유 기록.
- 완료 기준: 닫기 사유 — 범위 3항(Tool 메뉴 Dialog·창 닫아도 지속 / Direct Set 위젯 제거 / Output Cases 상태) 전부 PR #652. 잔여: `setDirectLauncherCases`·`setDesignVariableModel` 정의 잔존 → LCH-14, .stli·다중 큐잉 → LCH-19
- 변경 범위: -
- 선행: PR #652 머지
- 충돌: -
- 흡수: #604 · LCH-c06, LCH-c16, LCH-c17, LCH-c18 (잔여 LCH-c19 → LCH-19, LCH-c55 → LCH-14) · DOE-c35(Direct 잔재, LCH-c70)

#### LCH-26 · #616 닫기 — PR #651 머지로 종결, 잔여는 #647·#648
- 종류: CLOSE | 규모: S | 태그: A, C
- 목표: 닫기 사유 기록.
- 완료 기준: 닫기 사유 — 결정표 포맷 3종 × 범위 4항 + 추가 결정 2건 전부 PR #651 (Add File 복사·원장·Launcher Set / RW 검사 `DashReferenceKind::isRwReadable` / Launcher 탭 분기 — dfsxml·stli 는 dev 가 이미 일치, wbpj `_files` 한정 / `odbSourceSets` + fe-safe 복사 / 이름 충돌 경고 / 삭제 연동). 하위 #647 → LCH-10·LCH-11, #648 → LCH-18
- 변경 범위: -
- 선행: PR #651 머지
- 충돌: -
- 흡수: #616 · LCH-c08, LCH-c20, LCH-c21, LCH-c22, LCH-c23, LCH-c24, LCH-c25

#### LCH-27 · Direct wbpj 다중 파일에서 NX 로드 완료 구독을 잡 단위로 해제한다
- 종류: PR | 규모: S | 태그: B · bug
- 목표: `startDirectAnsysJournalJobs` 가 wbpj 마다 `loadPrtCompleted`·`nxCadParametersJson` 람다를 연결한 뒤, 첫 완료 람다 안에서 `disconnect(nxCad, …, this, nullptr)` 로 이 객체의 모든 구독을 끊어 두 번째 이후 wbpj 의 람다가 영영 불리지 않는다(케이스 Enqueued 잔존 → 종결 계약 위반). `launchAnsysJournal` 의 선례(`connCompleted`/`connFailed` 핸들)대로 `QMetaObject::Connection` 을 잡아 자기 것만 끊고, `capturedParams` 는 stp 경로 일치 검사를 거친 뒤에만 채운다.
- 완료 기준: (1) wbpj 2개 Direct 실행에서 두 케이스 모두 ANSYS Journal 이 기동하고 Done/Failed 에 이른다 (2) `DashJobRunnerAnsysJournal.cpp` 에 `disconnect(nxCad, …, this, nullptr)` 0건
- 변경 범위: `model/DashJobRunnerAnsysJournal.cpp` (`startDirectAnsysJournalJobs`)
- 선행: LCH-29 (wbpj 경로 처분) · PR #652 머지 (Direct 진입이 `DashDirectLaunchRunner` 로 바뀜 — 호출 시그니처 확인) · LCH-19 ((a) "다중 큐잉 지원 안 함" 이면 시그니처를 파일 1개로 좁히는 쪽이 더 작다)
- 충돌: LCH-06 · LCH-07 · LCH-14 (같은 파일) · B2 교집합: DashJobRunnerAnsysJournal.cpp → CAD-01 UIC-19 · PR #651(DashJobRunnerAnsysJournal.cpp)
- 흡수: #249(범위 밖 절 — CAD 가 넘김) · CAD-c14 · LCH-c64
- 비고: 단일 wbpj 에서는 발현하지 않아 PR #652 Direct Dialog(파일 1개, 다중 큐잉 범위 밖) 에서는 잠복. `nxCadParametersJson` 공유 캡처도 같은 기제 — 파일 N 개가 같은 `capturedParams` 를 덮어쓴다. LCH-29 가 **제거**면 이 항목은 소멸하고, **동결**이면 LCH-19(a) 로 대체한다(시그니처를 파일 1개로 좁히는 쪽이 더 작다) — **현행 유지**일 때만 본문대로 수술한다

#### LCH-28 · Launcher 배치 실행의 진행·취소·가드 표시를 EXE-07 규약에 맞춘다
- 종류: PR | 규모: S | 태그: B, D · feature
- 목표: #463 의 LCH 몫. 현행은 Start/Stop 버튼(`setLauncherIdle`) + executor `isRunning` 가드 + 케이스 표 상태 열로 진행·취소·가드 3요소를 이미 갖춘다. EXE-07 이 정한 규약(상태바 진행바·문구·취소 버튼 자리·반려 안내)과의 차이분만 배선한다 — 예: 상태바에 "N/M 케이스" 결정 진행바, 실행 중 Start 재클릭 반려 안내(EXE-09 헬퍼).
- 완료 기준: (1) EXE-07 규약 표 대비 Launcher 탭의 차이 0 (차이가 없으면 확인 기록으로 종료) (2) 기존 Start/Stop·케이스 표 동작 불변
- 변경 범위: `view/DashAnalysisLauncherWidgetLauncher.cpp` (`connectLaunchExecutor` · `setLauncherIdle`), `model/DashAnalysisLaunchExecutor.cpp` (케이스 집계 진행률 방출 — 규약이 요구할 때만)
- 선행: EXE-07 (규약) · EXE-09 (가드 헬퍼) · PR #651·#652 머지
- 충돌: LCH-01 · LCH-08 · LCH-15 · LCH-17 (같은 파일) · B2 교집합: DashAnalysisLauncherWidgetLauncher.cpp → LCH-10 LCH-16 LCH-29 LCH-33 · DashAnalysisLaunchExecutor.cpp → LCH-06 LCH-07 LCH-14 LCH-16 LCH-34 PRJ-09 UIC-20
- 흡수: #463(LCH 몫) · EXE-c23 · LCH-c92
- 비고: #456 은 해소됨(LCH-20) 이라 이 항목이 #463 의 LCH 적용처. PR #652 Direct Dialog 의 진행 표시도 머지 뒤 같은 규약 — 파일은 머지 뒤 확정

#### LCH-29 · wbpj 배치·Direct 실행 경로의 처분을 정한다
- 종류: DEC | 규모: S | 태그: A, C
- 목표: `.wbpj`(ANSYS Workbench) 경로를 (a) **현행 유지** — #616 결정표가 정본이고, 매니페스트의 "사장·불개입" 은 기준모델·조합·스탬프 묶음 안의 불개입(D32·D33 철회)으로 한정한다 / (b) **동결** — 버그만 고치고 기능 확장 없음 / (c) **제거** — 코드·UI 를 걷어낸다 중 무엇으로 할지 정한다. 입력 자료가 시간순으로 모순된다: `01-sources/wiki/Project-Manifest-CAD-Path-Disposition.md`(2026-09-18) "특화 일회성 경로 — 사장 예정, 개선 불개입 · wbpj DOE 전체 격리" vs #616 결정표(2026-10-02) wbpj 열 "Add File 복사 · Launcher Set `{파일명}_wbpj` · Target Part `.prt` 콤보 현행 유지 · 결과 `.rst` → #640 콤보" + PR #651(wbpj Project Assets·`_files` 한정) · PR #652(Direct Dialog 가 wbpj+`_files` 스테이징).
- 완료 기준: 결정 기록 — (1) 선택지 (a) 현행 유지 / (b) 동결 / (c) 제거 중 하나와 근거(어느 문서가 정본인지) (2) 소비자별 축소·되돌림 범위 (3) **PRJ 원장 조항** — (c) 제거(사장 확정)면 `.wbpj`·`.stli` 의 원장 비편입을 확정하고 PRJ 신규 항목은 0, (a) 현행 유지면 PRJ 에 `.wbpj`·`.stli` 원장 편입 항목 1건을 신설한다(`model/DashReferenceModelLedger` · Project Assets 트리 · `DashMainWindow::copyFileIntoProject`), (b) 동결이면 신규 편입 없이 현행 취급만 유지한다
- 변경 범위: (결정만) 후속 후보 `model/DashJobRunnerAnsysJournal.cpp`(wbpj TU 전체), `view/DashAnalysisLauncherWidgetLauncher.cpp`(`fillTargetPartCombo` wbpj 분기), PR #651·#652 의 wbpj 분기
- 선행: -
- 충돌: B2 교집합: DashAnalysisLauncherWidgetLauncher.cpp → LCH-01 LCH-08 LCH-10 LCH-15 LCH-16 LCH-17 LCH-28 LCH-33 · DashJobRunnerAnsysJournal.cpp → CAD-01 LCH-06 LCH-07 LCH-14 LCH-27 UIC-19 · PR #652(DashAnalysisLauncherWidgetLauncher.cpp) · PR #651(DashAnalysisLauncherWidgetLauncher.cpp·DashJobRunnerAnsysJournal.cpp)
- 흡수: Project-Manifest-CAD-Path-Disposition "사장 경로로 격리" 표 · #616 결정표 wbpj 열
- 비고: 소비자(결정 영향 대상) — **CAD-01 Phase 3** · **CAD-02** · **CAD-05**(불개입 경로 수정분을 뺄지) · **LCH-06** · **LCH-27** · **PRJ**(`.wbpj`·`.stli` 원장 편입이 PRJ 코드 — 완료 기준 (3)). CAD 쪽 항목의 `선행` 등록은 `보류: CAD 몫`. PRJ 소비자 등록은 **완료** — PRJ.md 머리말 · PRJ-21 비고 · 대응표 `LCH-29 (DEC, 접점) → 항목 없음` 행. PRJ 조항 근거 — 매니페스트가 `.wbpj`·`.stli` 원장 편입(후속작업 5)을 "범위 밖 유지" 로 미뤘고 그 코드가 PRJ 소유다. 현행 PRJ 소유 파일에 `wbpj` **0건**(`DashMainWindow.cpp`·`DashModelingTreeWidget.cpp`·`DashReferenceModelLedger.cpp`·`DashProject.cpp`), `.stli` 는 `view/DashMainWindow.cpp` 5곳(`:362`·`:2628` Add File 필터 · `:2649` 부모 폴더 복사 · `:2963`·`:2968` Reference Files 선택)이고, PR #651 이 `model/DashProject.cpp`·`view/DashModelingTreeWidget.cpp`·`model/DashReferenceSetName.h` 에 정책을 들여놓는다(PRJ 검토 19 의 "stli 1곳" 은 실측 5곳으로 정정). 축소 내용 — (c) 면 LCH-06 은 Journal TU 삭제 PR 에 흡수(시그널 자체 삭제), LCH-27 은 소멸, PR #651·#652 의 wbpj 분기와 #640 wbpj 사용처(PRE)를 되돌린다 / (b) 면 LCH-27 은 LCH-19(a) 로 대체. **LCH-28 은 포맷 무관**(`setLauncherIdle`·executor 집계)이라 축소 없음 — (c) 일 때 `cancelAllRuns` 의 Journal `m_stpBatch` 분기(`:502`)만 범위에서 빠진다

#### LCH-30 · fe-safe ODB 출처를 현행 DOE 의 Done 케이스로 한정하고, 미발견 시 탐색 경로를 남긴다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `runFeSafeDoe` 의 ODB 복사가 파일 존재만 보지 않고, 출처 Set 케이스가 Done 이며 현행 `tableId` 인지(`DashLauncherRuns::isCurrentCase`) 검사해 stale ODB 를 배제한다. 하나도 못 찾으면 Failed 와 함께 **어느 경로를 봤는지** 목록을 로그와 `caseLogUpdated`(케이스 표 Log 열)에 남긴다.
- 완료 기준: (1) 출처 Set 을 재샘플링해 `tableId` 가 바뀐 뒤 .stli Start 하면 옛 ODB 가 복사되지 않고 Failed (2) ODB 부재 케이스의 Log 열에 탐색한 절대경로 전부가 보인다 (3) 정상 경로(출처 Done · 현행 tableId)는 종전과 같이 복사된다
- 변경 범위: `model/DashJobRunnerFeSafe.cpp` (`runFeSafeDoe`), `model/preprocessor/DashFeSafeOdbSources.h` (PR #651 신설 — 탐색 경로 반환), `model/preprocessor/DashLauncherRuns.h` (`isCurrentCase` 재사용)
- 선행: PR #651 머지 (출처 위치·`odbSourceSets` 를 그 PR 이 깐다)
- 충돌: LCH-18 (같은 함수 실측) · B2 교집합: DashJobRunnerFeSafe.cpp → LCH-07 LCH-14 PRJ-14 UIC-19 · DashLauncherRuns.h → PRE-32
- 흡수: #648 기대 2 · DOE-D12(잔여 — "판정이 파일 존재뿐") · LCH-c23(출처 위치 외 잔여) · LCH-c76
- 비고: dev 의 미발견 로그는 "FE-safe prelaunch failed (no ODB sources found)" 1줄이고 PR #651 도 이 줄을 바꾸지 않는다(`DashJobRunnerFeSafe.cpp:286-290`). PR #651 의 `DashFeSafeOdbSources::sourceOdbPath` 는 `QFileInfo::exists` 만 본다

#### LCH-31 · GUI↔DashOptiMBD 단일 호출 계약을 정한다
- 종류: DEC | 규모: S | 태그: B, C
- 목표: LCH-10·LCH-11 이 공유할 호출 계약을 먼저 기록한다 — 인자 전달 형식(템플릿 경로·VTU 경로·DOE 값·출력 폴더·Target Part 를 CLI 인자로 줄지 JSON 파일로 줄지), 산출물 이름 규칙(`{runKey}.dfsxml`·`.dfmm`·`.dfg`·`.dfr`), 종료 코드·stdout 규약(성공/실패 판정 근거를 exit code 로만 둘지 stdout 토큰도 쓸지), 모델 종속 값(밀도·단위·`-b` 블록)의 소유처.
- 완료 기준: 결정 기록 — 계약 표 1개(인자 · 산출물 · 종료 규약 · 모델 종속 값 소유처)와 선택 근거
- 변경 범위: (결정만) 후속 후보 `controller/DashExtensionProcess.h`(`MBD_MotionWriter`·`MBD_MotionLauncher` 상수 주석의 인자 규격), DashOptiMBD CLI
- 선행: -
- 충돌: B2 교집합: DashExtensionProcess.h → EXE-11 EXE-12 LCH-10
- 흡수: LCH-10 비고의 "LCH-11 과 한 번에 정한다 — 되돌리기 비용이 큰 결정"
- 비고: 00-plan 1절 "되돌리기 비용이 큰 결정(공개 API·CLI 인터페이스)" 에 해당해 EXT(LCH-11)보다 앞선다. 현행은 두 서브커맨드가 각각 `motion-writer <ref_folder> <vtu_dir> <density> --unit m -o <out> -b 19` · `motion-launcher <ansys_path> <xml_dir>` 이고, 완료 판정이 exit code 와 stdout 양쪽에 걸쳐 있다(LCH-05 의 원인)

#### LCH-32 · Set 상태 갱신 비용을 검증하고 필요한 경우에만 기록 파일을 분리한다
- 종류: DEC | 규모: S | 태그: A, C
- 목표: #444는 #441 하위 저장 경계 작업이다. 저장·읽기·화면 갱신 비용을 측정하고 기존 구조의 단일 라이터·증분 갱신으로 해결 가능한지 먼저 판단한다. 해결되지 않는 병목에만 파일 분리를 선택하고 효과를 검증한다.
- 완료 기준: 상태 갱신 전후 비용과 병목을 기록하고 기존 구조 유지 또는 필요한 파일만 분리하는 결정을 남긴다. 분리 선택 시 저장·읽기·화면 갱신 개선 및 복원 정합을 검증한다. 모든 Set JSON 일괄 분할을 요구하지 않는다.
- 변경 범위: (결정만)
- 선행: -
- 충돌: -
- 흡수: #444 · PRJ-c60 · PRJ-c07(LCH-c89)
- 비고: LCH-07·LCH-08은 기존 구조 개선 대안 및 공유 코드 접점이다. 실측 없이 분할 불필요로 확정하지 않는다. 저장 경계 개선 후 LCH-09(#441)의 재시작 복구를 적용하며 ID 참조 전환을 선행으로 두지 않는다. PER-03의 포맷 규약은 실제 분리 결정 시 적용한다.

#### LCH-33 · Start가 선택한 DOE 입력과 실제 산출물 출처를 검증한다
- 종류: PR | 규모: S | 태그: C, A · bug
- 목표: runDoeAsync 호출 전에 현재 선택한 DOE setId와 Table·deck의 필수 출처 및 실제 선택 관계를 공통 계약으로 검증한다. 다른 DOE setId의 유효한 입력으로 변경할 수 있다. 현재 Launcher ID는 유지하고 선택 변경만으로 기존 실행 스냅샷·결과 출처를 바꾸지 않으며 새 실행이 실제 사용하는 출처를 기록한다.
- 완료 기준: ① 다른 유효 DOE Set 선택 후 Start 가능 ② 선택만 바꾼 상태의 기존 결과·출처 불변 ③ 새 실행 결과 덮어쓰기 시 실제 입력 출처 갱신 ④ 필수 출처 누락·잘못된 참조는 실행 전 거절하고 재생성 안내, runDoeAsync 미호출 ⑤ 쓰기 실패와 출처 검증 실패 사유 구분 ⑥ 최초 핀 부재를 통과 근거로 삼지 않음.
- 변경 범위: `view/DashAnalysisLauncherWidgetLauncher.cpp` (Start 람다), `model/DashAnalysisLauncher.h/.cpp` (`snapshotDoeTable` · 대조 판정 신설)
- 선행: DOE-16 (생산 출처와 스냅샷 전달)
- 충돌: LCH-01 · LCH-15 · LCH-16 · LCH-17 (같은 Start 람다·같은 파일) · PRE-32 (같은 출처 판독 계약·실행 기록 접점) · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashAnalysisLauncherWidgetLauncher.cpp → LCH-08 LCH-10 LCH-28 LCH-29 · DashAnalysisLauncher.h → PRE-03 PRE-08 PRE-16 PRE-23 PRE-24 PRJ-22 · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h)
- 흡수: #368 Phase 2 (T21 중 Start 거절 몫 — PRE 검토 #2 인계) · LCH-c99
- 비고: PRE-32와 같은 공통 계약을 사용하되 PRE-32의 최초 핀 기록에 의존하지 않는다. 기존 snapshotDoeTable 쓰기 실패 취소는 유지한다. #650 최신성 표시는 출처 유효성 검증과 별도다. 입력 선택·재실행 시나리오와 스냅샷 보존·갱신을 검증한다.

#### LCH-34 · 런처 JSON 기록 실패 사유를 호출부에서 알린다
- 종류: PR | 규모: S | 태그: D, A · bug
- 목표: PRE-15 가 `QString* error` 로 내주는 사유를 LCH 호출부가 받아 알린다 — Active 체크 기록 실패(`DashDoeCasesWidget` 2곳, 사용자 행위)는 모달에 경로 + 사유를 띄우고 체크 상태를 되돌린다. 케이스 상태 기록 실패(executor 단일 라이터)는 런당 1회 통지 + 실패 키 전체 로그로 모은다.
- 완료 기준: (1) 설정 파일을 깨진 JSON 으로 둔 뒤 케이스 Active 체크 → 모달에 파싱 오류 사유가 보이고 체크 상태가 원복 (2) 같은 상태로 배치 1회 실행 → 통지 1회 · 로그에 실패한 키 전부 (케이스 수만큼 모달이 뜨지 않는다) (3) 기록 성공 경로의 통지 0
- 변경 범위: `view/DashDoeCasesWidget.cpp/.h` (`saveAllActiveStates` · `persistActiveFlag`), `model/DashAnalysisLaunchExecutor.cpp/.h` (`onCaseStatusUpdated`)
- 선행: PRE-15 (사유를 내주는 출력 인자) · LCH-07 (상태 기록이 executor 한 곳이어야 "런당 1회" 가 성립 — 없으면 러너 TU 6개에 같은 통지를 흩뿌려야 한다)
- 충돌: LCH-06 · LCH-08 · LCH-14 · LCH-16 · LCH-28 (같은 파일) · B2 교집합: DashAnalysisLaunchExecutor.cpp → PRJ-09 UIC-20 · DashDoeCasesWidget.cpp → LCH-09
- 흡수: #638-2 (LCH 호출부 몫 — PRE-15 인계) · LCH-c100
- 비고: PRE-15 가 반환형을 `bool` 유지 + 출력 인자로 둔 덕에 LCH 호출부 4곳이 무변경 컴파일되고 LCH-07 과도 순서가 무관하다 — 본 항목은 그 사유를 쓰는 쪽만 더한다. 모달을 케이스 단위로 두지 않는 이유는 스레드가 아니라 횟수다: `moveToThread` 0건이고 `DashJobRunner` 는 executor 의 자식이라 네 호출부가 모두 GUI 스레드지만(`DashAnalysisLaunchExecutor.cpp:33`), 상태 기록은 케이스×전이마다 일어나 모달이 배치를 막는다. 선례는 `snapshotDoeTable` 의 쓰기 실패(통지 1회 + `cancelAllRuns`). Direct Launch 는 `launcherConfigPath` 가 비어 기록 자체가 없으므로 대상이 아니다(`DashJobRunner.cpp:131-134` · `DashDoeCasesWidget.cpp:352-355`·`:388-391`)

### PRE — Analysis Launcher — Preprocess·결과 처리

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> 기준 dev @ b08a91b3. 원천·판정은 02-claims/PRE.md. 작성기(DashResultXmlWriter.cpp) 항목은 PRE-07 → PRE-20 → PRE-06 → PRE-10 → PRE-04 순으로 하면 같은 함수를 한 번씩만 지난다. 열린 PR 7건 중 **머지 대상 6건**(#651 #652 #654 #655 #656 #658) — #530 은 재업로드 노선이라 머지하지 않는다(C-2 결정 ② · ⑩). #368 공통부는 PER-07 이 dev 기준으로 다시 올리고 T21 홉은 PRE-32 가 흡수하므로, #368 관련 충돌은 그 두 항목과의 충돌로만 센다.
>
> **PR #656**(#433 후속)이 PRE-03 을 전부 구현해 PRE-03 은 CLOSE 로 바뀌었고, PRE-04 의 TimeSteps 원문 파싱 모으기도 선반영됐다. **PR #658**(preprocessor v3 수용, draft)은 카탈로그 sub-result 발행 · 이름 기반 배열 조회(`responseArray`) · `modeShapeLeaf` · 질의의 `sub_result` 적재를 이미 고쳐 PRE-06 · PRE-10 · PRE-17 · PRE-18 의 전제를 바꾸고, 결과 XML 에 `quantity`·`unit`·`component_labels` 속성을 더해 PRE-29 의 포맷 기준선을 옮긴다 — 실측 기준까지 더해 PRE-01 · 06 · 10 · 17 · 18 · 29 여섯 항목이 #658 을 선행(PRE-29 는 선행 + 결정 입력)으로 둔다. #656 은 PRE-02 · PRE-04 의 선행이다. 단순 동시 수술은 D-1 의 `build_deps.py --apply` 가 충돌란에 채운다.

#### PRE-01 · #433 8단계 실측 — fe-safe ODB · 모달 `.rst`/`.odb` · Motion `.dfr` 을 Level 3 테스트에 더한다
- 종류: INV | 규모: S | 태그: F · docs
- 목표: `TestRealResultFiles` 에 fe-safe 2스텝 ODB(#493 누락 시나리오)·모달 `.rst`·모달 `.odb`·Motion `.dfr` 케이스를 추가하고 실측 결과(PASS/SKIP·발견 결함)를 #433 본문 형식으로 기록한다
- 완료 기준: 실측 결과 — 케이스 4종의 리더·미리보기·배치 경계 기록. 파일이 없는 케이스는 QSKIP 사유로 남긴다
- 변경 범위: tests/TestRealResultFiles.cpp · `DASH_TEST_RESOURCES` 리소스
- 선행: PR #658 (preprocessor v3 — 실측 기준이 v3 의 엄격한 오류 정책이어야 한다. #658 본문도 실파일 테스트를 SKIP 하고 QC 로 넘겼다. v2 에서 잰 경계는 머지 뒤 무효)
- 충돌: B2 교집합: TestRealResultFiles.cpp → PRE-06 PRE-09 PRE-16 PRE-17
- 흡수: #433-8 · #637(확인 방법) · PRE-c01, PRE-c02
- 비고: fe-safe 는 Abaqus ≥ 2023, Motion 은 `.dfr` 파일이 필요해 미확인. 실측에서 나온 결함은 별도 항목으로 뺀다

#### PRE-02 · #433 종료 검토 — 완료 기준 미체크 항목을 점검하고 #454 경계를 기록한다
- 종류: INV | 규모: S | 태그: E · docs
- 목표: 완료 기준의 미체크 6항(책임 분리·기존 클래스 재사용·동작/저장 결과 비교·빌드·회귀·새 세션 검토·증분 통합)을 현재 dev 에서 확인하고, #454 가 시작할 경계(`processResults`·`DashResultProcessor`·`DashReaderSession::Work`)를 본문에 기록한 뒤 #433 을 닫는다
- 완료 기준: 검토 기록 — 분해 전후 표 구성·응답 조회·미리보기·결과 XML·설정 JSON 비교 결과, 새 세션 검토 반영 여부, #433 종료. **실측 파일이 없는 케이스(PRE-01 의 QSKIP 분)는 "미확인 — 파일 부재" 로 기록하고 종료를 막지 않는다**
- 변경 범위: 문서(이슈 본문·위키)만
- 선행: PRE-01, PRE-04, PRE-07, PRE-20 (9단계 잔여) · PR #656 (#433 후속 — 이것이 머지돼야 9단계 질의 직렬화·모달 Name·TimeSteps 파싱이 끝난다)
- 충돌: -
- 흡수: #433 완료 기준 · #454 선행 · PRE-c03, PRE-c13
- 비고: 열린 #433 PR 은 #656(`refactor/433-launcher-common`) 하나이고 `refactor/433-*` 나머지 6개는 통합됐다. 9단계 잔여가 끝나기 전에는 "같은 책임의 병렬 구현을 추가하지 않는다" 를 체크할 수 없다. 이 항목은 문서 작업이라 PRE-23(#454) 의 선행이 아니다 — #433·#454 의 "같은 파일 동시 수술 금지" 는 코드 항목(PRE-04·07) 사이의 제약이다

#### PRE-03 · 런처·초기화기의 질의 직렬화와 모달 Name 리터럴 공용화 — PR #656 이 구현
- 종류: CLOSE | 규모: S | 태그: E · refactor
- 목표: PR #656(`refactor/433-launcher-common`, #433)이 이 항목 전부를 구현했다 — `toJson(Compact)` 4곳(`DashAnalysisLauncher.cpp` :704 :712 :1412 · `DashResponseInitializer.cpp` :185)이 `DashResultQuery::compact` 로, 모달 Name 리터럴 2곳(:638-641 · :759-769)이 `DashResultQuery::modalNames()` 로 바뀌고 쓰지 않는 `modeNames` 가 삭제됐다. 덤으로 GetTimeSteps 원문 파싱 3곳도 신설 `DashResultKeys::timeStepsOf` 로 모였다
- 완료 기준: 닫기 사유 — PR #656 머지. 잔여 1줄(`DashResultKeys.cpp:29` `firstTimeStepQuery` → `DashResultQuery::compact`)은 PRE-04 가 흡수한다 — #656 이 안 건드린 유일한 PRE 영역 직렬화 지점이고, 한 줄짜리 PR 로 세우지 않는다(00-plan 1-2)
- 변경 범위: - (PR #656: model/DashAnalysisLauncher.{h,cpp} · model/preprocessor/DashResponseInitializer.cpp · DashResultKeys.{h,cpp} · DashResultXmlWriter.cpp · tests)
- 선행: -
- 충돌: B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashResultXmlWriter.cpp → 공유 10건(deps.md 5절) · DashAnalysisLauncher.h → LCH-33 PRE-08 PRE-16 PRE-23 PRE-24 PRE-32 PRJ-22 · DashResponseInitializer.cpp → PRE-04 PRE-07 · DashResultKeys.cpp → PRE-04 PRE-19 · DashResultKeys.h → PRE-04 · PR #658(DashAnalysisLauncher.cpp·DashResultKeys.cpp·DashResultKeys.h·DashResultXmlWriter.cpp) · PR #656(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h·DashResponseInitializer.cpp·DashResultKeys.cpp·DashResultKeys.h·DashResultXmlWriter.cpp) · PR #652(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h) · PR #651(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h)
- 흡수: #433-9 · PRE-c08, PRE-c09
- 비고: 고객사 규칙 사본 9곳(`LGE_SpringRule.cpp` 2 · `ILJIN_TensionlinkRule.cpp` 7)과 어댑터 래퍼의 자체 헬퍼(`wrapper/LegacyJsonPreprocessor.cpp:52`)는 #656 도 손대지 않았고 앞으로도 손대지 않는다

#### PRE-04 · 요청→시점 해석을 `DashResultBatch::timeOf` 결과 전달로 단일화한다
- 종류: PR | 규모: L | 태그: E · refactor
- 목표: 런처가 구한 `TimeRef` 를 `DashResultProcessor::ProcessContext` → `appendSample` → `writeFieldOutputToXml` 과 `DashResponseInitializer` 에 넘기고, 처리기·작성기·초기화기의 loadStep/state 파싱 사본(처리기 1 · 작성기 3 · 초기화기 2)을 지운다. GetTimeSteps 원문 파싱(런처 2 · 작성기 1)은 PR #656 이 `DashResultKeys::timeStepsOf` 로 이미 모았으므로, 같은 파일의 잔여 직렬화 1줄(`DashResultKeys.cpp:29` `firstTimeStepQuery` → `DashResultQuery::compact`, PRE-03 잔여)만 함께 치운다
- 완료 기준: 처리기·작성기·초기화기에 `loadStep`·`State `·`Mode\s+` 파싱 0 · `TestResultProcessor`·`TestResultXmlWriter`·`TestResponseInitializer` 통과 · 생성 XML 의 파일명·step/substep 동일
- 변경 범위: model/preprocessor/DashResultProcessor.{h,cpp} · DashResultXmlWriter.{h,cpp} · DashResponseInitializer.{h,cpp} · DashResultKeys.{h,cpp} · model/DashAnalysisLauncher.cpp · tests
- 선행: PRE-07 (같은 시그니처에 플래그를 먼저 싣는다), PRE-05 · PR #656 (`timeStepsOf` 선반영 — 런처·초기화기·작성기의 같은 네 자리를 이미 고쳤다)
- 충돌: PRE-06, PRE-10, PRE-20 (작성기 같은 함수) · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashResultXmlWriter.cpp → 공유 10건(deps.md 5절) · DashResultXmlWriter.h → PRE-22 PRE-30 PRE-31 PRE-32 · DashResponseInitializer.cpp → PRE-03 · DashResultKeys.cpp → PRE-03 PRE-19 · DashResultProcessor.cpp → PRE-23 · DashResultProcessor.h → PRE-23 · DashResultKeys.h → PRE-03 · PR #658(DashAnalysisLauncher.cpp·DashResultKeys.cpp·DashResultKeys.h·DashResultXmlWriter.cpp) · PR #652(DashAnalysisLauncher.cpp) · PR #651(DashAnalysisLauncher.cpp)
- 흡수: #433-9 · PRE-c06, PRE-c05(잔여 — LGE 규칙 1곳만 남고 손대지 않는다), PRE-c09(잔여 `DashResultKeys.cpp:29`)
- 비고: L 사유 — 한 개념(시점 해석을 한 출처로)인데 사본이 처리기·작성기·초기화기·키 파서 9파일에 흩어져 있다. GetTimeSteps 원문 파싱 모으기가 #656 으로 빠져 규모는 L 하단이지만 대상 파일 수는 그대로다. `LGE_SpringRule::extractModalFrequency` 의 자체 파싱은 고객사 규칙이라 손대지 않는다. `processResults`·`DashResultProcessor` 는 #454 대상이므로 PRE-23 과 동시에 열지 않는다

#### PRE-05 · 위젯이 Motion Load Step 을 "State N" 으로 넘긴다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: Add·Preview·KPI 대화상자의 Load Step 문자열 조립 3곳이 `onSelectionChanged` 와 같은 규칙(부모가 "States" 면 자식 텍스트만)을 쓴다. 조립을 한 함수로 뽑는다. `parseMotionState`·`stateOf` 테스트에 "States / State N" 거부(또는 수용) 케이스를 더한다
- 완료 기준: Motion 결과에서 State 2 Preview 가 형식 오류 없이 질의까지 간다 · State 2 를 Add 한 행의 Load Step 문자열이 `State 2` 고 요청의 `timeOf` 가 state 2 로 풀린다(`TestResultBatch`) · 테스트 통과
- 변경 범위: view/DashAnalysisLauncherWidget.{h,cpp} · tests/TestResultQuery.cpp · tests/TestResultBatch.cpp
- 선행: -
- 충돌: B2 교집합: DashAnalysisLauncherWidget.cpp → PRE-08 PRE-18 PRE-23 PRE-24 PRE-27 · DashAnalysisLauncherWidget.h → LCH-01 PRE-23 · TestResultBatch.cpp → PRE-16 · PR #658(TestResultQuery.cpp) · PR #651(DashAnalysisLauncherWidget.h)
- 흡수: #634 · PRE-c33, PRE-c34
- 비고: 해석기 쪽 수용으로 가면 5곳을 고쳐야 하므로 위젯 쪽 통일을 택했다. 실제 `.dfr` 확인은 PRE-01. "State 1·2 Add → `_1_0_`·`_2_0_` 두 파일" 은 이 항목만으로 성립하지 않는다 — 처리기·작성기의 Motion 판정 입력이 참조 파일 basename 이라 전 샘플 Missing 이고, 쓴 샘플이 0 이면 파일을 만들지 않는다(`DashAnalysisLauncher.cpp:1053`). 파일 생성 확인은 PRE-07 뒤로 미룬다

#### PRE-06 · 필드 출력 질의에 `field_output_name` 을 `operator` 와 함께 싣는다
- 종류: PR | 규모: M | 태그: A · bug
- 목표: 카탈로그 항목으로 만드는 질의 전부 — 작성기 일반 경로(`result` 키 폴백 제거) · Mode Shape 루프 · 원형도 변위 탐색 · 미리보기(일반·Motion 분기에도 응답 키) · Level 3 테스트 — 에 `field_output_name` 을 싣는다. **PR #658 이 이미 한 것은 뺀다** — 배열을 이름으로 찾는 `responseArray()`(임의 `GetArray(0)` 폴백·성분 수 ≥3 선택 제거), leaf 조회를 질의 앞으로 올리기, 질의의 `sub_result` 지목, `MatchResponse` 가 둘 다 맞는 항목 우선(선택 항목이었다)
- 완료 기준: `TestResultXmlWriter`·`TestRealResultFiles` 질의에 field_output_name 포함 · operator 미발견 샘플은 Missing(#658 이 선반영한 것의 회귀 확인) · `.dfr` Preview 가 "No field output" 이 아니라 결과를 그린다(PRE-01 에서 확인)
- 변경 범위: model/preprocessor/DashResultXmlWriter.cpp · model/DashAnalysisLauncher.cpp (requestVtkPreview) · tests/TestRealResultFiles.cpp · tests/TestResultXmlWriter.cpp
- 선행: PRE-05 (Motion 미리보기가 질의까지 가야 확인된다), PRE-07 · PR #658 (같은 세 경로를 이름 조회로 이미 고쳤다 — 질의 적재만 남는다)
- 충돌: PRE-10, PRE-20, PRE-04 · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashResultXmlWriter.cpp → 공유 10건(deps.md 5절) · TestRealResultFiles.cpp → PRE-01 PRE-09 PRE-16 PRE-17 · TestResultXmlWriter.cpp → PRE-31 PRE-32 · PR #656(DashAnalysisLauncher.cpp·DashResultXmlWriter.cpp·TestResultXmlWriter.cpp) · PR #652(DashAnalysisLauncher.cpp) · PR #651(DashAnalysisLauncher.cpp)
- 흡수: #630 · PRE-c24(잔여 — field_output_name 적재·result 폴백), PRE-c26(질의 측), PRE-c27, PRE-c28, PRE-c29 · PRE-c25·PRE-c30 은 PR #658 로 해소됨
- 비고: ILJIN 규칙(배열 이름 = operator)은 손대지 않는다. Function Expression 의 배열 조회는 #658 이 `responseArray()` 로 바꿨으므로 질의 적재만 본다. Mode Shape 의 변위 항목 선택 규칙은 PRE-10

#### PRE-07 · 해석 종류(Motion·Modal) 플래그를 Load 에서 정해 처리기·작성기·초기화기에 넘긴다
- 종류: PR | 규모: M | 태그: A, C · bug
- 목표: `readerSession_.solverType()=="AnsysMotion"` 과 `loaded_.isModal` 을 `ProcessContext`·`appendSample`·`writeFieldOutputToXml`·`DashResponseInitializer::initialize` 의 인자로 넘기고, `currentAnalysisType=="Dynamic"`(처리기 1 · 작성기 2)·`selectedType=="Dynamic"`(초기화기) 비교를 지운다. `currentAnalysisType` 인자는 Motion 플래그로 대체하고 처리기·작성기·초기화기 시그니처에서 제거한다
- 완료 기준: Motion 배치가 `state_id` 질의를 만든다 — `TestResultProcessor`·`TestResultXmlWriter` 에 Motion 컨텍스트 케이스 추가 · 처리기·작성기·초기화기에 `"Dynamic"` 문자열 비교 0 · 정적·모달 XML 결과 불변
- 변경 범위: model/preprocessor/DashResultProcessor.{h,cpp} · DashResultXmlWriter.{h,cpp} · DashResponseInitializer.{h,cpp} · model/DashAnalysisLauncher.cpp · tests
- 선행: -
- 충돌: PRE-04, PRE-06, PRE-20 · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashResultXmlWriter.cpp → 공유 10건(deps.md 5절) · DashResultXmlWriter.h → PRE-22 PRE-30 PRE-31 PRE-32 · DashResponseInitializer.cpp → PRE-03 · DashResultProcessor.cpp → PRE-23 · DashResultProcessor.h → PRE-23 · PR #658(DashAnalysisLauncher.cpp·DashResultXmlWriter.cpp) · PR #656(DashAnalysisLauncher.cpp·DashResponseInitializer.cpp·DashResultXmlWriter.cpp) · PR #652(DashAnalysisLauncher.cpp) · PR #651(DashAnalysisLauncher.cpp)
- 흡수: #433-9(Motion 판정 통일) · #635(판정 전달) · PRE-c10, PRE-c36, PRE-c38
- 비고: #617 이후 `m_inputs.analysisType` 이 참조 파일 basename 이라 Motion 배치는 코드 경로상 전 샘플 Missing 이다(PRE-c38). `.dfr` 실측은 PRE-01. `contains("modal")` 판정은 입력이 통제되므로 그대로 둔다. `writeModelInfoToXml` 은 받은 `currentAnalysisType` 을 쓰지 않아(태그 기록 0, `DashResultXmlWriter.cpp:1173-1214`) 남길 이유가 없다 — model_info 에 들어갈 것은 PRE-32 의 실제 출처 기록이고 해석 이름이 아니다

#### PRE-08 · `ExtractedKeys::isAnsysMotion` 을 `hasFunctionExpression` 으로 이름을 바로잡는다
- 종류: PR | 규모: S | 태그: C, E · refactor
- 목표: 런처가 싣는 값(함수식 존재)과 위젯이 읽는 의미(Load Step 트리 초기 비활성)에 맞게 필드 이름과 주석을 바꾼다
- 완료 기준: `ExtractedKeys` 에 `isAnsysMotion` 없음 · 위젯 동작 불변(Function Expression 있는 결과에서 트리 초기 비활성)
- 변경 범위: model/preprocessor/DashResultTypes.h · model/DashAnalysisLauncher.{h,cpp} · view/DashAnalysisLauncherWidget.cpp
- 선행: - (이름 정정뿐이라 PRE-07 과 순서 무관 — 같은 파일이라 충돌만 본다)
- 충돌: PRE-07 (같은 파일) · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashAnalysisLauncher.h → LCH-33 PRE-03 PRE-16 PRE-23 PRE-24 PRE-32 PRJ-22 · DashAnalysisLauncherWidget.cpp → PRE-05 PRE-18 PRE-23 PRE-24 PRE-27 · DashResultTypes.h → PRE-16 · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h) · PR #652(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h) · PR #651(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h)
- 흡수: PRE-D5 · PRE-c66

#### PRE-09 · Abaqus 모달 ODB 판별 — `.odb` 도 `GetAnalysisInfo` 로 Static/Modal 을 가를지 실측한다
- 종류: INV | 규모: S | 태그: A · feature
- 목표: 모달 ODB 에서 어댑터 `GetAnalysisInfo` 가 `MODAL` 을 돌려주는지 확인하고, 그렇다면 `.rst` 판별 블록을 `.odb` 에도 적용하는 PR 로 잇는다
- 완료 기준: 실측 결과 — 모달 ODB 의 analysis 값 · 적용 시 `loadPreprocessInputs` 의 판별 범위 결정
- 변경 범위: (PR 시) model/DashAnalysisLauncher.cpp (loadPreprocessInputs) · tests/TestRealResultFiles.cpp
- 선행: PRE-01 (모달 ODB 파일)
- 충돌: B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · TestRealResultFiles.cpp → PRE-06 PRE-16 PRE-17 · PR #658(DashAnalysisLauncher.cpp·TestRealResultFiles.cpp) · PR #656(DashAnalysisLauncher.cpp) · PR #652(DashAnalysisLauncher.cpp) · PR #651(DashAnalysisLauncher.cpp)
- 흡수: #637(Abaqus 모달 경로) · PRE-D4(잔여) · PRE-c44
- 비고: 지금은 `.odb` 가 SupportedResults.defaultType("Static") 으로 고정돼 Abaqus 모달 경로가 없다

#### PRE-10 · Mode Shape 의 변위 항목을 한 곳에서 고른다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: PR #658 이 고친 `DashResultQuery::modeShapeLeaf`(`Displacement`·`U` 두 키만 보고 magnitude 를 `Magnitude` sub-result 로 찾는다)를 변위 항목의 유일한 선택 지점으로 두고, 작성기의 `availableResponses["Displacement"]` 고정 키 2곳(Mode Shape 루프 :384-392 · 원형도 변위 탐색 :984-985)을 같은 함수로 바꾼다. `modeShapeLeaf` 가 못 찾으면 빈 객체를 돌려주고 호출부가 조용히 지나가는 경로를 오류로 끝낸다(다른 항목 대체 없음)
- 완료 기준: Ansys 모달 `.rst` → Mode 1 → `Mode Shape / x` Preview 성공(PRE-01) · Abaqus 모달 배치가 Missing 이 아니다 · 작성기에 `"Displacement"` 리터럴 0 · `TestResultQuery`(modeShapeLeaf 실패 시 오류)·`TestResultXmlWriter`(고정 키 제거) 통과
- 변경 범위: model/preprocessor/DashResultQuery.cpp · DashResultXmlWriter.cpp · tests
- 선행: PRE-06 · PR #658 (`modeShapeLeaf`·배열 이름 조회를 이미 고쳤다 — 그 위에서만 성립한다)
- 충돌: PRE-04, PRE-20 · B2 교집합: DashResultXmlWriter.cpp → 공유 10건(deps.md 5절) · DashResultQuery.cpp → PRE-18 PRE-19 · PR #656(DashResultXmlWriter.cpp)
- 흡수: #637 · PRE-c42(작성기 고정 키) · PRE-c26(배열 선택 몫은 #658) · PRE-c40·PRE-c41 은 PR #658 로 해소됨
- 비고: Ansys 도 operator 는 `U`(field_output_name 은 `Displacement`, tests/TestRealResultFiles.cpp:560). 성분 순서는 `component_labels` 로 확인한다. 미리보기 x·y·z 를 배열 성분 0·1·2 로 자르는 안은 폐기 — #658 이 어댑터에 X·Y·Z sub-result 를 복원했으므로 질의로 지목하면 된다. 표시 계층(`DashFieldPreview`·위젯)은 PRE-18 로 넘겼다

#### PRE-11 · Side Force KPI 가 실패 샘플을 빼고 성분을 `component_labels` 로 고른다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `calculateMaxSideForce` 가 성공 여부를 함께 돌려주고 `processSideForceKPI` 가 실패 샘플을 건너뛴다(#573 규칙). operator 는 `Force/_` 에서, X·Y 는 `component_labels` 위치로 고른다. 쓰지 않는 `cachedTimeSteps` 인자를 정리한다
- 완료 기준: LGE 빌드에서 operator 를 못 찾는 run 은 XML 에 없고 로그에 남는다 · 정상 sideforce.rst 에서 값이 0 이 아니다
- 변경 범위: model/extensions/enterprise/LGE_SpringRule.{h,cpp} · model/DashAnalysisLauncherKPI.cpp
- 선행: -
- 충돌: PRE-12, PRE-21, PRE-22 (KPI.cpp) · B2 교집합: DashAnalysisLauncherKPI.cpp → PRJ-09 UIC-20 · LGE_SpringRule.h → OPT-19 PRE-16 · LGE_SpringRule.cpp → PRE-16
- 흡수: #631 · PRE-c31, PRE-c32
- 비고: grid 배열 이름·성분 순서는 실제 sideforce.rst 로 확인해야 한다(미확인). `DASH_BUILD_LGE_COMPSPRING` 빌드에서만 컴파일된다

#### PRE-12 · Modal Frequency KPI 의 자체 `allProcessFinished` 를 지운다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: 나머지 KPI 4종과 같이 `processFinished` 만 내고 완료 알림은 래퍼에 맡긴다
- 완료 기준: Dev 빌드에서 Modal Frequency 행 1개 Process → Success 팝업 1회 (`BUILD_TARGET=Dev` 가 `BUILD_LGE_CompSpring` 을 ON 으로 켜므로 `DASH_BUILD_LGE_COMPSPRING` 블록이 컴파일된다 — CMakeLists.txt:88-92)
- 변경 범위: model/DashAnalysisLauncherKPI.cpp
- 선행: -
- 충돌: PRE-11, PRE-21, PRE-22 · B2 교집합: DashAnalysisLauncherKPI.cpp → PRJ-09 UIC-20
- 흡수: #636-1 · PRE-c37

#### PRE-13 · KPI + 일반 행 혼합 배치의 완료 알림을 Process 1회당 1번으로 모을지 정한다
- 종류: DEC | 규모: S | 태그: B, D
- 목표: 래퍼가 일반 행까지 처리한 뒤 한 번만 내고 안쪽 `processResults` 가 생성 파일·보고 줄을 돌려줄지, 아니면 #454 워커 전환(PRE-23) 때 작업 단위 완료 신호로 바꾸면서 함께 할지 결정한다
- 완료 기준: 결정 기록 — 알림 횟수 규칙과 구현 위치(래퍼 PR 추가 또는 PRE-23 포함)
- 변경 범위: (결정에 따라) model/DashAnalysisLauncher.cpp (processResultsWithKPI · processResults)
- 선행: PRE-12
- 충돌: PRE-23 · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp) · PR #652(DashAnalysisLauncher.cpp) · PR #651(DashAnalysisLauncher.cpp)
- 흡수: #636-2 · PRE-c39
- 비고: 런처를 링크하는 자동 테스트가 없어 확인은 수동이다

#### PRE-14 · 설정 파일이 비어 있으면 빈 객체에서 시작한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `readRoot` 가 내용이 비었거나 공백뿐인 파일을 없는 파일처럼 다룬다. 깨진 파일(잘림·배열·스칼라)은 지금처럼 보존·거절한다. `invalidExistingConfigIsPreserved` 의 `empty` 행을 새 파일 케이스로 옮긴다
- 완료 기준: `test_analysis_launcher_config` — 0바이트·공백 파일에서 쓰기 성공, 깨진 파일 거절 · 0바이트 `AnalysisLauncher_{Set}.json` 에서 Start 가 취소되지 않는다
- 변경 범위: model/preprocessor/DashAnalysisLauncherConfig.cpp · tests/TestAnalysisLauncherConfig.cpp
- 선행: - (PER-02 헬퍼가 먼저 랜딩하면 `readRoot` 를 헬퍼 호출로 치환하는 형태로)
- 충돌: feat/616-input-format-policy (같은 파일) · PER-02 (읽기 규칙의 정본 — 같은 규칙을 두 곳에 두지 않는다) · B2 교집합: DashAnalysisLauncherConfig.cpp → DOE-03 DOE-16 LCH-16 PRE-15 PRE-27 PRE-32 · TestAnalysisLauncherConfig.cpp → DOE-03 DOE-16 LCH-16 PRE-15 PRE-32
- 흡수: #638-1 · PRE-c45 · PER-c19(증상 1) · PRE-c78
- 비고: #479(직쓰기 크래시)가 0바이트 파일을 만드는 경로다. #601 뒤 수정은 공용 `readRoot` 에 둔다. 읽기 규칙(없음·빈·공백 = 빈 객체, 손상 = 거절·보존)은 PER-02 계약과 같다

#### PRE-15 · 설정 쓰기 실패 사유를 호출부까지 돌려주고 보여 준다
- 종류: PR | 규모: M | 태그: D · feature
- 목표: `readRoot`/`writeRoot` 의 사유를 쓰기 함수가 `QString* error = nullptr` 출력 인자로 돌려주고(반환은 `bool` 유지 — 기존 호출부 무변경), PRE 호출부가 경로 뒤에 붙여 `errorOccurred`/`DashNotify` 로 낸다. `writePreprocessTargetFile` 의 무시된 반환도 알린다
- 완료 기준: 깨진 JSON 에서 Start·Target file 변경 시 모달에 사유(파싱 오류 문구)가 보인다 · `test_analysis_launcher_config` 가 출력 인자의 문구를 검사 · LCH 호출부 3곳(`DashAnalysisLaunchExecutor.cpp` · `DashJobRunner.cpp` · `DashDoeCasesWidget.cpp`)은 무변경 컴파일
- 변경 범위: model/preprocessor/DashAnalysisLauncherConfig.{h,cpp} · model/DashAnalysisLauncher.cpp · tests/TestAnalysisLauncherConfig.cpp
- 선행: PRE-14
- 충돌: feat/616-input-format-policy · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashAnalysisLauncherConfig.cpp → DOE-03 DOE-16 LCH-16 PRE-27 PRE-32 · TestAnalysisLauncherConfig.cpp → DOE-03 DOE-16 LCH-16 PRE-32 · DashAnalysisLauncherConfig.h → DOE-03 LCH-16 PRE-27 PRE-32 · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp) · PR #652(DashAnalysisLauncher.cpp)
- 흡수: #638-2 · PRE-c46 · PER-c19(증상 2) · PRE-c78
- 비고: 반환형을 `QString` 으로 바꾸면 LCH 소유 호출부 4곳(`writeCaseStatus` — DashAnalysisLaunchExecutor.cpp:243 · DashJobRunner.cpp:135, `writeCaseActive` — DashDoeCasesWidget.cpp:367·393)이 같이 바뀌고 LCH-07(같은 호출부를 executor 로 모으는 중)과 동시 수술이 된다. 그래서 출력 인자 방식을 택했다 — LCH-07 과 순서 무관. 사유를 LCH 쪽 모달에도 띄우려면 그때 `보류: LCH 몫` 으로 따로 받는다

#### PRE-16 · 주석·include·죽은 코드를 정리한다
- 종류: PR | 규모: L | 태그: E · refactor
- 목표: `solverType_` 주석을 실제 수명(마지막 `initialize()` 의 솔버)으로, `m_preprocessor`·"Data Upload 표" 주석 정정, 미사용 include(`DashAnalysisLauncher.h` `<filesystem>`, `.cpp` `<cmath>`·`<QProcess>`·`<stdexcept>`·`<QTextStream>`), `ExtractedKeys::frequencies`, 생산 호출 0 인 `DashResultBatch::keepDoneRuns`·`synthesizeRuns`(+테스트)·`LGE_SpringRule::addComponentToQuery` 를 지운다
- 완료 기준: 빌드 오류 0 · 지운 심볼 참조 0 · 테스트 통과
- 변경 범위: model/preprocessor/DashReaderSession.h · DashLoadedResult.h · DashResultTypes.h · DashResultBatch.{h,cpp} · model/DashAnalysisLauncher.{h,cpp} · model/extensions/enterprise/LGE_SpringRule.{h,cpp} · tests/TestResultBatch.cpp · tests/TestRealResultFiles.cpp
- 선행: -
- 충돌: PRE-07 (DashAnalysisLauncher.cpp) · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashAnalysisLauncher.h → LCH-33 PRE-03 PRE-08 PRE-23 PRE-24 PRE-32 PRJ-22 · TestRealResultFiles.cpp → PRE-01 PRE-06 PRE-09 PRE-17 · DashReaderSession.h → PRE-21 PRE-23 PRE-24 · LGE_SpringRule.h → OPT-19 PRE-11 · DashResultBatch.cpp → PRE-30 · DashResultBatch.h → PRE-30 · DashResultTypes.h → PRE-08 · LGE_SpringRule.cpp → PRE-11 · TestResultBatch.cpp → PRE-05 · PR #658(DashAnalysisLauncher.cpp·TestRealResultFiles.cpp) · PR #656(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h) · PR #652(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h) · PR #651(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h)
- 흡수: #638-3 · #638 비차단 3건 · PRE-D10(잔여) · PRE-c47, PRE-c48, PRE-c49, PRE-c50, PRE-c63(잔여), PRE-c07(SpringRule 사본)
- 비고: L 사유 — 한 개념(낡은 주석·미사용 include·죽은 심볼 제거)인데 대상이 11파일에 흩어져 있다. 파일당 변경은 몇 줄이고, 쪼개면 같은 정리 규칙을 두 PR 에 나눠 설명해야 해 유지한다(00-plan 1-2). `TestRealResultFiles` 가 `synthesizeRuns` 를 쓰므로 `DashLauncherRuns` 기반으로 바꾼다. `<algorithm>` 은 `std::max` 가 써서 남긴다. `LGE_SpringRule.cpp` 는 `file(GLOB_RECURSE model/*.cpp)` 로 모든 빌드에서 컴파일되므로(내부 `#ifdef` 없음) 별도 고객사 빌드 확인이 필요 없다

#### PRE-17 · 응답 카탈로그가 호출자의 시간 선택자를 반영한다
- 종류: PR | 규모: M | 태그: A · bug
- 목표: `LegacyJsonPreprocessor::GetAvailableResponses` 가 `ParseTimeQuery` → `MatchTime` 으로 시점을 고르고 그 시점의 응답만 낸다. 매칭 실패는 오류(무필터 폴백 금지). `Responses()` 캐시 키를 (파일, step, substep) 정수로 바꾼다. `GetFieldOutputVtk` 도 같은 시점 한정 목록으로 매칭한다
- 완료 기준: fe-safe 스텝 선택 시 Name 목록이 수명 결과만 (#658 뒤에는 sub-result 형제 키가 함께 세어지므로 기대 개수는 PRE-01 실측으로 고정한다) · 빈 질의(`{}`)는 지금처럼 전체 · `TestRealResultFiles` 통과
- 변경 범위: model/preprocessor/wrapper/LegacyJsonPreprocessor.{h,cpp} · tests/TestRealResultFiles.cpp
- 선행: PRE-01 (실측 파일) · PR #658 (어댑터를 v3 로 재작성 — `TimeStep`·`ResponseEntry` 타입과 카탈로그 발행 구조가 바뀌고 `GetAvailableResponses`·`GetFieldOutputVtk` 본문이 그 위에 선다. `(void)keyString` 은 #658 도 그대로 둔다)
- 충돌: B2 교집합: TestRealResultFiles.cpp → PRE-06 PRE-09 PRE-16
- 흡수: #494-A · #494 To-be 1·2·5 · PRE-c14, PRE-c18
- 비고: 도메인까지 넘기는 것은 Preprocessor `3ff07ff` 머지가 선행(EXT, PRE-c23) — 이 항목은 시간 선택자만 넘겨 그 선행 없이 간다. Motion(빈 질의)·Function Expression 은 영향 없음을 확인한다

#### PRE-18 · 응답 카탈로그에 성분 축(sub-result)을 신설하고 질의로 지목한다
- 종류: PR | 규모: M | 태그: A, C · feature
- 목표: PR #658 이 어댑터 발행(`_` 옆 형제 키)·`MatchResponse` 의 `sub_result` 지목·미리보기/작성기 질의의 `sub_result` 적재를 이미 했다. 남은 **표시 계층**을 그 위에 맞춘다 — 위젯의 `"_"`↔`Magnitude` 변환 3곳을 지워 실제 `Magnitude` sub-result 와 겹치지 않게 하고, 미리보기의 `sqrt(Σv²)` 축약(`DashFieldPreview::selectScalars` 의 `_magnitude` 합성)을 발행된 성분 선택으로 바꾸고, `responseLeaf` 의 `keys().first()` 폴백을 지운다
- 완료 기준: 위젯 Name 목록에 `Magnitude` 가 한 번만 나오고 선택이 그 sub-result 질의로 간다 · 성분 선택 시 `[N, 1]` · `_magnitude` 합성 배열 0, 텐서에 `sqrt(Σv²)` 를 칠하는 경로 없음 · `TestResultQuery`(responseLeaf 폴백 제거)·`TestFieldPreview` 통과
- 변경 범위: model/preprocessor/DashResultQuery.cpp · DashFieldPreview.{h,cpp} · view/DashAnalysisLauncherWidget.cpp · tests
- 선행: PR #658 (어댑터 발행·질의 지목 — 이것이 없으면 맞출 대상이 없다) · PRE-10 (Mode Shape 이름 규칙이 먼저 한 곳으로)
- 충돌: B2 교집합: DashAnalysisLauncherWidget.cpp → PRE-05 PRE-08 PRE-23 PRE-24 PRE-27 · DashResultQuery.cpp → PRE-19
- 흡수: #494-B · #494 To-be 3·6·7 · PRE-c19, PRE-c20, PRE-c21 · PRE-c16·PRE-c17(#494 To-be 4)는 PR #658 로 해소됨
- 비고: "발행과 표시를 한 PR 로" 라는 원 근거는 #658 이 발행을 먼저 올려 성립하지 않는다 — #658 머지 시점부터 위젯의 `"_"`↔`Magnitude` 겹침(PRE-c21)이 실제로 살아 있으므로 이 항목이 그 수선이다. #658 의 `regularNames` 는 형제가 있을 때 목록에서 `_` 를 빼는 데까지만 갔다. 선행에서 PRE-17 을 뺐다 — 어댑터(`LegacyJsonPreprocessor`)를 더 이상 고치지 않으므로 같은 함수 제약이 없다. 텐서 불변량(von Mises)은 Abaqus 미발행이라 범위 밖(#494). 내보내기는 `[N, nComp]` 원본이라 영향 없다

#### PRE-19 · `step_name` 을 Load Step 트리까지 전달한다
- 종류: PR | 규모: S | 태그: D · feature
- 목표: `DashResultKeys::parseTimeSteps` 가 어댑터의 `step_name` 을 읽어 트리 라벨에 싣고, `parseLoadStep` 이 그 라벨을 되읽는다
- 완료 기준: fe-safe ODB 에서 Load Step 트리에 스텝 이름이 보인다 · `TestResultKeys`·`TestResultQuery` 에 라벨 왕복 케이스
- 변경 범위: model/preprocessor/DashResultKeys.cpp · DashResultQuery.cpp · tests
- 선행: PRE-01
- 충돌: PRE-05 (위젯 조립 규칙) · B2 교집합: DashResultKeys.cpp → PRE-03 PRE-04 · DashResultQuery.cpp → PRE-10 PRE-18 · PR #658(DashResultKeys.cpp·DashResultQuery.cpp) · PR #656(DashResultKeys.cpp)
- 흡수: #494-A 부수 · #494 To-be 8 · PRE-c15

#### PRE-20 · 결과 XML 작성기의 컴포넌트 항을 `DashResultQuery::putComponentTerm` 으로 바꾼다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `DashResultXmlWriter::addComponentToQuery` 를 지우고 PRE-07 이 넘긴 Motion 플래그로 `putComponentTerm` 을 부른다 — Motion 질의에 `entity_name` 이 실린다
- 완료 기준: `TestResultXmlWriter` 에 Motion 컴포넌트 케이스(질의에 `entity_name`) · Mechanical 질의 불변 · `.dfr` DOE 에서 BODY 하나 Process → XML 노드 수가 전체 모델보다 작다(PRE-01)
- 변경 범위: model/preprocessor/DashResultXmlWriter.{h,cpp} · tests/TestResultXmlWriter.cpp
- 선행: PRE-07
- 충돌: PRE-06, PRE-10, PRE-04 · B2 교집합: DashResultXmlWriter.cpp → 공유 10건(deps.md 5절) · DashResultXmlWriter.h → PRE-22 PRE-30 PRE-31 PRE-32 · TestResultXmlWriter.cpp → PRE-31 PRE-32 · PR #658(DashResultXmlWriter.cpp·TestResultXmlWriter.cpp) · PR #656(DashResultXmlWriter.cpp·TestResultXmlWriter.cpp)
- 흡수: #635 · #433-9(컴포넌트 항) · PRE-c07, PRE-c35, PRE-c81
- 비고: `ILJIN_TensionlinkRule::addComponentToQuery` 사본은 Abaqus 전용이라 그대로 둔다. `putComponentTerm` 의 `entity_type`·`body_name` 분기는 어댑터가 `entity_type` 을 발행하지 않아 도달하지 않는다(`wrapper/LegacyJsonPreprocessor.cpp:466-472` 주석이 명시) — 발행은 외부 어댑터 몫(#334, 보드 밖)이라 분기는 그대로 두고 완료 기준에서 뺀다(PRE-c81)

#### PRE-21 · 배치 뒤 리더 입력 복원을 `DashReaderSession::Work` 종료 한 곳으로 모은다
- 종류: PR | 규모: M | 태그: A, B · bug
- 목표: 최상위 `Work` 가 Keep 으로 끝날 때 `loadedInputs_` 를 재오픈한다. KPI 4종의 `restoreLoadedInputs()` 호출을 지우고 Modal KPI·일반 `processResults` 도 같은 규칙을 탄다. `ensureForLoadedInputs(false)` 는 리더가 있으면 재오픈하지 않는다는 계약을 헤더에 적는다
- 완료 기준: 일반 Process 뒤 Load Step 클릭의 Name 목록이 Load 한 파일 기준(마지막 run 파일 아님) · `TestReaderSession` 에 Work 종료 복원 케이스 · KPI 4종 뒤 미리보기 불변
- 변경 범위: model/preprocessor/DashReaderSession.h · model/DashAnalysisLauncher.cpp · model/DashAnalysisLauncherKPI.cpp · tests/TestReaderSession.cpp
- 선행: -
- 충돌: PRE-11, PRE-12, PRE-22 (KPI.cpp) · PRE-23 · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashAnalysisLauncherKPI.cpp → PRJ-09 UIC-20 · DashReaderSession.h → PRE-16 PRE-24 · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp) · PR #652(DashAnalysisLauncher.cpp) · PR #651(DashAnalysisLauncher.cpp)
- 흡수: PRE-D6 · PRE-c70
- 비고: 복원 실패는 지금처럼 `faulted_` 로 리더를 폐기한다

#### PRE-22 · KPI 5종의 공통 프레임(매핑·parameterInfo·출력 폴더·샘플 프레임·model_info·저장)을 뽑는다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: 5함수가 복제한 입력 매핑·`loadParameterInfo`·`moduleDir`·샘플 dict 프레임(구 형식 폴백 + `writeParametersToXml` + 스칼라 항목)·`responseInfo`/file_name 루프·파일 저장을 `DashAnalysisLauncherKPI.cpp` 안의 헬퍼(또는 `DashResultXmlWriter` 스칼라 샘플 API)로 모은다. 계산 규칙은 건드리지 않는다
- 완료 기준: 두 고객사 빌드 모두 빌드 오류 0 · 같은 입력으로 생성한 KPI XML 바이트 동일
- 변경 범위: model/DashAnalysisLauncherKPI.cpp · model/preprocessor/DashResultXmlWriter.{h,cpp}
- 선행: PRE-11, PRE-12, PRE-21 (동작 변경 먼저)
- 충돌: PRE-23 · B2 교집합: DashResultXmlWriter.cpp → 공유 10건(deps.md 5절) · DashResultXmlWriter.h → PRE-04 PRE-07 PRE-20 PRE-30 PRE-31 PRE-32 · DashAnalysisLauncherKPI.cpp → PRJ-09 UIC-20 · PR #658(DashResultXmlWriter.cpp) · PR #656(DashResultXmlWriter.cpp)
- 흡수: PRE-D11 · PRE-c67
- 비고: `BUILD_TARGET=Dev` 가 `BUILD_LGE_CompSpring`·`BUILD_ILJIN_TensionLink` 를 함께 켜므로(CMakeLists.txt:88-92) Dev 빌드 하나로 두 고객사 블록이 컴파일된다 — 고객사 단독 타깃 빌드는 선택 확인

#### PRE-23 · 배치(`processResults`·`DashResultProcessor`)를 워커로 옮기고 펌핑 14곳을 지운다
- 종류: PR | 규모: L | 태그: B · refactor
- 목표: 요청 루프와 샘플 루프를 `controller/async` Job 으로 옮기고 결과·보고는 신호로 돌려준다. `processResults` 6곳·`DashResultProcessor` 8곳의 `processEvents` 를 지우고, 위젯의 `m_isProcessing` 가드·`rejectIfReaderBusy` 를 Job 상태로 바꾼다. `DashReaderSession` 의 스레드 소속을 명시한다
- 완료 기준: PRE 영역 비KPI `processEvents` 0 (적재 2곳 제외, PRE-24) · 배치 중 Add/Remove/Preview 가 재진입하지 않고 거절·대기 · 배치 중 상태바 진행 표시·취소 버튼이 EXE-07 규약대로 동작하고 Process 버튼은 EXE-09 가드로 비활성(#463) · 단일 파일/DOE·일부 누락·실패 후 재시도·KPI 혼합 시나리오의 XML 동일 · `TestResultProcessor` 통과
- 변경 범위: model/DashAnalysisLauncher.{h,cpp} · model/preprocessor/DashResultProcessor.{h,cpp} · DashReaderSession.h · view/DashAnalysisLauncherWidget.{h,cpp} · controller/async 소비
- 선행: PRE-04, PRE-07 (#433 9단계 코드 잔여 — 런처·처리기 같은 파일 동시 수술 금지 #239), PRE-13, PRE-21 · EXE-01 (레인 결정 — #454 가 어느 레인에 제출하는지) · EXE-02 (취소) · EXE-07 (진행 표시 규약) · EXE-09 (가드 헬퍼)
- 충돌: PRE-04, PRE-22 · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashAnalysisLauncher.h → LCH-33 PRE-03 PRE-08 PRE-16 PRE-24 PRE-32 PRJ-22 · DashAnalysisLauncherWidget.cpp → PRE-05 PRE-08 PRE-18 PRE-24 PRE-27 · DashReaderSession.h → PRE-16 PRE-24 · DashAnalysisLauncherWidget.h → LCH-01 PRE-05 · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h) · PR #652(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h) · PR #651(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h·DashAnalysisLauncherWidget.h)
- 흡수: #454(배치 14곳) · PRE-D3 · PRE-c11(배치), PRE-c12, PRE-c71 · #463(PRE 적용 — 진행 표시·취소·가드) · EXE-c23 · EXE-c48 · EXE-c43(PRE-D3) · PRE-c80
- 비고: L 사유 — 실행 모델 전환이라 처리기·런처·위젯 가드·리더 세션을 한 번에 바꿔야 중간 상태가 없다. 선행에서 PRE-02(#433 종료 문서 작업)를 뺐다 — 그 선행은 PRE-01 의 구할 수 없는 실측 파일까지 사슬로 끌고 오는데, #433·#454 가 금한 것은 같은 파일 동시 수술이라 코드 항목(PRE-04·07)으로 충분하다. KPI 7곳은 #454 결정대로 보존(래퍼가 KPI 를 동기로 먼저 돌리는 구조도 유지). 완료 판정은 #453(기각) 대신 이 항목의 기준으로

#### PRE-24 · 적재(`loadPreprocessInputs`·`selectTargetFile`·`.rst` 판별)를 워커로 옮기고 펌핑 2곳을 지운다
- 종류: PR | 규모: M | 태그: B · refactor
- 목표: 결과 파일 스캔·리더 생성·GetTimeSteps/Geometries/Responses 조회를 Job 으로 옮기고 `ExcludeUserInputEvents` 펌핑 2곳을 지운다. 로딩 인디케이터는 Job 시작·종료 신호로
- 완료 기준: PRE 영역 비KPI `processEvents` 0 · Preprocess 탭 진입 중 Set 전환·Target file 변경이 거절·대기 · Load 실패 뒤 재시도 계약(#573) 유지
- 변경 범위: model/DashAnalysisLauncher.{h,cpp} · model/preprocessor/DashReaderSession.h · view/DashAnalysisLauncherWidget.cpp
- 선행: PRE-23
- 충돌: B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashAnalysisLauncher.h → LCH-33 PRE-03 PRE-08 PRE-16 PRE-32 PRJ-22 · DashAnalysisLauncherWidget.cpp → PRE-05 PRE-08 PRE-18 PRE-27 · DashReaderSession.h → PRE-16 PRE-21 · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h) · PR #652(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h) · PR #651(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h)
- 흡수: #454(적재 2곳) · PRE-c11(적재) · EXE-c48 · PRE-c80

#### PRE-25 · 확장자→솔버 라우팅을 `SupportedResults` 기준으로 닫는다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: 확장자→솔버 선택을 `SupportedResults.solverName` 을 읽는 순수 함수(`DashTargetFiles::solverOf`)로 빼고, `createPreprocessor` 는 그 결과로 플러그인만 올린다 — 지원 솔버가 없는 확장자(`.op2`)는 오류로 거절하고 도달하지 않는 `res`·`dfsxml` 분기를 지운다
- 완료 기준: `tests/TestTargetFiles.cpp` 에 `solverOf` 케이스 — `.rst`→AnsysMechanical · `.dfr`→AnsysMotion · `.odb`→Abaqus · `.op2`·`res`·`dfsxml`→미지원(빈 값) · `createPreprocessor` 에 확장자 리터럴 0 · 수동 1회(`.rst` Load 불변)
- 변경 범위: model/preprocessor/DashTargetFiles.{h,cpp} · model/DashAnalysisLauncher.cpp (createPreprocessor) · tests/TestTargetFiles.cpp
- 선행: -
- 충돌: PRE-07 · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp) · PR #652(DashAnalysisLauncher.cpp) · PR #651(DashAnalysisLauncher.cpp)
- 흡수: PRE-U1 · PRE-U2 · PRE-c64, PRE-c73
- 비고: "`.op2` 를 Load 하면 오류" 는 앱에서 재현할 수 없다 — Preprocess 입력은 러너가 Done 에 기록한 resultFiles 뿐(#640)이고 NASTRAN 러너가 없다. `createPreprocessor` 는 `DashManager` 솔버 경로를 읽는 멤버라 Qt Core 테스트가 부를 수 없으므로, 확인 가능한 지점을 순수 함수로 뺀다(`DashTargetFiles` 는 이미 Qt Core 전용 · `test_target_files` 존재). `.op2` 를 목록(AnalysisFileDefines.h)·`DashManager` 솔버 목록에서 뺄지는 LCH·UIC 결정(접점)

#### PRE-26 · Output Response 기록을 재진입 복원으로 살릴지 쓰기를 없앨지 정한다
- 종류: DEC | 규모: S | 태그: A, C
- 목표: `Output Response` 가 쓰기 전용(읽는 코드 0)이고 KPI 행은 기록도 안 되며 PM 이 `readRoot`/`writeRoot` 밖에서 직쓰기한다. (a) 재진입 시 표 복원(KPI 행 포함) 구현 또는 (b) 기록 제거 중 하나로 정한다
- 완료 기준: 결정 기록 — 선택지·근거·PRE-27 의 범위
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: PRE-D7 · PRE-D8 · PRE-c61, PRE-c62, PRE-c51
- 비고: #601 뒤 Preprocess 는 Launcher 결과를 다시 읽으므로 표만 복원하면 되지만, Target file 변경·입력 변경 시 표를 비우는 현재 규칙(PRE-c68)과 맞춰야 한다

#### PRE-27 · Output Response 기록 결정을 반영한다
- 종류: PR | 규모: M | 태그: A, C · feature
- 목표: (a) 복원 — PM 에 읽기 추가, `refreshPreprocessTab` 이 입력이 같으면 표를 복원, `addKpiToResultTable` 도 저장, 저장은 `DashAnalysisLauncherConfig` 의 `readRoot`/`writeRoot` 경유. (b) 제거 — `saveOutputResponse` 와 호출 3곳 삭제
- 완료 기준: (a) Set 재진입 시 Output Response 행(KPI 포함)이 돌아온다 · 설정 파일의 다른 키 보존 (b) `Output Response` 키 쓰기 0
- 변경 범위: viewmodel/DashAnalysisLauncherPresentationModel.{h,cpp} · view/DashAnalysisLauncherWidget.cpp · model/preprocessor/DashAnalysisLauncherConfig.{h,cpp}
- 선행: PRE-26, PRE-14 · PER-02 ((a) 일 때 — 저장은 헬퍼 경유)
- 충돌: PRE-05 (위젯) · B2 교집합: DashAnalysisLauncherConfig.cpp → DOE-03 DOE-16 LCH-16 PRE-15 PRE-32 · DashAnalysisLauncherWidget.cpp → PRE-08 PRE-18 PRE-23 PRE-24 · DashAnalysisLauncherConfig.h → DOE-03 LCH-16 PRE-15 PRE-32 · PR #651(DashAnalysisLauncherConfig.cpp·DashAnalysisLauncherConfig.h)
- 흡수: PRE-D7 · PRE-D8 · PRE-c61, PRE-c62, PRE-c51 · #479 · #478 (PER 직쓰기 이행의 PRE 몫) · PER-c26 · PRE-c79
- 비고: (a) 든 (b) 든 `saveOutputResponse` 의 `QFile` 직쓰기는 사라진다 — PER 의 직쓰기 22지점 중 PRE 몫 1지점

#### PRE-28 · Preprocess XML 의 실측 파일 크기·생성 피크 메모리·샘플 수 증가율을 수집한다
- 종류: INV | 규모: S | 태그: F · perf
- 목표: 실기 DOE 산출물(정적 `.rst`·`.odb`, 모핑 N 케이스)에서 응답 수·샘플 수별 XML 크기와 `processResults` 피크 메모리를 재고 base64·DOM 누적·요청 수 세 겹의 기여를 나눈다
- 완료 기준: 실측 결과 — 표(샘플 수 × 응답 수 → 크기·피크) 와 #411 부분 대안 3종(위상 1회·paddingTarget·node_location 1회)의 예상 절감
- 변경 범위: 측정 스크립트·기록만
- 선행: -
- 충돌: -
- 흡수: #411(먼저 할 것) · PRE-c57
- 비고: 실기 산출물 필요(미확인). PER-03 ⑦ 이 "결과 XML 의 키 작성" 참조처로 PRE-28·29 를 적었으나(03-items/PER.md 완료 기준 2) **이 항목의 선행은 아니다** — 크기·피크 메모리 실측은 저장 포맷 버전 키 규약과 무관하고, 규약 수용은 PRE-29(결정)·PRE-30(구현) 몫이다. PER-03 선행 등재는 PRE-29 에만 넣었다

#### PRE-29 · Preprocess XML 의 단위·중복·포맷을 정한다
- 종류: DEC | 규모: S | 태그: A, C
- 목표: #643 1차(Set 단위 파일 1개 + 응답 추가)·2차(입력 식별과 버전별 이어쓰기/덮어쓰기 조건 검토)·중복 1회 저장·HDF5(vtkHDF) 전환 여부를 결정한다. 결정 입력: **DeepOpt 리더 계약 — `root` 의 첫 자식만 학습 데이터로 읽고 샘플 dict 는 동형이어야 한다(BLD-c26·BLD-14 비고 · 위키 Model-Builder-XML-DeepOpt-Pipeline)**, Builder 다중 part 포맷(BLD), `vtkIOHDF` 가용(DEV), 저장 포맷 버전 키 A3/N9(**PER-03 ⑦** — 결과 XML 이 같은 규약을 쓰는지), `DashXmlParser` 전환(ANA), HDF5·중복 1회 판단에는 PRE-28 수치, 현행 포맷 기준선에는 **PR #658** (주파수 `dict_item` 에 `quantity`·`unit` 속성 + Eigenvalue 는 무차원 `Eigenvalue` 키, 벡터 `resItem` 에 `component_labels` 속성 — 머지되면 기준선이 이것이다)
- 완료 기준: 파일 단위·중복·포맷·소비자 수용과 구 포맷 판독 호환 범위를 결정한다. setId·deck 식별자·버전을 구분하고 이어쓰기 허용 조건은 팀 논의로 확정한다. 구 포맷 판독 가능과 필수 출처 없는 산출물의 실행 허용을 구분하며 출처 자동 마이그레이션은 하지 않는다. DeepOpt의 model_info 위치·샘플 dict 동형을 대조한다.
- 변경 범위: -
- 선행: PER-03 (저장 포맷 버전 키 규약 ⑦ — 결과 XML 이 그 규약을 쓰는지 정해져야 포맷 결정이 닫힌다) · PR #658 (포맷 기준선). 1차 포맷·2차 식별자 결정 자체는 실측과 무관하고, HDF5 전환·중복 1회만 PRE-28 수치를 본다 — #643 은 W5 배정이라 측정 대기로 묶지 않는다
- 충돌: -
- 흡수: #643(1차·2차·추가 1·3) · #411(결정 1~4) · PRE-c52(결정부), PRE-c53, PRE-c55(결정부) · 범위밖 입력 PRE-c54, PRE-c56, PRE-c58, PRE-c59, PRE-c60 · ANA-c30 · PRE-c77 (ANA 파서 전환 검토 — 같은 결정 입력)
- 비고: #643·#411의 상세 범위와 이어쓰기 기준은 이슈 개정 이력의 추가 개정 계획이며 GitHub 반영 완료로 취급하지 않는다. #368의 PRE-32가 출처 기록·판독을 맡고 #650은 버전·최신성을 맡는다. 같은 model_info 위치를 쓰더라도 조합 ID 두 키나 최초 입력 핀을 전제로 삼지 않으며 상호 불필요한 선행을 만들지 않는다.

#### PRE-30 · 결과 XML 을 Set 단위 파일 하나에 응답을 추가하는 방식으로 쓴다
- 종류: PR | 규모: M | 태그: A, C · feature
- 목표: processResults가 Set 파일에 응답을 추가하는 저장 구조를 구현한다. Set 식별은 setId, deck 식별과 DOE tableId는 각자 역할을 유지한다. 출처 필드는 PRE-32의 #368 공통 계약을 사용하며 입력 변경 시 이어쓰기·덮어쓰기 조건은 PRE-29의 팀 논의 결정 뒤 적용한다.
- 완료 기준: 응답 2개를 Set 파일 1개에 저장하고 DeepOpt의 root 첫 자식·샘플 dict 동형을 보존한다. 팀이 확정한 이어쓰기 조건과 실제 출처 기록을 검증한다. 구산출물의 누락 출처를 이름·경로로 추론하지 않는다. BLD-14·ANA의 포맷 수용과 조율한다.
- 변경 범위: model/DashAnalysisLauncher.cpp (processResults) · model/preprocessor/DashResultBatch.{h,cpp} · DashResultXmlWriter.{h,cpp} · tests
- 선행: PRE-29
- 충돌: PRE-04, PRE-06, PRE-23 (processResults — 먼저 랜딩한 쪽에 리베이스) · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashResultXmlWriter.cpp → 공유 10건(deps.md 5절) · DashResultXmlWriter.h → PRE-07 PRE-20 PRE-22 PRE-31 PRE-32 · DashResultBatch.cpp → PRE-16 · DashResultBatch.h → PRE-16 · PR #658(DashAnalysisLauncher.cpp·DashResultXmlWriter.cpp) · PR #656(DashAnalysisLauncher.cpp·DashResultXmlWriter.cpp) · PR #652(DashAnalysisLauncher.cpp) · PR #651(DashAnalysisLauncher.cpp)
- 흡수: #643(1차·2차) · PRE-c52, PRE-c53
- 비고: 읽는 쪽(DashXmlParser · Builder · Analyzer) 변경은 BLD-14·ANA 항목 몫. 선행에서 PRE-23 을 뺐다 — #643 은 W5 배정인데 PRE-23 은 EXE 8건을 선행으로 둔 Backlog 라 1차 포맷이 워커 전환 뒤로 밀린다. 같은 `processResults` 를 고치므로 충돌로만 둔다. DeepOpt 는 `root` 첫 자식만 읽으므로 응답 추가는 샘플 dict 안의 키로만 하고 `model_info` 를 앞으로 옮기지 않는다

#### PRE-31 · 위상(connectivity · node_location)을 파일당 1회만 쓰고 paddingTarget 을 실제 maxStride 로 둔다
- 종류: PR | 규모: S | 태그: A · perf
- 목표: 작성기가 샘플마다 리셋하는 `m_nodeLocationWritten`·`m_connectivityWritten` 을 파일 단위로 올리고(모핑은 위상 불변, 조건-only·CAD 는 node_location 도 불변), `maxStride < 8 ? 8` 의 최소 8 규칙을 실제 maxStride 로 바꾼다
- 완료 기준: tet 메시 DOE 의 XML 크기 감소(PRE-28 기준) · 샘플 0 에만 위상을 두어도 샘플 dict 동형 전제를 깨지 않음을 DeepOpt 계약과 대조(PRE-29 결정) · `TestResultXmlWriter` 통과 · 파서 쪽 수용 — `보류: BLD 몫`(샘플 0 위상으로 나머지 읽기) · `보류: ANA 몫`(`DashXmlParser`)
- 변경 범위: model/preprocessor/DashResultXmlWriter.{h,cpp} · tests/TestResultXmlWriter.cpp
- 선행: PRE-29 (소비자 전제 확인 — DeepOpt 가 샘플별 위상을 전제하는지 포함)
- 충돌: PRE-30, PRE-06, PRE-10, PRE-04 · B2 교집합: DashResultXmlWriter.cpp → 공유 10건(deps.md 5절) · DashResultXmlWriter.h → PRE-07 PRE-20 PRE-22 PRE-32 · TestResultXmlWriter.cpp → PRE-20 PRE-32 · PR #658(DashResultXmlWriter.cpp·TestResultXmlWriter.cpp) · PR #656(DashResultXmlWriter.cpp·TestResultXmlWriter.cpp)
- 흡수: #643 추가 2 · #411 부분 대안 · PRE-c55
- 비고: 포맷 변경이므로 구 XML 읽기 호환은 PRE-29 의 마이그레이션 방침을 따른다. 샘플 1..N 의 dict 구조가 샘플 0 과 달라지므로 DeepOpt 의 "샘플 dict 동형" 전제에 걸린다 — PRE-29 가 그 계약을 확인하지 않으면 착수하지 않는다

#### PRE-32 · Launcher가 실제 run 출처를 검증하고 결과 XML에 기록한다
- 종류: PR | 규모: L | 태그: C, A · feature
- 목표: #368 계약으로 DOE 스냅샷과 실제 입력 run의 출처를 판독·검증하고 결과 XML model_info에 생성 Launcher setId·입력 DOE setId·상류 출처·세부 선택·deck 정보를 기록한다. 현재 Launcher setId를 유지하며 다른 DOE Set을 선택할 수 있다. 선택 변경은 기존 XML 출처를 변경하지 않고 결과 덮어쓰기 시 실제 출처를 함께 갱신한다.
- 완료 기준: ① 결과 XML 출처가 실제 사용한 스냅샷·run과 일치 ② 다른 유효한 DOE setId로 참조 변경·재실행 가능, 선택만 바꾸면 기존 산출물 불변 ③ priorSamples는 실제 출처와 선택 관계를 검증하며 조합 ID 동일성을 요구하지 않음 ④ 필수 출처 누락·해석 불가 run은 재생성 안내, live DOE JSON 추론·자동 이관 금지 ⑤ XML·설정·run 테스트에서 왕복과 오류 사유 확인.
- 변경 범위: model/DashAnalysisLauncher.{h,cpp} · model/preprocessor/DashResultXmlWriter.{h,cpp} · model/preprocessor/DashAnalysisLauncherConfig.{h,cpp} · model/preprocessor/DashLauncherRuns.{h,cpp} · tests/TestResultXmlWriter.cpp · tests/TestAnalysisLauncherConfig.cpp · tests/TestLauncherRuns.cpp
- 선행: DOE-16
- 충돌: PRE-30 (같은 `model_info` 자리 — 포맷 구조와 출처 기록의 적용 접점만 조율) · PRE-04 · PRE-06 · PRE-23 (processResults) · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashResultXmlWriter.cpp → 공유 10건(deps.md 5절) · DashAnalysisLauncher.h → LCH-33 PRE-03 PRE-08 PRE-16 PRE-24 PRJ-22 · DashAnalysisLauncherConfig.cpp → DOE-03 LCH-16 PRE-14 PRE-15 PRE-27 · DashResultXmlWriter.h → PRE-07 PRE-20 PRE-22 PRE-31 · TestAnalysisLauncherConfig.cpp → DOE-03 LCH-16 PRE-14 PRE-15 · DashAnalysisLauncherConfig.h → DOE-03 LCH-16 PRE-15 PRE-27 · TestResultXmlWriter.cpp → PRE-20 PRE-31 · DashLauncherRuns.cpp → LCH-09 · DashLauncherRuns.h → LCH-30 · PR #658(DashAnalysisLauncher.cpp·DashResultXmlWriter.cpp·TestResultXmlWriter.cpp) · PR #656(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h·DashResultXmlWriter.cpp·TestResultXmlWriter.cpp) · PR #652(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h) · PR #651(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h·DashAnalysisLauncherConfig.cpp·DashAnalysisLauncherConfig.h·TestAnalysisLauncherConfig.cpp)
- 흡수: #368 Phase 2(T21) · LCH-c36 · PRE-c76
- 비고: 기존 tableId 기반 run 선택은 유지하되 새 상류 입력 선택을 최초 값으로 잠그지 않는다. DOE-16은 스냅샷 전파, LCH-33은 실행 직전 검증, 본 항목은 결과 입력 검증·출처 기록을 담당한다. #643 포맷·이어쓰기 조건은 PRE-29의 별도 논의이며 출처 계약과 서로 불필요한 선행을 만들지 않는다.

### BLD — Model Builder

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> 기준 dev @ b08a91b3. 원천·판정은 02-claims/BLD.md. 약어는 claims 와 같다 (`M` `MCU` `W` `MW` `Base` `PM` `CH` `LTH`).
> 열린 PR 7건 중 머지 대상 6건 (#651 #652 #654 #655 #656 #658) — #530 은 재업로드 노선이라 머지 대상이 아니다 (05-final/decisions.md ⑩·②). BLD **본체 파일**(M · MCU · W · MW · Base · PM · CH · LTH · DashXmlTailLocator.h)을 만지는 머지 대상 PR 은 **0건**이고, 겹치는 것은 `tests/CMakeLists.txt`(#651 #652 #654 #655 — BLD-19) 뿐이다. **#656·#658 은 BLD 항목의 변경 범위와 교집합 0** 이라 선행 추가 없음 — #656 은 런처·작성기 공용 함수 추출로 XML 출력이 불변이고, #658 은 `DashResultXmlWriter` 의 배열 선택 로직과 응답 `dict_item` 속성(`quantity`·`unit`·`component_labels`)·모달 응답 키(`Eigenvalue`)를 바꾸지만 BLD 함수 본문은 건드리지 않는다 (hunk 확인, BLD-14 비고).
> #368 생산 계약은 BLD-20에서 model_info.json 생성까지 담당하고 #685가 소비를 이어받는다. PR #530의 당시 재업로드 결정은 보존하되 새 코드는 현행 계약으로 작성한다. 충돌은 같은 수정 지점의 적용 순서를 조율한다.

#### BLD-01 · MCU Data Label 을 재진입 시 되읽는다 — Dataset 배열 → 파일 표·라벨 표 복원
- 종류: PR | 규모: M | 태그: A, C · bug
- 목표: `DashModelBuilderMCU` 가 `Data Label.Dataset` 배열을 `{path, mode}` 목록으로 보관하고(베이스 `loadDataLabelConfig` 의 가상 훅 또는 재정의), `MW:onConfigLoaded` 가 베이스 XML 로더를 부르는 대신 파일 표를 그 목록으로 복원한 뒤 `onLoadButtonClickedMCU` 와 같은 헤더 재구성으로 Input/Output 표를 만들고 저장된 체크·reduction 을 적용한다. `populateIoTableWithFixedHeaders` 는 목록이 비었을 때만 쓴다. MCU 학습 시작의 XML 이식 분기는 CSV 를 열지 않도록 MCU 에서 제외한다.
- 완료 기준: (1) MCU Set 에서 파일 2개 추가·[Load]·체크 변경·[Set Dataset] 뒤 다른 Set 을 갔다 돌아오면 파일 표 2행(경로·Mode·State)과 Input/Output 체크·reduction 이 그대로다 (2) MCU 학습 시작 로그에 "Dataset path is empty" · "Failed to load model_info from XML" 이 없다 (3) Sim Set 의 복원 동작은 변하지 않는다
- 변경 범위: model/DashModelBuilder.h · model/DashModelBuilderMCU.h · model/DashModelBuilderMCU.cpp · view/DashModelBuilderMCUWidget.h · view/DashModelBuilderMCUWidget.cpp · viewmodel/DashModelBuilderPresentationModel.h · viewmodel/DashModelBuilderPresentationModel.cpp
- 선행: -
- 충돌: BLD-02 (M:loadDataLabelConfig) · BLD-09 · BLD-10 · BLD-12 (MW) · BLD-20 (M.h 가상 훅 인접) · B2 교집합: DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelBuilderMCU.cpp → BLD-13 BLD-17 BLD-18 PRJ-09 UIC-20 · DashModelBuilder.h → BLD-04 BLD-05 BLD-13 BLD-14 BLD-15 · DashModelBuilderMCU.h → BLD-15 · DashModelBuilderPresentationModel.cpp → BLD-16
- 흡수: BLD-D12 · BLD-D9(Dataset 형) · BLD-c08, BLD-c13
- 비고: 헤더 재구성(첫 유효 파일 헤더 → Input N-1 · Output 마지막 열)을 `onLoadButtonClickedMCU` 와 공유 함수로 뽑는다(동작 불변). 배열 파싱은 `CH:parseDataLabelSection` 의 배열 분기를 재사용한다. Dataset 형 차이(문자열 vs 배열)는 입력 모델의 반영이므로 유지하고 로더가 둘 다 읽는 것으로 종결(BLD-11 결정 항목에서 "유지" 로 기록).

#### BLD-02 · Data Label 섹션 읽기를 쓰기와 대칭으로 만든다 — parseDataLabelSection 배선 + 키 대조 sanitize 통일
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `M:loadDataLabelConfig` 의 수동 파싱을 `CH:parseDataLabelSection` · `parseConfigurationSection` 호출로 바꿔 Output `transformation` 이 읽히게 하고, `Base:updateLabelTable` 의 저장 목록 대조(`inputConfig.contains(name)`)를 `sanitizeString(name)` 기준으로 통일한다.
- 완료 기준: (1) Output transformation 을 `Log` 로 두고 [Set Dataset] → Set 재진입 시 콤보가 `Log` 다 (2) 공백·`/` 가 든 라벨(외부 XML)의 Input/Output 배치·체크·reduction 이 재진입 후 유지된다 (3) 기존 Sim 설정 JSON 이 그대로 로드된다
- 변경 범위: model/DashModelBuilder.cpp · view/DashModelBuilderWidgetBase.cpp · (대조 헬퍼가 필요하면) model/builder/ModelBuilderConfigHelper.cpp
- 선행: BLD-01 (배열 Dataset 을 읽으면 `m_datasetPath` 가 차므로 MCU 복원 경로가 먼저 분리돼야 한다)
- 충돌: BLD-20 (M.cpp) · BLD-07 · BLD-13 (M.cpp) · B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderWidgetBase.cpp → BLD-05 BLD-06 UIC-21
- 흡수: BLD-D4 · BLD-D8 · BLD-U3 · BLD-c04, BLD-c06, BLD-c07
- 비고: D4 는 XML 작성기(`model/preprocessor/DashUtils.cpp:sanitizeString`)가 같은 규칙이라 Sim 에서 잠재적이다 — 수정은 대조 기준 통일만, 저장 키 규칙은 바꾸지 않는다(DeepOpt 가 JSON 라벨 = XML 키 일치를 요구).

#### BLD-03 · 저장된 Response 를 콤보에서 sanitize 양측 기준으로 찾는다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `W:restoreConfigurationUI` · `MW:restoreConfigurationUI` 의 `findText(response, MatchContains)` 를 콤보 항목마다 `sanitizeString(stripResponseParen(text)) == response` 비교로 바꾼다 (`W:refreshAvailableModelsTable` 이 이미 쓰는 방식).
- 완료 기준: (1) MCU 에서 헤더 `Temp (C)` 를 Output 으로 학습·저장 → 재진입 시 Response 콤보가 그 항목이다 (2) Sim 의 `이름 (Field)` · `이름 (Max)` 표시가 그대로 복원된다
- 변경 범위: view/DashModelBuilderWidget.cpp · view/DashModelBuilderMCUWidget.cpp
- 선행: -
- 충돌: BLD-06 (같은 두 함수) · B2 교집합: DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelBuilderWidget.cpp → 공유 10건(deps.md 5절)
- 흡수: BLD-D7 · BLD-c05
- 비고: 대조 규칙은 PM 순수 함수로 두면 단위 테스트가 된다.

#### BLD-04 · [Load] 의 위젯↔모델 계약을 구분자 문자열에서 경로 인자로 바꾼다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `M:onLoadButtonClicked(const QString&)` 를 `(dir, file)` 두 인자(또는 절대경로 1개)로 바꾸고 `W:setModel` 의 loadButton 람다가 `"|"` 로 합치지 않게 한다.
- 완료 기준: (1) 소스에 `"|"` 조립·분할이 없다 (2) 디렉터리 콤보 + 파일 콤보로 [Load] 한 결과가 변경 전과 같다
- 변경 범위: model/DashModelBuilder.h · model/DashModelBuilder.cpp · view/DashModelBuilderWidget.cpp · view/DashModelBuilderMCUWidget.cpp (BLD-01 전이면 `onConfigLoaded` 호출부)
- 선행: -
- 충돌: BLD-20 (M:onLoadButtonClicked 첫머리에 공통 출처 검증 추가) · BLD-05 · BLD-14 · B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelBuilderWidget.cpp → 공유 10건(deps.md 5절) · DashModelBuilder.h → BLD-01 BLD-13 BLD-15
- 흡수: BLD-D2 · BLD-c02
- 비고: BLD-20 뒤에 하면 충돌이 사라진다.

#### BLD-05 · shape 를 로드 시점에 정수 배열로 파싱하고 차원 셈을 그 길이로 바꾼다
- 종류: PR | 규모: M | 태그: C, E · refactor
- 목표: `LabelInfo` 에 `QVector<int> dims` 를 두고 `M:onLoadButtonClicked` 가 파싱한 값을 채운다. `LTH:getShapeDimension` · `calculateMaxEffectiveOutputDim` 과 그 소비처가 문자열 쉼표 셈 대신 길이를 쓴다. 표시 문자열은 파생값.
- 완료 기준: (1) `LTH:getShapeDimension`(:269) · `calculateMaxEffectiveOutputDim`(:333) 이 `dims.size()` 를 쓰고, 표 셀 텍스트를 역파싱해 차원을 구하는 호출(`W:976 shapeItem->text()` · `W:1219 si->text()`)이 0 이다. `calculateShapeFromJsonArrayString` 의 `count(',')`(M:281 · MCU:93) 는 shape **문자열 생성** 폴백이라 존치 (2) Input/Output 자동 분배 · 모델 목록(1D 7종/ND 1종) · 머리글 교체 · 특수 행 활성이 변경 전과 같다 (3) base64 shape 와 JSON 배열 shape 두 경로 모두 같은 dims 를 낸다
- 변경 범위: model/DashModelBuilder.h · model/DashModelBuilder.cpp · model/builder/ModelBuilderLabelTableHelper.h · model/builder/ModelBuilderLabelTableHelper.cpp · view/DashModelBuilderWidgetBase.cpp · view/DashModelBuilderWidget.cpp
- 선행: -
- 충돌: BLD-20 (M:onLoadButtonClicked) · BLD-04 · BLD-13 (LTH) · BLD-14 · B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderWidget.cpp → 공유 10건(deps.md 5절) · DashModelBuilder.h → BLD-01 BLD-15 · DashModelBuilderWidgetBase.cpp → BLD-02 BLD-06 BLD-07 UIC-21 · ModelBuilderLabelTableHelper.cpp → BLD-16
- 흡수: BLD-D3 · BLD-c03
- 비고: 표 셀(2열)은 문자열을 계속 보여주되 판정은 모델 쪽 dims 를 조회한다 — 셀 텍스트 역파싱이 남지 않게.

#### BLD-06 · 설정 페이지 값 왕복을 레이아웃 인덱스가 아니라 jsonKey 로 짝짓는다
- 종류: PR | 규모: M | 태그: A, E · refactor
- 목표: `createModelConfigUI`(W·MW)가 만든 필드 위젯에 `objectName = jsonKey` 를 주고, `Base:getModelConfiguration` · `W:restoreConfigurationUI` · `MW:restoreConfigurationUI` 가 `itemAt(i, FieldRole)` 대신 키로 위젯을 찾는다. 숨긴 ND `critical_region_*` 도 같은 방식.
- 완료 기준: (1) 카탈로그(`PM::standardModelParameterCatalog` · MCU 카탈로그) 항목 순서를 바꿔 빌드해도 저장 JSON 의 키-값이 바뀌지 않는다 (2) 숨긴 ND 두 값이 이전과 같은 키로 기록된다 (3) MCU `checkbox_spin` 복원이 그대로다
- 변경 범위: view/DashModelBuilderWidgetBase.h · view/DashModelBuilderWidgetBase.cpp · view/DashModelBuilderWidget.cpp · view/DashModelBuilderMCUWidget.cpp
- 선행: -
- 충돌: BLD-03 (restoreConfigurationUI) · BLD-13 (MW 빈 루프) · B2 교집합: DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelBuilderWidget.cpp → 공유 10건(deps.md 5절) · DashModelBuilderWidgetBase.cpp → BLD-02 BLD-05 BLD-07 UIC-21
- 흡수: BLD-D5 · BLD-c09
- 비고: 숨긴 위젯 2종이 "화면에 없는 값을 기록" 하는 것은 그대로 둔다 — 노출 여부는 별개 결정.

#### BLD-07 · 모델 행 [Delete] 가 설정 JSON 의 Configuration 항목도 지우고 MCU 도 산출물을 지운다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `M:deleteTrainedModel` 이 `Configuration.{model}` 을 설정 JSON 에서 제거한다(또는 별도 `removeModelConfiguration` 을 `Base:onRemoveModelRowClicked` 가 부른다). `aboutToRemoveModelRow` 의 산출물 삭제를 Base 기본 구현으로 올려 MCU 행 삭제도 `userPath` 산출물·`errors` 를 지운다.
- 완료 기준: (1) `Done` 모델 행 [Delete] 뒤 설정 JSON 에 그 모델 키가 없고 다음 [Start] 에 되살아나지 않으며 재로드 시 행이 없다 (2) MCU 행 [Delete] 가 `{userPath}/ModelBuilder_{Set}/{response}/{model}*` 와 `model_info.errors` 를 지운다
- 변경 범위: model/DashModelBuilder.cpp · view/DashModelBuilderWidgetBase.cpp · view/DashModelBuilderWidget.cpp
- 선행: -
- 충돌: BLD-02 · BLD-13 (M.cpp) · BLD-11 (결정 항목 ⑦ 과 같은 내용 — 이 항목이 "MCU 도 지운다" 로 선결) · B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderWidget.cpp → 공유 10건(deps.md 5절) · DashModelBuilderWidgetBase.cpp → BLD-05 BLD-06 UIC-21
- 흡수: BLD-D6 · BLD-c10, BLD-c17
- 비고: [Start] 의 `status == "Done"` 보존 루프는 유지한다 — 삭제된 모델이 남지 않으면 보존이 올바른 동작이다.

> **BLD-08 — 결번.** MCU 파일 행 `[...]` 람다의 행 번호 값 캡처(BLD-D10 · BLD-c18 · c35)는 같은 함수를 고치는 **UIC-23 에 병합**(B2) — RUN·BLD 두 MCU 위젯을 한 헬퍼로 고친다. 번호는 재사용하지 않는다.

#### BLD-09 · MCU 헤더 검증의 기준 파일을 하나로 정하고 변경마다 전 행을 재검증한다
- 종류: PR | 규모: S | 태그: A, D · bug
- 목표: 기준 = "경로가 있는 첫 행의 헤더" 하나. `browseDatasetFile`(첫 파일 무검증 기록 · row==0 특례) · `onLoadButtonClickedMCU`(순회 중 처음 읽힌 파일) 의 분기를 없애고, 어느 행의 경로가 바뀌어도 전 행 State 를 다시 계산한다. 고정 15개(`PM::mcuFixedDatasetHeaders`)는 초기 표시·[Format] 전용으로 남긴다.
- 완료 기준: (1) 같은 파일 집합을 어떤 순서로 지정해도 State 결과가 같다 (2) 기준 행의 경로를 바꾸면 나머지 행 State 가 즉시 바뀐다 (3) 규칙이 PM 순수 함수로 있다 (단위 테스트는 BLD-19 의 TU 가 고정)
- 변경 범위: view/DashModelBuilderMCUWidget.cpp · viewmodel/DashModelBuilderPresentationModel.h · viewmodel/DashModelBuilderPresentationModel.cpp
- 선행: -
- 충돌: BLD-01 (헤더 재구성 공유 함수) · UIC-23 (MW — BLD 몫 병합) · B2 교집합: DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelBuilderPresentationModel.cpp → BLD-16
- 흡수: BLD-D11 · BLD-c19
- 비고: 대안 — 고정 15개 강제(`validateDatasetFile` 완전 일치가 이미 그 방향). [Load] 가 첫 파일 헤더로 Input/Output 을 재구성하는 현행 동작은 임의 헤더를 허용한다는 뜻이라 "첫 행 기준" 을 택했다. 고정 강제를 택하면 BLD-11 에서 결정.

#### BLD-10 · MCU 학습 종료를 위젯이 관측해 버튼을 되돌리고, 쓰지 않는 폴링 타이머를 끈다
- 종류: PR | 규모: S | 태그: B · bug
- 목표: `MCU:onTrainingStartButtonClicked` 가 `m_statusCheckTimer` 를 켜지 않는다. `MCU:onDaemonCommandCompleted(train)` 이 `trainingSucceeded`, `onDaemonCommandFailed` 가 `trainingFailed` 를 발행한다. `MW:setModel` 이 두 시그널을 연결해 Start/Stop 을 되돌리고 결과 표를 갱신하며, `MW:onModelStatusUpdated` 도 `"Running"` 행이 없으면 되돌린다.
- 완료 기준: (1) MCU 학습 정상 종료 뒤 Start 활성·Stop 비활성 (2) 데몬 명령 실패 시 같은 복귀 + 오류 통지 (3) 학습 중 `checkModelStatus` 가 호출되지 않는다 (4) [Stop] 이 `Interrupted` 와 데몬 재기동에 도달한다 (#548 해소 재확인)
- 변경 범위: model/DashModelBuilderMCU.cpp · view/DashModelBuilderMCUWidget.cpp
- 선행: -
- 충돌: BLD-01 · BLD-12 (MW:setModel) · B2 교집합: DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelBuilderMCU.cpp → BLD-13 BLD-17 BLD-18 PRJ-09 UIC-20
- 흡수: BLD-D13 · BLD-D15 · BLD-c20, BLD-c22 · (BLD-D14 해소 확인 · BLD-c21) · EXE-c37 · BLD-c37 · #463(BLD 몫) · EXE-c23 · BLD-c41
- 비고: Sim 과 같은 `trainingSucceeded/Failed` 계약으로 맞추는 것이 핵심 — 위젯이 데몬 시그널을 직접 알 필요가 없다. #463 BLD 몫: Start 비활성·Stop 취소는 Sim(W:959)·MCU(MW:1046) 모두 현행이고 빠진 것은 MCU 복귀(이 항목)뿐 — 상태바 진행 표시는 EXE-07 규약 확정 뒤 같은 시그널에 얹는다.

#### BLD-11 · Sim·MCU 쌍둥이 계약의 통일 방향을 항목별로 결정한다
- 종류: DEC | 규모: S | 태그: E, A · refactor
- 목표: 베이스를 공유하면서 갈라진 계약 중 **결정이 남은 4종**을 "유지 / 통일(후속 항목) / EXT" 로 확정한다. ① status 문자열·저장 위치(설정 JSON vs `model_info.json models.*`, 후자는 DashOptiMCU.exe 가 씀) ② 산출 루트(`.dproj` vs 사용자 루트 — `DashIOController::getModuleDir` 의 ModelBuilder 특례 `DashIOController.cpp:30-31`) ⑤ Test Results 탭 활성 조건 ⑥ [Set Dataset] 의 Input 체크 저장 규칙(Sim 전 행 vs MCU 체크 행 — DeepOpt 는 Input 키 전부를 쓴다). 나머지 3종은 **PR 항목이 이미 결론을 내고 있어 결정 대상이 아니다** — ③ `Dataset` 형 = 유지(BLD-01 비고) · ④ Data Label 을 쓰는 계층 = 모델 계층으로 통일(BLD-12) · ⑦ 행 삭제 시 산출물 삭제 = MCU 도 지운다(BLD-07). 이 결정 기록은 그 3건을 "PR 선결" 1줄로만 적는다
- 완료 기준: 결정 기록 — 항목 4개(①②⑤⑥) 각각 결론·근거·후속 항목 ID + ③④⑦ 의 PR 선결 1줄. ①②는 하류(Runner·Optimizer 가 읽는 `model_info.json` 경로)와 DashOptiMCU 출력 규약에 묶이므로 RUN·OPT·EXE 접점을 명시한다. ② 가 "통일" 로 결정되면 후속 PR 1건(Sim 산출 루트 이행 + Runner·Optimizer 읽기 경로 동반 수정)을 BLD 에 추가한다
- 변경 범위: (결정 문서) — 코드 없음
- 선행: -
- 충돌: -
- 흡수: BLD-D9 · BLD-c11, BLD-c12, BLD-c14, BLD-c15, BLD-c16
- 비고: ② 는 저장 위치 결정이라 되돌리기 비용이 크다 — "나중에 교체" 전제로 정하지 않는다. 결정만 남고 실행이 비면 안 되므로 후속 PR 을 완료 기준에 못박았다. ⑥ 은 Sim 의 Input 체크박스가 현재 무의미하다는 사실 확인이 선행.

#### BLD-12 · MCU Data Label 저장을 위젯 직쓰기에서 모델 계층으로 옮긴다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `MW:onSetButtonClicked` · `MW:onStartTrainingClicked` 의 설정 JSON read-modify-write 두 곳을 없애고 `DashModelBuilderMCU::updateAndSaveConfig(files, inputLabels, outputLabels)` 가 `PM::mcuDataLabelJson` 으로 쓴다. Sim 의 `updateAndSaveConfig → saveDataLabelConfig` 와 같은 층위.
- 완료 기준: (1) MW 에 `QFile`/`QJsonDocument` 로 설정 JSON 을 쓰는 코드가 없다 (2) 저장 JSON 내용이 변경 전과 같다(Dataset 배열 · 원문 키 · 섹션 보존)
- 변경 범위: model/DashModelBuilderMCU.h · model/DashModelBuilderMCU.cpp · view/DashModelBuilderMCUWidget.cpp
- 선행: BLD-01 (MCU 모델이 파일 목록을 상태로 들어야 그 위에 저장 경로를 둔다)
- 충돌: BLD-10 (MW:setModel) · BLD-11 ④ · B2 교집합: DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelBuilderMCU.cpp → BLD-13 BLD-17 BLD-18 PRJ-09 UIC-20 · DashModelBuilderMCU.h → BLD-15 BLD-20
- 흡수: BLD-D9(쓰는 계층) · BLD-c14
- 비고: -

#### BLD-13 · 죽은 코드를 세 층에서 제거한다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: 호출처 0 인 것을 지운다 — `LTH:populateIoTable·updateLabelTable·populateTableRow·moveSelectedLabels`(Base 에 동명 구현) · `Base:populateIoTable` · `M:getDatasetFiles`+`m_datasetFiles`+`setProjectDirectory` 의 디렉터리 스캔 2덩어리 · `M:getInputTableSetOptions·getInputTableReductionOptions·getOutputTableSetOptions·getOutputTableReductionOptions` · `M:getTrainedModelError`(Deprecated) · `M:loadLabelMetadata`+`m_labelMetadata`(write-only) · `MW:restoreConfigurationUI` 의 빈 중첩 루프 · `MCU.cpp` "inherited" 주석 블록(stopTraining 행이 사실과 다름) · W·MW 의 `static sanitizeString` 래퍼.
- 완료 기준: (1) 열거한 심볼이 저장소에서 사라지고 빌드가 통과한다 (2) `setProjectDirectory` 가 config 경로 계산 → `loadDataLabelConfig` 만 수행한다 (3) 동작 변화 없음(Set 선택·Load·학습·결과 열람 수동 확인)
- 변경 범위: model/builder/ModelBuilderLabelTableHelper.h · model/builder/ModelBuilderLabelTableHelper.cpp · view/DashModelBuilderWidgetBase.h · view/DashModelBuilderWidgetBase.cpp · model/DashModelBuilder.h · model/DashModelBuilder.cpp · model/DashModelBuilderMCU.cpp · view/DashModelBuilderMCUWidget.cpp · view/DashModelBuilderWidget.cpp
- 선행: -
- 충돌: BLD-02 · BLD-05 · BLD-06 · BLD-07 · BLD-20 (`loadLabelMetadata` 삭제 적용 접점) · B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelBuilderWidget.cpp → 공유 10건(deps.md 5절) · DashModelBuilderMCU.cpp → BLD-01 BLD-10 BLD-12 BLD-17 BLD-18 PRJ-09 UIC-20 · DashModelBuilder.h → BLD-01 BLD-04 BLD-14 BLD-15 · DashModelBuilderWidgetBase.cpp → UIC-21 · ModelBuilderLabelTableHelper.cpp → BLD-16
- 흡수: BLD-U1 · BLD-c23 · (BLD-c21 잔재 주석)
- 비고: `fileListUpdated` 시그널은 스캔 제거 뒤에도 콤보 갱신 트리거로 쓰이는지 확인 — W·MW 가 `updateAnalysisLauncherDirComboBox` 에 연결한다. T22 가 `loadLabelMetadata` 에 얹는 키 필터는 **기다리지 않는다** — 이 항목이 그 함수를 지우면 필터 자체가 불필요하고(#368 본문도 "방어 조치 · `m_labelMetadata` 가 write-only 라 무해" 로 적는다), 머지를 기다리면 방금 추가된 코드를 다시 지우는 왕복이 된다. BLD-20과 삭제 적용 순서만 조율하고 해당 옛 필터 hunk는 도입하지 않는다.

#### BLD-14 · Set 단위 Preprocess XML(응답 N 개)을 Builder 로더가 읽는다
- 종류: PR | 규모: M | 태그: A, C · feature
- 목표: #643 1차 포맷(Analysis Launcher Set 당 XML 1개, 응답을 그 안에 추가)에 맞춰 `M:onLoadButtonClicked` 의 샘플 라벨 열거와 `M:parseModelInfoStream·readSelectedResponseFromStream` 의 `selected_response` 단일 dict 전제를 복수 응답으로 바꾸고, `loadModelInfoFromXml` 의 head/tail 조각 탐색(`model/DashXmlTailLocator.h`)이 새 레이아웃에서 성립하는지 맞춘다. 학습 시작 시 `model_info.json` 이식도 응답별 메타를 싣는다.
- 완료 기준: (1) 응답 2개가 든 Set XML 을 [Load] 하면 Output 표에 두 응답이 각각 shape 와 함께 뜬다 (2) 학습 시작 뒤 `model_info.json` 에 두 응답의 메타가 있다 (3) 구 포맷(응답 1개) XML 도 그대로 로드된다 (4) 응답 2개 dataset 으로 1D·ND 학습이 끝까지 돈다 (5) DeepOpt 리더 계약 대조 — 응답 추가가 `root` 첫 자식(학습 데이터)과 샘플 dict 동형을 깨지 않는다. `model_info` 는 샘플 앞으로 옮기지 않는다 (6) **샘플 0 위상으로 나머지를 읽는다** — 위상(`node_location`·`connectivity`)이 샘플 0 에만 있는 XML(PRE-31 산출)을 [Load] 해도 라벨 열거가 그대로이고, 그 2키의 Shape 열에 샘플 수 `dataCount` 접두가 붙지 않는다(파일 단위 값이므로). 샘플 1..N 을 되읽는 코드가 새로 생기지 않는다 · `dashModelInfoMatchesFirstSample` 의 "model_info 파라미터 ⊆ 샘플 0 키" 불변과 꼬리 창 크기 전제(`DashXmlTailLocator.h` 전제 9·13)가 새 레이아웃에서 성립
- 변경 범위: model/DashModelBuilder.h (`LabelInfo`) · model/DashModelBuilder.cpp (onLoadButtonClicked :373-418 샘플 0 열거·`dataCount` 접두 :394-408 · parseModelInfoStream · readSelectedResponseFromStream · loadModelInfoFromXml) · model/DashXmlTailLocator.h (전제 9·13 — 샘플 0 키 집합·꼬리 창) · view/DashModelBuilderWidget.cpp (응답 선택 UI 가 필요해질 때만)
- 선행: PRE-29 · PRE-30 (XML 규격) · PRE-31 (위상 1회 쓰기) · BLD-16 (복수 응답 학습 실측)
- 충돌: BLD-20 (parseModelInfoStream) · BLD-04 · BLD-05 (onLoadButtonClicked) · B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderWidget.cpp → 공유 10건(deps.md 5절) · DashModelBuilder.h → BLD-01 BLD-13 BLD-15
- 흡수: #643 (BLD 몫) · BLD-c26 · PRE-c54(#643 추가 1) · BLD-c33 · PRE-c56(#643 추가 3 — 2차) · BLD-c39 · PRE-c55(#643 추가 2 — 로더 수용 몫만, 작성기는 PRE-31)
- 비고: PRE·BLD 양쪽이 지켜야 하는 DeepOpt 리더 계약(PRE-c59 → BLD-c34 로 넘어온 제약, 완료 기준 (5)) — DeepOpt 는 `root` 의 첫 자식만 학습 데이터로 읽고 **샘플 dict 가 동형**이어야 한다. `model_info` 를 샘플 앞으로 옮기거나 샘플 dict 구조를 바꾸면 Builder 가 읽어도 DeepOpt 와 호환되지 않는다 — 응답 추가는 샘플 dict 안의 키로만 한다. 복수 응답의 학습 성립 자체는 미확인(BLD-c44) — BLD-16 ⑥ 의 실측이 "불가" 면 이 항목은 EXT(DeepOpt) 동반이다. #643 추가 1 의 "개발 중인 Builder 다중 part 포맷" 은 dev 에 없다(BLD-c33) — 규격이 나오면 PRE-30 의 입력. 2차(HDF5) 는 PRE 결정 뒤 로더 교체 항목을 따로 낸다(L 예상, `DashXmlParser` 캐시 #515 와 함께 — 학습 본체 DeepOpt 리더 동반, BLD-16 ⑤).
  완료 기준 (6) 은 PRE-31(위상 1회 쓰기)의 `보류: BLD 몫` 수용이다 — 현행 로더는 이미 샘플 0 만 열거하므로(`inKeyZeroDict` 루프) 위상이 샘플 0 에만 있어도 라벨 목록은 깨지지 않는다. 실제로 손볼 것은 두 가지뿐이다: ① `dataCount` 접두가 파일 단위 위상 2키에도 붙어 `[N, nodes, 3]` 으로 표시되는 것을 제외 ② `DashXmlTailLocator` 의 꼬리 창이 "샘플 0 항목 수 × 상수" 라 위상·응답이 샘플 0 에만 모이면 창이 커지는 쪽(안전측)이므로 전제 재확인만. 샘플 1..N 을 되읽는 코드를 새로 만들지 않는 것이 수용의 요점이다 — 새로 만들면 PRE-31 의 절감이 사라진다. ANA 는 같은 성격의 보류를 ANA-23(결과 XML 스키마 변경의 파서 수용)으로 받았다.
  PR #658(draft, Registry #82 — preprocessor v3) 의 `DashResultXmlWriter.cpp` hunk 를 확인했다: 응답 배열을 인덱스 0 대신 이름(`field_output_name`/`result`)으로 고르고, 응답 `dict_item` 에 `quantity`·`unit`·`component_labels` 속성을 더하고, eigenvalue 가 있는 모달 스텝의 응답 키를 `resName` → `Eigenvalue` 로 바꾼다. 샘플 dict 구조와 `model_info` 위치는 그대로이고 BLD 함수 본문도 건드리지 않으므로 **선행 아님**. 다만 `component_labels` 는 이 항목의 "응답별 메타" 입력이고, `Eigenvalue` 키 변경은 기존 `ModelBuilder_{Set}.json` 의 라벨 키와 어긋나므로 완료 기준 (3)(구 포맷 로드)의 확인 대상에 포함한다.

#### BLD-15 · Builder가 실제 소비한 입력 버전으로 최신성을 판정한다
- 종류: PR | 규모: M | 태그: C, A · feature
- 목표: #650 규칙에 따라 학습에 실제 사용한 dataset 생산 Set·입력 버전을 결과와 함께 기록하고 DashModelBuilder::upstreamStaleReasons가 현재 상류 버전과 비교한다. 현재 Launcher 참조 선택만으로 과거 결과의 소비 버전을 덮지 않는다.
- 완료 기준: ① 실제 dataset 사용 버전 기록 ② 같은 Launcher Set의 산출물 재생성 시 규칙에 따른 최신성 사유 ③ 누락·비교 불가 상태를 PRJ-23 결정대로 처리 ④ 프로젝트 집계·VM 표시에서 Set 판정 결과 사용. MCU는 적용 입력의 버전을 판정하며 deck 비해당을 최신성 전체 면제로 취급하지 않는다.
- 변경 범위: model/DashModelBuilder.h · model/DashModelBuilder.cpp · model/DashModelBuilderMCU.h
- 선행: PRJ-23 (#650 버전·판정 규칙)
- 충돌: BLD-20 (같은 Set JSON) · BLD-14 · B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilder.h → BLD-01 BLD-04 BLD-05 BLD-13 · DashModelBuilderMCU.h → BLD-01 BLD-12
- 흡수: #650 (BLD 몫) · BLD-c25 · PRJ-c36 · BLD-c36
- 비고: BLD-20은 참조·출처, 본 항목은 버전·최신성이다. 생산 dataset 버전 기록은 #650의 생산 측 범위로 함께 정의하며 #643 포맷 전환을 일괄 선행으로 두지 않는다. PRJ-22 집계 구조와 공유 파일 적용 순서만 조율한다.

#### BLD-16 · DeepOpt 가 실제로 읽는 설정 키·토큰을 실측해 GUI 옵션과 맞춘다
- 종류: INV | 규모: S | 태그: A, G · bug
- 목표: 배포 `DashOptiDeepOpt.exe` 기준으로 ① Output reduction 토큰 집합(`Sum` vs `SUM`, 1D·ND 각각) ② Output `transformation` 소비 여부 ③ Input `reduction` 소비 여부 ④ `Configuration.<model>.response` 가 학습 대상을 제한하는지 ⑤ 학습 본체가 dataset XML 을 직접 읽는 리더의 입력 계약(#411 결정 2 — 포맷 교체 시 동반 변경 범위) ⑥ **복수 응답이 든 dataset 1개로 1D·ND 학습이 성립하는지** — 1D 의 라벨↔열 대응, StableNet 의 응답 연결 제약(위키 "다성분과 복수 응답" 행, BLD-c44) 을 실측한다.
- 완료 기준: 실측 결과 기록 + 후속 분기 — ① 불일치면 GUI 토큰 수정(S PR, `LTH:getReductionOptionsForShape`) 또는 EXT ②③ 미소비면 GUI 옵션 제거(S PR) 또는 EXT(DashOptiDeepOpt 구현) ④ 는 계약 결정(DEC, 행별 Response 의 의미) ⑥ "불가" 면 BLD-14 는 EXT(DeepOpt 복수 응답 지원) 동반 — BLD-14 의 선행으로 등록돼 있다
- 변경 범위: (조사) model/builder/ModelBuilderLabelTableHelper.cpp · viewmodel/DashModelBuilderPresentationModel.cpp · model/DashModelBuilder.cpp · 외부 DashOptiDeepOpt
- 선행: -
- 충돌: B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderPresentationModel.cpp → BLD-01 BLD-09 · ModelBuilderLabelTableHelper.cpp → BLD-05 BLD-13
- 흡수: Model-Builder-XML-DeepOpt-Pipeline "구현 차이" · BLD-c27, BLD-c28, BLD-c29, BLD-c30, BLD-c44 · #411(결정 2 — BLD 몫) · PRE-c59 · BLD-c34
- 비고: 위키는 DeepOpt `a4222b6` 로컬 소스 정적 대조다 — 배포 EXE 가 같은 커밋인지 확인하지 않았다.

#### BLD-17 · 설정 JSON·model_info.json 직쓰기를 공용 JSON 헬퍼로 이행한다
- 종류: PR | 규모: S | 태그: A · refactor
- 목표: `QFile::open(WriteOnly, Truncate)` 직쓰기 7지점 — M:onTrainingStartButtonClicked(:520 설정 · :602 model_info) · createModelInfoJson(:783) · saveDataLabelConfig(:934) · deleteTrainedModel(:2342) · MCU:onTrainingStartButtonClicked(:557 · :688) — 를 PER-02 가 공용 진입점으로 승격하는 **DashSaveSystem 헬퍼**(`persistence/DashSaveSystem::read/writeJsonFile` — QSaveFile · `Result` 반환)로 바꿔 원자 쓰기·사유 반환·(PER-04 뒤) 버전 키를 얻는다. MW:onSetButtonClicked(:819)·onStartTrainingClicked(:984) 2지점은 BLD-12 가 모델 계층으로 옮긴 뒤 같은 헬퍼를 탄다. `onDownloadFormatButtonClicked`(:1729 CSV 양식)은 산출물이라 제외.
- 완료 기준: BLD 5파일에서 `QIODevice::WriteOnly` 가 CSV 양식 1곳뿐 / 쓰기 실패(읽기 전용 경로) 시 기존 파일 바이트 동일 + 통지 1건 / 학습 시작·Set Dataset·Delete 동작 불변
- 변경 범위: model/DashModelBuilder.cpp · model/DashModelBuilderMCU.cpp (BLD-12 뒤면 view/DashModelBuilderMCUWidget.cpp 는 제외)
- 선행: PER-02 · BLD-12 (MCU 모델 저장 경로)
- 충돌: BLD-20 (M:onTrainingStartButtonClicked) · BLD-02 · BLD-07 · BLD-13 · BLD-18 (같은 쓰기 지점) · B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelBuilderMCU.cpp → BLD-01 BLD-10 PRJ-09 UIC-20
- 흡수: #479(BLD 몫) · #478(BLD 몫) · #480(BLD 몫) · PER-c27 · PER-c08(BLD 5지점) · BLD-c38
- 비고: `model_info.json` 은 출처 기록 자리 — 헬퍼 이행과 출처 쓰기가 같은 함수를 지난다

#### BLD-18 · Builder가 학습 산출물 버전을 기록한다
- 종류: PR | 규모: S | 태그: C, A · feature
- 목표: #650의 PRJ-23 규칙에 따라 생산 Builder Set이 model_info.json에 학습 산출물 버전을 기록한다. 동일 setId의 재학습 전후를 구분하며 갱신 시점·실패 처리는 결정된 버전 의미를 따른다.
- 완료 기준: 규칙이 정한 재생성 경계에서 버전이 바뀌고 재진입·단순 입력 선택으로 기존 산출물 버전이 바뀌지 않는다. Runner·Optimizer가 실제 사용한 버전과 비교 가능하다. MCU도 해당 학습 산출물 버전을 기록한다.
- 변경 범위: model/DashModelBuilder.cpp (createModelInfoJson :740-792 · onTrainingStartButtonClicked :602), model/DashModelBuilderMCU.cpp (onTrainingStartButtonClicked :688)
- 선행: PRJ-23
- 충돌: BLD-20 (같은 쓰기 지점) · BLD-17 (같은 쓰기 지점) · BLD-07 · B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderMCU.cpp → BLD-01 BLD-10 BLD-12 BLD-13 PRJ-09 UIC-20
- 흡수: #650(Model Builder 산출 id — 생산자 몫) · PRJ-c37(생산자 몫) · BLD-c43
- 비고: 소비 판정은 RUN-31·OPT-23. BLD-20 출처 기록과 저장 위치를 조율하되 같은 파일이라는 이유로 상호 선행을 걸지 않는다. setId는 버전 발급과 무관하게 유지한다.

#### BLD-19 · Model Builder 의 순수 함수에 단위 테스트 타깃을 둔다 — ConfigHelper · LabelTableHelper · PM
- 종류: PR | 규모: S | 태그: F · refactor
- 목표: `tests/` 에 `DashModelBuilder`·builder 헬퍼 참조 0 (#489 · DEV-c24). GUI·데몬 없이 도는 TU 1개 — CH:createInputLabelsJsonObject/createOutputLabelsJsonObject ↔ parseDataLabelSection 왕복(sanitize 키 · transformation · Dataset 문자열/배열) · LTH:getShapeDimension · getReductionOptionsForShape · PM::buildTrainingStartPlan · mcuDataLabelJson/mcuDatasetArrayJson · standardModelParameterCatalog 키 집합.
- 완료 기준: tests/CMakeLists.txt 에 `test_model_builder_helpers` 등록 · ctest 통과 / BLD-02 · BLD-05 · BLD-09 의 완료 기준이 이 TU 로 고정
- 변경 범위: tests/CMakeLists.txt, tests/TestModelBuilderHelpers.cpp (신규)
- 선행: -
- 충돌: BLD-02 · BLD-05 · BLD-09 (고정하는 동작 — 먼저 쓰고 각 PR 이 갱신) · DEV 의 tests 인프라 항목 · B2 교집합: tests/CMakeLists.txt → 공유 12건(deps.md 5절) · PR #655(tests/CMakeLists.txt) · PR #654(tests/CMakeLists.txt) · PR #652(tests/CMakeLists.txt) · PR #651(tests/CMakeLists.txt)
- 흡수: #489(BLD 몫) · DEV-c24(BLD) · BLD-c42
- 비고: `DashModelBuilder` 본체는 `DashProjectManager::Instance()` 역참조라 TU 밖 — 경로 주입은 PRJ-09 뒤. `LTH:calculateMaxEffectiveOutputDim` 은 QTableWidget 입력이라 제외. CAD-11 · OPT-20 과 같은 형태

#### BLD-20 · Builder가 Launcher 입력 참조를 저장하고 학습 산출물 출처를 기록한다
- 종류: PR | 규모: M | 태그: C, A · feature
- 목표: #368의 완료 지점. 실제 dataset을 생성한 Launcher setId와 dataset·응답·모델·part 등의 선택을 ModelBuilder Set 설정에 저장·복원한다. 공통 판독으로 dataset 출처를 검증한 뒤 model_info.json에 생성 Builder setId와 실제 dataset·상류·deck 출처를 기록한다. 현재 Builder ID를 유지하면서 다른 Launcher 참조를 선택할 수 있다.
- 완료 기준: ① 다른 유효 Launcher setId의 dataset 선택·저장·복원 가능 ② 선택만 바꾸면 기존 model_info 출처 불변 ③ 재학습 결과 덮어쓰기 때 실제 출처도 갱신 ④ 필수 출처 없는 구 dataset은 재생성 안내, 이름·경로 추론·자동 이관 금지 ⑤ Set 미지정 상태에 임의 기본 Set으로 저장하지 않음 ⑥ MCU CSV 입력은 deck 비해당 관계를 계약에서 구분하되 Builder 식별·실제 입력 기록을 생략하지 않음.
- 변경 범위: model/DashModelBuilder.h · model/DashModelBuilder.cpp · model/DashModelBuilderMCU.h · view/DashModelBuilderWidget.cpp
- 선행: PRE-32
- 충돌: BLD-01 (M.h 가상 훅 인접) · BLD-02 · BLD-04 · BLD-05 (M:onLoadButtonClicked) · BLD-03 · BLD-06 (W:setModel) · BLD-07 (M.cpp · W.cpp) · BLD-12 (MCU.h) · BLD-13 (이 항목이 뒤) · BLD-14 (parseModelInfoStream) · BLD-15 (같은 Set JSON) · BLD-16 (M.cpp) · BLD-17 · BLD-18 (M:onTrainingStartButtonClicked 의 같은 쓰기 지점) · B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderWidget.cpp → 공유 10건(deps.md 5절)
- 흡수: #368 Phase 3(T22) · BLD-c24 · BLD-c32 · LCH-c37
- 비고: #530 hunk는 수정 지점 참고만 하며 write-once·핀 불일치 차단을 이식하지 않는다. BLD-13의 loadLabelMetadata 삭제와는 파일 충돌만 조율한다. 버전·최신성은 BLD-15·BLD-18(#650), 소비 검증은 RUN-34·OPT-26(#685). 공통 판독 테스트와 실제 Set 왕복·재학습으로 검증한다.

#### BLD-21 · ND 판정을 응답 속성 술어 하나로 모은다 — `(Field)` 직접 판정 2곳과 모델 이름 카탈로그 분기를 걷어낸다
- 종류: PR | 규모: S | 태그: C · bug
- 목표: RUN-15 가 `DashSurrogateModelCommon` 에 두는 "응답 표시 이름 → ND" 술어를 호출로 바꾼다 — `W:updateModelError`(:1089, 지표 머리글 ND/1D 선택) · `W:hasNDModelInConfiguration`(:1681, Test Results 탭 활성). 같은 함수의 `ndModelNames()` OR 분기(:1675)는 지운다 — 카탈로그 5건이 `DashModelBuilder::getModelsForDimension(3)`={"StableNet"} 1건과 어긋난 중복이고 RUN-15 가 정본 아님으로 확정했다. `PM:rankTestResultsFolders`(:227)의 `ndModelNames()` 는 학습 산출 **폴더 이름** 접두 분류라 남긴다.
- 완료 기준: (1) `view/DashModelBuilderWidget.cpp` 에 `contains("(Field)")` 0건 — 전부 공용 술어 호출 (2) `hasNDModelInConfiguration` 이 응답 축만 본다 — 모델 이름이 `ndModelNames()` 안이어도 응답에 `(Field)` 가 없으면 Test Results 탭이 켜지지 않는다 (3) 같은 행에서 `W:updateModelComboBox`(:1049)의 `effectiveModelDimension(baseDim, reduction).isND` 와 술어 결론이 일치한다 — 생산 지점 `PM:responseDisplayText`(:176-178)가 같은 조건이라 코드 변경 없이 성립해야 하고, 어긋나면 응답 콤보 텍스트가 낡은 것이므로 갱신 순서를 고친다 (4) 지표 머리글·Test Results 탭 활성이 같은 입력에서 변경 전과 같다
- 변경 범위: view/DashModelBuilderWidget.cpp
- 선행: RUN-15 (공용 술어 신설 — 없으면 호출할 대상이 없다. `ndModelNames()` 자체는 RUN-15 가 BLD 용으로 남긴다)
- 충돌: BLD-11 ⑤ (Test Results 탭 활성 조건 결정 — 같은 함수. 이 항목은 "무엇이 ND 인가" 만 고치고 Sim/MCU 갈림은 BLD-11 몫) · BLD-05 (W:updateModelComboBox 의 `baseDim` 산출) · BLD-19 (술어 ↔ `effectiveModelDimension` 일치 케이스를 그 TU 에 둘 수 있다) · B2 교집합: DashModelBuilderWidget.cpp → 공유 10건(deps.md 5절)
- 흡수: RUN-D6(BLD 몫) · BLD-c45
- 비고: RUN 2차 반영이 코드로 재확인한 `(Field)` 판정은 5곳이 아니라 6곳이다 — RUN `W:962`·`view/common/SurrogateTableController.cpp:29`(RUN-15) · BLD `W:1089`·`W:1681`(이 항목) · OPT `DashOptimizerWidget.cpp:556`·`:867`(OPT 몫). 생산은 1곳 `PM:responseDisplayText`(:178) → `Base:getOutputResponseList`(:299) → `Output Response` → model_info `errors` 키. **생산자가 BLD** 이므로 술어의 정본 조건(`baseDim==3 && reduction=="None"`)은 BLD 가 쥐고 있다 — RUN-15 가 술어를 공용층에 옮길 때 그 조건을 그대로 옮기는지 확인한다. 번호는 BLD-21 — BLD-08 은 결번이라 재사용하지 않는다(위 BLD-07 뒤 주석).

### RUN — Model Runner

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> 기준: dev @ b08a91b3. 원자 항목은 `02-claims/RUN.md`. 파일 접두는 그 문서와 같다 (`W:`·`M:`·`PM:`·`MW:`·`AW:`).
> 열린 PR 7건 중 머지 대상 6건 (#651 #652 #654 #655 #656 #658) — #530 은 재업로드 노선이라 머지 대상이 아니다 (05-final/decisions.md ⑩·②). RUN **본체 파일**(M · W · PM · MW)을 만지는 것은 **PR #654**(#332 — M.cpp performMorphing) 하나뿐이고, 머지될 때까지 M:performMorphing 을 만지는 항목은 뒤로 둔다. 접점 파일만 겹치는 것 — `model/DashProject.cpp`(#651 #652) · `view/DashMainWindow.cpp`(#651 #652 #654 #655) · `tests/CMakeLists.txt`(#651 #652 #654 #655) · `view/dialog/DashDirectLaunchDialog`(#652 — RUN-30 의 선행). **#656·#658 은 RUN 항목의 변경 범위와 교집합 0** 이라 선행 추가 없음 (#656 = 런처·preprocessor 공용 함수 · #658 = RW 문서·preprocessor v3).
> 구 #368 T23 소비 범위는 #685의 RUN-34로 이관됐다. PR #530 hunk는 수정 지점 참고이며 조합 핀을 그대로 이식하지 않는다. #513 워커 이관·#650 최신성·결과 오류 수정은 각각의 목표로 진행한다.

#### RUN-01 · NodeSet 선택을 독립적으로 저장·복원한다 (#369)
- 종류: PR | 규모: S | 태그: A · feature
- 목표: 기존 nodeSetSource 저장·경로 처리 설계에 따라 Runner의 NodeSet 선택을 저장·복원한다. #443의 하위에서 분리된 독립 작업으로 유지한다.
- 완료 기준: 선택 저장 후 재진입·재시작에 같은 nodeSetSource 복원, 빈 선택·해석 불가 경로의 기존 처리 검증. #443·#368·#685를 선행이나 완료 조건으로 요구하지 않는다.
- 변경 범위: model/DashModelRunner.cpp · model/DashModelRunner.h · view/DashModelRunnerWidget.cpp
- 선행: -
- 충돌: -
- 흡수: #369 · RUN-c01
- 비고: 과거 범위 밖·종료 제안은 현행 독립 작업 결정으로 대체됐다. RUN-03의 컨트롤 의미 논의와 실제 저장·복원을 구분한다.

#### RUN-02 · #473 결과 항목 조작 오류 수정 묶음을 유지한다
- 종류: DEC | 규모: S | 태그: C
- 목표: #474 표 연결, #475 덮어쓰기 방지, #477 삭제·파일 해석의 구체적 오류 수정을 묶는다. 기존 열린 부모 상태를 유지한다.
- 완료 기준: RUN-10·RUN-11·RUN-12·RUN-13의 범위를 대응시키고 #443·#368·#685 선행을 두지 않는다. 별도 대장·버전 추적·최신성 경고·목록 전용 UI는 제외한다.
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #473 · RUN-c11

#### RUN-03 · Reference 줄·Part 콤보·NodeSet 소스 파일의 의미를 확정한다
- 종류: DEC | 규모: S | 태그: C, D
- 목표: 세 컨트롤이 실제로 결정하는 것을 정한다 — (1) Part 콤보가 모핑 대상인가 `_input_geometry.vtu` 추출 대상인가 (현행: 추출 전용, 모핑은 JSON 의 `actualPartName`), (2) 브라우즈한 NodeSet 소스 파일이 콤보 deck 과 다를 때의 정책 (현행: 라벨은 브라우즈 파일, 격자는 deck — 불일치 시 조용히 누락), (3) 빈 경로 게이트 존치 여부 (현행: 조회는 이미 deck 문서로 하고 경로는 검사에만 쓴다).
- 완료 기준: 결정 기록 — 각 컨트롤의 의미 1줄 · 게이트/다이얼로그 존치 여부 · 라벨 문구. 결정이 "다이얼로그 제거 + 게이트 삭제" 면 S PR 1건이 뒤따른다.
- 변경 범위: 결정 기록 (후속 PR 후보: W:updateReferenceFileAndPart · onDatFileEditClicked · M:performMorphing :2382-2415 · ui 라벨)
- 선행: -
- 충돌: PR #654(performMorphing) · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절)
- 흡수: RUN-c02 · RUN-D12 · RUN-c29 · TODO(#559 리뷰 7)
- 비고: #369는 기존 nodeSetSource 저장·경로 처리 설계를 유지하는 독립 작업이다. 이 DEC에서 저장·복원 요구를 취소하거나 #685 완료를 요구하지 않는다.

#### RUN-04 · updateModelUploadConfig 가 사용자 DV 값을 model_info 기본값으로 덮지 않게 한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: 실행 직전 계약 파일 기록이 `model_info.json` 을 재파싱해 `m_designVariables` 를 `meta.default` 로 교체하는 것을 멈춘다. Generate 때 `saveInputDesignVariableValues` 가 세운 값이 그대로 `Input Design Variables.value` 에 간다. 재파싱은 메타(min·max·라벨)만 쓰거나 아예 하지 않는다.
- 완료 기준: DV 를 바꿔 Generate → Run 하면 `ModelRunner_{Set}.json` 의 `Input Design Variables.value` 가 화면 값과 같다 · 기존 TestModelRunner 류 통과
- 변경 범위: M:updateModelUploadConfig (:1045 · :1168) · M:loadDesignVariables (:834, 필요 시 값 보존 인자)
- 선행: -
- 충돌: RUN-05 · RUN-17 · RUN-29 (같은 함수) · B2 교집합: DashModelRunner.cpp → 공유 19건(deps.md 5절) · PR #654(DashModelRunner.cpp)
- 흡수: RUN-D26 · RUN-c40
- 비고: #370 "주의" 절이 짚은 조용한 오답의 원인. RUN-06 의 선행

#### RUN-05 · ND·1D 동시 체크 실행을 직렬화하고 거절을 통지한다
- 종류: PR | 규모: S | 태그: B, A · bug
- 목표: ND 그룹과 1D 그룹을 한 번의 Run 에서 **순차** 실행한다 — 첫 Job `finished` 뒤 두 번째 그룹의 계약 파일을 쓰고 기동한다. `startPredictionJob` 의 거절(false)은 `runNDPrediction`·`run1DPrediction` 반환값으로 올려 위젯이 모달로 알린다.
- 완료 기준: ND+1D 동시 체크 → 두 결과가 모두 나오고 각 실행 시점의 JSON `Output Response` 가 그 그룹만 가리킨다 · 실행 중 Run 재클릭 → 거절 안내
- 변경 범위: M:startPredictionJob (:186) · runNDPrediction (:1768) · run1DPrediction (:1848) · updateModelUploadConfig(pairs) (:1168) · M.h · W:onRunAIPredictionClicked (:1330-1348)
- 선행: -
- 충돌: RUN-04 · RUN-06 · RUN-29 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashModelRunner.h → RUN-12 RUN-13 RUN-14 RUN-16 RUN-27 RUN-31 RUN-34 · PR #654(DashModelRunner.cpp)
- 흡수: #370-4 · RUN-D23 · RUN-D24 · RUN-c07 · RUN-c38 · #463(RUN 몫 — 예측 재클릭 가드·거절 안내) · EXE-c23 · RUN-c67
- 비고: 대안 — 두 번째 그룹을 거부하고 안내만. 결과 2종을 한 번에 원하는 것이 #370 의 기대 동작이라 직렬화를 택한다. 1D CSV 뷰어 미개방도 이 항목으로 해소

#### RUN-06 · 1D 모델은 파일 없는 DV-only 케이스로 Run AI Prediction 을 허용한다
- 종류: PR | 규모: S | 태그: A, D · bug
- 목표: ND 만 파일 케이스 필수. 1D 는 체크된 케이스 중 파일이 빈 DV-only 행을 그대로 Prediction Case 로 싣고(값은 행별 DV), 케이스가 전혀 없으면 dvTable 현재값으로 1건 만들어 실행한다.
- 완료 기준: 1D 모델 · 파일 행 없음 → Run 이 실행되고 CSV 가 열린다 · ND 모델 · 파일 행 없음 → 기존 에러 유지 · DV-only 행의 값이 JSON `Prediction Cases[].values` 에 그대로 간다
- 변경 범위: W:onRunAIPredictionClicked (:1278-1290) · W:collectPredictionCases (:1812) · PM:validatePredictParams (:196)
- 선행: RUN-04
- 충돌: RUN-05 · RUN-13 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunnerPresentationModel.cpp → RUN-10 RUN-11 RUN-12 RUN-15 RUN-17 RUN-29
- 흡수: #370 · RUN-c03
- 비고: Python 1D 경로(`DeepOpt/main.py` test-model-1d)가 `file` 을 로그에만 쓴다는 #370 의 확인을 전제

#### RUN-07 · Condition·CAD 생성 경로가 표를 재구축하지 않고 행을 추가한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `refreshFileTableFromDisk()` 호출 2곳을 Morphing 경로와 같은 `createFileTableRow` 행 추가로 바꾼다. 기존 행의 DV 값·체크 상태·Morphing `.vtu` 행이 생성 1회로 사라지지 않는다.
- 완료 기준: Morphing 케이스 A 생성 → Condition(또는 CAD) 케이스 B 생성 → A 행이 남고 A 선택 시 A 의 DV 값이 역주입된다
- 변경 범위: W:onGenerateInputFileClicked Condition 분기 (:591-618) · W:onCadFileReadyForFileTable (:650-676)
- 선행: -
- 충돌: RUN-08 · RUN-09 · RUN-12 (같은 함수) · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절)
- 흡수: #370-1 · RUN-D17 · RUN-c04
- 비고: 경로 일치 행을 선형 탐색하던 코드(:600-616 · :660-676)가 함께 사라진다

#### RUN-08 · 정규화 config 파싱 실패 경고를 CAD·Condition 생성 경로에도 낸다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `readModelNormalizationFromConfig` 결과가 `!valid && fileExists` 일 때의 `DashNotify::error` 를 생성 4경로가 공유한다 — 현재는 Morphing·DV-only 2경로에만 있고 CAD·Condition 은 무경고다. 보정 없이 통과하는 값이 사용자에게 보인다.
- 완료 기준: config.yaml 을 깨뜨린 모델로 CAD·Condition 생성 → 같은 경고가 뜬다
- 변경 범위: W:onGenerateInputFileClicked Condition (:596-597 무경고) · W:onCadFileReadyForFileTable (:658-659 무경고) · W:addDvOnlyRowToFileTable (:1674-1683 경고 보유) · W:performMorphingAndAddToFileTable (:1757-1766 경고 보유) — 공통 헬퍼 1개
- 선행: -
- 충돌: RUN-07 (같은 함수) — RUN-07 뒤에 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절)
- 흡수: RUN-D19 · RUN-c35
- 비고: RUN-07 과의 병합 제안(검토 7)은 기각 — 개념이 둘이다 (RUN-07 = 표 재구축으로 사라지는 행 상태, RUN-08 = 깨진 config 의 무경고 통과). 같은 두 함수를 고치는 것은 파일 교집합일 뿐이고 완료 기준·흡수 결함(D17 vs D19)이 갈린다

#### RUN-09 · CAD 생성 실패와 Set 전환에서 대기 상태를 정리한다
- 종류: PR | 규모: S | 태그: A, B · bug
- 목표: NX CAD 업데이트 실패 신호를 구독해 `m_pendingCadStpPath`·`m_pendingCadParams` 를 비우고 상태 애니메이션을 멈춘다. `clearAllTables` 도 같은 두 멤버를 비워 이전 Set 의 완료 통지가 새 Set 표에 행을 만들지 못하게 한다. 완료 통지 짝짓기(:643 경로 문자열 비교)는 CAD-01 이 요청 태그를 돌려주면 태그 비교로 바꾼다(RUN-D15 소비측).
- 완료 기준: CAD 업데이트 실패 → 애니메이션 종료 + 에러 안내 + 이후 같은 경로의 완료 통지가 행을 만들지 않는다 · 요청 중 Set 전환 → 완료 통지가 새 Set 표에 반영되지 않는다
- 변경 범위: W:setModel (:259-262 connect) · W:onCadFileReadyForFileTable (:641) · W:clearAllTables (:1599) · W.h
- 선행: - (태그 비교 전환만 CAD-01 뒤 — 그 전엔 현행 경로 문자열 짝짓기 유지)
- 충돌: RUN-07 · RUN-10 (clearAllTables) · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunnerWidget.h → PRJ-25 RUN-15 RUN-28 RUN-29 RUN-30 UIC-24
- 흡수: RUN-D16 · RUN-D36(pending 부분) · RUN-c33 · RUN-c48(일부) · RUN-D15(소비측) · EXE-c42 · RUN-c70
- 비고: 비배치 update 실패가 `loadPrtFailed` 로 나가는 것(controller/DashSolverNxCad.cpp:224)은 CAD 소관 — 신호 이름 정정 전까지는 그 신호를 구독한다. 접점 CAD

#### RUN-10 · 예측 산출물 채번을 디스크에서 유도해 재진입·Set 전환 뒤에도 이어간다
- 종류: PR | 규모: S | 태그: A, C · bug
- 목표: 현재 Set 폴더의 기존 결과를 조사해 다음 채번 후보를 얻고 실제 생성 대상 파일의 충돌을 확인한 뒤 생성한다. 재시작·재진입 후 기존 결과를 보존하는 것이 목표이며 프로젝트 전역 카운터는 요구하지 않는다.
- 완료 기준: 재시작·Set 재진입·Set 전환 후 기존 파일 내용 보존. 후보 이름이 이미 존재하면 충돌 없는 대상으로 생성하며 파일 종류별 충돌도 확인한다. 채번 파싱과 실제 파일 충돌 사례를 검증한다.
- 변경 범위: W (생성자 :73 · populateFileTable :1114 · clearAllTables :1599 · 증가 4곳) · PM:predictBaseName (:20) 역파싱 추가 · tests/TestModelRunnerPresentationModel
- 선행: -
- 충돌: RUN-09 · RUN-12 · RUN-13 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunnerPresentationModel.cpp → RUN-06 RUN-11 RUN-15 RUN-17 RUN-29 · TestModelRunnerPresentationModel.cpp → RUN-11 RUN-15 RUN-33
- 흡수: #475 · RUN-D34 · RUN-D36(카운터 부분) · RUN-c15 · RUN-c48(일부)
- 비고: 디스크 최대 번호는 후보 계산 방식이다. 번호 재사용 금지 자체나 영속 카운터 구축을 완료 조건으로 삼지 않는다. RUN-11과 파일 소속·명명 접점만 조율하며 독립 진행 가능하다.

#### RUN-11 · 행 삭제 범위를 접두사 매칭에서 정확 매칭으로 바꾼다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: 기존 모듈·산출물 기록의 항목 키로 선택 항목에 속한 파일만 삭제한다. 입력 파일과 프리뷰 파일의 용도를 구분하고 생성 직후와 재열기 후에 같은 항목으로 해석한다.
- 완료 기준: 선택 항목의 입력·프리뷰만 삭제되고 유사 접두 이름의 다른 항목 파일은 보존된다. 생성 직후·재열기 후 동일한 소속 판정과 삭제 결과를 검증한다.
- 변경 범위: PM:relatedFilePathsForDeletion (:40) · tests/TestModelRunnerPresentationModel
- 선행: -
- 충돌: B2 교집합: DashModelRunnerPresentationModel.cpp → RUN-06 RUN-10 RUN-12 RUN-15 RUN-17 RUN-29 · TestModelRunnerPresentationModel.cpp → RUN-10 RUN-15 RUN-33
- 흡수: #477(D21 부분) · RUN-D21 · RUN-c16
- 비고: RUN-12와 최소 항목 키·재열기 식별 기준, RUN-10과 명명·충돌 접점을 공유한다. 별도 UUID·전역 대장을 도입하지 않는다.

#### RUN-12 · 파일 표 행과 케이스를 식별자 하나로 결합한다
- 종류: PR | 규모: M | 태그: C, A · bug
- 목표: 케이스 식별자 = 기본 이름(`Predict_NN_{resp}_{model}`, DV-only 포함). 행 `Qt::UserRole` 에 식별자를 두고 `m_fileTableDvValues` 를 식별자 키로, JSON `Prediction Cases` 의 추가·활성·삭제를 식별자 조회로 바꾼다. 행 번호 재키잉·표시 이름 매칭이 사라진다.
- 완료 기준: 중간 행 삭제·정렬 후 콜백·조회·갱신·DV 보조 상태가 같은 데이터 항목을 가리킨다. 재열기 후 RUN-11과 같은 식별 기준을 사용하며 표시 이름 변경에도 결합이 유지된다. 기존 안정 키를 우선 사용하고 별도 UUID·전역 대장을 요구하지 않는다.
- 변경 범위: W:createFileTableRow (:1982) · onFileTableRowSelected (:1229) · 생성 3경로의 DV 기록 · M:appendPredictionCaseToJson (:2666) · updatePredictionCasesActiveStates (:2693) · removePredictionCasesFromJson (:2723) · M.h(PredictionCase 에 id) · PM
- 선행: -
- 충돌: RUN-07 · RUN-13 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashModelRunner.h → RUN-05 RUN-14 RUN-16 RUN-27 RUN-29 RUN-31 RUN-34 · DashModelRunnerPresentationModel.cpp → RUN-06 RUN-11 RUN-15 RUN-17 RUN-29 · PR #654(DashModelRunner.cpp)
- 흡수: #474(RUN 축) · RUN-c12
- 비고: 파일 경로를 키로 쓰면 DV-only 행(파일 없음)이 빠진다 — 기본 이름이 유일 키. DOE-D8 은 LCH, BLD-D10 은 BLD(BLD-c18)

#### RUN-13 · 재진입 복원을 디스크 스캔에서 JSON Prediction Cases 읽기로 바꾼다
- 종류: PR | 규모: M | 태그: A · bug
- 목표: `populateFileTable` 이 `ModelRunner_{Set}.json` 의 `Prediction Cases[]`(id · file · values · active) 로 행을 되살리고, 디스크 스캔은 JSON 에 없는 파일의 보충에만 쓴다. 체크 토글은 `syncFileTableToJson` 을 구현해(`updatePredictionCasesActiveStates`) JSON `active` 를 즉시 쓴다. 행 경로는 생성 시 기록한 것(.vtu 포함)이 그대로 복원된다.
- 완료 기준: 케이스 2건(DV 다르게) 생성 · 1건 체크 해제 → 재기동 → 행 2건 · DV 값 각각 · 체크 상태 유지 · Morphing 행 경로가 `.vtu` 그대로 · DV-only 행도 복원
- 변경 범위: W:populateFileTable (:1114) · syncFileTableToJson (:1158) · createFileTableRow · M: `readPredictionCases` 신설 (readConfigFile :554 재사용) · M.h
- 선행: RUN-12
- 충돌: RUN-07 · RUN-10 · RUN-29 (syncFileTableToJson 은 여기서 구현하므로 삭제 대상에서 제외) · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashModelRunner.h → RUN-05 RUN-14 RUN-16 RUN-27 RUN-31 RUN-34 · PR #654(DashModelRunner.cpp)
- 흡수: #477(D35 부분) · RUN-D33 · RUN-D35 · RUN-U1 · RUN-c17 · RUN-c47 · RUN-c51
- 비고: `Output Response`·`Input Design Variables` 의 되읽기(선택 모델·DV 입력값 복원)는 범위 밖 — 별도 feature 로 판단

#### RUN-14 · 파라미터 소스 해석을 하나로 모아 혼합 Set 을 전수 판정한다
- 종류: PR | 규모: S | 태그: C, E · bug
- 목표: `getReferenceFileAndPart` 의 첫 매치 `break` 와 `resolveParameterSourceLabel` 의 병행 판정을 파라미터별 결과를 돌려주는 해석기 하나로 바꾼다. Reference 줄·Part 콤보 활성은 전수 결과(형상 소스 존재 여부)로 정하고, `Source` 열은 판정 실패를 `"FE Cond"` 가 아니라 빈 값/`Unknown` 으로 구분한다.
- 완료 기준: Morphing+Condition 혼합 model_info 로 ND Generate → 거짓 거부 없음 · 키 순서를 바꿔도 같은 결과 · `source` 가 깨진 파라미터의 `Source` 열이 FE Cond 와 구분된다 · 단위 테스트 1건
- 변경 범위: M:getReferenceFileAndPart (:1584) · resolveParameterSourceLabel (:887) · loadDesignVariables (:882) · M.h · tests
- 선행: -
- 충돌: RUN-27 · RUN-25 · B2 교집합: DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashModelRunner.h → RUN-05 RUN-12 RUN-13 RUN-16 RUN-29 RUN-31 · PR #654(DashModelRunner.cpp)
- 흡수: #370-2 · RUN-D8 · RUN-D9 · RUN-c05 · RUN-c26

#### RUN-15 · ND 판정 규칙을 하나로 한다
- 종류: PR | 규모: M | 태그: C · bug
- 목표: ND 판정의 정본을 **응답 속성**(model_info 의 응답 표시 이름에 실린 `(Field)`)으로 확정하고, 응답 표시 이름을 받는 술어 1개를 `DashSurrogateModelCommon` 에 둔다. 모델 이름 접두사 판정(`isNDModel`)은 RUN 에서 걷어낸다. 보이는 열(헤더·행 지표)과 타는 경로(생성 분기·예측 그룹)가 어긋나지 않는다.
- 완료 기준: (1) RUN 파일과 `view/common/SurrogateTableController.cpp` 에 `contains("(Field)")` 직접 판정 0건 — 전부 공용 술어 호출 (2) 응답에 `(Field)` 가 있고 모델 이름이 `ndModelNames()` 밖인 model_info(또는 반대)에서 헤더·행 지표·생성 분기·예측 그룹이 같은 판정 (3) `DashSurrogateModelCommon::isNDModel` 삭제 — RUN 밖 호출처 0 (`ndModelNames()` 는 BLD 가 쓰므로 남긴다) (4) 술어 단위 테스트 1건 (RUN-33 TU)
- 변경 범위: W:populateSurrogateTable (:962) · updateTableHeadersForModelType (:822) · `isNDModel` 래퍼 (:817 삭제) · 모델 이름 판정 호출부 2곳 (:536 Condition 분기 거절 · :624 Unknown 폴백) · W.h (:105) · view/common/SurrogateTableController.cpp:createRow (:29 — RUN 전용 표 컨트롤러) · viewmodel/DashSurrogateModelCommon.cpp/.h (:93 `isNDModel` 삭제 · 응답 술어 신설 · `ndModelNames` :73 유지) · PM:groupCheckedPairs (:64) · tests/TestModelRunnerPresentationModel (RUN-33)
- 선행: -
- 충돌: RUN-25 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunnerPresentationModel.cpp → RUN-06 RUN-10 RUN-11 RUN-12 RUN-17 RUN-29 · DashModelRunnerWidget.h → PRJ-25 RUN-09 RUN-28 RUN-29 RUN-30 UIC-24 · TestModelRunnerPresentationModel.cpp → RUN-10 RUN-11 RUN-33
- 흡수: RUN-D6 · RUN-c24
- 비고: 정본 확정 — decisions ⑦ 의 "한 규칙으로" 를 코드 근거로 닫는다. ① Model Builder 가 `(Field)` 를 `baseDim == 3 && reduction == "None"` 에서 붙이고(`viewmodel/DashModelBuilderPresentationModel.cpp:174`) 같은 술어가 `effectiveModelDimension`(:188) 의 `isND` 다. 그 표시 이름이 `getOutputResponseList`(`view/DashModelBuilderWidgetBase.cpp:299`) → `Output Response` → model_info `errors` 키로 간다 — 즉 `(Field)` 는 **학습 시점에 기록된 ND 결정**이다. ② 모델 이름 목록 `ndModelNames()` 5건은 Model Builder 가 실제 제공하는 3D 모델 `DashModelBuilder::getModelsForDimension(3)` = `{"StableNet"}` 1건과 이미 어긋난 중복이라 정본이 아니다. ③ 전환에 배선 추가가 없다 — `GenerateInputFileParams::responseText` · `CheckedModelRow::responseText` 가 이미 응답 표시 이름을 들고 있다. 귀속 — `SurrogateTableController` 는 RUN·BLD·OPT 공용이 아니라 **RUN 전용**이다(소비자는 `DashModelRunnerWidget`·`DashModelRunnerMCUWidget` 2곳뿐, 전수 grep) → 다툼 없이 RUN-15 가 맡고 OPT-10 은 파일 교집합 없이 `선행: RUN-15` 로 술어만 소비한다(충돌 아님). `(Field)` 판정은 5곳이 아니라 **6곳**(+ 생산 1곳) — RUN W:962 · SurrogateTableController.cpp:29 / BLD DashModelBuilderWidget.cpp:1089·:1681 / OPT DashOptimizerWidget.cpp:556·:867 / 생산 DashModelBuilderPresentationModel.cpp:178. BLD 에는 대응 항목이 없어 BLD 2곳은 이 항목 밖(접점 BLD — 술어가 생기면 호출로 바꿀 자리). `DashModelRunnerMCUWidget::isNDModel`(:868)은 `return false` 상수 스텁에 호출처 0 — RUN-29 몫

#### RUN-16 · DV 스핀박스 범위와 초기값 규칙을 바로잡는다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: 상한을 `max` 그대로 두고(Max 열과 같은 값 입력 가능), 미설정 판정을 `value != 0.0` 대신 "저장값 존재" 로 한다 — 정확히 0.0 인 DV 가 중앙값으로 바뀌지 않는다.
- 완료 기준: Max 값을 그대로 입력할 수 있다 · DV 0.0 저장 후 재진입 → 0.0 유지
- 변경 범위: W:populateDesignVariableTable (:1096-1106) · DesignVariableInfo(M.h) 에 설정 여부 또는 `std::optional`
- 선행: -
- 충돌: RUN-17 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunner.h → RUN-05 RUN-12 RUN-13 RUN-14 RUN-27 RUN-29 RUN-31 RUN-34
- 흡수: RUN-D11 · RUN-c28

#### RUN-17 · 설계변수 값의 정본을 셀 위젯에서 모델로 옮긴다
- 종류: PR | 규모: M | 태그: E, A · refactor
- 목표: 스핀박스 `valueChanged` → `DashModelRunner::setDesignVariableValue` 결선. `collectSurrogateSelection`·Download·Generate 가 표를 폴링하지 않고 모델을 읽는다. 모델만 바꾸는 경로가 있어도 화면·저장이 갈리지 않는다.
- 완료 기준: 동작 불변 — Generate·Download·Run 결과가 이전과 같다 · `cellWidget(` 로 스핀박스를 읽는 곳 0
- 변경 범위: W:populateDesignVariableTable · collectSurrogateSelection (:1856) · collectDvRows · onDvUploadButtonClicked · M (setter·신호) · PM
- 선행: RUN-04 (모델이 값을 덮지 않아야 정본이 성립)
- 충돌: RUN-16 · RUN-29 (`designVariablesChanged` 신호 — RUN-29 가 지우면 여기서 재도입) · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashModelRunnerPresentationModel.cpp → RUN-06 RUN-10 RUN-11 RUN-12 RUN-15 · PR #654(DashModelRunner.cpp)
- 흡수: RUN-D10 · RUN-c27

#### RUN-18 · DV 치환값의 유효숫자 절삭을 없앤다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `QString::number(it.value())`(M:1717) 의 기본 포맷 'g'·유효숫자 6자리 절삭을 없앤다 — `QString::number(v, 'g', 17)` 또는 입력 자릿수 유지로 쓴다. **토큰 경계는 건드리지 않는다** — 치환 토큰이 닫는 `}` 를 포함한 완전 일치(M:1716 `QString("${%1}").arg(key)`)라 접두사 충돌·`QMap` 순서 의존이 애초에 없다.
- 완료 기준: `0.1234567` 을 넣은 DV 가 `.dat` 에 6자리로 잘리지 않고 그대로 간다 · 단위 테스트 1건
- 변경 범위: M:generateDatFile (:1715-1718) · tests
- 선행: -
- 충돌: B2 교집합: DashModelRunner.cpp → 공유 19건(deps.md 5절) · PR #654(DashModelRunner.cpp)
- 흡수: RUN-D18 · RUN-c34
- 비고: 결함 색인 RUN-D18 의 "치환 순서에 달린다" 절반은 무효 (검토 5) — `${L}` 은 `${L1}` 의 부분문자열이 아니다. 정규식 토큰화는 하지 않는다

#### RUN-19 · 1D 결과 CSV 선택을 고정 지연·최신 파일에서 결정적 규칙으로 바꾼다
- 종류: PR | 규모: S | 태그: B · bug
- 목표: `singleShot(500)` 을 없애고 Job `finished`(프로세스 종료) 시점에 "실행 시작 시각 이후 생성·수정된 CSV" 를 고른다. 쓰기가 늦어도 놓치지 않고 이전 결과를 최신으로 오인하지 않는다.
- 완료 기준: 두 번 연속 1D 예측 → 각각 자기 CSV 가 열린다 · 결과 파일이 없으면 안내 · ND 경로(VTU 자동 렌더)는 무영향
- 변경 범위: W:onRunAIPredictionClicked (시작 시각 기록) · onPredictionSucceeded (:1352-1399)
- 선행: -
- 충돌: RUN-05 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절)
- 흡수: RUN-D27 · RUN-c41 · EXE-c38 · RUN-c62
- 비고: DeepOpt 가 출력 파일명을 고정 규약으로 낸다면 그 경로를 직접 연다 — 규약 확인 뒤 택일. RUN-20 과의 병합 제안(검토 8)은 기각 — 개념이 둘이다 (RUN-19 = 1D CSV 를 고르는 타이밍·경쟁, RUN-20 = ND 렌더 대상 선택 정책). 같은 두 함수를 고치는 것은 파일 교집합

#### RUN-20 · 예측 완료 자동 렌더 대상을 정한다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: 마지막 케이스 고정 대신 "선택된 행이 체크 케이스면 그 행, 아니면 첫 체크 케이스" 를 렌더한다.
- 완료 기준: 케이스 3건 체크 · 2번째 행 선택 → 2번째 결과가 렌더 · 선택 없음 → 1번째
- 변경 범위: W:onRunAIPredictionClicked (:1320) · onPredictionSucceeded (:1400-1405)
- 선행: -
- 충돌: RUN-05 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절)
- 흡수: RUN-D25 · RUN-c39

#### RUN-21 · Set 불일치 방어가 최초 진입에서도 돌게 한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `onSurrogateCheckBoxChanged` 의 `&& !currentSetName.isEmpty()` 예외를 없애고, Set 이름이 비어 있으면 표를 비우거나 체크를 거부한다.
- 완료 기준: 새 세션 최초 진입에서 다른 Set 폴더의 모델을 체크 → 이전 파일 표가 남지 않는다
- 변경 범위: W:onSurrogateCheckBoxChanged (:1006-1013)
- 선행: -
- 충돌: B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절)
- 흡수: RUN-D38 · RUN-c50

#### RUN-22 · 민감도 패널 진입 시 MCU Set 이름에 접미사를 다시 붙이지 않는다
- 종류: PR | 규모: S | 태그: C · bug
- 목표: `MW:setModel` 이 이미 `-MCU` 로 끝나는 Set 이름에 `+ "-MCU"` 를 붙여 `ModelBuilder_Set1-MCU-MCU` 를 찾게 하던 것을 Set 이름 그대로 넘긴다 (MCU Set 이름은 model/DashProject.cpp:1080·:1095 가 이미 접미사를 붙인다).
- 완료 기준: MCU Set 진입 → 민감도 패널 콤보가 `ModelBuilder_{Set}` 을 선택한다 (`-MCU-MCU` 탐색 없음)
- 변경 범위: MW:setModel (:177)
- 선행: -
- 충돌: B2 교집합: DashModelRunnerMCUWidget.cpp → UIC-20 UIC-23
- 흡수: RUN-D37 · RUN-c49
- 비고: 매치 실패 시 0번 폴백(RUN-D30 · RUN-c44)은 변경 파일이 AW 뿐이라 ANA-06 으로 이관. 변수 목록 원천(RUN-D29 · RUN-c43, 구 RUN-23)도 ANA-18 로 이관 — RUN-23 은 삭제(번호 결번)

#### RUN-24 · 결과 열람의 VTU 중복 파싱을 없앤다
- 종류: PR | 규모: S | 태그: B · perf
- 목표: `checkFieldExistsInVtu` 가 존재 확인만을 위해 VTU 를 다시 읽지 않는다 — 한 번 읽은 데이터에서 필드 유무를 보고 그 데이터를 렌더에 넘긴다.
- 완료 기준: 열람 1회당 같은 VTU 읽기 1회 (로그 또는 카운터로 확인) · 렌더 결과 불변
- 변경 범위: W:performPreviewLogic (:1448-1557) · checkFieldExistsInVtu (:1558)
- 선행: -
- 충돌: RUN-28 · UIC-24 (같은 함수 `performPreviewLogic` W:1448 — UIC-24 가 시그니처에서 죽은 `row` 인자를 뺀다) · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절)
- 흡수: RUN-D5(열람 축) · RUN-c23
- 비고: 순서 — **UIC-24 가 먼저** (decisions ⑦). 시그니처 정리 뒤에 본문을 재작성한다

#### RUN-25 · 폴더 선택 스캔을 워커로 옮긴다
- 종류: PR | 규모: M | 태그: B · perf
- 목표: 폴더 열거 · `model_info.json` 파싱 · 메트릭 조회 · DV 별 GeometryParameter JSON 파싱을 `DashAsyncJobRunner`(#544) 작업 1건으로 묶어 결과 구조체를 GUI 로 넘기고, 위젯은 받은 구조체로 표 3종을 채운다. 진행 중 상태 표시. `model_info.json` 은 1회만 읽는다.
- 완료 기준: 폴더 선택 중 창이 응답한다 · 같은 폴더 선택 1회에 `model_info.json` 읽기 1회 · 진행 중 Generate/Run 비활성 · 표 내용 불변
- 변경 범위: W:populateModelBuilderFolderComboBox (:782) · populateSurrogateTable (:844) · onModelDataLoaded (:389) · M:getModelBuilderFolders (:1335) · loadModelInfoFromFolder (:1379) · loadDesignVariables (:834) · view/common/SurrogateTableController.cpp:updateModelErrorRow (:98)
- 선행: RUN-14
- 충돌: RUN-17 · RUN-27 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절) · SurrogateTableController.cpp → RUN-15 · PR #654(DashModelRunner.cpp)
- 흡수: #513 · RUN-D5(적재 축) · RUN-c08 · #463(RUN 몫 — 적재 진행 표시·버튼 비활성) · EXE-c23 · RUN-c67
- 비고: deck 파싱(`registry.load`) 몫은 EXE #458(RW 액터 스레드 이주) 이후 자동으로 워커로 간다 — 이 항목은 JSON·폴더 축만. MCU 경로는 비범위(#513). 진행 표시·버튼 비활성·반려 안내는 EXE-07 규약과 EXE-09 `DashJobGuard` 가 있으면 그것으로 — 없으면 현행 상태 애니메이션

#### RUN-26 · variant 정본을 JSON 키 하나로 한다
- 종류: PR | 규모: S | 태그: C · bug
- 목표: `writeConfigFile` 이 Set 이름 접미사로 `variant` 를 매번 덮지 않는다 — 기존 키가 있으면 유지, 없을 때(생성 시)만 기록. `detectRunnerVariant` 의 이름 접미사 폴백은 키 부재 파일이 더 없음을 확인한 뒤 제거한다.
- 완료 기준: JSON `variant` 를 손으로 바꿔도 저장이 되돌리지 않는다 · 신규 Set 생성 시 키가 기록된다
- 변경 범위: M:writeConfigFile (:576-599) · model/DashProject.cpp:detectRunnerVariant (:976)
- 선행: -
- 충돌: B2 교집합: DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · PR #654(DashModelRunner.cpp) · PR #652(DashProject.cpp) · PR #651(DashProject.cpp)
- 흡수: RUN-D2 · RUN-c20
- 비고: 접점 PRJ. 폴백 제거 여부는 기존 프로젝트 파일 조사 뒤 — 하위호환 분기를 쌓지 않는다

#### RUN-27 · view-source 컨텍스트 폴백 접근자를 하나로 만들고 `configsDir` 삼항을 지운다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `m_viewSourceContext.X.isEmpty() ? m_runtimeContext.X : m_viewSourceContext.X` 반복을 `viewSource()` 접근자 하나로, Set 무관 전역인 `configsDir` 은 RuntimeContext 에서 빼고 `getConfigsDirectory()` 직접 호출로 바꾼다.
- 완료 기준: 동작 불변 · 삼항 폴백 0건 · `RuntimeContext::configsDir` 삭제
- 변경 범위: M:calculateRuntimeContext (:476) · resolveParameterSourceLabel (:898) · getReferenceFileAndPart (:1593) · performMorphing (:2219) · readModelNormalizationFromConfig (:2487) · M.h RuntimeContext
- 선행: PR #654 (같은 함수 적용 순서)
- 충돌: RUN-14 · RUN-25 · B2 교집합: DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashModelRunner.h → RUN-05 RUN-12 RUN-13 RUN-16 RUN-29 RUN-31
- 흡수: RUN-D7 · RUN-c25

#### RUN-28 · 뷰의 MainWindow 부모 탐색·findChild·QMessageBox 결합을 걷어낸다
- 종류: PR | 규모: M | 태그: E, D · refactor
- 목표: `DashMainWindow` 를 부모 거슬러 찾는 4벌을 상태 애니메이션·CSV 뷰어·STEP 프리뷰 요청 신호(또는 주입된 인터페이스 1개)로 바꾸고, `findChild<` 5곳을 멤버 포인터로, 남은 `QMessageBox::` 7곳을 `DashNotify` 로 통일한다.
- 완료 기준: W 에서 `qobject_cast<DashMainWindow*>` 0 · `findChild<` 0 · `QMessageBox::` 0 · 동작 불변
- 변경 범위: W (:433-439 · :1383 · :1469 · :1550 · findChild 5곳 · QMessageBox 7곳) · W.h · view/DashMainWindow (신호 수신 결선)
- 선행: -
- 충돌: RUN-24 (performPreviewLogic) · UIC-17 (통지 래퍼) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunnerWidget.h → PRJ-25 RUN-09 RUN-15 RUN-29 RUN-30 UIC-24 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #652(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: RUN-D28 · RUN-c42
- 비고: 접점 PRJ(MainWindow) · UIC(통지). 다른 모듈 위젯에도 같은 패턴이 있으면 Phase B 에서 횡단 항목으로 승격 가능

#### RUN-29 · Model Runner 의 죽은 코드를 지운다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: 호출처 0 인 정의 14종, 수신처 0 인 신호 4종, 도달 불가 `fileTableFiles` 와 1-인자 `updateModelUploadConfig`, `runFESolver` 전용 멤버·헤더를 삭제한다.
- 완료 기준: 빌드·테스트 통과 · 삭제 목록 — M: onPredictButtonClicked · onResponseSurfaceButtonClicked · runFESolver(+`m_ansysLauncher`·`m_abaqusLauncher`·cae-launcher include) · savePartAsVtu · getXmlFiles · getModelList · getAvailableResponses · initializeSetConfig · getRuntimeContextForSet · updateSelectedModel(+`surrogateModelUpdated`) · 신호 `designVariablesChanged`·`surrogateModelsChanged`·`fileTableUpdated` · 1-인자 updateModelUploadConfig. W: onDeleteButtonClicked · populateAllWidgets · updateDesignVariablesFromModelInfo · syncAnalysisInputFilesToJson. PM: `fileTableFiles`
- 변경 범위: M.cpp/.h · W.cpp/.h · PM.cpp/.h
- 선행: -
- 충돌: RUN-04 · RUN-05 (updateModelUploadConfig) · RUN-13 (`syncFileTableToJson` 은 구현 대상이라 제외) · RUN-17 (`designVariablesChanged` 재도입 가능) · PR #654 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashModelRunner.h → RUN-12 RUN-14 RUN-16 RUN-27 RUN-31 RUN-34 · DashModelRunnerPresentationModel.cpp → RUN-06 RUN-10 RUN-11 RUN-12 RUN-15 · DashModelRunnerWidget.h → PRJ-25 RUN-09 RUN-15 RUN-28 RUN-30 UIC-24
- 흡수: RUN-U2 · RUN-U3 · RUN-U4 · RUN-U5 · RUN-U6 · RUN-c52 · RUN-c53 · RUN-c54 · RUN-c55 · RUN-c56
- 비고: `onDeleteButtonClicked`(체크 행 일괄 삭제)를 기능으로 원하면 별도 feature — 지금은 삭제. `runFESolver` 는 FE 실행 버튼이 없고 #653 이 Direct Launch 로 같은 요구를 덮는다

#### RUN-30 · Model Runner 에 FE Validation 버튼을 두고 Direct Launch 다이얼로그에 입력을 채워 연다
- 종류: PR | 규모: M | 태그: B, D · feature
- 목표: 버튼 클릭 → 현재 Set 의 입력 파일(체크된 케이스 1건 또는 선택 행)·Target Part·출력 폴더 `{ModelRunner_{Set}}/FEValidation/` 을 다이얼로그 `prefill(inputPath, targetPart, outputFolder)` 로 넘겨 Launcher 페이지로 연다. Done 뒤 Result Preview 자동 선택과 Direct↔Analysis Launcher 상호 배제는 #604 동작 그대로.
- 완료 기준: 버튼으로 연 다이얼로그에 세 값이 채워져 있다 · 실행 Done 뒤 Result Preview 가 열린다 · 입력 파일 생성은 이 버튼이 하지 않는다
- 변경 범위: W.cpp/.h · ui/DashModelRunnerWidget.ui · view/dialog/DashDirectLaunchDialog.cpp/.h (PR #652 의 파일 — `prefill` 진입점 신설)
- 선행: #604 (PR #652) 머지
- 충돌: RUN-28 (MainWindow 접근) · OPT-21 (같은 버튼 — prefill 진입점 공용, 먼저 머지되는 쪽이 만든다) · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunnerWidget.h → PRJ-25 RUN-09 RUN-15 RUN-29 UIC-24 · DashDirectLaunchDialog.cpp → LCH-19
- 흡수: #653(RUN 축) · RUN-c18
- 비고: 접점 LCH(다이얼로그) · OPT(동형 버튼 — RUN-c19 범위밖). 결과 처리(Set 설정으로 KPI) 는 #433 뒤 별도

#### RUN-31 · Runner가 실제 사용한 Builder 산출물 버전으로 최신성을 판정한다
- 종류: PR | 규모: M | 태그: C, A · feature
- 목표: #650 규칙으로 실제 실행에 사용한 Builder setId와 모델 버전을 기록하고 DashModelRunner::upstreamStaleReasons가 현재 생산 버전과 비교한다. Builder 참조 저장·복원·개명 해석은 RUN-34(#685) 계약을 사용한다.
- 완료 기준: 실제 사용 버전 기록·왕복, 동일 Builder 재학습 후 최신성 사유, 버전 누락·비교 불가의 PRJ-23 규칙 적용. 참조 선택만 바꿀 때 기존 결과의 출처·소비 버전은 불변이며 프로젝트 집계·VM 표시로 전달한다.
- 변경 범위: model/DashModelRunner.h (RuntimeContext · 소비 버전 기록), model/DashModelRunner.cpp (calculateRuntimeContext :476-500 · loadModelInfoFromFolder :1379-1440 · writeConfigFile 호출), (PRJ 소관) model/DashProject.cpp refreshUpstreamStaleness 쌍 추가
- 선행: BLD-18 · PRJ-23
- 충돌: RUN-14 · RUN-25 · RUN-27 (loadModelInfoFromFolder) · RUN-26 · RUN-32 (writeConfigFile) · B2 교집합: DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · DashModelRunner.h → RUN-05 RUN-12 RUN-13 RUN-16 RUN-29 · PR #654(DashModelRunner.cpp) · PR #652(DashProject.cpp) · PR #651(DashProject.cpp)
- 흡수: #650(RUN 몫) · PRJ-c37 · RUN-c58
- 비고: RUN-34와 공통 저장 경로를 조율하되 조합 핀이나 setId+이름 fallback을 도입하지 않는다. PRJ-22는 Set 판정을 호출·집계하며 VM은 표시만 한다. 참조·출처 유효성과 최신성 판정은 별개다.

#### RUN-32 · writeConfigFile·readConfigFile 을 DashSaveSystem 헬퍼로 이행한다
- 종류: PR | 규모: S | 태그: A · refactor
- 목표: `M:writeConfigFile`(:576-620 — `QFile` WriteOnly+Truncate · flush·길이 검사 직접 구현, 원자성 없음) 본문을 PER-02 가 공용 진입점으로 승격하는 **DashSaveSystem 헬퍼**(`DashSaveSystem::writeJsonFile`, `persistence/DashSaveSystem.h:59`) 호출로, `readConfigFile`(:554) 을 `readJsonFile`(:60) 로 바꾼다. 호출 9곳(:1082·:1158·:1192·:1250·:1332·:2473·:2690·:2720·:2744)과 RUN-34 의 참조 저장 호출은 시그니처 그대로. QSaveFile 원자성·0바이트/손상 구분·사유 반환·(PER-04 뒤) 버전 키가 따라온다.
- 완료 기준: M.cpp 에 `QIODevice::WriteOnly` 가 generateDatFile(:1748 .dat 산출물) 1곳뿐 / 쓰기 실패(읽기 전용 경로) 시 기존 JSON 바이트 동일 + WARN 사유 / 기존 저장·복원 동작 불변
- 변경 범위: model/DashModelRunner.cpp (writeConfigFile :576 · readConfigFile :554)
- 선행: PER-02
- 충돌: RUN-26 (writeConfigFile variant 분기) · RUN-13 (readConfigFile 재사용) · RUN-31 · RUN-34 (writeConfigFile 호출 추가) · B2 교집합: DashModelRunner.cpp → 공유 19건(deps.md 5절) · PR #654(DashModelRunner.cpp)
- 흡수: #479(RUN 몫) · #478(RUN 몫) · #480(RUN 몫) · PER-c28 · RUN-c64
- 비고: 신설 `utils/DashJsonFile` 은 중복이라 폐기 — PER-02 가 기존 `DashSaveSystem::read/writeJsonFile`(QSaveFile · Result 반환 · 테스트 보유)을 공용 진입점으로 승격한다 (decisions 3절)

#### RUN-33 · Model Runner PM 순수 함수에 단위 테스트 타깃을 둔다
- 종류: PR | 규모: S | 태그: F · refactor
- 목표: `tests/` 의 `DashModelRunner` 언급은 TestProcessRuntime 의 모듈명 문자열뿐(#489 · DEV-c24) — RUN-10 · RUN-11 이 전제한 `tests/TestModelRunnerPresentationModel.cpp` 가 없다. PM 순수 함수(`predictBaseName` · `relatedFilePathsForDeletion` · `groupCheckedPairs` · `validatePredictParams`)와 `viewmodel/DashSurrogateModelCommon::isNDModel` 을 TU 1개로 고정한다.
- 완료 기준: tests/CMakeLists.txt 에 `test_model_runner_presentation_model` 등록 · ctest 통과 / RUN-10 · RUN-11 · RUN-15 · RUN-18 의 테스트 완료 기준이 이 TU 에 들어간다
- 변경 범위: tests/CMakeLists.txt, tests/TestModelRunnerPresentationModel.cpp (신규)
- 선행: -
- 충돌: RUN-10 · RUN-11 · RUN-14 · RUN-15 · RUN-18 (고정하는 동작 — 먼저 쓰고 각 PR 이 갱신) · DEV 의 tests 인프라 항목 · B2 교집합: tests/CMakeLists.txt → 공유 12건(deps.md 5절) · PR #655(tests/CMakeLists.txt) · PR #654(tests/CMakeLists.txt) · PR #652(tests/CMakeLists.txt) · PR #651(tests/CMakeLists.txt)
- 흡수: #489(RUN 몫) · DEV-c24(RUN) · RUN-c71
- 비고: `DashModelRunner` 본체는 `DashProjectManager::Instance()` 역참조 — 모델 함수(generateDatFile 치환 등)는 경로 주입(PRJ-09) 뒤. CAD-11 · OPT-20 과 같은 형태

#### RUN-34 · Runner가 Builder를 setId로 참조하고 출처 검증 후 실행·조회·프리뷰에 사용한다 (#685)
- 종류: PR | 규모: S | 태그: C, A · feature
- 목표: #685의 소비 경계에서 Builder setId와 응답·모델·part 등 선택을 ModelRunner_{Set}.json에 저장·복원한다. #368의 공통 판독으로 Builder 산출물 출처를 검증하고 deck은 산출물 기록에서 해석한다. 현재 Runner Set의 ID를 유지하면서 다른 Builder를 선택할 수 있으며 외부 실행에는 ID로 해석한 실제 경로를 전달한다.
- 완료 기준: ① Builder 개명 후 동일 setId 참조 복원, 동명 재생성의 다른 setId와 구분 ② 다른 유효 Builder 선택·실행 가능 ③ 선택 변경만으로 기존 결과 출처 불변, 재실행 결과 덮어쓰기 때 실제 출처 갱신 ④ 필수 출처 누락·해석 불가 model_info는 재생성 안내, live parameter·이름·경로 추론 fallback과 자동 이관 금지 ⑤ 실행·조회·프리뷰가 같은 검증된 선택과 deck을 사용 ⑥ MCU 등 deck 비해당 유형은 공통 계약의 적용 관계로 판정하고 필수 출처 검증을 일괄 면제하지 않음.
- 변경 범위: model/DashModelRunner.cpp · model/DashModelRunner.h · view/DashModelRunnerWidget.cpp
- 선행: BLD-20 (#368 생산·공통 계약 완료)
- 충돌: RUN-14 · RUN-25 · RUN-27 · RUN-31 (`getReferenceFileAndPart`·`loadModelInfoFromFolder`) · RUN-32 (`writeConfigFile` 호출 추가) · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashModelRunner.h → RUN-05 RUN-12 RUN-13 RUN-16 RUN-29 · PR #654(DashModelRunner.cpp)
- 흡수: #685 (구 #368 T23 RUN 소비 몫) · #443 SI-6a ②(RUN 참조 축) · PRJ-c04(RUN 축) · RUN-c59 · RUN-c57 · LCH-c38
- 비고: PR #530은 당시 재업로드 결정 기록이며 옛 조합 ID 핀 코드를 그대로 이식하지 않는다. 생산 계약은 PER-07·BLD-20에서 재사용한다. #650 버전·최신성과 #473 결과 조작은 별도 목표이고 #681 머지 조건으로 두지 않는다. #513 워커 이관과는 공유 코드 순서만 조율하며 별도 영속 참조 체계를 만들지 않는다. 공통 검증 테스트와 Set 참조 왕복·프리뷰 수동 검증을 병행한다.

### ANA — Results Analyzer

> 기준 dev @ b08a91b3. 원자 항목은 02-claims/ANA.md. 항목 대부분이 `view/DashResultsAnalyzerWidget.cpp`(4,201줄) 한 파일을 고치므로 **같은 파일 항목은 직렬로 진행**한다 (각 항목 `충돌` 참조).

#### ANA-01 · SHAP 데이터셋 콤보 콜백에 파일 존재 가드를 둔다
- 종류: PR | 규모: S | 태그: B · bug
- 목표: `createShapWidget` 의 데이터셋 콤보 콜백이 `extractVariablesFromXml` 을 부르기 전에 형제 호출부(`onTargetDataChanged`)와 같은 `QFileInfo::exists()/isFile()` 가드를 둔다. 디렉터리·권한 거부 경로에서 콤보 조작마다 반복되던 `canOpenForRead` WARN 과 재시도가 사라진다.
- 완료 기준: 존재하지 않는 경로를 데이터셋으로 고르면 WARN 이 1회 이하로 남고 feature 콤보가 비어 있다 / 정상 XML 은 종전과 같이 채워진다
- 변경 범위: view/analyzer/DashPlotWidgetFactory.cpp (createShapWidget 람다 :1269-1290)
- 선행: -
- 충돌: ANA-14 (같은 파일 — 팩토리 죽은 진입점 삭제) · B2 교집합: DashPlotWidgetFactory.cpp → ANA-09 ANA-12 UIC-12
- 흡수: #519 · ANA-c03
- 비고: #519 가 분리 사유로 든 897줄 재포맷은 소멸 — 현재 파일은 `clang-format --dry-run` 경고 0. `canOpenForRead` 에서 사유별 캐시하는 대안은 권한 회복을 고착시킬 수 있어 채택하지 않는다.

#### ANA-02 · DashXmlParser 의 호출자 없는 리덕션 경로를 지운다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: 제품 코드 호출자가 0건인 `FieldStatistics`·`computeFieldStatistics`·`extractFieldStatistics` 와, #410 이후 `extractAllReducedValues` 로 대체된 `extractReducedValues`·`applyReduction`(Max 무음 폴백) 을 테스트와 함께 삭제한다. `reduceStd` 는 `extractAllReducedValues` 가 쓰므로 남긴다.
- 완료 기준: 다섯 심볼이 레포에 0건 / `test_xml_parser`·`TestDataLoaderCache` 통과 / `(std)` 리덕션 회귀 테스트(TestDataLoaderCache.cpp:292) 유지 / 레포에 `applyReduction` 을 지칭하는 주석이 남지 않는다 (DashDataLoader.cpp:304-307 의 "구 경로 applyReduction() 과는 다르다" 가 삭제 후 떠 있는 참조가 된다)
- 변경 범위: model/analyzer/DashXmlParser.h, model/analyzer/DashXmlParser.cpp, model/analyzer/DashDataLoader.cpp (:304-307 주석 — `knownReductions` 폴백 설명을 `applyReduction` 지칭 없이 다시 쓴다), tests/TestXmlParser.cpp (`extractFieldStatisticsSkipsMissingVariable`·`extractReducedValuesOrdersSamplesNumerically` 삭제 — 후자의 숫자 정렬 검증은 `extractAllReducedValues` 로 옮긴다), model/analyzer/DashScatter2DPlotter.h (:54 주석)
- 선행: -
- 충돌: ANA-17 (같은 파일 — 먼저 지우고 평탄화) · ANA-16 (DashDataLoader.cpp) · B2 교집합: DashXmlParser.cpp → ANA-23 · DashXmlParser.h → ANA-23 · TestXmlParser.cpp → ANA-23
- 흡수: #405 · #404(해소됨 — 닫기 제안) · ANA-c01 · ANA-c02 · ANA-c44 · ANA-D3(잔여 죽은 경로)
- 비고: #405 의 결정 지점 "reduction=None 로드맵 유무" 는 이 PR 설명에 기록하고 닫는다 — 현재 Std 를 포함한 4종 리덕션이 모두 `extractAllReducedValues` 한 경로로 나오므로 별도 통계 사슬이 필요한 호출자가 없다. 삭제 복구는 git 으로 싸다. #405 가 선행으로 못박은 **#404**(보드 밖 OPEN, "(std) 축약이 최댓값으로 떨어진다")는 038e687f(#410) 로 코드상 해소 — `extractAllReducedValues` 가 Std 실값을 돌려주고 `applyReduction` 의 Max 폴백은 죽은 경로다. 이 PR 이 그 폴백과 주석까지 지우므로 #404 는 별도 작업 없이 닫는다(닫기 사유를 PR 설명에 적는다). 해소 판정이라 CLOSE 항목을 따로 두지 않았다 — 삭제 대상이 ANA-c02 와 같은 심볼이어서 개념이 하나다.

#### ANA-03 · MCU 모델의 SHAP 지원 여부를 결정한다
- 종류: DEC | 규모: S | 태그: D · bug
- 목표: #459 "MCU Set 에서 SHAP Feature 콤보 복구" 는 현행 코드에서 성립하지 않는다 — MCU 인스턴스는 `setModelBuilderBasePath` 가 SHAP 패널 자체를 제거하고(a154a169), Sim 인스턴스는 `.dproj` 만 스캔해 루트에 있는 MCU Set 을 보지 못한다. 둘 중 하나를 정한다. (a) MCU SHAP 미지원 확정 → #459 닫고 `updateMethodWidgetsWithVariables` 의 `isMcu` CSV 분기를 ANA-14 에서 삭제. (b) 지원 → 새 feature 항목 (CSV 헤더로 feature 콤보 채우기 · 데몬 `shap` 명령의 `.h` 모델 경로 — RUN 접점).
- 완료 기준: 결정 기록 (어느 쪽이든 #459 의 처리 방식 명시)
- 변경 범위: 없음 (결정) — (a) 면 view/DashResultsAnalyzerWidget.cpp :1862-1895 가 ANA-14 로, (b) 면 신규 항목
- 선행: -
- 충돌: B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절)
- 흡수: #459 · ANA-c04 · ANA-c05
- 비고: #459 의 Related #409 는 Done — 전량 디코딩 축은 해소됐고 남은 것은 제품 결정뿐이다.

#### ANA-04 · Method 콤보 순서를 specFor 선언 순서로 맞춘다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: `setupMethods` 가 콤보·스택을 채울 때 `m_methodWidgets`(QMap, 알파벳 순) 대신 `specFor(viewType).methods` 순서로 순회한다. AnalysisLauncher 는 Box→Scatter→Parallel→Pair, ModelRunner 는 Sobol→Morris→SHAP 로 뜬다. 인덱스 잠금(콤보 인덱스 = 스택 인덱스)은 그대로다.
- 완료 기준: 두 ViewType 의 Method 콤보가 선언 순서와 같다 / `removeMethodWidget("SHAP")` 후 인덱스 잠금 유지
- 변경 범위: view/DashResultsAnalyzerWidget.cpp (setupMethods :424-452)
- 선행: -
- 충돌: ANA-05 ~ ANA-15 (같은 파일) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절)
- 흡수: ANA-D1 · ANA-c09

#### ANA-05 · initializeTargetData 중복 억제 캐시를 인스턴스 멤버로 옮긴다
- 종류: PR | 규모: S | 태그: B · bug
- 목표: 함수-로컬 `static QHash<QString, QDateTime> recentCalls` 를 멤버 타임스탬프 1개로 바꾼다. 키가 `viewType_setName` 이라 **DoeSampler Init/Resample** 의 analyzer 2개가 100ms 창을 공유하던 문제가 없어진다 — 두 변종 위젯이 각자 `viewType == DoeSampler`(=0) 인 analyzer 를 들고(DashMainWindow.cpp:1591-1608), `setModel` 이 `setSetName` 보다 먼저 `initializeTargetData()` 를 불러(DashDoeSamplerWidgetBase.cpp:80 → :83) 그 시점 키가 둘 다 `0_`(빈 Set) 로 겹친다. `m_lastMethodWidgetVariables` 가 같은 사유로 멤버가 된 선례를 따른다.
- 완료 기준: Init·Resample 두 Set 을 100ms 안에 연달아 띄워도 두 analyzer 가 모두 스캔한다 (`m_setName` 이 아직 빈 시점의 호출 포함) / 같은 인스턴스의 100ms 내 재호출은 종전처럼 건너뛴다
- 변경 범위: view/DashResultsAnalyzerWidget.h, view/DashResultsAnalyzerWidget.cpp (initializeTargetData :457-476)
- 선행: -
- 충돌: ANA-04, ANA-06 ~ ANA-15 (같은 파일) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절)
- 흡수: ANA-D2 · ANA-c10
- 비고: 색인 ANA-D2 가 든 "ModelRunner Sim/MCU" 쌍은 현행 코드에서 성립하지 않는다 — MCU 호스트가 `setSetName(currentSetName + "-MCU")`(DashModelRunnerMCUWidget.cpp:177) 라 Sim(DashModelRunnerWidget.cpp:143)과 키가 이미 다르다. 색인 좌표가 `-MCU` 접미사(a154a169 계열) 도입 전이다. RUN-22 가 그 접미사 이중 부착을 정리하다 접미사를 걷어내면 Sim/MCU 도 같은 키가 되므로 이 항목이 그때의 선행이 된다. 억제 창 자체를 없애고 호스트 5곳의 이중 호출(setModel + onTabChanged)을 정리하는 대안은 호스트 변경이 PRJ·LCH·OPT·RUN 에 걸쳐 보류.

#### ANA-06 · 타깃 콤보 스캔이 현재 Set 을 먼저 고르고 매치 실패 시 0번으로 떨어지지 않게 한다
- 종류: PR | 규모: S | 태그: C · bug
- 목표: `initializeTargetData` 세 분기에 같은 규칙을 둔다 — 현재 Set 폴더(`AnalysisLauncher_{m_setName}` · `DoeSampler_{…}` · `ModelBuilder_{m_setName}`)를 우선 선택하고, 없으면 0번 자동 선택 대신 빈 선택 + WARN. AnalysisLauncher 분기는 전량 나열 뒤 0번(:586-614), DoeSampler 분기도 0번(:616-634, Set 은 "Set1" 고정이라 실질 1건), ModelRunner 분기는 우선 선택은 하나 매치 실패 시 0번(:507-513)이라 MCU 접미사 이중 부착(RUN-22) 같은 매치 실패에서 무관한 Set 의 모델로 플롯이 나간다.
- 완료 기준: Set 2개 이상인 프로젝트에서 Analysis Launcher 분석 탭 진입 시 현재 Set 폴더가 선택돼 있다 / 현재 Set 폴더가 없으면 빈 선택 + WARN 1건 — 다른 Set 의 산출물이 자동으로 뜨지 않는다 / ModelRunner_Sensitivity 도 같은 규칙(`-MCU-MCU` 매치 실패 시 0번으로 가지 않는다) / **세 분기의 콤보 항목 툴팁에 그 Set 의 setId 가 보이고, 색인에 없는 폴더는 툴팁이 비어 있다**(#650 ANA 몫 — 표시만)
- 변경 범위: view/DashResultsAnalyzerWidget.cpp (initializeTargetData :507-513 · :586-634 — 우선 선택; `addItem` 3곳 :502 · :608 · :628 뒤에 `setItemData(…, Qt::ToolTipRole)` 로 setId 부착)
- 선행: -
- 충돌: ANA-04, ANA-05, ANA-07 ~ ANA-15, ANA-18, ANA-21, ANA-22 (같은 파일) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절)
- 흡수: ANA-D14 · ANA-c24 · RUN-D30 · RUN-c44 (RUN-22 에서 이관) · #650(ANA 몫 — 읽는 Set 표시) · PRJ-c39 · ANA-c33
- 비고: "다른 Set 산출물을 아예 숨길지" 는 설계 논점 — 최소안은 우선 선택 + 0번 폴백 제거. 필터링까지 가면 #617 Project Assets 의 Set 연동 규칙(PRJ)과 맞춰야 한다. #650 의 "읽는 Set 의 id 표시(표시만)" 에 PRJ 선행은 필요 없다 — 폴더명↔setId 역조회가 이미 public 이다 (`DashProject::setIds()`, model/DashProject.h:54 · 키는 모듈 json 파일명, model/DashSetIdentity.cpp:132). 폴더 `AnalysisLauncher_X` → `AnalysisLauncher_X.json` 으로 조회하고 미해석은 빈 툴팁(이름 폴백 금지 — SI-4). ⚠ 표시·검사 쌍 등록은 PRJ-22 몫이고 여기서는 표시만 한다. MCU 접미사 이중 부착 자체는 RUN-22.

#### ANA-07 · "Set1" 폴백 7벌을 한 접근자로 모으고 빈 Set 을 조용히 대체하지 않는다
- 종류: PR | 규모: S | 태그: C · bug
- 목표: `m_setName.isEmpty() ? "Set1" : m_setName` 7회를 접근자 하나로 바꾸고, Set 이 비어 있으면 무관한 `Set1` 산출물을 읽는 대신 WARN 후 조기 반환한다. 호스트가 `setSetName()` 전에 어느 경로를 밟아도 다른 Set 의 데이터가 조용히 뜨지 않는다.
- 완료 기준: `"Set1"` 리터럴이 파일에 0건 / `setSetName` 없이 `initializeTargetData()` 를 부르면 콤보가 비고 WARN 1건 / DoeSampler Init·Resample 진입 시 첫 스캔이 WARN 없이 해당 Set 으로 돈다 (역순 호스트 교정 확인)
- 변경 범위: view/DashResultsAnalyzerWidget.h, view/DashResultsAnalyzerWidget.cpp (:508·:522·:1025·:1099·:2487·:2989·:3733), view/DashDoeSamplerWidgetBase.cpp (`setModel` 의 :80 `initializeTargetData()` 를 :82-83 `setSetName(setName)` 뒤로 옮긴다 — 2줄)
- 선행: -
- 충돌: ANA-04 ~ ANA-06, ANA-08 ~ ANA-15 (같은 파일) · DOE-05 · DOE-11 · PRJ-25 (DashDoeSamplerWidgetBase.cpp — DOE-05 가 같은 `setModel` 경로의 `loadSettings` 중복을 정리한다) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절)
- 흡수: ANA-D15 · ANA-c25
- 비고: 호스트 5곳 중 **역순이 1곳 실재한다** — `DashDoeSamplerWidgetBase::setModel` 이 `initializeTargetData()`(:80) 를 `setSetName(setName)`(:83) 보다 먼저 부른다. "빈 Set 이면 WARN + 조기 반환" 을 넣으면 이 경로의 최초 스캔이 무효가 되므로(탭 진입 경로 :124-128 이 재초기화해 실해는 작지만 WARN 이 상시 뜬다) 두 줄 교정을 이 항목 범위에 넣었다 — 2줄짜리 호스트 교정이라 DOE 항목으로 넘기지 않는다. 나머지 4곳은 정순이다 (DashModelRunnerWidget.cpp:143-144 · DashModelRunnerMCUWidget.cpp:177-178 · DashAnalysisLauncherWidget.cpp:267-269 · DashDoeSamplerWidgetBase.cpp:124-128).

#### ANA-08 · 타깃 콤보 5종을 objectName/findChild 대신 타입 멤버로 보관한다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: `specFor` 가 만드는 타깃 콤보(TargetResults·TargetSecondary·ModelBuilder·ResponseFolder·TrainedModel)를 생성 시점에 멤버 구조체에 담고, `findChild<QComboBox*>("...")` 25회를 멤버 접근으로 바꾼다. 패널 내부 컨트롤이 `DashAnalyzerPanelControls` 로 옮겨간 것과 같은 방식이다. `objectName` 은 남겨도 되지만 분기 조건으로 쓰지 않는다.
- 완료 기준: 파일에 `findChild<QComboBox*>` 0건 / ViewType 4종 전부 종전과 같은 콤보 연쇄 동작
- 변경 범위: view/DashResultsAnalyzerWidget.h, view/DashResultsAnalyzerWidget.cpp
- 선행: -
- 충돌: ANA-04 ~ ANA-07, ANA-09 ~ ANA-15 (같은 파일) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절)
- 흡수: ANA-D5 · ANA-c13

#### ANA-09 · TextStyleGroup 수집을 타입 핸들로 바꾸고 폴백 캐스케이드를 지운다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: 팩토리가 이미 채우는 `DashAnalyzerPanelControls::textStyleGroup` 을 위젯이 읽게 하고, `findChild<QWidget*>("TextStyleGroup")` 13회와 그 뒤의 도달 불가 폴백(3열 이상 표 찾기)을 지운다. 텍스트 스타일 추출 20여 줄의 Method 별 복제를 헬퍼 하나로 모은다.
- 완료 기준: `"TextStyleGroup"` 문자열이 view/DashResultsAnalyzerWidget.cpp·view/analyzer/DashPlotWidgetFactory.cpp 두 파일에서 0건 / 팩토리의 `out.textStyleGroup` 읽기 지점 1곳 이상 / 플롯별 textSize·sigFigs 반영 동작 불변
- 변경 범위: view/DashResultsAnalyzerWidget.cpp (process*Plot 4종 + applyStyleToActivePlot), view/analyzer/DashAnalyzerPanelControls.h (핸들 타입을 `QTableWidget*` 로 좁히면 표 탐색도 사라진다), view/analyzer/DashPlotWidgetFactory.cpp (:624·:1461·:1679 의 잉여 `setObjectName("TextStyleGroup")` 삭제 — 이름은 `DashResultsAnalyzerWidget::createTextStyleGroup`(:205-208) 이 이미 항상 붙인다)
- 선행: -
- 충돌: ANA-04 ~ ANA-08, ANA-10 ~ ANA-15 (같은 파일) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · DashPlotWidgetFactory.cpp → ANA-01 UIC-12 · DashAnalyzerPanelControls.h → ANA-22
- 흡수: ANA-D7 · ANA-c15
- 비고: 잉여 `setObjectName` 3곳은 전부 **산 함수** 안이다 — :624 `createScatterPlotWidget`(:454) · :1461 `createConvergenceHistoryWidget`(:1345) · :1679 `createParetoFrontWidget`(:1479). ANA-14 가 지우는 세 함수는 :944 · :1724 · :1945 라 겹치지 않으므로 이 항목이 직접 지운다.

#### ANA-10 · 색 버튼 읽기를 getColorFromButton 한 경로로 통일한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `applyStyleToActivePlot` 의 16진수 전용 정규식 3곳(Box 색 3종·Pearson·Sobol)을 `getColorFromButton` 호출로 바꾼다. 초기값 `background-color: black` 같은 색 이름 표기가 정규식에 걸리지 않아 `Qt::black` 으로 떨어지던 불일치가 없어진다.
- 완료 기준: 파일에 `QRegularExpression rx("background-color` 0건 / 색 버튼을 바꾸지 않은 Box Plot 에서 즉시 스타일 반영 색과 Plot 색이 같다
- 변경 범위: view/DashResultsAnalyzerWidget.cpp (:4030-4045·:4138·:4187)
- 선행: -
- 충돌: ANA-04 ~ ANA-09, ANA-11 ~ ANA-15 (같은 파일) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절)
- 흡수: ANA-D6 · ANA-c14
- 비고: 정본을 스타일시트 문자열에서 버튼 동적 프로퍼티(QColor)로 옮기는 안이 더 낫지만 setter 쪽(DashPlotWidgetFactory.cpp:92-99, 위젯 :1738-1803)까지 바뀌어 M 이 된다. 최소안으로 S.

#### ANA-11 · 스핀박스 변경이 스타일 setter 와 디바운스 재플롯을 동시에 타지 않게 한다
- 종류: PR | 규모: S | 태그: B · bug
- 목표: `connectReactiveSignals` 가 스핀박스를 두 슬롯에 걸던 것을 `onStyleSettingChanged` 하나로 바꾸고, `applyStyleToActivePlot` 이 현재 위젯 타입에 setter 가 없을 때(Scatter2D·Scatter3D·Parallel·Convergence·Pareto·Morris·Shap 의 textOptions 외 설정)만 `onDataSettingChanged` 로 넘긴다. 값 하나를 바꿀 때 setter 반영 후 200ms 뒤 파일 재파싱/데몬 왕복이 한 번 더 도는 일이 없어진다.
- 완료 기준: Box Plot 에서 스핀박스 1회 변경 시 `onPlotButtonClicked` 가 불리지 않는다 / Scatter Plot 에서 setter 없는 값 변경은 종전처럼 200ms 뒤 재플롯
- 변경 범위: view/DashResultsAnalyzerWidget.h, view/DashResultsAnalyzerWidget.cpp (connectReactiveSignals :3842-3929, applyStyleToActivePlot :3960-)
- 선행: -
- 충돌: ANA-04 ~ ANA-10, ANA-12 ~ ANA-15 (같은 파일) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절)
- 흡수: ANA-D13 · ANA-c23
- 비고: 주석(:3860-3865)은 "setter 없는 설정을 받아내려는 의도" 라 적는다 — 그 의도는 반환값으로 분기하면 유지된다.

#### ANA-12 · 랭킹 표를 빌더 반환값으로 전달한다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: 민감도 빌더 3종이 랭킹 표를 플롯 위젯의 숨은 자식(`setParent(w)+hide()`)으로 실어 보내고 `onPlotWindowReady` 가 `findChild("rankingTable")` 로 꺼내던 부수 채널을 없앤다. 빌더·`DashPlotRequestHandler::build` 가 `{플롯 위젯, 랭킹 표(또는 null)}` 를 반환하고, 결합은 호출부 없는 `createPlotWithTable` 을 쓰거나 그것을 지우고 인라인 하나로 둔다. 화면 결과는 같다.
- 완료 기준: `"rankingTable"` objectName 조회 0건 / Morris·Sobol·SHAP-FI 의 표가 종전과 같은 위치에 뜬다 / `createPlotWithTable` 은 쓰이거나 삭제
- 변경 범위: view/analyzer/DashPlotWidgetFactory.h, view/analyzer/DashPlotWidgetFactory.cpp (:2440-2610), view/analyzer/DashPlotRequestHandler.h, view/analyzer/DashPlotRequestHandler.cpp, view/DashResultsAnalyzerWidget.h, view/DashResultsAnalyzerWidget.cpp (onPlotWindowReady :3607-3620·:3824-3834), view/analyzer/DashAnalyzerUtils.h/.cpp (createPlotWithTable :153)
- 선행: -
- 충돌: ANA-04 ~ ANA-11, ANA-13 ~ ANA-15 (같은 파일); ANA-15 (DashPlotRequestHandler.cpp) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · DashPlotWidgetFactory.cpp → ANA-01 UIC-12 · DashAnalyzerUtils.cpp → UIC-12
- 흡수: ANA-D11(구조) · ANA-U5(createPlotWithTable) · ANA-c20 · ANA-c21
- 비고: `DashPlotRequestHandler.cpp` 는 clang-format 미적용(dry-run 경고 78) — 건드리면 파일 전체 재포맷이 따라온다.

#### ANA-13 · PNG 저장에 랭킹 표를 포함한다
- 종류: PR | 규모: S | 태그: D · feature
- 목표: `[Save] → Image (PNG)` 가 `scrollArea`(플롯만) 대신 랭킹 표를 포함한 `outer` 를 캡처한다. GL 플롯은 `grabFramebuffer`, 표는 `grab` 으로 합성한다 (`saveAsPng` 의 기존 분기 확장).
- 완료 기준: Sobol 결과의 PNG 에 랭킹 표가 들어 있다 / 표 없는 플롯의 PNG 는 종전과 동일
- 변경 범위: view/analyzer/DashAnalyzerHelpers.cpp (ZoomableScrollArea::saveAsPng :68-93), view/DashResultsAnalyzerWidget.cpp (actPng 람다 :3751-3764)
- 선행: ANA-12, ANA-19 (같은 `saveAsPng` 를 고치고 순서가 고정 — DPR 합성을 먼저 바로잡은 위에 표를 얹는다)
- 충돌: ANA-04 ~ ANA-12, ANA-14, ANA-15 (같은 파일) · ANA-19 (saveAsPng) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · DashAnalyzerHelpers.cpp → ANA-20 ANA-21
- 흡수: ANA-D11(귀결)

#### ANA-14 · 호출부 없는 analyzer 코드를 지운다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: 도달 불가·소비 없음이 확인된 코드를 지운다. (1) 팩토리 `createUncertaintyDistributionWidget`·`createScatter2DWidget`·`createScatter3DWidget` 과 헤더 선언, (2) `onTargetDataChanged` DoeSampler 분기의 GeometryParameter·ConditionParameter·ModelBuilder·Optimizer 4갈래 (콤보는 `DoeSampler_*.json` 만 나열 — CON-D13 의 `"checked"` 읽기 :970 도 이 분기 안이라 삭제로 소멸), (3) `settings.parallel.save_json_path` 기록과 그 경로 조립, (4) 위젯 :1963 의 stale 주석, (5) ANA-03 이 (a) 로 결정되면 `updateMethodWidgetsWithVariables` 의 `isMcu` CSV 분기.
- 완료 기준: 다섯 심볼·키가 레포에 0건 / 빌드·기존 테스트 통과 / DoeSampler·AnalysisLauncher 분석 탭 동작 불변
- 변경 범위: view/analyzer/DashPlotWidgetFactory.h, view/analyzer/DashPlotWidgetFactory.cpp (:944-1055·:1724-1834·:1945-2053), view/DashResultsAnalyzerWidget.cpp (:946-1013·:2478-2491·:1963·:1862-1895)
- 선행: ANA-03 (항목 5 만)
- 충돌: ANA-01, ANA-09, ANA-12 (팩토리); ANA-04 ~ ANA-13, ANA-15 (위젯) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · DashPlotWidgetFactory.cpp → UIC-12
- 흡수: ANA-U1 · ANA-U2 · ANA-U5(팩토리 3개) · ANA-c05 · ANA-c26 · ANA-c27 · ANA-c28 · CON-D13 · CON-c13 · ANA-c31
- 비고: U1 은 "미구현" 이 아니라 삭제가 맞다 — #601 이후 DoeSampler 탭은 DOE 표만 그리고, 다른 모듈 산출물은 Analysis Launcher 탭이 XML 로 받는다.

#### ANA-15 · [Plot] 실패를 패널에 알린다
- 종류: PR | 규모: M | 태그: D · bug
- 목표: 세 계층의 조용한 실패에 같은 비모달 통지를 붙인다. (1) 호스트 모델 3종의 `requestPlot` 이 빈 spec 에서 `return` 하는 대신 `messages` 를 실은 실패를 되돌린다 (`plotSpecReady` 에 `{"error": …}` 를 싣거나 실패 시그널 1개 신설), (2) `DashPlotRequestHandler::build` 미매치와 `onPlotSpecReady` 의 조기 반환, (3) 비동기 잡 반려(`jobId.isNull()`). 패널은 Plot 버튼 근처 상태 라벨 또는 `DashNotify::warning` 으로 사유를 보여 준다. (1) 에서 `DashPlotSpecBuilder::build` 의 실재 게이트를 설정 JSON(`configFilePath`)이 아니라 데이터 파일(`target_optimum_path` · XML)로 바로잡는다(OPT-D20 — 설정은 실데이터가 아니다).
- 완료 기준: XML 미선택 상태에서 [Plot] 을 누르면 사유가 화면에 보인다 / 미지원 command 로 spec 이 와도 사유가 보인다 / **설정 JSON 이 없고 데이터 파일(`target_optimum_path` · XML)만 있어도 [Plot] 이 그려지고, 데이터 파일이 없으면 그 사유가 보인다** (현행은 `DashPlotSpecBuilder::build` 의 `configFilePath` 빈값·부재 검사 :8-22 가 유일 게이트이고 데이터 경로는 :74-120 에서 비어도 `absoluteConfigPath` 로 폴백한다) / 정상 경로 동작 불변
- 변경 범위: view/DashResultsAnalyzerWidget.h, view/DashResultsAnalyzerWidget.cpp (onPlotSpecReady :3550-3605), view/analyzer/DashPlotRequestHandler.cpp, model/analyzer/DashPlotSpecBuilder.cpp (build :8-22 게이트), model/DashDoeSampler.cpp (:1449-1462), model/DashAnalysisLauncher.cpp (:1437-1460), model/DashOptimizer.cpp (:1173-1185)
- 선행: -
- 충돌: ANA-04 ~ ANA-14 (위젯); ANA-12 (DashPlotRequestHandler.cpp); EXE-03 (#553 — 같은 함수 `onPlotSpecReady` 의 런너 호출 구조) · #433 스택 (PRE — model/DashAnalysisLauncher.cpp) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashDoeSampler.cpp → 공유 15건(deps.md 5절) · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp) · PR #654(DashOptimizer.cpp) · PR #652(DashAnalysisLauncher.cpp·DashDoeSampler.cpp) · PR #651(DashAnalysisLauncher.cpp)
- 흡수: ANA-D10 · ANA-c19 · OPT-D20 · OPT-c30 · ANA-c32
- 비고: 모델 3파일은 각 5줄 안팎이라 주 모듈은 ANA. 통지 수단은 설계 논점 — :3595 주석은 DashNotify 를 "시스템 실패용" 이라 보아 패널 내 상태 라벨이 성격에 맞다. 데몬 응답 오류(`DashModelRunner::processDaemonResponse` 가 로그만 남김)는 RUN 소관으로 같은 채널을 쓰게 한다.

#### ANA-16 · 플로터 데이터 컨테이너를 Eigen::VectorXf 에서 std::vector<float> 로 바꾼다
- 종류: PR | 규모: L | 태그: E · refactor
- 목표: `DashBasePlotter::inputs/outputs` 의 값 타입과 로더 출력, Box·Parallel·Scatter2D·Scatter3D 플로터, `normalize1d`, PearsonWidget 의 `rawVectors` 를 `std::vector<float>` 로 바꾼다. Pearson 의 공분산 계산만 `Eigen::Map<const VectorXf>` 로 감싸 Eigen 을 유지한다. analyzer 헤더에서 `<Eigen/Dense>` 가 빠져 view/analyzer 위젯의 컴파일 의존이 줄고 row/column-major 함정이 없어진다. 사용자에게 보이는 결과는 같다.
- 완료 기준: model/analyzer 헤더 중 `<Eigen/Dense>` 를 포함하는 것이 DashPearsonPlotter.h·DashXmlParser.h 뿐 / `TestDataLoaderCache` 통과 / Box·Parallel·Scatter2D·Scatter3D·Pearson 5종을 실데이터로 그려 변경 전과 눈으로 대조한 기록
- 변경 범위: model/analyzer/DashBasePlotter.h, DashBasePlotter.cpp, DashDataLoader.h, DashDataLoader.cpp, DashBoxPlotter.h, DashBoxPlotter.cpp, DashParallelPlotter.h (:14 `ParallelAxisData::normalizedVals` 가 `Eigen::VectorXf` — `DashBasePlotter.h` 에서 Eigen 이 빠지면 이 헤더가 컴파일되지 않는다), DashParallelPlotter.cpp, DashScatter2DPlotter.cpp, DashScatter3DPlotter.cpp, DashPlotterUtils.h, DashPlotterUtils.cpp, DashPearsonPlotter.h, DashPearsonPlotter.cpp, view/analyzer/DashPearsonWidget.cpp, tests/TestDataLoaderCache.cpp
- 선행: -
- 충돌: ANA-17 (DashXmlParser 는 이 항목이 건드리지 않는다 — 경계 유지) · ANA-02 (DashDataLoader.cpp) · B2 교집합: TestDataLoaderCache.cpp → ANA-23
- 흡수: #305(플로터·로더 부분) · ANA-c06
- 비고: L 사유 — `DashBasePlotter::inputs/outputs` 타입 하나가 로더·플로터 전부의 시그니처라 부분 적용이 컴파일되지 않는다 (`getVec()` 소비자 5종 Box·Parallel·Pearson·Scatter2D·Scatter3D 가 모두 그 타입을 받는다). 분할안 없음. #305 자신이 단독 착수를 권하지 않는다 — analyzer 데이터 구조를 어차피 손대는 시점에 얹는다. `percentile`·`normalize1d` 재작성 시 부동소수 결과가 미세하게 달라질 수 있다.

#### ANA-17 · DashXmlParser 의 TensorData 를 평탄 버퍼로 바꾼다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: `TensorData::matrix`(`Eigen::MatrixXf`) 를 `std::vector<float>` + `shape` 로 바꾸고 `parseTensor` 의 RowMajor `Eigen::Map` 우회와 `reduceMax/Min/Mean/Std` 의 Eigen 표현식을 평탄 루프로 바꾼다. numpy row-major 와 Eigen column-major 차이로 생기던 함정 자체가 없어진다. 파싱 결과·리덕션 값은 같다.
- 완료 기준: DashXmlParser.h 에서 `<Eigen/Dense>` 제거 / `test_xml_parser`·`TestDataLoaderCache`·`TestAnalyzerUtilsCache` 통과 (텐서 파싱 13 케이스 포함)
- 변경 범위: model/analyzer/DashXmlParser.h, model/analyzer/DashXmlParser.cpp, tests/TestXmlParser.cpp (`TensorData` 소비자는 테스트뿐)
- 선행: ANA-02 (죽은 리덕션 경로를 먼저 지워 변환 면적을 줄인다)
- 충돌: ANA-16 (Eigen 제거 축 — 경계는 파일로 나뉜다) · B2 교집합: DashXmlParser.cpp → ANA-23 · DashXmlParser.h → ANA-23 · TestXmlParser.cpp → ANA-23
- 흡수: #305(파서 부분) · ANA-c07
- 비고: `reduceStd` 의 수치는 Eigen 표현식과 수동 루프가 같은 순서로 더하지 않으면 마지막 자리가 달라질 수 있다 — 테스트는 허용 오차로 비교한다.

#### ANA-18 · 민감도 변수 목록의 원천을 model_info 의 `parameter` 키로 바꾸고 실패를 로그한다
- 종류: PR | 규모: S | 태그: C · bug
- 목표: `updateModelRunnerSecondaryCombo` 가 `Model upload.Input Design Variables.label`(Model Runner 설정 JSON 의 스키마 — GUI 는 그 키를 `ModelRunner_{Set}.json` 에만 쓴다, M:updateModelUploadConfig :1154) 대신 `DashModelRunner::loadDesignVariables` 와 같은 `parameter.*` 키에서 변수명을 읽는다. 4단 중첩 `if` 는 어디서 빠져도 WARN 1줄.
- 완료 기준: 실 `model_info.json` 으로 변수 목록이 채워진다 / 키 부재 시 로그가 남는다
- 변경 범위: view/DashResultsAnalyzerWidget.cpp (updateModelRunnerSecondaryCombo :1400-1472)
- 선행: -
- 충돌: ANA-04 ~ ANA-15, ANA-21, ANA-22 (같은 파일) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절)
- 흡수: RUN-D29 · RUN-c43 (RUN-23 에서 이관)
- 비고: Python 측 model_info.json 에 `Model upload` 블록이 있는지 실 파일로 먼저 확인 — 있으면 두 키 중 정본 결정만. 접점 RUN(키 기록 규칙). 변경 파일이 AW 뿐이라 RUN-23 을 ANA 로 옮김.

#### ANA-19 · ZoomableScrollArea 의 줌 상한과 PNG 합성을 DPR 기준으로 맞춘다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: (1) `wheelEvent` 의 `qBound(0.5, m_zoomFactor, 10.0)` 상한이 논리 px 기준이라 DPR 2 에서 FBO 가 논리 대비 4배 — 상한을 물리 px 한도(최대 FBO 변 길이 ÷ DPR)로 환산한다. (2) `saveAsPng` 가 `grabFramebuffer()`(물리 px) 위에 자식 오버레이를 `render(&p, child->pos())`(논리 px)로 그려 DPR≠1 에서 오버레이 위치·크기가 어긋난다 — `image.setDevicePixelRatio(dpr)` 또는 `p.scale(dpr, dpr)` 뒤 합성한다.
- 완료 기준: DPR 2 모니터에서 최대 줌 시 FBO 할당이 DPR 1 과 같은 물리 상한 / 저장 PNG 의 오버레이(SizeLegendOverlay) 위치가 화면과 일치 / DPR 1 결과 불변
- 변경 범위: view/analyzer/DashAnalyzerHelpers.cpp (ZoomableScrollArea::wheelEvent :100-131 · saveAsPng :68-93), view/analyzer/DashAnalyzerHelpers.h
- 선행: -
- 충돌: ANA-13 (saveAsPng) · ANA-21 (updateWidgetSize) · B2 교집합: DashAnalyzerHelpers.cpp → ANA-20
- 흡수: #447(R2·R3 — ANA 몫) · UIC-c31 · UIC-c32 · ANA-c35 · ANA-c36
- 비고: 접점 UIC(#447 DPI 카탈로그). 200% 실기 검증 필요

#### ANA-20 · GL 뷰포트 설정 관행을 하나로 한다 — resizeGL 인자 단위 실측 후 통일 또는 삭제
- 종류: INV | 규모: S | 태그: D · bug
- 목표: `DashTimeSeriesGLWidget::resizeGL` 은 `glViewport(0,0,w,h)`, 나머지(`DashPlotWidgetBase`·Box·Scatter2D·ShapDependence)는 `calculateViewport`(논리×DPR, `static_cast<int>` 절삭). Qt6 `QOpenGLWidget::resizeGL` 의 w/h 단위와 paintGL 직전 Qt 가 재설정하는 viewport 를 DPR 2 에서 1회 실측해 (a) resizeGL 의 glViewport 가 무의미하면 전부 삭제, (b) 의미 있으면 TimeSeries 도 `calculateViewport` 로 통일하고 절삭을 `qRound` 로 바꾼다.
- 완료 기준: 실측 결과 기록(인자 단위 · paintGL 전 viewport) + 후속 S PR 1건(삭제 또는 통일)
- 변경 범위: (조사) view/analyzer/DashTimeSeriesWidget.cpp (:64-67), view/analyzer/DashAnalyzerHelpers.cpp (calculateViewport :179-190), view/analyzer/DashPlotWidgetBase.cpp (:30-34)
- 선행: -
- 충돌: B2 교집합: DashAnalyzerHelpers.cpp → ANA-13 ANA-19 ANA-21
- 흡수: #447(R4 — ANA 몫) · UIC-c33 · ANA-c37

#### ANA-21 · ZoomableScrollArea 의 크기 정책을 한 메서드로 통일한다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: `updateWidgetSize`(min==max 고정)와 `autoFitToViewport`(min=원본·max=무제한)가 같은 콘텐츠 위젯에 다른 정책을 번갈아 적용하고, `onPlotWindowReady` 도 컨테이너에 min==max(800×600)를 미리 건다. 줌 상태(배율·자동맞춤)를 적용하는 메서드 하나(`applyZoom(scale)`)로 모아 정책을 한 곳에서 정하고, `setOriginalSize`·`resetZoom`·`wheelEvent`·`resizeEvent` 는 그 메서드만 부른다.
- 완료 기준: 수동 줌 → 리사이즈(자동맞춤 해제 상태) → 리셋 순서로 콘텐츠 크기가 각 단계의 기대값과 같다 / `setMinimumSize`·`setMaximumSize` 호출이 ZoomableScrollArea 안 1곳 + onPlotWindowReady 0곳
- 변경 범위: view/analyzer/DashAnalyzerHelpers.cpp (updateWidgetSize :144-153 · autoFitToViewport :155-176 · setOriginalSize :51 · resetZoom :59), view/analyzer/DashAnalyzerHelpers.h, view/DashResultsAnalyzerWidget.cpp (onPlotWindowReady :3650-3653)
- 선행: -
- 충돌: ANA-19 (wheelEvent → updateWidgetSize) · ANA-04 ~ ANA-15, ANA-18 (위젯) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · DashAnalyzerHelpers.cpp → ANA-20
- 흡수: #449(L3-3 — ANA 몫) · UIC-c35 · ANA-c38

#### ANA-22 · [Plot] 실행을 EXE 가드·진행 표시 표준에 결선한다
- 종류: PR | 규모: S | 태그: B, D · feature
- 목표: `onPlotSpecReady` 가 `DashAsyncJobRunner::run` 에 넣는 prefetch 잡 동안 Plot 버튼(패널 컨트롤)을 `DashJobGuard`(EXE-09)로 비활성·복구하고, 상태바 문구·취소는 EXE-08 의 훅(label)에 맡긴다. 반려(`jobId.isNull()`) 안내는 ANA-15 의 채널을 쓴다. 파일 전체에 `setEnabled(false)`·`QProgressBar` 가 0건 — ANA 의 긴 실행은 플롯 prefetch 1종뿐이다.
- 완료 기준: 대용량 XML 플롯 중 Plot 버튼 비활성 · 완료/실패 후 복구 / 디바운스 재플롯(onDataSettingChanged)이 가드에 막혀 반려될 때 안내 1건 / 동기 경로(data-only spec · .json)는 가드를 타지 않는다
- 변경 범위: view/DashResultsAnalyzerWidget.cpp (onPlotSpecReady :3575-3604 · onPlotButtonClicked), view/analyzer/DashAnalyzerPanelControls.h (Plot 버튼 핸들 추가 — 현재 shap 콤보 4종 등 패널 컨트롤만)
- 선행: EXE-07 · EXE-09 · ANA-15
- 충돌: ANA-04 ~ ANA-15, ANA-18, ANA-21 (위젯) · EXE-08 (같은 파일에 문구 지정) · EXE-03 (#553) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절)
- 흡수: #463(ANA 몫) · EXE-c23 · ANA-c43
- 비고: SHAP/Sobol/Morris 데몬 왕복은 RUN 소관 Job(#513) — 여기서는 플롯 prefetch 만

#### ANA-23 · 결과 XML 의 새 스키마(Set 단위 누적 · 위상 1회)를 analyzer 파서가 수용한다
- 종류: PR | 규모: S | 태그: A · feature
- 목표: PRE-30(Set 파일 하나에 응답 누적)·PRE-31(위상 2키를 파일당 1회만 기록)이 랜딩한 포맷을 `DashXmlParser` 가 읽게 한다. (1) 변수 목록을 첫 샘플 하나가 아니라 샘플 전체(또는 누적된 응답 전체)에서 모아 뒤에 추가된 응답의 변수가 빠지지 않게 한다. (2) `sortedSampleKeys` 가 샘플이 아닌 최상위 키(`model_info` 와 PRE-30 이 추가하는 키)를 샘플로 세지 않게 키 집합을 명시한다. (3) 샘플 0 에만 있는 위상 키 전제를 테스트로 고정한다. 읽는 값은 포맷 변경 전과 같다.
- 완료 기준: PRE-30 형식의 누적 XML(응답 2개)에서 두 응답의 변수가 모두 타깃 콤보에 뜬다 / PRE-31 형식(위상은 샘플 0 에만)에서 리덕션 값이 변경 전과 같다 / 샘플 수가 최상위 키 수와 어긋나는 파일에서 `extractAllReducedValues` 가 비샘플 키를 건너뛴다 / `test_xml_parser`·`TestDataLoaderCache` 통과 (새 포맷 픽스처 추가)
- 변경 범위: model/analyzer/DashXmlParser.h, model/analyzer/DashXmlParser.cpp (`sortedSampleKeys` :388-395 · `extractReducedValues` :397 · `extractAllReducedValues` :494 · `variableNamesFromXmlValue` :554 · `extractVariablesFromXml` :590-713 중 첫 샘플 선정 :629-651 과 변수 수집 :687-690), tests/TestXmlParser.cpp, tests/TestDataLoaderCache.cpp
- 선행: PRE-29 (포맷·식별자 결정 — 이것이 "안 바꾼다" 로 끝나면 이 항목은 소멸) · PRE-30 · PRE-31
- 충돌: ANA-02 · ANA-17 (같은 파일 DashXmlParser — ANA-17 의 평탄 버퍼 전환 뒤에 오는 편이 작다) · B2 교집합: TestDataLoaderCache.cpp → ANA-16
- 흡수: PRE-30(`보류: ANA 몫`) · PRE-31(`보류: ANA 몫`) · ANA-c45 · #643 추가 3(ANA 몫 — 스키마 축)
- 비고: 위상 2키는 `unconsumedTensorKeys()`(:67-70) 가 양쪽 추출 경로에서 이미 건너뛰므로 PRE-31 쪽 수용 부담은 전제 확인·테스트 고정뿐이다. 실제 변경량은 PRE-30 의 누적 구조가 "샘플 dict 안의 키 추가" 인지 "최상위 키 추가" 인지에 달렸다 — 전자면 (1) 만, 후자면 (1)(2) 둘 다. 컨테이너 자체를 바꾸는 HDF5 전환(#643 추가 3 의 다른 축 · ANA-c41)은 PRE-29 가 그쪽으로 결정할 때 별 항목으로 신설한다. BLD 로더 수용은 BLD-14.

### OPT — Optimizer

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> 기준: dev @ b08a91b3. 원천·판정은 02-claims/OPT.md. 담당 이슈 #316·#457 은 Backlog.
> 열린 PR 7건 중 머지 대상 6건(#651 #652 #654 #655 #656 #658) — #530 은 재업로드 노선이라 대기 대상이 아니다(decisions ⑩). OPT 항목과 파일이 겹치는 것은 셋뿐이다: `tests/CMakeLists.txt`(#651 #652 #654 #655 → OPT-20) · `view/DashMainWindow.cpp`(#651 #652 #654 #655 → OPT-22) · `model/DashOptimizer.cpp`(#654 → M 을 고치는 전 항목). **#656 · #658 은 OPT 교집합 0** — 런처·preprocessor·Rw 계열만 고친다(open_prs.md 재갱신본) → 선행·충돌 등재 없음.
> #530의 OPT 수정 지점은 OPT-26(#685)의 현행 참조·출처 계약으로 다시 작성한다. 당시 hunk 이식 결정은 기록으로 보존하며 조합 핀은 복원하지 않는다.
> 번호: **OPT-03 · OPT-04 는 결번** — 둘 다 OPT-26 으로 흡수(2026-10-06, 검토 #3·#4·#5). 사유는 OPT-26 비고.
> 파일 약칭: W = view/DashOptimizerWidget.cpp · Wh = view/DashOptimizerWidget.h · M = model/DashOptimizer.cpp · Mh = model/DashOptimizer.h · PM = viewmodel/DashOptimizerPresentationModel.cpp/.h

#### OPT-01 · Render Preview 를 비파괴 오버레이로 바꾼다 — 산출 .vtu 를 preview actor 로 겹치고 registry·BASE 레이어·카메라를 건드리지 않는다
- 종류: PR | 규모: M | 태그: A, E · bug
- 목표: 프리뷰 격자를 `performMorphing` 이 쓴 `Preview_*.vtu` 에서 읽어 전용 preview actor(반투명) 로 기존 씬 위에 겹친다. `removeAnalysisModelActor`·`GetActors()` 전량 제거·`clearLayer` 3종·`setDisplayedContext`·`updateAllGeometry`·무조건 `resetCamera` 를 없앤다. 등록·해제는 `DashRenderingManager` 의 preview actor API 를 거치고, `displayedContextChanged`(다음 Load) 와 재프리뷰에서 이전 actor 를 해제한다. `.vtu` 삭제 코드와 `performMorphing` 의 `_input_geometry.vtu` 추출(14단계) 을 제거한다.
- 완료 기준: (1) Preview 뒤 `registry.displayedFilePath()` · Modeling Tree · Mesh View 제목 불변 (2) 타 모듈 actor(핸들 5종 · FE 조건 하이라이트) 가 renderer 에 남고 `hasFeConditionHighlight()` 가 실제 상태와 일치 (3) 씬에 geometry 가 있으면 카메라 유지, 비어 있으면 리셋 (4) 다음 Load 또는 재프리뷰에서 이전 preview actor 해제 (5) `Preview_*.vtu` 가 남고 `_input_geometry.vtu` 는 생성되지 않음
- 변경 범위: W, Wh (preview actor 멤버 · 해제 슬롯), M (`performMorphing` 14단계 제거), controller/DashRenderingManager.h · controller/DashRenderingManager.cpp (전용 `add/removePreviewActor` 신설 — 레이어·scalar bar 미파괴 · `LAYER_MORPHING` 과 별도 슬롯)
- 선행: -
- 충돌: OPT-26 · OPT-21 (W 같은 함수·파일) · REN-07 (#318 소유자 태그 API 가 먼저 오면 등록 API 교체) · REN-05 · REN-08 · REN-09 · REN-10 · REN-12 (DashRenderingManager — REN 이 선언한 직렬 사슬) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashRenderingManager.cpp → 공유 10건(deps.md 5절) · DashOptimizerWidget.h → OPT-05 OPT-06 OPT-13 OPT-18 OPT-22 PRJ-25 UIC-22 · DashRenderingManager.h → PRJ-04 · PR #654(DashOptimizer.cpp)
- 흡수: #316 · OPT-D17 · OPT-D18 · #318(부류 3 ⑫) · OPT-c01, c02, c03, c04, c06, c07, c27 · OPT-c43, c44, c45 (← REN-c19, REN-c30, REN-c32)
- 비고: 기존 `addMorphingPreviewActor` 재사용은 불가다 — RESULT·COMPONENT 레이어와 scalar bar 를 지우고(controller/DashRenderingManager.cpp:1288-1293, 완료 기준 (2) 와 정면 충돌) 저장 슬롯이 `m_actors[LAYER_MORPHING]` 단일이라 Morphing Settings 프리뷰와 자리를 다툰다. 그래서 전용 API 신설을 변경 범위에 무조건 올렸다 (검토 #9). REN-10 이 OPT-01 을 선행으로 두므로(03-items/REN.md REN-10 선행) DashRenderingManager 직렬 사슬에서 OPT-01 이 REN-10 보다 앞에 온다 — REN 의 직렬 규칙 목록(REN-05·07·08·09·10·12)에 OPT-01 을 넣는 것은 `보류: REN 몫`. 소유자 태그·질의는 #318 몫 — 여기서는 태그 없이 성립. #315(Load 재클릭 게이트) 의 선행.

#### OPT-02 · 프리뷰 산출물의 위치·이름·수명을 정한다
- 종류: DEC | 규모: S | 태그: A, C
- 목표: `Preview_{col}_{template}_{ts}.dat/.inp` · `Preview_{col}_{ts}.stp`(·`.vtu`) 가 사용자 루트 `Optimizer_{Set}/` 에 타임스탬프로 누적되고 프로젝트 파일 트리에 `Load` 버튼까지 붙는 현행에 대해 (a) `.dproj` 내부로 이동(트리 비노출) (b) `Optimizer_{Set}/preview/` 하위 + 트리 필터 (c) 현행 위치 유지 + 재프리뷰 시 이전 파일 삭제 — 중 하나를 기록한다. #653 FE Validation 이 "그 Set 의 입력 파일" 로 무엇을 집을지(Preview_*.inp 인지 별도 생성 버튼 산출물인지) 를 함께 정한다.
- 완료 기준: 결정 기록 — 위치 · 이름 규칙 · 보존 개수 · 트리 노출 여부 · #653 의 입력 파일 정의
- 변경 범위: - (결정 후 PR: W, M `performMorphing` 출력 경로)
- 선행: -
- 충돌: B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · PR #654(DashOptimizer.cpp)
- 흡수: #316(산출물 위치) · OPT-c05
- 비고: 트리 Load 버튼은 확장자 규칙(view/delegate/ProjectFileTreeDelegate.cpp:46) 이라 파일이 보이는 한 붙는다. (a) 면 `getModuleDir` 의 내부/외부 분기(controller/DashIOController.cpp:31-36) 에 예외가 생긴다 — PER 접점.

#### OPT-05 · 최적화 Job 의 시작·실패·완료를 위젯에 결선한다
- 종류: PR | 규모: S | 태그: B, D · bug
- 목표: `DashOptimizer` 가 실행 상태 변화(시작·종료) 를 시그널로 내고 위젯이 Run 버튼을 잠그고 푼다. `optimizationFailed` 를 위젯에 연결해 사유를 `DashNotify::error` 로 띄운다.
- 완료 기준: (1) 실행 중 Run 비활성 + 상태 텍스트, 종료 시 복원 (2) exe 비정상 종료 · 구속 연산자 누락 · ProjectManager/IOController 부재 세 경로 모두 사용자에게 사유 표시 (3) `m_currentJob` 가드의 "already running" 경로가 수동으로 도달 불가
- 변경 범위: M, Mh, W, Wh
- 선행: -
- 충돌: OPT-06 · OPT-17 · OPT-18 (setModel 연결 블록 · 모델 시그널 블록) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashOptimizerWidget.h → OPT-01 OPT-13 OPT-21 OPT-22 PRJ-25 UIC-22 · DashOptimizer.h → OPT-07 OPT-15 OPT-16 OPT-23 OPT-26 · PR #654(DashOptimizer.cpp)
- 흡수: OPT-D11 · OPT-D13 · #463(OPT 몫 — Run) · OPT-c21, c23 · OPT-c48, c50, c51 (← UIC-c55, EXE-c44, EXE-c23)
- 비고: Set 전환 중 상태는 setModel 재바인딩에서 재계산 — LGE fit 버튼 선례(W:187-191). 성공 통지의 모달 2개(QMessageBox + `QDialog::exec`) 정비는 UIC 통지 표준 몫. 진행 표시·재클릭 가드 형식은 EXE-07 규약·EXE-09 헬퍼를 따른다 — #463 확산의 OPT 몫(Run 버튼). Preview 버튼은 OPT-22.

#### OPT-06 · DV Fixed · Init. Value · 목적 방향 편집을 모델에 즉시 반영한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: Fixed 체크 → `updateDesignVariableOptimizeFlags`, Init. Value 스핀/콤보 → `updateDesignVariableValues`, Minimize/Maximize 콤보 → `updateObjectiveFunction` 을 편집 시점에 호출한다. Run 의 강제 동기화는 그대로 둔다 (셀 편집 중 Run 대비).
- 완료 기준: (1) 세 값을 바꾸고 Run 없이 Set 전환 후 복귀하면 모델 값 유지 (2) LGE 피팅 결과가 위젯 쓰기 → 시그널로 `m_designVariables` 에 도달 (3) populate 중 재진입 없음 (`m_isPopulating` / blockSignals)
- 변경 범위: W, Wh
- 선행: -
- 충돌: OPT-05 · OPT-09 · OPT-12 · OPT-13 (W) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizerWidget.h → OPT-01 OPT-18 OPT-21 OPT-22 PRJ-25 UIC-22
- 흡수: OPT-D6 · OPT-D7 · OPT-D22 · OPT-c16, c17, c34
- 비고: 행 단위 setter 가 없어 벡터 전체를 다시 읽어 넘긴다 — `readConstraintsFromTable` 선례. 파일 영속화 시점은 OPT-07.

#### OPT-07 · Run 이외의 저장 시점을 둔다 — Set 이탈과 프로젝트 저장에서 saveSettings
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `setModel` 교체로 Set 을 떠날 때와 프로젝트 저장 시 `saveSettings()` 를 부른다. 포맷 불변.
- 완료 기준: (1) 설정 편집 → Run 없이 Set 전환 → 재시작 후 복원 (2) 편집하지 않은 Set 의 JSON 은 재기록되지 않음 (dirty 플래그) (3) 저장 실패 시 로그
- 변경 범위: M, Mh, W
- 선행: OPT-06
- 충돌: OPT-15 (saveSettings) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashOptimizer.h → OPT-05 OPT-16 OPT-18 OPT-23 OPT-26 · PR #654(DashOptimizer.cpp)
- 흡수: OPT-D12 · OPT-c22
- 비고: 프로젝트 저장 훅은 PRJ(DashProject 저장 경로) 접점 — 다른 모듈 Set 의 저장 호출 선례를 따른다. 대안 "편집 즉시 저장" 은 되돌리기가 없어 채택하지 않는다.

#### OPT-08 · 응답·설계변수 심볼의 정본을 모델 하나로 통일한다
- 종류: PR | 규모: S | 태그: C, A · bug
- 목표: 표시 심볼을 `info.symbol` 에서 읽고(행 인덱스 재생성 제거), 설정 JSON 복원 시 심볼은 응답·파라미터 이름에 붙은 값을 쓰며, 이름 집합이 바뀌면 새 항목만 다음 번호를 받고 기존 번호는 유지한다. 목적·구속 수식에 존재하지 않는 심볼이 있으면 경고.
- 완료 기준: (1) 응답 1개 추가·삭제 후 기존 `r{n}` 매핑 불변 (2) 수식 토큰이 없는 심볼이면 populate 시 경고 (3) 저장 JSON 의 symbol 과 표시가 동일
- 변경 범위: M, W
- 선행: -
- 충돌: OPT-14 · OPT-16 (loader) · OPT-20 · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · PR #654(DashOptimizer.cpp)
- 흡수: OPT-D24 · OPT-c28
- 비고: 대안 "재채번 + 수식 자동 치환" 은 DashOptiDeepOpt 가 symbol 을 키로 쓰므로 불리. Analysis Launcher 의 PRE-D26(`v{n}`) 과 같은 기제 — 결정을 공유한다.

#### OPT-09 · ModelBuilder 폴더 변경 시 설정 UI 와 모드를 함께 갱신한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `onModelBuilderFolderChanged` 가 `populateAllWidgets` 와 같은 순서(두 표 → 모드 색인 → `populateOptimizationSettings` → `onOptimizationModeChanged`) 를 밟도록 공통 재구성 함수로 묶는다.
- 완료 기준: (1) 폴더 전환 후 수식·구속·방법·모드가 새 폴더 기준 (2) 재진입 없음
- 변경 범위: W
- 선행: -
- 충돌: OPT-06 · OPT-13 · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절)
- 흡수: OPT-D3 · OPT-c13

#### OPT-10 · 대리모델 표의 1D/ND 지표 열을 행 단위로 정한다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: 첫 행 판정으로 표 전체 열을 여닫지 않는다. 1D·ND 행이 섞이면 양쪽 열을 모두 보이고 해당 없는 칸은 "-". `(Field)` 판정은 새 복사본을 만들지 않고 RUN-15 가 `DashSurrogateModelCommon` 에 정본화하는 응답 표시 이름 술어를 호출해 쓴다 — 정본은 학습 시점에 model_info 에 기록된 응답 속성이다.
- 완료 기준: (1) 1D+ND 혼합 model_info 에서 두 행의 지표가 모두 보임 (2) 단일 종류일 때 현행과 같은 열 집합 (3) W 에 `contains("(Field)")` 직접 판정 0건 · 괄호 제거 인라인 0건 — 전부 공용 술어·`strippedResponseName` 호출
- 변경 범위: W (`onSurrogateModelUpdated` :556 · `populateSurrogateTable` :867 — `(Field)` 직접 판정 2곳), PM (행 단위 열 집합 산출)
- 선행: RUN-15 (공용 `(Field)` 술어 정본화 — 같은 PR 이 RUN 전용 `view/common/SurrogateTableController.cpp` 도 함께 거둔다)
- 충돌: OPT-20 · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizerPresentationModel.cpp → OPT-12 OPT-14 OPT-15
- 흡수: OPT-D4 · OPT-c14
- 비고: ⑦ RUN-15 ↔ OPT-10 **확정** — 변경 파일 수 RUN-15 4(RunnerWidget · SurrogateTableController · DashSurrogateModelCommon · RUN PM) 대 OPT-10 2(W · PM) 로 **RUN-15 가 공용 술어·컨트롤러를 맡고 OPT-10 이 선행 소비자**다. `SurrogateTableController` 는 공용이 아니라 RUN 전용(소비자 `DashModelRunnerWidget`·`DashModelRunnerMCUWidget` 2곳)이라 파일 교집합이 없고 충돌이 아니다 — RUN-15 쪽 보강은 반영 완료(03-items/RUN.md RUN-15 완료 기준 (1)·변경 범위). 정본이 응답 속성인 코드 근거(접점 BLD): Model Builder 가 `(Field)` 를 `baseDim == 3 && reduction == "None"` 에서 붙이고(`viewmodel/DashModelBuilderPresentationModel.cpp:responseDisplayText` :174-178) 같은 술어가 `effectiveModelDimension`(:188) 의 `isND` 이며, 그 표시 이름이 `getOutputResponseList`(`view/DashModelBuilderWidgetBase.cpp:299`) 를 거쳐 model_info 로 간다 — 즉 model_info 의 `(Field)` 는 학습 시점 ND 결정이고 모델 이름 접두(`isNDModel`) 가 아니다. `(Field)` 판정은 전체 6곳(+생산 1) 이고 OPT 몫은 2곳. :558-561 의 괄호 제거 인라인도 이미 있는 공용 `DashSurrogateModelCommon::strippedResponseName`(.h:34) 과 같은 규칙이라 함께 호출로 바꾼다. BLD 2곳(`DashModelBuilderWidget.cpp:1089`·`:1681`)은 대응 항목이 없어 범위 밖.

#### OPT-11 · 최적화 모드 2차 판정을 양방향 재평가로 바꾼다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `loadDesignVariables` 의 색인 승격을 "model_info 1차 판정 OR 설정 JSON mean/std 존재" 의 재계산으로 바꿔 둘 다 없으면 0 으로 내린다.
- 완료 기준: (1) JSON 의 mean/std 가 제거되고 model_info 도 결정론이면 색인 0 (2) 기존 승격 케이스 동일
- 변경 범위: M
- 선행: -
- 충돌: OPT-16 · B2 교집합: DashOptimizer.cpp → 공유 17건(deps.md 5절) · PR #654(DashOptimizer.cpp)
- 흡수: OPT-D5 · OPT-c15
- 비고: 사용자 모드 선택(U1) 은 예정 기능 — 제외 유지.

#### OPT-12 · [+] 구속 행을 placeholder 로 심고 편집 확정 전엔 모델에 넣지 않는다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: 새 행은 회색 예시로 두고 `collectConstraintRows` 가 placeholder 행을 건너뛴다. 편집 확정(`itemChanged`) 시 보통 아이템으로 승격. 초기 회색 예시 행 0(`"r1 <= 163.23"`, `configureOptimizationSettingsGroup`) 도 같은 placeholder 규칙을 탄다 — 샘플 값이 저장 설정에 들어가지 않는다.
- 완료 기준: (1) [+] 후 편집 없이 Run → 구속 수 불변 · 초기 예시 행 0 도 수집되지 않음 (2) 편집 확정 후 모델에 1건 추가 (3) placeholder 행(초기 행 포함)이 저장 JSON 에 없음
- 변경 범위: W, PM
- 선행: -
- 충돌: OPT-06 · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizerPresentationModel.cpp → OPT-10 OPT-14 OPT-15
- 흡수: OPT-D8 · #483(OPT 샘플 행 몫) · OPT-c18 · OPT-c49 (← DEV-c30)

#### OPT-13 · 방법 옵션 기본값 주입을 사용자 변경 시에만 한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `onMethodSelectionChanged` 는 라벨·가시성만 바꾼다. 기본값은 사용자가 콤보를 바꿨고 그 방법의 편집값이 없을 때만 넣는다. 복원은 호출 순서에 의존하지 않는다.
- 완료 기준: (1) iteration 500 → 방법 변경 → 되돌림 → 500 유지(세션 내) (2) 저장값 복원이 `populateOptimizationSettings` 의 호출 순서와 무관 (3) 처음 고른 방법은 기본값 표시
- 변경 범위: W, Wh
- 선행: -
- 충돌: OPT-06 · OPT-09 · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizerWidget.h → OPT-01 OPT-05 OPT-18 OPT-21 OPT-22 PRJ-25 UIC-22
- 흡수: OPT-D10 · OPT-c20
- 비고: 방법별 편집값을 위젯이 맵으로 들면 "되돌림 유지" 가 성립. 모델 `m_methodOptions` 는 현재 방법 1벌만 — 그대로 둔다.

#### OPT-14 · 검증 표 헤더 분류를 모델이 아는 심볼·이름 대조로 바꾼다
- 종류: PR | 규모: S | 태그: C · bug
- 목표: `classifyValidationHeaders` 가 `startsWith("r")` 규칙 대신 호출자가 넘긴 응답 심볼 집합·설계변수 이름 집합으로 분류한다. objective/constraint/id 규칙은 유지.
- 완료 기준: (1) `r2_thickness` 설계변수가 DV 표로 (2) 기존 optimum.json 의 분류 결과 동일 (3) PM 단위 테스트
- 변경 범위: PM, W
- 선행: OPT-08
- 충돌: OPT-20 · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizerPresentationModel.cpp → OPT-10 OPT-12 OPT-15
- 흡수: OPT-D14 · OPT-c24

#### OPT-15 · ModelBuilder Set 선택을 setId 로 보유하고 설정 JSON 에 왕복한다
- 종류: PR | 규모: S | 태그: A, C · bug
- 목표: OPT-26(#685)의 Builder setId 저장·복원 계약에 따라 기존 선택·저장 경로를 연결한다. 이름은 표시용으로만 쓰고 실행 시 #520 역조회로 실제 경로를 얻는다. 현재 Optimizer ID를 유지하면서 다른 유효 Builder 참조로 변경할 수 있다.
- 완료 기준: 선택·저장·재시작 후 동일 Builder setId 복원. 개명 후 같은 Set을 해석하고 삭제·동명 재생성은 다른 Set으로 판정한다. 참조나 필수 출처를 해석할 수 없으면 명시적 재선택·재생성 안내를 내며 이름/폴더 우선순위로 자동 대체하지 않는다.
- 변경 범위: M, Mh, W, PM (`selectModelBuilderFolder`)
- 선행: OPT-26
- 충돌: OPT-07 · OPT-23 · OPT-24 (saveSettings) · OPT-16 (로더) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashOptimizer.h → OPT-05 OPT-18 OPT-26 · DashOptimizerPresentationModel.cpp → OPT-10 OPT-12 OPT-14 · PR #654(DashOptimizer.cpp)
- 흡수: OPT-D21 · #443 SI-6a ②(OPT 몫) · OPT-c33 · OPT-c53 (← PRJ-c04)
- 비고: OPT-26과 별도 ID 저장 체계를 만들지 않는다. PRJ-18 개명 오류 수정과 공유 경로 적용 순서만 조율하며 #685를 #681 머지 조건으로 두지 않는다.

#### OPT-16 · model_info.json 로더 3곳을 정화 규칙 1벌의 리더로 통합한다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: M 의 인라인 정화 복제 2곳(`loadModelInfoFromFolder` :757-764 · `loadModelInfoJson` :1302-1309)과 무정화 경로 1곳(`loadAllData` :572)이 공용 `DashSurrogateModelCommon::sanitizedModelInfoJson` 을 쓰는 읽기 함수 하나를 지난다. 진입 시 설정 JSON 재독은 1회로.
- 완료 기준: (1) NaN 포함 model_info.json 이 세 경로 모두에서 같은 문서로 파싱 (2) 기존 수치 동일 (3) 리더 단위 테스트
- 변경 범위: M, Mh
- 선행: -
- 충돌: OPT-08 · OPT-11 · OPT-15 (모델 로더) · OPT-26 (M 로더) · OPT-20 · B2 교집합: DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashOptimizer.h → OPT-05 OPT-07 OPT-18 OPT-23 · PR #654(DashOptimizer.cpp)
- 흡수: OPT-D1 · OPT-c11
- 비고: PM `sanitizedModelInfoJson` 은 이미 공용 함수로 포워딩하므로 정리 대상이 아니다 — 변경 범위에서 PM 을 뺐다 (검토 #10). 공용 함수 본문은 그대로 둔다.

#### OPT-17 · setModel(nullptr) 이 표를 비우고 위젯을 비활성으로 둔다
- 종류: PR | 규모: S | 태그: A, D · bug
- 목표: 모델이 null 이면 세 탭의 표·수식·콤보를 clear 하고 `setEnabled(false)` 로 끝난다.
- 완료 기준: (1) Set 삭제 후 화면이 비고 Run 비활성 (2) 다른 Set 선택 시 정상 복귀
- 변경 범위: W
- 선행: -
- 충돌: OPT-05 (setModel) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절)
- 흡수: OPT-D2 · OPT-c12 · OPT-c42 (← PRJ-c58)

#### OPT-18 · 도달하지 않는 선언 4종과 로그 전용 showEvent 를 지운다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `m_resultCsvPath` · `predictBtn` · `m_soraLabel`(생성·숨김 코드 포함) · `settingsSaved` 와 `showEvent` 오버라이드 제거.
- 완료 기준: (1) 심볼 4종 참조 0 (2) 빌드·동작 불변
- 변경 범위: W, Wh, M, Mh
- 선행: -
- 충돌: OPT-05 (모델 시그널 블록) · OPT-07 (`settingsSaved` 에 수신처가 생기면 제외) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashOptimizerWidget.h → OPT-01 OPT-06 OPT-13 OPT-21 OPT-22 PRJ-25 UIC-22 · DashOptimizer.h → OPT-15 OPT-16 OPT-23 OPT-26 · PR #654(DashOptimizer.cpp)
- 흡수: OPT-U2 · OPT-D9(잔재) · OPT-c19, c31

#### OPT-19 · LGE 피팅의 학습 모델 경로를 IOController 를 거쳐 만든다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `runFitVariables` 가 `getModuleDir(ModelBuilder, <상수>)` 를 쓰고 Set 이름 상수는 `LGE_SpringRule.h` 에 둔다.
- 완료 기준: (1) 경로 문자열 조립 0건 (2) LGE 빌드에서 피팅 동작 불변
- 변경 범위: M, model/extensions/enterprise/LGE_SpringRule.h
- 선행: -
- 충돌: B2 교집합: DashOptimizer.cpp → 공유 17건(deps.md 5절) · LGE_SpringRule.h → PRE-11 PRE-16 · PR #654(DashOptimizer.cpp)
- 흡수: OPT-D23 · OPT-c35
- 비고: `DASH_BUILD_LGE_COMPSPRING` 빌드에서만 컴파일 — CI 에 그 빌드가 없으면 수동 확인 (DEV 접점).

#### OPT-20 · Optimizer 단위 테스트 타깃을 만든다 — PM 변환 함수와 설정 JSON 왕복
- 종류: PR | 규모: M | 태그: F · refactor
- 목표: `tests/TestOptimizerPresentationModel.cpp`(methodCatalog · defaultOption · buildMethodOptions · classifyValidationHeaders · parseDvSource/resolveGeometrySource · findGeometryParameterJsonPath · sanitizedModelInfoJson · constraintsFromRows) 와 `tests/TestOptimizerSettings.cpp`(saveSettings/load* 왕복 · NaN "None" · 레거시 objective 배열 · symbol 유지) 를 추가한다.
- 완료 기준: (1) ctest 타깃 2개 통과 (2) OPT-08 · OPT-14 · OPT-16 의 완료 기준이 테스트로 고정
- 변경 범위: tests/CMakeLists.txt, tests/TestOptimizerPresentationModel.cpp(신규), tests/TestOptimizerSettings.cpp(신규)
- 선행: PR #655 (`tests/CMakeLists.txt` +18/-18 — #654 스택 위, 그 랜딩 뒤 등록)
- 충돌: OPT-08 · OPT-10 · OPT-14 · OPT-16 (테스트가 고정하는 동작 — 먼저 쓰고 각 PR 이 갱신) · DEV-19 (tests/CMakeLists.txt 등록 헬퍼 — 먼저 오면 그 형식으로 등록) · B2 교집합: tests/CMakeLists.txt → 공유 12건(deps.md 5절) · PR #652(tests/CMakeLists.txt) · PR #651(tests/CMakeLists.txt)
- 흡수: OPT-U3 · #489(OPT 몫) · OPT-c32 · OPT-c54, c55 (← UIC-c57, DEV-c24)
- 비고: `DashOptimizer` 가 `DashProjectManager::Instance()` 를 역참조하므로 JSON 왕복 테스트는 파일 경로를 주입할 수 있어야 한다 — `setProjectDirectory` 우회 접점 (M 사유).

#### OPT-21 · Optimizer 화면에 FE Validation 버튼을 두고 Direct Launch 를 prefill 로 연다
- 종류: PR | 규모: S | 태그: B · feature
- 목표: Validation 탭에 버튼을 추가한다. 그 Set 의 입력 파일(OPT-02 결정 산출물) · Target Part(`resolveGeometrySource` 의 componentName) · 출력 폴더 `Optimizer_{Set}/FEValidation/` 으로 다이얼로그 `prefill` 을 부른다.
- 완료 기준: (1) 버튼 → 다이얼로그가 세 값으로 채워져 열림 (2) 입력 파일 부재 시 버튼 비활성 + 툴팁 (3) Done 뒤 Result Preview 자동 선택은 #604 동작 그대로
- 변경 범위: W, Wh
- 선행: OPT-02 · PR #652(#604) · RUN-30 (다이얼로그 `prefill` 진입점 — 먼저 머지되는 쪽이 만든다)
- 충돌: OPT-01 · OPT-26 (W) · PR #652 · RUN-30 (prefill 진입점 공용) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizerWidget.h → OPT-05 OPT-06 OPT-13 OPT-18 OPT-22 PRJ-25 UIC-22
- 흡수: 접점 #653 · OPT-c36 · OPT-c40 (← RUN-c19)
- 비고: 담당 RUN — OPT 측 버튼만 이 항목.

#### OPT-22 · 프리뷰 실행 중 Preview 버튼을 잠그고 모핑 완료·NX 완료/실패 통지로 푼다 — 위젯이 자기 요청의 완료를 받는다
- 종류: PR | 규모: S | 태그: B, D · bug
- 목표: `onPreviewButtonClicked` 진입에서 `previewBtn` 을 잠그고(상태 텍스트), Morphing 분기는 `co_await performMorphing` 종료에서, CAD 분기는 CAD-01 이 태그를 실어 항상 방출하는 `updatePrtGeometryCompleted/Failed(requester, stpPath)` 를 위젯이 직접 구독해 자기 `stpPath` 와 짝지어 푼다. `DashMainWindow` 부모 탐색으로 상태 애니메이션만 켜던 블록은 위젯 시그널(`nxPreviewRequested`) 로 바꾸고 MainWindow 가 구독한다 (PRJ-25 와 같은 방식). OCCT 표시는 MainWindow 의 `onNxPreviewStepReady` 그대로.
- 완료 기준: (1) 프리뷰 중 Preview 재클릭 불가, 완료·실패·조기 `co_return` 전부에서 버튼 복원 (2) `view/DashOptimizerWidget.cpp` 에 `qobject_cast<DashMainWindow*>` 0건 (3) NX 실패(`updatePrtGeometryFailed`) 시 Optimizer 상태 텍스트가 실패로 바뀐다 — NX 환경 수동 1회
- 변경 범위: W (`onPreviewButtonClicked` :1498-1870 · `setupConnections`), Wh, view/DashMainWindow.cpp (구독 1곳)
- 선행: CAD-01 (대칭 4종 · 태그 — CAD 분기) · PRJ-25 (부모 탐색 제거를 그쪽이 먼저 하면 (2) 는 그 항목 몫) · PR #655 (`view/DashMainWindow.cpp` +1/-10 — #654 → #655 랜딩 뒤)
- 충돌: OPT-01 · OPT-26 (같은 함수) · PRJ-25 (W 같은 블록) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizerWidget.h → OPT-05 OPT-06 OPT-13 OPT-18 OPT-21 UIC-22 · PR #652(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: #281-D(버튼 몫) · OPT-D19(위젯 수신 몫) · #457(D19 후속) · #463(OPT 몫 — Preview) · OPT-c38(버튼 몫), c39, c51 (← MOR-c06, CAD-c37, EXE-c23)
- 비고: OPT-D19 본체(태그 왕복·`m_batchMode`)는 CAD-01 — 이 항목은 랜딩 뒤 OPT 측 소비자 전환. 가드 형식은 EXE-09 헬퍼가 있으면 그것을 쓴다. Morphing 분기만 먼저 떼어 CAD-01 전에 넣어도 된다.

#### OPT-23 · Optimizer가 실제 사용한 입력 버전으로 최신성을 판정한다
- 종류: PR | 규모: S | 태그: C, A · feature
- 목표: #650 규칙으로 실제 최적화에 사용한 Builder 모델 버전과 필요한 상류 입력 버전을 기록하고 DashOptimizer::upstreamStaleReasons가 비교한다. Builder·Geometry·Condition setId만 비교해서 재생성 최신성을 보장하지 않는다.
- 완료 기준: 실제 사용 버전의 저장·복원, Builder 재학습 후 최신성 사유, 버전 누락·비교 불가 규칙 적용. 현재 입력 선택 변경으로 기존 결과의 소비 버전·출처를 수정하지 않는다. 프로젝트 호출·집계와 VM 표시는 Set의 판정 결과를 사용한다.
- 변경 범위: M, Mh (`runOptimization` · `saveSettings` · `upstreamStaleReasons`)
- 선행: BLD-18 · PRJ-23
- 충돌: OPT-07 · OPT-15 · OPT-24 (saveSettings) · OPT-26 (`Optimizer_{Set}.json` 최상위 RMW — 서로 덮는다) · OPT-16 (로더) · B2 교집합: DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashOptimizer.h → OPT-05 OPT-18 · PR #654(DashOptimizer.cpp)
- 흡수: #650(OPT 몫) · OPT-c41 (← PRJ-c38)
- 비고: OPT-26은 #685 참조·출처 검증, 본 항목은 #650 버전·최신성이다. 최상위 JSON 저장은 OPT-24 공용 경로와 조율하되 최초 입력 핀과 비원자 핀 RMW를 신설하지 않는다. PRJ-22와 공유 코드 적용 순서만 조율한다.

#### OPT-24 · Optimizer 설정 JSON 쓰기를 공용 파일 헬퍼로 옮긴다
- 종류: PR | 규모: S | 태그: A · refactor
- 목표: saveSettings와 설정 JSON 읽기를 PER-02 공용 DashSaveSystem 헬퍼로 옮겨 원자 쓰기와 사유 반환을 사용한다. OPT-26의 현재 입력 참조·출처 저장도 같은 진입점을 사용하도록 적용 순서를 조율한다.
- 완료 기준: 설정 JSON 직접 읽기·직쓰기를 공용 경로로 모으고 읽기 전용 경로의 실패 시 기존 파일 보존·오류 로그를 검증한다. OPT-20 왕복에서 참조·실제 소비 버전 등 다른 최상위 키도 보존한다.
- 변경 범위: M (saveSettings · 설정 JSON 읽기 · OPT-26 참조 저장 접점)
- 선행: PER-02
- 충돌: OPT-07 · OPT-15 · OPT-23 (saveSettings) · OPT-26 (참조 저장의 같은 파일) · OPT-16 (로더) · B2 교집합: DashOptimizer.cpp → 공유 17건(deps.md 5절) · PR #654(DashOptimizer.cpp)
- 흡수: #479(OPT 몫) · #478(OPT 몫) · #480(OPT 몫 — PER-04 뒤 버전 키 자동) · OPT-c46 (← PER-c29)
- 비고: PER-c08 의 RMW 13지점 중 1건. 헬퍼가 RMW 를 돕는 진입점(`updateObject(path, fn)` 류) 을 두면 이 함수가 첫 소비자 후보. 공용 진입점 명칭은 PER-02 의 `DashSaveSystem` 승격 결정을 따른다 (decisions ③ — 신설 `utils/DashJsonFile` 은 폐기).

#### OPT-25 · 수렴 히스토리 PNG 를 DPR 반영해 표시한다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: `onOptimizationSucceeded` 가 PNG 를 논리 800×600 으로 `scaled` 해 QLabel 에 넣어 DPR≠1 에서 흐려진다. `devicePixelRatioF()` 배의 물리 크기로 스케일하고 `setDevicePixelRatio` 를 건다 (또는 원본을 두고 QLabel 논리 크기만 800×600).
- 완료 기준: (1) 150%·200% 모니터에서 PNG 선명 (2) 100% 에서 현행과 같은 표시 크기 (3) 다른 배율 모니터로 옮겨도 깨지지 않음 — UIC-02 실기 환경에서 함께
- 변경 범위: W (`onOptimizationSucceeded` :702-725)
- 선행: -
- 충돌: OPT-05 (성공 통지 블록 — 같은 함수) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절)
- 흡수: #447 R5 · OPT-c47 (← UIC-c34)
- 비고: R1~R5 중 OPT 몫. UIC-02 의 200% 포함 실기 검증에서 함께 확인하면 비용이 준다.

#### OPT-26 · Optimizer가 Builder를 setId로 참조하고 출처 검증 후 실행·조회·프리뷰에 사용한다 (#685)
- 종류: PR | 규모: S | 태그: A, C · bug
- 목표: #685의 소비 경계에서 Builder setId와 응답·모델·part 등 선택을 Optimizer_{Set}.json에 저장·복원한다. #368의 공통 판독으로 Builder 산출물 출처를 검증하고 deck은 산출물 기록에서 해석한다. 현재 Optimizer Set의 ID를 유지하면서 다른 Builder를 선택할 수 있으며 외부 실행에는 ID로 해석한 실제 경로를 전달한다.
- 완료 기준: ① Builder 개명 후 동일 setId 참조 복원, 동명 재생성의 다른 setId와 구분 ② 다른 유효 Builder 선택·실행 가능 ③ 선택 변경만으로 기존 결과 출처 불변, 재실행 결과 덮어쓰기 때 실제 출처 갱신 ④ 필수 출처 누락·해석 불가 model_info는 재생성 안내, live parameter·이름·경로 추론 fallback과 자동 이관 금지 ⑤ 실행·조회·프리뷰가 같은 검증된 선택과 deck을 사용 ⑥ MCU 등 deck 비해당 유형은 공통 계약의 적용 관계로 판정하고 필수 출처 검증을 일괄 면제하지 않음.
- 변경 범위: model/DashOptimizer.cpp · model/DashOptimizer.h · view/DashOptimizerWidget.cpp
- 선행: BLD-20 (#368 생산·공통 계약 완료)
- 충돌: OPT-01 · OPT-21 · OPT-22 (`onPreviewButtonClicked` 같은 함수) · OPT-23 · OPT-24 (`Optimizer_{Set}.json` 최상위 RMW) · OPT-16 (M 로더) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashOptimizer.h → OPT-05 OPT-07 OPT-15 OPT-18 · PR #654(DashOptimizer.cpp)
- 흡수: #685 (구 #368 T23 OPT 소비 몫) · OPT-D15 · OPT-D16 · #457(configs 전량 모핑·펌핑 2곳) · #281-D(펌핑 몫) · OPT-c09, c25, c26(해소됨), c57 · OPT-c38(펌핑 몫), c56 (← MOR-c06, UIC-c58)
- 비고: PR #530은 당시 재업로드 결정 기록이며 옛 조합 ID 핀 코드를 그대로 이식하지 않는다. 생산 계약은 PER-07·BLD-20에서 재사용한다. #650 버전·최신성과 #473 결과 조작은 별도 목표이고 #681 머지 조건으로 두지 않는다. OPT-03·OPT-04 흡수·결번은 유지한다. 프리뷰 deck 1건으로 configs 전수 모핑과 processEvents 2곳을 제거하고 UI 응답성을 확인한다. 참조 쓰기는 공용 헬퍼 도입 순서와 조율한다.

### PRJ — Project · Set · Assets · Module Tree · 셸

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> 기준: dev @ b08a91b3. 원자 항목은 02-claims/PRJ.md. 열린 PR 7건 중 머지 대상 6건 — #651 #652 #654 #655 #656 #658 (#530 은 재업로드 노선이라 제외, decisions ②⑩). PRJ 겹침 — #654(controller/DashManager.cpp · view/DashMainWindow.cpp) · #652(controller/DashManager.* · view/DashMainWindow.* · model/DashProject.cpp · view/DashDoeSamplerDirectWidget.*) · #651(model/DashProject.* · view/DashMainWindow.cpp · view/DashModelingTreeWidget.cpp) · #655(view/DashMainWindow.cpp — 1파일·20항목) · #656·#658(model/DashAnalysisLauncher.cpp·.h — PRJ-03·09·22). 충돌란은 D-1 의 `build_deps.py --apply` 가 자동 기입한다.
> **선행이어야 할 PRJ 항목은 6건 어디에도 없다** — #655 의 MainWindow hunk 3개는 모두 모핑 핸들 배선이다. #656 의 hunk 는 `loadResultKeys`·`previewNaturalFrequency`·`requestVtkGeometry`, #658 은 `requestVtkPreview`·`previewNaturalFrequency` 인데, PRJ-03·09 가 치환할 `DashProjectManager::Instance()` 5곳은 `ioController`(:91)·`processResults`(:862·:972)·`loadParameterInfo`(:1478)·`refreshLaunchTarget`(:1514) 로 전부 다른 함수다(행 드리프트만 생긴다). #656 의 `.h` hunk 는 진입점 설명 주석뿐이라 PRJ-22 가 옮길 `upstreamStaleReasons()` 선언을 건드리지 않는다.
> Phase B: #444 담당 PRJ → LCH. 이관 흡수 — CON-c19 → PRJ-21 · PER-c20 → PRJ-16/17/18 · CAD-c20 → PRJ-26 · 신규 PRJ-31(PER-c30 직쓰기) · PRJ-32(BLD-c01 variant 3벌). B2: DOE-01 → PRJ-33(이관) · DOE-04 → PRJ-24(병합) · UIC-04 → PRJ-14(병합). `DashMainWindow` 레이아웃·프레임 함수군은 UIC 소유 — PRJ-03·04·11·14 충돌에 UIC 항목 명시.
> C' 반영 (2026-10-06, 04-review/PRJ.md + 05-final/decisions.md): 신규 **PRJ-34**(DEC — Set 모델 공통 베이스, ⑧) · **PRJ-35**(Save As 가 Set·트리를 전멸시킨다, 검토 2) · **PRJ-36**(#394 자기 덮어쓰기 소실, ⑨). **PRJ-20 은 CLOSE** — #645-1 집행은 CON-03 (⑦). 제거 — 충돌란의 `#530`·`pipeline-deck-stamp` (②, #530 은 머지하지 않는다). PRJ-31 의 "DashJsonFile" → "DashSaveSystem 헬퍼" (③). `.wbpj`·`.stli` 원장 편입은 LCH-29(DEC) 결과 대기 — PRJ 는 소비자(①): 사장 확정이면 PRJ 신규 항목 0, 현행 유지면 원장 편입 항목 1건이 새로 필요하다.
> 보류: CON 몫 — CON-03 의 목표를 "`addReferenceFile` 재로드 성공 뒤 핀 deck 일치 시 `refreshFromFile`" 로 교정하고 "진입점 노출" 문구 삭제(이미 public), CON-03·04·06·07 충돌란의 `PRJ-20` 제거(CLOSE 됨), CON-05 에 `선행: PRJ-08`(역순 허용) 기재. 보류: LCH 몫 — LCH-29 의 선행·영향 목록에 PRJ 추가와 결정문의 "사장 → `.wbpj`·`.stli` 원장 비편입(PRJ 무작업) / 현행 유지 → PRJ 원장 편입 항목 신설" 조항.
> C' 2차 반영 (2026-10-06, 05-final/deferred.md `→ PRJ` 8행): BLD 몫 `checks[]` 쌍 1건을 PRJ-22 비고에 흡수로 기재. RUN 몫(`m_categoryWidgetMap` → PRJ-c69 · PRJ-19) · PER 몫(PRJ-31 의 "DashJsonFile" → `DashSaveSystem` 헬퍼) · LCH 몫(LCH-29 소비자 등록 — PRJ-21 비고 · 대응표)은 1차 C' 에서 이미 반영. 항목 수 변화 0.

##### Set 수명 · 프로젝트 전환

#### PRJ-01 · 프로젝트 전환 전에 모듈 위젯 전부를 setModel(nullptr) 로 해제한다
- 종류: PR | 규모: S | 태그: A, E · bug
- 목표: `onFileOpen`·`onFileNew` 가 `OpenProjectFromFolder`/`CreateNewProject` 를 부르기 전에 모든 모듈 위젯의 모델을 끊는다 — `unbindSetWidgets` 의 카테고리 분기를 Set 무관 전체 해제 함수로 묶어 호출. `clearAllSets` 가 모델을 지운 뒤 위젯이 옛 포인터로 disconnect 하는 UAF 7곳이 사라진다
- 완료 기준: (1) 프로젝트 A → B 전환 후 모든 카테고리 Set 클릭에 크래시·ASan 보고 0 (2) `DashProjectManager::SetProjectDirectory` 호출 전 모든 위젯 `m_model == nullptr` — 소멸 지점이 `SetProjectDirectory → SetProjectPath(new) → clearAllSets` 하나이고 Save As 도 같은 함수를 타므로, 해제 함수가 그 앞을 지킨다 (3) #549 가 QPointer 로 막은 Model Runner 2곳도 같은 경로를 탄다
- 변경 범위: view/DashMainWindow.cpp, view/DashMainWindow.h
- 선행: -
- 충돌: PRJ-03 · PRJ-04 · PRJ-25 · PRJ-35 (같은 파일 · 같은 해제 함수를 Save As 경로에서 재사용) · PR #654 #652 #651 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashMainWindow.h → 공유 11건(deps.md 5절) · PR #655(DashMainWindow.cpp)
- 흡수: #551 · PRJ-c12 · PRJ-c13 · PRJ-c14 · PRJ-c15 · PRJ-c16 · PRJ-c17 · PRJ-c18
- 비고: 위젯별 `QPointer` 방어(#551 to-be)는 각 모듈 선택 — 계약(PRJ-02)이 서면 불필요. c19(delegate) 는 CON, c20 은 해소됨. c12 가 적었던 `CloseProject → SetProjectPath("")` 사슬은 성립하지 않는다(빈 경로 조기 반환) — 교정 근거는 c12

#### PRJ-02 · 위젯 모델 교체·Set 전환·프로젝트 전환 정리 규칙을 문서로 정하고 리뷰 항목에 넣는다
- 종류: DEC | 규모: S | 태그: E, A · docs
- 목표: "어디서 끊고(wholesale disconnect + 모델이 sender 가 아닌 연결), 무엇을 비우고(표·콤보·pending 상태), 언제 초기화하는지(Set 삭제·전환·프로젝트 전환)" 를 docs/ 한 장으로 고정하고 PR 체크리스트 항목으로 둔다
- 완료 기준: 결정 기록 — docs/widget-lifecycle.md(가칭) + 리뷰 체크 문구. 사례로 c12-c18 · OPT-D2 · RUN-D36 · PRE-D1 을 인용
- 변경 범위: docs/ (신규 1), .github 템플릿이 있으면 그것
- 선행: -
- 충돌: -
- 흡수: #431 · PRJ-c21
- 비고: #407 전수조사 결과를 실측 근거로 편입. 코드 수정은 각 모듈 항목

#### PRJ-16 · Set 삭제가 산출물 폴더를 함께 지우고 삭제 전에 확인한다
- 종류: PR | 규모: S | 태그: A, C · bug
- 목표: `deleteSet` 이 json 과 함께 `{Module}_{Set}` 폴더를 지운다. MainWindow 삭제 경로가 폴더 경로·내용 유무를 보여 주는 확인 다이얼로그를 거친다 (참조 자산 삭제와 같은 문형). 실행 중이면 거부 — 판정은 공용 질의(가칭 `isBusy()`)로 두고 Builder·Runner·Optimizer 는 `m_currentJob` 으로 구현, `DashModelBuilderMCU` 는 그 상태가 없어 새로 둔다
- 완료 기준: (1) 삭제 후 `getModuleDir` 경로 부재 (2) 삭제 취소 시 json·폴더 불변 (3) 동명 재생성 후 옛 산출물이 보이지 않음 (4) rename 가능 4종 전부(**MCU Builder 포함**)가 실행 중 삭제를 거부
- 변경 범위: model/DashProject.cpp, view/DashMainWindow.cpp
- 선행: -
- 충돌: PRJ-17 · PRJ-18 · PRJ-19 · PRJ-31 · PRJ-32 (DashProject.cpp) · PR #652 #651 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp)
- 흡수: #443 SI-6a ③a · PRJ-c05 · Set-Identity SI-6a(PER 이관 — 삭제 동반) · PER-c20 · PRJ-c61
- 비고: SI-6a 가 "둘 다" 로 확정한 두 규칙 중 하나. 다른 하나는 PRJ-17. `DashModelBuilderMCU` 에는 `m_currentJob`·`isRunning` 이 없고 ProcessJob 이 `runTraining` 지역 변수라(c03) 공용 질의를 그 클래스에 신설하는 몫이 PRJ-16·18 에 함께 든다 — 접점 BLD

#### PRJ-17 · Set 생성 시 동명 산출물 폴더가 있으면 거부하고 안내한다
- 종류: PR | 규모: S | 태그: A, C · bug
- 목표: `createNewSet` 이 `hasSetNamed` 에 더해 `getModuleDir(type, name)` 존재를 검사해 거부하고, `onNewSetRequested` 가 "외부 복사·구 프로젝트 고아 폴더" 안내를 띄운다
- 완료 기준: (1) 고아 폴더가 있는 이름으로 Add Set → 생성 0 + 안내 (2) 폴더 제거 후 같은 이름 생성 성공
- 변경 범위: model/DashProject.cpp, view/DashMainWindow.cpp
- 선행: -
- 충돌: PRJ-16 · PRJ-18 · PRJ-19 · PRJ-31 · PRJ-32 · PR #652 #651 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp)
- 흡수: #443 SI-6a ③b · PRJ-c06 · PER-c20 · PRJ-c61 (동명 폴더 거부)

> #562·PR #681의 현행 수정 범위 재확인은 추가 개정 계획이다. 아래 코드 실측은 작성 당시 기록이며 #368·#685를 #681 머지 조건으로 적용하지 않는다.

#### PRJ-18 · Set rename 이 산출물 폴더를 함께 개명하고 실패 시 롤백한다
- 종류: PR | 규모: M | 태그: A, C · bug
- 목표: `renameSet` 이 json rename 과 `QDir::rename` 을 한 단위로 — 폴더 개명 실패 시 json 을 되돌리고 false. 모델이 실행 중이면 거부 — 판정은 PRJ-16 과 같은 공용 질의(`isBusy()`)이고 `DashModelBuilderMCU` 는 그 상태를 새로 둔다. 대상은 rename 가능한 ModelBuilder·MCU·ModelRunner·Optimizer
- 완료 기준: (1) rename 후 옛 폴더 0·새 폴더에 기존 run 결과 (2) 폴더 잠금 상태에서 rename → json 이름 불변 + 경고 (3) 실행 중 rename → 트리 텍스트 원복, rename 가능 4종 전부(**MCU Builder 포함**)
- 변경 범위: model/DashProject.cpp, model/DashProject.h, view/DashMainWindow.cpp
- 선행: PRJ-19 (죽은 분기 제거 후 손대는 편이 작다 — 선택)
- 충돌: PRJ-16 · PRJ-17 · PRJ-19 · PRJ-31 · PRJ-32 · PR #652 #651 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · DashProject.h → PRJ-08 PRJ-11 PRJ-22 PRJ-33 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp)
- 흡수: #562-1 · #443 SI-6a ① · PRJ-c03 · Set-Identity SI-6a(PER 이관 — rename 동반 개명) · PER-c20 · PRJ-c61
- 비고: #562-2·-4 는 Geometry 이름 고정(#599)으로 소멸(c08·c10), #562-3 은 DOE 소관(c09). Rename 시그널 미발행은 폴더를 참조하는 Runner·Optimizer(c04, RUN·OPT) 가 setId 를 들게 되면 불필요

##### Add File · Project Assets

#### PRJ-20 · (CLOSE) Add File 덮어쓰기 뒤 Condition 재읽기를 CON-03 에 넘긴다
- 종류: CLOSE | 규모: - | 태그: A · bug
- 목표: #645-1 을 CON-03 과 중복 항목화한 것을 정리한다 — PRJ 몫 실작업 0
- 완료 기준: 닫기 사유 — 같은 변경(MainWindow 훅 + 위젯 `refreshFromFile`)을 두 모듈이 각각 항목화했고, decisions ⑦ 이 **CON-03 에 남긴다**로 확정했다. PRJ-20 의 `DashConditionParameterizationWidget.h (refresh 진입점 공개)` 는 불필요(`refreshFromFile`·`pinnedDeckFileName` 이 이미 public, `view/DashMainWindow.cpp:777` 이 이미 호출) → 실질 1파일이라 변경 파일 수로도 CON-03 이 본체다. 단 **호출 자리는 PRJ-20 의 서술이 맞다** — `discardLoadedReferenceFile(:2713)` 은 `QFile::remove(:2715)`·`QFile::copy(:2718)` 보다 앞에 돌아 덮어쓰기 전 내용(또는 삭제된 파일)을 읽으므로, 훅은 호출자의 `co_await addReferenceFile(:2694)` → `registry.load(:2766)` 성공 **뒤**여야 한다
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #645-1 · PRJ-c32 (집행은 CON-03)
- 비고: 보류: CON 몫 — CON-03 목표의 훅 위치 교정과 "진입점 노출" 문구 삭제, CON-03·04·06·07 충돌란의 `PRJ-20` 제거. 레지스트리는 invalidate 후 load 를 첫 로드로 보아 `documentChanged` 를 내지 않고(REN), CON 모델은 #565 로 방송 구독을 걷었다 — 통지 책임은 덮어쓰기를 집행한 MainWindow 이고 그 호출 1줄이 CON-03 의 MainWindow 변경분이다. ID 는 CON 항목 4건이 충돌란에서 참조하므로 결번으로 비우지 않고 CLOSE 로 남긴다

#### PRJ-21 · Add File 복사를 원자화해 실패 시 기존 파일·등록을 보존한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `copyFileIntoProject` 가 임시 이름으로 복사한 뒤 성공했을 때만 `discardLoadedReferenceFile` + 교체(rename). 실패하면 기존 파일·컨텍스트·트리 행·원장·Set 이 그대로이고 사유를 알린다
- 완료 기준: (1) 읽기 불가 원본으로 덮어쓰기 → 기존 파일 내용·트리 행·Condition 화면 불변 + 오류 통지 (2) 성공 경로의 동작 불변
- 변경 범위: view/DashMainWindow.cpp
- 선행: -
- 충돌: CON-03 (같은 함수 — 복사 성공 뒤 재로드 훅이 이 원자화 뒤에 얹힌다) · PR #651 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #652(DashMainWindow.cpp)
- 흡수: #645-2 · PRJ-c33 · CON-c19 · PRJ-c59
- 비고: 같은 자리의 `releaseGeometryWidgetFor(:2738)` 는 복사 성공 후에도 Geometry 위젯을 start page 로 남기는데, Geometry 재진입 규칙은 #645 범위 밖이다. `.wbpj`·`.stli` 원장 편입(CAD-Path-Disposition 후속작업 5)이 이 함수에서 일어나므로 **LCH-29(DEC) 의 소비자** — 현행 유지로 결정되면 원장 편입 항목 1건이 새로 필요하다

#### PRJ-24 · 릴리스 빌드에서 Resample Set 클릭이 무음으로 끝나지 않게 한다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: `handleDoeSamplerSelectionForVariant` 가 위젯이 없는 variant 를 만나면 "이 빌드에서 지원하지 않는 Set" 통지 + 로그를 내고 dock 을 비운다 (또는 restore 시 그 Set 을 비활성 표시)
- 완료 기준: (1) 릴리스 빌드에서 DEV 프로젝트의 Resample Set 클릭 → 통지 1회 + 직전 모듈 화면 잔류 없음 (2) DEV 빌드 동작 불변
- 변경 범위: view/DashMainWindow.cpp (handleDoeSamplerSelectionForVariant)
- 선행: -
- 충돌: PRJ-01 · PR #652 · PR #651 · PR #654 (DashMainWindow.cpp) · DOE-05 (같은 함수) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · PR #655(DashMainWindow.cpp)
- 흡수: DOE-D25 · PRJ-c52 · DOE-c19 · LCH-c62(DOE-c58) (DOE-04 병합, B2)
- 비고: DOE-04 와 병합(B2, 같은 파일·같은 널 가드 자리). DOE 안은 "통지 후 dock 은 직전 화면 유지" — 통지 1회가 핵심이고 dock 처리는 구현 시 택일. #615 가 Resample 의 DEV 전용 유지를 명시 (숨김은 Set 삭제 경로까지 걸려 택하지 않음)

##### 전역 접근 해체

#### PRJ-03 · DashManager::PrjMgr() 별칭을 제거한다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: `PrjMgr()` 68줄(호출 65 · 선언 1 · 정의 2 — dev 실측 `git grep -c 'PrjMgr()'`: MainWindow 58 · ContextRegistry 5 · tests 2 · DashManager.cpp 2 · .h 1)을 `DashProjectManager::Instance()` 로 기계 치환하고 선언·정의를 지운다. 동작 변화 0
- 완료 기준: (1) `PrjMgr` 심볼 0 (2) 빌드·tests 통과
- 변경 범위: view/DashMainWindow.cpp, controller/DashAnalysisModelContextRegistry.cpp, controller/DashManager.cpp, controller/DashManager.h, tests/TestMorphingPreviewDriver.cpp
- 선행: -
- 충돌: PRJ-01 · PRJ-04 · PRJ-06 · PR #654 #652 #651 (MainWindow·DashManager 광역 치환이라 머지 직후에) · UIC-01 · UIC-03 · UIC-05 · UIC-09 (DashMainWindow 레이아웃·프레임 함수군은 UIC 소유 — 광역 치환은 UIC 항목 랜딩 사이에) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashManager.cpp → CAD-03 CAD-06 DOE-19 EXE-06 PRJ-14 REN-07 · DashAnalysisModelContextRegistry.cpp → EXE-22 REN-01 REN-02 REN-07 UIC-19 · DashManager.h → CAD-06 PRJ-19 · PR #655(DashMainWindow.cpp)
- 흡수: #434-1 · PRJ-c26
- 비고: 246-1 5절 1단계. #432(PRJ-08/09) 와 호출부가 겹치지 않도록 먼저 **D-1 정정(2026-10-06)** — `model/DashAnalysisLauncher.cpp` 는 이미 `DashProjectManager::Instance()` 5곳이고 `PrjMgr()` 0건이라 변경 범위에서 뺐다. 71 → 68 은 dev 실측.

#### PRJ-04 · DashManager 의 렌더 인프라를 DashRenderingManager 로 옮기고 PRJ 호출부를 주입으로 바꾼다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: `m_renWin`·`m_renderer`·`m_camWidget`·`m_interactorStyleRubberBand`·`m_originalActor` 와 `Redraw`·`GetRenderWindow`·`AddCamWidget`·`Set/GetCurrentActor`·`updateOriginalActor` 를 DashRenderingManager 소유로. 같은 기제의 **인터랙션 주입**(246-1 2단계 2번)도 함께 — `m_handlePicking`·`m_handleVisualizer` 와 접근자 `GetHandlePickingInteraction`·`GetHandleVisualizer` 를 걷고, 유일한 호출부인 `view/DashMainWindow.cpp:542-543`(`morphingInteraction_`·`morphingVisualizer_` 초기화)을 생성자/세터 주입으로 바꾼다. DashManager 접근자는 전달만 남겨 다른 모듈 호출부가 그대로 컴파일된다. MainWindow 39(렌더 37 + 핸들 2) · ModelingTree 2 곳은 MainWindow 가 든 `DashRenderingManager&` 로 치환
- 완료 기준: (1) `Mgr()->Redraw|GetRenderer|GetRenderWindow|GetRenderingManager|*CurrentActor|AddCamWidget|updateOriginalActor|GetHandlePickingInteraction|GetHandleVisualizer` 가 view/DashMainWindow.cpp·DashModelingTreeWidget.cpp 에서 0 (2) DashManager.h 의 vtk include 가 handle 관련만 (3) 렌더 회귀 0 (Load·모핑 프리뷰·Set 전환) + 핸들 피킹·가시화 회귀 0
- 변경 범위: controller/DashManager.cpp, controller/DashManager.h, controller/DashRenderingManager.cpp, controller/DashRenderingManager.h, view/DashMainWindow.cpp, view/DashMainWindow.h (주입된 `morphingInteraction_`·`morphingVisualizer_` 의 출처 변경), view/DashModelingTreeWidget.cpp
- 선행: PRJ-03
- 충돌: PRJ-01 · PRJ-06 · PRJ-19 · PR #654 (DashManager.cpp·MainWindow.cpp) · #652 · #651 · UIC-03 · UIC-05 · UIC-07 (`Redraw` 호출부가 resize·오버레이 배치 함수군에 걸치면 — UIC 소유) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashMainWindow.h → 공유 11건(deps.md 5절) · DashRenderingManager.cpp → 공유 10건(deps.md 5절) · DashManager.cpp → CAD-03 CAD-06 DOE-19 EXE-06 PRJ-14 REN-07 · DashRenderingManager.h → OPT-01 REN-07 REN-08 REN-09 REN-10 REN-12 · DashManager.h → CAD-06 · DashModelingTreeWidget.cpp → DEV-10 REN-12 · PR #655(DashMainWindow.cpp)
- 흡수: #434-2 · PRJ-c27 (PRJ 분 41곳 — MainWindow 39 + ModelingTree 2) · PRJ-c30 (m_originalActor) · 246-1 5절 2단계 2번(인터랙션 주입)
- 비고: 접점 REN(DashRenderingManager 소유) · MOR(`DashHandlePickingInteraction`·`DashHandleVisualizer` 가 MOR 소관 타입이나 소유·주입 자리가 PRJ 파일이고 호출부가 `DashMainWindow.cpp` 2곳뿐이라 PRJ 가 맡는다 — 04-review 5). MOR 호출부 54곳(c27) · BLD 1 · RUN 2 · OPT 3 · REN 6 은 각 모듈이 전달 접근자를 주입으로 바꾼다 — Phase B 재배정. 246-1 "2단계 verify: Mgr() 180건 미만" 은 이미 182 → 본 항목 후 약 140. PR #655 의 MainWindow hunk 는 `:542-543` 을 건드리지 않는다

#### PRJ-05 · 데몬·외부 프로세스·솔버 설정의 소유자를 정한다
- 종류: DEC | 규모: S | 태그: E, B
- 목표: DashManager 생성자가 만드는 journal·MCU·sensitivity 데몬, DashSolverNxCad, DashTopOptPostprocessRunner, `m_solverPaths`(QSettings), `m_cpuCoreCount` 의 목적지 — ① DashDaemonLifecycle 확장 ② 신설 프로세스 허브 ③ 소비 모듈 소유 — 중 하나로 결정
- 완료 기준: 결정 기록 (소유자 · 생성 시점 · 종료 순서 · `atexit(Destroy)` 대체)
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #434-3 · PRJ-c28
- 비고: DashDaemonLifecycle 은 sensitivity·MCU 만 다루고 Journal·NxCad 는 배치·세션 수명이 따로라고 못박았다(.h:21-23) — ① 은 그 전제를 바꾼다. 테스트 가능성의 분기점은 "DashManager 생성자에서 프로세스가 뜨지 않는 것"

#### PRJ-06 · 프로세스·설정 생성을 DashManager 생성자 밖으로 옮긴다
- 종류: PR | 규모: M | 태그: E, B · refactor
- 목표: PRJ-05 결정대로 생성·소멸을 소유자로 이동. DashManager 접근자(`mcuDaemon()` 등 38곳 소비)는 전달만 남긴다. `atexit(Destroy)` 를 MainWindow 소멸 순서로 대체
- 완료 기준: (1) `DashManager::DashManager()` 에 `new DashExtensionProcess`·`new DashSolverNxCad`·`QSettings` 0 (2) 앱 종료 시 데몬 고아 0 (3) tests 의 `Mgr()` 최초 호출이 프로세스를 띄우지 않음
- 변경 범위: controller/DashManager.cpp, controller/DashManager.h, 소유자 파일(PRJ-05 결정), main.cpp 또는 view/DashMainWindow.cpp
- 선행: PRJ-05 · PRJ-03
- 충돌: PRJ-04 · PR #654 #652 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashManager.cpp → CAD-03 CAD-06 DOE-19 EXE-06 PRJ-14 REN-07 · main.cpp → DEV-21 DEV-24 EXE-02 EXE-06 PRJ-14 UIC-05 UIC-26 · DashManager.h → CAD-06 PRJ-19 · PR #655(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: #434-3 · PRJ-c28 · PRJ-c30 (atexit)
- 비고: 소비자 38곳/15파일의 접근자 치환은 각 모듈 — Phase B 재배정

#### PRJ-07 · 공유 DV 모델과 NX CAD 파라미터 캐시의 소유자를 정한다
- 종류: DEC | 규모: S | 태그: E, C
- 목표: `m_designVariableModel`(CON·CAD 위젯 + DoeSampler·JobRunner 소비) 과 `m_lastNxCadParameterJson`(CAD 위젯 소비 1, `applyLast…` 가 PrjMgr 역참조) 의 목적지 — 프로젝트 수명 객체(DashProject) 또는 소비 모듈 — 결정
- 완료 기준: 결정 기록
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #434 · PRJ-c30 (DV 모델 · NX 캐시)
- 비고: 결정 후 이동 PR 은 CON·CAD 접점 — 결정이 "소비 모듈" 이면 CAD 항목

#### PRJ-34 · Set 모델에 공통 베이스를 둘지, 둔다면 어느 층에 둘지 정한다
- 종류: DEC | 규모: S | 태그: E, C
- 목표: Set 모델 10종에 공통 진입점(경로 주입 API · `upstreamStaleReasons()` 같은 가상 함수 · Run-완료 공통 시그널)을 둘 자리를 정한다. `DashMvvmModelBase` 는 production 상속자가 0이고(tests 7개 클래스뿐) Set 모델은 `QObject`(AnalysisLauncher·DoeSampler·ModelBuilder·ModelRunner·ModelRunnerMCU·Optimizer·AIGeometryGeneration) · `QAbstractTableModel`(ConditionParameterization·GeometryParameterCAD) · `QStandardItemModel`(GeometryParameter) 로 갈려 있어, 지금은 베이스를 고쳐도 닿는 코드가 없다. 선택지 — ① 비-QObject 인터페이스(`DashSetModel`/`DashSetPaths` 류)를 다중상속 ② 10클래스 각자 세터·가상 함수 ③ `DashMvvmModelBase` 로 재부모화(QObject 계열만 가능 → 표 모델 2종은 예외 처리)
- 완료 기준: 결정 기록 — 선택지 1개 · 그 자리에 둘 멤버 목록(경로 주입 API · `upstreamStaleReasons()` · Run-완료 시그널) · 표 모델 2종(`QAbstractTableModel`)과 `QStandardItemModel` 1종의 처분 · `DashMvvmModelBase` 를 쓰지 않기로 하면 그 클래스의 존속 여부
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: PRJ-c68
- 비고: decisions ⑧ 이 신설을 지시한 항목. 이 결정 없이는 PRJ-08(주입 API 1개)·PRJ-09(그 API 로의 치환)·PRJ-22(가상 함수 1개 + 공통 시그널)의 규모·완료 기준이 성립하지 않는다. `DashModelRunnerMCU::setProjectDirectory(userPath, projectPath)` 가 2-인자 변종이라 공통 계약이 이것까지 덮어야 한다. CON-05 가 PRJ-08 을 기다리므로 이 결정이 늦으면 CON 모델 1종 선행(역순)을 허용한다 — PRJ-05·07 과 같은 결정 전용 항목

#### PRJ-08 · DashProject 가 Set 모델에 경로 접근을 주입하고 자신의 ProjectManager 역호출을 없앤다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: Set 모델 생성(`add*`·`restoreExistingModules`) 시 `DashIOController*`(또는 경로 묶음)를 넘기는 공용 진입점을 **PRJ-34 가 정한 자리**에 두고, DashProject 자신의 `Instance()` 20건을 멤버 주입으로 바꾼다. no-op `SaveProject` 역호출 6건은 삭제
- 완료 기준: (1) model/DashProject.cpp 에 `DashProjectManager::Instance` 0 (2) 주입 API 1개 + `setProjectDirectory` **9클래스**(단일 인자 8 + `DashModelRunnerMCU` 2-인자 1)의 처분(유지·개명·삭제)이 PR 본문에 기록 — 인자 사용 양상이 갈려 있다(`DashModelBuilder.cpp:65`·`DashOptimizer.cpp:133` 은 "NO FALLBACKS" 로 인자 무시, `DashModelRunner.cpp:735`·`DashAIGeometryGeneration.cpp:15` 은 `m_projectPath = path` 저장) (3) 빌드·tests 통과, 프로젝트 열기·Set 생성 동작 불변
- 변경 범위: model/DashProject.cpp, model/DashProject.h, controller/DashProjectManager.cpp, PRJ-34 가 정한 주입 자리의 파일(공통 베이스를 두면 `model/DashMvvmModelBase.*`, 비-QObject 인터페이스면 그 신규 헤더, 각자 세터면 Set 모델 9종의 `.h`)
- 선행: PRJ-34 (주입 자리 결정) · PRJ-03
- 충돌: PRJ-16 · PRJ-17 · PRJ-18 · PRJ-19 · CON-05 (`setProjectDirectory` 계약의 CON 적용분) · PR #652 #651 · B2 교집합: DashProject.cpp → 공유 14건(deps.md 5절) · DashProject.h → PRJ-11 PRJ-22 PRJ-31 PRJ-32 PRJ-33 · DashProjectManager.cpp → EXE-06 PRJ-12 PRJ-13 PRJ-35 PRJ-36 REN-10
- 흡수: #432 · PRJ-c22 (DashProject 분) · PRJ-c23
- 비고: 9개 모델 클래스의 `setProjectDirectory` 가 이미 경로 주입의 절반이다 — 그 자리에 IOController 주입을 얹는다. `GetIOController` 가 94/112 이라 IOController 주입 하나로 대부분 닫힌다. **별도 DEC 로 쪼개지 않는다** — `setProjectDirectory` 계약은 이 항목이 코드로 정하는 한 개념이고(decisions ⑦, 00-plan 1-2), CON-05 는 그 적용분이라 `선행: PRJ-08` 이다. 단 PRJ-34 가 늦어 CON-05 가 블록되면 CON 모델 1종만 먼저 고치고 PRJ-08 이 일반화할 때 맞추는 역순을 허용한다. 보류: CON 몫(CON-05 에 선행 기재)

#### PRJ-09 · 모듈 모델 12파일의 DashProjectManager 전역 접근을 주입된 IOController 로 치환한다
- 종류: PR | 규모: L | 태그: E · refactor
- 목표: PRJ-08 의 진입점으로 `Instance()` 92건(+`PrjMgr` 3)을 치환. `IsProjectOpen` 10건은 주입 포인터 null 검사로, `GetProject` 9건은 필요한 값(setIds·referenceModel) 전달로
- 완료 기준: (1) `git grep DashProjectManager::Instance -- model/` 0 (2) tests 통과 (3) 모듈별 Set 진입·Run 회귀 0
- 변경 범위: model/DashModelBuilder.cpp, model/DashModelRunner.cpp, model/DashDoeSampler.cpp, model/DashOptimizer.cpp, model/DashModelBuilderMCU.cpp, model/DashJobRunner.cpp, model/DashAnalysisLauncherKPI.cpp, model/DashAnalysisLauncher.cpp, model/DashGeometryParameter.cpp, model/DashConditionParameterization.cpp, model/DashGeometryParameterCAD.cpp, model/DashAnalysisLaunchExecutor.cpp, model/DashJobRunnerAnsysMotion.cpp
- 선행: PRJ-08
- 충돌: PR #652 (DashAnalysisLauncher·DashDoeSampler) · #651 (DashAnalysisLauncher·DashJobRunner*) · #654 (DashModelRunner·DashOptimizer) · #433 스택(PRE 의 DashAnalysisLauncher 분해) · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절) · DashAnalysisLaunchExecutor.cpp → LCH-06 LCH-07 LCH-14 LCH-16 LCH-28 LCH-34 UIC-20 · DashModelBuilderMCU.cpp → BLD-01 BLD-10 BLD-12 BLD-13 BLD-17 BLD-18 UIC-20 · DashJobRunner.cpp → LCH-02 LCH-03 LCH-07 LCH-13 LCH-14 UIC-20 · DashAnalysisLauncherKPI.cpp → PRE-11 PRE-12 PRE-21 PRE-22 UIC-20 · DashConditionParameterization.cpp → CON-01 CON-02 CON-05 CON-06 UIC-20 · DashGeometryParameterCAD.cpp → CAD-03 CAD-05 CAD-06 CAD-09 UIC-20 · DashGeometryParameter.cpp → MOR-11 UIC-20 · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp)
- 흡수: #432 · PRJ-c22 (모듈 모델 분)
- 비고: 선행 PRJ-08 은 PRJ-34 결정 뒤에 선다 — 공통 베이스 부재(c68) 때문에 본 항목의 "주입된 IOController" 자리가 결정에 종속된다. L 사유 — 기제 1개의 기계적 치환이고 파일별로 쪼개면 두 접근 경로가 공존하는 중간 상태가 길어진다. 모듈별 PR(BLD 2 · RUN 1 · DOE 1 · OPT 1 · LCH/PRE 4 · MOR/CAD 2 · CON 1) 로 분할해도 무방 — 그 경우 각 모듈 접점

##### 저장 · 프로젝트 파일

#### PRJ-10 · 즉시 저장 체계에서 Save · Save As · 종료 확인의 의미를 정한다
- 종류: DEC | 규모: S | 태그: A, D
- 목표: 모듈 json 은 편집 즉시 쓰고 `SaveProject` 는 no-op 인데 Save 메뉴는 성공을 보고한다. ① Save 메뉴·SaveProject 제거(즉시 저장 명시) ② dirty 추적 도입 + 명시 저장 — 중 하나. 종료 확인(#485)은 ② 일 때만 성립
- 완료 기준: 결정 기록 + c40 실측(모듈별 "편집 → 디스크" 지연 지점 목록)
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #485 · PRJ-c24 · PRJ-c40
- 비고: 접점 #394(저장 실패 무시)는 보드·원천에 없다

#### PRJ-11 · 종료 시 미저장 변경을 확인한다
- 종류: PR | 규모: S | 태그: A, D · feature
- 목표: PRJ-10 이 ② 이면 — DashProject 가 dirty 를 들고 `DashMainWindow::closeEvent` 가 저장/버리기/취소를 묻는다. ① 이면 본 항목은 닫는다
- 완료 기준: (1) 미저장 상태에서 닫기 → 다이얼로그, 취소 시 창 유지 (2) 저장 직후 닫기 → 다이얼로그 없음
- 변경 범위: view/DashMainWindow.cpp, view/DashMainWindow.h, model/DashProject.h
- 선행: PRJ-10
- 충돌: PRJ-01 · PRJ-15 · UIC-05 (`closeEvent` 신설 공유 — geometry 저장은 UIC 소유, 저장 확인 분기는 그 안에 얹는다) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashMainWindow.h → 공유 11건(deps.md 5절) · DashProject.h → PRJ-08 PRJ-18 PRJ-19 PRJ-22 PRJ-31 PRJ-32 PRJ-33 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #652(DashMainWindow.cpp·DashMainWindow.h) · PR #651(DashMainWindow.cpp·DashProject.h)
- 흡수: #485 · PRJ-c40

#### PRJ-12 · Save As 가 프로젝트 루트 전체를 복사하고 실패를 보고한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `SaveProjectAs` 의 복사 원천을 `.dproj` 에서 프로젝트 루트로 넓혀 참조 파일·`{Module}_{Set}` 산출물 폴더를 포함하고, `removeRecursively`·`QFile::copy` 의 반환을 모아 실패하면 false 로 반환한다 (지금은 전부 버리고 무조건 `return true` 라 호출부의 "Failed to save project." 분기가 도달 불가다)
- 완료 기준: (1) Save As 결과 폴더에서 열기 → Set·참조 파일·run 결과 전부 보임 (2) 쓰기 불가 대상 → 오류 통지 + 원본 불변 (3) `SaveProjectAs` 안에 반환값을 버리는 파일 연산 0 · 한 건이라도 실패하면 false
- 변경 범위: controller/DashProjectManager.cpp, view/DashMainWindow.cpp
- 선행: -
- 충돌: PRJ-13 (같은 파일) · PRJ-35 · PRJ-36 (같은 함수 `SaveProjectAs`) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProjectManager.cpp → EXE-06 PRJ-08 PRJ-19 REN-10 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #652(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: PRJ-c25 · #394 (실패 무시·성공 오보 몫 — 자기 덮어쓰기 소실은 PRJ-36)
- 비고: 자체 실측. 접점 PER(복사 범위 규약). "기존 대상 폴더 `removeRecursively` 는 사용자 확인 뒤에만" 은 **해법에서 뺐다** — #394 본문이 "삭제를 시작한 시점에 이미 안전한 fallback 이 없다"(TOCTOU · 부분 성공)로 확인 다이얼로그를 기각했고, 기본값대로 확인만 하면 원본이 지워지는 케이스는 PRJ-36 이 거부로 막는다. 순서는 PRJ-36 → PRJ-12

#### PRJ-35 · Save As 뒤에 Set 모델과 Module Tree 를 복원한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `SaveProjectAs` 가 복사 뒤 `SetProjectDirectory(newProjectPath)` 를 불러 `clearAllSets()` 로 Set 10종을 `qDeleteAll` 하고 트리 행을 지우는데, `restoreExistingModules()` 재호출도 위젯 unbind 도 없다 — 저장 직후 화면에 Set 이 하나도 없고 위젯은 해제된 모델을 들고 있다. Save As 경로가 프로젝트 전환과 같은 순서를 타게 한다: 전체 위젯 해제(PRJ-01 의 해제 함수) → 경로 전환 → `restoreExistingModules()`
- 완료 기준: (1) Save As 직후 Module Tree 에 전환 전과 같은 Set 목록이 보인다 (2) Save As 직후 모든 카테고리 Set 클릭에 크래시·ASan 보고 0 (3) `SetProjectDirectory` 호출부 3곳(Open·New·Save As) 중 복원이 빠진 곳 0
- 변경 범위: controller/DashProjectManager.cpp, view/DashMainWindow.cpp
- 선행: PRJ-01 (전체 해제 함수를 Save As 경로에서 재사용)
- 충돌: PRJ-12 · PRJ-36 (같은 함수 `SaveProjectAs`) · PRJ-13 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProjectManager.cpp → EXE-06 PRJ-08 PRJ-19 REN-10 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #652(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: PRJ-c65
- 비고: 04-review 2 의 누락 지적. 대안은 "Save As 가 경로만 갱신하고 Set 을 지우지 않는다" — `SetProjectPath` 가 `clearAllSets(); addNewSetItems();` 를 무조건 하므로 그쪽을 고치면 Open·New 경로에 영향이 가고 범위가 커진다. c12 의 잘못된 인과 사슬(`CloseProject → SetProjectPath("")`)이 이 경로를 가렸다

#### PRJ-36 · Save As 가 현재 프로젝트를 가리키면 거부하고 삭제 전에 복사를 끝낸다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `SaveProjectAs` 가 대상 폴더를 받으면 (a) 그 폴더가 현재 프로젝트 루트이거나 그 상·하위면 거부하고 사유를 알린다 (b) 어느 경우에도 복사를 끝낸 뒤에만 기존 대상을 치운다 — 지금은 `destBaseDir.removeRecursively()` 가 먼저 돌고, 원본(`sourceProjectDir = GetProjectPath()`)이 대상 폴더 안에 있으면 그것을 지운 다음 빈 `.dproj` 를 순회해 0개를 복사하고 성공을 보고한다. 두 다이얼로그 기본값이 정확히 현재 프로젝트를 가리켜 "확인만" 으로 재현된다
- 완료 기준: (1) Save As 를 두 다이얼로그 기본값대로 확인 → 거부 + 사유 통지, 원본 프로젝트 파일 전부 보존 (2) 대상이 현재 프로젝트의 상위·하위 경로여도 거부 (3) 정상 대상에서는 복사 완료 전에 기존 대상 삭제가 일어나지 않는다 (임시 위치 → 교체)
- 변경 범위: controller/DashProjectManager.cpp, view/DashMainWindow.cpp (`onFileSaveAs` 의 거부 통지)
- 선행: -
- 충돌: PRJ-12 · PRJ-35 (같은 함수 `SaveProjectAs`) · PRJ-13 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProjectManager.cpp → EXE-06 PRJ-08 PRJ-19 REN-10 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #652(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: #394 (자기 덮어쓰기 데이터 소실 몫) · PRJ-c66
- 비고: 보드 밖 OPEN 이슈 4건 편입 중 PRJ 몫(decisions ⑨). #394 본문이 "삭제를 시작한 시점에 이미 안전한 fallback 이 없다"(권한 사전 검사는 TOCTOU · `removeRecursively` 부분 성공 · Windows 핸들 점유)로 확인 다이얼로그 해법을 기각했으므로 PRJ-12 의 "사용자 확인 뒤 `removeRecursively`" 로는 막지 못한다 — 거부와 순서 역전이 본체다. 실패 반환 수집·성공 오보 제거는 PRJ-12. 이슈 본문의 "Overwrite 동작 제거가 정책상 수용 가능한지" 는 아직 미회신이라, 거부 범위를 "자기·상·하위" 로 좁혀 기존 덮어쓰기 기능 자체는 남긴다

#### PRJ-13 · 프로젝트를 QLockFile 로 잠가 동시 열기를 막는다
- 종류: PR | 규모: S | 태그: A · feature
- 목표: `OpenProjectFromFolder`·`CreateNewProject` 가 `.dproj/.lock` 을 `QLockFile` 로 잡고 실패 시 false + 잠근 PID 안내; `CloseProject` 가 해제. stale 잠금은 QLockFile 기본 처리
- 완료 기준: (1) 두 인스턴스에서 같은 프로젝트 열기 → 두 번째 거부 + 안내 (2) 비정상 종료 뒤 재열기 성공
- 변경 범위: controller/DashProjectManager.cpp, controller/DashProjectManager.h, view/DashMainWindow.cpp
- 선행: -
- 충돌: PRJ-12 · PRJ-08 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProjectManager.cpp → EXE-06 PRJ-19 PRJ-35 PRJ-36 REN-10 · DashProjectManager.h → PRJ-19 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #652(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: #486 · PRJ-c41

#### PRJ-14 · QSettings 스코프를 하나로 통일한다
- 종류: PR | 규모: M | 태그: G, D · refactor
- 목표: main.cpp 에서 `setOrganizationName`/`setApplicationName` 을 한 번 정하고 인자 있는 생성 14곳이 기본 생성자 `QSettings()` 를 쓴다. 채택 스코프(`("NohLab","DashOptiAnalyzer")` 5곳 · `("YourCompany","DashApp")` 5곳 · `("NumeReal","DashOpti")` 4곳 중 하나)는 이 PR 에서 정해 본문에 기록한다 (UIC-04 병합 — 되돌리기 비용이 큰 결정이라 PR 본문에 결정 근거를 남긴다). 구 스코프 키 마이그레이션은 두지 않는다 — 솔버 경로·최근 폴더는 재입력
- 완료 기준: (0) 채택 스코프 · 이관 없음 · 레거시 스코프 방치 결정이 PR 본문에 기록 (1) `QSettings(` 인자 있는 생성 0 (2) 솔버 경로 저장·재기동 복원 동작 (3) 로그 설정(DashLogger::loadSettings) 동작 불변
- 변경 범위: main.cpp, controller/DashManager.cpp, model/DashJobRunnerFeSafe.cpp, view/dialog/SolverSettingsDialog.cpp, view/DashMainWindow.cpp, view/dialog/AboutDialog.cpp, view/log/DashLogDockWidget.cpp
- 선행: -
- 충돌: PRJ-06 (DashManager.cpp 솔버 경로 이동) · PRJ-15 · UIC-05 (창·dock 상태 키가 이 스코프를 쓴다) · UIC-06 (DashMainWindow scaleMenu `UI/scaleFactor` 키) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashManager.cpp → CAD-03 CAD-06 DOE-19 EXE-06 PRJ-03 PRJ-04 REN-07 · main.cpp → DEV-21 DEV-24 EXE-02 EXE-06 UIC-26 · DashJobRunnerFeSafe.cpp → LCH-07 LCH-14 LCH-18 LCH-30 UIC-19 · AboutDialog.cpp → DEV-22 DEV-24 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp·DashManager.cpp) · PR #652(DashMainWindow.cpp·DashManager.cpp) · PR #651(DashJobRunnerFeSafe.cpp·DashMainWindow.cpp)
- 흡수: #481 · PRJ-c42 · #448(스코프 결정 몫) · UIC-c07 (UIC-04 병합, B2)
- 비고: 접점 UIC(로그 dock) · LCH(FeSafe). PRJ-06 이 솔버 경로를 옮기면 그 파일 대신 소유자에서. UIC-05 의 창·dock 상태 키도 이 스코프에 쓴다

#### PRJ-15 · Project 메뉴에 최근 프로젝트 목록을 붙인다
- 종류: PR | 규모: S | 태그: D · feature
- 목표: 열기·생성 성공 시 루트 경로를 QSettings 목록(최대 10)에 올리고 Project 메뉴 "Open Recent" 서브메뉴로 보여 준다. 없는 경로는 선택 시 목록에서 제거
- 완료 기준: (1) 열기 후 재기동 → 목록에 있음 (2) 삭제된 경로 선택 → 안내 + 목록 제거
- 변경 범위: view/DashMainWindow.cpp, view/DashMainWindow.h
- 선행: PRJ-14
- 충돌: PRJ-01 · PRJ-11 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashMainWindow.h → 공유 11건(deps.md 5절) · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #652(DashMainWindow.cpp·DashMainWindow.h) · PR #651(DashMainWindow.cpp)
- 흡수: #481 · PRJ-c43
- 비고: 메뉴 구성이 `DashMainWindow` 생성자 인라인(:179-300, Project 메뉴 :179-204)이라 `setupMenus` 같은 함수가 없다 — UIC-05·06 과 같은 블록을 만지므로 랜딩 순서를 맞춘다

##### Module Tree · 상류 불일치

#### PRJ-22 · 상류 불일치 검사를 모듈별 쌍 등록 구조로 일반화하고 Set 선택 시에도 갱신한다
- 종류: PR | 규모: M | 태그: C, E · refactor
- 목표: `refreshUpstreamStaleness` 의 고정 `checks[]` 를 "카테고리 루트 × 모델의 `upstreamStaleReasons()`" 일반 순회로 바꾸고, 그 가상 함수를 **PRJ-34 가 정한 자리**(공통 베이스 또는 비-QObject 인터페이스)에 기본 빈 구현으로 둔다. **갱신 시점 3개를 모두 일반화** — 프로젝트 열 때(`restoreExistingModules`)·각 모듈 Run 완료·Set 선택. Run 완료는 지금 `addDoeSampler`(`csvFileGenerated`·`analysisFinished` :486-487) 와 `addAnalysisLauncher`(`doeTableSnapshotted` :539) 의 손배선 `connect` 로만 돌아가므로, 쌍 등록이 그 시그널까지 포함하거나 모델이 공통 시그널 1개를 내게 한다. MainWindow 의 Set 선택(`handleSubItemSelection`)에서도 갱신. 동작 변화 0 — Analysis Launcher 쌍만 그대로 돈다
- 완료 기준: (1) tests/TestUpstreamStaleness 통과 + Analysis Launcher ⚠ 회귀 0 (2) 새 쌍 추가가 해당 모델 1파일 변경으로 끝남 — **`DashProject.cpp` 의 `add*()` 에 `connect` 를 손으로 더하지 않아도 Run 완료 갱신이 돈다** (3) Set 선택 직후 ⚠ 갱신 (4) 프로젝트 열기 직후 ⚠ 갱신
- 변경 범위: model/DashProject.cpp, model/DashProject.h, model/DashAnalysisLauncher.h, view/DashMainWindow.cpp, PRJ-34 가 정한 가상 함수·공통 시그널 자리의 파일
- 선행: PRJ-34 (`upstreamStaleReasons()` 와 Run-완료 공통 시그널을 어디에 둘지 — PRJ-08 과 같은 축)
- 충돌: PRJ-08 (DashMvvmModelBase·DashProject) · PR #652 #651 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · DashAnalysisLauncher.h → LCH-33 PRE-03 PRE-08 PRE-16 PRE-23 PRE-24 PRE-32 · DashProject.h → PRJ-11 PRJ-18 PRJ-19 PRJ-31 PRJ-32 PRJ-33 · PR #656(DashAnalysisLauncher.h) · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp)
- 흡수: #650 · PRJ-c34
- 비고: #650 책임: 소비 Set이 실제 사용한 입력 버전의 최신성을 판정하고 프로젝트 객체는 판정을 호출·집계하며 VM은 표시·동작 전달만 맡는다. 버전 규칙은 PRJ-23, 소비 구현은 BLD-15·RUN-31·OPT-23 등이다. #368은 PER-07 → DOE-16 → PRE-32 → BLD-20 생산·공통 판독, #685는 RUN-34·OPT-26 소비이며 조합 ID 산식이나 최초 핀을 도입하지 않는다.

#### PRJ-23 · 산출물 버전·비교 불가 상태와 최신성 판정 규칙을 정한다
- 종류: DEC | 규모: S | 태그: C, A
- 목표: #650에서 setId(동일 Set 식별), 산출물 버전(재생성 전후), 결과 항목 키를 구분한다. 생산 Set이 버전을 기록하고 소비 Set이 실제 사용한 입력 버전으로 최신성을 판정한다. 프로젝트는 호출·집계, VM은 표시를 담당한다.
- 완료 기준: 버전 의미·갱신 시점·필수 버전 누락 등 비교 불가 상태·판정 규칙을 먼저 결정한다. 비교 불가를 정상 최신으로 간주하는 정책을 선결하지 않는다. setId·deck 출처만으로 재생성 최신성을 보장하지 않으며 파일 시간·경로·임시 해시로 대체하지 않는다.
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #650 · PRJ-c35
- 비고: #368·#685 출처 계약과 별도 목표다. 필수 출처 누락 구산출물의 재생성 정책과 버전 비교 불가 상태를 구분한다. 후속 구현은 생산 Set의 버전 기록과 소비 Set별 판정, 프로젝트 집계·VM 표시로 나눈다.

##### 셸 정리

#### PRJ-19 · PRJ 영역의 죽은 코드를 지운다
- 종류: PR | 규모: M | 태그: E, G · refactor
- 목표: 호출·연결이 0인 것을 한 번에 — `DashMainWindow::onEditUndo/onEditRedo`(.cpp:4800·4806 · .h:177-178), `DashMainWindow::m_categoryWidgetMap`(.h:338 선언 · .cpp:652-659 쓰기 7곳 · 읽기 0), `DashProject::addDummyData`, `renameSet` 의 rename 불가 카테고리 분기 4개, `DashProjectManager::GetModuleDataPath/GetModuleConfigPath/GetConfigsDirectory`, `DashManager::m_treeView`
- 완료 기준: (1) 위 심볼 0 (2) 빌드·tests 통과 (3) `"Set1"` 리터럴이 PRJ 파일에서 generateNextSetName 1건만 — `controller/DashIOController.h` 의 3건은 doxygen 예시 주석이라 대상 아님
- 변경 범위: view/DashMainWindow.cpp, view/DashMainWindow.h, model/DashProject.cpp, model/DashProject.h, controller/DashProjectManager.cpp, controller/DashProjectManager.h, controller/DashManager.h
- 선행: -
- 충돌: PRJ-03 · PRJ-04 · PRJ-08 · PRJ-16 · PRJ-17 · PRJ-18 · PR #654 #652 #651 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · DashMainWindow.h → 공유 11건(deps.md 5절) · DashProject.h → PRJ-11 PRJ-22 PRJ-31 PRJ-32 PRJ-33 · DashProjectManager.cpp → EXE-06 PRJ-12 PRJ-13 PRJ-35 PRJ-36 REN-10 · DashManager.h → CAD-06 PRJ-06 · DashProjectManager.h → PRJ-13 · PR #655(DashMainWindow.cpp)
- 흡수: #488 · PRJ-c44 · PRJ-c11 · PRJ-c55 · PRJ-c56 · PRJ-c30 (m_treeView) · RUN-D1 · RUN-c72 → PRJ-c69 (`m_categoryWidgetMap`)
- 비고: #488 은 "결정 완료, 실행만" — 툴바 버튼은 이미 없고 슬롯 2개만 남았다. MorphingBar 의 Undo/Redo 라벨 버튼은 모핑 단계 이동(MOR). `m_categoryWidgetMap` 은 RUN 이 `범위밖 → PRJ` 로 넘긴 것(RUN-c72) — 결함 색인에 RUN-D1 행이 빠져 전 모듈 claims 에서 0건이었다. 메뉴 구성이 `DashMainWindow` 생성자 인라인(:179-300)이라 `setupMenus` 심볼은 없다 — 슬롯 2개 삭제는 메뉴 블록과 무관

#### PRJ-25 · 위젯의 DashMainWindow 부모 역참조를 시그널로 바꾼다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: `qobject_cast<DashMainWindow*>` 로 부모를 거슬러 MainWindow 메서드를 부르는 12곳(ModelRunnerWidget 8 · DoeSamplerWidgetBase 2 · OptimizerWidget 2)을 위젯 시그널 + MainWindow connect 로. MainWindow 의 공개 슬롯은 그대로
- 완료 기준: (1) view/ 에 `qobject_cast<DashMainWindow*>` 0 (2) CSV 생성 → Project Assets 갱신 등 기존 경로 동작 불변
- 변경 범위: view/DashMainWindow.cpp, view/DashModelRunnerWidget.cpp, view/DashModelRunnerWidget.h, view/DashDoeSamplerWidgetBase.cpp, view/DashDoeSamplerWidgetBase.h, view/DashOptimizerWidget.cpp, view/DashOptimizerWidget.h
- 선행: -
- 충돌: PRJ-01 · PR #654 (DashOptimizer) · #652 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizerWidget.h → OPT-01 OPT-05 OPT-06 OPT-13 OPT-18 OPT-21 OPT-22 UIC-22 · DashModelRunnerWidget.h → RUN-09 RUN-15 RUN-28 RUN-29 RUN-30 UIC-24 · DashDoeSamplerWidgetBase.cpp → ANA-07 DOE-05 DOE-11 · DashDoeSamplerWidgetBase.h → DOE-11 · PR #655(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: RUN-D28 · PRJ-c54
- 비고: 접점 RUN · DOE · OPT. RUN 목록의 RUN-D28 항목과 중복이면 Phase B 에서 한쪽에 합친다

#### PRJ-26 · 메뉴 다이얼로그·셸의 이벤트 펌핑 7곳을 제거한다
- 종류: PR | 규모: S | 태그: B · refactor
- 목표: TopOptPostprocessDialog 6곳(onBrowseFem 2 · parseFemToUnstructuredGrid 3 · showProgressMessage 1)과 `DashMainWindow::openFileInViewport` 1곳. 레이아웃 flush 는 `QCoreApplication::sendPostedEvents`/`adjustSize` 로, 파싱 루프의 진행 표시는 워커 또는 `QTimer` 단발로, 코루틴 안의 1곳은 `co_await` yield 로
- 완료 기준: (1) 두 파일 `processEvents` 0 (2) .fem 파싱 중 진행 메시지 표시 유지 (3) Load 스피너가 첫 프레임에 보임
- 변경 범위: view/dialog/TopOptPostprocessDialog.cpp, view/DashMainWindow.cpp
- 선행: -
- 충돌: PRJ-01 · PR #651 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · TopOptPostprocessDialog.cpp → DEV-20 EXE-09 REN-07 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #652(DashMainWindow.cpp)
- 흡수: #455 · PRJ-c45 · PRJ-c47 · CAD-D2 · CAD-c20 · EXE-c43(CAD-D2) · PRJ-c64
- 비고: 완료 판정은 #453(닫힘) 기준. c46(ViewOptions 2) 은 REN, c48(MeshQualityDialog 1) 은 MOR. 접점 EXE(워커 기반). `openFileInViewport` 1곳은 CAD-D2(데몬 stdout 재진입) 의 원인 지점 — `.prt` 경로 회귀를 완료 기준 (3) 에 포함

##### 닫기

#### PRJ-27 · #246 God-object 해체 부모를 닫는다
- 종류: CLOSE | 규모: - | 태그: E
- 목표: 추적 전용
- 완료 기준: 닫기 사유 — 실작업이 #431(PRJ-02) · #432(PRJ-08/09) · #434(PRJ-03~07) · #433(PRE) 로 전부 분해됨
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #246 · PRJ-c49

#### PRJ-28 · #247 Presentation Model 개선 단계 부모를 닫는다
- 종류: CLOSE | 규모: - | 태그: E
- 목표: 추적 전용
- 완료 기준: 닫기 사유 — 착수 전제(#451·#246) 미완이고 본문 작업 3건은 각각 #434(PM 호출부)·모듈 항목·#489(DEV) 에 흡수
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #247 · PRJ-c50

#### PRJ-29 · #239 Track B 현황 문서 이슈를 닫는다
- 종류: CLOSE | 규모: - | 태그: E
- 목표: 추적 전용
- 완료 기준: 닫기 사유 — 현황표(2026-08-21)가 낡았고 새 목록이 대체한다
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #239 · PRJ-c51

#### PRJ-30 · #376 IsProjectOpen ERROR 오탐을 닫는다
- 종류: CLOSE | 규모: - | 태그: G
- 목표: 해소됨
- 완료 기준: 닫기 사유 — 59df1ee7(#377) 로 `IsProjectOpen` 이 멤버를 직접 검사 (controller/DashProjectManager.cpp:251)
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #376 · PRJ-c31

##### Phase B 이관 (PER · BLD · DOE)

#### PRJ-31 · DashProject 의 Set json 직접 I/O 를 공용 헬퍼로 옮긴다
- 종류: PR | 규모: S | 태그: A, E · refactor
- 목표: `createModuleJsonFile`(:883-912, 쓰기 :906)·`writeSetReferenceModel`(:199-245, 읽기 :216 · 쓰기 :242) 의 `QFile` 직접 I/O 를 PER-02 가 공용 진입점으로 승격한 **`DashSaveSystem` 헬퍼**(`read/writeJsonFile` — QSaveFile · Result 반환)로 바꾼다 — 원자 쓰기 · 쓰기 실패 시 Set 생성 중단 + 사유 로그(현행은 WARN 뒤 진행) · RMW 의 읽기 규칙(손상 파일 보존)은 헬퍼 계약을 따른다. 같은 파일의 직접 읽기 — `referenceUuidForSet`(:277)·검출기 4벌(:921·:960·:979·:1000) — 도 같이 치환해 두 경로가 공존하지 않게 한다. 동작 변화는 실패 경로뿐
- 완료 기준: (1) model/DashProject.cpp 에 `QIODevice::(WriteOnly|ReadOnly)` 0 (2) 쓰기 불가 configs/ 에서 Add Set → Set 생성 0 + 사유 로그 (3) tests/test_set_identity.cpp 통과 · PER-05 왕복 게이트 적용 (4) 손상된 Set json 에서 검출기가 폴백으로 내려가는 동작 불변
- 변경 범위: model/DashProject.cpp, model/DashProject.h
- 선행: PER-02 (헬퍼)
- 충돌: PRJ-08 · PRJ-16 · PRJ-17 · PRJ-18 · PRJ-19 · PRJ-32 (DashProject.cpp) · PR #652 #651 · B2 교집합: DashProject.cpp → 공유 14건(deps.md 5절) · DashProject.h → PRJ-11 PRJ-22 PRJ-33
- 흡수: #479 · #478 · #480(버전 키는 헬퍼가 자동 기록 — PER-04) · PER-c30 · PRJ-c62
- 비고: PER-02 가 치환하는 `DashSetIdentity.cpp` 사본과 같은 PR 에 실어도 된다(PER 접점). 직쓰기 22지점/14파일 중 PRJ 몫 2지점이고 읽기 6곳이 같은 파일에 있다. 검출기 4벌의 읽기는 PRJ-32 가 그 4벌을 하나로 합치면 자리가 줄어든다 — 두 항목 중 먼저 랜딩하는 쪽이 치환하고 다른 쪽은 결과를 받는다

#### PRJ-32 · Set 의 variant 정본을 JSON `variant` 하나로 고정하고 접미사·트리 역할 판별을 없앤다 (BLD-D1)
- 종류: PR | 규모: M | 태그: C, E · refactor
- 목표: 판별 근거를 Set json 의 `variant`(생성 시 기록, 구 파일은 검출기 폴백을 로드 1회 write-back 으로 승격 — SI-3 선례) 하나로 두고, 모델이 `getVariant()` 로 들며 트리 `UserRole+2` 는 그 값을 비추는 캐시(문자열 1종)로 통일한다. 대상 검출기는 **4벌** — `detectGeometryVariant`(:918, 4단 우선순위 `variant` 키 → `Morphing` 객체 → DV source 접두 → 이름 접미) · `detectBuilderVariant`(:957) · `detectRunnerVariant`(:976) · `detectDoeSamplerVariant`(:997). `endsWith("-MCU"/"-CAD")` 판정 12곳과 `UserRole+2` bool/문자열 혼재를 제거하고, **`UserRole+2` 의 비-variant 3번째 용도**(카테고리 루트의 원래 이름, :764 기록 · :1286 복원)도 함께 정리한다 — 루트를 `setEditable(false)`(:763) 로 바꾸고 `UserRole+2` 저장과 `onItemChanged` 의 도달 불가한 `!parentItem` 복원 분기를 지운다. Set 이름의 접미사는 표시 관례로만 남긴다(이름 고정 규칙 #599 변경 없음)
- 완료 기준: (1) `git grep -nE 'endsWith\("-(MCU|CAD)"\)' model/DashProject.cpp view/DashMainWindow.cpp` 0 (2) `UserRole + 2` 의 setData 가 **variant 를 갖는 카테고리에서 문자열 1종, 나머지(Optimizer 는 현재도 미설정 · 카테고리 루트)는 미설정** (3) Sim/MCU · Morphing/CAD · Init/Resample Set 생성·복원·선택·삭제·rename 회귀 0 — 접미사 없는 구 프로젝트 복원 포함 (4) `variant` 폴백·write-back 케이스 테스트가 **검출기별 1개**(4개) (5) 카테고리 루트를 더블클릭해도 편집이 시작되지 않음 — 루트 개명 후 Set rename·delete·Add Set 이 조용히 실패하는 경로가 사라진다
- 변경 범위: model/DashProject.cpp, model/DashProject.h, view/DashMainWindow.cpp (모델 `getVariant` 접근자가 없는 ModelBuilder·ModelRunner 는 접점 BLD·RUN)
- 선행: PRJ-19 (renameSet 죽은 분기 제거) · PER-03 (`variant` 와 버전 키의 역할 분리 ⑥)
- 충돌: PRJ-16 · PRJ-17 · PRJ-18 · PRJ-24 · PRJ-08 · PRJ-31 (DashProject) · PRJ-01 (MainWindow 라우팅) · PR #652 #651 #654 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · DashProject.h → PRJ-11 PRJ-22 PRJ-33 · PR #655(DashMainWindow.cpp)
- 흡수: BLD-D1 · BLD-c01 · PRJ-c63 · PRJ-c67 (카테고리 루트 개명 · 도달 불가 가드)
- 비고: BLD 가 "변경 파일이 전부 PRJ" 로 이관. Runner(`-MCU`)·Geometry(`-CAD`)·DoeSampler 가 같은 구조라 횡단 1건. 접미사 자체를 이름에서 떼는 것은 범위 밖(이름 고정 #599 와 얽힘). 루트 개명(c67)을 여기에 넣은 이유는 그 `UserRole+2` 가 variant 와 역할이 겹치는 3번째 용도라서다 — 완료 기준 (2) 가 그 정리 없이는 성립하지 않는다. `DashProjectWidget` 은 `setEditTriggers` 를 두지 않아 기본값(DoubleClicked)으로 루트 편집이 열린다

#### PRJ-33 · Add Set 을 복원해 Resample 을 `ResampleN` 번호로 추가한다 (DOE-01 이관)
- 종류: PR | 규모: M | 태그: C, D · feature
- 목표: DOE Sampler 의 Add Set 메뉴에서 Init 은 1개 고정(있으면 비활성), Resample 은 항상 활성이며 비어 있는 가장 작은 번호의 `ResampleN` 으로 만든다. 누르면 "Resample Set이 추가됩니다" 안내를 띄운다. variant 폴백도 `ResampleN` 을 인식한다. Rename 불가·DEV 전용 가드는 그대로.
- 완료 기준: Init 있는 프로젝트에서 Resample 을 3번 추가하면 `Resample1·2·3`, `Resample2` 삭제 후 추가하면 `Resample2` · 안내 팝업 1회 · `variant` 키 없는 `DoeSampler_Resample2.json` 이 Resample 로 열린다 · 번호 규칙 단위 테스트
- 변경 범위: view/DashProjectWidget.cpp · model/DashProject.cpp · model/DashProject.h · model/preprocessor/DashDoeTableFile.cpp/.h(다음 번호 헬퍼 — `selectDoeSamplerSet` 의 `ResampleN` 파싱 재사용) · tests/TestDoeTableFile.cpp
- 선행: -
- 충돌: PR #652 · PR #651 (DashProject.cpp) · DOE-05 (DashProject.cpp:addDoeSampler) · PRJ-08 · PRJ-16 · PRJ-17 · PRJ-18 · PRJ-19 · PRJ-31 · PRJ-32 (DashProject.cpp) · DOE-02 (DashDoeTableFile 번호 헬퍼 공용) · B2 교집합: DashProject.cpp → 공유 14건(deps.md 5절) · DashProject.h → PRJ-11 PRJ-22 · DashDoeTableFile.cpp → PER-02 · DashProjectWidget.cpp → DEV-10 UIC-19
- 흡수: #615-1 · #615-2 · #615-3 · DOE-c01, DOE-c02, DOE-c03, DOE-c07, DOE-c08
- 비고: DOE-01 에서 이관(B2) — 변경 파일이 PRJ 소유(DashProjectWidget · DashProject). 접점 DOE(#615 담당, DOE-02 가 번호 헬퍼를 공용). 안내 팝업은 UIC 통지 규칙(#482)을 따른다 (DashNotify)

### REN — VTK 씬 · 렌더링

> dev @ b08a91b3. 렌더링 매니저·registry 를 만지는 열린 PR 은 없다. 열린 PR 7건 중 머지 대상 6건(#651 #652 #654 #655 #656 #658 — #530 은 재업로드 노선이라 제외) 가운데 REN 과 파일이 겹치는 것은 4건 — #654(#332 — DashMainWindow.cpp · DashManager.cpp · DashMorphingController · DashHandleVisualizer · DashGeometryParameterWidget.cpp) · #655(#430, #654 스택 — DashMainWindow.cpp · DashGeometryParameterWidgetPreview.cpp · DashHandlePickingInteraction.cpp · DashHandleVisualizer.cpp · DashMorphingController.cpp · DashGizmo.cpp · DashMorphingSettings.cpp) · #652(#604 — DashMainWindow.{h,cpp} · DashManager.{h,cpp}) · #651(#616 — DashMainWindow.cpp · DashModelingTreeWidget.cpp). #656 · #658 은 model/preprocessor 쪽이라 접점이 없다.
> #655 는 전부 **충돌**이고 어느 REN 항목의 **선행**도 아니다 — DashMainWindow.cpp 몫은 `handleSubItemSelection` 의 gizmo visibility 1줄 · `initializeMorphingController` · `setupMorphingBar` 이고, `resetMorphingTarget` 의 매니저 경유 해제(REN-04 의 전제)와 `addMorphingPreviewActor` 호출 구조(REN-07·10 의 전제)는 #655 전후가 같다. 단 #654·#655 가 c02 의 직접 조작 21+10 곳을 다시 쓰므로 그 집계는 머지 후 재확인한다.
> 구성 — #319 의 4건(REN-01~04)과 split view 해제(REN-05)는 소유권 모델과 독립인 선행 파일럿. #318 본 구현은 결정(REN-06) → 소유자 태그(REN-07) → 공유 자원 2건(REN-08 · 09) → 인수=숨김(REN-10) 순. #320 은 결정(REN-11) 뒤 구현(REN-12 — 매니저 창구만 전제, 소유자 인자는 REN-07 이 뒤에 와도 된다). Optimizer Preview 전량 삭제(#316 = OPT-01)는 OPT 소관이며 REN-10 의 선행이고, OPT-01 이 `DashRenderingManager.{h,cpp}` 에 전용 preview actor API 를 신설하므로 아래 직렬 규칙에 함께 넣는다.
> 덮어쓰기 지점 재집계 — 이슈의 12곳 전부 현존(Project Assets 삭제 1곳은 #617 에서 조건부로 완화). 이슈가 #406 으로 제외한 `addMorphingPreviewActor` 는 매니저 내부에서 여전히 RESULT·COMPONENT 와 scalar bar 를 지우고 `m_actors[LAYER_MORPHING]` 단일 슬롯을 쓰므로 13곳째로 되살린다(REN-c20). 이 중 OCCT `loadStepFile` 은 별도 씬(CAD), Optimizer Preview 는 #316(OPT-01).
> 매니저 밖 직접 renderer 조작은 controller 21(Visualizer 4 · Picking 6 · MorphingController 11) + DashGizmo 10 + view 3 — #318 범위 제외 절과 같은 집계다(REN-c02, 항목 없음).
> Phase B1 흡수(범위밖 이관, REN-c34~c35): PRJ-c46(#455 View Options processEvents 2곳) → REN-13(신규) · EXE-c41 CON-D2 몫 → 해소됨(항목 없음).

#### REN-01 · FE actor 재표시가 카메라를 초기화하지 않게 한다 — 리셋은 최초 표시와 사용자 조작에서만
- 종류: PR | 규모: S | 태그: D, E · bug
- 목표: `DashAnalysisModelContextRegistry::updateActor` 의 무조건 `resetCamera()` 를 "이전 `m_displayedActor` 가 null 이었던 최초 표시" 조건 아래로 넣는다. 같은 경로 재표시 · Load 재클릭 · Modeling Tree `dat_parent`/`dat_part` 토글 · 다른 FE 파일로 교체 · 프로젝트 복원(`restoreReferenceModel`) 에서 사용자가 맞춘 카메라가 유지된다.
- 완료 기준:
  1. registry 의 `resetCamera` 1곳(`DashAnalysisModelContextRegistry.cpp:430`)이 "교체 전 `m_displayedActor` 가 null" 조건 안에 있다 — 조건 없는 호출 0 (코드 검사)
  2. `TestAnalysisModelContextRegistry.cpp` 에 "표시 중 actor 가 있는 상태의 `updateActor` 는 매니저에 카메라 리셋을 요청하지 않는다" 를 넣는다 — 렌더 윈도우가 필요하면 단정 대상을 호출 여부로 좁히고, 그조차 불가면 (3) 의 수동 회귀로 대체한다고 PR 본문에 적는다
  3. 수동: 카메라를 돌린 뒤 Load 재클릭 · `dat_parent` 토글 · 다른 FE 파일 Load 에서 카메라가 유지되고, 빈 씬의 첫 Load 는 모델이 화면에 맞는다
- 변경 범위: controller/DashAnalysisModelContextRegistry.cpp · controller/DashAnalysisModelContextRegistry.h
- 선행: -
- 충돌: REN-02 (registry 에 visibility API 를 추가하는 경우) · B2 교집합: DashAnalysisModelContextRegistry.cpp → EXE-22 PRJ-03 REN-07 UIC-19
- 흡수: #319-2 · REN-c11, c22
- 비고: #318 "공유 자원은 매니저 중재" 의 첫 적용이고, 기준값은 #319 완료 조건 "카메라 리셋이 사용자 조작 없이 일어나지 않는다" 다. 본 항목은 registry 한정 — 모듈이 스스로 부르는 `resetCamera` 2곳(`DashOptimizerWidget.cpp:1814` = OPT-01 완료 기준 (3) · `DashModelRunnerWidget.cpp:1545`)은 사용자가 Preview 를 눌러 시작한 리셋이라 범위 밖이고, 사용자 조작 없는 나머지 1곳 `loadVtkFile`(`DashMainWindow.cpp:3905`, Modeling Tree 재토글마다 리셋)은 REN-12 가 맡는다. `tests/TestAnalysisModelContextRegistry.cpp` 는 현재 `updateActor` 를 덮지 않는다(렌더 윈도우 의존).

#### REN-02 · Start Morphing 이 숨긴 FE actor 의 복원 경로를 만든다
- 종류: PR | 규모: S | 태그: A, D · bug
- 목표: FE actor 숨김·복원을 매니저 API(`setAnalysisModelActorVisibility`)로 통일하고 복원 지점 2개를 둔다 — Modeling Tree `dat_parent`/`dat_part` 체크 on 시 `ctx->controlVisibility` 앞에서 displayed actor 를 보이게, 모듈 이탈(`handleSubItemSelection`) 시 displayed actor 를 복원. `onStartMorphingClicked` 의 `displayedActor->SetVisibility(false)` 직접 호출을 매니저 경유로 바꾼다. 복원은 트리 눈 상태도 같이 맞춘다 — Start Morphing 이 `resetAllViews()` 로 모든 눈을 끈 뒤이므로(`DashMainWindow.cpp:4741`, `blockSignals` 아래 UserRole 만 false) actor 만 되살리면 체크박스와 화면이 어긋난다.
- 완료 기준:
  1. Morphing 진입 후 다른 모듈로 전환하면 FE 모델이 다시 보인다 (Load 재클릭 불필요)
  2. 그때 Modeling Tree 의 해당 `dat_parent` 눈이 on 으로 돌아온다 — `DashModelingTreeWidget::checkDatFileItem(path, true)` 또는 `displayedActorUpdated` 수신으로 갱신 (체크박스↔화면 불일치 = #320 이 지적한 증상의 재생산 금지)
  3. Morphing 진입 후 Modeling Tree `dat_parent` 체크로 FE 모델이 다시 보인다
  4. `git grep -E 'displayedActor(\(\))?->SetVisibility' view/` 0건
- 변경 범위: view/DashMainWindow.cpp (`onStartMorphingClicked` · `handleSubItemSelection` · `onTreeFileCheckChanged`) · 필요 시 controller/DashAnalysisModelContextRegistry.{h,cpp} (`setDisplayedActorVisible(bool)`) · 트리 눈 복원을 `checkDatFileItem` 으로 할 경우 호출 1줄(선언은 이미 view/DashModelingTreeWidget.h:44 에 있음 — 트리 파일 변경 없음)
- 선행: -
- 충돌: PR #654 · #655 · #652 · #651 (DashMainWindow.cpp — #655 는 `handleSubItemSelection` 같은 함수) · REN-04 · REN-10 (같은 함수) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashAnalysisModelContextRegistry.cpp → EXE-22 PRJ-03 REN-01 REN-07 UIC-19 · DashAnalysisModelContextRegistry.h → REN-01
- 흡수: #319-1 · REN-c14 (숨김 부분), c21
- 비고: #318 "유지 정책은 콘텐츠 부류별 — 문서형 유지" 의 선취. Morphing 모듈 안에서는 미리보기와 겹치므로 복원하지 않고 이탈 시점에만. 트리 동기화는 현재 `onDisplayedContextChanged` 수신에서만 일어나므로(`DashModelingTreeWidget.cpp:681-711`) 복원 경로가 registry API 를 거쳐야 눈 상태가 함께 간다. #315 재클릭 게이트의 선행(dead-end 제거).

#### REN-03 · Model Runner Preview 가 FE actor 를 결과 위에 남기지 않게 한다 — 삭제가 아니라 숨김
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `performPreviewLogic` 의 `clearAllLayers()` 뒤에 displayed FE actor 를 `setAnalysisModelActorVisibility(false)` 로 숨긴다. `m_analysisModelActors` 는 비우지 않는다. 복원은 REN-02 의 경로(Modeling Tree 체크 · 모듈 이탈)에 맡기고 `clearAllLayers` 의 "clean slate" 주석을 실제 범위로 고친다.
- 완료 기준:
  1. FE 모델 Load 후 Model Runner Preview 를 돌리면 FE actor 가 결과 위에 보이지 않는다
  2. Preview 후 Modeling Tree `dat_parent` 체크 또는 모듈 이탈로 FE 모델이 돌아온다
  3. `clearAllLayers` 가 `m_analysisModelActors` 를 제거하는 코드 0
- 변경 범위: view/DashModelRunnerWidget.cpp · controller/DashRenderingManager.cpp (주석)
- 선행: REN-02
- 충돌: REN-05 · REN-10 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashRenderingManager.cpp → 공유 10건(deps.md 5절)
- 흡수: #319-3 · REN-c23, c16 (FE actor 부분)
- 비고: REN-02 의 "모듈 이탈 복원" 은 Geometry 이탈뿐 아니라 모든 모듈 전환에 걸려야 Model Runner 이탈에서도 FE 가 돌아온다 — REN-02 구현 시 `handleSubItemSelection` 의 공통 경로에 둔다.

#### REN-04 · Geometry actor 의 등록·해제를 매니저 창구로 통일하고 중복 등록을 막는다
- 종류: PR | 규모: S | 태그: E · bug
- 목표: `onStartMorphingClicked` 의 직접 `GetRenderer()->RemoveActor(actor)`(`DashMainWindow.cpp:4587`)를 지운다 — 바로 뒤 `setModel` → `resetMorphingTarget` 이 `removeAnalysisModelActor` 로 같은 actor 를 떼므로 중복 호출이고, 지우면 Geometry actor 해제가 매니저 창구 1개로 모인다. `addAnalysisModelActor` 에 `contains` 조기 반환을 넣어 같은 actor 의 이중 등록을 막는다.
- 완료 기준:
  1. `git grep -n 'GetRenderer()->RemoveActor' view/DashMainWindow.cpp` 0건 (`m_vtuVtkActors` 루프의 `renderer->RemoveActor` 는 REN-12 몫이라 이 grep 에 걸리지 않는다)
  2. `addAnalysisModelActor` 진입부에 `m_analysisModelActors.contains(actor)` 조기 반환 1곳 (코드 검사)
  3. 수동: Set 을 3회 이상 바꾼 뒤 View Options 의 wireframe·clipping 토글이 현재 Set 의 actor 에만 걸린다 (목록에 죽은 항목이 없다는 관측 가능한 대리 — `m_analysisModelActors` 는 private 이고 접근자가 없다)
- 변경 범위: view/DashMainWindow.cpp · controller/DashRenderingManager.cpp
- 선행: -
- 충돌: PR #654 · #655 · #652 · #651 (DashMainWindow.cpp) · REN-02 · REN-07 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashRenderingManager.cpp → 공유 10건(deps.md 5절)
- 흡수: #319-4 · REN-c24, c25
- 비고: #319-4 의 "모델을 바꿀 때마다 목록이 누적" 은 #332 이후 사실상 닫혔다 — Start Morphing 은 Set 변경 여부와 무관하게 `setModel` → `resetMorphingTarget`(매니저 해제 + `SetCurrentActor(nullptr)`) → `UpdateTargetGeometry`(재등록) 순이고, `geometry_` 와 current actor 가 같이 세팅·리셋되어 가드 불일치 경로가 없다. 그래서 `SetCurrentActor` 에 선해제를 더 넣지 않는다 — 호출처가 `DashGeometryParameterWidget.cpp:2189`(nullptr) · `:2276`(신규) 2곳뿐이고 해제는 이미 `resetMorphingTarget` 이 한다. 남는 것은 :4587 중복 호출과 등록 가드 2건. `m_analysisModelActors` 순회 3곳(`setRepresentation` · `updateClipping` 2) 이 죽은 항목을 만지는 증상이 함께 닫힌다.

#### REN-05 · 씬을 새로 그리는 모든 매니저 경로가 split view 를 먼저 해제하게 한다
- 종류: PR | 규모: S | 태그: A, E · bug
- 목표: `updateAllGeometry` · `updateComponentGeometry` · `updateFieldOutput` · `addAnalysisModelActor` · `addMorphingPreviewActor` · `updateFeConditionHighlight` · `clearAllLayers` 진입부에서 `clearSplitView()` 를 부른다(내부 `m_isSplitViewActive` 가드로 비활성 시 no-op). `performPreviewLogic` 의 `isSplitViewActive`/`clearSplitView` 수동 호출을 지운다.
- 완료 기준:
  1. Model Builder Test Results Preview 뒤 Project Assets Load · Optimizer Preview · Morphing 진입 · Launcher preview 가 화면에 나타난다 (메인 renderer `GetDraw()` true)
  2. `isSplitViewActive()` · `clearSplitView()` 호출처가 매니저 밖에 0
- 변경 범위: controller/DashRenderingManager.cpp · view/DashModelRunnerWidget.cpp
- 선행: -
- 충돌: REN-03 · REN-07 · REN-08 · REN-09 · OPT-01 (DashRenderingManager.cpp) · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashRenderingManager.cpp → 공유 10건(deps.md 5절)
- 흡수: #318 완료 조건 2 · 문제 상세 1 · REN-c18
- 비고: 모듈 전환(`handleSubItemSelection`)은 지우기만 하고 그리지 않아 split view 가 남는다 — 전환 시 해제는 REN-10 의 인수 규칙에 넣는다. `SetDraw` 가 매니저 전용 공유 자원이라는 것은 #318 해법 방향이 이미 정한 것이라 결정 대기 없음.

#### REN-06 · 소유자 식별 형태와 문서형 명시 해제 시점을 확정한다
- 종류: DEC | 규모: S | 태그: E, A · refactor
- 목표: #318 "해법 방향 — 2026-09-21 확정" 과 "범위에서 제외" 절이 이미 답한 것(콘텐츠 부류표 = 문서형 Project Assets `.vtk/.vtu` BASE · FE displayed actor / 작업물형 Launcher preview · Model Runner 결과 · Optimizer preview · Morphing preview · CON highlight, 모듈 이탈 시 작업물형 폐기, 공유 자원 카메라·scalar bar·cube axes·`SetDraw` 는 매니저 중재, 핸들·피킹·DashGizmo 등 모듈 수명 표시물은 "존재 등록만")은 재결정하지 않는다. 남은 2개만 답한다 — (a) 소유자 식별 형태: enum 신설 vs 모듈 ID 문자열(`DashModuleName` 재사용), 문서형 소유자를 모듈과 같은 축에 둘지 (c) 문서형 명시 해제 시점과 API 형태: `DashProjectManager::CloseProject`(registry.clear 자리) · Project Assets 삭제 외에 지점이 더 필요한지, 일괄 `releaseDocuments()` 인지 단건 `releaseDocument(path)` 인지(#318 완료 조건 5).
- 완료 기준: 결정 기록 — 2개 질문의 답 + REN-07 · REN-10 의 설계 입력(소유자 타입의 정의 위치 · 해제 API 시그니처)
- 변경 범위: 문서만
- 선행: -
- 충돌: -
- 흡수: #318 해법 방향(미결 2문항) · 완료 조건 5 · REN-c04 (해제 시점)
- 비고: 종전 6문항 중 (b)(d)(e)(f) 는 #318 본문에 답이 있어 제외했다 — 결정 대기로 둘 이유가 없다(검토 #13). 메모리 검토는 이슈 본문 그대로 유효(`SetInputData` 참조 공유). `TopOptPostprocessDialog` 는 자체 `DashRenderingManager` 인스턴스 — API 변경의 컴파일 영향만 받는다.

#### REN-07 · 레이어·actor 에 소유자 태그를 붙이고 "지금 누가 그렸는지" 질의 API 를 둔다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: 콘텐츠 진입 API(`updateAllGeometry` · `updateComponentGeometry` · `updateFieldOutput` · `addMorphingPreviewActor` · `addAnalysisModelActor`) 에 소유자 인자를 추가하고 레이어·actor 별 소유자를 기록한다. `addAnalysisModelActor` 는 소유자를 내부 고정할 수 없다 — registry 가 문서형 FE actor 로(`DashAnalysisModelContextRegistry.cpp:429`), `DashManager::SetCurrentActor` 가 Geometry actor(모듈 수명 표시물)로(`DashManager.cpp:299`) 같은 함수를 부르므로, `addAnalysisModelActor(actor, owner)` 로 인자를 받아 registry 는 Document, `SetCurrentActor` 는 GeometryParameterization 을 넘긴다. `updateFeConditionHighlight` 만 CON 고정이라 시그니처 불변. `layerOwner(Layer)` · `sceneOwners()` 질의를 추가하고 `clearModuleLayers` 는 삭제한다. 동작 불변.
- 완료 기준:
  1. 호출처 전부가 소유자를 넘긴다 — 기본 인자 없음, 컴파일로 강제
  2. 인자를 버리는 `clearModuleLayers` 0
  3. Load → Launcher preview → Model Runner preview 순서에서 `layerOwner(LAYER_BASE_GEOMETRY)` 가 ProjectAssets → Launcher → ModelRunner 로 바뀐다 (디버그 로그)
  4. 화면 동작 변화 없음
- 변경 범위: controller/DashRenderingManager.h · controller/DashRenderingManager.cpp · controller/DashManager.cpp · controller/DashAnalysisModelContextRegistry.cpp (`addAnalysisModelActor` 호출 1곳) · view/DashMainWindow.cpp (Launcher connect 3곳을 람다로 · `loadVtkFile` · `showScalarField`:3149 — `updateFieldOutput` 호출) · view/DashModelRunnerWidget.cpp · view/DashOptimizerWidget.cpp · view/DashGeometryParameterWidgetPreview.cpp · view/dialog/TopOptPostprocessDialog.cpp
- 선행: REN-06
- 충돌: PR #654 · #655 · #652 · #651 (DashMainWindow.cpp · DashManager.cpp · DashGeometryParameterWidgetPreview.cpp) · REN-04 · REN-05 · REN-08 · REN-09 · REN-12 · OPT-01 (DashRenderingManager) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashRenderingManager.cpp → 공유 10건(deps.md 5절) · DashManager.cpp → CAD-03 CAD-06 DOE-19 EXE-06 PRJ-03 PRJ-04 PRJ-06 PRJ-14 · DashRenderingManager.h → PRJ-04 REN-10 · DashAnalysisModelContextRegistry.cpp → EXE-22 PRJ-03 REN-01 REN-02 UIC-19 · TopOptPostprocessDialog.cpp → DEV-20 EXE-09 PRJ-26 · DashGeometryParameterWidgetPreview.cpp → REN-10
- 흡수: #318 완료 조건 1 · REN-c01, c03, c08, c09, c10 (태그 부여 지점), c15 (태그 부여 지점)
- 비고: 파일 9개지만 호출당 인자 1개의 순변경. #315 재클릭 게이트(PRJ 소관, 후행)가 이 질의를 판정 근거로 쓴다. 분할 대안 — 기본 인자로 2단계 전환하면 임시 폴백이 생기므로 한 커밋. OPT-01 이 신설하는 전용 preview actor API 도 소유자 인자를 받아야 한다 — 어느 쪽이 먼저 랜딩하든 뒤에 오는 쪽이 맞춘다(OPT-01 충돌란에 명시됨).

#### REN-08 · base actor 의 ghost 외형을 매니저가 저장·복원한다
- 종류: PR | 규모: S | 태그: A, E · refactor
- 목표: ghost(wireframe · opacity 0.05 · lighting off) 적용 2곳을 `applyBaseGhost()` 로 모으고 적용 직전 원 외형을 보관, `restoreBaseAppearance()` 로 되돌린다. 복원 호출 — `updateComponentGeometry` 의 빈 grid 분기(현행) + ghost 를 유발한 COMPONENT/RESULT 레이어가 지워지거나 숨겨질 때.
- 완료 기준:
  1. ghost 적용 코드가 `applyBaseGhost()` 1곳 · 원복 코드가 `restoreBaseAppearance()` 1곳 (코드 검사)
  2. `restoreBaseAppearance` 호출처가 현행 복원 지점(`updateComponentGeometry` 의 빈 grid 분기) + COMPONENT/RESULT 레이어가 `clearLayer` 되거나 숨겨지는 경로 전부 (코드 검사)
  3. 수동: Launcher component preview → "All" 에서 base actor 가 surface · opacity 1.0 으로 돌아온다 (현행과 동일 — 단독 랜딩에서는 동작 불변)
- 변경 범위: controller/DashRenderingManager.h · controller/DashRenderingManager.cpp
- 선행: -
- 충돌: REN-05 · REN-07 · REN-09 · REN-10 · OPT-01 (DashRenderingManager) · B2 교집합: DashRenderingManager.cpp → 공유 10건(deps.md 5절) · DashRenderingManager.h → PRJ-04 REN-12
- 흡수: #318 완료 조건 4 · 문제 상세 3 · REN-c06 ; REN-c07 은 2단계(비고)
- 비고: 단독으로는 동작 불변이다 — "All" 경로는 지금도 복원되고(`DashRenderingManager.cpp:118-127`), 모듈 전환은 `handleSubItemSelection` 이 BASE 를 지워(`DashMainWindow.cpp:1301-1302`) base actor 자체가 없다. 화면으로 관찰되는 것은 REN-10 랜딩 뒤이고, 그 관찰은 REN-10 완료 기준 2 가 맡는다. 그래서 REN-10 의 숨김 전환 전에 들어가야 한다. REN-c07(`DashManager::updateOriginalActor` 로 모핑 중 해석 모델 actor 를 opacity 0.3 으로, 복원은 `DashMorphingSettings::UpdateAppearance`)은 MOR 소유 actor 의 외형이라 본 항목에서 손대지 않는다 — 매니저 중재로 옮길지는 MOR 과 협의(접점).

#### REN-09 · scalar bar · cube axes 의 생성·해제를 매니저 단일 경로로 모은다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: scalar bar 제거 5곳(`updateAllGeometry`:66 · `updateComponentGeometry`:105 · `updateFieldOutput`:182 · `clearAllLayers`:614 · `addMorphingPreviewActor`:1291) → `releaseScalarBar()` 1곳, cube axes 생성 2곳(`updateAxes`:690 · `addAnalysisModelActor`:1135) → 1곳 · 제거 2곳(`clearAllLayers`:620 · `updateAxes`:683) → 1곳. 제거를 `clearAllLayers` 에서 분리해 "씬 장식 해제" 로 둔다. split view 전용 축(`m_exactAxes` · `m_predictionAxes`)과 split view scalar bar 는 별 자원이라 그대로 둔다. 동작 불변.
- 완료 기준:
  1. `RemoveActor2D(m_scalarBar)` 1곳 · `m_cubeAxes = …::New()` 1곳 · `RemoveActor(m_cubeAxes)` 1곳 (split view 의 `m_exactAxes`·`m_predictionAxes` 생성 2곳은 대상 아님 — `vtkCubeAxesActor>::New` 전체 grep 은 4→3 이 된다)
  2. 화면 변화 없음 (Launcher field preview · Model Runner preview · FE Load 의 축·바 표시 동일)
- 변경 범위: controller/DashRenderingManager.cpp · controller/DashRenderingManager.h
- 선행: -
- 충돌: REN-05 · REN-07 · REN-08 · REN-10 · OPT-01 (DashRenderingManager) · B2 교집합: DashRenderingManager.cpp → 공유 10건(deps.md 5절) · DashRenderingManager.h → PRJ-04 REN-12
- 흡수: REN-c05 (코드 부분)
- 비고: 숨김 전환 시 scalar bar · cube axes 를 현재 소유자에 종속시키는 규칙은 #318 해법 방향("공유 자원은 매니저 중재")이 이미 정했다 — REN-10 이 그 규칙을 적용한다.

#### REN-10 · 다른 모듈의 씬 인수를 "파괴" 에서 "숨김 + 작업물 폐기" 로 바꾼다
- 종류: PR | 규모: M | 태그: A, E · bug
- 목표: 지점 5곳의 `clearLayer`/`clearAllLayers` 를 매니저 API 로 교체한다. 기제가 둘이라 API 도 둘이다 — 섞으면 모듈 전환이 Load 모델을 숨겨 완료 기준 1 · #318 완료 조건 3 · REN-02 와 충돌한다(검토 #10).
  - `takeOver(owner)` — **그리기 시작**: `onStartMorphingClicked` · `performPreviewLogic` · `addMorphingPreviewActor` · 매니저 update* 내부(Launcher 시그널 3개는 호출부 무변경). 다른 소유자의 문서형은 `SetVisibility(false)`, 작업물형은 제거, ghost 복원, split view 해제.
  - `releaseWorkProducts(owner)` / `releaseDocument(path)` — **폐기**: `handleSubItemSelection`(떠나는 모듈의 작업물만 폐기, 문서형은 복원) · `removeReferenceAsset`(삭제한 파일이 소유한 문서형만 해제) · `CloseProject` 의 `releaseDocuments()`(#318 완료 조건 5).
  결과로 Project Assets Load 모델(BASE 문서형 · FE actor)이 모듈 전환에 살아남고 `.dat`/`.vtu` 확장자별 차이가 없어진다. `handleSubItemSelection` 의 카테고리 문자열 비교 분기를 없앤다.
- 완료 기준:
  1. `.vtu` Load → 모듈 전환 → 복귀에서 모델이 보인다(재Load 불필요); `.dat` 도 같은 동작
  2. 모듈 이탈 뒤 base actor 가 ghost 가 아니다
  3. `git grep -n 'clearLayer(\|clearAllLayers(' view/` 0건 — 레이어 clear 는 매니저 내부만
  4. `DashProjectManager::CloseProject` 에 `releaseDocuments()` 호출 1곳(`Registry::Instance().clear()` 자리, `DashProjectManager.cpp:246`); 수동으로 `.vtu` Load → 프로젝트 닫기 → 새 프로젝트에서 이전 모델이 화면에 없다
- 변경 범위: controller/DashRenderingManager.h · controller/DashRenderingManager.cpp · view/DashMainWindow.cpp · view/DashModelRunnerWidget.cpp · controller/DashProjectManager.cpp (1줄). `addMorphingPreviewActor` 호출부(view/DashGeometryParameterWidgetPreview.cpp)는 REN-07 이 이미 소유자 인자를 넘기므로 무변경
- 선행: REN-07 · REN-08 · REN-02 · REN-03 · REN-05 · OPT-01 (#316 — Optimizer Preview 의 actor 전량 삭제가 남아 있으면 숨긴 문서형 actor 도 떼어 간다)
- 충돌: PR #654 · #655 · #652 · #651 (DashMainWindow.cpp — #655 는 `handleSubItemSelection` 같은 함수) · REN-12 (DashMainWindow.cpp 같은 함수) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashRenderingManager.cpp → 공유 10건(deps.md 5절) · DashProjectManager.cpp → EXE-06 PRJ-08 PRJ-12 PRJ-13 PRJ-19 PRJ-35 PRJ-36 · DashRenderingManager.h → PRJ-04 REN-09
- 흡수: #318 완료 조건 3 · 문제 상세 2 · REN-c04 (코드 부분), c12, c13, c14 (clear 부분), c15 (인수 규칙), c16, c20
- 비고: 작업물형은 모듈 이탈 시 폐기(복구 = 재실행) — #318 해법 방향이 정한 것이라 결정 대기 없음. 해제 API 를 일괄/단건 중 어느 모양으로 둘지는 REN-06 (c). `removeReferenceAsset` 은 #617 에서 `isDisplaying || vtk_parent` 조건부가 됐으므로(`DashMainWindow.cpp:2889-2894`) "삭제한 파일이 소유한 것만" 으로 좁히면 된다. DashProjectManager.cpp 는 PRJ 접점 — 1줄. 항목을 둘로 쪼개지는 않는다 — "인수를 파괴에서 숨김+작업물 폐기로" 가 한 개념이고 API 2개는 그 한 규칙의 양면이다(00-plan 1-2 개념적 응집).

#### REN-11 · 복수 .vtk/.vtu 동시 표시 요구를 확정한다
- 종류: DEC | 규모: S | 태그: D
- 목표: Modeling Tree 의 `.vtu/.vtk` 토글이 (b) 파일별 actor 복수 동시 표시(매니저 창구 경유) 인지 (c) 단일 표시 유지 + 복수 표시를 전제한 코드 정리 인지 결정한다. BASE 슬롯은 1개이고 트리는 `.vtk/.vtu` 를 `vtk_parent` + 자식 `vtk_single` 1개로만 만든다 — 결정 대상은 "`vtk_parent` 행 여러 개를 동시에 표시할 것인가" 다. (a) `m_vtuVtkActors` 에 채워 renderer 직접 추가는 #318 이 금지.
- 완료 기준: 결정 기록 — 요구 + REN-12 의 범위(M 또는 S)
- 변경 범위: 문서만
- 선행: -
- 충돌: -
- 흡수: #320 to-be 4 · not-to-be · REN-c29
- 비고: 현재 코드는 복수 표시를 전제로 쓰여 있으나 BASE 슬롯 1개라 성립하지 않는다. `vtm_parent` 는 행 생성 코드가 없어(`git grep vtm_parent` = `DashMainWindow.cpp:3722` `:3730` 뿐) 결정 대상이 아니다 — 죽은 분기 삭제는 결정과 무관하게 REN-12 범위. REN-06 선행 불필요 — (a) 금지는 #318 이 이미 못박았다(검토 #11).

#### REN-12 · Modeling Tree 의 .vtk/.vtu 표시 토글을 매니저 창구로 구현한다
- 종류: PR | 규모: M | 태그: A, D · bug
- 목표: `m_vtuVtkActors` 를 없애고 매니저에 파일별 문서형 actor API(`showFileActor(path, grid)` · `setFileActorVisible(path, bool)` · `removeFileActor(path)`, 소유자는 매니저 내부 고정 ProjectAssets)를 둔다. 체크 on/off 가 그 actor 의 visibility 만 바꾸고 다른 레이어를 지우지 않으며, 같은 파일 재토글은 디스크를 읽지 않고 **카메라도 건드리지 않는다** — 지금은 캐시가 항상 miss 라 토글마다 `loadVtkFile` 이 돌고 그 끝의 무조건 `resetCamera`(`DashMainWindow.cpp:3905`)가 사용자 시점을 초기화한다(#319 완료 조건 "사용자 조작 없는 리셋 0"). `openFileInViewport` 의 직접 `RemoveActor` 루프와 `onStartMorphingClicked` 의 숨김 루프도 매니저 경유로, 죽은 `vtm_parent` 분기는 삭제한다. 결정이 (c) 면 복수 표시 전제 코드 정리로 범위가 S 로 준다.
- 완료 기준:
  1. 체크 off 로 해당 파일이 사라지고 on 으로 돌아온다 — 다른 레이어 불변
  2. 같은 파일 재토글에 reader 호출 0 (로그) · 카메라 불변 (수동: 시점을 돌린 뒤 off→on)
  3. `git grep m_vtuVtkActors` 0건 · `git grep vtm_parent` 0건
  4. (b) 일 때 `.vtk/.vtu` 2개가 동시에 보인다
- 변경 범위: view/DashMainWindow.h · view/DashMainWindow.cpp · controller/DashRenderingManager.h · controller/DashRenderingManager.cpp (트리 쪽은 `vtk_parent`·`vtk_single` 행 생성만 하고 일괄 토글 UI 가 없어 view/DashModelingTreeWidget.cpp 변경 없음)
- 선행: REN-11
- 충돌: PR #654 · #655 · #652 · #651 (DashMainWindow) · REN-07 (매니저 API 에 소유자 인자 추가 — 뒤에 오면 인자만 더한다) · REN-10 (`onTreeFileCheckChanged` · `openFileInViewport` · `onStartMorphingClicked`) · OPT-01 (DashRenderingManager) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashMainWindow.h → 공유 11건(deps.md 5절) · DashRenderingManager.cpp → 공유 10건(deps.md 5절) · DashRenderingManager.h → PRJ-04 REN-08 REN-09 · DashModelingTreeWidget.cpp → DEV-10 PRJ-04
- 흡수: #320 · REN-c10 (토글 측), c26, c27, c28, c29
- 비고: Project Assets Load 경로(`loadVtkFile` isParent → BASE)의 단일 표시는 유지하되 같은 매니저 API 로 간다. `#320` 의 `blocked` 라벨은 매니저 창구 API 가 생길 때까지 유효하다 — #320 (b) 가 요구하는 것은 창구 경유이고 소유자 **태그**는 아니므로, REN-07(M, REN-06 뒤)을 선행으로 두어 #320 을 결정 2건 뒤로 밀지 않는다(검토 #12).

#### REN-13 · View Options 토글 람다의 `processEvents` 를 없애고 레이아웃 갱신을 Qt 에 맡긴다
- 종류: PR | 규모: S | 태그: B, E · refactor
- 목표: `DashViewOptionsWidget` 생성자의 `m_btnClip`·`m_btnColorBar` toggled 람다가 자식 프레임 `setVisible` 뒤 `adjustSize()` 앞에서 `QApplication::processEvents(ExcludeUserInputEvents)` 로 레이아웃을 flush 한다. `layout()->activate()` 뒤 `adjustSize()`(또는 `QTimer::singleShot(0, …)`)로 바꿔 중첩 이벤트 루프 재진입을 없앤다. 동작(오버레이 수축·확장) 불변.
- 완료 기준:
  1. `git grep -n processEvents view/overlay/DashViewOptionsWidget.cpp` 0건
  2. Clip·Color Bar 토글 on/off 에서 오버레이 크기가 현행과 같음(수동)
  3. DEV-18 grep 게이트의 view 기준값 14 → 12
- 변경 범위: view/overlay/DashViewOptionsWidget.cpp
- 선행: -
- 충돌: - (열린 PR 이 이 파일을 만지지 않음) · B2 교집합: DashViewOptionsWidget.cpp → UIC-07
- 흡수: #455 (REN 몫, PRJ-c46 이관) · REN-c34
- 비고: `adjustSize()` 는 `sizeHint()` 를 쓰므로 `layout()->activate()` 로 레이아웃 캐시를 무효화하면 flush 없이 충분한지 1회 확인 — 아니면 `QTimer::singleShot(0, this, &QWidget::adjustSize)`. 가드·레인 표준(EXE-c22 · c03)과 무관한 단순 제거.

##### 선행 순서

- 독립 착수 가능: REN-01 · REN-02 · REN-04 · REN-05 · REN-06 · REN-08 · REN-09 · REN-11 · REN-13 · (REN-03 은 REN-02 뒤)
- REN-06 → REN-07 → REN-10 (+ REN-08 · REN-02 · REN-03 · REN-05 · OPT-01)
- REN-11 → REN-12 (REN-07 은 선행 아님 — 뒤에 오면 소유자 인자만 더한다)
- 같은 파일 동시 수술 금지 ① `DashRenderingManager.{h,cpp}`: OPT-01 · REN-05 · 07 · 08 · 09 · 10 · 12 를 직렬로 한다. OPT-01 이 전용 preview actor API 를 신설하므로(`addMorphingPreviewActor` 재사용 불가 — RESULT·COMPONENT 레이어와 scalar bar 를 파괴하고 저장 슬롯이 `m_actors[LAYER_MORPHING]` 단일) 이 파일에 들어오고, REN-10 이 OPT-01 을 선행으로 두므로 사슬에서 OPT-01 이 REN-10 보다 앞이다 — 기존 선행 관계와 모순 없음. REN-07 과 OPT-01 은 순서 자유이고 뒤에 오는 쪽이 소유자 인자를 맞춘다.
- 같은 파일 동시 수술 금지 ② `DashMainWindow.{h,cpp}`: REN-02 · 04 · 07 · 10 · 12 는 열린 PR #654 #655 #652 #651 랜딩 뒤

### EXE — 실행 기반

> dev @ b08a91b3. 열린 PR 7건 중 머지 대상 6건(#651 #652 #654 #655 #656 #658 — #530 은 재업로드 노선이라 머지 대상이 아니다, C-2 ②⑩) 중 `controller/async/*` · `DashExtensionProcess` · `DashDaemonLifecycle` · `DashThreadAffinity` 를 만지는 것은 없다. `view/DashMainWindow.cpp` 는 #651 #652 #654 #655, `controller/DashManager.cpp` 는 #652 #654, `controller/DashMorphingService.h` 는 #654, `tests/CMakeLists.txt` 는 #651 #652 #654 #655, `controller/DashDoeBatchChain.{cpp,h}`·`tests/TestDoeBatchChain.cpp` 는 #654 #655, `controller/DashRwActor.cpp`·`controller/DashRwDocument.{cpp,h}`·`controller/DashRwDocumentHandle.h`·`tests/TestRwDocument.cpp`·`tests/rw/FakeRwModule.h` 는 #658(draft, Coupling 수용) 이 만진다. #656 은 EXE 항목과 겹치는 파일이 없다.
> 규모는 00-plan 1-3 파일 수 기준 — `S` 파일 3개 이하 · `M` 8개 이하. 공수가 작아도 파일이 4개 이상이면 M 으로 적는다 (검토 #11).
> 순서 골격: EXE-01(계약) → EXE-02(취소) → EXE-03(훅) → EXE-04(레인, 조건부). 표시·가드 축은 EXE-07(규약) → EXE-08 · EXE-09. 프로세스 축은 EXE-10(통지 규칙) → EXE-11 · EXE-12. RW 축은 EXE-14(실측·결정) → EXE-22(#458 적재 워커화, 조건부). 모듈 펌핑 제거(#454 #456 #457 #512 #513) 는 EXE-04 또는 EXE-01 의 "단일 슬롯 유지" 결정 뒤에 착수한다.
> Phase B 이관: #458 담당 RUN → EXE (EXE-22) · CON-U5 테스트 공백 → EXE-21 · MOR-c10 계측 → EXE-14 · CAD-c13/c31 → EXE-12 · ANA-c29 → EXE-03.
> C' 반영(2026-10-06): 215-2 4절 → EXE-01 · 7절 → EXE-07 (claims EXE-c61 · c62 신설) · EXE-12 종류 DEC → PR · EXE-14 종류 DEC → INV · EXE-09 바인더를 Widgets-free 로 재설계 · 좌표 정정(RW 액터 생성자 · readFeCondition · registry.load 전수) · 규모 5건 S → M. 항목 신설·삭제 없음(22건 유지).

#### EXE-01 · 실행 기반 계약 1종을 결정한다 — 레인(자원 키) · 재요청 정책 · 종료 경로 상한
- 종류: DEC | 규모: S | 태그: B · refactor
- 목표: DashAsyncJobRunner 의 "전역 단일 슬롯 · 거부" 를 유지할지, 215-2 3절·9절대로 자원 ID 별 레인(예: `PreprocessReader` · `AnalyzerCache` · `ModelRunnerScan`)으로 넓힐지 정한다. 레인을 두면 레인마다 재요청 처분(거부/대기)과 10절 큐 4정책(깊이·합치기·대기 취소·순서)의 미도입 사실을 함께 기록한다. 워커 기제 3종(DashAsyncJobRunner · DashMorphingService · DashDoeSampler 직접 QtConcurrent)의 병존 범위와 종료 경로 동기 대기 상한(drainAll · shutdownBlocking · MorphingService waitForDone)도 같은 기록에 넣는다.
- 완료 기준: 결정 기록 1건 — (1) 레인 목록 표(자원 → 키 → 재요청 처분) 또는 "단일 슬롯 유지" 선언 (2) #454 #456 #513 각 작업이 어느 레인에 제출하는지 1행씩 (3) 종료 대기 상한 표 3행 (4) 215-2 4절 "통지 출처 식별" 이 현행 수단으로 이미 충족된다는 1행 — 작업은 `QUuid`(`DashAsyncJobRunner.cpp:43`), 데몬 명령은 `commandId`(`currentCommandId()`), 완료 핸들러가 훅보다 먼저 `contexts_.take(jobId)` 로 자기 작업만 뺀다(`:52`). 레인을 도입해도 키가 `QUuid` 라 전제는 유지됨을 함께 적는다
- 변경 범위: 문서만 (docs/ThreadingContract.md 초안의 "실행 계약" 절 — EXE-05 가 파일을 만들면 거기에, 아니면 notes)
- 선행: -
- 충돌: B2 교집합: ThreadingContract.md → EXE-05 EXE-07
- 흡수: #451(공통 기반) · EXE-c01, c02, c03, c20, c61 · 215-2 2·3·4·9·10·13절
- 비고: #552 범위 밖 절이 "선점·예약·큐잉 안 함" 을 이미 고정했으므로 현실적 선택지는 "단일 슬롯 유지" 와 "자원별 단일 슬롯" 둘. 모듈 셋이 서로 반려하는 것이 수용 가능하면 전자가 가장 싸다. 모핑 서비스는 mesh-ops 스레드 예산과 결합돼 통합 대상에서 뺀다.

#### EXE-02 · DashAsyncJobContext 에 협조적 취소와 진행률 소스를 넣는다 (#552)
- 종류: PR | 규모: M | 태그: B · feature
- 목표: `QtConcurrent::run` 을 `QPromise<DashJobResult>&` 오버로드로 바꾸고 `Job::cancel()` 을 오버라이드해 `watcher_.future().cancel()` 로 잇는다. `DashAsyncJobRunner::cancel(QUuid)`·`cancelAll()` 을 공개하고 `main.cpp` 종료 경로를 `cancelAll() → drainAll()` 로 바꾼다. `onWorkFinished` 가 `isCanceled()` 를 먼저 보고 `State::Cancelled` 로 가게 해 빈 결과 읽기를 막는다. `QPromise::setProgressValue` 를 `Job::progressed(int)` 의 소스로 잇는다.
- 완료 기준:
  1. tests/TestAsyncJob.cpp 에 "cancel 중 작업은 Cancelled 로 끝나고 onSuccess/onFailure 가 돌지 않는다" · "cancelAll 뒤 drainAll 이 즉시 돌아온다" · "setProgressValue 가 progressed 를 낸다" 3건 추가·통과
  2. `git grep "취소는 없다" controller/async` 0건 · `git grep "소비자 없음" controller/async` 0건(`Job.h:37` 의 `progressed` 주석이 거짓이 되지 않게 함께 고친다) · `Job::cancel()` 기본 no-op 을 쓰는 Context 없음
  3. 대용량 XML 플롯 중 창 닫기에서 종료 지연이 "현재 work 종료까지" 에서 "협조 지점까지" 로 줄어듦(실측 기록) — SDK 내부 파싱은 안 끊기는 한계를 PR 본문에 명시
- 변경 범위: controller/async/Job.h(`progressed` 주석 1줄 — "소비자 없음 — W6-x 후속 예정" 삭제) · controller/async/DashAsyncJobContext.h · DashAsyncJobContext.cpp · DashAsyncJobRunner.h · DashAsyncJobRunner.cpp · main.cpp · tests/TestAsyncJob.cpp
- 선행: -
- 충돌: EXE-03 · EXE-05 (같은 async 파일) — EXE-02 를 먼저 랜딩한다 (#553 본문의 순서) · B2 교집합: main.cpp → DEV-21 DEV-24 EXE-06 PRJ-06 PRJ-14 UIC-05 UIC-26 · DashAsyncJobRunner.cpp → EXE-04 · DashAsyncJobRunner.h → EXE-04 EXE-08 · TestAsyncJob.cpp → EXE-04 EXE-09 · DashAsyncJobContext.h → EXE-04
- 흡수: #552 · #543(취소 표면의 전제) · EXE-c12, c13, c20(drainAll 부분)
- 비고: 취소는 협조적이다 — 첫 소비자 `DashDataLoader::prefetchXml` 은 안 끊긴다. 이 사실을 PR 과 헤더 주석에 적지 않으면 "취소가 안 된다" 가 버그로 올라온다. 선점(도는 작업 취소 후 새 것 시작)은 범위 밖.

#### EXE-03 · DashAsyncJobRunner::run 을 준비·실행·완료 훅 구조체로 바꾸고 Job::State 에 Skipped·Aborted 를 더한다 (#553)
- 종류: PR | 규모: M | 태그: B, E · refactor
- 목표: `run(work, onSuccess, onFailure)` → `run(DashAsyncJobHooks{preExecution, execution, postExecution})`. `preExecution`(GUI, `DashJobPreparation {Proceed, SkipExecution, Abort}` 반환) 은 `run()` 안 인라인으로 돌되 execution 과 같은 예외 정규화를 건다. `postExecution(Job::State, const QString&)` 은 어떤 종결에도 반드시 1회 불린다(취소 포함). `Job::State` 에 `Skipped`·`Aborted` 를 추가하고 `setState` 터미널 락에 넣는다. 유일 호출부 `DashResultsAnalyzerWidget::onPlotSpecReady` 의 동기 분기를 `SkipExecution` 한 줄로 옮겨 호출 갈래를 하나로 만든다.
- 완료 기준:
  1. `git grep -n "run(" controller/async/DashAsyncJobRunner.h` 가 훅 구조체 시그니처 1개만 보임 · 위치 인자 3개 오버로드 없음
  2. tests/TestAsyncJob.cpp — "pre 가 SkipExecution 이면 execution 없이 post 가 Skipped 를 받는다" · "pre 가 Abort 면 Aborted" · "pre 가 던지면 Aborted 로 정규화되고 슬롯이 풀린다" · "cancel 뒤 post 가 Cancelled 로 1회" 4건 추가·통과. tests/TestJobState.cpp 에 Skipped/Aborted 터미널 락 1건
  3. `DashResultsAnalyzerWidget::onPlotSpecReady` 에 `DashPlotRequestHandler::build` 호출이 1곳(post 안) — 동기 경로 조기 반환 블록 소멸
- 변경 범위: controller/async/Job.h · DashAsyncJobContext.h · DashAsyncJobContext.cpp · DashAsyncJobRunner.h · DashAsyncJobRunner.cpp · view/DashResultsAnalyzerWidget.cpp · tests/TestAsyncJob.cpp · tests/TestJobState.cpp
- 선행: EXE-02
- 충돌: EXE-04 · EXE-05 · EXE-08 (DashAsyncJobRunner.h) · ANA 의 DashResultsAnalyzerWidget.cpp 항목 · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · TestAsyncJob.cpp → EXE-09
- 흡수: #553 · EXE-c14, c15, c53 · ANA-c29 · EXE-c60 (호출부 — ANA 이관)
- 비고: 훅 간 데이터는 캡처로만(값 또는 `shared_ptr<페이로드>`, QObject·VTK 금지; GUI 객체는 `QPointer`) — 템플릿 체이닝·슬롯별 래퍼 금지(#553 "안 하는 것"). `Job::State::Skipped` 는 실패가 아니라는 주석을 enum 에 적고 ProcessJob 에는 도입하지 않는다 — 도입 시 `== Succeeded` 소비자 6곳을 함께 본다. 파일 8개지만 순변경 ~150줄.

#### EXE-04 · DashAsyncJobRunner 를 자원 키별 레인으로 확장한다 (EXE-01 조건부)
- 종류: PR | 규모: M | 태그: B · feature
- 목표: EXE-01 이 레인을 택했을 때 — `run(hooks, DashJobLane lane)` 으로 레인 키를 받고 `contexts_` 를 레인별 단일 슬롯으로 바꾼다. `anyRunning()`·`isRunning()` 에 레인 인자를 더하고 UI 차단 훅은 "어느 레인이든 1개 이상 실행 중" 으로 집계한다. `cancelAll()`·`drainAll()` 은 전 레인.
- 완료 기준:
  1. tests/TestAsyncJob.cpp — "다른 레인은 동시에 돈다" · "같은 레인은 반려" · "두 레인 중 하나가 끝나도 다른 레인이 남아 있으면 UI 차단이 유지된다" 3건 추가·통과
  2. 기존 14건 테스트 무변경 통과 (기본 레인 = 종전 단일 슬롯)
- 변경 범위: controller/async/DashAsyncJobRunner.h · DashAsyncJobRunner.cpp · DashAsyncJobContext.h · tests/TestAsyncJob.cpp · view/DashResultsAnalyzerWidget.cpp (레인 지정)
- 선행: EXE-01, EXE-03
- 충돌: EXE-08 (DashAsyncJobRunner.h 훅 시그니처) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · DashAsyncJobRunner.cpp → EXE-02 EXE-05 · DashAsyncJobRunner.h → EXE-02 · TestAsyncJob.cpp → EXE-02 EXE-09 · DashAsyncJobContext.h → EXE-02
- 흡수: #451(공통 기반 "직렬 실행 풀") · EXE-c03 · 접점 #454 #456 #513 의 선행
- 비고: EXE-01 이 "단일 슬롯 유지" 로 결정하면 이 항목은 CLOSE. 레인은 `QThreadPool` 을 늘리는 것이 아니라 슬롯 집계를 키로 나누는 것 — 전역 풀 그대로.

#### EXE-05 · 메인 스레드 게이트를 DASH_ASSERT_MAIN_THREAD 로 통일하고 docs/ThreadingContract.md 를 쓴다
- 종류: PR | 규모: M | 태그: B, E · refactor, docs
- 목표: 수제 `QThread::currentThread() == qApp->thread()` assert 5곳(DashAsyncJobContext 3 · DashAsyncJobRunner::run · **DashRwActor 생성자** `DashRwActor::DashRwActor()` 의 `:98` — `instance()`(:88-91) 는 Meyers 싱글턴 2줄이라 assert 가 없다) 을 `DASH_ASSERT_MAIN_THREAD("…")` 로 바꾼다(소유 스레드 검사 2곳 `assertActorThread`·`assertServiceThread` 는 의미가 달라 유지). 헤더가 정본으로 가리키는 `docs/ThreadingContract.md` 를 만든다 — 훅 스레드 고정(pre/post=GUI, execution=워커), 캡처 규약, 워커 금지 목록(위젯·VTK 렌더 객체·GUI 전용 싱글턴), LEAF RULE 과 교착 방지(blocking invoke 소유자는 호출자를 역호출하지 않는다), 203-2 D5 타입 화이트리스트, 215-2 Q12 의 대기 3계급(소멸자 암묵 대기·blocking 마샬링·join) 검사 목록.
- 완료 기준:
  1. `git grep -nE "currentThread\(\) == (qApp|QCoreApplication::instance\(\)|app)->thread\(\)" -- '*.cpp' '*.h' ':!controller/DashThreadAffinity.h' ':!view/common/DashNotify.cpp' ':!tests/*'` 0건
  2. docs/ThreadingContract.md 존재 · docs/index.md 에 링크 · 위 6개 절 각 1개 이상 규칙
  3. 전체 테스트 통과(동작 불변)
- 변경 범위: controller/async/DashAsyncJobContext.cpp · controller/async/DashAsyncJobRunner.cpp · controller/DashRwActor.cpp · docs/ThreadingContract.md(신규) · docs/index.md
- 선행: -
- 충돌: EXE-02 · EXE-03 (같은 async .cpp) — 둘 뒤에 랜딩하는 편이 충돌이 작다 · B2 교집합: DashAsyncJobRunner.cpp → EXE-04 · ThreadingContract.md → EXE-01 EXE-07 · index.md → DEV-12 DEV-13 · DashRwActor.cpp → EXE-22 · PR #658(DashRwActor.cpp)
- 흡수: #451(공통 기반 "메인 스레드 게이트 확산" · 구 #452) · EXE-c05, c06 · 203-2 D5 · 215-2 12절·다음 단계 3번 · EXE-c41(규칙 몫)
- 비고: `DashNotify.cpp:23` 의 스레드 검사는 "GUI 가 아니면 큐잉" 분기라 assert 대상이 아니다. EXE-01 결정 기록의 자리이기도 하다.

#### EXE-06 · 싱글톤 lazy-init 을 메인 스레드 선-초기화와 생성자 가드로 고정한다 (203-2 D1)
- 종류: PR | 규모: S | 태그: B · refactor
- 목표: `main.cpp` 에서 QApplication 생성 직후 `DashManager::Mgr()`·`DashProjectManager::Instance()` 를 1회 선호출하고, 두 생성자에 `DASH_ASSERT_MAIN_THREAD` 를 둔다. 워커가 첫 호출자가 되는 경로를 구조적으로 막는다(203-2 처방 A). magic static 전환(처방 B)은 `atexit(Destroy)` 정리와 얽혀 범위 밖.
- 완료 기준:
  1. main.cpp 에 두 선호출 존재 (`app` 생성과 `DashMainWindow` 생성 사이)
  2. DashManager · DashProjectManager 생성자에 `DASH_ASSERT_MAIN_THREAD` 1줄씩
  3. 앱 기동·종료 회귀 없음
- 변경 범위: main.cpp · controller/DashManager.cpp · controller/DashProjectManager.cpp
- 선행: -
- 충돌: PR #652 · #654 (controller/DashManager.cpp) · PRJ 의 DashManager 항목 · B2 교집합: DashManager.cpp → CAD-03 CAD-06 DOE-19 PRJ-03 PRJ-04 PRJ-06 PRJ-14 REN-07 · DashProjectManager.cpp → PRJ-08 PRJ-12 PRJ-13 PRJ-19 PRJ-35 PRJ-36 REN-10 · main.cpp → DEV-21 DEV-24 EXE-02 PRJ-06 PRJ-14 UIC-05 UIC-26
- 흡수: 203-2 D1 · EXE-c07
- 비고: DashProjectManager 는 소멸 경로가 없다(비대칭) — 고치지 않는다, PRJ 에 메모만 남긴다.

#### EXE-07 · 진행 표시·차단·반려 안내 규약 1종을 정한다 (#462 · #543 결정 축)
- 종류: DEC | 규모: S | 태그: B, D · docs
- 목표: Job 상태 → 화면 매핑 1종 — `Running(진행률 없음)` = 상태바 무한 진행바 + 문구, `Running(진행률 있음)` = 결정 진행바, `Cancelled/Failed` = 통지 규칙(EXE-10) 으로 위임. 차단 범위(최상단 전체 vs 콘텐츠만 — DashTitleBar·QSizeGrip 제외 여부), 반려 안내(비모달 상태바 문구 vs 침묵), `setUIEnabled`+`showLoadingIndicator` 짝과의 관계(통합/용도 분리), 취소 버튼의 자리(상태바 진행바 옆), 모달 여부를 결정한다. 현행 6방식(EXE-c21) 의 처분(수렴/존치)을 표로 남긴다. 215-2 7절 "상태 writer 단일화" 의 횡단 조항도 여기에 둔다 — **진행 표시·버튼 활성의 근거는 Job/프로세스 상태이고 외부 도구가 쓰는 상태 파일 폴링에 묶지 않는다**, 상태 항목마다 writer 1명, 늦은 쓰기 우선순위는 "종결 고정"(터미널 락과 같은 규칙).
- 완료 기준: 결정 기록 1건 — (1) 상태 → 표시 매핑 표 (2) 차단 대상 목록 (3) 6방식 처분 표 (4) 반려 안내 형태 (5) 상태 writer 조항 1항 + 현행 위반 사례 2행(BLD 1Hz status 폴링 EXE-c37 · 설정 JSON RMW EXE-c41) — 수정은 각 모듈
- 변경 범위: 문서만 (docs/ThreadingContract.md 의 "표면" 절 또는 별도 docs)
- 선행: EXE-01 (취소·재요청 정책이 표면을 정한다)
- 충돌: B2 교집합: ThreadingContract.md → EXE-05
- 흡수: #462 · #543(결정 4축) · EXE-c16, c17, c18, c19, c21, c62 · 215-2 7·11절 · OPT-D13(표준 몫)
- 비고: 저비용 선행 — #463 확산과 EXE-08·09 가 이 규약을 소비한다. 프레임리스 창(`DashMainWindow.cpp:172`) 이라 "창 이동을 살린다" 는 결정은 곧 DashTitleBar·QSizeGrip 을 차단 목록에서 빼는 결정이다.

#### EXE-08 · 비동기 작업의 차단·진행 표시를 규약대로 고친다 (#543 구현)
- 종류: PR | 규모: M | 태그: B, D · feature
- 목표: EXE-07 결정대로 — `setUiBlockHooks` 의 차단 대상을 규약 목록으로 바꾸고(타이틀바·사이즈그립 제외가 결정이면 `DashTitleBar`·`QSizeGrip` 을 건너뜀), 상태바 진행바에 작업 문구(훅 구조체의 label) 와 `Job::progressed` 진행률을 싣고, 반려 시 상태바 안내 1줄, 취소 버튼을 `DashAsyncJobRunner::cancel` 에 잇는다. `TODO(#543)` 를 지운다.
- 완료 기준:
  1. `git grep "TODO(#543)"` 0건
  2. 대용량 XML 플롯 중 창 이동·리사이즈 가능(결정이 "살린다" 일 때) · 상태바에 문구 표시 · 취소 클릭 시 `Cancelled` 로 종결되고 UI 복구
  3. tests/TestAsyncJob.cpp `uiBlockHooksWrapJobLifecycle` 통과 + 반려 안내 훅 1건 추가
- 변경 범위: view/DashMainWindow.h · view/DashMainWindow.cpp · controller/async/DashAsyncJobRunner.h (훅 시그니처에 문구·진행률) · view/DashResultsAnalyzerWidget.cpp (문구 지정)
- 선행: EXE-02 (취소) · EXE-03 (훅 구조체) · EXE-07 (규약)
- 충돌: PR #651 · #652 · #654 · #655 (view/DashMainWindow.cpp — #655 는 +1/-10) · EXE-04 (DashAsyncJobRunner.h) · PRJ/UIC 의 DashMainWindow 항목 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · DashMainWindow.h → 공유 11건(deps.md 5절)
- 흡수: #543 · EXE-c16, c17, c18
- 비고: `setUIEnabled` 계열 통합이 결정되면 범위가 M 으로 커진다 — 그 경우 통합은 별 항목으로 쪼갠다(PRJ 접점).

#### EXE-09 · 실행 중 재클릭 가드 표준을 헬퍼로 제공하고 기준 적용 1곳을 바꾼다 (#461)
- 종류: PR | 규모: M | 태그: B, D · feature
- 목표: 바인더를 **층별로 두 조각**으로 나눈다 — (a) `controller/async/DashJobGuard.{h,cpp}`: `Job`(또는 `isRunning` 을 내는 러너) 의 시작·종결에 맞춰 `std::function<void(bool enabled)>` 싱크를 부르고, 실행 중 재진입 요청을 거부 로그 + 안내 훅(`std::function<void(const QString&)>`, EXE-07 규약) 으로 번역한다. QtWidgets 를 들이지 않는다 — `controller/async/DashAsyncJobRunner.h:7` 이 그 층의 의존을 "Qt + Job.h + 로거까지" 로 선언하고 테스트 타깃 `test_async_job` 이 Core·Concurrent·Test 만 링크한다(`tests/CMakeLists.txt:54-60`). (b) `view/common/DashJobGuardWidgets.h`: `QAbstractButton*` 목록을 (a) 의 싱크로 접어주는 인라인 편의 오버로드. 표준 문장(버튼 비활성 + 모델 가드 + 거부 로그 + 안내)을 ThreadingContract 또는 통지 규칙 문서에 적는다. 기준 적용은 EXE 소유 러너 `DashTopOptPostprocessRunner` ↔ `TopOptPostprocessDialog`(현행: `QMessageBox::warning("Busy")` + 러너 WARN 로그, 버튼 열림).
- 완료 기준:
  1. tests/TestAsyncJob.cpp (Core·Concurrent·Test 하네스 그대로) — "Running 동안 싱크가 `false`, 종결(성공·실패·취소) 후 `true` 로 1회씩 불린다" · "실행 중 재요청은 거부되고 안내 훅이 1회 불린다" 2건. 버튼 비활성은 (b) 가 싱크를 호출하는 한 줄이라 자동 테스트 대상이 아니다 — 2번의 수동 확인으로 덮는다
  2. TopOptPostprocessDialog 의 실행 버튼이 `isRunning()` 동안 비활성 · `QMessageBox::warning(this, "Busy", …)` 삭제 (수동 시나리오 1건을 PR 본문에)
  3. 모듈 확산(#463) 이 이 헬퍼만 쓰면 되도록 (a) 의 공개 API 가 Job 과 러너 둘 다 받고, (b) 가 위젯 목록을 받음
- 변경 범위: controller/async/DashJobGuard.h(신규) · DashJobGuard.cpp(신규) · view/common/DashJobGuardWidgets.h(신규) · view/dialog/TopOptPostprocessDialog.cpp · tests/TestAsyncJob.cpp · tests/CMakeLists.txt (`test_async_job` 소스에 `DashJobGuard.cpp` 추가 — Widgets 링크는 늘리지 않는다)
- 선행: EXE-07
- 충돌: OPT/PRJ 의 TopOptPostprocessDialog 항목 · #455 (같은 파일의 processEvents 6곳) · B2 교집합: tests/CMakeLists.txt → 공유 12건(deps.md 5절) · TestAsyncJob.cpp → EXE-02 EXE-03 EXE-04 · TopOptPostprocessDialog.cpp → DEV-20 PRJ-26 REN-07 · PR #655(tests/CMakeLists.txt) · PR #654(tests/CMakeLists.txt) · PR #652(tests/CMakeLists.txt) · PR #651(tests/CMakeLists.txt)
- 흡수: #461 · EXE-c22 · OPT-D13(표준 몫) · DOE-D11(표준 몫)
- 비고: #315(Load 재클릭)·#221(모듈 진입 상태) 은 비범위(#461 not-to-be). 모듈별 적용은 #463 → 각 모듈 항목. 층을 가르는 이유는 테스트 하네스다 — `tests/CMakeLists.txt` 에서 Widgets 를 무조건 링크하는 타깃은 `test_analyzer_utils_cache`(:324-333) 하나이고 나머지 2개(`test_result_processor`·`test_real_result_files`)는 Preprocessor·VTK 가 있을 때만 켜진다. 바인더가 `QAbstractButton` 을 직접 받으면 `test_async_job` 에 Widgets 를 새로 들여야 하고, 그러면 그 파일이 지키는 "Qt Core + Test only" 성질(:388-394 주석)이 깨진다.

#### EXE-10 · 외부 프로세스 실패 통지 규칙을 세운다 (#466 · #482 와 문서 공유)
- 종류: DEC | 규모: S | 태그: B, D · docs
- 목표: 규칙 — (1) 실행층 종결(`Job::finished` Failed/Cancelled · `commandFailed` · `died`) 은 소비 모델이 도메인 시그널로 번역하고 **뷰가 반드시 구독한다** (connect 0 금지 — OPT-D11 류를 리뷰 게이트로 막는다) (2) 수단: 사용자 행위의 실패 = `DashNotify::error/warning`(모달), 배경 작업·배치 케이스 = 상태 열/상태바(비모달), 취소 = 통지 없음 (3) 메시지 포맷: 실행층 사유 문자열(현행 한글 리터럴 "종료 코드 %1" 등) 은 로그용이고 사용자 문구는 소비자가 만든다 (4) 리뷰 체크리스트 3줄. #482 와 같은 문서를 쓴다 — 먼저 착수하는 쪽이 만든다.
- 완료 기준: 결정 기록 1건 — 규칙 4항 + 체크리스트 · 현행 미결합 목록(OPT-D11 외 `*Failed` 시그널 중 view connect 0건) 1표
- 변경 범위: 문서만
- 선행: -
- 충돌: UIC-16 (#482 — 같은 문서)
- 흡수: #466 · EXE-c24, c54 · OPT-D11(규칙 몫) · 215-2 6절
- 비고: 개별 수정(#323 #324 #393 #394, OPT-D11) 은 각 소유 이슈·모듈. 실행층의 "무음 폐기 금지" 는 이미 구현·테스트돼 있다(TestProcessRuntime `missingDaemonExeFailsQueuedCommand` · `readyTimeoutFailsQueuedCommands` 등) — 규칙은 소비자 층을 겨냥한다.

#### EXE-11 · 데몬 명령 응답 타임아웃을 무활동 기반으로 넣는다 (#467)
- 종류: PR | 규모: M | 태그: B · bug
- 목표: `DashExtensionProcess` 에 명령 진행 중 stdout 무활동 상한(`setCommandInactivityTimeoutMs`, 기본값은 결정 필요 — 후보 10분) 을 두고, 만료 시 진행 명령을 `commandFailed("no output for N ms")` 로 마감한 뒤 `stop()` 경유로 데몬을 세운다(stop 5s → kill 승격은 기존). 타이머 수명은 `m_waitingFinished` 구간과 같게 `setState`/`trySendNext`/`handleDaemonLine` 에 묶는다. 기동 타임아웃(30s/NX 120s)·정지 타임아웃(5s) 은 이미 있어 손대지 않는다.
- 완료 기준:
  1. tests/TestProcessRuntime.cpp — daemon_stub 에 "명령 받고 침묵" 모드 추가, "무활동 만료 시 commandFailed 1회 + stopped" · "출력이 이어지면 만료 안 함" 2건 통과
  2. 기존 24건 통과(기본값이 충분히 커서 스텁 시나리오에 영향 없음)
  3. 통지 문구가 EXE-10 규칙을 따름 — 만료 사유가 소비자 도메인 시그널로 도달(ModelRunner·ModelBuilderMCU·NX 각 1회 수동 확인)
- 변경 범위: controller/DashExtensionProcess.h · DashExtensionProcess.cpp · tests/TestProcessRuntime.cpp · tests/daemon_stub.cpp
- 선행: EXE-10
- 충돌: EXE-12 (DashExtensionProcess.h 주석) · LCH 의 STP watchdog(`kStpCaseTimeoutMs` 600s) 항목 — 중복 상한이 되므로 LCH 가 자기 watchdog 유지 여부를 판정 · B2 교집합: DashExtensionProcess.h → LCH-10 LCH-31 · TestProcessRuntime.cpp → CAD-15 · DashExtensionProcess.cpp → CAD-15 · daemon_stub.cpp → CAD-15
- 흡수: #467 · EXE-c25, c26(해소분 기록), c32(비고)
- 비고: 고정 상한은 부적합 — MCU 학습은 수십 분, NX load 는 수 분이고 길이가 가변이라 "응답이 없다" 는 "출력이 없다" 로 정의한다. 진행 중 아무것도 안 찍는 명령이 있으면 그 데몬의 EXT 작업(heartbeat 라인)이 선행. `killOrphans` 의 동기 3s 는 수용(재기동 전용) — 손대지 않는다.

#### EXE-12 · 데몬 stdout 프로토콜 계약을 명문화한다 (CAD-U4)
- 종류: PR | 규모: S | 태그: B, E · docs
- 목표: `[READY]`(기동 1회) · `[FINISHED]`(명령 성공, 전체 일치) · `[ERROR] <msg>`(명령 실패, 부분 일치) · 비정상 종료 = 진행·대기 명령 전부 실패 · `commandId` 에코 — 를 계약으로 적고 두 조항을 더한다: (1) 실패는 반드시 `[ERROR]` 또는 비정상 종료로 표면화한다 — 둘 다 없으면 성공으로 마감되는 현행 동작을 계약으로 고정하고 데몬 측 의무로 돌린다 (2) 산출물 flush·닫기가 `[FINISHED]` 보다 앞선다(RUN-D27 류 예방) (3) 진행 중 명령의 취소는 프로토콜에 없다 — 대기 명령은 `dropQueuedCommands`, 진행 중은 `stop()` 승격뿐(현행 고정, #249 범위 밖 절의 per-command cancel 은 데몬 측 cancel 명령이 생기기 전에는 불가). GUI 측 산출물은 `DashExtensionProcess.h` 헤더 주석 + docs, 테스트 "ERROR 없는 실패는 성공으로 마감된다(계약 고정)" 1건. 데몬 측 준수는 EXT(DashOpti_Registry 의 JournalLauncher·MCU·SensitivityEngine·NX CAD).
- 완료 기준: (1) 계약 본문 3항이 `DashExtensionProcess.h` 헤더 주석 + docs 에 적힘 (2) tests/TestProcessRuntime.cpp 에 "`[ERROR]` 없이 정상 종료한 실패 명령은 성공으로 마감된다(계약 고정)" 1건 추가·통과 (3) EXT 추적 행 — 데몬 4종(JournalLauncher·MCU·SensitivityEngine·NX CAD) 준수 여부 표
- 변경 범위: controller/DashExtensionProcess.h(주석) · docs · tests/TestProcessRuntime.cpp
- 선행: -
- 충돌: EXE-11 (같은 헤더 주석) · B2 교집합: DashExtensionProcess.h → LCH-10 LCH-31 · TestProcessRuntime.cpp → CAD-15
- 흡수: CAD-U4 · CAD-c31(CAD 가 EXE 로 넘김) · EXE-c29, c57 · RUN-D27(계약 몫) · #249(범위 밖 절 — 명령 취소) · CAD-c13 · EXE-c56(해소 기록)
- 비고: 종류가 `PR` 인 이유 — 산출물에 헤더 주석과 테스트 1건이 있어 00-plan 1-2 의 `DEC`("산출물은 기록된 결정") 와 맞지 않는다(검토 #4). 계약 본문(문서)과 "계약 고정 테스트 + 헤더 주석"으로 2분할하는 안은 **기각** — 개념이 "데몬 stdout 계약" 하나이고, 테스트는 그 계약의 현행 동작을 못 박는 같은 덩어리다(00-plan 1-2 개념적 응집). EXT 가 실제 변경의 대부분 — GUI 는 계약을 쓰고 지키는지 검사할 뿐. 준수 표의 NX CAD 행은 CAD-10 을 **참조만** 한다 — CAD-D14(표현식 적용 실패를 삼킴) 의 실작업은 CAD-10 단일이고 본 항목 흡수 목록에서 뺐다(Phase B 중복 기록 병합 이행). 215-2 Q5 "status 를 stdout 계약으로" 도 같은 계약 문서의 후속 절.

#### EXE-13 · 고아 프로세스 재시작 조정과 취소 완료 정의를 정한다 (215-2 5·8절)
- 종류: DEC | 규모: S | 태그: B, A · docs
- 목표: (1) 크래시·강제 종료로 남는 자식 트리의 처분 — 예방(Job Object `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, "GUI 를 닫으면 실행이 죽는다" 고정) vs 사후(시작 시 PID·생성 시각·이미지 경로 기록 + 재기동 시 생존 확인 + 묻기) 중 선택 (2) 취소 완료의 정의 — 현행 "kill 신호 발신 = Cancelled 종결" 유지 vs 사망 관측 후 종결. 유지라면 "다음 실행 가드가 풀린 뒤 파일 핸들이 남는 창" 을 수용 사실로 기록한다 (3) append-only 실행 기록(started/finished) 도입 여부.
- 완료 기준: 결정 기록 1건 — 3항 각 선택과 사유 · 선택에 따른 후속 PR 후보 1~2개(예: Job Object 래퍼 `controller/async/ProcessJobObject` S)
- 변경 범위: 문서만
- 선행: EXE-01
- 충돌: -
- 흡수: EXE-c30, c31 · 215-2 5·8절 · Q6 · Q13~Q16 · 다음 단계 4번
- 비고: 215-2 가 "소유 티켓 없음" 으로 남긴 유일한 꼭지. 예방(Job Object) 이 가장 싸고(탐지·판정·처분 3단계 소멸) 정책 비용만 든다. `killOrphans` 의 "이전 세션 고아 미회수" 수용은 이 결정으로 대체된다.

#### EXE-14 · RW 액터의 GUI 점유를 실측하고 스레드 소유(Stage 2) 를 결정한다
- 종류: INV | 규모: S | 태그: B, E · docs
- 목표: `DashRwActor` 가 GUI 스레드에 전 인스턴스를 감금(Stage 1)한 상태에서, 워커가 RW 를 쓰는 길이 `invokeOnActor` 의 blocking 마샬링(GUI 로 되돌아옴)뿐이다. 선택지 — (a) 유지: RW 작업은 GUI 에 두고 긴 것만 다른 수단(외부 프로세스·QCoro 분할)으로 (b) 단일 액터 스레드: 전 인스턴스를 전용 스레드로, GUI 호출은 blocking 마샬링(교착 방지 = LEAF RULE) (c) per-instance 어피니티: 배치 클론은 워커, 표시 문서는 GUI. 대상 소비자: CON 의 동기 액터 호출(CON-D11 왕복), DOE 배치 체인(`DashDoeBatchChain` QCoro 가 GUI 에서 RW 편집·export), #281 의 전용 세션.
- 완료 기준:
  1. **실측 결과 1표** (선행) — 대형 deck 적재 · DOE 배치 체인 · 모핑 배치가 `invokeOnActor` 로 GUI 에 되돌리는 구간의 GUI 점유 시간(로그 타임스탬프, 경로별 최소·중위·최대). EXE-c55 판정이 `미확인` 이라 이 수치가 결정의 유일한 입력이다 (#281 Follow-up ⑵)
  2. 실측 뒤 결정 기록 1건 — (a)/(b)/(c) 중 선택과 사유 · 소비자 3종(CON · LCH 배치 · MOR #281) 각각에 미치는 영향 1행
  3. 선택이 (b)/(c) 면 후속 PR(EXE-22) 범위와 테스트(TestRwActor 에 스레드 확인 케이스) 명시 · (a) 면 EXE-22 를 CLOSE 로 내리고 #458 을 "GUI 스레드 유지 + 진행 표시(EXE-07)" 로 재정의
- 변경 범위: 문서만 (계측은 로그 타임스탬프 — 코드 변경 없음)
- 선행: EXE-01
- 충돌: -
- 흡수: EXE-c11 · #451 비범위 판정("CON 의 동기 액터 호출은 공통 기반 후속") · 215-2 Q3·Q10 · 접점 #281(EXE 몫) · #281-FU2(계측) · MOR-c10 · EXE-c55 · #458-a 의 선행(EXE-c59)
- 비고: 종류가 `INV` 인 이유 — 실측이 결정의 선행이고 결과에 따라 후속 PR(EXE-22)이 생기거나 CLOSE 되는 구조가 00-plan 1-2 의 INV 정의와 같다(검토 #5). 개념은 하나(액터 스레드 소유)라 분할하지 않는다. Preprocess(#454) 는 `IPreprocessorWrapper`(외부 Preprocessor) 경로라 이 결정과 무관 — 기다리지 않는다. DashRwActor.h:30-37 의 roadmap 주석이 (c) 를 가리킨다. #458(적재 워커화)이 이 결정의 첫 소비자.

#### EXE-15 · #463 모듈별 진행바·취소 버튼 확산 — 모듈 항목으로 분산하고 닫는다
- 종류: CLOSE | 규모: S | 태그: B, D · feature
- 목표: 확산은 모듈 작업이다. EXE 는 규약(EXE-07)·헬퍼(EXE-09)·취소(EXE-02)·진행률(EXE-02) 을 제공하고, 적용은 각 모듈 항목이 흡수한다.
- 완료 기준: 닫기 사유 — "규약·헬퍼는 EXE-07/09, 적용은 8모듈 항목이 흡수했다. `05-final/mapping.md` 의 `#463` 행이 그 증거 — MOR-01 · CAD-07 · **LCH-28** · PRE-23 · BLD-10 · RUN-05 · RUN-25 · ANA-22 · OPT-05 · OPT-22." 흡수 확인이 끝났으므로 지금 닫는다.
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #463 · EXE-c23
- 비고: 선행을 `-` 로 둔 이유 — 닫기 조건은 "8모듈이 `#463` 을 흡수했는가" 뿐이고 이미 충족됐다. EXE-07(규약)·EXE-09(헬퍼) 완성은 각 모듈 적용 항목의 선행이지 이 CLOSE 의 선행이 아니다(검토 #12). LCH 적용처는 LCH-28 이다 — `#456` 은 LCH 가 해소됨(LCH-20)으로 판정했다.

#### EXE-16 · #468 외부 프로세스 호출부 널 가드 — 해소됨으로 닫는다
- 종류: CLOSE | 규모: S | 태그: B · bug
- 목표: 실행층(ProcessJob · DashExtensionProcess) 은 슬롯·루프마다 프로세스 포인터를 재검사하고, 소비자 측 Job 포인터(`m_currentJob`·`m_fitJob`) 는 사용 전 전부 검사한다. 데몬 getter 는 DashManager 생성자가 상시 생성해 널이 될 수 없다.
- 완료 기준: 닫기 사유 — EXE-c27 좌표(실행층 9곳 · 소비자 6곳 · 생성 보장 `controller/DashManager.cpp:85-98`). 검사 없이 쓰는 4곳(DashModelBuilderMCU.cpp:42 · DashModelRunner.cpp:232·266·366) 은 생성 보장 아래 무해 — 기계적 추가는 하지 않는다.
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #468 · EXE-c27
- 비고: 직접 QProcess 를 쓰는 dfsxml 보존 경로(`m_motionProcesses`) 도 `if (proc)` 가드가 있다.

#### EXE-17 · #469 프로세스 인자·출력 인코딩 UTF-8 통일 — 본선 완료로 닫는다
- 종류: CLOSE | 규모: S | 태그: B · bug
- 목표: 본선(ProcessJob · DashExtensionProcess) 은 `PYTHONIOENCODING=utf-8`·`PYTHONUTF8=1` 주입 + LineAssembler 완성 라인 단위 `fromUtf8` + 데몬 명령 `toUtf8` 로 일원화돼 있고 테스트(`decodesUtf8SplitAcrossChunks` · TestLineAssembler `utf8SplitAcrossChunks`)가 고정한다. 인자는 `QProcess::start(exe, QStringList)` 라 Windows 에서 UTF-16 으로 전달된다.
- 완료 기준: 닫기 사유 — EXE-c28. 잔여 `fromLocal8Bit` 5곳(model/DashJobRunnerAnsysMotion.cpp:186·190·197·230·416) 은 #451 이 "격리만 하고 수정하지 않는다" 로 정한 dfsxml 보존 경로 — LCH 대응표에 보존 사실로 기록
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #469 · EXE-c28
- 비고: dfsxml 경로가 #458 로 ProcessJob 에 수렴하면 잔여도 자동 해소된다.

#### EXE-18 · #451 GUI 스레드 동기 실행과 이벤트 펌핑 제거 — 추적 부모를 닫는다
- 종류: CLOSE | 규모: S | 태그: B · refactor
- 목표: 공통 기반 몫은 EXE-01(계약) · EXE-04(레인) · EXE-05(게이트·문서) · EXE-06(싱글톤), 모듈 몫은 #454 #455 #456 #457 #512 #513 이 흡수한다.
- 완료 기준: 닫기 사유 — 서브 6건 열림 상태 유지, 본문의 "WorkerJob·ThreadPools·MorphingGate·ThreadingContract 부재" 전제는 EXE-c01 로 갱신(워커 단위는 #544 로 존재). processEvents 전수는 02-claims/EXE.md "processEvents 전수" 절(55 히트 · 49 호출).
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #451 · EXE-c49, c04
- 비고: MorphingGate 는 #281(MOR, In progress) 소관.

#### EXE-19 · #460 실행 진행 표시·취소·중복 실행 가드의 표준화 — 추적 부모를 닫는다
- 종류: CLOSE | 규모: S | 태그: B, D · feature
- 목표: #461 → EXE-09, #462 → EXE-07, #463 → EXE-15(모듈 분산), #464 → CAD.
- 완료 기준: 닫기 사유 — 위 대응. 취소는 EXE-02, 진행률 소스는 EXE-02, 표면은 EXE-08.
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #460 · EXE-c50
- 비고: -

#### EXE-20 · #465 외부 프로세스 안전핀 일괄 — 추적 부모를 닫는다
- 종류: CLOSE | 규모: S | 태그: B · bug
- 목표: #466 → EXE-10, #467 → EXE-11, #468 → EXE-16(해소), #469 → EXE-17(해소). 자식 프로세스 정리(#207) 는 Done. cae-launcher(ANSYS·Abaqus·fe-safe) 쪽 안전핀은 외부 저장소(EXE-c45).
- 완료 기준: 닫기 사유 — 위 대응 + 추가 발견 2건(프로토콜 계약 EXE-12 · 고아 재시작 EXE-13) 이 새 항목으로 등재됨.
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #465 · EXE-c51, c45
- 비고: -

#### EXE-21 · DashRwDocument 엔트리 분해 테스트를 flat 필드·요약 행·DV 종류 분류까지 넓힌다 (CON-U5)
- 종류: PR | 규모: S | 태그: F · refactor
- 목표: `tests/rw/FakeRwModule.h` 의 FakeRwDeck 에 Ansys flat 스키마 조건(`target`/`component` + 필드 N개) · 요약 행만 남는 조건(omega 벡터 · D 라벨) · bounded(min/max)·enum 속성을 더하고, `TestRwDocument` 에 `feConditionEntries` 분해 케이스 3건 — 필드별 행 수 · 요약 행 readOnly · `dvKind` Discrete/Categorical + cases — 을 추가한다. 생산 코드 변경 없음.
- 완료 기준:
  1. tests/TestRwDocument.cpp 에 3 케이스 추가·통과 — `rwPropertyDvKind` 의 세 분기(Continuous·Discrete·Categorical) 각 1건 이상
  2. FakeRwDeck 으로 **flat 조건(entries 없음 + 스칼라 스키마 2필드) · 읽기전용 요약 행(omega 벡터 · D 라벨) · bounded(min/max)·enum 속성 조건**을 만들 수 있고 읽기·편집이 거부되지 않는다(`/entries/` 외 경로가 필요하면 추가) — CON-09 완료 기준 (2) 를 이 항목이 대신 덮는다
  3. 기존 TestRwDocument 15건 무변경 통과 (PR #658 이 `couplingShapesKeepSeparateOwnersAndMembership` 1건을 더하므로 머지 뒤 기준 16건)
- 변경 범위: tests/TestRwDocument.cpp · tests/rw/FakeRwModule.h
- 선행: -
- 충돌: CON-09 (같은 `tests/rw/FakeRwModule.h` — EXE-21 을 먼저 랜딩한다) · B2 교집합: PR #658(FakeRwModule.h·TestRwDocument.cpp)
- 흡수: CON-U5 · CON-U5(픽스처 몫 — CON-09 완료 기준 (2)) · CON-c17 · EXE-c58
- 비고: 생산 좌표 — `controller/DashRwDocument.cpp:rwPropertyDvKind`(:450-488) · 분해 본체는 익명 namespace 의 코루틴 `readFeCondition`(:518) 안: flat 필드별 행 루프 :650-667 · 읽기전용 요약 행 :672-692. `DashRwDocument::feConditionEntries`(:1072-1075) 는 `m_gen->feConditions.value(condName).entries` 를 돌려주는 캐시 1줄이라 분해 코드가 없다. 생산 코드는 변경하지 않는다. CON-U5 는 "입력 검증 부재" 가 아니라 테스트 부재(UIC-c57 판정과 같음). 픽스처 귀속은 C-2 ⑦ 로 EXE-21 확정 — 공용 픽스처이고 흉내낼 대상(`DashRwDocument` flat 스키마 분해)이 EXE 소관이며 CON-09 는 픽스처를 **쓰는** 쪽. CON-09 의 완료 기준 (2) 삭제 · `FakeRwModule.h` 변경 범위 제외 · `선행: EXE-21` 추가는 `보류: CON 몫`.

#### EXE-22 · 해석 deck 적재를 RW 액터 워커로 옮긴다 (#458-a, EXE-14 조건부)
- 종류: PR | 규모: M | 태그: B · perf
- 목표: EXE-14 가 (b) 단일 액터 스레드 또는 (c) per-instance 어피니티를 택하면 — `DashRwActor` 의 GUI 스레드 감금(**생성자** `DashRwActor::DashRwActor()` 의 assert `:98` · 전 메서드 `assertActorThread`) 을 액터 스레드 소유로 바꾸고 `invokeOnActor` 마샬링 방향을 뒤집는다(GUI → 액터 blocking, 액터 → GUI 역호출 금지 = LEAF RULE). `DashAnalysisModelContextRegistry::load` 가 QCoro 라 소비측은 변경 없음 — `co_await …load(…)` 는 **8파일 9곳**이다: `view/DashMainWindow.cpp:2766`(1곳) · `view/DashAnalysisLauncherWidgetLauncher.cpp:338`·`:362` · `view/DashModelRunnerWidget.cpp:2202` · `view/DashModelingTreeWidget.cpp:539` · `controller/DashMorphingDoeExecutor.cpp:760` · `model/DashGeometryParameter.cpp:161` · `model/DashModelRunner.cpp:2153` · `model/DashOptimizer.cpp:1491`. `DashDoeBatchChain` 에는 `registry.load` 가 없다(`DashRwDocumentHandle` 경유). 적재 중 진행 표시는 EXE-07 규약.
- 완료 기준:
  1. 대형 deck(.inp/.dat) 적재 중 GUI 이벤트 루프가 돈다 — 상태바 진행 표시 · 창 이동 가능 (실측 기록, 현행 1~20s 프리즈 대비)
  2. tests/TestRwActor.cpp 에 "액터 메서드가 GUI 스레드에서 실행되지 않는다" · "GUI 에서 부른 invokeOnActor 가 액터 스레드에서 완료된다" 2건 추가·통과
  3. 기존 TestRwActor 6 · TestRwDocument · TestDoeBatchChain · TestMorphingGeometry 통과 (`TestDoeBatchChain` 은 PR #655 가 +7/-3 고치므로 머지 **뒤** 기준) + 소비측 무변경 확인 — 위 9곳 중 `view/DashModelRunnerWidget.cpp`·`view/DashModelingTreeWidget.cpp`·`model/DashGeometryParameter.cpp`·`model/DashModelRunner.cpp`·`model/DashOptimizer.cpp` 5경로를 각 1회 수동 적재로 확인
- 변경 범위: controller/DashRwActor.h · DashRwActor.cpp · controller/DashRwDocumentHandle.cpp · tests/TestRwActor.cpp (결정이 (c) 면 controller/DashAnalysisModelContextRegistry.cpp 도)
- 선행: EXE-14 · EXE-05 (스레드 계약 문서 · DashRwActor.cpp assert 치환이 먼저)
- 충돌: EXE-05 (DashRwActor.cpp) · MOR-16 (#281 Follow-up — RW 세션 계측) · PR #654 · PR #655 (controller/DashDoeBatchChain.{cpp,h} · tests/TestDoeBatchChain.cpp) · B2 교집합: DashAnalysisModelContextRegistry.cpp → PRJ-03 REN-01 REN-02 REN-07 UIC-19 · PR #658(DashRwActor.cpp)
- 흡수: #458(적재 축 — 담당 RUN → EXE) · RUN-D5(deck 파서 축) · RUN-c09 · EXE-c46, c59
- 비고: EXE-14(INV) 의 실측이 (a) 유지로 귀결되면 CLOSE — #458 은 "GUI 스레드 유지 + 진행 표시(EXE-07)" 로 재정의한다. dfsxml 1·2단계(#458-b) 는 LCH(RUN-c10). PoC PR #529(닫힘, 브랜치 `perf/458-rw-actor-worker`) 참고. Analyzer 축 캐시는 #410(Done) 으로 표면이 다르다.

### PER — 영속화 · 식별자

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> dev @ b08a91b3. 원천·판정은 02-claims/PER.md. PER 은 횡단 모듈이라 "공통 기반 1건" 만 항목으로 두고, 소비자별 이행(직쓰기 22지점 · 왕복 단절 28건 · 생산 출처 기록·소비 판독)은 `범위밖 → 해당 모듈` 로 넘긴다 (PER-c05 · c22~c30 · c13).
> 열린 PR 6건(#651 #652 #654 #655 #656 #658 — decisions ⑩) 중 PER 항목과 파일이 겹치는 것: #651(`DashAnalysisLauncherConfig.cpp`) · #652(`DashDoeSampler.cpp`) · #654·#655(`docs/test-levels.md`) · 넷 다 `tests/CMakeLists.txt`. #656·#658 은 PER 파일을 만지지 않는다. 겹침은 전부 **충돌**이고 **선행**이어야 하는 PER 항목은 없다 — 네 PR 중 어느 것도 PER 항목이 고치는 함수를 바꾸지 않는다(테스트 등록·문서 표만). #530 은 머지하지 않는다(C-2 ②) — PER-07 이 그 공통부를 재업로드한다.
> 권장 순서: PER-01 · PER-03 · PER-06 · PER-10 (결정 4건, 서로 독립 — PER-10 은 헬퍼 계약에 얹히므로 PER-02 앞) → PER-02 → PER-04 · PER-05 · PER-07 → 모듈별 이행.
> Phase B1: #368 주 모듈 LCH→PER 확정(00-progress 메모) — 본체는 PER-06·PER-07, 홉별 5건은 접점. 범위밖 이관 흡수(PER-c31~c33): MOR-c46 → PER-10(신규) · PRE-c60 → PER-03(기흡수) · EXE-c41 DOE-D22 몫 → PER-02.
> C' 반영(2026-10-06, 04-review/PER.md 14건 + decisions ②③④⑤): PER-02 를 `DashSaveSystem` 헬퍼 승격으로 재정의(③) · PER-06 ① 을 확정 전제로 내리고 결정 범위 축소(⑤) · PER-07 을 "공통부만 + 재업로드" 로 못박음(②) · `PER-11` 신설(#471 CLOSE). 항목 10 → 11.

#### PER-01 · 도메인 이행 대상 코덱 층을 하나로 정한다 — `utils/DashGadgetCodec` vs `persistence/DashSaveSystem`
- 종류: DEC | 규모: S | 태그: A, E
- 목표: 소비자 0 인 코덱 층이 둘이다 — #478 이 가리키는 `DashGadgetCodec`(Q_GADGET ↔ QJsonObject, 부분 로드 허용) 과 #584 가 들여온 `DashSaveSystem`(registered object 트리, 버전 키·QSaveFile·`Result` 내장). 모듈 Set JSON(설정 구조체 7종 + DOE Table + model_info + ModelRunner config)의 이행 대상 층과 미채택 층의 처분(삭제 / 용도 한정 유지)을 정하고, 이행 절차(구조체 선언 규칙 · 키 이름 = 현행 JSON 키 · 1호 소비자)를 기록한다.
- 완료 기준:
  1. 결정 기록 — 채택 층 · 미채택 층 처분 · 선택 근거 4가지: (a) 부분 로드 vs 실패 (b) 컨테이너 등록 (c) QUuid·Q_FLAG 취급 — (a)~(c) 는 docs/persistence.md "DashGadgetCodec 과의 차이" 표 기준 (d) **저장 단위** — 모듈 Set JSON 은 파일 1개를 여러 라이터가 섹션 단위 RMW 로 공유하는데(`AnalysisLauncher_{Set}.json`: `DashAnalysisLauncherConfig::write*` + PM `saveOutputResponse` · `GeometryParameter_{Set}.json`: `saveMorphingTarget` + PM `saveMorphingSettings` + Widget `setupMorphingTab` + `DashSetIdentity` write-back · c08 RMW 13곳) 두 코덱 모두 "객체 1 ↔ JSON 객체 1" 이다 → 섹션 변환과 다중 라이터 병합을 코덱 밖 헬퍼(`updateObject`, PER-02 비고)가 맡는지
  2. 이행 절차 1쪽 + 1호 소비자 지정(권장: 키가 적고 테스트가 있는 `DashSetReferenceModel` 또는 `DashParameterization` — 각각 PRJ·DOE 항목으로 발행)
  3. docs/persistence.md 또는 utils/DashGadgetCodec.h 머리말에 결정 반영 (문서 변경만)
- 변경 범위: docs/persistence.md (결정 기록) — 코드 변경 없음
- 선행: -
- 충돌: B2 교집합: persistence.md → PER-03 PER-10
- 흡수: #478 · PER-c01, c02
- 비고: **파일 계층(`DashSaveSystem::read/writeJsonFile`)은 이 선택의 대상이 아니다** — C-2 ③ 으로 공용 진입점으로 확정됐고(PER-02), 미채택이 persistence 여도 PER-08 은 그 2함수를 남긴다. 판단 재료 — `DashSaveSystem` 은 registered object(QObject) 전제라 현행 모듈 모델(대부분 QObject 이나 `DashRegisteredObject` 아님)에 바로 붙지 않고, `DashGadgetCodec` 은 구조체만 다뤄 기존 `loadFromJson/saveSettings` 함수의 본문을 교체하는 식으로 점진 이행이 된다. "둘 다 유지(MVVM Model 은 SaveSystem, 평면 설정 구조체는 GadgetCodec)" 도 선택지 — 그 경우 PER-08 은 CLOSE.

#### PER-02 · `DashSaveSystem` 의 JSON 파일 헬퍼를 공용 진입점으로 승격하고 파일 지역 사본 4벌을 치환한다 — 원자 쓰기 · 읽기 규칙 · 사유 반환
- 종류: PR | 규모: M | 태그: A, E · refactor
- 목표: 신설하지 않는다 — `persistence/DashSaveSystem::readJsonFile`/`writeJsonFile`(static · 임의 QVariantMap · `QSaveFile` · `Result` 오류 · `TestMvvmBase` 왕복 테스트 보유)이 이미 공용 파일 계층이고, 새 `utils/DashJsonFile` 은 9번째 구현이 된다(C-2 ③). 이 2함수를 **공용 진입점으로 승격**하고 모자란 3가지를 보강한다 — ① 읽기 규칙: "파일 없음·0바이트·공백 = 빈 객체(ok)", "손상(파싱 실패·배열·스칼라 루트) = 실패 + 사유, 원본 보존" (현행은 open 실패·빈 파일·손상을 모두 실패로 뭉갠다) ② `write` 반환 길이 검사 ③ `QJsonObject` 받고 돌려주는 오버로드 — 소비자 8벌이 전부 `QJsonObject` 를 쓴다. 치환은 c03 의 사본 7벌 중 4벌 — `model/DashSetIdentity.cpp`·`model/DashSetLegacyMigration.cpp` 의 anonymous `readJsonObject`/`writeJsonObject`, `model/DashDoeSelection.cpp:readJsonObject`(동작 불변 — 실패를 빈 객체로 받는다), `model/preprocessor/DashDoeTableFile.cpp:read`(`ReadResult.error` 를 헬퍼 사유로 채운다 — 호출 4곳의 시그니처 불변). 나머지 3벌은 같은 진입점으로 다른 항목이 이행 — `DashAnalysisLauncherConfig::readRoot/writeRoot` 는 #638 과 같은 자리라 PRE-14·15, `DashDoeSampler::loadJsonRoot`·`DashDoeConfigManager::loadSettings` 는 DOE-17.
- 완료 기준:
  1. `readJsonObject`/`writeJsonObject` 가 `model/` 에 0건 · 네 파일에 `QJsonDocument::fromJson`·`QSaveFile` 직접 호출 0 — 전부 진입점 경유
  2. `tests/TestJsonFile.cpp`(또는 `TestMvvmBase` 보강): 0바이트·공백 → ok+빈 객체 / 잘림·배열·스칼라 → 실패+사유 / 쓰기 실패(읽기 전용 경로) 시 기존 파일 바이트 동일 / 정상 쓰기 후 재읽기 동일 — ctest 통과
  3. 기존 `test_set_identity`·`test_set_legacy_migration`·`test_doe_selection`·`TestDoeTableFile`·`TestMvvmBase` 통과
  4. 소비자 9건이 이 진입점을 선행으로 둔다 (전건 등재 확인) — DOE-17 · CON-11 · MOR-22 · CAD-13 · OPT-24 · RUN-32 · BLD-17 · PRJ-31 · PRE-27(조건부). 각 항목의 "`DashJsonFile`" 문구는 "`DashSaveSystem` 헬퍼(공용 진입점)" 로 바뀐다 — PRJ-31 · RUN-32 · OPT-24 는 미치환(**보류: PRJ · RUN · OPT 몫**)
- 변경 범위: persistence/DashSaveSystem.h · persistence/DashSaveSystem.cpp · model/DashSetIdentity.cpp · model/DashSetLegacyMigration.cpp · model/DashDoeSelection.cpp · model/preprocessor/DashDoeTableFile.cpp · tests/TestJsonFile.cpp (신규) · tests/CMakeLists.txt
- 선행: -
- 충돌: PER-07 (model/DashDoeSelection.cpp — 순차) · PRE-14 · PRE-15 (같은 `readRoot` — **PRE-14 가 먼저**(#638 bug), PER-02 가 뒤에서 진입점으로 치환) · DOE-16 · DOE-17 (DOE 쪽 2벌을 같은 진입점으로 이행) · PER-04 · PER-08 (같은 `DashSaveSystem` 파일) · B2 교집합: tests/CMakeLists.txt → 공유 12건(deps.md 5절) · DashDoeSelection.cpp → DOE-12 · DashDoeTableFile.cpp → DOE-02 PRJ-33 · PR #655(tests/CMakeLists.txt) · PR #654(tests/CMakeLists.txt) · PR #652(tests/CMakeLists.txt) · PR #651(tests/CMakeLists.txt)
- 흡수: #478 · #479 · #638(공통 규칙) · DOE-D22(원자 쓰기 몫, EXE-c41 이관) · PER-c03, c06, c07, c08, c09, c19(규칙 부분), c33
- 비고: 코덱 층 선택(PER-01)과 **분리 유지** — 두 코덱 모두 파일 I/O 를 호출 측에 둔다(`DashGadgetCodec.h` 4항). 승격 대상은 코덱이 아니라 그 아래 파일 계층이므로 PER-01 이 persistence 를 미채택해도 이 2함수는 남는다(PER-08 완료 기준 3). 위치는 `persistence/DashSaveSystem` 그대로 두고 함수만 승격한다 — 파일을 옮기면 9모듈 이행 항목의 변경 범위가 전부 흔들린다. 직쓰기 22지점(c22~c30)은 이 진입점으로 이행하면서 원자성·사유 반환·(PER-04 후) 버전 키를 한 번에 얻는다 — 모듈별 항목. RMW 를 돕는 `updateObject(path, fn)` 를 둘지는 소비자 13곳(c08) 이행 시 결정 — PER-01 완료 기준 1(d) 의 입력.

#### PER-03 · 저장 포맷 버전 키 규약을 정한다 — 키 이름 · 자리 · 판정 · 키 부재 규약과의 관계
- 종류: DEC | 규모: S | 태그: A, C
- 목표: 현행은 "키 부재 = 구버전"(D14 · `referenceModel`·`setId`·`tableId`)이고 버전 키는 `referenceModels.json` 의 `schemaVersion` 1종뿐이다. 다음을 정한다 — ① 키 이름(`schemaVersion` 재사용 권장)과 자리(루트) ② 값 의미(파일 종류별 정수, 앱 버전 아님) ③ 로드 판정(상위 버전 → 거절·읽기 전용 + 안내, 하위·부재 → 현행 키 부재 규약으로 해석 — 마이그레이션 프레임워크 불도입) ④ 구 파일 write-back 시점(SI-3 선례 "열기 시 1회" vs "다음 저장 시") ⑤ 대상 파일(모듈 Set JSON 7종 · DOE Table · AnalysisLauncher config · model_info.json · ModelRunner config · referenceModels.json) ⑥ `variant`(타입 판별) 와의 역할 분리 ⑦ 결과 XML(PRE-28·29)이 같은 규약을 쓰는지 — #444 분할 파일은 LCH-32 비용 검증 결과 실제 분리가 필요할 때만 포함한다.
- 완료 기준:
  1. 결정 기록 7항 + 대상 파일별 초기 버전값 표 + **D14 개정 기록**(정본 문서 `Project-Manifest-0-Work-Order.md` 결정표 — "스키마 버전은 올리지 않고 키 부재를 구버전 판정으로" 가 #480 과 정반대이므로, 이 항목은 곧 D14 개정이거나 D14 유지 + #480 기각이다)
  2. 이 기록을 선행으로 참조하는 항목 — PRJ-32(⑥ `variant` 와의 역할 분리, 등재 확인) · 결과 XML 의 키 작성 PRE-28·29(미등재 — **보류: PRE 몫**) · RUN-10은 실제 파일 충돌 검사로 결과를 보존하며 새 채번 키를 요구하지 않음(c16)
- 변경 범위: 결정 기록 (03-items 비고 또는 docs/persistence.md) — 코드 변경 없음
- 선행: -
- 충돌: B2 교집합: persistence.md → PER-01 PER-10
- 흡수: #480 · #411 결정 3 (PRE-c60 이관) · PER-c10, c11, c32
- 비고: 되돌리기 비용이 큰 결정(저장 포맷)이라 PR 보다 먼저. 선례 2건이 이미 ③ 의 형태다 — `DashReferenceModelLedger::load`(상위 `schemaVersion` → 적재 안 함 + 쓰기 불가) · `utils/log/DashLogFormat.h:kFormatVersion`(=2, "없는 파일 = Legacy v1" — 키 부재 규약과 버전 키의 공존 선례).

#### PER-04 · 헬퍼가 버전 키를 자동 기록·판정하게 하고 ledger 의 손코딩 버전 처리를 통일한다
- 종류: PR | 규모: M | 태그: A, C · feature
- 목표: PER-02 가 승격한 진입점(`DashSaveSystem::writeJsonFile`)이 PER-03 의 키를 자동 기록하고 `readJsonFile` 이 상위 버전을 실패(사유 "newer format") 로 돌려준다 — 파일 종류별 버전값은 호출자가 넘긴다. `DashReferenceModelLedger::load/save` 의 `kSchemaVersion` 처리를 헬퍼 경유로 바꾼다 (동작 동일). 모듈 Set JSON 은 소비자가 PER-02 헬퍼로 이행하는 순간 키를 얻는다 — 모듈별 항목.
- 완료 기준:
  1. `tests/TestJsonFile.cpp`: 쓰기 후 파일에 키 존재 / 상위 버전 파일 읽기 → ok=false + 사유 / 키 부재 파일 → ok (현행 규약 유지)
  2. `test_reference_model_ledger` 통과 · `schemaVersion` 리터럴이 `model/DashReferenceModelLedger.cpp` 에 0건(진입점이 소유)
  3. 소비자 미이행 파일의 로드 동작 불변 (키 없는 구 프로젝트 열기 — 수동 1회)
- 변경 범위: persistence/DashSaveSystem.h · persistence/DashSaveSystem.cpp · model/DashReferenceModelLedger.cpp · tests/TestJsonFile.cpp · tests/TestReferenceModelLedger.cpp
- 선행: PER-02 · PER-03
- 충돌: PER-02 · PER-08 (같은 `DashSaveSystem` 파일 — 순차) · PRJ 의 ledger 항목(미작성) · B2 교집합: TestReferenceModelLedger.cpp → PER-05
- 흡수: #480 · PER-c10, c11
- 비고: write-back 시점이 "열기 시 1회"(PER-03 ④)로 정해지면 `DashSetIdentity::ensureAll` 과 같은 자리에 키 부여를 얹는 PRJ 항목이 하나 더 생긴다 — 그 전까지는 "다음 저장 시" 가 자연 경로.

#### PER-05 · "저장→로드→재저장 동일성" 테스트 게이트를 공용 픽스처로 세운다
- 종류: PR | 규모: S | 태그: A, F · refactor
- 목표: `tests/JsonRoundTrip.h` 에 "파일 → 로드 → 저장 → 파일" 두 JSON 의 정규화 비교(키 정렬 · 들여쓰기 무시 · 허용 차이 목록) 헬퍼와 픽스처 디렉터리 규칙(`tests/fixtures/<Module>_<case>.json`)을 두고, 첫 적용으로 `TestReferenceModelLedger` 에 referenceModels.json 왕복 케이스 1건을 넣는다. docs/test-levels.md 에 "모듈 JSON 의 저장 경로를 고치는 PR 은 왕복 케이스를 추가한다" 규칙 1줄.
- 완료 기준:
  1. 헬퍼 TU 없이 헤더만으로 기존 TU 에서 쓸 수 있다 (ledger 왕복 케이스 ctest 통과)
  2. docs/test-levels.md 규칙 1줄
- 변경 범위: tests/JsonRoundTrip.h (신규) · tests/TestReferenceModelLedger.cpp · docs/test-levels.md
- 선행: -
- 충돌: CAD-11 · DEV 의 tests 인프라 항목 (tests/CMakeLists.txt 를 건드리게 되면) · B2 교집합: TestReferenceModelLedger.cpp → PER-04 · test-levels.md → DEV-13 · PR #655(test-levels.md) · PR #654(test-levels.md)
- 흡수: #478(게이트) · PER-c04, c05
- 비고: **게이트는 선행이 아니다** — 왕복 단절 28건의 모듈 항목은 "왕복 케이스 1건(PER-05 헬퍼)" 을 자기 `완료 기준` 에만 쓰고 `선행: PER-05` 는 두지 않는다. 게이트를 선행으로 걸면 bug fix 가 인프라 PR 을 기다린다(검토 #9). DOE-17 은 제거 완료 · CON-11 은 미제거(**보류: CON 몫**). JSON 수준 비교라 코덱 선택(PER-01)과 무관. 현행 왕복 깨짐 중 "저장된 값이 로드 후 다른 키로 가는" 류(BLD-D4·D7)는 정규화 비교로 잡히고, "쓰기만 되고 읽기에서 버려지는" 류(BLD-D8·RUN-D33·ANA-D9)는 두 번째 저장이 키를 잃어 잡힌다 — 28건 중 쓰기 경로 자체가 없는 3건(MOR-D10·MOR-D11·CAD-D17)은 게이트 밖(모듈 feature).

#### PER-06 · Set 참조와 산출물 출처의 공통 계약을 정리한다
- 종류: DEC | 규모: S | 태그: C, A
- 목표: #520의 기존 Set JSON `setId` 발급·영속·역조회를 사용한다. Set 설정은 현재 상류 입력 참조를, 산출물은 생성 Set·실제 입력 Set·세부 선택·deck 출처를 소유한다. 현재 Set ID를 유지하면서 다른 상류 setId로 참조를 변경할 수 있다. 입력 선택만 바꾸어 기존 산출물 출처를 고치지 않으며, 재실행 결과를 덮어쓸 때 실제 출처를 함께 갱신한다.
- 완료 기준: ① 공통 기록·판독 계약과 필수 출처/검증 실패 사유를 정의 ② #368은 DOE-16 → PRE-32 → BLD-20의 model_info.json 생성까지, #685는 RUN-34·OPT-26 소비부터 담당 ③ parameterizationId·derivedId·최초 입력 영구 핀 폐기 ④ 구산출물 출처 누락은 재생성 안내, 이름·경로 추론/자동 이관 금지, 기존 Set ID 복원 유지 ⑤ #650 버전·최신성과 #473 결과 키를 구분. 전체 산출물 이력 보존과 별도 Set·산출물·소비 대장은 요구하지 않음.
- 변경 범위: 결정 기록 — 코드 변경 없음
- 선행: -
- 충돌: -
- 흡수: #368 공통 계약 · #443 입력 참조 · PER-c13, c15 · PER-c14(대장 취소 근거)
- 비고: #470은 출처 추적 상위 목표로 유지(PER-09), #471 취소는 PER-11. tableId는 기존 실행 스냅샷 식별에 유지하되 조합 ID나 #650 버전을 대신하지 않는다. 구 PR #530의 산식·핀 구현을 그대로 이식하지 않는다.

#### PER-07 · 개별 Set 참조와 출처 기록·판독 공통부를 구현한다
- 종류: PR | 규모: M | 태그: C · feature
- 목표: #368의 공통 기록·판독 타입, 필수 필드 검증, 재생성 안내를 구현한다. #520의 setId 해석을 재사용하고 producer Set·실제 입력 Set·세부 선택·deck 정보를 명시적으로 다룬다. 조합 문자열 생성·해석·비교 함수와 최초 입력 고정 API는 도입하지 않는다.
- 완료 기준: 공통 테스트에서 개별 setId·선택·deck 왕복, 필수 출처 누락 거절, 개명 뒤 동일 ID 해석, 동명 재생성의 다른 ID 구분을 검증한다. 다른 유효한 상류 Set으로 참조를 바꿀 수 있고 기존 산출물 출처는 보존된다. 생산·소비 모듈은 이 계약을 공유하며 소비측에서 스키마를 중복 정의하지 않는다.
- 변경 범위: model/DashPipelineStamp.h (공통 출처 타입·판독 계약) · model/DashDoeSelection.h · model/DashDoeSelection.cpp · tests/test_doe_selection.cpp
- 선행: PER-06
- 충돌: PER-02 (model/DashDoeSelection.cpp — 순차) · DOE-16 (`DashDoeSelection` · test_doe_selection — PER-07 먼저) · B2 교집합: DashDoeSelection.cpp → DOE-12 · test_doe_selection.cpp → DOE-10 DOE-12 · DashDoeSelection.h → DOE-12
- 흡수: #368 공통부 · #443 기존 setId 활용 · PER-c13
- 비고: PR #530 재업로드 노선은 당시 브랜치 처리 기록으로 보존한다. 새 구현은 현행 계약으로 다시 작성하며 기존 hunk의 산식·핀·fallback을 복원하지 않는다. PER-07 → DOE-16 → PRE-32 → BLD-20이 생산 경로이며 #368 완료 후 RUN-34·OPT-26이 #685를 구현한다.

#### PER-08 · 미채택 코덱 층과 그 테스트를 제거한다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: PER-01 이 한 층만 남기기로 하면 다른 층(`utils/DashGadgetCodec.{h,cpp}` + `tests/TestGadgetCodec.cpp`, 또는 `persistence/*` 4쌍 + `model/DashMvvmModelBase` + `viewmodel/DashMvvmViewModelBase` + `tests/TestMvvmBase.cpp` + docs 2편)을 지운다.
- 완료 기준:
  1. 닫기 사유 또는 삭제 — 제거 층의 심볼 0건 · tests/CMakeLists.txt 의 해당 `add_test` 제거 · ctest 전체 통과
  2. docs/persistence.md · docs/mvvm-pattern.md 의 참조 정리
  3. persistence 를 지우는 경우에도 **파일 계층은 남긴다** — `read/writeJsonFile` 2함수 + 그 테스트를 `persistence/DashJsonFile.{h,cpp}` 로 옮기고 PER-02 소비자 9건의 include 를 따라 고친다 (C-2 ③: 이 2함수가 공용 진입점)
- 변경 범위: PER-01 결과에 따라 위 두 집합 중 하나 + tests/CMakeLists.txt + docs (persistence 쪽을 지우면 persistence/DashJsonFile.h · persistence/DashJsonFile.cpp 신규)
- 선행: PER-01 · PER-02 (파일 계층 승격이 먼저 — 삭제 집합의 경계가 그때 확정된다)
- 충돌: PER-02 · PER-04 (같은 `DashSaveSystem` 파일) · B2 교집합: tests/CMakeLists.txt → 공유 12건(deps.md 5절) · PR #655(tests/CMakeLists.txt) · PR #654(tests/CMakeLists.txt) · PR #652(tests/CMakeLists.txt) · PR #651(tests/CMakeLists.txt)
- 흡수: PER-c01, c02 (처분 부분)
- 비고: PER-01 이 "둘 다 유지" 면 CLOSE. 삭제 전 `utils/log/DashLogModule.h` 의 모듈 주석(`App` 에 DashGadgetCodec 명시)도 함께 고친다.

#### PER-09 · #470 출처 추적 상위 목표를 유지한다
- 종류: DEC | 규모: S | 태그: C
- 목표: #470을 현행 상위 목표로 유지하고 #368 생산·공통 계약, #685 소비, #471 대장 취소와의 관계를 명시한다. 새 작업 목록 작성만으로 열린 이슈를 종료하지 않는다.
- 완료 기준: #470 유지와 #471 취소를 구별하고 #368 → #685 범위 및 #650 별도 목표를 대응표에 반영한다. GitHub 상태 변경은 이번 문서 작업에 포함하지 않는다.
- 변경 범위: -
- 선행: PER-06 (하위 처분 확정 뒤)
- 충돌: -
- 흡수: #470 · PER-c12
- 비고: 이전 종료 제안은 2026-10-08 결정으로 대체됐다.

#### PER-10 · 설정 초기값(default) 정책을 세운다 — 전수 조사표와 소유자·진입점·대역 로그 규칙
- 종류: DEC | 규모: S | 태그: A, E
- 목표: #423 의 1·2 단계. (1) 같은 JSON 키를 2곳 이상이 리터럴 대역으로 읽는 패턴(`"active"` `toBool(true)` 20곳/12파일 등 이슈 표의 키 14개) · `.ui`/멤버 초기값 이중화(.ui 6개) · `QSettings` 대역(36줄/12파일)을 dev 에서 확정한 조사표 (2) 초기값 3분류(정책 default · escape · sentinel) · 키별 소유자 1곳 · 진입점 1개 · `.ui` 리터럴 처분 · 대역 사용 시 WARN 규칙을 docs/ 에 기록. 적용(3 단계)은 키별 소유 모듈 항목 — 첫 사례 MOR-11.
- 완료 기준:
  1. 조사표 — **이슈 표의 키 14개**에 한정해 dev 수치로 재확정(키 · 읽는 곳 · 대역값 · 소유자 후보). 전수 재조사는 하지 않는다: 주요 수치가 재측정에서 일치했다(`"active"` `toBool(true)` 20곳/12파일 · `QSettings` 36줄/12파일) — 미재확인은 `.ui` 초기값 이중화 6개(패턴 C)뿐이라 그 6개만 센다
  2. 정책 문서(docs/persistence.md 절 신설) — 분류 · 소유자 규칙 · 진입점 · `.ui` 리터럴 · 로그 규칙
  3. PER-02 헬퍼 계약에 "키 부재 = 소유자 default 로 채운다(대역은 WARN)" 가 어떻게 얹히는지 1절
- 변경 범위: docs/persistence.md (기록만) — 코드 변경 없음
- 선행: -
- 충돌: B2 교집합: persistence.md → PER-01 PER-03
- 흡수: #423 (1·2 단계, MOR-c46 이관) · PER-c31
- 비고: PER-02 와 독립이지만 완료 기준 3(헬퍼 계약에 얹히는 방식)을 쓰려면 **PER-02 보다 앞**이 자연스럽다 — 머리말 권장 순서가 그 순서다. 선행란에 ID 를 적지 않은 것은 의도(괄호 안 ID 가 선행으로 파싱되는 것을 막는다 — 검토 #10). 종류는 조사 몫이 작아 `DEC` 유지(1-2 절 5종). #423 주 모듈은 MOR(배정표) 이고 3 단계 첫 사례가 MOR-11 — 1·2 단계는 횡단이라 PER. `"active"` 는 DOE 케이스 활성 플래그로 model 11파일에 흩어져 적용 몫은 LCH 가 가장 크다. 되돌리기 비용 낮은 결정(문서) — 간단히 정하고 넘어간다.

#### PER-11 · #471 독립 산출물·소비 대장 취소를 유지한다
- 종류: CLOSE | 규모: S | 태그: C, A
- 목표: 별도 산출물·소비 대장을 구축하지 않는다. 각 Set의 현재 입력 참조와 산출물의 생성 당시 출처를 원본으로 삼고 프로젝트 객체가 조회·집계한다.
- 완료 기준: 대장 취소 근거를 기존 Set JSON의 setId 참조와 #368·#685의 개별 출처 기록·판독 계약으로 설명한다. 현재 참조 조회와 과거 산출물 출처 조회를 구분하며 조합 ID 스캔으로 소비 이력을 복원한다고 보장하지 않는다. 전체 이력 보존은 요구하지 않는다.
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #471 · PER-c14
- 비고: #471 취소는 유지하며 #470은 PER-09에 따라 유지한다. 대장 재도입을 조건부 후속 PR로 미리 요구하지 않는다.

### UIC — UI 공통

> dev @ b08a91b3. 현행은 Qt6 — 위키 Stage 3(`PassThrough` 선언)은 소멸했고, 비정수 DPR 이 이미 들어오므로 R1~R5 는 현재 결함이다(각 모듈 소관). 열린 PR 5건 중 머지 대상 4건과의 충돌: #655 · #654 · #652 · #651 이 DashMainWindow.cpp 를 만지고, 그중 **#655 는 `setupMorphingBar()`·`initializeMorphingController()` 본문과 `view/overlay/DashMorphingSettings.{cpp,h}`·`ui/overlay/DashMorphingSettings.ui`·`tests/CMakeLists.txt` 를 재작성**한다 — UIC-07 · UIC-22 는 #655 를 선행으로 둔다(decisions ④). **#530 은 머지하지 않으므로**(decisions ②) 충돌란에서 제거했고 홉별 항목(RUN-34 · OPT-26)이 대신 선다. 단순 충돌란 기입은 D-1 `build_deps.py --apply` 가 파일 교집합으로 채운다. DashMainWindow 를 고치는 항목(01 · 03 · 05 · 07 · 09 · 10)은 PRJ 의 DashMainWindow 항목과도 같은 파일이다.
> 창·DPI 항목의 순서는 위키 3부 "순서에 관한 제약" 을 따른다: 01(응급) → 03(Stage 2) → 05(Stage 1) → 08/09(Stage 4, 02 결과로 선후 결정) → 07 · 10 · 12 · 13.

#### UIC-01 · 창 geometry 를 화면 작업 영역으로 클램프해 복구 불가 상태를 차단한다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: `DashMainWindow::clampToScreen()` 을 신설해 `moveEvent`/`resizeEvent` 에서 `screen()->availableGeometry()` 로 크기·위치를 제한한다(`QScopedValueRollback` 재진입 가드). 프레임리스 창이라 OS 보호가 없으므로 이것이 유일한 안전망이다. 다른 변경과 독립 — 가장 먼저 단독 적용.
- 완료 기준:
  1. 배율이 다른 모니터로 창을 옮긴 뒤 타이틀바·네 모서리가 화면 안에 있고 F11 없이 조작 가능
  2. 창을 화면 밖으로 끌어내려 해도 작업 영역 안에서 멈춘다 · 이동 중 CPU 점유가 튀지 않는다(재진입 가드)
  3. `git grep availableGeometry view/DashMainWindow.cpp` ≥ 1
- 변경 범위: view/DashMainWindow.h · view/DashMainWindow.cpp
- 선행: -
- 충돌: PR #651 · #652 · #654 (DashMainWindow.cpp) · UIC-03 · UIC-05 · UIC-09 · PRJ DashMainWindow 항목 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashMainWindow.h → 공유 11건(deps.md 5절) · PR #655(DashMainWindow.cpp)
- 흡수: #447 · L0-6 · UIC-c03
- 비고: UIC-09(경로 B)로 가면 OS 가 클램프를 대신하므로 이 코드는 제거 가능 — 그때까지의 응급 조치. 사내 선례의 "시작 시 1회 오프스크린 검증" 은 성격이 달라 UIC-05 에 둔다.

#### UIC-02 · 멀티디스플레이 프리즈를 실기 재현하고 지배 요인·DPI awareness 를 실측한다
- 종류: INV | 규모: S | 태그: D · bug
- 목표: 100%/150%/**200%** 조합 듀얼 모니터에서 (a) 창 이동 시 프리즈 지속 시간과 화면 밖 착지 재현, (b) 프로파일러로 GL 재할당 / 레이아웃 패스 / `ResizeToContents` 열 재계산 중 지배 요인 특정, (c) 프로세스 DPI awareness 실제 값(Qt6 → Per-Monitor V2 기대) 확인과 manifest 명시 선언 필요 여부, (d) UI Scale 메뉴 실사용 여부(UIC-06 입력), (e) 배율 전환 후 폰트 의존 캐시 크기(UIC-12 대상 6곳 · `PlotLegend`)의 재계산 여부 — L2-6 소멸 판정의 유일한 근거가 될 측정. 25건 분석이 전부 정적이라 이 실측이 Stage 4·6·7 의 착수 근거가 된다.
- 완료 기준:
  1. 실측 결과 — 재현 절차 · 프리즈 구간 프로파일 · DPI awareness 값 · 상시 증상(dock 요동) vs 치명 발현 중 급한 쪽 판정 — 를 기록. 결과에 따라 UIC-08 · UIC-10 · UIC-11 의 착수 여부와 UIC-05/09 순서를 확정
  2. (e) **배율 전환 후 캐시된 크기의 재계산 여부** — 100%↔150%(·200%) 모니터 간 이동 뒤 UIC-12 대상 표 6곳과 `PlotLegend` 가 다시 맞춰지는지. 안 맞으면 `screenChanged`/`logicalDotsPerInchChanged` 연결이 필요하다는 판정을 기록하고 UIC-12 범위에 넣는다(위키 L2-6 "경로 B 로 가도 이 항목은 남는다")
- 변경 범위: - (manifest 선언이 필요하면 resources/resources.rc · CMakeLists.txt → DEV 접점)
- 선행: UIC-01 (재현 중 복구 불가 방지)
- 충돌: B2 교집합: CMakeLists.txt → DEV-11 DEV-21 DEV-24 DEV-25 MOR-06 MOR-07 · PR #658(CMakeLists.txt) · PR #654(CMakeLists.txt)
- 흡수: #447 · L0-3(잔여 manifest) · UIC-c02 · UIC-c04
- 비고: 사내 선례가 100%+125% 로 통과시킨 뒤 200% 에서 재오픈된 전례 — 200% 포함 필수. R1~R5 (CAD·ANA·OPT 소관)도 같은 환경에서 함께 확인하면 비용이 준다.

#### UIC-03 · resize·트리 선택마다 dock 을 강제 재분배하는 경로를 없애고 크기 선언을 1회로 바꾼다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: `resizeEvent` 의 `applyDockResize()`·`applyInnerModuleRenderSplit()` 호출과 `showRightDock`/`hideRightDock` 의 `applyInnerModuleRenderSplit()` 을 제거하고, 모듈 dock `Preferred`/렌더 dock `Expanding` sizePolicy 와 `RIGHT_DOCK_MIN` 의 `setMinimumWidth` 선언 1회로 대체한다. `hideRightDock` 에 대칭 early return. `findChildren<QSplitter*>` 오결선 블록을 삭제하고, 타이머 4개(100/200/50/50ms)를 `showEvent` 최초 1회로 통합하며 `adjustLogDockHeight` 의 800 폴백과 미사용 `mainHeight` 를 없앤다. AI 필밍(`m_rightDockPinned`·`AI_DOCK_RATIO`) 경로는 명시 전환 시점의 1회 선언으로 남긴다.
- 완료 기준:
  1. 로그 dock 경계를 드래그한 뒤 창을 리사이즈해도 조정값 유지 · 모듈 내부 플롯 splitter 를 움직여도 로그 dock 높이 불변
  2. 트리 부모↔자식 반복 클릭·우측 dock 개폐 반복 시 왼쪽 트리 폭 고정 · 같은 모듈 재진입 시 우측 dock 폭 동일
  3. `resizeEvent`·`showRightDock`·`hideRightDock` 에 `resizeDocks` 호출 0 · `QTimer::singleShot` 으로 레이아웃을 만지는 곳 0 · AI 필밍 진입/복귀 회귀 없음
- 변경 범위: view/DashMainWindow.h · view/DashMainWindow.cpp
- 선행: UIC-01
- 충돌: PR #651 · #652 · #654 · UIC-05(같은 함수군 — 연속 작업) · UIC-10 · PRJ DashMainWindow 항목 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashMainWindow.h → 공유 11건(deps.md 5절) · PR #655(DashMainWindow.cpp)
- 흡수: #449 · L0-1 · L1-4 · L2-1 · L2-2 · L2-3 · L2-4 · L2-5 · UIC-c09, c10, c11, c12, c13, c14
- 비고: 위키는 Stage 1+2 를 한 변경으로 묶으라 하지만 기제가 둘(선언 복귀 vs 영속화)이라 나눈다. 이 순서(2→1)면 중간 상태도 성립한다 — 영속화 없이 Qt 기본 배치만 남는다. 반대 순서(1→2)는 복원값이 같은 프레임에서 덮여 "구현했는데 안 되는" 상태가 되므로 금지. `m_logHeightRatio`·`adjustLogDockHeight` 자체 삭제는 UIC-05 (복원이 대체).

#### UIC-05 · 창 geometry 와 dock 배치를 종료 시 저장하고 기동 시 복원한다
- 종류: PR | 규모: M | 태그: A, D · feature
- 목표: 모든 `QDockWidget`(outer 5 · inner 3, `onLogIconClicked` 재생성분 포함)에 `setObjectName`, `closeEvent` 에서 `saveGeometry()`·`saveState(version)`(outer·inner 별도 키), 기동 시 `restoreGeometry` 후 오프스크린·최소 크기 검증(어느 화면과도 교차하지 않거나 400×300 미만이면 기본 geometry) → `restoreState` 실패 시 `resetLayout`. main.cpp 의 `primaryScreen()->geometry()×0.8` 은 복원 실패 폴백으로만 남기고 `availableGeometry()` 로 바꾼다. `m_logHeightRatio`·`adjustLogDockHeight` 를 삭제한다(복원이 대체).
- 완료 기준:
  1. 앱을 껐다 켜면 창 위치·크기·dock 배치(floating 포함)가 복원된다 · 저장된 모니터가 없으면 주모니터 작업 영역 80% 로 뜬다
  2. dock 구성을 바꾸고 state version 을 올리면 구버전 저장값이 무시되고 기본 배치로 뜬다
  3. `git grep -E "saveGeometry|saveState|restoreGeometry|restoreState" view/DashMainWindow.cpp` 각 1 이상 · `m_logHeightRatio` 0건 · 모든 `new QDockWidget` 직후 `setObjectName`
- 변경 범위: view/DashMainWindow.h · view/DashMainWindow.cpp · main.cpp
- 선행: UIC-03 (강제 재분배가 남아 있으면 복원값이 덮인다) · PRJ-14 (키 스코프 — UIC DEC 병합)
- 충돌: PR #651 · #652 · #654 · UIC-01 · UIC-09(프레임 모델이 바뀌면 geometry 의미가 바뀌어 version 번프 필요 — 비고) · PRJ DashMainWindow 항목 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashMainWindow.h → 공유 11건(deps.md 5절) · main.cpp → DEV-21 DEV-24 EXE-02 EXE-06 PRJ-06 UIC-26 · PR #655(DashMainWindow.cpp)
- 흡수: #448 · L0-2 · L2-7 · UIC-c05, c06, c08
- 비고: UIC-09 를 먼저 하면 version 번프 1회를 아낀다 — 순서는 UIC-02 결과로 정한다(위키 "순서에 관한 제약" 표). 렌더 dock 이 floating 으로 복원돼 GL 위젯이 재부모화되는 경로는 VTK 가 `paintGL` 에서 스스로 재렌더 — `AA_ShareOpenGLContexts` 불요.

#### UIC-06 · UI Scale 메뉴(QT_SCALE_FACTOR)의 처분을 정한다
- 종류: DEC | 규모: S | 태그: D
- 목표: a(메뉴 제거, OS 표시 배율에 위임) / b(현행 유지 + 한계 명시) / c(`app.setFont` 포인트 배율로 전환, QSS px→em 선행) 중 택일. `QT_SCALE_FACTOR` 는 화면별 DPI 와 곱해지는 전역 상수라 멀티디스플레이 격차를 배수로 키우고 재시작을 요구한다. 권장 a, 차선 b.
- 완료 기준: 결정 기록 — 선택지 · 근거(UIC-02 의 실사용 조사) · a 선택 시 제거 범위(main.cpp:66-72 `QSettings`+`qputenv` 블록 · view/DashMainWindow.cpp:255-275 scaleMenu · `UI/scaleFactor` 키) → 구현은 **UIC-26**
- 변경 범위: -
- 선행: UIC-02 (실사용 여부)
- 충돌: -
- 흡수: #449 · L0-4 · UIC-c22
- 비고: c 는 UIC-15 가 끝난 뒤에만 의미가 있다 — 폰트만 키우면 px 고정 위젯이 안 따라와 지금보다 나빠진다. 검토 #13 반영 — 구현을 변경 범위 괄호에 숨기지 않고 UIC-08(DEC)↔UIC-09(PR) 선례대로 조건부 PR 항목 UIC-26 으로 분리했다(추적 가능성 확보).

#### UIC-07 · 오버레이 3종을 부모 크기에 따라 재배치하고 드래그를 부모 영역으로 클램프한다
- 종류: PR | 규모: M | 태그: D · bug
- 목표: `view/common/DashWidgetHelpers` 에 `clampToParent(QWidget*)` 1개를 두고 — (1) `eventFilter` 의 `m_viewOptionsPositioned` 플래그를 없애 렌더 view options 를 CAD 쪽과 같이 매 resize 재배치(사용자가 옮겼으면 부모 대비 상대 위치를 유지), (2) `DashMorphingBar`·`DashViewOptionsWidget` 의 `mouseMoveEvent` 드래그 결과를 클램프, (3) 메인 창 `moveEvent`/`resizeEvent` 에서 표시 중인 `m_morphingSettings` 를 모핑 바 아래로 재배치.
- 완료 기준:
  1. 렌더 뷰를 최소 크기까지 줄여도 view options·모핑 바가 영역 안에 남는다 · 오버레이를 부모 밖으로 끌어낼 수 없다
  2. 메인 창을 옮기거나 리사이즈하면 열린 모핑 설정 창이 따라온다
  3. `m_viewOptionsPositioned` 0건 · 오버레이 `move(` 호출이 전부 클램프를 거친다
- 변경 범위: view/common/DashWidgetHelpers.h · view/common/DashWidgetHelpers.cpp · view/DashMainWindow.cpp · view/overlay/DashMorphingBar.cpp · view/overlay/DashViewOptionsWidget.cpp
- 선행: UIC-01 (moveEvent 신설을 공유) · **PR #655 머지** (`setupMorphingBar()` 본문을 재작성 — `@@ -2405,11 +2401,6 @@` · `initializeMorphingController()` `@@ -2190,10 +2186,4 @@`. 그 앞에 얹으면 목표 (3) 모핑 설정 창 재배치가 전면 재작업)
- 충돌: PR #654 (DashMainWindow.cpp · 모핑 계열) · UIC-01 · UIC-22 (DashWidgetHelpers) · MOR 의 DashMorphingBar 항목 · REN 의 DashViewOptionsWidget 항목 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashMorphingBar.cpp → DEV-10 MOR-05 MOR-14 · DashWidgetHelpers.cpp → UIC-12 UIC-21 · DashWidgetHelpers.h → UIC-12 UIC-21 · DashViewOptionsWidget.cpp → REN-13 · PR #652(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: L3-4 · L3-5 · L3-6 · UIC-c27, c28, c29
- 비고: 접점 MOR(DashMorphingBar · DashMorphingSettings) · REN(DashViewOptionsWidget). 모핑 설정 창을 독립 `Qt::Tool` 창 대신 렌더 위젯의 자식 오버레이로 바꾸는 대안은 MOR 결정 — 여기서는 추적만.

#### UIC-08 · 프레임리스 창의 OS 위임 경로(A·B)와 착수 여부를 결정한다
- 종류: DEC | 규모: S | 태그: D
- 목표: 경로 A(`startSystemMove/Resize` — 구현 버그만 제거, 스냅·시스템 메뉴 복원 안 됨) vs 경로 B(`Qt::Window` + `WM_NCCALCSIZE`/`WM_NCHITTEST` — OS 창 관리 전부 복원, Windows 전용) 택일과, UIC-01/03/05 로 통증이 줄면 보류할지 결정. 위키 권장은 B(사내 선례 검증 구현 있음, 이 프로젝트는 MSVC/Windows 전용). 창 그림자 충돌 선행 확인은 불성립(그림자는 모핑 바에만) — 확인 목록에서 제외.
- 완료 기준: 결정 기록 — 경로 · 착수/보류 · UIC-05 와의 선후(B 를 먼저 하면 state version 번프 1회 절약)
- 변경 범위: -
- 선행: UIC-02 (상시 증상 vs 치명 발현 우선순위)
- 충돌: -
- 흡수: #450 · L0-5(결정부) · UIC-c26
- 비고: #450 의 Goal 이 "택일 여부 결정" 이므로 DEC 를 분리. 구현은 UIC-09.

#### UIC-09 · 창 프레임 관리를 OS 에 위임한다 — Qt::Window + WM_NCCALCSIZE/WM_NCHITTEST (경로 B)
- 종류: PR | 규모: M | 태그: D, E · refactor
- 목표: `setWindowFlags(Qt::FramelessWindowHint)` 를 `Qt::Window` 로 바꾸고 `nativeEvent(const QByteArray&, void*, qintptr*)`(Qt6) 에서 `WM_NCCALCSIZE`(프레임 0 + 최대화 시 프레임 두께만큼 `InflateRect` 인셋 — 작업 영역 통째 교체 금지) 와 `WM_NCHITTEST`(`ScreenToClient` 후 `/devicePixelRatioF()` 보정, 가장자리→`HT*`, 타이틀바 빈 영역→`HTCAPTION`, 그 외 `HTCLIENT`) 를 처리한다. `getResizeEdge`/`handleResize`/`getCursorForEdge` 와 `m_isResizing`/`m_resizeEdge`/`m_resizeStartPos`/`m_originalGeometry`, `DashTitleBar` 마우스 핸들러 4개와 `m_isDragging`/`m_dragPosition` 를 삭제하고, 히트테스트의 화이트리스트 2벌을 `childAt(pos)` 판정 하나로 바꾼다.
- 완료 기준:
  1. 드래그 중 커서가 타이틀바 같은 지점 유지 · Win+방향키 스냅 · `Alt+Space` 시스템 메뉴 · 작업표시줄 썸네일 우클릭 이동 동작
  2. 최대화 시 작업 영역에 정확히 맞고(자동 숨김 작업표시줄 호출 가능), 배율 다른 모니터에서도 맞는다 · **200% 모니터에서 우측·하단 절반이 리사이즈 영역으로 오판되지 않고 타이틀바 버튼이 클릭된다**
  3. `git grep -E "FramelessWindowHint|getResizeEdge|handleResize|m_dragPosition" view/DashMainWindow.* view/DashTitleBar.*` 0건
- 변경 범위: view/DashMainWindow.h · view/DashMainWindow.cpp · view/DashTitleBar.h · view/DashTitleBar.cpp
- 선행: UIC-08
- 충돌: PR #651 · #652 · #654 · UIC-01(클램프 제거 가능) · UIC-05(state version) · PRJ DashMainWindow·DashTitleBar 항목 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashMainWindow.h → 공유 11건(deps.md 5절) · DashTitleBar.cpp → DEV-10 · PR #655(DashMainWindow.cpp)
- 흡수: #450 · L0-5 · UIC-c25
- 비고: 사내 선례(DashOpti_Analyzer `view/DashMainWindow.cpp` nativeEvent)를 이식하되 결함 3건(최대화 `rcWork` 통째 교체 · 하드코딩 화이트리스트 · `y < height` 만 보는 영역 판정)을 고친다. `WM_GETMINMAXINFO` 와 권한 중복 금지. Qt6 에서 `QMouseEvent::globalPos()` 등 deprecated API 정리는 범위 밖.

#### UIC-10 · 모듈 위젯을 QScrollArea 로 감싸 스택의 최소 크기 전파를 끊는다
- 종류: PR | 규모: M | 태그: D · bug
- 목표: `setupWidgets` 의 `m_rightStackedWidget->addWidget` 13곳을 한 지점에서 `QScrollArea(setWidgetResizable(true))` 래핑으로 바꿔, 보이지 않는 페이지의 `minimumSize/sizeHint` 가 우측 dock 폭을 정하지 못하게 한다. 폭을 미는 실물은 `.ui` 의 컨테이너 `minimumSize` — `ui/DashGeometryParameterWidget.ui:39`(300×30) · `:45`(200×40) · `ui/DashAIGeometryGenerationWidget.ui:130`(250×120) — 이므로 이 셋을 걷어내고, 25/30px 아이콘 버튼 8건(AnalysisLauncher 2 · ModelBuilder 2 · ModelBuilderMCU 2 · Optimizer 2)은 그대로 둔다.
- 완료 기준:
  1. 데이터가 많은 테이블을 로드해도 우측 dock 폭이 튀지 않는다 · 지연 로딩되는 모듈로 전환해도 dock 폭 불변
  2. 모듈 10종 전환 시 우측 dock 최소 폭이 `RIGHT_DOCK_MIN`(550, DashMainWindow.h:390) 과 같다(런타임 `minimumSizeHint` 로그로 확인)
  3. 래핑 루프 1곳 · 우측 스택 13 위젯의 `minimumSizeHint().width()` 가 전부 `RIGHT_DOCK_MIN` 이하 · `ui/` 루트의 `minimumSize` 중 컨테이너 몫 3건 제거(아이콘 버튼 8건 유지)
- 변경 범위: view/DashMainWindow.cpp · ui/DashGeometryParameterWidget.ui · ui/DashAIGeometryGenerationWidget.ui
- 선행: UIC-03 (L0-1 이 남으면 재발) · UIC-02 (지배 요인이 레이아웃/테이블일 때)
- 충돌: PR #651 · #652 · #654 · UIC-03 · 각 모듈의 .ui 변경(BLD·RUN·DOE·OPT 등) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashGeometryParameterWidget.ui → MOR-11 · PR #655(DashGeometryParameterWidget.ui·DashMainWindow.cpp)
- 흡수: #449 · L1-2 · L1-3 · UIC-c19, c20
- 비고: Stage 6. `.ui` 수정이 모듈 영역을 넘으면 점검 결과만 기록하고 수정은 해당 모듈로 넘긴다. 대안(비활성 페이지 sizePolicy `Ignored`)은 전환마다 토글이 필요해 비권장. 검토 #7 반영 — 전 AC3 "최상위 레이아웃 없는 `.ui` 0" 은 HEAD 에서 이미 참(`ui/` 루트 16벌 전부 최상위 `QVBoxLayout`)이라 공허했다. 최상위 geometry(15파일 · 최대 700×800)는 부모 레이아웃이 즉시 덮으므로 AC 에서 빼고 점검 기록으로만 남긴다 — L1-3 의 실효 몫은 `minimumSize` 쪽이다.

#### UIC-11 · 중첩 QMainWindow 를 단일화할지 결정한다
- 종류: DEC | 규모: S | 태그: D, E
- 목표: outer `DashMainWindow` 의 `centralWidget` 이 inner `QMainWindow`(양쪽 `setDockNestingEnabled(true)`)인 구조를 A(단일 QMainWindow + `setCorner`) / B(inner 를 QSplitter) / C(유지 + 상태 분리 저장) 중 택일. 기본 C. UIC-03 뒤에도 프로파일링(UIC-02)에서 이중 패스가 지배 요인일 때만 A.
- 완료 기준: 결정 기록 — 선택 · 근거 프로파일 · A 선택 시 dock 10여 개 재배치 실험 결과
- 변경 범위: -
- 선행: UIC-02 · UIC-03
- 충돌: -
- 흡수: #450 · L1-1 · UIC-c23
- 비고: C 는 UIC-05 가 inner state 를 별도 키로 저장하면 자동 충족. 원천 정정(검토 #14) — L1-1 은 #449 가 아니라 #450("테두리 없는 창과 중첩 메인 윈도우 구조 재검토") 소관. 이 항목이 빠지면 #450 의 절반이 추적에서 누락된다.

#### UIC-12 · 폰트 의존 고정 높이 6곳을 sizeHint 로 바꿔 배율·폰트 변경에 추종시킨다
- 종류: PR | 규모: M | 태그: D · bug
- 목표: `rowCount*26+header`(ShortcutsDialog.cpp:31 · :38) · 행 높이 누적(DashMeshQualityDialog.cpp:54-57) · `verticalHeader()->length()`(DashResultsAnalyzerWidget.cpp:235 `createTextStyleGroup` · DashPlotWidgetFactory.cpp:114-117 파일 static **`fitTableHeight`** — `tableContentHeight`:106-112 를 `setFixedHeight` 로 굳히고 **:234 · :340 · :428 · :1655 네 표에서 호출**) · `fontMetrics().height()*2`(DashResultsAnalyzerWidget.cpp:250 `createPlotButton`) · `idealH`(DashAnalyzerUtils.cpp:115-121 `PlotLegend::draw`) 를 `setFixedHeight` 로 굳히지 않고, `view/common/DashWidgetHelpers` 의 "내용에 맞는 표 높이" 헬퍼(또는 `sizeHint()` 오버라이드)로 Qt 가 필요할 때 다시 묻게 한다. L2-6 의 명시 `screenChanged` 연결은 UIC-02 완료 기준 (2) 의 실측 결과에 따른다.
- 완료 기준:
  1. 배율 100%↔150% 모니터 간 이동 후 단축키 표·메시 품질 표·플롯 텍스트 스타일 표의 내용이 잘리지 않는다
  2. 위 6곳에 `setFixedHeight(` 0건 · `tableContentHeight` 류 private 복제 0 (공용 헬퍼 1개) · `fitTableHeight` 호출 4곳이 전부 헬퍼 경로
  3. 비대상을 건드리지 않는다 — `DashPlotWidgetFactory.cpp` 의 `setMinimumHeight(qMin(calculatedHeight, fontMetrics().height()*8))` 3곳(:842 · :989 · :1401)과 스페이서 `setFixedHeight(0)`/`(1)`(:1122 · :1124) 은 그대로
- 변경 범위: view/common/DashWidgetHelpers.h · view/common/DashWidgetHelpers.cpp · view/dialog/ShortcutsDialog.cpp · view/dialog/DashMeshQualityDialog.cpp · view/DashResultsAnalyzerWidget.cpp · view/analyzer/DashPlotWidgetFactory.cpp · view/analyzer/DashAnalyzerUtils.cpp
- 선행: UIC-03 · UIC-02 (완료 기준 (2) — `screenChanged` 연결 필요 여부)
- 충돌: UIC-07 · UIC-22 (DashWidgetHelpers) · ANA 의 DashResultsAnalyzerWidget·DashPlotWidgetFactory 항목 · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · DashPlotWidgetFactory.cpp → ANA-01 ANA-09 ANA-12 ANA-14 · DashWidgetHelpers.cpp → UIC-21 · DashWidgetHelpers.h → UIC-21 · DashMeshQualityDialog.cpp → MOR-01 UIC-13 · DashAnalyzerUtils.cpp → ANA-12
- 흡수: #449 · L3-2 · L2-6 · UIC-c17, c24
- 비고: 파일 7개 중 3개가 ANA — 기계적이고 작아 1건으로 둔다(접점 ANA). `PlotLegend::draw` 의 `MaxTableHeight` 상한은 유지. 좌표 정정(검토 #11) — `DashPlotWidgetFactory::createTextStyleGroup`:75-78 은 `return parent->createTextStyleGroup();` 한 줄 위임이라 고정 높이가 없다. L2-6 몫은 UIC-02 실측 전까지 임시 판정이다(검토 #15).

#### UIC-13 · 다이얼로그 생성자의 resize 하드코딩 2곳을 제거한다
- 종류: PR | 규모: S | 태그: D · refactor
- 목표: `DashMeshQualityDialog` `resize(550,300)` · `MaterialSetupDialog` `resize(500,450)` 을 지우고 레이아웃 `sizeHint()` 에 맡긴다. 크기 지정이 꼭 필요하면 `availableGeometry()` 상한을 건다.
- 완료 기준: 두 다이얼로그가 내용에 맞는 크기로 뜨고 200% 모니터에서 화면을 넘치지 않는다 · `git grep -nE "^[[:space:]]*resize\(" -- view/dialog` 0건 (착수 전 실행값 2 — `DashMeshQualityDialog.cpp:26` · `MaterialSetupDialog.cpp:48`)
- 변경 범위: view/dialog/DashMeshQualityDialog.cpp · view/dialog/MaterialSetupDialog.cpp
- 선행: -
- 충돌: PRJ 의 view/dialog 항목 · MOR(DashMeshQualityDialog 사용처) · B2 교집합: DashMeshQualityDialog.cpp → MOR-01 UIC-12
- 흡수: #449 · L3-7 · UIC-c16
- 비고: 접점 PRJ(view/dialog 소유). 독립적이라 언제 해도 된다. AC 정정(검토 #6) — 전 AC 의 `^\s*resize\(` 는 git 의 POSIX ERE 에 `\s` 가 없어 현행 2건에도 매치 0·exit 1 이었다(착수 전에도 통과하는 공허한 AC). `-P` 를 쓰면 `\s` 도 동작한다.

#### UIC-14 · 명령형 크기 지정(setFixed* · ResizeToContents · setSizes)의 허용 규칙을 정한다
- 종류: DEC | 규모: S | 태그: D, E
- 목표: `setFixed*` 74곳 35파일 · `ResizeToContents` 82곳 12파일 · `setSizes({상수})` 22곳의 공통 규칙을 docs/coding-convention.md 에 적는다 — (1) 정사각형 아이콘·칩(`DashMetrics` 토큰 크기)은 `setFixedSize` 허용, 컨테이너·텍스트 위젯은 `sizePolicy`+`minimumSize`, 폰트 연동은 `QFontMetrics`/`sizeHint`; (2) 긴 텍스트 열은 `Interactive`+`setDefaultSectionSize`, `ResizeToContents` 는 짧은 고정 어휘 열만; (3) `setSizes` 는 비율(`setStretchFactor`)로. UIC 영역 11곳(view/common 3 · DashTitleBar 5 · DashMainWindow 3)은 전부 정사각형 아이콘이라 규칙상 변경 0.
- 완료 기준: 결정 기록(컨벤션 절) · 모듈별 적용 대상 수 표(setFixed* / ResizeToContents) — OPT 3/32 · RUN 2/24 · BLD 1/15 · ANA 13/3 · MOR 6/3 · CAD 4/0 · DOE 1/1 · view/dialog 18/3 · view/ai 15/1 — 를 Phase B 에 넘김
- 변경 범위: docs/coding-convention.md
- 선행: UIC-03 (L0-1 이 남은 채 개별 위젯을 고치면 되돌아온다) · UIC-10 (전파 차단이 열 정책보다 우선)
- 충돌: B2 교집합: coding-convention.md → DEV-17 UIC-18 UIC-21
- 흡수: #449 · L3-1 · L3-9 · UIC-c15, c18
- 비고: 모듈별 적용은 `범위밖` — 대응표 참조. 기계적이지 않고(판단이 필요) 크므로 1건으로 묶지 않는다.

#### UIC-15 · QSS 의 px 크기 제약을 DashMetrics 토큰·em 으로 옮긴다
- 종류: PR | 규모: S | 태그: D, G · refactor
- 목표: qtheme_light.qss 의 px 크기 제약 42곳을 ① 토큰의 *의미*가 치수를 지배하는 것 → `@Token@`(이미 164곳 토큰화) ② 우연히 토큰과 같은 리터럴 → 그대로 유지 ③ 폰트 추종이 맞는 것 → `em`(현행 4곳) 으로 **3분류한 뒤 ①만 치환**한다. 일괄 치환은 금지 — `view/common/DashMetrics.h` 머리주석이 "A value here is used only where the token's *meaning* governs the dimension. A literal that merely happens to equal a token … keeps its literal." 로 못 박았다. 근거 불명한 `QMenuBar { max-width: 3000px }`(:1308) 는 의도 확인 후 제거. `.ui` 의 `maximumSize` 는 아이콘 버튼이라 유지.
- 완료 기준:
  1. 42곳의 ①②③ 분류표를 기록하고 ① 만 치환 — 남은 리터럴은 ② 또는 ③ 사유가 표에 적혀 있다
  2. `grep -cE "(^|[[:space:]])(min-|max-)?(width|height): *[0-9.]+px" resources/style/qtheme_light.qss` 가 분류표의 ②+③ 건수와 같다 (착수 전 실행값 42)
  3. 100%/150% 에서 위젯 외형 회귀 없음(uipreview 스크린샷 비교)
- 변경 범위: resources/style/qtheme_light.qss · view/common/DashMetrics.h
- 선행: UIC-06 (c 를 택하면 필수, a/b 면 선택) · UIC-14 (①②③ 판단 규칙 — 분류 자체를 명령형 크기 규칙에 합친다)
- 충돌: -
- 흡수: #449 · L3-8 · UIC-c21
- 비고: `tools/uipreview` 로 비교 가능. UIC-06 이 a/b 면 우선순위 최하. AC 정정(검토 #8) — 전 정규식 `(min|max)-(width|height): *[0-9]+px` 는 42 중 9만 세고, 검토가 제안한 `(width|height|min-width|…)` 형태는 `border-*-width: 2px` 4건을 끌어들여 46 이 된다. `(^|[[:space:]])(min-|max-)?(width|height):` 가 정확히 42(= 46−border 4).

#### UIC-16 · 사용자 통지 규칙을 세운다 — 무엇을 모달·dock·무통지로 보낼지
- 종류: DEC | 규모: S | 태그: D
- 목표: docs/unified-logger.md 6절(라우팅)을 확장하거나 별도 문서로 — (1) 시스템 실패(파일·외부 도구·모델 부재)는 `DashNotify::error/warning`(로그+모달), 입력 검증 안내는 모달 없이 인라인/툴팁 또는 `DashNotify::info`, 진행 중 정보는 dock; (2) 확인(question)은 래퍼 `confirm` 으로 통일; (3) 모델·컨트롤러는 팝업 금지 — 시그널로 승격하고 뷰가 통지(현행 위반 7건: DashDoeSampler 5 · DashMorphingController 1 · DashHandlePickingInteraction 1); (4) 성공 통지는 결과를 확인한 뒤 — 사례는 `view/DashModelRunnerWidget.cpp:457-462` **Morphing 분기**(`co_await performMorphingAndAddToFileTable(params)` 뒤 성공·실패 구분 없이 `stopGenerateStatusAnimation("Input file generated.")`). 같은 함수의 Condition 분기 `:578-588` 은 198a294c(#533) 에서 반환값을 보게 고쳐졌으므로 인용하지 않는다; (5) 배치 실행 중 모달 억제; (6) 외부 프로세스 실패 절은 #466(EXE)이 얹는다. 리뷰 게이트로 강제.
- 완료 기준: 결정 기록 — 규칙 문서 · 166건의 분류표를 **파일별 `총건 / 그중 Please 계열`** 2열로(규칙 (1) 분기까지 담아야 모듈별 스윕의 입력이 된다): DashMainWindow 21/2 · DoeSamplerWidget 17/6 · AnalysisLauncherWidget 17/11 · OptimizerWidget 16/3 · GeometryParameterWidget 15/7 · ModelBuilderMCUWidget 14/4 · ModelRunnerMCUWidget 13/6 · ModelBuilderWidget 9/6 · ModelRunnerWidget 7/0 · MorphingSettings 6/6 · DashDoeSampler 5/2 · MaterialSetupDialog 4/2 · TopOptPostprocessDialog 3/2 · DoeSamplerResample 3/1 · 나머지 ≤2 (합계 166 / Please 60) — 를 모듈별 적용 입력으로 Phase B 에 넘김
- 변경 범위: docs/unified-logger.md (또는 docs/notification-policy.md)
- 선행: -
- 충돌: EXE-10 (#466 — 같은 문서, 먼저 착수하는 쪽이 만든다)
- 흡수: #482 · #466(접점) · #370(접점, 사례) · UIC-c36, c37, c38 · UIC-c40(사례 — Condition 분기는 해소됨, 인용 좌표는 Morphing 분기 `DashModelRunnerWidget.cpp:457-462`) · UIC-c56(사례) · DOE-c26 · BLD-c31 · UIC-c59, c60 (모듈 건수 입력 — 스윕은 DOE·BLD)
- 비고: 개별 무통지 결함(#323 #324 #376 #393 #394)은 not-to-be 그대로. `QMessageBox` 166건 중 "Please …" 계열은 규칙 (1) 에서 모달 유지/비모달 전환을 갈라야 한다 — **31건이 아니라 60건(선두 45)** 으로 전체의 3분의 1 이상이다(검토 #5). 규칙 (1) 의 적용 범위와 모듈별 스윕 164건의 비용 추정이 2배로 늘어난다. `view/common/DashNotify.h` 주석("입력 검증 안내는 로그 대상이 아니므로 QMessageBox를 그대로 쓴다")이 현행 설계의 근거이므로 규칙은 이 주석을 바꾸는 결정과 함께 적는다.

#### UIC-17 · DashNotify 래퍼를 규칙에 맞게 확장한다 — info · confirm · 배치 중 억제
- 종류: PR | 규모: S | 태그: D, B · feature
- 목표: `DashNotify` 에 `info(module, parent, title, text)`(로그 INFO + information 박스)와 `confirm(parent, title, text, buttons) -> bool`(question, GUI 스레드 전용), 배치 실행 중 모달을 dock 로그로 강등하는 스코프 가드를 추가한다. 호출부 교체는 하지 않는다(모듈별 적용 항목).
- 완료 기준:
  1. 워커 스레드에서 `info` 호출 시 GUI 스레드로 큐잉되고 호출 스레드가 막히지 않는다(기존 `showBox` 경로 재사용)
  2. 신규 동작의 단위 테스트 — **Widgets 링크 테스트 타깃**(선례 `test_analyzer_utils_cache`, tests/CMakeLists.txt:324-336)에서 ① 억제 스코프 안 팝업 0 · 로그 1 ② `confirm` 이 GUI 스레드 밖 호출에서 거부되거나 큐잉되는 계약
- 변경 범위: view/common/DashNotify.h · view/common/DashNotify.cpp · tests/CMakeLists.txt (새 Widgets 링크 타깃) · tests/ (단위 테스트 1개)
- 선행: UIC-16
- 충돌: B2 교집합: tests/CMakeLists.txt → 공유 12건(deps.md 5절) · PR #655(tests/CMakeLists.txt) · PR #654(tests/CMakeLists.txt) · PR #652(tests/CMakeLists.txt) · PR #651(tests/CMakeLists.txt)
- 흡수: #482 · UIC-c39
- 비고: 모듈별 `QMessageBox` → 래퍼 스윕은 `범위밖`(PRJ 21+11(dialog) · DOE 28 · MOR 24 · BLD 23 · RUN 20 · LCH 18 · OPT 16 · CAD 2 · CON 1 = 164) — 대응표 참조. #490(tr 제거)과 한 스윕으로 묶자던 권고는 UIC-18 이 기계적 단일 PR 이라 더 이상 유효하지 않다. AC 정정(검토 #9) — `DashNotify.cpp` 가 `QMessageBox` 를 직접 호출하므로 "Core 전용 단위 테스트" 는 불가능하고(tests/CMakeLists.txt 의 Widgets 링크 타깃은 `test_analyzer_utils_cache` 하나뿐), "헤드리스에서 로그만" 은 `showBox` 의 기존 `if (!app) return;` 가 이미 보장해 신규 코드의 AC 가 될 수 없다.

#### UIC-18 · tr() 182곳을 제거하고 영어 고정을 규칙으로 못 박는다
- 종류: PR | 규모: L | 태그: G, E · refactor
- 목표: `tr("…")` 182곳 23파일(DashMainWindow 95 · ShortcutsDialog 11 · AnalysisLauncherWidgetLauncher 10 · KPIConfigDialog 9 · GeometryParameterWidget 9 · DashAiPlayerDialog 7 · DashConditionParameterization 7 · DashAnalysisLauncher 5 · DashLogDockWidget 4 · ModelRunnerWidget 4 · DashJobRunner 4 · OptimizerWidget 3 · 나머지 ≤2)를 `QStringLiteral`/리터럴로 바꾼다. `.arg` 체인은 그대로. `.ui` 의 `<string>`(uic translate)은 번역기 없이 원문을 돌려주므로 손대지 않는다. docs/coding-convention.md 에 "tr() 금지" 한 줄.
- 완료 기준: `git grep -E "(^|[^A-Za-z0-9_])tr\(" -- '*.cpp' '*.h' ':!tools' ':!tests'` 0건 · 빌드·tests 통과 · 메시지 문자열 diff 가 래퍼 제거뿐(의미 변경 0)
- 변경 범위: 위 23파일 + docs/coding-convention.md
- 선행: -
- 충돌: PR #651 · #652 (DashMainWindow.cpp · DashAnalysisLauncherWidgetLauncher.cpp · DashAnalysisLauncher.cpp · DashJobRunner.cpp · DashConditionParameterization 제외) · #654 · #655 (DashMainWindow.cpp · DashGeometryParameterWidget.cpp tr 9+1 · DashMorphingSettings.cpp) — **열린 PR 5건 중 머지 대상 4건(#651 · #652 · #654 · #655) 머지 후 착수** (#530 은 머지하지 않아 제외, decisions ②) · B2 교집합: coding-convention.md → DEV-17 UIC-14 UIC-21
- 흡수: #490 · UIC-c43, c44
- 비고: L 사유 — 치환 1종의 기계적 변경이라 모듈별로 나누면 리뷰 비용만 늘고 AC(0건)를 한 번에 검증할 수 없다. 반나절 작업이지만 파일 수 기준으로 L. 재유입 방지 grep 가드(CI)는 DEV 접점.

#### UIC-19 · Mgr()·GetProject()·GetDesignVariableModel() 직후의 도달 불가 null 가드 27건을 제거한다
- 종류: PR | 규모: L | 태그: E · refactor
- 목표: 항상 non-null 인 접근자(`DashManager::Mgr/PrjMgr` lazy new · `GetProject` 생성자 new 재할당 없음 · `GetDesignVariableModel` 동일) 직후의 순수 가드 — Mgr 12건 10파일 · GetProject 11건 3파일 · GetDVM 4건 2파일 — 를 삭제하고 복합 가드(DashDoeSampler 1)는 뒤 항만 남긴다. 고아가 된 로그 문자열·지역 변수만 정리, 주변 리팩터 금지, 파일 단위 커밋.
- 완료 기준: `git grep -A1 -E "= DashManager::(Mgr|PrjMgr)\(\);|GetProject\(\);|GetDesignVariableModel\(\);" -- '*.cpp' | grep -E "if *\(![a-zA-Z_]+\)"` 0건 · 빌드·tests 통과
- 변경 범위: view/DashMainWindow.cpp · view/DashGeometryParameterCADWidget.cpp · view/DashConditionParameterizationWidget.cpp · view/DashProjectWidget.cpp · controller/DashAnalysisModelContextRegistry.cpp · model/DashModelRunner.cpp · model/DashDoeSampler.cpp · model/DashJobRunnerFeSafe.cpp · model/DashJobRunnerAnsysMechanical.cpp · model/DashJobRunnerAnsysJournal.cpp · model/DashJobRunnerAbaqus.cpp
- 선행: -
- 충돌: PR #651 · #652 · #654 · #655 (DashMainWindow.cpp · DashDoeSampler.cpp · DashManager) · UIC-20(같은 파일 다수 — 연속 작업) · **CON-04 — 설계 충돌**(단순 파일 교집합이 아니다): CON-04 의 `GetProject` null 가드 신설은 **기각**이고(도달 불가), 같은 파일 `view/DashConditionParameterizationWidget.cpp` 에 뒤로 랜딩하면 이 항목의 완료 기준(해당 가드 0건)을 깬다. CON-04 에는 QPointer 2곳과 `:370-371` 쪽 실제 무가드 역참조만 남는다 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashGeometryParameterCADWidget.cpp → 공유 10건(deps.md 5절) · DashConditionParameterizationWidget.cpp → CON-03 CON-05 CON-06 CON-07 CON-12 DOE-19 · DashJobRunnerAnsysJournal.cpp → CAD-01 LCH-06 LCH-07 LCH-14 LCH-27 LCH-29 · DashAnalysisModelContextRegistry.cpp → EXE-22 PRJ-03 REN-01 REN-02 REN-07 · DashJobRunnerFeSafe.cpp → LCH-07 LCH-14 LCH-18 LCH-30 PRJ-14 · DashJobRunnerAbaqus.cpp → LCH-02 LCH-07 · DashJobRunnerAnsysMechanical.cpp → LCH-02 LCH-07 · DashProjectWidget.cpp → DEV-10 PRJ-33
- 흡수: #508 · UIC-c46, c47, c48
- 비고: `GetIOController()` 는 프로젝트 열기 전 null 이라 대상 아님(113건 그대로). 규모 정정(검토 #12) — 파일 11개로 M 상한(8)을 넘으니 `L`. L 사유는 UIC-20 과 같다: 삭제 1종의 기계적 변경이고 AC 가 레포 전체 0건이라 쪼개면 검증이 쪼개진다(파일당 1~3줄 삭제 · 파일 단위 커밋). **decisions ⑦ 확정** — CON-04 ↔ UIC-19 는 UIC-19 가 맞다. `DashProjectManager` ctor 가 `m_project = new DashProject()` 로 1회 할당하고 재할당이 없으며(`:26-28`), `GetProject()` 는 `return m_project` 뿐(`:45-48`), `CloseProject()` 도 `SetProjectPath(QString())` 로 내용만 비운다(`:239`) → 항상 non-null 이므로 CON-04 의 가드 신설은 기각한다.

#### UIC-20 · DashProjectManager::Instance() 직후의 도달 불가 null 가드 116건을 제거한다
- 종류: PR | 규모: L | 태그: E · refactor
- 목표: 순수 가드 103건 22파일(변경 범위에 전건 열거 — DashModelBuilder 15 · DashModelRunner 14 · DashDoeSampler 12 · DashProject 11 · DashOptimizer 9 · ResultsAnalyzerWidget 6 · DashModelBuilderMCU 6 · ModelBuilderMCUWidget 5 · ModelRunnerWidget 3 · ModelRunnerMCUWidget 3 · CAD·GeometryParameter·ConditionParameterization 모델 각 3 · 나머지 ≤2)을 삭제하고 복합 가드 13건(ResultsAnalyzerWidget 5 · AnalysisLauncherKPI 5 · AnalysisLauncher 2 · JobRunner 1)은 `IsProjectOpen()`/`GetIOController()` 항만 남긴다. 접근자 체이닝으로 불필요해진 지역 변수 제거. 파일 단위 커밋.
- 완료 기준: `git grep -A1 "= DashProjectManager::Instance();" -- '*.cpp' | grep -E "if *\(![a-zA-Z_]+\)"` 0건 · 복합 가드의 앞 항 0건 · 빌드·tests 통과
- 변경 범위: **23파일** — model/ 13: DashModelBuilder.cpp 15 · DashModelRunner.cpp 14 · DashDoeSampler.cpp 12 · DashProject.cpp 11 · DashOptimizer.cpp 9 · DashModelBuilderMCU.cpp 6 · DashConditionParameterization.cpp 3 · DashGeometryParameter.cpp 3 · DashGeometryParameterCAD.cpp 3 · DashAnalysisLaunchExecutor.cpp 1 · DashAnalysisLauncher.cpp 1+2(복합) · DashJobRunner.cpp 1+1(복합) · DashAnalysisLauncherKPI.cpp 0+5(복합) / view/ 10: DashResultsAnalyzerWidget.cpp 6+5(복합) · DashModelBuilderMCUWidget.cpp 5 · DashModelRunnerMCUWidget.cpp 3 · DashModelRunnerWidget.cpp 3 · DashModelBuilderWidget.cpp 2 · DashConditionParameterizationWidget.cpp 1 · DashDoeSamplerResampleWidget.cpp 1 · DashDoeSamplerWidget.cpp 1 · DashGeometryParameterWidget.cpp 1 · DashOptimizerWidget.cpp 1
- 선행: -
- 충돌: PR #651 · #652 (DashProject.cpp · DashDoeSampler.cpp · DashAnalysisLauncher.cpp · DashJobRunner.cpp) · #654 · #655 · UIC-19 — **열린 PR 머지 후 착수** (#530 은 머지하지 않아 제외, decisions ②) · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelBuilderWidget.cpp → 공유 10건(deps.md 5절) · DashAnalysisLaunchExecutor.cpp → LCH-06 LCH-07 LCH-14 LCH-16 LCH-28 LCH-34 PRJ-09 · DashConditionParameterizationWidget.cpp → CON-03 CON-05 CON-06 CON-07 CON-12 DOE-19 · DashGeometryParameterWidget.cpp → DEV-10 MOR-01 MOR-02 MOR-03 MOR-17 MOR-22 MOR-23 · DashModelBuilderMCU.cpp → BLD-01 BLD-10 BLD-12 BLD-13 BLD-17 BLD-18 PRJ-09 · DashJobRunner.cpp → LCH-02 LCH-03 LCH-07 LCH-13 LCH-14 PRJ-09 · DashAnalysisLauncherKPI.cpp → PRE-11 PRE-12 PRE-21 PRE-22 PRJ-09 · DashConditionParameterization.cpp → CON-01 CON-02 CON-05 CON-06 PRJ-09 · DashDoeSamplerWidget.cpp → DOE-05 DOE-06 DOE-09 DOE-11 DOE-13 · DashGeometryParameterCAD.cpp → CAD-03 CAD-05 CAD-06 CAD-09 PRJ-09 · DashDoeSamplerResampleWidget.cpp → DOE-02 DOE-20 · DashGeometryParameter.cpp → MOR-11 PRJ-09 · DashModelRunnerMCUWidget.cpp → RUN-22 UIC-23 · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp)
- 흡수: #508 · UIC-c45 · DOE-c27 · UIC-c61 (DOE 집계 — 규칙이 달라 착수 시 재집계)
- 비고: L 사유 — 삭제 1종의 기계적 변경, 이슈 본문이 "파일 단위 커밋(리뷰 단위)" 을 이미 정했고 AC 가 레포 전체 0건이라 분할하면 검증이 쪼개진다. 모듈별 분할이 필요하면 model/ 과 view/ 두 PR 로. 범위 정정(검토 #12) — 전 표기 "26파일(model 15 · view 11)" 은 실측과 다르다. 순수 가드 22파일(model 12 · view 10) ∪ 복합 가드 4파일(신규는 `model/DashAnalysisLauncherKPI.cpp` 1벌) = **23파일(model 13 · view 10)**. `01-sources/open_issues/508.md` 가 집중 파일로 든 `DashDataProcessor.cpp 17` 은 dev 에 그 파일이 없어 소멸.

#### UIC-21 · QLineEdit 숫자 입력에 범위 검증기와 허용 범위 툴팁을 공용 헬퍼로 적용한다
- 종류: PR | 규모: M | 태그: D · feature
- 목표: `view/common/DashWidgetHelpers` 에 `applyNumericRange(QLineEdit*, double min, double max, int decimals)`(`QDoubleValidator` + 범위 툴팁 + placeholder) 를 두고, **`QLineEdit` 을 파싱하는 5줄(7회) 1파일** — `DashModelBuilderWidgetBase::getModelConfiguration` `:337`(`toInt`) · `:342`(`toDouble`) · `:348`(`toFloat`) · `:355`(`toInt` ×2, int_range) · `:359`(`toFloat` ×2, float_range) — 에 적용한다. `QSpinBox` 계열은 위젯이 범위를 강제하므로 툴팁 규칙만 컨벤션에 적는다. 기존 `DashFeConditionValueDelegate` 의 검증기는 그대로.
- 완료 기준:
  1. 위 5줄 모두 범위 밖·비숫자 입력이 들어가지 않고 툴팁에 허용 범위가 보인다
  2. 착수 시 `git grep -nE "text\(\)\.to(Int|Double|Float)\(" -- view/` 전수 재집계로 누락 0 (정규식에 `toFloat\(` 포함 — 전 AC 의 `toDouble\(|toInt\(` 는 `:348`·`:359` 를 놓쳤다) · 헬퍼 단위 테스트 1개(Widgets 링크 테스트 타깃)
- 변경 범위: view/common/DashWidgetHelpers.h · view/common/DashWidgetHelpers.cpp · view/DashModelBuilderWidgetBase.cpp · docs/coding-convention.md · tests/
- 선행: UIC-16 (검증 실패 안내가 모달인지 인라인인지)
- 충돌: UIC-07 · UIC-12 · UIC-22 (DashWidgetHelpers) · B2 교집합: DashModelBuilderWidgetBase.cpp → BLD-02 BLD-05 BLD-06 BLD-07 BLD-13 · coding-convention.md → DEV-17 UIC-14 UIC-18
- 흡수: #487 · UIC-c41(a — `QLineEdit` 경로)
- 비고: 이슈가 "모듈별 상시 확산" 이라 했으나 현재 대상이 1파일 5줄이라 1건. 범위 축소(검토 #10) — 전 대상 "6곳 3파일" 중 3곳은 `QLineEdit` 이 아니라 **표 셀**(`DashDoeSamplerResampleWidget.cpp:300-309` 2곳 · `DashOptimizerWidget.cpp:1519-1522` 1곳)로 `QTableWidgetItem::text()` 를 파싱한다 — `applyNumericRange(QLineEdit*, …)` 로 손댈 수 없고 아이템 델리게이트(선례 `DashFeConditionValueDelegate.cpp:102-109`)가 필요한 다른 기제다. 그 3곳은 `범위밖` 으로 분리 → **보류: DOE(Resample 2) · OPT(1) 몫** (델리게이트 항목 신설은 각 모듈 판단). `QUndoStack` 0건(UIC-c42)은 요구 이슈가 없어 항목 없음.

#### UIC-22 · 표 셀 위젯의 현재 행을 해석하는 공용 헬퍼를 만들고 기존 private 헬퍼 2개를 흡수한다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: `view/common/DashWidgetHelpers.h` 에 `int tableRowOfCellWidget(const QTableWidget*, const QWidget*)` — 행·열을 훑어 `cellWidget(r,c) == widget || cellWidget->isAncestorOf(widget)` 이면 `r`, 못 찾으면 `-1`. `DashOptimizerWidget::constraintRowOfWidget`(#419) · `DashMorphingSettings::physicsRowOfWidget`(#505) 을 삭제하고 호출부를 교체한다. 동작 불변.
- 완료 기준:
  1. `git grep -n "RowOfWidget" view` 0건 · 헬퍼 호출 ≥ 3 (Optimizer 1 · MorphingSettings 2)
  2. 헬퍼 단위 테스트 — 셀 위젯 직접 / 자손 / 미등록 위젯 / 중간 행 삭제 후 — Widgets 링크 테스트 타깃(선례 test_analyzer_utils_cache)
- 변경 범위: view/common/DashWidgetHelpers.h · view/common/DashWidgetHelpers.cpp · view/DashOptimizerWidget.h · view/DashOptimizerWidget.cpp · view/overlay/DashMorphingSettings.h · view/overlay/DashMorphingSettings.cpp · tests/CMakeLists.txt · tests/(신규 1)
- 선행: **PR #655 머지** (`view/overlay/DashMorphingSettings.{cpp,h}` −213/−21 본문과 `tests/CMakeLists.txt` +18/−18 을 재작성. 그 앞에 얹으면 호출부 교체가 전면 재작업)
- 충돌: PR #654 (모핑 계열) · UIC-07 · UIC-12 · UIC-21 (DashWidgetHelpers) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · tests/CMakeLists.txt → 공유 12건(deps.md 5절) · DashOptimizerWidget.h → OPT-01 OPT-05 OPT-06 OPT-13 OPT-18 OPT-21 OPT-22 PRJ-25 · DashMorphingSettings.cpp → MOR-05 MOR-12 MOR-23 · DashMorphingSettings.h → MOR-05 MOR-12 · PR #652(tests/CMakeLists.txt) · PR #651(tests/CMakeLists.txt)
- 흡수: #514(Phase 1 · Phase 5) · UIC-c54
- 비고: #505 가 머지돼 Phase 5 를 뒤로 미룰 사유가 사라졌다 — 헬퍼 신설과 흡수를 한 PR 로. 방안 C(공용 자유 함수) 채택 근거는 이슈 본문 그대로: 대상 중 browse 버튼은 셀 위젯의 자손이라 `indexAt(pos())` 가 성립하지 않는다. **#655 로 흡수 전제는 생존**(검토 #1 확인) — `gh pr diff 655` 에 `RowOfWidget` 0건이고 `DashMorphingSettings.cpp` 의 마지막 hunk 가 `:1293` 대에서 끝나 `physicsRowOfWidget`(`:1735` 정의 · `:1775` · `:1786` 호출)과 `DashOptimizerWidget::constraintRowOfWidget`(`:2093` 호출)은 그대로다. 선행으로 둔 것은 같은 파일 본문이 재작성되기 때문.

#### UIC-23 · MCU 데이터셋 표 browse 버튼 2곳이 캡처한 행 대신 호출 시점의 행을 쓰게 한다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: `DashModelRunnerMCUWidget::addDatasetFileRow` · `DashModelBuilderMCUWidget::addDatasetFileRow` 의 `[this, row]` 람다가 버튼 포인터를 캡처하고 `tableRowOfCellWidget` 로 해석, `-1` 이면 파일 다이얼로그 전에 반환한다. 라디오 ID 재부여 루프는 별개 계약 — 건드리지 않는다. 같은 함수의 modeCombo(위젯 아이덴티티)와 규칙이 하나가 된다.
- 완료 기준: 두 표 각각에서 중간 행을 지운 뒤 아래 행의 browse 를 누르면 그 행에 경로가 기록되고 "Invalid file widget at row N" 이 뜨지 않는다 · 두 함수에 `[this, row]` 0건
- 변경 범위: view/DashModelRunnerMCUWidget.cpp · view/DashModelBuilderMCUWidget.cpp
- 선행: UIC-22
- 충돌: RUN-22 (DashModelRunnerMCUWidget) · BLD-01 · BLD-09 · BLD-10 · BLD-12 · BLD-13 · BLD-17 (DashModelBuilderMCUWidget) · B2 교집합: DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelRunnerMCUWidget.cpp → UIC-20
- 흡수: #514-2 · #514-3 · BLD-D10 · #474(BLD-D10 축) · UIC-c50, c51 · BLD-c18 · BLD-c35 · RUN-c14 (BLD-08 병합, B2)
- 비고: BLD-08 과 병합(B2 — 같은 함수를 같은 방식으로). #514-1(Reference File 표)은 #617 에서 파일이 사라져 해소, #514-4(Direct 입력 케이스 표)는 PR #652 가 표를 삭제해 머지 시 소멸 — 둘 다 항목 없음. 접점 RUN·BLD.

#### UIC-24 · Model Runner 파일 표 Preview 의 죽은 row 인자를 제거한다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `onFilePreviewClicked(int row, …)` · `performPreviewLogic(int row, …)` 에서 쓰이지 않는 `row` 를 빼고(자기 재귀 포함), `createFileTableRow` 의 람다 캡처를 `[this, filePath]` 로 줄인다. 행 삭제 뒤 Preview 가 다른 케이스를 열 가능성(잠복)을 구조적으로 없앤다.
- 완료 기준: `DashModelRunnerWidget.h` 의 두 시그니처에 `row` 없음 · 행 삭제 후 Preview 가 누른 행의 파일을 연다 · 빌드 통과
- 변경 범위: view/DashModelRunnerWidget.h · view/DashModelRunnerWidget.cpp
- 선행: -
- 충돌: **RUN-24 (같은 함수 — UIC-24 를 먼저)** · RUN 의 나머지 DashModelRunnerWidget 항목 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunnerWidget.h → PRJ-25 RUN-09 RUN-15 RUN-28 RUN-29 RUN-30
- 흡수: #514-5 · RUN-D22 · UIC-c53 · RUN-c37 · UIC-c62
- 비고: 접점 RUN. `[X]` 버튼은 이미 `indexAt` 재계산 — 유지. **decisions ⑦ 확정** — RUN-24 와 같은 함수 본문(`performPreviewLogic` :1448-1557)을 만지고 **순서는 UIC-24 가 먼저**다: UIC-24 가 시그니처(`int row` 삭제, `.h:53`·`:185`)와 자기 재귀(`:1465`)·람다 캡처(`:2006`)를 바꾸므로 먼저 랜딩해야 RUN-24 가 좁아진 시그니처 위에서 작업한다. RUN 쪽 대칭 기재는 `보류: RUN 몫`.

#### UIC-25 · #446 을 닫는다 — 추적 부모, 실작업 없음
- 종류: CLOSE | 규모: S | 태그: D
- 목표: 하위 #447~#450 이 UIC-01~03 · 05~15 · 26 으로 분해됐고 부모에 고유 작업이 없다.
- 완료 기준: 닫기 사유 — "서브 이슈 4건이 새 목록 항목으로 대체됨. Qt6 전환으로 L0-3(rounding policy)은 소멸"
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #446 · UIC-c01
- 비고: -

#### UIC-26 · UI Scale 메뉴와 QT_SCALE_FACTOR 경로를 제거한다 (UIC-06 이 a 를 택할 때)
- 종류: PR | 규모: S | 태그: D, G · refactor
- 목표: `main.cpp:66-72` 의 `QSettings("NohLab","DashOptiAnalyzer")` → `UI/scaleFactor` → `qputenv("QT_SCALE_FACTOR", …)` 블록과 `view/DashMainWindow.cpp:255-275` 의 `scaleMenu`(70~130% 액션 + 재시작 안내 `QMessageBox::information`)를 지우고 표시 배율을 OS 에 맡긴다. `UI/scaleFactor` 키는 더 쓰지 않는다.
- 완료 기준:
  1. `git grep -n "QT_SCALE_FACTOR\|scaleMenu\|UI/scaleFactor" -- main.cpp view/` 0건 (착수 전 실행값 6)
  2. 150% 모니터에서 위젯 크기가 OS 배율만 따르고 재시작 안내 팝업이 뜨지 않는다
- 변경 범위: main.cpp · view/DashMainWindow.cpp
- 선행: UIC-06 (a 결정 — b/c 를 택하면 이 항목은 소멸)
- 충돌: PR #651 · #652 · #654 · #655 (DashMainWindow.cpp) · UIC-05(main.cpp — 같은 브랜치에 실어도 됨) · PRJ-14 (`UI/scaleFactor` 키) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · main.cpp → DEV-21 DEV-24 EXE-02 EXE-06 PRJ-06
- 흡수: #449 · L0-4(구현부) · UIC-c22
- 비고: 검토 #13 반영 — 전에는 이 구현이 UIC-06 의 `변경 범위` 괄호에만 적혀 추적되지 않는 PR 이었다. UIC-08(DEC)↔UIC-09(PR) 선례에 맞춰 분리했다. UIC-06 이 c(폰트 배율 전환)를 택하면 이 항목 대신 UIC-15 가 선행이 된다.

### DEV — 개발 환경 · 빌드 · CI · 출고

> dev @ b08a91b3. 담당 이슈의 열린 PR 없음. 열린 PR 7건 중 머지 대상 6건(#651 #652 #654 #655 #656 #658, decisions ⑩ — #530 은 재업로드 노선이라 제외) 가운데 DEV 파일을 만지는 것: #655(tests/CMakeLists.txt · docs/test-levels.md · DashGeometryParameterWidget.cpp −1,722줄 4파일 분할 · DashMainWindow.cpp) · #654(CMakeLists.txt · tests/CMakeLists.txt · vcpkg-configuration.json · docs/test-levels.md · DashGeometryParameterWidget.cpp · DashMainWindow.cpp · DashMorphingBar.cpp) · #652(tests/CMakeLists.txt · DashMainWindow.cpp) · #651(tests/CMakeLists.txt · DashMainWindow.cpp · DashModelingTreeWidget.cpp). #530 은 머지하지 않으므로(C-2 결정 ②) 충돌·선행에서 뺀다. #655 는 base 가 `refactor/332-handle-state-integration` 인 스택 PR 이라 #654 뒤에 온다. CI 는 아직 없다 — #372 계열은 DEV-14 → 15 → 16 순.
> Phase B1 흡수(범위밖 이관, DEV-c38): PRE-c58(#411 결정 1, vtkIOHDF 가용 여부) → DEV-25(신규 INV).
>
> **공통 제약 (소스 파일을 고치는 전 항목 — DEV-10 · DEV-19 는 제외하고 DEV-20 · DEV-21 · DEV-22 · DEV-24 에 그대로 걸린다)**: pre-commit 훅이 스테이지된 C/C++ 파일 **전체**의 `.clang-format` 일치를 요구하는데(`scripts/hooks/run-format-checks.sh:7`) 저장소는 97% 미포맷이다(`:19`, PR #329). 한 줄만 고쳐도 파일 전체 재포맷 diff 가 따라오므로 **파일별로 "재포맷 커밋 → 변경 커밋" 2단**으로 간다. 한두 줄만 고치는 DEV-20(`TopOptPostprocessDialog.cpp`)·DEV-22(`AboutDialog.cpp`)는 이걸 안 하면 변경이 재포맷에 완전히 묻힌다.

#### DEV-01 · VS/MSVC 버전 운영 정책을 넷 중 하나로 확정한다
- 종류: DEC | 규모: S | 태그: F · docs
- 목표: MSVC 상향이 vcpkg `triplet_abi` 를 바꿔 캐시 전량 miss 가 되는 문제에 대해 A(전원 상향) · B(영구 고정 + 오프라인 레이아웃) · C(구 환경 병행 공급) · D(triplet abi 하위 호환) 중 하나를 고르고 근거·유지 비용·해제 조건을 기록한다. 어느 쪽이든 결정 전까지 18.9.2 고정은 유지한다.
- 완료 기준: 결정 기록(docs/development-environment-setup.md 2.1 또는 README Prerequisites 에 정책 1문단) · 선택지에 따른 후속 항목(DEV-02 상시 · DEV-03 은 C/D 일 때만) 확정
- 변경 범위: README.md · docs/development-environment-setup.md (기록만)
- 선행: -
- 충돌: B2 교집합: README.md → DEV-02 DEV-12 DEV-21 DEV-24 MOR-07 · development-environment-setup.md → DEV-02 DEV-12
- 흡수: #330 · DEV-c01, c02, c03, c04, c05
- 비고: 이슈 본문 권고는 B. D 는 레지스트리·메타 저장소 triplet 정본을 바꾸는 EXT 이고 ABI 위험을 CI 가 잡는다는 전제가 필요하다.

#### DEV-02 · VS 18.9.2 오프라인 설치 레이아웃을 보관하고 README 의 부트스트래퍼 TODO 를 대체한다
- 종류: PR | 규모: S | 태그: F, G · docs
- 목표: `--layout` 으로 18.9.2 + MSVC 14.51.36231 레이아웃을 떠 툴체인 버킷에 올리고, README 의 "fixed-version 부트스트래퍼" 항목과 TODO 를 레이아웃 경로·설치 명령으로 바꾼다. setup-environment.ps1 의 FAIL 메시지가 그 레이아웃을 안내하게 한다.
- 완료 기준: 1. README.md:25-27 TODO 블록 제거, 레이아웃 경로·`vs_setup --noweb` 계열 설치 명령 기재 2. 새 PC 에서 레이아웃만으로 setup-environment.ps1 `Visual Studio` 항목 OK 3. 레이아웃 산출 명령이 문서에 남아 다음 버전에서 재현 가능
- 변경 범위: README.md · scripts/setup-environment.ps1 · docs/development-environment-setup.md
- 선행: -
- 충돌: B2 교집합: README.md → DEV-01 DEV-12 DEV-21 DEV-24 MOR-07 · development-environment-setup.md → DEV-01 DEV-12
- 흡수: #330 · DEV-c06
- 비고: **DEV-01 과 무관하다** — 이슈 Must Know 가 "정책과 무관하게 지금 버전의 layout 을 따 놔야 한다" 로 못 박은 즉시 조치다. 정책이 A(전원 상향)로 가도 18.9.2 레이아웃은 과거 빌드 재현용으로 남는다. 레이아웃 업로드 자체는 버킷 쓰기 권한(CI 서비스 계정) 이 필요한 ops — 저장소 변경은 문서·스크립트뿐.

#### DEV-03 · 선택된 정책(C 또는 D)을 레지스트리·메타 저장소에 구현한다
- 종류: EXT | 규모: M | 태그: F
- 목표: DEV-01 이 C(구 환경 병행 공급) 또는 D(abi 하위 호환 triplet) 를 고르면 DashOpti_Registry CI 또는 메타 저장소 `DashOpti` 의 custom triplet 을 바꾸고 캐시를 재워밍한다. A/B 면 이 항목은 닫는다.
- 완료 기준: 외부 저장소 PR + GUI 쪽 triplets/x64-windows-dashopti.cmake 동기(필요 시 1줄) · `local-msvc-release` 콜드 configure 캐시 히트
- 변경 범위: (외부) DashOpti_Registry · DashOpti 메타 · (GUI) triplets/x64-windows-dashopti.cmake
- 선행: DEV-01
- 충돌: PR #654(vcpkg-configuration.json 변경 — baseline 범프와 순서 조율)
- 흡수: #330 · DEV-c04, c05
- 비고: GUI 는 추적만.

#### DEV-04 · mesh-ops portfile 의 intel-mkl 핀 주석을 현재 사실로 고친다
- 종류: EXT | 규모: S | 태그: F · docs
- 목표: `ports/mesh-ops/portfile.cmake` 의 "2023.2.0 핀 필수 · 실패는 빌드 오류" 주석을 삭제하거나 "핀 없음 · 캐시는 2025.2.0#1" 로 갱신한다.
- 완료 기준: 외부 저장소 PR(DashOpti_Registry) 1줄
- 변경 범위: (외부) DashOpti_Registry ports/mesh-ops/portfile.cmake
- 선행: -
- 충돌: -
- 흡수: #335-1 · DEV-c07
- 비고: GUI vcpkg.json 에 intel-mkl 핀이 없으므로 GUI 측 변경 없음.

#### DEV-05 · mesh-ops 2026-09-07.0 의 재작성된 git-tree 를 처분한다
- 종류: EXT | 규모: S | 태그: F, A
- 목표: versions DB 의 `2026-09-07.0` 을 (a) 제거 (b) 올바른 tree(`954d73eae3d3`) 로 되돌림 (c) baseline `46e3915` 사용 금지 공지 중 하나로 처리한다.
- 완료 기준: 외부 저장소 PR 또는 공지 기록 · GUI baseline(`c80fb330`) 이 영향 밖임을 확인한 메모
- 변경 범위: (외부) DashOpti_Registry versions/
- 선행: -
- 충돌: -
- 흡수: #335-2 · DEV-c08
- 비고: GUI 는 추적만.

#### DEV-06 · preprocessor 를 메타 저장소에 등록하고 GUI 의 feature 선택을 정본에 맞춘다
- 종류: EXT | 규모: S | 태그: F
- 목표: 메타 `repos.json`·`vcpkg.json` 에 `preprocessor` 를 등록해 feature 정본과 CI 교차 검증을 만들고, 확정된 feature 로 GUI vcpkg.json 의 `preprocessor` 항목(현재 `["test"]` 유추값)을 맞춘다.
- 완료 기준: 외부 저장소 PR · GUI vcpkg.json 1줄 동기 · `--only-binarycaching` 콜드 configure 히트
- 변경 범위: (외부) DashOpti 메타 · (GUI) vcpkg.json
- 선행: -
- 충돌: B2 교집합: vcpkg.json → DEV-21 · PR #658(vcpkg.json)
- 흡수: #335-3 · DEV-c09
- 비고: feature 가 어긋나면 ABI 해시가 달라 hard fail — GUI 동기가 같은 PR 묶음이어야 한다.

#### DEV-07 · 현장 Abaqus 지원 버전을 확정한다
- 종류: DEC | 규모: S | 태그: F
- 목표: 2024 만 / 2020+2024 중 공급 대상을 정한다. 러너 디스크·Abaqus 라이선스 제약을 같이 확인한다.
- 완료 기준: 결정 기록(#335 코멘트 또는 레지스트리 docs)
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #335-4 · DEV-c10
- 비고: DEV-08 의 선행.

#### DEV-08 · SSOT 러너에 Abaqus 2024 SDK 스냅샷을 두고 preprocessor 포트를 2024 포함으로 재발급한다
- 종류: EXT | 규모: M | 태그: F
- 목표: 러너에 `win_b64/code/{include,lib}` 스냅샷 배치 → 포트 `DASH_PR_ABAQUS_VERSIONS "2020;2024"` + `ABAQUS_BASE_DIR_2024` → 새 버전 발급·캐시 재워밍 → portfile 주석 갱신 → GUI baseline 범프.
- 완료 기준: 외부 저장소 PR · GUI 빌드 `bin/` 에 `Preprocessor_Abaqus_V2024.dll` 도착 · vcpkg-configuration.json baseline 1줄 범프
- 변경 범위: (외부) DashOpti_Registry ports/preprocessor · (GUI) vcpkg-configuration.json
- 선행: DEV-07
- 충돌: PR #654(vcpkg-configuration.json) · B2 교집합: PR #658(vcpkg-configuration.json)
- 흡수: #335-4 · DEV-c10
- 비고: GUI 는 추적 + baseline 범프만.

> **DEV-09 — 결번.** external/ 폐기의 저장소 변경이 `docs/scratchpad/build-environment.md` 1건뿐이고 DEV-12 가 같은 파일을 `docs/build-environment.md` 로 옮긴다 — 개념상 하나(= 그 파일의 최종 상태)인데 잘게 나뉘어 있었다(00-plan 1-2). **DEV-12 에 병합**(#336-1 · DEV-c11). 확인 불가한 완료 기준(공지 발송 · 클린 빌드 1회)은 DEV-12 비고의 선행 ops 로 내렸다. 번호는 재사용하지 않는다.

#### DEV-10 · Qt6 deprecated globalPos() 남은 곳을 globalPosition() 으로 바꾼다
- 종류: PR | 규모: M | 태그: F · refactor
- 목표: 실코드를 `globalPosition().toPoint()`(정수 좌표 필요처) 로, DashMorphingBar.cpp:125 의 주석 코드는 삭제한다. 동작 불변. 현재 14곳(실코드 13 + 주석 1) 중 2곳은 PR #655 가 먼저 치운다 — **착수 시점 대상은 12곳(실코드 11 + 주석 1)**.
- 완료 기준: 1. `git grep -n "globalPos()" -- '*.cpp' '*.h'` 0건 2. 빌드 경고에 `globalPos` deprecated 0건 3. 창 드래그·리사이즈(DashTitleBar·DashMainWindow)·트리 컨텍스트 메뉴·플롯 툴팁 수동 확인
- 변경 범위: view/DashMainWindow.cpp · view/DashModelingTreeWidget.cpp · view/DashProjectWidget.cpp · view/DashTitleBar.cpp · view/analyzer/DashScatter2DWidget.cpp · view/analyzer/DashShapDependenceWidget.cpp · view/overlay/DashMorphingBar.cpp · (#655 미머지 시에만) view/DashGeometryParameterWidget.cpp
- 선행: PR #655 머지 (`DashGeometryParameterWidget.cpp:2146·2150` 을 `view/common/DashHandleTree.cpp` 로 옮기면서 이미 `globalPosition()` 으로 바꾼다 — 먼저 손대면 1,722줄 삭제와 정면 충돌하고 치환이 버려진다), PR #654·#652·#651 머지
- 충돌: PR #655(DashGeometryParameterWidget.cpp · DashMainWindow.cpp) · #654(DashGeometryParameterWidget.cpp · DashMainWindow.cpp · DashMorphingBar.cpp) · #651(DashModelingTreeWidget.cpp · DashMainWindow.cpp) · #652(DashMainWindow.cpp) · UIC 의 창·DPI 항목(DashTitleBar · DashMainWindow resize 경로) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashGeometryParameterWidget.cpp → MOR-01 MOR-02 MOR-03 MOR-17 MOR-22 MOR-23 UIC-20 · DashMorphingBar.cpp → MOR-05 MOR-14 UIC-07 · DashModelingTreeWidget.cpp → PRJ-04 REN-12 · DashProjectWidget.cpp → PRJ-33 UIC-19 · DashTitleBar.cpp → UIC-09
- 흡수: #336-2 · DEV-c12
- 비고: #321 이 머지돼 순서 제약은 사라졌다. clang-format 공통 제약(파일 머리말)이 그대로 걸리므로 파일별 "재포맷 커밋 → 치환 커밋" 2단으로 간다. **좌표는 열린 PR 4건 머지 뒤 재확인한다** — #655 가 `DashGeometryParameterWidget.cpp` 를 1,722줄 걷어내고 4파일로 분할하므로 그 파일의 2곳은 사라지고, #654·#651·#652 가 `DashMainWindow.cpp`·`DashModelingTreeWidget.cpp` 를 함께 고친다.

#### DEV-11 · CRT 배포의 수동 glob 을 InstallRequiredSystemLibraries 로 되돌린다
- 종류: PR | 규모: S | 태그: F, G
- 목표: `CMakeLists.txt:15-36` 의 툴셋 경로 수동 glob 과 :11-14 의 TODO 를 지우고 `include(InstallRequiredSystemLibraries)`(+ `CMAKE_INSTALL_OPENMP_LIBRARIES`) 로 대체한다. 차단 조건은 이미 해제됐다 — CMake 4.3.3 의 `Modules/InstallRequiredSystemLibraries.cmake:252-254` 가 `MSVC_TOOLSET_VERSION 145 → VC145`·`_MSVC_IDE_VERSION 18` 을 알고 :297-312 가 `VS_18_DIR/VC/Redist/MSVC/*` 를 글롭하고 :610-621 이 `Microsoft.VC145.OPENMP/vcomp140.dll` 을 담는다. 같이 `cmake_minimum_required` 를 VC145 를 아는 최소 버전으로 범프한다(현 하한 3.25 로는 3.25~3.31 configure 에서 `MSVC_REDIST_DIR-NOTFOUND` 가 그대로 난다).
- 완료 기준: 1. `git grep -n "Redist/MSVC" CMakeLists.txt` 0건 · TODO 블록 제거 2. `cmake_minimum_required` 가 VC145 지원 하한 이상(또는 그 미만에서 glob 폴백을 남기는 버전 가드를 둔 근거를 비고에) 3. **소비처 2곳 모두** 산출물 동일 — 앱 `bin/`(:463-469) 과 `DashUiPreview_package`(:288-293) 에 CRT DLL + `vcomp140.dll` 이 치환 전과 같은 집합 4. Windows 빌드 1회로 (3) 대조
- 변경 범위: CMakeLists.txt · CMakePresets.json(`"version": 6` 이 3.25 하한 — 범프 폭에 따라)
- 선행: -
- 충돌: PR #654(CMakeLists.txt) · DEV-21(CMakeLists.txt) · B2 교집합: CMakeLists.txt → DEV-24 DEV-25 MOR-06 MOR-07 UIC-02 · PR #658(CMakeLists.txt)
- 흡수: #336-3 · DEV-c13
- 비고: 이슈의 "CMake 3.31 이 모른다" 는 이행 당시 실측 — 로컬 `cmake --version` = 4.3.3 에서 해제를 직접 확인했다(DEV-c13). VC145 를 처음 아는 CMake 버전은 릴리스 노트에서 확정한다 — 그 값이 하한 범프의 숫자다. `CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS` 는 변수 하나이므로 두 POST_BUILD 가 그것을 참조하도록 바꾸면 소비처 2곳이 한 번에 덮인다.

#### DEV-12 · vcpkg 이행 문서 2건을 삭제하고 build-environment.md 를 external 잔재 없이 docs/ 정식 위치로 승격한다
- 종류: PR | 규모: S | 태그: F · docs
- 목표: `docs/vcpkg-migration-scope.md` · `docs/vcpkg-migration-code-changes.md` 삭제(정본은 PR #313 본문). `docs/scratchpad/build-environment.md` 는 운영 지식이므로 `docs/build-environment.md` 로 옮기고 `../` 링크 제거, 삭제 문서를 가리키던 3곳(:12·44·345) 정리, docs/index.md 「공통 문서」 등록, README.md:60 · development-environment-setup.md 7곳의 경로 갱신. 같은 파일에서 **external/ 전제 서술도 걷는다**(DEV-09 병합) — 2.7 절 "낡은 external/ 트리 의심" 과 :34-35·:327-329. CMake 의 `EXTERNAL_DIR`(:73) 과 가드된 extension exe 2곳(:374-375·477·505)은 그대로 둔다.
- 완료 기준: 1. `git grep -n "vcpkg-migration"` 0건 2. `git grep -n "scratchpad/build-environment"` 0건 3. docs/index.md 에 build-environment 항목 존재 4. `git grep -n "external/" -- docs/` 가 진단 절차를 가리키지 않음(비추적 로컬 트리라는 사실 서술만 남음)
- 변경 범위: docs/vcpkg-migration-scope.md(삭제) · docs/vcpkg-migration-code-changes.md(삭제) · docs/scratchpad/build-environment.md → docs/build-environment.md · docs/index.md · docs/development-environment-setup.md · README.md
- 선행: -
- 충돌: DEV-13(docs/index.md) · B2 교집합: README.md → DEV-01 DEV-02 DEV-21 DEV-24 MOR-07 · development-environment-setup.md → DEV-01 DEV-02 · index.md → EXE-05
- 흡수: #336-1 · #336-4 · DEV-c11, c14, c15, c16, c17
- 비고: 선행 ops(항목 아님) — 팀 공지로 로컬 `external/` 삭제를 알린다(수 GB 회수). 저장소에는 지울 것이 없다: `external/` 은 비추적(.gitignore:482-484)이고 현 체크아웃에 부재다. "운영 지식 추출" 별도 티켓은 만들지 않는다 — CRT·MKL 복사 근거는 CMakeLists.txt:9-36·420-445 주석이 정본이고, build-environment.md 가 그 위치를 가리키면 된다.

#### DEV-13 · 테스트·문서 색인의 낡은 수치와 깨진 링크를 현행화한다
- 종류: PR | 규모: S | 태그: F · docs
- 목표: docs/test-levels.md 9절(실행 파일 14 · 서브테스트 191) 과 docs/test-execution.md:13("실행 파일 6개") 을 add_test 54건 기준으로 고치고, docs/index.md 가 가리키는 부재 문서(io-controller.md · modules/* · dialogs/*) 링크를 제거하거나 실제 문서로 잇는다.
- 완료 기준: 1. docs/index.md 의 상대 링크 전부 존재 2. test-levels.md 9절·test-execution.md 의 실행 파일 수가 `ctest -N` 과 일치(또는 수치를 빼고 "tests/CMakeLists.txt 가 정본" 으로 치환)
- 변경 범위: docs/test-levels.md · docs/test-execution.md · docs/index.md
- 선행: -
- 충돌: PR #655 · #654(docs/test-levels.md 9절 표를 둘 다 고친다 — #654 가 191→203, #655 가 203→233 · 타깃 개명 `TestSampledHandleTree`→`TestHandleTree` + `TestHandleEditing` 추가) · DEV-12(docs/index.md) · B2 교집합: index.md → EXE-05 · test-execution.md → DEV-14 DEV-18 · test-levels.md → PER-05
- 흡수: DEV-c21
- 비고: 원천 이슈 없는 부수 발견. 9절 전수 표는 "두 곳에 두면 갱신이 갈라진다" 고 스스로 적었으니 실행 파일별 수치를 빼는 쪽을 권장 — #654·#655 가 둘 다 그 표의 숫자를 손으로 고치고 있는 것이 그 근거다. `docs/index.md:6` 이 본문에서 `io-controller.md` 를 "모든 파일 경로 규칙의 기준" 으로 선언한 줄도 함께 처리 대상이다.

#### DEV-14 · CI 플랫폼과 러너 구성을 결정한다
- 종류: DEC | 규모: S | 태그: F
- 목표: 플랫폼(GitHub Actions 추정) · 러너(VS 18.9.2 + MSVC 14.51.36231 고정 self-hosted Windows, vcpkg 바이너리 캐시 읽기 권한, Ninja) · 레인 트리거(PR 에 Level 1·2 / 야간 또는 수동 Level 3) · 앱 빌드 포함 여부를 정한다. 앱 빌드 여부의 쟁점은 하나다 — **Level 3 레인이 `tests/e2e` 를 빌드·등록하는가.** `tests/` 본체는 독립 CMake 프로젝트라 앱 없이 빌드되지만(모핑·preprocessor 테스트만 `CMAKE_PREFIX_PATH` 로 vcpkg_installed 필요), `tests/e2e` 는 별도 프로젝트(`project(DashOptiRealExeE2E)`)이고 `-DDASH_BIN_DIR=<build>/bin` 이 필수라 `bin/extensions/` 의 실 extension exe = **앱 빌드 전체**를 요구한다. 이것이 CI 에 앱 빌드를 넣을 유일한 이유다.
- 완료 기준: 결정 기록 1곳 — `docs/test-execution.md` 신설 절(README 와 양자택일로 두지 않는다. DEV-13·DEV-18 도 이 파일을 고치므로 교집합이 한 곳으로 모인다) · `tests/e2e` 의 Level 3 등록 여부와 그 결론이 요구하는 앱 빌드 비용(러너 디스크·시간)이 그 절에 적힘
- 변경 범위: docs/test-execution.md (기록만)
- 선행: -
- 충돌: B2 교집합: test-execution.md → DEV-13 DEV-18
- 흡수: #372(선행 조건) · #373(닫힘 — "훅 우회는 CI 게이트로만") · DEV-c18
- 비고: DEV-01 은 **차단 선행이 아니다** — 정책이 미확정이어도 러너는 현 핀(18.9.2)으로 세울 수 있다. 단 DEV-01 이 A(전원 상향)로 가면 러너 핀 갱신이 운영 비용으로 따라오므로 결정 기록에 그 연결을 남긴다. 플랫폼이 GitHub 가 아니면 DEV-15 의 변경 범위가 바뀐다. `tests/e2e/test_e2e_real_exe.cpp` 가 "ctest 에 등록돼 있지 않다 … 등록 여부는 별건"(docs/test-levels.md 9절 말미)으로 미뤄 둔 그 "별건"이 이 결정이다.

#### DEV-15 · 테스트 레인 CI 워크플로를 신설한다
- 종류: PR | 규모: M | 태그: F · feature
- 목표: PR·push 에 `tests/` 를 configure·build 하고 `DASH_TEST_LEVEL=1`·`2` 로 ctest 를 돌리는 워크플로, 야간(또는 수동) Level 3 워크플로를 만든다. 훅이 `--no-verify` 로 우회된 커밋을 여기서 막는다(#373 결정). 서식 검사(run-format-checks.sh 의 clang-format 부분)도 같은 레인에 둔다. Level 3 레인은 DEV-14 가 `tests/e2e` 등록을 결정한 경우 앱을 빌드하고 `cmake -S tests/e2e -B build-e2e -DDASH_BIN_DIR=<build>/bin` 단계를 추가한다.
- 완료 기준: 1. PR 에 Level 1·2 레인이 돌고 실패가 머지를 막는다 2. 야간 Level 3 레인이 돈다 3. 레인 로그에 `ctest -V` 실행 파일별 시간이 남는다(DEV-16 입력) 4. `tests/e2e` 는 DEV-14 결정대로 — 등록이면 Level 3 레인에서 앱 빌드 + `bin/extensions/` 배치 뒤 `test_e2e_real_exe` 가 실행되고, 미등록이면 그 사유가 워크플로 주석과 docs/test-execution.md 에 남는다
- 변경 범위: .github/workflows/tests-level-1-2.yml · .github/workflows/tests-level-3.yml (신규) · scripts/run_tests.ps1(`-Level` 인자 이미 있음 — 비대화형 옵션 보강 시) · (e2e 등록 시) tests/e2e/CMakeLists.txt 에 `add_test` 또는 레인 스크립트
- 선행: DEV-14
- 충돌: B2 교집합: tests-level-1-2.yml → DEV-16
- 흡수: #372(선행 조건) · DEV-c18
- 비고: 레벨 게이트·스크립트는 #359 가 다 세웠다(tests/TestLevel.h · scripts/hooks/run-test-level.sh). 워크플로는 그 명령을 그대로 부른다. `tests/e2e` 는 `tests/CMakeLists.txt:17` 이 "built separately" 로 분리 선언한 별도 프로젝트라 `add_subdirectory` 가 아니라 레인의 독립 configure 단계다.

#### DEV-16 · Level 1 레인 소요 시간을 측정하고 5분 초과 시 알린다
- 종류: PR | 규모: S | 태그: F · feature
- 목표: Level 1 워크플로에서 `ctest` 구간만 벽시계로 재고, 임시 한도 5분을 넘으면 빌드를 깨지 않고 경고(annotation/요약)를 낸다. 경고에 `ctest -V` 에서 뽑은 실행 파일별 소요 시간 상위 목록을 붙인다.
- 완료 기준: 1. 측정 구간이 빌드를 제외한 ctest 실행만임이 스크립트에서 드러남 2. 한도 초과가 실패가 아닌 경고로 표시됨(의도적 초과 테스트로 1회 확인) 3. 경고에 실행 파일별 시간 포함 4. 한도 값이 워크플로 변수 1곳
- 변경 범위: .github/workflows/tests-level-1-2.yml · scripts/ci/ctest-timing.py (신규)
- 선행: DEV-15
- 충돌: -
- 흡수: #372 · DEV-c19, c20
- 비고: Level 2·3 한도는 두지 않는다(docs/test-levels.md 6절 결정 유지). 기준선이 쌓이면 5분을 조인다. 빌드 시간 감시는 별건.

#### DEV-17 · 네이밍 정렬의 방식·단위·속도를 결정한다
- 종류: DEC | 규모: S | 태그: F, E
- 목표: #386 재착수 1단계. 비테스트 소스 `m_` 접두 이름 1,161종(13,383회) 를 `.clang-tidy` 규칙(접미 `_`) 으로 정렬할 방식을 정한다 — 전수 일괄(열린 PR #655·#654·#652·#651 과 충돌·blame 덮음) vs 점진(파일/모듈 단위, 어떤 속도로, 어느 PR 에 얹을지) vs 보류 연장. 정렬 완료 판정(전체 clang-tidy 위반 0)과 그 뒤 검사 위치(훅/CI)는 결정에 포함하되 구현은 별도.
- 완료 기준: 결정 기록(docs/coding-convention.md 네이밍 절 갱신) · 점진이면 첫 단위와 순서 명시
- 변경 범위: docs/coding-convention.md (기록만)
- 선행: -
- 충돌: B2 교집합: coding-convention.md → UIC-14 UIC-18 UIC-21
- 흡수: #386 · DEV-c22, c23
- 비고: 보류 결정 자체는 기록 완료(해소됨). 검사기는 이전 구현(`0e3b7e7`)을 잇지 않고 새로 짠다 — 이슈 본문의 함정 목록이 그때의 입력. 정렬 전까지 #386 은 결정 기록으로 열어 둬도 된다. 파일 머리말의 clang-format 공통 제약과 같은 함정 — 정렬 커밋은 재포맷 커밋과 분리해야 blame 이 두 번 덮이지 않는다.

#### DEV-18 · 산재 카운트 grep 게이트를 만들어 Level 1 레인에 건다
- 종류: PR | 규모: S | 태그: F, E · feature
- 목표: 패턴별 기준값 파일(`scripts/hooks/grep-gate.txt`)과 검사 스크립트를 만든다. 하드(증가 시 실패): `processEvents`(model 41 · view 14) · model→view include(2). 소프트(추세 출력만): `Mgr()`(245). 기준값 갱신은 같은 PR 에서 사유와 함께. 모든 종료 경로가 패턴별 개수를 항상 출력한다(PR #329 교훈 — "출력 없음" 과 "검사 없음" 을 구분).
- 완료 기준: 1단계(이 항목) — 1. pre-commit 에서 실행 2. 기준값 초과 시 rc≠0, 통과 시에도 개수 출력 3. tests/hooks/ 에 시나리오(초과·동일·감소·빈 입력) 자체검사 4. **기준값은 착수 커밋에서 스크립트로 생성하고, 생성 명령을 기준값 파일 머리말에 남긴다**(위 수치는 b08a91b3 스냅샷이고 열린 PR 4건이 `model/`·`view/` 를 대량 수정하므로 착수 시점에 다시 떠야 한다). 2단계 — CI Level 1 레인 등록(DEV-15 가 레인을 세운 뒤)
- 변경 범위: scripts/hooks/run-grep-gate.sh · scripts/hooks/grep-gate.txt (신규) · .githooks/pre-commit · tests/hooks/test-grep-gate.py (신규) · docs/test-execution.md
- 선행: -
- 충돌: 열린 PR 전부(#655 #654 #652 #651 — 기준값 재생성 필요) · B2 교집합: test-execution.md → DEV-13 DEV-14
- 흡수: #489(F1 "grep 게이트") · DEV-c26
- 비고: **DEV-15 는 차단 선행이 아니다** — 훅 쪽 1단계는 CI 없이 독립으로 랜딩하고, 레인 등록만 DEV-15 뒤다(완료 기준의 2단계). 기준값 자체는 EXE(펌핑 제거)·PRJ(`Mgr()` 주입 전환) 항목이 내리면서 갱신한다. 도메인 커버리지 확장(CAD-U5 · OPT-U3 · BLD · RUN · DOE)은 각 모듈 항목 — DEV 는 인프라(게이트·등록 헬퍼)만 맡는다.

#### DEV-19 · tests/CMakeLists.txt 의 환경 변수 타깃 수동 나열을 DEFER 자동 수집으로 바꾼다
- 종류: PR | 규모: S | 태그: F · refactor
- 목표: `:383` 의 `set_tests_properties(<타깃 30개 나열> PROPERTIES ENVIRONMENT_MODIFICATION "PATH=…;QT_LOGGING_TO_CONSOLE=set:1")` 에서 손으로 든 30개 목록을 없애고, 같은 파일이 이미 쓰는 선례 — `:904` `_dash_attach_known_failures` + `:921` `cmake_language(DEFER CALL …)` 가 `BUILDSYSTEM_TARGETS` 로 `test_*` 를 훑는 방식 — 을 재사용해 **그 블록이 덮던 타깃 집합에만** 같은 환경 변수를 붙인다. ":393-394 목록에 안 넣으면 로더가 0xc0000135" 함정이 사라진다. 동작 불변.
- 완료 기준: 1. `ctest -N` 목록이 전후 동일(현행 54건) 2. **각 타깃의 `ENVIRONMENT_MODIFICATION` 값이 전후 동일** — 지금 그 변수가 붙은 타깃 집합과 붙지 않은 타깃 집합이 둘 다 그대로다(가드 안 24개는 `_dash_snapshot_path_ops`·`_dash_rw_path_ops`·`QT_QPA_PLATFORM` 가 서로 달라 건드리지 않는다) 3. Level 1·2 레인 통과
- 변경 범위: tests/CMakeLists.txt
- 선행: PR #655 머지 (`:392-404` hunk 가 `test_handle_array_names` 제거 · `test_sampled_handle_tree`→`test_handle_tree` 개명 · `test_handle_editing` 추가로 타깃 집합을 바꾼다)
- 충돌: PR #655 · #654 · #652 · #651(tests/CMakeLists.txt) · 각 모듈의 테스트 추가 항목(같은 파일) · B2 교집합: tests/CMakeLists.txt → 공유 12건(deps.md 5절)
- 흡수: #489(커버리지 확장의 인프라 비용) · DEV-c27
- 비고: 선택 항목. 열린 PR 4건 머지 뒤, 모듈 테스트 추가가 몰리기 전에 넣어야 충돌이 적다. **54개 등록 전면을 `dash_add_qtest` 래퍼 하나로 바꾸는 것은 이 항목이 아니다** — :383 의 30개만 Qt Core+Test 전용 한 블록을 공유하고 나머지 24개는 `if(VTK_FOUND)`·`core-lib`·`mesh-ops` 가드 안에서 링크 목록·`vtk_module_autoinit`·환경 변수가 전부 다르다(921줄 · `add_executable` 55 · `set_tests_properties` 26블록 · `QT_LOGGING_TO_CONSOLE` 14회). 전면 래퍼화는 `M` 이상의 별건이고, 그 쪽이 필요해지는 시점은 가드별 변종이 공통 규칙으로 수렴한 뒤다.

#### DEV-20 · 출고물의 개발자 로컬 경로를 제거한다
- 종류: PR | 규모: S | 태그: G · bug
- 목표: TopOptPostprocessDialog::onProgressTimer 의 `C:\Users\MIIIING\Downloads\TO\repaired_surface_7.stl` 하드코딩 렌더를 실제 산출물 경로(후처리 결과 STL) 로 바꾸거나, 산출물이 없으면 그 단계를 제거한다.
- 완료 기준: 1. `git grep -nIE '"[A-Za-z]:[/\\]' -- '*.cpp' '*.h' '*.ui' ':!tests'` 0건(주석 제외) 2. TopOpt 후처리 진행 마지막 단계에서 로컬 경로 없이 결과 렌더 또는 무동작
- 변경 범위: view/dialog/TopOptPostprocessDialog.cpp
- 선행: -
- 충돌: B2 교집합: TopOptPostprocessDialog.cpp → EXE-09 PRJ-26 REN-07
- 흡수: #483 · DEV-c28, c29, c31, c32
- 비고: 접점 PRJ(view/dialog). 변경이 한두 줄이라 **파일 머리말의 clang-format 공통 제약이 가장 세게 걸린다** — 재포맷 커밋을 먼저 분리하지 않으면 변경이 완전히 묻힌다. 플레이스홀더 문구·Dev 자산 경로는 해소됨(Release 미포함). Optimizer 샘플 제약 행(`r1 <= 163.23`)은 저장 왕복에 섞이므로 OPT 로 보냄(DEV-c30).

#### DEV-21 · 버전을 한 곳에서 exe 리소스와 Qt 앱 메타에 주입한다
- 종류: PR | 규모: S | 태그: G · feature
- 목표: CMake 에 숫자 버전(`DASH_VERSION_MAJOR/MINOR/PATCH`) 을 두고 `resources/resources.rc.in` 을 configure 해 `VERSIONINFO`(FILEVERSION · PRODUCTVERSION · ProductName · FileDescription · LegalCopyright) 를 넣는다. main.cpp 에서 `QCoreApplication::setApplicationName/Version` 을 호출해 저장 문서의 `createdAppVersion`·`modifiedAppVersion` 이 채워지게 한다. vcpkg.json `version-string` 은 같은 값으로 맞춘다.
- 완료 기준: 1. `DashOpti.exe` 속성창 「자세히」에 버전·제품명 표시 2. 새로 저장한 프로젝트 JSON 의 `createdAppVersion` 이 `DASH_VERSION` 과 같음 3. 버전 문자열 정의가 CMakeLists.txt 1곳 4. README.md 의 CMake 옵션 표·예제(:133 · :144)가 신설한 숫자 버전 변수를 반영
- 변경 범위: CMakeLists.txt · resources/resources.rc → resources/resources.rc.in · main.cpp · vcpkg.json · README.md
- 선행: -
- 충돌: PR #654(CMakeLists.txt) · DEV-11(CMakeLists.txt) · DEV-24(README.md 의 같은 옵션 표) · B2 교집합: main.cpp → EXE-02 EXE-06 PRJ-06 PRJ-14 UIC-05 UIC-26 · CMakeLists.txt → DEV-25 MOR-06 MOR-07 UIC-02 · README.md → DEV-01 DEV-02 DEV-12 MOR-07 · vcpkg.json → DEV-06 · PR #658(CMakeLists.txt·vcpkg.json)
- 흡수: #484-1 · DEV-c33, c34
- 비고: 접점 PER — `createdAppVersion` 이 비어 있던 기존 문서는 그대로 둔다(마이그레이션 없음). 파일 머리말의 clang-format 공통 제약이 `main.cpp` 에 걸린다.

#### DEV-22 · About 의 Build Date 가 항상 "어제" 로 표시되는 덮어쓰기를 지운다
- 종류: PR | 규모: S | 태그: G · bug
- 목표: AboutDialog::getBuildDate 에서 `__DATE__` 파싱 결과를 `QDate::currentDate().addDays(-1)` 로 덮는 2줄을 제거해 실제 빌드 날짜를 보인다.
- 완료 기준: About 의 Build Date 가 `__DATE__` 와 일치(다른 날 실행해도 불변)
- 변경 범위: view/dialog/AboutDialog.cpp
- 선행: -
- 충돌: DEV-24(같은 파일) · B2 교집합: AboutDialog.cpp → PRJ-14
- 흡수: #484(부수) · DEV-c36
- 비고: `addDays(-1)` 가 빌드 날짜 쪽에도 붙어 있다(:103) — 의도 불명, 같이 제거. 2줄 변경이라 **파일 머리말의 clang-format 공통 제약이 가장 세게 걸린다** — 재포맷 커밋을 먼저 분리한다. 같은 파일을 고치는 DEV-24 와 묶으면 재포맷을 한 번만 치른다.

#### DEV-23 · 라이선스 만료일 런타임화의 형식과 강제 여부를 결정한다
- 종류: DEC | 규모: S | 태그: G, A
- 목표: 현재 만료일은 컴파일 상수(`2026-08-31`, 경과) 이고 About 표시 전용이며 타입만 QSettings 런타임이다. (1) 형식 — 서명 파일(발급 도구 + 검증, W17 원안) vs 설정 키/단순 파일, (2) 만료 시 동작 — 표시만 vs 기동 차단, (3) 발급 주체·갱신 절차를 정한다.
- 완료 기준: 결정 기록 · DEV-24 의 규모(S/M) 확정
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #484-2 · DEV-c35
- 비고: 되돌리기 비용이 큰 결정(저장 포맷·발급 절차) — "나중에 교체" 전제로 정하지 않는다.

#### DEV-24 · 라이선스 만료일을 런타임 소스에서 읽는다
- 종류: PR | 규모: M | 태그: G, A · feature
- 목표: DEV-23 결정대로 로더(`utils/DashLicense` 신설)를 만들고 AboutDialog 가 그것을 읽는다. `DASH_LICENSE_EXPIRY_DATE` 컴파일 정의와 CMake 캐시 변수를 제거한다. 서명 파일이면 발급 도구(tools/) 와 검증을 포함한다.
- 완료 기준: 1. 재빌드 없이 만료일 변경이 About 에 반영 2. `git grep -n DASH_LICENSE_EXPIRY_DATE` 0건 — **README.md:134(옵션 표) · :145(예제) 포함** 3. 손상·부재 입력의 동작이 DEV-23 결정과 일치(단위 테스트 1건, Level 1) 4. README 의 라이선스 옵션 서술이 CMake 정의와 일치 — 지금 표의 기본값 `"2026-06-30"` 이 `CMakeLists.txt:107` 의 `"2026-08-31"` 과 어긋나 있다(DEV-c39)
- 변경 범위: utils/DashLicense.{h,cpp} (신규) · view/dialog/AboutDialog.{h,cpp} · CMakeLists.txt · README.md · main.cpp(기동 차단 시) · tests/ (신규 1건) · tools/ (서명 발급 시)
- 선행: DEV-23
- 충돌: DEV-21(CMakeLists.txt · README.md 의 같은 옵션 표) · DEV-11(CMakeLists.txt) · DEV-22(AboutDialog.cpp) · B2 교집합: main.cpp → EXE-02 EXE-06 PRJ-06 PRJ-14 UIC-05 UIC-26 · CMakeLists.txt → DEV-25 MOR-06 MOR-07 UIC-02 · README.md → DEV-01 DEV-02 DEV-12 MOR-07 · AboutDialog.cpp → PRJ-14 · PR #658(CMakeLists.txt) · PR #654(CMakeLists.txt)
- 흡수: #484-2 · DEV-c35, c39
- 비고: 설정 키 형식이면 S 로 줄어든다. `DEFAULT_LICENSE_TYPE` 도 같은 소스로 옮긴다 — README 표의 세 줄(:133-135)과 예제(:144-146)가 한 덩어리라 같이 걷는다. 파일 머리말의 clang-format 공통 제약이 `AboutDialog.cpp`·`main.cpp` 에 걸린다.

#### DEV-25 · 현 vcpkg VTK 포트에 `IOHDF` 모듈이 있는지 실측한다 (#411 결정 1)
- 종류: INV | 규모: S | 태그: F
- 목표: GUI 는 VTK 를 직접 선언하지 않고 mesh-ops/preprocessor 포트를 통해 default registry baseline `04a9d8e5` 의 vtk 9.3(feature `ioocct opengl openmp qt tbb utf8`) 을 받는다. Windows 빌드 트리의 `vcpkg_installed/x64-windows-dashopti/lib` 에 `vtkIOHDF-9.3.lib` 과 VTK targets 의 `VTK::IOHDF` 가 있는지 확인한다. 있으면 `find_package(VTK COMPONENTS …)` 에 `IOHDF` 1줄 추가로 끝. 없으면 vtk 포트 feature 추가가 mesh-ops/preprocessor 의 feature 문자열(ABI)에도 들어가야 하므로 메타 저장소·캐시 재워밍 비용을 기록한다.
- 완료 기준: 실측 기록(lib·타깃 유무 · VTK 버전) · 있으면 CMake 1줄 PR 범위 명시 / 없으면 EXT(메타 저장소 feature 추가 + 재워밍) 항목 발행 여부와 비용 — PRE-29 의 입력
- 변경 범위: 실측만 — 후속 시 CMakeLists.txt:300-329 (`find_package(VTK REQUIRED COMPONENTS …)` 28종) 1줄
- 선행: -
- 충돌: PR #654(CMakeLists.txt — 후속 PR 시) · DEV-11 · DEV-21(CMakeLists.txt) · B2 교집합: CMakeLists.txt → DEV-24 MOR-06 MOR-07 UIC-02 · PR #658(CMakeLists.txt)
- 흡수: #411 결정 1 (DEV 몫, PRE-c58 이관) · DEV-c38
- 비고: 현 macOS 체크아웃에는 vcpkg_installed 가 없어 Windows 러너에서 본다. GUI 단독 feature 추가는 불가 — CMakeLists.txt:297-299 주석("다른 VTK 를 가리키면 두 포트와 ABI 가 갈린다").

## 3. 의존 · 충돌

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> `python3 05-final/build_deps.py` 생성. 기준 03-items (dev @ b08a91b3). 충돌(항목) = `충돌:` 줄의 ID ∪ `변경 범위` 파일 교집합(basename 기준, 약칭 W/M/PM 등 해석). 충돌(PR) = `충돌:`·`선행:` 의 열린 PR ∪ 파일 교집합. 선행의 `PR #N` 은 머지 대기.

## 1. 항목별 선행 · 충돌

| 항목 | 종류 | 선행 | 충돌(항목) | 충돌(PR) |
|---|---|---|---|---|
| MOR-01 | PR | - | DEV-10 MOR-02 MOR-03 MOR-17 MOR-22 MOR-23 UIC-12 UIC-13 UIC-20 | #655 #654 |
| MOR-02 | PR | PR #655 | DEV-10 MOR-01 MOR-03 MOR-04 MOR-05 MOR-06 MOR-07 MOR-13 MOR-15 MOR-17 MOR-22 MOR-23 UIC-20 | #655 #654 |
| MOR-03 | PR | PR #655 | DEV-10 MOR-01 MOR-02 MOR-04 MOR-06 MOR-07 MOR-13 MOR-17 MOR-22 MOR-23 UIC-20 | #655 #654 |
| MOR-04 | PR | PR #655 PR #655 | MOR-02 MOR-03 MOR-06 MOR-07 MOR-13 MOR-15 MOR-17 MOR-23 | #655 #654 |
| MOR-05 | DEC | PR #655 | DEV-10 MOR-02 MOR-12 MOR-14 MOR-17 MOR-23 UIC-07 UIC-22 | #655 #654 |
| MOR-06 | PR | PR #655 | DEV-11 DEV-21 DEV-24 DEV-25 MOR-02 MOR-03 MOR-04 MOR-05 MOR-07 MOR-13 MOR-15 MOR-17 MOR-21 MOR-23 UIC-02 | #658 #655 #654 |
| MOR-07 | PR | PR #655 PR #655 | DEV-01 DEV-02 DEV-11 DEV-12 DEV-21 DEV-24 DEV-25 MOR-02 MOR-03 MOR-04 MOR-06 MOR-08 MOR-23 UIC-02 | #658 #655 #654 |
| MOR-08 | PR | MOR-07 | MOR-07 | #655 |
| MOR-09 | CLOSE | PR #655 | - | #655 |
| MOR-10 | DEC | - | LCH-13 MOR-11 | #654 |
| MOR-11 | PR | PER-10 PR #654 | ANA-15 LCH-13 MOR-10 MOR-22 OPT-01 OPT-02 OPT-05 OPT-07 OPT-08 OPT-11 OPT-15 OPT-16 OPT-18 OPT-19 OPT-23 OPT-24 OPT-26 PRJ-09 RUN-01 RUN-03 RUN-04 RUN-05 RUN-12 RUN-13 RUN-14 RUN-17 RUN-18 RUN-25 RUN-26 RUN-27 RUN-29 RUN-31 RUN-32 RUN-34 UIC-10 UIC-19 UIC-20 | #655 #654 |
| MOR-12 | PR | PR #655 | MOR-05 MOR-23 UIC-22 | #655 #654 |
| MOR-13 | PR | - | MOR-02 MOR-03 MOR-04 MOR-06 MOR-17 MOR-23 | #655 #654 |
| MOR-14 | DEC | - | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-05 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| MOR-15 | CLOSE | PR #655 | - | #655 |
| MOR-16 | PR | - | - | #654 |
| MOR-17 | INV | PR #655 | DEV-10 MOR-01 MOR-02 MOR-03 MOR-04 MOR-05 MOR-06 MOR-13 MOR-22 MOR-23 UIC-20 | #655 #654 |
| MOR-18 | CLOSE | - | - | - |
| MOR-19 | CLOSE | REN-01 REN-02 REN-03 REN-04 REN-05 REN-06 REN-07 REN-08 REN-09 REN-10 PR #655 | - | #655 |
| MOR-20 | CLOSE | PR #655 | - | #655 |
| MOR-21 | PR | MOR-06 MOR-05 PR #655 | MOR-06 | #655 #654 |
| MOR-22 | PR | PER-02 PR #655 | DEV-10 MOR-01 MOR-02 MOR-03 MOR-11 MOR-17 MOR-23 UIC-20 | #655 #654 |
| MOR-23 | INV | PR #655 | DEV-10 MOR-01 MOR-02 MOR-03 MOR-04 MOR-05 MOR-06 MOR-07 MOR-12 MOR-13 MOR-17 MOR-22 UIC-20 UIC-22 | #655 #654 |
| CAD-01 | PR | LCH-29 | CAD-02 CAD-03 CAD-04 CAD-05 CAD-06 CAD-07 CAD-08 CAD-09 CAD-12 CAD-13 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 DOE-19 EXE-08 LCH-02 LCH-06 LCH-07 LCH-10 LCH-12 LCH-14 LCH-27 LCH-29 MOR-14 OPT-01 OPT-02 OPT-05 OPT-06 OPT-07 OPT-08 OPT-09 OPT-10 OPT-12 OPT-13 OPT-14 OPT-15 OPT-17 OPT-18 OPT-21 OPT-22 OPT-25 OPT-26 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-03 REN-04 REN-05 REN-07 REN-10 REN-12 RUN-01 RUN-03 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-15 RUN-16 RUN-17 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-28 RUN-29 RUN-30 RUN-34 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-20 UIC-22 UIC-24 UIC-26 | #655 #654 #652 #651 |
| CAD-02 | PR | LCH-29 | CAD-01 CAD-03 CAD-06 CAD-08 CAD-15 | - |
| CAD-03 | PR | - | CAD-01 CAD-02 CAD-04 CAD-05 CAD-06 CAD-07 CAD-08 CAD-09 CAD-12 CAD-13 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 DOE-19 EXE-06 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-09 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-20 UIC-26 | #655 #654 #652 #651 |
| CAD-04 | PR | CAD-11 | CAD-01 CAD-03 CAD-05 CAD-06 CAD-07 CAD-09 CAD-11 CAD-13 DOE-19 UIC-19 | - |
| CAD-05 | PR | CAD-04 CAD-11 LCH-29 | CAD-01 CAD-03 CAD-04 CAD-06 CAD-07 CAD-09 CAD-11 CAD-13 DOE-19 PRJ-09 UIC-19 UIC-20 | - |
| CAD-06 | PR | - | CAD-01 CAD-02 CAD-03 CAD-04 CAD-05 CAD-07 CAD-08 CAD-09 CAD-13 CAD-15 DOE-19 EXE-06 PRJ-03 PRJ-04 PRJ-06 PRJ-09 PRJ-14 PRJ-19 REN-07 UIC-19 UIC-20 | #654 #652 |
| CAD-07 | PR | - | CAD-01 CAD-03 CAD-04 CAD-05 CAD-06 CAD-09 CAD-12 CAD-13 CAD-14 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 DOE-19 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| CAD-08 | PR | - | CAD-01 CAD-02 CAD-03 CAD-06 CAD-15 | - |
| CAD-09 | DEC | - | CAD-01 CAD-03 CAD-04 CAD-05 CAD-06 CAD-07 CAD-12 CAD-13 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 DOE-19 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-09 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-20 UIC-26 | #655 #654 #652 #651 |
| CAD-10 | EXT | - | - | - |
| CAD-11 | PR | - | BLD-19 CAD-01 CAD-02 CAD-04 CAD-05 CAD-13 CON-11 DEV-19 DOE-07 EXE-09 OPT-20 PER-02 PER-08 RUN-33 UIC-17 UIC-22 | #655 #654 #652 #651 |
| CAD-12 | DEC | - | CAD-01 CAD-03 CAD-07 CAD-09 CAD-14 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| CAD-13 | PR | PER-02 CAD-05 CAD-11 | CAD-01 CAD-03 CAD-04 CAD-05 CAD-06 CAD-07 CAD-09 CAD-11 DOE-19 UIC-19 | - |
| CAD-14 | PR | - | CAD-07 CAD-12 | - |
| CAD-15 | INV | - | CAD-01 CAD-02 CAD-03 CAD-06 CAD-07 CAD-08 CAD-09 CAD-12 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 EXE-11 EXE-12 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| CON-01 | PR | - | CON-02 CON-05 CON-06 CON-09 CON-11 PRJ-09 UIC-20 | - |
| CON-02 | PR | - | CON-01 CON-05 CON-06 CON-09 CON-11 PRJ-09 UIC-20 | - |
| CON-03 | PR | CON-02 PRJ-21 | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-04 CON-05 CON-06 CON-07 CON-12 DEV-10 DOE-05 DOE-19 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-20 UIC-26 | #655 #654 #652 #651 |
| CON-04 | PR | - | CON-03 CON-05 CON-06 CON-07 PRJ-01 UIC-19 | - |
| CON-05 | PR | CON-01 PRJ-08 | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-01 CON-02 CON-03 CON-04 CON-06 CON-07 CON-12 DEV-10 DOE-05 DOE-19 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-08 PRJ-09 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-31 PRJ-32 PRJ-33 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-26 RUN-28 RUN-31 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-20 UIC-26 | #655 #654 #652 #651 |
| CON-06 | PR | CON-04 PRJ-02 | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-01 CON-02 CON-03 CON-04 CON-05 CON-07 CON-12 DEV-10 DOE-05 DOE-19 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-09 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-20 UIC-26 | #655 #654 #652 #651 |
| CON-07 | PR | CON-11 UIC-17 | CON-03 CON-04 CON-05 CON-06 CON-12 DOE-19 UIC-19 UIC-20 | - |
| CON-09 | PR | CON-01 EXE-21 | CON-01 CON-02 CON-11 | - |
| CON-10 | DEC | - | - | - |
| CON-11 | PR | PER-02 CON-01 | BLD-19 CAD-11 CON-01 CON-02 CON-09 DEV-19 DOE-07 EXE-09 OPT-20 PER-02 PER-05 PER-08 RUN-33 UIC-17 UIC-22 | #655 #654 #652 #651 |
| CON-12 | PR | CON-01 | CON-03 CON-04 CON-05 CON-06 CON-07 DOE-19 UIC-19 UIC-20 | - |
| DOE-02 | PR | PRJ-33 | ANA-15 DOE-03 DOE-05 DOE-07 DOE-08 DOE-09 DOE-11 DOE-12 DOE-16 DOE-17 DOE-20 LCH-14 PER-02 PRJ-09 PRJ-33 UIC-19 UIC-20 | #652 |
| DOE-03 | PR | - | ANA-15 DOE-02 DOE-05 DOE-07 DOE-08 DOE-09 DOE-11 DOE-12 DOE-16 DOE-17 LCH-14 LCH-16 PRE-14 PRE-15 PRE-27 PRE-32 PRJ-09 UIC-19 UIC-20 | #652 #651 |
| DOE-05 | PR | - | ANA-07 ANA-15 CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-02 DOE-03 DOE-06 DOE-07 DOE-08 DOE-09 DOE-11 DOE-12 DOE-13 DOE-16 DOE-17 EXE-08 LCH-14 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-08 PRJ-09 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-31 PRJ-32 PRJ-33 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-26 RUN-28 RUN-31 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-20 UIC-26 | #655 #654 #652 #651 |
| DOE-06 | PR | - | DOE-05 DOE-09 DOE-11 DOE-13 UIC-20 | - |
| DOE-07 | PR | - | ANA-15 BLD-19 CAD-11 CON-11 DEV-19 DOE-02 DOE-03 DOE-05 DOE-08 DOE-09 DOE-11 DOE-12 DOE-16 DOE-17 EXE-09 LCH-14 OPT-20 PER-02 PER-08 PRJ-09 RUN-33 UIC-17 UIC-19 UIC-20 UIC-22 | #655 #654 #652 #651 |
| DOE-08 | PR | - | ANA-15 DOE-02 DOE-03 DOE-05 DOE-07 DOE-09 DOE-11 DOE-12 DOE-16 DOE-17 LCH-14 PRJ-09 UIC-19 UIC-20 | #652 |
| DOE-09 | PR | - | ANA-15 DOE-02 DOE-03 DOE-05 DOE-06 DOE-07 DOE-08 DOE-11 DOE-12 DOE-13 DOE-16 DOE-17 LCH-14 PRJ-09 UIC-19 UIC-20 | #652 |
| DOE-10 | PR | - | DOE-12 DOE-16 DOE-17 PER-07 | - |
| DOE-11 | PR | PR #652 | ANA-07 ANA-15 DOE-02 DOE-03 DOE-05 DOE-06 DOE-07 DOE-08 DOE-09 DOE-12 DOE-13 DOE-16 DOE-17 LCH-14 PRJ-09 PRJ-25 UIC-19 UIC-20 | #652 |
| DOE-12 | PR | - | ANA-15 DOE-02 DOE-03 DOE-05 DOE-07 DOE-08 DOE-09 DOE-10 DOE-11 DOE-16 DOE-17 LCH-02 LCH-03 LCH-04 LCH-05 LCH-07 LCH-10 LCH-12 LCH-13 LCH-14 PER-02 PER-07 PRJ-09 UIC-19 UIC-20 | #652 |
| DOE-13 | PR | - | DOE-05 DOE-06 DOE-09 DOE-11 UIC-20 | - |
| DOE-14 | DEC | - | - | - |
| DOE-15 | CLOSE | - | - | - |
| DOE-16 | PR | PER-07 | ANA-15 DOE-02 DOE-03 DOE-05 DOE-07 DOE-08 DOE-09 DOE-10 DOE-11 DOE-12 DOE-17 LCH-14 LCH-16 PER-02 PER-07 PRE-14 PRE-15 PRE-27 PRE-32 PRJ-09 UIC-19 UIC-20 | #652 #651 |
| DOE-17 | PR | PER-02 DOE-10 | ANA-15 DOE-02 DOE-03 DOE-05 DOE-07 DOE-08 DOE-09 DOE-10 DOE-11 DOE-12 DOE-16 LCH-14 PRJ-09 UIC-19 UIC-20 | #652 |
| DOE-18 | DEC | - | DOE-16 PER-07 | - |
| DOE-19 | PR | - | CAD-01 CAD-03 CAD-04 CAD-05 CAD-06 CAD-07 CAD-09 CAD-13 CON-03 CON-05 CON-06 CON-07 CON-12 EXE-06 PRJ-03 PRJ-04 PRJ-06 PRJ-14 REN-07 UIC-19 UIC-20 | #654 #652 |
| DOE-20 | PR | - | DOE-02 UIC-20 | - |
| LCH-01 | PR | PR #651 PR #652 | LCH-08 LCH-10 LCH-15 LCH-16 LCH-17 LCH-28 LCH-29 LCH-33 PRE-05 PRE-23 | #652 #651 |
| LCH-02 | PR | PR #651 PR #652 | CAD-01 DOE-12 LCH-03 LCH-04 LCH-05 LCH-06 LCH-07 LCH-10 LCH-12 LCH-13 LCH-14 PRJ-09 UIC-19 UIC-20 | #652 #651 |
| LCH-03 | PR | PR #651 PR #652 | DOE-12 LCH-02 LCH-04 LCH-05 LCH-07 LCH-10 LCH-12 LCH-13 LCH-14 PRJ-09 UIC-20 | #652 #651 |
| LCH-04 | PR | PR #652 | DOE-12 LCH-02 LCH-03 LCH-05 LCH-07 LCH-10 LCH-12 LCH-13 LCH-14 PRJ-09 | #652 |
| LCH-05 | PR | LCH-04 | DOE-12 LCH-02 LCH-03 LCH-04 LCH-07 LCH-10 LCH-12 LCH-13 LCH-14 PRJ-09 | #652 |
| LCH-06 | PR | LCH-29 PR #652 | CAD-01 LCH-02 LCH-07 LCH-10 LCH-12 LCH-14 LCH-16 LCH-27 LCH-28 LCH-29 LCH-34 PRJ-09 UIC-19 UIC-20 | #652 #651 |
| LCH-07 | PR | LCH-02 LCH-06 PR #651 PR #652 | CAD-01 DOE-12 LCH-02 LCH-03 LCH-04 LCH-05 LCH-06 LCH-10 LCH-12 LCH-13 LCH-14 LCH-16 LCH-18 LCH-27 LCH-28 LCH-29 LCH-30 LCH-34 PRJ-09 PRJ-14 UIC-19 UIC-20 | #652 #651 |
| LCH-08 | PR | LCH-02 PR #651 PR #652 | LCH-01 LCH-09 LCH-10 LCH-14 LCH-15 LCH-16 LCH-17 LCH-28 LCH-29 LCH-33 LCH-34 | #652 #651 |
| LCH-09 | DEC | LCH-32 | LCH-08 LCH-14 LCH-34 PRE-32 | - |
| LCH-10 | PR | LCH-31 LCH-11 PR #651 PR #652 | CAD-01 DOE-12 EXE-11 EXE-12 LCH-01 LCH-02 LCH-03 LCH-04 LCH-05 LCH-06 LCH-07 LCH-08 LCH-12 LCH-13 LCH-14 LCH-15 LCH-16 LCH-17 LCH-28 LCH-29 LCH-31 LCH-33 PRJ-09 | #652 #651 |
| LCH-11 | EXT | LCH-31 | - | - |
| LCH-12 | PR | LCH-10 LCH-03 | CAD-01 DOE-12 LCH-02 LCH-03 LCH-04 LCH-05 LCH-06 LCH-07 LCH-10 LCH-13 LCH-14 PRJ-09 | #652 #651 |
| LCH-13 | PR | PR #651 PR #652 | DOE-12 LCH-02 LCH-03 LCH-04 LCH-05 LCH-07 LCH-10 LCH-12 LCH-14 MOR-10 MOR-11 PRJ-09 UIC-20 | #654 #652 #651 |
| LCH-14 | PR | PR #651 PR #652 | ANA-15 CAD-01 DOE-02 DOE-03 DOE-05 DOE-07 DOE-08 DOE-09 DOE-11 DOE-12 DOE-16 DOE-17 LCH-02 LCH-03 LCH-04 LCH-05 LCH-06 LCH-07 LCH-08 LCH-09 LCH-10 LCH-12 LCH-13 LCH-16 LCH-18 LCH-27 LCH-28 LCH-29 LCH-30 LCH-34 PRJ-09 PRJ-14 UIC-19 UIC-20 | #652 #651 |
| LCH-15 | PR | PRE-02 PR #651 PR #652 | ANA-15 LCH-01 LCH-08 LCH-10 LCH-16 LCH-17 LCH-28 LCH-29 LCH-33 PRE-03 PRE-04 PRE-06 PRE-07 PRE-08 PRE-09 PRE-13 PRE-15 PRE-16 PRE-21 PRE-23 PRE-24 PRE-25 PRE-30 PRE-32 PRJ-09 UIC-20 | #658 #656 #652 #651 |
| LCH-16 | PR | LCH-07 PR #651 PR #652 | DOE-03 DOE-16 LCH-01 LCH-06 LCH-07 LCH-08 LCH-10 LCH-14 LCH-15 LCH-17 LCH-28 LCH-29 LCH-33 LCH-34 PRE-14 PRE-15 PRE-27 PRE-32 PRJ-09 UIC-20 | #652 #651 |
| LCH-17 | PR | PR #651 PR #652 | LCH-01 LCH-08 LCH-10 LCH-15 LCH-16 LCH-28 LCH-29 LCH-33 | #652 #651 |
| LCH-18 | INV | PR #651 | LCH-07 LCH-14 LCH-30 PRJ-14 UIC-19 | #651 |
| LCH-19 | DEC | PR #651 PR #652 | RUN-30 | #652 #651 |
| LCH-20 | CLOSE | - | - | - |
| LCH-21 | CLOSE | - | - | - |
| LCH-22 | CLOSE | LCH-03 LCH-08 LCH-09 | - | - |
| LCH-23 | CLOSE | PR #652 | - | #652 |
| LCH-24 | CLOSE | - | - | - |
| LCH-25 | CLOSE | PR #652 | - | #652 |
| LCH-26 | CLOSE | PR #651 | - | #651 |
| LCH-27 | PR | LCH-29 LCH-19 PR #652 | CAD-01 LCH-06 LCH-07 LCH-14 LCH-29 UIC-19 | #652 #651 |
| LCH-28 | PR | EXE-07 EXE-09 PR #651 PR #652 | LCH-01 LCH-06 LCH-07 LCH-08 LCH-10 LCH-14 LCH-15 LCH-16 LCH-17 LCH-29 LCH-33 LCH-34 PRJ-09 UIC-20 | #652 #651 |
| LCH-29 | DEC | - | CAD-01 LCH-01 LCH-06 LCH-07 LCH-08 LCH-10 LCH-14 LCH-15 LCH-16 LCH-17 LCH-27 LCH-28 LCH-33 UIC-19 | #652 #651 |
| LCH-30 | PR | PR #651 | LCH-07 LCH-14 LCH-18 PRE-32 PRJ-14 UIC-19 | #651 |
| LCH-31 | DEC | - | EXE-11 EXE-12 LCH-10 | - |
| LCH-32 | DEC | - | - | - |
| LCH-33 | PR | DOE-16 | ANA-15 LCH-01 LCH-08 LCH-10 LCH-15 LCH-16 LCH-17 LCH-28 LCH-29 PRE-03 PRE-04 PRE-06 PRE-07 PRE-08 PRE-09 PRE-13 PRE-15 PRE-16 PRE-21 PRE-23 PRE-24 PRE-25 PRE-30 PRE-32 PRJ-09 PRJ-22 UIC-20 | #658 #656 #652 #651 |
| LCH-34 | PR | PRE-15 LCH-07 | LCH-06 LCH-07 LCH-08 LCH-09 LCH-14 LCH-16 LCH-28 PRJ-09 UIC-20 | - |
| PRE-01 | INV | PR #658 PR #658 | PRE-06 PRE-09 PRE-16 PRE-17 | #658 |
| PRE-02 | INV | PRE-01 PRE-04 PRE-07 PRE-20 PR #656 | - | #656 |
| PRE-03 | CLOSE | - | ANA-15 LCH-15 LCH-33 PRE-04 PRE-06 PRE-07 PRE-08 PRE-09 PRE-10 PRE-13 PRE-15 PRE-16 PRE-19 PRE-20 PRE-21 PRE-22 PRE-23 PRE-24 PRE-25 PRE-30 PRE-31 PRE-32 PRJ-09 PRJ-22 UIC-20 | #658 #656 #652 #651 |
| PRE-04 | PR | PRE-07 PRE-05 PR #656 | ANA-15 LCH-15 LCH-33 PRE-03 PRE-06 PRE-07 PRE-08 PRE-09 PRE-10 PRE-13 PRE-15 PRE-16 PRE-19 PRE-20 PRE-21 PRE-22 PRE-23 PRE-24 PRE-25 PRE-30 PRE-31 PRE-32 PRJ-09 UIC-20 | #658 #656 #652 #651 |
| PRE-05 | PR | - | LCH-01 PRE-08 PRE-16 PRE-18 PRE-23 PRE-24 PRE-27 | #658 #651 |
| PRE-06 | PR | PRE-05 PRE-07 PR #658 | ANA-15 LCH-15 LCH-33 PRE-01 PRE-03 PRE-04 PRE-07 PRE-08 PRE-09 PRE-10 PRE-13 PRE-15 PRE-16 PRE-17 PRE-20 PRE-21 PRE-22 PRE-23 PRE-24 PRE-25 PRE-30 PRE-31 PRE-32 PRJ-09 UIC-20 | #658 #656 #652 #651 |
| PRE-07 | PR | - | ANA-15 LCH-15 LCH-33 PRE-03 PRE-04 PRE-06 PRE-08 PRE-09 PRE-10 PRE-13 PRE-15 PRE-16 PRE-20 PRE-21 PRE-22 PRE-23 PRE-24 PRE-25 PRE-30 PRE-31 PRE-32 PRJ-09 UIC-20 | #658 #656 #652 #651 |
| PRE-08 | PR | - | ANA-15 LCH-15 LCH-33 PRE-03 PRE-04 PRE-05 PRE-06 PRE-07 PRE-09 PRE-13 PRE-15 PRE-16 PRE-18 PRE-21 PRE-23 PRE-24 PRE-25 PRE-27 PRE-30 PRE-32 PRJ-09 PRJ-22 UIC-20 | #658 #656 #652 #651 |
| PRE-09 | INV | PRE-01 | ANA-15 LCH-15 LCH-33 PRE-01 PRE-03 PRE-04 PRE-06 PRE-07 PRE-08 PRE-13 PRE-15 PRE-16 PRE-17 PRE-21 PRE-23 PRE-24 PRE-25 PRE-30 PRE-32 PRJ-09 UIC-20 | #658 #656 #652 #651 |
| PRE-10 | PR | PRE-06 PR #658 | PRE-03 PRE-04 PRE-06 PRE-07 PRE-18 PRE-19 PRE-20 PRE-22 PRE-30 PRE-31 PRE-32 | #658 #656 |
| PRE-11 | PR | - | OPT-19 PRE-12 PRE-16 PRE-21 PRE-22 PRJ-09 UIC-20 | - |
| PRE-12 | PR | - | PRE-11 PRE-21 PRE-22 PRJ-09 UIC-20 | - |
| PRE-13 | DEC | PRE-12 | ANA-15 LCH-15 LCH-33 PRE-03 PRE-04 PRE-06 PRE-07 PRE-08 PRE-09 PRE-15 PRE-16 PRE-21 PRE-23 PRE-24 PRE-25 PRE-30 PRE-32 PRJ-09 UIC-20 | #658 #656 #652 #651 |
| PRE-14 | PR | - | DOE-03 DOE-16 LCH-16 PER-02 PRE-15 PRE-27 PRE-32 | #651 |
| PRE-15 | PR | PRE-14 | ANA-15 DOE-03 DOE-16 LCH-15 LCH-16 LCH-33 PRE-03 PRE-04 PRE-06 PRE-07 PRE-08 PRE-09 PRE-13 PRE-14 PRE-16 PRE-21 PRE-23 PRE-24 PRE-25 PRE-27 PRE-30 PRE-32 PRJ-09 UIC-20 | #658 #656 #652 #651 |
| PRE-16 | PR | - | ANA-15 LCH-15 LCH-33 OPT-19 PRE-01 PRE-03 PRE-04 PRE-05 PRE-06 PRE-07 PRE-08 PRE-09 PRE-11 PRE-13 PRE-15 PRE-17 PRE-21 PRE-23 PRE-24 PRE-25 PRE-30 PRE-32 PRJ-09 PRJ-22 UIC-20 | #658 #656 #652 #651 |
| PRE-17 | PR | PRE-01 PR #658 PR #658 | PRE-01 PRE-06 PRE-09 PRE-16 | #658 |
| PRE-18 | PR | PRE-10 PR #658 | PRE-05 PRE-08 PRE-10 PRE-19 PRE-23 PRE-24 PRE-27 | #658 |
| PRE-19 | PR | PRE-01 | PRE-03 PRE-04 PRE-05 PRE-10 PRE-18 | #658 #656 |
| PRE-20 | PR | PRE-07 | PRE-03 PRE-04 PRE-06 PRE-07 PRE-10 PRE-22 PRE-30 PRE-31 PRE-32 | #658 #656 |
| PRE-21 | PR | - | ANA-15 LCH-15 LCH-33 PRE-03 PRE-04 PRE-06 PRE-07 PRE-08 PRE-09 PRE-11 PRE-12 PRE-13 PRE-15 PRE-16 PRE-22 PRE-23 PRE-24 PRE-25 PRE-30 PRE-32 PRJ-09 UIC-20 | #658 #656 #652 #651 |
| PRE-22 | PR | PRE-11 PRE-12 PRE-21 | PRE-03 PRE-04 PRE-06 PRE-07 PRE-10 PRE-11 PRE-12 PRE-20 PRE-21 PRE-23 PRE-30 PRE-31 PRE-32 PRJ-09 UIC-20 | #658 #656 |
| PRE-23 | PR | PRE-04 PRE-07 PRE-13 PRE-21 EXE-01 EXE-02 EXE-07 EXE-09 | ANA-15 LCH-01 LCH-15 LCH-33 PRE-03 PRE-04 PRE-05 PRE-06 PRE-07 PRE-08 PRE-09 PRE-13 PRE-15 PRE-16 PRE-18 PRE-21 PRE-22 PRE-24 PRE-25 PRE-27 PRE-30 PRE-32 PRJ-09 PRJ-22 UIC-20 | #658 #656 #652 #651 |
| PRE-24 | PR | PRE-23 | ANA-15 LCH-15 LCH-33 PRE-03 PRE-04 PRE-05 PRE-06 PRE-07 PRE-08 PRE-09 PRE-13 PRE-15 PRE-16 PRE-18 PRE-21 PRE-23 PRE-25 PRE-27 PRE-30 PRE-32 PRJ-09 PRJ-22 UIC-20 | #658 #656 #652 #651 |
| PRE-25 | PR | - | ANA-15 LCH-15 LCH-33 PRE-03 PRE-04 PRE-06 PRE-07 PRE-08 PRE-09 PRE-13 PRE-15 PRE-16 PRE-21 PRE-23 PRE-24 PRE-30 PRE-32 PRJ-09 UIC-20 | #658 #656 #652 #651 |
| PRE-26 | DEC | - | - | - |
| PRE-27 | PR | PRE-26 PRE-14 PER-02 | DOE-03 DOE-16 LCH-16 PRE-05 PRE-08 PRE-14 PRE-15 PRE-18 PRE-23 PRE-24 PRE-32 | #651 |
| PRE-28 | INV | - | - | - |
| PRE-29 | DEC | PER-03 PRE-28 PR #658 | - | #658 |
| PRE-30 | PR | PRE-29 | ANA-15 LCH-15 LCH-33 PRE-03 PRE-04 PRE-06 PRE-07 PRE-08 PRE-09 PRE-10 PRE-13 PRE-15 PRE-16 PRE-20 PRE-21 PRE-22 PRE-23 PRE-24 PRE-25 PRE-31 PRE-32 PRJ-09 UIC-20 | #658 #656 #652 #651 |
| PRE-31 | PR | PRE-29 | PRE-03 PRE-04 PRE-06 PRE-07 PRE-10 PRE-20 PRE-22 PRE-30 PRE-32 | #658 #656 |
| PRE-32 | PR | DOE-16 | ANA-15 DOE-03 DOE-16 LCH-09 LCH-15 LCH-16 LCH-30 LCH-33 PRE-03 PRE-04 PRE-06 PRE-07 PRE-08 PRE-09 PRE-10 PRE-13 PRE-14 PRE-15 PRE-16 PRE-20 PRE-21 PRE-22 PRE-23 PRE-24 PRE-25 PRE-27 PRE-30 PRE-31 PRJ-09 PRJ-22 UIC-20 | #658 #656 #652 #651 |
| BLD-01 | PR | - | BLD-02 BLD-03 BLD-04 BLD-05 BLD-06 BLD-09 BLD-10 BLD-12 BLD-13 BLD-14 BLD-15 BLD-16 BLD-17 BLD-18 BLD-20 PRJ-09 UIC-20 UIC-23 | - |
| BLD-02 | PR | BLD-01 | BLD-04 BLD-05 BLD-06 BLD-07 BLD-13 BLD-14 BLD-15 BLD-16 BLD-17 BLD-18 BLD-20 PRJ-09 UIC-20 UIC-21 | - |
| BLD-03 | PR | - | BLD-01 BLD-04 BLD-05 BLD-06 BLD-07 BLD-09 BLD-10 BLD-12 BLD-13 BLD-14 BLD-17 BLD-20 BLD-21 UIC-20 UIC-23 | - |
| BLD-04 | PR | - | BLD-01 BLD-02 BLD-03 BLD-05 BLD-06 BLD-07 BLD-09 BLD-10 BLD-12 BLD-13 BLD-14 BLD-15 BLD-16 BLD-17 BLD-18 BLD-20 BLD-21 PRJ-09 UIC-20 UIC-23 | - |
| BLD-05 | PR | - | BLD-01 BLD-02 BLD-03 BLD-04 BLD-06 BLD-07 BLD-13 BLD-14 BLD-15 BLD-16 BLD-17 BLD-18 BLD-20 BLD-21 PRJ-09 UIC-20 UIC-21 | - |
| BLD-06 | PR | - | BLD-01 BLD-02 BLD-03 BLD-04 BLD-05 BLD-07 BLD-09 BLD-10 BLD-12 BLD-13 BLD-14 BLD-17 BLD-20 BLD-21 UIC-20 UIC-21 UIC-23 | - |
| BLD-07 | PR | - | BLD-02 BLD-03 BLD-04 BLD-05 BLD-06 BLD-11 BLD-13 BLD-14 BLD-15 BLD-16 BLD-17 BLD-18 BLD-20 BLD-21 PRJ-09 UIC-20 UIC-21 | - |
| BLD-09 | PR | - | BLD-01 BLD-03 BLD-04 BLD-06 BLD-10 BLD-12 BLD-13 BLD-16 BLD-17 UIC-20 UIC-23 | - |
| BLD-10 | PR | - | BLD-01 BLD-03 BLD-04 BLD-06 BLD-09 BLD-12 BLD-13 BLD-17 BLD-18 PRJ-09 UIC-20 UIC-23 | - |
| BLD-11 | DEC | - | - | - |
| BLD-12 | PR | BLD-01 | BLD-01 BLD-03 BLD-04 BLD-06 BLD-09 BLD-10 BLD-11 BLD-13 BLD-15 BLD-17 BLD-18 BLD-20 PRJ-09 UIC-20 UIC-23 | - |
| BLD-13 | PR | - | BLD-01 BLD-02 BLD-03 BLD-04 BLD-05 BLD-06 BLD-07 BLD-09 BLD-10 BLD-12 BLD-14 BLD-15 BLD-16 BLD-17 BLD-18 BLD-20 BLD-21 PRJ-09 UIC-20 UIC-21 UIC-23 | - |
| BLD-14 | PR | PRE-29 PRE-30 PRE-31 BLD-16 | BLD-01 BLD-02 BLD-03 BLD-04 BLD-05 BLD-06 BLD-07 BLD-13 BLD-15 BLD-16 BLD-17 BLD-18 BLD-20 BLD-21 PRJ-09 UIC-20 | - |
| BLD-15 | PR | PRJ-23 | BLD-01 BLD-02 BLD-04 BLD-05 BLD-07 BLD-12 BLD-13 BLD-14 BLD-16 BLD-17 BLD-18 BLD-20 PRJ-09 UIC-20 | - |
| BLD-16 | INV | - | BLD-01 BLD-02 BLD-04 BLD-05 BLD-07 BLD-09 BLD-13 BLD-14 BLD-15 BLD-17 BLD-18 BLD-20 PRJ-09 UIC-20 | - |
| BLD-17 | PR | PER-02 BLD-12 | BLD-01 BLD-02 BLD-03 BLD-04 BLD-05 BLD-06 BLD-07 BLD-09 BLD-10 BLD-12 BLD-13 BLD-14 BLD-15 BLD-16 BLD-18 BLD-20 PRJ-09 UIC-20 UIC-23 | - |
| BLD-18 | PR | PRJ-23 | BLD-01 BLD-02 BLD-04 BLD-05 BLD-07 BLD-10 BLD-12 BLD-13 BLD-14 BLD-15 BLD-16 BLD-17 BLD-20 PRJ-09 UIC-20 | - |
| BLD-19 | PR | - | BLD-02 BLD-05 BLD-09 CAD-11 CON-11 DEV-19 DOE-07 EXE-09 OPT-20 PER-02 PER-08 RUN-33 UIC-17 UIC-22 | #655 #654 #652 #651 |
| BLD-20 | PR | PRE-32 | BLD-01 BLD-02 BLD-03 BLD-04 BLD-05 BLD-06 BLD-07 BLD-12 BLD-13 BLD-14 BLD-15 BLD-16 BLD-17 BLD-18 BLD-21 PRJ-09 UIC-20 | - |
| BLD-21 | PR | RUN-15 | BLD-03 BLD-04 BLD-05 BLD-06 BLD-07 BLD-11 BLD-13 BLD-14 BLD-19 BLD-20 UIC-20 | - |
| RUN-01 | PR | - | CAD-01 MOR-11 PRJ-09 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-03 RUN-04 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-14 RUN-15 RUN-16 RUN-17 RUN-18 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-26 RUN-27 RUN-28 RUN-29 RUN-30 RUN-31 RUN-32 RUN-34 UIC-19 UIC-20 UIC-24 | #654 |
| RUN-02 | DEC | - | - | - |
| RUN-03 | DEC | - | CAD-01 MOR-11 PRJ-09 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-04 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-14 RUN-15 RUN-16 RUN-17 RUN-18 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-26 RUN-27 RUN-28 RUN-29 RUN-30 RUN-31 RUN-32 RUN-34 UIC-19 UIC-20 UIC-24 | #654 |
| RUN-04 | PR | - | MOR-11 PRJ-09 RUN-01 RUN-03 RUN-05 RUN-12 RUN-13 RUN-14 RUN-17 RUN-18 RUN-25 RUN-26 RUN-27 RUN-29 RUN-31 RUN-32 RUN-34 UIC-19 UIC-20 | #654 |
| RUN-05 | PR | - | CAD-01 MOR-11 PRJ-09 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-04 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-14 RUN-15 RUN-16 RUN-17 RUN-18 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-26 RUN-27 RUN-28 RUN-29 RUN-30 RUN-31 RUN-32 RUN-34 UIC-19 UIC-20 UIC-24 | #654 |
| RUN-06 | PR | RUN-04 | CAD-01 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-05 RUN-07 RUN-08 RUN-09 RUN-10 RUN-11 RUN-12 RUN-13 RUN-15 RUN-16 RUN-17 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-28 RUN-29 RUN-30 RUN-34 UIC-20 UIC-24 | - |
| RUN-07 | PR | - | CAD-01 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-05 RUN-06 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-15 RUN-16 RUN-17 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-28 RUN-29 RUN-30 RUN-34 UIC-20 UIC-24 | - |
| RUN-08 | PR | - | CAD-01 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-05 RUN-06 RUN-07 RUN-09 RUN-10 RUN-12 RUN-13 RUN-15 RUN-16 RUN-17 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-28 RUN-29 RUN-30 RUN-34 UIC-20 UIC-24 | - |
| RUN-09 | PR | - | CAD-01 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-05 RUN-06 RUN-07 RUN-08 RUN-10 RUN-12 RUN-13 RUN-15 RUN-16 RUN-17 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-28 RUN-29 RUN-30 RUN-34 UIC-20 UIC-24 | - |
| RUN-10 | PR | - | CAD-01 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-11 RUN-12 RUN-13 RUN-15 RUN-16 RUN-17 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-28 RUN-29 RUN-30 RUN-33 RUN-34 UIC-20 UIC-24 | - |
| RUN-11 | PR | - | RUN-06 RUN-10 RUN-12 RUN-15 RUN-17 RUN-29 RUN-33 | - |
| RUN-12 | PR | - | CAD-01 MOR-11 PRJ-09 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-04 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-11 RUN-13 RUN-14 RUN-15 RUN-16 RUN-17 RUN-18 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-26 RUN-27 RUN-28 RUN-29 RUN-30 RUN-31 RUN-32 RUN-34 UIC-19 UIC-20 UIC-24 | #654 |
| RUN-13 | PR | RUN-12 | CAD-01 MOR-11 PRJ-09 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-04 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-14 RUN-15 RUN-16 RUN-17 RUN-18 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-26 RUN-27 RUN-28 RUN-29 RUN-30 RUN-31 RUN-32 RUN-34 UIC-19 UIC-20 UIC-24 | #654 |
| RUN-14 | PR | - | MOR-11 PRJ-09 RUN-01 RUN-03 RUN-04 RUN-05 RUN-12 RUN-13 RUN-16 RUN-17 RUN-18 RUN-25 RUN-26 RUN-27 RUN-29 RUN-31 RUN-32 RUN-34 UIC-19 UIC-20 | #654 |
| RUN-15 | PR | - | CAD-01 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-11 RUN-12 RUN-13 RUN-16 RUN-17 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-28 RUN-29 RUN-30 RUN-33 RUN-34 UIC-20 UIC-24 | - |
| RUN-16 | PR | - | CAD-01 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-14 RUN-15 RUN-17 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-27 RUN-28 RUN-29 RUN-30 RUN-31 RUN-34 UIC-20 UIC-24 | - |
| RUN-17 | PR | RUN-04 | CAD-01 MOR-11 PRJ-09 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-04 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-11 RUN-12 RUN-13 RUN-14 RUN-15 RUN-16 RUN-18 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-26 RUN-27 RUN-28 RUN-29 RUN-30 RUN-31 RUN-32 RUN-34 UIC-19 UIC-20 UIC-24 | #654 |
| RUN-18 | PR | - | MOR-11 PRJ-09 RUN-01 RUN-03 RUN-04 RUN-05 RUN-12 RUN-13 RUN-14 RUN-17 RUN-25 RUN-26 RUN-27 RUN-29 RUN-31 RUN-32 RUN-34 UIC-19 UIC-20 | #654 |
| RUN-19 | PR | - | CAD-01 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-15 RUN-16 RUN-17 RUN-20 RUN-21 RUN-24 RUN-25 RUN-28 RUN-29 RUN-30 RUN-34 UIC-20 UIC-24 | - |
| RUN-20 | PR | - | CAD-01 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-15 RUN-16 RUN-17 RUN-19 RUN-21 RUN-24 RUN-25 RUN-28 RUN-29 RUN-30 RUN-34 UIC-20 UIC-24 | - |
| RUN-21 | PR | - | CAD-01 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-15 RUN-16 RUN-17 RUN-19 RUN-20 RUN-24 RUN-25 RUN-28 RUN-29 RUN-30 RUN-34 UIC-20 UIC-24 | - |
| RUN-22 | PR | - | UIC-20 UIC-23 | - |
| RUN-24 | PR | - | CAD-01 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-15 RUN-16 RUN-17 RUN-19 RUN-20 RUN-21 RUN-25 RUN-28 RUN-29 RUN-30 RUN-34 UIC-20 UIC-24 | - |
| RUN-25 | PR | RUN-14 | CAD-01 MOR-11 PRJ-09 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-04 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-14 RUN-15 RUN-16 RUN-17 RUN-18 RUN-19 RUN-20 RUN-21 RUN-24 RUN-26 RUN-27 RUN-28 RUN-29 RUN-30 RUN-31 RUN-32 RUN-34 UIC-19 UIC-20 UIC-24 | #654 |
| RUN-26 | PR | - | CON-05 DOE-05 MOR-11 PRJ-08 PRJ-09 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-22 PRJ-31 PRJ-32 PRJ-33 RUN-01 RUN-03 RUN-04 RUN-05 RUN-12 RUN-13 RUN-14 RUN-17 RUN-18 RUN-25 RUN-27 RUN-29 RUN-31 RUN-32 RUN-34 UIC-19 UIC-20 | #654 #652 #651 |
| RUN-27 | PR | PR #654 | MOR-11 PRJ-09 RUN-01 RUN-03 RUN-04 RUN-05 RUN-12 RUN-13 RUN-14 RUN-16 RUN-17 RUN-18 RUN-25 RUN-26 RUN-29 RUN-31 RUN-32 RUN-34 UIC-19 UIC-20 | #654 |
| RUN-28 | PR | - | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-03 REN-04 REN-05 REN-07 REN-10 REN-12 RUN-01 RUN-03 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-15 RUN-16 RUN-17 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-29 RUN-30 RUN-34 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-17 UIC-19 UIC-20 UIC-24 UIC-26 | #655 #654 #652 #651 |
| RUN-29 | PR | - | CAD-01 MOR-11 PRJ-09 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-04 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-11 RUN-12 RUN-13 RUN-14 RUN-15 RUN-16 RUN-17 RUN-18 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-26 RUN-27 RUN-28 RUN-30 RUN-31 RUN-32 RUN-34 UIC-19 UIC-20 UIC-24 | #654 |
| RUN-30 | PR | PR #652 | CAD-01 LCH-19 OPT-21 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-15 RUN-16 RUN-17 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-28 RUN-29 RUN-34 UIC-20 UIC-24 | #652 |
| RUN-31 | PR | BLD-18 PRJ-23 | CON-05 DOE-05 MOR-11 PRJ-08 PRJ-09 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-22 PRJ-31 PRJ-32 PRJ-33 RUN-01 RUN-03 RUN-04 RUN-05 RUN-12 RUN-13 RUN-14 RUN-16 RUN-17 RUN-18 RUN-25 RUN-26 RUN-27 RUN-29 RUN-32 RUN-34 UIC-19 UIC-20 | #654 #652 #651 |
| RUN-32 | PR | PER-02 | MOR-11 PRJ-09 RUN-01 RUN-03 RUN-04 RUN-05 RUN-12 RUN-13 RUN-14 RUN-17 RUN-18 RUN-25 RUN-26 RUN-27 RUN-29 RUN-31 RUN-34 UIC-19 UIC-20 | #654 |
| RUN-33 | PR | - | BLD-19 CAD-11 CON-11 DEV-19 DOE-07 EXE-09 OPT-20 PER-02 PER-08 RUN-10 RUN-11 RUN-14 RUN-15 RUN-18 UIC-17 UIC-22 | #655 #654 #652 #651 |
| RUN-34 | PR | BLD-20 | CAD-01 MOR-11 PRJ-09 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-04 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-14 RUN-15 RUN-16 RUN-17 RUN-18 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-26 RUN-27 RUN-28 RUN-29 RUN-30 RUN-31 RUN-32 UIC-19 UIC-20 UIC-24 | #654 |
| ANA-01 | PR | - | ANA-09 ANA-12 ANA-14 UIC-12 | - |
| ANA-02 | PR | - | ANA-16 ANA-17 ANA-23 | - |
| ANA-03 | DEC | - | ANA-04 ANA-05 ANA-06 ANA-07 ANA-08 ANA-09 ANA-10 ANA-11 ANA-12 ANA-13 ANA-14 ANA-15 ANA-18 ANA-21 ANA-22 EXE-03 EXE-04 EXE-08 UIC-12 UIC-20 | - |
| ANA-04 | PR | - | ANA-03 ANA-05 ANA-06 ANA-07 ANA-08 ANA-09 ANA-10 ANA-11 ANA-12 ANA-13 ANA-14 ANA-15 ANA-18 ANA-21 ANA-22 EXE-03 EXE-04 EXE-08 UIC-12 UIC-20 | - |
| ANA-05 | PR | - | ANA-03 ANA-04 ANA-06 ANA-07 ANA-08 ANA-09 ANA-10 ANA-11 ANA-12 ANA-13 ANA-14 ANA-15 ANA-18 ANA-21 ANA-22 EXE-03 EXE-04 EXE-08 UIC-12 UIC-20 | - |
| ANA-06 | PR | - | ANA-03 ANA-04 ANA-05 ANA-07 ANA-08 ANA-09 ANA-10 ANA-11 ANA-12 ANA-13 ANA-14 ANA-15 ANA-18 ANA-21 ANA-22 EXE-03 EXE-04 EXE-08 UIC-12 UIC-20 | - |
| ANA-07 | PR | - | ANA-03 ANA-04 ANA-05 ANA-06 ANA-08 ANA-09 ANA-10 ANA-11 ANA-12 ANA-13 ANA-14 ANA-15 ANA-18 ANA-21 ANA-22 DOE-05 DOE-11 EXE-03 EXE-04 EXE-08 PRJ-25 UIC-12 UIC-20 | - |
| ANA-08 | PR | - | ANA-03 ANA-04 ANA-05 ANA-06 ANA-07 ANA-09 ANA-10 ANA-11 ANA-12 ANA-13 ANA-14 ANA-15 ANA-18 ANA-21 ANA-22 EXE-03 EXE-04 EXE-08 UIC-12 UIC-20 | - |
| ANA-09 | PR | - | ANA-01 ANA-03 ANA-04 ANA-05 ANA-06 ANA-07 ANA-08 ANA-10 ANA-11 ANA-12 ANA-13 ANA-14 ANA-15 ANA-18 ANA-21 ANA-22 EXE-03 EXE-04 EXE-08 UIC-12 UIC-20 | - |
| ANA-10 | PR | - | ANA-03 ANA-04 ANA-05 ANA-06 ANA-07 ANA-08 ANA-09 ANA-11 ANA-12 ANA-13 ANA-14 ANA-15 ANA-18 ANA-21 ANA-22 EXE-03 EXE-04 EXE-08 UIC-12 UIC-20 | - |
| ANA-11 | PR | - | ANA-03 ANA-04 ANA-05 ANA-06 ANA-07 ANA-08 ANA-09 ANA-10 ANA-12 ANA-13 ANA-14 ANA-15 ANA-18 ANA-21 ANA-22 EXE-03 EXE-04 EXE-08 UIC-12 UIC-20 | - |
| ANA-12 | PR | - | ANA-01 ANA-03 ANA-04 ANA-05 ANA-06 ANA-07 ANA-08 ANA-09 ANA-10 ANA-11 ANA-13 ANA-14 ANA-15 ANA-18 ANA-21 ANA-22 EXE-03 EXE-04 EXE-08 UIC-12 UIC-20 | - |
| ANA-13 | PR | ANA-12 ANA-19 | ANA-03 ANA-04 ANA-05 ANA-06 ANA-07 ANA-08 ANA-09 ANA-10 ANA-11 ANA-12 ANA-14 ANA-15 ANA-18 ANA-19 ANA-20 ANA-21 ANA-22 EXE-03 EXE-04 EXE-08 UIC-12 UIC-20 | - |
| ANA-14 | PR | ANA-03 | ANA-01 ANA-03 ANA-04 ANA-05 ANA-06 ANA-07 ANA-08 ANA-09 ANA-10 ANA-11 ANA-12 ANA-13 ANA-15 ANA-18 ANA-21 ANA-22 EXE-03 EXE-04 EXE-08 UIC-12 UIC-20 | - |
| ANA-15 | PR | - | ANA-03 ANA-04 ANA-05 ANA-06 ANA-07 ANA-08 ANA-09 ANA-10 ANA-11 ANA-12 ANA-13 ANA-14 ANA-18 ANA-21 ANA-22 DOE-02 DOE-03 DOE-05 DOE-07 DOE-08 DOE-09 DOE-11 DOE-12 DOE-16 DOE-17 EXE-03 EXE-04 EXE-08 LCH-14 LCH-15 LCH-33 MOR-11 OPT-01 OPT-02 OPT-05 OPT-07 OPT-08 OPT-11 OPT-15 OPT-16 OPT-18 OPT-19 OPT-23 OPT-24 OPT-26 PRE-03 PRE-04 PRE-06 PRE-07 PRE-08 PRE-09 PRE-13 PRE-15 PRE-16 PRE-21 PRE-23 PRE-24 PRE-25 PRE-30 PRE-32 PRJ-09 UIC-12 UIC-19 UIC-20 | #658 #656 #654 #652 #651 |
| ANA-16 | PR | - | ANA-02 ANA-17 ANA-23 | - |
| ANA-17 | PR | ANA-02 | ANA-02 ANA-16 ANA-23 | - |
| ANA-18 | PR | - | ANA-03 ANA-04 ANA-05 ANA-06 ANA-07 ANA-08 ANA-09 ANA-10 ANA-11 ANA-12 ANA-13 ANA-14 ANA-15 ANA-21 ANA-22 EXE-03 EXE-04 EXE-08 UIC-12 UIC-20 | - |
| ANA-19 | PR | - | ANA-13 ANA-20 ANA-21 | - |
| ANA-20 | INV | - | ANA-13 ANA-19 ANA-21 | - |
| ANA-21 | PR | - | ANA-03 ANA-04 ANA-05 ANA-06 ANA-07 ANA-08 ANA-09 ANA-10 ANA-11 ANA-12 ANA-13 ANA-14 ANA-15 ANA-18 ANA-19 ANA-20 ANA-22 EXE-03 EXE-04 EXE-08 UIC-12 UIC-20 | - |
| ANA-22 | PR | EXE-07 EXE-09 ANA-15 | ANA-03 ANA-04 ANA-05 ANA-06 ANA-07 ANA-08 ANA-09 ANA-10 ANA-11 ANA-12 ANA-13 ANA-14 ANA-15 ANA-18 ANA-21 EXE-03 EXE-04 EXE-08 UIC-12 UIC-20 | - |
| ANA-23 | PR | PRE-29 PRE-30 PRE-31 | ANA-02 ANA-16 ANA-17 | - |
| OPT-01 | PR | - | ANA-15 CAD-01 MOR-11 OPT-02 OPT-05 OPT-06 OPT-07 OPT-08 OPT-09 OPT-10 OPT-11 OPT-12 OPT-13 OPT-14 OPT-15 OPT-16 OPT-17 OPT-18 OPT-19 OPT-21 OPT-22 OPT-23 OPT-24 OPT-25 OPT-26 PRJ-04 PRJ-09 PRJ-25 REN-03 REN-04 REN-05 REN-07 REN-08 REN-09 REN-10 REN-12 UIC-20 UIC-22 | #654 |
| OPT-02 | DEC | - | ANA-15 CAD-01 MOR-11 OPT-01 OPT-05 OPT-06 OPT-07 OPT-08 OPT-09 OPT-10 OPT-11 OPT-12 OPT-13 OPT-14 OPT-15 OPT-16 OPT-17 OPT-18 OPT-19 OPT-21 OPT-22 OPT-23 OPT-24 OPT-25 OPT-26 PRJ-09 PRJ-25 REN-07 UIC-20 UIC-22 | #654 |
| OPT-05 | PR | - | ANA-15 CAD-01 MOR-11 OPT-01 OPT-02 OPT-06 OPT-07 OPT-08 OPT-09 OPT-10 OPT-11 OPT-12 OPT-13 OPT-14 OPT-15 OPT-16 OPT-17 OPT-18 OPT-19 OPT-21 OPT-22 OPT-23 OPT-24 OPT-25 OPT-26 PRJ-09 PRJ-25 REN-07 UIC-20 UIC-22 | #654 |
| OPT-06 | PR | - | CAD-01 OPT-01 OPT-02 OPT-05 OPT-07 OPT-08 OPT-09 OPT-10 OPT-12 OPT-13 OPT-14 OPT-15 OPT-17 OPT-18 OPT-21 OPT-22 OPT-25 OPT-26 PRJ-25 REN-07 UIC-20 UIC-22 | - |
| OPT-07 | PR | OPT-06 | ANA-15 CAD-01 MOR-11 OPT-01 OPT-02 OPT-05 OPT-06 OPT-08 OPT-09 OPT-10 OPT-11 OPT-12 OPT-13 OPT-14 OPT-15 OPT-16 OPT-17 OPT-18 OPT-19 OPT-21 OPT-22 OPT-23 OPT-24 OPT-25 OPT-26 PRJ-09 PRJ-25 REN-07 UIC-20 UIC-22 | #654 |
| OPT-08 | PR | - | ANA-15 CAD-01 MOR-11 OPT-01 OPT-02 OPT-05 OPT-06 OPT-07 OPT-09 OPT-10 OPT-11 OPT-12 OPT-13 OPT-14 OPT-15 OPT-16 OPT-17 OPT-18 OPT-19 OPT-20 OPT-21 OPT-22 OPT-23 OPT-24 OPT-25 OPT-26 PRJ-09 PRJ-25 REN-07 UIC-20 UIC-22 | #654 |
| OPT-09 | PR | - | CAD-01 OPT-01 OPT-02 OPT-05 OPT-06 OPT-07 OPT-08 OPT-10 OPT-12 OPT-13 OPT-14 OPT-15 OPT-17 OPT-18 OPT-21 OPT-22 OPT-25 OPT-26 PRJ-25 REN-07 UIC-20 UIC-22 | - |
| OPT-10 | PR | RUN-15 | CAD-01 OPT-01 OPT-02 OPT-05 OPT-06 OPT-07 OPT-08 OPT-09 OPT-12 OPT-13 OPT-14 OPT-15 OPT-17 OPT-18 OPT-20 OPT-21 OPT-22 OPT-25 OPT-26 PRJ-25 REN-07 UIC-20 UIC-22 | - |
| OPT-11 | PR | - | ANA-15 MOR-11 OPT-01 OPT-02 OPT-05 OPT-07 OPT-08 OPT-15 OPT-16 OPT-18 OPT-19 OPT-23 OPT-24 OPT-26 PRJ-09 UIC-20 | #654 |
| OPT-12 | PR | - | CAD-01 OPT-01 OPT-02 OPT-05 OPT-06 OPT-07 OPT-08 OPT-09 OPT-10 OPT-13 OPT-14 OPT-15 OPT-17 OPT-18 OPT-21 OPT-22 OPT-25 OPT-26 PRJ-25 REN-07 UIC-20 UIC-22 | - |
| OPT-13 | PR | - | CAD-01 OPT-01 OPT-02 OPT-05 OPT-06 OPT-07 OPT-08 OPT-09 OPT-10 OPT-12 OPT-14 OPT-15 OPT-17 OPT-18 OPT-21 OPT-22 OPT-25 OPT-26 PRJ-25 REN-07 UIC-20 UIC-22 | - |
| OPT-14 | PR | OPT-08 | CAD-01 OPT-01 OPT-02 OPT-05 OPT-06 OPT-07 OPT-08 OPT-09 OPT-10 OPT-12 OPT-13 OPT-15 OPT-17 OPT-18 OPT-20 OPT-21 OPT-22 OPT-25 OPT-26 PRJ-25 REN-07 UIC-20 UIC-22 | - |
| OPT-15 | PR | OPT-26 | ANA-15 CAD-01 MOR-11 OPT-01 OPT-02 OPT-05 OPT-06 OPT-07 OPT-08 OPT-09 OPT-10 OPT-11 OPT-12 OPT-13 OPT-14 OPT-16 OPT-17 OPT-18 OPT-19 OPT-21 OPT-22 OPT-23 OPT-24 OPT-25 OPT-26 PRJ-09 PRJ-25 REN-07 UIC-20 UIC-22 | #654 |
| OPT-16 | PR | - | ANA-15 MOR-11 OPT-01 OPT-02 OPT-05 OPT-07 OPT-08 OPT-11 OPT-15 OPT-18 OPT-19 OPT-20 OPT-23 OPT-24 OPT-26 PRJ-09 UIC-20 | #654 |
| OPT-17 | PR | - | CAD-01 OPT-01 OPT-02 OPT-05 OPT-06 OPT-07 OPT-08 OPT-09 OPT-10 OPT-12 OPT-13 OPT-14 OPT-15 OPT-18 OPT-21 OPT-22 OPT-25 OPT-26 PRJ-25 REN-07 UIC-20 UIC-22 | - |
| OPT-18 | PR | - | ANA-15 CAD-01 MOR-11 OPT-01 OPT-02 OPT-05 OPT-06 OPT-07 OPT-08 OPT-09 OPT-10 OPT-11 OPT-12 OPT-13 OPT-14 OPT-15 OPT-16 OPT-17 OPT-19 OPT-21 OPT-22 OPT-23 OPT-24 OPT-25 OPT-26 PRJ-09 PRJ-25 REN-07 UIC-20 UIC-22 | #654 |
| OPT-19 | PR | - | ANA-15 MOR-11 OPT-01 OPT-02 OPT-05 OPT-07 OPT-08 OPT-11 OPT-15 OPT-16 OPT-18 OPT-23 OPT-24 OPT-26 PRE-11 PRE-16 PRJ-09 UIC-20 | #654 |
| OPT-20 | PR | PR #655 PR #654 | BLD-19 CAD-11 CON-11 DEV-19 DOE-07 EXE-09 OPT-08 OPT-10 OPT-14 OPT-16 PER-02 PER-08 RUN-33 UIC-17 UIC-22 | #655 #654 #652 #651 |
| OPT-21 | PR | OPT-02 RUN-30 PR #652 | CAD-01 OPT-01 OPT-02 OPT-05 OPT-06 OPT-07 OPT-08 OPT-09 OPT-10 OPT-12 OPT-13 OPT-14 OPT-15 OPT-17 OPT-18 OPT-22 OPT-25 OPT-26 PRJ-25 REN-07 RUN-30 UIC-20 UIC-22 | #652 |
| OPT-22 | PR | CAD-01 PRJ-25 PR #655 PR #654 PR #655 | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-14 OPT-01 OPT-02 OPT-05 OPT-06 OPT-07 OPT-08 OPT-09 OPT-10 OPT-12 OPT-13 OPT-14 OPT-15 OPT-17 OPT-18 OPT-21 OPT-25 OPT-26 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-20 UIC-22 UIC-26 | #655 #654 #652 #651 |
| OPT-23 | PR | BLD-18 PRJ-23 | ANA-15 MOR-11 OPT-01 OPT-02 OPT-05 OPT-07 OPT-08 OPT-11 OPT-15 OPT-16 OPT-18 OPT-19 OPT-24 OPT-26 PRJ-09 UIC-20 | #654 |
| OPT-24 | PR | PER-02 | ANA-15 MOR-11 OPT-01 OPT-02 OPT-05 OPT-07 OPT-08 OPT-11 OPT-15 OPT-16 OPT-18 OPT-19 OPT-23 OPT-26 PRJ-09 UIC-20 | #654 |
| OPT-25 | PR | - | CAD-01 OPT-01 OPT-02 OPT-05 OPT-06 OPT-07 OPT-08 OPT-09 OPT-10 OPT-12 OPT-13 OPT-14 OPT-15 OPT-17 OPT-18 OPT-21 OPT-22 OPT-26 PRJ-25 REN-07 UIC-20 UIC-22 | - |
| OPT-26 | PR | BLD-20 | ANA-15 CAD-01 MOR-11 OPT-01 OPT-02 OPT-05 OPT-06 OPT-07 OPT-08 OPT-09 OPT-10 OPT-11 OPT-12 OPT-13 OPT-14 OPT-15 OPT-16 OPT-17 OPT-18 OPT-19 OPT-21 OPT-22 OPT-23 OPT-24 OPT-25 PRJ-09 PRJ-25 REN-07 UIC-20 UIC-22 | #654 |
| PRJ-01 | PR | - | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-14 OPT-22 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| PRJ-02 | DEC | - | - | - |
| PRJ-16 | PR | - | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-08 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-31 PRJ-32 PRJ-33 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-26 RUN-28 RUN-31 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-20 UIC-26 | #655 #654 #652 #651 |
| PRJ-17 | PR | - | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-08 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-31 PRJ-32 PRJ-33 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-26 RUN-28 RUN-31 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-20 UIC-26 | #655 #654 #652 #651 |
| PRJ-18 | PR | PRJ-19 | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-08 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-31 PRJ-32 PRJ-33 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-26 RUN-28 RUN-31 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-20 UIC-26 | #655 #654 #652 #651 |
| PRJ-20 | CLOSE | - | - | - |
| PRJ-21 | PR | - | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| PRJ-24 | PR | - | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| PRJ-03 | PR | - | CAD-01 CAD-03 CAD-06 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 DOE-19 EXE-06 EXE-08 EXE-22 MOR-14 OPT-22 PRJ-01 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-01 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| PRJ-04 | PR | PRJ-03 | CAD-01 CAD-03 CAD-06 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 DOE-19 EXE-06 EXE-08 MOR-14 OPT-01 OPT-22 PRJ-01 PRJ-03 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-03 REN-04 REN-05 REN-07 REN-08 REN-09 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| PRJ-05 | DEC | - | - | - |
| PRJ-06 | PR | PRJ-05 PRJ-03 | CAD-01 CAD-03 CAD-06 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DEV-21 DEV-24 DOE-05 DOE-19 EXE-02 EXE-06 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| PRJ-07 | DEC | - | - | - |
| PRJ-34 | DEC | - | - | - |
| PRJ-08 | PR | PRJ-34 PRJ-03 | CON-05 DOE-05 EXE-06 PRJ-11 PRJ-12 PRJ-13 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-22 PRJ-31 PRJ-32 PRJ-33 PRJ-35 PRJ-36 REN-10 RUN-26 RUN-31 UIC-20 | #652 #651 |
| PRJ-09 | PR | PRJ-08 | ANA-15 BLD-01 BLD-02 BLD-04 BLD-05 BLD-07 BLD-10 BLD-12 BLD-13 BLD-14 BLD-15 BLD-16 BLD-17 BLD-18 BLD-20 CAD-03 CAD-05 CAD-06 CAD-09 CON-01 CON-02 CON-05 CON-06 DOE-02 DOE-03 DOE-05 DOE-07 DOE-08 DOE-09 DOE-11 DOE-12 DOE-16 DOE-17 LCH-02 LCH-03 LCH-04 LCH-05 LCH-06 LCH-07 LCH-10 LCH-12 LCH-13 LCH-14 LCH-15 LCH-16 LCH-28 LCH-33 LCH-34 MOR-11 OPT-01 OPT-02 OPT-05 OPT-07 OPT-08 OPT-11 OPT-15 OPT-16 OPT-18 OPT-19 OPT-23 OPT-24 OPT-26 PRE-03 PRE-04 PRE-06 PRE-07 PRE-08 PRE-09 PRE-11 PRE-12 PRE-13 PRE-15 PRE-16 PRE-21 PRE-22 PRE-23 PRE-24 PRE-25 PRE-30 PRE-32 RUN-01 RUN-03 RUN-04 RUN-05 RUN-12 RUN-13 RUN-14 RUN-17 RUN-18 RUN-25 RUN-26 RUN-27 RUN-29 RUN-31 RUN-32 RUN-34 UIC-19 UIC-20 | #658 #656 #654 #652 #651 |
| PRJ-10 | DEC | - | - | - |
| PRJ-11 | PR | PRJ-10 | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-08 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-31 PRJ-32 PRJ-33 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| PRJ-12 | PR | - | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-06 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-08 PRJ-11 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| PRJ-35 | PR | PRJ-01 | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-06 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-08 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| PRJ-36 | PR | - | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-06 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-08 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| PRJ-13 | PR | - | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-06 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-08 PRJ-11 PRJ-12 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| PRJ-14 | PR | - | CAD-01 CAD-03 CAD-06 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DEV-21 DEV-22 DEV-24 DOE-05 DOE-19 EXE-02 EXE-06 EXE-08 LCH-07 LCH-14 LCH-18 LCH-30 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-06 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| PRJ-15 | PR | PRJ-14 | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| PRJ-22 | PR | PRJ-34 | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 LCH-33 MOR-14 OPT-22 PRE-03 PRE-08 PRE-16 PRE-23 PRE-24 PRE-32 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-08 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-24 PRJ-25 PRJ-26 PRJ-31 PRJ-32 PRJ-33 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-26 RUN-28 RUN-31 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-20 UIC-26 | #656 #655 #654 #652 #651 |
| PRJ-23 | DEC | - | - | - |
| PRJ-19 | PR | - | CAD-01 CAD-03 CAD-06 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-06 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-08 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-31 PRJ-32 PRJ-33 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-26 RUN-28 RUN-31 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-20 UIC-26 | #655 #654 #652 #651 |
| PRJ-25 | PR | - | ANA-07 CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 DOE-11 EXE-08 MOR-14 OPT-01 OPT-02 OPT-05 OPT-06 OPT-07 OPT-08 OPT-09 OPT-10 OPT-12 OPT-13 OPT-14 OPT-15 OPT-17 OPT-18 OPT-21 OPT-22 OPT-25 OPT-26 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-03 REN-04 REN-05 REN-07 REN-10 REN-12 RUN-01 RUN-03 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-15 RUN-16 RUN-17 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-28 RUN-29 RUN-30 RUN-34 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-20 UIC-22 UIC-24 UIC-26 | #655 #654 #652 #651 |
| PRJ-26 | PR | - | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DEV-20 DOE-05 EXE-08 EXE-09 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| PRJ-27 | CLOSE | - | - | - |
| PRJ-28 | CLOSE | - | - | - |
| PRJ-29 | CLOSE | - | - | - |
| PRJ-30 | CLOSE | - | - | - |
| PRJ-31 | PR | PER-02 | CON-05 DOE-05 PRJ-08 PRJ-11 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-22 PRJ-32 PRJ-33 RUN-26 RUN-31 UIC-20 | #652 #651 |
| PRJ-32 | PR | PRJ-19 PER-03 | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-08 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-31 PRJ-33 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-26 RUN-28 RUN-31 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-20 UIC-26 | #655 #654 #652 #651 |
| PRJ-33 | PR | - | CON-05 DEV-10 DOE-02 DOE-05 PER-02 PRJ-08 PRJ-11 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-22 PRJ-31 PRJ-32 RUN-26 RUN-31 UIC-19 UIC-20 | #652 #651 |
| REN-01 | PR | - | EXE-22 PRJ-03 REN-02 REN-07 UIC-19 | - |
| REN-02 | PR | - | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 EXE-22 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-01 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| REN-03 | PR | REN-02 | CAD-01 OPT-01 PRJ-04 PRJ-25 REN-04 REN-05 REN-07 REN-08 REN-09 REN-10 REN-12 RUN-01 RUN-03 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-15 RUN-16 RUN-17 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-28 RUN-29 RUN-30 RUN-34 UIC-20 UIC-24 | - |
| REN-04 | PR | - | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-14 OPT-01 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-03 REN-05 REN-07 REN-08 REN-09 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| REN-05 | PR | - | CAD-01 OPT-01 PRJ-04 PRJ-25 REN-03 REN-04 REN-07 REN-08 REN-09 REN-10 REN-12 RUN-01 RUN-03 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-15 RUN-16 RUN-17 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-28 RUN-29 RUN-30 RUN-34 UIC-20 UIC-24 | - |
| REN-06 | DEC | - | - | - |
| REN-07 | PR | REN-06 | CAD-01 CAD-03 CAD-06 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DEV-20 DOE-05 DOE-19 EXE-06 EXE-08 EXE-09 EXE-22 MOR-14 OPT-01 OPT-02 OPT-05 OPT-06 OPT-07 OPT-08 OPT-09 OPT-10 OPT-12 OPT-13 OPT-14 OPT-15 OPT-17 OPT-18 OPT-21 OPT-22 OPT-25 OPT-26 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-01 REN-02 REN-03 REN-04 REN-05 REN-08 REN-09 REN-10 REN-12 RUN-01 RUN-03 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-15 RUN-16 RUN-17 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-28 RUN-29 RUN-30 RUN-34 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-20 UIC-22 UIC-24 UIC-26 | #655 #654 #652 #651 |
| REN-08 | PR | - | OPT-01 PRJ-04 REN-03 REN-04 REN-05 REN-07 REN-09 REN-10 REN-12 | - |
| REN-09 | PR | - | OPT-01 PRJ-04 REN-03 REN-04 REN-05 REN-07 REN-08 REN-10 REN-12 | - |
| REN-10 | PR | REN-07 REN-08 REN-02 REN-03 REN-05 OPT-01 | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-06 EXE-08 MOR-14 OPT-01 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-08 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-03 REN-04 REN-05 REN-07 REN-08 REN-09 REN-12 RUN-01 RUN-03 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-15 RUN-16 RUN-17 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-28 RUN-29 RUN-30 RUN-34 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-20 UIC-24 UIC-26 | #655 #654 #652 #651 |
| REN-11 | DEC | - | - | - |
| REN-12 | PR | REN-11 | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-14 OPT-01 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-03 REN-04 REN-05 REN-07 REN-08 REN-09 REN-10 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| REN-13 | PR | - | UIC-07 | - |
| EXE-01 | DEC | - | EXE-05 EXE-07 | - |
| EXE-02 | PR | - | DEV-21 DEV-24 EXE-03 EXE-04 EXE-05 EXE-06 EXE-08 EXE-09 PRJ-06 PRJ-14 UIC-05 UIC-26 | - |
| EXE-03 | PR | EXE-02 | ANA-03 ANA-04 ANA-05 ANA-06 ANA-07 ANA-08 ANA-09 ANA-10 ANA-11 ANA-12 ANA-13 ANA-14 ANA-15 ANA-18 ANA-21 ANA-22 EXE-02 EXE-04 EXE-05 EXE-08 EXE-09 UIC-12 UIC-20 | - |
| EXE-04 | PR | EXE-01 EXE-03 | ANA-03 ANA-04 ANA-05 ANA-06 ANA-07 ANA-08 ANA-09 ANA-10 ANA-11 ANA-12 ANA-13 ANA-14 ANA-15 ANA-18 ANA-21 ANA-22 EXE-02 EXE-03 EXE-05 EXE-08 EXE-09 UIC-12 UIC-20 | - |
| EXE-05 | PR | - | DEV-12 DEV-13 EXE-01 EXE-02 EXE-03 EXE-04 EXE-07 EXE-22 | #658 |
| EXE-06 | PR | - | CAD-03 CAD-06 DEV-21 DEV-24 DOE-19 EXE-02 PRJ-03 PRJ-04 PRJ-06 PRJ-08 PRJ-12 PRJ-13 PRJ-14 PRJ-19 PRJ-35 PRJ-36 REN-07 REN-10 UIC-05 UIC-26 | #654 #652 |
| EXE-07 | DEC | EXE-01 | EXE-01 EXE-05 | - |
| EXE-08 | PR | EXE-02 EXE-03 EXE-07 | ANA-03 ANA-04 ANA-05 ANA-06 ANA-07 ANA-08 ANA-09 ANA-10 ANA-11 ANA-12 ANA-13 ANA-14 ANA-15 ANA-18 ANA-21 ANA-22 CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-02 EXE-03 EXE-04 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-12 UIC-19 UIC-20 UIC-26 | #655 #654 #652 #651 |
| EXE-09 | PR | EXE-07 | BLD-19 CAD-11 CON-11 DEV-19 DEV-20 DOE-07 EXE-02 EXE-03 EXE-04 OPT-20 PER-02 PER-08 PRJ-26 REN-07 RUN-33 UIC-17 UIC-22 | #655 #654 #652 #651 |
| EXE-10 | DEC | - | UIC-16 | - |
| EXE-11 | PR | EXE-10 | CAD-15 EXE-12 LCH-10 LCH-31 | - |
| EXE-12 | PR | - | CAD-15 EXE-11 LCH-10 LCH-31 | - |
| EXE-13 | DEC | EXE-01 | - | - |
| EXE-14 | INV | EXE-01 | - | - |
| EXE-15 | CLOSE | - | - | - |
| EXE-16 | CLOSE | - | - | - |
| EXE-17 | CLOSE | - | - | - |
| EXE-18 | CLOSE | - | - | - |
| EXE-19 | CLOSE | - | - | - |
| EXE-20 | CLOSE | - | - | - |
| EXE-21 | PR | - | CON-09 | #658 |
| EXE-22 | PR | EXE-14 EXE-05 | EXE-05 MOR-16 PRJ-03 REN-01 REN-02 REN-07 UIC-19 | #658 #655 #654 |
| PER-01 | DEC | - | PER-03 PER-10 | - |
| PER-02 | PR | - | BLD-19 CAD-11 CON-11 DEV-19 DOE-02 DOE-07 DOE-12 DOE-16 DOE-17 EXE-09 OPT-20 PER-04 PER-07 PER-08 PRE-14 PRE-15 PRJ-33 RUN-33 UIC-17 UIC-22 | #655 #654 #652 #651 |
| PER-03 | DEC | - | PER-01 PER-10 | - |
| PER-04 | PR | PER-02 PER-03 | PER-02 PER-05 PER-08 | - |
| PER-05 | PR | - | CAD-11 DEV-13 PER-04 | #655 #654 |
| PER-06 | DEC | - | - | - |
| PER-07 | PR | PER-06 | DOE-10 DOE-12 DOE-16 PER-02 | - |
| PER-08 | PR | PER-01 PER-02 | BLD-19 CAD-11 CON-11 DEV-19 DOE-07 EXE-09 OPT-20 PER-02 PER-04 RUN-33 UIC-17 UIC-22 | #655 #654 #652 #651 |
| PER-09 | DEC | PER-06 | - | - |
| PER-10 | DEC | - | PER-01 PER-03 | - |
| PER-11 | CLOSE | - | - | - |
| UIC-01 | PR | - | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| UIC-02 | INV | UIC-01 | DEV-11 DEV-21 DEV-24 DEV-25 MOR-06 MOR-07 | #658 #654 |
| UIC-03 | PR | UIC-01 | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| UIC-05 | PR | UIC-03 PRJ-14 | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DEV-21 DEV-24 DOE-05 EXE-02 EXE-06 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| UIC-06 | DEC | UIC-02 | - | - |
| UIC-07 | PR | UIC-01 PR #655 | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-05 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 REN-13 RUN-28 UIC-01 UIC-03 UIC-05 UIC-09 UIC-10 UIC-12 UIC-19 UIC-21 UIC-22 UIC-26 | #655 #654 #652 #651 |
| UIC-08 | DEC | UIC-02 | - | - |
| UIC-09 | PR | UIC-08 | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-10 UIC-19 UIC-26 | #655 #654 #652 #651 |
| UIC-10 | PR | UIC-03 UIC-02 | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-11 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-19 UIC-26 | #655 #654 #652 #651 |
| UIC-11 | DEC | UIC-02 UIC-03 | - | - |
| UIC-12 | PR | UIC-03 UIC-02 | ANA-01 ANA-03 ANA-04 ANA-05 ANA-06 ANA-07 ANA-08 ANA-09 ANA-10 ANA-11 ANA-12 ANA-13 ANA-14 ANA-15 ANA-18 ANA-21 ANA-22 EXE-03 EXE-04 EXE-08 MOR-01 UIC-07 UIC-13 UIC-20 UIC-21 UIC-22 | - |
| UIC-13 | PR | - | MOR-01 UIC-12 | - |
| UIC-14 | DEC | UIC-03 UIC-10 | DEV-17 UIC-18 UIC-21 | - |
| UIC-15 | PR | UIC-06 UIC-14 | - | - |
| UIC-16 | DEC | - | EXE-10 | - |
| UIC-17 | PR | UIC-16 | BLD-19 CAD-11 CON-11 DEV-19 DOE-07 EXE-09 OPT-20 PER-02 PER-08 RUN-33 UIC-22 | #655 #654 #652 #651 |
| UIC-18 | PR | - | DEV-17 UIC-14 UIC-21 | #655 #654 #652 #651 |
| UIC-19 | PR | - | ANA-15 CAD-01 CAD-03 CAD-04 CAD-05 CAD-06 CAD-07 CAD-09 CAD-12 CAD-13 CAD-15 CON-03 CON-04 CON-05 CON-06 CON-07 CON-12 DEV-10 DOE-02 DOE-03 DOE-05 DOE-07 DOE-08 DOE-09 DOE-11 DOE-12 DOE-16 DOE-17 DOE-19 EXE-08 EXE-22 LCH-02 LCH-06 LCH-07 LCH-14 LCH-18 LCH-27 LCH-29 LCH-30 MOR-11 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-09 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-33 PRJ-35 PRJ-36 REN-01 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-01 RUN-03 RUN-04 RUN-05 RUN-12 RUN-13 RUN-14 RUN-17 RUN-18 RUN-25 RUN-26 RUN-27 RUN-28 RUN-29 RUN-31 RUN-32 RUN-34 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-20 UIC-26 | #655 #654 #652 #651 |
| UIC-20 | PR | - | ANA-03 ANA-04 ANA-05 ANA-06 ANA-07 ANA-08 ANA-09 ANA-10 ANA-11 ANA-12 ANA-13 ANA-14 ANA-15 ANA-18 ANA-21 ANA-22 BLD-01 BLD-02 BLD-03 BLD-04 BLD-05 BLD-06 BLD-07 BLD-09 BLD-10 BLD-12 BLD-13 BLD-14 BLD-15 BLD-16 BLD-17 BLD-18 BLD-20 BLD-21 CAD-01 CAD-03 CAD-05 CAD-06 CAD-09 CON-01 CON-02 CON-03 CON-05 CON-06 CON-07 CON-12 DEV-10 DOE-02 DOE-03 DOE-05 DOE-06 DOE-07 DOE-08 DOE-09 DOE-11 DOE-12 DOE-13 DOE-16 DOE-17 DOE-19 DOE-20 EXE-03 EXE-04 EXE-08 LCH-02 LCH-03 LCH-06 LCH-07 LCH-13 LCH-14 LCH-15 LCH-16 LCH-28 LCH-33 LCH-34 MOR-01 MOR-02 MOR-03 MOR-11 MOR-17 MOR-22 MOR-23 OPT-01 OPT-02 OPT-05 OPT-06 OPT-07 OPT-08 OPT-09 OPT-10 OPT-11 OPT-12 OPT-13 OPT-14 OPT-15 OPT-16 OPT-17 OPT-18 OPT-19 OPT-21 OPT-22 OPT-23 OPT-24 OPT-25 OPT-26 PRE-03 PRE-04 PRE-06 PRE-07 PRE-08 PRE-09 PRE-11 PRE-12 PRE-13 PRE-15 PRE-16 PRE-21 PRE-22 PRE-23 PRE-24 PRE-25 PRE-30 PRE-32 PRJ-08 PRJ-09 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-22 PRJ-25 PRJ-31 PRJ-32 PRJ-33 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-04 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-14 RUN-15 RUN-16 RUN-17 RUN-18 RUN-19 RUN-20 RUN-21 RUN-22 RUN-24 RUN-25 RUN-26 RUN-27 RUN-28 RUN-29 RUN-30 RUN-31 RUN-32 RUN-34 UIC-12 UIC-19 UIC-22 UIC-23 UIC-24 | #658 #656 #655 #654 #652 #651 |
| UIC-21 | PR | UIC-16 | BLD-02 BLD-05 BLD-06 BLD-07 BLD-13 DEV-17 UIC-07 UIC-12 UIC-14 UIC-18 UIC-22 | - |
| UIC-22 | PR | PR #655 | BLD-19 CAD-01 CAD-11 CON-11 DEV-19 DOE-07 EXE-09 MOR-05 MOR-12 MOR-23 OPT-01 OPT-02 OPT-05 OPT-06 OPT-07 OPT-08 OPT-09 OPT-10 OPT-12 OPT-13 OPT-14 OPT-15 OPT-17 OPT-18 OPT-20 OPT-21 OPT-22 OPT-25 OPT-26 PER-02 PER-08 PRJ-25 REN-07 RUN-33 UIC-07 UIC-12 UIC-17 UIC-20 UIC-21 | #655 #654 #652 #651 |
| UIC-23 | PR | UIC-22 | BLD-01 BLD-03 BLD-04 BLD-06 BLD-09 BLD-10 BLD-12 BLD-13 BLD-17 RUN-22 UIC-20 | - |
| UIC-24 | PR | - | CAD-01 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-15 RUN-16 RUN-17 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-28 RUN-29 RUN-30 RUN-34 UIC-20 | - |
| UIC-25 | CLOSE | - | - | - |
| UIC-26 | PR | UIC-06 | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DEV-21 DEV-24 DOE-05 EXE-02 EXE-06 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 | #655 #654 #652 #651 |
| DEV-01 | DEC | - | DEV-02 DEV-12 DEV-21 DEV-24 MOR-07 | - |
| DEV-02 | PR | - | DEV-01 DEV-12 DEV-21 DEV-24 MOR-07 | - |
| DEV-03 | EXT | DEV-01 | - | #654 |
| DEV-04 | EXT | - | - | - |
| DEV-05 | EXT | - | - | - |
| DEV-06 | EXT | - | DEV-21 | #658 |
| DEV-07 | DEC | - | - | - |
| DEV-08 | EXT | DEV-07 | - | #658 #654 |
| DEV-10 | PR | PR #655 PR #654 PR #652 PR #651 | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DOE-05 EXE-08 MOR-01 MOR-02 MOR-03 MOR-05 MOR-14 MOR-17 MOR-22 MOR-23 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-33 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-20 UIC-26 | #655 #654 #652 #651 |
| DEV-11 | PR | - | DEV-21 DEV-24 DEV-25 MOR-06 MOR-07 UIC-02 | #658 #654 |
| DEV-12 | PR | - | DEV-01 DEV-02 DEV-13 DEV-21 DEV-24 EXE-05 MOR-07 | - |
| DEV-13 | PR | - | DEV-12 DEV-14 DEV-18 EXE-05 PER-05 | #655 #654 |
| DEV-14 | DEC | - | DEV-13 DEV-18 | - |
| DEV-15 | PR | DEV-14 | DEV-16 | - |
| DEV-16 | PR | DEV-15 | DEV-15 | - |
| DEV-17 | DEC | - | UIC-14 UIC-18 UIC-21 | - |
| DEV-18 | PR | - | DEV-13 DEV-14 | #655 #654 #652 #651 |
| DEV-19 | PR | PR #655 | BLD-19 CAD-11 CON-11 DOE-07 EXE-09 OPT-20 PER-02 PER-08 RUN-33 UIC-17 UIC-22 | #655 #654 #652 #651 |
| DEV-20 | PR | - | EXE-09 PRJ-26 REN-07 | - |
| DEV-21 | PR | - | DEV-01 DEV-02 DEV-06 DEV-11 DEV-12 DEV-24 DEV-25 EXE-02 EXE-06 MOR-06 MOR-07 PRJ-06 PRJ-14 UIC-02 UIC-05 UIC-26 | #658 #654 |
| DEV-22 | PR | - | DEV-24 PRJ-14 | - |
| DEV-23 | DEC | - | - | - |
| DEV-24 | PR | DEV-23 | DEV-01 DEV-02 DEV-11 DEV-12 DEV-21 DEV-22 DEV-25 EXE-02 EXE-06 MOR-06 MOR-07 PRJ-06 PRJ-14 UIC-02 UIC-05 UIC-26 | #658 #654 |
| DEV-25 | INV | - | DEV-11 DEV-21 DEV-24 MOR-06 MOR-07 UIC-02 | #658 #654 |

## 2. 선행 그래프 순환

- 순환 없음 (선행 그래프는 DAG).
- 선행에 적혔으나 존재하지 않는 ID: 없음

## 3. 열린 PR 머지 전 착수 불가

(a) `선행:` 에 PR 머지를 명시한 항목 — 머지 전 착수 불가. (b) 파일만 겹치는 항목 — 동시 수술 금지(1-2절)라 머지 후 리베이스 전제로 착수, 또는 PR 랜딩 뒤 착수.

### PR #658 — 선행 명시 6 · 파일 겹침 36
- (a) PRE-01 PRE-06 PRE-10 PRE-17 PRE-18 PRE-29
- (b) ANA-15 DEV-06 DEV-08 DEV-11 DEV-21 DEV-24 DEV-25 EXE-05 EXE-21 EXE-22 LCH-15 LCH-33 MOR-06 MOR-07 PRE-03 PRE-04 PRE-05 PRE-07 PRE-08 PRE-09 PRE-13 PRE-15 PRE-16 PRE-19 PRE-20 PRE-21 PRE-22 PRE-23 PRE-24 PRE-25 PRE-30 PRE-31 PRE-32 PRJ-09 UIC-02 UIC-20
### PR #656 — 선행 명시 2 · 파일 겹침 25
- (a) PRE-02 PRE-04
- (b) ANA-15 LCH-15 LCH-33 PRE-03 PRE-06 PRE-07 PRE-08 PRE-09 PRE-10 PRE-13 PRE-15 PRE-16 PRE-19 PRE-20 PRE-21 PRE-22 PRE-23 PRE-24 PRE-25 PRE-30 PRE-31 PRE-32 PRJ-09 PRJ-22 UIC-20
### PR #655 — 선행 명시 21 · 파일 겹침 65
- (a) DEV-10 DEV-19 MOR-02 MOR-03 MOR-04 MOR-05 MOR-06 MOR-07 MOR-09 MOR-12 MOR-15 MOR-17 MOR-19 MOR-20 MOR-21 MOR-22 MOR-23 OPT-20 OPT-22 UIC-07 UIC-22
- (b) BLD-19 CAD-01 CAD-03 CAD-07 CAD-09 CAD-11 CAD-12 CAD-15 CON-03 CON-05 CON-06 CON-11 DEV-13 DEV-18 DOE-05 DOE-07 EXE-08 EXE-09 EXE-22 MOR-01 MOR-08 MOR-11 MOR-13 MOR-14 PER-02 PER-05 PER-08 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 RUN-33 UIC-01 UIC-03 UIC-05 UIC-09 UIC-10 UIC-17 UIC-18 UIC-19 UIC-20 UIC-26
### PR #654 — 선행 명시 5 · 파일 겹침 120
- (a) DEV-10 MOR-11 OPT-20 OPT-22 RUN-27
- (b) ANA-15 BLD-19 CAD-01 CAD-03 CAD-06 CAD-07 CAD-09 CAD-11 CAD-12 CAD-15 CON-03 CON-05 CON-06 CON-11 DEV-03 DEV-08 DEV-11 DEV-13 DEV-18 DEV-19 DEV-21 DEV-24 DEV-25 DOE-05 DOE-07 DOE-19 EXE-06 EXE-08 EXE-09 EXE-22 LCH-13 MOR-01 MOR-02 MOR-03 MOR-04 MOR-05 MOR-06 MOR-07 MOR-10 MOR-12 MOR-13 MOR-14 MOR-16 MOR-17 MOR-21 MOR-22 MOR-23 OPT-01 OPT-02 OPT-05 OPT-07 OPT-08 OPT-11 OPT-15 OPT-16 OPT-18 OPT-19 OPT-23 OPT-24 OPT-26 PER-02 PER-05 PER-08 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-09 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-01 RUN-03 RUN-04 RUN-05 RUN-12 RUN-13 RUN-14 RUN-17 RUN-18 RUN-25 RUN-26 RUN-28 RUN-29 RUN-31 RUN-32 RUN-33 RUN-34 UIC-01 UIC-02 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-17 UIC-18 UIC-19 UIC-20 UIC-22 UIC-26
### PR #652 — 선행 명시 22 · 파일 겹침 99
- (a) DEV-10 DOE-11 LCH-01 LCH-02 LCH-03 LCH-04 LCH-06 LCH-07 LCH-08 LCH-10 LCH-13 LCH-14 LCH-15 LCH-16 LCH-17 LCH-19 LCH-23 LCH-25 LCH-27 LCH-28 OPT-21 RUN-30
- (b) ANA-15 BLD-19 CAD-01 CAD-03 CAD-06 CAD-07 CAD-09 CAD-11 CAD-12 CAD-15 CON-03 CON-05 CON-06 CON-11 DEV-18 DEV-19 DOE-02 DOE-03 DOE-05 DOE-07 DOE-08 DOE-09 DOE-12 DOE-16 DOE-17 DOE-19 EXE-06 EXE-08 EXE-09 LCH-05 LCH-12 LCH-29 LCH-33 MOR-14 OPT-20 OPT-22 PER-02 PER-08 PRE-03 PRE-04 PRE-06 PRE-07 PRE-08 PRE-09 PRE-13 PRE-15 PRE-16 PRE-21 PRE-23 PRE-24 PRE-25 PRE-30 PRE-32 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-08 PRJ-09 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-31 PRJ-32 PRJ-33 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-26 RUN-28 RUN-31 RUN-33 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-17 UIC-18 UIC-19 UIC-20 UIC-22 UIC-26
### PR #651 — 선행 명시 17 · 파일 겹침 95
- (a) DEV-10 LCH-01 LCH-02 LCH-03 LCH-07 LCH-08 LCH-10 LCH-13 LCH-14 LCH-15 LCH-16 LCH-17 LCH-18 LCH-19 LCH-26 LCH-28 LCH-30
- (b) ANA-15 BLD-19 CAD-01 CAD-03 CAD-07 CAD-09 CAD-11 CAD-12 CAD-15 CON-03 CON-05 CON-06 CON-11 DEV-18 DEV-19 DOE-03 DOE-05 DOE-07 DOE-16 EXE-08 EXE-09 LCH-06 LCH-12 LCH-27 LCH-29 LCH-33 MOR-14 OPT-20 OPT-22 PER-02 PER-08 PRE-03 PRE-04 PRE-05 PRE-06 PRE-07 PRE-08 PRE-09 PRE-13 PRE-14 PRE-15 PRE-16 PRE-21 PRE-23 PRE-24 PRE-25 PRE-27 PRE-30 PRE-32 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-08 PRJ-09 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-31 PRJ-32 PRJ-33 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-26 RUN-28 RUN-31 RUN-33 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-17 UIC-18 UIC-19 UIC-20 UIC-22 UIC-26

합계(중복 제거): PR 대기 198 (선행 명시 55 · 파일 겹침만 143)

## 4. 즉시 착수 가능 — 선행 없음 · 열린 PR 과 파일 겹침 없음

합계 119 / 364

- MOR (1): MOR-18(CLOSE)
- CAD (3): CAD-08(PR) CAD-10(EXT) CAD-14(PR)
- CON (4): CON-01(PR) CON-02(PR) CON-04(PR) CON-10(DEC)
- DOE (7): DOE-06(PR) DOE-10(PR) DOE-13(PR) DOE-14(DEC) DOE-15(CLOSE) DOE-18(DEC) DOE-20(PR)
- LCH (5): LCH-20(CLOSE) LCH-21(CLOSE) LCH-24(CLOSE) LCH-31(DEC) LCH-32(DEC)
- PRE (4): PRE-11(PR) PRE-12(PR) PRE-26(DEC) PRE-28(INV)
- BLD (11): BLD-01(PR) BLD-03(PR) BLD-04(PR) BLD-05(PR) BLD-06(PR) BLD-07(PR) BLD-09(PR) BLD-10(PR) BLD-11(DEC) BLD-13(PR) BLD-16(INV)
- RUN (13): RUN-02(DEC) RUN-07(PR) RUN-08(PR) RUN-09(PR) RUN-10(PR) RUN-11(PR) RUN-15(PR) RUN-16(PR) RUN-19(PR) RUN-20(PR) RUN-21(PR) RUN-22(PR) RUN-24(PR)
- ANA (17): ANA-01(PR) ANA-02(PR) ANA-03(DEC) ANA-04(PR) ANA-05(PR) ANA-06(PR) ANA-07(PR) ANA-08(PR) ANA-09(PR) ANA-10(PR) ANA-11(PR) ANA-12(PR) ANA-16(PR) ANA-18(PR) ANA-19(PR) ANA-20(INV) ANA-21(PR)
- OPT (6): OPT-06(PR) OPT-09(PR) OPT-12(PR) OPT-13(PR) OPT-17(PR) OPT-25(PR)
- PRJ (11): PRJ-02(DEC) PRJ-20(CLOSE) PRJ-05(DEC) PRJ-07(DEC) PRJ-34(DEC) PRJ-10(DEC) PRJ-23(DEC) PRJ-27(CLOSE) PRJ-28(CLOSE) PRJ-29(CLOSE) PRJ-30(CLOSE)
- REN (7): REN-01(PR) REN-05(PR) REN-06(DEC) REN-08(PR) REN-09(PR) REN-11(DEC) REN-13(PR)
- EXE (10): EXE-01(DEC) EXE-02(PR) EXE-10(DEC) EXE-12(PR) EXE-15(CLOSE) EXE-16(CLOSE) EXE-17(CLOSE) EXE-18(CLOSE) EXE-19(CLOSE) EXE-20(CLOSE)
- PER (5): PER-01(DEC) PER-03(DEC) PER-06(DEC) PER-10(DEC) PER-11(CLOSE)
- UIC (4): UIC-13(PR) UIC-16(DEC) UIC-24(PR) UIC-25(CLOSE)
- DEV (11): DEV-01(DEC) DEV-02(PR) DEV-04(EXT) DEV-05(EXT) DEV-07(DEC) DEV-12(PR) DEV-14(DEC) DEV-17(DEC) DEV-20(PR) DEV-22(PR) DEV-23(DEC)

## 5. 파일 겹침 상위 파일 (충돌 꼬리가 "공유 N건" 으로 가리키는 허브 — 10건 이상)

| 파일 | 항목 수 | 항목 |
|---|---|---|
| DashMainWindow.cpp | 49 | CAD-01 CAD-03 CAD-07 CAD-09 CAD-12 CAD-15 CON-03 CON-05 CON-06 DEV-10 DOE-05 EXE-08 MOR-14 OPT-22 PRJ-01 PRJ-03 PRJ-04 PRJ-06 PRJ-11 PRJ-12 PRJ-13 PRJ-14 PRJ-15 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-21 PRJ-22 PRJ-24 PRJ-25 PRJ-26 PRJ-32 PRJ-35 PRJ-36 REN-02 REN-04 REN-07 REN-10 REN-12 RUN-28 UIC-01 UIC-03 UIC-05 UIC-07 UIC-09 UIC-10 UIC-19 UIC-26 |
| DashModelRunnerWidget.cpp | 30 | CAD-01 PRJ-25 REN-03 REN-05 REN-07 REN-10 RUN-01 RUN-03 RUN-05 RUN-06 RUN-07 RUN-08 RUN-09 RUN-10 RUN-12 RUN-13 RUN-15 RUN-16 RUN-17 RUN-19 RUN-20 RUN-21 RUN-24 RUN-25 RUN-28 RUN-29 RUN-30 RUN-34 UIC-20 UIC-24 |
| DashOptimizerWidget.cpp | 23 | CAD-01 OPT-01 OPT-02 OPT-05 OPT-06 OPT-07 OPT-08 OPT-09 OPT-10 OPT-12 OPT-13 OPT-14 OPT-15 OPT-17 OPT-18 OPT-21 OPT-22 OPT-25 OPT-26 PRJ-25 REN-07 UIC-20 UIC-22 |
| DashResultsAnalyzerWidget.cpp | 21 | ANA-03 ANA-04 ANA-05 ANA-06 ANA-07 ANA-08 ANA-09 ANA-10 ANA-11 ANA-12 ANA-13 ANA-14 ANA-15 ANA-18 ANA-21 ANA-22 EXE-03 EXE-04 EXE-08 UIC-12 UIC-20 |
| DashModelRunner.cpp | 20 | MOR-11 PRJ-09 RUN-01 RUN-03 RUN-04 RUN-05 RUN-12 RUN-13 RUN-14 RUN-17 RUN-18 RUN-25 RUN-26 RUN-27 RUN-29 RUN-31 RUN-32 RUN-34 UIC-19 UIC-20 |
| DashAnalysisLauncher.cpp | 20 | ANA-15 LCH-15 LCH-33 PRE-03 PRE-04 PRE-06 PRE-07 PRE-08 PRE-09 PRE-13 PRE-15 PRE-16 PRE-21 PRE-23 PRE-24 PRE-25 PRE-30 PRE-32 PRJ-09 UIC-20 |
| DashOptimizer.cpp | 17 | ANA-15 MOR-11 OPT-01 OPT-02 OPT-05 OPT-07 OPT-08 OPT-11 OPT-15 OPT-16 OPT-18 OPT-19 OPT-23 OPT-24 OPT-26 PRJ-09 UIC-20 |
| DashDoeSampler.cpp | 15 | ANA-15 DOE-02 DOE-03 DOE-05 DOE-07 DOE-08 DOE-09 DOE-11 DOE-12 DOE-16 DOE-17 LCH-14 PRJ-09 UIC-19 UIC-20 |
| DashProject.cpp | 14 | CON-05 DOE-05 PRJ-08 PRJ-16 PRJ-17 PRJ-18 PRJ-19 PRJ-22 PRJ-31 PRJ-32 PRJ-33 RUN-26 RUN-31 UIC-20 |
| DashModelBuilder.cpp | 13 | BLD-02 BLD-04 BLD-05 BLD-07 BLD-13 BLD-14 BLD-15 BLD-16 BLD-17 BLD-18 BLD-20 PRJ-09 UIC-20 |
| tests/CMakeLists.txt | 12 | BLD-19 CAD-11 CON-11 DEV-19 DOE-07 EXE-09 OPT-20 PER-02 PER-08 RUN-33 UIC-17 UIC-22 |
| DashJobRunnerAnsysMotion.cpp | 11 | DOE-12 LCH-02 LCH-03 LCH-04 LCH-05 LCH-07 LCH-10 LCH-12 LCH-13 LCH-14 PRJ-09 |
| DashModelBuilderMCUWidget.cpp | 11 | BLD-01 BLD-03 BLD-04 BLD-06 BLD-09 BLD-10 BLD-12 BLD-13 BLD-17 UIC-20 UIC-23 |
| DashMainWindow.h | 11 | EXE-08 PRJ-01 PRJ-04 PRJ-11 PRJ-15 PRJ-19 REN-12 UIC-01 UIC-03 UIC-05 UIC-09 |
| DashGeometryParameterCADWidget.cpp | 10 | CAD-01 CAD-03 CAD-04 CAD-05 CAD-06 CAD-07 CAD-09 CAD-13 DOE-19 UIC-19 |
| DashResultXmlWriter.cpp | 10 | PRE-03 PRE-04 PRE-06 PRE-07 PRE-10 PRE-20 PRE-22 PRE-30 PRE-31 PRE-32 |
| DashModelBuilderWidget.cpp | 10 | BLD-03 BLD-04 BLD-05 BLD-06 BLD-07 BLD-13 BLD-14 BLD-20 BLD-21 UIC-20 |
| DashModelRunner.h | 10 | RUN-01 RUN-05 RUN-12 RUN-13 RUN-14 RUN-16 RUN-27 RUN-29 RUN-31 RUN-34 |
| DashRenderingManager.cpp | 10 | OPT-01 PRJ-04 REN-03 REN-04 REN-05 REN-07 REN-08 REN-09 REN-10 REN-12 |

## 4. 대응표 (구 이슈 · 결함 → 새 항목)

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> `python3 05-final/build_mapping.py` 생성. 항목 = 03-items `흡수:` 에 원천이 적힌 항목. CLOSE 는 항목 제목이 닫기 사유.

## (a) 열린 이슈 117건 → 항목

| 이슈 | 제목 | 주 모듈 | 항목 | 비고 |
|---|---|---|---|---|
| #239 | Track B(구조 리팩터) 현황 | PRJ | PRJ-29 | CLOSE — Track B 현황 문서 이슈를 닫는다 |
| #246 | [W20] God-object 해체 — DataProcessor·DashManager·DashProjectM | PRJ | PRJ-27 | CLOSE — God-object 해체 부모를 닫는다 |
| #247 | [W21] Presentation Model 개선 단계 | PRJ | PRJ-28 | CLOSE — Presentation Model 개선 단계 부모를 닫는다 |
| #249 | NX CAD 파사드 완료 통지 일반화 — 요청 태그 왕복 + m_batchMode 제거 | CAD | CAD-01 CAD-15 LCH-27 EXE-12 |  |
| #281 | 단건 모핑 워커화 — QC·Optimizer·ModelRunner 진입점 이관 + 값 경계·전용 세션 (구  | MOR | MOR-04 MOR-16 MOR-18 OPT-22 OPT-26 EXE-14 | CLOSE(부모/본체) + 잔여 항목 — 닫기 — 모핑 축 진입점 이관은 끝났고 잔여는 OPT 측 펌핑 2곳뿐 |
| #305 | refactor: analyzer의 Eigen::VectorXf 컨테이너 용도 사용 정리 검토 (std::v | ANA | MOR-20 ANA-16 ANA-17 | CLOSE(부모/본체) + 잔여 항목 — 닫기 — PR #654 가 2번(sampling 치환)을 실행하고 1번(per-handle 반경)을 결정으로 종결했다 |
| #316 | Optimizer Preview 의 전체 actor 일괄 삭제 — 핸들 5종 복구 불가, 비파괴 오버레이로  | OPT | CAD-12 OPT-01 OPT-02 |  |
| #318 | 공유 VTK 씬에 모듈 소유권 도입 — 덮어쓰기 12곳 정리, 인수는 파괴가 아니라 숨김 | REN | CAD-12 OPT-01 REN-05 REN-06 REN-07 REN-08 REN-10 |  |
| #319 | 레이어 체계 밖 actor 의 수명·상태 결함 4건 — FE actor 숨김 방치 · 무조건 카메라 리셋 · | REN | REN-01 REN-02 REN-03 REN-04 |  |
| #320 | Modeling Tree 의 .vtk/.vtu 표시 토글 무동작 — m_vtuVtkActors 가 채워지지  | REN | REN-11 REN-12 |  |
| #322 | refactor: GizmoGroup 의 인덱스 병렬 컨테이너 3개 정리 — checked/백업 상태를 Da | MOR | MOR-09 | CLOSE — 닫기 — PR #655 가 `GizmoGroup` 을 삭제해 정리할 컨테이너가 없어진다 |
| #330 | 최신 MSVC version (18.10.0) 에서, vcpkg 를 통해 build artifact 가 공급 | DEV | DEV-01 DEV-02 DEV-03 |  |
| #331 | libs/ 임시 배치 해소 — DashGizmo 단일 빌드 재배치 · MarchingPlaneBound 상류 | MOR | MOR-06 MOR-07 MOR-08 |  |
| #332 | morphing — mesh-ops 공개 표면으로의 잔여 이관 2건 | MOR | MOR-20 | CLOSE — 닫기 — PR #654 가 2번(sampling 치환)을 실행하고 1번(per-handle 반경)을 결정으로 종결했다 |
| #335 | registry / meta 저장소 정합 4건 — portfile 주석 · git-tree · preproc | DEV | DEV-04 DEV-05 DEV-06 DEV-07 DEV-08 |  |
| #336 | vcpkg 이행 마무리 정리 4건 — external/ 삭제 · globalPos() · CRT 배포 · m | DEV | DEV-10 DEV-11 DEV-12 |  |
| #368 | 출처 기록과 공통 판독 계약 | PER | DOE-16 LCH-33 PRE-32 BLD-20 PER-06 PER-07 |  |
| #369 | NodeSet 선택 저장 — 독립 작업 | RUN | RUN-01 |  |
| #370 | ModelRunner: 1D 모델 Run AI Prediction 이 reference analysis fi | RUN | RUN-05 RUN-06 RUN-07 RUN-14 UIC-16 |  |
| #372 | CI: Level 1 레인 소요 시간 감시 — 건강 한도(임시 5분) 초과 시 알림 | DEV | DEV-14 DEV-15 DEV-16 |  |
| #376 | 프로젝트 열기 시 미열림 상태가 ERROR로 오탐지되는 문제 수정 | PRJ | PRJ-30 | CLOSE — IsProjectOpen ERROR 오탐을 닫는다 |
| #386 | clang-tidy 네이밍 검사: 저장소 소스가 컨벤션에 정렬된 뒤로 보류 | DEV | DEV-17 |  |
| #405 | DashXmlParser: FieldStatistics 계열이 호출자 0건 — 살릴지 지울지 결정 필요 | ANA | ANA-02 |  |
| #411 | DOE 산출 XML 포맷 교체 검토 — HDF5(vtkHDF) 등 스트리밍 가능 포맷 | PRE | PRE-28 PRE-29 PRE-31 BLD-16 PER-03 DEV-25 |  |
| #423 | 설정 초기값(default) 정책 — 소유자 · 진입점 · 대역 로그를 앱 전반에 세운다 (계기: 모핑 반경 | MOR | MOR-11 PER-10 |  |
| #427 | DOE 배치·Generate·프리뷰 실행을 화면 편집 상태에서 격리 | MOR | MOR-19 | CLOSE — 닫기 — 추적 전용 부모, 격리 몫은 끝났다 |
| #430 | 핸들 데이터 전용 타입 DashHandleData 신설 — VTP 읽기 5곳·쓰기 2곳 일원화 | MOR | MOR-15 | CLOSE — 닫기 — PR #655 가 interaction 의 핸들 소유를 해제했다 |
| #431 | 모델 교체·세트 전환 시 위젯 정리 규칙 문서화 | PRJ | PRJ-02 |  |
| #432 | 모델 계층이 프로젝트 관리자를 되부르는 의존 제거 | PRJ | PRJ-08 PRJ-09 |  |
| #433 | 데이터 처리 클래스 분해 | PRE | PRE-01 PRE-02 PRE-03 PRE-04 PRE-07 PRE-20 | CLOSE(부모/본체) + 잔여 항목 — 런처·초기화기의 질의 직렬화와 모달 Name 리터럴 공용화 — PR #656 이 구현 |
| #434 | 전역 관리 객체 해체 | PRJ | PRJ-03 PRJ-04 PRJ-05 PRJ-06 PRJ-07 |  |
| #438 | 배치 계산의 취소·진행 표시·재시작 복구를 완결 | LCH | LCH-22 | CLOSE — 닫기 — 추적 전용 부모 |
| #439 | 배치 취소가 대기 큐까지 비우게 완결 | LCH | LCH-03 |  |
| #440 | 실행 케이스마다 현재 상태가 표에 보이게 | LCH | LCH-23 | CLOSE — 닫기 — PR #652 가 Direct 표의 상태 배선을 해소한다 |
| #441 | 상태 기록과 재시작 복구 | LCH | LCH-08 LCH-09 |  |
| #442 | 실행 이력 목록 관리 | LCH | LCH-24 | CLOSE — 기록 — GitHub 에서 이미 닫힘 · gh-state CLOSED |
| #443 | Set 입력 참조 | PRJ | DOE-16 LCH-33 PRE-32 BLD-20 RUN-34 OPT-26 PER-06 PER-07 |  |
| #444 | Set 기록 분리 — 비용 검증 후 조건부 | LCH | LCH-32 |  |
| #446 | 창·레이아웃 크기 관리를 Qt 표준으로 전환 | UIC | UIC-25 | CLOSE — 을 닫는다 — 추적 부모, 실작업 없음 |
| #447 | 배율 다른 모니터로 이동 시 프리즈·복구 불가 차단 | UIC | CAD-14 ANA-19 ANA-20 OPT-25 UIC-01 UIC-02 |  |
| #448 | 창 위치·크기·도크 배치의 저장·복원 도입 | UIC | PRJ-14 UIC-05 |  |
| #449 | 명령형 크기 지정 제거 — 레이아웃에 크기 결정권 반환 | UIC | ANA-21 UIC-03 UIC-06 UIC-10 UIC-12 UIC-13 UIC-14 UIC-15 UIC-26 |  |
| #450 | 테두리 없는 창과 중첩 메인 윈도우 구조 재검토 | UIC | UIC-08 UIC-09 UIC-11 |  |
| #451 | GUI 스레드 동기 실행과 이벤트 펌핑 제거 | EXE | EXE-01 EXE-04 EXE-05 EXE-14 EXE-18 | CLOSE(부모/본체) + 잔여 항목 — GUI 스레드 동기 실행과 이벤트 펌핑 제거 — 추적 부모를 닫는다 |
| #454 | Data Preprocessor — 동기 실행 워커 이관과 펌핑 16곳 제거 | PRE | PRE-02 PRE-23 PRE-24 EXE-04 |  |
| #455 | 모듈 외 잔여 view 펌핑 10곳 분류·제거 | PRJ | MOR-01 PRJ-26 REN-13 |  |
| #456 | Analysis Launcher 정규 경로(.inp·ANSYS) — [Start] 동기 실행 워커 이관 | LCH | LCH-20 EXE-04 | CLOSE(부모/본체) + 잔여 항목 — 닫기 — 정규 경로 [Start] 는 이미 워커·시그널 구동이다 |
| #457 | Optimizer — 펌핑 2곳 제거와 요청 식별자 왕복 (OPT-D19) | OPT | CAD-01 OPT-22 OPT-26 |  |
| #458 | 해석 모델 적재를 워커로 이관 | EXE | LCH-12 EXE-14 EXE-22 |  |
| #459 | MCU Set 에서 SHAP Feature 콤보가 채워지지 않는 문제 복구 | ANA | ANA-03 |  |
| #460 | 실행 진행 표시·취소·중복 실행 가드의 표준화 | EXE | EXE-19 | CLOSE — 실행 진행 표시·취소·중복 실행 가드의 표준화 — 추적 부모를 닫는다 |
| #461 | 실행 중 재클릭·재진입 차단 | EXE | EXE-09 |  |
| #462 | 진행 표시 표준 1종 정의 | EXE | EXE-07 |  |
| #463 | 모듈별 진행바·취소 버튼 확산 | EXE | MOR-01 CAD-07 LCH-28 PRE-23 BLD-10 RUN-05 RUN-25 ANA-22 OPT-05 OPT-22 EXE-15 | CLOSE(부모/본체) + 잔여 항목 — 모듈별 진행바·취소 버튼 확산 — 모듈 항목으로 분산하고 닫는다 |
| #464 | 기존 진행 표시 결함 정리 — 스피너 비대칭 | CAD | CAD-07 |  |
| #465 | 외부 프로세스 안전핀 일괄 — 무음 실패·타임아웃·인코딩·널 가드 | EXE | EXE-20 | CLOSE — 외부 프로세스 안전핀 일괄 — 추적 부모를 닫는다 |
| #466 | 프로세스 무음 실패의 통지 규칙 수립 | EXE | EXE-10 UIC-16 |  |
| #467 | 데몬 기동·응답 타임아웃 도입 | EXE | EXE-11 |  |
| #468 | 외부 프로세스 호출부 널 가드 일괄 | EXE | EXE-16 | CLOSE — 외부 프로세스 호출부 널 가드 — 해소됨으로 닫는다 |
| #469 | 프로세스 인자·출력 인코딩 UTF-8 통일 | EXE | EXE-17 | CLOSE — 프로세스 인자·출력 인코딩 UTF-8 통일 — 본선 완료로 닫는다 |
| #470 | 출처 추적 상위 목표 유지 | PER | PER-09 |  |
| #471 | 독립 산출물·소비 대장 취소 유지 | PER | PER-11 | CLOSE — 독립 산출물·소비 대장 취소를 유지한다 |
| #473 | 결과 항목 조작 오류 수정 | RUN | RUN-02 |  |
| #474 | 표 행과 항목 연결 | RUN | RUN-12 UIC-23 |  |
| #475 | 예측 결과 덮어쓰기 방지 | RUN | RUN-10 |  |
| #477 | 삭제와 파일 해석 | RUN | RUN-11 RUN-13 |  |
| #478 | JSON 변환 헬퍼 표준화와 왕복 동일성 게이트 | PER | MOR-22 CAD-13 CON-11 DOE-17 PRE-27 BLD-17 RUN-32 OPT-24 PRJ-31 PER-01 PER-02 PER-05 |  |
| #479 | 파일 쓰기 원자성 — 저장 중 크래시에도 파일 보존 | PER | MOR-22 CAD-13 CON-11 DOE-17 PRE-27 BLD-17 RUN-32 OPT-24 PRJ-31 PER-02 |  |
| #480 | 저장 포맷에 버전 키 도입 | PER | MOR-22 CAD-13 CON-11 DOE-17 BLD-17 RUN-32 OPT-24 PRJ-31 PER-03 PER-04 |  |
| #481 | QSettings 스코프 통일과 최근 프로젝트 메뉴 | PRJ | PRJ-14 PRJ-15 |  |
| #482 | 사용자 통지 규칙 수립과 메시지 박스 래퍼 표준화 | UIC | UIC-16 UIC-17 |  |
| #483 | 출고물의 개발 잔재 제거 — 로컬 경로·플레이스홀더 문구 | DEV | OPT-12 DEV-20 |  |
| #484 | 릴리즈 식별·연장 — exe 버전 정보·만료일 런타임화 | DEV | DEV-21 DEV-22 DEV-23 DEV-24 |  |
| #485 | 종료 시 저장 확인 — 변경 추적과 닫기 이벤트 | PRJ | PRJ-10 PRJ-11 |  |
| #486 | 프로젝트 동시 열기 잠금 | PRJ | PRJ-13 |  |
| #487 | 숫자 입력 검증 일괄 — 범위 검증과 툴팁 | UIC | DOE-20 UIC-21 |  |
| #488 | 동작 없는 Undo/Redo 버튼 제거 | PRJ | PRJ-19 |  |
| #489 | 도메인 로직 테스트 커버리지 확장 | DEV | CAD-11 DOE-07 BLD-19 RUN-33 OPT-20 DEV-18 DEV-19 |  |
| #490 | 부분 적용된 다국어 처리 제거 — 영어 고정 | UIC | UIC-18 |  |
| #494 | 레거시 JSON 어댑터가 시간 선택자와 sub-result 를 버린다 — 응답 카탈로그 범위·성분 축 신설 | PRE | PRE-17 PRE-18 PRE-19 |  |
| #499 | morphing: mesh-ops 버전 범프 수용 — 신규 handle 생성기 API 와 고립 handle  | MOR | MOR-05 MOR-06 |  |
| #502 | 실행 1회로 조건 해석파일별 batch run 자동 반복 (T26 루프) | LCH | LCH-21 | CLOSE — 닫기 — 라디오 단일 선택 전제가 사라졌고 범위 밖으로 확정됐다 |
| #508 | 싱글턴 접근자 직후 도달 불가 null 가드 제거 — Instance()·Mgr()·GetProject()· | UIC | UIC-19 UIC-20 |  |
| #512 | Geometry Parameterization(Morphing) — setResults 펌핑 제거와 결정 시 | MOR | MOR-01 |  |
| #513 | Model Runner — 폴더 선택 동기 스캔 워커 이관 | RUN | RUN-25 EXE-04 |  |
| #514 | 표 셀 위젯이 캡처한 행 번호가 삭제 후 어긋난다 — 전수조사 잔여 5건과 행 해석 규칙 통일 (#503 계 | UIC | UIC-22 UIC-23 UIC-24 |  |
| #519 | DashPlotWidgetFactory: 열 수 없는 XML 경로를 콤보 조작마다 재시도한다 | ANA | ANA-01 |  |
| #543 | 비동기 작업 중 UI 차단·진행 표시의 UI/UX 정리 | EXE | EXE-02 EXE-07 EXE-08 |  |
| #551 | 프로젝트 전환 시 나머지 모듈 위젯 7곳도 해제된 모델을 역참조한다 — #549 전수조사 잔여 | PRJ | CON-04 PRJ-01 |  |
| #553 | DashAsyncJobRunner: 콜백 3개를 준비/실행/완료 훅 구조로 재구성한다 | EXE | EXE-03 |  |
| #557 | #500 후속 — DV-Geometry source 가 없는 GP 세트는 Target Component 비교 | MOR | MOR-10 |  |
| #562 | Set Rename 시 산출물 폴더·vtp 사이드카·Launcher Selected Design Variab | PRJ | DOE-18 PRJ-18 |  |
| #563 | Geometry Parameter Non-design(Constraints) 영역이 재진입·Set 전환 시  | MOR | MOR-02 MOR-03 MOR-04 |  |
| #580 | DOE Enqueued 이후 상태 없는 co_return 이 런 추적을 멈춘다 (stall 4곳) | LCH | LCH-02 |  |
| #604 | Tool 메뉴: Direct Launch를 별도 Dialog로 분리한다 | LCH | LCH-19 LCH-25 | CLOSE(부모/본체) + 잔여 항목 — 닫기 — PR #652 머지로 종결, 잔여는 LCH-14·LCH-19 |
| #615 | DOE Sampler: Add Set을 복원하되 Resample만 번호를 붙여 추가한다 | DOE | DOE-02 DOE-03 PRJ-33 |  |
| #616 | 입력 파일 정책: RW 미지원 포맷(.dfsxml/.wbpj/.stli)의 Project Assets·Con | LCH | LCH-26 LCH-29 | CLOSE(부모/본체) + 잔여 항목 — 닫기 — PR #651 머지로 종결, 잔여는 #647·#648 |
| #630 | 필드 출력 질의가 응답을 operator 로만 지정해 같은 operator 의 응답을 구분하지 못한다 | PRE | PRE-06 |  |
| #631 | Side Force KPI 가 Force X/Y operator 를 찾지 못하면 0 을 결과로 쓴다 | PRE | PRE-11 |  |
| #634 | Motion 의 Load Step 이 'States / State N' 으로 넘어가 배치는 state 1 만 | PRE | PRE-05 |  |
| #635 | 결과 XML 작성기가 Motion 컴포넌트의 entity_name 을 질의에 싣지 않아 전체 모델을 읽는다 | PRE | PRE-07 PRE-20 |  |
| #636 | Modal Frequency KPI 가 완료 신호를 직접 내 Success 팝업이 두 번 뜬다 | PRE | PRE-12 PRE-13 |  |
| #637 | Mode Shape 가 변위 결과를 하위 키·이름 순서·고정 키로 찾아 미리보기와 배치가 실패한다 | PRE | PRE-01 PRE-09 PRE-10 |  |
| #638 | Analysis Launcher 설정 저장이 0바이트 파일을 거절하고 실패 사유를 알리지 않는다 | PRE | LCH-34 PRE-14 PRE-15 PRE-16 PER-02 |  |
| #639 | Analysis Launcher: Target Part 로딩 중 Start를 누르면 빈 target이 저장되 | LCH | LCH-01 |  |
| #643 | Analysis Launcher: Preprocess XML을 Set 단위로 쓰고 중복 정보를 없앤다 (HD | PRE | PRE-29 PRE-30 PRE-31 BLD-14 ANA-23 |  |
| #645 | Project Assets: Add File로 덮어쓴 파일이 Condition 화면에 반영되지 않고 복사 실 | PRJ | CON-03 PRJ-20 PRJ-21 | CLOSE(부모/본체) + 잔여 항목 — (CLOSE) Add File 덮어쓰기 뒤 Condition 재읽기를 CON-03 에 넘긴다 |
| #646 | Analysis Launcher: 재실행 뒤 Preprocess 목록 미갱신, Re-run 실패 시 기존 결 | LCH | LCH-15 LCH-16 LCH-17 |  |
| #647 | Ansys Motion: dfsxml 실행이 LGE 압축기 예제에 하드코딩되어 있고 run마다 dfmm·df | LCH | LCH-10 LCH-11 |  |
| #648 | fe-safe: Set이 파일 하나에 묶인 뒤 입력 ODB 위치를 찾지 못한다 | LCH | LCH-18 LCH-30 |  |
| #649 | DOE Sampler·Analysis Launcher 재구성 후속 — Set 정책·입력 포맷·화면 갱신 | DOE | DOE-15 | CLOSE — 를 추적 부모로 닫는다 |
| #650 | 산출물 버전과 최신성 | PRJ | BLD-15 BLD-18 RUN-31 ANA-06 OPT-23 PRJ-22 PRJ-23 |  |
| #653 | Model Runner·Optimizer: FE Validation 버튼으로 Set의 입력 파일을 Direc | RUN | RUN-30 OPT-21 |  |
| #552 | DashAsyncJobContext 취소 불가 — 보드 밖 OPEN (#553 선행) | EXE | EXE-02 | gh-state OPEN(보드 밖) |
| #404 | Analyzer: "(std)" 축약이 표준편차가 아니라 최댓값으로 조용히 떨어진다 — 보드 밖 OPEN ( | ANA | ANA-02 | gh-state OPEN(보드 밖) |
| #394 | SaveProjectAs 가 모든 실패를 무시하고 true 를 반환하는 문제 — 보드 밖 OPEN | PRJ | PRJ-12 PRJ-36 | gh-state OPEN(보드 밖) |
| #577 | fix(view): Volume 핸들 생성기 — cylinder 삭제, Hexahedron 은 mesh-op | MOR | MOR-05 | gh-state OPEN(보드 밖) |

집계: 작업 항목 89 · CLOSE 19 · CLOSE+잔여 9 · 항목 없음 0

## (a-1) 원천 보드 snapshot 이후 확정된 소비 계약

| 이슈 | 항목 | 현재 범위 |
|---|---|---|
| #685 | RUN-34 · OPT-26 (OPT-15 저장 접점) | #443 하위. #368 생산·공통 계약 선행, Builder setId 참조·검증·실행·조회·프리뷰. #681 머지 조건 아님 |

위 (a)의 보드 수·gh-state는 당시 수집 기록이다. #443은 별도 Set 원장 구축을 요구하지 않고 #444·#369를 하위에서 분리한다. #444는 #441 하위, #473은 참조 전환과 독립이며 #470은 유지한다. 추가 개정 계획의 보드 정리·종료 후보는 이 표에서 실행하지 않는다.

## (b) 결함 201건 → 항목 또는 판정

| 결함 | 색인 요약 | 항목 | 판정 · 근거 CID |
|---|---|---|---|
| ANA-D6 | 색 값의 정본이 스타일시트 문자열이고 읽는 방식이 문자열 절단·정규식 2가지 | ANA-10 | 유효(ANA-c14) |
| ANA-D9 | 설정 JSON 의 `DOE Analysis`·`Data Analysis` 블록이 write-only | 항목 없음 | 해소됨(ANA-c17) |
| ANA-D3 | `applyReduction` 분기가 Max/Min/Mean 3종이고 나머지는 `reduceMax` 폴백 | ANA-02 | 유효(ANA-c02) 해소됨(ANA-c11) |
| ANA-D10 | spec 조립 실패·command 미매치·조기 반환이 UI 에 아무 변화를 주지 않음 | ANA-15 | 유효(ANA-c19) |
| ANA-D14 | 타깃 콤보 스캔이 Set 필터 없이 전량을 나열하고 항상 0번을 자동 선택 | ANA-06 | 유효(ANA-c24) |
| ANA-D12 | Save 메뉴 3종이 위젯 종류와 무관하게 뜨고 `dynamic_cast` 실패 시 무반응 | CAD-07 LCH-23 OPT-05 UIC-16 | CID 경유 — 해소됨(ANA-c22) 해소됨(ANA-c39) 해소됨(ANA-c40) 범위밖(EXE-c44) 범위밖(UIC-c56) |
| ANA-D2 | 중복 억제 캐시가 함수-로컬 `static` 이고 키에 인스턴스가 없다 | ANA-05 | 유효(ANA-c10) |
| ANA-D5 | 타깃 3콤보 등 5종이 `objectName` + `findChild` 문자열 계약 (25회) | ANA-08 | 유효(ANA-c13) |
| ANA-D11 | 랭킹 표를 반환 타입 밖의 숨은 자식으로 실어 보내고 `objectName` 으로 꺼낸다 | ANA-12 ANA-13 | 유효(ANA-c20) |
| ANA-D1 | `m_methodWidgets` 가 `QMap` 이라 Method 콤보가 키 알파벳 순 | ANA-04 | 유효(ANA-c09) 유효(ANA-c42) |
| ANA-D8 | `methodKey` 매핑 5줄이 세 파일에 각각 존재 | 항목 없음 | 해소됨(ANA-c16) |
| ANA-D15 | `m_setName` 이 비면 `"Set1"` 로 대체하는 폴백 삼항이 7회 복제 | ANA-07 | 유효(ANA-c25) 유효(PRJ-c55) |
| ANA-D4 | XML 변수 스캔이 매번 문서 전체를 GUI 스레드에서 파싱하고 폴백 경로는 결과가 다르다 | 항목 없음 | 해소됨(ANA-c12) |
| ANA-D13 | 스핀박스가 스타일 setter 와 디바운스 재플롯 양쪽에 연결돼 있다 | ANA-11 | 유효(ANA-c23) |
| ANA-D7 | 타입 핸들 `textStyleGroup` 에 9곳이 대입하고 읽는 코드는 0건 | ANA-09 | 유효(ANA-c15) |
| ANA-U1 | `onTargetDataChanged` 의 모듈 판별 4갈래가 도달 불가 | ANA-14 | 유효(ANA-c26) |
| ANA-U2 | `settings.parallel.save_json_path` 를 읽는 코드가 레포 전체 0건 | ANA-14 | 유효(ANA-c27) |
| ANA-U3 | `DashDoeConfigManager::updateConfigFile` 55줄의 호출처가 0건 | 항목 없음 | 해소됨(ANA-c18) |
| ANA-U5 | 호출부 없는 진입점 4개 (약 106·110·111·16줄) | ANA-12 ANA-14 | 유효(ANA-c21) 유효(ANA-c28) |
| BLD-D1 | Set 갈림 근거가 `UserRole+2` · JSON `variant` · 이름 접미사 3벌 | PRJ-32 | 범위밖(BLD-c01) 유효(PRJ-c63) |
| BLD-D4 | 라벨 키의 쓰기는 sanitize, 읽기는 원문 | BLD-02 | 유효(BLD-c04) |
| BLD-D7 | 저장된 Response 는 sanitize 된 이름, 콤보 표시는 원문 기반 | BLD-03 | 유효(BLD-c05) |
| BLD-D8 | Output `transformation` 은 쓰기만 되고 읽기에서 값이 버려진다 | BLD-02 | 유효(BLD-c06) |
| BLD-D12 | MCU 는 `Data Label.Dataset` 을 배열로 쓰는데 베이스 로더는 `toString()` | BLD-01 | 유효(BLD-c08) |
| BLD-D14 | MCU 의 `stopTraining` 이 `virtual` 이 아니라 베이스 no-op 이 불린다 | BLD-10 | 해소됨(BLD-c21) 해소됨(EXE-c40) |
| BLD-D2 | [Load] 의 위젯↔모델 계약이 `"dir|file"` 구분자 문자열 | BLD-04 | 유효(BLD-c02) |
| BLD-D3 | 차원 판정의 정본이 파싱 결과가 아니라 shape 문자열의 쉼표 개수 | BLD-05 | 유효(BLD-c03) |
| BLD-D5 | 설정값 왕복이 카탈로그 리스트 i번째와 `QFormLayout` i번째 `FieldRole` 의 짝 | BLD-06 | 유효(BLD-c09) 유효(BLD-c40) |
| BLD-D10 | MCU 파일 행의 [...] 람다가 생성 시점 `row` 를 값 캡처 | UIC-23 | 유효(BLD-c18) 유효(BLD-c35) 유효(BLD-c35) 범위밖(RUN-c14) 유효(UIC-c51) |
| BLD-D9 | Sim / MCU 쌍둥이 경로의 계약이 6곳에서 어긋난다 | BLD-01 BLD-11 BLD-12 | 유효(BLD-c11) 유효(BLD-c12) 유효(BLD-c13) 유효(BLD-c14) 유효(BLD-c15) 유효(BLD-c16) 유효(BLD-c17) |
| BLD-D6 | [Delete] 가 `model_info.json` 과 디스크만 지우고 설정 JSON 항목을 남긴다 | BLD-07 | 유효(BLD-c10) |
| BLD-D15 | MCU 위젯이 버튼 잠금을 되돌리지 않고 성공·실패 시그널도 연결하지 않는다 | BLD-10 | 유효(BLD-c22) |
| BLD-D11 | 헤더 검증의 기준 파일 출처가 넷이고 전부 조작 순서에 종속 | BLD-09 | 유효(BLD-c19) |
| BLD-D13 | MCU 가 쓰지 않는 1Hz 상태 폴링 타이머를 켠 채 두고 멈추는 경로도 안 탄다 | BLD-10 | 유효(BLD-c20) 유효(BLD-c37) 범위밖(EXE-c37) |
| BLD-U1 | 죽은 코드가 세 층에 남아 있다 (헬퍼 8개 중 실사용 4개 · `m_datasetFiles` 스캔 38줄 등) | BLD-13 | 유효(BLD-c23) |
| BLD-U3 | `parseDataLabelSection`·`parseConfigurationSection` 의 호출처가 0 | BLD-02 | 유효(BLD-c07) |
| CAD-D12 | 범위값의 정본이 모델이 아니라 셀 위젯의 스핀박스 | CAD-04 | 유효(CAD-c28) |
| CAD-D10 | `meta.default` 에 현재값이 아니라 Lower 열 값이 들어감 | CAD-05 | 유효(CAD-c26) |
| CAD-D11 | `Independent Parameter.Value` 저장은 `upper`, 로드는 "현재값" 으로 해석 | CAD-05 | 유효(CAD-c27) |
| CAD-D17 | Set ↔ `.prt` 결합이 어느 저장 경로에도 없다 (프로젝트 전역 1개) | CAD-09 | 유효(CAD-c34) |
| CAD-D14 | NX 표현식 적용 실패가 ListingWindow 에만 기록되고 stdout 으로 안 나감 | CAD-10 | 유효(CAD-c30) |
| CAD-D1 | `.prt` 성공 경로에 로딩 스피너 정지 호출이 없다 (실패 경로에만 있음) | CAD-07 | 해소됨(CAD-c17) 유효(CAD-c18) 유효(CAD-c49) 범위밖(EXE-c44) 범위밖(UIC-c56) |
| CAD-D9 | NX CAD 스피너가 비대칭 — 프리뷰 완료 경로에 대응하는 시작 호출이 없다 | CAD-07 | 유효(CAD-c19) 유효(CAD-c49) 범위밖(EXE-c44) 범위밖(UIC-c56) |
| CAD-D3 | 한 명령의 두 산출물(파라미터 JSON · STEP)이 다른 채널로 도착하고 합류점이 없다 | CAD-01 | 유효(CAD-c04) 유효(CAD-c44) 범위밖(EXE-c42) |
| CAD-D7 | 전송 계층은 `commandId` 를 갖지만 파사드의 `emitFailure` 에 경로 인자가 없다 | CAD-01 | 유효(CAD-c03) 유효(CAD-c44) 범위밖(EXE-c42) |
| CAD-D8 | 방출 대상이 요청 단위가 아니라 전역 `m_batchMode` 1비트로 스위칭 | CAD-01 | 유효(CAD-c01) 유효(CAD-c02) 유효(CAD-c44) 범위밖(EXE-c42) |
| CAD-U4 | 데몬 성공·실패 판정이 `[FINISHED]` 전체 일치와 `[ERROR]` 부분 일치 | EXE-12 | 범위밖(CAD-c31) 유효(EXE-c29) 유효(EXE-c57) |
| CAD-D6 | 정렬 방어가 이름 매칭 2 · 시각 행 인덱스 2 · 채우기 시점 캡처 1로 갈린다 | CAD-04 | 유효(CAD-c25) 유효(CAD-c51) |
| CAD-D13 | Set 삭제 시 위젯이 `mModel` 을 정리하지 않고 직후 `deleteLater()` 가 걸린다 | 항목 없음 | 해소됨(CAD-c29) 해소됨(PRJ-c57) |
| CAD-D15 | `loadPrt` 의 temp 정리가 승격이 복사해 둔 `.prt` 보관본과 같은 경로를 지운다 | CAD-09 | 유효(CAD-c32) |
| CAD-D16 | GUI 가 `--no-cleanup` 을 항상 붙이고 일괄 정리는 `.stp` 만 글로빙 | CAD-08 | 유효(CAD-c33) |
| CAD-D4 | `loadFromJson` 복원 직후 캐시 재적용이 전 행을 `isChecked = false` 로 재구성 | CAD-03 | 유효(CAD-c21) 유효(CAD-c23) 유효(CAD-c52) |
| CAD-D2 | `.prt` 진입 초입의 `processEvents` 가 큐된 슬롯·타이머를 실행 | PRJ-26 | 범위밖(CAD-c20) 유효(PRJ-c64) 범위밖(EXE-c43) |
| CAD-D5 | Set 진입마다 도는 해석 덱 유입 경로의 결과를 읽는 곳이 0 | 항목 없음 | 해소됨(CAD-c24) |
| CAD-U3 | 도달하지 않는 선언·정의 — `saveSettings` no-op · `getContext`/`getLoadedFilePath` | CAD-06 | 유효(CAD-c11) 유효(CAD-c35) |
| CAD-U5 | `tests/` 전체에 `NxCad`·`GeometryParameter` 참조 0건 | CAD-11 | 유효(CAD-c36) 유효(CAD-c47) 유효(CAD-c48) 범위밖(UIC-c57) 범위밖(DEV-c24) |
| CON-D4 | `.ui` 의 열 선언 5열과 모델 7열이 드리프트 | CON-06 | 유효(CON-c04) |
| CON-D5 | Value 인라인 편집이 메모리 deck 만 바꾸고 설정 JSON 에 대응 키가 없다 | CON-10 | 유효(CON-c05) |
| CON-D10 | 대상 deck 이 전역 active context 1개뿐, Set 별 저장 필드가 없다 | 항목 없음 | 해소됨(CON-c10) |
| CON-D13 | ResultsAnalyzer 가 `paramObj["checked"]` 를 읽는데 그 키를 쓰는 코드가 없다 | ANA-14 | 범위밖(CON-c13) 유효(ANA-c31) |
| CON-D12 | 조건 DV 주입 실패 3종이 전부 `continue` | 항목 없음 | 해소됨(CON-c12) |
| CON-D6 | GUI 편집과 DOE 배치가 같은 RW 세션을 공유하는데 상호 배제가 없다 | 항목 없음 | 해소됨(CON-c06) |
| CON-D2 | `getOrLoad` 의 실제 로드가 뮤텍스 밖에서 돈다 | DOE-07 EXE-05 PER-02 | CID 경유 — 해소됨(CON-c02) 해소됨(REN-c35) 해소됨(EXE-c09) 범위밖(EXE-c41) |
| CON-D1 | `setProjectDirectory` 가 인자를 쓰지 않고 경로를 다시 유도한다 | CON-05 | 유효(CON-c01) |
| CON-D8 | DV 섹션 판정이 파일명에 `"Condition"` 이 포함되는지 | DOE-10 | 유효(CON-c08) |
| CON-D3 | `m_params` 가 한 번도 clear 되지 않는다 | CON-02 | 유효(CON-c03) |
| CON-D7 | `loadFromJson` 이 행을 만드는 `refreshFromLoadedAnalysis` 보다 먼저 돈다 | CON-01 | 유효(CON-c07) |
| CON-D9 | 자기 쓰기 억제 플래그를 되돌린 다음 줄의 모달이 중첩 이벤트 루프를 돈다 | CON-07 | 유효(CON-c09) 유효(CON-c24) 범위밖(EXE-c43) |
| CON-D11 | `get_symbol_detail` 이 캐시되지 않는다 | CON-07 LCH-08 LCH-12 LCH-20 PRE-23 PRJ-26 | CID 경유 — 해소됨(CON-c11) 범위밖(EXE-c43) |
| CON-U1 | `setModel` 오버로드의 유일한 호출 인자가 항상 `nullptr` | CON-06 | 유효(CON-c14) |
| CON-U3 | 디렉토리 워처의 `directoryChanged` 연결이 레포 전체 0곳 | CON-06 | 유효(CON-c15) |
| CON-U5 | `tests/` 전체에 RW 관련 5심볼 참조 0건 | CON-09 EXE-21 | 유효(CON-c16) 범위밖(CON-c17) 유효(CON-c25) 유효(EXE-c58) 범위밖(UIC-c57) 해소됨(DEV-c25) |
| DOE-D5 | 같은 샘플이 위치 기반 `samples[]` 와 이름 기반 `rawSamples[]` 두 형태로 저장 | DOE-14 | 유효(DOE-c15) 유효(DOE-c57) 범위밖(LCH-c61) |
| DOE-D2 | Probabilistic Min/Max 가 모델에 되쓰이지 않고 샘플링에만 전달 | DOE-06 | 유효(DOE-c11) 유효(DOE-c12) 유효(DOE-c54) 범위밖(LCH-c58) |
| DOE-D26 | 제약식은 설정 JSON 에 영속화되는데 그 토큰인 `v{n}` 은 행 인덱스에서 매번 재생성 | DOE-09 | 유효(DOE-c20) 유효(DOE-c59) 범위밖(LCH-c63) |
| DOE-D12 | FE-safe 의 ODB 소스 판정이 파일 존재만 보고 워크플로 실행 여부를 안 본다 | LCH-30 | 범위밖(DOE-c41) 유효(LCH-c23) 미확인(LCH-c29) 유효(LCH-c76) |
| DOE-D15 | motion-launcher 가 `.dfr` 이 없으면 하드코딩 XML 7줄로 만들어 낸다 | LCH-04 | 범위밖(DOE-c44) 유효(LCH-c39) 유효(LCH-c79) |
| DOE-D19 | condition DV 적용 실패 3경로가 warning 후 `continue`, 호출부가 결과 미검사 | 항목 없음 | 범위밖(DOE-c48) 해소됨(LCH-c52) 해소됨(LCH-c83) |
| DOE-D25 | 릴리스 빌드는 Resample 위젯을 생성하지 않는데 트리의 그 variant Set 은 남아 있다 | PRJ-24 | 유효(DOE-c19) 유효(DOE-c58) 범위밖(LCH-c62) 유효(PRJ-c52) |
| DOE-U2 | Direct Output Cases 표가 `setModel` 도 상태 시그널도 받지 않고 Status 를 `"Enqueued"` | LCH-23 | 범위밖(DOE-c35) 유효(LCH-c10) 유효(LCH-c70) 유효(LCH-c94) 유효(LCH-c95) 범위밖(EXE-c44) 범위밖(UIC-c56) |
| DOE-D17 | 모핑 배치가 GUI 소유 싱글턴 핸들 인스턴스에 VTP 를 `DeepCopy` | 항목 없음 | 범위밖(DOE-c46) 해소됨(LCH-c50) 해소됨(LCH-c81) |
| DOE-D18 | 배치가 GUI 와 공유된 해석 컨텍스트를 in-place 변이하고 원복 두 줄에 의존 | 항목 없음 | 범위밖(DOE-c47) 해소됨(LCH-c51) 해소됨(LCH-c82) |
| DOE-D16 | `.dfsxml` 경로의 완료 판정 주체가 `finished` 람다와 stdout 감시 둘 | LCH-05 | 범위밖(DOE-c45) 유효(LCH-c40) 유효(LCH-c80) 유효(LCH-c96) 범위밖(EXE-c42) |
| DOE-D21 | 종결이 키 집합 소진 집계와 `jobFinished` 직접 방출 두 갈래 | LCH-06 | 범위밖(DOE-c49) 유효(LCH-c41) 유효(LCH-c84) 유효(LCH-c96) 범위밖(EXE-c42) |
| DOE-D4 | 워커가 GUI 소유 `QAbstractItemModel` 을 직접 읽는다 (결과 기록도 모델 포인터 경유) | DOE-07 | 유효(DOE-c14) 유효(DOE-c56) 유효(DOE-c62) 범위밖(LCH-c60) 범위밖(EXE-c41) |
| DOE-D22 | 설정 JSON read-modify-write 8곳 중 뮤텍스를 지나는 것이 1곳이고 그마저 인스턴스 멤버 | DOE-07 PER-02 | 유효(DOE-c17) 범위밖(DOE-c18) 유효(DOE-c62) 해소됨(LCH-c46) 해소됨(LCH-c65) 범위밖(EXE-c41) 유효(PER-c08) 유효(PER-c33) |
| DOE-D3 | Purpose 판정이 문장 완전일치이고 리터럴이 두 곳에 이중 정의 | DOE-08 | 유효(DOE-c13) 유효(DOE-c55) 범위밖(LCH-c59) |
| DOE-D8 | 표 행 ↔ 케이스 결합이 Case Name 열 표시 텍스트 파싱 (`UserRole` 없음) | 항목 없음 | 범위밖(DOE-c37) 해소됨(LCH-c47) 해소됨(LCH-c72) 해소됨(LCH-c88) 해소됨(LCH-c88) 범위밖(RUN-c13) |
| DOE-D24 | Direct Launcher 가 `analysisType` 을 빈 문자열로 넘겨 현재 Set 의 DOE JSON 을 연다 | LCH-23 LCH-25 | CID 경유 — 범위밖(DOE-c35) 해소됨(LCH-c48) 유효(LCH-c70) |
| DOE-D6 | Geometry/Condition 판별을 세 곳이 대소문자 구분·무시·정규식으로 각자 구현 | DOE-10 | 유효(DOE-c16) 해소됨(LCH-c49) |
| DOE-D10 | 말단 6경로가 착수·상태보고·종결을 각자 구현 | LCH-07 | 범위밖(DOE-c39) 유효(LCH-c42) 유효(LCH-c74) |
| DOE-D13 | 경로 조립기 두 개의 일치를 경고-후-덮어쓰기 한 줄이 강제 | LCH-13 | 범위밖(DOE-c42) 유효(LCH-c44) 유효(LCH-c77) |
| DOE-D23 | `cancelAllRuns` 가 진행 중 프로세스만 죽이고 motion 큐를 비우지 않는다 | LCH-03 | 범위밖(DOE-c50) 유효(LCH-c09) 유효(LCH-c85) 유효(LCH-c90) 범위밖(EXE-c33) |
| DOE-D1 | `loadSettings` 가 진입 1회에 3번 호출되고 앞 둘은 시그널 연결 전 | DOE-05 | 유효(DOE-c10) 유효(DOE-c53) 범위밖(LCH-c57) |
| DOE-D7 | 케이스 상태 1건마다 JSON 전문 재기록 → 워처가 표를 전량 재구축 | LCH-08 | 범위밖(DOE-c36) 유효(LCH-c11) 유효(LCH-c71) 유효(LCH-c89) 유효(LCH-c93) 범위밖(PRJ-c07) 범위밖(EXE-c43) |
| DOE-D9 | `runDoeAsync` 가 이름과 달리 동기 — `generateInputCases` 738줄이 GUI 스레드 | LCH-20 | 범위밖(DOE-c38) 해소됨(LCH-c01) 해소됨(LCH-c73) 유효(LCH-c93) 범위밖(EXE-c43) |
| DOE-D11 | `processEvents` 16곳이 동기 대기의 대체물 (전량 `DashJobRunner.cpp`) | LCH-12 EXE-09 | 범위밖(DOE-c40) 유효(LCH-c43) 유효(LCH-c75) 유효(LCH-c93) 유효(EXE-c22) 범위밖(EXE-c43) |
| DOE-D14 | `msleep(1000)` 이 이미 끝난 동기 호출 뒤에 있다 | LCH-12 | CID 경유 — 범위밖(DOE-c43) 해소됨(LCH-c45) 해소됨(LCH-c78) 유효(3곳)(LCH-c91) 범위밖(EXE-c39) |
| DOE-U3 | `visibleParamIndices` 가 계산되지만 표는 4열 고정이라 반영될 열이 없다 | 항목 없음 | 범위밖(DOE-c51) 해소됨(LCH-c53) 해소됨(LCH-c86) |
| DOE-U4 | 호출부가 0인 함수 8종 (`createRunsFolders` 2종 · `getStatusFromFileSystem` 53줄  | DOE-11 LCH-14 | 유효(DOE-c21) 범위밖(DOE-c22) 유효(1건)(LCH-c54) 유효(1건)(LCH-c66) |
| DOE-U5 | 도달하지 않는 연결·계산 3종 (`connLog` 빈 람다 · `.ui` 콤보 2항목 · `firstPartName`) | DOE-08 LCH-14 | 유효(DOE-c13) 유효(DOE-c23) 범위밖(DOE-c24) 유효(1건)(LCH-c56) 유효(1건)(LCH-c67) |
| MOR-D5 | 핸들 이름의 정본이 트리 아이템 텍스트와 세션 한정 `QMap` 뿐 | MOR-17 | 유효(MOR-c51) |
| MOR-D9 | 범위값의 정본이 polydata 배열이 아니라 트리 셀 위젯 | MOR-17 | 유효(MOR-c55) |
| MOR-D6 | θ 는 방향 벡터로만 저장되고 표시값은 기즈모 Euler 의 역산 | MOR-17 | 유효(MOR-c52) 유효(MOR-c87) |
| MOR-D10 | `Morphing.constraints` 는 파서만 있고 writer 가 레포에 없다 | MOR-02 | 유효(MOR-c18) 유효(MOR-c56) 유효(MOR-c87) |
| MOR-D11 | 대상 파트가 어느 저장 경로에도 기록되지 않음 | 항목 없음 | 해소됨(MOR-c57) 유효(MOR-c87) |
| MOR-D2 | geometry 부재 시 파트 검증 없이 렌더링 매니저의 base actor 로 대체 | 항목 없음 | 해소됨(MOR-c48) 해소됨(MOR-c81) 범위밖(REN-c33) |
| MOR-U1 | `MODE_PHYSICS` 가 `SetInteractionMode` 의 `switch` 에서 누락 | MOR-13 | 유효(MOR-c61) |
| MOR-D3 | Generate 분기가 타입 키가 아니라 7단 `isVisible()` 캐스케이드 | MOR-12 | 유효(MOR-c49) |
| MOR-D14 | Geometry 카테고리는 트리 루트 1개에 모델 배열 2벌인데 Morphing 갈래만 행 인덱스로 조회 | 항목 없음 | 해소됨(MOR-c60) 해소됨(MOR-c84) 해소됨(PRJ-c53) |
| MOR-D12 | 명시적 리셋이 Set 이 바뀔 때만 돌고 `appendConstraintTable` 은 무조건 `insertRow` | 항목 없음 | 해소됨(MOR-c58) |
| MOR-D1 | 초기화 체인 전체가 `dataLoaded` emit 에 걸려 있고 화면 전환이 먼저 일어난다 | 항목 없음 | 해소됨(MOR-c47) |
| MOR-D7 | 프리뷰 모핑이 GUI 스레드 동기 실행 | MOR-18 CON-07 LCH-08 LCH-12 LCH-20 PRE-23 PRJ-26 | CID 경유 — 해소됨(MOR-c09) 해소됨(MOR-c53) 해소됨(MOR-c85) 범위밖(EXE-c43) |
| MOR-D8 | `processEvents` 가 모핑 루프 안 2곳 | CON-07 LCH-08 LCH-12 LCH-20 PRE-23 PRJ-26 | CID 경유 — 해소됨(MOR-c54) 해소됨(MOR-c85) 범위밖(EXE-c43) |
| MOR-U2 | 툴바 Prev/Next 가 emit 만 하고 수신처가 없다 | MOR-14 | 유효(MOR-c62) 유효(PRJ-c44) |
| MOR-D4 | `DashHandlePickingInteraction` 3,121줄이 픽킹·기즈모·핸들 데이터·구속 오버레이 4역 | MOR-15 | 유효(MOR-c33) 유효(MOR-c50) |
| MOR-D13 | 컨트롤러가 뷰 포인터를 무가드로 역참조하는 곳 6군데 | 항목 없음 | 해소됨(MOR-c59) |
| OPT-D22 | 피팅 결과가 DV 표 위젯에만 쓰이고 `m_designVariables` 에 도달하지 않음 | OPT-06 | 유효(OPT-c34) |
| OPT-D24 | 심볼의 표시분은 행 인덱스 재생성, 모델분은 JSON `symbol`, 복원 매칭은 응답 이름 | OPT-08 | 유효(OPT-c28) |
| OPT-D5 | 최적화 모드 2차 판정이 1 로 올리기만 하고 0 으로 내리지 않는다 | OPT-11 | 유효(OPT-c15) 유효(OPT-c52) |
| OPT-D6 | Fixed 체크와 Init. Value 편집이 모델에 도달하지 않음 (시그널 미연결) | OPT-06 | 유효(OPT-c16) 유효(OPT-c52) |
| OPT-D7 | Minimize/Maximize 콤보에 수신 슬롯이 없다 | OPT-06 | 유효(OPT-c17) 유효(OPT-c52) |
| OPT-D12 | `saveSettings()` 호출처가 `runOptimization` 하나 | OPT-07 | 유효(OPT-c22) 유효(OPT-c52) |
| OPT-D21 | `m_activeModelBuilderFolder` 에 설정 JSON 왕복이 없다 | OPT-15 | 유효(OPT-c33) 유효(OPT-c52) |
| OPT-D8 | [+] 가 심는 예시 구속이 회색 placeholder 가 아니라 보통 아이템이고 즉시 모델에 들어간다 | OPT-12 | 유효(OPT-c18) |
| OPT-D11 | `optimizationFailed` 의 `connect` 가 레포 전체에 없다 | OPT-05 EXE-10 | 유효(OPT-c21) 유효(OPT-c50) 유효(EXE-c24) 범위밖(EXE-c44) |
| OPT-D13 | 중복 실행 방지가 모델의 `m_currentJob` 가드뿐이고 버튼은 열려 있다 | OPT-05 EXE-07 EXE-09 | 유효(OPT-c23) 유효(OPT-c48) 유효(OPT-c50) 유효(EXE-c22) 범위밖(EXE-c44) 범위밖(UIC-c55) |
| OPT-D18 | [Render Preview] 가 핸들 배열·렌더러 액터·전역 active context 3종을 갈아끼우고 복구 코드가 없다 | OPT-01 | 유효(OPT-c01) 유효(OPT-c03) 해소됨(OPT-c29) 유효(OPT-c43) 유효(OPT-c45) 범위밖(REN-c19) 범위밖(REN-c32) |
| OPT-D19 | 요청에 태그가 없고 완료 수신처가 `DashMainWindow` | CAD-01 OPT-22 | 유효(CAD-c41) 범위밖(OPT-c10) 유효(OPT-c39) 범위밖(EXE-c42) |
| OPT-D4 | 1D / ND 열 가시성이 첫 행 응답 이름의 `"(Field)"` 부분문자열로 정해진다 | OPT-10 | 유효(OPT-c14) |
| OPT-D14 | 검증 표 헤더 분류가 `startsWith("r")` + 두 번째 글자 숫자 규칙 | OPT-14 | 유효(OPT-c24) |
| OPT-D20 | 설정 JSON 이 실데이터가 아닌데 플롯의 실재 게이트로 쓰인다 | ANA-15 | 유효(ANA-c32) 범위밖(OPT-c30) |
| OPT-D15 | 프리뷰가 `templateFileName` 필터를 무시하고 configs 의 deck 전량을 순회 | OPT-26 | 유효(OPT-c25) 유효(OPT-c56) 유효(OPT-c57) |
| OPT-D1 | 같은 `model_info.json` 을 두 로더가 읽고 NaN 정화 수준이 다르다 | OPT-16 | 유효(OPT-c11) |
| OPT-D2 | Set 삭제 후 `setModel(nullptr)` 이 표 내용과 `setEnabled(true)` 를 그대로 둔다 | OPT-17 | 유효(OPT-c12) 유효(OPT-c42) 범위밖(PRJ-c58) |
| OPT-D3 | 폴더 변경 슬롯이 두 표만 재구성하고 `populateOptimizationSettings` 를 안 부른다 | OPT-09 | 유효(OPT-c13) |
| OPT-D10 | 방법 선택마다 옵션 칸에 기본값을 주입하고, 저장값 복원은 그 직후 덮어쓰는 순서로만 성립 | OPT-13 | 유효(OPT-c20) |
| OPT-D16 | 프리뷰 모핑이 GUI 스레드 동기이고 이 모듈 `processEvents` 2곳이 모두 그 루프 안 | OPT-26 | 유효(OPT-c09) 해소됨(OPT-c26) 유효(OPT-c57) |
| OPT-D17 | `performMorphing` 이 만든 `.vtu` 2종을 호출부가 곧바로 지운다 | OPT-01 | 유효(OPT-c27) |
| OPT-U2 | 도달하지 않는 선언 4종 | OPT-18 | 유효(OPT-c31) |
| OPT-U3 | `tests/` 전체에 Optimizer 참조 0건 | OPT-20 | 유효(OPT-c32) 유효(OPT-c54) 유효(OPT-c55) 범위밖(UIC-c57) 범위밖(DEV-c24) |
| OPT-D9 | `[popOS]` 디버그 `qDebug` 27줄과 `showEvent` 7줄이 빌드 가드 없이 남아 있다 | OPT-18 | 해소됨(OPT-c19) 유효(OPT-c31) |
| OPT-D23 | 피팅의 학습 모델 경로가 `ModelBuilder_LGE_Spring_Fitting` 하드코딩 | OPT-19 | 유효(OPT-c35) |
| PRE-D7 | 설정 JSON 4섹션 중 `Dataset`·`Output Response` 를 읽는 코드가 없다 | PRE-26 PRE-27 | 유효(PRE-c51) 유효(PRE-c61) |
| PRE-D8 | KPI 행 추가만 `saveOutputResponseToJson` 을 부르지 않는다 | PRE-26 PRE-27 | 유효(PRE-c62) |
| PRE-D10 | 모든 run 이 비-Done 이면 `Done` 필터 결과를 버리고 원본 배열을 쓴다 | PRE-16 | 해소됨(PRE-c63) |
| PRE-U1 | `.op2` 가 확장자 목록·파일 대화상자 필터·솔버 목록에는 있고 라우팅 분기에 NASTRAN 이 없다 | PRE-25 | 유효(PRE-c64) |
| PRE-D4 | Modal 판정이 `contains("modal")` 이고 대상이 단일 파일 모드에서는 basename | PRE-09 | 유효(PRE-c44) 해소됨(PRE-c65) |
| PRE-D5 | `isAnsysMotion` 플래그에 `hasFunctionExpression` 이 실린다 | PRE-08 | 유효(PRE-c66) |
| PRE-D11 | KPI 5종이 배치 입력 로딩(스냅샷-또는-합성) 블록을 각자 복제 | PRE-22 | 유효(PRE-c67) |
| PRE-D1 | `setModel` 에 Output Response 표 초기화가 없다 | 항목 없음 | 해소됨(PRE-c68) |
| PRE-D2 | `onAnalysisFileSelected` 의 조기 반환 4곳이 `endProcessing()` 을 건너뛴다 | 항목 없음 | 해소됨(PRE-c69) |
| PRE-D6 | 배치 후 DLL 상태 복원 블록이 5곳에 있고 일반 배치·Modal KPI·조회 경로에는 없다 | PRE-21 | 유효(PRE-c70) |
| PRE-D3 | 전용 워커·직렬 풀·게이트 0건이고 `processEvents` 25곳이 응답성을 대신한다 | PRE-23 | 유효(PRE-c11) 유효(PRE-c12) 유효(PRE-c71) 유효(PRE-c80) 범위밖(EXE-c43) |
| PRE-D9 | KPI 경로가 `m_isProcessing = true` 보다 앞에서 반환해 재진입 가드 밖에 있다 | CON-07 LCH-08 LCH-12 LCH-20 PRE-23 PRE-24 PRJ-26 | CID 경유 — 해소됨(PRE-c72) 유효(PRE-c80) 범위밖(EXE-c43) |
| PRE-U2 | `initializePreprocessor` 의 `res`·`dfsxml` 분기가 도달하지 않는다 | PRE-25 | 유효(PRE-c73) |
| PRE-U3 | `m_dynamicTables` 는 채우고 비우기만 하고 읽는 코드가 없다 | 항목 없음 | 해소됨(PRE-c74) |
| PRE-D12 | `DashDataProcessor.cpp` 4,671줄이 스캔·질의·XML·KPI 4역 (코드베이스 단일 최대) | 항목 없음 | 해소됨(PRE-c75) |
| RUN-D2 | `variant` 가 JSON 키와 Set 이름 접미사에 이중 보관 | RUN-26 | 유효(RUN-c20) |
| RUN-D10 | 설계변수 값의 정본이 모델이 아니라 셀 위젯 (시그널 결선 없이 폴링) | RUN-17 | 유효(RUN-c27) |
| RUN-D20 | NodeSet 판정 근거가 `Qt::UserRole` 과 이름 목록 2벌이고 후자는 미호출 | 항목 없음 | 해소됨(RUN-c36) |
| RUN-D24 | 두 번째 `updateModelUploadConfig` 가 첫 번째의 `Output Response` 를 덮음 | RUN-05 | 유효(RUN-c38) |
| RUN-D26 | `updateModelUploadConfig` 가 `model_info.json` 을 재파싱해 사용자 입력값을 기본값으로 덮음 | RUN-04 | 유효(RUN-c40) |
| RUN-D33 | 설정 JSON 의 `Prediction Cases`·`Output Response`·`Input Design Variables` | RUN-13 | 유효(RUN-c47) |
| RUN-D34 | `m_predictionCount` 가 세션을 넘기지 못하고 0 에서 재시작 | RUN-10 | 유효(RUN-c15) |
| RUN-D35 | Morphing 생성은 `.vtu` 경로를 싣고 디스크 스캔은 `*.dat`·`*.inp` 를 집는다 | RUN-13 | 유효(RUN-c17) |
| RUN-D14 | `SetBoxHandles` 가 렌더러 부재 시 데이터 없이 반환, 최종 가드는 "비어 있지 않은가" 뿐 | 항목 없음 | 해소됨(RUN-c31) 유효(RUN-c69) 범위밖(REN-c33) |
| RUN-D23 | `startPredictionJob` 의 거절 반환값을 호출부 3곳이 검사하지 않는다 | RUN-05 | 유효(RUN-c07) |
| RUN-D29 | 민감도 콤보가 다른 계층의 키를 기대하고 4단 중첩 `if` 에 로그가 없다 | ANA-18 | 유효(RUN-c43) |
| RUN-D30 | 민감도 폴더 열거에 Set 필터가 없다 | ANA-06 | 유효(RUN-c44) |
| RUN-D13 | Generate 가 Geometry Parameterization 의 공용 핸들 인스턴스를 제자리 교체 | 항목 없음 | 해소됨(RUN-c30) |
| RUN-D15 | `enqueueUpdatePrtGeometry` 가 요청 식별자를 돌려주지 않고 짝짓기가 멤버 문자열 비교 | CAD-01 RUN-09 | 유효(CAD-c39) 범위밖(RUN-c32) 유효(RUN-c70) 범위밖(EXE-c42) |
| RUN-D11 | 스핀박스 상한을 `max - 0.0001` 로 깎고 미설정 판정을 `value != 0.0` 으로 한다 | RUN-16 | 유효(RUN-c28) |
| RUN-D12 | Part 콤보가 모핑 대상이 아니라 `_input_geometry.vtu` 추출 대상만 고른다 | RUN-03 | 유효(RUN-c29) |
| RUN-D18 | 템플릿 치환이 `QMap` 사전순 전역 텍스트 치환 | RUN-18 | 유효(RUN-c34) |
| RUN-D21 | 행 삭제 범위가 `completeBaseName()` 접두사 매칭 | RUN-11 | 유효(RUN-c16) |
| RUN-D37 | MCU 민감도가 이미 `-MCU` 로 끝나는 이름에 접미사를 다시 붙인다 | RUN-22 | 유효(RUN-c49) |
| RUN-D8 | 소스 종류 판정이 `parameter` 딕셔너리 순회 중 첫 매치에서 `break` | RUN-14 | 유효(RUN-c05) 유효(RUN-c68) |
| RUN-D22 | `[Preview]` 만 람다 캡처된 `row` 를 쓴다 (`[X]` 는 매번 재계산) | UIC-24 | 범위밖(RUN-c37) 유효(UIC-c53) 유효(UIC-c62) |
| RUN-D25 | `m_lastPreviewedVtuPath` 를 루프 끝에서 한 번만 세운다 | RUN-20 | 유효(RUN-c39) 유효(RUN-c68) 유효(RUN-c69) 범위밖(REN-c33) |
| RUN-D6 | ND 판정이 응답 이름 부분문자열과 모델 이름 접두사 화이트리스트 2벌 | BLD-21 RUN-15 | 유효(BLD-c45) 유효(RUN-c24) |
| RUN-D9 | `Source` 열 라벨이 같은 JSON 을 다시 열어 별개로 판정하고 실패 3경로가 한 값 | RUN-14 | 유효(RUN-c26) |
| RUN-D19 | 정규화 config 파싱 실패의 처리가 경로마다 다르다 | RUN-08 | 유효(RUN-c35) |
| RUN-D4 | 공용 데몬 수명이 Set 전환에만 묶이고 모듈 이탈에는 안 묶인다 | 항목 없음 | 해소됨(RUN-c22) 해소됨(EXE-c34) |
| RUN-D16 | `m_pendingCadStpPath` 가 완료 슬롯 진입 직후에만 지워진다 | RUN-09 | 유효(RUN-c33) |
| RUN-D17 | CAD 완료 처리가 파일 표를 통째로 재구축한다 | RUN-07 | 유효(RUN-c04) |
| RUN-D31 | 민감도 캐시 키에 모델 내용이 없고 캐시를 비우는 곳이 2곳뿐 | 항목 없음 | 해소됨(RUN-c45) |
| RUN-D32 | 민감도 실패 4경로가 `m_pendingCommand` 를 지우지 않는다 | 항목 없음 | 해소됨(RUN-c46) 해소됨(RUN-c60) 범위밖(EXE-c35) |
| RUN-D36 | `clearAllTables` 가 `m_predictionCount`·`m_pendingCadStpPath`·`m_pendin` | RUN-09 RUN-10 | 유효(RUN-c15) 유효(RUN-c48) |
| RUN-D38 | Set 불일치 시 표를 비우는 방어에 `!currentSetName.isEmpty()` 예외가 붙어 있다 | RUN-21 | 유효(RUN-c50) |
| RUN-D5 | 모델 적재 전 구간이 GUI 스레드 직렬이고 같은 파일을 계층마다 다시 읽는다 | RUN-24 RUN-25 EXE-22 | 유효(RUN-c08) 범위밖(RUN-c09) 유효(RUN-c23) 유효(EXE-c59) |
| RUN-D3 | `daemonReady` 유실 보정이 3벌 중복이고 폴링이 실효 경로 | 항목 없음 | 해소됨(RUN-c21) 해소됨(RUN-c61) 범위밖(EXE-c36) |
| RUN-D27 | 1D 결과 대기가 고정 500ms 뒤 `lastModified` 최대 CSV 선택 | RUN-19 EXE-12 | 유효(RUN-c41) 유효(RUN-c62) 유효(EXE-c29) 범위밖(EXE-c38) |
| RUN-D7 | `configsDir` 이 양쪽 컨텍스트에 Set 무관 전역 경로로 들어가 삼항 폴백이 무의미 | RUN-27 | 유효(RUN-c25) |
| RUN-U1 | `syncFileTableToJson` 이 주석뿐인 빈 본문인데 3곳에서 호출된다 | RUN-13 | 유효(RUN-c51) |
| RUN-U2 | 체크 행 일괄 삭제 39줄이 구현돼 있으나 `connect` 0건이고 버튼도 없다 | RUN-29 | 유효(RUN-c52) |
| RUN-U3 | `params.fileTableFiles` 와 그 유일한 소비 함수가 도달 불가 | RUN-29 | 유효(RUN-c53) |
| RUN-U4 | 구버전 CLI 형태(출력 디렉터리 인자 없음)의 예측 슬롯이 남아 있다 | RUN-29 | 유효(RUN-c54) |
| RUN-U5 | 도메인 신호 4종의 수신처가 0곳 | RUN-29 | 유효(RUN-c55) |
| RUN-U6 | 도달하지 않는 정의 18종 | RUN-29 | 유효(RUN-c56) |
| RUN-D28 | 뷰가 `DashMainWindow` 를 부모 거슬러 4벌로 찾는다 | RUN-28 PRJ-25 | 유효(RUN-c42) 유효(PRJ-c54) |

집계: 항목 159 · 해소됨 21 · 항목(CID 경유) 8 · 범위밖/해소됨 8 · CLOSE 3 · 유효/해소됨 1 · 범위밖/유효/해소됨 1
