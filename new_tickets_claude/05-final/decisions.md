# C-2 횡단 결정 (2026-10-06)

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> 검토 16건 중 모듈 반영으로 끝나지 않는 결정. C' 의 각 모듈 agent 는 이 문서를 읽고 자기 모듈 항목을 고친다. 2026-10-06 검토 당시 전건 확정 기록이며, 아래 ②·⑤는 2026-10-08 결정으로 개정했다.

## ① wbpj 배치 경로 사장 여부 — DEC 는 LCH 몫, `LCH-29` 신설

- 근거: 01-sources/wiki/Project-Manifest-CAD-Path-Disposition.md (09-18 "사장·불개입") vs #616 결정표 (10-02 "현행 유지") · PR #651/#652 가 wbpj 를 구현 — 시간순 모순. 입력 포맷 정책(#616)·Journal/Direct 실행 코드가 LCH 소유 (LCH 검토 #1).
- 조치: LCH 가 `LCH-29` DEC 를 신설한다. 선행 등록 — CAD-01 Phase 3 · CAD-02 · CAD-05 · LCH-06 · LCH-27 (LCH-28 은 포맷 무관이라 제외).
- 사장 결정 시 축소: LCH-06 은 Journal TU 삭제에 흡수, LCH-27 은 소멸(동결 시 LCH-19(a) 로 대체). CAD-01/02/05 는 "불개입 경로" 수정분을 뺀다.
- PRJ 회신: **LCH-29 로 동의.** 단 `.wbpj`·`.stli` 원장 편입이 PRJ 코드라 PRJ 를 LCH-29 의 소비자(결정 영향 대상)로 등록한다.

## ② #368 생산·공통 계약 → #685 소비로 분리 (2026-10-08 개정)

- 2026-10-06의 #530 재업로드 결정은 브랜치 처리 이력으로 유지한다. 당시 base 스쿼시·구 파일명 문제는 원천 snapshot에 남아 있다. 기존 hunk는 수정 지점 참고이며 조합 ID·최초 입력 핀 구현을 그대로 이식하지 않는다.
- #520의 기존 Set JSON `setId` 발급·복원·역조회를 사용한다. 현재 Set ID는 유지하면서 기존 선택 UI에서 상류 Set 참조를 바꿀 수 있다. 입력 선택만으로 기존 산출물 출처를 바꾸지 않으며 재실행 결과 덮어쓰기 시 실제 출처도 갱신한다. 전체 이력 보존은 요구하지 않는다.

| 책임 | 항목 | 계약과 선행 |
|---|---|---|
| #368 공통 기록·판독 | PER-06 → PER-07 | 개별 Set·실제 선택·deck 출처, 필수 필드·오류 사유 |
| #368 DOE 생산·스냅샷 전달 | DOE-16 | PER-07 뒤, 조합 ID 생성 없음 |
| #368 Launcher 실행 검증 | LCH-33 | DOE-16 뒤, 다른 유효 DOE 참조 허용 |
| #368 Launcher 결과 XML | PRE-32 | DOE-16 뒤, 실제 run 출처 판독·기록 |
| #368 Builder 생산 완료 | BLD-20 | PRE-32 뒤, Launcher 참조·model_info.json 생성 |
| #685 Runner 소비 | RUN-34 | BLD-20 뒤, Builder setId 참조·검증·실행/조회/프리뷰 |
| #685 Optimizer 소비 | OPT-26 | BLD-20 뒤, 같은 공통 계약·deck 프리뷰. OPT-03·04 흡수 이력 유지 |

- 필수 출처 없는 구산출물은 재생성이 필요하다. 이름·경로 추론, live 정보 fallback, 출처 자동 이관은 금지하며 기존 Set ID 복원은 유지한다.
- 버전·최신성은 #650(PRJ-23 규칙 → 생산 Set 버전 기록 → 소비 Set 판정)에서 별도 구현한다. 프로젝트는 호출·집계, VM은 표시 담당이다.
- 같은 파일을 수정한다는 이유만으로 선행을 추가하지 않는다. #473 결과 오류 수정과 #369 NodeSet 저장은 독립이다. #444는 #441 하위로 비용 검증 후 필요한 경우에만 분리한다. #470은 유지하고 #471 독립 대장 취소도 유지한다.
- #685는 #443 하위이며 #368을 선행으로 한다. #681 머지 조건에는 넣지 않는다. #530의 당시 제외는 OPEN_PRS snapshot 처리 그대로 유지한다.

## ③ 공용 JSON 파일 헬퍼 — 신설 대신 `DashSaveSystem::read/writeJsonFile` 승격

- 사실: `persistence/DashSaveSystem` 의 read/writeJsonFile 이 이미 공용 · QSaveFile · Result 반환 · 테스트를 갖췄다 (PER 검토 #4). PER-02 의 `utils/DashJsonFile` 신설은 중복.
- 조치: PER-02 를 "DashSaveSystem 헬퍼를 공용 진입점으로 승격 + 기존 5벌(`DashDoeTableFile::read` 포함) 치환" 으로 고친다. PER-01 DEC(코덱 층 선택)와 분리 유지.
- 9모듈 이행 항목(DOE-17 CON-11 MOR-22 CAD-13 OPT-24 RUN-32 BLD-17 PRJ-31 등)의 선행은 그대로 PER-02. 각 모듈은 `변경 범위`·`목표` 의 "DashJsonFile" 문구만 "DashSaveSystem 헬퍼" 로 바꾼다.

## ④ PR #655 (#430 · #322 Closes, #654 스택) — 전 모듈 미반영

- 사실: open_prs.md 에는 있으나 claims·items·deps 어디에도 없었다 (MOR·OPT·REN 검토). 파일 71 · 겹침 항목 75 (MOR 17 · PRJ 20 · UIC 10 · CAD 6 · REN 5 · 기타).
- 조치: `items_index.OPEN_PRS` 에 '655' 등록 완료 (선반영). D-1 `build_deps.py --apply` 가 충돌란에 자동 기입하므로 C' 에서 수작업 치환은 불필요. 단 **선행**이 #655 여야 하는 항목은 C' 가 직접 고친다 — MOR-20 · MOR-17 · MOR-02/03/04 (#654 → #655), OPT-22 · OPT-20, UIC-07 · UIC-22 (#655 hunk 가 `setupMorphingBar()` · `DashMorphingSettings.cpp` 본문에 있음). PRJ 는 겹침 20항목이나 선행이어야 할 항목 없음 (PRJ 검토 회신).
- MOR-09(#322) · MOR-15(#430) 는 #655 가 구현 → CLOSE (+ MOR-15 잔여 INV S). MOR-05 는 #655 가 box 경로를 삭제 → DEC 로.

## ⑤ DOE Table 출처를 Launcher 스냅샷으로 전달한다 (2026-10-08 개정)

- DOE-16이 공통 계약의 실제 출처 필드를 DOE Table에 기록하고 `kSnapshotKeys`로 스냅샷에 전달한다. 옛 `parameterizationId`·`derivedId` 및 고정된 두 키 전제는 폐기한다.
- PRE-32는 실행에 사용한 스냅샷·run을 판독·검증하고 결과 XML에 실제 출처를 기록한다. 현재 입력 설정을 재조회하여 과거 결과 출처를 고치지 않는다.
- LCH-33은 Start 직전 선택한 입력과 산출물 출처를 검증한다. 다른 유효 DOE setId의 입력은 허용하며 최초 핀 부재를 통과 근거로 사용하지 않는다.
- 왕복·스냅샷 전달·필수 출처 누락·입력 선택 변경 후 기존 결과 보존·재실행 결과와 출처 동시 갱신을 검증한다. #615 자동 선택·#643 이어쓰기·#646 결과 교체 시점은 추가 개정 계획의 팀 논의로 남긴다.

## ⑥ 보드 밖 OPEN 이슈 #404 — ANA CLOSE, mapping 추가

- 사실: #405 가 선행으로 못박은 #404 가 GitHub 에 OPEN 인데 수집 범위(보드) 밖이라 어디에도 없다. 코드상 해소 (ANA 검토 #1).
- 조치: ANA 가 CLOSE 항목 1건 신설(또는 ANA-02 흡수) + `DashDataLoader.cpp:307` 주석 참조 정리. mapping.md 에 #552 와 같은 방식으로 추가 — `build_mapping.py` 가 이슈 목록을 어디서 읽는지 D-1 에서 확인.

## ⑦ 모듈 간 중복·충돌 (확정)

| 쌍 | 지적 출처 | 판단 | 상태 |
|---|---|---|---|
| CON-03 ↔ PRJ-20 (#645-1 완전 중복) | CON 검토 | **CON-03 에 남기고, 호출 자리를 PRJ-20 안(재로드 후)으로 교정.** PRJ-20 의 CON 헤더 변경은 불필요 — 이미 public 이라 실질 1파일 | 확정 (PRJ 검토 회신) |
| CON-05 ↔ PRJ-08 (`setProjectDirectory` 주입 재설계) | CON 검토 | **별도 DEC 불요 — PRJ-08 이 계약, CON-05 가 선행.** 단 아래 ⑧(공통 베이스 부재)이 PRJ-08 을 막으면 역순 허용. `DashModelRunnerMCU` 2-인자 변종 포함 | 확정 (PRJ 검토 회신) |
| CON-04 ↔ UIC-19 (`GetProject` 가드 둠 vs 삭제) | CON 검토 | **UIC-19 가 맞다 — CON-04 의 가드 신설은 기각.** `GetProject()` 는 ctor 에서 1회 new 하고 재할당이 없다(`DashProjectManager.cpp:26-28,45-48`) → null 가드가 불필요하고, 같은 파일에서 UIC-19 완료 기준을 깬다. CON-04 는 QPointer 2곳만 남긴다 | 확정 (UIC 검토 #2) |
| CON-09 ↔ EXE-21 (FakeRwModule flat 픽스처) | CON 검토 | **EXE-21 에 남김** — 파일 수 2:2 동률이나 공용 픽스처이고 생산 대상 `DashRwDocument` 가 EXE 소관. EXE-21 `흡수` 에 `CON-U5(픽스처 몫 — CON-09 완료 기준 (2))` 명기. CON-09 는 완료 기준 (2) 삭제 · `FakeRwModule.h` 를 변경 범위에서 제외 · `선행: EXE-21` | 확정 (EXE 검토 #7) |
| RUN-24 ↔ UIC-24 (같은 파일, 충돌 미등재) | RUN 검토 | **동의 — 같은 함수(`performPreviewLogic:1448`).** 양쪽 충돌란에 추가하고 순서는 UIC-24 먼저 | 확정 (UIC 검토 #3) |
| RUN-15 ↔ OPT-10 (`SurrogateTableController` 복사본 정리 규칙 불일치) | RUN 검토 | 한 규칙으로 — 공용 controller 는 어느 한 모듈이 맡고 다른 쪽은 선행 | C' 에서 RUN·OPT 가 각자 비고에 합의안 기재, 2차 반영에서 통일 |
| MOR-19 (#427) ← REN 항목 선행 누락 | MOR 검토 | MOR 가 선행 추가 | C' |
| OPT-01 에 `DashRenderingManager` 변경 필수 → REN 직렬 규칙 | OPT 검토 | OPT-01 변경 범위 추가 + REN-10 선행 확인 | C' (REN 2차 반영) |

## C' 운용

- 각 모듈 agent 는 자기 모듈 04-review 지적 + 이 문서의 자기 모듈 몫을 반영한다.
- 타 모듈 몫은 `보류: <MOD> 몫` 으로 남기고, C' 뒤 2차 반영에서 모아 넘긴다.
- 분할·병합 지적은 00-plan.md 1-2 "개념적 응집" 기준 — 개념상 하나면 기각.

## ⑧ Set 모델 공통 베이스 부재 — PRJ-08·09·22 전제 재설계 (PRJ 검토 #1)

- 사실: `DashMvvmModelBase` 의 production 상속자는 0 (tests 7개뿐). Set 모델 9종은 QObject · QAbstractTableModel · QStandardItemModel 로 갈려 공통 베이스가 없다 → 주입 API·가상함수를 둘 자리가 없어 PRJ-08·09·22 의 규모·완료 기준이 성립하지 않는다.
- 조치: PRJ 가 "공통 베이스를 둘지, 둔다면 어느 층에" 를 정하는 DEC 를 선행으로 신설(또는 PRJ-08 을 그 DEC 로 격하)하고, PRJ-09·22 는 그 결정 뒤로 돌린다. CON-05 의 선행 역순 허용(⑦)이 여기에 걸린다.

## ⑨ 보드 밖 OPEN 이슈 — 4건만 편입 (사용자 결정 2026-10-06)

- 사실: 보드(Projects #16)만 수집했기에 GitHub OPEN 138건 중 **26건**이 원천에 없다. 전수는 `01-sources/open_issues_offboard.md`.
- 결정: **검토가 직접 집어낸 4건만 편입**한다 — #552(EXE-02 편입 완료) · #577(MOR-c90 유효, MOR-05 흡수 — 완료) · #404(ANA 몫, ⑥) · #394(PRJ 몫 — `SaveProjectAs` 가 모든 실패를 무시하고 true 반환).
- 나머지 22건은 목록 밖으로 두고 전수 표에만 남긴다. 보드 기준이라는 00-plan 의 원 범위를 유지한다.
- 처리 시점: #404·#394 는 해당 모듈 C' 에서, 늦으면 2차 반영에서.

## ⑩ 열린 PR 스냅샷 재갱신 — #656 · #658 추가, #530 은 대기 대상에서 제외 (2026-10-06)

- `01-sources/open_prs.md` 를 재생성했다 (PR 7건, 파일 목록 포함). 신규 2건:

| PR | base | 내용 | 겹침 항목 |
|---|---|---|---|
| #656 | dev | refactor(model): 런처·초기화기·작성기의 모달 Name·질의 직렬화·TimeSteps 파싱을 공용 함수로 (#433) | 27 — PRE 21 · PRJ 3 · ANA 1 · LCH 1 · UIC 1 |
| #658 | dev (draft) | feat: Registry #82 수용 — preprocessor v3 및 Coupling 소비자 적응 | 42 — PRE 23 · DEV 6 · EXE 3 · PRJ 2 · UIC 2 · 기타 6 |

- `items_index.OPEN_PRS` 를 `('658','656','655','654','652','651')` 로 고쳤다. **#530 을 뺀 것은 의도** — 머지하지 않고 재업로드하므로 "머지 대기" 대상이 아니다 (②). 브랜치 alias 도 갱신했다.
- #656 은 PRE 의 거의 전 항목과 겹친다. PRE C' 가 이미 끝났으므로 **선행**이어야 하는 PRE 항목이 있는지 2차 반영에서 확인한다 (#433 의 후속이므로 PRE-02 의 "#433 종료 검토" 와 직결). 단순 충돌은 D-1 의 `build_deps.py --apply` 가 자동 기입한다.
- #658 은 preprocessor v3 수용이라 PRE·DEV 를 넓게 건드린다. 같은 방식으로 2차 반영에서 선행 여부만 판단한다.
