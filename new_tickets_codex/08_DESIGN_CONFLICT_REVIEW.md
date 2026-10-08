# notes 설계 충돌·개정 미전파 검토 — 2026-10-08

> **2026-10-08 적용 상태 갱신:** 이 검토는 수정 전 충돌과 근거 인용을 보존한다. Codex 카탈로그·모듈 JSON·대응표·실행 순서의 출처/대장/Set 원장 관련 지적은 이번 개정에 반영했다. PRJ-03=#368 생산, PRJ-04=#685 소비이며 대장 3카드는 철회 기록으로 실행에서 제외한다. 아래 인용을 현재 구현 요구로 사용하지 않는다. 다른 문서의 적용 상태와 독립 리뷰 판단은 이 주석으로 변경하지 않는다.

**같은 문서들을 현재 작업 지시로 함께 읽으면 충돌하는 내용이 있다. 가장 큰 원인은 명시된 개정이 오래된 Manifest·작업 목록·대응표에 전파되지 않은 것이다.** 특히 오늘 개정 이력의 입력 참조·출처 정책은 10월5~7일 Claude/Codex 작업 정의와 다르다. 별도 Set 원장 요구는 더 오래된 9월21일 결정도 놓친 Codex 작성 오류다.

이번 결과는 문서 대조다. GitHub 이슈가 실제로 현재 어떤 내용인지, 최신 코드/PR의 구현이 어느 정책을 따르는지는 재조회·빌드·실행하지 않았다. `Issue-Revision-History.md`의 **개정 반영/기존 개정 수록**과 **추가 개정 계획(아직 미반영)**을 구분했다. 최신 날짜만 보고 모든 문장을 확정 설계로 취급하지 않았다.

## 지금 착수 기준에서 먼저 정렬할 내용

| 주제 | 남아 있는 옛 요구 | 문서상 현재 방향 / 필요한 처리 |
|---|---|---|
| 입력 참조·출처 | 조합 ID 생성과 최초 입력 영구핀, 다른 조합 차단 | 개별 setId로 입력 참조 변경 허용. 이미 생성된 산출물 출처는 선택 변경만으로 바꾸지 않고 재실행 성공 시 실제 출처와 함께 갱신 |
| 산출물 대장 | PRJ-05·IO-10·IO-11의 별도 생산/소비 이력 대장 | #471 취소. Set·산출물이 원본 기록을 보유하고 프로젝트가 조회·집계. 과거 이력 보존은 요구하지 않음 |
| Set 원장 | PRJ-04의 별도 Set 원장으로 정본 전환 | 기존 setId 발급/파일 영속/역조회 활용. 별도 원장 불도입은 9월21일 SI-2에도 이미 있음 |
| 작업 경계 | G9/PR530 전체를 하나의 이행·선행으로 취급 | #368은 Builder 산출 기록까지, 소비 측은 #685. #473 결과 조작·#369 NodeSet 저장은 독립. #650 최신성과도 분리 |
| 상태 기록 | 기록 책임 분리와 파일 분할을 같은 것으로 해석 | #444는 비용 확인 후 필요한 경우만 파일 분리. AL-05와 LCH-32가 서로 반대의 물리 분할 확정안이라고 단정하지 않음 |
| 핸들/모핑 | DashHandleData·VTP/기존 GizmoGroup을 수정하는 계획 | 최신 작업 문서의 상태기·entry 모델 및 삭제 예정 범위와 대조한 뒤 잔여만 남김. PR 현재 상태를 이번에 실증한 것은 아님 |

정책 근거: [Issue-Revision-History.md:9](../Issue-Revision-History.md), [Issue-Revision-History.md:21](../Issue-Revision-History.md), [Issue-Revision-History.md:61](../Issue-Revision-History.md), [Project-Manifest-Set-Identity-And-Decision-Revisions.md:29](../Project-Manifest-Set-Identity-And-Decision-Revisions.md).

**특히 어제의 `07_BOARD_OVERLAY.md`는 10월7일 기준으로 보존해야 한다.** 그 문서의 “#471 존폐 미결”, “#368 조합 스탬프 기능 유지”, 원장 요구를 현재 설계로 그대로 인용하면 안 된다. 오늘 검토에서 AL-05를 물리 파일 분할 확정으로 해석한 과장도 교정했다.

## 주요 정합성 지적

13개 후보를 기록했다. 모두 같은 무게의 확정 설계 오류는 아니다. 개정 미전파, 범위 승계 차이, 완료 조건의 모호성을 구분하며 실제 제품 정책의 채택 여부가 필요한 곳은 명시한다.

| ID | 영향 | 분류 | 내용 |
|---|---|---|---|
| [DS-01](#ds-01) | 높음 | 개정 미전파·문구 정합성 | 조합 ID·최초 입력 영구핀 폐기가 Manifest와 두 작업 목록에 미반영 |
| [DS-02](#ds-02) | 높음 | 개정 미전파·문구 정합성 | 산출물·소비 이력 대장 취소가 Codex 구현 카드와 보드 대응표에 미반영 |
| [DS-03](#ds-03) | 높음 | 개정 미전파·문구 정합성 | 별도 Set 원장 도입 카드가 setId 파일 정본 결정과 어긋남 |
| [DS-04](#ds-04) | 높음 | 개정 미전파·문구 정합성 | G9/PR530 전체를 선행으로 두는 작업 경계가 #368→#685 분리와 미동기화 |
| [EXDC-01](#exdc-01) | 중간 | 개정 미전파·문구 정합성 | Launcher 기록 책임 분리와 물리 파일 분할의 조건을 구분해야 한다 |
| [EXDC-03](#exdc-03) | 중간 | 개정 미전파·문구 정합성 | 결과 파일 append 기준에 옛 uuid/tableId·PR530 스탬프 전제가 남아 있다 |
| [GDC-01](#gdc-01) | 높음 | 개정 미전파·문구 정합성 | 구 핸들 데이터 추출·VTP 체크리스트를 새 값 모델 작업으로 그대로 실행할 수 없다 |
| [GDC-02](#gdc-02) | 중간 | 개정 미전파·문구 정합성 | GizmoGroup 삭제 계획과 VIS-007의 즉시 리팩터링이 함께 남아 있다 |
| [GDC-03](#gdc-03) | 중간 | 개정 미전파·문구 정합성 | Box FFD 신규 제공의 확정 요구가 Claude 목록에서 기능 필요성 재결정으로 바뀌었다 |
| [GDC-04](#gdc-04) | 중간 | 설계안의 적용 범위 불일치 | CAD temp .prt의 불개입 범위와 정규 CAD 재분류가 정렬되지 않았다 |
| [EXDC-02](#exdc-02) | 중간 | 개정 미전파·문구 정합성 | 취소 후 drainAll 즉시 반환 테스트의 적용 범위가 모호하다 |
| [DS-05](#ds-05) | 중간 | 개정 미전파·문구 정합성 | Load 단일 등록 규칙의 마스터 요약에 D15 예외가 누락 |
| [GDC-05](#gdc-05) | 낮음 | 개정 미전파·문구 정합성 | Optimizer Preview의 카메라 예외 설명을 구체 완료 기준에 맞게 좁힐 필요가 있다 |

<a id="ds-01"></a>
### DS-01 · 조합 ID·최초 입력 영구핀 폐기가 Manifest와 두 작업 목록에 미반영

10월 8일 개정은 parameterizationId와 최초 입력 영구 고정을 폐기했다. 현재 입력 Set 참조는 바꿀 수 있고, 이미 생성한 산출물의 출처는 입력 선택만으로 바뀌지 않으며 재실행 덮어쓰기 시 함께 갱신한다. Manifest의 조합 동일성 차단, Codex PRJ-03, Claude PER-06/07·홉별 작업을 그대로 적용하면 최신 동작과 반대가 된다. 이는 선택 대안 간 미결 충돌이 아니라 명시적 후속 개정의 미전파다.

- 영향: 기존 Set에서 다른 입력을 선택할 때 불필요한 새 Set 생성을 요구하고 폐기된 조합 키·산식·테스트를 다시 구현할 수 있다. DOE/Preprocess/Builder/Runner/Optimizer 전 경로와 그 의존 작업이 영향받는다.
- 제안: 최신 개정 링크와 적용일을 기존 마스터·작업 목록 머리에 붙이고 구 스탬프 작업을 개별 setId·실제 입력 선택·deck 출처 생산/검증 작업으로 재정의한다. 출처 없는 구산출물 재생성 요구는 유지한다. 버전·최신성은 #650 별도 계약이며 이 변경만으로 최신성 경고 작업을 삭제하지 않는다.
- 확신: 높음 (문서 비교의 확신이며 구현 검증이 아님)
- 근거:
  - [Issue-Revision-History.md:9](../Issue-Revision-History.md) — 최신 개정: \\| 2026-10-08 \\| #368 출처 기록과 공통 판독 계약 \\| 기존 개정 수록 \\| 조합 ID의 생성·전파·비교와 입력 고정 규칙을 포함하고, Runner·Optimizer 처리까지 함께 다룸 \\| \`parameterizationId\`와 최초 입력 영구 고정을 폐기. 개별 \`setId\`와 실제 입력 선택·deck 정보를 산출물에 기록. 현재 입력 참조와 생성 당시 출처를 분리 \\| 완료 지점을 Builder의 \`model\_info.json\` 생성으로 한정. 공통 기록·판독 계약을 제공하고 소비 측 T23은 #685로 이관. 버전·최신성은 #650에서 별도 설계 \\|
  - [Issue-Revision-History.md:21](../Issue-Revision-History.md) — 현재 참조/산출물 출처 규칙: #368·#685의 공통 정책은 기존 선택 UI에서 현재 Set이 참조하는 상류 입력 Set을 다른 \`setId\`의 Set으로 변경할 수 있게 하는 것이다. 현재 Set 자체의 \`setId\`는 유지하며, 입력 참조 변경만으로 산출물의 출처를 수정하지 않는다. 재실행으로 산출물을 덮어쓸 때에는 실제 사용한 입력 출처도 함께 갱신한다. 이전 산출물과 출처의 이력 보존은 요구하지 않는다. 별도로, 필수 출처가 없는 구버전 산출물은 재생성을 요구하며, 이름·경로 추론이나 자동 마이그레이션으로 출처를 채우지 않는다. 기존 Set ID 발급·복원은 유지한다.
  - [Project-Manifest-0-Work-Order.md:64](../Project-Manifest-0-Work-Order.md) — 이전 문서: \\| D18 (재개정) \\| 소유자 집합                       \\| \*\*파이프라인 8모듈 — Condition·Morphing(생성 시점 핀) · CAD(키 미도입 — #366 · D31 유보) · Launcher(\`referenceModel\` 대신 \`parameterization\` — DOE 선택 시 조합 기록) + Preprocessor·Builder·Runner·Optimizer(최초 연결 시점 핀).\*\* Analyzer·AIGeo 만 제외. ModelRunner 의 NodeSet 소스는 별도 키. 근거는 Project-Manifest-3-Module-Deck-Ownership "소유자" 절  \\| \\| D19 (개정)  \\| 파이프라인 불변식 보장                 \\| \*\*산출물 스탬프 + Set 핀 + 홉별 검증.\*\* 불변식은 단일 deck 이 아니라 \*\*…
  - [Project-Manifest-3-Module-Deck-Ownership.md:123](../Project-Manifest-3-Module-Deck-Ownership.md) — 이전 문서: - \*\*핀은 최초 연결 1회.\*\* 이후 다른 조합의 입력·연결·사용은 차단하고 "다른 조합이면 새 Set" 을 안내한다(D20) — D17 과 동형. "연결 시점 갱신" 개념은 없다.
  - [03_TASK_CATALOG.json:3250](03_TASK_CATALOG.json) — 이전 문서:       "Preprocess·Sim Builder·Sim Runner/Optimizer 최초 연결에서 조합 id를 pin하고 이후 다른 조합/무스탬프 구산출물을 이유·재실행 안내와 함께 차단한다.",
  - [FINAL.md:3326](../new_tickets_claude/05-final/FINAL.md) — 이전 문서: - 비고: #368 본체 = 이 항목(결정) + PER-07(공통부 PR). \*\*"스탬프 소비자 0" 해소 경로\*\*(검토 #3 · C-2 ⑤) — DOE-16 이 \`saveResultsAsDvTable\` 에서 Table 루트에 2키를 쓰고 같은 항목이 \`kSnapshotKeys\` 에 그 2키를 더한다 → Start 의 스냅샷이 스탬프를 운반한다 → PRE-32 가 스냅샷의 스탬프를 \*\*읽어\*\* 검증한다(\`derivedId\` 재계산 금지 — "T21~T23 은 T27 이 낸 id 를 읽기만 한다") → BLD-20 · RUN-34 · OPT-26 이 각 Set JSON 에 핀하고 불일치를 차단한다. allowlist 가 빠지면 스냅샷에 읽을 값이 없어 소비자가 0 으로 되돌아간다. 접점(홉별, 각 모듈 항목이 이 결정을 선행으로 참조): T27 → DOE-16(LCH-c35 · DOE-c31) ·…
  - [FINAL.md:3330](../new_tickets_claude/05-final/FINAL.md) — 이전 문서: - 목표: \*\*노선 = 재업로드(dev 리베이스 후 새 PR)\*\* — PR #530 은 머지하지 않는다(C-2 ②: base \`feat/reference-model-manifest\` 가 스쿼시(198a294c)돼 merge-base 가 dev 조상이 아니고, 같은 PR 의 T21/T27 이 구 파일명 \`DashDataProcessor\*\` 를 고친다). 이 항목은 #530 T27 커밋의 \*\*공통부만\*\* dev 기준으로 다시 올린다 — \`model/DashPipelineStamp.h\`(키 2종 + D20 차단 문구 2종) · \`DashParameterization::derivedId()\`(SI-5: geometry setId + 정렬 condition setId 연접 ",", 성분 setId 결손 시 빈 문자열) · \`tests/test\_doe\_selection.cpp\` 의 derivedId 케이스…
  - [07_BOARD_OVERLAY.md:82](07_BOARD_OVERLAY.md) — 이전 문서: 2. \*\*#368 PR 처리:\*\* 10월7일 조회에서 PR530은 병합 없이 CLOSED다. PRJ-03의 기능 목적은 연결되지만 \`in\_flight\`/기존 PR 통합 설명은 현재 계획으로 갱신해야 한다. 구현 재이식과 홉별 검증으로 읽는다.
  - [FINAL.md:1065](../new_tickets_claude/05-final/FINAL.md) — LCH-33의 Start 시 조합 불일치 차단 요구: #### LCH-33 · Start 가 핀과 다른 조합 id 의 DOE Table 로 실행을 시작하지 못하게 거절한다 - 종류: PR \\| 규모: S \\| 태그: C, A · bug - 목표: Start 가 \`runDoeAsync\` 를 부르기 전에 live DOE Table 의 \`parameterizationId\` 를 \`AnalysisLauncher\_\<Set\>.json\` 의 핀과 대조해 다르면 실행을 시작하지 않고 D20 문구로 거절한다. 핀이 없으면(첫 실행·구 프로젝트) 종전처럼 통과시킨다 — 핀 기록은 PRE-32 몫. 판정은 \`doeTableStaleReason\` 과 같은 \`std::optional\<QString\>\` 반환으로 모델에 두고, \`snapshotDoeTable\` 이 핀과 다른 Table 로 스냅샷을 덮어쓰는 경로가 없어진다. - 완료 기준: (1) 핀이 박힌 Set 에서 DOE…

<a id="ds-02"></a>
### DS-02 · 산출물·소비 이력 대장 취소가 Codex 구현 카드와 보드 대응표에 미반영

10월 8일 기록은 #471의 독립 대장을 취소하고 과거 산출물·출처 이력 보존도 요구하지 않는다. Codex PRJ-05/IO-10/IO-11의 대장 및 과거 소비 이력은 그 이전 요구다. Claude PER-11의 대장 제외 결론은 최신 방향과 맞지만 parameterizationId 핀을 스캔하면 역방향 소비를 복원한다는 근거는 폐기된 조합 계약을 사용하므로 별도 수정해야 한다.

- 영향: 이미 취소한 영구 이력 저장을 구축하거나, 어제의 미결 판정을 보고 대장 존폐 논의를 다시 열 수 있다. 현재 Set 참조/산출물 출처 조회와 과거 실행별 소비 이력은 동일 보장이 아니다.
- 제안: 대장 카드 3종은 최신 범위에서 제외/대체 대상으로 표시한다. 필요한 현재 관계 조회는 Set·산출물 원본 기록을 프로젝트가 조회·집계하는 API로 다시 적는다. PER-11은 현재 정책을 근거로 바꾸고 옛 핀 스캔 설명을 역사로 남긴다. 07_BOARD_OVERLAY는 10월 7일 스냅샷임을 유지하되 최신 정책 안내를 추가한다.
- 확신: 높음 (문서 비교의 확신이며 구현 검증이 아님)
- 근거:
  - [Issue-Revision-History.md:21](../Issue-Revision-History.md) — 최신 개정: #368·#685의 공통 정책은 기존 선택 UI에서 현재 Set이 참조하는 상류 입력 Set을 다른 \`setId\`의 Set으로 변경할 수 있게 하는 것이다. 현재 Set 자체의 \`setId\`는 유지하며, 입력 참조 변경만으로 산출물의 출처를 수정하지 않는다. 재실행으로 산출물을 덮어쓸 때에는 실제 사용한 입력 출처도 함께 갱신한다. 이전 산출물과 출처의 이력 보존은 요구하지 않는다. 별도로, 필수 출처가 없는 구버전 산출물은 재생성을 요구하며, 이름·경로 추론이나 자동 마이그레이션으로 출처를 채우지 않는다. 기존 Set ID 발급·복원은 유지한다.  이번 범위 정리는 #471의 독립 산출물·소비 이력 대장 취소 결정을 따른다. 출처 추적의 상위 목표는 #470에서 관리한다. 기존 이슈의 열린 상태와 종료 상태는 변경하지 않았다.
  - [Issue-Revision-History.md:61](../Issue-Revision-History.md) — 현재 책임/보장 범위: \\| 원본과 책임 \\| Set 설정은 현재 입력 참조, 산출물은 생성 당시 출처를 보유. 별도 산출물·소비 이력 대장은 취소. 프로젝트 객체가 Set·의존관계를 조회하고 개별 Set의 최신성 판정을 호출·집계하며, VM은 표시·동작 전달 담당 \\| 공유 판독 계약과 프로젝트 객체의 조회·집계 API. 개별 Set의 판정 책임을 유지하면서 연결할 방법 \\| \\| 식별의 의미 \\| \`setId\`는 Set, 항목 키는 개별 결과, 버전은 재생성 전후를 구분. 이름·번호·경로는 표시나 위치이며 이 세 역할을 대신하지 않음 \\| #474·#477의 최소 항목 키, #650의 버전 의미·비교 불가 상태, #643의 이어쓰기 기준 \\| \\| 입력 참조 변경과 재실행 \\| 조합 ID와 최초 입력 영구 고정을 폐기. DOE Sampler·Analysis Launcher·Model Builder·Model Run…
  - [03_TASK_CATALOG.json:3318](03_TASK_CATALOG.json) — 이전 문서:     "title": "실행과 산출물의 생성·소비 관계를 파일 대장에 기록한다",
  - [03_TASK_CATALOG.json:4607](03_TASK_CATALOG.json) — 이전 문서:       "재학습/모델삭제가 이전 실행 이력의 출처를 소급 변경하지 않게 한다."
  - [03_TASK_CATALOG.json:4645](03_TASK_CATALOG.json) — 이전 문서:       "이동/재실행/취소/삭제에서 과거 기록과 현재 파일 가용성을 분리한다."
  - [FINAL.md:3383](../new_tickets_claude/05-final/FINAL.md) — 이전 문서:   1. 닫기 사유 4가지 — ① 설계 문서 \`Project-Manifest-8-Run-Artifact-Ledger\` 는 2026-09-19 폐기(Publication-Plan 주11)이고 조회 UI #476·#445 는 범위 정리로 닫혔다 ② dev 에 대장 구현 0 (대장 파일·소비 기록 코드 없음) ③ 유래의 \*\*정방향\*\*은 이미 기록된다 — \`tableId\`(스냅샷 ↔ 케이스 상태 ↔ 하류 stale 판정: \`DashUpstreamStaleness.h\` 4곳 · \`DashAnalysisLauncherConfig\` 7곳 · \`DashLauncherRuns\` 5곳) + \`referenceModels.json\` 원장 ④ \*\*역방향\*\* 소비 기록은 하류 핀이 대신한다 — T21~T23 이 각 Set JSON 에 쓰는 \`parameterizationId\`(PRE-32 · BLD-20 · RUN-3…
  - [07_BOARD_OVERLAY.md:81](07_BOARD_OVERLAY.md) — 이전 문서: 1. \*\*#471 대장 존폐:\*\* Codex는 별도 생산·소비 대장을 구현하고 Claude PER-11은 불필요하다고 닫는 방향이다. 현재 연결의 추적과 과거 실행별 소비 이력 요구를 구분해 결정해야 한다. #650의 세대 경고까지 함께 제거할 근거는 아니다.
  - [Backlog-Issue-Publication-Plan.md:173](../Backlog-Issue-Publication-Plan.md) — 이전 설계 폐기 기록: 11. \*\*목록 UI 4분할\*\* — B7d(실행) · C2d(Set) · C3b(산출물) · C4c(항목) 이 전부 후행·신규다. 통합 후보. 설계는 문서 8(산출물 대장 · 폐기됨 2026-09-19) · 문서 6(Set Registry · 폐기됨 2026-09-19).

<a id="ds-03"></a>
### DS-03 · 별도 Set 원장 도입 카드가 setId 파일 정본 결정과 어긋남

별도 Set 원장 불도입은 2026-09-21 SI-2에서 이미 명시됐고 10월8일 #443 개정이 다시 확인한다. 따라서 Codex PRJ-04는 최신 변경으로만 낡은 것이 아니라 10월5일 작성 당시 기존 결정을 놓친 항목이다. 기존 발급·영속·역조회에 기반한 입력 참조 전환이 잔여 작업이다. referenceModels.json이라는 기준 deck 원장까지 폐기한다는 의미는 아니다.

- 영향: setId가 이미 있는 프로젝트에 두 번째 정본과 동기화/복구 경계를 추가하고, 기존 파일 정본 전략과 반대되는 구현을 시작할 수 있다.
- 제안: PRJ-04는 새 원장 생성 대신 #368→#685의 참조 전환으로 귀속을 다시 정한다. 생성·삭제의 파일 정리 요구가 있으면 별도 실제 결함으로 검증하며 rename 전용 PRJ-02를 생성/삭제 작업의 대체로 삼지 않는다. 원장이라는 단어를 기준 deck 목록, Set 정본, 산출물 이력으로 분리한다.
- 확신: 높음 (문서 비교의 확신이며 구현 검증이 아님)
- 근거:
  - [Project-Manifest-Set-Identity-And-Decision-Revisions.md:29](../Project-Manifest-Set-Identity-And-Decision-Revisions.md) — Set 정본 결정: \\| SI-2 \\| 저장 위치 \\| \*\*각 \`{Module}\_{Set}.json\` 의 \`setId\` 키가 정본.\*\* 별도 Set 원장은 두지 않는다 — Set 은 파일별 영속이 이미 있어 원장 근거가 없다. setId → Set 역조회는 열기 시 전 Set 스캔(\`restoreExistingModules\` 가 이미 전 파일을 읽는다 — 추가 비용 0). 열기 시 중복 감지(json 손 복제) → 나중 파일 재발급 + 로그 \\| \\| SI-3 \\| 발급·저장 시점 \\| \*\*신규 Set = 생성 핸들러\*\*(생성 시 json 이 어차피 써진다 — 추가 저장 규약 0). \*\*구버전 Set(키 부재) = 열기 복원 시 발급 + 즉시 write-back 1회.\*\* 쓰기 실패 = 로그 + 메모리 유지, 다음 열기 재발급. P5 와 무마찰 — P5 의 취지는 적재·해싱 지연이지 쓰기 금지가 아니다 \\|
  - [Issue-Revision-History.md:11](../Issue-Revision-History.md) — 최신 #443 범위: \\| 2026-10-08 \\| #443 Set 입력 참조 \\| 개정 반영 \\| UUID 발급·별도 원장 구축을 목표로 기록 파일 분할과 NodeSet 선택 저장까지 포함 \\| 완료된 #520의 \`setId\` 발급·영속·역조회를 기반으로 개명·동명 재생성에 안전한 입력 참조 전환에 집중 \\| 남은 구현은 #368 → #685. #444와 #369를 하위에서 분리. 별도 Set 원장, 폴더명 ID 전환, 최신성 판정을 완료 조건에서 제외 \\|
  - [03_TASK_CATALOG.json:3281](03_TASK_CATALOG.json) — 이전 문서:     "title": "Set 목록의 정본을 파일명 탐색에서 setId 원장으로 옮긴다",
  - [03_TASK_CATALOG.json:3285](03_TASK_CATALOG.json) — 이전 문서:       "프로젝트 Set 원장을 도입하고 생성/삭제/복원/개명이 같은 경계를 통과하게 한다",
  - [07_BOARD_OVERLAY.md:53](07_BOARD_OVERLAY.md) — 이전 문서: \\| 59 / #443 Set 식별·원장 \\| PRJ-04, PRJ-02; #444는 AL-05 관련 \\| 기존 setId 발급 재구현 금지. 원장 정책과 파일 분할 여부는 재판정 \\|
  - [07_BOARD_OVERLAY.md:83](07_BOARD_OVERLAY.md) — 이전 문서: 3. \*\*#443 Set 원장:\*\* setId 발급과 원장으로의 정본 전환은 다르다. Codex PRJ-04와 Claude의 설정 파일 기반 관리 전략은 동일하지 않다. 또한 Set 생성 시 고아 폴더 충돌·삭제 시 산출물 정리 요구는 PRJ-02의 개명으로 대체되지 않는다. 기존 카탈로그의 명시적 완료 조건 공백으로 남긴다.
  - [Project-Manifest-Set-Identity-And-Decision-Revisions.md:3](../Project-Manifest-Set-Identity-And-Decision-Revisions.md) — 9월21일 결정 검토의 정본 지위: \> 작업 묶음: 프로젝트 매니페스트 도입과 모듈 의존성 관리 \> 관련 Issue: #239 \> 소관: 2026-09-21 결정 검토의 처분 정본 — setId 신규 결정(SI-1\\~SI-6a)과 기존 결정 개정(D15 · D16 · D20 · D21 · D26 · D27 · D28 · T18)의 원문·사유를 갖는다. 2026-09-22 구현 리뷰(PR #530)의 D21 부속 철회도 이 문서가 갖는다. Project-Manifest-0-Work-Order · Project-Manifest-3-Module-Deck-Ownership · Project-Manifest-4-Ticket-Slicing 의 해당 항목은 이 문서를 참조로 개정한다 — 종전 판은 각 문서의 git 이력이 갖는다.

<a id="ds-04"></a>
### DS-04 · G9/PR530 전체를 선행으로 두는 작업 경계가 #368→#685 분리와 미동기화

Manifest의 산출물 폴더 식별과 이전 목록은 G9/PR530 전체 이행을 기준으로 묶여 있다. 최신 반영 기록에서 #368은 Builder model_info.json 생성까지, 소비 측은 #685이며 NodeSet 저장·결과 항목 조작은 독립이다. PR681의 머지 조건으로 #685를 두지 않는다는 것은 10행에 이미 수록됐지만, #368까지 제외한다는 #562 문구 정리는 36행의 아직 미반영 계획이다. 두 지위를 구분해 이전 일괄 선행 관계를 재검토해야 한다.

- 영향: 개명·행 조작·NodeSet 같은 독립 수정이 폐기된 일괄 스탬프 작업을 기다리거나 생산자/소비자가 공통 출처 형식을 중복 정의할 수 있다. #650 최신성 작업의 필요성은 유지되지만 조합 ID 전제의 의존 수치는 재사용할 수 없다.
- 제안: 현재 의존 그래프를 #368 생산/공통 판독 → #685 Builder 소비 경계로 재작성한다. #369/#473의 독립성을 유지하고 공유 파일 충돌은 선행 요구와 구분한다. 예전 PR530 상태와 10월 7일 결과는 역사로 보존한다. 최신 #643/#514/#615 세부 조율안은 아직 팀 논의 계획임을 함께 표시한다.
- 확신: 높음 (문서 비교의 확신이며 구현 검증이 아님)
- 근거:
  - [Issue-Revision-History.md:9](../Issue-Revision-History.md) — 확정 개정 범위/독립 작업: \\| 2026-10-08 \\| #368 출처 기록과 공통 판독 계약 \\| 기존 개정 수록 \\| 조합 ID의 생성·전파·비교와 입력 고정 규칙을 포함하고, Runner·Optimizer 처리까지 함께 다룸 \\| \`parameterizationId\`와 최초 입력 영구 고정을 폐기. 개별 \`setId\`와 실제 입력 선택·deck 정보를 산출물에 기록. 현재 입력 참조와 생성 당시 출처를 분리 \\| 완료 지점을 Builder의 \`model\_info.json\` 생성으로 한정. 공통 기록·판독 계약을 제공하고 소비 측 T23은 #685로 이관. 버전·최신성은 #650에서 별도 설계 \\| \\| 2026-10-08 \\| #685 Runner·Optimizer의 Builder 참조 전환 \\| 기존 개정 수록 \\| Runner·Optimizer의 입력 처리·deck 판독·프리뷰 변경이 #368의 T23 범위에 포…
  - [Issue-Revision-History.md:10](../Issue-Revision-History.md) — #681 조건 제외: \\| 2026-10-08 \\| #685 Runner·Optimizer의 Builder 참조 전환 \\| 기존 개정 수록 \\| Runner·Optimizer의 입력 처리·deck 판독·프리뷰 변경이 #368의 T23 범위에 포함 \\| Builder 산출물을 소비하는 경계부터 독립 작업으로 정리. Builder를 \`setId\`로 저장·복원하고 출처를 검증하며 실행·조회·프리뷰에 사용 \\| #368 선행, #443 하위 관계 유지. 생산 측 계약을 중복 정의하지 않음. 외부 실행에는 ID로 해석한 실제 경로 전달. #681의 머지 조건으로 두지 않음 \\|
  - [Project-Manifest-4-Ticket-Slicing.md:162](../Project-Manifest-4-Ticket-Slicing.md) — 이전 문서: \\| 범위 밖 \\| 산출물 폴더 식별(SI-6a — 폴더명 유지 · setId 색인 역조회) \\| 별개 이슈 덩어리(마스터 후속작업 14) — G9(#530) 머지 후, #443 하위 발행 \\|
  - [Project-Manifest-0-Work-Order.md:192](../Project-Manifest-0-Work-Order.md) — 이전 문서: \\| 14 \\| \*\*산출물 폴더 식별(SI-6a)\*\* — 폴더명 \`{Module}\_{Set}\` 유지, 변환 없음. 소비자는 setId 보유 + \`DashProject::m\_setIds\` 역조회로 현행 \`getModuleDir\` 조립. 성립 조건 셋 — \`renameSet\` 의 산출물 폴더 동반 개명 · Set 참조 보관 자리의 setId 전환(Runner \`modelBuilderFolder\` · Optimizer 폴더 콤보 · 폴더명 역파싱 3곳) · 삭제 시 폴더 동반 삭제 + 생성 시 동명 폴더 거부. 선행 G9(#530) 머지. 규모 실측은 SI-6a \\| Project-Manifest-Set-Identity-And-Decision-Revisions \\|
  - [03_TASK_CATALOG.json:3246](03_TASK_CATALOG.json) — 이전 문서:       "이 PR의 전체 소비자 이관을 하나의 진행 작업으로 추적한다"
  - [decisions.md:27](../new_tickets_claude/05-final/decisions.md) — 이전 문서: - 선행 치환 (9건): \`PR #530 머지\` → \`PER-07 · \<자기 모듈 홉 항목\>\`. BLD-13 · BLD-14 · BLD-15 · BLD-17 · BLD-18 · RUN-14 · RUN-25 · RUN-27 · RUN-31. \*\*BLD-13 은 역전\*\* — \`loadLabelMetadata\` 삭제 항목이라 BLD-20 이 BLD-13 뒤에 오고, #530 의 필터 hunk 는 드롭한다. - 충돌 치환 (89건, \`#530\`·\`pipeline-deck-stamp\`·\`#368 T2x\` 가 충돌란에 있는 항목): 자기 모듈 홉 항목 ID 로 바꾼다. 홉 항목이 없는 모듈(MOR CAD ANA PRJ REN UIC)은 그 파일을 고치는 홉 항목이 분명하면 그 ID, 아니면 삭제 — D-1 의 \`build\_deps.py --apply\` 가 파일 교집합으로 다시 채운다. - 열린 PR 목록:…
  - [07_BOARD_OVERLAY.md:82](07_BOARD_OVERLAY.md) — 이전 문서: 2. \*\*#368 PR 처리:\*\* 10월7일 조회에서 PR530은 병합 없이 CLOSED다. PRJ-03의 기능 목적은 연결되지만 \`in\_flight\`/기존 PR 통합 설명은 현재 계획으로 갱신해야 한다. 구현 재이식과 홉별 검증으로 읽는다.
  - [Issue-Revision-History.md:25](../Issue-Revision-History.md) — 추가 개정 계획은 아직 미반영: ## 추가 개정 계획 — 2026-10-08  프로젝트 16의 By week 뷰를 점검해 찾은 후속 개정 후보다. 아래는 \*\*팀 논의용 계획이며 GitHub에 아직 반영하지 않았다.\*\* 위의 개정 이력과 구분하며, 반영할 때에는 실제 변경 내용을 새 이력으로 남긴다.
  - [Issue-Revision-History.md:36](../Issue-Revision-History.md) — #368까지 포함한 #562 설명 갱신은 계획: \\| 우선 \\| #562 Set 개명 \\| #443을 원장 구축으로 설명하고 과거 G9 조합 스탬프를 선행으로 명시. 현재 PR #681이 재현되지 않는다고 정리한 항목도 남음 \\| 현재 개명 가능한 모듈과 실제 결함으로 범위를 갱신. 개명 오류 수정과 #685의 ID 참조 전환을 구분하고, #368·#685를 PR #681의 머지 조건으로 두지 않음 \\| PR #681의 현재 수정 범위와 이슈 완료 조건을 일치시킬 것. 경로 치환은 기존 구조의 오류 수정이며 최종 참조 체계는 ID라는 점 명시 \\|

<a id="exdc-01"></a>
### EXDC-01 · Launcher 기록 책임 분리와 물리 파일 분할의 조건을 구분해야 한다

10월8일 #444 반영 내용은 갱신 비용·기존 구조 개선을 확인하고 필요한 경우에만 파일을 나눈다는 것이다. Codex AL-05는 기록 계약을 분리한다고 쓰므로 물리 파일 분할을 확정했다고 단정할 수 없다. Claude LCH-32는 현 단계 무분리를 결론으로 두되 두 대안의 효과와 로드 실측에 따른 재검토 조건을 명시한다. 양극단의 확정 설계 충돌이라기보다 최신 조건부 결정을 공유하고 논리적 책임 분리와 물리적 파일 분할을 구별하도록 문구를 정렬할 사안이다.

- 영향: AL-05/06 착수 시 불필요한 새 파일·이행 작업을 만들거나 반대로 실측상 필요한 분리를 배제할 수 있다. 단일 writer·변경 행 갱신과 물리 저장 경계 선택은 같은 결정이 아니다.
- 제안: #444의 효과 검증→필요 시 파일 분리를 공통 조건으로 명시한다. AL-05는 기록 책임/행 갱신과 파일 수를 분리해 서술하고, LCH-32의 현재 결론과 재검토 조건을 보존한다. 어제 overlay에서 AL-05를 물리 분할 확정으로 읽은 표현도 후속 갱신에서 교정한다.
- 확신: 높음 (문서 비교의 확신이며 구현 검증이 아님)
- 근거:
  - [Issue-Revision-History.md:16](../Issue-Revision-History.md) — 개정 반영: 현재 #444/#441 범위와 관계: \\| 2026-10-08 \\| #444 Set 기록 분리 \\| 개정 반영 \\| #443 하위에서 변경 빈도별 파일 분할을 전제로 추진 \\| 상태 갱신 비용을 확인하고 기존 구조로 해결 가능한지 먼저 판단. 필요한 경우에만 파일 분리하고 저장·읽기·화면 갱신 개선을 검증 \\| GitHub 하위 관계를 #443에서 #441로 이동. Set ID 도입과 분리하며 모든 Set JSON의 일괄 분할을 요구하지 않음 \\| \\| 2026-10-08 \\| #441 상태 기록과 재시작 복구 \\| 개정 반영 \\| #444와 파일 분할 설계를 공유하는 연관 관계 \\| #444가 저장 경계를 정리하고 #441이 그 기록을 사용하는 증분 갱신·재시작 복구를 담당 \\| #438 하위 유지, #444를 하위에 편입. 저장 포맷 중복 설계를 피하고 상태 기록 개선 후 재시작 복구 순서로 진행 \\|
  - [03_TASK_CATALOG.json:1081](03_TASK_CATALOG.json) — Codex 실행 제안: 설정/상태 분리 계약:     "outcome": "N건 상태 변경이 Set JSON 전체 쓰기와 표 전량 재구성을 반복하지 않는다.",     "scope": \[       "설정·DOE snapshot과 빈번한 실행 상태를 분리하는 기록 계약을 공통 IO와 정한다.",       "러너/Executor의 상태 기록 책임을 정리하고 status·resultFiles·tableId를 한 케이스 전이로 저장한다.",       "watcher의 전량 갱신을 행 단위 갱신으로 전환하고 기존 파일을 읽는 이행을 포함한다."
  - [03_TASK_CATALOG.json:1111](03_TASK_CATALOG.json) — Codex 상태: ready:     "status": "ready",     "priority": "P2",     "notes": "공통 파일 원자화는 IO-01/IO-03의 범위. 여기서는 실행 기록 구조·소유권·UI 증분 반영을 담당한다.",
  - [FINAL.md:1055](../new_tickets_claude/05-final/FINAL.md) — Claude 제안: 무분리 결론을 미리 고정: #### LCH-32 · Set 기록 파일 분할 여부를 정한다 — 분할하지 않음 - 종류: DEC \\| 규모: S \\| 태그: A, C - 목표: #444 "Set 기록 파일을 변경 빈도 단위로 분할" 의 처분을 \*\*분할하지 않음\*\*으로 기록한다. 근거: 설정·DOE Table 스냅샷·\`Launcher Cases\` 는 \`tableId\` 로 묶여 한 파일에 있어야 stale 판정이 한 번에 읽히고, 쓰기 증폭(상태 1건당 전문 재기록)은 LCH-07 단일 라이터로 케이스당 1회로 줄고 표 전량 재구축은 LCH-08 이 억제한다. #444 의 다른 반쪽 "모듈 로드도 이 파일들을 통째로 읽는다" 는 로드 시간 실측이 없어 분할 사유가 되지 못한다 — 실측은 분할을 다시 꺼낼 때의 선행 조건으로 적는다. - 완료 기준: 결정 기록 — 분할 안 함 + 두 대안(LCH-07·LCH-08)이 덮는 범위 +…

<a id="exdc-03"></a>
### EXDC-03 · 결과 파일 append 기준에 옛 uuid/tableId·PR530 스탬프 전제가 남아 있다

Codex RES-12/13과 Claude PRE-29의 PR530/D26 조합 스탬프 전제는 10월8일 출처 계약과 정렬해야 한다. 그러나 referenceModel.uuid와 tableId 자체가 폐기된 것은 아니며, 불일치 자료를 덮어쓰거나 섞지 않는 보호 규칙은 새 정책과 양립할 수 있다. #643 이어쓰기 기준과 #411 소유권 정리는 아직 추가 개정 계획이고 구체 새 포맷은 미확정이다.

- 영향: 같은 Set ID를 유지한 입력 참조 교체·재생성이 허용되므로 예전 식별 키만으로 이어쓰기 가능성을 판정하면 다른 입력/버전 결과를 섞을 수 있다. 반대로 포맷 결정이 출처 전체 개편을 기다리는 과도한 선행이 될 수 있다.
- 제안: 출처 계약에서 폐기된 parameterizationId 전제만 갱신하고 deck uuid·DOE tableId의 실제 의미는 보존/재정의 여부를 따로 확인한다. #643에서 세 식별자 역할과 append 허용 조건을 결정하되 파일 포맷 선택을 출처 기록의 불필요한 하드 선행으로 만들지 않는다.
- 확신: 높음 (문서 비교의 확신이며 구현 검증이 아님)
- 근거:
  - [03_TASK_CATALOG.json:1880](03_TASK_CATALOG.json) — 옛 결과 병합 키 조건:       "1차 구현 전에 전체 재생성·원자 교체 또는 증분 추가 중 최소 정책을 확정하고, 다른 uuid/tableId 결과에 병합하지 않는 규칙을 포함한다.",       "USD 원본/내보내기 후보의 논리 구조를 검토하되 1차 구현에 HDF5/USD 채택을 강제하지 않는다."
  - [03_TASK_CATALOG.json:1910](03_TASK_CATALOG.json) — 옛 PR530 stamp 접점:     "notes": "현재 referenceModel.uuid/tableId로 1차 정책을 세울 수 있으므로 PR530 전체 통합은 하드선행이 아니다. PRJ-11의 산출물 세대 의미를 보존하고 PR530 stamp와 접점을 맞춘다. 외부 reader·multi-part·호환 정책은 구현 관문이며 PR 크기는 생산자/소비자 일관성 기준으로 유연하게 잡는다.",
  - [03_TASK_CATALOG.json:1923](03_TASK_CATALOG.json) — RES-13의 uuid/tableId 완료 조건:     "acceptance": \[       "XML 유지/HDF5 전환/USD 관계에 대한 근거 있는 결정과 조건부 후속 구현 범위가 남는다.",       "uuid/tableId 불일치가 잘못된 기존 결과에 이어쓰지 않는다."
  - [FINAL.md:1369](../new_tickets_claude/05-final/FINAL.md) — Claude 포맷 제안: uuid 및 확정된 #368 스탬프 전제: - 목표: #643 1차(Set 단위 파일 1개 + 응답 추가)·2차(uuid 확인 → 이어쓰기/덮어쓰기)·중복 1회 저장·HDF5(vtkHDF) 전환 여부를 결정한다. 결정 입력: \*\*DeepOpt 리더 계약 — \`root\` 의 첫 자식만 학습 데이터로 읽고 샘플 dict 는 동형이어야 한다(BLD-c26·BLD-14 비고 · 위키 Model-Builder-XML-DeepOpt-Pipeline)\*\*, Builder 다중 part 포맷(BLD), \`vtkIOHDF\` 가용(DEV), 저장 포맷 버전 키 A3/N9(\*\*PER-03 ⑦\*\* — 결과 XML 이 같은 규약을 쓰는지), \`DashXmlParser\` 전환(ANA), HDF5·중복 1회 판단에는 PRE-28 수치, 현행 포맷 기준선에는 \*\*PR #658\*\* (주파수 \`dict\_item\` 에 \`quantity\`·\`unit\` 속성 + Eigenv…
  - [Issue-Revision-History.md:9](../Issue-Revision-History.md) — 반영된 출처 계약 변경: \\| 2026-10-08 \\| #368 출처 기록과 공통 판독 계약 \\| 기존 개정 수록 \\| 조합 ID의 생성·전파·비교와 입력 고정 규칙을 포함하고, Runner·Optimizer 처리까지 함께 다룸 \\| \`parameterizationId\`와 최초 입력 영구 고정을 폐기. 개별 \`setId\`와 실제 입력 선택·deck 정보를 산출물에 기록. 현재 입력 참조와 생성 당시 출처를 분리 \\| 완료 지점을 Builder의 \`model\_info.json\` 생성으로 한정. 공통 기록·판독 계약을 제공하고 소비 측 T23은 #685로 이관. 버전·최신성은 #650에서 별도 설계 \\|
  - [Issue-Revision-History.md:25](../Issue-Revision-History.md) — 아래 항목들은 아직 팀 논의용 계획: ## 추가 개정 계획 — 2026-10-08  프로젝트 16의 By week 뷰를 점검해 찾은 후속 개정 후보다. 아래는 \*\*팀 논의용 계획이며 GitHub에 아직 반영하지 않았다.\*\* 위의 개정 이력과 구분하며, 반영할 때에는 실제 변경 내용을 새 이력으로 남긴다.
  - [Issue-Revision-History.md:35](../Issue-Revision-History.md) — #643 변경 예정: Set/deck/version 분리와 append 결정: \\| 우선 \\| #643 XML Set 단위화 \\| \`referenceModel.uuid\`와 DOE \`tableId\`를 “Set의 uuid”로 묶어 이어쓰기·덮어쓰기 기준으로 사용 \\| Set ID·deck 식별자·입력 버전을 구분. 출처 형식은 #368, 버전·최신성 규칙은 #650과 맞추고, 본 이슈는 저장 구조·중복 제거·포맷 검토에 집중 \\| 어떤 입력 변경에서 이어쓰기를 허용할지 결정. 포맷 전환과 출처 기록이 서로의 불필요한 선행이 되지 않도록 접점 정의 \\|
  - [Issue-Revision-History.md:41](../Issue-Revision-History.md) — #411 변경 예정: 판독 호환과 파이프라인 출처 적격성 구분: \\| 경계 보완 \\| #411 포맷 교체 검토 \\| 댓글에서는 #643의 2차로 이어받기로 했지만 본문은 독립 계획. 구 산출물 호환의 의미도 넓게 기술 \\| 포맷 검토의 담당을 #643과 정리. 구 포맷을 읽을 수 있는 것과 출처 없는 산출물을 파이프라인 입력으로 허용하는 것을 구분 \\| 독립 검토 티켓을 유지할지 #643에 흡수할지 결정. 기존 USD 검토 요청을 포함한 후보 비교는 해당 포맷 작업에서 다룸 \\|

<a id="gdc-01"></a>
### GDC-01 · 구 핸들 데이터 추출·VTP 체크리스트를 새 값 모델 작업으로 그대로 실행할 수 없다

Handle-Data-View-Separation은 66c126c 조사에 기반해 DashHandleData 신설과 VTP 읽기·쓰기 통합을 다음 작업으로 적는다. Codex GEO-001은 VTP 종료를 이미 반영했지만 GEO-002에는 m_handleGeometry를 캐시로 남기는 중간 설계가 남아 있다. Claude FINAL은 PR654/655 대상 구조에서 m_handleGeometry·import·sampled tree가 삭제되고 DashHandleDefinition + DisplacementPolicy가 정본을 대신한다고 기록한다. 데이터/뷰 분리라는 목적은 같지만 구현할 타입·저장형식·소비자 계약이 다르다.

- 영향: GEO-001/002와 구 문서 체크리스트를 병렬 구현하면 삭제될 VTP 로더·polydata 캐시를 다시 만들거나 PR655 구현을 중복한다. 저장 왕복 테스트도 종료된 VTP를 목표로 잘못 고정할 수 있다.
- 제안: 원 조사 자료는 역사 기록으로 보존하되 적용 종료 기준을 표시하고, 착수 문서에서는 PR654+655 대상 타입·DV 식별·JSON 계약을 먼저 정렬한다. 핸들 정본 이행과 MOR-23의 실제 잔여 조사만 남기고 구 VTP 통합·DashHandleData 신설은 실행 목록에서 대체로 처분한다. 이번 검토는 PR 병합이나 최신 코드 완성을 확인한 것이 아니다.
- 확신: 높음 (문서 비교의 확신이며 구현 검증이 아님)
- 근거:
  - [Handle-Data-View-Separation.md:3](../Handle-Data-View-Separation.md) — 구 조사 좌표/권위: \> \*\*성격\*\*: 독립 조사 문서. 열린 티켓을 참조하지 않고, 진행 중인 워커화 계획과 무관하게 이 분리 하나만 잰다. \> \*\*좌표 기준\*\*: \`feat/rw-actor\` @ \`66c126c\`. 아래 모든 행 번호는 이 커밋 실측이다.
  - [Handle-Data-View-Separation.md:418](../Handle-Data-View-Separation.md) — 구 실행 체크리스트: VTP/타입 신설: \\| ⓖ 고정점 상태 소유 통합 (원천 1벌 + 환산 2종을 데이터 타입으로) \\| 중 — 프리뷰 2경로가 소비. 층위 분해는 끝났다 \\| 같은 원천의 세 소유자 해소. 구속 원천을 직렬화에 올릴 자리가 생긴다 \\| 3 \\| \\| ⓒ-2 \`Finalize\`·\`UpdateSurfaceGeometry\` 분해 \\| 중 — 별건 설계 필요 \\| 데이터·뷰 분리의 실질 관문 \\| 3 \\| \\| 핸들 VTP 직렬화 7곳(읽기 5 · 쓰기 2)을 한 곳으로 \\| 중 — 4계층에 걸쳐 있다 \\| 배열 규약을 가장 강하게 아는 코드를 데이터 타입이 소유 \\| 3 \\| \\| \`DashHandleData\` 타입 신설 + 소유자 결정 + \`filterSelectedHandles\` 이관 + TODO 2곳 갱신 \\| ⓐⓑⓒ 선행 필요 \\| 워커 진입 규약이 시그니처로 강제됨 \\| 4 \\| \\| 최소 단위 테스트 3개 (…
  - [03_TASK_CATALOG.json:6](03_TASK_CATALOG.json) — Codex JSON 이행과 과도기 sampled tree:     "outcome": "핸들·마커·DV가 하나의 값 모델과 version 1 JSON으로 복원되고 모든 실행 소비자가 동일한 구성을 받는다.",     "scope": \[       "PR #654 구현을 최종 검토·통합한다: sample\_handles, Setup→Configuration, (entry 이름, control ID) DV, 반경 재구축, JSON archive 및 QC/DOE/Optimizer/Runner 연결.",       "기존 VTP·constraints\[\]·핸들 ID DV와 cylinder 경로의 종료를 명시하고 구 Set 열기 시 재작성 안내와 파일 무변경을 보장한다.",       "현재 PR에 포함된 SectionFrameHandles 변환 어댑터와 sampled tree를 함께 검증한다."
  - [03_TASK_CATALOG.json:50](03_TASK_CATALOG.json) — Codex 중간 소유 구조:     "title": "핸들 interaction이 값 모델의 투영만 편집하도록 소유권을 마무리한다",     "outcome": "기즈모·피킹·표시가 같은 Configuration/Setup에 반영되며 별도의 수정 가능한 polydata 정본이 남지 않는다.",     "scope": \[       "m\_handleGeometry를 projection 캐시로 내리고 mesh-ops set output\_port에 렌더를 연결한다.",       "피킹, 그룹/해제, 이름 변경, 범위·pose 편집을 값 모델 명령으로 연결하고 과도기 polydata→state 이중 동기화를 제거한다.",       "Set 전환·재진입 시 actor/observer를 현재 모델에 재연결하고 이전 모델 참조를 해제한다."
  - [FINAL.md:180](../new_tickets_claude/05-final/FINAL.md) — 새 대상 구조 및 잔여 조사 경계: #### MOR-15 · #430 닫기 — PR #655 가 interaction 의 핸들 소유를 해제했다 - 종류: CLOSE \\| 규모: S \\| 태그: E, C - 목표: 닫기 사유 기록. #430 의 "PR 2" 가 PR #655 다 — \`m\_handleGeometry\` 를 삭제하고 렌더를 set 의 \`handle\_output\_port()\`·\`control\_output\_port()\` 에 직접 붙이며(\`DashHandleEntryRenderer\`), \`DashHandleImport\`·\`DashSampledHandleTree\`·구 피킹 경로(약 1,900줄)와 \`.cpp:1409\` TODO 를 지운다. 원문의 VTP 읽기 5곳·쓰기 2곳 일원화는 PR #654 가 VTP 자체를 없애 소멸했고, \`DashHandleData\` 타입 신설은 \`DashHandleDefinition\` + \`Displ…

<a id="gdc-02"></a>
### GDC-02 · GizmoGroup 삭제 계획과 VIS-007의 즉시 리팩터링이 함께 남아 있다

Codex VIS-007은 GizmoGroup의 병렬 컨테이너를 멤버 상태로 옮기는 ready 작업이다. Claude MOR-09는 PR655가 클래스와 빌드 항목을 삭제하므로 병합 확인 후 닫고, 병합 실패 때에만 구 리팩터링을 되살리도록 한다. 이는 설계 취향 차이가 아니라 수정 대상 자체가 소멸하는 차이다.

- 영향: VIS-006 경로 이동 뒤 VIS-007을 별도 구현하면 삭제될 컨테이너에 불필요한 변경·테스트가 생긴다.
- 제안: VIS-007은 PR655 삭제 적용 여부를 확인하는 조건부 처분으로 바꾸는 것이 맞다. 삭제가 채택되면 구현 PR 없이 대체 완료로 기록하고, 삭제가 철회될 때만 원 작업을 복원한다. 여기서는 클래스가 최신 dev에서 실제 삭제됐다고 단정하지 않는다.
- 확신: 높음 (문서 비교의 확신이며 구현 검증이 아님)
- 근거:
  - [03_TASK_CATALOG.json:525](03_TASK_CATALOG.json) — 현 카탈로그의 구현 요구:     "id": "VIS-007",     "module": "공통 VTK / Gizmo 그룹",     "title": "체크 상태와 조작 플래그 백업을 각 Gizmo가 소유하도록 한다",     "outcome": "그룹 멤버 삭제·재선택으로 다른 기즈모의 활성 상태가 어긋나지 않는다.",     "scope": \[       "GizmoGroup의 \_active/\_savedState 인덱스 병렬 저장을 멤버 소유 checked/restore 상태로 옮긴다.",       "체크 중복 호출을 멱등으로 만들고 removeMember/그룹 파괴 시 원래 조작 플래그를 복원한다.",       "그룹은 멤버 집합과 집단 변환만 담당하도록 한다."
  - [03_TASK_CATALOG.json:548](03_TASK_CATALOG.json) — 즉시 착수 상태와 조율만 있는 선행:     "sources": \[       322     \],     "evidence": \[       "libs/DashGizmo/src/GizmoGroup.cpp:40 removeMember; :67 setChecked",       "libs/DashGizmo/include/GizmoGroup.h:\_members/\_active/\_savedState"     \],     "status": "ready",     "priority": "P2",     "notes": "VIS-006 이전/이후 어느 쪽도 구현 가능하나 경로 이동 먼저가 충돌이 적다. GEO-002와 같은 interaction 표면의 변경을 조율한다.",
  - [FINAL.md:120](../new_tickets_claude/05-final/FINAL.md) — 삭제로 대체, 병합 확인 조건: #### MOR-09 · #322 닫기 — PR #655 가 \`GizmoGroup\` 을 삭제해 정리할 컨테이너가 없어진다 - 종류: CLOSE \\| 규모: S \\| 태그: E - 목표: 닫기 사유 기록. \`\_members\`·\`\_active\`·\`\_savedState\` 병렬 컨테이너와 \`removeMember\` 리인덱싱·\`setChecked\` 재진입 오염은 PR #655 가 \`libs/DashGizmo/{include/GizmoGroup.h,src/GizmoGroup.cpp}\` 를 통째로 삭제하고 \`libs/DashGizmo/CMakeLists.txt\` 에서 \`src/GizmoGroup.cpp\` 를 빼면서 함께 사라진다. 핸들 기즈모는 \`DashHandleGizmoEditor\` 가 entry 단위로 만든다. PR 본문이 "Closes #322" 로 못박았다. - 완료 기준: 닫기 사유 — PR #6…

<a id="gdc-03"></a>
### GDC-03 · Box FFD 신규 제공의 확정 요구가 Claude 목록에서 기능 필요성 재결정으로 바뀌었다

보관된 #577의 2026-10-05 개정은 Cylinder 삭제와 Hexahedron BoxHandles FFD 신규 제공을 확정하고 PR3 완료 흐름까지 명시한다. Codex GEO-004도 이를 구현 작업으로 받는다. Claude MOR-05는 PR655의 구 UI 삭제를 근거로 신규 UI를 만들지 않을 선택과 #577 종료까지 다시 결정하게 한다. 구 shell 구현 삭제는 신규 FFD 요구 철회의 근거가 아니다. 다만 새 작업 목록 자체가 제안이므로 MOR-05는 원 요구의 승계를 바꾸려는 제안으로 해석할 수 있다. 이를 확정된 제품 정책 위반으로 판단하지 않으며, 최종 제품 결정은 재검증하지 않았다.

- 영향: 신규 FFD 제공이 이미 승인된 것으로 진행하는 목록과 제공 자체를 취소할 수 있는 목록이 병존한다. 일정·완료 판정이 달라진다.
- 제안: 후속 명시적 요구 철회가 확인되지 않으면 신규 제공 목표는 유지하고 lattice·분할 수·baseline 편집 등 세부 선택만 결정 대상으로 좁힌다. 실제 취소를 제안하려면 #577의 확정 요구를 변경하는 별도 제안으로 표시한다. 원격 최신 #577의 후속 개정 여부는 이번 문서 검토에서 확인하지 않았다. 새 목록에서 원 요구를 다시 결정하려는 사유와 그 변경 제안의 채택 여부를 명시하여, 이미 확정된 요구와 미채택 변경안을 구별한다.
- 확신: 높음 (문서 비교의 확신이며 구현 검증이 아님)
- 근거:
  - [577.md:5](sources/issues/577.md) — 명시된 개정 요구 스냅샷: ## 결정 (2026-10-05 개정) — 복원이 아니라 cylinder 삭제 · Hexahedron 신규  mesh-ops 핸들 모델 이행(#332 · #499) 설계에서 Volume 생성기 두 종을 다음과 같이 확정했다. 원래 본문(두 유형 모두 GUI 접근 복원)은 아래에 접어 둔다.  - \*\*Cylinder — 삭제.\*\* 메뉴에서 도달 불가능했던 경로이고 mesh-ops 에 대응하는 생성기가 없다. 설정 UI·생성·표시 코드를 통째로 지운다. PR 1(\`refactor/332-handle-state-integration\`)의 커밋 \`fb534dd\` 가 이 몫이며, \`grep -rni cylinder controller view viewmodel model\` 이 0 이다. - \*\*Hexahedron — 복원이 아니라 신규 기능.\*\* 기존 shell 박스 코드를 되살리지 않고 mesh-ops…
  - [03_TASK_CATALOG.json:130](03_TASK_CATALOG.json) — 신규 구현 완료 목표:     "id": "GEO-004",     "module": "Geometry Parameter / Volume handles",     "title": "Hexahedron을 BoxHandles FFD 생성·면 DV 흐름으로 제공한다",     "outcome": "Volume 메뉴에서 박스 생성부터 면 오프셋 DV, QC, 저장, DOE까지 실행할 수 있다.",     "scope": \[       "Hexahedron 메뉴·파라미터 UI를 BoxHandles FFD 생성에 연결한다.",       "면 드래그 릴리즈 1회에 set\_faces 절대 pose를 갱신하고 face DV 행·범위를 값 모델에 반영한다.",       "반경은 Set radius 정책을 따르고 dump/load 후 pose·범위를 복원한다."     \],     "acceptance": \[       "Volume…
  - [FINAL.md:80](../new_tickets_claude/05-final/FINAL.md) — 기능 필요성 자체를 다시 여는 DEC: #### MOR-05 · Box(FFD) 핸들 생성 UI 를 되살릴지 정한다 - 종류: DEC \\| 규모: S \\| 태그: E, D · feature - 목표: PR #655 가 GUI 의 shell 격자 box 생성 경로를 대체가 아니라 \*\*삭제\*\*했다 — \`onGenerateBoxHandles\`·\`setHandlesBoxhandle\`·\`applyGenerateHandlesAsBox\`·\`GenerateAndShowBoxHandles\`·\`m\_pendingBoxHandles\`·\`BoxHandleInfo\`·Hexahedron 설정 페이지(\`getHexaGridParams\`·\`generateHexaBoxHandlesRequested\`·.ui) 전부. Box 엔트리는 JSON 으로만 들어오고 baseline 편집은 미지원(\`transformed()\` 거부)이다. #577 은 "복원이 아니라 mesh-o…
  - [decisions.md:39](../new_tickets_claude/05-final/decisions.md) — PR655 삭제로 DEC 전환한 경위: ## ④ PR #655 (#430 · #322 Closes, #654 스택) — 전 모듈 미반영  - 사실: open\_prs.md 에는 있으나 claims·items·deps 어디에도 없었다 (MOR·OPT·REN 검토). 파일 71 · 겹침 항목 75 (MOR 17 · PRJ 20 · UIC 10 · CAD 6 · REN 5 · 기타). - 조치: \`items\_index.OPEN\_PRS\` 에 '655' 등록 완료 (선반영). D-1 \`build\_deps.py --apply\` 가 충돌란에 자동 기입하므로 C' 에서 수작업 치환은 불필요. 단 \*\*선행\*\*이 #655 여야 하는 항목은 C' 가 직접 고친다 — MOR-20 · MOR-17 · MOR-02/03/04 (#654 → #655), OPT-22 · OPT-20, UIC-07 · UIC-22 (#655 hunk 가 \`setupMorphingB…

<a id="gdc-04"></a>
### GDC-04 · CAD temp .prt의 불개입 범위와 정규 CAD 재분류가 정렬되지 않았다

Project-Manifest-CAD-Path-Disposition은 2026-09-18 제품 방침을 근거로 temp .prt 누적(D16)을 사장 경로로 격리해 불개입한다고 명시한다. Claude CAD-08은 같은 D16을 다음 Load 시 glob으로 지우는 PR로 정의하고, 376행에서 구 매니페스트가 사장 경로로 묶었지만 프리뷰는 정규 CAD 동선이라고 명시적으로 재분류한다. 따라서 구 방침을 모르고 누락한 것은 아니다. 다만 서로 다른 문서가 같은 D16의 적용 범위를 반대로 분류하며 어느 문서가 이 범위를 승계하는지는 정렬되지 않았다. decisions의 LCH-29는 wbpj 배치 정책이고 대화형 프리뷰 정리와 반드시 같은 범위는 아니다. 구 문서가 무조건 우선이라는 결론도 아니다.

- 영향: 구 매니페스트를 따르면 D16은 제외되고 CAD-08의 명시 재분류를 따르면 대화형 프리뷰 청소가 포함된다. 작업 목록 구성과 방침 적용 범위가 달라진다. 코드상 실제로 정규 프리뷰만 건드리는지는 이번 문서 검토에서 실증하지 않았다.
- 제안: CAD-08의 정규 프리뷰 재분류를 범위 승계 결정으로 채택하는지 확인하고, 채택한다면 매니페스트의 D16 적용 제외를 대체하는 근거·정리 대상 temp 경계를 연결한다. 배치 산출 .prt와 대화형 temp를 구분하여 CAD-08에 LCH-29 전체를 자동 선행으로 걸지 않는다. 구 방침을 무조건 우선하거나 새 목록의 재분류만으로 제품 결정이 확정됐다고 간주하지 않는다.
- 확신: 중간 (문서 비교의 확신이며 구현 검증이 아님)
- 근거:
  - [Project-Manifest-CAD-Path-Disposition.md:55](../Project-Manifest-CAD-Path-Disposition.md) — 명시적 적용 제외 정책: \*\*이 묶음에서 닫히는 것은 없다 — 전부 격리·유보다.\*\*  \\| \\| 항목 \\| \\|---\\|---\\| \\| 유보 — 후속작업 13 동반 \\| Set↔\`.prt\` 미저장(코드맵 D17 — \`cadSource\` 가 닫을 예정) · 원장 kind · \`.prt\` 등록(D29\\~D31) \\| \\| 사장 경로로 격리 — 불개입 \\| 재Load 보관본 삭제(코드맵 D15) · 표시명-파일명 겸업(D32 철회) · temp \`.prt\` 누적(코드맵 D16) · wbpj DOE 전체 \\| \\| 범위 밖 유지 \\| \`.prt\` 캐시 전역 1개(문서 5 B절) · \`.wbpj\`·\`.stli\` 원장 편입(후속작업 5) · 미래 경로 본 설계(후속작업 13 — 생성 deck 의 등록 지점과 P4 관계 · NSET 재부착) \\|
  - [Code-Map-User-Flow-Geometry-Parameterization-CAD.md:416](../Code-Map-User-Flow-Geometry-Parameterization-CAD.md) — 동일 D16 결함의 정적 근거: \\| \*\*D15\*\* \\| 진입·수명 \\| \`loadPrt\` 의 temp 정리가 승격해 둔 \`.prt\` 보관본을 지운다 \\| 4-2 · 5절 \\| \`\_cleanup\_temp(step\_path)\`(\`main.py:214\`·\`:330-338\`)의 대상이 \`{configs}/{prtBase}.prt\`(출력 STEP \`DashMainWindow.cpp:2273\` 과 같은 base)라 승격 복사본(위젯 \`:626-641\`)과 \*\*같은 경로\*\*다 → 승격 후 재로드하면 보관본이 사라진다. \`loadPrt\` 는 SaveAs 를 하지 않아 지울 자기 부산물이 없다 \\| \\| \*\*D16\*\* \\| 진입·수명 \\| 프리뷰 temp \`.prt\` 가 영구히 쌓인다 \\| 4-3 · 5절 \\| 상시 \`--no-cleanup\`(\`SolverNxCad:159\`)이 데몬 정리를 막고(\`main.py:274-275\`) 다음 \`lo…
  - [FINAL.md:366](../new_tickets_claude/05-final/FINAL.md) — 정규 CAD 동선으로 명시 재분류한 구현 요구: #### CAD-08 · 프리뷰 temp .prt 를 정리한다 - 종류: PR \\| 규모: S \\| 태그: A · bug - 목표: 프리뷰마다 데몬이 \`{temp}/{base}\_{upper\\|lower}\_preview\_{seq}.prt\` 를 남기고 어느 경로도 지우지 않는 누적을 끊는다. GUI 단독 해법 — \`enqueueLoadPrt\` 의 정리 글로빙에 \`\*\_lower\_preview\*.prt\`·\`\*\_upper\_preview\*.prt\` 를 더한다. - 완료 기준: 2 는 \*\*NX 불요\*\*(글로빙 패턴·대상 디렉터리 검토), 1 은 \*\*NX 게이트\*\*(프리뷰 실행 필요)   1. (NX 게이트) 프리뷰 N회 후 다음 \`.prt\` Load 시 temp 의 \`\*\_preview\_\*.prt\` 가 0개   2. DOE 배치 산출 \`{outputBaseDir}/{runKey}/{runKey}.prt\` 는 …
  - [decisions.md:5](../new_tickets_claude/05-final/decisions.md) — 재결정은 있으나 CAD-08 조건 누락: ## ① wbpj 배치 경로 사장 여부 — DEC 는 LCH 몫, \`LCH-29\` 신설  - 근거: 01-sources/wiki/Project-Manifest-CAD-Path-Disposition.md (09-18 "사장·불개입") vs #616 결정표 (10-02 "현행 유지") · PR #651/#652 가 wbpj 를 구현 — 시간순 모순. 입력 포맷 정책(#616)·Journal/Direct 실행 코드가 LCH 소유 (LCH 검토 #1). - 조치: LCH 가 \`LCH-29\` DEC 를 신설한다. 선행 등록 — CAD-01 Phase 3 · CAD-02 · CAD-05 · LCH-06 · LCH-27 (LCH-28 은 포맷 무관이라 제외). - 사장 결정 시 축소: LCH-06 은 Journal TU 삭제에 흡수, LCH-27 은 소멸(동결 시 LCH-19(a) 로 대체). CAD-01/…
  - [FINAL.md:378](../new_tickets_claude/05-final/FINAL.md) — 비교: 명시적으로 재결정한 D15/D17: #### CAD-09 · .prt 보관본 삭제와 Set↔.prt 결합 미저장의 처분을 결정한다 - 종류: DEC \\| 규모: S \\| 태그: A, C - 목표: Project-Manifest-CAD-Path-Disposition(2026-09-18 방침)이 D15(재Load 가 승격 보관본 삭제)·D17(Set 별 \`.prt\` 미저장)을 "후속작업 13(미래 CAD 경로) 동반 유보 · 사장 경로로 격리" 로 기록했다. 새 작업 목록이 그 결정을 승계할지, 아니면 최소 수선을 지금 할지 정한다. - 완료 기준: 결정 기록 — (a) 유보 승계: 후속작업 13 의 \`cadSource {uuid, path}\` 설계에 D15·D17 을 입력으로 넘기고 본 목록에선 항목 없음. \*\*(a) 를 고르면 추적 위치를 함께 지정해야 한다\*\* — 현재 03-items 전체에 후속작업 13(미래 CAD 경로 — …

<a id="exdc-02"></a>
### EXDC-02 · 취소 후 drainAll 즉시 반환 테스트의 적용 범위가 모호하다

EXE-02는 cancelAll 뒤 drainAll 즉시 반환 테스트와 비취소 SDK/prefetchXml 소비자를 함께 설명한다. 즉시 반환이 협조적인 테스트 fixture만을 뜻하면 양립 가능하다. 모든 실제 소비자의 수명 종료까지 무조건 즉시 반환한다는 뜻이면 한계 설명과 충돌한다. 현재 문구만으로 fixture 범위를 확정할 수 없어 실제 설계 모순으로 단정하지 않고 완료 조건의 범위 모호성으로 낮춰 기록한다.

- 영향: 종료 시간을 잘못 약속하거나 논리적 Cancelled만 보고 실제 worker 수명이 끝나기 전에 자원을 정리하는 구현으로 이어질 수 있다. 현재 실행 기반이 그런 동작이라는 주장은 아니다.
- 제안: 테스트 fixture의 취소 가능성과 허용 대기시간을 명시하고, UI 취소 표시·논리적 종결·실제 작업 수명 종료를 구분한다. 비취소 SDK 구간을 포함한 전체 drain 즉시 반환을 보장하지 않는다.
- 확신: 중간 (문서 비교의 확신이며 구현 검증이 아님)
- 근거:
  - [FINAL.md:3003](../new_tickets_claude/05-final/FINAL.md) — 같은 제안의 구현 방향·즉시 drain 검증·SDK 대기 한계: - 목표: \`QtConcurrent::run\` 을 \`QPromise\<DashJobResult\>&\` 오버로드로 바꾸고 \`Job::cancel()\` 을 오버라이드해 \`watcher\_.future().cancel()\` 로 잇는다. \`DashAsyncJobRunner::cancel(QUuid)\`·\`cancelAll()\` 을 공개하고 \`main.cpp\` 종료 경로를 \`cancelAll() → drainAll()\` 로 바꾼다. \`onWorkFinished\` 가 \`isCanceled()\` 를 먼저 보고 \`State::Cancelled\` 로 가게 해 빈 결과 읽기를 막는다. \`QPromise::setProgressValue\` 를 \`Job::progressed(int)\` 의 소스로 잇는다. - 완료 기준:   1. tests/TestAsyncJob.cpp 에 "cancel 중 작업은 Cancelled 로 끝나고…
  - [FINAL.md:3011](../new_tickets_claude/05-final/FINAL.md) — 첫 소비자 비취소 명시: - 흡수: #552 · #543(취소 표면의 전제) · EXE-c12, c13, c20(drainAll 부분) - 비고: 취소는 협조적이다 — 첫 소비자 \`DashDataLoader::prefetchXml\` 은 안 끊긴다. 이 사실을 PR 과 헤더 주석에 적지 않으면 "취소가 안 된다" 가 버그로 올라온다. 선점(도는 작업 취소 후 새 것 시작)은 범위 밖.
  - [215-2-sync-pumping-to-async-conversion-checklist.md:51](../215-2-sync-pumping-to-async-conversion-checklist.md) — 일반론: 취소 완료와 자원 반납을 구분해야 함: ### 5. 취소 완료의 정의 — 신호 발신인가 자원 반납인가  취소 요청이 곧 정지 보장은 아니다. kill 은 신호만 쏘고, 상태 기계가 그 자리에서 terminal 로 잠기면 "취소 완료" 와 "자원 반납 완료" 가 분리된다. 다음 실행의 가드는 이미 풀렸는데 파일은 아직 잡혀 있는 창이 생기므로, 취소의 완료 정의를 둘 중 무엇으로 둘지 정하고 후자라면 종료를 관측할 주체를 지정한다.

<a id="ds-05"></a>
### DS-05 · Load 단일 등록 규칙의 마스터 요약에 D15 예외가 누락

마스터 P4는 등록이 Load 버튼 한 곳의 명시 호출이라고 단정한다. 같은 설계의 개정 정본과 모듈 소유 문서는 구 Set의 DV source를 복원할 때 원장 등록 후 핀하도록 하는 유일한 예외를 명시한다. 예외는 정해졌으나 진입 문서의 규칙 요약에 전파되지 않았다.

- 영향: P4만 따라 구현하거나 리뷰하면 구 Set 복원에서 필요한 등록을 제거하거나 금지할 수 있다. 최신 출처 없는 산출물 자동 마이그레이션 금지와는 객체가 다르다.
- 제안: 마스터 P4에 D15의 한정 예외를 직접 연결한다. 이 항목은 기존 Set 설정의 referenceModel 복원에 관한 역사적 계약이며, #368의 구산출물 출처를 추정해 채우는 허용 근거로 사용하지 않는다.
- 확신: 높음 (문서 비교의 확신이며 구현 검증이 아님)
- 근거:
  - [Project-Manifest-0-Work-Order.md:38](../Project-Manifest-0-Work-Order.md) — 마스터 단일 등록 규칙: \\| P4 \\| 등록은 Load 버튼 핸들러 한 곳의 \`registerReferenceModel\` 명시 호출 — \`getOrLoad\` 는 자격을 판정하지 않는 순수 캐시 조회로 남는다. 원장에 \`role\` 분류 필드를 두지 않는 근거이기도 하다 \\|
  - [Project-Manifest-Set-Identity-And-Decision-Revisions.md:40](../Project-Manifest-Set-Identity-And-Decision-Revisions.md) — 명시 개정 예외: \\| D15 (재개정) \\| 키 부재 시 진입 1회 \*\*전역 reference\*\* 를 읽어 핀 + 다음 저장 backfill. multi-source json 은 핀 deck 밖 행을 읽기 전용 보존 \\| \*\*핀 출처 = Set 자신의 DV \`source\`\*\* — Condition 은 상대경로 그대로, Morphing 은 bare filename 을 configs 복사본 → 원장 \`path\` → 루트 스캔 순으로 해석. 복수 히트는 없다고 가정 — 결정적 1건(정렬 후 첫번째) + 로그. 유도분은 \*\*원장에 등록한 뒤\*\* 핀한다 — M3·P4 "등록 지점은 Load 핸들러 하나" 의 유일한 예외. 등록 없이는 다음 열기의 D16 해석이 미스라 backfill 이 자기 자신을 못 넘긴다. 등록 실패 시 핀하지 않고 다음 진입에 재시도. 유도 실패 시에만 전역 폴백, 빈 값이면 핀하지 않음(유지).…
  - [Project-Manifest-3-Module-Deck-Ownership.md:207](../Project-Manifest-3-Module-Deck-Ownership.md) — 예외의 구현 조건: \\| 원장 등록 \\| 유도분은 원장에 등록한 뒤 핀한다 — "등록 지점은 Load 핸들러 하나(M3·P4)" 의 유일한 예외. 등록 없이는 다음 열기의 D16 1단이 미스라 backfill 이 자기 자신을 못 넘긴다. 등록 실패 시 핀하지 않고 다음 진입에 재시도 \\|

<a id="gdc-05"></a>
### GDC-05 · Optimizer Preview의 카메라 예외 설명을 구체 완료 기준에 맞게 좁힐 필요가 있다

OPT-01은 기존 geometry가 있으면 카메라를 유지하는 비파괴 overlay이고 Codex VIS-001도 기존 문서·카메라를 보존한다. REN-01 비고는 Optimizer resetCamera를 사용자가 Preview 버튼을 누른 리셋이라 registry 작업 범위 밖이라고 설명하며 OPT-01 완료 기준 (3)을 인용한다. 이는 처리 소유를 OPT-01에 넘긴다는 뜻으로 양립 가능하다. 다만 (3)이 허용하는 빈 씬 리셋 예외를 비고가 생략하여 일반 리셋 허용으로 오독할 여지가 있다. 구체 완료 기준이 이미 답하므로 미결 정책 충돌은 아니다.

- 영향: 공통 렌더 작업에서 Preview 버튼 클릭을 카메라 리셋의 포괄 허가로 해석하거나, 일반 takeOver의 문서 숨김을 Optimizer overlay에도 적용할 수 있다.
- 제안: REN-01 비고를 “Optimizer는 OPT-01의 빈 씬 예외만 허용”으로 정렬한다. 일반 모듈 takeover/Runner의 문서 숨김과 Optimizer overlay를 별도 동작으로 유지한다. #316과 #318 자체가 정책 충돌이라는 결론은 아니다.
- 확신: 높음 (문서 비교의 확신이며 구현 검증이 아님)
- 근거:
  - [FINAL.md:2185](../new_tickets_claude/05-final/FINAL.md) — 비파괴 overlay의 확정 완료 조건: #### OPT-01 · Render Preview 를 비파괴 오버레이로 바꾼다 — 산출 .vtu 를 preview actor 로 겹치고 registry·BASE 레이어·카메라를 건드리지 않는다 - 종류: PR \\| 규모: M \\| 태그: A, E · bug - 목표: 프리뷰 격자를 \`performMorphing\` 이 쓴 \`Preview\_\*.vtu\` 에서 읽어 전용 preview actor(반투명) 로 기존 씬 위에 겹친다. \`removeAnalysisModelActor\`·\`GetActors()\` 전량 제거·\`clearLayer\` 3종·\`setDisplayedContext\`·\`updateAllGeometry\`·무조건 \`resetCamera\` 를 없앤다. 등록·해제는 \`DashRenderingManager\` 의 preview actor API 를 거치고, \`displayedContextChange…
  - [FINAL.md:2818](../new_tickets_claude/05-final/FINAL.md) — 같은 문서 내 잘못 넓어진 예외 설명: - 비고: #318 "공유 자원은 매니저 중재" 의 첫 적용이고, 기준값은 #319 완료 조건 "카메라 리셋이 사용자 조작 없이 일어나지 않는다" 다. 본 항목은 registry 한정 — 모듈이 스스로 부르는 \`resetCamera\` 2곳(\`DashOptimizerWidget.cpp:1814\` = OPT-01 완료 기준 (3) · \`DashModelRunnerWidget.cpp:1545\`)은 사용자가 Preview 를 눌러 시작한 리셋이라 범위 밖이고, 사용자 조작 없는 나머지 1곳 \`loadVtkFile\`(\`DashMainWindow.cpp:3905\`, Modeling Tree 재토글마다 리셋)은 REN-12 가 맡는다. \`tests/TestAnalysisModelContextRegistry.cpp\` 는 현재 \`updateActor\` 를 덮지 않는다(렌더 윈도우 의존).
  - [FINAL.md:2923](../new_tickets_claude/05-final/FINAL.md) — 일반 takeover의 문서 숨김 정책은 별도: - 목표: 지점 5곳의 \`clearLayer\`/\`clearAllLayers\` 를 매니저 API 로 교체한다. 기제가 둘이라 API 도 둘이다 — 섞으면 모듈 전환이 Load 모델을 숨겨 완료 기준 1 · #318 완료 조건 3 · REN-02 와 충돌한다(검토 #10).   - \`takeOver(owner)\` — \*\*그리기 시작\*\*: \`onStartMorphingClicked\` · \`performPreviewLogic\` · \`addMorphingPreviewActor\` · 매니저 update\* 내부(Launcher 시그널 3개는 호출부 무변경). 다른 소유자의 문서형은 \`SetVisibility(false)\`, 작업물형은 제거, ghost 복원, split view 해제.   - \`releaseWorkProducts(owner)\` / \`releaseDocument(path)\` — \*\*폐기\*\*: …
  - [03_TASK_CATALOG.json:292](03_TASK_CATALOG.json) — VIS-001 카메라/기존 actor 보존:     "outcome": "기존 문서·핸들·카메라를 그대로 보존하면서 Optimizer 프리뷰만 겹쳐 표시한다.",     "scope": \[       "renderer actor 전체 순회 삭제를 자기 프리뷰 actor 해제/교체로 바꾼다.",       "기존 FE 문서·핸들·피킹 actor의 visibility, registry 표시 커서와 카메라를 유지한다. overlay actor만 등록·해제한다.",       "프리뷰 반복·실패·모듈 이탈 시 소유 actor만 정리한다."     \],     "acceptance": \[       "기존 로드 모델·핸들이 계속 보이고 표시커서·카메라가 변하지 않으며 preview만 겹친다.",       "연속 프리뷰가 actor를 누적시키지 않고 실패가 기존 화면을 잃게 하지 않는다.",       "다음 Load와 요청 무효화에서 previe…

## 실제 충돌로 집계하지 않은 차이

미확정 대안을 나란히 검토하거나 역사적 설계를 보존하는 것은 자체로 오류가 아니다. 아래는 현행 확정 계약 충돌에서 제외했다.

| ID | 구분 | 판단 |
|---|---|---|
| DS-06 | 명시적 대안·추가 결정 | Store 8종은 Index와 각 문서가 미확정임을 명시한다. 실행 파일/대장 유무, 정의 해시와 산출 rev, 3루트 유지와 β 재배치, 구버전 승격과 거부, 난수 ID와 이름 기반 v5는 대안별 비용/보장이 다르다. 구상 안의 정본·확정이라는 내부 표현만 떼어 현재 제품 계약으로 간주할 수 없다. |
| DS-07 | 명시적 대안·추가 결정 | D14는 referenceModel 키 도입 시 버전 증가 없이 키 부재로 구형을 구분하는 결정이다. Claude PER-03은 이를 개정하거나 #480을 기각할 선택을 명시한 결정 작업이고, Codex IO-01은 기존 DashSaveSystem의 format/class version 오류 경계를 다룬다. 아직 같은 저장 파일에 반대 동작이 동시에 확정됐다는 근거는 없다. #650의 산출물 버전도 저장 스키마 버전과 별개다. |
| DS-08 | 역사·시점 차이 / 현재 충돌 제외 | Set-Identity 개정표의 종전/개정 양쪽을 현재 요구로 읽으면 NodeSet 외부 절대경로 저장과 프로젝트 내 복사, 무스탬프 라이브 폴백과 재생성 요구가 충돌해 보인다. 그러나 표는 명시적 이전 이력이다. 최신 #369는 기존 nodeSetSource 저장·경로 설계를 유지하고, #368은 필수 출처 없는 구산출물 재생성을 요구한다. |
| EXDC-04 | 명시적 대안·추가 결정 | Claude는 EXE-01의 단일 슬롯/자원별 슬롯 결정 뒤 모듈 펌핑 제거를 착수시키고 EXE-07 UI 규약도 EXE-01에 의존시킨다. Codex는 기존 실행 기반을 이용해 모듈 이관을 먼저 허용하고 ASY 공통층을 무조건 선행으로 두지 않는다. 215-2는 자원 충돌과 재요청 정책을 먼저 확인하라는 일반 원칙이지 중앙 레인 구현을 모든 경로에 강제하는 결정은 아니다. |
| EXDC-05 | 명시적 대안·추가 결정 | CAD 처분 문서는 매니페스트 작업 묶음에서 wbpj 경로를 사장 예정·불개입으로 격리한다. Codex AL-09/DIR-01은 특수포맷 및 Direct 운용 지원을 통합하고 Claude LCH-29는 이를 알고 유지/동결/제거 결정을 제안한다. 현재 지원과 매니페스트 개선 범위는 다를 수 있어, 문서만으로 wbpj 지원을 삭제해야 한다거나 제품 방침이 철회됐다고 확정할 수 없다. |
| EXDC-06 | 역사·시점 차이 / 현재 충돌 제외 | 194/205 계열은 즉시 Cancelled/UI 해방, 별도 직렬 풀·게이트, 종료 상한 초과 _Exit 등의 설계·구현 이력을 갖는다. 215-1과 운영 문서가 refactor/async-execution 미병합 폐기를 명시하므로 이 내용을 현 dev의 의무 규약이나 이미 완료된 기반으로 계산하면 안 된다. 상속된 일부 일반 원칙과 개별 후속은 별개다. |
| EXDC-07 | 역사·시점 차이 / 현재 충돌 제외 | Launcher/Preprocessor Code Map과 XML 생성 설명은 커밋 고정 조사이며 수정 계획이 아니다. 269는 기존 상태 배선을 보존하는 기계적 분해 단계이고 실패 terminal 개선을 후속으로 명시했다. 525의 live GUI 부트스트랩은 rc 임시안이며 dev 소유권 분리 뒤 제거하도록 처분을 명시했다. 이를 새 실행 카드와 동시에 적용할 영구 설계로 읽는 것은 부적절하다. |
| GDC-X01 | 명시적 대안·추가 결정 | rw-document-gate는 planned/현재 동작 아님을 머리글에 명시한 제안이다. 전용 QThread·양방향 DeepCopy·완전 비동기 메시지를 요구하지만 현 GUI actor를 설명하는 코드맵과 다른 단계다. Claude EXE-14는 Stage2 소유 모델을 실측 후 선택하고 Codex AST-003은 deferred 워커 이행을 구체 목표로 삼는다. 스레드 전략 선택 범위는 아직 조율해야 하지만 둘을 동시에 시행하라는 규칙으로 볼 수 없다. |
| GDC-X02 | 역사·시점 차이 / 현재 충돌 제외 | 281-1은 eaa77a6 좌표의 비교 문서이며 채택 결정은 이슈가 소유한다고 한다. 뒤의 #281 보관본은 #408 이후 WorkerJob·morphingSerialPool·MorphingGate를 재도입하지 않도록 명시적으로 개정했다. Claude MOR-18과 Codex GEO-007도 현 서비스 경계의 잔여와 검증으로 옮겼다. 비교 문서의 “A로 지금 착수”를 현행 요구로 되살리면 안 된다. |
| GDC-X03 | 명시적 대안·추가 결정 | 202 문서는 기존 폼의 Qt Designer 전면 재작성을 기각하고 코드 정리 우선·선별 .ui 도입을 후순위로 둔다. Claude UIC-08/09의 Windows nativeEvent 경로는 OS 창 이동/리사이즈 책임을 바꾸는 안이며 전체 UI를 .ui 또는 QML로 재작성하는 안이 아니다. Codex UI-01도 실기 확인 후 창 구조 교체를 선택하도록 한다. |
| ROOT-01 | 역사·시점 차이 / 현재 충돌 제외 | 197은 전면 QML 전환 비용을 지적하고 현재 Widgets 내 대체를 제안한다. 192도 같은 방향이며 뒤의 Presentation Model 명칭 확정이 더 정밀한 정의다. 서로 다른 아키텍처를 동시에 요구하는 충돌로 집계하지 않는다. |
| ROOT-02 | 명시적 대안·추가 결정 | 7월 문서는 CI를 선택·비차단으로 보류했고 Codex DEV-01은 CI 연결을 ready P2로 제안한다. 새 목록은 제안이며 CI를 모든 작업의 하드 선행으로 만들지 않아 둘을 동시에 불가능한 설계로 보지는 않는다. |
| ROOT-03 | 역사·시점 차이 / 현재 충돌 제외 | 색인/축 문서가 측정 시점과 배타/중복 집계 범위 차이를 직접 설명한다. 설계 충돌이나 누락 작업 수로 환산하지 않는다. |

대표적으로 Store α/β·정의 버전안·ID 발급안은 Index부터 미확정이다. 스키마 버전과 산출물 버전도 같은 개념이 아니다. 폐기된 W6/W10 설계, rc 임시 수선, 고정 커밋의 Code Map, 현재 구현 예시와 확장 구상이 섞인 drawio 도면도 구분해 읽었다.

## 문서 정리 권고

1. 현재 참조·출처·버전의 책임을 한 문서에서 선언하고, 이전 Manifest 결정에는 대체된 조항과 날짜를 표시한다. 기존 이력을 삭제하거나 완료 당시 구현을 소급 수정하지 않는다.
2. Codex PRJ-03/04/05·IO-10/11 및 Claude PER-06/07·홉별 스탬프 작업·LCH-33부터 오늘 정책에 대조한다. 상세 자동 재작성은 이번 검토 범위가 아니다.
3. 보존할 조사·제안·과거 설계에는 기준 커밋/날짜와 지위를 명시한다. “정본”도 조사 사실의 정본인지 현재 구현 계약의 정본인지 구분한다.
4. #643 append/덮어쓰기, #615 자동 선택, 버전 비교 규칙 등 추가 계획을 이미 확정된 요구처럼 선행 그래프에 넣지 않는다.
5. 하위 계약의 부분 겹침은 담당과 테스트 경계로 조율한다. 파일이 겹친다는 이유만으로 모든 결함 수정에 전체 구조 이행을 선행시키지 않는다.

## 검토 범위와 산출물

- 루트 Markdown68개를 목록화하고 문서별 머리말·개정·주제 구간을 검토했다. 읽기 깊이는 coverage에 구분했다. 전 문서의 모든 문장을 완독했다는 뜻은 아니다.
- drawio2개의 도형 레이블을 확인했다. PNG는 같은 도면의 중복 표현으로 별도 검증하지 않았다.
- Claude/Codex 최종 작업 정의와 관련 결정·대응표를 대조했다. sources/wiki 및 이슈 복제본은 독립 현행 설계로 중복 집계하지 않았다.
- 세 agent 분담 검토와 두 차례 교차검토를 거쳤다. 교차검토에서 확정 정책/미반영 계획, 논리 계약/물리 분할, 테스트 범위의 혼동을 보정했다.
- 원문 설계·기존 작업 정의·GitHub는 수정하지 않았다. 이 보고서와 조사 산출물만 추가했다.

[통합 지적 JSON](reviews/design_conflicts_2026-10-08/findings.json) · [문서별 검토 범위](reviews/design_conflicts_2026-10-08/coverage.json) · [검증 결과](reviews/design_conflicts_2026-10-08/validation.json) · [교차검토 1](reviews/design_conflicts_2026-10-08/cross_review_execution.md) · [교차검토 2](reviews/design_conflicts_2026-10-08/cross_review_downstream.md)
