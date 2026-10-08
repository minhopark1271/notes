# DOE 작업 목록 (DOE Sampler — Init · Resample)

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> 기준 dev @ b08a91b3. 열린 PR 7건 중 머지 대상 6건 (#651 #652 #654 #655 #656 #658 — 05-final/decisions.md ⑩). DOE 항목과 파일이 겹치는 것: #652(DashDoeSampler.cpp/.h · DashProject.cpp · DashMainWindow.cpp · DashManager.cpp/.h · DashJobRunnerAnsysMotion.cpp · tests/CMakeLists.txt) · #651(DashProject.cpp/.h · DashMainWindow.cpp · DashAnalysisLauncherConfig.cpp/.h · TestAnalysisLauncherConfig.cpp · tests/CMakeLists.txt) · #654(DashMainWindow.cpp · DashManager.cpp · tests/CMakeLists.txt) · #655(DashMainWindow.cpp · tests/CMakeLists.txt). #656 · #658 은 DOE 변경 파일과 교집합 0 — 선행·충돌 없음 (2차 반영 판정, 01-sources/open_prs.md 파일 목록 대조).
> PR #530 은 머지하지 않는다 (C-2 결정 ② — base 가 스쿼시돼 dev 머지 불가). 공통부는 PER-07 이 다시 올리고 T27 홉 기록부는 DOE-16 이 dev 파일명 기준으로 재작성한다. 따라서 #530 은 충돌 대상이 아니다.

> #615 번호·기본 참조·자동 선택의 후속 개정은 팀 논의용 계획이다. 아래 기존 동작 제안은 확정된 setId 출처 계약과 구분하고 자동 선택 여부는 별도 결정한다.

### DOE-02 · Resample 의 Reference Set 기본값을 직전 Set 으로 하고 DOE Table 없는 Set 을 후보에서 뺀다
- 종류: PR | 규모: S | 태그: D · feature
- 목표: Reference Set 콤보 후보를 "DOE Table(samples)이 있는 다른 DoeSampler Set" 으로 좁히고, 기본 선택을 `Resample(N-1)`(N=1 이면 `Init`)로 한다. 사용자는 바꿀 수 있다.
- 완료 기준: `Resample2` 진입 시 콤보 기본값 `DoeSampler_Resample1`, `Resample1` 은 `DoeSampler_Init` · samples 없는 Set 은 후보에 없음 · 기본값 Set 이 없으면 번호가 가장 큰 후보
- 변경 범위: model/DashDoeSampler.cpp (getAvailableReferenceSets — `DashDoeTableFile::hasDoeTableSamples` 필터) · view/DashDoeSamplerResampleWidget.cpp (refreshReferenceSetCombo) · model/preprocessor/DashDoeTableFile.cpp/.h(직전 Set 헬퍼, DOE-01 의 번호 파싱 공용)
- 선행: PRJ-33 (`ResampleN` 번호 헬퍼 — DOE 에서 이관)
- 충돌: PR #652 (DashDoeSampler.cpp) · B2 교집합: DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashDoeSamplerResampleWidget.cpp → DOE-20 UIC-20 · DashDoeTableFile.cpp → PER-02
- 흡수: #615-4 · DOE-c04
- 비고: 콤보 표기는 현행대로 `completeBaseName`(`DoeSampler_ResampleN`) 을 유지한다 — `referenceSetJsonPathFor(displayName + ".json")` 가 그 표기로 경로를 복원한다(DashDoeSamplerResampleWidget.cpp:154-168). Set 이름만 보이게 바꾸려면 경로 복원을 UserRole 로 옮기는 별건

### DOE-03 · Resample prior 가 비활성 케이스를 Launcher Cases 의 `active` 로 거른다
- 종류: PR | 규모: M | 태그: A, C · bug
- 목표: `collectReferencePoints`·`getNextIterationForReferenceSet`·`runSpaceFillingResample` 이 DOE Table 의 `samples[].active`(항상 true) 대신 `AnalysisLauncher_*.json` 의 `Launcher Cases[<DoeSamplerSet>][runKey].active` 를 읽는다. `// TODO(#615)` 2곳을 걷는다.
- 완료 기준: Launcher 에서 비활성화한 케이스가 Resample prior·iteration 계산에서 빠진다 · Launcher Set 이 없거나 기록이 없으면 전부 활성(현행과 동일) · Init 재실행(새 `tableId`) 뒤 옛 Launcher 기록은 prior 에 영향 없음 · 읽기 함수 단위 테스트 (configs 디렉터리 고정물)
- 변경 범위: model/DashDoeSampler.cpp · model/preprocessor/DashAnalysisLauncherConfig.cpp/.h(참조 DOE Set 의 active 집계 — `readCases` 재사용 + Launcher json 열거) · tests/TestAnalysisLauncherConfig.cpp
- 선행: -
- 충돌: PR #651 (DashAnalysisLauncherConfig.cpp/.h) · PR #652 (DashDoeSampler.cpp) · B2 교집합: DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashAnalysisLauncherConfig.cpp → DOE-16 LCH-16 PRE-14 PRE-15 PRE-27 PRE-32 · TestAnalysisLauncherConfig.cpp → DOE-16 LCH-16 PRE-14 PRE-15 PRE-32 · DashAnalysisLauncherConfig.h → LCH-16 PRE-15 PRE-27 PRE-32
- 흡수: #615-6 · DOE-c06
- 비고: 결정 동반 — (1) 참조 DOE Set 을 스냅샷한 Launcher Set 이 여럿이면 어느 active 를 쓰나. 제안: 하나라도 active=true 면 포함, 기록 전무면 포함(기본 true). (2) 참조 Table 의 `tableId` 와 일치하는 케이스 기록만 본다 — `active` 만 보면 Init 재실행 전에 기록된 케이스가 새 Table 의 같은 runKey 에 붙어 다른 Table 의 값을 판정에 쓴다. 판독기는 `DashLauncherRuns::isCurrentCase` + `active` 조합을 재사용한다 — `resolveDoneRuns` 는 Done + resultFiles 조건까지 들어 prior 판정엔 과하다

### DOE-05 · DOE Sampler 진입 시 `loadSettings` 를 1회로 만든다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: `setProjectDirectory`·`setSetName` 에서 `loadSettings()` 호출을 떼고, 위젯이 시그널 연결을 마친 뒤 1회만 부른다. `setProjectDirectory(path)` 의 미사용 인자를 정리한다. 설정·DV 표 복원 결과는 동일.
- 완료 기준: 트리 클릭 1회에 `DashDoeConfigManager::loadSettings` 1회 · `DashDesignVariableModel::loadFromJsons` 1회 · 표 재구축 1회 (로그로 확인) · 프로젝트 열기·Set 전환·재진입에서 purpose/method/options/선택 Set/parameterization 복원 동일 · DashDoeSamplerWidget.cpp 의 "signal might not be connected yet" 주석 소멸
- 변경 범위: model/DashDoeSampler.cpp/.h · view/DashDoeSamplerWidgetBase.cpp · view/DashDoeSamplerWidget.cpp · view/DashMainWindow.cpp (handleDoeSamplerSelectionForVariant) · model/DashProject.cpp (addDoeSampler)
- 선행: -
- 충돌: PR #652 (DashDoeSampler.cpp/.h · DashProject.cpp · DashMainWindow.cpp) · PRJ-33 · PRJ-24 · DOE-07 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · DashDoeSampler.h → DOE-08 DOE-11 DOE-12 LCH-14 · DashDoeSamplerWidget.cpp → DOE-06 DOE-09 DOE-11 DOE-13 UIC-20 · DashDoeSamplerWidgetBase.cpp → ANA-07 DOE-11 PRJ-25 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp·DashProject.cpp)
- 흡수: DOE-D1 · DOE-c10, DOE-c34 · LCH-c57(DOE-c53)
- 비고: `DashDoeSamplerWidget::populateJsonFiles` 끝의 "setModel 은 loadSettings 를 연결 전에 돌리므로 여기서도 복원" 경로도 함께 정리

### DOE-06 · Probabilistic 모드의 Min/Max 편집을 모델·DV JSON 에 되쓴다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: Probabilistic 표의 Min/Max 스핀박스와 CSV Upload 의 Min/Max 가 General 과 같이 `DashDesignVariableModel` 3·4열 → DV JSON 으로 저장된다. σ 확장값(override)은 지금처럼 샘플링에만 쓴다.
- 완료 기준: Probabilistic 에서 Min 편집 → Set 재진입 후 값 유지 · CSV Upload 의 Min/Max 가 DV JSON 에 반영 · General 모드·override 계산 불변
- 변경 범위: view/DashDoeSamplerWidget.cpp (updateTableForSamplingMode Probabilistic 분기 · applyDvTableCsv)
- 선행: -
- 충돌: DOE-13 (같은 함수) · B2 교집합: DashDoeSamplerWidget.cpp → DOE-05 DOE-09 DOE-11 UIC-20
- 흡수: DOE-D2 · DOE-c11 · LCH-c58(DOE-c54)
- 비고: Min/Max 체크 해제(쌍 미사용) 상태의 저장 규칙은 구현 시 확정 — 제안: 값은 저장, 사용 여부는 저장하지 않음(현행과 같음)

### DOE-07 · 샘플링 워커에 DV 값 스냅샷을 넘기고 결과 기록을 GUI 스레드로 옮긴다
- 종류: PR | 규모: M | 태그: B, A · refactor
- 목표: `onRunButtonClicked` 가 DV 행(name·type·min·max·cases·source·column)과 Probabilistic override 를 값 구조체로 떠서 `QtConcurrent::run` 에 넘기고, 워커는 샘플 JSON 만 반환한다. 워커 본체(스냅샷 → 샘플 JSON)는 `DashProjectManager` 비의존 TU(`model/DashDoeSampling.{h,cpp}`)로 떼고 `DashDoeSampler` 는 호출만 한다 — 지금 `runAnalysisInThread` 가 `DashProjectManager::Instance()->GetIOController()->getUserPath()` 를 부르기 때문. `saveResultsAsDvTable`(파일 쓰기)은 `onAnalysisCompleted` 에서 GUI 스레드로 돈다. `m_setIdsSnapshot` 선례를 일반화한다.
- 완료 기준: `runAnalysisInThread` 본문과 그 호출 트리에 `m_designVariableModel` 접근 0 · 새 TU 에 `DashProjectManager`·`DashIOController` 포함 0 (경로는 호출부가 인자로 준다) · `DoeSampler_{Set}.json` 쓰기가 GUI 스레드에서만 일어남 · override 는 스냅샷 행에 동봉되어 인덱스 불일치가 구조상 불가 · 5 method 의 샘플 출력 동일 · 스냅샷 입력으로 위젯 없이 도는 샘플링 단위 테스트 1건 (tests/TestDoeSampler.cpp 신규 — 새 TU 만 링크, seed 고정 5 method — #489 DOE 몫)
- 변경 범위: model/DashDoeSampling.h · model/DashDoeSampling.cpp (신규 — 샘플링 본체) · model/DashDoeSampler.cpp/.h · model/DashDoeConfigManager.cpp/.h (saveResultsAsDvTable 이 모델 포인터 대신 스냅샷을 받음) · tests/TestDoeSampler.cpp (신규) · tests/CMakeLists.txt
- 선행: -
- 충돌: PR #652 (DashDoeSampler.cpp/.h) · DOE-05 · DOE-09 · DOE-16 (`saveResultsAsDvTable` 서명) · B2 교집합: DashDoeSampler.cpp → 공유 15건(deps.md 5절) · tests/CMakeLists.txt → 공유 12건(deps.md 5절) · DashDoeSampler.h → DOE-08 DOE-11 DOE-12 LCH-14 · DashDoeConfigManager.cpp → DOE-11 DOE-17 · DashDoeConfigManager.h → DOE-11 · PR #655(tests/CMakeLists.txt) · PR #654(tests/CMakeLists.txt) · PR #651(tests/CMakeLists.txt)
- 흡수: DOE-D4 · DOE-D22(DOE 측) · DOE-c12, DOE-c14, DOE-c17 · LCH-c60(DOE-c56) · EXE-c41(DOE-D4·D22 몫, DOE-c62) · #489(DOE 몫) · DEV-c24(DOE-c63)
- 비고: 본체 분리는 테스트 가능성이 근거다 — tests/ 는 Qt Core only 소형 실행 파일이고 controller 는 `controller/async/*` 만 링크한다(tests/CMakeLists.txt:46-57). GUI 싱글턴을 끌어오는 `DashDoeSampler` 를 그대로 링크할 수 없어, 분리 없이는 #489 DOE 몫 테스트가 불가하다. 실행 모델 표준(EXE)이 Job 타입을 정하면 그 위에 올린다 — 선행으로 두지는 않는다

### DOE-08 · Purpose→Method 대응표를 한 곳에 두고 콤보가 그 표에서 채워지게 한다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `{purpose, method, options}` 정적 표 1개를 `getPurposeOptions`·`onSetButtonClicked`·생성자 기본값이 공유하고, `.ui` 의 purposeCombo 정적 항목을 지운다. 콤보가 표에서 채워지므로 "표에 없는 purpose" 분기는 구조상 사라진다.
- 완료 기준: purpose 문자열 리터럴 1곳 · 5 purpose 각각 [Set] → 현행과 같은 method/options · 표의 method 이름이 `DashDoeSamplerWidget::setupMethodData` 의 5 이름과 같아 콤보 선택이 유지된다 · `ui/DashDoeSamplerWidget.ui` purposeCombo 항목 0개
- 변경 범위: model/DashDoeSampler.cpp/.h · ui/DashDoeSamplerWidget.ui
- 선행: -
- 충돌: PR #652 (DashDoeSampler.cpp/.h) · DOE-05 · DOE-07 · B2 교집합: DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashDoeSampler.h → DOE-11 DOE-12 LCH-14
- 흡수: DOE-D3 · DOE-U5(ui 항목) · DOE-c13, DOE-c23 · LCH-c59(DOE-c55)
- 비고: method 이름 리터럴은 뷰에도 있다 — `setupMethodData` 의 5 method + options(view/DashDoeSamplerWidget.cpp:892-917). `onSetButtonClicked` 의 recommendedMethod 가 그 이름과 맞아야 콤보가 선택되므로 완료 기준에 일치 조건만 둔다. 뷰 표 자체의 통합은 별건. 표를 `DashDoeSamplerPresentationModel` 로 옮기지는 않는다 — 소비자 3곳이 모두 model 층이고 `model/` 은 `viewmodel/` 을 포함하지 않는다(현행 0건). `resampleMethodCatalog()` 선례는 소비자가 뷰 1곳인 카탈로그다

### DOE-09 · 제약식의 변수 토큰을 행 번호가 아닌 변수 이름으로 영속한다
- 종류: PR | 규모: M | 태그: A, C · bug
- 목표: 저장되는 "Constraint equation" 은 변수 이름(`displayName`, DOE Table headers 와 동일) 식이다. `v{n}` 은 입력 편의로 위젯이 커밋 시 현재 표의 Symbol→Name 으로 전개한다. 실행·Resample 의 인덱스 치환 3곳을 이름 기반으로 바꾼다.
- 완료 기준: 식 저장 후 DV 행 추가·삭제·Set 변경을 거쳐도 JSON 의 식이 같은 변수를 가리킴(`v{n}` 이 JSON 에 없음) · cases 빈 discrete 행이 있어도 치환 대상이 표와 일치 · `v1`/`v10` 접두 문제 소멸 · Resample 이 Init 제약을 그대로 적용
- 변경 범위: view/DashDoeSamplerWidget.cpp (constrainedFuncEdit 커밋 전개) · model/DashDoeSampler.cpp (runAnalysisInThread 2곳 · runSpaceFillingResample 1곳)
- 선행: -
- 충돌: DOE-07 (runAnalysisInThread) · DOE-13 · PR #652 · B2 교집합: DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashDoeSamplerWidget.cpp → DOE-05 DOE-06 DOE-11 UIC-20
- 흡수: DOE-D26 · DOE-c20 · LCH-c63(DOE-c59)
- 비고: 구 파일의 `v{n}` 식은 변환하지 않는다 — 열면 그대로 보이고 사용자가 재입력 (하위호환 분기 금지). OPT-D24 가 같은 기제 — OPT 접점

### DOE-10 · Geometry/Condition JSON 판별을 DashDoeSelection 의 파일명 규칙으로 통일한다
- 종류: PR | 규모: S | 태그: E · refactor, bug
- 목표: `DashDesignVariableModel::parseJsonFile`·`saveToJsonFiles` 의 `contains("Geometry")`/`contains("Condition")` 을 `DashDoeSelection` 의 접두 규칙(`GeometryParameter_`/`ConditionParameter_`, `DashProject::restoreExistingModules` 의 표와 동일)으로 바꾸고, 어느 접두에도 맞지 않는 파일은 경고를 남기고 건너뛴다 (조용한 `DV-Condition` 기본 제거 — CON-D8).
- 완료 기준: DOE 영역에 `contains("Geometry")`·`contains("Condition")` 0곳 · 접두 불일치 파일명으로 `loadFromJsons` 하면 변수 0건 + WARN 1줄 · 앱이 만든 파일명(`GeometryParameter_`/`ConditionParameter_`)만 있는 프로젝트에서 DV 적재·저장 결과 동일 · 접두→절 대응이 한 함수에만 있다 · 접두 규칙 단위 테스트 (tests/test_doe_selection.cpp 확장)
- 변경 범위: model/DashDesignVariableModel.h · model/DashDesignVariableModel.cpp · tests/test_doe_selection.cpp
- 선행: -
- 충돌: DOE-17 (`saveToJsonFiles` 헬퍼 이행 — 본 항목 먼저) · B2 교집합: test_doe_selection.cpp → DOE-12 DOE-16 PER-07
- 흡수: DOE-D6(DOE 잔존분) · DOE-c16 · CON-D8 · CON-c08 (CON-08 병합, B2)
- 비고: 태그에 `bug` 를 병기한 이유 — 조용한 `DV-Condition` 폴백(DashDesignVariableModel.cpp:294-300 · :437-442) 제거는 CON-D8 의 조용한 실패를 고치는 동작 변경이다. 손으로 고친 파일명이 있는 프로젝트는 변수 0건 + WARN 으로 달라지므로 "결과 동일" 조건을 앱 생성 파일명으로 한정했다. `model/DashDesignVariableModel` 소속은 B2 에서 DOE 로 확정(1-1 표). CON-08(같은 두 함수, 같은 기제)을 여기로 병합. CON·CAD 위젯이 각각 `mDesignVariableModel->setParent(this)` 로 공용 모델의 부모를 빼앗는 줄(CON-08 비고 · CON-c27)은 소유권 기제라 DOE-19 로 갈랐다. LCH 측 2곳은 이미 DashDoeSelection 사용(해소)

### DOE-11 · DOE Sampler 의 호출부 없는 함수를 지운다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: 호출부 0 인 `DashDoeSampler::isDfsxmlWithMorphing`·`getPlottingData`(+`DashDoeConfigManager::getPlottingData`)·`getUserProjectFolderPath`·`DashDoeSamplerWidgetBase::getDvTablePath`·`DashDoeSamplerWidget::refreshJsonFiles` 를 삭제한다.
- 완료 기준: 위 심볼 부재 · 빌드·테스트 통과 · #652 머지 후 재집계에서 호출부 0 함수 추가분 없음
- 변경 범위: model/DashDoeSampler.cpp/.h · model/DashDoeConfigManager.cpp/.h · view/DashDoeSamplerWidgetBase.cpp/.h · view/DashDoeSamplerWidget.cpp/.h
- 선행: PR #652 머지 (writeCaseDat·JobRunner 제거 뒤 잔여 확정)
- 충돌: DOE-05 · DOE-07 · DOE-08 · DOE-12 · B2 교집합: DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashDoeSampler.h → LCH-14 · DashDoeSamplerWidget.cpp → DOE-06 DOE-09 DOE-13 UIC-20 · DashDoeConfigManager.cpp → DOE-16 DOE-17 · DashDoeSamplerWidgetBase.cpp → ANA-07 PRJ-25 · DashDoeConfigManager.h → DOE-16 · DashDoeSamplerWidgetBase.h → PRJ-25
- 흡수: DOE-U4(DOE 측) · DOE-c21
- 비고: 파일 8개지만 삭제만 — 반나절

### DOE-12 · `extractDfsxmlMorphingInfo` 를 DashDoeSampler 인스턴스 없이 쓰는 자유 함수로 옮긴다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: `DashJobRunnerAnsysMotion.cpp` 가 헬퍼 하나를 위해 `DashDoeSampler`(#652 뒤에는 DV 모델 생성)를 임시 생성하는 역의존을 끊는다 — `DashDoeSelection` 이 이미 가진 `Morphing|{deck}|{part}` 파서 `morphingPartName`(part 만 반환, .cpp:378-395)을 `{deck, part}` 반환으로 확장해 그것을 쓰고, `DfsxmlMorphingInfo` 를 따라 옮긴다 (경로 해석은 호출부가 IOController 로). 같은 라벨 파서를 둘로 늘리지 않는다.
- 완료 기준: `DashDoeSampler::extractDfsxmlMorphingInfo`·`DfsxmlMorphingInfo` 부재 · `Morphing|` 파싱이 `DashDoeSelection` 한 함수에만 있다 · `DashJobRunnerAnsysMotion.cpp` 에 `DashDoeSampler` 포함·생성 0 · 파싱 단위 테스트
- 변경 범위: model/DashDoeSampler.cpp/.h · model/DashDoeSelection.cpp/.h · model/DashJobRunnerAnsysMotion.cpp · tests/test_doe_selection.cpp
- 선행: -
- 충돌: PR #652 (DashDoeSampler.cpp/.h · DashJobRunnerAnsysMotion.cpp) · PER-07 (DashDoeSelection.cpp/.h) · DOE-11 · B2 교집합: DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절) · DashDoeSampler.h → DOE-05 DOE-07 DOE-08 LCH-14 · DashDoeSelection.cpp → DOE-16 PER-02 · test_doe_selection.cpp → DOE-10 DOE-16 · DashDoeSelection.h → DOE-16
- 흡수: DOE-c25

### DOE-13 · Probabilistic 체크박스 쌍 연동 람다 4벌을 하나로 합친다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `updateTableForSamplingMode` 의 Min↔Max·Mean↔Std 연동 람다 4개(같은 경고 문구 4회, ~130줄)를 쌍 인자를 받는 헬퍼 1개로 바꾼다. 동작 불변.
- 완료 기준: 쌍 해제 연동·전부 해제 시 경고 후 되돌림 동작 동일 · 경고 문구 1곳 · 함수 길이 감소
- 변경 범위: view/DashDoeSamplerWidget.cpp
- 선행: -
- 충돌: DOE-06 · DOE-09 (같은 파일) · B2 교집합: DashDoeSamplerWidget.cpp → DOE-05 DOE-11 UIC-20
- 흡수: DOE-c29

### DOE-14 · DOE Table 의 `samples[]` / `rawSamples[]` 중 정본을 정한다
- 종류: DEC | 규모: S | 태그: C, A
- 목표: 두 형태는 주소 방식만 다른 게 아니라 **내용**이 다르다 — `samples[].values` 는 매핑값(discrete 인덱스→case 문자열, categorical 인덱스→범주; DashDoeConfigManager.cpp:180-230), `rawSamples` 는 샘플러 원시 출력(`cachedSamples` — 인덱스 그대로 + `key`·`partName`). 결정 대상 1순위는 "mapped vs raw 의미 차이와 역매핑 가능성(`columns`·DV cases 로 되돌릴 수 있나)" 이고, 그 다음이 정본 선택이다.
- 완료 기준: 결정 기록 — 정본 1개와 역매핑 규정, 다른 쪽의 쓰기 중단 시점, 소비자별 전환 항목(LCH·PRE·ANA)과 순서, Journal 합성 Table 처분(LCH), 구 파일 읽기 규칙(재기록 없음)
- 변경 범위: - (결정)
- 선행: -
- 충돌: -
- 흡수: DOE-D5 · DOE-c15 · LCH-c61(DOE-c57 — LCH 소비 3곳 접점)
- 비고: 소비자 — 작성자 3 (`DashDoeConfigManager::saveResultsAsDvTable:294`·`saveResampledSamples:391` · `DashJobRunnerAnsysJournal.cpp:729` 가 1샘플 Table 을 `rawSamples` 만으로 합성) · rawSamples 독자 2 (`DashAnalysisLaunchExecutor.cpp:195` "raw (un-mapped) values" 주석 · `DashJobRunnerAnsysJournal.cpp:113`) · samples 독자 8 (`DashMorphingDoeExecutor.cpp:128` · `DashJobRunner.cpp:358` 메모리 내 active 병합 · `DashAnalysisLaunchExecutor.cpp:123`·`:176` · `DashLauncherRuns.cpp:31`·`:130` · `DashDoeCasesWidget.cpp:167` · `DashDataLoader.cpp:65`·`:127` · `DashResultsAnalyzerWidget.cpp:930`) · 스냅샷(`kSnapshotKeys`)은 둘 다 운반. 양안 — (a) raw 1벌 + 읽기 시 매핑 (b) mapped 1벌 + 역매핑. 종전 제안("samples 정본 + rawSamples 쓰기 중단")은 역매핑 규정 없이는 손실이라 (b) 의 전제 조건으로 내렸다. Code-Map D5 의 "`.wbpj` 만 후자" 는 낡음. 포맷 변경이라 PER 접점

### DOE-15 · #649 를 추적 부모로 닫는다
- 종류: CLOSE | 규모: - | 태그: E
- 목표: 실작업 없는 후속 추적 부모.
- 완료 기준: 닫기 사유 — 서브이슈 8건이 모듈 항목으로 흡수됨: #615 → PRJ-33(DOE-01 이관)·DOE-02·03 / #604 #616 #639 #646 → LCH / #643 → PRE / #645 #650 → PRJ
- 변경 범위: -
- 선행: 서브이슈 전부의 항목화 (Phase B 확인)
- 충돌: -
- 흡수: #649 · DOE-c09

### DOE-16 · DOE Table에 실제 입력 출처를 기록하고 Launcher 스냅샷으로 전파한다
- 종류: PR | 규모: M | 태그: C, A · feature
- 목표: #368 공통 계약으로 생성 DOE Set의 setId, 실제 Geometry·Condition Set의 setId, 선택 정보와 deck 출처를 DOE Table에 기록한다. 현재 DOE Set의 ID를 유지하면서 기존 UI에서 상류 참조를 바꿀 수 있다. Resample은 실제 사용한 참조 Table 출처를 읽어 기록하고 `kSnapshotKeys`가 필요한 출처 필드를 스냅샷으로 운반한다.
- 완료 기준: ① Init·Resample에 실제 사용한 개별 Set·선택·deck 출처 기록 ② 입력 선택 변경만으로 기존 Table 출처 불변 ③ 재샘플링 결과 덮어쓰기 시 출처도 갱신 ④ 필수 출처 누락 Table을 이름·경로로 추론하지 않고 재생성 안내 ⑤ test_doe_selection의 기록·판독과 TestAnalysisLauncherConfig의 스냅샷 전달 검증. 기존 Set ID 발급·복원 유지.
- 변경 범위: model/DashDoeSelection.cpp/.h · model/DashDoeConfigManager.cpp/.h · model/DashDoeSampler.cpp · model/preprocessor/DashAnalysisLauncherConfig.cpp (kSnapshotKeys 출처 필드) · tests/test_doe_selection.cpp · tests/TestAnalysisLauncherConfig.cpp
- 선행: PER-07
- 충돌: DOE-03 · DOE-07 (`saveResultsAsDvTable` 서명) · DOE-17 (같은 함수) · LCH-16 · PRE-14 · PRE-15 · PRE-27 · PRE-32 (출처 판독 소비자 — 순서는 DOE-16 먼저) · B2 교집합: DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashDoeConfigManager.cpp → DOE-11 · DashDoeSelection.cpp → DOE-12 PER-02 · test_doe_selection.cpp → DOE-10 DOE-12 · DashDoeConfigManager.h → DOE-11 · DashDoeSelection.h → DOE-12 · PR #652(DashDoeSampler.cpp) · PR #651(DashAnalysisLauncherConfig.cpp·TestAnalysisLauncherConfig.cpp)
- 흡수: #368 Phase 1(T27 DOE 홉) · PM4 T27 · DOE-c31 · LCH-c35(DOE-c52) · DOE-c64 · PER-06 ①(`kSnapshotKeys` allowlist — C-2 결정 ⑤ 로 DOE 귀속)
- 비고: 조합 ID를 생성·복사하지 않는다. 런처 스냅샷 전달은 DOE-16, 소비·결과 XML 기록은 PRE-32. #615의 Resample 번호·자동 선택 규칙은 추가 개정 계획으로 남으며 이번 출처 계약만으로 확정하지 않는다. 테스트는 Qt Core로 분리 가능한 공통부·설정 왕복을 사용한다.

### DOE-17 · DOE Sampler 의 JSON 쓰기 4곳을 공용 파일 헬퍼로 이행한다
- 종류: PR | 규모: S | 태그: A · refactor
- 목표: `DashDoeConfigManager::saveResultsAsDvTable`·`saveResampledSamples`(QFile Truncate + QTextStream, 쓴 길이 미검사)와 `DashDoeSampler::saveSettings`(RMW, `open` 반환 무검사)의 직쓰기를 PER-02 의 `DashSaveSystem` 헬퍼(공용 진입점 — `writeJsonFile`, QSaveFile 원자 쓰기 + `Result` 사유)로, 선행 읽기 3곳을 `readJsonFile` 로 바꾼다. 동작 불변.
- 완료 기준: (1) model/DashDoeConfigManager.cpp · model/DashDoeSampler.cpp 의 JSON 쓰기에 `QFile` 0 (2) 쓰기 실패가 로그와 반환값으로 드러난다 (3) 수동 확인 — Set 저장 → 재진입 → 재저장 뒤 `DoeSampler_<Set>.json` 바이트 동일
- 변경 범위: model/DashDoeConfigManager.cpp · model/DashDoeSampler.cpp · model/DashDesignVariableModel.cpp (`saveToJsonFiles` — 소속 DOE 확정분)
- 선행: PER-02 (헬퍼) · DOE-10 (`saveToJsonFiles` 절 판정 변경을 먼저)
- 충돌: DOE-05 (`saveSettings`·`loadSettings`) · DOE-07 (`saveResultsAsDvTable`) · DOE-16 · DOE-10 (`saveToJsonFiles`) · PR #652 (DashDoeSampler.cpp) · B2 교집합: DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashDoeConfigManager.cpp → DOE-11
- 흡수: #479(DOE 몫) · #478(DOE 몫) · #480(DOE 몫 — 버전 키는 헬퍼 경유로 자동, PER-04) · PER-c25(DOE-c61) · PER-c22(`DashDesignVariableModel::saveToJsonFiles` 몫 — B2 소속 결정, MOR-22 비고 참조)
- 비고: (3) 을 자동 테스트로 두지 않은 근거 — 쓰기 경로가 `DashDoeConfigManager`·`DashDoeSampler` 본체이고 둘 다 `DashProjectManager` 싱글턴에 의존해 Qt Core only 인 tests/ 에 링크되지 않는다(model/DashDoeConfigManager.cpp:5-6 · DashDoeSampler.cpp:711-724 · tests/CMakeLists.txt:46-57). 헬퍼 치환은 본체를 쪼갤 사유가 아니므로 PER-05 픽스처 대신 수동 확인으로 낮춘다. `선행: PER-05` 는 제거 — 게이트는 선행이 아니다(PER 검토 #9). 읽기 측 사본 2곳(`DashDoeSampler.cpp:28-40` 익명 `loadJsonRoot` — Resample 경로 입구 · `DashDoeConfigManager::loadSettings:59`)도 같이 이행한다 — PER-c03 ⑦⑧ 에 그 2곳이 올라 있고(2차 확인) 치환 몫은 본 항목이다. `saveToJsonFiles` 는 DV JSON 2종(Geometry·Condition)을 전체 재기록 — 헬퍼 치환만, 절 판정은 DOE-10. DOE Table 전체 재기록 2곳은 유지 — 기존 tableId는 실행 스냅샷 식별로 유지하고 출처 계약은 PER-06·PER-07을 따른다. `saveDoeToCsv` 는 JSON 이 아니라 대상 밖

### DOE-18 · `Selected Design Variables` 를 SI-4(setId + name 병기) 로 통일할지 정한다
- 종류: DEC | 규모: S | 태그: C
- 목표: `DashDoeSelection::writeSelectedSets` 는 `{set: 이름}` 만 쓰고, 같은 파일의 `parameterization`(T20)·`columns` 는 setId + `name` 병기(SI-4)다. 발화 조건 중 Set rename 은 Geometry 고정명·Condition 참조파일명 고정으로 소멸했으나 **동명 재생성**(Condition Set 삭제 후 같은 reference file 로 재생성 = 같은 이름·새 setId)은 남아 있다 — PM4 T29 가 이를 검증 항목으로 명시한다. (a) 현행 유지 — `Selected Design Variables` 는 편집 상태(선택)라 동명 재생성 뒤 새 Set 을 가리키는 것이 의도이고, 동결 기록은 `parameterization`·`columns` 가 setId 로 든다 (b) SI-4 통일 — `writeSelectedSets`/`readSelectedSets` 한 쌍 수정, 구 기록은 round-trip(재기록 없음) 중 택한다.
- 완료 기준: 결정 기록 — (b) 면 후속 S PR 범위 (model/DashDoeSelection.cpp · tests/test_doe_selection.cpp; 소비 5곳은 `readSelectedSets` 경유라 무변경)
- 변경 범위: (결정만)
- 선행: -
- 충돌: PER-07 (DashDoeSelection) · DOE-16
- 흡수: #562-3 · #443 SI-4(DOE 몫) · PRJ-c09(DOE-c60)
- 비고: PRJ 가 "통일 여부는 DOE 결정" 으로 넘김. 판단 재료 — 발화 조건은 rename 소멸 뒤에도 동명 재생성이 남는다(Project-Manifest-4-Ticket-Slicing.md:222 · DashDoeSelection.cpp:122-135 · DashProject.cpp:463). (a) 의 "선택은 편집 상태" 논거가 서면 DEC 가 닫히고 최소 변경이 된다

### DOE-19 · 공용 `DashDesignVariableModel` 의 소유자를 DashManager 로 못박고 소비자의 `setParent` 탈취를 없앤다
- 종류: PR | 규모: S | 태그: E · bug
- 목표: `DashManager` 가 부모 없이 만드는 공용 DV 모델(`DashManager.cpp:81`)에 소유자를 준다 — `new DashDesignVariableModel(this)`. 그 모델을 받아 쓰는 CON·CAD 위젯이 `setParent(this)` 로 소유권을 가져가는 2줄(`DashConditionParameterizationWidget.cpp:331` · `DashGeometryParameterCADWidget.cpp:310`)을 지운다. 먼저 파괴되는 위젯이 공용 인스턴스를 지워 남은 소비자와 `GetDesignVariableModel()` 이 대상 잃은 포인터를 드는 상태가 사라진다.
- 완료 기준: 공용 DV 모델 생성에 부모 있음 · 코드베이스에 `mDesignVariableModel->setParent` 0곳 · CON 위젯을 닫은 뒤 CAD 위젯에서 DV 적재·저장 정상 (수동) · 앱 종료 시 모델 파괴 1회
- 변경 범위: controller/DashManager.cpp · view/DashConditionParameterizationWidget.cpp · view/DashGeometryParameterCADWidget.cpp
- 선행: -
- 충돌: CON-03 · CON-05 · CON-06 · CON-07 · CON-12 · CAD-01 · CAD-03 · CAD-04 · CAD-05 · CAD-06 · CAD-07 · CAD-09 · CAD-13 · UIC-19 · PRJ-03 · PRJ-04 · PRJ-06 · PRJ-14 · EXE-06 · REN-07 · PR #652 · PR #654 (controller/DashManager.cpp — 둘 다 DV 모델 줄도 dtor 도 건드리지 않아 순서 무관) · B2 교집합: DashConditionParameterizationWidget.cpp → UIC-20
- 흡수: CON-c27 · Code-Map CON 3-1 · DOE-c66
- 비고: 소유자를 `DashManager` 로 둔 근거 — 모델은 ctor 에서 1회 생성되고 CON·CAD 두 위젯이 같은 인스턴스를 공유한다(`GetDesignVariableModel` 소비 6곳). 위젯 쪽으로 소유를 몰면 다른 위젯이 수명을 잃으므로 공유 소유자가 쥐는 쪽만 성립한다. dtor(`:103-123`)는 데몬 4종만 만지므로 부모를 주면 QObject 가 지운다. MOR(`DashGeometryParameterWidget.cpp:105`)·DOE(`DashDoeSampler.cpp:142`)는 각자 부모를 둔 별 인스턴스라 무관. DOE 귀속 근거 — `DashDesignVariableModel` 소속이 B2 에서 DOE(1-1 표). JSON 접두 판정(DOE-10)과는 다른 개념이라 나눴다. CON·CAD 접점

### DOE-20 · Resample 의 Search Min/Max 셀에 숫자·범위 검증을 둔다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: `mResampleDvTable` 의 Search Min(4열)·Max(5열) 을 아이템 델리게이트(선례 `view/delegate/DashFeConditionValueDelegate.cpp:102-109` — `QDoubleValidator`)로 받아 비수치 입력을 편집 중에 막고, 참조 Set 의 설계 공간(`getDesignSpaceRange`) 밖 값과 min ≥ max 를 커밋 때 되돌리며 허용 범위를 셀 툴팁으로 보인다. 지금은 `toDouble` 실패·역전 쌍이 조용히 ROI override 에서 빠져 전 설계 공간으로 되돌아간다(`onResampleRunClicked:298-309` 의 `if (okMin && okMax)`).
- 완료 기준: 비수치 입력이 셀에 커밋되지 않는다 · min ≥ max 또는 설계 공간 밖 값은 되돌려지고 사유 통지 1회 · 셀 툴팁에 참조 Set 의 `[min, max]` 표시 · prefill 과 override 전달 동작 불변 (파싱 가드 `okMin && okMax` 는 남긴다)
- 변경 범위: view/delegate/DashDoeSearchRangeDelegate.h · view/delegate/DashDoeSearchRangeDelegate.cpp (신규) · view/DashDoeSamplerResampleWidget.cpp
- 선행: -
- 충돌: DOE-02 (같은 파일 — 콤보·prefill 인접) · B2 교집합: DashDoeSamplerResampleWidget.cpp → UIC-20
- 흡수: #487(표 셀 DOE 2곳) · UIC-c41(b) · DOE-c65
- 비고: UIC-21 의 `applyNumericRange(QLineEdit*, …)` 는 쓸 수 없다 — 표 셀은 `QTableWidgetItem::text()` 파싱이라 델리게이트가 필요한 다른 기제다(UIC 검토 #10 이 `범위밖` 으로 갈라 DOE 로 넘김). 델리게이트를 공용(`view/common`)으로 빼지 않은 이유 — 지금 사용처가 이 표 하나고, 같은 기제의 OPT 몫 1곳이 자기 항목으로 서면 그때 UIC 로 올린다(단일 사용처 추상화 금지). 허용 범위의 출처는 prefill 과 같은 `getDesignSpaceRange`(참조 Table 의 min/max, `populateDvTableFromReferenceSet:226-241`) 라 셀 UserRole 에 실어 전달한다

## 대응표

| 원천 | 항목 | 비고 |
|---|---|---|
| #615 | → PRJ-33 (#615-1·2·3, DOE-01 이관) · DOE-02 · DOE-03 | #615-3 Rename 불가·#615-5 Launcher 의 DOE Table 선택은 해소됨(c03·c05). DEV 전용 유지는 PRJ-24 전제. DOE-01 은 변경 파일이 PRJ 소유라 B2 에서 PRJ-33 으로 이관 |
| #649 | DOE-15 | CLOSE (추적 부모) |
| #502 (접점) | 항목 없음 | 범위밖 → LCH (Deferred). DOE 쪽 요구 없음 — c32 |
| #443 (접점) | 항목 없음 | DOE 쪽 해소됨 (#520 · #533) — c33 |
| DOE-D1 | DOE-05 | |
| DOE-D2 | DOE-06 · DOE-07 | 되쓰기 → 06, 위치 첨자 → 07 |
| DOE-D3 | DOE-08 | |
| DOE-D4 | DOE-07 | |
| DOE-D5 | DOE-14 | DEC |
| DOE-D6 | DOE-10 | DOE 잔존분. LCH 측 2곳은 해소됨 |
| DOE-D7 | 항목 없음 | 범위밖 → LCH (c36) |
| DOE-D8 | 항목 없음 | 범위밖 → LCH (c37) |
| DOE-D9 | 항목 없음 | 범위밖 → LCH (c38) |
| DOE-D10 | 항목 없음 | 범위밖 → LCH (c39) |
| DOE-D11 | 항목 없음 | 범위밖 → LCH (c40) |
| DOE-D12 | 항목 없음 | 범위밖 → LCH (c41, PR #651) |
| DOE-D13 | 항목 없음 | 범위밖 → LCH (c42) |
| DOE-D14 | 항목 없음 | 범위밖 → LCH (c43) |
| DOE-D15 | 항목 없음 | 범위밖 → LCH (c44) |
| DOE-D16 | 항목 없음 | 범위밖 → LCH (c45) |
| DOE-D17 | 항목 없음 | 범위밖 → LCH (c46, MOR 접점) |
| DOE-D18 | 항목 없음 | 범위밖 → LCH (c47) |
| DOE-D19 | 항목 없음 | 범위밖 → LCH (c48) |
| DOE-D21 | 항목 없음 | 범위밖 → LCH (c49) |
| DOE-D22 | DOE-07 | DOE 측(워커 파일 쓰기)만. Launcher 콜백 측은 범위밖 → LCH (c18) |
| DOE-D23 | 항목 없음 | 범위밖 → LCH (c50) |
| DOE-D24 | 항목 없음 | 범위밖 → LCH (c35). dev 에서 Direct 는 JSON 기록 없음 — 해소 판정은 LCH |
| DOE-D25 | → PRJ-24 | DOE-04 병합(B2) — 같은 파일·기제. DOE-c19 · LCH-c62(DOE-c58) 도 PRJ-24 |
| DOE-D26 | DOE-09 | |
| DOE-U2 | 항목 없음 | 범위밖 → LCH (c35, PR #652 가 수정) |
| DOE-U3 | 항목 없음 | 범위밖 → LCH (c51) |
| DOE-U4 | DOE-11 | DOE 측. LCH 측 4종은 범위밖 (c22). createRunsFolders 2종은 해소됨 |
| DOE-U5 | DOE-08 | ui 항목. connLog·firstPartName 은 범위밖 → LCH (c24) |
| 코드 실측 c25 | DOE-12 | |
| 코드 실측 c29 | DOE-13 | |
| 코드 실측 c26 · c27 | 항목 없음 | 범위밖 → UIC (#482 · #508), 건수만 기록 |
| 코드 실측 c28 | 항목 없음 | 미확인 — 실측 전 |
| Project-Manifest-4 T24 (c30) | 항목 없음 | 해소됨 |
| Project-Manifest-4 T27 · #368 Phase 1 (c31 · c52) | DOE-16 | ← LCH-c35 되돌림(B1). 공통부는 PER-06·07, #368 주 모듈 PER. #530 은 머지하지 않고 T27 기록부를 DOE-16 이 재작성 (C-2 결정 ②) |
| #479 · #478 · #480 (DOE 몫) | DOE-17 | ← PER-c25(DOE-c61) · PER-c22(`saveToJsonFiles` 몫, B2 소속 결정). 헬퍼는 PER-02 |
| CON-D8 · CON-c08 (CON-08 병합) | DOE-10 | `DashDesignVariableModel` 소속 DOE (B2) — 같은 두 함수 같은 기제 |
| #562-3 · #443 SI-4 (DOE 몫) | DOE-18 (DEC) | ← PRJ-c09(DOE-c60) |
| #489 (DOE 몫) | DOE-07 | ← DEV-c24(DOE-c63) — 스냅샷화 뒤 샘플링 테스트 |
| LCH-c57 ~ c63 (DOE-D1·D2·D3·D4·D5·D25·D26) | DOE-05 · 06/07 · 08 · 07 · 14 · PRJ-24 · 09 | DOE-c53~c59 — 기존 항목이 덮음 |
| EXE-c41 (DOE-D4·D22 몫) | DOE-07 | DOE-c62 |
| PER-06 ① (`kSnapshotKeys` allowlist, c64) | DOE-16 | C-2 결정 ⑤ — 기록 측 한 모듈에 귀속. 읽는 쪽 PRE-32 는 보류: PRE 몫 |
| #487 (표 셀 DOE 2곳) | DOE-20 | ← UIC-c41(b)(DOE-c65) — 델리게이트 기제라 UIC-21 의 `QLineEdit` 헬퍼 적용 불가. OPT 몫 1곳은 OPT |
| Code-Map CON 3-1 · CON-c27 | DOE-19 | ← CON 이 넘긴 공용 DV 모델 소유권(DOE-c66). `DashDesignVariableModel` 소속 DOE(B2) · CON·CAD 접점 |
