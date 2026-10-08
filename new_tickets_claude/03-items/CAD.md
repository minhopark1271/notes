# CAD 작업 목록

> dev @ b08a91b3. 열린 PR 7건(#658 #656 #655 #654 #652 #651 · #530 은 재업로드 노선이라 머지 대기 대상이 아니다 — 05-final/decisions.md 2 · 10 항) 중 CAD 관련 파일을 만지는 것 4건: #651(#616 — DashJobRunner.{h,cpp} · DashJobRunnerAnsysJournal.cpp · DashMainWindow.cpp · tests/CMakeLists.txt) · #652(#604 — DashJobRunner.h · DashMainWindow.{h,cpp} · DashManager.{h,cpp} · tests/CMakeLists.txt) · #654(#332 — DashMainWindow.cpp · DashManager.cpp · tests/CMakeLists.txt) · #655(#430 · #322 — DashMainWindow.cpp +1/-10 · tests/CMakeLists.txt +18/-18). #658 · #656 은 CAD 접촉 0. #249 자체의 열린 PR 은 없다.
> #655 의 `DashMainWindow.cpp` hunk 3곳은 전부 모핑 블록(`handleSubItemSelection` · `initializeMorphingController` · `setupMorphingBar`)이라 CAD 항목의 **선행**은 아니다 — 단순 충돌은 D-1 의 `build_deps.py --apply` 가 파일 교집합으로 기입한다.

### CAD-01 · NX 파사드 완료 통지를 요청 태그 왕복 대칭 4종으로 일반화하고 m_batchMode 를 제거한다
- 종류: PR | 규모: M | 태그: B, E · refactor
- 목표: `enqueueLoadPrt`/`enqueueUpdatePrtGeometry` 가 `NxCadRequester {Interactive, Batch}`(클래스 내부 `Q_ENUM`) 를 받아 `commandId` 를 `"<verb>|<tag>|<stp>"` 로 싣고, 완료·실패를 `loadPrtCompleted/Failed` · `updatePrtGeometryCompleted/Failed(requester, stpPath[, message])` 대칭 4종으로 항상 방출한다. `nxCadParametersJson` 에도 `currentCommandId()` 에서 분해한 태그를 얹는다. 방출 억제(`m_batchMode`·`setBatchMode`·배치 전용 시그널 2종·`emitFailure`)는 삭제하고 판단은 구독자 필터로 옮긴다. 태그·경로를 얻을 수 없는 통지(빈 `outputStpPath`, 진행 커맨드 없는 JSON)는 귀속 없이 로그만 남긴다.
- 완료 기준: 1~3 은 **NX 불요**(빌드 · grep · CAD-11 TU), 4~5 는 **NX 게이트**(실기 수동)
  1. `git grep -E "m_batchMode|setBatchMode|updatePrtGeometryBatch|batchCompleted|batchFailed|emitFailure" -- '*.cpp' '*.h'` 0건 (주석 포함)
  2. 파사드에 모드 의존 방출 분기 0 · `commandId` 의 경로 필드를 버리는 지점 0 · `DashMainWindow` 에 `updatePrtGeometryFailed` 구독 존재 · 요청 6곳 각각의 완료·실패가 태그·경로로 짝지어진다 (RUN-D15 · OPT-D19)
  3. `onStpCaseFailed` 가 `onStpCaseCompleted` 와 같은 가드를 쓴다 — `requester == Batch && stpPath == m_stpBatch.current.stpPath` · 데몬 사망 1회당 Failed 케이스 1건(`drainCommands` 가 올리는 in-flight+큐 N건 중 현행 케이스 것만 계상) — CAD-11 TU + `tests/daemon_stub.cpp` 로 확인 (#249 "구독자 필터 규약" · AC 8항)
  4. (NX 게이트) DOE wbpj 배치 1회에서 콘솔 `Cannot queue arguments` 0건 · 케이스별 모달·미리보기 0회 — LCH-29 가 **제거**면 이 기준과 Phase 3 이 함께 소멸
  5. (NX 게이트) NX 환경 수동 회귀 5케이스(기하 파라미터 미리보기 · Optimizer 미리보기 · Model Runner 파일테이블 · load/update 실패 모달 각 1회 · loadPrt 후 파라미터 표 갱신) 회귀 없음
- 변경 범위: controller/DashSolverNxCad.h · controller/DashSolverNxCad.cpp · view/DashGeometryParameterCADWidget.cpp · view/DashMainWindow.cpp · view/DashModelRunnerWidget.cpp · view/DashOptimizerWidget.cpp · model/DashJobRunner.h · model/DashJobRunnerAnsysJournal.cpp
- 선행: LCH-29 (wbpj 경로 처분 — Phase 3 의 존폐를 정한다)
- 충돌: PR #651 · #652 · #654 · #655(DashMainWindow.cpp · DashJobRunner.h · DashJobRunnerAnsysJournal.cpp) · CAD-02 · CAD-06 · CAD-08(DashSolverNxCad) · CAD-07(DashMainWindow 구독 블록) · LCH-06 · LCH-07 · LCH-14 · LCH-27 (DashJobRunnerAnsysJournal) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashGeometryParameterCADWidget.cpp → 공유 10건(deps.md 5절) · DashJobRunner.h → LCH-02 LCH-10 LCH-12 · DashJobRunnerAnsysJournal.cpp → UIC-19 · DashSolverNxCad.cpp → CAD-03 CAD-15 · DashSolverNxCad.h → CAD-03
- 흡수: #249 · CAD-D3 · CAD-D7 · CAD-D8 · OPT-D19(본체) · #457(D19 태그 왕복 몫) · RUN-D15 · CAD-c01, c02, c03, c04, c05, c06, c07, c08, c09, c16, c38, c53 · CAD-c35(`JobType` · DashSolverNxCad.h:73-74 주석 몫 — 나머지 4건은 CAD-06) · CAD-c39, c41, c42, c44 (← RUN-c32, OPT-c10, OPT-c37, EXE-c42)
- 비고: 이슈 본문 설계(방안 A · 대칭 4종 · `|` 구분자 · `Q_ENUM`)를 그대로 쓴다. 분할 불가 — 시그니처 변경이 구독 9곳을 동시에 깨므로 한 커밋. 파일 8개지만 순변경 ~100줄, 비용의 대부분은 NX 수동 회귀. **LCH-29 조건** — `제거` 면 Phase 3(오케스트레이터 재배선)·`Batch` 태그·완료 기준 3·4 가 소멸하고 본 항목은 대화형 4종 대칭 + 태그(S) 로 줄어든다. 매니페스트가 "사장 예정·불개입" 으로 적은 경로의 수정분을 그만큼 뺀다. `현행 유지`·`동결` 이면 지금 범위 그대로(M). **소비자(랜딩 뒤 후속)** — OPT-D19(#457) 의 태그 왕복 몫은 본 항목이 흡수하고 Optimizer 위젯 측 소비자 전환(자기 요청 구독 · 부모 탐색 제거)은 OPT-22 · RUN-09 는 ModelRunner 의 `stpPath` 문자열 비교를 태그 비교로 바꾸는 몫만 본 항목 뒤에 둔다(RUN-09 본문이 괄호 조건으로 적어 파서가 선행으로 읽지 않는다). CAD-06 의 `JobType`·헤더 주석 2곳은 본 항목이 같은 블록을 고치므로 여기서 함께 지운다(검토 #16). CAD-D3 의 "표가 먼저, 형상이 나중" 순서 보장은 태그 상관까지만 — 합류점 설계는 별도 결정으로 남긴다.

### CAD-02 · 파사드 상태의 수명을 명령 경계에 맞춘다 — prt 출처 배치 오염 · JSON 버퍼
- 종류: PR | 규모: S | 태그: A, C · bug
- 목표: `enqueueUpdatePrtGeometry` 가 `m_originalPrtPath` 를 덮어쓰지 않게 해 "마지막에 Load 한 .prt" 의미를 `enqueueLoadPrt` 에만 둔다 — 호출 3곳(배치 `startNextStpCase` · Optimizer `onPreviewButtonClicked` 의 `configs/` 복사본 · ModelRunner `onGenerateInputFileClicked` 의 `getViewSourceConfigsDir()` 복사본) 어느 것도 `lastLoadedPrtPath()` 를 바꾸지 않는다. `m_jsonAccumBuffer` 를 커맨드 완료·실패 시 비운다.
- 완료 기준: 1 · 3 은 **NX 불요**(grep · CAD-11 TU), 2 는 **NX 게이트**(실기 수동)
  1. `controller/DashSolverNxCad.cpp:enqueueUpdatePrtGeometry` 에 `m_originalPrtPath` 쓰기 0건 (쓰기는 `enqueueLoadPrt` 1곳)
  2. (NX 게이트) wbpj DOE 배치 1회 / Optimizer 프리뷰 1회 / ModelRunner 프리뷰 1회 — 각각 뒤에 `lastLoadedPrtPath()` 가 마지막 Load 한 `.prt` 와 같다 (CADWidget [Preview] 가 그 prt 로 간다)
  3. 실패한 커맨드 뒤 `m_jsonAccumBuffer` 가 비어 있다 — `commandFailed` 를 직접 emit 하는 단위 테스트로 확인 (CAD-11 TU 에 1건 추가 — 선후 무관)
- 변경 범위: controller/DashSolverNxCad.cpp (필요 시 .h)
- 선행: LCH-29 (wbpj 경로 처분 — 완료 기준 2 의 배치 1회가 소멸할 수 있다)
- 충돌: CAD-01 · CAD-06 · CAD-08 (같은 파일) · B2 교집합: DashSolverNxCad.cpp → CAD-03 CAD-15
- 흡수: CAD-c10, c12
- 비고: 둘 다 "명령 단위로 끝나야 할 상태가 파사드 전역에 남는" 한 개념(#249 범위 밖 절) — 검토 #4 의 `c12` 분리(CAD-02b) 제안은 **기각**(00-plan 1-2 개념적 응집: 기제가 둘이어도 "파사드 전역 상태의 수명" 한 덩어리로 읽힌다). CAD-01 과 같은 브랜치에 넣지 않는다 — CAD-01 은 동작 불변 리팩터. **LCH-29 조건** — `제거` 면 완료 기준 2 의 배치 항이 빠지고 Optimizer·ModelRunner 2경로만 남는다(목표·수정분은 그대로, 불개입 경로 몫만 제외).

### CAD-03 · Set 진입 시 세션 캐시 재적용이 저장된 체크·범위를 덮지 않게 한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `setModel` 의 진입 순서를 "저장 JSON 1회 로드 → 세션 캐시는 이름 매칭 병합" 으로 바꾼다. 병합은 **캐시·데몬 경로 전용 함수**(예 `mergeNxCadParameterJson`)로 두고 `applyNxCadParameterJson` 자체는 교체로 유지한다 — 그 함수는 `loadFromJson:397` 도 호출하므로 병합으로 바꾸면 "파일이 정본" 의미가 깨진다(Set 재진입 시 파일값이 메모리의 미저장 편집에 밀린다). 병합은 기존 행의 `isChecked`·`lower`·`upper` 를 이름으로 보존하고(없는 이름만 추가·사라진 이름만 제거), MainWindow 와 위젯이 각각 부르던 `setProjectDirectory`→`loadFromJson` 2회를 1회로 줄인다. 프로젝트 전환에서 세션 전역 2곳을 비운다 — `DashManager::m_lastNxCadParameterJson` 과 파사드 `DashSolverNxCad::m_originalPrtPath`(clear 0곳이라 다른 프로젝트의 [Preview]·DV 승격 복사가 이전 프로젝트 `.prt` 로 간다).
- 완료 기준: 1 은 **NX 게이트**(실기 수동), 2~4 는 **NX 불요**(로그 · grep · CAD-11 TU)
  1. (NX 게이트) `.prt` 를 Load 한 세션에서 승격된 Set 을 재선택해도 체크 상태와 Lower/Upper 가 저장값과 같다
  2. 다른 프로젝트를 연 뒤 CAD Set 진입 시 이전 프로젝트의 파라미터 행이 뜨지 않는다
  3. Set 진입당 `loadFromJson` 호출 1회 (로그 `Loaded settings from` 1건)
  4. `applyNxCadParameterJson` 은 교체 그대로 — `loadFromJson` 왕복에서 파일값이 정본이다(CAD-11 TU) · 프로젝트 전환 뒤 `lastLoadedPrtPath()` 가 빈 문자열
- 변경 범위: view/DashGeometryParameterCADWidget.cpp · model/DashGeometryParameterCAD.cpp (병합 함수 신설) · controller/DashManager.cpp (캐시 초기화 1곳) · controller/DashSolverNxCad.h · controller/DashSolverNxCad.cpp (`m_originalPrtPath` reset 1곳) · view/DashMainWindow.cpp:handleGeometryParameterSelection (중복 `setProjectDirectory` 제거)
- 선행: -
- 충돌: CAD-04 · CAD-05 · CAD-07 (CADWidget.cpp) · PR #652 · #654 (DashManager.cpp · DashMainWindow.cpp) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashGeometryParameterCADWidget.cpp → 공유 10건(deps.md 5절) · DashManager.cpp → CAD-06 DOE-19 EXE-06 PRJ-03 PRJ-04 PRJ-06 PRJ-14 REN-07 · DashGeometryParameterCAD.cpp → CAD-06 CAD-09 PRJ-09 UIC-20 · DashSolverNxCad.cpp → CAD-01 CAD-02 CAD-06 CAD-08 CAD-15 · DashSolverNxCad.h → CAD-01 CAD-06 · PR #655(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: CAD-D4 · CAD-c21, c22, c23, c52
- 비고: 대안 — 캐시 적용을 "모델이 비었을 때만" 으로 한정하면 더 작지만, Load 직후 Set 재진입에서 데몬의 Part·Dependent 갱신을 잃는다. 병합안 권장. 초기화 지점 2곳 모두 #560 이 CAD Set 목록을 지운 프로젝트 전환 경로(`DashProject::clearAllSets` 호출부 — `model/DashProject.cpp:84`)와 같은 곳. 검토 #5 의 3분할(CAD-03a 병합 / CAD-03b 전환 초기화) 제안은 **기각** — "세션 캐시가 저장값·프로젝트 경계를 넘지 않게 한다" 한 개념이고 파일이 넷·모듈 접점이 PRJ 라는 것은 분할 사유가 아니다(00-plan 1-2). 검토 #15(파사드 `m_originalPrtPath`)는 c23 과 같은 기제라 본 항목에 합쳤다 — 파사드 쪽은 1줄 reset 이므로 규모 S 유지. PRJ 접점: 전환 훅 자리는 PRJ-c64 계열 함수와 겹칠 수 있다.

### CAD-04 · DV 승격의 범위값 정본을 모델로 단일화한다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `collectCadDvRows` 가 셀 스핀박스(`cellWidget(visualRow, 3/4)`) 대신 모델을 이름 매칭으로 읽어 lower/upper/defaultText 를 모은다. 표 접근 방식을 "체크는 표(이름 매칭) · 값은 모델" 둘로 줄여 정렬 방어 3갈래(이름 · 시각 행 · 캡처 행)를 없앤다. 모델은 이미 `valueChanged` → `setIndependentParameterBounds` 로 동기되므로 저장값은 불변.
- 완료 기준:
  1. `collectCadDvRows` 에 `cellWidget` 호출 0
  2. 헤더 클릭으로 정렬한 뒤 승격한 DV-Geometry 의 `min/max` 가 각 이름의 모델값과 일치 (단위 테스트 — CAD-11)
- 변경 범위: view/DashGeometryParameterCADWidget.cpp (`collectCadDvRows` · 필요 시 `onCadApplyAddValues` 도 모델 경유)
- 선행: CAD-11 (현행 동작을 고정한 TU 가 먼저 — 본 항목이 그 기대값을 갱신한다)
- 충돌: CAD-03 · CAD-05 · CAD-07 (같은 파일, CAD-05 와 같은 함수) · CAD-11 (tests/TestGeometryParameterCad.cpp 기대값 갱신) · B2 교집합: DashGeometryParameterCADWidget.cpp → 공유 10건(deps.md 5절)
- 흡수: CAD-D12 · CAD-D6 · CAD-c25, c28 · CAD-c51 (← UIC-c58)
- 비고: CAD-D6 의 세 갈래는 정적으로 각각 내부 정합이 성립한다(QTableWidget 정렬이 persistent index 로 cellWidget 을 옮기고, 람다 캡처 행은 `m_params` 인덱스). 결함의 실체는 접근 방식의 다중화라 정본 단일화로 닫는다.

### CAD-05 · 현재값(value)을 저장·복원하고 meta.default 에 쓴다
- 종류: PR | 규모: S | 태그: A, C · bug
- 목표: `toSettingsJsonObject` 의 `Independent Parameter.Value` 에 `upper` 대신 `CADParameterRow::value`(데몬 현재값)를 쓰고, `collectCadDvRows` 의 `defaultText` 를 모델 3열(=lower) 이 아니라 `value` 에서 채워 `DV-Geometry.meta.default` 가 현재값이 되게 한다. 로드 쪽(`applyNxCadParameterJson` — `Value` 를 현재값으로 읽고 `Lower/Upper` 로 범위 복구)은 그대로.
- 완료 기준: 2 · 3 은 **NX 불요**(CAD-11 TU · grep), 1 은 **NX 게이트**(데몬 현재값이 필요)
  1. (NX 게이트) 승격 후 JSON: `Independent Parameter.Value[i] == 데몬 Value[i]` · `DV-Geometry.<name>.meta.default == 그 값`
  2. 저장 → 재로드 왕복에서 `value`·`lower`·`upper` 셋이 보존 (단위 테스트 — CAD-11)
  3. 하류 1곳의 입력 변경이 의도대로다 — `journalLaunchConfig` 의 `indParamInitials`(wbpj Journal 비샘플 파라미터 초기값)가 upper 가 아니라 현재값을 받는다 (TU 또는 생성된 Journal 설정 JSON 1건 비교)
- 변경 범위: model/DashGeometryParameterCAD.cpp (`toSettingsJsonObject`, 필요 시 `value` 접근자) · view/DashGeometryParameterCADWidget.cpp (`collectCadDvRows`) · viewmodel/DashGeometryParameterCADPresentationModel.h (주석)
- 선행: CAD-04 (`collectCadDvRows` 를 먼저 모델 기반으로) · CAD-11 (현행 왕복 TU 선행 — 본 항목이 기대값 갱신) · LCH-29 (wbpj 경로 처분 — 완료 기준 3 의 존폐)
- 충돌: CAD-03 · CAD-04 · CAD-07 (CADWidget.cpp) · CAD-06 (Model .cpp) · CAD-11 (tests/TestGeometryParameterCad.cpp 기대값 갱신) · B2 교집합: DashGeometryParameterCADWidget.cpp → 공유 10건(deps.md 5절) · DashGeometryParameterCAD.cpp → CAD-09 PRJ-09 UIC-20
- 흡수: CAD-D10 · CAD-D11 · CAD-c26, c27
- 비고: 저장 포맷의 의미 변경(Value: upper → 현재값). 기존 파일은 `Lower/Upper` 키가 있어 범위 복원엔 영향 없고, `value` 만 옛 upper 로 읽혀 재승격 전까지 `meta.default` 가 낡는다 — 마이그레이션 불요. **하류 동작 변경 1건(의도된 것)** — `model/DashJobRunnerAnsysJournal.cpp:100-110 journalLaunchConfig` 가 `initIndParam["Value"]` 를 비샘플 파라미터 초기값으로 읽으므로 wbpj Journal 의 초기값 배열이 upper→현재값으로 바뀐다(**접점 LCH**). `viewmodel/DashSurrogateModelCommon.cpp:148-176 buildCadConfigJson`(Optimizer·ModelRunner)은 Name/Part 만 읽고 값은 DV 에서 받아 무영향. **LCH-29 조건** — `제거` 면 하류 영향이 사라져 완료 기준 3 이 소멸한다. PER 과 접점(저장 포맷)이나 파일은 CAD 소유.

### CAD-06 · CAD 영역 죽은 코드 6건을 제거한다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: 호출·연결 0인 선언·정의 4건을 지운다 — `DashGeometryParameterCAD::saveSettings`(no-op) · `m_lastLoadedStpPath`/`lastLoadedStpPath()` · `DashGeometryParameterCADWidget::onDirChanged` · `DashManager::applyLastNxCadParameterJsonToGeometryModels`. `DashSolverNxCad::JobType` 과 `DashSolverNxCad.h:73-74` 의 "commandId encodes JobType" 주석은 CAD-01 이 같은 블록을 재작성하므로 **CAD-01 몫**(검토 #16).
- 완료 기준:
  1. 위 4 심볼 `git grep` 0건
  2. 빌드 통과 · 동작 불변
- 변경 범위: controller/DashSolverNxCad.h · controller/DashSolverNxCad.cpp · model/DashGeometryParameterCAD.h · model/DashGeometryParameterCAD.cpp · view/DashGeometryParameterCADWidget.h · view/DashGeometryParameterCADWidget.cpp · controller/DashManager.h · controller/DashManager.cpp
- 선행: -
- 충돌: CAD-01 · CAD-02 · CAD-08 (DashSolverNxCad) · CAD-03 · CAD-05 (Model · Widget) · PR #652 · #654 (DashManager) · B2 교집합: DashGeometryParameterCADWidget.cpp → 공유 10건(deps.md 5절) · DashManager.cpp → DOE-19 EXE-06 PRJ-03 PRJ-04 PRJ-06 PRJ-14 REN-07 · DashGeometryParameterCAD.cpp → CAD-09 PRJ-09 UIC-20 · DashSolverNxCad.cpp → CAD-15 · DashManager.h → PRJ-03 PRJ-04 PRJ-06 PRJ-19
- 흡수: CAD-U3 · CAD-c11 · CAD-c35(4건 몫 — `JobType`·헤더 주석은 CAD-01)
- 비고: 파일 8개라 규칙상 M 이나 삭제만이라 반나절. `DashSolverNxCad.{h,cpp}` 는 `lastLoadedStpPath` 때문에 남는다 — 선행이 아니라 충돌 관계(CAD-01 과 순차). 색인 U3 의 `getContext`·`getLoadedFilePath`·`setModel` 오버로드는 a03efe0b 에서 이미 제거됐다.

### CAD-07 · 진행 표시 짝을 맞춘다 — 프리뷰 시작 호출 · STEP 로드 실패 시 정지
- 종류: PR | 규모: S | 태그: D · bug
- 목표: CADWidget `enqueuePreview` 가 요청 직전에 `startNxCadStatusAnimation("NX CAD updating geometry")` 을 걸어 ModelRunner·Optimizer 프리뷰와 같은 짝을 갖게 한다. `DashOcctViewWidget::loadStepFile` 의 중도 반환 4곳(뷰 미생성 · 파일 부재 · STEP 읽기 실패 · OneShape null)에 실패 통지(반환값 또는 `stepFileLoadFailed`)를 두고 MainWindow 가 그때 `stopProjectLoadStatusAnimation` 을 부른다.
- 완료 기준: 2 는 **NX 불요**(손상 `.stp` 직접 Load 로 재현), 1 은 **NX 게이트**(실기 수동)
  1. (NX 게이트) [Lower/Upper Preview] 클릭 직후 상태바에 "NX CAD updating geometry…" 가 돌고 완료 시 "NX CAD geometry updated." 로 끝난다
  2. 손상된 `.stp` 를 Load(또는 `.prt` 완료 후 OCCT 읽기 실패)하면 "Loading …" 이 남지 않는다 — `loadStepFile` 중도 반환 4곳 전부가 실패를 통지한다
- 변경 범위: view/DashGeometryParameterCADWidget.cpp · view/DashMainWindow.cpp · view/DashOcctViewWidget.h · view/DashOcctViewWidget.cpp
- 선행: -
- 충돌: PR #651 · #652 · #654 (DashMainWindow.cpp) · CAD-01 (MainWindow 의 NX 구독 블록) · CAD-03 · CAD-04 · CAD-05 (CADWidget.cpp) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashGeometryParameterCADWidget.cpp → 공유 10건(deps.md 5절) · DashOcctViewWidget.cpp → CAD-12 CAD-14 · PR #655(DashMainWindow.cpp)
- 흡수: #464 · CAD-D9 · CAD-D1(잔여) · #463(CAD 몫) · CAD-c18, c19 · CAD-c49, c50 (← EXE-c44, EXE-c23)
- 비고: CAD-D1 의 본체(성공 경로 미정지)는 해소돼 있다 — `stepFileLoaded` → `stopProjectLoadStatusAnimation` (DashMainWindow::ensureOcctViewerCreated, 25b9994c). 검토 #10 의 2분할(07a D9 / 07b D1 잔여) 제안은 **기각** — "진행 표시의 시작·정지 짝" 한 개념이고 둘 다 같은 스피너의 한쪽 끝이다(00-plan 1-2). **규약 연결**: CADWidget → MainWindow 도달은 위젯 시그널을 MainWindow 가 구독하는 쪽으로 — view→view 부모 탐색(`findMainWindow` 선례)을 늘리지 않는다. 같은 규약을 PRJ-25(부모 역참조 12곳 → 시그널, 목록에 CADWidget 은 **미포함**)와 OPT-22(`nxPreviewRequested`)가 쓰므로 **시그널명은 OPT-22 와 맞춘다**(`nxPreviewRequested`). PRJ-25 가 먼저 랜딩하면 그 형식을 따르고, 본 항목이 먼저면 PRJ-25 가 CADWidget 을 목록에 더하지 않는다(선행 관계는 아니다 — 파일이 다르다). "상태 고정 기입(Enqueued)" 은 #440(LCH) 소관, 여기서 다루지 않는다. 진행 표시 규약은 EXE-07 — #463 확산의 CAD 몫.

### CAD-08 · 프리뷰 temp .prt 를 정리한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: 프리뷰마다 데몬이 `{temp}/{base}_{upper|lower}_preview_{seq}.prt` 를 남기고 어느 경로도 지우지 않는 누적을 끊는다. GUI 단독 해법 — `enqueueLoadPrt` 의 정리 글로빙에 `*_lower_preview*.prt`·`*_upper_preview*.prt` 를 더한다.
- 완료 기준: 2 는 **NX 불요**(글로빙 패턴·대상 디렉터리 검토), 1 은 **NX 게이트**(프리뷰 실행 필요)
  1. (NX 게이트) 프리뷰 N회 후 다음 `.prt` Load 시 temp 의 `*_preview_*.prt` 가 0개
  2. DOE 배치 산출 `{outputBaseDir}/{runKey}/{runKey}.prt` 는 건드리지 않는다 (temp 밖)
- 변경 범위: controller/DashSolverNxCad.cpp
- 선행: -
- 충돌: CAD-01 · CAD-02 · CAD-06 (같은 파일) · B2 교집합: DashSolverNxCad.cpp → CAD-03 CAD-15
- 흡수: CAD-D16 · CAD-c33
- 비고: 대안은 프리뷰 요청에서 `--no-cleanup` 을 떼어 데몬 정리 분기(`main.py:274-275`)에 맡기는 것 — 데몬 측 동작 실측이 필요해 글로빙 확장을 택한다. 매니페스트 문서가 D16 을 "사장 경로로 격리" 로 묶었으나 프리뷰는 정규 CAD 동선이다.

### CAD-09 · .prt 보관본 삭제와 Set↔.prt 결합 미저장의 처분을 결정한다
- 종류: DEC | 규모: S | 태그: A, C
- 목표: Project-Manifest-CAD-Path-Disposition(2026-09-18 방침)이 D15(재Load 가 승격 보관본 삭제)·D17(Set 별 `.prt` 미저장)을 "후속작업 13(미래 CAD 경로) 동반 유보 · 사장 경로로 격리" 로 기록했다. 새 작업 목록이 그 결정을 승계할지, 아니면 최소 수선을 지금 할지 정한다.
- 완료 기준: 결정 기록 — (a) 유보 승계: 후속작업 13 의 `cadSource {uuid, path}` 설계에 D15·D17 을 입력으로 넘기고 본 목록에선 항목 없음. **(a) 를 고르면 추적 위치를 함께 지정해야 한다** — 현재 03-items 전체에 후속작업 13(미래 CAD 경로 — Meshing·Match NSET·deck 등록) 추적 항목이 0이라 D15·D17 이 어디에도 남지 않는다(검토 #13). 지정 후보: CAD 에 추적 항목 1건(CLOSE/EXT 형식) 신설 또는 PRJ 매니페스트 후속 항목에 D15·D17 입력 등재 / (b) 최소 수선: `loadPrt` 출력 STEP 위치를 `configs/` 밖(모듈 폴더)으로 옮겨 보관본과 base 충돌을 끊고(D15), Set JSON 에 `prt` 경로 1필드를 기록해 재진입 시 Load 없이 프리뷰 가능하게(D17) — 선택 시 PR 2건(S·S)으로 분할
- 변경 범위: (b) 선택 시 view/DashMainWindow.cpp:openFileInViewport · view/DashGeometryParameterCADWidget.cpp:syncDvFromCheckedCadParameters · viewmodel/DashGeometryParameterCADPresentationModel.cpp:mergeSettingsRoot · model/DashGeometryParameterCAD.cpp
- 선행: -
- 충돌: (b) 선택 시 CAD-03 · CAD-05 · CAD-07 · PR #651 · #652 · #654 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashGeometryParameterCADWidget.cpp → 공유 10건(deps.md 5절) · DashGeometryParameterCAD.cpp → CAD-06 PRJ-09 UIC-20 · DashGeometryParameterCADPresentationModel.cpp → CAD-13 · PR #655(DashMainWindow.cpp)
- 흡수: CAD-D15 · CAD-D17 · CAD-c32, c34
- 비고: D15 의 삭제 주체는 데몬(`main.py:214·330-338` `_cleanup_temp`)이라 (b) 의 GUI 측 수선은 경로 분리뿐이다. D17 은 PRJ 의 Set identity(Project-Manifest-Set-Identity-And-Decision-Revisions D29~D31) 와 접점 — (b) 를 고르면 PRJ 에 `cadSource` 키 합의가 필요하다. 검토 #15 의 파사드 `m_originalPrtPath` 전환 reset 은 본 DEC 의 입력이 아니라 CAD-03 의 수정분으로 넣었다 — c23 과 같은 기제라 결정을 기다릴 이유가 없다.

### CAD-10 · 데몬: NX 표현식 적용 실패를 stdout [ERROR] 로 올린다
- 종류: EXT | 규모: S | 태그: A · bug
- 목표: DashOpti_CadNx `nx_helpers.py:update_expressions` 가 이름별 실패를 ListingWindow 에만 쓰고 삼키는 것을 예외 전파(또는 실패 목록 수집 후 `RuntimeError`)로 바꿔 `main.py` 가 `[GUI] [ERROR]` 를 찍게 한다. GUI 는 기존 `[ERROR]` 매칭으로 `commandFailed` → `loadPrtFailed`/배치 실패로 받는다 — GUI 변경 0.
- 완료 기준: 외부 저장소 PR — PRT 에 없는 이름을 DV 로 올려 프리뷰하면 GUI 에 실패 모달이 뜨고 STEP 이 성공으로 등록되지 않는다 · DOE 배치는 그 케이스를 실패로 계상한다
- 변경 범위: (GUI 없음) DashOpti_CadNx `source/.../nx_helpers.py` · `main.py` — 위키 좌표 d71a17d
- 선행: -
- 충돌: -
- 흡수: CAD-D14 · CAD-c30
- 비고: 부분 실패(일부 이름만 없음) 를 전체 실패로 볼지, 적용된 이름만 반영하고 경고로 둘지는 데몬 측 결정 — GUI 쪽은 어느 쪽이든 `[ERROR]` 유무로만 판정한다. CAD-U4 의 "판정이 로그 포맷" 은 EXE-12 소관(범위밖)이며 본 항목은 그 계약 위에서 움직인다. CAD-D14 가 EXE-12 흡수 목록에도 올라 있다(03-items/EXE.md 대응표 "CAD-10 과 중복 기록 — Phase B 병합" 미이행) — **실작업은 본 항목 단일**이고 EXE-12 는 "데몬 4종 준수 표" 에서 본 항목을 참조만 해야 한다. `보류: EXE 몫`(EXE-12 흡수 목록·대응표에서 CAD-D14 제거).

### CAD-11 · CAD 모델·PM 의 JSON 왕복과 파사드 commandId 해석에 자동 테스트를 둔다
- 종류: PR | 규모: S | 태그: F · refactor
- 목표: NX 없이 도는 단위 테스트 1 TU 를 추가해 **현행 동작을 기대값으로 고정한다** — `DashGeometryParameterCAD::applyNxCadParameterJson`/`toSettingsJsonObject`/`toNxCadConfigJson` 왕복(데몬 JSON → 저장 JSON → 재로드, 현행 `Independent Parameter.Value == upper`) · `DashGeometryParameterCADPresentationModel::buildDvGeometryJson`/`mergeSettingsRoot` · `DashSolverNxCad` 의 `commandCompleted`/`commandFailed`/`outputLine` 을 직접 emit 해 방출 시그널·`commandId`(현행 `"<verb>:<stp>"`)·버퍼 상태를 `QSignalSpy` 로 검증.
- 완료 기준:
  1. `tests/CMakeLists.txt` 에 `test_geometry_parameter_cad` 등록 · `ctest` 통과
  2. 현행 저장 왕복과 `commandId` 규약이 기대값으로 고정된다 — 후행 항목(CAD-01 태그·대칭 4종 / CAD-02 버퍼 경계 / CAD-04 모델 정본 / CAD-05 현재값 / CAD-13 헬퍼 쓰기)이 각자 기대값을 갱신·추가한다
- 변경 범위: tests/CMakeLists.txt · tests/TestGeometryParameterCad.cpp (신규)
- 선행: -
- 충돌: CAD-01 · CAD-02 · CAD-04 · CAD-05 · CAD-13 (tests/TestGeometryParameterCad.cpp — 각자 기대값 갱신) · DEV-19 (tests/CMakeLists.txt 등록 헬퍼 — 먼저 오면 그 형식으로 등록) · B2 교집합: tests/CMakeLists.txt → 공유 12건(deps.md 5절) · PR #655(tests/CMakeLists.txt) · PR #654(tests/CMakeLists.txt) · PR #652(tests/CMakeLists.txt) · PR #651(tests/CMakeLists.txt)
- 흡수: CAD-U5 · #489(CAD 몫) · CAD-c36 · CAD-c47, c48 (← UIC-c57, DEV-c24)
- 비고: **선행 없이 먼저 랜딩한다** — 종전 `선행: CAD-01 · CAD-04 · CAD-05` 는 완료 기준 순환이었다(CAD-02 완료2 · CAD-04 완료2 · CAD-05 완료2 · CAD-13 완료3 이 "CAD-11 TU 로 확인" 인데 그 셋이 CAD-11 의 선행 → 선행 항목의 완료를 후행이 증명). 선행 그래프상 순환은 아니어서 `check_coverage.py`·`build_deps.py` 가 잡지 못했다(검토 #8). 현행 동작을 고정한 TU 를 먼저 두고 CAD-01·02·04·05·13 이 기대값을 갱신하는 순서로 끊는다. `DashSolverNxCad` 생성자는 `DashManager` 를 건드리지 않는다(`tryStartIfConfigured` 만 접근) — 테스트에서 직접 생성 가능. 시그널은 public 멤버라 테스트가 `emit` 할 수 있다. 전송 계층(`[FINISHED]`/`[ERROR]` 판정)은 test_process_runtime + daemon_stub 이 이미 덮는다.

### CAD-12 · OCCT 뷰의 프리뷰 덮어쓰기 처분을 정한다 — 단일 형상 뷰 유지 vs 원본 복귀 경로
- 종류: DEC | 규모: S | 태그: D, E
- 목표: `DashOcctViewWidget::loadStepFile` 은 `m_context->RemoveAll` 뒤 형상 하나만 올린다. CAD 위젯 Lower/Upper 프리뷰와 Optimizer 프리뷰 `.stp` 가 Load 한 `.prt` 의 STEP 을 덮고 되돌릴 UI 가 없다(원본은 `configs/{prtBase}.stp` 재 Load 또는 NX loadPrt 재실행). #316·#318 은 이 지점을 VTK 소유권 모델 밖(별도 씬)으로 뺐다. (a) 단일 형상 뷰 유지 — 결함 아님으로 기록 (b) 원본 STEP 경로를 기억해 "Show original" 복귀 1동작 (c) 원본·프리뷰 병치(투명도) 중 하나를 정한다.
- 완료 기준: 결정 기록 — 선택지·사유. (b)/(c) 면 후속 PR S (view/DashOcctViewWidget.{h,cpp} · view/DashMainWindow.cpp:previewStepFile)
- 변경 범위: - (결정 후: view/DashOcctViewWidget.cpp:loadStepFile :176-229 · clearView :376 · view/DashMainWindow.cpp:previewStepFile :3224 · onNxPreviewStepReady :3247 · onNxLoadPrtStepReady :3203)
- 선행: -
- 충돌: CAD-07 · CAD-14 (DashOcctViewWidget) · PR #651 · #652 · #654 (DashMainWindow.cpp) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · PR #655(DashMainWindow.cpp)
- 흡수: #316(.stp 덮어쓰기 — 범위 제외 명시) · #318(부류 2 ⑩ OCCT) · CAD-c40, c43 (← OPT-c08, REN-c17)
- 비고: OCCT 뷰는 공유 VTK renderer 가 아니라 REN 소유자 태그 모델의 대상이 아니다. (a) 가 가장 싸고 현행 사용 흐름(프리뷰를 보려고 누른다)과 맞는다.

### CAD-13 · DV 승격 JSON 쓰기를 공용 파일 헬퍼로 옮긴다
- 종류: PR | 규모: S | 태그: A · refactor
- 목표: `saveDvGeometry` 의 read-modify-write(`QFile` 읽기 → `mergeSettingsRoot` → `QFile` 직쓰기 Truncate) 를 PER-02 가 공용 진입점으로 승격하는 **DashSaveSystem 헬퍼**(`persistence/DashSaveSystem` 의 read/writeJsonFile — QSaveFile 원자 쓰기 · 길이 검사 · Result 사유 반환) 호출로 바꾼다. 포맷·병합 규칙 불변. 실패 사유를 호출자(CADWidget `syncDvFromCheckedCadParameters`)가 로그·통지한다.
- 완료 기준: (1) viewmodel/DashGeometryParameterCADPresentationModel.cpp 에 `QFile` 0건 (2) 읽기 전용 경로에서 승격 실패 시 기존 파일 바이트 동일 + 통지 (3) CAD-11 왕복 테스트 통과
- 변경 범위: viewmodel/DashGeometryParameterCADPresentationModel.cpp (`saveDvGeometry` :55-77) · view/DashGeometryParameterCADWidget.cpp (사유 소비 1곳)
- 선행: PER-02(DashSaveSystem 헬퍼 승격) · CAD-05 (저장 의미 변경을 먼저 — 같은 함수에서 동작 변경과 리팩터를 섞지 않는다) · CAD-11 (현행 왕복 TU 선행)
- 충돌: CAD-04 · CAD-05 (같은 함수) · CAD-03 (CADWidget) · CAD-11 (tests/TestGeometryParameterCad.cpp) · B2 교집합: DashGeometryParameterCADWidget.cpp → 공유 10건(deps.md 5절) · DashGeometryParameterCADPresentationModel.cpp → CAD-09
- 흡수: #479(CAD 몫) · #478(CAD 몫) · #480(CAD 몫 — PER-04 뒤 버전 키 자동) · CAD-c45 (← PER-c23)
- 비고: PER-c08 RMW 13지점 중 1건. `variant` 키 기록(PER-c10)은 그대로 — 버전 키와의 관계는 PER-03 결정. 05-final/decisions.md 3항 — PER-02 는 `utils/DashJsonFile` 신설을 버리고 기존 `DashSaveSystem::read/writeJsonFile` 승격으로 확정됐다. 선행은 그대로 PER-02.

### CAD-14 · OCCT 뷰 마우스 좌표에 DPR 을 반영한다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: `mousePressEvent`/`mouseMoveEvent` 가 논리 좌표 `event->x()/y()` 를 OCCT(`WNT_Window` — 물리 px 창)의 `StartRotation`·`Rotation`·`Pan` 에 그대로 넘겨 DPR≠1 에서 회전 피벗과 팬 거리가 어긋난다. `event->position() * devicePixelRatioF()` 로 물리 px 로 바꿔 넘기고 `m_lastMousePos` 도 같은 단위로 든다.
- 완료 기준: (1) 150%·200% 모니터에서 회전 피벗이 커서 아래 점과 일치하고 팬이 커서를 따라간다 (2) 100% 에서 현행과 동일 (3) 배율이 다른 모니터로 창을 옮긴 뒤에도 (1) — UIC-02 실기 환경
- 변경 범위: view/DashOcctViewWidget.cpp (`mousePressEvent` :452-462 · `mouseMoveEvent` :464-488)
- 선행: -
- 충돌: CAD-07 · CAD-12 (같은 파일)
- 흡수: #447 R1 · CAD-c46 (← UIC-c30)
- 비고: Qt6 는 `highDpiScaleFactorRoundingPolicy` 기본 PassThrough 라 150% 에서 지금 발현. `wheelEvent` 는 좌표를 쓰지 않아 대상 밖. `resizeEvent` 의 `MustBeResized` 는 OCCT 가 창 크기를 직접 읽어 영향 없음.

### CAD-15 · 데몬 사망 시 실패 통지 fan-out 을 실측하고 합산 정책을 정한다
- 종류: INV | 규모: S | 태그: B, D · bug
- 목표: `DashExtensionProcess::drainCommands` 가 in-flight 1건 + 큐 N건을 각각 `commandFailed` 로 동기 emit 하고(:280-285) 파사드가 그대로 `loadPrtFailed` 로 올려 `DashMainWindow` 모달이 N회 뜨는지, 모달이 동기 emit 루프 안에서 이벤트 루프를 세워 남은 통지를 지연시키는지 실측한다. 배치 측 오계상(CAD-c53)과 같은 뿌리이므로 결과를 CAD-01 의 구독자 필터 설계 입력으로 넘긴다.
- 완료 기준: 실측 결과 — `tests/daemon_stub.cpp` + `test_process_runtime` 으로 "큐 2건 + 기동 실패" 를 재현해 (1) `commandFailed` 방출 횟수 (2) 대화형 경로에서 모달이 몇 번 뜨는지(수동 1회) (3) 합산 정책 선택 — 첫 통지만 모달·나머지는 로그 / 요청 태그별 1회 / 현행 유지(#249 가 축소 범위 밖으로 명시) — 를 기록한다. NX 불요(스텁으로 재현)
- 변경 범위: (조사만) controller/DashExtensionProcess.cpp:drainCommands · controller/DashSolverNxCad.cpp:emitFailure · view/DashMainWindow.cpp(loadPrtFailed 람다) · tests/daemon_stub.cpp · tests/TestProcessRuntime.cpp
- 선행: -
- 충돌: CAD-01 (결과가 구독자 필터 설계에 들어간다 — 본 항목이 먼저) · EXE-12 (같은 계약 문서 · tests/TestProcessRuntime.cpp) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashSolverNxCad.cpp → CAD-02 CAD-03 CAD-06 CAD-08 · TestProcessRuntime.cpp → EXE-11 · DashExtensionProcess.cpp → EXE-11 · daemon_stub.cpp → EXE-11 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #652(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: #249(범위 밖 절 — 모달 N회) · CAD-c15
- 비고: 검토 #14. fan-out 자체는 코드로 성립하나 모달 횟수·순서는 모달이 중첩 이벤트 루프를 세우는지에 달려 실측이 필요하다. "현행 유지" 로 끝나면 CLOSE 사유만 남기고 PR 없이 닫는다. EXE-12 가 "비정상 종료 = 진행·대기 명령 전부 실패" 를 계약으로 고정하므로 방출 횟수 자체는 바꾸지 않고 **소비자 측 합산**만 정한다.

## 대응표

| 원천 | 항목 | 비고 |
|---|---|---|
| #249 | CAD-01 | 범위 밖 절의 파사드 상태 2건 → CAD-02 · CAD-06, per-command cancel → EXE-12(c13), Direct 다중 .wbpj disconnect → LCH(c14), 모달 N회 → CAD-15 INV(c15). 배치 실패 슬롯 가드·데몬 사망 계상(c53)은 CAD-01 완료 기준 3 |
| #464 | CAD-07 | CAD-D1 본체는 해소됨 — 잔여(OCCT 읽기 실패)와 D9 만 |
| #457 (접점) | CAD-01 (OPT-D19 본체) | OPT-c10 · c37 흡수 (CAD-c41 · c42). 위젯 측 소비자 전환은 OPT-22 (CAD-c37 이관) |
| CAD-D1 | 해소됨 (잔여 → CAD-07) | `stepFileLoaded` → `stopProjectLoadStatusAnimation` (25b9994c) |
| CAD-D2 | 범위밖 → PRJ-26 | `DashMainWindow::openFileInViewport` 의 processEvents, 전 확장자 공통. #455 는 B2 에서 UIC→PRJ 재배정(PRJ-c64) — CAD-c20 |
| CAD-D3 | CAD-01 | 태그 상관까지 — 합류점 설계는 비고 · EXE-c42 이관 (CAD-c44) |
| CAD-D4 | CAD-03 | |
| CAD-D5 | 해소됨 | a03efe0b(#507) |
| CAD-D6 | CAD-04 | UIC-c58 이관 (CAD-c51) |
| CAD-D7 | CAD-01 | |
| CAD-D8 | CAD-01 | |
| CAD-D9 | CAD-07 | EXE-c44 · EXE-c23 이관 (CAD-c49 · c50) |
| CAD-D10 | CAD-05 | |
| CAD-D11 | CAD-05 | |
| CAD-D12 | CAD-04 | |
| CAD-D13 | 해소됨 | b0600d6b(#560) QPointer |
| CAD-D14 | CAD-10 | EXT. EXE-12 흡수 목록에도 이중 등재 — 실작업은 CAD-10 단일, `보류: EXE 몫` |
| CAD-D15 | CAD-09 | DEC |
| CAD-D16 | CAD-08 | |
| CAD-D17 | CAD-09 | DEC |
| CAD-U3 | CAD-06 | 6건 중 3건은 a03efe0b 에서 해소 |
| CAD-U4 | 범위밖 → EXE-12 | `controller/DashExtensionProcess` 판정 계약(CAD-c31). 데몬 측은 CAD-10. CAD-c13(per-command cancel)도 EXE-12 |
| CAD-U5 | CAD-11 | UIC-c57 · DEV-c24 이관 (CAD-c47 · c48) |
| Project-Manifest-CAD-Path-Disposition | LCH-29(선행 DEC) · CAD-01 · CAD-02 · CAD-05 · CAD-09 | wbpj 사장 여부는 LCH-29 가 정한다(decisions.md 1항) — CAD-01 Phase 3 · CAD-02 · CAD-05 가 선행으로 등록. D29~D31 유보가 CAD-09 를 정한다 |
| OPT-D19 (접점) | CAD-01 | OPT 에서 이관 (OPT-c10 · c37 → CAD-c41 · c42) — 위젯 수신 후속은 OPT-22 |
| RUN-D15 (접점) | CAD-01 | RUN 에서 이관 (RUN-c32 → CAD-c39) |
| 접점 #316 .stp · #318 ⑩ | CAD-12 (DEC) | OPT · REN 에서 이관 (OPT-c08 · REN-c17 → CAD-c40 · c43) |
| 접점 #478 · #479 · #480 | CAD-13 | PER 에서 이관 (PER-c23 → CAD-c45) — 선행 PER-02 · CAD-05 |
| 접점 #447 R1 | CAD-14 | UIC 에서 이관 (UIC-c30 → CAD-c46) |
| 접점 #489 | CAD-11 | DEV 에서 이관 (DEV-c24 → CAD-c48) · UIC-c57 → CAD-c47 |
| 접점 #463 | CAD-07 | EXE 에서 이관 (EXE-c23 · EXE-c44 → CAD-c50 · c49) — 규약은 EXE-07 |
| #249 범위 밖 절 — 모달 N회 | CAD-15 (INV) | CAD-c15. 결과는 CAD-01 구독자 필터 설계 입력 |
