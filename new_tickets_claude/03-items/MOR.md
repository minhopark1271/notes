# MOR 작업 목록

> 기준 코드: dev @ b08a91b3. 열린 PR **#654**(핸들 상태기 · mesh-ops sampling · `Morphing.handles` v1 · MeshOps 0.5.0)가 `view/DashGeometryParameterWidget.*`·`controller/DashHandlePickingInteraction.*`·`controller/DashMorphingController.*`·`viewmodel/DashGeometryParameterPresentationModel.*`·`view/overlay/DashMorphingSettings.*`·`controller/DashMorphingDoeExecutor.cpp`·`model/geometry/DashMorphingUtils.*` 를 크게 바꾼다. 이 파일들을 만지는 항목은 전부 **#654 머지 후 착수**가 안전하고, 선행에 `PR #654` 로 적었다.
>
> 그 위에 쌓인 열린 PR **#655**(`refactor/430-handle-sets-render`, base #654, +6,722/−6,994, "Closes #430 · Closes #322 · Part of #427 · Refs #332")가 렌더·피킹·편집을 entry 상태로 통합하고 `m_handleGeometry`·`GizmoGroup`·`DashHandleImport`·`DashSampledHandleTree`·구 피킹 경로를 삭제한다 — 변경 파일 71개로 MOR 변경 범위 파일 대부분을 다시 쓴다. 아래 항목의 `선행` 은 #654 가 아니라 **#655** 머지 기준이고, 좌표는 머지 후 재측정이 필요한 곳에 표시했다. 충돌란의 열린 PR 은 D-1 `build_deps.py --apply` 가 파일 교집합으로 자동 기입한다.
>
> 원천별 claims 는 `02-claims/MOR.md`. #281 의 열린 PR 은 없다 — 잔여 판정은 이슈 본문 Phase 표 대 현행 코드로 했다.

### MOR-01 · QC 결과 다이얼로그의 `processEvents` 를 걷고 `finished` 대기를 `setResults` 앞에 세운다
- 종류: PR | 규모: S | 태그: B · bug
- 목표: `DashMeshQualityDialog::setResults` 의 `processEvents(AllEvents, 100)` 를 삭제하고, 호출부가 `qCoro(dialog, finished)` awaitable 을 `setResults` 전에 만들어 둔다. 결과 표시 중 Esc/닫기가 코루틴을 영구 suspend 시키고 `qcDialog_` 가 non-null 로 굳어 Set Design Variable 이 세션 내내 "already running" 이 되는 경로가 사라진다.
- 완료 기준: (1) `view/dialog/DashMeshQualityDialog.cpp` 에 `processEvents` 0건 — MOR 영역 view pE 0 (2) `disconnect(cancelOnClose)` 와 `co_await` 사이에 시그널이 발화해도 결정이 수신된다 — "Analysis Complete" 직후 Esc → `qcDialog_` 가 비고 다음 클릭이 동작 (3) Step 1/2 → 2/2 진행 텍스트가 여전히 갱신된다
- 변경 범위: `view/dialog/DashMeshQualityDialog.cpp` · `view/DashGeometryParameterWidget.cpp` (`onSaveDesignVariableClicked` `:1456-1463`)
- 선행: -
- 충돌: PR #654 (`view/DashGeometryParameterWidget.cpp` 259/310 변경 — 같은 함수 구간은 아님) · B2 교집합: DashGeometryParameterWidget.cpp → DEV-10 MOR-02 MOR-03 MOR-17 MOR-22 MOR-23 UIC-20 · DashMeshQualityDialog.cpp → UIC-12 UIC-13 · PR #655(DashGeometryParameterWidget.cpp)
- 흡수: #512-1 · #512-2 · #512-3 · #455(MOR 몫) · #463(MOR 몫) · MOR-c15, MOR-c16, MOR-c17 · MOR-c79, MOR-c86 (← PRJ-c48, EXE-c23)
- 비고: 자동 테스트는 `tests/` 하네스에 Widgets 가 없어 불가(`tests/CMakeLists.txt:33`). 수동 시나리오 1건("결과 표시 직후 Esc → 재클릭 동작")을 PR 본문에 기록한다. #463 확산의 MOR 몫 — QC 진행 텍스트·취소(`cancelOnClose`)·프리뷰 세대 폐기(`previewStop_`)는 이미 있고, 남은 결함이 이 항목. 가드 형식은 EXE-07 · 09

### MOR-02 · Constraints(고정 영역) 을 이름·셀 id 로 저장하고 Set 재진입 시 표와 오버레이를 복원한다
- 종류: PR | 규모: M | 태그: A, C · bug
- 목표: Set 저장이 `Morphing.constraints` 를 쓰지 않아 재진입·Set 전환 시 Constraints 표와 Non-design 영역이 사라지고, 그 상태에서 다시 Set 을 누르면 고정 영역이 빈 집합으로 덮여 DOE-Morphing 이 Non-design 없이 도는 비대칭을 없앤다. PR #654 가 세운 `Morphing.handles` v1 과 `DashFixedRegion` 위에 fixed 영역을 라벨(그룹 이름 + surface 셀 id)로 영속하고, 로드가 그룹별로 `appendConstraintTable` → 기존 시각화 사슬을 탄다. 구 형식(`AllFixedVolumeIds` 만 있는 VTP · `constraints[].node_ids`)은 PR #654 정책대로 변환하지 않는다.
- 완료 기준: (1) Constraints 지정 → Set → 모듈 재진입/Set 전환 후 표 행·오버레이·`fixedRegions` 가 같다 (2) 재진입 뒤 다시 Set 을 눌러도 고정 영역 수가 유지된다 (3) `test_handle_state`(또는 `TestFixedRegion`) 에 라벨 왕복 1건
- 변경 범위: `controller/DashHandleState.{h,cpp}`·`DashHandleStateJson.cpp`·`DashHandleDefinition.{h,cpp}`·`DashHandleRuntime.{h,cpp}` (PR #654·#655 신설) · `controller/DashFixedRegion.{h,cpp}` · `view/DashGeometryParameterWidget.cpp` (`loadMorphingFromJson`·`appendConstraintTable`·Set 수집) · `controller/DashHandlePickingInteraction.{h,cpp}` (`m_constraintSurfaceIds` 노출 — #655 에서 살아남지만 파일이 3,267 → 약 1,560줄로 줄어 `:3121`·`:3198` 좌표는 **머지 후 재측정**) · `tests/`
- 선행: PR #655
- 충돌: MOR-03 (같은 수집 경로) · MOR-15 · B2 교집합: DashGeometryParameterWidget.cpp → DEV-10 MOR-01 MOR-17 MOR-22 MOR-23 UIC-20 · DashHandlePickingInteraction.cpp → MOR-04 MOR-06 MOR-13 MOR-17 MOR-23 · DashHandlePickingInteraction.h → MOR-04 MOR-06 MOR-07 MOR-23 · DashHandleDefinition.cpp → MOR-05 MOR-17 · DashHandleDefinition.h → MOR-05 MOR-17 · DashHandleStateJson.cpp → MOR-05 MOR-17 · DashHandleState.cpp → MOR-06 · PR #654(DashFixedRegion.cpp·DashFixedRegion.h·DashGeometryParameterWidget.cpp·DashHandlePickingInteraction.cpp·DashHandlePickingInteraction.h·DashHandleState.cpp·DashHandleState.h·DashHandleStateJson.cpp)
- 흡수: #563 · MOR-D10 · MOR-c18, MOR-c19, MOR-c20, MOR-c23, MOR-c56
- 비고: #563 "기대" 의 스키마(JSON 이름·그룹 id + VTP 병렬 배열)는 PR #654 이후 VTP 가 없으므로 그대로 쓰지 않는다 — `DashFixedRegion` 에 PR #654 가 남긴 스펙 댓글(#563) 기준으로 설계한다. `referenceModel.uuid` 불일치 시 복원 건너뛰기는 유지

### MOR-03 · Hide 상태 행도 Set 수집에 포함되게 표시 상태와 소속을 분리한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `updateConstraintVisualization` 이 Show 행만 `SetVisibleConstraintIds` 에 넘기고 그 함수가 `m_constraintSurfaceIds` 를 덮어쓰므로 Hide 상태로 Set 을 누르면 Non-design 이 축소 저장된다. Show/Hide 는 오버레이에만 관여하고, Set 수집은 표 전체 행을 쓴다.
- 완료 기준: (1) 행 하나를 Hide 한 채 Set → `fixedRegions`/고정 id 수가 Show 때와 같다 (2) 오버레이는 Hide 행을 그리지 않는다
- 변경 범위: `view/DashGeometryParameterWidget.cpp` (`updateConstraintVisualization:2957` — #655 가 `fixedRegionsChanged()` 3줄을 추가) · `controller/DashHandlePickingInteraction.{h,cpp}` (`SetVisibleConstraintIds:3198` 를 표시 전용으로, 소속은 별 setter). 두 좌표 모두 **머지 후 재측정**
- 선행: PR #655
- 충돌: MOR-02 (같은 함수 — MOR-02 에 합쳐도 됨, 단 동작 변경 2건을 한 PR 에 싣는 셈) · B2 교집합: DashGeometryParameterWidget.cpp → DEV-10 MOR-01 MOR-17 MOR-22 MOR-23 UIC-20 · DashHandlePickingInteraction.cpp → MOR-04 MOR-06 MOR-13 MOR-17 MOR-23 · DashHandlePickingInteraction.h → MOR-04 MOR-06 MOR-07 MOR-23 · PR #654(DashGeometryParameterWidget.cpp·DashHandlePickingInteraction.cpp·DashHandlePickingInteraction.h)
- 흡수: #563 부수 · MOR-c22
- 비고: -

### MOR-04 · `m_nonDesignSurfaceIds` 와 `UpdateNonDesignFromUG()` 사문 코드를 지운다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: 유일 writer `UpdateNonDesignFromUG()` 호출부가 0 이라 항상 빈 집합인 `m_nonDesignSurfaceIds` 와 그 소비 분기 3곳을 삭제한다. 같은 성격의 사문 `DashMorphingUtils::applySurfaceExtraction`(정의만 있고 호출 0)도 함께 지운다. 실질 Non-design 소스는 Constraints 표 하나임을 코드가 말하게 한다.
- 완료 기준: (1) `UpdateNonDesignFromUG`·`m_nonDesignSurfaceIds`·`applySurfaceExtraction` grep 0건 (2) 빌드·`test_handle_cloud`·`test_fixed_region` 통과 (3) 고정 id 산출 결과 무변경
- 변경 범위: `controller/DashHandlePickingInteraction.{h,cpp}` (`:3121-3190`, `:1552`, `:1637`, `:3017`, `.h:207`·`:216`·`:279` — **머지 후 재측정**) · `model/geometry/DashMorphingUtils.{h,cpp}` (`.cpp:405`·`.h:67`)
- 선행: PR #655 (같은 파일 −1,707줄. `UpdateNonDesignFromUG`·`m_nonDesignSurfaceIds` 는 #655 무접촉으로 살아남는다)
- 충돌: MOR-02 · MOR-15 · B2 교집합: DashHandlePickingInteraction.cpp → MOR-03 MOR-06 MOR-13 MOR-17 MOR-23 · DashHandlePickingInteraction.h → MOR-03 MOR-06 MOR-07 MOR-23 · PR #654(DashHandlePickingInteraction.cpp·DashHandlePickingInteraction.h·DashMorphingUtils.cpp·DashMorphingUtils.h)
- 흡수: #563 부수 · #281-A(dead writer 몫) · MOR-c21, MOR-c89
- 비고: 동작 불변이라 MOR-02 와 섞지 않는다. `applySurfaceExtraction` 의 짝 `savePartAsVtu` 는 RUN-c56 소관

### MOR-05 · Box(FFD) 핸들 생성 UI 를 되살릴지 정한다
- 종류: DEC | 규모: S | 태그: E, D · feature
- 목표: PR #655 가 GUI 의 shell 격자 box 생성 경로를 대체가 아니라 **삭제**했다 — `onGenerateBoxHandles`·`setHandlesBoxhandle`·`applyGenerateHandlesAsBox`·`GenerateAndShowBoxHandles`·`m_pendingBoxHandles`·`BoxHandleInfo`·Hexahedron 설정 페이지(`getHexaGridParams`·`generateHexaBoxHandlesRequested`·.ui) 전부. Box 엔트리는 JSON 으로만 들어오고 baseline 편집은 미지원(`transformed()` 거부)이다. #577 은 "복원이 아니라 mesh-ops `BoxHandles` FFD 신규(DV = 면 오프셋 `set_faces`, 기즈모 릴리즈 1회 반영)" 로 노선만 정해 두었다. 그 UI 를 실제로 만들지, 만든다면 mesh-ops lattice 가 내부까지 채우고 축당 분할 수가 하나(`num_subdivisions`)인 제약을 어디까지 수용할지 정한다.
- 완료 기준: 결정 기록 — (1) Volume → Hexahedron 생성 UI 신설 여부와 근거 (2) 신설이면 lattice·`num_subdivisions` 수용 범위, `gridX/Y/Z` UI 축소 여부, Box baseline 편집 처분 (3) 불요면 #499-1 · #577 의 닫기 사유
- 변경 범위: 결정이 "신설" 이면 후속 feature PR M — `view/overlay/DashMorphingSettings.{h,cpp}`·`ui/overlay/DashMorphingSettings.ui`(Hexahedron 페이지 재신설) · `controller/DashHandleDefinition.{h,cpp}`·`DashHandleStateJson.cpp`(Box 엔트리 생성·영속) · `view/overlay/DashMorphingBar.cpp:27`(Volume 목록) · `tests/TestHandleState.cpp`
- 선행: PR #655 (삭제 범위가 확정되는 시점)
- 충돌: B2 교집합: DashMorphingBar.cpp → DEV-10 MOR-14 UIC-07 · DashMorphingSettings.cpp → MOR-12 MOR-23 UIC-22 · DashHandleDefinition.cpp → MOR-02 MOR-17 · DashHandleDefinition.h → MOR-02 MOR-17 · DashHandleStateJson.cpp → MOR-02 MOR-17 · DashMorphingSettings.h → MOR-12 UIC-22 · PR #654(DashHandleStateJson.cpp·DashMorphingBar.cpp·DashMorphingSettings.cpp·DashMorphingSettings.h·TestHandleState.cpp)
- 흡수: #499-1 · #577 · MOR-c26, MOR-c90
- 비고: mesh-ops 에 shell/축별 옵션을 요청하는 쪽이면 EXT 가 선행. 결정이 "신설" 이면 #577 의 완료 기준(면 드래그 → Done → DV 표 face 행 → 범위 → 프리뷰 → Save → DOE · Set 재열기 후 유지)이 그대로 후속 PR 의 완료 기준이 된다

### MOR-06 · marching plane 단면 핸들을 mesh-ops `section_frames` + `SectionFrameHandles` 로 대체하고 `libs/DashMarchingPlane` 을 삭제한다
- 종류: PR | 규모: M | 태그: E, F · refactor
- 목표: 남은 기제는 **절단기 교체**다 — PR #655 가 pending `MarchingPlaneData` → `SectionFrameHandles::create({.frame = f, …})` 생성까지 이미 넣었고, 자르는 쪽은 그대로 `MarchingPlaneBound`(vtkPolyDataAlgorithm, 상류 미머지 브랜치 출처, #655 무접촉)다. `onGenerateMarchingPlaneHandleRequested` 가 `marchingPlane->GetOutput()` 대신 `dash::mesh::section_frames(surface, start, end, N)` 를 쓰게 바꾸고, `MarchingPlaneData` pending 과 `libs/DashMarchingPlane`·`add_subdirectory`·ALIAS·install 항목을 제거한다. 끝 단면 skip 은 호출자가 목록에서 지운다.
- 완료 기준: (1) `libs/DashMarchingPlane` 디렉터리·`MarchingPlaneBound`·`MarchingPlaneData`·`m_pendingMarchingPlanes` grep 0건, `CMakeLists.txt` 에서 `DashMarchingPlane` 0건 (2) Volume 모드 Generate → Done 이 만드는 `SectionFrameHandles` set 의 단면 수·프레임이 교체 전과 같다 (3) Release·Debug 빌드·기동
- 변경 범위: `controller/DashMorphingController.{h,cpp}` (`:44`, `:76-203`) · `controller/DashHandlePickingInteraction.{h,cpp}` (`.h:42`·`:94-97`·`:332`, `Finalize` VOLUME 분기, `UpdateMarchingPlaneMarkers`) · `controller/DashHandleState*.cpp` · `CMakeLists.txt` (`:370-371`·`:404`·`:413`) · `libs/DashMarchingPlane/` 삭제 · `tests/`
- 선행: PR #655 (`SectionFrameHandles` 생성 경로가 거기 있다)
- 충돌: MOR-05 · MOR-07 (같은 `CMakeLists.txt` 블록) · MOR-15 · B2 교집합: CMakeLists.txt → DEV-11 DEV-21 DEV-24 DEV-25 UIC-02 · DashHandlePickingInteraction.cpp → MOR-02 MOR-03 MOR-04 MOR-13 MOR-17 MOR-23 · DashHandlePickingInteraction.h → MOR-02 MOR-03 MOR-04 MOR-23 · DashHandleState.cpp → MOR-02 · DashMorphingController.cpp → MOR-21 · DashMorphingController.h → MOR-21 · PR #658(CMakeLists.txt) · PR #654(CMakeLists.txt·DashHandlePickingInteraction.cpp·DashHandlePickingInteraction.h·DashHandleState.cpp·DashMorphingController.cpp·DashMorphingController.h)
- 흡수: #499-2 · #331-3 · MOR-c27, MOR-c42
- 비고: 단면당 중심점 1개 → 격자로 바뀌는 결과 차이는 PR #655 가 이미 만든 변화다. #331-3(상류 환원)은 이 대체로 불요. 규모는 파일 6개 + libs 삭제라 M 유지

### MOR-07 · `libs/DashGizmo` 를 앱 소스 트리로 옮겨 단일 빌드로 만든다
- 종류: PR | 규모: M | 태그: F, E · refactor
- 목표: 독립 static 타깃 + `DashGizmo::DashGizmo` ALIAS 로 링크하던 Gizmo 소스를 `controller/gizmo/`(또는 `libs/` 밖 glob 범위) 로 옮겨 `DashOptGUI` 하나로 컴파일한다. `add_subdirectory`·ALIAS·`libs/DashGizmo/CMakeLists.txt`·install TARGETS 항목이 사라진다. 원본 `DashOpti_Gizmo` 와의 재동기화 정책(fork 유지 / 원본 아카이브 / GUI 정본 승격)을 README 에 기록한다.
- 완료 기준: (1) `libs/DashGizmo` 부재, 링크 목록에 `DashGizmo.lib` 부재, unresolved external 0 (2) `CMakeLists.txt` 에 `DashGizmo` ALIAS·`add_subdirectory` 0건 (3) Release·Debug 빌드·기동, 기즈모 조작 무회귀
- 변경 범위: `CMakeLists.txt` (`:366-368`·`:403`·`:413`) · `libs/DashGizmo/{include,src}/DashGizmo.{h,cpp}` 이동 (PR #655 가 `GizmoGroup.{h,cpp}` 를 삭제하므로 대상은 2파일) · `libs/DashGizmo/README.md` · include 경로 2파일(`controller/DashGizmoPlane.h`·`controller/DashHandlePickingInteraction.h` — `.cpp` 에는 include 없음) + 머지 후 신설 includer `controller/DashHandleGizmoEditor.cpp`
- 선행: PR #655 (`DashGizmo.h` +169/−74 · `DashGizmo.cpp` +497/−331 · `libs/DashGizmo/CMakeLists.txt` 수정 — 머지 전에 파일을 옮기면 #655 리베이스 비용이 생긴다)
- 충돌: MOR-06 (`CMakeLists.txt` 인접 블록) · B2 교집합: CMakeLists.txt → DEV-11 DEV-21 DEV-24 DEV-25 UIC-02 · DashHandlePickingInteraction.h → MOR-02 MOR-03 MOR-04 MOR-23 · README.md → DEV-01 DEV-02 DEV-12 DEV-21 DEV-24 · DashGizmo.cpp → MOR-08 · DashGizmo.h → MOR-08 · GizmoGroup.cpp → MOR-08 · GizmoGroup.h → MOR-08 · PR #658(CMakeLists.txt) · PR #654(CMakeLists.txt·DashHandlePickingInteraction.h)
- 흡수: #331-1 · MOR-c40
- 비고: VTK COMPONENTS(`CommonComputationalGeometry`·`CommonMath`·`CommonTransforms`)는 루트에 이미 있다(`:302`·`:306`). 서브 CMakeLists 의 `find_package(VTK)` 재호출 함정은 단일 빌드로 소멸

### MOR-08 · 이관된 Gizmo 소스의 표기 관례를 저장소 규칙에 맞춘다
- 종류: PR | 규모: S | 태그: G, E · refactor
- 목표: 원본 레이아웃 보존을 위해 미뤘던 `_position` 식 선행 밑줄 등 표기를 `.clang-format`·`.clang-tidy`(#321 Done) 규칙으로 정리한다. MOR-07 로 `libs/` 가 사라지면 "원본 diff 대응" 예외 근거도 함께 사라진다. PR #655 의 "기즈모 서식" 커밋은 clang-format 만 적용했고 `_position`·`_euler_angles`·`_object_scale`·`_screen_pixels`·`_range_min` 식 표기는 그대로다.
- 완료 기준: (1) `scripts/hooks/run-format-checks.sh` 가 이동된 2파일(`DashGizmo.{h,cpp}`)을 통과 (2) 동작 무변경 — 기즈모 수동 시나리오 (3) 결정 기록: 규칙 적용 여부(예외 유지면 그 근거)
- 변경 범위: `DashGizmo.{h,cpp}` (MOR-07 이후 위치 — `GizmoGroup.{h,cpp}` 는 PR #655 가 삭제)
- 선행: MOR-07
- 충돌: B2 교집합: PR #655(DashGizmo.cpp·DashGizmo.h·GizmoGroup.cpp·GizmoGroup.h)
- 흡수: #331-2 · MOR-c41
- 비고: -

### MOR-09 · #322 닫기 — PR #655 가 `GizmoGroup` 을 삭제해 정리할 컨테이너가 없어진다
- 종류: CLOSE | 규모: S | 태그: E
- 목표: 닫기 사유 기록. `_members`·`_active`·`_savedState` 병렬 컨테이너와 `removeMember` 리인덱싱·`setChecked` 재진입 오염은 PR #655 가 `libs/DashGizmo/{include/GizmoGroup.h,src/GizmoGroup.cpp}` 를 통째로 삭제하고 `libs/DashGizmo/CMakeLists.txt` 에서 `src/GizmoGroup.cpp` 를 빼면서 함께 사라진다. 핸들 기즈모는 `DashHandleGizmoEditor` 가 entry 단위로 만든다. PR 본문이 "Closes #322" 로 못박았다.
- 완료 기준: 닫기 사유 — PR #655 머지 확인 후 닫는다 · 머지 후 `git grep GizmoGroup` 0건 · 머지가 깨지면 MOR-c38 을 PR 항목(규모 M)으로 되살린다
- 변경 범위: -
- 선행: PR #655
- 충돌: -
- 흡수: #322 · MOR-c38, MOR-c39 · MOR-c80 (← REN-c31, #322 몫)
- 비고: `_recalculateCentroid` 의 평균 방향 roll 소실·`GetRangeMin/Max` 우회·`_members` raw 포인터 수명 계약은 #322 not-to-be 로 범위 밖이었고 타입 삭제로 소멸한다. `external/DashGizmo` 사본은 gitignore 대상이라 처리 불요

### MOR-10 · DV-Geometry `source` 가 없는 GP 세트의 배치·단건 동작을 하나로 정한다
- 종류: DEC | 규모: S | 태그: A, C
- 목표: 같은 세트에 대해 DOE 배치(`DashMorphingDoeExecutor::plan`)는 WARN 후 Target Component 만 검증하고 진행하고, Optimizer·ModelRunner(`validateMorphingTarget` "names no part")는 거부한다. 하드 실패(세트 재저장 유도) 또는 진행(그러면 `source` 를 채우는 마이그레이션 유무) 중 하나로 결정하고 세 경로를 맞춘다.
- 완료 기준: 결정 기록 — (1) 선택지와 근거 (2) 세 호출부(`DashMorphingDoeExecutor.cpp:404-421` · `DashModelRunner.cpp:2291` · `DashOptimizer.cpp:1532`) 의 목표 동작 (3) 결정이 "진행" 이면 마이그레이션 여부(PR #654 의 "구 Set 변환 없음" 정책과 정합)
- 변경 범위: 결정 후 PR 은 `controller/DashMorphingDoeExecutor.cpp` 1줄 (+ RUN·OPT 각 1줄 — 접점)
- 선행: -
- 충돌: PR #654 (`DashMorphingDoeExecutor.cpp` 18/60) · #434 (part 를 Set 상태로 — 4단계가 이 검사를 없앤다, `:383` TODO) · B2 교집합: DashMorphingDoeExecutor.cpp → LCH-13 MOR-11
- 흡수: #557 · MOR-c43, MOR-c44
- 비고: #434 4단계가 먼저 오면 이 결정은 소멸한다 — PRJ(#434) 진척을 확인한 뒤 결정한다

### MOR-11 · 모핑 반경 기본값 10.0 의 소유자를 하나로 하고 대역 사용을 WARN 으로 남긴다
- 종류: PR | 규모: M | 태그: A, E · refactor
- 목표: `.ui` 스핀박스 · `DashGeometryParameter::m_morphingRadius` · `kDefaultMorphingKernelRadius` · `DashMorphingDoeExecutor::m_kernelRadius` · ModelRunner/Optimizer 의 `toDouble(10.0)` 여섯 곳이 각자 들고 있는 10.0 을 소유자 1곳(`DashGeometryParameter` · 도메인 상수 · 또는 PR #654 가 세운 상태기 `DashHandleSetup::radius()` 중 하나)에서 읽게 하고, `Morphing.radius` 를 읽는 함수 3개를 값 타입 하나 + `FromJson` 하나로 모아 같은 파서·같은 대역·같은 WARN 을 쓰게 한다. 값 자체(10.0)는 바꾸지 않는다.
- 완료 기준: (1) 리터럴 `10.0` 이 반경 의미로 남은 곳 1 — 건수는 PR #654 머지 후 재측정 (2) `radius` 키 없는 JSON 으로 DOE·Runner·Optimizer 실행 시 WARN 1줄 (3) `.ui` 값은 `setValue` 로 대체하거나 소유자와 같음을 테스트로 고정
- 변경 범위: `ui/DashGeometryParameterWidget.ui:130` · `model/DashGeometryParameter.{h,cpp}` (`.h:93`·`.cpp:212`) · `controller/DashMorphingBasis.h:31-35` · `controller/DashMorphingDoeExecutor.{h,cpp}` (`.h:97`·`.cpp:338`) · `view/DashGeometryParameterWidgetHandles.cpp` (PR #654 신설 — `persistHandleSetup` 이 `morphing["radius"] = handleSetup()->radius()` 로 쓴다) · `model/DashModelRunner.cpp:2344` (RUN 접점) · `model/DashOptimizer.cpp:1462` (OPT 접점)
- 선행: PER-10 (초기값 정책 — 있으면 따른다; 없어도 #423 초안 정책으로 착수 가능) · PR #654 (`Morphing.radius` 쓰기 정본이 하나 늘어 6곳 집계가 바뀐다)
- 충돌: PR #654 (`e82b7ba` 반경 변경 시 상태 재구축 — `DashGeometryParameterWidget`·`DashModelRunner.cpp`·`DashOptimizer.cpp` 수정) · B2 교집합: DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashGeometryParameter.cpp → PRJ-09 UIC-20 · DashMorphingDoeExecutor.cpp → LCH-13 MOR-10 · DashGeometryParameterWidget.ui → UIC-10 · DashGeometryParameterWidgetHandles.cpp → MOR-22 · DashMorphingDoeExecutor.h → LCH-13 · PR #655(DashGeometryParameterWidget.ui·DashGeometryParameterWidgetHandles.cpp)
- 흡수: #423 (모핑 반경 사례) · MOR-c45
- 비고: #423 의 1·2 단계(전수 조사·정책 문서)는 횡단이라 PER 로 넘겼다(MOR-c46). 이 항목은 3 단계 첫 사례

### MOR-12 · Morphing Settings 의 Generate 분기를 `isVisible()` 캐스케이드에서 현재 페이지 키로 바꾼다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `m_generateButton` 클릭 람다가 설정 위젯의 `isVisible()` 을 순서대로 검사해 신호를 고르는 구조를 — dev 는 7단, PR #654 가 cylinder·PR #655 가 hexahedron 분기를 지워 머지 후 5단(automatic · parametric×2 · physics · marching) — `swapSettingsWidget` 이 세우는 현재 페이지 enum 하나로 분기하게 한다. 페이지를 추가해도 캐스케이드 순서가 계약이 되지 않는다.
- 완료 기준: (1) 람다 안 `isVisible()` 0건 (2) 남은 모드 전부 × Generate 가 같은 신호를 낸다 (3) 빌드·기동
- 변경 범위: `view/overlay/DashMorphingSettings.{h,cpp}` (`:111-160`, `swapSettingsWidget` — 좌표는 머지 후 재측정)
- 선행: PR #655 (같은 파일 −213/−110: Advanced·Hexahedron 제거)
- 충돌: MOR-05 (Hexahedron 페이지) · B2 교집합: DashMorphingSettings.cpp → MOR-23 UIC-22 · DashMorphingSettings.h → UIC-22 · PR #654(DashMorphingSettings.cpp·DashMorphingSettings.h)
- 흡수: MOR-D3 · MOR-c49
- 비고: 머지 후 분기 5단에서 재측정하고 착수한다. MOR-05 결정이 "Hexahedron 신설" 이면 페이지가 하나 늘어 이 항목이 먼저 오는 쪽이 싸다

### MOR-13 · `MODE_PHYSICS` 를 `SetInteractionMode` 의 switch 에 넣는다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: 툴바 Physics 버튼이 `MODE_PHYSICS` 를 세우지만 switch 에 case 가 없어 `default: break` 로 떨어져 픽킹 방식이 직전 모드에서 이월된다. 의도한 `PickingMode`(File Import 페이지는 픽킹 없음 → `MODE_CLICK` + `m_boxWidget->Off()` 추정)를 명시한다.
- 완료 기준: (1) Constraints(박스) → Physics 로 전환하면 박스 위젯이 꺼진다 (2) Physics → Manual 왕복 무회귀
- 변경 범위: `controller/DashHandlePickingInteraction.cpp:1308-1346` — PR #655 가 `SetInteractionMode` 를 `:928` 로 옮기고 파일을 −1,707줄 바꾸므로 **머지 후 재측정**
- 선행: -
- 충돌: B2 교집합: DashHandlePickingInteraction.cpp → MOR-02 MOR-03 MOR-04 MOR-06 MOR-17 MOR-23 · PR #655(DashHandlePickingInteraction.cpp) · PR #654(DashHandlePickingInteraction.cpp)
- 흡수: MOR-U1 · MOR-c61
- 비고: 어느 픽킹 모드가 맞는지는 1줄 결정. 확정 전이면 `MODE_CLICK` 으로 두고 PR 에 기록

### MOR-14 · 툴바 Prev/Next 의 처분을 정한다 — 버튼 제거 또는 Undo/Redo 구현
- 종류: DEC | 규모: S | 태그: D, G
- 목표: `DashMorphingBar` 의 `stepPrevClicked`/`stepNextClicked` 는 emit 만 하고 수신처가 없다. `DashMainWindow::onEditUndo/onEditRedo` 의 TODO 와 짝이다. (a) 버튼·시그널·`.ui` 항목을 지운다, (b) 모핑 편집 undo 스택을 설계한다 중 하나를 정한다.
- 완료 기준: 결정 기록. (a) 면 후속 PR S — `view/overlay/DashMorphingBar.{h,cpp}`·`ui/DashMorphingBar.ui`·`DashMainWindow` `ResetMorphingBar` 분기. (b) 면 별도 설계 항목
- 변경 범위: `view/overlay/DashMorphingBar.{h,cpp}` (`.h:44-45`·`.cpp:67-68`) · `ui/` 대응 · `view/DashMainWindow.cpp:4800-4810` (PRJ 접점)
- 선행: -
- 충돌: B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashMorphingBar.cpp → DEV-10 MOR-05 UIC-07 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp·DashMorphingBar.cpp) · PR #652(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: MOR-U2 · MOR-c62
- 비고: 출고 품질(G) 관점에서 (a) 가 값싸다. Edit 메뉴 Undo/Redo 자체의 처분은 PRJ 몫

### MOR-15 · #430 닫기 — PR #655 가 interaction 의 핸들 소유를 해제했다
- 종류: CLOSE | 규모: S | 태그: E, C
- 목표: 닫기 사유 기록. #430 의 "PR 2" 가 PR #655 다 — `m_handleGeometry` 를 삭제하고 렌더를 set 의 `handle_output_port()`·`control_output_port()` 에 직접 붙이며(`DashHandleEntryRenderer`), `DashHandleImport`·`DashSampledHandleTree`·구 피킹 경로(약 1,900줄)와 `.cpp:1409` TODO 를 지운다. 원문의 VTP 읽기 5곳·쓰기 2곳 일원화는 PR #654 가 VTP 자체를 없애 소멸했고, `DashHandleData` 타입 신설은 `DashHandleDefinition` + `DisplacementPolicy` 가 대신한다. PR 본문이 "Closes #430" 이다.
- 완료 기준: 닫기 사유 — PR #655 머지 확인 후 닫는다 · 머지 후 `git grep m_handleGeometry` 0건 · 잔여를 MOR-23(INV)으로 분리했음을 명시 · 머지가 깨지면 MOR-c33 을 PR 항목(규모 L)으로 되살린다
- 변경 범위: -
- 선행: PR #655
- 충돌: -
- 흡수: #430 · MOR-D4 · MOR-c33, MOR-c34, MOR-c50 · MOR-c80 (← REN-c31, #430 몫)
- 비고: L 사유였던 "빌드 가능한 분할선이 보이지 않는다" 는 #655 가 해소했다. HDVS ⓒ-2·ⓓ·ⓕ 의 잔여(`UpdateSurfaceGeometry` 분해 · `.h:36` TODO · view/viewmodel 직접 쓰기 · `DashMorphingSettings` 표면 배열 2곳)는 MOR-23 이 받는다

### MOR-16 · 모핑 서비스에 동결·실행 소요 시간 계측을 넣는다
- 종류: PR | 규모: S | 태그: B · perf
- 목표: `DashMorphingService::submitFreeze`/`submitMorph` 가 요청 단위로 동결 시간과 실행 시간을 따로 재서 DEBUG 로그에 남긴다. 레인당 고정 `코어/2` 예산의 동적 재배정과 프리뷰 응답성 판단의 입력이 된다(#313 이후 모핑 1회 비용 미측정).
- 완료 기준: (1) 프리뷰 1회·QC 1회·DOE 샘플 1회의 로그에 `freeze ms`·`morph ms` 가 핸들 수와 함께 남는다 (2) `test_morphing_service` 무회귀
- 변경 범위: `controller/DashMorphingService.cpp` (`:140-182`) · 필요 시 `controller/DashMorphingRun.cpp`
- 선행: -
- 충돌: PR #654 (`DashMorphingService.h` +9줄)
- 흡수: #281 Follow-up ⑷ (#408 이월) · MOR-c12
- 비고: 계측값이 나오면 예산 재배정은 별 항목(DEC)으로 올린다

### MOR-17 · PR #655 머지 후 레거시 핸들 경로의 정본 결함 3건을 재판정한다 — 이름 미저장 · θ 왕복 · 범위값 정본
- 종류: INV | 규모: S | 태그: A, C · bug
- 목표: 현행 dev 에서 유효한 MOR-D5(핸들 이름 writer 0 — `HandleNames` 배열 읽기만 있음), MOR-D6(θ 는 벡터로만 저장, 표시는 Euler 역산), MOR-D9(저장이 트리 셀 스핀박스를 읽음)를 바꾸는 것은 #654 가 아니라 **PR #655** 다 — entry `displayName` JSON 영속(D5), θy/θz 두 각 + `withAngle()` + `eulerAnglesRoundTripAndPole` 테스트 + 행의 θ 입력 셀 삭제(D6), `DashHandleTree` 의 `committed` 프로퍼티·행 제자리 갱신(D9). 머지된 코드에서 세 결함이 어느 경로에 남는지 실측하고, 남으면 각각 PR S 를 연다.
- 완료 기준: 실측 결과 — (1) 이름·θ·범위 각각 정본 위치와 영속 여부 표 (2) 잔존 결함별 후속 항목 또는 "해소" 근거 커밋
- 변경 범위: 조사 대상 `view/DashGeometryParameterWidget.cpp` (`:1148-1200`·`:345`·`:564`·`:2387-2420`) · `controller/DashHandlePickingInteraction.cpp:1978-2000` · `controller/DashHandleDefinition.{h,cpp}` · `controller/DashHandleStateJson.cpp` · `view/common/DashHandleTree.cpp` — 좌표는 모두 **머지 전 기준**이고 #655 에서 이동·삭제된다
- 선행: PR #655
- 충돌: B2 교집합: DashGeometryParameterWidget.cpp → DEV-10 MOR-01 MOR-02 MOR-03 MOR-22 MOR-23 UIC-20 · DashHandlePickingInteraction.cpp → MOR-02 MOR-03 MOR-04 MOR-06 MOR-13 MOR-23 · DashHandleDefinition.cpp → MOR-02 MOR-05 · DashHandleDefinition.h → MOR-02 MOR-05 · DashHandleStateJson.cpp → MOR-02 MOR-05 · PR #654(DashGeometryParameterWidget.cpp·DashHandlePickingInteraction.cpp·DashHandleStateJson.cpp)
- 흡수: MOR-D5 · MOR-D6 · MOR-D9 · MOR-c51, MOR-c52, MOR-c55
- 비고: D6 의 처방은 PR #655 가 세운 구조(direction = Rz(θz)·Ry(θy)·X, 한 칸 편집은 `withAngle()` 로 그 축만, 기즈모 링은 두 각을 함께 바꿀 수 있다)에서 남는 레거시 경로만 대상으로 정한다

### MOR-18 · #281 닫기 — 모핑 축 진입점 이관은 끝났고 잔여는 OPT 측 펌핑 2곳뿐
- 종류: CLOSE | 규모: S | 태그: B, E
- 목표: 닫기 사유 기록. Phase A(dead code)·B1(값 경계)·B2(전용 세션 → 불변 문서)·B3(엔진 격리)·C(QC 코루틴)·E(ModelRunner 코루틴) 전부 dev 에 있고, `MorphingGate`·`WorkerJob`·`morphingSerialPool` 전제는 #408 이 폐기했다. 프리뷰 축(Follow-up ⑴)·DLL `LocalScope`(⑶)·`onDeleteHandles` 재-arm(⑤) 도 해소. 남는 것은 `view/DashOptimizerWidget.cpp:1698`·`:1724` 의 `processEvents` 2곳과 모핑 중 Preview 버튼 사전 비활성 — OPT-04 · OPT-22.
- 완료 기준: 닫기 사유 — 위 Phase 별 근거 좌표(`02-claims/MOR.md` c01~c14) · 잔여를 OPT 로 이관했음을 명시 · RW 경합 계측(⑵)은 EXE
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #281 · 281-1 wiki · MOR-c01~c05, MOR-c07, MOR-c08, MOR-c09, MOR-c11, MOR-c13, MOR-c14, MOR-c77 · MOR-c82 (← EXE-c47)
- 비고: 배정표에서 #281 을 MOR 담당에서 빼고 OPT 접점(`onPreviewButtonClicked` 펌핑)으로 옮기는 것을 제안

### MOR-19 · #427 닫기 — 추적 전용 부모, 격리 몫은 끝났다
- 종류: CLOSE | 규모: S | 태그: E
- 목표: 닫기 사유 기록. 서브 #428·#429 Done, 배치가 화면 상태를 되돌리던 원복 코드는 없다(`DashDoeBatchChain.cpp:230` "No restore", `DashMorphingDoeExecutor` 에 interaction 참조 0). #281 몫(B1·B2) 완결. 남은 서브 #430 은 MOR-15, 렌더러 축 #316·#318·#319 는 REN 항목으로 각자 추적한다.
- 완료 기준: 닫기 사유 + 잔여 서브의 새 항목 ID. 닫기 사유에 (1) 원복 코드가 dev 에 없다는 판정(`controller/DashDoeBatchChain.cpp:230` "generation is immutable. No restore") — PR #655 본문이 "원복 코드 삭제는 #427 마무리 몫" 으로 남긴 항을 이것으로 해소 (2) #430 은 PR #655 머지로 닫힘 (3) 렌더러 액터 소유권 축(#318 · #319)은 REN 항목으로 분리 제안 — 을 적는다
- 변경 범위: -
- 선행: PR #655 (#430 close) · REN-01~REN-10 (#319 → REN-01~04 · #318 → REN-05~10 축의 닫힘 — #316 은 OPT)
- 충돌: -
- 흡수: #427 · MOR-c36, MOR-c37
- 비고: 렌더러 축까지 #427 완료 기준에 묶어 두면 REN 10항목이 끝날 때까지 닫지 못한다 — 그 축을 #427 에서 떼는 제안을 닫기 코멘트에 함께 적는다

### MOR-20 · #332 닫기 — PR #654 가 2번(sampling 치환)을 실행하고 1번(per-handle 반경)을 결정으로 종결했다
- 종류: CLOSE | 규모: S | 태그: E
- 목표: 닫기 사유 기록. `selectHandlesGreedyByUnit`·`wendlandC2`·Eigen include 제거와 `sample_handles` 정책 래퍼(`DashHandleSampling`)는 PR #654 In review. per-handle `SupportRadius` 는 "반경은 Set 전체에 하나, set 안 값은 파생" 으로 결정(#332 1번 종결 댓글). #327(K 클램프)도 같은 PR 이 닫는다.
- 완료 기준: PR #655 머지 확인 후 닫기 — #332 는 "PR 2(interaction 의 핸들 소유 해제, #430) 병합 시 닫는다"(#332 댓글 10-04)이고 그 PR 2 가 #655 다. 머지가 깨지면 c31 을 PR 항목으로 되살린다 · 머지 후 `git grep Eigen -- controller/` 0건
- 변경 범위: -
- 선행: PR #655
- 충돌: -
- 흡수: #332 · #305(MOR 몫 — 죽은 `#include <Eigen/Dense>`) · MOR-c30, MOR-c31, MOR-c32 · MOR-c78 (← ANA-c08)
- 비고: `DashNonDesignUtils.cpp:292` `TODO(#332-2)` 는 PR #654 가 그 함수를 지운다. PR #654 diff 가 `controller/DashHandlePickingInteraction.cpp:2` 의 `#include <Eigen/Dense>`(사용 0, ANA-c08 이관) 도 지운다 — 머지가 깨지면 1줄 PR

### MOR-21 · `DashMorphingController` 의 남은 생성 알고리즘을 프리뷰 액터에서 떼어 자유 함수로 만든다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: PR #654(greedy·automatic·cylinder −396줄) · MOR-05(box) · MOR-06(marching plane) 뒤에도 `DashMorphingController` 는 parametric 선택(`onGenerateCurvatureHandles`·`onGenerateDistanceHandles`)·physics 클러스터(`createCluster`·`readCSVFile`)와 프리뷰 액터 3종(`createPhysicsPreviewForRow`·`visualizeClusterSamples`·marching plane 프리뷰)을 함께 든다. 순수 계산을 `DashNonDesignUtils` 형(싱글턴 0건 자유 함수)으로 떼고 컨트롤러는 입력 수집·프리뷰 표시만 남긴다.
- 완료 기준: (1) 분리된 TU 에 `DashManager::Mgr()`·`vtkActor`·`vtkRenderer` include 0건 (2) 컨트롤러 `DashManager::Mgr()` 16 → 프리뷰 표시 몫만 (3) parametric·physics Generate 결과 무회귀 + 분리 함수 단위 테스트 2건
- 변경 범위: `controller/DashMorphingController.{h,cpp}` · 신설 `controller/DashHandleGenerators.{h,cpp}`(가칭) · `tests/`
- 선행: PR #655 · MOR-06 · MOR-05 (DEC — "Box UI 신설" 로 결정되면 생성기가 하나 늘어 범위를 다시 잰다)
- 충돌: B2 교집합: PR #654(DashMorphingController.cpp·DashMorphingController.h)
- 흡수: Handle-Data-View-Separation "인접 혼합체" · MOR-c76
- 비고: 선행 뒤 잔여 규모를 다시 잰다 — 1,561줄 중 얼마가 남는지에 따라 S 로 줄 수 있다. 직접 renderer 조작 집계도 머지 후 전부 바뀐다(#655 가 Visualizer −476 · Interaction −1,707 · MorphingController −146 · DashGizmo 재작성) — dev 실측은 controller 21곳(MorphingController 11 · Interaction 6 · Visualizer 4) + `libs/DashGizmo/src/DashGizmo.cpp` 10곳이고, 매니저 경유화는 #318 범위 제외 유지라 머지 후 별 S 후보

### MOR-22 · 모핑 설정 JSON 쓰기 3곳을 공용 파일 헬퍼로 옮긴다
- 종류: PR | 규모: S | 태그: A · refactor
- 목표: 세 곳이 각자 들고 있는 파일 입출력을 PER-02 의 `DashSaveSystem` 헬퍼(공용 진입점 — `read/writeJsonFile`, QSaveFile 원자 쓰기 · 길이 검사 · 사유 반환) 호출로 바꾼다 — (a) `setupMorphingTab` 의 `applyRadius` 람다(위젯, `QFile` 직쓰기 RMW `Morphing.radius`, PR #654·#655 무접촉) (b) `DashGeometryParameterWidget::persistHandleSetup()`(PR #654 신설, `QFile` 읽기 → `Morphing.handles/radius` 교체 → 자체 `QSaveFile`) (c) PM `saveMorphingSettings`(PR #654 가 자체 `QSaveFile` + 길이 검사 + `commit()` 로 바꾼 코드). 포맷 불변.
- 완료 기준: (1) 세 함수에 `QFile`·`QSaveFile`·`QJsonDocument::fromJson` 직접 호출 0 (2) 읽기 전용 경로에서 Set·반경 변경이 실패해도 기존 파일 바이트가 같고, 헬퍼가 돌려준 사유가 기존 로그 경로에 남는다 (3) `test_handle_state`(JSON) 무회귀
- 변경 범위: `viewmodel/DashGeometryParameterPresentationModel.cpp` (`saveMorphingSettings` :337-402) · `view/DashGeometryParameterWidget.cpp` (`setupMorphingTab` applyRadius :683-712) · `view/DashGeometryParameterWidgetHandles.cpp` (`persistHandleSetup` — PR #654 신설). 좌표는 머지 후 재측정
- 선행: PER-02 · PR #655 (세 함수 모두 머지 대상 — `Morphing.handles` v1 쓰기 · `e82b7ba` 반경 재구축)
- 충돌: MOR-02 (PM 저장 경로) · MOR-11 (`applyRadius`·`persistHandleSetup` 이 같은 반경을 쓴다 — 소유자가 옮겨가면 이 쓰기도 따라간다, 순서 조율) · B2 교집합: DashGeometryParameterWidget.cpp → DEV-10 MOR-01 MOR-03 MOR-17 MOR-23 UIC-20 · DashGeometryParameterPresentationModel.cpp → MOR-23 · PR #654(DashGeometryParameterPresentationModel.cpp·DashGeometryParameterWidget.cpp·DashGeometryParameterWidgetHandles.cpp)
- 흡수: #479(MOR 몫) · #478(MOR 몫) · #480(MOR 몫 — PER-04 뒤 버전 키 자동) · MOR-c83 (← PER-c22, 3곳)
- 비고: 동작 변경은 넣지 않는다 — 통지는 헬퍼가 돌려준 사유를 기존 로그 경로에 싣는 데까지다. PER-c22 의 세 번째 지점 `model/DashDesignVariableModel.cpp:saveToJsonFiles` 는 공용 모델(호출 CON·DOE·CAD 위젯, MOR 위젯 0)이라 여기 넣지 않는다 — 소속 결정(B2, CON-08 · DOE-10 이 같은 파일) 뒤 그 모듈의 헬퍼 이행 항목으로. `model/DashGeometryParameter.cpp:saveMorphingTarget` 은 이미 QSaveFile(PER-c07)

### MOR-23 · PR #655 머지 후 핸들 데이터·액터 경계의 잔여를 재판정한다
- 종류: INV | 규모: S | 태그: E · refactor
- 목표: PR #655 가 `m_handleGeometry` 와 구 피킹 경로를 지우고 `Finalize` 를 264 → 104줄로 줄였지만 `UpdateSurfaceGeometry:229-530`(302줄)는 무접촉이고 `.h:36` TODO("separate handle data and gizmo functions")도 남는다. 머지된 코드에서 (a) `UpdateSurfaceGeometry` 의 데이터 산출 ↔ 액터 생성 분해가 아직 필요한지 (b) `.h:36` TODO 가 가리키는 분리가 끝났는지 (c) `view/overlay/DashMorphingSettings.cpp:1125`·`:1312` 의 표면 배열 직접 접근 2곳과 view/viewmodel 의 `SetComponent` 직접 쓰기가 남는지 실측하고, 남으면 각각 PR S 를 연다.
- 완료 기준: 실측 결과 — (1) 세 지점의 잔존 여부와 머지 후 좌표 (2) 잔존분의 후속 항목 ID 또는 "해소" 근거 (3) `.h:36` TODO 처분(삭제 또는 후속 항목 번호로 갱신)
- 변경 범위: 조사 대상 `controller/DashHandlePickingInteraction.{h,cpp}` · `view/overlay/DashMorphingSettings.cpp` · `view/DashGeometryParameterWidget.cpp`·`DashGeometryParameterWidgetEditing.cpp` · `viewmodel/DashGeometryParameterPresentationModel.cpp`
- 선행: PR #655
- 충돌: B2 교집합: DashGeometryParameterWidget.cpp → DEV-10 MOR-01 MOR-02 MOR-03 MOR-17 MOR-22 UIC-20 · DashHandlePickingInteraction.cpp → MOR-02 MOR-03 MOR-04 MOR-06 MOR-13 MOR-17 · DashHandlePickingInteraction.h → MOR-02 MOR-03 MOR-04 MOR-06 MOR-07 · DashMorphingSettings.cpp → MOR-05 MOR-12 UIC-22 · DashGeometryParameterPresentationModel.cpp → MOR-22 · PR #654(DashGeometryParameterPresentationModel.cpp·DashGeometryParameterWidget.cpp·DashHandlePickingInteraction.cpp·DashHandlePickingInteraction.h·DashMorphingSettings.cpp)
- 흡수: Handle-Data-View-Separation ⓒ-2·ⓓ·ⓕ · MOR-c70, MOR-c71, MOR-c72, MOR-c74
- 비고: MOR-15(#430 CLOSE) 에서 분리한 잔여. `UpdateSurfaceGeometry` 분해가 필요하다는 결론이면 동작 불변 리팩터 PR 하나로 끝난다

## 대응표

| 원천 | 항목 | 비고 |
|---|---|---|
| #281 | MOR-18 (CLOSE) · MOR-04 | Phase A 의 사문 `applySurfaceExtraction` 은 MOR-04 가 삭제 (MOR-c89) · 잔여 Phase D 펌핑 2곳 → OPT (MOR-c06 → OPT-04 · OPT-22) · Follow-up ⑵ → EXE (MOR-c10) · Follow-up ⑷ → MOR-16 · EXE-c47 이관 (MOR-c82) |
| #512 | MOR-01 | PRJ-c48 · EXE-c23 이관 (MOR-c79 · c86) |
| #563 | MOR-02 · MOR-03 · MOR-04 | 마이그레이션 항은 PR #654 정책으로 기각 (MOR-c23) |
| #577 (보드 밖 OPEN) | MOR-05 (DEC) | cylinder 몫은 PR #654 로 해소 (MOR-c28) · Hexahedron 몫은 MOR-05 의 결정 분기 (MOR-c90) |
| #499 | MOR-05 (DEC) · MOR-06 | #499-1 은 PR #655 가 box 경로를 삭제해 "신설 여부" 결정으로 바뀜. 범프·고립 handle·cylinder·설계 논점은 해소/PR #654 (MOR-c24, c25, c28, c29) |
| #332 | MOR-20 (CLOSE) | 2번은 PR #654 가 구현, 닫기 시점은 PR #655 머지 |
| #430 | MOR-15 (CLOSE) · MOR-23 (INV) | PR #655 가 구현 → CLOSE, 잔여(`UpdateSurfaceGeometry`·`.h:36` TODO·표면 배열 2곳)는 MOR-23. VTP 일원화·테스트 3개·원복 코드는 해소 (MOR-c34, c35, c36) · REN-c31 이관 (MOR-c80) |
| #427 (추적) | MOR-19 (CLOSE) | — |
| #322 | MOR-09 (CLOSE) | PR #655 가 `GizmoGroup` 을 삭제 → 실작업 소멸. 헤더 사본 항은 무효 (MOR-c39) · REN-c31 이관 (MOR-c80) |
| #331 | MOR-07 · MOR-08 · MOR-06 | #331-1·2 의 대상은 PR #655 뒤 `DashGizmo.{h,cpp}` 2파일 · #331-3 은 MOR-06 으로 흡수 — EXT 불요 |
| #557 | MOR-10 (DEC) | — |
| #423 | MOR-11 | 1·2 단계(전수 조사·정책 문서) → PER (MOR-c46) |
| MOR-D1 | 항목 없음 — 해소됨 (#588) | MOR-c47 |
| MOR-D2 | 항목 없음 — 해소됨 (#588) | MOR-c48 · REN-c33 이관 (MOR-c81) |
| MOR-D3 | MOR-12 | — |
| MOR-D4 | MOR-15 (CLOSE) · MOR-23 (INV) | #428 Done 과 PR #655 가 해소, 잔여는 MOR-23 |
| MOR-D5 | MOR-17 (INV) | PR #655 후 재판정 |
| MOR-D6 | MOR-17 (INV) | PER-c05 부록 A (MOR-c87) |
| MOR-D7 | 항목 없음 — 해소됨 (#506 · #587) | MOR-c53 · EXE-c43 이관 (MOR-c85) |
| MOR-D8 | 항목 없음 — 해소됨 (#506) | MOR-c54 · EXE-c43 이관 (MOR-c85) |
| MOR-D9 | MOR-17 (INV) | — |
| MOR-D10 | MOR-02 | = #563 · PER-c05 부록 A (MOR-c87) |
| MOR-D11 | 항목 없음 — 해소됨 (#588) | MOR-c57 · PER-c05 부록 A (MOR-c87) |
| MOR-D12 | 항목 없음 — 해소됨 (#588) | MOR-c58. `DashMainWindow.cpp:4583-4600` 중복 리셋 잔재는 PRJ 참고 |
| MOR-D13 | 항목 없음 — 해소됨 (#607) | MOR-c59 |
| MOR-D14 | 항목 없음 — 해소됨 (#588) | MOR-c60 · UIC-c58 이관 (MOR-c84) |
| MOR-U1 | MOR-13 | — |
| MOR-U2 | MOR-14 (DEC) | — |
| Handle-Data-View-Separation | MOR-15 (CLOSE) · MOR-21 · MOR-23 (INV) | ⓐⓑⓒ-1ⓔⓖ·리터럴·이름 중복·dead 멤버·`filterSelectedHandles`·ThreadingContract 는 해소/무효 (MOR-c63~c69, c73, c75, c88) |
| 281-1 | MOR-18 (CLOSE) | 설계 전제 소멸 (MOR-c77) |
| 접점 #316 #318 #319 | — | REN 소관. MOR 파일 접촉 없음 |
| 접점 #403 (닫힘) | — | Done — MOR-c04 근거 |
| 접점 #305 | MOR-20 | ANA 에서 이관 (ANA-c08 → MOR-c78) — 죽은 Eigen include, PR #654 가 제거 |
| 접점 #455 | MOR-01 | PRJ 에서 이관 (PRJ-c48 → MOR-c79) |
| 접점 #463 | MOR-01 | EXE 에서 이관 (EXE-c23 → MOR-c86) — 규약·헬퍼는 EXE-07 · 09 |
| 접점 #478 · #479 · #480 | MOR-22 | PER 에서 이관 (PER-c22 → MOR-c83) — 이행 대상 3곳, 진입점은 `DashSaveSystem` 헬퍼. `DashDesignVariableModel::saveToJsonFiles` 는 보류 — 소속 결정(B2) 뒤 |

### 범위밖 → 다른 모듈

| CID | 대상 모듈 | 내용 |
|---|---|---|
| MOR-c06 | OPT | `view/DashOptimizerWidget.cpp:1698`·`:1724` `processEvents` 2곳 제거 + 모핑 중 Preview 버튼 사전 비활성 (#281 Phase D 잔여) |
| MOR-c10 | EXE | RW 실행 스레드 점유 경합 계측 (#281 Follow-up ⑵) |
| MOR-c46 | PER | 설정 초기값 전수 조사·정책 문서 (#423 1·2 단계) |

### 선행 순서 (모듈 내)

```
MOR-01 · MOR-10 · MOR-13 · MOR-14 · MOR-16   (독립, #655 머지 전 가능)
MOR-11   (선행 PR #654 — 반경 쓰기 정본 증가)

PR #654 → PR #655 머지
├─ MOR-09 · MOR-15 · MOR-20 (CLOSE — 머지 확인 후 닫기)
├─ MOR-07 → MOR-08          (Gizmo 축 — `DashGizmo.{h,cpp}` 2파일)
├─ MOR-04 → MOR-02 → MOR-03
├─ MOR-05 (DEC) · MOR-06 → MOR-21
├─ MOR-12 · MOR-17 (INV) · MOR-23 (INV)
├─ MOR-19 (CLOSE — REN-01~REN-10 도 선행)
└─ MOR-22 (선행 PER-02)
```
