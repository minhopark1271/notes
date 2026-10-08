# 범위밖 이관 행 전수 (Phase A 산출, check_coverage.py 와 같은 규칙으로 추출)

> 대상 모듈이 둘 이상이거나 `?` 인 행은 B1 담당이 내용으로 판단한다.

## → ANA (9)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| CON-c13 | ResultsAnalyzer 가 `paramObj["checked"]` 를 읽는데 작성 키는 `"boolean"` 이라 조건 DV 가 변수 목록에 들어가지 않는다 | view/DashResultsAnalyzerWidget.cpp:onTargetDataChanged (`"checked"` 레포 유일 출현) · viewmodel/DashConditionParameterizationPresentationModel.cpp:buildDvConditionJson (`"boolean"`) | CON-D13 | 범위밖 | ANA 소관 — 읽는 쪽 1줄 수정. 작성 포맷은 바꾸지 않는다 |
| OPT-c30 | 설정 JSON 이 실데이터가 아닌데 플롯 spec 의 실재 게이트로 쓰인다 | model/DashOptimizer.cpp:requestPlot (:1173-1185) → model/analyzer/DashPlotSpecBuilder.cpp:build (:8-22 configFilePath 실재 검사, :108-111 데이터는 target_optimum_path) | OPT-D20 | 범위밖 | ANA 소관(SpecBuilder 소유). 실효 낮음 — optimum.json 은 Run(=saveSettings) 뒤에만 생긴다. ANA-c19 와 같은 함수 |
| PRJ-c39 | Results Analyzer ← 읽는 Set id 표시 | view/DashResultsAnalyzerWidget.cpp 스캔은 이름순 (ANA-D14) | #650 | 범위밖 | ANA |
| EXE-c46 | 접점 #458(Deferred) — FEM 파서 워커화 + dfsxml 1·2단계의 ProcessJob 수렴 | — | #458 | 범위밖 | → ANA(파서) · LCH(dfsxml). EXE 선행은 c03 레인 결정 |
| UIC-c31 | 플롯 확대 상한이 논리 px 기준 — `qBound(0.5, m_zoomFactor, 10.0)` 에 DPR 미반영, FBO 메모리 DPR² 배 (R2) | view/analyzer/DashAnalyzerHelpers.cpp:ZoomableScrollArea::wheelEvent · updateWidgetSize | R2 · #447 | 범위밖 | → ANA |
| UIC-c32 | PNG 저장에서 `grabFramebuffer()`(물리) 위에 자식 `render(&p, child->pos())`(논리) 합성 — `p.scale(dpr,dpr)` 없음 (R3) | view/analyzer/DashAnalyzerHelpers.cpp:ZoomableScrollArea::saveAsPng | R3 · #447 | 범위밖 | → ANA |
| UIC-c33 | 뷰포트 관행 둘 — `DashTimeSeriesGLWidget::resizeGL` 은 `glViewport(0,0,w,h)`, 나머지(`DashPlotWidgetBase`·Box·Scatter2D·ShapDependence)는 `calculateViewport`(논리×DPR, `static_cast<int>` 절삭) (R4) | view/analyzer/DashTimeSeriesWidget.cpp:resizeGL ; view/analyzer/DashAnalyzerHelpers.cpp:calculateViewport | R4 · #447 | 범위밖 | → ANA. Qt6 `resizeGL` 인자 단위 1회 실측 후 통일 또는 삭제 |
| UIC-c35 | `ZoomableScrollArea` 두 메서드의 크기 정책 불일치 — `updateWidgetSize` 는 min==max 고정, `autoFitToViewport` 는 min=원본·max=무제한 ; `onPlotWindowReady` 도 min==max (L3-3) | view/analyzer/DashAnalyzerHelpers.cpp:ZoomableScrollArea::updateWidgetSize · autoFitToViewport ; view/DashResultsAnalyzerWidget.cpp:onPlotWindowReady | L3-3 · #449 | 범위밖 | → ANA (파일 전부 ANA 소유). 줌 상태 관리 한 메서드로 통일 |
| UIC-c56 | 색인 "피드백 부재" ANA-D12 — Save 메뉴 `dynamic_cast` 실패 시 무반응 ; DOE-U2 — Direct Output Cases 표 상태 고정 ; CAD-D1·CAD-D9 — 스피너 비대칭 | — | ANA-D12 · DOE-U2 · CAD-D1 · CAD-D9 | 범위밖 | → ANA · LCH(PR #652 가 casesTable 신설) · CAD(CAD-07 흡수 완료). 통지 규칙(c37)의 "무반응 금지" 사례로 인용. 스피너 RAII 가드는 CAD-07 범위 |

## → BLD (7)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| LCH-c37 | T22 — Builder 핀·검증 + model_info 전사 | 위와 같음 | #368 Phase 3 | 범위밖 | → BLD |
| PRE-c54 | #643 추가 1 — Builder 다중 part 포맷과 호환 | model/builder | #643 | 범위밖 | BLD 접점 — 결정 입력으로만 |
| PRE-c59 | #411 결정 2 — 외부 학습 도구가 파일을 직접 읽는 계약 | 외부 도구 | #411 | 범위밖 | BLD·EXT |
| RUN-c14 | MCU 파일 행 [...] 람다의 행 번호 캡처 | BLD-D10 — view/DashModelBuilderMCUWidget | #474(BLD-D10 축) | 범위밖 | **BLD** — BLD-c18 이 흡수 |
| PRJ-c36 | Model Builder ← Analysis Launcher Preprocess XML id 핀 | model/DashModelBuilder.cpp — XML Set 단위화(#643) 선행 | #650 | 범위밖 | BLD (#643 후) |
| EXE-c37 | BLD-D13 MCU 가 쓰지 않는 1Hz 상태 폴링 타이머 | model/DashModelBuilder.cpp (status 폴링) | BLD-D13 · 215-2 Q5 | 범위밖 | → BLD. 215-2 Q5 의 "status 를 stdout 계약으로" 는 EXT(도구 측) |
| PER-c27 | 직쓰기 → 헬퍼 이행 — BLD: model/DashModelBuilder.cpp:onTrainingStartButtonClicked(설정 + model_info.json) · createModelInfoJson · saveDataLabelConfig · deleteTrainedModel(model_info.json) · model/DashModelBuilderMCU.cpp:onTrainingStartButtonClicked(2) · view/DashModelBuilderMCUWidget.cpp:onSetButtonClicked · onStartTrainingClicked — 9지점 | 좌동 | #479 · #478 · #480 | 범위밖 → BLD | 가장 많다. `model_info.json` 은 스탬프 전사 자리(#368 T22)라 c13 과 접점 |

## → CAD (10)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| RUN-c32 | `enqueueUpdatePrtGeometry` 가 요청 식별자를 돌려주지 않고 완료 신호 선택이 `m_batchMode` 에 달림 | controller/DashSolverNxCad.cpp:enqueueUpdatePrtGeometry (:149) · onCommandCompleted (:188, `m_batchMode` :203) · W (:262) 는 `updatePrtGeometryCompleted` 만 구독, 짝짓기 W:643 문자열 비교 | RUN-D15 | 범위밖 | **CAD** (`controller/DashSolverNxCad`). #452 기록 "`.prt` 경로 소속 — 비범위 기각". 호출자 4곳(JobRunner·Runner·Optimizer·CAD 위젯) |
| OPT-c08 | CAD 프리뷰 `.stp` 가 OCCT 뷰에서 `m_context->RemoveAll()` 로 같은 종류의 덮어쓰기 | view/DashMainWindow.cpp:previewStepFile (:3224) → view/DashOcctViewWidget.cpp:loadStepFile | #316 (범위 제외 명시) | 범위밖 | CAD 소관 |
| OPT-c10 | NX CAD 완료 통지가 요청과 짝지어지지 않는다 — `enqueueUpdatePrtGeometry` 무태그, 완료는 `m_batchMode` 전역 플래그로 갈려 `DashMainWindow` 람다가 받는다. 위젯은 부모 탐색으로 `DashMainWindow` 를 찾아 상태 애니메이션만 켠다 | view/DashOptimizerWidget.cpp:onPreviewButtonClicked (:1857-1863 부모 탐색, :1865 enqueue) · controller/DashSolverNxCad.h:68 `m_batchMode` · .cpp:203-206·221-224 · view/DashMainWindow.cpp:325-327 → onNxPreviewStepReady (:3247) | #457 · OPT-D19 · 접점 #249 | 범위밖 | CAD 소관 — #249 태그 왕복이 본체. 랜딩 후 위젯 구독 전환(부모 탐색 제거)이 OPT 후속이나 지금은 항목 없음 |
| OPT-c37 | NX CAD 파사드 요청 태그 왕복 + `m_batchMode` 제거 | controller/DashSolverNxCad.h:31 setBatchMode · :68 | 접점 #249 | 범위밖 | CAD 소관. OPT 는 c10 의 소비자 |
| REN-c17 | 덮어쓰기 ⑩ `loadStepFile` — OCCT `m_context->RemoveAll` | view/DashOcctViewWidget.cpp:loadStepFile | #318 (부류 2) | 범위밖 | 별도 OCCT 씬, 공유 VTK renderer 아님 → CAD. 소유권 모델 대상 아님 |
| EXE-c42 | 통지 미결합 7건 — 요청 식별자 왕복은 데몬 층이 이미 제공(`sendCommand(…, commandId)` 에코 · `currentCommandId()`); 미결합은 소비자 파사드 | controller/DashExtensionProcess.h:sendCommand/currentCommandId | CAD-D3 CAD-D7 CAD-D8 · DOE-D16 DOE-D21 · RUN-D15 · OPT-D19 | 범위밖 | CAD → CAD-01 · DOE-D16/D21 → LCH · RUN-D15 → RUN · OPT-D19 → OPT(#457). 공통 몫 없음 |
| PER-c23 | 직쓰기 → 헬퍼 이행 — CAD: viewmodel/DashGeometryParameterCADPresentationModel.cpp:saveDvGeometry (RMW) | 좌동 | #479 · #478 · #480 | 범위밖 → CAD | CAD-05(저장 의미 변경)와 같은 함수 — 순서 조율 |
| UIC-c30 | CAD 뷰가 논리 좌표 `event->x()/y()` 를 OCCT(물리 px 창)에 그대로 전달 — DPR≠1 에서 회전 피벗 어긋남 (R1) | view/DashOcctViewWidget.cpp:mousePressEvent (`StartRotation`) · mouseMoveEvent (`Rotation`·`Pan`) | R1 · #447 | 범위밖 | → CAD. Qt6 PassThrough 로 150% 모니터에서 **지금** 발현. 200% 실기 검증 필요 |
| UIC-c57 | 색인 "검증 부재" CAD-U5 · CON-U5 · OPT-U3 — `tests/` 참조 0 (테스트 부재, 입력 검증 아님) | — | CAD-U5 · CON-U5 · OPT-U3 | 범위밖 | → CAD · CON · OPT |
| DEV-c24 | #489 도메인 커버리지 공백 — CAD(`GeometryParameterCAD`·`NxCad` 참조 0, TestDashLogger 의 `NxCad` 는 모듈명 문자열) · OPT(`DashOptimizer` 0) · BLD(`DashModelBuilder` 0) · RUN(`DashModelRunner` 는 TestProcessRuntime 문자열만) · DOE(`DashDoeSampler` 0, `DashDoeSelection` 1) | tests/ 전체 grep · tests/CMakeLists.txt 소스 집계(model/preprocessor 15 · utils/log 9 · controller/async 5 · 모핑 controller 다수) | #489 · CAD-U5 · OPT-U3 | 범위밖 | → CAD(CAD-11 항목 존재) · OPT · BLD · RUN · DOE 각 모듈. DEV 는 인프라만 |

## → CON (2)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| PRJ-c19 | `DashFeConditionValueDelegate::m_dataModel` 은 2-인자 setModel 이 `if (!model) return;` 으로 빠져 QPointer 로 못 막는다 | view/DashConditionParameterizationWidget.cpp:setModel(QAbstractTableModel*,QString) (:305-313) | #551 별개 1 | 범위밖 | CON |
| PER-c24 | 직쓰기 → 헬퍼 이행 — CON: viewmodel/DashConditionParameterizationPresentationModel.cpp:saveDvCondition (RMW) | 좌동 | #479 · #478 · #480 | 범위밖 → CON | model/DashConditionParameterization.cpp:loadFromJson 의 재바인딩 write-back 은 이미 QSaveFile |

## → DEV (1)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| PRE-c58 | #411 결정 1 — vcpkg 구성에서 `vtkIOHDF` 가용 여부 | vcpkg 매니페스트·메타 저장소 | #411 | 범위밖 | DEV 접점 |

## → DOE (10)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| LCH-c35 | T27 — 조합 id 발급 + DOE Table 기록 | dev 에 `parameterizationId`·`DashPipelineStamp`·`derivedId` 0건. PR #530 이 `model/DashDoeConfigManager.cpp:saveResultsAsDvTable`·`saveResampledSamples`(DOE 모듈) 에 기록. #617 이후 런처가 실행 시점 DOE Table 스냅샷(`tableId`·`DOE configuration`) 을 `AnalysisLauncher_<Set>.json` 에 기록(`DashAnalysisLauncher.cpp:snapshotDoeTable`) | #368 Phase 1 | 범위밖 | → DOE (기록 지점이 샘플러 저장). PR #530 은 base `feat/reference-model-manifest`·구 파일명이라 **dev 리베이스 필요**. 기록 지점 재결정(DOE Table vs 런처 스냅샷 `tableId`) 은 스탬프 소유 모듈(PER) 의 DEC |
| LCH-c57 | `loadSettings` 진입 1회에 3번 | DOE Sampler 위젯 진입 경로 | DOE-D1 | 범위밖 | → DOE |
| LCH-c58 | Probabilistic Min/Max 되쓰기 없음 | DV 표·샘플링 | DOE-D2 | 범위밖 | → DOE |
| LCH-c59 | Purpose 문장 완전일치·이중 정의 | 샘플링 설정 | DOE-D3 | 범위밖 | → DOE |
| LCH-c60 | 워커가 GUI 소유 DV 모델 직접 읽기 | [Run] 샘플링 워커 | DOE-D4 | 범위밖 | → DOE |
| LCH-c61 | `samples[]` / `rawSamples[]` 정본 이중화 | 저장은 `DashDoeConfigManager::saveResultsAsDvTable`(DOE). 소비는 LCH — `DashAnalysisLaunchExecutor::runDoeAsync:195`(모핑에 `rawSamples`)·`DashJobRunnerAnsysJournal.cpp:journalLaunchConfig:113`(`rawSamples`)·치환 폴백(`values`) | DOE-D5 | 범위밖 | → DOE (저장 형식). 형식을 바꾸면 LCH 소비 3곳이 접점 |
| LCH-c62 | 릴리스 빌드에서 Resample variant Set 클릭이 무반응 | DOE Sampler Resample 위젯 DEV 가드·메인윈도 라우팅 | DOE-D25 | 범위밖 | → DOE (접점 PRJ) |
| LCH-c63 | 제약식 `v{n}` 토큰이 행 인덱스 유래 | 샘플링 설정 영속화 | DOE-D26 | 범위밖 | → DOE |
| PRJ-c09 | `Selected Design Variables` 가 Set 이름만 기록 — setId+name 병기(SI-4) 미적용 | model/DashDoeSelection.cpp:writeSelectedSets (:122-136 `{set: 이름}`), 소비 5곳 readSelectedSets (DashMorphingDoeExecutor.cpp:145 · DashAnalysisLaunchExecutor.cpp:297 · DashDoeConfigManager.cpp:84 · DashJobRunnerAnsysJournal.cpp:33 · DashDoeTableFile.cpp:174) | #562-3 · #443 SI-4 | 범위밖 | DOE. 발화 조건(rename) 은 Geometry 고정명·Condition 참조파일명 고정(DashProject.cpp:463)으로 소멸 — SI-4 규약 통일 여부는 DOE 결정 |
| PER-c25 | 직쓰기 → 헬퍼 이행 — DOE: model/DashDoeConfigManager.cpp:saveResultsAsDvTable · saveResampledSamples · model/DashDoeSampler.cpp:saveSettings (RMW · open 무검사) | 좌동 | #479 · #478 · #480 | 범위밖 → DOE | DOE Table 전체 재기록 2곳 — c15 run id 결정과 같은 함수 |

## → EXE (7)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| MOR-c10 | Follow-up ⑵ RW 실행 스레드 점유 경합 계측 (워커 RW 구간 동안 GUI 가 줄 섬) | `controller/DashRwDocument*`·`DashRwActor*` | #281-FU2 | 범위밖 | **EXE** — RW actor 계약. 모핑 쪽 입력은 불변 문서라 모핑 모듈 변경 없음 |
| CAD-c13 | `DashExtensionProcess` 에 per-command cancel / clearQueue 없음 | controller/DashExtensionProcess | #249(범위 밖 절) | 범위밖 | → EXE (전송 계층) |
| CAD-c31 | 성공·실패 판정이 `[FINISHED]` 전체 일치·`[ERROR]` 부분 일치 — 프로토콜 계약이 로그 포맷 | controller/DashExtensionProcess.cpp:handleDaemonLine | CAD-U4 | 범위밖 | → EXE (전송 계층 공통). 데몬 측 출력 규약은 c30 |
| CON-c17 | RW 문서의 엔트리 분해 중 Ansys flat 필드별 행·읽기전용 요약 행·Discrete/Categorical 분류가 테스트에 없다 — FakeRwModule 은 entries[] 만 흉내낸다 | controller/DashRwDocument.cpp:feConditionEntries · :rwPropertyDvKind · tests/rw/FakeRwModule.h | CON-U5 | 범위밖 | EXE 소관 (`controller/DashRwDocument*`) |
| RUN-c09 | 해석 deck(FEM) 파서를 워커로 — RW 액터 스레드 이주가 선행 | controller/DashRwActor.cpp:DashRwActor (:98 GUI 스레드 고정 assert) · :111 `assertActorThread`. 소비측 M:performMorphing (:2153) · W:loadSetsIntoPartCombo (:2202) 는 이미 `co_await` | #458-a · RUN-D5(deck 파서 축) | 범위밖 | **EXE** (`controller/DashRwActor*`). #458 코멘트(2026-09-22): PoC PR #529 닫힘(브랜치 `perf/458-rw-actor-worker` 참고용) · 실작업은 #544 로 이관(머지) · "해석 모델 적재는 여전히 GUI 스레드". RUN 쪽 잔여 없음 |
| ANA-c29 | `onPlotSpecReady` 의 `DashAsyncJobRunner::run` 3-람다 호출부 | view/DashResultsAnalyzerWidget.cpp:onPlotSpecReady (:3575-3589) | 접점 #553 | 범위밖 | EXE 소관 — #553 이 훅 구조를 바꾸면 이 호출부가 따라 바뀐다. ANA-15 와 같은 함수 |
| EXE-c48 | 접점 #454 #456 #457 #512 #513 — 모듈 펌핑 제거·워커 이관 | — | #454 #456 #457 #512 #513 | 범위밖 | 각 모듈. 공통 기반 소비 순서: EXE-01 → EXE-02/03 → EXE-04(레인) |

## → LCH (28)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| CAD-c14 | `startDirectAnsysJournalJobs` 가 다중 .wbpj 에서 `disconnect(nxCad, &loadPrtCompleted, this, nullptr)` 로 다른 잡의 구독까지 전량 해제 | model/DashJobRunnerAnsysJournal.cpp:startDirectAnsysJournalJobs(loadPrtCompleted 람다 내부) | #249(범위 밖 절) | 범위밖 | → LCH (Direct Launch, #604 PR #652 범위와 인접) |
| DOE-c18 | 설정 JSON 상태 기록 동시 쓰기 (Launcher 콜백) | model/preprocessor/DashAnalysisLauncherConfig.cpp 기록 경로 | DOE-D22 | 범위밖 | → LCH |
| DOE-c22 | 호출부 0 함수 (LCH 측) — DashJobRunner::createRunsFolders · isFeSafePostEnabled · DashDoeCasesWidget::getStatus/ErrorLogFromFileSystem · DashReferenceFileWidget::applySmartSelectionRules | — | DOE-U4 | 범위밖 | → LCH |
| DOE-c24 | `connLog` 빈 람다 · `firstPartName` 미사용 | model/DashJobRunnerAnsysJournal.cpp · controller/DashMorphingDoeExecutor.cpp | DOE-U5 | 범위밖 | → LCH |
| DOE-c31 | DOE Table 에 조합 id(`parameterizationId`) 기록 (T27) | PR #530 — DashDoeConfigManager::saveResultsAsDvTable·saveResampledSamples 에 stampParameterization | Project-Manifest-4 T27 · #368 | 범위밖 | → LCH #368 (In review). DashDoeConfigManager·DashDoeSelection 과 충돌 |
| DOE-c32 | 해석파일별 자동 반복 실행 — DOE 쪽 요구 없음(해석파일 집합은 DOE Table `columns[].{set,key}` 로 이미 기록) | model/DashDoeSelection.cpp:writeColumns | #502 (접점) | 범위밖 | → LCH (Deferred) |
| DOE-c35 | Direct variant 잔재 — DashDoeSamplerDirectWidget · DashDoeSampler 의 JobRunner·runDirectLauncherAsync·cancelAllRuns·onCaseStatusUpdated·m_expectedRunKeys | model/DashDoeSampler.h · view/DashDoeSamplerDirectWidget.* | DOE-U2 · DOE-D24 | 범위밖 | → LCH. PR #652 가 제거(U2 수정 명시). D24 는 dev 에서 JSON 기록 없음(onCaseStatusUpdated 는 로그만) — 해소 판정은 LCH |
| DOE-c36 | 케이스 1건마다 JSON 전문 재기록 → 표 전량 재구축 | — | DOE-D7 | 범위밖 | → LCH |
| DOE-c37 | 표 행 ↔ 케이스 결합이 Case Name 텍스트 파싱 | view/DashDoeCasesWidget.cpp | DOE-D8 | 범위밖 | → LCH |
| DOE-c38 | `runDoeAsync` 동기 실행 | — | DOE-D9 | 범위밖 | → LCH (#601 이후 DashAnalysisLaunchExecutor) |
| DOE-c39 | 말단 6경로 각자 구현 | model/DashJobRunner*.cpp | DOE-D10 | 범위밖 | → LCH |
| DOE-c40 | `processEvents` 동기 대기 | model/DashJobRunner*.cpp (DOE 파일 0곳) | DOE-D11 | 범위밖 | → LCH/EXE |
| DOE-c41 | FE-safe ODB 소스 판정 | model/DashJobRunnerFeSafe.cpp | DOE-D12 | 범위밖 | → LCH (PR #651 이 ODB 원본 복원) |
| DOE-c42 | 경로 조립기 2개 일치 강제 | model/DashJobRunner.cpp · controller/DashMorphingDoeExecutor.cpp | DOE-D13 | 범위밖 | → LCH |
| DOE-c43 | `msleep(1000)` 고정 지연 | model/DashJobRunnerAnsysMotion.cpp | DOE-D14 | 범위밖 | → LCH |
| DOE-c44 | motion-launcher 가 `.dfr` 을 만들어 낸다 | model/DashJobRunnerAnsysMotion.cpp | DOE-D15 | 범위밖 | → LCH |
| DOE-c45 | `.dfsxml` 완료 판정 주체 둘 | model/DashJobRunnerAnsysMotion.cpp | DOE-D16 | 범위밖 | → LCH |
| DOE-c46 | 모핑 배치의 핸들 DeepCopy | controller/DashMorphingDoeExecutor.cpp | DOE-D17 | 범위밖 | → LCH (MOR 접점, PR #654) |
| DOE-c47 | 공유 해석 컨텍스트 in-place 변이 | controller/DashMorphingDoeExecutor.cpp | DOE-D18 | 범위밖 | → LCH |
| DOE-c48 | condition DV 적용 실패 조용한 skip | controller/DashMorphingDoeExecutor.cpp | DOE-D19 | 범위밖 | → LCH |
| DOE-c49 | 종결 신호 두 갈래 | model/DashJobRunner*.cpp · model/DashAnalysisLaunchExecutor.cpp | DOE-D21 | 범위밖 | → LCH |
| DOE-c50 | 취소가 motion 큐를 비우지 않는다 | model/DashJobRunner.cpp:cancelAllRuns | DOE-D23 | 범위밖 | → LCH |
| DOE-c51 | `visibleParamIndices` 계산만 됨 | view/DashDoeCasesWidget.cpp | DOE-U3 | 범위밖 | → LCH |
| RUN-c10 | dfsxml 처리 1·2단계를 ProcessJob 흐름으로 수렴 | model/DashJobRunner 의 .dfsxml 갈래 — #452 가 펌핑 15곳 보존(`generateInputCases` 8 · `waitForVtuFileComplete` 5 · `runMotionWriter` 2) | #458-b | 범위밖 | **LCH**. #458 코멘트 "ANSYS Motion 은 범위 외" |
| RUN-c13 | DOE 표 Case Name 표시 텍스트 파싱 결합 | DOE-D8 — Model Runner 파일 밖 | #474(DOE-D8 축) | 범위밖 | **LCH** (실행 표) |
| PRJ-c07 | Set 기록 파일을 변경 빈도 단위로 분할 — AnalysisLauncher_{Set}.json 에 설정·DOE Table 스냅샷·`Launcher Cases` 상태가 동거, 상태 1건에 전문 재기록 | model/preprocessor/DashAnalysisLauncherConfig.cpp:writeCaseStatus (:133), .h:28-52 포맷 주석; 워처는 view/DashDoeCasesWidget.cpp (QFileSystemWatcher 4) | #444 · DOE-D7 | 범위밖 | LCH — #441(상태 기록 증분화)과 같은 파일·같은 설계 축. PRJ 몫 없음 |
| EXE-c33 | DOE-D23 `cancelAllRuns` 가 진행 중 프로세스만 죽이고 motion 큐를 안 비운다 | model/DashJobRunner.cpp:cancelAllRuns (`m_motionProcesses` 순회) | DOE-D23 | 범위밖 | → LCH (dfsxml 보존 경로) |
| EXE-c39 | DOE-D14 `msleep(1000)` 이 끝난 동기 호출 뒤 | model/DashJobRunnerAnsysMotion.cpp (`QThread::msleep(100)` 3곳 포함) | DOE-D14 | 범위밖 | → LCH 보존 경로 |

## → MOR (7)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| ANA-c08 | 죽은 `#include <Eigen/Dense>` | controller/DashHandlePickingInteraction.cpp:2 | #305 | 범위밖 | MOR 소관 |
| PRJ-c48 | DashMeshQualityDialog::setResults `processEvents` 1곳 (:164) | view/dialog/DashMeshQualityDialog.cpp | #455 신규 | 범위밖 | MOR (메시 QC 다이얼로그) |
| REN-c31 | #322 GizmoGroup 병렬 컨테이너 · #430 DashHandleData | libs/DashGizmo · controller/DashHandle* | #322 · #430 (접점) | 범위밖 | → MOR 담당. 렌더링 매니저 접점 없음 |
| REN-c33 | MOR-D2 — geometry 부재 시 `getBaseGeometryActor()` 로 대체 · RUN-D14 renderer 부재 반환 · RUN-D25 마지막 1건만 자동 렌더 | controller/DashRenderingManager.cpp:getBaseGeometryActor (getter 자체는 정상) | MOR-D2 · RUN-D14 · RUN-D25 | 범위밖 | → MOR · RUN. 매니저 API 결함 아님 |
| EXE-c47 | 접점 #281 — MorphingGate·전용 RW 세션. 본문의 `DashRwSession::MutationScope`·`isMutating` 은 dev 에 이미 없다(심볼 0) | `git grep` DashRwSession · MutationScope · isMutating 각 0건 | #281 | 범위밖 | → MOR. EXE 몫은 c11(액터 스레드) 결정과의 정합 |
| PER-c22 | 직쓰기 → 공용 헬퍼 이행 (원자성·버전 키·왕복 테스트 동반) — MOR: viewmodel/DashGeometryParameterPresentationModel.cpp:saveMorphingSettings · view/DashGeometryParameterWidget.cpp:setupMorphingTab · model/DashDesignVariableModel.cpp:saveToJsonFiles | 좌표 좌동 | #479 · #478 · #480 | 범위밖 → MOR | `DashDesignVariableModel` 은 CON 과 공유 — Phase B 에서 주 모듈 확정 |
| UIC-c58 | 색인 "위치·순서 결합" 9건 중 표 행 캡처는 BLD-D10(c51)·RUN-D22(c53) 2건 — 나머지 MOR-D14 · CAD-D6 · BLD-D5 · RUN-D8 · RUN-D25 · ANA-D1 · OPT-D15 는 각 모듈의 인덱스·순서 계약 | — | 좌 7건 | 범위밖 | → MOR · CAD · BLD · RUN · ANA · OPT |

## → OPT (12)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| MOR-c06 | Phase D — Optimizer 프리뷰 모핑 워커화. 모핑 자체는 `performMorphingAndExport` 가 `DashMorphingService::background()` 풀에서 돌고 호출부가 `co_await` 한다. **잔여**: 루프 안 `processEvents` 2곳(이제 불필요한 펌핑)과 모핑 중 Preview 버튼 사전 비활성 | `view/DashOptimizerWidget.cpp:onPreviewButtonClicked:1498` — `:1698`·`:1724` `QCoreApplication::processEvents()`. `model/DashOptimizer.cpp:performMorphing` 코루틴 | #281-D | 범위밖 | **OPT** (`view/DashOptimizerWidget.cpp`·`model/DashOptimizer.cpp`). view/ 전체 pE 14곳 중 Optimizer 2곳 |
| CAD-c37 | OPT-D19(Optimizer 완료 수신처가 MainWindow) 는 #249 태그 왕복 위에 얹음 | view/DashOptimizerWidget.cpp:onPreviewButtonClicked 말미 주석 | #457(접점) | 범위밖 | → OPT. 선행 CAD-01 |
| RUN-c19 | Optimizer 에 같은 FE Validation 버튼 | view/DashOptimizerWidget.cpp — `validationTab` (:220) 은 다른 기능 | #653(OPT 축) | 범위밖 | **OPT**. RUN-c18 과 같은 prefill 진입점 공용 |
| PRJ-c38 | Optimizer ← Model Builder 모델 id · Condition·Geometry Set 핀 | view/DashOptimizerWidget.h:127 폴더 콤보 | #650 | 범위밖 | OPT |
| PRJ-c58 | Set 삭제 후 Optimizer setModel(nullptr) 이 표·enabled 를 그대로 둔다 | view/DashOptimizerWidget.cpp:setModel (:119-136 null 분기 정리 0) | OPT-D2 | 범위밖 | OPT — c21 계약의 사례 |
| REN-c19 | 덮어쓰기 ⑫ Optimizer Preview — `renderer->GetActors()` 전량 `RemoveActor` 후 레이어 3개 clear · `setDisplayedContext(출력 deck)` | view/DashOptimizerWidget.cpp:onPreviewButtonClicked | #318 (부류 3) · #316 · OPT-D18 | 범위밖 | → OPT (#316 담당, 본 모듈 인수=숨김 항목의 선행) |
| REN-c30 | #316 Optimizer Preview 비파괴 전환 | view/DashOptimizerWidget.cpp:onPreviewButtonClicked | #316 (접점) | 범위밖 | → OPT. REN 인수=숨김 항목의 선행 파일럿 |
| REN-c32 | OPT-D18 — Render Preview 가 핸들 배열·renderer actor·active context 를 갈아끼우고 복구 없음 | view/DashOptimizerWidget.cpp:onPreviewButtonClicked | OPT-D18 | 범위밖 | → OPT (#316 과 동일 지점) |
| PER-c29 | 직쓰기 → 헬퍼 이행 — OPT: model/DashOptimizer.cpp:saveSettings (RMW) | 좌동 | #479 · #478 · #480 | 범위밖 → OPT | OPT-D12(saveSettings 호출처 1곳)와 같은 함수 |
| UIC-c34 | 수렴 히스토리 PNG 를 논리 800×600 으로 `scaled` — DPR≠1 에서 흐림, `setDevicePixelRatio` 없음 (R5) | view/DashOptimizerWidget.cpp:onOptimizationSucceeded | R5 · #447 | 범위밖 | → OPT |
| UIC-c55 | 색인 "피드백 부재" OPT-D13 — 중복 실행 방지가 모델 가드뿐, 버튼 열림 | — | OPT-D13 | 범위밖 | → OPT. "실행 중 버튼 비활성" 은 EXE 진행 표시 표준 소관, 공통 헬퍼 몫 아님 |
| DEV-c30 | #483 Optimizer 제약 표 초기 행 `"r1 <= 163.23"`(회색)·추가 행 기본값 `"r9 <= 153755.61"` 이 샘플 값이고 `collectConstraintRows` 가 행 0 을 그대로 수집 | view/DashOptimizerWidget.cpp:configureOptimizationSettingsGroup(452-455) · :657-660 · collectConstraintRows(2391-2398) | #483 · W2 | 범위밖 | → OPT(샘플 행이 저장 설정에 들어가는지는 OPT 판정) |

## → PER (2)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| MOR-c46 | 설정 초기값 전수 조사(`active` 18곳 등 키 14개·`.ui` 6개·`QSettings` 49곳)와 정책 문서화(정책 default · escape · sentinel · 소유자 · 진입점) | 앱 전반 | #423 1·2 단계 | 범위밖 | **PER** (JSON 읽기 헬퍼·저장 포맷 규칙). 모핑 반경은 c45 가 사례 적용 |
| PRE-c60 | #411 결정 3 — 저장 포맷 버전 키(A3/N9) 없이 포맷을 바꾸면 구 산출물 침묵 오독 | 결과 XML·설정 JSON 에 버전 키 0건 | #411 | 범위밖 | PER |

## → PRE (4)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| LCH-c36 | T21 — Preprocessor 핀·검증 + dataset XML 스탬프 | 위와 같음 | #368 Phase 2 | 범위밖 | → PRE |
| ANA-c30 | DOE 산출 XML 포맷 교체 검토 | model/analyzer/DashXmlParser.cpp 가 유일 소비 파서 | 접점 #411 | 범위밖 | PRE 소관 검토 티켓. 결론이 교체면 ANA 파서 항목이 생긴다 |
| PER-c19 | #638 — `readRoot` 가 0바이트 파일을 파싱 실패로 보고 저장 거절(증상 1)·사유 미반환(증상 2) 현행 유효. 수정 자체는 PRE 파일, 공통 규칙은 c06 | model/preprocessor/DashAnalysisLauncherConfig.cpp:readRoot(:12-40)·writeRoot(:42-62) · tests/TestAnalysisLauncherConfig.cpp:invalidExistingConfigIsPreserved | #638 | 범위밖 → PRE | PRE 항목의 선행에 PER 헬퍼(규칙 c06)를 두면 `readRoot`/`writeRoot` 가 헬퍼 호출 2줄로 준다 |
| PER-c26 | 직쓰기 → 헬퍼 이행 — PRE: viewmodel/DashAnalysisLauncherPresentationModel.cpp:saveOutputResponse (RMW) | 좌동 | #479 · #478 · #480 | 범위밖 → PRE | `DashAnalysisLauncherConfig` 는 이미 QSaveFile — 헬퍼 치환은 #638 항목(c19) |

## → PRJ (4)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| CON-c19 | Add File 복사 실패 시 기존 파일·원장 항목·Set 이 함께 사라진다 | view/DashMainWindow.cpp:copyFileIntoProject 이후 원장·Set 생성 경로 | #645 | 범위밖 | PRJ 소관 (Project Assets·원장) |
| PER-c18 | #444 Set 기록 파일을 변경 빈도 단위로 분할 — 저장 포맷 변경이지만 Set 수명·파일 배치가 PRJ 소관 | relations.json 443 → 444 | #443 · #444 | 범위밖 → PRJ | 분할 포맷은 c11 규약(버전 키)을 따른다 — PRJ 항목의 선행에 PER 버전 키 DEC 를 적는 것을 제안 |
| PER-c20 | SI-6a 산출물 폴더 식별(폴더명 `{Module}_{Set}` 유지 · setId 색인 역조회 · rename 시 폴더 동반 개명 · 삭제 시 폴더 동반 삭제) — 마스터 후속작업 14, G9 머지 후 #443 하위 발행 예정 | Set-Identity SI-6a · model/DashProject.cpp:renameSet(:1700)·deleteSet(:1117) | Set-Identity SI-6a | 범위밖 → PRJ | PER 항목 없음 |
| PER-c30 | 직쓰기 → 헬퍼 이행 — PRJ: model/DashProject.cpp:createModuleJsonFile(setId 발급 포함 · write 무검사) · writeSetReferenceModel (RMW) | 좌동 | #479 · #478 · #480 | 범위밖 → PRJ | — |

## → REN (2)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| PRJ-c46 | DashViewOptionsWidget::onColorBarChanged `processEvents` 2곳 (:82·:94, adjustSize 전 flush) | view/overlay/DashViewOptionsWidget.cpp | #455 | 범위밖 | REN (1-1 표 배정) |
| EXE-c41 | 스레드 경계 3건 — CON-D2(레지스트리 로드가 뮤텍스 밖) · DOE-D4(워커가 GUI 소유 모델 직접 읽기 — 현행은 `m_setIdsSnapshot` 등 스냅샷을 뜸, 부분 해소) · DOE-D22(설정 JSON RMW 8곳 중 뮤텍스 1곳) | controller/DashAnalysisModelContextRegistry.cpp:load · model/DashDoeSampler.cpp:onRunButtonClicked (스냅샷 주석) · model/DashJobRunner* 설정 쓰기 | CON-D2 · DOE-D4 · DOE-D22 · 203-2 D5 | 범위밖 | CON-D2 → REN · DOE-D4 → DOE · DOE-D22 → LCH/PER. 공통 몫(규칙) 은 c06 문서 |

## → RUN (8)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| LCH-c38 | T23 — Runner·Optimizer 핀·검증 | 위와 같음 | #368 Phase 4 | 범위밖 | → RUN · OPT |
| PRJ-c37 | Model Runner ← Model Builder 모델 id 핀 | model/DashModelRunner.cpp:497 폴더명 보유, 모델 id 비교 0 | #650 | 범위밖 | RUN (c04 와 같은 자리) |
| EXE-c35 | RUN-D32 민감도 실패 4경로가 `m_pendingCommand` 를 안 지움 | model/DashModelRunner.cpp (sensitivityDaemon 소비자) | RUN-D32 | 범위밖 | → RUN. 공통 몫 없음 — `currentCommandId()` 상관 수단은 이미 있다 |
| EXE-c36 | RUN-D3 `daemonReady` 유실 보정 3벌 중복 | #437(0894cac9) `daemonReadyChanged(bool)` + `isDaemonReady()` + `observeDaemonReady()` (model/DashModelRunner.cpp:observeDaemonReady · DashModelBuilderMCU.cpp:observeDaemonReady) | RUN-D3 | 범위밖 | → RUN 이 해소 여부 확인 (공통 계약은 #437 로 닫힘) |
| EXE-c38 | RUN-D27 1D 결과 대기가 고정 500ms 뒤 `lastModified` 최대 CSV 선택 | model/DashModelRunner.cpp (예측 완료 처리) | RUN-D27 | 범위밖 | → RUN. 공통 몫은 c29 계약("산출물 flush 가 종결 출력보다 앞") |
| PER-c16 | #473 산출물 항목 식별자·채번 영속화(#475 RUN-D34)·접두사 삭제(#477) — RUN 소관. PER 접점은 채번 영속 자리(설정 JSON 키)가 공용 포맷 규약(c11)을 따르는 것뿐 | relations.json 473 → {474, 475, 477} · RUN 담당 | #473 | 범위밖 → RUN | 항목 없음 |
| PER-c28 | 직쓰기 → 헬퍼 이행 — RUN: model/DashModelRunner.cpp:writeConfigFile (RMW) | 좌동 | #479 · #478 · #480 | 범위밖 → RUN | — |
| UIC-c40 | #370 부수 — Condition 브랜치가 `generateDatFile` 반환값을 무시하고 항상 "Input file generated." 표시 | view/DashModelRunnerWidget.cpp (`stopGenerateStatusAnimation("Input file generated.")` 2곳) | #370(접점) | 범위밖 | → RUN. 통지 규칙의 "성공 통지는 결과를 확인한 뒤" 예시로만 인용 |

## → UIC (5)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| CAD-c20 | `.prt` 진입 초입 `processEvents(ExcludeUserInputEvents)` — 큐된 슬롯·타이머 실행으로 데몬 stdout 처리 재진입 가능 | view/DashMainWindow.cpp:openFileInViewport(`startProjectLoadStatusAnimation` 직후, 전 확장자 공통) | CAD-D2 | 범위밖 | → UIC #455 ("view/DashMainWindow.cpp 1곳 — onProjectFileLoadClicked 로드 스피너 표시" 와 같은 지점). CAD 파일 내 processEvents 0건 |
| DOE-c26 | 통지 — 모델 계층 `QMessageBox` 5곳(DashDoeSampler.cpp: onRunButtonClicked 2 · checkVariableTypesForMethod 1 · onAnalysisCompleted 2), 뷰 24곳(Widget 17 · Resample 3 · Base 4), DashNotify 2곳 | grep `QMessageBox::` | 코드 실측 · #482 | 범위밖 | → UIC #482 (통지 래퍼 표준화). 건수만 기록 |
| DOE-c27 | 싱글턴 직후 null 가드 — DashDoeSampler.cpp 27 · Widget 14 · Resample 2 · Base 1 | grep `if (!prjMgr)` 등 | 코드 실측 · #508 | 범위밖 | → UIC #508 |
| BLD-c31 | `QMessageBox::` 직접 호출 — W 9 · MW 14 · Base 0 = 23곳 (DashNotify 와 혼용) | view/DashModelBuilderWidget.cpp · view/DashModelBuilderMCUWidget.cpp (grep -c). `processEvents` 는 BLD 5파일 0곳 | Code-Map-User-Flow-Model-Builder 5절 | 범위밖 | UIC 통지 래퍼 항목(#447~#450)에 건수 제공 |
| RUN-c37 | `[Preview]` 람다가 캡처한 `row` 를 쓴다 | W:createFileTableRow (:2005 `[this, row, filePath]`) → onFilePreviewClicked (:1407) → performPreviewLogic (:1448) — `row` 는 재귀(:1465)로 넘기기만 하고 미사용, 경로는 `filePath` 캡처 | RUN-D22 | 범위밖 | **UIC** — #514 Phase 4 "죽은 인자 제거". 실해 없음(잠복) |

## → ? (2)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| PRE-c23 | #494 선행 — 도메인까지 넘기려면 Preprocessor `3ff07ff` 머지 필요 | 외부 저장소(DashOpti_Preprocessor) | #494 | 범위밖 | EXT. 시간 선택자만 넘기면 선행 불요 — c14 는 진행 가능 |
| EXE-c45 | ANSYS·Abaqus·fe-safe 실행은 외부 라이브러리 cae-launcher(DashOpti_CAELauncher, vcpkg) 가 맡는다 — 프로세스 안전핀 4축의 그쪽 몫은 이 저장소 밖 | CMakeLists.txt:42 · model/DashJobRunnerCae.h (공용 헬퍼 3개) · model/DashJobRunner.cpp:~DashJobRunner (`m_*Launcher.reset()` = task 강제 종료 + worker join) | #465 | 범위밖 | EXT. GUI 측 접점은 TerminalState 번역(`caeTerminalStatusText`) 뿐 |

## → BLD/ANA (1)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| PRE-c56 | #643 추가 3 — HDF5 전환 시 `DashXmlParser`(캐시 #515) 도 전환 | model/analyzer/DashXmlParser | #643 · #411 | 범위밖 | ANA·BLD. 포맷 결정 뒤 |

## → CAD/LCH/ANA/OPT (1)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| EXE-c44 | 피드백 부재 중 실행 관련 — OPT-D11(통지 미결합) · OPT-D13(버튼 열림) · DOE-U2(케이스 표 고정) · CAD-D1(해소됨, CAD 판정)·CAD-D9(스피너 비대칭, #464) · ANA-D12(메뉴) | — | OPT-D11 OPT-D13 DOE-U2 CAD-D1 CAD-D9 ANA-D12 | 범위밖 | 규칙·표준 몫은 c24·c22. 수정은 OPT · LCH · CAD(#464) · ANA |

## → CAD/PRJ (1)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| BLD-c01 | Set 의 Sim/MCU 갈림 근거가 트리 `UserRole+2` · JSON `variant` · 이름 `-MCU` 접미사 3벌이고 읽는 곳마다 기준이 다르다 | model/DashProject.cpp:addModelBuilder·addModelBuilderMCU(UserRole+2 기록) · :detectBuilderVariant(JSON→접미사 폴백, 호출처 restoreExistingModules) · :deleteSet·renameSet·updateModelSetName(접미사만) · view/DashMainWindow.cpp:handleModelBuilderSelection(UserRole+2) · :clearModuleWidget 계열(getModelBuildersMCU 목록 소속) · :displayWidgetForNewSet(variant 인자) | BLD-D1 | 범위밖 | 변경 파일이 전부 PRJ(DashProject · DashMainWindow). ModelRunner(`-MCU`)·Geometry(`-CAD`)·DoeSampler 도 같은 3벌 구조 — PRJ 횡단 항목 "Set variant 정본 단일화" 로 이관 |

## → MOR/CAD/CON/LCH/PRE/PRJ (1)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| EXE-c43 | 동기 실행·재진입 모듈 고유 10건 | — | MOR-D7 MOR-D8 · CAD-D2 · CON-D9 CON-D11 · DOE-D7 DOE-D9 DOE-D11 · PRE-D3 PRE-D9 | 범위밖 | MOR(#512) · PRJ(#455, CAD-D2) · CON · LCH(#456) · PRE(#454). 공통 몫은 c03(레인)·c22(가드 표준) |

## → MOR/CAD/LCH/PRE/BLD/RUN/ANA/OPT (1)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| EXE-c23 | #463 모듈별 진행바·취소·가드 확산 | 각 모듈 위젯 | #463 | 범위밖 | LCH(#456) · PRE(#454) · OPT(#457) · MOR(#512) · RUN(#513) · BLD · CAD(#464) · ANA. EXE 는 규약(EXE-07)·헬퍼(EXE-09)·취소(EXE-02) 만 |

## → MOR/RUN/OPT (1)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| PER-c05 | 왕복 단절 28건 — 모듈별 저장·로드 결함. 공통 기제(헬퍼·왕복 게이트)는 PER, 각 결함 수정은 모듈 소관 | 부록 A 표 (ID · 모듈 · 타 모듈 claims 현황) | #478 · Cross-Module-Defect-Index "2 왕복 단절" | 범위밖 → 각 모듈 (부록 A) | Phase B 배분 근거. 타 모듈 claims 에 이미 21건 등재(유효 15 · 해소됨 2 · 범위밖 4), MOR 3·RUN 5·OPT 5 는 해당 모듈 미작성 |

## → RUN/OPT (1)

| CID | 현상 / 목표 | 근거 | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| PRJ-c04 | Set 참조를 보관하는 자리가 이름을 들고 있다 — Runner `modelBuilderFolder` = `"ModelBuilder_%1".arg(setName)`, Optimizer 폴더 콤보 | model/DashModelRunner.cpp:497; view/DashOptimizerWidget.h:127 `m_modelBuilderFolderCombo` | #443 SI-6a ② | 범위밖 | RUN · OPT |
