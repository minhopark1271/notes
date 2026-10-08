# Geometry·CAD·Condition·Assets·VTK 작업 카드

교차검토 반영본. 최종 통합 정본은 [전체 목록](../03_TASK_CATALOG.md)이다.

담당 초안 AST-002는 동일 PR651 작업인 [AL-09](../03_TASK_CATALOG.md#al-09)에 합쳤다. JSON 원본의 AST-002는 추적용으로만 남긴다.

## GEO-001

**핸들 편집·실행·저장을 Setup/Configuration 값 모델로 전환한다**

- 모듈: Geometry Parameter / Morphing
- 판정: PR 진행 중 · 제안 우선순위 P2 · 측면 태그 A, C, E
- 사용자 결과: 핸들·마커·DV가 하나의 값 모델과 version 1 JSON으로 복원되고 모든 실행 소비자가 동일한 구성을 받는다.
- 선행: 없음
- 기존 이슈: [#332](https://github.com/NumeRealWorks/DashOpti_GUI/issues/332), [#430](https://github.com/NumeRealWorks/DashOpti_GUI/issues/430), [#487](https://github.com/NumeRealWorks/DashOpti_GUI/issues/487), [#499](https://github.com/NumeRealWorks/DashOpti_GUI/issues/499), [#563](https://github.com/NumeRealWorks/DashOpti_GUI/issues/563), [#577](https://github.com/NumeRealWorks/DashOpti_GUI/issues/577)

**변경 범위**

- PR #654 구현을 최종 검토·통합한다: sample_handles, Setup→Configuration, (entry 이름, control ID) DV, 반경 재구축, JSON archive 및 QC/DOE/Optimizer/Runner 연결.
- 기존 VTP·constraints[]·핸들 ID DV와 cylinder 경로의 종료를 명시하고 구 Set 열기 시 재작성 안내와 파일 무변경을 보장한다.
- 현재 PR에 포함된 SectionFrameHandles 변환 어댑터와 sampled tree를 함께 검증한다.

**완료 조건**

- 저장·재진입 후 핸들, 고정점, DV 범위와 Set 반경이 복원된다.
- sampling 실패·취소 시 이전 편집 상태가 유지되고 구 형식은 실행 전 안내 후 거부된다.
- GUI 변경과 실행 snapshot의 수명·데이터가 분리된다.
- DV lower≤upper·유한성 및 양의 반경 검증이 저장/프리뷰/복원 경계에서 유지된다.

**검증 방법**

- PR 신설 TestHandleState/TestHandleSampling/TestSampledHandleTree 및 기존 QC/DOE/preview 테스트를 통합 기준에서 확인한다.
- 실제 GUI에서 Automatic→Done→범위 변경→QC→Proceed→재진입, 반경 변경, 구 Set 거부를 수행한다.

**근거**

- `dev controller/DashMorphingController.cpp:1052 selectHandlesGreedyByUnit`
- `dev viewmodel/DashGeometryParameterPresentationModel.cpp:381 handles_vtp`
- `sources/pr-654.diff:2084 DashHandleState.cpp; :2856 DashHandleStateJson.cpp; :8078 WidgetHandles`
- `sources/pr-654.json / PR #654 open`

**범위·결정 메모**

새 구현 PR를 중복 작성하지 않는다. PR 본문의 56/56·빌드 통과는 작성자 보고이며 이번 조사에서 재실행하지 않았다. GUI 수동 검증은 PR 본문상 미실행. per-handle 반경 UI·구 VTP 자동 변환은 최신 결정으로 제외.

## GEO-002

**핸들 interaction이 값 모델의 투영만 편집하도록 소유권을 마무리한다**

- 모듈: Geometry Parameter / Morphing
- 판정: 선행 작업 후 · 제안 우선순위 P2 · 측면 태그 A, C, E
- 사용자 결과: 기즈모·피킹·표시가 같은 Configuration/Setup에 반영되며 별도의 수정 가능한 polydata 정본이 남지 않는다.
- 선행: GEO-001
- 기존 이슈: [#332](https://github.com/NumeRealWorks/DashOpti_GUI/issues/332), [#427](https://github.com/NumeRealWorks/DashOpti_GUI/issues/427), [#430](https://github.com/NumeRealWorks/DashOpti_GUI/issues/430)

**변경 범위**

- m_handleGeometry를 projection 캐시로 내리고 mesh-ops set output_port에 렌더를 연결한다.
- 피킹, 그룹/해제, 이름 변경, 범위·pose 편집을 값 모델 명령으로 연결하고 과도기 polydata→state 이중 동기화를 제거한다.
- Set 전환·재진입 시 actor/observer를 현재 모델에 재연결하고 이전 모델 참조를 해제한다.

**완료 조건**

- 드래그·DV 표·프리뷰·저장 값이 동일하며 cached projection 직접 수정이 실행 정본을 우회하지 않는다.
- Set 왕복·삭제 후 선택/기즈모가 이전 Set을 수정하지 않고 actor/observer가 누적되지 않는다.

**검증 방법**

- TestMorphingPreviewDriver의 재진입·part 왕복 시나리오를 새 값 모델에서 검증한다.
- 그룹 편집·범위 변경·undo가 아니라 dropSamples 전이·재sampling·저장 후 재진입을 수동 검증한다.

**근거**

- `controller/DashHandlePickingInteraction.h:241 m_handleGeometry`
- `sources/pr-654.diff:1077 DashHandleImport 과도기 어댑터`
- `sources/issues/430.md 2026-10-04 댓글`

**범위·결정 메모**

#428의 이미 완료된 주입/수집 분리는 다시 구현하지 않는다. root #434 interaction 객체 수명 이동과 파일 접점은 조율하지만 서로를 자동 하드선행으로 두지 않는다.

## GEO-003

**고정 영역을 라벨이 있는 값 스펙으로 편집·복원하고 표시와 분리한다**

- 모듈: Geometry Parameter / Constraints
- 판정: 선행 작업 후 · 제안 우선순위 P1 · 측면 태그 A, C, D
- 사용자 결과: Non-design 영역을 숨겨도 실행 고정점이 바뀌지 않고 Set 왕복 후 원래 영역 이름·참조·범위가 남는다.
- 선행: GEO-001
- 기존 이슈: [#563](https://github.com/NumeRealWorks/DashOpti_GUI/issues/563)

**변경 범위**

- Constraints 생산 UI가 DashFixedRegion의 node set 참조·node label·grid mask·영역 이름을 명시적으로 만든다. control 영역의 이름도 같은 방식으로 정리한다.
- Morphing.handles.unpinned[]의 스펙을 표/오버레이와 왕복하고 Show/Hide는 시각화에만 적용한다.
- 현재 참조 모델과 맞지 않는 영역 및 유효하지 않은 참조를 저장/실행 전에 설명한다.

**완료 조건**

- 서로 다른 이름의 고정 영역 2개를 저장·재진입해 독립 복원한다.
- Hide 후 저장·QC·DOE와 Show 후 동일 실행의 fixed block이 같다.
- Set/프로젝트/모델 변경 시 이전 영역이 새 메시 인덱스로 오해되지 않는다.

**검증 방법**

- 고정 영역 스펙별 JSON 왕복·resolver 검증과 Hide/Show 동등성 테스트.
- 재진입→Hide→Set 재저장→DOE 실제 GUI 흐름 검증.

**근거**

- `view/DashGeometryParameterWidget.cpp:2957 updateConstraintVisualization`
- `controller/DashHandlePickingInteraction.cpp:3198 SetVisibleConstraintIds`
- `sources/pr-654.diff:2897 region JSON; :8214 constraints 단일 이름 수집`
- `sources/issues/563.md 최신 댓글`

**범위·결정 메모**

기존 이슈의 JSON constraints+VTP 그룹 배열/legacy 자동 역변환 설계는 폐기한다. PR654가 값 스펙과 영속 바탕을 제공하지만 라벨화 생산 UI는 명시적 범위 밖이다.

## GEO-004

**Hexahedron을 BoxHandles FFD 생성·면 DV 흐름으로 제공한다**

- 모듈: Geometry Parameter / Volume handles
- 판정: 선행 작업 후 · 제안 우선순위 P2 · 측면 태그 C, D, E
- 사용자 결과: Volume 메뉴에서 박스 생성부터 면 오프셋 DV, QC, 저장, DOE까지 실행할 수 있다.
- 선행: GEO-002
- 기존 이슈: [#499](https://github.com/NumeRealWorks/DashOpti_GUI/issues/499), [#577](https://github.com/NumeRealWorks/DashOpti_GUI/issues/577)

**변경 범위**

- Hexahedron 메뉴·파라미터 UI를 BoxHandles FFD 생성에 연결한다.
- 면 드래그 릴리즈 1회에 set_faces 절대 pose를 갱신하고 face DV 행·범위를 값 모델에 반영한다.
- 반경은 Set radius 정책을 따르고 dump/load 후 pose·범위를 복원한다.

**완료 조건**

- Volume→Hexahedron→면 드래그→Done→face 범위→프리뷰→QC Proceed→DOE가 연결된다.
- Set 재열기 후 박스와 DV 범위가 유지되고 Marching Plane에 회귀가 없다.

**검증 방법**

- box pose·face DV·반경 변경·archive 왕복 테스트.
- 실제 GUI에서 신규 Hexahedron 전체 사용자 경로를 확인한다.

**근거**

- `controller/DashMorphingController.cpp:1215 setHandlesBoxhandle 구 shell 구현`
- `view/overlay/DashMorphingBar.cpp:27 Volume 메뉴`
- `sources/issues/577.md 2026-10-05 결정`
- `sources/pr-654.json 포함하지 않은 것 PR 3`

**범위·결정 메모**

최신 #577 결정을 적용: cylinder는 복구하지 않고 GEO-001에서 삭제. 기존 shell 박스와 산출물 동일성은 요구하지 않는다. Box 축 분할 UI 세부 선택은 구현 리뷰에서 명시하되 이미 철회된 shell 동일성을 별도 차단 질문으로 되살리지 않는다.

## GEO-005

**단면 추출·핸들 생성을 mesh-ops 공개 API로 끝까지 이관한다**

- 모듈: Geometry Parameter / Marching Plane
- 판정: 선행 작업 후 · 제안 우선순위 P2 · 측면 태그 C, E
- 사용자 결과: 단면 프레임 생성부터 edge DV까지 하나의 공개 생성기 계약을 쓰며 사내 MarchingPlaneBound 복제본을 제거한다.
- 선행: GEO-002
- 기존 이슈: [#331](https://github.com/NumeRealWorks/DashOpti_GUI/issues/331), [#499](https://github.com/NumeRealWorks/DashOpti_GUI/issues/499)

**변경 범위**

- 현재 MarchingPlaneBound 기반 절단을 section_frames로 대체하고 시작/끝 단면 skip 정책을 호출자에서 보존한다.
- GEO-001의 SectionFrameHandles 어댑터를 직접 생성 경로로 연결하고 중간 polydata bounds 변환을 제거한다.
- 마지막 소비자가 사라지면 libs/DashMarchingPlane 및 CMake 독립 타깃을 제거한다.

**완료 조건**

- 기울어진 단면, 끝 단면 skip, edge 4방향 제어와 저장 복원이 일치한다.
- section_frames 실패·빈 단면이 명시적으로 보고되고 invalid 핸들을 남기지 않는다.

**검증 방법**

- 프레임 좌표·edge 방향·skip 개수·DV 처방 테스트.
- 동일 메시의 기존 단면과 새 단면 범위/방향을 비교하되 새 sampling의 수치 동일성을 요구하지 않는다.

**근거**

- `controller/DashMorphingController.cpp:105 MarchingPlaneBound`
- `CMakeLists.txt:371 DashMarchingPlane`
- `sources/pr-654.diff:2192 SectionFrameHandles 어댑터; section_frames 도입 없음`

**범위·결정 메모**

PR654는 SectionFrameHandles 값 모델을 도입하지만 원본 marching-plane 추출기는 남긴다. 상류 API 버전은 GEO-001의 MeshOps 0.5.0 기준으로 착수 시 확인한다.

## GEO-006

**QC 결과 창을 닫아도 저장 작업이 대기 상태에 갇히지 않게 한다**

- 모듈: Geometry Parameter / Mesh QC
- 판정: 착수 가능 · 제안 우선순위 P1 · 측면 태그 B, D
- 사용자 결과: 결과 표시 직후 Esc/닫기를 눌러도 QC 수명과 busy 상태가 정리되고 다시 Set Design Variable을 실행할 수 있다.
- 선행: 없음
- 기존 이슈: [#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281), [#512](https://github.com/NumeRealWorks/DashOpti_GUI/issues/512)

**변경 범위**

- DashMeshQualityDialog::setResults의 processEvents를 제거한다.
- 결정 수신과 취소/결과 전환 수명을 정리하여 이미 발생한 finished 시그널을 기다리지 않도록 한다.
- Proceed/Retry/닫힘/프로젝트 전환의 qcDialog_ 정리를 하나의 종료 경로에서 보장한다.

**완료 조건**

- 결과 표시 중 닫기 후 qcDialog_가 비워지고 숨은 dialog/coroutine이 남지 않는다.
- QC 중 닫기와 결과 직후 닫기 모두 다음 실행을 막지 않는다.

**검증 방법**

- 위젯 레벨에서 결과 게시 시점에 reject를 주입하고 다음 QC 시작 가능성을 검증한다.
- TestMeshQcStates는 계산 상태만 보므로 dialog 수명 검증을 별도로 수행한다.

**근거**

- `view/dialog/DashMeshQualityDialog.cpp:164 processEvents`
- `view/DashGeometryParameterWidget.cpp:1456 disconnect→setResults→:1463 await`
- `tests/TestMeshQcStates.cpp:358; tests/TestMorphingPreviewDriver.cpp`

**범위·결정 메모**

QC 계산 워커화 자체는 이미 완료되었다. QCoro wrapper를 변수에 먼저 만든다는 이유만으로 connect가 즉시 수행된다고 가정하지 말고 실제 수신 등록/재진입 제거를 검증한다.

## GEO-007

**모핑 값 경계의 미검증 교차 모듈 시나리오를 검증하고 발견된 회귀를 닫는다**

- 모듈: Geometry Parameter / 실행 통합
- 판정: 실측 필요 · 제안 우선순위 P2 · 측면 태그 A, B, F
- 사용자 결과: 구현 완료로 표시된 local화/상태기 경로가 프로젝트 전환과 DOE·Optimizer·Runner에서도 실제로 안전함을 확인한다.
- 선행: GEO-001
- 기존 이슈: [#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281), [#427](https://github.com/NumeRealWorks/DashOpti_GUI/issues/427), [#586](https://github.com/NumeRealWorks/DashOpti_GUI/issues/586)

**변경 범위**

- #586에서 보류한 DOE+프리뷰 동시 실행, 프로젝트 전환, Optimizer/Runner export를 새 Configuration 기준으로 재현한다.
- 실행 중 화면 편집·참조 변경이 실행 snapshot을 바꾸거나 완료가 다른 프로젝트 화면에 쓰는지 확인한다.
- 발견된 결함만 구체 수정하고 이미 사라진 worker/gate 체계를 재도입하지 않는다.

**완료 조건**

- 시나리오별 입력·예상 결과·실측·산출물·통과/실패가 남는다.
- 실행과 화면 상태가 독립이며 종료/취소/프로젝트 변경 후 이전 결과가 반영되지 않는다.

**검증 방법**

- TestMorphingRun/Service/DoeBatchChain/PreviewCollector를 관련 경계의 회귀로 사용한다.
- SDK·solver 가용 환경에서 통합 GUI 실행. 구 VTP와 새 sampling의 바이트 동일성은 제외하고 같은 Configuration 실행 재현성을 확인한다.

**근거**

- `model/geometry/DashMorphingUtils.cpp:134 performMorphingAndExport`
- `controller/DashMorphingDoeExecutor.cpp:529 Execute`
- `sources/issues/586.md 수동 검증 보류 5~7`
- `sources/pr-654.json GUI 시나리오 미실행`

**범위·결정 메모**

검증 게이트 성격의 작업이다. 통과하면 구현 PR이 필요 없을 수 있으며 미검증을 결함으로 단정하지 않는다. Optimizer/Runner 요청 ID·취소 구현은 downstream 카드 소유.

## VIS-001

**Optimizer 프리뷰가 자기 actor만 교체하도록 한다**

- 모듈: 공통 VTK / Optimizer Preview
- 판정: 착수 가능 · 제안 우선순위 P1 · 측면 태그 A, D, E
- 사용자 결과: 기존 문서·핸들·카메라를 그대로 보존하면서 Optimizer 프리뷰만 겹쳐 표시한다.
- 선행: 없음
- 기존 이슈: [#316](https://github.com/NumeRealWorks/DashOpti_GUI/issues/316), [#318](https://github.com/NumeRealWorks/DashOpti_GUI/issues/318), [#427](https://github.com/NumeRealWorks/DashOpti_GUI/issues/427)

**변경 범위**

- renderer actor 전체 순회 삭제를 자기 프리뷰 actor 해제/교체로 바꾼다.
- 기존 FE 문서·핸들·피킹 actor의 visibility, registry 표시 커서와 카메라를 유지한다. overlay actor만 등록·해제한다.
- 프리뷰 반복·실패·모듈 이탈 시 소유 actor만 정리한다.

**완료 조건**

- 기존 로드 모델·핸들이 계속 보이고 표시커서·카메라가 변하지 않으며 preview만 겹친다.
- 연속 프리뷰가 actor를 누적시키지 않고 실패가 기존 화면을 잃게 하지 않는다.
- 다음 Load와 요청 무효화에서 preview actor만 제거하고 새로운 기준 씬에 낡은 overlay가 남지 않는다.

**검증 방법**

- 문서 로드→모핑 편집→Optimizer 프리뷰→복귀와 실패/반복 프리뷰 GUI 검증.
- actor 소유 목록과 실제 등록 수를 검증하는 렌더 통합 테스트.

**근거**

- `view/DashOptimizerWidget.cpp:1751 prevDisplayedActor 제거; :1757 GetActors 전체 삭제`
- `controller/DashRenderingManager.cpp:1116 addAnalysisModelActor`

**범위·결정 메모**

OPT 비동기 요청 수명 카드와 별도 목적이다. 전면 씬 소유권 작업을 기다리지 않고 현재 API로 비파괴 파일럿을 만들 수 있다.

## VIS-002

**FE actor의 숨김·복원·등록 수명과 카메라 갱신을 바로잡는다**

- 모듈: 공통 VTK / FE 문서 actor
- 판정: 착수 가능 · 제안 우선순위 P1 · 측면 태그 D, E
- 사용자 결과: Morphing/Runner를 오간 뒤에도 문서 표시가 복원되고 사용자 카메라가 임의 초기화되지 않는다.
- 선행: 없음
- 기존 이슈: [#318](https://github.com/NumeRealWorks/DashOpti_GUI/issues/318), [#319](https://github.com/NumeRealWorks/DashOpti_GUI/issues/319), [#427](https://github.com/NumeRealWorks/DashOpti_GUI/issues/427)

**변경 범위**

- Start Morphing의 FE actor 숨김에 모듈 이탈/트리 표시 복원 경로를 짝지운다.
- Model Runner preview에서 남는 FE actor는 삭제가 아닌 숨김으로 처리한다.
- Geometry actor의 등록/해제를 RenderingManager로 맞추고 중복 등록을 막는다.
- 문서 교체와 명시적 fit 외에 카메라를 초기화하지 않도록 updateActor 호출 계약을 정리한다.

**완료 조건**

- FE 모델→Morphing→복귀 및 트리 눈 토글로 다시 표시된다.
- Geometry Set을 반복 전환해 actor 관리 목록이 늘어나지 않는다.
- 단순 재표시가 카메라 pose를 바꾸지 않는다.

**검증 방법**

- 문서/모듈 왕복 시 visibility·camera pose·actor 수 검증.
- Runner preview에서 FE 겹침이 없고 복귀하면 원래 FE 표시가 회복되는 GUI 확인.

**근거**

- `view/DashMainWindow.cpp:4755 FE 숨김; :4587 직접 RemoveActor`
- `controller/DashAnalysisModelContextRegistry.cpp:412 updateActor`
- `controller/DashRenderingManager.cpp:598 clearAllLayers; :1122 append`
- `view/DashModelRunnerWidget.cpp:1495 preview`

**범위·결정 메모**

clearAllLayers에 모든 문서 actor 삭제를 추가하는 방식은 확정된 문서 보존 정책과 맞지 않는다.

## VIS-003

**씬 콘텐츠를 모듈·문서 단위로 등록하고 전환 시 보존 정책을 적용한다**

- 모듈: 공통 VTK / 씬 소유권
- 판정: 선행 작업 후 · 제안 우선순위 P2 · 측면 태그 A, C, D, E
- 사용자 결과: 모듈 전환이 로드한 문서를 파괴하지 않고 누가 표시 중인지 질의할 수 있다.
- 선행: VIS-001, VIS-002
- 기존 이슈: [#318](https://github.com/NumeRealWorks/DashOpti_GUI/issues/318), [#427](https://github.com/NumeRealWorks/DashOpti_GUI/issues/427)

**변경 범위**

- RenderingManager에 소유자/콘텐츠 ID와 문서형·작업물형 등록 계약을 도입하고 첫 문서/모듈 소비자를 함께 이관한다.
- MainWindow 문서 Load·삭제·모듈 전환, Analysis Launcher 결과, Runner와 Optimizer 표시를 같은 창구로 연결한다.
- 문서는 프로젝트 종료/명시 삭제까지 보존하고 작업물은 모듈 이탈 시 정리한다. 기존 clearModuleLayers의 인자 무시 구현을 제거/대체한다.

**완료 조건**

- 현재 씬 소유자·원본 경로/Set을 질의할 수 있고 다른 모듈 콘텐츠를 파괴하지 않는다.
- .dat/.inp와 .vtk/.vtu 문서가 같은 유지 정책을 따른다.
- 프로젝트 전환 시 모든 소유 등록이 정리되고 외부 renderer 직접 삭제와 목록 불일치가 남지 않는다.

**검증 방법**

- 문서→Launcher→Runner→Optimizer→Geometry 전환 매트릭스 및 프로젝트 종료 반복 검증.
- 소유자별 등록/숨김/해제 계약 테스트와 메모리·actor 수 실측.

**근거**

- `controller/DashRenderingManager.h:Layer`
- `controller/DashRenderingManager.cpp:627 clearModuleLayers 인자 무시`
- `view/DashMainWindow.cpp:3031 문서 Load 제거 경로`
- `sources/issues/318.md 2026-09-21 정책`

**범위·결정 메모**

실제 소비자를 포함한 PR 단위이며 큰 경우 소비자군별 후속 PR로 나눌 수 있다. 핸들/피킹의 모든 renderer 호출을 이 PR에서 일괄 이동할 요구는 없다. #315 재클릭 게이트에 제공할 질의는 접점이며 별도 티켓 중복 생성하지 않는다.

## VIS-004

**split view 이탈과 ghost 외형·범례 복원을 씬 전환에 연결한다**

- 모듈: 공통 VTK / split view·공유 표시
- 판정: 착수 가능 · 제안 우선순위 P1 · 측면 태그 D, E
- 사용자 결과: Builder split view 이후 모든 모듈이 정상 렌더되고 문서의 외형·카메라·범례가 복원된다.
- 선행: 없음
- 기존 이슈: [#318](https://github.com/NumeRealWorks/DashOpti_GUI/issues/318)

**변경 범위**

- 메인 씬을 인수하는 진입점과 모듈 이탈에서 split renderer 해제 및 main SetDraw(true)를 보장한다.
- base actor ghost 변경 전 외형을 보존하고 결과/컴포넌트 표시 종료 시 복원한다.
- scalar bar·cube axes·camera 공유 자원의 활성 소유자 전환 계약을 RenderingManager에서 처리한다.

**완료 조건**

- Builder split→Project Load/Geometry/Optimizer/Launcher 각각에서 화면이 표시된다.
- component/result 이탈 뒤 base 문서 색·opacity·wireframe·lighting이 원상 복귀한다.
- 전환 반복으로 split renderer/범례/축이 누적되지 않는다.

**검증 방법**

- split 진입/이탈→다른 모듈 진입 GUI 회귀와 renderer Draw 상태 테스트.
- ghost property snapshot 왕복 및 범례 소유자 테스트.

**근거**

- `controller/DashRenderingManager.cpp:1338 SetDraw(false); :1550 clearSplitView`
- `view/DashModelRunnerWidget.cpp:1497 유일 외부 clearSplitView`
- `controller/DashRenderingManager.cpp:updateComponentGeometry/updateFieldOutput`

**범위·결정 메모**

소유권 본 구현과 조율하되 지금 수정 가능한 화면 복구 결함이므로 VIS-003을 필수 선행으로 강제하지 않는다.

## VIS-005

**VTK/VTU 파일별 표시 핸들을 등록하여 눈 토글을 구현한다**

- 모듈: Project Assets / VTK 문서 표시
- 판정: 선행 작업 후 · 제안 우선순위 P2 · 측면 태그 C, D
- 사용자 결과: 파일 하나의 표시를 켜고 끌 때 그 파일만 바뀌며 여러 파일을 함께 표시할 수 있다.
- 선행: VIS-003
- 기존 이슈: [#318](https://github.com/NumeRealWorks/DashOpti_GUI/issues/318), [#320](https://github.com/NumeRealWorks/DashOpti_GUI/issues/320)

**변경 범위**

- 파일별 scene handle/actor를 등록하고 트리 parent·child 표시 상태를 동일 콘텐츠 ID에 연결한다.
- 같은 파일 재표시는 재파싱 없이 처리하고 파일 교체/삭제/프로젝트 전환 시 캐시를 무효화한다.
- 단일 LAYER_BASE_GEOMETRY를 파일마다 덮는 경로와 항상 빈 m_vtuVtkActors 가정을 제거한다.

**완료 조건**

- 두 VTK 파일의 개별 on/off, 부모 일괄 on/off가 서로 독립적으로 동작한다.
- 파일 하나를 켜도 다른 모듈/문서 actor가 지워지지 않는다.
- 삭제·덮어쓰기 후 이전 메시를 되살리지 않는다.

**검증 방법**

- 2개 .vtu 및 .vtk 파일로 부모/자식 눈 상태와 실제 actor visibility 검사.
- 재표시 reader 재호출·캐시 정리·다른 문서 보존 검증.

**근거**

- `view/DashModelingTreeWidget.cpp:397 vtk_parent+vtk_single 생성`
- `view/DashMainWindow.cpp:3647 눈 토글; :3861 loadVtkFile`
- `view/DashMainWindow.h:m_vtuVtkActors, 저장 코드 없음`

**범위·결정 메모**

현 Project Assets 구조에서도 vtk_parent/child 경로는 실제 존재하므로 오래된 Modeling Tree 기능의 폐기로 처리할 수 없다.

## VIS-006

**Gizmo 소스를 앱 소유 코드로 옮겨 독립 임시 빌드 타깃을 제거한다**

- 모듈: 공통 VTK / Gizmo 빌드
- 판정: 착수 가능 · 제안 우선순위 P3 · 측면 태그 E, F
- 사용자 결과: Gizmo가 앱과 같은 컴파일/VTK 설정을 쓰며 임시 라이브러리 포장과 경로 예외가 사라진다.
- 선행: 없음
- 기존 이슈: [#331](https://github.com/NumeRealWorks/DashOpti_GUI/issues/331)

**변경 범위**

- libs/DashGizmo 소스를 앱 내부 적절한 디렉터리로 옮기고 include 경로를 갱신한다.
- 별도 add_subdirectory/ALIAS/CMakeLists를 제거하고 vtk_module_autoinit 대상 구성을 맞춘다.
- 확정된 저장소 naming 규칙을 적용하되 Gizmo 동작 변경과 불필요한 전면 스타일 변경은 섞지 않는다.

**완료 조건**

- 앱 단일 타깃 빌드에서 Gizmo가 링크되고 중복 컴파일·VTK 재탐색이 없다.
- 모핑 선택·그룹 이동·범위 슬라이더가 기존 동작을 유지한다.

**검증 방법**

- Release 앱 링크 및 관련 morphing GUI 연기 테스트.
- Gizmo 심벌/소스가 중복 편입되지 않는 CMake 구성 점검.

**근거**

- `CMakeLists.txt:368 add_subdirectory; :403 DashGizmo::DashGizmo; :413 autoinit`
- `libs/DashGizmo/README.md`

**범위·결정 메모**

MarchingPlane 제거는 GEO-005 소유. 동작 수정인 VIS-007과 경로 충돌을 피하기 위한 권장 순서이며 강한 제품 의존은 아니다.

## VIS-007

**체크 상태와 조작 플래그 백업을 각 Gizmo가 소유하도록 한다**

- 모듈: 공통 VTK / Gizmo 그룹
- 판정: 착수 가능 · 제안 우선순위 P2 · 측면 태그 C, E
- 사용자 결과: 그룹 멤버 삭제·재선택으로 다른 기즈모의 활성 상태가 어긋나지 않는다.
- 선행: 없음
- 기존 이슈: [#322](https://github.com/NumeRealWorks/DashOpti_GUI/issues/322)

**변경 범위**

- GizmoGroup의 _active/_savedState 인덱스 병렬 저장을 멤버 소유 checked/restore 상태로 옮긴다.
- 체크 중복 호출을 멱등으로 만들고 removeMember/그룹 파괴 시 원래 조작 플래그를 복원한다.
- 그룹은 멤버 집합과 집단 변환만 담당하도록 한다.

**완료 조건**

- 두 번 check 후 uncheck해도 원래 축·슬라이더 상태를 복원한다.
- 체크된 중간 멤버 제거가 나머지 멤버와 체크 상태를 바꾸지 않는다.
- 그룹 해제·파괴 후 기즈모가 조작 불능으로 남지 않는다.

**검증 방법**

- idempotent check, remove middle, destroy group, flag restore 단위 검증.
- 모핑 그룹 생성·그룹 이동·해제/삭제 GUI 검증.

**근거**

- `libs/DashGizmo/src/GizmoGroup.cpp:40 removeMember; :67 setChecked`
- `libs/DashGizmo/include/GizmoGroup.h:_members/_active/_savedState`

**범위·결정 메모**

VIS-006 이전/이후 어느 쪽도 구현 가능하나 경로 이동 먼저가 충돌이 적다. GEO-002와 같은 interaction 표면의 변경을 조율한다.

## AST-001

**파일·폴더 묶음의 덮어쓰기를 실패 시 복구 가능한 교체로 만든다**

- 모듈: Project Assets / 파일 교체
- 판정: 착수 가능 · 제안 우선순위 P1 · 측면 태그 A, C
- 사용자 결과: 복사 실패가 기존 파일·프로젝트 등록·연동 Set·화면을 손상시키지 않는다.
- 선행: 없음
- 기존 이슈: [#616](https://github.com/NumeRealWorks/DashOpti_GUI/issues/616), [#645](https://github.com/NumeRealWorks/DashOpti_GUI/issues/645)

**변경 범위**

- 새 콘텐츠를 임시 위치에 준비·검증한 후 교체하고 실패 시 이전 파일/동반 폴더를 복구한다.
- 성공이 확정된 뒤에만 registry invalidation·트리 재구성·연동 소비자 갱신을 통지한다.
- 단일 deck 외에 #651의 wbpj+_files 및 stli 상위 폴더 묶음, 같은 위치 파일, 이름 충돌을 포함한다.

**완료 조건**

- 단일 파일 및 동반 폴더 복사 중 실패를 주입해도 기존 바이트·원장 uuid·Set·표시가 유지된다.
- 성공하면 한 번의 변경 통지로 모든 관련 소비자가 새 세대로 갱신한다.
- 이미 프로젝트 안인 파일을 자기 자신 위에 복사/삭제하지 않는다.

**검증 방법**

- 임시 디렉터리에서 복사/교체/폴더 중간 실패·거절·같은 경로 회귀 검사.
- 기존 GP·Condition·Launcher를 가진 프로젝트에 덮어쓰기 성공/실패 GUI 검증.

**근거**

- `view/DashMainWindow.cpp:2700 copyFileIntoProject; :2713 discard→remove→copy`
- `view/DashMainWindow.cpp:2731 discardLoadedReferenceFile`
- `sources/pr-651.diff:1083 wbpj companion removeRecursively→copy`

**범위·결정 메모**

dev에서 원장/Set을 직접 삭제하는 코드는 확인되지 않았다. 실제 선삭제는 파일·context·tree이므로 원 이슈의 원장 유실 표현을 그대로 사실로 확정하지 않는다. #651 진행 중 구현과 조율하고 파일 실패 안전성은 별도 완료 조건으로 검증한다.

## AST-003

**RW 파싱과 문서 수집을 GUI 밖에서 실행하고 적재 수명을 보장한다**

- 모듈: Project Assets / FE deck 적재
- 판정: 보류 · 제안 우선순위 P2 · 측면 태그 B, E
- 사용자 결과: 대형 deck을 읽는 동안 화면이 응답하고 오래된 적재가 새 프로젝트/선택을 덮지 않는다.
- 선행: 없음
- 기존 이슈: [#458](https://github.com/NumeRealWorks/DashOpti_GUI/issues/458)

**변경 범위**

- DashRwActor의 SDK 소유 스레드를 GUI에서 전용 실행 영역으로 옮기고 open/clone/read/edit/export/close·종료 순서를 명시한다.
- 호출부가 BlockingQueuedConnection으로 GUI를 오래 기다리지 않도록 실제 무거운 호출의 await 경계를 구성한다.
- 이미 있는 registry load의 중복 대기·프로젝트/경로 generation을 유지·검증하고 취소/종료의 결과를 소비자에 전달한다.

**완료 조건**

- 대형 deck 적재 및 DOE exportDoeSample→clone/edit/export 소비 경로의 무거운 SDK 작업이 GUI에서 실행되지 않음을 thread/time trace로 확인한다.
- 같은 파일 동시 적재·빠른 프로젝트 전환·파일 교체·연속 선택·적재 중 종료가 유실/오염/영구 대기를 만들지 않는다.
- 최종 actor 연결은 GUI에서 수행되며 결과 수명과 SDK 메모리가 분리된다.

**검증 방법**

- GUI heartbeat와 단계별 thread/time trace, 두 크기 deck의 전후 실측.
- generation invalidate/dedup 및 종료·늦은 결과 회귀 테스트; 기존 RW fake-module 테스트 확장.

**근거**

- `controller/DashRwActor.cpp:96 GUI affinity; :137 factory parse`
- `controller/DashRwActor.h:137 invokeOnActor`
- `controller/DashAnalysisModelContextRegistry.cpp:53 load; :105 inFlight; :143 generation`
- `controller/DashAnalysisModelContext.cpp:31 load`
- `controller/DashRwDocumentHandle.cpp:60 GUI actor 동기 실행 주석; :141 exportContent; :151 clone`
- `controller/DashDoeBatchChain.cpp:216 exportDoeSample`

**범위·결정 메모**

이슈 Deferred 유지. registry의 기존 generation/dedup은 보존한다. co_await API여도 DashRwDocumentHandle은 GUI actor에서 suspend 전 동기 완료될 수 있으므로 AL-12 이후 남는 RW 작업의 실제 thread 이관도 여기서 소유한다. VTK actor는 GUI에 연결한다. ANSYS Motion 자체 solver 경로 개편은 범위 밖.

## CON-001

**참조 파일 교체 후 조건 목록과 DV 바인딩을 새 문서로 갱신한다**

- 모듈: Condition Parameter / 참조 파일 변경
- 판정: 선행 작업 후 · 제안 우선순위 P1 · 측면 태그 A, C, D
- 사용자 결과: Add File로 같은 경로를 교체해도 이전 부품·하중·강조 표시가 남지 않는다.
- 선행: AST-001
- 기존 이슈: [#645](https://github.com/NumeRealWorks/DashOpti_GUI/issues/645)

**변경 범위**

- 성공한 자산 교체의 경로/세대 통지를 받고 현재 및 비활성 Condition 모델을 갱신하거나 다음 진입 때 갱신되도록 표시한다.
- 부품·하중·조건 표와 강조 actor를 새 문서로 바꾸고 사라진 symbol을 기존 row index로 재사용하지 않는다.
- 기존 DV 선택은 의미상 같은 항목에만 유지하고 삭제/변경된 바인딩의 처리를 사용자에게 설명한다.

**완료 조건**

- 다른 하중/부품을 가진 같은 이름 파일 교체 직후와 재진입 후 새 목록이 보인다.
- 다른 경로를 참조하는 Set은 바뀌지 않고 실패한 교체는 기존 문서를 유지한다.
- 늦은 refresh가 새 Set/프로젝트에 반영되지 않는다.

**검증 방법**

- 기존 TestConditionParameterization의 loadGeneration/revision 테스트에 같은 경로 교체와 symbol 삭제를 추가한다.
- Assets 덮어쓰기→Condition 표/강조/DV→실행 입력의 일관성을 GUI 확인한다.

**근거**

- `view/DashConditionParameterizationWidget.cpp:77 연결은 DV watcher뿐; :441 refreshFromFile`
- `model/DashConditionParameterization.cpp:125 refreshFromLoadedAnalysis generation`
- `controller/DashAnalysisModelContextRegistry.cpp:161 publish documentChanged; :353 invalidate`

**범위·결정 메모**

registry displayedContextChanged는 표시 커서 이벤트라 문서 내용 변경 통지와 혼동하지 않는다. Condition의 자기 편집 후 publish를 무조건 재로드해 진행 중 편집을 덮는 연결도 피한다.

## CAD-001

**CAD 요청의 의도와 완료 결과를 동일한 요청 식별자로 왕복시킨다**

- 모듈: Geometry Parameter / NX CAD
- 판정: 보류 · 제안 우선순위 P2 · 측면 태그 B, C, E
- 사용자 결과: 대화형 형상 편집과 배치 요청이 모드 플래그에 의해 서로의 완료/실패를 받지 않는다.
- 선행: 없음
- 기존 이슈: [#249](https://github.com/NumeRealWorks/DashOpti_GUI/issues/249)

**변경 범위**

- load/update 요청에 request ID·출처·산출 경로를 담고 성공/실패 결과가 이를 유지한다.
- m_batchMode와 배치 전용 통지를 제거하고 구독자가 요청 식별자로 결과를 수신한다.
- CAD UI·배치 실행·Runner 소비자의 연결과 해제를 요청 수명에 맞춘다.
- nxCadParametersJson도 요청/PRT 식별을 보존하여 늦게 도착한 파라미터를 현재 다른 CAD Set에 적용하지 않는다.

**완료 조건**

- 같은 파일에 서로 다른 요청이 들어와도 완료/실패가 각 요청에 한 번씩 돌아간다.
- 실패가 load/update 종류를 잃지 않고 취소/소유자 소멸 후 다른 요청을 완료시키지 않는다.

**검증 방법**

- 외부 NX를 띄우지 않는 fake command completion으로 성공/실패/순서 뒤바뀜 검증.
- NX 가용 환경에서 대화형 load/update와 배치 교차 실행.

**근거**

- `controller/DashSolverNxCad.h:27 enqueue; :31 setBatchMode; :36 signals`
- `controller/DashSolverNxCad.cpp:203 mode branch; :221 emitFailure`
- `view/DashGeometryParameterCADWidget.cpp:79 nxCadParametersJson 무조건 현재 mModel 적용`

**범위·결정 메모**

현재 Deferred 우선도를 유지한다. Direct Launch/Workbench job 중복·구독 전량 해제 정리는 execution 담당이 별도로 판단한다. 새 CAD 기능이나 CAD 프로젝트 누수 해결(#560 완료)은 포함하지 않는다.

## CAD-002

**CAD 로드·프리뷰의 진행 표시 시작과 종료를 요청 수명에 맞춘다**

- 모듈: Geometry Parameter / CAD 진행 표시
- 판정: 착수 가능 · 제안 우선순위 P2 · 측면 태그 B, D
- 사용자 결과: PRT 로드가 끝나면 Loading 표시가 사라지고 Upper/Lower 프리뷰는 실행 중임을 보여준다.
- 선행: 없음
- 기존 이슈: [#464](https://github.com/NumeRealWorks/DashOpti_GUI/issues/464)

**변경 범위**

- load 성공·실패·표시 실패·중도 이탈에서 진행 표시를 정리한다.
- 프리뷰 enqueue 승인 시 진행을 시작하고 완료·실패와 짝지으며 다른 요청의 진행 표시를 종료하지 않는다.

**완료 조건**

- PRT 성공 후 Loading이 남지 않는다.
- 프리뷰 성공/실패와 연속 요청에서 busy 표시가 실제 실행과 일치한다.

**검증 방법**

- fake NX 완료/실패 신호로 진행 상태 전이 검증.
- NX 가용 환경에서 Load/Upper/Lower/실패/연속 클릭 확인.

**근거**

- `view/DashMainWindow.cpp:317 실패 stop; :3203 성공 stop 부재`
- `view/DashGeometryParameterCADWidget.cpp:710 enqueuePreview 시작 부재`

**범위·결정 메모**

CAD-001 요청 태그 일반화를 기다리지 않고 현재 요청 경계를 명시해 수정할 수 있다. 전역 busy 규약은 root 작업과 맞춘다.

## CAD-003

**CAD DV 하한·상한을 검증하여 잘못된 범위를 저장·실행하지 않는다**

- 모듈: Geometry Parameter / CAD 입력
- 판정: 착수 가능 · 제안 우선순위 P2 · 측면 태그 A, D
- 사용자 결과: Lower가 Upper보다 큰 범위와 비유한 값이 preview/DOE 설정으로 전달되지 않는다.
- 선행: 없음
- 기존 이슈: [#487](https://github.com/NumeRealWorks/DashOpti_GUI/issues/487)

**변경 범위**

- CAD bounds setter와 DV JSON 생성/읽기에 유한성·lower≤upper 검증을 적용한다.
- 양 끝값 개별 편집과 Add Values 일괄 적용에서 오류를 설명하고 유효한 이전 범위를 보존한다.
- 실제 허용 범위·단위/의미를 입력 툴팁에 안내한다.

**완료 조건**

- lower>upper 및 비유한 값을 저장/실행 전 거부한다.
- 일괄 offset 실패가 선택 행 일부만 잘못된 값으로 남기지 않는다.
- 유효한 음수·0·지수 규모 값은 CAD 파라미터 의미에 맞게 허용한다.

**검증 방법**

- bounds setter와 JSON 왕복에서 경계값·역전값·비유한 값 검증.
- Upper/Lower 편집 및 Add Values 이후 DV 표·preview 값 일치 확인.

**근거**

- `model/DashGeometryParameterCAD.cpp:192 setIndependentParameterBounds`
- `view/DashGeometryParameterCADWidget.cpp:411 spin 범위; :740 onCadApplyAddValues`
- `viewmodel/DashGeometryParameterCADPresentationModel.cpp:36 min/max 직접 기록`

**범위·결정 메모**

임의로 모든 CAD 값에 양수 제한을 추가하지 않는다. 저장 원자성은 root IO-02, shared DV 스키마 규약은 execution 담당과 접점이다.

## CON-002

**조건 숫자 편집기에 SDK 스키마 범위와 오류 안내를 적용한다**

- 모듈: Condition Parameter / 숫자 편집
- 판정: 착수 가능 · 제안 우선순위 P2 · 측면 태그 D
- 사용자 결과: 정수 외의 number 조건도 허용 범위를 편집 시 알려주고 잘못된 입력을 조용히 제출하지 않는다.
- 선행: 없음
- 기존 이슈: [#487](https://github.com/NumeRealWorks/DashOpti_GUI/issues/487)

**변경 범위**

- number QDoubleValidator에 제공된 minimum/maximum 및 스키마 경계 의미를 적용한다.
- 지수 표기와 number-or-reference 입력을 유지하면서 범위·단위 툴팁과 검증 실패 안내를 연결한다.
- SDK가 최종 검증을 거부하면 기존 값 유지·entryEditFailed 경로를 유지한다.

**완료 조건**

- 스키마의 범위 밖 숫자는 로컬에서 식별되고 유효한 경계값·지수값은 정상 전달된다.
- 참조 문자열은 숫자 검증 때문에 막히지 않고 실패 시 기존 값이 유지된다.

**검증 방법**

- delegate 테스트에서 number/int/number-or-ref 및 경계 조건 비교.
- TestConditionParameterization의 실패 보존 회귀와 실제 조건 편집 검증.

**근거**

- `view/delegate/DashFeConditionValueDelegate.cpp:90 integer min/max; :102 number validator 범위 미적용`
- `view/delegate/DashFeConditionValueDelegate.cpp:149 입력 승인`
- `model/DashConditionParameterization.cpp:371 commitEntryValue`

**범위·결정 메모**

현재 검증이 전혀 없다는 구 이슈 문구는 틀리다. 정수 범위·숫자 문법·SDK 검증은 존재하므로 number 범위와 안내만 잔여로 잡는다. 스키마가 범위를 제공하지 않으면 임의 물리 한계를 만들지 않는다.
