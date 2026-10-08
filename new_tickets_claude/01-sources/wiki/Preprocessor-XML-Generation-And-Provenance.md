# Preprocessor의 XML 생성 절차와 구성요소별 출처

Preprocessor 화면에서 생성하는 학습용 XML은 DOE 표의 설계변수, 해석 결과의 형상과 응답, DV 설정의 메타데이터를 합친 데이터셋이다. XML을 직접 조립하는 주체는 GUI의 `DashResultXmlWriter`다. Preprocessor 라이브러리는 결과 파일에서 데이터를 읽어 카탈로그와 VTK grid를 제공한다.

2026-10-02 GUI 커밋 `f71b8e82510cabf9b882163388637f47eaa5bdef`의 소스를 정적으로 검토했다. 링크는 해당 커밋에 고정했다. 일반 DOE 배치 경로를 중심으로 설명하고 단일 파일, 모달, Function Expression, KPI는 별도로 구분한다. 실제 결과 파일을 이용한 실행 검증과 solver 플러그인 내부의 보간·외삽 알고리즘 검증은 수행하지 않았다.

생성된 XML을 ModelBuilder와 DeepOpt가 소비하는 과정은 [Model Builder XML 구성과 DeepOpt 학습 입출력](Model-Builder-XML-DeepOpt-Pipeline.md)을 참고한다. 두 문서는 서로 다른 기준 커밋을 명시한 조사 기록이다.

## 생성에 참여하는 데이터

```text
DoeSampler_<Set>.json
  DOE Table.headers, samples
    → AnalysisLauncher_<Set>.json의 DOE 스냅샷
      → XML 샘플의 설계변수 이름과 값

각 run의 해석 결과 파일
  → Preprocessor 카탈로그와 VTK grid
    → XML의 좌표, connectivity, 응답 값

사용자의 Output Response 선택
  → component, loadStep, name
    → 결과 조회 조건, XML 파일명, selected_response

원본 DoeSampler_<Set>.json + Geometry/Condition 설정
  → 열별 출처와 meta 병합
    → model_info.parameter
```

여기서 **샘플의 실제 값과 메타데이터는 서로 다른 경로로 읽힌다.** 전자는 AnalysisLauncher의 스냅샷, 후자는 원본 DoeSampler와 DV 설정을 사용한다.

## XML 생산 절차

### DOE와 결과 파일 목록 준비

해석 폴더를 선택하면 `DashDatasetScanner`가 run 폴더의 파일을 탐색해 `m_dataset`을 채운다. 이어서 `AnalysisLauncher_<Set>.json`에 다음 DOE 스냅샷을 저장한다. [스캔과 스냅샷 저장][launcher]

| 스냅샷 항목 | 만들어지는 방식 |
|---|---|
| `DOE Table.samples` | 로드한 DOE 표의 samples를 복사 |
| `DOE Table.headers` | 로드한 DOE 표의 headers를 복사 |
| `DOE Table.output[analysisType]` | 탐색한 dataset에서 run 디렉터리 이름을 중복 없이 수집 |

DOE 샘플이 없으면 파일 목록의 run마다 `{key: runs번호, values: []}` 형태를 합성한다. 이 합성 과정은 파일에서 설계변수 값을 역추출하지 않는다. 원본 headers도 없으면 변수명은 빈 배열이다.

### Preprocessor Load와 사용자 선택

Load는 선택한 파일 그룹을 리더에 등록하고 다음 카탈로그를 읽는다. [Load 구현][launcher]

- `GetTimeSteps()`는 step, substep, mode, state 등의 선택지를 제공한다.
- `GetGeometries()`는 component와 해당 영역을 선택하는 정보를 제공한다.
- `GetAvailableResponses()`는 표시할 응답명과 operator·field 이름 등의 조회 정보를 제공한다.

사용자가 선택한 component, loadStep, name을 Output Response 표에 추가한다. Process 버튼은 표를 읽어 요청 목록을 만들고 일반 처리, KPI, BORE/BOSS 그룹 처리로 분기한다. **화면에서 고른 응답 이름은 실제 숫자 배열이 아니라, 배열을 조회하기 위한 선택 정보다.** [Process 버튼][widget], [요청 구성][presentation]

### 샘플과 결과 파일 매칭

`DashAnalysisLauncher::processResults()`는 AnalysisLauncher 스냅샷에서 samples, headers, output 목록을 읽는다. output 목록이 없거나 비었으면 dataset에서 run 목록을 합성한다. 이어 DOE 상태 필터와 `DashDatasetIndex::build()`를 통해 샘플과 결과를 매칭한다. [배치 진입][launcher], [매핑][index]

주요 매칭 키는 `runs17`의 숫자 17이다. 레거시 결과 목록의 `case017` 또는 `runs17` 패턴도 해석한다. 실제 결과 파일은 다음 위치에서 dataset의 선택 종류와 basename, run을 대조해 정한다.

```text
<프로젝트 루트>/<선택한 DoeSampler 파일의 stem>/<analysisType>/<dataset 상대 경로>
예: <프로젝트>/DoeSampler_Set1/Static/runs17/static.rst
```

Done 필터는 엄격한 성공 전용 필터가 아니다. `keepDoneRuns()`는 일부만 제외될 때는 거른 목록을 반환하지만 **모든 항목이 제외되면 원래 목록을 반환**한다. run 이름으로 해석되지 않는 레거시 항목도 유지한다. 이 동작은 현재 테스트에 명시되어 있다. [필터][batch], [필터 테스트][batch-test]

### 요청별 XML과 샘플 조립

일반 경로는 component·시점·응답으로 이루어진 요청마다 XML 문서를 하나 만든다. 각 문서는 여러 DOE 샘플을 담는다. BORE/BOSS 그룹 및 KPI는 묶음·파일명 규칙이 별도다.

각 샘플은 `DashResultProcessor::processSingleSample()`에서 실제 결과 파일을 열고 `DashResultXmlWriter::appendSample()`으로 전달한다. [샘플 처리][processor]

`appendSample()`의 순서는 다음과 같다. [샘플 writer][writer]

1. 임시 샘플 `dict_item`과 내부 `dict`를 만든다.
2. DOE 변수 이름과 값을 위치 인덱스로 대응시켜 tensor로 쓴다.
3. 필요한 경우 형상 grid에서 좌표와 연결정보를 쓴다.
4. 요청한 응답을 조회하여 tensor로 쓴다.
5. 응답까지 쓴 경우에만 샘플을 문서에 붙인다.

처리 결과는 `Written`, `Missing`, `ReadFailed`로 나뉜다. 일반 DOE 배치는 누락·실패 샘플을 제외하고, **실제로 쓴 샘플 수를 XML 키로 사용**한다. 따라서 첫 run이 누락되어도 첫 성공 샘플의 키는 `"0"`이다. 응답을 하나도 기록하지 못한 요청은 파일을 생성하지 않는다. 라이브러리 읽기 실패가 있으면 배치 종료 시 리더를 폐기한다.

### 메타데이터 추가와 저장

샘플용 dict를 만든 뒤 root의 별도 자식으로 `model_info`를 붙인다. parameter 정보가 비어 있으면 writer는 model_info 전체를 생략한다. 일반 경로는 프로젝트 루트의 `AnalysisLauncher_<Set>/` 아래에 저장한다. 기본 파일명은 다음 형태다. [메타데이터 조립][launcher], [파일명과 저장][batch]

```text
<정규화된 component>_<step>_<substep>_<정규화된 response>.xml
```

`DashResultBatch::saveXml()`은 QDomDocument를 UTF-8, 들여쓰기 2로 저장한다. 현재 파일 열기는 WriteOnly이므로 같은 경로가 있으면 기존 내용을 덮어쓴다.

## XML 구조와 항목별 출처

아래는 생략 표기가 포함된 구조 예시다. tensor 본문의 `…`는 실제 Base64 데이터가 아니므로 그대로 학습 입력으로 사용할 수 없다.

```xml
<root>
  <dict>
    <dict_item key="0">
      <dict>
        <dict_item key="Thickness">
          <tensor dtype="float32" shape="[1]" encoding="base64">…</tensor>
        </dict_item>
        <dict_item key="node_location">
          <tensor dtype="float32" shape="[100, 3]" encoding="base64">…</tensor>
        </dict_item>
        <dict_item key="connectivity">
          <tensor dtype="int32" shape="[50, 8]" encoding="base64">…</tensor>
        </dict_item>
        <dict_item key="Stress">
          <tensor dtype="float32" shape="[100, 1]" encoding="base64">…</tensor>
        </dict_item>
      </dict>
    </dict_item>
  </dict>
  <dict_item key="model_info">
    <dict>
      <dict_item key="parameter"><dict>…</dict></dict_item>
      <dict_item key="selected_response"><dict>…</dict></dict_item>
    </dict>
  </dict_item>
</root>
```

| XML 항목 | 읽는 원천 | 변환 또는 주의점 |
|---|---|---|
| 샘플 키 `0`, `1`, … | 성공적으로 기록한 샘플 수 | 원래 run 번호가 아니라 재부여한 번호 |
| 설계변수 이름 | AnalysisLauncher 스냅샷의 `headers[i]` | `sanitizeString()`으로 키 정규화 |
| 설계변수 값 | 스냅샷의 `samples[j].values[i]` | double로 읽은 뒤 float32, `[1]`로 저장. 레거시 `{runs번호: [...]}`도 지원 |
| `node_location` | 형상 또는 응답 VTK grid의 `GetPoints()` | XYZ를 float32, `[N,3]`로 저장 |
| `connectivity` | 형상 또는 응답 grid의 `GetCells()` | VTK point index를 int32로 저장. 폭은 최대 연결 수와 8 중 큰 값, 빈 칸은 `-1` |
| 일반 응답 키 | 요청의 `name`, 없으면 `result` | 이름을 정규화해 XML 키로 사용 |
| 일반 응답 값 | `GetFieldOutputVtk()` 반환 grid의 PointData | 선택한 배열의 모든 tuple·성분을 float32로 저장 |
| 일반 응답 shape | grid의 point 수와 배열의 성분 수 | `[N,C]`. 스칼라 필드도 `[N,1]` |
| dtype와 encoding | XML writer | float32 또는 int32, base64를 코드에서 지정 |
| parameter의 변수 이름 | 원본 DoeSampler의 `DOE Table.headers` | 샘플 값에 사용하는 스냅샷과 별도 읽기 |
| parameter의 source | DOE 열의 module·Set·변수 출처와 Set ID 매핑 | 해당 Geometry/Condition 설정 파일명 |
| parameter의 meta | DV 정의의 meta + 원본 DOE Table의 min/max/mean/std | 다음 절의 우선순위로 병합 |
| selected_response.component | 사용자 요청의 component | 표시 이름을 문자열로 저장 |
| selected_response.load_step | 요청의 loadStep | 없으면 step/substep으로 문자열 생성 |
| selected_response.name | 요청의 응답 이름 | 문자열로 저장 |
| selected_response.file_name | 처음 정상적으로 연 결과 파일의 basename | 없으면 선택 dataset의 첫 파일명. 샘플별 출처 목록이 아님 |

근거: [샘플 값과 tensor 기록][writer], [메타데이터 원천][doe], [selected_response 구성][launcher].

### 설계변수 이름과 값의 대응

변수의 이름과 값은 파일명이나 solver 결과에서 알아내는 것이 아니라 `headers[i]`와 `values[i]`를 위치로 결합한다. 값 배열이 짧으면 해당 변수는 기록하지 않는다. writer는 각 값을 double로 읽고 float로 변환한다.

공백과 일부 특수문자를 `_`로 바꾸므로 서로 다른 원래 이름이 같은 XML 키가 될 가능성이 있다. writer 단계에서 이러한 이름 충돌을 별도로 검증하지 않는다. [변수 기록][writer], [이름 정규화와 Base64][utils]

### 형상의 실제 출처

좌표와 connectivity는 GUI의 CAD 원본이나 미리보기 장면에서 복사하지 않는다. 해당 run의 해석 결과를 리더가 VTK grid로 변환한 결과에서 가져온다.

- 일반 경로는 `GetGeometryVtk()`의 좌표와 연결정보를 먼저 쓴다.
- `.odb`는 `preferFieldNodeLocation=true`로 전달해 필드 grid의 좌표와 연결정보를 사용하도록 한다. 이름과 달리 좌표와 connectivity 모두에 적용한다.
- 응답 grid를 읽었을 때 아직 기록되지 않은 형상 항목은 `writeTopologyFromFieldGrid()`에서 채운다.
- Natural Frequency 같은 모달 스칼라 응답은 일반 형상 기록을 생략한다. Mode Shape는 형상 기록 대상이다.

connectivity에 저장하는 값은 solver의 원래 노드 라벨이 아니라 **VTK grid 내부의 point index**다. writer는 cell type이나 원래 노드·요소 ID를 별도 XML 항목으로 기록하지 않는다. [형상 기록과 분기][writer], [ODB 플래그 전달][processor]

### 응답 질의와 배열 선택

component 이름은 geometry 카탈로그의 location과 named_selection 등으로 바뀐다. 응답 이름은 응답 카탈로그의 operator에 대응한다. 선택 시점과 함께 wrapper에 전달하면 wrapper가 현재 파일의 시간·영역·응답 selector를 찾아 Preprocessor를 호출한다. [질의 조립][writer], [wrapper][wrapper]

```text
현재 run의 결과 파일
+ 선택한 시점
+ 선택한 component의 domain
+ 선택한 응답의 selector
→ GetFieldOutputVtk()
→ 응답을 포함한 VTK grid
```

일반 필드 경로는 카탈로그의 `field_output_name`, 레거시 `result`로 배열 이름을 정하고, 해당 배열이 없으면 operator 이름으로 찾는다. 노드·요소 ID 보조 배열은 제거한다. `GetGeometries()`와 `GetAvailableResponses()`의 JSON은 조회용 카탈로그이며, XML의 수치 데이터 자체는 VTK에서 읽는다.

## parameter 메타데이터의 생성

`loadParameterInfo()`는 선택한 원본 DoeSampler JSON과 프로젝트 configs 폴더를 `DashDoeTableFile::readParameterInfo()`에 전달한다. 샘플 값용 AnalysisLauncher 스냅샷을 읽는 함수가 아니다. [호출부][launcher], [메타데이터 조립][doe]

1. 원본 `DOE Table.headers` 순서로 변수를 순회한다.
2. `DOE Table.columns`에서 module, Set, 변수 key를 얻는다. columns가 없는 레거시 데이터는 Selected Design Variables 등에서 출처를 추정한다.
3. Set ID와 현재 파일명 매핑으로 Geometry/Condition 설정 파일을 찾는다.
4. 그 파일의 `DV-Geometry` 또는 `DV-Condition`에서 해당 key를 찾는다.
5. 항목의 boolean이 참이고 meta가 있으면 meta를 복사한다.
6. 원본 DOE Table의 같은 인덱스에 min/max/mean/std 값이 있으면 덮어쓴다.

min/max는 숫자인 경우, mean/std는 숫자 또는 문자열인 경우 복사한다. XML writer는 내부 parameterInfo의 `value`에 담긴 파일명을 `source`로 기록하고, meta 숫자는 float 태그, 문자열은 string 태그로 쓴다. [열의 출처 해석][selection], [XML 메타데이터 기록][writer]

**이 단계에서 XML에 남은 샘플들의 통계를 다시 계산하지 않는다.** 누락된 run이 많아도 meta의 min/max/mean/std는 DOE 설정에서 가져온 값이다. 따라서 최종 XML 표본의 경험적 최소·최대·평균·표준편차라고 설명하면 안 된다.

parameter 정보가 없으면 model_info 전체가 생략되므로, 응답을 추출했더라도 selected_response가 없는 XML이 나올 수 있다. `writeModelInfoToXml()`의 인자인 currentAnalysisType도 현재 그 함수에서 별도 태그로 기록하지 않는다.

## 일반 필드와 다른 경로

| 경로 | 데이터 출처와 XML 기록 |
|---|---|
| 단일 파일 모드 | DOE 경로가 없으면 빈 설계변수 배열로 샘플 0 하나를 만든다. parameter 정보도 읽지 않으므로 model_info가 생략될 수 있음 |
| Natural Frequency | 현재 샘플의 `GetTimeSteps()`에서 선택 모드의 주파수를 읽어 float32 `[1]`로 기록 |
| Mode Shape | 모달 변위 grid에서 X/Y/Z 또는 벡터 크기를 구해 `[N,1]`로 기록 |
| Function Expression | 카탈로그의 식 이름·column을 사용해 조회한 배열의 마지막 tuple 첫 성분을 `[1]`로 기록 |
| Circularity와 기타 KPI | 별도 계산 규칙으로 만든 파생값. 일반 필드의 단순 복사가 아님 |

KPI 구현에는 모달 주파수 통계, 최대 Side Force, Critical Buckling Load, Max PEEQ, 최소 Fatigue Life 등이 있다. KPI별 파일 생성과 샘플 취급은 별도 함수에 있으므로 일반 `appendSample()` 경로의 모든 규칙을 그대로 적용한다고 가정하지 않는다. [특수 응답][writer], [KPI 함수들][kpi]

## 검토에서 확인한 제약

| 항목 | 확인한 코드 동작 | 해석 또는 영향 |
|---|---|---|
| 데이터 시점 | 샘플 값은 AnalysisLauncher 스냅샷, meta는 원본 DoeSampler와 DV 파일에서 읽음 | 스냅샷 이후 원본을 바꾸면 서로 다른 기준이 합쳐질 수 있음. 발생 여부는 프로젝트별 확인 필요 |
| run 추적 | 성공 샘플에 새 번호 부여, 샘플별 run과 파일 경로를 XML에 쓰지 않음 | XML 번호만으로 원래 run을 복원할 수 없음 |
| 대표 file_name | 필드 추출 성공 이전에 첫 정상 개방 파일명을 기억 | 첫 XML 샘플의 파일명과 항상 같지는 않음 |
| 성공 상태 필터 | 모두 제외되면 원래 목록 반환 | Done 상태만 포함된 XML이라고 단정할 수 없음 |
| 형상과 필드 정합성 | 일반 경로는 geometry grid와 field grid를 함께 사용, 노드 ID 순서 대조 없음 | 두 grid의 정렬·구성 일치를 전제로 함. 실제 불일치는 별도 데이터 재현이 필요 |
| 응답 길이 | 바이트는 numTuples 기준, shape는 numPoints 기준으로 기록 | 두 수가 다른 grid이면 저장한 shape와 데이터 길이가 어긋날 수 있음 |
| 설계변수 누락 | headers보다 values가 짧으면 항목 생략 | 샘플마다 같은 라벨 집합이라는 보장이 writer에 없음 |
| 통계 정보 | 원본 설정에서 복사하고 성공 샘플로 재계산하지 않음 | meta를 최종 표본 통계로 해석하면 안 됨 |

## 코드 탐색 순서

| 관심 지점 | 주요 함수 |
|---|---|
| 화면에서 요청 생성 | `DashAnalysisLauncherWidget::onProcessButtonClicked`, `buildProcessPlan` |
| 배치 전체 | `DashAnalysisLauncher::processResults` |
| 샘플과 run 연결 | `DashDatasetIndex::build` |
| 파일별 읽기와 성공 샘플 번호 | `DashResultProcessor::processSamples`, `processSingleSample` |
| XML 조립 | `DashResultXmlWriter::appendSample`, `writeParametersToXml`, `writeGeometryToXml`, `writeFieldOutputToXml` |
| 메타데이터 원천 | `DashDoeTableFile::readParameterInfo`, `DashDoeSelection::readColumns` |
| 메타데이터 직렬화 | `writeParameterSectionToXml`, `writeModelInfoToXml` |
| 실제 파일 저장 | `DashResultBatch::outputFileName`, `saveXml` |

[launcher]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/f71b8e82510cabf9b882163388637f47eaa5bdef/model/DashAnalysisLauncher.cpp
[widget]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/f71b8e82510cabf9b882163388637f47eaa5bdef/view/DashAnalysisLauncherWidget.cpp
[presentation]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/f71b8e82510cabf9b882163388637f47eaa5bdef/viewmodel/DashAnalysisLauncherPresentationModel.cpp
[index]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/f71b8e82510cabf9b882163388637f47eaa5bdef/model/preprocessor/DashDatasetIndex.cpp
[processor]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/f71b8e82510cabf9b882163388637f47eaa5bdef/model/preprocessor/DashResultProcessor.cpp
[writer]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/f71b8e82510cabf9b882163388637f47eaa5bdef/model/preprocessor/DashResultXmlWriter.cpp
[batch]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/f71b8e82510cabf9b882163388637f47eaa5bdef/model/preprocessor/DashResultBatch.cpp
[batch-test]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/f71b8e82510cabf9b882163388637f47eaa5bdef/tests/TestResultBatch.cpp
[doe]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/f71b8e82510cabf9b882163388637f47eaa5bdef/model/preprocessor/DashDoeTableFile.cpp
[selection]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/f71b8e82510cabf9b882163388637f47eaa5bdef/model/DashDoeSelection.cpp
[wrapper]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/f71b8e82510cabf9b882163388637f47eaa5bdef/model/preprocessor/wrapper/LegacyJsonPreprocessor.cpp
[utils]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/f71b8e82510cabf9b882163388637f47eaa5bdef/model/preprocessor/DashUtils.cpp
[kpi]: https://github.com/NumeRealWorks/DashOpti_GUI/blob/f71b8e82510cabf9b882163388637f47eaa5bdef/model/DashAnalysisLauncherKPI.cpp
