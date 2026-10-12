# 다중 응답·다중 모델 파이프라인 — 공통 규격 설계와 작업 계획

> 관련 Issue: 발행 전 (Epic 1 + 하위 13건 초안). 선행 #722, 접점 #724 · #643 · #684 · #726 · #741.
> 상태: **코드 조사 기반 설계안** — origin/dev `a076fde7` (2026-10-11), PR #722 브랜치, DashOpti_DeepOpt 현재 트리 기준. 구현 착수 시 좌표 재확인.
> 출처: `dashopti_project_unit_v1.drawio` 의 빨간 항목 (추가·확장할 비즈니스 로직).
> 해상도: #740 하위 이슈 양식 (`현상 / 범위 / 현재 구조 / 변경 / 기대 / Related`).


## 1. 조사로 바뀐 전제

| 그림의 전제 | 실제 코드 |
|---|---|
| Preprocessor 가 y 하나를 y.xml 로 쓴다 | 응답 목록은 이미 받지만 응답마다 XML 1개 (`DashAnalysisLauncher::processResults` 요청 루프, `DashResultBatch::outputFileName`). 응답 텐서 키는 `sanitizeString(name)`, `y` 키 없음 |
| Builder Configuration 단수 | `Configuration` 은 모델 타입을 키로 한 객체. 같은 타입 2개 불가 (`TrainingPlanError::DuplicateModel`). 응답별 reduction·transformation 은 `Data Label.Output` 에 이미 있음. 단, reload 가 transformation 을 버리고 DeepOpt 는 transformation 을 읽지 않음 |
| 마지막 학습본만 남음 | DeepOpt 가 `{out}/{response}/{Type}_{err}` 로 쓰고 `errors[response]` 를 1D run 마다 초기화, Smart 모드는 최적 외 삭제. 소비자는 첫 glob 일치를 집음 |
| Runner Output response 단수 | 이미 배열. 1D 는 전 항목, ND 는 `[0]` 만 실행 (DeepOpt main.py:473). `set` 은 절대경로 |
| Optimizer 가 `model` 키로 모델 선택 | DeepOpt `_build_response_paths` 가 `model` 을 무시하고 `{path}/{response}/**/*.pt` 중 최저 오차 파일을 고름 |
| set + model_id 참조 | `model_id` 는 두 레포 어디에도 없음. #722 가 Runner·Optimizer 의 Builder 참조를 `modelBuilder {set: setId, name}` 으로 바꾸는 중 (미머지) |

열린 작업과의 접점: #722 (Builder 참조 setId, 선행), #724 (Runner Output Response 영속 분리), #643 1차 (Set 단위 XML, 본 계획 1.1 이 흡수), #684 (SurrogatePredictor, 모델 참조 객체를 채택할 후속), #727 (#737, 무관하나 Set 파일 네임스페이스 공유).

## 2. 공통 규격 (D1~D7)

### D1. 응답은 데이터셋 XML 의 텐서 키로 식별한다
- Launcher Set 1회 Preprocess = XML 1개. 샘플 dict 에 응답 텐서가 N개, 키는 `sanitizeString(name)`.
- `model_info.selected_responses` = 배열. 항목 `{ key, component, load_step, name, file_name }`. `key` 가 샘플 텐서 키이자 하류의 응답 식별자. 단수 `selected_response` 는 쓰지 않는다.
- 1차 제약: 한 XML 의 응답은 같은 component. 다른 component 는 Preprocess 시작 시 거부 (topology 슬롯이 샘플당 1개). 다중 component 는 #643 추가 고려 1 로 둔다.

### D2. 모델은 (Builder setId, model_id) 로 식별한다
- `model_id` 는 Builder Set 안에서 유일, 형식 `model{N}`, Set json 의 `modelSeq` 카운터로 발급, 삭제 후 재사용 없음 (SI-4 와 같은 이유: 옛 참조가 새 모델에 붙지 않게).
- 참조 객체 `{ set: <Builder setId>, model_id }`. Runner·Optimizer·DOE 리샘플링이 같은 객체를 쓴다. 이름·폴더명·절대경로는 참조 키가 아니다.
- 외부 엔진 입력에는 실행 직전 해석한 절대경로 `path` 를 항목에 덧붙인다 (#722 가 Runner `Output Response[].set` 에 쓰는 방식). DeepOpt 는 `path` 만 읽고 set·model_id 의 의미를 모른다.

### D3. ModelBuilder_{Set}.json v2
```json
{
  "setId": "…", "variant": "Sim", "modelSeq": 2,
  "Data Label": { "Dataset": "<abs xml>", "Input": {"<label>": {"reduction": "None"}},
                  "Output": {"<key>": {"reduction": "Max", "transformation": "Log"}} },
  "Configuration": [
    { "id": "model1", "response": "<key>", "type": "RF",  "options": {…}, "run": true },
    { "id": "model2", "response": "<key2>", "type": "MLP", "options": {…}, "run": false }
  ]
}
```
- `Configuration` 은 배열, 행마다 id·response·type·options. 같은 type 여러 행 허용. 옵션은 행 소유.
- `status`·`error` 는 Set json 에서 뺀다. 산출물 상태는 model_info.json 의 소관 (D5).

### D4. 산출물 디렉터리 = `{ModelBuilder_Set}/{model_id}/`
- 내용: `model.pt` (+ `input_scaler.pkl`, `output_scaler.pkl`, `config.yaml`, ND 의 `rendered_results/` 등 기존 파일). 파일명에 오차를 싣지 않는다.
- 재학습은 같은 디렉터리를 비우고 다시 쓴다. Smart 모드의 후보 정리는 그 디렉터리 안에서만.
- `{response}/{Type}_{err}` 레이아웃과 glob 탐색은 전부 제거.

### D5. model_info.json v2
```json
{
  "parameter": {…},                       // 그대로
  "originRecord": {…},                    // #691 그대로
  "selected_responses": [ { "key": "...", "component": "...", "load_step": "...", "name": "...", "file_name": "..." } ],
  "models": {
    "model1": { "response": "<key>", "type": "RF", "input_order": ["dv1","dv2"],
                "reduction": "Max", "transformation": "Log",
                "path": "model1/model.pt", "status": "Done",
                "errors": { "R2": 0.98, "MAPE [%]": 1.2 } }
  }
}
```
- 소유: GUI 가 학습 시작 때 `parameter`·`selected_responses`·`originRecord` 와 `models[id]` 의 response·type·input_order·reduction·transformation·status="In Progress" 를 쓴다. DeepOpt 는 완료 때 `models[id]` 의 `path`·`status`·`errors` 만 갱신한다.
- 최상위 `errors`·`selected_response` 는 없다. 있으면 v1 산출물로 보고 거부한다.
- 사용 가능 모델 = `status == "Done"` 이고 `path` 가 존재하는 항목.

### D6. 소비 측 참조 형식
- Runner `Model upload.Output Response[]` = `{ set, model_id, response, model, path }` (`model` 은 type, 표시용. `path` 는 실행 직전 기록).
- Optimizer `Optimization.trained_surrogate_model[]` = `{ set, model_id, response, model, symbol, path }`. 항목마다 set 이 달라도 된다 (Deck 2~). 참조한 모든 모델의 `parameter` 라벨 집합이 같아야 하고 다르면 거부.
- `symbol` 은 행 추가 순서로 발급하고 저장값을 유지한다 (현재는 로드마다 r1.. 재부여).

### D7. 하위호환
- v1 데이터셋 (`selected_response` 단수)·v1 Set json (타입 키 Configuration)·v1 model_info (최상위 `errors`) 는 변환하지 않고 거부하며 재생성을 안내한다. #368·#685 의 정책과 같다.
- Runner·Optimizer 설정의 v1 항목 (`model_id` 없음) 은 빈 선택으로 연다.

## 3. 이슈 계층

```
[Epic] 다중 응답·다중 모델 파이프라인 — Launcher XML 1개에 응답 N개, Builder Set 에 모델 N개, set + model_id 참조
├─ 0 공통 규격
│  ├─ 0.1 GUI: 모델 참조 객체와 model_info v2 판독을 DashModelBuilderArtifact 에 둔다
│  └─ 0.2 DeepOpt: 산출물 계약 v2 — model_id 디렉터리, model_info.models, path 기반 로더
├─ 1 Preprocessor
│  ├─ 1.1 XML model_info 를 selected_responses 배열로 쓰고 Launcher 의 Output Response 저장을 Config 로 옮긴다
│  └─ 1.2 Launcher Set 1회 Preprocess 가 XML 1개에 응답 N개를 쓴다 (#643 1차 흡수)
├─ 2 Builder
│  ├─ 2.1 ModelBuilder Set json 의 Configuration 을 model_id 행 배열로 바꾼다
│  ├─ 2.2 Builder 가 selected_responses 를 읽고 model_info v2 의 models 를 기록한다
│  ├─ 2.3 모델 상태·오차·삭제를 model_info.models[id] 기준으로 바꾼다
│  └─ 2.4 DeepOpt train: Configuration 배열, model_id 출력 디렉터리, transformation 적용
├─ 3 Runner
│  ├─ 3.1 Runner Output Response 항목을 {set, model_id} 로 바꾸고 모델 단위 행으로 복원한다
│  ├─ 3.2 Run AI Prediction 이 선택 모델 전부를 실행하고 결과를 model_id 열로 누적한다
│  └─ 3.3 DeepOpt test-model-1d/nd: path 기반 로딩, ND 전 항목 실행
└─ 4 Optimizer
   ├─ 4.1 Optimizer 가 여러 Builder 의 모델을 {set, model_id} 로 선택·저장·복원한다
   ├─ 4.2 run-optimization 호출을 <OptSet.json> <OutputDir> 로 바꾸고 path 를 실행 직전 기록한다
   └─ 4.3 DeepOpt run_optimization: trained_model_path 제거, _build_response_paths 를 path 로 교체
```

선행 관계
```
#722 머지
 └─ 0.1 ─┬─ 1.1 ─ 1.2
         ├─ 2.1 ─┬─ 2.2 (1.1 뒤)
         │       └─ 2.3
         ├─ 3.1 (#724 와 조율) ─ 3.2
         └─ 4.1 ─ 4.2
0.2 ─┬─ 2.4 (2.1 과 동시)
     ├─ 3.3 (3.2 와 동시)
     └─ 4.3 (4.2 와 동시)
```
GUI 이슈와 DeepOpt 이슈는 레포가 다르다. 0.2·2.4·3.3·4.3 은 DashOpti_DeepOpt 에 발행하고 GUI 이슈에서 링크한다. 2.4/2.1, 3.3/3.2, 4.3/4.2 는 같은 계약의 양쪽이라 머지 시점을 맞춘다.

## 4. 이슈 초안

### 0.1 GUI: 모델 참조 객체와 model_info v2 판독을 DashModelBuilderArtifact 에 둔다

현상
- Runner 는 `Output Response[].set` 에 절대경로 (`DashModelRunner.cpp:999`), Optimizer 는 `trained_surrogate_model[]` 에 `{model, response, symbol}` 만 쓴다 (`DashOptimizer.cpp:422`). 모델을 가리키는 키가 모듈마다 다르고 `model_id` 는 없다.
- #722 가 `DashModelBuilderArtifact` (model_info 읽기·originRecord 판독) 와 `DashModelBuilderReference` (setId → 폴더·model_info) 를 신설한다. v1 `errors` 를 전제한다.

범위
- 건드림: `model/DashModelBuilderArtifact.{h,cpp}`, `model/DashModelBuilderReference.{h,cpp}` (#722), `tests/TestModelBuilderArtifact.cpp`
- 안 건드림: 각 모듈의 Set json 쓰기·UI (1~4 절), DeepOpt

현재 구조
- `DashModelBuilderArtifact::readModelInfo` / `parse` 는 originRecord 만 판독. 오차는 Runner `loadSurrogateModels` (`DashModelRunner.cpp:652`), Optimizer `loadSurrogateModelsFromJson` (`DashOptimizer.cpp:614`), `DashSurrogateModelCommon::parseSurrogateModelErrors` 가 각자 `errors[resp][model][metric]` 를 읽는다.
- `DashModelBuilderReference::load()` 가 setId → 폴더·model_info·deck 을 1회 해석한다.

변경
- `DashModelBuilderArtifact` 에 추가: `struct ModelRef { QString set, modelId; }` 와 json 읽기/쓰기 (키 `set`·`model_id`), `struct ModelEntry { id, response, type, inputOrder, reduction, transformation, path, status, errors }`, `readModels(modelInfoRoot, error)` — `models` 없음·최상위 `errors` 존재·항목 필수키 누락은 "<artifact> cannot be used: …" 로 거부. `usable(entry)` = Done 이고 path 존재.
- `DashModelBuilderReference` 에 `modelDir(modelId)` (절대경로) 와 `LoadedArtifact.models` 추가. `issueModelId(setRoot)` 는 `modelSeq` 를 올려 `model{N}` 을 돌려준다.
- `parseSurrogateModelErrors` 의 ErrorMap 생성을 `ModelEntry` 목록에서 하도록 교체.

기대
- 테스트: ModelRef round-trip, v1 model_info 거부 사유, models 판독·usable 판정, modelSeq 가 삭제 뒤에도 증가
- Runner·Optimizer 가 v1 `errors` 를 직접 읽는 코드가 남지 않는다 (3.1·4.1 에서 치환)

Related: 선행 #722. 후속 1~4 절 전부. #684 는 `ModelRef` 를 요청 키로 채택한다.

### 0.2 DeepOpt: 산출물 계약 v2 — model_id 디렉터리, model_info.models, path 기반 로더

현상
- 산출물이 `{out}/{response}/{Type}_{err:.8f}[.pt|/]` 이고 (`base_trainer.py:100`, `ann_trainer.py:397`, `result_saver.py:151`), 모델 식별이 파일명 접미 오차다. `pred_surrogates.detect_model_type` 이 경로 문자열의 `ANN_`/`MLP_`/`BNN_` 로 타입을 추정한다 (:327).
- model_info.json 은 `errors` 만 쓴다 (`run_train_1d.py:144`, `result_saver.py:40`).

범위
- 건드림: `source/models/oned/*trainer.py` 의 저장 경로, `trainer_utils/result_saver.py`, `run_train_1d._save_model_info_json`, `optimize/pred_surrogates.py` 로더, 신규 `source/artifact.py` (계약 1곳)
- 안 건드림: 학습 알고리즘, CLI 서브커맨드 (2.4·3.3·4.3)

변경
- `artifact.py`: `model_dir(output_dir, model_id)`, `write_model_entry(model_info_path, model_id, path, status, errors)` (지정 키만 갱신, 나머지 보존), `load_model(path, type)` — 타입은 model_info `models[id].type` 또는 호출자 인자, 경로 추정 없음.
- 트레이너는 `model_dir` 아래에 `model.pt`·scaler·config 를 쓴다. 파일명 오차 접미 제거. Smart 는 그 디렉터리 안의 후보만 정리.
- `_save_model_info_json` / `save_model_info_json` 은 `write_model_entry` 로 교체. `errors[response] = {}` 초기화 제거.

기대
- 두 트레이너 모두 `{out}/{id}/model.pt` 를 남기고 model_info `models[id].{path,status,errors}` 를 쓴다 (단위 테스트: 임시 디렉터리 round-trip)
- 작업 트리에 `_get_model_score`·`{Type}_*` glob 이 없다 (4.3·3.3 이 소비처를 지운 뒤)

Related: GUI 0.1 과 같은 계약. 2.4·3.3·4.3 선행.

### 1.1 XML model_info 를 selected_responses 배열로 쓰고 Launcher 의 Output Response 저장을 Config 로 옮긴다

현상
- `DashResultXmlWriter::writeModelInfoToXml` (`DashResultXmlWriter.cpp:971`) 이 `selected_response` 단수 dict 를 쓴다. 호출부 `DashAnalysisLauncher.cpp:1202` 와 KPI 경로 5곳 (`DashAnalysisLauncherKPI.cpp`) 이 4종 키 (`component`, `load_step`, `name`, `file_name`) 를 각자 만든다.
- Launcher 의 "Output Response" 표는 `DashAnalysisLauncherPresentationModel::saveOutputResponse` (:108) 가 `root["Output Response"]` 를 직접 read-modify-write 한다. `DashAnalysisLauncherConfig` 를 거치지 않고, 읽어 복원하는 코드가 없다.

범위
- 건드림: `DashResultXmlWriter::writeModelInfoToXml` 시그니처와 본문, `DashAnalysisLauncher.cpp` 의 responseInfo 조립 (:1077~1097 상당), `DashAnalysisLauncherKPI.cpp` 5곳, `DashAnalysisLauncherConfig` 에 `Output Response` 읽기/쓰기, `saveOutputResponse`, `tests/TestResultXmlWriter.cpp`, `tests/TestAnalysisLauncherConfig.cpp`
- 안 건드림: 샘플 텐서 쓰기, 요청 루프 (1.2), Builder 파서 (2.2)

변경
- `writeModelInfoToXml(doc, root, parameterInfo, analysisType, QList<SelectedResponse>, originRecord)`. `SelectedResponse { key, component, loadStep, name, fileName }` 는 `DashResultTypes.h` 에. `key` = 샘플에 쓴 텐서 키. 배열 1개도 배열로 쓴다.
- KPI 경로도 같은 구조체로 조립. 리터럴 4종 키는 XmlWriter 1곳.
- `DashAnalysisLauncherConfig::read/writeOutputResponses(root, QList<ResultRow>)`. `saveOutputResponse` 는 이것을 부른다. 위젯 열기 때 표 복원.

기대
- `TestResultXmlWriter` 에 `writeModelInfoToXml` 케이스: 항목 2개 배열, `key` 가 샘플 키와 같음, 빈 목록이면 model_info 생략 유지
- `TestAnalysisLauncherConfig` 에 Output Response round-trip
- 작업 트리의 XML 작성 코드에 `"selected_response"` 문자열이 없다

Related: 선행 0.1 (규격 문서 참조만, 코드 의존 없음). 후속 1.2·2.2. #643 과 접점.

### 1.2 Launcher Set 1회 Preprocess 가 XML 1개에 응답 N개를 쓴다 (#643 1차 흡수)

현상
- `DashAnalysisLauncher::processResults` 가 요청마다 `QDomDocument` 를 새로 만들어 (:1124) 전 샘플을 돌리고 저장한다 (:1212). 샘플 파일을 요청 × 샘플 횟수만큼 연다. 파일명은 `{comp}_{step}_{substep}_{name}.xml` (`DashResultBatch::outputFileName`).
- `appendSample` 은 샘플당 응답 1개를 쓰고 `responseWritten_` 플래그 1개로 성공을 판단한다. topology 슬롯은 샘플당 1개 (`writeGeometryToXml(componentName)`).
- 카탈로그는 `resultRequests[0]` 의 시간으로 1회 초기화된다 (:1029).

범위
- 건드림: `processResults` 루프 구조, `DashResultProcessor::processSamples`·`DashResultXmlWriter::appendSample` 의 응답 목록 인자, `DashResultBatch::outputFileName`, Builder 가 고르는 데이터셋 목록 (`DashModelBuilder` 의 Launcher 폴더 XML 나열), `tests/TestResultProcessor.cpp`, `tests/TestResultBatch.cpp`
- 안 건드림: circularity 의 BORE/BOSS 병합 (현행 유지, 별 XML), KPI 경로, 다른 component 응답의 topology 분리

변경
- 루프 반전: 샘플마다 파일 1회 열기 → 응답 N개 `GetFieldOutputVtk` → 같은 샘플 dict 에 N개 텐서. 응답별 성공 플래그, 하나라도 Missing 이면 샘플 제외 (현행 "부분 샘플 없음" 규칙 유지).
- 시작 전 검증: 응답들의 component 가 다르면 거부하고 사유 표시. step 이 카탈로그와 다른 응답은 요청별 카탈로그 조회.
- 파일명 `{LauncherSet}_{step}_{substep}.xml` 1개. `model_info.selected_responses` 에 N항목 (1.1).

기대
- 응답 2개 Preprocess 가 XML 1개를 만들고 Builder Output 표에 라벨 2개가 뜬다 (GUI)
- `TestResultProcessor`: 응답 2개 중 하나 Missing 인 샘플 제외, 파일 열기 횟수 = 샘플 수
- 다른 component 응답 혼합은 시작 전에 거부된다 (단위 테스트)

Related: 선행 1.1. #643 1차의 구현. 2차 (uuid 확인·이어쓰기·HDF5) 는 #643 에 남긴다.

### 2.1 ModelBuilder Set json 의 Configuration 을 model_id 행 배열로 바꾼다

현상
- `Configuration` 이 모델 타입을 키로 한 객체 (`DashModelBuilder.cpp:648, 768`). 같은 타입 두 행은 `TrainingPlanError::DuplicateModel` (`DashModelBuilderPresentationModel.cpp:370`) 로 막힌다. 옵션 패널은 타입당 1페이지 (`m_configWidgets[modelName]`, `DashModelBuilderWidget.cpp:777~888`) 라 두 행이 옵션을 공유한다.
- 상태 폴링 `checkModelStatusInternal` 과 `onModelStatusUpdated` 가 모델 콤보 텍스트 (타입) 로 행을 찾는다. `restoreConfigurationUI` 는 Configuration 키마다 행 1개.

범위
- 건드림: `DashModelBuilder::onTrainingStartButtonClicked` 의 Configuration 조립, `loadDataLabelConfig` (transformation 누락 결함 포함), `DashModelBuilderPresentationModel::buildTrainingStartPlan`·`TrainingRowInput`, `DashModelBuilderWidgetBase::addModelRow`·`getModelConfiguration`·`updateConfigUI`, `DashModelBuilderWidget::restoreConfigurationUI`·`onStartTrainingClicked`, `ModelBuilderConfigHelper` (죽은 parse 함수 정리), MCU 변형의 Configuration 쓰기 (`DashModelBuilderMCU.cpp:511~555, 729~760`)
- 안 건드림: model_info.json (2.2), 상태·삭제 (2.3), DeepOpt (2.4)

변경
- Configuration = 배열, 행 `{id, response, type, options, run}`. 새 행은 `DashModelBuilderReference::issueModelId` 로 id 발급. 행 데이터 (`TrainingRowInput`) 에 id 추가. `DuplicateModel` 삭제.
- 옵션 페이지를 행별 인스턴스로: `m_configWidgets[id]`. 타입을 바꾸면 그 행의 페이지를 새로 만든다.
- `status`·`error` 키를 쓰지 않는다. 폴링·행 찾기는 2.3 에서 id 로 바꾸므로 본 이슈는 Set json 쓰기·복원까지.
- `loadDataLabelConfig` 가 `transformation` 을 읽어 Output 표를 복원한다.

기대
- 같은 타입 두 행을 추가·학습 시작·재열기해도 행 2개와 각자 옵션이 복원된다 (GUI)
- 단위 테스트 (`buildTrainingStartPlan`): id 가 있는 행만 Configuration 에 들어가고 run 플래그·options 가 행별로 보존됨
- 작업 트리에 `DuplicateModel` 이 없다. 1D/ND 혼합 선택은 시작 전에 거부된다 (현재는 첫 행으로 서브커맨드를 정함, :841~843)

Related: 선행 0.1. 후속 2.2·2.3. 같은 계약 2.4.

### 2.2 Builder 가 selected_responses 를 읽고 model_info v2 의 models 를 기록한다

현상
- `parseModelInfoStream` 이 XML 에서 `parameter`·`selected_response` (단수, `:2036`) 를 읽고 `readSelectedResponseFromStream` (`:1859`) 은 flat string dict 만 받는다. 학습 시작 시 `modelInfoRoot["selected_response"]` 로 복사한다 (`:809`).
- 학습 시작 시 model_info.json 에는 parameter·selected_response·originRecord 만 쓰고, 모델별 메타 (응답·타입·입력 순서·reduction·transformation) 는 어디에도 없다. `DashXmlTailLocator` 의 꼬리 파싱이 `parameter`/`selected_response` 구조를 가정한다.

범위
- 건드림: `parseModelInfoStream`·`readSelectedResponseFromStream`, 학습 시작의 model_info 쓰기 (`:782~830`), `DashXmlTailLocator.h` 의 가정 주석·예산, Output 표 라벨 ↔ `selected_responses[].key` 대응, `DashModelBuilderMCU.cpp:617~676` 의 같은 복사
- 안 건드림: errors 읽기 (2.3), DeepOpt 쓰기 (2.4)

변경
- XML 의 `selected_responses` 배열을 `QList<SelectedResponse>` 로 읽는다. 단수 키는 거부 ("dataset cannot be used: v1 selected_response").
- 학습 시작 때 `models[id]` 를 행마다 기록: response (= Output 라벨 키), type, `input_order` (Input 표 체크 순서), reduction·transformation (Output 표 값), status "In Progress". 이미 있는 다른 id 의 항목은 보존, 같은 id 는 교체.
- 최상위 `errors`·`selected_response` 는 쓰지 않는다. 기존 파일에 있으면 제거한다 (재학습으로 v2 전환).

기대
- 단위 테스트 (XML 파서): 배열 2개 읽기, 단수 키 거부, 꼬리 파싱 예산 안에서 성공
- 학습 시작 직후 model_info.json 이 D5 형태 (GUI 확인, 또는 `writeTrainingStartModelInfo` 를 순수 함수로 빼 단위 테스트)

Related: 선행 1.1·2.1. 후속 2.3·3.1·4.1.

### 2.3 모델 상태·오차·삭제를 model_info.models[id] 기준으로 바꾼다

현상
- 상태는 Set json `Configuration[type].status` 를 폴링 (`checkModelStatusInternal`), 오차는 model_info `errors[resp][type][metric]` (`loadTrainedModelInfo :1163`, `refreshTrainedModelInfo :1287` 가 타입별 최저 MAPE 만 남김). 산출물 목록은 `{resp}/{Type}_{err}` 스캔 (`getTrainedModelList :2193`, `getTrainedModelFolderNames :2336`). 삭제는 `deleteTrainedModel` 이 `errors` 키와 `{model}*` 파일을 지운다.

범위
- 건드림: 위 함수들, `finalizeStaleStatuses`, `onModelStatusUpdated`·`aboutToRemoveModelRow` (행 → id), 모델 표 metrics 열 채우기 (`addModelRowExtras`), `getTestDatasetFiles` 경로, MCU 의 `updateModelStatusFromOutputDir`
- 안 건드림: Set json 형식 (2.1), DeepOpt

변경
- 폴링 대상 = model_info.json `models[id].status`. 행은 id 로 찾는다. 지연 폴링 `checkModelStatusFinal` 과 `finalizeStaleStatuses` 는 `models[id]` 에 적용.
- 오차 표시 = `models[id].errors`. 타입별 최저값 선별 로직 (`knownModelTypes`, :1162~1225 상당) 삭제.
- 산출물 디렉터리 = `{set}/{id}/`. 스캔 함수는 `models` 항목에서 나열. 삭제 = `models[id]` 제거 + 디렉터리 삭제.

기대
- 두 행 학습 후 표에 행별 상태·오차가 나오고, 한 행 삭제 뒤 다른 행과 디렉터리가 남는다 (GUI)
- `DashModelBuilder.cpp` 에 `"errors"` 최상위 읽기와 `_*.pt` glob 이 없다

Related: 선행 2.1·2.2·2.4 (DeepOpt 가 v2 를 써야 폴링이 돈다).

### 2.4 DeepOpt train: Configuration 배열, model_id 출력 디렉터리, transformation 적용

현상
- `train_model_1d` / `train_model_nd` (`main.py:143, 234`) 가 `Configuration` dict 를 순회하고 행의 `response` 를 버린 채 (:198, :287) 모든 Output 라벨을 학습한다. 상태는 Set json 에 `_update_json_status` (:57) 로 쓴다.
- `XMLTrainingDataBuilder.build_1d` 가 reduction 을 `"SUM"` 대문자로 비교해 GUI 의 `"Sum"` 이 무시된다 (:139). `transformation` 은 읽지 않는다.

범위
- 건드림: 두 서브커맨드의 설정 해석·루프, `_update_json_status` (삭제), `XMLTrainingDataBuilder` 의 reduction·transformation, 트레이너 호출 인자 (0.2 의 `model_dir`)
- 안 건드림: 모델 알고리즘, 테스트·최적화 서브커맨드 (3.3·4.3)

변경
- 행마다: 응답 = `row.response` 1개, 출력 = `model_dir(output_dir, row.id)`, 상태·오차·path 는 `write_model_entry` 로 model_info.json 에. Set json 은 읽기만.
- Output `transformation` (Log·Sqrt·Square·Reciprocal·Exponential) 을 y 에 적용하고 역변환 정보를 `models[id]` 에 남긴다 (`transformation` 키로 충분). reduction 비교는 대소문자 무시.
- 예외 시 `status: "Failed"` 와 메시지 기록, 비정상 종료 코드 반환 (현재는 0).

기대
- 샘플 Set json (행 2개, 같은 타입) 으로 돌리면 `{out}/model1/`·`{out}/model2/` 와 model_info `models` 2항목이 생긴다 (DeepOpt 단위 테스트, 합성 XML)
- `Sum`·`Log` 가 학습 데이터에 반영된다 (단위 테스트)

Related: 선행 0.2. GUI 2.1·2.2 와 같은 계약.

### 3.1 Runner Output Response 항목을 {set, model_id} 로 바꾸고 모델 단위 행으로 복원한다

현상
- (#722 기준) `DashModelRunnerConfig::writeOutputResponses(root, builderAbsPath, (response, model) 쌍)` 가 `{set: 절대경로, response, model}` 를 쓰고 `readSavedSelection` 은 (response, model) 쌍만 되읽는다. 표는 응답당 1행 + 모델 콤보 (`SurrogateTableController::createRow`).
- model_info v2 에서는 응답당 모델이 여러 개이고 같은 타입도 여러 개라 (response, type) 쌍으로는 모델을 특정할 수 없다.

범위
- 건드림: `DashModelRunnerConfig` 의 Output Response 읽기/쓰기, `SavedSelection`, `DashModelRunnerWidget::populateSurrogateTable`·`onRunAIPredictionClicked` 의 쌍 수집, `DashModelRunnerPresentationModel::groupCheckedPairs`, `DashSurrogateModelCommon::parseSurrogateModelErrors` 소비, `tests/TestModelRunnerConfig.cpp`
- 안 건드림: Builder 선택 참조 `modelBuilder {set, name}` (#722 그대로, Runner 는 Builder 1개), 실행 (3.2), 예측 항목 생성·삭제 (#741)

변경
- 항목 = `{ set, model_id, response, model, path }`. `set` = Builder setId, `path` 는 실행 직전 `DashModelBuilderReference::modelDir(id)` 로 기록 (#722 의 `set` 재해석 자리).
- 표 = `models` 의 usable 항목당 1행 (체크, id, response, type, metrics). 모델 콤보 삭제. 복원은 model_id 로 체크.
- 체크 변경 시점 저장은 #724 의 결정을 따른다. 본 이슈는 Run 시점 쓰기만 바꾸고, #724 가 먼저 머지되면 그 키에 model_id 를 싣는다.

기대
- `TestModelRunnerConfig`: 항목 round-trip, v1 항목 (model_id 없음) 은 빈 선택
- 같은 응답에 RF·MLP 두 모델을 체크·Run·재열기하면 두 행이 체크된 채 복원된다 (GUI)

Related: 선행 #722·0.1·2.3. 조율 #724·#726. 후속 3.2.

### 3.2 Run AI Prediction 이 선택 모델 전부를 실행하고 결과를 model_id 열로 누적한다

현상
- 1D 는 배열 전 항목을 돌리지만 결과 CSV 열이 응답 이름이라 같은 응답의 두 모델이 한 열에 겹친다 (`main.py:432` `_write_1d_test_result_to_csv`). ND 는 `Output Response[0]` 만 실행 (:473).
- GUI `onPredictionSucceeded` 는 500 ms 뒤 가장 최신 CSV 를 열어 보여준다. 예측 항목 (`Prediction Cases`) 은 응답·모델 정보가 없다 (`SharedTypes.h:51`).

범위
- 건드림: `DashModelRunner::run1DPrediction`·`runNDPrediction`·`onPredictionSucceeded`, CSV 뷰어로 넘기는 경로, `groupCheckedPairs` 의 ND/1D 분기
- 안 건드림: `[RESULT]` 파싱 모듈화 (#684), 예측 항목 생성·삭제 정합성 (#741)

변경
- ND·1D 각각 선택 항목 전부를 한 번의 config 로 넘긴다 (쌍 합집합 1회 쓰기, #724 의 경합 메모 해소).
- 결과 CSV 열 이름 = `{response} [{model_id}]`. 파일명 = `{RunnerSet}_test_results.csv` 로 고정하고 "최신 CSV 탐색" 을 지운다.
- ND 결과 vtu 는 `{case}/{model_id}/` 아래로 (3.3 과 합의).

기대
- 모델 3개 (1D 2, ND 1) 체크 후 Run 1회에 1D CSV 열 2개와 ND vtu 2세트가 생긴다 (GUI)
- `DashModelRunner.cpp` 에 최신 CSV 탐색 코드가 없다

Related: 선행 3.1·3.3. #684 가 뒤에 호출부를 모듈로 옮긴다.

### 3.3 DeepOpt test-model-1d/nd: path 기반 로딩, ND 전 항목 실행

현상
- `test_model_1d` 가 `set/response/{model}_*/model.pt` → `{model}_*.pt` glob 으로 첫 일치를 집는다 (`main.py:394~403`). `test_model_nd` 는 `Output Response[0]` 만 쓴다 (:473~476) 고 `{model}_*/model.pt` glob (:561).

범위
- 건드림: 두 서브커맨드의 모델 해석·루프·출력 파일명
- 안 건드림: `RunTest1D`·`RunTestNDFromVTU` 내부, `--with-std` 계약 (#684)

변경
- 항목의 `path` 로 `artifact.load_model` 호출. glob 삭제. `model_id` 는 출력 열·디렉터리 이름에만 쓴다.
- ND 는 전 항목 순회. 출력은 `{output_dir}/{case}/{model_id}/`.
- CSV 열 `{response} [{model_id}]`, 파일 `{basename(output_dir)}_test_results.csv`.

기대
- 샘플 config (항목 2개, 같은 응답) 로 CSV 열 2개가 생긴다 (단위 테스트, 더미 모델)
- `main.py` 에 `{model}_*` glob 이 없다

Related: 선행 0.2. GUI 3.2 와 같은 계약.

### 4.1 Optimizer 가 여러 Builder 의 모델을 {set, model_id} 로 선택·저장·복원한다

현상
- (#722 기준) Optimizer 는 Builder 1개를 `modelBuilder {set, name}` 으로 참조하고 `trained_surrogate_model[]` 항목은 `{model, response, symbol}` (`createSurrogateModelJsonArray :422`). `loadSurrogateModels (:880)` 가 response 문자열로만 행을 맞추고 심볼은 로드마다 `r1..` 재부여. DV 는 그 Builder 의 `parameter` 1개에서 온다. `performMorphing`·Preview 는 `m_modelInfoJsonPath` 1개를 읽는다.
- Deck 2~ 는 Builder 2개 (A 의 model1·model2, B 의 model3) 를 한 최적화에서 써야 한다.

범위
- 건드림: `DashOptimizer` 의 surrogate 행 모델 (`SurrogateModelInfo` 에 ModelRef 추가), `saveSettings`·`loadSurrogateModels`·`loadSurrogateModelsFromJson`·`loadDesignVariablesFromJson`, `DashOptimizerWidget::populateSurrogateTable` (행 추가 = Builder 콤보 + 모델 콤보), `DashOptimizerPresentationModel::selectModelBuilderFolder` (삭제), Preview·`performMorphing` 의 model_info 선택
- 안 건드림: 프로세스 호출 (4.2), 목적·제약식 편집, optimum.json 읽기

변경
- 행 = `{ set, model_id, response, model, symbol }`. 행 추가 UI 에서 Builder Set → usable 모델 선택. `symbol` 은 행 추가 때 발급하고 저장값을 유지, 삭제해도 재부여하지 않는다.
- DV = 참조 모델들의 `parameter` 를 합치되 라벨 집합이 다르면 Run 거부 + 사유. 모든 참조 모델의 originRecord Geometry Set id 가 같아야 Preview·Morphing 이 가능하고, 다르면 Preview 비활성 + 사유.
- `modelBuilder {set, name}` 단일 참조는 "기본 Builder" (DV·Preview 의 출처) 로 남기고 행마다 `set` 을 둔다. `selectModelBuilderFolder` 의 이름 일치 추정 삭제.

기대
- Builder 2개의 모델 3개를 행으로 추가·저장·재열기해 같은 행·심볼이 복원된다 (GUI)
- 단위 테스트 (설정 round-trip, DV 라벨 불일치 거부, v1 항목 빈 선택)

Related: 선행 #722·0.1·2.3. 후속 4.2. #726 의 Optimizer 재적용 정리와 조율.

### 4.2 run-optimization 호출을 <OptSet.json> <OutputDir> 로 바꾸고 path 를 실행 직전 기록한다

현상
- `runOptimization` 이 `run-optimization <trainedModelPath> <json> --output-dir <dir>` 를 조립한다 (`DashOptimizer.cpp:258`). `trainedModelPath` 는 `m_activeModelBuilderFolder` 의 이름에서 만든다 (:234~240).
- 성공 시 `optimization_log/convergence_history.png` 를 기대하지만 DeepOpt 는 `<output_dir>/convergence_history.png` 를 쓴다 (`utils.py:452`).

범위
- 건드림: `runOptimization` 의 argv 와 실행 직전 `trained_surrogate_model[].path` 기록, `onJobFinished` 의 png 경로
- 안 건드림: 설정 형식 (4.1), DeepOpt (4.3)

변경
- Run 직전 각 행의 `path` 를 `DashModelBuilderReference(set).modelDir(model_id)` 로 다시 써 저장한 뒤 `run-optimization <json> --output-dir <dir>`. 해석 실패 행이 있으면 저장 없이 거절 (#722 의 거부 패턴).
- png 경로를 DeepOpt 출력에 맞춘다.

기대
- argv 에 Builder 디렉터리 인자가 없다. 삭제된 Builder 를 참조한 행이 있으면 Run 이 사유와 함께 멈춘다 (GUI)
- 종료 후 convergence 그림이 표시된다

Related: 선행 4.1·4.3.

### 4.3 DeepOpt run_optimization: trained_model_path 제거, _build_response_paths 를 path 로 교체

현상
- `run_optimization(trained_model_path, optimization_json_path, output_dir)` (`main.py:601~623`). `MainOptimizer` → `prepare_problem_definition` → `_build_response_paths` (`problem_setup.py:461~484`) 가 `{path}/{response}/**/*.pt` 를 모아 `_get_model_score` 최저 파일을 고르고 `item["model"]` 은 무시한다.
- 예외를 로그만 하고 종료 코드 0 (:622).

범위
- 건드림: CLI 시그니처, `MainOptimizer.__init__`, `_build_problem`, `_build_response_paths`, `prepare_problem_definition`/`prepare_rbdo_problem_definition` 의 경로 인자, `pred_surrogates` 호출부 (0.2 의 `load_model`)
- 안 건드림: 최적화 알고리즘, optimum.json 형식, `run-fitting-lge-spring` (별도 경로, 그대로)

변경
- `run_optimization(optimization_json_path, output_dir)`. 심볼 → `item.path` 매핑으로 `response_paths` 조립. 항목에 `path` 가 없거나 파일이 없으면 즉시 실패.
- 모델 타입은 `item.model` (GUI 가 type 을 넣음) 으로 `load_model(path, type)`. 경로 문자열 추정 삭제.
- 실패 시 비정상 종료 코드.

기대
- 샘플 OptSet (Builder 2개 경로 항목 3개) 으로 문제 정의가 만들어진다 (단위 테스트, 더미 .pt)
- `problem_setup.py` 에 `_get_model_score`·`**/*.pt` glob 이 없다

Related: 선행 0.2. GUI 4.2 와 같은 계약.

## 5. 범위 밖과 확인 사항

- Builder (ND) 의 노드별 예측·vtu 생산은 그림에 검정이라 제외. ND 모델도 D2~D5 에 따라 `{id}/` 에 저장되므로 뒤에 올릴 수 있다.
- 다른 component 응답을 한 XML 에 싣는 topology 분리 (#643 추가 고려 1) 는 1.2 의 제약으로 두고 별도 이슈.
- DOE 리샘플링의 모델 참조 (그림 1열의 빨간 점선): `getAvailableModelBuilderSets` (`DashDoeSampler.cpp:325`) 가 Set 이름만 나열하고 선택값을 쓰는 곳이 없다 (Space-filling 만 동작). #684 가 `ModelRef` 를 요청 키로 채택하면 끝나므로 본 Epic 에 이슈를 두지 않는다.
- Runner 의 다중 Builder 선택은 그림에 없어 Builder 1개 유지. 항목 형식은 Optimizer 와 같아 뒤에 열 수 있다.
- 확인 필요 1: D1 의 "같은 component" 제약으로 1차 범위가 충분한지 (Deck 1 의 y1·y2 가 다른 part 일 수 있는지).
- 확인 필요 2: D3 에서 status·error 를 Set json 에서 빼는 결정. 현재 DeepOpt 가 Set json 에 쓰고 GUI 가 폴링하는 구조를 model_info 로 옮기는 것이라 2.3·2.4 가 함께 바뀐다.
- 확인 필요 3: #724 와 3.1 의 선후. #724 가 먼저면 3.1 은 그 키에 model_id 만 싣는다.
