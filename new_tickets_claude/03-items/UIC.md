# UIC 작업 목록

> dev @ b08a91b3. 현행은 Qt6 — 위키 Stage 3(`PassThrough` 선언)은 소멸했고, 비정수 DPR 이 이미 들어오므로 R1~R5 는 현재 결함이다(각 모듈 소관). 열린 PR 5건 중 머지 대상 4건과의 충돌: #655 · #654 · #652 · #651 이 DashMainWindow.cpp 를 만지고, 그중 **#655 는 `setupMorphingBar()`·`initializeMorphingController()` 본문과 `view/overlay/DashMorphingSettings.{cpp,h}`·`ui/overlay/DashMorphingSettings.ui`·`tests/CMakeLists.txt` 를 재작성**한다 — UIC-07 · UIC-22 는 #655 를 선행으로 둔다(decisions ④). **#530 은 머지하지 않으므로**(decisions ②) 충돌란에서 제거했고 홉별 항목(RUN-34 · OPT-26)이 대신 선다. 단순 충돌란 기입은 D-1 `build_deps.py --apply` 가 파일 교집합으로 채운다. DashMainWindow 를 고치는 항목(01 · 03 · 05 · 07 · 09 · 10)은 PRJ 의 DashMainWindow 항목과도 같은 파일이다.
> 창·DPI 항목의 순서는 위키 3부 "순서에 관한 제약" 을 따른다: 01(응급) → 03(Stage 2) → 05(Stage 1) → 08/09(Stage 4, 02 결과로 선후 결정) → 07 · 10 · 12 · 13.

### UIC-01 · 창 geometry 를 화면 작업 영역으로 클램프해 복구 불가 상태를 차단한다
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

### UIC-02 · 멀티디스플레이 프리즈를 실기 재현하고 지배 요인·DPI awareness 를 실측한다
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

### UIC-03 · resize·트리 선택마다 dock 을 강제 재분배하는 경로를 없애고 크기 선언을 1회로 바꾼다
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

### UIC-05 · 창 geometry 와 dock 배치를 종료 시 저장하고 기동 시 복원한다
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

### UIC-06 · UI Scale 메뉴(QT_SCALE_FACTOR)의 처분을 정한다
- 종류: DEC | 규모: S | 태그: D
- 목표: a(메뉴 제거, OS 표시 배율에 위임) / b(현행 유지 + 한계 명시) / c(`app.setFont` 포인트 배율로 전환, QSS px→em 선행) 중 택일. `QT_SCALE_FACTOR` 는 화면별 DPI 와 곱해지는 전역 상수라 멀티디스플레이 격차를 배수로 키우고 재시작을 요구한다. 권장 a, 차선 b.
- 완료 기준: 결정 기록 — 선택지 · 근거(UIC-02 의 실사용 조사) · a 선택 시 제거 범위(main.cpp:66-72 `QSettings`+`qputenv` 블록 · view/DashMainWindow.cpp:255-275 scaleMenu · `UI/scaleFactor` 키) → 구현은 **UIC-26**
- 변경 범위: -
- 선행: UIC-02 (실사용 여부)
- 충돌: -
- 흡수: #449 · L0-4 · UIC-c22
- 비고: c 는 UIC-15 가 끝난 뒤에만 의미가 있다 — 폰트만 키우면 px 고정 위젯이 안 따라와 지금보다 나빠진다. 검토 #13 반영 — 구현을 변경 범위 괄호에 숨기지 않고 UIC-08(DEC)↔UIC-09(PR) 선례대로 조건부 PR 항목 UIC-26 으로 분리했다(추적 가능성 확보).

### UIC-07 · 오버레이 3종을 부모 크기에 따라 재배치하고 드래그를 부모 영역으로 클램프한다
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

### UIC-08 · 프레임리스 창의 OS 위임 경로(A·B)와 착수 여부를 결정한다
- 종류: DEC | 규모: S | 태그: D
- 목표: 경로 A(`startSystemMove/Resize` — 구현 버그만 제거, 스냅·시스템 메뉴 복원 안 됨) vs 경로 B(`Qt::Window` + `WM_NCCALCSIZE`/`WM_NCHITTEST` — OS 창 관리 전부 복원, Windows 전용) 택일과, UIC-01/03/05 로 통증이 줄면 보류할지 결정. 위키 권장은 B(사내 선례 검증 구현 있음, 이 프로젝트는 MSVC/Windows 전용). 창 그림자 충돌 선행 확인은 불성립(그림자는 모핑 바에만) — 확인 목록에서 제외.
- 완료 기준: 결정 기록 — 경로 · 착수/보류 · UIC-05 와의 선후(B 를 먼저 하면 state version 번프 1회 절약)
- 변경 범위: -
- 선행: UIC-02 (상시 증상 vs 치명 발현 우선순위)
- 충돌: -
- 흡수: #450 · L0-5(결정부) · UIC-c26
- 비고: #450 의 Goal 이 "택일 여부 결정" 이므로 DEC 를 분리. 구현은 UIC-09.

### UIC-09 · 창 프레임 관리를 OS 에 위임한다 — Qt::Window + WM_NCCALCSIZE/WM_NCHITTEST (경로 B)
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

### UIC-10 · 모듈 위젯을 QScrollArea 로 감싸 스택의 최소 크기 전파를 끊는다
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

### UIC-11 · 중첩 QMainWindow 를 단일화할지 결정한다
- 종류: DEC | 규모: S | 태그: D, E
- 목표: outer `DashMainWindow` 의 `centralWidget` 이 inner `QMainWindow`(양쪽 `setDockNestingEnabled(true)`)인 구조를 A(단일 QMainWindow + `setCorner`) / B(inner 를 QSplitter) / C(유지 + 상태 분리 저장) 중 택일. 기본 C. UIC-03 뒤에도 프로파일링(UIC-02)에서 이중 패스가 지배 요인일 때만 A.
- 완료 기준: 결정 기록 — 선택 · 근거 프로파일 · A 선택 시 dock 10여 개 재배치 실험 결과
- 변경 범위: -
- 선행: UIC-02 · UIC-03
- 충돌: -
- 흡수: #450 · L1-1 · UIC-c23
- 비고: C 는 UIC-05 가 inner state 를 별도 키로 저장하면 자동 충족. 원천 정정(검토 #14) — L1-1 은 #449 가 아니라 #450("테두리 없는 창과 중첩 메인 윈도우 구조 재검토") 소관. 이 항목이 빠지면 #450 의 절반이 추적에서 누락된다.

### UIC-12 · 폰트 의존 고정 높이 6곳을 sizeHint 로 바꿔 배율·폰트 변경에 추종시킨다
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

### UIC-13 · 다이얼로그 생성자의 resize 하드코딩 2곳을 제거한다
- 종류: PR | 규모: S | 태그: D · refactor
- 목표: `DashMeshQualityDialog` `resize(550,300)` · `MaterialSetupDialog` `resize(500,450)` 을 지우고 레이아웃 `sizeHint()` 에 맡긴다. 크기 지정이 꼭 필요하면 `availableGeometry()` 상한을 건다.
- 완료 기준: 두 다이얼로그가 내용에 맞는 크기로 뜨고 200% 모니터에서 화면을 넘치지 않는다 · `git grep -nE "^[[:space:]]*resize\(" -- view/dialog` 0건 (착수 전 실행값 2 — `DashMeshQualityDialog.cpp:26` · `MaterialSetupDialog.cpp:48`)
- 변경 범위: view/dialog/DashMeshQualityDialog.cpp · view/dialog/MaterialSetupDialog.cpp
- 선행: -
- 충돌: PRJ 의 view/dialog 항목 · MOR(DashMeshQualityDialog 사용처) · B2 교집합: DashMeshQualityDialog.cpp → MOR-01 UIC-12
- 흡수: #449 · L3-7 · UIC-c16
- 비고: 접점 PRJ(view/dialog 소유). 독립적이라 언제 해도 된다. AC 정정(검토 #6) — 전 AC 의 `^\s*resize\(` 는 git 의 POSIX ERE 에 `\s` 가 없어 현행 2건에도 매치 0·exit 1 이었다(착수 전에도 통과하는 공허한 AC). `-P` 를 쓰면 `\s` 도 동작한다.

### UIC-14 · 명령형 크기 지정(setFixed* · ResizeToContents · setSizes)의 허용 규칙을 정한다
- 종류: DEC | 규모: S | 태그: D, E
- 목표: `setFixed*` 74곳 35파일 · `ResizeToContents` 82곳 12파일 · `setSizes({상수})` 22곳의 공통 규칙을 docs/coding-convention.md 에 적는다 — (1) 정사각형 아이콘·칩(`DashMetrics` 토큰 크기)은 `setFixedSize` 허용, 컨테이너·텍스트 위젯은 `sizePolicy`+`minimumSize`, 폰트 연동은 `QFontMetrics`/`sizeHint`; (2) 긴 텍스트 열은 `Interactive`+`setDefaultSectionSize`, `ResizeToContents` 는 짧은 고정 어휘 열만; (3) `setSizes` 는 비율(`setStretchFactor`)로. UIC 영역 11곳(view/common 3 · DashTitleBar 5 · DashMainWindow 3)은 전부 정사각형 아이콘이라 규칙상 변경 0.
- 완료 기준: 결정 기록(컨벤션 절) · 모듈별 적용 대상 수 표(setFixed* / ResizeToContents) — OPT 3/32 · RUN 2/24 · BLD 1/15 · ANA 13/3 · MOR 6/3 · CAD 4/0 · DOE 1/1 · view/dialog 18/3 · view/ai 15/1 — 를 Phase B 에 넘김
- 변경 범위: docs/coding-convention.md
- 선행: UIC-03 (L0-1 이 남은 채 개별 위젯을 고치면 되돌아온다) · UIC-10 (전파 차단이 열 정책보다 우선)
- 충돌: B2 교집합: coding-convention.md → DEV-17 UIC-18 UIC-21
- 흡수: #449 · L3-1 · L3-9 · UIC-c15, c18
- 비고: 모듈별 적용은 `범위밖` — 대응표 참조. 기계적이지 않고(판단이 필요) 크므로 1건으로 묶지 않는다.

### UIC-15 · QSS 의 px 크기 제약을 DashMetrics 토큰·em 으로 옮긴다
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

### UIC-16 · 사용자 통지 규칙을 세운다 — 무엇을 모달·dock·무통지로 보낼지
- 종류: DEC | 규모: S | 태그: D
- 목표: docs/unified-logger.md 6절(라우팅)을 확장하거나 별도 문서로 — (1) 시스템 실패(파일·외부 도구·모델 부재)는 `DashNotify::error/warning`(로그+모달), 입력 검증 안내는 모달 없이 인라인/툴팁 또는 `DashNotify::info`, 진행 중 정보는 dock; (2) 확인(question)은 래퍼 `confirm` 으로 통일; (3) 모델·컨트롤러는 팝업 금지 — 시그널로 승격하고 뷰가 통지(현행 위반 7건: DashDoeSampler 5 · DashMorphingController 1 · DashHandlePickingInteraction 1); (4) 성공 통지는 결과를 확인한 뒤 — 사례는 `view/DashModelRunnerWidget.cpp:457-462` **Morphing 분기**(`co_await performMorphingAndAddToFileTable(params)` 뒤 성공·실패 구분 없이 `stopGenerateStatusAnimation("Input file generated.")`). 같은 함수의 Condition 분기 `:578-588` 은 198a294c(#533) 에서 반환값을 보게 고쳐졌으므로 인용하지 않는다; (5) 배치 실행 중 모달 억제; (6) 외부 프로세스 실패 절은 #466(EXE)이 얹는다. 리뷰 게이트로 강제.
- 완료 기준: 결정 기록 — 규칙 문서 · 166건의 분류표를 **파일별 `총건 / 그중 Please 계열`** 2열로(규칙 (1) 분기까지 담아야 모듈별 스윕의 입력이 된다): DashMainWindow 21/2 · DoeSamplerWidget 17/6 · AnalysisLauncherWidget 17/11 · OptimizerWidget 16/3 · GeometryParameterWidget 15/7 · ModelBuilderMCUWidget 14/4 · ModelRunnerMCUWidget 13/6 · ModelBuilderWidget 9/6 · ModelRunnerWidget 7/0 · MorphingSettings 6/6 · DashDoeSampler 5/2 · MaterialSetupDialog 4/2 · TopOptPostprocessDialog 3/2 · DoeSamplerResample 3/1 · 나머지 ≤2 (합계 166 / Please 60) — 를 모듈별 적용 입력으로 Phase B 에 넘김
- 변경 범위: docs/unified-logger.md (또는 docs/notification-policy.md)
- 선행: -
- 충돌: EXE-10 (#466 — 같은 문서, 먼저 착수하는 쪽이 만든다)
- 흡수: #482 · #466(접점) · #370(접점, 사례) · UIC-c36, c37, c38 · UIC-c40(사례 — Condition 분기는 해소됨, 인용 좌표는 Morphing 분기 `DashModelRunnerWidget.cpp:457-462`) · UIC-c56(사례) · DOE-c26 · BLD-c31 · UIC-c59, c60 (모듈 건수 입력 — 스윕은 DOE·BLD)
- 비고: 개별 무통지 결함(#323 #324 #376 #393 #394)은 not-to-be 그대로. `QMessageBox` 166건 중 "Please …" 계열은 규칙 (1) 에서 모달 유지/비모달 전환을 갈라야 한다 — **31건이 아니라 60건(선두 45)** 으로 전체의 3분의 1 이상이다(검토 #5). 규칙 (1) 의 적용 범위와 모듈별 스윕 164건의 비용 추정이 2배로 늘어난다. `view/common/DashNotify.h` 주석("입력 검증 안내는 로그 대상이 아니므로 QMessageBox를 그대로 쓴다")이 현행 설계의 근거이므로 규칙은 이 주석을 바꾸는 결정과 함께 적는다.

### UIC-17 · DashNotify 래퍼를 규칙에 맞게 확장한다 — info · confirm · 배치 중 억제
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

### UIC-18 · tr() 182곳을 제거하고 영어 고정을 규칙으로 못 박는다
- 종류: PR | 규모: L | 태그: G, E · refactor
- 목표: `tr("…")` 182곳 23파일(DashMainWindow 95 · ShortcutsDialog 11 · AnalysisLauncherWidgetLauncher 10 · KPIConfigDialog 9 · GeometryParameterWidget 9 · DashAiPlayerDialog 7 · DashConditionParameterization 7 · DashAnalysisLauncher 5 · DashLogDockWidget 4 · ModelRunnerWidget 4 · DashJobRunner 4 · OptimizerWidget 3 · 나머지 ≤2)를 `QStringLiteral`/리터럴로 바꾼다. `.arg` 체인은 그대로. `.ui` 의 `<string>`(uic translate)은 번역기 없이 원문을 돌려주므로 손대지 않는다. docs/coding-convention.md 에 "tr() 금지" 한 줄.
- 완료 기준: `git grep -E "(^|[^A-Za-z0-9_])tr\(" -- '*.cpp' '*.h' ':!tools' ':!tests'` 0건 · 빌드·tests 통과 · 메시지 문자열 diff 가 래퍼 제거뿐(의미 변경 0)
- 변경 범위: 위 23파일 + docs/coding-convention.md
- 선행: -
- 충돌: PR #651 · #652 (DashMainWindow.cpp · DashAnalysisLauncherWidgetLauncher.cpp · DashAnalysisLauncher.cpp · DashJobRunner.cpp · DashConditionParameterization 제외) · #654 · #655 (DashMainWindow.cpp · DashGeometryParameterWidget.cpp tr 9+1 · DashMorphingSettings.cpp) — **열린 PR 5건 중 머지 대상 4건(#651 · #652 · #654 · #655) 머지 후 착수** (#530 은 머지하지 않아 제외, decisions ②) · B2 교집합: coding-convention.md → DEV-17 UIC-14 UIC-21
- 흡수: #490 · UIC-c43, c44
- 비고: L 사유 — 치환 1종의 기계적 변경이라 모듈별로 나누면 리뷰 비용만 늘고 AC(0건)를 한 번에 검증할 수 없다. 반나절 작업이지만 파일 수 기준으로 L. 재유입 방지 grep 가드(CI)는 DEV 접점.

### UIC-19 · Mgr()·GetProject()·GetDesignVariableModel() 직후의 도달 불가 null 가드 27건을 제거한다
- 종류: PR | 규모: L | 태그: E · refactor
- 목표: 항상 non-null 인 접근자(`DashManager::Mgr/PrjMgr` lazy new · `GetProject` 생성자 new 재할당 없음 · `GetDesignVariableModel` 동일) 직후의 순수 가드 — Mgr 12건 10파일 · GetProject 11건 3파일 · GetDVM 4건 2파일 — 를 삭제하고 복합 가드(DashDoeSampler 1)는 뒤 항만 남긴다. 고아가 된 로그 문자열·지역 변수만 정리, 주변 리팩터 금지, 파일 단위 커밋.
- 완료 기준: `git grep -A1 -E "= DashManager::(Mgr|PrjMgr)\(\);|GetProject\(\);|GetDesignVariableModel\(\);" -- '*.cpp' | grep -E "if *\(![a-zA-Z_]+\)"` 0건 · 빌드·tests 통과
- 변경 범위: view/DashMainWindow.cpp · view/DashGeometryParameterCADWidget.cpp · view/DashConditionParameterizationWidget.cpp · view/DashProjectWidget.cpp · controller/DashAnalysisModelContextRegistry.cpp · model/DashModelRunner.cpp · model/DashDoeSampler.cpp · model/DashJobRunnerFeSafe.cpp · model/DashJobRunnerAnsysMechanical.cpp · model/DashJobRunnerAnsysJournal.cpp · model/DashJobRunnerAbaqus.cpp
- 선행: -
- 충돌: PR #651 · #652 · #654 · #655 (DashMainWindow.cpp · DashDoeSampler.cpp · DashManager) · UIC-20(같은 파일 다수 — 연속 작업) · **CON-04 — 설계 충돌**(단순 파일 교집합이 아니다): CON-04 의 `GetProject` null 가드 신설은 **기각**이고(도달 불가), 같은 파일 `view/DashConditionParameterizationWidget.cpp` 에 뒤로 랜딩하면 이 항목의 완료 기준(해당 가드 0건)을 깬다. CON-04 에는 QPointer 2곳과 `:370-371` 쪽 실제 무가드 역참조만 남는다 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashGeometryParameterCADWidget.cpp → 공유 10건(deps.md 5절) · DashConditionParameterizationWidget.cpp → CON-03 CON-05 CON-06 CON-07 CON-12 DOE-19 · DashJobRunnerAnsysJournal.cpp → CAD-01 LCH-06 LCH-07 LCH-14 LCH-27 LCH-29 · DashAnalysisModelContextRegistry.cpp → EXE-22 PRJ-03 REN-01 REN-02 REN-07 · DashJobRunnerFeSafe.cpp → LCH-07 LCH-14 LCH-18 LCH-30 PRJ-14 · DashJobRunnerAbaqus.cpp → LCH-02 LCH-07 · DashJobRunnerAnsysMechanical.cpp → LCH-02 LCH-07 · DashProjectWidget.cpp → DEV-10 PRJ-33
- 흡수: #508 · UIC-c46, c47, c48
- 비고: `GetIOController()` 는 프로젝트 열기 전 null 이라 대상 아님(113건 그대로). 규모 정정(검토 #12) — 파일 11개로 M 상한(8)을 넘으니 `L`. L 사유는 UIC-20 과 같다: 삭제 1종의 기계적 변경이고 AC 가 레포 전체 0건이라 쪼개면 검증이 쪼개진다(파일당 1~3줄 삭제 · 파일 단위 커밋). **decisions ⑦ 확정** — CON-04 ↔ UIC-19 는 UIC-19 가 맞다. `DashProjectManager` ctor 가 `m_project = new DashProject()` 로 1회 할당하고 재할당이 없으며(`:26-28`), `GetProject()` 는 `return m_project` 뿐(`:45-48`), `CloseProject()` 도 `SetProjectPath(QString())` 로 내용만 비운다(`:239`) → 항상 non-null 이므로 CON-04 의 가드 신설은 기각한다.

### UIC-20 · DashProjectManager::Instance() 직후의 도달 불가 null 가드 116건을 제거한다
- 종류: PR | 규모: L | 태그: E · refactor
- 목표: 순수 가드 103건 22파일(변경 범위에 전건 열거 — DashModelBuilder 15 · DashModelRunner 14 · DashDoeSampler 12 · DashProject 11 · DashOptimizer 9 · ResultsAnalyzerWidget 6 · DashModelBuilderMCU 6 · ModelBuilderMCUWidget 5 · ModelRunnerWidget 3 · ModelRunnerMCUWidget 3 · CAD·GeometryParameter·ConditionParameterization 모델 각 3 · 나머지 ≤2)을 삭제하고 복합 가드 13건(ResultsAnalyzerWidget 5 · AnalysisLauncherKPI 5 · AnalysisLauncher 2 · JobRunner 1)은 `IsProjectOpen()`/`GetIOController()` 항만 남긴다. 접근자 체이닝으로 불필요해진 지역 변수 제거. 파일 단위 커밋.
- 완료 기준: `git grep -A1 "= DashProjectManager::Instance();" -- '*.cpp' | grep -E "if *\(![a-zA-Z_]+\)"` 0건 · 복합 가드의 앞 항 0건 · 빌드·tests 통과
- 변경 범위: **23파일** — model/ 13: DashModelBuilder.cpp 15 · DashModelRunner.cpp 14 · DashDoeSampler.cpp 12 · DashProject.cpp 11 · DashOptimizer.cpp 9 · DashModelBuilderMCU.cpp 6 · DashConditionParameterization.cpp 3 · DashGeometryParameter.cpp 3 · DashGeometryParameterCAD.cpp 3 · DashAnalysisLaunchExecutor.cpp 1 · DashAnalysisLauncher.cpp 1+2(복합) · DashJobRunner.cpp 1+1(복합) · DashAnalysisLauncherKPI.cpp 0+5(복합) / view/ 10: DashResultsAnalyzerWidget.cpp 6+5(복합) · DashModelBuilderMCUWidget.cpp 5 · DashModelRunnerMCUWidget.cpp 3 · DashModelRunnerWidget.cpp 3 · DashModelBuilderWidget.cpp 2 · DashConditionParameterizationWidget.cpp 1 · DashDoeSamplerResampleWidget.cpp 1 · DashDoeSamplerWidget.cpp 1 · DashGeometryParameterWidget.cpp 1 · DashOptimizerWidget.cpp 1
- 선행: -
- 충돌: PR #651 · #652 (DashProject.cpp · DashDoeSampler.cpp · DashAnalysisLauncher.cpp · DashJobRunner.cpp) · #654 · #655 · UIC-19 — **열린 PR 머지 후 착수** (#530 은 머지하지 않아 제외, decisions ②) · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelBuilderWidget.cpp → 공유 10건(deps.md 5절) · DashAnalysisLaunchExecutor.cpp → LCH-06 LCH-07 LCH-14 LCH-16 LCH-28 LCH-34 PRJ-09 · DashConditionParameterizationWidget.cpp → CON-03 CON-05 CON-06 CON-07 CON-12 DOE-19 · DashGeometryParameterWidget.cpp → DEV-10 MOR-01 MOR-02 MOR-03 MOR-17 MOR-22 MOR-23 · DashModelBuilderMCU.cpp → BLD-01 BLD-10 BLD-12 BLD-13 BLD-17 BLD-18 PRJ-09 · DashJobRunner.cpp → LCH-02 LCH-03 LCH-07 LCH-13 LCH-14 PRJ-09 · DashAnalysisLauncherKPI.cpp → PRE-11 PRE-12 PRE-21 PRE-22 PRJ-09 · DashConditionParameterization.cpp → CON-01 CON-02 CON-05 CON-06 PRJ-09 · DashDoeSamplerWidget.cpp → DOE-05 DOE-06 DOE-09 DOE-11 DOE-13 · DashGeometryParameterCAD.cpp → CAD-03 CAD-05 CAD-06 CAD-09 PRJ-09 · DashDoeSamplerResampleWidget.cpp → DOE-02 DOE-20 · DashGeometryParameter.cpp → MOR-11 PRJ-09 · DashModelRunnerMCUWidget.cpp → RUN-22 UIC-23 · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp)
- 흡수: #508 · UIC-c45 · DOE-c27 · UIC-c61 (DOE 집계 — 규칙이 달라 착수 시 재집계)
- 비고: L 사유 — 삭제 1종의 기계적 변경, 이슈 본문이 "파일 단위 커밋(리뷰 단위)" 을 이미 정했고 AC 가 레포 전체 0건이라 분할하면 검증이 쪼개진다. 모듈별 분할이 필요하면 model/ 과 view/ 두 PR 로. 범위 정정(검토 #12) — 전 표기 "26파일(model 15 · view 11)" 은 실측과 다르다. 순수 가드 22파일(model 12 · view 10) ∪ 복합 가드 4파일(신규는 `model/DashAnalysisLauncherKPI.cpp` 1벌) = **23파일(model 13 · view 10)**. `01-sources/open_issues/508.md` 가 집중 파일로 든 `DashDataProcessor.cpp 17` 은 dev 에 그 파일이 없어 소멸.

### UIC-21 · QLineEdit 숫자 입력에 범위 검증기와 허용 범위 툴팁을 공용 헬퍼로 적용한다
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

### UIC-22 · 표 셀 위젯의 현재 행을 해석하는 공용 헬퍼를 만들고 기존 private 헬퍼 2개를 흡수한다
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

### UIC-23 · MCU 데이터셋 표 browse 버튼 2곳이 캡처한 행 대신 호출 시점의 행을 쓰게 한다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: `DashModelRunnerMCUWidget::addDatasetFileRow` · `DashModelBuilderMCUWidget::addDatasetFileRow` 의 `[this, row]` 람다가 버튼 포인터를 캡처하고 `tableRowOfCellWidget` 로 해석, `-1` 이면 파일 다이얼로그 전에 반환한다. 라디오 ID 재부여 루프는 별개 계약 — 건드리지 않는다. 같은 함수의 modeCombo(위젯 아이덴티티)와 규칙이 하나가 된다.
- 완료 기준: 두 표 각각에서 중간 행을 지운 뒤 아래 행의 browse 를 누르면 그 행에 경로가 기록되고 "Invalid file widget at row N" 이 뜨지 않는다 · 두 함수에 `[this, row]` 0건
- 변경 범위: view/DashModelRunnerMCUWidget.cpp · view/DashModelBuilderMCUWidget.cpp
- 선행: UIC-22
- 충돌: RUN-22 (DashModelRunnerMCUWidget) · BLD-01 · BLD-09 · BLD-10 · BLD-12 · BLD-13 · BLD-17 (DashModelBuilderMCUWidget) · B2 교집합: DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelRunnerMCUWidget.cpp → UIC-20
- 흡수: #514-2 · #514-3 · BLD-D10 · #474(BLD-D10 축) · UIC-c50, c51 · BLD-c18 · BLD-c35 · RUN-c14 (BLD-08 병합, B2)
- 비고: BLD-08 과 병합(B2 — 같은 함수를 같은 방식으로). #514-1(Reference File 표)은 #617 에서 파일이 사라져 해소, #514-4(Direct 입력 케이스 표)는 PR #652 가 표를 삭제해 머지 시 소멸 — 둘 다 항목 없음. 접점 RUN·BLD.

### UIC-24 · Model Runner 파일 표 Preview 의 죽은 row 인자를 제거한다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `onFilePreviewClicked(int row, …)` · `performPreviewLogic(int row, …)` 에서 쓰이지 않는 `row` 를 빼고(자기 재귀 포함), `createFileTableRow` 의 람다 캡처를 `[this, filePath]` 로 줄인다. 행 삭제 뒤 Preview 가 다른 케이스를 열 가능성(잠복)을 구조적으로 없앤다.
- 완료 기준: `DashModelRunnerWidget.h` 의 두 시그니처에 `row` 없음 · 행 삭제 후 Preview 가 누른 행의 파일을 연다 · 빌드 통과
- 변경 범위: view/DashModelRunnerWidget.h · view/DashModelRunnerWidget.cpp
- 선행: -
- 충돌: **RUN-24 (같은 함수 — UIC-24 를 먼저)** · RUN 의 나머지 DashModelRunnerWidget 항목 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunnerWidget.h → PRJ-25 RUN-09 RUN-15 RUN-28 RUN-29 RUN-30
- 흡수: #514-5 · RUN-D22 · UIC-c53 · RUN-c37 · UIC-c62
- 비고: 접점 RUN. `[X]` 버튼은 이미 `indexAt` 재계산 — 유지. **decisions ⑦ 확정** — RUN-24 와 같은 함수 본문(`performPreviewLogic` :1448-1557)을 만지고 **순서는 UIC-24 가 먼저**다: UIC-24 가 시그니처(`int row` 삭제, `.h:53`·`:185`)와 자기 재귀(`:1465`)·람다 캡처(`:2006`)를 바꾸므로 먼저 랜딩해야 RUN-24 가 좁아진 시그니처 위에서 작업한다. RUN 쪽 대칭 기재는 `보류: RUN 몫`.

### UIC-25 · #446 을 닫는다 — 추적 부모, 실작업 없음
- 종류: CLOSE | 규모: S | 태그: D
- 목표: 하위 #447~#450 이 UIC-01~03 · 05~15 · 26 으로 분해됐고 부모에 고유 작업이 없다.
- 완료 기준: 닫기 사유 — "서브 이슈 4건이 새 목록 항목으로 대체됨. Qt6 전환으로 L0-3(rounding policy)은 소멸"
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #446 · UIC-c01
- 비고: -

### UIC-26 · UI Scale 메뉴와 QT_SCALE_FACTOR 경로를 제거한다 (UIC-06 이 a 를 택할 때)
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

## 대응표

| 원천 | 항목 | 비고 |
|---|---|---|
| #446 | UIC-25 | CLOSE — 추적 부모 |
| #447 | UIC-01 · UIC-02 | L0-3 은 Qt6 로 해소(manifest 실측만 UIC-02) · R1~R5 는 범위밖 |
| #448 | UIC-05 · → PRJ-14(스코프 결정 — UIC-04 병합, B2) · UIC-03(선행) | UIC-c07 도 PRJ-14 |
| #449 | UIC-03 · UIC-06 · UIC-07 · UIC-10 · UIC-12 · UIC-13 · UIC-14 · UIC-15 · UIC-26 | 모듈별 setFixed*/ResizeToContents 적용은 범위밖 · L1-1(UIC-11)은 #450 으로 이관(검토 #14) |
| #450 | UIC-08 · UIC-09 · UIC-11 | UIC-11 = L1-1 중첩 QMainWindow (이슈 제목·Background 가 명시) |
| #482 | UIC-16 · UIC-17 | 호출부 164건 스윕은 범위밖 → PRJ 32(DashMainWindow 21 + view/dialog 11) · DOE 28 · MOR 24 · BLD 23 · RUN 20 · LCH 18 · OPT 16 · CAD 2 · CON 1 (DashNotify 자체 2 제외) |
| #487 | UIC-21 (`QLineEdit` 5줄 — UIC-c41(a)) · 범위밖 → DOE · OPT (표 셀 3곳 — UIC-c41(b)) | 검토 #10 — 표 셀은 `QTableWidgetItem::text()` 파싱이라 델리게이트 기제. DoeSamplerResampleWidget 2곳 → DOE · OptimizerWidget 1곳 → OPT (`보류: DOE · OPT 몫`) |
| #490 | UIC-18 | |
| #508 | UIC-19 · UIC-20 | |
| #514 | UIC-22 · UIC-23 · UIC-24 | #514-1 해소됨(#617, UIC-c49) · #514-4 PR #652 머지 시 소멸(UIC-c52 — 머지 확인 후 닫음, 소유 DOE/LCH) |
| #466 (접점) | UIC-16 | 규칙 문서 공유 — EXE 가 프로세스 실패 절을 얹음 |
| #370 (접점, 부수 4건) | UIC-16(사례) | 부수3(UIC-c40)의 Condition 분기는 198a294c(#533)로 해소 — 사례는 Morphing 분기 `DashModelRunnerWidget.cpp:457-462` 로 교체(검토 #4). 수정은 범위밖 → RUN |
| L0-1 | UIC-03 | |
| L0-2 | UIC-05 | |
| L0-3 | 해소됨 | Qt6 기본 PassThrough — 잔여 manifest 실측은 UIC-02 |
| L0-4 | UIC-06 (결정) · UIC-26 (a 결정 시 구현) | |
| L0-5 | UIC-08 · UIC-09 | 그림자 선행 확인(c26)은 불성립 |
| L0-6 | UIC-01 | |
| L1-1 | UIC-11 | 원천 #450 (전 표기 #449 — 검토 #14) |
| L1-2 | UIC-10 | |
| L1-3 | UIC-10 | `.ui` 최상위 레이아웃은 16벌 전부 이미 있음 — 실효 몫은 컨테이너 `minimumSize` 3건(검토 #7) |
| L1-4 | UIC-03 | |
| L2-1 | UIC-03 | |
| L2-2 | UIC-03 | |
| L2-3 | UIC-03 | |
| L2-4 | UIC-03 | |
| L2-5 | UIC-03 | |
| L2-6 | UIC-02(실측) · UIC-12(잔여) | "Qt6 자동 처리" 는 임시 판정 — 위키가 "경로 B 로 가도 남는다" 고 못 박아 UIC-02 완료 기준 (2) 로 측정한 뒤 확정(검토 #15) |
| L2-7 | UIC-05 | |
| L3-1 | UIC-14 | 규칙 — UIC 영역 변경 0, 모듈 적용 범위밖 |
| L3-2 | UIC-12 | |
| L3-3 | 범위밖 → ANA | UIC-c35 — DashAnalyzerHelpers · DashResultsAnalyzerWidget |
| L3-4 | UIC-07 | |
| L3-5 | UIC-07 | 접점 MOR |
| L3-6 | UIC-07 | 접점 MOR · REN |
| L3-7 | UIC-13 | 접점 PRJ |
| L3-8 | UIC-15 | |
| L3-9 | UIC-14 | 규칙 — 모듈 적용 범위밖 |
| R1 | 범위밖 → CAD | UIC-c30 — DashOcctViewWidget 마우스 좌표 DPR 보정. Qt6 로 현재 발현 |
| R2 | 범위밖 → ANA | UIC-c31 |
| R3 | 범위밖 → ANA | UIC-c32 |
| R4 | 범위밖 → ANA | UIC-c33 — Qt6 `resizeGL` 단위 1회 실측 후 |
| R5 | 범위밖 → OPT | UIC-c34 |
| BLD-D10 | UIC-23 | |
| RUN-D22 | UIC-24 | RUN-c37 → UIC-c62 |
| #482 (DOE·BLD 건수 이관) | UIC-16 | DOE-c26 → UIC-c59 · BLD-c31 → UIC-c60 — 분류표 입력, 스윕은 각 모듈 |
| #508 (DOE 건수 이관) | UIC-19 · UIC-20 | DOE-c27 → UIC-c61 |
| CAD-D2 · #455 (CAD 가 UIC 로 넘김) | 범위밖 → PRJ-26 | CAD-c20 — `openFileInViewport` 는 PRJ 소유 함수 (PRJ-c64) |
| OPT-D13 | 범위밖 → OPT | UIC-c55 |
| ANA-D12 | 범위밖 → ANA | UIC-c56 — 통지 규칙 사례 |
| DOE-U2 | 범위밖 → LCH | UIC-c56 — PR #652 casesTable |
| CAD-D1 · CAD-D9 | 범위밖 → CAD | UIC-c56 — CAD-07 흡수 완료 |
| CAD-U5 · CON-U5 · OPT-U3 | 범위밖 → CAD · CON · OPT | UIC-c57 — 테스트 부재 |
| MOR-D14 · CAD-D6 · BLD-D5 · RUN-D8 · RUN-D25 · ANA-D1 · OPT-D15 | 범위밖 → 각 모듈 | UIC-c58 — 표 행 캡처 아님 |
| QUndoStack (조사 지시) | 항목 없음 | UIC-c42 — 0건, 요구 이슈 없음 |
