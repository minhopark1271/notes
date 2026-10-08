# View 정리 전략 — Qt Designer 도입 vs 코드 정리

> 원본: 사전조사 Issue #202 — 본문을 이 페이지로 이관한 뒤 Issue 삭제 (2026-08-24). **본 페이지가 정본**
> 이관 주석: 아래 머리글의 `상태:` (Wiki 미연동·원격 미생성) 는 이관 전 시점 표기

> 상태: 로컬 초안 (GitHub Issue / Wiki 미연동)
> 기반 문서: [[198-1-improvement-roadmap]] — 4절 진단(Fat View·중복)과 Phase 5(ViewModel 수렴)의 전제를 계승
> 관련 문서: [[192-1-architecture-analysis-mvc-mvvm]]
> 파생 문서: [[200-3-prioritized-backlog]] — 본 문서 0\~5단계를 통합 백로그의 W8·W13·W14·W19에 수록
> 관련 문서: [[197-1-gui-restructure-mvvm-qml]] — QML 전환 찬/반 판정. 본 문서의 코드 정리 전략(헬퍼 통합·스타일 일원화·.ui 파일럿)을 QML 이득의 대체 수단으로 인용
> 분석 시점: 2026-07-06, 브랜치 `dev` — view 47,485 LOC(.cpp 기준), `.ui` 파일 0개
> 개정 1: 2026-07-06 — 5절(추출 대상 정량 실측)·7절(그 외 정리 대상과 효과) 추가
> 개정 2: 2026-07-06 — 6절(의도치 않은 디자인 분기 — 정규화 관점) 추가, "one-off라 추출 무의미" 판정 일부 정정, 구 6·7절 → 7·8절로 이동

---

## 개요

view 코드의 공통 UI/디자인 요소를 분리·정리하는 작업을 앞두고, 여섯 가지 질문에 답한다.

| 질문                                   | 한 줄 답                                                                                                                                                                              |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Q1. Qt Designer를 쓰면 얼마나 잘 정리되나?      | **제한적** — 파일당 정적 레이아웃은 10\~18%뿐이고, 실측된 유지보수 고통(중복·스타일 산재·동적 UI·Fat View 로직)의 대부분은 Designer가 풀지 못하는 문제                                                                               |
| Q2. Designer로 분리 가능한 요소는?            | MainWindow 셸(메뉴/액션/독/툴바), 정적 설정 폼 그룹, 탭/스플리터 골격, 정적 다이얼로그 6\~7개 — 커스텀 위젯은 promoted placeholder가 한계                                                                                  |
| Q3. Designer 없이 코드만 정리하면?            | **권장** — 이미 헬퍼 인프라 선례가 있고, 실측 중복이 전부 코드 통합으로만 해소 가능. Designer는 이후 신규 다이얼로그에 선별 도입 옵션                                                                                               |
| Q4. 공통 디자인 요소/헬퍼 추출 대상은 어느 정도인가?     | **추출 대상 약 1,340\~1,390줄, 순삭제 약 1,100\~1,150줄, 영향 파일 약 24개** (5절 실측)                                                                                                                  |
| Q5. 그 외 정리/통합/삭제/모듈화/추상화 대상과 효과는?    | 쌍둥이 통합·analyzer 베이스클래스·죽은 코드·래퍼까지 합치면 순삭제 잠재량 약 3,900\~4,700줄 + 레이어 역전 12건 제거 (7절)                                                                                                  |
| Q6. "의도치 않은 분기"까지 정규화하면 얼마나 더 단순해지나? | **가설 입증** — 인라인 색 60종 중 UI 크롬 드리프트가 \~65%로, 정규 토큰 \~15종으로 수렴 가능. 상태 표시 5방식·다이얼로그 버튼행 7/8 수동·섹션 구분 4방식 등 구성 패턴 분기도 다수. **추가 순삭제 \~250줄 + 정의 개수 대폭 축소** — 총 잠재량 약 4,100\~4,900줄로 상향 (6절) |

---

## 1. 전제 — 현재 View 코드 실측

### 1-1. 구성 방식

- `.ui` 파일 **0개** — 100% 손코딩(programmatic) UI. 모든 위젯이 `생성자 → setupUI()/setupConnections()/setModel()` 패턴 (예: `view/DashOptimizerWidget.cpp:140-161`).
- CMake는 `AUTOMOC`/`AUTORCC`만 ON — **`CMAKE_AUTOUIC` 미설정** (`CMakeLists.txt:4-5`). Designer 도입 시 빌드 설정 변경이 선행 조건.
- Qt **5.15.16** (Widgets). 전역 테마는 `resources/style/qtheme_light.qss`(1,332줄)를 `main.cpp:62-65`에서 앱 전체 적용. 전역 폰트는 Pretendard 9pt(`main.cpp:38-42`).

### 1-2. 대형 위젯 7종의 정적/동적 비율 (라인 실측 기반 추정)

| 파일 | LOC | 정적 레이아웃 | 동적 UI·로직 (지배 요소) | connect |
|---|---:|---:|---|---:|
| DashResultsAnalyzerWidget | 3,972 | \~10% | 변수 수에 따른 테이블 행+셀위젯 재생성(`:1558-1925`), 플롯 컨테이너 런타임 래핑(`:3450-3682`), CLI 수집 \~1,400줄 | 25 |
| DashMainWindow | 3,630 | \~15-18% | VTK 뷰어 생성(`:1429-1585`), OCCT 네이티브 HWND 처리(`:1586-1642`), 트리 선택→스택 전환 | 125 |
| DashGeometryParameterWidget | 3,267 | \~10% | VTK 핸들→트리 행+셀위젯 생성(`:524-661`), 모핑 탭의 인라인 connect 람다(`:711-1200`) | 34 |
| DashOptimizerWidget | 2,702 | \~15-18% | 모드 전환 시 테이블/컬럼/셀위젯 재구성(`:2077-2254`), Preview 로직 \~370줄 | 35 |
| DashModelBuilderWidget | 2,506 | \~15% | **파라미터 스키마 순회 → 타입별 폼 행 동적 생성**(`:1053-1167`), 헤더 체크박스 수동 배치 트릭(`:263-289`) | 35 |
| DashModelRunnerWidget | 2,471 | \~12% | 행 단위 위젯 팩토리(`:2087-2246`), setModel 바인딩 \~154줄 | 29 |
| DashAnalysisLauncherWidget | 2,369 | \~18% | **setModel 437줄**(disconnect→reconnect 대량, `:149-585`), 샘플링 모드별 테이블 재구성(`:1704-1975`) | 82 |

핵심: **각 파일 코드량의 절반 이상이 (a) 런타임 데이터 기반 위젯 생성, (b) 커스텀 네이티브 뷰어, (c) 인라인 connect 람다, (d) setModel 데이터바인딩** — 전부 `.ui`로 옮길 수 없는 성격이다.

### 1-3. 실측된 중복 카탈로그 (정리 대상의 실체 — 정량은 5·6·7절)

| # | 중복 | 규모 | 근거 |
|---|---|---|---|
| 1 | `createSectionLabel`/`createSectionHeader` **로컬 정의 복사본** | **16개 파일** (공용 헬퍼 `ModelBuilderUIHelper`가 있는데 실사용은 위임 래퍼 2곳뿐) | `DashOptimizerWidget.cpp:163` = `DashResultsAnalyzerWidget.cpp:134` 등 verbatim |
| 2 | `createMainButton`(+`Layout`) 로컬 정의 복사본 | 12개 파일 (`#34BDFF` 버튼 스타일 문자열 포함 통째 복붙) | `DashAnalysisLauncherWidget.cpp:108` 등 |
| 3 | `QSplitter::handle` 흰색 스타일 raw-string | **22블록/9개 파일** (`DashPlotWidgetFactory.cpp` 단독 9블록) | grep `QSplitter::handle` |
| 4 | 인라인 `setStyleSheet` | **195건/26파일** — 반복 그룹 \~90건 + **UI 크롬 드리프트 후보 다수** (6절에서 재분류) | 1-4절 참조 |
| 5 | QTableWidget 컬럼 보일러플레이트 | 테이블 셋업 63회/23파일, 설정 클러스터 232회 | |
| 6 | 셀 내 체크박스 센터링 컨테이너 | 17회/3파일 | |
| 7 | analyzer GL 위젯 **11종(2D) 골격 복붙** — 동일 멤버·동일 메서드를 상속 없이 각자 보유 | 공통 베이스클래스 부재 (mixin `DashExportable`만 존재) | `DashBoxWidget.h:74-93` ≈ `DashScatter2DWidget.h:123-134` |
| 8 | MCU/비-MCU 쌍둥이 위젯 | Builder 쌍은 **진성 쌍둥이(중복 70\~75%)**, Runner 쌍은 부분 쌍둥이 — 7-1절 정밀 비교 | 로드맵 4-3절 |
| 9 | `getStatusIcon` (상태→svg 매핑) **바이트 동일 사본 4개 + 독립 변종 1개** | 5파일 | `DashAnalysisLauncherWidget.cpp:94`, `DashDoeCasesWidget.cpp:119`, `DashModelBuilderWidget.cpp:1901`, `DashModelBuilderMCUWidget.cpp:1613` + `DashMeshQualityDialog.cpp:194` |

### 1-4. 스타일 산재 — "테마는 있는데 안 쓰는" 상태

- `qtheme_light.qss`에 팔레트가 정의되어 있음 (강조 `#34BCFF`, 외곽선 `#E5F0F6`, 보조배경 `#F9FBFC` 등, 파일 상단 주석).
- 그러나 인라인 195건은 이를 무시하고 별도 색을 하드코딩: `#34BDFF`(**팔레트와 1자리 오타 — 28회 전파**, 6-1절), `#0078D4`(AboutDialog), `#E6E6F0`, `#FFFF99`, `#dcdcdc` 등.
- 이 문제의 소속은 **QSS/토큰 체계**이지 Designer가 아니다 — Designer로 폼을 옮겨도 인라인 스타일 문자열은 `.ui` 안의 `<string notr="true">` 속성으로 자리만 바꿀 뿐 중복은 그대로 남는다.

---

## 2. Q1 — Qt Designer를 쓰면 얼마나 잘 정리되나

### 2-1. 정량 추정

- `.ui`로 옮길 수 있는 것은 1-2절의 "정적 레이아웃" 열 — 대형 위젯 기준 **파일당 10\~18%**.
- view 전체로 보면: 정적 다이얼로그(6\~7개)와 셸/폼 그룹까지 최대한 옮겨도 **view LOC의 대략 15\~20% 이전**이 상한. 나머지 80%+는 동적 생성·커스텀 렌더링·바인딩·도메인 로직이라 그대로 남는다.
- 옮겨진 코드도 "삭제"가 아니라 "형태 변환"(C++ → XML)이다. 파일 수는 오히려 늘어난다 (`.ui` + 여전히 필요한 `.h/.cpp`).

### 2-2. Designer가 풀지 못하는 문제 (이 프로젝트의 실제 고통 지점)

| 실측된 문제 | Designer 효과 |
|---|---|
| 로컬 복사본 16+12개 (5-1·5-2절) | X — `.ui`로 옮겨도 각 폼에 라벨+아이콘 조합이 복제됨. 해법은 공용 위젯/헬퍼 통합 |
| 인라인 스타일 195건 산재 + 색 60종 드리프트 (1-4절·6-1절) | X — QSS 셀렉터/토큰 체계 문제 |
| analyzer GL 11종 골격 복붙 (7-2절) | X — `paintGL` 커스텀 렌더링은 Designer 대상 자체가 아님. 베이스클래스 추출 문제 |
| 데이터 주도 동적 폼 (`createModelConfigUI` 등) | X — 정적 XML로 표현 불가 |
| MCU 쌍둥이 중복 (7-1절) | X — 쌍둥이 통합은 코드 리팩터링 |
| Fat View — 위젯 안의 도메인 로직 (로드맵 4-2절) | X — 오히려 "레이아웃만 밖으로 빼고 로직은 남는" 착시 위험 |
| VTK/OCCT 네이티브 뷰어 | 부분 — promoted widget placeholder가 한계. OCCT의 `WA_NativeWindow`+HWND z-order 처리(`DashMainWindow.cpp:1591-1642`)는 코드 필수 |

### 2-3. Designer가 실제로 잘하는 것 (공정한 평가)

- **시각적 미리보기** — 실행 없이 레이아웃 확인. 폼 수정의 반복 주기가 짧아짐.
- **메뉴/액션/독 배치** — QMainWindow 셸은 Designer의 정통 영역. `DashMainWindow.cpp:106-266`(메뉴 160줄)+`:272-482`(독/스택 210줄)은 `.ui` 1장으로 깔끔히 대체 가능.
- **신규 정적 다이얼로그** — 앞으로 만들 설정류 다이얼로그는 `.ui`가 손코딩보다 빠르고 검토도 쉽다.
- **탭/스플리터/폼 그룹 골격** — `createOptimizationSettingsGroup`(`DashOptimizerWidget.cpp:640-716`) 같은 label+combo+lineEdit 그리드 폼.

### 2-4. 도입 비용

- `CMAKE_AUTOUIC ON` + 기존 손코딩 폼의 `.ui` 재작성 (변환 자동화 도구 없음 — 전부 수작업 재구축).
- `setupUI()`를 헤집는 과정에서 위젯 멤버 포인터·connect 대상이 전부 바뀌므로, **폼당 회귀 테스트 부담**이 리팩터링과 동급.
- 위젯 구성이 조건 분기되는 곳(`DashResultsAnalyzerWidget::setupUI`의 `switch(m_viewType)`, `:288-372`)은 viewType별 `.ui` 변형 5장이 필요 — 오히려 중복이 늘어난다.

---

## 3. Q2 — Designer로 분리해낼 수 있는 요소 카탈로그

계층별 판정 (A = 즉시 이득, B = 골격만, C = 불가):

### A. 분리 최적

| 요소 | 위치 |
|---|---|
| MainWindow 메뉴/액션/단축키 | `DashMainWindow.cpp:106-266` |
| 독 위젯 4\~5개 배치 + 중첩 QMainWindow + QStackedWidget 등록 | `DashMainWindow.cpp:272-482` |
| 아이콘바(QToolBar)·상태바 | `DashMainWindow.cpp:1864-1940` |
| 정적 설정 폼 그룹 | `DashOptimizerWidget.cpp:640-716`, `DashAnalysisLauncherWidget.cpp:901-1091` |
| 정적 다이얼로그 | AboutDialog, SolverSettingsDialog, DashMeshQualityDialog, ShortcutsDialog (전부 200\~300줄급 — 이득 자체는 작음) |
| 탭 컨테이너 골격 | Optimizer/ModelBuilder/ModelRunner/AnalysisLauncher의 `setupUI` 탭 조립부 |

### B. 골격만 (.ui 쉘 + 코드/promoted 병행)

- 테이블 헤더·컬럼 resize 정책 (헤더 라벨은 `.ui`, 정책은 코드)
- KPIConfigDialog·MaterialSetupDialog (쉘만 — 내용은 동적 교체)
- 커스텀 위젯 삽입 지점: `DashResultsAnalyzerWidget` 임베드 3곳, `DashReferenceFileWidget`/`DashDoeCasesWidget` — **promoted widget**으로 placeholder 등록
- DashTitleBar (레이아웃은 정적이나 창관리 로직 강결합)

### C. 분리 불가 (코드 유지 필수)

- 런타임 행/셀 위젯 생성 전부 (1-2절 "동적 UI" 열)
- VTK/OCCT 뷰어와 그 위 플로팅 오버레이 (`DashViewOptionsWidget` — `raise()`+수동 위치)
- overlay/ 전체 (드래그 가능 플로팅 위젯: `DashMorphingBar`, `DashMorphingSettings` 1,863줄)
- analyzer GL/VTK 플롯 위젯 11+2종 (커스텀 렌더링)
- `setModel` 데이터바인딩·인라인 connect 람다
- TopOptPostprocessDialog (2,208줄 — VTK+파싱+JSON 생성이 지배)

---

## 4. Q3 — Designer 없이 코드만 정리하는 접근

### 4-1. 이미 절반쯤 와 있다 — 기존 인프라 선례

| 인프라 | 제공 | 문제 |
|---|---|---|
| `view/builder/ModelBuilderUIHelper` | `createSectionLabel/createMainButton/createMainButtonLayout` (static) | **실사용은 위임 래퍼 2곳뿐** — 나머지는 로컬 복사본 (5-1·5-2절) |
| `model/builder/ModelBuilderLabelTableHelper` | `populateIoTable/updateLabelTable/moveSelectedLabels/…` | **MCU Builder만 위임** — 비-MCU Builder는 동일 로직 약 400줄을 인라인 유지 (7-1절) |
| `view/analyzer/DashAnalyzerUtils` | `PlotFont/PlotLayout/PlotSpacing/PlotColors` **디자인 토큰 네임스페이스** + 플롯 유틸 | 플롯 영역에 한정 — 전역 색 토큰은 부재 |
| `view/analyzer/DashAnalyzerHelpers` | `ButtonIconEventFilter`(hover 아이콘 스왑 정본), `ZoomableScrollArea` | 같은 개념의 `IconHoverEventFilter`가 2개 파일에 별도 구현 (5-7절) |
| `view/analyzer/DashPlotWidgetFactory` | 플롯 설정 패널 15종 static 팩토리 | 내부에 스플리터 스타일 9블록 등 자체 중복 (7-3절) |
| `DashInfoIconWidget::createInfoIcon` | 정보 아이콘 헬퍼 | 정상 작동 사례 |
| `DashWheelScrollSuppressor` | 휠 스크롤 억제 | `main.cpp:34-35`에서 **앱 전역 설치 완료** — 추가 조치 불필요 |

즉 "코드 정리" 방향은 새 발명이 아니라 **이미 정착된 패턴의 일관화**다. MCU Builder가 헬퍼 위임의 성공 사례를 이미 증명하고 있다. 플롯 서브시스템(`PlotFont` 토큰, tab10 팔레트)은 **이미 정규화된 모범 사례**로, 6절 정규화 논의에서 "의도된 특화"로 분리해 보존해야 한다.

### 4-2. 정리 작업의 세 축

- **축 1 — 공통 디자인 요소/헬퍼 추출** (Q4): 5절에서 항목별 정량 실측. **순삭제 약 1,100\~1,150줄 / 영향 파일 약 24개 / 전부 저위험 기계적 치환.**
- **축 2 — 의도치 않은 분기의 정규화** (Q6): 6절. 동일 문자열 중복이 아니라 "같은 의도의 변종"을 정규형으로 수렴. **추가 순삭제 \~250줄 + 정의 개수 대폭 축소(색 60→15종 등) + 시각 언어 통일.**
- **축 3 — 구조적 정리** (Q5): 쌍둥이 통합, 베이스클래스 추출, 죽은 코드 삭제, 래퍼 표준화, 레이어 역전 해소. 7절. **추가 순삭제 약 2,800\~3,500줄 + 아키텍처 이득.**

### 4-3. 한계

- 코드 정리는 시각적 미리보기를 주지 않는다 — 폼 수정 시 빌드+실행 확인은 여전히 필요.
- 헬퍼가 늘어나면 "어디에 뭐가 있는지" 발견 가능성 문제가 생김 → 공용 헬퍼를 `view/common/` 한 곳으로 모으고 새 폼 작성 규칙을 문서화해야 함.

---

## 5. Q4 — 공통 디자인 요소/헬퍼 추출 대상 정량 실측

측정 방법: ripgrep 기반 전수 카운트 + 정본 대비 샘플 diff (재현 명령은 각 항목에 병기). 대상: `view/` 49개 .cpp / 51개 .h.

### 5-1. `createSectionLabel`/`createSectionHeader` — 16개 복사본, \~369줄

정의 총 19개 = 정본 1(`ModelBuilderUIHelper.cpp:13-35`) + 위임 래퍼 2(`DashModelBuilderMCUWidget.cpp:103`, `DashPlotWidgetFactory.cpp:45`) + **완전 복사본 16**. 본문은 verbatim 동일(bold 라벨 + `label_bullet.svg` base64 임베드) — 4개 샘플 대조로 확인.

| 파일 | 라인 | LOC |
|---|---|---:|
| DashAnalysisLauncherWidget.cpp | 69-92 | 24 |
| DashDataProcessorWidget.cpp | 94-116 | 23 |
| DashConditionParameterizationWidget.cpp | 84-106 | 23 |
| DashDoeCasesWidget.cpp | 95-117 | 23 |
| DashGeometryParameterCADWidget.cpp | 100-122 | 23 |
| DashGeometryParameterWidget.cpp | 111-133 | 23 |
| DashModelBuilderWidget.cpp | 78-100 | 23 |
| DashModelRunnerMCUWidget.cpp | 64-86 | 23 |
| DashModelRunnerWidget.cpp | 75-97 | 23 |
| DashOptimizerWidget.cpp | 163-185 | 23 |
| DashReferenceFileWidget.cpp | 90-112 | 23 |
| DashResultsAnalyzerWidget.cpp (`createSectionHeader`) | 134-156 | 23 |
| dialog/TopOptPostprocessDialog.cpp | 402-424 | 23 |
| dialog/DashMeshQualityDialog.cpp | 160-182 | 23 |
| dialog/ShortcutsDialog.cpp | 85-105 | \~20 |
| dialog/MaterialSetupDialog.cpp | 315-337 | 23 |

**추출 대상 \~369줄 → 순삭제 \~350줄** (헬퍼 호출 1줄 치환).

### 5-2. `createMainButton`(+`Layout`) — 12개 복사본, \~441줄

`#34BDFF/#2A9FD9/#1F7FB3` 3상태 파란 버튼(+run 아이콘) 정의가 12개 파일에 복붙 (버튼 \~27줄 x 12 = \~324, 레이아웃 13줄 x 9 = \~117). 다이얼로그 3개(MeshQuality/MaterialSetup/TopOptPostprocess)는 버튼만 보유. **순삭제 \~415줄.**

### 5-3. `QSplitter::handle` 스타일 블록 — 22블록/9파일, \~133줄

내용은 전부 동일(`handle{#FFFFFF}, vertical{1px}`). `DashPlotWidgetFactory.cpp` 단독 9블록. `applyThinSplitterStyle(splitter)` 헬퍼 1개로 치환 시 **순삭제 \~111줄.**

### 5-4. 셀 위젯 센터링 컨테이너 — 17회/3파일, \~72줄

`QWidget`+`QHBoxLayout`+`setContentsMargins(0,0,0,0)`+`setAlignment(AlignCenter)` 조합. GeometryParameter 3회, ResultsAnalyzer 4회, PlotWidgetFactory 10회. `centeredCell(widget)` 치환 시 **순삭제 \~55줄.**

### 5-5. 테이블 설정 보일러플레이트 — 클러스터 232회/21파일

`setHorizontalHeaderLabels` 63회 직후의 설정 클러스터: `setSectionResizeMode` 162, `verticalHeader()->setVisible(false)` 27, `setSelectionBehavior` 34, `setEditTriggers` 9. 정본 성격의 `createStyledTable`이 이미 존재하나(`DashResultsAnalyzerWidget.cpp:158-186`) analyzer 모듈만 사용. 컬럼 스펙 리스트를 받는 헬퍼로 확장 적용 시 **순삭제 \~120\~150줄(보수적).**

### 5-6. 인라인 `setStyleSheet` 195건의 분해 — 1차 분류

| 그룹 | 내용 | 발생 | 추출 가치 |
|---|---|---:|---|
| A. 액션버튼 액센트 (#34BDFF 계열) | 참조 28회 (13은 5-2절 본문 내) | \~20 | 높음 — 5-2절과 함께 해소 |
| B. QSplitter 얇은선 | 5-3절과 동일 | 22 | 높음 — 5-3절과 함께 해소 |
| C. 테이블 헤더/섹션 스타일 | `QHeaderView::section` 등 | \~40-50 | 높음 — 5-5절과 함께 해소 |
| D. QScrollBar 커스텀 | | 3 | 낮음 |
| E. 리셋 `setStyleSheet("")` | 하이라이트 해제 (전량 DashMorphingSettings) | 18 | 없음 |
| F. 문맥 전용 one-off | 라벨색·상태 표시 등 | \~85-90 | (개정 1 판정) 없음\~낮음 → **개정 2에서 정정: 6절 참조** |

**개정 2 정정**: 개정 1에서는 F그룹 \~85-90건을 "유니크라 추출 무의미"로 분류했으나, 6절의 재조사 결과 **플롯 데이터 색/폰트(의도된 특화)를 분리하고 나면 나머지의 약 65%는 의도 패밀리 5\~6개로 수렴하는 드리프트**로 재판정되었다.

### 5-7. hover 아이콘 스왑 필터 — 동일 개념 3중 구현, \~96줄

정본 `ButtonIconEventFilter`(`DashAnalyzerHelpers.cpp:21-41`)가 있는데, `IconHoverEventFilter`라는 거의 동일한 로컬 클래스가 `DashOptimizerWidget.cpp:65-112`와 `dialog/TopOptPostprocessDialog.cpp:65-112`에 각각 \~48줄씩 별도 정의. 통합 시 **순삭제 \~70줄.**

### 5-8. 총계 (Q4의 답)

| 항목 | 추출 대상 LOC | 순삭제 LOC | 영향 파일 |
|---|---:|---:|---:|
| 5-1 섹션 라벨 | \~369 | \~350 | 16 |
| 5-2 메인 버튼(+레이아웃) | \~441 | \~415 | 12 |
| 5-3 스플리터 스타일 | \~133 | \~111 | 9 |
| 5-4 센터링 컨테이너 | \~72 | \~55 | 3 |
| 5-5 테이블 보일러플레이트 | \~232 | \~120 | 21 |
| 5-7 hover 필터 | \~96 | \~70 | 2 |
| 5-6 스타일 추가 여력 | (위 항목에 흡수) | \~30-50 | — |
| **합계** | **\~1,340-1,390** | **\~1,100-1,150** | **유니크 \~24** |

전부 "본문 삭제 → 헬퍼 호출 1줄" 형태의 **기계적 치환**이라 파일 단위로 쪼개 진행 가능하고 회귀 위험이 낮다.

---

## 6. Q6 — 의도치 않은 디자인 분기: 정규화 관점의 추가 단순화 (개정 2)

### 6-0. 관점 전환과 판정 기준

5절은 "**동일 문자열** = 중복"만 세었다. 이 절은 관점을 뒤집는다: **"같은 의도인데 다르게 구현된 변종(drift)"**을 세고, 정규형으로 수렴했을 때의 단순화를 추정한다. 가설 — 분기 대부분은 특화 디자인의 의도가 아니라 개별 작업이 중구난방으로 진행된 산물이다 — 은 아래 실측으로 **입증**되었다.

판정 기준: **의도된 특화 vs 드리프트**를 먼저 갈라야 한다. 이 코드베이스에서 의도된 특화로 보존할 것은 명확히 식별된다:

- **플롯 데이터 팔레트** (matplotlib tab10 — `#D62728`, `#FF7F0E`, `#1F77B4`, `#2CA02C` 등 11색, `DashBoxWidget.cpp:22-25` 외): 차트 시리즈 색은 데이터 시각화 규약.
- **플롯 폰트 토큰** (`PlotFont` Title/Label/Small 3계층, `DashAnalyzerUtils.h:23-27`): analyzer 서브시스템은 **이미 정규화 완료** 상태.
- QSS 특화색 3종 (타이틀바 `#002060`, 닫기 `#E81123`, 렌더 폴백 `#D3DDE1`).

이들을 제외한 **UI 크롬(버튼·라벨·테두리·배경·하이라이트)의 분기 약 65%가 드리프트**다.

### 6-1. 색상 드리프트 — 60종 → 정규 토큰 \~15종

view .cpp의 hex 색상 전수: **고유 60종**(6자리 53 + 3자리 7). 반면 qss 정규 팔레트는 8종. 의미 클러스터별 실측:

| 클러스터 | 현재 변종 | 정규화 후 | 드리프트 증거 |
|---|---:|---:|---|
| 파랑(액센트 의도) | **9종** — #34BDFF(28회)·#2A9FD9(18)·#1F7FB3(15)·#34BCFF(1)·#0078D4/#106EBE/#005A9E(AboutDialog)·#2196F3(ViewOptions 토글)·#0099FF/#0088EE/#0077DD | 3종 (액센트+hover+pressed) | **#34BDFF는 정규 액센트 #34BCFF의 1글자(BC→BD) 오타가 28회 전파된 것** (`ModelBuilderUIHelper.cpp:49` 발원). AboutDialog는 MS Fluent 블루를 별도 채용 |
| 회색(테두리/비활성/보조텍스트) | **\~18종** — 테두리 의도만 #A0A0A0·#D0D0D0·#CCCCCC·#CCC·gray·#888·#C7E4F5·#DCDCDC·#DFE3EB 9종 | 5종 (테두리1+텍스트2+배경2) | 정규 외곽선은 qss `#E5F0F6` 1색인데 인라인은 전부 다른 회색. #333333과 #333 같은 색의 3/6자리 표기 혼용 |
| 하이라이트/틴트 배경 | **7\~8종** — #E6E6F0·#FFFF99·#EAF6FF·#E8F8FF·#CCF0FF·#CCE8FF·#D6EAF8·#E0E8F0 | 2종 (편집강조+선택틴트) | `DashMorphingSettings.cpp`의 #FFFF99 4곳은 변수명부터 `highlighStyle`(오타)↔`highlightStyle`로 갈리고 세미콜론 유무도 분화 — **의도 없는 변종의 전형** |
| 빨강(에러/삭제) | 3종 (red·#FF4242·#FF4D4D) + qss #E81123 | 1종 | `color: red` 삭제버튼 스타일이 2파일에 동일 복붙 |
| 플롯 tab10 | 11종 | **유지** (의도) | — |

**정규화 효과: 색 정의 60종 → UI 크롬 \~15종** (QSS 5토큰 + 특화 4 + 파생 \~6) **+ 플롯 11종 보존.** exact-dup 스타일 문자열 3쌍(QHeaderView 섹션: `DashAnalyzerUtils.cpp:257` ≡ `DashResultsAnalyzerWidget.cpp:180` 등)도 상수 공유로 즉시 흡수.

### 6-2. 레이아웃 상수 드리프트 — 스케일 부재

값 분포 실측 (`grep -rhoE "setSpacing\([0-9]+\)" view` 등):

| 상수 | 값 분포 (빈도) | 판정 |
|---|---|---|
| `setSpacing` | **5(51)·10(31)·0(25)·4(15)·8(6)·2(6)·3(2)·15(2)·20(2)** — 고유 9값 | 5↔4, 10↔8이 같은 의도의 분화. 정규 스케일 {0,4,8,12} 4단계로 수렴 가능 |
| `setContentsMargins` | (0,0,0,0) 152회 지배 + 변형 20여 종 ((10,0,0,10) 22회, (2,2,2,2)/(10,10,10,10)/(4,4,4,4)/(5,5,5,5)/(15,15,15,15)…) | 제로마진 외에는 파편화 — 콘텐츠 마진 2\~3단계로 수렴 가능 |
| `setFixedHeight` | **30(18회 지배)**·24(6)·28(1)·29(1) | 버튼 높이 30 대세에 24/28/29 이탈 — 2단계(표준/컴팩트)로 수렴 |
| `setIconSize` | **16x16(22회 지배)**·12x12(6)·14x14(2)·기타 3 | 리소스 폴더(svg_12px 47참조/svg_14px 19/svg_16px 14)와 느슨한 대응 — 2\~3단계로 수렴 |
| `font-size`(스타일시트) | **11px(12회 지배)**·12px(3)·10px(1)·20px(1) | pt(전역 Pretendard 9pt)와 px 혼용이 잠재 리스크 |

LOC 절감은 작지만(값 교체가 대부분), **1단계 헬퍼(5절)의 기본값으로 흡수되면 호출부 설정 라인 자체가 사라지고**, 이후 새 코드가 스케일을 벗어나기 어려워진다.

### 6-3. 구성 패턴 드리프트 — 같은 역할, 화면마다 다른 구현

역할별 "변종 수 → 정규형 수" 실측:

| 역할 | 현재 변종 | 정규형 | 실측 근거 |
|---|---|---:|---|
| 주 실행 버튼 | 13개 구현 (전부 시각 동일 — 12 인라인 복붙 + 정본) | 1 | 5-2절과 동일 대상 |
| 상태 아이콘 매핑 `getStatusIcon` | **바이트 동일 4사본 + 독립 변종 1** (MeshQuality는 색까지 별도 정의) | 1 | `DashAnalysisLauncherWidget.cpp:94` 외 |
| **실행 중(진행) 표시** | **5방식** — 테이블 아이콘 / 버튼 텍스트 교체("Fitting...", `DashOptimizerWidget.cpp:2415`) / 스피너(`DashMainWindow.cpp:1869`) / 퍼센트 문자열(`TopOptPostprocessDialog.cpp:1790`) / **QProgressBar는 view 전체 0건** | 1\~2 | 진행 피드백이 모듈마다 다른 UX |
| 다이얼로그 버튼행 | **8개 중 7개 수동 조립** (표준 `QDialogButtonBox`는 KPIConfigDialog 1개뿐) — 순서·정렬·stretch 제각각. `DashMeshQualityDialog.cpp:78-91`은 정규 헬퍼와 동일 구성을 손으로 재조립(헬퍼 미인지 증거) | 1 | |
| 소형 도구 버튼 (+/-, ▲▼) | **4변종** — ▲▼ 30x30 가로(DataProcessor·ModelBuilder) vs +/- 25x25 세로(Optimizer) | 1 | 같은 "행 추가/삭제"가 화면마다 다른 모양·크기 |
| 아이콘 전용 투명 버튼 | \~3 인라인 패턴 (19건/5파일) | 1 | `TopOptPostprocessDialog.cpp:169-181` 등 |
| 섹션 구분 | **4방식** — bullet-bold 라벨(지배) / QGroupBox(24건, MorphingSettings 17건 집중) / QFrame HLine·VLine / 커스텀 배경 라벨 | 1\~2 | 같은 앱에서 섹션이 두 가지 이상의 시각 언어 |
| 폼 행(라벨+입력) | 3방식 — QHBoxLayout 수동(171건/27파일, **95%**) / QGridLayout(10) / **QFormLayout(9건, 5%)** | 1\~2 | 정규 Qt 도구가 사실상 미채택 |
| 볼드 라벨 | `setBold(true)` 35회, 조립 3변형 | 헬퍼 1 | |

### 6-4. 정규화 효과 정량 (Q6의 답)

**(a) 정의 개수 축소 — 이 관점의 본질적 이득:**

| 항목 | 현재 | 정규화 후 |
|---|---:|---:|
| 색 정의 (UI 크롬) | \~49종 | **\~15종** |
| 간격 스케일 | 9값 | 4값 |
| 버튼 높이 | 5값 | 2값 |
| 아이콘 크기 | 6값 | 2\~3값 |
| 진행 표시 방식 | 5방식 | 1\~2방식 |
| 섹션 구분 방식 | 4방식 | 1\~2방식 |
| 다이얼로그 버튼행 | 7변종 | 1방식 |

**(b) 추가 순삭제 LOC (5·7절과 비중복 신규분):**

| 대상 | 순삭제 |
|---|---:|
| `getStatusIcon` 사본 4+1 통합 | \~40 |
| 볼드 라벨 헬퍼화 (35회) | \~70 |
| 소형 도구 버튼 정규화 | \~30 |
| 아이콘 전용 버튼 정규화 | \~40 |
| 다이얼로그 버튼행 → QDialogButtonBox | \~60 |
| exact-dup 스타일 상수화 | \~15 |
| **소계** | **\~250** |

**(c) 비용 — 시각 변화 회귀 확인 지점 ≈ 25\~30곳:** #34BDFF→#34BCFF(28곳)는 사실상 무감이지만, AboutDialog 블루 2곳·ViewOptions 토글 1곳·회색 테두리 \~12곳·하이라이트 틴트 \~8곳은 눈에 보이는 변화라 **스크린샷 대조 확인**(또는 고객사 빌드 분기 확인)이 필요하다. 이것이 5절(무감 치환)과의 결정적 차이 — 정규화는 "보이는 것을 바꾸는" 작업이 일부 포함된다.

### 6-5. 판정 요약

- **가설 채택**: "one-off \~85-90건"의 재분류 결과, 플롯 특화를 제외한 UI 크롬 분기의 **약 65%는 드리프트**. 오타 전파(#34BDFF 28회), 오타 변수명(`highlighStyle`), 헬퍼 재발명(MeshQuality 버튼행) 등 "의도 없음"의 직접 증거 다수.
- 단, **analyzer 플롯 서브시스템은 예외** — 이미 토큰화된 모범 사례이므로 정규화 작업에서 제외(건드리면 오히려 후퇴).
- LOC로는 +250줄이지만, 실질 가치는 **정의 개수 축소와 시각 언어 통일**(같은 기능이 화면마다 다르게 보이는 4개 지점 해소), 그리고 신규 코드가 참조할 정규형의 존재다.

---

## 7. Q5 — 그 외 정리/통합/삭제/모듈화/추상화 대상과 효과

### 7-1. 쌍둥이 위젯 통합 — 최대 단일 절감원

세 쌍을 정밀 비교한 결과, **판정이 쌍마다 다르다**:

| 쌍 | 관계 판정 | (a)verbatim/(b)준동일 중복 | 절감 추정 | 난이도 |
|---|---|---|---:|---|
| Builder: `DashModelBuilderWidget`(2,506) vs MCU(2,514) | **진성 쌍둥이** (복붙 후 개변) | **70\~75%** — 공통명 메서드 \~51개, `onStopTrainingClicked` verbatim, `getModelConfiguration` 85% 동일 등 | **\~1,300-1,700줄** | 중 |
| Runner: `DashModelRunnerWidget`(2,471) vs MCU(1,207) | 부분 쌍둥이 (surrogate 테이블+오차지표 코어만 공유, 워크플로는 상이) | 코어 한정 \~90% (`createSurrogateTableRow` 95% 동일) | **\~350-450줄** | 중하 |
| Geometry: `DashGeometryParameterWidget`(3,267) vs CAD(1,035) | **쌍둥이 아님** — 핸들 모핑 에디터 vs CAD 파라미터 테이블, 모델 계층도 별개, 코딩 스타일도 상이(독립 저작) | 2\~3% (전역 보일러플레이트뿐) | 통합 대상 제외 | — |

Builder 통합의 구조적 근거: model 계층이 **이미 `DashModelBuilderMCU : public DashModelBuilder` 상속**(가상 override 5종)이므로, view도 template-method 베이스클래스(`DashModelBuilderWidgetBase`)가 자연스럽다. MCU 전용 요소(dataset 테이블·daemon 흐름·Manual/Smart 모드)는 가상 훅으로 처리.

Runner는 반대로 model 결합이 상속이 아니라 합성(`DashModelRunnerMCU`는 `QObject` 직속 136줄 어댑터)이라 **베이스클래스 부적합** — `SurrogateTableController` 헬퍼 추출이 정석.

**선행 무위험 항목**: 비-MCU Builder가 인라인으로 갖고 있는 `populateIoTable/updateLabelTable/moveSelectedLabels/…` 약 400줄은 이미 존재하는 `model/builder/ModelBuilderLabelTableHelper`로 위임만 하면 사라진다 — **MCU 쪽이 이미 이 방식으로 검증**해놓았다(위임 래퍼 4\~10줄).

추가: `getIOController`도 6+개 클래스에 verbatim 복붙 (클래스명만 다름).

### 7-2. analyzer GL 위젯 11종 — 베이스클래스 추출, 순 \~450-550줄

2D GL 위젯 11종(Box/Convergence/Morris/Parallel/Pareto/Pearson/Scatter2D/ShapDependence/Shap/Sobol/TimeSeries GL)이 `QOpenGLWidget`를 각자 직접 상속하며 골격을 복붙 공유:

- `generateTicks`("nice number" 알고리즘): 6곳 x 18\~25줄, 변종 단 2개 — Convergence와 Pareto는 **문자 단위 동일**. → 자유함수 1개(-110줄)
- `drawMarkerShape`: 3곳 x \~40줄, diff 결과 공백 차이만. → 유틸 1개(-80줄)
- `initializeGL`/`resizeGL`/`leaveEvent`/`paintGL` 프리앰블+마진 블록: 11종 x \~35줄 — `PlotLayout::compute` 마진 세팅 블록이 7개 위젯에 동일. → `DashPlotWidgetBase : QOpenGLWidget` 신설(-350\~450줄 순)

상수·유틸(`PlotLayout/PlotColors`, `calculateViewport`)은 이미 `DashAnalyzerUtils`로 추출되어 있으므로, 남은 것은 **메서드 골격을 담을 베이스클래스**뿐이다. 리스크: 렌더 회귀 — 위젯별 시각 확인 필요. 3D 2종(Scatter3D/Pareto3D)은 VTK 기반이라 대상 외.

### 7-3. DashPlotWidgetFactory(2,195줄) 내부 정리 — 순 \~300-400줄 (파일 15\~18% 축소)

패널 빌더 14종에서 기계적 반복 실측: 색버튼 생성 블록 10회 x \~11줄, 체크박스 셀 컨테이너 16회 x \~7줄, 스플리터 스타일 9회 x \~7줄, `setFixedHeight(...length()+...)` 공식 7회, mainLayout 프리앰블 12회 x \~4줄 = **중복 \~350-400줄**. `makeColorButton/makeCheckCell/fitTableHeight` 헬퍼화(-200\~250) + 테이블 스펙 배열 데이터 주도화(-100\~150).

### 7-4. model↔view 순환 의존 해소 — LOC보다 아키텍처 이득

- **레이어 역전**: 12개 플로터 .cpp가 view 위젯을 include하고 `plot()`에서 `new DashXxxWidget()` (`DashBoxPlotter.cpp:171` 등 전수 확인).
- **역방향 의존도 존재**: view 위젯 .h가 DTO struct 때문에 model 플로터 .h를 include (`DashBoxWidget.h:8` → `BoxData`) — **양방향 순환**.
- 정리 방식: (1) DTO를 `model/analyzer/DashPlotData.h`로 분리(순환 include 제거, 난이도 중), (2) `plot()`이 위젯 대신 데이터를 반환하고 위젯 생성을 Factory로 이관(model→view 12건 제거, **난이도 높음** — `DashResultsAnalyzerWidget` 호출부까지 파급).
- 부수: 5개 플로터의 `loadData` 8줄이 문자 단위 동일 → `DashBasePlotter::loadDataDefault()`(-32줄).
- 순 LOC 절감은 \~50-100줄로 작지만, **로드맵 Phase 5(ViewModel)의 선결 조건**인 "모델이 위젯을 만들지 않는 상태"를 만드는 작업이라 가치가 다른 축에 있다. 회귀 리스크 때문에 **독립 티켓 분리 권장**.

### 7-5. 죽은 코드 삭제 — 무위험 \~136줄

- `DashAnalysisLauncherWidget.cpp:821-907` — 주석 처리된 `updateDvTable()` 통째 \~87줄 + 헤더 선언(`.h:51`). 호출처 없음 → 즉시 삭제.
- 산발 주석 블록 4건(\~48줄): `DashMainWindow.cpp:1591-1604` 등.
- 그 외는 깨끗함: 미인스턴스화 위젯 0건, 선언만 있는 메서드 0건(샘플 검사), 백업성 파일 0건.

### 7-6. 호출 패턴 래퍼 — 순 \~160-210줄 + 일관성 이득

| 패턴 | 실측 | 정리 방식 | 효과 |
|---|---|---|---|
| `QMessageBox::warning/critical/...` | **213건/17파일** (ModelBuilderMCU 34, Optimizer 32) | `DashDialogs::warn/confirm` 정적 래퍼 | LOC 절감은 소(-\~100), **제목·부모·아이콘·언어 표준화** 이득이 본질 |
| `QFileDialog::getOpenFileName` | 30건 — QSettings 경로 기억이 비일관 (대부분 `""`) | 경로 기억 내장 헬퍼 | -30\~60줄 + UX(마지막 경로 기억) |
| start/stop 버튼 `setEnabled` 토글쌍 | ModelBuilder 6쌍 등 반복 | `setRunningState(bool)` 헬퍼 | -30\~50줄 |
| 휠 스크롤 억제 | — | **조치 불필요** — `DashWheelScrollSuppressor`가 이미 앱 전역 설치(`main.cpp:34-35`) | — |

### 7-7. 총괄 — 전체 절감 잠재량 (Q5+Q6 합산)

| 묶음 | 순삭제 추정 | 난이도 | 리스크 |
|---|---:|---|---|
| A. 공통 UI 헬퍼 통합 (5절 전체) | \~1,100-1,150 | 하 | 기계적 치환 |
| B. 죽은 코드 삭제 (7-5) | \~136 | 최하 | 없음 |
| C. Builder→LabelTableHelper 위임 (7-1) | \~400 | 하 | MCU가 검증한 경로 |
| D. 디자인 정규화 (6절 — 상태아이콘·볼드라벨·버튼행·소형버튼 등) | \~250 | 하\~중 | **시각 변화 25-30곳 확인 필요** |
| E. Builder 쌍둥이 베이스클래스 (7-1, C 이후 잔여) | \~1,000-1,300 | 중 | 학습 플로 회귀 테스트 필요 |
| F. Runner surrogate 코어 헬퍼 (7-1) | \~350-450 | 중하 | |
| G. analyzer GL 베이스클래스 (7-2) | \~450-550 | 중 | 렌더 시각 회귀 |
| H. PlotWidgetFactory 정리 (7-3) | \~300-400 | 하\~중 | |
| I. 플로터 loadData 공용화 (7-4 부수) | \~30-100 | 하 | |
| J. QMessageBox/QFileDialog/토글 래퍼 (7-6) | \~160-210 | 하 | |
| **합계** | **약 4,100-4,900** | | |
| (별도) 레이어 역전 해소 (7-4) | \~50-100 | **상** | 아키텍처 이득이 본질 — 독립 티켓 |

- **view .cpp 47,485줄 대비 약 9\~10% 순삭제.** A+B+C(≈1,600줄)는 무위험\~저위험 구간이라 즉시 착수 가능.
- 헬퍼 복사본이 쌍둥이 파일 안에도 있으므로 A와 E 사이에 \~100줄 내외 겹침 가능 — 합계는 보수적으로 읽을 것.
- LOC 외 이득: 색 정의 60→\~15종, 진행 표시 5→1\~2방식, 섹션 구분 4→1\~2방식 등 **디자인 정의 개수의 축소**(6-4절)와 model→view 역전 12건 제거(7-4절).

---

## 8. 종합 비교와 권고

### 8-1. 세 가지 옵션

| 옵션 | 장점 | 단점 | 실측 문제(1-3절) 해소 | 판정 |
|---|---|---|:---:|---|
| A. Designer 전면 도입 (기존 폼 `.ui` 재작성) | 시각 미리보기, 신규 폼 생산성 | 재작성 비용 = 폼당 리팩터링급, 정적 부분 10\~18%만 대상, viewType 분기는 `.ui` 중복 유발, 중복·스타일·Fat View 문제 미해소 | 0/9 | **기각** |
| B. Designer 선별 도입 (MainWindow 셸 + 신규 다이얼로그만) | A의 이득을 저비용 구간에만, AUTOUIC 한 줄 | 기존 중복은 별도 코드 정리 필요 (결국 C와 병행) | 0/9 (단독으로는) | **후순위 옵션** |
| C. 코드 정리 + 디자인 정규화 (5·6·7절 실행) | 실측 중복·드리프트 전부가 대상, 선례 인프라 존재, **순삭제 \~4,100-4,900줄(9-10%)** + 정의 개수 축소, 로드맵 Phase 5와 방향 일치 | 시각 미리보기 없음, 정규화분은 시각 변화 확인 필요 | 9/9 | **권장** |

### 8-2. 권고 — C 우선, B는 이후 선택

Qt Designer는 "UI를 처음 만들 때"의 도구이지 "이미 손코딩으로 만들어진 UI의 중복을 걷어내는" 도구가 아니다. 이 프로젝트의 고통은 후자다. 또한 로드맵의 진단(view:model = 1.66배, 위젯 안의 도메인 로직)이 가리키는 진짜 문제는 **레이아웃 표현 방식이 아니라 로직의 거처**이고, Designer 도입은 이 문제를 건드리지 않으면서 전환 비용만 지불하게 된다.

실행 순서 (난이도 오름차순 — 앞 단계가 뒷 단계의 기반):

```
[0단계] 죽은 코드 삭제 (7-5) — 무위험, ~136줄
   │   1. updateDvTable 주석 블록 + 헤더 선언 삭제
   │   2. 산발 주석 블록 4건 삭제
   ▼

[1단계] 공통 헬퍼 통합 (5절) — 순삭제 ~1,500줄 / 24+파일
   │   1. view/common 신설 (또는 ModelBuilderUIHelper 개명·이전)
   │   2. 섹션 라벨 16곳·메인 버튼 12곳 → 헬퍼 호출 치환
   │   3. 스플리터 스타일·센터링 셀·테이블 설정·hover 필터·getStatusIcon 통합
   │   4. 비-MCU Builder → LabelTableHelper 위임 (~400줄, MCU 검증 경로)
   │   ※ 파일당 독립 작업 — 커밋 단위 분리, 병렬 진행 가능. 시각 변화 없음
   ▼

[2단계] 디자인 정규화 (6절) — 순삭제 ~250줄 + 정의 개수 축소
   │   1. 색 토큰 확정 (60종 → ~15종) — #34BDFF 오타 28곳, 회색 18종, 틴트 7종 수렴
   │   2. 간격/크기 스케일 확정 — 헬퍼 기본값으로 흡수
   │   3. 진행 표시·다이얼로그 버튼행·소형 버튼·섹션 구분 정규형 결정
   │   4. qtheme_light.qss 셀렉터 이전 + 팔레트 상수 네임스페이스
   │   ※ 시각 변화 25~30곳 — 스크린샷 대조 확인 필수. 플롯 서브시스템(tab10·PlotFont)은 제외
   ▼

[3단계] 구조 통합 (7-1·7-2·7-3) — 순삭제 ~2,100-2,700줄
   │   1. Runner surrogate 코어 헬퍼 (중하)
   │   2. PlotWidgetFactory 헬퍼화+데이터 주도 (하~중)
   │   3. analyzer GL 베이스클래스 (중 — 렌더 시각 회귀 확인)
   │   4. Builder 쌍둥이 template-method 베이스클래스 (중)
   │   ※ Geometry 쌍은 쌍둥이 아님 — 통합 금지 (7-1 판정)
   ▼

[4단계·별도 티켓] 레이어 역전 해소 (7-4) — 아키텍처 이득
   │   1. DTO 분리 → 순환 include 제거
   │   2. plot()의 위젯 생성 → Factory 이관 (model→view 12건 제거)
   │   ※ 로드맵 Phase 5 선결 조건 — 회귀 리스크로 독립 진행
   ▼

[5단계·선택] Designer 선별 도입
       AUTOUIC ON + 신규 다이얼로그부터 .ui 시작.
       기존 폼 소급 전환은 하지 않음 (비용 > 이득).
       1~2단계에서 만든 공용 위젯·토큰은 promoted widget으로 등록 가능
```

### 8-3. 로드맵과의 정합

- 0\~3단계는 로드맵 Phase 5(ViewModel 수렴)의 **선행 정지 작업**으로 유효 — 위젯이 얇아질수록 표현 로직을 VM으로 옮기기 쉬워진다.
- 4단계(레이어 역전)는 로드맵 4-2절이 지목한 "모델이 위젯을 만드는" 문제의 직접 해소 — Phase 5의 선결 조건.
- Designer 전면 도입은 로드맵의 "전면 QML 전환·빅뱅 재작성 비권장" 판정과 같은 이유로 기각 — 형태 전환에 비용을 쓰는 동안 실측 문제는 그대로 남는다.

---

## 다음 단계

- [ ] 0\~1단계(죽은 코드 + 공통 헬퍼 통합, \~1,600줄 무위험\~저위험)를 ticket-plan으로 Issue 생성 — 파일 단위 분할 커밋
- [ ] 2단계 디자인 정규화 — 색 토큰 15종·스케일 확정안을 먼저 합의(시각 변화 승인 주체 확인: 고객사 빌드 분기 `#ifdef DASH_BUILD_*` 영향 포함), 이후 Issue화
- [ ] 3단계는 항목별 개별 Issue (Runner 헬퍼 → Factory → GL 베이스 → Builder 쌍둥이 순)
- [ ] 4단계(레이어 역전)는 로드맵 Phase 5와 함께 별도 기획
- [ ] Designer 선별 도입(5단계)은 1\~2단계 완료 후 재평가
