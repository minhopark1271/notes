# 다중 응답·다중 모델 파이프라인 — 공통 규격 설계와 작업 계획 (v4)

> 관련 Issue: 선행 #722. 접점 #724 · #650 · #684 · #726.
> 상태: **코드 조사 기반 설계안** — 2026-10-11, GUI `a076fde7`, PR #722 (조사 당시 open, 리뷰 0건), DeepOpt `a4222b6` 기준.
> 이전 문서: [원안](Multi-Response-Multi-Model-Pipeline-Plan.md), [v2](Multi-Response-Multi-Model-Pipeline-Plan_v2.md), [v3](Multi-Response-Multi-Model-Pipeline-Plan_v3.md).
> 범위: **Sim Builder 의 1D 계열.** ND 계열과 MCU variant 는 기존 계약을 유지한다.
> 해상도: 원안과 같은 이슈 초안 양식 (`현상 / 범위 / 현재 구조 / 변경 / 기대 / Related`).

## 1. 조사로 바뀐 전제

v3 의 범위 전제 "MCU·ND 는 전체가 별개 경로" 는 코드와 다르다. 그 위에 세운 "공유 코드를 바꿔도 제외 경로의 계약은 교체하지 않는다" 는 현 구조에서 성립하지 않는다.

| 사실 | 근거 |
|---|---|
| ND 는 Sim Builder 안의 모델 타입군이다. 1D 7종과 ND 5종이 같은 콤보 목록이고, 첫 행의 타입으로 `train-model-1d` / `train-model-nd` 를 고르며, 같은 Set json Configuration dict 와 같은 model_info.json 을 쓴다 | `model/DashModelBuilder.cpp:353-361`, `:702-706`, `:839-843` |
| `(Field)` 는 3D 응답 + reduction None 일 때의 표시 규칙이다 | `viewmodel/DashModelBuilderPresentationModel.cpp:192-195` |
| DeepOpt 의 ND 학습도 Configuration dict 를 순회하고 `_update_json_status` 로 Set json 에 상태를 쓰며, 평가 결과는 같은 model_info.json 의 최상위 `errors` 다 | `main.py:57-65`, `:249-262`, `source/run_train_nd_basic.py:508` |
| Runner 는 행별 타입 접두로 ND 를 판별해 같은 표에서 분기하고, ND·1D 를 두 번 써서 두 CLI 를 띄운다 | `viewmodel/DashModelRunnerPresentationModel.cpp:64-65`, `view/DashModelRunnerWidget.cpp:1351-1376` |
| MCU 는 별도 variant 지만 base 의 폴링·`loadTrainedModelInfo`·`loadDataLabelConfig`·`deleteTrainedModel` 을 상속하고, base 구현을 명시 호출하는 곳도 있다 | `model/DashModelBuilderMCU.h:28-49`, `model/DashModelBuilderMCU.cpp:768-813` |
| `loadDataLabelConfig` 는 이름과 달리 Configuration 을 dict 로 읽는다 | `model/DashModelBuilder.cpp:1057-1059` |
| `ProcessJob::cancel()` 은 QProcess 를 떼어내고 종료를 관측하기 전에 `Cancelled` 로 전이한다 | `controller/async/ProcessJob.cpp:97-121` |

v3 의 1D 계약 (set + model_id, trained_type, input_order, 고정 경로, 원자적 교체, 상태기, 마지막 학습 메타 보존) 은 유지한다. 다음을 더하거나 고친다.

| 항목 | v4 결정 |
|---|---|
| 계열 명시 | Sim Set 에 `modelFamily: 1D` 또는 `ND` 를 첫 설정에서 기록하고 고정한다 |
| 계약 선택 | (variant, modelFamily, 구형식 판별) 로 v2 / ND 기존 / MCU 기존 / 미확정 중 하나를 고른다. 미확정은 저장·실행을 차단한다 |
| 클래스 | 기존 클래스를 유지한다. 계약 분기점을 열거하고 한 판독값으로 분기한다. 새 variant 나 클래스 계층 재편은 하지 않는다 |
| 기존 ND Set | 구형식 Configuration 과 산출물이 모두 ND 면 ND 로 분류해 보존한다. 열기만으로 저장하지 않는다 |
| 공유 XML 파서 | 단수 `selected_response` 와 배열 `selected_responses` 를 모두 읽는다. 구형 XML 거부는 1D 경로에서만 한다 |
| Runner·Optimizer | Runner 는 참조 Builder 의 계약을 따른다. Optimizer 는 v2 Builder 만 참조하고 실행 직전 다시 확인한다 |
| 정확성 조건 | 학습 입력·응답 스칼라 검증, 실제 프로세스 종료 관측 뒤 보정, 부분 삭제·보정 실패 처리, 교체 재시도 한정 |
| 선행 작업 | Builder 와 Runner 의 계열 경계를 먼저 나누고 각 기능의 형식을 전환한다 |

채택하지 않은 대안: `variant: Field` 신설과 v1 공통 클래스 분리. 누락을 컴파일 오류로 만드는 이점이 있으나 생성 경로·프로젝트 판별·MCU 상속 사슬을 재편해야 해 이번 범위보다 크다. ND 나 MCU 를 v2 로 옮길 때 다시 검토한다.

일반 Launcher XML 통합, 1D Builder·Runner, 여러 Builder 를 참조하는 Optimizer 까지 대상이다. 같은 component·충돌 없는 응답 키·스칼라 DV 를 1차 제약으로 둔다. KPI·BORE/BOSS 의 별도 XML 은 통합하지 않는다.

## 2. 공통 규격

### 데이터셋

- 일반 Launcher Set 의 Preprocess 한 번은 `{LauncherSet}.xml` 하나를 쓴다. 샘플마다 응답 텐서 N개이며 하나라도 없으면 그 샘플을 제외한다.
- 텐서 키는 `sanitizeString(name)`. 정규화 후 중복, 입력 키·예약 키 충돌, 다른 component 혼합은 쓰기 전에 거부한다. 같은 이름의 다른 시점도 중복으로 거부한다. 자동 ID 는 만들지 않는다.
- `model_info.selected_responses[]` 항목은 `{key, component, load_step, substep, name, file_name}`. `key` 는 실제 텐서 키이며 step·substep 을 분리해 보존한다. 서로 다른 시점은 요청별 카탈로그를 조회한다.
- Launcher 응답 표는 Config 를 통해 저장·복원한다. 1D XML 의 작성·파서를 함께 배열 형식으로 바꾼다. DeepOpt 도 해당 1D 입력의 중복 dict 키를 거부한다.
- 공유 파서 `parseModelInfoStream` 은 배열과 구형 단수 키를 모두 읽어 같은 목록 구조로 돌려주고 구형 여부를 표시한다. 1D 경로는 구형을 거부하고 ND 경로는 둘 다 쓴다. DeepOpt 와 Runner 는 manifest 의 이 값을 읽지 않는다.
- 1D·ND 구분은 XML 과 무관하다. Launcher 는 계열을 선택하지 않고, 같은 XML 을 두 계열의 Builder Set 이 쓸 수 있다. 응답 수로 계열을 추정하지 않는다.

### 계열과 계약 선택

- Sim Set 은 `modelFamily` 를 가진다. 첫 설정 (Data Label 저장 또는 첫 행 추가) 에서 선택해 기록하고, Configuration 행이나 산출물이 생긴 뒤에는 바꾸지 않는다. 행과 산출물을 모두 지워도 자동으로 선택 가능 상태로 돌아가지 않는다. 다른 계열이 필요하면 새 Set 을 만든다. 같은 데이터셋으로 1D·ND 를 둘 다 학습하려면 Set 두 개를 쓴다.
- 판독 순서는 variant, `modelFamily` (없으면 구형식 분류), 계약이다. 설정 로딩·폴링·실행 전에 끝낸다. `loadDataLabelConfig` 의 Configuration 판독은 Data Label 판독과 분리해 계약별로 둔다.

| 판독 결과 | 계약 | 적용 |
|---|---|---|
| Sim + 1D | v2 | 아래 모델 식별·산출물·상태·소비 측 참조·하위호환 규격 |
| Sim + ND | ND 기존 | Configuration dict, Set json 상태, 최상위 `errors`, 현행 산출물 배치, `train-model-nd`·`test-model-nd` |
| MCU | MCU 기존 | 현행 override 와 base 의 v1 본문 |
| 미분류·혼합·알 수 없는 타입 | 없음 | 저장·실행 차단. 분리 또는 확정 안내 |

- 계약값은 설정·manifest 형식, 상태 출처, 학습 결과·오차 판독, 산출물 목록, 삭제에 쓴다. 모델 타입 목록·reduction 규칙·서브커맨드는 ND 와 MCU 가 다르므로 계약값이 아니라 계열값과 기존 MCU override 로 정한다.
- 분기점은 Configuration 직렬화·복원, 학습 시작의 manifest 쓰기, 상태 폴링 출처, 학습 결과·오차 판독, 산출물 목록, 삭제, 위젯 행 모델이다. 이 밖에서 계약·계열 문자열을 비교하지 않는다. v1 본문은 별도 함수로 두며 MCU 가 v1 을 유지하는 동안 남는다.
- 기존 Set 분류: `modelFamily` 가 없는 Sim Set 은 구형식 (dict) Configuration 의 전 행 타입과 산출물 폴더의 타입을 확인한다. 모두 ND 5종이면 ND. 모두 1D 7종이면 1D 로 분류하되 v1 형식이므로 하위호환 규격의 재생성 정책을 따른다. 충돌·알 수 없는 타입·빈 설정은 미분류. 어떤 경우도 1D 로 기본 처리하지 않고, 열기만으로 파일을 쓰지 않으며, 다음 저장 때 `modelFamily` 를 기록한다. 신형식 (배열) Configuration 에 ND 타입이 있으면 오류다. `(Field)` 표시 문자열은 판별에 쓰지 않는다.
- 1D 적합성: 각 행의 선택 응답은 reduction 후 샘플당 스칼라 하나여야 한다. 여러 성분이 남으면 거부하고 첫 성분만 학습하지 않는다. XML 의 응답 수는 제한하지 않는다. ND 는 reduction None 고정이다.
- 혼합 실행을 구성하는 UI 와 실행 조정은 없앤다. 설정 로드·실행 시 계열과 전 행 타입의 일치는 검증한다.

### 모델 식별과 설정 (Sim + 1D)

참조는 `{set: Builder setId, model_id}` 다. 이름·타입·경로를 식별자로 쓰지 않는다. `model_id` 는 Set 의 `modelSeq` 를 증가시켜 발급하는 `model{N}` 이며 삭제 후 재사용하지 않는다.

```jsonc
// ModelBuilder Set 의 Configuration (modelFamily: 1D). Data Label 의 기존 Input/Output 구조는 유지.
"Configuration": [
  {"id":"model1", "response":"stress", "type":"Smart", "options":{}, "run":true},
  {"id":"model2", "response":"stress", "type":"RF", "options":{}, "run":false}
]
```

같은 타입 여러 행을 허용하고 옵션 페이지는 `m_configWidgets[id]` 처럼 행별로 소유한다. 타입 변경 시 그 행의 옵션 페이지·값을 새 타입의 기본값으로 교체하고 다른 행은 유지한다. 행의 ID 는 유지하며, 저장된 학습 결과는 다음 재학습 전까지 마지막 학습 당시 메타로 표시한다.

Set json 에는 학습 상태·오차를 쓰지 않는다. `type` 은 선택한 알고리즘, `trained_type` 은 실제 저장된 모델 타입이다. Smart 도 소비 시에는 우승 모델의 타입을 쓴다. 행의 `response` 는 Output 의 실제 라벨 키이며 표시용 접미사를 포함하지 않는다.

### 산출물과 manifest (Sim + 1D)

최종 파일은 `{Builder}/{model_id}/model.pt`. manifest 의 `path` 는 `model_info.json` 기준 상대 파일 경로, 엔진에 넘기는 `path` 는 실행 직전 해석한 절대 파일 경로다. 디렉터리를 넘기지 않는다.

```jsonc
// model_info.json. parameter·originRecord·selected_responses 는 기존 출처 정보를 보존.
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
| `Smart` | 실제 타입으로 허용하지 않음. 후보를 `{id}/candidates/{type}/` 에 학습하고 우승 모델과 부속 파일을 함께 `{id}/` 로 이동 |

Smart 의 `Model_Error.csv` 도 `{id}/` 에 둔다. 타입별 저장 뒤 재로딩 검증에 필요한 파일을 포함하고, 필요한 파일이 모두 완성된 뒤에만 `Done` 을 기록한다. 경로 문자열로 타입·오차를 추정하거나 glob 으로 모델을 선택하지 않는다.

GUI 는 ID 형식과 `path == model_id + "/model.pt"` 를 확인해 경로를 조립한다. `path` 는 도출 가능하지만 두 저장소 간 계약 확인용으로 v3 대로 저장하고 일치를 검증한다. 범용 resolver 는 만들지 않는다. 모델 디렉터리 삭제에도 같은 ID 검증을 쓴다. 이 검증은 계약이 v2 일 때만 호출한다.

### 상태·쓰기·재학습 (Sim + 1D)

- 실행할 행·응답·옵션을 검증한 뒤 GUI 가 해당 행만 `In Progress` 로 초기화하고 이전 path·trained_type·input_order·errors·message 를 지운다. DeepOpt 가 성공 시 `Done`, 실패 시 `Failed` 와 메시지를 기록한다. 미실행 행은 보존한다.
- DeepOpt 는 학습 전에 입력을 검증한다. 모든 샘플에 선택 라벨이 있고, 라벨당 스칼라 하나이며, 유한값이어야 한다. X 의 열 수와 `input_order` 길이가 같아야 한다. 응답은 reduction 뒤 스칼라 하나여야 한다. 위반한 행은 `Failed` 다.
- DeepOpt 는 각 실행 행의 재학습 전에 해당 `{id}/` 를 비우고 새로 쓴다. 정리 실패 시 그 행을 실패 처리하며 이전 산출물을 다시 `Done` 으로 간주하지 않는다. 다른 ID 의 파일은 건드리지 않는다. GUI 의 프로세스 시작 실패도 종료 보정으로 처리한다.
- `In Progress`·`Failed` 에는 path·실제 타입·입력 순서가 없어도 된다. `Done` 에만 실행 필드를 요구한다. 사용 가능 조건은 유효한 완료 항목과 모델 파일의 존재다.
- 쓰기 순서는 **GUI 초기화, 실행 중 DeepOpt 만 작성, 실제 프로세스 종료 관측, GUI 최종 보정** 이다. 같은 디렉터리의 임시 파일을 완성한 뒤 GUI 는 `QSaveFile`, DeepOpt 는 `os.replace` 로 교체한다.
- 취소 통지와 실제 종료를 구분한다. `ProcessJob::cancel()` 은 QProcess 를 떼어내고 즉시 `Cancelled` 로 전이하므로, 떼어낸 프로세스의 `finished` 를 Job 의 별도 신호로 전달하거나 전이를 그 뒤로 미룬다. manifest 보정·재실행·삭제 허용은 이 신호에 묶는다.
- 교체의 일시적 실패 (Windows 공유 위반) 만 횟수를 제한해 재시도하고 최종 실패를 전파한다. 모든 PermissionError 를 일시적으로 간주하지 않는다.
- 폴링의 일시적 읽기 실패는 직전 표시를 유지하고 재시도한다. 종료 후 manifest 판독 실패나 보정 저장 실패는 보정 완료로 취급하지 않고 오류를 표시하며 다음 실행을 차단한다. 보정이 끝나면 남은 `In Progress` 는 `Failed` 가 되고 다음 실행을 허용한다. 시작부터 보정 완료까지 UI·삭제 함수 모두 모델 삭제를 거부한다.
- 모델 삭제는 행 설정·manifest 항목·해당 디렉터리를 대상으로 한다. 부분 실패한 모델은 usable 로 남기지 않고 manifest 항목을 `Failed` 와 메시지로 둔다. modelSeq 는 되돌리지 않는다.
- 같은 데이터셋의 Data Label 을 편집해도 다른 모델을 삭제하지 않는다. 미실행 모델의 `response`·reduction·transformation·input_order 는 마지막 학습 당시 값을 유지한다.
- 데이터셋 정체성은 `originRecord.dataset` 의 producer setId 와 파일명이다. 다른 데이터셋에서 학습을 시작하면 확인창 뒤 기존 모델 전체와 디렉터리를 무효화한다. 개명 뒤 재생성해 파일명이 바뀐 경우도 같다. 취소하면 모두 유지한다. 행·ID·modelSeq 는 유지한다. 같은 파일의 내용 변경은 #650 소관이다.
- transformation 은 값 보존·복원과 미적용 표시까지만 구현한다.

### Runner·Optimizer

| 설정 위치 | 저장 내용 |
|---|---|
| Runner `modelBuilder` | Builder 단일 참조 `{set, name}` 유지. Runner Set 에 별도 계열 키는 없다 |
| Runner 선택 영속 | #724 를 흡수해 별도 키에 체크 변경 시 기록 (Runner 모델별 선택·복원 작업에서 확정) |
| Runner `Model upload.Output Response[]` | 엔진 입력. v2 항목 `{set, model_id, response, model}` + 실행 직전 `path, trained_type, input_order` |
| Optimizer `modelBuilder` | DV·Preview 의 출처인 기본 Builder `{set, name}` |
| Optimizer `Optimization.trained_surrogate_model[]` | Runner 와 같은 항목 + `symbol`. 행마다 다른 v2 Builder 허용 |

- Runner 는 참조 Builder 의 계약을 따른다. v2 이면 모델 단위 표·v2 엔진 입력·`test-model-1d`, ND 기존이면 현행 ND 표·엔진 입력·`test-model-nd`. 한 Run 은 한 계열이며 ND·1D 분할과 설정 이중 쓰기는 없앤다. MCU Runner 는 별도 모듈 그대로다.
- 계약·계열·모델 목록은 `DashModelBuilderReference::load()` 가 한 번 해석해 `LoadedArtifact` 로 준다. v2 manifest 검증은 계약이 v2 일 때만 한다. 공통 표시 자료 (`ModelEntry` 행 자료, usable 판정) 는 GUI 공통 참조·판독 작업에서 정의하고 Runner·Optimizer 가 함께 쓴다.
- 실행 전 모든 참조를 해석해 `path`·`trained_type`·`input_order` 와 응답 메타를 manifest 에서 갱신한 뒤 한 번 저장한다. 하나라도 실패하면 저장·실행하지 않는다.
- DeepOpt 가 실제 학습 순서를 `input_order` 로 기록한다. 소비자는 label/value 를 매핑해 모델별로 재배열한다. 누락·중복·비유한 값·길이/차원 불일치는 실행 전 거부한다. reduction 이름 비교는 대소문자를 무시하고 모르는 값은 거부한다.
- Optimizer 는 v2 Builder 만 나열하고, 실행 직전 저장된 모든 참조의 Builder 가 v2 인지 다시 확인한다. 참조 모델의 입력 라벨 집합이 같을 때만 지원한다. DV 메타는 기본 Builder 의 `parameter` 를 사용하며 필요한 라벨이 없으면 거부한다. Geometry Set id 가 다른 모델을 섞으면 Preview·Morphing 을 비활성화한다.
- 심볼은 `max+1` 로 발급하고 저장값을 유지한다. 목적·제약식의 심볼 토큰으로 사용 중인 행은 삭제하지 못한다.
- 최적화의 일반 응답·`std_pred`·deterministic/probabilistic 평가가 모두 같은 입력 어댑터를 쓴다. `predict_responses` 뿐 아니라 `symbolic_module.ExpressionEvaluator` 도 변경한다.
- Runner CSV 는 `{RunnerSet}_test_results.csv`, active case 당 한 행, 모델당 `{response} [{model_id}]` 열 하나다. 기존 모델×case 단위 행 추가 함수를 case 별 집계로 바꾼다. 같은 표시명의 case 를 임의로 합치지 않는다.
- Run 시작 시 이전 CSV 를 삭제하고 실패하면 시작하지 않는다. CLI 의 내부 루프에서 잡은 예외도 최종 실패 코드에 반영한다. GUI 는 명시 결과 경로만 열며 실패 Run 의 부분 결과를 정상 완료로 표시하지 않는다.

### 하위호환

- v1 XML·Configuration·manifest 의 거부와 재생성 안내는 Sim + 1D 에만 적용한다. ND·MCU 의 기존 형식은 유효하다. manifest 버전은 `schema_version == 2` 하나로 판정하고 상태별 필수 구조를 검증한다.
- 계열 판별과 형식 호환은 별개다. 구형식 순수 1D Set 은 1D 로 분류되지만 v1 이므로 재생성 대상이다.
- 기존 ND Set 은 setId·폴더·산출물·Runner 참조를 유지한다. 1D v1 의 자동 변환이나 일반 호환 계층은 두지 않는다.
- Runner·Optimizer 의 `model_id` 없는 선택은 빈 선택으로 열고 다른 설정은 보존한다. 열기만으로 파일을 덮어쓰지 않는다.

## 3. 이슈 계층

```text
[Epic] 다중 응답·다중 모델 파이프라인 — Launcher XML 통합, Sim 1D 모델별 설정·산출물, set + model_id 참조
├─ 독립 결함 수정
│  ├─ DeepOpt: 실패 종료 코드와 명시 결과 경로를 제공한다
│  └─ GUI: 이번 실행의 결과 파일을 명시 경로로 연다
├─ 계열 경계
│  ├─ GUI: Builder 의 모델 계열을 명시하고 계약 경계를 나눈다
│  └─ GUI: Runner 가 참조 Builder 의 계열과 계약을 따른다
├─ 공통 참조·산출물
│  ├─ GUI: 모델 참조·산출물 판독·ID 발급을 공통화한다
│  ├─ DeepOpt: 산출물 저장·로딩·입력 검증의 공통 기반을 만든다
│  └─ DeepOpt: 트레이너 산출물을 model_id 디렉터리에 배치한다
├─ Preprocessor
│  ├─ GUI: Launcher 응답 표를 Config 로 저장·복원한다
│  ├─ GUI: XML 응답 메타를 배열로 쓰고 공유 파서를 함께 바꾼다
│  └─ GUI: Launcher Preprocess 가 XML 하나에 응답 N개를 쓴다
├─ Builder
│  ├─ GUI: Builder 설정과 옵션을 모델 ID 별 행으로 저장한다
│  ├─ GUI: 학습 시작 시 실행 모델의 manifest 를 초기화한다
│  ├─ GUI: 모델별 상태·오차·삭제를 manifest 기준으로 처리한다
│  └─ DeepOpt: Configuration 의 실행 행마다 1D 모델 하나를 학습한다
├─ Runner
│  ├─ GUI: Runner 에서 모델별 선택을 저장·복원한다
│  ├─ GUI: Runner 가 선택 모델의 참조를 해석해 한 번에 실행한다
│  └─ DeepOpt: 모델별 예측 결과를 case 당 CSV 한 행으로 모은다
└─ Optimizer
   ├─ GUI: Optimizer 가 여러 Builder 의 모델과 심볼을 저장·복원한다
   ├─ GUI: Optimizer 가 참조 모델을 해석해 새 CLI 계약으로 실행한다
   └─ DeepOpt: Optimizer 가 명시한 모델로 목적·제약식을 평가한다
```

### 선행 관계

| 작업 흐름 | 순서와 조건 |
|---|---|
| 독립 결함 수정 | DeepOpt 실패 종료 코드·명시 결과 경로 → GUI 명시 결과 열기 |
| Launcher·XML | 응답 표 영속은 독립 착수. Builder 계열 경계 → XML 메타 작성·공유 파서 전환 → XML 하나에 응답 N개 쓰기 |
| GUI 공통 참조 | #722 머지 → 모델 참조·산출물 판독·ID 발급 |
| Builder | GUI 공통 참조 + Builder 계열 경계 → 행별 설정·옵션 → 학습 시작·데이터셋 교체 → 상태·오차·삭제. 학습 시작에는 XML 메타·공유 파서 전환도 필요 |
| Runner | GUI 공통 참조 + Builder 계열 경계 → Runner 계열 경계 → 모델별 선택·복원 → 참조 해석·일괄 실행. 일괄 실행에는 GUI 명시 결과 열기도 필요 |
| Optimizer | GUI 공통 참조 → 다중 Builder 모델·심볼 → 최적화 실행 계약. 실행 계약에는 GUI 명시 결과 열기도 필요 |
| DeepOpt 학습 | 산출물·로딩·입력 공통 기반 → 트레이너 산출물 배치 → 행별 1D 학습. 행별 학습에는 실패 종료 코드 처리도 필요 |
| DeepOpt 소비 경로 | 산출물·로딩·입력 공통 기반과 실패 종료 코드 처리 뒤 모델별 예측·case 별 CSV, 선택 모델 식 평가를 병행 |

GUI 이슈와 DeepOpt 이슈는 각 저장소에 발행하고 연결한다. Builder 의 설정·학습 시작·상태 처리와 DeepOpt 행별 학습, Runner 일괄 실행과 DeepOpt 예측, Optimizer 실행 계약과 DeepOpt 식 평가는 같은 계약의 양쪽이므로 함께 통합 검증한다.

**코드 선행과 통합 검증 선행을 구분한다.** Runner 모델별 선택, Optimizer 다중 Builder 선택, Builder 상태·오차·삭제는 manifest fixture 로 먼저 구현할 수 있다. Builder 상태 처리보다 학습 시작 처리를 먼저 두는 것은 같은 파일의 수정 충돌을 피하기 위해서다.

실패 코드·결과 경로 수정, Builder 계열 경계, DeepOpt 공통 기반·트레이너 배치, Launcher 응답 표 영속은 #722 와 독립적으로 시작할 수 있다. Builder 계열 경계 뒤에는 XML 메타·공유 파서 전환과 XML 통합을 진행한다. #722 머지 뒤에는 GUI 공통 참조를 기반으로 Builder·Runner·Optimizer 작업을 진행한다.

임계 경로는 #722 리뷰 → GUI 공통 참조 → Builder 행별 설정 → 학습 시작 → 상태·오차·삭제 → Builder 통합 검증이다. Builder 행별 설정에는 계열 경계 작업도 필요하므로 선행 작업 추가가 일정에 영향을 주지 않는다고 단정하지 않는다.

통합 검증은 Launcher·1D Builder·Runner 의 작은 실행에서 시작해 Smart·부분 재학습·실패 처리와 다중 Builder Optimizer 로 넓힌다. ND·MCU 는 구형 XML 판독, 다중 응답 XML 의 필드 응답 전달, 학습·예측 1회로 회귀를 확인한다.

### dev 통합

기존 동작을 유지하는 실패 코드·결과 경로 수정, Builder 계열 경계, DeepOpt 공통 기반, Launcher 응답 표 영속, GUI 공통 참조의 헬퍼 추가분은 일반 절차로 먼저 머지한다. Runner 계열 경계도 형식 변경이 없으면 먼저 머지한다. 형식 전환 PR 은 양 저장소의 한시적 통합 브랜치에서 리뷰·검증한다.

1. 두 저장소 각각 dev 에서 `feat/multi-model` 을 분기한다.
2. 각 전환 PR 은 `feat/multi-model` 로 squash merge 한다.
3. 통합 검증 뒤 `feat/multi-model` 에서 dev 로 PR 하나를 만들어 squash merge 하고 브랜치를 삭제한다.
4. 검증한 GUI·DeepOpt 커밋 조합을 태그로 남기고 함께 배포한다.

잎 브랜치만 squash 하므로 [저장소 관리 수칙](https://github.com/NumeRealWorks/DashOpti_GUI/wiki/저장소-관리-수칙) 안의 절차다. 순차 머지를 위한 임시 v1/v2 이중 저장·장기 호환 계층·기능 플래그 체계는 추가하지 않는다.

fixture 는 두 저장소의 `tests/fixtures/multi_model_v2/` 에 같은 파일의 복사본을 둔다. 변경한 PR 에 양쪽 갱신을 연결하고 최종 통합 시 파일 일치를 확인한다. 한 저장소의 테스트가 다른 저장소 checkout 에 의존하지 않게 한다. 별도 공용 패키지는 만들지 않는다.

## 4. 이슈 초안

각 초안은 저장소 하나의 구현 PR 범위다. 공통 규격을 적용하며, 파일명은 조사 기준 코드와 #722 브랜치를 따른다.

### DeepOpt: 실패 종료 코드와 명시 결과 경로를 제공한다

현상

- 내부 루프에서 처리한 실패가 최종 종료 코드에 반영되지 않아 GUI 가 일부 실패를 정상 완료로 판단할 수 있다. 1D 예측 결과를 열 때 사용할 명시 CSV 경로도 필요하다.

범위

- 건드림: `main.py` 의 `train_model_1d`·`test_model_1d`·`run_optimization` 의 실패 집계와 CSV 경로 인자
- 안 건드림: 모델 선택, 설정 형식, CSV 행 집계, 학습·최적화 알고리즘

현재 구조

- 학습·예측·최적화 CLI 가 내부 예외를 처리한다. GUI 가 지정한 결과 경로와 CLI 의 저장 경로를 같은 계약으로 맞춰야 한다.

변경

- `main.py` 의 `train_model_1d`·`test_model_1d`·`run_optimization`. 내부 루프 실패를 집계하고 1D 예측에 명시 CSV 경로 옵션 추가. 모델 선택·설정 형식·CSV 행 집계는 바꾸지 않는다.

기대

- 모델 하나가 실패해도 최종 종료 코드가 0이 아니며 지정 CSV 에 기록한다. 기존 CLI 호출의 경로 기본값은 유지해 GUI 의 결과 열기 전환보다 먼저 적용할 수 있다.

Related: 선행 없음. 후속: GUI 의 명시 결과 열기, DeepOpt 의 행별 1D 학습·모델별 예측·선택 모델 식 평가. 기존 호출의 경로 기본값을 유지하므로 GUI 전환보다 먼저 적용할 수 있다.

### GUI: 이번 실행의 결과 파일을 명시 경로로 연다

현상

- Runner 가 지연 후 최신 CSV 를 찾아 열어 이전 실행 결과를 표시할 수 있다. Optimizer 가 기대하는 수렴 그림 경로도 DeepOpt 의 실제 출력 위치와 다르다.

범위

- 건드림: `DashModelRunner::run1DPrediction`·`onPredictionSucceeded`, `DashOptimizer::onJobFinished` 의 결과 경로·초기화·결과 열기
- 안 건드림: 모델 선택 형식, CSV 행 집계, 최적화 알고리즘

현재 구조

- Runner 는 성공 후 최신 CSV 를 탐색한다. Optimizer 는 `optimization_log/convergence_history.png` 를 기대하지만 DeepOpt 는 `<output_dir>/convergence_history.png` 를 쓴다.

변경

- `DashModelRunner::run1DPrediction`·`onPredictionSucceeded` 의 CSV 경로·초기화·결과 열기, `DashOptimizer::onJobFinished` 의 png 경로. 지연·최신 CSV 탐색 제거.

기대

- 두 번 실행해도 이번 Run 의 행만 표시하고 실패·CSV 삭제 실패를 정상 완료로 표시하지 않는다. 최적화 후 실제 출력 위치의 그림을 연다.

Related: 선행: DeepOpt 의 실패 종료 코드·명시 결과 경로. 후속: Runner 의 참조 해석·일괄 실행, Optimizer 의 실행 계약 전환.

### GUI: Builder 의 모델 계열을 명시하고 계약 경계를 나눈다

현상

- Sim Builder 가 1D·ND 타입을 함께 제공하고 첫 행으로 학습 명령을 고른다. MCU 도 base 의 여러 함수를 공유하므로 1D 형식을 바꾸기 전에 적용 경계를 확정해야 한다.

범위

- 건드림: `DashModelBuilder` 의 계열 판독·저장·분기, `loadDataLabelConfig` 의 Configuration 판독, `DashModelBuilderWidget` 의 첫 설정 선택 UI
- 안 건드림: Configuration·manifest 직렬화 형식 교체, MCU override 변경, 새 variant·클래스 계층 도입

현재 구조

- 1D 7종과 ND 5종이 같은 콤보와 Configuration dict 를 쓴다. `(Field)` 는 응답 표시 규칙이고 계열 식별자가 아니다. MCU 는 base 함수를 상속하거나 명시 호출한다.

변경

- `DashModelBuilder` 에 `modelFamily` 기록·판독·잠금과 기존 Set 분류를 추가한다. 공통 규격의 계열·계약 판독값과 분기점을 정의하고, `loadDataLabelConfig` 의 Configuration 판독을 분리한다. 타입 목록·reduction 규칙·서브커맨드는 계열값으로 정하고 미분류 Set 은 차단한다. `DashModelBuilderWidget` 에 첫 설정 선택 UI 와 잠금 표시를 추가하고 `(Field)` 문자열 검출을 삭제한다. 직렬화 형식과 MCU override 는 그대로다. 첫 행 타입으로 서브커맨드를 정하던 코드를 지운다.

기대

- Sim 1D·Sim ND·MCU 의 생성·재열기·학습·폴링·삭제가 현행과 같다. 순수 ND 구 Set 이 ND 로 분류돼 그대로 동작하고 다음 저장 때 키가 기록된다. 혼합·알 수 없는 Set 은 저장·실행이 차단되고 안내가 뜬다 (유일한 동작 변화. 현재 혼합 Set 은 다른 계열 행이 Refused 되는 상태). 타이머 연결, base 포인터 호출, MCU 의 명시 base 호출 (`DashModelBuilderMCU.cpp:805`) 경로를 검증에 포함한다. 구형 XML 1개와 다중 응답 XML 1개 fixture 로 ND Set 이 선택한 필드 응답을 그대로 받는지 확인한다.

Related: 선행 없음. 후속: XML 메타 작성·파서 전환, Builder 행별 설정, Runner 계열 경계. 형식 변경이 없으므로 dev 에 먼저 통합한다.

### GUI: Runner 가 참조 Builder 의 계열과 계약을 따른다

현상

- Runner 가 행별 타입으로 1D·ND 를 나누고 같은 설정을 두 번 써서 실행한다. Builder 에서 확정한 계열·계약과 Runner 의 실행 판단을 일치시켜야 한다.

범위

- 건드림: `DashModelRunner`·`DashModelRunnerWidget`·PresentationModel 의 표·실행 모드, `groupCheckedPairs`, `updateModelUploadConfig`
- 안 건드림: v2 모델 선택 영속 형식, MCU Runner, ND 엔진 계약

현재 구조

- `isNDModel` 과 타입 접두 판별로 행을 분류하고, `groupCheckedPairs` 가 ND·1D 를 나눈 뒤 설정을 각각 쓴다.

변경

- `DashModelRunner`·`DashModelRunnerWidget`·PresentationModel 이 `LoadedArtifact` 의 계약으로 표·실행 모드를 정한다. 행별 `isNDModel` 판별, `groupCheckedPairs` 의 ND·1D 분할, `updateModelUploadConfig` 이중 쓰기 제거. 기존 형식 대상.

기대

- 1D Builder 와 ND Builder 각각 현행과 같은 실행 결과. 한 Run 은 한 계열. #724 의 이중 쓰기 항목 해소를 확인한다.

Related: 선행: GUI 공통 참조·계약 판독, Builder 계열 경계. 후속: Runner 모델별 선택·복원. #724 의 이중 쓰기 제거를 포함한다. 형식 변경이 없으면 dev 에 먼저 통합하고, 형식이 바뀌면 통합 브랜치에 넣는다.

### GUI: 모델 참조·산출물 판독·ID 발급을 공통화한다

현상

- 기존 모델 참조와 오차 판독은 응답·타입 중심이어서 같은 타입의 모델 여러 개를 구분하지 못한다. ND·MCU 의 기존 형식을 보존하면서 v2 모델을 공통으로 판독해야 한다.

범위

- 건드림: `DashModelBuilderArtifact`, `DashModelBuilderReference`, `LoadedArtifact`, `DashSurrogateModelCommon` 의 참조·판독·표시 자료와 fixture 경로 제공
- 안 건드림: Runner·Optimizer 의 소비 UI 교체, Builder 학습 실행, DeepOpt

현재 구조

- #722 가 Builder setId 를 폴더·model_info 로 해석하는 참조 계층을 도입한다. 기존 산출물의 오차는 최상위 `errors` 에 있고 `model_id` 참조는 없다.

변경

- `DashModelBuilderArtifact` 에 ModelRef·ModelEntry·상태별 판독, `DashModelBuilderReference` 에 ID 발급·`modelDir`·`resolveModelFile`, `LoadedArtifact` 에 variant·`modelFamily`·계약. v2 manifest 검증은 계약이 v2 일 때만 호출한다. `DashSurrogateModelCommon` 의 공통 표시 자료 (`ModelEntry` 행 자료, usable 필터). fixture 경로 제공 방식 (CMake 복사 또는 경로 매크로) 을 정한다. 소비 UI 교체는 Runner 모델별 선택·복원과 Optimizer 다중 Builder 선택 소관.

기대

- 참조 round-trip, v1 거부 (v2 계약에서만), ND 계약 Builder 의 v1 manifest 통과, In Progress 와 Done 의 필수 필드 차이, 고정 경로 검증, 삭제 후 ID 미재사용. 기존 호출부를 유지한 헬퍼 추가까지는 단독 적용 가능.

Related: 선행 #722. 후속: Builder 행별 설정, Runner 계열 경계·모델별 선택, Optimizer 다중 Builder 선택. 기존 호출부를 유지하는 헬퍼 추가분은 단독 통합할 수 있다.

### DeepOpt: 산출물 저장·로딩·입력 검증의 공통 기반을 만든다

현상

- v2 는 모델별 manifest 와 명시 파일 경로·실제 타입·입력 순서를 사용한다. 저장·예측·최적화가 이 계약을 같은 방식으로 처리할 공통 함수가 필요하다.

범위

- 건드림: 신규 `source/artifact.py`, `optimize/pred_surrogates.py`, `preprocessor/xml_parser.py`, `tests/` 와 공통 fixture
- 안 건드림: CLI 전환, ND 파서 호출·기존 로더 호출의 변경, 별도 공용 패키지

현재 구조

- 기존 로더는 경로 문자열과 파일 탐색에 의존한다. 조사 기준 DeepOpt 저장소에는 `tests/` 디렉터리와 CI 가 없다.

변경

- 신규 `source/artifact.py` 의 manifest 원자 갱신 (한정 재시도)·명시 타입 로더·입력 어댑터, `optimize/pred_surrogates.py` 의 로더 연결, `preprocessor/xml_parser.py` 의 1D 중복 키 검증. `tests/` 신설 (pytest 설정, conftest, 더미 모델, `tests/fixtures/multi_model_v2/`). 현재 저장소에 `tests/` 디렉터리와 CI 가 없다. CLI 전환은 제외.

기대

- 다른 manifest 항목 보존, 타입별 저장 파일 재로딩, 순서 반전·누락·중복·길이/차원 오류 검증, 재시도 뒤 최종 실패 전파. ND 의 파서 호출과 기존 로더 호출은 유지한다.

Related: 선행 없음. 후속: 트레이너 산출물 배치, 모델별 예측·case 별 CSV, 선택 모델 식 평가. GUI 와 같은 fixture 를 각 저장소에 복사해 사용한다.

### DeepOpt: 트레이너 산출물을 model_id 디렉터리에 배치한다

현상

- 응답·타입·오차를 경로에 넣는 기존 배치는 같은 타입의 여러 모델과 모델별 재학습을 안정적으로 구분하기 어렵다. Smart 의 우승 모델도 부속 파일과 함께 보존해야 한다.

범위

- 건드림: `models/oned/*trainer.py`, `smart_trainer.py`, `run_train_1d._save_model_info_json` 의 저장 경로·후보 정리·모델별 오차 기록
- 안 건드림: CLI 의 Configuration 행 순회·최종 종료 판정, ND 트레이너, 학습 알고리즘

현재 구조

- 기존 산출물은 `{out}/{response}/{Type}_{err}` 형태이며, model_info 의 최상위 `errors` 에 오차를 기록한다. Smart 는 후보를 정리해 우승 모델을 남긴다.

변경

- `models/oned/*trainer.py`, `smart_trainer.py`, `run_train_1d._save_model_info_json`. model_id 디렉터리·부속 파일·Smart 후보 정리·모델별 오차 저장. CLI 행 순회·종료 판정은 행별 1D 학습 소관.

기대

- 같은 타입 두 모델의 파일이 공존하고, 재학습 대상만 정리한다. Smart 의 RF·MLP·BNN 우승 사례에서 재로딩과 `Model_Error.csv` 보존을 확인한다.

Related: 선행: DeepOpt 산출물·로딩·입력 공통 기반. 후속: DeepOpt 행별 1D 학습. 저장 파일의 타입별 재로딩을 함께 검증한다.

### GUI: Launcher 응답 표를 Config 로 저장·복원한다

현상

- Launcher 의 Output Response 표가 Config 를 거치지 않고 직접 저장되며, 위젯을 다시 열었을 때 같은 표로 복원하는 경로가 없다.

범위

- 건드림: `DashAnalysisLauncherConfig`, `DashAnalysisLauncherPresentationModel::saveOutputResponse`, 위젯 열기 시 응답 표 복원
- 안 건드림: XML 메타·샘플 형식, Preprocess 요청 루프

현재 구조

- `saveOutputResponse` 가 `root["Output Response"]` 를 직접 read-modify-write 한다.

변경

- `DashAnalysisLauncherConfig` 의 Output Response 읽기/쓰기, `DashAnalysisLauncherPresentationModel::saveOutputResponse`, 위젯 열기 시 복원. XML 형식은 제외.

기대

- 응답 여러 개의 이름·component·step·substep 을 저장·재열기해 같은 표로 복원한다.

Related: 선행 없음. XML 형식 전환과 독립적으로 dev 에 먼저 통합할 수 있다.

### GUI: XML 응답 메타를 배열로 쓰고 공유 파서를 함께 바꾼다

현상

- XML 작성과 Builder 파서가 단수 응답 메타를 전제로 한다. 응답 배열을 도입하면서 ND 의 구형 XML 판독도 보존해야 한다.

범위

- 건드림: `DashResultTypes.h`, `DashResultXmlWriter::writeModelInfoToXml`, Launcher·KPI 호출부, Builder XML 파서·학습 시작의 메타 복사, `DashXmlTailLocator`
- 안 건드림: 샘플 텐서 통합, KPI·BORE/BOSS 파일 통합, 1D 학습 시작의 구형 XML 거부

현재 구조

- 작성부는 `selected_response` 단수 메타를 조립하고, `parseModelInfoStream`·`readSelectedResponseFromStream` 과 꼬리 파싱도 같은 구조를 가정한다.

변경

- `DashResultTypes.h` 의 SelectedResponse, `DashResultXmlWriter::writeModelInfoToXml` 과 호출부 (Launcher 1곳, `DashAnalysisLauncherKPI.cpp` 6곳), `DashModelBuilder::parseModelInfoStream`·`readSelectedResponseFromStream` 의 양식 판독, `DashXmlTailLocator`. 학습 시작의 복사 지점은 파서의 목록 구조를 두 계열 모두 `selected_responses` 로 쓴다. 구형 거부는 Builder 학습 시작·데이터셋 교체 작업의 1D 경로에 둔다.

기대

- 1D 생산·소비 경로에서 배열 2개·substep·텐서 키 대응·꼬리 파싱을 검증한다. 구형 단수 XML 이 같은 구조로 읽히고 구형 표시가 붙는다. KPI 등 별도 XML 도 1D 가 소비하는 메타 변경은 함께 반영하되 XML 파일 자체는 통합하지 않는다.

Related: 선행: Builder 계열 경계. 후속: XML 하나에 응답 N개 쓰기, Builder 학습 시작·데이터셋 교체. 구형 XML 거부는 1D 학습 시작에 한정한다.

### GUI: Launcher Preprocess 가 XML 하나에 응답 N개를 쓴다

현상

- Preprocess 가 응답 요청마다 XML 을 만들고 샘플 파일을 반복해서 연다. 한 데이터셋에서 여러 응답을 학습하려면 같은 샘플 dict 에 응답을 모아야 한다.

범위

- 건드림: `DashAnalysisLauncher::processResults`, `DashResultProcessor::processSamples`, `DashResultXmlWriter::appendSample`, `DashResultBatch::outputFileName`, Builder 데이터셋 목록
- 안 건드림: 다른 component 의 topology 분리, KPI·BORE/BOSS 별도 XML 통합, DeepOpt 파서 구현

현재 구조

- 요청별 루프 안에서 XML 을 만들고 샘플을 순회한다. 샘플당 응답 성공 판정과 topology 슬롯도 단일 응답·component 를 전제로 한다.

변경

- `DashAnalysisLauncher::processResults`, `DashResultProcessor::processSamples`, `DashResultXmlWriter::appendSample`, `DashResultBatch::outputFileName`, Builder 데이터셋 목록. 키/component 검증을 시작 전에 수행한다.

기대

- 샘플당 파일 열기 1회, 응답 누락 샘플 제외, 요청별 시점 조회, 키 충돌·다른 component 거부. 거부 시 기존 XML 유지. ND Set 이 이 XML 에서 필드 응답 하나를 선택해 현행대로 학습한다. DeepOpt 중복 키 검증은 DeepOpt 산출물·로딩·입력 공통 기반 소관.

Related: 선행: XML 메타 작성·공유 파서 전환. DeepOpt 중복 키 검증은 산출물·로딩·입력 공통 기반에 포함한다. ND 의 필드 응답 전달을 회귀 검증한다.

### GUI: Builder 설정과 옵션을 모델 ID 별 행으로 저장한다

현상

- Configuration 이 타입을 키로 한 객체이고 옵션도 타입별로 공유하므로 같은 타입의 서로 다른 모델을 구성할 수 없다.

범위

- 건드림: v2 Configuration 조립·복원, `DashModelBuilderPresentationModel::TrainingRowInput`·`buildTrainingStartPlan`, Sim 위젯의 1D 행·옵션·`restoreConfigurationUI`
- 안 건드림: 상태 폴링, manifest 작성, ND·MCU 의 v1 행 모델·옵션 동작

현재 구조

- 기존 Configuration dict 는 타입마다 행 하나를 표현하고, 옵션 위젯도 `m_configWidgets[modelName]` 으로 관리한다. 공유 base 위젯과 MCU 위젯은 기존 계약을 쓴다.

변경

- v2 계약의 Configuration 배열 조립·복원, `DashModelBuilderPresentationModel::TrainingRowInput`·`buildTrainingStartPlan`, `DashModelBuilderWidget` 의 1D 행·옵션 (base 위젯의 행 함수를 virtual 로 두고 Sim 위젯이 1D 일 때 override), `restoreConfigurationUI`. `DashModelBuilderWidgetBase` 와 MCU 위젯은 v1 행 모델을 유지한다. 상태 폴링은 제외.

기대

- 같은 타입 두 행의 ID·run·옵션이 재열기 후 유지된다. 타입 변경 시 해당 행 옵션만 교체하고 transformation 값도 복원한다. 로드·실행 시 계열과 행 타입 불일치를 거부한다. ND·MCU 의 행·옵션 동작은 현행과 같다.

Related: 선행: GUI 공통 참조·ID 발급, Builder 계열 경계. 후속: Builder 학습 시작·데이터셋 교체. DeepOpt 행별 1D 학습과 같은 Configuration 계약을 사용한다.

### GUI: 학습 시작 시 실행 모델의 manifest 를 초기화한다

현상

- 부분 재학습에서는 실행할 모델만 초기화해야 하고, 다른 데이터셋으로 바꿀 때는 기존 학습 결과를 무효화해야 한다. 두 경우를 구분하지 않으면 마지막 학습 메타를 잃거나 다른 데이터셋의 결과를 재사용하게 된다.

범위

- 건드림: 1D 학습 시작의 manifest 작성 함수, 데이터셋 출처 비교·교체 확인, 응답 사전 검증, `QSaveFile` 저장·재시도
- 안 건드림: ND 학습 시작, 같은 파일의 내용 변경 감지, DeepOpt 의 재학습 폴더 정리

현재 구조

- Builder 가 XML 의 parameter·응답·originRecord 를 model_info 로 복사한다. v2 에서는 실행 행의 상태·메타와 미실행 행의 마지막 학습 메타를 구분해 기록해야 한다.

변경

- 1D 학습 시작의 manifest 작성을 함수로 분리. 구형 XML 거부, 출처 비교 (producer setId + 파일명), 응답 스칼라 사전 검증, 실행 행 초기화, `QSaveFile` 저장과 한정 재시도. ND 경로의 학습 시작은 그대로다.

기대

- 부분 재학습에서 미실행 메타를 보존하고 Data Label 편집만으로 전체 삭제하지 않는다. 다른 데이터셋 교체·삭제 확인 취소·쓰기 실패·구형 XML 거부를 검증한다. 재학습 폴더 정리는 DeepOpt 의 행별 1D 학습이 공통 산출물 정리 기능을 호출한다.

Related: 선행: XML 메타 작성·공유 파서 전환, Builder 행별 설정·옵션. 후속: Builder 상태·오차·삭제. 같은 파일의 내용 변경 감지는 #650 소관이다.

### GUI: 모델별 상태·오차·삭제를 manifest 기준으로 처리한다

현상

- 상태·오차·산출물 삭제가 응답·타입 중심이고, 취소 통지가 실제 프로세스 종료보다 먼저 발생한다. 이 상태에서 manifest 보정이나 삭제를 시작하면 실행 중 쓰기와 충돌할 수 있다.

범위

- 건드림: v2 상태 폴링·최종 보정, 학습 결과·오차·산출물 목록·삭제, 위젯의 모델 행 갱신, `ProcessJob` 의 실제 종료 신호
- 안 건드림: Configuration 형식, ND·MCU 의 기존 폴링·삭제 본문, DeepOpt 학습 구현

현재 구조

- 상태는 Set json, 오차는 model_info 최상위 `errors`, 산출물은 응답·타입별 경로를 사용한다. `ProcessJob::cancel()` 은 QProcess 를 떼어내고 종료 관측 전에 `Cancelled` 로 전이한다.

변경

- v2 계약의 `checkModelStatusInternal`·`finalizeStaleStatuses`, `loadTrainedModelInfo`·`refreshTrainedModelInfo`, 산출물 목록·`getTestDatasetFiles`·`deleteTrainedModel`, 위젯의 상태 갱신·행 삭제. `ProcessJob` 에 실제 종료 신호를 두고 보정·재실행·삭제 허용을 그 신호에 묶는다. 부분 삭제 실패와 보정 저장 실패 처리. ND·MCU 분기는 v1 본문을 유지한다.

기대

- 학습 중 UI·함수 양쪽의 삭제 거부, 취소 뒤 실제 종료 전 보정 없음, 종료 보정 후 재실행, 보정 저장 실패 시 차단, 한 모델 삭제 시 다른 모델 보존, 부분 삭제 실패 모델이 usable 이 아님. MCU·ND 의 폴링·삭제가 현행과 같다. 실학습 검증에는 DeepOpt 행별 1D 학습이 필요하다.

Related: 선행: Builder 학습 시작·데이터셋 교체 (같은 파일의 수정 충돌 회피). manifest fixture 로 먼저 구현할 수 있고, 실학습 검증에는 DeepOpt 행별 1D 학습이 필요하다.

### DeepOpt: Configuration 의 실행 행마다 1D 모델 하나를 학습한다

현상

- 기존 1D 학습은 타입별 Configuration 과 전체 Output 라벨을 전제로 한다. 모델별 응답·입력 순서·상태를 독립적으로 기록하고 행 실패를 최종 종료 코드에 반영해야 한다.

범위

- 건드림: `main.py::train_model_1d`, `run_train_1d`, `XMLTrainingDataBuilder.build_1d` 의 행 순회·입력 검증·상태 기록·실패 집계
- 안 건드림: `train_model_nd`, `_update_json_status`, transformation 계산, 학습 알고리즘

현재 구조

- `train_model_1d` 는 Configuration dict 를 순회하며 행의 응답 하나로 학습을 제한하지 않는다. reduction 비교의 `SUM` 과 GUI 의 `Sum` 표기도 다르다.

변경

- `main.py::train_model_1d`, `run_train_1d`, `XMLTrainingDataBuilder.build_1d`. Configuration 배열의 run 행만 처리하고 각 row.response 하나를 학습한다. 입력 검증 (라벨 존재·스칼라·유한값·열 수)·응답 스칼라 검증·input_order 반환·reduction 정규화·행별 상태·실패 집계를 연결한다. `train_model_nd` 와 `_update_json_status` 는 바꾸지 않는다.

기대

- 같은 타입 두 행의 별도 산출물, run:false 보존, Sum 계산, 실제 학습 열 순서 기록, 다성분 응답·비유한 값 거부, 한 행 실패 시 성공 행 보존·최종 비정상 종료.

Related: 선행: DeepOpt 실패 종료 코드·명시 결과 경로, 트레이너 산출물 배치. GUI 의 행별 설정·학습 시작·상태 처리와 통합 검증한다.

### GUI: Runner 에서 모델별 선택을 저장·복원한다

현상

- 응답·타입 쌍으로 선택을 저장하면 같은 응답과 같은 타입의 모델 여러 개를 구분할 수 없다. 실행하지 않고 체크만 바꿔도 선택이 보존돼야 한다.

범위

- 건드림: `DashModelRunnerConfig` 의 선택 읽기/쓰기·별도 영속 키, `DashModelRunnerWidget::populateSurrogateTable` 의 v2 모드, PresentationModel 의 선택 수집
- 안 건드림: Runner 의 단일 Builder 참조, ND 모드의 기존 경로, CLI 실행 조립

현재 구조

- 기존 표는 응답과 모델 타입을 조합해 선택한다. 실행용 `Model upload.Output Response[]` 와 사용자 선택의 영속 상태를 분리하는 작업이 #724 에 있다.

변경

- `DashModelRunnerConfig` 의 선택 읽기/쓰기와 별도 영속 키, `DashModelRunnerWidget::populateSurrogateTable` 의 v2 모드, PresentationModel 의 선택 수집. usable 모델당 한 행으로 바꾼다. ND 모드는 Runner 계열 경계 작업에서 분리한 기존 경로를 유지한다.

기대

- 같은 응답·같은 타입의 서로 다른 ID 를 독립 선택·복원한다. 실행 없이 선택만 바꿔도 영속 키에 반영된다. #724 의 두 항목 (영속 분리, 이중 쓰기 제거) 을 모두 확인한 뒤 종료한다.

Related: 선행: Runner 계열 경계, GUI 공통 참조·판독. #724 를 흡수하며 선택 영속 분리와 이중 쓰기 제거를 모두 확인한다. 후속: Runner 참조 해석·일괄 실행.

### GUI: Runner 가 선택 모델의 참조를 해석해 한 번에 실행한다

현상

- 실행용 참조는 저장 당시의 표시 정보만으로 확정할 수 없다. 선택한 모든 모델의 파일·실제 타입·입력 순서를 실행 직전에 확인해야 한다.

범위

- 건드림: `DashModelRunner::run1DPrediction` 과 엔진 입력 조립·저장·CLI 호출
- 안 건드림: 모델 선택 UI·영속 키, DeepOpt CSV 집계, ND 엔진 계약

현재 구조

- Runner 는 Builder 참조와 저장된 선택으로 엔진 입력을 만든다. v2 실행에는 manifest 에서 해석한 절대 파일 경로·`trained_type`·`input_order`·응답 메타가 필요하다.

변경

- `DashModelRunner::run1DPrediction` 과 엔진 입력 조립. 전체 참조의 파일·실제 타입·입력 순서·응답 메타를 해석한 뒤 1회 저장·1회 CLI 실행한다.

기대

- 한 참조가 실패하면 저장·실행하지 않는다. DeepOpt 모델별 예측·case 별 CSV 와 연동해 2 case × 2 model 의 CSV·재실행·부분 실패를 검증한다.

Related: 선행: GUI 명시 결과 열기, Runner 모델별 선택·복원. DeepOpt 모델별 예측·case 별 CSV 와 함께 실행 결과를 검증한다.

### DeepOpt: 모델별 예측 결과를 case 당 CSV 한 행으로 모은다

현상

- 기존 CSV 는 응답 이름을 열로 사용해 같은 응답의 모델 여러 개를 구분하지 못하고, 모델×case 단위 행 추가로 결과가 흩어진다.

범위

- 건드림: `main.py::test_model_1d`, `_write_1d_test_result_to_csv`, `RunTest1D` 의 로딩·입력 재배열·결과 집계
- 안 건드림: `test_model_nd`, ND 결과 형식, 모델 학습·선택 UI

현재 구조

- 1D 예측은 기존 경로의 glob 으로 모델을 찾고 응답 이름으로 CSV 를 기록한다. v2 는 각 항목의 명시 경로와 모델 ID 를 사용한다.

변경

- `main.py::test_model_1d`, `_write_1d_test_result_to_csv`, `RunTest1D`. 공통 로더·입력 어댑터를 연결하고 결과를 case 당 한 행으로 집계한다.

기대

- 같은 응답의 모델 두 개·입력 순서 반전·case 두 개로 정확히 2행·모델 열 2개. 같은 표시명의 case 도 별도 행이며 참조/예측 실패를 건너뛰어 성공 처리하지 않는다.

Related: 선행: DeepOpt 실패 종료 코드·명시 결과 경로, 산출물·로딩·입력 공통 기반. GUI Runner 일괄 실행과 같은 CSV 계약을 사용한다.

### GUI: Optimizer 가 여러 Builder 의 모델과 심볼을 저장·복원한다

현상

- Optimizer 가 Builder 하나의 응답·모델을 기준으로 복원하고 심볼을 다시 부여하면 여러 Builder 의 모델과 식의 참조 관계를 유지할 수 없다.

범위

- 건드림: `DashOptimizer` 의 SurrogateModelInfo·save/load·DV 복원, `DashOptimizerWidget::populateSurrogateTable`, 기본 Builder 선택·Preview·`performMorphing`
- 안 건드림: 목적·제약식 편집기, 프로세스 호출, 최적화 알고리즘

현재 구조

- `modelBuilder {set, name}` 은 Builder 단일 참조이며 DV·Preview 의 출처다. 기존 모델 항목은 응답·타입·심볼 중심이고 `selectModelBuilderFolder` 는 이름 일치를 추정한다.

변경

- `DashOptimizer` 의 SurrogateModelInfo·save/load·DV 복원, `DashOptimizerWidget::populateSurrogateTable` (v2 Builder 만 나열, `(Field)` 검출 삭제), Preview·`performMorphing` 의 기본 Builder 선택. `selectModelBuilderFolder` 의 이름 일치 추정을 제거한다. 식 편집기는 바꾸지 않는다.

기대

- Builder 두 개의 모델 세 개·심볼을 저장/복원한다. 입력 집합 불일치, 사용 중 심볼 삭제, Geometry 출처 불일치 시 Preview 제한을 검증한다. #726 의 재적용 작업과 수정 범위를 맞춘다.

Related: 선행: GUI 공통 참조·판독. 후속: Optimizer 실행 계약 전환. #726 의 Optimizer 재적용 작업과 수정 범위를 맞춘다. manifest fixture 로 먼저 구현할 수 있다.

### GUI: Optimizer 가 참조 모델을 해석해 새 CLI 계약으로 실행한다

현상

- Builder 디렉터리 하나를 인자로 넘기는 기존 호출은 여러 Builder 에서 고른 모델을 명시하지 못한다. 실행 직전에 모든 참조의 v2 계약과 모델 파일을 다시 확인해야 한다.

범위

- 건드림: `DashOptimizer::runOptimization` 의 참조 해석·엔진 입력 저장·argv 조립
- 안 건드림: 모델 선택 UI·심볼 영속, 최적화 알고리즘, 결과 그림 경로 수정

현재 구조

- 현재 호출은 `run-optimization <trainedModelPath> <json> --output-dir <dir>` 이고 Builder 폴더에서 `trainedModelPath` 를 만든다.

변경

- `DashOptimizer::runOptimization` 의 모든 참조 해석 (Builder 계약 v2 재확인 포함)·엔진 입력 저장·argv. 호출은 `run-optimization <OptSet.json> --output-dir <dir>` 이며 Builder 디렉터리 인자는 제거한다.

기대

- 참조 실패나 v2 가 아닌 Builder 참조 시 저장·실행하지 않는다. DeepOpt 의 선택 모델 식 평가와 연동해 선택한 모델로 실행하고, GUI 는 명시한 결과 경로의 파일을 표시한다.

Related: 선행: GUI 명시 결과 열기, Optimizer 다중 Builder 모델·심볼 선택. DeepOpt 선택 모델 식 평가와 같은 CLI 계약으로 통합 검증한다.

### DeepOpt: Optimizer 가 명시한 모델로 목적·제약식을 평가한다

현상

- 기존 최적화가 응답 폴더에서 최저 오차 파일을 고르면 GUI 에서 선택한 모델이 다른 모델로 대체된다. 일반 응답과 `std_pred` 의 입력 순서도 같게 처리해야 한다.

범위

- 건드림: `main.py::run_optimization`, `MainOptimizer`, `problem_setup.py`, `symbolic_module.ExpressionEvaluator` 의 모델 로딩·입력 매핑·식 평가 연결
- 안 건드림: 최적화 알고리즘, `optimum.json` 형식, 별도 fitting 경로

현재 구조

- `_build_response_paths` 가 응답 경로 아래의 모델 파일을 탐색해 최저 오차 파일을 고른다. `predict_responses` 와 `ExpressionEvaluator` 의 일반 응답·`std_pred` 를 함께 전환해야 한다.

변경

- `main.py::run_optimization`, `MainOptimizer`·`problem_setup.py` 의 문제 정의/경로 조립, `symbolic_module.ExpressionEvaluator` 의 일반 응답·std_pred. 공통 로더·입력 어댑터를 사용한다. 최적화 알고리즘·optimum.json·별도 fitting 경로는 유지한다.

기대

- Builder 두 개의 모델 세 개로 입력 순서 반전·Smart 실제 타입을 검증하고 목적·제약·std_pred 계산값까지 확인한다. 최저 오차 파일 탐색이 선택한 모델을 대체하지 않는다.

Related: 선행: DeepOpt 실패 종료 코드·명시 결과 경로, 산출물·로딩·입력 공통 기반. GUI Optimizer 실행 계약과 함께 검증한다.

## 5. 범위 밖과 확인 사항

### 범위 밖

- ND·MCU 의 v2 전환은 제외한다. 기존 Configuration·상태·산출물 계약을 유지하고 공유 코드의 분기와 회귀만 확인한다.
- 다른 component 의 응답 통합과 벡터 DV 펼침은 제외한다. 같은 component·충돌 없는 응답 키·스칼라 DV 를 1차 제약으로 둔다.
- KPI·BORE/BOSS 의 별도 XML 은 하나로 통합하지 않는다. 1D 가 소비하는 응답 메타와 공유 파서는 함께 전환한다.
- 모델 이력·복구와 같은 XML 의 내용 변경 감지는 제외한다. 내용 변경 감지는 #650 소관이다.
- DOE 리샘플링의 모델 참조는 #684 소관이다. Runner 는 Builder 하나를 참조하고, 여러 Builder 의 모델 선택은 Optimizer 에만 적용한다.
- transformation 계산은 제외한다. 값 보존·복원과 미적용 표시까지만 구현한다.

### 착수 전 확인

- 대상 Deck 의 응답들이 같은 component·서로 다른 정규화 키라는 1차 제약을 만족하는지 확인한다.
- Builder 계열 경계 작업 전 기존 프로젝트의 Sim Set 에 공통 규격의 분류 규칙을 적용해 순수 ND·순수 1D·혼합·미분류 수를 센다. 차단 범위와 재생성 범위를 미리 확인한다.
- ND 회귀용 fixture 로 구형 단수 XML 1개와 다중 응답 XML 1개를 확보한다.
