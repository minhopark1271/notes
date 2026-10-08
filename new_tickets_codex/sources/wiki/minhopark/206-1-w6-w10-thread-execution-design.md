# DashGUI2 W6·W10 실행 모델 설계 — 메인 이벤트 루프 스레드의 하위 작업 실행 방식 전환 (드래프트)

> 원본: 사전조사 Issue #206 — 본문을 이 페이지로 이관한 뒤 Issue 삭제 (2026-08-24). **본 페이지가 정본**

> 상태: 사전조사 이슈 발행 — DashGUI2#206 (본 문서가 정본, 이슈 본문과 동기)\
> 연관 Issue: #64 (Crash Debug — 재진입 크래시 계급의 원천이 본 문서의 대상 실행 모델)\
> 기반 문서: [[200-3-prioritized-backlog]] 5-1절 (W6·W10 정의·규모·착수 순서) · [[194-1-async-execution-patterns]] (판정·상세 설계 — 본 문서는 그 시각/구조 브리지) · [[193-1-async-execution-models]] (개념 해설)\
> 목적: 검토의견 2건에 대한 답 — ⑴ "현재 메인 이벤트 루프를 가진 스레드에서 하위 작업이 어떻게 실행되나"를 실측 예시로 도식화, ⑵ "이것이 W6·W10에서 어떻게 바뀌어야 하나"를 설계\
> 분석 시점: 2026-07-16, 브랜치 `dev` · 재검증: 2026-07-21, `dev` 커밋 `52965e4` — 라인 앵커는 재검증 커밋 기준 (유효기간 있음)\
> 개정 1: 2026-07-16 — 검토 질문 2건("창이 꺼지면 뒷단 작업도 함께 죽는 것 아닌가 — 수신자 스레드가 종료되는 것 아닌가" · "큐 관리 레이어가 작업 결과를 future로 들고 있다가 시그널로 방출하는 패턴이 맞나") 반영: 1-6절(소유 구조·큐 레이어 실측 — 창과 무관한 소유자는 이미 존재) · 3-6절(Job 소유권과 창 수명 — 위젯은 소유가 아니라 구독, 재진입은 pull 복구) 신설\
> 개정 2: 2026-07-21 — CI 미진행 결정(백로그 개정 29) 반영: W10 DoD 도식의 "W9 게이트 (하드) 봉인"을 "grep 수동 검증(W9 자동 게이트는 선택)"으로 완화. 설계·판정 불변 — 표기만 조정\
> 개정 3: 2026-07-21 — 자매 문서·코드베이스 재검토 반영 3건: ⑴ 실측을 커밋 기준(`52965e4`)으로 재검증 — 수치 갱신(1-3절·4장: `waitFor*` 23곳/4파일 · `msleep` 5곳 · `processEvents` 실호출 58곳=model 41+view 17 · QProcess 137), 앵커 2건 수정(FE C콜백 `:1170`→`:333` · `DashProjectManager.cpp:21`→`:13`)·나머지 전수 유효 확인, 음성 판정 인용(카탈로그 개정 1 — 세 패턴 밖 숨은 원천 없음) ⑵ W6 재정의(백로그 개정 28) 반영 — 구성을 엔진 위임(composition)으로, 범위를 단일 one-shot 소비자로 한정(`DashJobRunner` 다중 프로세스·C API·파일 폴링은 W10/W20 이연), DoD를 grep 0건에서 구조·행위 판정으로 전환(2장·4장) ⑶ Job 시그널 표면 정합(시그널 3종 = `started`·`progressed`·`finished`)·실행 주체 3갈래(`DaemonCommandJob` 분리) 정렬(3장 — [[205-5-w6-w10-async-minimal-example]] 4장 갈래 지도와 동기)

---

## 0. 이 문서의 자리

세 자매 문서와의 관계:

- **개념**은 [[193-1-async-execution-models]] — 이벤트 루프·시그널·Job·스레드가 각각 무엇이고 왜 층위가 다른가.
- **판정·상세 설계**는 [[194-1-async-execution-patterns]] — 완료 처리 방식(시그널 표준)·DLL 3등급·워커 선결 5건·서브태스크 분할.
- **실행 순서·규모**는 [[200-3-prioritized-backlog]] 5-1절 — W3 → W6 → W10, 합산 ~6.5주.

본 문서는 그 셋을 잇는 **시각/구조 브리지**다. 산문·표로 흩어진 "현재 스레드가 무엇을 하고 있나"와 "W6·W10 후 무엇이 달라지나"를 **하나의 진행 도식**으로 압축한다. 새 판정은 하지 않는다 — 기존 판정을 그림으로 옮긴 것이다.

한 문장 요약: **지금은 스레드가 하나뿐이라 화면을 살리는 일(이벤트 루프)과 하위 작업을 실행하는 일을 한 스레드가 번갈아 한다. W6은 그 하위 작업 실행을 한 곳으로 모으고(구조), W10은 "기다림"을 "통지받음"으로 바꿔 이벤트 루프가 멈추지 않게 한다(동작).**

---

## 1. 현재 — 단일 스레드가 이벤트 루프와 하위 작업을 겸한다

### 1-1. 한 장 요약 — 스레드는 하나, 역할은 둘

실측(2-1절 [[194-1-async-execution-patterns]]): `moveToThread`·`QThread`·`std::thread` 0건, 진짜 워커는 DOE 샘플링 1곳뿐. 사실상 **모든 코드가 메인(GUI) 스레드 하나에서 돈다.**

```
메인(GUI) 스레드 ── 프로세스에서 실질적으로 유일한 실행 흐름
├── 역할 1: Qt 이벤트 루프 (QApplication::exec)
│           클릭·키·타이머·리페인트·큐된 시그널 배달을 하나씩 꺼내 처리
│           → 이 루프가 돌아야 화면이 "살아 있다"
└── 역할 2: 모든 하위 작업의 실제 실행
            모핑 DLL(Morph) · 파일 파싱(reader.Update) · 결과/KPI 파싱 ·
            외부 프로세스(NX·Ansys·MBD) 기동과 완료 대기
```

문제의 뿌리는 **두 역할이 같은 스레드**라는 것 하나다 — 역할 2가 도는 동안 역할 1은 멈춘다. 하위 작업 하나가 수초~수분 걸리면 그 시간만큼 화면이 얼어붙는다("응답 없음").

### 1-2. 도식 — 정상 상태 vs 하위 작업 실행 중

같은 스레드의 시간 흐름을 따라가면 이렇게 된다 (모핑 실행 = 순수 동기 CPU 작업 예시):

```
[t0 · 이벤트 루프 상주] 메인 스레드가 exec() 안에서 이벤트를 하나씩 처리
   │   1. 마우스·키·타이머·리페인트 정상 배달
   │   2. 화면 반응 즉각 — 사용자가 "살아 있다"고 느끼는 유일한 상태
   ▼

[t1 · 버튼 슬롯 진입] "Run Morphing" 클릭 → 슬롯 호출 (여전히 메인 스레드)
   │   1. DashModelRunnerWidget 슬롯 → DashManager::ExecuteMorphing
   │   2. 슬롯이 끝나야 이벤트 루프로 복귀할 수 있음 — 아직 t0로 못 돌아감
   ▼

[t2 · 하위 작업 동기 실행] Morph() DLL 호출이 메인 스레드를 점유
   │   1. 이벤트 루프 정지: 새 이벤트는 큐에 쌓이지만 꺼내는 주체가 없음
   │   2. 화면 완전 정지 (N케이스 × 수초 — 배치면 수분)
   │   ※ 이 경로엔 processEvents조차 없어, 상태바 스피너 애니메이션(QTimer 기반)
   │      마저 발화하지 못하고 얼어붙는다 — "진행 표시가 진행을 못 보여주는" 역설
   ▼

[t3 · 슬롯 반환] 작업 종료 → 이벤트 루프 복귀(t0)
       t2 동안 쌓인 이벤트가 일괄 처리되며 UI가 갑자기 되살아남
```

정상 상태(t0)와 정지 상태(t2)를 **한 스레드가 번갈아** 오간다. 비동기가 아니라, 화면이 멈춘 걸 사용자가 눈치채기 전에 작업이 끝나기를 바라는 구조다.

### 1-3. 현재 하위 작업 실행의 3패턴 (실측 예시)

같은 "단일 스레드 점유"라도 코드 상 세 가지 얼굴로 나타난다. 셋 다 결과는 정지지만, W10 전환 처방이 갈리므로 구분한다.

**패턴 A — 순수 동기 (완전 정지, 은폐 없음)**

```
[t2-A] Morph() / reader.Update() 를 그냥 호출하고 반환을 기다림
   │   1. processEvents 없음 → 이벤트 루프 완전 정지
   │   2. 스피너·리페인트·클릭 전부 죽음
   │   실측: DashMorphingDoeExecutor::Execute 모핑 루프 (controller/, :163~)
   │         DashManager::ExecuteMorphing 본문
```

**패턴 B — 폴링 + processEvents (정지를 "가린" 척)**

```
[t2-B] 파일이 생길 때까지 for 루프로 반복 확인 (waitForFile)
   │   1. QCoreApplication::processEvents()  ← 이벤트 루프를 강제로 한 바퀴
   │      · 화면이 잠깐 반응하는 것처럼 보임 (은폐 효과)
   │      · 그러나 이 순간이 재진입 창(reentrancy window) — 1-5절
   │   2. QThread::msleep(2000)  ← 2초간 완전 정지
   │   3. 파일 없으면 1로 반복 (최대 600초)
   │   실측: DashJobRunner::waitForFile (model/DashJobRunner.cpp:2351-2364)
   │         for { processEvents(); if(exists) return; msleep(2000); }
```

**패턴 C — busy-wait (통지 무시하고 능동 대기)**

```
[t2-C] 데몬이 [READY]를 보낼 때까지 while 루프로 대기 (startDaemon)
   │   1. while(!ready && elapsed<timeout) { waitForReadyRead(300); onReadyRead(); }
   │   2. 완료 시그널 인프라가 있는데도 능동 폴링으로 우회
   │   3. NX 데몬 최초 기동 = 최대 120초 프리즈
   │   실측: DashExtensionProcess::startDaemon (controller/, :150-161)
```

세 패턴의 원천 규모(실측 — 재검증 2026-07-21, 커밋 `52965e4`): `processEvents` 실호출 **58곳/10파일**(model 41 + view 17 — view 전수·아종 2분류는 [[201-1-qprocess-antipattern-catalog]] 8절), `waitFor*` **23곳/4파일**, `msleep` **5곳**(전부 DashJobRunner), QProcess 표기 **137곳**. 이 밖의 차단 프리미티브(중첩 `QEventLoop::exec`·`QProcess::execute`·`std::async`·`QThread::wait` 등)는 전수 grep **0건** — 세 패턴 밖 숨은 원천은 없다(카탈로그 13절 음성 판정).

### 1-4. 반증 — 같은 코드베이스에 이미 있는 모범 (수렴 목표)

핵심은 **새 발명이 아니라 수렴**이라는 점이다. 같은 파일 안에 정답이 이미 산다:

```
[t1 · 요청] "connect 먼저, start 나중" — 완료 시그널을 구독한 뒤 큐에 넣음
   │   1. connect(nxCad, &DashSolverNxCad::loadPrtCompleted, this, <람다>, QueuedConnection)
   │   2. nxCad->enqueueLoadPrt(...)   ← 즉시 반환, 대기 없음
   │      실측: DashJobRunner::runDirectJobs .wbpj 경로 (:2326-2336)
   ▼

[t2 · 대기 0] 메인 스레드는 곧장 이벤트 루프로 복귀 — 화면 정상
   │   NX 데몬은 별도 OS 프로세스에서 병렬로 작업
   ▼

[tN · 완료] loadPrtCompleted 시그널 도착 → 슬롯(메인 스레드)에서 다음 단계 연쇄
       launchAnsysJournalDirect(...) — 폴링 한 번 없이 파이프라인 진행
```

**같은 목적의 나쁜 쌍둥이가 바로 옆에 있다**: `runWbpjDoeAsync`는 `enqueueUpdatePrtGeometry`(비동기 enqueue)를 호출해 놓고도 완료 시그널 `updatePrtGeometryCompleted`를 무시한 채 `waitForFile(stpOutputPath, 600)`으로 파일을 폴링한다(`:2670-2673`, 패턴 B). 이름만 `Async`지 동작은 동기다. W6·W10은 이 쌍둥이를 왼쪽(모범)으로 수렴시키는 작업이다.

기타 모범: `DashModelRunner`(`QProcess`를 다회 사용하면서 `waitFor*`/`processEvents`/`msleep` 0회 — 완전 시그널 구동), FE 솔버 C 콜백 → `invokeMethod` 큐 마샬링(`:333`), DOE 샘플링 워커(`QtConcurrent::run` + `QFutureWatcher`).

### 1-5. 왜 위험한가 — processEvents 재진입 창과 #64

패턴 B의 `processEvents()`는 정지를 가리는 진통제지만, 대가가 크다. 이벤트 루프를 **하위 작업의 한가운데서** 강제로 돌리므로, 그 순간 임의의 이벤트가 끼어든다:

```
[정상 흐름 가정] 슬롯 A 실행 중 → 완료 → 이벤트 루프 → 슬롯 B
[재진입 사고]   슬롯 A 실행 중 processEvents() 호출
   │   1. 큐에 있던 "Run 버튼 재클릭"이 여기서 배달됨
   │   2. 슬롯 A가 아직 안 끝났는데 슬롯 A'가 겹쳐 실행 (재진입)
   │   3. A가 반쯤 만든 상태를 A'가 건드림 → 널 역참조·이중 해제·use-after-free
       #64 크래시 계급의 구조적 원천 — 개별 버그가 아니라 결함의 '종(class)'
```

그래서 목표는 개별 크래시 패치가 아니라 **실행 모델 전환으로 결함의 종 자체를 제거**하는 것이다(백로그 5-1절). `processEvents` 41곳이 0이 되면 재진입 창이 원리적으로 닫힌다.

### 1-6. 소유 구조·큐 레이어 실측 — 창과 무관한 소유자는 이미 있다 (개정 1)

발단 질문: "특정 작업을 실행해 두고 창이 꺼지면 수신자 스레드가 함께 종료돼 뒷단 작업도 죽는 것 아닌가". 먼저 범주 구분 — **창(위젯)은 스레드가 아니다.** 창이 닫힐 때 소멸하는 것은 수신자 **객체**이지 스레드가 아니다. GUI 스레드는 QApplication이, 워커 풀은 앱 전역이 소유하므로 창 수명과 무관하고, 수신자 QObject가 소멸하면 Qt가 시그널 연결을 자동 해제해 통지가 조용히 유실될 뿐(크래시 없음) 작업 자체는 영향받지 않는다. 관건은 스레드가 아니라 **실행 객체를 누가 소유하는가**다.

소유 체인 실측 — 주 실행 체인의 소유자는 전부 뷰 밖이다:

- `DashManager` — 부모 없는 싱글톤 (`controller/DashManager.cpp:206`, `atexit` 파괴)
    - `DashSolverNxCad`(`:92`) · `DashExtensionProcess` 데몬 3개 — Journal·MCU·Sensitivity (`:94-108`)
- `DashProjectManager` — 싱글톤 (`controller/DashProjectManager.cpp:13`)
    - `DashProject` → `DashAnalysisLauncher`(`model/DashProject.cpp:79`, 유일한 `QFutureWatcher` 보유) → `DashJobRunner`(`model/DashAnalysisLauncher.cpp:51`)

예외 = 2-2절 산재 목록의 계층 위반 2건: `DashOptimizerWidget::m_fitProcess`(`view/DashOptimizerWidget.cpp:2418`)·`TopOptPostprocessDialog::m_postprocessProcess`(`view/dialog/TopOptPostprocessDialog.cpp:1749`)는 위젯이 부모라서 **창이 닫히면 QProcess 소멸자가 외부 프로세스를 kill한다** — "창 닫힘 = 작업 사망"이 현재 코드에 실존하는 유일한 곳. 처방은 3-6절.

큐 레이어 실측 — "작업 큐를 관리하는 레이어"는 축에 따라 있고 없다:

| 축 | 현재 | 비고 |
|---|---|---|
| 외부 데몬 | **있음** — `DashExtensionProcess::m_commandQueue` 직렬 명령 큐 + `commandCompleted` 시그널 · `DashSolverNxCad` 도메인 큐 | 문제는 큐가 아니라 큐를 우회하는 호출자 (1-3절 패턴 B·C) |
| 내부 작업 | **없음** — `QThreadPool`/`moveToThread` 0건 | W10이 직렬 풀 2종 신설 (3-3절) |
| 공통 표면 | **없음** — 종류 무관 시그널 구독을 주는 Job 부재 | W10이 신설 (3-2절) |

함의 둘: ⑴ W6·W10은 소유 구조를 재배치하는 작업이 아니다 — 창 무관 소유자(Job 레이어의 숙주)는 이미 준비돼 있고, 바꿀 것은 실행 모델뿐이다. ⑵ 다만 지금은 "창이 꺼져도 뒷단에서 계속"이 성립하는 상황 자체가 거의 없다 — 작업이 GUI 스레드에서 동기로 도는 동안 이벤트 루프가 멈춰 있어(1-2절 t2) 사용자가 창을 닫는 것조차 불가능하다(closeEvent 미처리). 그 능력은 W10 전환 후에야 생기며, 그때의 소유·구독 규칙이 3-6절이다.

---

## 2. W6 — 실행 경로 일원화 (구조 변화: 흩어진 N개 → 한 곳)

### 2-1. 무엇을 바꾸나

W6은 **동작을 바꾸지 않는다 — 실행 경로를 한 곳으로 모은다.** W10이 "한 곳만 고치면 되는" 상태를 만드는 전제다(백로그 5-1절 선행성). 구성(백로그 개정 28로 재정의 — 위임 구성·범위 한정·DoD 구조 판정):

1. `runAsync` **부분 수신 버그 선수리** — 비동기 one-shot 경로가 stdout을 온전히 받도록 (현재 `runAsync`가 결과 라인을 부분만 조립하는 결함 — 안 고치고 확산하면 마커 잘림이 전 소비자로 번짐).
2. **공통 책임을 엔진에 집약** — exe 검증·환경변수·UTF-8 디코딩·라인 조립·중복 실행 가드·취소·정리(child cleanup)를 엔진(`DashExtensionProcess`) 한 곳에. stdout/stderr 분리가 필요한 소비자(`DashModelBuilder`)를 위해 채널 모드(Merged/Separate)는 엔진 파라미터로 노출.
3. **단일 one-shot 소비자를 엔진 위임(composition)으로 전환** — 아래 5개 클래스(+ `DashJobRunner`의 motion-launcher 실행부)가 각자 `QProcess`를 직접 소유·기동하던 것을, 엔진 인스턴스 소유 + `runAsync` 호출 + 완료/로그 시그널을 도메인 시그널로 번역하는 위임으로 교체(선례 = MCU). 상속은 경로·환경 특수화 한정(선례 = `DashSolverNxCad`). `DashJobRunner`의 **다중 프로세스(`QHash`)·C API 런처·파일 폴링은 W6 범위 밖** — 단일 one-shot 모델과 불일치, W10(폴링→통지)·W20(God-object 분해)으로 이연.
4. `killOrphans` **축소** — 실행 파일 이름 기준 광역 `taskkill`(같은 이름의 무관한 프로세스까지 죽일 위험)을 자기 PID 추적 kill로.
5. **경로 카탈로그 일원화** — solver/exe 경로 조회를 한 곳(`DashExtensionProcess.h`)으로.

DoD(구조·행위 판정 — grep 카운트 비의존, 개정 28): ⑴ 대상 소비자가 자체 `new QProcess`/`start` 없이 엔진에 위임 ⑵ 공통 책임이 엔진 한 곳에만 존재 ⑶ 부분 수신 버그 재현 검증 통과 ⑷ `killOrphans`가 자기 PID만 정리 ⑸ 기존 실행 워크플로 무회귀. `grep QProcess`는 소프트 추세 가드(신규 산재 방지)로만 유지 — `DashJobRunner`의 C API·다중 프로세스가 정당하게 잔존하므로 리터럴 0을 목표로 하지 않는다.

### 2-2. 도식 — Before → After (구조)

```
[현재] QProcess가 6개 클래스에 흩어져 각자 다른 품질로 기동
   │   model/DashModelBuilder      (m_process)      — new QProcess
   │   model/DashModelRunner       (m_process)      — 시그널 구동 (유일한 모범)
   │   model/DashOptimizer         (m_process)      — new QProcess
   │   model/DashJobRunner         (new QProcess)   — 폴링/waitFor 혼재
   │                               ※ W6 대상은 motion-launcher 실행부만 — 다중 프로세스·
   │                                 C API 런처·파일 폴링은 W10/W20 이연 (개정 28)
   │   view/DashOptimizerWidget    (m_fitProcess)   — 뷰가 직접 실행 (계층 위반)
   │   view/dialog/TopOptPostprocessDialog (m_postprocessProcess) — 뷰가 직접 실행
   │   ※ 각자 exe 검증·env·UTF-8·타임아웃·중복가드·정리를 제각각 구현 (또는 누락)
   │   ※ 결함 수정이 6곳에 반복 필요 — 산재는 진행형(QProcess 123→137, 4일 사이)
   ▼

[W6 후] 공용 엔진 1개로 수렴 (엔진 = DashExtensionProcess — 위임, 상속은 경로·환경 특수화 한정)
   │   1. 공통 책임(exe검증·env·UTF-8·라인조립·중복가드·취소·정리)은 엔진이 1회 구현
   │   2. runAsync(수리) = 비동기 one-shot, runBlocking = 워커 전용(주석 계약 유지)
   │   3. 호출부는 "QProcess 직접 소유" → "엔진 위임(composition)"으로 교체
   │      (도메인 클래스는 엔진을 HAS-A 소유, 완료/로그 시그널을 도메인 시그널로 번역)
   │   4. killOrphans: 광역 taskkill → 자기 PID 추적 kill
   ▼

[결과] "실행"이라는 관심사가 한 파일에 — W10이 손댈 지점이 1곳으로 축소
       DoD = 구조·행위 판정 (2-1절 5건 — grep QProcess는 소프트 추세 가드, 개정 28)
```

### 2-3. 무엇을 아직 안 바꾸나 — 대기 모델은 W10 몫

**중요한 경계**: W6은 실행을 한 곳에 모을 뿐, "기다림"을 없애지 않는다. W6 직후에도 호출부는 여전히 편의상 블로킹 래퍼(또는 폴링)로 완료를 기다릴 수 있다 — 다만 이제 그 대기 로직이 **한 곳에만** 있어, W10이 그 한 곳을 시그널 구동으로 뒤집으면 전 호출부가 함께 전환된다.

```
W6 = "실행 코드를 한 곳에 모은다"       (구조 — where)
W10 = "그 한 곳의 대기를 통지로 바꾼다"  (동작 — how)
```

이 분리가 W6을 1.5주 / W10을 4주로 나눈 이유다. W6 없이 W10을 하면 6곳을 각각 뒤집어야 하고, 6곳의 미묘한 차이(env·UTF-8·타임아웃)까지 개별 검증해야 한다.

---

## 3. W10 — 이벤트 구동 전환 (동작 변화: 기다림 → 통지받음)

### 3-1. 무엇을 바꾸나

W10은 **대기를 통지로 바꾼다.** 구성(백로그 5-1절 + [[194-1-async-execution-patterns]] 7절 서브태스크 a~f):

1. **Job 상태머신 도입** — Pending → Running → Succeeded/Failed(reason)/Cancelled 전이를 **시그널 3종**(`started`·`progressed`·`finished`)으로 방송(취소 = `cancel()` 메서드, 실패 사유 = `finished` 파라미터 — "계약 4종"은 시그널 개수가 아니라 계약 차원). 호출자는 내부가 외부 exe인지 워커인지 모른 채 시그널만 구독(Job 표면).
2. **파일 폴링 → 완료 통지 구독** — `waitForFile`·`waitForVtuFileComplete`를 작업 완료 시그널 구독으로 교체(완료 시그널이 없는 외부 산출물에 한해 `QFileSystemWatcher`/`QTimer` 콜백을 보조로).
3. **model 계층 `processEvents` 41곳 제거** — 재진입 창을 원리적으로 닫음.
4. **데몬 기동 비동기화** — `startDaemon` busy-wait 제거 → `daemonReady` 시그널 → 큐 flush (NX 120초 프리즈 소멸).
5. **싱글톤 선-초기화·락** — `DashManager::Mgr()` 등 lazy-init을 메인 스레드 선-초기화 + 초기화 락(워커 투입 선결 조건).
6. **in-process 장시간 연산만 선별 워커화** — 모핑 DLL·파싱 등 CPU 점유 작업만 WorkerJob으로(전부 아님 — 5-1절 [[194-1-async-execution-patterns]]).

파일럿 = DOE 배치 경로(`runWbpjDoeAsync`의 `waitForFile` → `updatePrtGeometryCompleted` 구독, 참조 구현은 1-4절 `runDirectJobs`).

### 3-2. 도식 — 완료를 어떻게 되돌려 받나 (Job 표면 하나, 실행 주체 3갈래)

핵심 아이디어: 호출자는 "이게 외부 exe인지 워커 스레드인지" 모르게 하고, 완료 원천(QProcess 시그널·C 콜백·QFutureWatcher·파일 워처)은 Job 내부에서 흡수해 **밖으로는 Job 시그널 한 종류만** 낸다.

```
[요청] 위젯/PM이 Job 생성 — 종류 무관하게 시그널만 구독
   │   1. connect(job, started/progressed/finished) — "connect 먼저"
   │   2. job->start() — 즉시 반환, 메인 스레드는 이벤트 루프 상주 ("start 나중")
   ▼

[실행] Job 구현이 갈라짐 — 호출자에게는 비가시 (실행 주체 3갈래 — 예제 문서 4장 갈래 지도)
   │   1. ProcessJob (외부 one-shot exe) — 스레드 0개
   │      · QProcess는 본래 비동기. finished/runAsync를 Job 상태로 "번역"만
   │      · 취소 = 추적 PID kill (W6의 killOrphans 축소와 결합)
   │   2. DaemonCommandJob (외부 데몬 명령) — 스레드 0개
   │      · 명령 큐 commandCompleted·daemonReady 시그널을 Job 상태로 번역
   │   3. WorkerJob (in-process CPU) — 지정 스레드 풀에 함수 오프로딩
   │      · QtConcurrent::run(pool) + QFutureWatcher → 완료를 Job 시그널로 번역
   │      · "검토의견의 비동기 래퍼"가 바로 이것 (모핑 DLL·파싱)
   │   ※ 완료 변형 2 — 새 갈래가 아니라 Job 내부 디테일:
   │      · C API 런처 완료 = C 콜백 → invokeMethod 큐 마샬 → Job 번역
   │      · 파일 완료 판정 = "파일 존재" 폴링이 아니라 "완료 시그널 → 파일 검증" 순서
   │        (완료 시그널 없는 외부 산출물에 한해 QFileSystemWatcher/QTimer 보조)
   ▼

[완료] Job이 상태 시그널 방송 — 메인 스레드 문맥 보장 (QueuedConnection 마샬링)
       진행바(W11) · 실패 통지(W12) · Presentation Model(W21)이 같은 시그널 구독
```

### 3-3. 도식 — 스레드 모델 Before → After

```
[현재] 스레드 1개 — 이벤트 루프와 하위 작업을 겸함
   │   메인(GUI) 스레드: exec() + Morph() + reader.Update() + waitFor* ...
   │   → 하위 작업 실행 = 이벤트 루프 정지 (1장 전체)
   ▼

[W10 후] 메인은 통지만 받고, 무거운 in-process 작업은 워커로 분리
   │   메인(GUI) 스레드: exec() 상주 — Job 시그널 수신·UI 갱신만
   │   ├─ 외부 프로세스: 별도 OS 프로세스 (스레드 아님 — OS가 병렬 제공)
   │   │                  ProcessJob·DaemonCommandJob이 시그널로 완료 수신
   │   └─ 워커 풀 (선별): in-process DLL/파싱만
   │      · 모핑 직렬 풀 (maxThreadCount=1 — 비재진입 DLL 안전)
   │      · RW 직렬 풀   (maxThreadCount=1)
   │      · 완료는 QueuedConnection으로 메인 스레드에 마샬링
   │   ※ DLL 스레드 안전성 3등급(5-2절 [[194-1-async-execution-patterns]]):
   │      1=병렬 안전(확인된 것 없음) / 2=비재진입→직렬 풀(기본값) / 3=격리→외부 프로세스(NX, 이미 그렇게 함)
   ▼

[결과] "동시성이 아니라 응답성이 목표" — 워커는 GUI를 얼리지 않으려는 것이지 빠르게 하려는 게 아님
       메인 스레드는 항상 exec() 안 → 창 이동·리사이즈·취소가 실행 중에도 정상
```

### 3-4. 1-3절 3패턴이 각각 어떻게 바뀌나 (대응표)

```
패턴 A (순수 동기 — 모핑 DLL)     → WorkerJob (모핑 직렬 풀)
   │   입력을 시작 시점 스냅샷으로 고정(ExecuteMorphing은 이미 파라미터화됨) →
   │   워커에서 Morph() 실행 → 완료·진행을 Job 시그널로 → 메인 슬롯이 UI 반영
   │   효과: 얼어붙던 스피너(1-2절 t2 ※)가 진짜로 돌기 시작

패턴 B (폴링+processEvents — waitForFile) → 완료 시그널 구독 (DaemonCommandJob)
   │   enqueueUpdatePrtGeometry 후 updatePrtGeometryCompleted 시그널 구독으로 교체
   │   (나쁜 쌍둥이를 1-4절 runDirectJobs 모범으로 수렴 — 파일 검증은 시그널 뒤에)
   │   processEvents 제거 → 재진입 창 닫힘 (#64 종 소멸)

패턴 C (busy-wait — startDaemon)  → 데몬 비동기 기동
   │   while+waitForReadyRead 제거 → daemonReady 시그널 → 대기 큐 flush
   │   NX 120초 프리즈 소멸 (서브태스크 c)
```

### 3-5. 워커 투입 전 선결 조건 (스레드 도입의 대가)

외부 축(ProcessJob)은 스레드를 안 만들어 즉시 가능하지만, 워커 축(WorkerJob)은 "지금 사고를 안 내는 유일한 이유가 모든 코드가 한 스레드라 자동 직렬화되기 때문"이므로, 두 번째 스레드 등장 전에 공유 상태를 정리해야 한다. **없으면 프리즈가 레이스로 바뀐다.** 5건(상세는 [[203-2-worker-preconditions-analysis]], 서브태스크 e의 게이트):

1. 싱글톤 lazy-init 안전화 (`Mgr()`·`Instance()` 선-초기화 + 락)
2. `ExecuteMorphing` 공유 상태(`m_morphingOperator`) 소유권 분리
3. `DashAnalysisModelContext` 접근 규약 (직렬 워커 전용 또는 읽기 스냅샷)
4. 전역 `std::cout` rdbuf 스왑 제거 (`reader.Update()` 중 프로세스 전역 오염 — 레이스 시 영구 오리다이렉션)
5. GUI·VTK 객체 규칙 (메인 스레드 전용, 소유권 이전으로 넘김)

순서 강제: **선결 조건(d) → 워커 투입(e)**. 외부 축(a~c)은 이와 무관하게 선착수.

### 3-6. Job 소유권과 창 수명 — 창이 닫혀도 작업은 계속된다 (개정 1)

W10 후 "실행 중 창을 닫으면?"의 답은 소유권 규칙 하나로 정해진다: **Job(과 그 내부의 QProcess·QFutureWatcher)의 소유자는 뷰가 아니라 모델 계층이다** — 1-6절에서 실측한 창 무관 소유 체인이 그 숙주다. 위젯은 Job을 소유하지 않고 **구독**만 한다.

이 규칙 아래에서 창 닫힘·재열림의 의미:

```
[창 닫힘] 수신자 위젯 소멸 — 작업은 영향 없음
   │   1. Qt가 시그널 연결 자동 해제 — 이후 통지는 조용히 유실 (크래시 없음)
   │   2. ProcessJob: 외부 프로세스 계속 / WorkerJob: 워커 함수 계속
   ▼

[창 재열림] 시그널은 재생(replay)이 없음 — 놓친 통지는 돌아오지 않음
       state()/progress() pull 로 현재 상태 복구
       ([[194-1-async-execution-patterns]] 4절 계약 "구독" 규칙 2)
```

반대로 소유를 위젯에 두면 축마다 다르게 깨진다: WorkerJob은 돌던 함수가 완주는 하지만 watcher가 사라져 결과가 버려지고(작업 낭비), ProcessJob은 QProcess 소멸자가 자식 프로세스를 kill해 작업이 진짜로 죽는다. 1-6절의 뷰 소유 QProcess 2곳이 정확히 후자의 상태이며, W6 치환(2-2절) 때 실행 클래스 위임과 함께 소유도 모델 계층으로 옮겨 함께 해소된다.

경계 1건: 창 닫힘이 곧 앱 종료(메인윈도)인 경우는 별개 문제다 — closeEvent가 배치 취소를 호출하는 W7 경로 ([[194-1-async-execution-patterns]] 4-1절 정책 P2).

---

## 4. 종합 — 현재 → W6 → W10 진행 도식

```
[현재] 스레드 1개가 이벤트 루프 + 하위 작업 겸업, 실행 코드는 6곳 산재
   │   증상: 프리즈(120초 포함) · 재진입 크래시(#64) · 얼어붙는 진행 표시
   │   실측: processEvents 58(model 41+view 17) · waitFor* 23 · msleep 5 · QProcess 137
   ▼

[W3 선행] 외부 프로세스 안전핀 (백로그 — 본 문서 범위 밖, 4일)
   │   널 가드 · UTF-8 · 타임아웃 워치독 · 자식 정리 훅 — 즉효 취약점 차단
   ▼

[W6] 실행 경로 일원화 — 구조 (1.5주)
   │   1. one-shot QProcess 소비자 → 엔진 위임으로 수렴 (2-2절 — JobRunner는 부분, 개정 28)
   │   2. runAsync 버그 선수리 · killOrphans 축소 · 경로 카탈로그 일원화
   │   ※ 대기 모델은 아직 그대로 — W10이 뒤집을 "한 곳"을 만든 상태 (2-3절)
   │   DoD: 구조·행위 판정 5건 (2-1절 — grep QProcess는 소프트 추세 가드)
   ▼

[W10] 이벤트 구동 전환 — 동작 (4주, 파일럿 = DOE 배치)
   │   1. Job 상태머신 (ProcessJob / DaemonCommandJob / WorkerJob 3갈래, Job 표면 하나 — 3-2절)
   │   2. 파일 폴링 → 완료 통지 구독 · model processEvents 41곳 제거 · 데몬 비동기 기동
   │   3. 선결 5건(3-5절) 후 in-process 무거운 작업만 선별 워커화
   │   DoD: model processEvents 0 · GUI 스레드 waitFor*/msleep 0 (grep 수동 검증 — W9 자동 게이트는 선택)
   │        · #64 널 역참조 재현 시나리오 통과 · 실행 중 창 이동·리사이즈·취소 정상
   ▼

[이후] Job 시그널 표면이 후속 티어의 구독 대상이 됨
       W11 진행 UX · W12 실패 통지 · W21 Presentation Model 이 같은 시그널을 구독
       → 실행부 비동기화가 뷰 분리(W19~21)의 정지 작업 (판정 ④, 6절 [[194-1-async-execution-patterns]])
```

**한 줄로**: W6은 "실행을 한 곳에 모으고", W10은 "그 한 곳에서 기다림을 통지로 바꾼다". 둘 다 새 발명이 아니라, 코드 안에 이미 있는 모범(1-4절 `runDirectJobs`·`DashModelRunner`·DOE 워커)으로의 수렴이다.

---

## 5. 프레임워크 전달 메커니즘 — 입력은 어떻게 슬롯까지 오나 (현재 vs W10)

본 장은 1~4장의 밑에 깔린 **프레임워크 전달 메커니즘**을 심화로 따로 정리한다 — Qt가 작업을 **어떻게** 슬롯까지 전달하고, 슬롯 이후는 왜 "전달"이 아니며, W6·W10이 정확히 **어느 전달 경로를 새로 만드는지**의 근거다. 앞 장이 "무엇이 바뀌나"라면 본 장은 "그 밑에서 무엇이 오가나"다. (완료 회수의 구현 상세는 3-2·3-3절 — 본 장은 그 앞단의 전달 메커니즘만 다뤄 중복을 피한다.)

### 5-1. QApplication은 디스패처지 실행기가 아니다

흔한 오해: "사용자 신호가 들어오면 QApplication에 작업을 전달해 실행시킨다". 방향이 반대다.

- **QApplication/이벤트 루프의 역할 = 큐에서 이벤트를 꺼내(pull) 대상 슬롯을 호출(call)하는 것.** "디스패치"란 슬롯 함수를 부르는 것일 뿐이고, **슬롯이 곧 작업**이라 슬롯이 스스로 실행한다. 작업이 어딘가 백엔드 실행기로 넘어가는 게 아니다 — QApplication은 실행기(executor)가 아니라 이벤트 디스패처다.
- **같은 스레드 안의 시그널/슬롯 = `DirectConnection` = 그냥 동기 함수 호출.** "메시지 전달"이 아니다. 진짜 큐 기반 전달(`QueuedConnection`)은 **스레드를 건널 때만** 일어나는데, 현재는 그게 거의 없다(DOE 워커·FE C콜백 마샬링 정도가 예외).
- **귀결**: 현재 코드에는 "뒷단 작업 전달 경로"가 사실상 없다. 버튼 슬롯 → `DashManager` → DLL 은 전달이 아니라 **한 스레드 동기 콜스택**이고(1-2절 t2), 그래서 이벤트 루프가 멈춘다.

### 5-2. 도식 — 입력이 슬롯까지 오는 경로 (프레임워크 몫, W10 불변)

현재 유일하게 **진짜 큐 핸드오프**가 존재하는 구간이다. 그리고 W10은 이 구간을 한 줄도 바꾸지 않는다 — 클릭이 슬롯에 도달하는 방식은 Qt의 일이다.

```
[OS] 사용자가 "Run" 버튼 클릭
   │   Windows가 창 메시지(WM_LBUTTONUP)를 DashGUI2.exe 에 전달
   ▼

[Qt 플랫폼 플러그인] OS 메시지 → QMouseEvent 변환 → Qt 이벤트 큐에 post
   │   ★ 큐 기반 전달이 실제로 존재하는 (현재) 유일한 구간
   ▼

[main.cpp:83 · app.exec() = 이벤트 루프] 큐에서 이벤트 하나 꺼냄(dequeue)
   │   1. 대상 위젯(버튼)에 QMouseEvent 배달
   │   2. QAbstractButton 이 clicked() 시그널 emit
   │   3. connect된 슬롯 호출 — 같은 스레드 → DirectConnection → 동기 함수 호출
   ▼

[슬롯 진입 · 메인 스레드] 여전히 app.exec() 콜스택 안
```

### 5-3. 슬롯 도달 이후 — 현재는 전달이 여기서 끊긴다 (W10이 잇는 지점)

슬롯이 호출된 뒤가 갈림길이다. **입력 배달(5-2절)은 그대로 두고, W10은 슬롯의 "끝"만 바꾼다**:

```
[슬롯 진입 이후]
   │   현재:  Morph() 를 그 자리서 동기 실행 → 콜스택 안 풀림 → 이벤트 루프 정지
   │          (뒷단으로의 전달 없음 — 작업이 메인 스레드에 눌러앉는다)
   │   W10 :  입력 스냅샷 → Job 생성 → 시그널 connect → job->start() → 즉시 반환
   │          job->start() 가 처음으로 작업을 뒷단으로 넘긴다 (아래 ②)
   ▼

[완료 회수] 뒷단이 끝나면 완료가 메인 이벤트 큐로 돌아옴 (아래 ③)
       구현 상세(ProcessJob / DaemonCommandJob / WorkerJob / QueuedConnection 마샬링)는 3-2·3-3절
```

### 5-4. 큐 전달 경로 개수 — 현재 1개 → W10 3개

W10의 본질을 전달 경로 수로 요약하면: **현재는 입력 배달 1개뿐인데, W10이 뒷단 전달 2개를 새로 만든다.**

| 전달 경로 | 방향 | 현재 | W10 후 |
|---|---|---|---|
| ① 입력 배달 | OS → 이벤트 큐 → 루프 → 슬롯 | 있음 (프레임워크) | **그대로** — W10 무관 |
| ② dispatch-out | 메인 슬롯 → 뒷단 (워커 풀 / 외부 프로세스) | **없음** (동기 콜스택) | **신설** — `job->start()` |
| ③ completion-back | 뒷단 → 메인 이벤트 큐 → 완료 슬롯 | **없음** (예외 2건 제외) | **신설** — `QueuedConnection` / QProcess 시그널 |

②·③이 곧 "뒷단 작업 전달 경로"의 실체다. 현재 이 둘이 없어 작업이 메인 스레드에 눌러앉고(정지), W10이 이 둘을 만들어 메인을 해방한다. 이후 진행바(W11)·실패 통지(W12)·Presentation Model(W21)은 모두 ③의 완료 시그널을 구독한다 — 그 결과 상태는 3장·4장에서 상술했다.

---

## 6. 참고

- 개념: [[193-1-async-execution-models]] (이벤트 루프·시그널·Job·스레드 층위)
- 판정·상세: [[194-1-async-execution-patterns]] (완료 처리 3방식·DLL 3등급·선결 5건·서브태스크 a\~f·취소/실패 정책 P1\~P5)
- 코드 레벨 최소 구현 예제: [[205-5-w6-w10-async-minimal-example]] (Qt 정상 패턴 → ProcessRunner(W6) → Job/ProcessJob/DaemonCommandJob/WorkerJob(W10) 골격 · 4장 갈래 지도 · 8장 동기→비동기 전환 대상 전수 부록)
- 선결 조건 상세: [[203-2-worker-preconditions-analysis]]
- QProcess 안티패턴 전수: [[201-1-qprocess-antipattern-catalog]] (개정 1: 커밋 기준 재검증 · 8절 view 계층 17곳 전수·아종 2분류 · 13절 음성 판정)
- 실행 순서·규모: [[200-3-prioritized-backlog]] 5-1절 · [[198-1-improvement-roadmap]] Phase 1~2
- 실측 코드 앵커 (재검증 2026-07-21, `dev` 커밋 `52965e4`): `controller/DashExtensionProcess.cpp:150-161`(startDaemon busy-wait) · `model/DashJobRunner.cpp:2351-2364`(waitForFile 폴링)·`:2673`(runWbpjDoeAsync 나쁜 쌍둥이)·`:2326-2336`(runDirectJobs 모범)·`:333`(FE C콜백 마샬링) · `controller/DashMorphingDoeExecutor.cpp:163~`(모핑 동기 루프)
- 소유 구조 앵커 (1-6절, 재검증 2026-07-21, `dev` 커밋 `52965e4`): `controller/DashManager.cpp:206`(부모 없는 싱글톤)·`:92-108`(NX·데몬 3 소유) · `controller/DashProjectManager.cpp:13` · `model/DashProject.cpp:79` · `model/DashAnalysisLauncher.cpp:51` · `view/DashOptimizerWidget.cpp:2418`·`view/dialog/TopOptPostprocessDialog.cpp:1749`(뷰 소유 QProcess 2곳)
