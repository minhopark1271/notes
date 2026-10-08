# 결함 색인 — ANA

> 출처: 01-sources/wiki/Cross-Module-Defect-Index.md (좌표 cf44c25 기준 정적 판정, 런타임 검증 없음). 설명 전문·좌표는 01-sources/wiki/Code-Map-User-Flow-*.md 의 같은 ID. **현행 코드(dev @ b08a91b3) 재검증 필수.**

| 성격 | ID | 결함 | 귀결 |
|---|---|---|---|
| 1 정본 이중화 | ANA-D6 | 색 값의 정본이 스타일시트 문자열이고 읽는 방식이 문자열 절단·정규식 2가지 | 정규식 쪽은 색 이름 표기를 매치하지 못해 같은 버튼을 두 경로가 다르게 읽는다 |
| 2 왕복 단절 | ANA-D9 | 설정 JSON 의 `DOE Analysis`·`Data Analysis` 블록이 write-only | 매 Plot 이 축·색·스타일을 파일에 쓰지만 재기동 후 화면에 돌아오지 않는다 |
| 3 조용한 실패 | ANA-D3 | `applyReduction` 분기가 Max/Min/Mean 3종이고 나머지는 `reduceMax` 폴백 | `(std)` 를 고르면 표준편차가 아니라 최댓값이 그려진다 |
| 3 조용한 실패 | ANA-D10 | spec 조립 실패·command 미매치·조기 반환이 UI 에 아무 변화를 주지 않음 | [Plot] 을 눌러도 아무 일이 없는 상태가 세 계층에서 만들어진다 |
| 3 조용한 실패 | **ANA-D14** | 타깃 콤보 스캔이 Set 필터 없이 전량을 나열하고 항상 0번을 자동 선택 | 다른 Set 의 산출물이 콤보에 섞이고, 진입 직후 뜨는 것은 현재 Set 이 아니라 이름순 첫 Set 이다 (RUN-D30 이 그 ModelRunner 사례) |
| 4 피드백 부재 | ANA-D12 | Save 메뉴 3종이 위젯 종류와 무관하게 뜨고 `dynamic_cast` 실패 시 무반응 | `DashExportable` 미구현 11종에서 메뉴가 아무 일도 하지 않는다 |
| 5 공유 상태 오염 | ANA-D2 | 중복 억제 캐시가 함수-로컬 `static` 이고 키에 인스턴스가 없다 | 같은 ViewType 을 공유하는 ModelRunner Sim·MCU 두 인스턴스가 100ms 창을 공유한다 |
| 8 암묵 계약 | ANA-D5 | 타깃 3콤보 등 5종이 `objectName` + `findChild` 문자열 계약 (25회) | 컴파일러가 검증하지 않는 이름이 ViewType 4갈래의 분기 조건을 겸한다 |
| 8 암묵 계약 | ANA-D11 | 랭킹 표를 반환 타입 밖의 숨은 자식으로 실어 보내고 `objectName` 으로 꺼낸다 | 결합 결과 표가 `outer` 의 형제가 되어 PNG 저장 대상에서 빠진다 |
| 9 위치·순서 결합 | ANA-D1 | `m_methodWidgets` 가 `QMap` 이라 Method 콤보가 키 알파벳 순 | 배열 순서를 계약으로 적어 둔 주석과 실제 표시가 불일치한다 |
| 10 규칙 중복 | ANA-D8 | `methodKey` 매핑 5줄이 세 파일에 각각 존재 | command 를 추가하면 세 곳을 함께 고쳐야 한다 |
| 10 규칙 중복 | **ANA-D15** | `m_setName` 이 비면 `"Set1"` 로 대체하는 폴백 삼항이 7회 복제 | 호스트가 Set 을 주입하기 전 어느 경로든 밟히면 무관한 `Set1` 의 산출물을 경고 없이 읽는다 |
| 13 동기 실행·재진입 | ANA-D4 | XML 변수 스캔이 매번 문서 전체를 GUI 스레드에서 파싱하고 폴백 경로는 결과가 다르다 | 같은 파일이라도 파서 성공 여부에 따라 리덕션 항목이 나타나거나 사라진다 |
| 13 동기 실행·재진입 | ANA-D13 | 스핀박스가 스타일 setter 와 디바운스 재플롯 양쪽에 연결돼 있다 | 값 하나를 바꾸면 스타일 반영 후 200ms 뒤 전체 재플롯(파일 재파싱 또는 데몬 왕복)이 한 번 더 돈다 |
| 15 죽은 코드 | ANA-D7 | 타입 핸들 `textStyleGroup` 에 9곳이 대입하고 읽는 코드는 0건 | 위젯은 `findChild` 13회 + 도달 불가한 폴백 캐스케이드를 쓴다 (Method 분기마다 복제) |
| 15 죽은 코드 | ANA-U1 | `onTargetDataChanged` 의 모듈 판별 4갈래가 도달 불가 | 타깃 콤보를 채우는 코드가 `AnalysisLauncher_*.json` 만 나열한다 |
| 15 죽은 코드 | ANA-U2 | `settings.parallel.save_json_path` 를 읽는 코드가 레포 전체 0건 | 기록만 되고 소비되지 않는다 |
| 15 죽은 코드 | ANA-U3 | `DashDoeConfigManager::updateConfigFile` 55줄의 호출처가 0건 | `methodKey` 매핑을 담은 세 번째 사본이다 |
| 15 죽은 코드 | ANA-U5 | 호출부 없는 진입점 4개 (약 106·110·111·16줄) | 앞 3개는 헤더 선언까지 있고 `ViewSpec` 어디에도 등록돼 있지 않다 |
