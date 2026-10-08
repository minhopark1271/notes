# 결함 색인 — CAD

> 출처: 01-sources/wiki/Cross-Module-Defect-Index.md (좌표 cf44c25 기준 정적 판정, 런타임 검증 없음). 설명 전문·좌표는 01-sources/wiki/Code-Map-User-Flow-*.md 의 같은 ID. **현행 코드(dev @ b08a91b3) 재검증 필수.**

| 성격 | ID | 결함 | 귀결 |
|---|---|---|---|
| 1 정본 이중화 | CAD-D12 | 범위값의 정본이 모델이 아니라 셀 위젯의 스핀박스 | 위젯을 거치지 않고 모델만 바꾸는 경로가 생기면 저장값과 어긋난다 |
| 2 왕복 단절 | CAD-D10 | `meta.default` 에 현재값이 아니라 Lower 열 값이 들어감 | 원본 현재값이 DV JSON 에 전달되는 경로가 아예 없다 |
| 2 왕복 단절 | CAD-D11 | `Independent Parameter.Value` 저장은 `upper`, 로드는 "현재값" 으로 해석 | 데몬 JSON 만으로 채워진 행은 Lower = Upper = 현재값에서 출발한다 |
| 2 왕복 단절 | **CAD-D17** | Set ↔ `.prt` 결합이 어느 저장 경로에도 없다 (프로젝트 전역 1개) | 재로드 후 이 Set 의 대상 `.prt` 를 복원할 수단이 없고, 유일한 흔적인 configs 복사본은 CAD-D15 가 지운다 |
| 3 조용한 실패 | CAD-D14 | NX 표현식 적용 실패가 ListingWindow 에만 기록되고 stdout 으로 안 나감 | 값이 반영되지 않은 STEP 이 성공으로 처리되고, DOE 배치는 전 케이스가 같은 형상을 낼 수 있다 |
| 4 피드백 부재 | CAD-D1 | `.prt` 성공 경로에 로딩 스피너 정지 호출이 없다 (실패 경로에만 있음) | 로드가 성공하면 상태바가 "Loading …" 에 머문다 |
| 4 피드백 부재 | CAD-D9 | NX CAD 스피너가 비대칭 — 프리뷰 완료 경로에 대응하는 시작 호출이 없다 | 대화형 프리뷰는 진행 표시 없이 돌고 끝날 때만 완료 메시지가 뜬다 |
| 6 통지 미결합 | CAD-D3 | 한 명령의 두 산출물(파라미터 JSON · STEP)이 다른 채널로 도착하고 합류점이 없다 | 표가 채워진 시점과 형상이 뜬 시점의 선후를 코드가 보장하지 않는다 |
| 6 통지 미결합 | CAD-D7 | 전송 계층은 `commandId` 를 갖지만 파사드의 `emitFailure` 에 경로 인자가 없다 | `loadPrtFailed` 하나가 load 실패와 대화형 update 실패를 겸용한다 |
| 6 통지 미결합 | CAD-D8 | 방출 대상이 요청 단위가 아니라 전역 `m_batchMode` 1비트로 스위칭 | 배치 진행 중 프리뷰 버튼을 누르면 그 완료도 배치 시그널로 나간다 |
| 8 암묵 계약 | CAD-U4 | 데몬 성공·실패 판정이 `[FINISHED]` 전체 일치와 `[ERROR]` 부분 일치 | 프로토콜 계약이 코드가 아니라 로그 포맷이고, `[ERROR]` 를 stdout 에 안 쓰는 실패는 성공으로 마감된다 (CAD-D14) |
| 9 위치·순서 결합 | CAD-D6 | 정렬 방어가 이름 매칭 2 · 시각 행 인덱스 2 · 채우기 시점 캡처 1로 갈린다 | `sortItems` 개입 뒤 셋이 같은 행을 가리킨다는 보장이 없다 |
| 11 수명·정리 누락 | CAD-D13 | Set 삭제 시 위젯이 `mModel` 을 정리하지 않고 직후 `deleteLater()` 가 걸린다 | 살아 있는 `QFileSystemWatcher` 가 죽은 모델을 역참조할 수 있다 |
| 11 수명·정리 누락 | CAD-D15 | `loadPrt` 의 temp 정리가 승격이 복사해 둔 `.prt` 보관본과 같은 경로를 지운다 | 승격 후 같은 `.prt` 를 다시 Load 하면 0.5초 뒤 DOE 재현용 보관본이 사라진다 |
| 11 수명·정리 누락 | CAD-D16 | GUI 가 `--no-cleanup` 을 항상 붙이고 일괄 정리는 `.stp` 만 글로빙 | 프리뷰 1회마다 temp `.prt` 가 하나씩 남고 지우는 경로가 없다 |
| 12 순서 의존 | CAD-D4 | `loadFromJson` 복원 직후 캐시 재적용이 전 행을 `isChecked = false` 로 재구성 | `.prt` 를 한 번이라도 로드한 세션에서 저장된 체크가 사라지고 승격이 풀린다 |
| 13 동기 실행·재진입 | CAD-D2 | `.prt` 진입 초입의 `processEvents` 가 큐된 슬롯·타이머를 실행 | 데몬 stdout 처리가 재진입해 모델을 갈아엎을 수 있다 |
| 15 죽은 코드 | CAD-D5 | Set 진입마다 도는 해석 덱 유입 경로의 결과를 읽는 곳이 0 | 매 진입의 레지스트리 로드가 아무 산출도 내지 않고 실패해도 `qWarning` 뿐이다 |
| 15 죽은 코드 | CAD-U3 | 도달하지 않는 선언·정의 — `saveSettings` no-op · `getContext`/`getLoadedFilePath` · `setModel` 오버로드 · `enum class JobType` | 앞의 셋이 CAD-D5 가 말하는 "결과를 읽는 쪽이 없는" 그 지점이고, `JobType` 은 주석이 `commandId` 로 대체됐다고 적어 둠 |
| 16 검증 부재 | CAD-U5 | `tests/` 전체에 `NxCad`·`GeometryParameter` 참조 0건 | CAD 파사드의 분기 · 배치 오케스트레이션 · DV 승격 왕복이 덮여 있지 않다 |
