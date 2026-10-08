# Optimizer — 사용자 플로우 ↔ 코드 대응

> 관련 Issue: #281
> **성격**: 독립 참조 문서. Optimizer 모듈에서 사용자 행위 하나하나가 밟는 함수 체인의 대응표 — 수정 계획·우선순위 판정은 담지 않는다.
> **좌표 기준**: `dev` @ `4c7608e` 실측. 줄 번호·카운트는 이 커밋 기준이다(유효기간 있음).
> **검증 수준**: 정적 코드 근거만. 빌드·실행 검증 없음. 최적화 엔진(`DashOptiDeepOpt.exe`)은 별도 저장소라 GUI 호출측 코드로만 확인했다.

## 개요

Optimizer 는 탭 3면과 소스 5종(4,393줄)이 외부 실행파일 하나를 JSON 왕복으로 부리는 구조다. 최적화 알고리즘은 GUI 안에 없다 — 이 모듈이 하는 일은 앞선 모듈들의 산출물을 읽어 설정 JSON 을 조립하는 것뿐이고, 그래서 로직의 자리를 **경로·키 문자열 계약**이 차지한다. 판정 대부분이 타입이 아니라 문자열 비교다.

왕복은 둘로 갈린다. 설정 왕복(표 채우기·값 편집)은 GUI 안에서 동기로 끝나고, 실행 왕복(최적화·형상 프리뷰)은 외부 프로세스나 모핑 엔진을 탄다. 두 왕복이 만나는 지점이 [Run Optimizer] 한 번이고, 그것이 이 모듈의 유일한 영속화 지점이다.

3\~5절은 코드가 하는 일만 적고, 결함은 6절에 모았다 — 본문 `→ D{n}` · `→ U{n}` 이 링크다.

---

## 1. 탭 3면과 소유 클래스

우측 dock 스택의 한 페이지다(`view/DashMainWindow.cpp:508-511`). 카테고리 `"Optimizer"` ↔ 위젯 매핑은 `registerCategoryWidgets:517` 안의 한 줄(`:525`).

| 탭 | 화면 구성 | 조립 함수 |
|---|---|---|
| **Optimization** | 수직 스플리터 3단 — Trained Surrogate Model / Design Variables / Configuration + [Run Optimizer] | `setupOptimizationTab:214` |
| **Validation** | 표 3단(목적·구속 / 설계변수 / 응답) + 후보해 추가 3종 + [Render Preview] | `setupValidationTab:224` |
| **Results Analysis** | `DashResultsAnalyzerWidget` 임베드 (Optimizer 모드) | `setupAnalysisTab:268` |

세 탭은 `QTabWidget` 하나에 들어 있고 전환은 `onTabChanged:1163` 이 받는다.

| 클래스 (줄) | 담당 |
|---|---|
| `DashOptimizerWidget` (2,200 + h 185 + ui 377) | 탭 3면 전부. 표 3종 조립 · 실행 트리거 · 프리뷰 오케스트레이션 |
| `DashOptimizer` (1,531 + h 156) | Set 1개의 정본. 설정 JSON 입출력 · 프로세스 실행 · 단건 모핑 |
| `…PresentationModel` (213) | 상태 없는 변환 함수 11종 — 방법 카탈로그 · 헤더 분류 · 소스 파싱 |
| `DashOptimizerJsonParser` (72) | `optimum.json` → 플로터용 행렬 |

외부 의존은 `DashIOController`(모든 경로 산출의 단일 창구) · `ProcessJob`(외부 exe 구동, 최적화·피팅 각 1개) · `DashMorphingDoeExecutor`(프리뷰 모핑 — DOE 배치와 **같은 실행기**) · `DashSolverNxCad`(CAD 프리뷰용 NX 데몬) · `DashResultsAnalyzerWidget`(플롯 패널).

계층 배치의 특징 둘이 이후 절에서 반복 등장한다.

- **모델이 GUI 싱글턴을 역참조한다** — `DashOptimizer::performMorphing:1386` 이 `DashManager::Mgr()->GetHandlePickingInteraction()` 으로 모핑 모듈의 인터랙션 인스턴스를 직접 잡는다(`:1472`).
- **프리뷰의 요청자와 수신자가 다르다** — CAD 프리뷰를 요청하는 것은 Optimizer 위젯, 결과 STEP 을 받아 렌더하는 것은 `DashMainWindow` 다.

`DashOptimizer` 는 Set 마다 1개씩 생성되어 `DashProject::m_optimizers` 에 담긴다. 생성 4경로(`DashProject.cpp:89` 신규 기본 Set1 · `:793` 사용자 추가 · `:1202` configs 스캔 복원 · `:1392` 모듈 폴더 스캔 복원)가 전부 `addOptimizer:417` 로 수렴하고, 거기서 `setProjectDirectory`(`DashOptimizer.cpp:126`) 끝의 `loadAllData()` 가 즉시 돌아 **위젯이 열리기 전에 이미 1회 파싱**된다.

---

## 2. 전체 동선

```
1. 진입       프로젝트 트리에서 Optimizer Set 클릭 → 우측 dock 전환 + 표 2종 채움
              ※ 진입할 때마다 model_info.json 과 설정 JSON 을 다시 읽는다
2. 학습 결과  ModelBuilder 폴더 콤보 → 응답별 대리모델 콤보 (선택 즉시 지표 칸 교체)
              ※ 최적화 모드(결정론/신뢰도기반)는 데이터가 정한다 — 사용자 선택 불가
3. 설계변수   Fixed 체크로 제외 지정 · Init. Value 시작점 입력
              ※ Min/Max/Mean/Std 는 읽기 전용 — model_info.json 이 정본
4. 목적·구속  Minimize/Maximize + 수식 · [+] 로 구속 행 추가
              ※ [+] 가 심는 기본 텍스트는 편집하지 않아도 그대로 구속이 된다
5. 방법·옵션  결정론 = 방법 11종 택1 + 옵션 2칸 / 신뢰도기반 = 방법 UI 통째 숨김, SORA 고정
              ※ 방법을 바꿨다 되돌리면 옵션 2칸이 기본값으로 초기화된다
6. 실행       [Run Optimizer] → UI 강제 동기화 → 구속 연산자 검증 → JSON 기록 → exe 기동
              ※ 이 저장이 모듈의 유일한 영속화 지점이다
7. 검증       성공 시 Validation 자동 전환 → optimum.json → Optimum/Neighbor/Trajectory/MPP 열
              → DV 열 선택 → [Render Preview] → 형상 재구성 후 렌더뷰 표시
8. 플롯       Results Analysis 탭 — Convergence History · Pareto Front 2종

[산출] {프로젝트루트}/Optimizer_{Set}/optimum.json + optimization_log/convergence_history.png
       + Preview_*.dat / .inp / .stp
```

---

## 3. 단계별 대응

### 3-1. 모듈 진입

트리 클릭 하나가 두 겹의 로드를 부른다 — `DashMainWindow.cpp:1092-1094` → `handleOptimizerSelection:1509` → `setModel:107` → `populateAllWidgets:627`. 같은 클릭 안에서 `setCurrentWidget:1521` 이 dock 페이지를 바꾼다. Set **삭제**는 `:801-810` 이 `setModel(nullptr)`(`:805`) + `disconnect`(`:807`) 만 걸고, 위젯은 enabled 인 채 이전 Set 의 표를 유지한다. → D2

```
setModel(model)                                   DashOptimizerWidget.cpp:107
  ├─ setEnabled(false) · 이전 모델 연결 해제         :109-120
  ├─ connect 4종                                  :125-130
  │     dataLoaded · optimizationSucceeded · surrogateModelUpdated
  │     · fitFinished (LGE_CompSpring 빌드만)
  ├─ analyzer ↔ model 플롯 왕복 재결선             :133-140
  ├─ populateAllWidgets() · setEnabled(true)      :144 · :149
  └─ updateFitButtonState()                       :155  (LGE_CompSpring 빌드만)
```

마지막 줄의 이유를 주석이 남겨 뒀다(`:151-155`) — 자식의 명시적 `disable` 은 `WA_ForceDisabled` 로 남아 부모의 `setEnabled(true)` 로 풀리지 않으므로, 피팅 중 Set 을 전환했다 돌아오면 버튼이 "Fitting..." 비활성으로 굳는다.

```
populateAllWidgets()                              :627   ← m_isPopulating 재진입 가드
  ├─ getModelBuilderFolders()          Optimizer:1129  "ModelBuilder_*" 중 model_info.json 보유분
  ├─ 폴더 콤보 재구성 (blockSignals)     :645-656
  │     └─ PM::selectModelBuilderFolder:148   1순위 직전선택 · 2순위 setName 파생 · 3순위 첫 항목
  ├─ model->loadModelInfoFromFolder()  Optimizer:683   (blockSignals 로 dataLoaded 차단 :663-665)
  ├─ 두 표 clear → populateSurrogateTable:733 · populateDesignVariableTable:857
  ├─ 최적화 모드 색인 반영 (숨은 콤보 + 읽기전용 LineEdit)  :687-695
  ├─ populateOptimizationSettings:951 · onOptimizationModeChanged(색인):702
  └─ analyzer->setSetName()                       :708-717
```

가드 플래그 `m_isPopulating` 은 네 곳에서 읽힌다 — 자신(`:630`) · `onModelDataLoaded:596` · `onModelBuilderFolderChanged:725` · `onTabChanged:1210`.

**같은 JSON 을 최소 2회 읽는다.** `addOptimizer` 시점의 `loadAllData:548` 이 1회, 진입 시 `loadModelInfoFromFolder:683` 이 1회. 후자는 model_info.json 을 읽고 나서 설정 JSON 의 `Optimization` 섹션도 다시 읽어 덮어쓴다(`:749-763`). 두 로더의 차이는 NaN 정화 유무다 — 후자만 `NaN`·`Infinity`·`-Infinity` 를 `null` 로 치환한다(`:728-731`). → D1

### 3-2. 학습 결과 선택 — 대리모델 표

**폴더 콤보** — `currentTextChanged`(`:279`) → `onModelBuilderFolderChanged:723` → `loadModelInfoFromFolder`(blockSignals) → 두 표 재구성. **구속·방법 UI 는 갱신되지 않는다** — `populateOptimizationSettings` 를 부르지 않기 때문이다. → D3

**행 구성** — `populateSurrogateTable:733` 이 응답 하나당 1행. 9열 중 4열은 기본 숨김(`configureSurrogateTable:291-294`).

| 열 | 내용 | 채우는 곳 |
|---|---|---|
| 0 Symbol | `r{i+1}` — **행 인덱스로 재생성** | `:753` |
| 1 Response | model_info.json `errors` 의 키 | `:761` |
| 2 Model | 콤보 (그 응답의 학습 모델 목록) | `:763-771` |
| 3\~4 | R2 · MAPE[%] (1D 지표) | `updateModelErrorRow:798` |
| 5\~8 | Mean-MAPE · Peak-MAPE · Top5% WMAPE · WMAPE (ND 지표) | 같은 함수 |

**1D / ND 판별은 응답 이름의 부분문자열이다** — `info.response.contains("(Field)")`(`:755`). 첫 행의 판정 하나가 표 전체의 열 가시성을 정한다(`:756-758` → `updateTableHeadersForModelType:469`). → D4

모델 콤보 변경은 두 갈래가 동시에 간다(`:782-787`) — `updateSelectedSurrogateModel`(`Optimizer:502`)이 `surrogateModelUpdated` 를 올려 `onSurrogateModelUpdated:450` → `updateModelErrorRow` 로 가고, 같은 자리에서 `updateModelErrorRow` 를 직접도 부른다. 결과가 같아 화면 차이는 없다.

지표 출처는 `m_trainedModelErrors` 3중 맵(`response → model → metric → double`)이고 `loadSurrogateModelsFromJson:583` 이 채운다. 대표 오차 선택은 `Error [%]` → `MAPE [%]` → 첫 지표 3단 폴백(`:616-622`). **초기 선택은 최소 오차 모델**(`:628-632`)이고, 설정 JSON 에 이전 선택이 있으면 `loadSurrogateModels:827` 이 응답 이름 매칭으로 덮어쓴다.

**최적화 모드 결정** — 이 모듈에서 가장 오해하기 쉬운 지점이다. 모드 콤보는 `configureDesignVariableTable:300-305` 에서 만들어지지만 `hide()` 된 채 레이아웃에 들어가지 않는다. 사용자에게 보이는 것은 읽기 전용 `m_optimizationModeLineEdit` 이고 그 텍스트는 숨은 콤보의 복사본이다(`:693-694`). → U1

| 판정 | 위치 | 규칙 |
|---|---|---|
| 1차 | `parameterMetaHasNumericMeanAndStd`(`Optimizer:61`) | `parameter.*.meta` 에 숫자형 `mean`·`std` 가 하나라도 있으면 색인 1 |
| 2차 | `loadDesignVariables:917-926` | 설정 JSON 설계변수 중 mean·std 가 둘 다 NaN 아닌 것이 있으면 색인 1 로 승격 — **내리지는 않는다** → D5 |
| 잠금 | `m_optimizationLockFromModelInfo`(`:677-680`) | `parameter` 가 비어 있지 않을 때만 위 색인이 UI 에 반영 |

모드가 화면에 미치는 영향은 `onOptimizationModeChanged:1631` 한 함수에 모여 있다.

| 요소 | 결정론 (0) | 신뢰도기반 (1) |
|---|---|---|
| 구속 표 열 수 | 1 (헤더 숨김) | 3 — Constraint / Type / Reliability[%] |
| DV 표 Mean·Std 열 | 숨김 | 표시 |
| Methods 라벨·콤보·설명 | 표시 | 숨김 (SORA 고정) |
| Validation [Add MPP] · Fixed Variables Fitting | 숨김 | 표시 |

유효 호출처는 `populateAllWidgets:702` 하나다. 콤보의 `currentIndexChanged` 도 연결돼 있지만(`:419`) 색인을 바꾸는 유일한 코드가 `QSignalBlocker` 안이라(`:690-691`) 시그널로는 도달하지 않는다.

### 3-3. 설계변수 확정

`populateDesignVariableTable:857` 이 8열 표를 만든다 — 읽기 전용 4열 · 편집 2열.

| 열 | 위젯 | 편집 | 정본 |
|---|---|---|---|
| 0 Symbol | 아이템 (`v{i+1}` 재생성) | X | 인덱스 |
| 1 Parameter | 아이템 | X | model_info.json 키 |
| 2 Fixed | `QCheckBox` | O | 체크 = `optimize == false` |
| 3 Init. Value | `QDoubleSpinBox` 또는 `QComboBox` | O | `info.value` |
| 4\~5 Min·Max | 아이템 ("None" if NaN) | X | model_info.json meta |
| 6\~7 Mean·Std | 아이템 (신뢰도기반에서만 표시) | X | 같음 |

3열 위젯이 갈리는 조건은 `info.cases` 의 비어 있음 여부다(`:894`) — 케이스가 있으면 콤보, 없으면 스핀박스(범위 Min/Max, NaN 이면 `±1.0e10`, `:911-912`).

편집 2종은 모델에 닿지 않는다. **Fixed 체크**(`stateChanged` 람다 `:888` → `onFixedCheckBoxChanged:1822`)는 Min·Max·Mean·Std 아이템의 `Qt::ItemIsEnabled` 만 해제하고 `updateDesignVariableOptimizeFlags` 를 부르지 않는다. **Init. Value 는 시그널 연결 자체가 없다**. 두 값이 모델에 도달하는 유일한 시점이 [Run Optimizer] 다(3-6). → D6

Min/Max 아이템은 애초에 `~Qt::ItemIsEditable` 로 생성되므로(`:923`), `ItemIsEnabled` 해제는 회색 표시 이상의 의미가 없다.

### 3-4. 목적함수·구속 입력

**목적함수** — 수식은 `objectiveEdit::textChanged`(`:410`) → `onObjectiveFunctionChanged:546` → `updateObjectiveFunction(콤보텍스트, 수식)` 으로 즉시 모델에 닿는다. Minimize/Maximize 콤보는 `:185` 에서 별칭만 잡히고 수신 슬롯이 없다. → D7

**구속 표** — 초기에는 회색 예시 행 `"r1 <= 163.23"`(`configureOptimizationSettingsGroup:390-393`)이 놓여 있고, 모델 바인딩 시 `setRowCount(constraints.size())`(`:991`)로 사라진다.

| 행위 | 함수 체인 | 결과 |
|---|---|---|
| **[+]** | `onAddConstraintClicked:553` | 행 추가 + 기본 텍스트 `"r9 <= 153755.61"`(`:557`) → 편집 모드 → `updateConstraints`(`:589-590`) |
| **[−]** | `onRemoveConstraintClicked:1142` | 선택 행 **역순 정렬 후** 제거 → `updateConstraints` |
| 셀 편집 | `itemChanged`(`:411`) → `onConstraintItemChanged:442` | 글자색 검정 복원 + `updateConstraints` |
| Type 콤보 (신뢰도기반) | 람다(`:1051`) → `onConstraintTypeChanged:1809` | Probabilistic 일 때만 Reliability 스핀 활성 |
| Reliability 스핀 | 람다(`:1058`) | `updateConstraints` |

**[+] 로 만든 행은 편집하지 않아도 실제 구속이 된다** — `:557` 이 심는 텍스트는 회색 예시와 달리 보통 아이템이고 같은 함수 끝에서 곧바로 모델에 들어간다. → D8

```
readConstraintsFromTable()                        :2197
  ├─ collectConstraintRows():2170  행마다 {expression, typeIndex, probEnabled, probValue}
  └─ PM::constraintsFromRows:103
        name = "G{i+1}"  ← 매번 재채번, 사용자 지정 이름 없음
        type = typeIndex != 0 ? "probabilistic" : "deterministic"
        reliability = "{value}%"   ← probabilistic + 스핀 활성일 때만
```

`populateOptimizationSettings` 의 구속 루프는 전체가 `QSignalBlocker` 로 감싸여(`:975`) 부분 구축 상태의 `itemChanged` 재진입을 막고, 셀 위젯 연결은 두 위젯이 **모두 설치된 뒤에** 이뤄지며(`:1047-1062` 주석이 정본), 행 삭제도 `removeCellWidget` → `deleteLater` 순이다(`:979-987`). 같은 함수에 `[popOS]` 접두 `qDebug` 가 27줄 들어 있다(`:953`\~`:1096`). → D9

### 3-5. 방법·옵션 선택

방법 카탈로그는 `PM::methodCatalog:37` 에 하드코딩된 11종이다.

| 방법 | 옵션 2칸 | 기본값 |
|---|---|---|
| Smart | 없음 | — |
| SQP · Trust-region · Nelder-Mead · Conjugate gradient · L-BFGS-B · Powell · TNC | iteration · tolerance | 10 · 0.000001 |
| GA / PSO / DFL\_TLBO | population · iteration | 30 · 30 / 30 · 10 / 30 · 100 |

콤보 변경은 `currentIndexChanged`(`:414`) → `onMethodSelectionChanged:1100` 하나로 가고, 그 안에서 설명 라벨 갱신 · 옵션 2칸 표시/숨김 · **기본값 주입**(`:1120-1132`, `PM::defaultOption1Text:54`·`defaultOption2Text:61`)이 함께 일어난다. 저장값 복원은 `populateOptimizationSettings:1078-1093` 이 이 슬롯을 부른 **직후 덮어쓰는 순서**로만 성립한다. → D10

이 슬롯은 생성자 단계에서도 한 번 불린다 — `setupConnections:438` 의 `onMethodSelectionChanged(0)`.

### 3-6. 실행

[Run Optimizer] 한 번이 UI 전체를 모델로 밀어넣고 프로세스를 띄운다. `saveSettings()` 의 호출처는 `runOptimization:199` 하나뿐이다. → D12

```
[Run Optimizer] → onRunButtonClicked                DashOptimizerWidget.cpp:490
   ├─ updateObjectiveFunction(콤보, 수식)             :498-501   ← 강제 동기화
   ├─ updateConstraints(readConstraintsFromTable())  :502
   ├─ DV 표 순회  2열 체크 → optimize · 3열 위젯 → value(없으면 NaN)   :509-521
   ├─ updateDesignVariableOptimizeFlags / …Values    :522-523   (NaN 은 건너뜀)
   ├─ 신뢰도기반이면 setMethod("SORA") → runOptimization → return   :527-531
   └─ setMethod · setMethodOptions(PM::buildMethodOptions) · runOptimization   :538-543
```

강제 동기화의 의도는 주석이 남겨 뒀다(`:494-497`) — 위젯 시그널이 아직 발화하지 않았을 수 있으므로(예: 셀 편집 도중 Run) 여기서 다시 읽는다. 신뢰도기반 분기는 `setMethodOptions` 를 부르지 않고, `m_methodOptions` 가 비어 있으면 모델이 SORA 기본값 6종을 심는다(`Optimizer:480-487` — `max_budget` 900 · `max_cycles` 30 · `design_tolerance` 0.001 · `shift_tolerance` 0.001 · `inverse_form_solver` "SLSQP" · `statistics_sample` 100).

```
runOptimization()                                 DashOptimizer.cpp:158
  ├─ if (m_currentJob) → 경고 + logMessage + return         :160-165
  ├─ 구속 순회 — "<=" ">=" "<" ">" 중 하나도 없으면 실패 반환  :172-190
  │     (== 는 미지원 경고만 내고 진행)                       :191-196
  ├─ saveSettings()                                        :199
  ├─ 경로 산출                                              :219-232
  │     outputDir = getModuleDir(Optimizer, setName)
  │     trainedModel = getModuleDir(ModelBuilder, mbSetName)   ← "ModelBuilder_" 접두면 mid(13)
  │     exe = extensions/deep_opt/DashOptiDeepOpt.exe
  ├─ ProcessJob(exe, args) · ChannelMode::Separate         :254-255
  │     args = run-optimization {trainedModel} {optJson} --output-dir {outputDir}
  └─ connect outputLine/finished → job->start()            :256-
```

**중복 실행 방지는 모델에만 있다.** 위젯이 `runButton` 을 비활성화하지 않아 연타가 그대로 들어오고 `m_currentJob` 가드가 두 번째부터를 튕겨낸다 — `:160` 주석이 이를 명시한다. 튕긴 사실은 `logMessage` 로만 알려진다. → D13

**설정 JSON 조립** — `saveSettings:348` 은 read-merge-write 로 `Optimization` 섹션만 갈아끼운다.

| 키 | 생성 함수 | 내용 |
|---|---|---|
| `trained_surrogate_model` | `createSurrogateModelJsonArray:405` | `{model, response, symbol}` 배열 |
| `design_variables` | `createDesignVariableJsonArray:420` | `{symbol, parameter, value, min, max, mean, std, optimize}` — NaN 은 `"None"` |
| `sampling_mode` | 인라인 `:369-373` | SORA 면 `"probabilistic"`, 아니면 키 삭제 |
| `optimization_settings` | `createOptimizationSettingsJsonObject:444` | methods · objective\_function · use\_constrained\_function · constrained\_functions · configs |

정리 동작 둘이 함께 돈다 — 레거시 `"Results Analysis"` 섹션 제거(`:358`)와 UI 소유 키의 무조건 덮어쓰기(`:381-383`, 주석이 이유를 남겼다: 이전에는 SORA 경로가 기존 값을 보존해 낡은 JSON 이 현재 입력을 가렸다). `objective_function.type` 은 UI 가 정하지 않고 `m_method == "SORA"` 여부로 매번 재계산된다(`:452`). 끝의 `settingsSaved()` emit(`:392`)은 수신처가 없다. → U2

**프로세스 통지** — stdout 줄은 `onOutputLine:930` 이 받아 `"[GUI]"` 접두면 `logMessage` 로, 아니면 버퍼에 쌓는다. stderr 는 구독하지 않는다(도구가 진행 표시를 stderr 로 냄 — `:252-253` 주석). `onJobFinished:941` 이 성공이면 `optimizationSucceeded({optimizerDir}/optimization_log/convergence_history.png)`, 실패면 `optimizationFailed(fullOutput)` 을 올린다.

**`optimizationFailed` 는 레포 전체에 수신처가 없다** — 선언(`DashOptimizer.h:95`)과 emit 4곳(`:188`·`:207`·`:214`·`:978`) 외에 `connect` 가 없다. → D11

| 실패 지점 | logMessage | 사용자가 보는 것 |
|---|---|---|
| 구속 연산자 누락 (`:186-188`) | O | 로그 dock 메시지 (열려 있을 때) |
| ProjectManager/IOController 부재 (`:207`·`:214`) | X | **아무것도 없음** |
| 프로세스 실패 (`:978`) | X | **아무것도 없음** |

성공하면 `onOptimizationSucceeded:602` 가 탭을 Validation 으로 옮기고 모달 2개를 띄운다 — `QMessageBox::information`(`:606`)과 수렴 이미지가 있을 때 800×600 `QDialog::exec()`(`:611-622`). 그래서 **응답 없음 = 실패**가 사실상의 판별법이 된다.

### 3-7. 결과 검증 — Validation 탭

```
onTabChanged → currentWidget == validationTab     :1170
  ├─ model->loadValidationData()   Optimizer:1035   {optimizerDir}/optimum.json 파싱
  │     meta.item[] → headers · data[].name 별로 optimumValues/neighbors/trajectories/mpps
  ├─ 표 3개 clear + 행/열 0                         :1176-1178
  ├─ PM::classifyValidationHeaders:125 → 세로 헤더 3벌 · 스핀 최대치 clamp(개수,1,5)
  └─ addSolutionColumn("Optimum", optimumValues)   :1201
```

**헤더 분류가 문자열 규칙 3단이다**(`PM:130-144`) — `item == "objective"` 또는 `item.startsWith("constraint")` 면 목적·구속 표, `item.startsWith("r")` **그리고** 두 번째 글자가 숫자면 응답 표, `item == "id"` 면 버림, 그 외 전부 설계변수 표. → D14

탭에 다시 들어올 때마다 표는 통째로 지워지고 Optimum 열부터 다시 쌓인다 — 후보해 누적은 세션 안에서만 유지된다.

**후보해 추가** 3버튼은 기존 열 개수를 헤더 텍스트 접두로 세어 이어붙인다 — Add Neighbor(`:1267`, 접두 `"Neighbor"`) · Add Trajectory(`:1287`, `"Trajectory"`) · Add MPP(`:1307`, `"MPP_"`). `addSolutionColumn:1234` 이 세 표에 동시에 열을 넣고, `m_objConstIndices`·`m_dvIndices`·`m_respIndices` 로 원본 배열 성분을 행에 되짚는다 — 이 세 리스트가 분류 결과를 유지하는 유일한 상태다.

**[Render Preview]** 가 모듈에서 가장 긴 함수를 부른다(`onPreviewButtonClicked:1326`, 300줄).

```
[Render Preview] → onPreviewButtonClicked          :1326
   ├─ val_dvTable 열 1개 선택 확인 → QMap<파라미터명, 값>   :1333-1353
   ├─ model_info.json 읽기 + NaN 정화 (PM::sanitizedModelInfoJson:161)   :1372-1402
   ├─ PM::findGeometryParameterJsonPath:166
   │     parameter.*.source 중 ".json" 으로 끝나고 "GeometryParameter" 포함 + 실재하는 첫 파일
   ├─ GeometryParameter JSON → DV-Geometry          :1419-1434
   ├─ PM::resolveGeometrySource:183   1순위 검증 탭 행 이름과 같은 키 · 2순위 전체 키 순회
   │     source 형식 "Morphing|{deck}|{part}" 또는 "CAD|{prt}"  (parseDvSource PM:10-28)
   └─ isMorphing / isCad 분기                        :1460 / :1597
```

**모핑 갈래**(`:1460-1594`) — configs 의 `*.dat`+`*.inp` 전량을 나열해(`:1467-1470`) 템플릿마다 `performMorphing` 을 돌리고, 산출 deck 이 생기면 `.vtu` 와 `_input_geometry.vtu` 를 곧바로 지운 뒤(`:1503-1510`) **마지막 산출 deck 만 렌더**한다.

`resolveGeometrySource` 가 뽑아낸 `templateFileName` 은 비어 있는지만 검사되고(`:1461`) 루프 자체는 폴더 전량을 돈다 — 템플릿 필터가 걸리지 않는다. → D15
이 루프가 모듈 `processEvents` 2곳의 자리다(`:1489` 실패 시 · `:1514` 매 반복). → D16
`performMorphing` 이 deck 생성 후 뽑는 `_input_geometry.vtu`(`Optimizer:1516-1528`)를 호출부가 즉시 지운다. → D17

```
performMorphing(dvValues, datPath, targetPart, outVtuPath)   DashOptimizer.cpp:1386
  ├─ validateMorphingParameters:1181 · ContextRegistry::getOrLoad(deck)  ← RW 로 deck 적재
  ├─ loadModelInfoJson:1213 (NaN 정화) · findGeometryParameterFile:1309
  ├─ loadGeometryParameterAndCreateSample:1345
  │     Morphing.handles / DV-Geometry 추출 → DashMorphingUtils::createSampleFromDesignVariables:197
  │     kernelRadius = Morphing.radius (기본 10.0)
  ├─ DashManager::Mgr()->GetHandlePickingInteraction()   :1472   ← GUI 싱글턴 역참조
  ├─ createMorphOperator:1479 · loadHandlesFromVtp:1481 → MorphingUtils:39
  ├─ 출력 deck 경로 = {optimizerDir}/{vtu basename}.{입력 확장자}   :1487-1495
  ├─ performMorphingAndExport:1498 → MorphingUtils:267
  │     └─ DashMorphingDoeExecutor::ExecuteOneSample:544   ← DOE 배치와 같은 실행기
  └─ deck 이 생겼으면 extractPartVtuFromDat → _input_geometry.vtu   :1516-1528
```

`loadHandlesFromVtp` 는 **GUI 가 지금 쓰고 있는 `DashHandlePickingInteraction` 인스턴스를 직접 덮어쓴다** — `SetBoxHandles`(`MorphingUtils:91`) 다음 VTP 배열 6종을 `DeepCopy` 로 갈아끼운다(`:96-150`). 프리뷰 1회가 모핑 모듈의 핸들 상태를 바꾼다. → D18

`ExecuteOneSample` 의 deck 쓰기 구간 주석(`DashMorphingDoeExecutor.cpp:890-899`)이 이 경로의 실행 모델을 명시한다 — "여기서 edit\_data/edit\_mesh 로 건드리는 것은 GUI 가 렌더링 중인 바로 그 세션이다… 지금 레이스가 아닌 이유는 이 경로가 GUI 스레드에서 돌기 때문일 뿐이다." 정합성은 `:927-930` 의 원복 두 줄에만 기대고 있다. → D16

렌더 단계는 렌더러를 통째로 비운다 — `registry.activeActor()` 제거(`:1534-1537`) · 액터 전량 `RemoveActor`(`:1539-1550`) · `clearLayer(BASE_GEOMETRY/COMPONENT_GEOMETRY/RESULT)`(`:1552-1554`) · **`registry.setActiveContext(마지막 산출 deck)`**(`:1556`) · 파트 전량 `vtkAppendFilter` 합성 후 `resetCamera`. 활성 컨텍스트는 프리뷰가 끝나도 되돌아가지 않는다. → D18

**CAD 갈래**(`:1597-1627`) — `solverNxCad()` 확보 → configs 의 `{prt}` 실재 확인 → `PM::buildCadConfigJson:209` → stp 경로 선삭제 → 부모를 거슬러 `DashMainWindow` 를 찾아 상태 애니메이션 시작(`:1618-1622`) → `enqueueUpdatePrtGeometry(prt, stp, configJson)`(`:1624`).

완료는 요청과 짝지어지지 않는다. 데몬이 명령을 끝내면 `onCommandCompleted:187` 이 `m_batchMode` 전역 플래그로 배치용/단건용 시그널을 가르고(`DashSolverNxCad.cpp:200-206`), 후자를 받는 곳은 `DashMainWindow.cpp:281` 의 람다 → `onNxPreviewStepReady:2413` → `previewStepFile(stp)` 다. → D19

### 3-8. 결과 플롯 — Results Analysis 탭

임베드된 `DashResultsAnalyzerWidget` 은 생성자 인자로 `Optimizer` 모드를 받고(`:271`), 이 모드는 대상 선택 콤보 3개가 비어 있고 방법이 2종뿐이다(`DashResultsAnalyzerWidget.cpp:269-276`) — Convergence History(`convergence`) · Pareto Front(`pareto_2d`/`pareto_3d`).

```
onTabChanged → analysisTab                         :1208
  ├─ m_isPopulating 이면 즉시 반환                   :1210
  └─ analyzer->setSetName() · initializeTargetData()  :1217-1219
        └─ Optimizer 모드(:942)  optimum.json 실재 확인 → meta.item[] → m_variables
              → updateMethodWidgetsWithVariables  Convergence 1열 콤보 / Pareto 축 2열 콤보

analyzer::plotRequested → DashOptimizer::requestPlot:1117
  ├─ DashPlotSpecBuilder::build(command, m_optimizationJsonPath, "", settings, msgs)
  │     configFilePath 실재 검사 — 없으면 빈 객체 (SpecBuilder:18-23)
  │     dataPath = settings["target_optimum_path"]            (SpecBuilder:107-120)
  └─ emit plotSpecReady → analyzer::onPlotSpecReady:3166
        → DashPlotWidgetFactory → DashOptimizerJsonParser::load(optimum.json)
        → analysisResultReady → DashMainWindow::onPlotReady
```

**설정 JSON 은 게이트로만 쓰인다** — 실재 검사만 하고 실제 데이터는 `optimum.json` 에서 온다. → D20

같은 파일 경로가 한 함수 안에서 두 방식으로 유도되는 지점도 있다(`processOptimizerPlot:2607`) — `target_optimum_path` 는 `getUserPath()` + 문자열 조립(`:2627-2628`), 헤더 읽기는 `getModuleDir(Optimizer, setName)`(`:2634`). `getModuleDir` 은 ModelBuilder 만 숨김 폴더를 쓰므로(`DashIOController.cpp:31-36`) 오늘 두 경로는 같은 파일을 가리킨다. 규칙이 두 벌일 뿐 불일치는 아니다.

### 3-9. 재진입과 복원

| 복원 대상 | 저장처 | 읽는 곳 | 상태 |
|---|---|---|---|
| 대리모델 선택 | JSON `trained_surrogate_model` | `loadSurrogateModels:827` — 응답 이름 매칭 | 복원됨 |
| 설계변수 전량 | JSON `design_variables` | `loadDesignVariables:877` | 복원됨 |
| 목적함수 · 구속 전량 | JSON `optimization_settings` | `loadOptimizationSettings:784-800` (레거시 배열 포맷도 수용) | 복원됨 |
| 방법 · 방법 옵션 | 같은 섹션 `methods`/`configs` | `:777-781` → 표 반영은 `populateOptimizationSettings:1078-1093` | 덮어쓰기 순서 의존 → D10 |
| 최적화 모드 | 저장 안 함 — 매번 재판정 | `parameterMetaHasNumericMeanAndStd:61` + `loadDesignVariables:917-926` | 단방향 승격 → D5 |
| ModelBuilder 폴더 선택 | — | `m_activeModelBuilderFolder` 는 `:704` 에서만 세팅 | 세션 내 → D21 |
| 검증 표 후보해 열 | — | 탭 진입마다 `:1176-1178` 이 clear | 소실 |
| Run 없이 편집한 DV Fixed·Init. Value·방법·옵션 | — | 모델에조차 도달 안 함 | 소실 → D6 · D12 |

Set 을 **삭제**하면 `DashMainWindow.cpp:801-810` 이 `setModel(nullptr)` 과 `disconnect` 를 걸지만 위젯은 `setEnabled(true)` 와 직전 표 내용을 유지한다. → D2

### 3-10. 크리티컬 패스 밖의 경로

**LGE Spring 고정변수 피팅 — 빌드 타깃 전용.** `DASH_BUILD_LGE_COMPSPRING` 가드 블록 18개(위젯 cpp 8 · h 3 · 모델 cpp 3 · h 4). UI 는 DV 표 아래에 런타임 조립되고(`configureDesignVariableTable:319-385` — CSV 경로 표시줄 · 업로드 · Download Format · Fit Variables) 신뢰도기반 모드에서만 보인다(`:1798`).

| 행위 | 함수 체인 | 결과 |
|---|---|---|
| 업로드 | `onUploadCsvClicked:1882` | `QFileDialog` → 읽기전용 LineEdit 에 경로 표시 |
| Download Format | `onDownloadFormatClicked:1892` | 8줄 CSV 템플릿 직접 기록 (6행 + 데이터 2행) |
| Fit Variables | `onFitVariablesClicked:1933` → `runFitVariables:268` | 별도 `ProcessJob`(`m_fitJob`) |

`runFitVariables` 는 최적화 Job 과 **완전히 독립된 두 번째 실행 핸들**이다(`DashOptimizer.h:55-57` 주석이 동시 실행 가능함을 명시). 최적화와 다른 점 셋 — ① 학습 모델 경로가 하드코딩(`{projectPath}/ModelBuilder_LGE_Spring_Fitting`, `:295`) → D23 ② 작업 디렉터리가 `QCoreApplication::applicationDirPath()`(`:327`) ③ **stderr 를 구독한다**(`:333-335`, 피팅은 stderr 가 실패 메시지의 유일 정보원). 사전 검증 실패도 완료 통지로 되돌린다 — `failLater` 람다가 `QTimer::singleShot(0,…)` 으로 한 틱 미뤄 `fitFinished(false, -1, …)` 를 올린다(`:277-281`).

결과 해석은 뷰 몫이다(`onFitFinished:1962`) — stdout 을 줄 단위로 훑어 `{` 로 시작하는 지점부터 누적하며 파싱이 성공하는 첫 JSON 객체를 찾고(`:1983-1990`), `success` 와 숫자 값 유무로 3분기한다(하드 실패 / 최대 반복 도달 후 최선값 적용 / 성공). 적용은 심볼(`v1`, `v2`…)로 행을 찾아 DV 표 3열 위젯에 직접 쓴다(`:2116-2142`) — **모델의 `m_designVariables` 는 건드리지 않는다.** → D22

**`showEvent` — 로그만 하는 오버라이드.** `:159-169` 는 `QWidget::showEvent(event)` 한 줄 외에 `qDebug` 7줄이 전부다. → D9

---

## 4. 파일 계약

읽고 쓰는 파일은 5종이고 전부 `DashIOController` 를 거쳐 경로가 만들어진다.

| 파일 | 위치 | 방향 | 만드는 곳 |
|---|---|---|---|
| `Optimizer_{Set}.json` | `{.dproj}/configs/` | 읽기 + 쓰기 | `saveSettings:348` (GUI) |
| `model_info.json` | `{.dproj}/ModelBuilder_{Set}/` | 읽기만 | Model Builder |
| `GeometryParameter_{Set}.json` + `.vtp` | `{.dproj}/configs/` | 읽기만 (프리뷰) | Geometry Parameterization |
| `optimum.json` · `optimization_log/convergence_history.png` | `{프로젝트루트}/Optimizer_{Set}/` | 읽기 / 존재 확인 | `DashOptiDeepOpt.exe` |
| `Preview_*.dat` / `.inp` / `.stp` | 같음 | 쓰기 | 프리뷰 경로 |

```
getConfigsDirectory()  = {.dproj}/configs
getConfigFilePath(T,S) = {.dproj}/configs/{모듈명}_{S}.json
getModuleDir(T,S)      = ModelBuilder 면 {.dproj}/ModelBuilder_{S}
                         그 외      면 {프로젝트루트}/{모듈명}_{S}
```

**설정과 결과가 서로 다른 뿌리에 산다** — 설정 JSON 은 숨김 폴더 `.dproj/configs`, 결과 `optimum.json` 은 사용자가 보는 프로젝트 루트. 학습 결과(`model_info.json`)만 예외적으로 숨김 폴더다(`DashIOController.cpp:31-36`).

```jsonc
{ "Optimization": {
    "trained_surrogate_model": [ { "model": …, "response": …, "symbol": … } ],
    "design_variables": [ { "symbol": …, "parameter": …, "value": …, "min": …, "max": …,
                            "mean": …, "std": …, "optimize": … } ],   // NaN 은 문자열 "None"
    "sampling_mode": "probabilistic",                                  // SORA 일 때만 존재
    "optimization_settings": {
      "methods": "…",
      "objective_function": { "name": …, "direction": …, "type": …, "expression": … },
      "use_constrained_function": true,                                // 구속 개수 > 0
      "constrained_functions": [ { "name": …, "type": …, "expression": …, "reliability": … } ],
      "configs": { }                                                   // 방법 옵션 맵
} } }
```

`objective_function` 은 레거시 배열 포맷(`["direction","expression"]`)도 로드된다(`loadOptimizationSettings:793-800`). 쓰기는 항상 오브젝트다.

이 왕복 전체가 자동 검증 밖이다 — `tests/` 에 있는 것은 `tst_job_state.cpp`·`tst_line_assembler.cpp`·`tst_process_runtime.cpp` 로 async 트랜스포트 계층만 덮고, Optimizer 참조는 0건이다. → U3

---

## 5. 상태 소유 지도

같은 값이 위젯과 모델 양쪽에 있고, 어느 쪽이 정본인지는 **읽는 시점**에 따라 다르다.

| 상태 | 화면 보관 | 모델 보관 | 동기화 시점 |
|---|---|---|---|
| 목적 방향 | `objectiveCombo` | `m_objectiveFunction.direction` | 수식 편집 시 · Run → D7 |
| 목적 수식 | `objectiveEdit` | `.expression` | 편집 즉시 |
| 구속 전량 | `constraintTable` (셀 + 셀 위젯 2종) | `m_constraints` | 편집·추가·삭제 즉시 |
| 대리모델 선택 | 행별 `QComboBox` | `m_surrogateModels[i].selectedModel` | 선택 즉시 |
| DV Fixed · Init. Value | 행별 `QCheckBox` · 스핀/콤보 | `.optimize` · `.value` | **Run 시점만** → D6 |
| 방법 · 방법 옵션 | `methodCombo` · `option{1,2}Edit` | `m_method` · `m_methodOptions` | **Run 시점만** (SORA 는 옵션 아예 안 함) |
| 최적화 모드 | 숨은 콤보 + 읽기전용 LineEdit | `m_optimizationModeIndexFromModelInfo` | 로드 시 → U1 |
| ModelBuilder 폴더 | `m_modelBuilderFolderCombo` | `m_activeModelBuilderFolder` | 선택 즉시 → D21 |
| 검증 표 분류 | `m_objConstIndices`·`m_dvIndices`·`m_respIndices` | — | 탭 진입 시 |
| 피팅 결과값 | DV 표 3열 위젯 | — | 위젯에만 → D22 |
| 실행 중 여부 | — | `m_currentJob` / `m_fitJob` | — |

**"Run 시점만" 2행이 이 모듈의 특징적 위험**이다. 값을 바꾸고 Run 없이 Set 을 전환하면 그 변경은 파일에도 모델에도 남지 않는다. 반대로 Run 을 누르면 UI 의 현재 상태가 통째로 모델에 밀려 들어가 편집 도중이던 셀도 그대로 반영된다.

심볼(`r1`, `v1`)도 저장 값이 아니라 **행 인덱스에서 매번 재생성**된다(`:753`·`:874`) — JSON 의 `symbol` 은 로드 시에만 읽히고 표시에는 쓰이지 않는다.

싱글턴 도달 빈도는 위젯 한 파일에서 `DashManager::Mgr()` 4회(모핑 프리뷰 2 · CAD 프리뷰 1 · 렌더링 1), 모델 쪽은 `performMorphing:1472` 한 곳이다.

---

## 6. 결함 목록

3\~5절 서술 중 동작이 의도와 어긋나거나 어긋날 수 있는 지점. `D` 는 잘못 구현된 것(defect) 24건, `U` 는 구현되지 않은 것(unimplemented) 2건 (`U1` 은 예정 기능이라 제외). ID 는 3절 등장 순서이고 U2·U3 은 뒤에 붙였다. 우선순위 판정은 하지 않는다. 9개 모듈 교차 색인은 [Cross-Module-Defect-Index](Cross-Module-Defect-Index.md).

| ID | 분류 | 결함 | 좌표 | 근거와 귀결 |
|---|---|---|---|---|
| **D1** | 데이터 정본 | 같은 JSON 을 최소 2회 읽고 두 로더의 NaN 정화 수준이 다르다 | 3-1 | `loadAllData:548` 은 파일을 그대로 파싱하고 `loadModelInfoFromFolder:683` 만 `NaN`·`Infinity` 를 `null` 로 치환한다(`:728-731`) → **Python 이 NaN 을 쓴 model\_info.json 은 전자에서만 조용히 빈 문서로 떨어진다.** 진입·폴더 전환마다 반복되고 후자는 설정 JSON 까지 다시 읽어 덮어쓴다(`:749-763`) |
| **D2** | 진입·수명 | Set 삭제 후에도 위젯이 이전 Set 의 표를 유지한다 | 3-1 · 3-9 | `DashMainWindow.cpp:805` 가 `setModel(nullptr)` 을 걸지만 `setEnabled(true)` 와 표 내용은 그대로고, `:807` 의 `disconnect` 로 갱신 경로만 끊긴다 → 삭제된 Set 의 값이 화면에 남고 그 상태의 [Run Optimizer] 는 모델 없이 즉시 반환된다(`:492`) |
| **D3** | 데이터 정본 | 폴더를 바꿔도 목적함수·구속·방법 입력칸이 갱신되지 않는다 | 3-2 | `onModelBuilderFolderChanged:723` 이 두 표만 재구성하고 `populateOptimizationSettings` 를 부르지 않는다 → 응답 심볼이 바뀌어도 수식 문자열은 직전 폴더의 것이 남고, 수식이 가리키는 응답이 새 폴더에 없어도 화면에서 드러나지 않는다 |
| **D4** | 구조·결합 | 1D/ND 열 가시성이 첫 행 응답 이름의 부분문자열로 정해진다 | 3-2 | `contains("(Field)")`(`:755`) 판정이 첫 행에서만 이뤄져(`:756-758` → `updateTableHeadersForModelType:469`) 표 전체의 열 4개를 여닫는다 → 행마다 차원이 섞이면 나머지 행의 지표가 보이지 않는다 |
| **D5** | 데이터 정본 | 최적화 모드 2차 판정이 단방향 승격이다 | 3-2 · 3-9 | `loadDesignVariables:917-926` 이 색인을 1 로 올리기만 하고 0 으로 내리지 않는다 → 설정 JSON 에 한 번 mean/std 가 기록되면 model\_info.json 이 결정론으로 바뀌어도 신뢰도기반으로 남고, UI 에 모드를 내릴 수단이 없다(U1 과 연쇄) |
| **D6** | 데이터 정본 | Fixed 체크와 Init. Value 편집이 Run 전까지 모델에 도달하지 않는다 | 3-3 · 3-9 · 5절 | `onFixedCheckBoxChanged:1822` 는 아이템 4개의 `ItemIsEnabled` 만 끄고 flag 갱신을 부르지 않는다. Init. Value 위젯에는 시그널 연결 자체가 없다(`:894-918`) → **두 값을 고치고 Run 없이 Set 을 전환하면 변경이 파일에도 모델에도 남지 않는다** |
| **D7** | 데이터 정본 | Minimize/Maximize 콤보에 시그널 연결이 없다 | 3-4 · 5절 | `objectiveCombo` 는 `:185` 에서 별칭만 잡히고 수신 슬롯이 없다 → 방향만 바꾸고 수식을 건드리지 않으면 모델의 `direction` 이 낡은 값으로 남고, Run 시점의 강제 동기화(`:498-501`)로만 메워진다 |
| **D8** | 데이터 정본 | [+] 로 만든 행이 편집 없이 그대로 구속이 된다 | 3-4 | `onAddConstraintClicked:557` 이 심는 `"r9 <= 153755.61"` 은 `:390-393` 의 회색 예시와 달리 보통 아이템이고 같은 함수 끝(`:589-590`)에서 곧바로 모델에 들어간다 → [+] 를 누르고 편집하지 않으면 의도하지 않은 구속이 실행에 실린다 |
| **D9** | 구조·결합 | 크래시 추적용 디버그 로그가 배포 경로에 남아 있다 | 3-4 · 3-10 | `populateOptimizationSettings` 의 `[popOS]` `qDebug` 27줄(`:953`\~`:1096`, `probSpin` 생성 구간 `:1019-1044` 는 호출 한 줄마다) · `showEvent:159-169` 의 7줄. 둘 다 빌드 가드 없이 릴리스에 들어간다 |
| **D10** | 데이터 정본 | 방법을 바꿀 때마다 옵션 칸이 기본값으로 초기화된다 | 3-5 · 3-9 | `onMethodSelectionChanged:1120-1132` 가 선택 시마다 기본값을 주입한다 → iteration 을 500 으로 고쳐 둔 뒤 방법을 바꿨다 되돌리면 10 으로 돌아간다. 저장값 복원은 `populateOptimizationSettings:1078-1093` 이 이 슬롯을 부른 **직후 덮어쓰는 순서**로만 성립하므로 호출 순서가 바뀌면 복원이 깨진다 |
| **D11** | 구조·결합 | 실패가 화면에 도달하지 않는다 | 3-6 | `optimizationFailed` 는 선언(`DashOptimizer.h:95`)과 emit 4곳(`:188`·`:207`·`:214`·`:978`) 외에 `connect` 가 레포 전체에 없다 → exe 가 죽어도 위젯은 반응하지 않고, 성공 시에만 모달이 뜨므로 **사용자 입장의 실패 신호는 "아무 일도 안 일어남"뿐**이다. `:207`·`:214` 경로는 `logMessage` 조차 없다 |
| **D12** | 진입·수명 | Run 이 유일한 영속화 지점이다 | 3-6 · 3-9 | `saveSettings()` 호출처는 `runOptimization:199` 하나다 → 설정을 다듬고 Run 없이 나가면 전부 소멸한다. DV Fixed·Init. Value·방법·옵션 4종은 모델에조차 도달하지 않는다(D6 과 연쇄) |
| **D13** | 실행 모델 | 중복 실행 방지가 모델에만 있고 버튼은 열려 있다 | 3-6 | `:160` 주석이 "위젯에 버튼 잠금이 없어 Run 연타가 그대로 들어온다"고 명시한다. `m_currentJob` 가드가 튕겨낸 사실은 `logMessage` 로만 알려진다 → 로그 dock 이 닫혀 있으면 무시된 것인지 진행 중인지 화면으로 구분할 수 없다 |
| **D14** | 구조·결합 | 검증 표 헤더 분류가 문자열 규칙이다 | 3-7 | `PM:130-144` 의 3단 규칙이 `startsWith("r")` + 두 번째 글자 숫자를 응답으로 본다 → `r2_thickness` 같은 설계변수 이름이 **응답으로 잘못 분류된다.** 분류를 유지하는 유일한 상태가 인덱스 리스트 3벌이라 오분류가 프리뷰의 DV 열 선택까지 간다 |
| **D15** | 실행 모델 | 프리뷰가 템플릿 필터를 무시하고 configs 의 모든 deck 을 모핑한다 | 3-7 | `resolveGeometrySource` 가 뽑은 `templateFileName` 은 비어 있는지만 검사되고(`:1461`) 루프(`:1480`)는 `entryList({"*.dat","*.inp"})`(`:1467-1470`) 전량을 돈다 → 템플릿이 N 개면 모핑이 N 회 돌고 **마지막 하나만 화면에 뜬다** |
| **D16** | 실행 모델 | 프리뷰 모핑이 GUI 스레드 동기 실행이고 루프 안에 `processEvents` 가 있다 | 3-7 | 모듈 `processEvents` 2곳이 모두 이 루프 안이다(`:1489`·`:1514`). 실행 모델은 `DashMorphingDoeExecutor.cpp:890-899` 주석이 명시한다 — "…지금 레이스가 아닌 이유는 이 경로가 GUI 스레드에서 돌기 때문일 뿐이다." 정합성은 `:927-930` 의 원복 두 줄에만 기대고, export 나 원복이 실패하면 공유 세션이 오염된 채 남는다 |
| **D17** | 구조·결합 | 만든 `.vtu` 2종을 만들자마자 지운다 | 3-7 | `performMorphing` 이 deck 생성 후 `_input_geometry.vtu` 를 추가로 뽑는데(`Optimizer:1516-1528`) 호출부가 그 파일과 `.vtu` 를 곧바로 제거한다(`:1503-1510`) → 두 번의 디스크 왕복이 산출물 없이 끝난다 |
| **D18** | 진입·수명 | 프리뷰가 전역 상태 3개를 갈아끼우고 되돌리지 않는다 | 3-7 | 한 번의 [Render Preview] 가 ① `DashHandlePickingInteraction` 핸들 배열 교체(`MorphingUtils:91`·`:96-150`) ② 렌더러 액터 전량 제거 + 레이어 3종 clear(`:1539-1554`) ③ `setActiveContext(프리뷰 deck)`(`:1556`) 를 남긴다. 셋 다 복구 코드가 없다 → **프리뷰 1회 후의 전역 활성 해석 모델은 원본이 아니라 `Preview_*.dat`** 이고 모핑 모듈의 핸들 상태도 프리뷰 것으로 바뀌어 있다 |
| **D19** | 구조·결합 | NX CAD 완료 통지가 요청과 짝지어지지 않는다 | 3-7 | `enqueueUpdatePrtGeometry`(`:1624`)에 요청 태그가 없고 완료는 `m_batchMode` 전역 플래그로 갈린다(`DashSolverNxCad.cpp:200-206`). 수신은 `DashMainWindow.cpp:281` 이고 **Optimizer 위젯은 자기 요청의 완료를 알지 못한다** → 프리뷰 중 다른 CAD 요청이 끼면 구분 근거가 없다. 부모 탐색(`:1618-1620`)도 위젯 계층에 의존해 조용히 실패한다 |
| **D20** | 데이터 정본 | 설정 JSON 이 플롯의 게이트로만 쓰인다 | 3-8 | `requestPlot:1117` 이 넘기는 `configFilePath` 가 `SpecBuilder:18-23` 의 실재 검사에 걸리면 빈 객체를 돌려준다. 실제 데이터는 `settings["target_optimum_path"]` 의 `optimum.json` 이다(`SpecBuilder:107-120`) → **optimum.json 이 멀쩡해도 설정 JSON 이 없으면 플롯이 거부된다** |
| **D21** | 진입·수명 | ModelBuilder 폴더 선택이 세션을 넘기지 못한다 | 3-9 | `m_activeModelBuilderFolder` 는 `loadModelInfoFromFolder:704` 에서만 세팅되고 JSON 왕복이 없다. `PM::selectModelBuilderFolder:148` 의 1순위 "직전 선택"이 세션 한정 값이다 → 앱을 다시 띄우면 2순위(setName 파생)나 3순위(첫 항목)로 떨어져 **사용자가 고른 학습 결과가 아닌 폴더로 되돌아갈 수 있다** |
| **D22** | 데이터 정본 | 피팅 결과가 DV 표 위젯에만 쓰이고 모델에 도달하지 않는다 | 3-10 · 5절 | `onFitFinished:2116-2142` 가 심볼로 행을 찾아 위젯에 직접 쓰고 `m_designVariables` 는 건드리지 않는다 → 저장에 반영되려면 Run 의 강제 동기화를 거쳐야 하고, Run 없이 Set 을 전환하면 소멸한다(D6·D12 와 같은 경로) |
| **D23** | 구조·결합 | 피팅의 학습 모델 경로가 하드코딩이다 | 3-10 | `runFitVariables:295` 가 `{projectPath}/ModelBuilder_LGE_Spring_Fitting` 을 문자열로 조립한다. 최적화가 쓰는 `getModuleDir(ModelBuilder, mbSetName)`(`:228`)를 거치지 않아 폴더 이름이 다르면 도달할 방법이 없다 |
| **D24** | 데이터 정본 | 심볼의 저장분과 표시분이 어긋난다 | 3-2 · 3-4 · 5절 | 표시 심볼은 행 인덱스에서 매번 재생성되고(`Widget:753` `r{i+1}` · `:874` `v{i+1}`) 모델 심볼은 JSON `symbol` 을 읽어 쓴다(`DashOptimizer.cpp:414`·`:431` 쓰기 / `:840`·`:898` 읽기, 비었을 때만 인덱스로 생성 `:844`·`:902`). 복원 매칭은 응답 **이름**이다(`loadSurrogateModels:837-866`) → **응답이 하나 추가·삭제되면 저장된 심볼이 중복되거나 표시분과 어긋나고, 목적·구속 수식의 토큰이 그 심볼이라 도구가 최적화하는 응답과 사용자가 지목한 응답이 달라진다.** 화면에는 어떤 표시도 없다. Analysis Launcher 의 D26(제약식 `v{n}`)과 같은 기제다 |
| **U1** | 미구현 | ~~최적화 모드 사용자 선택 경로가 없다~~ | 3-2 · 5절 | **제외** — 착수 대기 기능 갈래다. `configureDesignVariableTable:300-305` 가 콤보를 만들고 `hide()` 한 뒤 레이아웃에 넣지 않아 모드는 데이터가 정한다. 사용자가 모드를 되돌릴 수 없다는 귀결은 D5 가 보유한다 |
| **U2** | 미구현 | 도달하지 않는 선언 4종 | 5절 · 3-6 | `m_resultCsvPath`(`DashOptimizer.h:127`) 참조 0. `predictBtn`(`DashOptimizerWidget.h:174`) `.ui` 에도 코드에도 없다 — **초기화되지 않은 포인터 멤버**. `m_soraLabel`(`:401-403`) 은 `setVisible(false)` 고정(`:1775` 주석 `"always hidden - SORA is implied"`). `settingsSaved` emit 1곳(`:392`), connect 0 |
| **U3** | 미구현 | 자동 회귀 보호가 없다 | 4절 | `tests/` 전체에 Optimizer 참조 0건. 존재하는 것은 async 트랜스포트 계층 테스트 3종뿐이다 → 설정 JSON 왕복, 헤더 분류(D14), 프리뷰 분기(D15\~D19) 전부 자동 검증 밖이다 |

---
