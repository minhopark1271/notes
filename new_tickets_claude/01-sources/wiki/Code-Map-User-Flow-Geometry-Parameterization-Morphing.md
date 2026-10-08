# Geometry Parameterization (Morphing) — 사용자 플로우 ↔ 코드 대응

> **성격**: 독립 참조 문서. Geometry Parameterization 의 Morphing 경로에서 사용자가 하는 행위 하나하나가 어떤 함수 체인을 밟는지의 대응표 — 수정 계획·우선순위 판정은 담지 않는다.
> **좌표 기준**: `dev` @ `ac6e4e6` 실측. 줄 번호는 이 커밋 기준이다(유효기간 있음).
> **검증 수준**: 정적 코드 근거만. 빌드·실행 검증 없음.

## 개요

화면 3면과 로직 클래스 8종이 VTK polydata `m_handleGeometry` 하나를 공동 편집한다. 사용자 행위는 `DashManager` 싱글턴을 거쳐 `DashHandlePickingInteraction` 의 배열에 도달하고, 화면은 그 배열을 다시 읽어 그린다. 3\~4절은 코드가 하는 일만, 결함은 5절 — 본문 `→ D{n}` 이 링크다.

---

## 1. 화면 3면과 소유 클래스

| 면 | 클래스 (소스 줄) | 부모 위젯 | 성격 |
|---|---|---|---|
| 우측 dock | `DashGeometryParameterWidget` (2,494 + ui 428) | `m_rightStackedWidget` | 탭 2종(Morphing·DV-Geometry). 핸들 트리·구속 표 소유 |
| 렌더뷰 툴바 | `DashMorphingBar` (128 + ui 163) | `m_renderingWidget` | 모드 6종 + Reset/Prev/Next/Done |
| 툴바 아래 팝업 | `DashMorphingSettings` (1,670 + ui 729) | `DashMainWindow` | 모드별 파라미터 + Generate |

부모가 달라 좌표를 코드로 맞춘다 — `DashMainWindow.cpp:1815-1823` 이 툴바 global 좌표 아래 10px 로 `move()`.

| 로직 클래스 (줄) | 담당 |
|---|---|
| `DashHandlePickingInteraction` (3,121) | 픽킹·기즈모·핸들 배열 정본. 모듈 단일 최대 파일 |
| `DashMorphingController` (1,498) | 자동 핸들 생성 6종 + physics/marching-plane 프리뷰 |
| `DashHandleVisualizer` (579) | 글리프·화살표·하이라이트 파이프라인 |
| `DashMorphingEngine` (95) | 모핑 DLL(`DashOptiMorphing` 0.0.4) 진입 — `ExecuteMorphing` 1종 |
| `…ParameterPresentationModel` (489) | DV 엔트리 조립 · VTP 쓰기 · 설정 JSON 병합 |
| `DashGeometryParameter` (192) | Set 1개의 GUI 표현 — 경로·이름·radius |
| `DashManager` (1,040) | 프리뷰·볼륨 모핑 진입점 · 싱글턴 허브 |
| `MeshQC` (`MeshQualityCheck.hpp`, 550) | Set Design Variable 직전 품질 판정 |

---

## 2. 전체 동선

```
1. 진입      [Add Set]→"for Morphing" → 파트 클릭 → [▶ Start Morphing]
             ※ 파트가 붙은 Set 재선택은 시작 페이지를 건너뛴 복구 진입
2. 모드 선택  툴바 6종 = 픽킹 방식(클릭/드래그/박스) 전환
             ※ 모드 진입 즉시 켜져 있던 프리뷰 강제 해제
3. 핸들 확정  렌더뷰 시드 → (Surface/Volume/Physics) [Generate] → [Done]
             ※ [Reset] 은 확정 핸들이 아니라 미확정 시드만 지운다
4. 범위 편집  트리 Lower/Upper/θy/θz 또는 기즈모 · Group/Ungroup/Delete/Add Values
             ※ 프리뷰 중이면 확인 대화상자로 해제를 먼저 요구
5. 범위 확인  Kernel Radius(즉시 JSON 기록) → [Lower/Upper Preview] 배타 토글
             ※ 켜진 상태의 값 변경은 입력마다 GUI 스레드 모핑 1회
6. DV 승격   [Set Design Variable] → Lower/Upper 볼륨 모핑 2회 품질 판정
             → [Proceed] → VTP + JSON → DV-Geometry 탭

[산출] configs/GeometryParameter_Set{N}.json + 동명 .vtp — 하류(DOE·Optimizer·Model Runner)가 읽는 전부
```

---

## 3. 단계별 대응

### 3-1. 진입

도크는 기본 숨김(`DashMainWindow.cpp:458`), Set 하위 항목 선택 시에만 열린다(`:592-593`). [Add Set] → `newSetRequested`(`DashProjectWidget.cpp:219-229`) → `onNewSetRequested:600` 이 **동기로** `displayWidgetForNewSet:801`(`:916-940` Morphing 분기 → `showStartPage()`·툴바 hide)을, **200ms 뒤** `QTimer::singleShot:625-652` 로 트리 프로그래매틱 선택 → `handleSubItemSelection` → `showStartPage()`·`showRightDock()` 를 밟는다. 신규 Set 은 `showStartPage()` 를 두 번 탄다.

**진입 갈림** — Set 선택마다 `getPartName()` 하나로 배타 판정(`:1125`). 비어 있으면 시작 페이지(`:1160-1171`), 채워져 있으면 복구 진입(`:1127-1159` — `setModel()` 만 재실행, `showStartPage()` 없음).

**시작 페이지** — 파트 클릭 `QTableView::clicked:536` → `updateStartMorphingUI:3311` → `updatePartSelection:183`. [▶ Start Morphing] → `onStartMorphingClicked:3197` → `getPartData(part)` → `setGeometry`/`setPartName`(`:3261-3262`) → `setModel:1797` → `initializeMorphingController:1697` → `setupMorphingBar:1750`. `m_partName` 이 채워지므로 **이후 이 Set 선택은 복구 갈래로 간다.** 파트 미선택이면 경고 후 중단(`:3211-3215`).

**초기화 체인** — 본체가 `setModel()` 직접 호출이 아니라 `dataLoaded` 람다 안에만 있다.

```
setModel(model)                              :1797
  ├─ connect(model, dataLoaded, [람다])      :1818
  │     ├─ UpdateTargetGeometry():1838 → DashManager::SetInputVTU():278
  │     │     ├─ CreateLinearizedVTU():347 (2차 요소만) · ComputeModelBoundSize():441
  │     │     ├─ ComputeMorphingSingleStep():459
  │     │     └─ InitializeHandlePicking():94
  │     │           └─ UpdateSurfaceGeometry():171 · InitializeHandleData():108
  │     │              · HandleVisualizer::InitializePipeline()
  │     ├─ loadMorphingFromJson():1869 · loadDvGeometryFromJson():2397
  │     └─ radius 복원 + Engine::SetMorphingKernelRadius:13
  ├─ showMainPage():1833
  └─ model->loadFromJson()                   DashGeometryParameter.cpp:127
```

`loadFromJson()` 은 마지막 줄에서 `emit dataLoaded()`(`:191`). 조기 반환 4경로(`:129`·`:135`·`:140`·`:148`)는 emit 없이 끝난다. → D1
`UpdateTargetGeometry()` 의 대상 선택은 2단 — 모델 `getGeometry()` 우선, 없으면 렌더링 매니저 base geometry actor 의 mapper 입력(`:1852-1861`). → D2

### 3-2. 모드 선택

툴바 6종은 `QButtonGroup::idClicked` 하나로 묶이고(`Bar:59`), 수신은 `DashMainWindow.cpp:1776` 람다 하나다.

| 툴바 모드 | `InteractionMode` | `PickingMode` | Settings 페이지 | Generate 신호 |
|---|---|---|---|---|
| Constraints | `MODE_CONSTRAINT` | `MODE_BOX` | Node | 없음 — Done 이 확정 |
| Manual | `MODE_MANUAL` | `MODE_CLICK` | Node | 없음 |
| Surface | `MODE_SURFACE` | `MODE_DRAG` | Automatic · Parametric | `generateRequested` · `…Distance…` · `…Curvature…` |
| Volume | `MODE_VOLUME` | `MODE_CLICK` | Marching Plane | `generateMarchingPlaneHandleRequested` |
| Physics | `MODE_PHYSICS` | **변경 없음** | File Import | `generatePhysicsHandleRequested` |
| Appearance | `MODE_NONE` | `MODE_CLICK` | Constraints · Morphing handle | 없음 |

전환은 `SetInteractionMode:1113` 의 `switch`(`:1152-1181`). Physics 가 "변경 없음"인 것은 이 `switch` 에 case 가 없어 `default: break` 로 떨어지기 때문이다. **표의 `PickingMode` 는 초기값일 뿐** — Node 페이지 라디오 3종이 `SetPickingMode:1190` 을 직접 호출해 덮어쓴다(Click `Settings:536`·Drag `:541`·Box `:546`). Constraints 에서만 4번째 **Node Set** 추가(`:527`, → 3-8).

부수효과 2종 — `isHandleCreationMode` 이면 `MorphingPreview(false,None)` 선행(`:1116-1122`) · `MODE_VOLUME` 진입·이탈 시 베이스 actor 불투명도 0.3 ↔ 저장값(`:1141-1149`).

페이지 교체는 `swapSettingsWidget:361`. Generate 신호 분기는 타입 키가 아니라 `isVisible()` 7단 캐스케이드다(`:116-160`). → D3
툴바 Prev/Next 는 emit 만 하고 수신처가 레포에 없다(`Bar:69-70`).

### 3-3. 핸들·구속 확정

> **용어** — 여기의 "구속"은 Constraints 모드로 찍는 고정 영역이다. 엔진이 보는 고정점은 더 넓다 — `GetAllFixedSurfacePointIds:3026` 이 파일 로드 비설계 영역(`m_nonDesignSurfaceIds`)과 사용자 구속(`m_constraintSurfaceIds`)을 합친다.

**시드 선택** — 렌더뷰 상호작용 결과는 전부 표면 polydata 의 `ConstraintsAndHandles` 배열 한 개에 값으로 기록된다.

| 값 | 의미 | 쓰는 곳 |
|---|---|---|
| `0.0` | 없음 | `Reset:1217-1230` · Shift+드래그(`OnLeftButtonUp:1031`) |
| `1.0` | 확정 핸들 시드 | Manual 드래그(`:1032`) · `UpdateSurfaceHandleSelection`(`Controller:1100`) |
| `2.0` | 구속 시드 | Constraint 드래그(`:1033`) |
| `3.0` | Surface 후보점 | Surface 드래그(`:1034`) |
| `-1.0` | 프리뷰 전용 숨은 고정점 | `MorphingPreview:725-742` |

도달 경로 3종 — 좌클릭 `Execute:521`→`OnLeftButtonDown:547`(20px 반경 + z-buffer + 배면 컬링) · 드래그 `OnLeftButtonUp:1002`→`vtkSelectVisiblePoints`→값 1/2/3 일괄 기록 · 박스 위젯 `OnBoxSelection:1082`(값 2).

**Generate** — 시드를 핸들 후보로 환산.

| 페이지 | 신호 | 슬롯 | 하는 일 |
|---|---|---|---|
| Automatic | `generateRequested(k)` | `Controller:185` | 값 3 에서 고정점 제외 → `calculateSupportRadius` → `selectHandlesGreedyByUnit` k개 → 값 1 승격 |
| Parametric (거리/곡률) | `generateDistance…`/`generateCurvature…` | `:892` / `:823` | 간격 균등 선택 / 곡률 임계 이상 선택 |
| File Import | `generatePhysicsHandleRequested` | `:237` | CSV 밀도값 → 클러스터 → 표면 `GroupIds` |
| Marching Plane | `generateMarchingPlaneHandleRequested` | `:80` | 시점·종점·구간수 → 평면열 → `AddPendingMarchingPlaneData` |

File Import 의 집합연산 버튼 3종은 만들어져 있으나 레이아웃에 배치되지 않는다(`Settings:1376`). **Generate 없이 Done** 이면 `Finalize` 가 "값 1 이 0개인데 값 3 있음"을 감지해 중단한다(`:1333-1349`).

```
[Done] → DashMainWindow.cpp:1848 람다
   ├─ (Constraints) GetSelectedConstraintCells():3000  ← Finalize 이전 채집
   ├─ interaction->Finalize()                     HandlePicking:1241
   │     ├─ pending box/cylinder                       :1252-1327
   │     ├─ MANUAL/SURFACE  값 1 → AddHandleData(type 1) :1328-1418
   │     ├─ PHYSICS  GroupIds>0 → AddHandleData         :1419-1507
   │     ├─ VOLUME   pending plane → AddHandleData(type 2) :1508-1534
   │     ├─ CONSTRAINT 값 2 셀 → m_constraintSurfaceIds  :1535-1588
   │     └─ Reset():1217 · SetInteractionMode(MODE_CONFIG):1113
   ├─ (Constraints) "Constraint_Group_{max+1}" → appendConstraintTable:647
   └─ (그 외) updateHandleTreeFromInteraction(isPhysics)   Widget:1895
```

pending box/cylinder 는 툴바에 대응 버튼이 없어 현재 UI 로는 도달하지 않는다. 확정 시 **비설계 필터 2겹** — `NonDesignMask` 배열과 구속·비설계 셀의 점 집합(`blockedPointIds`)(`:1351-1372`). 구속을 먼저 걸면 그 위에는 핸들이 생기지 않는다.

`AddHandleData:149` 가 쓰는 핸들 polydata 배열 11종(`DashHandleTypes.h`) — 핸들 1개의 모든 속성이 여기 흩어진다. → D4

| 배열 (성분) | 의미 |
|---|---|
| `LocalNormal`(3) / `HandleNormal`(3) | 기준 방향(사용자 지정 보존) / 실제 모핑 방향 |
| `SelectionScalars`(1) · `ActiveStatus`(1) | 선택 여부(활성 스칼라) / 0 이면 픽킹·기즈모 동기화 제외 |
| `GroupIds`(4) · `PlaneIds`(1) · `HandleType`(1) | 그룹 id(plane 은 4방향) / 평면 id / 1=표면, 2=plane |
| `LowerRange`(4) / `UpperRange`(4) | 표면 `[변위,0,0,0]` / 평면 `[xmin,xmax,ymin,ymax]` |
| `Bounds`(6) · `LocalToGlobal`(16) | marching plane 전용 2D 경계 · 변환 행렬 |

**트리 반영** — `updateHandleTreeFromInteraction:1895` 는 트리를 매번 통째로 재구축하고, 행 ↔ 핸들 결합은 `Qt::UserRole` 오프셋으로만 유지한다(`:1897-1903` 주석이 정본): `+1` type · `+2` handle id(= point index) · `+3` group id · `+4` plane id · `+5` bound index · `+6` matrix. 열은 0 No. / 1 체크박스 / 2 Name / 3 Lower / 4 Upper / 5 θy / 6 θz. 사용자가 붙인 이름만 `QMap<int,QString>` 으로 임시 보존했다 복원하며, 보관처는 이 맵과 아이템 텍스트뿐이다(`:1922-1937`). → D5

### 3-4. 범위·방향 편집

진입점은 스핀박스와 기즈모 둘, 둘 다 같은 배열에 도달한 뒤 `UpdatePreviewMorphing()` 을 부른다.

- **Lower/Upper 스핀박스** — `Widget:540/548` → `UpdateHandleRange:1828` → `UpdateHandleGizmos:2070` → `DashManager::UpdatePreviewMorphing:657`
- **θy/θz 스핀박스** — `:556/565` → `UpdateHandleGizmoEuler:1920` → `OnHandleGizmoChanged:2414` → `HandleNormal`(그룹 0 이면 `LocalNormal` 도) + `UpdateHandleRange`
- **기즈모 드래그** — `OnHandleGizmoChanged:2414` / `OnPlaneGizmoChanged:2460` / `OnGroupGizmoChanged:2497`
- **트리 행 선택** — `itemSelectionChanged:888` → `updateHandleSelection:196` → 하이라이트·기즈모 표시 갱신

기즈모 편집에는 역방향 경로가 붙는다 — 배열 수정 직후 `syncMorphingTableRows(id,isGroup)`(`Widget:284`)가 트리 셀 스핀박스에 되쓴다. 호출처는 전부 `HandlePicking` 안 3곳(`:2030` 개별 · `:2350` 그룹 · `:2493` 평면). 셀 위젯이 저장 정본이므로(→ D9) 이 동기화가 빠진 배열 변경은 저장에 반영되지 않는다.

θ 왕복은 각도가 아니라 방향 벡터를 거친다 — 기즈모 행렬 1열을 정규화해 `HandleNormal` 에(`:2436-2446`), 트리 표시값은 `GetEulerAngles()` 역산(`:527-537`), 재로드는 `SyncHandleGizmo:2077` 의 `SetDirectionFromVector`. → D6

편집 버튼 4종은 모두 `DashManager::PreviewCheck:852` 를 먼저 통과한다(프리뷰 중이면 확인 대화상자).

| 버튼 | 슬롯 | 동작 |
|---|---|---|
| Group | `onGroupHandles:1279` | 타입 혼합 금지 검사 → `nextGroupId`(PM `:477`) → 구성원 범위를 `±GetMorphingSingleStep()` 으로 **초기화** |
| Ungroup | `:1374` | `GroupIds` 0, 표면 핸들은 `LocalNormal` 로 방향 복원 |
| Delete | `:1426` | 표면 핸들 / 평면 id 집합 분리 후 제거 |
| Apply / Reset (Add Values) | `:1602` / `:1652` | 체크·선택 행 스핀박스에 직접 가감 — 배열이 아니라 위젯을 건드리고 값 변경 시그널이 위 체인을 다시 탄다 |

### 3-5. 변형 범위 확인

- **Kernel Radius** — `:676` → `SetMorphingKernelRadius:13` → **설정 JSON 즉시 read-merge-write**(`:640-663`). 프리뷰 중이면 재실행. 스텝 버튼 값은 정수 강제 반올림(`:683-695`). 위의 Morphing Function 콤보는 숨김(`:625-627`).
- **Straight Sided** — 상태만 보관하고 `IsStraightSidedChecked()` 로 조회. 프리뷰 중 radius·체크박스 비활성(`:701-702`).
- **[Lower/Upper Preview]** — `:717`/`:736` → `MorphingPreview:682`. 배타 — 한쪽을 켜면 다른 쪽을 `QSignalBlocker` 로 끈다.

```
MorphingPreview(true, type)                  DashManager.cpp:682
  ├─ SetInteractionMode(MODE_CONFIG)         (핸들 생성 차단)
  ├─ [최초 1회] 고정점 샘플링                  :702-770
  │     GetAllFixedSurfacePointIds():3026 → GenerateMarkerPointsFromSurfaceIds()
  │     → 샘플점 ConstraintsAndHandles = -1.0 (m_hiddenFixedIds)
  │     → ExtractInitialMorphingPoints():1598 → Engine::SetInitialHandles:23
  ├─ IsStraightSidedChecked() ? RunLinearMorphingForPreview:584 : RunMorphingForPreview:539
  │                              └─ 둘 다 Engine::ExecuteMorphing:61 (선형화 / 원본 표면)
  └─ 프리뷰 actor 등록 · updateHandleSelection()
```

프리뷰 중 입력 1회마다 `UpdatePreviewMorphing:657` 이 모핑 1회를 GUI 스레드에서 동기 실행한다. → D7
끄면 `-1.0` 숨은 고정점을 0 으로 되돌리고 actor·geometry 를 버린다(`:807-826`).

### 3-6. 설계변수 승격

`Set Design Variable` 한 번이 이 모듈의 유일한 영속화 지점이다 — 이 버튼 밖에서 파일에 기록되는 것은 Kernel Radius 뿐.

```
[Set Design Variable] → onSaveDesignVariableClicked   Widget:939
   ├─ 트리 순회 — 체크 행 itemWidget 스핀박스 값 → DvRow DTO   :949-985
   ├─ PM::buildDvGeometry():30   활성 .dat → configs 복사 · source "Morphing|{dat}|{component}"(:79-82)
   │                             · param{N}(min/max/group id/handle id/bound index)
   ├─ PM::filterSelectedHandles():172   선택 핸들만 복사 + old→new id 재매핑
   ├─ DashMeshQualityDialog + processEvents()    :1014-1018
   ├─ for testType in {Lower, Upper}             :1054-1127
   │     ├─ processEvents():1061
   │     ├─ ExtractInitial/TargetMorphingPoints  :1598 / :1674
   │     ├─ DashManager::RunVolumeMorphing:481 → ExecuteMorphing:61
   │     │                                     → CreateRestoredQuadraticVTU:426 (2차 요소일 때만)
   │     └─ MeshQC::EvaluateMeshQuality:522 · AnalyzeFailedElements:1175 (실패 셀 근처 핸들 KdTree 역추적)
   ├─ dialog.exec() — [Proceed] 아니면 중단       :1136
   └─ PM::saveMorphingSettings():325
         {jsonBaseName}.vtp 쓰기 · Morphing.handles_vtp/radius/straight_sided 병합
         · root["variant"]="Morphing" · root["DV-Geometry"]=param{N}
   → loadDvGeometryFromJson():2397 → DV-Geometry 탭
```

이 모듈의 `processEvents` 는 정확히 2곳이며 둘 다 이 함수 안이다(`:1018`·`:1061`). → D8
저장 시 범위값은 `itemWidget(item, 3/4)` 의 `QDoubleSpinBox` 에서 읽는다(`:960-969`) — polydata 의 `LowerRange`/`UpperRange` 는 병행 보관될 뿐 읽히지 않는다. → D9

### 3-7. 재진입과 복원

| 복원 대상 | 저장처 | 읽는 곳 | 상태 |
|---|---|---|---|
| 핸들 전량 (위치·방향·범위·그룹) | `{Set}.vtp` | `parseMorphingSettings`(PM `:393`) → `loadHandlesFromVtp:2360` → `DeepCopy` + `SyncHandleGizmosFromGeometry:2133` | 복원됨 |
| Kernel Radius · Straight Sided | JSON `Morphing.radius`/`.straight_sided` | `loadFromJson:127` · `DashMorphingDoeExecutor.cpp:780` | 복원됨 |
| DV 체크 상태 | JSON `DV-Geometry.param{N}.boolean` | `loadFromJson:164-188` | 복원됨 |
| 구속(Constraints) | — | `parseMorphingSettings:450-468` 이 읽으나 writer 가 없다 | 소실 → D10 |
| 대상 파트 · volume mesh | — | 호출처 `DashMainWindow.cpp:3261-3262` 1곳. 저장 키에 part 없음 | 소실 → D11 |
| 핸들 이름 | — | 트리 재구축 시 메모리에만(`:1922-1937`) | 세션 내 → D5 |

명시적 리셋은 Set 을 **바꿔** 진입할 때만 돈다(`:3229-3244` — `Reset()`·`MorphingPreview(false)`·`ResetPhysicsPreviews()`·트리 `clear()`). 같은 Set 재선택에는 이 블록이 없어 두 상태의 수명이 갈린다 — 구속 표는 `appendConstraintTable:575` 이 항상 `insertRow(rowCount())`(클리어·중복 검사 없음), 핸들 polydata 는 `InitializeHandleData:108` 의 `if (!m_handleGeometry)` 가드로 이전 것을 물려받는 반면 같은 초기화의 `UpdateSurfaceGeometry:171` 은 표면을 매번 교체한다. → D12

구속 행은 `updateConstraintVisualization:2432` → `SetVisibleConstraintIds:2989` → `UpdateNonDesignAndConstraintOverlay:2809` 를 거쳐 `vtkExtractSelection` 입력이 된다.

### 3-8. 크리티컬 패스 밖의 경로

| 경로 | 좌표 | 요점 |
|---|---|---|
| **구속 생성 2번째 경로 — Node Set** | `Settings:527`·`:559`·`loadNodeSetList:628` → `DashMainWindow.cpp:1766` | Constraints 전용 라디오. 명명 노드셋(엘리먼트셋 제외) → `ConvertAnsysIdToVtuId` → `vtkKdTreePointLocator` 최근접점 → 셀 집합 → `constraintAdded`. **픽킹도 [Done] 도 거치지 않는다** |
| **구속 표 UI** | `appendConstraintTable:575` | 행마다 Show/Hide·삭제 `X`. 추가·토글·삭제 셋 다 끝에서 `updateConstraintVisualization:2432`. 셀 id 는 이름 아이템 `Qt::UserRole` |
| **툴바 [Reset]** | `DashMainWindow.cpp:1830` | `ResetPhysicsPreviews:1470`→`Reset:1217`→`Redraw()`. 확정 핸들은 안 건드림. Done/Reset 은 초기 비활성 → 모드 버튼으로 활성(`Bar:60-63`) → `ResetMorphingBar` 로 복귀(`:73-83`) |
| **Physics 파일 행** | `addFileRow:1559`·`onPhysicsFilePathChanged:411`·`…Threshold…:478`·`…FileRemoved:464` | 행별 색 글리프 actor(`createPhysicsPreviewForRow:374`)는 [Generate] 이전 미리보기라 핸들 polydata 와 무관. Set 변경 시 `ResetPhysicsPreviews` 가 걷어냄 |
| **Appearance 모드** | `createAppearanceSettings:1431` → `UpdateAppearance:1647` | 픽킹 없이 표시만(`MODE_NONE`). 색(구속색 `SetConstraintColor:3098`)·프리뷰 불투명도·화살표/마커 크기. 렌더링에만 반영되고 저장 안 됨 |
| **렌더뷰 → 트리 역선택** | `SelectSurfaceHandleInTree:611` · `SelectEdgeInTree:663` | 핸들/평면 엣지 픽킹이 트리 선택으로. 빈 곳은 둘 다 `-1`(`:673-674`), Ctrl 이 다중 선택 플래그 |
| **그룹 방향 모드 L/U** | `Widget:2039`·`:2069`·`:2167-2188` | Uniform 일 때만 그룹 θy/θz 활성, 전환 순간 자식 normal 산술평균이 그룹 방향. 기본값 Local(`:2041`) |
| **DV-Geometry 탭** | `setupDvGeometryTab:1259`·`loadDvGeometryFromJson:2397` | `m_designVariableModel` 을 붙인 `QTableView` 하나. 값을 고치는 경로가 없는 읽기 표 |

---

## 4. 상태 소유 지도

| 상태 | 1차 보관 | 병행 보관 | 저장 시 읽는 곳 |
|---|---|---|---|
| 핸들 위치·방향 | `m_handleGeometry` 배열 | `DashGizmo` 인스턴스 | polydata |
| 핸들 범위 (Lower/Upper) | `LowerRange`/`UpperRange` | 트리 셀 `QDoubleSpinBox` | **셀 위젯** |
| 핸들 θy/θz | `DashGizmo` Euler | 트리 셀 스핀박스 | 저장 안 됨 (벡터로만 왕복) |
| 그룹 소속 | `GroupIds` | 트리 부모-자식 · `m_gizmoGroups` | polydata |
| 핸들 이름 | 트리 `item->text(2)` | — | 저장 안 됨 |
| 구속 셀 | `m_constraintSurfaceIds` | `m_consTable` 행 + `Qt::UserRole` id 리스트 | 저장 안 됨 |
| 대상 파트 | `DashGeometryParameter::m_partName` | — | 저장 안 됨 |
| 프리뷰 타입 | `DashManager::m_currentPreviewType` | 두 버튼의 checked 상태 | — |

`DashManager` 는 뷰 포인터 2개를 보유한다 — `m_geometryParameterWidget`(`DashManager.h:114`)·`m_morphingSettingsWidget`(`:116`). 프리뷰 계열이 이 포인터로 위젯 상태를 조회한다 — `IsStraightSidedChecked()`(`:673`·`:767`)·`updateHandleSelection()`(`:798`·`:827`)·버튼 `isChecked()`(`:836`·`:839`). → D13

싱글턴 도달 빈도 — 위젯 한 파일에서 `DashManager::Mgr()` 67회, `Qt::UserRole` 68회, `itemWidget(` 20회.

---

## 5. 결함 목록

3\~4절 서술 중 동작이 의도와 어긋나거나 어긋날 수 있는 지점 16건 — `D` 잘못 구현된 것 14건, `U` 구현되지 않은 것 2건. ID 는 3절 등장 순서, 우선순위 판정은 하지 않는다. 9개 모듈 교차 색인은 [Cross-Module-Defect-Index](Cross-Module-Defect-Index.md).

`U1`\~`U5` 는 2026-08-29 에 일괄 제거됐다. 그중 예정 기능 갈래 3건(볼륨 핸들 타입 주석 처리 · Physics 집합연산 버튼 미배치 · Morphing Function 콤보 숨김)은 결함이 아니라 착수 대기이므로 제외를 유지하고, 예정 기능이 아닌 2건은 아래에 `U1`·`U2` 로 복원했다.

| ID | 분류 | 결함 | 좌표 | 근거와 귀결 |
|---|---|---|---|---|
| **D1** | 진입·수명 | 초기화가 `dataLoaded` emit 에만 걸려 있고 화면 전환이 먼저다 | 3-1 | 조기 반환 4경로는 emit 없음 → **설정 JSON 없는 신규 Set 은 화면이 뜬 채 `UpdateTargetGeometry` 이하가 전부 건너뛰어진다** |
| **D2** | 진입·수명 | geometry 부재 시 파트 검증 없이 다른 액터로 대체 | 3-1 | `:1852-1861` 이 base geometry actor 를 그대로 넘긴다 → VTP 복원 핸들 인덱스가 다른 파트 표면을 가리킬 수 있다 |
| **D3** | 구조·결합 | Generate 분기가 위젯 가시성 캐스케이드 | 3-2 | `Settings:116-160` 7단 `isVisible()` — 페이지 추가 시 캐스케이드 순서가 계약이 된다 |
| **D4** | 구조·결합 | 한 클래스가 4역할 — 픽킹·기즈모·핸들 데이터·구속 오버레이 | 3-3·3-4·3-8 | 3,121줄, 도메인 타입 없이 배열 11종이 모델 노릇. 헤더 TODO(`:35-36`)에 분리 계획이 이미 적혀 있음 |
| **D5** | 데이터 정본 | 핸들 이름이 어디에도 저장되지 않는다 | 3-3·3-7 | `QMap`(`:1922-1937`)과 아이템 텍스트가 전부. VTP 에도 JSON 에도 없다 |
| **D6** | 데이터 정본 | θ 가 각도로 왕복하지 않는다 | 3-4 | 저장은 벡터, 표시는 Euler 역산(`:599-609`), 재로드는 `SetDirectionFromVector` → **표시값이 입력값과 같다는 보장이 없다** |
| **D7** | 실행 모델 | 프리뷰 모핑이 GUI 스레드 동기 실행 | 3-5 | `UpdatePreviewMorphing:657`. 프리뷰 중 입력 1회 = 모핑 1회. 워커화되지 않음 |
| **D8** | 실행 모델 | `processEvents` 가 모핑 루프 안에 있다 | 3-6 | `:1270`·`:1313`. 볼륨 모핑 2회가 도는 사이 사용자 입력이 재진입한다 |
| **D9** | 데이터 정본 | 범위값 정본이 배열이 아니라 트리 셀 위젯 | 3-4·3-6 | 저장이 `itemWidget(item, 3/4)` 를 읽으므로(`:960-969`), `syncMorphingTableRows` 가 빠진 배열 변경 경로는 저장값과 어긋난다 |
| **D10** | 데이터 정본 | `Morphing.constraints` 가 읽기 전용 | 3-3·3-7·3-8 | 파서(`PM:450-468`)만 있고 writer 가 없다 → Constraints 산출물이 세션을 넘기지 못한다 |
| **D11** | 진입·수명 | 대상 파트가 어느 저장 경로에도 없다 | 3-1·3-7 | `saveMorphingSettings`(PM `:325`) 키에 part 없음 → 재로드 후 `getPartName()` 이 항상 비어 설정 완료 Set 도 시작 페이지로 떨어지고, 재진입 시 **D2 와 연쇄** |
| **D12** | 진입·수명 | 같은 Set 재진입이 상태를 누적 | 3-7 | 리셋(`:3229-3244`)이 Set 이 **바뀔 때만** 돌아, 재진입 N 회면 구속 행이 N 배로 `vtkExtractSelection` 에 투입되고 핸들 polydata 는 표면과 수명이 어긋난다 |
| **D13** | 구조·결합 | 컨트롤러가 뷰 포인터를 무가드로 역참조 | 4절 | `:673`·`:767`·`:798`·`:827`·`:836`·`:839`. **`:827` 바로 아래 `:830` 에 같은 포인터의 널 가드가 있다** — 검사가 사용보다 뒤에 온다 |
| **D14** | 진입·수명 | Geometry 카테고리는 트리 루트 1개에 모델 배열 2벌인데 Morphing 갈래만 행 인덱스로 조회한다 | 3-1 | 트리는 `m_geometryParamRoot` 하나에 Morphing·CAD 항목을 함께 넣고(`DashProject.cpp:128`·`:166`) 모델은 `m_geometryParameters`·`m_geometryParametersCAD` 두 배열이다. 라우팅은 CAD 갈래만 이름 매칭이고(`DashMainWindow.cpp:1137-1144`) Morphing 갈래는 `index.row()` 로 배열을 첨자한다(`:1157-1164`). 프로젝트 재로드는 configs 파일명 순으로 적재하므로 `-CAD` Set 이 앞에 오면 뒤의 Morphing Set 은 `rowIndex >= params.size()` 로 조기 반환된다(`:1159-1161`) → **CAD Set 을 섞어 쓴 프로젝트에서 일부 Morphing Set 이 클릭해도 경고 없이 열리지 않는다.** Model Builder 는 Sim·MCU 양쪽을 이름 매칭으로 처리해(`:1391-1430`) 같은 구조에서 이 문제가 없다 |
| **U1** | 미구현 | `MODE_PHYSICS` 가 `SetInteractionMode` 의 `switch` 에서 누락 | 3-2 | 툴바 Physics 버튼이 `DashMainWindow.cpp:1878` 에서 이 모드를 세우지만 `switch`(`HandlePicking:1152-1181`)에 case 가 없어 `default: break` 로 떨어진다 → 픽킹 방식이 직전 모드에서 이월된다. 예정 기능이 아니라 살아 있는 경로의 누락이다 |
| **U2** | 미구현 | 툴바 Prev/Next 가 emit 만 하고 수신처가 없다 | 3-2 | `Bar:69-70` 의 두 시그널을 레포 전체에서 받는 곳이 없고 `onEditUndo`/`onEditRedo` 의 TODO 와 짝이다 → 버튼은 눌리는데 아무 일도 일어나지 않는다 |

---
