### [[Home]]

**저장소 운영**

- [[프로젝트 관리|프로젝트-관리]]
  - [[저장소 관리 수칙|저장소-관리-수칙]]
    - [[Release / QC 이벤트 브랜치|릴리스-QC-이벤트-브랜치]]
  - [[코딩 컨벤션 (제정 중)|코딩-컨벤션]]
  - [[문서 관리|문서-관리]]

**개인 문서**

<details>
<summary>minhopark</summary>

[[전체 색인|minhopark-Index]]

<details>
<summary>사용 흐름</summary>

- [[End-to-End User Flow|End-to-End-User-Flow]]

</details>

<details>
<summary>프로젝트 저장 구조</summary>

**조사 — 현황 실측**

- [[키 단위 쓰기·읽기 왕복 대장|Project-Store-Survey-Key-IO-Ledger]]
- [[입력 셋·페이로드·실행 경로|Project-Store-Survey-Inputs-Payloads-Runtime]]
- [[진입 파일 5종의 상류 동선|Project-Store-Survey-Reference-Entry-Upstream-Flows]]

**설계 — 미확정 (착수 근거로 인용 불가)**

- [[프로젝트 → AnalysisLauncher 구현 배선|Project-Store-Design-Wiring-Project-To-Launcher]]
- [[엔티티 모델 개편 3안|Project-Store-Design-Entity-Model-Options]]
- [[계층 재단과 배치|Project-Store-Design-Layer-Cut]]
- [[안 α 최소 착수|Project-Store-Design-Alpha-Minimal]]
- [[결함 축 대응과 신설 배선|Project-Store-Design-Rationale]]

</details>

<details>
<summary>프로젝트 매니페스트 도입과 모듈 의존성 관리</summary>

- [[작업 순서와 문서 배치 — 매니페스트 도입 · 마스터|Project-Manifest-0-Work-Order]]
- [[레지스트리 소비자와 모델 신원 저장소 — 매니페스트 도입 · 조사|Project-Manifest-1-Context-Registry-And-Model-Identity]]
- [[활성 커서와 모듈 데이터 소스 분리 — 매니페스트 도입 · 조사|Project-Manifest-2-Active-Cursor-Data-Coupling]]
- [[모듈별 기준 deck 소유 — 매니페스트 도입 · 설계|Project-Manifest-3-Module-Deck-Ownership]]
- [[PR 단위 티켓 분할 — 매니페스트 도입 · 착수 계획|Project-Manifest-4-Ticket-Slicing]]

</details>

<details>
<summary>코드 대응 대조표</summary>

- [[도메인 구조도 ↔ 코드 매핑|Code-Map-Domain-Diagram]]
- [[사용자 단 모듈 ↔ 크리티컬 패스 코드 동작 대조표|Code-Map-User-Flow]]
- [[Geometry Parameterization — Morphing|Code-Map-User-Flow-Geometry-Parameterization-Morphing]]
- [[Geometry Parameterization — CAD|Code-Map-User-Flow-Geometry-Parameterization-CAD]]
- [[Condition Parameterization|Code-Map-User-Flow-Condition-Parameterization]]
- [[Analysis Launcher|Code-Map-User-Flow-Analysis-Launcher]]
- [[Data Preprocessor|Code-Map-User-Flow-Data-Preprocessor]]
- [[Model Builder (Sim · MCU)|Code-Map-User-Flow-Model-Builder]]
- [[Model Runner (Sim · MCU)|Code-Map-User-Flow-Model-Runner]]
- [[Results Analyzer|Code-Map-User-Flow-Results-Analyzer]]
- [[Optimizer|Code-Map-User-Flow-Optimizer]]
- [[데이터 소유·소비 구조도 — RW 세션 · 모핑 핸들|Code-Map-Data-Ownership]]

</details>

<details>
<summary>리팩토링 · 배포 계획</summary>

- [[트라이얼 릴리스 작업 배분|Trial-Release-Work-Breakdown-and-Axes]]
- [[3트랙 병렬 배포 계획|200-1-release-phasing-plan]]
- [[W6·W10 티켓 요약표|205-1-w6-w10-ticket-summary]]
- [[W10-f 설계 결정 검토 스냅샷 (#279·#280·#281·#282)|215-1-w10-f-design-decision-review-snapshot]]
- [[W6·W10 실제 변경 내역과 잔여 이벤트·상태 설계|205-2-w6-w10-change-log-and-remaining-design]]
- [[모핑 진입점 전수와 격리 설계 4안 — A · A′ · B · C|281-1-morphing-entry-points-and-isolation-design-options]]
- [[핸들 데이터·뷰 분리 — DashHandleData 추출 범위|Handle-Data-View-Separation]]
- [[프로젝트 16 편입 스캔과 보드 운영|Project-Board-Intake-And-Operations]]
- [[백로그 28건 이슈 발행 계획 — 중복 판정 포함|Backlog-Issue-Publication-Plan]]

</details>

<details>
<summary>결함 분석</summary>

- [[모듈 9종 결함 통합 색인 — 성격별 분류|Cross-Module-Defect-Index]]
- [[프로젝트 매니페스트 귀속|Cross-Module-Defect-Menifest-Axis]]
- [[창·레이아웃 크기 불안정|Multi-Display-DPI-Scaling-Breakage]]

</details>

<details>
<summary>개념 해설</summary>

- [[배치잡 개념 정리 — batch · case · stage 와 장부 경계|264-2-batch-stage-ledger-concepts]]
- [[동기 펌핑 → 비동기 전환 — 차이와 선행 항목|215-2-sync-pumping-to-async-conversion-checklist]]
- [[워커 선결 조건 용어 해설|203-1-worker-precondition-concepts-qa]]

</details>

<details>
<summary>사전조사 (2026-07 · #192~#206)</summary>

**정본 2건**

- [[리팩토링 백로그 (통합 정본)|200-3-prioritized-backlog]]
- [[W6·W10 비동기 최소 구현 예제|205-5-w6-w10-async-minimal-example]]

**조사·설계 13건**

- [[아키텍처 분석 — MVC vs MVVM|192-1-architecture-analysis-mvc-mvvm]]
- [[비동기 실행 개념 정리|193-1-async-execution-models]]
- [[비동기 실행 패턴 — W6·W10 상세|194-1-async-execution-patterns]]
- [[백로그 W1~W21 코드 실증|195-1-backlog-code-evidence]]
- [[CI 구축 TODO|196-1-ci-todo]]
- [[GUI 재구성 — MVVM·QML 평가|197-1-gui-restructure-mvvm-qml]]
- [[개선 로드맵 — 4관점 통합 진단|198-1-improvement-roadmap]]
- [[JSON-RPC 2.0 가이드 — CadNx 최소 사용예|199-1-jsonrpc2-protocol-introduction-example-cadnx]]
- [[QProcess 안티패턴 카탈로그|201-1-qprocess-antipattern-catalog]]
- [[View 정리 전략 — Designer vs 코드 정리|202-1-view-qt-designer-vs-code-cleanup]]
- [[워커 선결 조건 D1~D5 상세 분석|203-2-worker-preconditions-analysis]]
- [[엔티티 소유 계층|204-1-entity-ownership-hierarchy]]
- [[W6·W10 실행 모델 설계|206-1-w6-w10-thread-execution-design]]

</details>

</details>
