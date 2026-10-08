# 계층 재단과 배치 — 저장 구조 설계 · 본체

> **이 문서는 단독으로 읽힌다.** 아래 문서들은 근거의 출처이지 서술의 일부가 아니다 — 인용된 사실은 본문에 다시 적었다.
>
> * [[Project-Store-Design-Rationale]] — 이 설계의 **근거**. 결함 축 A\~G 대응 · 읽기 배선 신설 15건 · 어휘 실측 · 경로 규약 불일치 5곳. 이 설계가 결함 몇 건을 닫고 무엇을 함께 고쳐야 하는지는 그쪽에 있다
> * [[Project-Store-Design-Alpha-Minimal]] — 이 설계의 **첫 배포 단위를 다시 자른 착수안**. 0.3 이 기각한 안 α 위에서 매니페스트만 최소로 도입하고 의존성 단위를 인스턴스로 접는다(execution 은 개체가 아니라 덮어쓰기). 본체와 갈리는 결정 셋 — 레이아웃(β→α) · `upstream.references` 배열화 · `$schema` 번호 축(α=1 · β=2). **9절의 마이그레이션 미수행이 α 에서는 승격으로 바뀐다** — 파일 이동이 0 이라 구프로젝트를 거부하지 않고 글로빙을 열기 경로에서 승격 경로로 한 번 옮긴다. 현황 1·5 가 닫히고 2·3·4(전부 실행 귀속)가 남으며(α 는 현황을 앞의 5건으로 자른다), 축 7개 중 C 하나만 통째로 사정권이다. α→β 전환에 **값 발급이 `exec_` 뿐이고 그 대상이 0건**이라는 것이 α 를 먼저 두는 근거다
> * [[Project-Store-Survey-Key-IO-Ledger]] — 현행 실측(`dev` @ `4c7608e`). 4절 "현재 실체" 열의 근거
> * [[Project-Store-Survey-Inputs-Payloads-Runtime]] — 대장의 여집합. 산출물 포맷 6종 · XML 컨테이너 · 실행 상태 쓰기 경로
> * [[Cross-Module-Defect-Menifest-Axis]] — 결함 69건의 7축 분류
>
> Track B 좌표: #239

> ## ⚠ 문서 상태: 구상 — **확정 아님**
>
> * **팀 합의 전, 착수 승인 전.** 이 문서로 구현에 착수하거나 티켓을 만들거나 스키마를 계약으로 인용하지 않는다
> * 확정되려면 : 10절 잔여 7건(조사·인계) + 8.3.4 미결 9건(사용자 행동 정책) 해소 → 팀 리뷰 → 계약 문서로 승격
> * 실행 검증 없음. 빌드·실행 없이 정적 근거만

## 개요

프로젝트 저장 구조를 **모듈 인스턴스 단위**로 다시 짠다. 저장물은 **귀속(프로젝트 · Set · 실행) 셋과 종류(메타 · 벌크) 둘의 교차 6칸**으로 갈리고, 칸마다 라이터가 하나다. 모듈 인스턴스 하나는 디렉토리 하나이고, 모듈 간 의존은 소비자 쪽 정의 파일에 ID 로 저장된다.

아홉 가지를 정한다 — 전제(0절) · 재단(1절) · 규약(2절) · 배치(3절) · 칸별 실체(4절) · 엣지(5절) · 입력파일(6절) · 스키마(7절) · I/O 시점(8절).

---

## 0. 전제

### 0.1 관리 단위 — 모듈 인스턴스

**모듈 인스턴스 = `(모듈, variant, Set)` 3튜플.** 이것이 저장·복사·삭제·분기의 단위다.

| 구분 | 대상 |
|---|---|
| 인스턴스가 되는 것 | Geometry · Condition · AnalysisLauncher · DataPreprocessor · ModelBuilder · ModelRunner · Optimizer |
| variant 를 갖는 모듈 | Geometry(`Morphing` · `CAD`) · AnalysisLauncher(`Init` · `Resample` · `Direct`) · ModelBuilder(`Sim` · `MCU`) · ModelRunner(`Sim` · `MCU`) |
| 인스턴스가 **아닌** 것 | **Results Analyzer** — 호스트 여러 곳에 임베드되는 패널이고 config 파일도 산출 디렉토리도 없다 |
| 인스턴스 **위** 계층 | **Reference**(기준 해석 파일) — 인스턴스 여럿이 공유하므로 프로젝트 레벨에 둔다 (6절) |

현행은 2튜플(`카테고리, Set 이름`)이고 variant 가 **3벌에 병행 보관**된다 — Set 이름 접미사 · JSON `variant` 키 · 트리 항목 `Qt::UserRole+2`. 읽는 자리마다 서로 다른 기준을 본다.

### 0.2 무엇이 문제인가 — 현황 8건

이 설계가 고치려는 것이다. **앞의 여섯은 안 α 와 안 β 가 공유하고 뒤의 둘이 안 β 의 고유 축이다**(0.3). 전부 `dev` @ `4c7608e` 실측이다.

| # | 현황 | 결과 |
|---|---|---|
| 1 | **프로젝트 매니페스트가 없다.** 프로젝트를 열 때 `configs/*.json` 을 글로빙해 **파일명 접두사로 모듈을 판정**한다(`DashProject::loadSetsFromConfigs()` `model/DashProject.cpp:1066-1211`) | 프로젝트의 정체성이 폴더 이름 + 파일명 집합이다. **파일명이 곧 스키마**다 |
| 2 | **정의와 실행 상태가 한 파일에 있다.** `{Module}_{Set}.json` 안에 설정 · 실행상태 · 산출물포인터가 섞여 있고 AnalysisLauncher 는 4성분이다 | 실행이 정의를 덮는다 — DOE 재실행 시 `DOE Table` 통째 교체, 재학습 시 고정 경로 덮어쓰기. **실행 1회를 가리키는 표현이 없어** 이력이 남지 않고, 상태 전이 1회마다 정의 파일 전문을 재직렬화해 총 I/O 가 케이스 수의 **제곱**이다 |
| 3 | **외부 도구가 같은 파일을 되쓴다.** `ModelBuilder_{Set}.json` 의 경로가 학습 도구의 CLI 인자이고, 도구가 끝나면 그 파일의 `status` 를 `"Done"` 으로 바꾼다. GUI 는 1초 타이머로 되읽는다(`DashModelBuilder.cpp:1364`) | 요청과 응답이 같은 파일 하나를 통과하는 양방향 채널이라 **라이터를 GUI 한 곳으로 줄일 수 없다**. 근거 3중 — `"Done"` 을 쓰는 C++ 코드 0건 · `DashModelBuilder.cpp:1420-1421` 주석이 "도구가 쓴 `Done` 은 건드리지 않는다" 로 적음 · 1초 폴링과 방어 구조 자체가 그 전제 위에 있음 |
| 4 | **산출물 대장이 없다.** 산출물 포인터는 `AnalysisLauncher.DOE Table.input/output` 과 `DataPreprocessor.DOE Table.output` **2곳뿐**이고 나머지는 디스크 스캔(`*.dat` · `*.inp` 글로빙)으로 찾는다 | 스캔 필터와 생성 시 경로가 어긋난다. 자산 · 부산물 · 실패를 구분하지 못한다 |
| 5 | **상위 선택이 기록되지 않거나 읽히지 않는다.** "이 Set 은 어느 모델 기준인가" 를 적는 키가 일부 모듈에 아예 없고, 있는 곳도 **읽는 코드가 0곳**이거나 절대경로 문자열이다(4절) | 프로젝트를 다시 열면 상위 바인딩이 복원되지 않아 사용자가 매번 다시 고른다 |
| 6 | **상위가 바뀐 것을 소비자가 알 자리가 없다.** 산출이 무엇의 어느 판으로 만들어졌는지 적는 자리가 어느 파일에도 없다 | 상위 정의 수정 · 상류 재실행 · 기준 파일 교체가 하류 화면에 흔적을 남기지 않아 **사용자가 낡은 결과를 최신으로 읽는다** |
| 7 | **루트가 셋이고 배정 규칙에 답하는 자리마다 답이 다르다**(0.3 근거 2) — `ModuleType` enum 주석 · `getModuleDir()` · `isUserOutputType()`(호출부 0곳) · MCU 우회 | 한 인스턴스의 데이터가 3루트에 흩어져 **"무엇을 함께 버려야 하는가" 가 아무 데도 적히지 않는다.** `deleteSet` 이 config JSON 1개만 지우는 것이 그 결과다. **안 β 의 고유 축** |
| 8 | **조인 키가 전부 사람이 읽는 문자열이다**(4.3) — 파일명 접두사 · Set 이름 접미사 · 파라미터 이름 · 알고리즘 이름 · 디렉토리명에 박힌 점수 | 이름의 소유자가 GUI 가 아니라 rename 을 막을 수 없고, 같은 알고리즘을 두 응답에 쓰지 못하는 제약이 사용자 경고문으로 노출된다(`DashModelBuilderWidget.cpp:809-812`). **안 β 의 고유 축** |

### 0.3 레이아웃 — 안 α 와 안 β

현행 저장 위치는 **루트가 셋**이다.

| 루트 | 경로 | 들어가는 것 |
|---|---|---|
| 숨김 설정 | `{Root}/.{Project}.dproj/configs/` | `{Module}_{Set}.json` 전 9종 + Morphing `.vtp` + 복사된 `.dat` · `.prt` |
| 숨김 산출 | `{Root}/.{Project}.dproj/ModelBuilder_{Set}/` | ModelBuilder **Sim** 산출물만 |
| 사용자 루트 | `{Root}/` | 나머지 전 모듈 산출 + ModelBuilder **MCU** 산출 + `[Add File]` 원본 |

| 축            | 안 α — 현행 3루트 유지, 파일 추가                    | 안 β — 인스턴스 = 자기완결 디렉토리                   |
| ------------ | ----------------------------------------- | ---------------------------------------- |
| 물리 배치        | `configs/` 에 실행·인덱스 파일을 나란히 추가, 산출물은 현 위치 | `{Root}/{Module}_{Set}/` 안에 정의·실행·산출물 전부 |
| 마이그레이션       | 불요                                        | 기존 자산 모두 폐기                              |
| 경로 규약 불일치    | 남는다                                       | **소멸** — 루트가 하나라 규칙 자체가 없어진다             |
| Set 삭제·분기·이동 | 파일 3\~4개 + 디렉토리 추적                        | 디렉토리 1개 조작                               |
| 숨김 경계        | 유지                                        | **상실** — 정의 JSON 이 사용자에게 보인다             |
| 착수 비용        | 소\~중                                      | 대                                        |

**채택: β.** 근거 셋.

1. **버릴 것의 목록을 디렉토리가 대신한다.** α 는 한 인스턴스의 데이터가 3루트에 흩어진 채 남아 "무엇을 함께 버려야 하는지" 가 아무 데도 안 적힌다.
2. **경로 규약 불일치는 루트가 셋이라 생겼다.** "어느 모듈 산출물이 숨김으로 가고 어느 것이 사용자 루트로 가나" 에 답하는 자리가 다섯인데 서로 다른 답을 낸다 — `ModuleType` enum 주석은 ModelBuilder 와 Optimizer 둘 다 숨김이라 하고, `getModuleDir()` 구현은 ModelBuilder 만 숨김이며(`DashIOController.cpp:31`), `isUserOutputType()` 은 Optimizer 를 제외하고(`:106-112`, **호출부 0곳**), MCU 는 `getModuleDir()` 자체를 우회한다(`DashModelBuilderMCU.cpp:554-562`). 규칙을 고치는 것보다 루트를 하나로 줄이는 것이 싸다.
3. **숨김 상실은 손실이 아니다.** 탐색기로 열어보는 실무 관행이 이미 있고, β 는 그것을 정식화한다 — 폴더 안에 사람이 읽는 정의 JSON 이 있다. **단 폴더명은 읽히지 않는다** — 3.1 이 디렉토리명을 ID 로 확정했으므로 탐색은 GUI 의 [폴더 열기]에서 출발한다. 근거 1·2 만으로 β 가 서고 이 근거는 대가에 대한 반박이므로, 축소를 그대로 수용한다.

### 0.4 실제 추가 · 변경되는 것

**파일 — 순수 이동은 하나뿐이다.** 이것이 9절이 마이그레이션을 미수행으로 정한 근거다 — 옮길 것이 `handles.vtp` 하나인데 이관 코드를 짤 이유가 없다.

| 구분 | 대상 |
|---|---|
| **추가** | `.dproj/project.json`(PM) · `{인스턴스}/definition.json`(SM) · `executions/{label}/execution.json`·`input.json`(EM) · `{인스턴스}/view.json`(칸 밖) · `references/`(PB) · `.dproj/cache/`(칸 밖) |
| **이동** | `handles.vtp`(SB) — **유일한 순수 이동** · 2루트에 흩어진 산출 전량 → `executions/{label}/`(레벨 +1) · 등록 원본과 `configs/` 복사본 2벌 → `references/` 1벌 |
| **분해** | `configs/{Module}_{Set}.json` 4종이 칸 2\~4개로 갈린다 — AnalysisLauncher 4칸 · DataPreprocessor 3칸 · ModelBuilder 2칸(Sim·MCU 각각) |
| **폐기** | `configs/` 디렉토리 · `.dproj/{Module}_{Set}/` 숨김 산출 루트 · `AIGeometryGeneration_{Set}.json` · 리더 0곳인 `DOE Analysis`·`Data Analysis` 블록 |

**코드 — 전환 셋을 합친 것보다 신설이 많다.**

| 갈래 | 건수 | 성격 |
|---|---|---|
| 경로 조립 | 10 | 함수 소멸 · 분기 소멸 · 인자 교체. 기계적이다 |
| 조인 키 | 7 (1 미결) | **가장 크다** — 함수 교체가 아니라 자료구조 교체여서 영향이 호출부 전체로 퍼진다 |
| 수명 조작 | 4 | 가장 작다. 넷의 방향이 서로 다르다 — 범위 확대 · 축소 · 폐기 · 신설 각 1 |
| 신설 배선 | 15 | **읽기 배선**이고 SM 11 · EM 2 · 칸 밖 1 · SB·SM 택일 1. 자리를 만드는 칸(PM · EM)과 어긋난다 |

**현황 8건의 판정.**

| # | 현황 | 안 β |
|---|---|---|
| 1 | 프로젝트 매니페스트가 없다 | **닫힌다 — 매니페스트가 아니라 고정 파일명 + 자기신고로.** 이름이 의미를 담지 않게 되어 모듈·variant 판정이 전부 `definition.json` 내용에서 나온다. `project.json` 은 Reference 대장으로 남고 인스턴스를 색인하지 않는다 (7.2) |
| 2 | 정의와 실행 상태가 한 파일에 있다 | **닫힌다** — 4성분이 4칸으로 갈리고, 실행마다 별 파일이라 상태 전이가 정의를 재작성하지 않는다 (규약 5 · 6) |
| 3 | 외부 도구가 같은 파일을 되쓴다 | **닫힌다 — 단 도구를 함께 릴리스해야 한다.** 규약 9 가 도구의 쓰기를 EB 안에 가둔다. 전송 요구 2건이 도구 측 인계다 (10절 2 · 3번) |
| 4 | 산출물 대장이 없다 | **닫힌다 — 요청 단위로.** `artifacts[]` 는 실행이 요청한 산출만 담고 GUI 가 경로를 조립하는 자리에서 기록한다. 자산·부산물 구분은 여집합 규칙이 한다 (7.4). 부산물의 개별 추적과 정리 UI 는 범위 밖이다 (9절) |
| 5 | 상위 선택이 기록되지 않거나 읽히지 않는다 | **자리는 닫히고 배선이 남는다** — `upstream` 3키가 자리이고, 사용자가 체감하는 결함은 읽기 배선 15건이 붙어야 닫힌다 |
| 6 | 상위가 바뀐 것을 소비자가 알 자리가 없다 | **닫힌다** — `bound` 지문 + 착수 시 `consumed` 고정 + 배지 6종 (5.2 · 5.3). 지문 재계산 트리거와 `handles.vtp` 의 스냅샷 처분은 미결이다 (8.3.4-6 · 8) |
| 7 | 루트가 셋이고 배정 규칙이 어긋난다 | **닫힌다** — 규칙을 고치는 것이 아니라 규칙이 필요 없게 만든다 (0.3 근거 2) |
| 8 | 조인 키가 전부 사람이 읽는 문자열이다 | **닫힌다 — 전환 비용이 가장 큰 축이다.** ID 도입은 필드 추가가 아니라 키 교체다 (4.3 · 7.1) |

**대가 넷.** 기존 프로젝트를 열 수 없고(9절 마이그레이션 미수행), 상대경로가 약 16자 늘며(10절 1번 — Windows `MAX_PATH` 잔여 예산 약 190자), 숨김 경계가 사라지면서 **폴더명이 ID 라 사람이 읽지 못하고**(3.1 · 0.3 근거 3), 도구를 GUI 와 함께 릴리스해야 한다.

### 0.5 표기

| 표기                         | 뜻                                                                                                                      |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `MOR-D5` · `RUN-D34` 같은 코드 | 기존 조사에서 매긴 **결함 번호**다. 본 문서는 근거로만 인용하고 전수 대응은 하지 않는다                                                                   |
| 축 A\~G                     | 매니페스트 부재로 귀속된 결함 69건의 7분류. 본 문서와 관계된 것은 **B**(파일명·경로가 스키마 노릇) · **E**(산출물 대장 부재) · **G**(설정 JSON 의 쓰기 주체·시점 규약 부재) 셋이다 |
| `dev` @ `4c7608e`          | 실측 기준 커밋                                                                                                               |

---

## 1. 재단 — 귀속 3 × 종류 2

| 귀속       | 라이터                                      | **메타** — 구조화 · 가변 · 단일 라이터                         | **벌크** — 불투명 · 파일마다 write-once          |
| -------- | ---------------------------------------- | -------------------------------------------------- | --------------------------------------- |
| **프로젝트** | 프로젝트 컨트롤러                                | `.dproj/project.json`                              | `references/*.inp` · `*.prt` · `*.wbpj` |
| **Set**  | GUI — SM 은 인스턴스 스토어 1곳 (7.3)           | `{인스턴스}/definition.json`                           | `{인스턴스}/handles.vtp`                    |
| **실행**   | EM 은 착수시킨 GUI 컨트롤러 · EB 는 그 실행이 부린 솔버·도구 | `executions/{label}/execution.json` · `input.json` | 케이스 산출물 · `*.pt` · `*.xml` · `*.vtu`    |

여섯 칸이 전부 채워진다. 프로젝트·Set 귀속은 메타와 벌크의 라이터가 같지만 **실행 귀속만 라이터가 갈린다** — EM 은 GUI 가 쓰고 EB 는 솔버·외부 도구가 직접 쓴다. 그래도 "칸마다 라이터 1곳" 은 성립한다. **칸마다 하나면 되지 귀속마다 하나일 필요는 없고**, 규약 9 가 도구의 쓰기를 EB 안에 가두는 것이 그 성립 조건이다.

| 코드   | 칸              | 코드   | 칸       |
| ---- | -------------- | ---- | ------- |
| `PM` | 프로젝트 메타        | `PB` | 프로젝트 벌크 |
| `SM` | Set 메타         | `SB` | Set 벌크  |
| `EM` | 실행 메타          | `EB` | 실행 벌크   |

---

## 2. 규약

**아래 11개는 기본값이지 불변 규칙이 아니다.** 구현 중 규약끼리 부딪히거나 규약이 실제 요구를 막는 자리가 나오면, 예외를 덧대 규약을 형식만 살리기보다 그 자리를 근거로 적고 규약 자체를 고친다. 규약 3 이 이미 예외를 하나 달고 있다

| #   | 규약                                      | 적용 · 이유                                                                                        |
| --- | --------------------------------------- | ---------------------------------------------------------------------------------------------- |
| 1   | **칸마다 라이터 1곳**                          | 6칸 전부. 0.2-3 의 양방향 채널이 이 규약의 유일한 예외였고 규약 9 가 그것을 없앤다                                           |
| 2   | **메타 쓰기는 원자적** (temp + rename)          | 메타 3칸. 현재 워커 스레드에서 락 없이 전문을 통째로 쓴다                                                             |
| 3   | **벌크는 파일마다 라이터 1곳 + 생성 후 불변**           | 벌크 3칸. 예외 1건 — `handles.vtp` 는 사용자 편집으로 재저장된다                                                  |
| 4   | **인덱스는 같은 칸의 메타가 가리킨다**                 | `project.json.references[].files` · `definition.json` 의 페이로드 참조 · `execution.json.artifacts[]` |
| 5   | **실행 중에는 Set 메타를 쓰지 않는다**               | 실행이 정의를 덮는 경로(0.2-2)를 구조적으로 없앤다                                                                |
| 6   | **실행 메타 쓰기는 해당 실행 파일 하나만 건드린다**         | 전문 재기록 금지. 현재는 상태 전이 1회마다 DOE JSON 전량을 재작성해 케이스 수에 **제곱으로** 커진다                                |
| 7   | **정리 대상은 벌크뿐**                          | 메타는 영구 보존                                                                                      |
| 8   | **재생성 가능하거나 소실을 허용하는 것은 칸의 정본에 넣지 않는다** | `.dproj/cache/` · `derived` · `view.json`                                                      |
| 9   | **쓰기는 담당 칸 아래로만 미친다**                    | **주체를 가리지 않는다** — GUI 든 외부 도구든 같다. 벌크는 말단 도구가 생산하는 것이 정상이고, 그 도구는 자기 실행의 EB 를 쓰되 **EM · SM · SB · PM · PB 는 건드리지 않는다.** 상태·진행 보고는 파일이 아니라 stdout |
| 10  | **읽기는 진입 1회 + 통지**                      | 폴링 금지. 현재 ModelBuilder 1초 타이머와 진입 1회에 3번 호출되는 로더가 있다                                           |
| 11  | **Set 메타 쓰기는 dirty 신호 + 디바운스**          | 양극단이 다 틀렸다 — "Run 눌러야 저장"(누르지 않고 나가면 전부 소멸)도, "셀 편집 1회 = 파일 쓰기 1회" 도 아니다                       |

규약 4 가 **산출물 포인터를 정의 파일에 역기입하던 문제**의 일반형이다. 포인터는 같은 칸의 메타에 있고 대상은 벌크에 있다. 이 진술이 귀속 셋 전부에 걸린다.

규약 9 가 규약 1 을 전 모듈에서 성립시킨다. **문제는 도구가 파일을 쓰는 것이 아니라 자기 칸 위를 쓰는 것이었다** — 0.2-3 의 학습 도구는 EB(`*.pt` · `model_info.json`)를 내면서 **SM**(`ModelBuilder_{Set}.json`)의 `status` 를 함께 되썼다. 쓰기 범위를 담당 칸 아래로 자르면 칸마다 라이터가 하나로 남고, 대용량 산출을 파일로 주고받는 관행(8.2)은 그대로 유지된다.

**가르는 선은 주체가 아니라 대상이다.** 주체로 가르면 3절이 `optimum.json` 을 도구 생산 EB 로 둔 것과 8.2 의 "대용량 산출을 파일로" 판정이 함께 무너진다.

---

## 3. 배치

레이아웃은 0.3 의 **안 β** — 모듈 인스턴스 하나 = 자기완결 디렉토리 하나.

**디렉토리명은 인스턴스 ID 다.** 아래 도면의 오른쪽 열이 `모듈 · variant · "라벨"` 이고 그 정본은 `definition.json`(7.3)이다 — 이름에는 아무 값도 박히지 않는다.

```
{ProjectRoot}/
   .{Project}.dproj/
      project.json                        PM  Reference 대장 — references[] (인스턴스는 색인하지 않는다)
      cache/                              --  파생 캐시 · 삭제 무해
   references/                            PB  역할 맵이 가리키는 실체 (6절)
      bracket_v3.inp                          role deck
      spring.prt                              role part
      spring.wbpj                             role template

   inst_7f3a2c1b04de/                         GeometryParameter · Morphing · "Set1"
      definition.json                     SM  upstream + DV-Geometry · Morphing.*
      handles.vtp                         SB  핸들 배열 11종
   inst_c3d80a17be42/                         GeometryParameter · CAD · "Set2"
      definition.json                     SM  upstream + Independent/Dependent Parameter
                                          SB  없음 — 입력 .prt 는 references/ 로 승격되고
                                              형상 산출 .stp 는 케이스마다 나오므로 EB 다
   inst_1e55da62c9f7/                         ConditionParameter · "Set1"
      definition.json                     SM  upstream + DV-Condition + Value 오버레이

   inst_4d19b2a70e55/                         AnalysisLauncher · Init · "Set1"
      definition.json                     SM  upstream + DOE configuration
      view.json                           --  RA 축·색·스타일. 선택 · 없으면 default
      executions/
         20260809-140233/
            execution.json                EM  consumed · params · cases · artifacts
            input.json                    EM  정의 스냅샷 — 착수 시 고정, 이후 불변
            doe_table_part1.csv           EB
            runs1/ ... runs80/            EB  케이스 디렉토리 — 현행 이름 유지
               runs1.dat | runs1.stp      EB  형상 산출. Morphing 은 .dat · CAD 는 .stp
               runs1.inp                  EB  솔버 입력
               runs1.odb  runs1.prt ...   EB  솔버 결과 + 부산물
               logs/                      EB
         20260805-093118/                     동형. analysisType 이 다르면 별 실행이다

   inst_2a6f95c10db3/                         DataPreprocessor · "Set1"
      definition.json                     SM  upstream + Output Response · KPI
      executions/20260811-101507/
         execution.json   input.json      EM
         *.xml                            EB

   inst_8b14ef7205ca/                         ModelBuilder · Sim · "Set1"
      definition.json                     SM  upstream + Data Label · Configuration
      executions/20260812-163044/
         execution.json                   EM  라이터 GUI 1곳 — 도구는 EM 을 쓰지 않는다
         input.json                       EM  재현성 기록. 도구에는 stdin 으로 직접 전달
         model_info.json                  EB  순수 벌크 · 도구 생산 (status 는 stdout 으로 온다)
         *.pt                             EB
         rendered_results/*.vtu           EB
   inst_5d92c6a3f0e1/                         ModelBuilder · MCU · "Set1"
      definition.json                     SM  upstream + Data Label.Dataset 배열
      executions/20260812-171230/
         execution.json   input.json      EM
         *.h                              EB  인코딩된 C 헤더

   inst_e07b3419d85f/                         ModelRunner · Sim · "Set1"
      definition.json                     SM  upstream + Model upload
      executions/20260813-090012/
         execution.json   input.json      EM
         {base}.dat  {base}.vtu  *.csv    EB
   inst_a4f18d60b2c7/                         ModelRunner · MCU · "Set1"
      definition.json                     SM  upstream — ModelBuilder MCU 실행 + 모델 지목
      executions/20260813-094510/
         execution.json   input.json      EM
                                          EB  현행 없음 — 예측 결과가 stdout JSON 으로만 오고
                                              파일로 남지 않는다 (`DashModelBuilderMCU::testModel1D`).
                                              남길지는 10절 7번

   inst_36ba9e5c14f0/                         Optimizer · "Set1"
      definition.json                     SM  upstream + Optimization
      executions/20260814-224501/
         execution.json   input.json      EM
         optimum.json                     EB  도구 생산 · GUI 4곳 읽기
         optimization_log/*.png           EB
```

### 3.1 배치 규칙

| 항목 | 규칙 |
|---|---|
| 모듈 어휘 | **현행 유지** — `GeometryParameter` · `ConditionParameter` · `AnalysisLauncher` · `DataPreprocessor` · `ModelBuilder` · `ModelRunner` · `Optimizer`. 정본은 `getModuleName()`(`DashIOController.cpp:61`)과 `ModuleType` enum 이다. 개명은 이득이 없다 — enum 과 그 분기 전부를 건드리면서 **조인 키를 하나도 없애지 못한다.** 이 문서가 산문에서 "Geometry" · "Condition" 으로 줄여 부르는 것은 약칭이고 디렉토리명·`module` 필드 값이 아니다 |
| 인스턴스 디렉토리명 | **`inst_` + 12-hex — ID 그 자체다.** 이름에 모듈 · variant · 라벨을 담지 않는다. 현행은 기본 variant 가 무접미사(Morphing · Init · Sim)라 비대칭이고 그 비대칭이 곧 variant 판정의 폴백이다 — `detectBuilderVariant` 는 JSON `variant` 키가 없으면 `setName.endsWith("-MCU")` 로 판정하고 아니면 `Sim` 을 반환한다(`DashProject.cpp:658-702`). 이름을 대칭으로 고치는 것이 아니라 **파싱할 이름을 없앤다** |
| 실행 라벨 | `YYYYMMDD-HHMMSS`. Windows 파일명에 `:` 가 불가하므로 시각 구분자를 쓰지 않는다. 조인 키가 UUID 이므로 라벨이 겹쳐도 정합성은 깨지지 않고 디렉토리명 충돌만 접미사로 피한다. 사용자 라벨은 `execution.json.label` 에 두고 **디렉토리는 rename 하지 않는다** |
| `analysisType` | 디렉토리 레벨이 아니라 **실행 파라미터**. 한 번의 실행은 타입 하나를 돈다(`DashJobRunner.cpp:1124` 의 `m_currentAnalysisType` 이 단수). 현행 경로 `{ModuleDir}/{analysisType}/{runId}` 의 중간 레벨이 사라진다 |
| 케이스 디렉토리 | `runs{K}` **현행 유지**. `DOE Table.input` 값에 `"runs1/runs1.dat"` 로 박혀 있고 솔버 로그·외부 도구도 그 이름을 쓴다 |
| Set rename | **`definition.json.label` 만 바꾼다.** 디렉토리는 건드리지 않는다 — 이름이 ID 이므로 라벨과 무관하다. 실행 라벨과 같은 규칙이다 |

**Results Analyzer** 는 자기 디렉토리를 갖지 않는다. 자기를 띄운 모듈 인스턴스 디렉토리에 `view.json` 을 **필요할 때만** 만들고, 없으면 default 를 적용하며 그때까지의 편집분은 버린다. 소실 허용이므로 칸의 정본이 아니다(규약 8).

**AI Geometry Generation** 은 배치에서 뺀다 — `model/DashAIGeometryGeneration.cpp` 50줄 전체에 read · write · save · load 가 **0줄**이고 `m_configJsonPath` 는 경로를 조립해 `qDebug()` 로 찍기만 한다(`:41-43`). 생산자도 소비자도 없어 파일이 만들어지지 않는다.

---

## 4. 각 칸의 실체

"현재 실체" 는 `dev` @ `4c7608e` 실측이다. 비어 있는 칸이 신설 대상이다.

| 칸 | 신 자리 | 현재 실체 | 상태 |
|---|---|---|---|
| **PM** | `.dproj/project.json` | **없다.** 프로젝트 열기가 `configs/*.json` 을 글로빙해 파일명 접두사로 모듈을 판정하고 variant 는 3단 폴백(`DashProject.cpp:1088-1210` · `:621`) | 전량 신설 |
| **PB** | `references/` | `[Add File]` 원본은 사용자 루트, 복사본 `.dat` · `.prt` 는 `configs/` 안 — **2벌** | 이동 + 역할 맵 신설 |
| **SM** `upstream` | `definition.json` 의 블록 | **키 4개 실재** — `DataPreprocessor.Dataset.Selected DV-Table` · `Selected Analysis File`(둘 다 리더 0곳) · `AnalysisLauncher.DOE configuration.Selected Design Variables` · `ModelRunner.Model upload.Output Response[].set`. ModelBuilder · Optimizer 는 키 자체가 없다 | **자리는 있고 리더가 없다.** 값을 ID 로 바꾸고 지문 추가 |
| **SM** 본문 | `definition.json` | `configs/{Module}_{Set}.json` 9종 — `DV-Geometry` · `DV-Condition` · `Independent/Dependent Parameter` · `Morphing.*` · `DOE configuration` · `Data Label` · `Configuration` · `Model upload` · `Optimization` | 정상. `$schema` · 신원 5필드(`id` · `module` · `variant` · `label` · `created`) · 안정 ID 추가 |
| **SB** | 인스턴스 디렉토리 | `configs/GeometryParameter_{Set}.vtp` — 핸들 배열 11종. 생산자 GUI 1곳 · 소비자 2곳 | 이동만 |
| **EM** | `executions/{label}/` | **독립 파일 0개.** 전부 Set 메타 파일에 섞여 있다 — `DOE Table.samples[].status*` · `Configuration.*.status` · `.error` · `model_info.models[].status` | 분리 + `cases[].reason` · `cases[].stages[]` 신설(**현재 파일 표현 자체가 없는 2건**) + `models[]` 재구성 — 조각이 `Configuration.{model}` · `model_info.models[]` · 디렉토리명에 흩어져 있다 |
| **EB** | 실행 디렉토리 | 케이스 입력·결과 · `*.xml` · `*.pt` · `*.vtu` · `doe_table_{base}.csv` · `optimum.json` · `optimization_log/*.png` · `model_info.json` | 이동. **인덱스가 2곳뿐**이라 나머지는 디스크 스캔 |

### 4.1 실행 메타는 성질이 둘로 갈린다

| 성질 | 실체 | 라이터 | 쓰기 시점 |
|---|---|---|---|
| 착수 시 고정 — 이후 불변 | `input.json`(정의 스냅샷) · `execution.json.consumed`(계보 스냅샷) | GUI | 착수 1회 |
| 실행 중 갱신 | `execution.json.cases` · `.artifacts` | 실행 소유자 | `cases` 는 전이마다 · `artifacts` 는 **요청 시점** — GUI 가 경로를 조립할 때 한 줄. 종결 시 디렉토리를 훑지 않는다 (7.4) |

### 4.2 확장자로 칸을 판정할 수 없다

같은 확장자가 두 칸에 동시에 있다. 축 E(자산 · 부산물 · 실패를 구분하지 못한다)의 실물이다.

**요청 단위 대장이 이 모호성을 판정 문제에서 빼낸다.** `kind` 는 스캔 결과를 분류한 값이 아니라 **요청 시점에 GUI 가 붙이는 라벨**이고, Abaqus restart `.prt` 같은 부산물은 애초에 대장에 들어오지 않는다. 구분은 여집합 규칙이 한다 (7.4).

| 확장자 | PB · 입력 | EB · 케이스 산출 |
|---|---|---|
| `.prt` | NX 파트 (`[Add File]` 등록분) | **Abaqus restart parts file** — `DashJobRunner.cpp:1163` 의 산출물 진단 필터 `{"*.log","*.msg","*.sta","*.dat","*.prt","*.com","*.rec","*.txt","*.json"}` 에 포함 |
| `.dat` | Ansys deck | Morphing 형상 산출 · Abaqus 부산물 |

CAD 경로는 `.prt` 를 만들지 않는다 — `updatePrtGeometry {prtPath} {stpPath}`(`DashSolverNxCad.cpp:159`)가 **하나의 `.prt` 를 읽어 케이스마다 다른 `.stp` 를 낸다.** `StpBatch` 에서 `prtPath` 는 배치당 필드 1개이고 `stpPath` 는 `StpCase` 마다다(`DashJobRunner.h:139-152`). 산출 위치는 `{runKey}/{runKey}.stp`(`:2322-2324`). 그래서 CAD 케이스는 형상 생성과 해석 2단계이고, Morphing 쪽 대응물은 `runs{K}.dat` 다.

### 4.3 이름에 값이 박혀 있는 자리 3곳

| 자리 | 현행 | 처리 |
|---|---|---|
| 학습 모델 디렉토리 | `{response}/{model}_{score}/` — 예 `Max_Mises/StableNet_0.57455868/`. 코드가 `{modelName}_*` 글로빙으로 찾는다(`DashModelRunner.cpp:2306-2312`) | 점수는 `execution.json.models[]` 의 값이 되고 조회는 글로빙이 아니라 모델 ID 가 한다 (7.4) |
| 학습 후보 키 | `Configuration.{model}` — 알고리즘 이름이 키다. 그래서 **같은 알고리즘을 두 응답에 쓸 수 없고**, 코드가 그 제약을 "현재 구조" 라고 자기 입으로 적는다(`DashModelBuilderPresentationModel.cpp:369-386` · `DashModelBuilderWidget.cpp:811-812`) | 모델의 정체가 `(rsp, reduction, algo)` 3튜플이 되고 키는 모델 ID 다 (7.4) |
| Set 이름 접미사 | variant 판정의 폴백(`DashProject.cpp:658-702`) | **접미사가 사라진다** — 디렉토리명이 ID 이고 판정은 `definition.json.variant` 가 한다. 라벨도 이름이 아니라 필드다 (3.1 · 7.3) |

---

## 5. 엣지 — 모듈 간 의존

### 5.1 엣지 3종

가리키는 칸이 다르면 다른 엣지다. **정의를 소비하는 엣지와 산출을 소비하는 엣지가 다르다**는 것이 핵심이다. 현행은 둘 다 파일명 문자열이거나 폴더 스캔이라 구분이 없고, 그래서 "이 데이터셋이 **어느 실행**에서 나왔는가" 를 적을 자리가 없다.

| 엣지 | 소비자 → 생산자 | 가리키는 것 |
|---|---|---|
| **reference** | 모든 모듈 → Reference | 프로젝트 메타의 Reference ID |
| **definition** | AnalysisLauncher → Geometry · Condition | 다른 인스턴스의 ID |
| **execution** | DataPreprocessor → AnalysisLauncher · ModelBuilder → DataPreprocessor · ModelRunner·Optimizer → ModelBuilder | 다른 인스턴스의 실행 ID. 학습 모델을 지목할 때는 `(실행 ID, 모델 ID)` 2단 |

**execution 엣지만 2단이다.** ModelRunner 와 Optimizer 는 한 학습 실행이 낸 모델 여럿 중 하나를 골라야 한다 — 실행을 고르고 그 안의 모델을 다시 고른다. 현행은 그것을 `Model upload.Output Response[]` 의 `{set(절대경로), response, model}` 문자열 3개로 한다.

여기의 **"2단" 은 지목 단계**이고 7.3 의 **"3단 수식" 은 문자열 마디 수**(`inst_` / `exec_` / `mdl`)다. 세는 대상이 다르므로 숫자가 어긋나 보여도 모순이 아니다.

### 5.2 저장 규칙 5개

| # | 규칙 | 이유 |
|---|---|---|
| 1 | **엣지는 소비자가 소유한다** | 생산자는 자기 소비자를 모른다 — 라이터를 늘리지 않는다 |
| 2 | **역방향("누가 나를 쓰는가")은 저장하지 않고 로드 시 계산한다** | 저장하면 두 자리를 동기화해야 하고 그 자체가 새 정본 이중화다 |
| 3 | **엣지는 ID 를 가리킨다** | 경로 · 파일명 · Set 이름을 가리키지 않는다. 경로는 어느 파일에도 저장하지 않고 열기 시 `*/definition.json` 스캔으로 얻는다(7.2). 이 한 줄이 축 B(파일명이 스키마 노릇) 와 절대경로 복사 · rename 시 디렉토리 미추종을 함께 없앤다 |
| 4 | **바인딩 시점의 지문을 함께 적는다** — reference · definition 엣지만 | 엣지 값만으로는 stale 을 판정할 수 없다. execution 엣지는 제외한다 — 재실행하면 새 ID 가 나오므로 같은 ID 가 다른 내용을 가리키는 일이 없고, 실행이 변하는 유일한 방향인 벌크 정리는 해시가 아니라 존재 조회로 잡힌다 |
| 5 | **실행 착수 시 엣지를 해석해 실행 메타에 고정한다** | 이후 정의가 바뀌어도 그 실행의 계보는 변하지 않는다 |

**규칙 5는 execution 엣지에도 걸린다.** 지문을 붙이지 않는 것(규칙 4)과 ID 를 고정하지 않는 것은 별개다. 전처리 실행은 때마다 다르기 때문이다 — `Done` 인 케이스만 데이터셋에 담으므로(`DashDataProcessor.cpp:3039-3043` → `statusForRunKey :3016`), **같은 정의 · 같은 상위 DOE 로 두 번 돌려도 그 사이 실패 케이스를 재실행했으면 샘플 수가 다른 XML 이 나온다.** 착수 시점에 박아 두지 않으면 정의를 나중에 다른 실행으로 옮겨 가리켰을 때 과거 학습의 계보가 조용히 바뀐다. 고정 자리는 `execution.json.consumed.executions[]` 다(7.4).

### 5.3 무효화 판정

**엣지를 저장하는 진짜 이유는 복원이 아니라 무효화 계산이다.**

```
판정 입력 = definition.json 의 upstream 엣지
          + reference · definition 엣지 → 가리킨 대상의 현재 지문
          + execution 엣지 → 대상 실행 디렉토리의 존재 + 그 실행 대장 항목의 파일 존재 조회
          + 로컬 ID 존재 확인 → 가리킨 dv · rsp 가 아직 있는가
          + 해당 인스턴스의 실행 존재 여부
   ▼
판정 출력 = Set 배지 6종
          Empty · Draft · Ready · Complete · Stale · Broken
```

이것이 없으면 잘못된 상위가 선택돼 있어도 화면상 아무 표시가 없다. **엣지의 값이 아니라 엣지와 지문의 조합이 사용자에게 주는 답이다** — "지금 보이는 이 결과가 최신 정의로 만들어진 것인가". 지문은 stale 을 잡지만 삭제된 항목은 못 잡으므로 로컬 ID 존재 확인이 따로 든다.

`upstream` 의 하위 키를 모듈별 이름이 아니라 **엣지 종류별 공통 키**로 두는 이유가 이것이다(7.3). 판정이 모듈 분기 없이 세 배열을 순회하면 끝난다.

### 5.4 파이프라인 의존 그래프

```
[PM] Reference
   │   references/ 의 파일 묶음 (6절의 역할 맵)
   │   Geometry · Condition · AnalysisLauncher · ModelRunner 가 reference 엣지로 참조
   ▼

[SM] Geometry 정의    Condition 정의
   │   정의만 있고 실행이 없는 모듈이라 실행 칸이 비어 있다
   │   AnalysisLauncher 가 definition 엣지로 참조
   ▼

[EM] AnalysisLauncher 실행
   │   케이스별 해석 입력·결과가 EB
   │   DataPreprocessor 가 execution 엣지로 참조
   │   "어느 DOE 실행인가" 가 여기서 처음 표현된다
   ▼

[EM] DataPreprocessor 실행
   │   *.xml 이 EB
   ▼

[EM] ModelBuilder 실행
   │   학습 산출물이 EB — 실행마다 별 디렉토리라 재학습이 이전 것을 덮지 않는다
   ▼

[EM] ModelRunner 실행    Optimizer 실행
       파이프라인 말단. Optimizer 후보해를 ModelRunner 로 되돌리는 현재의 수동 왕복은
       새 ModelRunner 실행의 upstream 에 optimizer 실행을 얹는 것으로 표현된다
```

---

## 6. Reference — 입력파일

### 6.1 1급 개체로

**Reference = 사용자가 `[Add File]` 로 등록하는 기준 해석 파일.** Morphing 이면 `.inp` · `.dat`, CAD 면 `.prt` + `.wbpj`.

현행은 이것이 데이터 모델 안에 없다. 좌측 Project Tree 는 파일시스템 뷰이고 `[Add File]` 은 파일을 폴더로 복사하는 것뿐이다. 파싱 결과는 메모리 해시에만 있고 활성 대상은 항상 1개이며 그 경로는 어디에도 직렬화되지 않는다. 그래서 프로젝트를 다시 열면 "이 Geometry Set 은 A.inp 기준" 이라는 사실이 복원되지 않고 사용자가 매번 다시 고른다(0.2-5).

**인스턴스 위 계층에 두는 이유**: 인스턴스 여럿이 같은 Reference 를 공유한다 — Geometry Set1 과 Set2 가 같은 `.inp` 를 볼 수 있다. Set 하나가 소유할 수 없으므로 프로젝트 레벨에 둔다.

**이름을 `Reference` 로 잡은 이유**: 기존 식별자(`referenceFile` · `refFile`)와 UI 라벨("Input Reference File" · "Add Reference File")이 전부 이 뜻이고, "기준" 은 형식 중립이라 FE·CAD 양쪽을 담는다. 대안은 전부 오염돼 있다 — 단독 `model` 은 MVC 계층과 대리모델이 차지했고 **화면에 뜨는 "Model" 은 거의 전부 대리모델**이며, `deck` 은 `.prt`·`.wbpj` 를 담지 못하고, `input` 은 세 뜻으로 갈려 있다(기준 해석 파일 / DOE 케이스 입력 / 학습 입력 변수).

### 6.2 파일 1개 ≠ Reference 1개 — 역할 맵

| 경로 | 파일 | 역할 |
|---|---|---|
| Morphing | `.inp`(또는 `.dat`) 1개 | 형상 + FE 조건 + 해석 템플릿 **3역 겸직** |
| CAD | `.prt` + `.wbpj` 2개 | 형상 / 해석 템플릿 분리 |
| FE-safe | + `.stli` 템플릿 + Material | 템플릿 보조 |

그래서 Reference 레코드는 경로 문자열 하나가 아니라 **역할 → 경로 맵**이다. `deck` · `part` · `template` · `material` 은 **역할 이름**이고 엔티티 이름이 아니다. 현행은 이 구분이 `input_files[]` 의 `{name, target_component, path}` 와 확장자 분기에 흩어져 있다.

### 6.3 복사본이 정본

`[Add File]` 은 이미 프로젝트 루트로 복사하고 있다. 이를 규약으로 승격한다 — **프로젝트 안의 복사본이 정본이고 원본은 참조하지 않는다.** 원본이 사라지거나 경로가 바뀌어도 프로젝트가 돈다.

원본 갱신은 **자동 반영하지 않는다.** 지문 불일치를 `⚠ Stale` 로 표시한 뒤 사용자가 명시적으로 [다시 가져오기] 를 눌렀을 때만 복사한다. 자동 동기화를 하지 않는 이유는 **기준 해석 파일 교체가 하위 산출물 전부를 무효화**하기 때문이다 — 그 판단을 파일 타임스탬프에 맡길 수 없다.

### 6.4 전역 활성 컨텍스트의 처분

현행은 활성 해석 모델 1개가 모듈 간 암묵 채널이다 — Condition 은 대상 deck 을 자기가 고르지 않고 전역을 따르며 Geometry 도 마찬가지다. `upstream.reference` 를 두면 **모듈마다 자기 모델을 갖고 전역이 필요 없어진다.**

단 구분이 필요하다. 렌더 뷰는 하나라 "지금 화면에 무엇이 떠 있나" 는 여전히 세션 상태다.

| 구분 | 대상 |
|---|---|
| 프로젝트에 저장 (`upstream`) | 인스턴스의 상위 바인딩 — 이 Set 은 어느 모델 기준인가 |
| 세션 전용 (저장 안 함) | 화면에 렌더된 대상 · 트리 선택 · 카메라 · 스크롤 |

현행은 이 둘이 같은 변수를 써서 **화면 조작이 데이터 결합을 바꾼다.** 프리뷰 1회가 전역 활성 컨텍스트를 갈아끼우고 복구하지 않는 결함(OPT-D18)이 그 극단이다.

### 6.5 프로젝트 밖에 남기는 것

솔버 실행 경로는 머신 전역 설정에 그대로 둔다 — 환경이지 프로젝트 자산이 아니다. 다만 프로젝트는 **필요한 솔버 종류**를 Reference 의 `solver` 에 적는다. 그러면 다른 PC 로 옮겼을 때 "Abaqus 경로가 필요한데 미설정" 을 화면에서 말할 수 있다.

---

## 7. 스키마

> 아래 키 이름 · 중첩 · ID 접두사는 **계약이 아니다.** 다만 마이그레이션을 하지 않기로 했으므로(9절) 첫 배포 후에는 바꿀 수 없다 — 배포 전에 확정한다.

공통 규칙 둘. ID 규칙은 분량이 있어 7.1 로 뺀다.

| 항목 | 값 |
|---|---|
| `$schema` | **1** 부터. 마이그레이션이 없어 현행 형식과 이어지지 않으므로 새로 센다 |
| 상태 어휘 | **5종 고정** — `Pending` `Running` `Done` `Failed` `Cancelled`. 정본은 코드의 `DashStageState` 다. 현행은 어휘가 9종으로 흩어져 있다(`In Progress` · `Success` · `Enqueued` · `Interrupted` 등) |

### 7.1 ID 체계

**가르는 기준은 발급 시점에 라이터가 대상 집합 전체를 손에 쥐고 있느냐다.** 쥐고 있으면 순번을 셀 수 있고 아니면 난수여야 한다.

| ID | 발급 시점의 라이터 | 전체 집합을 보는가 | 구분 |
|---|---|---|---|
| `ref_` | 프로젝트 컨트롤러 · 입력파일 추가 | 예 — `project.json.references[]` 전량 | 전역 |
| `inst_` | 프로젝트 컨트롤러 · Set 생성 | **아니오** — 인스턴스 목록은 어느 파일에도 없다 | 전역 |
| `exec_` | GUI · 실행 착수 | **아니오** — 실행 목록은 어느 파일에도 없다 | 전역 |
| `dv` · `rsp` | GUI · 정의 편집 | 예 — 자기 `definition.json` 안 | 로컬 |
| `mdl` | 실행 소유자 | 예 — 자기 `execution.json` 안 | 로컬 |

**`ref_` 만 발급처가 전체를 본다** — PM 이 `references[]` 를 들기 때문이다. 나머지 둘은 난수여야 하고 근거가 같다 — **발급이 다른 칸을 건드리지 않게 하는 것.** `exec_` 를 순번으로 하려면 `nextExecId` 를 Set 메타에 둬야 해서 8절의 "실행 착수 = SM 읽기만" 이 깨지고, `inst_` 를 순번으로 하려면 PM 이 인스턴스 목록을 들어야 해서 7.2 의 색인 폐기가 깨진다. **난수를 쓰는 근거는 유일성이 아니다.** `ref_` 는 순번도 가능하지만 형식을 전역끼리 맞춘다(아래). 반대로 `mdl` 을 전역으로 올릴 이유는 없다 — 발급처가 `execution.json` 하나이고 규약 6 이 그 안의 카운터를 안전하게 만든다.

항목 ID 를 로컬로 두는 이유는 **Set 분기**다. 8절이 분기를 `definition.json` 복사로 정의했는데 항목 ID 가 전역이면 사본이 원본과 같은 ID 를 갖는다 — 분기마다 DV ID 를 전량 재발급하고 Dependent Parameter 수식 · Value 오버레이의 내부 참조를 수선해야 해서 복사가 더 이상 복사가 아니게 된다. 로컬이면 `(inst, dv)` 쌍이 자동으로 갈리므로 `id` 한 줄만 갈아끼우면 된다. 대신 지운 번호를 재사용하지 않도록 컨테이너가 단조 카운터를 갖는다.

**형식** — 전역은 `접두사_` + 12-hex, 로컬은 접두사 + 순번(밑줄 없음). 모양만 보고 전역·로컬이 갈린다.

| 형식 | 비트 | 항목 10⁴개 충돌 확률 | `inst_` 포함 문자 수 |
|---|---|---|---|
| 6-hex | 24 | 약 16% | 11 |
| **12-hex** | 48 | 약 2×10⁻⁷ | 17 |
| 전체 UUID | 122 | 0 | 41 |

`QUuid::createUuid().toString(QUuid::Id128).left(12)` 로 만든다 — Qt 네이티브라 새 의존성이 아니고 레포에 `QUuid` 사용 0건이라 첫 사용이다. v4 UUID 의 버전 니블 `4` 는 13번째 hex 자리이므로 앞 12자는 전부 난수다. 전체 UUID 를 안 쓰는 이유는 이 값이 `bound` 키이자 수식 참조의 앞자리이자 로그 본문이기 때문이다 — 40자는 grep 은 되지만 읽히지 않는다.

**참조는 항상 수식한다.**

| 참조 | 형태 | 수식하는 이유 |
|---|---|---|
| 로컬 ID | `"inst_7f3a2c1b04de/dv3"` | **유일성.** Geometry 와 Condition 이 각자 카운터를 돌리므로 둘 다 `dv1` 을 갖고, AnalysisLauncher 의 `headers` 에는 양쪽이 섞여 들어온다 |
| `exec_` | `"inst_4d19b2a70e55/exec_b27c9153ae80"` | **소재확인.** `project.json` 은 실행을 색인하지 않으므로 맨 ID 로 파일을 찾으려면 `*/executions/*/execution.json` 전량을 열어야 한다 — 0.2-4 가 없앤 디스크 스캔과 같은 병이다 |

Set 분기가 로컬 수식을 한 번 더 못박는다 — 사본이 원본과 같은 `dv3` 을 갖는 것이 정상이고, 구분은 `inst_` 앞자리가 한다. `exec_` 는 전역 유일이라 맨 ID 로 로그에 찍혀도 모호하지 않다.

**실행을 거쳐 온 로컬 ID 는 그 실행의 `input.json` 에서 해석한다.** `rsp` 는 DataPreprocessor 정의가 발급하는데 ModelBuilder 는 그 정의를 execution 엣지로 본다. 그 사이 정의가 바뀌어 `rsp2` 가 삭제되거나 `label` 이 바뀔 수 있다. `input.json` 이 전 모듈에 존재하는 이유(7.4)가 여기서 두 번째 용도를 갖는다.

**ID 를 주지 않는 것** — 빠진 게 아니라 의도적 부재다.

| 대상 | 대신 쓰는 키 | 이유 |
|---|---|---|
| `artifacts[]` 항목 | `path` | 실행 디렉토리 안에서 파일시스템이 유일성을 보장한다 |
| 케이스 | `runs{K}` | DOE 샘플 인덱스에 의미가 있고 3.1 이 현행 유지로 확정 |
| Reference 역할 | `deck` · `part` · `template` · `material` | 6.2 의 고정 어휘. 엔티티가 아니다 |
| 스테이지 | `stp` · `solve` | 고정 어휘 |
| 학습 후보 | `input.json` 안의 순번 | 불변 스냅샷이라 순번이 이미 안정 키다 |

**구현 주의 — ID 는 직렬화 시점이 아니라 행 구조체에 산다.** `DashDataProcessorPresentationModel.cpp:119-127` 은 저장할 때마다 `Output Response` 배열을 `ResultRow{component, loadStep, name, kpiData, hasKpi}` 에서 전량 새로 만든다. 여기 그대로 ID 를 얹으면 저장마다 새 ID 가 나와 하위 참조가 끊긴다 — 안정 ID 스킴이 깨지는 1순위 경로다. DV 는 더 크다. 이름이 곧 JSON 키라(`dvGeometry.keys()` 가 파라미터 이름을 준다, `DashOptimizer.cpp:1289`) `dv` 도입은 필드 추가가 아니라 **키 교체 + `label` 신설**이고, 이름으로 조인하는 하위 모듈 배선을 함께 바꿔야 한다.

### 7.2 `project.json` — PM

```json
{
  "$schema": 1,
  "created": "2026-08-09T11:20:00+09:00",
  "references": [
    { "id": "ref_9b41e0c3f2a1", "label": "Bracket v3", "kind": "fe", "solver": ["Abaqus"],
      "files": { "deck": "references/bracket_v3.inp" },
      "origin": "C:/work/bracket_v3.inp",
      "fingerprint": "sha256:9b41e0…",
      "derived": { "parts": ["PART-1"], "nsets": ["FIX", "LOAD"] } }
  ]
}
```

| 필드 | 규약 |
|---|---|
| `files` | **프로젝트 상대경로.** 프로젝트를 옮겨도 깨지지 않는다. 키는 6.2 의 역할 이름이다 |
| `origin` | 출처 기록. **해석에 쓰지 않는다** — 없어도 프로젝트가 돈다 |
| `fingerprint` | 정본은 파일이고 stale 판정은 이 값이 한다 (6.3) |
| `derived` | 파싱 결과 **캐시.** 칸의 정본이 아니다(규약 8). 콤보를 채우려고 매번 재파싱하는 현재 동작(진입 시 1\~20초 프리즈, RUN-D5)의 대안 |

**PM 은 Reference 대장이고 인스턴스를 색인하지 않는다.** PM 에 남을 자격은 하나다 — **인스턴스가 소유할 수 없는 것.** Reference 는 인스턴스 여럿이 공유하므로(6.1) 그 기준을 통과하고, 인스턴스의 신원은 인스턴스 자신이 담을 수 있으므로 통과하지 못한다. 신원의 정본은 `definition.json`(7.3)이고 열거는 열기 시 `*/definition.json` 스캔이다.

**스캔은 0.2-1 의 글로빙과 다르다.** 그 병은 글로빙 자체가 아니라 **이름으로 판정**하는 것이었다 — `configs/{Module}_{Set}.json` 의 접두사가 모듈을 정하고 Set 이름 접미사가 variant 를 정했다. `definition.json` 은 고정명이고 그것을 담은 디렉토리명은 ID 라(3.1) 판정이 전부 파일 내용에서 나온다.

색인을 두지 않아 얻는 것 셋.

- **동기화 자리가 없다.** Set 생성 · 분기 · 삭제 · rename 이 PM 을 건드리지 않으므로(8절) 유령 항목도 미등록 디렉토리도 생길 수 없다.
- **디렉토리가 온전히 자기완결이다**(0.3 안 β). 복사해 넣으면 그대로 인스턴스이고 지우면 그대로 사라진다.
- **PM 손상의 피해가 Reference 로 한정된다.**

읽기 비용은 늘지 않는다 — 8절이 프로젝트 열기를 **SM 전량 읽기**로 이미 확정했다(배지 계산에 `upstream` 이 필요하다). `inst_` → 경로 맵은 그 읽기에서 메모리로 파생된다.

**대가 2건.** 정의 파일이 손상된 인스턴스는 신원을 알 수 없다 — 디렉토리명이 ID 라 이름으로 추정할 것도 없으므로(3.1) `inst_` 와 함께 "정의를 읽을 수 없는 인스턴스" 로만 표시한다. 그리고 표시 순서의 정본이 없어 `created` 로 정렬한다.

**`inst_` 이 가리키는 것은 모듈 인스턴스다**(0.1 의 관리 단위). `definition.json` 은 그 안의 파일 하나이고, 인스턴스는 정의가 편집돼도 같으며 삭제하면 실행까지 함께 사라진다. ID 가 정의 파일을 가리키는 것으로 읽히면 Set 분기에서 재발급을 빠뜨린다. 엣지 이름은 `definitions` 그대로 둔다 — 그 구분은 대상 종류가 아니라 **무엇을 보느냐**(정의 / 실행)이고, `"definitions": ["inst_7f3a2c1b04de"]` 는 "이 인스턴스들의 정의를 참조" 로 읽힌다.

### 7.3 `definition.json` — SM

```json
{
  "$schema": 1,
  "id": "inst_4d19b2a70e55",
  "module": "AnalysisLauncher",
  "variant": "Init",
  "label": "Set1",
  "created": "2026-08-09T11:20:00+09:00",

  "upstream": {
    "reference":   "ref_9b41e0c3f2a1",
    "definitions": ["inst_7f3a2c1b04de", "inst_1e55da62c9f7"],
    "executions":  [],
    "bound": {
      "ref_9b41e0c3f2a1":  "sha256:9b41e0…",
      "inst_7f3a2c1b04de": "sha256:1c07af…",
      "inst_1e55da62c9f7": "sha256:44b2d0…"
    }
  },

  "DOE configuration": {
    "headers": ["inst_7f3a2c1b04de/dv1", "inst_1e55da62c9f7/dv4"],
    "method": "Optimal LHC"
  }
}
```

**인스턴스 신원의 정본이 이 파일이다** — `id` · `module` · `variant` · `label` · `created` 다섯. PM 이 이것을 색인하지 않고(7.2) 디렉토리명은 ID 라 아무 값도 담지 않으므로(3.1) 정본이 한 벌이다. `variant` 3벌 병행 보관(0.1)이 여기 한 벌로 접힌다.

**라벨을 필드로 두는 이유는 파일명 규칙이다.** 디렉토리명을 라벨로 쓰면 사용자가 보는 문자열에 `\ / : * ? " < > |` 금지 · 예약어(`CON` · `PRN` · `AUX` · `NUL`) 회피 · 후행 마침표 금지 · 모듈 안 유일성이 걸린다. 라벨에 걸 계약이 아니다. 실행 라벨이 이미 같은 규칙이다 — 디렉토리는 `YYYYMMDD-HHMMSS` 이고 사용자 라벨은 `execution.json.label` 이다(3.1 · 7.4).

**대신 SM 라이터를 인스턴스 스토어 1곳으로 모아야 한다.** 라벨이 필드이므로 프로젝트 트리의 rename 과 모듈 위젯의 정의 편집이 같은 파일을 쓴다. 둘이 각자 쓰면 lost update 가 난다 — rename 이 파일을 고친 뒤 디바운스(규약 11)가 만료되면 위젯이 rename 이전 라벨을 담은 전문을 덮어쓰고, 규약 2 의 원자적 쓰기는 파일 찢김만 막고 전문 재기록끼리의 덮어쓰기는 막지 못한다. 한 문으로 모으면 성립하지 않는다. 규약 1 이 원래 요구하는 것이고 실행 칸이 이미 그 형태다.

**`upstream` 의 하위 키는 엣지 종류별 공통 키다** — 모듈별 이름(`design_space` · `dv_table` · `model_source` …)을 쓰지 않는다. 5.1 이 엣지를 reference · definition · execution 3종으로 나눴으므로 그 구분이 곧 키다. 모듈별 이름은 읽기는 쉽지만 판정 코드를 모듈 수만큼 갈라 놓는다.

`bound` 는 5.2-4 의 지문 맵이고 **키는 `ref_` 와 `inst_` 뿐이다.** execution 엣지는 지문을 갖지 않는다. 전역 ID 에 접두사를 유지하는 실질 근거가 이것이다 — 타입이 섞인 맵이라 키 접두사가 곧 판정 분기다.

**`upstream` 은 파생 요약이고 정본은 모듈 블록이다.** 어느 DV 를 쓰는지는 `DOE configuration.headers` 가 정하고, `upstream.definitions[]` 는 거기서 `inst_` 앞자리만 뽑아 **저장 시 재생성**한다. 사람이 두 자리를 맞출 일이 없으므로 이중화가 아니다. 그러면서 판정은 모듈 스키마를 몰라도 되고, 사람은 파일 맨 위에서 이 인스턴스가 무엇에 매달려 있는지 한눈에 본다 — **기계와 사람 양쪽에 추적이 가장 쉬운 형태**가 이것이다. "세 배열 순회로 판정이 끝난다" 는 그 결과이지 지켜야 할 규칙이 아니다.

**모델 지목은 3단 수식이다.** `mdl` 의 소유자가 `exec_` 이고 `exec_` 의 소유자가 `inst_` 이므로, 7.1 의 "로컬 ID 는 소유자로 수식한다" 를 두 번 적용하면 그대로 나온다.

| 층 | `dv` | `mdl` |
|---|---|---|
| `upstream` 배열 — 파생 요약 | `definitions[]` = `"inst_7f3a2c1b04de"` | `executions[]` = `"inst_…/exec_…"` |
| 모듈 블록 — 정본 | `DOE configuration.headers` = `"inst_7f3a2c1b04de/dv1"` | `Model upload.Output Response[].model` · `Optimization.trained_surrogate_model[].model` = `"inst_…/exec_…/mdl3"` |

별 키 `upstream.models[]` 를 만들지 않는 이유는 **문자열 하나가 소유 사슬 전체를 담기 때문**이다 — `/` 로 쪼개면 기계가 읽고 그대로 grep 하면 사람이 역추적한다. 지목을 두 필드로 쪼개면 둘을 함께 옮겨야 하는 자리가 생긴다.

블록 이름을 `upstream` 으로 둔 근거: 후보 중 유일하게 **방향**을 담고 충돌이 없다. 5.2-2 가 역방향을 저장하지 않기로 했으므로 이름이 방향을 말하는 것이 맞다. `input` 은 3중 충돌(6.1), `source` 는 DV 의 `source` 문자열(`"Morphing|part1.dat|COMPONENT-1"`)이 점유, `parent` 는 실행 계보에 이미 쓰였다.

**DV · Response 는 안정 ID 를 갖는다** — 키가 로컬 ID(`dv3` · `rsp2`)이고 사람이 붙인 이름은 `label` 이다. 이름을 키로 쓸 수 없는 이유는 rename 이 아니라 **소유권**이다. DV 이름의 소유자는 사용자가 아니라 Reference 이고 — Morphing 은 이름이 아예 없다(핸들 이름이 트리 아이템과 세션 `QMap` 에만 있다, MOR-D5) — 원본 파일의 파라미터 이름이 바뀌면 GUI 가 막을 수 없다. ID 가 있으면 행을 유지한 채 `source` 만 다시 매핑해 소비자 참조를 살린다.

**`dv` 네임스페이스는 variant 를 가로지른다.** CAD 설정은 `DV-Geometry` 와 `Independent Parameter` · `Dependent Parameter` 를 함께 쓰고(`DashGeometryParameterCADPresentationModel.cpp:49-51`) Morphing 은 `DV-Geometry` 만 쓴다. AnalysisLauncher 는 상위가 어느 쪽이든 `headers` 를 같은 방식으로 읽어야 하므로 **DOE 축이 될 수 있는 것은 전부 `dv` 하나의 네임스페이스다.** Dependent Parameter 는 DOE 축은 아니지만 참조 대상은 되므로 같은 네임스페이스에 `kind` 로 구분한다. 쪼개면 5.3 이 없앤 모듈 분기가 DV 층에서 되살아난다. 현행은 섹션 이름부터 흔들린다 — `DashReferenceFileWidget.cpp:585` 는 `{"DV-Geometry", "ConditionParameter"}`, `DashDesignVariableModel.cpp:288-296` 은 `DV-Condition` 이다.

**`rsp` 는 축약 전 물리량이다.** DataPreprocessor 가 XML 열로 낸 것이고 그 열은 스칼라일 수도 필드일 수도 있다(shape `[80,1]` · `[80,1234,3]`, `DashModelBuilder.cpp:352-377`). ModelBuilder 가 거기 거는 reduction(`None`·`Min`·`Max`·`Average`·`Sum`)은 응답의 성질이 아니라 학습 설정이므로 **ModelBuilder 정의가 `(rsp, reduction)` 쌍으로 소유한다.** 근거 셋 — 라이터가 다르고, reduction 옵션 집합이 shape 의 함수이며(`ModelBuilderLabelTableHelper.cpp:246-259`), `None` 이 정당한 선택지라 "축약 후" 개체가 항상 존재하지도 않는다.

**Condition 의 Value 오버레이**도 이 파일에 둔다. Condition 의 Value 인라인 편집은 다른 편집과 성격이 다르다 — **표보다 해석 파일이 먼저 바뀐다.** 즉 정의 편집이 아니라 입력파일 편집인데, 설정 JSON 에 대응 키가 없어 모듈을 떠나면 사라진다(CON-D5). 복사본 파일에 되쓰면 지문이 깨져 6.3 의 stale 판정이 오작동하므로, **`(uuid, entryPtr, value)[]` 오버레이로 정의에 저장하고 export 시점에 적용한다.**

Set 벌크를 갖는 모듈은 정의 안에서 그것을 가리킨다(규약 4).

### 7.4 `execution.json` — EM

```json
{
  "$schema": 1,
  "executionId": "exec_b27c9153ae80",
  "instance": "inst_4d19b2a70e55",
  "label": "",
  "created": "2026-08-09T14:02:33+09:00",
  "parent": "exec_a11f0384dd12",
  "params": { "analysisType": "Static", "method": "Optimal LHC", "n": 80 },

  "consumed": {
    "reference":   { "id": "ref_9b41e0c3f2a1", "fingerprint": "sha256:9b41e0…" },
    "definitions": ["inst_7f3a2c1b04de@sha256:1c07af…", "inst_1e55da62c9f7@sha256:44b2d0…"],
    "executions":  ["inst_2a8c5f019b3d/exec_c40e7a125fb8"]
  },

  "cases": {
    "runs1": { "state": "Done",   "stages": [["stp","Done"],["solve","Done"]] },
    "runs2": { "state": "Failed", "stages": [["stp","Done"],["solve","Failed"]],
               "reason": "ANSYS exit 8: license not available" }
  },

  "artifacts": [
    { "kind": "case_input",  "case": "runs1", "path": "runs1/runs1.inp" },
    { "kind": "case_result", "case": "runs1", "path": "runs1/runs1.odb" }
  ]
}
```

| 필드 | 근거 |
|---|---|
| `cases[].reason` | 케이스 실패 사유. 현재 **어떤 파일에도 없는 데이터**라 재시작하면 소실된다 |
| `cases[].stages[]` | 현재 케이스당 문자열 1개로 평탄화돼 "STP 는 됐는데 해석에서 죽었다" 를 구별하지 못한다. 4.2 가 보인 CAD 의 2단계가 그 예다 |
| `artifacts[]` | **요청 단위 대장** — 아래. 현재 인덱스는 2곳뿐이고 나머지는 디스크 스캔이다(0.2-4). 정의 파일에 역기입되던 `*_datapath` 계열은 현재 `dev` 에 **없으므로**, 이 필드는 이주가 아니라 **신설**이다 |
| `consumed` | 착수 시 엣지를 해석해 고정한다(5.2-5). **`upstream` 의 엣지 3종을 그대로 받는다** — 키가 셋인 이유는 5.2-5 가 "엣지" 라고만 했지 종류를 가리지 않았기 때문이다. `reference` · `definitions` 는 지문을 동반하고 `executions` 는 동반하지 않는다(5.2-4). 모델을 지목한 엣지면 `"inst_…/exec_…/mdl3"` 까지 그대로 옮겨 적는다 |
| `parent` | 이 실행이 파생된 이전 실행. 재샘플링·이어달리기의 계보 |
| `label` | 사용자 라벨(선택). 디렉토리명은 이 값으로 바뀌지 않는다 |

#### `artifacts[]` 는 요청 단위다

**대장에는 실행이 요청한 산출만 들어간다.** GUI 가 경로를 조립하는 그 자리에서 한 줄씩 붙고, 종결 시 디렉토리를 훑지 않는다. 도구가 이름을 정하는 것은 들어오지 않는다.

| 구분 | 예 | 대장 |
|---|---|---|
| GUI 가 경로를 정해 요청한 것 | `runs{K}/runs{K}.inp` · `runs{K}.dat`·`.stp` · 요청한 결과 `.odb` · `*.xml` · `optimum.json` | **들어간다** |
| 도구·솔버가 부수적으로 내는 것 | `.msg` · `.sta` · `.rec` · `logs/` · `optimization_log/*.png` · `rendered_results/*.vtu` | 들어가지 않는다 |

**여집합 규칙 — 대장에 있으면 자산, 실행 디렉토리 안인데 대장에 없으면 부산물.** 이것이 축 E 가 요구한 구분이고, 부산물을 개별 추적하지 않고도 성립한다. 규약 9 가 실행 디렉토리를 그 실행의 배타적 쓰기 범위로 만들어 놓았으므로 여집합이 정의된다.

**요청 단위로 좁히는 값은 배선이 0 이라는 것이다.** GUI 는 이미 그 경로들을 조립하고 있다 — 케이스 디렉토리 · `runs{K}.inp` · `{runKey}/{runKey}.stp`(`DashJobRunner.cpp:2322-2324`). 종결 시 스캔으로 채우면 0.2-4 가 지적한 "스캔 필터와 생성 시 경로가 어긋난다" 를 쓰기 자리로 옮겨 담을 뿐이다. 요청 시점 기록은 어긋날 자리 자체가 없다.

**`purged` 필드를 두지 않는다.** 벌크를 지운 뒤에도 실행 메타는 남으므로(규약 7) "파일이 없는 것이 정상" 인 상태가 생기는데, 그 구별은 필드가 아니라 두 축의 조합으로 파생된다.

| `cases[].state` | `path` | 판정 |
|---|---|---|
| `Done` | 있음 | 정상 |
| `Done` | 없음 | 정리됨 |
| `Failed` · `Cancelled` | 없음 | 실패 · 취소 |

부분 정리(용량이 큰 `.odb` 만 지우고 `.csv` · `logs/` 는 남기기)도 같은 조회로 항목마다 답이 나온다. 정리 여부를 파일에 새기지 않으므로 사용자가 탐색기로 지워도 대장이 어긋나지 않는다.

**`models[]` — ModelBuilder 실행에만 있는 배열이고 `mdl` 의 발급처다.**

```json
"models": [
  { "id": "mdl3", "rsp": "inst_1e55da62c9f7/rsp2", "reduction": "Max",
    "algo": "StableNet", "score": 0.57455868, "dir": "Max_Mises/StableNet_0.57455868/" }
]
```

모델 하나는 **디렉토리 하나**이고 그 안에 `config.yaml` · `*.pt` 등 파일이 여럿이다(4.3). 그 파일들은 도구가 이름을 정하므로 요청 단위가 아니고 `artifacts[]` 에 들어오지 않는다 — **모델의 소재는 `models[].dir` 이 들고 파일 단위 역참조는 두지 않는다.** 모델의 속성(`rsp` · `reduction` · `algo` · `score`)이 갈 자리도 여기서 생긴다 — 4.3 의 "점수는 값으로 들어간다" 가 이 필드다. `dir` 과 `score` 는 도구 보고로 채워진다(10절 2번 R1).

`input.json` 은 착수 시점 정의 본문의 스냅샷이고 **전 모듈에 만든다.** 용도가 둘이다 — 재현성(모듈을 가리지 않는다), 그리고 **실행을 거쳐 온 로컬 ID 의 해석 기준**(7.1). 도구에는 파일 경로가 아니라 내용을 stdin 으로 직접 전달한다(규약 9).

### 7.5 `view.json` — 칸 밖

Results Analyzer 의 축 · 색 · 스타일 · 표시 옵션. 모듈 인스턴스마다 **필요할 때만** 생성하고 없으면 default 를 적용한다. **소실 허용**이므로 칸의 정본이 아니고, 형식을 나중에 바꿔도 옛 파일을 무시하면 된다.

현행은 이 데이터가 호스트 config 의 `DOE Analysis` · `Data Analysis` 블록에 write-only 로 쌓인다 — 플롯을 그리는 코드가 config 경로를 받지만 **존재 여부만 확인하고 내용을 파싱하지 않으며**, 실제 설정은 메모리에서 온다. 즉 파일에 쌓이는 축·색·스타일을 다음 세션에서 아무도 보지 않는다. 그 블록은 **읽기 배선 신설 대상이 아니라 폐기 대상**이다.

---

## 8. 읽기 · 쓰기 · 복사의 시점

| 사용자 행위 | PM | SM | EM | 벌크 |
|---|---|---|---|---|
| 프로젝트 생성 | **쓰기** (Reference 대장 신규 · 빈 배열) | — | — | — |
| 프로젝트 열기 | 읽기 1회 | 읽기 (전량 — 배지 계산에 `upstream` 이 필요하다) | lazy (실행 목록 헤더) | — |
| 입력파일 추가 | **쓰기** (Reference 항목 + 지문) | — | — | **복사** (원본 → `references/`) |
| Set 생성 | — | **쓰기** (디렉토리 생성 + 빈 정의 · 신원 5필드 + 초기 바인딩) | — | — |
| 모듈 진입 | — | 읽기 + **무결성 판정** (5.3) | 읽기 (목록) | lazy (활성 실행만) |
| 상위 선택 변경 | — | **쓰기** (`upstream` 블록) | — | — |
| 정의 편집 | — | dirty → 디바운스 **쓰기** | — | — |
| 실행 착수 | — | 읽기 → `input.json` 스냅샷 · `upstream` 해석 → `consumed` 고정 | **쓰기** (실행 신규 · 전 케이스 `Pending`) | — |
| 실행 중 전이 | — | **쓰지 않음** (규약 5) | **쓰기** (해당 실행 파일만 — 전이 + 요청 시 `artifacts[]` 한 줄) | 생산자가 쓰기 |
| 실행 완료 | — | — | **쓰기** (종결 상태만 — 대장은 요청 시점에 이미 찼다) | — |
| 모듈 이탈 | — | flush | flush | — |
| Set 분기 | — | **복사** + `id` · `label` · `created` 갱신 | 복사 안 함 | Set 벌크만 복사 |
| Set 삭제 | — | 삭제 · 소비자에 `✕ Broken` 반영 | 삭제 | 삭제 (확인 후) |
| Set rename | — | **쓰기** (`label` 만) | — | — |
| 다른 이름으로 저장 | **쓰기** | — | — | **복사** (루트 전량) |
| 원본 파일 변경 감지 | 지문 갱신 **안 함** | 무결성 재계산 → `⚠ Stale` | — | — |
| 벌크 정리 | — | — | **쓰지 않음** — 정리 여부는 존재 조회로 파생 (7.4) | 삭제 |

셋이 따라 나온다.

- **복사는 네 자리에서만 일어난다** — 입력파일 편입 · Set 분기 · 다른 이름으로 저장 · 실행 착수 시 정의 스냅샷. 그 외의 "실행 중 임시 복사" 는 실행 벌크 안에서만 허용된다.
- **Set 분기는 Set 칸만 복사하고 실행 칸은 복사하지 않는다.** 정의는 이어받고 결과는 새로 만든다는 뜻이다.
- **인스턴스 수명 조작 넷이 PM 을 건드리지 않는다** — 생성 · 분기 · 삭제 · rename. 색인이 없으므로(7.2) 앞의 셋은 디렉토리 조작이고 rename 은 SM 필드 하나다. 디렉토리명이 ID 라 rename 이 파일시스템에 닿지 않는다.

### 8.1 "저장" 의 재정의

현행 `SaveProject()` 는 `return true` 한 줄이고 모든 쓰기가 이미 즉시 반영이다 — 메뉴가 있는데 아무 일도 하지 않는다.

**즉시 저장을 계약으로 명문화한다.** `SaveProject` 는 flush + PM 재작성으로 재정의한다. 명시적 저장(편집을 메모리에 두고 Save 에서 일괄 기록)은 **기각**한다 — 실행 산출물이 이미 디스크에 있어서 "저장 안 함" 이 성립하지 않기 때문이다. 벌크는 솔버와 외부 도구가 만들고 GUI 가 되돌릴 수 없으므로, 명시적 저장을 택하면 Set 메타만 트랜잭션이 되고 실행 칸은 아니라서 Save 의 의미가 칸마다 갈린다. **되돌리기가 필요하면 답은 저장이 아니라 실행 누적이다** — 정의는 최신 하나면 충분하고 산출은 이력이 남는다.

`SaveProjectAs` 는 β 레이아웃에서 **프로젝트 루트 전체 복사**가 된다. 현행은 숨김 `.dproj` 만 복사해 사용자 산출물 디렉토리와 원본 모델이 전부 누락되고, config 안 절대경로가 옛 경로를 가리킨 채 복사된다. β + 규칙 5.2-3(엣지는 ID)이면 절대경로가 남지 않아 **복사만으로 성립한다.**

### 8.2 외부 도구와의 경계

**파일로 정보를 주고받는 것 자체는 문제가 아니다.** 문제는 하나의 파일을 두 프로세스가 쓰는 것이고, 그것을 고치는 데 파일 IPC 를 버릴 필요는 없다. 현행 관행을 표준 여부로 가르면 여섯 줄이다.

| 패턴 | 표준인가 | 근거 |
|---|---|---|
| 입력 파일 + `--output-dir` 로 산출 분리 | **표준** | 컴파일러·빌드 도구의 기본형. 이미 부분적으로 하고 있다 |
| 대용량 산출(텐서·메시·결과)을 파일로 | **표준** | 소켓으로 옮길 이유가 없다 |
| 진행·완료를 stdout 줄 단위 JSON 으로 | **표준** | `cargo --message-format=json` · `npm --json` · `docker build --progress` · `ffmpeg -progress` 가 전부 이 형태 |
| 성공·실패를 exit code 로 | **표준** | — |
| **같은 파일을 양쪽이 read-modify-write** | **아니다** | 락 없는 공유 가변 상태. 경쟁 상태이자 소유권 부재 |
| **완료를 파일 폴링으로 감지** | **아니다** | 통지 채널이 없어서 생긴 우회. 지연·누락·부분 읽기가 따라온다 |

앞의 넷은 유지하고 뒤의 둘만 버린다. 지금 `ModelBuilder_{Set}.json` 에 그 둘이 함께 있다 — 도구가 같은 파일의 `status` 를 되쓰고(0.2-3), GUI 가 1초 타이머로 그것을 되읽는다. 나머지 모듈은 config 를 도구에 넘기기만 하고 되쓰기는 없으므로, 실제 수술 대상은 학습 계열 하나다(10절 3번).

**제어와 데이터를 채널로 가른다** — 상태·진행·실패 사유는 stdout, 모델·결과는 파일. 규약 9 가 자르는 것이 이 선이다. 도구는 EB 를 계속 파일로 쓰되 자기 칸 위(EM · SM · PM)로는 손이 가지 않으므로, 프로세스마다 쓰는 파일이 갈리고 규약 1(칸마다 라이터 1곳)이 예외 없이 성립한다.

```
[착수] 실행 디렉토리 생성
   │   1. 정의 본문을 executions/{label}/input.json 으로 스냅샷
   │   2. upstream 을 해석해 execution.json 의 consumed 블록에 고정
   ▼

[실행] 도구에 넘기는 것은 정의 내용 자체 (stdin)
   │   도구는 stdout 으로 보고하고, 산출 벌크만 자기 실행 디렉토리에 쓴다
   │   정의 파일도 실행 메타 파일도 도구 손에 닿지 않는다 (규약 9)
   │   GUI 는 자기가 경로를 정한 산출만 그 자리에서 artifacts[] 에 적는다
   ▼

[종결] GUI 가 execution.json 에 종결 상태 기록 — 디렉토리를 훑지 않는다
       Set 메타는 이 전 구간에 한 번도 쓰이지 않는다
```

얻는 것 셋.

- **Set 메타의 라이터가 GUI 1곳으로 회복된다** — 규약 1 이 전 모듈에 성립하고 0.2-3 의 예외가 사라진다.
- **그 실행이 어떤 정의로 돌았는지가 남는다** — 정의를 나중에 고쳐도 과거 실행이 재현된다.
- **"남은 In Progress 를 Failed 로 마감" 류의 전역 청소가 아예 불필요해진다** — 실행 상태의 정본이 파일이 아니라 프로세스이고, 비정상 종료는 exit code 로 그 자리에서 판정된다.

순서 제약은 남는다 — 도구가 새 계약으로 돌도록 함께 릴리스해야 한다(10절).

### 8.3 사용자 확인과 차단

8절 표가 "그때 무엇이 쓰이나" 라면 여기는 **"그때 무엇을 묻고 무엇을 막나"** 다. 저장 구조가 바뀌면서 **같은 조작의 파괴력이 달라지는 자리**가 있어 함께 정한다.

#### 8.3.1 확정 4건

| 행위 | 정책 | 근거 |
|---|---|---|
| **Set 삭제** | 인스턴스 디렉토리 전체 — **SM · SB · EM · EB 를 모두 지운다.** 실행 이력도 함께 사라진다. 확인 창에 실행 수 · 총 용량 · 소비자 목록을 보인다. 소비자가 있어도 삭제를 막지는 않는다 — 남은 쪽이 `✕ Broken` 이 된다 | β는 인스턴스가 자기완결 디렉토리이므로(3절) 삭제 단위도 디렉토리다. 8절 표의 Set 삭제 행을 확인 절차로 구체화한 것이다. 규약 7(정리 대상은 벌크뿐)은 **사용자가 실행을 정리하는 경우**의 규약이고 인스턴스 폐기에는 걸리지 않는다. 현행은 config JSON 1개만 지우고 산출 디렉토리를 남기므로(`DashProject.cpp:802-820`) 같은 버튼이 훨씬 세진다 — 확인 문구를 함께 고쳐야 하는 이유다 |
| **실행 중 정의 편집** | **읽기전용으로 잠근다.** 해당 인스턴스의 정의 편집 위젯을 착수에 비활성화하고 종결에 푼다 | 규약 5는 실행이 SM 을 쓰지 않는 것이고 8절의 "정의 편집 → 디바운스 쓰기" 는 그 구간에도 SM 을 쓴다. 잠그면 둘이 부딪히지 않는다. 정합성 근거는 아니다 — `input.json` 이 착수 시 고정이라 편집을 허용해도 그 실행은 안전하다. **화면이 말하는 것과 실행이 도는 것을 일치**시키는 것이 이유다 |
| **비정상 종료 후 `Running`** | 재진입 시 **`Failed` 과 동일하게 처리**한다. 프로세스가 없는데 종결 기록이 없으면 실패다. 6번째 상태를 만들지 않는다 | 8.2의 "exit code 로 그 자리에서 판정" 은 도구가 죽는 경우다. **GUI 가 죽으면 판정 주체가 사라진다.** 단 이것은 이번 판의 방편이다 — 8.3.2 |
| **`Stale` 에서 착수** | **허용한다.** `⚠ Stale` 은 착수를 막는 표시가 아니라 재실행을 권하는 표시다. `✕ Broken` 만 막는다 | 8.3.3 |

#### 8.3.2 실행 상태의 최종 방향 — 필드가 아니라 이벤트

비정상 종료를 **필드 마감으로 처리하는 것은 이번 판의 방편**이고 최종 방향은 다르다.

| | 이번 판 | 최종 |
|---|---|---|
| 실행 메타에 쓰는 것 | `cases[].state` 등 **현재 상태** | 일어난 **사건** — append-only 이벤트 |
| 상태를 얻는 법 | 필드를 읽는다 | 이벤트를 되짚어 **역추적**한다 |
| 비정상 종료 | 진입 시 `Running` 을 찾아 `Failed` 로 **쓴다** | 종결 이벤트가 없으면 미종결 — **쓰지 않고 판정만 한다** |

**필드 마감이 방편인 이유는 오판을 파일에 새기기 때문이다.** 도구는 정상 종료했는데 GUI 만 죽은 경우, 필드 방식은 성공한 실행을 `Failed` 로 덮고 그 사실이 남지 않는다. 이벤트 로그는 도구의 마지막 보고가 그대로 남으므로 같은 상황에서 "보고는 여기까지 왔고 종결 기록이 없다" 를 구별한다.

규약과의 관계 셋. 2절이 규약을 기본값으로 두고 부딪히는 자리에서 개정하도록 했으므로 아래는 **개정 후보**다.

| 규약 | 관계 |
|---|---|
| 6 — 실행 메타 쓰기는 해당 실행 파일 하나만 · 전문 재기록 금지 | **강화한다.** append 가 그 규약의 자연스러운 구현이다. 전이 1회에 한 줄이 붙어 파일 크기가 전이 수에 선형이다 |
| 2 — 메타 쓰기는 원자적 (temp + rename) | **부딪힌다.** temp + rename 은 전문 재기록 전제다. append 는 한 줄 단위 원자성으로 같은 목적을 달성하므로 규약을 "쓰기는 원자적" 으로 넓힌다 |
| 7 — 메타는 영구 보존 | 부딪히지 않는다. 이벤트 로그는 메타다 |

전환 시점은 이 문서가 정하지 않는다. 경로를 열어 두는 조건은 하나다 — **상태를 읽는 코드가 필드를 직접 보지 않고 조회 함수 하나를 거친다.**

#### 8.3.3 `Stale` 과 `Broken` 에서의 착수

**`Stale` 에서 실행 착수는 낡은 상위를 끌어다 쓰는 것이 아니라 낡은 결과를 다시 만드는 것이다.** 착수가 `upstream` 을 **그 시점의 현재 상태로** 해석해 `consumed` 에 고정하므로(5.2-5), 실행은 언제나 최신 상위를 읽는다. 새 실행이 최신 지문으로 `bound` 를 갱신하면 배지가 풀린다 — **재실행이 stale 해소의 정규 경로**다.

추가 구현이 없다. 오히려 막는 쪽이 착수 경로에 판정 분기를 하나 더 넣는다.

`Broken` 은 다르다. 가리킨 ID 가 없으면 `consumed` 를 만들 수 없어 착수가 **물리적으로 불가능**하다. 정책이 아니라 불능이므로 버튼을 비활성화하고 끊긴 참조를 문구로 보인다.

**`Stale` 이 두 뜻으로 쓰이고 있다.** 이 절이 말하는 것은 앞의 것이다.

| 주체 | 뜻 | 해소 |
|---|---|---|
| Set 배지 (5.3) | 내 실행 결과가 상위 정의보다 낡았다 | **재실행** |
| Reference (6.3) | 프로젝트 안 복사본이 원본 파일보다 낡았다 | **[다시 가져오기]** — 재실행으로는 풀리지 않는다 |

복사본이 정본이므로(6.3) 뒤의 것은 실행 정합성 문제가 아니다. 같은 배지 문구를 쓰면 사용자가 재실행으로 풀리는 줄 안다 — **문구를 갈라야 한다.**

#### 8.3.4 미결

확정 4건과 같은 층위인데 아직 정해지지 않은 것이다. 10절 잔여가 조사·인계 항목인 데 비해 이쪽은 **결정 항목**이다.

| # | 행위 | 정해야 할 것 |
|---|---|---|
| 1 | **다중 인스턴스** | 같은 프로젝트를 두 창에서 여는 경우. 즉시 저장이 계약(8.1)이면 두 프로세스가 같은 파일을 쓰므로 **규약 1이 성립하지 않는다.** 잠금 파일 · 단일 인스턴스 가드가 현행 레포에 0건이다 |
| 2 | **다른 이름으로 저장** | β에서 루트 전량 복사면 실행 결과 수 GB 가 따라온다. 복사 범위(실행 포함·제외) · 진행 표시 · **대상 폴더 비우기 확인** — 현행 `SaveProjectAs` 는 대상 폴더를 `removeRecursively()` 로 먼저 비운다(`DashProjectManager.cpp:174-176`) |
| 3 | ~~**벌크 정리 단위**~~ — **해소** | `purged` 필드를 폐기하고 정리 여부를 존재 조회로 파생하면서(7.4) UI 단위와 스키마 단위의 어긋남이 없어졌다. 실행 단위로 비우든 `.odb` 만 지우든 같은 조회가 답한다. 남은 것은 정리 UI 와 확인 문구이고 **벌크 관리는 범위 밖**(9절) |
| 4 | **실행 취소** — 후순위 | 어휘에 `Cancelled` 가 있는데 8절 표에 취소 행이 없다. 부분 산출 디렉토리를 남기나. 대장 쪽은 정해졌다 — 요청한 것은 이미 적혀 있고 파일이 없으면 `Cancelled` 와 조합해 파생된다(7.4) |
| 5 | **동시 실행 허용 범위** | 한 인스턴스에서 실행 둘, 모듈 간 동시 실행. 현행은 `"An analysis is already running."` 로 막는다(`DashAnalysisLauncher.cpp:220`) — 그 가드의 존속 여부 |
| 6 | **Reference 지문 재계산 트리거** | 6.3은 원본 변경을 `⚠ Stale` 로 표시하는데 규약 10이 폴링을 금지한다. 프로젝트 열기 1회인지 · 모듈 진입인지 · 수동 확인인지 |
| 7 | **Stale 전파 범위** | 직속 소비자만인지 전이적인지 |
| 8 | **`handles.vtp` 와 실행 스냅샷** | 규약 3의 예외로 재저장되는데 `input.json` 은 "정의 **본문**의 스냅샷" 이라 SB 를 담지 않는다. 핸들을 고치면 과거 실행의 계보가 조용히 어긋난다. 스냅샷에 넣을지 지문만 박을지 |
| 9 | **부분 `Broken` 재바인딩** | 참조 3개 중 1개만 끊긴 경우의 재지목 UI. 무효화 판정과 독립한 별개 작업이므로 **TBU** |
| 10 | **구버전 프로젝트 거부 안내** | 정책은 확정(9절)이나 문구와 대안이 없다. **기존 자산 폐기가 사용자 눈에 처음 보이는 자리**다 |

1 · 2번은 데이터 손실로 직결된다.

---

## 9. 확정 사항

| 축 | 결정 |
|---|---|
| **재단** | 귀속 3 × 종류 2 = 6칸. 층 번호 폐기, 좌표 표기(`PM` … `EB`) 채택 |
| **레이아웃** | 안 β — 모듈 인스턴스 = 자기완결 디렉토리 1개 |
| **PM 의 범위** | **Reference 대장만.** 인스턴스를 색인하지 않고 열기 시 `*/definition.json` 스캔으로 열거한다 — PM 에 남을 자격은 "인스턴스가 소유할 수 없는 것" 하나다. 신원(`id` · `module` · `variant` · `label` · `created`)의 정본은 SM 이고, 그 라이터는 **인스턴스 스토어 1곳**이다 — 트리의 rename 과 위젯의 편집이 같은 문을 통과한다 (7.2 · 7.3) |
| **어휘** | 실행 1회 = `execution`. `run` 은 코드가 케이스 뜻으로 점유하고 있어 쓰지 않는다 |
| **디렉토리명** | **인스턴스 = `inst_` + 12-hex ID 그 자체** · 실행 = `YYYYMMDD-HHMMSS`. 두 층 다 이름에 값을 담지 않고 사용자 라벨은 필드다(`definition.json.label` · `execution.json.label`) |
| **`analysisType`** | 디렉토리 레벨이 아니라 실행 파라미터 |
| **케이스 이름** | `runs{K}` 유지 |
| **ID** | 전역 3종 `ref_` · `inst_` · `exec_` = 접두사 + 12-hex 난수 · 로컬 3종 `dv` · `rsp` · `mdl` = 소유 파일 안 순번. 참조는 항상 수식 (7.1) |
| **`rsp` 의 정체** | 축약 전 물리량. reduction 은 ModelBuilder 정의가 `(rsp, reduction)` 으로 소유 |
| **학습 모델** | `execution.json.models[]` 에서 `mdl` 발급. 소재는 `models[].dir` — `artifacts[]` 역참조는 두지 않는다 |
| **산출물 대장** | **요청 단위.** `artifacts[]` 는 실행이 요청한 산출만 담고 GUI 가 경로를 조립하는 자리에서 기록한다 — 종결 시 디렉토리를 훑지 않으므로 배선이 0 이다. 대장 밖은 부산물이고 개별 추적하지 않는다(**여집합 규칙**). `purged` 필드는 두지 않고 정리·실패·취소 구별은 `cases[].state` × 파일 존재 조회로 파생한다 (7.4) |
| **엣지** | 소비자 소유 · 역방향 미저장 · ID 참조 · 지문 동반(reference · definition 만) · 착수 시 고정 (5.2) |
| **`upstream` 하위 키** | 엣지 종류별 공통 키 (`reference` · `definitions` · `executions` · `bound`) |
| **입력파일** | 역할 맵을 가진 Reference 로 1급화. **복사본이 정본**이고 원본은 `origin` 기록만. 자동 동기화 없음 |
| **도구 경계** | 정의는 stdin 으로 직접 전달, 보고는 stdout. **도구는 자기 실행의 EB 를 쓰되 EM 위로는 올라가지 않는다** — 가르는 선은 주체가 아니라 대상이다 (규약 9) |
| **모듈 어휘** | 현행 유지 — `GeometryParameter` · `ConditionParameter` 등 `getModuleName()` 그대로. 개명하지 않는다 (3.1) |
| **`Selected Analysis File`** | **이름과 달리 값이 해석 타입이다**(`DashDataProcessor.cpp:1224` 가 `m_currentAnalysisType` 을 넣는다). 상위 선택이 아니라 실행 파라미터로 간다 — `execution.json.params.analysisType` |
| **`consumed` 키** | `upstream` 과 같은 엣지 3종 — `reference` · `definitions` · `executions`. 앞의 둘만 지문 동반 (7.4) |
| **`upstream` 의 지위** | **파생 요약**이고 정본은 모듈 블록이다. 저장 시 재생성하므로 이중화가 아니다 (7.3) |
| **모델 지목** | 3단 수식 `"inst_…/exec_…/mdl3"` 을 모듈 블록에 둔다. `upstream.models[]` 를 만들지 않는다 (7.3) |
| **`input.json`** | 전 모듈. 용도는 재현성 |
| **`model_info.json`** | 실행 벌크. 상태는 stdout 으로 오므로 GUI 가 `execution.json` 에 쓴다 |
| **도구 상태 파일** | 만들지 않는다 |
| **저장 동작** | 즉시 저장을 계약으로 명문화. 명시적 저장 모델은 기각 |
| **Set 삭제 범위** | 인스턴스 디렉토리 전체 — SM · SB · EM · EB. 확인 창에 실행 수 · 용량 · 소비자 목록 (8.3.1) |
| **실행 중 정의 편집** | 읽기전용 잠금 (8.3.1) |
| **비정상 종료 실행** | `Failed` 과 동일 처리. 단 이는 방편이고 **최종 방향은 이벤트 append + 상태 역추적** (8.3.2) |
| **`Stale`·`Broken` 착수** | `Stale` 허용 — 재실행이 해소 경로다. `Broken` 은 차단 (8.3.3) |
| **마이그레이션** | **미수행.** 궁극 지향점 우선 — 기존 프로젝트를 열 수 없다는 것을 비용으로 수용한다 |
| **구버전 프로젝트** | 열기 거부 + 안내 1줄. `project.json` 부재를 판정 기준으로 삼고 **폴백 경로를 만들지 않는다** |
| **Set 벌크 칸** | 유지. 현재 `handles.vtp` 하나뿐이지만 폐기하면 그 파일이 갈 곳을 잃는다 |
| **RA `view`** | 인스턴스마다 별 파일 `view.json` · 지연 생성 · 소실 허용 |
| **벌크 관리의 우선순위** | **범위 밖.** 부산물의 개별 추적 · 정리 UI · 부분 정리 조작 · 취소 시 산출물 처분 · MCU 예측 결과 보존 — 재사용 · 편집 · 복사 · 실패 처리에 드는 **고도화**다. **칸과 요청 단위 대장은 지금 만들고 그 위의 관리 기능은 나중에 붙인다.** 요청 단위 대장 자체는 범위 안이다 — 디스크 스캔을 없애는 자리(축 E 8건 · 읽기 배선 15번)라 뒤로 밀면 그 결함이 함께 밀린다 |
| **실행 보존** | 무제한 누적 + **벌크만 수동 정리.** 자동 삭제는 하지 않는다 — 해석 결과 삭제는 되돌릴 수 없고 그 판단을 임계값에 맡길 수 없다. 실행 목록에 총량과 정리 상태를 표시하고 사용자가 실행 단위로 비운다 |
| **AI Geometry Generation** | 배치에서 제외 (미배선) |

---

## 10. 잔여

결정이 아니라 조사 · 인계 항목이다.

| # | 항목 | 내용 |
|---|---|---|
| 1 | **경로 길이 실측** | Windows `MAX_PATH` 260. `{Root}/inst_4d19b2a70e55/executions/20260809-140233/runs1/runs1.inp` 는 현행보다 약 16자 길다 — 디렉토리명을 ID 로 한 것이 사람이 읽는 이름(`AnalysisLauncher_Set1-Init`, 26자) 대비 9자를 회수한 값이다. `analysisType` 을 파라미터로 옮겨 한 레벨을 줄인 것이 상쇄분이다. 솔버(Abaqus · ANSYS)의 작업 경로 제약과 함께 재야 한다 |
| 2 | **도구 계약 — 전송 요구 2건** | 도구 측 구현으로 넘긴다. **R1** 전송 수단이 케이스별 · 스테이지별 전이와 구조화된 실패 사유를 실을 수 있어야 한다 — 현행 토큰 4종(`[READY]` · `[PROGRESS] {n}` · `[FINISHED]` · `[ERROR] {msg}`)은 페이로드를 못 싣는다(`DashExtensionProcess.cpp:404` 가 정확 일치 판정). **R2** 도구의 쓰기가 자기 실행 디렉토리(EB) 안에 머문다 — 정의 파일과 실행 메타를 되쓰지 않는다(규약 9). 요청↔완료 상관관계는 이미 있다 — 한 번에 하나만 미결인 엄격 직렬 큐(`:396-424`) |
| 3 | **도구 변경 범위** | MCU 와 NX 는 이미 stdin/stdout 데몬이다. 실제 변경 대상이 학습 도구(Sim) 하나인지 확인 |
| 4 | **KPI 가 `rsp` 인가 별 타입인가** | 7.3 이 DataPreprocessor 정의를 "Output Response · KPI" 로 적었다. Optimizer 의 목적·제약이 무엇을 가리키는지가 여기 달렸다. 현행 구조는 **속성** 쪽을 가리킨다 — `ResultRow` 가 `kpiData` · `hasKpi` 를 응답 행 안에 갖는다(`DashDataProcessorPresentationModel.h:20-26`) |
| 5 | **MCU Dataset 이 ID 를 갖나** | `Data Label.Dataset` 이 배열이고(`DashModelBuilderMCUWidget.cpp:710`) ModelRunner 가 개별 항목을 지목할 수 있다. 지목한다면 로컬 타입이 하나 더 필요하다 |
| 6 | **Reference 하나에 같은 역할 파일이 둘일 수 있나** | 다부품 어셈블리에서 `.prt` 가 둘이면 6.2 의 역할 → 경로 맵이 깨진다. 깨진다면 `files` 가 배열이 되고 `ref_…/f2` 라는 네 번째 로컬 타입이 생긴다 |
| 7 | **ModelRunner MCU 의 EB** — 후순위 (9절 벌크 관리) | 예측 결과가 stdout JSON 으로만 오고 파일로 남지 않는다(`DashModelBuilderMCU::testModel1D` — 페이로드를 데몬에 보내고 `testModel1DResultReady(success, obj)` 로 받는다). 실행 개체는 성립하므로 EM 은 있고 EB 만 빈다. 결과를 벌크로 남길지가 결정 항목이다. `Data_format.csv`(`DashModelRunnerMCU.cpp:94`)는 사용자가 받는 템플릿이라 프로젝트 자산이 아니다 |

---
