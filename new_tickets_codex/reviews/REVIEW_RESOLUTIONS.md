# 독립 검토와 반영 기록

세 agent가 담당 영역 조사·작성 후 서로 다른 영역의 코드를 대조했다. 원본 지적은 각 review JSON/Markdown에 남겨 두었다. 최종 반영은 `scripts/integrate_reviews.py`, `scripts/write_common_cards.py`, `scripts/build_catalog.py`로 재현한다.

| 지적 | 판단과 반영 | 최종 위치 |
|---|---|---|
| EXR-01 / DS-X02 | 수용. 단계별 조합 검증/MCU 예외를 분리하고, 더 최신 PR530에서 철회된 templateDecks/D21 부속은 복원하지 않는다. | PRJ-03 |
| EXR-02 / DS-X03 | 수용. 첫 AL→Builder 기록 외 학습모델 및 DOE/Runner/Optimizer/Analyzer 생성·소비 확산을 추가했다. 현재 version 경고/로컬 case 저장과 목적을 구분했다. | PRJ-05, IO-10·11 |
| EXR-03 | 수용. 준비 훅 예외를 실패로 정규화하고 UI/slot 회수 검증을 추가했다. | ASY-01 |
| EXR-04 | 수용. PR652가 삭제하는 Direct per-row Browse는 수정 요구에서 제외하고 실제 MCU 표/Runner preview 잔여로 좁혔다. | UI-06 |
| EXR-05 | 수용. 첫 적용 경계를 DashProject의 복원/개명/참조 네 경로로 고정하고 나머지 모듈별 소비 이관을 별도로 목록화했다. | PRJ-09, IO-07~09 |
| GXR-01 | 수용. co_await와 실제 worker 실행을 구분한다. RW clone/edit/export 이관은 AST-003에 명시하고 AL-12의 응답성 약속을 독립 파일 준비/fallback으로 좁혔다. | AST-003, AL-12 |
| GXR-02 | 수용. 기존 uuid/tableId로 Set 포맷 작업을 시작할 수 있어 PR530 전체 하드선행을 제거했다. | RES-12 |
| GXR-03 | 수용. 1차에도 안전한 교체·다른 식별자 병합 금지를 요구한다. XML 개선→2차 HDF5/USD 비교라는 기존 순서는 유지했다. | RES-12·13 |
| GXR-04 | 수용. 도메인 실파일 시험은 먼저 가능하되 sub-result/완료집계/worker 최종 승인은 해당 변경 후 재검증하도록 명시했다. | RES-11 |
| DS-X01 | 수용. 기존 actor 숨김 대신 기존 모델·핸들·카메라·표시커서를 그대로 보존하는 overlay로 교정했다. 일반 숨김 정책은 VIS-003이다. | VIS-001 |
| DS-X04 | 수용. IO-04에서 삭제된 Analyzer 시각화 설정 영속화를 되살릴 수 있는 표현을 제거했다. 도메인 편집 값은 OPT-05, 저장 기제는 IO-04다. | IO-04, OPT-05 |
| DS-X05 | 수용, 담당자가 이미 반영. NodeSet 파일의 저장뿐 아니라 실제 lookup에 그 문서를 사용하는지 검증한다. 별도 파일 허용 정책은 유지한다. | RUN-04 |
| EXD-01 | 수용. 전체 Set XML 이행을 version 경고의 필수 선행에서 제거하고 포맷 중립 세대 계약+AL 첫 생산 작업을 추가했다. | PRJ-11, BLD-01, ANA-03 |
| EXD-02 | 수용. 수동 Plot과 자동 debounce의 실패 안내를 구분하고 build null 실패도 포함한다. | ANA-07 |
| EXD-03 | 수용. 공유 NX 계면은 CAD-001이 소유한다. 모핑 귀속은 즉시 작업, NX 소비자 이행은 보류 상태를 승계하는 별도 작업으로 나눴다. | RUN-07·11, OPT-02·07, CAD-001 |
| root 통합 | 같은 PR651을 Assets/Launcher 두 구현으로 중복 세지 않도록 AST-002를 AL-09에 합쳤다. alias를 대응표에 반영했다. | AL-09, research/task_aliases.json |

지적 17건(같은 문제의 중복 발견 포함)을 모두 처분했다. ‘수용’은 문서의 범위·수용 조건을 고쳤다는 뜻이며 앱 구현을 수정했다는 뜻은 아니다. 제품 결정과 실측 관문은 [커버리지와 한계](../06_COVERAGE_AND_LIMITS.md)에 남아 있다.
