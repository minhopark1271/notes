# Geometry 설계 충돌 점검 — 2026-10-08

문서 대조 결과: **활성 충돌 1건, 문서 드리프트 4건**, 대안/역사로 제외한 사례 3건. 범위는 담당 notes 원문과 기존 Claude/Codex 최종 목록이다. 코드·원격·실행 결과를 새로 검증하지 않았으며, PR 설명과 완료 제안을 실제 병합/검증 완료로 간주하지 않았다. 원문과 작업 정본은 변경하지 않았다.

검토 우선순위는 핸들 이행 대상 정렬(GDC-01), 삭제될 GizmoGroup 작업 처분(GDC-02), FFD 요구 확정 상태 보존(GDC-03), CAD 불개입 범위 정리(GDC-04), 낮은 우선순위의 카메라 예외 설명 보완(GDC-05)이다. 계획/제안 지위가 명시된 RW·창 구조 설계는 별도로 두었다.

## GDC-01 · 구 핸들 데이터 추출·VTP 체크리스트를 새 값 모델 작업으로 그대로 실행할 수 없다

**document_drift · high · 확신 높음**

Handle-Data-View-Separation은 66c126c 조사에 기반해 DashHandleData 신설과 VTP 읽기·쓰기 통합을 다음 작업으로 적는다. Codex GEO-001은 VTP 종료를 이미 반영했지만 GEO-002에는 m_handleGeometry를 캐시로 남기는 중간 설계가 남아 있다. Claude FINAL은 PR654/655 대상 구조에서 m_handleGeometry·import·sampled tree가 삭제되고 DashHandleDefinition + DisplacementPolicy가 정본을 대신한다고 기록한다. 데이터/뷰 분리라는 목적은 같지만 구현할 타입·저장형식·소비자 계약이 다르다.

영향: GEO-001/002와 구 문서 체크리스트를 병렬 구현하면 삭제될 VTP 로더·polydata 캐시를 다시 만들거나 PR655 구현을 중복한다. 저장 왕복 테스트도 종료된 VTP를 목표로 잘못 고정할 수 있다.

권고: 원 조사 자료는 역사 기록으로 보존하되 적용 종료 기준을 표시하고, 착수 문서에서는 PR654+655 대상 타입·DV 식별·JSON 계약을 먼저 정렬한다. 핸들 정본 이행과 MOR-23의 실제 잔여 조사만 남기고 구 VTP 통합·DashHandleData 신설은 실행 목록에서 대체로 처분한다. 이번 검토는 PR 병합이나 최신 코드 완성을 확인한 것이 아니다.

근거:

- `Handle-Data-View-Separation.md:3–4` — 구 조사 좌표/권위
- `Handle-Data-View-Separation.md:418–422` — 구 실행 체크리스트: VTP/타입 신설
- `new_tickets_codex/03_TASK_CATALOG.json:6–10` — Codex JSON 이행과 과도기 sampled tree
- `new_tickets_codex/03_TASK_CATALOG.json:50–55` — Codex 중간 소유 구조
- `new_tickets_claude/05-final/FINAL.md:180–188` — 새 대상 구조 및 잔여 조사 경계

## GDC-02 · GizmoGroup 삭제 계획과 VIS-007의 즉시 리팩터링이 함께 남아 있다

**document_drift · medium · 확신 높음**

Codex VIS-007은 GizmoGroup의 병렬 컨테이너를 멤버 상태로 옮기는 ready 작업이다. Claude MOR-09는 PR655가 클래스와 빌드 항목을 삭제하므로 병합 확인 후 닫고, 병합 실패 때에만 구 리팩터링을 되살리도록 한다. 이는 설계 취향 차이가 아니라 수정 대상 자체가 소멸하는 차이다.

영향: VIS-006 경로 이동 뒤 VIS-007을 별도 구현하면 삭제될 컨테이너에 불필요한 변경·테스트가 생긴다.

권고: VIS-007은 PR655 삭제 적용 여부를 확인하는 조건부 처분으로 바꾸는 것이 맞다. 삭제가 채택되면 구현 PR 없이 대체 완료로 기록하고, 삭제가 철회될 때만 원 작업을 복원한다. 여기서는 클래스가 최신 dev에서 실제 삭제됐다고 단정하지 않는다.

근거:

- `new_tickets_codex/03_TASK_CATALOG.json:525–532` — 현 카탈로그의 구현 요구
- `new_tickets_codex/03_TASK_CATALOG.json:548–557` — 즉시 착수 상태와 조율만 있는 선행
- `new_tickets_claude/05-final/FINAL.md:120–127` — 삭제로 대체, 병합 확인 조건

## GDC-03 · Box FFD 신규 제공의 확정 요구가 Claude 목록에서 기능 필요성 재결정으로 바뀌었다

**document_drift · medium · 확신 높음**

보관된 #577의 2026-10-05 개정은 Cylinder 삭제와 Hexahedron BoxHandles FFD 신규 제공을 확정하고 PR3 완료 흐름까지 명시한다. Codex GEO-004도 이를 구현 작업으로 받는다. Claude MOR-05는 PR655의 구 UI 삭제를 근거로 신규 UI를 만들지 않을 선택과 #577 종료까지 다시 결정하게 한다. 구 shell 구현 삭제는 신규 FFD 요구 철회의 근거가 아니다. 다만 새 작업 목록 자체가 제안이므로 MOR-05는 원 요구의 승계를 바꾸려는 제안으로 해석할 수 있다. 이를 확정된 제품 정책 위반으로 판단하지 않으며, 최종 제품 결정은 재검증하지 않았다.

영향: 신규 FFD 제공이 이미 승인된 것으로 진행하는 목록과 제공 자체를 취소할 수 있는 목록이 병존한다. 일정·완료 판정이 달라진다.

권고: 후속 명시적 요구 철회가 확인되지 않으면 신규 제공 목표는 유지하고 lattice·분할 수·baseline 편집 등 세부 선택만 결정 대상으로 좁힌다. 실제 취소를 제안하려면 #577의 확정 요구를 변경하는 별도 제안으로 표시한다. 원격 최신 #577의 후속 개정 여부는 이번 문서 검토에서 확인하지 않았다. 새 목록에서 원 요구를 다시 결정하려는 사유와 그 변경 제안의 채택 여부를 명시하여, 이미 확정된 요구와 미채택 변경안을 구별한다.

근거:

- `new_tickets_codex/sources/issues/577.md:5–16` — 명시된 개정 요구 스냅샷
- `new_tickets_codex/03_TASK_CATALOG.json:130–145` — 신규 구현 완료 목표
- `new_tickets_claude/05-final/FINAL.md:80–88` — 기능 필요성 자체를 다시 여는 DEC
- `new_tickets_claude/05-final/decisions.md:39–43` — PR655 삭제로 DEC 전환한 경위

## GDC-04 · CAD temp .prt의 불개입 범위와 정규 CAD 재분류가 정렬되지 않았다

**active_conflict · medium · 확신 중간**

Project-Manifest-CAD-Path-Disposition은 2026-09-18 제품 방침을 근거로 temp .prt 누적(D16)을 사장 경로로 격리해 불개입한다고 명시한다. Claude CAD-08은 같은 D16을 다음 Load 시 glob으로 지우는 PR로 정의하고, 376행에서 구 매니페스트가 사장 경로로 묶었지만 프리뷰는 정규 CAD 동선이라고 명시적으로 재분류한다. 따라서 구 방침을 모르고 누락한 것은 아니다. 다만 서로 다른 문서가 같은 D16의 적용 범위를 반대로 분류하며 어느 문서가 이 범위를 승계하는지는 정렬되지 않았다. decisions의 LCH-29는 wbpj 배치 정책이고 대화형 프리뷰 정리와 반드시 같은 범위는 아니다. 구 문서가 무조건 우선이라는 결론도 아니다.

영향: 구 매니페스트를 따르면 D16은 제외되고 CAD-08의 명시 재분류를 따르면 대화형 프리뷰 청소가 포함된다. 작업 목록 구성과 방침 적용 범위가 달라진다. 코드상 실제로 정규 프리뷰만 건드리는지는 이번 문서 검토에서 실증하지 않았다.

권고: CAD-08의 정규 프리뷰 재분류를 범위 승계 결정으로 채택하는지 확인하고, 채택한다면 매니페스트의 D16 적용 제외를 대체하는 근거·정리 대상 temp 경계를 연결한다. 배치 산출 .prt와 대화형 temp를 구분하여 CAD-08에 LCH-29 전체를 자동 선행으로 걸지 않는다. 구 방침을 무조건 우선하거나 새 목록의 재분류만으로 제품 결정이 확정됐다고 간주하지 않는다.

근거:

- `Project-Manifest-CAD-Path-Disposition.md:55–61` — 명시적 적용 제외 정책
- `Code-Map-User-Flow-Geometry-Parameterization-CAD.md:416–418` — 동일 D16 결함의 정적 근거
- `new_tickets_claude/05-final/FINAL.md:366–376` — 정규 CAD 동선으로 명시 재분류한 구현 요구
- `new_tickets_claude/05-final/decisions.md:5–10` — 재결정은 있으나 CAD-08 조건 누락
- `new_tickets_claude/05-final/FINAL.md:378–386` — 비교: 명시적으로 재결정한 D15/D17

## GDC-05 · Optimizer Preview의 카메라 예외 설명을 구체 완료 기준에 맞게 좁힐 필요가 있다

**document_drift · low · 확신 높음**

OPT-01은 기존 geometry가 있으면 카메라를 유지하는 비파괴 overlay이고 Codex VIS-001도 기존 문서·카메라를 보존한다. REN-01 비고는 Optimizer resetCamera를 사용자가 Preview 버튼을 누른 리셋이라 registry 작업 범위 밖이라고 설명하며 OPT-01 완료 기준 (3)을 인용한다. 이는 처리 소유를 OPT-01에 넘긴다는 뜻으로 양립 가능하다. 다만 (3)이 허용하는 빈 씬 리셋 예외를 비고가 생략하여 일반 리셋 허용으로 오독할 여지가 있다. 구체 완료 기준이 이미 답하므로 미결 정책 충돌은 아니다.

영향: 공통 렌더 작업에서 Preview 버튼 클릭을 카메라 리셋의 포괄 허가로 해석하거나, 일반 takeOver의 문서 숨김을 Optimizer overlay에도 적용할 수 있다.

권고: REN-01 비고를 “Optimizer는 OPT-01의 빈 씬 예외만 허용”으로 정렬한다. 일반 모듈 takeover/Runner의 문서 숨김과 Optimizer overlay를 별도 동작으로 유지한다. #316과 #318 자체가 정책 충돌이라는 결론은 아니다.

근거:

- `new_tickets_claude/05-final/FINAL.md:2185–2188` — 비파괴 overlay의 확정 완료 조건
- `new_tickets_claude/05-final/FINAL.md:2818–2818` — 같은 문서 내 잘못 넓어진 예외 설명
- `new_tickets_claude/05-final/FINAL.md:2923–2925` — 일반 takeover의 문서 숨김 정책은 별도
- `new_tickets_codex/03_TASK_CATALOG.json:292–305` — VIS-001 카메라/기존 actor 보존

## GDC-X01 · RW 전용 스레드 제안과 GUI actor 현황은 현행 규범 충돌이 아니다

**proposal_alternative · low · 확신 높음**

rw-document-gate는 planned/현재 동작 아님을 머리글에 명시한 제안이다. 전용 QThread·양방향 DeepCopy·완전 비동기 메시지를 요구하지만 현 GUI actor를 설명하는 코드맵과 다른 단계다. Claude EXE-14는 Stage2 소유 모델을 실측 후 선택하고 Codex AST-003은 deferred 워커 이행을 구체 목표로 삼는다. 스레드 전략 선택 범위는 아직 조율해야 하지만 둘을 동시에 시행하라는 규칙으로 볼 수 없다.

영향: 문서 제목만 보고 RW actor가 이미 전용 스레드라고 믿거나, “clone 문서 타입 도입 완료=GUI 비차단 완료”로 판정하면 잘못된 선행/완료 기준이 된다.

권고: 현재 규범, 이미 구현된 타입 경계, 남은 thread 이행을 구분한다. AST-003 착수 전 EXE-14 선택 결과와 제안의 비차단 메시지·DeepCopy·close/drain 규칙을 맞춘다. 제안 문서를 구현 증거로 쓰거나 GUI blocking 방식을 확정하지 않는다.

근거:

- `rw-document-gate.md:3–5` — 명시적 제안 상태
- `rw-document-gate.md:15–25` — 제안 계약
- `Code-Map-User-Flow-Condition-Parameterization.md:353–353` — 과거 현황 설명
- `new_tickets_claude/05-final/FINAL.md:3144–3150` — Stage2 조사/선택
- `new_tickets_codex/03_TASK_CATALOG.json:603–611` — 미래 이행 목표
- `new_tickets_codex/03_TASK_CATALOG.json:633–635` — Deferred 상태

## GDC-X02 · #281의 A안/WorkerJob/MorphingGate는 폐기 이력으로 분리한다

**historical_resolved · low · 확신 높음**

281-1은 eaa77a6 좌표의 비교 문서이며 채택 결정은 이슈가 소유한다고 한다. 뒤의 #281 보관본은 #408 이후 WorkerJob·morphingSerialPool·MorphingGate를 재도입하지 않도록 명시적으로 개정했다. Claude MOR-18과 Codex GEO-007도 현 서비스 경계의 잔여와 검증으로 옮겼다. 비교 문서의 “A로 지금 착수”를 현행 요구로 되살리면 안 된다.

영향: 폐기된 실행 기제를 부활시키는 별도 PR이 생길 수 있으나, 이는 해소되지 않은 설계 선택이 아니라 이력 적용 범위의 문제다.

권고: 비교·소스 감사 이력은 보존하고 구 착수 체크리스트에 대체 문서/서비스 경계를 연결한다. 이슈 닫기 제안과 SDK 실제 런타임 검증 완료를 같은 뜻으로 취급하지 않는다.

근거:

- `281-1-morphing-entry-points-and-isolation-design-options.md:3–5` — 권위는 이슈 본문
- `281-1-morphing-entry-points-and-isolation-design-options.md:19–21` — 역사 좌표
- `281-1-morphing-entry-points-and-isolation-design-options.md:393–400` — 구 착수 권고
- `new_tickets_codex/sources/issues/281.md:61–74` — 명시적 전제 폐기
- `new_tickets_claude/05-final/FINAL.md:210–218` — 새 서비스 기준 처분

## GDC-X03 · Designer 전면 전환 기각과 OS 창 위임 선택은 다른 층의 대안이다

**proposal_alternative · low · 확신 높음**

202 문서는 기존 폼의 Qt Designer 전면 재작성을 기각하고 코드 정리 우선·선별 .ui 도입을 후순위로 둔다. Claude UIC-08/09의 Windows nativeEvent 경로는 OS 창 이동/리사이즈 책임을 바꾸는 안이며 전체 UI를 .ui 또는 QML로 재작성하는 안이 아니다. Codex UI-01도 실기 확인 후 창 구조 교체를 선택하도록 한다.

영향: 서로 다른 층의 정책을 충돌로 세면 허용된 창 관리 개선을 금지하거나, 반대로 B안이 이미 결정되었다고 착수할 수 있다.

권고: UIC-09는 UIC-08에서 B 선택 시에만 활성임을 분명히 하고 A/보류 선택 때 제외·축소한다. 202의 .ui 전면 이행 기각을 Windows frame 개선 금지로 넓히지 않는다. Geometry/CAD 위젯 통합 금지(202:356,469)도 기능이 다른 두 모듈에 한정한다.

근거:

- `202-1-view-qt-designer-vs-code-cleanup.md:430–438` — UI 작성 방식에 대한 권고
- `202-1-view-qt-designer-vs-code-cleanup.md:478–480` — 선별 Designer 도입만 옵션
- `new_tickets_claude/05-final/FINAL.md:3470–3478` — OS 위임 경로/착수 결정
- `new_tickets_claude/05-final/FINAL.md:3480–3488` — B안 구현은 UIC-08 선행
- `new_tickets_codex/03_TASK_CATALOG.json:3960–3963` — 실기 검증 후 조건부 구조 교체

## 범위와 제외 원칙

- Code-Map 문서는 각 머리글이 역사 커밋의 정적 현황표라고 한정한다. VTP·공유 RW 원복·테스트 0건 등 낡은 현황 수치를 모두 활성 충돌로 세지 않았다.
- CAD D29~31 유보·D32~33 철회는 명시적 처분이다. 미래 CAD deck 합류 방향과 현 .prt OCCT 프리뷰는 다른 단계다. CAD-09 재결정 자체도 몰래 방침을 바꾼 것으로 취급하지 않았다.
- 일반 씬 인수의 문서 숨김, 모듈 이탈 시 복원, Optimizer의 비파괴 overlay는 함께 성립한다. REN-01은 registry 범위와 OPT-01 소유를 구분한 설명으로 양립하며, 빈 씬 예외를 풀어 적는 교정 권고만 남겼다.
- Issue-Revision-History의 기존 개정/반영과 미반영 팀 논의 계획을 구분했다. setId·출처·대장 변경은 root/downstream 검토에 맡겨 중복 findings를 만들지 않았다.
- 커버리지의 full은 문서 전체, focused_deep/targeted는 기록한 절의 집중 대조를 뜻한다. 원격 상태·최신 코드 실증을 뜻하지 않는다.
