# 보드 밖 OPEN 이슈 (수집 누락)

> Projects #16 보드만 수집했기에 01-sources/open_issues/ 에 없는 GitHub OPEN 이슈 전수.  2026-10-06 기준 138건 중 26건.

| # | 라벨 | 제목 |
|---|---|---|
| #315 | area:MainWindow area:LeftPanel bugfix blocked | Load 버튼 재클릭 시 하이라이트 유지하고 재로드 무시 |
| #323 | - | Morphing 설정 저장 실패가 사용자에게 알려지지 않음 (DashGeometryParameterWidget) |
| #326 | - | DashMorphingController::readCSVFile: 비수치 밀도 값에서 std::stod 예외가 잡히지 않아 앱이 종료됨 |
| #327 | - | DashMorphingController::onGenerateAutomaticHandles: K 클램프가 고정점 제거 전에 이뤄져 오류 판정·팝업 수치가 어긋남 |
| #328 | - | Logger: 스레드 이름 알림이 sink 필터에 걸리면 그 sink는 이름 줄을 받지 못함 |
| #334 | bugfix | preprocessor 레거시 어댑터 — Ansys Motion 축 2건 미발행 |
| #337 | docs blocked | 이행 산출 운영 지식을 상설 문서로 추출 — docs format 확정 선행 |
| #375 | bug | Surface handle selection 이, drag selection 시 모든 표면 영역을 cover 하지 못하는 버그 |
| #393 | - | GenerateMarkerPointsFromSurfaceIds 의 실패·빈 결과가 호출부 3곳에서 조용히 넘어간다 (#325 후속) |
| #394 | bug | SaveProjectAs 가 모든 실패를 무시하고 true 를 반환하는 문제 |
| #404 | bug | Analyzer: "(std)" 축약이 표준편차가 아니라 최댓값으로 조용히 떨어진다 |
| #425 | bug infra | 훅의 테스트 레인이 VS 18 + CMake 3.31 기계에서 커밋·push 를 막는다 — 생성기가 NMake Makefiles 로 대체된다 |
| #495 | - | plotSpecReady 재연결 직전 disconnect 4곳이 교체 뒤 모델을 대상으로 한 죽은 코드 |
| #497 | - | setModel 류 함수의 자식 sender 연결 누적을 잡는 lint — (a) 유형만, 훅 연결 전제 |
| #498 | - | DashXmlParser: 변수가 없는 샘플을 건너뛰어 변수별 인덱스↔샘플 대응이 어긋난다 |
| #516 | docs split-group:451 | [참고] processEvents 펌핑 53곳 구조별 분류 — 크래시 취약점 파악 (a2222cc 기준) |
| #532 | - | 참조: XML 읽기 성능 축(#413)과 관계된 위키 문서 |
| #540 | - | TopOptPostprocessDialog: Non-design Domain 행 높이 손계산 — fallback 이 죽어 측정 실패가 드러나지 않는다 |
| #552 | - | DashAsyncJobContext: QtConcurrent callable 오버로드라 실행 중 취소가 불가능하다 |
| #555 | performance | 덱 적재 40초 — 컨테이너 아닌 전 심볼에 get_data 를 던져 Mesh 를 찾는 탐색 루프를 심볼 타입 기반으로 |
| #558 | backlog | #534 후속 — 항등이 아닌 instance transform 을 가진 실제 어셈블리 덱으로 partNames/editablePartNames 분리를 확인 |
| #567 | - | tests: 소스 파일명 규칙을 정하고, 테스트 코드의 식별자를 네이밍 컨벤션에 맞춘다 |
| #577 | - | fix(view): Volume 핸들 생성기 — cylinder 삭제, Hexahedron 은 mesh-ops BoxHandles FFD 로 신규 |
| #628 | feature | STEP converter feasibility check: CAD(STEP) -> inp 변환 가능성 검토 |
| #641 | in-progress feature | CAD(STEP) + inp 입력: CAD 보관과 NSET 의 CAD entity match |
| #644 | bug | Morphing: 저장된 part 가 있는 Set 에서 VTP 복원 실패 뒤 다른 part 로 Start Morphing 하면 핸들·DV 를 유지한 채 대상만 바뀐다 |
