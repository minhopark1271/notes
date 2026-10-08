# 배치잡 개념 정리 — batch · case · stage 와 장부의 경계

> 관련 Issue: [#264]
> 후속: [[205-2-w6-w10-change-log-and-remaining-design]] — [#251]·[#264]·[#265] 머지 후의 실제 변경 항목과 구현된 장부 모델

## 배경 및 동기

[#251] 이 `DashBatchLedger`(장부)를 도입하고 [#264] 가 장부 밖 경로를 전부 장부로 올리면서, 배치 실행 코드에 **batch · case · stage · phase · 장부** 다섯 용어가 동시에 쓰이게 됐다. 이름이 비슷해 보이지만 소유자와 축이 각각 다르고, 어느 것을 무엇으로 부르느냐가 [#265]\~[#269] 의 범위 판정에 직접 영향을 준다.

이 문서는 **개념 계층과 경계선**을 코드 실측으로 고정한다. 후속 티켓의 as-is / to-be 와 배치잡 모델의 일반형 설계는 범위 밖이며, 여기서는 그 모델이 **실제 코드에 어떻게 앉았는지**만 대조한다.

> **좌표 기준**: `refactor/async-execution` 계열 `264-ledger-outside-paths` @ `91e78f9`. 라인 번호는 참고값이고 규범은 심볼명이다.

## 핵심 질문

1. `batch` 와 `stage` 는 무엇이 다른가 — 같은 축의 크고 작은 단위인가?
2. 장부(`DashBatchLedger`)는 어디까지를 드는가? 무엇이 장부 밖인가?
3. [#264]\~[#269] 는 배치잡을 어떤 개념 축으로 나눠 처리하는가?
4. [#264] 는 어디까지 구현됐고 무엇이 남았는가?

---

## 1. 3계층 — batch · case · stage

### 1-1. 계층 정의

`batch` 와 `stage` 는 같은 축의 큰/작은 단위가 **아니다.** 다른 축이고, 사이에 `case` 가 있다.

| 계층 | 단위 | 식별자 | 수명 시작 → 끝 | 담는 곳 |
|---|---|---|---|---|
| **batch** | Start 1회 = 실행 1회 (동시 1개뿐) | 없음 — 단일 인스턴스 | `beginBatch` → `finishBatch` / `abortBatch` | `DashJobRunner::m_ledger` + 옆 4값 |
| **case** | DOE 샘플 1건 (= 실행 파일 1건) | `runKey` | 장부 등록 → 터미널 도달(`closed`) | `DashCaseRecord` |
| **stage** | 케이스 1건이 지나는 **처리 칸** | 칸 인덱스 `0` · `1` · `2` | Pending → Running → Done/Failed/Cancelled | `DashStageRecord` |

동시성 제약: 배치는 **동시에 하나뿐**이며 재진입 가드가 강제한다. 판정 술어는

```cpp
bool batchActive() const { return m_wbpjBatch.phase != WbpjPhase::Idle || m_ledger.hasBatch(); }
```

### 1-2. 격자 — 배치는 케이스 × 스테이지 2차원 표

```
batch (Start 1회)
   │
   ├─ case run_1   [ stage0 ][ stage1 ][ stage2 ]      ← 칸마다 state + reason
   ├─ case run_2   [ stage0 ][ stage1 ][ stage2 ]
   └─ case run_N   [ stage0 ][ stage1 ][ stage2 ]
                        └── terminalStage 칸이 Done 이어야 케이스가 "Done" 으로 닫힌다
```

`begin(runKeys, stageCount, terminalStage)` 세 인자가 곧 이 표의 크기와 종결 기준이다.

### 1-3. 경로별 칸 구성 (실측)

칸 수는 워크플로마다 다르다. 상수로 박으면 1칸 장부에서 전이가 범위 밖으로 버려지므로, 리포트는 전부 `m_ledger.terminalStage(key)` 를 쓴다.

| 경로 | 칸 수 | 칸 구성 | terminalStage | `beginBatch` 호출 |
|---|:---:|---|:---:|---|
| A — wbpj DOE | 2 | STP 생성 · Ansys Journal 해석 | 1 (`kAnalysisStage`) | `runWbpjDoeAsync:2867` |
| C — 모핑 → 솔버 | 2 | 모핑 · 솔버(dat/inp) | 1 (`kPostMorphStage`) | `generateInputCases:2108` |
| F — 모핑 → motion | 3 | 모핑 · motion-writer · motion-launcher | 2 (`kMotionLauncherStage`) | `generateInputCases:2108` |
| FE-safe (`.stli`) | 1 | 제출·완료 | 0 | `generateInputCases:1898` |
| 템플릿 치환 폴백 | 1 | 제출·완료 | 0 | `generateInputCases:2237` |
| Direct Launcher | 1 | 제출·완료 | 0 | `runDirectJobs:2376` |

솔버가 설정되지 않아 뒤 칸을 못 밟는 경우는 `setTerminalStage(runKey, stage)` 로 **케이스 단위 하향**한다 — 칸 수를 줄이는 게 아니라 종결 기준 칸을 앞으로 당긴다.

### 1-4. 전이 규칙 — 칸이 배치 종결을 결정한다

`DashBatchLedger::apply` (`DashBatchLedger.cpp:57-102`) 한 곳이 전 규칙을 판정한다.

```
[전이 요청] apply(runKey, stage, state, reason)
   │   1. 미등록 키 · 이미 closed · 범위 밖 stage → 버린다 (applied=false)
   │   2. 칸에 state + reason 기록
   │   3. 바깥으로 낼 문자열 결정
   │      Pending                        → 통지 없음 (begin 초기값과 구분 불가)
   │      Running                        → "Running"
   │      Done (stage <  terminalStage)  → "Running"      ← 조기 종료 방지
   │      Done (stage >= terminalStage)  → "Done"  + caseClosed
   │      Failed / Cancelled             → 그 문자열 + caseClosed  (칸 무관 즉시 종료)
   ▼

[통지] setStageState — applied 일 때만. 전이 1회 = 통지 1회
   │   DOE JSON 기록(ctx.doeJsonPath 스냅샷) · caseStatusUpdated · caseLogUpdated(reason)
   │   ※ 통지 없는 전이 · 전이 없는 통지가 구조적으로 불가능해진다
   ▼

[종결 판정] caseClosed && !m_ledger.active()  →  finishBatch()
       마지막 케이스가 터미널에 닿는 순간, 이 한 곳에서만 배치가 끝난다
```

핵심은 **`terminalStage` 이전 칸의 `Done` 을 바깥에 "Running" 으로 투영**하는 규칙이다. 집계기가 키별 첫 터미널 문자열로 케이스를 닫으므로, 중간 칸의 Done 을 그대로 내보내면 F 경로 케이스가 모핑 완료 시점에 종결돼 버린다 (`tst_batch_ledger::midStageDone_doesNotEmitTerminalString` 이 잠금).

### 1-5. 용어 충돌 주의 — `stage` vs `phase`

A(wbpj) 경로에는 `stage` 와 별개로 `WbpjPhase{Idle, Stp, Analysis}` 가 있다. 인덱스가 0/1 로 겹쳐 보이지만 **소유와 대상이 다르다.**

| | `stage` (0/1) | `phase` (Stp/Analysis) |
|---|---|---|
| 대상 | **케이스**의 진행 칸 | **배치**의 단계 컨텍스트 |
| 소유 | 장부 `m_ledger` | 러너 `m_wbpjBatch` |
| 존재 이유 | 케이스별 성패 회계 | 취소 처리가 단계별로 갈림 (Stp = 협조적 / Analysis = 즉시 중단) |
| 생존 판정 의미 | `hasBatch()` = "닫을 케이스가 있는가" | `phase != Idle` = "A 배치가 살아 있는가" |

둘이 짝이지만 동치가 아니라서 `batchActive()` 가 OR 로 묶는다 — 활성 케이스 0건인 A 배치는 `hasBatch()` 가 false 인데 phase 는 Stp 다.

---

## 2. 장부의 경계 — 어디까지가 장부인가

**장부 = 배치 1회의 상태 정본.** 자원도 실행도 신호도 들지 않는다. `QObject` 가 아니며 시그널은 소유자(`DashJobRunner`)가 낸다.

### 2-1. 안 / 밖

| 장부 안 (`DashBatchLedger`) | 장부 밖 (`DashJobRunner` 소유) |
|---|---|
| 케이스별 스테이지 배열 — `state` + `reason` | 실행 자원 핸들 — `m_activeTasks` · `m_abaqusTasks` · `m_feSafeTasks` · `m_motionProcesses` |
| `terminalStage` · `closed` | 큐·펌프 — `m_motionLauncherQueue` · `m_morphSamples` · `m_morphIndex` |
| 착수 순서 `m_order` → `openKeys()` · `active()` · `currentStage()` | 단계 컨텍스트 — `m_wbpjBatch`(phase · 경로 · config · launchId) · `m_morphBatch` |
| 전이 판정 `apply()` → `Transition{applied, status, caseClosed}` | 배치 회계 곁가지 — `m_batchFailReason` · `m_batchFailedKeys` · `m_batchConsecFail` · `m_batchCancelled` |
| `DashBatchContext` — 배치 1회 값 (`doeJsonPath` · `setName` · `analysisType` · `templatePath` · `canonicalPath` · `solverPath` · `isInp` · `isDfsxml`) | 시그널 방출 · DOE JSON 쓰기 · UI 표 갱신 |

### 2-2. 경계 기준

> **배치가 끝나면 함께 사라지는 값 중, 케이스 성패 판정에 쓰이는 것** — 그것이 장부 안이다.

`DashBatchContext` 가 장부 안에 있는 이유가 이 기준을 잘 보여준다. 후작업 슬롯이 읽는 배치 1회 값을 러너 멤버로 흩으면 수명·리셋 책임이 분산되므로, 장부가 한 곳에 든다. 반대로 `m_batch*` 4종은 판정이 아니라 **회계·집계**라 밖에 있지만, 수명이 같으므로 `beginBatch` 가 장부와 **함께 리셋**한다 (경로별로 리셋하면 빠뜨린 값이 이전 배치에서 샌다).

### 2-3. 수명 — `finishBatch` 가 네 곳을 함께 비운다

장부의 수명 경계를 실물로 정의하는 지점이다.

```
finishBatch(failReason)
   │   1. hasBatch() 아니면 즉시 return        ← 배치당 1회, 중복 종료 차단
   │   2. m_ledger.clear()                     장부
   │   3. releaseMorphBatch()                  모핑 배치 핸들 · 샘플 배열 · 인덱스
   │   4. m_motionLauncherQueue.clear()        motion-launcher 큐
   │   5. releaseWbpjBatch()                   A 배치 단계 컨텍스트 (phase → Idle)
   │   ※ 2\~5 가 "배치 스코프" 의 정의다 — 하나라도 남으면 다음 실행이 이전 상태를 본다
   ▼

[종료 요약 · 채널 결정]
   │   실패 키 목록 로그 1줄
   │   성공 0건이면 failReason 을 합성 — 전건 실패가 성공 채널로 나가는 것을 막는다
   ▼

[방출] jobFinished  또는  jobFailed(failReason)  중 정확히 하나
```

`abortBatch` 는 그 앞단이다 — 열린 키 전량을 `cancelSolverTaskForKey` + `setStageState(Failed/Cancelled)` 로 닫고, 마지막 키가 닫히며 `finishBatch` 가 자동으로 불린다. 열린 키가 0건이었던 경우를 위해 끝에 `finishBatch(reason)` 안전망이 한 번 더 있다. 장부가 서기 전의 착수 거부는 `releaseWbpjBatch()` + `emit jobFailed` 로 끝난다 — 초기화할 배치 상태가 애초에 없다.

### 2-4. "장부 밖 경로" 의 의미 변화 — [#264] 전후

같은 낱말이 [#264] 전후로 다른 것을 가리킨다. 문서·주석을 읽을 때 혼동 지점이다.

```
[#264] 이전 — 장부 밖 경로 = 케이스를 등록하지 않고 자체 종결하던 실행 경로
   │   템플릿 치환 폴백 · FE-safe · Direct Launcher · launchAnsysJournalDirect
   │   종결 주체가 없어 런처 키 카운터가 유일한 Start 복구 수단이었다
   │   → 카운터는 성공 채널만 알아서 전건 실패도 analysisFinished 로 나갔다
   ▼

[#264] 이후 — 그런 경로는 없다. 전 경로가 beginBatch 로 장부를 연다
       reportCaseStatus 의 else 분기에 남는 것은 "장부가 닫힌 뒤 도착한 지각 통지" 뿐 —
       표만 갱신하고 배치 집계에는 넣지 않는다
```

---

## 3. [#264]\~[#269] — 배치잡을 나누는 개념 축

여섯 티켓은 기능 분할이 아니라 **관심사(축) 분할**이다. 각각 배치 실행의 서로 다른 한 축을 맡는다.

### 3-1. 축 대응표

| # | 축 | 무엇을 하나로 만드나 | 상태 |
|---|---|---|---|
| [#264] | **종결 · 상태** | 모든 실행 경로 → 장부 통과. 종결 방출 지점 2곳(`finishBatch` · `abortBatch`) | 코드 랜딩 (4절) |
| [#265] | **제출** | 솔버별 제출 코드 1벌 — ANSYS 3→1 · Abaqus 2→1 · wbpj 설계 판단 · Motion 이미 통합 | OPEN |
| [#266] | **기록 (정본)** | 케이스 상태의 라이터 1곳. 설정 JSON 과 실행 상태 분리 | OPEN |
| [#267] | **키** | Direct 의 `status` vs `status_<stale>` 분열 | CLOSED ([#264] Phase 3 이 흡수) |
| [#268] | **시간 (상한)** | 통지가 안 올 때의 2차 상한 — 워치독 재무장 | OPEN |
| [#269] | **구조** | 워크플로 분기 해체. 계약을 구조로 강제 | OPEN |

### 3-2. 축이 배치 1회 흐름의 어디에 걸리는가

```
[착수] beginBatch 1곳 — 케이스 N개 × 칸 M개 격자 개설
   │   [#264]  착수 거부 7곳 · 활성 0건 3곳도 abortBatch 로 수렴 (무신호 return 0)
   │   [#269]  경로 4종이 각자 짜던 착수 코드를 공통 러너로
   ▼

[제출] 케이스별 솔버 태스크 디스패치
   │   [#265]  ANSYS 3벌 · Abaqus 2벌 → 각 1벌. 시그니처 (runKey, 입력경로, outDir, stage)
   │   [#267]  Direct 의 analysisType 규칙 확정 — 착수·완료가 같은 키에 기록되게
   ▼

[전이] setStageState — 상태 변경의 유일 경로
   │   [#264]  경로별 자체 상태보고(configManager 직접 호출 · 무통지) 폐지
   │   [#266]  JSON 이중 쓰기 해소 — 러너(ctx 스냅샷) vs 런처(현재값) 중 정본 1곳
   │   ※ "전이 1회 = 통지 1회" 가 여기서 강제된다
   ▼

[종결] finishBatch / abortBatch — 방출 2곳
   │   [#264]  1세대 런처 키 카운터 삭제 (성공 채널만 알던 카운터)
   │   [#268]  통지가 영영 안 오는 경우의 탈출구 — 워치독 재무장 → abortBatch
   ▼

[구조] 위 네 단계의 계약을 새 워크플로가 다시 구현하지 않게
       [#269]  generateInputCases 562줄의 워크플로 4분기 해체
```

### 3-3. 의존 순서

```
[#264] 계약 수립 — 전 경로 장부 통과
   │
   ├──→ [#265] 제출 통합       상태 보고가 setStageState 로 통일된 뒤 합쳐야 판단거리 0
   │        │
   │        └──→ [#269] 구조 분리   264 로 계약, 265 로 중복 제거 후 착수
   │
   ├──→ [#268] 2차 상한        264 가 최후 보루(카운터)를 지우므로 우선순위 상승
   │
   └──→ [#266] 정본 단일화     264 의 장부화로 범위가 이미 축소됨

[#267] CLOSED — [#264] Phase 3 이 해소
```

[#264] 가 뿌리인 이유는 나머지 다섯이 전부 **"경로마다 제각각"** 에서 나온 증상이고, [#264] 가 경로 무관 공통 계약을 세우기 때문이다. [#265] 는 그 위에서 물리적 중복을 지우고, [#269] 는 계약을 구조로 못박는다.

---

## 4. [#264] 구현 현황 — 코드는 랜딩, 검증·발행이 남았다

### 4-1. 코드 대조 (실측, `91e78f9`)

Implementation Plan 5항목(Commit A + Phase 1\~4)이 **전부 코드에 반영돼 있다.**

| 항목 | 검증 방법 | 결과 |
|---|---|---|
| Commit A — `jobStarted` 제거 | `grep -rn jobStarted model/ view/ controller/` | 심볼 0건 (선언 · 방출 · 릴레이 모두 소멸) |
| Phase 1 — 착수 거부 → `abortBatch` | `abortBatch` 호출 위치 | 7곳 (`:1757` `:1763` `:1768` `:1779` `:1831` `:1875` `:2215`) + 활성 0건 3곳 (`:1880` `:2039` `:2220`) |
| Phase 2 — 폴백 · FE-safe 장부화 | `beginBatch` 호출 위치 | FE-safe `:1898` · 폴백 `:2237` (둘 다 `1, 0`) |
| Phase 3 — Direct 장부화 | `runDirectJobs:2376` | `beginBatch(runKeys, 1, 0, {})` 존재. `launchAnsysJournalDirect` 의 자체 종결 방출 3곳 소멸 |
| Phase 4 — 런처 키 카운터 삭제 | 카운터 멤버 3종 grep | 심볼 0건 |
| 종결 지점 2곳 확정 | `emit jobFinished` / `emit jobFailed` | 3줄뿐 — `finishBatch:1252,1254` · `abortBatch:1268` |
| `analysisStarted` 액션당 1회 | 방출처 조사 | 3곳 (`Launcher:233` 샘플링 · `:1056` direct · `:1096` DOE) — 릴레이 소멸로 중복 해소 |
| 장부 테스트 보강 5항목 | `tests/tst_batch_ledger.cpp` | 14 케이스 — 티켓이 요구한 5항목 전부 존재 |
| `ctest` 전건 | `ctest -C Release` (build-tests) | **5/5 통과** (12.35s) |

### 4-2. 남은 것 — 코드가 아니라 종결 절차

| 잔여 | 현황 | 필요 조치 |
|---|---|---|
| 미커밋 변경 | 초판 작성 시점(10:02)에는 주석 교정 3줄이었으나 **10:12 실측 기준 5파일 `+81/-67`** (`DashJobRunner.cpp` 121줄 변동 · `DashBatchLedger.cpp` -12 · `DashAnalysisLauncher.{cpp}` · `DashJobRunner.h` · `DashBatchLedger.h` 각 5) — 작업이 계속 진행 중 | 커밋 전 diff 재확인 |
| 브랜치 미발행 | `264-ledger-outside-paths` 에 upstream 없음 — push 이력 0 | `git push -u` |
| PR 없음 | `gh pr list --head 264-ledger-outside-paths` = 빈 배열 | PR 생성 → base `refactor/async-execution` |
| Issue 상태 | OPEN · label `in-progress` · AC 체크박스 10건 전부 미체크 | AC 체크 후 `ticket-complete` |
| Release 빌드 경고 0 | 미확인 (앱 본체 빌드 로그 없음) | Release 빌드 1회 |
| 수동 시나리오 AC | H3 재현 · 전건 실패 배치 채널 · Start 복구 · 케이스 표 갱신 · Direct 키 일관성 — `DashJobRunner`/`DashAnalysisLauncher` 는 VTK 의존으로 테스트 타깃 편입 불가 | 수동 확인 |

### 4-3. 잔여 미세 항목 — 범위 판단 필요

[#264] AC 로는 닫히지만 **장부 계약의 가장자리에 남은 것** 2건. 어느 티켓으로 보낼지 판단이 필요하다.

| 항목 | 위치 | 성격 |
|---|---|---|
| `m_currentAnalysisType` 이 실행 진입 시 초기화되지 않는다 | `generateInputCases:1843` 에서만 세팅 · `reportCaseStatus:1220` 이 소비 | [#267] Implementation Plan 2번 항목이 미이행. 다만 [#264] 로 소비처가 **지각 통지 1곳**으로 줄어 증상 도달 범위가 크게 축소됐다 |
| `monitorMotionLauncherOutput` 이 `ctx` 스냅샷 대신 러너 현재값을 읽는다 | `:812-824` — `m_doeJsonPath` + `m_currentAnalysisType` 로 statusKey 조립 후 JSON 직접 읽기 | 읽기 전용이라 오염은 없으나 "배치 스코프 값은 `ctx` 스냅샷" 규약의 예외. [#266] 정본 단일화 범위와 접점 |

---

## 종합 정리

| 질문 | 답 |
|---|---|
| batch vs stage | 다른 축. batch = 실행 1회(동시 1개), stage = 케이스 1건의 처리 칸. 사이에 case(`runKey`)가 있고 배치는 **케이스 × 스테이지 격자** |
| 칸 수 | 경로마다 다름 — A·C 2칸 / F 3칸 / FE-safe·폴백·Direct 1칸. 상수 대신 `terminalStage(key)` 로 조회 |
| 종결 결정자 | `terminalStage` 칸의 Done, 또는 임의 칸의 Failed/Cancelled → `caseClosed` → 마지막 케이스에서 `finishBatch` |
| 장부 범위 | 배치와 함께 사라지고 **성패 판정에 쓰이는** 상태 — 케이스 칸 배열 · 순서 · 전이 판정 · 배치 1회 컨텍스트. 자원·큐·단계 컨텍스트·시그널·회계는 밖 |
| 축 분할 | 264 종결·상태 / 265 제출 / 266 기록 / 267 키 / 268 시간 / 269 구조. 264 가 뿌리이고 265→269 가 그 위 |
| [#264] 잔여 | 코드는 전부 랜딩(ctest 5/5). 미커밋 3줄 · push · PR · 수동 AC · Release 빌드 경고 확인이 남음 |

## 다음 단계

- [ ] 워킹 트리 주석 교정 3줄 커밋 → `264-ledger-outside-paths` push → PR (base `refactor/async-execution`)
- [ ] Release 빌드 경고 0 확인 + 수동 시나리오 AC 5건 확인 후 Issue AC 체크
- [ ] 4-3 잔여 미세 항목 2건의 소속 티켓 확정 — [#266] 흡수 또는 별건
- [ ] [#268] 착수 (카운터 삭제로 최후 보루가 사라진 상태)

[#214]: https://github.com/NumeRealWorks/DashOpti_GUI/issues/214
[#215]: https://github.com/NumeRealWorks/DashOpti_GUI/issues/215
[#251]: https://github.com/NumeRealWorks/DashOpti_GUI/issues/251
[#264]: https://github.com/NumeRealWorks/DashOpti_GUI/issues/264
[#265]: https://github.com/NumeRealWorks/DashOpti_GUI/issues/265
[#266]: https://github.com/NumeRealWorks/DashOpti_GUI/issues/266
[#267]: https://github.com/NumeRealWorks/DashOpti_GUI/issues/267
[#268]: https://github.com/NumeRealWorks/DashOpti_GUI/issues/268
[#269]: https://github.com/NumeRealWorks/DashOpti_GUI/issues/269
