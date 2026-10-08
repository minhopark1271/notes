# Data Preprocessor — 사용자 플로우 ↔ 코드 대응

> **성격**: 독립 참조 문서. 사용자 행위 하나하나가 밟는 함수 체인의 대응표 — 수정 계획·우선순위는 담지 않는다.
> **좌표 기준**: `dev` @ `4c7608e` 실측, 유효기간 있음 (이전 `ac6e4e6` 대비 `DashMainWindow.cpp`·`DashProject.cpp`·`.ui` 만 이동).
> **검증 수준**: 정적 근거만 — `.ui`·`connect`·함수 본문·키 문자열 grep 전수. 빌드·실행 검증 없고, preprocessor DLL 내부는 호출측 파싱 코드로만, 고객사 KPI 경로(D6·D11·D12)는 Dev 빌드에서 컴파일되지 않아 소스로만 확인했다.

## 개요

탭 3면과 클래스 10종이 preprocessor DLL 핸들 하나(`m_preprocessor`)를 순차로 두드린다. 사용자 행위는 `DashDataProcessor` 를 거쳐 `IPreprocessorWrapper` 의 가상 함수로 내려가고, 화면은 그 반환 JSON 을 다시 파싱해 트리·표를 세운다.

도메인 모델이 그 JSON 두 덩이다 — `m_geometries`(Component 정의)·`m_availableResponses`(Name↔operator). `types::Set` 같은 타입은 이 경로에 없고, 사용자 선택은 `QVariantMap` 요청으로 조립돼 그대로 DLL 질의 문자열이 된다. 모듈이 보유한 상태는 DLL 응답 사본과 위젯 값뿐이다. 3\~4절은 코드가 하는 일만, 결함은 5절 — 본문 `→ D{n}`·`→ U{n}` 이 링크다.

---

## 1. 화면과 클래스

세 면 모두 `QTabWidget` 한 개 안의 페이지다 — Morphing 처럼 부모가 갈리지 않아 좌표를 코드로 맞추는 로직이 없다.

`ui/DashDataProcessorWidget.ui` 의 세 페이지는 Data Upload `dataUploadTab`(`:21-77`, 콤보 2개 + 런타임 생성 표 N개 + [Load Raw Dataset]) · Preprocess `preprocessTab`(`:78-254`, Component 리스트·Load step 트리·Name 트리·Output Response 표) · Data Analysis `analysisTab`(`:255-`, 빈 페이지)다. `.ui` 밖이 둘 — Dataset 영역은 스크롤 내용 위젯을 `setupUI:446-452` 가 코드로 만들고 표·헤더 체크박스는 `datasetReady` 수신마다 새로 짓는다. Data Analysis 는 `setupUI:505-509` 가 `DashResultsAnalyzerWidget(DataPreprocessor)` 를 붙인다.

| 클래스 (줄) | 담당 |
|---|---|
| `DashDataProcessor` (4,671) | 스캔·질의·XML 생성 전량. **코드베이스 단일 최대 파일** |
| `DashDataProcessorWidget` (1,285 + ui 285) | 탭 3면 · 선택 검증 · 요청 조립 전 단계 |
| `…PresentationModel` (133) | 표 행 → 요청 계획 분류 · Output Response 기록 (W21 산출) |
| `KPIConfigDialog` (341) | 고객사 KPI 입력. 타입 목록이 빌드 타깃별 조건부 컴파일 |
| `DashResultProcessor` (344) | 샘플 전량 루프 — 샘플 1개 = DLL 재로드 1회 |
| `DashResultXmlWriter` (1,162) | XML 섹션 4종 기록 · operator 조회 |
| `DashResponseInitializer` (353) | 배치 전 응답 스키마 확보 (선택 없이 Process 한 경우) |
| `DashFileLocator` (210) | run 폴더 안 결과 파일 탐색 |
| `Ansys`·`AbaqusPreprocessorWrapper` (62 · 78) | DLL 진입점. 생성자에서 플러그인 로드 |
| `DashResultsAnalyzerWidget` (3,697) | Data Analysis 탭 — 다른 3모듈과 공유 |

DLL 경계는 `IPreprocessorWrapper` 가상 함수 8개가 전부다 — `SetInputFilePathes`(bool, 로드·Preview 복원·샘플마다) · `GetAnalysisInfo`(JSON, `.rst` Static/Modal 판정) · `GetTimeSteps`(JSON, Load Step 트리·파일 강제 로드·Modal 주파수) · `GetGeometries`(JSON, Component 목록) · `GetAvailableResponses`(JSON, Name 트리·operator 매핑) · `GetGeometryVtk`·`GetFieldOutputVtk`(`vtkUnstructuredGrid`, 배경/Component 지오메트리 · Preview/XML 필드 값) · `Clear`(void, 소멸자·플러그인 교체·**샘플마다**).

---

## 2. 전체 동선

```
1. 진입       Set 클릭 → setModel() 이 시그널 재연결 + configs 스캔
              ※ 시작 페이지·진입 전제가 없다 — Set 만 있으면 항상 같은 3탭
2. DOE 선택   Selected DOE 콤보 (configs 의 AnalysisLauncher_*.json + [Import single file ...])
              ※ JSON 의 output 키는 안 쓴다 — runs 하위 폴더 존재 여부가 유일 기준
3. 타입 선택  runs 폴더 전량 스캔 → (type, 파일명) 조합마다 표 하나 동적 생성
              ※ .rst 는 GetAnalysisInfo() 로 Static/Modal 판정 — DLL 첫 진입 지점
4. 로드       [Load Raw Dataset] → SetInputFilePathes → GetTimeSteps → GetGeometries
              → GetGeometryVtk("{}") → GetAvailableResponses (연달아 5회)
              ※ 이 버튼이 Output Response 표를 무조건 비운다
5. 3종 선택   Component · Load Step · Name — 선택마다 DLL 질의 1회, 카테고리는 선택 불가
              ※ Modal · Function Expression 은 Load Step 트리를 끄고 이름을 코드로 채운다
6. 응답 구성  [▼ Add] / [▲ Remove] / [Custom KPI]
              ※ Add·Remove 만 설정 JSON 에 기록 — KPI 행은 표에만 남는다
7. Preview    GetFieldOutputVtk 1건을 렌더뷰에 (선택 단계)
              ※ 진입 시 원본 다중 파일 상태를 먼저 복원 (Process 가 DLL 상태를 바꿔 놓으므로)
8. Process    표 전량을 PM 이 요청 계획으로 분류 → 요청마다 샘플 전량 루프
              ※ KPI 행이 하나라도 있으면 KPI 경로가 배치 전체를 가져간다
              ※ 샘플 1개당 Clear → SetInputFilePathes → GetTimeSteps

[산출] {프로젝트루트}/DataPreprocessor_{Set}/{Component}_{step}_{substep}_{Name}.xml
       Data Analysis 탭과 하류(Model Builder)가 읽는 전부
```

---

## 3. 단계별 대응

### 3-1. 진입

갈래가 없다. Set 이 선택되면 항상 같은 3탭이 뜬다 — `handleSubItemSelection:980` → 분기(`DashMainWindow.cpp:1082`) → `handleDataPreprocessorSelection:1289` → `setProjectDirectory:1303` → `setModel:1305` → `setCurrentWidget:1306`. 같은 클릭의 후반 `:1309-1366` 이 모델 시그널 6종 + Analyzer 1종을 재연결한다 — `logMessage:1310`(로그 창 "DataProcessor" 태그) · `processingStarted`/`Finished` `:1314`/`:1318`(`showLoadingIndicator` + 상태바) · `allGeometryReady`/`componentGeometryReady` `:1327`/`:1331`(`DashRenderingManager` 배경 메시·Component 하이라이트) · `fieldOutputReady:1335`(스칼라 이름을 위젯 `m_previewDisplayName` 으로 덮어쓰고(`:1342`) `updateFieldOutput` + 컬러바 범위) · Analyzer 경유 `analysisResultReady` → `onPlotReady:1364`. `connect` 7개 전부 `Qt::UniqueConnection` 이고 명시적 `disconnect` 가 앞에 붙는 것은 둘뿐이다(`logMessage:1309`·`analysisResultReady:1362`).

위젯 `setModel:97` 은 순서가 정해져 있다 — 이전 모델 `disconnect`(`:103`) → 콤보 2종 `disconnect`(`:107-114`) → 포인터 교체(`:116-117`) → `getProjectPath`·`setProjectDirectory`(`:124-127`) → 모델 시그널 8종(`:131-362`)·콤보/트리/리스트(`:365-392`) `connect` → Analyzer 연결 + `initializeTargetData`(`:395-407`) → `findDvTableFiles`(`:409`). **이 순서에 `resultTable` 초기화가 없다** — 표를 비우는 코드는 `onLoadButtonClicked:641-642` 하나뿐이다. → D1

모델 `setProjectDirectory:60` 은 인자를 `Q_UNUSED` 로 버리고(`:63`, 주석 `LEGACY`) `DashIOController` 에서 경로를 다시 얻는다 — 호출부가 넘긴 configs 경로는 쓰이지 않는다. Set 생성·복원은 `DashProject` 담당 — 생성 `:755-756`, 복원 2경로(`loadSetsFromConfigs:1145-1153` 파일명 역추출 · `restoreExistingModules:1395-1409` 미존재분 보충). 둘 다 `addDataProcessor:252-255` 를 거치고 이 함수가 `setSetName` 을 반드시 부르므로 `m_setName` 은 실사용에서 비지 않는다.

### 3-2. DOE 선택

| 사용자 행위 | 진입 신호 | 함수 체인 | 남는 상태 |
|---|---|---|---|
| (자동) 진입 직후 | `setModel:409` | `findDvTableFiles:269` → `entryList({"AnalysisLauncher_*.json"})` `:296-298` → `dvTableFilesFound` | 콤보 채움 + `setCurrentIndex(-1)`(`:142`) |
| 일반 항목 선택 | `currentIndexChanged:365` → `onDvTableSelectionChanged:516` | `configs/{userData}` 조립 `:573-603` → `loadDvTable:190` | `m_dvTablePath`·`m_dvTableRoot`·`analysisFilesFound` |
| [Import single file ...] | 같은 경로, 텍스트 일치 `:541` | `QFileDialog` `:542-547` → 타입 콤보 "N/A" 잠금 `:557-562` → `loadRstDataDirectly:671` (3-10) | `m_dvTablePath` **빈 문자열** = 단일 파일 모드 표식 |
| 콤보 선택 해제 | `index < 0` `:370` | 표·버튼 그룹 전량 삭제 `:518-538` | Dataset 영역 비움 |

`loadDvTable:190` 은 이름과 달리 **JSON 을 해석 타입 결정에 쓰지 않는다.** JSON 은 `m_dvTableRoot` 에 보관만 하고(`:214`), 콤보 항목은 파일시스템에서 뽑는다 — `{projectRoot}/{모듈폴더}` 하위 디렉토리를 순회해(`:229-238`) `^runs\d+$` 폴더가 하나라도 있으면 후보로 채택하고 emit 한다(`:247`). 진입 직후엔 `m_dataset.clear()` + 빈 `datasetReady`(`:194-196`)로 표를 즉시 비운다.

### 3-3. Analysis Type 선택 — Dataset 구성

이 모듈에서 가장 무거운 동기 구간이다. `onAnalysisFileSelected:304` 하나가 파일시스템 전수 스캔 + DLL 초기화 + DLL 질의 + 설정 JSON 쓰기를 연달아 한다. → D3

```
onAnalysisFileSelected(analysisType)              DashDataProcessor.cpp:304
  ├─ m_currentAnalysisType / m_currentStatusKey :307-308
  ├─ beginProcessing :312 → processEvents(ExcludeUserInputEvents) :313  ← 25곳 중 유일한 입력 차단
  ├─ {projectRoot}/{모듈}/{타입} 확인 :355-368 · ^runs?\d+$ 수집 + 숫자 오름차순 :371-388
  ├─ 결과 파일 가진 첫 runs 폴더 = 패턴 기준점 :404-427
  ├─ runs 폴더 **전량** 순회 → 파일명 합집합 + 등장 횟수 :456-466
  │     (filterSplitFiles:2964 로 ANSYS 분할 .rst 제외) · isDynamic 판정 :469-477
  ├─ 파일명마다 패턴 등록 :481-524 — .rst 면 initializePreprocessor("rst"):84 후
  │     SetInputFilePathes → GetAnalysisInfo → "analysis" 키 :496-520
  ├─ runs 순회하며 DatasetItem :538-609 — Dynamic 은 폴더마다 *.dfr 첫 파일 :549-570,
  │     그 외는 패턴 파일명 exact match 만 허용 :572-607
  └─ saveDoeTableSnapshot:2692 :617-665 · endProcessing :667 · emit datasetReady :668
```

`beginProcessing:312` 에 짝을 맞추지 않는 조기 반환이 넷이다 — `:367`·`:394`·`:425`·`:529`(`:320`·`:327`·`:335`·`:345` 는 맞춘다). → D2

**그루핑 키가 `patternFileName` 이다.** run 마다 파일명이 다른 경우(`runs1.odb`)와 모든 run 에 같은 이름이 있는 경우(`Fatigue_Compression.odb`)를 등장 횟수로 가른다 — 1회면 `"result" + 확장자` 로 통일해 한 표에 묶고, 여러 번이면 실제 파일명을 키로 쓴다(`:591-602`). `.rst` 는 항상 실제 파일명이다.

`initializePreprocessor:84` 의 솔버 판정은 확장자 문자열 하나다 — 같은 솔버면 재사용(`:101-103`), 타입이 바뀌면 `Clear()` 후 교체(`:106-109`). 래퍼 생성자의 `SetPlugin` 실패는 `std::runtime_error` 로 던져져 호출부에서 `errorOccurred` 가 된다.

| 확장자 | `m_solverType` / 래퍼 | 사전 검증 |
|---|---|---|
| `.odb` | `Abaqus` / `AbaqusPreprocessorWrapper` | Abaqus 루트 경로 (`:115-119`) |
| `res`·`dfsxml`·`dfr` | `AnsysMotion` / `AnsysPreprocessorWrapper(true)` | Ansys 루트 + `Motion/bin` 존재 (`:145-166`) → U2 |
| 그 외 (`.rst`·`.op2` 포함) | `AnsysMechanical` / `AnsysPreprocessorWrapper(false)` | Ansys 루트 경로 (`:132-138`) → U1 |

뷰의 `datasetReady` 수신 람다(`:154-295`)는 표를 **매번 통째로 재구축**한다 — 위젯·버튼 전량 삭제(`:156-171`) → `(type, basename)` 그룹핑(`:180-186`) → 그룹마다 `QFrame` 헤더 + `QCheckBox`(`:210-243`, 첫 그룹만 `setChecked(true)`) + 2열 `QTableWidget`(`:247-280`) → `m_dynamicTables[type] = table`(`:283`) → U3. 체크박스는 `QButtonGroup(exclusive)` 로 묶이고 **선택 결과는 위젯 property 문자열 2개**(`analysisType`·`baseFileName`)로만 전달된다. 남는 상태는 `m_dataset`·`m_currentAnalysisType`·`m_currentStatusKey`·`DOE Table` 스냅샷·동적 생성 위젯이다.

### 3-4. Load Raw Dataset — DLL 스키마 확보

`onLoadButtonClicked:611` 이 체크 버튼을 확인하고(없으면 첫 항목 강제 체크 `:619-630`) `resultTable->setRowCount(0)`(`:641-642`) 후 `loadRstDataFromTable:781` 로 간다.

```
loadRstDataFromTable(selectedType, selectedBaseName)   DashDataProcessor.cpp:781
  ├─ m_selectedType / m_selectedBaseName 보관 :786-787
  ├─ 입력 파일 목록 — 단일 파일 모드(m_dvTablePath 빔) :804-818 /
  │     DOE 모드 {projectRoot}/{모듈}/{타입}/{item.path} :819-870
  ├─ 첫 파일 확장자로 initializePreprocessor :918-920 · 파일 존재 전수 검증(하나라도 없으면 중단) :925-931
  ├─ SetInputFilePathes :933 · m_lastLoadedInputFiles 저장 :934  ← Preview 복원용
  ├─ m_isModalAnalysis = selectedType.contains("modal") :940   → D4
  ├─ GetTimeSteps :948 — Modal 은 숫자 정렬 후 Mode N 채번 :966-1028 /
  │     AnsysMotion 은 state_id 기반 "States"·"State N" :1029-1074 / 그 외 "Step N"·"Substep N" :1075-1093
  ├─ GetGeometries → components + "All" prepend :1105-1126 · GetGeometryVtk("{}") → allGeometryReady :1129-1141
  ├─ GetAvailableResponses(firstTimeStepQuery) :1164-1195
  │     └─ function_expression 있으면 components[1] 에 "Function Expression" 삽입 :1183-1187
  └─ emit keysExtracted :1202 →D5 · (Modal) namesUpdated :1207-1219 · updateDatasetConfig:2644 :1224 →D7
```

Modal 경로는 `GetTimeSteps` 의 키를 **숫자로 정렬한 뒤** 1-based `modeIndex` 를 붙인다(`:996-1011`). 정렬을 빼면 `QJsonObject` 의 사전식 순회("10" < "2") 때문에 Mode 2 가 substep 10 에 대응된다 — 주석이 그 이유를 명시한다(`:967-969`). `extractedKeys.isAnsysMotion` 에 들어가는 값은 `m_solverType` 이 아니라 **`hasFunctionExpression`** 이다(`:1200`). → D5

뷰의 `keysExtracted` 수신 람다(`:297-336`) — `componentList` 는 `clear()` 후 `addItems`, `m_storedLoadSteps` 는 `keys.loadSteps` 통째 보관(Function Expression 전환 후 복원용), `loadStepTree` 는 `setEnabled(!keys.isAnsysMotion)`(`:306`) 이고 활성일 때만 마지막 토큰 숫자 기준 정렬 후 2단 트리 구축(`:310-329`), `nameList` 는 `!isAnsysModal && !isAnsysMotion` 일 때만 `clear()`(`:332-334`) 하고 항상 `setEnabled(false)`. 그 가드는 모델이 `namesUpdated` 로 이미 채운 경우를 지키려는 것인데 주석(`:331`)은 조건을 "Modal or Dynamic" 이라 적었다. → D5

남는 상태는 `m_lastLoadedInputFiles`·`m_isModalAnalysis`·`m_modalDefs`·`m_geometries`·`m_availableResponses`·`m_storedLoadSteps` 와 DLL 이 물고 있는 다중 파일 상태다.

### 3-5. Component · Load Step · Name 선택

세 위젯의 선택이 사슬로 이어지고 각 단계가 DLL 질의를 한 번씩 유발한다. Component 는 `currentItemChanged:387` → `onComponentSelectionChanged:801`, Load step 은 `currentItemChanged:389` → 뷰 `onSelectionChanged:1003`, **Name 트리는 시그널이 없다** — Add/Preview 시점에 `currentItem()` 을 읽는다.

```
onComponentSelectionChanged()                     DashDataProcessorWidget.cpp:801
  ├─ m_isProcessing 이면 반환 :803
  ├─ "Function Expression" → loadStepTree 비활성·clear + onSelectionChanged(comp, "")  :814-820
  └─ 그 외 :821-861 — loadStepTree 활성, 비었으면 m_storedLoadSteps 로 재구축 :826-848
        → requestVtkGeometry(comp) :851 →D6 → 트리·리스트 선택 해제(QSignalBlocker) :853-858
        → onSelectionChanged() :860
```

뷰의 `onSelectionChanged:1003` 은 Load Step 표시 문자열을 조립한다 — 부모가 `"States"` 면 `"State N"`(`:1031-1033`), 부모 있으면 `"Step N / Substep M"`(`:1034-1036`), 부모 없고 Abaqus 면 `"Step N / Substep 0"`(`:1037-1039`). Modal(`:1012-1016`)·Function Expression(`:1019-1021`)·부모 없는 비-Abaqus(`:1040-1042`)는 조기 반환이다.

모델의 `onSelectionChanged:1330` 은 세 갈래다. → D6

| 갈래 | 질의 | 결과 |
|---|---|---|
| Function Expression `:1340-1392` | `GetAvailableResponses("{}")` | `function_expression` 키를 정렬해 단일 카테고리로 emit |
| Modal `:1395-1409` | **질의 없음** | `"Natural Frequency"`(자식 없음) + `"Mode Shape"`(x·y·z·magnitude) 를 코드로 생성 |
| 일반 `:1411-1461` | `parseLoadStep:1228` → `MakeMechanicalTermArray` + `addComponentToQuery:1263` → `GetAvailableResponses` | `m_availableResponses` 갱신 후 `function_expression` 제외 카테고리를 정렬해 emit |

`addComponentToQuery:1263` 이 Component 문자열을 질의 키로 바꾼다 — AnsysMotion 은 `entity_name`·`entity_type`(+`BODY` 면 `body_name`), 그 외는 `location`·`named_selection`. `m_geometries` 에 없으면 이름을 `named_selection` 으로 직접 쓰고(`:1306-1307`), `"All"` 이면 아무것도 넣지 않는다(`:1265-1267`).

`onNamesUpdated:1047` 이 Name 트리를 만든다. **자식이 있는 부모는 `Qt::ItemIsSelectable` 을 뗀다**(`:1074`) — 카테고리 선택을 막는 장치이고, 자식 없는 부모(`Natural Frequency`)는 leaf 로 선택된다(`:1076`). 자식 이름 `"_"` 는 표시만 `"Magnitude"`(`:1067`). 선택을 모델이 보관하는 필드는 없다 — 정본은 세 위젯의 `currentItem()` 이다.

### 3-6. Output Response 구성

```
[▼ Add] → onAddResultClicked                      DashDataProcessorWidget.cpp:675
  ├─ m_isProcessing 이면 반환 :677
  ├─ 검증 5종 — Component :682 / Name :690 / Name 이 카테고리 :695 /
  │     Load Step(FuncExpr·Modal 예외) :701 / 최상위 Step(Abaqus 예외) :709
  ├─ loadStep 4분기 :718-732 · name 조립("Magnitude" 는 부모 이름만) :734-746
  └─ resultTable 행 3열 추가 :748-752 → saveOutputResponseToJson → PM:103  :754  → D7
```

`loadStep` 값은 Function Expression `""` · Modal `"Modes / Mode N"` · 부모 있음 `"Step N / Substep M"` · 부모 없음(Abaqus) `"Step N / Substep 0"` 네 가지다. Modal 값이 Preview 와 다르다 — Add 는 부모까지 붙인 `"Modes / Mode N"`(`:723`), Preview 는 자식만 쓴 `"Mode 1"`(`:910`). 둘 다 하류에서 `Mode\s+(\d+)` 로 다시 파싱되므로(`:1767`·`:2253`) 결과는 같다. `PM::saveOutputResponse:103-133` 은 설정 JSON 을 read-merge-write 해 `Output Response` 배열을 갱신한다 — Add(`:754`)·Remove(`:774`) 마다 파일 I/O 1회다.

**Custom KPI** — General / Custom KPI 는 배타 토글이다(`onGeneralModeToggled:1103`·`onTargetKpiToggled:1118`). 켜면 즉시 `new KPIConfigDialog(nullptr)`(`:1142` — parent 를 주면 크래시, 헤더 주석 `:17-24`)가 뜨고, 현재 선택값을 고정값으로 주입(`:1147-1162`)한 뒤 Configuration 후보를 구성한다(`:1167-1191` — Modal 은 `"Mode N"` + `"All"`, 비-Modal 은 Name 트리를 `"부모 / 자식"` 으로 평탄화). Accepted 면 `addKpiToResultTable:1216` 이 0열 아이템의 `Qt::UserRole` 에 `KPIConfig` 를 심고(`:1227`) `collectResultRows:787` 이 `canConvert<KPIConfig>()` 로 식별한다. Rejected 면 두 토글 원위치(`:1206-1211`). 설정 JSON 은 쓰지 않는다. → D8

### 3-7. Preview

`onPreviewButtonClicked:864` 가 검증 4종(`:876-900`) 후 `loadStepText`(Modal 은 `"Mode N"` 만, `:902-916`)·`nameText`(Add 와 동일 규칙, `:918-929`)를 조립하고 `m_previewDisplayName = safe(loadStep) + "_" + safe(name)`(`:931-937`)을 세운 뒤 `requestVtkPreview` 로 넘긴다(`:939`).

```
requestVtkPreview(component, loadStep, name)      DashDataProcessor.cpp:2233
  ├─ m_lastLoadedInputFiles 로 원본 다중 파일 상태 복원 :2241-2244   → D6
  ├─ Modal — "Mode N" 파싱 → m_modalDefs 에서 step/substep 역인출 :2252-2275 /
  │     "Natural Frequency" 는 GetTimeSteps 주파수만 팝업 후 반환 :2278-2314 /
  │     표시 x/y/z/magnitude → API 키 X/Y/Z/_ :2320-2326 / GetAvailableResponses 재조회 :2330-2339
  ├─ 비-Modal — AnsysMotion "State N" → state_id 항 배열 :2358-2372 / 그 외 parseLoadStep +
  │     step 키(Abaqus int / ANSYS term-array) :2379-2385 · findOperatorFromName:1311
  ├─ addComponentToQuery + GetFieldOutputVtk :2397-2400 · ID 성격 배열 5종 제거 :2413-2417
  ├─ 활성 스칼라 — operator 이름 우선, 없으면 ID 아닌 첫 배열 :2418-2448 ·
  │     다성분이면 magnitude 배열 합성 후 활성화 :2452-2476
  └─ emit fieldOutputReady(outputUGrid) :2478
```

`m_lastLoadedInputFiles`(`:934` 저장)를 되돌리는 블록은 레포에 5곳뿐이고 배치·조회 경로에는 없다. → D6

`requestVtkGeometry:2481` 은 `"All"` 이면 빈 grid 를 emit 해 하이라이트를 지우고(`:2487-2490`), `m_geometries` 에 없는 Component 는 질의 없이 오류로 끝낸다(`:2499-2504`).

### 3-8. Process — XML 생성

```
[Process] → onProcessButtonClicked                DashDataProcessorWidget.cpp:942
  ├─ 표 비면 경고 반환 :949-952 · collectResultRows:777 → PM::buildProcessPlan:18 :954
  ├─ plan.usesKpi → processResultsWithKPI 후 즉시 반환 :956-959   → D9
  ├─ plan.hasBoreBossDisplacement → 진원도 확인 대화상자 :963-971
  └─ m_isProcessing=true :973 → Yes 면 bore/boss/other 각각 processResults :977-985 /
        No 면 mergedWithoutCircularity 로 한 번에 :987-990 → m_isProcessing=false :993
```

`buildProcessPlan:18-83` 의 분류 규칙:

| 조건 | 분류 | 부가 키 |
|---|---|---|
| 행 중 하나라도 `hasKpi` | 전 행이 `kpiRequests` (다른 분류 없음) | KPI 행에만 `kpiConfig` |
| (KPI 모드) BORE/BOSS + 이름에 `CIRCULARITY` | 같은 `kpiRequests` | `calculateCircularity`·`originalName`·`name`←`circularityDpfName` |
| BORE\* + 이름에 `DISPLACEMENT`/`DISP` | `boreRequests` | `calculateCircularity=true` |
| BOSS\* + 같은 조건 | `bossRequests` | 〃 |
| 그 외 | `otherRequests` | — |

`circularityDpfName:93-101` 은 이름에서 축을 추론한다 — `x-axis` 또는 `" x"` 로 끝나면 X, y 면 Y, **그 밖은 전부 Z**. 축 표기가 없는 이름은 조용히 Z 가 된다.

```
processResults(resultRequests)                    DashDataProcessor.cpp:1464
  ├─ 선결 검사(preprocessor · 프로젝트 열림 · 해석 타입) :1466-1481
  ├─ samples/headers/rstFilesArray — 단일 파일 모드는 더미 1건 :1491-1498 /
  │     DataPreprocessor_{Set}.json 의 DOE Table 스냅샷 :1502-1531 / 실패 시 m_dataset 합성 :1533-1565
  ├─ status_{해석타입} != "Done" 인 run 제외 :1572-1612   → D10
  ├─ buildIndexMapping:2099 (sample↔run↔파일↔XML 키) :1626 · loadParameterInfo:2733 :1656
  ├─ m_availableResponses 비면 DashResponseInitializer :1663-1680 · BORE/BOSS 그룹 판정 :1687-1705
  └─ 요청마다 :1714-2039 — 중복 키 스킵 :1716 · step/substep 4분기 :1744-1813 ·
        파일명 조립 :1818-1846 · 출력 경로 getModuleDir :1863-1865 · processEvents :1872 →D3 ·
        DashResultProcessor::processSamples :1959 · writeModelInfoToXml(parameterInfo 있을 때만)
        :2007-2010 · 파일 쓰기 + processFinished :2015-2027 · processEvents :2038
  → emit allProcessFinished(completedFiles) :2042-2044

processSamples  DashResultProcessor.cpp:23 — samples 순회 :32-83, 미매핑 스킵 :33,
   10건마다 로그 + processEvents :38, runKey→runsIndex 역산 :63-71 → processSingleSample :73

processSingleSample                               DashResultProcessor.cpp:86
  ├─ dvTablePath 로 모듈 디렉토리 재조립 · "runs{N}" 항목 탐색 · 존재 확인 :112-189
  ├─ Clear() :215 → SetInputFilePathes(단일 파일) :216 → GetTimeSteps()(파일 강제 로드) :217
  └─ step/substep 결정(Modal / AnsysMotion / 일반) :244-299 → XmlWriter::appendSample :310
```

파일명은 BORE/BOSS 그룹이면 `{BORE|BOSS}_{step}_{substep}_{originalName}.xml`(`:1828-1832`), 그 외는 `{Component}_{step}_{substep}_{Name}.xml`(`:1841-1845`) — 후자에서 BORE/BOSS 컴포넌트는 끝자리 숫자를 떼어 그룹명으로 통일한다(`:1838-1839`).

**샘플 1건 = DLL 재로드 1회**다. `Clear()` 의 이유는 주석에 있다 — 다수 샘플 처리 시 파일 핸들·메모리 고갈 방지(`:213-214`). 500 run 짜리 DOE 면 세 호출이 각각 500회 돌고, 루프 뒤 DLL 은 원본 다중 파일로 되돌지 않는다. → D6

`Done` 필터는 `m_dvTableRoot` 의 `DOE Table.samples[].status_{타입}` 을 본다 — 키 조립 `statusKeyForAnalysisType:3003` · 조회 `statusForRunKey:3016` · 판정 `isRunKeyDone:3040`. 적용 조건 `:1609` 가 `!filteredRstFiles.isEmpty() && filteredRstFiles.size() != rstFilesArray.size()` 라 전부 걸러진 경우 필터가 통째로 무시된다. → D10

**KPI 경로** — `processResultsWithKPI:2047` 이 `processFinished` 를 임시 구독해 경로를 모으고(`:2054-2057`) `kpiConfig.kpiType` 으로 분기한 뒤(`:2059-2088`) 남은 일반 요청을 `processResults` 로 넘긴다(`:2095-2096`). 분기·구현 전부가 조건부 컴파일 안이다 — `DASH_BUILD_LGE_COMPSPRING`(`:2062-2071`): Modal Frequency `:3053`·Max. Side Force `:3495` / `DASH_BUILD_ILJIN_TENSIONLINK`(`:2072-2085`): Critical Buckling `:3827`·Max. PEEQ `:4108`·Min. Fatigue Life `:4387`. 5종은 `processResults` 의 스냅샷 로딩·폴백 코드를 각자 복제한다(`processModalFrequencyKPI:3095-3172` ≒ `processResults:1500-1565`). → D11 빌드 가드는 `DashDataProcessor.cpp:2062`·`:2072`·`:3046`·`:3793`, `DashDataProcessor.h:90`·`:94`, `KPIConfigDialog.cpp:56`·`:59`·`:62` 소스 3파일 9블록에 흩어져 있다. → D12

산출은 디스크의 XML 묶음과 `allProcessFinished` 로 넘어간 경로 리스트다. 표·선택·DLL 상태는 배치 전으로 되돌지 않는다.

### 3-9. 재진입과 복원

설정 JSON(`configs/DataPreprocessor_{Set}.json`)에 쓰이는 섹션은 4개이고 **읽는 코드가 있는 것은 둘뿐**이다.

| 섹션 | 쓰는 곳 | 읽는 곳 | 상태 |
|---|---|---|---|
| `DOE Table` (samples·headers·output) | `saveDoeTableSnapshot:2692` | `processResults:1512-1521` · KPI 5종 각각 | 복원됨 (배치 입력으로만) |
| `Dataset.Selected DV-Table` / `.Selected Analysis File` | `updateDatasetConfig:2644` | **레포에 없음** | 소실 → D7 |
| `Output Response` | `PM::saveOutputResponse:127` | **레포에 없음** | 소실 → D7 |
| 플롯 설정 | `updateConfigFile:2563` | `DashPlotSpecBuilder::build` | 복원됨 |

**재진입은 항상 빈 화면에서 시작한다.** `setModel:97` 이 하는 복원은 `findDvTableFiles():409` 하나 — 콤보 목록을 다시 채우고 `setCurrentIndex(-1)`(`:142`)로 미선택 상태로 둔다. 이전 세션의 DOE·해석 타입·Output Response 는 화면에 돌아오지 않는다(파일에는 적혀 있다). 세션 내 재진입도 같다 — `setModel:103` 이 이전 모델 연결을 끊고 콤보를 다시 채우지만 `resultTable` 은 지우지 않는다. → D1

### 3-10. 크리티컬 패스 밖의 경로

| 경로 | 좌표 | 요점 |
|---|---|---|
| **단일 파일 Import** | `:541` → `QFileDialog` → `loadRstDataDirectly:671` | DOE 를 거치지 않는 두 번째 진입. 확장자를 `SupportedResults` 4종(`.rst`·`.dfr`·`.odb`·`.op2`)과 대조하고 `.rst` 면 `GetAnalysisInfo()` 로 Static/Modal 판정(`:712-743`). `DatasetItem.type` 은 **Modal 일 때만 해석 타입**, 그 외엔 파일 basename(`:756-762`) — 그대로 3-4 의 Modal 판정 입력 → D4 |
| **단일 파일 모드 표식** | `m_dvTablePath` 빈 문자열 | `loadRstDataFromTable:804-818`·`processResults:1491-1498` 이 이 값으로 갈래를 정하고 배치는 더미 샘플 1건으로 돈다 |
| **빌드 타깃별 KPI 노출** | `KPIConfigDialog.cpp:54-66` | `COMPCBLOCK`→Circularity / `COMPSPRING`→Max. Side Force·Modal Frequency / `TENSIONLINK`→Max. PEEQ·Critical Buckling Load·Min. Fatigue Life. `Dev` 는 목록이 비고 3-8 의 배치 분기도 같은 매크로 안이라 Custom KPI 토글이 빈 대화상자까지만 도달 |
| **Data Analysis 탭** | `currentChanged:511` → `onTabChanged:1084` → `setSetName`+`initializeTargetData` `:1093-1099` | 산출 XML 을 되읽는 확인용 면. 공유 위젯이고 XML 을 고치는 경로는 없다 |
| **Target Data 콤보** | `…::updateDataPreprocessorSecondaryCombo:1171` | 폴더 안 `*.xml` 나열 |
| **플롯 요청** | `plotRequested` → `requestPlot:2536` → `updateConfigFile:2563` → `DashPlotSpecBuilder::build:2555` → `plotSpecReady` → `analysisResultReady` → `DashMainWindow::onPlotReady` | — |

`initializeTargetData` 의 DataPreprocessor 분기(`:487-514`)는 `ioCtrl->getUserPath()` 아래 `DataPreprocessor_*` 폴더를 전부 나열한다 — **다른 Set 의 산출물도 함께 보인다.** `getUserPath()` 가 `m_projectRootDir` 을 그대로 돌려주고(`DashIOController.h:97`) 출력 경로(`getModuleDir:34-36`)도 같은 뿌리라 방금 만든 XML 이 그대로 잡힌다. `initializeTargetData:370-391` 은 100ms 안의 동일 호출을 `static QHash` 로 스킵한다 — `setModel:400`·`onTabChanged:1098` 의 연달은 호출 대응이다.

---

## 4. 상태 소유 지도

| 상태 | 1차 보관 | 병행 보관 | 배치가 읽는 곳 |
|---|---|---|---|
| 선택된 DOE | `m_dvTablePath` | 콤보 `currentIndex` · 설정 JSON `Dataset` | `m_dvTablePath` |
| 원본 DOE JSON | `m_dvTableRoot` | 설정 JSON `DOE Table` 스냅샷 | **스냅샷 우선**, 실패 시 `m_dataset` 합성 |
| 해석 타입 | `m_currentAnalysisType` | `m_selectedType` · `m_currentStatusKey` | 폴더 경로는 `m_currentAnalysisType`, 항목 필터는 `m_selectedType` |
| 결과 파일 목록 | `m_dataset` | `m_lastLoadedInputFiles` · DLL 내부 상태 | `m_dataset` (경로 재조립) |
| 선택 그룹 | 체크박스 property 2종 | `m_selectedType` · `m_selectedBaseName` | 모델 멤버 |
| Component 정의 | `m_geometries` | Component 리스트 항목 텍스트 | `m_geometries` |
| Name↔operator 매핑 | `m_availableResponses` | Name 트리 구조 | `m_availableResponses` |
| Modal 모드 정의 | `m_modalDefs` | Load Step 트리 `"Mode N"` 텍스트 | `m_modalDefs` (정규식 역인출) |
| Output Response 행 | `resultTable` 셀 텍스트 | 설정 JSON `Output Response`(쓰기 전용) | **셀 텍스트** |
| KPI 설정 | 0열 `Qt::UserRole` 의 `KPIConfig` | — | 셀 `data()` |
| Preview 스칼라 이름 | `m_previewDisplayName` | — | `DashMainWindow.cpp:1342` 가 역참조 |
| DLL 로드 상태 | `m_preprocessor` 내부 | `m_lastLoadedInputFiles` | 매 샘플 재설정 |

**Output Response 의 정본이 표 셀이다.** `collectResultRows:777-792` 가 `resultTable->item(i, 0..2)->text()` 를 그대로 읽어 요청으로 만든다 — Morphing 의 "범위값 정본이 트리 셀 위젯" 과 같은 계급의 잔여 지점이다.

---

## 5. 결함 목록

3\~4절 서술 중 동작이 의도와 어긋나거나 어긋날 수 있는 지점. `D` 잘못 구현된 것 12건 · `U` 구현되지 않은 것 3건. ID 는 3절 등장 순서, 우선순위 판정은 하지 않는다. 9개 모듈 교차 색인은 [Cross-Module-Defect-Index](Cross-Module-Defect-Index.md).

| ID | 분류 | 결함 | 좌표 | 근거와 귀결 |
|---|---|---|---|---|
| **D1** | 진입·수명 | Set 전환이 Output Response 표를 비우지 않는다 | 3-1·3-9 | `setModel:97-409` 에 `resultTable` 초기화가 없고 비우는 곳은 `onLoadButtonClicked:641-642` 뿐 → **이전 Set 의 행이 새 Set 에 붙고**, 그대로 Process 하면 `collectResultRows:777` 이 그 행을 새 Set 의 요청으로 만든다 |
| **D2** | 진입·수명 | 조기 반환 4곳이 `endProcessing()` 을 건너뛴다 | 3-3 | `:367`·`:394`·`:425`·`:529` 가 `return` 만 한다 → `m_loadingDepth`(`:2686`)가 0 으로 안 돌아와 인디케이터가 켜진 채 남고, 이후 `beginProcessing` 도 `processingStarted` 를 emit 하지 못한다 |
| **D3** | 실행 모델 | 전 경로가 GUI 스레드 동기 실행 | 3-3·3-4·3-8 | 전용 워커·직렬 풀·게이트 0건(`SerialPool`·`PreprocessorGate` grep 0, 이 경로 3파일에 `QThread`·`QtConcurrent`·`moveToThread` 0, `controller/async/` 4종은 외부 프로세스용·참조 0). 응답성을 `processEvents` 25곳이 대신 떠받친다(`DashDataProcessor.cpp` 14 · `DashResultProcessor.cpp` 8 · 위젯 3) → 이벤트 루프가 열려 입력이 재진입한다(D9 와 연쇄). 막는 것은 `:313` 한 곳뿐 |
| **D4** | 데이터 정본 | Modal 판정이 문자열 포함 검사 | 3-4·3-10 | `m_isModalAnalysis = selectedType.toLower().contains("modal", …)`(`:940`). `selectedType` 은 `GetAnalysisInfo()` 의 `"analysis"` 값이거나(rst), 포맷 기본값이거나(`odb`→`Static`), 단일 파일 모드에서는 **파일 basename**(`:756-762`) → 이름에 modal 이 든 파일 하나로 모듈 전체가 Modal 모드가 된다 |
| **D5** | 구조·결합 | `isAnsysMotion` 플래그에 `hasFunctionExpression` 이 들어간다 | 3-4 | `:1200` 이 그 값을 싣고 뷰는 이 플래그로 Load Step 트리를 끈다(`:306`) → 이름과 의미가 어긋난 채 계약이 성립해 있다. 진짜 AnsysMotion 판정이 필요해지면 재사용 불가 |
| **D6** | 진입·수명 | 배치 후 DLL 상태 복원이 경로마다 있고 없다 | 3-5·3-7·3-8 | `processSingleSample:215-217` 이 DLL 상태를 마지막 run 하나로 바꾼다. 되돌리는 블록은 `requestVtkPreview:2241` 과 KPI 4종 말미(`:3786`·`:4099`·`:4381`·`:4666`) 5곳뿐 — **일반 배치 `processResults:1464-2044`·`processModalFrequencyKPI:3053-3487` 와 조회 `onSelectionChanged:1330`·`requestVtkGeometry:2481` 에는 없다** → 일반 Process 뒤의 선택은 마지막 run 파일 하나 위에서 질의하고, Preview 를 거치면 복원돼 증상이 조작 순서에 따라 갈린다 |
| **D7** | 데이터 정본 | 설정 JSON 4섹션 중 2개가 쓰기 전용 | 3-4·3-6·3-9 | `Dataset`(`updateDatasetConfig:2644`)·`Output Response`(PM `:127`)를 읽는 코드가 레포에 없다. Add·Remove 마다 파일 I/O 1회를 쓰고도 → **재진입 시 DOE·해석 타입·Output Response 가 전부 초기화된다** |
| **D8** | 데이터 정본 | KPI 행 추가가 설정 JSON 에 기록되지 않는다 | 3-6 | Add·Remove 는 `saveOutputResponseToJson`(`:754`·`:774`)을 부르지만 `addKpiToResultTable:1216-1236` 은 부르지 않는다 → KPI 행은 표에만 존재. D7 로 표 자체가 복원되지 않아 결과는 같지만 기록 경로 유무가 행 종류마다 다르다 |
| **D9** | 실행 모델 | KPI 경로가 재진입 가드 밖에 있다 | 3-8 | `plan.usesKpi` 반환이 `:958`, `m_isProcessing = true` 는 `:973` → KPI 배치 중 `processEvents` 가 연 루프로 Add/Remove/Preview 가 재진입한다. 일반 경로도 `onProcessButtonClicked`·`onLoadButtonClicked` 자신은 가드 밖 |
| **D10** | 실행 모델 | `Done` 필터가 전부 실패한 배치에서 무력화 | 3-8 | `:1609` 의 `!filteredRstFiles.isEmpty() && size != size` → 모든 run 이 비-Done 이면 필터 결과를 버리고 원본 배열을 쓴다. 실패한 run 전량이 배치 입력이 되고 XML 은 값 없는 샘플로 채워진다 |
| **D11** | 구조·결합 | KPI 5종이 배치 입력 로딩 코드를 각자 복제 | 3-8 | `processResults:1500-1565` 의 스냅샷-또는-합성 블록이 `processModalFrequencyKPI:3095-3172` 등에 반복 → 스냅샷 스키마가 바뀌면 고칠 지점이 6곳 |
| **D12** | 구조·결합 | 한 파일이 스캔·질의·XML·KPI 4역할 | 1절·3-8 | `DashDataProcessor.cpp` 4,671줄로 코드베이스 단일 최대 파일. KPI 전용 함수 5개가 조건부 컴파일 2구간(`:3046-:3791`·`:3793-:4671`) 합 1,625줄 — 파일의 35%. 빌드 가드는 소스 3파일 9블록에 흩어져 있다 |
| **U1** | 미구현 | `.op2` 는 목록·필터에만 있고 라우팅이 없다 | 3-3 | `AnalysisFileDefines.h:24` 가 NASTRAN 결과로 등록하고 파일 대화상자 필터(`위젯:546`)와 `DashFileLocator.cpp:128` 의 결과 패턴, `DashManager.cpp:84` 의 솔버 목록에도 있지만, `initializePreprocessor:92-98` 의 확장자 분기에 NASTRAN 이 없어 `AnsysMechanical` 로 떨어진다. `SolverSettingsDialog.cpp:29` 는 NASTRAN 을 주석 처리해 경로를 넣을 수단조차 없다 → **UI 에 노출된 확장자가 경고 없이 다른 솔버로 처리된다** — 미구현 갈래를 사용자에게 열어 둔 것이 결함이다 |
| **U2** | 미구현 | `res`·`dfsxml` 분기는 도달하지 않는다 | 3-3 | `:93` 이 세 확장자를 AnsysMotion 으로 보내지만 스캐너가 등록하는 결과 확장자는 `SupportedResults` 4종뿐이라 그중 Motion 은 `.dfr` 하나. `.dfsxml` 은 `SupportedInputs` 소속(`AnalysisFileDefines.h:30`) |
| **U3** | 미구현 | `m_dynamicTables` 는 쓰기만 된다 | 3-3·4절 | `:283` 에서 채우고 `:174`·`:536`·`:667` 에서 비우는 것이 전부 — 읽는 코드가 없다. 같은 `type` 그룹이 둘 이상이면 마지막 표만 남는데 남아도 쓰이지 않는다 |

---
