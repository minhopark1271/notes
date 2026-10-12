# 다중 응답·다중 모델 파이프라인 — v3

> 설계·PR 분해안, 2026-10-11. 기준: GUI `a076fde7`, PR #722, DeepOpt `a4222b6`.
> 이전 문서: [원안](Multi-Response-Multi-Model-Pipeline-Plan.md), [v2](Multi-Response-Multi-Model-Pipeline-Plan_v2.md). v2는 그대로 보존한다.
> **범위: Sim의 1D 경로. MCU·ND는 전체가 별개 경로이며 이번 작업에서 전환하지 않는다.**

## 1. 검토 결론과 범위

원안의 `set + model_id` 참조와 v2의 명시 파일 경로·실제 학습 타입·입력 순서·키 충돌 검증은 유지한다. 모두 현재 다중 모델 실행에 필요한 계약이다. 다음만 줄이거나 보완한다.

| 항목 | v3 결정 |
|---|---|
| Data Label 스냅샷 | `data_label`과 Input/Output 변경 시 전체 삭제를 제거. 미실행 모델의 학습 당시 메타를 보존 |
| 데이터셋 교체 | 전체 무효화 유지. 같은 입력 라벨을 쓰는 다른 데이터셋은 `input_order`로 구분할 수 없음 |
| 쓰기·삭제 충돌 | 원자적 파일 교체와 실행 중 작성자 하나만 허용. 별도 잠금 체계는 만들지 않음 |
| 버전·경로 검사 | `schema_version == 2`, ID·고정 상대경로·필수 필드만 검사. 버전 협상·범용 경로 해석은 도입하지 않음 |
| transformation | 값 보존·복원만. 계산·역변환은 후속이며 UI에 미적용임을 표시 |
| 작업 분해 | 기능별 이슈 아래 PR 단위를 두되, XML 작성·파서는 함께 변경. 구현 PR과 dev 통합 시점을 구분 |

일반 Launcher XML 통합, 1D Builder·Runner, 여러 Builder를 참조하는 Optimizer까지 대상이다. 같은 component·충돌 없는 응답 키·스칼라 DV를 1차 제약으로 둔다. KPI·BORE/BOSS의 별도 XML은 통합하지 않는다.

MCU·ND의 설정·산출물·학습·예측·혼합 실행, 다중 component, 벡터 DV 펼침, 모델 이력·복구, 같은 XML의 내용 변경 감지(#650), DOE 리샘플링(#684), Runner 다중 Builder는 제외한다. 공유 위젯·파서·헬퍼를 바꿀 때도 제외 경로의 계약을 일괄 교체하지 않는다.

## 2. 공통 계약

### 2.1 데이터셋

- 일반 Launcher Set의 Preprocess 한 번은 `{LauncherSet}.xml` 하나를 쓴다. 샘플마다 응답 텐서 N개이며 하나라도 없으면 그 샘플을 제외한다.
- 텐서 키는 `sanitizeString(name)`. 정규화 후 중복, 입력 키·예약 키 충돌, 다른 component 혼합은 쓰기 전에 거부한다. 같은 이름의 다른 시점도 중복으로 거부한다. 자동 ID는 만들지 않는다.
- `model_info.selected_responses[]` 항목은 `{key, component, load_step, substep, name, file_name}`. `key`는 실제 텐서 키이며 step·substep을 분리해 보존한다. 서로 다른 시점은 요청별 카탈로그를 조회한다.
- Launcher 응답 표는 Config를 통해 저장·복원한다. 대상 1D XML의 작성·파서를 함께 배열 형식으로 바꾼다. DeepOpt도 해당 1D 입력의 중복 dict 키를 거부한다.

### 2.2 모델 식별과 설정

참조는 `{set: Builder setId, model_id}`다. 이름·타입·경로를 식별자로 쓰지 않는다. `model_id`는 Set의 `modelSeq`를 증가시켜 발급하는 `model{N}`이며 삭제 후 재사용하지 않는다.

```jsonc
// ModelBuilder Set의 Configuration. Data Label의 기존 Input/Output 구조는 유지.
"Configuration": [
  {"id":"model1", "response":"stress", "type":"Smart", "options":{}, "run":true},
  {"id":"model2", "response":"stress", "type":"RF", "options":{}, "run":false}
]
```

같은 타입 여러 행을 허용하고 옵션 페이지는 `m_configWidgets[id]`처럼 행별로 소유한다. 타입 변경 시 그 행의 옵션 페이지·값을 새 타입의 기본값으로 교체하고 다른 행은 유지한다. 행의 ID는 유지하며, 저장된 학습 결과는 다음 재학습 전까지 마지막 학습 당시 메타로 표시한다.

Set json에는 학습 상태·오차를 쓰지 않는다. `type`은 선택한 알고리즘, `trained_type`은 실제 저장된 모델 타입이다. Smart도 소비 시에는 우승 모델의 타입을 쓴다. 행의 `response`는 Output의 실제 라벨 키이며 표시용 접미사를 포함하지 않는다.

### 2.3 산출물과 manifest

최종 파일은 `{Builder}/{model_id}/model.pt`. manifest의 `path`는 `model_info.json` 기준 상대 파일 경로, 엔진에 넘기는 `path`는 실행 직전 해석한 절대 파일 경로다. 디렉터리를 넘기지 않는다.

```jsonc
// model_info.json. parameter·originRecord·selected_responses는 기존 출처 정보를 보존.
{"schema_version":2, "parameter":{}, "originRecord":{}, "selected_responses":[],
 "models":{
   "model1":{"response":"stress", "type":"Smart", "trained_type":"RF",
     "input_order":["dv1","dv2"], "reduction":"Max", "transformation":"None",
     "path":"model1/model.pt", "status":"Done", "errors":{}, "message":""}
 }}
```

| 실제 타입 | 로더·부속 파일 |
|---|---|
| `Kriging-KBCC`, `RBF`, `SVR`, `RF` | 기존 pickle 계열 로더. 현재 저장 객체의 scaling 정보 유지 |
| `MLP`, `BNN` | 각 전용 로더. 같은 폴더의 `model_info.txt`·input/output scaler 포함 |
| `Smart` | 실제 타입으로 허용하지 않음. 후보를 `{id}/candidates/{type}/`에 학습하고 우승 모델과 부속 파일을 함께 `{id}/`로 이동 |

Smart의 `Model_Error.csv`도 `{id}/`에 둔다. 타입별 저장→재로딩 검증에 필요한 파일을 포함하고, 필요한 파일이 모두 완성된 뒤에만 `Done`을 기록한다. 경로 문자열로 타입·오차를 추정하거나 glob으로 모델을 선택하지 않는다.

GUI는 ID 형식과 `path == model_id + "/model.pt"`를 확인해 경로를 조립한다. 파일에서 읽은 ID·path를 무검증으로 신뢰하지 않되 임의 경로를 지원하는 범용 resolver는 만들지 않는다. 모델 디렉터리 삭제에도 같은 ID 검증을 쓴다.

### 2.4 상태·쓰기·재학습

- 실행할 행·응답·옵션을 검증한 뒤 GUI가 해당 행만 `In Progress`로 초기화하고 이전 path·trained_type·input_order·errors·message를 지운다. DeepOpt가 성공 시 `Done`, 실패 시 `Failed`와 메시지를 기록한다. 미실행 행은 보존한다.
- DeepOpt는 각 실행 행의 재학습 전에 해당 `{id}/`를 비우고 새로 쓴다. 정리 실패 시 그 행을 실패 처리하며 이전 산출물을 다시 `Done`으로 간주하지 않는다. 다른 ID의 파일은 건드리지 않는다. GUI의 프로세스 시작 실패도 종료 보정으로 처리한다.
- `In Progress`·`Failed`에는 path·실제 타입·입력 순서가 없어도 된다. `Done`에만 실행 필드를 요구한다. 사용 가능 조건은 유효한 완료 항목과 모델 파일의 존재다.
- 쓰기 순서는 **GUI 초기화 → 실행 중 DeepOpt만 작성 → 종료 후 GUI 최종 보정**이다. 같은 디렉터리의 임시 파일을 완성한 뒤 GUI는 `QSaveFile`, DeepOpt는 `os.replace`로 교체한다.
- 폴링의 일시적 읽기 실패는 직전 표시를 유지하고 재시도한다. 종료 후 읽기 실패는 오류로 표시하고, 남은 `In Progress`는 `Failed`로 보정한 뒤 다음 실행을 허용한다. 시작부터 보정 완료까지 UI·삭제 함수 모두 모델 삭제를 거부한다.
- 모델 삭제는 행 설정·manifest 항목·해당 디렉터리를 대상으로 한다. 파일 삭제 실패 시 삭제 완료로 표시하지 않는다. modelSeq는 되돌리지 않는다.
- 같은 데이터셋의 Data Label을 편집해도 다른 모델을 삭제하지 않는다. 미실행 모델의 `response`·reduction·transformation·input_order는 **마지막 학습 당시 값**을 유지한다. 편집값으로 과거 산출물의 메타를 덮어쓰지 않는다.
- 다른 데이터셋에서 학습을 시작하면 기존 모델 전체를 무효화한다. 비교에는 기존 `originRecord.dataset`의 producer setId와 파일 식별을 사용한다. 실제 모델 폴더 삭제를 동반하므로 이때만 확인창을 두며, 취소하면 모두 유지한다. 행·ID·modelSeq는 유지한다.

v2 D5의 메타 기록과 D8의 라벨 검증은 데이터셋 정체성 검증을 대신하지 않는다. 전체 Data Label 스냅샷을 제거하는 근거는 **모델마다 마지막 학습 메타를 보존하기 때문**이다. 절대경로·표시명 변경과 같은 파일의 내용 변경 감지는 이 비교에서 다루지 않는다.

### 2.5 Runner·Optimizer

| 설정 위치 | 저장 내용 |
|---|---|
| Runner `modelBuilder` | Builder 단일 참조 `{set, name}` 유지. GUI 선택 영속 키는 #724에서 확정 |
| Runner `Model upload.Output Response[]` | 엔진 항목 `{set, model_id, response, model}` + 실행 직전 `path, trained_type, input_order` |
| Optimizer `modelBuilder` | DV·Preview의 출처인 기본 Builder `{set, name}` |
| Optimizer `Optimization.trained_surrogate_model[]` | Runner와 같은 항목 + `symbol`. 행마다 다른 Builder 허용 |

`set`은 Builder setId, `model`은 표시용 선택 타입이다. DeepOpt의 로딩에는 실행 시 전달한 파일 경로·실제 타입을 사용한다.

- 선택 영속과 엔진 입력 쓰기는 #724의 분리를 따른다. 실행 전 모든 참조를 해석해 `path`·`trained_type`·`input_order`와 응답 메타를 manifest에서 갱신한 뒤 한 번 저장한다. 하나라도 실패하면 저장·실행하지 않는다.
- DeepOpt가 실제 학습 순서를 `input_order`로 기록한다. 소비자는 label/value를 매핑해 모델별로 재배열한다. 누락·중복·비유한 값·길이/차원 불일치는 실행 전 거부한다. reduction 이름 비교는 대소문자를 무시하고 모르는 값은 거부한다.
- Optimizer는 참조 모델의 입력 라벨 집합이 같을 때만 지원한다. DV 메타는 기본 Builder의 `parameter`를 사용하며 필요한 라벨이 없으면 거부한다. Geometry Set id가 다른 모델을 섞으면 Preview·Morphing을 비활성화한다.
- 심볼은 `max+1`로 발급하고 저장값을 유지한다. 목적·제약식의 심볼 토큰으로 사용 중인 행은 삭제하지 못한다.
- 최적화의 일반 응답·`std_pred`·deterministic/probabilistic 평가가 모두 같은 입력 어댑터를 쓴다. `predict_responses`뿐 아니라 `symbolic_module.ExpressionEvaluator`도 변경한다.
- Runner CSV는 `{RunnerSet}_test_results.csv`, active case당 한 행, 모델당 `{response} [{model_id}]` 열 하나다. 기존 모델×case 단위 행 추가 함수를 case별 집계로 바꾼다. 같은 표시명의 case를 임의로 합치지 않는다.
- Run 시작 시 이전 CSV를 삭제하고 실패하면 시작하지 않는다. CLI의 내부 루프에서 잡은 예외도 최종 실패 코드에 반영한다. GUI는 명시 결과 경로만 열며 실패 Run의 부분 결과를 정상 완료로 표시하지 않는다.

### 2.6 하위호환

대상 Sim 1D의 v1 XML·Configuration·manifest는 자동 변환하지 않고 재생성을 안내한다. manifest 버전은 `schema_version == 2` 하나로 판정하고 상태별 필수 구조를 검증한다. 최상위 `errors`·단수 `selected_response`를 별도 버전 판정 신호로 쓰지 않는다.

Runner·Optimizer의 `model_id` 없는 선택은 빈 선택으로 열고 다른 설정은 보존한다. 열기만으로 파일을 덮어쓰지 않는다. 이 정책을 별개 경로인 MCU·ND에 적용하지 않는다.

## 3. 이슈 아래 PR 단위

기존 0~4 및 하위 이슈 번호는 기능 범위, `-A/-B`는 저장소 하나의 구현 PR 하나다. 총 18개이며 P6의 2개를 포함한다. 각 PR의 변경 지점·경계·완료 조건을 아래에 둔다. 파일명은 기존 코드 기준이고 #722 신설 파일은 해당 브랜치를 기준으로 한다. 공통 계약은 §2를 적용하며 반복하지 않는다.

### P6. 독립 결함 수정

**P6-A · DeepOpt — 실패 코드·결과 경로** / 선행 없음
- 변경: `main.py`의 `train_model_1d`·`test_model_1d`·`run_optimization`. 내부 루프 실패를 집계하고 1D 예측에 명시 CSV 경로 옵션 추가. 모델 선택·설정 형식·CSV 행 집계는 바꾸지 않는다.
- 완료: 모델 하나가 실패해도 최종 종료 코드가 0이 아니며 지정 CSV에 기록한다. 기존 CLI 호출의 경로 기본값은 유지해 P6-B보다 먼저 적용할 수 있다.

**P6-B · GUI — 명시 결과 열기** / 선행 P6-A
- 변경: `DashModelRunner::run1DPrediction`·`onPredictionSucceeded`의 CSV 경로·초기화·결과 열기, `DashOptimizer::onJobFinished`의 png 경로. 지연·최신 CSV 탐색 제거.
- 완료: 두 번 실행해도 이번 Run의 행만 표시하고 실패·CSV 삭제 실패를 정상 완료로 표시하지 않는다. 최적화 후 실제 출력 위치의 그림을 연다.

### 0. 공통 참조·산출물

**0.1-A · GUI — 참조·판독·ID 발급** / 선행 #722
- 변경: `DashModelBuilderArtifact`에 ModelRef·ModelEntry·상태별 판독, `DashModelBuilderReference`에 ID 발급·`modelDir`·`resolveModelFile`. 소비 UI 교체는 3.1·4.1 소관.
- 완료: 참조 round-trip, v1 거부, In Progress와 Done의 필수 필드 차이, 고정 경로 검증, 삭제 후 ID 미재사용. 기존 호출부를 유지한 헬퍼 추가까지는 단독 적용 가능.

**0.2-A · DeepOpt — 저장·로딩·입력 공통 함수** / 선행 없음
- 변경: 신규 `source/artifact.py`의 manifest 원자 갱신·명시 타입 로더·입력 어댑터, `optimize/pred_surrogates.py`의 로더 연결, `preprocessor/xml_parser.py`의 대상 1D 중복 키 검증. CLI 전환은 제외.
- 완료: 다른 manifest 항목 보존, 타입별 저장 파일 재로딩, 순서 반전·누락·중복·길이/차원 오류 검증. ND의 파서 호출과 기존 로더 호출은 유지한다.

**0.2-B · DeepOpt — 트레이너 산출물 배치** / 선행 0.2-A
- 변경: `models/oned/*trainer.py`, `smart_trainer.py`, `run_train_1d._save_model_info_json`. model_id 디렉터리·부속 파일·Smart 후보 정리·모델별 오차 저장. CLI 행 순회·종료 판정은 2.4 소관.
- 완료: 같은 타입 두 모델의 파일이 공존하고, 재학습 대상만 정리한다. Smart의 RF·MLP·BNN 우승 사례에서 재로딩과 `Model_Error.csv` 보존을 확인한다.

### 1. Preprocessor

**1.1-A · GUI — 응답 표 영속** / 선행 없음
- 변경: `DashAnalysisLauncherConfig`의 Output Response 읽기/쓰기, `DashAnalysisLauncherPresentationModel::saveOutputResponse`, 위젯 열기 시 복원. XML 형식은 제외.
- 완료: 응답 여러 개의 이름·component·step·substep을 저장·재열기해 같은 표로 복원한다.

**1.1-B · GUI — XML 메타 작성·파서 동시 전환** / 선행 없음
- 변경: `DashResultTypes.h`의 SelectedResponse, `DashResultXmlWriter::writeModelInfoToXml`, Launcher의 메타 조립, `DashModelBuilder::parseModelInfoStream`·`readSelectedResponseFromStream`, `DashXmlTailLocator`. 2.2의 XML 파서 작업을 이 PR에 포함한다.
- 완료: 대상 1D 생산·소비 경로에서 배열 2개·substep·텐서 키 대응·꼬리 파싱을 검증한다. KPI 등 별도 XML도 1D가 소비하는 메타 변경은 함께 반영하되 XML 파일 자체는 통합하지 않는다. MCU·ND 호출은 비전환.

**1.2-A · GUI — XML 하나에 응답 N개** / 선행 1.1-B
- 변경: `DashAnalysisLauncher::processResults`, `DashResultProcessor::processSamples`, `DashResultXmlWriter::appendSample`, `DashResultBatch::outputFileName`, Builder 데이터셋 목록. 키/component 검증을 시작 전에 수행한다.
- 완료: 샘플당 파일 열기 1회, 응답 누락 샘플 제외, 요청별 시점 조회, 키 충돌·다른 component 거부. 거부 시 기존 XML 유지. DeepOpt 중복 키 검증은 0.2-A 소관.

### 2. Builder

**2.1-A · GUI — 행별 설정·옵션** / 선행 0.1-A
- 변경: `DashModelBuilder::onTrainingStartButtonClicked`의 Configuration 조립·`loadDataLabelConfig`, `DashModelBuilderPresentationModel::TrainingRowInput`·`buildTrainingStartPlan`, `DashModelBuilderWidgetBase`의 행/옵션, `DashModelBuilderWidget::restoreConfigurationUI`. 상태 폴링은 제외.
- 완료: 같은 타입 두 행의 ID·run·옵션이 재열기 후 유지된다. 타입 변경 시 해당 행 옵션만 교체하고 transformation 값도 복원한다. 공용 위젯의 MCU·ND 형식은 유지한다.

**2.2-A · GUI — 학습 시작·데이터셋 교체** / 선행 1.1-B, 2.1-A
- 변경: `DashModelBuilder::onTrainingStartButtonClicked`의 manifest 작성 부분을 함수로 분리. 출처 비교·실행 행 초기화·원자적 저장을 담당하며 XML 파서는 1.1-B 소관이다.
- 완료: 부분 재학습에서 미실행 메타를 보존하고 Data Label 편집만으로 전체 삭제하지 않는다. 다른 데이터셋 교체·삭제 확인 취소·쓰기 실패를 검증한다. 재학습 폴더 정리는 DeepOpt 2.4가 0.2의 기능을 호출한다.

**2.3-A · GUI — 상태·오차·삭제** / 선행 2.2-A
- 변경: `checkModelStatusInternal`·`finalizeStaleStatuses`, `loadTrainedModelInfo`·`refreshTrainedModelInfo`, 산출물 목록·`getTestDatasetFiles`·`deleteTrainedModel`, 위젯의 상태 갱신·행 삭제. 모델 ID로 찾고 manifest의 실제 타입·오차를 표시한다.
- 완료: 학습 중 UI·함수 양쪽의 삭제 거부, 종료 보정 후 재실행, 한 모델 삭제 시 다른 모델 보존, 파일 삭제 실패 표시. 실학습 검증에는 2.4-A가 필요하다.

**2.4-A · DeepOpt — 행별 1D 학습** / 선행 P6-A, 0.2-B
- 변경: `main.py::train_model_1d`, `run_train_1d`, `XMLTrainingDataBuilder.build_1d`. Configuration 배열의 run 행만 처리하고 각 row.response 하나를 학습한다. input_order 반환·reduction 정규화·행별 상태·실패 집계를 연결한다.
- 완료: 같은 타입 두 행의 별도 산출물, run:false 보존, Sum 계산, 실제 학습 열 순서 기록, 한 행 실패 시 성공 행 보존·최종 비정상 종료. ND가 쓰는 `_update_json_status`까지 삭제하지 않는다.

### 3. Runner

**3.1-A · GUI — 모델별 선택·복원** / 선행 0.1-A, #724
- 변경: `DashModelRunnerConfig`의 선택 읽기/쓰기, `DashModelRunnerWidget::populateSurrogateTable`, PresentationModel의 선택 수집, `DashSurrogateModelCommon`의 v2 표시 자료. usable 모델당 한 행으로 바꾼다.
- 완료: 같은 응답·같은 타입의 서로 다른 ID를 독립 선택·복원한다. 실행 없이 선택만 바꿔도 #724의 영속 키에 반영된다. 엔진 입력 해석·프로세스 실행은 3.2 소관.

**3.2-A · GUI — 참조 해석·일괄 실행** / 선행 P6-B, 3.1-A
- 변경: `DashModelRunner::run1DPrediction`과 엔진 입력 조립. 전체 참조의 파일·실제 타입·입력 순서·응답 메타를 해석한 뒤 1회 저장·1회 CLI 실행한다.
- 완료: 한 참조가 실패하면 저장·실행하지 않는다. 3.3-A와 연동해 2 case × 2 model의 CSV·재실행·부분 실패를 검증한다. ND 실행·혼합 실행 조정은 제외.

**3.3-A · DeepOpt — 모델별 예측·case별 CSV** / 선행 P6-A, 0.2-A
- 변경: `main.py::test_model_1d`, `_write_1d_test_result_to_csv`, `RunTest1D`. 공통 로더·입력 어댑터를 연결하고 결과를 case당 한 행으로 집계한다.
- 완료: 같은 응답의 모델 두 개·입력 순서 반전·case 두 개로 정확히 2행·모델 열 2개. 같은 표시명의 case도 별도 행이며 참조/예측 실패를 건너뛰어 성공 처리하지 않는다.

### 4. Optimizer

**4.1-A · GUI — 다중 Builder 모델·심볼** / 선행 0.1-A
- 변경: `DashOptimizer`의 SurrogateModelInfo·save/load·DV 복원, `DashOptimizerWidget::populateSurrogateTable`, Preview·`performMorphing`의 기본 Builder 선택. `selectModelBuilderFolder`의 이름 일치 추정을 제거한다. 식 편집기는 바꾸지 않는다.
- 완료: Builder 두 개의 모델 세 개·심볼을 저장/복원한다. 입력 집합 불일치, 사용 중 심볼 삭제, Geometry 출처 불일치 시 Preview 제한을 검증한다. #726의 재적용 작업과 수정 범위를 맞춘다.

**4.2-A · GUI — 최적화 실행 계약** / 선행 P6-B, 4.1-A
- 변경: `DashOptimizer::runOptimization`의 모든 참조 해석·엔진 입력 저장·argv. 호출은 `run-optimization <OptSet.json> --output-dir <dir>`이며 Builder 디렉터리 인자는 제거한다.
- 완료: 참조 실패 시 무저장·무실행. 4.3-A와 연동해 선택한 모델로 실행하고 P6-B의 명시 결과를 표시한다.

**4.3-A · DeepOpt — 선택 모델로 식 평가** / 선행 P6-A, 0.2-A
- 변경: `main.py::run_optimization`, `MainOptimizer`·`problem_setup.py`의 문제 정의/경로 조립, `symbolic_module.ExpressionEvaluator`의 일반 응답·std_pred. 공통 로더·입력 어댑터를 사용한다. 최적화 알고리즘·optimum.json·별도 fitting 경로는 유지한다.
- 완료: Builder 두 개의 모델 세 개로 입력 순서 반전·Smart 실제 타입을 검증하고 목적·제약·std_pred 계산값까지 확인한다. 최저 오차 파일 탐색이 선택한 모델을 대체하지 않는다.

## 4. 순서와 통합

**코드 선행과 통합 검증 선행을 구분한다.** 3.1·4.1은 manifest fixture로 먼저 구현할 수 있으며 실제 학습 UI 완료를 기다릴 필요가 없다. 반대로 최종 검증에는 아래 생산자·소비자가 모두 필요하다.

1. P6, 0.2-A, 1.1-A/B는 #722와 독립적으로 시작한다. #722 뒤 0.1-A, #724 뒤 3.1-A를 진행한다. `0.1 → 1.1` 의존은 없다.
2. 1.1-B → 1.2-A와 0.1-A → 2.1-A → 2.2-A → 2.3-A, 0.2-A → 0.2-B → 2.4-A를 진행한다.
3. Builder 통합 검증은 1.2-A·2.3-A·2.4-A가 갖춰진 뒤 수행한다. 여러 응답·같은 타입 모델·Smart·부분 재학습을 확인한다.
4. Runner는 3.2-A + 3.3-A, Optimizer는 4.2-A + 4.3-A를 짝지어 검증한다. 두 소비 경로의 구현은 서로 독립적이다.

### dev에 불완전한 전환을 남기지 않는 방법

XML 작성·파서는 1.1-B 한 PR로 묶는다. 나머지는 산출물 형식 변경이 Builder·Runner·Optimizer 전체에 걸리므로 모듈별 PR을 순서대로 dev에 넣는 것만으로 해결되지 않는다. 특히 0.2-B나 2.1-A를 단독 적용하면 기존 소비자가 깨진다. 기능별 네 묶음으로 합쳐도 Builder 묶음이 먼저 머지되면 Runner·Optimizer가 깨지는 문제는 남는다.

**권고안은 전환 구현 PR들을 양 저장소의 한시적 통합 브랜치에서 리뷰하고, 최종 GUI·DeepOpt 조합을 검증한 뒤 dev용 통합 PR을 저장소별 하나씩 만드는 것이다.** P6·응답 표 영속 등 기존 동작을 유지하는 PR은 일반 절차로 먼저 머지할 수 있다. 두 저장소는 검증한 커밋 조합으로 함께 배포한다. 이 문서는 브랜치 운영의 제안이며 실제 생성·수칙 변경을 뜻하지 않는다.

이는 [저장소 관리 수칙](https://github.com/NumeRealWorks/DashOpti_GUI/wiki/저장소-관리-수칙)의 일반적인 작업 브랜치→dev 절차에 대한 예외 제안이다. 예외를 채택하지 않으면 공통 헬퍼 등 비활성 준비 PR만 먼저 dev에 넣고, 실제 전환은 저장소별 하나의 큰 PR로 묶는다. 순차 머지를 위해 임시 v1/v2 이중 저장·장기 호환 계층·기능 플래그 체계를 추가하지 않는다.

완료 조건의 함수 단위 검증은 해당 PR에 포함하고 실제 프로세스 연결 검증은 위 조합에서 수행한다. 마지막에는 Launcher→Builder→Runner→Optimizer를 한 번 이어 실행하고, 공용 코드 변경이 MCU·ND의 기존 계약을 전환하지 않았는지 확인한다. 범위 밖 기능의 신규 테스트 체계는 만들지 않는다.

fixture는 두 저장소의 `tests/fixtures/multi_model_v2/`에 같은 파일의 복사본을 둔다. 변경한 PR에 양쪽 갱신을 연결하고 최종 통합 시 파일 일치를 확인한다. 한 저장소의 테스트가 다른 저장소 checkout에 의존하지 않게 한다. 별도 공용 패키지는 만들지 않는다.

## 5. 착수 전 확인할 두 가지

- 대상 Deck의 응답들이 같은 component·서로 다른 정규화 키라는 1차 제약을 만족하는지 확인한다.
- `{LauncherSet}.xml`은 개명 후 재생성하면 파일명도 달라질 수 있다. 데이터셋 파일 식별과 Set 개명 대응을 2.2-A에서 확정한다. producer setId만으로는 KPI 등 별도 XML을 구분하지 못하므로 파일 식별을 무조건 제거하지 않는다.
