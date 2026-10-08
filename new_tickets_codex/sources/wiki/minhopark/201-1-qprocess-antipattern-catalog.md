# DashGUI2 QProcess 안티패턴 카탈로그 — 시그널/슬롯 우회 지점 전수 (패턴 축)

> 원본: 사전조사 Issue #201 — 본문을 이 페이지로 이관한 뒤 Issue 삭제 (2026-08-24). **본 페이지가 정본**

> 연관 Issue: #64 (Crash Debug — 재진입 크래시 계급의 원천인 실행 모델)\
> 기반 문서: [[194-1-async-execution-patterns]] — 같은 대상의 **위치·우선순위 축** 목록(2-2절). 본 문서는 동일 실측을 **패턴 축**으로 재편성하고 지점을 전수 보강한 카탈로그\
> 자매 문서: [[193-1-async-execution-models]] (개념 해설) · [[195-1-backlog-code-evidence]] (W6·W10 실증) · [[205-5-w6-w10-async-minimal-example]] 8장 (본 카탈로그의 종류별 요약 부록)\
> 분석 시점: 2026-07-15, 브랜치 `dev` 워킹트리 — **`controller/DashExtensionProcess.cpp` 는 수정 진행 중 상태**이므로 해당 파일 라인 앵커는 커밋 기준과 다를 수 있음\
> 발단: 검토 질문 — "QProcess 는 시그널/슬롯으로 원래 비동기로 구동하고 메인 스레드는 항상 이벤트 루프에서 대기 상태여야 하는데, 현재 잘못 구현된 패턴은 어떤 것들이 있는가 — 모두 나열"\
> 개정 1: 2026-07-21 — 커밋 기준(`dev` `52965e4`) 재검증: 전수 집계 재확인(0절 — `waitFor*` 24→23, 나머지 불변), 8절 P7 에 view 계층 17곳 전수·아종 2분류 보강, 13절 음성 판정(조사했으나 해당 없는 프리미티브) 신설(구 13절 참고 자료 → 14절), 종류별 요약 자매 문서([[205-5-w6-w10-async-minimal-example]] 8장) 상호 링크

---

## 0. 판정 기준 — 무엇을 "잘못"으로 세나

QProcess 의 본래 계약: `start()` 는 즉시 반환하고, 이후 진행은 전부 시그널로 통지된다 — `started` / `errorOccurred(FailedToStart)` / `readyReadStandardOutput` / `finished(exitCode, exitStatus)`. 메인 스레드가 할 일은 connect 후 이벤트 루프로 복귀하는 것뿐이다.

따라서 "잘못" = **메인(GUI) 스레드의 이벤트 루프 상주를 깨는 모든 것**:

1. `waitForStarted` / `waitForFinished` / `waitForReadyRead` / `waitForBytesWritten` — 블로킹 대기. Qt 공식 문서가 GUI 스레드 사용을 직접 경고하는 API ("can cause your user interface to freeze").
2. `QThread::msleep` — 이벤트 루프 완전 정지.
3. 시그널을 무시하고 파일시스템·상태를 폴링하는 루프.
4. `QApplication::processEvents` — 정지를 가리는 대신 **재진입 창**을 연다 (실행 중 사용자 입력·타이머·다른 슬롯이 현재 스택 위에서 실행됨 — #64 크래시 계급의 원천).

전수 집계 (grep, 2026-07-15 워킹트리):

| 프리미티브 | 지점 수 | 파일 수 | 비고 |
|---|:---:|:---:|---|
| `waitFor*` (QProcess 계열) | 24 | 4 | DashExtensionProcess 11 · DashJobRunner 8 · DashModelBuilder 3 · TopOptPostprocessDialog 2 |
| `QThread::msleep` | 5 | 1 | 전부 DashJobRunner |
| `processEvents` (실행 지점) | 58 | 10 | 모델 계층 41 (JobRunner 19 · DataProcessor 14 · ResultProcessor 8) |

재검증 (개정 1 — 2026-07-21, `dev` `52965e4` 커밋 기준): `waitFor*` **23곳/4파일** — DashJobRunner 8→7(`:459, 685, 697, 712, 714, 848, 948`), 분석 시점 워킹트리와 커밋 기준의 차이. `msleep` 5곳 불변. `processEvents` 58곳 불변 — 실호출 기준(주석 라인 `TopOptPostprocessDialog.cpp:531` 제외), 구성은 model 41 + **view 17**(전수는 8절 보강).

## 1. 결론 먼저 — 패턴 8종

| P# | 패턴 | 핵심 지점 | 최대 블로킹 |
|:---:|---|---|:---:|
| P1 | 데몬 기동 동기 대기 — `waitForStarted` + ready busy-wait | `DashExtensionProcess::startDaemon` + 호출자 7곳 | 30s + 120s(NX) |
| P2 | 동기 종료·취소 — terminate/kill 후 `waitForFinished` | stopDaemon · 소멸자 4곳 · cancelAllRuns 등 | 30s |
| P3 | 기동 확인 동기 대기 — `start()` 직후 `waitForStarted` | 5곳 (시그널 구동 경로 안에도 잔존) | 30s |
| P4 | one-shot 동기 완주 대기 — `waitForFinished(전체 타임아웃)` | `runBlocking` · `runMotionWriter` · `killOrphans` | 300s |
| P5 | 완료 시그널 무시 + 파일시스템 폴링 | `waitForFile` · `waitForVtuFileComplete` | 600s/케이스 |
| P6 | 고정 슬립 추측 대기 — `msleep(1000)` | dfsxml 모핑 루프 | 1s(반복) |
| P7 | `processEvents` 재진입 — 프리즈 위장 | 58곳/10파일 | — (재진입 창) |
| P8 | 동기 반환 API 계약 — `bool startDaemon()` / `runBlocking` | API 표면 자체 | 구조적 |

P1~P6 은 "메인 스레드가 멈춘다"(프리즈), P7 은 "멈춘 채 이벤트만 돌린다"(재진입 크래시), P8 은 앞의 것들을 **강제하는 API 형태**다. P8 을 고치지 않으면 P1 은 지점 수리로 사라지지 않는다.

## 2. P1 — 데몬 기동 동기 대기

**형태**: `start()` → `waitForStarted(30000)` → `[READY]` 마커 수신까지 `waitForReadyRead(300)` busy-wait 루프.

```cpp
// DashExtensionProcess.cpp:143-159
if (!m_daemonProcess->waitForStarted(30000)) { ... }        // 블로킹 1
QElapsedTimer timer; timer.start();
while (!m_daemonReady && timer.elapsed() < m_readyTimeoutMs // 블로킹 2: busy-wait
       && ...) {
    m_daemonProcess->waitForReadyRead(300);
    onDaemonReadyRead();                                     // 슬롯 수동 호출
}
```

| 지점 | 내용 | 최대 지속 |
|---|---|:---:|
| `DashExtensionProcess.cpp:143` | `waitForStarted(30000)` | 30s |
| `DashExtensionProcess.cpp:151-159` | ready busy-wait — 기본 15s (`DashExtensionProcess.h:180`), NX 는 **120s** (`DashSolverNxCad.cpp:16`) | 120s |
| `DashExtensionProcess.cpp:97-108` | 이중 기동 가드 경로 — 동일 busy-wait 반복 | 120s |
| `DashExtensionProcess.cpp:114` | 기동 경로가 `killOrphans` 경유 — P4 의 taskkill 동기 대기 포함 | +3s |

**메인 스레드 호출자 전수** (전부 GUI 스레드 — 버튼 슬롯·enqueue 경로):

| 호출자 | 위치 |
|---|---|
| `DashSolverNxCad::tryStartIfConfigured` | `DashSolverNxCad.cpp:115` |
| `DashSolverNxCad::enqueueLoadPrt` / `enqueueUpdatePrtGeometry` — 데몬 미기동 시 **첫 enqueue 가 동기 부팅 유발** | `DashSolverNxCad.cpp:124-126, 147-149` |
| `DashManager::enqueueLaunch` — Journal 데몬 | `DashManager.cpp:157` |
| `DashModelRunner::startDaemon` — Sensitivity 데몬 위임 | `DashModelRunner.cpp:240` |
| `DashModelBuilderMCU::startDaemon` — MCU 데몬 위임 | `DashModelBuilderMCU.cpp:120` |
| 위젯 직접 호출 3곳 | `DashModelBuilderMCUWidget.cpp:193` · `DashModelRunnerMCUWidget.cpp:197-198` · `DashModelRunnerWidget.cpp:244` |

**부수 증상 2건**:

1. **시그널 동기 발화** — `daemonReady()` 가 블로킹 호출 스택 내부에서 emit 되므로 호출자는 "connect 먼저, start 나중"을 강제당한다. `DashModelRunnerMCUWidget.cpp:185` 의 주석("Connect daemonReady BEFORE startDaemon() to avoid missing the synchronous ...")이 이 왜곡의 실증이다 — 시그널이 비동기였다면 필요 없는 방어.
2. **수신 경로 이중화** — `readyReadStandardOutput` 은 슬롯에 connect 돼 있는데(`:135-136`), busy-wait 루프가 같은 슬롯을 수동 호출(`:105, 158`)한다. `readAllStandardOutput` 이 멱등이라 사고는 안 나지만, 시그널 구동과 폴링 구동이 한 객체 안에 공존하는 설계 냄새.

**올바른 형태**: `start()` 후 즉시 반환 → `daemonReady` 시그널 수신 시 큐 flush (이미 `handleDaemonLine:256-260` 에 그 경로가 있다 — busy-wait 는 이를 기다려주지 않고 앞질러 가는 것). 미기동 상태의 `sendCommand` 는 이미 큐잉되므로(`trySendNext:209`), 기동을 비동기화해도 명령 유실이 없다. 상세 설계: 기반 문서 7절 서브태스크 c.

## 3. P2 — 동기 종료·취소

**형태**: `terminate()`/`kill()` 후 `waitForFinished(N)` 로 프로세스 사망을 블로킹 확인. 종료는 이미 `finished` 시그널로 통지되는 사건이다.

| 지점 | 내용 | 최대 지속 |
|---|---|:---:|
| `DashExtensionProcess::stopDaemon` (`:178-183`) | `write("exit")` → `waitForBytesWritten(1000)` → `waitForFinished(5000)` → `kill` → `waitForFinished(2000)` | 8s |
| `DashExtensionProcess` 소멸자 (`:18-21`) | 위 stopDaemon 을 소멸 경로에서 호출 — 앱 종료 시 데몬 수만큼 직렬 누적 | 8s×N |
| `DashExtensionProcess::runAsync` (`:379-384`) | 새 one-shot 시작 전 이전 프로세스 `kill` + `waitForFinished(2000)` | 2s |
| `DashModelBuilder::stopTraining` (`:1237-1243`) | `terminate` → `waitForFinished(3000)` → `kill` → `waitForFinished(3000)` | 6s |
| `DashJobRunner` 소멸자 (`:455-462`) | motion 프로세스 루프: `kill` + **`waitForFinished()` 인자 없음 = 기본 30s**/프로세스 | 30s×N |
| `DashJobRunner::cancelAllRuns` (`:946-948`) | `kill` + `waitForFinished(3000)` 루프 | 3s×N |
| `DashJobRunner::runMotionWriter` 타임아웃 경로 (`:711-714`) | `kill` → 실패 시 `terminate` → 재대기. **에스컬레이션 방향 역전** — kill(최강) 실패 후 terminate(약한 수단)로 강등하는 순서 오류 포함 | 10s |
| `TopOptPostprocessDialog` 소멸자 (`:2155-2157`) | `terminate` + `waitForFinished(3000)` — 다이얼로그 닫기 정지 | 3s |

**올바른 형태**: terminate/kill 은 발사 후 즉시 반환하고, 정리(`deleteLater`·상태 갱신)는 `finished` 슬롯에서. 사용자에게 약속하는 것은 "취소 = UI 즉시 해방"이다 (기반 문서 4-1절 P4 정책). 소멸 경로에서는 `kill()` + OS 에 회수 위임(또는 detach)으로 충분 — 앱 종료를 프로세스 사망 확인으로 볼모 잡지 않는다.

## 4. P3 — 기동 확인 동기 대기 (`start()` 직후 `waitForStarted`)

**형태**: 이후 흐름은 시그널 구동인데 기동 확인만 블로킹으로 한다. `errorOccurred(FailedToStart)` 시그널이 정확히 이 용도의 비동기 통지다.

| 지점 | 타임아웃 | 비고 |
|---|:---:|---|
| `DashModelBuilder.cpp:637` | 10s | 주석 "Python 실행 파일 로딩 시간 고려" 는 오해 — `waitForStarted` 는 OS 프로세스 생성까지만 보고 인터프리터 로딩과 무관 |
| `DashJobRunner.cpp:685` (`runMotionWriter`) | 10s | P4 동기 실행의 도입부 |
| `DashJobRunner.cpp:848` (`runMotionLauncher`) | **기본 30s** | 이 함수의 나머지는 모범적 시그널 구동(6절) — 이 한 줄만 잔존 |
| `TopOptPostprocessDialog.cpp:1794` | 3s | UI 스레드에서 직접 |
| `DashExtensionProcess.cpp:354` (`runBlocking`) | 15s | P4 내부 |

**올바른 형태**: `errorOccurred` 슬롯에서 FailedToStart 처리 (이미 `DashModelRunner.cpp:184-201` · `DashExtensionProcess.cpp:139-140` 에 연결된 선례가 같은 코드베이스에 있다).

## 5. P4 — one-shot 동기 완주 대기

**형태**: 프로세스 시작부터 종료까지 호출 스택에서 완주 대기. 함수 시그니처가 동기(반환값 = 결과)라서 생기는 구조.

| 지점 | 내용 | 최대 지속 |
|---|---|:---:|
| `DashExtensionProcess::runBlocking` (`:335-366`) | `waitForStarted(15000)` + `waitForFinished(timeoutMs)` — **기본 300000ms = 5분** (`DashExtensionProcess.h:108`). 헤더 주석 "Caller must NOT be the GUI thread" 명시(`h:105`)에도 워커 스레드가 0개인 현 구조에서 호출자는 GUI 스레드일 수밖에 없음. **현재 직접 호출처 0건 — 휴면 지뢰** | 300s |
| `DashJobRunner::runMotionWriter` (`:666-729`) | `waitForFinished(500)` + `processEvents` 를 5분간 반복 — P7 과 결합된 "동기 실행 + 재진입 창" 최악 조합 | 300s |
| `DashExtensionProcess::killOrphans` (`:52-69`) | `taskkill`/`pkill` 실행 후 `waitForFinished(3000)` — startDaemon 경로(P1)에 포함됨 | 3s |

**올바른 형태**: 같은 파일의 `runAsync` (`:370-405`) 가 이미 정답이다 — `oneShotFinished(jobId, success, output)` 시그널로 결과 통지. `runBlocking` 은 삭제(호출처 0)하거나 워커 스레드 전용임을 assert 로 강제. motion-writer 는 motion-launcher 큐(6절 모범)와 같은 형태로 이식.

## 6. P5 — 완료 시그널 무시 + 파일시스템 폴링

**형태**: 작업 완료가 시그널로 통지되는데도 이를 구독하지 않고, 산출물 파일의 존재·크기를 폴링해 완료를 추정.

| 지점 | 내용 | 최대 지속 |
|---|---|:---:|
| `DashJobRunner::waitForFile` (`:2351-2364`) | `processEvents` + `msleep(2000)` 반복. `runWbpjDoeAsync` 가 `enqueueUpdatePrtGeometry`(`:2670`) 직후 호출(`:2673`) — **`updatePrtGeometryCompleted` 시그널이 있는데 무시**하고 STP 파일 폴링. 2초 단위 완전 정지 반복 | 600s/케이스 |
| `DashJobRunner::waitForVtuFileComplete` (`:598-664`) | `msleep(100)` + `processEvents` 폴링으로 모핑 산출 VTU 대기 + **파일 크기 0.5s 안정화 휴리스틱** — flush 중 파일을 완료로 오판하는 레이스 내장 (기반 문서 로드맵 3-2절과 동류) | 60s |

**올바른 형태**: 완료 시그널 수신 → 파일 검증 순서 (파일 존재가 아니라 시그널이 완료의 근거). 같은 파일 안에 참조 구현이 있다 — `runDirectJobs` 의 .wbpj 경로는 `loadPrtCompleted` 에 람다를 `Qt::QueuedConnection` 으로 연결해 다음 단계를 연쇄한다 (`DashJobRunner.cpp:2326-2336`, GUI 블로킹 0). 시그널이 없는 외부 산출물만 `QFileSystemWatcher`/`QTimer` 콜백으로.

## 7. P6 — 고정 슬립 추측 대기

**형태**: 통지 대신 "이쯤이면 됐겠지" 시간 추측.

| 지점 | 내용 |
|---|---|
| `DashJobRunner.cpp:1576` | `msleep(1000)` — 주석 "Give some time for morphing to start". 모핑 시작·완료를 통지받을 수단(콜백·시그널)을 쓰지 않고 1초 고정 슬립 후 P5 폴링으로 진입 |

빠르면 낭비, 느리면 오동작 — 양쪽 모두에서 틀리는 패턴. 대기 근거가 사건(시그널)이 아니라 시계라는 점에서 P5 의 극단형.

## 8. P7 — `processEvents` 재진입 (프리즈 위장)

**형태**: 동기 루프를 유지한 채 중간중간 `processEvents` 로 이벤트를 펌핑. UI 가 "살아 보이게" 되지만 실제로는:

1. **재진입 창** — 사용자가 실행 중 버튼을 다시 누르면 같은 함수가 현재 스택 위에서 재진입 (#64 크래시 계급의 원천, 기반 문서 2-4절).
2. `msleep` 과 결합 시 UI 는 슬립 동안 얼고 펌핑 순간만 갱신 — 10Hz 프리즈 점멸.
3. 정지 원인이 코드에서 안 보이게 가려져 후속 수리를 지연시킴.

QProcess 실행 경로와 결합된 지점 (전체 58곳 중):

| 지점 | 결합 대상 |
|---|---|
| `DashJobRunner.cpp:696-707` | motion-writer `waitForFinished(500)` 루프 (P4) |
| `DashJobRunner.cpp:604-657` | VTU 폴링 (P5) — `msleep(100)` 결합 |
| `DashJobRunner.cpp:2357, 2679, 2686` | `waitForFile` 폴링 (P5)·STP 배치 루프 |
| `DashJobRunner.cpp:1577-1651` (8곳) | dfsxml 모핑+MBD 배치 루프 — 거의 모든 문장 뒤에 산재하는 "뿌리기" 형태 |
| `DashJobRunner.cpp:577` | run 폴더 생성 루프 |
| `DashOptimizerWidget.cpp:1913, 1938` | 동기 모핑 프리뷰 루프 (DLL 축 — 기반 문서 2-3절 2번) |
| `TopOptPostprocessDialog.cpp:2092` | `showProgressMessage` — QProcess 시그널 슬롯 안에서도 호출됨 |

**view 계층 전수** (개정 1 보강 — 17곳/7파일, 커밋 기준):

| 파일 | 지점 | 아종 |
|---|---|---|
| `view/dialog/TopOptPostprocessDialog.cpp` | `:470, 532, 648, 794, 1318, 2092` (6곳) | 혼재 — `:2092` 는 QProcess 시그널 슬롯 결합(위 표), `:532` 는 레이아웃 강제 계산 |
| `view/DashDataProcessorWidget.cpp` | `:1517, 1526, 1538` | 단발 강제 리페인트 |
| `view/DashOptimizerWidget.cpp` | `:1913, 1938` | **동기 루프 펌핑** — 모핑 프리뷰 루프 (위 표와 동일 지점) |
| `view/DashGeometryParameterWidget.cpp` | `:1532, 1572` | **동기 루프 펌핑** — 위젯 내 모핑 루프 (기반 문서 6-1절) |
| `view/overlay/DashViewOptionsWidget.cpp` | `:175, 187` | 단발 강제 리페인트 |
| `view/DashMainWindow.cpp` | `:2111` | 단발 강제 리페인트 |
| `view/dialog/DashMeshQualityDialog.cpp` | `:284` | 단발 강제 리페인트 |

아종 2분류 — **동기 루프 펌핑**(장시간 루프 안에서 반복 호출)은 재진입 위험이 model 41곳과 등가이며 내부 작업 축의 WorkerJob 전환과 함께 소멸한다. **단발 강제 리페인트**("UI 새로고침 강제" 주석류)는 동기 처리 중 화면 갱신을 강제하는 잔재로, 해당 처리의 비동기 전환 후 무의미해진다.

나머지 model 계층(DashDataProcessor 14 · DashResultProcessor 8)은 내부 장시간 작업 축 — 기반 문서 2-3절이 담당. **본 카탈로그 범위에서의 판정은 동일**: processEvents 는 수리가 아니라 위장이며, W10 DoD(`model/` processEvents 0건)가 전량 제거를 봉인한다.

## 9. P8 — 동기 반환 API 계약 (구조 원인)

P1~P4 는 지점 수리만으로 사라지지 않는다 — **API 시그니처가 동기 완료를 약속하고 있기 때문**이다.

| API | 계약 | 의존 호출자 (동기 반환값에 분기) |
|---|---|---|
| `bool DashExtensionProcess::startDaemon()` | 반환 시점에 ready 여부 확정 | `DashManager::enqueueLaunch` (`:156-162` — 반환 직후 `isDaemonReady()` 재확인 후 즉시 실패 처리) · `DashSolverNxCad::tryStartIfConfigured` (`:115-119`) · `DashModelRunner::startDaemon` (`:240-246`) · `DashModelBuilderMCU` (`:120`) |
| `bool DashExtensionProcess::runBlocking(...)` | 반환값 = 프로세스 결과 | 현재 0곳 (휴면) |
| `bool DashJobRunner::runMotionWriter(...)` | 반환값 = 실행 성공 여부 | 모핑+MBD 루프 (`:1645`) |

이 계약을 유지하는 한 구현부의 `waitFor*` 는 제거 불가능하다. 전환은 API 재설계와 동행해야 한다: `startDaemon()` → `void` (결과는 `daemonReady`/`daemonStopped` 시그널) + 상태 pull `isDaemonReady()` 병행 (기반 문서 4절 계약 "구독" 규칙 2). 호출자의 즉시 분기는 "미기동 시 큐잉 + ready 시 flush"로 대체 — 큐 인프라는 이미 존재한다.

## 10. 파일 × 패턴 매트릭스

| 파일 | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `controller/DashExtensionProcess.cpp` | ● | ● | ● | ● | | | | ● |
| `controller/DashSolverNxCad.cpp` | ●(유발) | | | | | | | ● |
| `controller/DashManager.cpp` | ●(호출) | | | | | | | ● |
| `model/DashModelRunner.cpp` | ●(위임) | | | | | | | ● |
| `model/DashModelBuilderMCU.cpp` | ●(위임) | | | | | | | ● |
| `model/DashModelBuilder.cpp` | | ● | ● | | | | | |
| `model/DashJobRunner.cpp` | | ● | ● | ● | ● | ● | ● | ● |
| `view/DashModelBuilderMCUWidget.cpp` 외 위젯 2곳 | ●(호출) | | | | | | | |
| `view/DashOptimizerWidget.cpp` | | | | | | | ● | |
| `view/dialog/TopOptPostprocessDialog.cpp` | | ● | ● | | | | ● | |

`DashJobRunner` 가 8패턴 중 6패턴을 보유한 최대 밀집 지점이며, `DashExtensionProcess` 는 지점 수는 적지만 **공용 베이스 클래스**라서 P1·P8 이 모든 데몬 사용처(NX·Journal·Sensitivity·MCU)로 전파된다.

## 11. 정상 구현 대조군 — 같은 코드베이스 안의 정답

전환 시 새 발명이 필요 없음을 보이는 내부 선례 (기반 문서 2-5절과 동일 목록 + 본 조사 보강):

| 선례 | 위치 | 무엇이 옳은가 |
|---|---|---|
| `DashModelRunner` 실행부 | `model/DashModelRunner.cpp:178-201` | QProcess 사용 전반에 `waitFor*` 0회 — finished/readyRead/errorOccurred 완전 시그널 구동 |
| `DashOptimizer` | `model/DashOptimizer.cpp:81-87` | 동일 |
| `DashOptimizerWidget` fit 프로세스 | `view/DashOptimizerWidget.cpp:2417-2424` | 위젯 계층에서도 가능함을 보이는 선례 |
| `DashExtensionProcess` 데몬 명령 큐 | `controller/DashExtensionProcess.cpp:193-226, 252-293` | sendCommand 큐잉 → 마커 파싱 → commandCompleted/commandFailed — 인프라 자체는 완성형 비동기 |
| `DashExtensionProcess::runAsync` | `controller/DashExtensionProcess.cpp:370-435` | one-shot 의 비동기 정답 (도입부 P2 한 줄 제외) |
| MBD motion-launcher 큐 | `model/DashJobRunner.cpp:751-858` | finished 람다 + `invokeMethod(QueuedConnection)` 순차 큐 — motion-writer 이식 목표 |
| `runDirectJobs` .wbpj 연쇄 | `model/DashJobRunner.cpp:2326-2336` | `loadPrtCompleted` 구독으로 다음 단계 연쇄 — `waitForFile`(P5) 의 비동기 등가물 |

## 12. 처방 귀속 — 어디서 고쳐지나

본 카탈로그는 신규 작업을 만들지 않는다. 전 지점이 기반 문서의 W10 서브태스크 분할(7절)에 이미 귀속된다:

- P1 (+P8 startDaemon 계약) → 서브태스크 c (데몬 기동 비동기화)
- P5 · P6 → 서브태스크 b (파일 폴링 → 워처/타이머) + a (파일럿: `runWbpjDoeAsync`)
- P2 · P3 · P4 → 서브태스크 a·f (ProcessJob 전환 과정에서 지점 소거)
- P7 → 서브태스크 f (잔여 processEvents 제거) — DoD "`model/` processEvents 0건, GUI 스레드 `waitFor*`/`msleep` 0건"이 봉인 게이트

## 13. 음성 판정 — 조사했으나 해당 없는 프리미티브 (개정 1)

발단 질문("잘못 구현된 패턴 **모두** 나열")의 '모두'를 닫기 위해, GUI 스레드 블로킹을 만들 수 있는 나머지 프리미티브를 재검증(2026-07-21, 커밋 기준)에서 전수 grep — 전부 0건 또는 비차단 판정:

| 프리미티브 | 결과 | 비고 |
|---|:---:|---|
| 중첩 이벤트 루프 `QEventLoop::exec` | 0건 | `QEventLoop` 표기는 전부 `processEvents(QEventLoop::...)` 플래그 인자 |
| `QProcess::execute` / `::system()` / `popen` | 0건 | 정적 블로킹 실행 부재 |
| `std::async` / `std::future` | 0건 | 기반 문서 2-1절 스레드 집계(0건)와 일치 |
| `QThread::wait` / `QThreadPool::waitForDone` / `QWaitCondition` / `QSemaphore` | 0건 | 스레드 조인·동기화 계열 부재 |
| `QFutureWatcher::result()` | 1건 — **비차단** | `DashAnalysisLauncher.cpp:590` — `finished` 슬롯(`onAnalysisCompleted`) 내부 호출이라 결과가 이미 준비된 상태. 대상 아님 |

함의: 본 카탈로그의 P1~P8 + 내부 작업 축(기반 문서 2-3절)이 GUI 스레드 블로킹의 전 원천이다 — 숨은 제9 패턴은 없다.

## 14. 참고 자료

- 내부: [[194-1-async-execution-patterns]] 2-2절(위치 축 목록)·4절(Job 계약)·7절(서브태스크) / [[198-1-improvement-roadmap]] / [[195-1-backlog-code-evidence]]
- 종류별 요약 + 전환 처방 매핑: [[205-5-w6-w10-async-minimal-example]] 8장 (본 카탈로그 지점을 종류 7분류·전환 후 형태로 재편)
- 외부: Qt 5.15 문서 `QProcess` — Synchronous Process API 절의 GUI 스레드 경고, `QProcess::errorOccurred`, `QFileSystemWatcher`
