# LCH 작업 목록 — Analysis Launcher (Launcher 탭 · 배치 실행 · JobRunner · Direct Launch)

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> 기준 dev @ b08a91b3. 열린 PR 7건 중 **머지 대상 6건**(#651 #652 #654 #655 #656 #658) — #530 은 재업로드 노선이라 머지 대상이 아니다 (C-2 ② · ⑩).
> LCH 파일을 건드리는 PR — **#651(#616) · #652(#604)**: `model/DashJobRunner.h/.cpp` · `DashJobRunnerAnsysMotion.cpp` · `DashJobRunnerAnsysJournal.cpp` · `DashJobRunnerFeSafe.cpp` · `model/DashAnalysisLauncher.*` · `view/DashAnalysisLauncherWidget*` 를 고치므로 그 파일을 만지는 항목은 두 PR 머지를 선행으로 둔다 · **#654 · #655**: `controller/DashDoeBatchChain.*`(+#654 `controller/DashMorphingDoeExecutor.cpp` — LCH-13 충돌에 기재) · **#656 · #658**: `model/DashAnalysisLauncher.cpp`(·`.h`).
> **#656 · #658 은 선행이 아니다** — 두 PR 의 `DashAnalysisLauncher.cpp` hunk 가 전부 PRE 결과 경로다(#656 = `loadResultKeys`·`previewNaturalFrequency`·`requestVtkGeometry` 의 TimeSteps 파싱·질의 직렬화·모달 Name 공용화 / #658 = `requestVtkPreview` 의 `sub_result`·`previewNaturalFrequency` 의 eigenvalue). LCH 겹침 항목은 LCH-15(`preprocessInputsChanged`·`connectLaunchExecutor`) 1건뿐이고 작업 자리가 겹치지 않으므로 단순 동시 수술 — 충돌란 기입은 D-1 의 `build_deps.py --apply` 가 파일 교집합으로 자동 처리한다.
> 종결 계약 (전 항목 공통 전제): `emitEnqueued` 이후 활성 키 전부가 `caseStatusUpdated(key, Done|Failed*|Cancelled)` 에 이르러야 `DashAnalysisLaunchExecutor` 의 런 추적이 끝나고 Start 가 풀린다.
> C' 2차 반영(2026-10-06)의 카드 신설 이력은 유지한다. LCH-33은 현재 출처 검증 계약으로 개정했고 LCH-34는 기록 실패 안내를 담당한다. LCH-29의 PRJ 원장 조항은 그대로다.

### LCH-01 · Target Part 를 읽는 동안 Start 를 막고, 로드 실패 시 저장된 target 을 보존한다
- 종류: PR | 규모: S | 태그: D, A · bug
- 목표: `fillTargetPartCombo` 가 `co_await` 하는 동안 Start 버튼을 비활성으로 두고, 로드가 끝난 뒤에만 Start 와 콤보를 되살린다. RW 로드 실패(`!loaded`)면 `setTargetComponent` 를 호출하지 않는다.
- 완료 기준: (1) 탭 진입 직후 Start 가 비활성이고 콤보가 채워진 뒤 활성 (2) 로드 실패 상태로 탭 진입 뒤 `AnalysisLauncher_<Set>.json` 의 `target_component` 가 이전 값 그대로 (3) 정상 로드 시 저장값이 콤보에 선택된다
- 변경 범위: `view/DashAnalysisLauncherWidgetLauncher.cpp` (`updateLauncherTabFromModel` · `fillTargetPartCombo` · `setLauncherIdle`), `view/DashAnalysisLauncherWidget.h`
- 선행: PR #651·#652 머지 (같은 파일)
- 충돌: LCH-17 (같은 파일 Start 람다) · B2 교집합: DashAnalysisLauncherWidgetLauncher.cpp → LCH-08 LCH-10 LCH-15 LCH-16 LCH-28 LCH-29 LCH-33 · DashAnalysisLauncherWidget.h → PRE-05 PRE-23
- 흡수: #639 · LCH-c30, LCH-c31
- 비고: `setLauncherIdle` 에 "콤보 채우는 중" 조건을 더하는 것으로 충분. 세대 검사(`m_targetPartsGeneration`)는 이미 있다

### LCH-02 · Enqueued 이후 종결 상태 없이 빠져나가는 경로를 전부 종결 상태로 닫는다
- 종류: PR | 규모: M | 태그: B · bug
- 목표: (a) `runDoeJobs` 의 `!prep.ansysReady` 와 Motion 의 소스 dat 추출 실패·부재는 `emitEnqueued` 이전 사전 검증으로 옮겨 `jobFailed` 로 끝낸다 — 사전 검증은 `.dat` 템플릿만 대상으로 하고, `prepareMorphingBatch:638-648` 이 `!ctx.isInp` 로 dfsxml 에도 걸던 MAPDL 초기화는 함께 제거한다(269-1 후속 "dfsxml 의 불필요한 MAPDL 초기화") (b) 모핑 뒤 프로젝트 닫힘·`ioCtrl` 없음(`resumeAfterMorph` false)은 활성 키 전부 "Cancelled" 방출 (c) 치환 폴백의 `!ansysReady continue`·템플릿 읽기 실패, Abaqus 배치 진입 실패 2곳은 `failActiveCases` 로 (d) JSON 에만 쓰고 시그널을 안 내는 **18곳**을 닫는다 — Failed 16곳은 `writeCaseStatus` 를 `emit caseStatusUpdated` 로 **치환**(기록은 executor `onCaseStatusUpdated:243` 이 하므로 이중 기록 0), Motion `:652` Done(`.dfr` resultFiles)·Mechanical Running 2곳(`submitMorphedAnsysMechanicalJobs:358` · `runTemplateFallback:480`)은 emit 을 추가하고 러너 기록은 LCH-07 이 걷는다.
- 완료 기준: (1) 4 경로(#580)를 강제 유발하면 Start 가 풀리고 표에 Failed/Cancelled 또는 `analysisFailed` (2) `runDoeJobs`·`runAnsysMotionMorphingDoe`·`runTemplateFallback`·`submitMorphed*` 에 Enqueued 이후 상태 없는 `co_return`/`return`/`continue` 가 0 (3) 러너의 `writeCaseStatus(..., "Running"|"Failed"|"Done")` 호출마다 같은 키의 `caseStatusUpdated` 가 함께 있다 — grep 으로 확인 (4) MAPDL 미설정 환경에서 dfsxml 배치가 종전처럼 실행된다 (5) 정상 DOE 5경로 회귀 없음
- 변경 범위: `model/DashJobRunner.cpp` (`runDoeJobs` · `prepareMorphingBatch` · `resumeAfterMorph`), `model/DashJobRunnerAnsysMotion.cpp` (`runAnsysMotionMorphingDoe` · `startNextMotionLauncher`), `model/DashJobRunnerAnsysMechanical.cpp` (`submitMorphedAnsysMechanicalJobs` · `runTemplateFallback`), `model/DashJobRunnerAbaqus.cpp` (`submitMorphedAbaqusJobs`), `model/DashJobRunner.h`
- 선행: PR #651 머지 (`failActiveCases` 재사용), PR #652 머지
- 충돌: LCH-03 · LCH-04 · LCH-07 · LCH-13 (같은 TU) · B2 교집합: DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절) · DashJobRunner.cpp → LCH-14 PRJ-09 UIC-20 · DashJobRunner.h → CAD-01 LCH-06 LCH-10 LCH-12 LCH-14 · DashJobRunnerAbaqus.cpp → UIC-19 · DashJobRunnerAnsysMechanical.cpp → UIC-19
- 흡수: #580 · 269-1 "시그널이 빠진 실패 — 후속" · 269-1 후속 "dfsxml 의 불필요한 MAPDL 초기화" · LCH-c02, LCH-c03, LCH-c04, LCH-c05, LCH-c07
- 비고: (a)·(c) 가 동작 변경 — (a) `.dat` 템플릿도 MAPDL 미설정을 모핑 전에 거부하고(dfsxml 은 MAPDL 과 무관해 제외), (c) 는 `runTemplateFallback` 의 "입력 파일만 생성" 모드(WARN `:385-386`)를 폐지해 미설정이면 `.dat` 도 Failed 가 된다. 둘 다 PR 본문에 명시

### LCH-03 · 취소가 motion-launcher 대기 큐까지 비우게 한다
- 종류: PR | 규모: S | 태그: B · bug
- 목표: `cancelAllRuns` 가 `m_motionLauncherQueue` 를 비우고 대기 중이던 키마다 "Cancelled" 를 방출한다. `startNextMotionLauncher` 는 취소 뒤 큐잉된 호출에서 아무것도 시작하지 않는다.
- 완료 기준: (1) dfsxml 케이스 3개 이상 실행 중 Stop → 진행 1건 Cancelled, 대기분 전부 Cancelled, 다음 프로세스가 뜨지 않는다 (2) Start 버튼이 풀린다
- 변경 범위: `model/DashJobRunner.cpp` (`cancelAllRuns`), `model/DashJobRunnerAnsysMotion.cpp` (`startNextMotionLauncher`)
- 선행: PR #651 머지 (`DashJobRunner.cpp`) · PR #652 머지 (`DashJobRunnerAnsysMotion.cpp`)
- 충돌: LCH-02 · LCH-04 · LCH-05 · LCH-10 · LCH-12 · B2 교집합: DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절) · DashJobRunner.cpp → LCH-07 LCH-13 LCH-14 PRJ-09 UIC-20
- 흡수: #439 · DOE-D23 · LCH-c09 · DOE-c50(LCH-c85) · EXE-c33(LCH-c90)
- 비고: Direct 큐(PR #652 러너)도 같은 큐를 쓰므로 Direct Stop 에도 적용된다

### LCH-04 · motion-launcher 가 `.dfr` 을 위조하지 않고 Failed 로 끝낸다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: exit 0 인데 `{runKey}.dfr` 이 없으면 하드코딩 XML 생성·Done 대신 Failed 를 기록·방출한다.
- 완료 기준: (1) `.dfr` 부재 케이스가 Failed 로 표시되고 run 폴더에 생성된 `.dfr` 이 없다 (2) Preprocess 가 그 케이스를 읽지 않는다 (3) `runMotionLauncher` 에 `<DFRInfo>` 리터럴이 없다
- 변경 범위: `model/DashJobRunnerAnsysMotion.cpp` (`runMotionLauncher` finished 람다)
- 선행: PR #652 머지
- 충돌: LCH-03 · LCH-05 · LCH-10 · B2 교집합: DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절)
- 흡수: DOE-D15 · LCH-c39 · DOE-c44(LCH-c79)

### LCH-05 · motion-launcher 완료 판정을 `finished` 람다 하나로 단일화한다
- 종류: PR | 규모: S | 태그: B · refactor
- 목표: `monitorMotionLauncherOutput` 은 stdout 을 로그로만 남기고 상태를 올리지 않는다. Done/Failed 판정은 `finished` 람다만 한다.
- 완료 기준: (1) `monitorMotionLauncherOutput` 에 `caseStatusUpdated`·`recordMotionDone` 호출이 없다 (2) 정상·실패 케이스에서 상태가 1회만 방출된다 (로그로 확인)
- 변경 범위: `model/DashJobRunnerAnsysMotion.cpp` (`monitorMotionLauncherOutput` · `runMotionLauncher`)
- 선행: LCH-04
- 충돌: LCH-03 · LCH-10 · LCH-12 · B2 교집합: DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절) · PR #652(DashJobRunnerAnsysMotion.cpp)
- 흡수: DOE-D16 · LCH-c40 · DOE-c45(LCH-c80) · EXE-c42(DOE-D16 몫, LCH-c96)
- 비고: LCH-10 이 motion-launcher 호출을 MBD 단일 호출로 바꾸면 이 함수가 사라질 수 있다 — 그때는 LCH-10 에 흡수

### LCH-06 · 배치 종결을 키 집계 한 갈래로 통일하고 `jobFinished` 를 없앤다
- 종류: PR | 규모: S | 태그: B · refactor
- 목표: `DashJobRunner::jobFinished` 시그널과 그 방출 2곳(wbpj DOE·Direct wbpj), executor 의 `jobFinished → analysisFinished` 직결을 제거한다. `launchAnsysJournal` 의 `jobFailed` 는 활성 키 전부 Failed 를 이미 방출하므로 함께 제거한다.
- 완료 기준: (1) wbpj DOE 완료 시 `analysisFinished` 가 1회 (2) Journal 실패 시 `analysisFailed` 가 `analysisFinished` 뒤에 따라오지 않는다 (3) `jobFinished` 심볼 0건
- 변경 범위: `model/DashJobRunner.h`, `model/DashJobRunnerAnsysJournal.cpp` (`onAnsysJournalCompleted` · `launchAnsysJournal` · `launchAnsysJournalDirect`), `model/DashAnalysisLaunchExecutor.cpp`
- 선행: LCH-29 (`jobFinished` 방출 2곳이 전부 wbpj Journal 경로다) · PR #652 머지 (Direct 러너가 `jobStarted` 만 구독함을 diff 에서 확인 — 머지 뒤 소비자는 executor 뿐)
- 충돌: LCH-07 · B2 교집합: DashAnalysisLaunchExecutor.cpp → LCH-14 LCH-16 LCH-28 LCH-34 PRJ-09 UIC-20 · DashJobRunner.h → CAD-01 LCH-02 LCH-10 LCH-12 LCH-14 · DashJobRunnerAnsysJournal.cpp → CAD-01 LCH-14 LCH-27 UIC-19 · PR #651(DashJobRunner.h·DashJobRunnerAnsysJournal.cpp)
- 흡수: DOE-D21 · LCH-c41 · DOE-c49(LCH-c84) · EXE-c42(DOE-D21 몫, LCH-c96)
- 비고: LCH-29 가 wbpj 경로 **제거**로 결정되면 이 항목은 소멸 — `jobFinished` 시그널 자체가 Journal TU 삭제 PR 에 흡수된다. **동결**·**현행 유지**면 그대로 — `analysisFinished` 2회는 `setLauncherIdle(true)`·표 재구축 2회로 무해하므로 우선순위만 낮춘다

### LCH-07 · 케이스 상태 기록을 executor 단일 라이터로 모은다
- 종류: PR | 규모: L | 태그: E, A · refactor
- 목표: 러너는 `caseStatusUpdated(key, status, analysisType, resultFiles)` 만 방출하고 `writeCaseStatus`·`recordMotionDone` 을 호출하지 않는다. `DashAnalysisLaunchExecutor::onCaseStatusUpdated` 가 유일하게 `DashAnalysisLauncherConfig::writeCaseStatus` 를 부른다(Direct 는 `launcherConfigPath` 가 비어 기록 없음 — 현행 유지).
- 완료 기준: (1) `model/DashJobRunner*.cpp` 에 `DashAnalysisLauncherConfig::writeCaseStatus` 호출 0 (2) 케이스 1건 Done 당 런처 JSON 기록 1회 (워처 `fileChanged` 1회) (3) Done 의 `resultFiles` 가 종전과 같이 기록된다 (Ansys `producedResultFiles` · Abaqus/fe-safe `<runKey>.odb` · Motion `<runKey>.dfr` · Journal 재귀 `.rst`)
- 변경 범위: `model/DashJobRunner.h/.cpp`, `model/DashJobRunnerAbaqus.cpp`, `model/DashJobRunnerAnsysMechanical.cpp`, `model/DashJobRunnerAnsysMotion.cpp`, `model/DashJobRunnerAnsysJournal.cpp`, `model/DashJobRunnerFeSafe.cpp`, `model/DashAnalysisLaunchExecutor.h/.cpp`
- 선행: LCH-02 (누락 방출을 먼저 채워야 기록을 걷어도 상태가 남는다), LCH-06, PR #651·#652 머지
- 충돌: LCH-03 · LCH-04 · LCH-05 · LCH-13 · LCH-14 · B2 교집합: DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절) · DashAnalysisLaunchExecutor.cpp → LCH-16 LCH-28 LCH-34 PRJ-09 UIC-20 · DashJobRunner.cpp → PRJ-09 UIC-20 · DashJobRunner.h → CAD-01 LCH-10 LCH-12 · DashJobRunnerAnsysJournal.cpp → CAD-01 LCH-27 LCH-29 UIC-19 · DashJobRunnerFeSafe.cpp → LCH-18 LCH-30 PRJ-14 UIC-19 · DashAnalysisLaunchExecutor.h → LCH-16 LCH-34 · DashJobRunnerAbaqus.cpp → UIC-19 · DashJobRunnerAnsysMechanical.cpp → UIC-19
- 흡수: DOE-D10 · LCH-c42 · LCH-c11(이중 기록분) · DOE-c39(LCH-c74)
- 비고: L 사유 — 한 클래스의 TU 6개가 같은 시그널 계약을 공유해 경로별로 가르면 중간 상태에서 기록이 두 벌/한 벌 섞인다. 시그널에 `resultFiles` 인자를 더하는 것이 핵심 설계 결정

### LCH-08 · 실행 중에는 케이스 표를 워처로 재구축하지 않는다
- 종류: PR | 규모: S | 태그: B · perf
- 목표: `DashDoeCasesWidget` 이 실행 중(`analysisStarted` ~ `analysisFinished/Failed`)에는 `fileChanged` 를 무시하고 시그널(`updateCaseStatus`·`updateCaseLog`)로만 셀을 갱신한다. 종료 시 1회 `updateFromDvTable` (현행 `analysisFinished` 연결 유지).
- 완료 기준: (1) N 케이스 실행 동안 `updateFromDvTable` 호출이 0, 종료 뒤 1 (2) 실행 중 체크박스·Log 열이 유지되고 Mechanical·Abaqus·fe-safe·Motion 케이스의 Running 전이가 실행 중 표에 보인다 (3) 실행 밖에서 JSON 을 바꾸면 종전처럼 재구축된다
- 변경 범위: `view/DashDoeCasesWidget.cpp/.h` (`setRunning(bool)` 또는 동등), `view/DashAnalysisLauncherWidgetLauncher.cpp` (`connectLaunchExecutor`)
- 선행: LCH-02 (Mechanical DOE 는 Running 을 어디서도 방출하지 않아 지금은 워처 재구축으로만 보인다 — 재구축을 끄면 Done 까지 Enqueued 로 남는다), PR #651·#652 머지
- 충돌: LCH-01 · LCH-14 · LCH-17 (같은 파일) · B2 교집합: DashAnalysisLauncherWidgetLauncher.cpp → LCH-10 LCH-15 LCH-16 LCH-28 LCH-29 LCH-33 · DashDoeCasesWidget.cpp → LCH-09 LCH-34 · DashDoeCasesWidget.h → LCH-34
- 흡수: #441-a · DOE-D7 · LCH-c11 · DOE-c36(LCH-c71) · EXE-c43(DOE-D7 몫, LCH-c93)
- 비고: #441 증분 화면 갱신의 개선안이며 파일 저장·읽기 비용까지 해결됐다고 간주하지 않는다. #444 저장 경계는 LCH-32에서 비용을 확인해 필요한 경우에만 분리한다. 두 작업은 공유 적용 지점을 조율한다.

### LCH-09 · 앱 재시작 뒤 "Running" 으로 남은 케이스의 처리 정책을 정한다
- 종류: DEC | 규모: S | 태그: B, A
- 목표: 재시작 후 런처 JSON 에 Running 이 남은 케이스를 (a) 자동 재개 (b) "Interrupted" 로 표시하고 Start 시 재실행 (c) 현행(표시만 Running, Start 가 Done 아닌 것을 재실행) 중 무엇으로 할지 결정한다.
- 완료 기준: 결정 기록 — 선택지·근거·후속 PR 범위. (b) 면 `DashDoeCasesWidget::updateFromDvTable` 의 표시 규칙 + 로드 시 상태 치환 지점(`DashAnalysisLauncher::refreshLaunchTarget` 또는 `DashLauncherRuns`) 명시
- 변경 범위: (결정만) 후속 후보 `view/DashDoeCasesWidget.cpp`, `model/preprocessor/DashLauncherRuns.cpp`
- 선행: LCH-32 (저장 경계·상태 기록 개선 확인)
- 충돌: B2 교집합: DashDoeCasesWidget.cpp → LCH-08 LCH-14 LCH-34 · DashLauncherRuns.cpp → PRE-32
- 흡수: #441-b · LCH-c12
- 비고: 자동 재개는 외부 프로세스 재부착 제약을 확인해야 하며 (b)가 최소 변경 후보다. #444 저장 경계 개선 후 그 기록을 사용하는 #441 복구를 적용한다.

### LCH-10 · dfsxml 실행의 모델 종속 규칙을 GUI 에서 걷어 MBD 단일 호출로 줄인다
- 종류: PR | 규모: M | 태그: E, B · feature
- 목표: Target Part "CBLOCK" 고정·density 7816.9·`--unit m -b 19`·VTU 대기 → motion-writer → motion-launcher 2단 큐를 GUI 에서 제거하고, run 마다 DashOptiMBD 를 한 번 호출해 템플릿 경로·VTU 경로·DOE 값·출력 폴더만 넘긴다. Target Part 는 MBD 가 템플릿에서 읽거나 Set json 에서 받는다.
- 완료 기준: (1) `CBLOCK`·`7816.9` 리터럴 0건 (2) run 폴더에 `.dfsxml`·`.dfmm`·`.dfg` 가 생기고 Done 기록의 `resultFiles` 는 `.dfr` (3) LGE 예제 외 dfsxml 모델 1건으로 실행 성공
- 변경 범위: `model/DashJobRunnerAnsysMotion.cpp` (`runAnsysMotionMorphingDoe` · `runMotionWriter` · `runMotionLauncher` — 서브커맨드 리터럴 `:136`·`:220` 을 기존 `DashExt::Cmd::MBD_*` 상수 사용으로 치환), `model/DashJobRunner.h`, `view/DashAnalysisLauncherWidgetLauncher.cpp` (`fillTargetPartCombo` dfsxml 분기), `controller/DashExtensionProcess.h` (`:58-59` 상수 주석의 인자 규격 갱신 — 상수 자체는 이미 있다)
- 선행: LCH-31 (CLI·JSON 계약), LCH-11 (MBD 쪽이 먼저 받아야 한다), PR #651·#652 머지
- 충돌: LCH-03 · LCH-04 · LCH-05 · LCH-12 · LCH-13 · B2 교집합: DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절) · DashAnalysisLauncherWidgetLauncher.cpp → LCH-01 LCH-08 LCH-15 LCH-16 LCH-17 LCH-28 LCH-29 LCH-33 · DashJobRunner.h → CAD-01 LCH-02 LCH-06 LCH-07 LCH-14 · DashExtensionProcess.h → EXE-11 EXE-12
- 흡수: #647-a · #647-c · LCH-c26, LCH-c28
- 비고: GUI 가 넘기는 인터페이스(CLI 인자·JSON) 는 LCH-31 DEC 의 산출물이다 — 되돌리기 비용이 큰 결정이라 LCH-10·LCH-11 착수 전에 기록한다

### LCH-11 · DashOptiMBD AnsysMotion 이 run 마다 dfsxml·dfmm·dfg 를 만들고 모델 종속 규칙을 수용한다
- 종류: EXT | 규모: M | 태그: B · feature
- 목표: DashOptiMBD 의 `motion-writer`/`motion-launcher` 를 하나의 진입점으로 묶어 템플릿 경로·VTU·DOE 값·출력 폴더를 받고, `.dfsxml`·`.dfmm`·`.dfg` 를 생성한 뒤 솔버를 돌린다. Target Part·밀도·단위 등 모델 종속 값은 Python 쪽 설정으로 옮긴다.
- 완료 기준: 외부 저장소 PR — LCH-31 이 정한 계약대로 구현 + LGE 예제와 다른 모델 1건의 실행 로그
- 변경 범위: DashOptiMBD (GUI 쪽은 추적만)
- 선행: LCH-31 (계약)
- 충돌: -
- 흡수: #647-b · #647-c · LCH-c27, LCH-c28

### LCH-12 · dfsxml 경로의 동기 대기와 `processEvents` 14곳을 비동기로 바꾼다
- 종류: PR | 규모: M | 태그: B · refactor
- 목표: `waitForVtuFileComplete` 폴링(배치 `co_await` 뒤라 파일은 이미 써져 있다 — 존재 검사로 대체), `runMotionWriter` 의 `waitForFinished(500)` 루프, 샘플 루프의 `processEvents` 7곳을 제거한다. 외부 프로세스 대기는 `QProcess` 시그널 또는 `qCoro(process).waitForFinished()` 로.
- 완료 기준: (1) `model/DashJobRunner*.cpp` 에 `processEvents`·`msleep` 0건 (2) dfsxml 배치 실행 중 UI 가 응답하고 [Start] 재클릭이 거부된다 (3) 케이스 결과·상태가 종전과 같다
- 변경 범위: `model/DashJobRunnerAnsysMotion.cpp`, `model/DashJobRunner.h`
- 선행: LCH-10 (단일 호출로 줄어든 뒤 하면 대기 지점이 1곳이 된다), LCH-03
- 충돌: LCH-04 · LCH-05 · B2 교집합: DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절) · DashJobRunner.h → CAD-01 LCH-02 LCH-06 LCH-07 LCH-14 · PR #652(DashJobRunner.h·DashJobRunnerAnsysMotion.cpp) · PR #651(DashJobRunner.h)
- 흡수: DOE-D11 · LCH-c43 · #458-b(dfsxml 몫) · DOE-c40(LCH-c75) · RUN-c10(LCH-c87) · EXE-c46(LCH-c97) · EXE-c39(`msleep(100)` 3곳, LCH-c91) · EXE-c43(DOE-D11 몫, LCH-c93)
- 비고: LCH-10 을 먼저 하면 `waitForVtuFileComplete`·`runMotionWriter` 가 사라져 이 항목은 프로세스 1개의 비동기 대기로 줄어든다. 순서를 바꾸면 M→L. #458-b 의 "dfsxml 1·2단계 ProcessJob 수렴" 은 그 1개 대기를 EXE 의 ProcessJob 으로 두는 것 — #458 담당은 EXE, 여기선 dfsxml 몫만

### LCH-13 · 모핑 실행기가 run 폴더 기준 경로를 직접 받게 한다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `DashMorphingDoeExecutor::plan/Execute`·`runDoeBatchForSet` 의 `referenceDatName` 인자를 `runsBaseDir`(절대경로) 로 바꾸고 `QDir(moduleDir).filePath(referenceDatName)` 조립을 지운다. 러너는 `ctx.outputRoot` 를 그 이름으로 넘긴다.
- 완료 기준: (1) executor 에 `moduleDir` 조립이 없다 (2) run 폴더 위치가 `<outputRoot>/<runKey>` 로 종전과 같다 (3) `TestDoeBatchChain` 통과
- 변경 범위: `controller/DashMorphingDoeExecutor.cpp/.h`, `model/DashJobRunner.cpp` (`morphFromTemplate`), `model/DashJobRunnerAnsysMotion.cpp` (`runAnsysMotionMorphingDoe`)
- 선행: PR #651 머지 (`DashJobRunner.cpp`) · PR #652 머지
- 충돌: LCH-02 · LCH-07 · LCH-10 · B2 교집합: DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절) · DashJobRunner.cpp → LCH-03 LCH-14 PRJ-09 UIC-20 · DashMorphingDoeExecutor.cpp → MOR-10 MOR-11 · DashMorphingDoeExecutor.h → MOR-11 · PR #654(DashMorphingDoeExecutor.cpp)
- 흡수: DOE-D13 · LCH-c44 · DOE-c42(LCH-c77)

### LCH-14 · JobRunner·케이스 표의 죽은 코드와 유명무실 인자를 지운다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `DashJobRunner::isFeSafePostEnabled`, `setDesignVariableModel`/`m_designVariableModel`, `MotionLauncherTask.logDir`, `launchAnsysJournal` 의 `connLog` 빈 연결, `DashDoeCasesWidget::setDirectLauncherCases` 를 삭제하고 `runDoeJobs(QStringList templateFilePaths)` 를 `QString templatePath` 로 좁힌다. `DashDoeSampler::extractDfsxmlMorphingInfo` 는 멤버 상태를 쓰지 않으므로 static 으로 바꿔, Motion 의 임시 `DashDoeSampler sampler;` 모델 생성과 중복 `GetIOController()` 가드(`runAnsysMotionMorphingDoe:462-468`)를 없앤다.
- 완료 기준: (1) 위 심볼 0건 (2) `DashJobRunner*.cpp` 에 `DashDoeSampler` 인스턴스 생성 0건 (3) 빌드·`ctest` 통과 (4) 동작 변경 없음
- 변경 범위: `model/DashJobRunner.h/.cpp`, `model/DashJobRunnerFeSafe.cpp`, `model/DashJobRunnerAnsysJournal.cpp`, `model/DashJobRunnerAnsysMotion.cpp`, `model/DashAnalysisLaunchExecutor.cpp`, `view/DashDoeCasesWidget.cpp/.h`, `model/DashDoeSampler.h/.cpp` (DOE 접점 — `extractDfsxmlMorphingInfo` static 화 1줄)
- 선행: PR #651 머지 (`DashJobRunner.h/.cpp`·`DashJobRunnerFeSafe.cpp`·`DashJobRunnerAnsysJournal.cpp`) · PR #652 머지 (`setDirectLauncherCases`·`setDesignVariableModel` 의 호출부를 그 PR 이 지운다)
- 충돌: LCH-07 · LCH-08 · B2 교집합: DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절) · DashAnalysisLaunchExecutor.cpp → LCH-06 LCH-16 LCH-28 LCH-34 PRJ-09 UIC-20 · DashJobRunner.cpp → LCH-02 LCH-03 LCH-13 PRJ-09 UIC-20 · DashJobRunner.h → CAD-01 LCH-02 LCH-06 LCH-10 LCH-12 · DashJobRunnerAnsysJournal.cpp → CAD-01 LCH-06 LCH-27 LCH-29 UIC-19 · DashDoeSampler.h → DOE-05 DOE-07 DOE-08 DOE-11 DOE-12 · DashJobRunnerFeSafe.cpp → LCH-18 LCH-30 PRJ-14 UIC-19 · DashDoeCasesWidget.cpp → LCH-09 LCH-34 · DashDoeCasesWidget.h → LCH-34
- 흡수: DOE-U4(잔여 1) · DOE-U5(`connLog`) · LCH-c54, LCH-c55, LCH-c56 · DOE-c22(LCH-c66) · DOE-c24(LCH-c67)
- 비고: LCH-10 이 dfsxml 경로를 MBD 단일 호출로 재작성하면 `extractDfsxmlMorphingInfo` 호출 자체가 사라진다 — LCH-10 이 먼저면 그쪽에 흡수

### LCH-15 · 실행이 끝나면 Preprocess 탭이 새 결과 기준으로 입력을 다시 찾는다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `analysisFinished` 에서 `m_inputsResolved` 를 내려 Preprocess 입력을 무효화한다(대안: `resultFiles` 의 mtime 을 비교 기록에 포함). 다음 Preprocess 탭 진입 또는 현재 탭이 Preprocess 면 즉시 `refreshPreprocessTab` 이 새 `resultFiles` 로 목록을 채운다.
- 완료 기준: (1) Re-run 뒤 Preprocess 탭의 부품·하중 목록이 새 결과 기준 (2) 결과가 바뀌지 않은 Set 재진입은 종전처럼 재탐색을 생략한다
- 변경 범위: `view/DashAnalysisLauncherWidgetLauncher.cpp` (`connectLaunchExecutor`), `model/DashAnalysisLauncher.cpp` (`preprocessInputsChanged`)
- 선행: PR #651·#652 머지 · PRE-02 (#433 종료 검토 — `model/DashAnalysisLauncher.cpp` 진행 중)
- 충돌: #433 (In progress) · LCH-01 · LCH-17 · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashAnalysisLauncherWidgetLauncher.cpp → LCH-08 LCH-10 LCH-16 LCH-28 LCH-29 LCH-33 · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp)
- 흡수: #646-1 · LCH-c32
- 비고: PRE 접점 — `preprocessInputsChanged` 는 결과 경로. 기제는 "비교 조건이 없다" 가 아니다 — `:293` 이 run 기록(`run.dir`+`run.resultFiles`)을 이미 비교하지만, Re-run 이 같은 이름의 결과 파일을 다시 만들면 기록이 동일해 재탐색을 건너뛰고 `readerSession_` 의 옛 내용이 남는다. `refreshPreprocessTab` 은 Set 선택(`DashAnalysisLauncherWidget.cpp:285`)과 탭 전환(`:878`) 양쪽에서 불린다

### LCH-16 · Re-run 이 새 결과가 Done 이 된 뒤에만 이전 결과를 버린다
- 종류: PR | 규모: M | 태그: A · bug
- 목표: `discardResults` 의 즉시 삭제를 "보류" 로 바꾼다 — Start 시 이전 `resultFiles` 를 `*.prev` 로 옮기고 케이스 상태만 초기화, 케이스 Done 시 `.prev` 삭제, Failed/Cancelled/프로젝트 닫힘, 그리고 `analysisFailed`(실행 거부·Stop) 시 `.prev` 를 되돌리고 종전 Done 상태·`resultFiles` 를 복구한다.
- 완료 기준: (1) Re-run 실패 케이스의 이전 결과 파일과 Done 상태가 남는다 (2) Re-run 성공 케이스에 `.prev` 가 남지 않는다 (3) Stop 뒤에도 이전 결과가 복구된다 (4) MAPDL 미설정·"No active cases" 등 사전 거부 뒤에도 이전 결과와 Done 상태가 보존된다 (5) `producedResultFiles` 의 mtime 비교가 `.prev` 에 영향받지 않는다
- 변경 범위: `model/DashAnalysisLaunchExecutor.cpp/.h` (`discardResults` · `onCaseStatusUpdated` · `cancelAllRuns`), `model/preprocessor/DashAnalysisLauncherConfig.cpp/.h` (`clearCaseResults` 대신 보류 상태), `view/DashAnalysisLauncherWidgetLauncher.cpp` (Start 람다), `tests/TestAnalysisLauncherConfig.cpp`
- 선행: LCH-07 (기록 주체가 executor 하나여야 Done/Failed 시점 훅이 한 곳), PR #651·#652 머지
- 충돌: LCH-01 · LCH-17 · LCH-15 · B2 교집합: DashAnalysisLauncherWidgetLauncher.cpp → LCH-08 LCH-10 LCH-28 LCH-29 LCH-33 · DashAnalysisLaunchExecutor.cpp → LCH-06 LCH-14 LCH-28 LCH-34 PRJ-09 UIC-20 · DashAnalysisLauncherConfig.cpp → DOE-03 DOE-16 PRE-14 PRE-15 PRE-27 PRE-32 · TestAnalysisLauncherConfig.cpp → DOE-03 DOE-16 PRE-14 PRE-15 PRE-32 · DashAnalysisLauncherConfig.h → DOE-03 PRE-15 PRE-27 PRE-32 · DashAnalysisLaunchExecutor.h → LCH-34
- 흡수: #646-2 · LCH-c33
- 비고: run 폴더를 재사용하므로 MAPDL 은 같은 이름의 `.rst` 를 덮어쓴다 — 이름 변경(`.prev`) 없이는 보존이 불가능하다. 새 run 폴더 번호를 쓰는 대안은 출력 레이아웃·Preprocess 조인(`DashLauncherRuns`) 을 바꾸므로 택하지 않는다. Start 람다가 `discardResults`(`:161`) 를 `runDoeAsync`(`:175`) **앞에** 부르므로 사전 검증 거부(`jobFailed` 4곳 · executor "No active cases")가 나면 이미 지운 결과를 되돌릴 지점이 없다 — 대안으로 `discardResults` 를 `runAccepted` 뒤로 옮기면 복구 경로 자체가 줄어든다

### LCH-17 · Start 확인창에서 Skip 의 뜻을 알린다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: 확인창 본문을 "Re-run: 이전 결과 파일을 지우고 다시 실행 · Skip: 결과가 있는 케이스는 건너뛰고 나머지만 실행" 으로 바꾸고 Skip 버튼에 툴팁을 단다.
- 완료 기준: 확인창 본문·툴팁에 Skip 의 의미가 보인다
- 변경 범위: `view/DashAnalysisLauncherWidgetLauncher.cpp` (Start 람다)
- 선행: PR #651·#652 머지
- 충돌: LCH-01 · LCH-15 · LCH-16 · B2 교집합: DashAnalysisLauncherWidgetLauncher.cpp → LCH-08 LCH-10 LCH-28 LCH-29 LCH-33
- 흡수: #646-3 · LCH-c34

### LCH-18 · fe-safe ODB 원본 복원을 실측하고 실패 사유 기록을 확인한다
- 종류: INV | 규모: S | 태그: A, B · bug
- 목표: PR #651 머지 뒤 fe-safe 설치 환경에서 A.inp·B.inp Done → .stli Start 를 돌려 run 폴더에 `A.odb`·`B.odb` 가 놓이고 fe-safe 가 `C.odb` 를 내는지 실측한다 (ODB 미발견 시의 사유 기록·Stale ODB 배제는 LCH-30 이 담당).
- 완료 기준: 실측 결과 기록 — 통과면 LCH-30 뒤 #648 닫기, 실패면 지점(`DashJobRunnerFeSafe.cpp:runFeSafeDoe` · `DashFeSafeOdbSources`) 과 후속 PR 범위
- 변경 범위: (조사) `model/DashJobRunnerFeSafe.cpp`, `model/preprocessor/DashFeSafeOdbSources.h` (PR #651 신설)
- 선행: PR #651 머지
- 충돌: B2 교집합: DashJobRunnerFeSafe.cpp → LCH-07 LCH-14 LCH-30 PRJ-14 UIC-19 · DashFeSafeOdbSources.h → LCH-30
- 흡수: #648 기대 1(실측 몫) · LCH-c29 · DOE-c41(LCH-c76)
- 비고: #648 본문이 "정확한 실패 지점은 아직 파악하지 못했다" 라 실측 없이는 닫을 수 없다. PR #651 은 출처 **위치**만 고친다 — 기대 2(탐색 경로 사유 기록)와 DOE-D12 의 "현재 DOE 것인지 안 본다" 는 LCH-30

### LCH-19 · Direct Launch 의 .stli 실행·여러 파일 큐잉 지원 여부를 정한다
- 종류: DEC | 규모: S | 태그: B
- 목표: PR #652 가 범위 밖으로 둔 두 기능을 (a) 지원 안 함 (b) .stli 만 (c) 둘 다 중 하나로 확정한다. (b)/(c) 면 ODB 출처 지정 UI 와 `DashDirectLaunchStaging` 의 큐 확장을 후속 PR 로 적는다.
- 완료 기준: 결정 기록
- 변경 범위: (결정만) 후속 후보 `controller/DashDirectLaunchRunner.cpp`, `view/dialog/DashDirectLaunchDialog.cpp`
- 선행: PR #651·#652 머지
- 충돌: B2 교집합: DashDirectLaunchDialog.cpp → RUN-30
- 흡수: #604 잔여 · LCH-c19

### LCH-20 · #456 닫기 — 정규 경로 [Start] 는 이미 워커·시그널 구동이다
- 종류: CLOSE | 규모: S | 태그: B
- 목표: 닫기 사유 기록.
- 완료 기준: 닫기 사유 — `runDoeJobs` 가 코루틴으로 모핑을 `DashMorphingService::background()` 에 `co_await`(#564 d8be33a4 · #586), 솔버 제출은 cae-launcher 비동기, 정규 경로 `processEvents` 0. `generateInputCases` 부재(#570). 잔여 동기 대기는 dfsxml 경로뿐이며 #456 이 비범위로 명시한 것 → LCH-12
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #456 · DOE-D9 · LCH-c01 · DOE-c38(LCH-c73) · EXE-c43(DOE-D9 몫, LCH-c93)

### LCH-21 · #502 닫기 — 라디오 단일 선택 전제가 사라졌고 범위 밖으로 확정됐다
- 종류: CLOSE | 규모: S | 태그: B
- 목표: 닫기 사유 기록.
- 완료 기준: 닫기 사유 — #601 이후 Analysis Launcher Set 은 파일 1개에 pin 되어 "여러 해석파일 = 여러 Set" 이 됐고 `DashReferenceFileWidget`·라디오가 삭제됐다(#617). PM4 가 "T26 루프 — 착수하지 않는다(2026-09-22)" 로 확정
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #502 · PM4 G8 "T26 루프" · LCH-c15 · DOE-c32(LCH-c69)

### LCH-22 · #438 닫기 — 추적 전용 부모
- 종류: CLOSE | 규모: S | 태그: B
- 목표: 닫기 사유 기록.
- 완료 기준: 닫기 사유 — 자식 전부 처분: #439 → LCH-03 · #440 → LCH-23 · #441 → LCH-08·LCH-09 · #442 → LCH-24
- 변경 범위: -
- 선행: LCH-03 · LCH-08 · LCH-09
- 충돌: -
- 흡수: #438 · LCH-c14

### LCH-23 · #440 닫기 — PR #652 가 Direct 표의 상태 배선을 해소한다
- 종류: CLOSE | 규모: S | 태그: D
- 목표: 닫기 사유 기록.
- 완료 기준: 닫기 사유 — PR #652 가 Direct Set 위젯을 지우고 새 Dialog 표가 러너 중계 시그널을 구독(본문 "Output Cases 상태가 Enqueued 에서 바뀌지 않음 → 수정"). 머지 뒤 닫는다
- 변경 범위: -
- 선행: PR #652 머지
- 충돌: -
- 흡수: #440 · DOE-U2 · LCH-c10, LCH-c18 · DOE-c35(U2 몫, LCH-c70) · EXE-c44(DOE-U2 몫, LCH-c94) · UIC-c56(DOE-U2 몫, LCH-c95)

### LCH-24 · #442 기록 — GitHub 에서 이미 닫힘
- 종류: CLOSE | 규모: S | 태그: C
- 목표: 보드 잔존분 정리.
- 완료 기준: 보드에서 제거 (범위 정리로 닫힌 이슈)
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #442 · LCH-c13

### LCH-25 · #604 닫기 — PR #652 머지로 종결, 잔여는 LCH-14·LCH-19
- 종류: CLOSE | 규모: S | 태그: B, D
- 목표: 닫기 사유 기록.
- 완료 기준: 닫기 사유 — 범위 3항(Tool 메뉴 Dialog·창 닫아도 지속 / Direct Set 위젯 제거 / Output Cases 상태) 전부 PR #652. 잔여: `setDirectLauncherCases`·`setDesignVariableModel` 정의 잔존 → LCH-14, .stli·다중 큐잉 → LCH-19
- 변경 범위: -
- 선행: PR #652 머지
- 충돌: -
- 흡수: #604 · LCH-c06, LCH-c16, LCH-c17, LCH-c18 (잔여 LCH-c19 → LCH-19, LCH-c55 → LCH-14) · DOE-c35(Direct 잔재, LCH-c70)

### LCH-26 · #616 닫기 — PR #651 머지로 종결, 잔여는 #647·#648
- 종류: CLOSE | 규모: S | 태그: A, C
- 목표: 닫기 사유 기록.
- 완료 기준: 닫기 사유 — 결정표 포맷 3종 × 범위 4항 + 추가 결정 2건 전부 PR #651 (Add File 복사·원장·Launcher Set / RW 검사 `DashReferenceKind::isRwReadable` / Launcher 탭 분기 — dfsxml·stli 는 dev 가 이미 일치, wbpj `_files` 한정 / `odbSourceSets` + fe-safe 복사 / 이름 충돌 경고 / 삭제 연동). 하위 #647 → LCH-10·LCH-11, #648 → LCH-18
- 변경 범위: -
- 선행: PR #651 머지
- 충돌: -
- 흡수: #616 · LCH-c08, LCH-c20, LCH-c21, LCH-c22, LCH-c23, LCH-c24, LCH-c25

### LCH-27 · Direct wbpj 다중 파일에서 NX 로드 완료 구독을 잡 단위로 해제한다
- 종류: PR | 규모: S | 태그: B · bug
- 목표: `startDirectAnsysJournalJobs` 가 wbpj 마다 `loadPrtCompleted`·`nxCadParametersJson` 람다를 연결한 뒤, 첫 완료 람다 안에서 `disconnect(nxCad, …, this, nullptr)` 로 이 객체의 모든 구독을 끊어 두 번째 이후 wbpj 의 람다가 영영 불리지 않는다(케이스 Enqueued 잔존 → 종결 계약 위반). `launchAnsysJournal` 의 선례(`connCompleted`/`connFailed` 핸들)대로 `QMetaObject::Connection` 을 잡아 자기 것만 끊고, `capturedParams` 는 stp 경로 일치 검사를 거친 뒤에만 채운다.
- 완료 기준: (1) wbpj 2개 Direct 실행에서 두 케이스 모두 ANSYS Journal 이 기동하고 Done/Failed 에 이른다 (2) `DashJobRunnerAnsysJournal.cpp` 에 `disconnect(nxCad, …, this, nullptr)` 0건
- 변경 범위: `model/DashJobRunnerAnsysJournal.cpp` (`startDirectAnsysJournalJobs`)
- 선행: LCH-29 (wbpj 경로 처분) · PR #652 머지 (Direct 진입이 `DashDirectLaunchRunner` 로 바뀜 — 호출 시그니처 확인) · LCH-19 ((a) "다중 큐잉 지원 안 함" 이면 시그니처를 파일 1개로 좁히는 쪽이 더 작다)
- 충돌: LCH-06 · LCH-07 · LCH-14 (같은 파일) · B2 교집합: DashJobRunnerAnsysJournal.cpp → CAD-01 UIC-19 · PR #651(DashJobRunnerAnsysJournal.cpp)
- 흡수: #249(범위 밖 절 — CAD 가 넘김) · CAD-c14 · LCH-c64
- 비고: 단일 wbpj 에서는 발현하지 않아 PR #652 Direct Dialog(파일 1개, 다중 큐잉 범위 밖) 에서는 잠복. `nxCadParametersJson` 공유 캡처도 같은 기제 — 파일 N 개가 같은 `capturedParams` 를 덮어쓴다. LCH-29 가 **제거**면 이 항목은 소멸하고, **동결**이면 LCH-19(a) 로 대체한다(시그니처를 파일 1개로 좁히는 쪽이 더 작다) — **현행 유지**일 때만 본문대로 수술한다

### LCH-28 · Launcher 배치 실행의 진행·취소·가드 표시를 EXE-07 규약에 맞춘다
- 종류: PR | 규모: S | 태그: B, D · feature
- 목표: #463 의 LCH 몫. 현행은 Start/Stop 버튼(`setLauncherIdle`) + executor `isRunning` 가드 + 케이스 표 상태 열로 진행·취소·가드 3요소를 이미 갖춘다. EXE-07 이 정한 규약(상태바 진행바·문구·취소 버튼 자리·반려 안내)과의 차이분만 배선한다 — 예: 상태바에 "N/M 케이스" 결정 진행바, 실행 중 Start 재클릭 반려 안내(EXE-09 헬퍼).
- 완료 기준: (1) EXE-07 규약 표 대비 Launcher 탭의 차이 0 (차이가 없으면 확인 기록으로 종료) (2) 기존 Start/Stop·케이스 표 동작 불변
- 변경 범위: `view/DashAnalysisLauncherWidgetLauncher.cpp` (`connectLaunchExecutor` · `setLauncherIdle`), `model/DashAnalysisLaunchExecutor.cpp` (케이스 집계 진행률 방출 — 규약이 요구할 때만)
- 선행: EXE-07 (규약) · EXE-09 (가드 헬퍼) · PR #651·#652 머지
- 충돌: LCH-01 · LCH-08 · LCH-15 · LCH-17 (같은 파일) · B2 교집합: DashAnalysisLauncherWidgetLauncher.cpp → LCH-10 LCH-16 LCH-29 LCH-33 · DashAnalysisLaunchExecutor.cpp → LCH-06 LCH-07 LCH-14 LCH-16 LCH-34 PRJ-09 UIC-20
- 흡수: #463(LCH 몫) · EXE-c23 · LCH-c92
- 비고: #456 은 해소됨(LCH-20) 이라 이 항목이 #463 의 LCH 적용처. PR #652 Direct Dialog 의 진행 표시도 머지 뒤 같은 규약 — 파일은 머지 뒤 확정

### LCH-29 · wbpj 배치·Direct 실행 경로의 처분을 정한다
- 종류: DEC | 규모: S | 태그: A, C
- 목표: `.wbpj`(ANSYS Workbench) 경로를 (a) **현행 유지** — #616 결정표가 정본이고, 매니페스트의 "사장·불개입" 은 기준모델·조합·스탬프 묶음 안의 불개입(D32·D33 철회)으로 한정한다 / (b) **동결** — 버그만 고치고 기능 확장 없음 / (c) **제거** — 코드·UI 를 걷어낸다 중 무엇으로 할지 정한다. 입력 자료가 시간순으로 모순된다: `01-sources/wiki/Project-Manifest-CAD-Path-Disposition.md`(2026-09-18) "특화 일회성 경로 — 사장 예정, 개선 불개입 · wbpj DOE 전체 격리" vs #616 결정표(2026-10-02) wbpj 열 "Add File 복사 · Launcher Set `{파일명}_wbpj` · Target Part `.prt` 콤보 현행 유지 · 결과 `.rst` → #640 콤보" + PR #651(wbpj Project Assets·`_files` 한정) · PR #652(Direct Dialog 가 wbpj+`_files` 스테이징).
- 완료 기준: 결정 기록 — (1) 선택지 (a) 현행 유지 / (b) 동결 / (c) 제거 중 하나와 근거(어느 문서가 정본인지) (2) 소비자별 축소·되돌림 범위 (3) **PRJ 원장 조항** — (c) 제거(사장 확정)면 `.wbpj`·`.stli` 의 원장 비편입을 확정하고 PRJ 신규 항목은 0, (a) 현행 유지면 PRJ 에 `.wbpj`·`.stli` 원장 편입 항목 1건을 신설한다(`model/DashReferenceModelLedger` · Project Assets 트리 · `DashMainWindow::copyFileIntoProject`), (b) 동결이면 신규 편입 없이 현행 취급만 유지한다
- 변경 범위: (결정만) 후속 후보 `model/DashJobRunnerAnsysJournal.cpp`(wbpj TU 전체), `view/DashAnalysisLauncherWidgetLauncher.cpp`(`fillTargetPartCombo` wbpj 분기), PR #651·#652 의 wbpj 분기
- 선행: -
- 충돌: B2 교집합: DashAnalysisLauncherWidgetLauncher.cpp → LCH-01 LCH-08 LCH-10 LCH-15 LCH-16 LCH-17 LCH-28 LCH-33 · DashJobRunnerAnsysJournal.cpp → CAD-01 LCH-06 LCH-07 LCH-14 LCH-27 UIC-19 · PR #652(DashAnalysisLauncherWidgetLauncher.cpp) · PR #651(DashAnalysisLauncherWidgetLauncher.cpp·DashJobRunnerAnsysJournal.cpp)
- 흡수: Project-Manifest-CAD-Path-Disposition "사장 경로로 격리" 표 · #616 결정표 wbpj 열
- 비고: 소비자(결정 영향 대상) — **CAD-01 Phase 3** · **CAD-02** · **CAD-05**(불개입 경로 수정분을 뺄지) · **LCH-06** · **LCH-27** · **PRJ**(`.wbpj`·`.stli` 원장 편입이 PRJ 코드 — 완료 기준 (3)). CAD 쪽 항목의 `선행` 등록은 `보류: CAD 몫`. PRJ 소비자 등록은 **완료** — PRJ.md 머리말 · PRJ-21 비고 · 대응표 `LCH-29 (DEC, 접점) → 항목 없음` 행. PRJ 조항 근거 — 매니페스트가 `.wbpj`·`.stli` 원장 편입(후속작업 5)을 "범위 밖 유지" 로 미뤘고 그 코드가 PRJ 소유다. 현행 PRJ 소유 파일에 `wbpj` **0건**(`DashMainWindow.cpp`·`DashModelingTreeWidget.cpp`·`DashReferenceModelLedger.cpp`·`DashProject.cpp`), `.stli` 는 `view/DashMainWindow.cpp` 5곳(`:362`·`:2628` Add File 필터 · `:2649` 부모 폴더 복사 · `:2963`·`:2968` Reference Files 선택)이고, PR #651 이 `model/DashProject.cpp`·`view/DashModelingTreeWidget.cpp`·`model/DashReferenceSetName.h` 에 정책을 들여놓는다(PRJ 검토 19 의 "stli 1곳" 은 실측 5곳으로 정정). 축소 내용 — (c) 면 LCH-06 은 Journal TU 삭제 PR 에 흡수(시그널 자체 삭제), LCH-27 은 소멸, PR #651·#652 의 wbpj 분기와 #640 wbpj 사용처(PRE)를 되돌린다 / (b) 면 LCH-27 은 LCH-19(a) 로 대체. **LCH-28 은 포맷 무관**(`setLauncherIdle`·executor 집계)이라 축소 없음 — (c) 일 때 `cancelAllRuns` 의 Journal `m_stpBatch` 분기(`:502`)만 범위에서 빠진다

### LCH-30 · fe-safe ODB 출처를 현행 DOE 의 Done 케이스로 한정하고, 미발견 시 탐색 경로를 남긴다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `runFeSafeDoe` 의 ODB 복사가 파일 존재만 보지 않고, 출처 Set 케이스가 Done 이며 현행 `tableId` 인지(`DashLauncherRuns::isCurrentCase`) 검사해 stale ODB 를 배제한다. 하나도 못 찾으면 Failed 와 함께 **어느 경로를 봤는지** 목록을 로그와 `caseLogUpdated`(케이스 표 Log 열)에 남긴다.
- 완료 기준: (1) 출처 Set 을 재샘플링해 `tableId` 가 바뀐 뒤 .stli Start 하면 옛 ODB 가 복사되지 않고 Failed (2) ODB 부재 케이스의 Log 열에 탐색한 절대경로 전부가 보인다 (3) 정상 경로(출처 Done · 현행 tableId)는 종전과 같이 복사된다
- 변경 범위: `model/DashJobRunnerFeSafe.cpp` (`runFeSafeDoe`), `model/preprocessor/DashFeSafeOdbSources.h` (PR #651 신설 — 탐색 경로 반환), `model/preprocessor/DashLauncherRuns.h` (`isCurrentCase` 재사용)
- 선행: PR #651 머지 (출처 위치·`odbSourceSets` 를 그 PR 이 깐다)
- 충돌: LCH-18 (같은 함수 실측) · B2 교집합: DashJobRunnerFeSafe.cpp → LCH-07 LCH-14 PRJ-14 UIC-19 · DashLauncherRuns.h → PRE-32
- 흡수: #648 기대 2 · DOE-D12(잔여 — "판정이 파일 존재뿐") · LCH-c23(출처 위치 외 잔여) · LCH-c76
- 비고: dev 의 미발견 로그는 "FE-safe prelaunch failed (no ODB sources found)" 1줄이고 PR #651 도 이 줄을 바꾸지 않는다(`DashJobRunnerFeSafe.cpp:286-290`). PR #651 의 `DashFeSafeOdbSources::sourceOdbPath` 는 `QFileInfo::exists` 만 본다

### LCH-31 · GUI↔DashOptiMBD 단일 호출 계약을 정한다
- 종류: DEC | 규모: S | 태그: B, C
- 목표: LCH-10·LCH-11 이 공유할 호출 계약을 먼저 기록한다 — 인자 전달 형식(템플릿 경로·VTU 경로·DOE 값·출력 폴더·Target Part 를 CLI 인자로 줄지 JSON 파일로 줄지), 산출물 이름 규칙(`{runKey}.dfsxml`·`.dfmm`·`.dfg`·`.dfr`), 종료 코드·stdout 규약(성공/실패 판정 근거를 exit code 로만 둘지 stdout 토큰도 쓸지), 모델 종속 값(밀도·단위·`-b` 블록)의 소유처.
- 완료 기준: 결정 기록 — 계약 표 1개(인자 · 산출물 · 종료 규약 · 모델 종속 값 소유처)와 선택 근거
- 변경 범위: (결정만) 후속 후보 `controller/DashExtensionProcess.h`(`MBD_MotionWriter`·`MBD_MotionLauncher` 상수 주석의 인자 규격), DashOptiMBD CLI
- 선행: -
- 충돌: B2 교집합: DashExtensionProcess.h → EXE-11 EXE-12 LCH-10
- 흡수: LCH-10 비고의 "LCH-11 과 한 번에 정한다 — 되돌리기 비용이 큰 결정"
- 비고: 00-plan 1절 "되돌리기 비용이 큰 결정(공개 API·CLI 인터페이스)" 에 해당해 EXT(LCH-11)보다 앞선다. 현행은 두 서브커맨드가 각각 `motion-writer <ref_folder> <vtu_dir> <density> --unit m -o <out> -b 19` · `motion-launcher <ansys_path> <xml_dir>` 이고, 완료 판정이 exit code 와 stdout 양쪽에 걸쳐 있다(LCH-05 의 원인)

### LCH-32 · Set 상태 갱신 비용을 검증하고 필요한 경우에만 기록 파일을 분리한다
- 종류: DEC | 규모: S | 태그: A, C
- 목표: #444는 #441 하위 저장 경계 작업이다. 저장·읽기·화면 갱신 비용을 측정하고 기존 구조의 단일 라이터·증분 갱신으로 해결 가능한지 먼저 판단한다. 해결되지 않는 병목에만 파일 분리를 선택하고 효과를 검증한다.
- 완료 기준: 상태 갱신 전후 비용과 병목을 기록하고 기존 구조 유지 또는 필요한 파일만 분리하는 결정을 남긴다. 분리 선택 시 저장·읽기·화면 갱신 개선 및 복원 정합을 검증한다. 모든 Set JSON 일괄 분할을 요구하지 않는다.
- 변경 범위: (결정만)
- 선행: -
- 충돌: -
- 흡수: #444 · PRJ-c60 · PRJ-c07(LCH-c89)
- 비고: LCH-07·LCH-08은 기존 구조 개선 대안 및 공유 코드 접점이다. 실측 없이 분할 불필요로 확정하지 않는다. 저장 경계 개선 후 LCH-09(#441)의 재시작 복구를 적용하며 ID 참조 전환을 선행으로 두지 않는다. PER-03의 포맷 규약은 실제 분리 결정 시 적용한다.

### LCH-33 · Start가 선택한 DOE 입력과 실제 산출물 출처를 검증한다
- 종류: PR | 규모: S | 태그: C, A · bug
- 목표: runDoeAsync 호출 전에 현재 선택한 DOE setId와 Table·deck의 필수 출처 및 실제 선택 관계를 공통 계약으로 검증한다. 다른 DOE setId의 유효한 입력으로 변경할 수 있다. 현재 Launcher ID는 유지하고 선택 변경만으로 기존 실행 스냅샷·결과 출처를 바꾸지 않으며 새 실행이 실제 사용하는 출처를 기록한다.
- 완료 기준: ① 다른 유효 DOE Set 선택 후 Start 가능 ② 선택만 바꾼 상태의 기존 결과·출처 불변 ③ 새 실행 결과 덮어쓰기 시 실제 입력 출처 갱신 ④ 필수 출처 누락·잘못된 참조는 실행 전 거절하고 재생성 안내, runDoeAsync 미호출 ⑤ 쓰기 실패와 출처 검증 실패 사유 구분 ⑥ 최초 핀 부재를 통과 근거로 삼지 않음.
- 변경 범위: `view/DashAnalysisLauncherWidgetLauncher.cpp` (Start 람다), `model/DashAnalysisLauncher.h/.cpp` (`snapshotDoeTable` · 대조 판정 신설)
- 선행: DOE-16 (생산 출처와 스냅샷 전달)
- 충돌: LCH-01 · LCH-15 · LCH-16 · LCH-17 (같은 Start 람다·같은 파일) · PRE-32 (같은 출처 판독 계약·실행 기록 접점) · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashAnalysisLauncherWidgetLauncher.cpp → LCH-08 LCH-10 LCH-28 LCH-29 · DashAnalysisLauncher.h → PRE-03 PRE-08 PRE-16 PRE-23 PRE-24 PRJ-22 · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h)
- 흡수: #368 Phase 2 (T21 중 Start 거절 몫 — PRE 검토 #2 인계) · LCH-c99
- 비고: PRE-32와 같은 공통 계약을 사용하되 PRE-32의 최초 핀 기록에 의존하지 않는다. 기존 snapshotDoeTable 쓰기 실패 취소는 유지한다. #650 최신성 표시는 출처 유효성 검증과 별도다. 입력 선택·재실행 시나리오와 스냅샷 보존·갱신을 검증한다.

### LCH-34 · 런처 JSON 기록 실패 사유를 호출부에서 알린다
- 종류: PR | 규모: S | 태그: D, A · bug
- 목표: PRE-15 가 `QString* error` 로 내주는 사유를 LCH 호출부가 받아 알린다 — Active 체크 기록 실패(`DashDoeCasesWidget` 2곳, 사용자 행위)는 모달에 경로 + 사유를 띄우고 체크 상태를 되돌린다. 케이스 상태 기록 실패(executor 단일 라이터)는 런당 1회 통지 + 실패 키 전체 로그로 모은다.
- 완료 기준: (1) 설정 파일을 깨진 JSON 으로 둔 뒤 케이스 Active 체크 → 모달에 파싱 오류 사유가 보이고 체크 상태가 원복 (2) 같은 상태로 배치 1회 실행 → 통지 1회 · 로그에 실패한 키 전부 (케이스 수만큼 모달이 뜨지 않는다) (3) 기록 성공 경로의 통지 0
- 변경 범위: `view/DashDoeCasesWidget.cpp/.h` (`saveAllActiveStates` · `persistActiveFlag`), `model/DashAnalysisLaunchExecutor.cpp/.h` (`onCaseStatusUpdated`)
- 선행: PRE-15 (사유를 내주는 출력 인자) · LCH-07 (상태 기록이 executor 한 곳이어야 "런당 1회" 가 성립 — 없으면 러너 TU 6개에 같은 통지를 흩뿌려야 한다)
- 충돌: LCH-06 · LCH-08 · LCH-14 · LCH-16 · LCH-28 (같은 파일) · B2 교집합: DashAnalysisLaunchExecutor.cpp → PRJ-09 UIC-20 · DashDoeCasesWidget.cpp → LCH-09
- 흡수: #638-2 (LCH 호출부 몫 — PRE-15 인계) · LCH-c100
- 비고: PRE-15 가 반환형을 `bool` 유지 + 출력 인자로 둔 덕에 LCH 호출부 4곳이 무변경 컴파일되고 LCH-07 과도 순서가 무관하다 — 본 항목은 그 사유를 쓰는 쪽만 더한다. 모달을 케이스 단위로 두지 않는 이유는 스레드가 아니라 횟수다: `moveToThread` 0건이고 `DashJobRunner` 는 executor 의 자식이라 네 호출부가 모두 GUI 스레드지만(`DashAnalysisLaunchExecutor.cpp:33`), 상태 기록은 케이스×전이마다 일어나 모달이 배치를 막는다. 선례는 `snapshotDoeTable` 의 쓰기 실패(통지 1회 + `cancelAllRuns`). Direct Launch 는 `launcherConfigPath` 가 비어 기록 자체가 없으므로 대상이 아니다(`DashJobRunner.cpp:131-134` · `DashDoeCasesWidget.cpp:352-355`·`:388-391`)

## 대응표

| 원천 | 항목 | 비고 |
|---|---|---|
| #456 | LCH-20 (CLOSE) | 해소됨 — 코루틴·모핑 서비스 |
| #580 | LCH-02 | (4) Direct `taskCount==0` 은 PR #652 흡수, wbpj·fe-safe 5곳은 PR #651 흡수 |
| #438 | LCH-22 (CLOSE) | 추적 부모 |
| #439 | LCH-03 | |
| #440 | LCH-23 (CLOSE) | PR #652 흡수 |
| #441 | LCH-08 · LCH-09 | 증분화(재구축 억제) / 재시작 복구(DEC) |
| #442 | LCH-24 (CLOSE) | GitHub 닫힘 |
| #502 | LCH-21 (CLOSE) | 전제 소멸 + PM4 범위 밖 확정 |
| #604 | LCH-25 (CLOSE) · LCH-19 · LCH-14 | PR #652 In review. 잔여 DEC·죽은 코드 |
| #616 | LCH-26 (CLOSE) · LCH-29 (DEC) | PR #651 In review. 잔여는 하위 이슈. 결정표 wbpj 열 ↔ 매니페스트 "사장" 의 시간순 모순은 LCH-29 |
| #647 | LCH-31 (DEC) · LCH-11 (EXT) · LCH-10 | 계약 먼저, MBD 다음, GUI 축소 뒤 |
| #648 | LCH-18 (INV) · LCH-30 | 기대 1(실측) → LCH-18 · 기대 2(탐색 경로 사유 기록) → LCH-30. 출처 위치는 PR #651 |
| #639 | LCH-01 | |
| #646 | LCH-15 · LCH-16 · LCH-17 | 3건 분리 |
| #368 (접점 — 담당 PER) | LCH-33 · PRE-32 | DOE-16 출처·스냅샷 → Launcher 실행 검증·결과 XML → BLD-20 model_info 생산. 소비 RUN-34·OPT-26은 #685 |
| 269-1 (추가 원천) | LCH-02 · LCH-14 | "시그널이 빠진 실패 — 후속" + 후속 "dfsxml 의 불필요한 MAPDL 초기화" → LCH-02 · 죽은 코드 → LCH-14 |
| Project-Manifest-CAD-Path-Disposition (추가 원천 — CAD 인계) | LCH-29 (DEC) | "사장·불개입"(09-18) ↔ #616 결정표(10-02)·PR #651/#652 의 시간순 모순. 소비자 CAD-01 Phase 3·CAD-02·CAD-05·LCH-06·LCH-27·PRJ |
| PM4 G8·G9 (추가 원천) | LCH-21 · (#368 범위밖) | |
| DOE-D5 | 항목 없음 — 범위밖 → DOE | LCH 소비 3곳이 접점 (LCH-c61) |
| DOE-D2 | 항목 없음 — 범위밖 → DOE (LCH-c58) | |
| DOE-D26 | 항목 없음 — 범위밖 → DOE (LCH-c63) | |
| DOE-D12 | LCH-30 · LCH-18 | 출처 위치는 PR #651 흡수 · "판정이 파일 존재뿐" 잔여는 LCH-30 · 실측은 LCH-18 |
| DOE-D15 | LCH-04 | |
| DOE-D19 | 항목 없음 — 해소됨 (f14c5831 #559, LCH-c52) | |
| DOE-D25 | 항목 없음 — 범위밖 → DOE (접점 PRJ, LCH-c62) | |
| DOE-U2 | LCH-23 (CLOSE) | PR #652 흡수 |
| DOE-D17 | 항목 없음 — 해소됨 (c9c9dedb #403, LCH-c50) | |
| DOE-D18 | 항목 없음 — 해소됨 (f14c5831 #559, LCH-c51) | |
| DOE-D16 | LCH-05 | |
| DOE-D21 | LCH-06 | |
| DOE-D4 | 항목 없음 — 범위밖 → DOE (LCH-c60) | |
| DOE-D22 | 항목 없음 — 해소됨 (#617 뮤텍스 삭제, 콜백 직렬화, LCH-c46) | |
| DOE-D3 | 항목 없음 — 범위밖 → DOE (LCH-c59) | |
| DOE-D8 | 항목 없음 — 해소됨 (#617 `kKeyRole`, LCH-c47) | |
| DOE-D24 | 항목 없음 — 해소됨 (#617; PR #652 가 경로 삭제, LCH-c48) | |
| DOE-D6 | 항목 없음 — 해소됨 (`DashDoeSelection` 통일, LCH-c49) | |
| DOE-D10 | LCH-07 | |
| DOE-D13 | LCH-13 | |
| DOE-D23 | LCH-03 | |
| DOE-D1 | 항목 없음 — 범위밖 → DOE (LCH-c57) | |
| DOE-D7 | LCH-08 | |
| DOE-D9 | LCH-20 (CLOSE) | 해소됨 |
| DOE-D11 | LCH-12 | |
| DOE-D14 | 항목 없음 — 해소됨 (d8be33a4 #564, LCH-c45) | |
| DOE-U3 | 항목 없음 — 해소됨 (#617, LCH-c53) | |
| DOE-U4 | LCH-14 | 8건 중 7건 해소, `isFeSafePostEnabled` 1건 잔존 |
| DOE-U5 | LCH-14 | `connLog` 1건 잔존; `firstPartName` 해소; `.ui purposeCombo` → DOE |
| #444 (#441 하위) | LCH-32 (DEC) · LCH-08 | 비용 검증 → 기존 구조 개선 가능성 판단 → 필요한 경우에만 분리. ID 참조 전환과 독립 |
| #249 (범위 밖 절) | LCH-27 | ← CAD-c14(LCH-c64). #249 본체는 CAD |
| #463 (LCH 몫) | LCH-28 | ← EXE-c23(LCH-c92). 규약은 EXE-07 |
| #458-b (dfsxml 몫) | LCH-12 · LCH-10 | ← RUN-c10(LCH-c87) · EXE-c46(LCH-c97). #458 담당은 EXE |
| #474 (DOE-D8 축) | 항목 없음 — 해소됨 (#617, LCH-c47) | ← RUN-c13(LCH-c88). #474 본체는 RUN |
| DOE-c18 c22 c24 c31 c32 c35~c51 (DOE 이관 21행) | LCH-c65~c86 — 기존 항목(03·04·05·06·07·08·12·13·14·18·20·21·23·25)이 덮거나 해소됨 10 | c31(T27) 은 DOE-16 이 덮음 |
| EXE-c33 · EXE-c39 · EXE-c42 · EXE-c43 · EXE-c44 · UIC-c56 (LCH 몫) | LCH-03 · LCH-12 · LCH-05/06 · LCH-08/20/12 · LCH-23 · LCH-23 | LCH-c90 c91 c96 c93 c94 c95 |
| #638-2 (PRE 담당 — LCH 호출부 몫) | LCH-34 | ← PRE-c46(LCH-c100). 사유 생산은 PRE-15(`bool` + `QString* error` — LCH 호출부 4곳 무변경), 노출이 LCH 몫 |

## 요약

- 항목 34: PR 20 (S 15 · M 4 · L 1) · DEC 5 · INV 1 · EXT 1 · CLOSE 7 (이 중 In review 2건 #604·#616 은 PR 머지 조건부). B1 추가: LCH-27(CAD-c14) · LCH-28(#463 LCH 몫, EXE-07 뒤). C' 추가: LCH-29(wbpj 처분 DEC — C-2 ①) · LCH-30(fe-safe ODB 현행 케이스 한정, 검토 #5) · LCH-31(MBD 계약 DEC, 검토 #6) · LCH-32(#444 비용 검증 후 조건부 분리 DEC, 검토 #7). C' 2차 추가: LCH-33(Start 실제 입력 출처 검증 — PRE 검토 #2 인계) · LCH-34(기록 실패 사유 노출 — PRE-15 인계)
- 권장 순서: LCH-29·LCH-31 (DEC) · LCH-32 (비용 검증·저장 경계 결정) · LCH-11(EXT) 착수와 별개로 PR #651·#652 머지 → LCH-01·LCH-17·LCH-03·LCH-04 (S bug) → LCH-02 → LCH-06 → LCH-07 → LCH-08·LCH-13·LCH-14·LCH-15·LCH-16·LCH-30·LCH-34 → LCH-10 → LCH-05·LCH-12. LCH-33 은 DOE-16 뒤 (모듈 밖 선행)
