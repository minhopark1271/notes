# EXE 작업 목록

> dev @ b08a91b3. 열린 PR 7건 중 머지 대상 6건(#651 #652 #654 #655 #656 #658 — #530 은 재업로드 노선이라 머지 대상이 아니다, C-2 ②⑩) 중 `controller/async/*` · `DashExtensionProcess` · `DashDaemonLifecycle` · `DashThreadAffinity` 를 만지는 것은 없다. `view/DashMainWindow.cpp` 는 #651 #652 #654 #655, `controller/DashManager.cpp` 는 #652 #654, `controller/DashMorphingService.h` 는 #654, `tests/CMakeLists.txt` 는 #651 #652 #654 #655, `controller/DashDoeBatchChain.{cpp,h}`·`tests/TestDoeBatchChain.cpp` 는 #654 #655, `controller/DashRwActor.cpp`·`controller/DashRwDocument.{cpp,h}`·`controller/DashRwDocumentHandle.h`·`tests/TestRwDocument.cpp`·`tests/rw/FakeRwModule.h` 는 #658(draft, Coupling 수용) 이 만진다. #656 은 EXE 항목과 겹치는 파일이 없다.
> 규모는 00-plan 1-3 파일 수 기준 — `S` 파일 3개 이하 · `M` 8개 이하. 공수가 작아도 파일이 4개 이상이면 M 으로 적는다 (검토 #11).
> 순서 골격: EXE-01(계약) → EXE-02(취소) → EXE-03(훅) → EXE-04(레인, 조건부). 표시·가드 축은 EXE-07(규약) → EXE-08 · EXE-09. 프로세스 축은 EXE-10(통지 규칙) → EXE-11 · EXE-12. RW 축은 EXE-14(실측·결정) → EXE-22(#458 적재 워커화, 조건부). 모듈 펌핑 제거(#454 #456 #457 #512 #513) 는 EXE-04 또는 EXE-01 의 "단일 슬롯 유지" 결정 뒤에 착수한다.
> Phase B 이관: #458 담당 RUN → EXE (EXE-22) · CON-U5 테스트 공백 → EXE-21 · MOR-c10 계측 → EXE-14 · CAD-c13/c31 → EXE-12 · ANA-c29 → EXE-03.
> C' 반영(2026-10-06): 215-2 4절 → EXE-01 · 7절 → EXE-07 (claims EXE-c61 · c62 신설) · EXE-12 종류 DEC → PR · EXE-14 종류 DEC → INV · EXE-09 바인더를 Widgets-free 로 재설계 · 좌표 정정(RW 액터 생성자 · readFeCondition · registry.load 전수) · 규모 5건 S → M. 항목 신설·삭제 없음(22건 유지).

### EXE-01 · 실행 기반 계약 1종을 결정한다 — 레인(자원 키) · 재요청 정책 · 종료 경로 상한
- 종류: DEC | 규모: S | 태그: B · refactor
- 목표: DashAsyncJobRunner 의 "전역 단일 슬롯 · 거부" 를 유지할지, 215-2 3절·9절대로 자원 ID 별 레인(예: `PreprocessReader` · `AnalyzerCache` · `ModelRunnerScan`)으로 넓힐지 정한다. 레인을 두면 레인마다 재요청 처분(거부/대기)과 10절 큐 4정책(깊이·합치기·대기 취소·순서)의 미도입 사실을 함께 기록한다. 워커 기제 3종(DashAsyncJobRunner · DashMorphingService · DashDoeSampler 직접 QtConcurrent)의 병존 범위와 종료 경로 동기 대기 상한(drainAll · shutdownBlocking · MorphingService waitForDone)도 같은 기록에 넣는다.
- 완료 기준: 결정 기록 1건 — (1) 레인 목록 표(자원 → 키 → 재요청 처분) 또는 "단일 슬롯 유지" 선언 (2) #454 #456 #513 각 작업이 어느 레인에 제출하는지 1행씩 (3) 종료 대기 상한 표 3행 (4) 215-2 4절 "통지 출처 식별" 이 현행 수단으로 이미 충족된다는 1행 — 작업은 `QUuid`(`DashAsyncJobRunner.cpp:43`), 데몬 명령은 `commandId`(`currentCommandId()`), 완료 핸들러가 훅보다 먼저 `contexts_.take(jobId)` 로 자기 작업만 뺀다(`:52`). 레인을 도입해도 키가 `QUuid` 라 전제는 유지됨을 함께 적는다
- 변경 범위: 문서만 (docs/ThreadingContract.md 초안의 "실행 계약" 절 — EXE-05 가 파일을 만들면 거기에, 아니면 notes)
- 선행: -
- 충돌: B2 교집합: ThreadingContract.md → EXE-05 EXE-07
- 흡수: #451(공통 기반) · EXE-c01, c02, c03, c20, c61 · 215-2 2·3·4·9·10·13절
- 비고: #552 범위 밖 절이 "선점·예약·큐잉 안 함" 을 이미 고정했으므로 현실적 선택지는 "단일 슬롯 유지" 와 "자원별 단일 슬롯" 둘. 모듈 셋이 서로 반려하는 것이 수용 가능하면 전자가 가장 싸다. 모핑 서비스는 mesh-ops 스레드 예산과 결합돼 통합 대상에서 뺀다.

### EXE-02 · DashAsyncJobContext 에 협조적 취소와 진행률 소스를 넣는다 (#552)
- 종류: PR | 규모: M | 태그: B · feature
- 목표: `QtConcurrent::run` 을 `QPromise<DashJobResult>&` 오버로드로 바꾸고 `Job::cancel()` 을 오버라이드해 `watcher_.future().cancel()` 로 잇는다. `DashAsyncJobRunner::cancel(QUuid)`·`cancelAll()` 을 공개하고 `main.cpp` 종료 경로를 `cancelAll() → drainAll()` 로 바꾼다. `onWorkFinished` 가 `isCanceled()` 를 먼저 보고 `State::Cancelled` 로 가게 해 빈 결과 읽기를 막는다. `QPromise::setProgressValue` 를 `Job::progressed(int)` 의 소스로 잇는다.
- 완료 기준:
  1. tests/TestAsyncJob.cpp 에 "cancel 중 작업은 Cancelled 로 끝나고 onSuccess/onFailure 가 돌지 않는다" · "cancelAll 뒤 drainAll 이 즉시 돌아온다" · "setProgressValue 가 progressed 를 낸다" 3건 추가·통과
  2. `git grep "취소는 없다" controller/async` 0건 · `git grep "소비자 없음" controller/async` 0건(`Job.h:37` 의 `progressed` 주석이 거짓이 되지 않게 함께 고친다) · `Job::cancel()` 기본 no-op 을 쓰는 Context 없음
  3. 대용량 XML 플롯 중 창 닫기에서 종료 지연이 "현재 work 종료까지" 에서 "협조 지점까지" 로 줄어듦(실측 기록) — SDK 내부 파싱은 안 끊기는 한계를 PR 본문에 명시
- 변경 범위: controller/async/Job.h(`progressed` 주석 1줄 — "소비자 없음 — W6-x 후속 예정" 삭제) · controller/async/DashAsyncJobContext.h · DashAsyncJobContext.cpp · DashAsyncJobRunner.h · DashAsyncJobRunner.cpp · main.cpp · tests/TestAsyncJob.cpp
- 선행: -
- 충돌: EXE-03 · EXE-05 (같은 async 파일) — EXE-02 를 먼저 랜딩한다 (#553 본문의 순서) · B2 교집합: main.cpp → DEV-21 DEV-24 EXE-06 PRJ-06 PRJ-14 UIC-05 UIC-26 · DashAsyncJobRunner.cpp → EXE-04 · DashAsyncJobRunner.h → EXE-04 EXE-08 · TestAsyncJob.cpp → EXE-04 EXE-09 · DashAsyncJobContext.h → EXE-04
- 흡수: #552 · #543(취소 표면의 전제) · EXE-c12, c13, c20(drainAll 부분)
- 비고: 취소는 협조적이다 — 첫 소비자 `DashDataLoader::prefetchXml` 은 안 끊긴다. 이 사실을 PR 과 헤더 주석에 적지 않으면 "취소가 안 된다" 가 버그로 올라온다. 선점(도는 작업 취소 후 새 것 시작)은 범위 밖.

### EXE-03 · DashAsyncJobRunner::run 을 준비·실행·완료 훅 구조체로 바꾸고 Job::State 에 Skipped·Aborted 를 더한다 (#553)
- 종류: PR | 규모: M | 태그: B, E · refactor
- 목표: `run(work, onSuccess, onFailure)` → `run(DashAsyncJobHooks{preExecution, execution, postExecution})`. `preExecution`(GUI, `DashJobPreparation {Proceed, SkipExecution, Abort}` 반환) 은 `run()` 안 인라인으로 돌되 execution 과 같은 예외 정규화를 건다. `postExecution(Job::State, const QString&)` 은 어떤 종결에도 반드시 1회 불린다(취소 포함). `Job::State` 에 `Skipped`·`Aborted` 를 추가하고 `setState` 터미널 락에 넣는다. 유일 호출부 `DashResultsAnalyzerWidget::onPlotSpecReady` 의 동기 분기를 `SkipExecution` 한 줄로 옮겨 호출 갈래를 하나로 만든다.
- 완료 기준:
  1. `git grep -n "run(" controller/async/DashAsyncJobRunner.h` 가 훅 구조체 시그니처 1개만 보임 · 위치 인자 3개 오버로드 없음
  2. tests/TestAsyncJob.cpp — "pre 가 SkipExecution 이면 execution 없이 post 가 Skipped 를 받는다" · "pre 가 Abort 면 Aborted" · "pre 가 던지면 Aborted 로 정규화되고 슬롯이 풀린다" · "cancel 뒤 post 가 Cancelled 로 1회" 4건 추가·통과. tests/TestJobState.cpp 에 Skipped/Aborted 터미널 락 1건
  3. `DashResultsAnalyzerWidget::onPlotSpecReady` 에 `DashPlotRequestHandler::build` 호출이 1곳(post 안) — 동기 경로 조기 반환 블록 소멸
- 변경 범위: controller/async/Job.h · DashAsyncJobContext.h · DashAsyncJobContext.cpp · DashAsyncJobRunner.h · DashAsyncJobRunner.cpp · view/DashResultsAnalyzerWidget.cpp · tests/TestAsyncJob.cpp · tests/TestJobState.cpp
- 선행: EXE-02
- 충돌: EXE-04 · EXE-05 · EXE-08 (DashAsyncJobRunner.h) · ANA 의 DashResultsAnalyzerWidget.cpp 항목 · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · TestAsyncJob.cpp → EXE-09
- 흡수: #553 · EXE-c14, c15, c53 · ANA-c29 · EXE-c60 (호출부 — ANA 이관)
- 비고: 훅 간 데이터는 캡처로만(값 또는 `shared_ptr<페이로드>`, QObject·VTK 금지; GUI 객체는 `QPointer`) — 템플릿 체이닝·슬롯별 래퍼 금지(#553 "안 하는 것"). `Job::State::Skipped` 는 실패가 아니라는 주석을 enum 에 적고 ProcessJob 에는 도입하지 않는다 — 도입 시 `== Succeeded` 소비자 6곳을 함께 본다. 파일 8개지만 순변경 ~150줄.

### EXE-04 · DashAsyncJobRunner 를 자원 키별 레인으로 확장한다 (EXE-01 조건부)
- 종류: PR | 규모: M | 태그: B · feature
- 목표: EXE-01 이 레인을 택했을 때 — `run(hooks, DashJobLane lane)` 으로 레인 키를 받고 `contexts_` 를 레인별 단일 슬롯으로 바꾼다. `anyRunning()`·`isRunning()` 에 레인 인자를 더하고 UI 차단 훅은 "어느 레인이든 1개 이상 실행 중" 으로 집계한다. `cancelAll()`·`drainAll()` 은 전 레인.
- 완료 기준:
  1. tests/TestAsyncJob.cpp — "다른 레인은 동시에 돈다" · "같은 레인은 반려" · "두 레인 중 하나가 끝나도 다른 레인이 남아 있으면 UI 차단이 유지된다" 3건 추가·통과
  2. 기존 14건 테스트 무변경 통과 (기본 레인 = 종전 단일 슬롯)
- 변경 범위: controller/async/DashAsyncJobRunner.h · DashAsyncJobRunner.cpp · DashAsyncJobContext.h · tests/TestAsyncJob.cpp · view/DashResultsAnalyzerWidget.cpp (레인 지정)
- 선행: EXE-01, EXE-03
- 충돌: EXE-08 (DashAsyncJobRunner.h 훅 시그니처) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · DashAsyncJobRunner.cpp → EXE-02 EXE-05 · DashAsyncJobRunner.h → EXE-02 · TestAsyncJob.cpp → EXE-02 EXE-09 · DashAsyncJobContext.h → EXE-02
- 흡수: #451(공통 기반 "직렬 실행 풀") · EXE-c03 · 접점 #454 #456 #513 의 선행
- 비고: EXE-01 이 "단일 슬롯 유지" 로 결정하면 이 항목은 CLOSE. 레인은 `QThreadPool` 을 늘리는 것이 아니라 슬롯 집계를 키로 나누는 것 — 전역 풀 그대로.

### EXE-05 · 메인 스레드 게이트를 DASH_ASSERT_MAIN_THREAD 로 통일하고 docs/ThreadingContract.md 를 쓴다
- 종류: PR | 규모: M | 태그: B, E · refactor, docs
- 목표: 수제 `QThread::currentThread() == qApp->thread()` assert 5곳(DashAsyncJobContext 3 · DashAsyncJobRunner::run · **DashRwActor 생성자** `DashRwActor::DashRwActor()` 의 `:98` — `instance()`(:88-91) 는 Meyers 싱글턴 2줄이라 assert 가 없다) 을 `DASH_ASSERT_MAIN_THREAD("…")` 로 바꾼다(소유 스레드 검사 2곳 `assertActorThread`·`assertServiceThread` 는 의미가 달라 유지). 헤더가 정본으로 가리키는 `docs/ThreadingContract.md` 를 만든다 — 훅 스레드 고정(pre/post=GUI, execution=워커), 캡처 규약, 워커 금지 목록(위젯·VTK 렌더 객체·GUI 전용 싱글턴), LEAF RULE 과 교착 방지(blocking invoke 소유자는 호출자를 역호출하지 않는다), 203-2 D5 타입 화이트리스트, 215-2 Q12 의 대기 3계급(소멸자 암묵 대기·blocking 마샬링·join) 검사 목록.
- 완료 기준:
  1. `git grep -nE "currentThread\(\) == (qApp|QCoreApplication::instance\(\)|app)->thread\(\)" -- '*.cpp' '*.h' ':!controller/DashThreadAffinity.h' ':!view/common/DashNotify.cpp' ':!tests/*'` 0건
  2. docs/ThreadingContract.md 존재 · docs/index.md 에 링크 · 위 6개 절 각 1개 이상 규칙
  3. 전체 테스트 통과(동작 불변)
- 변경 범위: controller/async/DashAsyncJobContext.cpp · controller/async/DashAsyncJobRunner.cpp · controller/DashRwActor.cpp · docs/ThreadingContract.md(신규) · docs/index.md
- 선행: -
- 충돌: EXE-02 · EXE-03 (같은 async .cpp) — 둘 뒤에 랜딩하는 편이 충돌이 작다 · B2 교집합: DashAsyncJobRunner.cpp → EXE-04 · ThreadingContract.md → EXE-01 EXE-07 · index.md → DEV-12 DEV-13 · DashRwActor.cpp → EXE-22 · PR #658(DashRwActor.cpp)
- 흡수: #451(공통 기반 "메인 스레드 게이트 확산" · 구 #452) · EXE-c05, c06 · 203-2 D5 · 215-2 12절·다음 단계 3번 · EXE-c41(규칙 몫)
- 비고: `DashNotify.cpp:23` 의 스레드 검사는 "GUI 가 아니면 큐잉" 분기라 assert 대상이 아니다. EXE-01 결정 기록의 자리이기도 하다.

### EXE-06 · 싱글톤 lazy-init 을 메인 스레드 선-초기화와 생성자 가드로 고정한다 (203-2 D1)
- 종류: PR | 규모: S | 태그: B · refactor
- 목표: `main.cpp` 에서 QApplication 생성 직후 `DashManager::Mgr()`·`DashProjectManager::Instance()` 를 1회 선호출하고, 두 생성자에 `DASH_ASSERT_MAIN_THREAD` 를 둔다. 워커가 첫 호출자가 되는 경로를 구조적으로 막는다(203-2 처방 A). magic static 전환(처방 B)은 `atexit(Destroy)` 정리와 얽혀 범위 밖.
- 완료 기준:
  1. main.cpp 에 두 선호출 존재 (`app` 생성과 `DashMainWindow` 생성 사이)
  2. DashManager · DashProjectManager 생성자에 `DASH_ASSERT_MAIN_THREAD` 1줄씩
  3. 앱 기동·종료 회귀 없음
- 변경 범위: main.cpp · controller/DashManager.cpp · controller/DashProjectManager.cpp
- 선행: -
- 충돌: PR #652 · #654 (controller/DashManager.cpp) · PRJ 의 DashManager 항목 · B2 교집합: DashManager.cpp → CAD-03 CAD-06 DOE-19 PRJ-03 PRJ-04 PRJ-06 PRJ-14 REN-07 · DashProjectManager.cpp → PRJ-08 PRJ-12 PRJ-13 PRJ-19 PRJ-35 PRJ-36 REN-10 · main.cpp → DEV-21 DEV-24 EXE-02 PRJ-06 PRJ-14 UIC-05 UIC-26
- 흡수: 203-2 D1 · EXE-c07
- 비고: DashProjectManager 는 소멸 경로가 없다(비대칭) — 고치지 않는다, PRJ 에 메모만 남긴다.

### EXE-07 · 진행 표시·차단·반려 안내 규약 1종을 정한다 (#462 · #543 결정 축)
- 종류: DEC | 규모: S | 태그: B, D · docs
- 목표: Job 상태 → 화면 매핑 1종 — `Running(진행률 없음)` = 상태바 무한 진행바 + 문구, `Running(진행률 있음)` = 결정 진행바, `Cancelled/Failed` = 통지 규칙(EXE-10) 으로 위임. 차단 범위(최상단 전체 vs 콘텐츠만 — DashTitleBar·QSizeGrip 제외 여부), 반려 안내(비모달 상태바 문구 vs 침묵), `setUIEnabled`+`showLoadingIndicator` 짝과의 관계(통합/용도 분리), 취소 버튼의 자리(상태바 진행바 옆), 모달 여부를 결정한다. 현행 6방식(EXE-c21) 의 처분(수렴/존치)을 표로 남긴다. 215-2 7절 "상태 writer 단일화" 의 횡단 조항도 여기에 둔다 — **진행 표시·버튼 활성의 근거는 Job/프로세스 상태이고 외부 도구가 쓰는 상태 파일 폴링에 묶지 않는다**, 상태 항목마다 writer 1명, 늦은 쓰기 우선순위는 "종결 고정"(터미널 락과 같은 규칙).
- 완료 기준: 결정 기록 1건 — (1) 상태 → 표시 매핑 표 (2) 차단 대상 목록 (3) 6방식 처분 표 (4) 반려 안내 형태 (5) 상태 writer 조항 1항 + 현행 위반 사례 2행(BLD 1Hz status 폴링 EXE-c37 · 설정 JSON RMW EXE-c41) — 수정은 각 모듈
- 변경 범위: 문서만 (docs/ThreadingContract.md 의 "표면" 절 또는 별도 docs)
- 선행: EXE-01 (취소·재요청 정책이 표면을 정한다)
- 충돌: B2 교집합: ThreadingContract.md → EXE-05
- 흡수: #462 · #543(결정 4축) · EXE-c16, c17, c18, c19, c21, c62 · 215-2 7·11절 · OPT-D13(표준 몫)
- 비고: 저비용 선행 — #463 확산과 EXE-08·09 가 이 규약을 소비한다. 프레임리스 창(`DashMainWindow.cpp:172`) 이라 "창 이동을 살린다" 는 결정은 곧 DashTitleBar·QSizeGrip 을 차단 목록에서 빼는 결정이다.

### EXE-08 · 비동기 작업의 차단·진행 표시를 규약대로 고친다 (#543 구현)
- 종류: PR | 규모: M | 태그: B, D · feature
- 목표: EXE-07 결정대로 — `setUiBlockHooks` 의 차단 대상을 규약 목록으로 바꾸고(타이틀바·사이즈그립 제외가 결정이면 `DashTitleBar`·`QSizeGrip` 을 건너뜀), 상태바 진행바에 작업 문구(훅 구조체의 label) 와 `Job::progressed` 진행률을 싣고, 반려 시 상태바 안내 1줄, 취소 버튼을 `DashAsyncJobRunner::cancel` 에 잇는다. `TODO(#543)` 를 지운다.
- 완료 기준:
  1. `git grep "TODO(#543)"` 0건
  2. 대용량 XML 플롯 중 창 이동·리사이즈 가능(결정이 "살린다" 일 때) · 상태바에 문구 표시 · 취소 클릭 시 `Cancelled` 로 종결되고 UI 복구
  3. tests/TestAsyncJob.cpp `uiBlockHooksWrapJobLifecycle` 통과 + 반려 안내 훅 1건 추가
- 변경 범위: view/DashMainWindow.h · view/DashMainWindow.cpp · controller/async/DashAsyncJobRunner.h (훅 시그니처에 문구·진행률) · view/DashResultsAnalyzerWidget.cpp (문구 지정)
- 선행: EXE-02 (취소) · EXE-03 (훅 구조체) · EXE-07 (규약)
- 충돌: PR #651 · #652 · #654 · #655 (view/DashMainWindow.cpp — #655 는 +1/-10) · EXE-04 (DashAsyncJobRunner.h) · PRJ/UIC 의 DashMainWindow 항목 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · DashMainWindow.h → 공유 11건(deps.md 5절)
- 흡수: #543 · EXE-c16, c17, c18
- 비고: `setUIEnabled` 계열 통합이 결정되면 범위가 M 으로 커진다 — 그 경우 통합은 별 항목으로 쪼갠다(PRJ 접점).

### EXE-09 · 실행 중 재클릭 가드 표준을 헬퍼로 제공하고 기준 적용 1곳을 바꾼다 (#461)
- 종류: PR | 규모: M | 태그: B, D · feature
- 목표: 바인더를 **층별로 두 조각**으로 나눈다 — (a) `controller/async/DashJobGuard.{h,cpp}`: `Job`(또는 `isRunning` 을 내는 러너) 의 시작·종결에 맞춰 `std::function<void(bool enabled)>` 싱크를 부르고, 실행 중 재진입 요청을 거부 로그 + 안내 훅(`std::function<void(const QString&)>`, EXE-07 규약) 으로 번역한다. QtWidgets 를 들이지 않는다 — `controller/async/DashAsyncJobRunner.h:7` 이 그 층의 의존을 "Qt + Job.h + 로거까지" 로 선언하고 테스트 타깃 `test_async_job` 이 Core·Concurrent·Test 만 링크한다(`tests/CMakeLists.txt:54-60`). (b) `view/common/DashJobGuardWidgets.h`: `QAbstractButton*` 목록을 (a) 의 싱크로 접어주는 인라인 편의 오버로드. 표준 문장(버튼 비활성 + 모델 가드 + 거부 로그 + 안내)을 ThreadingContract 또는 통지 규칙 문서에 적는다. 기준 적용은 EXE 소유 러너 `DashTopOptPostprocessRunner` ↔ `TopOptPostprocessDialog`(현행: `QMessageBox::warning("Busy")` + 러너 WARN 로그, 버튼 열림).
- 완료 기준:
  1. tests/TestAsyncJob.cpp (Core·Concurrent·Test 하네스 그대로) — "Running 동안 싱크가 `false`, 종결(성공·실패·취소) 후 `true` 로 1회씩 불린다" · "실행 중 재요청은 거부되고 안내 훅이 1회 불린다" 2건. 버튼 비활성은 (b) 가 싱크를 호출하는 한 줄이라 자동 테스트 대상이 아니다 — 2번의 수동 확인으로 덮는다
  2. TopOptPostprocessDialog 의 실행 버튼이 `isRunning()` 동안 비활성 · `QMessageBox::warning(this, "Busy", …)` 삭제 (수동 시나리오 1건을 PR 본문에)
  3. 모듈 확산(#463) 이 이 헬퍼만 쓰면 되도록 (a) 의 공개 API 가 Job 과 러너 둘 다 받고, (b) 가 위젯 목록을 받음
- 변경 범위: controller/async/DashJobGuard.h(신규) · DashJobGuard.cpp(신규) · view/common/DashJobGuardWidgets.h(신규) · view/dialog/TopOptPostprocessDialog.cpp · tests/TestAsyncJob.cpp · tests/CMakeLists.txt (`test_async_job` 소스에 `DashJobGuard.cpp` 추가 — Widgets 링크는 늘리지 않는다)
- 선행: EXE-07
- 충돌: OPT/PRJ 의 TopOptPostprocessDialog 항목 · #455 (같은 파일의 processEvents 6곳) · B2 교집합: tests/CMakeLists.txt → 공유 12건(deps.md 5절) · TestAsyncJob.cpp → EXE-02 EXE-03 EXE-04 · TopOptPostprocessDialog.cpp → DEV-20 PRJ-26 REN-07 · PR #655(tests/CMakeLists.txt) · PR #654(tests/CMakeLists.txt) · PR #652(tests/CMakeLists.txt) · PR #651(tests/CMakeLists.txt)
- 흡수: #461 · EXE-c22 · OPT-D13(표준 몫) · DOE-D11(표준 몫)
- 비고: #315(Load 재클릭)·#221(모듈 진입 상태) 은 비범위(#461 not-to-be). 모듈별 적용은 #463 → 각 모듈 항목. 층을 가르는 이유는 테스트 하네스다 — `tests/CMakeLists.txt` 에서 Widgets 를 무조건 링크하는 타깃은 `test_analyzer_utils_cache`(:324-333) 하나이고 나머지 2개(`test_result_processor`·`test_real_result_files`)는 Preprocessor·VTK 가 있을 때만 켜진다. 바인더가 `QAbstractButton` 을 직접 받으면 `test_async_job` 에 Widgets 를 새로 들여야 하고, 그러면 그 파일이 지키는 "Qt Core + Test only" 성질(:388-394 주석)이 깨진다.

### EXE-10 · 외부 프로세스 실패 통지 규칙을 세운다 (#466 · #482 와 문서 공유)
- 종류: DEC | 규모: S | 태그: B, D · docs
- 목표: 규칙 — (1) 실행층 종결(`Job::finished` Failed/Cancelled · `commandFailed` · `died`) 은 소비 모델이 도메인 시그널로 번역하고 **뷰가 반드시 구독한다** (connect 0 금지 — OPT-D11 류를 리뷰 게이트로 막는다) (2) 수단: 사용자 행위의 실패 = `DashNotify::error/warning`(모달), 배경 작업·배치 케이스 = 상태 열/상태바(비모달), 취소 = 통지 없음 (3) 메시지 포맷: 실행층 사유 문자열(현행 한글 리터럴 "종료 코드 %1" 등) 은 로그용이고 사용자 문구는 소비자가 만든다 (4) 리뷰 체크리스트 3줄. #482 와 같은 문서를 쓴다 — 먼저 착수하는 쪽이 만든다.
- 완료 기준: 결정 기록 1건 — 규칙 4항 + 체크리스트 · 현행 미결합 목록(OPT-D11 외 `*Failed` 시그널 중 view connect 0건) 1표
- 변경 범위: 문서만
- 선행: -
- 충돌: UIC-16 (#482 — 같은 문서)
- 흡수: #466 · EXE-c24, c54 · OPT-D11(규칙 몫) · 215-2 6절
- 비고: 개별 수정(#323 #324 #393 #394, OPT-D11) 은 각 소유 이슈·모듈. 실행층의 "무음 폐기 금지" 는 이미 구현·테스트돼 있다(TestProcessRuntime `missingDaemonExeFailsQueuedCommand` · `readyTimeoutFailsQueuedCommands` 등) — 규칙은 소비자 층을 겨냥한다.

### EXE-11 · 데몬 명령 응답 타임아웃을 무활동 기반으로 넣는다 (#467)
- 종류: PR | 규모: M | 태그: B · bug
- 목표: `DashExtensionProcess` 에 명령 진행 중 stdout 무활동 상한(`setCommandInactivityTimeoutMs`, 기본값은 결정 필요 — 후보 10분) 을 두고, 만료 시 진행 명령을 `commandFailed("no output for N ms")` 로 마감한 뒤 `stop()` 경유로 데몬을 세운다(stop 5s → kill 승격은 기존). 타이머 수명은 `m_waitingFinished` 구간과 같게 `setState`/`trySendNext`/`handleDaemonLine` 에 묶는다. 기동 타임아웃(30s/NX 120s)·정지 타임아웃(5s) 은 이미 있어 손대지 않는다.
- 완료 기준:
  1. tests/TestProcessRuntime.cpp — daemon_stub 에 "명령 받고 침묵" 모드 추가, "무활동 만료 시 commandFailed 1회 + stopped" · "출력이 이어지면 만료 안 함" 2건 통과
  2. 기존 24건 통과(기본값이 충분히 커서 스텁 시나리오에 영향 없음)
  3. 통지 문구가 EXE-10 규칙을 따름 — 만료 사유가 소비자 도메인 시그널로 도달(ModelRunner·ModelBuilderMCU·NX 각 1회 수동 확인)
- 변경 범위: controller/DashExtensionProcess.h · DashExtensionProcess.cpp · tests/TestProcessRuntime.cpp · tests/daemon_stub.cpp
- 선행: EXE-10
- 충돌: EXE-12 (DashExtensionProcess.h 주석) · LCH 의 STP watchdog(`kStpCaseTimeoutMs` 600s) 항목 — 중복 상한이 되므로 LCH 가 자기 watchdog 유지 여부를 판정 · B2 교집합: DashExtensionProcess.h → LCH-10 LCH-31 · TestProcessRuntime.cpp → CAD-15 · DashExtensionProcess.cpp → CAD-15 · daemon_stub.cpp → CAD-15
- 흡수: #467 · EXE-c25, c26(해소분 기록), c32(비고)
- 비고: 고정 상한은 부적합 — MCU 학습은 수십 분, NX load 는 수 분이고 길이가 가변이라 "응답이 없다" 는 "출력이 없다" 로 정의한다. 진행 중 아무것도 안 찍는 명령이 있으면 그 데몬의 EXT 작업(heartbeat 라인)이 선행. `killOrphans` 의 동기 3s 는 수용(재기동 전용) — 손대지 않는다.

### EXE-12 · 데몬 stdout 프로토콜 계약을 명문화한다 (CAD-U4)
- 종류: PR | 규모: S | 태그: B, E · docs
- 목표: `[READY]`(기동 1회) · `[FINISHED]`(명령 성공, 전체 일치) · `[ERROR] <msg>`(명령 실패, 부분 일치) · 비정상 종료 = 진행·대기 명령 전부 실패 · `commandId` 에코 — 를 계약으로 적고 두 조항을 더한다: (1) 실패는 반드시 `[ERROR]` 또는 비정상 종료로 표면화한다 — 둘 다 없으면 성공으로 마감되는 현행 동작을 계약으로 고정하고 데몬 측 의무로 돌린다 (2) 산출물 flush·닫기가 `[FINISHED]` 보다 앞선다(RUN-D27 류 예방) (3) 진행 중 명령의 취소는 프로토콜에 없다 — 대기 명령은 `dropQueuedCommands`, 진행 중은 `stop()` 승격뿐(현행 고정, #249 범위 밖 절의 per-command cancel 은 데몬 측 cancel 명령이 생기기 전에는 불가). GUI 측 산출물은 `DashExtensionProcess.h` 헤더 주석 + docs, 테스트 "ERROR 없는 실패는 성공으로 마감된다(계약 고정)" 1건. 데몬 측 준수는 EXT(DashOpti_Registry 의 JournalLauncher·MCU·SensitivityEngine·NX CAD).
- 완료 기준: (1) 계약 본문 3항이 `DashExtensionProcess.h` 헤더 주석 + docs 에 적힘 (2) tests/TestProcessRuntime.cpp 에 "`[ERROR]` 없이 정상 종료한 실패 명령은 성공으로 마감된다(계약 고정)" 1건 추가·통과 (3) EXT 추적 행 — 데몬 4종(JournalLauncher·MCU·SensitivityEngine·NX CAD) 준수 여부 표
- 변경 범위: controller/DashExtensionProcess.h(주석) · docs · tests/TestProcessRuntime.cpp
- 선행: -
- 충돌: EXE-11 (같은 헤더 주석) · B2 교집합: DashExtensionProcess.h → LCH-10 LCH-31 · TestProcessRuntime.cpp → CAD-15
- 흡수: CAD-U4 · CAD-c31(CAD 가 EXE 로 넘김) · EXE-c29, c57 · RUN-D27(계약 몫) · #249(범위 밖 절 — 명령 취소) · CAD-c13 · EXE-c56(해소 기록)
- 비고: 종류가 `PR` 인 이유 — 산출물에 헤더 주석과 테스트 1건이 있어 00-plan 1-2 의 `DEC`("산출물은 기록된 결정") 와 맞지 않는다(검토 #4). 계약 본문(문서)과 "계약 고정 테스트 + 헤더 주석"으로 2분할하는 안은 **기각** — 개념이 "데몬 stdout 계약" 하나이고, 테스트는 그 계약의 현행 동작을 못 박는 같은 덩어리다(00-plan 1-2 개념적 응집). EXT 가 실제 변경의 대부분 — GUI 는 계약을 쓰고 지키는지 검사할 뿐. 준수 표의 NX CAD 행은 CAD-10 을 **참조만** 한다 — CAD-D14(표현식 적용 실패를 삼킴) 의 실작업은 CAD-10 단일이고 본 항목 흡수 목록에서 뺐다(Phase B 중복 기록 병합 이행). 215-2 Q5 "status 를 stdout 계약으로" 도 같은 계약 문서의 후속 절.

### EXE-13 · 고아 프로세스 재시작 조정과 취소 완료 정의를 정한다 (215-2 5·8절)
- 종류: DEC | 규모: S | 태그: B, A · docs
- 목표: (1) 크래시·강제 종료로 남는 자식 트리의 처분 — 예방(Job Object `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, "GUI 를 닫으면 실행이 죽는다" 고정) vs 사후(시작 시 PID·생성 시각·이미지 경로 기록 + 재기동 시 생존 확인 + 묻기) 중 선택 (2) 취소 완료의 정의 — 현행 "kill 신호 발신 = Cancelled 종결" 유지 vs 사망 관측 후 종결. 유지라면 "다음 실행 가드가 풀린 뒤 파일 핸들이 남는 창" 을 수용 사실로 기록한다 (3) append-only 실행 기록(started/finished) 도입 여부.
- 완료 기준: 결정 기록 1건 — 3항 각 선택과 사유 · 선택에 따른 후속 PR 후보 1~2개(예: Job Object 래퍼 `controller/async/ProcessJobObject` S)
- 변경 범위: 문서만
- 선행: EXE-01
- 충돌: -
- 흡수: EXE-c30, c31 · 215-2 5·8절 · Q6 · Q13~Q16 · 다음 단계 4번
- 비고: 215-2 가 "소유 티켓 없음" 으로 남긴 유일한 꼭지. 예방(Job Object) 이 가장 싸고(탐지·판정·처분 3단계 소멸) 정책 비용만 든다. `killOrphans` 의 "이전 세션 고아 미회수" 수용은 이 결정으로 대체된다.

### EXE-14 · RW 액터의 GUI 점유를 실측하고 스레드 소유(Stage 2) 를 결정한다
- 종류: INV | 규모: S | 태그: B, E · docs
- 목표: `DashRwActor` 가 GUI 스레드에 전 인스턴스를 감금(Stage 1)한 상태에서, 워커가 RW 를 쓰는 길이 `invokeOnActor` 의 blocking 마샬링(GUI 로 되돌아옴)뿐이다. 선택지 — (a) 유지: RW 작업은 GUI 에 두고 긴 것만 다른 수단(외부 프로세스·QCoro 분할)으로 (b) 단일 액터 스레드: 전 인스턴스를 전용 스레드로, GUI 호출은 blocking 마샬링(교착 방지 = LEAF RULE) (c) per-instance 어피니티: 배치 클론은 워커, 표시 문서는 GUI. 대상 소비자: CON 의 동기 액터 호출(CON-D11 왕복), DOE 배치 체인(`DashDoeBatchChain` QCoro 가 GUI 에서 RW 편집·export), #281 의 전용 세션.
- 완료 기준:
  1. **실측 결과 1표** (선행) — 대형 deck 적재 · DOE 배치 체인 · 모핑 배치가 `invokeOnActor` 로 GUI 에 되돌리는 구간의 GUI 점유 시간(로그 타임스탬프, 경로별 최소·중위·최대). EXE-c55 판정이 `미확인` 이라 이 수치가 결정의 유일한 입력이다 (#281 Follow-up ⑵)
  2. 실측 뒤 결정 기록 1건 — (a)/(b)/(c) 중 선택과 사유 · 소비자 3종(CON · LCH 배치 · MOR #281) 각각에 미치는 영향 1행
  3. 선택이 (b)/(c) 면 후속 PR(EXE-22) 범위와 테스트(TestRwActor 에 스레드 확인 케이스) 명시 · (a) 면 EXE-22 를 CLOSE 로 내리고 #458 을 "GUI 스레드 유지 + 진행 표시(EXE-07)" 로 재정의
- 변경 범위: 문서만 (계측은 로그 타임스탬프 — 코드 변경 없음)
- 선행: EXE-01
- 충돌: -
- 흡수: EXE-c11 · #451 비범위 판정("CON 의 동기 액터 호출은 공통 기반 후속") · 215-2 Q3·Q10 · 접점 #281(EXE 몫) · #281-FU2(계측) · MOR-c10 · EXE-c55 · #458-a 의 선행(EXE-c59)
- 비고: 종류가 `INV` 인 이유 — 실측이 결정의 선행이고 결과에 따라 후속 PR(EXE-22)이 생기거나 CLOSE 되는 구조가 00-plan 1-2 의 INV 정의와 같다(검토 #5). 개념은 하나(액터 스레드 소유)라 분할하지 않는다. Preprocess(#454) 는 `IPreprocessorWrapper`(외부 Preprocessor) 경로라 이 결정과 무관 — 기다리지 않는다. DashRwActor.h:30-37 의 roadmap 주석이 (c) 를 가리킨다. #458(적재 워커화)이 이 결정의 첫 소비자.

### EXE-15 · #463 모듈별 진행바·취소 버튼 확산 — 모듈 항목으로 분산하고 닫는다
- 종류: CLOSE | 규모: S | 태그: B, D · feature
- 목표: 확산은 모듈 작업이다. EXE 는 규약(EXE-07)·헬퍼(EXE-09)·취소(EXE-02)·진행률(EXE-02) 을 제공하고, 적용은 각 모듈 항목이 흡수한다.
- 완료 기준: 닫기 사유 — "규약·헬퍼는 EXE-07/09, 적용은 8모듈 항목이 흡수했다. `05-final/mapping.md` 의 `#463` 행이 그 증거 — MOR-01 · CAD-07 · **LCH-28** · PRE-23 · BLD-10 · RUN-05 · RUN-25 · ANA-22 · OPT-05 · OPT-22." 흡수 확인이 끝났으므로 지금 닫는다.
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #463 · EXE-c23
- 비고: 선행을 `-` 로 둔 이유 — 닫기 조건은 "8모듈이 `#463` 을 흡수했는가" 뿐이고 이미 충족됐다. EXE-07(규약)·EXE-09(헬퍼) 완성은 각 모듈 적용 항목의 선행이지 이 CLOSE 의 선행이 아니다(검토 #12). LCH 적용처는 LCH-28 이다 — `#456` 은 LCH 가 해소됨(LCH-20)으로 판정했다.

### EXE-16 · #468 외부 프로세스 호출부 널 가드 — 해소됨으로 닫는다
- 종류: CLOSE | 규모: S | 태그: B · bug
- 목표: 실행층(ProcessJob · DashExtensionProcess) 은 슬롯·루프마다 프로세스 포인터를 재검사하고, 소비자 측 Job 포인터(`m_currentJob`·`m_fitJob`) 는 사용 전 전부 검사한다. 데몬 getter 는 DashManager 생성자가 상시 생성해 널이 될 수 없다.
- 완료 기준: 닫기 사유 — EXE-c27 좌표(실행층 9곳 · 소비자 6곳 · 생성 보장 `controller/DashManager.cpp:85-98`). 검사 없이 쓰는 4곳(DashModelBuilderMCU.cpp:42 · DashModelRunner.cpp:232·266·366) 은 생성 보장 아래 무해 — 기계적 추가는 하지 않는다.
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #468 · EXE-c27
- 비고: 직접 QProcess 를 쓰는 dfsxml 보존 경로(`m_motionProcesses`) 도 `if (proc)` 가드가 있다.

### EXE-17 · #469 프로세스 인자·출력 인코딩 UTF-8 통일 — 본선 완료로 닫는다
- 종류: CLOSE | 규모: S | 태그: B · bug
- 목표: 본선(ProcessJob · DashExtensionProcess) 은 `PYTHONIOENCODING=utf-8`·`PYTHONUTF8=1` 주입 + LineAssembler 완성 라인 단위 `fromUtf8` + 데몬 명령 `toUtf8` 로 일원화돼 있고 테스트(`decodesUtf8SplitAcrossChunks` · TestLineAssembler `utf8SplitAcrossChunks`)가 고정한다. 인자는 `QProcess::start(exe, QStringList)` 라 Windows 에서 UTF-16 으로 전달된다.
- 완료 기준: 닫기 사유 — EXE-c28. 잔여 `fromLocal8Bit` 5곳(model/DashJobRunnerAnsysMotion.cpp:186·190·197·230·416) 은 #451 이 "격리만 하고 수정하지 않는다" 로 정한 dfsxml 보존 경로 — LCH 대응표에 보존 사실로 기록
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #469 · EXE-c28
- 비고: dfsxml 경로가 #458 로 ProcessJob 에 수렴하면 잔여도 자동 해소된다.

### EXE-18 · #451 GUI 스레드 동기 실행과 이벤트 펌핑 제거 — 추적 부모를 닫는다
- 종류: CLOSE | 규모: S | 태그: B · refactor
- 목표: 공통 기반 몫은 EXE-01(계약) · EXE-04(레인) · EXE-05(게이트·문서) · EXE-06(싱글톤), 모듈 몫은 #454 #455 #456 #457 #512 #513 이 흡수한다.
- 완료 기준: 닫기 사유 — 서브 6건 열림 상태 유지, 본문의 "WorkerJob·ThreadPools·MorphingGate·ThreadingContract 부재" 전제는 EXE-c01 로 갱신(워커 단위는 #544 로 존재). processEvents 전수는 02-claims/EXE.md "processEvents 전수" 절(55 히트 · 49 호출).
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #451 · EXE-c49, c04
- 비고: MorphingGate 는 #281(MOR, In progress) 소관.

### EXE-19 · #460 실행 진행 표시·취소·중복 실행 가드의 표준화 — 추적 부모를 닫는다
- 종류: CLOSE | 규모: S | 태그: B, D · feature
- 목표: #461 → EXE-09, #462 → EXE-07, #463 → EXE-15(모듈 분산), #464 → CAD.
- 완료 기준: 닫기 사유 — 위 대응. 취소는 EXE-02, 진행률 소스는 EXE-02, 표면은 EXE-08.
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #460 · EXE-c50
- 비고: -

### EXE-20 · #465 외부 프로세스 안전핀 일괄 — 추적 부모를 닫는다
- 종류: CLOSE | 규모: S | 태그: B · bug
- 목표: #466 → EXE-10, #467 → EXE-11, #468 → EXE-16(해소), #469 → EXE-17(해소). 자식 프로세스 정리(#207) 는 Done. cae-launcher(ANSYS·Abaqus·fe-safe) 쪽 안전핀은 외부 저장소(EXE-c45).
- 완료 기준: 닫기 사유 — 위 대응 + 추가 발견 2건(프로토콜 계약 EXE-12 · 고아 재시작 EXE-13) 이 새 항목으로 등재됨.
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #465 · EXE-c51, c45
- 비고: -

### EXE-21 · DashRwDocument 엔트리 분해 테스트를 flat 필드·요약 행·DV 종류 분류까지 넓힌다 (CON-U5)
- 종류: PR | 규모: S | 태그: F · refactor
- 목표: `tests/rw/FakeRwModule.h` 의 FakeRwDeck 에 Ansys flat 스키마 조건(`target`/`component` + 필드 N개) · 요약 행만 남는 조건(omega 벡터 · D 라벨) · bounded(min/max)·enum 속성을 더하고, `TestRwDocument` 에 `feConditionEntries` 분해 케이스 3건 — 필드별 행 수 · 요약 행 readOnly · `dvKind` Discrete/Categorical + cases — 을 추가한다. 생산 코드 변경 없음.
- 완료 기준:
  1. tests/TestRwDocument.cpp 에 3 케이스 추가·통과 — `rwPropertyDvKind` 의 세 분기(Continuous·Discrete·Categorical) 각 1건 이상
  2. FakeRwDeck 으로 **flat 조건(entries 없음 + 스칼라 스키마 2필드) · 읽기전용 요약 행(omega 벡터 · D 라벨) · bounded(min/max)·enum 속성 조건**을 만들 수 있고 읽기·편집이 거부되지 않는다(`/entries/` 외 경로가 필요하면 추가) — CON-09 완료 기준 (2) 를 이 항목이 대신 덮는다
  3. 기존 TestRwDocument 15건 무변경 통과 (PR #658 이 `couplingShapesKeepSeparateOwnersAndMembership` 1건을 더하므로 머지 뒤 기준 16건)
- 변경 범위: tests/TestRwDocument.cpp · tests/rw/FakeRwModule.h
- 선행: -
- 충돌: CON-09 (같은 `tests/rw/FakeRwModule.h` — EXE-21 을 먼저 랜딩한다) · B2 교집합: PR #658(FakeRwModule.h·TestRwDocument.cpp)
- 흡수: CON-U5 · CON-U5(픽스처 몫 — CON-09 완료 기준 (2)) · CON-c17 · EXE-c58
- 비고: 생산 좌표 — `controller/DashRwDocument.cpp:rwPropertyDvKind`(:450-488) · 분해 본체는 익명 namespace 의 코루틴 `readFeCondition`(:518) 안: flat 필드별 행 루프 :650-667 · 읽기전용 요약 행 :672-692. `DashRwDocument::feConditionEntries`(:1072-1075) 는 `m_gen->feConditions.value(condName).entries` 를 돌려주는 캐시 1줄이라 분해 코드가 없다. 생산 코드는 변경하지 않는다. CON-U5 는 "입력 검증 부재" 가 아니라 테스트 부재(UIC-c57 판정과 같음). 픽스처 귀속은 C-2 ⑦ 로 EXE-21 확정 — 공용 픽스처이고 흉내낼 대상(`DashRwDocument` flat 스키마 분해)이 EXE 소관이며 CON-09 는 픽스처를 **쓰는** 쪽. CON-09 의 완료 기준 (2) 삭제 · `FakeRwModule.h` 변경 범위 제외 · `선행: EXE-21` 추가는 `보류: CON 몫`.

### EXE-22 · 해석 deck 적재를 RW 액터 워커로 옮긴다 (#458-a, EXE-14 조건부)
- 종류: PR | 규모: M | 태그: B · perf
- 목표: EXE-14 가 (b) 단일 액터 스레드 또는 (c) per-instance 어피니티를 택하면 — `DashRwActor` 의 GUI 스레드 감금(**생성자** `DashRwActor::DashRwActor()` 의 assert `:98` · 전 메서드 `assertActorThread`) 을 액터 스레드 소유로 바꾸고 `invokeOnActor` 마샬링 방향을 뒤집는다(GUI → 액터 blocking, 액터 → GUI 역호출 금지 = LEAF RULE). `DashAnalysisModelContextRegistry::load` 가 QCoro 라 소비측은 변경 없음 — `co_await …load(…)` 는 **8파일 9곳**이다: `view/DashMainWindow.cpp:2766`(1곳) · `view/DashAnalysisLauncherWidgetLauncher.cpp:338`·`:362` · `view/DashModelRunnerWidget.cpp:2202` · `view/DashModelingTreeWidget.cpp:539` · `controller/DashMorphingDoeExecutor.cpp:760` · `model/DashGeometryParameter.cpp:161` · `model/DashModelRunner.cpp:2153` · `model/DashOptimizer.cpp:1491`. `DashDoeBatchChain` 에는 `registry.load` 가 없다(`DashRwDocumentHandle` 경유). 적재 중 진행 표시는 EXE-07 규약.
- 완료 기준:
  1. 대형 deck(.inp/.dat) 적재 중 GUI 이벤트 루프가 돈다 — 상태바 진행 표시 · 창 이동 가능 (실측 기록, 현행 1~20s 프리즈 대비)
  2. tests/TestRwActor.cpp 에 "액터 메서드가 GUI 스레드에서 실행되지 않는다" · "GUI 에서 부른 invokeOnActor 가 액터 스레드에서 완료된다" 2건 추가·통과
  3. 기존 TestRwActor 6 · TestRwDocument · TestDoeBatchChain · TestMorphingGeometry 통과 (`TestDoeBatchChain` 은 PR #655 가 +7/-3 고치므로 머지 **뒤** 기준) + 소비측 무변경 확인 — 위 9곳 중 `view/DashModelRunnerWidget.cpp`·`view/DashModelingTreeWidget.cpp`·`model/DashGeometryParameter.cpp`·`model/DashModelRunner.cpp`·`model/DashOptimizer.cpp` 5경로를 각 1회 수동 적재로 확인
- 변경 범위: controller/DashRwActor.h · DashRwActor.cpp · controller/DashRwDocumentHandle.cpp · tests/TestRwActor.cpp (결정이 (c) 면 controller/DashAnalysisModelContextRegistry.cpp 도)
- 선행: EXE-14 · EXE-05 (스레드 계약 문서 · DashRwActor.cpp assert 치환이 먼저)
- 충돌: EXE-05 (DashRwActor.cpp) · MOR-16 (#281 Follow-up — RW 세션 계측) · PR #654 · PR #655 (controller/DashDoeBatchChain.{cpp,h} · tests/TestDoeBatchChain.cpp) · B2 교집합: DashAnalysisModelContextRegistry.cpp → PRJ-03 REN-01 REN-02 REN-07 UIC-19 · PR #658(DashRwActor.cpp)
- 흡수: #458(적재 축 — 담당 RUN → EXE) · RUN-D5(deck 파서 축) · RUN-c09 · EXE-c46, c59
- 비고: EXE-14(INV) 의 실측이 (a) 유지로 귀결되면 CLOSE — #458 은 "GUI 스레드 유지 + 진행 표시(EXE-07)" 로 재정의한다. dfsxml 1·2단계(#458-b) 는 LCH(RUN-c10). PoC PR #529(닫힘, 브랜치 `perf/458-rw-actor-worker`) 참고. Analyzer 축 캐시는 #410(Done) 으로 표면이 다르다.

## 대응표

| 원천 | 항목 | 비고 |
|---|---|---|
| #451 | EXE-18 (CLOSE) · 공통 기반 → EXE-01 · EXE-04 · EXE-05 · EXE-06 | 모듈 몫 #454 #455 #456 #457 #512 #513 — 각 모듈. 전제 갱신 EXE-c01 |
| #460 | EXE-19 (CLOSE) | #464 는 CAD 담당 |
| #461 | EXE-09 | 적용 확산은 #463 → 모듈 |
| #462 | EXE-07 | #543 결정 축과 한 기록 |
| #463 | EXE-15 (CLOSE · 범위밖 → LCH PRE OPT MOR RUN BLD CAD ANA) | 규약·헬퍼는 EXE-07/09. 8모듈 흡수 완료 — mapping.md `#463` 행(LCH 적용처는 **LCH-28**) |
| #465 | EXE-20 (CLOSE) | cae-launcher 몫은 EXT (EXE-c45) |
| #466 | EXE-10 | #482(UIC) 와 문서 공유. OPT-D11 수정은 OPT |
| #467 | EXE-11 | 기동·정지 타임아웃은 해소됨(EXE-c26), 명령 응답만 남음 |
| #468 | EXE-16 (CLOSE · 해소됨) | EXE-c27 |
| #469 | EXE-17 (CLOSE · 해소됨) | 잔여 dfsxml 보존 경로 → LCH 기록 (EXE-c28) |
| #543 | EXE-07 (결정) · EXE-08 (구현) · EXE-02 (취소 전제) | |
| #553 | EXE-03 | 선행 EXE-02 (#552) |
| #552 (보드 밖, gh OPEN) | EXE-02 | 배정표에 EXE 담당으로 추가 제안 |
| #454 (접점) | 범위밖 → PRE | EXE-01/04 가 선행. RW 액터 결정(EXE-14) 과 무관 |
| #456 (접점) | 범위밖 → LCH | EXE-01/04 선행 |
| #457 (접점) | 범위밖 → OPT | OPT-D11·D13 수정 포함. 규칙·표준은 EXE-10/09 |
| #512 (접점) | 범위밖 → MOR (MOR-01 이 `#512-1` 로 흡수) | 남은 1곳은 `view/dialog/DashMeshQualityDialog.cpp:164` 의 `processEvents(AllEvents, 100)` — EXE 전수표에 있다. 02-claims 전수표 소관을 `#455` → `#512-1` 로 정정(PRJ-c48 → MOR-c79) |
| #513 (접점) | 범위밖 → RUN | EXE-01/04 선행 |
| #458 (담당 — Phase B 에서 RUN → EXE) | EXE-22 (EXE-14 조건부) | 적재 축(RUN-c09 → EXE-c59). dfsxml 축(#458-b)은 LCH(RUN-c10). EXE-c46 재판정 유효 |
| #281 (접점, In progress) | 범위밖 → MOR · 계측(FU2) EXE-14 | EXE 몫은 EXE-14 정합. 본문의 DashRwSession::MutationScope 는 dev 에 없음(EXE-c47). MOR-c10 → EXE-c55 |
| CAD-U4 (CAD 가 EXE 로 넘김) | EXE-12 | CAD-c31 → EXE-c57 |
| #249 범위 밖 절 — 명령 취소 (CAD 이관) | EXE-12 (해소 기록) | CAD-c13 → EXE-c56: `dropQueuedCommands` 존재, in-flight 는 stop() 뿐 |
| CON-U5 (CON 이관 — RW 문서 테스트 공백) | EXE-21 (픽스처 몫 포함 — CON-09 완료 기준 (2)) | CON-c17 → EXE-c58. 귀속 확정 C-2 ⑦. CON-09 쪽 수정(완료 기준 (2) 삭제 · `FakeRwModule.h` 제외 · 선행 EXE-21)은 `보류: CON 몫` |
| #553 (ANA 접점 호출부) | EXE-03 | ANA-c29 → EXE-c60 |
| CAD-D14 | → CAD-10 | 실작업은 CAD-10 단일(EXT · DashOpti_CadNx). EXE-12 는 데몬 4종 준수 표에서 CAD-10 을 참조만 한다 — 이중 등재 해소 |
| RUN-D27 | 범위밖 → RUN · 계약 몫 EXE-12 | |
| RUN-D4 | 해소됨 (#436 DashDaemonLifecycle) | EXE-c34 |
| RUN-D3 | 범위밖 → RUN (해소 추정, #437) | EXE-c36 |
| RUN-D32 | 범위밖 → RUN | EXE-c35 |
| BLD-D13 | 범위밖 → BLD | EXE-c37 |
| BLD-D14 | 해소됨 (`virtual void stopTraining()`) | EXE-c40 |
| DOE-D14 · DOE-D23 | 범위밖 → LCH (dfsxml 보존 경로) | EXE-c39, c33 |
| CON-D2 · DOE-D4 · DOE-D22 | 범위밖 → REN · DOE · LCH/PER | 규칙 몫 EXE-05 (EXE-c41) |
| CAD-D3 · CAD-D7 · CAD-D8 · DOE-D16 · DOE-D21 · RUN-D15 · OPT-D19 | 범위밖 → CAD · LCH · RUN · OPT | 공통 몫 없음 (EXE-c42) |
| MOR-D7 · MOR-D8 · CAD-D2 · CON-D9 · CON-D11 · DOE-D7 · DOE-D9 · DOE-D11 · PRE-D3 · PRE-D9 | 범위밖 → MOR · PRJ(#455) · CON · LCH · PRE | 공통 몫 EXE-01/04 · EXE-09 (EXE-c43) |
| OPT-D11 | 규칙 몫 EXE-10 · 수정 범위밖 → OPT | |
| OPT-D13 | 표준 몫 EXE-07/09 · 수정 범위밖 → OPT | |
| DOE-U2 · CAD-D1 · CAD-D9 · ANA-D12 | 범위밖 → LCH · CAD(#464) · ANA | EXE-c44 |
| 215-2 (sync pumping → async checklist) | EXE-01 (2·3·**4**·9·10·13절) · EXE-05 (12절) · EXE-07 (**7**·11절) · EXE-10 (6절) · EXE-13 (5·8절) · EXE-14 (Q3·Q10) | 종합정리 11꼭지 전건 흡수. 4절(통지 출처 식별 — 현행 충족 기록, EXE-c61) · 7절(상태 writer 단일화 — 횡단 조항, EXE-c62) 은 C' 에서 추가. 다음 단계 4건 중 1·2번은 EXE-01, 3번 EXE-05, 4번 EXE-13 |
| 203-2 (worker preconditions D1~D5) | D1 → EXE-06 · D2 해소됨(#408) · D3 해소됨(getOrLoad 소멸) · D4 해소됨(rdbuf 0) · D5 → EXE-05 | EXE-c07~c10 |
