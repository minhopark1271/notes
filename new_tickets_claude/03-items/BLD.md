# BLD 작업 목록

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> 기준 dev @ b08a91b3. 원천·판정은 02-claims/BLD.md. 약어는 claims 와 같다 (`M` `MCU` `W` `MW` `Base` `PM` `CH` `LTH`).
> 열린 PR 7건 중 머지 대상 6건 (#651 #652 #654 #655 #656 #658) — #530 은 재업로드 노선이라 머지 대상이 아니다 (05-final/decisions.md ⑩·②). BLD **본체 파일**(M · MCU · W · MW · Base · PM · CH · LTH · DashXmlTailLocator.h)을 만지는 머지 대상 PR 은 **0건**이고, 겹치는 것은 `tests/CMakeLists.txt`(#651 #652 #654 #655 — BLD-19) 뿐이다. **#656·#658 은 BLD 항목의 변경 범위와 교집합 0** 이라 선행 추가 없음 — #656 은 런처·작성기 공용 함수 추출로 XML 출력이 불변이고, #658 은 `DashResultXmlWriter` 의 배열 선택 로직과 응답 `dict_item` 속성(`quantity`·`unit`·`component_labels`)·모달 응답 키(`Eigenvalue`)를 바꾸지만 BLD 함수 본문은 건드리지 않는다 (hunk 확인, BLD-14 비고).
> #368 생산 계약은 BLD-20에서 model_info.json 생성까지 담당하고 #685가 소비를 이어받는다. PR #530의 당시 재업로드 결정은 보존하되 새 코드는 현행 계약으로 작성한다. 충돌은 같은 수정 지점의 적용 순서를 조율한다.

### BLD-01 · MCU Data Label 을 재진입 시 되읽는다 — Dataset 배열 → 파일 표·라벨 표 복원
- 종류: PR | 규모: M | 태그: A, C · bug
- 목표: `DashModelBuilderMCU` 가 `Data Label.Dataset` 배열을 `{path, mode}` 목록으로 보관하고(베이스 `loadDataLabelConfig` 의 가상 훅 또는 재정의), `MW:onConfigLoaded` 가 베이스 XML 로더를 부르는 대신 파일 표를 그 목록으로 복원한 뒤 `onLoadButtonClickedMCU` 와 같은 헤더 재구성으로 Input/Output 표를 만들고 저장된 체크·reduction 을 적용한다. `populateIoTableWithFixedHeaders` 는 목록이 비었을 때만 쓴다. MCU 학습 시작의 XML 이식 분기는 CSV 를 열지 않도록 MCU 에서 제외한다.
- 완료 기준: (1) MCU Set 에서 파일 2개 추가·[Load]·체크 변경·[Set Dataset] 뒤 다른 Set 을 갔다 돌아오면 파일 표 2행(경로·Mode·State)과 Input/Output 체크·reduction 이 그대로다 (2) MCU 학습 시작 로그에 "Dataset path is empty" · "Failed to load model_info from XML" 이 없다 (3) Sim Set 의 복원 동작은 변하지 않는다
- 변경 범위: model/DashModelBuilder.h · model/DashModelBuilderMCU.h · model/DashModelBuilderMCU.cpp · view/DashModelBuilderMCUWidget.h · view/DashModelBuilderMCUWidget.cpp · viewmodel/DashModelBuilderPresentationModel.h · viewmodel/DashModelBuilderPresentationModel.cpp
- 선행: -
- 충돌: BLD-02 (M:loadDataLabelConfig) · BLD-09 · BLD-10 · BLD-12 (MW) · BLD-20 (M.h 가상 훅 인접) · B2 교집합: DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelBuilderMCU.cpp → BLD-13 BLD-17 BLD-18 PRJ-09 UIC-20 · DashModelBuilder.h → BLD-04 BLD-05 BLD-13 BLD-14 BLD-15 · DashModelBuilderMCU.h → BLD-15 · DashModelBuilderPresentationModel.cpp → BLD-16
- 흡수: BLD-D12 · BLD-D9(Dataset 형) · BLD-c08, BLD-c13
- 비고: 헤더 재구성(첫 유효 파일 헤더 → Input N-1 · Output 마지막 열)을 `onLoadButtonClickedMCU` 와 공유 함수로 뽑는다(동작 불변). 배열 파싱은 `CH:parseDataLabelSection` 의 배열 분기를 재사용한다. Dataset 형 차이(문자열 vs 배열)는 입력 모델의 반영이므로 유지하고 로더가 둘 다 읽는 것으로 종결(BLD-11 결정 항목에서 "유지" 로 기록).

### BLD-02 · Data Label 섹션 읽기를 쓰기와 대칭으로 만든다 — parseDataLabelSection 배선 + 키 대조 sanitize 통일
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `M:loadDataLabelConfig` 의 수동 파싱을 `CH:parseDataLabelSection` · `parseConfigurationSection` 호출로 바꿔 Output `transformation` 이 읽히게 하고, `Base:updateLabelTable` 의 저장 목록 대조(`inputConfig.contains(name)`)를 `sanitizeString(name)` 기준으로 통일한다.
- 완료 기준: (1) Output transformation 을 `Log` 로 두고 [Set Dataset] → Set 재진입 시 콤보가 `Log` 다 (2) 공백·`/` 가 든 라벨(외부 XML)의 Input/Output 배치·체크·reduction 이 재진입 후 유지된다 (3) 기존 Sim 설정 JSON 이 그대로 로드된다
- 변경 범위: model/DashModelBuilder.cpp · view/DashModelBuilderWidgetBase.cpp · (대조 헬퍼가 필요하면) model/builder/ModelBuilderConfigHelper.cpp
- 선행: BLD-01 (배열 Dataset 을 읽으면 `m_datasetPath` 가 차므로 MCU 복원 경로가 먼저 분리돼야 한다)
- 충돌: BLD-20 (M.cpp) · BLD-07 · BLD-13 (M.cpp) · B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderWidgetBase.cpp → BLD-05 BLD-06 UIC-21
- 흡수: BLD-D4 · BLD-D8 · BLD-U3 · BLD-c04, BLD-c06, BLD-c07
- 비고: D4 는 XML 작성기(`model/preprocessor/DashUtils.cpp:sanitizeString`)가 같은 규칙이라 Sim 에서 잠재적이다 — 수정은 대조 기준 통일만, 저장 키 규칙은 바꾸지 않는다(DeepOpt 가 JSON 라벨 = XML 키 일치를 요구).

### BLD-03 · 저장된 Response 를 콤보에서 sanitize 양측 기준으로 찾는다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `W:restoreConfigurationUI` · `MW:restoreConfigurationUI` 의 `findText(response, MatchContains)` 를 콤보 항목마다 `sanitizeString(stripResponseParen(text)) == response` 비교로 바꾼다 (`W:refreshAvailableModelsTable` 이 이미 쓰는 방식).
- 완료 기준: (1) MCU 에서 헤더 `Temp (C)` 를 Output 으로 학습·저장 → 재진입 시 Response 콤보가 그 항목이다 (2) Sim 의 `이름 (Field)` · `이름 (Max)` 표시가 그대로 복원된다
- 변경 범위: view/DashModelBuilderWidget.cpp · view/DashModelBuilderMCUWidget.cpp
- 선행: -
- 충돌: BLD-06 (같은 두 함수) · B2 교집합: DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelBuilderWidget.cpp → 공유 10건(deps.md 5절)
- 흡수: BLD-D7 · BLD-c05
- 비고: 대조 규칙은 PM 순수 함수로 두면 단위 테스트가 된다.

### BLD-04 · [Load] 의 위젯↔모델 계약을 구분자 문자열에서 경로 인자로 바꾼다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `M:onLoadButtonClicked(const QString&)` 를 `(dir, file)` 두 인자(또는 절대경로 1개)로 바꾸고 `W:setModel` 의 loadButton 람다가 `"|"` 로 합치지 않게 한다.
- 완료 기준: (1) 소스에 `"|"` 조립·분할이 없다 (2) 디렉터리 콤보 + 파일 콤보로 [Load] 한 결과가 변경 전과 같다
- 변경 범위: model/DashModelBuilder.h · model/DashModelBuilder.cpp · view/DashModelBuilderWidget.cpp · view/DashModelBuilderMCUWidget.cpp (BLD-01 전이면 `onConfigLoaded` 호출부)
- 선행: -
- 충돌: BLD-20 (M:onLoadButtonClicked 첫머리에 공통 출처 검증 추가) · BLD-05 · BLD-14 · B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelBuilderWidget.cpp → 공유 10건(deps.md 5절) · DashModelBuilder.h → BLD-01 BLD-13 BLD-15
- 흡수: BLD-D2 · BLD-c02
- 비고: BLD-20 뒤에 하면 충돌이 사라진다.

### BLD-05 · shape 를 로드 시점에 정수 배열로 파싱하고 차원 셈을 그 길이로 바꾼다
- 종류: PR | 규모: M | 태그: C, E · refactor
- 목표: `LabelInfo` 에 `QVector<int> dims` 를 두고 `M:onLoadButtonClicked` 가 파싱한 값을 채운다. `LTH:getShapeDimension` · `calculateMaxEffectiveOutputDim` 과 그 소비처가 문자열 쉼표 셈 대신 길이를 쓴다. 표시 문자열은 파생값.
- 완료 기준: (1) `LTH:getShapeDimension`(:269) · `calculateMaxEffectiveOutputDim`(:333) 이 `dims.size()` 를 쓰고, 표 셀 텍스트를 역파싱해 차원을 구하는 호출(`W:976 shapeItem->text()` · `W:1219 si->text()`)이 0 이다. `calculateShapeFromJsonArrayString` 의 `count(',')`(M:281 · MCU:93) 는 shape **문자열 생성** 폴백이라 존치 (2) Input/Output 자동 분배 · 모델 목록(1D 7종/ND 1종) · 머리글 교체 · 특수 행 활성이 변경 전과 같다 (3) base64 shape 와 JSON 배열 shape 두 경로 모두 같은 dims 를 낸다
- 변경 범위: model/DashModelBuilder.h · model/DashModelBuilder.cpp · model/builder/ModelBuilderLabelTableHelper.h · model/builder/ModelBuilderLabelTableHelper.cpp · view/DashModelBuilderWidgetBase.cpp · view/DashModelBuilderWidget.cpp
- 선행: -
- 충돌: BLD-20 (M:onLoadButtonClicked) · BLD-04 · BLD-13 (LTH) · BLD-14 · B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderWidget.cpp → 공유 10건(deps.md 5절) · DashModelBuilder.h → BLD-01 BLD-15 · DashModelBuilderWidgetBase.cpp → BLD-02 BLD-06 BLD-07 UIC-21 · ModelBuilderLabelTableHelper.cpp → BLD-16
- 흡수: BLD-D3 · BLD-c03
- 비고: 표 셀(2열)은 문자열을 계속 보여주되 판정은 모델 쪽 dims 를 조회한다 — 셀 텍스트 역파싱이 남지 않게.

### BLD-06 · 설정 페이지 값 왕복을 레이아웃 인덱스가 아니라 jsonKey 로 짝짓는다
- 종류: PR | 규모: M | 태그: A, E · refactor
- 목표: `createModelConfigUI`(W·MW)가 만든 필드 위젯에 `objectName = jsonKey` 를 주고, `Base:getModelConfiguration` · `W:restoreConfigurationUI` · `MW:restoreConfigurationUI` 가 `itemAt(i, FieldRole)` 대신 키로 위젯을 찾는다. 숨긴 ND `critical_region_*` 도 같은 방식.
- 완료 기준: (1) 카탈로그(`PM::standardModelParameterCatalog` · MCU 카탈로그) 항목 순서를 바꿔 빌드해도 저장 JSON 의 키-값이 바뀌지 않는다 (2) 숨긴 ND 두 값이 이전과 같은 키로 기록된다 (3) MCU `checkbox_spin` 복원이 그대로다
- 변경 범위: view/DashModelBuilderWidgetBase.h · view/DashModelBuilderWidgetBase.cpp · view/DashModelBuilderWidget.cpp · view/DashModelBuilderMCUWidget.cpp
- 선행: -
- 충돌: BLD-03 (restoreConfigurationUI) · BLD-13 (MW 빈 루프) · B2 교집합: DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelBuilderWidget.cpp → 공유 10건(deps.md 5절) · DashModelBuilderWidgetBase.cpp → BLD-02 BLD-05 BLD-07 UIC-21
- 흡수: BLD-D5 · BLD-c09
- 비고: 숨긴 위젯 2종이 "화면에 없는 값을 기록" 하는 것은 그대로 둔다 — 노출 여부는 별개 결정.

### BLD-07 · 모델 행 [Delete] 가 설정 JSON 의 Configuration 항목도 지우고 MCU 도 산출물을 지운다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `M:deleteTrainedModel` 이 `Configuration.{model}` 을 설정 JSON 에서 제거한다(또는 별도 `removeModelConfiguration` 을 `Base:onRemoveModelRowClicked` 가 부른다). `aboutToRemoveModelRow` 의 산출물 삭제를 Base 기본 구현으로 올려 MCU 행 삭제도 `userPath` 산출물·`errors` 를 지운다.
- 완료 기준: (1) `Done` 모델 행 [Delete] 뒤 설정 JSON 에 그 모델 키가 없고 다음 [Start] 에 되살아나지 않으며 재로드 시 행이 없다 (2) MCU 행 [Delete] 가 `{userPath}/ModelBuilder_{Set}/{response}/{model}*` 와 `model_info.errors` 를 지운다
- 변경 범위: model/DashModelBuilder.cpp · view/DashModelBuilderWidgetBase.cpp · view/DashModelBuilderWidget.cpp
- 선행: -
- 충돌: BLD-02 · BLD-13 (M.cpp) · BLD-11 (결정 항목 ⑦ 과 같은 내용 — 이 항목이 "MCU 도 지운다" 로 선결) · B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderWidget.cpp → 공유 10건(deps.md 5절) · DashModelBuilderWidgetBase.cpp → BLD-05 BLD-06 UIC-21
- 흡수: BLD-D6 · BLD-c10, BLD-c17
- 비고: [Start] 의 `status == "Done"` 보존 루프는 유지한다 — 삭제된 모델이 남지 않으면 보존이 올바른 동작이다.

> **BLD-08 — 결번.** MCU 파일 행 `[...]` 람다의 행 번호 값 캡처(BLD-D10 · BLD-c18 · c35)는 같은 함수를 고치는 **UIC-23 에 병합**(B2) — RUN·BLD 두 MCU 위젯을 한 헬퍼로 고친다. 번호는 재사용하지 않는다.

### BLD-09 · MCU 헤더 검증의 기준 파일을 하나로 정하고 변경마다 전 행을 재검증한다
- 종류: PR | 규모: S | 태그: A, D · bug
- 목표: 기준 = "경로가 있는 첫 행의 헤더" 하나. `browseDatasetFile`(첫 파일 무검증 기록 · row==0 특례) · `onLoadButtonClickedMCU`(순회 중 처음 읽힌 파일) 의 분기를 없애고, 어느 행의 경로가 바뀌어도 전 행 State 를 다시 계산한다. 고정 15개(`PM::mcuFixedDatasetHeaders`)는 초기 표시·[Format] 전용으로 남긴다.
- 완료 기준: (1) 같은 파일 집합을 어떤 순서로 지정해도 State 결과가 같다 (2) 기준 행의 경로를 바꾸면 나머지 행 State 가 즉시 바뀐다 (3) 규칙이 PM 순수 함수로 있다 (단위 테스트는 BLD-19 의 TU 가 고정)
- 변경 범위: view/DashModelBuilderMCUWidget.cpp · viewmodel/DashModelBuilderPresentationModel.h · viewmodel/DashModelBuilderPresentationModel.cpp
- 선행: -
- 충돌: BLD-01 (헤더 재구성 공유 함수) · UIC-23 (MW — BLD 몫 병합) · B2 교집합: DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelBuilderPresentationModel.cpp → BLD-16
- 흡수: BLD-D11 · BLD-c19
- 비고: 대안 — 고정 15개 강제(`validateDatasetFile` 완전 일치가 이미 그 방향). [Load] 가 첫 파일 헤더로 Input/Output 을 재구성하는 현행 동작은 임의 헤더를 허용한다는 뜻이라 "첫 행 기준" 을 택했다. 고정 강제를 택하면 BLD-11 에서 결정.

### BLD-10 · MCU 학습 종료를 위젯이 관측해 버튼을 되돌리고, 쓰지 않는 폴링 타이머를 끈다
- 종류: PR | 규모: S | 태그: B · bug
- 목표: `MCU:onTrainingStartButtonClicked` 가 `m_statusCheckTimer` 를 켜지 않는다. `MCU:onDaemonCommandCompleted(train)` 이 `trainingSucceeded`, `onDaemonCommandFailed` 가 `trainingFailed` 를 발행한다. `MW:setModel` 이 두 시그널을 연결해 Start/Stop 을 되돌리고 결과 표를 갱신하며, `MW:onModelStatusUpdated` 도 `"Running"` 행이 없으면 되돌린다.
- 완료 기준: (1) MCU 학습 정상 종료 뒤 Start 활성·Stop 비활성 (2) 데몬 명령 실패 시 같은 복귀 + 오류 통지 (3) 학습 중 `checkModelStatus` 가 호출되지 않는다 (4) [Stop] 이 `Interrupted` 와 데몬 재기동에 도달한다 (#548 해소 재확인)
- 변경 범위: model/DashModelBuilderMCU.cpp · view/DashModelBuilderMCUWidget.cpp
- 선행: -
- 충돌: BLD-01 · BLD-12 (MW:setModel) · B2 교집합: DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelBuilderMCU.cpp → BLD-13 BLD-17 BLD-18 PRJ-09 UIC-20
- 흡수: BLD-D13 · BLD-D15 · BLD-c20, BLD-c22 · (BLD-D14 해소 확인 · BLD-c21) · EXE-c37 · BLD-c37 · #463(BLD 몫) · EXE-c23 · BLD-c41
- 비고: Sim 과 같은 `trainingSucceeded/Failed` 계약으로 맞추는 것이 핵심 — 위젯이 데몬 시그널을 직접 알 필요가 없다. #463 BLD 몫: Start 비활성·Stop 취소는 Sim(W:959)·MCU(MW:1046) 모두 현행이고 빠진 것은 MCU 복귀(이 항목)뿐 — 상태바 진행 표시는 EXE-07 규약 확정 뒤 같은 시그널에 얹는다.

### BLD-11 · Sim·MCU 쌍둥이 계약의 통일 방향을 항목별로 결정한다
- 종류: DEC | 규모: S | 태그: E, A · refactor
- 목표: 베이스를 공유하면서 갈라진 계약 중 **결정이 남은 4종**을 "유지 / 통일(후속 항목) / EXT" 로 확정한다. ① status 문자열·저장 위치(설정 JSON vs `model_info.json models.*`, 후자는 DashOptiMCU.exe 가 씀) ② 산출 루트(`.dproj` vs 사용자 루트 — `DashIOController::getModuleDir` 의 ModelBuilder 특례 `DashIOController.cpp:30-31`) ⑤ Test Results 탭 활성 조건 ⑥ [Set Dataset] 의 Input 체크 저장 규칙(Sim 전 행 vs MCU 체크 행 — DeepOpt 는 Input 키 전부를 쓴다). 나머지 3종은 **PR 항목이 이미 결론을 내고 있어 결정 대상이 아니다** — ③ `Dataset` 형 = 유지(BLD-01 비고) · ④ Data Label 을 쓰는 계층 = 모델 계층으로 통일(BLD-12) · ⑦ 행 삭제 시 산출물 삭제 = MCU 도 지운다(BLD-07). 이 결정 기록은 그 3건을 "PR 선결" 1줄로만 적는다
- 완료 기준: 결정 기록 — 항목 4개(①②⑤⑥) 각각 결론·근거·후속 항목 ID + ③④⑦ 의 PR 선결 1줄. ①②는 하류(Runner·Optimizer 가 읽는 `model_info.json` 경로)와 DashOptiMCU 출력 규약에 묶이므로 RUN·OPT·EXE 접점을 명시한다. ② 가 "통일" 로 결정되면 후속 PR 1건(Sim 산출 루트 이행 + Runner·Optimizer 읽기 경로 동반 수정)을 BLD 에 추가한다
- 변경 범위: (결정 문서) — 코드 없음
- 선행: -
- 충돌: -
- 흡수: BLD-D9 · BLD-c11, BLD-c12, BLD-c14, BLD-c15, BLD-c16
- 비고: ② 는 저장 위치 결정이라 되돌리기 비용이 크다 — "나중에 교체" 전제로 정하지 않는다. 결정만 남고 실행이 비면 안 되므로 후속 PR 을 완료 기준에 못박았다. ⑥ 은 Sim 의 Input 체크박스가 현재 무의미하다는 사실 확인이 선행.

### BLD-12 · MCU Data Label 저장을 위젯 직쓰기에서 모델 계층으로 옮긴다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `MW:onSetButtonClicked` · `MW:onStartTrainingClicked` 의 설정 JSON read-modify-write 두 곳을 없애고 `DashModelBuilderMCU::updateAndSaveConfig(files, inputLabels, outputLabels)` 가 `PM::mcuDataLabelJson` 으로 쓴다. Sim 의 `updateAndSaveConfig → saveDataLabelConfig` 와 같은 층위.
- 완료 기준: (1) MW 에 `QFile`/`QJsonDocument` 로 설정 JSON 을 쓰는 코드가 없다 (2) 저장 JSON 내용이 변경 전과 같다(Dataset 배열 · 원문 키 · 섹션 보존)
- 변경 범위: model/DashModelBuilderMCU.h · model/DashModelBuilderMCU.cpp · view/DashModelBuilderMCUWidget.cpp
- 선행: BLD-01 (MCU 모델이 파일 목록을 상태로 들어야 그 위에 저장 경로를 둔다)
- 충돌: BLD-10 (MW:setModel) · BLD-11 ④ · B2 교집합: DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelBuilderMCU.cpp → BLD-13 BLD-17 BLD-18 PRJ-09 UIC-20 · DashModelBuilderMCU.h → BLD-15 BLD-20
- 흡수: BLD-D9(쓰는 계층) · BLD-c14
- 비고: -

### BLD-13 · 죽은 코드를 세 층에서 제거한다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: 호출처 0 인 것을 지운다 — `LTH:populateIoTable·updateLabelTable·populateTableRow·moveSelectedLabels`(Base 에 동명 구현) · `Base:populateIoTable` · `M:getDatasetFiles`+`m_datasetFiles`+`setProjectDirectory` 의 디렉터리 스캔 2덩어리 · `M:getInputTableSetOptions·getInputTableReductionOptions·getOutputTableSetOptions·getOutputTableReductionOptions` · `M:getTrainedModelError`(Deprecated) · `M:loadLabelMetadata`+`m_labelMetadata`(write-only) · `MW:restoreConfigurationUI` 의 빈 중첩 루프 · `MCU.cpp` "inherited" 주석 블록(stopTraining 행이 사실과 다름) · W·MW 의 `static sanitizeString` 래퍼.
- 완료 기준: (1) 열거한 심볼이 저장소에서 사라지고 빌드가 통과한다 (2) `setProjectDirectory` 가 config 경로 계산 → `loadDataLabelConfig` 만 수행한다 (3) 동작 변화 없음(Set 선택·Load·학습·결과 열람 수동 확인)
- 변경 범위: model/builder/ModelBuilderLabelTableHelper.h · model/builder/ModelBuilderLabelTableHelper.cpp · view/DashModelBuilderWidgetBase.h · view/DashModelBuilderWidgetBase.cpp · model/DashModelBuilder.h · model/DashModelBuilder.cpp · model/DashModelBuilderMCU.cpp · view/DashModelBuilderMCUWidget.cpp · view/DashModelBuilderWidget.cpp
- 선행: -
- 충돌: BLD-02 · BLD-05 · BLD-06 · BLD-07 · BLD-20 (`loadLabelMetadata` 삭제 적용 접점) · B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelBuilderWidget.cpp → 공유 10건(deps.md 5절) · DashModelBuilderMCU.cpp → BLD-01 BLD-10 BLD-12 BLD-17 BLD-18 PRJ-09 UIC-20 · DashModelBuilder.h → BLD-01 BLD-04 BLD-14 BLD-15 · DashModelBuilderWidgetBase.cpp → UIC-21 · ModelBuilderLabelTableHelper.cpp → BLD-16
- 흡수: BLD-U1 · BLD-c23 · (BLD-c21 잔재 주석)
- 비고: `fileListUpdated` 시그널은 스캔 제거 뒤에도 콤보 갱신 트리거로 쓰이는지 확인 — W·MW 가 `updateAnalysisLauncherDirComboBox` 에 연결한다. T22 가 `loadLabelMetadata` 에 얹는 키 필터는 **기다리지 않는다** — 이 항목이 그 함수를 지우면 필터 자체가 불필요하고(#368 본문도 "방어 조치 · `m_labelMetadata` 가 write-only 라 무해" 로 적는다), 머지를 기다리면 방금 추가된 코드를 다시 지우는 왕복이 된다. BLD-20과 삭제 적용 순서만 조율하고 해당 옛 필터 hunk는 도입하지 않는다.

### BLD-14 · Set 단위 Preprocess XML(응답 N 개)을 Builder 로더가 읽는다
- 종류: PR | 규모: M | 태그: A, C · feature
- 목표: #643 1차 포맷(Analysis Launcher Set 당 XML 1개, 응답을 그 안에 추가)에 맞춰 `M:onLoadButtonClicked` 의 샘플 라벨 열거와 `M:parseModelInfoStream·readSelectedResponseFromStream` 의 `selected_response` 단일 dict 전제를 복수 응답으로 바꾸고, `loadModelInfoFromXml` 의 head/tail 조각 탐색(`model/DashXmlTailLocator.h`)이 새 레이아웃에서 성립하는지 맞춘다. 학습 시작 시 `model_info.json` 이식도 응답별 메타를 싣는다.
- 완료 기준: (1) 응답 2개가 든 Set XML 을 [Load] 하면 Output 표에 두 응답이 각각 shape 와 함께 뜬다 (2) 학습 시작 뒤 `model_info.json` 에 두 응답의 메타가 있다 (3) 구 포맷(응답 1개) XML 도 그대로 로드된다 (4) 응답 2개 dataset 으로 1D·ND 학습이 끝까지 돈다 (5) DeepOpt 리더 계약 대조 — 응답 추가가 `root` 첫 자식(학습 데이터)과 샘플 dict 동형을 깨지 않는다. `model_info` 는 샘플 앞으로 옮기지 않는다 (6) **샘플 0 위상으로 나머지를 읽는다** — 위상(`node_location`·`connectivity`)이 샘플 0 에만 있는 XML(PRE-31 산출)을 [Load] 해도 라벨 열거가 그대로이고, 그 2키의 Shape 열에 샘플 수 `dataCount` 접두가 붙지 않는다(파일 단위 값이므로). 샘플 1..N 을 되읽는 코드가 새로 생기지 않는다 · `dashModelInfoMatchesFirstSample` 의 "model_info 파라미터 ⊆ 샘플 0 키" 불변과 꼬리 창 크기 전제(`DashXmlTailLocator.h` 전제 9·13)가 새 레이아웃에서 성립
- 변경 범위: model/DashModelBuilder.h (`LabelInfo`) · model/DashModelBuilder.cpp (onLoadButtonClicked :373-418 샘플 0 열거·`dataCount` 접두 :394-408 · parseModelInfoStream · readSelectedResponseFromStream · loadModelInfoFromXml) · model/DashXmlTailLocator.h (전제 9·13 — 샘플 0 키 집합·꼬리 창) · view/DashModelBuilderWidget.cpp (응답 선택 UI 가 필요해질 때만)
- 선행: PRE-29 · PRE-30 (XML 규격) · PRE-31 (위상 1회 쓰기) · BLD-16 (복수 응답 학습 실측)
- 충돌: BLD-20 (parseModelInfoStream) · BLD-04 · BLD-05 (onLoadButtonClicked) · B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderWidget.cpp → 공유 10건(deps.md 5절) · DashModelBuilder.h → BLD-01 BLD-13 BLD-15
- 흡수: #643 (BLD 몫) · BLD-c26 · PRE-c54(#643 추가 1) · BLD-c33 · PRE-c56(#643 추가 3 — 2차) · BLD-c39 · PRE-c55(#643 추가 2 — 로더 수용 몫만, 작성기는 PRE-31)
- 비고: PRE·BLD 양쪽이 지켜야 하는 DeepOpt 리더 계약(PRE-c59 → BLD-c34 로 넘어온 제약, 완료 기준 (5)) — DeepOpt 는 `root` 의 첫 자식만 학습 데이터로 읽고 **샘플 dict 가 동형**이어야 한다. `model_info` 를 샘플 앞으로 옮기거나 샘플 dict 구조를 바꾸면 Builder 가 읽어도 DeepOpt 와 호환되지 않는다 — 응답 추가는 샘플 dict 안의 키로만 한다. 복수 응답의 학습 성립 자체는 미확인(BLD-c44) — BLD-16 ⑥ 의 실측이 "불가" 면 이 항목은 EXT(DeepOpt) 동반이다. #643 추가 1 의 "개발 중인 Builder 다중 part 포맷" 은 dev 에 없다(BLD-c33) — 규격이 나오면 PRE-30 의 입력. 2차(HDF5) 는 PRE 결정 뒤 로더 교체 항목을 따로 낸다(L 예상, `DashXmlParser` 캐시 #515 와 함께 — 학습 본체 DeepOpt 리더 동반, BLD-16 ⑤).
  완료 기준 (6) 은 PRE-31(위상 1회 쓰기)의 `보류: BLD 몫` 수용이다 — 현행 로더는 이미 샘플 0 만 열거하므로(`inKeyZeroDict` 루프) 위상이 샘플 0 에만 있어도 라벨 목록은 깨지지 않는다. 실제로 손볼 것은 두 가지뿐이다: ① `dataCount` 접두가 파일 단위 위상 2키에도 붙어 `[N, nodes, 3]` 으로 표시되는 것을 제외 ② `DashXmlTailLocator` 의 꼬리 창이 "샘플 0 항목 수 × 상수" 라 위상·응답이 샘플 0 에만 모이면 창이 커지는 쪽(안전측)이므로 전제 재확인만. 샘플 1..N 을 되읽는 코드를 새로 만들지 않는 것이 수용의 요점이다 — 새로 만들면 PRE-31 의 절감이 사라진다. ANA 는 같은 성격의 보류를 ANA-23(결과 XML 스키마 변경의 파서 수용)으로 받았다.
  PR #658(draft, Registry #82 — preprocessor v3) 의 `DashResultXmlWriter.cpp` hunk 를 확인했다: 응답 배열을 인덱스 0 대신 이름(`field_output_name`/`result`)으로 고르고, 응답 `dict_item` 에 `quantity`·`unit`·`component_labels` 속성을 더하고, eigenvalue 가 있는 모달 스텝의 응답 키를 `resName` → `Eigenvalue` 로 바꾼다. 샘플 dict 구조와 `model_info` 위치는 그대로이고 BLD 함수 본문도 건드리지 않으므로 **선행 아님**. 다만 `component_labels` 는 이 항목의 "응답별 메타" 입력이고, `Eigenvalue` 키 변경은 기존 `ModelBuilder_{Set}.json` 의 라벨 키와 어긋나므로 완료 기준 (3)(구 포맷 로드)의 확인 대상에 포함한다.

### BLD-15 · Builder가 실제 소비한 입력 버전으로 최신성을 판정한다
- 종류: PR | 규모: M | 태그: C, A · feature
- 목표: #650 규칙에 따라 학습에 실제 사용한 dataset 생산 Set·입력 버전을 결과와 함께 기록하고 DashModelBuilder::upstreamStaleReasons가 현재 상류 버전과 비교한다. 현재 Launcher 참조 선택만으로 과거 결과의 소비 버전을 덮지 않는다.
- 완료 기준: ① 실제 dataset 사용 버전 기록 ② 같은 Launcher Set의 산출물 재생성 시 규칙에 따른 최신성 사유 ③ 누락·비교 불가 상태를 PRJ-23 결정대로 처리 ④ 프로젝트 집계·VM 표시에서 Set 판정 결과 사용. MCU는 적용 입력의 버전을 판정하며 deck 비해당을 최신성 전체 면제로 취급하지 않는다.
- 변경 범위: model/DashModelBuilder.h · model/DashModelBuilder.cpp · model/DashModelBuilderMCU.h
- 선행: PRJ-23 (#650 버전·판정 규칙)
- 충돌: BLD-20 (같은 Set JSON) · BLD-14 · B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilder.h → BLD-01 BLD-04 BLD-05 BLD-13 · DashModelBuilderMCU.h → BLD-01 BLD-12
- 흡수: #650 (BLD 몫) · BLD-c25 · PRJ-c36 · BLD-c36
- 비고: BLD-20은 참조·출처, 본 항목은 버전·최신성이다. 생산 dataset 버전 기록은 #650의 생산 측 범위로 함께 정의하며 #643 포맷 전환을 일괄 선행으로 두지 않는다. PRJ-22 집계 구조와 공유 파일 적용 순서만 조율한다.

### BLD-16 · DeepOpt 가 실제로 읽는 설정 키·토큰을 실측해 GUI 옵션과 맞춘다
- 종류: INV | 규모: S | 태그: A, G · bug
- 목표: 배포 `DashOptiDeepOpt.exe` 기준으로 ① Output reduction 토큰 집합(`Sum` vs `SUM`, 1D·ND 각각) ② Output `transformation` 소비 여부 ③ Input `reduction` 소비 여부 ④ `Configuration.<model>.response` 가 학습 대상을 제한하는지 ⑤ 학습 본체가 dataset XML 을 직접 읽는 리더의 입력 계약(#411 결정 2 — 포맷 교체 시 동반 변경 범위) ⑥ **복수 응답이 든 dataset 1개로 1D·ND 학습이 성립하는지** — 1D 의 라벨↔열 대응, StableNet 의 응답 연결 제약(위키 "다성분과 복수 응답" 행, BLD-c44) 을 실측한다.
- 완료 기준: 실측 결과 기록 + 후속 분기 — ① 불일치면 GUI 토큰 수정(S PR, `LTH:getReductionOptionsForShape`) 또는 EXT ②③ 미소비면 GUI 옵션 제거(S PR) 또는 EXT(DashOptiDeepOpt 구현) ④ 는 계약 결정(DEC, 행별 Response 의 의미) ⑥ "불가" 면 BLD-14 는 EXT(DeepOpt 복수 응답 지원) 동반 — BLD-14 의 선행으로 등록돼 있다
- 변경 범위: (조사) model/builder/ModelBuilderLabelTableHelper.cpp · viewmodel/DashModelBuilderPresentationModel.cpp · model/DashModelBuilder.cpp · 외부 DashOptiDeepOpt
- 선행: -
- 충돌: B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderPresentationModel.cpp → BLD-01 BLD-09 · ModelBuilderLabelTableHelper.cpp → BLD-05 BLD-13
- 흡수: Model-Builder-XML-DeepOpt-Pipeline "구현 차이" · BLD-c27, BLD-c28, BLD-c29, BLD-c30, BLD-c44 · #411(결정 2 — BLD 몫) · PRE-c59 · BLD-c34
- 비고: 위키는 DeepOpt `a4222b6` 로컬 소스 정적 대조다 — 배포 EXE 가 같은 커밋인지 확인하지 않았다.

### BLD-17 · 설정 JSON·model_info.json 직쓰기를 공용 JSON 헬퍼로 이행한다
- 종류: PR | 규모: S | 태그: A · refactor
- 목표: `QFile::open(WriteOnly, Truncate)` 직쓰기 7지점 — M:onTrainingStartButtonClicked(:520 설정 · :602 model_info) · createModelInfoJson(:783) · saveDataLabelConfig(:934) · deleteTrainedModel(:2342) · MCU:onTrainingStartButtonClicked(:557 · :688) — 를 PER-02 가 공용 진입점으로 승격하는 **DashSaveSystem 헬퍼**(`persistence/DashSaveSystem::read/writeJsonFile` — QSaveFile · `Result` 반환)로 바꿔 원자 쓰기·사유 반환·(PER-04 뒤) 버전 키를 얻는다. MW:onSetButtonClicked(:819)·onStartTrainingClicked(:984) 2지점은 BLD-12 가 모델 계층으로 옮긴 뒤 같은 헬퍼를 탄다. `onDownloadFormatButtonClicked`(:1729 CSV 양식)은 산출물이라 제외.
- 완료 기준: BLD 5파일에서 `QIODevice::WriteOnly` 가 CSV 양식 1곳뿐 / 쓰기 실패(읽기 전용 경로) 시 기존 파일 바이트 동일 + 통지 1건 / 학습 시작·Set Dataset·Delete 동작 불변
- 변경 범위: model/DashModelBuilder.cpp · model/DashModelBuilderMCU.cpp (BLD-12 뒤면 view/DashModelBuilderMCUWidget.cpp 는 제외)
- 선행: PER-02 · BLD-12 (MCU 모델 저장 경로)
- 충돌: BLD-20 (M:onTrainingStartButtonClicked) · BLD-02 · BLD-07 · BLD-13 · BLD-18 (같은 쓰기 지점) · B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderMCUWidget.cpp → 공유 11건(deps.md 5절) · DashModelBuilderMCU.cpp → BLD-01 BLD-10 PRJ-09 UIC-20
- 흡수: #479(BLD 몫) · #478(BLD 몫) · #480(BLD 몫) · PER-c27 · PER-c08(BLD 5지점) · BLD-c38
- 비고: `model_info.json` 은 출처 기록 자리 — 헬퍼 이행과 출처 쓰기가 같은 함수를 지난다

### BLD-18 · Builder가 학습 산출물 버전을 기록한다
- 종류: PR | 규모: S | 태그: C, A · feature
- 목표: #650의 PRJ-23 규칙에 따라 생산 Builder Set이 model_info.json에 학습 산출물 버전을 기록한다. 동일 setId의 재학습 전후를 구분하며 갱신 시점·실패 처리는 결정된 버전 의미를 따른다.
- 완료 기준: 규칙이 정한 재생성 경계에서 버전이 바뀌고 재진입·단순 입력 선택으로 기존 산출물 버전이 바뀌지 않는다. Runner·Optimizer가 실제 사용한 버전과 비교 가능하다. MCU도 해당 학습 산출물 버전을 기록한다.
- 변경 범위: model/DashModelBuilder.cpp (createModelInfoJson :740-792 · onTrainingStartButtonClicked :602), model/DashModelBuilderMCU.cpp (onTrainingStartButtonClicked :688)
- 선행: PRJ-23
- 충돌: BLD-20 (같은 쓰기 지점) · BLD-17 (같은 쓰기 지점) · BLD-07 · B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderMCU.cpp → BLD-01 BLD-10 BLD-12 BLD-13 PRJ-09 UIC-20
- 흡수: #650(Model Builder 산출 id — 생산자 몫) · PRJ-c37(생산자 몫) · BLD-c43
- 비고: 소비 판정은 RUN-31·OPT-23. BLD-20 출처 기록과 저장 위치를 조율하되 같은 파일이라는 이유로 상호 선행을 걸지 않는다. setId는 버전 발급과 무관하게 유지한다.

### BLD-19 · Model Builder 의 순수 함수에 단위 테스트 타깃을 둔다 — ConfigHelper · LabelTableHelper · PM
- 종류: PR | 규모: S | 태그: F · refactor
- 목표: `tests/` 에 `DashModelBuilder`·builder 헬퍼 참조 0 (#489 · DEV-c24). GUI·데몬 없이 도는 TU 1개 — CH:createInputLabelsJsonObject/createOutputLabelsJsonObject ↔ parseDataLabelSection 왕복(sanitize 키 · transformation · Dataset 문자열/배열) · LTH:getShapeDimension · getReductionOptionsForShape · PM::buildTrainingStartPlan · mcuDataLabelJson/mcuDatasetArrayJson · standardModelParameterCatalog 키 집합.
- 완료 기준: tests/CMakeLists.txt 에 `test_model_builder_helpers` 등록 · ctest 통과 / BLD-02 · BLD-05 · BLD-09 의 완료 기준이 이 TU 로 고정
- 변경 범위: tests/CMakeLists.txt, tests/TestModelBuilderHelpers.cpp (신규)
- 선행: -
- 충돌: BLD-02 · BLD-05 · BLD-09 (고정하는 동작 — 먼저 쓰고 각 PR 이 갱신) · DEV 의 tests 인프라 항목 · B2 교집합: tests/CMakeLists.txt → 공유 12건(deps.md 5절) · PR #655(tests/CMakeLists.txt) · PR #654(tests/CMakeLists.txt) · PR #652(tests/CMakeLists.txt) · PR #651(tests/CMakeLists.txt)
- 흡수: #489(BLD 몫) · DEV-c24(BLD) · BLD-c42
- 비고: `DashModelBuilder` 본체는 `DashProjectManager::Instance()` 역참조라 TU 밖 — 경로 주입은 PRJ-09 뒤. `LTH:calculateMaxEffectiveOutputDim` 은 QTableWidget 입력이라 제외. CAD-11 · OPT-20 과 같은 형태

### BLD-20 · Builder가 Launcher 입력 참조를 저장하고 학습 산출물 출처를 기록한다
- 종류: PR | 규모: M | 태그: C, A · feature
- 목표: #368의 완료 지점. 실제 dataset을 생성한 Launcher setId와 dataset·응답·모델·part 등의 선택을 ModelBuilder Set 설정에 저장·복원한다. 공통 판독으로 dataset 출처를 검증한 뒤 model_info.json에 생성 Builder setId와 실제 dataset·상류·deck 출처를 기록한다. 현재 Builder ID를 유지하면서 다른 Launcher 참조를 선택할 수 있다.
- 완료 기준: ① 다른 유효 Launcher setId의 dataset 선택·저장·복원 가능 ② 선택만 바꾸면 기존 model_info 출처 불변 ③ 재학습 결과 덮어쓰기 때 실제 출처도 갱신 ④ 필수 출처 없는 구 dataset은 재생성 안내, 이름·경로 추론·자동 이관 금지 ⑤ Set 미지정 상태에 임의 기본 Set으로 저장하지 않음 ⑥ MCU CSV 입력은 deck 비해당 관계를 계약에서 구분하되 Builder 식별·실제 입력 기록을 생략하지 않음.
- 변경 범위: model/DashModelBuilder.h · model/DashModelBuilder.cpp · model/DashModelBuilderMCU.h · view/DashModelBuilderWidget.cpp
- 선행: PRE-32
- 충돌: BLD-01 (M.h 가상 훅 인접) · BLD-02 · BLD-04 · BLD-05 (M:onLoadButtonClicked) · BLD-03 · BLD-06 (W:setModel) · BLD-07 (M.cpp · W.cpp) · BLD-12 (MCU.h) · BLD-13 (이 항목이 뒤) · BLD-14 (parseModelInfoStream) · BLD-15 (같은 Set JSON) · BLD-16 (M.cpp) · BLD-17 · BLD-18 (M:onTrainingStartButtonClicked 의 같은 쓰기 지점) · B2 교집합: DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashModelBuilderWidget.cpp → 공유 10건(deps.md 5절)
- 흡수: #368 Phase 3(T22) · BLD-c24 · BLD-c32 · LCH-c37
- 비고: #530 hunk는 수정 지점 참고만 하며 write-once·핀 불일치 차단을 이식하지 않는다. BLD-13의 loadLabelMetadata 삭제와는 파일 충돌만 조율한다. 버전·최신성은 BLD-15·BLD-18(#650), 소비 검증은 RUN-34·OPT-26(#685). 공통 판독 테스트와 실제 Set 왕복·재학습으로 검증한다.

### BLD-21 · ND 판정을 응답 속성 술어 하나로 모은다 — `(Field)` 직접 판정 2곳과 모델 이름 카탈로그 분기를 걷어낸다
- 종류: PR | 규모: S | 태그: C · bug
- 목표: RUN-15 가 `DashSurrogateModelCommon` 에 두는 "응답 표시 이름 → ND" 술어를 호출로 바꾼다 — `W:updateModelError`(:1089, 지표 머리글 ND/1D 선택) · `W:hasNDModelInConfiguration`(:1681, Test Results 탭 활성). 같은 함수의 `ndModelNames()` OR 분기(:1675)는 지운다 — 카탈로그 5건이 `DashModelBuilder::getModelsForDimension(3)`={"StableNet"} 1건과 어긋난 중복이고 RUN-15 가 정본 아님으로 확정했다. `PM:rankTestResultsFolders`(:227)의 `ndModelNames()` 는 학습 산출 **폴더 이름** 접두 분류라 남긴다.
- 완료 기준: (1) `view/DashModelBuilderWidget.cpp` 에 `contains("(Field)")` 0건 — 전부 공용 술어 호출 (2) `hasNDModelInConfiguration` 이 응답 축만 본다 — 모델 이름이 `ndModelNames()` 안이어도 응답에 `(Field)` 가 없으면 Test Results 탭이 켜지지 않는다 (3) 같은 행에서 `W:updateModelComboBox`(:1049)의 `effectiveModelDimension(baseDim, reduction).isND` 와 술어 결론이 일치한다 — 생산 지점 `PM:responseDisplayText`(:176-178)가 같은 조건이라 코드 변경 없이 성립해야 하고, 어긋나면 응답 콤보 텍스트가 낡은 것이므로 갱신 순서를 고친다 (4) 지표 머리글·Test Results 탭 활성이 같은 입력에서 변경 전과 같다
- 변경 범위: view/DashModelBuilderWidget.cpp
- 선행: RUN-15 (공용 술어 신설 — 없으면 호출할 대상이 없다. `ndModelNames()` 자체는 RUN-15 가 BLD 용으로 남긴다)
- 충돌: BLD-11 ⑤ (Test Results 탭 활성 조건 결정 — 같은 함수. 이 항목은 "무엇이 ND 인가" 만 고치고 Sim/MCU 갈림은 BLD-11 몫) · BLD-05 (W:updateModelComboBox 의 `baseDim` 산출) · BLD-19 (술어 ↔ `effectiveModelDimension` 일치 케이스를 그 TU 에 둘 수 있다) · B2 교집합: DashModelBuilderWidget.cpp → 공유 10건(deps.md 5절)
- 흡수: RUN-D6(BLD 몫) · BLD-c45
- 비고: RUN 2차 반영이 코드로 재확인한 `(Field)` 판정은 5곳이 아니라 6곳이다 — RUN `W:962`·`view/common/SurrogateTableController.cpp:29`(RUN-15) · BLD `W:1089`·`W:1681`(이 항목) · OPT `DashOptimizerWidget.cpp:556`·`:867`(OPT 몫). 생산은 1곳 `PM:responseDisplayText`(:178) → `Base:getOutputResponseList`(:299) → `Output Response` → model_info `errors` 키. **생산자가 BLD** 이므로 술어의 정본 조건(`baseDim==3 && reduction=="None"`)은 BLD 가 쥐고 있다 — RUN-15 가 술어를 공용층에 옮길 때 그 조건을 그대로 옮기는지 확인한다. 번호는 BLD-21 — BLD-08 은 결번이라 재사용하지 않는다(위 BLD-07 뒤 주석).

## 대응표

| 원천 | 항목 | 비고 |
|---|---|---|
| BLD-D1 | 항목 없음 — 범위밖 → PRJ | Set variant 정본 단일화(DashProject · DashMainWindow). Runner·Geometry·DoeSampler 도 같은 구조 |
| BLD-D2 | BLD-04 | |
| BLD-D3 | BLD-05 | |
| BLD-D4 | BLD-02 | Sim 에선 잠재 (XML 작성기가 같은 sanitize 규칙) |
| BLD-D5 | BLD-06 | ← UIC-c58 (BLD-c40) |
| BLD-D6 | BLD-07 | |
| BLD-D7 | BLD-03 | MCU 에서 실발현 |
| BLD-D8 | BLD-02 | |
| BLD-D9 | BLD-11 (결정) · BLD-01 (Dataset 형) · BLD-12 (쓰는 계층) · BLD-07 (행 삭제) | status 통로·산출 루트·탭 조건·Input 체크 규칙은 결정 뒤 후속 |
| BLD-D10 | → UIC-23 | BLD-08 결번 — UIC-23 병합(B2) — ← RUN-c14 · #474(BLD-D10 축) (BLD-c18 · c35). UIC-23 이 RUN·BLD 두 MCU 위젯을 한 헬퍼로 고친다 |
| BLD-D11 | BLD-09 | |
| BLD-D12 | BLD-01 | |
| BLD-D13 | BLD-10 | ← EXE-c37 (BLD-c37) |
| BLD-D14 | 항목 없음 — 해소됨 | c055711c (#548 · PR #579). 잔재 주석은 BLD-13 |
| BLD-D15 | BLD-10 | |
| BLD-U1 | BLD-13 | |
| BLD-U3 | BLD-02 | |
| #643 | BLD-14 | 선행 PRE 1차. 2차(HDF5) 는 PRE 결정 뒤 별도 · ← PRE-c54 추가 1 (BLD-c33, dev 에 포맷 0건) · PRE-c56 추가 3 (BLD-c39) · ← PRE-c55 추가 2 의 로더 수용 몫 (BLD-c26 보강, 완료 기준 (6) — 작성기는 PRE-31) |
| RUN-D6 (BLD 몫) | BLD-21 | ← RUN-c24 (BLD-c45). `(Field)` 판정 6곳 중 BLD 2곳 (`W:1089`·`W:1681`) + 모델 이름 카탈로그 OR 분기 삭제. `선행: RUN-15`(술어 신설). 생산 1곳 `PM:178` 은 정본이라 유지 |
| #650 | BLD-15(소비 버전 판정) · BLD-18(생산 버전 기록) | 프로젝트 호출·집계, VM 표시. 출처 계약과 별도 |
| #368 | BLD-20 (생산 완료) | PRE-32 입력 출처 판독 → model_info.json 기록. PR #530 hunk는 참고만 하며 BLD-13과는 삭제 적용 접점 조율. 공통부 PER-06·PER-07 · ← LCH-c37 (BLD-c24 · BLD-c32) |
| Model-Builder-XML-DeepOpt-Pipeline "구현 차이" | BLD-16 | ⑥ 복수 응답 학습 성립은 BLD-c44 (BLD-14 의 전제). `model_info` 위치·샘플 dict 동형 제약은 BLD-14 완료 기준 (5) |
| Code-Map-User-Flow-Model-Builder 3-3 (Input 체크 저장) · 4절 (MCU 행 삭제) | BLD-11 ⑥ · BLD-07 | 위키 본문에서 추가 발견 (c16 · c17) |
| QMessageBox 23곳 (c31) | 항목 없음 — 범위밖 → UIC | #447~#450 통지 래퍼에 건수 제공 |
| #479 · #478 · #480 (BLD 몫) | BLD-17 | ← PER-c27 (BLD-c38) |
| #411 결정 2 (BLD 몫) | BLD-16 ⑤ | ← PRE-c59 (BLD-c34) |
| #463 (BLD 몫) | BLD-10 | ← EXE-c23 (BLD-c41). 가드·취소는 현행 |
| #489 (BLD 몫) | BLD-19 | ← DEV-c24 (BLD-c42) |
