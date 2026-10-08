# Execution 작업 카드 독립 검토

검토 기준: dev `b08a91b`, `modules/execution.json` 31개 카드, 최신 #643/#411/#441/#444/#615/#454/#494/#502, PR651/652/654 diff. 코드·원격 변경과 실행 테스트는 하지 않았다.

결론: 이미 완료된 구조를 대규모로 재작업하는 오류는 발견하지 않았다. 수정 권고는 medium 3건, low 1건이다. 특히 `co_await`와 실제 GUI 스레드 이탈을 구분해야 한다.

## GXR-01 [medium] AL-12, AST-003

AL-12가 이미 await하는 조건 export 경로를 제외하는 문구는 실제 GUI 실행 잔여를 완료분으로 오해하게 한다. 현재 document-handle 코루틴은 suspend 전에 GUI actor 함수를 동기 호출한다. AST-003이 Deferred이면 AL-12 완료 뒤에도 clone/edit/export의 GUI 정지가 남는다.

근거:
- `controller/DashRwDocumentHandle.cpp:60 주석: GUI actor에서 task가 suspend 전에 이미 완료됨`
- `controller/DashRwDocumentHandle.cpp:141 exportContent, :151 clone`
- `controller/DashRwActor.cpp:96 GUI affinity; controller/DashRwActor.h:137 invokeOnActor`
- `controller/DashDoeBatchChain.cpp:216 exportDoeSample→toMutable/updateMeshPoints/exportSolverInput`

AL-12의 제외 이유를 값 경계가 이미 준비돼 있다는 의미로 한정하고, 실제 RW clone/edit/export 실행 스레드 이관은 AST-003의 명시적 소비 경로·수용기준에 포함한다. AL-12의 UI 응답 완료조건은 파일 준비/fallback 범위로 한정하며 전체 DOE 입력 생성 응답성은 AST-003 완료 후 검증한다고 기록한다. 독립 파일 작업에 AST-003 하드선행을 만들 필요는 없다.

## GXR-02 [medium] RES-12, PRJ-03

RES-12의 PRJ-03 전체 하드선행은 현재 요구보다 넓다. #643이 명시한 선행 #597은 이미 병합됐고 referenceModel.uuid 및 DOE tableId는 dev에 존재한다. 산출물 핀 검증 전체 PR530이 완결되지 않아도 Set 단위 결과 구조를 설계·구현할 수 있다.

근거:
- `sources/issues/643.md 선행: #597(#617 머지) 이후`
- `model/DashDoeConfigManager.cpp:24 stampTableIdentity가 tableId 생성`
- `model/preprocessor/DashAnalysisLauncherConfig.cpp:149 상태에 snapshot tableId 기록`
- `RES-12 scope는 Set 구조·producer/consumer 이행이고 PRJ-03는 PR530 pipeline pin 통합`

필요한 식별 계약을 구체적으로 적고 PRJ-03을 접점/검토 선행으로 바꾸거나, PR530만 제공하는 특정 필드가 정말 필요할 때 그 필드로 의존 범위를 제한한다. 기존 uuid/tableId 사용만이면 RES-12 dependencies에서 PRJ-03 제거를 권고한다.

## GXR-03 [medium] RES-12, RES-13

1차 XML 구현 후 2차 형식 비교라는 순서 자체는 최신 이슈와 맞지만, 1차가 기존 Set 파일에 응답을 추가할 때의 최소 충돌/재생성 정책이 카드에 빠져 있다. append/overwrite 의미를 전부 RES-13로 미루면 RES-12가 이미 존재하는 다른 tableId 결과를 갱신할 때 안전한 완료 조건을 판단하기 어렵다. USD 구조에 따라 중복 제거 설계가 달라진다는 최신 댓글도 1차 설계 검토에 반영할 필요가 있다.

근거:
- `sources/issues/643.md 1차: Set XML 하나에 응답 추가; 2차: uuid/tableId로 이어쓰기/덮어쓰기`
- `sources/issues/643.md 2026-10-02 댓글: USD 역할에 따라 중복 제거 설계가 달라짐`
- `RES-12 scope: 구조 확정+중복 제거+writer/consumer 이행`
- `RES-13 scope: referenceModel.uuid/tableId별 append/overwrite 의미 정의`

전체 HDF5/USD 채택 결정을 RES-12 앞으로 강제 이동하지 않는다. 대신 RES-12 착수 시 1차 정책(예: 전체 재생성·원자 교체, 기존 다른 식별 결과에 병합 금지)과 확장 가능한 논리 구조를 먼저 정한다. 이후 RES-13은 실측 기반 형식 선택과 증분 갱신 정책을 담당하도록 분리한다. 1차에서 이미 증분 append를 구현하려면 해당 최소 식별 충돌 정책은 RES-12로 옮긴다.

## GXR-04 [low] RES-11, RES-02, RES-07, RES-09

RES-11의 최종 처리 경계 검증은 dependency 목록보다 넓다. 현재 목록에는 RES-01/04/05/06만 있어 일반 sub-result(RES-02), 완료 집계(RES-07), worker 수명(RES-09)이 끝나기 전에 후속 worker 경계까지 검증 완료로 읽힐 수 있다.

근거:
- `modules/execution.json RES-11 acceptance: #433 최종 분해 경계·후속 worker 경계 검토`
- `modules/execution.json RES-11 dependencies에는 RES-02/07/09 없음`
- `model/preprocessor/DashReaderSession.h:Work의 현재 재진입 depth/faulted 수명 계약`
- `sources/issues/433.md 최종 경계 검증 잔여`

RES-11을 도메인 파일 검증과 최종 통합 체크로 나누거나, 도메인 검증은 먼저 가능하되 worker/완료 집계 최종 승인은 RES-02/07/09 이후라고 조건을 명시한다. 단위·실파일 검증 자체를 모든 리팩터 완료까지 불필요하게 지연하지 않는다.

## 별도 지적 없이 타당한 항목

- AL-05/AL-06 분할은 #441의 증분 기록→재시작 복구 순서와 일치한다. 복구를 곧바로 solver 재연결 또는 자동 재제출로 단정하지 않고 needs_decision으로 둔 점은 적절하다. 상태 journal·정적 설정·snapshot 분리에는 AL-05가 단일 소유자가 되어야 한다.
- AL-02는 실제 결함 근거가 있다. snapshotDoeTable 실패가 cancelAllRuns를 호출하더라도 runAccepted 시그널 반환 뒤 generateInputCases가 계속 진행하는 경로를 확인했다. Config의 QSaveFile을 다시 도입하지 않고 저장 veto 전달을 고치는 범위가 맞다.
- AL-05와 IO-03의 목적은 분리 가능하다. AL-05는 상태 기록 구조/단일 writer/증분 UI, IO-03은 DOE·Launcher 설정 저장/실패 반환/왕복이다. root가 결과 메타데이터 제목을 유지한다면 case journal은 AL-05 소유라고 명시하는 편이 낫다. 별도 같은 파일 원자화 PR를 각각 만들 필요는 없다.
- AL-09/AST-002는 root 계획대로 PR651 한 통합 카드로 합치면 된다. #648의 원인 추정을 확정 수정으로 만들지 않은 점이 적절하다. AST-001 파일/동반 폴더 교체 실패보존은 PR651에 구현됐다고 오해하면 안 된다.
- DIR-01은 PR652의 0-submit·runSerial·앱 수명 runner를 신규 요구가 아닌 진행 중 구현으로 잡았다. stli/다중 파일 큐 확장은 범위 밖으로 둔 점이 적절하다.
- AL-13은 PR654 legacy 형식 거부에 따라 무구현 종료될 수 있음을 명시해, #557의 낡은 정책 분기를 자동 복구하지 않는다.
- AL-14는 현 Set별 실행 구조에서 #502를 재판단하는 Deferred 결정 작업이어서 승인되지 않은 복수 실행 엔진을 확정하지 않는다.
- RES-08은 결과 Preprocessor reader 경계로 RW deck actor와 다른 표면이다. AST-003을 RES-08의 무조건 선행으로 연결할 근거는 없다. 기존 DashReaderSession 작업별 수명은 worker 이행에서 보존해야 한다.
- RES-01~07은 현재 어댑터/질의/Writer 경로와 이슈의 구체 증상을 반영한다. 응답 없는 시점 fallback·성분 임의 선택·SideForce 실패값 0 혼동·중복 완료 통지를 각각 독립 완료 조건으로 둔 분할은 적절하다.

## 제한

전체 카드의 모든 외부 solver 분기를 실행 재현하지 않았다. result SDK/외부 reader 스레드 안전성과 실제 파일 검증은 RES-08/11의 착수·완료 검증 사항이다. 이번 리뷰는 코드와 명시된 요구의 모순 및 작업 경계·의존성 위주다.
