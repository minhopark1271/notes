# 모듈별 새 작업 목록 — Codex 조사본

2026-10-05, dev `b08a91b39bbdb7c3b75796ff2cd7f663d53258ef` 기준. 기존 보드 이슈를 요구/이력의 참고로 사용하고, 현재 코드·테스트·최신 PR과 사용자 흐름을 대조해 새로 작성했다. GitHub 발행·수정·커밋·push 또는 애플리케이션 코드 변경은 하지 않았다.

**새 추적 단위 123개**: 착수 가능71, 선행 작업 후28, 진행 PR4, 결정 필요7, 실측 필요6, 보류7. 진행/조건부/검증 항목을 포함하므로 123개의 신규 PR을 반드시 만들어야 한다는 의미는 아니다. PR 크기는 독립적인 목적과 검증 가능성으로 유연하게 잡았다.

보드 **207개 전수**, 그중 열린 이슈 **112개 전수**를 새 작업 또는 해결·철회·대체 근거에 연결했다. A~G는 작업의 관련 측면을 나타내는 복수 태그이며 작업 분할의 축으로 사용하지 않았다.

## 읽는 순서

1. [전체 작업 목록](03_TASK_CATALOG.md) — 모듈/판정 색인과 작업별 범위·완료 조건·검증·근거. [JSON](03_TASK_CATALOG.json).
2. [착수 순서](04_EXECUTION_ORDER.md) — 열린 PR, 즉시 P1, 논리적 선행 관계, 같은 파일의 충돌 주의, 결정 관문.
3. [기존 이슈 대응표](05_ISSUE_CROSSWALK.md) — 207개 처분과 새 작업의 다대다 연결. [JSON](05_ISSUE_CROSSWALK.json).
4. [모듈·워크플로 지도](02_MODULE_WORKFLOWS.md)와 [커버리지·한계](06_COVERAGE_AND_LIMITS.md).
5. [교차검토 반영](reviews/REVIEW_RESOLUTIONS.md)과 [문서 검증 결과](reviews/validation.md).

후속 대조(2026-10-07): [board.txt의 기존 이슈와 작업 정의 겹쳐 보기](07_BOARD_OVERLAY.md). 원본62개 이슈 전수 대응, 통합·분할·정책 차이를 기록했다. 기존123개 카탈로그를 수정한 결과가 아니라 별도 대응 뷰다.

## 중요한 재정의

- 모듈 개명/Launcher 탭 이동 이후의 실제 소유자로 배정했다. 오래된 함수명·펌핑 개수는 완료 기준으로 쓰지 않았다.
- 이미 존재하는 setId·SaveSystem·QSaveFile·비동기 실행기·기동 timeout을 새 기반 도입으로 중복 계산하지 않았다.
- PR530/651/652/654는 각각 한 진행 작업으로 집계했다. PR651의 Assets/Launcher 부분은 통합했다.
- PR530의 MCU 예외와 templateDecks 철회, PR654의 값 상태기·JSON/구형식 처리 등 최신 결정을 반영했다.
- 부모 이슈와 하위 이슈를 모두 구현 작업으로 세지 않았다. 조회 UI 철회·naming gate 보류 등 기존 범위 결정을 유지했다.
- 사용자 흐름 조사로 확인한 저장/실패/값 유실/삭제/내보내기 문제도 근거를 붙여 추가했다. 조건부 기능은 확정 구현과 구분했다.

## 파일 구조와 정본

| 위치 | 역할 |
|---|---|
| `00_PLAN.md`, `01_PROGRESS.md` | 운영 계획·역할 분담·orchestrator 인계 기록 |
| `02_…` ~ `06_…` | 최종 통합 결과; 작업 목록/대응표 JSON이 기계가독 정본 |
| `modules/` | 담당별 작업 카드 및 교차검토 반영 뷰. JSON의 AST-002만 PR651 통합 전 추적 alias로 보존 |
| `research/` | 실제 코드 조사, raw 검색 근거, 담당 이슈 처분, counts/alias |
| `reviews/` | 다른 담당자의 독립 검토·처분·검증 결과 |
| `sources/` | board·issue·comment·wiki·repo 문서·열린 PR 전체 diff·외부 파일 스냅샷 |
| `scripts/` | 읽기 전용 소스 수집 및 문서 생성·검증 재현 |

`notes`는 별도 notes 저장소를 가리키는 심볼릭 링크다. 요청한 `notes/new_tickets_codex` 아래에 모든 산출물을 남겼다. imported wiki/repo 문서는 조사 당시 근거이므로 그 안의 옛 상태를 최종 상태로 읽지 않는다. 상세 근거 문자열의 코드 경로는 DashOpti_GUI 저장소 루트 기준이며 행번호는 기준 커밋의 좌표다.

## 검증 범위

수행: 코드·기존 테스트 소스·열린 PR diff 대조, 세 agent의 분담 조사와 교차검토, ID/의존/링크/보드 전수 대응 검사.

미수행: Windows 앱 빌드·GUI·solver·SDK 실제 실행. 각 카드의 테스트는 구현 후 수행할 완료 조건이다. mixed-DPI, 대형 결과, NX/Ansys/Abaqus/fe-safe, 외부 공급 환경은 실측 관문으로 남겼다. 자세한 내용은 [한계 문서](06_COVERAGE_AND_LIMITS.md)를 따른다.

## 재생성

프로젝트 루트에서 아래를 순서대로 실행한다. 애플리케이션 코드를 바꾸지 않는다.

```sh
python3 notes/new_tickets_codex/scripts/write_common_cards.py
python3 notes/new_tickets_codex/scripts/integrate_reviews.py
python3 notes/new_tickets_codex/scripts/build_catalog.py
python3 notes/new_tickets_codex/scripts/validate_catalog.py
```

`refresh_sources.py`는 인증된 GitHub 읽기만 수행하지만 조사 입력 스냅샷을 최신값으로 덮어쓴다. 새 기준으로 재조사할 때만 실행하고 기존 결과와 기준 커밋을 함께 갱신해야 한다. token은 subprocess 환경에서만 사용하며 문서/파일에 저장하지 않는다.
