# 데이터 소유·소비 구조도 — RW 세션 · 모핑 핸들

> **성격**: 독립 참조 문서. 다이어그램 중심 — reader-writer(RW) 가 들고 있는 데이터와 그 소유자, GUI 가 옮겨 담는 데이터와 그 소유자, 그 데이터의 소비처를 한 장에 잇는다. 마지막 절 "모핑 데이터 — 현재 ↔ 목표 구조" 만 **제안 (미확정)** 이며, 그 앞 절은 전부 실측이다.
> **관련 Issue**: 없음 (독립 문서)
> **관련 문서**: [Code-Map-User-Flow-Condition-Parameterization](Code-Map-User-Flow-Condition-Parameterization.md) — 조건 DV 표가 `DashFeConditionEntry` 를 옮기는 경로 · [Project-Manifest-1-Context-Registry-And-Model-Identity](Project-Manifest-1-Context-Registry-And-Model-Identity.md) — Registry 소비자 전수 · [204-1-entity-ownership-hierarchy](204-1-entity-ownership-hierarchy.md) — GUI 전체 소유 계층 · [Code-Map-User-Flow-Geometry-Parameterization-Morphing](Code-Map-User-Flow-Geometry-Parameterization-Morphing.md) — 모핑 절이 인용하는 결함 번호 (D5·D6·D9·D11·D12) 의 출처 · [Handle-Data-View-Separation](Handle-Data-View-Separation.md) — 핸들 데이터·뷰 분리 조사 (제안 절의 기반) · [246-1-singleton-inventory-and-dashmanager-decomposition](246-1-singleton-inventory-and-dashmanager-decomposition.md) — DashManager 분해 순서 · [Project-Store-Design-Layer-Cut](Project-Store-Design-Layer-Cut.md) — `{인스턴스}/definition.json + handles.vtp` 배치
> **좌표 기준**: GUI `dev` @ `0e6b499` · ReaderWriter `dev` @ `a051251` (로컬 체크아웃 — GUI 가 링크하는 `reader-writer` 패키지 2026-09-22.0 과의 일치는 미확인). 정적 코드 근거만 — 빌드·실행 검증 없음.
> **범례**: `├──` 소유(수명 관리) · `→` 값 복사·변환 · `★` 데이터 본체 · `[Mesh]` 등 대괄호 = 어느 페이로드에서 왔는가

---

## 한 줄 요약

```
deck.inp ──parse──▶ AST (파일당 1개)            ──get_symbol_tree / get_data (값 복사)──▶ DashRwSession::State (파일당 1개)
                    소유: AbaqusModule                                                   소유: DashAnalysisModelContext::m_rw
                          ← DashRwActor::m_sessions[id]                                        ← Registry::m_contexts[경로]
                                                                                         소비: 렌더 · 모핑/DOE · 조건 DV 표 · 목록 UI
```

---

## 전체 구조도

```
[파일]  deck.inp — 텍스트
   │   Parser.cpp 스캐너가 줄 → keyword object. `**` 주석·빈 줄은 여기서 버려지고 `\` continuation 은 병합
   ▼

[1. RW 가 들고 있는 것]                            소유자: AbaqusModule (IRWModule 구현체 — 인터페이스 자체는 데이터 멤버 없음)
   │
   │   AbaqusModule                                source/Abaqus/AbaqusModule.hpp:88-100
   │   └── loaded_contents_[]                      로드한 파일 1개 = 원소 1개
   │       └── LoadedContent
   │           ├── info : ContentInfo              { file_path, display_name, uuid }
   │           └── ast  : ASTRoot  ★               RW 가 가진 데이터의 전부. 심볼 트리·페이로드는 캐시 없이 요청마다 여기서 생성
   │               ├── 타입 노드 (해석한 필드)       Part{vtk grid} · Assembly · Instance · Step · Nset · Elset · Surface
   │               │                               Boundary · CLoad · Dsload {entries, params} · Amplitude · Transform
   │               └── Unclassified {raw}           *MATERIAL · *SECTION · *TIE · *STATIC · *OUTPUT … keyword object 원문 보존
   │
   │   경계를 넘는 형태 — 전부 값 복사, 액터 스레드에서 실행
   │     get_symbol_tree()         → SymbolTreeNode 트리  { display_name, symbol_type, uuid, capabilities, children[] }
   │     get_data(uuid)            → Mesh | Set | FECondition
   │     get_symbol_detail(uuid)   → JSON { display_name, detail{ kind, entries[] } }
   │     get_edit_schema(uuid,ptr) → JSON Schema
   │     edit_data / edit_mesh / export_content   ← GUI 가 AST 로 되쓰는 방향
   ▼

[2. GUI 가 들고 있는 것]                            소유 사슬: 싱글턴 2개 + 파일당 객체 2개
   │
   │   DashRwActor (싱글턴 · 전용 QThread)                              ← AbaqusModule 인스턴스의 실제 소유자
   │   └── m_sessions : map<id, Session{ unique_ptr<IRWModule> }>       세션 1개 = 모듈 인스턴스 1개 = 파일 1개
   │
   │   DashAnalysisModelContextRegistry (싱글턴 · 메인 스레드)
   │   └── m_contexts : map<파일 절대경로, DashAnalysisModelContext>      파일당 1개
   │       ├── m_rw : DashRwSession ──── State  ★                        GUI 가 옮겨 담은 데이터 (controller/DashRwSession.cpp)
   │       │        ├── client                       DashRwClient { actor, id } 핸들 — 소멸 시 액터 세션을 닫음 (RAII)
   │       │        ├── [Mesh]        parts · partNames · partUuids · partDataUuids     비컨테이너 노드 전수 get_data 해서 Mesh 로 온 것
   │       │        ├── [Set]         nodeSets · elementSets                            같은 순회에서 Set 으로 온 것 (이름 → 라벨)
   │       │        ├── [FECondition] feConditionNames · feConditionUuids · feConditionCaps   트리에서 노드만 수집, 페이로드는 아직 안 받음
   │       │        ├── [지연 캐시]   editSchemaCache · feConditionShapeCache             getter 가 처음 불릴 때 채움. 재로드 시 통째로 소멸
   │       │        └── pluginName · loadedFilePath
   │       ├── m_polySurfaceMultiblock · m_partIndexMap                  parts 에서 파생 — 렌더용
   │       └── m_visualActor · m_displayAttributes
   │
   │   State 에 없고 getter 가 즉석에서 만들어 주는 타입 (controller/DashRwSession.h)
   │     DashFeConditionEntry   ← symbol detail JSON entries[] + edit schema      조건 1행
   │     DashFeConditionShape   ← types::FECondition (mesh · mask · values)       조건의 위치·값
   ▼

[3. 소비처]  전부 DashAnalysisModelContext 의 동명 getter 를 거친다
       렌더          parts                 → Context::buildPolySurfaceMultiBlock · buildPartIndexCache
                     feConditionShapeCache → DashConditionParameterizationWidget::onFeConditionSelectionChanged
       모핑 · DOE    parts                 → DashMorphingDoeExecutor::ExecuteOneSample  (updateMeshPoints → exportSolverInput, RW 로 되씀)
                     parts · nodeSets      → DashMorphingUtils::extractPartVtuFromDat · extractComponentVtuFromDat
                     nodeSets              → DashMorphingSettings::loadNodeSetList · createNodeSettings  (고정점)
                     feCondition*          → DashMorphingDoeExecutor::rwApplyConditionDvs · rwRestoreConditionDvs  (샘플 값 주입·복원, RW 로 되씀)
       조건 DV 표    feCondition*          → DashConditionParameterization::refreshFromLoadedAnalysis · commitEntryValue · entryParamSchema
       목록 UI       partNames             → DashReferenceFileWidget · DashModelingTreeWidget · DashModelRunnerWidget · DashOptimizerWidget
                     nodeSets · elementSets → DashModelRunnerWidget::loadSetsIntoPartCombo
```

---

## 모핑 데이터 — 핸들·고정점의 소유

핸들 정본은 한 곳, 고정점은 세 곳. 모델 계층(`DashGeometryParameter`) 은 설정값만 들고, 핸들·구속·그룹의 정본은 `DashManager` 싱글턴이 소유한 DashHandlePickingInteraction 하나에 VTK 배열로 흩어져 있으며, 저장 시점에 geom parm presentation model 이 그것을 VTP + JSON 두 파일로 내린다.

```
DashManager::Mgr()  ★싱글턴                                  controller/DashManager.h
├── m_handlePicking : DashHandlePickingInteraction            핸들·구속의 실질 정본 (헤더 TODO 에 분리 계획)
│   ├── m_handleGeometry : vtkPolyData  ★핸들 정본            점 1개 = 핸들 1개. 속성은 point-data 배열 11종 (DashHandleTypes.h)
│   │       LocalNormal · HandleNormal · SelectionScalars · ActiveStatus · GroupIds(4) · PlaneIds
│   │       LowerRange(4) · UpperRange(4) · Bounds(6) · LocalToGlobal(16) · HandleType (1 표면 / 2 marching plane)
│   ├── m_surfaceGeometry : vtkPolyData                       모핑 대상 표면. 스칼라 ConstraintsAndHandles (0/1/2/3/-1) 로 픽킹 상태 기록
│   ├── m_constraintSurfaceIds · m_constraintUGPointIds       ★고정점 1 — 표면 픽킹·nset 으로 들어온 구속 셀·점 id
│   ├── m_handleGizmos · m_planeGizmos · m_gizmoGroups · m_groupMembers · m_groupNormalModes   핸들 위치·Euler·그룹의 병행 보관
│   ├── m_pendingBoxHandles / Cylinder / MarchingPlanes       생성 버튼 → Done 사이 임시
│   └── m_controller ┈▶ DashMorphingController               (소유자는 DashMainWindow::m_morphingController — 역참조)
├── m_fixedMarkers : DashFixedMarkerSelection                 ★고정점 2 — 마커 = basis handle. 표면·구속 id·설계 핸들 점군·반경의 지문으로 무효화
├── m_designVariableModel : DashDesignVariableModel*          DV-Geometry 승격 결과 (공유 모델. Launcher·JobRunner 도 같은 포인터)
├── m_handleVisualizer · m_morphingPreviewGeometry/Actor · m_morphingStep · m_currentPreviewType   프리뷰 산출·상태
└── m_morphingSettingsWidget ┈▶ DashMorphingSettings          뷰 포인터 (계층 역전)

DashProject → QList<DashGeometryParameter*>                   model/DashGeometryParameter.h — Set 단위 설정만
    m_mesh · m_actor · m_partName · m_morphingRadius · m_referenceModel · m_setName · m_geometryParameterJsonPath

DashAnalysisModelContext::m_rw (RW 세션)                       ★고정점 3 의 출처 — nodeSets (위 구조도 2단의 [Set])
    DashMorphingSettings::createNodeSettings → getSetIndicesByName → constraintAdded
      → DashMainWindow → DashGeometryParameterWidget::appendConstraintTable → interaction 의 구속 id

[저장물]  configs/
├── GeometryParameter_{Set}.vtp     선택 핸들만 걸러 point-data 11종 그대로 + fieldData
│                                   AllFixedVolumeIds · FixedMarkerPoints · FixedMarkerSurfaceIds · FixedMarkerBasisKey
└── GeometryParameter_{Set}.json    Morphing { handles_vtp, radius, straight_sided, constraints[{name, node_ids[]}] }
                                    DV-Geometry { name: {type, min, max, default, source "Morphing|dat|component",
                                                          meta{handle id, group id, bound index, design value}} }
```

핸들·고정점 외에 얽힌 데이터:

| 데이터 | 보관 | 비고 |
|---|---|---|
| 모핑 대상 표면 | interaction `m_surfaceGeometry` | RW 세션의 parts 에서 추출 (`DashMorphingUtils::extractPartVtuFromDat`). 핸들 polydata 와 수명이 어긋남 (D12) |
| 대상 파트 이름 | `DashGeometryParameter::m_partName` | JSON 에 저장 안 됨 (D11) |
| 반경 | `DashGeometryParameter::m_morphingRadius` ↔ JSON `radius` | 같은 10.0 이 DoeExecutor `m_kernelRadius` · Basis 기본값 · 위젯 스핀박스에 흩어짐 (#423) |
| 범위 Lower/Upper | polydata 배열 | 저장은 트리 셀 스핀박스를 읽음 (D9) |
| 핸들 이름 · θ | 트리 item 텍스트 · Gizmo Euler | 저장 안 됨 / 벡터로만 왕복 (D5, D6) |
| 그룹 | `GroupIds` 배열 + `m_gizmoGroups` + 트리 부모-자식 | 셋이 병행 |
| 동결 basis | `DashMorphingBasis { m_config : MorphingConfiguration, blockSizes, kernelRadius }` | 요청마다 `Freeze` 로 생성 (`DashMorphingService` · `DashPreviewStates` · `DoeExecutor`). 장기 보관 없음. 프리뷰·MeshQC·DOE 가 같은 마커 선별로 동결해야 같은 형상 |
| 핸들 생성 보조 입력 | `DashMorphingController::m_physicsFiles/Previews`, 위젯 스핀박스 (hexa/cylinder/marching plane 격자) | 생성 시점에만 씀 |
| 레거시 마커 재계산 입력 | `DoeExecutor::m_legacyMarkerPoints`, `DashLegacyMarkerSource` | 마커 없는 구 VTP 전용. 삭제 예정 |

---

## 모핑 데이터 — 현재 ↔ 목표 구조 (제안 · 미확정)

> 기반: [Handle-Data-View-Separation](Handle-Data-View-Separation.md) (분리선·결합 ⓐ~ⓖ·소유자 결정) · #428 (결합 절단 4건) · #430 (`DashHandleData` 신설) · [Project-Store-Design-Layer-Cut](Project-Store-Design-Layer-Cut.md) (Set 벌크 = `handles.vtp`). 위키 분리 문서는 최종 소유자를 `DashManager` 로 잡았다. 본 절은 그것을 과도기로 보고 **Set 모델을 종착지**로 제안한다 — 근거는 #525 와 D12 가 "인스턴스 1개" 구조에서 나오는 결함이고, 저장 구조 설계가 이미 핸들을 Set 벌크로 배치했다는 점이다.

### 현재

```
DashManager::Mgr()  ★싱글턴 · 앱 전체 1개
├── m_handlePicking : DashHandlePickingInteraction (vtkCommand)    ★핸들·구속 정본 + 픽킹 + 기즈모 + 오버레이 4역할
│   ├── m_handleGeometry  배열 11종 (도메인 타입 없음, 156곳이 배열 이름·레이아웃 직접 가정)
│   ├── m_constraintSurfaceIds · m_nonDesignSurfaceIds             고정점 원천 1
│   └── ConstraintsAndHandles 스칼라 (표면 polydata 에 상주)        픽킹 임시 상태와 데이터가 같은 객체
├── m_fixedMarkers : DashFixedMarkerSelection                     고정점 원천 2 (같은 원천의 다른 환산)
└── m_designVariableModel                                          DV-Geometry 승격 결과

DashGeometryParameter (Set 모델)    설정값만 — 핸들·구속 없음. partName 은 저장되지 않음 (D11)
GUI 위젯                            범위 정본 = 트리 셀 스핀박스 (D9) · 이름 = 아이템 텍스트 (D5) · θ = Euler 역산 (D6)
PresentationModel                   저장: 파생물만 — VTP fieldData AllFixedVolumeIds. Morphing.constraints 는 파서만 (D10)
DoeExecutor · Optimizer · ModelRunner   interaction 의 live 핸들을 재생성해서 읽음 → GP 세트를 안 열면 실패 (#525)
```

### 목표

```
DashProject → QList<DashGeometryParameter*>   Set 모델 (파일 = definition.json + handles.vtp)
   └── DashHandleData  ★정본 · Set 당 1개 · QObject/vtkObject 아님 · DashManager·actor·gizmo·view 참조 0
       ├── handles        vtkPolyData 배열 11종 (규약 현행 유지) + HandleNames (신규, D5)
       ├── constraints    원천 목록 {name, 출처(surface-pick | nset | non-design), cellIds 또는 nsetName}
       ├── fixedPoints    파생 환산 2종 — surfacePointIds() · volumePointIds() (저장 안 함, 재계산)
       ├── partName · deck 참조 (D11) · radius (#423 정본)
       └── snapshot()  →  DashMorphingInputSnapshot (DeepCopy, GUI 스레드에서 생성)
             ├── 주입 ──▶ DashHandlePickingInteraction   편집 UI 만 남김: 픽킹 스칼라 · 기즈모 · 오버레이 actor
             ├── 주입 ──▶ DashHandleVisualizer            렌더
             ├── 호출 ──▶ PresentationModel                저장·로드 = DashHandleData 의 직렬화 연산을 부르는 얇은 층
             └── 스냅샷 ▶ DoeExecutor · PreviewStates · Optimizer · ModelRunner   Set 을 열지 않아도 실행 가능
```

### 바꿔야 할 것

| # | 현재 | 문제 | 목표 | 근거 |
|---|---|---|---|---|
| 1 | 핸들 정본이 앱 전역 인터랙션 1개 | Set 재진입 누적, GP 세트를 안 열면 DOE 실패, 모델·최적화기가 GUI live 핸들을 재생성해서 읽음 | Set 모델이 소유. 인터랙션은 Set 진입 시 주입받고 이탈 시 비움 | D12 · #525 · #221 |
| 2 | 배열 11종이 도메인 타입 없이 모델 노릇 | 156곳이 배열 이름·레이아웃을 직접 가정 | `DashHandleData` 가 배열 규약과 mutation API 를 소유. 뷰 직접 쓰기 4곳부터 API 경유 | D4 · #430 · 분리 문서 ⓓ |
| 3 | 고정점 원천이 두 소유자 (인터랙션 셀 id 2종 + `m_fixedMarkers`) | 같은 원천이 다른 인자로 두 번 엔진에 들어감 | 원천 1벌 + 환산 함수 2종을 데이터 타입에. 마커 선별은 원천의 파생 캐시 | 분리 문서 ⓖ |
| 4 | 저장이 파생물만 (`AllFixedVolumeIds`), `Morphing.constraints` 는 파서만 | 재로드 시 오버레이·구속 표 복원 불가, 마커 재선별은 빈 집합 | 구속 원천 (셀 id 또는 nset 이름) 을 직렬화 대상으로. `AllFixedVolumeIds` 는 실행 스냅샷 (`input.json` 자리) 으로 격하 | D10 · Layer-Cut 7.3 |
| 5 | 범위 = 트리 셀 위젯, 이름 = 아이템 텍스트, θ = Euler 역산, 파트명 미저장 | 표시값 ≠ 저장값 | 범위·이름·방향 벡터·파트명 전부 데이터 타입 필드. θ 는 표시 전용 파생 | D5 · D6 · D9 · D11 |
| 6 | 픽킹 스칼라 `ConstraintsAndHandles` 가 표면 polydata 에 상주 | UI 제스처 상태가 데이터와 같은 객체 | 뷰 임시 상태로 남기되 `Finalize` 가 데이터 API 로 커밋. 스칼라 자체는 정본 아님 | 분리 문서 "배열 소유권 판정" |

### 순서

```
[1단계] #428 — 타입 없이 결합 절단 4건
   │   싱글턴 되부름 제거 · 배열 이름 통일 · 데이터 함수의 기즈모 호출 분리 · 주입 전환
   │   ※ 단독 커밋 가능, 동작 무변경
   ▼

[2단계] #430 — DashHandleData 신설
   │   첫 소유자는 분리 문서 결정대로 DashManager. 인터랙션·비주얼라이저에 주입
   │   최소 테스트 3개 동반 — 튜플 수 일치 · 고정면 id 환산 · VTP 라운드트립 (현재 핸들 테스트 0건)
   ▼

[3단계] 소유자를 DashGeometryParameter 로 이관
   │   인터랙션 리셋을 Set 진입·이탈 계약으로 묶음
   │   ※ #221 · D12 · #525 가 여기서 닫힌다
   ▼

[4단계] 직렬화 확장
       구속 원천 · 파트명 · 이름 · 범위 → definition.json, 핸들 배열 → handles.vtp
       Layer-Cut 의 {인스턴스}/definition.json + handles.vtp 배치와 그대로 맞물린다
```

### 하지 말 것

- 데이터 타입을 vtkObject 파생으로 만들지 않는다 — 담는 것이 vtk 객체일 뿐 자신은 콜백도 파이프라인 요소도 아니다.
- 고정점을 핸들 polydata 의 점으로 승격하지 않는다 — 엔진에는 "변위 0 핸들" 이지만 데이터로는 별개 목록이다.
- 배치 실행이 live 인터랙션을 건드리지 않는다 (#427 격리 원칙).
- 1단계 전에 타입을 먼저 만들지 않는다 — 액터 참조가 새어 leaf 가 깨진다.
