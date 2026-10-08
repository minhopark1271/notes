# 결함 색인 — PRE

> 출처: 01-sources/wiki/Cross-Module-Defect-Index.md (좌표 cf44c25 기준 정적 판정, 런타임 검증 없음). 설명 전문·좌표는 01-sources/wiki/Code-Map-User-Flow-*.md 의 같은 ID. **현행 코드(dev @ b08a91b3) 재검증 필수.**

| 성격 | ID | 결함 | 귀결 |
|---|---|---|---|
| 2 왕복 단절 | PRE-D7 | 설정 JSON 4섹션 중 `Dataset`·`Output Response` 를 읽는 코드가 없다 | Add·Remove 마다 파일 I/O 를 쓰고도 재진입 시 DOE·해석 타입·응답이 전부 초기화된다 |
| 2 왕복 단절 | PRE-D8 | KPI 행 추가만 `saveOutputResponseToJson` 을 부르지 않는다 | KPI 행은 표에만 존재해, 기록 경로의 유무가 행 종류마다 다르다 |
| 3 조용한 실패 | PRE-D10 | 모든 run 이 비-Done 이면 `Done` 필터 결과를 버리고 원본 배열을 쓴다 | 실패한 run 전량이 배치 입력이 되고 XML 이 값 없는 샘플로 채워진다 |
| 3 조용한 실패 | PRE-U1 | `.op2` 가 확장자 목록·파일 대화상자 필터·솔버 목록에는 있고 라우팅 분기에 NASTRAN 이 없다 | UI 에 열어 둔 확장자가 경고 없이 `AnsysMechanical` 로 처리된다 (솔버 경로 입력 UI 는 주석 처리돼 있다) |
| 8 암묵 계약 | PRE-D4 | Modal 판정이 `contains("modal")` 이고 대상이 단일 파일 모드에서는 basename | 이름에 modal 이 든 파일 하나로 모듈 전체가 Modal 모드로 넘어간다 |
| 8 암묵 계약 | PRE-D5 | `isAnsysMotion` 플래그에 `hasFunctionExpression` 이 실린다 | 필드 이름과 실제 의미가 어긋난 채 계약이 성립해, 진짜 판정이 필요해지면 재사용할 수 없다 |
| 10 규칙 중복 | PRE-D11 | KPI 5종이 배치 입력 로딩(스냅샷-또는-합성) 블록을 각자 복제 | 스냅샷 스키마가 바뀌면 고칠 지점이 6곳이다 |
| 11 수명·정리 누락 | PRE-D1 | `setModel` 에 Output Response 표 초기화가 없다 | 이전 Set 의 행이 새 Set 의 요청으로 만들어진다 |
| 11 수명·정리 누락 | PRE-D2 | `onAnalysisFileSelected` 의 조기 반환 4곳이 `endProcessing()` 을 건너뛴다 | `m_loadingDepth` 가 0 으로 안 돌아와 인디케이터가 남고 이후 emit 도 막힌다 |
| 11 수명·정리 누락 | PRE-D6 | 배치 후 DLL 상태 복원 블록이 5곳에 있고 일반 배치·Modal KPI·조회 경로에는 없다 | 일반 Process 뒤의 선택은 마지막 run 파일 하나 위에서 질의하고, 증상이 조작 순서로 갈린다 |
| 13 동기 실행·재진입 | PRE-D3 | 전용 워커·직렬 풀·게이트 0건이고 `processEvents` 25곳이 응답성을 대신한다 | 스캔·질의·배치가 도는 동안 이벤트 루프가 열려 사용자 입력이 재진입한다 (PRE-D9 와 연쇄) |
| 13 동기 실행·재진입 | PRE-D9 | KPI 경로가 `m_isProcessing = true` 보다 앞에서 반환해 재진입 가드 밖에 있다 | KPI 배치 중 Add/Remove/Preview 가 그대로 재진입한다 |
| 15 죽은 코드 | PRE-U2 | `initializePreprocessor` 의 `res`·`dfsxml` 분기가 도달하지 않는다 | 스캐너가 등록하는 Motion 결과 확장자는 `.dfr` 하나이고 `.dfsxml` 은 입력 소속이다 |
| 15 죽은 코드 | PRE-U3 | `m_dynamicTables` 는 채우고 비우기만 하고 읽는 코드가 없다 | 같은 `type` 그룹이 둘 이상이면 마지막 표만 남는데 남아도 쓰이지 않는다 |
| 17 구조 잔여 | PRE-D12 | `DashDataProcessor.cpp` 4,671줄이 스캔·질의·XML·KPI 4역 (코드베이스 단일 최대) | 고객사 KPI 전용 5함수가 1,625줄 — 파일의 35%. 빌드 가드는 3파일 9블록에 흩어져 있다 |
