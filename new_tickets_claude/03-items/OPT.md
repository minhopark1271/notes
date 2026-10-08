# OPT 작업 목록

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> 기준: dev @ b08a91b3. 원천·판정은 02-claims/OPT.md. 담당 이슈 #316·#457 은 Backlog.
> 열린 PR 7건 중 머지 대상 6건(#651 #652 #654 #655 #656 #658) — #530 은 재업로드 노선이라 대기 대상이 아니다(decisions ⑩). OPT 항목과 파일이 겹치는 것은 셋뿐이다: `tests/CMakeLists.txt`(#651 #652 #654 #655 → OPT-20) · `view/DashMainWindow.cpp`(#651 #652 #654 #655 → OPT-22) · `model/DashOptimizer.cpp`(#654 → M 을 고치는 전 항목). **#656 · #658 은 OPT 교집합 0** — 런처·preprocessor·Rw 계열만 고친다(open_prs.md 재갱신본) → 선행·충돌 등재 없음.
> #530의 OPT 수정 지점은 OPT-26(#685)의 현행 참조·출처 계약으로 다시 작성한다. 당시 hunk 이식 결정은 기록으로 보존하며 조합 핀은 복원하지 않는다.
> 번호: **OPT-03 · OPT-04 는 결번** — 둘 다 OPT-26 으로 흡수(2026-10-06, 검토 #3·#4·#5). 사유는 OPT-26 비고.
> 파일 약칭: W = view/DashOptimizerWidget.cpp · Wh = view/DashOptimizerWidget.h · M = model/DashOptimizer.cpp · Mh = model/DashOptimizer.h · PM = viewmodel/DashOptimizerPresentationModel.cpp/.h

### OPT-01 · Render Preview 를 비파괴 오버레이로 바꾼다 — 산출 .vtu 를 preview actor 로 겹치고 registry·BASE 레이어·카메라를 건드리지 않는다
- 종류: PR | 규모: M | 태그: A, E · bug
- 목표: 프리뷰 격자를 `performMorphing` 이 쓴 `Preview_*.vtu` 에서 읽어 전용 preview actor(반투명) 로 기존 씬 위에 겹친다. `removeAnalysisModelActor`·`GetActors()` 전량 제거·`clearLayer` 3종·`setDisplayedContext`·`updateAllGeometry`·무조건 `resetCamera` 를 없앤다. 등록·해제는 `DashRenderingManager` 의 preview actor API 를 거치고, `displayedContextChanged`(다음 Load) 와 재프리뷰에서 이전 actor 를 해제한다. `.vtu` 삭제 코드와 `performMorphing` 의 `_input_geometry.vtu` 추출(14단계) 을 제거한다.
- 완료 기준: (1) Preview 뒤 `registry.displayedFilePath()` · Modeling Tree · Mesh View 제목 불변 (2) 타 모듈 actor(핸들 5종 · FE 조건 하이라이트) 가 renderer 에 남고 `hasFeConditionHighlight()` 가 실제 상태와 일치 (3) 씬에 geometry 가 있으면 카메라 유지, 비어 있으면 리셋 (4) 다음 Load 또는 재프리뷰에서 이전 preview actor 해제 (5) `Preview_*.vtu` 가 남고 `_input_geometry.vtu` 는 생성되지 않음
- 변경 범위: W, Wh (preview actor 멤버 · 해제 슬롯), M (`performMorphing` 14단계 제거), controller/DashRenderingManager.h · controller/DashRenderingManager.cpp (전용 `add/removePreviewActor` 신설 — 레이어·scalar bar 미파괴 · `LAYER_MORPHING` 과 별도 슬롯)
- 선행: -
- 충돌: OPT-26 · OPT-21 (W 같은 함수·파일) · REN-07 (#318 소유자 태그 API 가 먼저 오면 등록 API 교체) · REN-05 · REN-08 · REN-09 · REN-10 · REN-12 (DashRenderingManager — REN 이 선언한 직렬 사슬) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashRenderingManager.cpp → 공유 10건(deps.md 5절) · DashOptimizerWidget.h → OPT-05 OPT-06 OPT-13 OPT-18 OPT-22 PRJ-25 UIC-22 · DashRenderingManager.h → PRJ-04 · PR #654(DashOptimizer.cpp)
- 흡수: #316 · OPT-D17 · OPT-D18 · #318(부류 3 ⑫) · OPT-c01, c02, c03, c04, c06, c07, c27 · OPT-c43, c44, c45 (← REN-c19, REN-c30, REN-c32)
- 비고: 기존 `addMorphingPreviewActor` 재사용은 불가다 — RESULT·COMPONENT 레이어와 scalar bar 를 지우고(controller/DashRenderingManager.cpp:1288-1293, 완료 기준 (2) 와 정면 충돌) 저장 슬롯이 `m_actors[LAYER_MORPHING]` 단일이라 Morphing Settings 프리뷰와 자리를 다툰다. 그래서 전용 API 신설을 변경 범위에 무조건 올렸다 (검토 #9). REN-10 이 OPT-01 을 선행으로 두므로(03-items/REN.md REN-10 선행) DashRenderingManager 직렬 사슬에서 OPT-01 이 REN-10 보다 앞에 온다 — REN 의 직렬 규칙 목록(REN-05·07·08·09·10·12)에 OPT-01 을 넣는 것은 `보류: REN 몫`. 소유자 태그·질의는 #318 몫 — 여기서는 태그 없이 성립. #315(Load 재클릭 게이트) 의 선행.

### OPT-02 · 프리뷰 산출물의 위치·이름·수명을 정한다
- 종류: DEC | 규모: S | 태그: A, C
- 목표: `Preview_{col}_{template}_{ts}.dat/.inp` · `Preview_{col}_{ts}.stp`(·`.vtu`) 가 사용자 루트 `Optimizer_{Set}/` 에 타임스탬프로 누적되고 프로젝트 파일 트리에 `Load` 버튼까지 붙는 현행에 대해 (a) `.dproj` 내부로 이동(트리 비노출) (b) `Optimizer_{Set}/preview/` 하위 + 트리 필터 (c) 현행 위치 유지 + 재프리뷰 시 이전 파일 삭제 — 중 하나를 기록한다. #653 FE Validation 이 "그 Set 의 입력 파일" 로 무엇을 집을지(Preview_*.inp 인지 별도 생성 버튼 산출물인지) 를 함께 정한다.
- 완료 기준: 결정 기록 — 위치 · 이름 규칙 · 보존 개수 · 트리 노출 여부 · #653 의 입력 파일 정의
- 변경 범위: - (결정 후 PR: W, M `performMorphing` 출력 경로)
- 선행: -
- 충돌: B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · PR #654(DashOptimizer.cpp)
- 흡수: #316(산출물 위치) · OPT-c05
- 비고: 트리 Load 버튼은 확장자 규칙(view/delegate/ProjectFileTreeDelegate.cpp:46) 이라 파일이 보이는 한 붙는다. (a) 면 `getModuleDir` 의 내부/외부 분기(controller/DashIOController.cpp:31-36) 에 예외가 생긴다 — PER 접점.

### OPT-05 · 최적화 Job 의 시작·실패·완료를 위젯에 결선한다
- 종류: PR | 규모: S | 태그: B, D · bug
- 목표: `DashOptimizer` 가 실행 상태 변화(시작·종료) 를 시그널로 내고 위젯이 Run 버튼을 잠그고 푼다. `optimizationFailed` 를 위젯에 연결해 사유를 `DashNotify::error` 로 띄운다.
- 완료 기준: (1) 실행 중 Run 비활성 + 상태 텍스트, 종료 시 복원 (2) exe 비정상 종료 · 구속 연산자 누락 · ProjectManager/IOController 부재 세 경로 모두 사용자에게 사유 표시 (3) `m_currentJob` 가드의 "already running" 경로가 수동으로 도달 불가
- 변경 범위: M, Mh, W, Wh
- 선행: -
- 충돌: OPT-06 · OPT-17 · OPT-18 (setModel 연결 블록 · 모델 시그널 블록) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashOptimizerWidget.h → OPT-01 OPT-13 OPT-21 OPT-22 PRJ-25 UIC-22 · DashOptimizer.h → OPT-07 OPT-15 OPT-16 OPT-23 OPT-26 · PR #654(DashOptimizer.cpp)
- 흡수: OPT-D11 · OPT-D13 · #463(OPT 몫 — Run) · OPT-c21, c23 · OPT-c48, c50, c51 (← UIC-c55, EXE-c44, EXE-c23)
- 비고: Set 전환 중 상태는 setModel 재바인딩에서 재계산 — LGE fit 버튼 선례(W:187-191). 성공 통지의 모달 2개(QMessageBox + `QDialog::exec`) 정비는 UIC 통지 표준 몫. 진행 표시·재클릭 가드 형식은 EXE-07 규약·EXE-09 헬퍼를 따른다 — #463 확산의 OPT 몫(Run 버튼). Preview 버튼은 OPT-22.

### OPT-06 · DV Fixed · Init. Value · 목적 방향 편집을 모델에 즉시 반영한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: Fixed 체크 → `updateDesignVariableOptimizeFlags`, Init. Value 스핀/콤보 → `updateDesignVariableValues`, Minimize/Maximize 콤보 → `updateObjectiveFunction` 을 편집 시점에 호출한다. Run 의 강제 동기화는 그대로 둔다 (셀 편집 중 Run 대비).
- 완료 기준: (1) 세 값을 바꾸고 Run 없이 Set 전환 후 복귀하면 모델 값 유지 (2) LGE 피팅 결과가 위젯 쓰기 → 시그널로 `m_designVariables` 에 도달 (3) populate 중 재진입 없음 (`m_isPopulating` / blockSignals)
- 변경 범위: W, Wh
- 선행: -
- 충돌: OPT-05 · OPT-09 · OPT-12 · OPT-13 (W) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizerWidget.h → OPT-01 OPT-18 OPT-21 OPT-22 PRJ-25 UIC-22
- 흡수: OPT-D6 · OPT-D7 · OPT-D22 · OPT-c16, c17, c34
- 비고: 행 단위 setter 가 없어 벡터 전체를 다시 읽어 넘긴다 — `readConstraintsFromTable` 선례. 파일 영속화 시점은 OPT-07.

### OPT-07 · Run 이외의 저장 시점을 둔다 — Set 이탈과 프로젝트 저장에서 saveSettings
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `setModel` 교체로 Set 을 떠날 때와 프로젝트 저장 시 `saveSettings()` 를 부른다. 포맷 불변.
- 완료 기준: (1) 설정 편집 → Run 없이 Set 전환 → 재시작 후 복원 (2) 편집하지 않은 Set 의 JSON 은 재기록되지 않음 (dirty 플래그) (3) 저장 실패 시 로그
- 변경 범위: M, Mh, W
- 선행: OPT-06
- 충돌: OPT-15 (saveSettings) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashOptimizer.h → OPT-05 OPT-16 OPT-18 OPT-23 OPT-26 · PR #654(DashOptimizer.cpp)
- 흡수: OPT-D12 · OPT-c22
- 비고: 프로젝트 저장 훅은 PRJ(DashProject 저장 경로) 접점 — 다른 모듈 Set 의 저장 호출 선례를 따른다. 대안 "편집 즉시 저장" 은 되돌리기가 없어 채택하지 않는다.

### OPT-08 · 응답·설계변수 심볼의 정본을 모델 하나로 통일한다
- 종류: PR | 규모: S | 태그: C, A · bug
- 목표: 표시 심볼을 `info.symbol` 에서 읽고(행 인덱스 재생성 제거), 설정 JSON 복원 시 심볼은 응답·파라미터 이름에 붙은 값을 쓰며, 이름 집합이 바뀌면 새 항목만 다음 번호를 받고 기존 번호는 유지한다. 목적·구속 수식에 존재하지 않는 심볼이 있으면 경고.
- 완료 기준: (1) 응답 1개 추가·삭제 후 기존 `r{n}` 매핑 불변 (2) 수식 토큰이 없는 심볼이면 populate 시 경고 (3) 저장 JSON 의 symbol 과 표시가 동일
- 변경 범위: M, W
- 선행: -
- 충돌: OPT-14 · OPT-16 (loader) · OPT-20 · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · PR #654(DashOptimizer.cpp)
- 흡수: OPT-D24 · OPT-c28
- 비고: 대안 "재채번 + 수식 자동 치환" 은 DashOptiDeepOpt 가 symbol 을 키로 쓰므로 불리. Analysis Launcher 의 PRE-D26(`v{n}`) 과 같은 기제 — 결정을 공유한다.

### OPT-09 · ModelBuilder 폴더 변경 시 설정 UI 와 모드를 함께 갱신한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `onModelBuilderFolderChanged` 가 `populateAllWidgets` 와 같은 순서(두 표 → 모드 색인 → `populateOptimizationSettings` → `onOptimizationModeChanged`) 를 밟도록 공통 재구성 함수로 묶는다.
- 완료 기준: (1) 폴더 전환 후 수식·구속·방법·모드가 새 폴더 기준 (2) 재진입 없음
- 변경 범위: W
- 선행: -
- 충돌: OPT-06 · OPT-13 · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절)
- 흡수: OPT-D3 · OPT-c13

### OPT-10 · 대리모델 표의 1D/ND 지표 열을 행 단위로 정한다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: 첫 행 판정으로 표 전체 열을 여닫지 않는다. 1D·ND 행이 섞이면 양쪽 열을 모두 보이고 해당 없는 칸은 "-". `(Field)` 판정은 새 복사본을 만들지 않고 RUN-15 가 `DashSurrogateModelCommon` 에 정본화하는 응답 표시 이름 술어를 호출해 쓴다 — 정본은 학습 시점에 model_info 에 기록된 응답 속성이다.
- 완료 기준: (1) 1D+ND 혼합 model_info 에서 두 행의 지표가 모두 보임 (2) 단일 종류일 때 현행과 같은 열 집합 (3) W 에 `contains("(Field)")` 직접 판정 0건 · 괄호 제거 인라인 0건 — 전부 공용 술어·`strippedResponseName` 호출
- 변경 범위: W (`onSurrogateModelUpdated` :556 · `populateSurrogateTable` :867 — `(Field)` 직접 판정 2곳), PM (행 단위 열 집합 산출)
- 선행: RUN-15 (공용 `(Field)` 술어 정본화 — 같은 PR 이 RUN 전용 `view/common/SurrogateTableController.cpp` 도 함께 거둔다)
- 충돌: OPT-20 · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizerPresentationModel.cpp → OPT-12 OPT-14 OPT-15
- 흡수: OPT-D4 · OPT-c14
- 비고: ⑦ RUN-15 ↔ OPT-10 **확정** — 변경 파일 수 RUN-15 4(RunnerWidget · SurrogateTableController · DashSurrogateModelCommon · RUN PM) 대 OPT-10 2(W · PM) 로 **RUN-15 가 공용 술어·컨트롤러를 맡고 OPT-10 이 선행 소비자**다. `SurrogateTableController` 는 공용이 아니라 RUN 전용(소비자 `DashModelRunnerWidget`·`DashModelRunnerMCUWidget` 2곳)이라 파일 교집합이 없고 충돌이 아니다 — RUN-15 쪽 보강은 반영 완료(03-items/RUN.md RUN-15 완료 기준 (1)·변경 범위). 정본이 응답 속성인 코드 근거(접점 BLD): Model Builder 가 `(Field)` 를 `baseDim == 3 && reduction == "None"` 에서 붙이고(`viewmodel/DashModelBuilderPresentationModel.cpp:responseDisplayText` :174-178) 같은 술어가 `effectiveModelDimension`(:188) 의 `isND` 이며, 그 표시 이름이 `getOutputResponseList`(`view/DashModelBuilderWidgetBase.cpp:299`) 를 거쳐 model_info 로 간다 — 즉 model_info 의 `(Field)` 는 학습 시점 ND 결정이고 모델 이름 접두(`isNDModel`) 가 아니다. `(Field)` 판정은 전체 6곳(+생산 1) 이고 OPT 몫은 2곳. :558-561 의 괄호 제거 인라인도 이미 있는 공용 `DashSurrogateModelCommon::strippedResponseName`(.h:34) 과 같은 규칙이라 함께 호출로 바꾼다. BLD 2곳(`DashModelBuilderWidget.cpp:1089`·`:1681`)은 대응 항목이 없어 범위 밖.

### OPT-11 · 최적화 모드 2차 판정을 양방향 재평가로 바꾼다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `loadDesignVariables` 의 색인 승격을 "model_info 1차 판정 OR 설정 JSON mean/std 존재" 의 재계산으로 바꿔 둘 다 없으면 0 으로 내린다.
- 완료 기준: (1) JSON 의 mean/std 가 제거되고 model_info 도 결정론이면 색인 0 (2) 기존 승격 케이스 동일
- 변경 범위: M
- 선행: -
- 충돌: OPT-16 · B2 교집합: DashOptimizer.cpp → 공유 17건(deps.md 5절) · PR #654(DashOptimizer.cpp)
- 흡수: OPT-D5 · OPT-c15
- 비고: 사용자 모드 선택(U1) 은 예정 기능 — 제외 유지.

### OPT-12 · [+] 구속 행을 placeholder 로 심고 편집 확정 전엔 모델에 넣지 않는다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: 새 행은 회색 예시로 두고 `collectConstraintRows` 가 placeholder 행을 건너뛴다. 편집 확정(`itemChanged`) 시 보통 아이템으로 승격. 초기 회색 예시 행 0(`"r1 <= 163.23"`, `configureOptimizationSettingsGroup`) 도 같은 placeholder 규칙을 탄다 — 샘플 값이 저장 설정에 들어가지 않는다.
- 완료 기준: (1) [+] 후 편집 없이 Run → 구속 수 불변 · 초기 예시 행 0 도 수집되지 않음 (2) 편집 확정 후 모델에 1건 추가 (3) placeholder 행(초기 행 포함)이 저장 JSON 에 없음
- 변경 범위: W, PM
- 선행: -
- 충돌: OPT-06 · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizerPresentationModel.cpp → OPT-10 OPT-14 OPT-15
- 흡수: OPT-D8 · #483(OPT 샘플 행 몫) · OPT-c18 · OPT-c49 (← DEV-c30)

### OPT-13 · 방법 옵션 기본값 주입을 사용자 변경 시에만 한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `onMethodSelectionChanged` 는 라벨·가시성만 바꾼다. 기본값은 사용자가 콤보를 바꿨고 그 방법의 편집값이 없을 때만 넣는다. 복원은 호출 순서에 의존하지 않는다.
- 완료 기준: (1) iteration 500 → 방법 변경 → 되돌림 → 500 유지(세션 내) (2) 저장값 복원이 `populateOptimizationSettings` 의 호출 순서와 무관 (3) 처음 고른 방법은 기본값 표시
- 변경 범위: W, Wh
- 선행: -
- 충돌: OPT-06 · OPT-09 · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizerWidget.h → OPT-01 OPT-05 OPT-18 OPT-21 OPT-22 PRJ-25 UIC-22
- 흡수: OPT-D10 · OPT-c20
- 비고: 방법별 편집값을 위젯이 맵으로 들면 "되돌림 유지" 가 성립. 모델 `m_methodOptions` 는 현재 방법 1벌만 — 그대로 둔다.

### OPT-14 · 검증 표 헤더 분류를 모델이 아는 심볼·이름 대조로 바꾼다
- 종류: PR | 규모: S | 태그: C · bug
- 목표: `classifyValidationHeaders` 가 `startsWith("r")` 규칙 대신 호출자가 넘긴 응답 심볼 집합·설계변수 이름 집합으로 분류한다. objective/constraint/id 규칙은 유지.
- 완료 기준: (1) `r2_thickness` 설계변수가 DV 표로 (2) 기존 optimum.json 의 분류 결과 동일 (3) PM 단위 테스트
- 변경 범위: PM, W
- 선행: OPT-08
- 충돌: OPT-20 · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizerPresentationModel.cpp → OPT-10 OPT-12 OPT-15
- 흡수: OPT-D14 · OPT-c24

### OPT-15 · ModelBuilder Set 선택을 setId 로 보유하고 설정 JSON 에 왕복한다
- 종류: PR | 규모: S | 태그: A, C · bug
- 목표: OPT-26(#685)의 Builder setId 저장·복원 계약에 따라 기존 선택·저장 경로를 연결한다. 이름은 표시용으로만 쓰고 실행 시 #520 역조회로 실제 경로를 얻는다. 현재 Optimizer ID를 유지하면서 다른 유효 Builder 참조로 변경할 수 있다.
- 완료 기준: 선택·저장·재시작 후 동일 Builder setId 복원. 개명 후 같은 Set을 해석하고 삭제·동명 재생성은 다른 Set으로 판정한다. 참조나 필수 출처를 해석할 수 없으면 명시적 재선택·재생성 안내를 내며 이름/폴더 우선순위로 자동 대체하지 않는다.
- 변경 범위: M, Mh, W, PM (`selectModelBuilderFolder`)
- 선행: OPT-26
- 충돌: OPT-07 · OPT-23 · OPT-24 (saveSettings) · OPT-16 (로더) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashOptimizer.h → OPT-05 OPT-18 OPT-26 · DashOptimizerPresentationModel.cpp → OPT-10 OPT-12 OPT-14 · PR #654(DashOptimizer.cpp)
- 흡수: OPT-D21 · #443 SI-6a ②(OPT 몫) · OPT-c33 · OPT-c53 (← PRJ-c04)
- 비고: OPT-26과 별도 ID 저장 체계를 만들지 않는다. PRJ-18 개명 오류 수정과 공유 경로 적용 순서만 조율하며 #685를 #681 머지 조건으로 두지 않는다.

### OPT-16 · model_info.json 로더 3곳을 정화 규칙 1벌의 리더로 통합한다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: M 의 인라인 정화 복제 2곳(`loadModelInfoFromFolder` :757-764 · `loadModelInfoJson` :1302-1309)과 무정화 경로 1곳(`loadAllData` :572)이 공용 `DashSurrogateModelCommon::sanitizedModelInfoJson` 을 쓰는 읽기 함수 하나를 지난다. 진입 시 설정 JSON 재독은 1회로.
- 완료 기준: (1) NaN 포함 model_info.json 이 세 경로 모두에서 같은 문서로 파싱 (2) 기존 수치 동일 (3) 리더 단위 테스트
- 변경 범위: M, Mh
- 선행: -
- 충돌: OPT-08 · OPT-11 · OPT-15 (모델 로더) · OPT-26 (M 로더) · OPT-20 · B2 교집합: DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashOptimizer.h → OPT-05 OPT-07 OPT-18 OPT-23 · PR #654(DashOptimizer.cpp)
- 흡수: OPT-D1 · OPT-c11
- 비고: PM `sanitizedModelInfoJson` 은 이미 공용 함수로 포워딩하므로 정리 대상이 아니다 — 변경 범위에서 PM 을 뺐다 (검토 #10). 공용 함수 본문은 그대로 둔다.

### OPT-17 · setModel(nullptr) 이 표를 비우고 위젯을 비활성으로 둔다
- 종류: PR | 규모: S | 태그: A, D · bug
- 목표: 모델이 null 이면 세 탭의 표·수식·콤보를 clear 하고 `setEnabled(false)` 로 끝난다.
- 완료 기준: (1) Set 삭제 후 화면이 비고 Run 비활성 (2) 다른 Set 선택 시 정상 복귀
- 변경 범위: W
- 선행: -
- 충돌: OPT-05 (setModel) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절)
- 흡수: OPT-D2 · OPT-c12 · OPT-c42 (← PRJ-c58)

### OPT-18 · 도달하지 않는 선언 4종과 로그 전용 showEvent 를 지운다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `m_resultCsvPath` · `predictBtn` · `m_soraLabel`(생성·숨김 코드 포함) · `settingsSaved` 와 `showEvent` 오버라이드 제거.
- 완료 기준: (1) 심볼 4종 참조 0 (2) 빌드·동작 불변
- 변경 범위: W, Wh, M, Mh
- 선행: -
- 충돌: OPT-05 (모델 시그널 블록) · OPT-07 (`settingsSaved` 에 수신처가 생기면 제외) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashOptimizerWidget.h → OPT-01 OPT-06 OPT-13 OPT-21 OPT-22 PRJ-25 UIC-22 · DashOptimizer.h → OPT-15 OPT-16 OPT-23 OPT-26 · PR #654(DashOptimizer.cpp)
- 흡수: OPT-U2 · OPT-D9(잔재) · OPT-c19, c31

### OPT-19 · LGE 피팅의 학습 모델 경로를 IOController 를 거쳐 만든다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `runFitVariables` 가 `getModuleDir(ModelBuilder, <상수>)` 를 쓰고 Set 이름 상수는 `LGE_SpringRule.h` 에 둔다.
- 완료 기준: (1) 경로 문자열 조립 0건 (2) LGE 빌드에서 피팅 동작 불변
- 변경 범위: M, model/extensions/enterprise/LGE_SpringRule.h
- 선행: -
- 충돌: B2 교집합: DashOptimizer.cpp → 공유 17건(deps.md 5절) · LGE_SpringRule.h → PRE-11 PRE-16 · PR #654(DashOptimizer.cpp)
- 흡수: OPT-D23 · OPT-c35
- 비고: `DASH_BUILD_LGE_COMPSPRING` 빌드에서만 컴파일 — CI 에 그 빌드가 없으면 수동 확인 (DEV 접점).

### OPT-20 · Optimizer 단위 테스트 타깃을 만든다 — PM 변환 함수와 설정 JSON 왕복
- 종류: PR | 규모: M | 태그: F · refactor
- 목표: `tests/TestOptimizerPresentationModel.cpp`(methodCatalog · defaultOption · buildMethodOptions · classifyValidationHeaders · parseDvSource/resolveGeometrySource · findGeometryParameterJsonPath · sanitizedModelInfoJson · constraintsFromRows) 와 `tests/TestOptimizerSettings.cpp`(saveSettings/load* 왕복 · NaN "None" · 레거시 objective 배열 · symbol 유지) 를 추가한다.
- 완료 기준: (1) ctest 타깃 2개 통과 (2) OPT-08 · OPT-14 · OPT-16 의 완료 기준이 테스트로 고정
- 변경 범위: tests/CMakeLists.txt, tests/TestOptimizerPresentationModel.cpp(신규), tests/TestOptimizerSettings.cpp(신규)
- 선행: PR #655 (`tests/CMakeLists.txt` +18/-18 — #654 스택 위, 그 랜딩 뒤 등록)
- 충돌: OPT-08 · OPT-10 · OPT-14 · OPT-16 (테스트가 고정하는 동작 — 먼저 쓰고 각 PR 이 갱신) · DEV-19 (tests/CMakeLists.txt 등록 헬퍼 — 먼저 오면 그 형식으로 등록) · B2 교집합: tests/CMakeLists.txt → 공유 12건(deps.md 5절) · PR #652(tests/CMakeLists.txt) · PR #651(tests/CMakeLists.txt)
- 흡수: OPT-U3 · #489(OPT 몫) · OPT-c32 · OPT-c54, c55 (← UIC-c57, DEV-c24)
- 비고: `DashOptimizer` 가 `DashProjectManager::Instance()` 를 역참조하므로 JSON 왕복 테스트는 파일 경로를 주입할 수 있어야 한다 — `setProjectDirectory` 우회 접점 (M 사유).

### OPT-21 · Optimizer 화면에 FE Validation 버튼을 두고 Direct Launch 를 prefill 로 연다
- 종류: PR | 규모: S | 태그: B · feature
- 목표: Validation 탭에 버튼을 추가한다. 그 Set 의 입력 파일(OPT-02 결정 산출물) · Target Part(`resolveGeometrySource` 의 componentName) · 출력 폴더 `Optimizer_{Set}/FEValidation/` 으로 다이얼로그 `prefill` 을 부른다.
- 완료 기준: (1) 버튼 → 다이얼로그가 세 값으로 채워져 열림 (2) 입력 파일 부재 시 버튼 비활성 + 툴팁 (3) Done 뒤 Result Preview 자동 선택은 #604 동작 그대로
- 변경 범위: W, Wh
- 선행: OPT-02 · PR #652(#604) · RUN-30 (다이얼로그 `prefill` 진입점 — 먼저 머지되는 쪽이 만든다)
- 충돌: OPT-01 · OPT-26 (W) · PR #652 · RUN-30 (prefill 진입점 공용) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizerWidget.h → OPT-05 OPT-06 OPT-13 OPT-18 OPT-22 PRJ-25 UIC-22
- 흡수: 접점 #653 · OPT-c36 · OPT-c40 (← RUN-c19)
- 비고: 담당 RUN — OPT 측 버튼만 이 항목.

### OPT-22 · 프리뷰 실행 중 Preview 버튼을 잠그고 모핑 완료·NX 완료/실패 통지로 푼다 — 위젯이 자기 요청의 완료를 받는다
- 종류: PR | 규모: S | 태그: B, D · bug
- 목표: `onPreviewButtonClicked` 진입에서 `previewBtn` 을 잠그고(상태 텍스트), Morphing 분기는 `co_await performMorphing` 종료에서, CAD 분기는 CAD-01 이 태그를 실어 항상 방출하는 `updatePrtGeometryCompleted/Failed(requester, stpPath)` 를 위젯이 직접 구독해 자기 `stpPath` 와 짝지어 푼다. `DashMainWindow` 부모 탐색으로 상태 애니메이션만 켜던 블록은 위젯 시그널(`nxPreviewRequested`) 로 바꾸고 MainWindow 가 구독한다 (PRJ-25 와 같은 방식). OCCT 표시는 MainWindow 의 `onNxPreviewStepReady` 그대로.
- 완료 기준: (1) 프리뷰 중 Preview 재클릭 불가, 완료·실패·조기 `co_return` 전부에서 버튼 복원 (2) `view/DashOptimizerWidget.cpp` 에 `qobject_cast<DashMainWindow*>` 0건 (3) NX 실패(`updatePrtGeometryFailed`) 시 Optimizer 상태 텍스트가 실패로 바뀐다 — NX 환경 수동 1회
- 변경 범위: W (`onPreviewButtonClicked` :1498-1870 · `setupConnections`), Wh, view/DashMainWindow.cpp (구독 1곳)
- 선행: CAD-01 (대칭 4종 · 태그 — CAD 분기) · PRJ-25 (부모 탐색 제거를 그쪽이 먼저 하면 (2) 는 그 항목 몫) · PR #655 (`view/DashMainWindow.cpp` +1/-10 — #654 → #655 랜딩 뒤)
- 충돌: OPT-01 · OPT-26 (같은 함수) · PRJ-25 (W 같은 블록) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizerWidget.h → OPT-05 OPT-06 OPT-13 OPT-18 OPT-21 UIC-22 · PR #652(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: #281-D(버튼 몫) · OPT-D19(위젯 수신 몫) · #457(D19 후속) · #463(OPT 몫 — Preview) · OPT-c38(버튼 몫), c39, c51 (← MOR-c06, CAD-c37, EXE-c23)
- 비고: OPT-D19 본체(태그 왕복·`m_batchMode`)는 CAD-01 — 이 항목은 랜딩 뒤 OPT 측 소비자 전환. 가드 형식은 EXE-09 헬퍼가 있으면 그것을 쓴다. Morphing 분기만 먼저 떼어 CAD-01 전에 넣어도 된다.

### OPT-23 · Optimizer가 실제 사용한 입력 버전으로 최신성을 판정한다
- 종류: PR | 규모: S | 태그: C, A · feature
- 목표: #650 규칙으로 실제 최적화에 사용한 Builder 모델 버전과 필요한 상류 입력 버전을 기록하고 DashOptimizer::upstreamStaleReasons가 비교한다. Builder·Geometry·Condition setId만 비교해서 재생성 최신성을 보장하지 않는다.
- 완료 기준: 실제 사용 버전의 저장·복원, Builder 재학습 후 최신성 사유, 버전 누락·비교 불가 규칙 적용. 현재 입력 선택 변경으로 기존 결과의 소비 버전·출처를 수정하지 않는다. 프로젝트 호출·집계와 VM 표시는 Set의 판정 결과를 사용한다.
- 변경 범위: M, Mh (`runOptimization` · `saveSettings` · `upstreamStaleReasons`)
- 선행: BLD-18 · PRJ-23
- 충돌: OPT-07 · OPT-15 · OPT-24 (saveSettings) · OPT-26 (`Optimizer_{Set}.json` 최상위 RMW — 서로 덮는다) · OPT-16 (로더) · B2 교집합: DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashOptimizer.h → OPT-05 OPT-18 · PR #654(DashOptimizer.cpp)
- 흡수: #650(OPT 몫) · OPT-c41 (← PRJ-c38)
- 비고: OPT-26은 #685 참조·출처 검증, 본 항목은 #650 버전·최신성이다. 최상위 JSON 저장은 OPT-24 공용 경로와 조율하되 최초 입력 핀과 비원자 핀 RMW를 신설하지 않는다. PRJ-22와 공유 코드 적용 순서만 조율한다.

### OPT-24 · Optimizer 설정 JSON 쓰기를 공용 파일 헬퍼로 옮긴다
- 종류: PR | 규모: S | 태그: A · refactor
- 목표: saveSettings와 설정 JSON 읽기를 PER-02 공용 DashSaveSystem 헬퍼로 옮겨 원자 쓰기와 사유 반환을 사용한다. OPT-26의 현재 입력 참조·출처 저장도 같은 진입점을 사용하도록 적용 순서를 조율한다.
- 완료 기준: 설정 JSON 직접 읽기·직쓰기를 공용 경로로 모으고 읽기 전용 경로의 실패 시 기존 파일 보존·오류 로그를 검증한다. OPT-20 왕복에서 참조·실제 소비 버전 등 다른 최상위 키도 보존한다.
- 변경 범위: M (saveSettings · 설정 JSON 읽기 · OPT-26 참조 저장 접점)
- 선행: PER-02
- 충돌: OPT-07 · OPT-15 · OPT-23 (saveSettings) · OPT-26 (참조 저장의 같은 파일) · OPT-16 (로더) · B2 교집합: DashOptimizer.cpp → 공유 17건(deps.md 5절) · PR #654(DashOptimizer.cpp)
- 흡수: #479(OPT 몫) · #478(OPT 몫) · #480(OPT 몫 — PER-04 뒤 버전 키 자동) · OPT-c46 (← PER-c29)
- 비고: PER-c08 의 RMW 13지점 중 1건. 헬퍼가 RMW 를 돕는 진입점(`updateObject(path, fn)` 류) 을 두면 이 함수가 첫 소비자 후보. 공용 진입점 명칭은 PER-02 의 `DashSaveSystem` 승격 결정을 따른다 (decisions ③ — 신설 `utils/DashJsonFile` 은 폐기).

### OPT-25 · 수렴 히스토리 PNG 를 DPR 반영해 표시한다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: `onOptimizationSucceeded` 가 PNG 를 논리 800×600 으로 `scaled` 해 QLabel 에 넣어 DPR≠1 에서 흐려진다. `devicePixelRatioF()` 배의 물리 크기로 스케일하고 `setDevicePixelRatio` 를 건다 (또는 원본을 두고 QLabel 논리 크기만 800×600).
- 완료 기준: (1) 150%·200% 모니터에서 PNG 선명 (2) 100% 에서 현행과 같은 표시 크기 (3) 다른 배율 모니터로 옮겨도 깨지지 않음 — UIC-02 실기 환경에서 함께
- 변경 범위: W (`onOptimizationSucceeded` :702-725)
- 선행: -
- 충돌: OPT-05 (성공 통지 블록 — 같은 함수) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절)
- 흡수: #447 R5 · OPT-c47 (← UIC-c34)
- 비고: R1~R5 중 OPT 몫. UIC-02 의 200% 포함 실기 검증에서 함께 확인하면 비용이 준다.

### OPT-26 · Optimizer가 Builder를 setId로 참조하고 출처 검증 후 실행·조회·프리뷰에 사용한다 (#685)
- 종류: PR | 규모: S | 태그: A, C · bug
- 목표: #685의 소비 경계에서 Builder setId와 응답·모델·part 등 선택을 Optimizer_{Set}.json에 저장·복원한다. #368의 공통 판독으로 Builder 산출물 출처를 검증하고 deck은 산출물 기록에서 해석한다. 현재 Optimizer Set의 ID를 유지하면서 다른 Builder를 선택할 수 있으며 외부 실행에는 ID로 해석한 실제 경로를 전달한다.
- 완료 기준: ① Builder 개명 후 동일 setId 참조 복원, 동명 재생성의 다른 setId와 구분 ② 다른 유효 Builder 선택·실행 가능 ③ 선택 변경만으로 기존 결과 출처 불변, 재실행 결과 덮어쓰기 때 실제 출처 갱신 ④ 필수 출처 누락·해석 불가 model_info는 재생성 안내, live parameter·이름·경로 추론 fallback과 자동 이관 금지 ⑤ 실행·조회·프리뷰가 같은 검증된 선택과 deck을 사용 ⑥ MCU 등 deck 비해당 유형은 공통 계약의 적용 관계로 판정하고 필수 출처 검증을 일괄 면제하지 않음.
- 변경 범위: model/DashOptimizer.cpp · model/DashOptimizer.h · view/DashOptimizerWidget.cpp
- 선행: BLD-20 (#368 생산·공통 계약 완료)
- 충돌: OPT-01 · OPT-21 · OPT-22 (`onPreviewButtonClicked` 같은 함수) · OPT-23 · OPT-24 (`Optimizer_{Set}.json` 최상위 RMW) · OPT-16 (M 로더) · B2 교집합: DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashOptimizer.h → OPT-05 OPT-07 OPT-15 OPT-18 · PR #654(DashOptimizer.cpp)
- 흡수: #685 (구 #368 T23 OPT 소비 몫) · OPT-D15 · OPT-D16 · #457(configs 전량 모핑·펌핑 2곳) · #281-D(펌핑 몫) · OPT-c09, c25, c26(해소됨), c57 · OPT-c38(펌핑 몫), c56 (← MOR-c06, UIC-c58)
- 비고: PR #530은 당시 재업로드 결정 기록이며 옛 조합 ID 핀 코드를 그대로 이식하지 않는다. 생산 계약은 PER-07·BLD-20에서 재사용한다. #650 버전·최신성과 #473 결과 조작은 별도 목표이고 #681 머지 조건으로 두지 않는다. OPT-03·OPT-04 흡수·결번은 유지한다. 프리뷰 deck 1건으로 configs 전수 모핑과 processEvents 2곳을 제거하고 UI 응답성을 확인한다. 참조 쓰기는 공용 헬퍼 도입 순서와 조율한다.

## 대응표

| 원천 | 항목 | 비고 |
|---|---|---|
| #316 | OPT-01, OPT-02 | 일괄 삭제·관리 목록·컨텍스트·카메라·무효화 → 01 / 산출물 위치 → 02. CAD `.stp` 덮어쓰기는 범위밖(CAD, OPT-c08) |
| #457 | OPT-26, OPT-22 | configs 전량 모핑·펌핑 2곳 → 26 (구 OPT-03·OPT-04 결번) / OPT-D19 태그 왕복 → CAD-01 (OPT-c10·c37 을 그쪽 흡수에 등재) / 위젯 측 수신 후속 → 22 |
| OPT-D1 | OPT-16 | |
| OPT-D2 | OPT-17 | PRJ-c58 이관 (OPT-c42) |
| OPT-D3 | OPT-09 | |
| OPT-D4 | OPT-10 | |
| OPT-D5 | OPT-11 | |
| OPT-D6 | OPT-06 | |
| OPT-D7 | OPT-06 | |
| OPT-D8 | OPT-12 | |
| OPT-D9 | OPT-18 | 본체는 해소됨(#314, OPT-c19) — showEvent 잔재만 |
| OPT-D10 | OPT-13 | |
| OPT-D11 | OPT-05 | |
| OPT-D12 | OPT-07 | |
| OPT-D13 | OPT-05 | UIC-c55 · EXE-c44 이관 (OPT-c48 · c50) |
| OPT-D14 | OPT-14 | |
| OPT-D15 | OPT-26 | 구 OPT-03 결번 — 26 으로 흡수. UIC-c58 이관 (OPT-c56) |
| OPT-D16 | OPT-26 | 구 OPT-04 결번 — 26 으로 흡수. 펌핑만. 세션 오염은 해소됨(#559·#564, OPT-c26) |
| OPT-D17 | OPT-01 | |
| OPT-D18 | OPT-01 | ① 핸들 덮어쓰기는 해소됨(#564, OPT-c29); ②③ → 01 · REN-c32 이관 (OPT-c45) |
| OPT-D19 | CAD-01 (본체) · OPT-22 (위젯 수신 후속) | 태그 왕복·`m_batchMode` 는 CAD-01 이 흡수 (OPT-c10·c37). 위젯 소비자 전환은 OPT-22 (CAD-c37 이관, OPT-c39) |
| OPT-D20 | 항목 없음 | 범위밖 — ANA DashPlotSpecBuilder (OPT-c30) |
| OPT-D21 | OPT-15 | |
| OPT-D22 | OPT-06 | |
| OPT-D23 | OPT-19 | |
| OPT-D24 | OPT-08 | |
| OPT-U2 | OPT-18 | |
| OPT-U3 | OPT-20 | UIC-c57 · DEV-c24 이관 (OPT-c54 · c55) |
| 접점 #653 | OPT-21 | 담당 RUN (RUN-30 prefill 진입점 선행). OPT 측 버튼만 — RUN-c19 이관 (OPT-c40) |
| 접점 #685 | OPT-26 | Builder setId 참조·공통 출처 검증·deck 프리뷰. 선행 BLD-20(#368) |
| 접점 #249 | CAD-01 | OPT-c10·c37 을 CAD-01 흡수에 등재 (CAD-c41 · c42) |
| 접점 #281-D | OPT-26 · OPT-22 | MOR 에서 이관 (MOR-c06 → OPT-c38) — 펌핑 → 26(구 OPT-04), Preview 버튼 → 22 |
| 접점 #318 ⑫ | OPT-01 | REN 에서 이관 (REN-c19 · c30 · c32 → OPT-c43 · c44 · c45) — REN-10 인수=숨김의 선행 |
| 접점 #443 · #685 | OPT-15 · OPT-26 | #520 setId 기반 참조 저장 계약 공유 |
| 접점 #650 | OPT-23 | 실제 소비 버전으로 Set이 판정. 선행 PRJ-23·BLD-18 |
| 접점 #463 | OPT-05 · OPT-22 | EXE 에서 이관 (EXE-c23 → OPT-c51) — 규약·헬퍼는 EXE-07 · 09 |
| 접점 #483 | OPT-12 | DEV 에서 이관 (DEV-c30 → OPT-c49) — 샘플 구속 행 |
| 접점 #489 | OPT-20 | DEV 에서 이관 (DEV-c24 → OPT-c55) — DEV 는 인프라(DEV-18 · 19) |
| 접점 #447 R5 | OPT-25 | UIC 에서 이관 (UIC-c34 → OPT-c47) |
| 접점 #487 | 항목 없음 | UIC 에서 이관 (UIC-c41(b) OPT 1곳 → OPT-c58). `val_dvTable` 은 `NoEditTriggers`(ui/DashOptimizerWidget.ui:255) 라 사용자 편집 경로가 없다 — 범위 검증 대상 아님, 델리게이트 항목 신설 불요 (편집 가능한 DOE-20 과 전제가 다르다) |
| 접점 #478 · #479 · #480 | OPT-24 | PER 에서 이관 (PER-c29 → OPT-c46). 부록 A OPT 5건(D5 · D6 · D7 · D12 · D21)은 OPT-11 · 06 · 06 · 07 · 15 가 덮음 (PER-c05 → OPT-c52) |
