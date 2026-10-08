# Analysis Launcher — 사용자 플로우 ↔ 코드 대응

> 관련 Issue: #269
> 후속 문서: [[Project-Store-Survey-Reference-Entry-Upstream-Flows]] — 진입 파일 5종이 **AL 에 닿기 전** 밟는 상류 모듈 동선(3-6 절 분기의 전사) · 짝 지정 기제 3종
> **성격**: 독립 참조 문서. 사용자 행위가 밟는 함수 체인의 대응표 — 수정 계획·우선순위는 담지 않는다.
> **좌표 기준**: `dev` @ `4c7608e` 실측 (유효기간 있음). 정적 코드 근거만 — 빌드·실행 검증 없음. 외부 데몬(NX CAD · Ansys Journal · DashOptiMBD)과 cae-launcher 내부는 GUI 호출측 코드로만 확인했다.

## 개요

위젯 3 variant 와 로직 클래스 6종이 설정 JSON 한 개(`configs/AnalysisLauncher_{Set}.json`)를 공동 편집·판독한다. 사용자 행위는 위젯 → `DashAnalysisLauncher` → `DashJobRunner` 3단을 지나 cae-launcher 또는 외부 프로세스에 닿고, 진행 상태는 그 JSON 에 되쓰인 뒤 표로 되읽힌다. **이 JSON 이 실질 도메인 모델**이며 `types::Set` 같은 도메인 타입은 이 경로에 없다 — 왕복이 전부 read-modify-write 로 나타나고, 실행 말단 6경로가 같은 파일을 각자 다른 규칙으로 쓴다. 3\~6절은 코드가 하는 일만, 판정은 7절 — 본문 `→ D{n}`·`→ U{n}` 이 링크다.

---

## 1. 3 variant 와 소유 클래스

Set 생성 시 고른 variant 가 이름과 JSON 을 함께 가른다 — `Set1`/`Set1-Resample`/`Set1-Direct`, JSON 최상위 `variant` 키(`model/DashProject.cpp:592-616`). 트리 행이 그 문자열을 `Qt::UserRole+2` 로 들고 `…ForVariant`(`view/DashMainWindow.cpp:1236`)가 라우팅하며, 파일명 접미 폴백도 있다(`detectLauncherVariant:690`).

| variant | 위젯 (줄) | 탭 | 고유 기능 |
|---|---|---|---|
| Init | `DashAnalysisLauncherWidget` (1,419) | DOE configuration · DOE Analysis · DOE Launcher | DV 표 · 샘플링 설정 · [Run] · DV CSV 입출력 |
| Resample | `DashAnalysisLauncherResampleWidget` (63) | Resample DOE · DOE Analysis · DOE Launcher | **Resample 탭은 위젯 별칭만 — 로직 0줄** → U1 |
| Direct | `DashAnalysisLauncherDirectWidget` (318) | 없음 (단일 스플리터) | Input Cases 표 · Output Cases 표 · [Start]/[Stop] |

Init·Resample 은 `DashAnalysisLauncherWidgetBase`(288)를 상속한다. 베이스가 DOE Analysis·DOE Launcher 탭 전체(레퍼런스 파일 표 · 케이스 표 · CPU · [Start]/[Stop])를 소유하고, 파생은 자기 `.ui` 를 로드해 베이스 보호 멤버로 **별칭만 잇는다**(zero-churn aliasing). Direct 는 베이스를 상속하지 않는 독립 `QWidget` 이다.

| 로직 클래스 (줄) | 담당 |
|---|---|
| `DashReferenceFileWidget` (1,192) | 레퍼런스 파일 행 · 라디오 단일 선택 · target part 매칭 |
| `DashDoeCasesWidget` (664) | 케이스 표 4열(체크 · Case Name · Status · Log) |
| `DashAnalysisLauncher` (1,627) | 모듈 모델 · DOE 샘플링 워커 · 완료 집계 |
| `DashDoeConfigManager` (660) | 설정 JSON read-modify-write 전담 |
| `DashJobRunner` (2,694) | 워크플로 분기 · cae-launcher · 외부 프로세스 |
| `DashMorphingDoeExecutor` (1,129) | 샘플별 모핑 + deck export (Job 1회 소유) |
| `DashDesignVariableModel` (486) | DV 표 정본 모델 (8열) |

계층 배치의 특징 셋이 이후 절에서 반복된다 — 실행 분기 전체가 `generateInputCases` 738줄 한 함수에 있고(4절), 동기 대기가 `processEvents` 로 대체돼 있으며(**전량 `DashJobRunner.cpp` 16곳**, 다른 파일 0곳), 워커·배치가 GUI 상태를 값으로 뜨지 않고 공유한 채 읽고 쓴다(3-4 · 3-6-4). `DASH_BUILD_*` 조건부 컴파일은 0곳이다.

---

## 2. 전체 동선

Init 기준. Resample 은 2\~4단계가 Resample 탭(미구현)으로 대체되고, Direct 는 1·6·7만 밟는다.

```
1. 진입       트리 Set 클릭 → variant 판별 → 위젯 라우팅 → JSON 경로 확정 → 캐시 샘플·설정 로드
              ※ setProjectDirectory / setSetName / 위젯 setModel 이 각자 loadSettings 를 부른다
2. DV 확정    Geometry·Condition JSON 콤보 → [Set] → DV 표 적재 → Type/Min/Max/Cases/Mean/Std 편집
              → [Download]/[Upload] 로 표 전체를 CSV 왕복
              ※ Sampling Mode 를 Probabilistic 로 바꾸면 표가 7열 → 8열로 통째로 재구축
3. 샘플링 설정 Auto(Purpose + scale → method·샘플수 역산 후 UI 로 되쏨) 또는 Manual(Method 5종 + 옵션)
4. 샘플 생성   [Run] → 케이스 체크 저장 → (Probabilistic 이면 Min/Max 를 Mean±kσ 로 환산)
              → QtConcurrent 워커 → DashOptiDOE 샘플러 → DOE Table 기록 + CSV
              ※ 이 모듈에서 워커 스레드로 나가는 유일한 경로
5. 입력 확정   레퍼런스 파일 표 등록(DV source 자동 + 수동) → 라디오 1개 = 실행 템플릿 확정
              ※ 확장자가 곧 워크플로. .wbpj 이면 target part(.prt) 지정, CPU 스핀박스 비활성
6. 실행       [Start] → 등록 파일 전량 configs 복사 → active 키를 완료 대기 집합에
              → generateInputCases 738줄 (확장자로 4분기 · 말단 6경로)
              ※ 이름과 달리 GUI 스레드 동기 실행
7. 상태·종결   status_{analysisType} 키 되쓰기 → 같은 시그널이 케이스 표 Status 열 갱신
              ※ 종결 신호 두 갈래 — 키 집합 소진 집계 / jobFinished 직접 방출
8. 결과 열람   DOE Analysis 탭 — 탭 전환 시 Results Analyzer 재적재, 플롯 요청도 설정 JSON 경유

[산출] configs/AnalysisLauncher_{Set}.json — variant · DOE configuration · DOE Table · input_files · status
       {moduleDir}/{analysisType}/{runKey}/ — 입력 덱과 솔버 산출물(.odb .rst .dat .dfr .vtu)
       DOE 성공 시 CSV 1개 — csvFileGenerated 로 메인윈도우가 뷰어를 연다
[밖]   Direct Launcher · [Stop] 취소 · Resample 탭 → 3-9
```

---

## 3. 단계별 대응

### 3-1. 모듈 진입

카테고리 문자열 `"Analysis Launcher"` 로 분기하고(`DashMainWindow.cpp:1077`), 트리 행 표시 텍스트가 Set 이름 · `UserRole+2` 가 variant 다. Set 클릭 → `handleAnalysisLauncherSelection:1214` → `launcher->setSetName(표시명):1228` → `…ForVariant:1236` → `setProjectDirectory:1244` → variant 위젯 `setModel` 이고, 남는 상태는 `m_setName`·`m_variant`·`m_doeJsonPath`·`m_cachedSamples` 다. `setSetName`(`model/DashAnalysisLauncher.cpp:164`)과 `setProjectDirectory`(`:126`)는 **둘 다** `m_doeJsonPath` 를 재계산하고 `loadCachedSamplesFromFile()` + `loadSettings()` 를 부른다(이름이 같으면 즉시 반환 `:166`).

```
variant 위젯 setModel
  ├─ Init: 버튼 람다 8종 disconnect + 모델 연결 해제        Widget.cpp:49-69
  ├─ Base::setModel(model, path)                            Base.cpp:28
  │     ├─ 이전 모델 연결 전량 해제                          :33-48
  │     ├─ setProjectDirectory(prjMgr 경로):62 · 이름 변경 시 setSetName:70  ← loadSettings
  │     ├─ ReferenceFile·DoeCases 결선:75-93 · analysisFinished/csvFileGenerated/버튼:98-132
  │     └─ Analyzer 결선 + setSetName + initializeTargetData :135-148
  └─ Init: populateJsonFiles → 콤보 재적재 → 버튼 재connect  :73-300
        · loadSettings(false):307 ← loadSettings · findAndEmitSourceFiles:311
        · referenceFileWidget->initializeFromJson(dvPath):316
```

마지막 `loadSettings(false)` 의 이유는 주석이 밝힌다(`Widget.cpp:303-306`) — 앞선 호출들은 시그널 연결 전이라 `settingsLoaded` 를 받는 쪽이 없다. 초기화 순서를 코드가 아니라 재호출로 맞추는 구조다. → D1
`.ui` 의 `purposeCombo` 2항목(`ui/DashAnalysisLauncherWidget.ui:211-212`)은 `setModel` 의 `clear()` 뒤 모델의 5개(`DashAnalysisLauncher.cpp:878-885`)로 덮여 표시되지 않는다. → U5

### 3-2. 설계변수 확정

DV 표는 `QTableWidget` 이고 뒤에 `DashDesignVariableModel`(8열)이 정본으로 있다. 표는 모델을 뷰로 물지 않고 셀 위젯으로 재조립한다.

| 사용자 행위 | 함수 체인 | 결과 |
|---|---|---|
| Geometry/Condition 콤보 변경 | `Widget.cpp:123`/`:139` 람다 → `updateSelectedDvGeometry/Condition` | 문자열 멤버만 갱신 (파일 미접근) |
| **[Set]** | `onSetDesignVariables:525` → `updateDesignVariables:703` → `DashDesignVariableModel::loadFromJsons` → `findAndEmitSourceFiles:1214` | DV 모델 적재 + 레퍼런스 후보 emit |
| 모델 적재 완료 | `modelLoaded` → `openPersistentEditors:462` → `updateTableForSamplingMode` | 표 전면 재구축 |
| Sampling Mode 콤보 | sigma 컨트롤 토글 + `updateTableForSamplingMode:754` | 7열 ↔ 8열 재구축 |
| **[Download]/[Upload]** | `buildDvTableCsv:1077` / `applyDvTableCsv:1193` | 표 ↔ CSV 왕복 |

`updateTableForSamplingMode:754` 가 표의 유일한 조립 지점이다 — General 7열(Symbol·Name·Source·Type·Min·Max·Cases, Type=`QComboBox` 3종 · Min/Max=`QDoubleSpinBox`) / Probabilistic 8열(…·Mean·Std, Type continuous 고정·비활성 · 값 4종 = `QCheckBox`+`QDoubleSpinBox`). Symbol 열(`v1`, `v2`, …)은 행 번호에서 즉석 생성되는 제약식용 이름이고 저장되지 않는다. **모델 되쓰기 경로는 모드마다 다르다.**

| 편집 | General | Probabilistic |
|---|---|---|
| Type | `setData(row,2)` + 저장 (`:997-1010`) | 편집 불가 |
| Min / Max | `setData(row,3/4)` + 저장 (`:1014-1020`) | **되쓰기 없음** — UI 에만 남는다 → D2 |
| Mean / Std | 열 없음 | `setData(row,6/7)` + 저장 (`:965-970`) |
| Cases | `itemChanged` 람다(`:606`) — discrete/categorical 만 `setData(row,5)` | 열 없음 |

Probabilistic Min/Max 가 모델에 안 들어가는 것은 설계 의도와 맞물린다 — [Run] 시점에 `updateMinMaxFromMeanStd:1026` 이 셀 위젯에서 직접 읽어 **샘플링 전용 override** 로만 넘기고(`setProbabilisticMinMaxOverrides`, `model/DashAnalysisLauncher.cpp:69`), 헤더 주석이 정본이다(`.h:78-79`): "UI/table and JSON/model Min/Max must remain unchanged."

```
updatedMin = baseMin + mean - (sigmaLevel * std)      :1059-1060
updatedMax = baseMax + mean + (sigmaLevel * std)
```

`baseMin`/`baseMax` 는 표 스핀박스 현재값, `sigmaLevel` 은 1\~3(기본 1). **기존 Min/Max 에 더해지므로** 0 이 아니면 구간이 그만큼 평행이동한다. 체크박스 4종은 Min↔Max · Mean↔Std 두 쌍으로 묶이고 넷이 모두 해제되면 경고 후 되돌린다.

CSV 헤더는 General `Name,Min,Max,Case1…` / Probabilistic `Name,Min,Max,Mean,Std` 로 다르다. Import 는 헤더·`Name`·필수 열 검사 뒤 **셀 위젯에 써 넣고** `saveDesignVariablesToJson()` 을 호출하는데(`:1416`), General 은 `setValue` 가 되쓰기 람다를 타지만 Probabilistic Min/Max 는 타지 않는다 — D2 와 같은 구멍이다.

### 3-3. 샘플링 설정

Auto 와 Manual 은 같은 두 멤버(`m_selectedMethod`·`m_methodOptions`)를 쓰고, Auto 는 그 값을 계산해 **UI 로 되쏜다**.

```
[Set] → Widget.cpp:86 람다 → onSetButtonClicked()      DashAnalysisLauncher.cpp:608
   ├─ nruns = dimension * {Low:10, Mid:25, High:40}     :617-627
   ├─ purpose 문자열 5종 → method 역산                   :631-655
   └─ emit settingsReconfigured(method, options)         :660
         → onModelReconfigured:684 — methodCombo 를 blockSignals 로 세팅 후
           updateSelectedMethod 를 명시 호출해 모델을 다시 맞춘다
```

| Purpose | 역산되는 Method | 추가 옵션 |
|---|---|---|
| Training with progressive updating | Optimal Latin Hyper Cube | — |
| Linear sensitivity analysis | Orthogonal Array | Level = 2 |
| Surrogate Reliability analysis or validation | Monte Carlo | — |
| Training with constrained design variables, robust regardless of dimensionality | Optimal Latin Hyper Cube | — |
| Training with constrained design variables, high quality sampling in low-dimensional problems (\~5) | Translational Propagation Latin Hyper Cube | — |

Purpose 판정은 문자열 완전일치다 — 다섯 문자열이 `getPurposeOptions():878` 과 `onSetButtonClicked:631-655` 양쪽에 리터럴로 박혀 상수를 공유하지 않고, 어긋나면 `else { return; }` 로 조용히 끝난다. → D3

Manual 5종은 `setupMethodData:722` 의 `m_methodData` 가 정본이고 옵션 개수로 UI 가 갈린다(`onMethodSelectionChanged:617`).

| Method | 옵션 | option2 위젯 | Greedy |
|---|---|---|:---:|
| Optimal Latin Hyper Cube | Number of samples · Constrained function | `constrainedFuncEdit` | 노출 |
| Optimal Latin Hyper Volume | Number of samples · Constrained function | `constrainedFuncEdit` (**항상 체크·비활성**) | 노출 |
| Monte Carlo | Number of samples | 숨김 | 숨김 |
| Orthogonal Array | Number of samples · Level | `levelSpinBox` (기본 2) | 숨김 |
| Translational Propagation LHC | Number of samples | 숨김 | 숨김 |

option2 위젯 교체는 `QStackedWidget` 이지만 분기 조건이 옵션 이름 문자열이다(`"Level"` / `"Constrained function"`).

### 3-4. 샘플 생성 — [Run]

이 모듈에서 워커 스레드로 나가는 유일한 경로다.

```
[Run] → Widget.cpp:103 람다
   ├─ m_doeCasesWidget->saveAllActiveStates()    DoeCasesWidget:334  (표 체크 → JSON active)
   ├─ (Probabilistic) updateMinMaxFromMeanStd:1026 → setProbabilisticMinMaxOverrides
   │  (General)       clearProbabilisticMinMaxOverrides()
   └─ onRunButtonClicked()                       DashAnalysisLauncher.cpp:217
         ├─ 워커 실행 중 / method 미선택이면 경고 후 중단      :219-227
         ├─ checkVariableTypesForMethod:239 — LHV·TPLHS 는 전 행 continuous 강제
         ├─ saveSettings():780 · emit analysisStarted()
         └─ QtConcurrent::run(this, &runAnalysisInThread)      :235-236
```

**워커/GUI 값 경계가 없다.** `runAnalysisInThread:286` 이 워커 스레드에서 `m_designVariableModel` 을 직접 읽고(행 수 `:310`, 이름·타입 `:326-327`, min/max `:336-337`, cases `:341`·`:348`), 결과 기록도 모델 포인터를 그대로 넘기며(`:266` → `saveResultsAsDvTable:180`), `DashJobRunner` 도 같은 포인터를 보유한다(`setDesignVariableModel:423`). → D4
Probabilistic override 는 같은 루프에서 **위치 인덱스로** 소비된다(`:331-332`) — 크기 가드가 없고 대응은 [Run] 직전 위젯이 맞춰 준 순서에만 기댄다. → D2

DV 를 `ProcessedParameter` 로 환산한 뒤 method 문자열로 샘플러를 고른다(`:369-582`) — 5개 method 가 **8개 샘플러 클래스**로 갈린다.

| Method | 추가 조건 | 샘플러 | 파라미터 |
|---|---|---|---|
| Monte Carlo | — | `MonteCarlo` | — |
| Optimal Latin Hyper Cube | Constrained + Greedy | `ConstrainedLH_Greedy` | `SetStrategyParameters(5,3,2,10)` |
| Optimal Latin Hyper Cube | Constrained | `ConstrainedLH` | `SetStrategyParameters(20,5,10,1,1,1.2,2,0)` |
| Optimal Latin Hyper Cube | discrete/categorical 존재 | `ProgressiveLH` | `SetPLHSParameters(1,1)` |
| Optimal Latin Hyper Cube | 전 continuous | `OptimizedLH` | `SetOptimizationParameters(100,50)` |
| Orthogonal Array | — | `OrthogonalArray` | `SetLevel(level)` — 실패 시 false |
| Optimal Latin Hyper Volume | Greedy | `ConstrainedLHV_Greedy` | `SetAlgorithmParameters(50.0,20,5,3)` |
| Optimal Latin Hyper Volume | — | `ConstrainedLHV` | `SetAlgorithmParameters(200,20,15,5,10,3,0)` |
| Translational Propagation LHC | — | `TranslationalPropagationLH` | — |

`OptimizedLH` 분기만 **continuous 파라미터만 등록한다**(`:474-476`). 나머지는 세 타입을 모두 등록하고 미지원 method 는 `std::runtime_error`(`:580`). 제약식 치환은 UI 심볼 `v{n}` → 실제 변수명이며 `v1` 이 `v10` 의 접두를 먼저 먹지 않도록 **역순으로** 돈다 — 같은 블록이 OLHC·OLHV 두 분기에 복제돼 있다(`:401-410`·`:514-523`).

```
saveResultsAsDvTable(samples, categoricalMappings, dvModel, refFileName, &cachedSamples)
                                                       DashDoeConfigManager.cpp:180
  ├─ JsonWrapper → stringstream → QJsonDocument                   :188-191
  ├─ 모델 행 순회 → headers + source/min/max/mean/std 병렬 맵      :214-255
  │     refFileName 은 첫 source 에서 유도 — "Morphing|{dat}|{part}" 면 2번째 토막
  ├─ 샘플 i 마다 discrete/categorical 인덱스를 실제 값으로 역치환   :282-302
  │     key = "runs{i+1}" · slice = (i/5)+1 · active = true        :308-313
  │     cachedSamples 에는 원본(파라미터명 키) 객체                 :349
  └─ 기존 JSON read → root["source"] 제거 → root["DOE Table"] 교체 → write :352-413
```

**같은 샘플이 두 형태로 저장된다** — `samples[]` 는 헤더 순서 위치 기반 `values` 배열, `rawSamples[]`(= `cachedSamples`, `:394`)는 파라미터명 키 객체이고 하류가 둘 중 무엇을 읽느냐가 경로마다 다르다. → D5
성공 시 `saveDoeToCsv()` 가 CSV 를 쓰고 `csvFileGenerated` 로 메인윈도우가 뷰어를 연다(`Base.cpp:111-119`). 워커 종료는 `QFutureWatcher::finished` → `onAnalysisCompleted:590`.

### 3-5. 실행 입력 확정 — DOE Launcher 탭

레퍼런스 파일 표는 세 경로로 채워진다 — DV source 자동 수집(`findAndEmitSourceFiles:1214` → `sourceFilesFound` → `Base::onSourceFilesFound:251` → `addReferenceFileRow`, `hasFile()` 로 중복 차단) · 설정 JSON 복원(`initializeFromJson:934` — `DOE Table.source[]` + `input_files[]`, **행 전량 제거 후 재구축**) · 수동 추가(`onAddReferenceFileClicked:205` → `addReferenceFileRow:288`).

`findAndEmitSourceFiles` 의 파일 판별은 **파일명 부분일치**다 — `contains("Condition")||contains("cond")`(`:1242`) · `contains("Geometry")||contains("geom")`(`:1290`). 거기서 각 DV 의 `source` 를 꺼내 확장자 `dat|inp|bdf|dfsxml|stli` 만 후보로 삼고, Geometry 쪽은 `"Morphing|{dat}|{part}"` 의 2번째 토막만 쓴다. 같은 판별을 세 곳이 각자 구현한다 — `DashAnalysisLauncher.cpp:1242`/`:1290` **대소문자 구분** `contains`, `DashMorphingDoeExecutor.cpp:130`/`:134` `Qt::CaseInsensitive`, `DashJobRunner.cpp:2229` `QRegularExpression("^GeometryParameter_.*\\.json$")`. → D6

라디오 선택이 곧 실행 템플릿이다. `getSelectedReferenceFiles:101` 이 라디오 행 경로를 **1개짜리 리스트**로, `getAllReferenceFiles:153` 이 전 행을 중복제거해 돌려주며 둘의 용도가 [Start] 에서 갈린다(3-6). `.wbpj` 를 고르면 CPU 라벨·스핀박스가 비활성된다(`Base.cpp:275-277`). 선택이 바뀌면 `updateFromDvTable`(`DashDoeCasesWidget.cpp:108`)이 케이스 표를 다시 그린다 — 표의 유일한 조립 지점이다.

```
updateFromDvTable(selectedFileName)
  ├─ QFileSystemWatcher 감시 경로를 현재 DOE JSON 으로 교체         :119-129
  ├─ DOE JSON 읽기 → headers · samples · source                    :131-150
  ├─ 선택 파일과 source[i] 파일명이 같은 파라미터 인덱스만 수집      :157-182
  │     (하나도 안 맞으면 전 인덱스를 다시 넣는다)                   → U3
  ├─ 기존 Log 열 텍스트를 key 별로 백업                             :184-196
  ├─ 표 전면 재구축 — 4열 고정 (" " · Case Name · Status · Log)      :198-259
  │     analysisType = 선택 파일 basename
  │     statusKey    = "status_{analysisType}"  (선택 없으면 "status")
  │     fileExtension = "." + 선택 파일 suffix   (.wbpj → .rst 로 치환)
  │     Case Name = "{key}{fileExtension}" · Status 없으면 "Enqueued"
  └─ 헤더 일괄 체크박스 위치 재계산 (QTimer::singleShot(0))         :264-273
```

파일 감시는 DOE JSON 이 바뀔 때마다 이 함수 전체를 다시 돌린다(`:102-105`). `setSampleStatus` 가 케이스 1건마다 JSON 을 통째로 다시 쓰므로 실행 중에는 케이스 수만큼 표 재구축이 유발된다. → D7
행 ↔ 케이스 결합은 Case Name 열 텍스트의 `completeBaseName()` 으로만 유지된다(`:290`·`:322`). → D8
체크박스 되쓰기는 개별(`onItemChanged:388` → `persistActiveFlag:397`)과 일괄(`saveAllActiveStates:334`) 둘이고, 둘 다 JSON read-modify-write 다.

### 3-6. 실행 — [Start]

```
[Start] → Base.cpp:177 람다
   ├─ DashManager::setCPUCoreCount + applyLauncherCPUCoreCount:83  :180-184
   ├─ DOE JSON 부재면 경고 후 중단                                  :187-191
   ├─ templateFiles = getSelectedReferenceFiles() (라디오 1개):196
   │  allReferenceFiles = getAllReferenceFiles()  (전 행):197
   │  templateFiles 비면 경고 후 중단                               :200-203
   ├─ allReferenceFiles 전량을 configs 로 복사                      :207-210
   ├─ setInputReferenceFileName / setReferenceTemplates             :212-214
   └─ runDoeAsync()                            DashAnalysisLauncher.cpp:1038
         ├─ DOE JSON 재파싱 → active 키를 m_expectedRunKeys 로 적재  :1042-1058
         ├─ emit analysisStarted()
         └─ generateInputCases(m_referenceTemplates):894 → JobRunner :1063
```

`runDoeAsync` 는 이름과 달리 `generateInputCases` 를 GUI 스레드에서 직접 호출한다. 비동기인 부분은 cae-launcher 완료 콜백과 NX/Journal 데몬 시그널이며, 그 앞의 모핑·파일 생성·프로세스 대기는 전부 동기다. → D9

#### 3-6-0. 솔버 실행 계층 — cae-launcher

Ansys·Abaqus·FE-safe 실행은 **cae-launcher C++ API**(`dash::cl::`)를 쓰고, 세 런처가 같은 형태다.

| 런처 | 생성 | 제출 | 종결 |
|---|---|---|---|
| `dash::cl::AnsysMechanicalLauncher` | `ensureLauncherInitialized:948` | `submitAnsysTask:1057` | `onAnsysTaskTerminal:1120` |
| `dash::cl::AbaqusLauncher` | `ensureAbaqusLauncherInitialized:998` | `submitAbaqusTask:1087` | `onAbaqusTaskTerminal:1133` |
| `dash::cl::FeSafeLauncher` | `ensureFeSafeLauncherInitialized:345` | `launchFeSafePost:275` | `onFeSafeTaskTerminal:370` |

공통 규칙 셋 — **콜백 스레드 고정**(`makeCallbackDispatcher:1048` 이 모든 콜백을 `QMetaObject::invokeMethod(this, …, Qt::QueuedConnection)` 로 이 객체의 스레드에 큐잉. config 구조체가 `std::filesystem::path` 를 받아 수동 버퍼 수명 관리가 없다) · **재생성 조건**(실행파일 경로·CPU 수가 그대로면 재사용, 바뀌어도 진행 중 태스크가 있으면 경고 후 유지) · **태스크 맵 정리는 종결 콜백이 한다**(취소 `abort` 는 요청과 UI 반영까지만).

종결 콜백의 JSON 기록은 통일돼 있지 않다 — ANSYS 는 시그널만 올리고(모델이 기록), Abaqus·FE-safe 는 `DashDoeConfigManager` 를 직접 만들어 기록한 뒤 시그널도 올린다(같은 상태를 두 번 쓴다). → D10

#### 3-6-1. 분기 판정

```
generateInputCases(templateFilePaths, cachedSamples, targetPartName)
                                        model/DashJobRunner.cpp:1186-1923 (738줄)
  ├─ [공통] ProjectManager · IOController · IsProjectOpen 3중 가드     :1188-1202
  ├─ [공통] DOE JSON → headers · samples · rawSamples                  :1210-1261
  ├─ [공통] input_files[] → odbSourceAnalysisTypes (FE-safe ODB 후보)  :1231-1259
  ├─ [공통] templateFilePaths.first() 확장자로 4 플래그 결정           :1271-1279
  │           isStli / isDfsxml / isWbpj / isInp
  │           analysisType = 템플릿 basename → m_currentAnalysisType
  ├─ [공통] active 케이스 전부에 "Enqueued" 통지                       :1285-1293
  ├─ (A) isStli ──────────────────────────── FE-safe          :1300-1373  (74줄)
  ├─ (B) isWbpj ──────────────────────────── NX CAD + Journal :1376-1419  (44줄)
  ├─ (C) !templatePath.isEmpty() && !cachedSamples.isEmpty()
  │       && DashManager::Mgr() ──────────── 모핑 블록        :1425-1839 (415줄)
  │        ├─ (C-1) isDfsxml && hasMorphing → 모핑 + motion 체인      :1517-1682
  │        └─ (C-2) 그 외 → MorphFromDoeSamples                       :1686-1698
  │              ├─ (C-2a) isInp → Abaqus                             :1700-1763
  │              └─ (C-2b) 그 외 → ANSYS                              :1765-1839
  └─ (D) 폴백 ───────────────────────────── 템플릿 치환 + ANSYS :1841-1923  (83줄)
```

각 경로가 `return` 으로 빠지므로 (D) 는 **모핑 블록에 진입하지 못한 경우에만** 도달한다 — `cachedSamples` 가 비었거나 `DashManager::Mgr()` 가 없을 때다. → D10 · D11

#### 3-6-2. (A) `.stli` — FE-safe

앞선 워크플로가 만든 `.odb` 를 모아 후처리를 거는 경로다. 자기 입력을 스스로 만들지 않는다.

```
isStli 분기 :1300 — m_feSafeTemplateProjectAbsPath 부재면 중단 :1301-1304
  srcTypes = odbSourceAnalysisTypes - {자기 analysisType}       :1306-1310
  active 케이스마다 — run 디렉터리 mkpath (실패 → Failed)
    ├─ {src}/{runKey}.odb → {dst}/{srcType}.odb 복사            :1332-1350
    ├─ copied == 0 → Failed 후 continue
    └─ "Running" 기록 + launchFeSafePost(runKey, dstRunDir):275
          project_root = .stli 부모 · output_directory = run 디렉터리
          output_file_name = runKey · 같은 key 의 이전 task 는 abort
```

ODB 소스 후보는 `input_files[]` 중 확장자 `inp|dat|dfsxml|wbpj` 인 항목의 basename 집합이다(`:1249-1256`) — 레퍼런스 표에 남은 항목이 곧 ODB 소스 목록이며, 실제로 그 워크플로가 돌았는지는 검사하지 않고 파일 존재로만 판정한다. → D12

#### 3-6-3. (B) `.wbpj` — NX CAD STP → Ansys Journal

이 경로만 2단계로 나뉘고, 1단계가 케이스별 이벤트 구동 루프다.

```
isWbpj 분기 :1376 — input_files[] 에서 .wbpj + target_component(.prt) 확보 :1380-1404
  └─ runWbpjDoeAsync(...)                                        :2175
        ├─ m_stpBatch.active 이면 새 요청 무시 · NX CAD·ANSYS 경로 확보(없으면 중단)
        ├─ GeometryParameter_*.json 정규식 → "Independent Parameter" 적재 :2229-2253
        ├─ 전 케이스 STP 존재 선판정(allStpExist)
        │    NX 설정됨 → setBatchMode(true) / 미설정+allStpExist → 재사용 / 아니면 중단
        ├─ 케이스별 config JSON 조립 → m_stpBatch.pending · "connect 먼저, enqueue 나중"
        └─ startNextStpCase()                                     :2388
```

| 슬롯 | 위치 | 하는 일 |
|---|---|---|
| `startNextStpCase` | `:2388` | pending 1건 take → **잔존 STP 를 먼저 삭제**(`:2407`) → watchdog 600초 → `enqueueUpdatePrtGeometry` |
| `onStpCaseCompleted` | `:2416` | 경로 일치 → watchdog 정지 → `consecFail=0` → activeRunKeys 적재 → 다음 |
| `onStpCaseFailed` | `:2434` | Failed 기록 → `consecFail` 3회 연속이면 단계 중단 |
| `onStpCaseTimeout` | `:2466` | **케이스 실패 회계를 직접 하지 않는다** — 데몬을 `stop()` 해 `batchFailed` 하나가 회계를 맡게 한다 |
| `finishStpPhase` | `:2485` | 구독 해제 · `setBatchMode(false)` · 미착수분 "Cancelled" · 취소 아니면 `launchWbpjJournal()` |

잔존 STP 삭제의 근거는 주석이 밝힌다 — 파사드가 **출력 파일 존재로 성공을 판정**하므로 이전 파일이 남아 있으면 실패가 성공으로 위장된다.

Step 2(`launchWbpjJournal:2536`)는 STP 를 확보한 `activeRunKeys` 만 대상으로 Journal 을 **일괄 1회** 던지고, 완료 콜백이 케이스별로 `{outputBaseDir}/{runKey}` 를 뒤져 판정한다 — `*.dat` 없음 → "DAT file not generated" Failed / `*.rst` 있음 → Done / 없음 → "RST result not found" Failed (둘 다 최상위 → `QDirIterator::Subdirectories` 2단 탐색). `rawSamples` 를 `initIndParam` 의 전체 이름 순서로 재정렬해 넘기고(`:2562-2595`) DOE 가 건드리지 않는 파라미터는 GeometryParameter JSON 초기값으로 채운다 — **이 경로만 `rawSamples`, 나머지는 `samples`.** `connLog`(`:2614-2617`)는 빈 람다에 연결된 뒤 해제만 된다. → U5

#### 3-6-4. (C) 모핑 — `.dat` / `.inp` / `.dfsxml`

공통 전처리 넷 — ANSYS 런처 선확보(`:1433-1443`, `isInp` 가 아니면 `ensureLauncherInitialized()`. 실패해도 모핑은 진행하고 제출만 건너뛴다) · `referenceDatName` 정합(`:1455-1458`, 템플릿 basename ≠ `analysisType` 이면 **경고 후 덮어쓴다**) · active 필터(`:1462-1479`, active 키로 `cachedSamples` 를 걸러 `samplesForMorphing` 생성) · target part 해석(`:1480-1513`, 인자 → `input_files[].target_component` 순. `.inp` 인데 비면 경고만).

덮어쓰는 이유는 출력 경로다 — `DashJobRunner` 는 `{moduleDir}/{analysisType}/{runKey}` 를, `DashMorphingDoeExecutor` 는 `{moduleDir}/{referenceDatName}/{runKey}` 를 만들고(`Executor.cpp:151-161`) 두 조립기가 독립이라, 경고-후-덮어쓰기 한 줄이 둘의 일치를 강제한다. → D13

**(C-1) `.dfsxml` + Morphing — 모핑 → motion-writer → motion-launcher.** 이 모듈 `processEvents` 16곳 중 **8곳이 이 분기 안**(`:1569`\~`:1643`)에 있다.

```
isDfsxml && hasMorphing :1517 — source[] 의 "Morphing|{dat}|{part}" 파싱 → partName 주입
  ├─ mgr->MorphFromDoeSamples(..., sourceDatPath, ..., templatePath)  :1553
  ├─ QThread::msleep(1000) + processEvents  ← 모핑 완료 대기          :1568-1569
  ├─ active 케이스마다 — run 디렉터리 mkpath
  │     ├─ waitForVtuFileComplete(vtuPath, runKey, 60초)             :525
  │     │     존재 폴링 100ms → 크기 5회 연속 동일까지 (processEvents 5)
  │     ├─ runMotionWriter(refFolder, vtu, dfsxmlOut, 7816.9)        :593
  │     │     DashOptiMBD "motion-writer" 프로세스, 5분 상한 (processEvents 2)
  │     ├─ dfsxml 생성 확인 (없으면 Failed)
  │     └─ ANSYS 경로 있으면 m_motionLauncherQueue 적재, 없으면 "Done"
  └─ 스냅샷 3종 보관 후 startNextMotionLauncher()                     :788
```

`MorphFromDoeSamples` 는 동기 호출이라 반환 시점에 이미 전 샘플이 처리돼 있는데, `msleep(1000)` 은 그 뒤에 있고 주석은 "Give some time for morphing to start" 다. → D14
motion-launcher 는 **직렬 큐**다 — `startNextMotionLauncher:788` 이 1건 take → `runMotionLauncher:663` 이 `QProcess` 를 띄우고 `finished` 람다가 판정 후 다음 건을 큐잉한다(`:763`). 성공 판정 특이점 — exit code 0 인데 `{runKey}.dfr` 이 없으면 하드코딩 XML 로 만들어 넣고 Done 마감(`:689-720`). → D15
동시에 `monitorMotionLauncherOutput:816` 이 stdout 의 `SUCCESS`/`COMPLETED`/`FAILED`/`ABORT` 로도 상태를 올린다 — 판정 주체가 둘이고 중복 방지는 JSON 의 현재 status 재확인뿐이다. → D16

**(C-2) `.dat` / `.inp` — MorphFromDoeSamples.** 진입부가 인터랙션 인스턴스와 해석 컨텍스트를 둘 다 공유본으로 배치에 넘긴다.

```
mgr->MorphFromDoeSamples(samplesForMorphing, canonicalPath, cb, ...) :1686
   └─ DashManager::MorphFromDoeSamples                  DashManager.cpp:1003
        ├─ GetHandlePickingInteraction() — GUI 가 쓰는 그 인스턴스    :1013-1019
        ├─ DashAnalysisModelContextRegistry::getOrLoad(canonicalPath) :1027-1034
        └─ DashMorphingDoeExecutor(스택)::Execute(...)                :1036-1039
              Executor.cpp:47 전처리 — DOE JSON 재파싱 → Geometry/Condition
              파일명 → runsBaseDir → DV-Condition 맵 → DV-Geometry meta 를
              handlesArray 로 → Morphing.radius 커널 반경
              → Morphing.handles_vtp 를 loadHandlesFromVtp 로 적재
                 = interaction->GetMorphingHandles()->DeepCopy :1054-1077 → D17
샘플 루프 :342-426 — runKey → partName → DOE 값 → condition DV 부착
                   → 템플릿 확장자로 출력 경로(dfsxml=VTU만 / dat / inp)
  ExecuteOneSample(...)                                               :544
    ├─ interaction = Mgr()->GetHandlePickingInteraction()             :553
    ├─ ug 3단 해석 — getPartData(partName) → getPartNames().first() → GetInputVTU() :565-582
    ├─ currentHandles = interaction->GetMorphingHandles()             :584  → D17
    ├─ ug points 를 double 로 in-place 승격                            :599-604
    ├─ meta 의 group id / handle id 로 변위 맵 → SetInitialHandles     :612-823
    ├─ editedModel = Mgr()->RunVolumeMorphing(...):835 · {runKey}.vtu 기록 :865-868
    └─ outputDatPath 있으면 :886 — rwApplyConditionDvs:902-906
          · ctx->updateMeshPoints:909-916 · ctx->exportSolverInput:919-922
          · 원복 2줄 — basePart updateMeshPoints + rwRestoreConditionDvs :927-930
```

`Execute` 가 전 샘플을 훑어 채우는 `firstPartName`(`:164-174`)은 이후 읽는 곳이 없다. → U5

**변이 대상이 GUI 와 공유된 세션이다.** 주석(`:890-899`)이 전제를 명시한다 — `analysisContext` 는 레지스트리 공유본이고 정합성은 원복 두 줄에만 기대며, export 나 원복이 실패하면 세션이 오염된 채 남는다. 지금 레이스가 아닌 이유는 이 경로가 GUI 스레드에서 돌기 때문일 뿐이다. → D18
condition DV 주입(`rwApplyConditionDvs:441-491`)의 세 실패 경로는 모두 **warning 후 `continue`** — 건너뛴 필드는 레퍼런스 값으로 export 되고 샘플은 성공으로 마감된다. 원복(`rwRestoreConditionDvs:496-508`) 실패도 warning 뿐. → D19

**(C-2a) `.inp` — Abaqus / (C-2b) ANSYS.** 둘 다 run 디렉터리 mkpath → 모핑이 만든 입력 파일 존재 확인(없으면 Failed) → 태스크 제출 → "Running" 기록이다. Abaqus 만 `m_abaqusRunDirs` 에 출력 디렉터리를 보관해 실패 시 진단 목록(`*.log *.msg *.sta …` + `logs/`)을 로그로 남긴다(`onAbaqusTaskTerminal:1160-1183`). ANSYS 는 `{runKey}.vtu` 존재를 로그로만 남기고 판정에 쓰지 않는다.

#### 3-6-5. (D) 폴백 — 템플릿 치환 + ANSYS

템플릿 전문을 읽고, active 케이스마다 run 디렉터리를 만든 뒤 `writeCaseDat:443` 으로 헤더 이름을 값으로 치환해 `{key}.dat` 을 쓴다. 런처가 없으면 파일 생성까지만 한다. 모핑도 외부 데몬도 거치지 않는 경로다.

### 3-7. 상태 반영·종결

```
DashJobRunner::caseStatusUpdated(key, status, analysisType)
  └─ DashAnalysisLauncher::onCaseStatusUpdated                       :1020
        ├─ setSampleStatus(key, status, analysisType, m_doeJsonPath) :966
        │     ├─ QMutexLocker(m_statusFileMutex)
        │     ├─ JSON 전문 read → samples[] 선형 탐색 → statusKey 갱신 → 전문 write
        │     │     statusKey = analysisType 비면 "status", 아니면 "status_{analysisType}"
        │     └─ emit caseStatusUpdated(key, status)   ← 2인자 시그널로 재방출
        └─ 완료 집계 — m_expectedRunKeys 에 있고 Done|Failed|Cancelled 이면
              m_completedRunKeys 에 넣고 크기가 같아지면 analysisFinished  :1026-1036
```

재방출된 2인자 시그널은 `DashDoeCasesWidget::updateCaseStatus:276` 이 받아 Case Name 열 basename 과 key 를 비교해 행을 찾고 Status 를 갱신한다. 동시에 JSON 이 바뀌었으므로 `QFileSystemWatcher` 가 `updateFromDvTable` 전량 재구축도 유발한다.

**종결 신호가 두 갈래다.** 키 집합 소진 집계(`onCaseStatusUpdated:1026-1035`, 전 경로)와 `jobFinished` 직접 방출(`DashJobRunner.cpp:2156` Direct wbpj · `:2664` DOE wbpj, Journal 두 경로만)이 모두 `analysisFinished` 로 이어진다(`DashAnalysisLauncher.cpp:54`). `jobStarted` 는 `runDirectJobs:2079` 한 곳뿐이고, FE-safe·모핑·폴백 세 경로는 `jobFinished` 를 영영 방출하지 않고 키 집계에만 의존한다. → D21

`analysisFinished` 수신처는 셋 — 버튼 상태 복구(`Base.cpp:126-130`) · 케이스 표 재적재(`:98-105`, 선택 파일이 `.wbpj` 면 건너뜀) · Direct 위젯 버튼 복구(`Direct.cpp:51-57`). 설정 JSON read-modify-write 지점은 8곳이고 뮤텍스로 보호되는 것은 하나뿐이다(6절). → D22

### 3-8. 결과 열람

DOE Analysis 탭은 `DashResultsAnalyzerWidget` 을 임베드한다(`Base::setupAnalysisTab:157`, 모드 `AnalysisLauncher`). Direct variant 에는 이 탭이 없어 `analyzerHost` 가 null 로 남는다(`DashMainWindow.cpp:1280`).

| 사용자 행위 | 함수 체인 |
|---|---|
| 탭 전환 | `Base::onTabChanged:232` → `analyzerWidget->setSetName` → `initializeTargetData()` |
| 플롯 요청 | `plotRequested` → `requestPlot:1136` → `updateConfigFile:1164` (설정 JSON 기록) → `DashPlotSpecBuilder::build` → `plotSpecReady` → `onPlotSpecReady` |
| 플롯 완성 | `analysisResultReady` → `DashMainWindow::onPlotReady` |

플롯 요청도 설정 JSON 을 경유한다 — 먼저 파일에 명령·설정을 쓰고 그 경로를 스펙 빌더에 넘긴다.

### 3-9. 크리티컬 패스 밖의 경로

**[Stop] — 취소.** `Base.cpp:219` / `Direct.cpp:125` 람다 → `cancelAllRuns:1150` → `DashJobRunner::cancelAllRuns:859` → 추적 상태 초기화 → `emit analysisFailed("Cancelled by user")`.

| 대상 | 위치 | 방식 |
|---|---|---|
| motion `QProcess` | `:866-883` | `kill()` + `waitForFinished(3000)` → Cancelled 통지 |
| FE-safe / Abaqus / ANSYS 태스크 | `:885-912` | 런처 `abort(taskId)` — 맵 정리는 종결 콜백이 |
| STP 배치 | `:927-933` | **협조적 취소** — `m_stpBatch.cancelled = true` 만 세운다 |

STP 배치만 다른 이유는 주석이 밝힌다 — 진행 중 1건은 완료를 수용해 결과를 보존하고 잔여만 미착수로 둔다. 그래서 배치 중에는 NX CAD 데몬을 죽이지 않고(`:936-940`) Journal 데몬은 조건 없이 `stop()` 한다. `m_motionLauncherQueue` 는 이 함수에서 비우지 않는다. → D23

**Direct Launcher.** DOE 없이 고른 파일을 그대로 제출하는 별도 경로로, 설정 JSON 의 샘플과 무관하다. `[Start]`(`Direct.cpp:105`) → CPU 적용 → `getInputCaseFilePaths():295`(표 0열 `QLineEdit` 수집) → `runDirectLauncherAsync:1087`(각 파일 `completeBaseName` 을 `m_expectedRunKeys` 로) → `runDirectJobs:1924`. 확장자로 4묶음을 만든 뒤 **순차로 전부 처리한다** — DOE 경로처럼 하나를 골라 return 하지 않는다.

| 묶음 | 처리 | runKey | outDir |
|---|---|---|---|
| `.dat` | `ensureLauncherInitialized` → `submitAnsysTask` | 파일 basename | 파일이 있는 디렉터리 |
| `.inp` | `ensureAbaqusLauncherInitialized` → `submitAbaqusTask` | 파일 basename | 파일이 있는 디렉터리 |
| `.dfsxml` | `m_motionLauncherQueue` 적재 후 "Pending" → `startNextMotionLauncher` | 파일 basename | 파일이 있는 디렉터리 |
| `.wbpj` | `nxCad->enqueueLoadPrt(prt, stp)` → `loadPrtCompleted` 람다 → `launchAnsysJournalDirect:2086` | **prt** basename | prt 가 있는 디렉터리 |

제출 키는 `m_directRunKeys` 에 들어가고(`:1954`·`:1988`) 종결 콜백이 그 집합으로 direct 를 판별해 **JobRunner 측 JSON 기록을 건너뛴다**(`:1122-1124`·`:1135-1137`). 다만 `caseStatusUpdated` 의 analysisType 이 빈 문자열이라 모델의 `onCaseStatusUpdated` 는 여전히 `"status"` 키로 현재 Set 의 DOE JSON 을 연다. → D24

**Direct 의 Output Cases 표** — `m_directOutputCasesWidget` 은 `DashDoeCasesWidget` 인스턴스인데 `setModel()` 도 상태 시그널 연결도 없고, `setDirectLauncherCases:593` 이 Status 를 `"Enqueued"` 로 고정 기입한다. → U2
**Resample 탭** — `.ui` 742줄에 UI 는 있고(콤보 2 · 스핀박스 1 · 표 2 · 버튼 2) `setupUI` 는 포인터 별칭만 잡는다(`Resample.cpp:22-44`). 연결도 로직도 없다. → U1

**호출부가 없는 코드 8종, 총 269줄.** → U4

| 대상 (위치 · 줄 수) | 비고 |
|---|---|
| `DashJobRunner::createRunsFolders` (`DashJobRunner.cpp:478-508` · 31) | `processEvents` 1곳 포함 |
| `DashAnalysisLauncher::createRunsFolders` (`:916-954` · 39) | `{moduleDir}/runs{N}` — 실사용 레이아웃과 다름 |
| `DashJobRunner::isFeSafePostEnabled` (`:269-273` · 5) | `QSettings` 를 읽지만 아무도 묻지 않는다 |
| `DashDoeCasesWidget::getStatusFromFileSystem` (`:429-482` · 54) · `getErrorLogFromFileSystem` (`:483-583` · 101) | — |
| `DashReferenceFileWidget::applySmartSelectionRules` (`:920-932` · 13) | 플래그를 세웠다 즉시 내리는 빈 스텁 |
| `DashAnalysisLauncher::writeCaseDat` (`:906-914` · 9) · `isDfsxmlWithMorphing` (`:1405-1421` · 17) | 위임 래퍼. 실사용은 `DashJobRunner` 직접 호출 |

---

## 4. 말단 6경로 대조

6개 말단 경로와 Direct Launcher 가 **착수·상태보고·종결을 각자 구현한다**. → D10

| 항목 | (A) stli | (B) wbpj | (C-1) dfsxml | (C-2a) inp | (C-2b) ansys | (D) 폴백 | (Direct) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `Enqueued` 선통지 | O | O | O | O | O | O | X |
| JSON 상태 기록 주체 | 콜백 + 모델 (2회) | 콜백 캡처 + `finishStpPhase` | `configManager` 지역 | 콜백 + 모델 (2회) | 모델만 | `configManager` 지역 | 모델만 |
| `analysisType` 동봉 | O | O | 일부 | O | O | 일부 | **X (빈 문자열)** |
| `jobFinished` 방출 | X | **O** | X | X | X | X | **O (케이스마다)** |
| 완료 판정 근거 | 런처 TerminalState | `*.dat`+`*.rst` 존재 | exit code + stdout 문자열 + `.dfr` 존재 | 런처 TerminalState | 런처 TerminalState | 런처 TerminalState | 혼합 |
| 취소 방식 | `abort` | 협조적(플래그) | `kill()` | `abort` | `abort` | `abort` | 대상별 상이 |

`.wbpj` DOE 경로만 종결 신호를 두 갈래로 올린다 — 키 집계와 `jobFinished` 가 모두 `analysisFinished` 에 닿는다. → D21

`processEvents` 16곳은 전부 `DashJobRunner.cpp` 안이고 전부 "기다리는 동안 UI 를 살려두기" 목적이다. → D11

| 위치 | 함수 | 개수 | 무엇을 기다리나 |
|---|---|:---:|---|
| `:504` | `createRunsFolders` | 1 | (호출부 없음 → U4) |
| `:533` `:538` `:557` `:578` `:583` | `waitForVtuFileComplete` | 5 | VTU 존재 + 크기 안정화 (100ms 폴링, 60초 상한) |
| `:628` `:632` | `runMotionWriter` | 2 | motion-writer 프로세스 (500ms 폴링, 5분 상한) |
| `:1569`\~`:1643` | `generateInputCases` (C-1) | 8 | 모핑 완료 · 샘플 루프 진행 |

이 구간에서 이벤트 루프가 열리므로 [Start] 재클릭 · 탭 전환 · 트리 클릭(= `setModel` 재진입)이 실행 중에 재진입할 수 있다. 재진입 차단은 `m_analysisWatcher.isRunning()`(샘플링만)과 `m_stpBatch.active`(STP 배치만) 두 곳뿐이다.

---

## 5. 계약을 대신하는 문자열

도메인 타입이 없는 자리를 문자열·파일명·확장자가 메운다.

| 계약 | 실제 판별 | 위치 |
|---|---|---|
| variant | `"Init"`/`"Resample"`/`"Direct"` + Set 이름 접미 폴백 | `DashProject.cpp:690-703` · `DashMainWindow.cpp:1250-1266` |
| 워크플로 선택 | 템플릿 파일 확장자 | `DashJobRunner.cpp:1274-1277` |
| analysisType | 템플릿 파일 basename | `:1278` |
| runKey | `"runs{i+1}"` 리터럴 | `DashDoeConfigManager.cpp:308` |
| 상태 키 | `"status_{analysisType}"` 조립 | `DashAnalysisLauncher.cpp:979` · `DashDoeCasesWidget.cpp:227` |
| Geometry/Condition JSON 판별 | `contains` 2종 + 정규식 1종 | 3-5 → D6 |
| DV source 의 모핑 정보 | `"Morphing\|{dat}\|{part}"` `\|` 분리 | `DashAnalysisLauncher.cpp:1442` · `DashDoeConfigManager.cpp:242` · `DashReferenceFileWidget.cpp:992` |
| Purpose → Method | 5개 문장 완전일치 | `DashAnalysisLauncher.cpp:631-655` → D3 |
| Method → 샘플러 | method 이름 문자열 | `:369-582` |
| option2 위젯 선택 | 옵션 이름 `"Level"`/`"Constrained function"` | `view/DashAnalysisLauncherWidget.cpp:617-683` |
| 케이스 표 행 ↔ 케이스 | Case Name 열 텍스트의 `completeBaseName()` | `view/DashDoeCasesWidget.cpp:290` `:322` → D8 |
| motion-launcher 결과 | stdout 의 `SUCCESS`/`COMPLETED`/`FAILED`/`ABORT` | `DashJobRunner.cpp:816-858` |
| condition DV ↔ FE entry | `uuid` → 이름 조회 실패 시 **dvKey 를 표시명으로 간주** | `DashMorphingDoeExecutor.cpp:453-456` |

케이스 표는 행 ↔ 케이스 결합을 표시 텍스트 파싱으로 유지한다 — `Qt::UserRole` 도 별도 키 컬럼도 쓰지 않는다.

---

## 6. 상태 소유 지도

같은 사실이 여러 곳에 병행 보관된다. 어느 것이 정본인지는 읽는 시점에 따라 달라진다.

| 상태 | 1차 보관 | 병행 보관 | 실행 시 읽는 곳 |
|---|---|---|---|
| 설계변수 (type/min/max/cases) | `DashDesignVariableModel` | DV 표 셀 위젯 · 원본 파라미터 JSON | **워커가 모델을 직접** → D4 |
| Probabilistic Min/Max | DV 표 셀 위젯 | `m_probabilisticMin/MaxOverrides` | 워커가 위치 인덱스로 → D2 |
| DOE 샘플 | `DOE Table.samples[]` (values 배열) | `rawSamples[]` (파라미터명 키) · `m_cachedSamples` | 경로마다 다름 — `.wbpj` 만 `rawSamples` → D5 |
| 모핑 핸들 | `DashHandlePickingInteraction` polydata (싱글턴) | Set 별 `{Set}.vtp` | 배치가 VTP 로 **덮어쓴 뒤** 그 자리에서 읽는다 → D17 |
| 해석 모델 (메시 · FE condition) | `DashAnalysisModelContextRegistry` 공유 컨텍스트 | `basePart` 사본 · `appliedFeEdits` | 배치가 변이 후 원복 2줄로 → D18 · D19 |
| 케이스 active | `DOE Table.samples[i].active` | 케이스 표 0열 체크박스 | JSON |
| 케이스 status | `DOE Table.samples[i].status_{type}` | 케이스 표 Status 열 | JSON (파일 감시로 표에 되반영) → D7 |
| 케이스 log | — | 케이스 표 Log 열 (재구축 시 메모리 백업/복원) | 저장 안 됨 |
| 레퍼런스 파일 목록 | `input_files[]` | 레퍼런스 표 행 · `DOE Table.source[]` | 두 배열을 각각 읽어 표를 조립 |
| 실행 템플릿 선택 | 레퍼런스 표 라디오 | `m_referenceTemplates` · `m_inputReferenceFileName` | 라디오 |
| variant | JSON `variant` 키 | `m_variant` · 트리 `UserRole+2` · Set 이름 접미 | 트리 role (라우팅) · JSON (로드) |
| analysisType | 템플릿 basename 에서 매번 재계산 | `m_currentAnalysisType` · `m_stpBatch.analysisType` | 호출부마다 다름 |
| 태스크 핸들 | 런처별 `QMap<runKey, TaskId>` (`m_activeTasks`·`m_abaqusTasks`·`m_feSafeTasks`) | `m_directRunKeys` | 종결 콜백이 제거 |
| CPU 코어 수 | `DashManager` 싱글턴 | variant 별 스핀박스 | 싱글턴 |

`DashManager::Mgr()` 도달은 `DashJobRunner.cpp` 13회 · `DashReferenceFileWidget.cpp` 5회 · `DashMorphingDoeExecutor.cpp` 5회(엔진 커널 반경 · 핸들 인터랙션 · 입력 VTU 폴백 · 초기 핸들 · 볼륨 모핑) · 위젯 베이스/Direct 각 3회이고, 모델 계층(`DashAnalysisLauncher`·`DashDoeConfigManager`)은 0회다.

설정 JSON read-modify-write 8곳 — `saveSettings:780`(`DOE configuration`) · `setSampleStatus:966`(`samples[i].status_*`, **유일하게 뮤텍스**) · `updateConfigFile:1164`(`DOE Analysis`) · `DashDoeConfigManager::saveInputFileSettings:140`(`input_files[]`) · `saveResultsAsDvTable:180`(`DOE Table` 전체) · `DashDoeConfigManager::setSampleStatus:528`(콜백이 인스턴스를 새로 만들어 호출) · `DashDoeCasesWidget::saveAllActiveStates:334` · `persistActiveFlag:397`(`samples[].active`). 뮤텍스는 `DashAnalysisLauncher` 인스턴스 멤버라 콜백 경로는 통과하지 않는다. → D22

---

## 7. 결함 목록

3\~6절 서술 중 **동작이 의도와 어긋나거나 어긋날 수 있는 지점**을 모았다. `D` 는 잘못 구현된 것 25건, `U` 는 구현되지 않은 것 4건. 교차 색인이 이 ID 를 참조하므로 번호는 고정이고 `D20` 은 결번, `U1` 은 제외다. 9개 모듈 교차 색인은 [[Cross-Module-Defect-Index]].

| ID | 분류 | 결함 | 좌표 | 근거와 귀결 |
|---|---|---|---|---|
| **D1** | 진입·수명 | 초기화 순서를 코드가 아니라 재호출로 맞춘다 | 3-1 | 진입 1회에 `loadSettings:844` 3\~4회 — `DashMainWindow:1244`·`Base::setModel:62`(+`:70`)·`Init::setModel:307`. 앞의 것들은 시그널 연결 전이라 수신처가 없다(주석 `Widget.cpp:303-306`) → 같은 파일을 여러 번 읽고 대부분 버린다 |
| **D2** | 데이터 정본 | Probabilistic Min/Max 가 모델에 되쓰이지 않고, 워커가 위치 인덱스로만 소비한다 | 3-2 · 3-4 | 값은 `updateMinMaxFromMeanStd:1026` → `…Overrides:69` 로 샘플링에만 전달(의도는 `.h:78-79`) → 편집값이 저장처가 없어 **다음 진입 때 사라지고**(CSV import 동일), 워커가 override 를 모델 행 인덱스로 첨자한다(`:331-332`, 크기 가드 없음) |
| **D3** | 구조·결합 | Purpose 판정이 문장 완전일치이고 리터럴이 이중 정의 | 3-3 · 5절 | 다섯 문자열이 `getPurposeOptions():878` 과 `onSetButtonClicked:631-655` 에 각각 박혀 상수를 공유하지 않고, 어긋나면 `else { return; }` → **[Set] 을 눌러도 갱신도 경고도 없다** |
| **D4** | 실행 모델 | 워커가 GUI 소유 DV 모델을 직접 읽는다 | 3-4 · 6절 | `QtConcurrent::run:235` → `runAnalysisInThread:286` 이 `m_designVariableModel->data(...)`(`:310`·`:326-348`), 결과 기록도 모델 포인터 그대로(`:266`). 워커 진입 시점의 값 스냅샷이 없어 경계가 포인터 하나다 |
| **D5** | 데이터 정본 | 같은 샘플이 두 형태로 저장되고 하류가 경로마다 다른 쪽을 읽는다 | 3-4 · 6절 | 위치 기반 `samples[].values` vs 파라미터명 키 `rawSamples[]`(`DashDoeConfigManager.cpp:394`). `.wbpj` 만 후자(`DashJobRunner.cpp:2562-2595`) → 한쪽만 갱신하는 변경이 경로별로 다르게 보인다 |
| **D6** | 구조·결합 | 같은 Geometry/Condition 판별을 세 곳이 각자 다른 규칙으로 구현 | 3-5 · 5절 | `DashAnalysisLauncher.cpp:1242`·`:1290` 대소문자 구분 `contains` / `DashMorphingDoeExecutor.cpp:130`·`:134` `Qt::CaseInsensitive` / `DashJobRunner.cpp:2229` 정규식 → 파일명 대소문자·접두가 바뀌면 판정이 갈린다 |
| **D7** | 실행 모델 | 케이스 표 재구축이 케이스 수만큼 유발된다 | 3-5 · 3-7 | `setSampleStatus:966` 이 케이스 1건마다 JSON 전문 재기록, 워처(`DashDoeCasesWidget.cpp:102-105`)가 그때마다 `updateFromDvTable:108` 전량 재구축 → N 케이스면 N 회 |
| **D8** | 데이터 정본 | 표 행 ↔ 케이스 결합이 표시 텍스트 파싱 | 3-5 · 5절 | `updateCaseStatus:276` 이 Case Name 열의 `completeBaseName()` 을 key 와 비교해 행을 찾는다(`:290`·`:322`). `Qt::UserRole` 도 키 컬럼도 없다 → 표시 규칙(`.wbpj` → `.rst`)이 바뀌면 결합이 끊긴다 |
| **D9** | 실행 모델 | `runDoeAsync` 는 비동기가 아니다 | 3-6 | `generateInputCases` 738줄 전체가 GUI 스레드 동기 실행(`:1063`). 워커로 나가는 것은 [Run] 의 DOE 샘플링뿐 |
| **D10** | 구조·결합 | 말단 6경로가 착수·상태보고·종결을 각자 구현 | 3-6 · 4절 | 4절 대조표. JSON 기록이 셋으로 갈린다 — ANSYS·Direct 모델만, Abaqus·FE-safe 는 콜백과 모델이 **두 번**(`:1146-1150`·`:373-377`), 모핑·폴백은 지역 `configManager` |
| **D11** | 실행 모델 | `processEvents` 16곳이 동기 대기의 대체물 | 3-6 · 4절 | 전부 `DashJobRunner.cpp`(4절 분포표). 이벤트 루프가 열려 [Start] 재클릭·탭 전환·트리 클릭(= `setModel` 재진입)이 가능하고 차단은 두 곳뿐 |
| **D12** | 데이터 정본 | FE-safe 의 ODB 소스 판정이 워크플로 실행 여부를 보지 않는다 | 3-6-2 | 후보는 `input_files[]` 중 `inp\|dat\|dfsxml\|wbpj` 항목의 basename(`:1249-1256`) — 표에 남아 있기만 하면 소스다. 판정은 `{src}/{runKey}.odb` 존재뿐, 현재 DOE 의 것인지는 안 본다 |
| **D13** | 구조·결합 | 경로 조립기 두 개의 일치를 경고-후-덮어쓰기 한 줄이 강제 | 3-6-4 | `{moduleDir}/{analysisType}/{runKey}` vs `{…}/{referenceDatName}/{runKey}`(`Executor.cpp:151-161`). `:1455-1458` 이 다르면 덮는다 → 빠지면 모핑 산출물과 제출 경로가 갈린다 |
| **D14** | 실행 모델 | `msleep(1000)` 이 동기 호출 뒤에 있다 | 3-6-4 | `MorphFromDoeSamples` 반환 시점에 전 샘플이 끝나 있는데 `:1568` 이 "Give some time for morphing to start" 주석과 함께 1초를 잔다 → 케이스 수와 무관한 고정 지연 |
| **D15** | 실행 모델 | motion-launcher 가 결과 파일이 없으면 결과 파일을 만들어 낸다 | 3-6-4 | `runMotionLauncher:689-720` — exit code 0 인데 `{runKey}.dfr` 이 없으면 하드코딩 XML 로 생성하고 Done 마감 → 존재로 판정하는 하류가 실패를 성공으로 읽는다 |
| **D16** | 실행 모델 | 한 케이스의 완료 판정 주체가 둘 | 3-6-4 | `finished` 람다(`:726`)와 stdout 감시(`:816`)가 각각 상태를 올린다. 중복 방지는 현재 status 재확인뿐 → 어느 쪽이 남는지는 도착 순서로 정해진다 |
| **D17** | 데이터 정본 | 모핑 배치가 GUI 의 핸들 polydata 를 덮어쓴다 | 3-6-4 · 6절 | `GetHandlePickingInteraction()` 싱글턴을 배치에 넘기고 `loadHandlesFromVtp` 가 `GetMorphingHandles()` 에 VTP 를 `DeepCopy`(`Executor.cpp:1054-1077`) → **DOE 1회로 열려 있는 Set 의 핸들 배열이 VTP 내용으로 교체된다** |
| **D18** | 실행 모델 | 배치가 GUI 와 공유된 해석 컨텍스트를 변이하고 원복 두 줄에 의존 | 3-6-4 · 6절 | 공유본을 그대로 넘기고(`DashManager.cpp:1027-1028`) points 를 in-place double 승격(`:599-604`) 후 변이, 두 줄로 원복(`:927-930`). 주석(`:890-899`)이 전제를 명시 — 실패 시 세션 오염이 남고, 지금 레이스가 아닌 이유는 GUI 스레드 실행뿐이다 |
| **D19** | 데이터 정본 | condition DV 적용 실패가 조용한 skip | 3-6-4 | `rwApplyConditionDvs:441-491` 의 세 실패 경로(legacy `param` 없음 · entry 없음 · `editFeConditionEntry` 실패)가 모두 warning 후 `continue`, 호출부는 검사 없이 export → **해당 필드만 레퍼런스 값인 deck 이 성공으로 남는다** |
| **D21** | 구조·결합 | 종결 신호가 두 갈래이고 한 경로만 양쪽을 올린다 | 3-7 · 4절 | 키 집계(`:1026-1035`)와 `jobFinished`(`DashJobRunner.cpp:2156`·`:2664`)가 모두 `analysisFinished` 에 닿는다(`:54`). FE-safe·모핑·폴백은 영영 방출 안 함, `.wbpj` DOE 는 양쪽, Direct `.wbpj` 는 케이스마다 |
| **D22** | 데이터 정본 | 설정 JSON 동시 쓰기 보호가 한 곳에만 있다 | 3-7 · 6절 | 8곳 중 뮤텍스를 지나는 것은 `setSampleStatus:966` 하나이고 인스턴스 멤버라, 콜백이 새로 만드는 `DashDoeConfigManager::setSampleStatus:528` 은 통과하지 않는다 → 콜백 두 건이 겹치면 전문 재기록끼리 덮어쓴다 |
| **D23** | 실행 모델 | 취소가 motion 큐를 비우지 않는다 | 3-9 | `cancelAllRuns:859` 가 `QProcess` 를 `kill()` 하지만 `m_motionLauncherQueue` 는 그대로이고 `finished` 람다가 `startNextMotionLauncher` 를 큐잉한다(`:763`) → **취소 후 잔여 큐가 이어서 돈다** |
| **D24** | 데이터 정본 | Direct Launcher 의 상태가 현재 Set 의 DOE JSON 에 쓰인다 | 3-9 | JobRunner 는 `m_directRunKeys` 로 건너뛰지만(`:1122-1124`·`:1135-1137`) analysisType 이 빈 문자열이라 `onCaseStatusUpdated:1020` 이 `"status"` 키로 현재 Set 의 JSON 을 연다. 케이스 키가 사용자 파일명이라 `runs{N}` 과 안 맞으면 전문 재기록만 된다 |
| **D25** | 진입·수명 | 릴리스 빌드에서 Resample variant Set 을 고르면 아무 일도 일어나지 않는다 | 3-1 · 1절 | `65e5673` 이 Resample 을 DEV 전용으로 가드해 릴리스는 `m_analysisLauncherResampleWidget` 을 **생성하지 않는다**(`DashMainWindow.cpp:483-486`). 라우팅은 널 가드로 넘어가고(`:1258-1263`) `targetWidget` 이 null 이면 `setCurrentWidget` 을 건너뛴다(`:1277-1279`) → **DEV 빌드에서 만든 프로젝트(또는 `-Resample` 접미 Set)를 릴리스로 열면 dock 이 직전 모듈 화면에 머물고 경고도 로그도 없다.** [+ New Set] 메뉴에서 항목만 가린 것(`DashProjectWidget.cpp:233-245`)이라 이미 만들어진 Set 은 트리에 그대로 남는다 |
| **D26** | 데이터 정본 | 제약식의 `v{n}` 토큰이 행 인덱스 유래인데 심볼이 저장되지 않는다 | 3-2 · 3-4 | Symbol 열은 행 번호에서 즉석 생성되고(3-2) 실행 시 `QString("v%1").arg(i+1)` 로 실제 변수명에 치환된다(`:404`·`:517`). 반면 사용자가 적은 제약식은 `m_methodOptions` 로 설정 JSON 에 영속화되고(`:808`) 그대로 복원된다(`:859`) → **DV 행을 추가·삭제·재정렬하면 저장된 제약식의 `v{n}` 이 다른 변수를 가리키고 화면에 표시가 없다.** Optimizer 의 D24 와 같은 기제다 |
| **U1** | 미구현 | ~~Resample 탭이 UI 만 있고 로직이 없다~~ | 3-9 · 1절 | **제외** — 착수 대기 기능 갈래다. `65e5673` 이 DEV 빌드 전용으로 가드했고 `2694b53` 이 UI 를 신규 디자인으로 교체했다. 결함이 아니라 예정 작업이며, 가드가 만든 결함은 D25 가 보유한다 |
| **U2** | 미구현 | Direct 의 Output Cases 표가 상태 갱신 경로를 갖지 않는다 | 3-9 | 베이스를 상속하지 않아 `setModel()` 도 시그널 연결도 없고 `setDirectLauncherCases:593` 이 Status 를 `"Enqueued"` 고정 기입 → **실행 중 표가 움직이지 않는다** |
| **U3** | 미구현 | `visibleParamIndices` 가 계산만 되고 쓰일 열이 없다 | 3-5 | `updateFromDvTable:157-182` 이 인덱스를 고르고 안 맞으면 전 인덱스를 다시 넣는다. 표는 4열 고정이라 반영될 열이 없다 |
| **U4** | 미구현 | 호출부가 0인 함수 8종 | 3-9 | 3-9 표, 총 269줄 — `createRunsFolders` 2종 · `isFeSafePostEnabled` · `getStatus`/`getErrorLogFromFileSystem` · `applySmartSelectionRules`(빈 스텁) · 위임 래퍼 2종 |
| **U5** | 미구현 | 도달하지 않는 연결·계산 3종 | 3-1 · 3-6-3 · 3-6-4 | `connLog`(`DashJobRunner.cpp:2614-2617`) 빈 람다 · `.ui` `purposeCombo` 2항목(`:211-212`) `clear()` 로 덮임 · `firstPartName`(`Executor.cpp:164-174`) 읽는 곳 없음 |

---

## 8. 검증 한계

| 항목 | 근거 강도 | 비고 |
|---|---|---|
| variant 3분기 · 탭 구성 · 소유 클래스 · 줄 수 | **강** | `.ui` 정적 구조 + 라우팅 코드 + 줄 수 실측 |
| 함수 체인·줄 번호 (3절 전반) · `generateInputCases` 4분기 6경로 | **강** | 함수 본문 직접 확인 (738줄 전문 포함) |
| cae-launcher 런처 3종 (3-6-0) | **강** | 생성·제출·종결 3경로 전문 |
| `processEvents` · `Mgr()` · 미호출 함수 카운트 | **강** | grep 전수 |
| D11 재진입 발생 · D16·D21 도착 순서 · D17 화면 체감 | **중** | 코드 사실(`processEvents` 위치 · 판정 주체 둘 · polydata 덮어쓰기)은 확정. 런타임 순서·빈도·재그리기 시점은 미확인 |
| 외부 데몬 · cae-launcher 내부 · 빌드 실행 | **없음** | 별도 저장소라 GUI 호출측 코드로만 확인. 실행 검증은 ANSYS·Abaqus·NX·MBD 설치 환경 필요 |

---
