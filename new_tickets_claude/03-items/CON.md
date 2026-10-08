# CON 작업 목록 (Condition Parameterization)

> 기준 dev @ b08a91b3. 원자 항목은 02-claims/CON.md — 28건 중 유효 19건(c01 c03 c04 c05 c07 c08 c09 c14 c15 c16 c18 c20 c21 c22 c23 c24 c25 c26 c28)을 개념별로 11개 항목으로 묶었다. 해소됨 5건(D2 D6 D10 D11 D12)·범위밖 4건(D13→ANA · U5 RW 몫→EXE · #645 복사 실패→PRJ · c27 DV 모델 소유권→DOE)은 항목 없음. CON-08 은 결번(DOE-10 병합, B2).
> 진행 중 PR 과의 접점: 열린 PR 6건(#658 #656 #655 #654 #652 #651) 중 CON 파일과 겹치는 것은 **4건** — #651 #652 #654 #655 가 전부 `view/DashMainWindow.cpp` 와 `tests/CMakeLists.txt` 를 고친다. #656 은 겹침 0, #658 은 `tests/rw/FakeRwModule.h` 뿐(CON-09 범위에서 제외됨). #530 은 머지하지 않으므로 충돌에서 뺀다(decisions ②). CON 고유 파일(위젯·모델·viewmodel·`.ui`)을 직접 고치는 열린 PR 은 없다.
> #655 는 CON 항목의 **선행이 아니다** — MainWindow hunk 가 `handleSubItemSelection`(:1333)·`initializeMorphingController`(:2190)·`setupMorphingBar`(:2405) 에만 있어 CON-03(`addReferenceFile`·`copyFileIntoProject`)·CON-05(`handleConditionParameterizationSelection`)·CON-06(`unbindSetWidgets`) 과 함수가 겹치지 않는다. 단순 충돌만 등록(decisions ④).
> Phase B1 흡수(범위밖 이관, CON-c22~c25): PRJ-c19 → CON-04 · PER-c24 → CON-11(신규) · EXE-c43 CON 몫 → CON-07(D9)·해소됨(D11) · UIC-c57 CON 몫 → CON-09.

### CON-01 · 저장된 체크 상태를 행 재구축 뒤에 적용해 첫 진입에서도 복원되게 한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `loadFromJson` 을 "설정 읽기(핀·source 힌트·체크 키 집합)" 와 "행에 체크 적용" 으로 나누고, 적용을 `rebuildFromDocument` 의 `endResetModel()` 앞에서 실행한다. 적용 단계는 **IOController 없이 호출할 수 있는 seam** 으로 노출한다(`applyDvConditionSection(const QJsonObject&)` 또는 설정 경로 setter) — 그래야 테스트에서 돈다. 지금은 세 호출처가 전부 행 생성 전에 돌아 첫 진입이 전부 해제로 보이고, 그 상태의 [Set Design Variable] 이 `DV-Condition` 을 `{}` 로 덮는다.
- 완료 기준: (1) 새 세션 첫 진입에서 FE 탭 체크가 JSON 의 `boolean` 과 일치한다 (2) 그 직후 [Set Design Variable] 이 기존 DV 를 보존한다 (3) `TestConditionParameterization` 에 "재구축 뒤 체크 복원" 케이스 추가(gen4 키로 1행만 묶이는지 포함) — 적용 단계를 `DashProjectManager` 스텁 없이 직접 부를 수 있어야 한다
- 변경 범위: model/DashConditionParameterization.h · model/DashConditionParameterization.cpp · tests/TestConditionParameterization.cpp
- 선행: -
- 충돌: CON-02 (같은 `rebuildFromDocument`) · CON-05 (같은 모델 파일) · CON-09 (같은 테스트 파일) · B2 교집합: DashConditionParameterization.cpp → CON-06 PRJ-09 UIC-20 · TestConditionParameterization.cpp → CON-11 · DashConditionParameterization.h → CON-06
- 흡수: CON-D7 · CON-c07
- 비고: 핀 해석(`resolveReferenceDeck`)은 deck 로드 전에 `m_referenceModel`·`m_dvSourceHints` 를 써야 하므로 "읽기" 는 지금 시점을 유지한다. stale uuid 재바인딩의 QSaveFile 쓰기는 적용 단계로 옮긴다. 편집 commit 마다 재구축이 도니 파싱 결과를 멤버로 캐시할지 구현에서 정한다. **seam 이 필요한 근거**(검토 #9) — `tests/TestConditionParameterization.cpp:94-104` 가 `DashProjectManager::Instance()`→nullptr · `getConfigFilePath`→`{}` 로 스텁하므로 `setProjectDirectory`(:30-50)·`setSetName`(:60-78) 이 조기 반환하고 `loadFromJson` 이 아예 돌지 않는다. CON-09·CON-11 의 완료 기준이 이 seam 에 걸린다. **최소 대안** — "읽기/적용 분리 + 멤버 캐시" 대신 `refreshFromLoadedAnalysis` 가 `rebuildFromDocument` 직후 `loadFromJson()` 을 1회 더 부르는 안(:125-146, 편집 commit 경로는 existing 행이 `isChecked` 를 보존하므로 불필요)을 구현에서 함께 재고한다.

### CON-02 · 행 재구축이 사라진 조건과 다른 source 의 행을 버린다
- 종류: PR | 규모: S | 태그: A, C · bug
- 목표: `rebuildFromDocument` 가 현재 세대의 조건 이름 집합 밖에 있는 행과 현재 deck 파일명이 아닌 source 의 행을 제거한다. 남는 행의 `isChecked` 는 지금처럼 보존한다. Set↔deck 1:1(#603) 이후 다른 source 행이 남을 정당한 이유가 없다.
- 완료 기준: (1) 조건이 빠진 deck 으로 재구축하면 그 행이 표에서 사라진다 (2) 핀이 다른 파일로 재해석돼도 이전 파일 행이 남지 않는다 (3) 테스트 케이스 — 조건 2개 deck → 1개 deck 재로드 후 `rowCount()==1`
- 변경 범위: model/DashConditionParameterization.cpp · tests/TestConditionParameterization.cpp
- 선행: -
- 충돌: CON-01 (같은 함수) · CON-09 · B2 교집합: DashConditionParameterization.cpp → CON-05 CON-06 PRJ-09 UIC-20 · TestConditionParameterization.cpp → CON-11
- 흡수: CON-D3 · CON-c03
- 비고: 하류 `DashAnalysisLauncher` 가 DV 별 `source` 로 참조 파일을 모으는 설계는 JSON 쪽 계약이라 영향 없음.

### CON-03 · 덮어쓴 기준 deck 을 표시 중인 Condition 위젯이 다시 읽는다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `DashMainWindow::addReferenceFile` 의 `registry.load` **성공 직후**에, 표시 중인 Condition 위젯의 핀 deck 파일명이 방금 덮어쓴 파일과 같으면 `refreshFromFile` 을 다시 부른다(`refreshConditionWidgetFor` 1줄). 위젯 쪽은 `refreshFromFile` 이 재로드 전에 `clearFeConditionHighlight()` 를 부르게 하는 1줄만 바꾼다.
- 완료 기준: (1) Add File 로 같은 이름의 다른 deck 을 덮어쓰면 열려 있는 Condition 표가 새 조건 목록으로 바뀐다 (2) 다른 deck 을 핀한 Set 은 영향 없음 (3) 덮어쓰기 중 선택돼 있던 하이라이트가 남지 않는다 (4) 훅이 `QFile::copy` **뒤**에 돈다 — 구 파일을 다시 파싱하지 않는다
- 변경 범위: view/DashMainWindow.cpp · view/DashConditionParameterizationWidget.cpp
- 선행: CON-02 (유령 행을 먼저 없애야 새 내용만 보인다) · PRJ-21 (복사 원자화가 먼저 들어가면 훅이 그 성공 분기에 얹힌다 — 순서만, 기능 의존 아님)
- 충돌: 열린 PR #651 #652 #654 #655 (`view/DashMainWindow.cpp`) · CON-04 CON-06 CON-07 (위젯 파일) · PRJ-21 (#645 — 복사 실패 복원, 같은 함수군) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashConditionParameterizationWidget.cpp → CON-05 CON-12 DOE-19 UIC-19 UIC-20
- 흡수: #645 (CON 몫) · #645-1 (PRJ-20 이 CLOSE 로 넘긴 집행분) · CON-c18
- 비고: **훅 위치 교정**(검토 #1 · decisions ⑦) — `discardLoadedReferenceFile`(:2727) 은 `QFile::remove`(:2715)·`QFile::copy`(:2718) 보다 **앞**에 돌아 거기서 `refreshFromFile` 을 부르면 구 파일을 다시 파싱하거나 삭제와 경쟁한다. 새 내용이 로드되는 자리는 호출자의 `co_await addReferenceFile`(:2694) → `registry.load`(:2766) 뒤다. "public 진입점 노출" 문구는 삭제 — `refreshFromFile`·`pinnedDeckFileName` 이 이미 public(`view/DashConditionParameterizationWidget.h:41,45`)이고 `clearFeConditionHighlight` 는 private 이라 위젯 변경은 `refreshFromFile` 안 1줄로 끝난다(헤더 무변경). **PRJ-20 과의 관계** — 같은 #645-1 을 PRJ 가 PRJ-20 으로 항목화했으나 decisions ⑦ 이 **CON-03 에 남기기로 확정**했고 PRJ-20 은 CLOSE 다(PRJ 헤더 변경 불요 → 실질 1파일). 충돌란에서 `PRJ-20` 을 뺐다. 대안은 레지스트리에 `invalidated(filePath)`/`documentChanged` 를 쓰는 것 — 레지스트리가 invalidate 후 load 를 첫 로드로 보아 `documentChanged` 를 내지 않고(REN) CON 모델은 #565 로 방송 구독을 걷었으므로, 통지 책임은 덮어쓰기를 집행한 MainWindow 다.

### CON-04 · 프로젝트 전환 뒤 해제된 조건 모델 역참조를 QPointer 로 막는다
- 종류: PR | 규모: S | 태그: A, E · bug
- 목표: `DashConditionParameterizationWidget::mModel` 과 `DashFeConditionValueDelegate::m_dataModel` 을 `QPointer<DashConditionParameterization>` 으로 바꾼다 — **이 2곳뿐**. `clearAllSets` 가 모델을 지우면 둘 다 null 이 되어 기존 `!mModel`/`!m_dataModel` 가드가 그대로 작동한다.
- 완료 기준: (1) 프로젝트 A → B 전환 뒤 Condition Set 클릭·표 셀 더블클릭·DV JSON 외부 변경에서 크래시·ASan 보고 없음 (2) 변경은 헤더 2개의 멤버 선언뿐 — 가드를 새로 넣지 않는다
- 변경 범위: view/DashConditionParameterizationWidget.h · view/delegate/DashFeConditionValueDelegate.h
- 선행: -
- 충돌: CON-03 CON-06 CON-07 (위젯 헤더) · PRJ-01 (#551 — 7개 위젯을 한 PR 로 묶으면 이 항목은 그쪽에 흡수) · UIC-19 (같은 위젯 — 설계 충돌이 아니라 순서만, 아래 비고) · B2 교집합: DashConditionParameterizationWidget.h → CON-05
- 흡수: #551 (CON 몫) · #551 별개 1 (PRJ-c19 이관) · CON-c20 · CON-c22
- 비고: #551 not-to-be 가 적은 "delegate 는 QPointer 로 해결되지 않는다" 는 2-인자 `setModel` 이 null 을 조기 반환하기 때문인데(PRJ-c19 가 같은 지적), delegate 포인터 자체를 QPointer 로 두면 그 경로와 무관하게 null 이 된다. 리셋 계약 명문화는 #431(PRJ-02). **`GetProject` 가드 신설은 기각**(검토 #4 · decisions ⑦) — `DashProjectManager::GetProject()` 는 ctor 에서 1회 `new` 하고 재할당이 없어(`controller/DashProjectManager.cpp:26-28`·`:45-48`) 항상 non-null 이고, 같은 파일에서 바로 그 가드를 **삭제**하는 UIC-19 의 완료 기준을 깬다. 규모·변경 범위를 QPointer 2곳으로 줄였다. `setModel` 안의 실제 무가드 역참조(`mModel->getSettingsJsonPath()` — qobject_cast 실패 시 · `getIOController()->getConfigsDirectory()` :369-371)는 setModel 경로를 합치는 **CON-06** 이 같은 줄에서 다룬다. **PRJ-01(전환 전 전 위젯 `setModel(nullptr)`)이 먼저 랜딩하면 이 항목은 CLOSE** — 1-인자 경로가 delegate 까지 null 로 만든다(PRJ-01 비고와 교차).

### CON-05 · `setProjectDirectory` 의 중복 호출과 무시되는 인자를 걷어낸다 (PRJ-08 계약의 CON 적용분)
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: CON 모델의 설정 읽기를 한 번만 돌게 한다 — (a) Set 선택 경로의 중복 1곳(위젯 2-인자 `setModel`:321)을 지우고 `handleConditionParameterizationSelection`(:1436) 만 남긴다 (b) `renameSet`(`model/DashProject.cpp:1756`) 의 `setSetName` + `setProjectDirectory` 2중 읽기에서 뒤 호출을 지운다(`setSetName` 이 이미 경로를 다시 짜고 `loadFromJson` 을 부른다) (c) 2-인자 `setModel(model, projectPath)` 의 `Q_UNUSED(projectPath)` 인자와 호출부(`view/DashMainWindow.cpp:1438`)의 인수를 삭제한다. **시그니처 처분(유지·개명·삭제)은 PRJ-08 이 9클래스 공통으로 정하고, 이 항목은 그 적용분이다.**
- 완료 기준: (1) Set 선택 1회에 `loadFromJson` 이 1회 (2) Set 이름 변경 1회에 `loadFromJson` 이 1회 (3) 위젯 `setModel` 에 `Q_UNUSED` 0 (4) 동작 불변 — 핀 해석·체크 복원 결과 동일
- 변경 범위: view/DashConditionParameterizationWidget.h · view/DashConditionParameterizationWidget.cpp · view/DashMainWindow.cpp · model/DashProject.cpp (+ PRJ-08 이 개명·인자 삭제를 정하면 `model/DashConditionParameterization.h/.cpp`)
- 선행: CON-01 (설정 읽기/적용 분리 뒤에 호출 수를 줄여야 체크 복원이 안 깨진다) · PRJ-08 (Set 모델 공통 계약 — 아래 비고의 역순 조건)
- 충돌: 열린 PR #651 #652 #654 #655 (`view/DashMainWindow.cpp`) · PR #651 #652 (`model/DashProject.cpp`) · CON-06 (MainWindow·위젯) · PRJ-08 (`setProjectDirectory` 계약) · PRJ 의 `model/DashProject.cpp` 항목 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · DashConditionParameterizationWidget.cpp → CON-03 CON-07 CON-12 DOE-19 UIC-19 UIC-20 · DashConditionParameterization.cpp → CON-02 PRJ-09 UIC-20 · DashConditionParameterizationWidget.h → CON-04 CON-07
- 흡수: CON-D1 · CON-c01 · CON-c28 (`Q_UNUSED(projectPath)`)
- 비고: **PRJ-08 이 계약, 이 항목이 적용**(decisions ⑦) — 다른 Set 모델 8종(+ `DashModelRunnerMCU::setProjectDirectory(userPath, projectPath)` 2-인자 변종)도 같은 관례라 개명/인자 처분을 CON 혼자 정하면 어긋난다. **역순 허용** — decisions ⑧ 이 지적한 Set 모델 공통 베이스 부재로 PRJ-34(DEC) → PRJ-08 이 늦어져 이 항목이 블록되면, (a)(b)(c) 만 CON 에서 먼저 내고 시그니처는 PRJ-08 이 일반화할 때 맞춘다. 그때도 `setProjectDirectory` 심볼 삭제는 완료 기준에 넣지 않는다. 숫자 정정(검토 #3) — 호출은 5곳이고 Set 선택 시 읽기는 2회다(1-인자 `setModel`:392 는 nullptr 로만 호출돼 도달 불가 — CON-06 이 그 오버로드를 지울 때 함께 사라진다). 파일 4개라 M 이지만 작업량은 반나절.

### CON-06 · 도달 불가 경로와 드리프트한 선언을 제거한다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: (a) `setModel` 진입점을 2-인자 하나로 합치고 null 을 리셋(연결 해제·delegate null·표 비움)으로 처리, 1-인자 오버로드와 그 안의 `dataChanged→updateUI`·`dataLoaded→onModelDataLoaded` 연결 블록, 수신처 0곳인 `dataLoaded` 시그널을 제거 (b) `directoryChanged` 가 연결되지 않는 userPath 디렉토리 감시, `onDvJsonChanged` 의 `else` 분기, `onDirChanged`, `updateDvWatcher` 별칭을 제거 (c) `.ui` 의 5열 선언을 모델 7열과 맞추거나 열 선언을 지우고 주석으로 정본(모델)을 가리킨다.
- 완료 기준: (1) `DashConditionParameterizationWidget` 에 public `setModel` 이 하나 (2) `QFileSystemWatcher::directories()` 가 항상 비어 있다 (3) Set 삭제 경로(`unbindSetWidgets`)에서 표가 비고 delegate 가 에디터를 열지 않는다 (4) `.ui` 열 수 == `columnCount()`
- 변경 범위: view/DashConditionParameterizationWidget.h · view/DashConditionParameterizationWidget.cpp · ui/DashConditionParameterizationWidget.ui · model/DashConditionParameterization.h · model/DashConditionParameterization.cpp · view/DashMainWindow.cpp (`unbindSetWidgets` 호출 1줄)
- 선행: CON-04 (QPointer 로 바꾼 뒤 리셋 경로를 정리해야 두 번 손대지 않는다) · PRJ-02 (리셋 계약 DEC — (a) 가 "null = 표 비움" 으로 동작을 바꾸므로 계약을 먼저 받는다)
- 충돌: CON-03 CON-05 CON-07 · 열린 PR #651 #652 #654 #655 (`view/DashMainWindow.cpp`) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashConditionParameterizationWidget.cpp → CON-12 DOE-19 UIC-19 UIC-20 · DashConditionParameterization.cpp → CON-01 CON-02 PRJ-09 UIC-20 · DashConditionParameterization.h → CON-01
- 흡수: CON-U1 · CON-U3 · CON-D4 · CON-c14 · CON-c15 · CON-c04
- 비고: 세 결함 모두 "정본이 아닌 선언·경로" 라 한 개념으로 묶었다. **분할 지적(검토 #5)은 기각** — 1-인자 오버로드는 `nullptr` 로만 호출되는 도달 불가 경로이고, 그것을 지우려면 2-인자가 null 을 받아야 하므로 (a) 의 동작 변경은 (b)(c) 와 같은 "죽은 선언·경로 제거" 개념의 귀결이다. 00-plan 1-2 "개념적 응집" 기준으로 개념이 하나면 동작 변경·리팩터가 섞여도 유지한다. 대신 검토가 지적한 의존은 받았다 — 선행에 PRJ-02 추가. MainWindow 변경은 `unbindSetWidgets` 호출 1줄뿐이라 열린 PR 4건이 길어지면 그 1줄만 뒤로 떼어 내는 순서 조정으로 흡수한다(항목 분할은 하지 않는다). `setParent(this)` 로 공용 DV 모델 소유권을 빼앗는 줄(:331, CON-c27)은 여기 넣지 않았다 — **보류: DOE 몫**(소유자 결정이 `DashDesignVariableModel` 소관). `saveSettings` 빈 슬롯과 미사용 `JsonKeys` 네임스페이스도 같은 파일에 있으나 원천 밖이라 언급만 한다.

### CON-07 · DV 저장 뒤 자기 쓰기 억제를 실제로 작동하게 한다
- 종류: PR | 규모: S | 태그: B, D · bug
- 목표: `m_blockDvWatcher` 를 동기 구간에서 되돌리는 방식(큐로 오는 `fileChanged` 를 못 막는다)을 **횟수 무관 설계**로 바꾼다 — 자기 쓰기 직후 `updateDvWatchers()` 로 감시를 재등록하고, 배달된 `fileChanged` 는 마지막으로 쓴 바이트(또는 mtime·크기)와 같으면 리로드를 생략한다. 같은 줄에서 `syncDvFromCheckedFeConditions` 의 성공 모달 `QMessageBox::information` 을 `DashNotify::info` 로 바꾼다(UIC-17 이 추가하는 변형).
- 완료 기준: (1) [Set Design Variable] 1회에 `loadFromJsons` 가 1회(저장 직후 명시 리로드)만 돈다 (2) DV-Condition 탭 셀 편집 1회에 워처 리로드 0회 (3) 외부 편집기로 JSON 을 바꾸면 리로드 1회 — 단 **원자 저장(rename) 편집기에서 감시가 끊기는 기존 한계는 그대로다**(`QFileSystemWatcher` 가 inode 를 잃는다), 재등록 시점이 자기 쓰기 뒤뿐이므로 (4) CON 영역 직접 `QMessageBox` 0
- 변경 범위: view/DashConditionParameterizationWidget.h · view/DashConditionParameterizationWidget.cpp
- 선행: CON-11 (`saveDvCondition` 이 `QSaveFile` 로 바뀌면 같은 파일의 `fileChanged` 패턴이 달라진다 — 아래 비고) · UIC-17 (`DashNotify::info`)
- 충돌: CON-03 CON-04 CON-06 (같은 위젯) · B2 교집합: DashConditionParameterizationWidget.cpp → CON-05 CON-12 DOE-19 UIC-19 UIC-20 · DashConditionParameterizationWidget.h → CON-05
- 흡수: CON-D9 · CON-c09 · CON-c21 · CON-c24 (EXE-c43 CON 몫 — D9 전용)
- 비고: **"1회 무시 토큰" 안을 버린 이유**(검토 #6) — 무시 횟수가 플랫폼·쓰기 프리미티브에 따라 달라진다. 현행 `saveDvCondition`(`QIODevice::Truncate` 직쓰기, `viewmodel/DashConditionParameterizationPresentationModel.cpp:135-142`)은 1~2회를 내고, CON-11 이 `QSaveFile`(rename) 로 바꾸면 macOS 에서 감시가 끊겨 0회가 될 수 있어 토큰이 남아 **다음 외부 변경을 삼킨다**. 감시 대상이 바로 `saveDvCondition` 이 쓰는 `mModel->getSettingsJsonPath()` 와 같은 파일이라 둘은 직결이다. 따라서 CON-11 을 선행으로 두고 횟수에 의존하지 않는 설계로 간다. 횟수 실측이 필요하면 CON-11 랜딩 뒤 플랫폼별 `fileChanged` 횟수 INV 를 따로 낸다. CAD 위젯(`DashGeometryParameterCADWidget`)이 같은 플래그 패턴을 쓰므로 CAD 가 같은 설계를 재사용할 수 있다. `QMessageBox` → `DashNotify::info` 는 같은 함수 1줄이라 UIC-17 뒤 이 항목이 함께 처리한다(검토 #7, UIC 대응표의 "CON 1").

### CON-09 · dvKey 채번과 gen1~gen4 체크 바인딩에 회귀 테스트를 붙인다
- 종류: PR | 규모: S | 태그: F · refactor
- 목표: `TestConditionParameterization` 에 (a) dvKey 3규칙 — 엔트리 1개는 맨이름, Abaqus 다수 엔트리는 `{name}_e{N}`, flat 다수 필드는 `{name}_{param}` (b) DV-Condition 의 gen1(이름)·gen2(uuid)·gen3(uuid+entry_ptr)·gen4(uuid+entry_ptr+param) 엔트리가 각각 어느 행을 체크하는지 (c) 이름으로만 묶였는데 저장 uuid 가 다르면 파일의 uuid 가 재기록되는지 를 추가한다.
- 완료 기준: (1) 케이스 3군 통과 (2) 기존 10케이스 영향 없음
- 변경 범위: tests/TestConditionParameterization.cpp
- 선행: CON-01 (IOController 없이 설정 JSON 을 행에 적용하는 seam 이 생긴다 — CON-01 목표·비고에 명시) · EXE-21 (flat 조건 픽스처를 `tests/rw/FakeRwModule.h` 에 만드는 쪽)
- 충돌: CON-01 CON-02 (같은 테스트 파일) · B2 교집합: TestConditionParameterization.cpp → CON-11
- 흡수: CON-U5 (CON 몫) · CON-c16 · CON-c25 (UIC-c57 CON 몫)
- 비고: **픽스처 몫은 EXE-21**(decisions ⑦ · 검토 #8) — 구 완료 기준 (2) "FakeRwModule 로 flat 조건을 만들 수 있다" 를 삭제하고 `tests/rw/FakeRwModule.h` 를 변경 범위에서 뺐다. 공용 픽스처이고 흉내낼 대상(`DashRwDocument` flat 스키마 분해)이 EXE 소관이며 이 항목은 픽스처를 **쓰는** 쪽이다. 이로써 `FakeRwModule.h` 충돌(EXE-21 · 열린 PR #658)도 소멸한다. 태그는 `docs` 오분류를 `refactor` 로 정정(EXE-21 과 동일). flat 분해·요약 행·Discrete/Categorical 분류 자체의 테스트도 EXE 몫 — CON-c17.

### CON-10 · Value 인라인 편집의 영속 정책을 정한다
- 종류: DEC | 규모: S | 태그: A, C
- 목표: 세대 모델 도입 뒤 Value 편집은 레지스트리의 메모리 세대만 바꾸고 프로젝트 재로드에서 사라진다. 세 안 중 하나를 기록한다 — (A) 세션 한정으로 못박고 표·툴팁에 "저장되지 않음" 표시 (B) `ConditionParameter_Set{N}.json` 에 `{uuid, entry_ptr, param, value}` 덮어쓰기 절을 두고 로드 직후 `toMutable→edit→seal→publish` 로 재적용 (C) 편집 시 deck 파일 자체를 `exportSolverInput` 으로 다시 쓴다 (content uuid·원장 스탬프 갱신 수반).
- 완료 기준: 결정 기록 — 선택안, 하류(DOE 주입·Launcher 참조 파일·Model Runner `inputFileName`)에 미치는 영향, 후속 PR 범위
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: CON-D5 · CON-c05
- 비고: (B) 가 가장 자연스럽지만 PER 의 저장 포맷 규칙과 PRJ 의 Set 원장(`DashSetReferenceModel`)에 걸친다. (C) 는 #617 의 "덮어쓰기 = invalidate" 흐름과 충돌한다.

### CON-11 · `saveDvCondition` 의 읽기-병합-직쓰기를 공용 JSON 헬퍼로 이행한다
- 종류: PR | 규모: S | 태그: A · refactor
- 목표: `DashConditionParameterizationPresentationModel::saveDvCondition` 이 `QFile` 로 기존 파일을 읽어 `DV-Condition` 절을 합친 뒤 `QIODevice::Truncate` 직쓰기하는 경로(RMW · `write` 길이 무검사)를 **PER-02 가 공용 진입점으로 승격하는 `DashSaveSystem` 헬퍼**(`readJsonFile`/`writeJsonFile` — QSaveFile · `Result` 반환)로 바꾼다. 쓰기 중 크래시·디스크 풀에서 `FE Condition` 등 기존 절이 함께 소실되지 않는다. 동작 불변.
- 완료 기준: (1) `viewmodel/DashConditionParameterizationPresentationModel.cpp` 에 `QFile` 직쓰기 0 (2) 쓰기 실패(읽기 전용 경로) 시 기존 파일 바이트 동일 + WARN 에 사유 (3) `ConditionParameter_<Set>.json` 저장→로드→재저장 동일 — 케이스 1건 (PER-05 왕복 헬퍼가 랜딩해 있으면 그것으로, 아니면 이 TU 안에서 비교)
- 변경 범위: viewmodel/DashConditionParameterizationPresentationModel.cpp · tests/TestConditionParameterization.cpp (왕복 케이스) · tests/CMakeLists.txt (`test_condition_parameterization` 타깃에 PM `.cpp` 추가)
- 선행: PER-02 · CON-01 (왕복 케이스가 설정 JSON 을 행에 적용하는 seam 을 쓴다)
- 충돌: CON-09 (같은 테스트 파일) · 열린 PR #651 #652 #654 #655 (`tests/CMakeLists.txt`) · PER-02 · PER-05 · UIC-17 · DEV 의 `tests/CMakeLists.txt` 항목 · B2 교집합: tests/CMakeLists.txt → 공유 12건(deps.md 5절) · TestConditionParameterization.cpp → CON-02
- 흡수: #479 · #478 · #480 (CON 몫, PER-c24 이관) · CON-c23
- 비고: **문구 교정(decisions ③)** — PER-02 는 `utils/DashJsonFile` 신설이 아니라 `persistence/DashSaveSystem::read/writeJsonFile` 승격으로 확정됐다. API 이름도 `readObject/writeObject` → `readJsonFile/writeJsonFile`. **`tests/CMakeLists.txt` 추가 근거(검토 #10)** — `test_condition_parameterization` 타깃(`tests/CMakeLists.txt:616-623`)의 소스가 모델·`DashSetReferenceModel`·registry.h·`DashRwDocument`·`DashRwActor`·`DashRwDocumentHandle` 뿐이고 `viewmodel/DashConditionParameterizationPresentationModel.cpp` 가 없어, 왕복 케이스를 이 TU 에 두려면 링크를 늘려야 한다. 대안 — PM 을 링크하지 않고 PER-02 의 `TestJsonFile` 에 케이스를 두면 `tests/CMakeLists.txt` 충돌 10건을 피할 수 있다. 구현에서 택일하고, 후자를 고르면 완료 기준 (3) 과 변경 범위에서 CMakeLists 를 뺀다. `loadFromJson` 의 재바인딩 write-back 은 이미 QSaveFile. 버전 키는 PER-04 뒤 헬퍼가 자동 기록 — 여기서 따로 하지 않는다. `DashDesignVariableModel::saveToJsonFiles` 는 DOE-17 (B2 — 소속 DOE). **2차 반영(C' 2차)** — `선행: PER-05` 제거 (PER 검토 #9: 왕복 게이트를 선행으로 걸면 bug fix 가 인프라 PR 을 기다린다. 왕복 케이스는 모듈 완료 기준에만 두고 선행으로 걸지 않는다 — DOE-17 과 같은 처리). `충돌` 의 PER-05 는 같은 테스트 파일을 만지므로 유지.

### CON-12 · FE 표의 체크 토글을 모델에 바로 써서 재구축에 잃지 않게 한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: col 0 의 `itemChanged` 가 헤더 체크박스만 갱신하는 자리에서 `mModel->setData(index(modelRow,0), state, Qt::CheckStateRole)` 로 write-through 하고, `syncDvFromCheckedFeConditions` 선두의 역동기화 루프를 지운다. 지금은 토글이 `QTableWidgetItem` 에만 머물다가 `modelReset` → `populateFeConditionTable` 이 모델의 `CheckStateRole` 로 다시 그려 저장 전 토글이 조용히 사라진다.
- 완료 기준: (1) 체크 → Value 셀 편집(`commitEntryValue` 가 reset 을 낸다) 뒤에도 체크가 남는다 (2) 헤더 전체 체크/해제도 모델에 반영된다 (3) [Set Design Variable] 결과가 전과 같다 — `collectCheckedFeRows` 가 `getCheckedParameters()` 를 쓰므로 write-through 만으로 충분하다
- 변경 범위: view/DashConditionParameterizationWidget.cpp
- 선행: CON-01 (모델 체크의 의미 — 저장된 체크를 재구축 뒤 적용하는 계약 — 이 먼저 서야 write-through 가 그 값과 싸우지 않는다)
- 충돌: CON-03 CON-04 CON-06 CON-07 (같은 위젯) · B2 교집합: DashConditionParameterizationWidget.cpp → CON-05 DOE-19 UIC-19 UIC-20
- 흡수: CON-c26
- 비고: 검토 #11 신설. 좌표 — `itemChanged` 핸들러 `:166-170`(헤더만) · `modelReset`→`populateFeConditionTable` 연결 `:297-302` · 재취득 `:510-518` · 버튼 때만 도는 역동기화 루프 `:566-577` · reset 원천 `model/DashConditionParameterization.cpp:458`. CON-c18(덮어쓰기 재로드) 도 같은 소실을 일으키므로 CON-03 뒤에 랜딩하면 그 경로까지 덮인다. `blockSignals(true)` 로 그리는 `populateFeConditionTable` 안에서는 `itemChanged` 가 안 나므로 write-through 가 재귀하지 않는다.

## 대응표

| 원천 | 항목 | 비고 |
|---|---|---|
| CON-D1 | CON-05 | |
| CON-D2 | 항목 없음 | 해소됨 — f14c5831(#559)·d8be33a4(#564), `Registry::load` 가 뮤텍스+in-flight 대기 |
| CON-D3 | CON-02 | |
| CON-D4 | CON-06 | |
| CON-D5 | CON-10 | DEC |
| CON-D6 | 항목 없음 | 해소됨 — f14c5831(#559), 샘플별 클론·원복 없음 |
| CON-D7 | CON-01 | |
| CON-D8 | → DOE-10 | CON-08 병합(B2) — `DashDesignVariableModel` 소속 DOE. CON-c08 도 DOE-10 |
| CON-D9 | CON-07 | |
| CON-D10 | 항목 없음 | 해소됨 — #603 Done·5b29c6f7(#617), `DashSetReferenceModel` 핀 |
| CON-D11 | 항목 없음 | 해소됨 — f14c5831(#559), 봉인 세대 동기 접근자 |
| CON-D12 | 항목 없음 | 해소됨 — f14c5831(#559), `applyConditionDvs` 실패가 샘플 Failed |
| CON-D13 | 범위밖 → ANA | `DashResultsAnalyzerWidget::onTargetDataChanged` 의 `"checked"` → `"boolean"` |
| CON-U1 | CON-06 | |
| CON-U3 | CON-06 | |
| CON-U5 | CON-09 · 범위밖 → EXE (CON-c17) | 부분 해소 — 편집 세대·액터·DOE 주입은 이미 테스트됨 |
| #645 (접점) | CON-03 · 범위밖 → PRJ (CON-c19) | CON 몫 = 표시 중 위젯 재로드 |
| #551 (접점) | CON-04 | PRJ 가 7개 위젯을 한 PR 로 묶으면 흡수 |
| #551 별개 1 (PRJ-c19 이관) | CON-04 | delegate 멤버 QPointer 화로 2-인자 `setModel` 조기 반환 경로와 무관 (CON-c22) |
| #645-1 (PRJ-20 → CON-03) | CON-03 | decisions ⑦ — PRJ-20 은 CLOSE, 집행은 CON-03. 훅 자리는 `addReferenceFile` 의 `registry.load` 뒤 |
| #479 · #478 · #480 CON 몫 (PER-c24 이관) | CON-11 | `saveDvCondition` 헬퍼 이행 (CON-c23) · 선행 PER-02 |
| CON-D9 · CON-D11 (EXE-c43 이관) | CON-07 · 해소됨 | CON-c24 — D9 는 CON-07, D11 은 f14c5831 |
| CON-U5 (UIC-c57 이관) | CON-09 | CON-c25 — 부분 해소, c16 과 동일. 픽스처 몫(구 완료 기준 (2))은 EXE-21 (decisions ⑦) |
| Code-Map CON 6절 (표 체크 이중 보관) | CON-12 | 검토 #11 신설 — CON-c26 |
| Code-Map CON 3-1 (`Q_UNUSED(projectPath)`) | CON-05 | 검토 #13 — CON-c28 |
| Code-Map CON 3-1 (공용 DV 모델 `setParent`) | 범위밖 → DOE | 검토 #12 — CON-c27. **보류: DOE 몫** (`DashDesignVariableModel` 소유자 결정). CAD 접점 |
