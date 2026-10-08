# 새 작업 목록 작성 계획과 운영 규칙

사용자 요청: 기존 이슈는 참고로 사용하고 남은 일을 모듈별로 완전히 재작성한다. 작업은 대체로 PR 하나로 구현·검증할 크기로 잡되 엄격한 크기 제한은 두지 않는다. GitHub 발행·수정·커밋·push는 하지 않는다. 모든 문서와 조사 결과는 이 폴더에 남긴다.

## 기준

- 조사 시작: 2026-10-05 (Asia/Seoul).
- 코드 기준: local dev `b08a91b39bbdb7c3b75796ff2cd7f663d53258ef`. 원격 dev와 열린 PR은 별도 확인한다.
- `notes`는 `../DashOpti_GUI.notes`의 심볼릭 링크다. 이 작업의 쓰기 범위는 `notes/new_tickets_codex/`뿐이다.
- 기존 보드: NumeRealWorks project 16. 최초 스냅샷 207항목/열린 이슈112건. 최신 조회 성공 시 갱신한다.
- 기존 이슈의 오래된 수치·설계·상태를 현재 코드 사실로 인용하지 않는다. 로컬 코드, 병합 PR, 미병합 PR, 이슈 요구, 추정을 구분한다.
- 기능 범위: 이미 요청된 기능·정책, 실제 결함, 이를 해결하는 구조·인프라 작업. 근거 없는 전면 재설계나 신규 제품 기능은 확정 목록에 넣지 않는다.

## 진행 단계

1. 소스 스냅샷과 모듈/워크플로 지도를 작성한다.
2. 담당 agent가 요구·최신 결정 추출 → 실제 코드/테스트 대조 → 워크플로 누락 점검 → 작업 카드 작성을 수행한다.
3. orchestrator가 공통 저장·프로젝트·UI·인프라를 조사하고 모듈 간 책임/중복/선행 관계를 통합한다.
4. 다른 담당 agent가 작업 카드의 타당성·누락·중복을 교차 검토한다. 지적마다 처분을 기록한다.
5. 전체 목록, 착수 순서, 모든 기존 이슈의 처분/연결표, 조사 범위/제약을 완성한다.
6. 링크·ID·의존 순환·이슈 전수 대응·JSON/Markdown 정합을 스크립트로 검증한다. 종료 직전 원격 변경 여부를 재확인한다.

## 위임과 문맥 관리

- agent A: Geometry/CAD/Condition/Project Assets/VTK, 접두 `GEO`, `CAD`, `CON`, `AST`, `VIS`.
- agent B: DOE Sampler/Analysis Launcher/Direct Launch/결과 처리/solver, 접두 `DOE`, `AL`, `RES`, `DIR`.
- agent C: Model Builder/Runner/Optimizer/Results Analyzer, 접두 `BLD`, `RUN`, `OPT`, `ANA`.
- root: 공통 프로젝트/저장/실행기/UI/개발환경, 접두 `PRJ`, `IO`, `ASY`, `UI`, `DEV`.
- 각 agent는 자신의 `research/<owner>.md`, `modules/<owner>.md`, `modules/<owner>.json`, `research/<owner>_dispositions.json`만 작성한다. 공통 결정은 root가 문서화한다. 다른 담당 파일을 수정하지 않는다.
- 중간 보고는 파일 경로, 핵심 발견, 넘겨야 할 접점만 보낸다. 상세는 디스크에 유지한다. `01_PROGRESS.md`가 orchestrator 인계 지점이다.
- 독립 조사에는 병렬 tool 호출을 활용하되 코드 변경·build·GitHub mutation은 하지 않는다. 실행이 필요한 확인은 검증 작업/제약으로 명시한다.

## 작업 카드 형식

각 JSON 파일은 배열이다. 카드마다 다음 필드를 작성한다:

`id`, `module`, `title`, `outcome`, `scope`(문자열 배열), `acceptance`(문자열 배열), `validation`(문자열 배열), `dependencies`(작업ID 배열), `tags`(A~G 배열), `sources`(이슈번호 정수 배열), `evidence`(파일:행/심벌 또는 PR 근거 배열), `status`(`ready`/`after_dependency`/`in_flight`/`needs_decision`/`needs_runtime_check`/`deferred`), `priority`(`P1`/`P2`/`P3`), `notes`.

- 태그 A=데이터무결성 B=실행모델 C=데이터모델·식별자 D=UI표준화 E=코드구조 F=개발인프라 G=출고품질. 다중 태그이며 작업의 소속·우선순위와 분리한다.
- priority는 새 목록 제안이다. P1=데이터손실/잘못된 결과/크래시/핵심 흐름 차단, P2=정상 기능 완결/응답성/공통 계약, P3=후순위 정리·조건부 편의. 근거에 따라 판단한다.
- status는 조사 판정이다. 미병합 PR의 구현은 `in_flight`; 단순 예상 구현을 완료 처리하지 않는다.
- broad parent는 실행 카드로 중복 세지 않는다. 필요하면 개별 완료 가능한 부분만 카드로 만든다.
- 구현 선택이 미확정이면 정책 결정이 필요한 구체 질문과 영향 범위를 notes에 기록한다. 임의로 정책을 확정하지 않는다.
- PR 크기는 목적·일관된 변경·독립 검증 기준으로 유연하게 정한다. 인위적인 파일별/레이어별 분할을 피한다.

## 요구 처분 형식

`research/<owner>_dispositions.json`: 배열. 각 항목 `issue`(정수), `disposition`(`mapped`/`partial`/`resolved`/`superseded`/`withdrawn`/`historical`/`needs_check`/`cross_owner`), `tasks`(ID배열), `reason`(근거/다른 담당 접점). 기존 이슈 본문을 그대로 작업으로 복제하지 않는다.

## 완성 산출물

- `README.md`: 읽는 순서·기준·결과와 한계.
- `02_MODULE_WORKFLOWS.md`: 현재 모듈/흐름/조사 범위.
- `03_TASK_CATALOG.md` 및 `.json`: 통합 전체 작업 목록.
- `04_EXECUTION_ORDER.md`: 선행 관계와 착수 묶음.
- `05_ISSUE_CROSSWALK.md` 및 `.json`: 207개 원본 이슈 전수 대응과 처분.
- `06_COVERAGE_AND_LIMITS.md`: 흐름별 커버리지·코드 확인/실측 미확인·결정 질문.
- `reviews/`: 독립 검토와 처분.
- `sources/`, `research/`, `modules/`, `scripts/`: 근거 스냅샷·상세 조사·카드·검증 재현 도구.
