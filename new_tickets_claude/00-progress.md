# 진행 상태

기준 코드: dev @ b08a91b3 · 시작 2026-10-05

## 준비

- [x] 원천 수집 — open_issues 113 · closed 94 · relations · wiki 스냅샷
- [x] 결함 색인 모듈 분할 (01-sources/defects/) — 201건, prefix 별 건수가 색인 헤더와 일치
- [x] 00-plan.md (틀·형식·과정·배정표) · 00-prompts.md
- [x] 배정 검사 — 열린 이슈 113건 전부 모듈 1개에 배정, 중복 0
- Phase A 착수 2026-10-05 — 16 모듈 병렬
- **중단 1회차**: 11 모듈(MOR CON DOE RUN OPT PRJ REN EXE PER UIC DEV)이 API 세션 한도(429, 리셋 03:30 KST)로 산출물 없이 종료. CAD LCH PRE BLD ANA 는 결과 미수신. 재개 시 00-prompts.md Phase A 템플릿으로 모듈별 재실행 — 02-claims/03-items 에 파일이 있는 모듈은 건너뛴다.

## Phase A (모듈별 수집·검증·항목화)

| MOD | 상태 | claims | items | 비고 |
|---|---|---|---|---|
| MOR | 완료 | 77 (유효34·해소39·범위밖3·CLOSE1) | 21 (PR15·DEC2·INV1·CLOSE3 / S7·M7·L1) | #281 열린 PR 없고 Phase A~E 전부 dev 반영→CLOSE 제안. PR #654(#332)가 MOR 핵심 파일 대부분 변경 — #563·#499·#430·D3·D5·D6·D9 전부 "PR #654 머지 후". #281 잔여 펌핑 2곳→OPT, RW 경합 계측→EXE, #423→PER |
| CAD | 완료 | 38 (유효28·해소3·미확인2·범위밖5) | 11 (PR9·DEC1·EXT1) | #249 는 LCH 의 wbpj 경로 사장 판정과 선행 관계 확정 필요(Phase B). CAD-D2→UIC, CAD-U4·cancel→EXE, OPT-D19→OPT |
| CON | 완료 | 21 (유효13·해소5·범위밖3) | 10 (PR9·DEC1 / S7·M2) | D7 첫 진입 체크 미복원→DV-Condition 덮어쓰기(데이터 손실) 유효. D13→ANA, U5 RW 분해 테스트→EXE, #645 복사 실패 복원→PRJ |
| DOE | 완료 | 51 (유효20·해소5·미확인1·CLOSE1·범위밖24) | 15 (PR13·DEC1·CLOSE1 / S6·M7) | #615→3건 분리. DOE-D7~D19·D21·D23·D24·U2~U5→LCH. QMessageBox 29·null 가드 44→UIC. 미확인: Resample 동기 샘플링 실측 필요 |
| LCH | 완료 | 63 (유효38·해소11·미확인1·범위밖11·CLOSE2) | 26 (PR15·DEC2·INV1·EXT1·CLOSE7 / S10·M4·L1) | #604→PR #652, #616→PR #651 전부 흡수. #456 은 해소됨(코루틴·모핑 서비스)→CLOSE. 신규: JSON 에만 쓰고 시그널 미방출 16곳이 #580 과 같은 stall 기제(LCH-02). DOE-D1~D5·D25·D26·U5→DOE |
| PRE | 완료 | 75 (유효55·해소11·범위밖6·미확인3) | 31 (PR24·DEC3·INV4 / S11·M12·L1) | 펌핑 실측 23곳(런처8·처리기8·KPI7). 신규 bug 2건 발견(Motion 판정 basename 입력 PRE-07 · 작성기 operator 폴백 PRE-06). 범위밖: 3ff07ff(EXT), 다중 part 포맷(BLD/EXT), XmlParser 전환(ANA), vtkIOHDF(DEV), 버전 키(PER) |
| BLD | 완료 | 31 (유효28·해소1·범위밖2) | 16 (PR14·DEC1·INV1 / S10·M6) | #368 BLD 몫(T22)은 feat/pipeline-deck-stamp 에 전부 있어 항목 없음. BLD-D1→PRJ(3벌 variant 구조 공통), QMessageBox 23곳→UIC |
| RUN | 완료 | 56 (유효39·해소8·범위밖7·CLOSE2) | 30 (PR27·DEC1·CLOSE2 / S20·M7) | #369→CLOSE(G10 범위 밖 확정, 잔여는 DEC RUN-03). #458→EXE(RW 액터 GUI 스레드 고정). #474 DOE-D8→LCH, BLD-D10→BLD, RUN-D15→CAD, RUN-D22→UIC |
| ANA | 완료 | 30 (유효21·해소6·범위밖3) | 17 (PR16·DEC1 / S10·M5·L1) | #459 는 DEC(MCU SHAP 지원 결정 선행). #519 분리 사유 소멸. ANA-c08→MOR, c29(#553)→EXE, c30(#411)→PRE |
| OPT | 완료 | 37 (유효30·해소3·범위밖4) | 21 (PR20·DEC1 / S19·M2) | #316→OPT-01(비파괴 오버레이)+OPT-02(산출물 위치 DEC). #457 펌핑 2건, EXE 선행 불요. OPT-D19→CAD, OPT-D20→ANA, .stp 덮어쓰기→CAD |
| PRJ | 완료 | 58 (유효34·해소9·미확인1·범위밖11·CLOSE3) | 30 (PR21·DEC5·CLOSE4 / S16·M9·L1) | #376·#434 4단계·#562-2/4·setId SI-1~4 해소됨. #485 는 SaveProject no-op 이라 실측 선행(DEC). 신규 2건: Save 메뉴 no-op 성공 보고, Save As 가 .dproj 만 복사. #444→LCH, #562-3→DOE, #650 모듈별 핀→BLD·RUN·OPT·ANA |
| REN | 완료 | 33 (유효25·범위밖8) | 12 (PR10·DEC2 / S7·M3) | #318 덮어쓰기 12곳 전부 현존 + addMorphingPreviewActor 1곳 추가(13). #319 4건 전부 유효. 구성: 파일럿 4 → 결정 → 소유자 태그 → 숨김 정책. c17→CAD, c19→OPT, #322·#430·renderer 직접 조작→MOR, RUN-D14·D25→RUN |
| EXE | 완료 | 54 (유효26·해소8·범위밖15·CLOSE3·정보2) | 20 (PR8·DEC6·CLOSE6 / S6·M2) | processEvents 실호출 49(model 37·view 12), 보존 21·본선 28. #451 "WorkerJob 부재" 는 #544 로 절반 해소. #467 기동 타임아웃·#468·#469 해소됨→CLOSE. 단일 슬롯 거부 정책(EXE-01 DEC)이 #454/#456/#513 선행 |
| PER | 완료 | 30 (유효13·해소1·미확인1·범위밖14·CLOSE1) | 9 (DEC3·PR5·CLOSE1 / S5·M4) | 코덱 층 2종(DashGadgetCodec·DashSaveSystem) 모두 소비자 0. JSON I/O 헬퍼 5벌 중복. QSaveFile 8지점 vs 직쓰기 22지점/14파일. parameterizationId dev 0건. 직쓰기 헬퍼 이행 9모듈→각 모듈, #638→PRE, #444·SI-6a→PRJ, #473→RUN |
| UIC | 완료 | 58 (유효42·해소3·미확인1·범위밖11·CLOSE1) | 25 (PR17·DEC6·INV1·CLOSE1 / S7·M8·L2) | 현행 Qt6 — DPI L0-3 소멸, R1~R5 는 현재 결함. 실측: QMessageBox 166 · tr 182 · Instance 가드 116 · setFixed* 74 · ResizeToContents 82 · saveGeometry/QValidator/QUndoStack 0. #514 ①④ 해소, ②③⑤ 유효. L 2건은 기계적 단일 치환 |
| DEV | 완료 | 37 (유효25·해소5·미확인5·범위밖2) | 24 (PR13·DEC5·EXT5·INV1 / S13·M5) | CI 부재(.github 0건)→#372 는 DEC→워크플로→측정 3단. 만료 상수 2026-08-31 경과(표시 전용). About Build Date 항상 "어제" 버그. #489 도메인 커버리지→각 모듈 |

## Phase B (횡단 정합)

- [ ] B1 범위밖 흡수 (5 묶음 병렬: ①LCH·DOE ②OPT·CAD·MOR ③ANA·RUN·BLD ④EXE·UIC·PRE·PRJ ⑤CON·PER·REN·DEV) — 입력 05-final/oos_rows.md 127행
- [x] B1 범위밖 흡수 완료 (5 묶음)
- [x] B2 완료 — 배정 변경 6 · 병합 4(BLD-08→UIC-23 · UIC-04→PRJ-14 · DOE-04→PRJ-24 · CON-08→DOE-10) · 신규 1(DOE-01→PRJ-33) · DashDesignVariableModel→DOE. deps.md(build_deps.py · items_index.py): 순환 0 · PR 대기 217(선행 명시 43 · 파일 겹침 174) · 즉시 착수 92. mapping.md(build_mapping.py): 이슈 114→항목 88·CLOSE 19·CLOSE+잔여 7, 결함 201→항목 160·CID 경유 8·CLOSE 2·해소/범위밖 31.
- B2 후 집계: claims 908 · items 346 (PR 260 · DEC 43 · INV 11 · EXT 7 · CLOSE 25)

## Phase C (검토 · 반영)

| MOD | 검토 | 반영 |
|---|---|---|
| MOR | 완료 (지적 20) | 완료 (반영 20·기각 0·보류 0 / 22→23) |
| CAD | 완료 (지적 16) | 완료 (반영 12·기각 3·보류 1 / 14→15) |
| CON | 완료 (지적 16) | 완료 (반영 14·기각 1·보류 1 / 10→11) |
| DOE | 완료 (지적 11) | 완료 (반영 10·기각 1·보류 2 / 16 유지) |
| LCH | 완료 (지적 10) | 완료 (반영 10·기각 0·보류 3 / 28→32) |
| PRE | 완료 (지적 18) | 완료 (반영 13·기각 4·보류 6 / 32 유지) |
| BLD | 완료 (지적 11) | 완료 (반영 11·기각 0·보류 3 / 18→19) |
| RUN | 완료 (지적 12) | 완료 (반영 11·기각 1·보류 2 / 32→33) |
| ANA | 완료 (지적 9) | 완료 (반영 8·기각 1·보류 0 / 22→23) |
| OPT | 완료 (지적 11) | 완료 (반영 11·기각 0·보류 2 / 25→24) |
| PRJ | 완료 (지적 20) | 완료 (반영 16·기각 4·보류 4 / 33→36) |
| REN | 완료 (지적 13) | 완료 (반영 13·기각 1·보류 0 / 13 유지) |
| EXE | 완료 (지적 13) | 완료 (반영 13·기각 1·보류 1 / 22 유지) |
| PER | 완료 (지적 14) | 완료 (반영 14·기각 0·보류 5 / 10→11) |
| UIC | 완료 (지적 16) | 완료 (반영 16·기각 0·보류 4 / 24→25) |
| DEV | 완료 (지적 12) | 완료 (반영 11·기각 1·보류 0 / 25→24) |

## Phase D

- [ ] 05-final/FINAL.md — `python3 05-final/build_final.py` 로 조립 (03-items + deps + mapping)

## Phase B 로 넘길 메모 (subagent 보고에서 추출)

- CAD: #249(NX 파사드 태그 왕복) 와 LCH 의 wbpj 배치 경로 사장 판정(Project-Manifest-CAD-Path-Disposition) 순서 확정 — 경로 제거가 먼저면 CAD-01 축소. 충돌 PR #651 #652 #654 #530.
- ANA: `gh pr list` 가 저장소 해석 실패로 미실행 — 진행 중 PR 충돌(#553 #433)은 배정표 기준. Phase B 에서 `gh pr list --repo NumeRealWorks/DashOpti_GUI` 로 보강. ANA-16(#305) L 1건은 분할 불가 사유 기재됨.
- BLD: #643·#650 BLD 몫(BLD-14·15)은 PRE 의 XML Set 단위 id 선행, ⚠ 쌍 등록은 PRJ. #643 제약 "DeepOpt 는 root 첫 자식만 읽음" 을 PRE 로 전달. DashModelBuilder.h/.cpp 7개 항목이 feat/pipeline-deck-stamp 와 충돌. `gh` 저장소 해석 실패(404) 재발 — Phase B 에서 `--repo` 명시.
- PRE: In review `feat/pipeline-deck-stamp`(#368, dev 보다 40커밋 뒤)가 DashAnalysisLauncher.cpp·DashResultXmlWriter.cpp 를 고침 — PRE 항목 다수와 충돌. PRE-15 는 LCH 호출부 서명 변경 동반. 미확인 3건은 실측 파일(fe-safe ODB ≥2023 · 모달 rst/odb · Motion dfr · sideforce.rst) 부재. PRE-U1 `.op2` 목록 삭제는 LCH·UIC 접점.
- LCH: **#368 주 모듈을 PER 로 변경 제안** (횡단 스탬프, LCH 자체 작업 0, PR #530 은 `feat/reference-model-manifest` base·구 파일명이라 dev 리베이스 필요). T27→DOE · T21→PRE · T22→BLD(브랜치에 있음) · T23→RUN·OPT 로 분배. #648 은 fe-safe 환경 실측 필요(INV).
- CON: `model/DashDesignVariableModel` 이 1-1 모듈 표에 없음 — CON·CAD·MOR·DOE 공용. Phase B 에서 소속 결정 (제안: PRJ 또는 PER). Set 모델 공통 `setProjectDirectory(path)` 계약은 PRJ DEC 후보. 열린 PR 3건이 DashMainWindow.cpp 를 건드려 CON-03/05/06 과 충돌.
- gh: 활성 계정 minhopark-lgtm, 보조 계정 minhopark1271. 일부 subagent 가 저장소 접근 실패를 보고 — `--repo` 명시로 해결됨 (01-sources/open_prs.md 참조).
- DOE: DOE-01·DOE-04 는 변경 파일이 전부 PRJ 소유(DashProjectWidget·DashProject·DashMainWindow) — Phase B 에서 PRJ 재배정 검토. `DashDesignVariableModel` 소속은 DOE 가 제안 (CON 도 요청) — 한 곳으로 결정. PR 충돌: #652(DashDoeSampler) · #530(DoeConfigManager·DoeSelection) · #651/#654(MainWindow·Project).
- OPT: OPT-01 이 #318(REN) 의 선행·파일럿 — REN deps 에 반영. PER 접점: OPT-15(저장 키)·OPT-02. OPT-21(#653 버튼)은 PR #652 + RUN/LCH prefill 진입점 선행.
- REN: OPT-01(#316)이 REN-10 선행 — deps 에 OPT→REN 기록. DashMainWindow·DashManager 를 만지는 REN 5건은 열린 PR 3건 랜딩 뒤 착수. 자동 테스트가 updateActor/resetCamera 를 덮지 않아 완료 기준이 수동 회귀 중심.
- DEV: #489 를 "DEV = 인프라(grep 게이트·등록 헬퍼), 커버리지 = 각 모듈" 로 분할 — 각 모듈 items 에 테스트 항목이 있는지 Phase B 에서 확인. CI 구축은 원천 이슈 없음 → #372 비고 또는 신규. 타임아웃 상수화 중 프로세스 대기 8곳은 EXE. DEV-10·19 는 PR #654/#651/#652 머지 후.
- MOR: #281 을 MOR 담당에서 빼고 OPT 접점으로 (잔여가 OPT 파일뿐 — OPT-03/04 와 동일 지점, Phase B 에서 흡수 확인). #331-3(MarchingPlaneBound 상류 환원)은 #499-2 로 대체. MOR-15(#430 interaction 핸들 소유 해제) L — PR #654 머지 후 2분할 가능. #577 은 보드 밖 이슈라 미반영.
- RUN: #458 담당을 EXE 로. RUN-22·23(D29·D30)은 변경 파일이 ANA 영역(DashResultsAnalyzerWidget) — Phase B 에서 ANA 재배정 검토. PR #530·#654 가 getReferenceFileAndPart·loadModelInfoFromFolder·performMorphing 을 만져 RUN-14·25·27 은 머지 후.
- PER: #368 주 모듈 LCH→PER 로 확정(PER-06·07 공통부, 홉별 4건은 DOE/PRE/BLD/RUN/OPT 접점) — LCH 보고와 일치. #471 은 PER-06 결정 결과에 따라 CLOSE 가능. 왕복 단절 28건 부록 A 표를 Phase B 에서 모듈 claims 와 대조.
- UIC: DashMainWindow 를 고치는 창 항목 6건이 PRJ 소유 파일과 겹침 — Phase B 에서 "DashMainWindow 레이아웃·프레임 함수군은 UIC" 경계 명시 또는 PRJ 접점. R1→CAD, R2~R4·L3-3→ANA, R5→OPT, DOE-U2→LCH. QMessageBox·setFixed* 모듈 스윕은 규칙 DEC 후 모듈별(건수표 포함). UIC-18·20 은 PR 머지 후.
- EXE: 보드 밖 OPEN 이슈 #552(DashAsyncJobContext 취소 불가, #553 선행)를 EXE 담당으로 추가 — Phase B 에서 mapping 에 포함. docs/ThreadingContract.md 는 헤더가 참조하나 파일 없음. CAD-U4→EXE-12 흡수. #463 확산은 각 모듈 items 에 진행 표시 항목이 있는지 확인.
- PRJ: #434 잔여 실측 — PrjMgr 71/6파일, 렌더 접근자 113/14파일(PRJ 41·MOR 54), 프로세스·설정 소비 38/15파일 — MOR 호출부 54건·소비자 38건은 Phase B 재배정. #432 model/ Instance() 112/14파일. #444 를 LCH 담당으로(#441 과 한 설계).

## Phase A 완료 (2026-10-05)

합계 claims 749 · items 318. check_coverage.py: 열린 이슈 누락 0 · 결함 claims 누락 2 (BLD-D2 CON-D3) · 참조 오류 0 · 범위밖 이관 50건(대상 모듈 미파싱 44 포함).

## Phase B1 진행

- ⑤ CON·PER·REN·DEV 완료 — 흡수 5 · 신규 4(CON-11 PER-10 REN-13 DEV-25) · 보류 2(PRE-c23·EXE-c45 EXT, 원 모듈 추적). CON-D3 누락은 셀 내 `\|` 가 열을 밀어 생긴 파서 문제 — REN·DEV 에서도 같은 깨짐 정정. #368→PER 반영(PER-06·07 본체).
- ① LCH·DOE 완료 — 흡수 32 · 신규 5(LCH-27·28 DOE-16·17·18) · 해소 8 · 보류 6(타 모듈 몫). #444 는 LCH-08 에 "B2 배정 확정 조건" 으로 준비. 복수 대상 행 5건(UIC-c56·EXE-c42·EXE-c46→LCH, EXE-c41·DEV-c24→DOE)의 LCH·DOE 몫 흡수 — B2 에서 다른 묶음과 중복 흡수 여부 확인.
- ④ EXE·UIC·PRE·PRJ 완료 — 흡수 16 · 신규 5(EXE-21·22 PRE-32 PRJ-31·32) · 덮음 1 · 보류 1(#444→LCH 대응표 갱신). #552→EXE-02 일치. UIC 머리말에 DashMainWindow 경계 명시, PRJ-03/04/11/14 충돌에 UIC 추가 — **PRJ-14 와 UIC-04 는 같은 결정 → B2 병합 후보**. #458 담당 RUN→EXE 반영(EXE-22).
- ② OPT·CAD·MOR 완료 — 흡수 28 · 신규 8(OPT-22~25 CAD-12~14 MOR-22) · 덮음 5 · 보류 1(PER-c22 `DashDesignVariableModel::saveToJsonFiles` — 소속 결정 뒤 CON-08·DOE-10 중 하나로, B2). #281-D→OPT-04, OPT-D19→CAD-01 본체.
- ③ ANA·RUN·BLD 완료 — 흡수 15 · 신규 11(ANA-18~22 RUN-31~33 BLD-17~19) · 보류 4(미확인). RUN-23→ANA-18 이관, RUN-22 축소. **B2 지적: BLD-08↔UIC-23 중복, CAD-01 흡수에 RUN-D15 누락(②는 등재했다고 보고 — 확인), PER 부록 A "RUN 미작성" 낡음.**
- B1 완료. check_coverage 결과는 아래.

### B1 완료 집계 (check_coverage)

claims 908 · items 350 · 이슈 누락 0 · 결함 누락 0 · 참조 오류 0 · 범위밖 흡수 123 / 미흡수 3 (PRJ-c60 #444→LCH 는 B2 배정 확정 대기 · PRE-c23 · EXE-c45 는 EXT 로 원 모듈 추적).

### B2 입력 메모 (B1 보고에서 추출)

- 중복·병합 후보: BLD-08↔UIC-23(같은 함수 같은 방식) · PRJ-14↔UIC-04(같은 결정) · 복수 대상 행 5건(UIC-c56 EXE-c42 EXE-c46 EXE-c41 DEV-c24)이 두 묶음에 중복 흡수됐는지
- 확인: CAD-01 흡수에 RUN-D15 등재 여부(②는 등재, ③은 누락 보고) · PER 부록 A "RUN 미작성" 갱신
- 결정: `DashDesignVariableModel` 소속(CON-08·DOE-10 이 같은 파일, PER-c22 보류분 헬퍼 항목 귀속) · #444 PRJ→LCH 확정(LCH-08 흡수)

## Phase C

- **중단 2회차** (2026-10-05 밤): 검토 16개 전부 API 세션 한도(429, 리셋 02:50 KST)로 산출물 없이 종료. 2026-10-06 재실행 — 04-review/<MOD>.md 가 있는 모듈은 건너뛴다.
- **중단 3회차** (2026-10-06): 재실행 16개 전부 Fable 한도(429)로 산출물 없이 종료. 계정 전환 후 재실행.
- C: CON 검토 완료 — 설계 오류 1(CON-03 훅 위치) · PRJ-20 과 중복 · 모듈 간 충돌 3(PRJ-08 UIC-19 EXE-21) · 누락 2 · 신규 PR #655 미반영. open_prs.md 갱신(2026-10-06).
- C: CAD 검토 완료 — **wbpj 경로 사장 판정 DEC 가 어느 모듈에도 없음**(LCH 또는 PRJ 신설 후 CAD-01 선행 등록) · 누락 4 · 분할 제안 3(CAD-02/03/07) · CAD-11(TU) 순환 선행 · NX 게이트 분리 표기 · 중복 2.
- C: REN 검토 완료 — 직접 renderer 조작 재집계 오류(controller 7→21) · PR #655(#430, #654 스택) 충돌 미반영(open_prs.md 는 갱신됨) · REN-04 축소 · REN-07/10 설계 모순(소유자·takeOver 분리) · 완료 기준 부실 4.
- C: PER 검토 완료 — **횡단 결정 2**: ⑴ PR #530(#368) 처분 노선 통일(재업로드 vs 그대로 — base 스쿼시·구 파일명이라 현 상태 머지 불가, 9건이 선행으로 걸림) ⑵ DashSaveSystem::read/writeJsonFile 이 이미 공용 헬퍼 — PER-02 새 utils/DashJsonFile 신설 대신 그것 채택 검토. PER-06 ① 스탬프 소비자 0(DOE-16·PRE-32 보강). deps 가 괄호 안 ID 를 선행으로 오독(build_deps.py 수정).
- **중단 4회차** (2026-10-06): 3차 재실행 중 12 모듈(DOE OPT BLD ANA MOR LCH PRE RUN PRJ EXE + 미착수 UIC DEV)이 세션 한도(429, 리셋 12:50 KST)로 종료. 완료 4(CON CAD PER REN). **인수인계 문서 00-HANDOFF.md 작성 — 새 세션은 그 문서부터.**
- **재개 5회차** (2026-10-06, 새 세션): 00-HANDOFF.md 기준 C-1 착수. 묶음 1 = MOR DOE LCH PRE (4개 병렬), 완료 후 묶음 2 = BLD RUN ANA OPT, 묶음 3 = PRJ EXE UIC DEV. 각 프롬프트에 HANDOFF 3절 "검토가 넘긴 질문" 을 덧붙임.
- D-1 선반영 (묶음 1 대기 중): `items_index.py` — ① `선행:` 괄호 안 ID 제외(`strip_parens`, 중첩 포함). 영향 5건 PRE-14·RUN-09·PER-10·DEV-02·DEV-18 전부 `선행: -` 뒤 괄호 설명의 오독 → 선행 없음으로 정정. ② `OPEN_PRS` 에 '655' 추가 + 브랜치 alias. open_prs.md 파싱 #655 파일 71. #655 와 파일 겹침 항목 75(MOR 17 · PRJ 20 · UIC 10 · CAD 6 · REN 5 · 기타). deps.md 재생성은 C' 뒤.
- C: MOR 검토 완료 — **PR #655(#430·#322 Closes) 가 claims·items·deps 어디에도 없음**, MOR 16건이 같은 파일. MOR-09(#322)·MOR-15(#430) → #655 가 구현 → CLOSE(+잔여 INV). MOR-05 는 #655 가 box 경로 삭제 → DEC 로. MOR-20·17·02/03/04 선행은 #654 아닌 #655. MOR-22·11·12 근거 갱신. REN 재집계(controller 21 + DashGizmo 10) 맞음 — MOR 쪽 고칠 건수 없음.
- C: DOE 검토 완료 — PER-06 ① 확인: `kSnapshotKeys`(DashAnalysisLauncherConfig.cpp:226) 14키에 스탬프 키 없음 → DOE-16 에 스냅샷 전파 완료 기준·2키 추가 제안, PRE-32 몫은 보류. DOE-16 근거 오류(Resample 은 `m_parameterization` 미사용 → PR #530 식 참조 Table 복사로). DOE-07·16·17 테스트 불가(tests/ Qt Core only, ProjectManager 의존). DOE-14 DEC 쟁점 틀림(`samples` 매핑값 vs `rawSamples` 원시값). 누락 없음.
- C: LCH 검토 완료 — **wbpj 경로 DEC 는 LCH 몫**(입력 포맷 정책 #616·Journal/Direct 실행 코드 소유). 매니페스트 "사장·불개입"(09-18) vs #616 결정표 "현행 유지"(10-02)·PR #651/#652 wbpj 구현이 시간순 모순 → LCH-29 DEC 신설 제안, CAD-01·LCH-06·LCH-27 선행 등록. 시그널 없는 JSON 기록 16→18곳(Mechanical Running 2곳 누락). LCH-15 기제 오류(동명 재생성 미탐지). #648 PR 항목 신설(LCH-30) · MBD CLI 계약 DEC(LCH-31) · #444 DEC 분리(LCH-32) 제안.
- C: PRE 검토 완료 — PER-06 ① 회신: PRE-32 를 `derivedId` 재계산 → 스냅샷 스탬프 소비로, `kSnapshotKeys` 확장을 PRE-32 범위에 포함(DOE 검토는 DOE-16 범위로 제안 — C' 에서 한쪽으로 정리), 선행 DOE-16. #617 이후 "다른 조합 run 폴더 차단" 기준 재현 불가 → 검증 지점 재정의. **9개 항목이 `feat/pipeline-deck-stamp` 충돌 대기 → #530 머지 불가라 충돌 제거 제안**(C-2 ② 와 연동). PRE-04·16·18 분할, 선행 과대 4건, DeepOpt 제약 누락 1.
- C-2 ② 메모: DOE·PRE 양쪽이 `kSnapshotKeys` 확장을 각자 범위로 제안 — 같은 파일(DashAnalysisLauncherConfig.cpp) 한 곳이므로 C' 전 한 모듈로 귀속 결정 필요. 제안: DOE-16(스탬프 기록 측)이 allowlist 를 넓히고, PRE-32 는 읽기만.
- 묶음 2 중단 (사용자 지시): BLD RUN ANA OPT 4개 정지, 산출물 없음. **이후 검토 subagent 는 model=opus 로 실행** (동시 4개 유지).
- 기준 보정 (사용자 지시 2026-10-06): 분할은 엄밀한 1기제가 아니라 **개념적 응집** 기준. 00-plan.md 1-2 · 00-prompts.md C' 템플릿에 반영, 실행 중 검토 4개(BLD RUN ANA OPT)에 전달. 끝난 8개 검토는 재검토하지 않음 (사용자 지시) — C' 가 반영 여부를 정할 때만 이 기준을 적용.
- C: BLD 검토 완료 (opus) — PER 인계 답: `gh pr diff 530` 으로 T22 실물 확인, BLD 4파일은 dev 파일명과 일치하나 PR 전체는 T21·T27 이 구 `DashDataProcessor*` 를 고쳐 머지 불가(merge-base NO). **재업로드 노선에서 PRE-32·DOE-16 은 있는데 BLD 홉만 없음 → BLD-20(T22) 신설 제안**, mapping.md:25 가 누락을 굳힘. 선행 치환 BLD-13·14·15·17·18 — BLD-13 은 역전(`loadLabelMetadata` 삭제라 BLD-20 이 뒤). BLD-05 완료 기준 좌표 오류, BLD-15 변경 범위 `DashProject.cpp` 모순, DeepOpt 복수 응답 제약 누락.
- C-2 ② 메모 추가: BLD 검토는 "PER-07 흡수" 가 아니라 **홉별 항목 신설(BLD-20)** 을 제안 — HANDOFF 4절 ② 의 "별도 신설 불요" 와 다름. RUN·OPT 검토 결과를 보고 C-2 에서 노선 통일 (PER-07 = 공통부 + 홉별 항목 4건(DOE-16·PRE-32·BLD-20·RUN/OPT) 구조가 유력).
- C: RUN 검토 완료 (opus) — PER 인계 답: T23 RUN 몫은 #530 에 실재(`DashModelRunner.cpp` +61 · `.h` +6 · `Widget.cpp` +9, 셋 다 dev 파일명 일치 → hunk 이식 가능). **"PER-07 흡수" 는 전제 오류** — PER-07 변경 범위는 `DashPipelineStamp.h`·`DashDoeSelection`·테스트뿐이고 본문이 "홉별 핀·검증은 RUN·OPT 항목이 한다" 고 명시 → **RUN-34 신설 필요**(원본 커밋 0bbcc9c6). 선행 치환 RUN-14·25·27·31. 기타: RUN-18 토큰 치환 전제 반대, RUN-15 `SurrogateTableController` 복사본 누락·OPT-10 과 규칙 불일치, RUN-07+08 병합, RUN-D1 전 모듈 누락, RUN-24↔UIC-24 충돌 미등재.
- C-2 ② 확정 방향: BLD·RUN 검토가 일치 — PER-07 은 공통부(스탬프 타입·DoeSelection·테스트)만이고 홉별 항목은 모듈마다 신설(DOE-16 · PRE-32 기존, BLD-20 · RUN-34 신설, OPT 는 OPT 검토 대기). "PR #530 머지" 선행은 전부 "PER-07 + 해당 홉 항목" 으로 치환. HANDOFF 4절 ② 의 "별도 신설 불요" 는 폐기.
- C: OPT 검토 완료 (opus) — **#368 T23 이 OPT claims/items/대응표에 전무** → OPT-26(T23) 신설 필요. PER 회답: T23 OPT 몫은 #530 에 실재(`pinnedParameterizationId`·`modelInfoBlocked` 등), "PER-07 흡수" 는 틀림(PER-07 목표가 T21~T23 명시 제외). `선행: PR #530 머지` 항목은 0건, 충돌란 `#530` 24건 → `OPT-26` 로 치환. REN 회답: #655 누락 OPT-22(DashMainWindow)·OPT-20(tests/CMakeLists). deps.md 전체 #655 0건. OPT-03↔#368 D20 충돌·OPT-04 pE 2곳은 #530 이 제거 → OPT-03+04 병합 또는 OPT-26 흡수. OPT-01 에 `DashRenderingManager` 변경 필수(변경 범위·REN 직렬 규칙 누락). OPT-16 근거 오류.
- C-2 ② 홉 항목 확정: DOE-16 (T27) · PRE-32 (T21) · BLD-20 신설 (T22) · RUN-34 신설 (T23 Runner) · OPT-26 신설 (T23 Optimizer). 공통부 PER-07.
- C: ANA 검토 완료 (opus) — **보드 밖 OPEN 이슈 #404**(#405 의 선행)가 어디에도 없음 — 코드상 해소라 CLOSE 제안(mapping 에 추가 필요, #552 와 같은 처리). ANA-05 "Runner Sim/MCU 100ms 창 공유" 무효(MCU 가 `set + "-MCU"` 키). ANA-06 #650 몫 완료 기준 없음. ANA-09 좌표 오류(:1461·:1680 산 함수 안, :624 추가). ANA-13↔ANA-19 선행 미등재. ANA-16 L 분할 불가 사유 타당, `DashParallelPlotter.h` 변경 범위 누락. 잔존 없음.
- C-2 초안: `05-final/decisions.md` 작성 — ① LCH-29(PRJ 회신 대기) ② #530 재업로드 + 홉 5건(선행 9건·충돌 89건 치환 규칙, OPEN_PRS 에서 530 제거는 D-1) ③ PER-02 DashSaveSystem 승격 ④ #655 ⑤ kSnapshotKeys→DOE-16 ⑥ #404 ANA CLOSE ⑦ 모듈 간 쌍 8건(PRJ·EXE·UIC 회신 대기). C' 템플릿이 decisions.md 를 읽도록 갱신.
- **중단 5회차** (2026-10-06 14시경): PRJ UIC DEV EXE 4개가 세션 한도(429, 리셋 14:30 KST)로 산출물 없이 종료. 완료 12/16. 계정 전환 후 같은 프롬프트로 재실행.
- C: DEV 검토 완료 (opus) — **DEV-11 오판정**: #336-3 차단 조건 해제(로컬 CMake 4.3.3 `InstallRequiredSystemLibraries.cmake:252-254` 가 v145, `:610-621` 이 vcomp140.dll 처리) → `미확인`/INV → `유효`/PR, `cmake_minimum_required(3.25)` 범프 동반. DEV-19 과대(54 등록 비동형·가드 24블록 상이, S 아님, 완료 기준 2 와 "동작 불변" 모순, 선례 `:921 cmake_language(DEFER)`). DEV-24/21 변경 범위 README.md 누락 → 완료 기준 통과 불가. 누락 `tests/e2e`(DEV-14/15). DEV-09→DEV-12 병합 권고. #372 3단 분할 타당. 열린 PR "4건" 표기 → 5건(#655 가 `tests/CMakeLists.txt`·`docs/test-levels.md` 등 변경, DEV-10·13·19 충돌 누락).
- DEV 검토 #5 `deps.md` 선행 오파싱 지적(`선행: - (DEV-01 과 무관)` 을 선행으로 읽음)은 **이미 수정됨** — 본 세션 D-1 선반영 `items_index.strip_parens`. DEV-02·18 포함 5건이 그 수정 대상이었다. C' 에서 기각 처리.
- C: EXE 검토 완료 (opus) — Phase A 집계 전부 코드와 일치 확인(processEvents 49호출 · 보존 21 · 본선 28 · #467/#468/#469 CLOSE 근거 · ThreadingContract.md 부재). **#512 서술이 원천과 반대** — c04 비고·대응표가 "남은 1곳은 processEvents 아님" 이라 했으나 #512 본문이 `DashMeshQualityDialog.cpp:164` 를 잔여로 못 박음(소관 #455 오기, 실제 MOR-01 이 흡수). 좌표 오류 2(RW assert 는 `instance()` 아닌 생성자 :98 · flat 분해는 코루틴 `readFeCondition` :518). 종류 오분류 2(EXE-12 DEC→PR, EXE-14 →INV). EXE-09 가 `controller/async` 에 QAbstractButton 유입 → 층 경계 위반 + `test_async_job` Widgets 미링크로 완료 기준 성립 불가. 215-2 4·7절 미흡수. #655 누락(EXE-08·09·22).
- C-2 ⑦ EXE 행 확정: CON-09 ↔ EXE-21 → **EXE-21 에 남김** (공용 픽스처 · 생산 대상 `DashRwDocument` 가 EXE 소관). CON-09 는 완료 기준 (2) 삭제 · `FakeRwModule.h` 제외 · 선행 EXE-21.
- C: PRJ 검토 완료 (opus) — **PRJ-08·09·22 전제 오류**: `DashMvvmModelBase` production 상속자 0(tests 7뿐), Set 모델 9종이 QObject/QAbstractTableModel/QStandardItemModel 로 갈려 공통 베이스 없음 → 주입 API 자리 없음(decisions ⑧ 신설). 누락 3: Save As 가 Set 모델·트리 전멸(`SaveProjectAs`→`SetProjectDirectory`→`clearAllSets`, 복원·unbind 없음) · 보드 밖 OPEN #394(자기 덮어쓰기 소실) · 카테고리 루트 개명 가능(`setEditable(true)` + 복원 가드 `UserRole` 미설정 → Set rename/delete/Add 조용히 실패). 기타: 246-1 2단계 주입 무항목 · MCU Builder `m_currentJob` 부재 · #650 Run-완료 트리거 · variant 검출기 4벌 중 1벌 근거 · DashManager 좌표 드리프트 · `setupMenus` 심볼 부재 · c12 인과 오류.
- C-2 확정 (PRJ 회신): ⑦ CON-03↔PRJ-20 → CON-03 에 남기고 호출 자리를 PRJ-20 안으로 교정 · CON-05↔PRJ-08 → PRJ-08 계약, CON-05 선행(⑧ 걸리면 역순 허용) · ① wbpj DEC → LCH-29 동의, PRJ 를 소비자로 등록. #655 PRJ 겹침은 DashMainWindow.cpp 1파일 20항목, 선행이어야 할 PRJ 항목 없음(D-1 자동 기입으로 충분).
- C-2 ⑨ 신설: **보드 밖 OPEN 이슈 4건** #552(완료) #404(ANA) #394(PRJ) #577(MOR) — D-1 에서 mapping 입력에 추가. 차집합 전수(`gh issue list --state open` vs 보드)를 한 번 떠 둘 것.
- C: UIC 검토 완료 (opus) — **#655 전건 미등재**(UIC-01·03·05·06·07·09·10·18·19·20·21·22), 그중 UIC-07·22 는 선행으로 승격(#655 hunk 가 `setupMorphingBar()`·`DashMorphingSettings.cpp` 본문). 회신: CON-04↔UIC-19 → **UIC-19 가 맞음**(GetProject 는 ctor 1회 new·재할당 없음) · RUN-24↔UIC-24 → 동의, UIC-24 먼저. 잔존 1(UIC-c40 #370 부수3 해소 — 살아 있는 사례는 Morphing 분기 `:457-462`). 실측 오류 1("Please 계열 31" → 60). 공허한 완료 기준 3(UIC-13 `\s` git ERE 미지원 · UIC-10 AC3 · UIC-15 grep). 기타: UIC-12 좌표 오기 · UIC-20 26→23파일 · UIC-19 규모 M→L · L1-1 원천 #449→#450 · UIC-c19 오판. 실측 5종·UIC-14 표는 전건 일치.
- **Phase C 완료 (16/16)** — 지적 합계 212 (CON 16 · CAD 16 · PER 14 · REN 13 · MOR 20 · DOE 11 · LCH 10 · PRE 18 · BLD 11 · RUN 12 · ANA 9 · OPT 11 · DEV 12 · EXE 13 · PRJ 20 · UIC 16).
- **C-2 확정** — `05-final/decisions.md` 9건 전부 확정 (회신 대기 0). C' 착수.

## Phase C' (검토 반영)

- 묶음 1 완료 (MOR DOE LCH PRE, opus) — items 346 → 352. 신설: LCH-29(wbpj DEC) LCH-30(#648 PR) LCH-31(MBD CLI DEC) LCH-32(#444 DEC) MOR-23(#430 잔여 INV). MOR-09·15 CLOSE 전환, MOR-05 → DEC. 기각 5(DOE Purpose 표 층 역전 1 · PRE 분할 제안 4 — 개념 1개). 보류 11(PRE→LCH 2·BLD 2·ANA 2, DOE→PRE 1·PER 1, LCH→CAD 1·PRJ 1·PER 1).
- **수집 범위 결정** (사용자): 보드 밖 OPEN 26건 중 **검토가 집어낸 4건만 편입** (#552 완료 · #577 완료 · #404 ANA · #394 PRJ). 나머지 22건은 `01-sources/open_issues_offboard.md` 전수 표에만 남긴다. 처리는 해당 모듈 C' 또는 2차 반영.
- C': RUN 완료 — RUN-34(T23 Runner 홉) 신설, 선행 4건 `PER-07 · RUN-34` 치환, 충돌란 #530 22행 제거. 기각 2(RUN-07+08 · RUN-19+20 병합 — 개념 2개: D17 행 상태 보존 vs D19 무경고 통과). 보류 2(OPT-10 `(Field)` 문구 · PRJ-19 `m_categoryWidgetMap` = 신설 claim RUN-c72). 좌표 재보정 2(CAD W:658-659 · Morphing 경고 W:1757-1766), RUN-08 을 "생성 4경로 중 2경로" 로 정정.
- C': OPT 완료 — OPT-26(T23 Optimizer 홉) 신설하고 **OPT-03·04 를 결번 처리해 OPT-26 으로 흡수**. 근거: #530 의 OPT hunk 하나가 deck 출처(configs 전수 스캔 → `kGeometryDeck`+`resolveSourceFilePath`)·processEvents 2곳·핀/차단을 함께 바꾸고 그것이 D20 재개정 자체 — 개념적 응집상 1개념. 충돌란 #530 24건 제거, OPT-22·20 선행에 PR #655. 좌표 재측정(c10·c39 → `:1854-1860`·`:1862`), OPT-16 변경 범위에서 PM 삭제(이미 공용 포워딩). **RUN-15↔OPT-10: 변경 파일 4:2 로 RUN-15 가 공용 규칙·컨트롤러를 맡고 OPT-10 이 선행 소비자** (2차 반영에서 RUN 확인).
- C': BLD 완료 — BLD-20(T22) 신설(`gh pr diff 530` 실물 확인: M.cpp +121 · M.h +9 · MCU.h +3 · W.cpp +4, 파일명 dev 일치). 선행 `PER-06 · PER-07 · PRE-32 · BLD-13`(역전 반영), `loadLabelMetadata` 필터 hunk 드롭 명기. 선행 치환 BLD-14·15·17·18, 충돌란 #530 전량 → `BLD-20 (<함수>)`. BLD-05 근거 보정(검토가 M:281 만 적었으나 MCU:93 도 같은 생성 폴백), BLD-15 변경 범위에서 `DashProject.cpp` 삭제, BLD-11 을 4항으로 축소(③④⑦ 은 BLD-01·12·07 선결), DeepOpt 제약을 BLD-c44·16·14 에 반영. 보류 2(D-1 deps 재생성 · PRJ-22 `checks[]`).
- C': ANA 완료 — ANA-23 신설(PRE-30·31 이 넘긴 결과 XML 스키마 파서 수용. 근거: `extractVariablesFromXml` 이 첫 샘플로만 변수 목록을 세움 `:629-651`·`:687-690`, `sortedSampleKeys:388-395` 가 최상위 키 전부를 샘플로 봄). #404 → ANA-02 흡수(판정 해소됨 038e687f/#410, 떠 있는 `applyReduction()` 주석 참조를 범위에, 대응표 "닫기 제안"). 기각 1(ANA-19 재배분 — 논리px↔물리px 환산 누락이 1개념, 쪼개면 DPR 규칙이 흩어짐). ANA-05 공유 쌍 정정(실 근거는 빈 Set 시점 키 `0_` 겹침), ANA-06 은 **PRJ 선행 불필요**로 확인.
- C': EXE 완료 — claims 60→62(215-2 4절 해소됨→EXE-01 · 7절 유효→EXE-07 흡수). 규모 5건 S→M(00-plan 1-2 파일 수 기준 머리말 명시), EXE-14 DEC→INV, EXE-12 는 종류만 DEC→PR(2분할 기각 — "데몬 stdout 계약" 1개념). 좌표 정정: RW assert 는 생성자 `DashRwActor():98`, flat 분해는 코루틴 `readFeCondition:518`. #512 잔여는 `DashMeshQualityDialog.cpp:164` 가 맞아 전수표 소관을 `#512-1 → MOR-01` 로, 본선 28 을 `PRE 16 · #455 9 · #512 1 · OPT 2` 로 정정. **검토 자체 오류 1건 정정** — EXE-22 소비측이 "5파일 6곳" 이 아니라 8파일 9곳(`DashGeometryParameter.cpp:161`·`DashModelRunner.cpp:2153`·`DashOptimizer.cpp:1491` 누락). EXE-09 는 `controller/async/DashJobGuard`(Widgets-free) + `view/common/DashJobGuardWidgets.h` 로 층 분리해 현행 하네스에서 성립하게 고침.
- C': PRJ 완료 — 신설 3: PRJ-34(DEC Set 모델 공통 베이스 자리 — ⑧ 코드 재확인: `DashMvvmModelBase` production 상속자 0, Set 모델이 QObject/QAbstractTableModel/QStandardItemModel 3갈래) · PRJ-35(Save As 가 `clearAllSets` 로 Set·트리 전멸, 복원 없음) · PRJ-36(#394 자기 덮어쓰기 소실). **PRJ-20 은 결번 대신 CLOSE** — CON 4항목이 충돌란에서 참조해 결번 시 없는 ID 참조 발생. 선행 사슬 PRJ-34→PRJ-08→CON-05(역순 허용). 기각 4(모두 검토의 좌표·집계 오류: `setRenderer` 는 `.h:46` 이 맞음 · c44 가 `setupMenus` 를 근거로 들지 않음 · `registry.load` 는 `:2766` · "MainWindow 39" 가 맞음 — 렌더 37 + 핸들 2). RUN-c72 미흡수 해소(PRJ-c69). 보류 4(CON 3 · LCH 1).
- C': DEV 완료 — 반영 11 · 기각 1 · 보류 0. 항목 25→24(**DEV-09 결번** — external/ 폐기의 저장소 변경이 `build-environment.md` 1건뿐이고 DEV-12 가 같은 파일을 옮기므로 1개념 → DEV-12 병합, #336-1 흡수). claims 38→39(`DEV-c39` 신설 — README 라이선스 옵션 기본값 `2026-06-30` vs CMake `2026-08-31` 불일치). **DEV-11 INV→PR**: 로컬 `cmake --version` 4.3.3 의 `InstallRequiredSystemLibraries.cmake:252-254`(v145)·`:297-312`(VS_18 글롭)·`:610-621`(vcomp140.dll) 로 차단 해제 직접 확인, c13 미확인→유효, `cmake_minimum_required(3.25)`→범프 + CRT 소비처 2곳(`:463-469` 앱 · `:288-293` UiPreview) 완료 기준화. **DEV-19 축소**: 54 등록 비동형(가드 24블록 환경 변수 상이) → ":383 수동 30개 나열 제거 + `:921 cmake_language(DEFER)` 선례 재사용", 완료 기준 2 를 "ENVIRONMENT_MODIFICATION 값 전후 동일" 로 바꿔 "동작 불변" 과 정합. **PR #655 선행 2건** — DEV-10(`:2146·2150` 을 `DashHandleTree.cpp` 로 옮기며 이미 `globalPosition()` 치환 → 대상 14→12곳, 그 파일 변경 범위 조건부) · DEV-19(`:392-404` hunk 가 타깃 집합 변경). 기각 1: deps.md 괄호 선행 오파싱 = `items_index.strip_parens` 로 해소(괄호 문구는 비고·완료 기준 단계로 이동). `tests/e2e` 를 DEV-14 결정 쟁점·DEV-15 완료 기준 4 로 편입. 수치 정정 4(VTK 29→28 · 타임아웃 28→27 · `Mgr()` 244→245 · find_package 좌표 300-329). #530 표기 제거, clang-format 공통 제약을 파일 머리말 1회로. #489 분할(DEV=인프라 / 커버리지=각 모듈) 유지 확인.
- C': DEV 완료 — DEV-11 INV→PR(로컬 `cmake --version` 4.3.3 의 `InstallRequiredSystemLibraries.cmake:252-254` v145 · `:297-312` VS_18 글롭 · `:610-621` vcomp140.dll 로 차단 해제 직접 확인, `cmake_minimum_required(3.25)` 범프 + CRT 소비처 2곳). **PR #655 는 단순 충돌이 아니라 선행 2건** — DEV-10 은 #655 가 `DashGeometryParameterWidget.cpp:2146·2150` 을 `view/common/DashHandleTree.cpp` 로 옮기며 이미 `globalPosition()` 으로 치환(대상 14→12), DEV-19 는 `:392-404` hunk 가 타깃 집합을 바꿈. DEV-19 축소(54 등록 비동형 확인 → `:383` 수동 30개 + `:921 cmake_language(DEFER)` 선례), DEV-09→DEV-12 병합(개념적 응집). 기각 1(괄호 선행 오파싱 — `strip_parens` 로 해소). 수치 정정 4.
- ⚠ 새 PR **#656 · #658** 이 2026-10-06 중 열림 — `01-sources/open_prs.md` 스냅샷(5건) 밖이라 C' 에 미반영. D-1 에서 갱신 여부 판단.
- D-1 선반영 2: `01-sources/open_prs.md` 재생성 (PR 7건·파일 목록). `items_index.OPEN_PRS` → `('658','656','655','654','652','651')` — **#530 제외는 의도**(재업로드 노선이라 머지 대기 아님). 신규 #656 겹침 27(PRE 21·PRJ 3·ANA 1·LCH 1·UIC 1) · #658 겹침 42(PRE 23·DEV 6·EXE 3·PRJ 2·UIC 2·기타 6). decisions ⑩ 으로 기록 — 선행 여부는 2차 반영에서 판단, 단순 충돌은 `build_deps.py --apply` 자동 기입.
- C': UIC 완료 — UIC-26 신설(UIC-06 DEC 의 숨은 구현을 조건부 PR 로 분리). 실측 재확인 전건(Please 60·선두 45 / QMessageBox 종류별 124·33·5·1 / Instance 가드 23파일 / `fitTableHeight` 호출 4곳 / `ui/` 16벌 전부 최상위 레이아웃 보유 / `minimumSize` 300×30·200×40 가 `.ui` 로 이동해 생존). #655 diff 로 `setupMorphingBar` hunk 확인 → UIC-07·22 선행 승격, `RowOfWidget` 0건이라 UIC-22 전제 생존. **검토 자체 오차 2건 교정** — UIC-15 정규식 대상이 42 아닌 46(`border-*-width` 4건 포함) → `(^|[[:space:]])(min-|max-)?(width|height):` 로 확정, UIC-12 비대상이 2곳 아닌 3곳(`:842·:989·:1401`). 보류 4(CON-04 축소 · RUN-24 대칭 기재 · DOE 2곳 · OPT 1곳).
- 표기 통일: "열린 PR 5건 중 머지 대상 4건(#651 #652 #654 #655)" — #530 은 재업로드라 머지 대상 아님. (스냅샷 재갱신 후로는 PR 7건 중 머지 대상 6건.)
- C': CON 완료 — decisions ⑦ 4쌍 전건 처리. CON-03 훅을 `addReferenceFile` 의 `registry.load` 성공 뒤로 교정(`discardLoadedReferenceFile:2727` 이 `QFile::remove:2715`·`copy:2718` 보다 앞에 도는 것을 코드로 확인), CON-04 는 가드 신설 기각하고 QPointer 2곳만, CON-09 는 완료 기준 (2) 삭제·선행 EXE-21, CON-05 는 선행 PRJ-08(PRJ-34 지연 시 역순). **#655 는 CON 선행 아님** — MainWindow hunk 가 `handleSubItemSelection:1333`·`initializeMorphingController:2190`·`setupMorphingBar:2405` 뿐이라 CON 함수와 무교차. 신설 CON-12(FE 표 체크 write-through). 기각 1(CON-06 분할 — 1인자 오버로드 삭제가 2인자 null 수용을 요구해 1개념). 보류 1(공용 DV 모델 `setParent(this)` → DOE 몫, `DashManager.cpp:81` 부모 없이 new 확인). c24→D9 전용 축소·D11 몫 c11 이관으로 mapping 오귀속 해소.
- C': CAD 완료 — **순환 선행 실재 확인** (선행 그래프가 아니라 완료 기준 경유라 스크립트가 못 잡음): CAD-11 선행이 CAD-01·04·05 인데 CAD-02/04/05/13 완료 기준이 "CAD-11 TU 로 확인" → CAD-11 을 `선행: -` 로 먼저 랜딩(현행 동작 고정)하고 CAD-04·05·13 선행에 CAD-11 을 넣어 끊음. LCH-29 를 CAD-01·02·05 선행 등록. 기각 3(CAD-02·03·07 분할 — 각각 "명령 경계 파사드 전역 상태"·"세션 캐시가 저장값·경계를 넘지 않게"·"진행 표시 시작·정지 짝" 1개념, 단 지적 내용은 반영). 신설 CAD-15(INV 데몬 사망 통지 fan-out 실측) + claims 2. #655 는 CAD 선행 아님(hunk 3곳 전부 모핑 블록).
- D-1 선반영 3: `items_index.load_open_prs` 가 `OPEN_PRS` 필터 없이 open_prs.md 전부를 읽어 **#530 이 deps.md PR 열에 남던 문제** 수정 (CAD C' 발견). 이제 머지 대상 6건만 집계.
- C': PER 완료 — PER-02 를 `DashSaveSystem::read/writeJsonFile` **승격**으로 재정의(완료 기준에 소비자 9건, PER-01·08 에 "파일 계층 존치" 명시). PER-07 을 "재업로드 · 공통부 한정" 으로 못박고 홉별 5건(DOE-16·PRE-32·BLD-20·RUN-34·OPT-26) 등재. 코드로 확정: **#471 CLOSE**(대장 구현 0 · `tableId` 3계층 추적 현존 · 설계문서 폐기 · 하류 핀이 역방향 기록) → PER-11 · JSON 헬퍼 중복이 5벌 아닌 **8벌**(`DashDoeTableFile::read` + DOE 이관 `loadJsonRoot`·`loadSettings`) · PER-c33 뮤텍스 전제 무효(`model/` QMutex 0) · PER-c18 은 LCH-32 확정으로 PER-03 에서 제외. 겹침 PR 4건 모두 충돌(선행 불요 — #652 diff 로 `loadJsonRoot` 미삭제 확인).
- 교차 확인 (orchestrator): PER 이 보류로 넘긴 "PRJ-31·RUN-32·OPT-24 의 DashJsonFile 미치환" 은 **오판** — 세 항목의 목표·완료 기준·변경 범위에 그 문구는 0줄이고, 남은 것은 비고의 "신설은 폐기됐다" 설명 문맥뿐. 2차 반영 불요. 남은 `#530` 언급 32곳도 전부 "머지하지 않는다" 설명·대응표 사유이고 **충돌란의 #530 은 0건** (decisions ② 이행 완료).
- D-1 할 일 추가: **머리말 열린 PR 건수 표기가 모듈마다 불일치** (CAD 7 · REN 7 · CON 6 · PER 6 · DEV 5 · EXE 5 · OPT "#530 하나"). decisions ⑩ 기준 "열린 PR 7건 중 머지 대상 6건(#651 #652 #654 #655 #656 #658)" 으로 일괄 통일.
- C': REN 완료 — **직접 renderer 조작 재집계 확정**: controller 21(Visualizer 4 · Picking 6 · MorphingController 11) + DashGizmo 10 + view 3. 종전 "controller 7" 은 `GetRenderer()->Add/RemoveActor` 패턴만 세어 지역 변수 `ren->`·`renderer->` 경유를 놓친 오집계였고, 21 은 #318 범위 제외 절 집계와 일치. REN-07 소유자 모순을 `addAnalysisModelActor(actor, owner)` 로 해소(+`showScalarField:3149` 누락), REN-11 을 "복수 `.vtk/.vtu` 동시 표시" 로 재작성(`vtm_parent` 는 행 생성 코드 0 → 죽은 분기), REN-04 축소(누적은 #332 로 닫힘), REN-06 을 (a)(c) 로 축소. 완료 기준 7건을 grep·코드 검사 기준으로 확인 가능하게. OPT-01 을 `DashRenderingManager` 직렬 규칙·충돌 7건에 등재(REN-10 이 OPT-01 선행이라 모순 없음). #655 선행 불요.

### Phase C' 완료 (16/16, 2026-10-06)

| 집계 | 값 |
|---|---|
| 반영 | 199 |
| 기각 | 19 |
| 보류 (타 모듈) | 35 |
| items | 346 → 359 (결번 3 제외) |
| 신설 | LCH-29~32 · MOR-23 · BLD-20 · RUN-34 · OPT-26 · ANA-23 · PRJ-34~36 · CON-12 · PER-11 · UIC-26 · CAD-15 (16) |
| 삭제·CLOSE 전환 | OPT-03 · OPT-04 (결번) · DEV-09 (결번) · PRJ-20 (CLOSE) · MOR-09 · MOR-15 (CLOSE) |

## Phase D-1 (재생성)

## Phase C' 2차 반영 (보류 이관)

- 보류 전수를 `05-final/deferred.md` 로 저장 (75행, 중복 제외 고유 약 35건, 대상 모듈 14). 실행 순서가 늦은 모듈(CON CAD PER REN)은 1차에서 자기 앞 보류를 이미 처리했을 수 있어 **확인 후 미반영분만** 고치게 지시.
- 2차: PRJ 완료 — 보류 8행 = 실건 4건. 반영 1(BLD 몫 `checks[]` → PRJ-22 가 그 자리를 일반 순회로 바꾸는 항목이라 **별도 추가가 아니라 흡수**로 기재, `DashProject.cpp:1657-1698` 재확인 + 예고 주석 근거). 이미 반영 3(RUN-c72→PRJ-c69 · PRJ-31 문구 · LCH-29 소비자). **PR 선행 추가 0** — `gh pr diff` 로 hunk 확인: #656 은 `loadResultKeys`·`previewNaturalFrequency`·`requestVtkGeometry`, #658 은 `requestVtkPreview`·`previewNaturalFrequency` 만 고치고 PRJ-03·09 가 치환할 `DashProjectManager::Instance()` 5곳은 전부 다른 함수 → 단순 동시 수술. 열린 PR 표기 통일.
- ⚠ D-1 확인거리 (PRJ 2차가 범위 밖으로 남김): PRJ-03 변경 범위의 `model/DashAnalysisLauncher.cpp` 는 실측상 `PrjMgr()` 0건 (`PrjMgr()` 68건 = MainWindow 58 · ContextRegistry 5 · DashManager 3 · tests 2). 변경 범위에서 뺄지 D-1 에서 판단.
- 2차 교차 확인 (orchestrator 직접): **ANA · CAD · PER · REN 은 1차에서 이미 전건 처리** — ANA-23 신설(PRE-30·31 흡수) · CAD-01·02·05 선행 LCH-29 · REN-10 선행 OPT-01(REN 전체 OPT-01 언급 21회) · PER-02 DashSaveSystem 승격. 2차 agent 불요. MOR 은 PRJ 가 "PRJ-04 가 맞다" 로 결론해 불요.
- 2차: CON 은 ⑦ 4쌍이 1차에서 이미 처리됐고 **`CON-11` 의 `선행: PER-05` 1건만 남아 직접 제거** (PER 검토 #9 — 왕복 게이트를 선행으로 걸면 bug fix 가 인프라 PR 을 기다린다. DOE-17 과 같은 처리). 완료 기준 (3) 을 "PER-05 가 랜딩해 있으면 그것으로, 아니면 이 TU 안에서 비교" 로 고쳐 PER-05 없이도 확인 가능하게. `충돌` 의 PER-05 는 같은 테스트 파일이라 유지.
- 2차: DOE 완료 — 반영 2(신설 2). **DOE-19** 공용 `DashDesignVariableModel` 소유권(← CON-c27): `DashManager.cpp:81` 에 부모 부여 + CON `:331`·CAD `:310` 의 `setParent(this)` 2줄 삭제. 코드 재확인 — dtor `:103-123` 은 데몬 4종만 만지고 DV 모델 미관여, MOR/DOE 는 자기 부모를 둔 별 인스턴스. DOE-10 과 개념이 달라 분할. **DOE-20** Resample Search Min/Max 셀 델리게이트 검증(← UIC-c41(b), 선례 `DashFeConditionValueDelegate.cpp:102-109`). PR 선행 0(#656·#658 모두 DOE 파일과 교집합 0). items 16→18 · claims 64→66. **CON-c27 미흡수 해소** (미흡수 3→2).
- 2차: RUN 완료 — 반영 1(RUN-15). **정본 확정**: `(Field)` 는 Model Builder 가 `baseDim==3 && reduction=="None"`(`DashModelBuilderPresentationModel.cpp:174`·`:188`)에서 붙여 `getOutputResponseList`(`DashModelBuilderWidgetBase.cpp:299`) → `Output Response` → model_info `errors` 키까지 실어 보내는 기록된 ND 결정이고, 모델 이름 카탈로그 `ndModelNames()` 5건은 `getModelsForDimension(3)`={"StableNet"} 1건과 이미 어긋난 중복 → **응답 속성이 정본**. 변경 범위에 모델 이름 판정 호출부 4곳 추가, 규모 S→M.
- 2차 RUN 이 **넘긴 모듈 판단 2건 정정**: ① `view/common/SurrogateTableController.cpp` 는 공용이 아니라 **RUN 전용**(소비자 2곳뿐) → decisions ⑦ 의 "4:2 귀속 다툼" 자체가 성립 안 함, OPT-10 은 파일 교집합 없는 선행 소비자. ② `(Field)` 판정은 5곳이 아니라 **6곳**(+생산 1곳) — BLD 2곳(`DashModelBuilderWidget.cpp:1089`·`:1681`)은 대응 항목이 없어 접점 BLD. #656·#658 은 RUN 과 교집합 0.
- 2차: EXE 완료 — 반영 3(EXE-12 흡수에서 CAD-D14 제거 + 대응표 `→ CAD-10` · 열린 PR 표기 통일). CAD 판단 타당 확인: CAD-D14 = `nx_helpers.py:update_expressions` 가 실패를 ListingWindow 에만 쓰는 외부 저장소 결함이고 EXE-12 는 그 위의 stdout 계약이라 실작업 없음. **머리말 "`DashRwActor` 를 만지는 PR 없다" 가 #658 로 거짓이 되어** 접촉 5파일 명기. PR 선행 0 — `gh pr diff 658` hunk 확인: `DashRwActor.cpp` +16 은 익명 namespace `deepCopyCoupling` 신설뿐(EXE-05 생성자 assert `:98` 과 무접촉) · `DashRwDocument.cpp` +66 은 Constraint/Coupling 수집·`fetchCouplingShape` 로 EXE-21 이 겨냥한 `readFeCondition` 과 다른 갈래 · `registry.load` 변화 없어 EXE-22 의 8파일 9곳 전수 유지. EXE-21 완료 기준의 `TestRwDocument 15건` 에 "#658 머지 뒤 16건" 괄호 추가(dev 실측 15 확인).
- 2차: LCH 완료 — 반영 3, 신설 2. **LCH-33**(Start 거절 — `snapshotDoeTable` 가드 + Start 람다 거절, 선행 PRE-32·DOE-16, #368 Phase 2 Start 몫 흡수) · **LCH-34**(PRE-15 사유 노출 — Active 체크 2곳은 모달·상태 기록은 런당 1회, 선행 PRE-15·LCH-07, #638-2 흡수). LCH-29 완료 기준에 PRJ 원장 조항 3항(제거=비편입·PRJ 신규 0 / 현행 유지=원장 편입 1건 / 동결=현행 유지). PR 선행 0 — #656·#658 의 `DashAnalysisLauncher.cpp` hunk 가 전부 PRE 결과 경로(`loadResultKeys`·`previewNaturalFrequency`·`requestVtkGeometry`·`requestVtkPreview`)라 LCH-15 작업 자리(`preprocessInputsChanged`·`connectLaunchExecutor`)와 무교차. items 32→34 · claims 98→100.
- 부수 정정: PRJ 검토 19 의 "`.stli` 1곳(`DashMainWindow.cpp:2665`)" 은 실측 5곳(`:362`·`:2628`·`:2649`·`:2963`·`:2968`) — LCH 2차가 고침.
- 2차: OPT 완료 — 반영 2(OPT-10 에 decisions ⑦ 확정 반영 · 열린 PR 표기). 정본은 **응답 표시 이름의 `(Field)`** — `responseDisplayText:174-178` 의 `baseDim==3 && reduction=="None"` 이 `effectiveModelDimension:188` 의 `isND` 와 같은 술어라 model_info 까지 기록되고, 모델 이름 접두 `isNDModel` 이 아님. `SurrogateTableController` 는 RUN 전용이라 파일 교집합 0 → RUN-15 가 맡고 OPT-10 은 선행 소비자(충돌 아님). **미반영 1 — 넘긴 판단이 틀림**: UIC-c41(b) 의 OPT 몫(`DashOptimizerWidget.cpp:1519-1522`)은 `val_dvTable` 이 `ui/DashOptimizerWidget.ui:255` 에서 `NoEditTriggers` 이고 `setEditTriggers` 0건, 셀 값은 `addSolutionColumn:1416` 이 `QString::number` 로 쓰므로 사용자 입력 경로가 없다 → 범위 검증 대상 아님(OPT-c58 판정 `해소됨`). PR 선행 0(#656·#658 과 교집합 0). items 24 유지 · claims 57→58.
- 2차: BLD 완료 — 반영 3. BLD-14 에 PRE-31 수용(완료 기준 (6) "샘플 0 위상으로 나머지를 읽는다", 선행 PRE-31, `M.cpp:373-418`). **BLD-21 신설**(← RUN 2차 발견: `W:1089 updateModelError` · `W:1681 hasNDModelInConfiguration` 을 공용 술어 호출로, `ndModelNames()` OR 분기 `:1675` 삭제, 선행 RUN-15). PR 선행 0 — #658 `DashResultXmlWriter.cpp` hunk 는 응답 배열을 이름으로 고르고 `quantity`·`unit`·`component_labels` 속성 추가·모달 키 `Eigenvalue` 변경이나 샘플 dict 구조·`model_info` 위치 불변(BLD-14 비고 기재). items 19→20 · claims 44→45.
- D-1 선반영 4 (PRE 2차 대기 중): `build_mapping.py` EXTRA_ISSUES 에 보드 밖 4건(#552 #404 #394 #577) · DEV items·UIC claims 머리말 PR 표기 통일(이제 16 모듈 전부 "7건 중 머지 대상 6건") · **PRJ-03 정정** — `model/DashAnalysisLauncher.cpp` 는 `PrjMgr()` 0건(이미 `Instance()` 5곳)이라 변경 범위에서 제외, 건수 71 → 68(dev 실측: MainWindow 58 · Registry 5 · tests 2 · DashManager 3).
- 2차: PRE 완료 — 반영 2(PRE-32 `geometryDeck` 도 스냅샷에서 · PRE-29 선행 PER-03). 미반영 1(PRE-28 의 PER-03 선행 — 실측은 버전 키 규약과 무관). **#656 이 PRE-03 을 전부 구현**(compact 4곳·modalNames 2곳·`modeNames` 삭제) → PRE-03 PR→CLOSE, 잔여 1줄은 PRE-04 흡수. **#658 이 어댑터 sub-result 발행·`responseArray()` 이름 조회·`modeShapeLeaf` 재작성을 이미 수행** → 선행 추가 8(PRE-01·02·04·06·10·17·18·29), 범위 축소 PRE-06·10(M→S)·18. claims 해소됨 8건 전환(11→19). items 32 유지.

### Phase C' 2차 완료 (9/9 + CON 직접, 2026-10-06)

| 집계 | 값 |
|---|---|
| 반영 | 17 |
| 이미 반영 (1차에서 처리) | 12 |
| 미반영 (넘긴 판단 오류) | 2 — OPT UIC-c41(b) `NoEditTriggers` · PRE-28 PER-03 선행 |
| 신설 | DOE-19 · DOE-20 · LCH-33 · LCH-34 · BLD-21 (5) · PRE-03 CLOSE 전환 |
| PR #656·#658 선행 추가 | PRE 8 · 그 외 0 |
| 넘긴 모듈 판단 정정 | `SurrogateTableController` 는 RUN 전용 · `(Field)` 판정 6곳 · `.stli` 5곳 |
- D-1 재생성 완료 — `build_deps.py --apply`(충돌 줄 269 갱신) → deps.md · mapping.md · check_coverage 0. 부수 수정 2: `items_index.PR_ALIAS` 의 `'#368 PR'·'#368 T2' → 530` 제거(RUN-14 의 "#368 T23" 설명문이 #530 으로 오인되던 원인 — deps.md #530 0건 확인) · `build_mapping.py` 주 모듈 열에 보드 밖 이슈 fallback(첫 항목의 모듈).

## Phase D-2 납품 (2026-10-06)

`python3 05-final/build_final.py` → `05-final/FINAL.md` (767 KB).

| 최종 집계 | 값 |
|---|---|
| claims | 938 |
| items | 364 — PR 268 · DEC 46 · INV 13 · EXT 7 · CLOSE 30 / S 256 · M 92 · L 10 |
| 태그 | A 138 · B 69 · C 69 · D 77 · E 106 · F 30 · G 16 |
| 정합 검사 | 열린 이슈 누락 0 · 결함 누락 0 · 참조 오류 0 · 범위밖 미흡수 2 (EXT 의도) |
| deps | 순환 0 · PR 대기 197 (선행 명시 57 · 파일 겹침만 140) · 즉시 착수 119 |
| mapping (a) 이슈 117 (113 + 보드 밖 4) | 항목 86 · CLOSE 21 · CLOSE+잔여 10 · 항목 없음 0 |
| mapping (b) 결함 201 | 항목 159 · CID 경유 8 · CLOSE 3 · 해소됨/범위밖 31 |

B2 대비 변화: items 346 → 364 (+18), 즉시 착수 92 → 119, PR 대기 217 → 197 (#530 제외 + 선행 정리).

**발행 단계는 별도** — 이슈·PR·위키·보드 변경 없음 (00-plan 1-5 유지).
