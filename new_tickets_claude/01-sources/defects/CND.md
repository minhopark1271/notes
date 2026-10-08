# 결함 색인 — CON

> 출처: 01-sources/wiki/Cross-Module-Defect-Index.md (좌표 cf44c25 기준 정적 판정, 런타임 검증 없음). 설명 전문·좌표는 01-sources/wiki/Code-Map-User-Flow-*.md 의 같은 ID. **현행 코드(dev @ b08a91b3) 재검증 필수.**

| 성격 | ID | 결함 | 귀결 |
|---|---|---|---|
| 1 정본 이중화 | CON-D4 | `.ui` 의 열 선언 5열과 모델 7열이 드리프트 | 런타임은 모델이 덮어써 증상이 없지만 디자이너 편집이 무효다 |
| 2 왕복 단절 | CON-D5 | Value 인라인 편집이 메모리 deck 만 바꾸고 설정 JSON 에 대응 키가 없다 | 모듈을 떠났다 돌아오면 편집이 사라지고 되돌리기 경로도 없다 |
| 2 왕복 단절 | CON-D10 | 대상 deck 이 전역 active context 1개뿐, Set 별 저장 필드가 없다 | 프로젝트를 재로드하면 사용자가 deck 을 다시 열어야 표가 채워진다 |
| 2 왕복 단절 | CON-D13 | ResultsAnalyzer 가 `paramObj["checked"]` 를 읽는데 그 키를 쓰는 코드가 없다 | 조건 DV 는 그 변수 목록에 절대 들어가지 않는다 (실제 키는 `boolean`) |
| 3 조용한 실패 | CON-D12 | 조건 DV 주입 실패 3종이 전부 `continue` | 조건 DV 가 하나도 적용되지 않아도 기준값 그대로 export 되고 성공으로 집계된다 |
| 5 공유 상태 오염 | CON-D6 | GUI 편집과 DOE 배치가 같은 RW 세션을 공유하는데 상호 배제가 없다 | 원복 실패 시 GUI 세션에 주입값이 남아 화면 표시와 이후 샘플 export 가 오염된다 |
| 7 스레드 경계 | CON-D2 | `getOrLoad` 의 실제 로드가 뮤텍스 밖에서 돈다 | 같은 미캐시 deck 을 동시 요청하면 파싱이 두 번 돌고 하나가 버려진다 |
| 8 암묵 계약 | CON-D1 | `setProjectDirectory` 가 인자를 쓰지 않고 경로를 다시 유도한다 | 호출 3곳이 서로 다른 값을 넘기며, 인자를 신뢰한 호출이 추가되면 조용히 무시된다 |
| 8 암묵 계약 | CON-D8 | DV 섹션 판정이 파일명에 `"Condition"` 이 포함되는지 | 매칭되지 않는 파일명은 경고 없이 `DV-Condition` 으로 기본 처리된다 |
| 11 수명·정리 누락 | CON-D3 | `m_params` 가 한 번도 clear 되지 않는다 | 어떤 deck 의 행이 표에 남아 있는지는 `source` 열로만 구분된다 |
| 12 순서 의존 | CON-D7 | `loadFromJson` 이 행을 만드는 `refreshFromLoadedAnalysis` 보다 먼저 돈다 | 세션 최초 진입에서 FE 탭 체크가 전부 해제돼 보이고, 그 상태의 [Set Design Variable] 이 절을 빈 객체로 덮는다 |
| 13 동기 실행·재진입 | CON-D9 | 자기 쓰기 억제 플래그를 되돌린 다음 줄의 모달이 중첩 이벤트 루프를 돈다 | 방금 쓴 파일의 `fileChanged` 가 그 안에서 배달돼 리로드가 한 번 더 유발된다 |
| 13 동기 실행·재진입 | CON-D11 | `get_symbol_detail` 이 캐시되지 않는다 | 표 1회 구축에 조건당 최소 3회의 RW 왕복이 발생한다 |
| 15 죽은 코드 | CON-U1 | `setModel` 오버로드의 유일한 호출 인자가 항상 `nullptr` | `dataChanged`·`dataLoaded` 를 거는 유일한 지점이 건너뛰어져 수신처가 0곳이다 |
| 15 죽은 코드 | CON-U3 | 디렉토리 워처의 `directoryChanged` 연결이 레포 전체 0곳 | `onDvJsonChanged` 의 `else` 분기와 `onDirChanged` 가 도달 불가다 |
| 16 검증 부재 | CON-U5 | `tests/` 전체에 RW 관련 5심볼 참조 0건 | 액터 마샬링·엔트리 분해·dvKey 채번·DOE 주입·원복이 전부 미검증이다 |
