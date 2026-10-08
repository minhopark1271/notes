# 결함 색인 — RUN

> 출처: 01-sources/wiki/Cross-Module-Defect-Index.md (좌표 cf44c25 기준 정적 판정, 런타임 검증 없음). 설명 전문·좌표는 01-sources/wiki/Code-Map-User-Flow-*.md 의 같은 ID. **현행 코드(dev @ b08a91b3) 재검증 필수.**

| 성격 | ID | 결함 | 귀결 |
|---|---|---|---|
| 1 정본 이중화 | RUN-D2 | `variant` 가 JSON 키와 Set 이름 접미사에 이중 보관 | 두 값이 어긋나면 저장이 매번 이름 쪽으로 덮는다 |
| 1 정본 이중화 | RUN-D10 | 설계변수 값의 정본이 모델이 아니라 셀 위젯 (시그널 결선 없이 폴링) | 모델만 바꾸는 경로(RUN-D26)가 실제로 존재해 화면과 저장이 갈린다 |
| 1 정본 이중화 | RUN-D20 | NodeSet 판정 근거가 `Qt::UserRole` 과 이름 목록 2벌이고 후자는 미호출 | 콤보 텍스트만 세우는 경로에서 UserRole 이 비어 NodeSet 이 Part 로 취급된다 |
| 2 왕복 단절 | RUN-D24 | 두 번째 `updateModelUploadConfig` 가 첫 번째의 `Output Response` 를 덮음 | 실제로 돈 것은 ND 인데 계약 파일은 1D 를 가리킨다 |
| 2 왕복 단절 | RUN-D26 | `updateModelUploadConfig` 가 `model_info.json` 을 재파싱해 사용자 입력값을 기본값으로 덮음 | 외부 실행파일이 읽는 계약 파일이 화면과 다른 값을 담는다 |
| 2 왕복 단절 | RUN-D33 | 설정 JSON 의 `Prediction Cases`·`Output Response`·`Input Design Variables` 가 쓰기 전용 | 재진입 후 [Run AI Prediction] 이면 모든 행이 현재 dvTable 값 한 벌을 공유한다 |
| 2 왕복 단절 | RUN-D34 | `m_predictionCount` 가 세션을 넘기지 못하고 0 에서 재시작 | 재진입 후 Generate 가 기존 `Predict_01_*` 을 같은 이름으로 덮어쓴다 |
| 2 왕복 단절 | RUN-D35 | Morphing 생성은 `.vtu` 경로를 싣고 디스크 스캔은 `*.dat`·`*.inp` 를 집는다 | 재진입 뒤 같은 케이스의 행 경로가 바뀌고 열람이 동명 리다이렉트에 의존한다 |
| 3 조용한 실패 | RUN-D14 | `SetBoxHandles` 가 렌더러 부재 시 데이터 없이 반환, 최종 가드는 "비어 있지 않은가" 뿐 | 직전 Set 의 핸들이 남아 있으면 `true` 를 돌려주고 그 핸들로 모핑이 돈다 |
| 3 조용한 실패 | RUN-D23 | `startPredictionJob` 의 거절 반환값을 호출부 3곳이 검사하지 않는다 | ND 와 1D 를 함께 실행하면 1D 가 모달 경고 없이 누락된다 |
| 3 조용한 실패 | RUN-D29 | 민감도 콤보가 다른 계층의 키를 기대하고 4단 중첩 `if` 에 로그가 없다 | 키가 없으면 플롯 패널의 변수 목록이 조용히 빈다 |
| 3 조용한 실패 | RUN-D30 | 민감도 폴더 열거에 Set 필터가 없다 | 다른 Set 의 학습 결과가 목록에 뜨고, 매치 실패 시 0번이 선택돼 무관한 Set 으로 플롯이 나간다 |
| 5 공유 상태 오염 | RUN-D13 | Generate 가 Geometry Parameterization 의 공용 핸들 인스턴스를 제자리 교체 | Model Runner 의 Generate 1회가 Morphing 탭이 편집 중이던 핸들 배열을 덮는다 |
| 6 통지 미결합 | RUN-D15 | `enqueueUpdatePrtGeometry` 가 요청 식별자를 돌려주지 않고 짝짓기가 멤버 문자열 비교 | 다른 모듈이 배치 모드를 켠 채면 완료 통지가 오지 않고 행도 JSON 도 안 생긴다 |
| 8 암묵 계약 | RUN-D11 | 스핀박스 상한을 `max - 0.0001` 로 깎고 미설정 판정을 `value != 0.0` 으로 한다 | 표시된 상한을 입력할 수 없고, 정확히 `0.0` 인 DV 는 매 진입마다 중앙값으로 대체된다 |
| 8 암묵 계약 | RUN-D12 | Part 콤보가 모핑 대상이 아니라 `_input_geometry.vtu` 추출 대상만 고른다 | 라벨(`Select Set / NodeSet`)과 실제 효과가 어긋난다 |
| 8 암묵 계약 | RUN-D18 | 템플릿 치환이 `QMap` 사전순 전역 텍스트 치환 | 이름이 다른 이름의 접두사면 결과가 순서에 달리고, 값이 유효숫자 6자리로 잘린다 |
| 8 암묵 계약 | RUN-D21 | 행 삭제 범위가 `completeBaseName()` 접두사 매칭 | `Predict_1` 이 `Predict_1x` 를 함께 잡고, RUN-D34 로 카운터가 리셋되면 충돌이 앞당겨진다 |
| 8 암묵 계약 | RUN-D37 | MCU 민감도가 이미 `-MCU` 로 끝나는 이름에 접미사를 다시 붙인다 | 대상 폴더를 찾지 못해 목록 0번이 선택된다 (RUN-D30 과 연쇄) |
| 9 위치·순서 결합 | RUN-D8 | 소스 종류 판정이 `parameter` 딕셔너리 순회 중 첫 매치에서 `break` | 혼합 Set 에서는 키 순서가 소스 종류와 Reference 줄·Part 콤보 활성까지 정한다 |
| 9 위치·순서 결합 | RUN-D22 | `[Preview]` 만 람다 캡처된 `row` 를 쓴다 (`[X]` 는 매번 재계산) | 앞 행이 지워진 뒤 Preview 를 누르면 다른 케이스가 열린다 |
| 9 위치·순서 결합 | RUN-D25 | `m_lastPreviewedVtuPath` 를 루프 끝에서 한 번만 세운다 | 케이스가 여러 건이어도 자동 렌더는 마지막 1건뿐이다 |
| 10 규칙 중복 | RUN-D6 | ND 판정이 응답 이름 부분문자열과 모델 이름 접두사 화이트리스트 2벌 | 한쪽만 ND 로 판정되면 화면의 열과 실제 예측 경로가 어긋난다 |
| 10 규칙 중복 | RUN-D9 | `Source` 열 라벨이 같은 JSON 을 다시 열어 별개로 판정하고 실패 3경로가 한 값 | 판정 실패와 실제 ConditionParameter 가 화면에서 구분되지 않는다 |
| 10 규칙 중복 | RUN-D19 | 정규화 config 파싱 실패의 처리가 경로마다 다르다 | 경고가 Morphing 경로에만 있어 CAD·ConditionParameter 는 부호 보정 실패를 알리지 않는다 |
| 11 수명·정리 누락 | RUN-D4 | 공용 데몬 수명이 Set 전환에만 묶이고 모듈 이탈에는 안 묶인다 | Set 전환 1회 = 공용 데몬 재기동 1회 + 결과 캐시 폐기, 이탈 시엔 데몬이 남는다 |
| 11 수명·정리 누락 | RUN-D16 | `m_pendingCadStpPath` 가 완료 슬롯 진입 직후에만 지워진다 | 생성 실패 시 이전 대기 경로가 남아 흘러간 요청이 되살아날 수 있다 |
| 11 수명·정리 누락 | RUN-D17 | CAD 완료 처리가 파일 표를 통째로 재구축한다 | 요청과 완료 사이에 손으로 넣은 체크와 `m_fileTableDvValues` 전량이 사라진다 |
| 11 수명·정리 누락 | RUN-D31 | 민감도 캐시 키에 모델 내용이 없고 캐시를 비우는 곳이 2곳뿐 | 같은 경로에서 모델이 재학습되면 캐시가 낡은 결과를 낸다 |
| 11 수명·정리 누락 | RUN-D32 | 민감도 실패 4경로가 `m_pendingCommand` 를 지우지 않는다 | 공용 데몬 브로드캐스트 구조에서 다음 응답이 이 러너의 것으로 오인 수신될 수 있다 |
| 11 수명·정리 누락 | RUN-D36 | `clearAllTables` 가 `m_predictionCount`·`m_pendingCadStpPath`·`m_pendingCadParams` 를 남긴다 | 진행 중이던 CAD 요청의 완료가 새 Set 의 표에 이전 Set 의 DV 값으로 행을 만든다 |
| 12 순서 의존 | **RUN-D38** | Set 불일치 시 표를 비우는 방어에 `!currentSetName.isEmpty()` 예외가 붙어 있다 | Set 이름이 아직 비어 있는 최초 진입에서 방어가 돌지 않아 이전 표가 남고 Generate 가 섞인 입력을 만든다 |
| 13 동기 실행·재진입 | RUN-D5 | 모델 적재 전 구간이 GUI 스레드 직렬이고 같은 파일을 계층마다 다시 읽는다 | `QThread` 0곳·`processEvents` 0곳이라 1\~20초 프리즈 구간에 진행 표시조차 없다 |
| 14 고정 지연·폴링 | RUN-D3 | `daemonReady` 유실 보정이 3벌 중복이고 폴링이 실효 경로 | 신호 계약이 아니라 현재 상태 재조회가 실제 동작이다 |
| 14 고정 지연·폴링 | RUN-D27 | 1D 결과 대기가 고정 500ms 뒤 `lastModified` 최대 CSV 선택 | 쓰기가 더 걸리면 이번 결과를 놓치고 다음 예측에서 이전 파일이 최신으로 잡힌다 |
| 15 죽은 코드 | RUN-D7 | `configsDir` 이 양쪽 컨텍스트에 Set 무관 전역 경로로 들어가 삼항 폴백이 무의미 | 나머지 4곳의 삼항과 형태만 같고 효과가 없다 |
| 15 죽은 코드 | RUN-U1 | `syncFileTableToJson` 이 주석뿐인 빈 본문인데 3곳에서 호출된다 | 체크 상태가 메모리에만 있고 재진입에서 소실된다 (RUN-D33) |
| 15 죽은 코드 | RUN-U2 | 체크 행 일괄 삭제 39줄이 구현돼 있으나 `connect` 0건이고 버튼도 없다 | 행 삭제는 행별 `[X]` 하나뿐이다 |
| 15 죽은 코드 | RUN-U3 | `params.fileTableFiles` 와 그 유일한 소비 함수가 도달 불가 | 두 목록의 필터가 다른데 그 불일치를 소비할 함수의 호출처가 0곳이다 |
| 15 죽은 코드 | RUN-U4 | 구버전 CLI 형태(출력 디렉터리 인자 없음)의 예측 슬롯이 남아 있다 | 호출처 0곳이고 현행 두 경로와 인자 개수가 다르다 |
| 15 죽은 코드 | RUN-U5 | 도메인 신호 4종의 수신처가 0곳 | 모델→뷰 갱신이 신호가 아니라 `dataLoaded` 재사용 + 플래그로 좁혀진다 |
| 15 죽은 코드 | RUN-U6 | 도달하지 않는 정의 18종 | `runFESolver` 는 런처 DLL 을 직접 열고 모델 계층에서 `QMessageBox` 를 4회 띄운다 |
| 17 구조 잔여 | RUN-D28 | 뷰가 `DashMainWindow` 를 부모 거슬러 4벌로 찾는다 | 같은 파일의 `findChild` 5회 · 뷰에서 직접 띄우는 `QMessageBox` 15회와 함께 반복된다 |
