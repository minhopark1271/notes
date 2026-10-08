# 엔티티 모델 개편 3안 — 저장 구조 설계 · 초안

> ## ⚠ 문서 상태: 분석 · 아이디에이션 — **확정 아님**
>
> | | |
> |---|---|
> | 단계 | 문제 분석 + 발산적 아이디에이션. **설계 확정 전, 팀 합의 전, 착수 승인 전** |
> | 확정된 것 | **없음.** 1\~4절의 현황 진단만 코드 근거를 가지며, 5절 이후는 전부 검토 대상 |
> | 이 문서로 하면 안 되는 것 | 구현 착수 · 일정 산정 · 티켓 생성 · 외부 커밋. 엔티티 이름/ID 규칙/파일 레이아웃 어느 것도 계약이 아님 |
> | 확정되려면 | 11절 열린 질문 6건 해소 → 팀 리뷰 → 별도 **계약 문서**(9.2절 0단계) 작성. 그 계약 문서가 나오기 전까지 본 문서는 인용 근거가 아니라 논의 재료임 |
> | 대안 취급 | 5절의 A/B/C 3안은 **비교를 위해 나열한 것**이며 C안 "추천"은 작성자 1인의 잠정 의견이다. 3안 밖의 4번째 안이 나올 여지를 닫지 않았음 |
>
> 기반 문서: [[Project-Store-Survey-Key-IO-Ledger]] · [[Project-Store-Survey-Inputs-Payloads-Runtime]] (현황 조사 — 그쪽은 사실, 이쪽은 의견)
> 제약 1건: `ModelBuilder_{Set}.json` 은 외부 도구(DeepOpt·MCU)가 `status` 를 **되쓰는 양방향 IPC 채널**이라, C안 6.2 의 "Definition 파일 = 정의만" 이 그 2개 모듈에서 성립하지 않는다 (9.2 2단계 참조). 도구 개정 권한은 확인됐으므로 차단이 아니라 **순서 제약**이다 (근거는 대장 3.3)
> 후속 문서 2: [[Project-Store-Design-Layer-Cut]] — 본 문서의 C안을 **사용자 모듈 단위**로 다시 세운 설계. 물리 배치를 `configs/` 평면 대신 "모듈 인스턴스 = 자기완결 디렉토리" 로 잡고, 6.3 Run 인덱스를 `executions/{label}/execution.json` 으로 두며, 열린 질문 5(Model 을 복사본 기준으로 볼지 원본 참조로 볼지)에 **복사본이 정본 + 원본은 출처 기록 + 지문 불일치는 `⚠ Stale` 표시**로 답한다. 본 문서 3.4 의 엔티티 `Model` 은 그쪽에서 **`Reference`(`ref_*`)로 개명**됐다 — 어휘 실측 수치는 [[Project-Store-Design-Rationale]] 4절. 확정 아님
> 작성: 2026-08-09, 코드 근거는 `refactor/async-execution` `b97e23a` 기준

## 배경

선행 조사는 프로젝트가 `(카테고리, Set 이름)` 2튜플 하나로만 구성되고, 해석 모델·샘플 셋·계보가 1급 개체가 아니라는 것을 확인했다. 본 문서는 그 조사에서 도출되는 재설계안을 제시한다.

핵심 진단 두 줄:

> **Set은 노드인데 엣지가 없다.**
> **정의(definition)와 산출(production)이 한 Set에 눌려 있어 실행이 정의를 덮어쓴다.**

---

## 1. 현재 구조의 두 가지 결손

### 1.1 엣지 부재

노드(Set)는 잘 정의돼 있는데 노드를 잇는 엣지가 데이터 모델에 없다. 엣지는 세 형태로 흩어져 있다.

| 형태 | 예 | 문제 |
|---|---|---|
| 문자열 파싱 | `"Morphing\|part1.dat\|PART-1"` → `split("\|")` 로 실행 폴더명 생성 | 이름 바뀌면 끊김 |
| 관례 추정 | `Optimizer_Set1` → `ModelBuilder_Set1` | Set 번호는 카테고리별 독립 발급이라 보장 없음 |
| 기록 없음 | ModelRunner → `folders[0]` | 사실상 엣지 부재 |

### 1.2 정의/산출 미분리

모든 산출 단계가 고정 경로에 덮어쓴다.

| 단계 | 성격 | 재실행 시 | 적절한가 |
|---|---|---|---|
| Geometry / Condition Param | **정의** | 덮어쓰기 | O — 정의는 최신 하나면 충분 |
| DataPreprocessor 라벨 설정 | **정의** | 덮어쓰기 | O |
| ModelBuilder 하이퍼파라미터 | **정의** | 덮어쓰기 | O |
| **Analysis Launcher 실행** | **산출** | `DOE Table` 통째 교체, `runs1..N` 키 재발급 | **X** |
| **ModelBuilder 학습** | **산출** | `ModelBuilder_{Set}/model_info.json` 고정 경로 | **X** |
| **Optimizer 실행** | **산출** | `Optimizer_{Set}/optimum.json` 고정 경로 | **X** |

**정의는 덮어써도 되지만 산출은 누적돼야 한다.** 이 한 줄이 본 제안 전체의 설계 지침이다.

---

## 2. 모듈별 사용자 패턴

각 모듈을 "동사 하나 + 입출력 엔티티"로 정의하면 규칙성이 드러난다.

| 모듈 | 사용자 동사 | 입력 | 출력 | 재실행 의미 |
|---|---|---|---|---|
| Project Tree | 기준 모델을 **등록한다** | 파일 | **Model** | 모델 추가 |
| Geometry Param | 형상 변수를 **정의한다** | Model | DesignSpace(geo) | 덮어쓰기 |
| Condition Param | 조건 변수를 **정의한다** | Model | DesignSpace(cond) | 덮어쓰기 |
| Analysis Launcher | 실험을 **실행한다** | Model + DesignSpace | **SampleSet** | **새 배치 생성** |
| Data Preprocessor | 응답을 **라벨링한다** | SampleSet | Dataset | 덮어쓰기 |
| Model Builder | 대리모델을 **학습한다** | Dataset | Surrogate[] | **누적** |
| Model Runner | 예측·민감도를 **조회한다** | Surrogate[] | (조회 결과) | 무상태 |
| Optimizer | 최적해를 **탐색한다** | Surrogate[] | Optimum[] | **누적** |

이 표에서 **"Model 등록"이 모듈이 아니라 Project Tree 의 부수효과로만 존재**한다는 점이 드러난다. 워크플로의 0번 단계가 1급 시민이 아닌 것이 계보 문제의 근원이다.

---

## 3. 엔티티 목록

### 3.1 이미 제대로 된 선례 — FE Condition

먼저 짚을 것: **FE Condition 은 이미 안정 식별자를 가지고 있다.**

```cpp
// controller/DashAnalysisModelContext.h:88
// Deterministic symbol uuid of the condition (persistable across sessions as
// long as the content identity and deck structure are unchanged)
QString getFeConditionUuid(const QString& condName) const;
```

게다가 편집 좌표가 `(uuid, entryPtr, param)` 삼중항이고 `entryPtr` 은 JSON Pointer 다 (`"" = whole node`, `"/entries/N"`). **도메인 전체가 따라야 할 모범이 코드베이스 안에 이미 있다.** 본 제안은 새 개념 도입이 아니라 이 패턴의 확장으로 읽는 게 정확하다.

### 3.2 ID 가 필요한데 없는 것

| 엔티티 | 현재 식별 방식 | 깨지는 지점 | 심각도 |
|---|---|---|---|
| **DesignVariable** | 이름 문자열 | `sanitizeString()` 비가역 변환. 핸들 rename 시 상·하류 연결 단절 | **상** |
| **Response** | 이름 문자열 (+ component · loadstep 과 합쳐 파일명이 됨) | 동일. 추가로 **두 벌로 중복된 sanitizer 가 계약 없이 일치해야만** XML key ↔ config response 매칭이 성립 (3.2.1) | **상** |
| **Run** (실행 배치) | 없음 | DOE·학습·최적화 모두 고정 경로 덮어쓰기 | **상** |
| **Surrogate** | `(response, model)` 쌍 | 재학습 시 같은 쌍이 다른 산출물을 가리킴 → 최적화 결과 재현 불가 | **중** |
| **Model** (기준 해석 모델) | 없음 (Registry 메모리 전용) | 재오픈 시 "이 Set 은 어느 모델 기준" 소실 | **상** |

**DV·Response 의 근거 — 이름 변형은 실제로 손실이다** (`model/builder/ModelBuilderConfigHelper.cpp:12-25`):

```cpp
QString ModelBuilderConfigHelper::sanitizeString(const QString& str) {
    QString result = str;
    result.replace(" ", "_");   result.replace("/", "_");   result.replace("\\", "_");
    result.replace(":", "_");   result.replace("\"", "_");  result.replace("<", "_");
    result.replace(">", "_");   result.replace("|", "_");   result.replace("?", "_");
    result.replace("*", "_");
    return result;
}
```

`"Max Stress"` 와 `"Max/Stress"` 가 둘 다 `"Max_Stress"` 가 된다. 역변환 불가다. 그리고 UI 는 이미 이 충돌과 싸우고 있다 — `DashModelBuilderWidget.cpp:1070-1071` 은 `findText(displayResp)` 가 실패하면 `findText(diskResp)` 로 재시도한다. **이름이 식별자 역할을 하는데 경로 중간에서 이름이 변형된다.**

#### 3.2.1 더 심각한 것 — sanitizer 가 두 벌이다

11절 Q4 조사 과정에서 확인된 사항. **바이트 단위로 동일한 `sanitizeString` 이 서로 다른 모듈에 각각 존재하고, 학습 파이프라인은 이 둘의 출력이 일치한다는 전제 위에서만 동작한다.**

| 구현 | 위치 | 용도 |
|---|---|---|
| `DashPR::Utils::sanitizeString` | `model/preprocessor/DashUtils.cpp:18-32` | XML 의 `dict_item key` 생성 (`DashResultXmlWriter.cpp:309·423·443·581·702`) |
| `ModelBuilderConfigHelper::sanitizeString` | `model/builder/ModelBuilderConfigHelper.cpp:12-25` | config 의 `Configuration.{model}.response` 값 생성 |

외부 학습 프로세스는 config 의 `response` 로 XML 안의 key 를 찾는다. 두 함수 중 **한쪽만 수정되면 매칭이 깨지고 조용히 실패**한다. 이것은 계약이 아니라 우연한 코드 중복으로 유지되는 결합이다.

(같은 종류의 중복: `filterSplitFiles` 가 `DashDataProcessor` · `DashFileLocator` · `DashResponseInitializer` 3곳에 존재. 이쪽은 결과파일 필터라 파이프라인 정합성과는 무관.)

**Response ID 도입 시 실제 작업 대상은 파일명이 아니라 이 sanitizer 계약의 일원화다.** ID 를 `[a-z0-9_]` 로만 발급하면 식별 경로에서 sanitize 자체가 사라지고, 두 함수는 표시 라벨 정규화 용도로만 남는다 (또는 제거).

### 3.3 새 ID 가 필요 없는 것 (합성 참조로 충분)

| 대상 | 참조 형태 | 이유 |
|---|---|---|
| Part / Component | `mdl_9b41e0#PART-1` | 모델 내에서 이름이 안정적 |
| Sample (`runs1`) | `run_a11f03#runs1` | 배치 내에서만 유효하면 됨 |
| FE Condition | `mdl_9b41e0#{uuid}{entryPtr}` | 이미 uuid 보유 (3.1) |
| Symbol (`v1`, `r1`) | Optimizer 정의 내부 바인딩 | 엔티티가 아니라 수식 지역변수 |
| Solver 경로 | `"solver": "Abaqus"` (종류 참조, 런타임 해석) | 환경이지 프로젝트 자산이 아님 |

### 3.4 최종 엔티티 목록

```
Project                                        매니페스트
   ├─ Model[]           mdl_*                  기준 해석 모델 (.inp | .prt + .wbpj)
   │      ├ Part        mdl_*#PART-1           (합성 참조)
   │      └ Condition   mdl_*#{uuid}{ptr}      (기존 uuid 활용)
   ├─ DesignVariable[]  dv_*                   형상·조건 설계변수
   ├─ Response[]        rsp_*                  응답·KPI 정의
   ├─ Definition[]      def_*                  정의 — 덮어쓰기 대상
   ├─ Run[]             run_*                  실행 배치 — 누적 대상
   └─ Surrogate[]       sur_*                  학습 산출물
```

---

## 4. 핵심 재구조 — 모듈 = 정의 1 + 실행 N

엔티티 목록보다 중요한 발견. 8개 모듈을 "무엇을 담고 있나"로 다시 보면 규칙적이다.

| 모듈 | 정의 (덮어쓰기) | 실행 (누적 필요) | 현재 |
|---|---|---|---|
| Geometry Param | 핸들·그룹·범위 | — | 정합 |
| Condition Param | 조건 DV 선택 | — | 정합 |
| Analysis Launcher | DOE 설정 + 기준파일 | **DOE 실행** | 한 Set 에 눌림 |
| Data Preprocessor | 라벨·KPI 정의 | **Process 실행** | 한 Set 에 눌림 |
| Model Builder | 모델·하이퍼파라미터 | **학습 실행** | 한 Set 에 눌림 |
| Model Runner | 조회 설정 | (무상태) | 정합 |
| Optimizer | 목적함수·제약 | **최적화 실행** | 한 Set 에 눌림 |

**4개 모듈이 정의와 실행을 한 Set 에 눌러 담고 있고, 그 결과 실행이 정의를 덮어쓴다.** 1.2절의 고정 경로 3건이 전부 이 구조에서 나온다.

필요한 분리:

```
[현재]  AnalysisLauncher_Set1.json  =  DOE 설정 + DOE 표(재실행 시 덮어씀)

[제안]  def_al_7f3a2c   DOE 설정 (덮어쓰기 OK)
            │  produces
            ├─ run_a11f03   2026-08-05  LHC 50   complete
            ├─ run_b27c91   2026-08-09  LHC 80   complete   parent=run_a11f03
            └─ run_c04e2a   2026-08-09  LHC 80   running
```

`Definition → Run[]` 은 4개 모듈에 **동일한 모양**으로 적용된다. 엔티티가 늘어나는 게 아니라 4개 모듈의 저장 구조가 한 패턴으로 통일된다.

---

## 5. 개편 3안 비교

### 5.1 A안 — 기존 구조 위에 헤더만 추가

각 Set JSON 에 `id` / `kind` / `label` / `created` / `upstream` 5개 키만 추가. 기존 섹션 무변경.

**원리적 한계가 있다.** DV·Response 에 ID 를 부여하려면 **이름이 JSON 키인 곳 5군데**를 전부 손대야 한다:

| 위치 | 형태 |
|---|---|
| `GeometryParameter_{Set}.json` > `DV-Geometry` | 키 = DV 이름 |
| `AnalysisLauncher_{Set}.json` > `DOE Table.headers` | DV 이름 배열 |
| `DataPreprocessor_{Set}/*.xml` > `model_info.parameter` | `dict_item key` = DV 이름 |
| `ModelBuilder_{Set}/model_info.json` > `parameter` · `errors` | 키 = DV·Response 이름 |
| `Optimizer_{Set}.json` > `design_variables[].parameter` | 값 = DV 이름 |

ID 를 넣는 순간 additive 가 아니게 된다. **A안으로는 3.2절 상위 2개(DV·Response identity)를 고칠 수 없다.** 계보만 고치고 식별자는 남기는 절반의 해법이다.

### 5.2 B안 — 엔티티 스토어 전면 개편 (ID 기반 레이아웃)

```
.{Project}.dproj/
   project.json                     엔티티 인덱스
   models/mdl_9b41e0.json
   defs/def_7f3a2c.json
   runs/run_a11f03.json
{ProjectRoot}/
   runs/run_a11f03/{part}/runs1..N/
```

**한계**: 폴더명이 opaque ID 가 되어 수동 검사가 어려워진다. 지금 `AnalysisLauncher_Set1/` 을 탐색기로 열어보는 실무 관행이 깨진다. 자동 테스트가 없는 저장소에서 이 관찰 가능성 손실은 실제 비용이다.

### 5.3 C안 — 개념 전면 개편 + 사람이 읽는 레이아웃 (**추천**)

정의/실행 분리와 엔티티 ID 는 B안대로 전면 도입하되, **파일·폴더 이름은 사람이 읽는 라벨을 유지**하고 ID 는 내용 안에 둔다.

```
.{Project}.dproj/
   project.json                              엔티티 인덱스 (id ↔ 경로 매핑)
   configs/
      Model_Bracket-v3.json                  id: mdl_9b41e0
      Geometry_Set1-Morphing.json            id: def_7f3a2c
      AnalysisLauncher_Set1.json             id: def_4d19b2   (정의만)
      AnalysisLauncher_Set1.runs.json        run[] 인덱스
{ProjectRoot}/
   AnalysisLauncher_Set1/
      2026-08-05_LHC50/{part}/runs1..50/     라벨 폴더 + 내부 meta.json 에 run_id
      2026-08-09_LHC80/{part}/runs1..80/
```

### 5.4 비교와 추천

| 축 | A안 | B안 | **C안** |
|---|---|---|---|
| DV·Response identity | **불가** | 가능 | 가능 |
| 정의/실행 분리 | 모듈별 임시방편 | 구조적 | 구조적 |
| 무효화 전파 계산 | 부분 | 가능 | 가능 |
| 수동 검사 가능성 | 유지 | **손실** | 유지 |
| 구버전 호환 | 자동 | 마이그레이터 | 마이그레이터 |
| 구현 비용 | 소 | 대 | 중~대 |
| 영구 부채 | **읽기 경로 2벌** | 없음 | 없음 |

**잠정 추천(작성자 의견): C안 + 양방향 호환 포기 (1회성 마이그레이터).** 확정 아님 — 아래 3가지는 검토 시작점이지 결론이 아니다. 특히 2·3번은 조직 상황(기존 프로젝트 자산 규모, 고객사 배포 이력)에 따라 뒤집힐 수 있고, 그 정보는 본 조사 범위 밖이다.

1. **양방향 호환 유지 비용이 가장 크다.** 읽기 경로 2벌 = 검증 대상 2벌인데, 이 저장소에는 자동 테스트가 없다(`CLAUDE.md`). 검증 못 하는 분기를 영구히 안게 된다.
2. **1회성 마이그레이터는 유한하다.** 원본 `.dproj` 를 `.dproj.bak` 으로 보존하고 변환하면 실패 시 복구 가능하다. 변환 로직은 기존 `detectGeometryVariant()` 류 휴리스틱을 재활용하고, 그것이 그 휴리스틱의 **마지막 사용처**가 된다 (이후 삭제).
3. **지금이 가장 싸다.** 프로젝트 자산이 누적될수록 비용이 선형 증가한다.

---

## 6. 스키마 예시 (C안 기준 — 스케치)

> 이 절의 JSON 은 **개념을 눈에 보이게 하려는 스케치**이며 스키마 확정안이 아니다. 키 이름·중첩 구조·ID 접두사 모두 논의 대상이다. 확정은 9.2절 0단계의 계약 문서에서 이뤄진다.

### 6.1 `configs/project.json` — 엔티티 인덱스

```json
{
  "$schema": 2,
  "name": "Bracket",
  "created": "2026-08-09T10:02:00+09:00",
  "models": [
    {
      "id": "mdl_9b41e0",
      "label": "Bracket v3",
      "kind": "fe",
      "solver": "Abaqus",
      "files": { "deck": "bracket_v3.inp" },
      "parts": ["PART-1", "PART-2"],
      "fingerprint": "sha256:9b41e0…"
    },
    {
      "id": "mdl_2c8d15",
      "label": "Spring (NX)",
      "kind": "cad",
      "solver": ["NX", "Ansys"],
      "files": { "part": "spring.prt", "template": "spring.wbpj" }
    }
  ],
  "index": {
    "def_7f3a2c": "configs/Geometry_Set1-Morphing.json",
    "def_4d19b2": "configs/AnalysisLauncher_Set1.json"
  }
}
```

`fingerprint` 는 신규 자산이 아니다 — `DashAnalysisModelContext::referenceModelChangedOnDisk()` 가 이미 deck 지문을 관리한다. 매니페스트에 얹기만 하면 "기준 파일이 변경되었습니다" 경고가 **프로젝트 재오픈 시에도** 가능해진다.

### 6.2 Definition 파일 — 공통 헤더 + 모듈 섹션

```json
{
  "$schema": 2,
  "id": "def_4d19b2",
  "kind": "AnalysisLauncher",
  "label": "브래킷 3변수 LHC",
  "created": "2026-08-09T11:20:00+09:00",
  "upstream": {
    "model": "mdl_9b41e0",
    "design_space": ["def_7f3a2c", "def_1e55da"]
  },

  "DOE configuration": { … }
}
```

### 6.3 Run 인덱스 — `AnalysisLauncher_Set1.runs.json`

```json
{
  "$schema": 2,
  "definition": "def_4d19b2",
  "runs": [
    { "id": "run_a11f03", "dir": "2026-08-05_LHC50", "created": "…",
      "method": "Optimal LHC", "n": 50, "status": "complete",
      "table": { "headers": ["dv_a1", "dv_b2"], "samples": […] } },

    { "id": "run_b27c91", "dir": "2026-08-09_LHC80", "created": "…",
      "method": "Optimal LHC", "n": 80, "status": "complete",
      "parent": "run_a11f03",
      "table": { … } }
  ],
  "active": "run_b27c91"
}
```

`parent` 가 있으면 증분(Resampling), 없으면 신규 실행이다. **경로 생성이 이미 `DashIOController` 에 중앙화되어 있어 배치 레벨 삽입의 코드 영향이 좁다** — `getRunFolderPathWithAnalysisType()` 시그니처에 배치 ID 를 추가하면 호출부 7곳이 전부다.

### 6.4 DV / Response 참조 — 이름 → ID

```json
// Geometry 정의
"design_variables": [
  { "id": "dv_a1", "label": "Handle 0 - 두께", "source": "mdl_9b41e0#PART-1",
    "type": "continuous", "min": -0.5, "max": 0.5, "default": 0.0 }
]

// DOE Table headers — 이름 배열 대신 ID 배열
"headers": ["dv_a1", "dv_b2"]

// model_info.json — 키가 ID, 라벨은 값으로
"parameter": { "dv_a1": { "label": "Handle 0 - 두께", "meta": { … } } }
```

`sanitizeString()` 은 **표시 라벨에만** 적용되고 식별자에는 적용되지 않는다. ID 는 `[a-z0-9_]` 로만 발급하므로 sanitize 자체가 불필요해진다.

---

## 7. 분기 시나리오 — 어떤 조합이 사용자에게 의미를 주는가

### 7.1 시나리오

> "현재 수작업" 열은 코드로 확인한 사실이고, **"목표" 열은 5\~6절 제안이 채택됐을 때의 가정**이다. 시나리오 목록 자체도 도메인 추론으로 뽑은 것이라 실사용자 확인이 필요하다 (검증 한계 참조).

| # | 사용자 상황 | 분기점 | 그대로 재사용 | 재생성 필요 | 현재 수작업 | 목표 |
|---|---|---|---|---|---|---|
| S1 | 대리모델 오차 12% → 샘플 부족 판단 | Run 증분 | Model, DV 정의 | 추가 샘플 해석, Dataset, Surrogate | Set 신규 + DV 재선택 → **기존 50샘플 해석 결과 폐기** | `[샘플 추가]` — 기존 배치 상속, 증분만 해석 |
| S2 | 브래킷 형상안 A vs B 비교 | **Model** | 없음 | 전부 | 프로젝트 통째 복사 | `[모델 추가]` + `[구조 복제]` |
| S3 | 같은 형상, 하중 500N → 800N | Condition 정의 | Model, Geometry 정의 | SampleSet 이하 전부 | Condition Set 신규 + AL Set 신규 + DV 재선택 | `[여기서 분기]` 1회 |
| S4 | 변위 최소화했는데 응력도 보고 싶다 | Response 정의 | Model, DV, **SampleSet(해석 결과)** | Dataset, Surrogate, Optimum | DP Set 신규 → **DOE 재선택(복원 안 됨)** → 재라벨링 | 상위 자동 상속, 응답만 추가 |
| S5 | StableNet vs Kriging 비교 | Surrogate | Dataset 전체 | Surrogate 만 | (한 Set 안에서 가능) | 현행 유지 |
| S6 | 목적함수 가중치 변경 | Optimizer 정의 | Surrogate 전부 | Optimum 만 | Optimizer Set 신규 → 폴더 관례추정 의존 | Run 누적으로 이력 비교 |

**S1·S4 가 실무 빈도가 가장 높은데 현재 둘 다 상위 산출물을 버리게 된다.** S4 가 특히 뼈아프다 — 해석 결과(가장 비싼 자산)는 그대로 쓸 수 있는데도 DOE 선택이 복원되지 않아 사용자가 처음부터 다시 찾아야 한다 (기반 문서 7-1절).

의미 있는 조합은 예외 없이 **"상위 재사용 + 특정 지점 분기"** 형태다. `O` 하나뿐인 S5 가 잘 되는 이유도 명확하다 — 분기가 **한 Set 내부**에서 일어나 엣지가 필요 없기 때문이다.

### 7.2 무효화 전파 행렬 — 엔티티 모델의 실질 payoff

엔티티와 엣지가 있으면 **"무엇이 낡았는가"를 계산할 수 있다.** 이것이 사용자에게 주는 가장 큰 가치다.

| 변경 대상 | 무효화되는 하위 | 재사용 가능한 것 |
|---|---|---|
| Model deck 교체 | 전부 | 없음 |
| DV 추가 / 범위 변경 | Run(DOE) 이하 전부 | Model |
| **DV 이름만 변경** | **없음** (ID 기반이면) | 전부 — 현재는 전부 단절 |
| SampleSet 증분 | Dataset, Surrogate, Optimum | 기존 해석 결과 |
| Response 추가 | Dataset, Surrogate, Optimum | Model, DV, **SampleSet** |
| Labeling 규칙 변경 | Dataset 이하 | SampleSet |
| 하이퍼파라미터 변경 | 해당 Surrogate, Optimum | Dataset |
| 목적함수 변경 | Optimum 만 | Surrogate 전부 |

"DV 이름만 변경 → 무효화 없음" 행이 ID 도입의 가치를 가장 압축적으로 보여준다. 지금은 핸들 하나 rename 하면 하류 전체가 조용히 끊긴다.

---

## 8. UI 설계 아이디어

기반 문서 7-4절이 지적한 "화면 어디에도 계보가 없다"에 대한 방향 스케치. **UI 기획이 아니라 데이터 모델 변경이 화면에서 어떻게 보일 수 있는지를 보이려는 예시**다. 배지 기호·문구·배치는 전부 임의이며, 실제 화면은 기획 검토를 거쳐야 한다.

### 8.1 Set 상태 배지 — I/O 완결성

| 배지 | 상태 | 판정 |
|---|---|---|
| ○ | Empty | 정의 없음 |
| ◐ | Draft | 정의 미완 (필수 입력 누락) |
| ● | Ready | 정의 완결, 실행 산출 없음 |
| ✔ | Complete | 정의 완결 + 유효 산출 존재 |
| ⚠ | **Stale** | 산출은 있으나 상위가 그 뒤에 변경됨 |
| ✕ | Broken | 상위 미해결 (파일 삭제 · ID 미발견) |

`⚠ Stale` 은 7.2절 전파 행렬로 자동 계산된다. **"이 모듈이 의미론적으로 완결인가"를 사용자가 한눈에 보는 지점이다.**

### 8.2 사이드바 — 계보와 상태

```
[Project]
   ▾ 기준 모델                                    ← 신설 섹션
       ✔ Bracket v3        Abaqus · 2 parts
       ⚠ Spring            NX+Ansys · 파일 변경됨
   ▾ Geometry Parameterization
       ✔ Set1-Morphing     ◂ Bracket v3           ← 상위 라벨 인라인
       ✕ Set2-Morphing     ◂ (모델 없음)
   ▾ Analysis Launcher
       ✔ Set1              ◂ Set1-Morphing + Set1(cond)   3 runs
       ⚠ Set2              ◂ Set1-Morphing        1 run · DV 변경 후 미실행
   ▾ Data Preprocessor
       ⚠ Set1              ◂ AL-Set1 / 2026-08-05  ← 어느 배치인지까지 표시
```

### 8.3 모듈 패널 상단 — breadcrumb + 완결성 체크리스트

```
Bracket v3  ›  Set1-Morphing + Set1(cond)  ›  AL-Set1 / 2026-08-09_LHC80
─────────────────────────────────────────────────────────────────────────
입력  ✔ 기준 모델   ✔ 설계변수 5   ✔ 기준 해석파일   ✔ 솔버 경로(Abaqus)
출력  ✔ 샘플 80     ✔ 해석 완료 78   ⚠ 실패 2
```

이 두 줄이 "이 모듈의 I/O 가 완결적인가"에 대한 직접적 답이다. 상위 클릭 시 해당 Set 으로 이동한다.

### 8.4 실행 이력 패널 — 누적 개념 노출

각 실행형 모듈(AL · DP · MB · Opt) 하단에 공통 배치:

```
실행 이력                                        [ + 새 실행 ]  [ ⤴ 샘플 추가 ]
  ●  2026-08-09_LHC80    80샘플   완료 78 / 실패 2      ← 활성
     2026-08-05_LHC50    50샘플   완료 50               [활성으로] [비교] [삭제]
```

`[⤴ 샘플 추가]` 가 S1 을, `[비교]` 가 S5 · S6 을 직접 지원한다. 현재 UI 만 존재하고 로직이 없는 Resampling 탭이 여기로 흡수된다.

### 8.5 분기 메뉴

| 메뉴 | 위치 | 동작 | 지원 시나리오 |
|---|---|---|---|
| `[여기서 분기]` | Set 우클릭 | 선택 Set 의 `upstream` 을 복사한 형제 Set 생성 | S3 · S4 · S6 |
| `[구조 복제]` | Model 우클릭 | 이 모델에 매달린 하위 그래프 전체를 새 모델 기준으로 복제 | S2 |

---

## 9. 도입 단계와 기존 티켓 관계

### 9.1 W20(#246) 과 동시 진행하지 않는다

당초 "같은 파일을 두 번 열게 되니 묶자"고 보았으나 **철회한다.**

**결정적 근거**: 이 저장소에는 자동 테스트가 없다(`CLAUDE.md`). 테스트 없는 상태에서 **코드 구조 축(God-object 해체)과 데이터 구조 축(스키마 개편)을 동시에 바꾸면 회귀 발생 시 원인 분리가 불가능**하다. 롤백 단위도 엉킨다. 파일을 두 번 여는 비용보다 이쪽이 훨씬 크다.

다만 순수한 순차 진행도 낭비다. W20 이 현행 스키마 기준으로 클래스 경계를 그으면, 스키마 개편 때 그 경계를 다시 조정하게 된다.

### 9.2 잠정 순서안 — 계약 선행, 구현 순차

> 아래 단계 구분은 **논의용 초안**이다. 각 단계의 범위·기간은 산정하지 않았고, 티켓으로 옮기기 전에 재검토가 필요하다.

```
[0단계] 엔티티 계약 확정 — 문서만, 코드 변경 0
   │   엔티티 목록 · ID 발급/참조 규칙 · 정의↔실행 분리 · 무효화 전파 · 마이그레이션 매핑표
   │   → 코드 충돌 없음. W20 설계의 입력이 됨
   │   산출: 스펙 문서 1건 + 열린 질문(11절) 해소
   ▼

[1단계] W20 (#246) — 단, 계약을 경계 설계에 반영
   │   DashProject 를 쪼갤 때 "설정 파일 I/O" 조각의 인터페이스를
   │   미래 엔티티 스토어 기준으로 설계 (구현은 현행 스키마 그대로)
   │   → 나중에 구현체만 교체
   │   검증: 기존 프로젝트 열기/저장 동작 무변화
   ▼

[2단계] 엔티티 스토어 구현 (C안)
   │   1단계 인터페이스 뒤편만 교체 + 1회성 마이그레이터 (.dproj.bak 보존)
   │   검증: 구버전 프로젝트 변환 → 트리 · 상위연결 · 산출물 동일성 확인
   ▼

[3단계] UI (8절)
       완결성 배지 · breadcrumb · 실행 이력 · 분기 메뉴
```

0단계가 핵심이다. **문서 하나로 두 작업의 충돌을 제거하면서 W20 을 헛되게 만들지 않는다.**

> **2단계 선행 조건 (2026-08-18 추가 — [[Project-Store-Survey-Key-IO-Ledger]] 3.3)**
> `ModelBuilder_{Set}.json` · `ModelBuilder_{Set}-MCU.json` 은 config 경로가 DeepOpt·MCU 의 CLI 인자이고 **도구가 `status` 를 되쓴다** (`"Done"` 을 쓰는 C++ 코드 0건 · `DashModelBuilder.cpp:1420` 주석 · 1초 폴링 구조 3중 정황). 따라서 그 2개 모듈에 한해 **도구 계약 개정이 엔티티 스토어 교체보다 먼저**여야 한다.
> 개정 권한은 있음이 확인됐으므로(2026-08-18) 차단이 아니라 **순서 제약**이다. 단 규약과 구현의 소유가 갈린다 — **계약·규약은 중앙(본 계열 문서)에서 관리하고 도구 코드 수정은 별건**이다. 열린 질문 추가는 불요.

### 9.3 관련 티켓

| 티켓 | 관계 |
|---|---|
| #246 [W20] God-object 해체 | 9.2 의 1단계. `DashProject` · `DashProjectManager` 가 공통 대상 |
| #239 Track B(구조 리팩터) 현황 | 본 제안은 Track B 의 데이터 계층 축 |
| 기반 문서 9절 우선순위 1~3 | 2단계에 흡수 (별도 진행하면 중복 작업) |

---

## 10. 현 시점에서 검토 대상에 넣지 않은 것

논의가 무한 확산하지 않도록 경계를 적어 둔다. **금지 사항이 아니라 이번 라운드의 스코프 선언**이며, 필요하다고 판단되면 다시 열면 된다.

- **DB / ORM 도입 안 함** — JSON 파일 유지. 문제는 저장 매체가 아니라 엣지 부재와 식별자 부재다.
- **엔티티마다 클래스 계층 안 만듦** — 공통 헤더 구조체 하나와 그것을 읽고 쓰는 자유함수면 충분하다. 8종 모듈 모델 클래스를 상속으로 묶는 리팩터는 이득 대비 위험이 크다.
- **Surrogate / Optimum 을 파일 단위로 승격 안 함** — Definition 하위 배열 원소로 두되 ID 만 부여해 나중에 승격 가능하게 한다.
- **사용자에게 ID 를 노출 안 함** — 화면에는 라벨만. ID 는 저장·참조 전용.
- **양방향 호환 유지 안 함** — 1회성 마이그레이터로 갈음 (5.4 근거).
- **Set 명명 규칙 폐기 안 함** — `{Module}_{Set}` 파일명과 폴더명은 사람이 읽는 라벨로 유지 (C안).

---

## 11. 열린 질문 — 착수 전 결정 필요

| # | 질문 | 영향 |
|---|---|---|
| 1 | ID 발급 방식 — 랜덤 short id vs 내용 해시 vs 순번 | 마이그레이션 재현성. 내용 해시면 같은 프로젝트를 두 번 변환해도 동일 ID (권장) |
| 2 | Run 보존 정책 — 무제한 누적 vs N개 초과 시 경고 vs 자동 정리 | 디스크 사용량. 해석 결과는 GB 단위 |
| 3 | 기존 프로젝트 마이그레이션 시점 — 열 때 자동 vs 명시적 메뉴 | 사용자 놀람 방지 vs 편의 |
| ~~4~~ | ~~XML 데이터셋 파일명을 ID 기반으로 바꿀 것인가~~ | **✔ 해소 (2026-08-09 코드 조사)** — 아래 11.1 참조 |
| 5 | Model 을 프로젝트 루트 복사본 기준으로 볼 것인가, 원본 경로 참조로 볼 것인가 | 현재 `[Add File]` 은 복사한다. 원본이 갱신되면? |
| 6 | 0단계 계약 문서를 `[사전조사]` Issue 로 연동할 것인가 | 기존 [#197](https://github.com/NumeRealWorks/DashOpti_GUI/wiki/197-1-gui-restructure-mvvm-qml)~[#206](https://github.com/NumeRealWorks/DashOpti_GUI/wiki/206-1-w6-w10-thread-execution-design) 패턴 준거 여부 |

남은 1·2·3·5·6번은 팀 합의 사항이다.

### 11.1 Q4 해소 — XML 파일명은 아무도 파싱하지 않는다

**질문 전제부터 틀렸다.** `docs/Module_Configuration_Files.md` 는 파일명을 `{response_name}.xml` 로 기술하지만 실제는 KPI 정의 삼중항의 인코딩이다.

| 경로 | 규칙 | 근거 |
|---|---|---|
| 일반 | `{component}_{step}_{substep}_{name}.xml` | `DashDataProcessor.cpp:1844` |
| BORE/BOSS 그룹 | `{BORE\|BOSS}_{step}_{substep}_{originalName}.xml` | `:1831` |
| Modal | `{component}_{stat}_{modeName}.xml` | `:3266` |
| Custom KPI | `{component}_{loadstep}_{name}.xml` | `:3650` · `:3967` · `:4249` · `:4532` |

**결론: 파일명을 파싱하는 코드가 없다.** XML 참조 지점 전수 조사 결과 전부 `*.xml` 글롭 + 경로 전달이다.

| 소비처 | 동작 |
|---|---|
| `DashModelBuilder.cpp:89 · 107 · 190` | `entryList("*.xml")` — 목록 나열만 |
| `DashModelRunner.cpp:1552` | 동일 |
| `DashResultsAnalyzerWidget.cpp:1303 · 1822` | 동일 (콤보 표시용) |
| `DashModelBuilder::onLoadButtonClicked()` `:268-308` | 파일명으로 **경로만 조립**, 이후 파일을 열어 내용 파싱 |

`completeBaseName()` 을 쓰는 유일한 지점(`DashResponseInitializer.cpp:336`)은 `.odb`/`.rst` 결과파일 분할 필터로 XML 과 무관하다.

응답 식별은 **XML 내부 `dict_item key`** 로 이뤄지고, 외부 학습 프로세스는 config JSON 을 통해 경로와 응답명을 **별도로** 받는다:

```
DashOptiDeepOpt.exe train-model-1d "<ModelBuilder_{Set}.json>" --output-dir "<…>"
                                          ├─ "Data Label" > "Dataset"          = XML 절대경로
                                          └─ "Configuration".{model}."response" = 응답명(sanitized)
```

따라서 **파일명을 ID 기반으로 바꿔도 GUI 는 깨지지 않는다.**

**단서 2가지**:
- `extensions/deep_opt/DashOptiDeepOpt.exe` 는 이 저장소에 없어 내부 동작은 미확인이다. 위 결론은 **인터페이스 기반 추론**이며 exe 확보 시 재확인이 필요하다 (필요한 정보를 별도로 받으므로 파일명을 파싱할 구조적 이유가 없다는 근거).
- 조사 중 **진짜 위험은 파일명이 아니라 sanitizer 이중화**임이 드러났다 (3.2.1). Response ID 도입의 실제 작업 대상은 그쪽이다.

---

## 검증 한계

| 항목 | 근거 강도 | 비고 |
|---|---|---|
| 1절 결손 진단 | **강** | 기반 문서의 정적 조사 결과를 그대로 승계 |
| 3.2절 sanitize 손실 | **강** | `ModelBuilderConfigHelper.cpp:12-25` 원문 + UI 우회 코드 확인 |
| 4절 정의/실행 미분리 | **강** | 고정 경로 3건 코드 확인 |
| 5절 A안 한계 (JSON 키 5군데) | **강** | `docs/Module_Configuration_Files.md` 와 각 모듈 저장 코드 대조 |
| 6절 스키마 | **제안** | 검증 대상 아님 — 합의 후 확정 |
| 7절 시나리오 빈도 추정 | **약** | 실사용 로그 없이 도메인 추론. 실제 사용자 인터뷰로 보정 필요 |
| 8절 UI | **제안** | 프로토타입 미제작 |
| 9절 단계 구분 | **중** | 티켓 범위는 Issue 본문 기준. 실제 착수 시 재산정 필요 |
