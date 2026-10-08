# ANA 작업 목록

> 기준 dev @ b08a91b3. 원자 항목은 02-claims/ANA.md. 항목 대부분이 `view/DashResultsAnalyzerWidget.cpp`(4,201줄) 한 파일을 고치므로 **같은 파일 항목은 직렬로 진행**한다 (각 항목 `충돌` 참조).

### ANA-01 · SHAP 데이터셋 콤보 콜백에 파일 존재 가드를 둔다
- 종류: PR | 규모: S | 태그: B · bug
- 목표: `createShapWidget` 의 데이터셋 콤보 콜백이 `extractVariablesFromXml` 을 부르기 전에 형제 호출부(`onTargetDataChanged`)와 같은 `QFileInfo::exists()/isFile()` 가드를 둔다. 디렉터리·권한 거부 경로에서 콤보 조작마다 반복되던 `canOpenForRead` WARN 과 재시도가 사라진다.
- 완료 기준: 존재하지 않는 경로를 데이터셋으로 고르면 WARN 이 1회 이하로 남고 feature 콤보가 비어 있다 / 정상 XML 은 종전과 같이 채워진다
- 변경 범위: view/analyzer/DashPlotWidgetFactory.cpp (createShapWidget 람다 :1269-1290)
- 선행: -
- 충돌: ANA-14 (같은 파일 — 팩토리 죽은 진입점 삭제) · B2 교집합: DashPlotWidgetFactory.cpp → ANA-09 ANA-12 UIC-12
- 흡수: #519 · ANA-c03
- 비고: #519 가 분리 사유로 든 897줄 재포맷은 소멸 — 현재 파일은 `clang-format --dry-run` 경고 0. `canOpenForRead` 에서 사유별 캐시하는 대안은 권한 회복을 고착시킬 수 있어 채택하지 않는다.

### ANA-02 · DashXmlParser 의 호출자 없는 리덕션 경로를 지운다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: 제품 코드 호출자가 0건인 `FieldStatistics`·`computeFieldStatistics`·`extractFieldStatistics` 와, #410 이후 `extractAllReducedValues` 로 대체된 `extractReducedValues`·`applyReduction`(Max 무음 폴백) 을 테스트와 함께 삭제한다. `reduceStd` 는 `extractAllReducedValues` 가 쓰므로 남긴다.
- 완료 기준: 다섯 심볼이 레포에 0건 / `test_xml_parser`·`TestDataLoaderCache` 통과 / `(std)` 리덕션 회귀 테스트(TestDataLoaderCache.cpp:292) 유지 / 레포에 `applyReduction` 을 지칭하는 주석이 남지 않는다 (DashDataLoader.cpp:304-307 의 "구 경로 applyReduction() 과는 다르다" 가 삭제 후 떠 있는 참조가 된다)
- 변경 범위: model/analyzer/DashXmlParser.h, model/analyzer/DashXmlParser.cpp, model/analyzer/DashDataLoader.cpp (:304-307 주석 — `knownReductions` 폴백 설명을 `applyReduction` 지칭 없이 다시 쓴다), tests/TestXmlParser.cpp (`extractFieldStatisticsSkipsMissingVariable`·`extractReducedValuesOrdersSamplesNumerically` 삭제 — 후자의 숫자 정렬 검증은 `extractAllReducedValues` 로 옮긴다), model/analyzer/DashScatter2DPlotter.h (:54 주석)
- 선행: -
- 충돌: ANA-17 (같은 파일 — 먼저 지우고 평탄화) · ANA-16 (DashDataLoader.cpp) · B2 교집합: DashXmlParser.cpp → ANA-23 · DashXmlParser.h → ANA-23 · TestXmlParser.cpp → ANA-23
- 흡수: #405 · #404(해소됨 — 닫기 제안) · ANA-c01 · ANA-c02 · ANA-c44 · ANA-D3(잔여 죽은 경로)
- 비고: #405 의 결정 지점 "reduction=None 로드맵 유무" 는 이 PR 설명에 기록하고 닫는다 — 현재 Std 를 포함한 4종 리덕션이 모두 `extractAllReducedValues` 한 경로로 나오므로 별도 통계 사슬이 필요한 호출자가 없다. 삭제 복구는 git 으로 싸다. #405 가 선행으로 못박은 **#404**(보드 밖 OPEN, "(std) 축약이 최댓값으로 떨어진다")는 038e687f(#410) 로 코드상 해소 — `extractAllReducedValues` 가 Std 실값을 돌려주고 `applyReduction` 의 Max 폴백은 죽은 경로다. 이 PR 이 그 폴백과 주석까지 지우므로 #404 는 별도 작업 없이 닫는다(닫기 사유를 PR 설명에 적는다). 해소 판정이라 CLOSE 항목을 따로 두지 않았다 — 삭제 대상이 ANA-c02 와 같은 심볼이어서 개념이 하나다.

### ANA-03 · MCU 모델의 SHAP 지원 여부를 결정한다
- 종류: DEC | 규모: S | 태그: D · bug
- 목표: #459 "MCU Set 에서 SHAP Feature 콤보 복구" 는 현행 코드에서 성립하지 않는다 — MCU 인스턴스는 `setModelBuilderBasePath` 가 SHAP 패널 자체를 제거하고(a154a169), Sim 인스턴스는 `.dproj` 만 스캔해 루트에 있는 MCU Set 을 보지 못한다. 둘 중 하나를 정한다. (a) MCU SHAP 미지원 확정 → #459 닫고 `updateMethodWidgetsWithVariables` 의 `isMcu` CSV 분기를 ANA-14 에서 삭제. (b) 지원 → 새 feature 항목 (CSV 헤더로 feature 콤보 채우기 · 데몬 `shap` 명령의 `.h` 모델 경로 — RUN 접점).
- 완료 기준: 결정 기록 (어느 쪽이든 #459 의 처리 방식 명시)
- 변경 범위: 없음 (결정) — (a) 면 view/DashResultsAnalyzerWidget.cpp :1862-1895 가 ANA-14 로, (b) 면 신규 항목
- 선행: -
- 충돌: B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절)
- 흡수: #459 · ANA-c04 · ANA-c05
- 비고: #459 의 Related #409 는 Done — 전량 디코딩 축은 해소됐고 남은 것은 제품 결정뿐이다.

### ANA-04 · Method 콤보 순서를 specFor 선언 순서로 맞춘다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: `setupMethods` 가 콤보·스택을 채울 때 `m_methodWidgets`(QMap, 알파벳 순) 대신 `specFor(viewType).methods` 순서로 순회한다. AnalysisLauncher 는 Box→Scatter→Parallel→Pair, ModelRunner 는 Sobol→Morris→SHAP 로 뜬다. 인덱스 잠금(콤보 인덱스 = 스택 인덱스)은 그대로다.
- 완료 기준: 두 ViewType 의 Method 콤보가 선언 순서와 같다 / `removeMethodWidget("SHAP")` 후 인덱스 잠금 유지
- 변경 범위: view/DashResultsAnalyzerWidget.cpp (setupMethods :424-452)
- 선행: -
- 충돌: ANA-05 ~ ANA-15 (같은 파일) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절)
- 흡수: ANA-D1 · ANA-c09

### ANA-05 · initializeTargetData 중복 억제 캐시를 인스턴스 멤버로 옮긴다
- 종류: PR | 규모: S | 태그: B · bug
- 목표: 함수-로컬 `static QHash<QString, QDateTime> recentCalls` 를 멤버 타임스탬프 1개로 바꾼다. 키가 `viewType_setName` 이라 **DoeSampler Init/Resample** 의 analyzer 2개가 100ms 창을 공유하던 문제가 없어진다 — 두 변종 위젯이 각자 `viewType == DoeSampler`(=0) 인 analyzer 를 들고(DashMainWindow.cpp:1591-1608), `setModel` 이 `setSetName` 보다 먼저 `initializeTargetData()` 를 불러(DashDoeSamplerWidgetBase.cpp:80 → :83) 그 시점 키가 둘 다 `0_`(빈 Set) 로 겹친다. `m_lastMethodWidgetVariables` 가 같은 사유로 멤버가 된 선례를 따른다.
- 완료 기준: Init·Resample 두 Set 을 100ms 안에 연달아 띄워도 두 analyzer 가 모두 스캔한다 (`m_setName` 이 아직 빈 시점의 호출 포함) / 같은 인스턴스의 100ms 내 재호출은 종전처럼 건너뛴다
- 변경 범위: view/DashResultsAnalyzerWidget.h, view/DashResultsAnalyzerWidget.cpp (initializeTargetData :457-476)
- 선행: -
- 충돌: ANA-04, ANA-06 ~ ANA-15 (같은 파일) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절)
- 흡수: ANA-D2 · ANA-c10
- 비고: 색인 ANA-D2 가 든 "ModelRunner Sim/MCU" 쌍은 현행 코드에서 성립하지 않는다 — MCU 호스트가 `setSetName(currentSetName + "-MCU")`(DashModelRunnerMCUWidget.cpp:177) 라 Sim(DashModelRunnerWidget.cpp:143)과 키가 이미 다르다. 색인 좌표가 `-MCU` 접미사(a154a169 계열) 도입 전이다. RUN-22 가 그 접미사 이중 부착을 정리하다 접미사를 걷어내면 Sim/MCU 도 같은 키가 되므로 이 항목이 그때의 선행이 된다. 억제 창 자체를 없애고 호스트 5곳의 이중 호출(setModel + onTabChanged)을 정리하는 대안은 호스트 변경이 PRJ·LCH·OPT·RUN 에 걸쳐 보류.

### ANA-06 · 타깃 콤보 스캔이 현재 Set 을 먼저 고르고 매치 실패 시 0번으로 떨어지지 않게 한다
- 종류: PR | 규모: S | 태그: C · bug
- 목표: `initializeTargetData` 세 분기에 같은 규칙을 둔다 — 현재 Set 폴더(`AnalysisLauncher_{m_setName}` · `DoeSampler_{…}` · `ModelBuilder_{m_setName}`)를 우선 선택하고, 없으면 0번 자동 선택 대신 빈 선택 + WARN. AnalysisLauncher 분기는 전량 나열 뒤 0번(:586-614), DoeSampler 분기도 0번(:616-634, Set 은 "Set1" 고정이라 실질 1건), ModelRunner 분기는 우선 선택은 하나 매치 실패 시 0번(:507-513)이라 MCU 접미사 이중 부착(RUN-22) 같은 매치 실패에서 무관한 Set 의 모델로 플롯이 나간다.
- 완료 기준: Set 2개 이상인 프로젝트에서 Analysis Launcher 분석 탭 진입 시 현재 Set 폴더가 선택돼 있다 / 현재 Set 폴더가 없으면 빈 선택 + WARN 1건 — 다른 Set 의 산출물이 자동으로 뜨지 않는다 / ModelRunner_Sensitivity 도 같은 규칙(`-MCU-MCU` 매치 실패 시 0번으로 가지 않는다) / **세 분기의 콤보 항목 툴팁에 그 Set 의 setId 가 보이고, 색인에 없는 폴더는 툴팁이 비어 있다**(#650 ANA 몫 — 표시만)
- 변경 범위: view/DashResultsAnalyzerWidget.cpp (initializeTargetData :507-513 · :586-634 — 우선 선택; `addItem` 3곳 :502 · :608 · :628 뒤에 `setItemData(…, Qt::ToolTipRole)` 로 setId 부착)
- 선행: -
- 충돌: ANA-04, ANA-05, ANA-07 ~ ANA-15, ANA-18, ANA-21, ANA-22 (같은 파일) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절)
- 흡수: ANA-D14 · ANA-c24 · RUN-D30 · RUN-c44 (RUN-22 에서 이관) · #650(ANA 몫 — 읽는 Set 표시) · PRJ-c39 · ANA-c33
- 비고: "다른 Set 산출물을 아예 숨길지" 는 설계 논점 — 최소안은 우선 선택 + 0번 폴백 제거. 필터링까지 가면 #617 Project Assets 의 Set 연동 규칙(PRJ)과 맞춰야 한다. #650 의 "읽는 Set 의 id 표시(표시만)" 에 PRJ 선행은 필요 없다 — 폴더명↔setId 역조회가 이미 public 이다 (`DashProject::setIds()`, model/DashProject.h:54 · 키는 모듈 json 파일명, model/DashSetIdentity.cpp:132). 폴더 `AnalysisLauncher_X` → `AnalysisLauncher_X.json` 으로 조회하고 미해석은 빈 툴팁(이름 폴백 금지 — SI-4). ⚠ 표시·검사 쌍 등록은 PRJ-22 몫이고 여기서는 표시만 한다. MCU 접미사 이중 부착 자체는 RUN-22.

### ANA-07 · "Set1" 폴백 7벌을 한 접근자로 모으고 빈 Set 을 조용히 대체하지 않는다
- 종류: PR | 규모: S | 태그: C · bug
- 목표: `m_setName.isEmpty() ? "Set1" : m_setName` 7회를 접근자 하나로 바꾸고, Set 이 비어 있으면 무관한 `Set1` 산출물을 읽는 대신 WARN 후 조기 반환한다. 호스트가 `setSetName()` 전에 어느 경로를 밟아도 다른 Set 의 데이터가 조용히 뜨지 않는다.
- 완료 기준: `"Set1"` 리터럴이 파일에 0건 / `setSetName` 없이 `initializeTargetData()` 를 부르면 콤보가 비고 WARN 1건 / DoeSampler Init·Resample 진입 시 첫 스캔이 WARN 없이 해당 Set 으로 돈다 (역순 호스트 교정 확인)
- 변경 범위: view/DashResultsAnalyzerWidget.h, view/DashResultsAnalyzerWidget.cpp (:508·:522·:1025·:1099·:2487·:2989·:3733), view/DashDoeSamplerWidgetBase.cpp (`setModel` 의 :80 `initializeTargetData()` 를 :82-83 `setSetName(setName)` 뒤로 옮긴다 — 2줄)
- 선행: -
- 충돌: ANA-04 ~ ANA-06, ANA-08 ~ ANA-15 (같은 파일) · DOE-05 · DOE-11 · PRJ-25 (DashDoeSamplerWidgetBase.cpp — DOE-05 가 같은 `setModel` 경로의 `loadSettings` 중복을 정리한다) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절)
- 흡수: ANA-D15 · ANA-c25
- 비고: 호스트 5곳 중 **역순이 1곳 실재한다** — `DashDoeSamplerWidgetBase::setModel` 이 `initializeTargetData()`(:80) 를 `setSetName(setName)`(:83) 보다 먼저 부른다. "빈 Set 이면 WARN + 조기 반환" 을 넣으면 이 경로의 최초 스캔이 무효가 되므로(탭 진입 경로 :124-128 이 재초기화해 실해는 작지만 WARN 이 상시 뜬다) 두 줄 교정을 이 항목 범위에 넣었다 — 2줄짜리 호스트 교정이라 DOE 항목으로 넘기지 않는다. 나머지 4곳은 정순이다 (DashModelRunnerWidget.cpp:143-144 · DashModelRunnerMCUWidget.cpp:177-178 · DashAnalysisLauncherWidget.cpp:267-269 · DashDoeSamplerWidgetBase.cpp:124-128).

### ANA-08 · 타깃 콤보 5종을 objectName/findChild 대신 타입 멤버로 보관한다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: `specFor` 가 만드는 타깃 콤보(TargetResults·TargetSecondary·ModelBuilder·ResponseFolder·TrainedModel)를 생성 시점에 멤버 구조체에 담고, `findChild<QComboBox*>("...")` 25회를 멤버 접근으로 바꾼다. 패널 내부 컨트롤이 `DashAnalyzerPanelControls` 로 옮겨간 것과 같은 방식이다. `objectName` 은 남겨도 되지만 분기 조건으로 쓰지 않는다.
- 완료 기준: 파일에 `findChild<QComboBox*>` 0건 / ViewType 4종 전부 종전과 같은 콤보 연쇄 동작
- 변경 범위: view/DashResultsAnalyzerWidget.h, view/DashResultsAnalyzerWidget.cpp
- 선행: -
- 충돌: ANA-04 ~ ANA-07, ANA-09 ~ ANA-15 (같은 파일) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절)
- 흡수: ANA-D5 · ANA-c13

### ANA-09 · TextStyleGroup 수집을 타입 핸들로 바꾸고 폴백 캐스케이드를 지운다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: 팩토리가 이미 채우는 `DashAnalyzerPanelControls::textStyleGroup` 을 위젯이 읽게 하고, `findChild<QWidget*>("TextStyleGroup")` 13회와 그 뒤의 도달 불가 폴백(3열 이상 표 찾기)을 지운다. 텍스트 스타일 추출 20여 줄의 Method 별 복제를 헬퍼 하나로 모은다.
- 완료 기준: `"TextStyleGroup"` 문자열이 view/DashResultsAnalyzerWidget.cpp·view/analyzer/DashPlotWidgetFactory.cpp 두 파일에서 0건 / 팩토리의 `out.textStyleGroup` 읽기 지점 1곳 이상 / 플롯별 textSize·sigFigs 반영 동작 불변
- 변경 범위: view/DashResultsAnalyzerWidget.cpp (process*Plot 4종 + applyStyleToActivePlot), view/analyzer/DashAnalyzerPanelControls.h (핸들 타입을 `QTableWidget*` 로 좁히면 표 탐색도 사라진다), view/analyzer/DashPlotWidgetFactory.cpp (:624·:1461·:1679 의 잉여 `setObjectName("TextStyleGroup")` 삭제 — 이름은 `DashResultsAnalyzerWidget::createTextStyleGroup`(:205-208) 이 이미 항상 붙인다)
- 선행: -
- 충돌: ANA-04 ~ ANA-08, ANA-10 ~ ANA-15 (같은 파일) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · DashPlotWidgetFactory.cpp → ANA-01 UIC-12 · DashAnalyzerPanelControls.h → ANA-22
- 흡수: ANA-D7 · ANA-c15
- 비고: 잉여 `setObjectName` 3곳은 전부 **산 함수** 안이다 — :624 `createScatterPlotWidget`(:454) · :1461 `createConvergenceHistoryWidget`(:1345) · :1679 `createParetoFrontWidget`(:1479). ANA-14 가 지우는 세 함수는 :944 · :1724 · :1945 라 겹치지 않으므로 이 항목이 직접 지운다.

### ANA-10 · 색 버튼 읽기를 getColorFromButton 한 경로로 통일한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `applyStyleToActivePlot` 의 16진수 전용 정규식 3곳(Box 색 3종·Pearson·Sobol)을 `getColorFromButton` 호출로 바꾼다. 초기값 `background-color: black` 같은 색 이름 표기가 정규식에 걸리지 않아 `Qt::black` 으로 떨어지던 불일치가 없어진다.
- 완료 기준: 파일에 `QRegularExpression rx("background-color` 0건 / 색 버튼을 바꾸지 않은 Box Plot 에서 즉시 스타일 반영 색과 Plot 색이 같다
- 변경 범위: view/DashResultsAnalyzerWidget.cpp (:4030-4045·:4138·:4187)
- 선행: -
- 충돌: ANA-04 ~ ANA-09, ANA-11 ~ ANA-15 (같은 파일) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절)
- 흡수: ANA-D6 · ANA-c14
- 비고: 정본을 스타일시트 문자열에서 버튼 동적 프로퍼티(QColor)로 옮기는 안이 더 낫지만 setter 쪽(DashPlotWidgetFactory.cpp:92-99, 위젯 :1738-1803)까지 바뀌어 M 이 된다. 최소안으로 S.

### ANA-11 · 스핀박스 변경이 스타일 setter 와 디바운스 재플롯을 동시에 타지 않게 한다
- 종류: PR | 규모: S | 태그: B · bug
- 목표: `connectReactiveSignals` 가 스핀박스를 두 슬롯에 걸던 것을 `onStyleSettingChanged` 하나로 바꾸고, `applyStyleToActivePlot` 이 현재 위젯 타입에 setter 가 없을 때(Scatter2D·Scatter3D·Parallel·Convergence·Pareto·Morris·Shap 의 textOptions 외 설정)만 `onDataSettingChanged` 로 넘긴다. 값 하나를 바꿀 때 setter 반영 후 200ms 뒤 파일 재파싱/데몬 왕복이 한 번 더 도는 일이 없어진다.
- 완료 기준: Box Plot 에서 스핀박스 1회 변경 시 `onPlotButtonClicked` 가 불리지 않는다 / Scatter Plot 에서 setter 없는 값 변경은 종전처럼 200ms 뒤 재플롯
- 변경 범위: view/DashResultsAnalyzerWidget.h, view/DashResultsAnalyzerWidget.cpp (connectReactiveSignals :3842-3929, applyStyleToActivePlot :3960-)
- 선행: -
- 충돌: ANA-04 ~ ANA-10, ANA-12 ~ ANA-15 (같은 파일) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절)
- 흡수: ANA-D13 · ANA-c23
- 비고: 주석(:3860-3865)은 "setter 없는 설정을 받아내려는 의도" 라 적는다 — 그 의도는 반환값으로 분기하면 유지된다.

### ANA-12 · 랭킹 표를 빌더 반환값으로 전달한다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: 민감도 빌더 3종이 랭킹 표를 플롯 위젯의 숨은 자식(`setParent(w)+hide()`)으로 실어 보내고 `onPlotWindowReady` 가 `findChild("rankingTable")` 로 꺼내던 부수 채널을 없앤다. 빌더·`DashPlotRequestHandler::build` 가 `{플롯 위젯, 랭킹 표(또는 null)}` 를 반환하고, 결합은 호출부 없는 `createPlotWithTable` 을 쓰거나 그것을 지우고 인라인 하나로 둔다. 화면 결과는 같다.
- 완료 기준: `"rankingTable"` objectName 조회 0건 / Morris·Sobol·SHAP-FI 의 표가 종전과 같은 위치에 뜬다 / `createPlotWithTable` 은 쓰이거나 삭제
- 변경 범위: view/analyzer/DashPlotWidgetFactory.h, view/analyzer/DashPlotWidgetFactory.cpp (:2440-2610), view/analyzer/DashPlotRequestHandler.h, view/analyzer/DashPlotRequestHandler.cpp, view/DashResultsAnalyzerWidget.h, view/DashResultsAnalyzerWidget.cpp (onPlotWindowReady :3607-3620·:3824-3834), view/analyzer/DashAnalyzerUtils.h/.cpp (createPlotWithTable :153)
- 선행: -
- 충돌: ANA-04 ~ ANA-11, ANA-13 ~ ANA-15 (같은 파일); ANA-15 (DashPlotRequestHandler.cpp) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · DashPlotWidgetFactory.cpp → ANA-01 UIC-12 · DashAnalyzerUtils.cpp → UIC-12
- 흡수: ANA-D11(구조) · ANA-U5(createPlotWithTable) · ANA-c20 · ANA-c21
- 비고: `DashPlotRequestHandler.cpp` 는 clang-format 미적용(dry-run 경고 78) — 건드리면 파일 전체 재포맷이 따라온다.

### ANA-13 · PNG 저장에 랭킹 표를 포함한다
- 종류: PR | 규모: S | 태그: D · feature
- 목표: `[Save] → Image (PNG)` 가 `scrollArea`(플롯만) 대신 랭킹 표를 포함한 `outer` 를 캡처한다. GL 플롯은 `grabFramebuffer`, 표는 `grab` 으로 합성한다 (`saveAsPng` 의 기존 분기 확장).
- 완료 기준: Sobol 결과의 PNG 에 랭킹 표가 들어 있다 / 표 없는 플롯의 PNG 는 종전과 동일
- 변경 범위: view/analyzer/DashAnalyzerHelpers.cpp (ZoomableScrollArea::saveAsPng :68-93), view/DashResultsAnalyzerWidget.cpp (actPng 람다 :3751-3764)
- 선행: ANA-12, ANA-19 (같은 `saveAsPng` 를 고치고 순서가 고정 — DPR 합성을 먼저 바로잡은 위에 표를 얹는다)
- 충돌: ANA-04 ~ ANA-12, ANA-14, ANA-15 (같은 파일) · ANA-19 (saveAsPng) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · DashAnalyzerHelpers.cpp → ANA-20 ANA-21
- 흡수: ANA-D11(귀결)

### ANA-14 · 호출부 없는 analyzer 코드를 지운다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: 도달 불가·소비 없음이 확인된 코드를 지운다. (1) 팩토리 `createUncertaintyDistributionWidget`·`createScatter2DWidget`·`createScatter3DWidget` 과 헤더 선언, (2) `onTargetDataChanged` DoeSampler 분기의 GeometryParameter·ConditionParameter·ModelBuilder·Optimizer 4갈래 (콤보는 `DoeSampler_*.json` 만 나열 — CON-D13 의 `"checked"` 읽기 :970 도 이 분기 안이라 삭제로 소멸), (3) `settings.parallel.save_json_path` 기록과 그 경로 조립, (4) 위젯 :1963 의 stale 주석, (5) ANA-03 이 (a) 로 결정되면 `updateMethodWidgetsWithVariables` 의 `isMcu` CSV 분기.
- 완료 기준: 다섯 심볼·키가 레포에 0건 / 빌드·기존 테스트 통과 / DoeSampler·AnalysisLauncher 분석 탭 동작 불변
- 변경 범위: view/analyzer/DashPlotWidgetFactory.h, view/analyzer/DashPlotWidgetFactory.cpp (:944-1055·:1724-1834·:1945-2053), view/DashResultsAnalyzerWidget.cpp (:946-1013·:2478-2491·:1963·:1862-1895)
- 선행: ANA-03 (항목 5 만)
- 충돌: ANA-01, ANA-09, ANA-12 (팩토리); ANA-04 ~ ANA-13, ANA-15 (위젯) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · DashPlotWidgetFactory.cpp → UIC-12
- 흡수: ANA-U1 · ANA-U2 · ANA-U5(팩토리 3개) · ANA-c05 · ANA-c26 · ANA-c27 · ANA-c28 · CON-D13 · CON-c13 · ANA-c31
- 비고: U1 은 "미구현" 이 아니라 삭제가 맞다 — #601 이후 DoeSampler 탭은 DOE 표만 그리고, 다른 모듈 산출물은 Analysis Launcher 탭이 XML 로 받는다.

### ANA-15 · [Plot] 실패를 패널에 알린다
- 종류: PR | 규모: M | 태그: D · bug
- 목표: 세 계층의 조용한 실패에 같은 비모달 통지를 붙인다. (1) 호스트 모델 3종의 `requestPlot` 이 빈 spec 에서 `return` 하는 대신 `messages` 를 실은 실패를 되돌린다 (`plotSpecReady` 에 `{"error": …}` 를 싣거나 실패 시그널 1개 신설), (2) `DashPlotRequestHandler::build` 미매치와 `onPlotSpecReady` 의 조기 반환, (3) 비동기 잡 반려(`jobId.isNull()`). 패널은 Plot 버튼 근처 상태 라벨 또는 `DashNotify::warning` 으로 사유를 보여 준다. (1) 에서 `DashPlotSpecBuilder::build` 의 실재 게이트를 설정 JSON(`configFilePath`)이 아니라 데이터 파일(`target_optimum_path` · XML)로 바로잡는다(OPT-D20 — 설정은 실데이터가 아니다).
- 완료 기준: XML 미선택 상태에서 [Plot] 을 누르면 사유가 화면에 보인다 / 미지원 command 로 spec 이 와도 사유가 보인다 / **설정 JSON 이 없고 데이터 파일(`target_optimum_path` · XML)만 있어도 [Plot] 이 그려지고, 데이터 파일이 없으면 그 사유가 보인다** (현행은 `DashPlotSpecBuilder::build` 의 `configFilePath` 빈값·부재 검사 :8-22 가 유일 게이트이고 데이터 경로는 :74-120 에서 비어도 `absoluteConfigPath` 로 폴백한다) / 정상 경로 동작 불변
- 변경 범위: view/DashResultsAnalyzerWidget.h, view/DashResultsAnalyzerWidget.cpp (onPlotSpecReady :3550-3605), view/analyzer/DashPlotRequestHandler.cpp, model/analyzer/DashPlotSpecBuilder.cpp (build :8-22 게이트), model/DashDoeSampler.cpp (:1449-1462), model/DashAnalysisLauncher.cpp (:1437-1460), model/DashOptimizer.cpp (:1173-1185)
- 선행: -
- 충돌: ANA-04 ~ ANA-14 (위젯); ANA-12 (DashPlotRequestHandler.cpp); EXE-03 (#553 — 같은 함수 `onPlotSpecReady` 의 런너 호출 구조) · #433 스택 (PRE — model/DashAnalysisLauncher.cpp) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashDoeSampler.cpp → 공유 15건(deps.md 5절) · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp) · PR #654(DashOptimizer.cpp) · PR #652(DashAnalysisLauncher.cpp·DashDoeSampler.cpp) · PR #651(DashAnalysisLauncher.cpp)
- 흡수: ANA-D10 · ANA-c19 · OPT-D20 · OPT-c30 · ANA-c32
- 비고: 모델 3파일은 각 5줄 안팎이라 주 모듈은 ANA. 통지 수단은 설계 논점 — :3595 주석은 DashNotify 를 "시스템 실패용" 이라 보아 패널 내 상태 라벨이 성격에 맞다. 데몬 응답 오류(`DashModelRunner::processDaemonResponse` 가 로그만 남김)는 RUN 소관으로 같은 채널을 쓰게 한다.

### ANA-16 · 플로터 데이터 컨테이너를 Eigen::VectorXf 에서 std::vector<float> 로 바꾼다
- 종류: PR | 규모: L | 태그: E · refactor
- 목표: `DashBasePlotter::inputs/outputs` 의 값 타입과 로더 출력, Box·Parallel·Scatter2D·Scatter3D 플로터, `normalize1d`, PearsonWidget 의 `rawVectors` 를 `std::vector<float>` 로 바꾼다. Pearson 의 공분산 계산만 `Eigen::Map<const VectorXf>` 로 감싸 Eigen 을 유지한다. analyzer 헤더에서 `<Eigen/Dense>` 가 빠져 view/analyzer 위젯의 컴파일 의존이 줄고 row/column-major 함정이 없어진다. 사용자에게 보이는 결과는 같다.
- 완료 기준: model/analyzer 헤더 중 `<Eigen/Dense>` 를 포함하는 것이 DashPearsonPlotter.h·DashXmlParser.h 뿐 / `TestDataLoaderCache` 통과 / Box·Parallel·Scatter2D·Scatter3D·Pearson 5종을 실데이터로 그려 변경 전과 눈으로 대조한 기록
- 변경 범위: model/analyzer/DashBasePlotter.h, DashBasePlotter.cpp, DashDataLoader.h, DashDataLoader.cpp, DashBoxPlotter.h, DashBoxPlotter.cpp, DashParallelPlotter.h (:14 `ParallelAxisData::normalizedVals` 가 `Eigen::VectorXf` — `DashBasePlotter.h` 에서 Eigen 이 빠지면 이 헤더가 컴파일되지 않는다), DashParallelPlotter.cpp, DashScatter2DPlotter.cpp, DashScatter3DPlotter.cpp, DashPlotterUtils.h, DashPlotterUtils.cpp, DashPearsonPlotter.h, DashPearsonPlotter.cpp, view/analyzer/DashPearsonWidget.cpp, tests/TestDataLoaderCache.cpp
- 선행: -
- 충돌: ANA-17 (DashXmlParser 는 이 항목이 건드리지 않는다 — 경계 유지) · ANA-02 (DashDataLoader.cpp) · B2 교집합: TestDataLoaderCache.cpp → ANA-23
- 흡수: #305(플로터·로더 부분) · ANA-c06
- 비고: L 사유 — `DashBasePlotter::inputs/outputs` 타입 하나가 로더·플로터 전부의 시그니처라 부분 적용이 컴파일되지 않는다 (`getVec()` 소비자 5종 Box·Parallel·Pearson·Scatter2D·Scatter3D 가 모두 그 타입을 받는다). 분할안 없음. #305 자신이 단독 착수를 권하지 않는다 — analyzer 데이터 구조를 어차피 손대는 시점에 얹는다. `percentile`·`normalize1d` 재작성 시 부동소수 결과가 미세하게 달라질 수 있다.

### ANA-17 · DashXmlParser 의 TensorData 를 평탄 버퍼로 바꾼다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: `TensorData::matrix`(`Eigen::MatrixXf`) 를 `std::vector<float>` + `shape` 로 바꾸고 `parseTensor` 의 RowMajor `Eigen::Map` 우회와 `reduceMax/Min/Mean/Std` 의 Eigen 표현식을 평탄 루프로 바꾼다. numpy row-major 와 Eigen column-major 차이로 생기던 함정 자체가 없어진다. 파싱 결과·리덕션 값은 같다.
- 완료 기준: DashXmlParser.h 에서 `<Eigen/Dense>` 제거 / `test_xml_parser`·`TestDataLoaderCache`·`TestAnalyzerUtilsCache` 통과 (텐서 파싱 13 케이스 포함)
- 변경 범위: model/analyzer/DashXmlParser.h, model/analyzer/DashXmlParser.cpp, tests/TestXmlParser.cpp (`TensorData` 소비자는 테스트뿐)
- 선행: ANA-02 (죽은 리덕션 경로를 먼저 지워 변환 면적을 줄인다)
- 충돌: ANA-16 (Eigen 제거 축 — 경계는 파일로 나뉜다) · B2 교집합: DashXmlParser.cpp → ANA-23 · DashXmlParser.h → ANA-23 · TestXmlParser.cpp → ANA-23
- 흡수: #305(파서 부분) · ANA-c07
- 비고: `reduceStd` 의 수치는 Eigen 표현식과 수동 루프가 같은 순서로 더하지 않으면 마지막 자리가 달라질 수 있다 — 테스트는 허용 오차로 비교한다.

### ANA-18 · 민감도 변수 목록의 원천을 model_info 의 `parameter` 키로 바꾸고 실패를 로그한다
- 종류: PR | 규모: S | 태그: C · bug
- 목표: `updateModelRunnerSecondaryCombo` 가 `Model upload.Input Design Variables.label`(Model Runner 설정 JSON 의 스키마 — GUI 는 그 키를 `ModelRunner_{Set}.json` 에만 쓴다, M:updateModelUploadConfig :1154) 대신 `DashModelRunner::loadDesignVariables` 와 같은 `parameter.*` 키에서 변수명을 읽는다. 4단 중첩 `if` 는 어디서 빠져도 WARN 1줄.
- 완료 기준: 실 `model_info.json` 으로 변수 목록이 채워진다 / 키 부재 시 로그가 남는다
- 변경 범위: view/DashResultsAnalyzerWidget.cpp (updateModelRunnerSecondaryCombo :1400-1472)
- 선행: -
- 충돌: ANA-04 ~ ANA-15, ANA-21, ANA-22 (같은 파일) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절)
- 흡수: RUN-D29 · RUN-c43 (RUN-23 에서 이관)
- 비고: Python 측 model_info.json 에 `Model upload` 블록이 있는지 실 파일로 먼저 확인 — 있으면 두 키 중 정본 결정만. 접점 RUN(키 기록 규칙). 변경 파일이 AW 뿐이라 RUN-23 을 ANA 로 옮김.

### ANA-19 · ZoomableScrollArea 의 줌 상한과 PNG 합성을 DPR 기준으로 맞춘다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: (1) `wheelEvent` 의 `qBound(0.5, m_zoomFactor, 10.0)` 상한이 논리 px 기준이라 DPR 2 에서 FBO 가 논리 대비 4배 — 상한을 물리 px 한도(최대 FBO 변 길이 ÷ DPR)로 환산한다. (2) `saveAsPng` 가 `grabFramebuffer()`(물리 px) 위에 자식 오버레이를 `render(&p, child->pos())`(논리 px)로 그려 DPR≠1 에서 오버레이 위치·크기가 어긋난다 — `image.setDevicePixelRatio(dpr)` 또는 `p.scale(dpr, dpr)` 뒤 합성한다.
- 완료 기준: DPR 2 모니터에서 최대 줌 시 FBO 할당이 DPR 1 과 같은 물리 상한 / 저장 PNG 의 오버레이(SizeLegendOverlay) 위치가 화면과 일치 / DPR 1 결과 불변
- 변경 범위: view/analyzer/DashAnalyzerHelpers.cpp (ZoomableScrollArea::wheelEvent :100-131 · saveAsPng :68-93), view/analyzer/DashAnalyzerHelpers.h
- 선행: -
- 충돌: ANA-13 (saveAsPng) · ANA-21 (updateWidgetSize) · B2 교집합: DashAnalyzerHelpers.cpp → ANA-20
- 흡수: #447(R2·R3 — ANA 몫) · UIC-c31 · UIC-c32 · ANA-c35 · ANA-c36
- 비고: 접점 UIC(#447 DPI 카탈로그). 200% 실기 검증 필요

### ANA-20 · GL 뷰포트 설정 관행을 하나로 한다 — resizeGL 인자 단위 실측 후 통일 또는 삭제
- 종류: INV | 규모: S | 태그: D · bug
- 목표: `DashTimeSeriesGLWidget::resizeGL` 은 `glViewport(0,0,w,h)`, 나머지(`DashPlotWidgetBase`·Box·Scatter2D·ShapDependence)는 `calculateViewport`(논리×DPR, `static_cast<int>` 절삭). Qt6 `QOpenGLWidget::resizeGL` 의 w/h 단위와 paintGL 직전 Qt 가 재설정하는 viewport 를 DPR 2 에서 1회 실측해 (a) resizeGL 의 glViewport 가 무의미하면 전부 삭제, (b) 의미 있으면 TimeSeries 도 `calculateViewport` 로 통일하고 절삭을 `qRound` 로 바꾼다.
- 완료 기준: 실측 결과 기록(인자 단위 · paintGL 전 viewport) + 후속 S PR 1건(삭제 또는 통일)
- 변경 범위: (조사) view/analyzer/DashTimeSeriesWidget.cpp (:64-67), view/analyzer/DashAnalyzerHelpers.cpp (calculateViewport :179-190), view/analyzer/DashPlotWidgetBase.cpp (:30-34)
- 선행: -
- 충돌: B2 교집합: DashAnalyzerHelpers.cpp → ANA-13 ANA-19 ANA-21
- 흡수: #447(R4 — ANA 몫) · UIC-c33 · ANA-c37

### ANA-21 · ZoomableScrollArea 의 크기 정책을 한 메서드로 통일한다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: `updateWidgetSize`(min==max 고정)와 `autoFitToViewport`(min=원본·max=무제한)가 같은 콘텐츠 위젯에 다른 정책을 번갈아 적용하고, `onPlotWindowReady` 도 컨테이너에 min==max(800×600)를 미리 건다. 줌 상태(배율·자동맞춤)를 적용하는 메서드 하나(`applyZoom(scale)`)로 모아 정책을 한 곳에서 정하고, `setOriginalSize`·`resetZoom`·`wheelEvent`·`resizeEvent` 는 그 메서드만 부른다.
- 완료 기준: 수동 줌 → 리사이즈(자동맞춤 해제 상태) → 리셋 순서로 콘텐츠 크기가 각 단계의 기대값과 같다 / `setMinimumSize`·`setMaximumSize` 호출이 ZoomableScrollArea 안 1곳 + onPlotWindowReady 0곳
- 변경 범위: view/analyzer/DashAnalyzerHelpers.cpp (updateWidgetSize :144-153 · autoFitToViewport :155-176 · setOriginalSize :51 · resetZoom :59), view/analyzer/DashAnalyzerHelpers.h, view/DashResultsAnalyzerWidget.cpp (onPlotWindowReady :3650-3653)
- 선행: -
- 충돌: ANA-19 (wheelEvent → updateWidgetSize) · ANA-04 ~ ANA-15, ANA-18 (위젯) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절) · DashAnalyzerHelpers.cpp → ANA-20
- 흡수: #449(L3-3 — ANA 몫) · UIC-c35 · ANA-c38

### ANA-22 · [Plot] 실행을 EXE 가드·진행 표시 표준에 결선한다
- 종류: PR | 규모: S | 태그: B, D · feature
- 목표: `onPlotSpecReady` 가 `DashAsyncJobRunner::run` 에 넣는 prefetch 잡 동안 Plot 버튼(패널 컨트롤)을 `DashJobGuard`(EXE-09)로 비활성·복구하고, 상태바 문구·취소는 EXE-08 의 훅(label)에 맡긴다. 반려(`jobId.isNull()`) 안내는 ANA-15 의 채널을 쓴다. 파일 전체에 `setEnabled(false)`·`QProgressBar` 가 0건 — ANA 의 긴 실행은 플롯 prefetch 1종뿐이다.
- 완료 기준: 대용량 XML 플롯 중 Plot 버튼 비활성 · 완료/실패 후 복구 / 디바운스 재플롯(onDataSettingChanged)이 가드에 막혀 반려될 때 안내 1건 / 동기 경로(data-only spec · .json)는 가드를 타지 않는다
- 변경 범위: view/DashResultsAnalyzerWidget.cpp (onPlotSpecReady :3575-3604 · onPlotButtonClicked), view/analyzer/DashAnalyzerPanelControls.h (Plot 버튼 핸들 추가 — 현재 shap 콤보 4종 등 패널 컨트롤만)
- 선행: EXE-07 · EXE-09 · ANA-15
- 충돌: ANA-04 ~ ANA-15, ANA-18, ANA-21 (위젯) · EXE-08 (같은 파일에 문구 지정) · EXE-03 (#553) · B2 교집합: DashResultsAnalyzerWidget.cpp → 공유 21건(deps.md 5절)
- 흡수: #463(ANA 몫) · EXE-c23 · ANA-c43
- 비고: SHAP/Sobol/Morris 데몬 왕복은 RUN 소관 Job(#513) — 여기서는 플롯 prefetch 만

### ANA-23 · 결과 XML 의 새 스키마(Set 단위 누적 · 위상 1회)를 analyzer 파서가 수용한다
- 종류: PR | 규모: S | 태그: A · feature
- 목표: PRE-30(Set 파일 하나에 응답 누적)·PRE-31(위상 2키를 파일당 1회만 기록)이 랜딩한 포맷을 `DashXmlParser` 가 읽게 한다. (1) 변수 목록을 첫 샘플 하나가 아니라 샘플 전체(또는 누적된 응답 전체)에서 모아 뒤에 추가된 응답의 변수가 빠지지 않게 한다. (2) `sortedSampleKeys` 가 샘플이 아닌 최상위 키(`model_info` 와 PRE-30 이 추가하는 키)를 샘플로 세지 않게 키 집합을 명시한다. (3) 샘플 0 에만 있는 위상 키 전제를 테스트로 고정한다. 읽는 값은 포맷 변경 전과 같다.
- 완료 기준: PRE-30 형식의 누적 XML(응답 2개)에서 두 응답의 변수가 모두 타깃 콤보에 뜬다 / PRE-31 형식(위상은 샘플 0 에만)에서 리덕션 값이 변경 전과 같다 / 샘플 수가 최상위 키 수와 어긋나는 파일에서 `extractAllReducedValues` 가 비샘플 키를 건너뛴다 / `test_xml_parser`·`TestDataLoaderCache` 통과 (새 포맷 픽스처 추가)
- 변경 범위: model/analyzer/DashXmlParser.h, model/analyzer/DashXmlParser.cpp (`sortedSampleKeys` :388-395 · `extractReducedValues` :397 · `extractAllReducedValues` :494 · `variableNamesFromXmlValue` :554 · `extractVariablesFromXml` :590-713 중 첫 샘플 선정 :629-651 과 변수 수집 :687-690), tests/TestXmlParser.cpp, tests/TestDataLoaderCache.cpp
- 선행: PRE-29 (포맷·식별자 결정 — 이것이 "안 바꾼다" 로 끝나면 이 항목은 소멸) · PRE-30 · PRE-31
- 충돌: ANA-02 · ANA-17 (같은 파일 DashXmlParser — ANA-17 의 평탄 버퍼 전환 뒤에 오는 편이 작다) · B2 교집합: TestDataLoaderCache.cpp → ANA-16
- 흡수: PRE-30(`보류: ANA 몫`) · PRE-31(`보류: ANA 몫`) · ANA-c45 · #643 추가 3(ANA 몫 — 스키마 축)
- 비고: 위상 2키는 `unconsumedTensorKeys()`(:67-70) 가 양쪽 추출 경로에서 이미 건너뛰므로 PRE-31 쪽 수용 부담은 전제 확인·테스트 고정뿐이다. 실제 변경량은 PRE-30 의 누적 구조가 "샘플 dict 안의 키 추가" 인지 "최상위 키 추가" 인지에 달렸다 — 전자면 (1) 만, 후자면 (1)(2) 둘 다. 컨테이너 자체를 바꾸는 HDF5 전환(#643 추가 3 의 다른 축 · ANA-c41)은 PRE-29 가 그쪽으로 결정할 때 별 항목으로 신설한다. BLD 로더 수용은 BLD-14.

## 대응표

| 원천 | 항목 | 비고 |
|---|---|---|
| #405 | ANA-02 | 널 역참조는 #424 에서 해소, 결정+삭제만 남음 |
| #404 (보드 밖 OPEN) | ANA-02 | 해소됨 — 038e687f(#410) 가 Std 실값 경로로 대체. 죽은 Max 폴백과 `DashDataLoader.cpp:307` 주석 참조를 ANA-02 가 지운다 → **닫기 제안**. #405 가 선행으로 못박은 이슈 (ANA-c44) |
| #519 | ANA-01 | 재포맷 부수효과 소멸 |
| #459 | ANA-03 | MCU SHAP 은 a154a169 로 설계상 제거 — 결정 선행 |
| #305 | ANA-16 · ANA-17 | 죽은 include 1건은 MOR 로 (ANA-c08) |
| ANA-D1 | ANA-04 | |
| ANA-D2 | ANA-05 | |
| ANA-D3 | 항목 없음 | 해소됨 — 038e687f(#410) `extractAllReducedValues` 가 Std 실값. 죽은 `applyReduction` 은 ANA-02 가 지운다 |
| ANA-D4 | 항목 없음 | 해소됨 — 50d43597·038e687f 스트리밍 스캔+캐시, ca68a573(#544) 워커 prefetch |
| ANA-D5 | ANA-08 | |
| ANA-D6 | ANA-10 | |
| ANA-D7 | ANA-09 | |
| ANA-D8 | 항목 없음 | 해소됨 — d1795826 write-only 코드 제거 |
| ANA-D9 | 항목 없음 | 해소됨 — d1795826 (되읽기 구현이 아니라 쓰기 제거) |
| ANA-D10 | ANA-15 | 호스트 모델 3파일은 DOE·PRE·OPT 접점 |
| ANA-D11 | ANA-12 · ANA-13 | 구조(12) 와 PNG 포함(13) 분리 |
| ANA-D12 | 항목 없음 | 해소됨 — e2857898 `DashPlotWidgetBase : DashExportable`, dock 경로 위젯 12종 전부 구현 |
| ANA-D13 | ANA-11 | |
| ANA-D14 | ANA-06 | ModelRunner 분기 사례는 RUN-D30 |
| ANA-D15 | ANA-07 | |
| ANA-U1 | ANA-14 | 삭제 |
| ANA-U2 | ANA-14 | 삭제 |
| ANA-U3 | 항목 없음 | 해소됨 — d1795826 |
| ANA-U5 | ANA-12 (createPlotWithTable) · ANA-14 (팩토리 3개) | |
| 접점 #553 | 항목 없음 | EXE 소관 — `onPlotSpecReady` 호출부가 따라 바뀜 (ANA-15 와 충돌) |
| 접점 #411 | 항목 없음 | PRE 소관 결정(PRE-29) — 컨테이너 교체 결론이면 별 항목 신설. 컨테이너 유지 + 스키마 변경 축은 ANA-23 |
| PRE-30 · PRE-31 (`보류: ANA 몫`) | ANA-23 | PRE 가 명시로 넘긴 파서 수용 (ANA-c45) |
| RUN-D29 | ANA-18 | ← RUN-23 (RUN 에서 이관 — 변경 파일이 AW 뿐) |
| RUN-D30 | ANA-06 | ← RUN-22 의 AW 몫 (MCU 접미사 이중 부착은 RUN-22 잔류) |
| CON-D13 | ANA-14 | ← CON-c13 (ANA-c31). 읽는 분기가 도달 불가 — 삭제로 소멸 |
| OPT-D20 | ANA-15 | ← OPT-c30 (ANA-c32). 실재 게이트를 데이터 파일로 |
| #650 (ANA 몫) | ANA-06 | ← PRJ-c39 (ANA-c33). 표시만 — 콤보 항목 툴팁에 `DashProject::setIds()` 로 setId 를 붙인다 (PRJ 선행 없음) |
| #458 (ANA 몫) | 항목 없음 | ← EXE-c46 (ANA-c34). 해소됨 — Analyzer 축은 #410·#544 (ANA-c12) |
| #447 R2 · R3 (ANA 몫) | ANA-19 | ← UIC-c31 · UIC-c32 (ANA-c35 · c36) |
| #447 R4 (ANA 몫) | ANA-20 | ← UIC-c33 (ANA-c37) |
| #449 L3-3 (ANA 몫) | ANA-21 | ← UIC-c35 (ANA-c38) |
| ANA-D12 (피드백 부재 색인) | 항목 없음 | ← UIC-c56 · EXE-c44 (ANA-c39 · c40). 해소됨 — 위 ANA-D12 행 |
| #643 추가 3 · #411 (ANA 몫) | ANA-23 (스키마 축) · 항목 없음 (HDF5 축) | ← PRE-c56 (ANA-c41). 컨테이너 교체는 PRE-29 결정 전 항목 없음 |
| ANA-D1 (위치·순서 색인) | ANA-04 | ← UIC-c58 (ANA-c42) |
| #463 (ANA 몫) | ANA-22 | ← EXE-c23 (ANA-c43) |
