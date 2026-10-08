# PER 작업 목록

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> dev @ b08a91b3. 원천·판정은 02-claims/PER.md. PER 은 횡단 모듈이라 "공통 기반 1건" 만 항목으로 두고, 소비자별 이행(직쓰기 22지점 · 왕복 단절 28건 · 생산 출처 기록·소비 판독)은 `범위밖 → 해당 모듈` 로 넘긴다 (PER-c05 · c22~c30 · c13).
> 열린 PR 6건(#651 #652 #654 #655 #656 #658 — decisions ⑩) 중 PER 항목과 파일이 겹치는 것: #651(`DashAnalysisLauncherConfig.cpp`) · #652(`DashDoeSampler.cpp`) · #654·#655(`docs/test-levels.md`) · 넷 다 `tests/CMakeLists.txt`. #656·#658 은 PER 파일을 만지지 않는다. 겹침은 전부 **충돌**이고 **선행**이어야 하는 PER 항목은 없다 — 네 PR 중 어느 것도 PER 항목이 고치는 함수를 바꾸지 않는다(테스트 등록·문서 표만). #530 은 머지하지 않는다(C-2 ②) — PER-07 이 그 공통부를 재업로드한다.
> 권장 순서: PER-01 · PER-03 · PER-06 · PER-10 (결정 4건, 서로 독립 — PER-10 은 헬퍼 계약에 얹히므로 PER-02 앞) → PER-02 → PER-04 · PER-05 · PER-07 → 모듈별 이행.
> Phase B1: #368 주 모듈 LCH→PER 확정(00-progress 메모) — 본체는 PER-06·PER-07, 홉별 5건은 접점. 범위밖 이관 흡수(PER-c31~c33): MOR-c46 → PER-10(신규) · PRE-c60 → PER-03(기흡수) · EXE-c41 DOE-D22 몫 → PER-02.
> C' 반영(2026-10-06, 04-review/PER.md 14건 + decisions ②③④⑤): PER-02 를 `DashSaveSystem` 헬퍼 승격으로 재정의(③) · PER-06 ① 을 확정 전제로 내리고 결정 범위 축소(⑤) · PER-07 을 "공통부만 + 재업로드" 로 못박음(②) · `PER-11` 신설(#471 CLOSE). 항목 10 → 11.

### PER-01 · 도메인 이행 대상 코덱 층을 하나로 정한다 — `utils/DashGadgetCodec` vs `persistence/DashSaveSystem`
- 종류: DEC | 규모: S | 태그: A, E
- 목표: 소비자 0 인 코덱 층이 둘이다 — #478 이 가리키는 `DashGadgetCodec`(Q_GADGET ↔ QJsonObject, 부분 로드 허용) 과 #584 가 들여온 `DashSaveSystem`(registered object 트리, 버전 키·QSaveFile·`Result` 내장). 모듈 Set JSON(설정 구조체 7종 + DOE Table + model_info + ModelRunner config)의 이행 대상 층과 미채택 층의 처분(삭제 / 용도 한정 유지)을 정하고, 이행 절차(구조체 선언 규칙 · 키 이름 = 현행 JSON 키 · 1호 소비자)를 기록한다.
- 완료 기준:
  1. 결정 기록 — 채택 층 · 미채택 층 처분 · 선택 근거 4가지: (a) 부분 로드 vs 실패 (b) 컨테이너 등록 (c) QUuid·Q_FLAG 취급 — (a)~(c) 는 docs/persistence.md "DashGadgetCodec 과의 차이" 표 기준 (d) **저장 단위** — 모듈 Set JSON 은 파일 1개를 여러 라이터가 섹션 단위 RMW 로 공유하는데(`AnalysisLauncher_{Set}.json`: `DashAnalysisLauncherConfig::write*` + PM `saveOutputResponse` · `GeometryParameter_{Set}.json`: `saveMorphingTarget` + PM `saveMorphingSettings` + Widget `setupMorphingTab` + `DashSetIdentity` write-back · c08 RMW 13곳) 두 코덱 모두 "객체 1 ↔ JSON 객체 1" 이다 → 섹션 변환과 다중 라이터 병합을 코덱 밖 헬퍼(`updateObject`, PER-02 비고)가 맡는지
  2. 이행 절차 1쪽 + 1호 소비자 지정(권장: 키가 적고 테스트가 있는 `DashSetReferenceModel` 또는 `DashParameterization` — 각각 PRJ·DOE 항목으로 발행)
  3. docs/persistence.md 또는 utils/DashGadgetCodec.h 머리말에 결정 반영 (문서 변경만)
- 변경 범위: docs/persistence.md (결정 기록) — 코드 변경 없음
- 선행: -
- 충돌: B2 교집합: persistence.md → PER-03 PER-10
- 흡수: #478 · PER-c01, c02
- 비고: **파일 계층(`DashSaveSystem::read/writeJsonFile`)은 이 선택의 대상이 아니다** — C-2 ③ 으로 공용 진입점으로 확정됐고(PER-02), 미채택이 persistence 여도 PER-08 은 그 2함수를 남긴다. 판단 재료 — `DashSaveSystem` 은 registered object(QObject) 전제라 현행 모듈 모델(대부분 QObject 이나 `DashRegisteredObject` 아님)에 바로 붙지 않고, `DashGadgetCodec` 은 구조체만 다뤄 기존 `loadFromJson/saveSettings` 함수의 본문을 교체하는 식으로 점진 이행이 된다. "둘 다 유지(MVVM Model 은 SaveSystem, 평면 설정 구조체는 GadgetCodec)" 도 선택지 — 그 경우 PER-08 은 CLOSE.

### PER-02 · `DashSaveSystem` 의 JSON 파일 헬퍼를 공용 진입점으로 승격하고 파일 지역 사본 4벌을 치환한다 — 원자 쓰기 · 읽기 규칙 · 사유 반환
- 종류: PR | 규모: M | 태그: A, E · refactor
- 목표: 신설하지 않는다 — `persistence/DashSaveSystem::readJsonFile`/`writeJsonFile`(static · 임의 QVariantMap · `QSaveFile` · `Result` 오류 · `TestMvvmBase` 왕복 테스트 보유)이 이미 공용 파일 계층이고, 새 `utils/DashJsonFile` 은 9번째 구현이 된다(C-2 ③). 이 2함수를 **공용 진입점으로 승격**하고 모자란 3가지를 보강한다 — ① 읽기 규칙: "파일 없음·0바이트·공백 = 빈 객체(ok)", "손상(파싱 실패·배열·스칼라 루트) = 실패 + 사유, 원본 보존" (현행은 open 실패·빈 파일·손상을 모두 실패로 뭉갠다) ② `write` 반환 길이 검사 ③ `QJsonObject` 받고 돌려주는 오버로드 — 소비자 8벌이 전부 `QJsonObject` 를 쓴다. 치환은 c03 의 사본 7벌 중 4벌 — `model/DashSetIdentity.cpp`·`model/DashSetLegacyMigration.cpp` 의 anonymous `readJsonObject`/`writeJsonObject`, `model/DashDoeSelection.cpp:readJsonObject`(동작 불변 — 실패를 빈 객체로 받는다), `model/preprocessor/DashDoeTableFile.cpp:read`(`ReadResult.error` 를 헬퍼 사유로 채운다 — 호출 4곳의 시그니처 불변). 나머지 3벌은 같은 진입점으로 다른 항목이 이행 — `DashAnalysisLauncherConfig::readRoot/writeRoot` 는 #638 과 같은 자리라 PRE-14·15, `DashDoeSampler::loadJsonRoot`·`DashDoeConfigManager::loadSettings` 는 DOE-17.
- 완료 기준:
  1. `readJsonObject`/`writeJsonObject` 가 `model/` 에 0건 · 네 파일에 `QJsonDocument::fromJson`·`QSaveFile` 직접 호출 0 — 전부 진입점 경유
  2. `tests/TestJsonFile.cpp`(또는 `TestMvvmBase` 보강): 0바이트·공백 → ok+빈 객체 / 잘림·배열·스칼라 → 실패+사유 / 쓰기 실패(읽기 전용 경로) 시 기존 파일 바이트 동일 / 정상 쓰기 후 재읽기 동일 — ctest 통과
  3. 기존 `test_set_identity`·`test_set_legacy_migration`·`test_doe_selection`·`TestDoeTableFile`·`TestMvvmBase` 통과
  4. 소비자 9건이 이 진입점을 선행으로 둔다 (전건 등재 확인) — DOE-17 · CON-11 · MOR-22 · CAD-13 · OPT-24 · RUN-32 · BLD-17 · PRJ-31 · PRE-27(조건부). 각 항목의 "`DashJsonFile`" 문구는 "`DashSaveSystem` 헬퍼(공용 진입점)" 로 바뀐다 — PRJ-31 · RUN-32 · OPT-24 는 미치환(**보류: PRJ · RUN · OPT 몫**)
- 변경 범위: persistence/DashSaveSystem.h · persistence/DashSaveSystem.cpp · model/DashSetIdentity.cpp · model/DashSetLegacyMigration.cpp · model/DashDoeSelection.cpp · model/preprocessor/DashDoeTableFile.cpp · tests/TestJsonFile.cpp (신규) · tests/CMakeLists.txt
- 선행: -
- 충돌: PER-07 (model/DashDoeSelection.cpp — 순차) · PRE-14 · PRE-15 (같은 `readRoot` — **PRE-14 가 먼저**(#638 bug), PER-02 가 뒤에서 진입점으로 치환) · DOE-16 · DOE-17 (DOE 쪽 2벌을 같은 진입점으로 이행) · PER-04 · PER-08 (같은 `DashSaveSystem` 파일) · B2 교집합: tests/CMakeLists.txt → 공유 12건(deps.md 5절) · DashDoeSelection.cpp → DOE-12 · DashDoeTableFile.cpp → DOE-02 PRJ-33 · PR #655(tests/CMakeLists.txt) · PR #654(tests/CMakeLists.txt) · PR #652(tests/CMakeLists.txt) · PR #651(tests/CMakeLists.txt)
- 흡수: #478 · #479 · #638(공통 규칙) · DOE-D22(원자 쓰기 몫, EXE-c41 이관) · PER-c03, c06, c07, c08, c09, c19(규칙 부분), c33
- 비고: 코덱 층 선택(PER-01)과 **분리 유지** — 두 코덱 모두 파일 I/O 를 호출 측에 둔다(`DashGadgetCodec.h` 4항). 승격 대상은 코덱이 아니라 그 아래 파일 계층이므로 PER-01 이 persistence 를 미채택해도 이 2함수는 남는다(PER-08 완료 기준 3). 위치는 `persistence/DashSaveSystem` 그대로 두고 함수만 승격한다 — 파일을 옮기면 9모듈 이행 항목의 변경 범위가 전부 흔들린다. 직쓰기 22지점(c22~c30)은 이 진입점으로 이행하면서 원자성·사유 반환·(PER-04 후) 버전 키를 한 번에 얻는다 — 모듈별 항목. RMW 를 돕는 `updateObject(path, fn)` 를 둘지는 소비자 13곳(c08) 이행 시 결정 — PER-01 완료 기준 1(d) 의 입력.

### PER-03 · 저장 포맷 버전 키 규약을 정한다 — 키 이름 · 자리 · 판정 · 키 부재 규약과의 관계
- 종류: DEC | 규모: S | 태그: A, C
- 목표: 현행은 "키 부재 = 구버전"(D14 · `referenceModel`·`setId`·`tableId`)이고 버전 키는 `referenceModels.json` 의 `schemaVersion` 1종뿐이다. 다음을 정한다 — ① 키 이름(`schemaVersion` 재사용 권장)과 자리(루트) ② 값 의미(파일 종류별 정수, 앱 버전 아님) ③ 로드 판정(상위 버전 → 거절·읽기 전용 + 안내, 하위·부재 → 현행 키 부재 규약으로 해석 — 마이그레이션 프레임워크 불도입) ④ 구 파일 write-back 시점(SI-3 선례 "열기 시 1회" vs "다음 저장 시") ⑤ 대상 파일(모듈 Set JSON 7종 · DOE Table · AnalysisLauncher config · model_info.json · ModelRunner config · referenceModels.json) ⑥ `variant`(타입 판별) 와의 역할 분리 ⑦ 결과 XML(PRE-28·29)이 같은 규약을 쓰는지 — #444 분할 파일은 LCH-32 비용 검증 결과 실제 분리가 필요할 때만 포함한다.
- 완료 기준:
  1. 결정 기록 7항 + 대상 파일별 초기 버전값 표 + **D14 개정 기록**(정본 문서 `Project-Manifest-0-Work-Order.md` 결정표 — "스키마 버전은 올리지 않고 키 부재를 구버전 판정으로" 가 #480 과 정반대이므로, 이 항목은 곧 D14 개정이거나 D14 유지 + #480 기각이다)
  2. 이 기록을 선행으로 참조하는 항목 — PRJ-32(⑥ `variant` 와의 역할 분리, 등재 확인) · 결과 XML 의 키 작성 PRE-28·29(미등재 — **보류: PRE 몫**) · RUN-10은 실제 파일 충돌 검사로 결과를 보존하며 새 채번 키를 요구하지 않음(c16)
- 변경 범위: 결정 기록 (03-items 비고 또는 docs/persistence.md) — 코드 변경 없음
- 선행: -
- 충돌: B2 교집합: persistence.md → PER-01 PER-10
- 흡수: #480 · #411 결정 3 (PRE-c60 이관) · PER-c10, c11, c32
- 비고: 되돌리기 비용이 큰 결정(저장 포맷)이라 PR 보다 먼저. 선례 2건이 이미 ③ 의 형태다 — `DashReferenceModelLedger::load`(상위 `schemaVersion` → 적재 안 함 + 쓰기 불가) · `utils/log/DashLogFormat.h:kFormatVersion`(=2, "없는 파일 = Legacy v1" — 키 부재 규약과 버전 키의 공존 선례).

### PER-04 · 헬퍼가 버전 키를 자동 기록·판정하게 하고 ledger 의 손코딩 버전 처리를 통일한다
- 종류: PR | 규모: M | 태그: A, C · feature
- 목표: PER-02 가 승격한 진입점(`DashSaveSystem::writeJsonFile`)이 PER-03 의 키를 자동 기록하고 `readJsonFile` 이 상위 버전을 실패(사유 "newer format") 로 돌려준다 — 파일 종류별 버전값은 호출자가 넘긴다. `DashReferenceModelLedger::load/save` 의 `kSchemaVersion` 처리를 헬퍼 경유로 바꾼다 (동작 동일). 모듈 Set JSON 은 소비자가 PER-02 헬퍼로 이행하는 순간 키를 얻는다 — 모듈별 항목.
- 완료 기준:
  1. `tests/TestJsonFile.cpp`: 쓰기 후 파일에 키 존재 / 상위 버전 파일 읽기 → ok=false + 사유 / 키 부재 파일 → ok (현행 규약 유지)
  2. `test_reference_model_ledger` 통과 · `schemaVersion` 리터럴이 `model/DashReferenceModelLedger.cpp` 에 0건(진입점이 소유)
  3. 소비자 미이행 파일의 로드 동작 불변 (키 없는 구 프로젝트 열기 — 수동 1회)
- 변경 범위: persistence/DashSaveSystem.h · persistence/DashSaveSystem.cpp · model/DashReferenceModelLedger.cpp · tests/TestJsonFile.cpp · tests/TestReferenceModelLedger.cpp
- 선행: PER-02 · PER-03
- 충돌: PER-02 · PER-08 (같은 `DashSaveSystem` 파일 — 순차) · PRJ 의 ledger 항목(미작성) · B2 교집합: TestReferenceModelLedger.cpp → PER-05
- 흡수: #480 · PER-c10, c11
- 비고: write-back 시점이 "열기 시 1회"(PER-03 ④)로 정해지면 `DashSetIdentity::ensureAll` 과 같은 자리에 키 부여를 얹는 PRJ 항목이 하나 더 생긴다 — 그 전까지는 "다음 저장 시" 가 자연 경로.

### PER-05 · "저장→로드→재저장 동일성" 테스트 게이트를 공용 픽스처로 세운다
- 종류: PR | 규모: S | 태그: A, F · refactor
- 목표: `tests/JsonRoundTrip.h` 에 "파일 → 로드 → 저장 → 파일" 두 JSON 의 정규화 비교(키 정렬 · 들여쓰기 무시 · 허용 차이 목록) 헬퍼와 픽스처 디렉터리 규칙(`tests/fixtures/<Module>_<case>.json`)을 두고, 첫 적용으로 `TestReferenceModelLedger` 에 referenceModels.json 왕복 케이스 1건을 넣는다. docs/test-levels.md 에 "모듈 JSON 의 저장 경로를 고치는 PR 은 왕복 케이스를 추가한다" 규칙 1줄.
- 완료 기준:
  1. 헬퍼 TU 없이 헤더만으로 기존 TU 에서 쓸 수 있다 (ledger 왕복 케이스 ctest 통과)
  2. docs/test-levels.md 규칙 1줄
- 변경 범위: tests/JsonRoundTrip.h (신규) · tests/TestReferenceModelLedger.cpp · docs/test-levels.md
- 선행: -
- 충돌: CAD-11 · DEV 의 tests 인프라 항목 (tests/CMakeLists.txt 를 건드리게 되면) · B2 교집합: TestReferenceModelLedger.cpp → PER-04 · test-levels.md → DEV-13 · PR #655(test-levels.md) · PR #654(test-levels.md)
- 흡수: #478(게이트) · PER-c04, c05
- 비고: **게이트는 선행이 아니다** — 왕복 단절 28건의 모듈 항목은 "왕복 케이스 1건(PER-05 헬퍼)" 을 자기 `완료 기준` 에만 쓰고 `선행: PER-05` 는 두지 않는다. 게이트를 선행으로 걸면 bug fix 가 인프라 PR 을 기다린다(검토 #9). DOE-17 은 제거 완료 · CON-11 은 미제거(**보류: CON 몫**). JSON 수준 비교라 코덱 선택(PER-01)과 무관. 현행 왕복 깨짐 중 "저장된 값이 로드 후 다른 키로 가는" 류(BLD-D4·D7)는 정규화 비교로 잡히고, "쓰기만 되고 읽기에서 버려지는" 류(BLD-D8·RUN-D33·ANA-D9)는 두 번째 저장이 키를 잃어 잡힌다 — 28건 중 쓰기 경로 자체가 없는 3건(MOR-D10·MOR-D11·CAD-D17)은 게이트 밖(모듈 feature).

### PER-06 · Set 참조와 산출물 출처의 공통 계약을 정리한다
- 종류: DEC | 규모: S | 태그: C, A
- 목표: #520의 기존 Set JSON `setId` 발급·영속·역조회를 사용한다. Set 설정은 현재 상류 입력 참조를, 산출물은 생성 Set·실제 입력 Set·세부 선택·deck 출처를 소유한다. 현재 Set ID를 유지하면서 다른 상류 setId로 참조를 변경할 수 있다. 입력 선택만 바꾸어 기존 산출물 출처를 고치지 않으며, 재실행 결과를 덮어쓸 때 실제 출처를 함께 갱신한다.
- 완료 기준: ① 공통 기록·판독 계약과 필수 출처/검증 실패 사유를 정의 ② #368은 DOE-16 → PRE-32 → BLD-20의 model_info.json 생성까지, #685는 RUN-34·OPT-26 소비부터 담당 ③ parameterizationId·derivedId·최초 입력 영구 핀 폐기 ④ 구산출물 출처 누락은 재생성 안내, 이름·경로 추론/자동 이관 금지, 기존 Set ID 복원 유지 ⑤ #650 버전·최신성과 #473 결과 키를 구분. 전체 산출물 이력 보존과 별도 Set·산출물·소비 대장은 요구하지 않음.
- 변경 범위: 결정 기록 — 코드 변경 없음
- 선행: -
- 충돌: -
- 흡수: #368 공통 계약 · #443 입력 참조 · PER-c13, c15 · PER-c14(대장 취소 근거)
- 비고: #470은 출처 추적 상위 목표로 유지(PER-09), #471 취소는 PER-11. tableId는 기존 실행 스냅샷 식별에 유지하되 조합 ID나 #650 버전을 대신하지 않는다. 구 PR #530의 산식·핀 구현을 그대로 이식하지 않는다.

### PER-07 · 개별 Set 참조와 출처 기록·판독 공통부를 구현한다
- 종류: PR | 규모: M | 태그: C · feature
- 목표: #368의 공통 기록·판독 타입, 필수 필드 검증, 재생성 안내를 구현한다. #520의 setId 해석을 재사용하고 producer Set·실제 입력 Set·세부 선택·deck 정보를 명시적으로 다룬다. 조합 문자열 생성·해석·비교 함수와 최초 입력 고정 API는 도입하지 않는다.
- 완료 기준: 공통 테스트에서 개별 setId·선택·deck 왕복, 필수 출처 누락 거절, 개명 뒤 동일 ID 해석, 동명 재생성의 다른 ID 구분을 검증한다. 다른 유효한 상류 Set으로 참조를 바꿀 수 있고 기존 산출물 출처는 보존된다. 생산·소비 모듈은 이 계약을 공유하며 소비측에서 스키마를 중복 정의하지 않는다.
- 변경 범위: model/DashPipelineStamp.h (공통 출처 타입·판독 계약) · model/DashDoeSelection.h · model/DashDoeSelection.cpp · tests/test_doe_selection.cpp
- 선행: PER-06
- 충돌: PER-02 (model/DashDoeSelection.cpp — 순차) · DOE-16 (`DashDoeSelection` · test_doe_selection — PER-07 먼저) · B2 교집합: DashDoeSelection.cpp → DOE-12 · test_doe_selection.cpp → DOE-10 DOE-12 · DashDoeSelection.h → DOE-12
- 흡수: #368 공통부 · #443 기존 setId 활용 · PER-c13
- 비고: PR #530 재업로드 노선은 당시 브랜치 처리 기록으로 보존한다. 새 구현은 현행 계약으로 다시 작성하며 기존 hunk의 산식·핀·fallback을 복원하지 않는다. PER-07 → DOE-16 → PRE-32 → BLD-20이 생산 경로이며 #368 완료 후 RUN-34·OPT-26이 #685를 구현한다.

### PER-08 · 미채택 코덱 층과 그 테스트를 제거한다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: PER-01 이 한 층만 남기기로 하면 다른 층(`utils/DashGadgetCodec.{h,cpp}` + `tests/TestGadgetCodec.cpp`, 또는 `persistence/*` 4쌍 + `model/DashMvvmModelBase` + `viewmodel/DashMvvmViewModelBase` + `tests/TestMvvmBase.cpp` + docs 2편)을 지운다.
- 완료 기준:
  1. 닫기 사유 또는 삭제 — 제거 층의 심볼 0건 · tests/CMakeLists.txt 의 해당 `add_test` 제거 · ctest 전체 통과
  2. docs/persistence.md · docs/mvvm-pattern.md 의 참조 정리
  3. persistence 를 지우는 경우에도 **파일 계층은 남긴다** — `read/writeJsonFile` 2함수 + 그 테스트를 `persistence/DashJsonFile.{h,cpp}` 로 옮기고 PER-02 소비자 9건의 include 를 따라 고친다 (C-2 ③: 이 2함수가 공용 진입점)
- 변경 범위: PER-01 결과에 따라 위 두 집합 중 하나 + tests/CMakeLists.txt + docs (persistence 쪽을 지우면 persistence/DashJsonFile.h · persistence/DashJsonFile.cpp 신규)
- 선행: PER-01 · PER-02 (파일 계층 승격이 먼저 — 삭제 집합의 경계가 그때 확정된다)
- 충돌: PER-02 · PER-04 (같은 `DashSaveSystem` 파일) · B2 교집합: tests/CMakeLists.txt → 공유 12건(deps.md 5절) · PR #655(tests/CMakeLists.txt) · PR #654(tests/CMakeLists.txt) · PR #652(tests/CMakeLists.txt) · PR #651(tests/CMakeLists.txt)
- 흡수: PER-c01, c02 (처분 부분)
- 비고: PER-01 이 "둘 다 유지" 면 CLOSE. 삭제 전 `utils/log/DashLogModule.h` 의 모듈 주석(`App` 에 DashGadgetCodec 명시)도 함께 고친다.

### PER-09 · #470 출처 추적 상위 목표를 유지한다
- 종류: DEC | 규모: S | 태그: C
- 목표: #470을 현행 상위 목표로 유지하고 #368 생산·공통 계약, #685 소비, #471 대장 취소와의 관계를 명시한다. 새 작업 목록 작성만으로 열린 이슈를 종료하지 않는다.
- 완료 기준: #470 유지와 #471 취소를 구별하고 #368 → #685 범위 및 #650 별도 목표를 대응표에 반영한다. GitHub 상태 변경은 이번 문서 작업에 포함하지 않는다.
- 변경 범위: -
- 선행: PER-06 (하위 처분 확정 뒤)
- 충돌: -
- 흡수: #470 · PER-c12
- 비고: 이전 종료 제안은 2026-10-08 결정으로 대체됐다.

### PER-10 · 설정 초기값(default) 정책을 세운다 — 전수 조사표와 소유자·진입점·대역 로그 규칙
- 종류: DEC | 규모: S | 태그: A, E
- 목표: #423 의 1·2 단계. (1) 같은 JSON 키를 2곳 이상이 리터럴 대역으로 읽는 패턴(`"active"` `toBool(true)` 20곳/12파일 등 이슈 표의 키 14개) · `.ui`/멤버 초기값 이중화(.ui 6개) · `QSettings` 대역(36줄/12파일)을 dev 에서 확정한 조사표 (2) 초기값 3분류(정책 default · escape · sentinel) · 키별 소유자 1곳 · 진입점 1개 · `.ui` 리터럴 처분 · 대역 사용 시 WARN 규칙을 docs/ 에 기록. 적용(3 단계)은 키별 소유 모듈 항목 — 첫 사례 MOR-11.
- 완료 기준:
  1. 조사표 — **이슈 표의 키 14개**에 한정해 dev 수치로 재확정(키 · 읽는 곳 · 대역값 · 소유자 후보). 전수 재조사는 하지 않는다: 주요 수치가 재측정에서 일치했다(`"active"` `toBool(true)` 20곳/12파일 · `QSettings` 36줄/12파일) — 미재확인은 `.ui` 초기값 이중화 6개(패턴 C)뿐이라 그 6개만 센다
  2. 정책 문서(docs/persistence.md 절 신설) — 분류 · 소유자 규칙 · 진입점 · `.ui` 리터럴 · 로그 규칙
  3. PER-02 헬퍼 계약에 "키 부재 = 소유자 default 로 채운다(대역은 WARN)" 가 어떻게 얹히는지 1절
- 변경 범위: docs/persistence.md (기록만) — 코드 변경 없음
- 선행: -
- 충돌: B2 교집합: persistence.md → PER-01 PER-03
- 흡수: #423 (1·2 단계, MOR-c46 이관) · PER-c31
- 비고: PER-02 와 독립이지만 완료 기준 3(헬퍼 계약에 얹히는 방식)을 쓰려면 **PER-02 보다 앞**이 자연스럽다 — 머리말 권장 순서가 그 순서다. 선행란에 ID 를 적지 않은 것은 의도(괄호 안 ID 가 선행으로 파싱되는 것을 막는다 — 검토 #10). 종류는 조사 몫이 작아 `DEC` 유지(1-2 절 5종). #423 주 모듈은 MOR(배정표) 이고 3 단계 첫 사례가 MOR-11 — 1·2 단계는 횡단이라 PER. `"active"` 는 DOE 케이스 활성 플래그로 model 11파일에 흩어져 적용 몫은 LCH 가 가장 크다. 되돌리기 비용 낮은 결정(문서) — 간단히 정하고 넘어간다.

### PER-11 · #471 독립 산출물·소비 대장 취소를 유지한다
- 종류: CLOSE | 규모: S | 태그: C, A
- 목표: 별도 산출물·소비 대장을 구축하지 않는다. 각 Set의 현재 입력 참조와 산출물의 생성 당시 출처를 원본으로 삼고 프로젝트 객체가 조회·집계한다.
- 완료 기준: 대장 취소 근거를 기존 Set JSON의 setId 참조와 #368·#685의 개별 출처 기록·판독 계약으로 설명한다. 현재 참조 조회와 과거 산출물 출처 조회를 구분하며 조합 ID 스캔으로 소비 이력을 복원한다고 보장하지 않는다. 전체 이력 보존은 요구하지 않는다.
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #471 · PER-c14
- 비고: #471 취소는 유지하며 #470은 PER-09에 따라 유지한다. 대장 재도입을 조건부 후속 PR로 미리 요구하지 않는다.

## 대응표

| 원천 | 항목 | 비고 |
|---|---|---|
| #478 | PER-01 · PER-02 · PER-05 | 소비자별 코덱·헬퍼 이행은 범위밖 → MOR/CAD/CON/DOE/PRE/BLD/RUN/OPT/PRJ (PER-c22~c30) · 미채택 층 처분 PER-08 |
| #479 | PER-02 | 직쓰기 22지점 이행 → 모듈별 (PER-c22~c30) · 텍스트·CSV 21지점은 항목 없음(c07 비고) |
| #480 | PER-03 · PER-04 | 모듈 Set JSON 의 키 부여는 헬퍼 이행과 동시 (모듈별) |
| #470 | PER-09 (DEC) | 출처 추적 상위 목표 유지 |
| #471 | PER-11 (CLOSE) · PER-06 | 독립 대장 취소 유지. 각 Set·산출물의 원본 기록을 프로젝트가 조회·집계 |
| #368 (담당 PER) | PER-06 · PER-07 | 공통 계약 → DOE-16 → PRE-32(+LCH-33) → BLD-20 생산 완료. #685 소비는 RUN-34·OPT-26 |
| #443 (접점 · PRJ 담당) | PER-06 · PER-07 | #520 setId 기반 입력 참조 전환은 #368 → #685. #444는 #441 하위 조건부 분리, #369는 독립 |
| #473 (접점 · RUN 담당) | 범위밖 → RUN (PER-c16) | 기존 항목 키·파일 소속·실제 충돌 검사로 결함 수정, 새 채번 키 요구 없음 |
| #638 (접점 · PRE 담당) | 범위밖 → PRE (PER-c19) | 공통 규칙은 PER-02 — PRE 항목 선행에 PER-02 제안 |
| Project-Manifest-Set-Identity-And-Decision-Revisions | PER-06 · PER-07 (SI-5 · D20 · D21 부속 철회 · D26) | SI-6a → 범위밖 PRJ (PER-c20) · D16/후속작업 4 sha256 → 미확인 (PER-c21) |
| #411 결정 3 (PRE-c60 이관) | PER-03 | 결과 XML 의 버전 키는 같은 규약을 쓰되 작성은 PRE-29 (PER-c32) |
| #423 1·2 단계 (MOR-c46 이관) | PER-10 | 전수 조사 + 정책 문서. 3 단계 첫 사례 MOR-11 (PER-c31) |
| DOE-D22 PER 몫 (EXE-c41 이관) | PER-02 | 원자 쓰기·사유 반환 (PER-c33). 직렬화는 LCH(DOE-c18) |
| Cross-Module-Defect-Index "왕복 단절" 28건 | PER-05 (게이트) · 02-claims 부록 A | 각 결함 수정은 모듈 항목 — 부록 A 가 Phase B 배분표 |
