# subagent 프롬프트 템플릿

`<MOD>` 를 모듈 코드로 바꿔 쓴다. 경로는 저장소 루트 `/Users/minhopark/Projects/DashOpti_GUI` 기준. 작업 폴더 `notes/new_tickets_claude/` 는 `N/` 으로 줄여 쓴다.

## Phase A — 모듈별 수집·검증·항목화

```
DashOpti_GUI 저장소(/Users/minhopark/Projects/DashOpti_GUI, 브랜치 dev @ b08a91b3)에서 모듈 <MOD> 의 작업 목록을 작성한다. 결과는 파일로만 남기고 보고는 10줄 이내로 한다.

절차
1. notes/new_tickets_claude/00-plan.md 를 끝까지 읽는다. 1절(틀)·4절(형식)·5절(운용)·6절(배정표)은 그대로 따른다.
2. 6절 배정표에서 <MOD> 의 담당 이슈 · 접점 이슈 · 결함 prefix · 추가 원천을 확인한다.
3. 담당 이슈 전문을 notes/new_tickets_claude/01-sources/open_issues/<N>.md 에서 읽는다. 결함은 01-sources/defects/<PREFIX>.md 를 읽고, 설명이 부족하면 01-sources/wiki/Code-Map-User-Flow-*.md 의 같은 ID 를 본다. 접점 이슈는 제목·Goal 만 본다. 01-sources/closed_issues.md 는 "이미 해소/기각" 판정에 쓴다.
4. 원자 항목으로 분해해 notes/new_tickets_claude/02-claims/<MOD>.md 를 4-1 형식으로 쓴다. 이슈 하나에 여러 작업이 섞여 있으면 전부 분리한다.
5. 항목마다 현행 코드에서 재확인한다 — 심볼·패턴이 아직 있는가, 이미 고쳐졌는가(git log -S, closed_issues.md, 최근 PR). 좌표는 현재 파일:함수로 적고, 이슈 본문의 행 번호는 믿지 않는다. 건수가 작업 규모를 정하는 항목(펌핑·QMessageBox·null 가드·직쓰기 등)은 <MOD> 영역 안에서 직접 세어 적는다.
6. 판정 유효인 항목을 1-2 규칙(모듈 1 · 기제 1 · 동작 변경과 리팩터 혼합 금지)으로 작업 단위로 묶어 notes/new_tickets_claude/03-items/<MOD>.md 를 4-2 형식으로 쓴다. 파일 끝 대응표에 담당 이슈·결함 ID 전부를 한 행씩 넣는다. 다른 모듈 소관이면 판정 `범위밖` + 대상 모듈을 적고 항목은 만들지 않는다.
7. 담당 이슈 중 In progress · In review 가 있으면 `gh pr list --state open --search "<N>"` 과 `gh pr view` 로 열린 PR 의 범위를 보고 잔여분만 항목으로 쓴다.
8. 보고(10줄 이내): claims 수와 판정 분포, items 수와 종류·규모 분포, 미확인 사유, 다른 모듈로 보낸 항목, 배정표 수정 제안.

금지: 코드 수정 · 빌드 · gh 쓰기(issue/pr/comment 생성·편집) · notes/new_tickets_claude 밖 파일 생성.
```

## Phase C — 모듈별 독립 검토

```
DashOpti_GUI 저장소(/Users/minhopark/Projects/DashOpti_GUI, dev @ b08a91b3)에서 모듈 <MOD> 의 작업 목록 초안을 검토한다. 결과는 notes/new_tickets_claude/04-review/<MOD>.md 에 4-3 형식으로 쓰고 보고는 10줄 이내로 한다.

절차
1. notes/new_tickets_claude/00-plan.md 를 읽는다.
2. 검토 대상: 02-claims/<MOD>.md 와 03-items/<MOD>.md. 원천: 6절 배정표의 담당 이슈 전문(01-sources/open_issues/)·결함 파일(01-sources/defects/)·closed_issues.md.
3. 다음을 찾는다.
   a. 누락 — 원천에 있는데 claims 에 없는 작업. 접점 이슈가 <MOD> 에 요구하는 작업도 포함
   b. 잔존 — "해소됨" 이어야 하는데 유효로 남은 항목. 코드에서 직접 확인
   c. 근거 오류 — 좌표가 현행 코드와 다르거나 심볼이 없음
   d. 단위 위반 — 한 항목에 기제가 둘, 동작 변경과 리팩터 혼합, 모듈이 둘
   e. 완료 기준 부실 — 확인 불가능하거나 비어 있음
   f. 선행·충돌 누락 — 같은 파일을 고치는 항목끼리, 진행 중 PR 과의 충돌
   g. 종류 오분류 — PR 이어야 할 DEC, DEC 이어야 할 PR 등
4. 지적마다 근거(파일:함수 또는 원천 ID)와 조치 제안을 적는다. 문제 없는 항목은 적지 않는다.

금지: 03-items·02-claims 직접 수정 · 코드 수정 · gh 쓰기.
```

## Phase C' — 검토 반영

```
notes/new_tickets_claude/04-review/<MOD>.md 의 지적을 02-claims/<MOD>.md · 03-items/<MOD>.md 에 반영한다. 00-plan.md 의 형식을 유지한다. 반영하지 않는 지적은 04-review/<MOD>.md 의 해당 행 끝에 `| 기각: 사유` 를 덧붙인다. 보고는 5줄 이내 — 반영 N건 · 기각 N건 · 항목 수 변화.
```

## Phase B — 횡단 정합 (단일 subagent)

```
notes/new_tickets_claude/ 의 모듈별 초안 16종(02-claims/*.md · 03-items/*.md)을 모듈 간에 정합한다. 먼저 00-plan.md 를 읽고, `python3 notes/new_tickets_claude/05-final/check_coverage.py` 를 실행해 현황을 본다.

할 일
1. 범위밖 이관 — 스크립트의 "범위밖 이관" 목록을 대상 모듈별로 처리한다. 대상 모듈 03-items 에 같은 기제의 항목이 있으면 그 항목의 `흡수` 에 CID·원천 ID 를 덧붙이고, 없으면 새 항목을 끝 번호 다음으로 추가한다 (4-2 형식). 대상 모듈 02-claims 에도 행을 옮겨 적는다 (CID 는 대상 모듈 번호로 새로 매기고 비고에 "← <원 CID>").
2. 모듈 간 중복 — 같은 작업이 두 모듈에 각각 항목으로 있으면 변경 파일이 많은 쪽에 남기고 다른 쪽은 삭제, 남긴 쪽 `흡수` 에 합친다. 삭제한 모듈의 대응표 행은 "→ <남긴 항목 ID>" 로 고친다.
3. 모듈 간 선행·충돌 — 각 항목의 `선행`·`충돌` 에 다른 모듈 항목 ID 를 보강한다. 같은 파일을 고치는 항목 쌍은 양쪽 `충돌` 에 적는다 (파일 교집합은 `변경 범위` 로 계산). 결과를 05-final/deps.md 에 표로 쓴다: `| 항목 | 선행 | 충돌 | 비고 |` + 순환 여부.
4. 스크립트를 다시 돌려 열린 이슈 누락 0 · 결함 누락 0 · 존재하지 않는 참조 0 이 될 때까지 반복한다. 결함이 어느 모듈에서도 유효하지 않다고 판정됐으면(해소됨·미확인) claims 에 그 판정이 있으면 된다 — items 에 억지로 넣지 않는다.
5. 05-final/mapping.md 에 두 표를 쓴다 — (a) 열린 이슈 113건 → 새 항목 ID 목록 (CLOSE 면 사유), (b) 결함 201건 → 새 항목 ID 또는 판정.
6. 보고(10줄 이내): 이관 N건 · 병합 N건 · 신규 항목 N건 · 스크립트 최종 결과 요약.

금지: 코드 수정 · gh 쓰기 · 폴더 밖 파일 생성.
```

## Phase B1 — 범위밖 흡수 (대상 모듈 묶음별 병렬, 각 agent 는 자기 모듈 파일만 수정)

```
notes/new_tickets_claude/ 에서 Phase A 가 다른 모듈로 넘긴 "범위밖" 항목을 대상 모듈 <MODS> 의 목록에 흡수한다. 먼저 00-plan.md 를 읽는다.

입력: 05-final/oos_rows.md — 대상 모듈별로 묶인 범위밖 행 전수. 네 담당은 `## → <MOD>` 절 중 <MODS> 에 해당하는 것과, 대상이 둘 이상(`A/B/C`)이거나 `?` 인 절에서 내용상 <MODS> 몫인 행이다.

할 일 (행마다)
1. 대상 모듈 03-items/<MOD>.md 에 같은 기제의 항목이 있으면 그 항목의 `흡수` 에 원 CID 와 원천 ID 를 덧붙인다. 필요하면 `변경 범위`·`완료 기준` 을 보강한다.
2. 없으면 새 항목을 끝 번호 다음으로 추가한다 (4-2 형식 그대로, 코드에서 좌표 확인).
3. 대상 모듈 02-claims/<MOD>.md 끝에 행을 옮겨 적는다 — CID 는 대상 모듈 번호로 새로 매기고(끝 번호 다음), 판정을 새로 내리고(유효/해소됨/미확인), 비고에 "← <원 CID>" 를 적는다. 원 모듈 파일은 건드리지 않는다.
4. 이미 다른 모듈 항목이 덮고 있어 흡수가 불필요하면 claims 행만 옮기고 비고에 "→ <그 항목 ID> 가 덮음" 을 적는다.
5. 대상이 애매한 행(`?`·복수 대상)은 내용으로 판단해 <MODS> 몫이 아니면 건드리지 않는다.
6. 대응표를 갱신한다.

추가: 결함 BLD-D2 · CON-D3 이 어느 claims 에도 없다 — <MODS> 에 BLD 또는 CON 이 있으면 01-sources/defects/ 에서 찾아 claims 행으로 추가하고 판정한다.

끝나면 `python3 notes/new_tickets_claude/05-final/check_coverage.py` 를 돌려 <MODS> 관련 오류가 없는지 본다. 보고 5줄 이내 — 흡수 N · 신규 항목 N · 덮음 N · 보류 N(사유).

금지: <MODS> 외 모듈의 02-claims/03-items 수정 · 코드 수정 · gh 쓰기 · 폴더 밖 파일 생성.
```

## Phase B2 — 횡단 정합 (단일)

```
notes/new_tickets_claude/ 의 16 모듈 목록(02-claims/*.md · 03-items/*.md, B1 흡수 완료본)을 모듈 간에 정합한다. 먼저 00-plan.md 와 00-progress.md 의 "Phase B 로 넘길 메모" 를 읽고, `python3 notes/new_tickets_claude/05-final/check_coverage.py` 를 돌린다.

할 일
1. 메모의 배정 변경을 적용한다 — #368 주 모듈 LCH→PER(홉별 4건은 DOE/PRE/BLD/RUN/OPT 접점) · #444 PRJ→LCH · #458 RUN→EXE · #281 MOR→CLOSE(잔여 펌핑 2곳은 OPT 항목이 덮는지 확인) · DOE-01/DOE-04 PRJ 재배정 검토 · RUN-22/23 ANA 재배정 검토 · `DashDesignVariableModel` 소속 결정(1-1 표 갱신, 제안: DOE) · "DashMainWindow 레이아웃·프레임 함수군은 UIC" 경계 명시 · 보드 밖 #552 를 EXE 항목에 포함 · #489 커버리지를 각 모듈 items 가 갖는지 확인. 적용 결과를 00-plan.md 6절 배정표에 반영한다.
2. 모듈 간 중복 — 같은 작업이 두 모듈에 항목으로 있으면 변경 파일이 많은 쪽에 남기고 다른 쪽은 삭제, 남긴 쪽 `흡수` 에 합친다. 삭제한 모듈의 대응표 행은 "→ <남긴 항목 ID>" 로 고친다. 후보: 펌핑 제거(#455 vs 모듈), QMessageBox·null 가드 스윕(UIC vs 모듈), 진행 표시 확산(EXE vs 모듈), 상류 핀 ⚠(PRJ vs BLD/RUN/OPT/ANA), Set rename(PRJ vs DOE/RUN/OPT), 산출물 스탬프(PER vs 홉별), #653 버튼(RUN vs OPT).
3. 모듈 간 선행·충돌 — 각 항목의 `선행`·`충돌` 에 다른 모듈 항목 ID 를 보강한다. 같은 파일을 고치는 항목 쌍은 `변경 범위` 교집합으로 계산해 양쪽 `충돌` 에 적는다. 열린 PR 4건(01-sources/open_prs.md)의 파일과 겹치는 항목은 `충돌` 에 PR 번호를 적는다. 결과를 05-final/deps.md 에 표로 쓴다: `| 항목 | 선행 | 충돌(항목) | 충돌(PR) |` + 선행 그래프 순환 여부 + 열린 PR 머지 전 착수 불가 항목 목록.
4. 스크립트를 다시 돌려 열린 이슈 누락 0 · 결함 누락 0 · 존재하지 않는 참조 0 · 범위밖 미흡수 0 이 될 때까지 반복한다.
5. 05-final/mapping.md 에 두 표 — (a) 열린 이슈 113건 + #552 → 새 항목 ID 목록 (CLOSE 면 사유), (b) 결함 201건 → 새 항목 ID 또는 판정(해소됨/미확인 + 근거 CID).
6. 보고(10줄 이내): 배정 변경 N · 병합 N · 신규/삭제 항목 N · 최종 items 수 · 스크립트 최종 결과 요약.

금지: 코드 수정 · gh 쓰기 · 폴더 밖 파일 생성.
```

## Phase C — 모듈별 독립 검토 (실제 사용 프롬프트)

```
DashOpti_GUI 저장소(/Users/minhopark/Projects/DashOpti_GUI, dev @ b08a91b3)에서 모듈 <MOD> 의 작업 목록 초안을 독립 검토한다. 초안을 쓴 쪽과 다른 눈으로 본다 — 원천과 코드를 직접 다시 확인한다. 결과는 notes/new_tickets_claude/04-review/<MOD>.md 에 4-3 형식(| # | 대상 | 지적 | 근거 | 조치 제안 |)으로 쓰고 보고는 10줄 이내로 한다.

절차
1. notes/new_tickets_claude/00-plan.md 를 읽는다 (1절 틀 · 4절 형식 · 6절 배정표).
2. 검토 대상: 02-claims/<MOD>.md 와 03-items/<MOD>.md. 원천: 6절 배정표의 담당 이슈 전문(01-sources/open_issues/)·결함 파일(01-sources/defects/)·위키 Code-Map(01-sources/wiki/)·closed_issues.md·open_prs.md. 05-final/deps.md 의 <MOD> 행도 본다.
3. 다음을 찾는다. 항목 수의 10% 이상은 코드에서 직접 재확인한다.
   a. 누락 — 원천(담당 이슈·결함·접점 이슈가 <MOD> 에 요구하는 것)에 있는데 claims 에 없는 작업
   b. 잔존 — 코드에서 이미 고쳐졌는데 유효로 남은 항목 (git log -S · closed_issues · 현행 코드)
   c. 근거 오류 — 좌표(파일:함수)가 현행 코드와 다르거나 심볼이 없음
   d. 단위 위반 — 한 항목에 기제가 둘, 동작 변경과 리팩터 혼합, 모듈이 둘, L 인데 분할 사유 없음
   e. 완료 기준 부실 — 확인 불가능하거나 비어 있음, 변경 범위가 비어 있음
   f. 선행·충돌 누락 — 같은 파일을 고치는 항목끼리, 열린 PR(01-sources/open_prs.md)과의 충돌
   g. 종류 오분류 — PR 이어야 할 DEC, DEC 이어야 할 PR, 실측 없이 PR 로 둔 INV 성격
   h. 과대·과소 — 실제로는 작업이 아닌 것(설명만), 또는 하나로 묶을 수 있는 잔 항목
4. 지적마다 근거(파일:함수 또는 원천 ID)와 조치 제안을 적는다. 문제 없는 항목은 적지 않는다. 지적이 없으면 "지적 없음" 과 확인한 범위를 적는다.

금지: 03-items·02-claims·05-final 직접 수정 · 코드 수정 · gh 쓰기.
```

## Phase C' — 검토 반영 (실제 사용 프롬프트)

```
notes/new_tickets_claude/04-review/<MOD>.md 의 지적과 05-final/decisions.md(C-2 횡단 결정)의 <MOD> 몫을 02-claims/<MOD>.md · 03-items/<MOD>.md 에 반영한다. 00-plan.md 4절 형식을 유지한다. 분할·병합 지적은 1-2절 "개념적 응집" 기준으로 판단한다 — 개념이 둘이면 나누고, 개념상 하나면 기제가 둘이어도 유지하며 그 지적은 기각한다. 코드로 확인되는 지적은 반영하고, 근거가 약하거나 틀린 지적은 04-review/<MOD>.md 의 해당 행 끝 열에 `기각: 사유` 를 적는다 (열이 없으면 `| 처리 |` 열을 추가). 항목을 삭제하면 결번으로 두고 대응표를 고친다. 다른 모듈 항목을 고쳐야 하는 지적은 반영하지 말고 `보류: <MOD2> 몫` 으로 적는다. 끝나면 `python3 notes/new_tickets_claude/05-final/check_coverage.py` 로 <MOD> 오류 0 을 확인한다. 보고 5줄 이내 — 반영 N · 기각 N · 보류 N · 항목 수 변화.

금지: <MOD> 외 모듈 파일 수정 · 코드 수정 · gh 쓰기.
```
