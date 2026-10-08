# 저장·식별·산출물 설계 문서 교차 검토

기준일: 2026-10-08. 원문·정본·코드는 변경하지 않았고 원격 조회도 하지 않았다. 최신 정책 기준은 `Issue-Revision-History.md`의 개정 이력(9–23행)과 현재 방향(57–85행)이다. 25–53행의 추가 개정 계획은 팀 논의안이며 이미 반영된 결정과 구분했다.

**주요 5건은 모두 document_drift다.** 담당 범위에서 우선순위가 정해지지 않은 별개의 확정 계약 간 active_conflict는 확인하지 않았다. 아래의 대안/역사 3건은 활성 충돌 수에 포함하지 않는다. 이전 작업 목록은 작성 시점 스냅샷으로 보존할 수 있으나 착수용으로 다시 읽을 때 최신 개정 안내가 필요하다.

## DS-01 · 조합 ID·최초 입력 영구핀 폐기가 Manifest와 두 작업 목록에 미반영

분류: `document_drift` · 심각도: high · 신뢰도: 높음

10월 8일 개정은 parameterizationId와 최초 입력 영구 고정을 폐기했다. 현재 입력 Set 참조는 바꿀 수 있고, 이미 생성한 산출물의 출처는 입력 선택만으로 바뀌지 않으며 재실행 덮어쓰기 시 함께 갱신한다. Manifest의 조합 동일성 차단, Codex PRJ-03, Claude PER-06/07·홉별 작업을 그대로 적용하면 최신 동작과 반대가 된다. 이는 선택 대안 간 미결 충돌이 아니라 명시적 후속 개정의 미전파다.

근거:

- `Issue-Revision-History.md:9–9` (최신 개정): | 2026-10-08 | [#368](https://github.com/NumeRealWorks/DashOpti_GUI/issues/368) 출처 기록과 공통 판독 계약 | 기존 개정 수록 | 조합 ID의 생성·전파·비교와 입력 고정 규칙을 포함하고, Runner·Optimizer 처리까지 함께 다룸 | `parameterizationId`와 최초 입력 영구 고정을 폐기. 개별 `setId`와 실제 입력 선택·deck 정보를 산출물에 기록. 현재 입력 참조와 생성 당시 출처를 분리 | 완료 지점을 Builder의 `model_info.json` 생성으로 한정. 공통 기록·판독 계약을 제공하고 소비 측 T23은 #685로 이관. 버전·최신성은 #650에서 별도 설계 |
- `Issue-Revision-History.md:21–21` (현재 참조/산출물 출처 규칙): #368·#685의 공통 정책은 기존 선택 UI에서 현재 Set이 참조하는 상류 입력 Set을 다른 `setId`의 Set으로 변경할 수 있게 하는 것이다. 현재 Set 자체의 `setId`는 유지하며, 입력 참조 변경만으로 산출물의 출처를 수정하지 않는다. 재실행으로 산출물을 덮어쓸 때에는 실제 사용한 입력 출처도 함께 갱신한다. 이전 산출물과 출처의 이력 보존은 요구하지 않는다. 별도로, 필수 출처가 없는 구버전 산출물은 재생성을 요구하며, 이름·경로 추론이나 자동 마이그레이션으로 출처를 채우지 않는다. 기존 Set ID 발급·복원은 유지한다.
- `Project-Manifest-0-Work-Order.md:64–66` (이전 문서): | D18 (재개정) | 소유자 집합                       | **파이프라인 8모듈 — Condition·Morphing(생성 시점 핀) · CAD(키 미도입 — #366 · D31 유보) · Launcher(`referenceModel` 대신 `parameterization` — DOE 선택 시 조합 기록) + Preprocessor·Builder·Runner·Optimizer(최초 연결 시점 핀).** Analyzer·AIGeo 만 제외. ModelRunner 의 NodeSet 소스는 별도 키. 근거는 [Project-Manifest-3-Module-Deck-Ownership](Project-Manifest-3-Module-Deck-Ownership.md) "소유자" 절  | | D19 (개정)  | 파이프라인 불변식 보장                 | **산출물 스탬프 + Set 핀 + 홉별 검증.** 불변식은 단일 deck 이 아니라 **DOE 조합**(Geometry Set 1 + Condition Set N — D23)의 동일성이다. 산출물 스탬프의 형태는 D26 이 정한다(조합 id + 형상 deck). 상세는 문서 3 "파이프라인 스탬프" 절 | | D20 (재개정)  | 스탬프·핀 불일치 시                  | **차단.** 판정 기준은 deck 단일성이 아니라 **DOE 조합 일치**(D23)다 — 서로 다른 deck 의 입력이라도 같은 조합이면 정상이다. 불일치 시 거부하고 "다른 조합이면 새 Set" 안내 — D17 동형. **구버전 폴백 불도입 — 무스탬프 산출물은 연결 차단** + "스탬프 없는 구산출물 — 재실행 필요" 안내(차단 문형 동형). 라이브 체인은 part 명 조회 용도만 잔존. 핀은 id 를 든 첫 입력에서 걸린다                                                              |
- `Project-Manifest-3-Module-Deck-Ownership.md:123–123` (이전 문서): - **핀은 최초 연결 1회.** 이후 다른 조합의 입력·연결·사용은 차단하고 "다른 조합이면 새 Set" 을 안내한다(D20) — D17 과 동형. "연결 시점 갱신" 개념은 없다.
- `new_tickets_codex/03_TASK_CATALOG.json:3250–3250` (이전 문서):       "Preprocess·Sim Builder·Sim Runner/Optimizer 최초 연결에서 조합 id를 pin하고 이후 다른 조합/무스탬프 구산출물을 이유·재실행 안내와 함께 차단한다.",
- `new_tickets_claude/05-final/FINAL.md:3326–3326` (이전 문서): - 비고: #368 본체 = 이 항목(결정) + PER-07(공통부 PR). **"스탬프 소비자 0" 해소 경로**(검토 #3 · C-2 ⑤) — DOE-16 이 `saveResultsAsDvTable` 에서 Table 루트에 2키를 쓰고 같은 항목이 `kSnapshotKeys` 에 그 2키를 더한다 → Start 의 스냅샷이 스탬프를 운반한다 → PRE-32 가 스냅샷의 스탬프를 **읽어** 검증한다(`derivedId` 재계산 금지 — "T21~T23 은 T27 이 낸 id 를 읽기만 한다") → BLD-20 · RUN-34 · OPT-26 이 각 Set JSON 에 핀하고 불일치를 차단한다. allowlist 가 빠지면 스냅샷에 읽을 값이 없어 소비자가 0 으로 되돌아간다. 접점(홉별, 각 모듈 항목이 이 결정을 선행으로 참조): T27 → DOE-16(LCH-c35 · DOE-c31) · T21 → PRE-32(LCH-c36) · T22 → BLD-20(LCH-c37) · T23 → RUN-34 · OPT-26(LCH-c38). LCH-c35 가 요청한 DEC. SI-5 산식 자체(정렬 setId 연접 · 해시 없음 · 파싱 금지)는 Set-Identity 정본대로 유지하고 자리만 정한다. ④ 는 CLOSE 로 닫혔으므로 "대장 파일 1개 + 소비 기록 쓰기" PR 은 발행하지 않는다 — 되살리는 조건은 PER-11 비고.
- `new_tickets_claude/05-final/FINAL.md:3330–3330` (이전 문서): - 목표: **노선 = 재업로드(dev 리베이스 후 새 PR)** — PR #530 은 머지하지 않는다(C-2 ②: base `feat/reference-model-manifest` 가 스쿼시(198a294c)돼 merge-base 가 dev 조상이 아니고, 같은 PR 의 T21/T27 이 구 파일명 `DashDataProcessor*` 를 고친다). 이 항목은 #530 T27 커밋의 **공통부만** dev 기준으로 다시 올린다 — `model/DashPipelineStamp.h`(키 2종 + D20 차단 문구 2종) · `DashParameterization::derivedId()`(SI-5: geometry setId + 정렬 condition setId 연접 ",", 성분 setId 결손 시 빈 문자열) · `tests/test_doe_selection.cpp` 의 derivedId 케이스(멱등 · 정렬 · 결손). 분담 — 기록부·홉별 핀·검증은 이 항목 범위 **밖**이고 5건이 전부 신설·확정됐다: DOE-16(T27 Table 기록 + `kSnapshotKeys`) · PRE-32(T21 Preprocess 입력 검증) · BLD-20(T22 Builder 핀·검증) · RUN-34(T23 Runner 핀·검증) · OPT-26(T23 Optimizer 핀·검증).
- `new_tickets_codex/07_BOARD_OVERLAY.md:82–82` (이전 문서): 2. **#368 PR 처리:** 10월7일 조회에서 PR530은 병합 없이 CLOSED다. PRJ-03의 기능 목적은 연결되지만 `in_flight`/기존 PR 통합 설명은 현재 계획으로 갱신해야 한다. 구현 재이식과 홉별 검증으로 읽는다.

영향: 기존 Set에서 다른 입력을 선택할 때 불필요한 새 Set 생성을 요구하고 폐기된 조합 키·산식·테스트를 다시 구현할 수 있다. DOE/Preprocess/Builder/Runner/Optimizer 전 경로와 그 의존 작업이 영향받는다.

조치: 최신 개정 링크와 적용일을 기존 마스터·작업 목록 머리에 붙이고 구 스탬프 작업을 개별 setId·실제 입력 선택·deck 출처 생산/검증 작업으로 재정의한다. 출처 없는 구산출물 재생성 요구는 유지한다. 버전·최신성은 #650 별도 계약이며 이 변경만으로 최신성 경고 작업을 삭제하지 않는다.

## DS-02 · 산출물·소비 이력 대장 취소가 Codex 구현 카드와 보드 대응표에 미반영

분류: `document_drift` · 심각도: high · 신뢰도: 높음

10월 8일 기록은 #471의 독립 대장을 취소하고 과거 산출물·출처 이력 보존도 요구하지 않는다. Codex PRJ-05/IO-10/IO-11의 대장 및 과거 소비 이력은 그 이전 요구다. Claude PER-11의 대장 제외 결론은 최신 방향과 맞지만 parameterizationId 핀을 스캔하면 역방향 소비를 복원한다는 근거는 폐기된 조합 계약을 사용하므로 별도 수정해야 한다.

근거:

- `Issue-Revision-History.md:21–23` (최신 개정): #368·#685의 공통 정책은 기존 선택 UI에서 현재 Set이 참조하는 상류 입력 Set을 다른 `setId`의 Set으로 변경할 수 있게 하는 것이다. 현재 Set 자체의 `setId`는 유지하며, 입력 참조 변경만으로 산출물의 출처를 수정하지 않는다. 재실행으로 산출물을 덮어쓸 때에는 실제 사용한 입력 출처도 함께 갱신한다. 이전 산출물과 출처의 이력 보존은 요구하지 않는다. 별도로, 필수 출처가 없는 구버전 산출물은 재생성을 요구하며, 이름·경로 추론이나 자동 마이그레이션으로 출처를 채우지 않는다. 기존 Set ID 발급·복원은 유지한다.  이번 범위 정리는 [#471](https://github.com/NumeRealWorks/DashOpti_GUI/issues/471)의 독립 산출물·소비 이력 대장 취소 결정을 따른다. 출처 추적의 상위 목표는 [#470](https://github.com/NumeRealWorks/DashOpti_GUI/issues/470)에서 관리한다. 기존 이슈의 열린 상태와 종료 상태는 변경하지 않았다.
- `Issue-Revision-History.md:61–63` (현재 책임/보장 범위): | 원본과 책임 | Set 설정은 현재 입력 참조, 산출물은 생성 당시 출처를 보유. 별도 산출물·소비 이력 대장은 취소. 프로젝트 객체가 Set·의존관계를 조회하고 개별 Set의 최신성 판정을 호출·집계하며, VM은 표시·동작 전달 담당 | 공유 판독 계약과 프로젝트 객체의 조회·집계 API. 개별 Set의 판정 책임을 유지하면서 연결할 방법 | | 식별의 의미 | `setId`는 Set, 항목 키는 개별 결과, 버전은 재생성 전후를 구분. 이름·번호·경로는 표시나 위치이며 이 세 역할을 대신하지 않음 | #474·#477의 최소 항목 키, #650의 버전 의미·비교 불가 상태, #643의 이어쓰기 기준 | | 입력 참조 변경과 재실행 | 조합 ID와 최초 입력 영구 고정을 폐기. DOE Sampler·Analysis Launcher·Model Builder·Model Runner·Optimizer에서 상류 입력 Set의 참조를 다른 `setId`로 변경할 수 있음(대상 관계는 아래 표). 현재 Set 자체의 ID는 유지. 참조 변경만으로 산출물의 출처를 수정하지 않으며, 재실행으로 산출물을 덮어쓸 때 실제 입력 출처도 함께 갱신. 이전 산출물과 출처의 이력 보존은 요구하지 않음 | #615의 자동 선택 정책과 #646의 결과 교체 시점. 재실행 결과와 출처가 함께 갱신되도록 할 경계. 출처 정보가 없는 구버전 산출물의 재생성 정책과는 구분 |
- `new_tickets_codex/03_TASK_CATALOG.json:3318–3318` (이전 문서):     "title": "실행과 산출물의 생성·소비 관계를 파일 대장에 기록한다",
- `new_tickets_codex/03_TASK_CATALOG.json:4607–4607` (이전 문서):       "재학습/모델삭제가 이전 실행 이력의 출처를 소급 변경하지 않게 한다."
- `new_tickets_codex/03_TASK_CATALOG.json:4645–4645` (이전 문서):       "이동/재실행/취소/삭제에서 과거 기록과 현재 파일 가용성을 분리한다."
- `new_tickets_claude/05-final/FINAL.md:3383–3383` (이전 문서):   1. 닫기 사유 4가지 — ① 설계 문서 `Project-Manifest-8-Run-Artifact-Ledger` 는 2026-09-19 폐기(Publication-Plan 주11)이고 조회 UI #476·#445 는 범위 정리로 닫혔다 ② dev 에 대장 구현 0 (대장 파일·소비 기록 코드 없음) ③ 유래의 **정방향**은 이미 기록된다 — `tableId`(스냅샷 ↔ 케이스 상태 ↔ 하류 stale 판정: `DashUpstreamStaleness.h` 4곳 · `DashAnalysisLauncherConfig` 7곳 · `DashLauncherRuns` 5곳) + `referenceModels.json` 원장 ④ **역방향** 소비 기록은 하류 핀이 대신한다 — T21~T23 이 각 Set JSON 에 쓰는 `parameterizationId`(PRE-32 · BLD-20 · RUN-34 · OPT-26)를 스캔하면 "무엇이 무엇을 소비했나" 가 복원된다
- `new_tickets_codex/07_BOARD_OVERLAY.md:81–81` (이전 문서): 1. **#471 대장 존폐:** Codex는 별도 생산·소비 대장을 구현하고 Claude PER-11은 불필요하다고 닫는 방향이다. 현재 연결의 추적과 과거 실행별 소비 이력 요구를 구분해 결정해야 한다. #650의 세대 경고까지 함께 제거할 근거는 아니다.
- `Backlog-Issue-Publication-Plan.md:173–173` (이전 설계 폐기 기록): 11. **목록 UI 4분할** — B7d(실행) · C2d(Set) · C3b(산출물) · C4c(항목) 이 전부 후행·신규다. 통합 후보. 설계는 문서 8(산출물 대장 · 폐기됨 2026-09-19) · 문서 6(Set Registry · 폐기됨 2026-09-19).

영향: 이미 취소한 영구 이력 저장을 구축하거나, 어제의 미결 판정을 보고 대장 존폐 논의를 다시 열 수 있다. 현재 Set 참조/산출물 출처 조회와 과거 실행별 소비 이력은 동일 보장이 아니다.

조치: 대장 카드 3종은 최신 범위에서 제외/대체 대상으로 표시한다. 필요한 현재 관계 조회는 Set·산출물 원본 기록을 프로젝트가 조회·집계하는 API로 다시 적는다. PER-11은 현재 정책을 근거로 바꾸고 옛 핀 스캔 설명을 역사로 남긴다. 07_BOARD_OVERLAY는 10월 7일 스냅샷임을 유지하되 최신 정책 안내를 추가한다.

## DS-03 · 별도 Set 원장 도입 카드가 setId 파일 정본 결정과 어긋남

분류: `document_drift` · 심각도: high · 신뢰도: 높음

별도 Set 원장 불도입은 SI-2에서 이미 명시됐고 10월 8일 #443 개정이 다시 확인한다. 기존 발급·영속·역조회에 기반한 입력 참조 전환이 잔여 작업이다. Codex PRJ-04의 Set 목록 정본을 별도 원장으로 옮기는 작업은 현재 범위와 다르다. referenceModels.json이라는 기준 deck 원장까지 폐기한다는 의미는 아니다.

근거:

- `Project-Manifest-Set-Identity-And-Decision-Revisions.md:29–30` (Set 정본 결정): | SI-2 | 저장 위치 | **각 `{Module}_{Set}.json` 의 `setId` 키가 정본.** 별도 Set 원장은 두지 않는다 — Set 은 파일별 영속이 이미 있어 원장 근거가 없다. setId → Set 역조회는 열기 시 전 Set 스캔(`restoreExistingModules` 가 이미 전 파일을 읽는다 — 추가 비용 0). 열기 시 중복 감지(json 손 복제) → 나중 파일 재발급 + 로그 | | SI-3 | 발급·저장 시점 | **신규 Set = 생성 핸들러**(생성 시 json 이 어차피 써진다 — 추가 저장 규약 0). **구버전 Set(키 부재) = 열기 복원 시 발급 + 즉시 write-back 1회.** 쓰기 실패 = 로그 + 메모리 유지, 다음 열기 재발급. P5 와 무마찰 — P5 의 취지는 적재·해싱 지연이지 쓰기 금지가 아니다 |
- `Issue-Revision-History.md:11–11` (최신 #443 범위): | 2026-10-08 | [#443](https://github.com/NumeRealWorks/DashOpti_GUI/issues/443) Set 입력 참조 | 개정 반영 | UUID 발급·별도 원장 구축을 목표로 기록 파일 분할과 NodeSet 선택 저장까지 포함 | 완료된 #520의 `setId` 발급·영속·역조회를 기반으로 개명·동명 재생성에 안전한 입력 참조 전환에 집중 | 남은 구현은 #368 → #685. #444와 #369를 하위에서 분리. 별도 Set 원장, 폴더명 ID 전환, 최신성 판정을 완료 조건에서 제외 |
- `new_tickets_codex/03_TASK_CATALOG.json:3281–3281` (이전 문서):     "title": "Set 목록의 정본을 파일명 탐색에서 setId 원장으로 옮긴다",
- `new_tickets_codex/03_TASK_CATALOG.json:3285–3285` (이전 문서):       "프로젝트 Set 원장을 도입하고 생성/삭제/복원/개명이 같은 경계를 통과하게 한다",
- `new_tickets_codex/07_BOARD_OVERLAY.md:53–53` (이전 문서): | 59 / #443 Set 식별·원장 | PRJ-04, PRJ-02; #444는 AL-05 관련 | 기존 setId 발급 재구현 금지. 원장 정책과 파일 분할 여부는 재판정 |
- `new_tickets_codex/07_BOARD_OVERLAY.md:83–83` (이전 문서): 3. **#443 Set 원장:** setId 발급과 원장으로의 정본 전환은 다르다. Codex PRJ-04와 Claude의 설정 파일 기반 관리 전략은 동일하지 않다. 또한 Set 생성 시 고아 폴더 충돌·삭제 시 산출물 정리 요구는 PRJ-02의 개명으로 대체되지 않는다. 기존 카탈로그의 명시적 완료 조건 공백으로 남긴다.

영향: setId가 이미 있는 프로젝트에 두 번째 정본과 동기화/복구 경계를 추가하고, 기존 파일 정본 전략과 반대되는 구현을 시작할 수 있다.

조치: PRJ-04는 새 원장 생성 대신 #368→#685의 참조 전환으로 귀속을 다시 정한다. 생성·삭제의 파일 정리 요구가 있으면 별도 실제 결함으로 검증하며 rename 전용 PRJ-02를 생성/삭제 작업의 대체로 삼지 않는다. 원장이라는 단어를 기준 deck 목록, Set 정본, 산출물 이력으로 분리한다.

## DS-04 · G9/PR530 전체를 선행으로 두는 작업 경계가 #368→#685 분리와 미동기화

분류: `document_drift` · 심각도: high · 신뢰도: 높음

Manifest의 산출물 폴더 식별과 기존 작업 목록은 G9/PR530 전체 이행을 기준으로 묶여 있다. 최신 #368은 Builder model_info.json 생성까지이고 소비 측은 #685이며, NodeSet 저장과 결과 항목 조작은 독립이다. 개명 PR #681도 #368/#685를 머지 조건으로 두지 않는다. PR530의 폐기 후 재이식이라는 이전 계획만 반영하면 새 책임 경계를 놓친다.

근거:

- `Issue-Revision-History.md:9–18` (확정 개정 범위/독립 작업): | 2026-10-08 | [#368](https://github.com/NumeRealWorks/DashOpti_GUI/issues/368) 출처 기록과 공통 판독 계약 | 기존 개정 수록 | 조합 ID의 생성·전파·비교와 입력 고정 규칙을 포함하고, Runner·Optimizer 처리까지 함께 다룸 | `parameterizationId`와 최초 입력 영구 고정을 폐기. 개별 `setId`와 실제 입력 선택·deck 정보를 산출물에 기록. 현재 입력 참조와 생성 당시 출처를 분리 | 완료 지점을 Builder의 `model_info.json` 생성으로 한정. 공통 기록·판독 계약을 제공하고 소비 측 T23은 #685로 이관. 버전·최신성은 #650에서 별도 설계 | | 2026-10-08 | [#685](https://github.com/NumeRealWorks/DashOpti_GUI/issues/685) Runner·Optimizer의 Builder 참조 전환 | 기존 개정 수록 | Runner·Optimizer의 입력 처리·deck 판독·프리뷰 변경이 #368의 T23 범위에 포함 | Builder 산출물을 소비하는 경계부터 독립 작업으로 정리. Builder를 `setId`로 저장·복원하고 출처를 검증하며 실행·조회·프리뷰에 사용 | #368 선행, #443 하위 관계 유지. 생산 측 계약을 중복 정의하지 않음. 외부 실행에는 ID로 해석한 실제 경로 전달. #681의 머지 조건으로 두지 않음 | | 2026-10-08 | [#443](https://github.com/NumeRealWorks/DashOpti_GUI/issues/443) Set 입력 참조 | 개정 반영 | UUID 발급·별도 원장 구축을 목표로 기록 파일 분할과 NodeSet 선택 저장까지 포함 | 완료된 #520의 `setId` 발급·영속·역조회를 기반으로 개명·동명 재생성에 안전한 입력 참조 전환에 집중 | 남은 구현은 #368 → #685. #444와 #369를 하위에서 분리. 
- `Issue-Revision-History.md:10–10` (#681 조건 제외): | 2026-10-08 | [#685](https://github.com/NumeRealWorks/DashOpti_GUI/issues/685) Runner·Optimizer의 Builder 참조 전환 | 기존 개정 수록 | Runner·Optimizer의 입력 처리·deck 판독·프리뷰 변경이 #368의 T23 범위에 포함 | Builder 산출물을 소비하는 경계부터 독립 작업으로 정리. Builder를 `setId`로 저장·복원하고 출처를 검증하며 실행·조회·프리뷰에 사용 | #368 선행, #443 하위 관계 유지. 생산 측 계약을 중복 정의하지 않음. 외부 실행에는 ID로 해석한 실제 경로 전달. #681의 머지 조건으로 두지 않음 |
- `Project-Manifest-4-Ticket-Slicing.md:162–162` (이전 문서): | 범위 밖 | 산출물 폴더 식별(SI-6a — 폴더명 유지 · setId 색인 역조회) | 별개 이슈 덩어리(마스터 후속작업 14) — G9(#530) 머지 후, #443 하위 발행 |
- `Project-Manifest-0-Work-Order.md:192–192` (이전 문서): | 14 | **산출물 폴더 식별(SI-6a)** — 폴더명 `{Module}_{Set}` 유지, 변환 없음. 소비자는 setId 보유 + `DashProject::m_setIds` 역조회로 현행 `getModuleDir` 조립. 성립 조건 셋 — `renameSet` 의 산출물 폴더 동반 개명 · Set 참조 보관 자리의 setId 전환(Runner `modelBuilderFolder` · Optimizer 폴더 콤보 · 폴더명 역파싱 3곳) · 삭제 시 폴더 동반 삭제 + 생성 시 동명 폴더 거부. 선행 G9(#530) 머지. 규모 실측은 SI-6a | [Project-Manifest-Set-Identity-And-Decision-Revisions](Project-Manifest-Set-Identity-And-Decision-Revisions.md) |
- `new_tickets_codex/03_TASK_CATALOG.json:3246–3246` (이전 문서):       "이 PR의 전체 소비자 이관을 하나의 진행 작업으로 추적한다"
- `new_tickets_claude/05-final/decisions.md:27–30` (이전 문서): - 선행 치환 (9건): `PR #530 머지` → `PER-07 · <자기 모듈 홉 항목>`. BLD-13 · BLD-14 · BLD-15 · BLD-17 · BLD-18 · RUN-14 · RUN-25 · RUN-27 · RUN-31. **BLD-13 은 역전** — `loadLabelMetadata` 삭제 항목이라 BLD-20 이 BLD-13 뒤에 오고, #530 의 필터 hunk 는 드롭한다. - 충돌 치환 (89건, `#530`·`pipeline-deck-stamp`·`#368 T2x` 가 충돌란에 있는 항목): 자기 모듈 홉 항목 ID 로 바꾼다. 홉 항목이 없는 모듈(MOR CAD ANA PRJ REN UIC)은 그 파일을 고치는 홉 항목이 분명하면 그 ID, 아니면 삭제 — D-1 의 `build_deps.py --apply` 가 파일 교집합으로 다시 채운다. - 열린 PR 목록: #530 은 머지하지 않으므로 D-1 에서 `items_index.OPEN_PRS` 와 alias 에서 제거한다. open_prs.md 는 원천이라 그대로 둔다. - OPT-03 ↔ #368 D20 재개정(model_info 스탬프) 정면 충돌, OPT-04 의 pE 2곳은 #530 이 제거 → OPT 는 OPT-03+04 를 OPT-26 에 흡수하거나 병합 (OPT 검토 #4).
- `new_tickets_codex/07_BOARD_OVERLAY.md:82–82` (이전 문서): 2. **#368 PR 처리:** 10월7일 조회에서 PR530은 병합 없이 CLOSED다. PRJ-03의 기능 목적은 연결되지만 `in_flight`/기존 PR 통합 설명은 현재 계획으로 갱신해야 한다. 구현 재이식과 홉별 검증으로 읽는다.

영향: 개명·행 조작·NodeSet 같은 독립 수정이 폐기된 일괄 스탬프 작업을 기다리거나 생산자/소비자가 공통 출처 형식을 중복 정의할 수 있다. #650 최신성 작업의 필요성은 유지되지만 조합 ID 전제의 의존 수치는 재사용할 수 없다.

조치: 현재 의존 그래프를 #368 생산/공통 판독 → #685 Builder 소비 경계로 재작성한다. #369/#473의 독립성을 유지하고 공유 파일 충돌은 선행 요구와 구분한다. 예전 PR530 상태와 10월 7일 결과는 역사로 보존한다. 최신 #643/#514/#615 세부 조율안은 아직 팀 논의 계획임을 함께 표시한다.

## DS-05 · Load 단일 등록 규칙의 마스터 요약에 D15 예외가 누락

분류: `document_drift` · 심각도: medium · 신뢰도: 높음

마스터 P4는 등록이 Load 버튼 한 곳의 명시 호출이라고 단정한다. 같은 설계의 개정 정본과 모듈 소유 문서는 구 Set의 DV source를 복원할 때 원장 등록 후 핀하도록 하는 유일한 예외를 명시한다. 예외는 정해졌으나 진입 문서의 규칙 요약에 전파되지 않았다.

근거:

- `Project-Manifest-0-Work-Order.md:38–38` (마스터 단일 등록 규칙): | P4 | 등록은 Load 버튼 핸들러 한 곳의 `registerReferenceModel` 명시 호출 — `getOrLoad` 는 자격을 판정하지 않는 순수 캐시 조회로 남는다. 원장에 `role` 분류 필드를 두지 않는 근거이기도 하다 |
- `Project-Manifest-Set-Identity-And-Decision-Revisions.md:40–40` (명시 개정 예외): | D15 (재개정) | 키 부재 시 진입 1회 **전역 reference** 를 읽어 핀 + 다음 저장 backfill. multi-source json 은 핀 deck 밖 행을 읽기 전용 보존 | **핀 출처 = Set 자신의 DV `source`** — Condition 은 상대경로 그대로, Morphing 은 bare filename 을 configs 복사본 → 원장 `path` → 루트 스캔 순으로 해석. 복수 히트는 없다고 가정 — 결정적 1건(정렬 후 첫번째) + 로그. 유도분은 **원장에 등록한 뒤** 핀한다 — M3·P4 "등록 지점은 Load 핸들러 하나" 의 유일한 예외. 등록 없이는 다음 열기의 D16 해석이 미스라 backfill 이 자기 자신을 못 넘긴다. 등록 실패 시 핀하지 않고 다음 진입에 재시도. 유도 실패 시에만 전역 폴백, 빈 값이면 핀하지 않음(유지). 소급 없음 — 기존 핀 불문. **multi-source json 은 진입 시 1회 자동 분할**(deck 별 Set) + `.bak` 보존 + 결과 통지(선택지 없음) | 전역 출처는 첫 진입 시점의 우연(다른 deck Load 상태)을 영구 동결한다 — G7 이 닫은 대표 결함이 마이그레이션 코호트에서 1회 재현된 채 D17(변경 UI 불요)로 정정 불가가 된다. 종전 현행은 매 진입 재평가라 복구 가능했으므로 이 케이스에 한해 개악이었다. Set 자신의 DV source 가 더 충실한 역사적 증거다 |
- `Project-Manifest-3-Module-Deck-Ownership.md:207–207` (예외의 구현 조건): | 원장 등록 | 유도분은 원장에 등록한 뒤 핀한다 — "등록 지점은 Load 핸들러 하나(M3·P4)" 의 유일한 예외. 등록 없이는 다음 열기의 D16 1단이 미스라 backfill 이 자기 자신을 못 넘긴다. 등록 실패 시 핀하지 않고 다음 진입에 재시도 |

영향: P4만 따라 구현하거나 리뷰하면 구 Set 복원에서 필요한 등록을 제거하거나 금지할 수 있다. 최신 출처 없는 산출물 자동 마이그레이션 금지와는 객체가 다르다.

조치: 마스터 P4에 D15의 한정 예외를 직접 연결한다. 이 항목은 기존 Set 설정의 referenceModel 복원에 관한 역사적 계약이며, #368의 구산출물 출처를 추정해 채우는 허용 근거로 사용하지 않는다.

## DS-06 · Store α/β·정의 버전안·ID 발급안의 차이는 미채택 대안

분류: `proposal_alternative` · 심각도: low · 신뢰도: 높음

Store 8종은 Index와 각 문서가 미확정임을 명시한다. 실행 파일/대장 유무, 정의 해시와 산출 rev, 3루트 유지와 β 재배치, 구버전 승격과 거부, 난수 ID와 이름 기반 v5는 대안별 비용/보장이 다르다. 구상 안의 정본·확정이라는 내부 표현만 떼어 현재 제품 계약으로 간주할 수 없다.

근거:

- `minhopark-Index.md:25–27` (문서군 상태): ### 설계 — 미확정 (착수 근거로 인용 불가)  아래 표에 없는 셋 — [정의 버전 최소안](Project-Store-Design-Definition-Version-Minimal.md) · [엣지 3종 전량 커버 최소안](Project-Store-Design-Edge-Complete-Minimal.md) · [의존성과 상태의 화면 표시](Project-Store-Design-Dependency-State-Display.md). 요약 미작성.
- `Project-Store-Design-Layer-Cut.md:13–17` (β 상태): > ## ⚠ 문서 상태: 구상 — **확정 아님** > > * **팀 합의 전, 착수 승인 전.** 이 문서로 구현에 착수하거나 티켓을 만들거나 스키마를 계약으로 인용하지 않는다 > * 확정되려면 : 10절 잔여 7건(조사·인계) + 8.3.4 미결 9건(사용자 행동 정책) 해소 → 팀 리뷰 → 계약 문서로 승격 > * 실행 검증 없음. 빌드·실행 없이 정적 근거만
- `Project-Store-Design-Entity-Model-Options.md:7–11` (아이디에이션 상태): > | 단계 | 문제 분석 + 발산적 아이디에이션. **설계 확정 전, 팀 합의 전, 착수 승인 전** | > | 확정된 것 | **없음.** 1\~4절의 현황 진단만 코드 근거를 가지며, 5절 이후는 전부 검토 대상 | > | 이 문서로 하면 안 되는 것 | 구현 착수 · 일정 산정 · 티켓 생성 · 외부 커밋. 엔티티 이름/ID 규칙/파일 레이아웃 어느 것도 계약이 아님 | > | 확정되려면 | 11절 열린 질문 6건 해소 → 팀 리뷰 → 별도 **계약 문서**(9.2절 0단계) 작성. 그 계약 문서가 나오기 전까지 본 문서는 인용 근거가 아니라 논의 재료임 | > | 대안 취급 | 5절의 A/B/C 3안은 **비교를 위해 나열한 것**이며 C안 "추천"은 작성자 1인의 잠정 의견이다. 3안 밖의 4번째 안이 나올 여지를 닫지 않았음 |
- `Project-Store-Design-Edge-Complete-Minimal.md:8–8` (지문/계보 차이 명시): > * [Project-Store-Design-Definition-Version-Minimal](Project-Store-Design-Definition-Version-Minimal.md) — 이 안에서 **run 파일을 뺀 판**. 지문이 3종에서 정의 1종으로 줄고 그 자리가 계보 파일이 아니라 소비자 SM 안(`upstream.consumed`)이며, 배지가 2종이고 PM 이 `instances[]` 를 갖지 않는다(모듈·variant 는 config 자기신고). 5.2 가 "실행 `rev` 를 SM 으로 옮기지 않는" 근거 넷을 댄 자리에서 그 안은 **정수 카운터 자체를 버리고 정의 블록 지문**을 쓴다 — 실행 상태가 SM 에 남는 한 카운터는 쓰기 트리거라 상태 전이마다 오르지만 내용 지문은 움직이지 않는다. 지불하는 축은 하나, **정의 무변경 재실행을 하류가 모른다**(이 안 5.2 의 산출 `rev` 가 닫던 것). 그 대신 **계보를 직속이 아니라 조상 전량으로 든다** — 6.3 이 전파를 하지 않는 근거로 든 "산출 `rev` 는 상류의 상위가 바뀌었다고 오르지 않는다" 가 그쪽에는 없으므로, 조상 전량을 `consumed` 에 담지 않으면 상위 정의 변경이 하류에 영구히 닿지 않는다
- `Project-Store-Design-Wiring-Project-To-Launcher.md:15–17` (배선은 제안): > ## ⚠ 문서 상태: 구상 — 확정 아님 > > 팀 합의 전 · 착수 승인 전. 여기의 좌표는 실측이고 **배선 판정은 제안**이다.
- `Project-Store-Design-Wiring-Project-To-Launcher.md:160–163` (구안의 v5): | `ref_` | `UUID::from_namespace(ns_ref, 프로젝트상대경로)` | `[Add File]` 등록 · 승격 | **경로가 곧 유일 키다** — [Add File] 은 이름을 바꾸지 않고(`view/DashMainWindow.cpp:2176`) 같은 이름이면 덮어쓸지 묻는다(`:2178-2185`). 같은 경로에 항목이 둘일 수 없다 | | `inst_` | `UUID::from_namespace(ns_inst, "{Module}_{Set}")` | Set 생성 · 승격 | **승격이 멱등해진다** — 아래 |  **둘 다 v5(네임스페이스)이고 난수 발급(`create()`)을 쓰지 않는다.** 네임스페이스 UUID 는 하드코딩 상수 2개이고, **같은 패턴의 선례가 같은 파일에 있다** — `rwResolveContentIdentity` 가 하드코딩 `ns` + canonicalPath 로 deck 의 content uuid 를 만든다(`controller/DashRwSession.cpp:1105-1108`).
- `Project-Manifest-Set-Identity-And-Decision-Revisions.md:28–29` (이후 실제 Set 결정): | SI-1 | 형식 | **12자리 랜덤 hex(v4 절단)** + 발급 시 프로젝트 내 중복 검사. 생성 순서는 id 에 싣지 않는다 — 필요 시 `createdAt` 필드. v5 파생 배제 — Set 은 안정된 자연 키가 없어(이름 가변) 파생 원천이 없다. 카운터 배제 — 고수위 유실 시 번호 재사용이 곧 재바인딩 결함의 재생산이다 | | SI-2 | 저장 위치 | **각 `{Module}_{Set}.json` 의 `setId` 키가 정본.** 별도 Set 원장은 두지 않는다 — Set 은 파일별 영속이 이미 있어 원장 근거가 없다. setId → Set 역조회는 열기 시 전 Set 스캔(`restoreExistingModules` 가 이미 전 파일을 읽는다 — 추가 비용 0). 열기 시 중복 감지(json 손 복제) → 나중 파일 재발급 + 로그 |

영향: 이를 모두 동시에 이행하면 불필요한 스키마와 마이그레이션 작업이 늘지만, 문서 상태를 존중하면 현재 확정 충돌은 아니다.

조치: 미채택 비교 자료로 보존한다. 현재 Set 발급/정본은 SI-1/SI-2와 최신 이력에 따라 해석한다. 정의 지문만 쓰는 안은 동일 정의 재실행을 감지하지 못한다는 명시된 한계를 #650 검토 자료로만 사용한다.

## DS-07 · 스키마 버전·산출 세대·Set ID는 다른 계약이며 버전 키 확대는 미결

분류: `proposal_alternative` · 심각도: medium · 신뢰도: 높음

D14는 referenceModel 키 도입 시 버전 증가 없이 키 부재로 구형을 구분하는 결정이다. Claude PER-03은 이를 개정하거나 #480을 기각할 선택을 명시한 결정 작업이고, Codex IO-01은 기존 DashSaveSystem의 format/class version 오류 경계를 다룬다. 아직 같은 저장 파일에 반대 동작이 동시에 확정됐다는 근거는 없다. #650의 산출물 버전도 저장 스키마 버전과 별개다.

근거:

- `Project-Manifest-0-Work-Order.md:60–60` (D14 범위): | D14 (개정) | 모듈 JSON 스키마                  | **`referenceModel` 객체 하나**에 `uuid`(조인 키)·`path`(표시·폴백 — D24). 스키마 버전은 올리지 않고 키 부재를 구버전 판정으로 쓴다                                                                                                                              |
- `new_tickets_claude/05-final/FINAL.md:3280–3282` (명시된 결정 작업): - 목표: 현행은 "키 부재 = 구버전"(D14 · `referenceModel`·`setId`·`tableId`)이고 버전 키는 `referenceModels.json` 의 `schemaVersion` 1종뿐이다. 다음을 정한다 — ① 키 이름(`schemaVersion` 재사용 권장)과 자리(루트) ② 값 의미(파일 종류별 정수, 앱 버전 아님) ③ 로드 판정(상위 버전 → 거절·읽기 전용 + 안내, 하위·부재 → 현행 키 부재 규약으로 해석 — 마이그레이션 프레임워크 불도입) ④ 구 파일 write-back 시점(SI-3 선례 "열기 시 1회" vs "다음 저장 시") ⑤ 대상 파일(모듈 Set JSON 7종 · DOE Table · AnalysisLauncher config · model_info.json · ModelRunner config · referenceModels.json) ⑥ `variant`(타입 판별) 와의 역할 분리 ⑦ 결과 XML(PRE-28·29)이 같은 규약을 쓰는지 — #444 분할 파일은 빠진다(LCH-32 가 "분할하지 않음" 으로 확정). - 완료 기준:   1. 결정 기록 7항 + 대상 파일별 초기 버전값 표 + **D14 개정 기록**(정본 문서 `Project-Manifest-0-Work-Order.md` 결정표 — "스키마 버전은 올리지 않고 키 부재를 구버전 판정으로" 가 #480 과 정반대이므로, 이 항목은 곧 D14 개정이거나 D14 유지 + #480 기각이다)
- `new_tickets_codex/03_TASK_CATALOG.json:3552–3552` (이전 문서):       "DashSaveSystem의 지원 format/class version 검증과 문서 오류 반환을 명확히 한다",
- `new_tickets_codex/03_TASK_CATALOG.json:3585–3585` (이전 문서):     "notes": "QSaveFile과 version 필드는 이미 있다. registered-object 참조 누락 qFatal는 명시된 설계이므로 임의 변경하지 않고 도메인 적용 시 잘못된 파일의 선검증/오류 경계를 결정한다.",
- `Issue-Revision-History.md:19–19` (산출물 버전의 별도 책임): | 2026-10-08 | [#650](https://github.com/NumeRealWorks/DashOpti_GUI/issues/650) 산출물 버전과 최신성 | 개정 반영 | Set 참조·출처 기록과 같은 목표로 설명하고, Set ID와 산출물 버전의 역할이 혼재 | `setId`와 버전을 구분. 생산 Set이 버전을 기록하고 소비 Set이 실제 사용한 입력 버전으로 최신성을 판정. 프로젝트는 호출·집계, VM은 표시 담당 | #368·#685의 출처 계약과 별도 목표로 명시. 버전 의미·비교 불가 상태·판정 규칙을 먼저 정의. #473의 항목 키와도 구분 |
- `Issue-Revision-History.md:64–64` (구산출물 출처 정책): | 호환과 보장 범위 | 새 출처 정보가 없는 구버전 산출물은 재생성이 필요하며, 이름·경로 추론이나 자동 마이그레이션으로 출처를 채우지 않음. 기존 Set ID 발급·복원은 유지. 출처 추적만으로 같은 Set의 재실행 여부나 최신성까지 보장하지 않음 | 구버전 산출물의 재생성 안내와 적용 시점, 구버전 포맷 판독 호환의 범위. 최신성이 필요한 사용 경로와 #650의 도입 순서 |

영향: 한 버전 규약으로 묶으면 코드 저장 틀의 버전 거절을 모든 legacy 도메인 파일에 무조건 적용하거나, 구형 포맷을 읽는 것과 출처가 없는 산출물을 실행 입력으로 허용하는 것을 혼동한다.

조치: 파일 종류별로 schema version, Set id, 생성 버전, 출처 필수성의 네 칸을 결정 기록에 명시한다. IO-01에 도메인 키 확대까지 포함한다면 먼저 D14 변경을 명시하고, 읽기 호환을 출처 자동 보충으로 확대하지 않는다.

## DS-08 · NodeSet 절대경로와 무스탬프 폴백은 이미 개정된 역사

분류: `historical_resolved` · 심각도: low · 신뢰도: 높음

Set-Identity 개정표의 종전/개정 양쪽을 현재 요구로 읽으면 NodeSet 외부 절대경로 저장과 프로젝트 내 복사, 무스탬프 라이브 폴백과 재생성 요구가 충돌해 보인다. 그러나 표는 명시적 이전 이력이다. 최신 #369는 기존 nodeSetSource 저장·경로 설계를 유지하고, #368은 필수 출처 없는 구산출물 재생성을 요구한다.

근거:

- `Project-Manifest-Set-Identity-And-Decision-Revisions.md:43–43` (폴백 불도입 개정): | D20 (개정) | 스탬프 없는 구버전 산출물은 **라이브 체인 폴백으로 해석하고 검증 없이 통과** — 핀하지 않는다 | **구버전 폴백 불도입 — 무스탬프 산출물의 연결 차단** + "스탬프 없는 구산출물 — 재실행 필요" 안내(차단 문형 동형). 라이브 체인은 part 명 조회 용도만 잔존. 차단·재스탬프 금지 등 D20 본문의 나머지는 불변 | 폴백 유지 + "출처 미검증" 표시보다 코드가 적고, 무경고 재바인딩 결함이 구산출물에서 신호가 아니라 **소멸**로 닫힌다. G9 미구현(#368 보류)이라 걷어낼 코드가 아니라 안 짤 코드다. 구버전 호환 경시 방침·D28 폐기와 같은 철학이다 |
- `Project-Manifest-Set-Identity-And-Decision-Revisions.md:48–48` (NodeSet 경로 개정): | T18 스펙 (NodeSet 소스) | 루트 내부 = 상대, **밖 = 절대경로** 저장 | 루트 밖 선택 시 **프로젝트 안으로 복사 후 루트 상대경로 저장**(P1 동형 — 복사 위치는 Add Files to Project 관례인 프로젝트 루트). 절대경로 영속 없음 | 절대경로 영속은 G6 이 닫은 결함 부류(프로젝트 이동 시 파괴)의 재도입이고 경로 규약의 유일한 신규 예외였다. 루트 밖 deck 워크플로우가 실재해 거부 대신 복사를 취한다 |
- `Issue-Revision-History.md:18–18` (NodeSet 독립/기존 설계 유지): | 2026-10-08 | [#369](https://github.com/NumeRealWorks/DashOpti_GUI/issues/369) NodeSet 선택 저장 | 개정 반영 | #443의 하위 작업 | Runner의 독립적인 선택 저장·복원 작업으로 분리. 기존 `nodeSetSource` 저장·경로 처리 설계는 유지 | GitHub에서 #443 부모 관계 제거. #443·#368·#685의 완료 조건이나 선행 작업으로 두지 않음 |
- `Issue-Revision-History.md:21–21` (구산출물 재생성): #368·#685의 공통 정책은 기존 선택 UI에서 현재 Set이 참조하는 상류 입력 Set을 다른 `setId`의 Set으로 변경할 수 있게 하는 것이다. 현재 Set 자체의 `setId`는 유지하며, 입력 참조 변경만으로 산출물의 출처를 수정하지 않는다. 재실행으로 산출물을 덮어쓸 때에는 실제 사용한 입력 출처도 함께 갱신한다. 이전 산출물과 출처의 이력 보존은 요구하지 않는다. 별도로, 필수 출처가 없는 구버전 산출물은 재생성을 요구하며, 이름·경로 추론이나 자동 마이그레이션으로 출처를 채우지 않는다. 기존 Set ID 발급·복원은 유지한다.

영향: 구문서의 종전 열을 구현 지시로 인용하지 않으면 추가 설계 충돌이 없다. 기존 Set ID 발급/복원과 무출처 산출물 자동 변환은 서로 다른 대상이다.

조치: 개정 이력을 보존하고 인용 시 종전/현재를 함께 명시한다. NodeSet 저장 작업에 #443/#368/#685 전체를 선행으로 새로 추가하지 않는다.

## 조사 기록을 설계 충돌로 세지 않은 사례

- Code-Map 4모듈 문서는 `4c7608e` 등 명시된 커밋의 현재 동작/결함 진단이다. 입력·설정이 셀 위젯에만 존재하거나 write-only 키가 있다는 기록과, 새 목록의 왕복 복구 목표는 현재→목표 관계다.
- XML 출처 문서와 Builder/DeepOpt 문서는 서로 다른 10월 2일 커밋을 명시하고 root의 샘플 dict와 형제 model_info, parameterInfo가 없으면 메타데이터 생략, 학습 시작 시 JSON 전사라는 내용이 정합적이다. XML 형식을 바꾸는 작업에는 DeepOpt 첫 자식 판독 제약을 유지해야 하지만, 이 조사 기록 자체는 새 스키마 계약이 아니다.
- Ownership 문서의 마지막 Set 모델 소유안은 미확정 제안이며 앞부분의 현재 DashManager 소유 실측과 확정 충돌로 분류하지 않았다.
- #471 취소는 기준 deck 목록(referenceModels.json), 현재 Set 참조, #650 최신성 표시까지 없앤다는 뜻이 아니다. PRJ-02는 개명이며 생성/삭제 결함을 자동으로 덮지 않는다.

검토 범위·깊이는 `downstream_coverage.json`, 정확한 원문 발췌는 `downstream_findings.json`에 기록했다. Store 문서군 전체 파일을 대상에 포함했으나 구현 배선 전 행의 독립 검증은 하지 않았으며 관련 정책 절의 교차 검토다.
