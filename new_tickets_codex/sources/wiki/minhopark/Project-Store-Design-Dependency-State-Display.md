# 의존성과 상태의 화면 표시 — 저장 구조 설계 · 화면 층

> 관련 Issue: #239
>
> 기반 문서: [[Project-Store-Design-Edge-Complete-Minimal]] — 배지 6종과 판정 규칙(6.3)의 정본. **이 문서는 그 판정 결과를 어디에 어떻게 띄우는가만 다루고 판정 규칙도 저장 스키마도 바꾸지 않는다.** 저장에 더하는 필드가 0 이다
>
> 실측 기준: `dev` @ `4c7608e` + 작업 트리. 빌드·실행 검증 없음, 정적 근거만.

> ## ⚠ 문서 상태: 구상 — 확정 아님
>
> 팀 합의 전 · 착수 승인 전. 여기의 위젯 이름·문구를 계약으로 인용하지 않는다.

## 개요

기반 문서는 배지 6종을 **계산**까지 끝내 놓고 **표시**를 열어 두었다. 남은 질문이 둘이다 — 사용자가 "지금 이 모듈이 무엇에 매달려 있나" 를 어디서 보고, "그것이 READY·DRAFT·STALE·COMPLETE·BROKEN 중 무엇인가" 를 어디서 보는가.

**답은 한 자리가 아니라 세 자리다.** 두 질문이 서로 다른 시점에 뜨고 요구하는 정보 밀도가 다르기 때문이다 — 프로젝트를 열자마자 "어디가 문제인가" 를 훑을 때와, 그 모듈에 들어와 "왜 낡았고 무엇을 해야 하나" 를 볼 때가 같은 화면일 수 없다.

| 층 | 자리 | 답하는 질문 | 밀도 |
|---|---|---|---|
| **1** | 모듈 트리 Set 아이템 | 어디가 문제인가 | 아이콘 1개 |
| **2** | 우측 독 상단 의존성 스트립 | 무엇에 매달려 있고 무엇이 낡았나 | 1줄 → 펼치면 엣지 표 |
| **3** | 실행 버튼 · 툴팁 · 로그 | 지금 착수할 수 있나 · 무엇을 했나 | 차단과 기록 |

**세 층이 같은 판정을 세 밀도로 되풀이한다.** 판정 코드는 한 벌이고(6.1.1) 층마다 갈리는 것은 표시뿐이다.

---

## 0. 전제

### 0.1 표시 대상 — 배지 6종과 그 원인

배지는 인스턴스 1개당 하나인데 **원인은 엣지에 있다.** 그래서 화면이 실제로 다루는 값은 둘이다 — 인스턴스 배지 1개와 그 인스턴스가 가진 엣지마다의 상태.

엣지 상태 5종은 **새 저장이 아니다.** 6.1.1 의 판정이 배지를 내기 위해 이미 만드는 중간값이고, 화면은 그 중간값을 버리지 않고 표에 적을 뿐이다.

| 엣지 상태 | 조건 | 이 엣지가 인스턴스 배지에 미치는 것 |
|---|---|---|
| `Unset` | 그 배열이 비었는데 6.2 에서 필수다 | `Draft` |
| `Broken` | 가리킨 ID 가 매니페스트(또는 run 파일)에 없다 | `✕ Broken` |
| `Waiting` | 생산자 run 파일이 없거나 `state != Done` (execution 엣지 한정) | `Draft` |
| `Stale` | `consumed` 의 `@지문` 이 현재와 다르다 | `⚠ Stale` |
| `Current` | 일치한다 | `Complete` 후보 |

**인스턴스 배지 = 엣지 상태의 최악값에 자기 run 상태를 얹은 것이다.** 우선순위가 배지 어휘를 그대로 재현한다.

```
✕ Broken   ←  엣지 하나라도 Broken
   ▼ 아니면
Draft      ←  엣지 하나라도 Unset · Waiting
   ▼ 아니면
⚠ Stale    ←  자기 run 이 Done 이고 엣지 하나라도 Stale
   ▼ 아니면
Complete   ←  자기 run 이 Done 이고 엣지 전부 Current
Ready      ←  엣지 전부 Current 인데 자기 run 파일이 없다
Empty      ←  SM 모듈 블록 본문이 없다
```

**정의 인스턴스는 이 사다리의 위 세 칸만 쓴다.** Geometry·Condition 은 실행이 없어 run 파일이 없고 계보가 없다(6.3) — `Complete`·`⚠ Stale` 이 서지 않고 `Empty`·`Draft`·`Ready`·`✕ Broken` 넷에서 멈춘다. 화면도 그 넷만 낼 수 있어야 하며, 그 둘의 스트립은 reference 행 하나뿐이다.

### 0.2 현행 화면에 이 값을 놓을 자리가 없다 — 실측

| # | 실측 | 좌표 |
|---|---|---|
| 1 | **모듈 트리 Set 아이템에 아이콘도 툴팁도 없다.** 카테고리 아이템만 SVG 를 갖고 Set 은 텍스트뿐이다. `DecorationRole` 슬롯이 비어 있고 뷰의 `iconSize` 는 이미 24 다 | `DashProject::createCategoryItem()` · `addGeometryParameter()`(`model/DashProject.cpp:119-133`) · `DashMainWindow.cpp:449` |
| 2 | **모듈 트리에 델리게이트가 없다.** 파일 트리 쪽에는 있다 — `ProjectFileTreeDelegate` 가 우측 정렬 `Load` 버튼을 직접 그린다(35×15 라운드 사각) | `view/DashProjectWidget.cpp:16-22` · `view/delegate/ProjectFileTreeDelegate.cpp:104-147` |
| 3 | **모듈 위젯에 공통 헤더가 없다.** 7 모듈 전부 `.ui` 최상위가 `QTabWidget` 이라 배지를 놓을 공통 띠가 없다 | `ui/DashDataProcessorWidget.ui:11-21` 등 |
| 4 | **상태 아이콘 어휘는 이미 있다 — 케이스·모델 표 안에만.** `getStatusIcon()` 이 `Running`·`Done`·`Failed` 3종을 내고 호출부가 9곳인데 전부 표 셀이다 | `view/common/DashWidgetHelpers.cpp:9-19` · `DashDoeCasesWidget` 3 · `DashModelBuilderWidget` 4 · `DashModelBuilderMCUWidget` 2 |
| 5 | **상위 선택 컨트롤은 있는데 상태가 없다.** 6모듈에 콤보가 흩어져 있고 값이 복원되지 않으며(리더 0곳) 일부는 사용자가 아니라 정렬 순서가 고른다(`folders.first()`) | `dvGeometryCombo`·`dvConditionCombo`(AL) · `dvTableComboBox`·`analysisFileComboBox`(DP) · `dataPreprocessorDirCombo`·`datasetFileCombo`(MB) · `m_modelBuilderFolderComboBox`(MR) · `m_modelBuilderFolderCombo`(Opt) |
| 6 | **Geometry·Condition 은 콤보조차 없다.** 기준 파일을 전역 활성 컨텍스트로 따라가서 화면에 "이 Set 은 무엇 기준인가" 가 뜨는 자리가 아예 없다 | 기반 문서 3.2 |

**5·6번이 이 화면 층의 진짜 이유다.** 배지만 붙이면 사용자는 "낡았다" 는 것만 알고 **무엇이** 낡았는지 볼 자리가 여전히 없다. 그래서 이 문서는 배지와 의존성 목록을 같은 자리에 둔다.

### 0.3 화면 문구는 영문이다

현행 GUI 는 영문 전용이다 — `.ui` 16종에 한글 문자열 0건, 번역 카탈로그(`.ts`) 0건, `tr()` 83곳은 감싸기만 하고 대응 번역이 없다. 기반 문서 6.3 이 적은 한글 사유 문구("기준 파일이 교체됐습니다")는 **설계 표기이지 화면 문자열이 아니다.** 화면은 영문으로 쓰고 관례대로 `tr()` 로 감싼다.

---

## 1. 층 1 — 모듈 트리 배지

### 1.1 6종을 4등급으로 접는다

**트리는 전역 스캔용이라 6종을 다 내면 안 된다.** 인스턴스가 수십인 화면에서 아이콘 6종은 구분되지 않고, 무엇보다 **`Draft` 는 정상 초기 상태**다 — 승격 직후 전 하류가 `Draft` 이므로(8절) 여기에 경고색을 주면 갓 흡수한 프로젝트가 통째로 고장 난 것처럼 보인다. 6.3 이 `Broken` 과 `Draft` 를 가른 논리가 색에도 그대로 걸린다.

| 등급 | 배지 | 트리 아이콘 | 조달 |
|---|---|---|---|
| **차단** | `✕ Broken` | `status_failed.svg` | **있다** — 재사용 |
| **주의** | `⚠ Stale` | 경고 1종 | **신설** — 색 미정(4절) |
| **최신** | `Complete` | `status_done.svg` | **있다** — 재사용 |
| **조용** | `Empty` · `Draft` · `Ready` | 없음 | — |

**신설 아이콘이 1종뿐이다.** 나머지 둘은 케이스 표가 이미 쓰는 파일이라 어휘가 화면 전체에서 한 벌로 유지된다.

**조용 3종을 트리에서 구분하지 않는 손실은 두 자리가 갚는다** — 층 2 의 스트립이 배지 이름을 글자로 적고, 층 3 의 실행 버튼 비활성이 "지금 착수할 수 없다" 를 직접 말한다.

### 1.2 방식 — `DecorationRole` 을 고른다

| 방식 | 코드 | 장점 | 단점 |
|---|---|---|---|
| **`Qt::DecorationRole` + `Qt::ToolTipRole`** | 아이템 `setData` 2줄 | 델리게이트 0 · 인라인 rename(`setEditable(true)`)과 무충돌 · `iconSize(24)` 이미 설정 | 단어가 안 보여 툴팁에 의존 |
| 델리게이트 우측 pill | 새 델리게이트 1종 | 단어가 보인다 · `ProjectFileTreeDelegate` 선례 | 트리 폭 경쟁(`Set1-Morphing` 같은 라벨) · 편집기와 겹침 처리 · 클릭 히트박스가 `mousePressEvent` 의 `new_set` 분기와 얽힌다 |

**`DecorationRole` 을 고른다.** 등급이 셋이라 아이콘으로 충분하고, 단어가 필요한 자리는 층 2 가 이미 답한다. 델리게이트는 얻는 것에 비해 건드리는 코드가 많다.

### 1.3 툴팁 — 아이콘이 못 하는 말

`Qt::ToolTipRole` 에 3줄. 배지 이름이 여기서 처음 글자로 나온다.

```
Stale
Upstream definition changed — Geometry Set1 (rev 3 → 5)
Re-run to refresh
```

조용 등급도 툴팁은 갖는다 — 아이콘이 없을 뿐 `Draft` 인지 `Ready` 인지는 여기서 갈린다.

---

## 2. 층 2 — 우측 독 상단 의존성 스트립

### 2.1 자리 — 코드 한 곳

**우측 독이 모듈 위젯 7종을 `QStackedWidget` 하나로 들고 있다.** 그 스택 위에 띠를 하나 얹으면 전 모듈이 한 벌로 덮인다.

```cpp
// 현행 — view/DashMainWindow.cpp:458-462
m_rightDock = new QDockWidget("Parameters", this);
m_rightStackedWidget = new QStackedWidget(this);
m_rightDock->setWidget(m_rightStackedWidget);

// 신 — 컨테이너 1개를 끼운다
auto* host = new QWidget();
auto* v = new QVBoxLayout(host);
v->setContentsMargins(0, 0, 0, 0);
v->setSpacing(0);
v->addWidget(m_dependencyBar);        // ★ 신설
v->addWidget(m_rightStackedWidget);
m_rightDock->setWidget(host);
```

**이 자리를 고르는 근거 셋.**

| # | 근거 |
|---|---|
| 1 | **`.ui` 7개를 건드리지 않는다.** 모듈마다 헤더를 넣으면 `.ui` 7 파일 + 위젯 클래스 7벌에 같은 배선이 복제되고, 나중에 모듈이 하나 늘면 잊힌다 |
| 2 | **갱신 배선이 신호 1개에 붙는다.** 모듈 전환의 단일 입구가 `DashMainWindow::handleSubItemSelection()`(`:980`, 카테고리 분기 `:1053-1095`)이라 스트립 갱신을 그 끝에 한 줄로 단다 |
| 3 | **인스턴스가 아닌 화면은 숨기면 된다.** 스택에는 Geometry AI Generation 처럼 인스턴스가 아닌 위젯도 있다 — `currentChanged` 에서 hide |

### 2.2 접힘 — 1줄

기본은 접힘이다. 폭을 항상 먹는 것은 한 줄뿐이다.

```
⚠ Stale   Set1-Morphing      Reference file was replaced        [ Details ▾ ]   [ Re-run ]
```

| 칸 | 내용 |
|---|---|
| 배지 | 아이콘 + 이름. 층 1 의 4등급이 아니라 **6종 전부** — 여기는 좁지 않다 |
| 인스턴스 | `instances[].label` (+ variant) |
| 사유 | 6.3 의 `Stale` 3갈래를 그대로 받는다. 갈래가 둘 이상이면 `2 issues` 로 접고 펼침에서 나눈다 |
| 조치 | 배지마다 하나 — `Stale` → `Re-run` · `Draft` → `Run upstream` · `Broken` → `Re-select` |

**조치 버튼이 배지마다 다른 것이 6.3 의 "문구를 갈라야 한다" 를 화면에서 지키는 방법이다.** 셋을 한 버튼으로 뭉치면 사용자가 재실행으로 풀리는 줄 안다.

### 2.3 펼침 — 엣지 표

`Details` 를 펴면 그 인스턴스의 `upstream` 3배열이 행으로 선다.

| Kind | Bound to | State | |
|---|---|---|---|
| Reference · deck | Bracket v3 | ⚠ Replaced — `sha256:9b41e0` → `4c2a71` | `[ Open ]` |
| Definition | Geometry Set1 | ⚠ Changed — `rev 3` → `5` | `[ Open ]` |
| Execution | DataPreprocessor Set1 | Current — `rev 7` | `[ Open ]` |

**계보 값과 현재 값을 나란히 적는 것이 이 표의 값이다.** "낡았다" 만으로는 얼마나 낡았는지, 무엇을 다시 봐야 하는지 알 수 없다. `rev 3 → 5` 는 상위 정의가 두 번 저장됐다는 뜻이고, 해시는 앞 6자리로 자르되 전문은 셀 툴팁에 둔다.

**행 구성은 6.2 표가 그대로 정한다** — 모듈마다 행 수가 다르다.

| 모듈 | 행 |
|---|---|
| GeometryParameter | Reference 1 (Morphing `deck` · CAD `part`) |
| ConditionParameter | Reference 1 (`deck`) |
| AnalysisLauncher | Reference 2 (`template`·`deck`) + Definition 2 (Geometry·Condition) |
| DataPreprocessor | Execution 1 (AnalysisLauncher) |
| ModelBuilder | Execution 1 (DataPreprocessor) |
| ModelRunner | Reference 1 + Definition 1 + Execution 1 — **엣지 3종이 다 차는 유일한 인스턴스** |
| Optimizer | Execution 1 (ModelBuilder) |

**빈 배열은 행을 만들지 않되 `Unset` 행은 만든다.** 6.2 에서 `O` 인 자리가 비어 있으면 그것이 `Draft` 의 사유이므로 화면에 나와야 하고, `—` 인 자리는 애초에 그 모듈에 없는 엣지라 행이 아니다. **무엇이 필수인가의 정본은 6.2 표다.**

### 2.4 `Open` 이 하는 일

행의 `Open` 은 그 상위 인스턴스를 트리에서 선택한 것과 같다 — 모듈 전환의 입구가 `handleSubItemSelection()` 하나라 스트립이 그 함수를 부르면 끝이고, 새 항해 경로를 만들지 않는다. **상류를 열어 보는 것이 `Draft`·`Stale` 해소의 실제 동선**이기 때문에 이 링크가 조치 버튼만큼 쓰인다.

---

## 3. 층 3 — 착수 차단 · 툴팁 · 로그

**가장 강한 표시는 배지가 아니라 버튼이 안 눌리는 것이다.**

| 표면 | 내용 | 근거 |
|---|---|---|
| **실행 버튼 비활성** | `Draft` · `✕ Broken` 에서 막고 툴팁에 사유. `⚠ Stale` 은 **막지 않는다** | 6.3 — 착수가 `upstream` 을 그 시점 현재로 해석해 `consumed` 를 다시 고정하므로 재실행이 `Stale` 해소의 유일한 경로다 |
| **로그 1줄** | 실행 착수 때 고정된 `consumed` 를 `logMessage` 로 남긴다 — `consumed: ref_9b41e0c3f2a1@sha256:9b41e0, inst_7f3a2c1b04de@3` | 로그 독이 이미 있다(`m_logDock`). 배지는 "지금" 만 말하고 로그는 사후 추적을 남긴다 |
| **statusBar** | **쓰지 않는다** | 상주 안내 문구가 이미 점유하고 있고(`DashMainWindow.cpp:292`) 순간 메시지는 놓친다 |

---

## 4. 색과 아이콘

**신규 색이 하나 필요하고 그것이 이 화면 층의 유일한 디자인 결정이다.**

| 배지 | 토큰 | 상태 |
|---|---|---|
| `Complete` | `DashPalette::Accent` `#34BCFF` | 있다 — `status_done.svg` 의 stroke 와 같은 값 |
| `✕ Broken` | `DashPalette::Error` `#E53935` | 있다 |
| `⚠ Stale` | **없다** | 팔레트에 경고(amber) 계열이 0 |
| `Draft` · `Ready` | `DashPalette::TextMuted` / `IconNeutral` | 있다 — 조용 등급이라 트리에는 안 뜬다 |

**경고색을 `Error` 로 대신하면 안 되는 이유 하나.** 이 표시의 존재 이유가 "사용자가 낡은 결과를 최신으로 읽는다"(현황 6)를 막는 것인데, **주의를 차단과 같은 색으로 칠하면 사용자가 둘 다 무시하거나 둘 다 막힌 줄 안다.** `⚠ Stale` 은 착수를 막지 않고 `✕ Broken` 은 막으므로 색이 갈려야 한다.

토큰 신설은 `DangerTint` 2종이 W13 트랙에서 추가된 선례를 따른다 — 디자이너 확정 대기(#242).

**부수 실측 하나.** `status_failed.svg` 의 stroke 는 `#FF4242` 인데 `DashPalette::Error` 는 `#E53935` 다. 그 아이콘을 배지에 재사용하면 팔레트 밖 색이 한 벌 더 들어온다. **이 문서의 대상이 아니므로 지적만 한다.**

---

## 5. 갱신 배선 — 배지가 낡지 않게

**판정에 계산이 없다는 것과 판정이 저절로 다시 돈다는 것은 다르다.** 지문 셋이 전부 저장 값이라 비교는 공짜지만(7절), 언제 다시 비교하는가는 배선이다. 폴링 금지(규약 10)를 지키면서 트리거는 여섯이고 전부 쓰기 경로 뒤에 붙는 신호다.

| 트리거 | 무엇이 바뀌나 | 화면 갱신 |
|---|---|---|
| 프로젝트 열기 | 전량 | 트리 전량 + 스트립 |
| `[Add File]` 재등록 | `references[].fingerprint` | 그 ref 를 계보에 가진 인스턴스 |
| 정의 저장 (SM 헬퍼) | 정의 `rev` | 그 인스턴스를 `consumed.definitions` 에 가진 것 |
| 실행 착수 | 자기 `rev` · `consumed` | 자기 + 하류(상류 `rev` 가 올라 하류가 `Stale` 이 된다) |
| 실행 종결 | 자기 `state` · `outputs` | 자기 + 직하류(`Waiting` 이 풀려 `Draft` → `Ready`) |
| 상위 선택 변경 | `upstream` | 자기만 |

**부분 무효화를 설계하지 않는다.** 트리거마다 전 인스턴스를 다시 판정한다 — 파일을 읽지 않고 메모리의 정수·문자열을 견주는 일이라 인스턴스 수십 개에서 즉시 끝난다. 역방향 인덱스("누가 나를 계보에 갖고 있나")를 배지 때문에 만들지 않는다. 저장 규칙 2 가 역방향을 이미 로드 시 계산으로 두었고, 배지는 그 계산을 다시 돌리면 된다.

**배지가 폴링을 새로 만들지 않는다.** ModelBuilder 만 외부 도구가 SM 을 되쓰고 GUI 가 1초 폴링으로 읽는데(5.1), 그 폴링이 `Done` 을 본 순간이 곧 run 파일 종결 쓰기이고 그 쓰기가 배지 갱신 신호다. 현행 폴링 1건이 그대로 남을 뿐 늘지 않는다.

---

## 6. 기각한 대안

| 안 | 기각 사유 |
|---|---|
| **그래프 뷰** — 노드·엣지 다이어그램 | 파이프라인이 선형 7단이라 표가 그래프보다 읽기 쉽고, 인스턴스가 수십이면 다이어그램이 먼저 무너진다. 새 렌더링 위젯이 드는 값이 없다 |
| **트리 자식 노드로 upstream 표시** | 모듈 트리가 이미 카테고리 8 × Set N 인데 손자 층을 더하면 스캔이 무너진다. Set 아이템이 인라인 rename 대상이라 종류가 섞이면 편집이 오작동한다 |
| **모달 다이얼로그** | 상태는 상시 보여야 한다. 모달은 "지금 확인하고 닫는" 형이라 낡음 경고와 형이 맞지 않는다 |
| **기존 콤보 옆 인라인 배지만** | 콤보가 6모듈에 흩어져 있고 Geometry·Condition 은 콤보 자체가 없다(0.2-6). 균일한 자리가 되지 못한다 |
| **배지를 저장한다** | 파생값이라 정본이 둘이 된다. 지문 셋만 저장하고 배지는 매번 만드는 것이 기반 문서의 전제다 |
| **`Stale` 전이를 하류로 전파해 표시** | 6.3 — 전파는 재실행을 따라 한 칸씩 내려간다. 화면이 먼저 전파하면 저장 값과 화면이 어긋난다 |

---

## 7. 순서 — S6 안에서 셋으로 자른다

기반 문서 9.3 의 **S6**(지문 3종 + `consumed` + 배지)이 이 화면 층의 상류다. 판정이 없으면 표시할 값이 없으므로 순서는 고정이고, S6 안에서 다시 셋으로 자른다.

```
V1  트리 배지 4등급 + 툴팁                       [어디가 문제인지 보인다]
    │  아이콘 2종 재사용 + 경고 1종 신설, DecorationRole·ToolTipRole 만
    │  verify: 상위 Geometry 저장 → AL Set 에 주의 아이콘, 툴팁에 rev 3 → 5
    │          승격 직후 프로젝트에 경고 아이콘 0개 (전부 Draft = 조용)
    ▼
V2  우측 독 스트립 접힘 1줄 + 조치 버튼           [사유와 다음 행동이 보인다]
    │  DashMainWindow.cpp:458-462 컨테이너 1곳, 갱신은 handleSubItemSelection 끝
    │  verify: 모듈 7종 전환에 스트립이 따라오고, 인스턴스 아닌 화면에서 사라진다
    │          Draft·Broken 에서 실행 버튼이 비활성이고 Stale 에서는 눌린다
    ▼
V3  스트립 펼침 엣지 표 + Open 링크               [무엇이 얼마나 낡았는지 보인다]
       verify: ModelRunner 에서 3행(Reference·Definition·Execution)이 다 뜬다
               Geometry 에서 1행만 뜨고 Complete·Stale 이 나오지 않는다
               필수 엣지가 비면 Unset 행이 서고 그것이 Draft 사유로 접힘 줄에 뜬다
```

**V1 과 V2 를 가르는 이유는 대상이 다르기 때문이다.** V1 은 "프로젝트 전체에서 어디를 볼까" 이고 V2 는 "이 모듈에서 무엇을 할까" 다. V1 만으로도 현황 6("사용자가 낡은 결과를 최신으로 읽는다")이 실질적으로 닫히고, V2·V3 이 그 다음 행동을 준다.

---

## 8. 미결

| # | 항목 | 정해야 할 것 |
|---|---|---|
| 1 | **경고색 토큰** | `⚠ Stale` 의 색. 팔레트에 amber 가 없고 `Error` 재사용은 주의와 차단을 뭉갠다(4절). 디자이너 확정 대기 — #242 트랙과 같은 자리 |
| 2 | **조용 3종을 정말 안 나눠도 되나** | 트리에서 `Empty`·`Draft`·`Ready` 가 같아 보인다. 실사용에서 "이 Set 이 착수 가능한가" 를 트리에서 알고 싶어지면 조용 등급에 옅은 아이콘 1종을 더한다 |
| 3 | **스트립 기본 상태** | 항상 접힘인가, 경고 배지일 때만 자동 펼침인가. 자동 펼침은 모듈 전환 때마다 높이가 튀어 레이아웃이 흔들린다 |
| 4 | **Results Analyzer** | 인스턴스가 아니라 호스트 탭에 임베드되는 패널이다(0.2). 호스트의 배지를 그대로 따르는지, 아무것도 안 띄우는지 |
| 5 | **`Running` 중 표시** | run 파일 `state` 가 `Running` 인 동안은 배지 6종 어디에도 없다. `Complete` 로 가는 중임을 트리에 띄울지, 실행 중 표시는 현행 케이스 표에 맡길지 |
| 6 | **두 창** | 같은 프로젝트를 두 창에서 열면 한쪽 실행이 다른 쪽 배지를 낡게 만드는데 통지 채널이 없다. 11.2-1 과 같은 자리이고 화면 층이 새로 만드는 문제는 아니다 |

---
