# Model Builder XML 구성과 DeepOpt 학습 입출력

ModelBuilder의 Sim 경로에서 해석 결과 XML이 만들어지고, GUI 설정을 통해 DeepOpt에 전달된 뒤, 학습 배열과 모델 파일로 바뀌는 과정을 설명한다. GUI는 XML의 라벨·shape·메타데이터를 읽고 학습 설정 JSON을 만든다. 실제 tensor 디코딩, 입력·정답 구성, 정규화와 학습은 DeepOpt 프로세스 안에서 수행한다.

기준일은 2026-10-02이며 GUI `5a4e6b96268b6919239eccc0dd416499867b4672`, DeepOpt `a4222b69cf3ec64864c99ae3fbd4aa4dddb77f4c`의 로컬 소스를 대조했다. 아래 코드 링크는 해당 커밋에 고정했다. 배포된 EXE가 이 DeepOpt 커밋과 같은지는 확인하지 않았다. MCU의 CSV 학습 경로는 범위 밖이다. 화면 동선은 [Model Builder 사용자 플로우](Code-Map-User-Flow-Model-Builder.md)를 참고한다.

## 전체 데이터 흐름

```text
DOE 설계변수 값 + 해석 결과의 형상·응답
  → GUI DashResultXmlWriter
  → dataset.xml
      ├─ GUI Load: 샘플 수 + 첫 샘플 라벨·shape
      ├─ GUI 학습 시작: model_info → 결과 폴더/model_info.json
      └─ DeepOpt: 실제 수치 데이터 디코딩

GUI에서 Input/Output·reduction·모델 옵션 선택
  → configs/ModelBuilder_Set1.json
  → DashOptiDeepOpt.exe train-model-1d 또는 train-model-nd
      ├─ XML 읽기 → 전처리 → 학습 → 평가
      ├─ 모델·스케일러·설정·VTU 저장
      ├─ model_info.json의 errors 갱신
      └─ 입력 설정 JSON의 status·error 갱신
  → GUI가 JSON·파일을 다시 읽어 상태와 결과 표시
```

## XML 구성

### 샘플과 메타데이터의 위치

일반 생성 경로는 `DashAnalysisLauncher`가 `root`와 샘플용 `dict`를 만들고, `DashResultXmlWriter`가 샘플과 메타데이터를 기록한다. `model_info`는 샘플용 dict 내부가 아니라 root 아래의 형제 항목이다. [XML writer][gui-writer]

`dict`는 사전, `dict_item key`는 항목의 키다. 값의 형식은 `tensor`, `string`, `float` 등의 태그로 표현한다. 설계변수의 실제 값은 각 샘플의 tensor에 들어가고, `model_info.parameter`는 출처와 범위 등의 메타데이터다.

생산 단계의 상세와 항목별 원천은 [Preprocessor의 XML 생성 절차와 구성요소별 출처](Preprocessor-XML-Generation-And-Provenance.md)를 참고한다. 해당 문서는 GUI `f71b8e8` 기준의 별도 검토다.

| 항목 | 개별 샘플의 dtype과 shape | 의미 |
|---|---|---|
| 설계변수 | `float32`, `[1]` | DOE의 해당 샘플 값 |
| `node_location` | `float32`, `[N,3]` | 노드 N개의 좌표 |
| `connectivity` | `int32`, `[E,K]` | 요소 E개의 노드 인덱스. K는 최대 연결 수와 8 중 큰 값. 남는 칸은 `-1` |
| 스칼라 필드 | `float32`, `[N,1]` | 노드별 응답 |
| 벡터 필드 | `float32`, `[N,C]` | 노드별 C개 성분 |
| `parameter.<변수>.source` | `string` | 변수를 정의한 DV 설정 파일 |
| `parameter.<변수>.meta` | `float` 또는 `string`의 사전 | `min`, `max`, `mean`, `std` 등 |
| `selected_response` | 문자열 사전 | `component`, `load_step`, `name`, `file_name` |

writer는 변수명과 응답명의 공백 및 일부 특수문자를 `_`로 바꾼다. JSON 라벨은 이렇게 만들어진 XML 키와 일치해야 한다. `parameterInfo`가 비어 있으면 현재 writer는 `model_info` 전체를 쓰지 않는다. [XML writer][gui-writer], [이름 변환][gui-utils]

### tensor의 실체

tensor 본문은 숫자 문자열이 아니라 배열의 바이너리 바이트를 Base64로 변환한 것이다. 필드 값은 노드, 성분 순서로 기록한다. DeepOpt는 다음 식으로 복원한다. [XMLTrainingDataBuilder][deep-xml]

```python
dtype = np.dtype(elem.get("dtype"))
# shape 속성을 정수 tuple로 해석한 후
raw = base64.b64decode(elem.text.strip().encode("ascii"))
arr = np.frombuffer(raw, dtype=dtype).reshape(shape)
tensor = torch.from_numpy(arr.copy())
```

예를 들어 `float32`, `[100,3]`이면 300개 숫자, 1200바이트를 100행 3열로 복원한다. shape와 바이트 수가 맞지 않으면 reshape 등에서 실패한다. 별도의 엔디언 변환은 없으므로 writer가 쓴 바이트와 NumPy dtype의 해석이 일치해야 한다. Base64가 아닌 본문은 `ast.literal_eval()`로 해석한 뒤 `torch.tensor()`로 변환한다.

## GUI에서 DeepOpt로 전달

### Load 단계

`DashModelBuilder::onLoadButtonClicked()`는 먼저 `root/dict` 직계 항목 중 정수 키의 수를 세고, 파일을 되감아 `key="0"`의 라벨과 shape를 읽는다. Base64를 수치 배열로 디코딩하지 않는다. 샘플 수 S를 shape 앞에 붙여 `[N,1]`을 `[S,N,1]`로 표시한다. 다른 샘플의 키와 shape가 같은지는 검사하지 않는다. [GUI Load][gui-builder]

GUI는 저장된 분류가 없으면 표시 shape가 2축인 라벨을 Input, 3축 이상인 라벨을 Output에 놓는다. `node_location`과 `connectivity`는 특별한 Input이다. XML 자체에는 Input과 Output 구분이 없다. [라벨 분류][gui-widget-base]

### 설정 JSON

Set Dataset은 XML 절대 경로, Input과 Output, reduction, 출력 transformation을 저장한다. 학습 시작 시 모델 옵션을 `Configuration`에 기록한다. 다음은 스칼라 회귀 예시이며 형상 입력은 생략했다. [설정 저장과 실행][gui-builder], [옵션 구성][gui-pm]

```json
{
  "variant": "Sim",
  "Data Label": {
    "Dataset": "C:/Project/AnalysisLauncher_Set1/stress.xml",
    "Input": {
      "Thickness": { "reduction": "None" },
      "Force": { "reduction": "None" }
    },
    "Output": {
      "Stress": { "reduction": "Max", "transformation": "None" }
    }
  },
  "Configuration": {
    "MLP": {
      "run": true,
      "response": "Stress",
      "best_model_epoch": 3000,
      "loocv": false,
      "status": "In Progress",
      "error": ""
    }
  }
}
```

`Data Label.Input/Output`의 키가 데이터 선택에 쓰이고, `Configuration`의 키는 모델 종류다. GUI는 같은 모델을 여러 행에 등록하는 것을 거부한다. 모델 이름을 키로 사용하는 구조이므로 같은 MLP를 응답별로 서로 다른 설정의 여러 항목으로 표현하지 않는다.

설정은 내부 폴더의 `configs/ModelBuilder_{Set}.json`, 결과는 내부 폴더의 `ModelBuilder_{Set}/`에 저장한다. GUI 코드에서 내부 폴더는 `.dproj`로 설명된다. [경로 규칙][gui-io]

### 프로세스 실행과 메타데이터

```text
extensions/deep_opt/DashOptiDeepOpt.exe
  train-model-1d <설정 JSON 절대 경로>
  --output-dir <결과 폴더 절대 경로>
```

ND는 `train-model-nd`를 사용한다. GUI는 `ProcessJob`으로 실행하며, 배열을 IPC로 보내거나 중간 CSV를 생성하지 않는다. DeepOpt가 JSON 안의 XML 경로를 직접 연다.

학습 시작 전에 GUI는 XML의 `model_info.parameter`와 `selected_response`를 읽어 결과 폴더의 `model_info.json`으로 옮긴다. 파일 앞부분과 끝부분을 먼저 살펴보고, 해당 부분을 사용할 수 없으면 전체를 순차 탐색한다. Set Dataset에서 호출하는 `createModelInfoJson()`은 현행 구현에서 기존 JSON을 보존해 저장할 뿐이다. XML 메타데이터를 반영하는 시점은 학습 시작이다. [메타데이터와 실행][gui-builder]

## DeepOpt의 공통 진입점

`main.py`의 `train_model_1d()`와 `train_model_nd()`는 JSON을 읽고 `run`이 참인 모델들을 순서대로 실행한다. 같은 설정 JSON에 시작 시 `In Progress`, 정상 완료 시 `Done`, 모델별 예외 시 `Refused`와 오류 문자열을 쓴다. 한 모델이 실패해도 다음 모델로 진행하므로 프로세스 종료만으로 전체 성공을 판단할 수 없다. [CLI][deep-main]

중요한 실제 동작은 다음과 같다.

- `Configuration.<모델>.response`는 trainer 호출 전에 제거한다. **학습 대상으로 전달되는 것은 `Data Label.Output` 전체**다.
- `run`, `status`, `error`도 모델 옵션에서 제거한다. 1D에서는 `loocv` 또는 `LOOCV`를 별도 인자로 전달한다.
- 1D는 `MainTrainer`, ND Basic은 `MainTrainerNDBasic`, ND Proto는 `RunTrainerNDProto`로 분기한다.

## DeepOpt가 XML을 읽는 방법

1D와 ND Proto는 `XMLTrainingDataBuilder.load_data_from_xml()`, ND Basic은 `dataset/utils.py`의 로더를 쓴다. 둘 다 `lxml`의 `XMLParser(huge_tree=True, recover=True)`로 파일을 분석하고 `tree.getroot()[0]`, 즉 **root의 첫 번째 자식**만 Python 사전으로 변환한다. [1D와 Proto 로더][deep-xml], [Basic 로더][deep-xml-utils]

```text
raw
  "0"
    Thickness     tensor [1]
    Force         tensor [1]
    node_location tensor [N,3]
    connectivity  tensor [E,K]
    Stress        tensor [N,1]
  "1"
    ...
```

표준 XML의 두 번째 자식인 `model_info`는 학습 데이터 사전에 포함되지 않는다. XML의 `parameter.meta.min/max`를 이 로더를 통해 정규화에 사용하는 것은 아니다. GUI의 메타데이터 복사와 DeepOpt가 실데이터에서 스케일을 계산하는 과정은 별개다.

DeepOpt는 파일 전체의 XML 트리와 tensor를 만든다. GUI의 메타데이터 부분 탐색과 달리 메모리 사용이 데이터 크기에 비례하며 XML 트리, Base64 문자열, NumPy 배열, Torch tensor가 중첩될 수 있다. `recover=True`는 엄격한 XML 검증을 뜻하지 않는다.

## 1D 학습 처리

### 입력 X와 정답 y 구성

`MainTrainer.run()`은 `XMLTrainingDataBuilder.prepare()`를 호출하고 결과를 `.numpy()`로 바꿔 모델별 `train(inputs, outputs, response_labels, run_loocv)`에 전달한다. 이 호출에서는 builder의 feature scaler와 중간 파일 저장을 사용하지 않는다. [1D MainTrainer][deep-1d]

`build_1d()`의 규칙은 다음과 같다. [배열 구성][deep-xml]

| 항목 | 실제 처리 |
|---|---|
| 샘플 순서 | `raw.items()` 순서, 즉 XML 출현 순서. 숫자 키로 다시 정렬하지 않음 |
| 입력 순서 | 읽어 들인 Input 사전의 키 순서 |
| 입력 결합 | tensor를 `torch.cat(..., dim=0)`. 0차원 값은 1축으로 바꾸지만 임의의 고차원 배열을 flatten하지 않음 |
| 형상 입력 | `node_location`, `connectivity` 제외 |
| 입력 reduction | 설정을 읽지 않음 |
| 출력 순서 | Output 사전의 키 순서 |
| 출력 reduction | `Max`, `Min`, `Average`, `SUM`을 dim=0에 적용. 그 외에는 원 tensor 유지 |
| 샘플 결합 | `torch.stack(..., dim=0)`으로 X, y 구성 |

스칼라 설계변수 2개로 노드별 응력의 최댓값을 예측하는 예시는 다음과 같다.

```text
sample 0: Thickness=[2], Force=[100], Stress=[[10],[20],[15]]
sample 1: Thickness=[3], Force=[120], Stress=[[12],[18],[16]]

X = [[2,100], [3,120]]  shape=[2,2]
y = [[20],   [18]]     shape=[2,1]
```

스칼라 입력 P개, 스칼라 출력 Q개이면 `X=[S,P]`, `y=[S,Q]`가 된다. 단, 응답이 `[N,C]`라면 dim=0 축약 후에도 C개 성분이 남는다. MLP는 응답 라벨별로 `outputs[:, i:i+1]`를 선택하므로, 한 라벨이 여러 열을 만드는 경우까지 올바르게 대응한다고 일반화할 수 없다.

누락 키는 건너뛸 뿐 스키마를 보완하지 않는다. 빈 입력의 cat 또는 다른 shape의 stack에서 실패할 수 있다. 여기서 1D는 입력 변수 개수가 하나라는 뜻이 아니다.

### MLP의 정규화와 학습

MLP는 `ANNTrainer`다. 다음 분할 방법을 RF나 RBF 등 다른 trainer에 일반화해서는 안 된다. [MLP trainer][deep-ann]

1. 응답 라벨마다 X와 출력 한 열을 float32로 만든다.
2. X와 y에 각각 MinMaxScaler를 fit한다. **분할 전 전체 샘플로 fit**하며 XML meta는 읽지 않는다.
3. Optuna로 학습률, 층 수, 노드 수, batch size, dropout 등을 탐색한다. GUI 옵션은 trainer 기본값과 병합된다.
4. `loocv=false`이면 XML 출현 순서의 앞 90%로 학습하고 뒤 10%로 평가한다. 탐색용 검증도 같은 90:10 구간이다. 분할은 섞지 않지만 학습 DataLoader는 shuffle한다.
5. `loocv=true`이면 탐색 시 앞 85%와 뒤 15%를 사용하고, 최종 모델은 전체 데이터로 학습하며 별도로 Leave-One-Out 평가를 한다.
6. 최적 파라미터로 `best_model_epoch`만큼 Adam과 MSELoss를 사용해 학습한다. 출력 scaler로 예측을 역변환하여 평가한다.

GUI의 `Output.transformation`은 1D trainer에 전달되지 않는다. 확인한 경로에는 해당 설정을 적용하는 코드가 없다.

## ND 학습 처리

### 모델별 경로

| 모델 | trainer와 전처리 | 데이터 형태 |
|---|---|---|
| MeshBasedNet | ND Basic, MetaStandaloneDataset, ConnToEdgeIndex | 샘플 사전. connectivity에서 edge_index 생성 |
| PointBasedNet, PointVoxelNet | ND Basic, MetaStandaloneDataset | 좌표, 설계변수, 응답을 가진 샘플 사전 |
| StableNet | ND Proto, GeomDeepONetPreprocessor | 설계변수, 추출한 점 좌표, 대응 응답 |
| SprintNet | ND Proto, 전용 strategy | Mixer용 전처리와 dataset 구성 |

이는 DeepOpt의 dispatch 목록이다. GUI가 현재 모든 모델을 선택지로 제공하는 것은 아니며 `getModelsForDimension(3)`은 StableNet을 반환한다. [CLI][deep-main], [ND Basic][deep-basic], [ND Proto][deep-proto], [GUI 모델 목록][gui-builder]

### StableNet의 전처리

StableNet은 Input과 Output의 키를 GeomDeepONetPreprocessor에 전달한다. [strategy][deep-strategy], [dataset 구성][deep-common], [점 추출 전처리][deep-deeponet]

1. 설계변수 후보에서 `node_location`, `connectivity`를 제외한다. 나머지 입력은 키 순서대로 flatten 후 연결한다.
2. 기본적으로 샘플을 숫자 키 순서로 정렬한다. 1D의 XML 출현 순서와 다르다.
3. 샘플당 `num_points=M`개 점을 뽑는다. 점이 충분하면 기본적으로 중복 없이 뽑고, 부족하면 기본적으로 중복 추출한다.
4. 좌표와 응답을 같은 점 인덱스로 추출한다. 응답의 첫 축이 원래 노드 수와 다르면 예외다.
5. 전체 샘플의 추출 좌표에서 축별 min/max를 구해 0~1로 정규화한다.
6. 설계변수를 feature별 min/max로 정규화하고 응답에 signed-log1p 변환을 적용한다. train/test 분할보다 먼저 수행한다.

```text
processed_input["parameters"]  [S,P]
processed_input["positions"]   [S,M,3]
processed_output["values"]     [S,M,C]
```

`append_sdf=true`이면 좌표 특징에 SDF가 추가된다. `values`는 지정한 응답들의 성분을 연결한 tensor다. 이 결과를 샘플마다 `design_variable`, `node_location`, `<target_key>`에 나눠 담는다. 원 좌표, connectivity, 응답도 결과를 원 메쉬로 복원하기 위해 보존한다. num_points를 지정하면 원 노드 수가 달라도 M개로 맞출 수 있다.

응답 변환은 `sign(y) * log(1 + abs(y)) / 10^n`이다. n은 전체 응답의 로그 절댓값 99퍼센타일을 기준으로 구한다. 이는 DeepOpt 내부 처리이며 GUI의 `transformation="Log"`를 읽어 실행하는 것이 아니다. 역변환에 필요한 상태도 저장한다. [응답 정규화][deep-target]

Proto는 dataset을 무작위 90:10으로 나누고 **같은 10%를 validation과 test에 사용**한다. Lightning으로 학습하고 val_loss 기준 best checkpoint로 평가한다. [학습 루프][deep-proto]

복수 Output에는 추가 제약이 있다. Proto의 바깥 루프는 target별로 돌지만 StableNet 전처리에는 매번 Output 전체가 전달된다. 전처리된 전체 `values`를 현재 target 이름 아래에 넣으므로, 각 Output을 완전히 독립된 단일 응답으로 학습한다고 설명할 수 없다. 단일 Output의 정상 흐름과 구분해야 한다.

### ND Basic의 차이

Basic은 별도 XML 로더에서 MetaStandaloneDataset을 만든다. Input 키에는 FeatureWiseNorm, target에는 별도 signed-log1p 변환을 적용한다. 전체의 90%를 학습 후보, 10%를 test로 나누고, 학습 후보를 다시 90:10으로 나눠 train과 validation을 만든다. 반올림을 제외하면 약 81:9:10이다. [ND Basic][deep-basic], [Dataset][deep-dataset]

Input에 형상 키가 포함되면 정규화 strategy 사전을 합치는 과정에서 형상의 NoNorm이 Input 쪽 FeatureWiseNorm으로 덮일 수 있다. GUI 입력 표와 trainer의 global feature 처리 규칙을 함께 확인해야 한다.

## 학습 결과 저장

### 모델과 부가 파일

`.pt` 확장자라도 모델 종류에 따라 내부 형식이 다르다.

| 계열 | 파일 | 내용 |
|---|---|---|
| BaseTrainer의 pickle 저장을 사용하는 1D 모델 | `<response>/<model>_<error>.pt` | `pickle.dump([model] + list(model_data))` |
| MLP | `<response>/MLP_<error>/model.pt` | PyTorch state_dict |
| MLP 부가 파일 | `input_scaler.pkl`, `output_scaler.pkl`, `model_info.txt` | joblib scaler, 네트워크 구성과 학습 조건 |
| ND | `<response>/<model>_<error>/model.pt`, 원래 `.ckpt` | best Lightning checkpoint의 복사본 |
| ND 부가 파일 | `config.yaml`, `rendered_results/` 등 | 모델 구성, 정규화 상태, 평가, 비교용 VTU |

근거: [1D 공통 저장][deep-base-trainer], [MLP 저장][deep-ann], [ND 저장][deep-saver].

StableNet의 config.yaml에는 모델 설정, target, 평가 외에도 좌표 min/max, `parameter_keys`, 설계변수 min/max, 응답 변환 n과 q가 기록된다. 추론 시 동일한 입력 순서와 정규화, 역변환을 재현하기 위한 정보다. ND의 모델 복사는 best checkpoint가 있을 때 수행하므로 설정 파일의 존재만으로 모델 본체 저장까지 성공했다고 판단하지 않는다.

```text
ModelBuilder_Set1/
├── model_info.json
├── training_log.txt                 # Proto 실행 로그
└── Stress/
    ├── MLP_<error>/
    │   ├── model.pt
    │   ├── input_scaler.pkl
    │   ├── output_scaler.pkl
    │   └── model_info.txt
    └── StableNet_<error>/
        ├── model.pt
        ├── <best checkpoint>.ckpt
        ├── config.yaml
        └── rendered_results/
            └── *.vtu
```

계열별 예시를 함께 표시한 것으로, 매번 이 파일이 전부 생성된다는 뜻은 아니다. GUI는 VTU의 `Exact_*`, `Prediction_*` point data를 찾아 비교 표시한다. [GUI 비교 표시][gui-preview]

### 평가 지표와 상태

결과 폴더의 model_info.json에는 GUI가 기록한 메타데이터와 DeepOpt가 기록한 errors가 공존한다.

```text
model_info.json
  parameter
    <변수>: {source, meta}
  selected_response
    {component, load_step, name, file_name}
  errors
    <응답명>
      <모델명>: {R2, MAPE [%] 또는 CVE [%], ...}
```

1D는 R2와 MAPE 또는 CVE, ND는 `R2`, `Mean-MAPE[%]`, `Peak-MAPE[%]`, `Top5% WMAPE[%]`, `WMAPE [%]`를 쓴다. ND ResultSaver는 마지막 두 항목에 같은 Weighted-MAPE 값을 기록한다. 1D의 사전 형식 결과 저장은 해당 응답의 errors를 비운 뒤 기록하므로, 여러 모델을 순서대로 학습할 때 이전 지표가 계속 보존된다고 가정할 수 없다. [1D 결과 저장][deep-1d], [ND 결과 저장][deep-saver]

GUI는 1초마다 입력 설정 JSON의 `Configuration.<모델>.status`를 읽고 Done 상태에서 지표를 갱신한다. stdout과 stderr는 로그 및 오류 표시에 사용하며 모델을 전달하는 채널이 아니다. [GUI 상태 확인][gui-builder]

## 구현 차이와 검증 범위

| 항목 | 확인된 동작 | 영향 |
|---|---|---|
| 모델 response | CLI에서 제거하고 Output 전체 전달 | GUI 모델 행의 응답 선택만으로 대상이 제한되지 않음 |
| Sum | GUI는 `Sum`, 1D 파서는 `SUM` 검사 | 선택한 Sum이 축약되지 않고 원 tensor가 전달됨 |
| 출력 transformation | 확인한 학습 경로에서 해당 JSON 필드를 적용하지 않음 | GUI에서 선택한 Log 등의 적용을 보장하지 않음 |
| 입력 reduction | 1D build_1d에서 읽지 않음 | 설정만으로 입력 필드를 스칼라화하지 못함 |
| model_info 위치 | DeepOpt는 root의 첫 자식만 읽음 | 메타데이터를 처음으로 옮기면 GUI가 읽어도 DeepOpt와 호환되지 않을 수 있음 |
| 샘플 순서 | MLP는 XML 순서, StableNet은 기본 숫자 키 순서 | 동일한 평가 샘플을 사용한다고 가정할 수 없음 |
| 정규화 fit | MLP와 확인한 ND 경로는 분할 전 수행 | 평가 집합에서 독립된 전처리가 아님 |
| 다성분과 복수 응답 | 1D의 라벨과 열 대응, StableNet의 응답 연결에 제약 | 단일 스칼라 출력의 설명을 일반화하지 않음 |

소스를 정적으로 대조했다. 로컬 DeepOpt의 `.venv`에 torch가 없어 XML 파서 실행과 학습은 하지 않았다. 수치 예제는 배열 조작의 설명이며 학습 실측값이 아니다. 배포 EXE와의 버전 일치, 전체 모델의 성능과 정확도는 확인하지 않았다.

## 코드 참조

| 처리 | 파일과 주요 함수 |
|---|---|
| XML 생성 | GUI `model/preprocessor/DashResultXmlWriter.cpp`: `appendSample`, `writeModelInfoToXml` |
| GUI 로딩과 실행 | GUI `model/DashModelBuilder.cpp`: `onLoadButtonClicked`, `saveDataLabelConfig`, `loadModelInfoFromXml`, `onTrainingStartButtonClicked` |
| CLI | DeepOpt `main.py`: `train_model_1d`, `train_model_nd` |
| 배열 구성 | DeepOpt `source/preprocessor/xml_parser.py`: `load_data_from_xml`, `build_1d`, `prepare` |
| 1D 학습 | DeepOpt `source/run_train_1d.py`: `MainTrainer.run` |
| MLP 학습과 저장 | DeepOpt `source/models/oned/ann_trainer.py`: `train`, `_save_model` |
| ND Basic | DeepOpt `source/run_train_nd_basic.py` |
| ND Proto | DeepOpt `source/run_train_nd_proto.py` |
| StableNet 전처리 | DeepOpt `source/preprocessor/deeponet_preprocessor.py`, `source/trainer_utils/proto_strategies/_common.py` |
| ND 저장 | DeepOpt `source/trainer_utils/result_saver.py` |

[gui-launcher]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/5a4e6b96268b6919239eccc0dd416499867b4672/model/DashAnalysisLauncher.cpp#L1750
[gui-writer]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/5a4e6b96268b6919239eccc0dd416499867b4672/model/preprocessor/DashResultXmlWriter.cpp
[gui-utils]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/5a4e6b96268b6919239eccc0dd416499867b4672/model/preprocessor/DashUtils.cpp
[gui-builder]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/5a4e6b96268b6919239eccc0dd416499867b4672/model/DashModelBuilder.cpp
[gui-widget-base]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/5a4e6b96268b6919239eccc0dd416499867b4672/view/DashModelBuilderWidgetBase.cpp#L486
[gui-pm]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/5a4e6b96268b6919239eccc0dd416499867b4672/viewmodel/DashModelBuilderPresentationModel.cpp#L355
[gui-io]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/5a4e6b96268b6919239eccc0dd416499867b4672/controller/DashIOController.cpp
[gui-preview]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/5a4e6b96268b6919239eccc0dd416499867b4672/view/DashModelBuilderWidget.cpp#L1633
[deep-main]: https://github.com/NohLabWorks/DashOpti_DeepOpt/blob/a4222b69cf3ec64864c99ae3fbd4aa4dddb77f4c/main.py
[deep-xml]: https://github.com/NohLabWorks/DashOpti_DeepOpt/blob/a4222b69cf3ec64864c99ae3fbd4aa4dddb77f4c/source/preprocessor/xml_parser.py
[deep-xml-utils]: https://github.com/NohLabWorks/DashOpti_DeepOpt/blob/a4222b69cf3ec64864c99ae3fbd4aa4dddb77f4c/source/preprocessor/dataset/utils.py
[deep-1d]: https://github.com/NohLabWorks/DashOpti_DeepOpt/blob/a4222b69cf3ec64864c99ae3fbd4aa4dddb77f4c/source/run_train_1d.py
[deep-ann]: https://github.com/NohLabWorks/DashOpti_DeepOpt/blob/a4222b69cf3ec64864c99ae3fbd4aa4dddb77f4c/source/models/oned/ann_trainer.py
[deep-base-trainer]: https://github.com/NohLabWorks/DashOpti_DeepOpt/blob/a4222b69cf3ec64864c99ae3fbd4aa4dddb77f4c/source/models/oned/base_trainer.py
[deep-basic]: https://github.com/NohLabWorks/DashOpti_DeepOpt/blob/a4222b69cf3ec64864c99ae3fbd4aa4dddb77f4c/source/run_train_nd_basic.py
[deep-proto]: https://github.com/NohLabWorks/DashOpti_DeepOpt/blob/a4222b69cf3ec64864c99ae3fbd4aa4dddb77f4c/source/run_train_nd_proto.py
[deep-strategy]: https://github.com/NohLabWorks/DashOpti_DeepOpt/blob/a4222b69cf3ec64864c99ae3fbd4aa4dddb77f4c/source/trainer_utils/proto_strategies/stablenet.py
[deep-common]: https://github.com/NohLabWorks/DashOpti_DeepOpt/blob/a4222b69cf3ec64864c99ae3fbd4aa4dddb77f4c/source/trainer_utils/proto_strategies/_common.py
[deep-deeponet]: https://github.com/NohLabWorks/DashOpti_DeepOpt/blob/a4222b69cf3ec64864c99ae3fbd4aa4dddb77f4c/source/preprocessor/deeponet_preprocessor.py
[deep-target]: https://github.com/NohLabWorks/DashOpti_DeepOpt/blob/a4222b69cf3ec64864c99ae3fbd4aa4dddb77f4c/source/trainer_utils/target_normalizer.py
[deep-dataset]: https://github.com/NohLabWorks/DashOpti_DeepOpt/blob/a4222b69cf3ec64864c99ae3fbd4aa4dddb77f4c/source/preprocessor/dataset/dataset.py
[deep-saver]: https://github.com/NohLabWorks/DashOpti_DeepOpt/blob/a4222b69cf3ec64864c99ae3fbd4aa4dddb77f4c/source/trainer_utils/result_saver.py
