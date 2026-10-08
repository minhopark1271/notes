# 핸들 데이터·뷰 분리 — `DashHandleData` 추출 범위

> **성격**: 독립 조사 문서. 열린 티켓을 참조하지 않고, 진행 중인 워커화 계획과 무관하게 이 분리 하나만 잰다.
> **좌표 기준**: `feat/rw-actor` @ `66c126c`. 아래 모든 행 번호는 이 커밋 실측이다.

## 배경 및 동기

RW 축은 이미 같은 분리를 했다. `b533191` 이 `DashAnalysisModelContext` 에서 RW 계층을 `DashRwSession` 으로 떼내고 컨텍스트에는 GUI 표현만 남겼다. 그 앞 커밋 `3734897` 이 DLL 접근을 `DashRwActor`/`DashRwClient` 한 쌍으로 좁혔고, 두 타입 모두 **LEAF RULE** — `DashManager`·렌더·view 를 참조하지 않는다 — 을 명시적 계약으로 달고 있다.

모핑 축에 같은 것을 적용하려면 먼저 분리선을 찾아야 한다. **계산부는 이미 떨어져 있다** — `DashMorphingEngine`(213줄)은 `DashManager`·view·렌더 참조가 0건이고 값을 받아 값을 돌려준다. 남아 있는 결합은 다른 곳에 있다: `DashHandlePickingInteraction`(3121줄, `DashManager::Mgr()` 36곳)이 핸들 **데이터**와 기즈모·피커·액터를 한 몸에 갖고 있다.

그 결과가 오늘 관측되는 결합이다. `model/DashOptimizer.cpp:1481` 과 `model/DashModelRunner.cpp:2202` 가 모핑 입력을 얻으려고 `DashMorphingUtils::loadHandlesFromVtp(vtpPath, interaction)` 를 부르고, 그 함수는 `interaction->SetBoxHandles()`(`model/geometry/DashMorphingUtils.cpp:93`)로 GUI live 핸들을 재생성한 뒤 `GetMorphingHandles()` 폴리데이터의 배열을 직접 덮어쓴다(`:96`-`:176`). `SetBoxHandles` 말미는 `ResetCameraClippingRange`·`rw->Render()`·`DashManager::Mgr()->Redraw(false)` 를 부른다(`controller/DashHandlePickingInteraction.cpp:2614`-`:2616`). **계산 경로가 렌더에 물린 객체를 변이한다.**

`docs/ThreadingContract.md` 2절이 `DashHandlePickingInteraction*` 를 워커 진입 금지 타입으로 못박아 뒀지만, 시그니처가 `interaction*` 인 한 그 규약은 주석에 머문다.

## 핵심 질문

1. RW 의 "컨텍스트 → 세션" 분리에 대응하는 모핑 쪽 분리선은 어디인가
2. 떼낼 것을 무엇이라 부르고, 무엇을 이관하고 무엇을 남기는가
3. 데이터 절반이 leaf 가 되기까지 풀어야 할 결합은 몇 건이고 어디인가

## 탐색

### 대응 관계

| RW (`3734897` · `b533191`) | 모핑 (본 문서) |
|---|---|
| `DashAnalysisModelContext` = deck 로드 산물 + 렌더 자원(액터·멀티블록·블록 인덱스) | `DashHandlePickingInteraction` = 핸들 파라미터화 상태 + 기즈모·피커·액터 |
| 떼낸 것: `DashRwSession` — 모듈 인스턴스 1개 + 심볼 uuid 맵. LEAF | 떼낼 것: 핸들 폴리데이터 + 배열 규약 + 그룹 노멀 모드 + 고정면 id + 표면 지오메트리. LEAF |
| 남은 것: GUI 표현만 | 남는 것: 피킹 · 기즈모 · 오버레이 |
| 배치가 `ctx->session()` 으로 RW 절반만 받는다 | 워커·계산 경로가 데이터 절반만 받는다 |
| LEAF RULE 이 스레드 이주를 교착 없이 만든 조건 | 같은 규칙이 워커 진입 규약을 시그니처로 강제하는 조건 |

### 이미 서 있는 것 — 분리선의 증거 3건

1. **렌더 절반이 데이터를 소유하지 않는다.** `DashHandleVisualizer` 가 `InitializePipeline(ren, m_handleGeometry, boundSize)` 로 핸들 폴리데이터를 **주입받는다**(`DashHandlePickingInteraction.cpp:105`).
2. **모핑이 쓰는 두 함수가 이미 인스턴스 독립이다.** `ExtractInitialMorphingPoints`(`:1598`)·`ExtractTargetMorphingPoints`(`:1674`)는 멤버를 하나도 읽지 않고 인자 `inputHandles` 의 배열만 읽는다. 사실상 자유 함수이며 모핑 진입점 전원이 이것을 쓴다.
3. **값 스냅샷 타입이 이미 있다.** `DashMorphingInputSnapshot`·`DashMorphingMeshSet`(`controller/DashMorphingSnapshot.h`). 떼낼 데이터 타입은 이 스냅샷이 복사해 가는 **원본**의 자리에 들어간다.
4. **핸들 부분집합 복제도 이미 인스턴스 독립이다.** `DashGeometryParameterPresentationModel::filterSelectedHandles`(`viewmodel/…PresentationModel.cpp:171`-`:172`)가 인자로 받은 폴리데이터에서 배열 11종을 골라 새 폴리데이터를 만든다(`:186`-`:216`). 위치가 viewmodel 이라는 것만 잘못됐고, 시그니처는 이미 옮길 준비가 된 형태다.

### 이름

레포에 후보가 이미 둘 있고 서로 다르다.

| 후보 | 출처 | 판정 |
|---|---|---|
| `DashHandleDataModel` | `DashHandlePickingInteraction.h:35`-`:36` TODO ("separate handle data and gizmo functions") | 비추천 — `*Model` 충돌 |
| **`DashHandleData`** | 같은 파일 `.cpp:1239`-`:1240` TODO ("핸들 데이터 클래스 만들어서 분리 필요") | **채택** |
| `DashHandleDataSet` | 검토 후보 | `*Set` 이 값 타입을 함의해 live 편집 대상과 어긋난다 |

`*Model` 을 피하는 근거: 이 레포에서 `*Model` 은 Qt item model 을 뜻한다 — `DashDesignVariableModel`·`DashConditionParameterization`·`DashGeometryParameterCAD` 가 `QAbstractTableModel` 파생, `DashGeometryParameter` 가 `QStandardItemModel` 파생이다.

`*Session` 을 쓰면 안 되는 근거: `DashRwSession` 의 "세션" 은 외부 DLL 인스턴스의 **식별과 수명**을 감싸는 이름이다(`open()`/RAII 종료, canonical path 에서 유도한 content uuid 로 deck 동일성 판정 — `DashRwSession.h:54`-`:57`). 핸들 데이터는 DLL 자산이 아니라 GUI 가 편집하는 프로젝트 상태이고, 닫을 대상도 식별자도 없다.

이름 확정 시 **TODO 두 곳을 함께 갱신한다** — 지금 서로 다른 이름 두 개가 남아 있다.

### 분리선 — 멤버

| 이관 (`DashHandleData`) | 헤더 행 | 비고 |
|---|---|---|
| `m_handleGeometry` | `:194` | 배열 11종은 `DashHandleTypes.h:8`-`:20` `HandleArrayNames` 규약 |
| `m_surfaceGeometry` · `m_linearSurfaceGeometry` | `:186` · `:188` | 고정면 id → 점 id 변환의 입력 |
| `m_surfaceLocator` | `:191` | `GetClosestSurfacePoint` 전용 |
| `m_nonDesignSurfaceIds` · `m_constraintSurfaceIds` · `m_constraintUGPointIds` | `:231`-`:233` | 고정점의 **원천**. 오버레이는 이것의 파생 표시일 뿐이므로 함께 가지 않는다 — ⓖ 참조 |
| `m_groupNormalModes` | `:275` | |
| `m_BoxHandles` · `m_CylinderHandles` + `m_hasExternal*` · `m_pending*` | `:267`-`:273` | VTP 로드 경로의 입력 상태 |
| `m_pendingMarchingPlanes` | `:265` | `MarchingPlaneData`(`:40`) = POD |

| 존치 (인터랙션) | 헤더 행 |
|---|---|
| 액터·글리프·소스 9종 (`m_surfaceActor`·`m_selection*`·`m_hover*`·`m_boxHandle*`·`m_cylinderHandle*`·`m_overlayActor`·`m_surfaceEdgeActor`) | `:187`-`:230` |
| 피커 2종 (`m_surfaceSelector`·`m_cellSelector`) · `m_boxWidget` · `m_interactorStyle` | `:218`-`:222` · `:183` |
| 기즈모 4종 (`m_handleGizmos`·`m_planeGizmos`·`m_gizmoGroups`·`m_groupMembers`) | `:277`-`:281` |
| 모드·호버·색 상태 | `:227`-`:237` · `:260` |

### 분리선 — public API

| 구분 | 함수 |
|---|---|
| **데이터** (이관) | `GetMorphingHandles`(`h:114`) · `Extract{Initial,Target}MorphingPoints`(`h:119`-`:120`) · `UpdateHandleRange`(`h:125`) · `Get{,Linear}SurfaceGeometry`(`h:129`-`:130`) · `IsGroupUniformNormal`(`h:134`) · `AppendConstraintSurfaceIds`(`h:168`) · `GetConstraintUGPointIds`(`h:170`) · `GetAllFixed{Surface,Volume}PointIds`(`h:173`-`:174`) · `GetClosestSurfacePoint`(`h:179`) · `SetPending{Box,Cylinder}Handles`(`h:81`-`:87`) · marching plane pending 3종(`h:76`-`:78`) · `InitializeHandleData`·`AddHandleData`(`h:248`-`:249`) |
| **뷰** (존치) | 기즈모 15종(`h:131`-`:153`) · 모드 4종(`h:101`-`:109`) · `Enable`/`Disable`/`Show`/`Hide`(`h:91`-`:96`) · `Execute`(`h:98`) · 선택·오버레이 시각화 6종(`h:158`-`:171`) · `GetConstraintActor`(`h:155`) · 가시성 2종(`h:126`·`h:166`) |
| **혼합** (분해 필요) | `SetGroupNormalMode`(`h:133`) · `Set{Box,Cylinder}Handles`(`h:160`·`h:163`) · `Set{Box,Cylinder}Selection`(`h:161`·`h:164`) · `Finalize`(`h:112`) · `UpdateSurfaceGeometry`(`h:247`) · `GenerateAndShow{Box,Cylinder}Handles`(`h:123`-`:124`) · **`Reset`**(`h:93`) |

> `Reset`(`cpp:1217`)은 이름이 상태 초기화처럼 읽히지만 실제로는 **데이터 변이**다 — `m_surfaceGeometry` 의 `"ConstraintsAndHandles"`·`"GroupIds"` 를 0으로 채우고 `m_hasExternal*` 플래그와 pending 마칭플레인을 지운다. 렌더 호출은 없다. 호출부는 `view/DashMainWindow.cpp:1847`·`:3244` 두 곳이다. 초기 분류에서 `Enable`/`Show` 계열과 묶어 뷰로 넣었던 것을 정정한다.

### 데이터 객체 안에 섞인 뷰 상태 — 판정 필요 2건

멤버 목록을 옮기는 것만으로 끝나지 않는다. **폴리데이터 하나를 쪼갤 수 없으므로**, 그 안의 배열별로 소유 의미를 정해야 한다.

| 배열 | 어디에 | 데이터 성격 | 뷰 성격 | 참조 지점 |
|---|---|---|---|---|
| `"ConstraintsAndHandles"` | `m_surfaceGeometry` point array. 생성 `cpp:302`-`:305` | 비설계면·구속면 판정 = 고정점 산출의 입력. 단 값 `-1.0` 만은 예외 — 프리뷰 중 마커를 화면에서 숨기려는 **뷰 표시**이고 해제 시 0 으로 복원된다(`DashManager.cpp:686`·`:761`-`:771`) | active scalars(`:323`) + 표면 mapper 색 배열(`:327`) | 인터랙션 9곳 + `DashMorphingController.cpp:963`·`:1105` + `DashManager.cpp:677`·`:758` + **view** `DashMorphingSettings.cpp:1023`·`:1189` |
| `HandleArrayNames::SELECTION` | `m_handleGeometry` | 없음 — 선택은 편집 UI 상태다 | active scalars(`:145`) + `DashHandleVisualizer` 색 배열(`:85`·`:116`·`:123`·`:216`·`:381`) | 인터랙션 2곳(`:744`·`:811`) |

판정 제안:

- **`SELECTION` 은 뷰다.** 데이터셋이 배열을 만들되 의미는 뷰 소유로 문서화하고, 계산·워커 경로가 이 배열을 읽지 않음을 규약으로 못박는다. 모핑 실행부가 핸들에서 읽는 것은 `STATUS`·`HANDLETYPE`·`BOUND`·`L2G`·`LOWER`·`UPPER`·`GROUPID`·`HANDLENORMAL` 이다.
- **`ConstraintsAndHandles` 는 양쪽이다.** 표면 폴리데이터가 데이터 쪽으로 가면 이 배열도 함께 가고, 색 배열 지정(`:327`)만 뷰에 남는다. 다만 view(`DashMorphingSettings`)가 이 배열을 **직접** 쓰는 2곳은 데이터 API 경유로 바꿔야 한다 — 그대로 두면 뷰가 데이터 배열을 직접 만지는 결합이 남는다.

### 배열 규약의 실제 소비 범위 — 7파일 · 156곳

`HandleArrayNames` 소비를 파일별로 세면 배열 규약이 어디까지 새 나갔는지 나온다.

| 파일 | 곳 | 계층 |
|---|---|---|
| `controller/DashHandlePickingInteraction.cpp` | 74 | 분리 대상 |
| `view/DashGeometryParameterWidget.cpp` | 28 | **뷰** |
| `controller/DashHandleVisualizer.cpp` | 23 | 렌더 |
| `viewmodel/DashGeometryParameterPresentationModel.cpp` | 22 | **뷰모델** |
| `controller/DashMorphingDoeExecutor.cpp` | 6 | 계산 |
| `view/overlay/DashMorphingSettings.cpp` | 2 | **뷰** |
| `controller/DashHandleTypes.h` | 1 | 정의 |

**UI 계층(뷰 + 뷰모델)이 52곳이다.** 배열 이름을 알고 있다는 것은 배열 레이아웃 계약을 알고 있다는 뜻이므로, 데이터 타입이 규약을 소유한다는 말은 이 52곳이 무엇을 경유할지 정한다는 말과 같다. 전부 접근자로 감쌀 필요는 없지만 — 읽기 전용 소비는 폴리데이터를 그대로 넘겨도 된다 — **쓰기와 레이아웃 가정(튜플 개수·컴포넌트 수)은 데이터 타입 안에 있어야 한다.**

### 직렬화 — 핸들 VTP 라운드트립이 4계층에 흩어져 있다

핸들은 `.vtp` 로 저장·복원되는데 그 코드가 계층을 가로질러 7곳에 있다.

| 방향 | 위치 | 계층 |
|---|---|---|
| 쓰기 | `viewmodel/DashGeometryParameterPresentationModel.cpp:22`(`saveMorphingSettings:325`) · `view/DashGeometryParameterWidget.cpp:64` | 뷰모델 · 뷰 |
| 읽기 | `controller/DashMorphingDoeExecutor.cpp:998` · `controller/DashManager.cpp:54` · `model/DashModelRunner.cpp:37` · `model/geometry/DashMorphingUtils.cpp:53` · `view/DashGeometryParameterWidget.cpp:2622` | 컨트롤러 · 모델 · 뷰 |

직렬화는 배열 규약을 가장 강하게 아는 코드다(배열 하나가 빠지면 라운드트립이 조용히 깨진다). ⓕ 의 "VTP 로더 2벌" 은 이 표의 일부였고, 실제 범위는 **읽기 5곳 · 쓰기 2곳**이다. 데이터 타입의 자연스러운 책임이며, 여기서 규약을 한 곳으로 모으면 ⓕ 와 위 156곳의 상당 부분이 함께 줄어든다.

### 자료형 자체를 손볼 후보 5건

| 대상 | 지금 | 제안 |
|---|---|---|
| `HandleArrayNames`(`DashHandleTypes.h:8`) | 상수가 있는데 `"SelectionScalars"` 리터럴이 인터랙션에 6곳 하드코딩(`:1288`·`:1320`·`:2604`·`:2667`·`:2711`·`:2771`) | 상수로 통일. 배열 규약을 데이터 타입이 소유하려면 리터럴이 남아 있으면 안 된다 |
| `m_surfaceGeometry` 의 `"GroupIds"`(`Reset:1226`) | 핸들 폴리데이터의 `HandleArrayNames::GROUPID` 와 **다른 배열인데 이름이 같다** | 이관 전 이름 구분. 같은 이름 두 벌은 분리 후 혼동 원인 |
| `BoxHandleInfo`(`DashHandleTypes.h:3`) | `position[3]`+`vector[3]`. 실린더 핸들도 같은 타입을 쓴다(`SetCylinderHandles`) | 이름만 오해를 낳는다. 이관 시 재검토(선택) |
| `BoxHandleInfo` · `MarchingPlaneData` 의 raw 배열 (`double l2g[16]`·`localBounds[6]`) | C 배열이라 복사·비교·경계 검사가 수동이다 | `std::array` — 값으로 워커에 넘기는 타입이므로 복사 의미가 명확한 편이 낫다 (선택) |
| `m_savedBaseColor`(`h:263`) | `double*` raw 포인터. **`.cpp` 사용 0건** — 선언만 남아 있다 | 사전 존재 dead 이므로 본 작업에서 건드리지 않는다. 별건으로 삭제 |

**반대쪽 참조 조치**: 뷰 절반이 핸들 배열을 상시 읽는다(기즈모 동기화가 `HANDLENORMAL`·`GROUPID`·`LOWER`·`UPPER`·`BOUND`·`L2G`). 데이터 타입은 non-owning 읽기 접근자를 노출하면 되고, **역방향 back pointer 는 두지 않는다** — 데이터가 인터랙션을 참조하는 순간 leaf 가 깨진다. 이 규칙 하나가 RW 의 LEAF RULE 과 같은 자리다.

### 풀어야 할 결합 ⓐ — 데이터 쓰기 말미의 기즈모 동기화

`AddHandleData`(`cpp:149`-`:169`)가 배열 11개에 값을 넣고 **같은 함수 말미에서** `EnsureHandleGizmoCount`(`:167`)·`SyncHandleGizmo`(`:168`)를 부른다. 데이터가 뷰를 호출하는 방향이라 leaf 가 성립하지 않는다.

### 풀어야 할 결합 ⓑ — `DashManager` 싱글톤 되부름

전체 36곳 중 **데이터 절반에 걸린 것은 4곳**이다. `AddHandleData` 안에만 있지 않다.

| 위치 | 소유 함수 | 되부르는 것 | 주입 형태 |
|---|---|---|---|
| `cpp:151` | `AddHandleData:149` | `GetMorphingSingleStep()` | 인자 — 호출 시점 값이 필요 |
| `cpp:172` | `UpdateSurfaceGeometry:171` | `GetInputVTU()` | 생성 시 1회 주입 |
| `cpp:2916` | `UpdateNonDesignFromUG:2914` | `GetInputVTU()` | 같음 |
| `cpp:3064` | `GetAllFixedVolumePointIds:3062` | `GetInputVTU()` | 같음 |

나머지 32곳은 전부 뷰 절반이다 — `Redraw`·`GetHandleVisualizer`·`GetRenderer`·기즈모 크기용 `GetModelBoundSize`·`UpdatePreviewMorphing`·`GetGeometryParameterWidget`·`GetPreviewType`. 존치 클래스에 남으므로 손대지 않는다.

### 풀어야 할 결합 ⓒ — 혼합 함수 분해

| 함수 | 스팬 | 섞인 것 |
|---|---|---|
| `SetGroupNormalMode` | `cpp:1873`-`:1899` (27줄) | `m_groupNormalModes` 쓰기 + 기즈모 축 활성 6줄 + `Redraw` |
| `SetBoxHandles` | `cpp:2562`-`:2621` | 핸들 재생성 + 말미 렌더 3줄(`:2614`-`:2616`) |
| `Finalize` | `cpp:1241`-`:1596` (356줄) | 핸들 확정 + `GetHandleVisualizer`(`:1250`) · `Redraw`(`:1595`) |
| `UpdateSurfaceGeometry` | `cpp:171`-`:463` (293줄) | 표면 추출·노멀·double 승격·locator(데이터) + 선택/호버 글리프·액터 생성(뷰) + `GetMidNodeMap` 기반 엣지 필터링(`:382`) |

앞 둘은 30줄 이하라 분해가 자명하다. **실질 관문은 `UpdateSurfaceGeometry` 다** — 293줄 안에서 데이터 산출과 액터 생성이 교차하고, 액터가 데이터 산출의 중간 결과(글리프 입력)에 물려 있어 순서 의존이 있다.

### 풀어야 할 결합 ⓓ — 인터랙션 밖에서 데이터를 직접 잡는 41곳

`GetMorphingHandles()`·`Get{,Linear}SurfaceGeometry()` 호출부를 인터랙션 자신을 빼고 세면 41곳이다. 분리 후 이들이 무엇을 경유할지 정하는 것이 이관 목록보다 큰 일이다.

| 소유자 | 곳 | 성격 |
|---|---|---|
| `view/DashGeometryParameterWidget.cpp` | 13 | 읽기 + **쓰기**. `LOWER`/`UPPER` 직접 `SetComponent`(`:1608`-`:1609`·`:2366`·`:2395`) + `handles->Modified()` 6곳(`:1620`·`:1681`·`:1788`·`:2369`·`:2399`·`:2480`) |
| `controller/DashMorphingController.cpp` | 12 | surface 읽기 + `ConstraintsAndHandles` 쓰기 2곳(`:963`·`:1105`) |
| `controller/DashManager.cpp` | 8 | 프리뷰 경로 + `ConstraintsAndHandles` 쓰기(`:677`·`:758`) |
| `controller/DashHandleVisualizer.cpp` | 3 | ⓔ 참조 |
| `model/geometry/DashMorphingUtils.cpp` | 2 | 계산 경로(`:94`·`:179`) |
| `view/DashMainWindow.cpp` · `view/overlay/DashMorphingSettings.cpp` | 1 + 1 | |

**읽기 41곳이 아니라 쓰기가 섞여 있는 41곳**이라는 점이 중요하다. 읽기만이면 non-owning 접근자로 끝나지만, view 가 배열을 직접 쓰는 4곳은 데이터 타입의 mutation API 로 올려야 한다.

### 풀어야 할 결합 ⓔ — `DashHandleVisualizer` 가 주입받은 것을 전역으로 다시 얻는다

`InitializePipeline(ren, m_handleGeometry, boundSize)` 로 핸들 폴리데이터를 **주입받으면서**, `:209`·`:250`·`:338` 에서는 `DashManager::Mgr()->GetHandlePickingInteraction()->GetMorphingHandles()` 로 다시 얻는다. 싱글톤 3단 체인이다.

원인은 헤더에 있다 — **`DashHandleVisualizer` 는 주입받은 폴리데이터를 멤버로 보관하지 않는다.** 멤버 16개가 전부 렌더 객체(LUT·액터·글리프·소스)와 자기 소유 폴리데이터(`m_morphingArrowGeometry`·`m_edgeGeometry`·`m_mpMarkerPolyData`)다. 그래서 나중에 핸들 데이터가 필요해진 함수 3곳이 싱글톤으로 되돌아간 것이다.

따라서 수정은 "주입된 것을 쓴다" 가 아니라 **멤버 추가 + 대입 1 + 치환 3** 이다. 그래도 선행 요구가 0이고 이 클래스의 싱글톤 사용은 총 6곳뿐이다. 지금은 같은 객체를 가리키므로 증상이 없지만, 데이터 소유자가 바뀌는 순간 이 3곳이 조용히 다른 인스턴스를 볼 수 있다.

부수 관찰: 이 클래스는 자기 배열 이름을 `static constexpr const char*`(`h:53`-`:54` `ARROW_SCALE`·`ARROW_DIRECTION`)로 두는데, `HandleArrayNames`(`DashHandleTypes.h:8`)는 헤더 안 `static const char* const` 묶음이다. 같은 목적에 두 관례가 공존한다 — 규약을 데이터 타입으로 옮길 때 하나로 맞춘다.

### 풀어야 할 결합 ⓕ — 쓰기 경로 이중화와 데이터 규칙 복제

| 항목 | 두 벌 |
|---|---|
| 핸들 range 갱신 | `UpdateHandleRange`(`cpp:1828`)가 있는데 view 가 같은 일을 배열 직접 쓰기로 한다(`DashGeometryParameterWidget.cpp:2366`·`:2395`) |
| 초기 range = ±`GetMorphingSingleStep()` 규칙 | `AddHandleData:151` 과 `DashGeometryParameterWidget.cpp:1608`-`:1609` 두 곳 |
| VTP → 핸들 로더 | `DashMorphingUtils.cpp:40`(live 인터랙션에 싣는다) 과 `DashMorphingDoeExecutor.cpp:990`(스냅샷 사본에 싣는다) |

`GetMorphingSingleStep()` 소비 6곳 중 3곳은 스핀박스 step 설정이라 순수 UI 이고(`DashGeometryParameterWidget.cpp:527` · `DashMorphingSettings.cpp:720`·`:733`), **데이터 규칙으로 쓰는 곳이 2곳**이다. 그 규칙은 데이터 타입이 소유해야 한다.

### 풀어야 할 결합 ⓖ — 고정점 상태가 두 소유자에 쪼개져 있다

`DashManager::m_hiddenFixedIds`(`DashManager.h:62`, 사용 7곳 — `:511`·`:560`·`:679`·`:683`·`:696`·`:761`·`:771`)와 인터랙션의 `m_nonDesignSurfaceIds`·`m_constraintSurfaceIds`(→ `GetAllFixedSurfacePointIds`)가 **같은 개념**이다: 모핑 시 제자리에 고정할 점.

`DashManager` 쪽은 마커 샘플링 결과를 담고 프리뷰 2경로가 소비하며, 인터랙션 쪽은 사용자가 지정한 비설계면·구속면에서 유도된다. 분리 시 한 소유자로 합치는 것이 맞고, 합칠 곳은 `DashHandleData` 다 — 프리뷰·QC·배치가 모두 이 둘을 함께 필요로 한다.

#### 합치기 전에 갈라야 할 것 — 원천 · 표시 · 계산 3층위

"같은 개념" 은 **원천이 같다**는 뜻이지 같은 자료가 아니다. 셋을 층위로 갈라야 이관 대상이 정해진다. 원천만 상태이고 나머지 둘은 파생물이다.

| 층위 | 실체 | 성격 | 이관 판정 |
|---|---|---|---|
| **원천** — 구속 지정 | 셀 id 집합 2종 — `m_constraintSurfaceIds`(사용자가 박스 선택으로 찍은 면) · `m_nonDesignSurfaceIds`(UG `NonDesignMask` 에서 유도, `UpdateNonDesignFromUG:2914`) | 순수 데이터. 렌더 무관 | **데이터** — 이미 이관 목록(`h:231`-`:233`) |
| **표시** — 구속 오버레이 | `UpdateNonDesignAndConstraintOverlay:2809` 가 두 집합을 `vtkExtractSelection` 으로 뽑아 반투명 액터로 겹쳐 그림 | 소비만 한다. 데이터를 만들지 않음 | **뷰** — 존치 |
| **계산** — 고정점 | 원천 셀의 구성 점 합집합(`GetAllFixedSurfacePointIds:3026`)을 모핑 인자 형태로 환산한 것 | 계산 입력 | **데이터** — 환산 함수까지 함께 |

오버레이와 고정점은 같은 원천의 형제 파생물이고, 오버레이는 고정점 산출에 관여하지 않는다. "오버레이" 라는 이름 때문에 구속 원천까지 뷰로 분류하기 쉬운데, 뷰인 것은 액터 조립 한 겹뿐이다.

#### 고정점이 엔진에 닿는 경로가 둘이다

원천 하나가 서로 다른 두 인자로 엔진에 들어간다. ⓖ 의 통합은 이 둘의 산출지를 함께 옮기는 것을 뜻한다.

| 경로 | 환산 | 엔진 인자 | 생성 시점 |
|---|---|---|---|
| 마커 샘플링 | 고정점 중 **핸들 커널 반경 안**만 포아송 간격으로 추림 (`NonDesignUtils::GenerateMarkerPointsFromSurfaceIds:350`) | `SetInitialHandles(initialPoints)` 배열에 append — 프리뷰 `DashManager.cpp:669`·`:714`, 배치 `DoeExecutor:739`·`:773` | 실행 때마다 재생성 (핸들 위치에 의존) |
| volume 인덱스 | 표면 점 id → `vtuIds` 배열로 볼륨 점 id (`GetAllFixedVolumePointIds:3062`) | `RunVolumeMorphing(..., volumeFixedIds, ...)` (`DoeExecutor:786`-`:787`) | Set Design Variable 때 VTP fieldData `AllFixedVolumeIds` 로 굳음 (`PM:313`-`:319`) |

**엔진 인터페이스에서 고정점은 "변위 0 인 핸들" 이다.** 배치는 마커 좌표를 initial·target 양쪽에 같은 값으로 넣는다(`DoeExecutor:747`-`:753`). 별도 개념이 아니라 핸들 배열의 특수값이므로, 데이터 타입이 핸들과 고정점을 함께 소유하는 것이 인자 형태와도 맞는다.

다만 고정점은 **핸들 폴리데이터의 점으로 승격되지 않는다** — `Finalize` 산물에 없고, 남는 흔적은 표면 스칼라 `-1.0`(프리뷰 중 임시 표시, `DashManager.cpp:686`, 해제 시 0 복원)과 VTP **fieldData** 뿐이다. 이관 시 "핸들 점 배열" 과 "고정점 목록" 을 같은 칸에 넣지 않아야 한다.

#### 영속화가 비대칭이다 — 원천은 저장되지 않고 파생물만 저장된다

`m_constraintSurfaceIds` 를 쓰는 writer 가 레포에 없다(`Morphing.constraints` 는 파서만 존재). `.vtp` 에 나가는 `AllFixedVolumeIds` 는 저장 시점에 굳은 파생물이고, 되읽을 때 원천을 재구성하지 못한다. 재로드하면 오버레이가 사라지고 구속 표를 이어 편집할 수 없는데, 마커 샘플링은 그 시점에 원천을 다시 요구한다 — 빈 집합이면 마커 0개가 된다.

데이터 타입이 서면 **원천을 직렬화 대상으로 올릴 자리가 생긴다.** 위 "직렬화" 절의 배열 목록 대조에 이 항목을 함께 넣는다.

> **브랜치 차이 1건.** 본 문서 기준(`66c126c`)에서 배치 경로는 스냅샷을 경유한다 — `DashMorphingInputSnapshot::fixedSurfacePointIds`(`controller/DashMorphingSnapshot.h`)를 `DashManager.cpp:439` 가 GUI 스레드에서 채우고 `DoeExecutor:738` 이 그 값만 읽는다. **고정점의 값 스냅샷 필드가 이미 존재한다는 것**이 이 개념을 데이터 절반으로 보내는 직접 근거다(위 "증거 3건" 의 스냅샷 항목과 같은 자리). 반면 `dev` @ `ac6e4e6` 의 같은 지점은 `interaction->GetAllFixedSurfacePointIds()` 직접 호출이다 — 배치가 픽킹 객체를 되부르는 형태이며, 통합 시 스냅샷 쪽으로 수렴시켜야 한다.

### 인접 혼합체 — `DashMorphingController`

같은 성격의 혼합이 하나 더 있다. `DashMorphingController`(1498줄, `DashManager::Mgr()` 25곳, surface 직접 접근 12곳)가 프리뷰 액터 3종(`m_marchingPlanePreviewActor`·`m_physicsPreviews`·`m_clusterPreviewActor`)과 **순수 생성 알고리즘**(`collectSurfaceSeedNodeIds`·`calculateSupportRadius`·`selectHandlesGreedyByUnit`·`createCluster`·`wendlandC2`)을 함께 갖고 있다.

생성 알고리즘은 표면 데이터에 대한 순수 계산이라 자유 함수로 떼는 데 걸림이 없고, **선례가 이미 레포에 있다** — `controller/DashNonDesignUtils.cpp` 는 `DashManager::Mgr()` 호출이 **0건**인 자유 함수 묶음이고 프리뷰·QC 양쪽이 쓴다(`DashManager.cpp:671` · `DashGeometryParameterWidget.cpp:1341`).

본 문서 범위 밖이지만 같은 분리선이므로 함께 등재한다. 순서는 `DashHandleData` 다음이다 — 생성 알고리즘의 출력이 곧 핸들 데이터라, 데이터 타입이 먼저 서야 인자 형태가 정해진다.

### 소유자 결정 — 새 타입을 누가 들 것인가

`DashHandlePickingInteraction` 은 `vtkCommand` 파생이고 `vtkSmartPointer` 로 수명이 관리된다(`New()` · `DashManager::m_handlePicking`). 새 데이터 타입을 vtkObject 파생으로 만들 이유는 없다 — 담는 것이 vtk 객체일 뿐 자신은 콜백도 파이프라인 요소도 아니다.

소유 구조는 이미 답을 시사한다. `DashManager` 가 인터랙션(`m_handlePicking`)과 비주얼라이저(`m_handleVisualizer`)를 **둘 다** 소유하고, 두 클래스가 같은 핸들 폴리데이터를 봐야 한다. 따라서 **`DashManager` 가 `DashHandleData` 를 소유하고 두 소비자에 주입**하는 형태가 현재 구조와 맞는다. ⓔ 가 그 형태를 이미 절반 하고 있다(주입 시점은 있고, 보관과 재사용이 없다).

### 목표 계약과 검증 기준

분리의 목적이 워커 안전이므로 **데이터 타입의 스레드 계약을 먼저 못박아야 한다.** 지금 문서에 없던 항목이다.

| 항목 | 계약 |
|---|---|
| 소유·변이 | GUI 스레드 전용. 데이터 타입 자체를 워커로 넘기지 않는다 |
| 워커 입력 | `DashMorphingInputSnapshot` 같은 **DeepCopy 값 스냅샷만**. 스냅샷 생성은 GUI 스레드 |
| 참조 방향 | 데이터 → 뷰 참조 0. 뷰 → 데이터는 읽기 접근자 + 명시적 mutation API |

leaf 여부는 기계적으로 판정할 수 있다. 단계별 수용 기준:

| 단계 | 판정 |
|---|---|
| ⓔ | `DashHandleVisualizer.cpp` 의 `DashManager::Mgr()` 6곳 → 3곳 |
| ⓐ·ⓑ | 데이터 함수에서 `DashManager::Mgr()` 0건 · 기즈모 함수 호출 0건 |
| 타입 신설 | 새 헤더에 `DashManager`·`vtkActor`·`vtkRenderer`·`DashGizmo`·`view/` include 0건. `.cpp` 에 `DashManager::Mgr()` 0건 |
| 규약 이관 | `HandleArrayNames` 소비 156곳 중 **쓰기·레이아웃 가정**이 데이터 타입 밖에 0건 |

**회귀망이 없다는 것을 전제로 잡아야 한다.** `tests/` 에는 `tst_job_state`·`tst_line_assembler`·`tst_process_runtime`·`tst_thread_affinity` 4개와 `e2e/` 가 있고, **핸들·인터랙션·모핑 단위 테스트는 0건**이다. 그래서 ⓐ~ⓖ 의 검증은 지금 수동 시나리오뿐이다.

역으로 이것이 분리의 부수 이득이다 — 데이터 타입이 leaf 가 되는 순간 렌더러 없이 인스턴스를 만들 수 있으므로 **핸들 데이터가 처음으로 단위 테스트 가능해진다.** 타입 신설 커밋에 최소 테스트 3개(핸들 추가 후 배열 튜플 수 일치 · 고정면 id → 점 id 변환 · VTP 라운드트립)를 붙이는 것이 맞다.

## Q&A

### Q. RW DLL 접근을 한 쌍의 경계 타입으로 좁힌 것(`3734897`)을 모핑 DLL 에 그대로 하면 작업 내용이 명확한가

명확하지 않다. 그 커밋을 성립시킨 전제가 모핑에는 대부분 없고, 일부는 **이미 반대 방향으로 규약이 서 있다**.

| `3734897` 이 기댄 사실 | 모핑 쪽 대응물 |
|---|---|
| `IRWModule` 을 여러 호출부가 공유·직접 소유 | 없다. 프리뷰 1개(`DashManager.cpp:72`) + 배치 per-Job 1개(`DashMorphingDoeExecutor.h:96`)로 이미 분리 |
| 세션 = deck 식별 + 수명 → RAII 종료 필요 | 없다. operator 상태는 커널 반경과 초기 핸들 둘뿐이고 샘플마다 재설정된다 |
| `types::Set` 의 `std::function` resolver 가 경계를 넘는 문제 | 없다. 입출력이 `vtkPoints`/`vtkUnstructuredGrid` 값 계열 |
| 단일 스레드 봉인이 이득 | 반대다. DLL 이 자체 다중 스레드 솔버를 돌린다(`DashMorphingEngine.cpp:53` `SetSolverNumberOfThreads(16)`) — 액터 한 스레드에 몰면 배치가 직렬화된다 |

`docs/ThreadingContract.md` 4절이 이미 모핑 엔진을 **per-Job 인스턴스로 공유 금지**로 못박고 있다(3단 시퀀스가 비원자라 공유하면 "조용한 오답"). 액터는 반대로 단일 소유자에 몰아넣는 구조다.

그대로 옮길 수 있는 것은 **경계 일원화**뿐이다. 지금 모핑 DLL 접근 지점은 4갈래다.

| 접근 지점 | 위치 | 성격 |
|---|---|---|
| 프리뷰 엔진 (GUI 소유) | `DashManager.cpp:72` 소유, `486`·`529`·`579`·`671`·`714` 호출 | live |
| 같은 엔진을 view 가 직접 잡음 | `view/DashGeometryParameterWidget.cpp:754`·`1279`·`1352`·`2089` | 경계 누출 |
| 배치 엔진 (per-Job) | `DashMorphingDoeExecutor.cpp:773`·`786` | live |
| 원시 operator 직접 생성 | `model/geometry/DashMorphingUtils.cpp:188` ← `DashOptimizer.cpp:1479`, `DashModelRunner.cpp:2199` | 실행에 닿지 않는다 — `performMorphingAndExport` 가 `:278` 에서 널 검사만 하고 이후 참조하지 않으며, 실제 실행 주체는 `:284` 의 지역 executor 다 |

`SetInitialHandles` → `RunVolumeMorphing` 2단 시퀀스가 view · `DashManager` · engine 세 층에 흩어져 있다 — `DashGeometryParameterWidget.cpp:1352` 가 엔진에 초기 핸들을 심고 `:1355` 에서 `DashManager::RunVolumeMorphing` 을 부른다. 그 사이가 열려 있고, 커널 반경도 view 가 엔진에서 직접 읽는다(`:1341`). 이것을 단일 호출로 닫는 것이 RW 커밋에서 옮겨올 수 있는 부분이고, 액터화는 아니다.

### Q. 그러면 모핑도 계산 쪽과 뷰 쪽을 뗄 수 있는가. 무엇을 떼는 것이라고 해야 하는가

뗄 수 있다. 단 **계산부는 이미 떨어져 있다** — `DashMorphingEngine` 은 `DashManager`·view·렌더 참조가 0건이다. `DashAnalysisModelContext` 가 세션을 들고 있던 자리에 대응하는 것은 엔진이 아니라 `DashHandlePickingInteraction` 이고, 떼는 것은 **핸들 데이터**다. 이름은 `DashHandleData` — 근거는 위 "이름" 절.

즉 이 문서의 분리는 모핑 계산부를 떼는 작업이 아니라, **계산부가 입력을 얻으려고 렌더에 물린 객체를 만지는 경로를 없애는** 작업이다.

### Q. 핸들 폴리데이터·배열 규약·그룹 노멀 모드·고정면 id 를 leaf 로 떼고 피킹·기즈모·오버레이를 남기면 되는가

방향은 맞다. 다만 이관 목록에 **4항 추가**가 필요하다.

| 추가 항목 | 왜 데이터 쪽인가 |
|---|---|
| `m_surfaceGeometry` · `m_linearSurfaceGeometry` | 고정면 id 가 셀 id 라서, 점 id 로 바꾸려면 표면 셀을 순회해야 한다(`GetAllFixedSurfacePointIds:3026`). 표면 없이는 고정면 id 가 쓸 수 없는 값이다 |
| `m_surfaceLocator` | `GetClosestSurfacePoint` 가 이것만 쓴다 |
| `m_BoxHandles`·`m_CylinderHandles` + `m_hasExternal*`·`m_pending*` | VTP 로드 경로의 입력 상태. `SetBoxHandles` 가 이걸 읽어 핸들을 재생성한다 |
| `m_pendingMarchingPlanes` | `MarchingPlaneData` 는 POD |

그리고 멤버 이동만으로 끝나지 않는다 — 위 "데이터 객체 안에 섞인 뷰 상태" 2건의 소유 판정과 "자료형 자체를 손볼 후보" 5건이 함께 붙는다. 특히 `HandleArrayNames` 리터럴 6곳과 같은 이름 배열 두 벌(`GroupIds`)은 **분리 전에** 정리하는 편이 낫다. 분리 후에는 두 클래스에 걸쳐 있어 고치기가 더 어렵다.

이관 목록에는 함수도 하나 추가된다 — `DashGeometryParameterPresentationModel::filterSelectedHandles`(`viewmodel/…PresentationModel.cpp:171`)는 핸들 부분집합 복제이므로 데이터 타입의 연산이다. 이미 폴리데이터를 인자로 받는 형태라 옮기는 데 걸림이 없다.

### Q. `AddHandleData` 를 값만 바꿔 반환하고 호출부가 `EnsureHandleGizmoCount`+`SyncHandleGizmo` 를 부르게 하면 되는가

맞다. 반환값은 삽입 인덱스(`vtkIdType`)다. 다만 **값 넣기는 전부 데이터 쪽**이고 호출부는 기즈모만 잇는다 — 호출부가 값을 나눠 넣는 형태가 아니다.

그리고 호출부 3곳(`:1410`·`:1498`·`:1525`)을 다 고칠 필요가 없다. 인터랙션에 `AddHandleData` 를 이름 그대로 남기고 몸통을 `m_data->AppendHandle(...)` → 기즈모 동기화 순서로 두면, 데이터는 뷰를 모르게 되고 호출부는 무변경이다. 새 이름은 데이터 쪽에만 필요하다.

### Q. 싱글톤 되부름은 필요한 값만 주입하면 되는가. 전부 `AddHandleData` 안에 있는가. 케이스별로 함수를 나눠야 하는가

`AddHandleData` 안에만 없다 — 위 ⓑ 표의 4곳이다. `GetInputVTU()` 3곳은 같은 대상이므로 **한 번 주입하면 3곳이 함께 정리된다.** `GetMorphingSingleStep()` 은 호출 시점 값이 필요하므로 인자가 맞고, ⓐ 의 시그니처 변경과 같은 커밋에 들어간다.

싱글톤 때문에 함수를 나눌 필요는 없다. 나눠야 하는 이유는 ⓒ 혼합 함수이고 그것은 별 사안이다.

### Q. 모델이 교체되는 경우는 언제인가. 재생성과 setter 중 무엇이 맞는가. deck 마다 id 를 부여해 맵으로 소유하고 핸들로 접근하는 방식은 어떤가

**교체 지점은 1곳이다.** `DashManager::SetInputVTU`(`controller/DashManager.cpp:285`-`:326`)이고, 프로덕션 호출부는 `view/DashGeometryParameterWidget.cpp:2124` 하나다. `view/DashMainWindow.cpp:993` 주석이 "모듈 재진입은 지오메트리를 다시 로드하지 않는다" 를 명시한다.

그 함수가 이미 전체 재생성 캐스케이드를 돈다 — double 승격 → 선형화 또는 `m_originalQuadraticCells`/`m_midNodeMap` 정리 → `ComputeModelBoundSize`·`ComputeMorphingSingleStep` → `InitializeHandlePicking()`(`:319`) → appearance 재적용. `InitializeHandlePicking`(`cpp:94`)은 `UpdateSurfaceGeometry`·`InitializeHandleData`·visualizer 파이프라인을 다시 세운다(`:101`-`:105`).

**따라서 재생성이 정답이고 setter 는 불필요하다.** 재생성 경로가 이미 서 있으므로 생성 시 주입이 그 위에 자연히 얹힌다. setter 를 두면 "그리드만 갈리고 핸들 데이터는 남는" 중간 상태가 새로 생긴다 — 지금 없는 상태다.

**deck 별 id 맵은 지금 불필요하다.** 근거 둘:

1. `DashManager` 가 `m_inputVTU` 를 1개만 들고 GUI 는 한 번에 한 모델을 보인다. 핸들 세트도 그 모델 하나에 붙는다.
2. deck 다중 소유·식별은 **RW 축에 이미 있다** — 레지스트리가 canonical path 로 키를 잡고 content uuid 를 그 경로에서 결정론적으로 유도한다(`DashRwSession.h:54`-`:57`). 핸들 쪽에 두 번째 맵을 세우면 같은 문제를 두 벌로 푸는 것이 된다.

필요해지는 조건은 명확하다: **deck 을 오가며 각자의 핸들 세트를 살려야 할 때.** 지금은 살아남지 않는다 — 재로드가 `InitializeHandlePicking` 을 다시 부른다. 그 요구가 생기면 데이터 타입을 값 타입으로 두고 소유자에 `QHash<식별자, DashHandleData>` 를 얹으면 되고, 그때 RW 의 키 유도 방식을 그대로 재사용하는 것이 맞다. 지금 만들면 사용처 0인 추상이다.

> **재생성 경로에서 먼저 확인할 것 1건.** `InitializeHandleData`(`cpp:108`)는 `m_handleGeometry` 가 이미 있으면 **점은 그대로 두고** `CreateArray` 로 배열만 다시 `AddArray` 한다(`:118`-`:129`). VTK 는 같은 이름 배열을 교체하므로, 두 번째 `SetInputVTU` 이후 **점 N개 + 튜플 0개** 상태가 만들어진다(코드 읽기 기준 · 런타임 미확인). 이후 `AddHandleData` 의 `InsertNextTuple` 은 점 인덱스와 어긋난다. 재생성 방식을 택하면 이 지점을 함께 정리해야 하고, 데이터 타입 생성이 곧 초기화가 되면 이 결함은 구조적으로 사라진다.

### Q. 혼합 함수 분해는 따로 뒤로 미뤄 상세 분석·설계하는 것이 맞는가

맞다. ⓒ 4개 중 `SetGroupNormalMode`(27줄)와 `SetBoxHandles`(60줄) 말미는 지금 분해할 수 있지만, `Finalize`(356줄)와 `UpdateSurfaceGeometry`(293줄)는 별건으로 떼는 편이 맞다. 두 함수가 본 분리 비용의 대부분이고, "기능별로 떼서 각각 호출" 로 끝나지 않는다 — 액터가 데이터 산출의 중간 결과에 물려 순서 의존이 있다.

그 후속 설계가 산출해야 하는 것:

- `UpdateSurfaceGeometry` 293줄에서 액터가 참조하는 중간 결과 목록과 그 확정 순서
- 엣지 필터링(`:382`, `GetMidNodeMap` 소비)이 데이터인지 엣지 액터 전용인지 판정
- `Finalize` 356줄의 데이터 확정 / 렌더 통지 경계
- 분해 후에도 유지돼야 하는 호출 순서 계약 (지금은 함수 내부 순서에 암묵적으로 들어 있다)

### Q. 추가로 분리·형 변환·함수 분할·전역 되부름 제거가 필요한 곳은 더 없는가

2차 스윕에서 4건이 더 나왔다. ⓐⓑⓒ 만으로는 부족하다.

| # | 항목 | 성격 | 지금 가능한가 |
|---|---|---|---|
| ⓓ | 인터랙션 밖 데이터 직접 접근 41곳 — 그중 **쓰기 4곳**(view 가 `LOWER`/`UPPER` 를 직접 `SetComponent`) | 분리 후 경유 경로 결정 | 분리와 동시 |
| ⓔ | `DashHandleVisualizer` 가 주입받은 폴리데이터를 싱글톤 3단 체인으로 다시 얻는다 (`:209`·`:250`·`:338`) | 전역 되부름 제거 | **지금 · 독립** |
| ⓕ | 쓰기 경로 이중화 3건 — range 갱신 2벌, 초기 range 규칙 2벌, VTP 로더 2벌 | 중복 제거 | 부분적으로 지금 |
| ⓖ | 고정점 상태가 `DashManager::m_hiddenFixedIds` 와 인터랙션 두 곳에 쪼개져 있다 | 소유 통합 | 분리와 동시 |

그리고 **범위 밖이지만 같은 분리선인 것 1건**: `DashMorphingController`(1498줄, 싱글톤 25곳)가 프리뷰 액터 3종과 순수 생성 알고리즘 5종을 함께 갖고 있다. `DashNonDesignUtils`(싱글톤 0건 자유 함수)가 그 목표 형태의 선례다. 순서는 `DashHandleData` 다음이다 — 생성 알고리즘의 출력이 곧 핸들 데이터라 데이터 타입이 먼저 서야 인자 형태가 정해진다.

**형 변환 후보**는 3건에서 5건으로 늘었다 — 기존 3건(`HandleArrayNames` 리터럴 · `GroupIds` 이름 중복 · `BoxHandleInfo` 명칭)에 raw 배열 `std::array` 화와 사용 0건 멤버 `m_savedBaseColor` 가 붙는다. 여기에 형 변환은 아니지만 같은 급의 결정 하나 — **새 타입을 vtkObject 파생으로 만들지 않고 `DashManager` 가 소유해 두 소비자에 주입하는 형태** — 가 함께 간다.

가장 값싼 것부터 꼽으면 **ⓔ 다.** 멤버 추가 + 대입 1 + 치환 3 이고, 분리·타입 신설·함수 분해 어느 것도 선행으로 요구하지 않으며, 데이터 소유자가 바뀔 때 조용히 다른 인스턴스를 보는 위험을 미리 없앤다.

### Q. 문서 전체를 다시 읽고 검토 누락이 없는지 확인하면

3차 검토에서 **자체 정정 4건과 미검토 축 5건**이 나왔다.

정정:

| # | 내용 |
|---|---|
| 1 | `Reset`(`h:93`)을 뷰로 분류한 것은 오류다 — 표면 배열 2종을 0으로 채우는 **데이터 변이**이고 렌더 호출이 없다. 혼합으로 재분류 |
| 2 | ⓔ 를 "3줄 수정" 이라 적은 것은 부정확하다 — `DashHandleVisualizer` 는 주입받은 폴리데이터를 **멤버로 보관하지 않는다**(멤버 16개 전부 렌더 객체). 멤버 추가가 선행이다 |
| 3 | "자료형 손볼 후보 3건" 제목이 표 5행과 어긋나 있었다 |
| 4 | 형 변환 후보 계수 "3 → 6" 은 소유자 결정을 형 변환으로 셌다. 5건 + 결정 1로 분리 |

미검토였던 축:

| # | 축 | 실측 |
|---|---|---|
| 1 | 배열 규약의 실제 소비 범위 | **7파일 · 156곳.** 그중 UI 계층(뷰 28 + 뷰모델 22 + 오버레이 2)이 52곳 |
| 2 | 핸들 VTP 직렬화 위치 | **읽기 5곳 · 쓰기 2곳**이 뷰·뷰모델·컨트롤러·모델 4계층에 흩어져 있다. ⓕ 의 "로더 2벌" 은 그 일부였다 |
| 3 | 옮길 준비가 된 함수 | `filterSelectedHandles`(viewmodel `:171`)가 배열 11종 복제를 하며 이미 인자로 폴리데이터를 받는다 |
| 4 | 데이터 타입의 스레드 계약 | 문서에 없었다. GUI 전용 소유 · 워커는 DeepCopy 스냅샷만 · 데이터→뷰 참조 0 으로 명시 |
| 5 | 회귀망 | **핸들·인터랙션·모핑 단위 테스트 0건**(`tests/` 4파일은 job state·line assembler·process runtime·thread affinity). 검증이 지금 수동뿐이라는 것이 전제이고, leaf 화가 그것을 처음으로 바꾼다 |

미검토 축 1·2 가 이 분리의 규모 추정을 바꾼다. ⓓ 41곳은 "핸들/표면 폴리데이터를 얻는 지점" 이고, 배열 이름을 아는 지점은 그보다 훨씬 많은 156곳이다 — 다만 전부 감쌀 필요는 없고 **쓰기와 레이아웃 가정만** 데이터 타입 안으로 넣으면 된다는 것이 판정이다.

## 종합 정리

| 항목 | 실현 가능성 | 기대 효과 | 우선순위 |
|---|---|---|---|
| ⓔ `DashHandleVisualizer` 싱글톤 3단 체인 3곳 제거 (폴리데이터 멤버 추가 후 재사용) | 상 — 멤버 1 + 치환 3. 선행 0 | 소유자 교체 시 조용히 다른 인스턴스를 보는 위험 제거 | **1** |
| `HandleArrayNames` 리터럴 6곳 통일 + `GroupIds` 이름 중복 해소 | 상 — 기계적 | 배열 규약 소유가 가능해진다. 분리 전 정리가 싸다 | 1 |
| ⓐ `AddHandleData` 방향 뒤집기 (인덱스 반환 + 인터랙션이 기즈모 동기화) | 상 — 호출부 무변경 | leaf 방향 확보. 동작 무변경 | 1 |
| ⓑ 데이터 절반 4곳의 싱글톤 주입 전환 | 상 — `GetInputVTU` 3곳이 1회 주입으로 수렴 | leaf 성립 조건 충족 | 1 |
| ⓕ 쓰기 경로 이중화 3건 정리 (range 갱신 · 초기 range 규칙 · VTP 로더) | 중 — 로더 통합은 계산 경로에 닿는다 | 데이터 규칙을 데이터 타입이 소유 | 2 |
| 배열 소유권 2건 판정 + view 직접 쓰기 4곳 API 경유화 (ⓓ) | 중 — 판정이 선행 | 뷰가 데이터 배열을 직접 만지는 결합 제거 | 2 |
| ⓒ-1 `SetGroupNormalMode`·`SetBoxHandles` 말미 분해 | 상 | 계산 경로의 렌더 호출 제거 | 2 |
| ⓖ 고정점 상태 소유 통합 (원천 1벌 + 환산 2종을 데이터 타입으로) | 중 — 프리뷰 2경로가 소비. 층위 분해는 끝났다 | 같은 원천의 세 소유자 해소. 구속 원천을 직렬화에 올릴 자리가 생긴다 | 3 |
| ⓒ-2 `Finalize`·`UpdateSurfaceGeometry` 분해 | 중 — 별건 설계 필요 | 데이터·뷰 분리의 실질 관문 | 3 |
| 핸들 VTP 직렬화 7곳(읽기 5 · 쓰기 2)을 한 곳으로 | 중 — 4계층에 걸쳐 있다 | 배열 규약을 가장 강하게 아는 코드를 데이터 타입이 소유 | 3 |
| `DashHandleData` 타입 신설 + 소유자 결정 + `filterSelectedHandles` 이관 + TODO 2곳 갱신 | ⓐⓑⓒ 선행 필요 | 워커 진입 규약이 시그니처로 강제됨 | 4 |
| 최소 단위 테스트 3개 (튜플 수 일치 · 고정면 id 변환 · VTP 라운드트립) | 타입 신설과 같은 커밋 | **지금 회귀망 0건**. leaf 화의 첫 수확 | 4 |
| `DashMorphingController` 생성 알고리즘 5종 자유 함수화 | 데이터 타입 선행 | 두 번째 혼합체 해소. `DashNonDesignUtils` 가 선례 | 5 — 범위 밖 |

**우선순위 1의 넷은 타입 신설 없이 단독 커밋으로 가능하고 그것만으로도 값이 남는다.** 그중 ⓔ 는 선행이 0이라 가장 먼저 넣을 수 있다. 타입 신설은 ⓒ-2 이후가 맞다 — 293줄과 356줄이 갈리지 않은 상태에서 타입을 먼저 만들면 데이터가 액터를 참조하게 되어 leaf 가 깨진다.

## 다음 단계

- [ ] ⓔ `DashHandleVisualizer.cpp:209`·`:250`·`:338` 을 주입된 멤버 참조로 — 선행 0, 3줄
- [ ] `HandleArrayNames` 리터럴 6곳 통일 · `m_surfaceGeometry` 의 `"GroupIds"` 개명 — 분리 선행 정리
- [ ] ⓐ·ⓑ 를 한 커밋으로. `GetInputVTU` 주입 시점을 `InitializeHandlePicking` 에 맞출지 데이터 생성자로 올릴지 결정
- [ ] `InitializeHandleData` 재초기화 시 점/튜플 개수 불일치 런타임 확인 — `SetInputVTU` 를 두 번 타는 시나리오로 재현
- [ ] `ConstraintsAndHandles` 소유 판정 후 `DashMorphingSettings.cpp:1023`·`:1189` 를 데이터 API 경유로 전환
- [ ] `UpdateSurfaceGeometry`·`Finalize` 분해를 별 문서로 — 액터가 물고 있는 중간 결과와 순서 계약 목록화
- [ ] 이름 확정 후 TODO 2곳 갱신 (`h:35`-`:36` · `cpp:1239`-`:1240`)
- [ ] ⓖ 통합 — 의미 차이는 확인됐다(원천 · 표시 · 계산 3층위). 같은 목록에 넣지 않고 **원천 1벌 + 환산 함수 2종** 형태로 이관하고, `m_hiddenFixedIds` 는 프리뷰 표시 상태로 남길지 데이터 파생 캐시로 볼지 결정
- [ ] ⓖ 후속 — 구속 원천을 직렬화 대상에 올린다. 지금은 writer 가 없고 파생물(`AllFixedVolumeIds` fieldData)만 저장돼 재로드 시 원천 재구성이 불가능하다
- [ ] ⓓ 41곳 중 **쓰기 4곳**을 먼저 mutation API 로 올린다 — 읽기는 접근자로 미룰 수 있다
- [ ] 핸들 VTP 직렬화 7곳(읽기 5 · 쓰기 2)의 배열 목록이 서로 일치하는지 대조 — 불일치가 있으면 라운드트립이 이미 조용히 깨져 있다
- [ ] `filterSelectedHandles`(viewmodel `:171`)를 데이터 타입 연산으로 이관 — 시그니처 무변경으로 옮길 수 있는지 확인
- [ ] 타입 신설 커밋에 최소 테스트 3개 — 지금 핸들 관련 테스트가 0건이라 이것이 첫 회귀망이 된다
- [ ] `DashMorphingController` 생성 알고리즘 5종의 자유 함수화 — 별 문서. `DashNonDesignUtils` 형태를 목표로
- [ ] `docs/ThreadingContract.md` 2절 금지 타입 표에 "데이터 타입은 허용, 인터랙션은 금지" 행 추가 — 분리 완료 시점
