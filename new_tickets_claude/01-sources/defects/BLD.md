# 결함 색인 — BLD

> 출처: 01-sources/wiki/Cross-Module-Defect-Index.md (좌표 cf44c25 기준 정적 판정, 런타임 검증 없음). 설명 전문·좌표는 01-sources/wiki/Code-Map-User-Flow-*.md 의 같은 ID. **현행 코드(dev @ b08a91b3) 재검증 필수.**

| 성격 | ID | 결함 | 귀결 |
|---|---|---|---|
| 1 정본 이중화 | BLD-D1 | Set 갈림 근거가 `UserRole+2` · JSON `variant` · 이름 접미사 3벌 | 읽는 5곳이 각각 다른 기준을 봐, 어긋나면 같은 Set 이 경로마다 다른 종류가 된다 |
| 2 왕복 단절 | BLD-D4 | 라벨 키의 쓰기는 sanitize, 읽기는 원문 | 공백·`/`·`:` 가 든 라벨은 저장된 배치·체크·reduction 을 잃고 기본 규칙으로 떨어진다 |
| 2 왕복 단절 | BLD-D7 | 저장된 Response 는 sanitize 된 이름, 콤보 표시는 원문 기반 | `findText` 가 -1 을 돌려 Response 가 항상 0번 항목으로 남는다 |
| 2 왕복 단절 | BLD-D8 | Output `transformation` 은 쓰기만 되고 읽기에서 값이 버려진다 | 재진입 시 콤보가 항상 `None` 으로 되돌아간다 |
| 2 왕복 단절 | BLD-D12 | MCU 는 `Data Label.Dataset` 을 배열로 쓰는데 베이스 로더는 `toString()` | Input/Output 체크 소실 · XML 이식 누락 · 파일 표가 빈 표로 복귀 3연쇄 |
| 3 조용한 실패 | BLD-D14 | MCU 의 `stopTraining` 이 `virtual` 이 아니라 베이스 no-op 이 불린다 | [Stop] 이 데몬을 멈추지 못하고 아무 일도 하지 않는다 |
| 8 암묵 계약 | BLD-D2 | [Load] 의 위젯↔모델 계약이 `"dir\|file"` 구분자 문자열 | 경로에 구분자가 들어가면 조립이 깨진다 |
| 8 암묵 계약 | BLD-D3 | 차원 판정의 정본이 파싱 결과가 아니라 shape 문자열의 쉼표 개수 | 자동 분배·모델 목록·머리글 교체·특수 행 활성화가 모두 이 셈 하나에 걸린다 |
| 9 위치·순서 결합 | BLD-D5 | 설정값 왕복이 카탈로그 리스트 i번째와 `QFormLayout` i번째 `FieldRole` 의 짝 | 항목 순서를 바꾸거나 중간 삽입하면 값이 다른 키로 오간다 |
| 9 위치·순서 결합 | BLD-D10 | MCU 파일 행의 [...] 람다가 생성 시점 `row` 를 값 캡처 | 중간 행 삭제 후 [...] 가 어긋난 행에 경로를 쓴다 |
| 10 규칙 중복 | BLD-D9 | Sim / MCU 쌍둥이 경로의 계약이 6곳에서 어긋난다 | status 문자열·저장 위치·산출 루트·`Dataset` 형·쓰는 계층·탭 활성 조건이 전부 다르다 |
| 11 수명·정리 누락 | BLD-D6 | [Delete] 가 `model_info.json` 과 디스크만 지우고 설정 JSON 항목을 남긴다 | 지운 모델이 `status:"Done"` 인 채 다음 [Start] 에서 되살아나 외부 도구에 넘어간다 |
| 11 수명·정리 누락 | BLD-D15 | MCU 위젯이 버튼 잠금을 되돌리지 않고 성공·실패 시그널도 연결하지 않는다 | 학습이 정상 종료해도 Start 버튼이 잠긴 채 남는다 |
| 12 순서 의존 | BLD-D11 | 헤더 검증의 기준 파일 출처가 넷이고 전부 조작 순서에 종속 | 같은 파일 집합이라도 지정 순서에 따라 통과·실패가 갈린다 |
| 14 고정 지연·폴링 | BLD-D13 | MCU 가 쓰지 않는 1Hz 상태 폴링 타이머를 켠 채 두고 멈추는 경로도 안 탄다 | 슬롯이 매번 즉시 반환하는 타이머가 계속 돈다 |
| 15 죽은 코드 | BLD-U1 | 죽은 코드가 세 층에 남아 있다 (헬퍼 8개 중 실사용 4개 · `m_datasetFiles` 스캔 38줄 등) | `m_datasetFiles` 를 채우는 스캔은 Set 선택마다 실행된다 |
| 15 죽은 코드 | BLD-U3 | `parseDataLabelSection`·`parseConfigurationSection` 의 호출처가 0 | 깨진 왕복 3종(BLD-D4·D8·D12)의 읽기 측 구현이 존재한 채 연결만 빠져 있다 |
