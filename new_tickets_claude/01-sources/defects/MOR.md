# 결함 색인 — MOR

> 출처: 01-sources/wiki/Cross-Module-Defect-Index.md (좌표 cf44c25 기준 정적 판정, 런타임 검증 없음). 설명 전문·좌표는 01-sources/wiki/Code-Map-User-Flow-*.md 의 같은 ID. **현행 코드(dev @ b08a91b3) 재검증 필수.**

| 성격 | ID | 결함 | 귀결 |
|---|---|---|---|
| 1 정본 이중화 | MOR-D5 | 핸들 이름의 정본이 트리 아이템 텍스트와 세션 한정 `QMap` 뿐 | VTP 배열 11종에도 JSON 에도 없어 세션을 넘기지 못한다 |
| 1 정본 이중화 | MOR-D9 | 범위값의 정본이 polydata 배열이 아니라 트리 셀 위젯 | 셀 위젯에 되쓰지 않는 배열 변경 경로는 저장값과 어긋난다 |
| 2 왕복 단절 | MOR-D6 | θ 는 방향 벡터로만 저장되고 표시값은 기즈모 Euler 의 역산 | 표시되는 θy/θz 가 사용자가 입력했던 값과 같다는 보장이 없다 |
| 2 왕복 단절 | MOR-D10 | `Morphing.constraints` 는 파서만 있고 writer 가 레포에 없다 | Constraints 모드 산출물이 세션을 넘기지 못한다 |
| 2 왕복 단절 | MOR-D11 | 대상 파트가 어느 저장 경로에도 기록되지 않음 | 재로드 후 설정 완료 Set 도 시작 페이지로 떨어지고 MOR-D2 와 연쇄한다 |
| 3 조용한 실패 | MOR-D2 | geometry 부재 시 파트 검증 없이 렌더링 매니저의 base actor 로 대체 | VTP 에서 복원된 핸들 인덱스가 다른 파트 표면을 가리킬 수 있다 |
| 3 조용한 실패 | MOR-U1 | `MODE_PHYSICS` 가 `SetInteractionMode` 의 `switch` 에서 누락 | 툴바로 도달하는 살아 있는 모드인데 `default: break` 로 떨어져 픽킹 방식이 직전 모드에서 이월된다 |
| 8 암묵 계약 | MOR-D3 | Generate 분기가 타입 키가 아니라 7단 `isVisible()` 캐스케이드 | 페이지를 추가하면 캐스케이드 순서가 그대로 계약이 된다 |
| 9 위치·순서 결합 | **MOR-D14** | Geometry 카테고리는 트리 루트 1개에 모델 배열 2벌인데 Morphing 갈래만 행 인덱스로 조회 | `-CAD` Set 이 앞에 오면 뒤의 Morphing Set 이 `rowIndex >= size` 로 조기 반환돼 클릭해도 경고 없이 열리지 않는다 |
| 11 수명·정리 누락 | MOR-D12 | 명시적 리셋이 Set 이 바뀔 때만 돌고 `appendConstraintTable` 은 무조건 `insertRow` | N 회 재진입이면 구속 행이 N 배가 되어 그대로 `vtkExtractSelection` 에 투입된다 |
| 12 순서 의존 | MOR-D1 | 초기화 체인 전체가 `dataLoaded` emit 에 걸려 있고 화면 전환이 먼저 일어난다 | 설정 JSON 이 없는 신규 Set 은 화면이 뜬 채 초기화 전량이 건너뛰어진다 |
| 13 동기 실행·재진입 | MOR-D7 | 프리뷰 모핑이 GUI 스레드 동기 실행 | 프리뷰 중 스핀박스·기즈모 입력 1회마다 모핑 1회가 돈다 |
| 13 동기 실행·재진입 | MOR-D8 | `processEvents` 가 모핑 루프 안 2곳 | 볼륨 모핑 2회가 도는 사이 사용자 입력이 재진입한다 |
| 15 죽은 코드 | MOR-U2 | 툴바 Prev/Next 가 emit 만 하고 수신처가 없다 | `onEditUndo/onEditRedo` 의 TODO 와 짝 — 버튼은 눌리는데 아무 일도 없다 |
| 17 구조 잔여 | MOR-D4 | `DashHandlePickingInteraction` 3,121줄이 픽킹·기즈모·핸들 데이터·구속 오버레이 4역 | 도메인 타입 없이 polydata 배열 11종이 사실상 모델 노릇을 한다 (헤더 TODO 가 분리를 적어 둠) |
| 17 구조 잔여 | MOR-D13 | 컨트롤러가 뷰 포인터를 무가드로 역참조하는 곳 6군데 | 한 지점은 같은 포인터의 널 가드가 사용보다 뒤에 온다 |
