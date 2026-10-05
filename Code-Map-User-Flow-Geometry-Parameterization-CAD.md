# Geometry Parameterization (CAD) — 사용자 플로우 ↔ 코드 대응

> **성격**: 독립 참조 문서. CAD 경로에서 사용자 행위 하나하나가 밟는 함수 체인의 대응표 — 수정 계획·우선순위는 담지 않는다.
> **좌표 기준**: GUI 는 `DashOpti_GUI` `dev` @ `ac6e4e6`, 데몬은 `DashOpti_CadNx` `main` @ `d71a17d` 실측(유효기간 있음).
> **검증 수준**: 정적 코드 근거만 — 양쪽 저장소 전문 확인. 빌드·실행 검증 없음(NX 설치 환경 필요).
> **분리 원칙**: 3\~6절은 코드가 하는 일만 적고 판정은 7절에 모았다. 본문 `→ D{n}` 이 링크다.

## 개요

CAD 경로는 탭 4면과 로직 클래스 7종이 외부 NX 프로세스 하나를 stdin/stdout 라인 텍스트로 부리는 구조다. Morphing 과 달리 형상을 만질 수단이 GUI 안에 없다 — 파라미터 값을 표에 모아 데몬에 보내고 돌려받은 STEP 을 렌더할 뿐이다. 데몬은 별도 저장소(`DashOpti_CadNx`)의 342줄 Python CLI 를 PyInstaller 로 묶은 `DashOptiCADNX.exe` 이며 NXOpen 으로 NX 세션을 직접 잡는다.

왕복은 둘로 갈린다 — **명령 왕복**(`.prt` 등록·프리뷰)은 비동기 큐를 타고, **값 편집**은 전부 GUI 안에서 동기로 끝난다. 둘이 만나는 지점이 [Set Design Variable] 한 번이고 그것이 이 모듈의 유일한 영속화 지점이다. 여러 단계에 걸치는 데몬 프로토콜(4절)·산출 파일(5절)은 따로 뺐다.

---

## 1. 탭 4면과 소유 클래스

`ui/DashGeometryParameterCADWidget.ui` 는 탭 4개를 정의하지만 가운데 둘은 **착수 예정 기능의 자리표시자**다 — UI 만 먼저 뚫어 두고 로직은 이후 작업으로 남겼다. 릴리스 빌드는 위젯 생성 시점에 두 탭을 런타임 제거·삭제한다(`view/DashGeometryParameterCADWidget.cpp:143-148`).

| 탭 | 릴리스 노출 | 로직 | 종결 액션 |
|---|:---:|---|---|
| **CAD Parameter** | O | Independent 편집 · Dependent 열람 · 프리뷰 요청 | Apply · Lower/Upper Preview |
| Match NSET | **X** (`DASH_BUILD_DEV` 만) | 예정 — Reference NSET 표는 `.ui` 하드코딩 더미 2행 | (▼ · Clear — 미배선) |
| **DV-Geometry** | O | 전역 공유 DV 모델 바인딩 · 인테이블 편집 | Set Design Variable |

Meshing 은 더 이상 탭이 아니다 — `b791b10` 이 `.ui` 에서 탭을 걷어내고 `DashMeshingDialog`(`view/dialog/`)로 분리해, DEV 빌드에서 `mMeshingButton` → `onMeshingButtonClicked:827` 로 배선했다(`:297-299`). 릴리스는 버튼·다이얼로그 전체가 컴파일되지 않는다.

`DASH_BUILD_DEV` 는 `CMakeLists.txt:99-101` 의 `BUILD_Dev` 에서만 켜지고 사용처는 이 파일과 `view/analyzer/DashPlotWidgetFactory.cpp:1013`·`:1017` 뿐이다. 실동선은 **CAD Parameter → DV-Geometry** 2탭이며, `.ui` 의 `<connections/>`(`:409`)가 비어 auto-connect 는 0건이다.

| 로직 클래스 (소스 줄) | 담당 |
|---|---|
| `DashGeometryParameterCADWidget` (846) | 표 2종 채우기 · 프리뷰 요청 · **DV 승격 본체** |
| `DashGeometryParameterCAD` (`model/`, 435) | 파라미터 보관(`QAbstractTableModel`) · JSON 왕복 |
| `…CADPresentationModel` (`viewmodel/`, 86) | DV-Geometry JSON 규칙 · 프리뷰 STP 경로 규칙 |
| `DashSolverNxCad` (`controller/`, 270) | NX 데몬 파사드 — 명령 조립·응답 해석 |
| `DashExtensionProcess` (`controller/`, 482) | 데몬 수명·직렬 명령 큐 (CAD 전용 아님) |
| `DashMainWindow` (3,636) | `.prt` 진입 · 완료 통지 수신 · 트리/뷰 갱신 |
| `DashOcctViewWidget` (508) | STEP 최종 소비자 (`STEPControl_Reader`, `:192`) |

계층 배치의 특징 둘이 이후 절에서 반복된다 — **위젯은 OCCT 뷰를 직접 참조하지 않는다**(CAD 위젯 소스에 OCCT 심볼 0건. 요청은 위젯, 렌더는 `DashMainWindow`). **DV 승격 로직이 모델이 아니라 뷰에 있다**(`syncDvFromCheckedCadParameters` 는 위젯 `:561-644`, 모델의 `saveSettings()`(`Model:117-120`)는 `qDebug` 한 줄 no-op).

---

## 2. 전체 동선

```
1. 사전 조건  Solver Settings 에 NX 루트 입력 → [Set]
             ※ 기동은 비동기. 경로가 비면 무동작, 이후 명령이 오면 lazy 기동
2. .prt 등록  Project Tree 행 Load → 사전조건 3종 검사 → loadPrt 큐잉
             ※ 명령 하나가 산출물 둘로 갈리고 서로 다른 통지로 도착한다
                · 파라미터 JSON → CAD Parameter 탭 표 2종
                · STEP         → Modeling Tree "Original" + OCCT 뷰
3. Set 선택   저장 JSON 복원 → 세션 캐시 재적용 → 전역 공유 DV 모델 바인딩
             ※ 활성 해석파일 컨텍스트는 로드되지만 표에 반영되지 않는다
4. 값 편집    Independent 행 체크 · Lower/Upper 스핀박스 · [Apply] 오프셋 일괄 가산
             ※ Dependent 표는 전 열 읽기 전용 (NX 수식 파라미터 열람용)
5. 형상 확인  [Lower/Upper Preview] → config JSON 조립 → updatePrtGeometry 큐잉
             ※ 두 버튼은 배타가 아니고, 왕복 없이 바로 7 로 가도 된다
6. (예정)     메시 생성 · NSET 매칭 — 릴리스에 탭 없음, DEV 에서도 connect 없음
             현재 메싱은 DOE 실행 시점의 GUI 밖 ANSYS Workbench Journal 이 수행
7. DV 승격    [Set Design Variable] → 체크 상태 이름 매칭 역동기화
             → DV-Geometry 기록 → 공유 DV 모델 재로드 → 마지막 .prt 를 configs 로 복사

[산출] configs/GeometryParameter_Set{N}-CAD.json + 같은 폴더의 .prt 복사본
       하류(DOE·Optimizer·Model Runner)가 이 둘로 케이스별 STEP 을 만들고,
       ANSYS Journal 이 파일명 규약으로 그 STEP 을 집어간다
```

---

## 3. 단계별 대응

### 3-1. 사전 조건 — NX 경로와 데몬 기동

| 사용자 행위 | 코드 |
|---|---|
| Solver Settings 에 NX 루트 입력 후 [Set] | `view/dialog/SolverSettingsDialog.cpp:132` 저장 → `:138` `DashManager::tryStartNxCadDaemon()`(`DashManager.cpp:146-150`) |
| (자동) 기동 시도 | `tryStartIfConfigured:114-124` — `getSolverPath("NX")` 가 비면 **무동작 return** |
| (자동) exe 경로 해석 | `resolveExePath:41-75` — `<NX>/NXBIN/python/python3*.dll` 의 버전 태그로 `extensions/cad_nx_py<tag>/DashOptiCADNX.exe` 조립 |
| (자동) 환경 구성 | `setupEnvironment:77-104` — `UGII_BASE_DIR` · `PATH` 앞단 4종 · `PYTHONPATH` |

기동은 이 경로 말고도 `enqueueLoadPrt`/`enqueueUpdatePrtGeometry` 진입부(`:128-130`·`:151-153`)와 `sendCommand`(`ExtensionProcess:326-327`)에서 lazy 로 걸린다. 명령이 큐에 흡수되므로 호출부는 ready 를 기다리지 않는다. ready 타임아웃은 NX 만 **120초**로 재정의돼 있다(`SolverNxCad:16`, 기반 클래스 기본 30초).

남는 상태는 `m_nxBaseDir` 와 `Starting`/`Ready` 로 전이한 프로세스 상태다. 성공·실패는 반환값이 아니라 `ready()`/`died()` 시그널로만 온다(`:26-31`).

### 3-2. `.prt` 등록 — 한 명령, 두 산출물

진입은 CAD 위젯이 아니라 `DashMainWindow` 다. Project Tree 행의 델리게이트 Load 버튼 → `ProjectFileTreeDelegate::editorEvent:160-181` → `loadButtonClicked(index)` → `DashMainWindow.cpp:331` → `onProjectFileLoadClicked:2121`.

| 코드 | 내용 |
|---|---|
| `:2154-2155` | `startProjectLoadStatusAnimation()` + `processEvents(ExcludeUserInputEvents)` → D1 · D2 |
| `:2157-2179` | 사전조건 3종 — 프로젝트 열림 / NX 경로 / 파사드 존재. 각각 모달 warning 후 return. **ready 판정은 하지 않는다**(주석 `:2177-2178`) |
| `:2187-2244` | 기존 렌더 정리 — active actor 제거 · 레이어 3종 clear · Modeling Tree 비우기 |
| `:2269-2278` | 출력 STEP 을 `{configs}/{prtBase}.stp` 로 정하고 `enqueueLoadPrt(prt, stp)` |
| `SolverNxCad:132-138` | **이전 세션 프리뷰 STP 를 temp 에서 일괄 삭제**(`*_lower_preview*.stp`·`*_upper_preview*.stp`) |
| `:142-145` | stdin 한 줄 `loadPrt "<prt>" "<stp>"`, `commandId = "loadPrt:<stp>"` |

```
데몬 stdout → handleDaemonLine:384 → emit outputLine(line):386   ← 상태 무관, 모든 라인
   ├─ JSON 라인 → tryParseJsonFromLine  SolverNxCad:242-261 → nxCadParametersJson(obj)
   │     → 위젯 :77-82 (생성자에서 상시 구독)
   │          ├─ DashManager::setLastNxCadParameterJson(obj)   세션 캐시
   │          └─ mModel->applyNxCadParameterJson(obj)          Model:295-374
   │               m_params ← "Independent Parameter" (:298-340)
   │               m_dependentParams ← "Dependent Parameter" (:342-370)
   │               emit dataLoaded():373 → 표 2종 재구축
   └─ "[FINISHED]" → onCommandCompleted:187-207 → 존재 검사(:192-196)
         → loadPrtCompleted(stp) → onNxLoadPrtStepReady:2300-2319
              addStepChildToTree(stp, "Original") · loadStepFile(stp)
```

**파라미터 표와 3D 형상이 서로 다른 통지로 도착한다.** `outputLine` 은 명령 수명과 무관하게 라인마다 방출되고(`:386`, `m_waitingFinished` 검사 이전) `[FINISHED]` 는 별개 채널이다. 파사드는 `{` 로 시작하는 라인부터 파싱 성공까지 버퍼를 누적한다(상한 2,000,000자, `:258`). → D3 남는 상태 셋 — `m_originalPrtPath` · `m_lastLoadedStpPath`(파사드) · `DashManager::m_lastNxCadParameterJson`(싱글턴 세션 캐시).

### 3-3. Set 선택 — 모델 바인딩

`handleGeometryParameterSelection:1088-1113` 이 `Qt::UserRole+2` 플래그 또는 이름 `-CAD` 접미로 CAD 갈래를 판정한다(`:1092`). [Add Set] → "for CAD" 는 `DashProject::createNewSet:679` 의 `:686-689` 가 `Set{N}-CAD` 로 채번하고 `{"variant":"CAD"}` 스켈레톤을 만든다(`createModuleJsonFile:584-608`).

```
handleGeometryParameterSelection                 DashMainWindow.cpp:1088
  ├─ paramCAD->setProjectDirectory(configsDir)   :1107 → Model:18-43 → :42 loadFromJson():376-435
  │     ├─ Independent/Dependent 키 있으면 applyNxCadParameterJson(root)  Model:403-405
  │     ├─ DV-Geometry 의 boolean==true 로 체크 상태 복원                  :407-430
  │     └─ emit dataLoaded()                                              :433
  └─ widget->setModel(paramCAD, m_projectPath)   :1109 → 위젯 :307-353 (mModel = cast :315)
        ├─ setProjectDirectory(...) → loadFromJson() **2회차**   :317-323
        ├─ lastNxCadParameterJson() 이 비지 않으면 재적용        :324-327   → D4
        ├─ 전역 공유 DashDesignVariableModel 을 DV 탭에 바인딩   :330-342
        │     └─ dataChanged → onSharedDvModelEdited (UniqueConnection)
        ├─ updateDvWatchers() · setupConnections() · onModelDataLoaded()  :345-347
        └─ 활성 해석파일이 있으면 refreshFromFile(activeFilePath)         :349-352
```

`setProjectDirectory()` 가 두 번 불려 `loadFromJson()` 도 두 번 돌지만(`:1107`·위젯 `:321`) 둘 다 시그널 연결(`:346`) 이전이라 표 재구축으로 이어지지는 않는다. 표에 행이 유입되는 경로는 둘이고 둘 다 같은 `applyNxCadParameterJson` 을 거친다 — 저장 JSON(`loadFromJson:403-405`, 이전 세션의 이름·파트·Lower/Upper)과 데몬 JSON(위젯 `:77-82`·`:324-327`, NX PRT 표현식 파라미터).

세 번째 경로였던 해석 덱 유입은 아무것도 만들지 않는다 — 위젯 `refreshFromFile:412-424` → `Model::refreshFromLoadedAnalysis:102-115` 가 `getOrLoad(filePath)`(`:106`) 후 `m_loadedFilePath` 만 적고 `true` 를 돌려주는데(`:112-114`), 읽는 쪽 `getContext():97-100`·`getLoadedFilePath()`(`Model.h:44`)는 호출처가 0이다. CAD 모델이 RW 계층에 닿는 지점은 이 체인뿐이며 RW 의 메시 API 는 Morphing 전용이다. → D5

남는 상태 — `m_params` · `m_dependentParams` · `m_settingsJsonPath` · `m_loadedFilePath` · 공유 DV 모델 바인딩 · 파일 워처 2종(설정 JSON + user 디렉터리, 위젯 `:680-708`).

### 3-4. CAD Parameter 탭 — 값 편집

Independent 표는 5열(`""` · Name · Part · Lower · Upper, `Model:77`)이고 Part(2열)는 숨김(위젯 `:451`). Lower(3열)·Upper(4열)는 `QDoubleSpinBox` 셀 위젯, 나머지는 `ItemIsEditable` 을 뗀 아이템이다(`:464-493`).

| 사용자 행위 | 코드 |
|---|---|
| 개별 Lower/Upper 입력 | 셀 스핀박스 `valueChanged`(`:483-485`) → `updateParameterValueFromSpinBox:774-780` → `Model::setIndependentParameterBounds:207-221` |
| 행 체크 | 0열 `checkState` → `itemChanged`(`:239-243`) → `updateCadTableHeaderCheckBoxState:831-846` 로 헤더 tristate 재계산. **모델 반영은 승격 시점 한 번** |
| 헤더 체크박스 전체 토글 | `:228-237` — `QSignalBlocker` 억제 후 전 행 `setCheckState` |
| [Apply] 오프셋 일괄 가산 | `onCadApplyAddValues:811-829` — 체크 행 스핀박스에 가산, 각 스핀박스가 위 경로를 다시 발화 |
| 열 정렬 | `:496` `sortItems(1, Ascending)` — 채우기 직후 1회, 이후 헤더 클릭마다 |

정렬이 개입할 때 행을 짚는 방식이 경로마다 다르다 — 체크 역동기화(`:568-579`)·`defaultText` 조회(`:668-673`)는 **이름 매칭**, 범위값 수집(`:660-665`)·[Apply](`:818-828`)는 **시각 행 인덱스**, 스핀박스 람다는 **채우기 시점 캡처 모델 행**(`:483`). 셋이 같은 행을 가리킨다는 보장이 코드에 없다. → D6

Dependent 표(`:511-559`)는 Name·Part·Value 3열 전부 read-only 이고 Part 는 숨김(`:541`). 채워지는 곳이 `applyNxCadParameterJson()` 하나뿐이라 GUI 편집 경로가 없다 — NX 수식 파라미터(예: `L_total = d*12`) 확인용이다.

남는 상태는 `m_params[].lower/upper` 와 셀 스핀박스 값 두 벌이다. 체크 상태는 이 단계에서 표에만 있고 모델에는 없다.

### 3-5. Lower / Upper 프리뷰

```
[Upper/Lower Preview] → 위젯 :801-809 → enqueuePreview(useUpperValue)  :782-799
   · lastLoadedPrtPath() 가 비면 모달 warning "Load a PRT file first."  (:793)
   · 출력 = PM::previewStpPath(base, useUpper)                          (PM:80-86)
       {temp}/{prtBase}_{upper|lower}_preview_{seq}.stp   ← seq 는 프로세스 전역 static
   · payload = mModel->toNxCadConfigJson(useUpperValue)                 (Model:223-245)
       Independent 4배열만 — Value 에 upper 또는 lower
   ▼ :798 enqueueUpdatePrtGeometry(prt, stp, config)
stdin: updatePrtGeometry "<prt>" "<stp>" --config-json "<이중 이스케이프>" --no-cleanup
   commandId = "updatePrt:<stp>" (SolverNxCad:159-164) · 전송 직전 출력 STP 선삭제 (:346-347)
   ▼ "[FINISHED]" → onCommandCompleted:187-207 → 존재 검사(:192) → m_batchMode==false
   ▼ emit updatePrtGeometryCompleted(stp) (:205)
DashMainWindow.cpp:277-280   ← 요청자가 아니라 메인윈도가 받는다
   stopNxCadStatusAnimation() → onNxPreviewStepReady:2343-2348 → previewStepFile:2321-2341
      addStepChildToTree(stp, "Upper|Lower Preview")  ← 경로 문자열로 라벨 판정 (:2324-2329)
      m_occtViewWidget->loadStepFile(stp)
```

관찰 셋 — **요청자와 수신자가 다르다**(완료 시그널은 경로를 싣지만(`:205`) 실패는 싣지 않는다. `onCommandFailed:209-212` 가 `commandId` 를 동사 판별에만 쓰고 `emitFailure(bool, message)`(`:218-225`)에 경로 인자가 없다 → D7). **방출 대상이 전역 1비트로 갈린다**(`m_batchMode`, `DashSolverNxCad.h:68` → `:200-206`·`:220-224` → D8). **스피너가 비대칭이다**(프리뷰는 `stopNxCadStatusAnimation()` 만 부르고 시작 호출이 없다 → D9).

두 버튼은 토글이 아니라 단발 push 다. 누를 때마다 seq 가 증가한 새 STP 가 temp 에 쌓이고 정리는 다음 `loadPrt` 때만 일어난다(`SolverNxCad:132-138`).

### 3-6. 예정 단계 — Meshing · Match NSET

Meshing 은 `b791b10` 으로 탭에서 다이얼로그로 옮겨졌다 — `.ui` 에 탭이 없고 DEV 빌드의 `mMeshingButton` 이 `DashMeshingDialog` 를 띄운다(`:297-299`·`:827-830`). Match NSET 은 여전히 탭이며 릴리스는 위젯 생성 시점에 제거·삭제하고(`:137-138`) DEV 는 포인터 별칭만 잡는다(`:128-135`) — `mReferenceNsetTable`·`mMatchNsetDoneButton` 등 `connect` 0건이다.

**Match NSET 은 착수를 앞두고 UI 만 먼저 뚫어 둔 자리표시자다** — 헤더가 `"UI only, logic not yet implemented"` 로 적어 뒀고 `#ifdef` 로 릴리스에서 지우는 것도 미완성 UI 노출을 막기 위한 장치다. 결함이 아니라 예정 작업이다.

현재 메싱은 사라진 것이 아니라 위치가 GUI 밖이다 — DOE 실행 시 GUI 는 샘플별 STEP 까지만 만들고 ANSYS Workbench Journal 이 재메싱·해석한다. Meshing 다이얼로그가 실동선에 붙으면 이 경계가 GUI 안으로 옮겨온다. NSET 매칭이 풀어야 할 문제는 따로다 — **CAD 는 형상 재생성 → 재메싱이라 원본 해석 덱의 노드 인덱스 집합이 무효화된다.** 노드 번호가 보존되는 Morphing 과 달리 기준 NSET 을 새 메시에 다시 붙일 수단이 현재 없다.

### 3-7. 설계변수 승격

`Set Design Variable` 한 번이 이 모듈의 유일한 영속화 지점이다. 이 버튼 밖에서 파일에 기록되는 것은 DV-Geometry 탭 인테이블 편집(`onSharedDvModelEdited:760-772`)뿐이다.

```
[Set Design Variable] → syncDvFromCheckedCadParameters   위젯:561-644
   ├─ 표 체크 → 모델 역동기화. **이름 매칭**으로 정렬된 행 방어     :568-579
   ├─ mModel->getCheckedParameters()                    Model:196-205  :581
   ├─ collectCadDvRows(checkedNames)                    위젯:646-678
   │     ├─ name/part = 표 아이템 (시각 행)                   :651-657
   │     ├─ lower/upperBound = **셀 스핀박스에서 직접**        :660-665  → D12
   │     └─ defaultText = 모델 3열(=lower) 을 이름 매칭으로    :668-673  → D10
   ├─ m_blockDvWatcher = true — 파일 워처 재진입 차단          :595
   ├─ PM::saveDvGeometry(jsonPath, rows, toSettingsJsonObject())      :597
   │     ├─ buildDvGeometryJson  PM:14-42 — source "CAD"|"CAD|{part}", type "continuous"
   │     │     하드코딩, meta {default,min,max}, boolean = row.checked (**미체크 행도 기록**)
   │     ├─ mergeSettingsRoot    PM:44-53 — variant "CAD" 강제 + Independent/Dependent 동봉
   │     └─ 기존 JSON read → merge → Truncate write     PM:55-78
   ├─ 공유 DashDesignVariableModel::loadFromJsons({fileName}, configsDir)  :610-621
   │     └─ boolean==true 만 DV 채택 → DV-Geometry 탭 reset
   ├─ NX 가 마지막에 로드한 .prt 를 configs/ 로 복사 — DOE 재현용         :626-641
   └─ 모달 QMessageBox::information("Success", …)                       :643
```

저장값 출처가 두 갈래다 — 범위값은 **셀 스핀박스**, `meta.default` 는 **모델 3열**. 3열은 `Model::data:153` 이 `param.lower` 를 돌려주는 열이라 `meta.default` 에 현재값이 아니라 Lower 가 들어간다. PM 헤더 주석은 그 자리를 `// current model value as text` 로 적어 뒀고(`PM.h:24`), 원본 현재값 `CADParameterRow::value` 는 DV JSON 에 전달되지 않는다. → D10 그리고 `toSettingsJsonObject:247-293` 이 쓰는 `Independent Parameter.Value` 에는 `p.upper` 가 들어가는데(`:259`), 로드는 같은 키를 "현재값" 으로 읽어 `lower = upper = value` 초기화에 쓰고(`:321-324`) `Lower`/`Upper` 키가 있으면 덮어써 복구한다(`:325-330`). → D11

승격 이후 편집은 둘로 되돌아온다 — DV-Geometry 인테이블 편집(Min/Max/Cases) → `onSharedDvModelEdited:760-772` → `saveToJsonFiles()` 즉시 영속화 · 파일 외부 변경 → `fileChanged` → `onDvJsonChanged:715-753` → 공유 모델 재로드 + 뷰 reset. 모델 쪽 저장 경로는 없다(`saveSettings()`(`Model:117-120`)는 `qDebug` 한 줄, 호출처 0).

### 3-8. 재진입과 복원

| 복원 대상 | 저장처 | 읽는 곳 | 상태 |
|---|---|---|---|
| 파라미터 이름·파트·Lower/Upper | JSON `Independent Parameter` | `loadFromJson:403-405` → `applyNxCadParameterJson:298-340` | 복원됨 |
| Dependent 파라미터 | JSON `Dependent Parameter` | 같은 경로 `:342-370` | 복원됨 |
| 승격된 DV (min/max/boolean/source) | JSON `DV-Geometry` | 공유 `DashDesignVariableModel::loadFromJsons` | 복원됨 |
| DV 체크 상태 | JSON `DV-Geometry.{key}.boolean` | `loadFromJson:407-430` | 세션 캐시가 비었을 때만 → D4 |
| 대상 `.prt` 경로 | `configs/` 복사본 (승격 시에만) | 파사드 `m_originalPrtPath` 는 세션 한정 | 승격 전이면 소실 |
| Set ↔ `.prt` 결합 | — | `.prt` 는 프로젝트 전역 1개, Set 별 필드 없음 | 없음 |

Set 을 **삭제**하면 `onDeleteSetRequested:659` 가 `setModel(nullptr, QString())` 을 걸지만(`:677`) 위젯 `:311-313` 의 `if (!model) return;` 이 즉시 빠져나가 `mModel` 이 남고, 직후 `DashProject.cpp:790` 이 그 모델에 `deleteLater()` 를 건다. → D13

Set variant 판정은 재오픈 시 `DashProject::detectGeometryVariant:613-645` 가 `variant` 키 → 최상위 `Morphing` 오브젝트 → `DV-Geometry.source` 접두 → Set 이름 `-CAD` 접미 순으로 내려간다.

---

## 4. 데몬 프로토콜

`QProcess` stdin/stdout 라인 텍스트. 프로세스 인자는 `DashOptiCADNX.exe daemon --nx-base <UGII_BASE_DIR>`(`SolverNxCad:121`). 아래 데몬측 좌표는 `DashOpti_CadNx` 기준이다.

### 4-1. 라인 계약

| 방향 | 형식 | GUI 측 판정 | 데몬 측 근거 |
|---|---|---|---|
| GUI → exe | `loadPrt "<prt>" "<stp>"` | — | `main.py:137-214` |
| GUI → exe | `updatePrtGeometry "<prt>" "<stp>" --config-json "<json>" --no-cleanup` | — | `main.py:217-278` |
| GUI → exe | `exit` | 종료 (`ExtensionProcess:191`·`:300`) | `main.py:319-320` — `exit`·`quit` 대소문자 무시. stdin EOF 도 동일(`:301-306`) |
| exe → GUI | `[GUI] NX path (UGII_BASE_DIR): <경로>` | ready 판정 (`SolverNxCad:106-110`) | `main.py:296` |
| exe → GUI | `{...}` JSON 한 줄 | `{` 로 시작하는 라인부터 누적 파싱 (`:242-261`) | `main.py:207` — `json.dumps` 단일 라인 |
| exe → GUI | `[GUI] [SUCCESS] STEP file saved: <abs>` | 로그로 재방출 (`:178-181`) | `export_utils.py:62` |
| exe → GUI | `[GUI] [DEBUG] …` | **로그에서 걸러냄** (`:172-174`) | `main.py:258`·`:260` |
| exe → GUI | `[FINISHED]` | 성공 — 라인 **전체 일치** (`ExtensionProcess:404`) | `main.py:325` |
| exe → GUI | `[GUI] [ERROR] …` | 실패 — `contains` 매칭 (`:415`) | `main.py:327` · `export_utils.py:77` |

**ready 판정은 데몬 로그 한 줄에 고정돼 있다.** GUI 는 `[GUI]` 또는 `UGII_BASE_DIR` 을 포함하는 첫 라인을 ready 로 보고(`:106-110`), 데몬이 stdout 에 처음 쓰는 `main.py:296` 한 줄이 두 조건을 모두 만족한다(`logger` 는 `[GUI] ` 접두를 붙여 stdout 으로 쓰고 레코드마다 flush — `source/utils/logger.py:32-42`). **다만 ready 가 NX 세션 준비를 뜻하지는 않는다** — 기동 시간 대부분은 모듈 임포트 시점의 NXOpen 로드(`main.py:104`·`:110-120`)이고 `Session.GetSession()`(`nx_helpers.py:8-15`)은 첫 명령이 와야 불린다. 타임아웃을 120초로 재정의한 이유가 이 임포트다.

STEP export 실패는 `[ERROR]` 를 **두 줄** 낸다(`export_utils.py:77` 이 찍고 재던지면 `main.py:327` 이 다시 찍음). GUI 는 첫 줄에서 `commandFailed` 를 내고 `m_waitingFinished` 를 내리므로 둘째 줄은 `handleDaemonLine:398` 가드에 걸려 버려진다 — 로그에는 두 줄 다 남는다.

### 4-2. `loadPrt` — 파라미터 추출 규칙

```
loadPrt <prt> <stp>                              main.py:137-214
  ├─ _ensure_step_path — 확장자 없으면 .stp 부착   :125-129
  ├─ get_nx_session / open_part                   nx_helpers.py:8-36
  │     └─ 이미 열린 파트는 경로 정규화 비교로 재사용, SetWork 만   :19-27
  ├─ get_user_expressions(wp)                     nx_helpers.py:47-54
  │     └─ **정규식 `^p\d+.*$` 이름 제외** — NX 자동 생성 p 변수 배제 (:6)
  ├─ 값 파싱으로 2분류                             :162-190
  │     · int/float 파싱 성공 → Independent · 실패(수식 문자열) → Dependent
  ├─ Part = wp.DisplayName ?: wp.Name ?: "A"      :159   ← 전 행이 같은 값
  ├─ Type = "NX CAD" 리터럴                        :184 · :189
  ├─ print(json.dumps(...))                       :207   ← stdout 한 줄
  ├─ export_step(save_before_export=False)        :210
  └─ close_part → _cleanup_temp(step_path)        :213-214   → D15
```

GUI 의 Independent / Dependent 구분이 여기서 정해진다 — **숫자로 평가되면 편집 가능, 수식이면 열람 전용.** 이 JSON 에는 `Lower`/`Upper` 키가 없고(`:192-205`), 그것이 D11 이 말하는 구조다.

### 4-3. `updatePrtGeometry` — 형상 재생성 규칙

```
updatePrtGeometry <prt> <stp> --config-json <json> --no-cleanup   main.py:217-278
  ├─ **"Independent Parameter" 의 Name/Value 만 읽는다**            :238-245
  │     · Part·Type·Dependent 는 무시 · 길이 불일치/빈 Name → RuntimeError :241-244
  ├─ open_part(원본) → SaveAs({stp 와 같은 base}.prt)               :247-259
  │     └─ 이후 작업은 전부 사본에서 — **원본 .prt 는 건드리지 않는다**
  ├─ update_expressions(wp, new_values)          nx_helpers.py:56-62
  │     └─ 이름별 try/except, 실패는 NX ListingWindow 에만 기록      :61-62   → D14
  ├─ update_model — SetUndoMark 후 DoUpdate      nx_helpers.py:67-79
  ├─ save_part → export_step → close_part        :267-273
  ├─ --no-cleanup 이면 temp .prt 를 남긴다        :274-275   → D16
  └─ STEP 부재 시 RuntimeError                    :277-278
```

GUI 는 `--no-cleanup` 을 **항상** 붙인다(`SolverNxCad:159`) — 플래그의 정리 분기는 GUI 경로에서 도달하지 않는다.

| `export_step` (`export_utils.py:13-78`) | 값 |
|---|---|
| 포맷 | **AP214**(`ExportAsOption.Ap214`, `:35`), `ExportFrom = ExistingPart`(`:36`) |
| 대상 | Solids · Surfaces · Curves (`:41-43`) |
| 설정 파일 | `{UGII_BASE_DIR}/step214ug/ugstep214.def` 있으면 적용 (`:45-49`) |
| 선삭제 | 기존 `<out>.stp`·`<out>.log` 를 export 전에 제거 (`:30-31`) |
| 완료 판정 | 존재 **AND 크기 > 500바이트** 를 0.5초 × 30회 = 최대 **15초** 폴링 (`:54-59`) |
| 부산물 | STEP creator 의 `<out>.log` 를 성공 후 삭제 (`:70-74`) |

**출력 STEP 선삭제가 3중이다** — 데몬(`export_utils.py:30`) · 전송 계층(`ExtensionProcess:346-347`) · 배치 오케스트레이터(`DashJobRunner.cpp:2658`). 성공 판정도 2중이며(데몬은 크기까지, GUI 는 존재만 `SolverNxCad:192-196`) GUI 검사는 데몬 검사의 부분집합이다.

### 4-4. 큐와 수명

**동시 in-flight 명령은 항상 1개**다 — GUI 는 `trySendNext:331-354` 가 `m_waitingFinished` 로 직렬화하고, 데몬은 `readline()` 단일 루프라 병렬 실행이 없다(`main.py:299-327`). 응답 라인에 요청 식별자가 없어 파사드는 자신이 보관한 `commandId`(`"loadPrt:<stp>"`/`"updatePrt:<stp>"`)와 **순서로** 짝짓는다. 데몬 루프는 stdin 을 `shlex.split()` 성공까지 누적하지만(`:298-314`) GUI 가 항상 한 줄로 보내 이 분기는 타지 않으며, **명령 실행 중 예외가 나도 루프는 죽지 않는다**(`:323-327` — `[GUI] [ERROR]` 만 찍고 다음 라인 대기).

| 항목 | 값·동작 |
|---|---|
| 기동 | lazy — 명령이 큐를 채우고 `reconcile():132` 이 프로세스를 올린다 |
| ready 타임아웃 | 120,000ms (`SolverNxCad:16`) — NXOpen 임포트 시간을 덮는다 |
| stop 타임아웃 | 5,000ms 후 `kill()` (`ExtensionProcess:24`) |
| 사망 시 | `m_wantUp = false`(`:235`) — **자동 재기동·replay 없음**. 진행·대기 명령 전부 `commandFailed` |
| 앱 종료 | `DashManager` 소멸자 → `shutdownBlocking():289` — `exit` write 후 최대 5초, 실패 시 kill |

exe 는 NX 내장 Python ABI 에 맞춰 버전별로 따로 빌드된다 — `resolveExePath:41-75` 가 `python3*.dll` 에서 뽑는 태그가 이 표에 대응한다.

| NX 버전 | 내장 Python DLL | exe 폴더 |
|---|---|---|
| NX2212 | `python310.dll` | `cad_nx_py310` |
| NX2306 \~ NX2406 | `python311.dll` | `cad_nx_py311` |
| NX2506 | `python312.dll` | `cad_nx_py312` |

JSON-RPC 2.0 은 양쪽 어디에도 없다 — GUI 전체에서 `jsonrpc`·`json_rpc`·`QLocalSocket`·`QTcpSocket` grep 0건, 데몬도 stdin 라인 파싱(`main.py:300`)이 전부다. `tests/` 전체에 `NxCad` 참조 0건이며, 트랜스포트(`DashExtensionProcess`)만 `tests/tst_process_runtime.cpp` 로 덮여 있고 그 위의 CAD 파사드 분기·배치 오케스트레이션은 덮여 있지 않다.

---

## 5. 산출 파일

**STEP — 생성 지점별 4종.**

| 산출 경로 | 언제 | 소비 |
|---|---|---|
| `{configs}/{prtBase}.stp` | `.prt` 등록 | Modeling Tree "Original" + OCCT |
| `{temp}/{prtBase}_{upper\|lower}_preview_{seq}.stp` | 프리뷰 버튼 | 프리뷰 노드 + OCCT. **다음 `loadPrt` 때 일괄 삭제**(`SolverNxCad:132-138`) |
| `{configs}/{prtFileName}` (`.prt` 복사본) | Set Design Variable | DOE 재현용 원본 보관 (위젯 `:626-641`) |
| `{outputBaseDir}/{runKey}/{runKey}.stp` | DOE 실행 (모듈 밖) | ANSYS Journal 이 파일명 규약으로 집어감 (`DashJobRunner.cpp:2529`·`:2577`) |

**`.prt` 부산물 — 데몬이 STEP 옆에 만든다.** `updatePrtGeometry` 는 원본 보호를 위해 출력 STEP 과 같은 base 의 `.prt` 로 SaveAs 한 뒤 사본을 고치므로(`main.py:252-259`) STEP 이 놓이는 자리마다 같은 이름의 `.prt` 가 함께 생긴다. (`.stp` 옆 `.log` 는 STEP creator 부산물이고 `export_utils.py:70-74` 가 성공 직후 지운다.)

| 경로 | 만드는 명령 | 지워지는가 |
|---|---|---|
| `{temp}/{prtBase}_{upper\|lower}_preview_{seq}.prt` | 프리뷰 | **안 지워진다** — GUI 가 `--no-cleanup` 상시(`SolverNxCad:159`), 다음 `loadPrt` 정리는 `*_preview*.stp` 만 글로빙(`:132-138`) → D16 |
| `{outputBaseDir}/{runKey}/{runKey}.prt` | DOE 배치 | 안 지워진다 — 실행 디렉터리 산출물로 남는다 |
| `{configs}/{prtBase}.prt` | — (`loadPrt` 가 **지운다**) | `_cleanup_temp`(`main.py:214`·`:330-338`)가 제거. 승격이 복사해 둔 보관본과 같은 경로 → D15 |

**`GeometryParameter_{Set}-CAD.json` — 실제 기록되는 키.**

```jsonc
{
  "variant": "CAD",                          // mergeSettingsRoot 가 강제 (PM:48)
  "Independent Parameter": {                 // Type 은 전부 "NX CAD" 리터럴 (Model:258)
    "Name": [...], "Part": [...], "Type": [...],
    "Value": [/* = upper, Model:259 */], "Lower": [...], "Upper": [...]
  },
  "Dependent Parameter": { "Name": [...], "Part": [...], "Type": [...], "Value": [/* 수식 */] },
  "DV-Geometry": {
    "<paramName>": {
      "boolean": true,                       // 미체크 행도 false 로 함께 기록된다
      "source": "CAD" 또는 "CAD|<part>",
      "type": "continuous",                  // 하드코딩 (PM:29)
      "meta": { "default": <num|null>, "min": <lower>, "max": <upper> }
    }
  }
}
```

경로 규칙은 `controller/DashIOController.cpp:12-22`(`{configs}/{module}_{setName}.json`)·`:114-121`, Set 생성 스켈레톤은 `model/DashProject.cpp:584-608` 이 `{"variant": "CAD"}` 만 적는다.

---

## 6. 상태 소유 지도

| 상태 | 1차 보관 | 병행 보관 | 저장 시 읽는 곳 |
|---|---|---|---|
| 파라미터 이름·파트 | `m_params` | 표 1·2열 아이템 | 모델 (`toSettingsJsonObject`) |
| Lower / Upper | `m_params[].lower/upper` | 셀 `QDoubleSpinBox` | **셀 위젯** (`collectCadDvRows:660-665`) |
| 체크 상태 | 표 0열 `checkState` | `m_params[].isChecked` · 헤더 tristate | 표 → 모델 역동기화 후 모델 |
| 현재값 (`value`) | `m_params[].value` | — | 저장 안 됨 — `meta.default` 는 lower |
| Dependent 파라미터 | `m_dependentParams` | Dependent 표 | 모델 |
| NX 파라미터 원본 | `DashManager::m_lastNxCadParameterJson` (`.h:153`) | — | 세션 캐시 — 파일에 안 씀 |
| 승격된 DV | 전역 공유 `DashDesignVariableModel` | 설정 JSON `DV-Geometry` | 공유 모델 `saveToJsonFiles()` |
| 마지막 `.prt` 경로 | `m_originalPrtPath` | 승격 시 `configs/` 복사본 | 복사본으로만 |
| 마지막 STEP 경로 | `m_lastLoadedStpPath` | Modeling Tree 노드 | — |
| 활성 해석파일 경로 | `Model::m_loadedFilePath` | 레지스트리 `activeFilePath()` | 읽는 곳 없음 → D5 |
| 배치 여부 | `m_batchMode` | — | — |

`DashManager` 가 허브 셋을 겸한다 — NX 파사드 소유(`solverNxCad()`) · 파라미터 JSON 세션 캐시 · 전역 공유 DV 모델(`GetDesignVariableModel()`). 위젯 한 파일에서 `DashManager::Mgr()` 9회, `getIOController()` 7회, `cellWidget(` 4회.

---

## 7. 결함 목록

3\~6절 서술 중 동작이 의도와 어긋나거나 어긋날 수 있는 지점 20건 — `D` 잘못 구현된 것 17건, `U` 구현되지 않은 것 3건. ID 는 3절 등장 순서, D14\~D16 은 데몬 왕복 고유라 뒤에 붙였다. 우선순위 판정은 하지 않는다. 9개 모듈 교차 색인은 [Cross-Module-Defect-Index](Cross-Module-Defect-Index.md).

`U1`\~`U5` 는 2026-08-29 에 일괄 제거됐다. 예정 기능 2건(Meshing · Match NSET, 3-6)은 제외를 유지하고 — Meshing 은 그 뒤 `b791b10` 이 DEV 전용 다이얼로그로 분리·배선했다 — 예정 기능이 아닌 3건은 아래에 `U3`\~`U5` 로 복원했다.

| ID | 분류 | 결함 | 좌표 | 근거와 귀결 |
|---|---|---|---|---|
| **D1** | 진입·수명 | `.prt` 성공 경로에서 로딩 스피너가 멈추지 않는다 | 3-2 | stop(`:2292-2297`)이 `suffix != "prt"` 안에 있고 완료 슬롯(`:2300-2319`)에도 없다 → 정지는 실패 경로(`:271`)뿐, **성공하면 상태바가 "Loading …" 에 머문다** |
| **D2** | 실행 모델 | `.prt` 진입 초입에 `processEvents` 가 있다 | 3-2 | `:2155`. `ExcludeUserInputEvents` 는 큐된 슬롯·타이머를 막지 않는다 → 데몬 stdout 처리가 재진입해 `applyNxCadParameterJson` 으로 모델을 갈아엎을 수 있다 |
| **D3** | 구조·결합 | 한 명령의 두 산출물이 다른 채널로 도착하고 합류점이 없다 | 3-2 | 파라미터 JSON 은 `outputLine`(`:386`, 명령 수명 무관), STEP 은 `[FINISHED]`(`:404`) → 둘의 선후도 정합 확인 지점도 없다 |
| **D4** | 데이터 정본 | 세션 캐시 재적용이 저장된 DV 체크 상태를 지운다 | 3-3 · 3-8 | 위젯 `:317-323` 이 `boolean` → `isChecked` 를 복원한 직후 `:324-327` 이 캐시를 재적용하고, 그 함수는 `m_params` 를 비워(`Model:299`) 전 행을 `isChecked = false`(`:332`)로 재구성한다 → **`.prt` 를 한 번이라도 로드한 세션은 저장 체크가 뜨지 않고,** 그대로 승격하면 전 항목이 `boolean:false` 로 덮인다 |
| **D5** | 구조·결합 | 해석 덱 유입 경로가 결과를 만들지 않은 채 살아 있다 | 3-3 · 6절 | `refreshFromFile:412-424` → `refreshFromLoadedAnalysis:102-115` 가 `m_loadedFilePath` 만 적는데 읽는 둘(`:97-100`·`Model.h:44`)은 호출처 0 → 매 진입의 레지스트리 로드가 무산출, 실패해도 `:421` 이 `qWarning` 뿐 |
| **D6** | 데이터 정본 | 정렬 방어가 경로마다 다르다 | 3-4 · 3-7 | 이름 매칭(`:568-579`·`:668-673`) · 시각 행(`:660-665`·`:818-828`) · 캡처 행(`:483`). `sortItems`(`:496`) 뒤 셋이 같은 행이라는 보장이 없다 → 잘못된 파라미터에 범위가 붙는다 |
| **D7** | 구조·결합 | 실패 통지가 요청과 짝지어지지 않는다 | 3-5 · 4절 | 손실은 파사드에서 난다 — `onCommandFailed:209-212` 가 `commandId` 를 동사 판별에만 쓰고 `emitFailure(bool, message)`(`:218-225`)에 경로 인자가 없다. 성공은 2종인데 실패는 `loadPrtFailed` 하나가 겸용(`:223`) |
| **D8** | 구조·결합 | 방출 대상이 전역 1비트로 스위칭된다 | 3-5 · 4절 | `m_batchMode` — `.h:68` 선언 · `:202`·`:220` 읽기 · `DashJobRunner.cpp:2544`·`:2748` on·off. 요청 단위가 아니라 전역이라 배치 중 프리뷰를 누르면 그 완료도 배치 시그널로 나가고 막는 락이 없다. 헤더 주석(`:41-45`)이 "구독자는 뷰" 전제를 명시 |
| **D9** | 진입·수명 | NX CAD 스피너가 비대칭이다 | 3-5 | 프리뷰 완료(`DashMainWindow.cpp:278`)는 stop 만 부르고 시작이 없다(`start…` 호출처는 `DashModelRunnerWidget.cpp:450`·`DashOptimizerWidget.cpp:1622`) → 진행 표시 없이 돌고 끝날 때만 문구가 뜬다 |
| **D10** | 데이터 정본 | `meta.default` 에 현재값이 아니라 Lower 가 들어간다 | 3-7 | 위젯 `:670` 이 읽는 모델 3열은 `Model::data:153` 의 `param.lower` 다. PM 헤더는 `// current model value as text`(`PM.h:24`)이고 `CADParameterRow::value` 는 DV JSON 에 닿는 경로가 없다 |
| **D11** | 데이터 정본 | `Independent Parameter.Value` 의 쓰기·읽기 계약이 어긋난다 | 3-7 · 4-2 | 저장은 `p.upper`(`Model:259`), 로드는 "현재값" 으로 읽어 `lower = upper = value`(`:321-324`). `Lower`/`Upper` 가 있으면 복구되나(`:325-330`) 데몬 JSON 에는 없다(`main.py:192-205`) → 데몬 JSON 만으로 채워진 행은 Lower = Upper 에서 출발 |
| **D12** | 데이터 정본 | 범위값의 정본이 모델이 아니라 셀 위젯이다 | 3-4 · 3-7 | 저장이 `cellWidget(visualRow, 3/4)` 스핀박스를 읽는다(`:660-665`). `m_params[].lower/upper` 는 병행 보관될 뿐 → 위젯을 거치지 않는 모델 변경은 저장값과 어긋난다 |
| **D13** | 진입·수명 | Set 삭제가 위젯의 모델 포인터를 댕글링으로 남긴다 | 3-8 | `:677` 의 `setModel(nullptr, …)` 을 `:311-313` 이 즉시 return 으로 흘리고, 직후 `DashProject.cpp:790` 이 `deleteLater()` 를 건다. 시그널은 `DashMainWindow.cpp:679` 에서 끊기나 살아 있는 워처의 `onDvJsonChanged:717-721` 이 죽은 `mModel` 을 역참조할 수 있다 |
| **D14** | 구조·결합 | 표현식 적용 실패가 GUI 에 닿지 않고 성공으로 보고된다 | 4-3 | `update_expressions`(`nx_helpers.py:56-62`)가 실패를 NX ListingWindow 에만 쓴다(`:62`) → `[ERROR]` 매칭(`:415`)에 안 걸리고 `main.py:325` 가 `[FINISHED]` 를 찍는다. **PRT 에 없는 이름이 DV 로 올라가면 값 미반영 STEP 이 성공 처리되고,** DOE 배치는 전 케이스가 같은 형상을 낼 수 있다 |
| **D15** | 진입·수명 | `loadPrt` 의 temp 정리가 승격해 둔 `.prt` 보관본을 지운다 | 4-2 · 5절 | `_cleanup_temp(step_path)`(`main.py:214`·`:330-338`)의 대상이 `{configs}/{prtBase}.prt`(출력 STEP `DashMainWindow.cpp:2273` 과 같은 base)라 승격 복사본(위젯 `:626-641`)과 **같은 경로**다 → 승격 후 재로드하면 보관본이 사라진다. `loadPrt` 는 SaveAs 를 하지 않아 지울 자기 부산물이 없다 |
| **D16** | 진입·수명 | 프리뷰 temp `.prt` 가 영구히 쌓인다 | 4-3 · 5절 | 상시 `--no-cleanup`(`SolverNxCad:159`)이 데몬 정리를 막고(`main.py:274-275`) 다음 `loadPrt` 정리는 `*_preview*.stp` 만 글로빙한다(`:132-138`) → 프리뷰 1회마다 `.prt` 가 남고 지우는 경로가 없다. NX 파트 파일이라 크기도 작지 않다 |
| **D17** | 데이터 정본 | Set ↔ `.prt` 결합이 어느 저장 경로에도 없다 | 3-8 · 5절 | `.prt` 는 프로젝트 전역 1개(`m_originalPrtPath`, 세션 한정)이고 설정 JSON 에 Set 별 필드가 없다(5절 키 목록). 승격이 `configs/` 로 복사해 두는 것이 유일한 흔적이며(위젯 `:626-641`) 그 복사본조차 D15 로 지워진다 → **재로드 후 어떤 `.prt` 가 이 Set 의 대상이었는지 복원할 수단이 없고 다시 Load 해야 한다.** Morphing 의 D11(대상 파트 미저장) · Condition 의 D10(대상 deck 미저장)과 같은 계급이다 |
| **U3** | 미구현 | 도달하지 않는 선언·정의가 남아 있다 | 3-3 · 3-7 | 호출처 0 — `Model::saveSettings`(`.h:52`·`.cpp:117`, `qDebug` 한 줄 no-op) · `Model::getContext`(`.h:34`·`.cpp:97`) · `Model::getLoadedFilePath`(`.h:44`) · 위젯 `setModel(DashGeometryParameterCAD*)` 오버로드(`.h:38`) · `enum class JobType`(`SolverNxCad.h:58`, 주석 `:73` 이 `commandId` 로 대체됐다고 적어 둠). 앞의 셋이 D5 가 말하는 "결과를 읽는 쪽이 없는" 그 지점이다 |
| **U4** | 미구현 | 성공·실패 판정이 데몬 로그 한 줄의 문자열 매칭이다 | 4-1 | `[FINISHED]` 라인 **전체 일치**(`ExtensionProcess:404`)와 `[ERROR]` **부분 일치**(`:415`)가 판정 전부다. 응답 라인에 요청 식별자가 없어 짝짓기는 순서에 의존하고(4-4), 데몬이 `[ERROR]` 를 stdout 에 쓰지 않는 실패 경로는 성공으로 마감된다(→ D14) → 프로토콜 계약이 코드가 아니라 로그 포맷이다. (JSON-RPC 도입은 예정 작업이고 여기서 말하는 결함은 그 부재가 아니라 현행 판정 근거다) |
| **U5** | 미구현 | 자동 회귀 보호가 없다 | 4-4 | `tests/` 전체에 `NxCad`·`GeometryParameter` 참조 0건. 등록 테스트는 `tst_job_state`·`tst_line_assembler`·`tst_process_runtime` 과 `e2e/tst_e2e_real_exe` 로 전부 프로세스·잡 계층이다 → 파사드 분기·배치 오케스트레이션·DV 승격 왕복이 전부 자동 검증 밖이다 |

---
