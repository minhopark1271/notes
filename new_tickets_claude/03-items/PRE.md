# PRE 작업 목록

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> 기준 dev @ b08a91b3. 원천·판정은 02-claims/PRE.md. 작성기(DashResultXmlWriter.cpp) 항목은 PRE-07 → PRE-20 → PRE-06 → PRE-10 → PRE-04 순으로 하면 같은 함수를 한 번씩만 지난다. 열린 PR 7건 중 **머지 대상 6건**(#651 #652 #654 #655 #656 #658) — #530 은 재업로드 노선이라 머지하지 않는다(C-2 결정 ② · ⑩). #368 공통부는 PER-07 이 dev 기준으로 다시 올리고 T21 홉은 PRE-32 가 흡수하므로, #368 관련 충돌은 그 두 항목과의 충돌로만 센다.
>
> **PR #656**(#433 후속)이 PRE-03 을 전부 구현해 PRE-03 은 CLOSE 로 바뀌었고, PRE-04 의 TimeSteps 원문 파싱 모으기도 선반영됐다. **PR #658**(preprocessor v3 수용, draft)은 카탈로그 sub-result 발행 · 이름 기반 배열 조회(`responseArray`) · `modeShapeLeaf` · 질의의 `sub_result` 적재를 이미 고쳐 PRE-06 · PRE-10 · PRE-17 · PRE-18 의 전제를 바꾸고, 결과 XML 에 `quantity`·`unit`·`component_labels` 속성을 더해 PRE-29 의 포맷 기준선을 옮긴다 — 실측 기준까지 더해 PRE-01 · 06 · 10 · 17 · 18 · 29 여섯 항목이 #658 을 선행(PRE-29 는 선행 + 결정 입력)으로 둔다. #656 은 PRE-02 · PRE-04 의 선행이다. 단순 동시 수술은 D-1 의 `build_deps.py --apply` 가 충돌란에 채운다.

### PRE-01 · #433 8단계 실측 — fe-safe ODB · 모달 `.rst`/`.odb` · Motion `.dfr` 을 Level 3 테스트에 더한다
- 종류: INV | 규모: S | 태그: F · docs
- 목표: `TestRealResultFiles` 에 fe-safe 2스텝 ODB(#493 누락 시나리오)·모달 `.rst`·모달 `.odb`·Motion `.dfr` 케이스를 추가하고 실측 결과(PASS/SKIP·발견 결함)를 #433 본문 형식으로 기록한다
- 완료 기준: 실측 결과 — 케이스 4종의 리더·미리보기·배치 경계 기록. 파일이 없는 케이스는 QSKIP 사유로 남긴다
- 변경 범위: tests/TestRealResultFiles.cpp · `DASH_TEST_RESOURCES` 리소스
- 선행: PR #658 (preprocessor v3 — 실측 기준이 v3 의 엄격한 오류 정책이어야 한다. #658 본문도 실파일 테스트를 SKIP 하고 QC 로 넘겼다. v2 에서 잰 경계는 머지 뒤 무효)
- 충돌: B2 교집합: TestRealResultFiles.cpp → PRE-06 PRE-09 PRE-16 PRE-17
- 흡수: #433-8 · #637(확인 방법) · PRE-c01, PRE-c02
- 비고: fe-safe 는 Abaqus ≥ 2023, Motion 은 `.dfr` 파일이 필요해 미확인. 실측에서 나온 결함은 별도 항목으로 뺀다

### PRE-02 · #433 종료 검토 — 완료 기준 미체크 항목을 점검하고 #454 경계를 기록한다
- 종류: INV | 규모: S | 태그: E · docs
- 목표: 완료 기준의 미체크 6항(책임 분리·기존 클래스 재사용·동작/저장 결과 비교·빌드·회귀·새 세션 검토·증분 통합)을 현재 dev 에서 확인하고, #454 가 시작할 경계(`processResults`·`DashResultProcessor`·`DashReaderSession::Work`)를 본문에 기록한 뒤 #433 을 닫는다
- 완료 기준: 검토 기록 — 분해 전후 표 구성·응답 조회·미리보기·결과 XML·설정 JSON 비교 결과, 새 세션 검토 반영 여부, #433 종료. **실측 파일이 없는 케이스(PRE-01 의 QSKIP 분)는 "미확인 — 파일 부재" 로 기록하고 종료를 막지 않는다**
- 변경 범위: 문서(이슈 본문·위키)만
- 선행: PRE-01, PRE-04, PRE-07, PRE-20 (9단계 잔여) · PR #656 (#433 후속 — 이것이 머지돼야 9단계 질의 직렬화·모달 Name·TimeSteps 파싱이 끝난다)
- 충돌: -
- 흡수: #433 완료 기준 · #454 선행 · PRE-c03, PRE-c13
- 비고: 열린 #433 PR 은 #656(`refactor/433-launcher-common`) 하나이고 `refactor/433-*` 나머지 6개는 통합됐다. 9단계 잔여가 끝나기 전에는 "같은 책임의 병렬 구현을 추가하지 않는다" 를 체크할 수 없다. 이 항목은 문서 작업이라 PRE-23(#454) 의 선행이 아니다 — #433·#454 의 "같은 파일 동시 수술 금지" 는 코드 항목(PRE-04·07) 사이의 제약이다

### PRE-03 · 런처·초기화기의 질의 직렬화와 모달 Name 리터럴 공용화 — PR #656 이 구현
- 종류: CLOSE | 규모: S | 태그: E · refactor
- 목표: PR #656(`refactor/433-launcher-common`, #433)이 이 항목 전부를 구현했다 — `toJson(Compact)` 4곳(`DashAnalysisLauncher.cpp` :704 :712 :1412 · `DashResponseInitializer.cpp` :185)이 `DashResultQuery::compact` 로, 모달 Name 리터럴 2곳(:638-641 · :759-769)이 `DashResultQuery::modalNames()` 로 바뀌고 쓰지 않는 `modeNames` 가 삭제됐다. 덤으로 GetTimeSteps 원문 파싱 3곳도 신설 `DashResultKeys::timeStepsOf` 로 모였다
- 완료 기준: 닫기 사유 — PR #656 머지. 잔여 1줄(`DashResultKeys.cpp:29` `firstTimeStepQuery` → `DashResultQuery::compact`)은 PRE-04 가 흡수한다 — #656 이 안 건드린 유일한 PRE 영역 직렬화 지점이고, 한 줄짜리 PR 로 세우지 않는다(00-plan 1-2)
- 변경 범위: - (PR #656: model/DashAnalysisLauncher.{h,cpp} · model/preprocessor/DashResponseInitializer.cpp · DashResultKeys.{h,cpp} · DashResultXmlWriter.cpp · tests)
- 선행: -
- 충돌: B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashResultXmlWriter.cpp → 공유 10건(deps.md 5절) · DashAnalysisLauncher.h → LCH-33 PRE-08 PRE-16 PRE-23 PRE-24 PRE-32 PRJ-22 · DashResponseInitializer.cpp → PRE-04 PRE-07 · DashResultKeys.cpp → PRE-04 PRE-19 · DashResultKeys.h → PRE-04 · PR #658(DashAnalysisLauncher.cpp·DashResultKeys.cpp·DashResultKeys.h·DashResultXmlWriter.cpp) · PR #656(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h·DashResponseInitializer.cpp·DashResultKeys.cpp·DashResultKeys.h·DashResultXmlWriter.cpp) · PR #652(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h) · PR #651(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h)
- 흡수: #433-9 · PRE-c08, PRE-c09
- 비고: 고객사 규칙 사본 9곳(`LGE_SpringRule.cpp` 2 · `ILJIN_TensionlinkRule.cpp` 7)과 어댑터 래퍼의 자체 헬퍼(`wrapper/LegacyJsonPreprocessor.cpp:52`)는 #656 도 손대지 않았고 앞으로도 손대지 않는다

### PRE-04 · 요청→시점 해석을 `DashResultBatch::timeOf` 결과 전달로 단일화한다
- 종류: PR | 규모: L | 태그: E · refactor
- 목표: 런처가 구한 `TimeRef` 를 `DashResultProcessor::ProcessContext` → `appendSample` → `writeFieldOutputToXml` 과 `DashResponseInitializer` 에 넘기고, 처리기·작성기·초기화기의 loadStep/state 파싱 사본(처리기 1 · 작성기 3 · 초기화기 2)을 지운다. GetTimeSteps 원문 파싱(런처 2 · 작성기 1)은 PR #656 이 `DashResultKeys::timeStepsOf` 로 이미 모았으므로, 같은 파일의 잔여 직렬화 1줄(`DashResultKeys.cpp:29` `firstTimeStepQuery` → `DashResultQuery::compact`, PRE-03 잔여)만 함께 치운다
- 완료 기준: 처리기·작성기·초기화기에 `loadStep`·`State `·`Mode\s+` 파싱 0 · `TestResultProcessor`·`TestResultXmlWriter`·`TestResponseInitializer` 통과 · 생성 XML 의 파일명·step/substep 동일
- 변경 범위: model/preprocessor/DashResultProcessor.{h,cpp} · DashResultXmlWriter.{h,cpp} · DashResponseInitializer.{h,cpp} · DashResultKeys.{h,cpp} · model/DashAnalysisLauncher.cpp · tests
- 선행: PRE-07 (같은 시그니처에 플래그를 먼저 싣는다), PRE-05 · PR #656 (`timeStepsOf` 선반영 — 런처·초기화기·작성기의 같은 네 자리를 이미 고쳤다)
- 충돌: PRE-06, PRE-10, PRE-20 (작성기 같은 함수) · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashResultXmlWriter.cpp → 공유 10건(deps.md 5절) · DashResultXmlWriter.h → PRE-22 PRE-30 PRE-31 PRE-32 · DashResponseInitializer.cpp → PRE-03 · DashResultKeys.cpp → PRE-03 PRE-19 · DashResultProcessor.cpp → PRE-23 · DashResultProcessor.h → PRE-23 · DashResultKeys.h → PRE-03 · PR #658(DashAnalysisLauncher.cpp·DashResultKeys.cpp·DashResultKeys.h·DashResultXmlWriter.cpp) · PR #652(DashAnalysisLauncher.cpp) · PR #651(DashAnalysisLauncher.cpp)
- 흡수: #433-9 · PRE-c06, PRE-c05(잔여 — LGE 규칙 1곳만 남고 손대지 않는다), PRE-c09(잔여 `DashResultKeys.cpp:29`)
- 비고: L 사유 — 한 개념(시점 해석을 한 출처로)인데 사본이 처리기·작성기·초기화기·키 파서 9파일에 흩어져 있다. GetTimeSteps 원문 파싱 모으기가 #656 으로 빠져 규모는 L 하단이지만 대상 파일 수는 그대로다. `LGE_SpringRule::extractModalFrequency` 의 자체 파싱은 고객사 규칙이라 손대지 않는다. `processResults`·`DashResultProcessor` 는 #454 대상이므로 PRE-23 과 동시에 열지 않는다

### PRE-05 · 위젯이 Motion Load Step 을 "State N" 으로 넘긴다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: Add·Preview·KPI 대화상자의 Load Step 문자열 조립 3곳이 `onSelectionChanged` 와 같은 규칙(부모가 "States" 면 자식 텍스트만)을 쓴다. 조립을 한 함수로 뽑는다. `parseMotionState`·`stateOf` 테스트에 "States / State N" 거부(또는 수용) 케이스를 더한다
- 완료 기준: Motion 결과에서 State 2 Preview 가 형식 오류 없이 질의까지 간다 · State 2 를 Add 한 행의 Load Step 문자열이 `State 2` 고 요청의 `timeOf` 가 state 2 로 풀린다(`TestResultBatch`) · 테스트 통과
- 변경 범위: view/DashAnalysisLauncherWidget.{h,cpp} · tests/TestResultQuery.cpp · tests/TestResultBatch.cpp
- 선행: -
- 충돌: B2 교집합: DashAnalysisLauncherWidget.cpp → PRE-08 PRE-18 PRE-23 PRE-24 PRE-27 · DashAnalysisLauncherWidget.h → LCH-01 PRE-23 · TestResultBatch.cpp → PRE-16 · PR #658(TestResultQuery.cpp) · PR #651(DashAnalysisLauncherWidget.h)
- 흡수: #634 · PRE-c33, PRE-c34
- 비고: 해석기 쪽 수용으로 가면 5곳을 고쳐야 하므로 위젯 쪽 통일을 택했다. 실제 `.dfr` 확인은 PRE-01. "State 1·2 Add → `_1_0_`·`_2_0_` 두 파일" 은 이 항목만으로 성립하지 않는다 — 처리기·작성기의 Motion 판정 입력이 참조 파일 basename 이라 전 샘플 Missing 이고, 쓴 샘플이 0 이면 파일을 만들지 않는다(`DashAnalysisLauncher.cpp:1053`). 파일 생성 확인은 PRE-07 뒤로 미룬다

### PRE-06 · 필드 출력 질의에 `field_output_name` 을 `operator` 와 함께 싣는다
- 종류: PR | 규모: M | 태그: A · bug
- 목표: 카탈로그 항목으로 만드는 질의 전부 — 작성기 일반 경로(`result` 키 폴백 제거) · Mode Shape 루프 · 원형도 변위 탐색 · 미리보기(일반·Motion 분기에도 응답 키) · Level 3 테스트 — 에 `field_output_name` 을 싣는다. **PR #658 이 이미 한 것은 뺀다** — 배열을 이름으로 찾는 `responseArray()`(임의 `GetArray(0)` 폴백·성분 수 ≥3 선택 제거), leaf 조회를 질의 앞으로 올리기, 질의의 `sub_result` 지목, `MatchResponse` 가 둘 다 맞는 항목 우선(선택 항목이었다)
- 완료 기준: `TestResultXmlWriter`·`TestRealResultFiles` 질의에 field_output_name 포함 · operator 미발견 샘플은 Missing(#658 이 선반영한 것의 회귀 확인) · `.dfr` Preview 가 "No field output" 이 아니라 결과를 그린다(PRE-01 에서 확인)
- 변경 범위: model/preprocessor/DashResultXmlWriter.cpp · model/DashAnalysisLauncher.cpp (requestVtkPreview) · tests/TestRealResultFiles.cpp · tests/TestResultXmlWriter.cpp
- 선행: PRE-05 (Motion 미리보기가 질의까지 가야 확인된다), PRE-07 · PR #658 (같은 세 경로를 이름 조회로 이미 고쳤다 — 질의 적재만 남는다)
- 충돌: PRE-10, PRE-20, PRE-04 · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashResultXmlWriter.cpp → 공유 10건(deps.md 5절) · TestRealResultFiles.cpp → PRE-01 PRE-09 PRE-16 PRE-17 · TestResultXmlWriter.cpp → PRE-31 PRE-32 · PR #656(DashAnalysisLauncher.cpp·DashResultXmlWriter.cpp·TestResultXmlWriter.cpp) · PR #652(DashAnalysisLauncher.cpp) · PR #651(DashAnalysisLauncher.cpp)
- 흡수: #630 · PRE-c24(잔여 — field_output_name 적재·result 폴백), PRE-c26(질의 측), PRE-c27, PRE-c28, PRE-c29 · PRE-c25·PRE-c30 은 PR #658 로 해소됨
- 비고: ILJIN 규칙(배열 이름 = operator)은 손대지 않는다. Function Expression 의 배열 조회는 #658 이 `responseArray()` 로 바꿨으므로 질의 적재만 본다. Mode Shape 의 변위 항목 선택 규칙은 PRE-10

### PRE-07 · 해석 종류(Motion·Modal) 플래그를 Load 에서 정해 처리기·작성기·초기화기에 넘긴다
- 종류: PR | 규모: M | 태그: A, C · bug
- 목표: `readerSession_.solverType()=="AnsysMotion"` 과 `loaded_.isModal` 을 `ProcessContext`·`appendSample`·`writeFieldOutputToXml`·`DashResponseInitializer::initialize` 의 인자로 넘기고, `currentAnalysisType=="Dynamic"`(처리기 1 · 작성기 2)·`selectedType=="Dynamic"`(초기화기) 비교를 지운다. `currentAnalysisType` 인자는 Motion 플래그로 대체하고 처리기·작성기·초기화기 시그니처에서 제거한다
- 완료 기준: Motion 배치가 `state_id` 질의를 만든다 — `TestResultProcessor`·`TestResultXmlWriter` 에 Motion 컨텍스트 케이스 추가 · 처리기·작성기·초기화기에 `"Dynamic"` 문자열 비교 0 · 정적·모달 XML 결과 불변
- 변경 범위: model/preprocessor/DashResultProcessor.{h,cpp} · DashResultXmlWriter.{h,cpp} · DashResponseInitializer.{h,cpp} · model/DashAnalysisLauncher.cpp · tests
- 선행: -
- 충돌: PRE-04, PRE-06, PRE-20 · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashResultXmlWriter.cpp → 공유 10건(deps.md 5절) · DashResultXmlWriter.h → PRE-22 PRE-30 PRE-31 PRE-32 · DashResponseInitializer.cpp → PRE-03 · DashResultProcessor.cpp → PRE-23 · DashResultProcessor.h → PRE-23 · PR #658(DashAnalysisLauncher.cpp·DashResultXmlWriter.cpp) · PR #656(DashAnalysisLauncher.cpp·DashResponseInitializer.cpp·DashResultXmlWriter.cpp) · PR #652(DashAnalysisLauncher.cpp) · PR #651(DashAnalysisLauncher.cpp)
- 흡수: #433-9(Motion 판정 통일) · #635(판정 전달) · PRE-c10, PRE-c36, PRE-c38
- 비고: #617 이후 `m_inputs.analysisType` 이 참조 파일 basename 이라 Motion 배치는 코드 경로상 전 샘플 Missing 이다(PRE-c38). `.dfr` 실측은 PRE-01. `contains("modal")` 판정은 입력이 통제되므로 그대로 둔다. `writeModelInfoToXml` 은 받은 `currentAnalysisType` 을 쓰지 않아(태그 기록 0, `DashResultXmlWriter.cpp:1173-1214`) 남길 이유가 없다 — model_info 에 들어갈 것은 PRE-32 의 실제 출처 기록이고 해석 이름이 아니다

### PRE-08 · `ExtractedKeys::isAnsysMotion` 을 `hasFunctionExpression` 으로 이름을 바로잡는다
- 종류: PR | 규모: S | 태그: C, E · refactor
- 목표: 런처가 싣는 값(함수식 존재)과 위젯이 읽는 의미(Load Step 트리 초기 비활성)에 맞게 필드 이름과 주석을 바꾼다
- 완료 기준: `ExtractedKeys` 에 `isAnsysMotion` 없음 · 위젯 동작 불변(Function Expression 있는 결과에서 트리 초기 비활성)
- 변경 범위: model/preprocessor/DashResultTypes.h · model/DashAnalysisLauncher.{h,cpp} · view/DashAnalysisLauncherWidget.cpp
- 선행: - (이름 정정뿐이라 PRE-07 과 순서 무관 — 같은 파일이라 충돌만 본다)
- 충돌: PRE-07 (같은 파일) · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashAnalysisLauncher.h → LCH-33 PRE-03 PRE-16 PRE-23 PRE-24 PRE-32 PRJ-22 · DashAnalysisLauncherWidget.cpp → PRE-05 PRE-18 PRE-23 PRE-24 PRE-27 · DashResultTypes.h → PRE-16 · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h) · PR #652(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h) · PR #651(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h)
- 흡수: PRE-D5 · PRE-c66

### PRE-09 · Abaqus 모달 ODB 판별 — `.odb` 도 `GetAnalysisInfo` 로 Static/Modal 을 가를지 실측한다
- 종류: INV | 규모: S | 태그: A · feature
- 목표: 모달 ODB 에서 어댑터 `GetAnalysisInfo` 가 `MODAL` 을 돌려주는지 확인하고, 그렇다면 `.rst` 판별 블록을 `.odb` 에도 적용하는 PR 로 잇는다
- 완료 기준: 실측 결과 — 모달 ODB 의 analysis 값 · 적용 시 `loadPreprocessInputs` 의 판별 범위 결정
- 변경 범위: (PR 시) model/DashAnalysisLauncher.cpp (loadPreprocessInputs) · tests/TestRealResultFiles.cpp
- 선행: PRE-01 (모달 ODB 파일)
- 충돌: B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · TestRealResultFiles.cpp → PRE-06 PRE-16 PRE-17 · PR #658(DashAnalysisLauncher.cpp·TestRealResultFiles.cpp) · PR #656(DashAnalysisLauncher.cpp) · PR #652(DashAnalysisLauncher.cpp) · PR #651(DashAnalysisLauncher.cpp)
- 흡수: #637(Abaqus 모달 경로) · PRE-D4(잔여) · PRE-c44
- 비고: 지금은 `.odb` 가 SupportedResults.defaultType("Static") 으로 고정돼 Abaqus 모달 경로가 없다

### PRE-10 · Mode Shape 의 변위 항목을 한 곳에서 고른다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: PR #658 이 고친 `DashResultQuery::modeShapeLeaf`(`Displacement`·`U` 두 키만 보고 magnitude 를 `Magnitude` sub-result 로 찾는다)를 변위 항목의 유일한 선택 지점으로 두고, 작성기의 `availableResponses["Displacement"]` 고정 키 2곳(Mode Shape 루프 :384-392 · 원형도 변위 탐색 :984-985)을 같은 함수로 바꾼다. `modeShapeLeaf` 가 못 찾으면 빈 객체를 돌려주고 호출부가 조용히 지나가는 경로를 오류로 끝낸다(다른 항목 대체 없음)
- 완료 기준: Ansys 모달 `.rst` → Mode 1 → `Mode Shape / x` Preview 성공(PRE-01) · Abaqus 모달 배치가 Missing 이 아니다 · 작성기에 `"Displacement"` 리터럴 0 · `TestResultQuery`(modeShapeLeaf 실패 시 오류)·`TestResultXmlWriter`(고정 키 제거) 통과
- 변경 범위: model/preprocessor/DashResultQuery.cpp · DashResultXmlWriter.cpp · tests
- 선행: PRE-06 · PR #658 (`modeShapeLeaf`·배열 이름 조회를 이미 고쳤다 — 그 위에서만 성립한다)
- 충돌: PRE-04, PRE-20 · B2 교집합: DashResultXmlWriter.cpp → 공유 10건(deps.md 5절) · DashResultQuery.cpp → PRE-18 PRE-19 · PR #656(DashResultXmlWriter.cpp)
- 흡수: #637 · PRE-c42(작성기 고정 키) · PRE-c26(배열 선택 몫은 #658) · PRE-c40·PRE-c41 은 PR #658 로 해소됨
- 비고: Ansys 도 operator 는 `U`(field_output_name 은 `Displacement`, tests/TestRealResultFiles.cpp:560). 성분 순서는 `component_labels` 로 확인한다. 미리보기 x·y·z 를 배열 성분 0·1·2 로 자르는 안은 폐기 — #658 이 어댑터에 X·Y·Z sub-result 를 복원했으므로 질의로 지목하면 된다. 표시 계층(`DashFieldPreview`·위젯)은 PRE-18 로 넘겼다

### PRE-11 · Side Force KPI 가 실패 샘플을 빼고 성분을 `component_labels` 로 고른다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `calculateMaxSideForce` 가 성공 여부를 함께 돌려주고 `processSideForceKPI` 가 실패 샘플을 건너뛴다(#573 규칙). operator 는 `Force/_` 에서, X·Y 는 `component_labels` 위치로 고른다. 쓰지 않는 `cachedTimeSteps` 인자를 정리한다
- 완료 기준: LGE 빌드에서 operator 를 못 찾는 run 은 XML 에 없고 로그에 남는다 · 정상 sideforce.rst 에서 값이 0 이 아니다
- 변경 범위: model/extensions/enterprise/LGE_SpringRule.{h,cpp} · model/DashAnalysisLauncherKPI.cpp
- 선행: -
- 충돌: PRE-12, PRE-21, PRE-22 (KPI.cpp) · B2 교집합: DashAnalysisLauncherKPI.cpp → PRJ-09 UIC-20 · LGE_SpringRule.h → OPT-19 PRE-16 · LGE_SpringRule.cpp → PRE-16
- 흡수: #631 · PRE-c31, PRE-c32
- 비고: grid 배열 이름·성분 순서는 실제 sideforce.rst 로 확인해야 한다(미확인). `DASH_BUILD_LGE_COMPSPRING` 빌드에서만 컴파일된다

### PRE-12 · Modal Frequency KPI 의 자체 `allProcessFinished` 를 지운다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: 나머지 KPI 4종과 같이 `processFinished` 만 내고 완료 알림은 래퍼에 맡긴다
- 완료 기준: Dev 빌드에서 Modal Frequency 행 1개 Process → Success 팝업 1회 (`BUILD_TARGET=Dev` 가 `BUILD_LGE_CompSpring` 을 ON 으로 켜므로 `DASH_BUILD_LGE_COMPSPRING` 블록이 컴파일된다 — CMakeLists.txt:88-92)
- 변경 범위: model/DashAnalysisLauncherKPI.cpp
- 선행: -
- 충돌: PRE-11, PRE-21, PRE-22 · B2 교집합: DashAnalysisLauncherKPI.cpp → PRJ-09 UIC-20
- 흡수: #636-1 · PRE-c37

### PRE-13 · KPI + 일반 행 혼합 배치의 완료 알림을 Process 1회당 1번으로 모을지 정한다
- 종류: DEC | 규모: S | 태그: B, D
- 목표: 래퍼가 일반 행까지 처리한 뒤 한 번만 내고 안쪽 `processResults` 가 생성 파일·보고 줄을 돌려줄지, 아니면 #454 워커 전환(PRE-23) 때 작업 단위 완료 신호로 바꾸면서 함께 할지 결정한다
- 완료 기준: 결정 기록 — 알림 횟수 규칙과 구현 위치(래퍼 PR 추가 또는 PRE-23 포함)
- 변경 범위: (결정에 따라) model/DashAnalysisLauncher.cpp (processResultsWithKPI · processResults)
- 선행: PRE-12
- 충돌: PRE-23 · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp) · PR #652(DashAnalysisLauncher.cpp) · PR #651(DashAnalysisLauncher.cpp)
- 흡수: #636-2 · PRE-c39
- 비고: 런처를 링크하는 자동 테스트가 없어 확인은 수동이다

### PRE-14 · 설정 파일이 비어 있으면 빈 객체에서 시작한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `readRoot` 가 내용이 비었거나 공백뿐인 파일을 없는 파일처럼 다룬다. 깨진 파일(잘림·배열·스칼라)은 지금처럼 보존·거절한다. `invalidExistingConfigIsPreserved` 의 `empty` 행을 새 파일 케이스로 옮긴다
- 완료 기준: `test_analysis_launcher_config` — 0바이트·공백 파일에서 쓰기 성공, 깨진 파일 거절 · 0바이트 `AnalysisLauncher_{Set}.json` 에서 Start 가 취소되지 않는다
- 변경 범위: model/preprocessor/DashAnalysisLauncherConfig.cpp · tests/TestAnalysisLauncherConfig.cpp
- 선행: - (PER-02 헬퍼가 먼저 랜딩하면 `readRoot` 를 헬퍼 호출로 치환하는 형태로)
- 충돌: feat/616-input-format-policy (같은 파일) · PER-02 (읽기 규칙의 정본 — 같은 규칙을 두 곳에 두지 않는다) · B2 교집합: DashAnalysisLauncherConfig.cpp → DOE-03 DOE-16 LCH-16 PRE-15 PRE-27 PRE-32 · TestAnalysisLauncherConfig.cpp → DOE-03 DOE-16 LCH-16 PRE-15 PRE-32
- 흡수: #638-1 · PRE-c45 · PER-c19(증상 1) · PRE-c78
- 비고: #479(직쓰기 크래시)가 0바이트 파일을 만드는 경로다. #601 뒤 수정은 공용 `readRoot` 에 둔다. 읽기 규칙(없음·빈·공백 = 빈 객체, 손상 = 거절·보존)은 PER-02 계약과 같다

### PRE-15 · 설정 쓰기 실패 사유를 호출부까지 돌려주고 보여 준다
- 종류: PR | 규모: M | 태그: D · feature
- 목표: `readRoot`/`writeRoot` 의 사유를 쓰기 함수가 `QString* error = nullptr` 출력 인자로 돌려주고(반환은 `bool` 유지 — 기존 호출부 무변경), PRE 호출부가 경로 뒤에 붙여 `errorOccurred`/`DashNotify` 로 낸다. `writePreprocessTargetFile` 의 무시된 반환도 알린다
- 완료 기준: 깨진 JSON 에서 Start·Target file 변경 시 모달에 사유(파싱 오류 문구)가 보인다 · `test_analysis_launcher_config` 가 출력 인자의 문구를 검사 · LCH 호출부 3곳(`DashAnalysisLaunchExecutor.cpp` · `DashJobRunner.cpp` · `DashDoeCasesWidget.cpp`)은 무변경 컴파일
- 변경 범위: model/preprocessor/DashAnalysisLauncherConfig.{h,cpp} · model/DashAnalysisLauncher.cpp · tests/TestAnalysisLauncherConfig.cpp
- 선행: PRE-14
- 충돌: feat/616-input-format-policy · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashAnalysisLauncherConfig.cpp → DOE-03 DOE-16 LCH-16 PRE-27 PRE-32 · TestAnalysisLauncherConfig.cpp → DOE-03 DOE-16 LCH-16 PRE-32 · DashAnalysisLauncherConfig.h → DOE-03 LCH-16 PRE-27 PRE-32 · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp) · PR #652(DashAnalysisLauncher.cpp)
- 흡수: #638-2 · PRE-c46 · PER-c19(증상 2) · PRE-c78
- 비고: 반환형을 `QString` 으로 바꾸면 LCH 소유 호출부 4곳(`writeCaseStatus` — DashAnalysisLaunchExecutor.cpp:243 · DashJobRunner.cpp:135, `writeCaseActive` — DashDoeCasesWidget.cpp:367·393)이 같이 바뀌고 LCH-07(같은 호출부를 executor 로 모으는 중)과 동시 수술이 된다. 그래서 출력 인자 방식을 택했다 — LCH-07 과 순서 무관. 사유를 LCH 쪽 모달에도 띄우려면 그때 `보류: LCH 몫` 으로 따로 받는다

### PRE-16 · 주석·include·죽은 코드를 정리한다
- 종류: PR | 규모: L | 태그: E · refactor
- 목표: `solverType_` 주석을 실제 수명(마지막 `initialize()` 의 솔버)으로, `m_preprocessor`·"Data Upload 표" 주석 정정, 미사용 include(`DashAnalysisLauncher.h` `<filesystem>`, `.cpp` `<cmath>`·`<QProcess>`·`<stdexcept>`·`<QTextStream>`), `ExtractedKeys::frequencies`, 생산 호출 0 인 `DashResultBatch::keepDoneRuns`·`synthesizeRuns`(+테스트)·`LGE_SpringRule::addComponentToQuery` 를 지운다
- 완료 기준: 빌드 오류 0 · 지운 심볼 참조 0 · 테스트 통과
- 변경 범위: model/preprocessor/DashReaderSession.h · DashLoadedResult.h · DashResultTypes.h · DashResultBatch.{h,cpp} · model/DashAnalysisLauncher.{h,cpp} · model/extensions/enterprise/LGE_SpringRule.{h,cpp} · tests/TestResultBatch.cpp · tests/TestRealResultFiles.cpp
- 선행: -
- 충돌: PRE-07 (DashAnalysisLauncher.cpp) · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashAnalysisLauncher.h → LCH-33 PRE-03 PRE-08 PRE-23 PRE-24 PRE-32 PRJ-22 · TestRealResultFiles.cpp → PRE-01 PRE-06 PRE-09 PRE-17 · DashReaderSession.h → PRE-21 PRE-23 PRE-24 · LGE_SpringRule.h → OPT-19 PRE-11 · DashResultBatch.cpp → PRE-30 · DashResultBatch.h → PRE-30 · DashResultTypes.h → PRE-08 · LGE_SpringRule.cpp → PRE-11 · TestResultBatch.cpp → PRE-05 · PR #658(DashAnalysisLauncher.cpp·TestRealResultFiles.cpp) · PR #656(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h) · PR #652(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h) · PR #651(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h)
- 흡수: #638-3 · #638 비차단 3건 · PRE-D10(잔여) · PRE-c47, PRE-c48, PRE-c49, PRE-c50, PRE-c63(잔여), PRE-c07(SpringRule 사본)
- 비고: L 사유 — 한 개념(낡은 주석·미사용 include·죽은 심볼 제거)인데 대상이 11파일에 흩어져 있다. 파일당 변경은 몇 줄이고, 쪼개면 같은 정리 규칙을 두 PR 에 나눠 설명해야 해 유지한다(00-plan 1-2). `TestRealResultFiles` 가 `synthesizeRuns` 를 쓰므로 `DashLauncherRuns` 기반으로 바꾼다. `<algorithm>` 은 `std::max` 가 써서 남긴다. `LGE_SpringRule.cpp` 는 `file(GLOB_RECURSE model/*.cpp)` 로 모든 빌드에서 컴파일되므로(내부 `#ifdef` 없음) 별도 고객사 빌드 확인이 필요 없다

### PRE-17 · 응답 카탈로그가 호출자의 시간 선택자를 반영한다
- 종류: PR | 규모: M | 태그: A · bug
- 목표: `LegacyJsonPreprocessor::GetAvailableResponses` 가 `ParseTimeQuery` → `MatchTime` 으로 시점을 고르고 그 시점의 응답만 낸다. 매칭 실패는 오류(무필터 폴백 금지). `Responses()` 캐시 키를 (파일, step, substep) 정수로 바꾼다. `GetFieldOutputVtk` 도 같은 시점 한정 목록으로 매칭한다
- 완료 기준: fe-safe 스텝 선택 시 Name 목록이 수명 결과만 (#658 뒤에는 sub-result 형제 키가 함께 세어지므로 기대 개수는 PRE-01 실측으로 고정한다) · 빈 질의(`{}`)는 지금처럼 전체 · `TestRealResultFiles` 통과
- 변경 범위: model/preprocessor/wrapper/LegacyJsonPreprocessor.{h,cpp} · tests/TestRealResultFiles.cpp
- 선행: PRE-01 (실측 파일) · PR #658 (어댑터를 v3 로 재작성 — `TimeStep`·`ResponseEntry` 타입과 카탈로그 발행 구조가 바뀌고 `GetAvailableResponses`·`GetFieldOutputVtk` 본문이 그 위에 선다. `(void)keyString` 은 #658 도 그대로 둔다)
- 충돌: B2 교집합: TestRealResultFiles.cpp → PRE-06 PRE-09 PRE-16
- 흡수: #494-A · #494 To-be 1·2·5 · PRE-c14, PRE-c18
- 비고: 도메인까지 넘기는 것은 Preprocessor `3ff07ff` 머지가 선행(EXT, PRE-c23) — 이 항목은 시간 선택자만 넘겨 그 선행 없이 간다. Motion(빈 질의)·Function Expression 은 영향 없음을 확인한다

### PRE-18 · 응답 카탈로그에 성분 축(sub-result)을 신설하고 질의로 지목한다
- 종류: PR | 규모: M | 태그: A, C · feature
- 목표: PR #658 이 어댑터 발행(`_` 옆 형제 키)·`MatchResponse` 의 `sub_result` 지목·미리보기/작성기 질의의 `sub_result` 적재를 이미 했다. 남은 **표시 계층**을 그 위에 맞춘다 — 위젯의 `"_"`↔`Magnitude` 변환 3곳을 지워 실제 `Magnitude` sub-result 와 겹치지 않게 하고, 미리보기의 `sqrt(Σv²)` 축약(`DashFieldPreview::selectScalars` 의 `_magnitude` 합성)을 발행된 성분 선택으로 바꾸고, `responseLeaf` 의 `keys().first()` 폴백을 지운다
- 완료 기준: 위젯 Name 목록에 `Magnitude` 가 한 번만 나오고 선택이 그 sub-result 질의로 간다 · 성분 선택 시 `[N, 1]` · `_magnitude` 합성 배열 0, 텐서에 `sqrt(Σv²)` 를 칠하는 경로 없음 · `TestResultQuery`(responseLeaf 폴백 제거)·`TestFieldPreview` 통과
- 변경 범위: model/preprocessor/DashResultQuery.cpp · DashFieldPreview.{h,cpp} · view/DashAnalysisLauncherWidget.cpp · tests
- 선행: PR #658 (어댑터 발행·질의 지목 — 이것이 없으면 맞출 대상이 없다) · PRE-10 (Mode Shape 이름 규칙이 먼저 한 곳으로)
- 충돌: B2 교집합: DashAnalysisLauncherWidget.cpp → PRE-05 PRE-08 PRE-23 PRE-24 PRE-27 · DashResultQuery.cpp → PRE-19
- 흡수: #494-B · #494 To-be 3·6·7 · PRE-c19, PRE-c20, PRE-c21 · PRE-c16·PRE-c17(#494 To-be 4)는 PR #658 로 해소됨
- 비고: "발행과 표시를 한 PR 로" 라는 원 근거는 #658 이 발행을 먼저 올려 성립하지 않는다 — #658 머지 시점부터 위젯의 `"_"`↔`Magnitude` 겹침(PRE-c21)이 실제로 살아 있으므로 이 항목이 그 수선이다. #658 의 `regularNames` 는 형제가 있을 때 목록에서 `_` 를 빼는 데까지만 갔다. 선행에서 PRE-17 을 뺐다 — 어댑터(`LegacyJsonPreprocessor`)를 더 이상 고치지 않으므로 같은 함수 제약이 없다. 텐서 불변량(von Mises)은 Abaqus 미발행이라 범위 밖(#494). 내보내기는 `[N, nComp]` 원본이라 영향 없다

### PRE-19 · `step_name` 을 Load Step 트리까지 전달한다
- 종류: PR | 규모: S | 태그: D · feature
- 목표: `DashResultKeys::parseTimeSteps` 가 어댑터의 `step_name` 을 읽어 트리 라벨에 싣고, `parseLoadStep` 이 그 라벨을 되읽는다
- 완료 기준: fe-safe ODB 에서 Load Step 트리에 스텝 이름이 보인다 · `TestResultKeys`·`TestResultQuery` 에 라벨 왕복 케이스
- 변경 범위: model/preprocessor/DashResultKeys.cpp · DashResultQuery.cpp · tests
- 선행: PRE-01
- 충돌: PRE-05 (위젯 조립 규칙) · B2 교집합: DashResultKeys.cpp → PRE-03 PRE-04 · DashResultQuery.cpp → PRE-10 PRE-18 · PR #658(DashResultKeys.cpp·DashResultQuery.cpp) · PR #656(DashResultKeys.cpp)
- 흡수: #494-A 부수 · #494 To-be 8 · PRE-c15

### PRE-20 · 결과 XML 작성기의 컴포넌트 항을 `DashResultQuery::putComponentTerm` 으로 바꾼다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `DashResultXmlWriter::addComponentToQuery` 를 지우고 PRE-07 이 넘긴 Motion 플래그로 `putComponentTerm` 을 부른다 — Motion 질의에 `entity_name` 이 실린다
- 완료 기준: `TestResultXmlWriter` 에 Motion 컴포넌트 케이스(질의에 `entity_name`) · Mechanical 질의 불변 · `.dfr` DOE 에서 BODY 하나 Process → XML 노드 수가 전체 모델보다 작다(PRE-01)
- 변경 범위: model/preprocessor/DashResultXmlWriter.{h,cpp} · tests/TestResultXmlWriter.cpp
- 선행: PRE-07
- 충돌: PRE-06, PRE-10, PRE-04 · B2 교집합: DashResultXmlWriter.cpp → 공유 10건(deps.md 5절) · DashResultXmlWriter.h → PRE-22 PRE-30 PRE-31 PRE-32 · TestResultXmlWriter.cpp → PRE-31 PRE-32 · PR #658(DashResultXmlWriter.cpp·TestResultXmlWriter.cpp) · PR #656(DashResultXmlWriter.cpp·TestResultXmlWriter.cpp)
- 흡수: #635 · #433-9(컴포넌트 항) · PRE-c07, PRE-c35, PRE-c81
- 비고: `ILJIN_TensionlinkRule::addComponentToQuery` 사본은 Abaqus 전용이라 그대로 둔다. `putComponentTerm` 의 `entity_type`·`body_name` 분기는 어댑터가 `entity_type` 을 발행하지 않아 도달하지 않는다(`wrapper/LegacyJsonPreprocessor.cpp:466-472` 주석이 명시) — 발행은 외부 어댑터 몫(#334, 보드 밖)이라 분기는 그대로 두고 완료 기준에서 뺀다(PRE-c81)

### PRE-21 · 배치 뒤 리더 입력 복원을 `DashReaderSession::Work` 종료 한 곳으로 모은다
- 종류: PR | 규모: M | 태그: A, B · bug
- 목표: 최상위 `Work` 가 Keep 으로 끝날 때 `loadedInputs_` 를 재오픈한다. KPI 4종의 `restoreLoadedInputs()` 호출을 지우고 Modal KPI·일반 `processResults` 도 같은 규칙을 탄다. `ensureForLoadedInputs(false)` 는 리더가 있으면 재오픈하지 않는다는 계약을 헤더에 적는다
- 완료 기준: 일반 Process 뒤 Load Step 클릭의 Name 목록이 Load 한 파일 기준(마지막 run 파일 아님) · `TestReaderSession` 에 Work 종료 복원 케이스 · KPI 4종 뒤 미리보기 불변
- 변경 범위: model/preprocessor/DashReaderSession.h · model/DashAnalysisLauncher.cpp · model/DashAnalysisLauncherKPI.cpp · tests/TestReaderSession.cpp
- 선행: -
- 충돌: PRE-11, PRE-12, PRE-22 (KPI.cpp) · PRE-23 · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashAnalysisLauncherKPI.cpp → PRJ-09 UIC-20 · DashReaderSession.h → PRE-16 PRE-24 · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp) · PR #652(DashAnalysisLauncher.cpp) · PR #651(DashAnalysisLauncher.cpp)
- 흡수: PRE-D6 · PRE-c70
- 비고: 복원 실패는 지금처럼 `faulted_` 로 리더를 폐기한다

### PRE-22 · KPI 5종의 공통 프레임(매핑·parameterInfo·출력 폴더·샘플 프레임·model_info·저장)을 뽑는다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: 5함수가 복제한 입력 매핑·`loadParameterInfo`·`moduleDir`·샘플 dict 프레임(구 형식 폴백 + `writeParametersToXml` + 스칼라 항목)·`responseInfo`/file_name 루프·파일 저장을 `DashAnalysisLauncherKPI.cpp` 안의 헬퍼(또는 `DashResultXmlWriter` 스칼라 샘플 API)로 모은다. 계산 규칙은 건드리지 않는다
- 완료 기준: 두 고객사 빌드 모두 빌드 오류 0 · 같은 입력으로 생성한 KPI XML 바이트 동일
- 변경 범위: model/DashAnalysisLauncherKPI.cpp · model/preprocessor/DashResultXmlWriter.{h,cpp}
- 선행: PRE-11, PRE-12, PRE-21 (동작 변경 먼저)
- 충돌: PRE-23 · B2 교집합: DashResultXmlWriter.cpp → 공유 10건(deps.md 5절) · DashResultXmlWriter.h → PRE-04 PRE-07 PRE-20 PRE-30 PRE-31 PRE-32 · DashAnalysisLauncherKPI.cpp → PRJ-09 UIC-20 · PR #658(DashResultXmlWriter.cpp) · PR #656(DashResultXmlWriter.cpp)
- 흡수: PRE-D11 · PRE-c67
- 비고: `BUILD_TARGET=Dev` 가 `BUILD_LGE_CompSpring`·`BUILD_ILJIN_TensionLink` 를 함께 켜므로(CMakeLists.txt:88-92) Dev 빌드 하나로 두 고객사 블록이 컴파일된다 — 고객사 단독 타깃 빌드는 선택 확인

### PRE-23 · 배치(`processResults`·`DashResultProcessor`)를 워커로 옮기고 펌핑 14곳을 지운다
- 종류: PR | 규모: L | 태그: B · refactor
- 목표: 요청 루프와 샘플 루프를 `controller/async` Job 으로 옮기고 결과·보고는 신호로 돌려준다. `processResults` 6곳·`DashResultProcessor` 8곳의 `processEvents` 를 지우고, 위젯의 `m_isProcessing` 가드·`rejectIfReaderBusy` 를 Job 상태로 바꾼다. `DashReaderSession` 의 스레드 소속을 명시한다
- 완료 기준: PRE 영역 비KPI `processEvents` 0 (적재 2곳 제외, PRE-24) · 배치 중 Add/Remove/Preview 가 재진입하지 않고 거절·대기 · 배치 중 상태바 진행 표시·취소 버튼이 EXE-07 규약대로 동작하고 Process 버튼은 EXE-09 가드로 비활성(#463) · 단일 파일/DOE·일부 누락·실패 후 재시도·KPI 혼합 시나리오의 XML 동일 · `TestResultProcessor` 통과
- 변경 범위: model/DashAnalysisLauncher.{h,cpp} · model/preprocessor/DashResultProcessor.{h,cpp} · DashReaderSession.h · view/DashAnalysisLauncherWidget.{h,cpp} · controller/async 소비
- 선행: PRE-04, PRE-07 (#433 9단계 코드 잔여 — 런처·처리기 같은 파일 동시 수술 금지 #239), PRE-13, PRE-21 · EXE-01 (레인 결정 — #454 가 어느 레인에 제출하는지) · EXE-02 (취소) · EXE-07 (진행 표시 규약) · EXE-09 (가드 헬퍼)
- 충돌: PRE-04, PRE-22 · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashAnalysisLauncher.h → LCH-33 PRE-03 PRE-08 PRE-16 PRE-24 PRE-32 PRJ-22 · DashAnalysisLauncherWidget.cpp → PRE-05 PRE-08 PRE-18 PRE-24 PRE-27 · DashReaderSession.h → PRE-16 PRE-24 · DashAnalysisLauncherWidget.h → LCH-01 PRE-05 · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h) · PR #652(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h) · PR #651(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h·DashAnalysisLauncherWidget.h)
- 흡수: #454(배치 14곳) · PRE-D3 · PRE-c11(배치), PRE-c12, PRE-c71 · #463(PRE 적용 — 진행 표시·취소·가드) · EXE-c23 · EXE-c48 · EXE-c43(PRE-D3) · PRE-c80
- 비고: L 사유 — 실행 모델 전환이라 처리기·런처·위젯 가드·리더 세션을 한 번에 바꿔야 중간 상태가 없다. 선행에서 PRE-02(#433 종료 문서 작업)를 뺐다 — 그 선행은 PRE-01 의 구할 수 없는 실측 파일까지 사슬로 끌고 오는데, #433·#454 가 금한 것은 같은 파일 동시 수술이라 코드 항목(PRE-04·07)으로 충분하다. KPI 7곳은 #454 결정대로 보존(래퍼가 KPI 를 동기로 먼저 돌리는 구조도 유지). 완료 판정은 #453(기각) 대신 이 항목의 기준으로

### PRE-24 · 적재(`loadPreprocessInputs`·`selectTargetFile`·`.rst` 판별)를 워커로 옮기고 펌핑 2곳을 지운다
- 종류: PR | 규모: M | 태그: B · refactor
- 목표: 결과 파일 스캔·리더 생성·GetTimeSteps/Geometries/Responses 조회를 Job 으로 옮기고 `ExcludeUserInputEvents` 펌핑 2곳을 지운다. 로딩 인디케이터는 Job 시작·종료 신호로
- 완료 기준: PRE 영역 비KPI `processEvents` 0 · Preprocess 탭 진입 중 Set 전환·Target file 변경이 거절·대기 · Load 실패 뒤 재시도 계약(#573) 유지
- 변경 범위: model/DashAnalysisLauncher.{h,cpp} · model/preprocessor/DashReaderSession.h · view/DashAnalysisLauncherWidget.cpp
- 선행: PRE-23
- 충돌: B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashAnalysisLauncher.h → LCH-33 PRE-03 PRE-08 PRE-16 PRE-32 PRJ-22 · DashAnalysisLauncherWidget.cpp → PRE-05 PRE-08 PRE-18 PRE-27 · DashReaderSession.h → PRE-16 PRE-21 · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h) · PR #652(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h) · PR #651(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h)
- 흡수: #454(적재 2곳) · PRE-c11(적재) · EXE-c48 · PRE-c80

### PRE-25 · 확장자→솔버 라우팅을 `SupportedResults` 기준으로 닫는다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: 확장자→솔버 선택을 `SupportedResults.solverName` 을 읽는 순수 함수(`DashTargetFiles::solverOf`)로 빼고, `createPreprocessor` 는 그 결과로 플러그인만 올린다 — 지원 솔버가 없는 확장자(`.op2`)는 오류로 거절하고 도달하지 않는 `res`·`dfsxml` 분기를 지운다
- 완료 기준: `tests/TestTargetFiles.cpp` 에 `solverOf` 케이스 — `.rst`→AnsysMechanical · `.dfr`→AnsysMotion · `.odb`→Abaqus · `.op2`·`res`·`dfsxml`→미지원(빈 값) · `createPreprocessor` 에 확장자 리터럴 0 · 수동 1회(`.rst` Load 불변)
- 변경 범위: model/preprocessor/DashTargetFiles.{h,cpp} · model/DashAnalysisLauncher.cpp (createPreprocessor) · tests/TestTargetFiles.cpp
- 선행: -
- 충돌: PRE-07 · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp) · PR #652(DashAnalysisLauncher.cpp) · PR #651(DashAnalysisLauncher.cpp)
- 흡수: PRE-U1 · PRE-U2 · PRE-c64, PRE-c73
- 비고: "`.op2` 를 Load 하면 오류" 는 앱에서 재현할 수 없다 — Preprocess 입력은 러너가 Done 에 기록한 resultFiles 뿐(#640)이고 NASTRAN 러너가 없다. `createPreprocessor` 는 `DashManager` 솔버 경로를 읽는 멤버라 Qt Core 테스트가 부를 수 없으므로, 확인 가능한 지점을 순수 함수로 뺀다(`DashTargetFiles` 는 이미 Qt Core 전용 · `test_target_files` 존재). `.op2` 를 목록(AnalysisFileDefines.h)·`DashManager` 솔버 목록에서 뺄지는 LCH·UIC 결정(접점)

### PRE-26 · Output Response 기록을 재진입 복원으로 살릴지 쓰기를 없앨지 정한다
- 종류: DEC | 규모: S | 태그: A, C
- 목표: `Output Response` 가 쓰기 전용(읽는 코드 0)이고 KPI 행은 기록도 안 되며 PM 이 `readRoot`/`writeRoot` 밖에서 직쓰기한다. (a) 재진입 시 표 복원(KPI 행 포함) 구현 또는 (b) 기록 제거 중 하나로 정한다
- 완료 기준: 결정 기록 — 선택지·근거·PRE-27 의 범위
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: PRE-D7 · PRE-D8 · PRE-c61, PRE-c62, PRE-c51
- 비고: #601 뒤 Preprocess 는 Launcher 결과를 다시 읽으므로 표만 복원하면 되지만, Target file 변경·입력 변경 시 표를 비우는 현재 규칙(PRE-c68)과 맞춰야 한다

### PRE-27 · Output Response 기록 결정을 반영한다
- 종류: PR | 규모: M | 태그: A, C · feature
- 목표: (a) 복원 — PM 에 읽기 추가, `refreshPreprocessTab` 이 입력이 같으면 표를 복원, `addKpiToResultTable` 도 저장, 저장은 `DashAnalysisLauncherConfig` 의 `readRoot`/`writeRoot` 경유. (b) 제거 — `saveOutputResponse` 와 호출 3곳 삭제
- 완료 기준: (a) Set 재진입 시 Output Response 행(KPI 포함)이 돌아온다 · 설정 파일의 다른 키 보존 (b) `Output Response` 키 쓰기 0
- 변경 범위: viewmodel/DashAnalysisLauncherPresentationModel.{h,cpp} · view/DashAnalysisLauncherWidget.cpp · model/preprocessor/DashAnalysisLauncherConfig.{h,cpp}
- 선행: PRE-26, PRE-14 · PER-02 ((a) 일 때 — 저장은 헬퍼 경유)
- 충돌: PRE-05 (위젯) · B2 교집합: DashAnalysisLauncherConfig.cpp → DOE-03 DOE-16 LCH-16 PRE-15 PRE-32 · DashAnalysisLauncherWidget.cpp → PRE-08 PRE-18 PRE-23 PRE-24 · DashAnalysisLauncherConfig.h → DOE-03 LCH-16 PRE-15 PRE-32 · PR #651(DashAnalysisLauncherConfig.cpp·DashAnalysisLauncherConfig.h)
- 흡수: PRE-D7 · PRE-D8 · PRE-c61, PRE-c62, PRE-c51 · #479 · #478 (PER 직쓰기 이행의 PRE 몫) · PER-c26 · PRE-c79
- 비고: (a) 든 (b) 든 `saveOutputResponse` 의 `QFile` 직쓰기는 사라진다 — PER 의 직쓰기 22지점 중 PRE 몫 1지점

### PRE-28 · Preprocess XML 의 실측 파일 크기·생성 피크 메모리·샘플 수 증가율을 수집한다
- 종류: INV | 규모: S | 태그: F · perf
- 목표: 실기 DOE 산출물(정적 `.rst`·`.odb`, 모핑 N 케이스)에서 응답 수·샘플 수별 XML 크기와 `processResults` 피크 메모리를 재고 base64·DOM 누적·요청 수 세 겹의 기여를 나눈다
- 완료 기준: 실측 결과 — 표(샘플 수 × 응답 수 → 크기·피크) 와 #411 부분 대안 3종(위상 1회·paddingTarget·node_location 1회)의 예상 절감
- 변경 범위: 측정 스크립트·기록만
- 선행: -
- 충돌: -
- 흡수: #411(먼저 할 것) · PRE-c57
- 비고: 실기 산출물 필요(미확인). PER-03 ⑦ 이 "결과 XML 의 키 작성" 참조처로 PRE-28·29 를 적었으나(03-items/PER.md 완료 기준 2) **이 항목의 선행은 아니다** — 크기·피크 메모리 실측은 저장 포맷 버전 키 규약과 무관하고, 규약 수용은 PRE-29(결정)·PRE-30(구현) 몫이다. PER-03 선행 등재는 PRE-29 에만 넣었다

### PRE-29 · Preprocess XML 의 단위·중복·포맷을 정한다
- 종류: DEC | 규모: S | 태그: A, C
- 목표: #643 1차(Set 단위 파일 1개 + 응답 추가)·2차(입력 식별과 버전별 이어쓰기/덮어쓰기 조건 검토)·중복 1회 저장·HDF5(vtkHDF) 전환 여부를 결정한다. 결정 입력: **DeepOpt 리더 계약 — `root` 의 첫 자식만 학습 데이터로 읽고 샘플 dict 는 동형이어야 한다(BLD-c26·BLD-14 비고 · 위키 Model-Builder-XML-DeepOpt-Pipeline)**, Builder 다중 part 포맷(BLD), `vtkIOHDF` 가용(DEV), 저장 포맷 버전 키 A3/N9(**PER-03 ⑦** — 결과 XML 이 같은 규약을 쓰는지), `DashXmlParser` 전환(ANA), HDF5·중복 1회 판단에는 PRE-28 수치, 현행 포맷 기준선에는 **PR #658** (주파수 `dict_item` 에 `quantity`·`unit` 속성 + Eigenvalue 는 무차원 `Eigenvalue` 키, 벡터 `resItem` 에 `component_labels` 속성 — 머지되면 기준선이 이것이다)
- 완료 기준: 파일 단위·중복·포맷·소비자 수용과 구 포맷 판독 호환 범위를 결정한다. setId·deck 식별자·버전을 구분하고 이어쓰기 허용 조건은 팀 논의로 확정한다. 구 포맷 판독 가능과 필수 출처 없는 산출물의 실행 허용을 구분하며 출처 자동 마이그레이션은 하지 않는다. DeepOpt의 model_info 위치·샘플 dict 동형을 대조한다.
- 변경 범위: -
- 선행: PER-03 (저장 포맷 버전 키 규약 ⑦ — 결과 XML 이 그 규약을 쓰는지 정해져야 포맷 결정이 닫힌다) · PR #658 (포맷 기준선). 1차 포맷·2차 식별자 결정 자체는 실측과 무관하고, HDF5 전환·중복 1회만 PRE-28 수치를 본다 — #643 은 W5 배정이라 측정 대기로 묶지 않는다
- 충돌: -
- 흡수: #643(1차·2차·추가 1·3) · #411(결정 1~4) · PRE-c52(결정부), PRE-c53, PRE-c55(결정부) · 범위밖 입력 PRE-c54, PRE-c56, PRE-c58, PRE-c59, PRE-c60 · ANA-c30 · PRE-c77 (ANA 파서 전환 검토 — 같은 결정 입력)
- 비고: #643·#411의 상세 범위와 이어쓰기 기준은 이슈 개정 이력의 추가 개정 계획이며 GitHub 반영 완료로 취급하지 않는다. #368의 PRE-32가 출처 기록·판독을 맡고 #650은 버전·최신성을 맡는다. 같은 model_info 위치를 쓰더라도 조합 ID 두 키나 최초 입력 핀을 전제로 삼지 않으며 상호 불필요한 선행을 만들지 않는다.

### PRE-30 · 결과 XML 을 Set 단위 파일 하나에 응답을 추가하는 방식으로 쓴다
- 종류: PR | 규모: M | 태그: A, C · feature
- 목표: processResults가 Set 파일에 응답을 추가하는 저장 구조를 구현한다. Set 식별은 setId, deck 식별과 DOE tableId는 각자 역할을 유지한다. 출처 필드는 PRE-32의 #368 공통 계약을 사용하며 입력 변경 시 이어쓰기·덮어쓰기 조건은 PRE-29의 팀 논의 결정 뒤 적용한다.
- 완료 기준: 응답 2개를 Set 파일 1개에 저장하고 DeepOpt의 root 첫 자식·샘플 dict 동형을 보존한다. 팀이 확정한 이어쓰기 조건과 실제 출처 기록을 검증한다. 구산출물의 누락 출처를 이름·경로로 추론하지 않는다. BLD-14·ANA의 포맷 수용과 조율한다.
- 변경 범위: model/DashAnalysisLauncher.cpp (processResults) · model/preprocessor/DashResultBatch.{h,cpp} · DashResultXmlWriter.{h,cpp} · tests
- 선행: PRE-29
- 충돌: PRE-04, PRE-06, PRE-23 (processResults — 먼저 랜딩한 쪽에 리베이스) · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashResultXmlWriter.cpp → 공유 10건(deps.md 5절) · DashResultXmlWriter.h → PRE-07 PRE-20 PRE-22 PRE-31 PRE-32 · DashResultBatch.cpp → PRE-16 · DashResultBatch.h → PRE-16 · PR #658(DashAnalysisLauncher.cpp·DashResultXmlWriter.cpp) · PR #656(DashAnalysisLauncher.cpp·DashResultXmlWriter.cpp) · PR #652(DashAnalysisLauncher.cpp) · PR #651(DashAnalysisLauncher.cpp)
- 흡수: #643(1차·2차) · PRE-c52, PRE-c53
- 비고: 읽는 쪽(DashXmlParser · Builder · Analyzer) 변경은 BLD-14·ANA 항목 몫. 선행에서 PRE-23 을 뺐다 — #643 은 W5 배정인데 PRE-23 은 EXE 8건을 선행으로 둔 Backlog 라 1차 포맷이 워커 전환 뒤로 밀린다. 같은 `processResults` 를 고치므로 충돌로만 둔다. DeepOpt 는 `root` 첫 자식만 읽으므로 응답 추가는 샘플 dict 안의 키로만 하고 `model_info` 를 앞으로 옮기지 않는다

### PRE-31 · 위상(connectivity · node_location)을 파일당 1회만 쓰고 paddingTarget 을 실제 maxStride 로 둔다
- 종류: PR | 규모: S | 태그: A · perf
- 목표: 작성기가 샘플마다 리셋하는 `m_nodeLocationWritten`·`m_connectivityWritten` 을 파일 단위로 올리고(모핑은 위상 불변, 조건-only·CAD 는 node_location 도 불변), `maxStride < 8 ? 8` 의 최소 8 규칙을 실제 maxStride 로 바꾼다
- 완료 기준: tet 메시 DOE 의 XML 크기 감소(PRE-28 기준) · 샘플 0 에만 위상을 두어도 샘플 dict 동형 전제를 깨지 않음을 DeepOpt 계약과 대조(PRE-29 결정) · `TestResultXmlWriter` 통과 · 파서 쪽 수용 — `보류: BLD 몫`(샘플 0 위상으로 나머지 읽기) · `보류: ANA 몫`(`DashXmlParser`)
- 변경 범위: model/preprocessor/DashResultXmlWriter.{h,cpp} · tests/TestResultXmlWriter.cpp
- 선행: PRE-29 (소비자 전제 확인 — DeepOpt 가 샘플별 위상을 전제하는지 포함)
- 충돌: PRE-30, PRE-06, PRE-10, PRE-04 · B2 교집합: DashResultXmlWriter.cpp → 공유 10건(deps.md 5절) · DashResultXmlWriter.h → PRE-07 PRE-20 PRE-22 PRE-32 · TestResultXmlWriter.cpp → PRE-20 PRE-32 · PR #658(DashResultXmlWriter.cpp·TestResultXmlWriter.cpp) · PR #656(DashResultXmlWriter.cpp·TestResultXmlWriter.cpp)
- 흡수: #643 추가 2 · #411 부분 대안 · PRE-c55
- 비고: 포맷 변경이므로 구 XML 읽기 호환은 PRE-29 의 마이그레이션 방침을 따른다. 샘플 1..N 의 dict 구조가 샘플 0 과 달라지므로 DeepOpt 의 "샘플 dict 동형" 전제에 걸린다 — PRE-29 가 그 계약을 확인하지 않으면 착수하지 않는다

### PRE-32 · Launcher가 실제 run 출처를 검증하고 결과 XML에 기록한다
- 종류: PR | 규모: L | 태그: C, A · feature
- 목표: #368 계약으로 DOE 스냅샷과 실제 입력 run의 출처를 판독·검증하고 결과 XML model_info에 생성 Launcher setId·입력 DOE setId·상류 출처·세부 선택·deck 정보를 기록한다. 현재 Launcher setId를 유지하며 다른 DOE Set을 선택할 수 있다. 선택 변경은 기존 XML 출처를 변경하지 않고 결과 덮어쓰기 시 실제 출처를 함께 갱신한다.
- 완료 기준: ① 결과 XML 출처가 실제 사용한 스냅샷·run과 일치 ② 다른 유효한 DOE setId로 참조 변경·재실행 가능, 선택만 바꾸면 기존 산출물 불변 ③ priorSamples는 실제 출처와 선택 관계를 검증하며 조합 ID 동일성을 요구하지 않음 ④ 필수 출처 누락·해석 불가 run은 재생성 안내, live DOE JSON 추론·자동 이관 금지 ⑤ XML·설정·run 테스트에서 왕복과 오류 사유 확인.
- 변경 범위: model/DashAnalysisLauncher.{h,cpp} · model/preprocessor/DashResultXmlWriter.{h,cpp} · model/preprocessor/DashAnalysisLauncherConfig.{h,cpp} · model/preprocessor/DashLauncherRuns.{h,cpp} · tests/TestResultXmlWriter.cpp · tests/TestAnalysisLauncherConfig.cpp · tests/TestLauncherRuns.cpp
- 선행: DOE-16
- 충돌: PRE-30 (같은 `model_info` 자리 — 포맷 구조와 출처 기록의 적용 접점만 조율) · PRE-04 · PRE-06 · PRE-23 (processResults) · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashResultXmlWriter.cpp → 공유 10건(deps.md 5절) · DashAnalysisLauncher.h → LCH-33 PRE-03 PRE-08 PRE-16 PRE-24 PRJ-22 · DashAnalysisLauncherConfig.cpp → DOE-03 LCH-16 PRE-14 PRE-15 PRE-27 · DashResultXmlWriter.h → PRE-07 PRE-20 PRE-22 PRE-31 · TestAnalysisLauncherConfig.cpp → DOE-03 LCH-16 PRE-14 PRE-15 · DashAnalysisLauncherConfig.h → DOE-03 LCH-16 PRE-15 PRE-27 · TestResultXmlWriter.cpp → PRE-20 PRE-31 · DashLauncherRuns.cpp → LCH-09 · DashLauncherRuns.h → LCH-30 · PR #658(DashAnalysisLauncher.cpp·DashResultXmlWriter.cpp·TestResultXmlWriter.cpp) · PR #656(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h·DashResultXmlWriter.cpp·TestResultXmlWriter.cpp) · PR #652(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h) · PR #651(DashAnalysisLauncher.cpp·DashAnalysisLauncher.h·DashAnalysisLauncherConfig.cpp·DashAnalysisLauncherConfig.h·TestAnalysisLauncherConfig.cpp)
- 흡수: #368 Phase 2(T21) · LCH-c36 · PRE-c76
- 비고: 기존 tableId 기반 run 선택은 유지하되 새 상류 입력 선택을 최초 값으로 잠그지 않는다. DOE-16은 스냅샷 전파, LCH-33은 실행 직전 검증, 본 항목은 결과 입력 검증·출처 기록을 담당한다. #643 포맷·이어쓰기 조건은 PRE-29의 별도 논의이며 출처 계약과 서로 불필요한 선행을 만들지 않는다.

## 대응표

| 원천 | 항목 | 비고 |
|---|---|---|
| #433 | PRE-01, PRE-02, PRE-04, PRE-07, PRE-20 (PRE-03 = CLOSE) | 1~7단계·9단계 카탈로그/주파수/작성기 직렬화는 해소됨(#642). 9단계 질의 직렬화·모달 Name·TimeSteps 파싱은 **열린 PR #656** 이 구현 → PRE-03 CLOSE |
| #454 | PRE-23, PRE-24 | KPI 7곳 보존. 선행 PRE-02 · EXE-01/02/07/09. EXE 접점 EXE-c48 · EXE-c43 → PRE-c80 |
| #463 (EXE 이관 — 모듈별 진행바·취소·가드 적용) | PRE-23 | EXE-c23 → PRE-c80. 규약·헬퍼는 EXE-07/09 |
| #368 (PER 담당 · T21 홉 이관) | PRE-32 | LCH-c36 → PRE-c76. 공통부 PER-06·07 · 생산자 DOE-16. PR #530 은 머지하지 않고 T21 hunk 만 참조한다 |
| #479 · #478 (PER 직쓰기 이행 — PRE 몫) | PRE-27 | PER-c26 → PRE-c79 (`saveOutputResponse` 1지점) |
| #494 | PRE-17, PRE-18, PRE-19 | 도메인 전달 선행(Preprocessor 3ff07ff)은 EXT · setModel 중복 connect 는 해소됨 · To-be 4(sub-result 발행·지목)는 **PR #658** 로 해소됨 → PRE-18 은 표시 계층만 |
| #630 | PRE-06 | Motion 항목은 PRE-05 뒤 · 임의 배열 대체(c25)·MatchResponse 우선(c30)은 **PR #658** 로 해소됨 |
| #631 | PRE-11 | sideforce.rst 실측 미확인 |
| #634 | PRE-05 | |
| #635 | PRE-07, PRE-20 | |
| #636 | PRE-12, PRE-13 | |
| #637 | PRE-10, PRE-09, PRE-01 | 단일 파일 배치 항목은 해소됨(#617) · 미리보기 x·y·z·magnitude 선택(c40·c41)은 **PR #658** 로 해소됨 |
| #334 (보드 밖 · 어댑터 EXT) | PRE-20 (분기 보존) | PRE-c81 — `entity_type` 발행이 생기기 전에는 `putComponentTerm` 분기가 도달하지 않는다 |
| #638 | PRE-14, PRE-15, PRE-16 | PER-c19 → PRE-c78. 공통 읽기 규칙은 PER-02 |
| #643 | PRE-29, PRE-30, PRE-31 | 추가 1(Builder 포맷)·3(파서 전환)은 BLD·ANA |
| #411 | PRE-28, PRE-29 | 결정 1·2·3 입력은 DEV·BLD/EXT·PER-03 ⑦ (PRE-29 선행). ANA 접점 ANA-c30 → PRE-c77 |
| PRE-D1 | 항목 없음 | 해소됨 — #617 refreshPreprocessTab 이 표를 비운다 |
| PRE-D2 | 항목 없음 | 해소됨 — #568, 현재 qScopeGuard |
| PRE-D3 | PRE-23, PRE-24 | 23곳 중 KPI 7곳 보존. EXE-c43 → PRE-c80 |
| PRE-D4 | PRE-09 | basename 입력은 해소됨(#617); 잔여는 Abaqus 모달 판별 수단 |
| PRE-D5 | PRE-08 | |
| PRE-D6 | PRE-21 | |
| PRE-D7 | PRE-26, PRE-27 | Dataset 부분은 해소됨(#617) |
| PRE-D8 | PRE-26, PRE-27 | |
| PRE-D9 | 항목 없음 | 해소됨 — 위젯 가드가 KPI 분기 앞, 모델 ReaderWork. EXE-c43 → PRE-c80 |
| PRE-D10 | PRE-16 | 해소됨(#617 resolveDoneRuns); 죽은 keepDoneRuns·synthesizeRuns 만 정리 |
| PRE-D11 | PRE-22 | 스냅샷 로딩 복제는 해소됨(#617); 공통 프레임 복제로 재정의 |
| PRE-D12 | 항목 없음 | 해소됨 — #435 KPI 분리 · #433 2~7단계 |
| PRE-U1 | PRE-25 | 목록 삭제 여부는 LCH·UIC |
| PRE-U2 | PRE-25 | |
| PRE-U3 | 항목 없음 | 해소됨 — #617 Data Upload 탭 제거 |
