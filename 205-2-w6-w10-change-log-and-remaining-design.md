# W6·W10 실제 변경 내역과 잔여 이벤트·상태 설계

> 관련 Issue: [#205](205-5-w6-w10-async-minimal-example.md)
> 기반 문서: [205-1-w6-w10-ticket-summary](205-1-w6-w10-ticket-summary.md)
> 원본 문서: [205-5-w6-w10-async-minimal-example](205-5-w6-w10-async-minimal-example.md) — [#205](205-5-w6-w10-async-minimal-example.md) 개념설계 본문 이관본 (최소 구현 골격)

## 개요

[205-1-w6-w10-ticket-summary](205-1-w6-w10-ticket-summary.md) 가 **계획 시점**의 티켓 9건 요약이라면, 본 문서는 W6·W10 브랜치(`refactor/async-execution`)에 **머지 완료된 13건**의 실제 변경 항목을 커밋 기준으로 열거하고, 아직 열려 있는 티켓의 범위를 같은 수준으로 정리한다.

머지분은 세 파동으로 나뉜다.

| 파동 | 티켓 | 범위 | 항목 |
|---|---|---|:--:|
| 1차 (`7340d73`\~`9f2f14f`) | [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207)\~[#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210)·[#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212)·[#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) | 외부 프로세스 축(엔진·소비자·데몬) + 워커 선결 조건 게이트 | 87 |
| 2차 (`b2b8e7f`\~`b579bcf`) | [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260)·[#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251)·[#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264)·[#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214)·[#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265)·[#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) | 배치 장부·종결 수렴 + 워커 인프라(`WorkerJob`·직렬 풀·`MorphingGate`) | 108 |
| 3차 (`0320683`) | [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) | W10-f 축별 확산 1/5 — preprocessor 축 워커화, **model 계층 `processEvents` 0 달성** | 32 |

3차는 [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) 5분할의 첫 티켓이다. 인프라를 새로 세우는 대신 2차가 세운 것(`WorkerJob`·직렬 풀·게이트 형)을 **두 번째 서브시스템에 적용**하는 작업이고, 형태가 재사용 가능한지가 여기서 처음 시험됐다.

티켓 본문의 Implementation Plan 은 **계획**이고, 여기 실린 항목은 **머지된 diff·커밋 메시지에서 확인한 결과**다. 목적은 셋이며, 셋 다 티켓 checkbox 만으로는 얻을 수 없다.

1. **계획분이 무엇이 되었는지 판정** — 각 항목을 티켓 Phase 와 1:1 대조해 계획분 / 계획 외를 표기했다. 전체 227항 중 계획분 125항.
2. **계획에 없던 수리의 가시화** — 나머지 102항. 선재 버그·전환이 만든 회귀·검증과 리뷰가 낳은 추가분이며, 대부분 기존 Phase 안에 흡수돼 checkbox 로는 흔적이 남지 않는다. "계획 대비 실제 — 항목 분류" 섹션에서 사유별로 집계한다.
3. **추가로 수정할 항목의 구분과 귀속** — 성격이 다른 세 부류를 나눠 싣는다. ⑴ **계획 잔여** = [#205](205-5-w6-w10-async-minimal-example.md) 8장 부록의 전환 대상 37지점. "부록 8 전수 목록 대조 — 진행 현황" 에서 완료·부분·미착수·폐기를 판정하고 담당 티켓을 붙였다(잔여 8건 + 폐기 1건). ⑵ **진행 중·계획** = [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) 5분할의 잔여 4건 — [#280](https://github.com/NumeRealWorks/DashOpti_GUI/issues/280)·[#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281)·[#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282)·[#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279). ⑶ **별건** = 이 브랜치의 릴리스 창과 분리된 [#269](https://github.com/NumeRealWorks/DashOpti_GUI/issues/269)·[#249](https://github.com/NumeRealWorks/DashOpti_GUI/issues/249)·Track B(데이터 계층).

### 읽는 법 — 항목 표기

티켓 4개 절의 항목은 `[출처] **성격** 대상 — 내용` 형식이다.

- **출처** — `[계획]` 티켓 Implementation Plan 에 있던 것. 나머지 넷은 전부 계획 외 — `[선재]` 전환 이전부터 있던 버그 · `[회귀]` 이번 전환·신설이 만든 결함(사라진 암묵 보호 포함) · `[검증]` 실 exe·타 Qt 버전·코드 리뷰가 낳은 추가 수리·테스트·인프라 · `[파생]` 결함이 아니라 전환이 요구한 계획 외 신설·정리
- **성격** — **신설** / **전환** / **수리** / **제거** / **테스트** / **정리**

## 대상 범위

| 티켓 | 분할 | PR | 커밋 | 규모 | 상태 |
|---|---|---|---|---|---|
| [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207) | W6-1 엔진 | #223 | `7340d73` | 19파일 +1169/-167 | CLOSED |
| [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207) 사후 보강 | — | #230 | `f1d9855` | 8파일 +284/-120 | — |
| [#208](https://github.com/NumeRealWorks/DashOpti_GUI/issues/208) | W6-2 model 3종 | #232 | `30933c8` | 13파일 +362/-260 | CLOSED |
| [#209](https://github.com/NumeRealWorks/DashOpti_GUI/issues/209) | W6-3 view 2곳 | #248 | `9b0aa24` | 21파일 +713/-261 | CLOSED |
| [#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) | W10-a DOE 파일럿 | #250 | `6538773` | 4파일 +277/-66 | CLOSED |
| [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) | W10-c 데몬 기동 | #255 | `b6d2cf6` | 18파일 +653/-319 | CLOSED |
| [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) | W10-d 워커 게이트 | #257 | `9f2f14f` | 35파일 +974/-337 | CLOSED |
| [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) | W10-b 모핑 per-sample 파일럿 | #261 | `b2b8e7f` | 11파일 +1448/-765 | CLOSED |
| [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) | DOE 2단계 이벤트·상태 3축 | #262 | `3666dd7` | 7파일 +524/-315 | CLOSED |
| [#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264) | 장부 밖 경로 통합·종결 2곳 | #271 | `fc167bd` | 10파일 +510/-230 | CLOSED |
| [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) | W10-e 워커 인프라·모핑 단일화 | #272 | `77d7371` | 19파일 +1043/-42 | CLOSED |
| [#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265) | 솔버 제출 통합·direct wbpj 승격 | #273 | `9b5a95a` | 6파일 +448/-439 | CLOSED |
| 인접 커밋 (티켓 없음) | Journal 그룹 분할·motion kill | #275 | `6f5ba1e` | 5파일 +247/-49 | — |
| [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) | 게이트 증명화·종료 오케스트레이션 | #276 | `b579bcf` | 28파일 +649/-292 | CLOSED |
| [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) | W10-f-1 RST/KPI 워커화·게이트 신설 | #286 | `0320683` | 21파일 +2576/-1200 | CLOSED |
| [#280](https://github.com/NumeRealWorks/DashOpti_GUI/issues/280) | W10-f-2a `RwGate` 신설 | — | — | 3 Phase — 소유 pE 0곳 | OPEN |
| [#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281) | W10-f-2b 단건 모핑 워커화 | — | — | 6 Phase — view pE 5→0 예상 | OPEN |
| [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) | W10-f-2c dfsxml stage·FEM 파서 | — | — | 2 Phase — model 2 + view 5 pE 예상 | OPEN |
| [#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279) | W10-f-3 DoD 봉인 | — | — | 4 Phase — 판정·기록 + dead code 2건 | OPEN |
| [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) | W10-f 부모 (분석·분할 근거) | — | — | 구현 위임 | OPEN |
| [#249](https://github.com/NumeRealWorks/DashOpti_GUI/issues/249) | 파사드 통지 일반화 | — | — | 8파일 65\~80줄 예상 | OPEN (별건) |
| [#269](https://github.com/NumeRealWorks/DashOpti_GUI/issues/269) | `generateInputCases` 분기 해체 | — | — | 방향 2안 미결 | OPEN (별건) |

브랜치 `refactor/async-execution`. PR 전부 squash 머지이므로 개별 커밋 이력은 머지 커밋 본문에 남아 있다. base 가 기본 브랜치(`main`)가 아니라 `Closes #N` 이 발동하지 않으므로 이 그룹의 Issue close 는 전부 수동이다 — 유일한 예외가 [#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264)(PR #271)이고, 그 자동 close 는 관례에서 벗어난 우연이다.

## 축별 진척 — 1차 파동

| 축 | [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207) | [#208](https://github.com/NumeRealWorks/DashOpti_GUI/issues/208) | [#209](https://github.com/NumeRealWorks/DashOpti_GUI/issues/209) | [#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) | [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) | [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) |
|---|---|---|---|---|---|---|
| 블로킹 제거 | 0건 (의도적 불변) | 3건 | 3건 | 폴링 루프 1건 (무게중심) | **6건 — GUI 경로 `waitFor*` 0** | 0건 (스레드 미생성) |
| 실행 객체 소유 | 엔진 신설 | model 3종 위임 | **view → controller/model** | 해당 없음 (데몬 명령 = Job 미생성) | 데몬 역할 in-place 강화 (신클래스 없음) | 모핑 엔진 per-Job · 컨텍스트 `shared_ptr` |
| 취소 | 터미널 잠금 | `cancel()` 채택 | 트리 kill + 앱 종료 상한 | 협조적 취소 (P2) | `stop()` = 종료 + 큐 drain 통지 (`cancel(id)` 미구현) | 해당 없음 |
| 식별자·이벤트 | 객체 자체가 식별자 | 동일 | 동일 | **`commandId` 최초 활용** — 단 배치 전용 시그널 증설로 우회 | `ready()`/`died()`/`stopped()` 신설 · 완료 상관을 `commandId` 로 정정 | 해당 없음 (레지스트리 per-key 로드) |

[#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) 칸의 "우회" 가 [#249](https://github.com/NumeRealWorks/DashOpti_GUI/issues/249) 의 출발점이고, 같은 티켓이 세운 배치 오케스트레이션의 상태 처리 공백이 [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) 의 출발점이다. [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) 은 워커 축의 **게이트**라 이 네 축을 움직이지 않는다 — 공유 상태를 끊어 [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 가 스레드를 넣을 수 있게 하는 것이 전부다.

## 축별 진척 — 2차 파동

2차는 축이 다르다. 1차가 "외부 프로세스 대기를 지우는 일" 이었다면 2차는 **배치 장부·종결 계약을 한 벌로 만들고 그 위에 스레드를 얹는 일**이다. 그래서 축을 새로 뽑았다.

| 축 | [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) | [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) | [#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264) | [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) | [#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265) | [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) |
|---|---|---|---|---|---|---|
| 상태 장부 | **`DashBatchLedger` 신설** — 케이스당 스테이지 배열 (C=2 · F=3) | A(wbpj)를 2칸으로 이관 — flat enum 8종 폐기 | 장부 밖 3경로(폴백·FE-safe·Direct)를 1칸 장부로 | 무접촉 | stage 하드코딩 → `terminalStage` 유도 | 무접촉 |
| 종결 지점 | `finishBatch` 1곳 + `abortBatch` | 조기 이탈 7곳 수렴 | **`finishBatch`·`abortBatch` 2곳 확정** — 1세대 카운터 삭제 | 무접촉 | 런치별 종결로 세분(전건 실패는 `finishBatch`) | `rejectBeforeBegin` 분리 (착수 전 15곳) |
| 실행 단위 | `Execute` → `PrepareBatch` + `RunOneSample` (동기) | 해당 없음 | 해당 없음 | **`RunOneSample` 1건 = 모핑 직렬 풀 위 WorkerJob 1개** | 제출 헬퍼 3벌+2벌 → 1벌+1벌 | 진입점 5 는 Claim 스코프 동기 유지 (축소) |
| 배제 기제 | 없음 (스레드 미도입) | `batchActive()` 술어 정정 | 재진입 가드를 `runDirectJobs` 에도 | **`MorphingGate` 신설** — 프로세스 전역 · 2토큰 카운트 | 무접촉 | **증명형 재편** — `Witness`/`Claim`/`Reservation`, DLL 함수 4곳이 타입으로 요구 |
| 식별자 | `DashSampleResult{runKey, ok, reason}` 값 반환 | 배치 고유 `launchId` + 실패에 `stpPath` 동반 | `directRunKey` 한 곳 · `reportCaseStatus` 에서 `stage` 제거 | 해당 없음 | `launchId → 케이스 집합` 맵 (한 wbpj 실패가 남을 닫지 않음) | 해당 없음 |
| 종료 안전 | 해당 없음 | 해당 없음 | 해당 없음 | `aboutToQuit` 에 풀 배수 | 해당 없음 | **`AppShutdown::run()` 4단계** — 데몬 회수를 정적 소멸에서 이관 |

두 파동의 접합점은 [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260)·[#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) 이다. 원래 [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) 이 먼저 착수돼 flat enum 8종으로 구현·PR 까지 갔으나, 두 티켓이 `DashJobRunner` 에 같은 이름(`finishBatch`)을 각자 두어 **1인자 호출이 ambiguous** 였고(기본인자 개수는 오버로드 tiebreaker 가 아니다) 정상 종결 경로 5곳이 전부 깨졌다. [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) 이 Draft 로 내려가 [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) 머지를 기다린 뒤 **인코딩을 배열형 장부로 뒤집어** 재작업했다 — 축 1(종료 수렴)·축 2(귀속·수명·순서)는 인코딩 무관이라 그대로 승계됐고, 축 3(상태 표현)만 갈아엎혔다.

---

## [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207) W6-1 — 공용 실행 엔진

**계획 8항 / 계획 외 5항** (회귀 3 · 선재 1 · 파생 1)

1. [계획] **신설** `controller/async/Job.h/.cpp` — 5상태 머신, `setState()` 단일 전이점 + **터미널 잠금**(취소 뒤 늦은 완료의 `finished` 이중 방송 차단)
2. [계획] **신설** `controller/async/ProcessJob.h/.cpp` — 1회용 실행 객체. exe 검증·env·UTF-8·채널 모드(Merged/Separate)·취소·자식 정리 집약, `outputLine`/`errorOutputLine`, pull 접근자 `exitCode()`/`stdoutText()`
3. [계획] **신설** `controller/async/LineAssembler.h` — 라인 조립을 순수 함수로 추출. `runAsync` 부분 수신(결과 라인 일부만 조립) **수리**
4. [계획] **제거** `DashExtensionProcess` 의 one-shot 경로(`runAsync` 계열) 전면 삭제 — 데몬 경로만 잔존
5. [계획] **전환** `DashModelBuilderMCU` 재배선 — 기존 위임 소비자를 `oneShotFinished` → Job 계약으로
6. [계획] **수리** `killOrphans` — exe 이름 기준 광역 `taskkill /IM` → 자기 spawn PID `taskkill /F /PID` (동명 무관 프로세스 사망 위험 제거)
7. [계획] **전환** 경로 카탈로그 일원화 — DeepOpt exe 하드코딩 4곳(`DashModelBuilder`, `DashModelRunner` ND/1D, `DashOptimizerWidget`)을 `DashExt::Path::DeepOpt` + `resolveAbsPath()` 로
8. [회귀] **수리** Qt5 메타타입 — `finished` 파라미터를 `Job::State` 로 정규화, `qRegisterMetaType<Job::State>` 를 `Job` 생성자에서 선등록(Qt6 통과 / Qt5 실패였던 `tst_job_state` 2건), `tests/` 에 `/utf-8`. 1~2항 신설분의 이식성 결함이라 Windows·Qt5 재검증에서야 드러남 (티켓 Phase 5 로 사후 추가)
9. [선재] **수리** `stopDaemon()` 재진입 — `waitForFinished()` 가 `QProcess::finished` 를 동기 전달해 `onDaemonFinished()` 재진입 → 널 재역참조 + `daemonStopped` 2회 방송. 대기 블록 뒤 널 가드 (티켓 Phase 6 으로 사후 추가)
10. [계획] **테스트 신설** `tests/` CMake · `daemon_stub` · `tst_line_assembler` · `tst_job_state` · `tst_process_runtime` · `tests/e2e/tst_e2e_real_exe`(실 exe 3종 데몬 왕복) — 계획은 3항의 재현 테스트 1건이었고 하네스 4종으로 확장됐다

### 사후 보강 (PR #230)

11. [회귀] **수리** `LineAssembler` 바이트 기반 재작성 — 3항 신설분의 청크 단위 디코드가 만든 **UTF-8 read 경계 결함** + 개행 없이 끝난 마지막 줄 유실
12. [파생] **전환** 데몬 경로 수동 조립(`m_daemonStdoutBuffer` + `processDaemonStdoutLines`) → `LineAssembler` — 구현 2벌 → 1벌 (계획은 데몬 경로 잔존이었음)
13. [회귀] **수리** `forceKillPid` 에 `/T` 추가 — 6항이 광역 `/IM` 을 자기 PID 로 좁히며 회수 범위 밖으로 빠진 PyInstaller onefile 의 실제 워커 자식을 트리로 복원

---

## [#208](https://github.com/NumeRealWorks/DashOpti_GUI/issues/208) W6-2 — model 소비자 3종

**계획 4항 / 계획 외 10항** (회귀 5 · 검증 2 · 파생 2 · 선재 1)

1. [계획] **전환** `DashModelRunner` — 자체 `QProcess` 폐기, `startPredictionJob()` 단일 진입점으로 predict/ND/1D 3경로 통합
2. [계획] **전환** `DashModelBuilder` — 동일. stderr 축적(`m_errorOutput`)을 `errorOutputLine` 구독으로 승계
3. [계획] **전환** `DashOptimizer` — 동일. stderr 는 Separate 로 분리하되 **미구독**(진행 표시가 실패 메시지에 섞이지 않던 기존 동작 유지)
4. [파생] **신설** `ProcessJob::setWorkingDirectory()` — 미지정 시 기존 동작(exe 디렉터리). Runner 만 프로젝트 경로에서 도구 실행
5. [계획] **제거** 블로킹 3건 — `waitForStarted(10000)` → `finished(Failed)` 통지, `waitForFinished(3000)`×2 → `cancel()` (Phase 2 Notes 가 위임의 부산물로 예고한 몫)
6. [파생] **제거** `errorOccurred` 에러 번역 람다 — 엔진이 흡수
7. [회귀] **수리** 기동 호출을 함수 말미로 이동 — CreateProcess 실패의 **동기** 통지가 "In Progress" 상태 기록과 타이머 기동을 앞지르던 순서 결함
8. [회귀] **수리** 재실행 가드 3종 복원 — 공유 `QProcess` 시절 Qt 가 2번째 `start()` 를 거부해 주던 암묵 보호가 "실행 1회 = Job 1개" 로 소멸. Optimizer(`runOptimization()` 최상단) · Runner(predict 는 원래 무가드였음) · Builder(startButton 잠금이 status 1초 폴링에 걸려 재클릭 창 → `m_currentJob` 이 덮여 job#1 의 완료 람다가 job#2 핸들을 지움 → Stop 무동작·이중 학습). Runner 분만 계획의 "단일 핸들 + 실행 중 거절 가드" 결정에 포함돼 있었고 나머지 2종은 소멸한 보호의 복원
9. [회귀] **수리** Runner 가드 순서 — 판정이 `m_stdoutBuffer.clear()` 뒤로 밀려, 거절된 실행이 **진행 중인 실행의 출력을 지움**
10. [회귀] **수리** `ProcessJob::cancel()` 수명 분리 — kill 은 신호만 쏘고 QProcess 는 종료 관측까지 Running. 소비자의 `deleteLater` 가 앞질러 `~QProcess` 가 Running 을 만나 `waitForFinished`(기본 30s)로 GUI 블로킹(`Destroyed while process is still running`). kill 직후 QProcess 를 Job 자식에서 분리하고 자기 종료를 자기가 회수. `exitCode()` 는 -1 유지라 소비자 판정 불변
11. [회귀] **수리** 학습 실패 종료 시 모델 status 가 "In Progress" 로 고착 — 지연 status 확인이 모두 끝난 시점에 잔여 항목만 "Failed" 로 마감(도구가 쓴 "Done" 은 제외, 마감 직전 새 학습이 시작됐으면 미개입). 기존 코드가 `waitForStarted` 실패 시 status 기록 전에 return 했으므로 이 PR 이 만든 회귀
12. [선재] **수리** `DashModelBuilderWidget` Stop 버튼 미배선 (view 쪽) — `stopButton` 포인터를 잡고 enable/disable 만 토글하고 `clicked` 연결이 없어 학습 중단이 아예 동작하지 않았음. 위임된 `cancel()` 경로가 GUI 어느 경로로도 도달하지 않으므로 함께 수리 (`setModel` 재호출 중복 연결 방지로 `disconnect` 선행)
13. [검증] **테스트** 기동 실패 2갈래 봉인 — `missingExeFinishesAsFailed`(exe 부재, `start()` 직후 `finished.count()==0` 까지 검사해 동기 방출 금지 봉인) · `unlaunchableExeFinishesAsFailed`(파일은 있으나 CreateProcess 실패 → `errorOccurred(FailedToStart)` — 코드 경로가 달라 분리). workingDirectory 기본값·재지정 2건, `daemon_stub` cwd 모드
14. [검증] **테스트** ctest 에 Qt bin PATH 주입 — Qt DLL 이 PATH 에 없는 셸에서 세 테스트 전부 `0xc0000135`(DLL_NOT_FOUND)로 죽어 "실행 불가"가 "테스트 실패"로 보였음

---

## [#209](https://github.com/NumeRealWorks/DashOpti_GUI/issues/209) W6-3 — view 소유 QProcess 2곳

**계획 8항 / 계획 외 5항** (파생 3 · 회귀 1 · 검증 1) — 계획서가 D1~D7 결정으로 선재 결함·소멸자 누락까지 미리 적어 W6 3건 중 계획 외 이탈이 가장 작다.

1. [계획] **신설** `controller/async/ProcessKill.h/.cpp` — `forceKillPid` 를 `DashExtensionProcess.cpp` 익명 namespace 에서 승격. 비동기(`startDetached`) 기본, `waitForCompletion=true` 는 `killOrphans` 전용(데몬 재기동 직전 정리라 동기 필요)
2. [계획] **수리** `ProcessJob::cancel()` 을 트리 kill 로 — 부트로더 PID 만 죽던 **반쪽 취소** 해소. 생산 호출처가 `DashModelBuilder::stopTraining()` 1곳뿐이라 회귀 범위가 좁음
3. [파생] **수리** `killProcessTree` bool 반환 + `cancel()` 폴백 — taskkill 을 못 띄웠을 때 `m_proc->kill()` 로 하강. 무조건 병행은 부트로더를 먼저 죽여 `/T` 의 트리 열거를 깨므로 **폴백 한정**
4. [계획] **신설** 실행 중 Job 전역 레지스트리 + `ProcessJob::cancelAllRunning()`, `main.cpp` 에서 `aboutToQuit` 연결 — 프로세스 수명 상한 = 앱 종료
5. [회귀] **수리** `cancelAllRunning()` 의 `blockSignals` 통지 억제 — `aboutToQuit` 은 메인 루프 종료 후 방출되므로, 소비자가 `Cancelled` 를 도메인 실패로 번역해 띄우는 모달(fit/prediction)이 앱 종료를 붙잡았음. 4항 신설분이 만든 결함
6. [계획] **전환** fit 실행 이전 — `DashOptimizerWidget::m_fitProcess` → `DashOptimizer::runFitVariables(csvFilePath)` + `fitFinished(success, stdoutText, stderrText)`. `m_fitJob` 을 `m_currentJob` 과 별도 핸들로 둬 optimization 과의 동시 실행 의미 보존, stderr 는 fit 만 축적, `#ifdef DASH_BUILD_LGE_COMPSPRING` 가드와 DE 상수 2종 동반 이동
7. [계획] **수리** fit 버튼 고착 — `setModel()` 이 옛 모델 연결을 전면 절단해 fit 중 Set 을 전환하면 통지가 유실되고 `"Fitting..."` 비활성으로 영구 고착(Qt 가 자식의 명시적 disable 을 `WA_ForceDisabled` 로 기억해 부모 `setEnabled(true)` 로도 안 풀림). `updateFitButtonState()` + `isFitRunning()` pull 로 재계산 (`model == nullptr` 인 Set 삭제 경로 포함). 선재 결함이지만 계획서 D5 가 원인·해법까지 적시해 계획분
8. [파생] **제거** `fitProcessLogMessage` 시그널과 `DashMainWindow` 의 해당 배선 — 위젯이 실행 주체가 아니게 되어 소멸
9. [계획] **수리** `~DashOptimizer` 에서 실행 중 Job 정리(`m_fitJob` + 누락돼 있던 `m_currentJob`) — Set 삭제·프로젝트 정리 경로에서 `~QProcess` 가 Running 을 만나 GUI 스레드를 막던 것. `m_currentJob` 누락분까지 계획에 명시돼 있었음
10. [계획] **신설** `controller/DashTopOptPostprocessRunner.h/.cpp` — thin 경계 `run(configJson, outputStlPath)`, `progressed(double)` / `finished(success, outputStlPath, errorText)`. `outputStlPath` 를 러너가 보관(다이얼로그가 죽어도 결과 경로 생존). `DashManager` 필드 1개 + 접근자 1개로 소유 — 실행 로직의 DashManager 흡수는 W20 역행이라 기각
11. [계획] **전환·제거** `TopOptPostprocessDialog` — QProcess 소유 폐기·구독만. `waitForStarted(3000)` 과 소멸자 `terminate()`+`waitForFinished` 블록 소멸, `[PROGRESS] xx%` 파싱은 러너로 이전, 설정 JSON 조립은 다이얼로그 잔류
12. [검증] **테스트** e2e 2건 — ⑴ 구독자(다이얼로그 대역)를 실행 중 소멸시켜도 소유자에 매달린 러너가 `finished` 를 끝까지 수신(죽은 구독자엔 미통지, `[PROGRESS]`·stderr 실측) ⑵ 워커 자식이 뜬 뒤(파이프라인 약 8초 지점) `cancelAllRunning()` → 동명 인스턴스 0. `tasklist /FO CSV` 사용 — 기본 테이블 형식은 이미지명을 25자로 잘라 31자 exe 이름이 절대 매칭되지 않음
13. [파생] **정리** `updateFitButtonState` 선언을 데이터 멤버 블록에서 헤더 private 함수 섹션으로

---

## [#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) W10-a — DOE 배치 파일럿

**계획 10항 / 계획 외 3항** (검증 2 · 파생 1) — Step 1 전환이 파사드 경계를 건드리지 않는 model 내부 작업이라 "암묵 보호 소멸" 계급이 없었다.

1. [계획] **전환** `runWbpjDoeAsync` Step 1 — 동기 `for` + `waitForFile`(2s 간격 × 최대 600s) 제거 → pending 큐 + 완료 슬롯 연쇄. 진행 촉발 주체가 호출부 → Qt 이벤트 루프 (실행 순서 불변)
2. [계획] **신설** `startNextStpCase()` · `onStpCaseCompleted()` · `onStpCaseFailed()` · `onStpCaseTimeout()` · `finishStpPhase()`
3. [계획] **신설** `StpCase` / `StpBatch` 멤버 — 루프 콜스택에 살던 상태(현재 케이스·pending·누적 실패·중단 조건)를 배치 수명으로 이관
4. [계획] **전환** Step 2 를 `launchWbpjJournal()` 로 분리 — 본문 무변경(이미 이벤트 구동), 호출 위치만 완료 연쇄 뒤로
5. [계획] **신설** `DashSolverNxCad` 배치 전용 시그널 2종(`updatePrtGeometryBatchCompleted`/`Failed`) — 대화형 시그널은 미리보기 STEP 로드·모달 경고를 띄워 배치가 구독 불가. 특히 실패 모달은 이벤트 루프를 잡아 continue-on-error 연쇄를 막음
6. [계획] **수리** `onCommandFailed` 가 버리던 `commandId` 로 load/update 판정 → 실패를 완료와 같은 기준으로 라우팅
7. [계획] **신설** 케이스 워치독 600s — `stopDaemon()` 이 `m_waitingFinished` 를 먼저 지워 `onDaemonFinished` 의 `wasWaiting` 이 false 가 되므로 진행 커맨드가 `commandFailed` 로 회수되지 않음. 워치독이 실패 회계를 직접 태움
8. [계획] **신설** 정책 구현 — P1 완료분 보존(진행 1건 완료 수용) · P2 협조적 취소(잔여 미착수 `Cancelled` 표시 + Step 2 대상 제외, 배치 중 데몬 미살해) · P3 continue-on-error + 연속 3건 실패 시 STP 단계 중단 · P5 자동 재시도 없음
9. [계획] **신설** 배선 규약 — `connect` 선행 + `QueuedConnection | UniqueConnection`(완료 시그널이 데몬 stdout 핸들러 콜스택에서 방출되므로 재진입 방지), 배치 종료 시 `disconnect`, 경로 귀속 가드
10. [계획] **제거** 죽은 `waitForFile` 정의·선언 + 고아가 된 `QCoreApplication` include (구 [#211](https://github.com/NumeRealWorks/DashOpti_GUI/issues/211) 흡수 — 레포 전체 `grep waitForFile` → 0)
11. [검증] **수리** (리뷰 반영) `activeRunKeys` 가 "성공 + 실패" 였음 — Step 2 는 이 목록을 돌며 DAT/RST 를 찾으므로 STP 없는 실패 케이스를 재탐색해 Failed 로 재판정. 성공=`activeRunKeys` / 실패=`failedKeys` / 미착수=`pending` 3갈래로 분리하고, 종료 판정은 `activeRunKeys` 공백 검사 하나로 축소
12. [검증] **수리** (리뷰 반영) 취소 종결 지점에서 NX 데몬 회수 복원 — 취소 시점에는 P1 때문에 죽일 수 없지만 이 지점은 진행 케이스가 이미 마감된 뒤라 안전. 전환 전 `cancelAllRuns` 의 취소 의미 복구
13. [파생] **정리** 주석의 변경 이력 서술 제거, 시그널 주체 오기 1건 정정

### 인접 커밋

`454fb0f` — 데몬 ready 타임아웃 15s → 30s. 티켓 어디에도 속하지 않는 단독 완화였고, 근본(데몬 기동 ready 동기 대기)은 [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) 가 `b6d2cf6` 에서 제거했다. 값 자체는 남아 이제 **프리즈 상한이 아니라 Starting 상태의 이벤트 상한**으로 쓰인다.

---

## [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) W10-c — 데몬 기동 비동기화

**계획 10항 / 계획 외 5항** (회귀 3 · 검증 1 · 파생 1) — 계약 1점(`bool startDaemon()`)을 바꾸면 공유 기반 클래스를 통해 소비처 18곳이 동시에 깨지는 구조라, 계획서가 그 18곳을 전수표로 확정하고 시작했다. 계획 외 3건은 전부 그 전환이 만든 회귀다.

1. [계획] **전환** API 재계약 — `bool startDaemon()` → `void start()`, `stopDaemon()` → `void stop()`. 결과는 `ready()`/`died()`/`stopped()`. busy-wait 루프 2곳 · `waitForStarted(30000)` · `stopDaemon` 의 `waitForBytesWritten`+`waitForFinished`×2 삭제 → **GUI 경로 `waitFor*` 0건**
2. [계획] **신설** desired/actual reconcile — actual 4상태(`NotRunning`/`Starting`/`Ready`/`Stopping`)는 프로세스 이벤트가, desired 1비트(`m_wantUp`)는 `start`/`stop` 의도가 갱신하고, 안정점마다 `reconcile()` 이 수렴시킨다. `stop(); start()` 재기동 · 미기동 lazy 기동 · 전이 중 재호출 무시가 전부 이 한 규칙에서 나온다
3. [계획] **신설** `QTimer` 2종 — ready-timeout(Starting 상한, 만료 시 kill + `died()` + drain) · stop-timeout(kill 승격). **타이머 수명 = 상태 수명**이라 Starting 을 어느 경로로 벗어나도 해제되고, Starting 중 `stop()` 뒤 잔존 타이머가 이미 멈춘 데몬에 가짜 `died()` 를 쏘는 창이 생기지 않는다
4. [계획] **수리** 실패 3모드 라우팅 — never-ready(타이머) · FailedToStart(`finished` 가 오지 않는 유일 경로라 `errorOccurred` 에서 직접 마감) · pre-launch(exe 부재·빈 경로 — 프로세스가 없어 `errorOccurred` 조차 없음). 사망 시 진행 중·대기 명령을 전부 `commandFailed` 로 접는다 — 종전 `Crashed` 가드가 in-flight 실패를 삼켜 아무에게도 알리지 않던 무음이 소멸
5. [계획] **신설** 사망 = 종착(P5) — 자동 재기동·replay 없음. 다음 `sendCommand` 가 lazy 로 되살린다 (크래시 유발 명령의 자동 replay = 크래시 루프)
6. [계획] **신설** `shutdownBlocking()` — 소멸자·앱 종료 전용 유한 동기 대기. 비동기화하면 정리를 맡은 `finished` 슬롯이 객체 소멸 뒤라 실행되지 않아 데몬이 고아로 남는다. 리포에 남은 데몬 `waitFor*` 3건이 전부 여기다
7. [계획] **정리** 포인터 삭제를 `teardownProcess` 단독 소유로 (구 3곳) · PID 등록은 사라진 `waitForStarted` 자리를 `QProcess::started` 슬롯이 대체
8. [계획] **전환** 소비처 18곳 — 래퍼 자체 버퍼(무음 드롭 2곳 · `m_pendingTest` defer-replay) 를 걷어내 host 큐를 유일 버퍼로 두고, "이미 ready" 즉답 emit 2곳을 없앤 뒤 view 4곳이 초기 1회 조회로 현재 상태를 반영(`DashModelRunnerMCU::isDaemonReady()` 위임 신설). 완료 상관을 가변 모드 스칼라 → `commandId` 기준으로 정정
9. [계획] **전환** DOE 기동 게이트 → config 판정 (`nxStarted` → `nxConfigured`) — `start()` 가 비동기라 그 시점의 ready 여부는 "NX 를 쓸 수 있는가"를 답하지 못한다. 낡은 STP 무음 재사용(A7)·케이스 Failed 영속화(A8) 갈래를 재생성 경로로 합류
10. [계획] **제거** 미준비 게이트 3종 — `DashMainWindow` 모달(A18, `.prt` 조기 return 3곳에 스피너 stop 짝 복원) · `DashManager::enqueueLaunch` 의 journal ready 게이트(A4, DOE Step 2 전멸 경로) · `DashModelRunner` 의 감도 plot 게이트(A16)
11. [회귀] **수리** `onStpCaseTimeout` 이중 실패 회계 — `stop()` 의 drain 이 `commandFailed` 를 통지하게 되면서 직접 회계와 겹쳐 같은 케이스가 두 번 계상됐다. 통지를 유일 경로로 두고, 케이스 마감 시 `current` 를 비워 늦게 온 통지가 다음 케이스를 오판정하지 못하게 함
12. [회귀] **수리** (self-review) `stop()` 전이 순서 — drain 통지를 전이보다 먼저 하면, 통지 슬롯이 그 자리에서 `sendCommand` 를 부를 때 desired 가 Up 으로 되돌아가 뒤늦은 `reconcile()` 이 종료를 건너뛰고, 상태가 아직 Ready 라 새 명령이 세우려던 데몬 stdin 으로 들어간다. `Stopping` 을 먼저 확정하면 그 명령은 큐에 래치돼 재기동 후 실행된다. 현행 소비자는 배치 실패 통지가 `QueuedConnection` 이라 이 창을 열지 않아 **라이브 회귀는 아니었고**, 순서 의존 제거가 목적
13. [회귀] **수리** (self-review) I/O 오류 무음 — `onDaemonProcessError` 가 `FailedToStart` 외 전부 early return 이라 `WriteError`/`ReadError`(Qt 가 채널을 닫은 뒤 발생 → `finished()` 없음)에서 진행 중 명령이 영구 미마감이었다. Ready 에는 상한이 없어 무음 hang 이 확정된다. base 는 `error != Crashed` 에서 `commandFailed` 를 냈으므로 **본 티켓이 만든 회귀** — `Crashed` 만 `finished()` 에 위임하고 나머지는 통지 후 `Stopping` 경유 정리
14. [파생] **제거** `DashMainWindow` `.prt` 분기의 중복 사전 기동 블록 — `enqueueLoadPrt` 가 같은 분기를 이미 갖고 `tryStartIfConfigured` 가 NX 경로를 스스로 재조회하므로 잔존 효과 없이 로그만 늘렸다
15. [검증] **테스트** 신규 6건 + `daemon_stub` `noready` 모드 + e2e 이벤트 구동 전환 — 미기동 enqueue 순서 보장 · ready-timeout drain · Starting 중 stop 뒤 가짜 died 0 · 재기동 성립과 Ready 중 반복 start 무동작 · pre-launch 통지 · `commandFailed` 슬롯에서 재-`sendCommand` 하는 소비자 하에서도 `stop()` 관철(전이 순서를 되돌리면 깨짐)

### 의도적 미구현 2건 (별 티켓 미생성)

- **`cancel(id)`** (Phase 3b) — 단건 취소를 요구하는 소비처가 0건이다. 취소 지점 4곳(`cancelAllRuns` STP·journal · `onStpCaseTimeout` · `stopTraining`) 은 전부 "전체 취소" 또는 "데몬째 재기동"이 의도이고, 데몬 큐에 동시 2건 이상 쌓는 소비처가 없어 단건 취소가 성립할 자리가 없다. **재도입 트리거**: 동시 2건 이상을 쌓는 소비처가 생기고 그중 1건만 빼야 할 때.
- **R5=E1 (데몬/one-shot 클래스 분리)** — 티켓은 "후속 과제, 목표 = E1" 로 판정했으나 전제가 이미 해소됐다. E1 의 ⑴ 데몬/one-shot 분리는 선행 티켓에서 끝났고(`runBlocking`/`runAsync` 전 리포 0건, one-shot 은 `ProcessJob` 소유), 잔여는 ⑵ 상속→합성 하나인데 서브클래스 1개(`DashSolverNxCad`)·오버라이드 3개뿐이다. **폐기 후보로 기록** — 재도입 트리거는 서브클래스가 2개 이상으로 늘 때.

---

## [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) W10-d — 워커 선결 조건 게이트

**계획 11항 / 계획 외 8항** (회귀 6 · 검증 1 · 파생 1) — 스레드를 하나도 만들지 않는 티켓인데 계획 외가 8항이다. 회귀 6건 중 5건이 "공유를 끊자 그 공유에 기대던 것이 드러난" 계급이고, 발견 경로는 코드 리뷰 5 · 런타임 1 이다.

> [#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) 은 리뷰 반영분을 `[검증]` 으로 실었으나, 여기서는 결함의 **출처**가 이번 전환이라 `[회귀]` 로 분류하고 발견 경로를 항목 안에 병기한다.

1. [계획] **전환** D1 싱글톤 — `main()` 에서 두 싱글톤을 GUI 스레드에서 선-초기화(M1) → magic static 전환 + `atexit(Destroy)`·heap 포인터 전제 inline `Destroy()` 제거(M2). 생성자에 메인스레드 가드. `runAnalysisInThread`(`QtConcurrent`)가 이미 `DashProjectManager::Instance()` 를 호출하므로 lazy-init 경합은 **오늘 도달 가능한 결함**이었다
2. [계획] **수리** D3-M1 안전핀 — `emplace` 는 중복 키 검사 **전에** 노드를 구성하며 `ctx` 를 move-out 시켜, 경합 시 사전 캡처한 raw 가 폐기 노드를 가리킨다. `try_emplace` 교체 + **반환도 맵 이터레이터 경유** (교체만으로는 미해소)
3. [계획] **전환** D2 엔진 per-Job — 배치 엔진을 executor 소유로 격상해 operator 설정→실행 3단 시퀀스가 남의 핸들과 섞이지 않게 했다. `m_morphingOperator` raw → `unique_ptr` (기존 raw `new` 는 해제 경로가 없었다)
4. [계획] **전환** D6 그리드 스냅샷 — 그리드 일습을 `DashMorphingMeshSet` 값으로 뽑아 `DashMorphingEngine::RunVolumeMorphing` 으로 옮기고, 배치는 `DeepCopied()` 사본으로 진입한다. 결과 메시가 `m_inputVTU`(ShallowCopy)·`m_originalQuadraticCells`(SetCells)를 심지 않음. 프리뷰는 소유 인스턴스를 그대로 넘겨 동작 불변
5. [계획] **제거** executor 싱글톤 접근 6곳 → 경로는 `DashDoeIoPaths` 로 호출부(GUI 스레드)가 해석해 넘긴다. **배치 경로 `DashManager::Mgr()` 접근 0건**
6. [계획] **신설** `controller/DashMorphingSnapshot.{h,cpp}` — executor 가 live `DashHandlePickingInteraction` 대신 값 사본(`DashMorphingInputSnapshot`)을 수령. 부수 효과로 `loadHandlesFromVtp` 가 GUI 의 live 핸들을 DeepCopy 로 덮어쓰던 경로가 사라졌다
7. [계획] **전환** D3-M2 캐시 — 값 타입을 `shared_future<shared_ptr<Context>>` 로. 소유가 future 에 실려 dangling 이 원천 소멸하고 같은 키 동시 진입 시 파싱이 1회로 수렴하며, 무거운 `.dat` 파싱은 락 밖에서 돈다. 로드 실패·예외는 캐시하지 않고 항목을 빼 다음 호출이 재시도. 반환형 파급 28곳(`getOrLoad` 15 · `get` 5 · `activeContext` 8) 수렴
8. [계획] **신설** D3 양층 규약 — `updateActor` 메인스레드 가드 + 기존 위반자 `DashConditionParameterization::commitEntryValue` 가 변이 구간 중 편집을 거부(막지 않으면 배치 restore 에 덮여 lost update)
9. [계획] **전환** D7 변이 창 — inject→export→restore 를 `DashContextMutationScope` + `ConditionDvInjection`/`MeshInjection` scope guard 로 묶었다. 변이 창 닫힘이 문장 순서가 아니라 스코프 수명에 걸려 중간 return 에도 복원이 보장된다. `ExecuteOneSample`·`ExecuteOneSampleConditionOnly` 동일 규약
10. [계획] **수리** D5 현존 위반 — `runAnalysisInThread`(워커)가 GUI 소유 `DashDesignVariableModel` 을 직접 읽던 7곳(`rowCount`·`data` 6 + `saveResultsAsDvTable` 경유 1)을 워커 기동 직전 메인 스레드 `DashDesignVariableSnapshot` 으로. 워커의 `QAbstractItemModel` 직접 접근 0건
11. [계획] **신설** D5 규약·가드 — `docs/ThreadingContract.md`(워커 진입 파라미터 금지 타입 화이트리스트 + 코드 리뷰 체크리스트) + `controller/DashThreadAffinity.h` 의 `DASH_ASSERT_MAIN_THREAD`(디버그 assert / 릴리스 `qCritical`) 를 렌더 계열 3곳(`GetRenderWindow`·`Redraw`·`MakeMorphingInputSnapshot`)에. 규약만으로는 재발을 못 막고 assert 만으로는 무엇이 금지인지 안 남는다
12. [회귀] **수리** (리뷰 F1) condition-only DOE 전면 차단 — 새 게이트가 `snapshot.isValid()`(= `inputVTU && morphingHandles`)를 요구했으나 두 값은 기하 파라미터화 UI(`SetInputVTU` → `InitializeHandlePicking`)를 거치지 않으면 채워지지 않는다. 구 게이트 `!interaction` 은 `GetHandlePickingInteraction()` 이 늘 lazily 생성해 **발동한 적이 없어**, 사실상 게이트가 새로 생긴 것이었다. FE 조건만 쓰는 프로젝트는 전 샘플 `.dat` 미생성
13. [회귀] **수리** (리뷰 F2) RBF 커널 반경 미전달 — 반경을 싣는 지점이 `Execute()` 안에만 있어 `performMorphingAndExport` → `ExecuteOneSample` 직행 경로가 우회, 산출물이 조용히 기본 10.0 형상이 됐다. Model Runner 경로는 per-Job 분리가 만든 회귀이고 **Optimizer 경로는 선재**(반경 전달 코드가 애초에 없어 공유 엔진의 잔존값에 의존)로, 같은 수정이 둘을 닫았다 — **Optimizer 결과 형상은 이번 변경으로 의도적으로 달라진다**(회귀가 아니라 교정. 이전 결과를 기준선으로 쓰고 있었다면 재실행 필요)
14. [회귀] **수리** (리뷰 F3) 정적 소멸에서 파괴된 `DashManager` 참조 — `~DashProjectManager()` 의 `delete m_project` 가 `DashProject` 의 QObject 자식을 연쇄 소멸시키고 `~DashModelRunner()` 가 `DashManager::Mgr()` 를 참조한다. 선-초기화 순서를 `Mgr` → `Instance` 로 반전
15. [회귀] **수리** (런타임 검증) `~DashProjectManager()` 의 `delete m_project` 제거 — 14항의 순서 반전이 그 대가로 데몬 수거를 깨지는 체인 뒤로 밀었다. `QApplication` 사후라 이벤트 디스패처가 없어 view 의 모델 해제 콜백이 타이머를 못 띄우고(`QBasicTimer` 경고 3줄), 체인이 중간에 멈춰 `~DashManager()` 가 미실행 → `shutdownBlocking()`×4 불발 → **데몬 4종 고아**. 자식 소멸자에 저장·flush 부작용이 없어 프로세스 종료 시 OS 회수에 맡김
16. [회귀] **수리** (리뷰 F6) `getOrLoad` 의 promise 충족을 `PromiseCloser` 스코프 가드로 — `emplace` 후 `set_value` 전에 예외가 나면 맵에 broken future 가 남아 이후 그 경로의 모든 호출이 `std::future_error` 를 던졌다. D7 과 같은 기법
17. [회귀] **수리** (리뷰 F8) 변이 창을 레지스트리 전역 카운터 → 컨텍스트 per-key 로 축소 — A.dat 배치가 무관한 B.dat 의 GUI 편집을 막지 않는다. 경로는 컨텍스트가 이미 보유한 `loadedFilePath()` 라 추가 배관 없음
18. [검증] **테스트 신설** `tests/tst_thread_affinity` — `DASH_ASSERT_MAIN_THREAD` 가 딛고 선 `isMainThread()` 를 실제 `QThread` 로 검증. 이 판정이 늘 true 를 돌려주면 본 티켓이 건 가드 6곳이 전부 조용히 무력화된다
19. [파생] **정리** 스냅샷 전환으로 고아가 된 `DashDoeConfigManager` 의 include·fwd decl 제거 · `DashAnalysisLauncher.h` 의 존재하지 않는 `runAnalysis()` 주석 정정

**D4 는 작업 0** — 전역 `std::cout`/`cerr` rdbuf 스왑이 repo 에 없어(1st-party `rdbuf` 매치 0건) 대상 소멸 확인만 했다.

### 검증 상태

Release 빌드(에러 0 · 변경 파일 신규 경고 0) · `tst_thread_affinity` · 정적/구조 확인(배치 경로 `Mgr()` 0건 · 결과 메시 앨리어싱 0건 · operator 3단이 per-Job 위에서만 · 복원이 scope guard · `try_emplace` 반환값 · 소비자 28곳 전수) 통과. 런타임 수동 4건 중 **1건(앱 종료·고아 프로세스 0건)만 통과**했고, 완료 시점 기준 나머지 3건(condition-only DOE · RBF 커널 반경 · 단일 스레드 무회귀 스모크)은 worktree 정리로 빌드 산출물이 사라져 미실행이다. 동시성 기준(동시 호출 시 파싱 1회 · 두 스레드 앨리어싱 · 변이 창 중 메인 읽기)은 본 티켓이 스레드를 만들지 않아 여기서 실행 불가 — [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 소유.

**W10-e([#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214)) 착수 게이트 오픈** — M1 + M2 완료.

---

## [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) W10-b — 모핑 DOE 배치 per-sample 분해 파일럿

**계획 8항 / 계획 외 14항** (회귀 5 · 검증 5 · 선재 2 · 파생 2) — 2차 파동에서 계획 외 비율이 가장 높다. 스레드를 도입하지 않고 **동기 루프를 이벤트 연쇄로 펴는** 작업이라, 루프 콜스택이 암묵적으로 보장하던 것(단일 착수·컨텍스트 수명·순서)이 한꺼번에 드러났다.

1. [계획] **전환** `Execute`(`:49-404`) → `PrepareBatch` + `RunOneSample` 2표면. 준비 산물을 `DashMorphingRunContext` 값 타입으로 뽑아 **"준비 없이 실행" 을 컴파일 불가**로 만들었다. `ExecuteOneSample`·`ExecuteOneSampleConditionOnly` 의 `bool` 을 `DashSampleResult{runKey, ok, reason}` 으로 승격
2. [계획] **신설** `model/DashBatchLedger.{h,cpp}` — 케이스당 스테이지 배열 + `terminalStage` + 스테이지→통지 매핑. `setStageState`(단일 전이) · `finishBatch`(단일 종료) · `abortBatch`(착수 거부) · `morphingBatchActive`([#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 가드 근거)
3. [계획] **전환** F(dfsxml) 꼬리 117줄 → `continueDfsxmlForSample` per-sample 연쇄
4. [계획] **제거** `waitForVtuFileComplete`(정의 67줄 + 선언 + 호출) · `msleep(1000)+processEvents` — 배치당 **`1000ms + N × 500ms` 확정 소진 소멸**. 부수로 `DashJobRunner` 의 `processEvents` 가 16 → 3, model 계층 38 → 25
5. [계획] **전환** C(dat/inp) 꼬리 326줄 → `continueDatForSample` + `submitAnsysTaskForSample`/`submitAbaqusTaskForSample`, Abaqus 런처 1회 준비를 `prepareAbaqusBatchLauncher` 로 분리
6. [계획] **제거** 성공 판정용 `QFile::exists({key}.dat / .vtu / .inp)` 3곳 — 성공의 유일 근거를 `DashSampleResult::ok` 로. 낡은 산출물이 성공으로 위장하던 경로 소멸
7. [계획] **제거** `Execute`·`MorphFromDoeSamples` 래퍼(호출부 0곳) · 읽히지 않던 `projectPath` 인자 · 사문 지역변수 3개
8. [계획] **테스트 신설** `tests/tst_batch_ledger` 9케이스 — 장부가 순수 값 타입(비 `QObject`)이라 Qt Core+Test 전용 하네스에서 전이·매핑·종료 판정을 환경 없이 검증한다
9. [검증] **조정** C = **2칸**(모핑·솔버), 티켓은 1칸 — 1칸이면 stage 0 `Done` 이 `"Done"` 으로 나가 **ANSYS 완료 전에 집계기가 케이스를 닫는다**. F = 3칸으로 두고 규칙 "마지막이 아닌 칸의 `Done` → `"Running"`" 을 세웠다. 배열형 인코딩 선택 자체는 티켓 그대로
10. [회귀] **수리** (자체 리뷰 HIGH) `finishBatch(const QString&)` 가 호출부의 `m_batchFailReason` 에 바인딩된 뒤 `isEmpty()` 검사 **전에** `clear()` 를 해, 취소·착수 거부·연속 실패 차단기·상한 초과 **전 경로가 사유를 잃고 `jobFinished`** 로 성공 보고. 값으로 받도록 수정
11. [선재] **수리** `ExecuteOneSample` 이 VTU 쓰기 실패를 경고만 남기고 `true` 반환 — 호출부의 파일 존재 검사(6항)를 없앤 탓에 **낡은 VTU 가 motion-writer 입력**이 될 수 있었다. `Write()` 결과를 판정해 실패 반환. 이 실패를 관용하던 워크플로가 있었다면 동작이 달라진다
12. [회귀] **수리** Morphing source 없는 `.dfsxml` 템플릿이 C 경로로 흘러 생성되지 않는 `{key}.dat` 으로 ANSYS 태스크를 제출(구 코드는 존재 검사로 Failed 처리). `dat`/`inp` 아닌 확장자를 착수 거부로 수렴
13. [회귀] **수리** `m_motionLauncherQueue` 를 취소·종료 시 비우지 않아, 죽인 프로세스의 `finished` 핸들러가 `startNextMotionLauncher` 를 걸어 **이미 Cancelled 로 확정된 행을 장부 밖 통지로 되살림**
14. [회귀] **수리** `finishBatch` 가 장부만 비우고 `m_morphBatch` 를 남겨, 기본 컨텍스트(빈 `setName`·`analysisType`) 위에서 디스패치가 계속되며 솔버 태스크를 제출. `releaseMorphBatch()` 호출 + `samplesForMorphing` 키 중복 제거(태스크 핸들 누출 차단)
15. [회귀] **수리** `setStageState` 의 장부 컨텍스트 참조 → 사본(동기 슬롯 재진입 시 댕글링) · motion-launcher 착수 판정을 큐 길이 → "도는 런처 없음"(앞선 배치의 잔여 큐에 걸림)
16. [검증] **수리** (`ticket-review` HIGH) 착수 지점이 둘(프로세스 종료 핸들러 · 샘플 완료 슬롯)이 되면서 motion-launcher 가 **동시에 2개** 뜰 수 있었다. 직렬 가드를 `startNextMotionLauncher` 로 옮겨 착수 판정 소유자를 하나로
17. [검증] **수리** (리뷰 MED-HIGH) 솔버 런처 준비 실패를 착수 거부로 수렴시켜 **모핑 산출물이 아예 생성되지 않는 회귀**. `terminalStage` 하향("모핑만" 배치)으로 F 의 Ansys 미설정 skip 과 대칭화. AC 문구도 *착수 거부* → *"모핑만" 배치 후 `Done`* 으로 개정
18. [검증] **수리** (리뷰 MED → HIGH 연쇄) `abortBatch` 가 진행 중 솔버 태스크를 끊지 않아, 완료 콜백이 장부가 비워진 뒤 도착해 Failed 로 닫힌 케이스를 `Done` 으로 되살렸다. `cancelSolverTaskForKey` 신설 → 그 수정이 `cancelAllRuns` 의 함수 스코프 `QMutexLocker` 와 겹쳐 **데드락**을 만들어, 락 범위를 ANSYS 취소 루프로 좁혔다
19. [검증] **수리** (리뷰 MED) 전 케이스 실패인데 `jobFinished`(성공 채널)로 나갔다. 성공 0건이면 `jobFailed`
20. [선재] **수리** (리뷰 HIGH) `m_cancelledTasks` 를 비우는 곳이 없어, runKey 재사용 탓에 **한 번 중단된 배치의 키가 이후 전 실행에서 취소를 못 받았다**. 기록자가 1곳 → 4곳으로 늘며 노출이 넓어진 선재 결함. 핸들 free 자리에서 함께 제거
21. [파생] **신설** P5 배치 종료 요약 — 종전 종료 로그는 실패가 섞여도 "=== Completed processing ... ===" 로 성공처럼 읽혔다
22. [파생] **수리** `partName` 미해석 실패 사유가 `"Failed"` 뿐이어서 원인(`target_component` 미설정)이 로그에서 사라지던 것

### 새로 세운 계약 5종

1. **성공의 유일한 근거 = `bool`** — 생산자(`ExecuteOneSample`)의 반환값이 진실해야 하므로 VTU 쓰기 실패를 `false` 로 바꿨다(11항). 콜백은 실패 **사유** 전용
2. **전이 1회 = 통지 1회** — `setStageState` 만이 상태를 바꾸므로 "통지 없는 전이" 가 구조적으로 불가능
3. **마지막이 아닌 칸의 `Done` → `"Running"`** — 집계기(키별 첫 터미널로 케이스를 닫음)의 조기 종료 차단
4. **단일 종료 지점** — 배치를 떠나는 모든 경로가 `finishBatch` 를 통과하고 `jobFinished`/`jobFailed` 중 하나를 방출
5. **디스패치 구간의 무조건 `return`** — 소멸한 `return` 8곳을 대신해 템플릿 치환 폴백 도달 경로를 2가지로 고정

### 검증 상태

Release 빌드 성공 · 신규 경고 0 · `ctest` 5/5. 정적 확인: `grep waitForVtuFileComplete` → 0 · `DashJobRunner` 내 `msleep` → 0 · 성공 판정 경로의 파일 존재·크기 검사 0건. **실물 미검증 6종**(DOE 프로젝트 데이터 필요) — 슬립 소멸 측정 · 잔존 산출물 위장 · 착수 거부 UI 복구 · 솔버 미설정 종결 · C 산출물 무변경 · 비모핑 폴백 무회귀.

---

## [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) — DOE 2단계 배치 이벤트·상태 3축

**계획 8항 / 계획 외 10항** (파생 6 · 회귀 4) — 결함 수리 4건이 전부 이번 전환이 만든 것이고, 선재·검증 계급이 0 이다. 계획 외의 절반 이상(파생 6)이 **이관 후 이름·중복 정리**인 것도 이 티켓 고유다.

1. [계획] **전환** 축 3 상태 표현 — 착수 시 `CaseState` 8종 flat enum 으로 구현했다가 [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) 머지 후 **`DashBatchLedger` 2칸**(stage 0 = STP 생성 · stage 1 = 해석 실행 · `terminalStage = 1`)으로 이관. `pending`·`current`·`activeRunKeys`·`failedKeys`·`active`·`cancelled` **6개 제거** — 진행 1건과 다음 착수분은 상태에서 파생하므로 인덱스 멤버가 0개다
2. [계획] **신설** 축 1 종료 수렴 — `finishBatch(reason, sweepAs)` 를 유일한 종료 지점으로. **조기 이탈 7곳 수렴**에 배치 컨텍스트뿐 아니라 **케이스 목록 구성까지** 착수 게이트 앞으로 옮겨, 종료 스윕이 전 케이스를 종료 상태로 확정한다. `finishBatch()` 가 `jobFinished`/`jobFailed` 1건을 방출해 Start 버튼 복구를 케이스 집계와 독립시켰다
3. [계획] **전환** 축 2 발신 — `updatePrtGeometryBatchFailed` 에 `stpPath` 를 실어 실패 슬롯이 완료 슬롯과 **동일 기준**으로 귀속. `onCommandFailed` 가 `commandId` 에서 경로를 뽑는다
4. [계획] **전환** 축 2 수신 — 슬롯 2곳을 `귀속 → 전이 → advance()` **3단**으로. 차단기·취소 확인·다음 착수·단계 마감이 `advance()` 한 곳에 모인다
5. [계획] **신설** Step 2 배치 고유 `launchId`(`doe:<analysisType>:<seq>`) — 완료·실패 핸들러 4곳이 대조. **식별자를 무명 파라미터로 버리는 지점 0건**
6. [계획] **전환** 구독 수명 — NX 구독·batchMode 는 단계 scope, Journal 구독은 `finishBatch()` 에서 해제. **데몬 정지가 `setBatchMode(false)` 보다 먼저**다(뒤집히면 drain 통지가 `loadPrtFailed` 모달로 샌다). Journal heap `Connection*` 3개 → 멤버 2개
7. [계획] **신설** 종료 단조성 — 종료 상태 재전이를 경고와 함께 무시. Analysis 단계 취소가 뒤늦은 `journalLaunchFailed` 에 Failed 로 덮이지 않는 근거
8. [계획] **테스트** `tst_batch_ledger` M2 케이스(`stageState()` 접근자)
9. [회귀] **수리** **빈 배치 종결 누락** — 활성 케이스 0건이면 `begin()` 이 빈 장부를 만들어 `finishStpPhase` 의 `hasBatch()` 가드가 job 시그널 없이 return 했다. Start 가 잠기고 이후 실행이 재진입 가드에 영구 차단된다 — **이 티켓이 없애려던 결함 3 그 자체**였다. 판정을 `phase == Stp` 로 바꿔 "아직 안 끝난 배치" 를 정확히 가른다
10. [회귀] **수리** (독립 검토 M3) **사용자 취소가 `Failed` 로 뒤집힌다** — `cancelAllRuns` 의 motion-launcher 루프에서 `kill()` 이 부르는 `finished` 핸들러가 ⑴ 케이스를 Failed 로 먼저 닫아 뒤이은 `Cancelled` 가 **종료 단조성에 삼켜지고** ⑵ 순회 중인 `m_motionProcesses` 에서 노드를 지워 반복자를 무효화(UB)했다. 표·DOE JSON·배치 요약이 전부 Failed 로 남고 `jobFailed` 가 나갔다. **7항이 도입한 종료 단조성이 만든 회귀** → 핸들을 먼저 빼앗아 사본을 돌고, 취소를 kill 보다 먼저 확정
11. [회귀] **수리** (M5) `batchActive()` 가 `m_ledger.active()` 만 봐서, 활성 케이스 0건인 A 배치 구간(`phase == Stp` 인데 `hasBatch() == false`)을 "배치 없음" 으로 오판했다. [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 의 모핑 단일화 가드가 이 술어를 쓰면 배치 중 프리뷰가 통과한다. 재진입 가드와 술어를 통일하고 `runWbpjDoeAsync` 의 인라인 조건도 호출로 교체 — **판정 근거가 한 벌만 남는다**
12. [회귀] **수리** `launchAnsysJournalDirect` 착수 게이트 1곳의 종결 신호 누락 — 직전 커밋이 상태 통지 3곳을 `reportCaseStatus` 로 통일했는데 `DashManager` 부재 게이트가 빠졌다. `runDirectJobs` 가 이미 `jobStarted` 를 낸 뒤라 Start 가 잠긴다
13. [파생] **신설** `beginBatch()` — 장부와 배치 스코프 상태를 세우는 **단 한 곳**(`finishBatch()` 가 비우는 단 한 곳과 짝). A 는 phase 를 그 옆에서 세워 `phase` 와 `hasBatch()` 가 갈리는 틈을 없앤다
14. [파생] **정리** 배치 스코프 상태를 한 벌로 — `m_morphCancelled` + `StpBatch::cancelRequested` → `m_batchCancelled` · `m_morphConsecFail` + `consecFail` → `m_batchConsecFail` · 상한 상수 2종 → `kBatchConsecFailLimit`(케이스 상한 2종은 서브시스템이 달라 존치). 부수 효과로 **"전이가 배치를 종결시키면 카운터가 리셋된다" 순서 의존이 소멸**
15. [파생] **정리** 어휘 통일 3라운드 — `advance` → `advanceStpPhase` → **`runNextStpCase`**(단계를 넘기는 것은 `finishStpPhase` 인데 이름이 그렇게 읽혔고 모핑 형제 `runNextMorphSample` 과도 비대칭) · `endStpStage` → `releaseNxCadBatchMode` · `StpBatch`→`WbpjBatch` / `BatchPhase`→`WbpjPhase` / `releaseStpBatch`→`releaseWbpjBatch`(구조체가 이미 Step 2 를 들고 있는데 이름만 Step 1 을 가리켰다). Phase(배치 단계) / Stage(장부 칸) 가 코드 전체에서 한 뜻으로 고정
16. [파생] **정리** 중복 조회 — 상태별 첫 STP 키 조회 2벌 → `firstStpKey()` · `runKeyForStp` 의 역방향 인라인 루프 → `StpBatch::caseFor()` · 도달 불가 가드 제거 · `notStarted` → `unfinished`(워치독 대기 중 Running 도 담긴다)
17. [파생] **정리** `launchAnsysJournalDirect` 의 날것 `caseStatusUpdated` 3곳 → `reportCaseStatus` 통일(`analysisType` 빈 문자열 → `m_currentAnalysisType` 값 불일치 동반 해소) · `abortBatch` 가 장부 유무와 무관하게 사유를 1회 로그 → `generateInputCases` 의 `logMessage`+`jobFailed` 3쌍이 `abortBatch` 한 줄씩으로 축소 · `"aborting STP phase"` 는 실동작(확보분은 Step 2 로 진행)과 반대라 `"no further STP requests will be sent"` 로 정정
18. [파생] **제거** `WbpjBatch::doeJsonPath` 죽은 필드(이관이 만든 고아, 정본은 장부 컨텍스트) · `startNextStpCase`(펌프가 하나면 착수 전용 함수를 둘 이유가 없다) · 지역 `configManager` 3곳 · 빈 람다 `connLog` · 헤더↔cpp 중복 주석 6쌍 · 3축 인라인 라벨 10개

### 사용자에게 보이는 동작 변화 5건

Step 1 취소 시 STP 확보분 상태 확정 · 조기 이탈 7곳에서 Start 버튼 복구 · 요약 로그 단계별 세분화 · Analysis 단계 취소가 Failed 대신 Cancelled 로 기록 · Step 2 진행 중 새 DOE 실행 거부.

### 검증 상태

Release 빌드 통과(자체 경고 0) · `ctest` 5/5. 정적 확인: wbpj 구간 `return` 19곳 전수 분류 → 배치를 매단 채 빠지는 `return` 0건 · 직접 `caseStatusUpdated`·`setSampleStatus` 호출 0건 · 구 심볼 잔존 0건. **기능 검증 미실시** — Step 1 이 NX, Step 2 가 Ansys 환경에 묶인다(티켓의 범위 축소 근거와 같은 제약). 상태 층위만 `tst_batch_ledger` 로 환경 없이 검증된다.

되돌린 판단 2건도 기록한다 — `DashBatchContext` 의 `BatchKind` 필드 신설 철회(`phase` + 장부가 이미 판별자를 답한다), `advanceStpPhase` → `runNextStpCase` 재개명.

---

## [#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264) — 장부 밖 실행 경로 통합 · 종결 지점 2곳 확정

**계획 10항 / 계획 외 10항** (회귀 4 · 검증 3 · 파생 3) — 종결 메커니즘 **2세대 공존**(런처 키 카운터 · 장부)을 해소하는 티켓이다. 계획 외 4건이 전부 리뷰에서 나온 회귀이고, 그중 2건(15·18항)은 "장부에 올리는 순간 성립하게 되는 결함" 계급이다.

1. [계획] **제거** `jobStarted` — 방출 · 선언 · 릴레이. 호출부 두 줄 위 `runDirectLauncherAsync` 가 이미 `analysisStarted` 를 내므로 **direct 경로의 이중 방출이 함께 사라진다**
2. [계획] **전환** stage 인덱스 정합 — 티켓은 `onFeTaskCompletedQueued:1156` **1곳**만 지목했으나 리포트 지점 **15곳**(`morphSolverStage()` 6 + `kMotionLauncherStage` 9)이 스테이지 번호를 상수로 박고 있어 1칸 장부에서 전이가 범위 밖으로 버려진다. 전부 `m_ledger.terminalStage(key)` 로 치환 → `morphSolverStage()` 는 호출처 0곳이 되어 삭제. 모핑 배치(C=1 / F=2)와 1칸 장부(=0) 양쪽이 맞는다
3. [계획] **전환** 착수 거부 — `generateInputCases` 의 무신호 `return` 7곳 → `abortBatch(reason)`. 이제 이 함수의 모든 `return`(20곳)이 `abortBatch` / `finishBatch` / 하위 배치 소유를 통과한다
4. [계획] **신설** 활성 케이스 0건 검사 3곳(모핑 · 폴백 · FE-safe) — `hasBatch()` 가 false 라 `beginBatch` 를 해도 `finishBatch` 가 조용히 return 하던 구멍
5. [계획] **전환** 폴백 · FE-safe · Direct **3경로 장부화** — 모두 `beginBatch(keys, 1, 0, ctx)` 로 열고 상태 보고를 `setStageState` 로 일원화. **키 전량 등록이 루프보다 앞서야** 마지막 케이스가 닫히기 전에 `finishBatch` 가 조기 발동하지 않는다
6. [계획] **전환** 솔버 런처 미초기화를 실패가 아니라 **입력 파일 생성 모드**로 — `Done` 으로 닫는다([#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) 의 `terminalStage` 하향과 같은 형태)
7. [계획] **전환** Direct 키 규칙을 `directRunKey` 한 곳으로 — `.wbpj` 는 prt basename, prt 미지정이면 wbpj basename 으로 자리를 잡아 그 케이스를 Failed 로 닫는다. 런처가 키를 짐작하지 않으므로 종전 불일치도 해소
8. [계획] **제거** `launchAnsysJournalDirect` 의 자체 종결 방출 3곳
9. [계획] **제거** 런처 키 카운터 — `m_isLauncherRunTracking` / `m_expectedRunKeys` / `m_completedRunKeys` + 카운터 블록 + 키 수집 2곳 + `cancelAllRuns` 의 clear. 카운터가 **성공 채널만 알아 전건 실패에도 `analysisFinished` 를 먼저 내던** 문제가 함께 사라진다
10. [계획] **테스트** `tst_batch_ledger` +4건 — `terminalStage` 의 1칸·미등록 키 응답, 1칸 장부의 상위 stage 전이 폐기(회귀 방지), 전건 Failed 후 `active()` false, 중복 통지
11. [파생] **정리** 활성 키 목록을 함수 앞에서 1회 산출 → 장부 개설 · 0건 판정 · 모핑 샘플 필터가 같은 목록을 본다. 모핑 분기의 중복 산출도 함께 소멸
12. [파생] **수리** `startNextMotionLauncher` 의 스냅샷 빔 이탈 → `abortBatch`. 큐를 들고 빠지면 대기 케이스가 영영 닫히지 않는데, 5항이 그 대기 케이스를 장부에 올리는 순간 성립한다. **원인(스냅샷 수명주기)은 손대지 않고 증상만** 종결로 수렴 — 유예된 티켓의 범위는 그대로 남는다
13. [파생] **전환** Direct `.dfsxml` 의 `"Pending"` 은 raw `caseStatusUpdated` 로 존치 — `Pending` 은 `begin()` 초기 상태와 구분되지 않아 `apply` 가 통지 대상에서 제외한다. 종결에 영향 없는 UI 힌트이므로 DOE 경로의 `"Enqueued"` 와 같은 형태로 두고 주석으로 근거를 남겼다
14. [검증] **제거** (리뷰) `reportCaseStatus` 의 장부 밖 폴백 — 배치 종결 후 도착한 지각 통지가 `m_currentAnalysisType`(직전 DOE 값)으로 나갔다(direct 는 빈 문자열이어야 한다). 종결 후 통지는 정의상 터미널 이후이므로 **배치 안과 같은 이유로 버린다**. `dashStageStateToStatus()`·`contains()` 는 소비자가 사라져 함께 제거
15. [검증] **전환** (리뷰) `reportCaseStatus` 시그니처에서 `stage` 제거 — 호출부 **21곳이 예외 없이** 터미널 칸을 넘기고 있었다. `setStageState` = 명시 칸 / `reportCaseStatus` = 터미널 귀속으로 역할이 갈린다. **타입이 이 축소를 보증한다** — 터미널 아닌 칸을 넘기던 호출부가 하나라도 있었으면 `int` → `DashStageState`(enum class) 변환이 없어 컴파일이 깨진다
16. [검증] **테스트 신설** (리뷰) `model/DashDirectJobPlan.h`(헤더 온리, QtCore 만)로 direct 파일→키·분류 판정을 순수 함수로 분리 + `tst_direct_job_plan` 6건. `DashJobRunner`/`DashAnalysisLauncher` 는 `DashManager.h` 가 VTK 를 끌어와 테스트 타깃에 넣을 수 없어 **판정만 떼어 냈다**
17. [회귀] **신설** (리뷰) `runDirectJobs` 재진입 가드 — `beginBatch` 호출자가 됐는데 가드가 없어 **남의 케이스 기록을 지운다**(`runWbpjDoeAsync` 와 같은 근거)
18. [회귀] **제거** (리뷰) `DashAnalysisLauncher::cancelAllRuns` 의 자체 `analysisFailed` — 협조적 취소 중 Start 를 풀어 다음 실행이 진행 중인 배치의 장부를 덮었다. 종결을 러너에 일임하고 취소 요청만 로그로. **동작 변화: Stop 후 Start 는 진행 1건이 끝나야 풀린다**
19. [회귀] **수리** (리뷰) direct 키 중복 시 장부는 1칸인데 태스크는 2개 제출 → 핸들 누수 + 둘째 완료 통지 소멸. 중복 2건째와 빈 키를 사유 로그와 함께 제외
20. [회귀] **수리** (리뷰) direct `.wbpj` 가 `loadPrtFailed` 를 미구독 → NX 로드 실패 시 케이스가 Running 으로 남아 배치가 닫히지 않고 **Start 가 영구 잠김**. 구독 추가 + **1건 제한**(`loadPrtFailed` 가 stp 경로를 싣지 않아 다건 귀속이 원천 불가), 초과분은 착수 없이 Failed. 이 제한은 [#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265) 가 해제한다

### 검증 상태

`ctest` 6/6 · Release 빌드 자체 경고 0. AC 9항 중 자동 확인 9항 통과(종결 신호 방출처 = `finishBatch` 2 + `abortBatch` 1 · `return` 20곳 전수 가드 · 액션 1회당 `analysisStarted` 1회). **GUI 런타임 재현 4건 잔여** — H3 재현 조건에서 Start 복구 · 솔버 런처 미초기화 시 입력 파일 생성 유지 · 실행 중 케이스 표·로그 갱신 · 취소 시 Start 해제 시점.

**빌드 인프라 결함이 함께 드러났다** — `CMakeLists.txt:63` 이 `GLOB_RECURSE` 를 `CONFIGURE_DEPENDS` 없이 쓰는데 기존 `build/` vcxproj 가 [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) 신규 `DashBatchLedger.cpp` 를 담고 있지 않아 `LNK2019` 10건. `cmake -S . -B build` 재구성으로 해소했으나 **같은 브랜치를 체크아웃한 다른 사람도 같은 링크 실패를 본다**.

---

## [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) W10-e — WorkerJob · 서브시스템 직렬 풀 2종 · 모핑 국면 단일화

**계획 10항 / 계획 외 6항** (검증 3 · 파생 3) — **결함 수리 0항**이다. 2차 파동에서 회귀·선재가 0인 유일한 티켓이고, 그 이유는 선행 3건([#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) 진입 경계 · [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) 준비/실행 2표면 · [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251)·[#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264) 장부·단일 종결)이 **워커를 끼울 자리를 완성해 둔** 데 있다. 변경의 핵심은 `RunOneSample` 호출 1줄이 Job 으로 바뀌고 `onMorphSampleFinished` 가 슬롯이 되는 것이다.

1. [계획] **신설** `controller/async/ThreadPools.{h,cpp}` — `morphingSerialPool()`·`rwSerialPool()` 각 `maxThreadCount=1`, `waitForAllSerialPools()`. `setExpiryTimeout(-1)` 로 유휴 워커를 재사용한다(샘플마다 스레드를 새로 띄우면 **DLL thread-local 초기화 비용이 케이스 수만큼** 붙는다). 직렬은 CPU 활용을 낮추는 선택이 아니라 **operator 설정 상태의 상호배제**가 목적 — 모핑 엔진은 내부적으로 16 스레드를 띄운다. RW 풀은 선언만(첫 소비자는 [#280](https://github.com/NumeRealWorks/DashOpti_GUI/issues/280) 이 아니라 그 후속으로 재판정됐다)
2. [계획] **신설** `controller/async/WorkerJob.{h,cpp}` — `QtConcurrent::run(pool)` + `QFutureWatcher` → Job 시그널 번역. `shared_ptr<atomic<bool>>` 취소 채널(맨 멤버 플래그 금지), 결과는 pull 접근자(`ProcessJob` 규약 계승), task 예외를 Failed 사유로 번역
3. [계획] **신설** `controller/async/MorphingGate.{h,cpp}` — "모핑 진행 중" 의 정본. `batchActive()` 는 진입점에서 도달 불가(`DashJobRunner` 는 세트별 launcher 소유이고 `DashManager` 는 둘 중 어느 것도 참조하지 않는다)하므로 판정자를 **프로세스 전역**으로 세웠다. 수명은 배치 전체가 아니라 **모핑 국면**(준비 성공 \~ `releaseMorphBatch`) — 배치 종결까지 쥐면 모핑이 0건인 솔버 구간까지 프리뷰가 막힌다. 워커 스레드에서의 해제는 게이트 스레드로 마샬링
4. [계획] **전환** `runNextMorphSample` 의 동기 `RunOneSample` 호출 → WorkerJob 착수. `onMorphJobFinished` 신설(완료 원천 번역)만으로 **연쇄 · 정책(P1·P2·P3·P5) · 장부 · 단일 종료 지점은 무수정**
5. [계획] **신설** 모핑 진입점 6곳 게이트 가드 — 조기 반환값 고정(5 = **`false` 필수** — 양 호출부가 검사하므로 `true` 면 조용한 성공 오인 · 2 = `nullptr` · 3 = reject) + 모핑 파라미터 편집 탭 비활성 + 상태바 안내 + indeterminate 스피너
6. [계획] **전환** `batchActive()` 에 워커 생존 항 추가 · `releaseMorphBatch()` 에 게이트 배치 축 해제. Start 재활성이 워커보다 앞서면 다음 배치가 진행 중 워커와 겹쳐 등급 2 가 뚫린다
7. [계획] **신설** 취소·상한 **UI 해방 2축** — Stop 직후 즉시: 스피너 해제·로그·잔여 케이스 Cancelled 기록(P4). 워커가 DLL 을 떠난 뒤: Start 재활성(등급 2 유지). `refreshRunControls()` 가 Start/Stop 활성의 단일 판정점
8. [계획] **전환** per-case 상한을 사후 판정 → `m_morphWatchdog` QTimer **선점**. 사후 검사 제거 — 종전은 `RunOneSample` 이 반환한 뒤 상한을 검사해 "이미 10분 태운 뒤" 알렸다
9. [계획] **신설** `docs/ThreadingContract.md` **7절** — "두 풀 동시 사용은 두 Job 의 서브시스템 집합이 서로소일 때만. 두 서브시스템을 함께 만지는 Job(= 모핑 샘플)은 모핑 풀 하나에만 오르고, 그 Job 이 활성인 동안 RW 풀에 제출하지 않는다" + 리뷰 체크리스트 4항 + `MorphingGate` 절
10. [계획] **전환** 앱 종료 배수를 `aboutToQuit` 에 — `~DashManager()` 의 `shutdownBlocking()`×4 는 정적 소멸 시점이라 배수 자리로 부적절하고, `aboutToQuit` 이 정적 소멸보다 앞서므로 순서 요구가 자연히 만족된다
11. [파생] **설계 이탈** `MorphingGate::Token` 기본 생성은 **비어 있다** — Design 스케치의 `Token()` 이 획득이면 `DashJobRunner` 멤버로 두는 순간 러너 생성 시점에 게이트가 잠긴다. 획득은 `acquire()` 하나로 모으고 해제는 소멸·이동대입·`release()` 로 수렴
12. [파생] **설계 이탈** 국면 참가자를 **2토큰 카운트**(배치 축 / 워커 축)로 센다. 워커 축은 task 캡처에 실려 워커가 모핑 DLL 을 떠날 때 풀린다. **`Job::finished` 에 걸면 안 된다** — `cancel()` 은 즉시 터미널로 가지만 DLL 은 계속 돌아, 그 시점에 게이트를 놓으면 UI 해방 2축이 무너진다
13. [파생] **철회** 초판의 "executor 통지 표면 QObject 화·시그널화" 무효 — [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) 이 통지를 값 반환(`DashSampleResult`)으로 닫아 승격할 표면이 없다. 워커 경계를 넘는 것은 값뿐이라 마샬링 대상이 0
14. [검증] **테스트 신설** `tests/tst_worker_job` **9케이스** — 성공 페이로드 · 실패 사유 · 예외→Failed 번역 · 취소 즉시성 + 늦은 완료 폐기 · 직렬 풀 최대 동시성 1 · 두 풀 구분/배수 · **task 실행 중 메인 이벤트 루프 생존**(AC "샘플 내부까지 UI 반응") · 취소 2축 순서 · `waitForAllSerialPools()` 배수 완결성
15. [검증] **테스트 신설** `tests/tst_morphing_gate` **6케이스** + **변이 테스트** — 마샬링 제거 · `release()` 멱등성 제거 2건을 주입하면 실패하고 복원하면 통과함을 확인했다. **통과가 공허하지 않음을 증명한 것**이 이 항목의 실체다
16. [검증] **계측 신설** 준비 구간 `QElapsedTimer` — AC "측정해서 잔여 정지 시간을 기록한다" 가 사람 스톱워치 대신 로그로 남는다. 워커화 후 남는 **유일한 GUI 정지원**이 준비 구간(스냅샷 DeepCopy + `.dat` 파싱)이다

### 관측 동작 변화 2건

- **Stop 의 P1 의미가 바뀌었다.** [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) 에서는 동기 실행이라 Stop 이 샘플 반환 뒤 처리돼 진행 1건의 결과가 보존됐다. 이제 Stop 은 진행 케이스를 즉시 `Cancelled` 로 닫고 늦은 결과를 폐기한다 — 약속은 "UI 즉시 해방" 이지 "CPU 즉시 해방" 이 아니고, DLL 은 계속 돈다.
- **워커화가 기존 방어선 하나를 처음으로 발화시킨다.** 공유 컨텍스트 변이 창의 GUI 심층 편집 거부(`DashConditionParameterization.cpp:347`)는 종전에 배치가 GUI 스레드를 점유해 **도달 불가**했다. 이제 실제로 동작하며, 판정 근거인 레지스트리 `m_mutating` 맵은 `std::mutex` 로 보호돼 워커에서 읽어도 race 가 없다.

### 자동화 범위의 한계

진입점 6곳의 **실제** 거부는 단위 테스트로 옮길 수 없다 — `DashManager`·`DashMorphingUtils` 가 VTK·OCCT·모핑 DLL 을 끌어와 Qt Core 전용 테스트 타깃에 들어가지 못하고, 앱은 라이브러리가 아니라 단일 exe(`GLOB_RECURSE`)라 링크할 대상 자체가 없다. 게이트 술어는 `tst_morphing_gate` 가 봉인하므로 남는 미검증분은 "각 진입점이 그 술어를 호출하는지" 6줄로 좁혀진다. `ctest` 8/8 · Release 빌드 성공. AC 잔여 1건은 **`.vtu` 파라미터 정합 실기 확인** — 주 실패 모드가 크래시가 아니라 조용한 오형상이라 "안 죽었다" 를 통과 기준으로 쓸 수 없다.

---

## [#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265) — 솔버 제출 통합 · direct `.wbpj` 배치 기제 승격

**계획 10항 / 계획 외 6항** (파생 4 · 선재 1 · 검증 1) — 순변경이 +9줄(6파일 +448/-439)인데 항목 16개다. 중복 제거가 본체이고, `ticket-review` 3축 검토에서 **논리·문법 결함 0** 이었다.

1. [계획] **전환** ANSYS `.dat` 제출 **3벌 → 1벌** `submitAnsysTaskForSample(runKey, datPath, outDir)`. stage 하드코딩(`kPostMorphStage`) 제거 → `reportCaseStatus` 경유 `terminalStage(runKey)` 유도. 완료 콜백 람다 3벌은 파일 스코프 `dashOnAnsysTaskCompleted` 1개로
2. [계획] **전환** Abaqus `.inp` 제출 **2벌 → 1벌** `submitAbaqusTaskForSample`. direct 의 인라인 완료 람다를 지우고 정적 `onAbaqusTaskCompleted` 에 합류 — **direct 도 실패 시 artifacts/logs 진단을 받게 됐다**
3. [계획] **전환** `WbpjBatch` → `StpCase` 케이스별 확장 — `wbpjPath`/`prtPath`/`targetComponent`/`outputBaseDir` 에 더해 **Journal 샘플 행(`journalHeaders`·`journalSample`)까지 케이스가 든다**. 표를 배치에 남기면 통합 함수가 "DOE 표가 있나?" 분기를 다시 갖는다 → DOE 의 enrich 를 준비 시점 1회로 옮기고 `initIndParam`·`rawDoeTable` 필드를 없앴다. **"DOE 표가 있나?" 분기 0**
4. [계획] **전환** `WbpjBatch::launchId` 스칼라 → `QHash<launchId, caseKeys> launches`. 구독 커넥션은 **2개 그대로** 두고 람다가 launchId 로 자기 케이스 집합을 조회한다 — 그룹마다 connect 하면 `new QMetaObject::Connection` 수명 관리가 되살아난다. `launchWbpjJournal` 이 (wbpj · target_component · outputBaseDir)로 묶어 그룹마다 launchId 를 발급하고 완료·실패를 `openKeys()` 전량이 아니라 **그 집합**으로 판정한다 → **한 wbpj 의 실패가 다른 wbpj 의 케이스를 닫지 않는다**
5. [계획] **전환** 실패 람다가 `abortBatch` 대신 **그 런치의 케이스만** `Failed` 로 닫는다. 전건 실패면 마지막 전이가 `finishBatch` 로 `"all N case(s) failed"` 를 낸다
6. [계획] **신설** direct `.wbpj` 를 배치 기제로 승격(`runDirectWbpjBatch`) — `updatePrtGeometry` + `setBatchMode(true)` + `m_stpWatchdog` + 서킷브레이커 + `runNextStpCase` 펌프를 물려받고 `launchWbpjJournal` 로 합류. 인라인 `connect` 3개와 커넥션 수명 관리 삭제
7. [계획] **제거** `launchAnsysJournalDirect` — **Journal 진입점이 하나**다
8. [계획] **제거** 1건 제한 — `kDashDirectWbpjRunLimit`·`wbpjRunnable`·`wbpjExcessKeys`. [#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264) 가 `loadPrtFailed` 귀속 불가로 걸었던 제한이 배치 기제 승격(귀속을 배치 시그널이 담당)으로 자동 해제됐다
9. [계획] **신설** 혼합 direct 배치 거부 — `DashDirectJobPlan::mixedWbpjSelection`(순수 함수) 판정으로 위젯 Start 가 사유와 함께 막고 `runDirectJobs` 가 이중 방어한다. **착수 0건이라 부분 실행이 없다.** 5지점(`firstStpKey`·`finishStpPhase`×2·`launchWbpjJournal`·`cancelAllRuns`)의 "배치 = wbpj 전용" 전제가 그대로 산다
10. [계획] **테스트** `tst_direct_job_plan` 다건 착수 · 혼합 거부(wbpj-only·non-wbpj-only 통과, skip 된 파일은 혼합 근거가 아님) · `tst_batch_ledger` 에 착수·완료가 `terminalStage` 로 같은 칸에 떨어지는지(1·2·3칸 + 터미널 하향)
11. [선재] **수리** `target_component` 를 **basename 으로 통일** — DOE 는 2026-04(`5c177d2`) 이래 데몬에 `completeBaseName()` 을 보냈고, direct(`4b02ae8`, 2026-06)가 DOE JSON **저장** semantics(wbpj 기준 상대경로)를 변환 없이 복제한 것이 이탈이다. `.prt` 가 `.wbpj` 와 같은 폴더일 때만 두 값이 우연히 일치해 드러나지 않았다. **DOE 무변경이라 회귀 면적은 direct 한쪽뿐**이다. 실환경 실측 대신 레포 내부 증거 3건으로 확정했다
12. [파생] **수리** 태스크 생성 실패 시 `m_abaqusRunDirs` 를 함께 되돌린다(모핑 경로에 있던 누락)
13. [파생] **수리** `firstStpKey` 를 배치 케이스가 있는 키로 좁힘(`caseFor(key)` 가드)
14. [파생] **전환** direct 의 ANSYS 미설정 처리를 DOE 와 통일 — 종전 `Failed` 에서 "해석 칸을 잘라 STP 만 생성" 으로 바뀐다. 배치 기제를 물려받는다는 것의 일부이며 코드 경로가 하나로 유지된다. NX 미설정은 종전대로 착수 거부 — direct 는 "지금 고른 PRT" 를 도는 것이라 DOE 의 "기존 STP 재사용" 분기를 상속하지 않는다
15. [파생] **전환** direct 의 Journal 헤더·값은 **빈 배열**로 확정(미확인 전제 폴백) — "이 파일을 그대로 돌린다" 의 정확한 표현이고 통합 함수의 분기가 0 이 된다
16. [검증] **정리** (리뷰) 주석 압축 14곳(커밋 아카이브·기각 대안·중복 서술 제거, 근거 서술은 보존) · `launchWbpjJournal` 종료 로그의 run 수를 `openKeys()` → **실제 큐잉된 런치의 케이스 합계**로(동기 실패로 케이스가 닫히면 `for 0 run(s)` 로 나갔다) · `cancelAllRuns`·`finishStpPhase` 의 `"DOE ..."` 취소 로그 3건을 경로 중립 문구로(direct wbpj 배치도 같은 분기를 탄다) · launchId prefix `"doe:"` → `"wbpj:"`

### 검증 상태

Release 빌드 변경 4파일 경고 0 · `ctest` 8/8. **`launchId → 케이스 집합 귀속` AC 가 커버리지 밖**이다 — `launchWbpjJournal` 이 VTK 의존 클래스 안이라 순수 함수로 떼어내기 전에는 자동 검증이 불가하고, direct `.wbpj` 다건 수동 실행으로만 확인된다. 실환경 확인 5건(NX·ANSYS·Journal 데몬)이 잔여.

### 인접 커밋 — PR #275 (`6f5ba1e`, 티켓 없음)

[#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265) 와 [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 사이에 단독으로 랜딩했고, [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 착수 시 좌표 갱신 2건의 원인이 됐다.

- **Step 2 그룹 분할을 순수 함수로** — `launchWbpjJournal` 안의 지역 struct + 조립 루프를 `model/DashWbpjLaunchPlan.h` 의 `dashBuildWbpjLaunchGroups(cases, readyKeys)` 로 옮겼다. `StpCase` 도 같은 헤더로 나온다(`DashJobRunner.h` 는 `DashManager.h` 로 VTK 를 끌어와 테스트 타깃에 못 들어간다). **분할 규칙은 무변경** — 호출부는 `openKeys()` 를 STP Done 으로 걸러 넘기기만 한다
- **강제 종결에 motion kill 추가** — `cancelSolverTaskForKey` 가 Abaqus·ANSYS 핸들만 끊고 motion `QProcess` 는 두고 나갔다. 사용자 Stop(`cancelAllRuns`)은 kill 하지만 `abortBatch` 경유 종결에서는 **케이스가 장부에서 닫힌 뒤에도 프로세스가 계속 돌았다**. `waitForFinished` 는 하지 않는다 — 종료 핸들러가 같은 호출 스택에서 Failed 를 기록하면 호출부의 전이가 종료 단조성에 걸려 삼켜진다
- `tests/tst_wbpj_launch_plan` 5케이스 신설 — DOE 1그룹 · direct wbpj 별 1그룹 · 미착수 키 배제 · 같은 wbpj 다른 target 비병합 · 케이스 없는 키 무시

---

## [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) — 모핑 게이트 증명화 · 판정 단일화 · 종료 오케스트레이션

**계획 9항 / 계획 외 7항** (파생 4 · 검증 2 · 회귀 1) — [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 가 세운 게이트를 **질의형에서 증명형으로** 바꾸는 티켓이다. 28파일을 만지지만 순변경은 +357줄이고, 파일 수가 많은 이유는 증명 인자가 호출 사슬을 관통하기 때문이다.

1. [계획] **전환** `MorphingGate` 증명화 — `acquire()`·`Token` 삭제, `tryClaim() -> optional<Claim>` 이 **획득의 유일한 지점**. `Witness`/`Claim`/`Reservation` 3형과 원자 워드 1개(bit0 = Claim, bit1.. = Reservation)로 배치 축·워커 축을 **타입으로** 가른다. `busy()` 는 correctness 에서 빠지고 표시 전용으로 강등
2. [계획] **전환** DLL 실행 함수 4곳(`DashMorphingEngine::{RunVolumeMorphing,ExecuteMorphing}` · `DashMorphingDoeExecutor::{RunOneSample,ExecuteOneSample}`)이 `const Witness&` 를 첫 인자로 요구 — **게이트를 빠뜨린 코드가 컴파일되지 않는다.** `ExecuteOneSampleConditionOnly` 는 DLL 미경유라 제외. 단 `Witness` 생성자는 `protected` 이므로 막는 대상은 **누락**이고 파생을 통한 고의 위조는 막지 않는다(문서에 명기)
3. [계획] **전환** 진입점 1·1b·2·3·4 전부 `tryClaim()` 으로. `PrepareDoeMorphingBatch` 가 `DashMorphingBatchPrepared{claim, handle}`(이동 전용)을 돌려 **check-then-act 를 없앤다**
4. [계획] **전환** `batchActive()` 3항을 `m_morphJob != nullptr` → `!m_morphWorkerRes.expired()` — 취소 후 워커가 DLL 을 떠날 때까지 재착수가 거부된다. **신규 시그널 0개**로 생존 판정을 자원 시점으로 옮겼다
5. [계획] **전환** `beginBatch -> bool` 이 재진입을 판정하고 `batchBegun()` 을 낸다. 진입점별 인라인 가드 제거, `analysisStarted` 선행 방출을 `batchBegun` 중계로 이관 — **착수 신호가 판정보다 먼저 나가지 않는다**
6. [계획] **전환** `cancelSolverTaskForKey` → `releaseRunResources` 통합 — motion·FE-safe·Abaqus·ANSYS **4종**을 키 단위로 회수하고 **상태는 건드리지 않는다**. 진입 assert 가 "상태 확정이 먼저" 를 국소 검출하고, `cancelAllRuns` 는 컨테이너 키 합집합을 장부 착수 순서로 돌며 이 함수를 재사용한다
7. [계획] **신설** `controller/async/AppShutdown` — 종료 4단계(외부 프로세스 취소 · 데몬 종료 · 직렬 풀 배수 3s · 초과 시 flush + `_Exit`)의 **단일 소유자**(멱등). 데몬 회수를 `~DashManager()` 의 정적 소멸에서 `shutdownDaemons()` 로 이관하고 소멸자는 멱등 백스톱으로 축소 — [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) 15항이 증상만 막아 둔 "정적 소멸 구간을 아예 피한다" 를 실행한 것이다
8. [계획] **전환** `waitForAllSerialPools(int timeoutMs) -> bool`(두 풀이 상한 공유) · `main.cpp` 의 `aboutToQuit` 이 `AppShutdown::run()` 한 줄
9. [계획] **테스트** `tst_morphing_gate` 7케이스 재작성(배타성 · Reservation 잔류 · 경계 방출 · 이동/멱등 · 워커 마샬링) · `tst_worker_job` 를 Claim/Reservation 형상으로 갱신, 풀 배수 상한 인자화
10. [회귀] **신설** `rejectBeforeBegin` — 인라인 가드를 `beginBatch` 로 옮기자 **착수 전 이탈 경로가 노출**됐다. `generateInputCases`·`runDirectJobs` 는 `beginBatch` 이전에도 `abortBatch(...)` 를 부르는 지점이 **15곳** 있는데, 그 시점에 다른 배치가 살아 있으면 `abortBatch` 가 **남의 장부 open 키를 취소한다**. 종전에는 두 함수의 인라인 가드가 그 앞에서 막고 있었으므로 가드만 옮기면 회귀다. 착수 전 15곳을 `rejectBeforeBegin(reason)`(로그만, 장부·job 시그널 무접촉)으로 갈랐고 `abortBatch` 헤더 주석에 "`beginBatch` 성공 이후에만" 을 계약으로 박았다
11. [파생] **수리** 진입점 5 의 `busy()` 검사 삭제 — `performMorphingAndExport` 가 **자기 Claim 에 자기가 거부되던** 구멍
12. [파생] **수리** `DashModelRunnerWidget` 의 틀린 오류 문구(reference file / part name)를 실제 사유와 분기
13. [파생] **축소** 진입점 5 워커화 미실행(티켓이 미리 승인한 대체안) — `DashOptimizer::performMorphing`·`DashModelRunner::performMorphing` 이 모핑 호출 전에 **GUI 소유 `DashHandlePickingInteraction` 에 VTP 핸들을 싣고** `DashManager` 를 직접 만진다. 워커화하려면 배치 축의 `PrepareBatch`/`RunOneSample` 분리를 이 두 경로에 새로 만들어야 하고 그건 D5(GUI 소유 객체) 때문에 별건이다. Claim 을 루프/함수 스코프로 들고 동기 유지 → 루프 시작 거부(iteration 0건) · 자기 거부 없음 · 역순서 창 폐쇄는 충족되고, **"모핑 구간 `processEvents()` 0건" 은 미충족**(`DashOptimizerWidget.cpp` 2곳 잔존). `ThreadingContract` 7절에 "Claim 구간의 `processEvents()` 는 재진입을 Claim 이 막는다" 를 명시
14. [파생] **정리** 좌표 갱신 — PR #275 가 `cancelSolverTaskForKey` 에 motion kill 을 이미 넣어 as-is 는 "Abaqus·ANSYS 2종" 이 아니라 **3종**이었고 남은 누락은 FE-safe 1종이었다. `cancelAllRuns` 쪽 motion 처리(take-then-kill + `waitForFinished(3000)`)를 키 경로에도 통일했고, 안전 근거는 진입 assert 가 보증하는 "상태 확정이 먼저" 다 — 그래야 `waitForFinished` 가 펌프하는 CrashExit→Failed 가 종료 단조성에 막힌다
15. [검증] **수리** (`ticket-review` 8건 중 6 적용) `Claim::reserve()` 에 `Q_ASSERT(m_held)`(놓은 Claim 이 경계 방출 없이 워드를 올리는 구멍) · `runNextMorphSample` 에 `Q_ASSERT(m_morphClaim)` + 불변식 명시 · `AppShutdown` 의 `_Exit(0)` → **`_Exit(1)`**(강제 종결을 성공 코드로 보고하지 않는다) · 호출부 0건인 `Claim::held()` 삭제 · `cancelAllRuns` 순회를 `openKeys()`(착수 순서) 우선 → 장부 밖 잔여 키는 사전순 고정(`QSet` 무순서 순회 제거) · 로그 문구 `Cancelled N running case(s)` → `Swept N case(s) for cancellation`(N 은 키 개수이지 실제 취소 건수가 아니다)
16. [검증] **정리** 신규·수정 주석 압축(근거 보존, 티켓 본문과의 중복 서술만 제거 — 605 → 571 insertions)

### 남은 창 3건 (문서화하고 수용)

- **`beginBatch`(장부)가 `tryClaim`(게이트)보다 먼저 온다** — 게이트가 이미 잡혀 있으면 장부를 세운 뒤 전 케이스가 Failed 로 접힌다. 오늘은 `refreshRunControls` 가 `busy()` 를 보고 DOE Start 를 잠그므로 도달하지 않는다.
- **`abortBatch` 의 마지막 키**는 `setStageState` → `finishBatch` 가 그 키의 자원 회수보다 먼저 난다. `QProcess::waitForFinished` 가 GUI 이벤트를 펌프하지 않아 실제 도달 경로가 없어 2-pass 로 바꾸지 않았다.
- **`busyChanged` stale 방출**(워커의 큐된 `notify(false)` 가 새 `tryClaim()` 의 `notify(true)` 뒤에 도착) 은 `acquire()` 시절과 동일한 구조로 기존 동작이며 이번 개정이 악화시키지 않았다.

### 검증 상태

`ctest` **9/9**(Debug — assert 활성이므로 신규 `Q_ASSERT` 3종이 기존 의미론을 깨지 않음이 확인된다) · Release 앱 빌드 클린. 정적 대조: `MorphingGate::acquire()`/`Token`/`cancelSolverTaskForKey` 정의·호출 **0건**, `busy()` 잔존 소비자는 표시 목적 3곳뿐, `abortBatch`(11곳)/`rejectBeforeBegin`(12곳) 배치가 `beginBatch` 호출부 6곳 경계와 전 경로 정합. **실기 미확인 2항목** — 종료 순서(고아 데몬 0 · 타임아웃 내 종료 · 사유 로그 flush) · `.vtu` 결과 정합.

또 **티켓의 위험 항목 1건이 성립하지 않는 것으로 판정됐다** — `DashJobRunner::createRunsFolders`/`DashAnalysisLauncher::createRunsFolders` 를 "`beginBatch` 앞 `processEvents` 재진입원" 으로 지목했으나 실은 호출부 0건인 죽은 함수였다. 삭제는 [#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279) 소유.

---

## [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) W10-f-1 — RST/KPI 파싱 워커화 · preprocessor 직렬 풀·게이트 신설

**계획 19항 / 계획 외 13항** (검증 5 · 회귀 4 · 선재 2 · 파생 2) — 브랜치 단일 PR 최대 규모(21파일 +2576/-1200)이고 **model 계층 `processEvents` 를 0 으로 만든 티켓**이다. Phase 0(동기 리팩터, 동작 무변경)을 앞에 세워 선결 조건 6건을 워커화 이전에 닫은 것이 이 티켓 구조의 핵심이다.

> **설계 검토가 초안의 최대 결함을 뒤집은 뒤 착수했다.** 초안은 배제 스팬을 "워커 1회 실행" 으로 잡았으나 실제 단위는 **GUI 진입 1회**이고 그 1회가 Job 여러 개로 펼쳐진다. 반례 3건이 코드에 실재했고 그중 "Job k 완료 \~ k+1 착수 사이의 틈으로 프리뷰가 들어와 인스턴스를 오염시킨다" 는 **틀린 숫자가 XML 에 기록**되는 계급이었다. 확정 8건은 착수 전에 본문에 반영됐다.

### Phase 0 — 동기 리팩터 (`f230e8f`, pE 22 무변화)

1. [계획] **전환** `DashResultProcessor::ProcessContext` 참조 멤버 11개 → 값 + 경로 선해석(`getProjectRootDir` 를 GUI 가 끝내 `processSingleSample` 의 싱글턴 접촉 2건 제거, 출력 디렉터리 해석을 요청 루프 밖으로 — 루프 불변). **복사는 GUI 스레드에서** 일어난다 — Qt 암시적 공유 컨테이너를 워커가 복사하면 GUI 변경과 경합한다
2. [계획] **전환** `m_preprocessor` 를 `shared_ptr` 로 승격 — 소유자가 런타임에 파괴된다(세트 삭제 · 프로젝트 정리). task 가 값으로 캡처해야 **수명이 게이트 정확성에서 독립**한다
3. [계획] **전환** 위젯의 `processResults` 3연속 호출 → `processResultsGroups` 단일 제출. 배제 단위가 GUI 진입 1회라 제출이 쪼개지면 **2·3회차가 게이트에 걸려 조용히 유실**된다
4. [계획] **전환** 재진입 가드 `m_isProcessing` 을 한 곳으로 모으고 **KPI 경로까지** 덮는다 — 종전 KPI 분기가 가드를 켜는 지점보다 앞에서 return 해 KPI 실행 중에는 가드가 없었다
5. [계획] **신설** `ProcessingScope` RAII — 결과 처리·KPI 5종에 진행 통지 신설(종전 0건. 오늘은 pE 펌프만으로 UI 가 살아 있었다)
6. [선재] **수리** `onAnalysisFileSelected` 의 조기 return 4곳이 통지를 건너뛰어 **스피너가 영구 잔류**하던 것 — 5항의 RAII 가 함께 닫는다
7. [계획] **전환** `processResultsWithKPI` 의 시그널 왕복 수집 → 모델 소유 `PendingBatch`. 종전은 스택 지역을 참조 캡처한 람다를 `processFinished` 에 걸고 **sender 필터 없이 전역 수집**했으므로, 비동기가 되면 스코프가 먼저 끝나 댕글링이 된다

### Phase 1 — 배제 기제 3종 + 파일럿 (`121cacb`, pE 22 → 21)

8. [계획] **신설** `DashPools::preprocessorSerialPool()` — 3번째 직렬 풀. `waitForAllSerialPools` 가 **세 풀이 상한 하나를 나눠 쓰게** 했다 — 풀마다 상한을 주면 최악 대기가 풀 수만큼 늘어난다
9. [계획] **신설** `controller/async/PreprocessorGate` — `MorphingGate` 동형 3형(`Witness`/`Claim`/`Reservation`/`tryClaim()`, `busy()` 표시 전용). 수명은 **GUI 진입 1회**다. 형태를 맞춘 이유는 세 게이트가 선 뒤 공용 기제로 추출하는 경로를 열어 두기 위해서였고, 그 판단은 이후 "3벌 유지" 로 뒤집혔다(아래)
10. [계획] **전환** `WorkerJob::Task` 에 `ProgressSink` 추가 — `WorkerProgressRelay` 가 `shared_ptr` + `deleteLater` 로 살아 **task 가 Job 보다 오래 살아도 통지 경로가 댕글링하지 않는다**
11. [계획] **전환** DPF 진입점 8곳 전수 증명 배선 — `ensurePreprocessor(const Witness&, ext)` 가 DPF 사용의 관문이라 **게이트를 빠뜨린 진입점은 컴파일되지 않는다**. 판정 자체는 종전과 동일
12. [계획] **전환** 공개/내부 2층 분리 — 공개 진입(`processResultsGroups`·`processResultsWithKPI`)이 토큰을 잡고 내부 호출(`runResultGroup`·KPI 5종·`DashResponseInitializer::initialize`)은 증명을 인자로 받아 재획득하지 않는다. `processResultsWithKPI` 의 일반 요청 처리도 공개 진입 → 내부 호출로 바꿨다 — **공개를 부르면 자기가 쥔 토큰에 자기가 걸린다**([#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 11항과 같은 구멍)
13. [계획] **전환** 파일럿 `onAnalysisFileSelected` 워커화 — 무거운 절반(DPF `GetAnalysisInfo` · run × pattern 존재 확인)을 Job 1개로. 경로 해석과 runs 폴더 열거는 GUI 에 남긴다(디렉터리 열거는 메타데이터만 읽어 싸다). **확장자 사전 스캔으로 solver 를 정하고 GUI 가 인스턴스를 만든다** — 래퍼 생성자가 싱글턴을 만져 워커에서 만들 수 없다. `.rst` 가 없으면 초기화도 하지 않는다(종전 동작 보존 — Abaqus 경로 미설정 시 불필요한 오류 팝업 방지). task 는 `this` 미캡처, 결과는 `shared_ptr<AnalysisScanPayload>`, 취소 폴링은 run 루프 경계 — **이 경계가 per-run 전환 시 Job 경계가 된다**
14. [계획] **신설** 위젯이 `busyChanged` 를 구독해 정적 컨트롤을 사전 비활성 · `AppShutdown::isShuttingDown()` 공개(종료 중 신규 Job 착수 거부 — 종료 정책 ⑵)

### Phase 2 — `processResults` + `DashResultProcessor` (`f75aa4a`, pE 21 → 7)

15. [계획] **전환** 요청 단위 Job 연쇄 — 요청 N개 → Job N개. **샘플 루프는 task 내부 존치**(결과 처리는 샘플별 산출물이 없고 장부 칸도 없어 per-sample 로 쪼개면 얻는 것 없이 신설 부담만 남는다). 토큰은 공개 진입 1개가 사슬 전체를 살고 **마지막 완료 슬롯**이 놓는다. 스냅샷은 **사슬 착수 시 1회** — Job 마다 다시 뜨면 그 사이 `loadRstDataFromTable` 이 갈아엎는 6개 필드가 중간에 섞인다. `DashResultProcessor` **8 → 0** · `processResults` 소유 6곳 소멸
16. [계획] **전환** 데이터 흐름 분리 — 워커는 DOM 조립(`processSamples`·`appendSample`·`writeModelInfoToXml`), GUI 완료 슬롯이 `doc.save` + `processFinished`. **워커가 디스크에 쓰지 않는 것이 강제 종료 시 반쯤 쓰인 XML 이 남지 않는 근거**다. `payload->doc` 는 워커가 완전히 놓은 뒤 GUI 가 잡는다 — `QDomDocument` 는 암시적 공유이고 스레드 안전하지 않아 중간 사본을 만들지 않는다. `logCallback` 의 `emit logMessage` + `processEvents` 결합을 해체해 `ProgressSink` 로 재정의
17. [계획] **신설** 사슬 실패 규약(현행 `continue` 계승) — k번째 실패는 해당 요청분만 `errorOccurred` 하고 나머지 Job 은 계속, `allProcessFinished` 는 성공분만 담아 사슬 종료 시 1회, 취소 시 미착수분은 착수하지 않는다. 증명·통지 해제는 `finishResultChain()` **한 곳**이라 예외 경로에서도 스피너가 잔류하지 않는다
18. [파생] **정리** 요청과 무관한 루프 불변량 이동 — 단일 파일 모드의 입력 경로 탐색을 요청 루프 밖으로(실패 통지가 요청 수만큼 → 1회) · step/substep 해석 결과를 계획에 실어 워커가 재파싱하지 않게(`m_modalDefs`·`m_solverType` 을 아는 것은 GUI 뿐이다)
19. [검증] **조정** `allProcessFinished` 축소가 계획보다 **앞당겨졌다** — 티켓은 3 → 1회를 Phase 3·4 에 배치했으나 **사슬 종결이 곧 수집기 종결**이라 Phase 2 에서 3 → 2회로 자연 감소했다

### Phase 3 — KPI 동형 4종 + 사슬 일반화 (`6def6dc`, pE 7 → 3)

20. [검증] **설계 변경** 사슬을 **클로저 단위로 일반화** — 티켓 Phase 3 은 "Phase 2 골격 4회 적용" 이었으나 그러면 착수·저장·종결 기제가 **5벌**이 된다. `ResultChain` 의 칸을 `ChainUnit{fileName, outputPath, savedLog, codec, build}` 로 바꿔 `build` 클로저 1개로 일반 결과 처리와 KPI 5종이 같은 사슬을 쓴다. Phase 2 가 세운 요청 전용 타입(`PlannedResultRequest` + `ProcessContext` 멤버)을 대체한다. 스냅샷은 각 칸의 캡처에 실린다 — Qt 컨테이너 사본은 refcount 증가라 칸마다 떠도 싸고, 복사는 여전히 GUI 스레드에서 일어난다
21. [회귀] **차단** 출력 코덱 — 일반 결과 처리만 `stream.setCodec("UTF-8")` 을 명시했고 KPI 5종은 `QTextStream` 기본값(로케일 코덱)이었다. 사슬 저장을 하나로 합치면 **KPI 산출물의 인코딩과 XML 선언이 바뀐다**(바이트 동등 파괴). 코덱을 칸 속성으로 두어 경로별 종전 값을 보존했다 — 일반화가 만들 수 있었던 조용한 산출물 변경을 통합 시점에 잡은 것이다
22. [계획] **전환** KPI 동형 4종(SideForce · CriticalBucklingLoad · MaxPEEQ · MinFatigueLife) 워커화 — per-run 루프(파일 해석 → `SetInputFilePathes` → 규칙 계산 → DOM append)를 워커로. 골격 중복 제거(1,177줄)는 범위 밖이라 네 함수의 형태는 그대로 두고 워커화가 강제하는 것만 바꿨다. **task 캡처 목록을 명시해 멤버 참조가 남으면 컴파일이 깨지게** 했다. 취소 폴링은 run 루프 경계. KPI 경로에도 토큰이 걸려 실행 중 프리뷰가 배제된다 — **오늘 가드가 없던 경로라 신규 동작**이다
23. [계획] **전환** 프리뷰 복원(`SetInputFilePathes(m_lastLoadedInputFiles)`)을 **사슬 종료 1회**로 이동 — 칸마다 되돌리면 DPF 로드가 헛돈다. **Claim 을 놓기 전에** 수행한다(놓은 뒤에 만지면 게이트 밖에서 DPF 를 만지는 것이 된다)

### Phase 4 — `processModalFrequencyKPI` (`dea6cfc`, pE 3 → **0**)

24. [계획] **전환** `mode × stat` 중첩 출력을 출력 단위 사슬로 펼쳤다 → **model 계층 `processEvents` 0 달성**(`DashDataProcessor` 14 → 0 · `DashResultProcessor` 8 → 0). 토큰 1개가 칸 사이의 틈까지 덮는다 — 워커 스코프였다면 그 틈으로 프리뷰가 들어와 다음 칸이 엉뚱한 파일을 읽었다
25. [계획] **전환** `allProcessFinished` 직접 방출을 사슬 규약에 합류 — **방출 지점이 `closeBatch()` 한 곳**이 되어 최대 3회 → **1회**. 소비 위젯이 방출마다 팝업을 띄우므로 사용자에게 보이는 변화다(팝업 3개 → 1개) — 티켓이 선언한 **의도적 UX 변경**
26. [계획] **신설** ModalFreq 프리뷰 복원 — 5종 중 이 함수에만 없었다. `mode_lstp*.rst` 단독 로드 상태로 끝나면 이후 프리뷰가 엉뚱한 파일을 본다. "이동" 이 아니라 신설이며 동작 변경이다

### 보강 · 자체 리뷰 (`4f3ee41`·`6b4c64f` + 리뷰 커밋)

27. [회귀] **수리** 위젯 enabled 복원이 앱 규칙을 덮었다 — 두 갈래다. ⑴ 동적 3종(`analysisFileComboBox`·`loadStepTree`·`nameList`)이 사전 비활성 대상에서 빠져 있어 **사슬 도중 콤보·트리가 이동한 뒤 거부되어 표시와 실제가 어긋난다** ⑵ GUI 동기 진입점은 claim 획득·해제가 같은 콜스택이고 그 사이에 모델이 `keysExtracted`·`namesUpdated` 를 방출하므로, 무조건 활성 복원이 그 시점의 앱 규칙을 덮어 **Name 목록이 채워진 채 비활성으로 남아 Add Result 로 진행이 불가**했다. `setDynamicEnabled` 신설 + 동적 3종의 `setEnabled` 호출부 9곳 전부 경유, busy 진입 시점의 enabled 를 적어 두고 그대로 되돌린다. 이로써 GUI 진입점 5곳 전부 사전 비활성
28. [회귀] **수리** 소멸자가 공유 DPF 인스턴스에 무조건 `Clear()` 했다 — 소유자는 사슬 중에도 파괴되고(세트 삭제 · 프로젝트 정리) `~WorkerJob` 은 취소도 대기도 하지 않는다. `use_count() == 1` 일 때만 `Clear()`. 스코프·증명은 본문에서 놓아 멤버 소멸 단계의 시그널 방출을 없앴다
29. [회귀] **수리** 순서·수명 3건 — `finishResultChain` 이 모달 완료 팝업을 스코프·claim 해제보다 앞세워 **팝업 뒤로 스피너가 잔류**했다(`onAnalysisScanFinished` 와 같은 순서로) · `WorkerJob::detachRelay` 신설으로 **터미널 이후의 sink 통지 폐기**(`setState` 뒤 호출) · 종료 확인을 `tryClaim()` 앞으로(진입점 3곳)
30. [선재] **수리** `analysisFilesFound` 의 첫 `addItem` 이 `currentIndex` 를 0 으로 올려 **고르지도 않은 Analysis Type 의 스캔을 착수**시켰다. 스캔이 비동기가 되면서 그 `datasetReady` 가 `setCurrentIndex(-1)` 정리보다 늦게 도착해 **콤보 미선택인데 테이블이 남는다** → `blockSignals`. 선재 결함이지만 비동기화가 증상을 만들었다
31. [파생] **정리** `advanceResultChain` 착수 불변식을 주석이 아니라 단정으로(증명 없이 불리면 `reserve()` 가 성립하지 않는다) · KPI 5종의 지역 `ProcessingScope` 제거(사슬 통지가 `processResultsWithKPI` 에 있고, 계획만 하고 즉시 반환하는 함수에서 스코프를 열고 닫는 것은 의미가 없다) · ModalFreq 산출물별 완료 로그 복구 · dead 조건·들여쓰기 정리
32. [계획] **문서** `docs/ThreadingContract.md` 7절 개정 2라운드 — ⑴ 세 풀 · 풀과 게이트의 역할 분리("워커로 올라가지 않는 GUI 동기 호출이 남는 서브시스템은 풀만으로 등급 2 배제가 성립하지 않는다") · 배제 단위가 **GUI 진입 1회** · 워커 경계 규약 5항 · 종료 정책 3항 ⑵ (보강) 디스크 쓰기를 **전역 금지에서 축 한정으로 강등**하고 완결 판정은 워커 반환값 소유로 · 거부 UX 키 규칙 · 게이트 3벌 유지 결정 · 전역 규칙 3(풀 추가는 드레인 예산 재판정 대상이 아니다) · **"모핑 배치 중 결과 처리 정상 완료" 가 풀 서로소가 아니라 `isRunKeyDone` 의 Done 필터 위에 선다**는 전제 명시
33. [검증] **테스트 신설** `tests/tst_preprocessor_gate` 7종 — 배타성 · 취소 비대칭 · **사슬이 Job 여러 개를 하나의 Claim 으로 덮음** · 이동/멱등 · 워커 해제의 GUI 마샬링. 발급 경로가 타입으로 닫혀 있음은 **`static_assert` 5개**로 봉인했다. `tst_worker_job` +2종(sink 마샬링 · 취소 폴링이 샘플 경계에서 걸림) + 3풀 드레인
34. [검증] **조사** 워커 경계 실측 — 워커에서 도달하는 코드에 싱글턴·GUI 접촉 **0건** 확인(`LGE_SpringRule`·`ILJIN_TensionlinkRule`·`LGE_BoreBossComponentRule`·`DashResultXmlWriter`·`DashFileLocator`·`DashUtils` 전부 `Instance()`/`Mgr()`/`QApplication`/`QWidget` 미접촉). `DashResponseInitializer` 만 `Instance()` 를 만지고 그것은 설계대로 GUI 에 남았다
35. [검증] **조사** 종료 정책 ⑶ — `DashOptiPreprocessor 1.2.2` 에 **협조적 취소·라이선스 반납 표면이 없다**(cancel·abort·license 계열 0건, 플러그인 해제는 소멸자에만). `_Exit` 상시화 수용이 유일한 답이고 **그 범위를 알고 수용한다**는 것이 결론이다

### 검증 상태

`BUILD_TARGET=Dev` 전 타깃 컴파일 통과(Phase 마다 1회 + 최종 full build) · **`ctest` 10/10**. 정적 확인: `grep processEvents model/` 잔여 3곳 전부 `DashJobRunner` · `emit allProcessFinished` 1곳.

**수동 검증 4건 미실시** — 출력 XML 바이트 동등(`fc /b`)은 **픽스처 프로젝트(고객사 데이터)가 레포에 없어 기준선 캡처 자체가 불가**하다(골든 기준선은 `b579bcf` 체크아웃으로 사후 캡처 가능) · `LGE_CompSpring`(SideForce·ModalFreq)·`ILJIN_TensionLink`(3종) 런타임 실행 · 모핑 배치 실행 중 결과 처리 정상 완료 / 프리뷰 비활성 · 방출 팝업 1회.

**최대 잔여 리스크는 VTK 전역 상태**다 — `DashResultXmlWriter` 가 워커에서 `GetFieldOutputVtk`/`GetGeometryVtk` 로 VTK 객체를 만든다. Job-local 이라 GUI 로 넘어가지 않지만 VTK 전역 상태(출력 윈도우 등) 접촉 여부는 미확인이고, 런타임 검증에서 가장 먼저 볼 지점이다.

---

## 계획 대비 실제 — 항목 분류

위 12개 절의 195항을 출처별로 집계한 것. **계획 외 89항이 이 문서의 존재 이유**이고, 티켓 checkbox 에는 이 중 [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207) 의 2건(Phase 5·6 사후 추가)만 드러난다 — 나머지 87항은 기존 Phase 안에서 처리돼 계획서만 보면 없는 일이 된다.

| 티켓 | 항목 | 계획 | 계획 외 | 선재 | 회귀 | 검증 | 파생 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207) W6-1 엔진 | 13 | 8 | 5 | 1 | 3 | — | 1 |
| [#208](https://github.com/NumeRealWorks/DashOpti_GUI/issues/208) W6-2 model 3종 | 14 | 4 | **10** | 1 | **5** | 2 | 2 |
| [#209](https://github.com/NumeRealWorks/DashOpti_GUI/issues/209) W6-3 view 2곳 | 13 | 8 | 5 | — | 1 | 1 | 3 |
| [#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) W10-a DOE | 13 | 10 | 3 | — | — | 2 | 1 |
| [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) W10-c 데몬 기동 | 15 | 10 | 5 | — | 3 | 1 | 1 |
| [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) W10-d 워커 게이트 | 19 | 11 | **8** | — | **6** | 1 | 1 |
| **1차 소계** | **87** | **51** | **36** | **2** | **18** | **7** | **9** |
| [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) W10-b per-sample | 22 | 8 | **14** | 2 | 5 | **5** | 2 |
| [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) 이벤트·상태 3축 | 18 | 8 | 10 | — | 4 | — | **6** |
| [#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264) 장부 밖 경로 | 20 | 10 | 10 | — | 4 | 3 | 3 |
| [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) W10-e 워커 인프라 | 16 | 10 | 6 | — | **—** | 3 | 3 |
| [#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265) 솔버 제출 통합 | 16 | 10 | 6 | 1 | **—** | 1 | 4 |
| [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 게이트 증명화 | 16 | 9 | 7 | — | 1 | 2 | 4 |
| **2차 소계** | **108** | **55** | **53** | **3** | **14** | **14** | **22** |
| [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) W10-f-1 preprocessor | 32 | **19** | 13 | 2 | 4 | 5 | 2 |
| **3차 소계** | **32** | **19** | **13** | **2** | **4** | **5** | **2** |
| **합계** | **227** | **125** | **102** | **7** | **36** | **26** | **33** |

- **[#208](https://github.com/NumeRealWorks/DashOpti_GUI/issues/208) 만 계획 외가 계획분의 2배** — 위임 3종이 공유 `QProcess` 를 지우면서 Qt 가 대신 지켜 주던 보호가 한꺼번에 사라진 결과다(회귀 5건이 전부 이 계급). 계획서가 Phase 3개 · Notes 위주였던 것과도 맞물린다.
- **계획서 상세도가 계획 외 비율을 결정한다** — [#209](https://github.com/NumeRealWorks/DashOpti_GUI/issues/209) 는 항목 수가 [#208](https://github.com/NumeRealWorks/DashOpti_GUI/issues/208) 과 같은데 계획분이 2배다. D1~D7 결정으로 선재 결함(fit 버튼 고착)·소멸자 누락까지 미리 적어 뒀기 때문이고, 남은 회귀 1건도 전환분이 아니라 신설 기능(`cancelAllRunning`) 쪽이다. [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) 도 같은 계급 — 소비처 18곳 전수표를 계획서가 확정해 계획분이 10항이고 계획 외 3건은 전부 새로 만든 회귀다.
- **결함 수리 20항(선재 2 + 회귀 18) 중 18항은 이번 작업이 만든 것** — 모두 같은 브랜치 안에서 발견·수리돼 잔존하지 않지만, 발견 경로가 대부분 단위 테스트가 아니라 실 exe·실 GUI·코드 리뷰였다. 전환의 실익은 결함 제거가 아니라 구조이고, 그 대가가 이 18항이다.
- **회귀 계급이 티켓마다 다른 얼굴을 한다** — [#208](https://github.com/NumeRealWorks/DashOpti_GUI/issues/208) 은 "Qt 가 지켜 주던 암묵 보호의 소멸", [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) 는 "동기 계약을 지우자 드러난 무음 실패 경로", [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) 은 "공유를 끊자 그 공유의 부작용에 기대던 것"이다. 공통점은 셋 다 **제거한 것이 무엇을 겸하고 있었는지**를 미리 세지 않아 생겼다는 것.
- **[#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) 은 결함 수리 0항** — 계획 외 3항이 리뷰 반영 2 + 주석 정리 1 이다. 부록 상 ✅ 로 바뀐 것은 8-4 의 1건뿐이지만 계획 대비 이탈이 가장 작다.
- 이 195항과 **부록 37지점은 분모가 다르다** — 부록에 대응 행이 생기는 것은 전환·제거 항목뿐이고, 신설·테스트·결함 수리는 "동기 → 비동기 전환 지점" 목록에 애초에 자리가 없다. 두 집계를 합산하거나 비율로 비교하지 않는다.

### 2차 파동에서 달라진 것

- **계획 외 비율이 41% → 49% 로 올랐는데 결함 수리 비율은 절반으로 떨어졌다.** 1차 계획 외 36항 중 결함 수리(선재+회귀)가 20항(56%)이었고, 2차 53항 중에서는 17항(32%)이다. 늘어난 것은 **검증 7→14**(테스트·계측·리뷰 반영)과 **파생 9→22**(이름·중복 정리)다. 전환의 성격이 "동기 계약을 지우는 일" 에서 "이미 세운 계약을 한 벌로 모으는 일" 로 옮겨간 결과이고, 후자는 결함보다 중복을 만든다.
- **[#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214)·[#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265) 는 회귀 0항**이다. 브랜치 전체에서 이 둘뿐이고, 두 티켓의 공통점은 **선행이 자리를 완성해 둔 상태에서 착수했다**는 것이다. [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 는 [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213)(진입 경계)·[#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260)(2표면·값 결과)·[#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251)·[#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264)(장부·단일 종결) 위에, [#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265) 는 [#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264)(장부화·`terminalStage`) 위에 얹혔다. 반대로 [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) 은 계획 외 14항으로 브랜치 최대인데, 선행 없이 동기 루프를 처음 펼친 티켓이다.
- **파생 22항의 절반이 이관 후 이름·중복 정리**([#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) 6항 · [#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265) 4항)다. [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) 은 인코딩을 뒤집으면서 `StpBatch`→`WbpjBatch`·`advance`→`runNextStpCase` 를 **3라운드에 걸쳐** 고쳤다 — 이관 자체는 한 번이지만 "이관 후 이름이 사실과 어긋난 것" 을 찾는 데 독립 검토 3대가 동원됐다. 대규모 이관에서 이름 정리를 같은 PR 에 넣지 않으면 어긋난 이름이 그대로 굳는다.
- **취소 경로가 리뷰 전담 구역이다.** 2차에서 `ticket-review`·독립 에이전트 검토가 잡은 것 중 [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) M3(취소가 실패로 뒤집힘) · [#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264) 18항(취소 중 Start 조기 복구) · [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 10항(남의 장부 취소)은 셋 다 **취소 경로**의 결함이다. 취소는 단위 테스트가 덮기 가장 어려운 경로이고(트리거가 GUI, 대상이 외부 프로세스·스레드, 판정이 "그 뒤에 무엇이 오지 않는가"), 실제로 셋 다 코드 리뷰에서만 잡혔다.

### 3차 파동에서 달라진 것

- **계획분 비율이 다시 올랐다** — 1차 59% → 2차 51% → 3차 **59%**. 이유는 [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 이 착수 **전에** 독립 검토 3건으로 초안의 결함 8건을 확정하고 본문을 재작성했기 때문이다. 특히 "배제 단위 = GUI 진입 1회" 판정과 선결 조건 6건이 계획서에 들어간 덕에 Phase 0 전량(7항)이 계획분이 됐다. [#209](https://github.com/NumeRealWorks/DashOpti_GUI/issues/209)·[#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) 에서 나온 "계획 외 비율은 계획 단계 조사 깊이의 함수" 가 세 번째로 확인된 셈이다.
- **동기 리팩터 Phase 를 앞에 세우는 것이 값을 했다.** Phase 0 은 pE 를 하나도 줄이지 않고(22 무변화) 동작도 바꾸지 않지만, 게이트 자기충돌(3연속 제출)·가드 증발(KPI 경로)·무피드백 구간(진행 통지 0건)·워커 진입 불가(참조 멤버 11개 · raw 포인터 수명)를 **워커화 이전 상태에서** 닫았다. 회귀 위험이 0 이라 리뷰만으로 검증되고, 그 뒤 Phase 1\~4 의 회귀 4건은 전부 "워커화 자체가 만든 것" 으로 좁혀진다.
- **일반화가 조용한 산출물 변경을 만들 수 있었다.** Phase 3 의 사슬 통합(21항)에서 KPI 5종이 `QTextStream` 기본 코덱을 쓰고 있던 것이 드러났다 — 저장 경로를 합치는 순간 산출 XML 의 인코딩과 선언이 바뀐다. 코덱을 칸 속성으로 뽑아 경로별 종전 값을 보존했다. **"같은 일을 하는 코드 N벌을 1벌로 합친다" 는 변경은 N벌이 실제로 같은 일을 했는지부터 확인해야 한다** — [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) F1(같은 뜻의 판정으로 교체)과 같은 계급이다.
- **비동기화가 선재 결함을 증상으로 바꾼다.** 30항 — `analysisFilesFound` 의 첫 `addItem` 이 미선택 Analysis Type 의 스캔을 착수시키는 것은 선재였지만, 스캔이 동기이던 동안에는 `setCurrentIndex(-1)` 정리가 항상 뒤에 왔다. 비동기가 되자 순서가 뒤집혀 **콤보 미선택인데 테이블이 남는** 상태가 생겼다. 6항(스피너 잔류)도 같은 계급이다.
- **enabled 복원은 스냅샷-복원으로 풀어야 한다.** 27항 — 게이트 busy 창을 위젯 비활성으로 표시할 때 "끝나면 전부 활성" 은 그 창 **안에서** 바뀐 앱 규칙을 덮는다. GUI 동기 진입점은 획득·해제가 같은 콜스택인데 그 사이에 모델이 시그널을 방출하므로 창 내부에 상태 변화가 실재한다. 진입 시점의 enabled 를 적어 두고 그대로 되돌리는 것이 정해다.
- **형이 재사용된다는 것이 처음 확인됐다.** [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 가 세운 `Witness`/`Claim`/`Reservation` 3형과 `tryClaim()` 단일 획득이 두 번째 서브시스템에 **기계적으로 복제됐고**, 그 과정에서 정확성 결함이 하나도 나오지 않았다(게이트 관련 회귀 0). `WorkerJob` 은 확장이 필요했지만(`ProgressSink`) 그것도 계획분이다. 반대로 재사용되지 않은 것은 **거부 UX** 다 — `MorphingGate` 는 키가 없어 사전 비활성이 정해인데 여기서는 동적 enabled 3종 때문에 스냅샷-복원이 추가로 필요했고, 그 차이가 회귀 2건(27항)을 냈다.

---

## 검증 자산 (현재 상태)

| 테스트 | ctest 등록 | 봉인 대상 |
|---|:---:|---|
| `tst_line_assembler` | O | 부분 수신 라인 조립, UTF-8 read 경계, 개행 없는 마지막 줄 |
| `tst_job_state` | O | 상태 전이, 터미널 잠금(취소 뒤 늦은 완료의 이중 방송 0) |
| `tst_process_runtime` | O | 취소 1회 마감, 기동 실패 2갈래, workingDirectory, `killOrphans` 동명 방관자 생존 · **([#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212))** 미기동 enqueue 순서, ready-timeout drain, Starting 중 stop 뒤 가짜 died 0, 재기동·start idempotent, pre-launch 통지, 실패 슬롯 재-enqueue 하 stop 관철 |
| `tst_thread_affinity` | O | **([#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213))** 실제 `QThread` 에서 메인 판정 false — 가드 6곳이 조용히 무력화되는 것을 차단 |
| `tst_batch_ledger` | O | **([#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) 9 → [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) +1 → [#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264) +4 → [#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265) +1)** 스테이지 전이·통지 매핑·`terminalStage` 유도(1·2·3칸 + 터미널 하향) · 1칸 장부의 상위 stage 전이 폐기 · 전건 Failed 후 `active()` false · 중복 통지 |
| `tst_direct_job_plan` | O | **([#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264) 6 → [#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265) 갱신)** direct 파일→키·분류 판정 — 확장자 분류·착수 순서 · `.wbpj` prt 키 규칙과 폴백 · 중복·빈 키 제외 · 다건 착수 · 혼합 선택 거부 |
| `tst_worker_job` | O | **([#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 9 → [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274)·[#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 갱신)** 성공 페이로드·실패 사유·예외→Failed · 취소 즉시성 + 늦은 완료 폐기 · 직렬 풀 동시성 1 · **task 실행 중 메인 이벤트 루프 생존** · 취소 2축 순서 · **3풀** 배수 완결성 · `ProgressSink` 마샬링 · 취소 폴링이 샘플 경계에서 걸림 |
| `tst_morphing_gate` | O | **([#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 6 → [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 7 재작성)** 획득 배타성 · Reservation 이 Claim 보다 오래 살아 다음 Claim 을 막음 · `busyChanged` 는 0↔1 경계에서만 · 이동/멱등 · 워커 스레드 해제의 GUI 마샬링 |
| `tst_preprocessor_gate` | O | **([#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 7 신설)** 배타성 · 취소 비대칭 · **사슬이 Job 여러 개를 하나의 Claim 으로 덮음**(배제 단위가 GUI 진입 1회라는 판정의 봉인) · 이동/멱등 · 워커 해제 마샬링. 발급 경로가 타입으로 닫혀 있음은 **`static_assert` 5개** |
| `tst_wbpj_launch_plan` | O | **(PR #275)** Step 2 그룹 분할 — DOE 1그룹 · direct wbpj 별 1그룹 · 미착수 키 배제 · 같은 wbpj 다른 target 비병합 · 케이스 없는 키 무시 |
| `tests/e2e/tst_e2e_real_exe` | X (실물 하네스) | 실 exe 3종 데몬 왕복(이벤트 구동 전환), 구독자 소멸 중 러너 생존, 워커 자식까지 트리 kill |

e2e 는 실 exe·실 환경을 요구해 ctest 에 등록하지 않는 별도 하네스다 ([#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207) 관례). ctest 등록 타깃은 5 → **10**으로 늘었다.

**2차 파동이 검증에 세운 것 3가지**

1. **장부를 순수 값 타입(비 `QObject`)으로 둔 결정이 검증을 환경에서 풀었다** — A(wbpj) 경로는 Step 1 이 NX, Step 2 가 Ansys 에 묶여 e2e 가 환경 확보까지 밀리는데, `DashBatchLedger` 가 값이면 Qt Core+Test 전용 하네스에서 전이·매핑·종료 판정을 환경 없이 검증할 수 있다. [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251)·[#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264)·[#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265) 가 이 하네스로 상태 층위를 덮었다.
2. **VTK 의존을 피해 판정만 떼어 내는 패턴이 3회 반복됐다** — `DashDirectJobPlan.h`([#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264)) · `DashWbpjLaunchPlan.h`(PR #275) 는 헤더 온리 + QtCore 만이라 테스트 타깃에 들어간다. `DashJobRunner`/`DashAnalysisLauncher` 는 `controller/DashManager.h` 가 `vtk*.h` 를 끌어와 **영구히 못 들어가므로**, 검증하려면 판정을 순수 함수로 빼는 것이 유일한 길이다.
3. **변이 테스트로 통과의 공허함을 확인했다** — [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 가 `MorphingGate` 에 변이 2건(마샬링 제거 · `release()` 멱등성 제거)을 주입해 `tst_morphing_gate` 가 실패하는지 확인하고 복원했다. 이 브랜치에서 유일한 사례다.

**3차가 더한 것 — `static_assert` 로 발급 경로를 봉인**했다. `tst_preprocessor_gate` 는 런타임 케이스 7종 외에 "`Reservation` 을 `Claim` 없이 만들 수 없다" 를 `static_assert` 5개로 못 박는다. 런타임 테스트는 *잘못된 사용이 실패함* 을 보이지만 `static_assert` 는 *잘못된 사용이 존재할 수 없음* 을 보인다 — 게이트처럼 "빠뜨림" 이 주 실패 모드인 기제에는 후자가 맞는 층위다.

**자동화가 덮지 못하는 것** — 데몬 계열 단위 테스트는 전부 `daemon_stub` 기준이라 실 exe 거동(특히 실 데몬이 stdin `exit` 를 무시하는 것)을 잡지 못한다. 앱 자체는 라이브러리가 아니라 단일 exe(`GLOB_RECURSE`)라 **`view/`·`DashManager`·`DashMorphingUtils` 는 링크할 대상이 없다** — 진입점 가드 6곳, 게이트 거부의 실제 발화, 케이스 표·로그 갱신이 전부 수동 확인이다. 실기 잔여는 "추가 수정 항목" 절에 모았다. 또 `external/DashGizmo/lib/DashGizmo.lib` 가 Release 전용이라 **Debug 구성은 빌드되지 않는다**(`LNK2038`×4 → `LNK1319`) — [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 가 `ctest -C Debug` 로 9/9 를 돌린 것은 `tests/` 가 Qt Core+Test 전용 별 타깃이기 때문이고, 앱 쪽 assert 를 켜려면 여전히 RelWithDebInfo + `QT_FORCE_ASSERTS` 를 쓴다.

---

## 부록 8 전수 목록 대조 — 진행 현황

[#205](205-5-w6-w10-async-minimal-example.md) 8장 부록("동기 → 비동기 전환 대상 전수 목록")의 각 지점을 위 변경 항목과 대조한 결과. **표기**: `207-4항` = 본 문서 [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207) 섹션 4번 항목 · ✅ 완료 · 🔶 부분(완화·부산물) · ⬜ 미착수 · ❌ 폐기(재판정으로 대상 소멸). 라인 번호는 부록 기준(2026-07-15/16 `dev`)이며 이동한 것은 `현 :N` 으로 병기 — **2차 파동의 재편으로 좌표가 크게 이동했으므로 착수 시 재실측한다**([#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279) 가 좌표를 규범에서 뺀 이유).

### 지표 실측 — 부록 기준 시점 대비

| 지표 | 부록 (2026-07-21 `dev` `52965e4`) | 1차 종료 (`9f2f14f`) | 2차 종료 (`b579bcf`) | 현재 (`0320683`) | 근거 |
|---|---|---|---|---|---|
| `QProcess::waitFor*` 실호출 | 23곳 / 4파일 (ExtensionProcess 11 · JobRunner 7 · ModelBuilder 3 · TopOptDialog 2) | **11곳 / 3파일** (ExtensionProcess 3 · JobRunner 7 · ProcessKill 1) — 잔여 ExtensionProcess 3은 전부 `shutdownBlocking()` 이라 **GUI 경로 0건** | 11곳 불변 | **11곳 불변** — 잔여 JobRunner 7곳이 motion stage 1·2 에 몰려 있다([#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) 전량 제거 예정) | `207-4항` · `208-5항` · `209-11항` · `212-1·6항` |
| `QThreadPool::waitForDone` | 0 | 0 | **2곳 신규** (모핑·RW) | **3곳** (+ preprocessor) — 세 풀이 상한 하나(3s)를 나눠 쓴다. GUI 스레드를 막는 **진짜 블로킹 대기**라 명시 존치로 선언해야 "GUI 대기 0건" 이 성립한다 | `214-1·10항` · `274-7·8항` · `277-8항` |
| `msleep` | 5곳 (전부 JobRunner) | **4곳** 불변 (`waitForVtuFileComplete` 3 · dfsxml 1) | **0곳** | 0곳 불변 | `260-4항` |
| `processEvents` 실호출 | 58곳 (model 41 + view 17) | **55곳** 불변 (model 38 + view 17) | **42곳** (model 25 + view 17) | **20곳 (model 3 + view 17)** — **model 계층 목표 달성.** 잔여 3곳 전부 `DashJobRunner` | `260-4항` · `277-1\~26항` |
| 뷰 소유 QProcess | 2건 | **0건** | 0건 | **0건** 불변 | `209-6·11항` |
| 수제 QProcess 보유 클래스 | 6 | **1** (`DashJobRunner` motion 2지점) | 1 불변 | **1** 불변 | `207-2·4항` · `208-1\~3항` · `209-6·10·11항` |
| `bool` 동기 반환 데몬 API | 1 (`startDaemon`) | **0** — `void start()` + `ready()`/`died()`/`stopped()` | 0 불변 | **0** 불변 | `212-1항` |
| 워커 스레드 진입 경로 | 1 (`QtConcurrent::run` — DOE 샘플링) | 1 불변 | **2** — `WorkerJob`(직렬 풀) 추가 | **2** 불변. `moveToThread`·`std::thread`·`QRunnable` 은 여전히 0건 | `214-2항` |
| 직렬 풀 | 0 | 0 | **2** (모핑 · RW — RW 소비자 0건) | **3** (+ preprocessor). RW 소비자는 여전히 0건 | `214-1항` · `277-8항` |
| 등급 2 배제 게이트 | 0 | 0 | **1** (`MorphingGate` 증명형) | **2** (+ `PreprocessorGate` — 동형 3형) | `214-3항` · `274-1·2항` · `277-9·11항` |

[#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) 은 1차 6지표를 하나도 움직이지 않는다 — 워커 축 게이트라 외부 프로세스 대기 지점을 건드리지 않기 때문이고, 이는 티켓 설계대로다.

**지표를 움직인 티켓은 소수다.** 2차에서 `msleep` 0 과 model `processEvents` −13 은 전부 [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) 하나의 산물이고, 나머지 5건은 이 표를 움직이지 않았다. 3차의 model pE −22 는 [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 하나다. 지표가 크게 내려간 두 시점이 모두 **"동기 루프를 이벤트 연쇄로 펴는" 성격의 티켓**이었고, 장부·종결 수렴이나 게이트 재편은 계수를 건드리지 않는다 — 그런 티켓의 값은 계수 밖에 있다.

**model 계층 `processEvents` 0 이 [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) 의 1차 목표였다.** 잔여 3곳은 전부 `DashJobRunner` 이고 담당이 확정돼 있다 — [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) 2곳(`runMotionWriter` 폴링 루프) · [#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279) 1곳(`createRunsFolders` — dead code 삭제).

> **검사 명령이 좌표 목록을 대체했다** ([#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279) 산물). 위 계수의 규범은 이제 아래 3명령이고, 잔여 목록은 착수 시 실측이 만든다. 전수(⑴)와 실호출(⑵)의 차이가 곧 주석 오탐 목록이므로 제외 목록을 사람이 관리하지 않는다.
>
> ```bash
> L="model/ view/ controller/ viewmodel/"
> grep -rn "processEvents" $L                                    # 전수
> grep -rn "processEvents" $L | grep -v ":[0-9]*: *//"           # 실호출
> grep -rn "waitFor[A-Za-z]*(" $L                                # GUI 블로킹 대기
> grep -rn "msleep\|QThread::sleep\|::usleep" $L                 # 슬립
> ```
>
> `b579bcf` 에서 pE = 44 / 42 / 2, 대기 = 16(주석 0), 슬립 = 0.

### 8-1. one-shot 동기 완주·기동 확인 (P3·P4) → ProcessJob

| 대상 | Issue | 근거 | 현황 |
|---|---|---|---|
| `DashExtensionProcess::runBlocking` `:335-366` (호출처 0, 휴면 지뢰) | [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207) | `207-4항` | ✅ `grep runBlocking` → 0 |
| `killOrphans` 광역 taskkill + `waitForFinished(3000)` `:52-69` | [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207)·[#209](https://github.com/NumeRealWorks/DashOpti_GUI/issues/209) | `207-6항` · `209-1항` | ✅ 광역 `/IM` → 자기 PID `/F /PID /T`. 3s 동기는 의도적 잔존(데몬 재기동 직전 정리) |
| `waitForStarted` — `DashModelBuilder:637` | [#208](https://github.com/NumeRealWorks/DashOpti_GUI/issues/208) | `208-5항` | ✅ `finished(Failed)` 통지 |
| `waitForStarted` — `TopOptPostprocessDialog:1794` | [#209](https://github.com/NumeRealWorks/DashOpti_GUI/issues/209) | `209-11항` | ✅ 위임의 부산물 |
| `waitForStarted` — `DashExtensionProcess:354` | [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207) | `207-4항` | ✅ 경로 자체 소멸 |
| `waitForStarted` — `DashJobRunner:685` (motion-writer, 현 `:610` 10s) | **[#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282)** | — | ⬜ `ProcessJob` 수렴 예정 |
| `waitForStarted` — `DashJobRunner:848` (motion-launcher, 현 `:773` 무인자=30s) | **[#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282)** | — | ⬜ 동일. `QProcess::started` 슬롯 안은 **철회**됐다 — `Job::started` 가 `m_proc->start()` 이전에 뜨므로 양립 불가 |
| `DashJobRunner::runMotionWriter` `:666-729` — `waitForFinished(500)`+`processEvents` 5분 반복 (현 `:591`) | **[#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282)** | — | ⬜ **이 대기 하나에 stage 1 의 직렬성·상한·취소가 전부 얹혀 있다**(아래) |

### 8-2. 데몬 기동 동기 대기 (P1) → DaemonHost + `daemonReady`

| 대상 | Issue | 근거 | 현황 |
|---|---|---|---|
| `startDaemon` `:143` `waitForStarted(30000)` (현 `:163`) | [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) | `212-1항` | ✅ 삭제 — PID 등록은 `QProcess::started` 슬롯이 대체 |
| `[READY]` busy-wait `:151-159` — 기본 15s, NX 120s (현 `:182`) | [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) | `212-1·3항` | ✅ 루프 2곳 삭제 → `QTimer` 상한. 값(30s / NX 120s)은 남되 **프리즈 상한이 아니라 Starting 이벤트 상한** |
| 이중 기동 가드 `:97-108` (현 `:123`) | [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) | `212-2항` | ✅ desired/actual reconcile 로 대체 — `start()` 가 Ready·Starting 에서 idempotent |
| `enqueueLoadPrt`/`enqueueUpdatePrtGeometry` `:124-126,147-149` — 첫 enqueue 가 동기 부팅 유발 | [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) | `212-1·8항` | ✅ lazy 기동 + 즉시 반환, 순서는 큐가 흡수 |
| 동기 부팅 진입점 7곳 큐잉 전환 | [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) | `212-8·9·10항` | ✅ 소비처 18곳 전수 전환에 포함 |

[#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) 이 범위 밖에 뒀던 DOE 진입 전 `tryStartIfConfigured()` 동기 대기는 [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) 가 제거했고, 게이트는 config 판정(`nxConfigured`)으로 바뀌어 기동 실패가 케이스별 `batchFailed` 로 온다. 이로써 [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) 의 "조기 return 4곳" 중 데몬 기동 실패 항은 성격이 달라졌고, 나머지 3곳은 [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) 이 조기 이탈 7곳으로 재실측해 `finishBatch()` 로 수렴시켰다. [#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264) 가 남은 무신호 `return` 7곳을 `abortBatch` 로 덮고, [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 가 그중 **착수 전 15곳을 `rejectBeforeBegin` 으로 갈랐다**(`abortBatch` 는 `beginBatch` 성공 이후에만 유효하다는 계약). 세 티켓이 같은 지점을 세 번 만졌고, 최종 형태는 "착수 전 = 로그만 / 착수 후 = 장부 스윕 + job 시그널" 2갈래다.

### 8-3. 동기 종료·취소 대기 (P2) → kill 발사 후 즉시 반환

| 대상 | Issue | 근거 | 현황 |
|---|---|---|---|
| `runAsync` 도입부 kill + `waitForFinished(2000)` `:379-384` | [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207) | `207-4항` | ✅ |
| `DashModelBuilder::stopTraining` terminate→kill 재대기 `:1237-1243` | [#208](https://github.com/NumeRealWorks/DashOpti_GUI/issues/208)·[#209](https://github.com/NumeRealWorks/DashOpti_GUI/issues/209) | `208-5항` · `209-2항` | ✅ `cancel()` + 트리 kill (워커까지 회수) |
| `TopOptPostprocessDialog` 소멸자 `:2155-2157` (3s) | [#209](https://github.com/NumeRealWorks/DashOpti_GUI/issues/209) | `209-11항` | ✅ |
| `stopDaemon` `:178-183` + 소멸자 `:18-21` — 8s×N 직렬 누적 (현 `:204-207`) | [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) | `207-9항`(재진입 수리) · `212-1·6항` | ✅ `stop()` = exit 요청 + stop-timer(만료 시 kill). 동기 대기는 소멸자·앱 종료의 `shutdownBlocking()` 만 **의도적 잔존** — 다만 실 데몬이 stdin `exit` 를 무시해 종료당 5s 소진 후 kill 로 떨어진다(신규 발견분 참조) |
| `DashJobRunner` 소멸자 `:455-462` — 무인자 `waitForFinished()`=30s/프로세스 (현 `:482`) | **[#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282)** | — | ⬜ 컨테이너 값 타입이 `ProcessJob*` 로 바뀌면 `job->cancel()` 로 대체된다 — 트리 kill + 터미널 잠금이 "늦은 핸들러 폐기" 를 **대기 없이** 성립시킨다 |
| `cancelAllRuns` `:946-948` (현 `releaseRunResources:1315` `waitForFinished(3000)`) | **[#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282)** | `210-12항`(NX 데몬 회수 시점) · `260-18항`(`cancelSolverTaskForKey` 신설) · PR #275(motion kill 추가) · `274-6항`(4종 통합 + 진입 assert) | 🔶 **열거는 한 벌이 됐다** — 취소 자원 4종이 `releaseRunResources` 한 곳으로 모이고 순회 순서가 장부 착수 순서로 고정됐다. 대기 자체는 존치 |
| motion-writer 타임아웃 `:711-714` (현 `:637-639`) | **[#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282)** | — | ⬜ |

### 8-4. 파일 폴링·고정 슬립 (P5·P6) → 완료 시그널 구독 + 파일 검증

| 대상 | Issue | 근거 | 현황 |
|---|---|---|---|
| `waitForFile` `:2351-2364` ← `runWbpjDoeAsync:2670-2673` (600s/케이스) | [#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) | `210-1항` · `210-7항`(워치독 승계) · `210-10항` | ✅ `grep waitForFile` → 0 |
| `waitForVtuFileComplete` `:598-664` — `msleep(100)`+`processEvents` + 0.5s 안정화 휴리스틱 | [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) | `260-3·4항` | ✅ 정의·선언·호출 삭제. 존재 검사가 아니라 **`DashSampleResult::ok`** 가 성공을 판정한다 (구 [#211](https://github.com/NumeRealWorks/DashOpti_GUI/issues/211) 흡수분 종결) |
| `msleep(1000)` 고정 슬립 `:1576` — dfsxml 모핑+MBD 루프 도입부 | [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) | `260-4항` | ✅ 삭제 — 모핑이 이미 완주한 뒤의 대기였다. 배치당 `1000ms + N × 500ms` 확정 소진 소멸, 리포 전체 `msleep` **0건** |

### 8-5. in-process 동기 실행 → WorkerJob + 직렬 풀

| 순위 | 대상 | Issue | 근거 | 현황 |
|:---:|---|---|---|---|
| — | 선결 조건 5건 게이트 (D1\~D5) | [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) | `213-1~11항` | ✅ 실제 해소는 **6건**(D1·D2·D3·D5·D6·D7) — D4 는 대상 소멸, D6·D7 은 계획 단계에서 추가. **[#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 게이트 오픈** |
| 1 | DOE 배치 모핑 루프 — `processEvents` 조차 없는 완전 정지 | [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260)·[#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) | `260-1항` · `214-1·2·4항` | ✅ `RunOneSample` 1건 = 모핑 직렬 풀 위 WorkerJob 1개. 샘플 **내부에서도** 이벤트 루프가 산다 |
| 2 | 단건 모핑·프리뷰 N루프 | **[#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281)** | `274-13항` | 🔶 진입점 5(Optimizer·ModelRunner)가 Claim 스코프로 **동기 유지**(축소 구현) — 루프 진입 거부는 서고 워커화는 남았다. 프리뷰(1·1b)는 [#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281) 도 무접촉 — **후속 과제로 분리** |
| 3 | FE 모델 파싱 | **[#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282)** | — | ⬜ `parseFemToUnstructuredGrid` 705줄. view 에 있지만 model 급 작업 |
| 4 | RST/KPI 파싱 7종 | [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) | `277-13·15·22·24항` | ✅ 2,964줄 · pE 22곳 전량. 요청·출력 단위 Job 연쇄 + `preprocessorSerialPool` + `PreprocessorGate` |
| 5 | export/serialize/메시 갱신 | ([#280](https://github.com/NumeRealWorks/DashOpti_GUI/issues/280) 재판정) | — | ❌ **폐기.** 컨텍스트 write 호출부 7곳 중 6곳이 이미 `morphingSerialPool` 워커 안이고, `rwSerialPool` 로 보내면 규약 7절("두 서브시스템을 함께 만지는 Job 은 모핑 풀 하나에만")을 정면 위반한다. GUI 잔여 write 는 조건 셀 1개 편집 하나로 워커화 이득이 없고 `serialize` 는 심볼 0건 |
| 6 | VTU/VTK·CSV 쓰기 (여력 시) | **[#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281)** 흡수 | — | 🔶 구 P5([#283](https://github.com/NumeRealWorks/DashOpti_GUI/issues/283))로 떼어냈다가 **전수 실측 후 흡수·close**. live 4곳은 진입점 워커화와 **동반 이동**, 1곳은 dead, CSV(`DashAnalysisLauncher::saveDoeToCsv`)는 이미 `QtConcurrent::run` 안이고 지울 쪽은 `DashDoeConfigManager` 의 중복 구현이었다 |

[#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) 이 이 절에서 유일하게 닫은 행이 게이트였고, [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260)·[#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 가 순위 1, [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 이 순위 4 를 닫았다. **[#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) 는 확산 5건을 직접 구현하지 않고 부모 티켓이 됐다** — 4축으로 갈라 [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277)(preprocessor) · [#280](https://github.com/NumeRealWorks/DashOpti_GUI/issues/280)(RW) · [#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281)(모핑) · [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282)(프로세스·파서)에 넘기고 [#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279) 가 봉인한다. 중간에 [#278](https://github.com/NumeRealWorks/DashOpti_GUI/issues/278)(6 Phase 통합)과 [#283](https://github.com/NumeRealWorks/DashOpti_GUI/issues/283)(구 P5)이 생성됐다가 재분할·흡수로 close 됐다.

### 8-6. `processEvents` 재진입 창 (P7) → 전환의 부산물

| 대상 | Issue | 근거 | 현황 |
|---|---|---|---|
| model 41곳 (`DashJobRunner` 19 · `DashDataProcessor` 14 · `DashResultProcessor` 8) | [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) 2 · [#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279) 1 | `260-4항` · `277-1\~26항` | 🔶 **3곳** — JobRunner 19 → 3([#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260)) · `DashDataProcessor` 14 → 0 · `DashResultProcessor` 8 → 0([#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277)). 잔여 3곳 = **[#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282)** 2(`runMotionWriter` 폴링) + **[#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279)** 1(`createRunsFolders` — dead code 삭제) |
| view 17곳 (TopOpt 6 · DataProcessorWidget 3 · Optimizer 2 · GeometryParam 2 · ViewOptions 2 · MainWindow 1 · MeshQuality 1) | [#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281) 5 · [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) 5 · [#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279) 7 | — | ⬜ **17곳 불변** — 담당은 갈렸다. **[#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281)** 5(GeometryParam 2 + MeshQuality 1 + Optimizer 2) · **[#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282)** 5(TopOptPostprocessDialog) · **[#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279)** 7(⒝ 단발 리페인트 분류 + `runKpiAutoTest` dead 3) |

> **아종 3분류가 확정됐다** ([#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279)). ⒜ 동기 루프 펌핑 = 재진입 창이므로 [#64](https://github.com/NumeRealWorks/DashOpti_GUI/issues/64) 크래시 계급 — 선행 3건이 전량 제거한다. ⒝ 단발 강제 리페인트 = 진행 시그널 배관 신설이 W11 scope 라 **인계 목록으로만** 산출한다. ⒞ 실행 경로 밖 = dead code, DoD 계수 대상을 보유하면 제거한다. 이 축은 처분 범주(⓵ 소멸 · ⓶ 항구 존치 · ⓷ W11 인계 · ⓸ 비실행 오탐)와 **다른 축**이다.
>
> `reader->Update()` 계열 GUI 프리즈는 **어느 DoD 축에도 걸리지 않는다** — 이벤트를 펌핑하지 않아 재진입 창을 열지 않으므로 [#64](https://github.com/NumeRealWorks/DashOpti_GUI/issues/64) 계급이 아니고, 성격이 응답성이라 W11 소관이다. 중첩 `exec()` 도 같다 — 재진입 창은 같은 계급이나 DoD 를 넓히지 않고 각 자식이 자기 함수에서 확인한다.

### 8-7. 동기 반환 API 계약 (P8) → 시그널 계약

| API | Issue | 근거 | 현황 |
|---|---|---|---|
| `bool DashExtensionProcess::startDaemon()` — 반환 시점에 ready 확정, 의존 호출자 4곳 | [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) | `212-1항` | ✅ `void start()` + `ready()`/`died()`/`stopped()`. 소비처는 4곳이 아니라 **18곳**이었고 전수 전환 |
| `bool runBlocking(...)` — 호출처 0 | [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207) | `207-4항` | ✅ 삭제 |
| `bool DashJobRunner::runMotionWriter(...)` — 모핑+MBD 루프 `:1645` 의존 (현 `continueDfsxmlForSample` 경유) | **[#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282)** | — | ⬜ `void` 로 전환 예정. `runMotionLauncher` 의 bool 분기도 완료 슬롯으로 이동 |

### 동반 사항 2건 (W6 구조 전제)

| 대상 | Issue | 근거 | 현황 |
|---|---|---|---|
| 수제 QProcess 6클래스 수렴 | [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207)·[#208](https://github.com/NumeRealWorks/DashOpti_GUI/issues/208)·[#209](https://github.com/NumeRealWorks/DashOpti_GUI/issues/209) | `207-2·4항` · `208-1\~3항` · `209-6·10·11항` | ✅ 실질 1클래스(`DashJobRunner` motion 2지점 — [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) 대상). 엔진 `ProcessJob`·데몬 `DashExtensionProcess` 제외 |
| 뷰 소유 QProcess 2건 (`m_fitProcess:2418` · `m_postprocessProcess:1749`) | [#209](https://github.com/NumeRealWorks/DashOpti_GUI/issues/209) | `209-6항` · `209-11항` | ✅ `view/` QProcess 0 — "창 닫힘 = 작업 사망" 소멸 |

### 진척 집계

| 부록 절 | 대상 | ✅ | 🔶 | ⬜ | ❌ | 남은 것의 담당 |
|---|:---:|:---:|:---:|:---:|:---:|---|
| 8-1 one-shot | 8 | 5 | — | 3 | — | [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) |
| 8-2 데몬 기동 | 5 | **5** | — | — | — | — |
| 8-3 종료·취소 | 7 | 4 | 1 | 2 | — | [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) |
| 8-4 폴링·슬립 | 3 | **3** | — | — | — | — |
| 8-5 in-process | 7 | 3 | 2 | 1 | 1 | [#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281) 2 · [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) 1 |
| 8-6 processEvents | 2 | — | 1 | 1 | — | [#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281)·[#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282)·[#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279) |
| 8-7 API 계약 | 3 | 2 | — | 1 | — | [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) |
| 동반 사항 | 2 | 2 | — | — | — | — |
| **합계** | **37** | **24** | **4** | **8** | **1** | — |

1차 종료 시점 대비 ✅ **20 → 24**, ⬜ **16 → 8**. 담당은 [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) 단일 소유에서 자식 티켓으로 갈라졌고, 그중 [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 은 **자기 몫을 다 닫고 나갔다**.

| 담당 | 잔여 | 내역 |
|---|:--:|---|
| [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) | **8** | 8-1 의 3 · 8-3 의 3(🔶 1 포함) · 8-5 순위 3(FE 파서) · 8-7 의 1 — `DashJobRunner` motion stage 1·2 가 한 덩어리다 |
| [#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281) | 2 | 8-5 순위 2(🔶) · 순위 6(🔶) |
| [#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279) | — | 8-6 의 최종 판정·봉인 (계수 소유 아님) |
| [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) | **0** | 8-5 순위 4 완료 (CLOSED) |
| ([#280](https://github.com/NumeRealWorks/DashOpti_GUI/issues/280) 재판정) | ❌ 1 | 8-5 순위 5 폐기 |

- **외부 축(8-1·8-2·8-3·8-4·8-7)은 26건 중 20건이 닫혔다**(1차 종료 17건 → +3, 8-4 완결). 잔여 6건은 전부 `DashJobRunner` 의 motion 계열이고 **한 티켓([#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282)) Phase 1 이 통째로 가져간다** — stage 1 의 직렬성·상한·취소가 그 블로킹 대기 하나에 얹혀 있어 쪼갤 수 없다.
- **8-4(폴링·슬립) 완결** — [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) 이 남은 2건을 한 번에 닫았다. 구 [#211](https://github.com/NumeRealWorks/DashOpti_GUI/issues/211) 흡수분까지 포함해 **리포 전체 `msleep` 0건**이다.
- **8-2(데몬 기동) 완결** — [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) 가 5건을 한 브랜치에서 닫았다. 축별 분할을 하지 않은 것이 옳았다 — 계약이 공유 기반 클래스에 있어 쪼개면 구 `bool startDaemon()` 호환 분기가 필요해진다.
- **8-5(워커 축)에서 진짜로 워커가 된 것은 순위 1 하나다.** [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) 게이트 → [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) 분해 → [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 워커화로 3티켓이 걸렸고, 그 대가로 **인프라(`WorkerJob`·직렬 풀·`MorphingGate`)가 서서 순위 3·4 의 착수 비용이 내려갔다**. 순위 5 는 재판정으로 폐기, 순위 6 은 별 티켓([#283](https://github.com/NumeRealWorks/DashOpti_GUI/issues/283))을 만들었다가 실측 후 흡수했다 — **워커화 대상 목록은 실측 없이 만들면 과대추정된다.**
- **순서 제약이 셋에서 둘로 줄었다.** [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 이 `WorkerJob::Task` 를 2인자 형(`const std::atomic<bool>&`, `const ProgressSink&`)으로 확장하고 머지되면서 **[#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) Phase 2 의 유일한 선행이 해소됐다**. 남은 제약은 ⑴ [#280](https://github.com/NumeRealWorks/DashOpti_GUI/issues/280) → [#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281) Phase D·E(`RwGate` 배관) ⑵ [#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281)·[#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) → [#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279) 둘이고, **[#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) 는 두 Phase 모두 지금 착수 가능**하다.
- 위 37건 집계에 **포함되지 않는 것**: 본 문서 항목 중 결함 수리 37건(회귀 32 · 선재 5) · 테스트·검증 21건 · 파생 31건 · 별건 티켓 [#249](https://github.com/NumeRealWorks/DashOpti_GUI/issues/249)·[#269](https://github.com/NumeRealWorks/DashOpti_GUI/issues/269). 부록은 "동기 → 비동기" **지점** 목록이라 이 부류에 대응 행이 없다 — 항목별 내역은 "계획 대비 실제 — 항목 분류" 참조.

---

## 잔여 설계 2건의 처분 — [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) 머지 · [#249](https://github.com/NumeRealWorks/DashOpti_GUI/issues/249) 별건

[#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) 의 미진분은 두 방향으로 갈렸다 — **수신측**(받은 뒤 무엇으로 확정하는가) = [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251), **발신측**(누가 무엇을 받는가) = [#249](https://github.com/NumeRealWorks/DashOpti_GUI/issues/249). 수신측은 3티켓([#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251)·[#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264)·[#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265))에 걸쳐 닫혔고 발신측은 여전히 열려 있다(별건 절 참조).

**[#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) 은 설계가 바뀐 채로 구현됐다.** 계획 시점 설계(방안 A — `CaseState` 8종 flat enum + `BatchPhase` 4종)로 PR #262 까지 갔다가 [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) 과의 심볼 충돌로 Draft 로 내려가고, 그 위에서 **인코딩을 배열형 장부로 뒤집었다**. 계획 대비 실제는 이렇다.

| 축 | 계획 (방안 A) | 실제 |
|---|---|---|
| 상태 표현 | `CaseState` 8종(단계×결과) flat enum + `BatchPhase` 4종. `setCaseState` 단일 출구 | **`DashBatchLedger` 2칸**(stage 0 = STP · stage 1 = 해석 · `terminalStage = 1`) + `WbpjPhase` **3종**. `setStageState` 단일 출구. 8종 flat enum 폐기 |
| 종료 수렴 | `finishBatch()` 한 지점 + 잔여 스윕. 조기 return 4곳 → `abortBatch` | **그대로 승계** — 인코딩에 무관한 축이었다. 조기 이탈은 실측 후 **7곳**으로 늘었고, [#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264) 가 나머지 7곳을, [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 가 착수 전 15곳 분리를 마쳤다 |
| 발신·수신 규약 | 실패 시그널에 `stpPath` · 슬롯 3단(`귀속 → 전이 → advance()`) | **그대로 승계** |
| 사라진 멤버 | `pending`·`current`·`activeRunKeys`·`failedKeys`·`active`·`cancelled` 6개 | **그대로** — 인덱스 멤버 0개 |
| 미결로 남긴 것 | Step 2 대기 상한(규약 E4) · `status_cancelled.svg` · Set/프로젝트 전환 중 진행 · P3 차단분과 사용자 취소 구분 | **전부 잔존** — 아래 "추가 수정 항목" |
| 규모 | 4파일 / 순변경 +70 / 5 Phase | **7파일 / +524 −315(순 +209) / 커밋 6개.** 초과분은 주석 70줄 + 블록 이동의 diff 이중 계상 + 결함 8건 수리 |

**인코딩을 뒤집은 대가 1건**: `stage 0 Running` 표기 규칙이 갈렸다. [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) 규칙은 `"Running"`, [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) 초안은 생략이었다. 규칙에 맞추면 특례가 사라지는 대신 **STP 생성 중 1건이 `Enqueued` 대신 `Running` 으로 보인다**(미착수분은 `Pending` 이라 `Enqueued` 유지). AC 한 줄("Step 1 진행 중 `Enqueued` 표기가 STP 성공까지 유지")을 [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) 쪽에서 양보했다. 나머지 4개 매핑은 전수 대조에서 일치했다.

### 구현된 케이스 상태 모델 — 배열형 장부

```
장부 = { runKey → [stage 0 상태, stage 1 상태, ...] }  ·  stage 상태 5종
경로별 칸 구성   A(wbpj) 2칸 · C(dat/inp) 2칸 · F(dfsxml) 3칸 · 폴백·FE-safe·Direct 1칸

A(wbpj) 케이스 1건의 생애
   │
   ├─ [stage 0] STP 생성 — NX CAD 데몬
   │      Pending ─착수─→ Running
   │         │               ├─ 성공 → Done  (마지막 칸이 아니므로 UI 는 "Running")
   │         │               ├─ 실패 · 워치독 타임아웃 · 데몬 사망 통지 → Failed ▣
   │         │               └─ 취소가 와도 끊지 않음 (완료 수용 = P1)
   │         └─ 미착수인 채 배치 종료 → Cancelled ▣
   │
   ├─ [stage 1] 해석 실행 — Ansys Journal (terminalStage)
   │      Pending ─그룹 1회 launch─→ Running
   │         │               ├─ RST 확인 → Done ▣  (마지막 칸이므로 UI 는 "Done")
   │         │               ├─ DAT·RST 없음 · launch 실패 → Failed ▣
   │         │               └─ Journal 미착수 · 진행 중 취소 → Cancelled ▣
   │         └─ stage 0 이 터미널로 닫히면 이 칸은 열리지 않는다
   │
   └─ [종결] 전 케이스가 터미널 도달 → finishBatch() 가 jobFinished / jobFailed 1건
              성공 0건이면 jobFailed · 사유는 값으로 전달 (참조 바인딩 금지)
```

전이 규칙 5종이 장부에 있고 경로가 공유한다 — 마지막 아닌 칸 `Done` → `"Running"` · 마지막 칸 `Done` → `"Done"` · 임의 칸 `Failed`/`Cancelled` → 동명 라벨 · `Pending` → **통지 생략**(미착수분의 `Enqueued` 표기 보존). 종료 상태 재전이는 경고와 함께 무시된다(**종료 단조성**) — 이것이 Analysis 단계 취소가 뒤늦은 `journalLaunchFailed` 에 Failed 로 덮이지 않는 근거이고, 동시에 [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) M3 회귀(취소가 Failed 로 뒤집힘)의 원인이기도 했다 — 단조성은 **상태 확정 순서에 대한 요구**를 새로 만든다.

`terminalStage` 는 배치별로 **하향 조정**된다 — 솔버 미설정이면 해석 칸을 잘라 "모핑만" 배치가 되고, 그 상태에서 stage 0 `Done` 이 마지막 칸이 되어 `"Done"` 으로 나간다([#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) 17항 · [#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264) 6항 · [#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265) 14항이 같은 형태를 세 경로에 적용). 리포트 지점이 스테이지 번호를 상수로 박으면 이 하향에서 전이가 범위 밖으로 버려지므로, [#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264) 가 15곳을 전부 `terminalStage(key)` 유도로 바꿨다.

상세는 [264-2-batch-stage-ledger-concepts](264-2-batch-stage-ledger-concepts.md).

---

## 핵심 발견

- **전환이 만든 회귀가 전환 자체보다 항목 수가 많다.** [#208](https://github.com/NumeRealWorks/DashOpti_GUI/issues/208) 14항 중 계획분은 4항(위임 3종 + 그 부산물인 블로킹 제거)이고 나머지 10항은 수리·테스트다. 특히 "공유 `QProcess` 를 Qt 가 배타 자원으로 지켜 주던 보호"가 1회용 Job 으로 바뀌며 사라진 계급(재실행 가드 3종·초기화 순서·수명 분리)이 반복해서 나왔다 — 위임 전환 시 **암묵적 보호의 목록화**가 선행되어야 한다는 교훈.
- **계획서에 결정을 적어 두면 그만큼이 계획분이 된다.** [#209](https://github.com/NumeRealWorks/DashOpti_GUI/issues/209) 는 [#208](https://github.com/NumeRealWorks/DashOpti_GUI/issues/208) 과 항목 수가 같은데 계획분이 8항이다 — 차이는 코드가 아니라 D1~D7 로 선재 결함·소멸자 누락·버튼 상태 복원까지 미리 적었다는 점이다. 계획 외 비율은 구현 난도보다 **계획 단계 조사 깊이의 함수**다.
- **블로킹은 소멸하지 않고 소멸자로 이동한다.** [#208](https://github.com/NumeRealWorks/DashOpti_GUI/issues/208) 10항(`~QProcess` 의 `waitForFinished` 30s)과 [#209](https://github.com/NumeRealWorks/DashOpti_GUI/issues/209) 9항(`~DashOptimizer`)은 같은 계급이다. `waitFor*` grep 이 0 이어도 소멸자 경로는 잡히지 않는다.
- **폴링이 겸하던 책임은 폴링과 함께 사라진다.** [#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) 에서 `waitForFile` 의 600s 상한이 워치독으로 승계되어야 했고, 강제 종료 시 진행 커맨드 회수 누락이 그 자리에서 드러났다.
- **식별자를 버리는 한 줄이 시그널 증설로 되돌아온다.** [#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) 이 배치 전용 시그널 2종을 증설한 이유가 파사드의 `commandId` 폐기이고, 소비자가 3종이 되면 같은 증설이 반복된다 — [#249](https://github.com/NumeRealWorks/DashOpti_GUI/issues/249) 가 이 지점을 닫는다.
- **동기 계약을 지우면 컴파일러가 잡아 주는 것은 소수다.** [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) 의 소비처 18곳 중 `bool` 반환을 읽는 3곳만 컴파일 에러가 되고, 나머지 15곳은 **조용히 오작동**한다(무음 드롭·낡은 STP 재사용·모달·배치 abort). 계획서가 18곳 전수표를 먼저 만든 것이 이 티켓의 계획분 비율을 결정했고, 반대로 컴파일 통과를 완료 신호로 삼았다면 은닉 회귀가 그대로 나갔다.
- **무음 실패는 가드 한 줄에 숨어 있다.** 사망 경로에서 `if (error != QProcess::Crashed)` 가드 하나가 in-flight 명령의 실패 통지를 삼켰고, 꼬리 라인 drain 도 `!m_waitingFinished` 조기 반환에 막혀 죽어가는 데몬의 마지막 `[ERROR]` 줄까지 버렸다. "무음 실패 금지"를 DoD 로 세우지 않으면 이런 줄은 리뷰에서 정상 코드로 읽힌다.
- **공유를 끊으면 그 공유의 부작용에 기대던 것이 드러난다.** [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) 의 F2 가 정확히 이 계급이다 — 모핑 엔진을 per-Job 으로 쪼개자 "공유 엔진에 남아 있던 커널 반경"에 우연히 의존하던 두 경로가 동시에 드러났고, 하나는 회귀·하나는 선재였다. 격리 작업의 진짜 비용은 격리 자체가 아니라 **부작용 의존의 발굴**이다.
- **게이트를 갈아 끼우면 새 게이트가 새 차단이 된다.** [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) F1 — 구 게이트 `!interaction` 은 lazily 생성 때문에 **한 번도 발동한 적이 없었고**, 그 자리에 넣은 `snapshot.isValid()` 는 실제로 발동해 condition-only DOE 를 전면 차단했다. "같은 뜻의 판정으로 교체"라고 적힌 변경은 구 판정이 실제로 무엇을 통과시켜 왔는지부터 확인해야 한다.
- **한 번도 실행되지 않던 소멸자를 살리는 것은 신설과 같다.** [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) 의 magic static 전환으로 `~DashProjectManager()` 가 생애 최초 실행됐고, 그 안의 `delete m_project` 가 `QApplication` 사후에 QObject 트리를 해체하다 체인을 끊어 **데몬 4종이 고아로 남았다**. 정적 소멸 구간은 이벤트 루프가 없는 별세계이며, 여기 처음 들어가는 코드는 신규 코드로 취급해야 한다. [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 가 `AppShutdown::run()` 을 `aboutToQuit` 에 두고 소멸자를 멱등 백스톱으로 축소해 **정적 소멸 구간을 아예 피하는** 근본안으로 마감했다.

### 2차 파동의 발견

- **참조로 받은 실패 사유 한 줄이 전 실패 경로를 성공으로 보고했다.** [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) 10항 — `finishBatch(const QString&)` 가 호출부의 멤버에 바인딩된 뒤 `isEmpty()` 검사 **전에** 그 멤버를 `clear()` 했다. 취소·착수 거부·차단기·상한 초과 넷이 전부 `jobFinished`(성공 채널)로 나갔다. **단일 종료 지점을 만드는 것과 그 지점이 진실을 말하는 것은 다른 문제**이고, 후자는 시그니처(값 vs 참조) 한 글자에 달려 있었다.
- **성공의 근거를 옮기려면 생산자의 반환값이 먼저 진실해야 한다.** [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) 이 파일 존재 검사 3곳을 지우고 `bool` 로 판정을 옮겼는데, 그 `bool` 을 내는 `ExecuteOneSample` 이 VTU 쓰기 실패에 `true` 를 반환하고 있었다(11항). 검사를 지운 커밋과 반환값을 고친 커밋이 갈렸으면 **낡은 VTU 가 조용히 솔버 입력이 됐을** 것이다. 판정 이관은 생산자 감사와 같은 커밋에 들어가야 한다.
- **이름을 두 티켓이 각자 발급하면 컴파일이 먼저 깨진다.** [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251)·[#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) 이 `DashJobRunner` 에 각자 `finishBatch` 를 두어 1인자 호출이 **ambiguous** 였다(기본인자 개수는 오버로드 tiebreaker 가 아니다). 겹치는 심볼은 하나였는데 정상 종결 경로 5곳이 전부 깨지고 실패 경로만 남았다. 병행 티켓의 충돌 검사에서 **"같은 클래스에 새 public 이름을 넣는가" 는 파일 충돌보다 앞선 질문**이다.
- **종료 단조성은 공짜가 아니라 순서 요구를 만든다.** [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) 7항이 "종료 상태 재전이 무시" 를 도입한 즉시 M3 회귀가 성립했다 — `kill()` 이 동기 호출하는 `finished` 핸들러가 케이스를 Failed 로 **먼저** 닫아 뒤이은 Cancelled 가 삼켜졌다. 해법은 단조성을 되돌리는 것이 아니라 **취소를 kill 보다 먼저 확정**하는 것이고, [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 는 그 순서 요구를 `releaseRunResources` 진입 assert 로 국소 검출 가능하게 만들었다. 불변식을 도입하면 그것을 지키는 순서도 코드로 강제해야 한다.
- **핸들을 먼저 빼앗고 죽인다** — [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) M3 · [#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264) 19항 · [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 6항이 같은 관용구에 도달했다. 늦게 오는 핸들러가 **되살릴 대상이 없어야** 하고, 순회 중 컨테이너 변경(반복자 무효화)도 이 순서가 함께 막는다. `take` → `kill` 이 취소 코드의 기본형이다.
- **취소는 단위 테스트가 가장 못 덮는 경로다.** 2차 회귀 14건 중 취소 관련이 3건이고 셋 다 **코드 리뷰에서만** 잡혔다([#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) M3 · [#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264) 18항 · [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 10항). 트리거가 GUI, 대상이 외부 프로세스·스레드, 판정이 "그 뒤에 무엇이 오지 않는가" 라서 하네스가 성립하지 않는다.
- **질의형 게이트는 검사와 획득 사이가 벌어진다.** [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 는 `busy()` 조회 + `acquire()` 로 시작했고, [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 가 `tryClaim()` 단일 지점 + DLL 함수 4곳의 `const Witness&` 인자로 바꿔 **게이트를 빠뜨린 코드가 컴파일되지 않게** 했다. 다만 `Witness` 생성자가 `protected` 라 막는 대상은 **누락**이고 고의 위조는 아니다 — 타입으로 세우는 계약의 강도는 그 접근 지정자만큼이다.
- **자기 Claim 에 자기가 거부되는 구멍이 증명형 전환의 고정 비용이다.** [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 11항 — 진입점이 Claim 을 쥔 뒤 내부 함수가 `busy()` 를 다시 검사하면 실패한다. [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277)·[#280](https://github.com/NumeRealWorks/DashOpti_GUI/issues/280) 이 같은 형태의 게이트를 세우면서 **공개 진입은 획득 / 내부 호출은 증명 상속** 2층 분리를 설계에 미리 넣은 이유가 이것이다.
- **`Job::finished` 는 스레드 종료를 뜻하지 않는다.** [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 12항 — `ProcessJob::cancel()` 은 `QProcess` 를 떼어내 자기 종료를 자기가 회수하게 만든 뒤 즉시 터미널로 가는데, 풀 스레드는 그 "떼어내기" 가 불가능해 DLL 을 계속 쥔다. 같은 규약을 쓰면 `Morph()` 가 도는 중에 게이트가 풀려 **정확히 막으려던 등급 2 위반**이 열린다. 취소의 즉시성과 자원 해방을 **두 축으로 갈라야** 한다 — 약속은 "UI 즉시 해방" 이지 "CPU 즉시 해방" 이 아니다.
- **워커화는 잠들어 있던 방어선을 처음 발화시킨다.** [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) — 공유 컨텍스트 변이 창의 GUI 편집 거부는 배치가 GUI 스레드를 점유해 **도달 불가**였다. 스레드를 넣는 순간 실제로 동작하기 시작하며, 그 판정 근거의 스레드 안전성이 새로 문제가 된다. 반대 방향의 [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) F1(발동한 적 없던 게이트를 교체하니 전면 차단)과 대칭이다.
- **가드를 한 곳으로 모으면 그 앞의 경로가 노출된다.** [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 10항 — 진입점별 인라인 재진입 가드를 `beginBatch` 로 내리자, 그 **이전에** `abortBatch` 를 부르던 15곳이 남의 장부를 취소하게 됐다. 종전에는 인라인 가드가 우연히 앞을 막고 있었다. 판정을 단일화하는 변경은 **단일 지점 이전 구간의 부작용 목록**을 함께 만들어야 한다.
- **워커화 대상 목록은 실측 없이 만들면 과대추정된다.** 부록 8-5 의 6행 중 순위 5 는 재판정으로 폐기(이미 워커 안 6/7 + 이득 없는 1), 순위 6 은 별 티켓([#283](https://github.com/NumeRealWorks/DashOpti_GUI/issues/283))을 만들었다가 전수 실측 후 흡수(live 4곳은 동반 이동 · 1곳 dead · CSV 는 이미 워커)됐다. "무거워 보이는 작업" 을 세는 것과 "GUI 스레드에서 실제로 도는 작업" 을 세는 것은 다르다.
- **직렬 풀 하나가 종료 정책의 빈도를 바꾼다.** `waitForAllSerialPools` 의 상한은 원래부터 완료 대기가 아니라 **포기 판정**(초과 시 `_Exit(1)`)이다. 풀을 더하는 것은 새 실패 모드가 아니라 **빈도 승격**이고, 결과 처리는 모핑 배치보다 훨씬 흔해 예외가 상시가 된다. [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 이 "풀 추가는 드레인 예산의 재판정 대상이 아니다" 를 규약으로 올린 이유이며, 실해악을 줄이는 것은 예산이 아니라 **워커가 디스크에 쓰지 않는다는 계약**이다. 그리고 그 수용 범위가 실측으로 확정됐다 — DPF 에 협조적 취소·라이선스 반납 표면이 없으므로 `_Exit` 상시화가 유일한 답이고, 남는 실해악은 **라이선스 미반납 하나**다.

### 3차 파동의 발견

- **동기 리팩터를 Phase 0 으로 분리하면 회귀의 출처가 좁혀진다.** [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) Phase 0 은 `processEvents` 를 하나도 줄이지 않고 동작도 바꾸지 않으면서, 워커 진입을 막던 선결 조건 6건과 게이트 자기충돌 요인 3건을 닫았다. 회귀 위험이 0 이라 리뷰만으로 검증되고, 그 뒤 나온 회귀 4건은 전부 "워커화 자체가 만든 것" 으로 판정할 수 있다. **비동기 전환에서 계획 외 비율을 낮추는 가장 값싼 수단**이 이 분리다 — 1차의 [#208](https://github.com/NumeRealWorks/DashOpti_GUI/issues/208)(계획 외 10항)이 이것을 하지 않았던 티켓이다.
- **"N벌을 1벌로 합친다" 는 변경은 N벌이 같은 일을 했는지부터 확인해야 한다.** [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 21항 — 사슬 저장을 통합하려는데 일반 경로만 `setCodec("UTF-8")` 을 명시하고 KPI 5종은 `QTextStream` 기본값(로케일)이었다. 합치면 **산출 XML 의 인코딩과 선언이 바뀐다**. 코덱을 칸 속성으로 뽑아 경로별 종전 값을 보존했다. [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) F1(같은 뜻의 판정으로 교체) · [#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265) 11항(basename vs 상대경로)과 같은 계급이고, 셋 다 **차이가 조용한 산출물 변경으로 나타나는** 부류다.
- **비동기화는 선재 결함의 순서 전제를 깬다.** [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 30항 — 콤보의 첫 `addItem` 이 미선택 항목의 스캔을 착수시키는 것은 선재였지만, 스캔이 동기이던 동안에는 `setCurrentIndex(-1)` 정리가 **항상 뒤에 왔다**. 비동기가 되자 순서가 뒤집혀 콤보 미선택인데 테이블이 남는다. "선재라서 회귀가 아니다" 는 판정은 그 결함이 **순서에 의존하지 않을 때만** 맞다.
- **busy 창을 위젯 비활성으로 표시하면 그 창 안의 상태 변화를 잃는다.** [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 27항 — "끝나면 전부 활성" 이 창 내부에서 바뀐 앱 규칙(단일 파일 모드 · Mode 미선택)을 덮었다. GUI 동기 진입점은 획득·해제가 같은 콜스택인데 그 사이에 모델이 시그널을 방출하므로 창 내부에 상태 변화가 실재한다. 정해는 **진입 시점 enabled 의 스냅샷-복원**이고, 이것이 게이트 3벌을 공용화로 묶을 수 없는 지점이기도 하다.
- **런타임 테스트는 "잘못된 사용이 실패함" 을, `static_assert` 는 "잘못된 사용이 존재할 수 없음" 을 보인다.** [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 33항이 `Reservation` 발급 경로를 `static_assert` 5개로 봉인했다. 게이트처럼 **주 실패 모드가 "빠뜨림" 인 기제**에는 후자가 맞는 층위다 — [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 가 `const Witness&` 인자로 컴파일 에러를 만든 것과 같은 방향이고, 둘 다 테스트가 아니라 타입으로 계약을 세운다.
- **인프라가 서면 두 번째 소비자의 비용은 절반이 아니라 그보다 작다.** [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214)+[#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 가 게이트 기제를 세우는 데 계획 외 13항을 썼는데, [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 이 같은 기제를 두 번째 서브시스템에 복제하면서 **게이트 관련 회귀는 0** 이었다. 반면 남은 회귀 4건은 전부 그 서브시스템 고유의 것(위젯 enabled 규칙 · 공유 인스턴스 소멸 · 코덱 · 콤보 순서)이다. 재사용되는 것은 **기제**이고, 재사용되지 않는 것은 **그 기제가 만나는 UI·수명 규칙**이다.

## 추가 수정 항목 — 신규 발견분

"부록 8 전수 목록 대조" 의 잔여 8건은 **계획에 있던 것이 아직 안 된 것**이고, 아래는 구현들이 **새로 드러냈거나 범위 밖으로 밀어 둔 것**이다. 담당 티켓이 붙은 것만 표기한다.

### #207\~#210 발견분 (2건 미해소 · 4건 해소)

- [ ] **Step 2(Journal) 대기 상한** — 규약 E4("응답을 기다리는 모든 구간에 상한") 위반. [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) 에서 Q2 로 제외됐고 담당 미정이다. `DashManager::enqueueLaunch` 의 `!m_journalDaemon` 무음 반환으로 빠지면 배치가 `Analysis` 에 갇히고 Stop 버튼만 탈출구다. [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) 가 stage 1 에 케이스 상한(300s 선점 워치독)을 세우면 **stage 2 가 상한 없는 유일한 구간**으로 남는다.
- [ ] **`status_cancelled.svg` 리소스 추가** — `getStatusIcon`(`view/common/DashWidgetHelpers.cpp`)이 `Cancelled` 에 빈 아이콘을 반환. [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251)·[#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 로 `Cancelled` 표기 빈도가 늘었다(취소 시 진행 케이스를 즉시 Cancelled 로 닫는다).
- [x] ~~**`runDirectJobs` 다중 .wbpj 시 구독 전량 해제 결함**~~ — [#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265) 해소. `launchAnsysJournalDirect` 를 지우고 direct `.wbpj` 를 배치 기제(`runDirectWbpjBatch`)에 태워 인라인 `connect` 3개와 커넥션 수명 관리가 함께 사라졌다. `disconnect(…, nullptr)` 전량 해제 지점이 소멸.
- [ ] **`DashAnalysisLauncher` 의 live-path status 기록** — 실행 중 Set 을 바꾸면 snapshot 경로와 갈라진다. [#266](https://github.com/NumeRealWorks/DashOpti_GUI/issues/266) 이 이 문제를 다뤘으나 **원 범위가 데이터 모델 축임이 드러나 종결**됐고 실질 내용은 [Project-Store-Survey-Inputs-Payloads-Runtime](Project-Store-Survey-Inputs-Payloads-Runtime.md) 5.1(라이터 단일화)로 이관됐다. Track A 가 아니라 Track B 소유다.
- [x] ~~**`stopDaemon()` 의 진행 커맨드 회수 누락**~~ — [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) 해소. `stop()` 이 진행 중·대기 명령을 `commandFailed` 로 drain 한다(`212-1·4항`). 우회하던 워치독은 이중 회계가 돼 함께 정리(`212-11항`).
- [x] ~~**데몬 ready 동기 대기**~~ — [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) 해소(`212-1·3항`).
- [x] ~~**`stopDaemon()` 의 진행 커맨드 회수 누락**~~ — [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) 해소. `stop()` 이 진행 중·대기 명령을 `commandFailed` 로 drain 한다(`212-1·4항`). 우회하던 워치독은 이중 회계가 돼 함께 정리(`212-11항`).
- [x] ~~**데몬 ready 동기 대기**~~ — [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) 해소(`212-1·3항`). `454fb0f` 의 완화(15s → 30s)는 값만 남고 의미가 바뀌었다.

### #212·#213 발견분 (7건 미해소 · 3건 해소)

- [ ] **앱 종료 지연 — live 데몬 수 × 최대 5s** — 실 데몬 exe 가 stdin `exit` 를 무시한다(직접 구동해 9초 뒤에도 미종료 실측). `shutdownBlocking()` 이 `kStopTimeoutMs=5000` 을 소진하고 `kill()` 로 떨어지는 구조라 협상 시간이 순수 낭비다. **[#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 가 순서를 고쳤을 뿐 값은 그대로다** — `AppShutdown::run()` 이 데몬 종료를 정적 소멸에서 `aboutToQuit` 으로 끌어왔고 초과 시 `_Exit(1)` 로 떨어진다. 후보 ⑴ 데몬이 `exit` 를 처리(정공법 — 데몬 exe 는 별도 소유) ⑵ `killProcessTree(m_daemonPid)` 직행 ⑶ 타임아웃 \~300ms 축소.
- [ ] **실기 검증 잔여** — [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) 2건 + [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) 3건 + 2차 파동분(아래 "실기 잔여" 표). 스텁 데몬·Qt Core 하네스가 못 덮는 몫이 누적됐다.
- [ ] **`stopTraining()` 의 의도적 중단이 실패 로그를 남김** — 상태는 이미 `Interrupted` 인데 `Daemon command failed: Daemon stopped before command finished.` 가 사용자 로그에 뜬다. "무음 실패 금지" 와의 트레이드오프이므로 표시 문구 층위에서 처리할 것.
- [ ] **`model/DashJobRunner.cpp` 잉여 `setNxBaseDir` + `tryStartIfConfigured` 짝** — `.prt` 분기에서 제거한 것과 동형(값 출처도 같은 `getSolverPath("NX")`). 좌표는 [#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265)·[#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 의 재편으로 이동했다.
- [ ] **`view/DashMainWindow.cpp` 무검사 역참조** — 검증된 `nx` 대신 `DashManager::Mgr()->solverNxCad()` 를 재조회해 앞선 null 가드가 실효화됨.
- [ ] **`controller/DashExtensionProcess.cpp:6` dead include** — `#include <QDeadlineTimer>` (선재, base 에서도 미사용).
- [x] ~~**`DashMorphingUtils::performMorphingAndExport` 의 죽은 `morphOperator` 인자**~~ — [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 가 `busy()` 검사를 지우며 부분 해소했고, **[#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281) Phase B1 이 인자를 시그니처에서 삭제**한다(`interaction` 과 함께). 두 호출부의 `createMorphOperator`·`delete morphOp` 도 그때 사라진다.
- [ ] **프리뷰·산출 마커 밀도 불일치** — 고정점 포아송 간격이 프리뷰 `spacing=8.0`, 배치·산출 `20.0`. 같은 커널 반경에서도 두 경로 형상이 완전히 일치하지 않는다.
- [x] ~~**`~DashProjectManager()` 의 의도적 미해제**~~ — [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 7항이 근본안을 실행했다. 데몬 회수를 `shutdownDaemons()` 로 분리해 `aboutToQuit`(정적 소멸보다 앞)에서 돌리고 소멸자는 멱등 백스톱으로 축소했다 — `~DashManager()` 백스톱은 `run()` 이 아니라 `shutdownDaemons()` 만 다시 부른다(정적 소멸에서 풀 배수·`_Exit` 를 돌리지 않기 위해).
- [ ] **Debug 구성 빌드 불가** — `external/DashGizmo/lib/DashGizmo.lib` 가 Release 전용(`/MD`, `_ITERATOR_DEBUG_LEVEL=0`) → `LNK2038`×4 → `LNK1319`. 벤더에 Debug 라이브러리 요청이 유일한 정공법이고, 대안은 RelWithDebInfo + `QT_FORCE_ASSERTS`. `DASH_ASSERT_MAIN_THREAD` 와 [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 의 신규 `Q_ASSERT` 3종을 앱에서 발동시켜 보려면 이 구성이 필요하다(`tests/` 는 별 타깃이라 `ctest -C Debug` 가 돈다).

### 2·3차 파동 발견분 (11건 미해소 · 2건 해소 · dead·인프라 별도)

**결함**

- [ ] **`setSampleStatus` 의 O(N) 상태 재작성 — 프리즈의 다음 주범** — `model/DashAnalysisLauncher.cpp` 가 케이스 전이마다 DOE JSON 전체 read → 파싱 → 전 샘플 선형 탐색 → `toJson(Indented)` 재작성을 한다. `caseStatusUpdated` 에 **direct 연결**이라 `setStageState` 의 emit 스택 안에서 GUI 스레드 동기 실행된다. 전이 횟수가 늘지 않아도, **전이를 시간축에 흩어 놓던 블로킹이 사라지면 이 비용이 노출**된다(`runs498` 규모). `monitorMotionLauncherOutput` 이 같은 파일을 독립 파싱하므로 완료 1건당 2회. DoD 3종에 잡히지 않는다.
- [ ] **DOE JSON 이중 기록** — `setStageState` 의 `DashDoeConfigManager` 기록과 `DashAnalysisLauncher::onCaseStatusUpdated` 의 `setSampleStatus` 가 겹쳐 전이당 2회 재작성. 종전 동작의 합집합이라 회귀는 아니다. "설정 파일이 실행 상태 저장소를 겸한다" 는 설계 문제이므로 **Track B 소유**([Project-Store-Survey-Inputs-Payloads-Runtime](Project-Store-Survey-Inputs-Payloads-Runtime.md) 5.1 · 7.2 의 10번).
- [ ] **`monitorMotionLauncherOutput` 의 직접 JSON 읽기 — 소유자 없음** — `m_doeJsonPath` 를 열어 `status_<analysisType>` 을 직접 판정한다(장부 경유 아님). [#266](https://github.com/NumeRealWorks/DashOpti_GUI/issues/266) 이 CLOSED 됐으나 이 경로는 정리되지 않았고 [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) Phase 1 은 프로세스 축만 바꿔 인수하지 않는다.
- [ ] **완료 슬롯 안의 모달** — `DashAnalysisLauncher` 가 `onAnalysisCompleted`(`QFutureWatcher` 완료 슬롯)에서 `QMessageBox` 를 띄운다. 중첩 이벤트 루프 계급이고 [#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279) view 분류 소유.
- [ ] **direct `.wbpj` 의 NX 구독 수명** — `loadPrtCompleted`/`loadPrtFailed` 구독이 배치 취소 시 해제되지 않아 지각 완료가 취소된 배치의 Journal 을 띄울 수 있다(기존 문제). 대화형 NX 로드가 in-flight 일 때 그 실패가 direct 케이스를 닫는 거짓 실패 여지도 남는다 — **[#249](https://github.com/NumeRealWorks/DashOpti_GUI/issues/249) 흡수 후보**.
- [ ] **`initializePreprocessor` 교체 분기 도달 불가** — 호출부가 전부 `!m_preprocessor &&` 가드라 솔버 타입 재판정이 죽어 있다. `.rst` 로 초기화한 뒤 `.odb` 를 선택하면 Ansys 래퍼가 Abaqus 파일을 받는다. **선결이었던 `shared_ptr` 승격은 [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 2항이 끝냈으므로 이제 다룰 수 있다** — 담당 미정.
- [x] ~~**`allProcessFinished` 가 최대 3회 방출되고 방출마다 팝업이 뜬다**~~ — [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 해소(`277-19·25항`). 방출 지점이 `closeBatch()` **한 곳**이 되어 최대 3회 → 1회. 팝업 3개 → 1개는 티켓이 선언한 의도적 UX 변경이다.
- [x] ~~**KPI 실행 중 재진입 가드가 없다**~~ — [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) Phase 0 해소(`277-4항`). 가드를 한 곳으로 모으고 KPI 경로까지 덮은 뒤, Phase 1\~4 가 그 지점을 게이트(`busyChanged` 구독 + 사전 비활성)로 교체했다.
- [ ] **워커 안의 VTK 전역 상태 — [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 이 남긴 최대 잔여 리스크** — `DashResultXmlWriter` 가 워커 스레드에서 `GetFieldOutputVtk`/`GetGeometryVtk` 로 VTK 객체를 만든다. Job-local 이라 GUI 로 넘어가지 않고 워커 도달 코드의 싱글턴·GUI 접촉은 0건으로 실측됐으나, **VTK 전역 상태(오브젝트 팩토리 · 출력 윈도우 · SMP 백엔드) 접촉 여부는 미확인**이다. [#280](https://github.com/NumeRealWorks/DashOpti_GUI/issues/280) 이 RW 등급 판정에서 남긴 유보 1건과 같은 지점이고, 오늘 이미 모핑 워커가 VTK 를 만지므로 **새로 생긴 위험은 아니다**. 런타임 검증에서 가장 먼저 볼 곳.
- [ ] **`_Exit` 시 DPF 라이선스 미반납** — `DashOptiPreprocessor 1.2.2` 에 협조적 취소·라이선스 반납 표면이 **없음**이 실측 확인됐다(`277-35항`). 종료 드레인 상한을 초과하면 `_Exit(1)` 이므로 라이선스가 반납되지 않는다. 벤더에 API 요청 여부는 별건.
- [ ] **FEM 파싱 중 Browse 재클릭이 이미 성립한다** — `TopOptPostprocessDialog` 의 `processEvents` 4곳이 `ExcludeUserInputEvents` 없이 입력을 배달해, 라벨=파일B / grid·체크박스=파일A 로 갈린 상태에서 **두 파일을 섞은 솔버 JSON** 이 만들어진다. 무표시로 끝나는 조용한 오답이다. [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) Phase 2 가 pump 제거와 **짝으로** 단일 실행 가드를 넣는다.
- [ ] **Optimizer/ModelRunner 실행이 사용자 live 핸들을 덮는다** — `loadHandlesFromVtp(vtpPath, interaction)` 이 GUI live 인터랙션의 핸들을 통째로 교체하고 직후 `performMorphingAndExport` 가 내부 스냅샷으로 그것을 다시 읽는다 — **live 객체가 전송 버퍼**다. 동기라 크래시는 없는 조용한 상태 오염. 배치 경로는 이미 자기 사본에만 싣는 정해를 갖고 있다. [#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281) Phase B1 이 소멸시킨다.
- [ ] **프리뷰 ON 상태에서 QC 를 실행하면 공유 엔진이 덮인다** — QC 의 `SetInitialHandles` 가 프리뷰 엔진을 덮고 두 포인터를 되돌리는 곳이 프리뷰 off 분기뿐이라, 이후 프리뷰가 QC 구성으로 모핑할 것으로 보인다(정적 추적). [#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281) Phase B2 가 수동 재현 1회로 확인하고 성립하면 버그 수정으로 기록한다.
- [ ] **`m_analysisActive` 는 `setModel` 재호출로 리셋되지 않는다** — 해석 중 프로젝트를 바꾸면 Start 가 잠긴 채 남는다. 종전 코드도 같은 동작이라 회귀는 아니다.

**dead code · 잔재** (담당 확정)

- [ ] `DashJobRunner::createRunsFolders` — 호출부 0건 · pE 1곳 보유 → **[#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279) Phase 2**. `DashAnalysisLauncher::createRunsFolders` 는 pE 미보유라 무접촉
- [ ] `DashDataProcessorWidget::runKpiAutoTest` — 호출부 0건 · pE 3곳 보유 · **`--test-kpi` 인수 파싱 자체가 부재**(`main.cpp` 에 `QCommandLineParser` 없음)라 도입 시점부터 실행 불가 → **[#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279) Phase 2**
- [ ] `DashManager::MorphFromDoeDirectory`(81줄) · `DashDoeConfigManager::saveDoeToCsv`(102줄, 살아있는 동명 함수의 중복 구현) → **[#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281) Phase A**. 전자는 `tryClaim()`·`ExecuteOneSample`·VTU 쓰기를 함께 들고 나가 게이트 호출부가 7 → 6곳이 된다
- [ ] `applySurfaceExtraction`(호출부 0건) · `validateGenerateInputFileParams`(참조 0건, slot 아님) · `DashBatchContext::canonicalPath` write-only · `generateInputCases` 의 `rawSamples` 미사용 → 담당 미정([#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) dead 함수 목록). `DashResultProcessor::processSamples` 의 죽은 지역변수는 [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 이 그 함수를 워커로 옮기며 함께 정리됐다

**인프라**

- [ ] **`CMakeLists.txt:63` `GLOB_RECURSE` 에 `CONFIGURE_DEPENDS` 없음** — 소스가 추가되면 stale 빌드 트리가 링크 에러를 낸다([#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264) 착수 시 `LNK2019` 10건으로 실현). `CONFIGURE_DEPENDS` 추가 또는 명시적 소스 목록이 후보.
- [ ] **`waitForAllSerialPools` 의 상한 분배** — 이제 **세 풀**이 상한 하나(3s)를 나눠 쓰므로 앞선 풀이 예산을 다 쓰면 뒤 풀이 `waitForDone(0)` 을 받아 즉시 초과 판정된다. [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 은 "풀마다 상한을 주면 최악 대기가 풀 수만큼 늘어난다" 를 근거로 분배를 유지했고, 최소 보장 필요 여부는 rw 풀 첫 소비자가 생기는 시점의 판단으로 남았다([#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 리뷰 보류 항목). 초과 시 `_Exit(1)` 이므로 **결과 처리처럼 흔한 작업이 풀에 오르면 예외가 상시가 된다** — 실해악을 줄이는 것은 예산이 아니라 "워커가 디스크에 쓰지 않는다" 는 축 한정 계약이다.
- [ ] **`XML 포맷 분리 + per-sample Job 전환`** — 현 포맷은 샘플마다 메시 전체를 반복 기록하는데 소비처는 샘플당 스칼라 1개만 쓴다(`connectivity` 는 DOE 전 샘플 동일해 완전 중복). [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 이 **per-sample 전환 계약 5항목을 코드로 세워** 뒀으므로(페이로드 채널 · GUI 소유 저장 · 샘플 루프 경계 취소 폴링 · `ProgressSink` · 증명 값 이동) 남은 작업은 ⑴ 샘플 루프를 Job 연쇄로 펼치기 ⑵ 샘플별 장부 칸 신설 둘이다. 포맷 분리 후보 3개가 모두 "샘플마다 산출물" 을 요구하므로 같은 티켓에서 처리한다.
- [ ] **`BatchRunner` 추출 검토** — [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) 완료 시점에 DOE 배치 골격이 **4곳** 공존한다(`runWbpjDoeAsync` · `runNextStpCase` · `runNextMorphSample` · `runNextPostMorph`). 배열형 상태 인코딩은 `DashBatchLedger` 가 이미 세웠으므로 추출 대상은 **골격·정책뿐**이다. [#269](https://github.com/NumeRealWorks/DashOpti_GUI/issues/269) 와 범위를 먼저 가른다.

> **별 티켓 없이 폐기로 판정된 것 4건** — `cancel(id)` · R5=E1(상속→합성)([#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) 절) · 부록 8-5 순위 5(export/serialize 워커화, [#280](https://github.com/NumeRealWorks/DashOpti_GUI/issues/280) 재판정) · 게이트 3벌 공용 기제 추출([#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277)·[#280](https://github.com/NumeRealWorks/DashOpti_GUI/issues/280) 이 **3벌 유지로 확정**, 재검토 조건은 네 번째 게이트 또는 CAS 의미론이 실제로 갈리는 버그).

### 실기 잔여 — 자동화가 원리적으로 못 덮는 것

| 항목 | 소유 | 자동화 불가 사유 |
|---|---|---|
| `.vtu` 파라미터 정합(배치 중 프리뷰 시도 후 산출 형상) | [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214)·[#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) | 주 실패 모드가 크래시가 아니라 **조용한 오형상** — "안 죽었다" 를 통과 기준으로 쓸 수 없다. 골든 파일 하네스가 있으면 가능 |
| 모핑 중 앱 종료 — 고아 데몬 0 · 고아 스레드 0 · 타임아웃 내 종료 · 사유 로그 flush | [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) | 실 데몬 4종 + 실 DLL 필요 |
| `releaseRunResources` 진입 assert 의 순서 위반 검출 | [#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) | 의도적 위반 1회 주입이 필요하고 Debug 구성이 안 서므로 RelWithDebInfo + `QT_FORCE_ASSERTS` |
| direct `.wbpj` 다건 실행 · `launchId → 케이스 집합` 귀속 | [#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265) | `launchWbpjJournal` 이 VTK 의존 클래스 안 — 순수 함수로 떼기 전에는 불가 |
| H3 재현 조건 Start 복구 · 솔버 미초기화 시 입력 파일 생성 유지 · 케이스 표·로그 갱신 · 취소 시 Start 해제 시점 | [#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264) | GUI 런타임 |
| 진입점 6곳의 실제 거부 (게이트 술어 호출 6줄) | [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) | 앱이 단일 exe 라 링크할 대상이 없다. 게이트 술어 자체는 `tst_morphing_gate` 가 봉인 |
| DOE 회귀 표면 조합(`isDfsxml` × `hasMorphing` × `conditionOnly` × dfsxml/dat/inp + 비모핑 폴백 2종) | [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) | 실 DOE 프로젝트 데이터 |
| NX `.prt` 최초 열기 프리즈 소멸 · condition-only DOE · RBF 커널 반경 | [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212)·[#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) | 실 NX 설치 |
| 출력 XML 바이트 동등(`fc /b`) — 일반 결과 처리 · KPI 5종 | [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) | **픽스처 프로젝트(고객사 데이터)가 레포에 없어 기준선 캡처 자체가 불가.** 골든 기준선은 `b579bcf` 체크아웃으로 사후 캡처 가능 |
| `LGE_CompSpring`(SideForce·ModalFreq) · `ILJIN_TensionLink`(3종) 런타임 · 모핑 배치 중 결과 처리 완료·프리뷰 비활성 · 방출 팝업 1회 | [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) | 빌드 타깃별 실행 + 실 프로젝트. `BUILD_TARGET=Dev` 컴파일은 전 플래그 ON 이라 1회로 족하지만 **실행은 타깃별로 필요** |
| 워커 안의 VTK 전역 상태 접촉 | [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) | 정적 근거로는 판정 불가 — 접촉이 있어도 대개 조용하다 |

**패턴이 하나 있다** — 이 11행 중 6행의 사유가 "`DashManager.h` 가 `vtk*.h` 를 끌어와 테스트 타깃에 못 들어간다" 또는 "앱이 라이브러리가 아니라 단일 exe 다" 다. 실기 잔여를 줄이는 근본안은 개별 테스트를 늘리는 것이 아니라 **controller/model 을 정적 라이브러리로 분리하는 CMake 재구성**이고, [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) Follow-up 5 가 그것을 지목한다.

**두 번째 패턴은 픽스처의 부재**다 — [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) 의 DOE 회귀 표면 조합, [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 의 XML 바이트 동등이 **테스트 코드가 없어서가 아니라 입력 데이터가 레포에 없어서** 막혔다. 두 티켓 모두 "골든 기준선을 사후 캡처 가능" 이라고 적어 뒀으므로, 대표 프로젝트 1건을 픽스처로 확보하는 것이 자동화 가능 범위를 가장 크게 넓히는 단일 조치다.

> 배치잡 관점에서 담당 티켓이 없던 5건 중 **3건이 처분됐다** — 배열형 N단계 상태 모델은 [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260)·[#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251)·[#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264) 가 구현, `DashMorphingDoeExecutor` 통지 표면 승격은 값 반환(`DashSampleResult`)으로 **불요 판정**, `runMotionLauncher` raw QProcess 잔존은 [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) 소유. 남은 2건은 BatchRunner 추출(위 인프라)과 **view 단계·액션 컬럼 · 개별 실행**(W11 UX). `DashMorphingDoeExecutor::Execute` 의 조기 return 3곳은 [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260) 이 `Execute` 자체를 제거하며 소멸했다.

---

## 진행 중 & 계획 — [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) 5분할

> **본 절은 2026-08-20 오전 이전 티켓 본문 기준이고 5건이 stale 하다** — [215-1-w10-f-design-decision-review-snapshot](215-1-w10-f-design-decision-review-snapshot.md) "205-2 대비 갱신된 결정" 참조. 어긋나는 항목: #280 배제 단위(경로 1개 → **경로 집합** + `covers()`·`tryExtend`) · #280 `getOrLoad` 2형 계수(6/9 → **10/5**) · #280 게이트 3벌 근거 교체 · #282 stage 1 동시 1건 근거 **2건 철회** · #279 검사 축(세 명령 → **네 명령**)과 범주 ⓸ 정의 확장. 그쪽 페이지는 착수 직전 재검토용 스냅샷이며 **정본은 각 Issue 본문**이다.

### 분할 경위

[#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215)(W10-f, 8 Phase)는 구현되지 않고 **부모 티켓**이 됐다. 두 단계로 갈라졌다.

```
#215  W10-f 워커 확산·펌프 제거 (8 Phase · model pE 38→0 목표)
   │
   ├─[1차 분할]─→ #277  P3 단독 (RST/KPI — 2,964줄 · pE 22곳 = 나머지 7 Phase 합의 2.6배)
   │              #278  P1·P2·P4·P5·P6·P8 (6 Phase · 4축 · 파일 union 14개)
   │              #279  P7 (DoD 봉인)
   │
   └─[2차 분할]─→ #278 을 **축으로** 3분할하고 close
                  #280  RW 축      (구 P2·P3)
                  #281  모핑 축    (구 P1 + 구 P5 흡수)
                  #282  프로세스 축 + view·DLL 무접촉 축 (구 P6·P8)

  #283  구 P5(VTU/VTK·CSV 쓰기) — 별 티켓으로 뽑았다가 **전수 실측 후 #281 흡수·close**
```

분할 기준이 Phase 가 아니라 **축(서브시스템)** 인 이유는 등급 2 배제가 서브시스템 단위이기 때문이다. Phase 로 자르면 한 서브시스템의 게이트 배관이 두 티켓에 걸린다.

### 티켓별 요약

| 티켓 | 축 | 소유 pE | 신설 기제 | Phase | 상태 |
|---|---|:--:|---|:--:|---|
| [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) | preprocessor (RST/KPI) | model 22 | `preprocessorSerialPool` · `PreprocessorGate` · `WorkerJob::Task` 확장 | 5 | **CLOSED** (`0320683`) |
| [#280](https://github.com/NumeRealWorks/DashOpti_GUI/issues/280) | RW (ReaderWriter 모듈) | **0** | `RwGate`(키 있는 변종) | 3 | OPEN |
| [#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281) | 모핑 (QC·Optimizer·ModelRunner) | **view 5** | 없음 — 기존 기제 위 진입점 이관 | 6 | OPEN |
| [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) | 프로세스(dfsxml stage 1·2) + FEM 파서 | **model 2 + view 5** | `backgroundPool`(범용 배경 풀) | 2 | OPEN |
| [#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279) | DoD 봉인 | **model 1 + view 3**(dead code) | 없음 — 판정·기록 | 4 | OPEN |

[#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 의 실제 변경 항목은 위 티켓 절에 있다. 남은 4건이 아래다.

### [#280](https://github.com/NumeRealWorks/DashOpti_GUI/issues/280) — `RwGate` 신설, 배제를 컨텍스트 단위로

**RW 모듈 등급이 소스 실측으로 확정됐다**(`DashOpti_ReaderWriter` @ `f5d4c59`). `ThreadingContract` 는 "벤더 문서 근거가 없어 등급 2 유지" 라 적었으나 RW 는 사내 컴포넌트이므로 판정이 가능했다.

| 질문 | 판정 | 근거 |
|---|---|---|
| 같은 인스턴스 · 두 스레드 동시 | **불안전** | 동기화 primitive 0건. `global_mesh_cache` 가 `mutable` + lazy 합성이라 **`get_data` 읽기-읽기조차 레이스** |
| 다른 인스턴스 · 두 스레드 동시 | **독립(안전)** | 팩토리 = `make_unique`(등록·캐시 없음) · 상태 전부 인스턴스 멤버 · 싱글턴 0 · 가변 전역 0 · UUID 는 결정적 UUIDv5 |
| 같은 인스턴스 · 스레드 이동(순차) | **안전** | `thread_local` 0건 |

따라서 **배제 단위가 프로세스 전역이 아니라 canonical path** 다 — `tryClaim(const QString& canonicalPath)`. 사용자 관점 결과는 한 문장이다: *모핑 샘플 루프가 도는 동안 그 배치가 쓰는 모델만 열거나 편집할 수 없고, 다른 모델과 이미 열린 모델의 표시는 정상*.

두 대안 선택이 **맞물려야 성립**한다. 증명 요구를 RW 호출 4함수 시그니처에 두면(방안 B) 누락이 컴파일 에러가 되지만 읽기까지 거부되어 조건 테이블이 빈다. 읽기 4함수를 **로드 시 캐시로 승격**하면(방안 B) 읽기가 모듈 접촉에서 빠져 거부·빈 테이블·방어코드가 전부 소멸한다. 함께 하면 모듈 접촉이 **로드 1 + 쓰기 3 = 4함수**로 줄고 넷 다 사용자가 기다릴 것을 아는 연산이라 `Witness` 인자가 자연스럽다.

- `getOrLoad` **2형 분할** — `getOrLoad(path, Witness&)`(증명 보유 6곳) / `tryGetOrLoad(path) -> LoadResult{Ok, Failed, Rejected}`(신규 획득 9곳)
- `Rejected` 는 `Failed` 와 갈라야 한다 — **거부가 위젯을 비우면 사용자의 target part 선택이 JSON 에서 영구 삭제된다**(실패 경로가 `partCombo->clear()` 이고 호출부가 곧바로 전 행을 다시 쓴다)
- `busy()`·`busyChanged` **미신설** — 키 있는 게이트라 전역 `busy` 라는 상태가 성립하지 않는다(참조파일 위젯은 행마다 파일이 다르다). 거부 UX 는 사전 비활성이 아니라 **사후 거부 + 위젯 상태 불변**
- `DashContextMutationScope`·`isMutationInProgress` 를 `RwGate` 로 **동등 교체** — 축(경로 단위)은 옳았고 형(질의)과 범위(소비자 1곳)가 부족했다
- **워커 이관은 분리했다** — `load_contents` 를 풀로 옮기는 것은 코드 이동이 아니라 `getOrLoad` 의 **반환 계약 변경**이고 그 예산이 없었다. 따라서 `rwSerialPool` 소비자는 여전히 0건이다

### [#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281) — 단건 모핑 워커화, `Claim` → `Reservation` 확장

[#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274) 가 함수 스코프 `Claim` 까지 세웠고 이 티켓이 **워커 스코프 `Reservation` 으로 늘린다**. 진입점 2 는 삭제(Claim 이 호출부로 승격되어 래퍼 소멸), 진입점 5 두 반쪽(Optimizer·ModelRunner)은 `morphingSerialPool` 이관, 진입점 4 는 dead code 삭제 → 게이트 호출부 **7 → 6곳**.

**프리뷰 축(진입점 1·1b)은 무접촉**으로 분리했다. 선행 조사가 이미 "워커 이전 대상 아님 — 메인 잔류" 로 판정했고, 프리뷰를 빼도 AC(pE 5곳 · VTU/VTP 4곳 · dead code 2곳)가 전부 유지된다 — 잃는 것은 "GUI 진입점 0곳" 문장뿐이다. 착수 판정은 Phase B2 의 계측값에 걸었다(1회 프리뷰 모핑 `< 100ms` 불필요 / `100–200ms` 선택 / `> 200ms` 필요).

**워커 진입을 막는 3중 결합**이 초판의 "금지 타입 1종" 요약보다 무겁다.

1. `DashMorphingEngine` 이 operator·커널·초기 핸들·반경을 멤버로 들고 **2콜 프로토콜**(`SetInitialHandles` → `ExecuteMorphing`)을 요구하는데, `Witness` 는 **뒤쪽 콜에만** 걸려 있고 `SetInitialHandles` 는 게이트 밖이다
2. QC 가 프리뷰 엔진을 빌려 쓴다 — 규약 4절은 배치·프리뷰 2 소유자만 상정했고 QC 는 열거돼 있지 않다
3. `loadHandlesFromVtp(vtpPath, interaction)` 이 **GUI live 인터랙션의 핸들을 통째로 교체**하고 직후 `performMorphingAndExport` 가 내부 스냅샷으로 그것을 다시 읽는다 — live 객체가 전송 버퍼다

**Phase B1(값 경계) · B2(엔진 격리)가 스레드를 만들지 않고 이 셋을 먼저 끊는다.** 부수 효과로 "Optimizer 실행이 사용자 3D 뷰 핸들을 덮는 기존 버그" 가 B1 에서 소멸한다.

구 P5(VTU/VTK·CSV 쓰기)를 흡수한 근거: 대상 쓰기 5곳 중 1곳은 dead, 1곳은 이미 워커(`saveDoeToCsv` 는 `QtConcurrent::run` 안), 나머지 4곳은 진입점 워커화와 **동반 이동**한다. 별 티켓으로 두면 순서 의존만 생긴다. **워커가 파일을 쓰는 것은 규약 위반이 아니다** — 완결 판정은 워커 반환값이 소유하고, 산출 파일의 참조(파일 테이블 행·렌더 등록)가 완료 슬롯 소유라 강제 종료 시 참조가 생기지 않는다(고아 파일로 남을 뿐).

**취소는 AC 대상이 아니다** — 이관 대상 3경로에 취소 어포던스가 없다.

### [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) — dfsxml stage 1·2 `ProcessJob` 수렴 + FEM 파서 워커화

축 2건을 한 티켓에 합친 **의도적 편차**다. 파일이 겹치지 않고 **Phase 간 선행이 없다** — Phase 1 은 선행 0 이라 [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 을 기다리지 않고 먼저 커밋할 수 있고, Phase 2 만 [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) Phase 1 의 `Task` 시그니처 확정에 걸린다.

**stage 1 의 직렬성·상한·취소가 전부 그 블로킹 대기 하나에 얹혀 있다** — 이것이 이 티켓의 핵심 발견이다.

| 성질 | 현행 근거 | 대기를 걷으면 |
|---|---|---|
| 동시 1건 | 큐드 `runNextMorphSample` 이 폴링 루프에 갇혀 디스패치되지 못한다 | 최대 샘플 수만큼 동시 기동. 스냅샷 멤버가 단일값이라 서로 덮는다 |
| 케이스 상한 | `runMotionWriter` 안에 하드코딩된 300000ms + kill | 상한 0. `m_morphWatchdog` 는 모핑 워커 국면만 덮고 `m_stpWatchdog` 는 STP 전용이라 **post-morph 를 아무도 덮지 않는다** |
| 취소 회수 | **없다.** `QProcess` 가 스택 지역이라 컨테이너에 등록되지 않아 `releaseRunResources`("취소 자원 열거의 유일한 지점")가 stage 1 을 보지 못한다 | 변화 없음 — 등록하지 않으면 결함이 이월된다 |

해법은 신설이 아니라 **`runNextStpCase` 형 복사**다 — `bctx` 값 복사(장부 재독 금지) · 전용 단발 `QTimer`(예산 300000ms 승계) · 진행 1건 게이트. job 을 runKey 별 컨테이너에 등록해 `releaseRunResources` 회수 대상이 **4종 → 5종**이 되는 것이 stage 1 취소 회수의 유일한 성립 조건이다.

stage 2 는 `ProcessJob` 수렴으로 확정했고 종전의 "`QProcess::started` 슬롯" 지시는 **철회**됐다 — `ProcessJob` 은 `m_proc` 를 노출하지 않고 `Job::started` 가 `m_proc->start()` **이전**에 뜨므로 두 지시가 양립 불가다. 기동 실패는 `Job::finished(Failed)` 로 비동기 도착하므로 `runMotionLauncher` 가 `void` 가 되고 bool 분기가 완료 슬롯으로 옮겨간다. 결과로 **`DashJobRunner.cpp` 의 `QProcess::waitFor*` 가 0곳**이 된다.

FEM 파서(705줄)는 **범용 배경 풀**(`backgroundPool`)로 간다 — 전용 `femParsePool` 안은 재판정으로 기각됐다. 직렬 풀의 정의가 "등급 2 DLL 서브시스템당 1개" 인데 FEM 파서는 **DLL 무접촉**(순수 텍스트 + VTK)이라 배제할 서브시스템이 없고, 전용 풀을 세우면 규약 정의가 흔들리며 같은 부류마다 풀이 늘어 종료 드레인 예산을 잘게 나눈다. 병렬·out-of-order 차단은 **활성 파싱 Job 1개 불변식**이 소유한다. 파서를 **익명 namespace 자유 함수**로 떼는 것도 규약이다 — 705줄을 멤버 함수 람다로 감싸면 암묵 `this` 캡처를 컴파일러가 막지 못한다.

**범위 규약: 차단은 본 티켓 · 정책은 후속.** 목적은 ⑴ 동기 대기의 비동기 전환과 ⑵ 그 전환이 새로 여는 병렬 진입면의 차단 둘뿐이고, 거부된 시도의 처분(무시·큐잉·교체)과 실패·재시도·진행 표시 정책은 안전에 영향이 없어 후속으로 넘긴다.

### [#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279) — DoD 봉인

**규범이 좌표 목록에서 검사 절차로 옮겨간 것**이 이 티켓의 실체다. 종전 본문은 존치 `waitFor*` 6곳·주석 5줄·view 7곳을 줄번호로 못박고 DoD 를 "그 목록을 제외한 나머지가 0" 으로 정의했는데, 그 목록이 선행 구현 계획과 **이미 4건 어긋나 있었다**. 원인은 개별 실수가 아니라 구조다 — 마무리 티켓이 선행의 산출물을 좌표로 예측해 본문에 복사하면, 선행이 구현 중 방식을 바꿀 때마다 봉인 티켓이 틀리고 그 사실은 착수 후에야 드러난다.

**DoD = 세 명령의 전 히트가 4범주로 귀속되고 미분류 0건.**

| 범주 | 정의 | 산출물 |
|---|---|---|
| ⓵ 소멸 | 선행 또는 본 티켓이 없앴다 | 계수만 |
| ⓶ 항구 존치 | 프로덕션 경로의 의도적 동기. 상한과 근거가 있다 | 건별 근거 1줄 → `ThreadingContract` |
| ⓷ W11 인계 | 제거 대상이나 배관 신설이 W11 scope | 위치·소유 함수·필요 배관 → 인계 목록 |
| ⓸ 비실행 오탐 | 주석. 명령이 자동 식별한다 | 없음 |

계급별 추가 조건: pE 는 model 계층에 ⓵ 외 범주 0건 · ⒜ 아종 0건, 대기는 ⓷ 0건(전부 ⓶), 슬립은 전 범주 0건.

**선행 산출물을 재작업하지 않는다** — 실측이 예상과 다르면 해당 선행으로 되돌린다. 봉인 티켓이 남의 산출물을 고치면 DoD 의 의미가 사라진다.

`docs/ThreadingContract.md` 7절은 [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277)·[#280](https://github.com/NumeRealWorks/DashOpti_GUI/issues/280)·[#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279) **3자 공유**이고 이 티켓이 최종 통합자다. 그래서 풀·게이트 개수를 본문에 미리 박지 않는다 — 선행 2건이 각각 풀을 더한다.

### 선행 관계

```
[완료] #277  — WorkerJob::Task 2인자 확장 · preprocessorSerialPool · PreprocessorGate
                 └─ #282 Phase 2 의 유일한 선행이 여기서 해소됐다

지금 착수 가능
   ├─ #280 Phase 1  (RwGate 신설 — 선행 0)
   ├─ #281 Phase A  (dead code 2곳 — 선행 0 · 최우선)
   ├─ #281 Phase B1 (값 경계 — 스레드 무변경)
   ├─ #282 Phase 1  (dfsxml stage 1·2 — 선행 0)
   └─ #282 Phase 2  (FEM 파서 — #277 이 Task 형을 확정했다)

#280 (RwGate 배관)
   └─→ #281 Phase D·E  (Job 이 ExecuteOneSample 을 타 RW 를 함께 만진다 — 규약 7절)

#281 Phase A → B2 → C   (엔진 격리가 QC 워커화의 선결)
#281 Phase B1 → D · E

#281 · #282  (계수)  ┐
#280         (문서)  ├─→ #279  DoD 봉인
                     ┘
```

**파일 충돌은 코드가 아니라 문서에 있다** — `docs/ThreadingContract.md` 가 [#280](https://github.com/NumeRealWorks/DashOpti_GUI/issues/280) ∩ [#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279)(+ [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 가 이미 2라운드 개정), `view/dialog/TopOptPostprocessDialog.cpp` 가 [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) ∩ [#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279)(같은 함수), `model/DashJobRunner.cpp` 가 [#280](https://github.com/NumeRealWorks/DashOpti_GUI/issues/280) ∩ [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) ∩ [#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279)(구역 분리), `view/DashModelRunnerWidget.cpp` 가 [#280](https://github.com/NumeRealWorks/DashOpti_GUI/issues/280) ∩ [#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281)(구역 분리)로 겹친다. 초안의 "네 티켓 모두 병행 가능" 은 **코드에만 참**이었다. [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) ∩ [#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279) 의 `view/DashDataProcessorWidget.cpp` 는 [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 이 먼저 랜딩해 해소됐고, [#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279) 는 그 파일에서 `runKpiAutoTest`(dead) 삭제만 남았다 — 좌표는 이동했다.

### 게이트 3벌 — 공용 기제 추출은 기각됐다

`MorphingGate`([#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274)) · `PreprocessorGate`([#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277)) 는 **머지됐고** `RwGate`([#280](https://github.com/NumeRealWorks/DashOpti_GUI/issues/280))가 세 번째다. 같은 원자 워드 로직이 세 벌이 되는 시점에 공용 기제로 추출하려 했으나 **3벌 유지로 확정**했다.

| # | 근거 |
|---|---|
| ⑴ | **셋이 완전 동형이 아니다** — `RwGate` 는 키 있는 변종이라 추출하면 "키 없는 게이트 = 키가 하나뿐인 게이트" 로 일반화해야 하고, 그 일반화가 앞의 둘을 실제보다 복잡한 타입으로 만든다 |
| ⑵ | **`busy()` 표면이 게이트마다 다르다** — `MorphingGate` 는 소비자 3곳, `PreprocessorGate` 는 신설, `RwGate` 는 없음. 공용 베이스에 올리면 셋 중 둘에 미사용 API 가 생긴다 |
| ⑶ | **이득이 원자 워드 \~50줄 중복 제거뿐**이고, 세 게이트가 각자 단위 테스트로 불변식을 검증한다 |

**재검토 조건**: 네 번째 게이트가 생기거나, 세 게이트의 CAS 의미론·해제 순서가 실제로 갈리는 버그가 나올 때. 판단과 조건은 [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 이 `ThreadingContract` 게이트 절에 기록했다.

그럼에도 **형은 통일했다** — `PreprocessorGate` 를 `MorphingGate` 동형 3형으로 확정한 이유가 이것이다. 검토 1차안(`shared_ptr<Claim>` 1형)은 정확성이 동일하지만 ⑴ 호출부 코드가 어차피 같고(워커 축은 어느 쪽이든 `shared_ptr` 캡처) ⑵ 이미 머지된 3형과 독자가 두 형태를 모두 알아야 하며 ⑶ 이형이 섞이면 나중에 추출이 사실상 불가능해진다.

**[#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 이 이 판단을 검증했다** — 3형 복제에서 게이트 관련 회귀가 0 이었고, `Reservation` 발급이 `Claim` 없이는 불가함을 `static_assert` 5개로 봉인했다. 반면 **재사용되지 않은 부분은 거부 UX** 다: `MorphingGate` 는 키가 없어 사전 비활성이 정해인데 `PreprocessorGate` 쪽은 동적 enabled 3종 때문에 스냅샷-복원이 추가로 필요했고 그 차이가 회귀 2건을 냈다. `RwGate` 는 **키가 있어** 또 다르다 — 사후 거부 + `Rejected` 구분이다. 세 게이트의 진짜 차이는 원자 워드가 아니라 **거부를 사용자에게 어떻게 보이느냐**이고, 그것이 공용화로 묶이지 않는 부분이다.

### [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) 가 자식에게 물려준 공용 판정 5건

자식 티켓이 각자 다시 정하지 않도록 부모가 확정한 것 — ⒜ **거부 UX 는 게이트 키 유무가 정한다**(키 없음 = 사전 비활성 / 키 있음 = 사후 거부 + 위젯 상태 불변) ⒝ 게이트 형은 `Claim` + `Reservation` 2객체 ⒞ **종료 중 진행 Job 강제 종료를 수용**하고 취소 훅을 신설하지 않는다. 완결 판정은 **워커 반환값이 소유**하며 워커의 파일 쓰기를 금지하지 않는다 ⒟ 워커→GUI 반환 규약을 전역화한다([#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 이 형식을 세우고 나머지가 따른다) ⒠ DoD 는 현행 3축 유지, 중첩 `exec()` 는 각 자식이 자기 함수에서 확인.

---

## 별건 — 이 브랜치의 릴리스 창과 분리된 것

### [#249](https://github.com/NumeRealWorks/DashOpti_GUI/issues/249) — NX CAD 파사드 통지 일반화

[#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) 이 배치 전용 시그널 2종을 증설한 **이유 자체**를 없애는 티켓이다. 파사드가 상위(`commandCompleted(commandId, …)`)가 준 요청 식별자를 버려서 **하위 계층이 상위보다 정보가 적다.**

| 하자 | 근거 | 결과 |
|---|---|---|
| 대칭 붕괴 | 성공은 경로별 둘, 실패는 하나로 합쳐짐 | `loadPrtFailed` 가 update 실패에도 발화 |
| 식별자 손실 | `onCommandFailed` 가 `commandId` 를 **동사 판별에만** 쓰고 경로는 버린다 | 실패 수신자가 귀속 판별 불가 |
| 송신자 모드 의존 | `m_batchMode` 읽기 2곳 · on/off 2곳 | 요청 단위가 아니라 전역이라 **배치 중 대화형 요청이 끼면 오억제** |
| 구독자 성격 가정 누출 | 억제 판단에 "구독자가 미리보기·모달을 띄우는 뷰" 라는 전제 | controller 가 view 동작을 안다 |

**실어야 하는 것은 "어느 파일" 이 아니라 "어떤 의도의 요청인가"** 다. `stpPath` 만으로는 부족한데, 브로드캐스트 핸들러가 **남이 낸 요청을 대신 받기** 때문이다 — 요청 지점 5곳 중 2곳(`DashGeometryParameterCADWidget` · `DashOptimizerWidget`)은 자체 구독이 없어 `DashMainWindow` 가 완료를 처리한다. 해법은 `enum class NxCadRequester{Interactive, Batch}` 를 `enqueue*` 인자로 받아 `commandId` 에 싣고 완료·실패에 되돌려주는 것이고, **대칭 4종 시그널을 무조건 방출하고 필터는 구독자 몫**으로 옮긴다.

사라지는 것: `m_batchMode`/`setBatchMode()` · `updatePrtGeometryBatch{Completed,Failed}` · `emitFailure()` · `loadPrtFailed` 의 update 겸용.

**규모** 8파일 / 순변경 65\~80줄 / 3 Phase — **분할 불가**(시그니처 변경 순간 구독자 4곳이 동시 파손되고 빌드가 서는 중간 상태가 없다) → 한 커밋.

**위험 성격**: 시그니처 불일치는 PMF connect 로 컴파일 에러가 되지만 **필터 오조건 = 대화형 기능의 조용한 사망**(미리보기 로드·파일테이블 등록·실패 모달)이다. **NX 환경 수동 회귀 4\~5케이스가 하드 게이트**이고, 이것이 이 티켓을 별건으로 미룬 결정적 이유다 — 코드가 아니라 환경에 묶인다.

2차 파동이 이 티켓에 남긴 델타 3건.

- **원칙 2종의 선례가 섰다** — "하위가 판정한 정보를 상위로 전달"·"통지 대칭" 은 경로 무관 원칙이고 [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260)(값 반환 `DashSampleResult`) · [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251)(실패에 `stpPath` 동반) · [#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265)(`launchId → 케이스 집합`)가 이미 구현·검증했다. 본 티켓에 남는 것은 **NX 파사드 고유 기제 2종**(요청 태그 왕복 · `m_batchMode` 제거)이다.
- **[#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) 선행이 성립했다** — Phase 3(`DashJobRunner`)은 슬롯이 이미 `귀속 → 전이 → advance()` 3단이라 **"태그 필터 한 절 추가" 로 축소**된다. D3(실패 시그널에 `stpPath`)는 버려지지 않고 태그 필터로 승계된다.
- **소비자가 3종이 될 조건이 사라졌다** — [#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265) 가 direct `.wbpj` 를 DOE 와 **같은 배치 기제**에 태워 `launchAnsysJournalDirect` 를 지웠다. "소비자가 3종이 되면 같은 증설이 반복된다" 던 위험이 당장은 실현되지 않는다 — 다만 그 대가로 direct 의 NX 구독부가 본 티켓 완료 후 **한 번 더 바뀐다**(요청 태그 방식으로).

### [#269](https://github.com/NumeRealWorks/DashOpti_GUI/issues/269) — `DashJobRunner` 워크플로 분기 해체

`generateInputCases` 한 함수가 **562줄**에서 워크플로 4종(FE-safe `.stli` / NX CAD `.wbpj` / 모핑 / 폴백)을 분기하고, `runDirectJobs` 가 같은 솔버들을 별도로 다룬다. 문제는 길이가 아니라 **계약을 강제하는 구조가 없다**는 것이다 — 워크플로가 추가될 때마다 그 경로가 착수·상태보고·종결을 각자 다시 구현했다.

| 시점 | 무슨 일이 있었나 |
|---|---|
| FE-safe 추가 | 자기만의 상태 기록 — `configManager.setSampleStatus` 직접 호출 |
| Direct Launcher 추가 | 자기만의 종결 — `launchAnsysJournalDirect` 가 `jobFinished` 직접 방출 |
| [#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251) 모핑 장부 도입 | 나머지 경로가 안 따라옴 → **[#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264)** 가 뒤늦게 수습 |
| — | 같은 제출 코드가 ANSYS 3벌 · Abaqus 2벌 → **[#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265)** 가 수습 |

**[#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264)·[#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265) 는 계약을 세우고 중복을 지웠으나 계약을 강제하지는 않는다** — 다섯 번째 분기를 붙이면 그 경로도 장부·종결·상태 보고를 처음부터 다시 짠다. 검토할 방향 2안(착수 시 비교): ⑴ **워크플로 전략 분리** — 각 워크플로를 "입력 준비" 인터페이스 구현체로 빼고 착수·상태보고·종결은 공통 러너가 소유 ⑵ **함수 분해만** — 클래스 구조 유지, 비용이 낮고 강제는 약하다. `DashBatchLedger` 가 상태 축을 분리해 낸 선례이므로 **같은 방식으로 실행 축을 분리할 수 있는지가 판단 지점**이다.

선결 [#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264)·[#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265)(둘 다 머지 완료) · [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214)·[#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215)(파일 표면 겹침 — [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 완료, [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) 계열 진행 중). **[#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) 완료 시 배치 골격이 4곳**이 되므로 BatchRunner 추출과 범위를 먼저 가른다. [#246](https://github.com/NumeRealWorks/DashOpti_GUI/issues/246)(W20 God-object 해체)의 대상 목록에 `DashJobRunner`(3,289줄)가 빠져 있어 이 티켓이 보완한다.

**2026-09-28 착수** — 방향 ⑵ 함수 분해 채택, 케이스별 TU 6개로 분리. 설계 상세: [269-1-jobrunner-case-decomposition-design](269-1-jobrunner-case-decomposition-design.md).

### Track B — 데이터 계층 ([Project-Store-Design-Layer-Cut](Project-Store-Design-Layer-Cut.md) 파생)

[#266](https://github.com/NumeRealWorks/DashOpti_GUI/issues/266)("`AnalysisLauncher_Set{N}.json` 이 설정 파일이면서 실행 상태 저장소를 겸한다")은 **종결**됐다. 근거 3건: ⑴ 티켓의 2안 중 하나(별도 파일 분리)가 ModelBuilder 의 외부 도구 계약에서 막히는데 티켓이 그 사실을 모른다 ⑵ Track A 좌표(`refactor/async-execution`, [#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264) 관계)에 등록돼 있으나 문제는 비동기가 아니라 데이터 모델이고, 그대로 두면 **Track A 릴리스 창에 끌려 들어간다** ⑶ 실질 내용이 문서 Step 1 로 보존되고 티켓에 없던 사실 4건이 추가됐다.

전수 측정이 밝힌 것은 **문제가 하나가 아니라 셋**이라는 점이다.

| 문제 | 내용 | 범위 |
|---|---|---|
| A | 설정 파일이 실행 상태를 겸한다 (이중 쓰기 · direct 실행이 선택된 Set JSON 오염 · `"Enqueued"` 리셋 · 리더 3곳) | AnalysisLauncher — [#266](https://github.com/NumeRealWorks/DashOpti_GUI/issues/266) 원 범위 |
| B | **외부 도구 양방향 IPC** (신규 발견) — DeepOpt·MCU 가 config JSON 에 `Done` 을 직접 쓰고 GUI 가 1초 폴링으로 읽는다 | 도구 계약 개정 필요 → 규약(5a, 본 저장소) / 구현(5b, **별건**)으로 분할 |
| C | `*_datapath` 필드 — 산출물 포인터가 설정에 섞여 있다 | 3모듈 |

**Track A 와 겹치지 않게 배치한다** — [Project-Store-Design-Entity-Model-Options](Project-Store-Design-Entity-Model-Options.md) 이 정한 "테스트 없는 상태에서 코드 구조 축과 데이터 구조 축을 동시에 바꾸지 않는다" 가 그대로 적용된다. 착수 승인 시 Step 1\~5a 를 티켓 6개(B-1 \~ B-6)로 분할하는 초안이 문서에 있다.

**종결로 남는 것 2건은 의도적 수용이다** — direct 실행이 선택된 Set JSON 을 오염시키는 것(평문 `"status"` 키만, 파급 제한적) · 전이당 JSON 쓰기 2회와 표 재구축 최대 2회(성능·깜빡임, 기능 결함 아님). 다만 후자는 **[#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) 가 stage 1 의 블로킹을 걷으면 노출된다** — 전이를 시간축에 흩어 놓던 대기가 사라져 `setSampleStatus` 의 O(N) 재작성이 프리즈로 보이기 시작하고, 그 시점에 Step 1 만 별도 티켓으로 먼저 뽑는 판단이 필요하다.

미결 2건: `.state.json` 스키마를 모듈 공통으로 할지(`DashBatchLedger` 가 이미 그 모양이라 직렬화만 추가하면 된다) · Step 5a 의 통지 방식(파일워처 vs stdout 프로토콜).
