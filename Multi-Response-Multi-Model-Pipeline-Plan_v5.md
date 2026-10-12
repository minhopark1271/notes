# 다중 응답·다중 모델 파이프라인 — 공통 규격 설계와 작업 계획 (v5)

> 관련 Issue: 선행 #722. 접점 #724 · #650 · #684 · #726.
> 상태: **코드 조사 기반 설계안** — 2026-10-11, GUI `a076fde7`, #722 브랜치의 참조 구조, DeepOpt `a4222b6` 기준. 구현 착수 시 좌표를 재확인한다.
> 이전 문서: [원안](Multi-Response-Multi-Model-Pipeline-Plan.md), [v2](Multi-Response-Multi-Model-Pipeline-Plan_v2.md), [v3](Multi-Response-Multi-Model-Pipeline-Plan_v3.md), [v4](Multi-Response-Multi-Model-Pipeline-Plan_v4.md).
> 범위: **Sim 1D·ND의 모델 관리 형식 통일. 기존 Sim 설정·XML·학습 결과는 재생성을 요구한다.** MCU는 기존 계약을 유지하고, Optimizer는 Sim 1D만 지원한다.
> 해상도: 원안과 같은 이슈 초안 양식 (`현상 / 범위 / 현재 구조 / 변경 / 기대 / Related`). 임시 작업 번호 없이 작업명으로 선행 관계를 연결한다.

## 1. 조사로 바뀐 전제

v4는 Sim 1D만 새 형식으로 전환하고 ND의 기존 설정·상태·산출물을 보존했다. v5는 Sim 1D·ND의 Configuration, 모델 ID, 상태·오차, 산출물 경로와 소비 측 참조를 함께 통일한다. 기존 Sim 데이터를 다시 생성할 수 있으므로 구형 계열 추정·자동 변환·선택 복원은 구현하지 않는다.

| 조사 결과 | v5에 반영할 내용 |
|---|---|
| Sim 1D·ND는 같은 Builder의 Configuration 저장·복원·상태 조회를 사용한다 (`model/DashModelBuilder.cpp:648`, `:768`, `:1058`, `:1622`) | 두 계열 모두 같은 배열 설정과 `models[id]`를 사용한다. Sim 내부에서 형식 버전으로 분기하지 않는다 |
| ND 학습도 Configuration dict를 순회하고 `_update_json_status`로 Set JSON에 상태를 쓴다 (`DeepOpt/main.py:249`, `:282`) | ND CLI도 행별 실행과 manifest 상태 기록으로 전환한다 |
| ND의 `ResultSaver`는 응답·타입·오차 경로와 최상위 `errors`를 쓴다 (`source/trainer_utils/result_saver.py:40`, `:151`) | ND의 오차·산출물 배치까지 모델 ID 기준으로 바꾼다. 체크포인트 내용과 전처리 메타는 유지한다 |
| ND Runner는 첫 Output Response를 사용하고 glob으로 모델을 고른다 (`main.py:473`, `:561`) | 선택 모델 전부를 명시 파일 경로로 실행하고 case·모델별 결과를 분리한다 |
| `RunTestNDFromVTU`는 전달된 `.pt` 대신 첫 `.ckpt`를 고를 수 있고, DV 키를 정렬하며 입력 VTU에 결과를 쓴다 (`source/run_test_nd.py:873`, `:916`, `:952`) | 지정한 파일·학습 입력 순서를 그대로 사용하고 별도 결과 VTU에 쓴다 |
| ND 직접 VTU 예측은 현재 모든 모델 타입에서 구현되어 있지 않다 (`source/run_test_nd.py:899` 이후) | 기존 지원 범위를 명시하고 미지원 타입은 실행 전에 거부한다. 새 추론 알고리즘 개발은 별도 범위로 둔다 |
| MCU는 Builder의 설정 판독·오차·상태 함수와 XML 파서를 상속하거나 명시 호출한다 (`model/DashModelBuilderMCU.cpp:666`, `:773`, `:805`) | Sim 전환 전에 MCU의 기존 처리 경계를 분리한다. MCU용 기존 본문을 Sim의 구형 fallback으로 사용하지 않는다 |
| `ProcessJob::cancel()`은 실제 종료 관측 전에 `Cancelled`로 전이한다 (`controller/async/ProcessJob.cpp:97`) | 형식 통일과 별도로 실제 종료 뒤 manifest 보정·재실행·삭제를 허용한다 |

| 결정 항목 | v5 결정 |
|---|---|
| Sim 관리 형식 | 1D·ND 모두 v2. Configuration 배열, `model_id`, `models[id]`, 고정 모델 경로, 명시 참조 |
| 모델 계열 | `modelFamily`를 명시하고 고정한다. 모델 목록·입출력 검증·학습 및 예측 경로·결과 표시를 선택하는 데 쓴다 |
| 구형 데이터 | 기존 Sim Builder·Runner·Optimizer 설정, 구형 XML, 학습 결과는 새로 만든다. 추정·변환·복원하지 않는다 |
| MCU | 기존 설정·상태·XML·산출물과 실행 경로를 유지한다. 재생성 정책의 적용 대상에서 제외한다 |
| Optimizer | 유효한 v2 중에서도 `variant == Sim`이고 `modelFamily == 1D`인 Builder만 허용한다 |
| 알고리즘 | 1D·ND 학습·예측 알고리즘과 전용 로더는 유지한다. 관리 형식, 호출 연결, 경로와 입력 순서를 정리한다 |

설정·상태만 통일하고 오차·파일 배치를 남기는 중간 형식은 두지 않는다. ND 저장·로딩 전환은 추가되지만, Sim의 두 관리 형식과 구형 복원 경로를 함께 유지하는 작업은 없어진다. 최초 구현 공수의 순감소를 전제로 일정이나 PR 수를 정하지 않는다.

## 2. 공통 규격

### 데이터셋

- 일반 Launcher Set의 Preprocess 한 번은 `{LauncherSet}.xml` 하나를 쓴다. 샘플마다 응답 텐서 N개를 담고 하나라도 없으면 해당 샘플을 제외한다.
- 텐서 키는 `sanitizeString(name)`. 정규화 후 중복, 입력·예약 키 충돌, 다른 component 혼합은 파일을 쓰기 전에 거부한다. 같은 이름의 다른 시점도 중복으로 거부하며 자동 ID는 만들지 않는다.
- `model_info.selected_responses[]`의 항목은 `{key, component, load_step, substep, name, file_name}`이다. `key`는 실제 텐서 키다. step·substep을 분리해 보존하고 시점별 요청은 해당 카탈로그를 조회한다.
- Launcher 응답 표는 Config를 통해 저장·복원한다. Sim의 XML 작성·GUI 파서·DeepOpt 판독은 배열 형식으로 함께 전환한다. DeepOpt는 1D·ND 모두 중복 dict 키를 거부한다.
- Sim 파서는 `selected_responses`만 받아 필수 메타와 텐서 키의 대응을 검증한다. 단수 `selected_response`는 재생성 대상으로 거부하며 내부에서 배열로 변환하지 않는다. XML 내용으로 모델 계열을 추정하지 않는다.
- 같은 XML을 1D·ND Builder Set이 각각 사용할 수 있다. 각 모델 행은 응답 키 하나를 선택하며, ND에서는 그 키의 필드 텐서 전체를 전달한다.
- KPI·BORE/BOSS의 별도 XML은 통합하지 않는다. Sim이 소비하는 응답 메타는 같은 배열 규격을 따른다. MCU의 기존 XML 판독은 MCU 전용 경로에 남긴다.

### 계열과 MCU 처리 경계

- 새 Sim Set은 첫 설정에서 `modelFamily: 1D` 또는 `ND`를 선택해 기록한다. Configuration 행이나 산출물이 생긴 뒤에는 바꾸지 않으며 모두 삭제해도 잠금을 풀지 않는다. 다른 계열은 새 Set으로 만든다.
- 신규 생성 흐름과 기존 파일 열기를 구분한다. 기존 Sim Set에 형식 버전이나 계열이 없으면 재생성을 안내한다. Configuration 타입·산출물 폴더·`(Field)` 표시로 추정하거나 빈 기존 설정을 신규 Set으로 간주하지 않는다.
- Sim 1D·ND의 설정 직렬화·복원, manifest 작성·폴링, 오차 판독, 모델 목록·삭제, 모델 행의 ID 관리는 공통이다. `modelFamily`로 이 관리 형식을 나누지 않는다.
- 계열별 처리는 모델 타입 목록, 옵션 내용, 응답 검증·reduction, 학습·예측 CLI, 로더와 결과 표시에 둔다. Set의 계열과 모든 행의 타입을 로드·실행 시 검증하고 혼합을 거부한다.
- 1D는 reduction 뒤 샘플당 응답 스칼라 하나여야 한다. ND는 reduction `None`이며 모델이 받는 필드 형상을 유지한다. 응답 개수로 계열을 결정하지 않는다.
- 기존 클래스와 variant 구분을 유지한다. 공통 base를 사용하는 MCU의 설정·XML·상태·오차·삭제·위젯 경로를 기존 전용 함수 또는 override로 분리한 뒤 Sim 공통 본문을 전환한다. 타이머·base 포인터 호출·명시 base 호출도 이 경계를 따라야 한다.
- MCU 전용 기존 함수는 Sim 구형 파일을 받아 주는 호환 계층이 아니다. Sim 판독 실패 시 MCU 처리로 넘어가지 않는다.

### 모델 식별과 설정

참조는 `{set: Builder setId, model_id}`다. 이름·타입·경로를 식별자로 쓰지 않는다. `model_id`는 Set의 `modelSeq`를 증가시켜 발급하는 `model{N}`이며 삭제 뒤 재사용하지 않는다.

```jsonc
// Sim Builder Set 예시. ND도 같은 구조이며 별도 Set에 계열과 ND 타입을 기록한다.
{
  "schema_version": 2,
  "setId": "<Builder setId>", "variant": "Sim", "modelFamily": "1D", "modelSeq": 2,
  "Data Label": {
    "Dataset": "<abs xml>",
    "Input": {"dv1": {"reduction": "None"}},
    "Output": {"stress": {"reduction": "Max", "transformation": "None"}}
  },
  "Configuration": [
    {"id": "model1", "response": "stress", "type": "Smart", "options": {}, "run": true},
    {"id": "model2", "response": "stress", "type": "RF", "options": {}, "run": false}
  ]
}
```

- Sim 1D·ND 모두 같은 타입의 여러 행을 허용한다. 옵션 페이지는 `m_configWidgets[id]`처럼 행별로 소유한다. 타입 변경 시 그 행의 옵션만 기본값으로 교체하며 ID는 유지한다.
- 한 행은 응답 키 하나와 모델 하나를 표현한다. ND의 여러 필드 응답도 각각 행을 만든다. `row.response`는 Output의 실제 키이며 `(Field)` 같은 표시 접미사를 저장하지 않는다.
- Set JSON에는 학습 상태·오차를 쓰지 않는다. `type`은 선택한 알고리즘, `trained_type`은 실제 저장 모델의 타입이다. Smart는 우승 타입을 기록하고 ND는 실제 ND 타입을 기록한다.
- 행의 설정을 편집해도 기존 학습 결과는 다음 재학습까지 마지막 학습 당시 메타로 표시한다. 설정 값으로 완료 모델의 응답·타입·입력 순서를 덮어쓰지 않는다.

### 산출물과 manifest

최종 모델 파일은 두 계열 모두 `{Builder}/{model_id}/model.pt`다. manifest의 `path`는 `model_info.json` 기준 상대 파일 경로, 엔진 입력의 `path`는 실행 직전에 해석한 절대 파일 경로다.

```jsonc
// 두 계열의 공통 manifest 구조. 예시는 ND 모델 한 개다.
{
  "schema_version": 2, "parameter": {}, "originRecord": {}, "selected_responses": [],
  "models": {
    "model1": {
      "response": "stress", "type": "StableNet", "trained_type": "StableNet",
      "input_order": ["dv1", "dv2"], "reduction": "None", "transformation": "None",
      "path": "model1/model.pt", "status": "Done", "errors": {}, "message": ""
    }
  }
}
```

| 실제 타입 | 저장·로딩 규칙 |
|---|---|
| `Kriging-KBCC`, `RBF`, `SVR`, `RF` | 기존 pickle 계열 객체와 scaling 정보를 유지한다 |
| `MLP`, `BNN` | 전용 로더와 같은 폴더의 `model_info.txt`·input/output scaler를 유지한다 |
| ND 모델 | `model.pt`는 기존 체크포인트 내용이다. 같은 폴더에 `config.yaml`, 전처리·정규화 메타, 해당 모델의 학습 결과를 둔다. ND 전용 로더를 사용한다 |
| `Smart` | 실제 타입으로 허용하지 않는다. `{id}/candidates/{type}/`에 후보를 학습하고 우승 모델과 부속 파일을 `{id}/`로 옮긴다 |

- 필요한 부속 파일이 완성되고 타입에 맞게 읽을 수 있을 때만 `Done`을 기록한다. ND의 `config.yaml`에 있는 타입·응답·DV 순서는 manifest와 일치해야 한다. 기존 알고리즘의 내부 정규화·역변환 정보는 보존한다.
- Smart의 `Model_Error.csv`, ND의 평가 CSV·`rendered_results/`·로그는 해당 `{id}/` 안에 둔다. ND의 basic·proto 저장 경로 모두 동일하게 적용하고 정리는 해당 모델 디렉터리 안에서만 한다.
- 로더는 지정한 `model.pt`를 읽는다. `{response}/{Type}_{err}` 탐색, 파일명의 오차·타입 추정, 첫 `.ckpt`로의 대체는 제거한다. 확장자가 `.pt`여도 기존 체크포인트 내용을 전용 로더로 읽는다.
- GUI는 ID 형식과 `path == model_id + "/model.pt"`를 검증한다. 디렉터리 삭제도 같은 ID 검증을 쓴다. 범용 경로 resolver는 만들지 않는다.
- `models[id].errors`는 metric 이름과 수치의 맵이다. 1D·ND가 서로 다른 metric을 가져도 같은 판독·행 갱신 경로로 읽고 계열에 맞는 열에 표시한다.

### 상태·쓰기·재학습

- GUI는 실행할 행·응답·옵션을 검증한 뒤 출처 정보와 실행 행의 응답·선택 타입·reduction·transformation을 기록한다. 실행 행만 `In Progress`로 초기화하고 이전 path·trained_type·input_order·errors·message를 지운다. 미실행 항목은 보존한다.
- DeepOpt는 성공 시 실제 `trained_type`·`input_order`·path·errors와 `Done`, 실패 시 `Failed`와 사유를 기록한다. GUI가 예상한 입력 순서로 실제 학습 순서를 대신하지 않는다.
- 두 계열 모두 선택 DV가 모든 샘플에 존재하고 라벨당 유한한 스칼라 하나인지 검증한다. `input_order`는 실제 DV 순서다. ND의 좌표·연결성·필드 텐서는 이 목록에 넣거나 스칼라로 펼치지 않고 ND 전처리 규칙으로 검증한다.
- 1D 응답은 reduction 뒤 스칼라 하나인지 확인한다. ND 응답은 선택한 필드의 존재·형상·유한값과 모델별 입력 적합성을 확인한다. 여러 성분을 임의로 첫 성분 하나로 줄이지 않는다.
- 재학습 직전에 실행할 `{id}/`만 비운다. 정리 실패 시 그 행은 실패이며 이전 파일을 다시 완료 산출물로 간주하지 않는다. `run:false`의 파일·메타는 유지한다.
- `In Progress`·`Failed`에는 실행 필드가 없어도 된다. `Done`에는 path·실제 타입·입력 순서 등 실행 필드를 요구한다. 사용 가능한 모델은 유효한 완료 항목이며 모델과 필수 부속 파일이 존재해야 한다.
- 쓰기 순서는 **GUI 초기화 → 실행 중 DeepOpt만 작성 → 실제 프로세스 종료 관측 → GUI 최종 보정**이다. CLI는 행을 순차 실행한다. GUI는 `QSaveFile`, DeepOpt는 같은 디렉터리의 임시 파일과 `os.replace`로 원자적으로 교체한다.
- 취소 통지와 실제 종료를 구분한다. `ProcessJob`이 실제 `finished`를 전달하도록 하고 manifest 보정·재실행·삭제 허용을 그 신호에 묶는다. 프로세스 시작 실패도 종료 보정 대상이다.
- 일시적인 파일 교체 실패만 횟수를 제한해 재시도하고 최종 실패를 전파한다. 모든 `PermissionError`를 일시적 실패로 간주하지 않는다. 폴링 중 일시적 읽기 실패는 직전 표시를 유지한다.
- 종료 후 판독·보정 저장 실패는 오류를 표시하고 다음 실행을 막는다. 보정이 끝나면 남은 `In Progress`를 `Failed`로 바꾸고 재실행을 허용한다. 시작부터 보정 완료까지 UI·삭제 함수 모두 모델 삭제를 거부한다.
- 삭제 대상은 모델 행·manifest 항목·해당 디렉터리다. 부분 삭제 실패 시 그 모델은 사용 가능 상태로 남기지 않고 `Failed`와 사유를 기록한다. modelSeq는 되돌리지 않는다.
- 같은 데이터셋의 Data Label 편집은 다른 모델을 삭제하지 않는다. 미실행 모델은 마지막 학습 메타를 유지한다. 데이터셋 정체성은 `originRecord.dataset`의 producer setId와 파일명이다.
- 다른 데이터셋에서 학습을 시작하면 확인 뒤 기존 모델 결과·디렉터리를 모두 무효화한다. 취소하면 유지한다. 행·ID·modelSeq는 유지한다. 개명 뒤 재생성해 파일명이 달라진 경우도 교체이며, 같은 파일의 내용 변경 감지는 #650 소관이다.
- UI의 transformation 계산 추가는 제외한다. 값 보존·복원과 미적용 표시까지만 다룬다. ND 모델 내부에서 이미 사용하는 정규화·역변환은 그대로 유지한다.

### Runner·Optimizer

| 설정 위치 | 저장 내용 |
|---|---|
| Sim Runner·Optimizer Set | `schema_version: 2`. 구형 설정을 새 형식으로 자동 복원하지 않는다 |
| Runner `modelBuilder` | Builder 하나의 참조 `{set, name}`. 계열은 참조 Builder에서 읽는다 |
| Runner 선택 영속 | #724를 흡수한 별도 키에 `{set, model_id}` 선택을 체크 변경 시 저장 |
| Runner `Model upload.Output Response[]` | `{set, model_id, response, model}` + 실행 직전 갱신한 `path, trained_type, input_order` |
| Optimizer `modelBuilder` | DV·Preview 출처인 기본 Sim 1D Builder `{set, name}` |
| Optimizer `Optimization.trained_surrogate_model[]` | Runner와 같은 모델 항목 + `symbol`. 여러 Sim 1D Builder를 참조할 수 있다 |

- `DashModelBuilderReference::load()`가 variant·modelFamily·manifest·모델 목록을 한 번 해석한다. Runner는 Sim 1D·ND 모두 사용 가능한 모델당 한 행으로 표시하고 ID로 선택을 복원한다. MCU Runner는 기존 모듈을 유지한다.
- 한 Runner 실행은 참조 Builder의 계열 하나다. 전체 선택의 경로·실제 타입·입력 순서·응답·실행 지원 여부를 먼저 확인하고, 모두 유효할 때 설정을 한 번 저장해 해당 계열 CLI를 한 번 실행한다. ND·1D 분할과 설정 이중 쓰기는 없앤다.
- 모델별 DV는 label/value를 실제 `input_order`에 맞춰 배치한다. 누락·중복·비유한 값·길이 불일치를 거부하고 알파벳순 정렬로 대체하지 않는다. reduction 이름은 대소문자를 무시하되 모르는 값은 거부한다.
- 1D CSV는 `{RunnerSet}_test_results.csv`, active case당 한 행, 모델당 `{response} [{model_id}]` 열 하나다. 같은 표시명의 case도 합치지 않는다.
- ND 결과는 실행 설정의 case 순번을 사용한 `case{N}/{model_id}/prediction.vtu`에 쓴다. 순번은 해당 실행 설정에서 고정하고 표시명·입력 파일명으로 합치지 않는다. 각 모델은 원본 형상을 입력으로 받고 결과를 별도 파일로 쓴다. GUI는 요청한 case·모델과 연결된 결과 경로를 표시한다.
- 실행 전 이번 실행의 결과 경로에 남은 파일을 정리하고 실패하면 시작하지 않는다. GUI는 명시 결과 경로만 열고, 내부 루프 실패를 CLI 최종 실패 코드에 반영한다. 실패 실행의 일부 결과를 전체 정상 완료로 표시하지 않는다.
- ND 직접 VTU 예측의 현재 지원 타입을 명시적으로 관리한다. 미지원 모델을 정상 실행처럼 건너뛰지 않고 사전 거부한다. 기존 ND 학습 지원과 직접 VTU 예측 지원을 같은 목록으로 간주하지 않는다.
- Optimizer는 UI 나열과 실행 직전 모두 **Sim + 1D + 유효한 v2**를 확인한다. ND도 v2이므로 버전만으로 허용하면 안 된다. DeepOpt 최적화 로더도 ND 타입을 거부한다.
- 최적화에 참조한 모델의 DV 라벨 집합은 같아야 한다. DV 메타는 기본 Builder의 `parameter`를 사용하며 필요한 라벨이 없으면 거부한다. Geometry Set id가 다르면 Preview·Morphing을 비활성화한다.
- 심볼은 `max+1`로 발급하고 저장값을 유지한다. 목적·제약식에서 사용 중인 심볼 행은 삭제를 막는다. 일반 응답·`std_pred`·deterministic/probabilistic 평가가 같은 입력 어댑터를 사용하며 `symbolic_module.ExpressionEvaluator`도 전환한다.
- 최적화 호출은 `run-optimization <OptSet.json> --output-dir <dir>`다. Builder 디렉터리 인자를 제거하고 항목별 명시 모델 경로를 사용한다.

### 구형 데이터와 재생성

- Sim 1D·ND 모두 기존 Builder·Runner·Optimizer 설정, 단수 응답 XML, 기존 학습 결과를 자동 변환·추정·복원하지 않는다. 새 Builder·Runner·Optimizer Set을 구성하고 XML 재생성·재학습·모델 재선택을 요구한다.
- 기존 Builder Set은 `schema_version == 2`, 명시된 `modelFamily`, 배열 Configuration을 확인한다. manifest가 있으면 `schema_version == 2`와 상태별 필수 구조를 확인한다. 새 Set의 미학습 상태에서는 manifest가 없어도 되며, 소비 측에는 사용 가능한 모델이 없는 것으로 표시한다. Sim XML은 배열 `selected_responses`를 요구한다. 구형 또는 잘못된 구조의 파일은 사유를 표시하고 사용을 거부한다.
- 이미 새 버전으로 저장된 모델 참조의 필수 파일 누락·깨진 참조도 오류로 처리한다. 타입·폴더명으로 보완하거나 다른 모델로 대체하지 않는다. 구형 선택을 빈 선택으로 바꿔 조용히 저장하는 경로는 두지 않는다.
- 열기만으로 기존 파일을 덮어쓰거나 삭제하지 않는다. 재생성은 새 Set 생성·Preprocess·학습 등 사용자가 실행한 동작으로 한다. 프로젝트 전체, Geometry·DOE 등 변경하지 않는 모듈의 재생성을 요구하지 않는다.
- MCU의 기존 설정·XML·학습 결과는 계속 유효하다. MCU 전용 처리 보존과 회귀 검증은 이번 범위에 포함하며 MCU 형식 전환은 제외한다.

## 3. 이슈 계층

```text
[Epic] 다중 응답·다중 모델 파이프라인 — Sim 1D·ND 관리 형식 통일과 구형 데이터 재생성
├─ 독립 결함 수정
│  ├─ DeepOpt: 실행 실패 코드와 명시 결과 경로
│  └─ GUI: 이번 실행의 결과 파일 표시
├─ 공통 참조·처리 경계
│  ├─ GUI: Sim 계열 명시와 MCU 기존 처리 분리
│  ├─ GUI: 모델 참조·산출물 판독·ID 발급
│  └─ DeepOpt: manifest·로더·입력 검증 공통 기반
├─ Preprocessor
│  ├─ GUI: Launcher 응답 표 저장·복원
│  ├─ GUI: Sim XML 작성·파서의 배열 형식 전환
│  └─ GUI: XML 하나에 응답 N개 쓰기
├─ Builder
│  ├─ GUI: Sim 1D·ND 행별 설정·옵션
│  ├─ GUI: 공통 학습 시작·데이터셋 교체
│  ├─ GUI: 공통 상태·오차·삭제
│  ├─ DeepOpt: 1D 트레이너 산출물 배치
│  ├─ DeepOpt: 행별 1D 학습
│  └─ DeepOpt: 행별 ND 학습·산출물 배치
├─ Runner
│  ├─ GUI: Sim 모델별 선택·계열별 실행 모드
│  ├─ GUI: 전체 참조 해석·일괄 실행
│  ├─ DeepOpt: 1D 모델별 예측·case별 CSV
│  └─ DeepOpt: ND 모델별 예측·case별 VTU
└─ Optimizer
   ├─ GUI: 여러 Sim 1D Builder의 모델·심볼 선택
   ├─ GUI: 최적화 실행 계약과 Sim 1D 재검증
   └─ DeepOpt: 선택한 1D 모델로 목적·제약식 평가
```

### 선행 관계

| 작업 흐름 | 선행 관계 |
|---|---|
| 독립 결함 수정 | DeepOpt 실패 코드·명시 결과 경로 → GUI 명시 결과 표시 |
| GUI 공통 기반 | #722 → 공통 참조·산출물 판독. Sim 전환 전 MCU 기존 처리 경계 분리 |
| Preprocessor | 응답 표 영속은 독립 착수. MCU 파서 경계 분리 → Sim XML 배열 전환 → XML 통합 |
| Builder GUI | 공통 참조 + Sim·MCU 처리 경계 → 행별 설정 → 학습 시작 → 상태·오차·삭제. 학습 시작에는 XML 배열 전환도 필요 |
| Builder DeepOpt | 공통 기반 → 1D 산출물 배치 → 행별 1D 학습. 공통 기반 뒤 ND 학습·저장 전환을 병행. 양쪽 학습은 실패 코드 처리에 의존 |
| Runner | 공통 참조 + Sim 계열 명시 → 모델별 선택·실행 모드 → 전체 참조 해석·일괄 실행. 실행에는 명시 결과 표시도 필요 |
| DeepOpt 예측 | 공통 기반 + 실패 코드·명시 결과 경로 뒤 1D 예측과 ND 예측을 병행 |
| Optimizer | 공통 참조 → 여러 Sim 1D Builder 선택 → 실행 계약. DeepOpt는 공통 기반·실패 코드 처리 뒤 식 평가 전환 |

GUI와 DeepOpt의 이슈는 각 저장소에 발행하고 같은 계약의 양쪽을 연결한다. 공통 manifest fixture로 GUI 선택·상태 처리를 먼저 구현할 수 있다. 학습 시작 뒤 상태 처리를 배치하는 것은 같은 파일의 수정 충돌을 피하기 위한 순서이며, 실제 학습과의 검증은 두 계열의 DeepOpt 전환 뒤에 한다.

v4의 별도 Runner 계열 경계 작업은 공통 모델 선택·실행 모드 작업에 합친다. 기존 ND 설정을 받아 주기 위한 선행 전환은 만들지 않는다. Sim 설정·XML·manifest를 바꾸는 PR은 모두 통합 브랜치에서 함께 검증한다.

### 통합과 검증

- Launcher → Sim 1D 학습·예측, Launcher → Sim ND 학습·예측을 각각 검증한다. 같은 XML, 같은 타입의 모델 두 개, 응답 여러 개, 부분 재학습·실패·삭제를 포함한다.
- ND 학습·저장은 basic·proto 경로를 모두 확인한다. 직접 VTU 예측은 현재 지원 타입의 실제 실행과 미지원 타입의 사전 거부를 검증한다. 여러 case·모델의 결과 경로와 원본 VTU 보존을 확인한다.
- Smart의 실제 타입·부속 파일 재로딩과 입력 순서 반전을 검증하고, 여러 Sim 1D Builder를 쓰는 최적화로 넓힌다. 유효한 v2 ND 모델도 Optimizer에서 거부되는지 확인한다.
- 구형 Sim 파일은 사용 거부·재생성 안내·기존 파일 무변경을 확인한다. 구형 Sim 학습·예측을 성공시키는 호환 검증은 두지 않는다. MCU는 기존 설정·XML로 열기·학습·폴링·삭제·예측 회귀를 확인한다.
- fixture는 두 저장소의 `tests/fixtures/multi_model_v2/`에 같은 파일의 복사본을 둔다. 1D·ND 정상 사례, 잘못된 형식·참조, MCU 경계 사례를 구분한다. 한 저장소의 테스트가 다른 저장소 checkout에 의존하지 않게 한다.

형식 불변인 실패 코드·결과 경로 수정, Launcher 응답 표 영속, MCU 경계 분리와 미사용 공통 헬퍼 추가분은 독립 검증 후 dev에 먼저 통합할 수 있다. 실제 Sim 형식 전환은 다음 절차를 따른다.

1. 두 저장소 각각 dev에서 `feat/multi-model`을 분기한다.
2. 전환 PR은 각 통합 브랜치로 squash merge 한다.
3. 두 계열·MCU·Optimizer 검증 후 통합 브랜치에서 dev로 PR을 만들어 squash merge 하고 브랜치를 삭제한다.
4. 검증한 GUI·DeepOpt 커밋 조합을 태그로 남기고 함께 배포한다.

[저장소 관리 수칙](https://github.com/NumeRealWorks/DashOpti_GUI/wiki/저장소-관리-수칙)에 따라 통합한다. 순차 배포를 위한 Sim v1/v2 이중 저장·장기 호환 계층·기능 플래그 체계는 추가하지 않는다. 배포 안내에 Sim 설정 재구성·XML 재생성·재학습·모델 재선택 순서를 명시한다.

## 4. 이슈 초안

각 초안은 저장소 하나의 구현 PR 범위다. 공통 규격을 적용하며, 아래 변경과 기대는 구현 완료 기준이다.

### DeepOpt: 실행 실패 코드와 명시 결과 경로를 제공한다

현상

- CLI 내부에서 잡은 실패가 최종 종료 코드에 반영되지 않고, GUI가 사용할 결과 경로도 명시적으로 맞춰야 한다.

범위

- 건드림: `main.py`의 1D·ND 학습·예측과 `run_optimization`, 명시 결과 경로 전달.
- 안 건드림: Configuration 형식, 모델 선택, 학습·예측 알고리즘.

현재 구조

- ND도 행 실패를 로그로 남기고 계속 실행한다. `RunTestNDFromVTU`는 출력 경로 인자를 실제 저장에 사용하지 않는다.

변경

- 서브커맨드의 내부 실패를 집계해 비정상 종료 코드로 반환한다. 결과가 없거나 저장에 실패한 실행도 실패 처리한다.
- 1D CSV와 ND VTU의 명시 출력 경로를 호출부에서 전달할 수 있게 한다. 기존 CLI의 경로 기본값은 유지하며 모델 ID별 경로 배치는 후속 예측 작업에서 연결한다.

기대

- 성공 항목이 있어도 하나가 실패하면 최종 종료 코드가 0이 아니다. 지정한 결과 경로에 저장되고 내부 함수의 실패가 호출부에 전달된다.

Related: 선행 없음. 후속: GUI 결과 표시, 두 계열의 학습·예측, 선택 모델 식 평가.

### GUI: 이번 실행의 결과 파일을 명시 경로로 표시한다

현상

- 최신 CSV 탐색은 이전 결과를 열 수 있다. ND도 여러 모델의 결과를 구분해야 하며 Optimizer의 수렴 그림 경로는 실제 출력 위치와 다르다.

범위

- 건드림: `DashModelRunner`의 결과 초기화·성공 및 실패 처리·뷰어 연결, `DashOptimizer::onJobFinished`.
- 안 건드림: 모델 선택 영속 형식, 예측·최적화 알고리즘.

현재 구조

- Runner는 지연 후 CSV를 탐색하며 ND 표시도 단일 예측 결과 중심이다. Optimizer는 `optimization_log/convergence_history.png`를 기대하지만 엔진은 `<output_dir>/convergence_history.png`를 쓴다.

변경

- 실행 전에 이전 결과 파일을 정리하고 실패하면 실행을 막는다. CSV와 case·모델별 VTU를 명시 경로로 연결하고 이번 실행의 완료 여부와 함께 표시한다.
- 지연·최신 파일 탐색을 제거하고 수렴 그림 경로를 실제 위치에 맞춘다. 모델별 결과 선택 연결은 Runner 일괄 실행과 함께 완성한다.

기대

- 반복 실행에서 이전 파일을 이번 결과로 표시하지 않는다. 부분 실패·결과 정리 실패를 정상 완료로 표시하지 않고 ND 결과를 case·모델별로 열 수 있다.

Related: 선행: DeepOpt 실패 코드·명시 결과 경로. 후속: Runner 일괄 실행과 Optimizer 실행 계약. 형식 불변인 수정분은 먼저 통합할 수 있다.

### GUI: Sim 계열을 명시하고 MCU의 기존 처리를 분리한다

현상

- Sim의 형식 교체가 공유 base를 사용하는 MCU의 설정·상태·XML 처리까지 바꿀 수 있다. 계열은 현재 첫 행 타입이나 표시 문자열에 의존한다.

범위

- 건드림: `DashModelBuilder`와 `DashModelBuilderMCU`의 공유 진입점, Sim 위젯의 계열 선택, MCU가 쓰는 base 위젯·XML 파서 경계.
- 안 건드림: MCU 설정·상태·XML·산출물 형식, 새 variant 도입, 구형 Sim 계열 추정.

현재 구조

- MCU는 `loadDataLabelConfig`, XML 파서, 상태·오차 함수를 상속하며 `refreshTrainedModelInfo`를 명시 base 호출한다. Sim은 첫 행으로 CLI를 결정한다.

변경

- 기존 MCU 본문을 전용 함수 또는 override로 분리하고 모든 MCU 진입점이 이를 사용하도록 한다. 이후 Sim 1D·ND는 같은 새 관리 경로를 사용한다.
- 신규 Sim Set의 `modelFamily` 선택·기록·잠금을 구현한다. 신규 생성과 기존 파일 열기를 구분하고 계열 누락·혼합·알 수 없는 타입을 거부한다. `(Field)` 판별과 기존 폴더 스캔에 의한 추정은 두지 않는다.

기대

- MCU의 기존 설정·XML·학습·폴링·삭제가 유지된다. 타이머, base 포인터, 명시 base 호출을 검증한다. Sim의 계열은 재열기해도 유지되고 구형 Sim은 MCU 경로로 우회하지 않는다.

Related: 선행 없음. MCU 분리는 형식 전환 전 수행한다. 후속: Sim XML 전환, 공통 행·학습·상태 처리, Runner 실행 모드.

### GUI: 모델 참조·산출물 판독·ID 발급을 공통화한다

현상

- 응답·타입 중심의 참조로는 같은 타입의 여러 모델을 식별할 수 없다. 1D·ND 모델을 같은 규격으로 읽고 사용 가능 여부를 판단해야 한다.

범위

- 건드림: `DashModelBuilderArtifact`, `DashModelBuilderReference`, `LoadedArtifact`, `DashSurrogateModelCommon`과 fixture 경로 제공.
- 안 건드림: 각 모듈의 선택 UI, MCU의 기존 산출물 판독, 모델 알고리즘.

현재 구조

- #722가 Builder setId를 폴더·model_info로 해석하는 참조 계층을 도입한다. 기존 오차는 최상위 `errors`에 있다.

변경

- ModelRef·ModelEntry, 상태별 필수 필드 검증, `modelSeq` 발급, `modelDir`·`resolveModelFile`을 둔다. `LoadedArtifact`는 variant·modelFamily·모델 목록을 제공한다.
- Sim 1D·ND 모두 v2 판독과 ID 기반 파일 검증을 사용한다. 타입별 필수 부속 파일과 계열 적합성을 검증하고 공통 모델 행·metric 표시 자료를 만든다. 구형 산출물 읽기·타입 추정은 추가하지 않는다.

기대

- 두 계열의 참조 round-trip, 상태별 검증, 잘못된 경로·부속 파일 누락 거부, 삭제 뒤 ID 미재사용을 확인한다. `Failed` 모델은 선택할 수 없다.

Related: 선행 #722. MCU 공통 호출부를 교체할 때는 MCU 처리 경계 분리가 필요하다. 후속: Builder 행, Runner 선택, Optimizer의 Sim 1D 선택.

### DeepOpt: manifest·로더·입력 검증의 공통 기반을 만든다

현상

- 학습·예측·최적화가 모델별 상태·명시 경로·실제 타입·DV 순서를 같은 규칙으로 처리해야 한다.

범위

- 건드림: 신규 `source/artifact.py`, 전용 로더 연결, `preprocessor/xml_parser.py`, `tests/`와 공통 fixture.
- 안 건드림: 각 학습 루프·결과 배치, 새 ND 추론 알고리즘, MCU 엔진 계약.

현재 구조

- ND의 `ResultSaver`와 1D 저장 함수가 각각 메타를 쓰고 소비자는 경로를 탐색한다. 조사 기준 DeepOpt에 `tests/` 디렉터리와 CI가 없다.

변경

- manifest 항목의 원자적 갱신·한정 재시도·모델 디렉터리 정리·명시 타입 로더를 공통화한다. 다른 모델 항목은 보존한다.
- DV label/value 검증·순서 재배열을 공유하되 ND 형상·필드 검증은 ND 전처리에 둔다. 두 계열 XML의 중복 키·응답 배열 구조를 검증한다.
- pytest 설정·conftest·더미 모델·1D 및 ND fixture를 마련한다. ND는 전달한 `model.pt`와 필요한 config를 전용 로더로 읽는다.

기대

- 다른 모델 메타 보존, 파일 교체 최종 실패 전파, 실제 지정 파일 로딩, DV 순서 반전·누락·중복·비유한 값 거부를 확인한다. 필드 텐서를 스칼라 DV 검증에 넣지 않는다.

Related: 선행 없음. 후속: 두 계열의 저장·학습·예측과 Optimizer 식 평가. Sim 구형 파일용 fallback은 만들지 않는다.

### GUI: Launcher 응답 표를 Config로 저장·복원한다

현상

- 응답 표가 Config를 거치지 않고 직접 저장되며 재열기 복원 경로가 없다.

범위

- 건드림: `DashAnalysisLauncherConfig`, `DashAnalysisLauncherPresentationModel::saveOutputResponse`, 위젯 열기 시 표 복원.
- 안 건드림: XML 형식과 Preprocess 샘플 루프.

현재 구조

- `saveOutputResponse`가 `root["Output Response"]`를 직접 read-modify-write 한다.

변경

- Config에 응답 목록 읽기·쓰기를 두고 저장과 위젯 초기화를 연결한다.

기대

- 응답 여러 개의 이름·component·step·substep이 저장·재열기 후 같은 표로 복원된다.

Related: 선행 없음. XML 전환과 독립적으로 통합할 수 있다. Launcher 설정 전체의 재생성을 요구하지 않는다.

### GUI: Sim XML 작성·파서를 응답 배열 형식으로 전환한다

현상

- XML 작성과 Builder 파서가 단수 응답 메타를 전제로 한다. Sim에서는 새 배열만 사용하고 MCU의 기존 판독은 별도로 유지해야 한다.

범위

- 건드림: `DashResultTypes.h`, `DashResultXmlWriter::writeModelInfoToXml`, Launcher·KPI 호출부, Sim XML 파서·학습 메타 복사, `DashXmlTailLocator`.
- 안 건드림: MCU의 XML 계약, 샘플 텐서 통합, KPI·BORE/BOSS 파일 통합.

현재 구조

- `parseModelInfoStream`·`readSelectedResponseFromStream`과 학습 메타 복사가 단수 `selected_response`를 사용하며 MCU도 이 파서를 호출한다.

변경

- Sim 작성·판독을 SelectedResponse 목록과 `selected_responses`로 전환한다. Launcher와 KPI의 메타 작성 호출부를 함께 바꾸고 step·substep·실제 텐서 키를 보존한다.
- Sim의 단수 XML은 재생성 사유와 함께 거부한다. MCU 전용 파서로 fallback하거나 단수 메타를 배열로 감싸지 않는다. 꼬리 파싱과 학습 시작의 복사도 배열만 사용한다.

기대

- 1D·ND가 같은 배열 메타를 읽고 응답 키와 텐서가 대응한다. 구형 Sim XML은 열기·학습에서 거부되며 MCU의 기존 XML 판독은 유지된다.

Related: 선행: MCU XML 처리 경계 분리. 후속: XML 통합과 Sim 공통 학습 시작.

### GUI: Launcher Preprocess가 XML 하나에 응답 N개를 쓴다

현상

- 응답 요청마다 XML을 만들고 같은 샘플 파일을 반복해서 연다.

범위

- 건드림: `DashAnalysisLauncher::processResults`, `DashResultProcessor::processSamples`, `DashResultXmlWriter::appendSample`, `DashResultBatch::outputFileName`, Builder 데이터셋 목록.
- 안 건드림: 다중 component의 topology 분리, KPI·BORE/BOSS 별도 XML 통합.

현재 구조

- 요청별 XML 안에서 샘플을 순회하고 샘플당 응답 성공 판정도 하나다. topology 슬롯은 샘플당 하나다.

변경

- 샘플 파일을 한 번 열고 응답 N개를 같은 샘플 dict에 기록한다. 응답별 성공 여부를 검사하고 하나라도 누락되면 해당 샘플을 제외한다.
- 키·component 충돌을 쓰기 전에 검증하고 요청별 시점의 카탈로그를 사용한다. 출력은 `{LauncherSet}.xml` 하나다.

기대

- 파일 열기 횟수가 샘플 수와 같고 1D·ND가 동일 XML에서 각 행의 응답을 선택한다. 검증 실패 시 기존 XML을 덮어쓰지 않는다.

Related: 선행: Sim XML 배열 전환. DeepOpt 중복 키 검증은 공통 기반 작업에 포함한다.

### GUI: Sim 1D·ND의 설정과 옵션을 모델 ID별 행으로 저장한다

현상

- 타입을 키로 하는 Configuration과 타입별 옵션 페이지는 동일 타입의 서로 다른 모델을 표현하지 못한다.

범위

- 건드림: Sim Configuration 조립·복원, `TrainingRowInput`·`buildTrainingStartPlan`, `DashModelBuilderWidget`의 행·옵션·복원, 설정 버전 검증.
- 안 건드림: MCU 행 모델, 상태 폴링, 모델 학습 알고리즘.

현재 구조

- Configuration은 타입별 dict이고 `m_configWidgets[modelName]`으로 옵션을 관리한다. 1D·ND가 같은 Sim 위젯을 쓴다.

변경

- Sim 두 계열 모두 `{id, response, type, options, run}` 배열로 저장하고 ID별 옵션 페이지를 사용한다. 새 ID 발급·타입 변경·행 복원을 같은 경로로 처리한다.
- `schema_version: 2`와 명시 계열을 저장하고 상태·오차 키는 제거한다. 기존 dict 설정은 재생성을 안내하며 읽어 변환하지 않는다. ND 행에는 실제 필드 키와 `None` reduction을 적용한다.
- transformation 값을 복원하고 미적용 표시를 유지한다. 계열에 맞는 모델 타입만 선택하도록 검증한다.

기대

- 1D와 ND 각각 같은 타입의 두 행을 저장·재열기해 ID·run·서로 다른 옵션이 유지된다. 한 행의 타입 변경이 다른 행에 영향을 주지 않으며 MCU 행 동작은 유지된다.

Related: 선행: GUI 공통 참조·ID 발급, Sim 계열 명시·MCU 처리 경계. 후속: 공통 학습 시작. DeepOpt 두 학습 CLI와 같은 배열 계약을 사용한다.

### GUI: 두 계열의 학습 시작과 데이터셋 교체를 공통 처리한다

현상

- 부분 재학습과 데이터셋 교체를 구분해 모델별 마지막 학습 메타를 관리해야 한다.

범위

- 건드림: Sim 학습 시작의 manifest 초기화·출처 비교·교체 확인, 계열별 사전 검증 연결, `QSaveFile` 저장·재시도.
- 안 건드림: MCU 학습 시작, 같은 XML의 내용 변경 감지, DeepOpt의 재학습 폴더 정리.

현재 구조

- Builder는 XML 메타를 model_info로 복사하고 상태를 Set JSON에 기록한다. 계열별 검증과 공통 초기화가 분리되어 있지 않다.

변경

- 두 계열이 같은 함수로 출처와 실행 행을 기록한다. 실행 모델만 초기화하고 미실행 모델의 마지막 학습 메타를 보존한다.
- 새 설정·XML·응답 키·계열을 검증한 뒤 데이터셋 교체 확인을 수행한다. 1D 스칼라 응답과 ND 필드 적합성 검증을 각 경로에 연결하고 공통 manifest를 원자적으로 저장한다.

기대

- 두 계열의 부분 재학습, 다른 데이터셋 교체, 확인 취소, 구형 파일 거부, 초기화 저장 실패를 검증한다. Data Label 편집만으로 전체 결과를 지우지 않는다.

Related: 선행: Sim XML 배열 전환, 공통 행별 설정. 후속: 공통 상태·오차·삭제. 내용 변경 감지는 #650 소관이다.

### GUI: 두 계열의 상태·오차·삭제를 manifest 기준으로 처리한다

현상

- 상태·오차·산출물은 서로 다른 파일·경로에 있고, 취소 통지가 실제 종료보다 먼저 발생한다.

범위

- 건드림: `checkModelStatusInternal`·`finalizeStaleStatuses`, 학습 결과·오차·목록·`getTestDatasetFiles`·삭제, 모델 행 갱신, `ProcessJob` 실제 종료 신호.
- 안 건드림: MCU의 기존 상태·오차 계약, 모델 학습 알고리즘.

현재 구조

- 상태는 Configuration, 오차는 최상위 `errors`, 결과는 응답·타입·오차 경로에 있다. MCU도 관련 base 함수를 사용한다.

변경

- Sim 두 계열 모두 `models[id]`에서 상태·metric을 읽고 ID로 행을 갱신한다. 산출물과 학습 결과도 해당 모델 디렉터리로 찾고 ND metric·렌더링 결과를 표시한다.
- 실제 종료 뒤 남은 상태를 보정하고 완료 전 재실행·삭제를 차단한다. 읽기·보정 저장 실패와 부분 삭제 실패를 처리한다. 삭제 범위는 선택한 ID로 한정한다.

기대

- 계열별 형식 분기 없이 1D·ND의 행별 상태·오차·삭제가 동작한다. 취소 뒤 실제 종료 전에는 보정하지 않으며 한 모델의 재학습·삭제가 다른 모델에 영향을 주지 않는다. MCU는 기존 경로로 동작한다.

Related: 선행: 공통 학습 시작, MCU 처리 경계. fixture로 먼저 구현할 수 있고 실제 학습 검증에는 DeepOpt 1D·ND 전환이 필요하다.

### DeepOpt: 1D 트레이너 산출물을 모델 ID 디렉터리에 배치한다

현상

- 응답·타입·오차 경로는 같은 타입의 여러 모델과 모델별 재학습을 구분하기 어렵다.

범위

- 건드림: `models/oned/*trainer.py`, `smart_trainer.py`, `run_train_1d._save_model_info_json`의 저장 경로·후보 정리·오차 기록.
- 안 건드림: Configuration 행 순회, ND 트레이너 저장, 학습 알고리즘.

현재 구조

- 기존 파일은 `{out}/{response}/{Type}_{err}` 아래에 있고 Smart는 후보를 정리해 우승 모델을 남긴다.

변경

- 공통 산출물 함수를 사용해 `{id}/model.pt`와 타입별 부속 파일을 저장한다. 최상위 `errors` 쓰기를 모델 항목 갱신으로 교체한다.
- Smart 후보는 해당 ID 내부에서만 관리하고 우승 모델·부속 파일·`Model_Error.csv`를 보존한다.

기대

- 같은 타입의 모델 두 개가 공존하고 재학습 대상만 정리된다. Smart의 RF·MLP·BNN 우승 사례를 재로딩해 확인한다.

Related: 선행: DeepOpt 공통 기반. 후속: 행별 1D 학습. ND 저장 전환은 별도 ND 학습·산출물 작업에서 같은 계약을 따른다.

### DeepOpt: Configuration의 실행 행마다 1D 모델 하나를 학습한다

현상

- 기존 1D 학습은 타입별 dict를 순회하고 행의 선택 응답 하나로 학습을 제한하지 않는다.

범위

- 건드림: `main.py::train_model_1d`, `run_train_1d`, `XMLTrainingDataBuilder.build_1d`의 행 순회·검증·상태 기록.
- 안 건드림: ND 학습 구현, UI transformation 계산, 학습 알고리즘.

현재 구조

- `_update_json_status`로 Set JSON을 갱신한다. reduction의 `SUM` 비교와 GUI의 `Sum` 표기도 다르다.

변경

- 유효한 Sim 1D 설정의 `run:true` 행마다 `row.response` 하나를 학습한다. 입력 스칼라·유한값·열 수와 응답 스칼라를 검증하고 실제 입력 순서를 반환한다.
- reduction을 정규화하고 모델별 디렉터리 정리·manifest 상태·실패 집계를 연결한다. Set JSON은 읽기만 한다.

기대

- 같은 타입 두 행의 별도 결과, `run:false` 보존, Sum 계산, 실제 DV 순서, 다성분 응답 거부를 확인한다. 한 행이 실패해도 성공 행의 결과는 보존하고 최종 종료는 실패로 반환한다.

Related: 선행: DeepOpt 실패 코드 처리, 1D 트레이너 산출물 배치. GUI 공통 학습 시작·상태 처리와 통합 검증한다.

### DeepOpt: ND를 행별 학습과 공통 산출물 형식으로 전환한다

현상

- ND는 Configuration dict·Set 상태·최상위 errors·응답 및 오차 경로를 모두 사용한다. 설정·상태만 바꾸면 저장·로딩 경로가 계속 이원화된다.

범위

- 건드림: `main.py::train_model_nd`, `run_train_nd_basic.py`, `run_train_nd_proto.py`, `trainer_utils/result_saver.py`의 대상 응답·저장·오차·정리·입력 순서 반환.
- 안 건드림: 모델 네트워크·손실·학습 알고리즘, 기존 정규화·역변환 계산, 새 ND 타입 추가.

현재 구조

- CLI는 타입별 Configuration을 순회하고 전체 Output을 넘긴다. basic·proto 모두 ResultSaver를 사용하며 응답별 폴더·최상위 오차를 작성한다.

변경

- 유효한 Sim ND 설정의 실행 행마다 `row.response` 하나만 전달한다. basic은 해당 필드 하나를 대상으로, proto도 단일 target 목록으로 실행한다. ND 필드의 성분 구조와 전처리는 보존한다.
- 각 행의 `{id}/`를 작업·출력 범위로 사용하고 `model.pt`, `config.yaml`, 정규화·전처리 메타, 평가 CSV·렌더링·로그를 함께 둔다. 모델 루트와 공통 manifest 경로를 구분해 ID 내부에 별도 manifest를 만들지 않는다.
- 실제 DV 순서를 결과로 반환하고 config와 manifest에 일치시킨다. 모델·필수 부속 파일이 준비된 뒤 공통 writer로 오차와 완료 상태를 기록한다. 실패 시 해당 ID만 실패 처리한다.
- basic·proto의 파일 정리와 CSV 경로를 함께 바꾼다. Sim에서 Set JSON 상태 갱신을 없애고 `_update_json_status`는 남은 호출 여부를 확인한 뒤 정리한다.

기대

- basic·proto 각각 새 형식으로 학습·재로딩된다. 같은 타입 두 행과 서로 다른 응답, 부분 재학습·실패, ID별 로그·CSV·부속 파일 보존을 확인한다. ND 필드에 1D 스칼라 응답 제약을 적용하지 않는다.

Related: 선행: DeepOpt 공통 기반·실패 코드 처리. GUI 공통 학습·상태와 함께 검증하고 ND 예측의 학습 산출물을 제공한다.

### GUI: Runner의 모델별 선택과 계열별 실행 모드를 정리한다

현상

- 응답·타입 쌍으로 선택하면 같은 타입의 여러 모델을 구분할 수 없다. 행별 ND·1D 분할과 설정 이중 쓰기도 남아 있다.

범위

- 건드림: `DashModelRunnerConfig`의 선택 영속·버전 검증, `DashModelRunnerWidget::populateSurrogateTable`, PresentationModel의 선택 수집·실행 모드.
- 안 건드림: Runner의 단일 Builder 참조, MCU Runner, 예측 알고리즘.

현재 구조

- 표는 응답별 모델 선택 중심이며 `groupCheckedPairs`로 계열을 나눠 설정을 두 번 쓴다. 선택 영속 분리는 #724의 범위다.

변경

- 1D·ND 모두 사용 가능한 모델당 한 행으로 표시하고 `{set, model_id}`로 체크를 저장·복원한다. 실행용 Output Response와 별도 영속 키를 사용한다.
- 참조 Builder의 `modelFamily`로 실행 모드·metric·결과 표시를 고르고 행별 분할을 제거한다. 새 설정만 열며 구형 설정의 선택 추정·빈 선택 변환은 하지 않는다.
- ND 직접 예측 미지원 모델은 이유를 표시하고 실행 선택을 막는다. 표시되는 학습 모델 목록과 실행 지원 여부를 구분한다.

기대

- 1D·ND 각각 같은 응답·타입의 서로 다른 ID가 독립 선택·복원된다. 체크만 바꿔도 저장되며 한 실행은 한 계열이다. #724의 선택 영속 분리와 이중 쓰기 제거가 모두 충족된다.

Related: 선행: GUI 공통 참조, Sim 계열 명시. 후속: 전체 참조 해석·일괄 실행. ND 지원 여부는 DeepOpt 예측 계약과 맞춘다.

### GUI: Runner가 전체 참조를 해석해 한 번에 실행한다

현상

- 저장된 표시 정보만으로는 실제 모델 파일·입력 순서·실행 지원 여부를 보장할 수 없다.

범위

- 건드림: `DashModelRunner::run1DPrediction`·`runNDPrediction`, 엔진 입력 조립·저장, case·모델별 결과 경로 연결.
- 안 건드림: 예측 알고리즘, 다중 Builder 선택, 새 영속 case ID 체계.

현재 구조

- 1D·ND의 호출과 결과 처리 경로가 나뉘며 기존 모델 참조는 응답·타입·폴더를 사용한다.

변경

- 모든 선택의 파일·trained_type·input_order·응답과 실행 지원 여부를 먼저 해석한다. 하나라도 실패하면 설정 저장·CLI 실행을 하지 않는다.
- 전체 항목을 한 번 저장하고 Builder 계열에 맞는 CLI를 한 번 실행한다. ND는 현재 실행 설정의 case 순번과 model_id로 결과 경로를 만들고 결과 표시와 연결한다.
- 실행 전 결과 파일 정리와 실패 처리를 공통으로 적용한다. ND의 case별 DV도 모델별 실제 입력 순서에 맞춰 전달한다.

기대

- 두 계열 각각 2 case × 2 model을 한 호출로 실행한다. ND의 같은 표시명·같은 입력 파일 case도 결과가 충돌하지 않는다. 참조 실패·재실행·부분 실패 처리가 두 계열에 동일하게 적용된다.

Related: 선행: Runner 모델별 선택, GUI 명시 결과 표시. DeepOpt 1D·ND 예측과 통합 검증한다.

### DeepOpt: 1D 예측 결과를 case당 CSV 한 행으로 모은다

현상

- 응답 이름만 사용하는 열과 모델×case 단위 행 추가로 동일 응답의 모델 결과가 겹치거나 흩어진다.

범위

- 건드림: `main.py::test_model_1d`, `_write_1d_test_result_to_csv`, `RunTest1D`의 로딩·DV 매핑·결과 집계.
- 안 건드림: 1D 예측 알고리즘, ND 예측, 학습 코드.

현재 구조

- 기존 경로에서 glob으로 모델을 찾고 응답 이름으로 CSV를 기록한다.

변경

- 항목의 명시 path·trained_type으로 모델을 읽고 공통 입력 어댑터를 적용한다. active case당 한 행, `{response} [{model_id}]`별 열로 집계해 지정 CSV에 저장한다.
- 참조·예측·저장 실패를 전파한다. 같은 표시명의 case를 합치지 않는다.

기대

- 두 모델과 두 case에서 정확히 2행·모델 열 2개를 얻는다. 입력 순서 반전·재실행·한 모델 실패를 검증한다.

Related: 선행: DeepOpt 공통 기반·실패 코드·명시 결과 경로. GUI Runner 일괄 실행과 같은 CSV 계약을 사용한다.

### DeepOpt: ND 모델별 예측 결과를 case·모델별 VTU로 저장한다

현상

- 첫 Output Response만 사용하고 모델 경로를 탐색하며 입력 VTU에 결과를 쓴다. DV를 정렬하거나 첫 체크포인트를 고르면 선택 모델의 학습 계약과 달라질 수 있다.

범위

- 건드림: `main.py::test_model_nd`, `source/run_test_nd.py::RunTestNDFromVTU`의 항목 순회·로딩·DV 순서·결과 저장·실패 반환.
- 안 건드림: 새 ND 추론 알고리즘, 현재 미지원 타입의 직접 VTU 예측 구현, 모델 네트워크.

현재 구조

- `Output Response[0]`과 `{model}_*` 탐색을 사용한다. `RunTestNDFromVTU`는 `.pt` 대신 첫 `.ckpt`를 고르고 DV를 알파벳순 정렬하며 `output_vtu_path`를 사용하지 않는다. 일부 타입은 실행 본문이 없다.

변경

- 전체 선택과 active case를 순회한다. `model.pt`를 직접 사용하고 config의 타입·응답·DV 순서를 manifest에서 전달된 값과 검증한다. 다른 체크포인트나 경로로 대체하지 않는다.
- 학습 때의 DV 순서로 입력을 구성하고 기존 정규화·역변환을 적용한다. 결과는 명시한 `case{N}/{model_id}/prediction.vtu`에 쓰며 원본 VTU를 수정하지 않는다.
- 실제 지원 타입만 실행한다. 미지원·로딩·예측·저장 실패를 명확히 반환하고 출력이 없는 경로를 성공으로 반환하지 않는다.

기대

- 지원 타입의 2 case × 2 model 결과 네 개가 독립적으로 남는다. 같은 표시명의 case와 다른 DV 순서, 원본 파일 보존, 정확한 모델 파일 사용을 확인한다. 미지원 타입은 GUI·CLI에서 거부된다.

Related: 선행: DeepOpt 공통 기반·실패 코드·명시 결과 경로. fixture로 먼저 구현하고 실제 저장 파일 검증은 ND 학습 전환 뒤 수행한다.

### GUI: 여러 Sim 1D Builder의 모델과 심볼을 저장·복원한다

현상

- 기존 Optimizer는 단일 Builder의 응답·모델을 중심으로 복원하고 심볼을 다시 부여한다. ND도 새 형식을 사용하므로 형식 버전만으로 최적화 대상을 고를 수 없다.

범위

- 건드림: `DashOptimizer`의 SurrogateModelInfo·save/load·DV 복원, 모델 선택 표, 기본 Builder 선택·Preview·`performMorphing`.
- 안 건드림: 식 편집기, ND 최적화, 프로세스 호출, 구형 설정 복원.

현재 구조

- `modelBuilder {set, name}`은 DV·Preview의 단일 출처다. 기존 선택 항목은 응답·타입·심볼 중심이고 Builder 선택에 이름 일치 추정이 있다.

변경

- 행마다 Builder → 사용 가능한 모델을 선택하고 `{set, model_id, response, model, symbol}`로 저장한다. Builder 목록은 명시적으로 Sim 1D의 유효한 v2만 허용한다. `(Field)` 판별과 이름 일치 추정을 제거한다.
- 새 Optimizer 설정의 버전을 기록하고 심볼은 `max+1`로 발급·보존한다. 사용 중 심볼의 행 삭제를 막는다. 기본 Builder로 DV·Preview를 복원하고 입력 라벨 집합·Geometry 출처를 검증한다.

기대

- 두 Builder의 모델 세 개와 심볼이 저장·복원된다. 입력 집합 불일치, 사용 중 심볼 삭제, Geometry 출처 불일치 시 Preview 제한을 확인한다. 유효한 v2 ND Builder와 MCU Builder는 선택할 수 없다.

Related: 선행: GUI 공통 참조. 후속: 최적화 실행 계약. #726의 Optimizer 재적용 작업과 범위를 맞춘다.

### GUI: 최적화 실행 직전에 Sim 1D 참조와 새 CLI 계약을 검증한다

현상

- Builder 디렉터리 하나를 넘기는 호출은 여러 Builder의 선택 모델을 명시하지 못한다. 저장 후 변경되거나 잘못된 설정으로 들어온 ND 참조도 실행 전에 차단해야 한다.

범위

- 건드림: `DashOptimizer::runOptimization`의 참조 해석·계열 검증·엔진 입력 저장·argv.
- 안 건드림: 선택 UI, 최적화 알고리즘, 결과 그림 형식.

현재 구조

- 호출은 `run-optimization <trainedModelPath> <json> --output-dir <dir>`이며 Builder 폴더에서 경로를 만든다.

변경

- 모든 참조의 Sim·1D·v2 조건과 모델 실행 필드를 재확인한다. 성공한 경우에만 path·trained_type·input_order·응답 메타를 한 번 저장한다.
- `run-optimization <OptSet.json> --output-dir <dir>`로 호출하고 Builder 디렉터리 인자를 제거한다.

기대

- 삭제된 참조, ND·MCU 참조, 구형 설정, 실행 필드 누락은 저장·실행 없이 사유를 표시한다. 정상 실행은 선택한 모델을 사용하고 실제 출력 위치의 수렴 그림을 연다.

Related: 선행: 여러 Sim 1D Builder 선택, GUI 명시 결과 표시. DeepOpt 선택 모델 식 평가와 통합 검증한다.

### DeepOpt: 선택한 1D 모델로 목적·제약식을 평가한다

현상

- 최저 오차 파일을 자동으로 고르면 GUI가 선택한 모델과 다른 모델을 사용한다. 일반 응답과 `std_pred`도 같은 DV 순서로 평가해야 한다.

범위

- 건드림: `main.py::run_optimization`, `MainOptimizer`, `problem_setup.py`, `symbolic_module.ExpressionEvaluator`, 공통 로더 연결.
- 안 건드림: 최적화 알고리즘, `optimum.json`, 별도 fitting 경로, ND 최적화.

현재 구조

- `_build_response_paths`가 응답 경로의 모델 파일 중 최저 오차를 고른다. 일반 응답과 `std_pred`를 처리하는 호출부가 나뉘어 있다.

변경

- Builder 디렉터리 인자를 없애고 항목의 명시 path·trained_type·input_order로 로더·입력 어댑터를 구성한다. 최저 오차 파일 탐색과 타입 경로 추정을 제거한다.
- 최적화에서는 1D 타입만 받아 ND를 거부한다. 일반 응답·`std_pred`·deterministic/probabilistic 평가를 같은 어댑터에 연결하고 실패 코드를 전파한다.

기대

- 두 Builder의 모델 세 개로 입력 순서 반전·Smart 실제 타입·목적 및 제약 계산값을 확인한다. ND 모델을 직접 CLI에 전달해도 거부하고 다른 모델로 대체하지 않는다.

Related: 선행: DeepOpt 공통 기반·실패 코드 처리. GUI Optimizer 실행 계약과 함께 검증한다.

## 5. 범위 밖과 확인 사항

### 범위 밖

- MCU의 새 형식 전환과 MCU 기존 데이터 재생성. 기존 코드 경계 분리와 회귀 검증은 포함한다.
- Sim 구형 설정·XML·학습 결과의 자동 변환, 계열·모델 추정, 기존 선택 복원, 양 형식 동시 저장.
- 다른 component의 응답 통합, 벡터 DV 펼침, 한 Builder Set에서 1D·ND 혼합 실행.
- ND의 새 네트워크·학습 알고리즘·새 직접 VTU 예측 지원 타입, ND 최적화. ND 모델 관리 형식과 기존 지원 예측 경로의 전환은 포함한다.
- KPI·BORE/BOSS의 별도 XML 통합. Sim이 소비하는 응답 메타 변경은 포함한다.
- 모델 이력·복구, 같은 XML의 내용 변경 감지 (#650), DOE 리샘플링 참조 (#684), Runner 다중 Builder 선택.
- UI transformation의 실제 계산 추가. 값 보존·미적용 표시와 모델 내부의 기존 정규화 정보 보존은 포함한다.

### 착수 전 확인

- 대상 Deck이 같은 component·충돌 없는 응답 키·스칼라 DV라는 제약을 만족하는지 확인한다. ND의 형상·필드 텐서는 별도 모델 입력이다.
- 기존 Sim 자료의 재구성·XML 재생성·재학습에 필요한 원본 데이터와 설정 정보를 사용자가 확보할 수 있는지 확인한다. 자동 변환 도구나 구형 계열 분류 작업은 만들지 않는다.
- MCU가 공유하는 XML·설정·상태·삭제 진입점과 명시 base 호출을 확인하고 기존 fixture를 확보한다. MCU의 기존 데이터 생산·소비 경로를 Sim 전환과 함께 바꾸지 않는다.
- ND의 basic·proto별 필수 저장 파일, 실제 DV 순서의 출처, 직접 VTU 예측 지원 타입을 코드 기준으로 확정한다. 지원 목록을 GUI와 DeepOpt 검증에 일치시킨다.
- 공통 fixture에 1D·ND 새 설정·XML·manifest, ND config·체크포인트 재로딩 사례, 구형 거부 사례, Optimizer의 v2 ND 거부 사례를 준비한다.
- GUI·DeepOpt를 함께 배포하고 Sim 재생성 절차를 안내할 수 있는지 확인한다. v4에서 제외했던 ND 저장·로딩 전환을 일정에 포함한다.
