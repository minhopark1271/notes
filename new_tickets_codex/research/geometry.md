# Geometry / CAD / Condition / Project Assets / VTK 조사

## 기준과 조사 방법

기준 코드는 local dev `b08a91b39bbdb7c3b75796ff2cd7f663d53258ef`이며 root가 원격 dev 동일성을 확인했다. 코드 변경·빌드·GUI 실행·GitHub mutation은 하지 않았다. 문서와 코드의 정적 대조, 열린 PR diff 검토를 수행했다. 이 문서의 완료 판정은 기존 완료 이력+현재 구현 존재 확인이며 새 실행 검증 통과라는 뜻이 아니다.

읽은 원본: sources/issues의 담당 이슈 본문·최신 댓글, `pr-654.diff/json`, `pr-651.diff/json`. 보드 외 #577은 #499/#654에서 연결된 필수 결정으로 추가 확인했다. 과거 위키/이슈의 클래스명·행수·스레드 설계보다 현재 코드와 최신 결정에 우선순위를 두었다. 직접 CLI API 404 이후 root가 제공한 인증 스냅샷으로 PR diff를 읽었다.

결과: `../modules/geometry.json` 및 `.md` 22개 카드, `geometry_dispositions.json` 42건 처분. PR 크기는 억지 파일 분할 없이 사용자 결과와 독립 검증 단위로 잡았다. in_flight 카드 두 개는 각각 기존 PR의 담당 범위라 새 중복 PR를 뜻하지 않는다. GEO-007은 구현 필요가 아직 확정되지 않은 실측 게이트다.

## 모듈과 사용자 흐름

| 영역 | 확인한 흐름 | 구현/결정의 현 상태 | 남은 카드 |
|---|---|---|---|
| Morphing | 참조 deck/part 진입→영역/핸들 생성→선택/그룹→범위·반경→preview→Lower/Upper QC→Proceed→저장→재진입→DOE/Runner/Optimizer 소비 | 값 경계·Run·local 서비스·주입은 구현. dev 저장은 VTP+JSON; PR654는 Setup/Configuration+JSON으로 전환 중 | GEO-001~007 |
| 고정 영역 | 영역 칠하기→Constraints 행→Hide/Show→저장→Set 왕복→고정점 실행 | dev의 visible IDs가 membership까지 바꿈. JSON 저장 비대칭. 새 상태기의 unpinned 스펙이 후속 정본 | GEO-003 |
| Hexahedron/Marching Plane | Volume 유형→파라미터→생성→edge/face DV→QC→archive | Cylinder 삭제/Box FFD 신규가 최신 확정. PR654 section 핸들 어댑터 후에도 MarchingPlaneBound 원본 절단기 잔존 | GEO-004,005 |
| CAD | PRT 로드→NX 파라미터→lower/upper→preview→DV 저장→배치 | 요청 mode 의존과 진행 표시 비대칭, bounds 교차 검증 부재. CAD 모델 프로젝트 청소는 완료 | CAD-001~003 |
| Condition | 참조 Set 진입→FE condition 편집→DV 선택/범위→저장→파일 교체/재진입 | immutable document 편집·revision/loadGeneration 방어·schema editor 있음. Assets 교체 notification 연결과 number 범위 UI 잔여 | CON-001,002; 공통 저장 IO-02 |
| Assets | Add File→복사/중복→원장/연동 Set→트리 표시→덮어쓰기→삭제→프로젝트 전환 | 같은 경로 교체 전에 파일/context/tree를 먼저 제거. PR651 특수 포맷이 진행 중 | AST-001~003 |
| 공유 VTK | 문서 Load→모듈 간 전환→preview/result→split→원래 문서 복귀→파일별 눈 토글 | Layer는 소유자 구분이 없고 외부 actor 목록과 renderer가 불일치. split 탈출은 Runner만 호출 | VIS-001~005 |
| Gizmo | checked/group 변환→멤버 삭제/그룹 해제→모델 이탈; 빌드 | 인덱스 병렬 상태·독립 임시 static target 잔존 | VIS-006,007 |

## 중요한 사실 정정

### 핸들 이행은 두 개의 구현 상태를 분리해야 한다

- dev `DashMorphingController.cpp:1052`에 Eigen greedy sampling, `DashHandlePickingInteraction.h:241`에 수정 가능한 `m_handleGeometry` 정본이 존재한다.
- dev `DashGeometryParameterPresentationModel.cpp:381`은 `handles_vtp`를 쓰며 `:479` constraints 배열을 읽지만 저장하지 않는다.
- PR654 diff는 `DashHandleState`, state JSON, sampling, archive, consumer를 추가하고 VTP 소비를 걷어낸다. `DashHandleImport`는 기존 편집 polydata를 값 모델로 변환하는 과도기 어댑터다.
- PR654의 `DashHandleSets::section`은 기존 l2g/bounds를 SectionFrame으로 변환한다. diff에서 `section_frames` 호출 도입은 없고 기존 `DashMorphingController`의 MarchingPlaneBound 생산 경로는 남는다. 따라서 GEO-005는 이미 끝난 SectionFrameHandles 도입을 반복하지 않고 원본 단면 추출기를 교체한다.
- PR654의 숫자/반경 검증(`std::isfinite`, lower≤upper)은 GEO-001에 포함한다. 기존 #487의 ‘검증 사실상 없음’을 GP에 그대로 적용하지 않는다.
- 최신 #332 댓글로 per-handle 반경 UI는 종결. 최신 #577로 cylinder 복원은 철회, Hexahedron은 BoxHandles FFD 신규. 구 shell 격자 동일성 요구를 되살리지 않는다.
- 구 Set 자동 migration은 PR654에서 명시적으로 제외되었다. 구 파일 무변경·재작성 안내가 완료 조건이다.

### #281을 그대로 다시 구현하면 완료된 작업을 중복한다

현 `DashMorphingUtils::performMorphingAndExport`는 `freezeDoeBatch`/`runDoeBatch`를 `co_await`하고 별도 문서로 export한다. `DashMorphingDoeExecutor::Execute`도 같은 service 경로다. `DashMorphingRun`과 입력 collector가 계산/수집 경계를 제공한다. WorkerJob·MorphingGate·레인 복원은 현재 요구가 아니다.

실제 잔여는 QC 결과창 신호 유실(GEO-006), #586이 보류했다고 적은 교차 모듈 GUI 검증(GEO-007), downstream의 요청 수명/취소, AST-003의 RW 실제 파싱 스레드 이관이다. #586의 기존 산출물 바이트 비교 보류를 새 sampling에 동일성 요구로 그대로 넘기지 않는다.

### QC 결과창 결함은 현재 코드로 확인된다

`DashMeshQualityDialog.cpp:164`가 `processEvents(AllEvents,100)`을 호출한다. 위젯 `:1456`은 close-cancel 연결을 먼저 끊고 setResults를 호출한 뒤 `:1463`에 finished를 await한다. 결과 표시 내부 재진입에서 닫힘이 지나가면 다음 await가 대기할 수 있다. 단순 ‘qCoro wrapper 변수를 먼저 생성’이 즉시 connect 보장은 아닐 수 있으므로 구현자는 이벤트 펌핑 제거와 실제 구독 시점을 검증해야 한다. `TestMeshQcStates`는 계산 상태 테스트이고 현재 driver도 이 결과창 타이밍을 직접 검증하지 않는다.

### Add File 손상 범위를 실제 코드에 맞췄다

`copyFileIntoProject:2700`은 overwrite 승인 후 `discardLoadedReferenceFile`→`QFile::remove(dest)`→`QFile::copy` 순서다. discard는 Geometry UI release, registry invalidate, tree remove를 수행한다. 코드 주석과 실제 구현상 원장·연동 Set 자체는 유지한다. 따라서 ‘실패하면 원장 등록이 반드시 삭제된다’고 확정하지 않는다. 입증된 문제는 이전 파일 선삭제·context/tree 폐기와 실패 후 복구 없음이며 이들이 원장/Set과 불일치하는 것이다.

PR651 diff는 `.wbpj` 파일 복사 뒤 companion 폴더를 `removeRecursively`하고 copy한다. 따라서 파일 하나만 atomic write로 바꾸면 묶음 실패 문제는 남는다. AST-001은 staging/교체/복구를 문서와 동반 폴더 단위로 검증하고, 성공 통지 후에 CON-001이 갱신하도록 나눈다.

### Deck load는 코루틴 여부와 실제 스레드를 구분한다

`DashRwActor.cpp:96`은 GUI thread affinity를 assert한다. `doOpenInstance`의 SDK factory가 parsing을 수행하며 `invokeOnActor`는 다른 스레드에서 부르면 BlockingQueuedConnection이다. 즉 호출 API가 QCoro라고 파싱 워커화가 완료된 것은 아니다.

동시에 registry에는 이미 path/project generation과 inFlight dedup이 있다. 예전 #529 PoC의 m_pending 구조에 관한 경고를 근거로 지금의 guard를 무조건 지우거나 ‘비동기 기반 없음’으로 다시 만들지 않는다. AST-003은 actor 생명주기/실제 실행 스레드/호출자 await를 함께 다룬다. `createVisualActor:129`에서 표면 변환도 이루어지지만 과거 206~263 ms를 현재 실측값으로 쓰지 않는다. 파싱 이관 후 다시 계측해 유의한 GUI 잔여만 추가 이관한다.

### VTK 결함은 Project Assets 개편 후에도 남는다

- Optimizer `:1757` 전체 actor 삭제가 관리 밖 핸들/피킹까지 지운다.
- MainWindow `:4755` FE actor 숨김과 `:4587` 직접 actor 제거가 남고, manager 등록은 append하여 수명 불일치가 가능하다.
- RenderingManager `clearAllLayers`는 5개 Layer와 장식만 정리한다. 해결은 모든 FE actor 삭제 확대가 아니라 문서 보존/작업물 정리 정책이다.
- split view의 main `SetDraw(false)`와 `clearSplitView` 복원 사이 외부 호출은 Runner preview뿐이다.
- ModelingTreeWidget `:397`이 vtk_parent+vtk_single을 실제 만든다. `.vtk/.vtu` cache map의 삽입은 없다. UI 개편으로 폐기된 기능이라고 처분할 수 없다.
- #318에서 확정한 renderer 하나, 모듈 actor 소유, 등록 단일 창구, 문서 보존/작업물 폐기 원칙을 따랐다. transient 핸들 actor 전체를 새 추상화로 이동하는 광범위 작업은 추가하지 않았다.

### 숫자 입력과 CAD 진행 상태

CAD bounds setter `model/DashGeometryParameterCAD.cpp:192`는 lower/upper를 바로 기록하며 PM이 JSON에 직접 쓴다. UI SpinBox 범위가 크기 상한을 제공하지만 하한≤상한 검증을 대체하지 않는다(CAD-003).

Condition delegate는 integer minimum/maximum, 숫자 문법, 참조 문자열 검증이 이미 있다. number editor는 스키마 minimum/maximum을 QDoubleValidator에 넘기지 않는다(CON-002). SDK 최종 검증이 있을 수 있으므로 데이터 오염이 입증됐다고 쓰지 않고 입력 단계 일관성/안내 작업으로 분류한다.

CAD load 실패는 진행 표시를 멈추지만 onNxLoadPrtStepReady 성공 경로는 stop을 호출하지 않는다. enqueuePreview는 시작 통지 없이 NX에 요청한다(CAD-002). CAD 요청 ID 일반화(CAD-001 Deferred)를 전제하지 않아도 비대칭 수정은 가능하다.

## 완료 이력 검증 표본

| 기존 이슈 | 현재 근거 / 처분 |
|---|---|
| #560 | `model/DashProject.cpp:1380` qDeleteAll(m_geometryParametersCAD)+clear 확인. 재작업 제외 |
| #503 | `DashMorphingSettings.cpp:1785` browseButton을 캡처해 `physicsRowOfWidget`으로 현재 행 조회. 고정 row 캡처 결함 해결 |
| #599 | `DashProject.cpp:1043` Geometry 고정 variant 이름·중복 gate와 DOE 고정 이름 흐름 존재 |
| #605 | Manager의 MorphFromDoeSamples/등록 API 제거, executor 옆 runDoeBatchForSet 존재 |
| #362/#361 | displayed 명명과 root-relative path 코드 존재 |
| #428 | interaction 의존 주입/배열 이름 분리 현 구조와 부합. 아직 남은 polydata 정본은 #430 후속으로 구분 |
| #403/#408/#422/#586 | Run/Service/collector/Result 오류 경계가 현존하며 local 서비스가 옛 레인 설계를 대체 |
| #243/#546 | 이슈 완료 이력과 해당 UI/handle tree 코드 확인. 모든 예전 GUI 시나리오 재실행은 하지 않음 |

## 다른 담당과의 접점

- root IO-06: #423 default 정책. Set radius 정본과 코드 읽기 fallback 정책을 맞춘다.
- root IO-02: GP/CAD/Condition 저장 왕복·atomic JSON 계약. GEO-001의 archive 이관과 CON 값 편집 구현을 중복하지 않는다.
- root #434: interaction/visualizer 객체 소유 이동. GEO-002의 데이터 정본 소유와 목적을 구분하고 파일 변경을 조율한다.
- execution: #616의 Launcher/fe-safe 실행은 execution, 자산 복사·원장·Condition 미생성은 AST-002. #557 legacy source 판단도 execution. PR651 한 개의 부분 카드이므로 실행 순서에서 병합 게이트를 함께 묶는다.
- downstream: #316은 VIS-001, #457 요청 ID/취소/비동기 수명은 OPT. Runner/Optimizer의 empty stop_token 전달 및 위젯 수명은 downstream 검토 범위. Builder split view exit는 VIS-004 소유.

## 제약과 착수 전 확인

1. 코드/PR diff 정적 조사가 완료됐으며 Windows 앱·NX·RW/solver 실제 실행은 하지 않았다. 제시한 validation은 후속 PR의 완료 조건이지 이번 실행 결과가 아니다.
2. PR654의 기존 56/56 테스트·빌드 결과는 PR 작성자 보고다. GUI 미실행은 명시적 잔여다.
3. CAD-001과 AST-003은 기존 Deferred를 유지했다. 필요 없다고 철회한 것으로 보지 않는다.
4. GEO-007 검증 결과가 통과하면 구현 PR 없이 증거 문서로 완료될 수 있다. 발견되지 않은 신규 결함을 미리 창작하지 않는다.
5. 신규 AI Geometry/미노출 CAD mesh 기능을 일반 개선이라는 이유로 확장하지 않았다. 현재 지원 흐름과 유효한 요구에 한정한다.
6. 문서 링크·의존성·이슈 대응 검수는 root 통합 단계가 수행한다. 각 카드 증거는 기준 커밋 좌표이며 PR diff 좌표는 `sources/` 파일 내부 줄이다.
