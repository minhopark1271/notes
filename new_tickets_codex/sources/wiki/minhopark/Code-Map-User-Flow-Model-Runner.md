# Model Runner — 사용자 플로우 ↔ 코드 대응

> **성격**: 독립 참조 문서. 사용자 행위 하나하나가 밟는 함수 체인의 대응표 — 수정 계획·우선순위 판정은 담지 않는다.
> **좌표 기준**: `dev` @ `4c7608e` 실측 (유효기간 있음). 정적 코드 근거만 — 빌드·실행 검증 없음.
> **파일 접두**: `W:`=`view/DashModelRunnerWidget.cpp` · `M:`=`model/DashModelRunner.cpp` · `PM:`=`viewmodel/DashModelRunnerPresentationModel.cpp` · `MW:`=`view/DashModelRunnerMCUWidget.cpp` · `MCU:`=`model/DashModelRunnerMCU.cpp` · `AW:`=`view/DashResultsAnalyzerWidget.cpp` · `Main:`=`view/DashMainWindow.cpp`. 접두 없는 `:NNN` 은 그 문단에서 직전에 밝힌 파일이다.

## 개요

학습이 끝난 대리모델을 골라, 설계변수 값 한 벌로 입력 파일을 만들고, 외부 실행파일에 예측을 시킨다. 구조 특징은 둘 — **실행 방식이 축마다 갈리고**(예측 = 일회성 `DashOptiDeepOpt.exe`, 민감도 = 상주 `DashOptiSensitivityEngine.exe`), **읽는 Set 과 쓰는 Set 이 다르다**(모델 정보는 콤보가 가리키는 `m_viewSourceContext`, 저장은 항상 활성 `m_runtimeContext`). 후자가 `M:` 여러 함수에 같은 삼항 폴백으로 반복된다. 1\~5절은 코드가 하는 일만, 판정은 6절 — 본문 `→ D{n}` · `→ U{n}` 이 링크다.

---

## 1. 화면과 소유 클래스

우측 dock 위젯은 사용자가 아니라 Set 의 `variant` 가 고른다 — Sim = `DashModelRunnerWidget`(`W:` 1,988 + `ui/DashModelRunnerWidget.ui` 222), MCU = `DashModelRunnerMCUWidget`(`MW:` 786 + `ui/DashModelRunnerMCUWidget.ui` 160).

Model Upload 탭은 `uploadSplitter` 로 좌→우 3분할이고 칸마다 표 하나다.

| 표 | 열 | 소유 상태 |
|---|---|---|
| `surrogateTable` | Symbol · Response · Model · R2 · MAPE + ND 전용 4열(기본 숨김) | 체크박스 = 예측 대상 |
| `dvTable` | Parameter · Source · Value · Min · Max | Value 스핀박스 = 설계변수 값의 정본 → D10 |
| `fileTable` | 체크 · File Name · Preview · Delete | 행 = 예측 케이스 1건 |

| 클래스 (줄) | 담당 |
|---|---|
| `DashModelRunner` (`M:` 2,507) | Sim·MCU 공용 모델. 경로 계산 · JSON 입출력 · 예측 프로세스 · 민감도 데몬 |
| `DashModelRunnerPresentationModel` (`PM:` 360) | 검증 5종 · 파일명 규칙 · ND/1D 분류 · DV CSV 왕복 |
| `SurrogateTableController` (`view/common/SurrogateTableController.cpp` 198) | 대리모델 표 행 생성·메트릭 셀 (Model Builder·Optimizer 공용) |
| `DashResultsAnalyzerWidget` (`AW:` 3,697) | `ModelRunner_Sensitivity` 모드로 임베드되는 민감도 패널 |
| `DashModelRunnerMCU` (`MCU:` 142) | 폴더 스캔 · CSV 검증 · 예측을 `DashModelBuilderMCU` 로 위임 |
| `DashExtensionProcess` · `ProcessJob` (`controller/`) | 상주 데몬(인스턴스는 `DashManager` 소유) · 일회성 프로세스 1건 |

`RuntimeContext`(`model/DashModelRunner.h:20-42`)가 경로 계약이며, 필드 7개 전부가 Set 이름 하나에서 파생된다 — `configJsonPath`(`ModelRunner_{Set}.json`, 이 모듈의 유일한 저장처) · `modelBuilderPath` · `modelInfoJsonPath`(대리모델·설계변수의 원천) · `modelRunnerDir` · `modelBuilderFolder` · `configsDir`. 마지막 `configsDir` 만은 Set 무관 전역 경로다 → D7.

---

## 2. 전체 동선

```
1. 모듈 진입   Set 클릭 → variant 판별로 위젯 전환 → 민감도 데몬 기동(즉시 반환)
2. 모델 적재   ModelBuilder 폴더 콤보(model_info.json 있는 것만) → 대리모델 표 재구축
               → 첫 행 자동 체크 → 설계변수 표·Reference 줄 갱신
               ※ QC 상 1~20초 무응답 구간 — 전부 GUI 스레드 동기 실행
3. DV 값       dvTable 스핀박스 직접 입력, 또는 Download → CSV 편집 → Upload 일괄 주입
4. Generate    소스를 Morphing / CAD / ConditionParameter / 미상 4갈래로 판별
               → 파일 1건 + fileTable 행 1건 + JSON Prediction Case 1건
               ※ 이 버튼이 유일한 파일 생성 지점
5. 케이스 편집 행 체크 = 예측 포함 · 행 선택 = DV 역주입 · [X] = 같은 접두사 파일 전량 삭제
6. Run 예측    체크 행을 ND / 1D 로 분류 → 분류마다 JSON 기록 + 프로세스 1건
               ※ 프로세스는 상호 배타 — 두 번째 요청은 거절된다
7. 결과 열람   ND = 결과 VTU 의 Prediction 필드를 렌더뷰에 · 1D = 최신 CSV 를 뷰어로
8. 민감도 탭   ModelBuilder → Response → Trained Model 3단 콤보 → 방법 3종 → [Plot]
               → 데몬 왕복 → 캐시 → 플롯 위젯을 MainWindow 로 승격

[산출] configs/ModelRunner_{Set}.json + ModelRunner_{Set}/ 의 생성·결과 파일
       JSON 의 Model upload 블록만이 외부 실행파일이 읽는 계약이다
```

---

## 3. 단계별 대응

### 3-1. 모듈 진입

| 사용자 행위 | 함수 체인 | 남는 상태 |
|---|---|---|
| Set 클릭 | `Main:handleSubItemSelection:980` → `handleModelRunnerSelection:1427` → `DashProject::detectRunnerVariant:673` → 위젯 선택 → `setModel(runner)` | 현재 위젯 · 모델 포인터 |
| 카테고리 노드 클릭 | `Main:600` 의 `parent().isValid()` false → `hideRightDock()` | 위젯 안 뜸. `m_categoryWidgetMap`(`Main:519-525`)은 읽는 코드 없는 죽은 상태 → D1 |
| 다른 모듈로 이탈 | `Main:776-798` — variant 판별 후 `setModel(nullptr)` | 데몬은 계속 산다 → D4 |

`detectRunnerVariant` 는 JSON `variant` → Set 이름 `-MCU` 접미사 순으로 판정하고, `M:writeConfigFile:540` 은 `m_runtimeContext.setName` 접미사로 매 저장마다 다시 쓴다 → D2.

`W:setModel:79` 이 진입 초기화 본체이며 순서에 의미가 있다.

```
setEnabled(false) → [이전 모델] stopDaemon() + disconnect 전량
  → dataLoaded / referenceFileChanged / setChanged 결선
  → setEnabled(true)        ← 적재보다 먼저 (셀 위젯이 disabled 를 물려받지 않게)
  → setProjectDirectory()   ← 모델 데이터 clear
  → 민감도 패널 결선 + setPlotEnabled(false) → startDaemon() (즉시 반환)
  → isDaemonRunning() 이면 setPlotEnabled(true)   ← daemonReady 유실 보정 → D3
  → singleShot(0) 민감도 초기화 → 콤보·대리모델 표·파일 표 → 예측 결과 결선
```

`daemonReady` 는 데몬 부팅당 1회뿐이라 위젯 재초기화가 놓친다 — 같은 보정이 `MW:110-111`·`:143-145` 에도. `M:stopDaemon:240` 은 `DashManager` 소유 **공용 데몬을 실제로 종료**하므로 Set 전환 1회 = 재기동 1회 + 캐시 폐기(`M:236`) → D4.

### 3-2. 모델 적재

체감 지연 구간. 폴더 스캔·JSON 파싱·표 재구축이 전부 GUI 스레드 직렬이다 → D5.

| 계기 | 함수 체인 |
|---|---|
| (자동) 진입 | `W:populateModelBuilderFolderComboBox:646` → `M:getModelBuilderFolders:1245` — `ModelBuilder_*` 열거 + 각각 `model_info.json` 확인 |
| 콤보 변경 | `W:onModelBuilderFolderChanged:590` → `switchToSet:1403` — `ensureSetConfigExists` → `clearAllTables` → `loadModelInfoFromFolder` |
| (후속) 표 재구축 | `W:populateSurrogateTable:707` — 폴더 재스캔 → `model_info.json` 재파싱 → NaN/Infinity 정화 → `SurrogateTableController::createRow:22` → 헤더 전환 → 첫 행 자동 체크 |

`createRow` 가 체크박스·응답·모델 콤보 3열을 채우고 `updateModelErrorRow:98` 이 메트릭 셀을 채운다 — 조회 실패 시 `m_allTrainedModelErrors` 전 폴더 선형 탐색(`:127-139`). ND 판정 근거는 두 벌 — 헤더 전환은 응답 이름의 `"(Field)"`(`W:830`), 예측 경로 분류는 모델 이름 접두사 5종 화이트리스트(`viewmodel/DashSurrogateModelCommon.cpp:75`) → D6.

`W:onSurrogateCheckBoxChanged:841` 은 체크된 첫 행 폴더를 `selectModelAndUpdateDesignVariables:1422` 로 넘기고, 그 안에서 `m_skipSurrogateTableUpdate` 를 세운 뒤 `loadModelInfoFromFolder` 를 다시 부른다 — 같은 `dataLoaded` 를 재사용하되 수신 슬롯 동작만 플래그로 좁힌다. `W:onModelDataLoaded:329` 는 `m_isPopulating` 이면 무동작(재진입 차단) · `m_skipSurrogateTableUpdate` 면 설계변수 표 + Reference 줄만 · 둘 다 false 면 콤보·대리모델 표·설계변수 표·Reference 줄·파일 표 전부.

`M:loadModelInfoFromFolder:1282` 는 `m_runtimeContext` 를 건드리지 않고 읽기 전용 컨텍스트를 `m_viewSourceContext` 에만 넣는다 — 저장이 항상 활성 Set 을 겨냥하게 하는 장치다. 이 분리가 `getViewSourceConfigsDir()`·`getReferenceFileAndPart:1478`·`resolveParameterSourceLabel:835`·`performMorphing:1950`·`readModelNormalizationFromConfig:2291` 다섯 곳에 같은 삼항 폴백으로 반복되고, `configsDir` 은 `calculateRuntimeContext:444` 가 양쪽에 같은 전역 경로를 넣어 무의미하다 → D7.

`W:updateReferenceFileAndPart:1005` 가 `getReferenceFileAndPart()` 결과로 상단 두 컨트롤을 세운다.

| 소스 | 판별 근거 (`M:1478`) | Reference 줄 · Part 콤보 |
|---|---|---|
| `Morphing` | 파라미터 `source` 가 `GeometryParameter*.json` → 그 안 `DV-Geometry.*.source` 가 `"Morphing\|{deck}\|{part}"` | deck 파일명 · deck 의 Part + NodeSet — **둘 다 활성** |
| `CAD` | 같은 경로에서 `"CAD\|{part}"` | 둘 다 비활성 |
| `ConditionParameter` | 파라미터 `source` 가 `ConditionParameter*.json` → `DV-Condition.*.source` | deck 파일명 · 콤보 비활성 |
| `Unknown` | 위 어느 것도 아님 | 둘 다 비움 |

판정은 `parameter` 순회 중 첫 매치에서 `break` 한다 → D8. `Source` 열 라벨(`Morphing`/`CAD`/`FE Cond`)은 `M:resolveParameterSourceLabel:835` 가 같은 JSON 을 다시 열어 병행 판정하며 실패 3경로가 전부 `"FE Cond"` 다 → D9.

### 3-3. 설계변수 값 확정

값의 정본은 `dvTable` 2열 `QDoubleSpinBox` 다. `m_designVariables[i].value` 는 병행 보관일 뿐이고 읽는 시점마다 `W:collectSurrogateSelection:1650` 이 표에서 폴링한다 → D10.

| 사용자 행위 | 함수 체인 · 결과 |
|---|---|
| Value 스핀박스 입력 | 시그널 결선 없음 — 즉시 반영되는 곳 없음 |
| [Download] | `W:onDvDownloadButtonClicked:1869` → `collectDvRows:1706` → `PM:dvCsvDownloadBody:80` → `dv_values_{yyyyMMdd_HHmmss}.csv` (헤더 `Parameter,Value,Min,Max`) |
| [Upload] | `W:onDvUploadButtonClicked:1901` → `PM:validateDvCsvUpload:91` → 스핀박스 일괄 `setValue`. 거부 6조건(헤더 4열 · 행 수 · 열 수 · 이름 불일치 · 숫자 파싱 · Min/Max 또는 범위) 통과 시에만 |

CSV 는 표 순서와 인덱스로 대응하므로 재정렬한 파일은 이름 불일치로 거부된다. `W:populateDesignVariableTable:916` 은 스핀박스 상한을 `info.max - 0.0001` 로 깎으면서 Max 열엔 원래 값을 보이고, 초기값은 `info.value != 0.0` 일 때만 저장값을 쓴다 → D11.

### 3-4. Generate Input File

버튼 하나가 파일 생성·행 추가·JSON 기록을 한 번에 한다. 4갈래 공통 선행은 둘이다.

```
[Generate Input File] → W:onGenerateInputFileClicked:353
   ├─ PM:validateBaseParams:192   응답(:292) · 모델(:332) · DV 표(:344)
   ├─ M:saveInputDesignVariableValues:1201   ← JSON 을 즉시 쓰는 유일한 지점
   └─ getReferenceFileAndPart() → sourceType 4분기
```

**A.1 Morphing** (`W:390-402` → `performMorphingAndAddToFileTable:1517`) — `mkpath` → `m_predictionCount++` → `PM:predictBaseName:20`(`Predict_%02d_{resp}_{model}`) → `M:performMorphing:1950` → fileTable 행 추가(경로 = `.vtu` 절대경로) → 정규화 보정 → `appendPredictionCaseToJson`. 시작·종료에 `Main:startGenerateStatusAnimation:3549`·`:3554`. `performMorphing` 은 모듈 최장 함수(282줄)이고 다른 모듈의 전역 상태에 손을 댄다.

```
AnalysisModelContextRegistry::getOrLoad(dat)
  → model_info.json 재파싱 → GeometryParameter JSON 탐색 → actualPartName 재추출
  → {같은이름}.vtp 확인 → DashMorphingUtils::createSampleFromDesignVariables:197
  → createMorphOperator:187 (Wendland C2 · MT_DIRECT · 16 threads, kernelRadius 기본 10.0)
  → DashManager::GetHandlePickingInteraction():269   ← 싱글턴 공용 객체
  → loadHandlesFromVtp:39 → SetBoxHandles (DashHandlePickingInteraction.cpp:2562)
  → performMorphingAndExport:267 → VTU + deck 동시 생성
  → extractPartVtuFromDat / extractComponentVtuFromDat → {base}_input_geometry.vtu
```

특징 3종 — **Part 콤보는 모핑 대상을 정하지 않는다**(모핑은 JSON 재추출 `actualPartName`, 사용자의 `targetPart` 는 마지막 `_input_geometry.vtu` 추출 전용) → D12 · **핸들 객체가 Morphing 모듈과 공용**(`SetBoxHandles` 가 싱글턴 `m_handleGeometry` 를 제자리 교체) → D13 · **핸들 적재 실패가 조용히 통과**(렌더러 없으면 데이터 채우기 전 반환 `:2570-2578`, `loadHandlesFromVtp` 최종 가드는 "비어 있지 않은가" 하나) → D14. NodeSet 여부는 콤보 아이템 `Qt::UserRole` 로만 판정하는데 값을 세우는 곳이 `W:loadSetsIntoPartCombo:1965` 뿐이라 텍스트만 세우는 경로(`updateReferenceFileAndPart` 의 `setCurrentText`)에서는 비어 있다 → D20.

**A.2 CAD** (`W:405-455` → `onCadFileReadyForFileTable:521`) — 유일한 비동기 분기로 요청과 완료가 다른 함수에 있다.

```
solverNxCad 확인 → {componentName}.prt 확인 → PM:buildCadConfigJson:14
  → m_predictionCount++ → stpPath 결정 + 기존 파일 삭제
  → m_pendingCadStpPath / m_pendingCadParams 보관 → Main:startNxCadStatusAnimation:3539
  → DashSolverNxCad::enqueueUpdatePrtGeometry:148        (여기서 함수 종료)
  ⋮ 데몬 왕복
  → onCadFileReadyForFileTable: 경로 불일치면 무시 → refreshFileTableFromDisk()
    → 재구축된 표에서 경로 일치 행 선형 탐색 → DV 값 기록 + appendPredictionCaseToJson
```

요청과 완료를 잇는 것은 문자열 1개다. 완료 신호도 `DashSolverNxCad::onCommandCompleted:187` 이 `m_batchMode` 로 `updatePrtGeometryBatchCompleted`(`:203`)·`updatePrtGeometryCompleted`(`:205`) 중 하나를 고르는데 Model Runner 는 후자만 구독한다 → D15. 대기 상태는 완료 슬롯 진입 직후에만 지워져 실패 경로에서는 남고 → D16, 완료 처리가 표를 통째로 재구축하므로 그 사이의 체크 상태와 `m_fileTableDvValues` 가 사라진다 → D17.

**B. ConditionParameter** (`W:458-517`) — ND 면 즉시 거부, 아니면 템플릿(`configsDir/{inputFileName}`)을 `M:generateDatFile:1574` 로 치환해 `modelRunnerDir/Predict_NN_*.{ext}` 를 만들고 디스크 재스캔으로 행을 찾아 JSON 을 쓴다. 치환은 `"${이름}"` 텍스트 전역 치환 · `QMap` 사전순 순회 · `QString::number` 기본 정밀도(유효숫자 6자리) → D18.

**미상** (`W:519-529`) — ND 는 거부, 1D 는 경고 후 `addDvOnlyRowToFileTable:1478` 로 파일 없는 행을 만든다. 이름에 `" (DV only)"` 가 붙고 Preview 가 비활성화되며, 대응 파일이 없어 재진입에서 사라진다(3-9).

**공통 후처리 — DV 부호 보정** — 세 경로 모두 `M:readModelNormalizationFromConfig:2291` → `computeInferenceDvValues:2389` 를 거친다. 전자는 `modelBuilderPath/{response}/{model}_*/config.yaml` 을 YAML 라이브러리 없이 상태 5개짜리 수동 스캐너로 읽고, 후자는 파라미터별 `(min+max)/2` 부호를 UI 쪽과 config 쪽에서 비교해 반대이면 음수화하고 `logMessage` 로 통지한다. 파싱 무효면 값이 보정 없이 통과하며 경고는 Morphing 경로에만 있다 → D19.

### 3-5. 예측 케이스 편집

`fileTable` 행 1건 = 예측 케이스 1건. 행이 보유하는 것은 표시 이름과 `Qt::UserRole` 의 파일 경로, 위젯 밖 `m_fileTableDvValues` 의 DV 값 한 벌이다.

| 사용자 행위 | 함수 체인 · 결과 |
|---|---|
| 행 선택 | `W:onFileTableRowSelected:1055` — `m_fileTableDvValues[row]` 를 dvTable 로 역주입. 맵에 없는 행은 무동작 |
| 체크 토글 | `W:1830` 람다 → `syncFileTableToJson:998` — 빈 본문이라 체크 상태는 실행 시점까지 메모리에만 → U1 |
| [Preview] | `W:1795` 람다 → `onFilePreviewClicked:1208` → `performPreviewLogic:1247` (3-7) |
| [X] | `W:1803` 람다 — JSON 케이스 삭제 → `PM:relatedFilePathsForDeletion:40` 로 같은 접두사 파일 전량 삭제 → 행 제거 → 맵 인덱스 재정렬 |

삭제 범위는 `completeBaseName()` 접두사의 같은 폴더 파일 전량이다. `%02d` 덕에 `Predict_01`\~`Predict_09` 는 안전하고 `Predict_1` 이 `Predict_1x` 를 잡는 것은 10번대부터다 → D21. 행 인덱스 취득도 갈린다 — `[X]` 는 `indexAt(버튼 중심).row()` 재계산, `[Preview]` 는 캡처된 `row` → D22. 체크 행 일괄 삭제 `W:onDeleteButtonClicked:550` 은 connect 0건 → U2.

### 3-6. Run AI Prediction

```
W:onRunAIPredictionClicked:1077
   ├─ 체크된 대리모델 0개면 거부 → PM:validatePredictParams:248
   ├─ collectPredictionCases:1608   active && file 있는 것만
   ├─ PM:groupCheckedPairs:56       → ndPairs / d1Pairs
   ├─ M:updatePredictionCasesActiveStates:2463
   ├─ 추적 상태 세팅 (.stp/.step 이면 {base}_input_geometry.vtu 로 미리 치환)
   └─ ndPairs / d1Pairs → M:updateModelUploadConfig:1096 → runNDPrediction:1641 / run1DPrediction:1717
```

다섯 가지가 갈린다.

1. `params.fileTableFiles` 는 채워지지만 소비되지 않는다 — `collectPredictionCases()` 와 필터가 다르고(전자 `dat`/`inp`/`vtu`, 후자 `.stp` 포함), 유일한 소비 함수 `W:syncAnalysisInputFilesToJson:1721` 은 호출처 0곳 → U3.
2. ND·1D 가 둘 다면 프로세스 2건이 연달아 요청되고 두 번째는 거절된다 — `M:startPredictionJob:177` 이 `m_currentJob` 하나로 배타를 판정하는데 호출부 3곳이 반환값을 안 본다 → D23.
3. 두 번째 `updateModelUploadConfig` 가 같은 JSON 키를 read-merge-write 하며 첫 번째의 `Output Response` 를 덮는다 → D24.
4. `m_lastPreviewedVtuPath` 는 루프 끝에서 한 번 세워져 마지막 케이스만 가리킨다 → D25.
5. `updateModelUploadConfig` 가 `model_info.json` 을 재파싱해 `m_designVariables` 를 교체하고 그 `meta.default` 를 `Input Design Variables.value` 로 쓴다 → D26.

프로세스 인자(`DashExt::Path::DeepOpt`)는 `M:runNDPrediction:1641` = `test-model-nd {configJson} {modelRunnerDir}` · `M:run1DPrediction:1717` = `test-model-1d {configJson} {modelRunnerDir}` · `M:onPredictButtonClicked:881` = `test-model-1d {configJson}`(호출처 0곳, 구버전 형태 → U4).

`ProcessJob` 결선은 stderr 를 분리하되 구독하지 않는다(도구가 진행 표시를 stderr 로 낸다). stdout 은 `M:onOutputLine:1188` 이 받아 `[GUI]` 접두사 줄만 승격하고 나머지는 버퍼에 쌓았다가 실패 시 전문을 `predictionFailed` 에 싣는다(`onJobFinished:1169`).

### 3-7. 결과 열람

성공 통지 하나가 모델 종류에 따라 갈린다(`W:onPredictionSucceeded:1154`).

**1D** — `QTimer::singleShot(500ms)` 뒤 ModelRunner 폴더 `*.csv` 중 `lastModified` 최대 파일을 골라 `m_lastCsvModTime` 보다 새로우면 `Main:OpenCsvViewer:2782` 로 연다. 500ms 는 고정 상수 → D27.

**ND** — `W:performPreviewLogic:1247` 로 넘긴다.

```
파일 없으면 경고 → .stp/.step 이면 동명 _input_geometry.vtu 로 재귀, 없으면 Main:previewStepFile:2391
  → .vtu 아니면 동명 .vtu 로 리다이렉트 (표는 .dat/.inp 경로를 들고 있으므로)
  → 분할 뷰 해제 + clearAllLayers() → 본 VTU 로드 → Prediction 필드 탐색 3단
       본 VTU 에               → updateFieldOutput
       {base}_input_geometry.vtu 에 → 전부 VTK_VERTEX 이면 KdTree 최근접 사상
                                 (mapPointCloudToMesh:1222, 보간 없음), 아니면 본 메시 렌더 + 그 격자로 출력
       없으면                   → updateComponentGeometry (필드 없음)
```

`checkFieldExistsInVtu:1341` 이 존재 확인만을 위해 VTU 를 다시 읽어 최악의 경우 같은 파일이 3회 파싱된다 → D5. `DashMainWindow` 부모 거슬러 올라가기는 이 파일에 4벌(`W:371` 람다·`:1185`·`:1264`·`:1335`) → D28.

### 3-8. Sensitivity Analysis 탭

두 축은 실행 방식·대상 선택·Set 해석이 모두 갈린다 — 예측 = `ProcessJob` 일회성 · `surrogateTable` 체크 + 폴더 콤보 · 읽기는 view source 쓰기는 active. 민감도 = `DashExtensionProcess` 상주 데몬 · 패널 자체의 3단 콤보 · `m_setName` 문자열 1개.

```
AW:initializeTargetData:370  (ModelRunner_Sensitivity 분기, 100ms 중복 호출 억제)
  ├─ ModelBuilder_* 전량 열거 → ModelBuilderCombo (Set 필터 없음 → D30)
  ├─ "ModelBuilder_{m_setName}" 을 찾아 선택, 없으면 0번
  └─ updateModelRunnerSecondaryCombo:1233
       ├─ 선택 폴더의 하위 디렉터리 → ResponseFolderCombo
       ├─ model_info.json 의 Model upload.Input Design Variables.label → 플롯 변수 → D29
       └─ updateModelRunnerTrainedModelCombo:1304   MCU 판정으로 확장자 결정 (.h / .pt)

[Plot] → AW:onPlotButtonClicked:1723 → processModelRunnerPlot:2897
           Sobol Indices→"sobol" · Morris Method→"morris" · SHAP→"shap"
           model_path = TrainedModelCombo currentData · model_config = {폴더}/model_info.json
   → W:onSensitivityPlotRequested:1046 → M:requestPlot:929
        setName 검사 → 명령 3종 화이트리스트 → inputJson·displaySettings 조립
        → buildCacheKey:294 조회 (적중 시 데몬 없이 processCachedResult:305)
        → sendSensitivityCommand:322 → daemon->sendCommand("{command}\n{compact json}")
   ⋮ 데몬 왕복
   → M:onSensitivityCommandCompleted:272 → processDaemonResponse:341
        m_pendingCommand 비었으면 무시 (공용 데몬 브로드캐스트 방어) → [FINISHED] 절취
        → 첫 '{' 이전 절단 + NaN/Infinity 치환 → 파싱/error 실패는 logMessage 만
        → 캐시 삽입(10건 초과 시 전량 폐기) → emit plotSpecReady
   → AW:onPlotSpecReady:3166 → DashPlotRequestHandler::build() → ZoomableScrollArea
        → emit analysisResultReady → DashMainWindow::onPlotReady
```

캐시 키는 `command` + `model_path` + `model_config`(+SHAP 은 `dataset_path`)뿐 — 표시 설정 제외는 의도된 동작이고, 비우는 곳은 `startDaemon`(`M:236`)과 `setSetName`(`M:649`) 둘뿐이다 → D31. 실패 처리는 두 갈래 — `commandFailed`(`M:284`)만 `daemonError` 로 승격돼 Plot 버튼을 되돌리고, `processDaemonResponse` 안의 실패 4경로는 `m_pendingCommand` 를 남긴다 → D32.

### 3-9. 재진입과 복원

`ModelRunner_{Set}.json` 4블록 중 화면으로 되돌아오는 것은 `variant` 뿐 — 설정 JSON 은 사실상 쓰기 전용이고 복원은 전적으로 디스크 스캔에 의존한다 → D33.

| 블록 | 쓰는 곳 | 화면에 되돌리는 곳 |
|---|---|---|
| `variant` | `M:writeConfigFile:540` (매 저장) | `DashProject::detectRunnerVariant:673` — 위젯 선택에만 |
| `Model upload.Output Response[]` | `M:updateModelUploadConfig:982`·`:1096` | 없음 |
| `Model upload.Input Design Variables` | `M:saveInputDesignVariableValues:1201` · `updateModelUploadConfig` | 없음 — 화면은 `model_info.json` 의 `meta` 를 쓴다 |
| `Model upload.Prediction Cases[]` | `M:appendPredictionCaseToJson:2439`·`:2463`·`:2489` | 없음 |

복원되는 것은 파일 표 행뿐이다 — `ModelRunner_{Set}/` 의 `*.dat` `*.inp` `*.stp` `*.step` 를 `W:populateFileTable:957` 이 파일명으로 되살린다. 나머지는 소실이다 — 행별 DV 값·행 체크 상태·DV-only 행(`populateFileTable` 이 맵을 비우고 복원 행은 항상 `isChecked=false`) → D33 · `m_predictionCount`(생성자에서 0 → 재진입 후 `Predict_01` 이 기존 파일과 충돌) → D34 · 선택 모델·응답·DV 입력값(항상 첫 행 자동 체크, DV 는 `meta.default`). Morphing 행은 생성 시 `.vtu` 스캔 시 `.dat`/`.inp` 로 같은 케이스가 다른 확장자로 복원된다 → D35. 행별 DV 값이 소실되므로 재진입 후 실행하면 `collectPredictionCases` 의 폴백이 걸려 모든 행이 현재 dvTable 값 한 벌을 공유한다.

Set 전환은 `W:switchToSet:1403` → `ensureSetConfigExists` → `clearAllTables:1381` → `loadModelInfoFromFolder` 순이고, `clearAllTables` 는 표 3종·맵 3종만 비워 `m_predictionCount`·`m_pendingCadStpPath`·`m_pendingCadParams` 를 남긴다 → D36. `onSurrogateCheckBoxChanged` 의 "체크 행 Set ≠ 현재 Set 이면 파일 표 비움" 방어는 `currentSetName.isEmpty()` 예외가 붙어 초기 진입에서 돌지 않는다.

---

## 4. MCU 경로의 갈림

같은 `DashModelRunner` 모델을 쓰지만 위젯이 갈린 뒤로는 로직을 거의 공유하지 않는다.

| 항목 | Sim 경로 | MCU 경로 |
|---|---|---|
| 폴더 스캔 기준 | 프로젝트 경로 | **사용자 경로** (`MCU:getMcuModelBuilderFolders:35`) |
| 폴더 필터 | `ModelBuilder_*` + `model_info.json` | 위 + 이름이 `-MCU`/`MCU` 로 끝날 것 |
| 대리모델 표 | 선택된 폴더 1개 | **폴더 전량 병합** (`MW:populateSurrogateTable:390`) |
| 입력 | 설계변수 스핀박스 + 생성 파일 | 사용자가 고른 CSV + smoothing window |
| 입력 검증 | 없음 (생성 시점에 결정) | 행 추가·모델 변경마다 헤더 대조 (`MW:validateAllInputFiles:505`) |
| 실행 | `ProcessJob` 일회성 (`DashOptiDeepOpt.exe`) | 상주 데몬 (`DashOptiMCU.exe`, `DashModelBuilderMCU` 경유) |
| 결과 | 렌더뷰 필드 / CSV 뷰어 | `DashTimeSeriesWidget` 창 (`MW:onPredictionResultReady:726`) |
| 민감도 방법 | Sobol · Morris · SHAP | SHAP 제거 (`AW:setModelBuilderBasePath:543`) |
| 민감도 모델 확장자 | `*.pt` | `*.h` |
| 민감도 Set 이름 | `getSetName()` | `getSetName() + "-MCU"` (`MW:163`) → D37 |

민감도 축은 두 경로가 `M:requestPlot` 을 공용하고 예측 축만 갈린다. MCU 위젯은 민감도 데몬과 MCU 데몬을 둘 다 기동한다(`MW:140-141`). Model Runner 관련 4파일에 `DASH_BUILD_*` 조건부 컴파일이 0건이므로 이 모듈은 전 타깃에서 같은 코드로 노출된다.

---

## 5. 상태 소유 지도

| 상태 | 1차 보관 | 병행 보관 | 실제로 읽히는 곳 |
|---|---|---|---|
| 설계변수 값 | `dvTable` 2열 스핀박스 | `m_designVariables[i].value` · JSON | **셀 위젯** |
| 행별 DV 값 | `m_fileTableDvValues` | JSON `Prediction Cases[].values` | 위젯 멤버 (세션 내) |
| 행 체크 상태 | 0열 `QCheckBox` | JSON `.active` | 셀 위젯 |
| 파일 경로 | 1열 `Qt::UserRole` | 디스크 · JSON `file` | `Qt::UserRole` |
| 선택 응답·모델 | `surrogateTable` 1열 + 2열 콤보 | JSON `Output Response[]` | 표 위젯 |
| 모델 출처 폴더 | 1열 `Qt::UserRole` | `m_surrogateTableFolderMap` | 양쪽 (`W:onModelChanged:885` 이 둘 다 갱신) |
| 활성 / 조회 대상 Set | `m_runtimeContext` / `m_viewSourceContext` | `AW:m_setName` · 콤보 텍스트 | 각자, 삼항 폴백 5곳 |
| Reference deck 경로 | `m_datFilePath` (browse 로만) | 라인에디트 텍스트 · JSON `"Morphing\|…"` | `m_datFilePath` 우선, 비면 `configsDir/텍스트` |
| MCU 여부 | Set 이름의 `-MCU` | JSON `variant` | 이름(저장 시) · JSON(판별 시) |
| 예측 카운터 / 민감도 캐시 | `m_predictionCount` / `m_resultCache`(최대 10) | — | 세션 내 / 키 3\~4필드 |

신호 수신처 — `dataLoaded` 는 위젯 2종, `predictionSucceeded`·`predictionFailed` 는 Sim 위젯, `plotSpecReady`·`logMessage`·`daemonReady`·`daemonError`·`setChanged`·`referenceFileChanged` 는 각 1곳. `designVariablesChanged`·`surrogateModelsChanged`·`fileTableUpdated`·`surrogateModelUpdated` 는 0곳이다 → U5.

뷰 계층 결합 지표(`W:` 한 파일) — `cellWidget(` 13 · `getSetName()` 11 · `QMessageBox::` 15 · `Qt::UserRole` 10 · `findChild<` 5 · `DashManager::Mgr()` 4 · `DashMainWindow` 부모 거슬러 올라가기 4벌 · `processEvents` 0 · `QThread` 0. `M:` 에도 `QMessageBox::` 가 4회 있으며 전부 미호출 함수 `runFESolver` 안이다 → U6.

---

## 6. 결함 목록

`D` 는 잘못 구현된 것 37건(D1 은 철회, ID 는 재번호하지 않는다), `U` 는 구현되지 않은 것 6건 — 6건 다 예정 기능 갈래가 아니라 죽은 코드·빈 본문이다. 분류는 진입·수명 / 데이터 정본 / 구조·결합 / 실행 모델 4종이며 우선순위 판정은 하지 않는다. 9개 모듈 교차 색인은 [[Cross-Module-Defect-Index]].

| ID | 분류 | 결함 | 절 | 근거·귀결 |
|---|---|---|---|---|
| **D1** | — | ~~카테고리 노드 클릭이 `variant` 를 무시한다~~ **철회** | 3-1 | `m_categoryWidgetMap`(`Main:519-525`)은 읽는 코드가 없고 카테고리 클릭은 `Main:600` 에서 `hideRightDock()` 으로 끝난다 — 남은 사실은 죽은 상태 1개 |
| **D2** | 데이터 정본 | `variant` 가 JSON 키와 Set 이름 접미사에 이중 보관 | 3-1·3-9 | 읽기는 JSON→이름 순, 쓰기(`writeConfigFile:540`)는 이름 접미사로 매 저장 갱신 → 어긋나면 이름이 덮는다 |
| **D3** | 구조·결합 | `daemonReady` 유실 보정이 3벌 중복 | 3-1 | 부팅당 1회 신호를 위젯 재초기화가 놓쳐 상태를 재조회(`W:184`·`MW:110-111`·`:143-145`) → 폴링이 실효 경로 |
| **D4** | 진입·수명 | 공용 데몬 수명이 Set 전환에 묶이고 모듈 이탈엔 안 묶인다 | 3-1 | `setModel` 이 이전 `stopDaemon()` + 새 `startDaemon()` → 전환 1회 = 재기동 + 캐시 폐기. 이탈(`Main:776-798`)엔 남는다 |
| **D5** | 실행 모델 | 적재·열람이 전부 GUI 스레드 동기이고 같은 파일을 계층마다 다시 읽는다 | 3-2·3-7 | Set 선택 1회 = 폴더 열거 2회 + `model_info.json` 최소 3회 + DV 수만큼 GeometryParameter JSON + 메트릭 셀마다 폴더 선형 탐색 + deck 파싱, 열람은 같은 VTU 최대 3회. `QThread`·`processEvents` 0곳 → 프리즈 구간에 진행 표시 없음 |
| **D6** | 데이터 정본 | ND 판정 근거가 두 벌 | 3-2 | 헤더 전환은 응답 이름 `"(Field)"`, 예측 분류는 모델 이름 접두사 5종 → 한쪽만 ND 인 조합에서 보이는 열과 타는 경로가 어긋난다 |
| **D7** | 구조·결합 | `configsDir` 의 컨텍스트 분리가 무의미 | 3-2·1절 | `calculateRuntimeContext:444` 가 양쪽에 Set 무관 전역 경로를 넣어 삼항이 항상 같은 값 |
| **D8** | 데이터 정본 | 소스 종류 판정이 첫 매치에서 끊긴다 | 3-2 | `getReferenceFileAndPart:1478` 의 `break` → 소스를 섞은 Set 은 딕셔너리 키 순서가 소스 종류와 컨트롤 활성 여부를 정한다 |
| **D9** | 데이터 정본 | `Source` 열 라벨이 병행 판정이고 실패가 한 값으로 떨어진다 | 3-2 | `resolveParameterSourceLabel:835` 의 실패 3경로가 전부 `"FE Cond"` → 판정 실패와 실제 ConditionParameter 가 구분되지 않는다 |
| **D10** | 데이터 정본 | 설계변수 값의 정본이 모델이 아니라 셀 위젯 | 3-3·3-6 | 스핀박스에 시그널 결선이 없고 필요할 때 폴링 → 모델만 바꾸는 경로(D26)가 저장값과 어긋난다 |
| **D11** | 데이터 정본 | 스핀박스 범위 세팅이 표시값과 미설정 판정을 왜곡 | 3-3 | 상한 `max - 0.0001` 인데 Max 열은 원래 값 → 표시된 상한을 입력할 수 없다. `value != 0.0` 조건 → 정확히 `0.0` 인 DV 는 매 진입마다 중앙값 |
| **D12** | 구조·결합 | Part 콤보가 모핑 대상이 아니라 렌더 대상을 고른다 | 3-4 | 모핑은 재추출한 `actualPartName`, `targetPart` 는 `_input_geometry.vtu` 추출 전용 → 라벨과 효과가 어긋난다 |
| **D13** | 구조·결합 | Generate 가 Geometry Parameterization 의 공용 핸들 인스턴스를 덮는다 | 3-4 | `GetHandlePickingInteraction():269` 는 싱글턴 1개, `SetBoxHandles` 가 `m_handleGeometry` 를 제자리 교체 → Generate 1회가 Morphing 탭 편집 중인 핸들 배열을 갈아끼운다 |
| **D14** | 실행 모델 | 핸들 적재 실패가 조용히 통과 | 3-4 | 렌더러 없으면 데이터 채우기 전 반환, 가드는 "비어 있지 않은가" 하나 → 직전 Set 핸들로 모핑이 돈다 |
| **D15** | 구조·결합 | CAD 완료 통지가 요청과 짝지어지지 않는다 | 3-4 | `enqueueUpdatePrtGeometry:148` 이 식별자를 안 돌려줘 짝짓기가 문자열 비교이고, 신호 선택도 `onCommandCompleted:187` 의 `m_batchMode` 에 달렸다 → 다른 모듈이 배치 모드를 켜 두면 통지가 오지 않는다 |
| **D16** | 진입·수명 | CAD 실패 경로가 대기 상태를 정리하지 않는다 | 3-4 | `m_pendingCadStpPath` 는 완료 슬롯 진입 직후에만 지워진다 → 실패 후 같은 경로의 완료 통지가 오면 흘러간 요청이 되살아난다 |
| **D17** | 데이터 정본 | CAD 완료 처리가 파일 표를 재구축해 사용자 상태를 지운다 | 3-4 | `refreshFileTableFromDisk()` 가 표를 통째로 다시 만든다 → 요청과 완료 사이의 체크 상태와 `m_fileTableDvValues` 전량이 사라진다 |
| **D18** | 데이터 정본 | 템플릿 치환이 텍스트 전역 치환이고 값이 절삭된다 | 3-4 | `generateDatFile:1574` 이 `QMap` 사전순으로 `"${이름}"` 전역 치환 → `${L}` 가 `${L1}` 를 잡고, `QString::number` 기본 정밀도로 6자리에서 잘린다 |
| **D19** | 실행 모델 | 정규화 config 파싱 실패의 처리가 경로마다 다르다 | 3-4 | 수동 YAML 스캐너가 무효를 내면 값이 보정 없이 통과하고 경고는 Morphing 경로에만 → CAD·ConditionParameter 는 실패를 알리지 않는다 |
| **D20** | 데이터 정본 | NodeSet 판정이 `Qt::UserRole` 에만 있고 텍스트 경로에서 비어 있다 | 3-4 | 값은 `loadSetsIntoPartCombo:1965` 만 세우고 `setCurrentText` 경로에선 비어 → NodeSet 이 Part 로 취급. 두 번째 규칙 `PM:isNodeSetPart:75` 는 미호출 경로에서만 닿는다 |
| **D21** | 데이터 정본 | 행 삭제 범위가 접두사 매칭 | 3-5 | `PM:relatedFilePathsForDeletion:40` 이 `completeBaseName()` 접두사 파일 전량 삭제 → `Predict_1` 이 `Predict_1x` 를 함께 잡고, D34 로 카운터가 리셋되면 충돌이 앞당겨진다 |
| **D22** | 데이터 정본 | Preview 버튼의 행 인덱스가 생성 시점에 고정 | 3-5 | `[X]` 는 `indexAt(...).row()` 재계산, `[Preview]` 는 캡처된 `row` → 앞 행이 지워지면 다른 케이스가 열린다 |
| **D23** | 실행 모델 | 예측 프로세스 상호 배타가 조용하다 | 3-6 | `startPredictionJob:177` 의 `false` 를 호출부 3곳이 검사하지 않는다 → ND 와 1D 를 함께 실행하면 1D 가 모달 경고 없이 누락된다 |
| **D24** | 데이터 정본 | 두 번째 `updateModelUploadConfig` 가 첫 번째의 `Output Response` 를 덮는다 | 3-6 | 같은 JSON 키를 read-merge-write → 1D 가 D23 으로 거절돼도 JSON 엔 1D 페어가 남아 계약 파일이 실제 실행과 다르다 |
| **D25** | 데이터 정본 | 자동 렌더가 마지막 케이스 1건만 가리킨다 | 3-6 | `m_lastPreviewedVtuPath` 를 루프 끝에서 한 번 세운다 → 나머지는 행별 `[Preview]` 로만 열린다 |
| **D26** | 데이터 정본 | `updateModelUploadConfig` 가 사용자 입력값을 기본값으로 되돌린다 | 3-6 | `model_info.json` 재파싱으로 `m_designVariables` 를 교체하고 `meta.default` 를 JSON 에 쓴다 → Generate 때 저장한 화면 값이 실행 시점에 덮인다 |
| **D27** | 실행 모델 | 1D 결과 대기가 고정 500ms | 3-7 | `singleShot(500)` 뒤 `lastModified` 최대 CSV 선택 → 쓰기가 더 걸리면 이번 결과를 놓치고 다음 예측에서 이전 파일이 최신으로 잡힌다 |
| **D28** | 구조·결합 | 뷰가 `DashMainWindow` 를 부모 거슬러 4벌로 찾는다 | 3-7·5절 | `W:371` 람다·`:1185`·`:1264`·`:1335`. 같은 파일의 `findChild<` 5회·`QMessageBox::` 15회와 같은 성격 |
| **D29** | 구조·결합 | 민감도 콤보가 다른 계층의 키를 기대하고 실패가 조용하다 | 3-8 | `AW:1233` 이 `ModelBuilder_*/model_info.json` 에서 Model Runner 자기 JSON 스키마(`Model upload.Input Design Variables.label`)를 읽고, 4단 중첩 `if` 는 어디서 빠져도 로그가 없다 → 변수 목록이 조용히 빈다 |
| **D30** | 구조·결합 | 민감도 폴더 열거에 Set 필터가 없다 | 3-8 | `initializeTargetData:370` 이 `ModelBuilder_*` 전량을 담고 `m_setName` 은 초기 인덱스에만 → 매치 실패 시(D37) 0번이 선택돼 무관한 Set 으로 플롯이 나간다 |
| **D31** | 데이터 정본 | 민감도 캐시 키가 모델 내용 변경을 감지하지 못한다 | 3-8 | 키는 명령 + 경로 2\~3개뿐이고 비우는 곳은 `startDaemon` 최초 기동과 `setSetName` 둘뿐 → 같은 경로에서 재학습하면 낡은 결과가 나온다 |
| **D32** | 진입·수명 | 민감도 실패 4경로가 대기 상태를 남긴다 | 3-8 | 빈 응답·파싱 실패·`error` 키·미대기 상태가 `m_pendingCommand` 를 안 지운다 → 공용 데몬 브로드캐스트에서 다음 응답을 오인 수신할 수 있다 |
| **D33** | 데이터 정본 | 설정 JSON 이 쓰기 전용 | 3-9 | `Prediction Cases` 는 쓰기 3함수만 있고 읽는 코드가 없다 → 행별 DV 값·체크 상태·DV-only 행·카운터가 세션을 못 넘기고, 재진입 후 실행하면 모든 행이 현재 dvTable 값 한 벌을 공유한다 |
| **D34** | 진입·수명 | `m_predictionCount` 소실이 생성 파일을 덮어쓴다 | 3-9 | 생성자에서 0 이고 `clearAllTables` 도 안 건드린다 → 재진입 후 Generate 하면 같은 이름이 다시 만들어져 두 행이 아니라 한 행이 된다 |
| **D35** | 데이터 정본 | 같은 케이스가 다른 확장자로 복원된다 | 3-9 | 생성은 `.vtu` 절대경로, 스캔은 `*.dat`·`*.inp` → 열람이 동명 `.vtu` 리다이렉트에 의존한다 |
| **D36** | 진입·수명 | Set 전환이 CAD 대기 상태를 이월한다 | 3-9 | `clearAllTables:1381` 이 표·맵만 비우고 대기 경로·파라미터를 남긴다 → 이전 Set 의 완료 신호가 새 Set 표에 행을 만든다 |
| **D37** | 데이터 정본 | MCU 민감도 Set 이름에 접미사가 이중으로 붙는다 | 4절 | `MW:163` 이 이미 `-MCU` 로 끝나는 이름에 다시 붙인다 → `ModelBuilder_Set1-MCU-MCU` 를 찾다 실패하고 0번이 선택된다(D30) |
| **D38** | 진입·수명 | Set 불일치 방어가 초기 진입에서 돌지 않는다 | 3-9 | `onSurrogateCheckBoxChanged` 의 "체크 행 Set ≠ 현재 Set 이면 파일 표·DV 맵을 비운다" 방어에 `&& !currentSetName.isEmpty()`(`W:857`) 예외가 붙어 있다 → `getSetName()` 이 아직 비어 있는 최초 진입에서는 다른 Set 의 모델을 체크해도 이전 표가 남고, 그 상태의 Generate 가 섞인 입력을 만든다 |
| **U1** | 미구현 | 파일 표 체크 상태를 JSON 에 반영하는 함수가 빈 본문 | 3-5 | `W:syncFileTableToJson:998` 은 주석뿐인데 3곳(`:587`·`:1825`·`:1831`)에서 호출된다 → 체크 상태가 재진입에서 소실(D33) |
| **U2** | 미구현 | 체크 행 일괄 삭제가 UI 에 없다 | 3-5 | `W:onDeleteButtonClicked:550` 39줄이 구현돼 있으나 connect 0건 · 대응 버튼 없음 |
| **U3** | 미구현 | `params.fileTableFiles` 와 그 소비 함수가 도달 불가 | 3-6 | `PM:validatePredictParams:248` 이 채우지만 이후 코드는 `collectPredictionCases()` 만 쓰고, 유일한 소비 함수 `W:syncAnalysisInputFilesToJson:1721` 은 호출처 0곳 |
| **U4** | 미구현 | 구버전 CLI 형태의 예측 슬롯이 남아 있다 | 3-6 | `M:onPredictButtonClicked:881` 이 출력 디렉터리 인자 없는 `test-model-1d {configJson}` 로 호출한다. 호출처 0곳 |
| **U5** | 미구현 | 도메인 신호 4종의 수신처가 0곳 | 5절 | `designVariablesChanged`·`surrogateModelsChanged`·`fileTableUpdated` 는 연결하지 않는 이유가 주석으로 있고(`W:108-109`), `surrogateModelUpdated` 는 방출부 `M:updateSelectedModel:919` 자체가 미호출 → 모델→뷰 갱신이 `dataLoaded` 재사용 + 플래그로 좁혀진다 |
| **U6** | 미구현 | 도달하지 않는 정의 18종 | 3-4·3-6·5절 | `M:` — `onPredictButtonClicked:881`·`onResponseSurfaceButtonClicked:878`(빈 함수)·`runFESolver:1793`·`savePartAsVtu:1635`·`getXmlFiles:1445`·`getModelList:1374`·`getAvailableResponses:1365`·`initializeSetConfig:2237`·`getRuntimeContextForSet:514`·`updateSelectedModel:919`. `W:` — `onDeleteButtonClicked:550`·`populateAllWidgets:621`·`updateDesignVariablesFromModelInfo:1429`·`validateGenerateInputFileParams:1440`·`syncAnalysisInputFilesToJson:1721`. `PM:` — `validateGenerateInputFileParams:171`·`validateReferenceFile:222`·`isNodeSetPart:75`(셋 다 위 미호출 뷰 함수로만 도달). 이 중 `runFESolver` 는 157줄로 cae-launcher C++ API(`dash::cl::AnsysMechanicalLauncher`·`AbaqusLauncher`)를 직접 몰고 모델 계층에서 `QMessageBox::warning` 을 4회 띄우며, 전용 멤버 `m_ansysLauncher`·`m_abaqusLauncher` 가 객체 수명 내내 유지된다 — 화면엔 FE 솔버 실행 버튼이 없다 |

---
