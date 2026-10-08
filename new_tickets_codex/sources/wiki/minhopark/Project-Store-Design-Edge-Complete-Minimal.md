# 엣지 3종 전량 커버 최소안 — 지문과 계보

> 관련 Issue: #239
>
> **이 문서는 단독으로 읽힌다.** 다른 문서를 열지 않아도 스키마 · 엣지 · I/O 시점이 전부 여기 있다.
>
> * [[Project-Store-Design-Alpha-Minimal]] — 이 안의 **출발점**. 매니페스트 최소 도입과 승격은 그쪽 결정을 그대로 받고, **상위가 바뀐 것을 소비자가 아는가** 한 축만 갈린다 — 그쪽은 지문을 전부 빼서 execution 사슬이 디렉토리에서 끝나고 상류 변경이 화면에 드러나지 않는다. 이 문서는 지문 3종과 run 파일로 그 자리를 닫는다(5\~6절)
> * [[Project-Store-Design-Definition-Version-Minimal]] — 이 안에서 **run 파일을 뺀 판**. 지문이 3종에서 정의 1종으로 줄고 그 자리가 계보 파일이 아니라 소비자 SM 안(`upstream.consumed`)이며, 배지가 2종이고 PM 이 `instances[]` 를 갖지 않는다(모듈·variant 는 config 자기신고). 5.2 가 "실행 `rev` 를 SM 으로 옮기지 않는" 근거 넷을 댄 자리에서 그 안은 **정수 카운터 자체를 버리고 정의 블록 지문**을 쓴다 — 실행 상태가 SM 에 남는 한 카운터는 쓰기 트리거라 상태 전이마다 오르지만 내용 지문은 움직이지 않는다. 지불하는 축은 하나, **정의 무변경 재실행을 하류가 모른다**(이 안 5.2 의 산출 `rev` 가 닫던 것). 그 대신 **계보를 직속이 아니라 조상 전량으로 든다** — 6.3 이 전파를 하지 않는 근거로 든 "산출 `rev` 는 상류의 상위가 바뀌었다고 오르지 않는다" 가 그쪽에는 없으므로, 조상 전량을 `consumed` 에 담지 않으면 상위 정의 변경이 하류에 영구히 닿지 않는다
> * [[Project-Store-Design-Dependency-State-Display]] — 이 안의 **화면 층**. 6.3 배지 6종과 6.2 엣지 표를 화면 어디에 어떻게 띄우는가를 3층(모듈 트리 아이콘 · 우측 독 스트립 · 착수 차단)으로 가른다. 저장에 더하는 필드가 0 이고 판정 규칙도 바꾸지 않는다
>
> 실측 기준: `dev` @ `4c7608e`. 빌드·실행 검증 없음, 정적 근거만.

> ## ⚠ 문서 상태: 구상 — 확정 아님
>
> 팀 합의 전 · 착수 승인 전. 여기의 키 이름을 계약으로 인용하지 않는다.

## 개요

**엣지 3종이 전부 파일에 닿고, 그 대상이 바뀌면 소비자가 아는 것**이 이 안의 목표다. 현행 3루트를 그대로 두고 파일 2종을 더해, 지금 파일명·접미사·디스크 스캔이 하던 판정을 그 파일들이 대신하게 한다.

- **`.dproj/project.json`** — 엣지가 가리킬 엔티티(기준 해석 파일 · 모듈 인스턴스)의 색인
- **`.dproj/outputs/{inst}.json`** — 인스턴스마다 하나, **덮어쓰기**. 그 인스턴스의 **현재** 산출 · 그 산출이 무엇의 **몇 번째 판**으로 만들어졌는지

**두 축이 다른 안과 갈린다.**

1. **최소 실행 추적** — 실행을 개체로 두지 않고(실행 ID 없음 · 이력 없음 · 재실행은 덮는다) **단조 정수 `rev`** 로 "그 산출이 몇 번 덮였는가" 만 기록한다. execution 엣지가 디렉토리가 아니라 파일에서 끝난다.
2. **지문 3종** — 엣지가 가리킨 것이 바뀌었는지를 **셋 다** 판정한다. 기준 해석 파일 · 정의 · 산출이 각각 다른 방식으로 지문을 갖고, 판정은 하나의 비교로 끝난다(5.2).

**버전은 엣지가 아니라 계보가 든다.** `upstream` 은 "무엇에 매달려 있나"(순수 ID)이고, run 파일의 `consumed` 는 "이 산출이 무엇의 몇 번째 판으로 만들어졌나"(ID@지문)다. 배지는 뒤엣것과 현재를 비교해서 나온다 — 소비자가 알아야 하는 것이 "내 바인딩이 낡았나" 가 아니라 **"지금 보이는 이 결과가 최신 상위로 만들어진 것인가"** 이기 때문이다.

---

## 0. 전제

### 0.1 문제 인식 — 현황 8건

**앞의 여섯은 두 안이 공유하고 뒤의 둘은 이 안이 범위 밖으로 둔다**(0.3 · 10절). 전부 `dev` @ `4c7608e` 실측이다.

| # | 현황 | 결과 |
|---|---|---|
| 1 | **프로젝트 매니페스트가 없다.** 프로젝트를 열 때 `configs/*.json` 을 글로빙해 **파일명 접두사로 모듈을 판정**한다(`DashProject::loadSetsFromConfigs()` `model/DashProject.cpp:1066-1211`) | 프로젝트의 정체성이 폴더 이름 + 파일명 집합이다. **파일명이 곧 스키마**다 |
| 2 | **정의와 실행 상태가 한 파일에 있다.** `{Module}_{Set}.json` 안에 설정 · 실행상태 · 산출물포인터가 섞여 있고, AnalysisLauncher 는 4성분이다 | 실행이 정의를 덮는다. **실행 1회를 가리키는 표현이 없어** 재실행이 같은 경로를 덮고 이력이 남지 않는다. 상태 전이 1회마다 정의 파일 전문을 재직렬화해 총 I/O 가 케이스 수의 제곱이다 |
| 3 | **외부 도구가 같은 파일을 되쓴다.** `ModelBuilder_{Set}.json` 의 경로가 학습 도구의 CLI 인자이고 도구가 그 파일의 `status` 를 `"Done"` 으로 바꾼다. GUI 는 1초 타이머로 되읽는다(`DashModelBuilder.cpp:1364`) | 요청과 응답이 파일 하나를 통과하는 양방향 채널이라 라이터를 GUI 한 곳으로 줄일 수 없다 |
| 4 | **산출물 대장이 없다.** 인덱스는 `AnalysisLauncher.DOE Table.input`/`output` 과 DataPreprocessor `output` **2곳뿐**이고 나머지는 디스크 스캔이다 | 스캔 필터와 생성 시 경로가 어긋난다. 자산 · 부산물 · 실패를 구분하지 못한다 |
| 5 | **상위 선택이 기록되지 않거나 읽히지 않는다.** 자리가 없는 모듈 둘 · 있지만 리더가 0곳인 모듈 하나 · 절대경로 문자열로 적는 모듈 하나(5.5) | 프로젝트를 다시 열면 상위 바인딩이 복원되지 않아 사용자가 매번 다시 고른다 |
| 6 | **상위가 바뀐 것을 소비자가 알 자리가 없다.** 산출이 무엇의 어느 판으로 만들어졌는지 적는 자리가 어느 파일에도 없다 | 상위 정의 수정 · 상류 재실행 · 기준 파일 교체가 하류 화면에 흔적을 남기지 않아 **사용자가 낡은 결과를 최신으로 읽는다** |
| 7 | **루트가 셋이고 배정 규칙에 답하는 자리가 넷인데 서로 다른 답을 낸다** — `ModuleType` enum 주석 · `getModuleDir()` · `isUserOutputType()`(호출부 0곳) · MCU 우회 | 한 인스턴스의 데이터가 3루트에 흩어져 **"무엇을 함께 버려야 하는가" 가 아무 데도 적히지 않는다.** `deleteSet` 이 config JSON 1개만 지우는 것이 그 결과다. **이 안 밖**(10절) |
| 8 | **조인 키가 전부 사람이 읽는 문자열이다** — 파일명 접두사 · Set 이름 접미사 · 파라미터 이름 · 알고리즘 이름 · 디렉토리명에 박힌 점수 | 이름의 소유자가 GUI 가 아니라 rename 을 막을 수 없고, 같은 알고리즘을 두 응답에 쓰지 못하는 제약이 사용자 경고문으로 노출된다(`DashModelBuilderWidget.cpp:809-812`). **인스턴스 층만 닫고 항목 층은 두지 않는다**(10절) |

**6번이 [[Project-Store-Design-Alpha-Minimal]] 대비 이 안의 고유분이다.** 앞의 다섯을 다 고쳐도 남고, 정의는 소비자를 거치지 않고도 바뀐다 — AL 화면에서 상위 Geometry 파일을 되쓰는 경로가 있다(`DashDesignVariableModel::saveToJsonFiles` `model/DashDesignVariableModel.cpp:375-485`).

### 0.2 개선 내용 — 이 안이 세우는 전제

여섯은 [[Project-Store-Design-Layer-Cut]] 에서 그대로 받고 다섯이 갈린다. 갈리는 행은 첫머리에 표시했다.

| 항목 | 내용 |
|---|---|
| **관리 단위** | **모듈 인스턴스 = `(모듈, variant, Set)` 3튜플.** 저장·복사·삭제·분기의 단위다. 인스턴스가 되는 것은 Geometry · Condition · AnalysisLauncher · DataPreprocessor · ModelBuilder · ModelRunner · Optimizer 일곱이고, Results Analyzer 는 호스트에 임베드되는 패널이라 아니다 |
| **칸 좌표 6종** | 귀속 3(프로젝트 · Set · 실행) × 종류 2(메타 · 벌크) — `PM` · `PB` · `SM` · `SB` · `EM` · `EB`. `--` 는 칸 밖. **현행은 셋만 실재하고 이 안이 신설하는 파일 2종이 `PM` 과 `EM` 이다** |
| **물리 배치** | **갈린다 — 현행 3루트를 그대로 둔다.** 파일 2종만 더한다: `.dproj/project.json`(PM) · `.dproj/outputs/{inst}.json`(EM). 정의는 `configs/` 에 남고 산출은 현 위치에 남는다 |
| **실행** | **갈린다 — 개체가 아니다.** 실행 ID 도 이력도 없고 재실행이 덮는다. 인스턴스마다 run 파일 1개가 **단조 정수 `rev`** 로 "그 산출이 몇 번 덮였는가" 만 센다 |
| **모듈 어휘** | 현행 유지 — `GeometryParameter` · `ConditionParameter` 등. 정본은 `DashIOController::getModuleName()`(`.cpp:61-82`)과 `ModuleType` enum |
| **ID 2종** | **갈린다 — 전역 2종(`ref_` · `inst_`)만 도입하고 로컬 3종(`dv` · `rsp` · `mdl`)은 두지 않는다.** 형식은 접두사 + 12-hex 난수 — `QUuid::createUuid().toString(QUuid::Id128).left(12)`. Qt 네이티브라 새 의존성이 아니고 레포에 `QUuid` 사용 0건이다. 48비트라 항목 10⁴개에서 충돌이 약 2×10⁻⁷ 이고, 전체 UUID(41자)는 맵 키·로그 본문으로 읽히지 않아 쓰지 않는다 |
| **Reference** | 사용자가 `[Add File]` 로 등록하는 기준 해석 파일(Morphing 은 `.inp`·`.dat`, CAD 는 `.prt` + `.wbpj`). 인스턴스 여럿이 공유하므로 프로젝트 레벨에 두고, 레코드는 경로 하나가 아니라 **역할 → 경로 맵**이다 — 역할 어휘 `deck` · `part` · `template` · `material` 4종 고정. **복사본이 정본**이고 원본은 `origin` 기록만. 단 `references/` 디렉토리는 만들지 않는다(1절) |
| **규약 5개** | 11개 중 이 안에 걸리는 다섯 — **1** 칸마다 라이터 1곳 · **2** 메타 쓰기는 원자적(temp + rename) · **5** 실행 중에는 Set 메타를 쓰지 않는다 · **10** 읽기는 진입 1회 + 통지, 폴링 금지 · **11** Set 메타 쓰기는 dirty 신호 + 디바운스 |
| **엣지 3종** | reference(모든 모듈 → 기준 해석 파일) · definition(AnalysisLauncher → Geometry · Condition) · execution(하류 → 상류 산출). **execution 엣지가 디렉토리가 아니라 파일에서 끝난다** — `outputs[].path`. 모델 지목은 2단 ID 가 아니라 `outputs[]` 항목이 받는다 |
| **저장 규칙 4개** | **갈린다 —** 소비자가 소유 · 역방향 미저장 · ID 참조까지는 같고, **엣지에 지문을 달지 않는다.** 지문은 착수 시 해석해 계보(`consumed`)에만 고정한다. 아래 전문 |
| **마이그레이션** | **갈린다 — 불요.** 파일을 옮기지 않으므로 구버전을 거부하지 않고 **승격으로 1회 흡수**한다(8절). 되돌리기도 싸다 — `project.json` 과 `outputs/` 를 지우면 현행 경로로 복귀한다 |

| 엣지             | 소비자 → 생산자                                                                                                        | 무엇을 보나          | 가리키는 것  |
| -------------- | ---------------------------------------------------------------------------------------------------------------- | --------------- | ------- |
| **reference**  | 모든 모듈 → 기준 해석 파일                                                                                                 | 프로젝트 귀속의 입력 파일  | `ref_`  |
| **definition** | AnalysisLauncher → Geometry · Condition                                                                          | 다른 인스턴스의 **정의** | `inst_` |
| **execution**  | DataPreprocessor → AnalysisLauncher<br>ModelBuilder → DataPreprocessor<br>ModelRunner · Optimizer → ModelBuilder | 다른 인스턴스의 **산출** | `inst_` |

**저장 규칙 4.**

1. **소비자가 소유한다** — 생산자는 자기 소비자를 모른다
2. **역방향("누가 나를 쓰는가")은 저장하지 않고 로드 시 계산한다**
3. **엣지는 ID 만 가리킨다** — 경로 · 파일명 · Set 이름을 가리키지 않고 **지문도 달지 않는다**
4. **지문은 실행 착수 시 해석해 계보(`consumed`)에 고정한다** — 엣지는 "무엇에 매달려 있나", 계보는 "이 산출이 무엇의 몇 번째 판으로 만들어졌나"

### 0.3 두 안의 차이

**갈리는 뿌리는 둘이다** — 레이아웃(3루트 유지 / 1루트 재배치)과 실행 개체화(정수 카운터 / `exec_` 개체). 아래 나머지 행은 그 둘에서 따라 나온다.

| 축 | **안 β** — [[Project-Store-Design-Layer-Cut]] | **안 α-edge** — 이 문서 |
|---|---|---|
| 물리 배치 | 인스턴스 = 자기완결 디렉토리, **루트 1개** | 현행 3루트 유지, 파일 2종 추가 |
| 신설 파일 | `project.json` · `definition.json` · `execution.json` · `input.json` · `view.json` | `project.json` · `outputs/{inst}.json` 둘 |
| 실행 | **개체다** — `exec_` ID · `executions/{label}/` 누적 · 이력 보존 | 개체가 아니다 — 실행 ID·이력 없음, 재실행이 덮고 **단조 정수 `rev`** 만 센다 |
| 조인 키 | **ID 6종** — 전역 3 + 로컬 3 | 전역 2종(`ref_` · `inst_`)만. 항목 단위 조인은 **현행 이름 조인 유지** |
| 정의 파일 본문 | **키까지 바뀐다** — DV 이름 → `dv{N}`, 응답 3필드 → `rsp{N}`, 알고리즘 이름 → `mdl{N}` | **손대지 않는다** — 최상위 키 3개(`$schema` · `upstream` · `rev`)만 더한다 |
| 지문의 자리 | 엣지(`upstream.bound`)와 계보(`consumed`) **둘 다** | **계보에만** — 엣지는 순수 ID |
| 지문의 형태 | reference · definition 만 `sha256`. execution 엣지는 지문 없음(새 `exec_` 가 나므로) | **3종 전부 저장 값** — PM `sha256` · SM `rev` · run 파일 `rev`. 실행이 개체가 아니라 산출에도 지문이 든다 |
| 배지 | 6종 | 6종 — 판정 입력이 다르다 |
| 산출물 대장 | `artifacts[]` **전량** — `kind` · `purged` · `model` 역참조 + `cases[].reason` · `stages[]` | `outputs[]` — **소비자가 여는 것만 · 성공분만** |
| 경로 규약 불일치 | **소멸** — 루트가 하나라 질문 자체가 없어진다 | **남는다** — 조립 규칙을 `getModuleDir()` 하나로 인정하고 호출부 25곳을 건드리지 않는다 |
| Set 삭제 · 분기 | 디렉토리 1개 조작 | 파일 3\~4개 + 산출 디렉토리 추적 |
| 도구 계약 | **바꾼다** — 규약 9(정의는 stdin, 보고는 stdout, 쓰기는 EB 아래로만). 도구를 함께 릴리스해야 한다 | **안 바꾼다** — 1초 폴링과 도구의 SM 되쓰기가 남는다 |
| 기존 프로젝트 | 마이그레이션 미수행 · **열기 거부** | **승격 1회 흡수** — 파일을 옮기지 않아 거부가 불요하다 |
| 되돌리기 | 사실상 불가 | `project.json` 과 `outputs/` 를 지우면 현행 경로로 복귀 |
| 숨김 경계 · 경로 길이 | 상실(정의 JSON 이 사용자에게 보인다) · **상대경로 +25자** | 유지 · 무변화 |
| 착수 비용 | 대 — 단계 계획은 아직 없다 | 소~중 — 6단계, 각 단계 종료 시 빌드·실행 가능 |

**두 안이 같은 것도 적지 않다.** 관리 단위 · 칸 좌표 6종 · 모듈 어휘 · 전역 ID 형식 · Reference 의 역할 맵 · 엣지 3종과 소비자 소유 규칙 · `upstream` 의 공통 키 셋 · 배지 6종 · 매니페스트가 variant 의 유일한 정본이 되는 것이 그것이다. 0.2 의 표에서 갈리는 것은 **물리 배치 · 실행 개체 · 로컬 ID · 지문의 자리 · 마이그레이션** 다섯 행뿐이다.

**α 선 안에서 α-min 과 갈리는 것은 "상위가 바뀐 것을 소비자가 아는가" 한 축이다.**

| 축                     | α-min              | 이 안                                                    |
| --------------------- | ------------------ | ------------------------------------------------------ |
| 신설 파일                 | `project.json` 1종  | + `outputs/{inst}.json` — 인스턴스 1개당 1개, 덮어쓰기            |
| 실행 추적                 | 없음                 | **단조 정수 `rev`** — 실행 ID·이력은 여전히 없다                     |
| execution 사슬          | 디렉토리에서 끝나고 그 안은 스캔 | **파일에서 끝난다** — `outputs[].path`                        |
| 지문                    | 없음                 | **3종 전부 저장 값** — PM `sha256` · SM `rev` · run 파일 `rev` |
| 배지                    | 4종                 | **6종** — `Complete` · `⚠ Stale` 이 서고 Stale 사유가 3갈래     |
| 순서                    | 4단계                | 6단계 — S5(run 파일) · S6(지문·계보) 추가                        |
| 로컬 ID · 파일 이동 · 도구 계약 | 안 한다               | **같다**                                                 |

### 0.4 실제 추가 · 변경되는 것

**파일 — 더하기만 하고 옮기지도 지우지도 않는다.**

| 구분 | 대상 | 근거 |
|---|---|---|
| **추가** | `.dproj/project.json`(PM) · `.dproj/outputs/{inst}.json`(EM · 인스턴스당 1개 · 덮어쓰기) | 1\~2절 · 5.1 |
| **이동** | **없다** — `[Add File]` 복사본도 `configs/` 의 정의도 현 위치에 남는다 | 1절 |
| **분해** | **없다.** 정의 본문은 손대지 않고 최상위 키 3개(`$schema` · `upstream` · `rev`)만 더한다. 실행 상태와 산출 포인터만 run 파일로 나간다 | 4.1 · 5.4 |
| **폐기** | **없다** — `configs/` · 숨김 산출 루트 · `configs/` 안 두 번째 복사본이 전부 남는다 | 10절 |

**코드 — 새로 만드는 것이 넷이고 기존 수정은 판정 주체 교체와 라이터 5곳이다.**

| 갈래 | 건수 | 성격 |
|---|---|---|
| **9.1 신설 접근자** | 3 | 매니페스트 · run 파일 · **SM 저장 헬퍼** |
| **9.2 판정 주체 교체** | 8 | 글로빙 · 접미사 판정 14곳 · `folders.first()` · 모델 디렉토리 글로빙 · 케이스 게이팅을 **저장 값 조회**로 |
| **엣지 배선** | 모듈 7종 | `upstream` 3배열 읽기·쓰기 + 배지 판정 1벌(6.2 · 6.3) |
| **기존 코드 수정** | 5곳 | 정의 라이터(Geometry 3벌 · Condition 2벌)가 SM 저장 헬퍼를 통과 |

**경로 조립 함수 4개와 그 호출부 25곳은 건드리지 않는다.** 조인 키의 자료구조 교체도 없고(이름 조인 유지), 수명 조작은 `deleteSet` 에 run 파일 삭제가 붙는 정도다. [[Project-Store-Design-Rationale]] 2절의 읽기 배선 15건을 기준으로 보면 다섯(1 · 2 · 6 · 9 · 14번)이 닫히고 15번은 **소비자가 여는 산출에 한해** 닫힌다 — 나머지 아홉은 정의 본문 안의 미배선이라 본문을 손대지 않는 이 안 밖이다.

**현황 8건의 판정 — 셋이 닫히고 셋이 부분이며 둘이 남는다.**

| # | 현황 | 이 안 |
|---|---|---|
| 1 | 프로젝트 매니페스트가 없다 | **닫힌다** — 2절 |
| 2 | 정의와 실행 상태가 한 파일에 있다 | **부분** — 실행 상태와 산출 포인터가 run 파일로 나간다. AL 케이스 상태 전이와 MB `Configuration.{model}.status` 는 SM 에 남고, 실행이 개체가 아니라 이력도 없다(5.4 · 10절) |
| 3 | 외부 도구가 같은 파일을 되쓴다 | **남는다** — 도구 계약 변경이 이 안 밖이다. 다만 run 파일에는 도구 손이 닿지 않아 **라이터 1곳이 실행 칸에서는 성립한다**(5.1) |
| 4 | 산출물 대장이 없다 | **부분** — `outputs` 가 소비자가 여는 것만 담는다. 부산물·실패 케이스·정리 표시는 없다(5.4) |
| 5 | 상위 선택이 기록되지 않거나 읽히지 않는다 | **닫힌다** — 3\~5절 엣지 + 6절 판정 |
| 6 | 상위가 바뀐 것을 소비자가 알 자리가 없다 | **닫힌다** — 지문 3종과 계보로 상위 변경이 배지에 뜬다. **이 안의 고유분**(5.2 · 5.3 · 6.3) |
| 7 | 루트가 셋이고 배정 규칙이 어긋난다 | **남는다** — 조립 규칙을 `getModuleDir()` 하나로 인정한다. 다만 "무엇을 함께 버려야 하는가" 는 `instances[]` 와 run 파일이 부분적으로 답한다(10절) |
| 8 | 조인 키가 전부 사람이 읽는 문자열이다 | **부분** — 모듈 판정과 variant 는 `inst_` 로 닫히고, DV · 응답 · 학습 모델 · 실행은 이름 조인으로 남는다(10절) |

**대가 넷.** 실행 이력이 없어 재실행이 이전 산출을 덮고(케이스 실패 사유·스테이지 상태도 자리가 없다), 항목 단위 조인이 이름 조인으로 남으며, 기준 파일의 제자리 수정을 탐지하지 못하고(3.3), 경로 규약 불일치와 `configs/` 두 번째 복사본이 그대로 남는다. **대신 되돌리기가 싸다** — 물리 변화가 파일 추가뿐이라 승격 코드가 남아 있는 동안은 현행 경로로 복귀한다.

**대상 범위 — 넣는 것과 빼는 것 전수.**

| 항목                                                  | 이 안     | 근거                                          |
| --------------------------------------------------- | ------- | ------------------------------------------- |
| `.dproj/project.json` (PM) — 엔티티 색인                 | **넣는다** | 현황 1. 물리 변화 둘 중 하나 (2절)                     |
| `references[]` 등록 레코드 + `fingerprint`               | **넣는다** | reference 엣지의 대상과 그 지문. 해시는 등록 1회 (3.3)     |
| `instances[]` 색인 — `id`·`module`·`variant`·`config` | **넣는다** | Set 단위 의존성의 대상이자 **variant 의 유일한 정본** (2절)  |
| 전역 ID 2종 — `ref_` · `inst_`                         | **넣는다** | 엣지가 가리킬 것. 형식은 0.2 그대로                      |
| `upstream` 3배열 (SM)                                 | **넣는다** | 현황 5. 원소는 **순수 ID** — 지문을 달지 않는다 (0.2 규칙 3) |
| 정의 `rev` (SM) + SM 저장 헬퍼                            | **넣는다** | 정의 지문. 라이터 5곳을 한 자리로 모은다 (4.3 · 9.1)        |
| `.dproj/outputs/{inst}.json` (EM)                   | **넣는다** | 물리 변화 둘 중 나머지. 실행 1회당 쓰기 2번 (5.1)           |
| 산출 `rev` · `consumed` · `outputs`                   | **넣는다** | 지문 · 계보 · 소비자가 여는 것 (5.2\~5.4)              |
| 배지 6종 + `Stale` 사유 3갈래                              | **넣는다** | 현황 6. 판정 입력이 전부 저장 값이라 계산이 0 이다 (6.3)       |
| 승격 — 구프로젝트 1회 흡수                                    | **넣는다** | 파일을 옮기지 않으므로 거부가 불요하다 (8절)                  |
| 실행 ID · 이력 · 정의 본문 스냅샷 · 산출물 대장 전량                  | **뺀다**  | 실행을 개체로 두지 않는다 (10절)                        |
| 로컬 ID 3종 — `dv` · `rsp` · `mdl`                     | **뺀다**  | 의존성 단위가 인스턴스다. 항목 단위 조인은 현행 이름 조인 유지 (10절)  |
| 파일 이동 · 도구 계약 변경 · 마이그레이션                           | **뺀다**  | 3루트 유지가 전제다 (10절)                           |
| 제자리 수정 탐지 · `Stale` 전이 전파                           | **뺀다**  | 지문이 등록 시 동결이고 전파는 재실행을 따라 내려간다 (3.3 · 6.3)  |

---

## 1. 물리 배치 — 신설 파일 2종

```
{ProjectRoot}/
   .{Project}.dproj/
      project.json                       ★ 신설 — 엔티티 색인                    PM
      outputs/
         inst_2a8c5f019b3d.json          ★ 신설 — 인스턴스 1개당 1개 · 덮어쓰기   EM
         inst_5c31ff08a742.json
      configs/
         AnalysisLauncher_Set1.json         현행 그대로 + upstream 블록만 추가    SM
         GeometryParameter_Set1.json        동상                                  SM
         GeometryParameter_Set1.vtp         현행 그대로 — 핸들 배열               SB
         AnalysisModelIdentity.json         제자리 유지                           --
         bracket_v3.dat  spring.prt         두 번째 복사본 — 남는다               PB
      ModelBuilder_Set1/                    현행 그대로 — Sim 학습 산출           EB
   bracket_v3.inp                           [Add File] 복사본                     PB
   AnalysisLauncher_Set1/                   현행 그대로 — 케이스 디렉토리와 산출  EB
   DataPreprocessor_Set1/                   동상
   ...
```

**run 파일명이 인스턴스 ID 다.** `{Module}_{Set}` 를 쓰면 이름 조인이 되살아나고 Set rename 이 파일 rename 을 요구한다. ID 로 두면 매니페스트의 `instances[].id` 가 곧 파일명이라 조회에 조립이 없다.

**`configs/` 와 다른 디렉토리에 둔다.** `configs/*.json` 글로빙이 파일명 접두사로 모듈을 판정하므로(`DashProject::loadSetsFromConfigs()` `model/DashProject.cpp:1066-`) 같은 디렉토리에 파일을 더하면 승격 경로가 오판한다.

**`references/` 디렉토리를 만들지 않는다.** `[Add File]` 은 지금처럼 `{Root}/` 로 복사하고 `references[].files` 가 그 자리를 가리킨다.

---

## 2. `project.json` — 엔티티 색인 (PM)

```json
{
  "$schema": 1,
  "references": [
    { "id": "ref_9b41e0c3f2a1",
      "label": "Bracket v3",
      "kind": "fe",
      "files": { "deck": "bracket_v3.inp" },
      "origin": "C:/work/bracket_v3.inp",
      "fingerprint": "sha256:9b41e0…" }
  ],
  "instances": [
    { "id": "inst_4d19b2a70e55",
      "module": "AnalysisLauncher",
      "variant": "Init",
      "label": "Set1",
      "config": ".dproj/configs/AnalysisLauncher_Set1.json" }
  ]
}
```

| 필드 | 내용 |
|---|---|
| `references[].kind` | `fe` \| `cad`. 모듈이 고를 수 있는 Reference 를 거르는 축 — Morphing·Condition 은 `fe` 만, CAD 는 `cad` 만 후보로 본다. 지금 확장자 분기 3곳(`DashRwSession::load:1361-1370` · `DashMainWindow::onProjectFileLoadClicked:2210-2227` · `DashReferenceFileWidget::findAnalysisFiles:448`)이 각자 하던 판정을 등록 1회로 앞당긴 값이다 |
| `references[].files` | **역할 → 경로 맵.** Morphing 은 `.inp`(또는 `.dat`) 1개가 형상·FE 조건·해석 템플릿 3역 겸직, CAD 는 `.prt` + `.wbpj` 2개가 형상 / 템플릿으로 갈린다 |
| `references[].origin` | 출처 기록. **해석에 쓰지 않는다.** 등록 순간에만 손에 있는 값이고(`QFileDialog::getOpenFileNames` 결과, `DashMainWindow.cpp:2131`) 현행은 복사한 뒤 버린다 |
| `references[].fingerprint` | 복사본의 sha256. **등록·재가져오기 때 1회 계산해 저장한다** (3.3). 해시는 `rwFileSha256()`(`DashRwSession.cpp:1030-1066`)이 이미 낸다 |
| `instances[].variant` | **variant 의 유일한 정본.** 현행은 Set 이름 접미사 · JSON `variant` 키 · 트리 `Qt::UserRole+2` 3벌에 병행 보관된다 |
| `instances[].label` | 현행 `setName`(`Set1-Morphing`) 그대로. **정본은 매니페스트이고 접미사는 라벨이다** — 접미사를 떼면 파일명·트리 표시·`getModuleDir()` 인자가 함께 움직이고 그것은 경로 축 작업이다 |
| `instances[].config` | SM 파일의 경로 |

**복사본이 정본이다.** 프로젝트 안의 복사본을 쓰고 원본은 참조하지 않는다. 원본이 사라지거나 경로가 바뀌어도 프로젝트가 돈다.

**매니페스트는 엣지를 담지 않는다.** 담는 것은 엣지가 가리키는 엔티티와 ID → 실물 좌표뿐이라, 상위 선택을 바꿔도 PM 이 안 써진다.

---

## 3. reference 엣지 — 기준 해석 파일

### 3.1 저장 자리

| 무엇 | 어디 |
|---|---|
| 대상을 정의하는 메타 | `.dproj/project.json` → `references[]` |
| 엣지 | 소비자의 `configs/{Module}_{Set}.json` → `upstream.references[]` |

```json
"upstream": { "references": ["ref_9b41e0c3f2a1"], "definitions": [], "executions": [] }
```

**배열이다.** FE-safe 가 **같은 Set 안 다른 템플릿이 낸 ODB** 를 입력으로 받으므로 단수로는 그 모듈이 서지 않는다. 뒤에 배열로 바꾸는 것은 스키마 변경이다.

**원소는 순수 ID 다** — 지문을 달지 않는다(0.2 규칙 3). 지문은 계보에만 있다(5.3).

**빈 배열을 생략하지 않는다.** 판정이 "키가 있나" 를 먼저 묻지 않고 세 배열 순회로 끝나야 한다.

### 3.2 소비자

| 소비자 | 역할 | 현행 |
|---|---|---|
| GeometryParameter Morphing | `deck` | 전역 활성 컨텍스트 1개를 따른다 — 메모리 전용, 직렬화되지 않는다 |
| GeometryParameter CAD | `part` | 동상. 마지막 NX 응답을 전 CAD 인스턴스에 일괄 적용(`DashManager.cpp:187-196`) |
| ConditionParameter | `deck` | 동상 — 대상 deck 을 자기가 고르지 않는다 |
| AnalysisLauncher | `template` · `deck` | `input_files[]` `{name, target_component, path}` 로 부분 존재 |
| ModelRunner | `deck` | 없다 |

### 3.3 지문 — 등록 시 동결

**이 지문이 답하는 것은 "기준 파일이 다시 등록됐나" 하나다.** `[Add File]` 로 같은 역할에 다른 파일을 넣으면 지문이 갈리고, 옛 파일로 만든 하위 산출이 `⚠ Stale` 이 된다.

| 항목 | 값 |
|---|---|
| 형태 | `"sha256:9b41e0…"` — 복사본 파일 전문의 해시 |
| 자리 | PM `references[].fingerprint` — **저장한 값** |
| 계산 시점 | `[Add File]` 등록 1회. **그 외에는 재계산하지 않는다** |
| 비용 | 기준 파일은 수백 MB 까지 간다(`.inp` · `.prt`). 등록 때는 같은 파일을 복사하느라 이미 I/O 바운드라 **스트리밍하며 해시하면 실질 추가 비용이 없다** |

**정수 카운터가 아니라 해시인 이유는 하나다** — 같은 파일을 다시 등록해도 지문이 그대로라 하류가 헛되이 `Stale` 이 되지 않는다. 카운터는 등록할 때마다 오른다.

**제자리 수정은 탐지하지 못한다 — 이 안의 한계다.** 저장된 값끼리 견주므로 파일 내용이 앱 밖에서 바뀌어도 지문은 움직이지 않는다. 실제 채널이 있다 — FE-safe 재료 설정이 `.stlx` · `.dbase` 를 직접 고치고 `.bak_{yyyyMMdd_HHmmss}` 백업만 남긴다(`MaterialSetupDialog:196` · `:577`). 잡으려면 비교 시점에 파일을 다시 봐야 하는데(최소 `(size, mtime)` stat), **이 배포에 넣지 않는다**(10절).

### 3.4 시점

| | 시점 | 내용 |
|---|---|---|
| **메타 쓰기** | `[Add File]` (`view/DashMainWindow.cpp:2118-2183`) | `references[]` 1항목 — `id` 발급 · `kind` 판정 · `files` 조립 · `origin` · **`fingerprint` 계산** |
| **메타 읽기** | 프로젝트 열기 1회 | 매니페스트 전문. 이후 메모리 조회 — **지문도 저장된 값이라 파일을 열지 않는다** |
| **엣지 쓰기** | 사용자가 Reference 를 고르는 순간 | 소비자 SM 의 `upstream.references[]` (순수 ID) |
| **엣지 읽기** | 모듈 진입 1회 | `upstream.references[]` → `references[].files` → 파일 열기. 폴링 없음 |
| **지문 비교** | 모듈 진입 · 프로젝트 열기 | 소비자 run 파일 `consumed.references[]` 의 `@지문` vs `references[].fingerprint`. **둘 다 저장된 값이라 재등록만 잡는다**(3.3) |

**전역 활성 컨텍스트가 이 배선으로 대체된다.** 화면에 렌더된 대상 · 트리 선택 · 카메라는 세션 전용으로 남고, "이 Set 은 어느 파일 기준인가" 만 `upstream` 이 갖는다. 현행은 둘이 같은 변수라 **화면 조작이 데이터 결합을 바꾼다.**

---

## 4. definition 엣지 — Geometry · Condition 정의

### 4.1 저장 자리

| 무엇 | 어디 |
|---|---|
| 대상을 정의하는 메타 | `configs/GeometryParameter_{Set}.json` · `ConditionParameter_{Set}.json` — **현행 본문 그대로** |
| 그 메타의 좌표 | `.dproj/project.json` → `instances[]` (`id` · `module` · `variant` · `config`) |
| 엣지 | 소비자 SM → `upstream.definitions[]` |

```json
"upstream": { "references": ["ref_9b41e0c3f2a1"],
              "definitions": ["inst_7f3a2c1b04de", "inst_1e55da62c9f7"],
              "executions": [] }
```

**정의 본문은 손대지 않는다.** `DV-Geometry` · `DV-Condition` · `Morphing.*` · `Independent/Dependent Parameter` 는 현행 스키마 그대로다. SM 에 더해지는 것은 최상위 키 셋 — `$schema` · `upstream` · `rev`(4.3) 뿐이고, 모듈 블록 안은 한 줄도 건드리지 않는다.

### 4.2 소비자

| 소비자 | 가리키는 것 | 근거 |
|---|---|---|
| AnalysisLauncher | Geometry · Condition | DOE 축이 될 DV 의 출처 |
| ModelRunner | Geometry | **정의를 실제로 여는 소비자다** — `Morphing.radius`(`model/DashModelRunner.cpp:2164-2167`)와 핸들 배열 `.vtp`(`:2062`)를 열어 케이스 형상을 만든다. 자기 파일에 엣지가 없으면 닿을 방법이 남지 않는다 |

### 4.3 지문 — SM 의 `rev` 정수

**정의 변경은 소비자가 모르는 사이에 일어난다.** Geometry Set 을 고친 사람과 그것을 상위로 쓰는 AnalysisLauncher 를 여는 사람이 같은 순간에 있지 않고, DV 범위는 **AL 화면에서 Geometry 파일을 되쓰는 경로**(`DashDesignVariableModel::saveToJsonFiles` `model/DashDesignVariableModel.cpp:375-485`)로도 바뀐다. 지문이 없으면 이미 돌린 DOE 가 어느 정의로 만들어졌는지 말할 자리가 없다.

| 항목 | 값 |
|---|---|
| 형태 | 단조 증가 정수. `{"$schema": 1, "rev": 3, "upstream": {…}, "DV-Geometry": {…}}` |
| 자리 | **SM 자기 파일** |
| 뜻 | 이 인스턴스의 **정의가 저장된 횟수** |
| 올리는 주체 | 정의 저장 경로 — 실행이 아니다 |

**해시를 쓰지 않는 근거 하나.** 정의 칸은 SM(`{Module}_{Set}.json`, 수 KB\~수백 KB) 하나가 아니라 **SM + SB** 이고, Morphing 의 SB(`.vtp`)가 **수백 MB 까지 간다** — `AllFixedVolumeIds` 가 핸들 수가 아니라 메시 크기에 비례하는 항이기 때문이다. 읽기 시점 해시는 배지 계산마다 그 파일을 통째로 읽는다는 뜻이라 성립하지 않는다.

**SB 를 따로 세지 않아도 된다.** SM 과 SB 는 한 쓰기 단위다 — `saveMorphingSettings`(`viewmodel/DashGeometryParameterPresentationModel.cpp:325-`)가 `.vtp` 와 `.json` 을 잇달아 쓰고, 그 직전 `filterSelectedHandles`(`:171-323`)가 SM 의 `handle id` 를 새 인덱스로 치환한다. **SM 의 `rev` 가 SB 변경까지 덮는다.** 두 쓰기 사이의 크래시 창은 11.2-9 다.

**`rev` 를 갖는 SM 은 Geometry·Condition 둘뿐이다.** 정의로 참조당하는 인스턴스가 그 둘이기 때문이다(6.2). AnalysisLauncher 이하 다섯은 자기 정의를 아무도 보지 않고 산출만 소비당하므로 SM 에 `rev` 를 두지 않는다 — 그쪽 지문은 run 파일에 있다.

**정수 카운터가 해시보다 나은 자리도 하나 있다.** 핸들을 선택 집합 변경 없이 위치만 옮기면 SM 바이트가 그대로일 수 있는데, 쓰기 트리거인 `rev` 는 그래도 오른다. 내용 비교는 그것을 놓친다.

**대가는 오탐 하나와 배선 하나다.**

| | 내용 |
|---|---|
| 오탐 | 값을 고쳤다 되돌리면 내용은 같은데 `rev` 는 두 칸 올라 하류가 `⚠ Stale` 이 된다. 착수를 막지 않는 경고이므로 감수한다(6.3) |
| 배선 | 라이터가 Geometry 3벌(PM `:325` · 위젯 `:654` radius 스핀박스 · `DesignVariableModel:375`) · Condition 2벌이라 **증가를 흩어 두면 나중에 라이터를 하나 더 붙이는 사람이 잊는다.** 9.1 의 **SM 저장 헬퍼**로 5곳을 통과시켜 증가를 한 자리에 둔다 |

**승격된 프로젝트는 `rev` 키가 없고 그것을 `0` 으로 읽는다.** 계보가 비어 있어 비교 대상이 없으므로 무해하다.

### 4.4 시점

| | 시점 | 내용 |
|---|---|---|
| **메타 쓰기 · 색인** | Set 생성(`DashProject::createNewSet()` `:705-` → `createModuleJsonFile()` `:592-`) · 삭제(`:802-`) · rename(`:1416-`) | `instances[]` 항목 추가 · 제거 · `label`·`config` 갱신 |
| **메타 쓰기 · 본문** | 현행 트리거 유지 — Geometry 는 `[Set Design Variable]` 1회, Condition 은 체크박스 sync | 정의 본문 + **`rev` +1**. 전부 SM 저장 헬퍼를 통과한다(9.1) |
| **메타 읽기** | 모듈 진입 1회 | 자기 SM |
| **엣지 쓰기** | AL 화면에서 상위 Geometry·Condition Set 을 고르는 순간 | `upstream.definitions[]` (순수 ID) |
| **엣지 읽기** | ① 모듈 진입 ② 실행 착수 | `upstream.definitions[]` → `instances[].config` → 그 파일 |
| **지문 읽기** | ① 실행 착수 (계보에 고정) ② 프로젝트 열기 · 소비자 진입 (비교) | 생산자 SM 의 `rev` — **파일 열기 1회, 계산 없음** |

**현행은 ②만 있고 ①이 없다.** DOE 실행 착수 시 상위 config 를 파일 경로로 직접 여는데(`DashMorphingDoeExecutor:255-311` · `AL:1257/1305`) 그 경로가 관례 조립이라, 진입 시점에는 "이 Set 이 무엇에 매달려 있나" 를 화면이 말하지 못한다.

---

## 5. execution 엣지 — 다른 인스턴스의 산출

**여기가 다른 안과 갈리는 축이다.** 실행을 개체로 두지 않으면서(ID 없음 · 이력 없음 · 덮어쓰기) 엣지가 파일까지 닿게 한다.

### 5.1 run 파일 — `.dproj/outputs/{inst}.json` (EM)

```json
{
  "$schema": 1,
  "instance": "inst_4d19b2a70e55",
  "rev": 7,
  "state": "Done",
  "started":  "2026-09-02T14:02:33+09:00",
  "finished": "2026-09-02T14:41:07+09:00",
  "params": { "analysisType": "Static" },

  "consumed": {
    "references":  ["ref_9b41e0c3f2a1@sha256:9b41e0…"],
    "definitions": ["inst_7f3a2c1b04de@3", "inst_1e55da62c9f7@1"],
    "executions":  []
  },

  "outputs": [
    { "kind": "case", "type": "Static", "key": "runs1",
      "path": "AnalysisLauncher_Set1/Static/runs1" }
  ]
}
```

**예시는 AnalysisLauncher 다** — `consumed` 가 채워진 배열과 6.2 의 그 모듈 행이 일치한다(references · definitions 만). 하류인 DataPreprocessor 는 정반대로 `executions` 만 찬다.

```json
"consumed": { "references": [], "definitions": [],
              "executions": ["inst_4d19b2a70e55@7"] }
```

| 항목 | 규약 |
|---|---|
| 자리 | 인스턴스 1개당 파일 1개. **재실행이 같은 파일을 덮는다** — 이력이 없다 |
| 라이터 | **1곳** — 그 실행을 착수시킨 GUI 컨트롤러. 외부 도구는 이 파일을 건드리지 않는다 |
| 쓰기 횟수 | 실행 1회당 **2번** (착수 · 종결). 케이스 전이마다 쓰지 않는다 |
| 대상 모듈 | 실행이 있는 5종 — AnalysisLauncher · DataPreprocessor · ModelBuilder · ModelRunner · Optimizer. Geometry·Condition 은 실행이 없어 run 파일이 없다 |
| `state` | `Running` · `Done` · `Failed` · `Cancelled` |
| 원자성 | temp + rename |

**도구 계약을 바꾸지 않고도 라이터가 1곳이다.** ModelBuilder 는 외부 도구가 `ModelBuilder_{Set}.json` 의 `Configuration.{model}.status` 를 `"Done"` 으로 되쓰고 GUI 가 1초 폴링으로 그것을 읽는데(`MB:1364`·`:1384`), run 파일은 **GUI 가 그 `Done` 을 본 뒤** 쓴다. 도구는 여전히 SM 을 되쓰지만 run 파일에는 손이 닿지 않는다.

### 5.2 `rev` — 지문

**`rev` = 이 인스턴스의 산출이 덮어써진 횟수.** 단조 증가 정수, **실행 착수 시 +1**.

| 시점 | `rev` | `state` | `outputs` |
|---|---|---|---|
| 착수 | +1 | `Running` | **비운다** — 이 순간부터 디스크의 산출이 갈린다 |
| 종결 | 유지 | `Done` \| `Failed` \| `Cancelled` | 기록 |

**종결이 아니라 착수에서 올리는 이유는 정직성이다.** 실행 중에는 디스크의 산출이 이미 덮이고 있으므로, 소비자가 바인딩해 둔 값과 어긋나는 것이 사실이다. 실패해도 이전 산출은 돌아오지 않으므로 `rev` 를 되돌리지 않는다.

**산출에는 해시를 쓰지 않는다.** 케이스 디렉토리 수십 개 · 텐서 파일 · 학습 모델 디렉토리라 내용 해시가 진입 1회에 초 단위를 먹는다. 정수 비교는 비용이 0 이고, 답해야 하는 질문("내가 본 뒤에 덮였나")에 정확히 답한다.

**실행 `rev` 를 SM 으로 옮기지 않는 근거 넷.** 정의 `rev` 는 SM 에 사는데(4.3) 실행 `rev` 는 아니다 — 같은 정수라도 놓이는 파일에 따라 성립 여부가 갈린다.

| # | 근거 |
|---|---|
| 1 | **실행이 정의 파일을 쓰게 된다.** 착수가 SM 의 `rev` 를 올리면 "정의와 실행 상태가 한 파일에 있다" 는 현행 문제를 하나 더 만드는 것이다 |
| 2 | **라이터가 갈린다.** SM 의 라이터는 정의 편집자, run 파일의 라이터는 실행 착수 컨트롤러다. 한 파일에 두 귀속의 라이터를 넣으면 "칸마다 라이터 1곳" 이 그 파일에서만 깨진다 |
| 3 | **`rev` 와 `outputs` 는 원자적으로 함께 움직인다.** 착수 = `rev`+1 & `outputs` 비움, 종결 = `outputs` 기록. 두 파일로 쪼개면 그 사이 크래시에 둘이 어긋나 소비자가 "`rev` 는 8인데 `outputs` 는 7판 것" 을 본다. 한 파일이면 temp + rename 한 번이다 |
| 4 | **ModelBuilder SM 은 외부 도구가 되쓴다.** `Configuration.{model}.status` 를 도구가 `"Done"` 으로 바꾼다. GUI 소유 값을 다른 프로세스가 read-modify-write 하는 파일에 넣게 된다. **정의 SM 에는 이 문제가 없다** — Geometry·Condition 을 되쓰는 외부 프로세스가 없다 |

**지문 3종을 가르는 규칙은 하나다 — 지문은 그것이 기술하는 대상과 같은 칸에 살고, 그 칸의 라이터가 올린다.**

| 대상 | 사는 칸 | 올리는 주체 | 형태 | 왜 그 형태인가 |
|---|---|---|---|---|
| 기준 해석 파일 (PB) | PM `references[].fingerprint` | 프로젝트 컨트롤러 — `[Add File]` 등록 | `sha256` **저장** | 등록이 유일한 갱신 경로다. 정수가 아니라 해시인 것은 **같은 파일 재등록이 헛된 `Stale` 을 만들지 않게** 하려는 것이고(3.3), 등록 1회라 수백 MB 라도 감당된다 |
| 정의 (SM · SB) | **SM `rev`** | 정의 저장 헬퍼 | 정수 **저장** | SB 가 수백 MB 까지 가 읽기 시점 해시가 성립하지 않는다(4.3) |
| 산출 (EB) | **run 파일 `rev`** | 실행 착수 컨트롤러 | 정수 **저장** | 산출이 크고 여럿인데 라이터가 1곳이라 세는 것이 유일하게 싸다 |

**읽기 시점 계산이 0 이다.** 셋 다 저장된 값이라 배지 판정이 파일을 읽기만 하고 아무것도 계산하지 않는다. 유일한 해시는 `[Add File]` 1회이고, 그때 같은 파일을 복사하느라 이미 I/O 바운드라 스트리밍하며 해시하면 실질 추가 비용이 없다.

**비교 방식도 셋 다 같다** — 계보의 `@` 뒷자리와 현재 값을 문자열로 견준다. 판정 코드에 대상별 분기가 없고, 갈리는 것은 "현재 값을 어디서 읽나" 한 줄이다.

### 5.3 `consumed` — 계보

**착수 시점에 `upstream` 을 해석하고 그때의 지문을 붙여 고정한다.** 이후 소비자가 상위 선택을 바꾸거나 상위가 바뀌어도 이 산출의 계보는 변하지 않는다. **버전을 드는 자리가 여기 하나다.**

| 키 | 값 | 무엇에 답하나 |
|---|---|---|
| `references` | `ref_@sha256:…` | 어느 기준 파일의 **어느 판**에서 나왔나 |
| `definitions` | `inst_@rev` | 어느 Geometry·Condition 정의의 **몇 번째 판**으로 만들어졌나 — **현행은 적는 자리가 없다** |
| `executions` | `inst_@rev` | 어느 상류 산출의 **몇 번째 판**을 먹었나 |

**정의 본문 스냅샷은 뜨지 않는다.** 파일 전문을 복사하면 실행마다 정의 크기만큼 쌓이고, 되돌리기를 지원하지 않는 이 안에서 그것을 읽을 자리가 없다. **지문은 "그때와 같은가" 에 답하고 스냅샷은 "그때 무엇이었나" 에 답하는데, 이 안이 필요한 것은 앞엣것뿐이다.** `consumed` 는 좌표와 지문만 담는다.

**말단 두 모듈(ModelRunner · Optimizer)도 run 파일을 쓴다.** `outputs` 는 비지만 `consumed` 가 "이 최적화가 어느 학습 산출의 몇 번째 판으로 돌았나" 를 답한다 — 소비자가 없어도 그 답이 필요한 것은 사용자다.

### 5.4 `outputs` — 소비자가 여는 것만

**산출물 대장 전량이 아니다.** 부산물 · 실패 케이스 · 로그 · 정리 표시를 담지 않는다. **하류가 실제로 여는 것만** 적는다.

| 생산자 | 항목 | 소비자가 쓰는 법 |
|---|---|---|
| **AnalysisLauncher** | `{kind:"case", type, key, path}` — **성공한 케이스만** | DataPreprocessor 가 데이터셋에 담을 케이스 목록. 현행은 AL config 의 `DOE Table.samples[].status_{type}` 를 읽어 `Done` 만 거른다(`DashDataProcessor.cpp:3039-3043`) |
| **DataPreprocessor** | `{kind:"dataset", path}` — `*.xml` | ModelBuilder `Data Label.Dataset` 의 후보 |
| **ModelBuilder** | `{kind:"model", response, algo, path}` | ModelRunner·Optimizer 의 모델 지목. 현행은 `{response}/{model}_{score}/` 디렉토리를 `modelName + "_*"` 로 글로빙한다(`DashModelRunner.cpp:2306-2312`) — **점수가 디렉토리 이름에 박혀 있어서다** |
| **ModelRunner · Optimizer** | 없음 — 파이프라인 말단 | — |

**AnalysisLauncher 의 케이스 상태 전이는 옮기지 않는다.** 전이마다 SM 전문을 재작성하는 현행 경로(`DoeConfigManager:528-556`, 총 I/O 가 케이스 수의 제곱)는 이 안의 대상이 아니다. run 파일은 **종결 시 그 결과를 요약해 한 번 적는다.** 그 대신 하류는 상류 SM 을 더 이상 읽지 않는다 — DataPreprocessor 가 AL 의 `DOE Table` 을 무변환 복사해 자기 config 에 넣던 경로(`DashDataProcessor.cpp:2714-2719`)가 목적을 잃는다.

**Direct variant 의 케이스 이름은 입력 파일 basename 이다.** `key` 가 그것을 그대로 받는다 — `runs{K}` 를 가정하지 않는다.

### 5.5 엣지

```json
"upstream": { "references": [], "definitions": [],
              "executions": ["inst_2a8c5f019b3d"] }
```

**원소가 순수 `inst_` 다** — 다른 두 엣지와 같은 형이다. 지문은 계보(`consumed`)에만 있다(0.2 규칙 4).

| 소비자 | 생산자 | 현행 |
|---|---|---|
| DataPreprocessor | AnalysisLauncher | `Dataset.Selected DV-Table` · `Selected Analysis File` 을 쓰지만 **읽는 코드가 0곳**. 후보 목록은 `configs/AnalysisLauncher_*.json` 글로빙(`DashDataProcessor.cpp:295-297`) |
| ModelBuilder | DataPreprocessor | `Data Label.Dataset` — **XML 절대경로 문자열** |
| ModelRunner | ModelBuilder | `Model upload.Output Response[].set` — 절대경로. 목록은 프로젝트 루트에서 `ModelBuilder_*` 디렉토리를 훑어 `model_info.json` 이 있는 것만(`DashModelRunner.cpp:1245-`), 선택이 없으면 **`folders.first()`**(`view/DashModelRunnerWidget.cpp:744`) |
| Optimizer | ModelBuilder | `Optimization.trained_surrogate_model[]` `{model, response, symbol}`. 동상 — `folders.first()`(`view/DashOptimizerWidget.cpp:660-662`) |

**`folders.first()` 가 사라지는 것이 이 엣지의 첫 이득이다.** 지금은 사용자가 고른 것이 아니라 **정렬 순서가 고른 것**이 상위 바인딩이 된다.

### 5.6 시점

| | 시점 | 내용 |
|---|---|---|
| **메타 쓰기** | ① 실행 착수 | `rev` +1 · `state: Running` · `consumed` 고정 · `outputs` 비움 |
| | ② 실행 종결 | `state` 종결값 · `outputs` 기록 |
| **메타 읽기** | ① 프로젝트 열기 | 전량 — 배지 계산에 생산자의 `rev` 가 필요하다 |
| | ② 모듈 진입 | 자기 것(실행 상태 복원 · 계보 비교) + 생산자 것(`outputs` 로 목록 채우기 · `rev` 읽기) |
| | ③ 실행 착수 | 생산자 것 — `consumed` 에 고정할 값 |
| **엣지 쓰기** | 사용자가 상위 인스턴스를 고르는 순간 | `upstream.executions[]` — ID 만 |
| **엣지 읽기** | 모듈 진입 1회 + 실행 착수 | 폴링 없음 |

**계보는 재실행으로만 갱신된다.** `⚠ Stale` 은 상위를 다시 고른다고 풀리지 않는다 — 낡은 것은 바인딩이 아니라 **이미 만들어진 산출**이기 때문이다. 재실행이 `consumed` 를 그 시점의 현재로 다시 고정하면 배지가 풀린다. **재실행이 `Stale` 해소의 유일한 경로**이고, 그것이 지문을 엣지가 아니라 계보에 둔 이유이기도 하다.

---

## 6. 해석 사슬과 판정

### 6.1 ID 에서 실물까지 — 셋 다 파일에서 끝난다

| 엣지 | 소비자 SM 에 적히는 것 | 거치는 곳 | 실물 | 현재 지문을 어디서 |
|---|---|---|---|---|
| **reference** | `"ref_9b41e0c3f2a1"` | `project.json` → `references[].files.deck` | `{Root}/bracket_v3.inp` | `references[].fingerprint` — 저장된 값 |
| **definition** | `"inst_7f3a2c1b04de"` | `project.json` → `instances[].config` | `configs/GeometryParameter_Set1.json` (+ `.vtp`) | 그 SM 의 `rev` — 저장된 값 |
| **execution** | `"inst_2a8c5f019b3d"` | `outputs/inst_2a8c5f019b3d.json` → `outputs[].path` | `{Root}/DataPreprocessor_Set1/Max_Mises_Static.xml` | run 파일 `rev` — 저장된 값 |

**execution 사슬이 매니페스트를 거치지 않는다.** run 파일명이 곧 인스턴스 ID 라 조회가 파일 열기 1회다. 매니페스트는 그 인스턴스의 표시 이름(`label`·`module`)이 필요할 때만 본다.

### 6.1.1 판정 — 한 문장

```
소비자 run 파일 consumed[*] 의 "@" 뒷자리   vs   그 대상의 현재 지문
        (이 산출이 무엇의 몇 번째 판으로 만들어졌나)      (지금 무엇인가)
   ▼
다르면  ⚠ Stale     — 지금 보이는 결과가 최신 상위로 만들어진 것이 아니다
같으면  Complete    — 최신이다
run 파일이 없으면   — 아직 만든 것이 없다 (Ready | Draft)
```

**대상별 분기가 하나뿐이다** — "현재 지문을 어디서 얻나"(6.1 마지막 열). 비교 자체는 세 엣지가 같은 코드다.

### 6.2 모듈별로 어느 배열이 차나

| 소비자 SM                          |   `references[]`    |     `definitions[]`      |    `executions[]`    |
| ------------------------------- | :-----------------: | :----------------------: | :------------------: |
| `GeometryParameter_{Set}.json`  |   O — deck · part   |            —             |          —           |
| `ConditionParameter_{Set}.json` |      O — deck       |            —             |          —           |
| `AnalysisLauncher_{Set}.json`   | O — template · deck | O — Geometry · Condition |          —           |
| `DataPreprocessor_{Set}.json`   |          —          |            —             | O — AnalysisLauncher |
| `ModelBuilder_{Set}.json`       |          —          |            —             | O — DataPreprocessor |
| `ModelRunner_{Set}.json`        |          —          |            —             |   O — ModelBuilder   |
| `Optimizer_{Set}.json`          |          —          |            —             |   O — ModelBuilder   |

### 6.3 배지 6종

**엣지가 배지 넷을 정하고 계보가 둘을 정한다.**

| 배지 | 판정 입력 | 조건 |
|---|---|---|
| `Empty` | SM | 모듈 블록 본문이 없다 |
| `Draft` | SM `upstream` + 생산자 run 파일 | 착수할 수 없다 — `upstream` 이 비었거나 · 필수 엣지가 빠졌거나 · **상류에 아직 산출이 없다**(생산자 run 파일 없음 또는 `state != Done`) |
| `✕ Broken` | 엣지 + 매니페스트 | **가리킨 ID 가 매니페스트에 없다** — 끊긴 참조 |
| `Ready` | 엣지 + 자기 run 파일 | 상류가 준비됐는데 **자기가 아직 만든 것이 없다** |
| `Complete` | **계보** | 자기 run 파일이 `Done` 이고 `consumed` 의 `@지문` 이 **셋 다** 현재와 같다 |
| `⚠ Stale` | **계보** | 자기 run 파일이 `Done` 인데 `consumed` 의 `@지문` 중 하나라도 현재와 다르다 |

**`Broken` 과 `Draft` 를 가르는 것은 고칠 주체다.** "상류가 아직 안 돌았다" 는 **정상 초기 상태**이고 상류를 돌리면 풀린다 — 승격 직후 전 하류가 여기다. "가리킨 ID 가 없다" 는 사용자가 다시 지목해야 풀린다. 둘을 한 배지로 묶으면 갓 만든 프로젝트가 전부 고장난 것처럼 보인다.

**정의 인스턴스는 `Complete`·`Stale` 을 갖지 않는다.** Geometry·Condition 은 실행이 없어 run 파일이 없고, 계보가 없으면 견줄 대상도 없다 — 엣지 배지 넷(`Empty`·`Draft`·`Ready`·`✕ Broken`)에서 멈춘다. **그래서 기준 파일 교체는 그 둘의 화면이 아니라 하류(AnalysisLauncher · ModelRunner)에서 뜬다.** Morphing 의 구속이 메시 인덱스에 붙는 유일한 정의 데이터라 이 자리가 가장 아쉬운데, 정의 인스턴스에 계보를 주려면 실행 개체가 필요하므로 이 배포 밖이다.

**`Stale` 의 사유는 세 갈래이고 문구를 가른다.**

| 어긋난 배열 | 무엇이 바뀌었나 | 문구 |
|---|---|---|
| `consumed.references` | 기준 해석 파일이 **다시 등록**됐다 | "기준 파일이 교체됐습니다" |
| `consumed.definitions` | 상위 Geometry·Condition 정의가 바뀌었다 | "상위 정의가 바뀌었습니다" |
| `consumed.executions` | 상류가 재실행돼 산출이 덮였다 | "상류 결과가 다시 만들어졌습니다" |

셋을 한 문구로 뭉치면 사용자가 어디를 봐야 하는지 모른다. **판정은 공통 코드 한 벌이고 갈리는 것은 표시뿐이다.**

**`Stale` 에서 착수를 막지 않는다.** 착수가 `upstream` 을 그 시점의 현재로 해석해 `consumed` 에 다시 고정하므로 실행은 언제나 최신 상류를 읽는다 — **재실행이 `Stale` 해소의 유일한 경로다.** 막는 것은 `Draft` 와 `✕ Broken` 둘이고, 이유가 같다 — `consumed` 를 만들 수 없어 착수가 물리적으로 불가능하다. **문구는 갈라야 한다** — 앞은 "상류를 먼저 실행하세요", 뒤는 "끊긴 참조를 다시 지목하세요".

**전이 전파는 하지 않는다.** 상류가 `Stale` 이어도 그 하류는 자기 계보만 본다. 하류가 먹은 것은 상류의 **산출**이고 그 산출의 `rev` 는 상류의 상위가 바뀌었다고 오르지 않기 때문이다 — 상류가 재실행해야 비로소 오르고, 그때 하류가 `Stale` 이 된다. **전파는 재실행을 따라 한 칸씩 내려간다.**

---

## 7. I/O 시점 — 통합

| 사용자 행위 | PM `project.json` | SM `configs/*.json` | EM `outputs/*.json` |
|---|---|---|---|
| 프로젝트 생성 | **쓰기** — 빈 배열 둘 | — | — |
| 프로젝트 열기 | 읽기 1회 | 읽기 전량 (배지) | 읽기 전량 (`rev`·`state`·`consumed`) |
| `[Add File]` | **쓰기** — `references[]` + **해시 1회** | — | — |
| Set 생성 | **쓰기** — `instances[]` | **쓰기** — 빈 정의 | — |
| Set 삭제 | **쓰기** — 항목 제거 | 삭제 | 삭제 |
| Set rename | **쓰기** — `label`·`config` | — | — |
| 모듈 진입 | — | 읽기 + 배지 판정 | 읽기 — 자기 것 + 생산자 것 |
| 상위 선택 변경 | — | **쓰기** — `upstream` | — |
| 정의 편집 | — | **쓰기** — 현행 트리거 유지 + `rev`+1 | — |
| 실행 착수 | — | 읽기 — `upstream` 해석 + 생산자 `rev` | **쓰기** — `rev`+1 · `Running` · `consumed` 고정 |
| 실행 중 전이 | — | 현행 유지 — AL 케이스 상태 | — |
| 실행 종결 | — | — | **쓰기** — 종결 상태 · `outputs` |

**지문이 갱신되는 자리는 셋뿐이고 전부 쓰기 경로다.**

| 지문 | 갱신 시점 | 읽을 때 |
|---|---|---|
| 기준 해석 파일 | `[Add File]` 등록 — 해시 1회 | 저장된 값 조회 |
| 정의 (`rev`) | 정의 저장 — SM 저장 헬퍼가 +1 | 저장된 값 조회 |
| 산출 (`rev`) | 실행 착수 — +1 | 저장된 값 조회 |

넷이 따라 나온다.

- **매니페스트 쓰기는 5지점이고 전부 사용자 조작이다.** 실행 중에는 한 번도 쓰이지 않는다.
- **run 파일 쓰기는 실행 1회당 2번이다.** 케이스 수에 비례하지 않는다.
- **배지 판정에 계산이 없다.** 지문 셋이 전부 저장 값이라 파일을 읽기만 한다 — 수백 MB 급 `.vtp` 와 deck 을 배지 때문에 여는 일이 없다.
- **폴링이 늘지 않는다.** 읽기는 진입 1회 + 통지. 현행 ModelBuilder 1초 폴링은 그대로 남는다(도구 계약이 이 안 밖이다).

---

## 8. 승격 — 구프로젝트 1회 흡수

**파일을 옮기지 않으므로 구버전을 거부할 필요가 없다.**

```
[열기] .{name}.dproj 탐색  (현행 findDprojFolder 그대로)
   │
   ├─ project.json 있다 ──▶ 매니페스트만 읽는다. 글로빙 없음
   │
   └─ 없다 ──▶ [승격] loadSetsFromConfigs() 를 1회 돌린다
                 │   판정 결과(모듈 · variant · setName · config 경로)를
                 │   instances[] 로 적고 project.json 을 만든다
                 │   references[]  비운다 — 등록 레코드가 현행에 없다
                 │   upstream      비운다 — 기록된 상위 선택이 없거나 리더가 0곳이다
                 │   outputs/      만들지 않는다 — 산출이 몇 번 덮였는지 모른다
                 ▼
              이후 열기는 위쪽 갈래
```

**승격된 프로젝트는 모든 Set 이 `Draft` 다.** 사용자가 상위를 한 번 다시 고르고, run 파일은 첫 재실행에서 생긴다. **현행과 동등하다** — 지금은 열 때마다 다시 고른다.

**지문 셋 다 승격에 아무것도 요구하지 않는다.** 계보가 비어 있어 비교 대상이 자체가 없기 때문이다. 정의 `rev` 는 키 부재를 `0` 으로 읽고 첫 저장에서 `1` 이 되며, 산출 `rev` 는 첫 실행에서 생기고, 기준 해석 파일 지문은 `[Add File]` 재등록 때 계산된다.

**판정 코드가 사라지지 않고 호출부가 옮겨간다.** `loadSetsFromConfigs()` 와 `detectGeometryVariant`(`:621-`) · `detectBuilderVariant`(`:658-`)는 열기 경로에서 빠져 승격 경로 한 곳에서만 불린다. 상시 유지되는 하위호환 분기가 아니라 **1회 실행되는 입구**다.

**되돌리는 값이 싸다.** 물리 변화가 파일 추가뿐이라 승격 코드가 남아 있는 동안은 `project.json` 과 `outputs/` 를 지우면 현행 경로로 그대로 복귀한다.

---

## 9. 코드 전환

### 9.1 신설 — 접근자 3종

| 접근자 | 라이터 | API |
|---|---|---|
| 매니페스트 | **1곳** — 프로젝트 컨트롤러. 모듈은 읽기만 | 로드 · 저장(temp + rename) · `instances` 조회(id / (module,label)) · `references` 조회 · 항목 추가·제거 |
| run 파일 | **인스턴스마다 1곳** — 그 실행을 착수시킨 컨트롤러 | 로드(id) · 착수 기록 · 종결 기록 |
| **SM 저장 헬퍼** | 정의 라이터 전량이 통과 | 현재 `rev` 읽기 → +1 → temp + rename |

자리는 `model/` 또는 `controller/` — `DashProject` 가 이미 Set 귀속 데이터를 들고 있으므로 그 옆.

**SM 저장 헬퍼가 지문 때문에 생기는 유일한 기존 코드 수정이다.** (판정 주체 교체 8건은 별개다 — 9.2) 정의 라이터 5곳(Geometry 3벌 · Condition 2벌)을 "파일을 직접 쓴다" 에서 "헬퍼를 부른다" 로 바꾸는 기계적 변경이고, 얻는 것 셋 — `rev` 증가가 한 자리에 있어 **나중에 라이터를 붙이는 사람이 잊을 수 없고**, 규약 2(원자적 쓰기)가 같은 작업에서 서며, 규약 1(칸마다 라이터 1곳)이 정의 칸에서 실질적으로 성립한다.

### 9.2 판정 주체 교체

| # | 현행 판정 | 좌표 | 신 |
|---|---|---|---|
| 1 | **파일명 접두사로 모듈 판정** | `DashProject::loadSetsFromConfigs()` `model/DashProject.cpp:1066-` | `instances[]` 순회 |
| 2 | **Geometry variant 4단 폴백** — JSON `variant` → 최상위 `Morphing` 객체 → DV source 접두 → 이름 접미사 | `detectGeometryVariant()` `:621-` | `instances[].variant` 조회 1회 |
| 3 | **Builder variant 3단 폴백** — JSON `variant` → `endsWith("-MCU")` → `Sim` | `detectBuilderVariant()` `:658-` | 동상 |
| 4 | **접미사 직접 판정 14곳** | `endsWith("-MCU")` 10 · `endsWith("-CAD")` 2 · `endsWith("MCU")` 1 · `contains` 1 — `DashProject.cpp` 7 · `DashMainWindow.cpp` 3 · `DashModelRunner.cpp` 1 · `DashModelRunnerMCU.cpp` 1 · `DashSurrogateModelCommon.cpp` 1 | 매니페스트 조회 |
| 5 | **트리 아이템 `Qt::UserRole+2`** — variant 를 bool·string 두 형으로 병행 보관 | `view/DashMainWindow.cpp:1126`(bool) · `:1230`(string) · `:1381`(bool) | 트리는 `inst_` 를 들고 variant 는 매니페스트가 답한다 |
| 6 | **상위 산출 디렉토리 추정** — `folders.first()` | `view/DashModelRunnerWidget.cpp:744` · `view/DashOptimizerWidget.cpp:660-662` | `upstream.executions[]` → run 파일 `outputs[]` |
| 7 | **학습 모델 디렉토리 글로빙** — `modelName + "_*"` | `model/DashModelRunner.cpp:2306-2312` | `outputs[].path` 조회 |
| 8 | **케이스 게이팅** — 상류 SM 의 `status_{type}` 를 읽어 `Done` 만 거른다 | `model/DashDataProcessor.cpp:3016` · `:3039-3043` | 생산자 run 파일의 `outputs[]` (성공분만 적혀 있다) |

**4·5번이 "variant 가 3벌에 병행 보관된다" 의 실체다.** 셋 다 판정 자리에서 내려오고 `instances[].variant` 하나가 정본이 된다. JSON `variant` 키는 파일에 남되 읽지 않는다.

### 9.3 순서 — 6단계

각 단계 종료 시 빌드·실행 가능하다.

```
S1  매니페스트 파일 · 접근자 · 쓰기 5지점              [현행 동작 무변경]
    │  아무도 읽지 않는 상태로 먼저 만든다 — write-only
    │  verify: Set 3개 생성·1개 삭제·1개 rename 후 project.json 이 configs/ 실체와 일치
    ▼
S2  승격 + 열기 경로 교체                              [글로빙 호출부 이동]
    │  verify: 구프로젝트 열기 → project.json 생성 → 재열기에서 글로빙 미실행
    ▼
S3  variant 판정 교체 — 9.2 의 2~5번                   [접미사 판정 14곳]
    │  verify: -MCU · -CAD Set 이 각 모듈에서 정상 진입
    │          project.json 의 variant 를 손으로 고치면 판정이 따라온다
    ▼
S4  upstream 3배열 + reference·definition 엣지 배선    [상위 선택이 복원된다]
    │  verify: 상위를 고르고 프로젝트를 닫았다 열면 선택이 복원된다
    │          상위 Set 을 지우면 소비자가 ✕ Broken
    ▼
S5  run 파일 + execution 엣지 + outputs               [사슬이 파일에서 끝난다]
    │  verify: folders.first() · 모델 디렉토리 글로빙 · 케이스 게이팅 호출부 0
    │          상류 산출을 하류가 목록으로 받는다
    ▼
S6  SM 저장 헬퍼 + 지문 3종 + consumed + 배지 6종       [낡음이 화면에 뜬다]
       verify: 상위 Geometry 를 고치면 AL 이 ⚠ "상위 정의가 바뀌었습니다"
               상류를 재실행하면 하류가 ⚠ "상류 결과가 다시 만들어졌습니다"
               기준 파일을 다시 등록하면 ⚠ "기준 파일이 교체됐습니다"
               각각 재실행하면 Complete 로 풀린다
```

**S5 와 S6 을 가르는 이유는 검증 대상이 다르기 때문이다.** S5 는 "닿나", S6 은 "낡음을 아나" 다. S5 까지만 해도 현행보다 낫고(디스크 스캔이 없어진다), S6 이 사용자에게 보이는 값을 만든다.

---

## 10. 범위 밖 — 이 배포에 없는 것

**자리를 미리 만들지도 않는다.** "첫 배포 후에는 스키마를 바꿀 수 없다" 는 제약은 **쓴 필드**에 걸리고, 쓰지 않은 필드를 비워 두는 것은 계약이 아니다.

| 뺀 것 | 근거 |
|---|---|
| 실행 ID · 실행 이력 · `executions/{label}/` 누적 | 실행을 개체로 두지 않는다. 재실행은 덮어쓴다 |
| 정의 본문 스냅샷(`input.json`) | `consumed` 가 좌표만 담는다 (5.3) |
| 산출물 대장 전량 — 부산물 · 실패 케이스 · 케이스 실패 사유 · 스테이지 상태 · 정리 표시 | `outputs` 는 소비자가 여는 것만 (5.4) |
| 로컬 ID — DV · 응답 · 학습 모델 | 의존성 단위가 인스턴스다. 항목 단위 조인은 현행 이름 조인 유지 |
| **지문의 항목 단위 해석** — "무엇이 바뀌었나" | 지문은 "바뀌었나" 까지만 답한다. 어느 DV·어느 응답이 바뀌었는지는 로컬 ID 가 있어야 하므로 함께 미뤄진다 |
| **`Stale` 의 전이 전파** | 재실행을 따라 한 칸씩 내려간다 (6.3) |
| 파일 이동 — `references/` · 인스턴스 디렉토리 · `configs/` 폐기 | 3루트 유지가 전제다 |
| 도구 계약 변경 — 상태를 stdout 으로, 도구 쓰기를 실행 벌크 안에 가둠 | ModelBuilder 1초 폴링과 도구의 SM 되쓰기가 남는다. 도구를 함께 릴리스해야 하는 순서 제약이 이 안에는 없다는 뜻이기도 하다 |
| AL 케이스 상태 전이의 자리 이동 | 전이마다 SM 전문 재작성(총 I/O 가 케이스 수의 제곱)은 별 작업이다 (5.4) |
| **기준 해석 파일의 제자리 수정 탐지** | 지문이 등록 시 동결이라 앱 밖 편집이 잡히지 않는다(3.3). 잡으려면 비교 시점에 `(size, mtime)` stat 이 들어가고, 그 값을 어디에 캐시할지가 새 결정이 된다 |
| Results Analyzer 뷰 설정 파일 · 파생 캐시 | 지금 들어갈 것이 없다 |
| 마이그레이션 · 구버전 거부 | 승격으로 대체한다 (8절) |

**남는 것 둘.**

| 남는 것 | 실측 | 판정 |
|---|---|---|
| **경로 규약 불일치** — "어느 모듈 산출이 숨김으로 가나" 에 답하는 자리가 다섯인데 서로 다르다 | 실제 조립은 `getModuleDir()`(`DashIOController.cpp:24-43`, ModelBuilder 만 숨김) 하나이고 호출부 25곳. 어긋나는 셋은 `ModuleType` enum 주석 · `isUserOutputType()`(`:106-112`, **호출부 0곳** — 죽은 코드) · MCU 우회(`DashModelBuilderMCU.cpp:554-562`) | 조립 규칙을 `getModuleDir()` 하나로 인정한다. run 파일의 `outputs[].path` 는 그 결과를 **루트 상대로 적은 값**이라 25곳을 건드리지 않는다 |
| **`configs/` 안 두 번째 복사본** — `.dat` · `.prt` 가 `{Root}/` 원본과 별개로 한 벌 더 있다(`DashGeometryParameterCADWidget.cpp:622-637`) | 등록 레코드가 없어 모듈이 자기가 쓸 파일을 자기 옆에 복사해 둔 것이다. Reference 표를 채우는 `findAnalysisFiles()`(`DashReferenceFileWidget.cpp:438-498`)가 훑는 `configs` 는 `{Root}/configs` 라 **실제 자리에 도달하지 않는다** | `references[]` 가 생기면 목적을 잃지만, 없애려면 각 모듈이 등록 경로를 읽도록 바꿔야 한다 — 이 안 **이후에 가능해지는 것**으로 기록해 둔다 |

---

## 11. 되돌리기 어려운 결정 · 미결

### 11.1 배포 전에 확정할 것

| # | 결정 | 답 |
|---|---|---|
| 1 | `$schema` 번호 축 | `1` |
| 2 | 전역 ID 형식 | 접두사 + 12-hex. 48비트라 항목 10⁴개에서 충돌이 약 2×10⁻⁷ |
| 3 | `upstream` 키 이름과 원소 형 | `references` · `definitions` · `executions` — 셋 다 배열, 원소는 **순수 ID** |
| 4 | **지문의 자리** | 엣지가 아니라 계보(`consumed`)에만. 원소 형 `{ID}@{지문}` (0.2 규칙 4 · 5.3) |
| 5 | **지문 3종의 방식** | 셋 다 **저장**. 기준 파일 `sha256`(PM) · 정의 `rev` 정수(SM) · 산출 `rev` 정수(run 파일). 읽기 시점 계산 0 (5.2) |
| 6 | 정의 `rev` 의 자리와 뜻 | **SM 자기 파일** · 정의가 저장된 횟수. SM·SB 가 한 쓰기 단위라 SB 변경까지 덮는다 (4.3) |
| 7 | 경로 기준 | 프로젝트 루트 상대 + 숨김 루트는 `.dproj/` 토큰 (1절 배치 · 2절 `config` 값) |
| 8 | run 파일의 자리와 이름 | `.dproj/outputs/{inst_id}.json` |
| 9 | 산출 `rev` 의 의미 | **덮어쓴 횟수**, 착수 시 +1, 실패해도 되돌리지 않는다. **SM 으로 옮기지 않는다** (5.2) |
| 10 | `outputs` 의 범위 | 소비자가 여는 것만 · 성공분만 (5.4) |

### 11.2 미결

| # | 항목 | 정해야 할 것 |
|---|---|---|
| 1 | **다중 인스턴스** | 같은 프로젝트를 두 창에서 여는 경우. 잠금 파일·단일 인스턴스 가드가 현행 레포에 0건이라 두 창이 `project.json` 과 run 파일을 함께 쓴다. 매니페스트 쓰기 지점이 5개(전부 사용자 조작)라 창이 좁지만, run 파일은 두 창이 같은 인스턴스를 동시에 실행하면 겹친다 |
| 2 | **비정상 종료 후 `Running`** | GUI 가 죽으면 run 파일이 `Running` 으로 남는다. 재진입 시 `Failed` 로 마감할지, 미종결로 표시만 할지 |
| 3 | **`[Add File]` 필터** | 넣는 쪽 12종(`DashMainWindow.cpp:2118-2119`)과 Reference 표에 띄우는 쪽 6종(`DashReferenceFileWidget.cpp:448`)이 어긋난다 — `.wbpj`·`.cdb` 는 목록에 뜨는데 넣을 수 없고, `.vtk`·`.vtu`·`.rst`·`.odb`·`.csv`·`.stp` 는 넣을 수 있는데 역할 4종에 자리가 없다 |
| 4 | **`kind` 어휘** | `fe`\|`cad` 둘로 충분한지. FE-safe 가 세 번째인지 `fe` 의 하위인지 |
| 5 | **Reference 하나에 같은 역할 파일이 둘** | 다부품 어셈블리에서 `.prt` 가 둘이면 `files` 역할 맵이 깨진다. 깨지면 `files` 가 배열이 되고 로컬 ID 가 하나 생긴다 |
| 6 | **승격 시 `outputs` 채우기** | 8절은 만들지 않는다로 두었으나, 디스크 스캔 1회로 기존 산출을 `rev: 0` 으로 굳히는 선택지가 있다. 승격 프로젝트가 상위 선택을 어차피 다시 골라야 하므로 이득이 작다는 판정이나, 재실행 비용이 큰 자산이면 다시 본다 |
| 7 | **Set 분기** | 현행에 기능이 없다. 만든다면 `instances[]` 항목 신규 + SM 복사이고 run 파일은 복사하지 않는다(정의는 이어받고 결과는 새로 만든다) |
| 8 | **정의 `rev` 의 오탐 허용치** | 값을 고쳤다 되돌려도 `rev` 는 오른다(4.3). 실무에서 그 빈도가 배지 신뢰를 깎을 만하면, 내용 비교를 얹을 자리는 SM(작다)뿐이고 SB(수백 MB)는 여전히 불가라 **SM 만 해시 + SB 는 `rev`** 라는 혼합안이 후보다 |
| 10 | **`.vtp` 재작성 비용** | SB 가 수백 MB 인데 정의 저장마다 전문 재작성된다(`filterSelectedHandles`). 이 안의 대상은 아니지만 `rev` 증가가 곧 그 쓰기라, 저장 빈도를 낮추는 작업(규약 11 — dirty 신호 + 디바운스)과 같은 자리를 본다 |
| 9 | **SB·SM 쓰기 순서** | `saveMorphingSettings` 가 `.vtp` 를 먼저 쓰고 `.json` 을 나중에 쓴다(`viewmodel/DashGeometryParameterPresentationModel.cpp:348-351` → `:377-`). 사이에 크래시하면 SB 는 새것인데 SM `rev` 는 옛것이라 하류가 최신인 줄 안다. 창이 좁지만 0 은 아니다 — 두 쓰기를 한 단위로 묶을지, `rev` 를 먼저 올릴지 |
