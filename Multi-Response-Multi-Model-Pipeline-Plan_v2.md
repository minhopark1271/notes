# 다중 응답·다중 모델 파이프라인 — 공통 계약 v2 와 작업 계획 (개정)

> 관련 Issue: 발행 전 (독립 결함 수정 1건 + Epic 하위 14건 초안). 선행 #722, 접점 #724 · #643 · #650 · #684 · #726 · #741.
> 상태: **원안 검토·재검토를 반영한 개정 설계안** — 2026-10-11. GUI origin/dev `a076fde7` 및 PR #722 브랜치, DeepOpt `a4222b6` 기준. 구현 착수 시 좌표와 선행 PR 상태를 재확인한다.
> 원안: [Multi-Response-Multi-Model-Pipeline-Plan](Multi-Response-Multi-Model-Pipeline-Plan.md). 원안 대비 보강 4건 (모델 파일 경로, `trained_type`, `substep`, 라벨 기준 입력 매핑) 과 독립 결함 이슈 1건 (P6) 을 더하고, 수명주기·버전 체계로의 확장은 넣지 않았다.
> 출처: `dashopti_project_unit_v1.drawio` 의 빨간 항목.
> 해상도: #740 하위 이슈 양식 (`현상 / 범위 / 현재 구조 / 변경 / 기대 / Related`).

## 1. 조사로 바뀐 전제

| 그림의 전제 | 실제 코드 |
|---|---|
| Preprocessor 가 y 하나를 y.xml 로 쓴다 | 응답 목록은 이미 받지만 응답마다 XML 1개 (`DashAnalysisLauncher::processResults` 요청 루프, `DashResultBatch::outputFileName`). 응답 텐서 키는 `sanitizeString(name)`, `y` 키 없음 |
| Builder Configuration 단수 | `Configuration` 은 모델 타입을 키로 한 객체. 같은 타입 2개 불가 (`TrainingPlanError::DuplicateModel`). 응답별 reduction·transformation 은 `Data Label.Output` 에 이미 있음. 단, reload 가 transformation 을 버리고 DeepOpt 는 transformation 을 읽지 않음 |
| 마지막 학습본만 남음 | DeepOpt 가 `{out}/{response}/{Type}_{err}` 로 쓰고 `errors[response]` 를 1D run 마다 초기화, Smart 모드는 최적 외 삭제. 소비자는 첫 glob 일치를 집음 |
| Runner Output response 단수 | 이미 배열. 1D 는 전 항목, ND 는 `[0]` 만 실행 (DeepOpt `main.py:473`). `set` 은 절대경로. 결과 CSV 는 append 라 성공 실행끼리도 행이 쌓임 (`main.py:89`) |
| Optimizer 가 `model` 키로 모델 선택 | DeepOpt `_build_response_paths` 가 `model` 을 무시하고 `{path}/{response}/**/*.pt` 중 최저 오차 파일을 고름. 로더 타입은 경로 문자열의 `ANN_`/`MLP_`/`BNN_` 로 추정 (`pred_surrogates.py:327`) |
| set + model_id 참조 | `model_id` 는 두 레포 어디에도 없음. #722 가 Runner·Optimizer 의 Builder 참조를 `modelBuilder {set: setId, name}` 으로 바꾸는 중 (미머지) |

추가로 확인한 사실
- `sanitizeString` 이 공백·`/`·`\`·`:` 등을 모두 `_` 로 접는다 (`DashUtils.cpp:18~`). DeepOpt 의 XML dict 파싱은 중복 키를 조용히 덮어쓴다 (`xml_parser.py:75`).
- 학습 입력 배열 순서는 `input_labels.keys()` 순서다 (`xml_parser.py:120`). 그 키는 GUI `QJsonObject` 가 사전순으로 쓴 것이고 Runner·Optimizer 쪽도 같은 사전순이라 현재는 일치한다. 명시 계약은 없다.
- Smart 는 응답별로 후보를 학습한 뒤 우승 모델을 고르고 나머지를 삭제한다 (`smart_trainer.py:75~78`). 선택 키 `Smart` 만으로는 로더를 정할 수 없다.

열린 작업과의 접점: #722 (Builder 참조 setId, 선행), #724 (Runner Output Response 영속 분리), #643 1차 (Set 단위 XML, 1.2 가 흡수), #650 (산출물 버전·최신성, 본 계획은 침범하지 않음), #684 (SurrogatePredictor, `ModelRef` 를 채택할 후속), #727 (#737, Set 파일 네임스페이스 공유).

## 2. 공통 규격 (D1~D9)

### D1. 응답은 데이터셋 XML 의 텐서 키로 식별한다
- 일반 Launcher Set 1회 Preprocess = XML 1개, 샘플 dict 에 응답 텐서 N개. KPI·BORE/BOSS 의 별도 XML 경로는 통합 대상에서 제외.
- 키 생성은 기존 `sanitizeString(name)` 유지. 변환 후 응답 키 중복, 입력 파라미터 키와의 충돌, `node_location`·`connectivity` 등 예약 키 충돌은 쓰기 전에 거부한다. 자동 접미사·덮어쓰기 없음. 같은 응답 이름의 다른 시점도 키 충돌로 거부. DeepOpt 도 중복 dict 키를 거부한다.
- `model_info.selected_responses` = 배열. 항목 `{ key, component, load_step, substep, name, file_name }`. 시점은 `ResultTimeRef` 의 step·substep 을 손실 없이 싣는다. `key` 는 샘플 텐서 키와 같다.
- 1차 제약: 한 XML 의 응답은 같은 component. 다른 component 는 시작 전에 거부 (topology 슬롯이 샘플당 1개). 다중 component 는 #643 후속.
- 파일명은 `{LauncherSet}.xml`. 재실행은 같은 파일을 교체한다.

### D2. 모델은 (Builder setId, model_id) 로 식별하고 선택 키와 학습 키를 구분한다
- 참조 객체 `{ set: <Builder setId>, model_id }`. 이름·타입·폴더명·절대경로는 참조 키가 아니다.
- `model_id` 는 Builder Set 안에서 유일한 `model{N}`. Set json 의 `modelSeq` 로 발급, 삭제 후 재사용 없음.
- `type` = 사용자가 고른 알고리즘 키 (Smart 포함). `trained_type` = 실제 학습된 모델 키로 DeepOpt 가 산출물과 함께 기록. 일반 모델은 둘이 같고 Smart 는 `trained_type = RF|MLP|BNN|…`. 로더와 1D/ND 구분 (`isNDModel`) 은 `trained_type` 으로 정한다.
- 외부 엔진 입력에는 실행 직전 해석한 절대 모델 파일 경로 `path` 와 `trained_type`·`input_order` 를 항목에 덧붙인다 (#722 가 Runner `Output Response[].set` 에 쓰는 방식). DeepOpt 는 그것만 읽고 set·model_id 의 의미를 모른다.

### D3. ModelBuilder_{Set}.json v2
```jsonc
{
  "setId": "…", "variant": "Sim", "modelSeq": 2,
  "Data Label": {
    "Dataset": "<abs xml>",
    "Input":  { "dv1": { "reduction": "None" }, "dv2": { "reduction": "None" } },
    "Output": { "stress": { "reduction": "Max", "transformation": "None" } }
  },
  "Configuration": [
    { "id": "model1", "response": "stress", "type": "Smart", "options": {}, "run": true },
    { "id": "model2", "response": "stress", "type": "RF",    "options": {}, "run": false }
  ]
}
```
- `Configuration` 은 행 배열. 행마다 `id`·`response`·`type`·`options`·`run`. 같은 type 여러 행 허용, 옵션은 행 소유.
- `status`·`error` 는 Set json 에 쓰지 않는다 (D5).
- transformation 은 필드만 유지하고 계산은 미구현 (5.1). reload 가 값을 버리는 결함은 2.1 에서 고친다.

### D4. 산출물 디렉터리와 path 의 의미
- 최종 산출물 = `{ModelBuilder_Set}/{model_id}/`. 모델 파일 `model.pt`, scaler·구조 설정·ND 부속 파일은 같은 디렉터리.
- manifest 의 `path` 는 **model_info.json 기준 상대 모델 파일 경로** (`model1/model.pt`). 소비 측 실행 항목의 `path` 는 이를 해석한 **절대 모델 파일 경로**. 디렉터리를 `path` 에 넣지 않는다. `modelDir(id)` 는 저장·삭제용, `resolveModelFile(ref)` 는 실행용.
- 재학습은 `{id}/` 를 비우고 다시 쓴다. Smart 후보는 `{id}/candidates/{type}/` 에서 학습하고 우승 파일을 `{id}/model.pt` 로 옮긴다.
- 파일명 오차 접미사, `{response}/{Type}_{err}` 레이아웃, glob 선택, 경로 문자열 타입 추정은 제거.

### D5. model_info.json v2 와 쓰기 책임
```jsonc
{
  "schema_version": 2,
  "parameter": {}, "originRecord": {},
  "data_label": { "Input": {}, "Output": {} },      // 학습 시작 때의 Data Label 스냅샷 (D9)
  "selected_responses": [ { "key": "stress", "component": "part1", "load_step": "1", "substep": "1", "name": "stress", "file_name": "result" } ],
  "models": {
    "model1": { "response": "stress", "type": "Smart", "trained_type": "RF",
                "input_order": ["dv1", "dv2"], "reduction": "Max", "transformation": "None",
                "path": "model1/model.pt", "status": "Done", "errors": { "R2": 0.98, "MAPE [%]": 1.2 }, "message": "" }
  }
}
```
- GUI 는 학습 시작 때 `parameter`·`originRecord`·`data_label`·`selected_responses` 와 `run:true` 행의 `models[id]` 를 `response`·`type`·`reduction`·`transformation`·`status: "In Progress"` 로 초기화하고 이전 `trained_type`·`input_order`·`path`·`errors` 를 지운다. 실행하지 않는 기존 행은 보존.
- DeepOpt 는 완료 때 `trained_type`·`input_order`·`path`·`errors`·`status: "Done"`, 실패 때 `status: "Failed"`·`message` 를 쓴다. 필요한 파일을 모두 저장한 뒤에만 `Done`.
- 상태는 `In Progress → Done | Failed`. GUI 는 프로세스 종료 후 최종 상태 보정 (`In Progress` 잔존 → `Failed`) 을 끝낸 뒤 다음 실행을 허용한다.
- `usable(entry)` = `Done` 이고 `path` 파일 존재. 최상위 `errors`·`selected_response` 는 쓰지 않으며 있으면 v1 로 거부.

### D6. 소비 측 참조 형식
- Runner `Model upload.Output Response[]` = `{ set, model_id, response, model }` + 실행 직전 `path`·`trained_type`·`input_order`. `model` 은 표시용 선택 키. Runner 는 Builder 1개 (`modelBuilder {set, name}`, #722).
- Optimizer `Optimization.trained_surrogate_model[]` = 같은 항목 + `symbol`. 행마다 `set` 이 달라도 된다 (Deck 2~).
- 실행 직전 모든 항목을 해석해 같은 Set json 에 기록한 뒤 프로세스를 띄운다. 하나라도 실패하면 저장 없이 거절 (#722 의 거부 패턴). 영속 선택과 엔진 입력의 분리는 #724 의 결정을 따른다.
- `symbol` 은 행 추가 때 `max+1` 로 발급하고 저장값을 유지한다. 목적·제약식에 쓰인 심볼의 행은 삭제를 거부한다 (식 텍스트의 심볼 토큰 검색). 삭제된 심볼이 식에 남은 채 재발급돼 다른 모델을 가리키는 경우를 막기 위함.

### D7. 하위호환
- v1 데이터셋 (`selected_response` 단수), v1 Set json (타입 키 Configuration), v1 model_info (최상위 `errors`, `schema_version` 없음) 는 변환하지 않고 거부하며 재생성을 안내한다. #368·#685 정책과 같다.
- Runner·Optimizer 설정의 v1 항목 (`model_id` 없음) 은 빈 선택으로 열고 다른 설정은 보존한다. 열기만으로 파일을 덮어쓰지 않는다.
- `schema_version` 은 model_info.json 에만 둔다. 버전 핸드셰이크·미래 버전 처리는 두지 않는다.

### D8. 학습과 소비가 공유하는 입력 계약
- DeepOpt 가 실제 학습 배열을 구성한 라벨 순서를 `models[id].input_order` 에 기록한다. 작성자는 DeepOpt 뿐이다.
- Runner case 와 Optimizer DV 는 `{label: value}` 로 해석한 뒤 모델별 `input_order` 로 배열을 만든다. 누락·중복·비유한 값·차원 불일치는 실행 전 거부.
- 다중 Builder 최적화는 참조 모델들의 `input_order` 라벨 집합이 같은 경우만 지원하며, DV 메타 (기본값·범위·분포) 는 기본 Builder 의 `parameter` 를 따른다. 서로 다른 DOE·DV 의미의 조합은 범위 밖.
- reduction 비교는 대소문자 무시 (`Sum`/`SUM` 결함).

### D9. 재학습·무효화·실행 결과
- Builder Set 하나가 데이터셋·입력 계약 하나를 소유한다. 학습 시작 때 현재 `Data Label` 의 `Input`·`Output` 과 데이터셋 정체성 (`originRecord.dataset` 의 파일명 + producer setId) 을 model_info 의 스냅샷과 비교한다. 다르면 확인창 뒤 `models` 전체와 `{id}/` 디렉터리를 삭제하고 새 스냅샷으로 시작한다. Configuration 행·model_id·modelSeq 는 유지. 취소하면 학습을 중단하고 기존 manifest 와 산출물을 유지한다. 절대경로·표시명은 비교하지 않는다 (프로젝트 이동·Set 개명은 무효화 사유가 아님). 경로가 같고 내용만 바뀐 XML 은 #650 소관.
- 같은 스냅샷에서 일부 행만 재학습하면 그 행만 D5 절차로 바뀐다.
- Builder 는 한 실행에 1D·ND 혼합을 허용하지 않는다. Runner 는 여러 실행의 1D·ND 모델을 함께 선택할 수 있고, 계열별 CLI 를 순차 실행한 뒤 완료를 알린다.
- 실행 실패는 CLI 비정상 종료 코드로 전달한다. GUI 는 자신이 넘긴 명시 결과 경로만 열고 최신 파일 탐색·고정 지연에 의존하지 않는다. Run 시작 때 그 CSV 를 삭제해 이번 실행 결과만 남긴다 (DeepOpt 는 append 유지).
- 1D 결과 CSV = `{RunnerSet}_test_results.csv`, 모델 열 = `{response} [{model_id}]`. ND 결과 = `{output_dir}/{case}/{model_id}/`.

## 3. 이슈 계층

```
[P6] DeepOpt 실행 실패·결과 경로 결함 수정 (독립)
[Epic] 다중 응답·다중 모델 파이프라인
├─ 0 공통 규격
│  ├─ 0.1 GUI: 모델 참조·model_info v2 판독·model_id 발급 (DashModelBuilderArtifact/Reference)
│  └─ 0.2 DeepOpt: model_id 디렉터리, models 항목 쓰기, trained_type 기반 로더
├─ 1 Preprocessor
│  ├─ 1.1 selected_responses 배열과 Launcher Output Response 영속
│  └─ 1.2 XML 하나에 응답 N개 + 키 충돌 검증 (#643 1차)
├─ 2 Builder
│  ├─ 2.1 Configuration 행 배열·행별 옵션·transformation 복원
│  ├─ 2.2 다중 응답 파싱, 학습 시작 manifest, Data Label 스냅샷 무효화
│  ├─ 2.3 모델별 상태·오차·삭제
│  └─ 2.4 DeepOpt train: 행별 학습, {id}/ 출력, trained_type·input_order 기록
├─ 3 Runner
│  ├─ 3.1 모델 참조 저장·복원
│  ├─ 3.2 선택 모델 전체 실행과 결과 집계
│  └─ 3.3 DeepOpt test-model-1d/nd: 명시 경로·input_order, ND 전 항목
└─ 4 Optimizer
   ├─ 4.1 여러 Builder 모델 선택·입력 계약·심볼
   ├─ 4.2 run-optimization 호출과 실행 직전 해석
   └─ 4.3 DeepOpt run_optimization: path·trained_type·input_order
```

분리 기준: 기존 결함인지가 아니라 확장과 독립적으로 수정·검증·배포할 실익이 있는지. 그 기준으로 P6 만 독립이고, Smart 타입 추정·transformation reload 유실·키 충돌은 기존 결함이지만 해당 구현 이슈에 흡수한다.

선행 관계
```
P6 (독립, 언제든)
#722 머지
 └─ 0.1 ─┬─ 1.1 ─ 1.2
         ├─ 2.1 ─┬─ 2.2 (1.1 뒤)
         │       └─ 2.3 (2.4 뒤)
         ├─ 3.1 (#724 조율) ─ 3.2
         └─ 4.1 ─ 4.2
0.2 ─┬─ 2.4 (2.1 과 같은 계약)
     ├─ 3.3 (3.2 와 같은 계약)
     └─ 4.3 (4.2 와 같은 계약)
```
DeepOpt 이슈 (0.2·2.4·3.3·4.3·P6 일부) 는 DashOpti_DeepOpt 에 발행하고 GUI 이슈에서 링크한다. 같은 계약의 쌍은 머지 시점을 맞춘다. DeepOpt tests 에 샘플 Set json·model_info·OptSet 한 벌을 두고 양쪽이 같은 fixture 를 읽는다.

## 4. 이슈 초안

### P6 DeepOpt 실행 실패를 종료 코드로 전달하고 GUI 가 명시 결과 경로만 연다

현상
- `train_model_*`·`test_model_*`·`run_optimization` 이 예외를 로그만 하고 종료 코드 0 (`main.py:228, 324, 622`). GUI 는 성공으로 본다.
- Runner `onPredictionSucceeded` 가 500 ms 뒤 가장 최신 `*.csv` 를 연다. 1D CSV 는 append 라 성공 실행끼리도 행이 쌓인다 (`main.py:89`).
- Optimizer 가 `optimization_log/convergence_history.png` 를 기대하지만 DeepOpt 는 `<output_dir>/convergence_history.png` 를 쓴다 (`utils.py:452`).

범위
- 건드림: DeepOpt 서브커맨드 5개의 예외 처리, `DashModelRunner::onPredictionSucceeded`·`run1DPrediction` 의 결과 경로, `DashOptimizer::onJobFinished` 의 png 경로
- 안 건드림: 설정 형식, 모델 탐색 (0~4 절), `[RESULT]` 파싱 (#684)

변경
- DeepOpt: 예외 시 비정상 종료 코드. GUI 는 종료 코드 ≠ 0 을 실패로 표시.
- Runner: 결과 CSV 경로를 `{RunnerSet}_test_results.csv` 로 고정해 CLI 에 넘기고, Run 시작 때 그 파일을 삭제한다. 종료 후 그 경로를 연다. 지연·최신 파일 탐색 제거.
- Optimizer: png 경로를 DeepOpt 출력에 맞춘다.

기대
- 예측·최적화 실패가 정상 완료로 보이지 않는다. 같은 case 를 두 번 Run 해도 CSV 에 이번 실행 행만 있다.
- `DashModelRunner.cpp` 에 최신 CSV 탐색과 고정 지연이 없다.

Related: 독립 결함 수정. 3.2·3.3·4.2 가 이 규칙 위에 다중 모델 결과를 올린다.

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
- `DashModelBuilderArtifact` 에 추가: `struct ModelRef { QString set, modelId; }` 와 json 읽기/쓰기 (키 `set`·`model_id`), `struct ModelEntry { id, response, type, trainedType, inputOrder, reduction, transformation, path, status, errors, message }`, `readModels(modelInfoRoot, error)` — `schema_version` 없음·최상위 `errors`·`models` 없음·필수 키 누락은 "<artifact> cannot be used: …" 로 거부. `usable(entry)` = Done 이고 `path` 파일 존재.
- `DashModelBuilderReference` 에 `modelDir(modelId)` (저장·삭제용 절대 디렉터리), `resolveModelFile(ref)` (실행용 절대 파일 경로, 해당 Builder 의 해당 모델 디렉터리 안인지 검증), `LoadedArtifact.models`. `issueModelId(setRoot)` 는 `modelSeq` 를 올려 `model{N}` 을 돌려준다.
- `parseSurrogateModelErrors` 의 ErrorMap 생성을 `ModelEntry` 목록에서 하도록 교체.

기대
- 테스트: ModelRef round-trip, v1 model_info 거부 사유, models 판독·usable 판정, 상대→절대 파일 경로 해석과 Builder 밖 경로 거부, modelSeq 가 삭제 뒤에도 증가
- Runner·Optimizer 가 v1 `errors` 를 직접 읽는 코드가 남지 않는다 (3.1·4.1 에서 치환)

Related: 선행 #722. 후속 1~4 절 전부. #684 는 `ModelRef` 를 요청 키로 채택한다.

### 0.2 DeepOpt: 산출물 계약 v2 — model_id 디렉터리, models 항목 쓰기, trained_type 기반 로더

현상
- 산출물이 `{out}/{response}/{Type}_{err:.8f}[.pt|/]` 이고 (`base_trainer.py:100`, `ann_trainer.py:397`, `result_saver.py:151`), 모델 식별이 파일명 접미 오차다. `pred_surrogates.detect_model_type` 이 경로 문자열로 타입을 추정한다 (:327).
- model_info.json 은 `errors` 만 쓴다 (`run_train_1d.py:144`, `result_saver.py:40`). Smart 는 우승 외 후보를 파일명 규칙으로 지운다 (`smart_trainer.py:119`).

범위
- 건드림: `source/models/oned/*trainer.py` 의 저장 경로, `smart_trainer.py` 의 후보 배치·정리, `trainer_utils/result_saver.py`, `run_train_1d._save_model_info_json`, `optimize/pred_surrogates.py` 로더, 신규 `source/artifact.py` (계약 1곳)
- 안 건드림: 학습 알고리즘, CLI 서브커맨드 (2.4·3.3·4.3)

변경
- `artifact.py`: `model_dir(output_dir, model_id)`, `write_model_entry(model_info_path, model_id, patch)` (지정 키만 갱신, 다른 항목 보존), `load_model(path, trained_type)` — 경로 추정 없음, 모르는 타입은 실패. 타입별 필요한 부속 파일 (scaler·config) 은 로더가 같은 디렉터리에서 연다.
- 트레이너는 `model_dir` 아래에 `model.pt` 와 부속 파일을 쓴다. 파일명 오차 접미사 제거. Smart 는 `{id}/candidates/{type}/` 에서 학습하고 우승 파일을 `{id}/` 로 옮긴 뒤 `trained_type` 을 기록한다.
- `_save_model_info_json` / `save_model_info_json` 을 `write_model_entry` 로 교체. `errors[response] = {}` 초기화 제거. 필요한 파일을 다 쓴 뒤에만 `status: Done`.

기대
- 두 트레이너와 Smart 모두 `{out}/{id}/model.pt` 를 남기고 `models[id]` 의 `trained_type`·`input_order`·`path`·`status`·`errors` 를 쓴다 (단위 테스트: 임시 디렉터리 round-trip, Smart 가 RF·MLP·BNN 을 고르는 fixture)
- 작업 트리에 `_get_model_score`·`detect_model_type`·`{Type}_*` glob 이 없다 (3.3·4.3 이 소비처를 지운 뒤)

Related: GUI 0.1 과 같은 계약. 2.4·3.3·4.3 선행.

### 1.1 XML model_info 를 selected_responses 배열로 쓰고 Launcher 의 Output Response 저장을 Config 로 옮긴다

현상
- `DashResultXmlWriter::writeModelInfoToXml` (`DashResultXmlWriter.cpp:971`) 이 `selected_response` 단수 dict 를 쓴다. 호출부 `DashAnalysisLauncher.cpp:1202` 와 KPI 경로 5곳 (`DashAnalysisLauncherKPI.cpp`) 이 4종 키를 각자 만든다. substep 은 `load_step` 문자열에 섞여 들어간다.
- Launcher 의 "Output Response" 표는 `DashAnalysisLauncherPresentationModel::saveOutputResponse` (:108) 가 `root["Output Response"]` 를 직접 read-modify-write 한다. `DashAnalysisLauncherConfig` 를 거치지 않고, 읽어 복원하는 코드가 없다.

범위
- 건드림: `writeModelInfoToXml` 시그니처와 본문, `DashAnalysisLauncher.cpp` 의 responseInfo 조립, `DashAnalysisLauncherKPI.cpp` 5곳, `DashAnalysisLauncherConfig` 에 `Output Response` 읽기/쓰기, `saveOutputResponse`, `tests/TestResultXmlWriter.cpp`, `tests/TestAnalysisLauncherConfig.cpp`
- 안 건드림: 샘플 텐서 쓰기, 요청 루프 (1.2), Builder 파서 (2.2)

변경
- `writeModelInfoToXml(doc, root, parameterInfo, analysisType, QList<SelectedResponse>, originRecord)`. `SelectedResponse { key, component, loadStep, substep, name, fileName }` 는 `DashResultTypes.h` 에. `key` = 샘플 텐서 키. 배열 1개도 배열로 쓴다.
- KPI 경로도 같은 구조체로 조립. 4종 키 리터럴은 XmlWriter 1곳.
- `DashAnalysisLauncherConfig::read/writeOutputResponses(root, QList<ResultRow>)`. `saveOutputResponse` 는 이것을 부른다. 위젯 열기 때 표 복원.

기대
- `TestResultXmlWriter` 에 `writeModelInfoToXml` 케이스: 항목 2개 배열, `key` 가 샘플 키와 같음, substep 보존, 빈 목록이면 model_info 생략 유지
- `TestAnalysisLauncherConfig` 에 Output Response round-trip
- 작업 트리의 XML 작성 코드에 `"selected_response"` 문자열이 없다

Related: 선행 0.1 (코드 의존 없음, 규격 참조). 후속 1.2·2.2. #643 과 접점.

### 1.2 Launcher Set 1회 Preprocess 가 XML 1개에 응답 N개를 쓴다 (#643 1차 흡수)

현상
- `DashAnalysisLauncher::processResults` 가 요청마다 `QDomDocument` 를 새로 만들어 (:1124) 전 샘플을 돌리고 저장한다 (:1212). 샘플 파일을 요청 × 샘플 횟수만큼 연다. 파일명은 `{comp}_{step}_{substep}_{name}.xml`.
- `appendSample` 은 샘플당 응답 1개를 쓰고 `responseWritten_` 플래그 1개로 성공을 판단한다. topology 슬롯은 샘플당 1개.
- 키는 `sanitizeString(name)` 이라 `A/B`·`A:B`, 같은 이름의 다른 시점, 입력 파라미터와 동명, 예약 키가 충돌할 수 있다. 지금은 응답당 XML 이라 드러나지 않는다.
- 카탈로그는 `resultRequests[0]` 의 시간으로 1회 초기화된다 (:1029).

범위
- 건드림: `processResults` 루프 구조, `DashResultProcessor::processSamples`·`appendSample` 의 응답 목록 인자, 시작 전 키 검증기 (신규, 순수 함수), `DashResultBatch::outputFileName`, Builder 의 Launcher 폴더 XML 나열, DeepOpt `xml_parser` 의 중복 키 거부, `tests/TestResultProcessor.cpp`, `tests/TestResultBatch.cpp`
- 안 건드림: circularity 의 BORE/BOSS 병합 (별 XML 유지), KPI 경로, 다른 component 응답의 topology 분리

변경
- 루프 반전: 샘플마다 파일 1회 열기 → 응답 N개 `GetFieldOutputVtk` → 같은 샘플 dict 에 N개 텐서. 응답별 성공 플래그, 하나라도 Missing 이면 샘플 제외.
- 시작 전 검증 (순수 함수): 정규화 키의 중복, 입력 키·예약 키 충돌, component 불일치를 거부하고 원래 이름·시점·충돌 키를 표시. 기존 XML 은 변경하지 않는다. 시점이 다른 응답은 요청별 카탈로그 조회.
- 파일명 `{LauncherSet}.xml` 1개. `model_info.selected_responses` 에 N항목 (1.1). DeepOpt 는 중복 dict 키 XML 을 학습 전에 거부.

기대
- 응답 2개 Preprocess 가 XML 1개를 만들고 Builder Output 표에 라벨 2개가 뜬다 (GUI)
- `TestResultProcessor`: 응답 2개 중 하나 Missing 인 샘플 제외, 파일 열기 횟수 = 샘플 수
- 검증기 단위 테스트: `A/B`·`A:B`, 같은 이름 다른 시점, 입력·응답 동명, 예약 키, component 불일치 거부

Related: 선행 1.1. #643 1차의 구현. 2차 (uuid 확인·이어쓰기·HDF5) 는 #643 에 남긴다.

### 2.1 ModelBuilder Set json 의 Configuration 을 model_id 행 배열로 바꾼다

현상
- `Configuration` 이 모델 타입을 키로 한 객체 (`DashModelBuilder.cpp:648, 768`). 같은 타입 두 행은 `DuplicateModel` (`DashModelBuilderPresentationModel.cpp:370`) 로 막힌다. 옵션 패널은 타입당 1페이지 (`m_configWidgets[modelName]`, `DashModelBuilderWidget.cpp:777~888`).
- `loadDataLabelConfig` 가 Output 의 `transformation` 을 읽지 않아 reload 때 값이 사라진다. `ModelBuilderConfigHelper::parse*` 는 transformation 을 읽지만 호출처가 없다.
- 상태 폴링과 `onModelStatusUpdated` 가 모델 콤보 텍스트 (타입) 로 행을 찾는다.

범위
- 건드림: `onTrainingStartButtonClicked` 의 Configuration 조립, `loadDataLabelConfig`, `buildTrainingStartPlan`·`TrainingRowInput`, `DashModelBuilderWidgetBase::addModelRow`·`getModelConfiguration`·`updateConfigUI`, `restoreConfigurationUI`·`onStartTrainingClicked`, `ModelBuilderConfigHelper` (죽은 parse 정리), MCU 변형의 Configuration 쓰기 (`DashModelBuilderMCU.cpp:511~555, 729~760`)
- 안 건드림: model_info.json (2.2), 상태·삭제 (2.3), DeepOpt (2.4), transformation 계산 (5.1)

변경
- Configuration = 배열, 행 `{id, response, type, options, run}`. 새 행은 `issueModelId` 로 발급. `TrainingRowInput` 에 id. `DuplicateModel` 삭제.
- 옵션 페이지를 행별 인스턴스로 (`m_configWidgets[id]`). 타입을 바꾸면 그 행의 페이지를 새로 만든다.
- `status`·`error` 키를 쓰지 않는다. 폴링·행 찾기는 2.3.
- `loadDataLabelConfig` 가 `transformation` 을 읽어 Output 표를 복원한다. 1D/ND 혼합 선택은 시작 전에 거부 (현재는 첫 행으로 서브커맨드를 정함, :841~843).

기대
- 같은 타입 두 행을 추가·학습 시작·재열기해도 행 2개와 각자 옵션이 복원된다 (GUI). transformation 선택값이 reload 뒤 유지된다.
- 단위 테스트 (`buildTrainingStartPlan`): id 있는 행만 Configuration 에, run·options 행별 보존, 혼합 거부
- 작업 트리에 `DuplicateModel` 이 없다

Related: 선행 0.1. 후속 2.2·2.3. 같은 계약 2.4.

### 2.2 Builder 가 selected_responses 를 읽고 model_info v2 를 기록하며 Data Label 변경 시 모델을 무효화한다

현상
- `parseModelInfoStream` 이 `selected_response` 단수 (`:2036`) 를 읽고 `readSelectedResponseFromStream` (`:1859`) 은 flat string dict 만 받는다. 학습 시작 시 그대로 복사한다 (`:809`).
- 학습 시작 시 기존 model_info 를 읽어 보존하면서 `parameter`·`originRecord` 만 새 데이터셋으로 덮어쓴다 (`:782~830`). 옛 산출물과 새 메타가 섞인다. 모델별 메타는 없다.
- `DashXmlTailLocator` 의 꼬리 파싱이 `parameter`/`selected_response` 구조를 가정한다.

범위
- 건드림: `parseModelInfoStream`·`readSelectedResponseFromStream`, 학습 시작의 model_info 쓰기 (순수 함수로 분리), `DashXmlTailLocator.h` 의 가정·예산, Output 표 라벨 ↔ `selected_responses[].key` 대응, `DashModelBuilderMCU.cpp:617~676` 의 같은 복사
- 안 건드림: errors 읽기 (2.3), DeepOpt 쓰기 (2.4)

변경
- `selected_responses` 배열을 `QList<SelectedResponse>` 로 읽는다. 단수 키는 거부 ("dataset cannot be used: v1 selected_response").
- 학습 시작 전 D9 비교: 현재 `Data Label.Input/Output` 과 `originRecord.dataset` 정체성이 model_info 스냅샷과 다르면 확인창. 확인 시 `models` 전체·`{id}/` 삭제, 취소 시 중단. 행·model_id·modelSeq 유지.
- D5 대로 `run:true` 행의 `models[id]` 를 `In Progress` 로 초기화 (이전 `trained_type`·`input_order`·`path`·`errors` 제거), 실행하지 않는 행 보존, `data_label` 스냅샷·`schema_version: 2` 기록. 최상위 `errors`·`selected_response` 는 쓰지 않는다. v1 파일은 D7 대로 거부하고 새 manifest 로 시작한다.

기대
- 단위 테스트 (XML 파서): 배열 2개 읽기, 단수 키 거부, 꼬리 파싱 예산 안에서 성공
- 단위 테스트 (manifest 순수 함수): In Progress 초기화·보존, 스냅샷 불일치 판정 (절대경로·표시명 차이는 불일치 아님)
- 데이터셋을 다른 Launcher Set 으로 바꾼 뒤 학습하면 옛 모델이 usable 로 남지 않는다 (GUI)

Related: 선행 1.1·2.1. 후속 2.3·3.1·4.1. 내용만 바뀐 같은 경로 XML 은 #650.

### 2.3 모델 상태·오차·삭제를 model_info.models[id] 기준으로 바꾼다

현상
- 상태는 Set json `Configuration[type].status` 폴링 (`checkModelStatusInternal`), 오차는 `errors[resp][type][metric]` (`loadTrainedModelInfo :1163`, `refreshTrainedModelInfo :1287` 가 타입별 최저 MAPE 만 남김). 산출물 목록은 `{resp}/{Type}_{err}` 스캔 (`getTrainedModelList :2193`, `getTrainedModelFolderNames :2336`). 삭제는 `deleteTrainedModel` 이 `errors` 키와 `{model}*` 파일을 지운다.
- 종료 처리는 500 ms·1000 ms 지연 콜백에서 상태를 다시 읽고 `finalizeStaleStatuses` 로 보정한다 (`:1329~1372, 1516~1566`). 단일 Job 가드 (`:441`) 는 중복 기동만 막는다.

범위
- 건드림: 위 함수들, `finalizeStaleStatuses`, `onModelStatusUpdated`·`aboutToRemoveModelRow` (행 → id), `addModelRowExtras`, `getTestDatasetFiles` 경로, MCU 의 `updateModelStatusFromOutputDir`
- 안 건드림: Set json 형식 (2.1), DeepOpt

변경
- 폴링 대상 = `models[id].status`. 행은 id 로 찾는다. 프로세스 종료 후 최종 보정 (`In Progress` 잔존 → `Failed`) 을 끝낸 뒤에 다음 실행을 허용한다.
- 오차 표시 = `models[id].errors`, `trained_type` 열 추가. 타입별 최저값 선별 (`knownModelTypes`, :1162~1225 상당) 삭제.
- 산출물 목록 = `models` 항목. 삭제 = `models[id]` 제거 + `{id}/` 삭제. 실패하면 삭제 완료로 표시하지 않는다.

기대
- 두 행 학습 후 행별 상태·오차·실제 타입이 나오고, 한 행 삭제 뒤 다른 행과 디렉터리가 남는다 (GUI)
- `DashModelBuilder.cpp` 에 최상위 `"errors"` 읽기와 `_*.pt` glob 이 없다

Related: 선행 2.1·2.2·2.4.

### 2.4 DeepOpt train: Configuration 배열과 model_id 산출물 계약을 적용한다

현상
- `train_model_1d` / `train_model_nd` (`main.py:143, 234`) 가 `Configuration` dict 를 순회하고 행의 `response` 를 버린 채 (:198, :287) 모든 Output 라벨을 학습한다. 상태는 Set json 에 `_update_json_status` (:57).
- `build_1d` 가 reduction 을 `"SUM"` 으로 비교해 `"Sum"` 이 무시된다 (:139). 입력 배열 순서는 `input_labels.keys()` 순서이고 어디에도 기록되지 않는다 (:120).

범위
- 건드림: 두 서브커맨드의 설정 해석·루프, `_update_json_status` (삭제), `XMLTrainingDataBuilder` 의 reduction 정규화와 입력 순서 반환, 트레이너 호출 (0.2 의 `model_dir`·`write_model_entry`)
- 안 건드림: 모델 알고리즘, transformation 계산 (5.1), 테스트·최적화 서브커맨드

변경
- `run:true` 행마다 `row.response` 하나를 학습한다. 출력 = `model_dir(output_dir, row.id)`. 학습에 쓴 라벨 순서를 `input_order` 로, 실제 모델 키를 `trained_type` 으로 `write_model_entry` 에 기록. Set json 은 읽기만.
- reduction 비교는 대소문자 무시, 모르는 값은 실패.
- 예외 시 `status: Failed`·`message` 기록 + 비정상 종료 코드 (P6).

기대
- 샘플 Set json (행 2개, 같은 타입) 으로 `{out}/model1/`·`{out}/model2/` 와 `models` 2항목이 생긴다 (단위 테스트, 합성 XML)
- Smart 행의 `trained_type` 이 우승 모델 키이고 `input_order` 가 학습 배열 순서와 같다. `Sum` 이 합계를 계산한다.

Related: 선행 0.2. GUI 2.1·2.2 와 같은 계약.

### 3.1 Runner Output Response 항목을 {set, model_id} 로 바꾸고 모델 단위 행으로 복원한다

현상
- (#722 기준) `DashModelRunnerConfig::writeOutputResponses(root, builderAbsPath, (response, model) 쌍)` 가 `{set: 절대경로, response, model}` 를 쓰고 `readSavedSelection` 은 (response, model) 쌍만 되읽는다. 표는 응답당 1행 + 모델 콤보 (`SurrogateTableController::createRow`).
- v2 에서는 응답당 모델이 여러 개이고 같은 타입도 여러 개라 (response, type) 로는 모델을 특정할 수 없다.

범위
- 건드림: `DashModelRunnerConfig` 의 Output Response 읽기/쓰기, `SavedSelection`, `DashModelRunnerWidget::populateSurrogateTable`·`onRunAIPredictionClicked`, `groupCheckedPairs`, `parseSurrogateModelErrors` 소비, `tests/TestModelRunnerConfig.cpp`
- 안 건드림: `modelBuilder {set, name}` (#722 그대로, Builder 1개), 실행 (3.2), 예측 항목 생성·삭제 (#741)

변경
- 항목 = `{ set, model_id, response, model }`. 실행 직전 `resolveModelFile(ref)` 의 절대 파일 경로와 `trained_type`·`input_order` 를 같은 항목에 기록 (#722 가 `set` 을 재해석하던 자리). 디렉터리를 `path` 로 넘기지 않는다.
- 표 = usable 모델당 1행 (체크, id, response, 선택 타입, 실제 타입, metrics). 모델 콤보 삭제. 복원은 model_id 로 체크.
- 체크 변경 시점 저장은 #724 의 결정을 따른다. 본 이슈는 Run 시점 쓰기만 바꾸고, #724 가 먼저 머지되면 그 키에 model_id 를 싣는다.

기대
- `TestModelRunnerConfig`: 항목 round-trip, v1 항목 (model_id 없음) 은 빈 선택
- 같은 응답에 RF·MLP 두 모델을 체크·Run·재열기하면 두 행이 체크된 채 복원된다 (GUI)

Related: 선행 #722·0.1·2.3. 조율 #724·#726. 후속 3.2.

### 3.2 Run AI Prediction 이 선택 모델 전부를 실행하고 결과를 model_id 열로 누적한다

현상
- 1D 는 배열 전 항목을 돌리지만 CSV 열이 응답 이름이라 같은 응답의 두 모델이 한 열에 겹친다 (`main.py:432`). ND 는 `Output Response[0]` 만 실행 (:473). ND·1D 가 섞이면 `updateModelUploadConfig` 를 두 번 불러 배열을 교체한다 (#724).
- 예측 항목 (`Prediction Cases`) 은 응답·모델 정보가 없다 (`SharedTypes.h:51`).

범위
- 건드림: `DashModelRunner::run1DPrediction`·`runNDPrediction`, `groupCheckedPairs` 의 계열 분기, 결과 열기 (P6 의 명시 경로 위에)
- 안 건드림: `[RESULT]` 파싱 모듈화 (#684), 예측 항목 정합성 (#741)

변경
- 선택 항목 전체를 한 번 기록한 뒤 (`trained_type` 으로 계열 구분) 1D·ND CLI 를 순차 실행하고 둘 다 끝나면 완료를 알린다. 어느 하나라도 실패하면 전체 성공으로 표시하지 않는다.
- CSV 열 `{response} [{model_id}]`, 파일 `{RunnerSet}_test_results.csv` (P6 의 Run 시작 삭제 규칙 유지). ND 결과는 `{case}/{model_id}/` (3.3 과 합의).

기대
- 모델 3개 (1D 2, ND 1), active case 2개 Run 으로 1D CSV 에 case 행 2개·모델 열 2개, ND 출력 디렉터리 2개가 생긴다 (GUI). ND 하나 실패 시 실패로 표시.

Related: 선행 P6·3.1·3.3. #684 가 뒤에 호출부를 모듈로 옮긴다.

### 3.3 DeepOpt test-model-1d/nd: 명시 경로·input_order 로 로딩하고 ND 전 항목을 실행한다

현상
- `test_model_1d` 가 `set/response/{model}_*/model.pt` → `{model}_*.pt` glob 으로 첫 일치를 집는다 (`main.py:394~403`). `test_model_nd` 는 `Output Response[0]` 만 쓴다 (:473~476) 고 `{model}_*/model.pt` glob (:561). case 의 values 는 DV 라벨 순서 가정 없이 그대로 전달된다.

범위
- 건드림: 두 서브커맨드의 모델 해석·루프·출력, case 값 → 모델 입력 재배열 (공통 어댑터), `RunTest1D`·`RunTestNDFromVTU` 의 모델 인자
- 안 건드림: `--with-std` 확장 (#684)

변경
- 항목의 `path`·`trained_type` 으로 `artifact.load_model`. glob 삭제. `trained_type` 이 CLI 계열과 맞는 항목만 처리.
- case 값을 `{label: value}` 로 만들고 항목의 `input_order` 로 재배열. 누락·중복·비유한 값은 실행 전 실패.
- ND 는 ND 항목 전부 순회, 출력 `{output_dir}/{case}/{model_id}/`. CSV 모델 열 `{response} [{model_id}]`, 파일은 GUI 가 넘긴 경로.

기대
- 샘플 config (항목 2개, 같은 응답, 입력 순서 반대) 로 CSV 열 2개가 생기고 각 모델에 올바른 열 순서로 값이 전달된다 (단위 테스트, 더미 모델)
- `main.py` 에 `{model}_*` glob 이 없다

Related: 선행 0.2·P6. GUI 3.2 와 같은 계약.

### 4.1 Optimizer 가 여러 Builder 의 모델을 {set, model_id} 로 선택·저장·복원한다

현상
- (#722 기준) Optimizer 는 Builder 1개를 `modelBuilder {set, name}` 으로 참조하고 `trained_surrogate_model[]` 항목은 `{model, response, symbol}` (`createSurrogateModelJsonArray :422`). `loadSurrogateModels (:880)` 가 response 로만 행을 맞추고 심볼은 로드마다 `r1..` 재부여. DV 는 그 Builder 의 `parameter` 에서. `performMorphing`·Preview 는 `m_modelInfoJsonPath` 1개.
- Deck 2~ 는 Builder 2개 (A 의 model1·model2, B 의 model3) 를 한 최적화에서 쓴다.

범위
- 건드림: `SurrogateModelInfo` (ModelRef·trainedType 추가), `saveSettings`·`loadSurrogateModels`·`loadSurrogateModelsFromJson`·`loadDesignVariablesFromJson`, `DashOptimizerWidget::populateSurrogateTable` (행 추가 = Builder 콤보 + 모델 콤보, 행 삭제 가드), `selectModelBuilderFolder` (삭제), Preview·`performMorphing` 의 model_info 선택
- 안 건드림: 프로세스 호출 (4.2), 목적·제약식 편집기, optimum.json 읽기

변경
- 행 = `{ set, model_id, response, model, symbol }`. Builder Set → usable 모델 순으로 선택. `symbol` 은 `max+1` 발급·저장값 유지. 목적·제약식 텍스트에 쓰인 심볼의 행은 삭제 거부.
- 참조 모델들의 `input_order` 라벨 집합이 다르면 Run 거부. DV 메타는 기본 Builder (`modelBuilder {set, name}`) 의 `parameter`. 모든 참조 모델의 originRecord Geometry Set id 가 같아야 Preview·Morphing 이 가능하고, 다르면 비활성 + 사유.
- `selectModelBuilderFolder` 의 이름 일치 추정 삭제.

기대
- Builder 2개의 모델 3개를 행으로 추가·저장·재열기해 같은 행·심볼이 복원된다 (GUI)
- 단위 테스트: 설정 round-trip, 라벨 집합 불일치 거부, 식에 쓰인 심볼 행 삭제 거부, v1 항목 빈 선택

Related: 선행 #722·0.1·2.3. 후속 4.2. #726 의 Optimizer 재적용 정리와 조율.

### 4.2 run-optimization 호출을 <OptSet.json> --output-dir 로 바꾸고 실행 직전 항목을 해석한다

현상
- `runOptimization` 이 `run-optimization <trainedModelPath> <json> --output-dir <dir>` 를 조립한다 (`DashOptimizer.cpp:258`). `trainedModelPath` 는 `m_activeModelBuilderFolder` 이름에서 만든다 (:234~240).

범위
- 건드림: `runOptimization` 의 argv 와 실행 직전 항목 기록
- 안 건드림: 설정 형식 (4.1), DeepOpt (4.3), png 경로 (P6)

변경
- Run 직전 모든 행을 `resolveModelFile(ref)` 로 해석해 `path`·`trained_type`·`input_order` 를 항목에 기록·저장한 뒤 `run-optimization <json> --output-dir <dir>`. 해석 실패 행이 있으면 저장 없이 거절.

기대
- argv 에 Builder 디렉터리 인자가 없다. 삭제된 Builder 를 참조한 행이 있으면 Run 이 사유와 함께 멈춘다 (GUI)

Related: 선행 P6·4.1·4.3.

### 4.3 DeepOpt run_optimization: trained_model_path 제거, 항목의 path·trained_type·input_order 로 평가한다

현상
- `run_optimization(trained_model_path, optimization_json_path, output_dir)` (`main.py:601~623`). `_build_response_paths` (`problem_setup.py:461~484`) 가 `{path}/{response}/**/*.pt` 중 `_get_model_score` 최저를 고르고 `item["model"]` 은 무시한다. 모든 모델에 같은 `full_x` 를 넘긴다 (:584~586).

범위
- 건드림: CLI 시그니처, `MainOptimizer.__init__`, `_build_problem`, `_build_response_paths`, `prepare_problem_definition`/`prepare_rbdo_problem_definition`, `pred_surrogates` 호출부 (3.3 과 같은 입력 어댑터)
- 안 건드림: 최적화 알고리즘, optimum.json 형식, `run-fitting-lge-spring`

변경
- `run_optimization(optimization_json_path, output_dir)`. 심볼 → `{path, trained_type, input_order}` 매핑. 경로·파일 없음·모르는 타입은 즉시 실패.
- 각 심볼 평가 때 DV 를 `{label: value}` 로 만들고 그 모델의 `input_order` 로 재배열. deterministic·probabilistic 경로 모두 같은 어댑터.
- 실패 시 비정상 종료 코드 (P6).

기대
- Builder 2개의 항목 3개 (입력 순서 반대 모델 포함, Smart → MLP 모델 포함) 로 문제 정의가 만들어지고 더미 로더가 올바른 열 순서로 값을 받는다 (단위 테스트)
- `problem_setup.py` 에 `_get_model_score`·`**/*.pt` glob 이 없다

Related: 선행 0.2·P6. GUI 4.2 와 같은 계약.

## 5. 범위 밖과 후속

### 5.1 transformation 은 미구현으로 유지한다
DeepOpt 가 읽지 않는 현 상태를 유지한다. 이번 범위는 필드 보존과 reload 복원 (2.1) 까지이고, 적용 순서 (reduction → transformation → scaling), 정의역·overflow, Square 의 역변환 조건, 역변환 책임 위치 (Runner·Optimizer·지표·시각화), 오차 계산 공간, 1D·ND 지원 범위는 별도 이슈에서 정한다.

### 5.2 제외
- Builder (ND) 의 노드별 예측·vtu 생산. ND 모델도 `{id}/` 에 저장되므로 뒤에 올릴 수 있다.
- 다른 component 응답의 topology 분리 (#643 후속), 키 충돌 시 자동 ID, 같은 이름 여러 시점.
- 모델별 데이터셋 이력, 옛 학습본 복구, 내용 변경 감지 (#650), 실행 배타성·잠금.
- 입력 라벨 집합이 다른 모델의 최적화 결합, 벡터 DV 펼침, DV 메타 충돌 UI.
- DOE 리샘플링 (#684 가 `ModelRef` 채택), Runner 다중 Builder 선택.

### 5.3 착수 시 확인
- 같은 component·충돌 없는 키라는 1차 제약이 대상 Deck 의 y1·y2 를 충족하는지.
- #722·#724·#726·#741 의 최신 상태와 Runner 설정 쓰기 책임의 중복.
- 실제 타입별 부속 파일과 ND 계열 매핑은 0.2 에서 현행 트레이너·로더를 대조해 확정. Smart 는 선택 키이고 `trained_type` 목록에 들어가지 않는다.
