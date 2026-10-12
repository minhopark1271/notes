# 다중 응답·다중 모델 파이프라인 — 공통 규격 설계와 작업 계획 (v7)

> 관련 Issue: 선행 #722. 접점 #724 · #650 · #684 · #726.
> 상태: **코드 조사 기반 설계안** — 2026-10-12, GUI `a076fde7`, #722 (PR, `685-runner-optimizer-set-id`) 의 참조 구조, DeepOpt `a4222b6` 기준. 구현 착수 시 좌표를 재확인한다.
> 이전 문서: [원안](Multi-Response-Multi-Model-Pipeline-Plan.md), [v2](Multi-Response-Multi-Model-Pipeline-Plan_v2.md), [v3](Multi-Response-Multi-Model-Pipeline-Plan_v3.md), [v4](Multi-Response-Multi-Model-Pipeline-Plan_v4.md), [v5](Multi-Response-Multi-Model-Pipeline-Plan_v5.md), [v6](Multi-Response-Multi-Model-Pipeline-Plan_v6.md).
> 범위: **Sim 1D·ND의 모델 관리 형식 통일. 기존 Sim 설정·XML·학습 결과는 재생성을 요구한다.** MCU는 기존 계약을 유지하고, Optimizer는 Sim 1D만 지원한다.
> 해상도: 원안과 같은 이슈 초안 양식 (`현상 / 범위 / 현재 구조 / 변경 / 기대 / Related`). 임시 작업 번호 없이 작업명으로 선행 관계를 연결한다.

## 1. v6에서 바뀐 결정

v6는 모델별 상태·오차를 `{Builder}/{id}/model.json`에 두고 형식 통일에 필요 없는 견고성 규칙을 뺐다. v7은 그 형식을 유지하면서 v6 검토에서 드러난 상태 계약의 빈틈을 닫고, 소비 측 설정의 복제 필드와 양쪽 DV 재배열을 없애며, 작업을 기능 완료 단위로 다시 자른다. 상태 파일의 작성자 셋 (GUI 초기화 → DeepOpt 기록 → GUI 보정) 은 취소 사유를 재열기 뒤까지 남기기 위해 유지한다.

| 항목 | v6 | v7 |
|---|---|---|
| 종료 보정 대상 | 남은 `In Progress` 상태 파일 | 이번 실행 행 중 `Done`·`Failed`가 아닌 행. 파일이 없는 행도 `Failed`로 쓴다 |
| DeepOpt 디렉터리 정리 | 재학습 직전 해당 행. 시점 미정 | CLI 시작 시 설정 검증 뒤 실행 행 전부. 상태 파일은 행 종료 시에만 쓴다 |
| 폴링 | `In Progress` 행의 파일 | 이번 실행 행만. 파일 없음은 진행 중 |
| `ProcessJob` 취소 | 즉시 `Cancelled`, 별도 늦은 신호 | `cancel()`은 kill만 하고 실제 종료에서 `finished(Cancelled)`. 독립 선행 PR |
| 소비 측 저장 항목 | 선택 키와 `Output Response[]` 분리, 실행 직전 `path`·`trained_type`·`input_order` 기록 | 항목 하나를 체크 변경 시 저장하고 실행 직전 `path`만 더한다. #724를 흡수 |
| 실제 타입·입력 순서의 출처 | GUI가 상태 파일에서 읽어 설정에 복제 | 엔진이 `path`의 `model.json`에서 읽는다 |
| DV 재배열 | GUI·엔진 양쪽 | 엔진 입력 어댑터 한 곳 |
| ND 예측 대조 | `config.yaml` ↔ Runner 설정 | `config.yaml` ↔ `model.json`. 산출물 내부 일관성만 |
| 행 `response` | 편집 가능, ID 유지 | 행 생성 시 고정. 다른 응답은 새 행 |
| Optimizer 실행 직전 검증 | Sim·1D·v2·실행 필드 | 저장된 `response`와 `model.json`의 일치를 더한다 |
| 심볼 | 행 기준 `max+1` | Optimizer Set의 `symbolSeq`로 발급, 재사용 없음. 미정의 심볼은 DeepOpt에서 최적화 시작 전 거부하며 GUI에는 별도 사전 검증을 추가하지 않는다 |
| 데이터셋 교체 | 확인 뒤 전체 모델 삭제·manifest 재작성 | manifest가 생긴 뒤 잠근다. 다른 데이터셋은 새 Builder |
| DeepOpt 공통 기반 | 상태 쓰기·정리·로더·DV 검증·XML·테스트 기반 | 상태 파일 writer·설정 판독 검증·fixture·pytest 기반. 로더·어댑터·XML 판독은 첫 사용 작업에 둔다 |
| Builder GUI 이슈 | 학습 시작 / 상태·오차·삭제 | 실행 수명 하나 |
| DeepOpt 1D 학습 이슈 | 트레이너 산출물 배치 / 행별 학습 | 하나 |
| 구현 순서 | 공통 기반 뒤 1D·ND 병행 | 1D 학습 → 예측 → 최적화를 먼저 끝내고 ND를 같은 경계에 붙인다. 배포는 함께 |

| 조사 결과 | v7에 반영할 내용 |
|---|---|
| v6의 보정은 "남은 `In Progress` 파일"이 대상인데, DeepOpt의 재학습 정리가 GUI가 쓴 그 파일을 지운다. 삭제 뒤 새 상태를 쓰기 전에 종료되면 행은 미학습으로 남는다 | 보정 대상을 GUI가 아는 이번 실행 행 목록으로 바꾼다. 정리는 CLI 시작 시 한 번이다 |
| `ProcessJob::cancel()`은 QProcess를 떼어내고 즉시 `Cancelled`를 방출한다 (`controller/async/ProcessJob.cpp:97`). 소비자 6곳 (`model/DashModelBuilder.cpp:909`, `model/DashModelBuilderMCU.cpp:367`, `model/DashModelRunner.cpp:80`, `model/DashOptimizer.cpp:276`, `:342`, `controller/DashTopOptPostprocessRunner.cpp:29`) 모두 `finished`에서 `deleteLater` 한다. `DashOptimizer::releaseRunningJob`은 소유자 소멸 전 QProcess 분리를 위해 `cancel()`을 부른다 (`model/DashOptimizer.cpp:86`). 소비자 코드는 `State::Cancelled`로 분기하지 않는다 | 늦은 `finished`는 소비자 계약을 바꾸지 않는다. 소멸 시 분리는 소멸자로 옮기고 새 `State` 값을 두지 않는다. 공용 기반이므로 독립 PR |
| 현재 Builder는 종료 뒤 500ms·1000ms 지연 재확인 뒤 남은 `In Progress`를 `Failed`로 쓴다 (`model/DashModelBuilder.cpp:1545`, `:1723`). 위젯은 중지 클릭 직후 시작 버튼을 켠다 (`view/DashModelBuilderWidgetBase.cpp:70`) | 지연 재확인을 실제 종료 신호로 대체한다. 버튼은 `finished`에서 푼다 |
| v6는 `trained_type`·`input_order`를 Runner·Optimizer 설정에 복제하고 ND 예측에서 `config.yaml`과 Runner 설정을 대조한다. DV 재배열은 GUI (Runner 일괄 실행) 와 DeepOpt (공통 기반) 양쪽에 있다 | 엔진이 `model.json`을 읽고 재배열도 엔진만 한다. 복제 필드와 대조 규칙을 없앤다 |
| #724는 `Output Response[]`가 엔진 입력과 선택 영속을 겸해 생긴 미복원 (Run 없이 체크만 바꾸면 복원 안 됨) 과 ND·1D 이중 쓰기를 다룬다 | 체크 변경 시 저장과 한 차원 한 실행으로 두 증상이 사라진다. 별도 키 없이 같은 항목을 쓴다 |
| v6는 행 편집 시 ID를 유지해 재학습 뒤 같은 ID의 응답이 바뀔 수 있고, Optimizer 식은 그 ID를 계속 참조한다 | `response`를 행 생성 시 고정한다 |
| v6의 `max+1` 심볼은 `r3` 삭제 뒤 새 행에 `r3`을 다시 준다 | `symbolSeq` 영속 발급 |
| v6의 데이터셋 교체는 전체 삭제 실패를 로그로만 남겨 미실행 행의 옛 `Done`이 새 manifest와 어긋난 채 남을 수 있다 | 교체 경로를 없앤다 |

| 결정 항목 | v7 결정 |
|---|---|
| Sim 관리 형식 | v6과 같다. 1D·ND 모두 v2, Configuration 배열, `model_id`, `{id}/model.json`, 고정 모델 경로, 명시 참조 |
| 상태 파일 작성자 | GUI 초기화, DeepOpt 행 종료 기록, GUI 종료 보정. 보정은 실제 종료 뒤 이번 실행 행 목록 기준 |
| 소비 측 참조 | 항목 `{set, model_id}`와 표시용 이름. 실행 직전 `path`만 더한다. 타입·입력 순서·DV 재배열은 엔진 |
| 모델 행 | `response`는 생성 시 고정. 타입·옵션·`run`은 편집 가능. reduction은 전역 `Data Label.Output` 유지 |
| 심볼 | `symbolSeq` 영속, 재사용 없음, DeepOpt에서 미정의 심볼 거부. GUI 사전 검증·사용 중 삭제 차단 없음 |
| 데이터셋 | manifest가 있는 Builder는 `Dataset`을 바꾸지 않는다 |
| 작업 단위 | 기능 완료 단위. `ProcessJob`·MCU 분리는 독립 선행. 1D 수직 완성 뒤 ND |
| 유지 | 모델 차원 불변, MCU 불변, Optimizer Sim 1D 한정, 구형 Sim 재생성, ND 2단계 분할 기각, 타입별 부속 파일 검증 제외 |

채택하지 않은 대안:

- DeepOpt만 `model.json`을 쓰는 단일 작성자. 초기화·보정·보정 실패 시 실행 차단이 없어지지만 정상 취소 뒤 재열기 시 사유가 남지 않는다. 취소 사유 영속을 요구하므로 기각.
- 실행 직전 별도 실행 요청 파일. Set JSON이 실행마다 바뀌지 않는 장점뿐이고 새 포맷과 CLI 인자가 늘어난다. `path` 하나 추가로 충분하다.
- 행이 reduction을 소유하고 응답·reduction 변경 시 새 행 생성. 같은 응답·다른 reduction 모델의 요구가 없고 스키마·위젯·엔진 판독이 바뀐다. `response` 고정으로 ID의 의미를 지킨다.
- 각 행 시작 시 그 행만 정리. 취소 시 미도달 행의 이전 모델이 남지만, 폴링이 옛 `Done`을 이번 결과로 오인하지 않도록 시각 대조가 필요하다.

## 2. 공통 규격

### 데이터셋

- 일반 Launcher Set의 Preprocess 한 번은 `{LauncherSet}.xml` 하나를 쓴다. 샘플마다 응답 텐서 N개를 담고 하나라도 없으면 해당 샘플을 제외한다.
- 텐서 키는 `sanitizeString(name)`. 정규화 후 중복, 입력·예약 키 충돌, 다른 component 혼합은 파일을 쓰기 전에 거부한다. 같은 이름의 다른 시점도 중복으로 거부하며 자동 ID는 만들지 않는다.
- `model_info.selected_responses[]`의 항목은 `{key, component, load_step, substep, name, file_name}`이다. `key`는 실제 텐서 키다. step·substep을 분리해 보존하고 시점별 요청은 해당 카탈로그를 조회한다.
- Launcher 응답 표는 Config를 통해 저장·복원한다. Sim의 XML 작성·GUI 파서·DeepOpt 판독은 배열 형식으로 함께 전환한다. DeepOpt는 1D·ND 모두 중복 dict 키를 거부한다.
- Sim 파서는 `selected_responses`만 받아 필수 메타와 텐서 키의 대응을 검증한다. 단수 `selected_response`는 재생성 대상으로 거부하며 내부에서 배열로 변환하지 않는다. XML 내용으로 모델 차원을 추정하지 않는다.
- 같은 XML을 1D·ND Builder Set이 각각 사용할 수 있다. 각 모델 행은 응답 키 하나를 선택하며, ND에서는 그 키의 필드 텐서 전체를 전달한다.
- Builder의 `Data Label.Dataset`은 manifest가 생기기 전까지만 바꿀 수 있다. manifest가 있으면 위젯은 경로 선택을 잠그고, 다른 데이터셋은 새 Builder Set으로 만든다. 학습 시작 시 manifest의 `originRecord.dataset`과 현재 XML의 출처 (producer setId와 파일명) 가 다르면 거부한다. 같은 파일의 재생성은 교체가 아니며 내용 변경 감지는 #650 소관이다.
- KPI·BORE/BOSS의 별도 XML은 통합하지 않는다. Sim이 소비하는 응답 메타는 같은 배열 규격을 따른다. MCU의 기존 XML 판독은 MCU 전용 경로에 남긴다.

### 모델 차원과 MCU 처리 경계

- 새 Sim Set은 생성 시 `modelDimension: 1D` 또는 `ND`를 선택해 기록하고 이후 바꾸지 않는다. 다른 차원은 새 Set으로 만든다.
- 신규 생성 흐름과 기존 파일 열기를 구분한다. 기존 Sim Set에 형식 버전이나 모델 차원이 없으면 재생성을 안내한다. Configuration 타입·산출물 폴더·`(Field)` 표시로 추정하거나 빈 기존 설정을 신규 Set으로 간주하지 않는다.
- Sim 1D·ND의 설정 직렬화·복원, manifest·상태 파일 작성·폴링, 오차 판독, 모델 목록·삭제, 모델 행의 ID 관리는 공통이다. `modelDimension`으로 이 관리 형식을 나누지 않는다.
- 차원별 처리는 모델 타입 목록, 옵션 내용, 응답 검증·reduction, 학습·예측 CLI, 로더와 결과 표시에 둔다. Set의 차원과 모든 행의 타입을 로드·실행 시 검증하고 혼합을 거부한다.
- 1D는 reduction 뒤 샘플당 응답 스칼라 하나여야 한다. ND는 reduction `None`이며 모델이 받는 필드 형상을 유지한다. 응답 개수로 차원을 결정하지 않는다.
- 기존 클래스와 variant 구분을 유지한다. 공통 base를 사용하는 MCU의 설정·XML·상태·오차·삭제·위젯 경로를 기존 전용 함수 또는 override로 분리한 뒤 Sim 공통 본문을 전환한다. 타이머·base 포인터 호출·명시 base 호출도 이 경계를 따라야 한다.
- MCU 전용 기존 함수는 Sim 구형 파일을 받아 주는 호환 계층이 아니다. Sim 판독 실패 시 MCU 처리로 넘어가지 않는다.

### 모델 식별과 설정

참조는 `{set: Builder setId, model_id}`다. 이름·타입·경로를 식별자로 쓰지 않는다. `model_id`는 Set의 `modelSeq`를 증가시켜 발급하는 `model{N}`이며 삭제 뒤 재사용하지 않는다.

```jsonc
// Sim Builder Set 예시. ND도 같은 구조이며 별도 Set에 모델 차원과 ND 타입을 기록한다.
{
  "schema_version": 2,
  "setId": "<Builder setId>", "variant": "Sim", "modelDimension": "1D", "modelSeq": 2,
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
- `row.response`는 행을 만들 때 정하고 바꾸지 않는다. 위젯은 생성 뒤 응답 선택을 잠근다. 다른 응답의 모델은 새 행이며 새 ID를 받는다. 한 ID는 한 예측 대상을 뜻하고, 소비 측 참조는 그 ID의 최신 완료 산출물을 쓴다.
- reduction·transformation은 전역 `Data Label.Output`에 둔다. 같은 응답의 모든 행이 같은 reduction을 쓴다.
- Set JSON에는 학습 상태·오차를 쓰지 않는다. `type`은 선택한 알고리즘, `trained_type`은 실제 저장 모델의 타입이다. Smart는 우승 타입을 기록하고 ND는 실제 ND 타입을 기록한다.
- 타입·옵션·`run`을 편집해도 기존 학습 결과는 다음 재학습까지 마지막 학습 당시 메타로 표시한다. 설정 값으로 완료 모델의 타입·입력 순서를 덮어쓰지 않는다.

### 산출물·manifest·모델 상태 파일

최종 모델 파일은 두 차원 모두 `{Builder}/{model_id}/model.pt`다. 같은 디렉터리의 `model.json`이 그 모델의 상태·오차·실제 타입·입력 순서를 담는다. manifest `model_info.json`은 데이터셋 메타만 담고 GUI가 학습 시작 때 쓴다. 소비 측 엔진 입력의 `path`는 실행 직전에 해석한 `{Builder}/{model_id}` 절대 디렉터리이며, 엔진은 그 안의 `model.json`·`model.pt`를 읽는다.

```text
ModelBuilder_{Set}/
├─ model_info.json            데이터셋 메타. GUI가 학습 시작 때 쓴다
├─ model1/
│  ├─ model.json              이 모델의 상태. GUI 초기화 → DeepOpt 종료 기록 → GUI 보정
│  ├─ model.pt
│  └─ 타입별 부속 파일, Smart는 candidates/{type}/ 와 Model_Error.csv
└─ model2/ …
```

```jsonc
// {Builder}/model_info.json
{ "schema_version": 2, "parameter": {}, "originRecord": {}, "selected_responses": [] }

// {Builder}/model1/model.json — 예시는 ND 모델 한 개다.
{
  "schema_version": 2,
  "response": "stress", "type": "StableNet", "trained_type": "StableNet",
  "input_order": ["dv1", "dv2"], "reduction": "None", "transformation": "None",
  "status": "Done", "errors": {}, "message": ""
}
```

| 실제 타입 | 저장·로딩 규칙 |
|---|---|
| `Kriging-KBCC`, `RBF`, `SVR`, `RF` | 기존 pickle 계열 객체와 scaling 정보를 유지한다 |
| `MLP`, `BNN` | 전용 로더와 같은 폴더의 `model_info.txt`·input/output scaler를 유지한다 |
| ND 모델 | `model.pt`는 기존 체크포인트 내용이다. 같은 폴더에 `config.yaml`, 전처리·정규화 메타, 해당 모델의 학습 결과를 둔다. ND 전용 로더를 사용한다 |
| `Smart` | 실제 타입으로 허용하지 않는다. `{id}/candidates/{type}/`에 후보를 학습하고 우승 모델과 부속 파일을 `{id}/`로 옮긴다 |

- DeepOpt는 모델 파일과 필요한 부속 파일을 타입에 맞게 다시 읽을 수 있을 때만 `Done`을 기록한다. ND의 `config.yaml`에 있는 타입·응답·DV 순서는 상태 파일과 일치해야 하며, 예측·로딩 시 둘을 대조한다. 기존 알고리즘의 내부 정규화·역변환 정보는 보존한다.
- Smart의 `Model_Error.csv`, ND의 평가 CSV·`rendered_results/`·로그는 해당 `{id}/` 안에 둔다. ND의 basic·proto 저장 경로 모두 동일하게 적용하고 정리는 해당 모델 디렉터리 안에서만 한다.
- 로더는 `path`의 `model.json`에서 `trained_type`·`input_order`를 읽고 지정한 `model.pt`를 읽는다. `{response}/{Type}_{err}` 탐색, 파일명의 오차·타입 추정, 첫 `.ckpt`로의 대체는 제거한다. 확장자가 `.pt`여도 기존 체크포인트 내용을 전용 로더로 읽는다.
- GUI는 ID 형식을 검증하고 모델 디렉터리를 `{Builder}/{id}`, 모델 파일을 `{id}/model.pt`로 고정 해석한다. 상태 파일에 경로 필드를 두지 않는다. 디렉터리 삭제도 같은 ID 검증을 쓴다. 범용 경로 resolver는 만들지 않는다.
- 사용 가능한 모델은 상태 파일이 `Done`이고 `{id}/model.pt`가 있는 모델이다. 타입별 부속 파일 목록은 DeepOpt 로더에만 있고 GUI는 검사하지 않는다. 누락은 실행 시 로딩 오류로 드러난다.
- 모델 목록은 Configuration 행의 ID에서 만들고 행마다 `{id}/model.json`을 읽는다. 행은 있고 상태 파일이 없으면 미학습이다. 행이 없는 디렉터리는 무시한다. 상태 파일 하나가 깨지면 그 모델만 사용 불가다.
- manifest가 없는 Builder는 학습한 적이 없는 Set이며 소비 측 Builder 목록에 나타나지 않는다. #722의 `availableSets()` 기준과 같다.
- `errors`는 metric 이름과 수치의 맵이다. 1D·ND가 서로 다른 metric을 가져도 같은 판독·행 갱신 경로로 읽고 차원에 맞는 열에 표시한다.

### 상태·쓰기·재학습

- GUI 학습 시작: 실행할 행·응답·옵션·차원을 검증하고 manifest 출처와 현재 XML 출처의 일치를 확인한다. manifest에 출처 정보와 데이터셋 메타를 쓰고, 실행 행마다 `{id}/model.json`을 응답·선택 타입·reduction·transformation과 `In Progress`로 통째로 쓴다. 이전 trained_type·input_order·errors·message는 이 쓰기로 사라진다. 실행 행 ID 목록을 이번 실행으로 보관하고 CLI 기동은 마지막 동작이다. 미실행 행의 파일은 건드리지 않는다.
- 초기화 쓰기가 하나라도 실패하면 기동하지 않는다. 이미 `In Progress`를 쓴 행은 아래 종료 보정 규칙으로 `Failed`와 사유를 쓴다.
- DeepOpt는 설정·manifest·데이터셋을 검증한 뒤 실행 행 전부의 `{id}/`를 비우고 순차 학습한다. 정리에 실패한 행은 `Failed`를 쓰고 학습하지 않으며 이전 파일을 완료 산출물로 간주하지 않는다. 행 종료 시 `{id}/model.json`을 통째로 쓴다. 성공 시 실제 `trained_type`·`input_order`·errors와 `Done`, 실패 시 `Failed`와 사유다. 상태 파일은 행 종료 시에만 쓴다. GUI가 예상한 입력 순서로 실제 학습 순서를 대신하지 않는다. 다른 모델의 파일과 manifest는 읽지도 쓰지도 않는다. `run:false`의 파일·메타는 유지한다.
- 두 차원 모두 선택 DV가 모든 샘플에 존재하고 라벨당 유한한 스칼라 하나인지 검증한다. `input_order`는 실제 DV 순서다. ND의 좌표·연결성·필드 텐서는 이 목록에 넣거나 스칼라로 펼치지 않고 ND 전처리 규칙으로 검증한다.
- 1D 응답은 reduction 뒤 스칼라 하나인지 확인한다. ND 응답은 선택한 필드의 존재·형상·유한값과 모델별 입력 적합성을 확인한다. 여러 성분을 임의로 첫 성분 하나로 줄이지 않는다.
- `In Progress`·`Failed`에는 실행 필드가 없어도 된다. `Done`에는 실제 타입·입력 순서 등 실행 필드를 요구한다.
- 쓰기 순서는 **GUI 초기화 → 실행 중 DeepOpt만 작성 → 실제 프로세스 종료 관측 → GUI 보정**이다. 모든 쓰기는 파일 전체를 덮어쓰며 상대가 쓴 내용을 읽어 합치지 않는다. CLI는 행을 순차 실행한다. GUI는 `QSaveFile`, DeepOpt는 같은 디렉터리의 임시 파일과 `os.replace`로 교체한다. 교체 실패는 그 쓰기의 실패로 전파하고 재시도 규칙은 두지 않는다.
- 폴링은 이번 실행 행의 상태 파일만 읽는다. 파일이 없으면 정리 뒤 아직 쓰지 않은 것이므로 진행 중으로 표시한다. 파일이 있으면 그 상태를 표시한다. 일시적 읽기 실패는 직전 표시를 유지한다. 미실행 행은 폴링하지 않는다.
- 종료 보정은 `finished` (정상 종료·실패·취소·기동 실패 모두) 뒤에 이번 실행 행 중 `Done`·`Failed`가 아닌 행, 즉 파일이 없거나 `In Progress`인 행을 `Failed`와 사유 (사용자 취소·종료 코드·기동 실패) 로 통째로 쓴다. DeepOpt가 쓴 `Done`·`Failed`는 건드리지 않는다. 실제 종료 전에는 UI·삭제 함수 모두 재실행·삭제를 거부하고, 보정이 끝나면 허용한다.
- 보정 저장 실패는 오류를 표시하고 그 Set을 다시 열기 전까지 실행·삭제를 막는다. 열기 시 실행 중인 Job 없이 남은 `In Progress`는 미완료로 표시만 하고 쓰지 않는다. 다음 초기화 쓰기가 덮는다.
- 삭제 대상은 모델 행과 `{id}/` 디렉터리다. 행을 지운 뒤 디렉터리를 지우고, 디렉터리 삭제 실패는 로그로 남긴다. 행이 없는 디렉터리는 목록에 나타나지 않는다. modelSeq는 되돌리지 않는다.
- Data Label의 Input·Output 편집은 다른 모델을 삭제하지 않는다. 미실행 모델은 마지막 학습 메타를 유지한다.
- UI의 transformation 계산 추가는 제외한다. 값 보존·복원과 미적용 표시까지만 다룬다. ND 모델 내부에서 이미 사용하는 정규화·역변환은 그대로 유지한다.

### 프로세스 종료

- `ProcessJob::cancel()`은 프로세스 트리를 kill하고 취소 요청을 기록할 뿐 상태를 바꾸지 않는다. `QProcess::finished`에서 취소 요청이 있으면 `Cancelled("사용자 취소")`, 없으면 종료 코드로 `Succeeded`·`Failed`로 전이하고 `finished`를 한 번 방출한다. 새 `State` 값은 두지 않는다.
- `finished`는 프로세스가 끝났다는 뜻이다. 소비자의 `finished → deleteLater`는 그대로다. 기동 실패 (`FailedToStart`, 실행 파일 없음) 는 프로세스가 없으므로 지금처럼 즉시 `Failed`다.
- 소유자가 실행 중 소멸하면 소멸자가 QProcess를 떼어내 자기 종료를 자기가 회수하게 한다. `DashOptimizer::releaseRunningJob`의 분리 목적은 소멸자가 대신한다. 앱 종료 훅 `cancelAllRunning()`은 통지 차단·분리·즉시 종단을 지금처럼 유지한다.
- 소비자는 취소 요청 뒤 중지 버튼을 잠그고 `finished`에서 시작 버튼을 푼다. 상태 파일 보정·재실행·삭제 허용은 이 신호에 묶는다. 동기 대기·재시도·타임아웃은 두지 않는다.
- 한계: 트리 kill이 실패해 부트로더만 죽으면 고아 워커가 늦게 파일을 쓸 수 있다. 현재와 같은 한계다.

### Runner·Optimizer

| 설정 위치 | 저장 내용 |
|---|---|
| Sim Runner·Optimizer Set | `schema_version: 2`. 구형 설정을 새 형식으로 자동 복원하지 않는다 |
| Runner `modelBuilder` | Builder 하나의 참조 `{set, name}`. 모델 차원은 참조 Builder에서 읽는다 |
| Runner `Model upload.Output Response[]` | 선택 항목 `{set, model_id, response, model}`. 체크·콤보 변경 시 저장하고 재열기 복원도 이 항목을 읽는다. 실행 직전 각 항목에 `path`를 더해 한 번 저장한다. `response`·`model`은 표시용이다 |
| Optimizer `modelBuilder` | DV·Preview 출처이자 모델 선택 대상인 Sim 1D Builder `{set, name}` |
| Optimizer `Optimization.trained_surrogate_model[]` | Runner와 같은 항목 + `symbol`. 항목의 `set`은 참조 Builder와 같다. 다른 Builder를 섞는 확장은 별도 이슈다 |
| Optimizer `symbolSeq` | 심볼 발급 카운터. 삭제해도 되돌리지 않는다 |

- `DashModelBuilderReference::load()`가 variant·modelDimension·manifest를 읽고, Configuration 행의 ID마다 `{id}/model.json`을 읽어 모델 목록을 만든다. Runner는 Sim 1D·ND 모두 사용 가능한 모델당 한 행으로 표시하고 ID로 선택을 복원한다. MCU Runner는 기존 모듈을 유지한다.
- `path`는 실행 직전 해석한 `{Builder}/{model_id}` 절대 디렉터리다. 엔진은 그 안의 `model.json`·`model.pt`를 읽어 실제 타입·입력 순서·응답을 정한다. GUI는 `trained_type`·`input_order`를 설정에 쓰지 않는다.
- GUI는 실행 직전 모든 항목에 대해 참조 Builder의 variant·차원·v2, 행 존재, 상태 `Done`, `model.pt` 존재, 실행 지원 여부를 상태 파일에서 확인한다. Optimizer는 저장된 `response`와 `model.json`의 `response` 일치를 더한다. 하나라도 실패하면 저장·실행하지 않고 사유를 표시한다.
- 한 Runner 실행은 참조 Builder의 차원 하나다. 모두 유효할 때 설정을 한 번 저장해 해당 차원 CLI를 한 번 실행한다. ND·1D 분할과 설정 이중 쓰기는 없앤다.
- 선택 항목은 엔진 입력이자 선택 영속이다. 쓰기 시점은 체크 변경과 실행 직전 둘뿐이고 한 실행이 한 차원이므로 연속 쓰기가 없다. #724는 별도 키 없이 이 규칙으로 닫는다.
- 모델별 DV는 엔진의 입력 어댑터 한 곳이 label/value를 `model.json`의 `input_order`에 맞춰 배치한다. 누락·중복·비유한 값·길이 불일치를 거부하고 알파벳순 정렬로 대체하지 않는다. GUI는 case의 label/value를 그대로 전달한다. reduction 이름은 대소문자를 무시하되 모르는 값은 거부한다.
- 1D CSV는 `{RunnerSet}_test_results.csv`, active case당 한 행, 모델당 `{response} [{model_id}]` 열 하나다. 같은 표시명의 case도 합치지 않는다.
- ND 결과는 실행 설정의 case 순번을 사용한 `case{N}/{model_id}/prediction.vtu`에 쓴다. 순번은 해당 실행 설정에서 고정하고 표시명·입력 파일명으로 합치지 않는다. 각 모델은 원본 형상을 입력으로 받고 결과를 별도 파일로 쓴다. GUI는 요청한 case·모델과 연결된 결과 경로를 표시한다.
- 실행 전 이번 실행의 결과 경로에 남은 파일을 정리하고 실패하면 시작하지 않는다. GUI는 명시 결과 경로만 열고, 내부 루프 실패를 CLI 최종 실패 코드에 반영한다. 실패 실행의 일부 결과를 전체 정상 완료로 표시하지 않는다.
- ND 직접 VTU 예측의 현재 지원 타입을 명시적으로 관리한다. 미지원 모델을 정상 실행처럼 건너뛰지 않고 사전 거부한다. 기존 ND 학습 지원과 직접 VTU 예측 지원을 같은 목록으로 간주하지 않는다.
- Optimizer는 UI 나열과 실행 직전 모두 **Sim + 1D + 유효한 v2**를 확인한다. ND도 v2이므로 버전만으로 허용하면 안 된다. DeepOpt 최적화 로더도 ND 타입을 거부한다.
- DV 메타는 참조 Builder의 `parameter`를 사용하며 필요한 라벨이 없으면 거부한다. Geometry 출처도 참조 Builder를 따른다.
- 심볼은 `symbolSeq`로 `r{N}`을 발급하고 저장값을 유지한다. 삭제한 심볼은 재사용하지 않는다. DeepOpt는 최적화 시작 전 식의 미정의 심볼을 거부하고 실패를 GUI에 전달한다. GUI에는 별도의 식 심볼 사전 검증을 추가하지 않는다. 사용 중 심볼의 삭제 차단은 두지 않는다. 일반 응답·`std_pred`·deterministic/probabilistic 평가가 같은 입력 어댑터를 사용하며 `symbolic_module.ExpressionEvaluator`도 전환한다.
- 최적화 호출은 `run-optimization <OptSet.json> --output-dir <dir>`다. Builder 디렉터리 인자를 제거하고 항목별 `path`를 사용한다.
- 다중 Builder 참조는 별도 이슈다. 그때 행마다 Builder를 고르고, 기본 Builder가 DV·Preview 출처가 되며, 참조한 모든 Builder의 DV 라벨 집합 일치와 Geometry Set id 불일치 시 Preview·Morphing 비활성 규칙을 더한다. 모델 항목 형식은 바뀌지 않는다.

### 구형 데이터와 재생성

- Sim 1D·ND 모두 기존 Builder·Runner·Optimizer 설정, 단수 응답 XML, 기존 학습 결과를 자동 변환·추정·복원하지 않는다. 새 Builder·Runner·Optimizer Set을 구성하고 XML 재생성·재학습·모델 재선택을 요구한다.
- 기존 Builder Set은 `schema_version == 2`, 명시된 `modelDimension`, 배열 Configuration을 확인한다. manifest가 있으면 `schema_version == 2`를 확인하고, 상태 파일은 상태별 필수 구조를 확인한다. 새 Set의 미학습 상태에서는 manifest·상태 파일이 없어도 되며 소비 측 Builder 목록에 나타나지 않는다. Sim XML은 배열 `selected_responses`를 요구한다. 구형 또는 잘못된 구조의 파일은 사유를 표시하고 사용을 거부한다.
- 이미 새 버전으로 저장된 모델 참조의 모델 파일 누락·깨진 참조도 오류로 처리한다. 타입·폴더명으로 보완하거나 다른 모델로 대체하지 않는다. 구형 선택을 빈 선택으로 바꿔 조용히 저장하는 경로는 두지 않는다.
- 열기만으로 기존 파일을 덮어쓰거나 삭제하지 않는다. 재생성은 새 Set 생성·Preprocess·학습 등 사용자가 실행한 동작으로 한다. 프로젝트 전체, Geometry·DOE 등 변경하지 않는 모듈의 재생성을 요구하지 않는다.
- MCU의 기존 설정·XML·학습 결과는 계속 유효하다. MCU 전용 처리 보존과 회귀 검증은 이번 범위에 포함하며 MCU 형식 전환은 제외한다.

## 3. 이슈 계층

```text
[Epic] 다중 응답·다중 모델 파이프라인 — Sim 1D·ND 관리 형식 통일과 구형 데이터 재생성
├─ 독립 선행
│  ├─ GUI: ProcessJob 취소 후 실제 종료에서 finished
│  ├─ GUI: Sim 모델 차원 명시와 MCU 기존 처리 분리
│  ├─ DeepOpt: 실행 실패 코드와 명시 결과 경로
│  └─ GUI: 이번 실행의 결과 파일 표시
├─ 공통 계약
│  ├─ GUI: 모델 참조·상태 파일 판독·ID 발급
│  └─ DeepOpt: 상태 파일 writer·설정 판독·fixture
├─ 다중 응답 데이터셋
│  ├─ GUI: Launcher 응답 표 저장·복원
│  ├─ GUI: Sim XML 작성·파서의 배열 형식 전환
│  ├─ GUI: XML 하나에 응답 N개 쓰기
│  └─ DeepOpt: XML 응답 배열·중복 키 판독
├─ Builder
│  ├─ GUI: Sim 1D·ND 모델 행·옵션 저장
│  ├─ GUI: Builder 실행 수명
│  ├─ DeepOpt: 1D 행별 학습과 모델 ID 산출물
│  └─ DeepOpt: ND 행별 학습과 모델 ID 산출물
├─ Runner
│  ├─ GUI: Runner 모델별 선택 영속과 실행 모드
│  ├─ GUI: Runner 전체 참조 해석·일괄 실행
│  ├─ DeepOpt: 1D 모델 로더·입력 어댑터와 case별 CSV 예측
│  └─ DeepOpt: ND 모델 로더와 case·모델별 VTU 예측
└─ Optimizer
   ├─ GUI: Sim 1D Builder의 모델·심볼 선택
   ├─ GUI: 최적화 실행 계약과 Sim 1D 재검증
   ├─ DeepOpt: 선택한 1D 모델로 목적·제약식 평가
   └─ GUI: Optimizer 다중 Builder 참조
```

### 선행 관계

| 작업 흐름 | 선행 관계 |
|---|---|
| 독립 선행 | 넷 모두 선행 없음. ProcessJob → Builder 실행 수명. DeepOpt 실패 코드 → GUI 결과 표시, 모든 DeepOpt 학습·예측 |
| 공통 계약 | GUI: #722 → 참조·상태 파일 판독. DeepOpt: 선행 없음. 두 저장소의 fixture 내용을 맞춘다 |
| 데이터셋 | 응답 표 영속은 독립 착수. MCU 경계 분리 → Sim XML 배열 전환 → XML N개. DeepOpt XML 판독은 공통 계약 뒤 |
| Builder GUI | 공통 참조 + MCU 경계 → 모델 행 → 실행 수명. 실행 수명에는 ProcessJob과 XML 배열 전환도 필요 |
| Builder DeepOpt | 공통 계약 + XML 판독 + 실패 코드 → 1D 학습 → ND 학습 |
| Runner | GUI: 공통 참조 + 모델 차원 명시 → 선택 영속 → 일괄 실행 (결과 표시 필요). DeepOpt: 1D 학습 → 1D 예측 → ND 학습 → ND 예측 |
| Optimizer | GUI: 공통 참조 → 모델·심볼 선택 → 실행 계약 → 다중 Builder. DeepOpt: 1D 예측 (로더·어댑터) → 식 평가 |

GUI와 DeepOpt의 이슈는 각 저장소에 발행하고 같은 계약의 양쪽을 연결한다. 공통 manifest·상태 파일 fixture로 GUI 선택·실행 수명을 먼저 구현할 수 있다.

구현 순서는 1D 수직 완성이 먼저다. DeepOpt는 1D 학습 → 1D 예측 → 식 평가로 한 타입 집합에서 계약 전체를 검증한 뒤 ND 학습·예측을 같은 writer·로더 경계에 붙인다. GUI의 Builder·Runner 작업은 차원 무관 관리 형식이라 순서 제약이 없다. 이는 배포 분할이 아니며 ND까지 완성한 뒤 함께 배포한다는 결정과 충돌하지 않는다. 2절의 ND 저장 규격 (`config.yaml`·전처리 메타·basic/proto) 은 1D 구현 중에도 계약으로 유지한다.

v4의 별도 Runner 차원 경계 작업은 공통 모델 선택·실행 모드 작업에 합친다. 기존 ND 설정을 받아 주기 위한 선행 전환은 만들지 않는다. Sim 설정·XML·manifest·상태 파일을 바꾸는 PR은 모두 통합 브랜치에서 함께 검증한다.

### 통합과 검증

- Launcher → Sim 1D 학습·예측·최적화를 먼저 검증하고, Launcher → Sim ND 학습·예측을 그 뒤에 검증한다. 같은 XML, 같은 타입의 모델 두 개, 응답 여러 개, 부분 재학습·취소·기동 실패·삭제를 포함한다.
- 취소는 `finished` 뒤 보정으로 `Failed("사용자 취소")`가 남고 재열기 뒤 유지되는지, 정리 뒤 파일이 없는 행도 `Failed`가 되는지, 실제 종료 전 재실행·삭제가 거부되는지 확인한다.
- ND 학습·저장은 basic·proto 경로를 모두 확인한다. 직접 VTU 예측은 현재 지원 타입의 실제 실행과 미지원 타입의 사전 거부를 검증한다. 여러 case·모델의 결과 경로와 원본 VTU 보존을 확인한다.
- Smart의 실제 타입·부속 파일 재로딩과 입력 순서 반전을 검증한다. 다중 Builder 이슈 뒤 여러 Sim 1D Builder를 쓰는 최적화로 넓힌다. 유효한 v2 ND 모델도 Optimizer에서 거부되는지 확인한다.
- 구형 Sim 파일은 사용 거부·재생성 안내·기존 파일 무변경을 확인한다. 구형 Sim 학습·예측을 성공시키는 호환 검증은 두지 않는다. MCU는 기존 설정·XML로 열기·학습·폴링·중지·삭제·예측 회귀를 확인한다.
- `ProcessJob`은 취소 뒤 `finished` 1회·실제 종료 뒤 방출, 실행 중 소유자 소멸 시 GUI 스레드 비차단, 앱 종료 훅 회귀를 확인한다.
- fixture는 두 저장소의 `tests/fixtures/multi_model_v2/`에 같은 파일의 복사본을 둔다. 1D·ND 정상 사례, 잘못된 형식·참조, 깨진 상태 파일, MCU 경계 사례를 구분한다. 한 저장소의 테스트가 다른 저장소 checkout에 의존하지 않게 한다.

형식 불변인 ProcessJob 종료 계약, 실패 코드·결과 경로 수정, Launcher 응답 표 영속, MCU 경계 분리와 미사용 공통 헬퍼 추가분은 독립 검증 후 dev에 먼저 통합할 수 있다. 실제 Sim 형식 전환은 다음 절차를 따른다.

1. 두 저장소 각각 dev에서 `feat/multi-model`을 분기한다.
2. 전환 PR은 각 통합 브랜치로 squash merge 한다.
3. 1D 검증, ND 검증, MCU·Optimizer 회귀 후 통합 브랜치에서 dev로 PR을 만들어 squash merge 하고 브랜치를 삭제한다.
4. 검증한 GUI·DeepOpt 커밋 조합을 태그로 남기고 함께 배포한다.

[저장소 관리 수칙](https://github.com/NumeRealWorks/DashOpti_GUI/wiki/저장소-관리-수칙)에 따라 통합한다. 순차 배포를 위한 Sim v1/v2 이중 저장·장기 호환 계층·기능 플래그 체계는 추가하지 않는다. 배포 안내에 Sim 설정 재구성·XML 재생성·재학습·모델 재선택 순서를 명시한다.

## 4. 이슈 초안

각 초안은 저장소 하나의 구현 PR 범위다. 공통 규격을 적용하며, 아래 변경과 기대는 구현 완료 기준이다.

### GUI: ProcessJob이 취소 뒤 실제 종료에서 finished를 보낸다

현상

- `cancel()`이 QProcess를 떼어내고 즉시 `Cancelled`를 방출해, 소비자가 프로세스가 아직 파일을 쓰는 동안 종료 처리 (상태 보정·재실행·삭제) 를 한다. Builder는 500ms·1000ms 지연 재확인으로 피한다.

범위

- 건드림: `controller/async/ProcessJob.{h,cpp}`의 `cancel()`·`onProcFinished`·소멸자·`cancelAllRunning()`, `model/DashOptimizer.cpp::releaseRunningJob`, `view/DashModelBuilderWidgetBase.cpp::onStopTrainingClicked`, `tests/TestProcessRuntime.cpp`.
- 안 건드림: `Job` 상태 집합, 소비자의 `finished → deleteLater` 계약, 데몬 경로 (`DashExtensionProcess`), MCU Builder의 데몬 재시작 중지.

현재 구조

- `cancel()`은 트리 kill 뒤 QProcess를 분리하고 `setState(Cancelled)`를 동기 방출한다 (`ProcessJob.cpp:97`). 분리 이유는 소비자가 `finished`에서 `deleteLater` 하면 `~QProcess`가 실행 중 프로세스를 만나 `waitForFinished`로 GUI 스레드를 막기 때문이다. `releaseRunningJob`은 소유자 소멸 전 같은 분리를 위해 `cancel()`을 부른다. 소비자 코드는 `State::Cancelled`로 분기하지 않는다.

변경

- `cancel()`은 트리 kill과 취소 요청 기록만 한다. `onProcFinished`가 취소 요청이면 `Cancelled("사용자 취소")`, 아니면 종료 코드로 전이한다. `finished`는 프로세스 종료 뒤 한 번만 나온다. 기동 실패 경로는 그대로다.
- 실행 중 소멸하는 소멸자가 QProcess 분리 (disconnect·reparent·자기 `deleteLater`) 를 맡는다. `cancelAllRunning()`은 통지 차단·분리·즉시 종단을 유지한다. `releaseRunningJob`은 분리 호출을 없애고 disconnect만 남긴다.
- Builder 위젯의 중지 클릭은 중지 버튼만 잠그고, 시작 버튼은 `trainingFailed`·`trainingSucceeded`에서 푼다.
- 테스트: 취소 뒤 `finished`가 실제 종료 뒤 1회이고 상태가 `Cancelled`다. 실행 중 소멸 시 GUI 스레드가 막히지 않는다. `cancelAllRunning` 회귀는 유지한다.

기대

- 취소 뒤 `finished`를 받은 시점에 프로세스가 없다. Runner·Optimizer·TopOpt 후처리는 코드 변경 없이 취소 피드백만 종료까지 늦어진다. MCU Builder 동작은 변하지 않는다.

Related: 선행 없음. 후속: Builder 실행 수명. 형식 불변이므로 독립 검증 뒤 dev에 먼저 통합한다.

### GUI: Sim 모델 차원을 명시하고 MCU의 기존 처리를 분리한다

현상

- Sim의 형식 교체가 공유 base를 사용하는 MCU의 설정·상태·XML 처리까지 바꿀 수 있다. 모델 차원은 현재 첫 행 타입이나 표시 문자열에 의존한다.

범위

- 건드림: `DashModelBuilder`와 `DashModelBuilderMCU`의 공유 진입점, Sim Set 생성 시 모델 차원 선택, MCU가 쓰는 base 위젯·XML 파서 경계.
- 안 건드림: MCU 설정·상태·XML·산출물 형식, 새 variant 도입, 구형 Sim 차원 추정.

현재 구조

- MCU는 `loadDataLabelConfig`, XML 파서, 상태·오차 함수를 상속하며 `refreshTrainedModelInfo`를 명시 base 호출한다. Sim은 첫 행으로 CLI를 결정한다.

변경

- 기존 MCU 본문을 전용 함수 또는 override로 분리하고 모든 MCU 진입점이 이를 사용하도록 한다. 이후 Sim 1D·ND는 같은 새 관리 경로를 사용한다.
- 신규 Sim Set 생성 시 `modelDimension` 선택·기록을 구현하고 생성 뒤에는 바꾸지 않는다. 신규 생성과 기존 파일 열기를 구분하고 차원 누락·혼합·알 수 없는 타입을 거부한다. `(Field)` 판별과 기존 폴더 스캔에 의한 추정은 두지 않는다.

기대

- MCU의 기존 설정·XML·학습·폴링·삭제가 유지된다. 타이머, base 포인터, 명시 base 호출을 검증한다. Sim의 모델 차원은 재열기해도 유지되고 구형 Sim은 MCU 경로로 우회하지 않는다.

Related: 선행 없음. MCU 분리는 형식 전환 전 수행한다. 후속: Sim XML 전환, 모델 행, 실행 수명, Runner 실행 모드.

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

Related: 선행 없음. 후속: GUI 결과 표시, 두 차원의 학습·예측, 선택 모델 식 평가.

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

### GUI: 모델 참조·상태 파일 판독·ID 발급을 공통화한다

현상

- 응답·타입 중심의 참조로는 같은 타입의 여러 모델을 식별할 수 없다. 1D·ND 모델을 같은 규격으로 읽고 사용 가능 여부를 판단해야 한다.

범위

- 건드림: `DashModelBuilderArtifact`, `DashModelBuilderReference`, `LoadedArtifact`, `DashSurrogateModelCommon`과 fixture 경로 제공.
- 안 건드림: 각 모듈의 선택 UI, MCU의 기존 산출물 판독, 모델 알고리즘.

현재 구조

- #722가 Builder setId를 폴더·model_info로 해석하는 참조 계층을 도입한다. 산출물 판독은 `originRecord`만 읽고, Runner·Optimizer는 기존 최상위 `errors`를 응답·타입 키로 읽는다.

변경

- ModelRef·ModelEntry, 상태별 필수 필드 검증, `modelSeq` 발급, `{Builder}/{id}` 디렉터리와 `{id}/model.pt`의 고정 해석을 둔다. `LoadedArtifact`는 variant·modelDimension·manifest와 함께 Configuration 행마다 읽은 `{id}/model.json`의 모델 목록을 제공한다.
- Sim 1D·ND 모두 v2 판독과 ID 기반 경로를 사용한다. 사용 가능 여부는 상태 `Done`과 `model.pt` 존재로 판정하고 타입별 부속 파일 목록은 두지 않는다. 차원 적합성을 검증하고 공통 모델 행·metric 표시 자료를 만든다. 구형 산출물 읽기·타입 추정은 추가하지 않는다.
- `tests/fixtures/multi_model_v2/`에 1D·ND 정상, 잘못된 형식·참조, 깨진 상태 파일 사례를 두고 DeepOpt 저장소와 내용을 맞춘다.

기대

- 두 차원의 참조 round-trip, 상태별 검증, 잘못된 ID·모델 파일 누락 거부, 삭제 뒤 ID 미재사용을 확인한다. `Failed`·`In Progress` 모델은 선택할 수 없다. 깨진 상태 파일은 그 모델만 사용 불가로 만들고 다른 모델에 영향을 주지 않는다.

Related: 선행 #722. MCU 공통 호출부를 교체할 때는 MCU 처리 경계 분리가 필요하다. 후속: 모델 행, Runner 선택, Optimizer 선택.

### DeepOpt: 상태 파일 writer·설정 판독·fixture를 만든다

현상

- 학습·예측·최적화가 같은 Set JSON v2·manifest·`model.json` 규격을 읽어야 하고, 학습은 같은 writer로 상태 파일을 써야 한다. 조사 기준 DeepOpt에 `tests/` 디렉터리와 CI가 없다.

범위

- 건드림: 신규 `source/artifact.py` (상태 파일 통째 쓰기·판독·상태별 필수 필드 검증, Set JSON v2·manifest 판독과 거부 사유, 모델 디렉터리 경로), `tests/`의 pytest 설정·conftest·공통 fixture.
- 안 건드림: 모델 로더·DV 입력 어댑터 (1D 예측 작업), XML 파서 (XML 판독 작업), 각 학습 루프·결과 배치, MCU 엔진 계약.

현재 구조

- ND의 `ResultSaver`와 1D 저장 함수가 각각 최상위 `errors`를 read-modify-write 하고 소비자는 경로를 탐색한다.

변경

- `model.json`의 통째 쓰기 (같은 디렉터리 임시 파일 + `os.replace`) 와 판독·검증, v2 설정·manifest 판독과 구형 거부를 둔다. 다른 모델의 파일과 manifest를 건드리지 않는다.
- pytest 설정·conftest와 `tests/fixtures/multi_model_v2/` (1D·ND 정상, 잘못된 형식, 깨진 상태 파일) 를 마련한다. GUI 저장소의 같은 fixture와 파일 내용을 맞춘다.

기대

- 상태별 필수 필드 검증, 교체 실패 전파, 구형·잘못된 설정 거부를 테스트로 확인한다. 이 작업만으로 기존 학습·예측 동작은 바뀌지 않는다.

Related: 선행 없음. 후속: XML 판독, 1D 학습, 1D 예측. Sim 구형 파일용 fallback은 만들지 않는다.

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

Related: 선행: MCU XML 처리 경계 분리. 후속: XML N개와 Builder 실행 수명.

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

Related: 선행: Sim XML 배열 전환. DeepOpt 측 중복 키 검증은 DeepOpt XML 판독 작업이 맡는다.

### DeepOpt: XML의 응답 배열과 중복 키를 판독한다

현상

- 1D·ND 학습 데이터 빌더가 단수 응답 메타를 전제하고 중복 dict 키를 거부하지 않는다.

범위

- 건드림: `preprocessor/xml_parser.py`, `XMLTrainingDataBuilder`의 응답 메타 판독과 행별 응답 선택 함수.
- 안 건드림: 학습 루프와 행 순회, reduction 계산, ND 전처리.

현재 구조

- 파서가 `selected_response` 하나를 읽고 1D·ND가 각각 응답을 고른다.

변경

- `selected_responses[]`를 읽고 단수 키는 재생성 사유로 거부한다. 중복 dict 키와 입력·예약 키 충돌을 거부한다. 행의 `row.response`로 응답 하나와 그 메타를 얻는 접근 함수를 1D·ND 공통으로 둔다.

기대

- 응답 N개 XML에서 지정 키 하나를 얻고 단수 XML·중복 키는 사유와 함께 거부된다. GUI의 배열 fixture와 같은 파일로 검증한다.

Related: 선행: DeepOpt 공통 계약 (fixture). GUI XML 배열 전환과 같은 형식을 쓴다. 후속: 1D·ND 학습.

### GUI: Sim 1D·ND의 설정과 옵션을 모델 ID별 행으로 저장한다

현상

- 타입을 키로 하는 Configuration과 타입별 옵션 페이지는 동일 타입의 서로 다른 모델을 표현하지 못한다.

범위

- 건드림: Sim Configuration 조립·복원, `TrainingRowInput`·`buildTrainingStartPlan`, `DashModelBuilderWidget`의 행·옵션·복원, 설정 버전 검증.
- 안 건드림: MCU 행 모델, 실행 수명, 모델 학습 알고리즘.

현재 구조

- Configuration은 타입별 dict이고 `m_configWidgets[modelName]`으로 옵션을 관리한다. 1D·ND가 같은 Sim 위젯을 쓴다.

변경

- Sim 두 차원 모두 `{id, response, type, options, run}` 배열로 저장하고 ID별 옵션 페이지를 사용한다. 새 ID 발급·타입 변경·행 복원을 같은 경로로 처리한다.
- `response`는 행 추가 때 고르고 그 뒤 잠근다. 다른 응답은 새 행이다. `schema_version: 2`와 명시 모델 차원을 저장하고 상태·오차 키는 제거한다. 기존 dict 설정은 재생성을 안내하며 읽어 변환하지 않는다. ND 행에는 실제 필드 키와 `None` reduction을 적용한다.
- transformation 값을 복원하고 미적용 표시를 유지한다. 차원에 맞는 모델 타입만 선택하도록 검증한다.

기대

- 1D와 ND 각각 같은 타입의 두 행을 저장·재열기해 ID·run·서로 다른 옵션이 유지된다. 한 행의 타입 변경이 다른 행에 영향을 주지 않고 저장된 행의 응답은 바꿀 수 없다. MCU 행 동작은 유지된다.

Related: 선행: GUI 공통 참조·ID 발급, 모델 차원 명시·MCU 처리 경계. 후속: Builder 실행 수명. DeepOpt 두 학습 CLI와 같은 배열 계약을 사용한다.

### GUI: Builder 실행 수명을 모델 상태 파일 기준으로 처리한다

현상

- 학습 시작·폴링·종료 보정·재실행·삭제가 Set JSON 상태, 최상위 `errors`, 응답·타입 경로와 지연 재확인에 흩어져 있다. 데이터셋 교체는 삭제 실패 시 일관성이 없다.

범위

- 건드림: Sim 학습 시작 (검증·manifest·`In Progress` 초기화·실행 행 목록·기동), `checkModelStatusInternal`·`finalizeStaleStatuses`, 학습 결과·오차·목록·`getTestDatasetFiles`·삭제, 모델 행 갱신, `stopTraining`, 데이터셋 선택 잠금.
- 안 건드림: MCU 학습·상태·삭제, 같은 XML의 내용 변경 감지 (#650), DeepOpt의 디렉터리 정리.

현재 구조

- Builder는 XML 메타를 model_info로 복사하고 상태를 Set JSON에 쓴다 (`model/DashModelBuilder.cpp:782`, `:886`). 종료 뒤 500ms·1000ms 지연 재확인 뒤 남은 `In Progress`를 `Failed`로 쓴다 (`:1545`, `:1723`). 오차는 최상위 `errors`, 결과는 응답·타입·오차 경로에 있다.

변경

- 시작: 행·응답·옵션·차원을 검증하고 manifest 출처와 현재 XML 출처 일치를 확인한다. manifest를 쓰고 실행 행의 `{id}/model.json`을 `In Progress`로 통째로 쓴다 (`QSaveFile`). 실행 행 목록을 보관하고 기동한다. 초기화 실패 시 기동하지 않고 이미 쓴 행을 보정한다.
- 폴링: 이번 실행 행만 읽는다. 파일 없음은 진행 중, 읽기 실패는 직전 유지.
- 보정: `finished`에서 실행 행 중 `Done`·`Failed`가 아닌 행을 `Failed`와 사유로 쓴다. 지연 재확인을 제거한다. 보정 실패는 오류 표시와 실행·삭제 차단, 재열기 시 남은 `In Progress`는 미완료로 표시만 한다. 실제 종료 전에는 재실행·삭제를 거부한다.
- 결과·오차·metric 표시와 삭제를 ID와 모델 디렉터리 기준으로 바꾼다. 삭제는 행 뒤 디렉터리, 실패는 로그. ND metric·렌더링 결과를 표시한다.
- manifest가 있는 Builder는 `Dataset` 선택을 잠근다. 교체 확인·전체 삭제 경로는 만들지 않는다.

기대

- 두 차원 공통으로 부분 재학습·취소·기동 실패·초기화 실패·보정 실패·삭제를 검증한다. 취소 뒤 `Failed("사용자 취소")`가 재열기 뒤 남는다. 정리 뒤 파일이 없는 행도 실제 종료 뒤 `Failed`가 된다. 잠긴 데이터셋은 바꿀 수 없고 manifest와 다른 XML은 거부된다. Data Label 편집만으로 전체 결과를 지우지 않는다. MCU는 기존 경로로 동작한다.

Related: 선행: ProcessJob 종료 계약, 공통 참조, 모델 행, Sim XML 배열 전환. fixture로 먼저 구현하고 실제 학습 검증은 DeepOpt 1D 학습 뒤 수행한다.

### DeepOpt: Configuration의 실행 행마다 1D 모델 하나를 학습해 모델 ID 디렉터리에 둔다

현상

- 1D 학습은 타입별 dict를 순회하고 행의 선택 응답 하나로 제한하지 않으며, `{response}/{Type}_{err}` 저장·최상위 `errors` read-modify-write·Set JSON 상태 갱신을 한다.

범위

- 건드림: `main.py::train_model_1d`, `run_train_1d` (`_save_model_info_json`), `XMLTrainingDataBuilder.build_1d`, `models/oned/*trainer.py`, `smart_trainer.py`의 저장 경로·후보 정리·결과 반환.
- 안 건드림: ND 학습, UI transformation 계산, 학습 알고리즘.

현재 구조

- `_update_json_status`로 Set JSON을 갱신한다. reduction의 `SUM` 비교와 GUI의 `Sum` 표기가 다르다. Smart는 후보를 정리해 우승 모델을 남긴다.

변경

- 유효한 Sim 1D 설정·manifest를 검증한 뒤 `run:true` 행 전부의 `{id}/`를 비운다. 정리 실패 행은 `Failed`를 쓰고 건너뛴다. 행마다 `row.response` 하나를 학습한다.
- 트레이너는 `{id}/model.pt`와 타입별 부속 파일을 쓰고 실제 타입·입력 순서·오차를 반환한다. 공통 writer가 행 종료 시 `model.json`을 쓴다. 입력 스칼라·유한값·열 수와 응답 스칼라를 검증하고 reduction을 정규화한다.
- Smart 후보는 `{id}/candidates/{type}/`에서 관리하고 우승 모델·부속 파일·`Model_Error.csv`를 `{id}/`에 보존한다. 최상위 `errors` 쓰기와 Set JSON 상태 갱신을 없앤다. 한 행이 실패해도 다음 행을 계속하고 최종 종료는 실패로 반환한다.

기대

- 같은 타입 두 행의 별도 결과, `run:false` 보존, Sum 계산, 실제 DV 순서, 다성분 응답 거부, 정리 실패 행의 `Failed`를 확인한다. Smart의 RF·MLP·BNN 우승 사례를 재로딩한다. GUI 실행 수명과 통합 검증한다.

Related: 선행: DeepOpt 공통 계약, XML 판독, 실패 코드 처리. 후속: 1D 예측, ND 학습.

### DeepOpt: ND를 행별 학습과 공통 산출물 형식으로 전환한다

현상

- ND는 Configuration dict·Set 상태·최상위 errors·응답 및 오차 경로를 모두 사용한다. 설정·상태만 바꾸면 저장·로딩 경로가 계속 이원화된다.

범위

- 건드림: `main.py::train_model_nd`, `run_train_nd_basic.py`, `run_train_nd_proto.py`, `trainer_utils/result_saver.py`의 대상 응답·저장·오차·정리·입력 순서 반환.
- 안 건드림: 모델 네트워크·손실·학습 알고리즘, 기존 정규화·역변환 계산, 새 ND 타입 추가.

현재 구조

- CLI는 타입별 Configuration을 순회하고 전체 Output을 넘긴다. basic·proto 모두 ResultSaver를 사용하며 `{response}/{Type}_{err}/` 폴더와 최상위 오차를 작성한다.

변경

- 1D 학습과 같은 진입 규칙을 쓴다. 설정 검증 뒤 실행 행 전부의 `{id}/`를 비우고 행마다 `row.response` 하나만 전달한다. basic은 해당 필드 하나를 대상으로, proto도 단일 target 목록으로 실행한다. ND 필드의 성분 구조와 전처리는 보존한다.
- 각 행의 `{id}/`를 작업·출력 범위로 사용하고 `model.pt`, `config.yaml`, 정규화·전처리 메타, 평가 CSV·렌더링·로그를 함께 둔다. 실제 DV 순서를 반환하고 config와 상태 파일을 일치시킨다. 모델·필수 부속 파일이 준비된 뒤 공통 writer로 `model.json`을 쓴다. 실패 시 해당 ID만 실패 처리한다. manifest에는 쓰지 않는다.
- basic·proto의 파일 정리와 CSV 경로를 함께 바꾼다. Sim에서 Set JSON 상태 갱신을 없애고 `_update_json_status`는 남은 호출 여부를 확인한 뒤 정리한다.

기대

- basic·proto 각각 새 형식으로 학습·재로딩된다. 같은 타입 두 행과 서로 다른 응답, 부분 재학습·실패, ID별 로그·CSV·부속 파일 보존을 확인한다. ND 필드에 1D 스칼라 응답 제약을 적용하지 않는다.

Related: 선행: 1D 학습 (진입 규칙·writer 재사용), 실패 코드 처리. GUI 실행 수명과 함께 검증하고 ND 예측의 학습 산출물을 제공한다.

### GUI: Runner의 모델별 선택 영속과 차원별 실행 모드를 정리한다

현상

- 응답·타입 쌍으로 선택하면 같은 타입의 여러 모델을 구분할 수 없다. 체크만 바꾸면 복원되지 않고 (#724), 행별 ND·1D 분할과 설정 이중 쓰기도 남아 있다.

범위

- 건드림: `DashModelRunnerConfig`의 선택 항목 저장·복원·버전 검증, `DashModelRunnerWidget::populateSurrogateTable`, PresentationModel의 선택 수집·실행 모드.
- 안 건드림: Runner의 단일 Builder 참조, MCU Runner, 예측 알고리즘, 실행 직전 `path` 해석.

현재 구조

- 표는 응답별 모델 선택 중심이며 `groupCheckedPairs`로 차원을 나눠 설정을 두 번 쓴다. #722의 `Output Response[]`는 `{set, response, model}` 쌍이고 Run 시점에만 쓴다.

변경

- 1D·ND 모두 사용 가능한 모델당 한 행으로 표시하고 `{set, model_id, response, model}` 항목을 체크·콤보 변경 시 저장·복원한다. 별도 선택 키는 두지 않는다.
- 참조 Builder의 `modelDimension`으로 실행 모드·metric·결과 표시를 고르고 행별 분할과 이중 쓰기를 제거한다. 새 설정만 열며 구형 설정의 선택 추정·빈 선택 변환은 하지 않는다.
- ND 직접 예측 미지원 모델은 이유를 표시하고 실행 선택을 막는다. 표시되는 학습 모델 목록과 실행 지원 여부를 구분한다.

기대

- 1D·ND 각각 같은 응답·타입의 서로 다른 ID가 독립 선택·복원된다. Run 없이 체크만 바꿔도 재열기 뒤 복원되고 한 실행은 한 차원이다. #724의 두 증상이 사라진다.

Related: 선행: GUI 공통 참조, Sim 모델 차원 명시. 후속: 전체 참조 해석·일괄 실행. ND 지원 여부는 DeepOpt 예측 계약과 맞춘다. #724를 닫는다.

### GUI: Runner가 전체 참조를 해석해 한 번에 실행한다

현상

- 저장된 선택만으로는 실제 모델 파일·실행 지원 여부를 보장할 수 없고, 1D·ND 호출과 결과 처리 경로가 나뉘어 있다.

범위

- 건드림: `DashModelRunner::run1DPrediction`·`runNDPrediction`, 엔진 입력 조립·저장, case·모델별 결과 경로 연결.
- 안 건드림: 예측 알고리즘, 다중 Builder 선택, 새 영속 case ID 체계, DV 재배열.

현재 구조

- 기존 모델 참조는 응답·타입·폴더를 사용하고 차원별로 다른 함수가 설정을 쓴다.

변경

- 모든 선택 항목의 행 존재·`Done`·`model.pt`·실행 지원 여부를 상태 파일에서 먼저 확인한다. 하나라도 실패하면 설정 저장·CLI 실행을 하지 않는다.
- 각 항목에 `path` (`{Builder}/{model_id}`) 를 더해 한 번 저장하고 Builder 차원에 맞는 CLI를 한 번 실행한다. `trained_type`·`input_order`는 쓰지 않고 case의 DV label/value는 그대로 전달한다. ND는 현재 실행 설정의 case 순번과 model_id로 결과 경로를 만들고 결과 표시와 연결한다.
- 실행 전 결과 파일 정리와 실패 처리를 공통으로 적용한다.

기대

- 두 차원 각각 2 case × 2 model을 한 호출로 실행한다. ND의 같은 표시명·같은 입력 파일 case도 결과가 충돌하지 않는다. 참조 실패·재실행·부분 실패 처리가 두 차원에 동일하게 적용된다.

Related: 선행: Runner 선택 영속, GUI 명시 결과 표시. DeepOpt 1D·ND 예측과 통합 검증한다.

### DeepOpt: 1D 모델 로더·입력 어댑터로 case당 CSV 한 행을 모은다

현상

- 1D 예측은 기존 경로에서 glob으로 모델을 찾고 응답 이름으로 CSV를 기록해, 동일 응답의 모델 결과가 겹치거나 흩어진다. 타입별 로더와 DV 매핑이 호출부마다 다르다.

범위

- 건드림: 신규 1D 모델 로더 (`path`의 `model.json`에서 `trained_type`·`input_order`를 읽고 타입별 로더로 `model.pt`·부속 파일 로딩), 입력 어댑터 (label/value → `input_order`), `main.py::test_model_1d`, `_write_1d_test_result_to_csv`, `RunTest1D`.
- 안 건드림: 1D 예측 알고리즘, ND 예측, 학습 코드.

현재 구조

- `{response}/{Type}_{err}` 탐색과 파일명 추정으로 모델을 고른다.

변경

- 항목의 `path`에서 모델을 읽고 어댑터로 DV를 배치한다. 누락·중복·비유한 값·길이 불일치를 거부하고 정렬로 대체하지 않는다. active case당 한 행, `{response} [{model_id}]`별 열로 집계해 지정 CSV에 저장한다.
- 참조·로딩·예측·저장 실패를 전파한다. 같은 표시명의 case를 합치지 않는다. 로더·어댑터는 최적화 작업이 재사용한다.

기대

- 두 모델과 두 case에서 정확히 2행·모델 열 2개를 얻는다. 입력 순서 반전·재실행·한 모델 실패·Smart 실제 타입 재로딩을 검증한다.

Related: 선행: 1D 학습 (산출물), 공통 계약, 실패 코드·명시 결과 경로. GUI Runner 일괄 실행과 같은 CSV 계약을 사용한다. 후속: 선택 모델 식 평가.

### DeepOpt: ND 모델 로더로 case·모델별 VTU를 저장한다

현상

- 첫 Output Response만 사용하고 모델 경로를 탐색하며 입력 VTU에 결과를 쓴다. DV를 정렬하거나 첫 체크포인트를 고르면 선택 모델의 학습 계약과 달라질 수 있다.

범위

- 건드림: ND 로더 (`path`의 `model.json`·`config.yaml` 일치 검증과 `model.pt` 로딩), `main.py::test_model_nd`, `source/run_test_nd.py::RunTestNDFromVTU`의 항목 순회·DV 순서·결과 저장·실패 반환.
- 안 건드림: 새 ND 추론 알고리즘, 현재 미지원 타입의 직접 VTU 예측 구현, 모델 네트워크.

현재 구조

- `Output Response[0]`과 `{model}_*` 탐색을 사용한다. `RunTestNDFromVTU`는 `.pt` 대신 첫 `.ckpt`를 고르고 DV를 알파벳순 정렬하며 `output_vtu_path`를 사용하지 않는다. 일부 타입은 실행 본문이 없다.

변경

- 전체 선택과 active case를 순회한다. `path`의 `model.pt`를 직접 사용하고 `config.yaml`의 타입·응답·DV 순서를 `model.json`과 대조한다. 다른 체크포인트나 경로로 대체하지 않는다.
- 1D 예측의 입력 어댑터로 학습 때의 DV 순서를 구성하고 기존 정규화·역변환을 적용한다. 결과는 명시한 `case{N}/{model_id}/prediction.vtu`에 쓰며 원본 VTU를 수정하지 않는다.
- 실제 지원 타입만 실행한다. 미지원·로딩·예측·저장 실패를 명확히 반환하고 출력이 없는 경로를 성공으로 반환하지 않는다.

기대

- 지원 타입의 2 case × 2 model 결과 네 개가 독립적으로 남는다. 같은 표시명의 case와 다른 DV 순서, 원본 파일 보존, 정확한 모델 파일 사용을 확인한다. 미지원 타입은 GUI·CLI에서 거부된다.

Related: 선행: ND 학습 (산출물), 1D 예측 (어댑터), 실패 코드·명시 결과 경로. fixture로 먼저 구현하고 실제 저장 파일 검증은 ND 학습 전환 뒤 수행한다.

### GUI: Sim 1D Builder의 모델과 심볼을 저장·복원한다

현상

- 기존 Optimizer는 응답·타입 중심으로 모델을 복원하고 심볼을 행 순서로 다시 부여한다. 삭제한 심볼이 재발급되면 남은 식이 다른 모델에 연결된다. ND도 새 형식을 사용하므로 형식 버전만으로 최적화 대상을 고를 수 없다.

범위

- 건드림: `DashOptimizer`의 SurrogateModelInfo·save/load·DV 복원, 모델 선택 표, Builder 선택·Preview·`performMorphing`, `symbolSeq`.
- 안 건드림: 식 편집기, ND 최적화, 프로세스 호출, 구형 설정 복원, 다중 Builder 참조.

현재 구조

- `modelBuilder {set, name}`은 DV·Preview의 단일 출처다. 기존 선택 항목은 응답·타입·심볼 중심이고 심볼은 `r{i}`로 표를 채울 때마다 재부여한다. Builder 선택에 이름 일치 추정이 있다.

변경

- 참조 Builder의 사용 가능한 모델을 행으로 선택하고 `{set, model_id, response, model, symbol}`로 저장한다. Builder 목록은 명시적으로 Sim 1D의 유효한 v2만 허용한다. `(Field)` 판별과 이름 일치 추정을 제거한다.
- 새 Optimizer 설정의 버전을 기록하고 심볼은 `symbolSeq`로 발급·보존한다. 삭제한 심볼은 재사용하지 않는다. 참조 Builder로 DV·Preview를 복원하고 필요한 라벨이 없으면 거부한다.

기대

- 모델 세 개와 심볼이 저장·복원되고 재열기 뒤 심볼이 바뀌지 않는다. `r3` 삭제 뒤 새 행은 `r4`를 받는다. 유효한 v2 ND Builder와 MCU Builder는 선택할 수 없다.

Related: 선행: GUI 공통 참조. 후속: 최적화 실행 계약, Optimizer 다중 Builder 참조. #726의 Optimizer 재적용 작업과 범위를 맞춘다.

### GUI: 최적화 실행 직전에 Sim 1D 참조와 새 CLI 계약을 검증한다

현상

- Builder 디렉터리 하나를 넘기는 호출은 선택 모델을 명시하지 못한다. 저장 후 변경되거나 잘못된 설정으로 들어온 ND 참조·응답 불일치도 실행 전에 차단해야 한다.

범위

- 건드림: `DashOptimizer::runOptimization`의 참조 해석·차원 검증·엔진 입력 저장·argv.
- 안 건드림: 선택 UI, 최적화 알고리즘, 결과 그림 형식, GUI의 식 심볼 사전 검증.

현재 구조

- 호출은 `run-optimization <trainedModelPath> <json> --output-dir <dir>`이며 Builder 폴더에서 경로를 만든다.

변경

- 모든 참조의 Sim·1D·v2 조건, 행 존재, `Done`·`model.pt`, 저장된 `response`와 `model.json`의 `response` 일치를 재확인한다. 성공한 경우에만 각 항목에 `path`를 더해 한 번 저장한다.
- `run-optimization <OptSet.json> --output-dir <dir>`로 호출하고 Builder 디렉터리 인자를 제거한다.

기대

- 삭제된 참조, ND·MCU 참조, 구형 설정, 응답 불일치는 저장·실행 없이 사유를 표시한다. 정상 실행은 선택한 모델을 사용하고 실제 출력 위치의 수렴 그림을 연다.

Related: 선행: Sim 1D Builder 모델 선택, GUI 명시 결과 표시. 후속: Optimizer 다중 Builder 참조. DeepOpt 선택 모델 식 평가와 통합 검증한다.

### DeepOpt: 선택한 1D 모델로 목적·제약식을 평가한다

현상

- 최저 오차 파일을 자동으로 고르면 GUI가 선택한 모델과 다른 모델을 사용한다. 일반 응답과 `std_pred`도 같은 DV 순서로 평가해야 한다.

범위

- 건드림: `main.py::run_optimization`, `MainOptimizer`, `problem_setup.py`, `symbolic_module.ExpressionEvaluator`의 1D 로더·어댑터 연결.
- 안 건드림: 최적화 알고리즘, `optimum.json`, 별도 fitting 경로, ND 최적화.

현재 구조

- `_build_response_paths`가 응답 경로의 모델 파일 중 최저 오차를 고른다. 일반 응답과 `std_pred`를 처리하는 호출부가 나뉘어 있다.

변경

- Builder 디렉터리 인자를 없애고 항목의 `path`로 1D 예측 작업의 로더·입력 어댑터를 구성한다. 최저 오차 파일 탐색과 타입 경로 추정을 제거한다.
- 최적화에서는 1D 타입만 받아 ND를 거부한다. 미정의 심볼은 실행 전 실패로 반환한다. 일반 응답·`std_pred`·deterministic/probabilistic 평가를 같은 어댑터에 연결하고 실패 코드를 전파한다.

기대

- 모델 세 개로 입력 순서 반전·Smart 실제 타입·목적 및 제약 계산값을 확인한다. 항목마다 `path`를 받으므로 서로 다른 Builder 디렉터리의 모델도 같은 경로로 처리된다. ND 모델을 직접 CLI에 전달해도 거부하고 다른 모델로 대체하지 않는다.

Related: 선행: 1D 예측 (로더·어댑터), 실패 코드 처리. GUI Optimizer 실행 계약과 함께 검증한다.

### GUI: Optimizer가 여러 Sim 1D Builder의 모델을 참조한다

현상

- Builder 하나의 모델만 고를 수 있어 서로 다른 Launcher Set에서 학습한 응답을 한 최적화에 쓸 수 없다.

범위

- 건드림: `DashOptimizer`의 Builder 선택 표, DV·Preview 출처 선택, Preview·Morphing 활성 조건, 저장 항목의 `set` 해석, 실행 직전 재검증.
- 안 건드림: 모델 항목 형식, DeepOpt 식 평가, ND 최적화, Runner.

현재 구조

- 모델 항목은 이미 `{set, model_id, response, model, symbol}`을 담지만, 선택 UI와 DV·Preview 출처는 참조 Builder 하나다.

변경

- 행마다 Builder를 고른 뒤 그 Builder의 사용 가능한 모델을 선택한다. 기본 Builder가 DV·Preview 출처이며 참조한 모든 Builder의 DV 라벨 집합이 같아야 한다. Geometry Set id가 다르면 Preview·Morphing을 비활성화한다.
- 실행 직전 재검증을 모든 참조 Builder에 적용한다. 항목 형식과 DeepOpt 호출은 바꾸지 않는다.

기대

- 두 Builder의 모델 세 개와 심볼이 저장·복원된다. 입력 집합 불일치 거부, Geometry 출처 불일치 시 Preview 제한을 확인한다.

Related: 선행: Sim 1D Builder 모델 선택, 최적화 실행 계약. 형식 변경 없음.

## 5. 범위 밖과 확인 사항

### 범위 밖

- MCU의 새 형식 전환과 MCU 기존 데이터 재생성. 기존 코드 경계 분리와 회귀 검증은 포함한다.
- Sim 구형 설정·XML·학습 결과의 자동 변환, 차원·모델 추정, 기존 선택 복원, 양 형식 동시 저장.
- 다른 component의 응답 통합, 벡터 DV 펼침, 한 Builder Set에서 1D·ND 혼합 실행.
- ND의 새 네트워크·학습 알고리즘·새 직접 VTU 예측 지원 타입, ND 최적화. ND 모델 관리 형식과 기존 지원 예측 경로의 전환은 포함한다.
- KPI·BORE/BOSS의 별도 XML 통합. Sim이 소비하는 응답 메타 변경은 포함한다.
- 모델 이력·복구, 같은 XML의 내용 변경 감지 (#650), DOE 리샘플링 참조 (#684), Runner 다중 Builder 선택.
- UI transformation의 실제 계산 추가. 값 보존·미적용 표시와 모델 내부의 기존 정규화 정보 보존은 포함한다.
- GUI의 타입별 부속 파일 검증. 사용 가능 판정은 상태 `Done`과 `model.pt` 존재로 한다.
- GUI의 식 심볼 사전 검증. 미정의 심볼 검증과 실패 반환은 DeepOpt가 맡는다.
- Builder 안의 데이터셋 교체. 다른 데이터셋은 새 Builder로 한다. 같은 응답·다른 reduction 모델.
- 실행 직전 별도 실행 요청 파일. 엔진 입력은 Set JSON과 항목별 `path`다.
- 파일 교체 경합 재시도, 부분 삭제 실패 복구, 사용 중 심볼 삭제 차단, 트리 kill 실패 시 고아 워커의 늦은 쓰기 방지, 취소 대기 타임아웃. 별건으로 다룬다.

### 착수 전 확인

- 대상 Deck이 같은 component·충돌 없는 응답 키·스칼라 DV라는 제약을 만족하는지 확인한다. ND의 형상·필드 텐서는 별도 모델 입력이다.
- 기존 Sim 자료의 재구성·XML 재생성·재학습에 필요한 원본 데이터와 설정 정보를 사용자가 확보할 수 있는지 확인한다. 자동 변환 도구나 구형 차원 분류 작업은 만들지 않는다.
- `ProcessJob` 소비자 6곳의 취소 직후 가정 (버튼 상태, 소유자 소멸 경로, 테스트) 을 목록으로 확정한다.
- MCU가 공유하는 XML·설정·상태·삭제 진입점과 명시 base 호출을 확인하고 기존 fixture를 확보한다. MCU의 기존 데이터 생산·소비 경로를 Sim 전환과 함께 바꾸지 않는다.
- ND의 basic·proto별 필수 저장 파일, 실제 DV 순서의 출처, 직접 VTU 예측 지원 타입을 코드 기준으로 확정한다. 지원 목록을 GUI와 DeepOpt 검증에 일치시킨다.
- 공통 fixture에 1D·ND 새 설정·XML·manifest·상태 파일, ND config·체크포인트 재로딩 사례, 구형 거부 사례, 깨진 상태 파일 사례, Optimizer의 v2 ND 거부 사례를 준비한다.
- GUI·DeepOpt를 함께 배포하고 Sim 재생성 절차를 안내할 수 있는지 확인한다. 1D 수직 완성 뒤 ND 저장·로딩 전환을 일정에 포함한다.
