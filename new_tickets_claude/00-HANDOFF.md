# 인수인계 — 상태: 전 단계 완료 (2026-10-06)

> 기준 코드 `dev` @ `b08a91b3`. 이 폴더 밖에는 아무것도 쓰지 않았다 (이슈·PR·위키·코드·보드 무변경).
> 납품물: `05-final/FINAL.md`. 재개가 필요하면 `00-progress.md` 끝부분 → `05-final/decisions.md` 순으로 읽는다.

## 1. 완료 상태

```
[Phase A] 모듈별 수집·검증·항목화 ........ 완료 (16/16)
[Phase B] 횡단 정합 .................... 완료 (B1 · B2)
[Phase C] 모듈별 독립 검토 ............. 완료 (16/16, 지적 212)
[C-2]     횡단 결정 .................... 완료 (10건, 05-final/decisions.md)
[C']      검토 반영 1차 ................ 완료 (16/16 — 반영 199 · 기각 19 · 보류 35)
[C' 2차]  보류 이관 반영 ............... 완료 (9 + CON 직접 — 반영 17 · 이미 반영 12 · 미반영 2)
[D-1]     재생성 ....................... 완료 (deps · mapping · check_coverage 0)
[D-2]     FINAL.md 조립 ................ 완료
```

| 최종 집계 | 값 |
|---|---|
| claims | 938 |
| items | 364 — PR 268 · DEC 46 · INV 13 · EXT 7 · CLOSE 30 / S 256 · M 92 · L 10 |
| 정합 검사 | 이슈 누락 0 · 결함 누락 0 · 참조 오류 0 · 범위밖 미흡수 2 (EXT 의도: PRE-c23 · EXE-c45) |
| deps | 순환 0 · PR 대기 197 · 즉시 착수 119 |
| mapping | 이슈 117 → 항목 86 · CLOSE 21 · CLOSE+잔여 10 / 결함 201 → 항목 159 · CID 경유 8 · CLOSE 3 · 해소/범위밖 31 |

## 2. 이번 세션의 주요 결정 (상세는 05-final/decisions.md)

| # | 결정 |
|---|---|
| ① | wbpj 배치 경로 처분 DEC = **LCH-29** 신설. 소비자 CAD-01·02·05 · LCH-06·27 · PRJ |
| ② | **PR #530 은 머지하지 않는다** — 재업로드. 공통부 PER-07 + 홉별 5건(DOE-16 · PRE-32 · BLD-20 · RUN-34 · OPT-26). HANDOFF 구판의 "홉 신설 불요" 폐기 |
| ③ | 공용 JSON 헬퍼 = 신설 대신 `DashSaveSystem::read/writeJsonFile` **승격** (PER-02 재정의, 중복 8벌) |
| ④ | PR #655 전 모듈 반영. 선행 승격: MOR 5 · OPT 2 · UIC 2 · DEV 2 |
| ⑤ | `kSnapshotKeys` allowlist 확장은 DOE-16, 읽기는 PRE-32 |
| ⑥⑨ | 보드 밖 OPEN 이슈 26건 중 **4건만 편입** (#552 #404 #394 #577, 사용자 결정). 전수는 `01-sources/open_issues_offboard.md` |
| ⑧ | Set 모델 공통 베이스 부재 → **PRJ-34** DEC 선행, PRJ-08·09·22 재설계 |
| ⑩ | 열린 PR 스냅샷 재갱신 — #656 #658 추가. PRE 는 #656·#658 이 작업 일부를 이미 수행해 선행 8건·CLOSE 1건(PRE-03) |
| 규칙 | 분할 기준 = **개념적 응집** (00-plan 1-2 보정, 사용자 지시). 개념이 하나면 기제가 둘이어도 유지 |

## 3. 다음 단계 (이 폴더 밖 — 별도 승인 필요)

- **발행**: FINAL.md 의 364 항목을 GitHub Issue 로 올리는 것은 00-plan 1-5 금지 범위. 별도 단계로 승인 후 진행.
- 발행 전 재확인거리: 열린 PR 7건 상태(머지되면 해당 선행 해소) · 보드 밖 22건 편입 여부 재검토 · DEC 46건 중 결정 주체 지정.
- D-1 이 남긴 검토거리: PRE-28 ↔ PER-03 선행 여부(PRE 2차가 "무관" 으로 미반영) · RUN-15 ↔ OPT-10 합의는 "SurrogateTableController 는 RUN 전용" 으로 종결.

## 4. 운용 메모 (유지)

- subagent 동시 수 4개 상한. 16개 동시는 매번 429. Opus 로 돌릴 때 이전 계정 한도 1회 소진(14:30 리셋).
- `gh` 는 항상 `--repo NumeRealWorks/DashOpti_GUI`. 열린 PR 재갱신 명령은 `01-sources/open_prs.md` 머리말.
- `items_index.OPEN_PRS` 가 "머지 대기" 집합 — #530 은 의도적으로 빠져 있다. 새 PR 이 열리면 여기와 `PR_ALIAS` 에 추가.
- 선행 파서는 괄호 안 ID 를 제외한다(`strip_parens`). 조건부 선행은 괄호 안에 쓴다.

## 5. 폴더 지도

| 경로 | 내용 |
|---|---|
| `00-plan.md` · `00-prompts.md` · `00-progress.md` | 틀 · 템플릿 · 진행 기록(전 단계 append) |
| `01-sources/` | 원천 — open_issues 113 · closed 94 · defects 201 · wiki · `open_prs.md`(7건) · `open_issues_offboard.md`(26건) |
| `02-claims/` · `03-items/` | 모듈 16 × 원자 항목 / 작업 단위 (C' 2차 반영본) |
| `04-review/` | 검토 16 + `처리` 열(반영/기각/보류 사유) |
| `05-final/` | `decisions.md`(C-2 10건) · `deferred.md`(2차 보류 전수) · `deps.md` · `mapping.md` · **`FINAL.md`** · 스크립트 5종 |
