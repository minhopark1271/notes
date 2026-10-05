# Condition Parameterization — 사용자 플로우 ↔ 코드 대응

> **성격**: 독립 참조 문서. 사용자 행위가 밟는 함수 체인의 대응표 — 수정 계획·우선순위 판정은 담지 않는다.
> **좌표 기준**: `dev` @ `ac6e4e6` 실측 (유효기간 있음). 정적 코드 근거만 — 빌드·실행 검증 없음. RW 모듈 내부(Abaqus·AnsysMechanical DLL)는 별도 저장소라 GUI 호출측 코드로만 확인했다.

## 개요

화면 1면(탭 2종)과 로직 클래스 12종이 외부 reader-writer(RW) DLL 이 파싱한 FEM deck 하나를 표로 펼치고, 그중 Continuous 로 분류된 스칼라 필드만 설계변수로 승격한다. 사용자 입력은 표의 체크박스·인라인 에디터와 버튼 1개가 전부이고, 렌더뷰로 나가는 유일한 출력은 선택 행의 조건 하이라이트다 — 렌더뷰에서 무언가를 찍거나 끄는 경로가 없다.

도메인 모델은 `ParameterRow` 배열(`model/DashConditionParameterization.h:15-32`) 하나로, RW 세션이 내주는 `DashFeConditionEntry`(`controller/DashRwSession.h:67-83`)를 1:1로 옮긴 것에 체크 상태 한 비트를 얹은 것이다. `types::Set`·`Function` 같은 RW SDK 타입은 이 경로에 없다 — 액터 경계에서 전부 값으로 환산된다. 3\~6절은 코드가 하는 일만, 결함은 7절 — 본문 `→ D{n}` 이 링크다.

---

## 1. 화면 1면과 소유 클래스

우측 dock 스택에 카테고리 이름 `"Condition Parameterization"` 으로 등록된 위젯 하나가 전부다(`view/DashMainWindow.cpp:510`). 진입 시 렌더뷰 오버레이 툴바는 명시적으로 숨는다(`:1041`).

| 탭 | 구성 위젯 (`ui/DashConditionParameterizationWidget.ui`) | 역할 |
|---|---|---|
| **FE Condition** | `mFeConditionLabel` · `mTableView`(`QTableWidget`) · `mSetDvButton` (`:18-52`) | FE 조건을 엔트리 단위 행으로 열람·편집·체크 · 선택 행 하이라이트 |
| **DV-Condition** | `mDvConditionTableView`(`QTableView`) (`:54-64`) | 승격된 DV 의 Min/Max/Cases 조정 |

| 로직 클래스 (줄) | 담당 |
|---|---|
| `…ParameterizationWidget` (676) | 탭 구성 · 표 재구축 · 체크 수집 · 하이라이트 · 파일 워처 |
| `DashConditionParameterization` (517) | `ParameterRow` 배열 = 표 모델. deck→행 변환 · 체크 상태 JSON 복원 |
| `…PresentationModel` (142) | `DV-Condition` JSON 조립 · read-merge-write |
| `DashFeConditionValueDelegate` (184) | 편집 스키마 → 에디터 선택 · 커밋 · 롤백 |
| `DashDesignVariableModel` (486) | Geometry·Condition 공용 DV 표 모델 (`DashManager` 소유) |
| `DashRenderingManager` | 조건 하이라이트 레이어 (`.h:78`·`:81`·`:84`) |
| `DashAnalysisModelContext` (343) | 렌더 표현 + RW 세션 보유. RW 질의는 전량 위임(`:258-343`) |
| `…ContextRegistry` (107) | `filePath` → context 캐시 + active context 1개 |
| `DashRwSession` (1,530) | deck 1개 = 모듈 인스턴스 1개. 심볼 uuid 맵 · 스키마/shape 캐시 |
| `DashRwClient` (169) | 액터로 마샬링하는 값 핸들 (복사 가능, RAII close) |
| `DashRwActor` (266) | RW DLL 단독 소유자. 현재 GUI 스레드 상주 |
| `DashDvKind` (`.h`, 35) | DV 분류 4종 + 체크 정책 `isDvCheckable` |

특징 셋이 이후 절에서 반복된다 — 위젯·모델은 RW 를 직접 참조하지 않고(전부 `DashAnalysisModelContext` 경유, 예외는 위젯이 직접 부르는 렌더링 `Widget:167-175`·`:242-244`), DV 표 모델은 이 모듈 소유가 아니며(`DashManager` 의 전역 공유 인스턴스를 Geometry 파라미터화와 공유), 모듈 안에 스레드 우회·조건부 컴파일이 없다(`processEvents` 0곳 · `DASH_BUILD_*` 0곳 · `Qt::UserRole` 은 "시각 행 → 모델 행" 한 용도).

---

## 2. 전체 동선

```
1. 모듈 진입   Project Tree > Condition Parameterization > Set{N}
               dock 교체 · 렌더뷰 툴바 숨김 · 설정 JSON 선(先)읽기 (행이 없어 체크가 안 선다)
               ※ deck 을 고르는 UI 가 모듈 안에 없다 — 대상은 전역 active context
2. deck 확정   Modeling Tree 에서 .dat/.inp 열기·체크 → active context 교체 → 위젯 자동 refresh
               ※ 진입 전후 순서 무관. RW 세션 로드 1회가 이 모듈이 쓰는 모든 데이터의 출처
3. 표 구성     조건 1개 → 엔트리 N행 (Abaqus entries[] / Ansys 스칼라 필드 per-component)
               ※ Continuous 행만 보인다 — 나머지는 회색이 아니라 제외
4. 하이라이트  행 선택 → 조건 payload → 렌더 레이어. 집중·체적하중만 화살표
               ※ payload 가 없으면 조용히 해제 — 이름 매칭 폴백 없음
5. 값 편집     Value 열 인라인 (선택) — 스키마 모양이 에디터를 정하고 커밋은 deck 으로 먼저 간다
               ※ 되돌리기 없음. 파일화는 하류 export 시점에만
6. DV 승격     [Set Design Variable] → 표 체크를 모델로 역동기화 → 체크 행만 수집
               → DV-Condition 절 전량 재기록(증분 아님). 초기 범위는 현재 값이 한쪽 끝
7. 범위 조정   DV-Condition 탭 Min/Max/Cases — 셀 편집 1회당 JSON write-through 1회

[산출] configs/ConditionParameter_Set{N}.json 의 "DV-Condition" 절
       하류(DOE·Data Preprocessor·Model Runner)가 읽는 전부
```

---

## 3. 단계별 대응

### 3-1. 모듈 진입

갈래가 없다. Set 클릭 → `currentChanged`(`DashMainWindow.cpp:528`) → `onProjectTreeSelectionChanged:577` → `handleSubItemSelection:946` → `:1040-1042`(툴바 숨김 + 분기) → `handleConditionParameterizationSelection:1066`. **[+ New Set]** 은 `newSetRequested`(`:530`) → `onNewSetRequested:600` → `createNewSet:607` → `createModuleJsonFile("ConditionParameter", …)`(`DashProject.cpp:584`, 호출 `:700`) → `addConditionParameterization:171` → `QTimer::singleShot(200ms)` 트리 선택(`:625`)으로 같은 경로에 합류하며 내용 `{}` 인 설정 JSON 을 남긴다.

```
handleConditionParameterizationSelection(index)          DashMainWindow.cpp:1066
  ├─ project->getConditionParameterizations().at(index.row())   :1070-1077
  │     ※ 이름이 아니라 트리 행 인덱스 조회 — 트리 순서와 배열 순서가 계약
  ├─ newModel->setProjectDirectory(getConfigsDirectory())       :1082
  │     └─ Model:29 → getConfigFilePath(...):49 → loadFromJson():53
  └─ widget->setModel(newModel, m_projectPath):1084 · setCurrentWidget(...):1085
```

`setProjectDirectory(path)` 는 **인자를 쓰지 않는다** — 비었는지만 보고 경로는 `getConfigFilePath`(`DashIOController.cpp:12`)로 다시 유도한다. → D1

```
setModel(model, projectPath)                    Widget:269
  ├─ Q_UNUSED(projectPath):271 · mModel = qobject_cast<…>(model):277
  │     · mModel->setProjectDirectory(getProjectPath()):283
  ├─ mDesignVariableModel = DashManager::Mgr()->GetDesignVariableModel()    :291
  │     └─ setParent(this)(공용 싱글턴 모델의 부모를 위젯으로 재지정):293
  │        · mDvConditionTableView->setModel(...):294 · connect(dataChanged→onSharedDvModelEdited):298-300
  ├─ setDataModel(mModel):305 · updateDvWatchers():308 · setupConnections():309
  ├─ onModelDataLoaded() → 하이라이트 해제 + populateFeConditionTable()      :310
  └─ activeFilePath 가 있으면 refreshFromFile(activeFilePath)                :313-316
```

**오버로드 2개 중 하나는 사실상 죽어 있다.** `setModel(DashConditionParameterization*)`(`:319`)은 `dataChanged → updateUI` 와 `dataLoaded → onModelDataLoaded` 를 잇는 유일한 지점(`:339-342`)인데, 호출처가 Set 삭제 경로(`DashMainWindow.cpp:732`, `:727-735`) 한 곳뿐이고 인자가 항상 `nullptr` 이라 `:330` 가드가 연결 블록을 건너뛴다. 실운영에서 `dataLoaded`(`Model:516`) 수신처는 0곳이다.

### 3-2. 참조 deck 확정

모듈은 대상 deck 을 스스로 고르지 않는다. 대상은 `…ContextRegistry` 의 **active context 1개**이고, 바꾸는 것은 파일 열기(`DashMainWindow.cpp:2248`)와 Modeling Tree 체크 2종 — deck 루트 `dat_parent`(`:2419`, 자식 파트 가시성 일괄)·파트 `dat_part`(`:2446`, `controlVisibility`) — 셋 다 `setActiveContext` 로 수렴한다.

```
setActiveContext(filePath)                 Registry:50
  ├─ getOrLoad(filePath)                   :23
  │     ├─ canonicalFilePath 로 키 정규화 · 뮤텍스 아래 캐시 조회(히트면 반환)   :24-32
  │     ├─ 뮤텍스 밖에서 로드                                                 :34-39  → D2
  │     │     └─ Context::loadAnalysisModelFromFile:58 → RwSession::open:1148
  │     └─ 성공분만 뮤텍스 아래 맵에 삽입 — 실패는 캐시하지 않는다              :41-47
  ├─ 같은 경로면 actor 갱신만 하고 반환 — 시그널을 다시 쏘지 않는다             :55-58
  └─ m_activeFilePath 갱신 + emit activeContextChanged                       :60-62
```

`activeContextChanged` 람다(`DashMainWindow.cpp:423-431`)가 `refreshFromFile`(`Widget:367`)을 부르고, 이 슬롯은 `mModel` 이 null 이거나(`:369-371` — 모듈 진입 전) 파일이 없으면(`:372-374`) 즉시 반환한 뒤 `refreshFromLoadedAnalysis`(`Model:114`)로 간다. 진입 시점에도 같은 슬롯을 한 번 더 부르므로(`Widget:313-316`) deck 을 먼저 열든 나중에 열든 결과가 같다.

**deck → FE 조건 추출** — `DashRwSession::load`(`:1360`)가 한 번 도는 것이 이 모듈이 쓰는 모든 데이터의 출처다.

```
DashRwSession::load(filePath, identityStoreDir)      :1360
  ├─ 확장자로 모듈 선택 — .inp→Abaqus, .dat→AnsysMechanical, 그 외 실패   :1361-1370
  ├─ DashRwActor::instance().openSession(kind)                          :1379
  ├─ rwResolveContentIdentity — SHA-256(8MB 청크 · (size,mtime) 메모이즈, :1030) + 경로 유도 uuid,
  │     스토어 read-modify-write 는 static QMutex 로 직렬화. 저장 uuid 가 있으면 그것을 쓰고
  │     해시 불일치만 기록                              :1090 · :1095-1109 · :1124-1132
  ├─ loadContent:1400 · getSymbolTree:1406
  ├─ FECondition 심볼 수집 → names/Uuids/Caps, 이름 충돌은 "{name}_{맵크기}" 채번  :1412-1424
  ├─ 모든 비컨테이너 노드에 get_data — Set→nodeSets/elementSets:1456-1470 ·
  │     Mesh→parts/partUuids/partNames(비 MeshEditable 은 ResolveInstancePart):1472-1507
  ├─ Abaqus 인데 셋이 안 나오면 .inp 직접 파싱          :1515-1519
  └─ diagnoseFeConditionPayloads (DASH_RW_FE_DIAG=1)   :1521-1523 → :1237
```

심볼 uuid 는 (content uuid, AST 경로)의 결정적 함수라, content uuid 를 파일별로 고정해 두면 세션을 넘어 재사용된다 — 3-8 의 DV 바인딩이 이름보다 uuid 를 우선하는 근거다. 파일이 바뀌면 SHA-256 불일치로 `referenceModelChangedOnDisk()`(`:1014`)가 서지만 **uuid 자체는 바꾸지 않는다**.

**deck → 행 변환**

```
refreshFromLoadedAnalysis(filePath)                  Model:114
  ├─ registry.getOrLoad(filePath):118 · beginResetModel():128
  ├─ for name in ctx->getFeConditionNames()          :133-206
  │     ├─ getFeConditionTypeString(name) ← get_symbol_detail 왕복:134
  │     │  · getFeConditionUuid:135 · getFeConditionEntries:136 (RwSession:639)
  │     ├─ 사라진 (entryPtr|param) 조합의 기존 행 제거              :141-149
  │     ├─ 있으면 갱신 / 없으면 신규 push                          :151-186
  │     │     └─ 갱신은 isChecked 를 안 건드린다 — 체크는 행의 수명을 탄다  :160-169
  │     └─ dvKey 채번                                             :188-205
  └─ endResetModel()  → modelReset → 표 재구축                     :208
```

`m_params` 는 **한 번도 clear 되지 않는다.** 다른 deck 을 열면 그 행이 (name, source) 로 구분되어 누적된다. `buildDvConditionJson` 이 "각 파라미터 자신의 source 를 쓴다"(`PM:67`)고 적고 하류 `DashAnalysisLauncher.cpp:1243-1278` 이 DV 별 `source` 로 여러 참조 파일을 수집하는 것이 이 누적을 전제한 설계다. → D3

`dvKey` 채번(`Model:188-205`)은 하류 계약의 뿌리다. 접미사만 붙이고 접두사를 안 붙이는 것은 하류가 키를 사전순 정렬하기 때문이다(`:188-191` 주석).

| 조건 | dvKey | 근거 |
|---|---|---|
| 엔트리 1개 | `{name}` (맨이름) | 기존 config 와 `${name}` 템플릿 토큰 호환 |
| 엔트리 다수 · `entryPtr` 있음 (Abaqus) | `{name}_e{N}` | `N` = `/entries/N` 의 마지막 세그먼트 |
| 엔트리 다수 · `entryPtr` 빈 문자열 (Ansys flat) | `{name}_{param}` | 벡터 성분(`omega_x` 등)을 성분별로 파라미터화 |

**엔트리 분해** — `getFeConditionEntries`(`RwSession:639`)가 세 갈래로 갈린다.

| 갈래 | 판별 | 행 구성 | `entryPtr` |
|---|---|---|---|
| **Abaqus entries[]** | `detail.entries` 가 비지 않음(`:654`) | 원소당 1행. `mode=="type"`(ENCASTRE 등) 읽기전용(`:663-665`), `magnitude` 있으면 편집 가능(`:666-677`) | `/entries/{i}` |
| **Ansys flat** | entries 없음 + 편집 스키마의 스칼라/enum 필드가 deck 에 실재(`:696-714`) | **스키마 필드당 1행** — `CMOMEGA` 는 `omega_x`/`_y`/`_z` 로 쪼개진다 | `""` (공유) |
| **읽기전용 요약** | 위 둘 다 아님(`:718-737`) | 1행. omega 는 `(x, y, z)`, 그 외 `value` 또는 `labels` | `""` |

편집 가능 여부는 두 겹 — 심볼의 `DataEditable` 능력(`:647-649`)과 엔트리 모양(`rwEntryEditable:436`)이고, flat 은 모듈이 편집 스키마를 내주는지로 판정한다(`isFeConditionEditable:937`). `dvKind` 는 편집 가능으로 판정된 자리에서만 설정되고 기본값이 `None` 이라(`RwSession.h:77-80` 주석) 읽기전용 엔트리와 요약 행은 분류 단계를 밟지 못한다.

**DV 분류** — `rwPropertyDvKind`(`RwSession:495`)가 스키마 프로퍼티 모양 하나로 4종을 가른다.

| 스키마 모양 | `DashDvKind` | DV JSON `type` | `meta` | 표 노출 |
|---|---|---|---|---|
| `const` 있음 | `None` | — | — | X |
| `enum` 있음 | `Categorical` | `categorical` | `case: [문자열]` | X |
| `{"type":"number"}` | `Continuous` | `continuous` | `min` / `max` | **O** |
| `oneOf[number, string]` (APDL `%ref%` 방언) | `Continuous` | `continuous` | `min` / `max` | **O** |
| `integer` + `minimum`/`maximum`, 폭 ≤ 32 | `Discrete` | `discrete` | `case: [숫자]` | X |
| 그 외 (폭 넓은 integer 등) | `None` | — | — | X |

`isDvCheckable`(`DashDvKind.h:32-35`)이 `Continuous` 만 통과시키고 `populateFeConditionTable:389-395` 가 그 결과로 행 자체를 걸러낸다. **읽기전용 행과 모드 키(SFE `kval` 등)는 회색 표시가 아니라 부재다.** 헤더 정책 주석(`DashDvKind.h:26-31`)이 이유를 적는다 — discrete 샘플러는 case 값이 아니라 0..count 인덱스를 내보내고 categorical 은 `categoricalMappings` 를 거치는데, FE 적용 경로에 그 역매핑이 없다.

### 3-3. FE Condition 표 구성

`populateFeConditionTable`(`Widget:381`)은 `QTableWidget` 을 **매번 통째로 재구축**한다. 트리거는 `modelReset`(`:265-266`)과 `onModelDataLoaded` 경유 직접 호출(`:310`·`:364`)이다.

```
populateFeConditionTable()                        Widget:381
  ├─ visibleRows = isDvCheckable(dvKind) 인 모델 행만               :389-395
  ├─ clear()+setRowCount/ColumnCount:397-399 · 헤더를 모델 headerData 에서 재취득:401-405
  ├─ 열 resize 모드·고정 폭 재적용                                   :408-419
  ├─ blockSignals(true) 로 셀 채우기                                :422-457
  │     ├─ col 0: 체크박스 + setData(Qt::UserRole, 모델 행 id)       :428-433
  │     └─ col 1..6: 표시 문자열 + 모델 flags·전경색·툴팁 미러링       :435-453
  ├─ setSortingEnabled(true) + sortItems(2, Ascending)              :458-459
  └─ 헤더 체크박스 상태 갱신·재배치                                   :461-471
```

**표가 사용자 정렬 가능이라 시각 행 ≠ 모델 행이다.** 모든 셀이 `Qt::UserRole` 에 모델 행 번호를 들고(`:432`·`:444`), delegate·체크 수집·하이라이트가 그 값만 본다(`Delegate:53-58` · `Widget:487`·`:214`).

열 계약은 모델이 정본이다 — `"" | Source | Name | Type | Target | Param | Value` 7열(`Model:88`). `.ui` 는 5열만 선언했고(`ui/…:30-34`) `setColumnCount(mModel->columnCount())`(`:399`)가 매번 덮어쓴다. → D4

`Param` 열은 원시 필드명이 아니라 스키마 `title` 을 우선하고(`Model:251-254` — SFE 의 `val1` 은 "Convection - film coefficient"), `dvKey` 는 원시 이름을 쓴다. 툴팁도 스키마 `title`/`description` 에서 와(`Model:272-285`) 아이템에 복사된다(`:449-452`). 읽기전용 행의 회색 표시·전용 툴팁(`Model:262-270`)과 delegate 의 `nullptr` 분기(`Delegate:117`)는 그 행이 표에 오르지 못하므로 도달하지 않는다.

헤더 일괄 체크박스는 `QHeaderView` 위에 얹은 별도 3-state `QCheckBox` 이고(`Widget:122-153`), 섹션 리사이즈·지오메트리 변경마다 `setGeometry` 로 위치를 다시 계산한다(`:126-140`). 초기 배치가 `QTimer::singleShot(0)` 인 것은 헤더 레이아웃 전에는 좌표를 못 구하기 때문이다(`:140`·`:462-471`).

### 3-4. 조건 하이라이트 — 표 행 선택

표는 행 단위 선택이고(`Widget:162`), 선택이 바뀔 때마다 렌더뷰 레이어를 다시 그린다.

```
itemSelectionChanged:163-164 → onFeConditionSelectionChanged      Widget:183
  ├─ 선택 없음 / 아이템 없음 → clearFeConditionHighlight          :191-203
  ├─ col 0 의 UserRole 로 모델 행 → rowAt(...)                    :211-213
  ├─ 같은 조건이고 레이어가 살아 있으면 재질의하지 않는다           :226-228
  │     ※ 조건 1개가 여러 행(entries[], flat 성분행)이라 필요한 가드
  ├─ ctx->getFeConditionShape(row->name)     Context:337 → RwSession:887
  │     ├─ 조건별 캐시 히트면 반환:891-894 · client.getData(uuid):903
  │     ├─ FECondition payload + 점 있는 grid 면 valid            :907-919
  │     ├─ 아니면 경고만 남기고 invalid — 이름 매칭 폴백 없음       :925-931
  │     └─ 실패도 캐시한다                                        :933
  ├─ shape.valid 아니면 해제하고 종료                              :236-241
  └─ renderMgr->updateFeConditionHighlight(mesh, maskArrayName, onPoints, arrowArrayName)
                                             Widget:242-244 · RenderingManager.h:78
```

화살표 여부는 조건 종류가 정한다(`arrowArrayName:841-870`) — `ConcentratedLoad` 는 `Force`→`Moment`(3성분 우선 1개), `BodyLoad` 는 `AngularVelocity` 로 화살표, `PrescribedDof`·`SurfaceLoad`·`Unknown` 은 소속(mask) 표시만. 주석이 근거를 적는다(`:843-846`) — 구속은 크기가 없거나 벡터가 아니라 구속으로 읽히고, 면하중은 방향 없는 스칼라 압력이다.

해제 경로는 셋 — 선택 해제(`:191-203`)·모듈 이탈(`hideEvent:177-181`)·표 재구축 직전(`onModelDataLoaded:363`). 마지막은 세션이 다시 열렸을 수 있어 하이라이트 대상의 존재가 보장되지 않기 때문이다.

### 3-5. 값 편집 — Value 열 인라인

Value 열(6)만 편집 가능하고 조건은 `param.editable && !param.param.isEmpty()` 다(`Model:309-314`). `QTableWidget` 은 자체 아이템 flags 를 쓰므로 위젯이 모델 flags 를 아이템에 복사해 준다(`Widget:439-443`) — 이 미러링이 없으면 delegate 가 에디터를 못 연다. 에디터 선택은 **스키마 모양 → 위젯 종류** 단일 규칙이다(`Delegate:60-118`).

| 스키마 | 에디터 | 커밋 값 |
|---|---|---|
| `enum` | `QComboBox` (항목 data 에 원시 `QJsonValue` 보존) | 표시 문자열이 아니라 타입 보존된 값 (`:146-150`) |
| `{"type":"integer"}` | `QSpinBox` (`minimum`/`maximum` 반영) | `int` |
| `{"type":"number"}` | `QLineEdit` + `QDoubleValidator(ScientificNotation)` | `double` — 지수 입력(`1e6`) 때문에 스핀박스를 안 쓴다 (`:103`) |
| `oneOf[number, string]` | `QLineEdit` + 정규식 `^(-?\d+(\.\d+)?([eE][+-]?\d+)?\|%[A-Za-z_]\w*%)$` | 숫자면 `double`, `%ref%` 면 문자열 (`:161`) |
| 그 외 (`const`/`string`/미상) | 없음 (`nullptr`) | — |

커밋은 표가 아니라 **deck 으로 먼저 간다.**

```
setModelData(editor, model, index)                 Delegate:137
  └─ m_dataModel->commitEntryValue(modelRow, newValue, &error)   Model:339
        ├─ editable/param 비었거나 컨텍스트 없으면 거부            :346-358
        ├─ ctx->editFeConditionEntry(name, entryPtr, {param: value})  Context:330
        │     └─ RwSession:775
        │           ├─ getFeConditionEditSchema(캐시):793 · rwEffectiveProperties(oneOf 병합):794
        │           ├─ 대상 엔트리 존재 확인 (entryPtr 일치)                    :798-807
        │           ├─ payload = 스키마 프로퍼티 ∩ entry.raw + 스키마 const     :811-823
        │           │     ※ Ansys "target"/"component" 같은 읽기전용 필드는 안 실림
        │           ├─ changes 덮어쓰기, 스키마에 없는 키면 실패                :824-828
        │           └─ client.editData(uuid, entryPtr, json)                  :830-832
        ├─ 모듈이 정규화했을 수 있으니 캐노니컬 값을 다시 읽는다    :366-375
        └─ emit dataChanged(index(row,6), DisplayRole)            :376-377
```

성공하면 delegate 가 정렬을 잠시 끄고 캐노니컬 값을 셀에 반영해(`:174-183`) Value 열 정렬 상태에서 커밋 중 행이 이동하는 것을 막는다. 실패하면 **표에 아무것도 쓰지 않고** 에디터 아래 `QToolTip` 으로 사유만 띄운다(`:167-171`) — 암묵적 롤백이다.

**이 편집은 파일이 아니라 메모리의 deck 을 바꾼다.** 되돌리기 경로가 없고 파일화는 하류 `exportSolverInput` 시점에만 일어난다. → D5
편집을 막는 게이트도 없다. DOE 배치가 같은 컨텍스트·같은 세션을 쓰는 동안에도 이 경로는 열려 있다(5절). → D6

### 3-6. 설계변수 승격

`Set Design Variable` 한 번이 이 모듈의 유일한 영속화 지점이다 — 이 버튼 밖에서 파일에 기록되는 것은 DV-Condition 탭 편집(3-7)뿐.

```
[Set Design Variable] → syncDvFromCheckedFeConditions()   Widget:474
  ├─ 시각 행 순회 → UserRole 의 모델 행 id 로 setData(CheckStateRole)   :483-490
  │     ※ 이름 조회를 안 쓰는 이유: 같은 조건의 엔트리 행들이 이름을 공유
  ├─ jsonPath = getSettingsJsonPath():497 · m_blockDvWatcher = true:500
  ├─ m_pm->saveDvCondition(jsonPath, collectCheckedFeRows(), userPath)   PM:117
  │     ├─ getCheckedParameters() — isChecked && isDvCheckable 이중 필터  Model:392·:398
  │     ├─ 기존 파일을 읽어 다른 절 보존                                PM:123-128
  │     ├─ root["DV-Condition"] = buildDvConditionJson(rows, userPath)  PM:42
  │     └─ Truncate 로 전량 재기록                                     PM:133-140
  ├─ updateDvWatchers():508 · sharedModel->loadFromJsons({파일명}, configsDir):529
  ├─ reset()+resizeColumnsToContents():530-531 · m_blockDvWatcher = false:532
  └─ QMessageBox::information("Design Variables have been set successfully.")   :535
```

`buildDvConditionJson`(`PM:42`)의 엔트리 조립 — 키는 `row.dvKey`(비면 `row.name`) · `boolean` 은 체크 행만 쓰므로 항상 `true` · `source` 는 `resolvedSourcePath`(가능하면 프로젝트 상대경로, 실패하면 원본, 빈 값이면 `"FECondition"`, `PM:16-40`) · `type` 은 `toDvTypeString(dvKind)`(`DashDvKind.h:16`) · `uuid`/`entry_ptr`/`param` 은 uuid 가 있을 때만 3개 동시(`PM:74-87`) · `meta.default` 는 현재 값의 숫자 파싱 결과, 실패면 `null`(`PM:88-93`) · `meta.case` 는 Discrete/Categorical 일 때만(`PM:97-110`, 현재 정책상 도달 불가).

초기 범위는 **현재 값을 한쪽 끝으로 삼는 규칙**이다(`PM:54-65`) — `v > 1e-9` 면 `[0, v]`, `v < -1e-9` 면 `[v, 0]`, `0` 이거나 파싱 불가(`%ref%` 등)면 `[0, 1]`.

`DV-Condition` 절은 **매번 통째로 다시 쓰인다** — 체크를 다 해제하고 누르면 절이 빈 객체가 된다. → D7 이것이 gen1\~gen4 마이그레이션의 실행 기제이기도 하다: 옛 엔트리도 한 번 sync 되면 그 자리에서 gen4 형태로 백필된다(`PM:75-83`).

### 3-7. DV-Condition 탭 편집

DV 표 모델은 이 모듈 전용이 아니라 `DashManager` 소유의 **공용** `DashDesignVariableModel` 이다. Source·Name 은 편집 불가, Type 은 표에서 불가(DOE 런처의 검증된 콤보만 `setData` 직접 호출), Min·Max 는 `continuous` 일 때, Cases 는 `discrete`/`categorical` 일 때만 열린다(`flags:84-107`). 편집 1회마다 파일이 쓰인다.

```
셀 편집 → dataChanged → onSharedDvModelEdited()      Widget:639
  ├─ m_blockDvWatcher 또는 모델 null 이면 반환:645-647 · m_blockDvWatcher = true:648
  ├─ saveToJsonFiles()                                DvModel:375
  │     ├─ spec.fileName 별 그룹핑:389-394
  │     ├─ 파일명 문자열로 섹션 판정 ("Condition" 포함 → "DV-Condition")   :410-417
  │     ├─ JSON 에 없는 label 은 skip:428-430 · type/meta 만 갱신 후 Truncate 재기록:434-481
  └─ m_blockDvWatcher = false                         :650
```

섹션 판정이 **파일명 부분 문자열**이라는 점이 읽기·쓰기 양쪽의 계약이다(`DvModel:288-297`·`:410-417`). 매칭되지 않는 파일명은 조용히 `DV-Condition` 으로 기본 처리된다. → D8

`loadFromJsons` 는 `begin/endResetModel` 을 쓰고 `dataChanged` 를 내지 않으므로 워처가 유발한 리로드는 `onSharedDvModelEdited` 로 재진입하지 않는다(`Widget:641-644` 주석).

**파일 워처** — 생성자가 `fileChanged → onDvJsonChanged` 를 잇고(`:68-69`), `updateDvWatchers:558` 이 기존 감시를 전부 해제한 뒤 settings JSON(`:567-572`)과 userPath 디렉토리(`:580-587`)를 재등록한다. 디렉토리를 감시 목록에 넣지만 **`directoryChanged` 는 어디에도 연결돼 있지 않아**(레포 전수 0곳) `onDvJsonChanged` 의 `else` 분기(`:627-636`)와 `onDirChanged`(`:653`)는 도달 불가다. 자기 쓰기 억제도 실효가 없다 — 이벤트 루프 복귀 **전에** `m_blockDvWatcher` 를 false 로 되돌리고(`:532`) 다음 줄의 모달 `QMessageBox`(`:535`)가 중첩 이벤트 루프를 돌린다. → D9

### 3-8. 재진입과 복원

| 복원 대상 | 저장처 | 읽는 곳 | 상태 |
|---|---|---|---|
| DV 목록 · 범위 · 타입 | JSON `DV-Condition.*` | `DvModel::parseJsonFile:243` | 복원됨 |
| FE 표의 체크 상태 | JSON `DV-Condition.*.boolean` | `Model::loadFromJson:405-517` | 첫 진입에서만 실패 → D7 |
| Value 인라인 편집 | — | — | 소실 — 메모리 deck 에만 존재 → D5 |
| 대상 deck | — | 전역 active context | 프로젝트 재로드 시 다시 열어야 함 → D10 |
| 조건 하이라이트 | — | `m_highlightedCondition` 은 세션 한정, `hideEvent` 가 해제 | 소실 (의도) |
| 표 정렬·열 폭 | — | 매 재구축마다 초기화(`:408-419`·`:459`) | 소실 |

체크 상태 복원은 **행이 이미 있어야 작동한다.** `loadFromJson` 은 `m_params` 를 순회해 `isChecked` 를 세우는데(`:488-508`), 호출처 둘(`setProjectDirectory:53`·`setSetName:82`)이 모두 행을 만드는 `refreshFromLoadedAnalysis` 보다 **먼저** 돈다. 프로젝트 로드는 `restoreExistingModules`(`DashProject.cpp:1170`, Condition 분기 `:1269-1272`) → `setSetName` → `loadFromJson`(빈 배열) → `addConditionParameterization:171` → `:189` → `loadFromJson`(여전히 빈 배열)을 밟고, 첫 진입은 `:1082` → `loadFromJson`(빈 배열) → `setModel` → `refreshFromFile` → `refreshFromLoadedAnalysis` 가 행을 **`isChecked = false` 로** 만든다. 두 번째 진입부터는 `m_params` 가 차 있어 `loadFromJson` 이 체크를 세우고, 갱신 분기(`:160-169`)가 `isChecked` 를 안 건드리므로 그대로 뜬다.

바인딩 우선순위 자체는 4세대 마이그레이션을 감당하도록 설계돼 있다(`Model:434-447` 주석 · `:488-508` 구현).

| 세대 | 엔트리 필드 | 매칭 키 | 결과 |
|---|---|---|---|
| gen4 | `uuid` + `entry_ptr` + `param` | 세 값 전부 | 정확히 1행 |
| gen3 | `uuid` + `entry_ptr` | 두 값 | Abaqus 는 정확, flat 은 조건 전체 |
| gen2 | `uuid` | uuid | 그 조건의 모든 행 |
| gen1 | 없음 | `dvKey` 또는 `name` | 이름이 같은 모든 행 |

이름으로만 매칭됐는데 저장 uuid 가 현재 uuid 와 다르면 경고를 남기고 진행한다(`:498-507`) — deck 구조가 바뀌었을 수 있다는 신호다.

---

## 4. RW 경계 — 호출이 실제로 도달하는 곳

표 한 칸을 그리는 데도 외부 DLL 왕복이 필요하다. 경계는 3겹이다.

```
Widget / Model / Delegate            (GUI 스레드)
   │  DashAnalysisModelContext        — 렌더 표현 + 전량 위임 (Context:258-343)
   ▼
DashRwSession                         — deck 1개 = 모듈 인스턴스 1개, 심볼 맵·스키마/shape 캐시 소유
   │  DashRwClient                     — 값 핸들. 마지막 복사본 소멸 = 세션 close (RAII)
   ▼  invokeOnActor  (RwActor.h:105-115)
DashRwActor                           — RW DLL 단독 소유자. 현재 GUI 스레드 상주 (RwActor.cpp:30-36)
   ▼
dash::rw::IRWModule                   (Abaqus / AnsysMechanical DLL)
```

| 경계 규칙 | 근거 | 귀결 |
|---|---|---|
| **호출은 전부 동기다** | `invokeOnActor` 는 같은 스레드면 직접 호출(`RwActor.h:107-109`) | 액터가 GUI 스레드에 있어 현재 전부 직접 경로. 크로스스레드는 경고 후 `BlockingQueuedConnection`(`:110-114`) |
| **리졸버는 경계를 못 넘는다** | `types::Set` 이 모듈 내부로 되돌아가는 `std::function` 을 들어, 액터가 라벨을 즉시 실체화해 `DashRwSetData` 값으로 바꾼다(`materializeSet:119`, `doGetData:151-161`) | FECondition payload 의 소속 Set·mesh 리졸버도 같은 자리에서 실행(`:156-161`). Set 을 반환하는 `callFunction` 은 거부(`:260-263`) |
| **Mesh 는 통과하되 별칭이다** | 모듈 내부 메모리를 가리킨다(`DashRwClient.h:56-58`) | `edit_mesh` 왕복 밖 변형 금지. 이 모듈은 안 만지지만 세션을 공유하는 모핑 경로가 만진다 |
| **액터는 leaf 다** | `DashManager`·렌더링·view 를 참조하지 않는다(`RwActor.h:31-33`) | 스레드 이주 시 교착이 없는 근거. 이주 자체는 아직 안 됐다 |

캐시 셋의 수명은 전부 세션과 같다 — per-entry 편집 스키마(키 `"uuid\|entryPtr"`, **빈 객체로도 캐시**해 delegate 의 읽기전용 반복 질의를 막는다, `:748-763`) · 조건 shape(키는 조건 표시 이름, invalid 도 캐시, `:891-894`·`:933`) · content uuid(키는 canonical 경로, 스토어 파일에 영속, `:1090`). 반면 `get_symbol_detail` 은 캐시되지 않는다. → D11

액터 스레드 이주가 왜 아직 안 됐는지는 헤더가 직접 적어 둔다(`RwActor.h:17-30`) — 블로커가 vtk mesh 별칭과 **DOE 배치의 세션 공유**이고, 배치 격리 구현(`refactor/async-execution` 의 `17aed65`)은 이 브랜치에 포팅되지 않았다.

`tests/` 전체에 `ConditionParameterization`·`DashRwSession`·`DashRwActor`·`DashRwClient`·`DashDvKind` 참조 0건이다. 등록된 테스트 3종(`tst_line_assembler`·`tst_job_state`·`tst_process_runtime`)은 전부 프로세스·잡 계층이다(`tests/CMakeLists.txt:28-47`).

---

## 5. 산출 파일과 하류 소비자

산출물은 파일 하나의 절 하나다 — `configs/ConditionParameter_{Set}.json` 의 `"DV-Condition"`.

```jsonc
"DV-Condition": {
  "<dvKey>": {
    "boolean": true,
    "source": "<프로젝트 상대경로 | 파일명 | \"FECondition\">",
    "type": "continuous",                  // 현재 정책상 continuous 만 도달
    "uuid": "<조건 심볼 uuid>",
    "entry_ptr": "" | "/entries/N",
    "param": "magnitude" | "value" | "omega_z" | ...,
    "meta": { "default": <number|null>, "min": <number>, "max": <number> }
  }
}
```

| 소비자 (위치) | 읽는 것 |
|---|---|
| `DashDesignVariableModel` (`:314-353`) | `boolean` 인 엔트리 전량 → DV 표 · DOE 후보 |
| `DashDoeConfigManager` (`:217`·`:238`) | `spec.label`(= dvKey) → **DOE 열 헤더** |
| `DashMorphingDoeExecutor` (`:186-198`) | `DV-Condition` 맵 로드 → 헤더 해석용 |
| ㄴ 주입/적용/원복 (`:512`·`:441`·`:496`) | 헤더와 dvKey 대조해 샘플에 부착(`boolean` 아니면 제외 `:526`) → uuid 로 조건명 역조회 후 `editFeConditionEntry` → 주입 전 값 역순 복원 |
| ㄴ 조건 전용 경로 (`:950`) | 모핑 DV 없이 조건 DV 만으로 export |
| `DashAnalysisLauncher` (`:1243-1278`) | `source` → 참조 파일 수집(`.dat`/`.inp`/`.bdf`/`.dfsxml`/`.stli`) |
| `DashDataProcessor` (`:2879`) | `meta` → DOE 테이블 min/max 오버라이드 |
| `DashModelRunner` (`:1546-1563`) | 첫 유효 `source` → `inputFileName` 결정 |

DOE 실행 중의 계약은 **주입 → export → 원복**이고, 배치는 자기 세션을 열지 않고 레지스트리가 GUI 에 물려 준 컨텍스트를 그대로 쓴다.

```
ExecuteOneSample                                   DoeExecutor:905-930
  ├─ rwApplyConditionDvs(sample["DV-Condition"], ctx, runKey)      :441
  │     ├─ uuid → getFeConditionNameByUuid, 실패 시 키를 조건명으로 폴백  :453-456
  │     ├─ param 이 비면 (레거시 엔트리) 경고 후 skip                     :457-461  → D12
  │     ├─ (entryPtr, param) 으로 현재 값 채집, 조합 없으면 skip           :463-478
  │     ├─ editFeConditionEntry(...) — 실패해도 경고 후 skip              :483-487
  │     └─ 적용분을 {condName, entryPtr, param, original} 로 반환          :488
  ├─ updateMeshPoints (모핑 경로일 때만):909-916 · exportSolverInput:921
  └─ 메시 원복 + rwRestoreConditionDvs(applied, ctx)                     :927-930 → :496
```

`rwRestoreConditionDvs` 는 실패해도 경고만 남긴다. 소스 주석(`:493-495`)이 귀결을 적어 둔다 — 원복 실패 시 GUI 세션에 주입값이 남아 화면 표시와 이후 샘플 export 가 오염되고, 배치가 자기 세션을 여는 구조로 가면 되돌릴 것 자체가 없어진다. `:893-899` 주석은 지금 레이스가 아닌 이유가 "이 경로가 GUI 스레드에서 돌기 때문일 뿐" 이라고 못박는다. → D6

조건 전용 경로(`:950-1002`)도 같은 주입·원복 쌍과 같은 위험을 공유한다(`:980-982` 주석). 두 경로 모두 **export 실패만** 샘플을 `Failed` 로 만든다(`:932-939`·`:991-998`). → D12

`DashResultsAnalyzerWidget` 의 조건 DV 경로는 `view/DashResultsAnalyzerWidget.cpp:832` 에서 `paramObj["checked"]` 를 본다. → D13

---

## 6. 상태 소유 지도

| 상태 | 1차 보관 | 병행 보관 | 저장 시 읽는 곳 |
|---|---|---|---|
| FE 조건 값 | RW 모듈 내부 (deck) | `ParameterRow::value` · 표 셀 텍스트 | deck (export 시) |
| 편집 스키마 | RW 모듈 | `RwSession::editSchemaCache` | — |
| 조건 shape | RW 모듈 payload | `feConditionShapeCache` · 렌더 레이어 | — |
| 심볼 uuid | RW 모듈 (content uuid 유도) | `feConditionUuids` · `AnalysisModelIdentity.json` | DV JSON `uuid` |
| 체크 상태 | `ParameterRow::isChecked` | 표 col 0 아이템 `checkState` | DV JSON `boolean` |
| DV 범위 | DV JSON `meta.min/max` | `DvModel::m_variables` | DV JSON (편집 즉시) |
| 대상 deck 경로 | `Registry::m_activeFilePath` | `ParameterRow::source` · `Model::m_loadedFilePath` | DV JSON `source` |
| 하이라이트 대상 | `Widget::m_highlightedCondition` | 렌더링 매니저 레이어 | — |
| 설정 JSON 경로 | `Model::m_settingsJsonPath` | 워처 등록 목록 | — |

체크 상태가 표 아이템과 모델 양쪽에 있고 둘을 맞추는 시점이 **[Set Design Variable] 을 누를 때 한 번**이라는 것이 이 지도의 핵심이다(`Widget:483-490`). 버튼을 누르지 않고 모듈을 떠나면 표에서 만진 체크는 모델에 반영되지 않는다.

---

## 7. 결함 목록

3\~6절 서술 중 동작이 의도와 어긋나거나 어긋날 수 있는 지점 16건 — `D` 잘못 구현된 것 13건, `U` 구현되지 않은 것 3건. ID 는 3절 등장 순서, 우선순위 판정은 하지 않는다. 9개 모듈 교차 색인은 [Cross-Module-Defect-Index](Cross-Module-Defect-Index.md).

`U1`\~`U5` 는 2026-08-29 에 일괄 제거됐다. 예정 작업 2건은 제외를 유지한다 — `isDvCheckable` 이 `Continuous` 만 통과시키는 것은 헤더가 근거를 적어 둔 의도된 정책이고(3-2), `DashRwActor` 의 스레드 이주는 헤더가 블로커까지 적어 둔 착수 대기다(4절, 그 미이주가 낳는 결함은 D6 가 보유). 예정 작업이 아닌 3건은 아래에 `U1`·`U3`·`U5` 로 복원했다 (번호는 원판을 유지).

| ID | 분류 | 결함 | 좌표 | 근거와 귀결 |
|---|---|---|---|---|
| **D1** | 구조·결합 | `setProjectDirectory` 가 인자를 쓰지 않는다 | 3-1 | `Model:29-33` 이 경로를 `getConfigFilePath` 로 재유도한다. 호출 3곳이 서로 다른 값을 넘겨도 결과가 같다 → 시그니처가 약속한 계약과 달라, 인자를 신뢰한 호출이 추가되면 조용히 무시된다 |
| **D2** | 실행 모델 | `getOrLoad` 의 로드가 뮤텍스 밖에서 일어난다 | 3-2 | 조회(`Registry:25-32`)와 삽입(`:41-47`)만 락을 잡고 로드(`:34-39`)는 락 밖 → 같은 미캐시 deck 을 둘이 동시에 요청하면 파싱이 두 번 돌고 하나는 버려진다. 호출처 10곳(`DashManager.cpp:1028` 외)이 전부 GUI 스레드라 현재는 안 나지만, 뮤텍스를 둔 의도 자체가 그 전제를 부정한다 |
| **D3** | 진입·수명 | `m_params` 가 한 번도 clear 되지 않는다 | 3-2 | 사라진 (entryPtr\|param) 조합만 제거하고(`:141-149`) 배열을 비우지 않는다. 다중 deck 누적은 의도된 설계지만(`PM:67`) 세션 안에서 정리하는 경로가 없다 → 어느 deck 의 행인지는 `source` 열로만 구분된다 |
| **D4** | 데이터 정본 | `.ui` 의 열 선언이 모델과 드리프트했다 | 3-3 | `.ui` 5열 vs 모델 7열(`Model:88`). `setColumnCount`(`Widget:399`)가 매번 덮어써 증상은 없지만 디자이너에서 열을 고치는 편집이 무효다 |
| **D5** | 데이터 정본 | Value 인라인 편집이 어느 저장 경로에도 남지 않는다 | 3-5·3-8 | `commitEntryValue:339-379` 는 메모리 deck 만 바꾸고 설정 JSON 에 대응 키가 없다. 되돌리기도 없다 → 모듈을 떠났다 오면 편집이 사라지고, 그 값에서 유도된 `meta.default`·`min/max` 만 파일에 남는다 |
| **D6** | 실행 모델 | GUI 편집과 DOE 배치가 같은 세션을 공유하는데 상호 배제가 없다 | 3-5·5절 | 배치가 레지스트리 컨텍스트를 그대로 쓰며 샘플마다 주입·원복하는데(`DoeExecutor:905`·`:930`) 원복 실패는 경고뿐이라(`:503-506`) GUI 세션에 주입값이 남아 화면과 이후 샘플 export 가 오염된다. GUI 쪽 게이트도 없고, `:893-899` 주석이 지금 레이스가 아닌 이유는 GUI 스레드 실행뿐이라고 명시한다 |
| **D7** | 진입·수명 | 첫 진입에서 체크 상태가 복원되지 않는다 | 3-6·3-8 | `loadFromJson` 호출처 둘(`:53`·`:82`)이 행을 만드는 `refreshFromLoadedAnalysis` 보다 먼저 돈다 → **최초 진입에서 FE 탭 체크가 전부 해제돼 보인다.** DV-Condition 탭에는 변수가 그대로라 어긋난 상태이고, 그대로 [Set Design Variable] 을 누르면 절 전량 재기록(`PM:133-140`)이 `DV-Condition` 을 빈 객체로 덮는다 |
| **D8** | 구조·결합 | DV 섹션 판정이 파일명 부분 문자열이다 | 3-7 | `DvModel:288-297`·`:410-417` 이 파일명의 `"Condition"` 포함 여부로 절을 가르고 매칭 실패는 조용히 `DV-Condition` 으로 간다 → 파일명 규약이 바뀌면 잘못된 절에 기록되고 경고가 없다 |
| **D9** | 실행 모델 | 자기 쓰기 억제 플래그가 실효 없다 | 3-7 | 이벤트 루프 복귀 전에 플래그를 되돌리고(`:532`) 다음 줄의 모달 `QMessageBox`(`:535`)가 중첩 루프를 돌린다 → 방금 쓴 파일의 `fileChanged` 가 그 안에서 배달돼 리로드가 한 번 더 돈다. 결과가 같아 무해하지만 의도한 억제는 일어나지 않는다 |
| **D10** | 진입·수명 | 대상 deck 이 어느 저장 경로에도 기록되지 않는다 | 3-8 | 대상은 `Registry::m_activeFilePath` 전역 1개이고 Set 별 필드가 없다. `source` 는 승격된 DV 가 있을 때만 남는다 → 프로젝트를 재로드하면 사용자가 deck 을 다시 열어야 표가 채워진다 |
| **D11** | 실행 모델 | `get_symbol_detail` 이 캐시되지 않는다 | 4절 | `getFeConditionTypeString`(`:549`)·`getFeConditionSetName`(`:572`)·`getFeConditionEntries`(`:639`)가 각각 `rwSymbolDetailJson`(`:357`)을 호출하고 `editFeConditionEntry` 가 검증용으로 1회 더 부른다(`:798`) → 표 1회 구축에 조건당 최소 3회 왕복 |
| **D12** | 데이터 정본 | 조건 DV 주입 실패가 조용한 skip 이다 | 5절 | 실패 3종이 전부 `continue` 다 — `param` 없음(`:457-461`)·조합 없음(`:474-478`)·편집 실패(`:483-487`). 샘플을 `Failed` 로 만드는 것은 export 실패뿐이라(`:932-939`·`:991-998`) 조건 DV 가 하나도 적용되지 않아도 기준값 그대로 export 되고 성공으로 집계된다 |
| **D13** | 데이터 정본 | ResultsAnalyzer 의 조건 DV 수집이 없는 키를 읽는다 | 5절 | `DashResultsAnalyzerWidget.cpp:832` 가 보는 `paramObj["checked"]` 는 레포 전체에서 그 한 줄에만 존재한다 — 쓰는 코드가 없다. 실제 키는 `"boolean"` → 조건 DV 는 그 변수 목록에 절대 들어가지 않는다 |
| **U1** | 미구현 | `setModel` 오버로드의 유일한 호출 인자가 항상 `nullptr` | 3-1 | `setModel(DashConditionParameterization*)`(`Widget:319`)은 `dataChanged → updateUI` 와 `dataLoaded → onModelDataLoaded` 를 잇는 유일한 지점(`:339-342`)인데 호출처가 Set 삭제 경로(`DashMainWindow.cpp:750`) 하나이고 인자가 항상 `nullptr` 이라 `:330` 가드가 연결 블록을 건너뛴다 → 실운영에서 `dataLoaded`(`Model:516`) 수신처가 0곳이다 |
| **U3** | 미구현 | 디렉토리 워처의 `directoryChanged` 연결이 0곳 | 3-7 | `updateDvWatchers:580-587` 이 userPath 디렉토리를 감시 목록에 넣지만 `directoryChanged` 는 레포 전체에서 **한 번도 나오지 않는다** → `onDvJsonChanged` 의 `else` 분기(`:627-636`)와 `onDirChanged`(`:653`)가 도달 불가다 |
| **U5** | 미구현 | 자동 회귀 보호가 없다 | 4절 | `tests/` 전체에 `ConditionParameterization`·`DashRwSession`·`DashRwActor`·`DashRwClient`·`DashDvKind` 참조 0건 → 액터 마샬링 · 엔트리 분해 3갈래 · dvKey 채번 · gen1\~gen4 바인딩 · DOE 주입·원복이 전부 자동 검증 밖이다 |

런타임 미확인 3건 — D7 의 실제 화면 체감(호출 순서는 코드로 확정, 프로젝트 로드 경로의 `loadFromJson` 실행 횟수 미확인) · D11 의 조건당 지연(왕복 횟수는 확정, `DASH_RW_FE_DIAG=1` 의 `diagnoseFeConditionPayloads`(`RwSession:1237`)가 측정용) · 하이라이트의 실제 렌더 결과(모듈이 FECondition payload 를 내주는지는 덱·모듈 버전에 달렸다).

---
