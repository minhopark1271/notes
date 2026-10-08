# 실행·결과 처리 설계 문서 대조 — 2026-10-08

로컬 문서만 검토했다. 원문·코드·원격 상태를 변경하거나 실행 검증하지 않았다. 7건 중 현재 제안의 완료 조건 충돌 1건, 최신 개정에 맞춰야 할 드리프트 2건, 미결 계획 대안 2건, 현행 충돌에서 제외할 역사·단계 차이 2건이다. 코드가 실제로 결함을 가진다는 판정과 구분한다.

근거의 권위는 `Issue-Revision-History.md`의 개정 반영, 추가 개정 계획, 팀 논의 순서를 구분했다. 특히 #643/#411 새 포맷은 아직 결정 완료로 취급하지 않았다.

## EXDC-01 — Launcher 기록 분리의 양극단을 최신 조건부 결정으로 좁혀야 한다

- 분류: `document_drift` / 심각도: medium / 확신: 높음

10월 8일 반영된 #444는 갱신 비용과 기존 구조 개선을 먼저 확인하고 필요한 경우에만 파일을 분리한다. Codex AL-05의 분리 계약·ready와 Claude LCH-32의 분할하지 않음 확정은 둘 다 현재 착수 기준으로 그대로 재사용할 수 없다. 10월 5일 목록이 당시 제안이었다는 사실은 보존해야 한다.

근거:

- `Issue-Revision-History.md:16–17` — 개정 반영: 현재 #444/#441 범위와 관계
- `new_tickets_codex/03_TASK_CATALOG.json:1081–1085` — Codex 실행 제안: 설정/상태 분리 계약
- `new_tickets_codex/03_TASK_CATALOG.json:1111–1113` — Codex 상태: ready
- `new_tickets_claude/05-final/FINAL.md:1055–1060` — Claude 제안: 무분리 결론을 미리 고정

**영향:** AL-05/06 착수 시 불필요한 새 파일·이행 작업을 만들거나 반대로 실측상 필요한 분리를 배제할 수 있다. 단일 writer·변경 행 갱신과 물리 저장 경계 선택은 같은 결정이 아니다.

**제안:** 후속 실행 목록에서는 측정→기존 파일 내 단일 writer/행 갱신→필요 시 분리의 관문을 명시한다. #444가 저장 경계, #441이 그 기록을 이용하는 갱신·복구를 소유하게 하고 옛 목록에는 최신 결정 링크만 둔다.

## EXDC-02 — 협조적 취소 카드가 drainAll 즉시 반환을 무조건 완료 조건으로 쓴다

- 분류: `active_conflict` / 심각도: medium / 확신: 중간

Claude EXE-02는 cancelAll 뒤 drainAll이 즉시 돌아오는 테스트를 요구하면서 같은 카드에서 첫 소비자 prefetchXml은 끊을 수 없고 SDK 내부 파싱은 협조 지점까지 기다린다고 명시한다. 작업과 캡처 수명이 끝나는 drain을 뜻한다면 두 요구를 일반적으로 동시에 보장할 수 없다. 현 코드 결함 확정이 아니라 카드 완료 조건의 범위 충돌이다.

근거:

- `new_tickets_claude/05-final/FINAL.md:3003–3007` — 같은 제안의 구현 방향·즉시 drain 검증·SDK 대기 한계
- `new_tickets_claude/05-final/FINAL.md:3011–3012` — 첫 소비자 비취소 명시
- `215-2-sync-pumping-to-async-conversion-checklist.md:51–53` — 일반론: 취소 완료와 자원 반납을 구분해야 함

**영향:** 종료 시간을 잘못 약속하거나 논리적 Cancelled만 보고 실제 worker 수명이 끝나기 전에 자원을 정리하는 구현으로 이어질 수 있다. 현재 실행 기반이 그런 동작이라는 주장은 아니다.

**제안:** 취소 요청 즉시성, 논리적 terminal, 실제 worker 반환/자원 회수 완료를 별도 조건으로 쓴다. 즉시 drain 테스트는 미실행·이미 종료된 작업에 한정하거나 협조 체크포인트에 도달한 fixture로 제한하고, 비협조 SDK 실행 중에는 완료 대기/종료 예산을 명시한다.

## EXDC-03 — 결과 파일 append 기준에 옛 uuid/tableId·PR530 스탬프 전제가 남아 있다

- 분류: `document_drift` / 심각도: medium / 확신: 높음

Codex RES-12/13은 referenceModel.uuid/tableId 및 PR530 stamp 접점을, Claude PRE-29는 기존 #368의 스탬프 두 키 확정을 포맷 결정의 전제로 둔다. 최신 반영 이력은 조합 ID/영구 핀을 폐기하고 출처와 버전을 분리했다. 다만 #643의 새 append 판정·#411 소유권 정리는 아직 추가 개정 계획이며 구체 새 포맷이 확정된 것은 아니다.

근거:

- `new_tickets_codex/03_TASK_CATALOG.json:1880–1881` — 옛 결과 병합 키 조건
- `new_tickets_codex/03_TASK_CATALOG.json:1910–1910` — 옛 PR530 stamp 접점
- `new_tickets_codex/03_TASK_CATALOG.json:1923–1925` — RES-13의 uuid/tableId 완료 조건
- `new_tickets_claude/05-final/FINAL.md:1369–1375` — Claude 포맷 제안: uuid 및 확정된 #368 스탬프 전제
- `Issue-Revision-History.md:9–9` — 반영된 출처 계약 변경
- `Issue-Revision-History.md:25–27` — 아래 항목들은 아직 팀 논의용 계획
- `Issue-Revision-History.md:35–35` — #643 변경 예정: Set/deck/version 분리와 append 결정
- `Issue-Revision-History.md:41–41` — #411 변경 예정: 판독 호환과 파이프라인 출처 적격성 구분

**영향:** 같은 Set ID를 유지한 입력 참조 교체·재생성이 허용되므로 예전 식별 키만으로 이어쓰기 가능성을 판정하면 다른 입력/버전 결과를 섞을 수 있다. 반대로 포맷 결정이 출처 전체 개편을 기다리는 과도한 선행이 될 수 있다.

**제안:** Set 묶음 키, 실제 입력 출처, 생성 버전, append 허용 조건을 별도 항목으로 정의한다. 새 출처 기록은 포맷과 무관하게 연결하고 #643/#411의 담당·기존 파일 판독 범위는 미결 관문으로 남긴다. 식별 계약 자체의 최종 개정은 downstream 검토와 통합한다.

## EXDC-04 — 레인·취소·UI 규약의 필수 선행 범위는 두 목록의 계획 대안이다

- 분류: `proposal_alternative` / 심각도: medium / 확신: 높음

Claude는 EXE-01의 단일 슬롯/자원별 슬롯 결정 뒤 모듈 펌핑 제거를 착수시키고 EXE-07 UI 규약도 EXE-01에 의존시킨다. Codex는 기존 실행 기반을 이용해 모듈 이관을 먼저 허용하고 ASY 공통층을 무조건 선행으로 두지 않는다. 215-2는 자원 충돌과 재요청 정책을 먼저 확인하라는 일반 원칙이지 중앙 레인 구현을 모든 경로에 강제하는 결정은 아니다.

근거:

- `new_tickets_claude/05-final/FINAL.md:2987–2987` — Claude 착수 순서 전체 문장
- `new_tickets_claude/05-final/FINAL.md:2993–2999` — 명시적으로 열려 있는 단일 슬롯/자원별 슬롯 선택
- `new_tickets_claude/05-final/FINAL.md:3067–3073` — UI 결정 범위·EXE-01 선행
- `new_tickets_codex/03_TASK_CATALOG.json:3779–3779` — Codex 무조건 선행 배제
- `215-2-sync-pumping-to-async-conversion-checklist.md:39–45` — 경로별 재요청·실제 자원 충돌 원칙
- `215-2-sync-pumping-to-async-conversion-checklist.md:71–73` — 대기를 선택할 때만 생기는 큐 정책

**영향:** 의존성 그래프를 그대로 합치면 작은 입력 차단/종료 복구와 독립 스캔까지 전체 스케줄러 결정에 묶인다. 반대로 자원 공유 검증 없이 독립 이관을 허용하면 동시성 안전성을 놓칠 수 있다.

**제안:** 모듈마다 현재 슬롯으로 안전한지·공유 reader/session/경로가 있는지 한 줄로 확인한 뒤, 필요한 계약만 하드 선행으로 둔다. 레인 확장·큐 정책·표시 규약은 선택적 결정으로 구분한다. 실제 자원 소유권 검증 자체는 생략하지 않는다.

## EXDC-05 — wbpj 불개입의 적용 범위와 현재 지원 유지 여부는 재결정 경계다

- 분류: `proposal_alternative` / 심각도: medium / 확신: 높음

CAD 처분 문서는 매니페스트 작업 묶음에서 wbpj 경로를 사장 예정·불개입으로 격리한다. Codex AL-09/DIR-01은 특수포맷 및 Direct 운용 지원을 통합하고 Claude LCH-29는 이를 알고 유지/동결/제거 결정을 제안한다. 현재 지원과 매니페스트 개선 범위는 다를 수 있어, 문서만으로 wbpj 지원을 삭제해야 한다거나 제품 방침이 철회됐다고 확정할 수 없다.

근거:

- `Project-Manifest-CAD-Path-Disposition.md:3–4` — 불개입 결정의 작업 묶음 범위
- `Project-Manifest-CAD-Path-Disposition.md:24–26` — 사장 예정 제품 방향
- `Project-Manifest-CAD-Path-Disposition.md:40–40` — 이 묶음은 CAD에 손대지 않는다는 한정
- `new_tickets_claude/05-final/FINAL.md:1025–1029` — 유지/동결/제거가 아직 DEC인 후속 제안
- `new_tickets_codex/03_TASK_CATALOG.json:1226–1234` — Codex 현재 지원을 통합하는 제안의 범위

**영향:** LCH-29를 이미 승인된 삭제 작업으로 읽으면 지원 포맷을 불필요하게 걷어낼 수 있다. 반대로 운영 지원 PR만으로 형상 출처·매니페스트 일반화까지 승인됐다고 보면 범위가 팽창한다.

**제안:** 운영 지원/결함 수정, 매니페스트 편입, 장기 경로 폐기의 세 범위를 구분하고 LCH-29의 권위 선택을 기록한다. .stli는 별도 포맷이므로 wbpj 처분의 자동 결과로 묶지 않는다. 구체 CAD temp 파일 불개입 충돌은 geometry 담당 지적으로 통합한다.

## EXDC-06 — 폐기된 W6/W10의 풀·게이트·즉시취소·강제종료는 현행 충돌에서 제외한다

- 분류: `historical_resolved` / 심각도: low / 확신: 높음

194/205 계열은 즉시 Cancelled/UI 해방, 별도 직렬 풀·게이트, 종료 상한 초과 _Exit 등의 설계·구현 이력을 갖는다. 215-1과 운영 문서가 refactor/async-execution 미병합 폐기를 명시하므로 이 내용을 현 dev의 의무 규약이나 이미 완료된 기반으로 계산하면 안 된다. 상속된 일부 일반 원칙과 개별 후속은 별개다.

근거:

- `194-1-async-execution-patterns.md:188–191` — 당시 취소 정책 P1~P4
- `205-2-w6-w10-change-log-and-remaining-design.md:9–9` — 구현 기록의 브랜치 기준
- `205-2-w6-w10-change-log-and-remaining-design.md:830–834` — 당시 취소 두 축·_Exit 정책
- `215-1-w10-f-design-decision-review-snapshot.md:6–8` — 명시된 폐기 및 스냅샷 지위
- `Project-Board-Intake-And-Operations.md:11–11` — 14건 폐기와 미병합 기준
- `269-1-jobrunner-case-decomposition-design.md:63–63` — 후속 #269도 dev에 장부 선례가 없음을 반영

**영향:** 옛 문서를 현재 정책으로 적용하면 이미 폐기한 WorkerJob/MorphingGate/BatchLedger 체계를 재도입하거나 worker 완료 검증을 잘못 생략하게 된다.

**제안:** 옛 문서는 보존하고 읽기 안내에서 폐기/승계 경계를 표시한다. 새 취소·종료 정책은 현재 DashAsyncJobContext/MorphingService 기준으로 별도 결정한다. 이 지적은 새로운 worker/게이트 구현 요구가 아니다.

## EXDC-07 — 고정시점 코드맵·기계적 분해·rc 임시 복구는 단계 차이로 제외한다

- 분류: `historical_resolved` / 심각도: low / 확신: 높음

Launcher/Preprocessor Code Map과 XML 생성 설명은 커밋 고정 조사이며 수정 계획이 아니다. 269는 기존 상태 배선을 보존하는 기계적 분해 단계이고 실패 terminal 개선을 후속으로 명시했다. 525의 live GUI 부트스트랩은 rc 임시안이며 dev 소유권 분리 뒤 제거하도록 처분을 명시했다. 이를 새 실행 카드와 동시에 적용할 영구 설계로 읽는 것은 부적절하다.

근거:

- `Code-Map-User-Flow-Analysis-Launcher.md:5–6` — 독립 참조·고정 커밋·실행 미검증
- `Code-Map-User-Flow-Data-Preprocessor.md:3–5` — 정적 대응표·고정 커밋
- `Preprocessor-XML-Generation-And-Provenance.md:5–7` — XML 설명의 고정 커밋·조사 지위
- `269-1-jobrunner-case-decomposition-design.md:10–12` — 기계적 분해와 기준 시점
- `269-1-jobrunner-case-decomposition-design.md:44–44` — 상태 신호 누락은 후속이라는 명시
- `525-1-rc-hotfix-plan-and-dev-root-fix.md:55–62` — rc 조각과 dev 근본 해소의 backmerge 처분

**영향:** 고정시점의 Direct Set, XML 요청별 파일, 과거 미연결 상태를 현재 지시로 오인하면 완료 작업 재생성 또는 올바른 후속 수선의 기각으로 이어진다.

**제안:** 후속 카드의 변경 이유로만 참조하고 현재 구현 확정 근거로 쓰지 않는다. 스냅샷 본문을 소급 수정하지 말고 필요하면 최신 코드/작업 문서 링크를 머리말에 추가한다.

## 추가 제외 사례

- 재실행 실패 시 마지막 성공 결과를 보존하는 AL-07은 이전 산출물을 영구 이력으로 관리하는 요구가 아니다. 최신 개정의 “이력 보존 불요”와 양립하며 교체 시점만 #646에서 정하면 된다.
- #264의 실행 중 케이스/스테이지 장부와 폐기된 #471 산출물·소비 이력 대장은 같은 대상이 아니다.
- 199의 JSON-RPC는 개선 예제, 193/203 Q&A는 교육 자료다. 예시 코드의 존재만으로 현재 구현 의무를 만들지 않는다.
- RW 전용 actor 스레드 대안은 EXE-14 계측·결정과 EXE-22 조건부 구현에 남아 있다. 현재 GUI 소유권과 충돌하는 확정 지시로 세지 않았다.

검토 커버리지 23개는 `execution_coverage.json`에 깊이와 한계를 기록했다.
