# Model Builder — 사용자 플로우 ↔ 코드 대응

XML 구조와 DeepOpt 내부 학습 처리의 상세는 [Model Builder XML 구성과 DeepOpt 학습 입출력](Model-Builder-XML-DeepOpt-Pipeline.md)을 참고한다. 해당 문서는 GUI와 DeepOpt의 2026-10-02 로컬 소스를 별도로 대조한 기록이다.

> **성격**: 독립 참조 문서. 사용자 행위가 어떤 함수 체인을 밟는지의 대응표 — 수정 계획·우선순위 판정은 담지 않는다. Sim(`DashModelBuilderWidget`)·MCU(`DashModelBuilderMCUWidget`) 두 경로 모두 다루며, 둘은 위젯·모델이 각각 별개이고 베이스 클래스 하나를 공유한다.
> **좌표 기준**: `dev` @ `4c7608e` 실측(유효기간 있음). 정적 코드 근거만 — 빌드·실행 검증 없음.
> **좌표 표기**: `W:` = `view/DashModelBuilderWidget.cpp` · `MW:` = `view/DashModelBuilderMCUWidget.cpp` · `Base:` = `view/DashModelBuilderWidgetBase.cpp` · `M:` = `model/DashModelBuilder.cpp` · `MCU:` = `model/DashModelBuilderMCU.cpp` · `PM:` = `viewmodel/DashModelBuilderPresentationModel.cpp` · `CH:` = `model/builder/ModelBuilderConfigHelper.cpp` · `LTH:` = `model/builder/ModelBuilderLabelTableHelper.cpp` · `Main:` = `view/DashMainWindow.cpp` · `Proj:` = `model/DashProject.cpp`. 접두 없는 `:NNN` 은 그 문단에서 직전에 밝힌 파일이며, 6절 표는 셀마다 접두를 붙였다.
> **분리 원칙**: 1\~5절은 코드가 무엇을 하는지만 적고 판정은 6절에 모았다. 본문의 `→ D{n}` · `→ U{n}` 이 6절 ID 다.

## 개요

탭 3면과 로직 클래스 9종이 JSON 2개(`configs/ModelBuilder_{Set}.json` · `{산출루트}/ModelBuilder_{Set}/model_info.json`)와 디스크 폴더 트리를 공동 편집한다. 사용자 입력의 정본은 거의 전부 `QTableWidget` 셀 위젯이고, 학습은 그 셀을 훑어 JSON 을 조립해 외부 실행파일에 넘긴 뒤 JSON·디스크를 되읽어 표에 채운다. **GUI 는 학습 과정을 관측하지 못한다** — 아는 것은 프로세스·데몬 종료 통지, 외부 도구가 JSON 에 써 넣은 `status` 문자열, 디스크에 생긴 이름 셋뿐이며 이 셋의 갱신 시점이 어긋나는 것이 이 모듈 특징적 문제의 뿌리다. 3절은 Sim 기준, MCU 갈림은 4절, 3-8 은 모델 표가 복원되는 두 갈래다.

---

## 1. 탭 3면과 소유 클래스

| 탭 | Sim 화면 | MCU 화면 |
|---|---|---|
| **Data Label** | DataPreprocessor 디렉터리 콤보 + `.xml` 콤보 → [Load] → Input/Output 표 → [Set Dataset] | 파일 표(File Name·Mode·State) + [Add]/[Delete]/[Format] → [Load] → Input/Output 표 → [Set Dataset] |
| **Configuration** | Available Models 표(9열) + 파라미터 스택 + [Start AI Training]/[Stop] | 같은 구조 + Training Results 표(Original/Compressed) + Mode 콤보(Manual/Smart) |
| **Test Results** | Response·Model 콤보 · Case 표 → [Preview] → VTU 분할 렌더 | Response 콤보 · Model **표**(다중 체크) · Case 표(+Smoothing) → [Preview] → 시계열 플롯 |

| 클래스 | 소스 (줄) | 담당 |
|---|---|---|
| `DashModelBuilderWidgetBase` | `Base:` (728) | 공유 슬롯·표 조립·설정 페이지 읽기. 훅 12종(`.h:79-90`)이 쌍둥이 차이를 흡수 |
| `DashModelBuilderWidget` | `W:` (1,442) + ui (339) | Sim 화면 전량 |
| `DashModelBuilderMCUWidget` | `MW:` (1,727) + ui (455) | MCU 화면 전량 — 모듈 단일 최대 파일 |
| `DashModelBuilder` | `M:` (2,113) | Sim 백엔드. 설정 JSON 입출력 · XML 파싱 · 프로세스 실행 · 상태 폴링 |
| `DashModelBuilderMCU` | `MCU:` (1,252) | MCU 백엔드. `DashModelBuilder` 상속 후 7개 지점만 갈아끼움 |
| `DashModelBuilderPresentationModel` | `PM:` (390) | 두 위젯이 공유하는 카탈로그·순수 규칙·파서 |
| `DashSurrogateModelCommon` | `viewmodel/DashSurrogateModelCommon.cpp` (177) | Model Runner·Optimizer 와 공유하는 대리모델 규칙 |
| `ModelBuilderConfigHelper` | `CH:` (114) | `sanitizeString` + Data Label JSON 조립 |
| `ModelBuilderLabelTableHelper` | `LTH:` (350) | shape → reduction 옵션 규칙 · 특수 입력 행 활성화 |

공유 베이스는 `Ui::` 타입을 모르고 위젯 포인터 25개를 **별칭(alias)** 으로만 받는다(`.h:98-122`, 계약은 `.h:25-28` 주석이 정본). MCU 는 그중 `dataPreprocessorDirCombo`·`datasetFileCombo` 2개를 `nullptr` 로 별칭하고 그 둘을 만지는 베이스 슬롯 2종을 빈 구현으로 덮는다(`MW:181-182`·`:556-564`). `.ui` 의 Load·Add 가 `DashSubButton`, Delete·Stop 이 `DashMainButton`(`variant` 3)인 것은 둘 다 `QPushButton` 상속이라 별칭·`connect` 가 그대로 성립하는 표현 계층 교체다. PM 의 지표·모델명 규칙 6종은 본체 없이 `DashSurrogateModelCommon` 에 위임하며(`PM:149-172`·`:207-210`), 그 네임스페이스를 직접 부르는 곳은 PM 뿐이다.

---

## 2. 전체 동선

```
1. 모듈 진입      트리 Set 클릭 → Qt::UserRole+2 불리언 하나로 Sim / MCU 위젯이 갈린다
                  ※ 새 Set 이 MCU 면 이름 끝에 "-MCU"
2. 데이터셋 적재   Sim — DataPreprocessor_* 디렉터리 → .xml → [Load] (XML 2회 순회로 이름·shape)
                  MCU — [Add] 로 행 추가 → .csv/.xlsx → [Load] (첫 파일 헤더로 나머지 검증)
3. Input/Output   shape 차원으로 Input(2D)/Output(3D+) 분배 → ▲▼ 이동 · 체크 · Reduction
                  ※ node_location · connectivity 는 이동·체크 불가 특수 행
4. 모델 행 구성    [Add] → Response·Model 콤보 · Status · 지표 5열
                  Response 의 shape·reduction 이 Model 목록(1D 7종 / ND 1종)과 파라미터 페이지를 정한다
                  ※ 디스크에 학습된 모델이 있으면 행이 자동 복원된다
5. 학습 실행      [Start] → 체크 행 수집 → 기존 status == "Done" 보존 후 병합
                  → Configuration 을 JSON 에 쓰고 그 경로를 외부 도구에 전달
                  ※ Sim 은 1회성 프로세스, MCU 는 상주 데몬 stdin
6. 상태 추적      Sim — 1초 타이머가 설정 JSON 의 status 를 되읽음
                  MCU — 데몬 완료 통지 시 model_info.json 의 models.status 를 1회 반영
                  ※ 두 경로가 읽는 status 의 저장 위치가 다르다
7. 결과 열람      Response → Model → Case → [Preview] — Sim 은 VTU 분할 렌더, MCU 는 시계열 플롯

[산출] configs/ModelBuilder_{Set}.json                  Data Label + Configuration
       {산출루트}/ModelBuilder_{Set}/model_info.json     parameter · errors · model_sizes
       {산출루트}/ModelBuilder_{Set}/{response}/{model}…  .pt · 폴더 · rendered_results
       하류(Model Runner · Optimizer)가 읽는 전부
```

---

## 3. 단계별 대응 — Sim 경로

### 3-1. 모듈 진입

Sim / MCU 갈림은 트리 항목에 심어 둔 불리언 하나로 끝난다.

| 사용자 행위 | 진입 신호 → 함수 체인 | 남는 상태 |
|---|---|---|
| 트리에서 Set 클릭 | `Main:onProjectTreeSelectionChanged:1088` → `handleModelBuilderSelection:1377` → `Qt::UserRole+2`(`:1381`)로 분기 → 이름으로 builder 검색 → `setModel(builder, m_projectPath)` → 스택 전환 | 활성 위젯 · builder 포인터 |
| [+] 로 새 Set 생성 | `Proj:createNewSet:705`(분기 `:761`) → MCU 면 `setName = base + "-MCU"`(`:765`) → `createModuleJsonFile` → `addModelBuilderMCU:338` | JSON 파일 + 트리 항목(`UserRole+2 = true`, `:362`) |
| 프로젝트 재로드 | `Proj:loadSetsFromConfigs:1066`(분기 `:1158`) → `detectBuilderVariant:658` — JSON `variant` 우선, 없으면 이름 접미사 폴백(`:668`) | 위와 동일 |
| 프로젝트 부분 복구 | `Proj:restoreExistingModules:1213`(분기 `:1337`) → 같은 `detectBuilderVariant`(`:1339`), 목록에 없는 Set 만 신설 | 위와 동일 |

**Set 갈림의 근거는 세 벌로 병행 보관된다** — 트리 `Qt::UserRole+2` · JSON `variant` 키 · 이름 `-MCU` 접미사. 읽는 곳마다 기준이 다르다 — `Main:1381`(UserRole+2) · `Main:706-709`(`getModelBuildersMCU()` 목록) · `Main:830`(`displayWidgetForNewSet:820` 의 `variant` 인자) · `Proj:658`(JSON → 접미사 폴백) · `Proj:875`·`:1487`(접미사만). → D1

`registerCategoryWidgets` 의 카테고리→위젯 표에는 **Sim 위젯만 등록돼 있고**(`Main:517`, 항목 `:523`), MCU 위젯은 그 표를 거치지 않고 선택 핸들러가 직접 스택을 전환한다.

`setModel`(`W:72`)의 마지막 줄이 초기화 본체를 촉발한다.

```
setModel(model, projectPath)                          W:72
  ├─ 이전 model 시그널 해제 :75-77 · 시그널 6종 결선 :83-88 · 버튼 4종 결선 :82-115
  └─ model->setProjectDirectory(projectPath)          M:52
        ├─ m_configJsonPath = getConfigFilePath():72
        ├─ projectRootDir 의 *.xml *.npy 스캔 :76-87 · DataPreprocessor_* 하위 *.xml 병합 :89-113
        ├─ emit fileListUpdated():117 · loadLabelMetadata():1146
        └─ loadDataLabelConfig():747 → emit configLoaded() → 위젯 복원 개시
```

스캔 두 덩어리(`M:76-113`, 약 38줄)가 채우는 `m_datasetFiles` 는 **읽는 코드가 없다** — 접근자 `getDatasetFiles()`(`M:123`) 호출처가 0곳이고, 파일 콤보는 `getDataPreprocessorDirectories()`(`M:128`)·`getDatasetFilesInDirectory()`(`M:160`)가 그때그때 다시 스캔해 채운다. `*.npy` 필터도 이 죽은 목록에만 걸린다. → U1

`configLoaded` 수신(`W:334`) 후 복원 순서는 `updateDataPreprocessorDirComboBox:460` → 저장된 datasetPath 부모 폴더명이 `"DataPreprocessor_"` 로 시작하면 콤보 2개 복원(`:351-354`) → `restoreConfigurationUI:371`(JSON → 표) → `refreshAvailableModelsTable:985`(디스크 → 표) → `populateTestResultsResponseComboBox`(`Base:365`) → `onTabChanged:499` 다.

### 3-2. 데이터셋 적재

| 사용자 행위 | 함수 체인 | 결과 |
|---|---|---|
| 디렉터리 콤보 변경 | `onDataPreprocessorDirChanged:480` → `getDatasetFilesInDirectory(dir)` (`*.xml` 만) | 파일 콤보 재구성 |
| **[Load]** | `W:104` 람다가 디렉터리·파일명을 `"dir\|file"` 한 문자열로 합쳐 전달(`:109`) → `M:onLoadButtonClicked:261` 이 `"\|"` 로 재분할해 절대경로 조립(`M:267-297`) | `m_labelTableItems` · `m_datasetPath` |

위젯이 합치고 모델이 쪼개는 **구분자 문자열 계약**이다. → D2

XML 파싱은 같은 파일을 두 번 훑는다 — 1차로 `root/dict` 의 숫자 key `dict_item` 개수를 세어 `dataCount`(샘플 수)를 얻고(`M:318-333`), `file.reset()`(`:336`) 후 2차로 `key="0"` dict 안의 tensor 만 읽는다(`:341-386`). `encoding=="base64"` 면 shape 속성 앞에 `dataCount` 를 삽입하고(`:359-366`), 그 외는 본문 JSON 배열을 재귀로 훑어 shape 을 계산한다(`:368-374`, `calculateShapeFromJsonArrayString:243`). 결과가 `m_labelTableItems += {이름, "[dataCount,…]"}` 이고 `emit labelsUpdated()`(`:395`) 로 끝난다.

shape 는 `"[100,3,8]"` 같은 **문자열**로만 존재하며 이후 차원 판정은 전부 이 문자열의 쉼표 개수를 센다(`LTH:262` `getShapeDimension`). → D3

### 3-3. Input / Output 배치

`labelsUpdated` 수신은 `updateLabelTable`(`Base:486`)이고, 표 2개를 통째로 비우고 다시 만든다.

| 조건 | 배치 |
|---|---|
| 이름이 `node_location` / `connectivity` | Input 표 고정, 체크 불가 (`Base:543-545`) |
| 저장된 Input / Output 목록에 있음 | 해당 표 + 저장 reduction(Output 은 +transformation) 복원 + **체크됨** (`Base:562-565`) |
| 그 외 shape 차원 2 / 3 이상 | Input / Output 표, 미체크 |

**저장된 목록과의 대조에 sanitize 비대칭이 있다** — 저장 키는 `obj[sanitizeString(it.key())]` 로 특수문자가 `_` 로 치환되는데(`CH:34`·`:46`) 읽을 때는 `it.key()` 원문을 쓰고(`M:784`·`:793`), 대조 상대인 `m_labelTableItems` 의 이름은 XML 원문이다. → D4

| 사용자 행위 | 함수 체인 |
|---|---|
| ▲ / ▼ | `W:117`/`W:120` → `moveSelectedLabels`(`Base:585`) — 원본 행을 읽어 새 행을 만들고 원본 삭제, 특수 2행은 건너뜀(`Base:612`) |
| 헤더 체크박스 | `onInputHeaderCheckBoxToggled`(`Base:154`) / `onOutputHeaderCheckBoxToggled`(`Base:168`) — 일괄 토글 후 3상태 재계산 |
| Output Reduction 변경 | `onOutputReductionChanged`(`Base:61`) → `updateSpecialInputsState`(`Base:42`) → Configuration 탭이 열려 있으면 `onTabChanged` 재실행 |

`updateSpecialInputsState` 는 헬퍼 위임만 하고 실제 규칙은 `LTH:272` 다 — Output 의 **유효 차원** 최대값이 3 이상일 때만 특수 2행을 활성화하며, 유효 차원은 `baseDim`, reduction 이 None 이 아니면 `baseDim - 1` 이다(`LTH:336-343`).

**[Set Dataset]** 이 Data Label 탭의 영속화 지점이다.

```
[Set Dataset] → onSetButtonClicked                   W:583
   ├─ m_labelTableItems 비었으면 중단 :587-590 · 콤보 2개로 절대경로 조립 :610-620
   ├─ Input 표 전 행 순회 — reduction 수집 :622-631   ※ 체크 여부를 보지 않는다
   ├─ Output 표 전 행 순회 — reduction + transformation :633-643
   ├─ model->updateAndSaveConfig(path, in, out)      M:681
   │     ├─ saveDataLabelConfig():805 — m_configJsonPath 재계산 :810-817 · 기존 파일 read
   │     │     (다른 섹션 보존) :827-836 · resolveDatasetPath 람다 :842-857
   │     │     (.dproj / ModelBuilder_ 포함 시 프로젝트 루트로 교정)
   │     │     · Input/Output 을 sanitize 된 키로 기록 :860-861 · write + emit :866-873
   │     └─ createModelInfoJson():694  (read-merge-write, 실질 no-op)
   └─ tabWidget->setCurrentIndex(1)                  :647
```

`createModelInfoJson` 은 기존 `model_info.json` 을 읽어 **아무것도 바꾸지 않고 그대로 다시 쓰고**(`M:722-744`) 파일이 없으면 `{}` 를 만든다. 그 존재 자체가 `getModelBuilderFolders:1691` 의 폴더 인식 조건이다.

### 3-4. 모델 행 구성

행 하나가 9열이다 — 0 체크박스 · 1 Response 콤보 · 2 Model 콤보 · 3 Status, 그리고 지표 5열이 ND 면 `R2`·`Mean-MAPE[%]`·`Peak-MAPE[%]`·`Top5% WMAPE[%]`·`WMAPE [%]`, 1D 면 `R2`·`MAPE [%]` + 열 6\~8 숨김이다. 교체는 `updateTableHeadersForModelType(isND)`(`W:1136`, 숨김 `:1147-1149`)가 하고, 지표 이름의 정본은 PM 이 아니라 `DashSurrogateModelCommon` 의 `ndMetricNames`·`oneDMetricNames`·`oneDAltMetricNames` 다(`PM:154-167`).

| 사용자 행위 | 함수 체인 |
|---|---|
| **[Add]** | `onAddModelRowClicked`(`Base:81`) → 플레이스홀더 제거 → `addModelRow`(`Base:220`) |
| **[Delete]** | `onRemoveModelRowClicked`(`Base:93`) → 체크 행마다 `aboutToRemoveModelRow(i)` → `removeRow(i)` |
| Response 콤보 변경 | `onModelResponseChanged`(`Base:106`) → `updateModelComboBox`(`W:864`) → `updateModelError`(`W:912`) |
| Model 콤보 변경 | `onModelSelectionChanged`(`Base:127`) → `updateModelError` → `updateConfigUI`(`Base:257`) |
| 행 선택 이동 | `onModelTableRowChanged`(`Base:148`) → `updateConfigUI(current.row())` |

Response 콤보는 `getOutputResponseList()`(`Base:293`)가 **Output 표에서 체크된 행만** 모아 만들고, 표시 문자열은 훅 `responseDisplayText` 를 거쳐 shape 3D + reduction None 이면 `이름 (Field)`, reduction 이 있으면 `이름 (reduction)`, 그 외는 `이름` 이 된다(`PM:177-184`).

`updateModelComboBox`(`W:864`)는 괄호를 떼어 낸 이름(`PM::stripResponseParen`)으로 **Output 표를 역탐색**해 shape·reduction 을 되찾은 뒤(`W:880-890`) `effectiveModelDimension`(`PM:188`)으로 목록을 정한다 — 유효 차원 3 이면 `StableNet` 1종(`M:225`), 2 면 `Smart`·`MLP`·`Kriging-KBCC`·`RBF`·`SVR`·`RF`·`BNN` 7종(`M:209-211`)이다. 이 함수가 2 또는 3 만 내므로(`PM:194-195`) `getModelsForDimension` 의 세 번째 분기(빈 목록, `M:227`)는 도달하지 않는다. `getNDModelNames()` 는 5종을 반환하지만(`M:213`) 콤보에 실리는 ND 모델은 `StableNet` 하나뿐이다. → U2

현재 목록에 없는 모델명(과거 저장분·디스크 복원분)은 콤보에 넣되 `Qt::UserRole+1 = true` 로 표시하고(`W:901-905`), 그 플래그를 본 `updateModelTableRowStates`(`W:1111`)가 행의 체크박스를 `Qt::NoItemFlags` 로 잠그고 글자를 흐리게 만든다.

설정 페이지는 `createModelConfigUI`(`W:656`)가 시작 시 13개(모델 12종 + Default)를 미리 만들어 `QStackedWidget` 에 넣고 선택에 따라 페이지만 바꾼다. 파라미터 타입 8종(`bool` `int` `double` `combo` `float` `string` `int_range` `float_range`)으로 위젯 종류가 갈린다. **되읽는 경로는 `QFormLayout` 인덱스 순서에 묶여 있다** — `getModelConfiguration`(`Base:305`)이 카탈로그 i 번째 정의와 `layout->itemAt(i, FieldRole)` 를 짝짓고(`Base:318-322`), ND 의 `critical_region_ratio`·`critical_region_weight` 는 **만들되 숨겨서**(`W:714-725`) 화면에 없는 값이 그대로 수집돼 JSON 에 기록된다. → D5

**[Delete] 는 학습 산출물을 실제로 지운다** — 체크 행마다 `aboutToRemoveModelRow`(`W:851`) → `deleteTrainedModel(sanitize(response), model)`(`M:2031`) 이 `.pt` 파일(`:2052-2062`)과 모델 폴더(`:2065-2075`)를 `{model}_*` 까지 재귀 삭제하고 `model_info.json` 의 `errors[response]` 에서 해당 키를 뺀다(`:2086-2100`). 설정 JSON 의 Configuration 섹션은 건드리지 않는다. → D6

### 3-5. 학습 실행

```
[Start AI Training] → onStartTrainingClicked          W:772
   ├─ 체크 행 순회 — {행번호, Response표시, 모델명, 설정값} 수집 :785-798
   ├─ PM::buildTrainingStartPlan(rows)                PM:356
   │     모델명 빈 행 → EmptyModelName 중단 · 중복 → DuplicateModel 중단
   │     options["run"] = true · options["response"] = stripResponseParen(표시문자열)
   ├─ 오류 3종 분기(빈 모델 / 중복 / 선택 0건) :802-819 · 버튼 잠금 전환 :821-822
   └─ model->onTrainingStartButtonClicked("trained_model", plan)   M:398
         1. m_currentJob 있으면 즉시 반환 :404-408  (잠금이 마지막 "Done" 에 풀려 재클릭 가능)
         2. saveDataLabelConfig() :423
         3. 기존 Configuration 읽기 :429-438 — status == "Done" 만 새 섹션에 보존 :444-451  → D6
         4. 이번 옵션 병합 — response 만 sanitize :453-475 (status / error 없으면 빈 문자열)
         5. variant = "Sim", Configuration 기록 후 write :477-487
         6. 첫 모델명으로 1D / ND 판정 :500-510
         7. m_outputDirPath = getModuleDir(ModelBuilder, setName) :521
              model_info.json read-merge-write :523-565
              + 데이터셋 XML 에서 parameter · selected_response 이식 :542-556
         8. 실행파일 해석·존재 확인 :569-580 — DashExt::Path::DeepOpt
              = "extensions/deep_opt/DashOptiDeepOpt.exe" (DashExtensionProcess.h:27)
            인자 train-model-1d | train-model-nd <config.json> --output-dir <출력폴더> :598-606
            status 를 "In Progress" 로 기록 + emit :630-661
            m_statusCheckTimer->start() (1초) :664 · ProcessJob 생성 → start() :668-678
```

**기동을 마지막에 두는 것이 명시적 계약이다**(`M:666-667` 주석). 기동 실패 시 엔진이 그 자리에서 `finished(Failed)` 를 방출하므로, 앞에서 시작하면 실패 번역이 "In Progress" 기록과 타이머 기동을 앞지른다.

### 3-6. 상태 추적

상태를 나르는 통로가 **셋** 있고 셋 다 `modelStatusUpdated` 로 합류한다. 읽는 곳은 셋 다 설정 JSON 의 `Configuration.{model}.status` 다.

| 통로 | 주기 | 함수 |
|---|---|---|
| 1초 폴링 | 실행 중 | `checkModelStatus:1304` → `checkModelStatusInternal:1320` |
| 프로세스 종료 통지 | 종료 시 2회 | `onJobFinished:1238` → 500ms · 1,500ms 지연 재검사(`:1248`·`:1253`) |
| 마감 처리 | 실패 종료 시 1회 (쓰기) | `finalizeStaleStatuses:1416` |

`checkModelStatus` 는 `m_currentJob` 이 없으면 즉시 반환하고(`M:1306-1308`), 판독은 `checkModelStatusInternal` 이 하며 `m_lastKnownStatus` 와 다른 값만 올린다(`M:1366-1375`). 하나라도 `"Done"` 이면 `loadTrainedModelInfo()`(`M:885`)로 지표를 다시 읽는다(`M:1403-1413`). `finalizeStaleStatuses` 는 **실패로 끝났는데 `"In Progress"` 로 남은 항목만** `"Failed"` 로 마감하고 도구가 쓴 `"Done"` 은 걸러낸다(`M:1445-1447`) — 기동 실패는 도구가 뜨지도 못하므로 이 마감이 유일한 종결점이다.

표준출력 처리 규칙은 접두사 하나다(`M:1283`) — `[GUI]` 로 시작하면 접두 6자를 떼고 로그 패널에(`M:1287-1288`), 그 외 stdout 과 stderr 전량은 `m_errorOutput` 에 누적한다(`M:1290`, `onErrorLine:1295`). 실패 시 `m_errorOutput` 이 사용자에게 보이는 유일한 사유이므로(`M:1270-1276`) 의도된 동작이다.

위젯 수신은 `onModelStatusUpdated`(`W:1153`)다 — 모델명으로 행을 찾아 Status 셀·아이콘을 갱신하고, `"Done"` 이면 전 행 지표를 다시 읽으며(`W:1174-1176`), 어느 행도 `"In Progress"` 가 아니면 버튼 잠금을 되돌린다(`W:1181-1190`).

지표 표시(`updateModelError:912`)는 Response 문자열에 `"(Field)"` 가 있으면 ND 로 보아 5종을 그대로 조회하고(`W:924`), 그 외는 `R2`·`MAPE [%]` 조회 후 음수면 `R2`·`CVE [%]` 로 재시도한다(`W:958-960`). 음수는 `"-"` 로 표시하는데 `-1.0` 은 `loadTrainedModelInfo`(`M:965-974`)·`refreshTrainedModelInfo`(`M:1113-1117`)가 NaN·Infinity·null 을 눌러 담은 값이다. `model_info.json` 은 표준 JSON 이 아닐 수 있어 파싱 전에 그 셋을 정규식으로 `null` 치환하고(`M:913-918`), 그래도 실패하면 오류 지점까지 잘라 부분 파싱을 재시도한다(`M:922-935`).

`refreshTrainedModelInfo`(`M:1002`)는 `Smart_0.05` 같은 접미사 키를 알려진 모델 12종 접두로 되돌려(`M:1082-1088`) **같은 base 중 오차가 가장 낮은 항목만 남긴다**(`M:1126-1134`). 대표 오차는 `MAPE [%]`, 없으면 `Mean-MAPE[%]` 다(`M:1090-1094`).

### 3-7. 결과 열람 — Test Results

이 탭은 **ND 모델이 설정에 있을 때만 열린다** — `testResultsTabEnabledState:1408` → `hasNDModelInConfiguration:1413` 이 Response 에 `"(Field)"` 가 있거나 모델명이 ND 5종에 속하는 행을 찾는다.

```
탭 진입 → onTabChanged:499 → populateTestResultsResponseComboBox   Base:365
   └─ getAvailableResponses M:1731 → model_info.json 의 errors 최상위 키 :1777-1780

Response 선택 → onTestResultsResponseChanged:1262
   ├─ populateTestResultsModelComboBox :1222
   │     getTrainedModelFolderNames(M:1922, 디스크 폴더·.pt baseName)
   │     + getTrainedModelFolderErrors(M:1958, model_info.json)
   │     → PM::rankTestResultsFolders PM:220 — ND 폴더만 → 오차 오름차순 → 최저 1개에 " (best)"
   └─ populateTestResultsDatasetTable Base:397
         └─ getTestDatasetFiles M:1862 — {response}/{model}/rendered_results/*.vtu

[Preview] → onTestResultsPreviewClicked               W:1273
   ├─ 라디오 그룹에서 선택 행 판별 :1278-1290 · " (best)" 제거 :1319
   ├─ 정확한 폴더명 우선, 없으면 sanitize 된 이름 + "_" 접두 매칭 :1331-1341
   ├─ vtkXMLUnstructuredGridReader 로 VTU 적재 :1369-1372
   ├─ PointData 에서 Exact_* / Prediction_* 배열 탐색 :1384-1391
   └─ RenderingManager::updateSplitView(grid, exact, pred, true) :1402
```

Exact·Prediction 중 하나라도 없으면 분할 뷰를 띄우지 않고 경고로 끝난다(`W:1401-1405`). 렌더링 매니저 접근은 이 모듈에서 `DashManager::Mgr()` 를 쓰는 **유일한 지점**이다(`W:1350`).

### 3-8. 모델 표의 복원 — 두 갈래

Configuration 탭의 행은 서로 다른 두 소스에서 복원되고, 두 함수는 `onConfigLoaded` 에서 **연달아** 실행된다(`W:360-361`).

| 소스 | 함수 | 대조 방식 |
|---|---|---|
| 설정 JSON `Configuration` | `restoreConfigurationUI:371` | 키 = 모델명. Response 는 `findText(response, Qt::MatchContains)`(`:397`) |
| 디스크 폴더·파일 | `refreshAvailableModelsTable:985` | `(sanitize(Response), 모델명)` 쌍으로 중복 판정(`:1011-1018`) |

앞이 JSON 으로 표를 채우고, 뒤가 현재 Output 라벨에 없는 행을 제거한 다음(`W:998-1008`) 디스크에만 있는 조합을 새 행으로 추가한다(`W:1067-1104`). `restoreConfigurationUI` 는 **sanitize 된 이름으로 표시 문자열을 찾는데** 저장값은 sanitize 를 거치고(`M:461`) 콤보 표시는 원문 기반이다. 반면 `refreshAvailableModelsTable` 은 양쪽을 모두 sanitize 해 비교한다(`W:1006`·`W:1054`). → D7

값 복원은 `restoreConfigurationUI:434-441` 이 담당하며 `getModelConfiguration` 과 마찬가지로 **카탈로그 인덱스 ↔ 폼 레이아웃 인덱스** 짝짓기를 쓴다. → D5

**Output Transformation 은 왕복하지 않는다** — 쓰기 `CH:createOutputLabelsJsonObject:45` 는 `detail["transformation"]` 을 JSON 에 남기지만 읽기 `M:loadDataLabelConfig:798` 이 `{"", detailObj["reduction"]}` 로 값을 버리고, 그 결과 `setupOutputRowTransform`(`W:323`)의 `findData("")` 가 -1 이 되어 콤보가 `None` 으로 되돌아간다. → D8
`transformation` 을 제대로 읽는 파서 `CH:parseDataLabelSection:51` 은 존재하지만 호출처가 0곳이다. → U3

---

## 4. MCU 경로의 갈림

MCU 는 `DashModelBuilder` 를 상속해 **메서드 7개를 재정의**하고 — virtual 5개(`DashModelBuilderMCU.h:26`·`:34`·`:37`·`:40`·`:43`) + 비가상 2개 — 데몬 제어·CSV 검증·학습 후처리를 새로 얹는다. 나머지는 그대로 물려받는다.

| 갈아끼운 것 | 근거 |
|---|---|
| 모델 목록 — 차원과 무관하게 `MLP` 1종 | `getModelsForDimension:59` (virtual) |
| 산출 루트 — `getUserPath()` = 프로젝트 루트 | `onTrainingStartButtonClicked:555-562` |
| 실행 방식 — 상주 데몬 stdin | `sendDaemonCommand:132` |
| 결과 조회 4종 — 산출 루트만 바꿔 재구현 | `getAvailableResponses:772` · `getTrainedModelList:811` · `getTestDatasetFiles:868` · `refreshTrainedModelInfo:739` |
| 학습 시작 · 중단 — 비가상 재정의 | `onTrainingStartButtonClicked:453` · `stopTraining:408` |

베이스의 virtual 중 `getTrainedModelFolderNames`(`DashModelBuilder.h:68`)만 재정의되지 않아, Test Results 의 폴더 열람은 MCU 도 Sim 의 숨김 루트 구현을 그대로 탄다.

### 4-1. 산출물 루트가 다르다

`DashIOController::getModuleDir`(`controller/DashIOController.cpp:24`)은 **ModelBuilder 만 특별 취급**해 `m_internalConfigDir`(숨김 `.dproj`)를 주고(`:31-32`) 그 외 모듈에는 `m_projectRootDir`(사용자 루트)를 준다(`:33-35`). MCU 는 이 함수를 쓰지 않고 `getUserPath()`(= `m_projectRootDir`, `DashIOController.h:97`)에 직접 `ModelBuilder_{Set}` 을 붙인다 — 설정 JSON 은 `{internal}/configs/…` 로 공유하면서 산출 폴더만 Sim 이 `{internal}/ModelBuilder_{Set}/`, MCU 가 `{root}/ModelBuilder_{Set}/` 로 **같은 이름이 두 뿌리에 산다**. → D9

베이스 `getCurrentModelBuilderFolder()`(`Base:52`)가 **폴더 이름만** 돌려주므로 공유가 가능하고, 뿌리를 붙이는 일은 각 경로가 따로 한다.

### 4-2. 데이터셋 적재 — CSV 검증

| 사용자 행위 | 함수 | 결과 |
|---|---|---|
| **[Add]** | `addDatasetFileRow`(`MW:1313`) | 행 추가 — 파일 편집기 + [...] 버튼, Mode 콤보(Train/Test/Pool), State 셀 |
| **[...]** | `browseDatasetFile(row)`(`MW:1391`) | 파일 선택 후 즉시 검증 → State 에 `valid`/`failed` |
| Mode 를 `Pool` 로 | `MW:1344-1353` | **다른 모든 행의 Mode 도 `Pool` 로 강제** |
| **[Format]** | `onDownloadFormatButtonClicked`(`MW:1492`) | 고정 헤더 15개만 담긴 `Data_format.csv` 를 사용자 루트에 생성 |
| **[Load]** | `onLoadButtonClickedMCU`(`MW:1529`) | 전 행 검증 → Input/Output 표를 첫 파일 헤더로 재구성 |

검증 규칙은 `validateDatasetFile`(`MCU:1118`)에 있다 — 확장자가 `.csv`/`.xlsx`/`.xls` 외(`:1141-1144`), 정렬 후 기준 헤더와 **완전 일치**하지 않음(순서 무관, `:1193-1202`), 데이터 구간 빈 줄(`:1209-1212`), 열 개수 불일치(`:1215-1221`), 빈 셀(`:1228-1233`), `toDouble` 실패(`:1235-1242`) 중 하나면 실패다. `transformHeaders = true` 인 두 번째 모드는 **부분집합 검사**로 바뀌지만(`MCU:1181-1191`) Model Builder 경로는 이 인자를 넘기지 않는다. Excel 은 `exportExcelToTempCsv` 로 임시 CSV 를 만들어 검증하고 지우며(`MCU:1086-1092`), Windows 전용 `QAxObject` 구현과 비-Windows 스텁 두 벌이 있다(`MCU:1014`/`:1067`).

기준 헤더의 출처가 상황마다 다르다 — `[...]` 로 첫 파일 지정은 검증 없이 `valid` 기록 후 0행이면 나머지 전체 재검증(`MW:1453-1474`), 두 번째 이후는 경로가 채워진 **첫 행**의 헤더(`MW:1476-1488`), `[Load]` 는 순회 중 처음 읽는 데 성공한 파일(`MW:1574-1588`), 초기 표시는 `PM::mcuFixedDatasetHeaders()` 고정 15개(`PM:128`)다. → D11

**`browseDatasetFile` 의 행 번호는 값 캡처다** — [...] 람다가 생성 시점의 `row` 를 그대로 가둔다(`MW:1331-1333`). → D10

### 4-3. Data Label 저장 — 위젯이 직접 쓴다

Sim 은 모델 계층의 `updateAndSaveConfig` 를 거치지만, MCU 위젯은 **설정 JSON 을 직접 연다**(`MW:697-717`).

```
[Set Dataset] → onSetButtonClicked                   MW:638
   ├─ collectDatasetFileEntries():1361 (편집기 텍스트 + Mode) · 비었으면 중단 :661-664
   ├─ Input / Output 표 — 체크된 행만 수집 :666-679 / :681-694
   ├─ 설정 JSON 을 읽어 rootObj 확보 :698-706
   ├─ rootObj["Data Label"] = PM::mcuDataLabelJson(...)   PM:327
   │     Dataset = [{path, mode}, …] 배열 · Input / Output = 원문 컬럼명 (sanitize 없음)
   └─ write + Configuration 탭으로 전환 :712-719
```

Sim 이 sanitize 하는 자리를 MCU 는 하지 않는다 — **CSV 헤더와 문자 단위로 일치해야 하기 때문**이다(`PM:334-335` 주석). 이 차이가 `Data Label.Dataset` 의 자료형까지 갈라 Sim 은 문자열(절대경로 1개), MCU 는 배열(`{path, mode}` N개)이 된다. → D9

베이스 `loadDataLabelConfig`(`M:773`)는 `dataLabelObj["Dataset"].toString()` 만 하고(`M:780`) 배열에 `toString()` 을 걸면 빈 문자열이므로 **MCU 의 `m_datasetPath` 는 항상 비어 있다.** → D12
배열형 `Dataset` 을 읽을 수 있는 파서(`CH:65-78`)는 그 목적으로 작성돼 있으나 배선되지 않았다. → U3

### 4-4. 데몬 경유 실행

MCU 는 프로세스를 매번 띄우지 않고 `DashManager` 가 소유한 상주 데몬 하나를 쓴다.

| 항목 | 값 |
|---|---|
| 실행파일 | `extensions/DashOptiMCU.exe` (`DashExtensionProcess.h:24`) |
| 소유 | `DashManager::m_mcuDaemon` (`DashManager.cpp:114-115`, 접근자 `.h:228`) |
| 명령 2종 | `train-model-1d "<config>" --output-dir "<out>"` · `test-model-1d\n<payload_json>` (`DashExtensionProcess.h:43-44`) |
| 상관 키 | `commandId` — `"train"` / `"test"` 리터럴 (`DashModelBuilderMCU.h:101-102`) |

위젯은 Set 을 붙이는 순간(`MW:setModel:85`) 데몬을 띄우고 **준비될 때까지 버튼 2개를 잠근다**(`MW:141-167`) — start·preview 를 `"(Preparing engine...)"` 라벨로 비활성화 → `connect(daemonReady, onEngineReady)`(`:160`) → `startDaemon()`(`:162`) → `isDaemonReady()` 면 즉시 1회 더(`:165-167`). `daemonReady` 가 부팅당 1회뿐이라 위젯 재생성이 놓치는 것에 대한 보정이다(`MW:163-164` 주석).

학습 시작 체인은 Sim 과 앞부분이 같고 뒤가 갈린다.

```
[Start AI Training] → onStartTrainingClicked          MW:830
   ├─ 설정 JSON 의 Data Label.Dataset 만 갱신 후 write :866-874 (Input/Output 보존)
   ├─ 체크 행 수집 → PM::buildTrainingStartPlan(rows, Mode) PM:356
   │     MLP 이면 options["mode"] = "Manual" | "Smart"  PM:382-384
   └─ model->onTrainingStartButtonClicked(...)        MCU:453
        ├─ status == "Done" 보존 + 새 옵션 병합 :486-519 (Sim 과 동일)  → D6
        ├─ variant = "MCU" :521 · MLP 이 아니면 즉시 실패 :545-549
        ├─ m_outputDirPath = {userPath}/ModelBuilder_{Set} :555-562
        ├─ model_info.json 의 errors 가지치기 :597-620
        │     Done 인 모델만 보존, 현재 Output 라벨 키는 빈 객체로 신설
        ├─ 데이터셋에서 parameter · selected_response 이식 :623-624
        ├─ status 를 "Running" 으로 기록 + emit :684-715
        └─ sendDaemonCommand(command, "train") :718 · m_statusCheckTimer->start() :721
```

**Sim 은 `"In Progress"`, MCU 는 `"Running"` 을 쓴다.** 상태 아이콘 매핑은 둘 다 처리한다(`view/common/DashWidgetHelpers.cpp:11`). → D9

`m_statusCheckTimer` 를 켜지만 그 슬롯(`M:1304`)은 `m_currentJob` 이 없으면 첫 줄에서 반환하고, MCU 는 `ProcessJob` 을 만들지 않아 그 포인터가 언제나 `nullptr` 이다. → D13

실제 상태 갱신은 데몬 완료 통지 1회다 — `onDaemonCommandCompleted`(`MCU:153`)가 `commandId == "train"` 일 때만 `refreshTrainedModelInfo()`(`:739`, userPath 로 임시 치환 후 베이스 호출) → `updateModelStatusFromOutputDir()`(`:201`, `model_info.json` 의 `root["models"].{model}.status` 를 읽어 emit) → `encodeTrainedHeaders()`(`:269`) 를 밟는다. **status 를 읽는 위치가 Sim 과 다르다**(설정 JSON `Configuration.{model}.status` vs `model_info.json` `models.{model}.status`). → D9

원시 stdout 은 실행 중인 명령을 데몬에 되물어 상관시킨다(`MCU:170-174`) — `test` 중이고 줄이 `{` 로 시작하면 JSON 으로 파싱해 `testModel1DResultReady` 로 올리고(`:182-191`), 그 외 `[GUI]` 줄은 로그 패널로 보낸다(`:194-198`).

### 4-5. 학습 후처리 — 헤더 인코딩

Sim 에 없는 단계다. `encodeTrainedHeaders()`(`MCU:269`)가 `model_info.json` 의 `model_sizes.*.header_file` 을 수집해(`:291-313`) 파일이 없거나 첫 4KB 에 마커 `/* DASHOPT_ENCODED_HEADER v1 */` 가 있으면 건너뛰고(`:304-306`), 나머지를 큐에 담아 `processNextHeaderEncodeJob()`(`:318`)이 `m_headerEncodeRunning` 플래그로 1개씩 직렬 처리한다. 각 작업은 원본 배열 심볼을 정규식으로 뽑아(`:389`) `extensions/encode_header_tool.exe --input <원본> --output <원본>.enc.tmp [--symbol <심볼>]` 를 실행하고(`:341-349`), `onHeaderEncodeFinished`(`:352`)가 성공+출력 있음이면 원본→`.bak`·tmp→원본·`.bak` 삭제(`:362-366`), 실패면 `.bak` 복구 후 tmp 보존(`:368-375`), 성공+출력 없음이면 이미 인코딩된 것으로 본다(`:376-379`). 멱등성 판정이 **파일 내용의 마커**라 GUI 와 도구가 같은 문자열을 각자 정의해 맞춘다(`MCU:253-254` 주석).

완료 상태가 `"Done"` 으로 올라오면 `deleteBaseFolders()`(`MCU:918`)가 모든 response 폴더에서 이름에 `_BASE_` 가 든 하위 폴더를 재귀 삭제한다(`:953-958`). 호출 지점은 `MW:1052` 한 곳이다.

### 4-6. Test Results — 시계열

Sim 이 VTU 를 렌더뷰에 붙이는 자리에서 MCU 는 CSV 를 데몬에 넘겨 플롯 위젯을 만든다.

```
[Preview] → onTestResultsPreviewClicked               MW:1199
   ├─ 라디오 그룹에서 Case 행 판별 :1203-1215 · Smoothing Window Size 읽기 :1220-1221
   ├─ 모델 표에서 체크된 행 전부의 폴더 경로 수집 :1249-1267
   │     첫 번째로 발견되는 rendered_results/{case}.csv 를 테스트 입력으로 고정
   ├─ testModel1DResultReady 를 1회용으로 재연결 :1279-1297
   └─ testModel1D(csv, modelDirs, smoothWindow)      MCU:424
         payload = {test_csv, model_dirs[], smooth_window}
         → sendDaemonCommand("test-model-1d\n{payload}\n", "test")

결과 도착 → 람다 :1281 — DashTimeSeriesPlotter::loadFromJson → DashTimeSeriesWidget 생성·setData
   → emit plotReady(widget) :1296 → Main:493 connect → Main:onPlotReady:3621
```

`plotReady` 위젯은 메인 윈도우가 받아 결과 패널(`m_plotDock`)에 붙인다. Model Builder 에서 렌더뷰·결과 패널로 나가는 경로는 이 시그널과 Sim 의 `updateSplitView` 둘뿐이다. 탭 활성 조건도 갈린다 — Sim 은 ND 모델 유무를 따지지만(`hasNDModelInConfiguration:1413`) MCU 는 베이스 기본값 `true` 를 그대로 써서 **항상 열려 있다**(`Base:702-705`). → D9

### 4-7. Stop 버튼

MCU 위젯은 Stop 을 자기 슬롯이 아니라 **베이스 슬롯**에 연결한다(`MW:119`) — `&DashModelBuilderMCUWidget::onStopTrainingClicked` 라는 이름이 MCU 위젯에 없어 상속된 `Base:onStopTrainingClicked:69` 로 해석된다. 그 슬롯의 `modelBuilder()->stopTraining()`(`Base:75`)은 반환형이 `DashModelBuilder*` 이고 `stopTraining` 이 `virtual` 이 아니라(`DashModelBuilder.h:82`) 정적 디스패치로 베이스 구현(`M:1225`)을 부르는데, 그 안의 `if (m_currentJob)` 이 MCU 에서는 언제나 거짓이라 버튼 상태만 되돌리고 끝난다(`Base:77-78`). `"Running"` 을 `"Interrupted"` 로 바꾸고 데몬을 재기동하는 `MCU:stopTraining:408` 은 호출처가 0곳이다. → D14

MCU 위젯의 `onModelStatusUpdated`(`MW:1022`)는 Sim 과 달리 버튼 잠금을 되돌리지 않고, `trainingSucceeded`·`trainingFailed` 도 연결하지 않는다(`setModel:104-107`). → D15

### 4-8. Sim ↔ MCU 계약 대조

베이스를 공유하면서 갈라진 지점. → D9

| 항목 | Sim | MCU |
|---|---|---|
| status 문자열 | `"In Progress"` | `"Running"` |
| status 저장 위치 | 설정 JSON `Configuration.{model}.status` | `model_info.json` `models.{model}.status` |
| 산출 루트 | 숨김 `.dproj` | 사용자 루트 |
| `Data Label.Dataset` 형 | 문자열 | 배열 |
| Data Label 을 쓰는 계층 | 모델 (`updateAndSaveConfig`) | 위젯 (`onSetButtonClicked` 직접 write) |
| Test Results 탭 활성 조건 | ND 모델 존재 시에만 | 항상 |

---

## 5. 상태 소유 지도

같은 사실이 세 곳에 병행 보관된다. 셋을 갱신하는 함수가 서로 다르고, 셋을 동시에 갱신하는 함수는 없다. → D6

| 저장소 | 위치 | 담고 있는 것 | 쓰는 곳 | 읽는 곳 |
|---|---|---|---|---|
| **A. 설정 JSON** | `configs/ModelBuilder_{Set}.json` | `Data Label`(Dataset·Input·Output) · `Configuration`(파라미터·status·error) · `variant` | `M:saveDataLabelConfig:805` · `M:onTrainingStartButtonClicked:480` · `M:finalizeStaleStatuses:1416` · `MW:712` | `M:loadDataLabelConfig:747` · `M:checkModelStatusInternal:1320` · `M:getModelConfigStatus:2014` · `Proj:detectBuilderVariant:658` · 외부 학습 도구 |
| **B. 모델 정보 JSON** | `{산출루트}/ModelBuilder_{Set}/model_info.json` | `parameter` · `selected_response` · `errors` · `model_sizes` · (MCU) `models.status` | `M:createModelInfoJson:694` · `M:onTrainingStartButtonClicked:558` · `M:deleteTrainedModel:2101` · 외부 학습 도구 | `M:refreshTrainedModelInfo:1002` · `M:getAvailableResponses:1731` · `M:getTrainedModelFolderErrors:1958` · `PM::parseMcuTrainingResults:261` |
| **C. 디스크 트리** | `{산출루트}/ModelBuilder_{Set}/{response}/…` | `.pt` · 모델 폴더 · `rendered_results/` | 외부 학습 도구 · `M:deleteTrainedModel:2052` · `MCU:deleteBaseFolders:918` | `M:getTrainedModelList:1785` · `M:getTrainedModelFolderNames:1922` · `M:getTestDatasetFiles:1862` |

GUI 내부의 병행 보관도 있다.

| 상태 | 1차 보관 | 병행 보관 | 저장 시 읽는 곳 |
|---|---|---|---|
| 모델별 파라미터 값 | 설정 페이지 위젯 | 설정 JSON `Configuration` | **위젯** (`getModelConfiguration:305`) |
| Response 선택 | 모델 표 1열 `QComboBox` | 설정 JSON `Configuration.{model}.response` | **셀 위젯** |
| 라벨 체크·reduction | Input/Output 표 셀 위젯 | 설정 JSON `Data Label` | **셀 위젯** |
| 모델 status | `m_lastKnownStatus` | 표 3열 텍스트 · 설정 JSON | 설정 JSON |
| 학습 지표 | `m_trainedModelErrors` | 표 4\~8열 텍스트 | 저장 안 됨 (읽기 전용) |
| MCU 데이터셋 파일 목록 | 파일 표 셀 위젯 | 설정 JSON `Dataset` 배열 | **셀 위젯** (`collectDatasetFileEntries:1361`) · 되읽는 코드 없음 → D12 |
| MCU Manual/Smart 모드 | `m_modeComboBox` | 설정 JSON `Configuration.MLP.mode` | 콤보 위젯 |

세 위젯 파일에서 `cellWidget(` 은 50회(`W` 29 · `MW` 16 · `Base` 5), `qobject_cast<QComboBox*>` 는 48회(`W` 30 · `MW` 12 · `Base` 6) 나온다 — **모든 사용자 입력의 정본이 테이블 셀 위젯이다.** 한편 `QApplication::processEvents` 는 **0곳**이다(위젯 3종·모델 2종 전량 확인) — 실행이 `ProcessJob`(Sim)과 데몬 명령 큐(MCU)로 전부 비동기라 이벤트 루프를 강제로 돌리는 지점이 없다.

---

## 6. 결함 목록

`D` 는 잘못 구현된 것 15건, `U` 는 구현되지 않은 것 2건 (`U2` 는 예정 기능이라 제외). ID 는 3\~4절 등장 순서이고 분류는 진입·수명 / 데이터 정본 / 구조·결합 / 실행 모델 4종이며, 우선순위 판정은 하지 않는다. 9개 모듈 교차 색인은 [Cross-Module-Defect-Index](Cross-Module-Defect-Index.md).

| ID | 분류 | 결함 | 절 | 근거·귀결 |
|---|---|---|---|---|
| **D1** | 데이터 정본 | Set 갈림의 근거가 세 벌이고 읽는 곳마다 기준이 다르다 | 3-1 | 트리 `UserRole+2` · JSON `variant` · 이름 접미사를 읽는 5곳이 제각각이다(`Main:1381`·`:706-709`·`:830` · `Proj:658`(호출처 `:1163`·`:1339`)·`:875`·`:1487`) → 셋이 어긋나면 같은 Set 이 경로마다 다른 종류로 판정된다 |
| **D2** | 구조·결합 | [Load] 의 위젯↔모델 계약이 구분자 문자열이다 | 3-2 | 위젯이 `"dir\|file"` 로 합치고(`W:109`) 모델이 쪼갠다(`M:267-297`) → 타입이 아니라 문자열 규약이 계약이라 경로에 구분자가 들어가면 조립이 깨진다 |
| **D3** | 데이터 정본 | 차원 판정의 정본이 파싱 결과가 아니라 shape 문자열이다 | 3-2 · 3-3 | 전부 `"[100,3,8]"` 의 쉼표 개수 세기다(`LTH:262`) → Input/Output 분배 · 모델 목록 · 머리글 교체 · 특수 행 활성화가 이 셈 하나에 걸린다 |
| **D4** | 데이터 정본 | 라벨 키의 쓰기·읽기 sanitize 가 비대칭이다 | 3-3 | 저장은 `sanitizeString`(`CH:34`·`:46`), 읽기와 대조 상대는 원문(`M:784`·`:793`) → 공백·`/`·`:` 가 든 라벨은 `contains(name)` 이 실패해 저장된 배치·체크·reduction 을 잃고 차원 기본 규칙으로 떨어진다 |
| **D5** | 구조·결합 | 설정값 왕복이 리스트 인덱스에 묶여 있다 | 3-4 · 3-8 | `Base:318-322`·`W:434-441` 이 카탈로그 i 번째와 `QFormLayout` i 번째 `FieldRole` 을 짝짓는다 → 카탈로그(`PM:20`·`:91`) 순서를 바꾸면 값이 다른 키로 오가고, 숨긴 ND 위젯 2종(`W:714-725`)도 인덱스를 차지한다 |
| **D6** | 데이터 정본 | [Delete] 가 지운 모델이 다음 [Start] 에서 되살아난다 | 3-4 · 3-5 · 5절 | [Delete] 는 B·C 만 지우고(`M:2031`) A 에 `status:"Done"`·`run:true` 를 남기는데 [Start] 가 A 의 Done 항목을 전량 보존해(`M:444-451`) 외부 도구에 넘긴다(`M:477-487`) → 지운 모델이 다시 학습되고 재로드 시 `W:371` 이 행까지 되살린다. MCU 는 `errors` 가지치기로(`MCU:597-613`) A·B 만 맞춘다 |
| **D7** | 데이터 정본 | 저장된 Response 가 복원되지 않는다 | 3-8 | `W:397` 이 sanitize 된 저장값(`M:461`)으로 원문 기반 표시 문자열을 `findText` 한다 → 해당 문자가 든 라벨은 -1 이 돌아와 Response 가 0번 항목으로 남는다. 양쪽을 sanitize 하는 `W:1006`·`:1054` 는 겪지 않는다 |
| **D8** | 데이터 정본 | Output `transformation` 이 왕복하지 않는다 | 3-8 | 쓰기(`CH:45`)는 JSON 에 남기지만 읽기(`M:798`)가 값을 버린다 → `W:323` 의 `findData("")` 가 -1 이 되어 재진입 시 콤보가 항상 `None` 으로 되돌아간다 |
| **D9** | 구조·결합 | 쌍둥이 경로의 계약이 6곳에서 어긋난다 | 4-1 · 4-3 · 4-4 · 4-6 · 4-8 | status 문자열 · status 저장 위치 · 산출 루트 · `Dataset` 형 · Data Label 을 쓰는 계층 · Test Results 활성 조건 → 7개 지점만 갈아끼웠는데 갈린 계약이 6종이고, 그중 `Dataset` 형은 베이스 로더와 정면 충돌한다(→ D12) |
| **D10** | 데이터 정본 | MCU 파일 행의 [...] 가 행 번호를 값 캡처한다 | 4-2 | `MW:1331-1333` 람다가 생성 시점 `row` 를 가둔다 → 중간 행을 지우면 아래 행 캡처값이 실제 위치보다 커진 채 남아 어긋난 행에 경로를 쓴다 |
| **D11** | 데이터 정본 | 헤더 검증의 기준 파일이 조작 순서에 종속된다 | 4-2 | 기준 출처가 넷이다 — 무검증 첫 파일(`MW:1453-1474`) · 경로가 채워진 첫 행(`:1476-1488`) · [Load] 순회 중 처음 성공한 파일(`:1574-1588`) · 고정 15개(`PM:128`) → 같은 파일 집합도 지정 순서에 따라 통과·실패가 갈린다 |
| **D12** | 데이터 정본 | MCU 의 `Dataset` 배열을 베이스 로더가 읽지 못한다 | 4-3 · 5절 | MCU 는 배열로 쓰지만(`PM:327`) 베이스가 `toString()` 만 한다(`M:780`) → `m_datasetPath` 가 항상 비고 연쇄가 셋이다 — `MW:414` 분기가 항상 `else` 로 떨어져 고정 헤더 15개가 저장된 체크를 덮고(`MW:370`), `MCU:623` 의 이식이 건너뛰어져 `model_info.json` 에 `parameter`·`selected_response` 가 없고, 파일 표를 되읽는 코드가 없어 재진입하면 빈 표가 된다 |
| **D13** | 실행 모델 | MCU 가 쓰지 않는 폴링 타이머를 켠 채 둔다 | 4-4 | `MCU:721` 은 실행되지만 슬롯(`M:1304`)이 `m_currentJob` 부재로 즉시 반환하고(`M:1306-1308`) 멈추는 두 지점(`M:1229`·`:1241`)도 MCU 경로에선 안 돈다 → 1Hz 로 계속 돌며 매번 즉시 반환한다 |
| **D14** | 구조·결합 | MCU 의 [Stop] 이 데몬을 멈추지 못한다 | 4-7 | `stopTraining` 이 `virtual` 이 아니고(`DashModelBuilder.h:82`) 호출처가 베이스 포인터 경유(`Base:75`)라 정적 디스패치로 `M:1225` 가 불리고 `m_currentJob` 이 없어 아무 일도 없다. `MCU:408` 의 재정의는 호출처 0곳이고 `MCU:762` 에 그와 모순되는 `// stopTraining is inherited` 주석이 남아 있다 |
| **D15** | 진입·수명 | 학습이 정상 종료해도 MCU 의 Start 버튼이 잠긴 채 남는다 | 4-7 | `MW:1022` 가 Sim(`W:1181-1190`)과 달리 잠금을 되돌리지 않고 `MW:104-107` 이 `trainingSucceeded`·`trainingFailed` 를 연결하지 않는다 → 푸는 경로가 아무것도 멈추지 않는 [Stop](→ D14)과 Set 전환 둘뿐이다 |
| **U1** | 미구현 | 죽은 코드가 세 층에 남아 있다 | 3-1 · 3-4 · 4-3 | 호출처 0곳 — `LTH` 의 표 조립 4종(동명 구현이 `Base` 에 따로 있어 8개 중 실사용 4개) · `Base:populateIoTable:435` · `M:getDatasetFiles:123` 과 그것이 읽는 `m_datasetFiles`(채우는 스캔 38줄 `M:76-113` 이 Set 선택마다 실행) · 옵션 4종(`M:193-207`) · `MW:499-507` 의 빈 중첩 루프. `M:getTrainedModelError:986` 은 헤더에 `Deprecated` 명시 |
| **U2** | 미구현 | ~~ND 모델 5종 중 1종만 콤보에 노출된다~~ | 3-4 | **제외** — 착수 대기 기능 갈래다. `getNDModelNames()` 는 5종을 반환하지만(`M:213`) 콤보에는 `StableNet` 하나만 실린다(`M:225`). 나머지 4종은 카탈로그(`PM:52-85`)·머리글 판정·폴더 인식(`M:217`)에 자리만 잡아 둔 것이고 UI 에 노출되지 않으므로 결함이 아니다 |
| **U3** | 미구현 | Data Label 왕복을 올바로 읽는 파서가 배선되지 않았다 | 3-8 · 4-3 | `CH:parseDataLabelSection:51` 이 `transformation`(→ D8)과 배열형 `Dataset`(→ D12)을 모두 처리하도록 작성됐으나 호출처가 0곳이고 `CH:parseConfigurationSection:105` 도 그렇다 → 깨진 왕복 3종의 읽기 측 구현이 존재한 채 연결만 빠져 있다 |

---
