# REN 작업 목록

> dev @ b08a91b3. 렌더링 매니저·registry 를 만지는 열린 PR 은 없다. 열린 PR 7건 중 머지 대상 6건(#651 #652 #654 #655 #656 #658 — #530 은 재업로드 노선이라 제외) 가운데 REN 과 파일이 겹치는 것은 4건 — #654(#332 — DashMainWindow.cpp · DashManager.cpp · DashMorphingController · DashHandleVisualizer · DashGeometryParameterWidget.cpp) · #655(#430, #654 스택 — DashMainWindow.cpp · DashGeometryParameterWidgetPreview.cpp · DashHandlePickingInteraction.cpp · DashHandleVisualizer.cpp · DashMorphingController.cpp · DashGizmo.cpp · DashMorphingSettings.cpp) · #652(#604 — DashMainWindow.{h,cpp} · DashManager.{h,cpp}) · #651(#616 — DashMainWindow.cpp · DashModelingTreeWidget.cpp). #656 · #658 은 model/preprocessor 쪽이라 접점이 없다.
> #655 는 전부 **충돌**이고 어느 REN 항목의 **선행**도 아니다 — DashMainWindow.cpp 몫은 `handleSubItemSelection` 의 gizmo visibility 1줄 · `initializeMorphingController` · `setupMorphingBar` 이고, `resetMorphingTarget` 의 매니저 경유 해제(REN-04 의 전제)와 `addMorphingPreviewActor` 호출 구조(REN-07·10 의 전제)는 #655 전후가 같다. 단 #654·#655 가 c02 의 직접 조작 21+10 곳을 다시 쓰므로 그 집계는 머지 후 재확인한다.
> 구성 — #319 의 4건(REN-01~04)과 split view 해제(REN-05)는 소유권 모델과 독립인 선행 파일럿. #318 본 구현은 결정(REN-06) → 소유자 태그(REN-07) → 공유 자원 2건(REN-08 · 09) → 인수=숨김(REN-10) 순. #320 은 결정(REN-11) 뒤 구현(REN-12 — 매니저 창구만 전제, 소유자 인자는 REN-07 이 뒤에 와도 된다). Optimizer Preview 전량 삭제(#316 = OPT-01)는 OPT 소관이며 REN-10 의 선행이고, OPT-01 이 `DashRenderingManager.{h,cpp}` 에 전용 preview actor API 를 신설하므로 아래 직렬 규칙에 함께 넣는다.
> 덮어쓰기 지점 재집계 — 이슈의 12곳 전부 현존(Project Assets 삭제 1곳은 #617 에서 조건부로 완화). 이슈가 #406 으로 제외한 `addMorphingPreviewActor` 는 매니저 내부에서 여전히 RESULT·COMPONENT 와 scalar bar 를 지우고 `m_actors[LAYER_MORPHING]` 단일 슬롯을 쓰므로 13곳째로 되살린다(REN-c20). 이 중 OCCT `loadStepFile` 은 별도 씬(CAD), Optimizer Preview 는 #316(OPT-01).
> 매니저 밖 직접 renderer 조작은 controller 21(Visualizer 4 · Picking 6 · MorphingController 11) + DashGizmo 10 + view 3 — #318 범위 제외 절과 같은 집계다(REN-c02, 항목 없음).
> Phase B1 흡수(범위밖 이관, REN-c34~c35): PRJ-c46(#455 View Options processEvents 2곳) → REN-13(신규) · EXE-c41 CON-D2 몫 → 해소됨(항목 없음).

### REN-01 · FE actor 재표시가 카메라를 초기화하지 않게 한다 — 리셋은 최초 표시와 사용자 조작에서만
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

### REN-02 · Start Morphing 이 숨긴 FE actor 의 복원 경로를 만든다
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

### REN-03 · Model Runner Preview 가 FE actor 를 결과 위에 남기지 않게 한다 — 삭제가 아니라 숨김
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

### REN-04 · Geometry actor 의 등록·해제를 매니저 창구로 통일하고 중복 등록을 막는다
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

### REN-05 · 씬을 새로 그리는 모든 매니저 경로가 split view 를 먼저 해제하게 한다
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

### REN-06 · 소유자 식별 형태와 문서형 명시 해제 시점을 확정한다
- 종류: DEC | 규모: S | 태그: E, A · refactor
- 목표: #318 "해법 방향 — 2026-09-21 확정" 과 "범위에서 제외" 절이 이미 답한 것(콘텐츠 부류표 = 문서형 Project Assets `.vtk/.vtu` BASE · FE displayed actor / 작업물형 Launcher preview · Model Runner 결과 · Optimizer preview · Morphing preview · CON highlight, 모듈 이탈 시 작업물형 폐기, 공유 자원 카메라·scalar bar·cube axes·`SetDraw` 는 매니저 중재, 핸들·피킹·DashGizmo 등 모듈 수명 표시물은 "존재 등록만")은 재결정하지 않는다. 남은 2개만 답한다 — (a) 소유자 식별 형태: enum 신설 vs 모듈 ID 문자열(`DashModuleName` 재사용), 문서형 소유자를 모듈과 같은 축에 둘지 (c) 문서형 명시 해제 시점과 API 형태: `DashProjectManager::CloseProject`(registry.clear 자리) · Project Assets 삭제 외에 지점이 더 필요한지, 일괄 `releaseDocuments()` 인지 단건 `releaseDocument(path)` 인지(#318 완료 조건 5).
- 완료 기준: 결정 기록 — 2개 질문의 답 + REN-07 · REN-10 의 설계 입력(소유자 타입의 정의 위치 · 해제 API 시그니처)
- 변경 범위: 문서만
- 선행: -
- 충돌: -
- 흡수: #318 해법 방향(미결 2문항) · 완료 조건 5 · REN-c04 (해제 시점)
- 비고: 종전 6문항 중 (b)(d)(e)(f) 는 #318 본문에 답이 있어 제외했다 — 결정 대기로 둘 이유가 없다(검토 #13). 메모리 검토는 이슈 본문 그대로 유효(`SetInputData` 참조 공유). `TopOptPostprocessDialog` 는 자체 `DashRenderingManager` 인스턴스 — API 변경의 컴파일 영향만 받는다.

### REN-07 · 레이어·actor 에 소유자 태그를 붙이고 "지금 누가 그렸는지" 질의 API 를 둔다
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

### REN-08 · base actor 의 ghost 외형을 매니저가 저장·복원한다
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

### REN-09 · scalar bar · cube axes 의 생성·해제를 매니저 단일 경로로 모은다
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

### REN-10 · 다른 모듈의 씬 인수를 "파괴" 에서 "숨김 + 작업물 폐기" 로 바꾼다
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

### REN-11 · 복수 .vtk/.vtu 동시 표시 요구를 확정한다
- 종류: DEC | 규모: S | 태그: D
- 목표: Modeling Tree 의 `.vtu/.vtk` 토글이 (b) 파일별 actor 복수 동시 표시(매니저 창구 경유) 인지 (c) 단일 표시 유지 + 복수 표시를 전제한 코드 정리 인지 결정한다. BASE 슬롯은 1개이고 트리는 `.vtk/.vtu` 를 `vtk_parent` + 자식 `vtk_single` 1개로만 만든다 — 결정 대상은 "`vtk_parent` 행 여러 개를 동시에 표시할 것인가" 다. (a) `m_vtuVtkActors` 에 채워 renderer 직접 추가는 #318 이 금지.
- 완료 기준: 결정 기록 — 요구 + REN-12 의 범위(M 또는 S)
- 변경 범위: 문서만
- 선행: -
- 충돌: -
- 흡수: #320 to-be 4 · not-to-be · REN-c29
- 비고: 현재 코드는 복수 표시를 전제로 쓰여 있으나 BASE 슬롯 1개라 성립하지 않는다. `vtm_parent` 는 행 생성 코드가 없어(`git grep vtm_parent` = `DashMainWindow.cpp:3722` `:3730` 뿐) 결정 대상이 아니다 — 죽은 분기 삭제는 결정과 무관하게 REN-12 범위. REN-06 선행 불필요 — (a) 금지는 #318 이 이미 못박았다(검토 #11).

### REN-12 · Modeling Tree 의 .vtk/.vtu 표시 토글을 매니저 창구로 구현한다
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

### REN-13 · View Options 토글 람다의 `processEvents` 를 없애고 레이아웃 갱신을 Qt 에 맡긴다
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

## 선행 순서

- 독립 착수 가능: REN-01 · REN-02 · REN-04 · REN-05 · REN-06 · REN-08 · REN-09 · REN-11 · REN-13 · (REN-03 은 REN-02 뒤)
- REN-06 → REN-07 → REN-10 (+ REN-08 · REN-02 · REN-03 · REN-05 · OPT-01)
- REN-11 → REN-12 (REN-07 은 선행 아님 — 뒤에 오면 소유자 인자만 더한다)
- 같은 파일 동시 수술 금지 ① `DashRenderingManager.{h,cpp}`: OPT-01 · REN-05 · 07 · 08 · 09 · 10 · 12 를 직렬로 한다. OPT-01 이 전용 preview actor API 를 신설하므로(`addMorphingPreviewActor` 재사용 불가 — RESULT·COMPONENT 레이어와 scalar bar 를 파괴하고 저장 슬롯이 `m_actors[LAYER_MORPHING]` 단일) 이 파일에 들어오고, REN-10 이 OPT-01 을 선행으로 두므로 사슬에서 OPT-01 이 REN-10 보다 앞이다 — 기존 선행 관계와 모순 없음. REN-07 과 OPT-01 은 순서 자유이고 뒤에 오는 쪽이 소유자 인자를 맞춘다.
- 같은 파일 동시 수술 금지 ② `DashMainWindow.{h,cpp}`: REN-02 · 04 · 07 · 10 · 12 는 열린 PR #654 #655 #652 #651 랜딩 뒤

## 대응표

| 원천 | 항목 | 비고 |
|---|---|---|
| #318 | REN-06 · REN-07 · REN-08 · REN-09 · REN-10 · REN-05 | 완료 조건 1→REN-07, 2→REN-05, 3→REN-10, 4→REN-08, 5→REN-06+REN-10. 범위 제외 절(직접 조작 controller 21 + DashGizmo 10 + view 3 · OCCT · Optimizer 전량 삭제)은 항목 없음 — 아래 c02 · c17 · c19 |
| #319 | REN-01 · REN-02 · REN-03 · REN-04 | 4건 분리, 전부 유효 |
| #319-1 | REN-02 | |
| #319-2 | REN-01 | 호출처 4→7 |
| #319-3 | REN-03 | |
| #319-4 | REN-04 | 부분 해소(#332) — 직접 호출 1곳 잔존 |
| #320 | REN-11 · REN-12 | 이슈 시점과 동일하게 미구현. to-be 4 의 `vtm_parent` 는 행 생성 코드가 없어 결정 대상이 "복수 `vtk_parent` 동시 표시" 로 좁혀진다 |
| #316 (접점) | 범위밖 → OPT | REN-10 의 선행. 지점은 REN-c19 |
| #322 (접점) | 범위밖 → MOR | 렌더링 매니저 접점 없음 (REN-c31) |
| #430 (접점) | 범위밖 → MOR | 렌더링 매니저 접점 없음 (REN-c31) |
| OPT-D18 | 범위밖 → OPT | #316 과 동일 지점 (REN-c32) |
| MOR-D2 · RUN-D14 · RUN-D25 | 범위밖 → MOR · RUN | 매니저 API 결함 아님 (REN-c33) |
| REN-c02 | 항목 없음 | #318 범위 제외 유지. 재집계로 이슈 집계와 일치 — controller 21(Visualizer 4 · Picking 6 · MorphingController 11) + DashGizmo 10 + view 3. MOR 후속 후보이고 PR #654·#655 머지 후 재확인 |
| REN-c07 | REN-08 (비고) | MOR 소유 actor 외형 — 접점 협의 |
| REN-c17 | 범위밖 → CAD | OCCT 별도 씬, 소유권 모델 대상 아님 |
| #455 REN 몫 (PRJ-c46 이관) | REN-13 | DashViewOptionsWidget 토글 람다 processEvents 2곳 (REN-c34) — PRJ-c46 의 `onColorBarChanged` 좌표는 오기 |
| CON-D2 (EXE-c41 이관) | 항목 없음 | 해소됨 — f14c5831(#559) · d8be33a4(#564), `Registry::load` 뮤텍스 + in-flight 대기 (REN-c35) |

CID 전수 — c01 REN-07 · c02 없음 · c03 REN-07 · c04 REN-06/10 · c05 REN-09 (정책 부분은 #318 해법 방향이 이미 확정) · c06 REN-08 · c07 REN-08(비고) · c08 REN-07/12 · c09 REN-07 · c10 REN-07/12 · c11 REN-01 · c12 REN-10 · c13 REN-10 · c14 REN-02/10 · c15 REN-07/10 · c16 REN-03/05/10 · c17 CAD · c18 REN-05 · c19 OPT · c20 REN-10 · c21 REN-02 · c22 REN-01 · c23 REN-03 · c24 REN-04 · c25 REN-04 · c26~c28 REN-12 · c29 REN-11 · c30 OPT · c31 MOR · c32 OPT · c33 MOR/RUN · c34 REN-13 · c35 없음(해소됨)
