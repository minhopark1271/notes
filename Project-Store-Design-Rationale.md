# 결함 축 대응과 신설 배선 — 저장 구조 설계 · 근거

> **설계안은 [Project-Store-Design-Layer-Cut](Project-Store-Design-Layer-Cut.md) 에 있다.** 그쪽이 "무엇을 만들 것인가" 이고 본 문서는 **"왜 만드는가 · 무엇이 닫히는가 · 무엇을 함께 고쳐야 하는가"** 다.
> 현황 키 단위 실측: [Project-Store-Survey-Key-IO-Ledger](Project-Store-Survey-Key-IO-Ledger.md)
> 결함 축 정의: [Cross-Module-Defect-Menifest-Axis](Cross-Module-Defect-Menifest-Axis.md) · [Cross-Module-Defect-Axis-Candidates](Cross-Module-Defect-Axis-Candidates.md)
> Track B 좌표: #239

> ## ⚠ 문서 상태: 조사 — 설계 확정 아님
>
> * 여기 담긴 **현황 사실**은 정적 실측이고, **대응 판정**은 설계안이 확정돼야 성립한다
> * 이 문서로 티켓을 만들지 않는다. 3절이 작업 목록의 후보이지 작업 목록 자체는 아니다

## 개요

초판은 저장 구조 설계와 그 근거를 한 문서에 담았다. 설계는 [Project-Store-Design-Layer-Cut](Project-Store-Design-Layer-Cut.md) 로 넘어갔고, 여기 남는 것은 **그 설계가 서 있는 근거 다섯**이다.

| 절 | 내용 | 왜 남기나 |
|---|---|---|
| 1 | 파일 표현이 아예 없는 데이터 | 설계가 신설하는 자리의 출발점 |
| 2 | 읽기 배선을 신설해야 할 것 15건 | **구현 작업 목록의 후보.** 설계는 "무엇을 저장하나" 만 정하고 "어디서 읽나" 는 정하지 않는다 |
| 3 | 결함 축 A\~G 와의 대응 | 이 작업이 결함 69건 중 무엇을 닫고 무엇을 못 닫는지 |
| 4 | 어휘 실측 | `Reference` 명명의 수치 근거 |
| 5 | 경로 규약 불일치 5곳 | 레이아웃을 단일 루트로 바꾸는 근거 |

---

## 1. 파일 표현이 없는 데이터

저장 자리가 아예 없어 재시작하면 소실되는 것들이다. 설계안이 신설하는 필드의 출발점이다.

| # | 데이터 | 현재 | 설계안의 자리 |
|---|---|---|---|
| 1 | **케이스 실패 사유** | 어떤 파일에도 없다 | `execution.json` 의 `cases[].reason` |
| 2 | **스테이지별 상태** | 케이스당 문자열 1개로 평탄화 — "STP 는 됐는데 해석에서 죽었다" 를 구별 못 함 | `cases[].stages[]` |
| 3 | 프로젝트 매니페스트 | 없다. 폴더 이름 + `configs/` 의 파일명 집합이 정체성 | `project.json` |
| 4 | 모듈 인스턴스 색인 | 없다. 파일명 접두사 글로빙으로 복원 | `instances[]` |
| 5 | Reference 레코드 | 파싱 결과가 메모리 해시에만, 활성 대상 1개, 경로 미직렬화 | `references[]` |
| 6 | 상위 바인딩 + 지문 | 키가 일부만 있고 리더가 없다 (2절) | `definition.json` 의 `upstream` |
| 7 | 실행 레코드 | 없다. 재실행이 이전 것을 덮는다 | `execution.json` |
| 8 | Condition Value 편집분 | 메모리 deck 에만 있고 모듈을 떠나면 소실 (CON-D5) | 정의의 Value 오버레이 |
| 9 | 예측 카운터 | 메모리 전용 → 0 에서 재시작해 기존 파일을 덮는다 (RUN-D34) | 실행 메타 |

---

## 2. 읽기 배선을 신설해야 할 것 15건

**저장이 아니라 읽기가 없어서 생긴 것들이다.** 설계안이 자리를 만들어도 이 배선이 없으면 값은 여전히 쓰이기만 한다.

좌표는 설계안의 칸 표기를 쓴다 — `upstream`(정의 안의 계보 블록) · Set 메타(`definition.json`) · 실행 메타(`execution.json`) · 벌크(페이로드 파일).

| # | 대상 | 현재 | 신설 읽기 시점 | 결함 ID |
|---|---|---|---|---|
| 1 | DataPreprocessor 상위 DOE 선택 | 쓰기만 (`Selected DV-Table` · `Selected Analysis File` — 읽는 코드 **0곳**) | 모듈 진입 시 `upstream` | **PRE-D7** (우선순위 1) |
| 2 | ModelRunner · Optimizer 의 ModelBuilder 선택 | **기록 자체 없음** → `folders[0]` / 관례 추정 | 진입 시 `upstream` | **RUN-D8 · OPT-D21** (우선순위 2) |
| 3 | ResultsAnalyzer method 블록 (축·색·스타일) | write-only | 패널 생성 시 `view.json` | ANA-D9 |
| 4 | ModelRunner 예측 3섹션 | write-only | 진입 시 Set 메타 | RUN-D33 |
| 5 | 예측 카운터 | 메모리 전용 → 0 에서 재시작해 기존 파일을 덮는다 | 진입 시 실행 메타 (마지막 실행의 다음 번호) | RUN-D34 |
| 6 | 모핑 대상 파트 | 저장 경로 없음 | `upstream` | MOR-D11 (MOR-D2 와 연쇄) |
| 7 | 핸들 이름 | 트리 아이템 텍스트 + 세션 한정 `QMap` | Set 벌크(VTP 배열) 또는 Set 메타 | MOR-D5 |
| 8 | Morphing constraints | **파서만 있고 라이터가 레포에 없다** | Set 메타 | MOR-D10 |
| 9 | Condition 대상 deck | 전역 active context 1개 | `upstream.reference` | CON-D10 |
| 10 | ModelBuilder `transformation` | 쓰기만 하고 로더가 값을 버린다 — 원인은 **로더 2벌** | Set 메타 로드 | BLD-D8 |
| 11 | `parseDataLabelSection` · `parseConfigurationSection` | 구현 있고 **호출부 0** | Set 메타 로드에 배선 | BLD-U3 |
| 12 | MCU `Data Label.Dataset` 배열 | 배열로 저장되나 상속 로더가 `.toString()` 을 불러 빈 문자열이 되고 고정 헤더 표로 떨어진다 | Set 메타 로드 (배열 로더는 이미 있고 호출부가 0) | 신규 |
| 13 | CAD 파라미터 체크 상태 | 복원 직후 캐시 재적용이 전 행을 `false` 로 덮는다 | 복원을 캐시 재적용 **뒤로** | CAD-D4 |
| 14 | 활성 해석 모델 | 메모리 전용 (`m_activeFilePath` 미직렬화) | `upstream` — 모듈마다 | PDM 5-2 |
| 15 | 산출물 경로 | 디스크 스캔 (`*.dat` · `*.inp` 글로빙, `AnalysisLauncher_*.json` 글로빙) | 실행 메타 `artifacts[]` | RUN-D35 · ANA-U1 |

12번은 [Project-Store-Survey-Key-IO-Ledger](Project-Store-Survey-Key-IO-Ledger.md) 의 신규 실측이고 나머지는 선행 조사 승계다.

---

## 3. 결함 축 A\~G 와의 대응

### 3.1 축별로 닫는 자리

매니페스트 부재로 귀속된 결함 **69건**을 7축으로 가른 것이다.

| 축 | 건 | 닫는 자리 |
|---|---|---|
| **A** 기준 모델·상위 선택이 기록되지 않는다 | 12 | 정의의 `upstream` (reference · definition · execution 엣지) + **2절 읽기 배선** |
| **B** 파일명·경로가 스키마 노릇을 한다 | 11 | 프로젝트 메타의 색인 (ID ↔ 경로) + "엣지는 ID 를 가리킨다" 규칙. **조인 키가 이름에서 ID 로 옮겨간다** |
| **C** variant 판정이 휴리스틱으로 흩어져 있다 | 6 | 색인의 명시 `variant` 필드 1곳. 이름 접미사 · JSON 키 · `UserRole+2` 3벌 폐기 |
| **D** 스키마 명세가 없어 키·형이 어긋나거나 자리가 없다 | 15 | `$schema` + 키 계약. 자리가 없던 것(핸들 이름 · constraints · Condition Value)은 1절 신설 |
| **E** 산출물 대장이 없어 자산·부산물·실패를 구분하지 못한다 | 8 | `artifacts[]` + `cases[].reason` + `cases[].stages` |
| **F** Set 이 1급 개체가 아니다 | 11 | 모듈 인스턴스 = 디렉토리 + 색인 항목. 전환·삭제·스코프 계약이 한 곳에 모인다 |
| **G** 설정 JSON 의 쓰기 주체·시점 규약이 없다 | 6 | 칸마다 라이터 1곳 + I/O 시점 표. **도구의 쓰기가 자기 실행의 EB 안에 갇혀 외부 도구 예외가 사라진다** — 금지되는 것은 파일 쓰기가 아니라 담당 칸 위를 쓰는 것이다 (설계안 규약 9) |

### 3.2 이 구조가 닫지 못하는 것

**저장 구조를 세워도 그것만으로 닫히는 결함은 0건이다.** 41건은 개별 수정으로 닫히되 **스키마 결정에 종속**되고(그 결정 없이 고치면 나중에 다시 고친다), 28건은 다른 축의 동반 작업을 요구한다.

| 동반 축 | 건 | 이 구조가 못 하는 것 |
|---|---|---|
| 소유 경계 | 12 | **뷰가 정본인 문제.** 위젯 셀 스핀박스에서 값을 읽는 한 정의 파일에 무엇을 쓸지가 정해지지 않는다 |
| 실행 모델 | 9 | 배치 오케스트레이션 · 워커화. 실행 메타의 파일 형태를 정해도 **쓰는 주체가 GUI 스레드면** 원자성·비폴링 규약이 지켜지지 않는다 |
| 요청↔완료 | 7 | 외부 데몬 · DLL 경계 |

축 밖으로 남는 것도 있다. **판정 규칙 축 18건**(`startsWith("r")` + 두 번째 글자 숫자로 케이스 판정 · 쉼표 개수로 차원 판정 · `contains("modal")`)은 판정 대상이 매니페스트에 담을 값이 아니라 **자리를 만들어도 남는다.**

---

## 4. 어휘 실측 — `Reference` 명명의 근거

설계안은 기준 해석 파일 엔티티를 `Reference` 로 부른다. 초판은 `Model` 이라 불렀고, 후보 4종을 실측해 바꿨다. (`dev` @ `4c7608e`, `external/` 제외)

| 용어 | 코드 | 무엇을 가리키나 | 사용자 노출 |
|---|---|---|---|
| `model` 단독 | `setModel(` **91회** · `model/` 디렉토리 · surrogate 계열 **293회** | **MVC 계층** + **대리모델** 두 뜻으로 포화 | UI 문자열 14종 — Trained Surrogate Model · Available Models · Model Upload · Model Type · Select Model … **거의 전부 대리모델** |
| `AnalysisModelContext` | 174회 | 파싱된 해석 덱 | 0 |
| `deck` | 40회 · **전부 주석, 식별자 0건** · 11파일 | 솔버 입력 텍스트 (`.inp`·`.dat`) | 0 |
| `input` | `inputFiles` 64 · `input_files` 35 · `InputFilePathes` 25 · `inputFilePath` 16 | **3중 충돌** | UI 8종, 역시 3뜻 |
| **`reference`** | `referenceFile` 48 · `refFile` 29 = **77회** | 기준 해석 파일과 그 템플릿 행 | Input Reference File · Add Reference File · Reference Set: |

**`Model` 기각** — 해석 덱 뜻으로 쓰이는 것은 `DashAnalysisModelContext` 복합어 하나뿐이고 단독 "Model" 은 MVC 와 대리모델이 이미 차지했다. 화면에 뜨는 "Model" 이 거의 전부 대리모델이라 사용자 혼동 위험이 가장 크다.

**`deck` 기각** — 충돌은 0이지만 `.prt`(NX 파트)·`.wbpj`(WB 프로젝트)를 담지 못하고, 설계안이 이미 **역할 이름**으로 쓰고 있어 엔티티로 올리면 `Deck.files.deck` 이 된다.

**`input` 기각** — 넷 중 가장 나쁘다. 이미 세 뜻으로 갈려 있다.

| 뜻 | 쓰이는 곳 |
|---|---|
| 기준 해석 파일 | "Input Reference File" · `input_files[]` |
| DOE 가 생성한 케이스 입력 파일 | "Analysis Input Files" · "Generate Input File" · "Input Cases" |
| 학습 입력 변수 | "Input Design Variables" |

여기에 `InputFilePathes`(25회)는 preprocessor DLL 의 **결과** 파일 경로라 이름과 뜻이 이미 어긋나 있다.

**`Reference` 채택** — 기존 식별자 77회와 UI 라벨이 전부 이 뜻이라 새 어휘를 만들지 않는다 · 기존 Reference File 행이 이미 `{name, target_component, path}` 로 **파일 묶음**이라 개념이 연속적이다 · "기준" 은 형식 중립이라 FE·CAD 양쪽을 담는다.

| 자리 | 채택 |
|---|---|
| 엔티티 · ID · 색인 키 · 디렉토리 | `Reference` · `ref_*` · `references[]` · `references/` |
| 엣지 | `upstream.reference` |
| `files` 안 역할 이름 | `deck` · `part` · `template` · `material` — **변경 없음** |
| 사용자 라벨 | 기준 해석 파일 |
| C++ 타입 | `DashAnalysisModelContext` 계열 **유지** — 174회 선례이고 내부 전용이라 UI 충돌이 없다 |

부작용 1건: AnalysisLauncher JSON 의 `input_files[]` 키가 개념과 어긋난 채 남는다. 개명이 자연스럽다.

---

## 5. 경로 규약 불일치 5곳

질문은 하나다 — **"어느 모듈의 산출물이 숨김 `.dproj` 로 가고 어느 것이 사용자 루트로 가나".** 여기에 답하는 자리가 다섯인데 서로 다른 답을 낸다. 실질 쟁점은 **Optimizer 하나**이고 MCU 가 예외로 붙는다.

| # | 자리 | 무엇이라고 말하나 | 좌표 |
|---|---|---|---|
| 1 | `ModuleType` enum 주석 | `// Internal Data: Uses ProjectPath (hidden from user)` 그룹에 **ModelBuilder 와 Optimizer 둘 다** 들어 있다 | `DashIOController.h:22-24` |
| 2 | 클래스·함수 doc-comment | `Internal Data: In {ProjectRootDir}/…` — 이름은 "Internal" 인데 경로는 사용자 루트이고, **User Output 과 같은 경로**를 적어 둬 구분 자체가 무의미하다 | `DashIOController.h:39-40` · `:63-65` |
| 3 | `getModuleDir()` 구현 | `if (type == ModuleType::ModelBuilder)` 만 internal → **Optimizer 는 UserRoot** | `DashIOController.cpp:31` |
| 4 | MCU 역방향 예외 | `getModuleDir()` 자체를 우회해 `getUserPath()` 에 직접 `ModelBuilder_{Set}` 를 붙인다. 주석 — *"MCU training results must live under userPath, not the hidden projectPath (.dproj)"* | `DashModelBuilderMCU.cpp:554-562` |
| 5 | `isUserOutputType()` | AnalysisLauncher · DataPreprocessor · ModelRunner · ResultsAnalyzer 만 true → **Optimizer 를 제외**한다 (3번 구현과 반대) | `DashIOController.cpp:106-112` |

Optimizer 에 대해 1번은 "숨김", 3번은 "사용자 루트", 5번은 "user output 아님" 이라고 각각 말한다. 2번은 두 분류의 경로를 같게 적어 구분을 무너뜨린다.

**실제 거동은 3번 + 4번**이다 — ModelBuilder Sim 만 `.dproj` 안, 나머지 전부 사용자 루트, MCU 는 우회.

5번이 지금 무해한 이유는 **`isUserOutputType()` 호출부가 0곳**이기 때문이다. 참조는 선언(`.h:131`)과 정의(`.cpp:106`) 둘뿐이다. **그 함수를 신뢰하는 코드가 생기는 순간 결함이 된다.**

이것이 설계안에서 단일 루트를 택한 근거다 — **규칙을 고치는 것보다 루트를 하나로 줄이면 규칙 자체가 필요 없어진다.**

---

## 6. 검증 한계

| 항목 | 근거 강도 | 비고 |
|---|---|---|
| 5절 경로 규약 5곳 · `isUserOutputType()` 호출부 0곳 | **강** | `dev` @ `4c7608e` 재확인 |
| 4절 어휘 실측 | **중** | `dev` @ `4c7608e` 리터럴·식별자 grep 기준. 변수로 조립되는 문자열과 `.ui` 밖 사용자 노출은 누락 가능 |
| 1절 · 2절의 현황 열 | **강** | 선행 조사 3종의 정적 측정과 [Project-Store-Survey-Key-IO-Ledger](Project-Store-Survey-Key-IO-Ledger.md) 의 키 단위 실측 승계. "읽는 코드 0곳" 판정만 **중**(grep 1중) |
| 2절의 "신설 읽기 시점" 열 | **중** | 설계 제안이다. 각 행이 현재 코드의 어느 함수에 배선돼야 하는지는 특정하지 않았다 |
| 3절 축 대응 | **중** | 축 정의에 자리를 붙인 것이고 건별 재판정은 하지 않았다 |
| 3.2 의 41 / 28 분류 | **중** | 선행 조사의 판정을 그대로 승계 |
| 실행 검증 | **없음** | 빌드 · 실행 없이 정적 근거만 |
