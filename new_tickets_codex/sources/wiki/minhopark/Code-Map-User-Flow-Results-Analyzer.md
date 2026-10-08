# Results Analyzer — 사용자 플로우 ↔ 코드 대응

> **성격**: 독립 참조 문서. Results Analyzer 패널에서 사용자 행위 하나하나가 밟는 함수 체인의 대응표 — 수정 계획·우선순위 판정은 담지 않는다.
> **좌표 기준**: `dev` @ `4c7608e` 실측 (유효기간 있음). 패널 정본(`view/DashResultsAnalyzerWidget.*` · `view/analyzer/` · `model/analyzer/`)은 `ac6e4e6` 과 바이트 동일이고 재측정분은 호스트측 좌표다. 정적 코드 근거만 — 빌드·실행 검증 없음.

## 개요

한 클래스(`DashResultsAnalyzerWidget`)를 호스트 탭 6곳에 인스턴스로 심는 구조다. 생성자 인자 `ViewType` 하나가 타깃 콤보 구성·Method 목록·설정 수집 함수 4종을 전부 가른다. 사용자 행위는 언제나 같은 왕복이다 — 패널에서 조건을 짜고 `Plot` 으로 호스트 모델에 요청을 던지면, 모델이 되돌려준 spec 으로 패널이 직접 플롯 위젯을 만들어 `DashMainWindow` 의 plot dock 에 꽂는다. 패널이 요청자이자 수신자이고 호스트 모델은 경유지다. 3\~5절은 코드가 하는 일만, 결함은 6절 — 본문 `→ D{n}` · `→ U{n}` 이 링크다.

---

## 1. 임베드와 소유

| 호스트 | ViewType | 생성 지점 | 배치 |
|---|---|---|---|
| `DashAnalysisLauncherWidget` (Init DOE) | `AnalysisLauncher` | `DashAnalysisLauncherWidgetBase::setupAnalysisTab:159` ← `:410` | `analysisLayout` |
| `DashAnalysisLauncherResampleWidget` | `AnalysisLauncher` | 같은 함수 ← `:54` | `analysisLayout` |
| `DashDataProcessorWidget` | `DataPreprocessor` | `setupUI:505-509` | `analysisTab` 에 런타임 `QVBoxLayout` 신설 |
| `DashModelRunnerWidget` | `ModelRunner_Sensitivity` | `setupSensitivityAnalysisTab:325` | `ui->analysisLayout` |
| `DashModelRunnerMCUWidget` | `ModelRunner_Sensitivity` | `setupSensitivityAnalysisTab:312` | `ui->analysisLayout` |
| `DashOptimizerWidget` | `Optimizer` | `setupAnalysisTab:271` | `ui->analysisLayout` |

AnalysisLauncher 3 variant 중 Init·Resample 만 `DashAnalysisLauncherWidgetBase` 를 상속해 analyzer 를 얻는다 — `DashAnalysisLauncherDirectWidget` 는 `QWidget` 직상속이라 MainWindow 가 `analyzerHost` 를 null 로 넘긴다(`DashMainWindow.cpp:1256-1260`·`:1280` 주석). `ViewType` 이 생성자 필수 인자라 Qt Designer 승격이 성립하지 않는다는 주석이 세 호스트에 있다(`DashOptimizerWidget.cpp:270`·`DashModelRunnerWidget.cpp:324`·`DashModelRunnerMCUWidget.cpp:311`).

**ViewType 4종에 인스턴스 6개** — 공유 쌍이 둘이다. ModelRunner Sim ↔ MCU 는 `setModelBuilderBasePath():543` 이 가르고(MCU 만 호출 — `DashModelRunnerMCUWidget.cpp:160`. 스캔 기준 `projectPath`→`userPath` `:408` · Method 콤보에서 SHAP 제거 `:551`), Init DOE ↔ Resample DOE 는 가르는 코드가 없어 구성까지 동일하다. → D2

**화면 2면** — 패널 `.ui` 는 골격만 잡고 내용은 전부 런타임에 채운다. 설정 패널은 호스트 탭이, plot dock 은 `DashMainWindow` 가 소유하므로 패널이 만든 위젯이 자기 부모가 아닌 dock 으로 건너가는 것이 이 모듈의 기본 동작이다.

```
[우측 dock — 설정 패널 (DashResultsAnalyzerWidget)]
   targetSectionSlot   <- createSectionHeader("Target Data") + 콤보 0~3개
   methodHeaderSlot    <- createSectionHeader("Method")
   methodContainer     <- m_methodComboBox                    (.ui 정적)
   settingsScroll      <- m_stackedWidget (Method 별 패널)     (.ui 정적, stretch 1)
   bottomLayout        <- [Plot] 버튼

[중앙 plot dock — DashMainWindow 소유 (m_plotDock)]
   ZoomableScrollArea +- 플롯 위젯 (QOpenGLWidget 파생) + 버튼 오버레이 2종
   (+ 민감도 3종은 하단에 rankingTable 결합)
```

`settingsScroll` stretch 는 `.ui` 가 아니라 `setupUI:292` 에서 코드로 준다(uic 5.15 가 `.ui` 프로퍼티에서 유효한 `QBoxLayout` stretch 호출을 만들지 못한다는 주석이 근거).

| 클래스 (줄) | 담당 |
|---|---|
| `DashResultsAnalyzerWidget` (view 3,697 + `.h` 153 + `.ui` 78) | 설정 패널 정본. 타깃 스캔·변수 목록·설정 수집·플롯 창 조립. 모듈 단일 최대 파일 |
| `DashPlotWidgetFactory` (view/analyzer 2,354) | Method 별 설정 패널 10종 + 플롯 빌더 14종 |
| `DashPlotRequestHandler` (49) | command 문자열 → 빌더 디스패치 (해시 2개) |
| `DashPlotSpecBuilder` (model/analyzer 188) | settings → `{dataPath, settings}` spec 조립. 파일 기반 8 command |
| `DashDataLoader` · `DashXmlParser` (157 · 303) | 확장자 기준 JSON/XML 분기 · XML 파싱 + 리덕션 |
| `DashAnalyzerUtils` · `DashAnalyzerHelpers` (390 · 249) | 콤보 채우기·중복 차단·랭킹 표 / `ZoomableScrollArea`·아이콘 필터 |
| `DashPlotWidgetBase` (135) | `QOpenGLWidget` 파생 공통 베이스 — 뷰포트·hover·마커·틱 |
| 플로터 12종 · 플롯 위젯 13종 (`model/analyzer/Dash*Plotter.cpp` · `view/analyzer/Dash*Widget.cpp`) | `loadData → setVars → calculate` / `paintGL` + hover + export |

플롯 위젯 13종의 베이스는 3갈래다 — `DashPlotWidgetBase`(Box·Convergence·Morris·Pareto·Parallel·Pearson·Scatter2D·Shap·ShapDependence·Sobol 10종) · `QVTKOpenGLNativeWidget`+`DashExportable`(Pareto3D·Scatter3D 2종) · `QWidget` 래퍼(TimeSeries 1종). 패널 내부 컨트롤 핸들은 패널별 그룹 구조체 `DashAnalyzerPanelControls`(`view/analyzer/DashAnalyzerPanelControls.h`, 24줄)로 넘어온다 — 팩토리가 `out.<panel>.<control>` 을 채우고 위젯이 `m_methodPanels[methodName]` 으로 되읽는다.

---

## 2. 전체 동선

```
1. 패널 생성  ctor(ViewType) → setupUI() → setupMethods() — 호스트 탭 구성 시 1회
             ※ 콤보 순서는 선언 순서가 아니라 키 알파벳 순
2. 탭 진입    탭 전환/모델 이벤트 → setSetName() → initializeTargetData() 동기 스캔
             ※ 같은 키 재진입은 100ms 창 안에서 조용히 무시
3. 변수 확정  콤보 변경 → onTargetDataChanged → m_variables
             → updateMethodWidgetsWithVariables() 가 모든 패널 표를 재구축
             ※ 직전 호출과 같은 목록이면 재구축 전체를 건너뜀
4. Method    onMethodChanged(index) → 스택 이동 + 반응형 재플롯 차단
             ※ dock 의 플롯은 안 지워짐 — 화면과 패널이 어긋난 상태가 남음
5. 설정 편집  표 셀 위젯이 설정값의 정본 — 설정 모델 없음, Plot 시점에 훑어 JSON 조립
6. [Plot]    process{ViewType}Plot() → emit plotRequested(command, settings)
             · 파일 기반 3경로 → DashPlotSpecBuilder::build 동기 완결
             · 민감도 3경로   → 공유 데몬 왕복 (캐시 히트면 즉시)
             → plotSpecReady → RequestHandler::build → 팩토리 4단 파이프라인
7. 창 조립    rankingTable 분리 · SHAP 재정렬 · ZoomableScrollArea 포장 · 오버레이 부착
             → analysisResultReady → MainWindow 가 dock 위젯을 delete 하고 교체
8. 상호작용   휠 줌 0.5\~10배 · Alt+휠 · 호버 툴팁 · [Init] · [Save] PNG/CSV/JSON
             ※ 한 번 휠을 굴리면 dock 리사이즈 자동 맞춤이 멈춤
9. 반응형    스타일 → 즉시 setter · 데이터 → 200ms 디바운스 후 6단계 전체 재실행
             ※ 스핀박스는 두 경로에 모두 걸려 있음

[산출] plot dock 의 위젯 1개(휘발). AnalysisLauncher·DataPreprocessor 만 설정 JSON 에
       method 블록을 남기고, 그 블록을 되읽는 코드는 레포에 없다
```

---

## 3. 단계별 대응

### 3-1. 패널 생성

생성자는 3줄이다 — 디바운스 타이머 준비 → `setupUI()` → `setupMethods(viewType)`(`:77-87`). `specFor(viewType)`(`:232`)이 **선언적 정본**이고, `static const ViewSpec specs[]` 행 순서를 enum 선언 순서와 맞춰야 한다는 계약을 주석이 명시한다(`:230-231`).

| ViewType | primary | secondary | tertiary | Method (선언 순서) |
|---|---|---|---|---|
| `AnalysisLauncher` | `TargetResultsCombo` | `TargetSecondaryCombo` | — | Box · Pair · Scatter |
| `DataPreprocessor` | `TargetResultsCombo` | `TargetSecondaryCombo` | — | Box · Scatter · Parallel · Pair |
| `ModelRunner_Sensitivity` | `ModelBuilderCombo` | `ResponseFolderCombo` | `TrainedModelCombo` | Sobol · Morris · SHAP |
| `Optimizer` | — | — | — | Convergence · Pareto |

`Optimizer` 는 콤보가 없어도 `targetContainer` 를 무조건 추가한다 — 주석이 "결과로 남는 \~10px 하단 마진이 load-bearing spacing" 이라 적어 둔다(`:301-302`). `ComboSpec::onIndexChanged` 는 슬롯 **리스트**이고 연결 순서가 곧 호출 순서다(`:311`) — `DataPreprocessor` primary 만 2개(`onTargetDataChanged` → `updateDataPreprocessorSecondaryCombo`)를 건다. 타깃 콤보 5종(`TargetResultsCombo`·`TargetSecondaryCombo`·`ModelBuilderCombo`·`ResponseFolderCombo`·`TrainedModelCombo`)은 `objectName` 으로만 식별되고 `findChild<QComboBox*>` 로 되찾아진다 — 이 파일에서 25회. → D5

`setupMethods`(`:341`)는 스택 전량을 지우고 `specFor(viewType).methods` 를 순회해 `m_methodWidgets[m.name]` 을 채운 뒤, 그 **QMap 순회**로 콤보·스택을 같이 채우고 `connectReactiveSignals()`(`:367`)를 부른다. `m_methodWidgets` 가 `QMap<QString, QWidget*>`(`.h:123`)이라 순회는 키 알파벳 순 — 인덱스 잠금은 성립하지만 **화면 순서가 `specFor` 배열 순서가 아니다**(DataPreprocessor 선언 `Box→Scatter→Parallel→Pair` vs 실제 `Box→Pair→Parallel→Scatter` · ModelRunner 선언 `Sobol→Morris→SHAP` vs 실제 `Morris→SHAP→Sobol`). → D1

호출처는 생성자 `:86` 한 곳뿐 — 패널 묶음은 위젯 수명 동안 한 번만 만들어진다.

### 3-2. 탭 진입 — 타깃 확정

진입점은 호스트마다 다르다. 넷은 탭 전환 슬롯이고 ModelRunner 만 모델 이벤트다.

| 호스트 | 진입 지점 | 특이사항 |
|---|---|---|
| AnalysisLauncher Init · Resample | `DashAnalysisLauncherWidgetBase::onTabChanged:232-249` | `setModel:138` 에서도 1회 |
| `DashDataProcessorWidget` | `onTabChanged:1084-1101` | `setModel:400` 에서도 1회 |
| `DashOptimizerWidget` | `onTabChanged:1163`, 분석 탭 분기 `:1208-1231` | `m_isPopulating` 이면 즉시 반환 |
| `DashModelRunnerWidget` | `setChanged` 람다 `:115-128` · `QTimer::singleShot(0)` `:188-196` | 탭 전환이 아니라 모델 이벤트 |
| `DashModelRunnerMCUWidget` | `setModelBuilderBasePath:160` 직후 `:164` | MCU 전용 경로 |

`DashOptimizerWidget` 에는 `m_analyzerWidget` 이 null 일 때를 대비한 **레이아웃 인덱스 폴백**이 두 곳 남아 있다 — `analysisTab->layout()->itemAt(0)->widget()` 를 `qobject_cast` 로 되찾는다(`:712`·`:1221`).

`initializeTargetData()`(`:370`)는 ViewType 4갈래로 완전히 갈린다.

| ViewType | 스캔 대상 | 결과 |
|---|---|---|
| `ModelRunner_Sensitivity` | `{scanPath}/ModelBuilder_*` (`:408-415`) | `ModelBuilder_{setName}` 우선, 없으면 0번 → `updateModelRunnerSecondaryCombo()` |
| `Optimizer` | `{모듈디렉토리}/optimum.json` 의 `meta.item` (`:432-481`) | 콤보 없이 `m_variables` 만 (`"id"` 제외) |
| `DataPreprocessor` | `{userPath}/DataPreprocessor_*` (`:494-507`) | → `updateDataPreprocessorSecondaryCombo()` → `onTargetDataChanged()` |
| `AnalysisLauncher` | `{configs}/AnalysisLauncher_*.json` (`:522-526`) | → `onTargetDataChanged()` |

진입부에는 **함수-로컬 `static QHash<QString, QDateTime> recentCalls`** 기반 100ms 중복 억제가 있고(`:373-391`) 키는 `"{viewType}_{setName}"` 이다. 같은 파일의 `m_lastMethodWidgetVariables` 는 "같은 ViewType 을 공유하는 인스턴스가 있으므로 함수-로컬 static 이면 안 된다"는 이유로 이미 멤버로 옮겨졌으나(`.h:137-141`) `recentCalls` 에는 그 교정이 적용되지 않았다. → D2

ModelRunner 의 3콤보 연쇄는 `updateModelRunnerSecondaryCombo():1233` 이 `ResponseFolderCombo` 를 `blockSignals` 로 잠근 뒤 하위 디렉토리 전량을 나열하고, `model_info.json` 의 `Model upload.Input Design Variables.label` 로 `m_variables` 를 채운 다음 `updateMethodWidgetsWithVariables()` → `updateModelRunnerTrainedModelCombo():1304` 로 이어진다. 마지막 단계는 `isModelBuilderMcu():555`(= `DashProject::detectBuilderVariant(...) == "MCU"`, IOController 없으면 setName 의 `"-MCU"` 접미사로 폴백)로 확장자를 `*.h`/`*.pt` 로 정하고 응답 폴더 직속 파일 + 1단계 하위 디렉토리의 첫 파일을 모은다. `TrainedModelCombo` 는 파일명에서 확장자 길이(`extLen` = 2 또는 3)만큼 잘라 표시명을 만든다(`:1326`) — 상수로 박혀 있다.

### 3-3. 변수 목록 확정

`m_variables`(+ `m_fieldVariables`)가 이 모듈의 **데이터 계약 전부**다. 모든 패널의 변수 콤보가 이 목록에서 나온다.

| ViewType | 읽는 파일 | 읽는 키 | 코드 |
|---|---|---|---|
| `AnalysisLauncher` | `configs/AnalysisLauncher_*.json` | `DOE Table.headers` (없으면 `name`) | `:786-808` |
| `DataPreprocessor` | 선택한 `*.xml` | 첫 샘플의 `dict_item` 키 전량 | `:662-671` |
| `ModelRunner_Sensitivity` | `ModelBuilder_{Set}/model_info.json` | `Model upload.Input Design Variables.label` | `:913-938` |
| `Optimizer` | `Optimizer_{Set}/optimum.json` | `meta.item` (`"id"` 제외) | `:980-999` |

`onTargetDataChanged()` 의 `AnalysisLauncher` 분기에는 파일명 접두사로 모듈을 판별하는 5갈래 `if` 가 있으나(`AnalysisLauncher:786`·`GeometryParameter:809`·`ConditionParameter:826`·`ModelBuilder:841`·`Optimizer:858`), 콤보를 채우는 코드는 `{configs}/AnalysisLauncher_*.json` 만 나열하므로(`:522`) 아래 4갈래는 도달 경로가 없다. → U1

**필드 변수와 리덕션은 DataPreprocessor 전용이다.** `extractVariablesFromXml`(`DashAnalyzerUtils.cpp:307`)이 XML **첫 샘플**로 타입을 판정해 `XmlValue::Tensor` 이고 `!isScalar()` 면 `var (mean)`·`var (std)`·`var (max)` 3항목으로 확장, 그 외는 스칼라 1항목이며 `node_location`·`connectivity` 는 항상 제외한다(`:341`·`:376`). 파싱 실패 시 넘어가는 `QXmlStreamReader` 스트림 폴백은 `fieldVariables` 를 채우지 않는다(`:322-354`). 문서 전체를 GUI 스레드에서 파싱하며 호출처는 `onTargetDataChanged:662` 와 SHAP 데이터셋 콤보 람다(`DashPlotWidgetFactory.cpp:1058`) 둘이다. → D4

콤보 항목의 userData 는 `"변수명|리덕션"` 형식(`populateComboBoxWithVariables:295-297`)이고 이 문자열이 저장 시점까지 흐른다 — 콤보 `"Stress|Mean"` → `getVarKeyFromCombo`(widget 안 람다)가 `"Stress (mean)"` 로 settings 에 싣고 → 팩토리 `buildXxxPlot` 이 접미사를 되파싱해 reduction 을 복원하고 → `DashDataLoader::loadFromXml:116-133` 이 다시 파싱해 → `DashXmlParser::extractReducedValues` → `applyReduction` 으로 간다. `applyReduction`(`DashXmlParser.cpp:213`)의 분기는 `Max`·`Min`·`Mean` 3종(`:219-221`)이고 나머지는 `reduceMax` 폴백(`:224`) — 콤보가 내보내는 `Std` 는 이 분기에 없다. → D3

`updateMethodWidgetsWithVariables()`(`:1346`)는 진입 즉시 `m_lastMethodWidgetVariables` 와 비교해 같으면 반환하고(`:1349-1353`), 통과하면 Method 이름으로 8갈래 분기해 표를 갈아끼운다.

| Method | 하는 일 | 보존 대상 |
|---|---|---|
| Pair Plot | 변수 개수만큼 행 생성, 전부 체크 | 없음 — 통째로 재생성 |
| Scatter Plot | 기존 행의 콤보만 재채움 | 변수명 + 리덕션 |
| Parallel Plot | `Color` + 축 5행 기본 + 잔여 변수 행 추가 | 표시 텍스트 · 체크 |
| Box Plot | `max(기존 행 수, 변수 수)` 행, 앞 5행 체크 | 변수 · 체크 · 색 3종 |
| Convergence · Pareto | 표의 콤보만 재채움 | 표시 텍스트 |
| SHAP | 데이터셋 콤보 재스캔 (MCU면 `*.csv`, 아니면 `DataPreprocessor_*/**.xml`) | 파일명 |
| Morris Method | 없음 (스타일 표 제거됨) | — |

끝에서 `connectReactiveSignals()` 를 다시 불러(`:1699`) 방금 만든 셀 위젯에 반응형 시그널을 붙인다. Box Plot 의 색 버튼은 `QColorDialog` 람다를 물고 색이 바뀌면 **문자열 이름으로** 슬롯을 호출하는데(`:1560` — `QMetaObject::invokeMethod(this, "onStyleSettingChanged", Qt::QueuedConnection)`), 헤더 슬롯 선언에 `// Do NOT rename: invoked by string name` 이 붙은 이유다(`.h:66`·`:68`).

### 3-4. Method 선택

`onMethodChanged(int index)`(`:592`)는 세 줄이다 — `m_stackedWidget->setCurrentIndex(index)` · `m_activePlotWidget = nullptr` · `m_reactiveEnabled = false`. **콤보 인덱스가 곧 스택 인덱스**라는 계약으로 패널이 교체되고 반응형 재플롯이 꺼진다. 이미 dock 에 떠 있는 플롯은 지워지지 않으므로 화면의 플롯과 패널이 다른 Method 를 가리키는 상태가 정상 경로로 만들어진다. 이 인덱스 잠금은 `applyStyleToActivePlot` 이 `m_methodPanels.value(m_methodComboBox->currentText())` 로 패널 핸들을 되찾는 근거이기도 하다(`:3534` 주석).

### 3-5. 설정 편집

패널 컨트롤이 **설정값의 유일한 정본**이다. 별도 설정 모델이 없고 `Plot` 시점에 표 셀을 훑어 JSON 을 만든다.

| 컨트롤 | 읽는 방법 |
|---|---|
| View 체크박스 (0열) | `cellWidget(i,0)->findChild<QCheckBox*>()` |
| 축 라벨 (1열) | `item(i,1)->text()` — `"Color"`·`"Size"`·`"1"` 문자열 비교 |
| 변수 콤보 (2열) | `currentData()` 의 `"이름\|리덕션"`, 비면 `currentText()` 되파싱 |
| 색 버튼 | `styleSheet()` 에서 `background-color:` 추출 → D6 |
| 스핀박스 | `cellWidget(i, col)` 캐스팅 후 `value()` |
| Text Style 표 | `findChild<QWidget*>("TextStyleGroup")` → 그 안의 첫 `QTableWidget` |

색 값은 **스타일시트 문자열이 저장소**이고 읽는 쪽이 두 갈래다 — `getColorFromButton`(`DashAnalyzerUtils.cpp:22`)은 `indexOf("background-color:")` 문자열 절단, `applyStyleToActivePlot` 은 정규식(`:3564` 등 4곳)이다. 중복 선택 차단은 `setupComboBoxDuplicateCheck(table, nameColumn)`(`DashAnalyzerUtils.cpp:220`)이 `QStandardItemModel` 항목 레벨에서 처리하고 `"(none)"` 만 예외다.

### 3-6. [Plot] — 요청 왕복

```
[Plot] -> onPlotButtonClicked                                :1723
  |- currentMethod = m_methodComboBox->currentText()
  |- ViewType 4갈래  DataPreprocessor :1760 · AnalysisLauncher :2263
  |                  ModelRunner_Sens :2897 · Optimizer       :2607
  |- !processed || cliCommand.isEmpty() -> return             :1744
  |- (ModelRunner 만) settings["target_model_info_path"] 주입  :1748-1755
  +- emit plotRequested(cliCommand, settings)                 :1757
```

| ViewType | Method | command | 분기 조건 |
|---|---|---|---|
| DataPreprocessor · AnalysisLauncher | Pair / Box | `pearson` / `box` | — |
| DataPreprocessor · AnalysisLauncher | Scatter | `scatter_2d` / `scatter_3d` | 축 표 **3행의 체크박스** |
| DataPreprocessor | Parallel | `parallel` | — |
| ModelRunner | Sobol / Morris / SHAP | `sobol` / `morris` / `shap` | — |
| Optimizer | Convergence | `convergence` | — |
| Optimizer | Pareto | `pareto_2d` / `pareto_3d` | 축 표 **3행의 체크박스** |

Scatter 의 축 역할 배정은 **행 인덱스와 축 라벨 문자열의 혼합**이다(`:1983-1989`) — `i==0`→X, `i==1`→Y, `i==2 && is3D`→Z, 그 외는 `Plot Type=="Bubble"` 일 때 `axisLabel` 이 `"Color"`/`"Size"` 인지로 색축·크기축을 가린다. `x_var`·`y_var`(3D 면 `z_var` 포함)가 비면 `false` 를 반환해 요청 자체가 서지 않는다(`:1999-2002`). Parallel Plot 은 `settings.parallel.save_json_path` 에 `parallel.json` 경로를 함께 싣는다(`:2187`). → U2

Text Style 수집 코드는 **같은 20여 줄이 Method 분기마다 복제돼 있다** — `findChild<QWidget*>("TextStyleGroup")` 성공 경로와 실패 시 3열 이상 표를 찾는 폴백 캐스케이드 쌍이다. 이 파일에서 `findChild<QWidget*>("TextStyleGroup")` 은 13회(12회가 `process*Plot` 계열, 1회가 `applyStyleToActivePlot:3514`)이고, objectName 은 `createTextStyleGroup:148` 이 생성 시점에 항상 붙이므로 폴백은 도달하지 않는다. → D7

**호스트 모델 경유** — AnalysisLauncher Init·Resample(`Base:136-137`) · `DashDataProcessorWidget`(`:396-397`) · `DashOptimizerWidget`(`:134-135`) 셋은 모델의 `requestPlot` 에 직결되고, `DashModelRunnerWidget`(`:149-150`)과 `DashModelRunnerMCUWidget`(`:93-94`)만 위젯 슬롯 `onSensitivityPlotRequested`(각 `:1046`·`:754`)를 경유한다.

**파일 기반 3경로** — 모델이 spec 을 만들어 즉시 되돌린다.

```
requestPlot(command, settings)
  |- [AnalysisLauncher] updateConfigFile   DashAnalysisLauncher.cpp:1164
  |     -> DOE Analysis.method.{methodKey} 통째 교체 -> m_doeJsonPath 에 write
  |- [DataPreprocessor] updateConfigFile   DashDataProcessor.cpp:2563
  |     -> Data Analysis.method.{methodKey} 통째 교체
  |- [Optimizer] 저장 없음                  DashOptimizer.cpp:1117
  |- DashPlotSpecBuilder::build(command, configPath, xmlPath, settings, messages)
  |- messages 전량 emit logMessage · spec.isEmpty() -> return (조용한 실패)
  +- emit plotSpecReady(command, spec)
```

진입점 좌표: `DashAnalysisLauncher::requestPlot:1136`(build `:1142`·isEmpty `:1145`·emit `:1147`) · `DashDataProcessor::requestPlot:2536`(build `:2555`·isEmpty `:2558`·emit `:2560`) · `DashOptimizer::requestPlot:1117`(build `:1120`·isEmpty `:1123`·emit `:1125`).

`methodKey` 는 command 를 Python CLI 시절 키로 되돌린 것이고(`box`→`boxplot`, `scatter_2d`→`scatter2d`, `scatter_3d`→`scatter3d`, `pearson`·`parallel` 은 그대로), 같은 5줄 변환이 세 파일에 복제돼 있다 — `DashAnalysisLauncher.cpp:1186-1191`·`DashDataProcessor.cpp:2603-2613`·`DashDoeConfigManager.cpp:440-450`. 세 번째는 호출처가 없다. → D8 · U3
기록된 method 블록을 되읽는 코드는 레포에 없다 — `"DOE Analysis"`·`"Data Analysis"` 키의 전 출현이 write 경로다. → D9

`DashPlotSpecBuilder::build`(`:6`)가 만드는 것은 `{dataPath, settings}` 2키 객체뿐이고, command 8종을 처리하며 그 외는 오류 메시지를 담아 빈 객체를 반환한다(`:184-187`).

| command | `dataPath` 결정 | `settings` 로 싣는 것 |
|---|---|---|
| `scatter_2d` · `scatter_3d` · `pearson` · `box` | XML 경로 있으면 그것, 없으면 config 경로 | `settings[command]` 하위 객체 |
| `parallel` | `settings.parallel.xml_datapath` 우선 | `settings["parallel"]` |
| `pareto_2d` · `pareto_3d` · `convergence` | `settings.target_optimum_path` 우선 | `settings` 전체 |

`AnalysisLauncher` 는 XML 인자에 `QString()` 을 넘기므로(`:1142`) 항상 config 경로가 dataPath 가 되어 하류 로더가 JSON 분기를 타고, `DataPreprocessor` 만 `settings["xml_file_path"]` 를 전달해 XML 분기로 간다(`DashDataProcessor.cpp:2550-2551`). spec 조립이 실패하면 오류가 `logMessage` 까지는 흐르지만 UI 에는 아무 변화가 없다. → D10

**민감도 3경로** — 데몬 왕복이 끼어든다.

```
DashModelRunner::requestPlot(command, settings)                :929
  |- setName 비면 return · command not in {morris,sobol,shap} 이면 return :938-941
  |- 준비 여부를 묻지 않는다 — 미기동이면 host 가 lazy 기동     :943 주석
  |- inputJson = { model_path, model_config, (shap) dataset_path }
  |- displaySettings = display_options + 라우팅 키 5종          :953-969
  |     plot_type · selected_feature(_name) · selected_sample(_name)
  |- key = buildCacheKey(command, inputJson)                    :972 (정의 :294)
  |     +- 캐시 히트 -> processCachedResult -> plotSpecReady 즉시 :973-977 (정의 :305)
  +- sendSensitivityCommand -> daemon->sendCommand(line, command) :979 (정의 :322)
       v (비동기)
     onSensitivityCommandCompleted:272 -> processDaemonResponse  :341
       |- [FINISHED] 앞부분 절단(첫 '{' 앞을 버림) · NaN/Infinity -> null :366-367
       |- 파싱 실패 · "error" 키 존재 -> 로그만 남기고 return
       |- m_resultCache 적재 (MAX_CACHE_SIZE 도달 시 전량 clear)  :388-398
       +- emit plotSpecReady(command, {data, settings})          :400-402
```

데몬은 `DashManager` 가 소유하는 `DashExtensionProcess` 1개(선언 `DashManager.h:150`·생성 `.cpp:117`·접근자 `.h:229`)를 모든 러너가 공유하고, `processDaemonResponse` 첫 줄의 `m_pendingCommand.isEmpty()` 가드가 그 공유의 방어선이다 — "공유 데몬이 모든 러너에 브로드캐스트하므로 명령을 보내지 않은 러너는 무시한다"는 주석이 붙어 있다(`:343-345`).

`requestPlot` 은 데몬 준비를 묻지 않지만 `Plot` 버튼은 호스트 위젯이 게이팅한다 — `setPlotEnabled(false)` 로 시작해 `daemonReady` 에 열고 `daemonError` 에 닫으며(`DashModelRunnerWidget.cpp:163-186`·`DashModelRunnerMCUWidget.cpp:100-111`), 비활성 상태에서는 버튼 텍스트가 `"Plot (Preparing engine...)"` 로 바뀐다(`:217-225` — 비활성 버튼이 ToolTip 이벤트를 받지 못하기 때문). `daemonReady` 는 부팅당 1회뿐이라 위젯 재초기화 시 놓치므로 `isDaemonRunning()` 으로 현재 상태를 한 번 더 반영한다.

캐시 키는 `command` + `model_path` + `model_config` (+ SHAP 이면 `dataset_path`) 4개뿐이라(`:294-303`) `display_options`·`plot_type` 은 키에 없다 — 같은 모델에서 SHAP plot type 만 바꾸면 왕복 없이 캐시된 원자료로 다시 그린다. 상한은 10이고 넘치면 부분 축출이 아니라 **전량 clear** 다(`.h:234`·`.cpp:390-393`).

**spec → 위젯** — `onPlotSpecReady(command, spec)`(`:3166`)가 `DashPlotRequestHandler::build`(`DashPlotRequestHandler.cpp:8`)에 넘기면, `spec["settings"].toObject().toVariantMap()` 을 풀고 `"data"` 키가 있으면 JSON 빌더 3종(morris·sobol·shap), 없으면 파일 빌더 11종으로 간다. 매치 실패면 `nullptr` 이고 `onPlotSpecReady` 가 조용히 반환한다(`:3169-3170`). 3종은 두 해시에 모두 있고 `data` 키 유무가 유일한 갈림인데, 현재 데몬 경로로만 도달하므로 파일 빌더 쪽은 호출되지 않는다. 빌더는 전부 같은 4단 파이프라인이다.

```
buildXxxPlot(filePath, settings)                    DashPlotWidgetFactory.cpp
  1. plotter->loadData(path, inputLabel, outputLabel)   <- 확장자로 JSON/XML 분기
  2. plotter->setVars(settings)                        <- 변수명 · 스타일 흡수
  3. plotter->calculate()                              <- 정규화 · 통계 · 렌더 데이터
  4. new DashXxxWidget() + setter 체인 + setData()      <- setData 는 마지막
```

플로터는 `std::make_unique` 로 힙에 잡고("클래스 크기가 바뀌었는데 일부 TU 만 재빌드되면 스택 레이아웃이 어긋난다", `:1633-1635`) 함수가 끝나면 파괴되므로 계산 결과는 위젯 안에만 남는다. `setData()` 가 항상 마지막인 것도 주석이 근거다(`:2270-2271`).

**리덕션 접미사 되파싱**이 빌더 3곳(`buildBoxPlot:1860-1885`·`buildPearsonPlot:1921-1945`·`buildScatter2DPlot:1589-1628`)에 복제돼 있고 `DashDataLoader::loadFromXml:94` 안의 `loadVar` 람다(`:108-146`)가 또 한 번 같은 파싱을 한다 — 접미사 파싱이 위젯·팩토리·로더 3계층에 걸쳐 있다. 로더 분기 자체는 한 줄이다(`DashDataLoader.cpp:21` — `.json` 이면 `loadFromJson`, 아니면 `loadFromXml`).

민감도 3종의 랭킹 표는 빌더가 **위젯의 숨은 자식으로 실어 보낸다** — 지표 내림차순 정렬 → `createRankingTable`(`DashAnalyzerUtils.cpp:81`, objectName `"rankingTable"`) → `setParent(w)` → `hide()`. → D11

SHAP 빌더는 중요도 순 변수명을 동적 프로퍼티로 붙인다(`attachShapImportanceOrder:2204` — `setProperty("shap_var_names_by_importance", ...)`). plot type 6종 중 실제 구현은 2종이고(`buildShapWidget:2278`), `dependence` 만 전용 위젯이며 나머지 4종은 Feature Importance 로 폴백한다(`:2283-2287`). 미구현 4종은 `#ifdef DASH_BUILD_DEV`(`:1013-1021`)로 개발 빌드에만 노출되고, Sample 콤보는 `"Sample 0"` \~ `"Sample 99"` 플레이스홀더 100개다(`:1089-1093`). → U4

### 3-7. 플롯 창 조립

```
onPlotWindowReady(container)                                 :3176
  |- findChild<QTableWidget*>("rankingTable"):3180 — 있으면 setParent(nullptr)+show()
  |- container->property("shap_var_names_by_importance")     :3190
  |     +- SHAP feature 콤보를 중요도 순 재구성, 선택은 이름으로 복원 :3196-3207
  |- m_activePlotWidget = container;  m_reactiveEnabled = true  :3211-3212
  |- ZoomableScrollArea 생성 :3214 — container 800x600 고정 -> autoFit
  |- buttonContainer geometry(10, h-40, 140, 40)             :3224-3229
  |     |- [Init] -> scrollArea->resetZoom() (+ hover 아이콘 교체 필터)
  |     +- [Save] QToolButton(MenuButtonPopup) + QMenu (parent = this)
  |           Image(PNG) / Data(CSV) / Data(JSON), 기본 클릭 = PNG  :3381-3383
  |- rankingTable 있으면 outer QWidget("plotWithRankingTable") 로 수직 결합 :3386-3393
  +- emit analysisResultReady(outer 또는 scrollArea)          :3394 / :3396
       +- DashMainWindow::onPlotReady:3621 — 기존 위젯 있고 다르면 delete :3626-3628
          -> setWidget -> show() + raise()
```

`QMenu` 의 부모를 `saveButton` 이 아니라 `this` 로 두는 이유는 메뉴가 GL 뷰포트와 겹칠 때의 OpenGL 컴포지팅 문제 회피다(`:3305-3306`). 저장 기본 디렉토리는 `ioCtrl->getModuleDir(ModuleType::ResultsAnalyzer, setName)`(`:3302`)이고 `ModuleType::ResultsAnalyzer` 를 실제 경로 조회에 쓰는 곳은 이 한 지점뿐이다. CSV/JSON 은 `dynamic_cast<DashExportable*>` 이 실패하면 **아무 반응 없이 반환하고**(`:3332-3333`·`:3351-3352`) 메뉴 항목은 위젯 종류와 무관하게 항상 3개가 뜬다. → D12

PNG 저장은 `QOpenGLWidget` 여부로 갈린다(`DashAnalyzerHelpers.cpp:68-93`) — 파생이면 `grabFramebuffer()` 후 보이는 직속 자식 오버레이를 `QPainter` 로 합성, 그 외는 `widget->grab()`. 랭킹 표는 `outer` 의 형제라 저장 대상(`scrollArea`)에 들어가지 않는다. 같은 결합을 하는 `createPlotWithTable`(`DashAnalyzerUtils.cpp:144`)이 있으나 호출부가 없고 `onPlotWindowReady` 가 같은 일을 인라인으로 다시 한다 — 팩토리에도 선언만 있고 호출부 없는 진입점이 3개 더 있다. → U5

### 3-8. 플롯 상호작용

| 사용자 행위 | 코드 | 동작 |
|---|---|---|
| 휠 | `ZoomableScrollArea::wheelEvent:100` | 배율 `*1.1`/`*0.9`, `qBound(0.5, z, 10.0)`. 포인터 아래 지점 고정 보정 |
| Alt+휠 | `:102-105` | 줌 대신 기본 스크롤 |
| dock 리사이즈 | `resizeEvent:133` | `m_autoFit` 인 동안 `FillRatio` 재조정 + 버튼 재배치 |
| [Init] | `resetZoom:59` | `m_autoFit = true` 복귀, 스크롤바 0 |
| 플롯 위 마우스 이동 | 각 위젯 `mouseMoveEvent` | 20px 픽 반경 + 마커 반경+4px 내 최근접 점 → `QToolTip` HTML |
| 플롯 밖으로 이동 | `DashPlotWidgetBase::leaveEvent:36` | `m_hoverIdx = -1` + `update()` |

한 번 휠을 굴리면 `m_autoFit` 이 false 로 떨어져(`:117`) dock 리사이즈 자동 맞춤이 멈추고 `[Init]` 만 이를 되돌린다. 공통 레이아웃·폰트는 `DashAnalyzerUtils.h` 의 상수 네임스페이스(`PlotFont`·`PlotLayout`·`PlotSpacing`·`PlotColors`·`PlotLegend`·`PlotTooltip`)로 고정돼 있다.

### 3-9. 반응형 갱신

`connectReactiveSignals()`(`:3404`)가 모든 Method 패널을 순회하며 컨트롤을 스타일/데이터 트리거로 나눠 연결한다. 전부 `Qt::UniqueConnection` 이라 표 재구축 후 재호출해도 중복이 생기지 않는다.

| 컨트롤 | 연결 대상 |
|---|---|
| `QSpinBox` · `QDoubleSpinBox::valueChanged` | `onStyleSettingChanged` **와** `onDataSettingChanged` 양쪽 → D13 |
| `QComboBox::currentIndexChanged` · 셀 `QCheckBox::stateChanged` | `onDataSettingChanged` |
| 색 버튼 | 연결 없음 — 색 선택 람다가 `invokeMethod("onStyleSettingChanged")` 로 직접 호출 |

```
onStyleSettingChanged:3479  — !m_reactiveEnabled || !m_activePlotWidget 이면 return
  +- applyStyleToActivePlot:3502
       |- 현재 패널의 TextStyleGroup 에서 textSize · sigFigs 추출
       +- qobject_cast 10단 체인 — 첫 매치에서 setter 호출 후 return
            Box -> Scatter2D -> Scatter3D -> Parallel -> Pearson ->
            Convergence -> Pareto -> Morris -> Sobol -> Shap

onDataSettingChanged:3485
  +- m_debounceTimer->start() (200ms, single-shot, 매 변경마다 재시작)
       +- debouncedReplot:3493 -> onPlotButtonClicked()   <- 6단계 전체 재실행
```

전용 스타일 setter 를 받는 것은 Box(색 3종 + 스타일 6값)·Pearson(그룹 스타일 + 회귀선)·Sobol(색 2종) 3종뿐이다. Scatter2D·Scatter3D·Parallel·Convergence·Pareto·Morris·Shap 7종은 `setTextOptions` 만 받고 나머지는 재플롯을 기다리며, ShapDependence·Pareto3D·TimeSeries 3종은 체인에 아예 없다.

---

## 4. ViewType 4종 대조표

| 항목 | AnalysisLauncher | DataPreprocessor | ModelRunner_Sensitivity | Optimizer |
|---|---|---|---|---|
| 인스턴스 수 | 2 (Init · Resample) | 1 | 2 (Sim · MCU) | 1 |
| 타깃 콤보 | 2 | 2 | 3 | 0 |
| 타깃 스캔 대상 | `configs/AnalysisLauncher_*.json` | `{userPath}/DataPreprocessor_*` | `{scanPath}/ModelBuilder_*` | — |
| 변수 출처 | `DOE Table.headers` | XML 첫 샘플 키 | `model_info.json` DV label | `optimum.json` `meta.item` |
| 필드 변수 리덕션 | 없음 | mean / std / max | 없음 | 없음 |
| Method 수 | 3 | 4 | 3 (MCU 는 2) | 2 |
| 데이터 경로 | DOE JSON (항상) | 선택한 XML | 없음 (데몬 JSON) | `Optimizer_{Set}/optimum.json` |
| 로더 | `loadFromJson` | `loadFromXml` | 해당 없음 | `loadFromJson` |
| 비동기 여부 | 동기 | 동기 | **비동기** (데몬 + 캐시) | 동기 |
| 설정 영속화 | `DOE Analysis.method` (write-only) | `Data Analysis.method` (write-only) | 없음 | 없음 |
| 랭킹 표 | 없음 | 없음 | 있음 (Morris · Sobol · SHAP-FI) | 없음 |
| Plot 버튼 게이팅 | 없음 | 없음 | `daemonReady` 까지 비활성 | 없음 |

---

## 5. 상태 소유와 재진입

| 상태 | 1차 보관 | Plot 시 읽는 곳 | 재진입 |
|---|---|---|---|
| 변수 목록 | `m_variables` (`QStringList`) | 콤보 `currentData()` | 복원됨 — 원본 파일이 정본, 매 진입 재파싱 |
| 필드 변수 집합 | `m_fieldVariables` (`QSet`) | 접미사 되파싱 | 복원됨 (파서 성공 시에만 → D4) |
| 타깃 선택 | 콤보 `currentIndex` + `userData`(절대경로) | `findChild<QComboBox*>(objectName)` | 이름 우선순위 규칙으로만 재선택 |
| Set 이름 | `m_setName` | — | 호스트가 매 진입 `setSetName()` 재주입 |
| 현재 Method | `m_methodComboBox` 인덱스 | 콤보 `currentText()` (패널 키) | 위젯 수명 내에서만 — 재기동은 0번 복귀 |
| 축·변수 배정 · 수치 스타일 | 표 셀 위젯 | **셀 위젯** | 소실 → D9 |
| 색 | 버튼 `styleSheet()` 문자열 | 문자열 절단 또는 정규식 → D6 | 소실 → D9 |
| 텍스트 스타일 | `TextStyleGroup` 안 표의 0행 | `findChild("TextStyleGroup")` → D7 | 소실 → D9 |
| 활성 플롯 · 계산 결과 | `m_activePlotWidget` (`QPointer`) | — | 소실 — dock 교체 시 `delete`(`DashMainWindow.cpp:3627`) |
| 민감도 원자료 | `DashModelRunner::m_resultCache` (상한 10) | 캐시 키 4필드 | 세션 내에서만 — 상한 초과 시 전량 clear |

**플롯 데이터는 어디에도 남지 않는다** — 플로터는 빌더 함수 안에서 파괴되고, 계산 결과는 위젯 멤버에만 있으며, 위젯은 dock 교체 시 delete 된다. 다시 보려면 6단계 전체를 다시 탄다.

명시적 리셋 경로는 없고 대신 재진입 억제가 두 겹 걸린다 — `initializeTargetData:373-391` 의 100ms 중복 억제와 `updateMethodWidgetsWithVariables:1349-1353` 의 "변수 목록이 직전과 같으면 반환"이다. 둘 다 통과하면 패널 표가 갈아끼워지고, 그때 보존되는 것은 3-3 의 표가 적은 항목뿐이며 그 보존은 전부 메모리 안에서 일어난다. `m_setName` 은 위젯이 스스로 알아내지 않아 비어 있으면 각 함수가 `"Set1"` 로 대체하는데, 이 폴백 삼항식이 파일 안에 7회 복제돼 있다(`:417`·`:431`·`:884`·`:951`·`:2184`·`:2627`·`:3301`). `Optimizer` 와 `ModelRunner_Sensitivity` 는 설정 영속화 경로가 아예 없다.

---

## 6. 결함 목록

3\~5절 서술 중 동작이 의도와 어긋나거나 어긋날 수 있는 지점 19건 — `D` 잘못 구현 15건, `U` 미구현 4건 (`U4` 는 예정 기능이라 제외). ID 는 3절 등장 순서이고 D14·D15 는 5절 유래라 뒤에 붙였다. 우선순위 판정은 하지 않는다. 9개 모듈 교차 색인은 [[Cross-Module-Defect-Index]].

| ID | 분류 | 결함 | 좌표 | 근거와 귀결 |
|---|---|---|---|---|
| **D1** | 구조·결합 | Method 콤보 순서가 선언 순서와 다르다 | 3-1 | `m_methodWidgets` 가 `QMap<QString, QWidget*>`(`.h:123`)이라 `setupMethods:358-361` 순회가 키 알파벳 순 → DataPreprocessor(4종)·ModelRunner(3종)에서 순서가 어긋나고, 배열 순서를 계약으로 적은 주석(`:230-231`)과 불일치한다 |
| **D2** | 진입·수명 | 중복 억제 캐시가 함수-로컬 static | 3-2 | `initializeTargetData:373` 의 `recentCalls` 가 인스턴스를 구분하지 않고 `"{viewType}_{setName}"` 만 키로 쓴다(`:374`) → 두 공유 쌍(ModelRunner Sim/MCU · AnalysisLauncher Init/Resample)이 100ms 창을 공유. 후자는 variant 분리(`d0f78f1`)로 새로 생긴 공유다. 같은 파일 `m_lastMethodWidgetVariables` 는 정확히 이 사유로 이미 멤버(`.h:137-141`) |
| **D3** | 데이터 정본 | `(std)` 리덕션이 조용히 Max 로 대체된다 | 3-3 | 콤보는 `"var\|Std"` 를 내보내고 `DashDataLoader` 는 `"Std"` 로 해석하지만 `applyReduction:213` 분기는 Max/Min/Mean 3종(`:219-221`)뿐, 나머지는 `reduceMax` 폴백(`:224`) → **`(std)` 를 고르면 표준편차가 아니라 최댓값이 그려진다.** `reduceStd:206` 은 `computeFieldStatistics:227-232` 에서만 쓰인다 |
| **D4** | 실행 모델 | XML 변수 스캔이 매번 문서 전체를 GUI 스레드에서 파싱 | 3-3 | `extractVariablesFromXml`(`DashAnalyzerUtils.cpp:307`)이 전문을 읽고 호출처 둘(`:662`·`DashPlotWidgetFactory.cpp:1058`) 다 GUI 스레드. 실패 시 스트림 폴백(`:322-354`)은 `fieldVariables` 를 채우지 않아 → **같은 파일이라도 파서 성공 여부에 따라 리덕션 항목이 나타나거나 사라진다** |
| **D5** | 구조·결합 | 타깃 콤보가 `objectName`+`findChild` 문자열 계약 | 3-1 · 5절 | 패널 내부 컨트롤은 `DashAnalyzerPanelControls` 타입 핸들로 옮겼으나 타깃 콤보 5종은 여전히 문자열 — `findChild<QComboBox*>` 25회. 컴파일러가 검증하지 않는 이름이 ViewType 4갈래 분기 조건을 겸한다 |
| **D6** | 데이터 정본 | 색의 정본이 스타일시트 문자열이고 읽는 방식이 둘 | 3-5 | `getColorFromButton`(`DashAnalyzerUtils.cpp:22`)은 `indexOf("background-color:")` 절단, `applyStyleToActivePlot` 은 `QRegularExpression("background-color:\\s*(#[0-9a-fA-F]+)")`(`:3564` 등 4곳) → 후자는 16진수만 받아 색 이름 표기(`black`)를 매치하지 못하고 `Qt::black` 폴백으로 떨어진다 |
| **D7** | 구조·결합 | 타입 핸들 `textStyleGroup` 이 채워지기만 하고 읽히지 않는다 | 3-6 | 팩토리가 9곳에서 `out.textStyleGroup` 에 대입하지만(선언 `DashAnalyzerPanelControls.h:11`) 읽는 코드 0건. 위젯은 전부 `findChild<QWidget*>("TextStyleGroup")`(13회) + 폴백 캐스케이드를 쓰고 objectName 은 `createTextStyleGroup:148` 이 항상 붙이므로 **폴백도 도달하지 않는다** — 복제된 20여 줄의 절반이 죽은 코드 |
| **D8** | 구조·결합 | `methodKey` 매핑이 세 파일에 복제 | 3-6 | `box`→`boxplot` 등 5줄 변환이 `DashAnalysisLauncher.cpp:1186-1191`·`DashDataProcessor.cpp:2603-2613`·`DashDoeConfigManager.cpp:440-450` 에 각각 존재. 세 사본이 command 목록을 독립적으로 들고 있어 추가 시 세 곳을 함께 고쳐야 한다 |
| **D9** | 데이터 정본 | 설정 JSON 의 method 블록이 write-only | 3-6 · 5절 | `"DOE Analysis"`·`"Data Analysis"` 키의 전 출현이 write 경로이고(`DashAnalysisLauncher.cpp:1174-1205`·`DashDataProcessor.cpp:2589-2632`·`DashDoeConfigManager.cpp:428-465`) 복원 reader 는 0건 → **매 Plot 이 축·색·스타일을 파일에 쓰지만 재기동 후 그 값이 화면에 돌아오지 않는다** |
| **D10** | 실행 모델 | spec 조립 실패가 조용하다 | 3-6 | 오류가 `messages`→`logMessage` 로 흐르지만 `spec.isEmpty()` 이후 UI 변화 없음(`DashAnalysisLauncher.cpp:1145`·`DashDataProcessor.cpp:2558`·`DashOptimizer.cpp:1123`). `DashPlotRequestHandler` 미매치(`nullptr`)와 `onPlotSpecReady:3169-3170` 조기 반환도 동일 → [Plot] 무반응이 세 계층에서 만들어진다 |
| **D11** | 구조·결합 | 랭킹 표를 위젯 트리의 숨은 자식으로 실어 보낸다 | 3-6 · 3-7 | 팩토리가 `createRankingTable`(`DashAnalyzerUtils.cpp:81`) 결과를 `setParent(w)`+`hide()` 로 붙이고 `onPlotWindowReady:3180` 이 `findChild("rankingTable")` 로 꺼낸다 → 반환 타입(`QWidget*`) 밖의 부수 채널이며 계약이 objectName 문자열. 결합 결과 표는 `outer` 의 형제가 되어 PNG 저장 대상에서 빠진다 |
| **D12** | 구조·결합 | CSV/JSON export 가 미지원 위젯에서 무반응 | 3-7 | Save 메뉴는 위젯 종류와 무관하게 항상 3개가 뜨고 `dynamic_cast<DashExportable*>` 실패 시 로그도 대화상자도 없이 반환(`:3332-3333`·`:3351-3352`) → `DashExportable` 구현은 Pareto3D·Scatter3D 2종뿐이라 나머지 11종에서 메뉴가 아무 일도 하지 않는다 |
| **D13** | 실행 모델 | 스핀박스 1회 변경이 두 경로를 동시에 탄다 | 3-9 | `connectReactiveSignals:3404` 가 스핀박스를 `onStyleSettingChanged:3479` 와 `onDataSettingChanged:3485` 양쪽에 건다 → 즉시 setter 반영 후 200ms 뒤 같은 변경이 `debouncedReplot:3493`→`onPlotButtonClicked` 로 전체 재플롯(파일 재파싱 또는 데몬 왕복 포함, 민감도는 캐시 히트면 왕복 없음). 주석(`:3423-3427`)은 직접 setter 없는 설정을 받아내려는 의도라 적지만 setter 가 있는 설정에서는 중복 실행이다 |
| **D14** | 진입·수명 | 타깃 콤보 스캔에 Set 필터가 없고 항상 0번을 자동 선택한다 | 3-1 · 4절 | `initializeTargetData` 의 DataPreprocessor 분기(`:487-514`)는 `getUserPath()` 아래 `DataPreprocessor_*` 폴더 **전량**을, AnalysisLauncher 분기(`:516-534`)는 configs 의 `AnalysisLauncher_*.json` **전량**을 나열한 뒤 `setCurrentIndex(0)` 로 0번을 골라 `onTargetDataChanged()` 까지 실행한다 — `m_setName` 을 필터로 쓰지 않는다 → **다른 Set 의 산출물이 콤보에 섞이고, 진입 직후 화면에 뜨는 것은 현재 Set 이 아니라 이름순 첫 Set 이다.** ModelRunner 인스턴스에서 같은 코드가 낳는 결함이 Model Runner 의 D30 이다 |
| **D15** | 데이터 정본 | `m_setName` 이 비면 `"Set1"` 로 조용히 대체하는 폴백이 7회 복제돼 있다 | 5절 | `m_setName.isEmpty() ? "Set1" : m_setName` 이 `:417`·`:431`·`:884`·`:951`·`:2184`·`:2627`·`:3301` 에 그대로 있다. `:417` 은 그 값으로 `ModelBuilder_{Set}` 폴더를 조립한다 → **호스트가 `setSetName()` 을 주입하기 전에 어느 경로든 밟히면 무관한 `Set1` 의 산출물을 읽고 경고가 없다.** 위젯이 Set 을 스스로 알아내지 않는 구조(5절)가 이 폴백 7벌로 메워져 있다 |
| **U1** | 미구현 | `onTargetDataChanged` 의 모듈 판별 4갈래가 도달 불가 | 3-3 | `GeometryParameter`(`:809`)·`ConditionParameter`(`:826`)·`ModelBuilder`(`:841`)·`Optimizer`(`:858`) 가 파일명 접두사로 갈리지만 콤보를 채우는 코드는 `{configs}/AnalysisLauncher_*.json` 만 나열(`:522`) → 네 분기의 변수 추출 규칙이 실행되지 않는다 |
| **U2** | 미구현 | `save_json_path` 가 기록만 되고 소비되지 않는다 | 3-6 | Parallel Plot 이 `settings.parallel.save_json_path` 에 경로를 넣지만(`:2187`) 레포 전체에서 이 키를 읽는 코드가 0건 |
| **U3** | 미구현 | `DashDoeConfigManager::updateConfigFile` 이 호출처 없이 살아 있다 | 3-6 | `model/DashDoeConfigManager.cpp:418`(선언 `.h:45`) — `DOE Analysis.method` write 와 `methodKey` 매핑을 담은 55줄이고 참조 0건. `DashAnalysisLauncher::updateConfigFile:1164` 와 겹치는 세 번째 사본 |
| **U4** | 미구현 | ~~SHAP plot type 6종 중 4종이 폴백~~ | 3-6 | **제외** — 착수 대기 기능 갈래다. `buildShapWidget:2278` 에서 `dependence` 만 전용 위젯이고 `beeswarm`·`permutation`·`permutation_box`·`waterfall` 은 Feature Importance 로 되돌아가지만(`:2283-2287`), 그 4종은 `#ifdef DASH_BUILD_DEV`(`:1013-1021`)로 릴리스에 노출되지 않는다 |
| **U5** | 미구현 | 호출부 없는 진입점 4개 | 3-7 | `createUncertaintyDistributionWidget:739`(약 106줄)·`createScatter2DWidget:1466`(약 110줄)·`createScatter3DWidget:1669`(약 111줄) — `DashPlotWidgetFactory.h:22`·`:44`·`:65` 에 선언까지 돼 있고 `ViewSpec` 어디에도 등록 안 됨. `createPlotWithTable`(`DashAnalyzerUtils.cpp:144`, 16줄)은 `onPlotWindowReady:3386-3393` 이 같은 일을 인라인으로 다시 한다 |

---
