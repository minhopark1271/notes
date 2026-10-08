# C' 2차 반영 — 모듈별 보류 전수 (2026-10-06)

> 1차 C' 가 `보류: <MOD> 몫` 으로 남긴 전부. 실행 순서가 늦은 모듈(CON CAD PER REN 등)은 자기 앞 보류를 1차에서 이미 처리했을 수 있다 — **각 모듈은 반영 여부를 먼저 확인하고 미반영분만 고친다.**

합계 75행 (같은 보류가 04-review·03-items 양쪽에 적혀 중복 포함) · 대상 모듈 14

## → CON (14행)

| 출처 | 넘긴 모듈 | 내용 |
|---|---|---|
| `04-review/EXE.md:17` | EXE |  까지 넓힘, 충돌에 CON-09 를 "EXE-21 먼저" 로 등재. CON-09 쪽(완료 기준 (2) 삭제 · `FakeRwModule.h` 제외 · 선행 EXE-21) 은 **보류: CON 몫** \| |
| `04-review/EXE.md:40` | EXE | \| ⑦ CON-09 ↔ EXE-21 (FakeRwModule flat 픽스처) \| 검토 #9 행 참조. EXE-21 에 흡수·완료 기준·충돌 반영. CON-09 쪽은 **보류: CON 몫** \| |
| `04-review/PER.md:15` | PER | 를 막지 않게 \| 반영 — PER-05 완료 기준 2 삭제, 규칙("왕복 케이스는 모듈 완료 기준에만 · 선행 금지")은 비고로. CON-11 의 `선행: PER-05` 제거는 `보류: CON 몫`(DOE-17 은 이미 제거) \| |
| `04-review/PER.md:36` | PER | - 보류 — PER-02 문구 치환 미완 `보류: PRJ · RUN · OPT 몫`(3건이 아직 "DashJsonFile" 로 적혀 있다) · CON-11 의 `선행: PER-05` 제거 `보류: CON 몫` · PRE-28·29 가 PER-03 을 선행으로 참조 `보류: PRE 몫`. mapping.md·deps.md 재생성은 D-1 몫. |
| `04-review/PRJ.md:24` | PRJ |  닫기 사유에 적고 대응표 `#645` 행을 `PRJ-21 · PRJ-20(CLOSE)` + "집행은 CON-03" 으로 고쳤다. PRJ-21 `충돌` 에 CON-03 추가. **보류: CON 몫** — CON-03 목표의 훅 위치 교정 · "진입점 노출" 문구 삭제 · CON 4항목의 `PRJ-20` 참조 제거 \| |
| `04-review/PRJ.md:25` | PRJ | 넣었다. 별도 DEC 는 신설하지 않고 선행을 PRJ-34 → PRJ-08 → CON-05 로, 역순 허용을 PRJ-08 비고에. PRJ-08 `충돌` 에 CON-05 추가. **보류: CON 몫** — CON-05 에 `선행: PRJ-08`(역순 허용) 기재 \| |
| `04-review/UIC.md:10` | UIC | sions ⑦ 확정 근거(`DashProjectManager.cpp:26-28 · 45-48 · 239`) 기록. CON-04 축소(가드 신설 기각 · QPointer 2곳)는 `보류: CON 몫` \| |
| `04-review/UIC.md:44` | UIC | \| `보류: CON 몫` \| CON-04 축소 — `GetProject` 가드 신설 기각, QPointer 2곳 + `:370-371` 만 남김 (decisions ⑦) \| |
| `03-items/EXE.md:246` | EXE |  소관이며 CON-09 는 픽스처를 **쓰는** 쪽. CON-09 의 완료 기준 (2) 삭제 · `FakeRwModule.h` 변경 범위 제외 · `선행: EXE-21` 추가는 `보류: CON 몫`. |
| `03-items/EXE.md:287` | EXE | 2)) \| CON-c17 → EXE-c58. 귀속 확정 C-2 ⑦. CON-09 쪽 수정(완료 기준 (2) 삭제 · `FakeRwModule.h` 제외 · 선행 EXE-21)은 `보류: CON 몫` \| |
| `03-items/PER.md:71` | PER | `선행: PER-05` 는 두지 않는다. 게이트를 선행으로 걸면 bug fix 가 인프라 PR 을 기다린다(검토 #9). DOE-17 은 제거 완료 · CON-11 은 미제거(**보류: CON 몫**). JSON 수준 비교라 코덱 선택(PER-01)과 무관. 현행 왕복 깨짐 중 "저장된 값이 로드 후 다른 키로 가는" 류(BLD-D4·D7)는 정규화 비교로 잡히고, "쓰기만 되고 읽기에서 버려지는" 류(BLD-D8·RUN-D33·ANA-D9)는 두 번째 저장이 키를 잃어 잡힌다 — 28건 중 쓰기 경로 자체가 없는 3건(MOR-D1 |
| `03-items/PRJ.md:6` | PRJ | > 보류: CON 몫 — CON-03 의 목표를 "`addReferenceFile` 재로드 성공 뒤 핀 deck 일치 시 `refreshFromFile`" 로 교정하고 "진입점 노출" 문구 삭제(이미 public), CON-03·04·06·07 충돌란의 `PRJ-20` 제거(CLOSE 됨), CON-05 에 `선행: PRJ-08`(역순 허용) 기재. 보류: L |
| `03-items/PRJ.md:69` | PRJ | - 비고: 보류: CON 몫 — CON-03 목표의 훅 위치 교정과 "진입점 노출" 문구 삭제, CON-03·04·06·07 충돌란의 `PRJ-20` 제거. 레지스트리는 invalidate 후 load 를 첫 로드로 보아 `documentChanged` 를 내지 않고(REN), CON 모델은 #565 로 방송 구독을 걷었다 — 통지 책임은 덮어쓰기를 집행한 MainW |
| `03-items/PRJ.md:161` | PRJ |  적용분이라 `선행: PRJ-08` 이다. 단 PRJ-34 가 늦어 CON-05 가 블록되면 CON 모델 1종만 먼저 고치고 PRJ-08 이 일반화할 때 맞추는 역순을 허용한다. 보류: CON 몫(CON-05 에 선행 기재) |

## → PRJ (8행)

| 출처 | 넘긴 모듈 | 내용 |
|---|---|---|
| `04-review/BLD.md:14` | BLD | roject.cpp·#652·#651 제거. `DashProject.cpp:1665-1676` 의 `checks[]` 1건 + 예고 주석 확인. `checks[]` 추가 자체는 `보류: PRJ 몫`(PRJ-22) · deps.md 의 BLD-15 ↔ DashProject.cpp·#652·#651 행은 `보류: D-1 몫` \| |
| `04-review/LCH.md:7` | LCH |  영향 — **LCH-06**: `jobFinished` 방출 2곳이 전부 Journal 경로라 (c) 면 Journal TU 삭제 PR 에 흡수(시그널 자체 삭제), (b) 면 보류(2회 `analysisFinished` 는 `setLauncherIdle(true)`·표 재구축 2회로 무해) · **LCH-27**: (c) 소멸, (b) LCH-19(a) "다중 큐잉 안 함" 으로 `startDirectAnsysJournalJobs` 시그니처를 파일 1개로 좁히는 쪽이 더 작다 · **LCH-28**: 포맷 무관(`setLaunc |
| `04-review/PER.md:36` | PER | - 보류 — PER-02 문구 치환 미완 `보류: PRJ · RUN · OPT 몫`(3건이 아직 "DashJsonFile" 로 적혀 있다) · CON-11 의 `선행: PER-05` 제거 `보류: CON 몫` · PRE-28·29 가 PER-03 을 선행으로 참조 `보류: PRE 몫`. mapping.md·deps.md 재생성은 D-1 몫. |
| `04-review/RUN.md:15` | RUN | 기 7곳 · `.h:338` 선언 · 읽기 0 재확인. claims 에 **RUN-c72**(판정 범위밖 → PRJ) 신설 + 대응표 RUN-D1 행 추가. PRJ-19 등재는 `보류: PRJ 몫` \| |
| `04-review/RUN.md:34` | RUN | 보류 2건 — OPT-10 의 `(Field)` 판정 문구(`보류: OPT 몫`) · PRJ-19 에 `m_categoryWidgetMap` 등재(`보류: PRJ 몫`). |
| `03-items/LCH.md:282` | LCH | 경로 수정분을 뺄지) · **LCH-06** · **LCH-27** · **PRJ**(`.wbpj`·`.stli` 원장 편입이 PRJ 코드). CAD 쪽 항목의 `선행` 등록은 `보류: CAD 몫`, PRJ 소비자 등록은 `보류: PRJ 몫`. 축소 내용 — (c) 면 LCH-06 은 Journal TU 삭제 PR 에 흡수(시그널 자체 삭제), LCH-27 은 소멸, PR #651·#652 의 wbpj 분기와 #640 wbpj 사용처(PRE)를 되돌린다 / (b) 면 LCH-27 은 LCH-19(a) 로 대체. **LCH-28 은  |
| `03-items/PER.md:29` | PER | . 각 항목의 "`DashJsonFile`" 문구는 "`DashSaveSystem` 헬퍼(공용 진입점)" 로 바뀐다 — PRJ-31 · RUN-32 · OPT-24 는 미치환(**보류: PRJ · RUN · OPT 몫**) |
| `03-items/RUN.md:342` | RUN | D1 \| 항목 없음 \| 범위밖 → PRJ (`m_categoryWidgetMap` 죽은 코드 · RUN-c72). 결함 색인에 D1 행이 빠져 전 모듈 누락이었다 (검토 9) — 보류: PRJ 몫 (PRJ-19 등재) \| |

## → ANA (7행)

| 출처 | 넘긴 모듈 | 내용 |
|---|---|---|
| `04-review/ANA.md:23` | ANA | - PRE 가 넘긴 몫 — PRE-30·PRE-31 의 `보류: ANA 몫`(결과 XML 스키마 변경의 파서 수용)에 대응하는 ANA 항목이 없었다. ANA-c45 신설(유효) + **ANA-23 신설**. 기존 ANA-c30·c41 은 "컨테이너 교체(HDF5)" 축이라 그대로 두고 비고에서 스키마 축을 ANA-23 으로 가른다. |
| `04-review/PRE.md:22` | PRE | ct 동형) 기재(신설 행 대신 기존 행 보강 — c59 는 이미 BLD-c34 로 흡수돼 있다) · PRE-29 결정 입력 · PRE-30·31 완료 기준·비고. 파서 변경은 `보류: BLD 몫`·`보류: ANA 몫` \| |
| `03-items/ANA.md:227` | ANA | - 흡수: PRE-30(`보류: ANA 몫`) · PRE-31(`보류: ANA 몫`) · ANA-c45 · #643 추가 3(ANA 몫 — 스키마 축) |
| `03-items/ANA.md:260` | ANA | \| PRE-30 · PRE-31 (`보류: ANA 몫`) \| ANA-23 \| PRE 가 명시로 넘긴 파서 수용 (ANA-c45) \| |
| `03-items/PRE.md:294` | PRE | 답 2개 · 응답 추가가 `root` 첫 자식(학습 데이터)과 샘플 dict 동형을 깨지 않는다(DeepOpt 계약) · 식별자 불일치 시 규칙대로 동작 · BLD 로더 수용은 `보류: BLD 몫`(BLD-14) · ANA 파서는 `보류: ANA 몫` |
| `03-items/PRE.md:304` | PRE |  에만 위상을 두어도 샘플 dict 동형 전제를 깨지 않음을 DeepOpt 계약과 대조(PRE-29 결정) · `TestResultXmlWriter` 통과 · 파서 쪽 수용 — `보류: BLD 몫`(샘플 0 위상으로 나머지 읽기) · `보류: ANA 몫`(`DashXmlParser`) |

## → OPT (7행)

| 출처 | 넘긴 모듈 | 내용 |
|---|---|---|
| `04-review/PER.md:36` | PER | - 보류 — PER-02 문구 치환 미완 `보류: PRJ · RUN · OPT 몫`(3건이 아직 "DashJsonFile" 로 적혀 있다) · CON-11 의 `선행: PER-05` 제거 `보류: CON 몫` · PRE-28·29 가 PER-03 을 선행으로 참조 `보류: PRE 몫`. mapping.md·deps.md 재생성은 D-1 몫. |
| `04-review/RUN.md:12` | RUN | ontroller.cpp:createRow (:29)` 추가, 충돌에 OPT-10, 완료 기준에 정본 택일 1줄, 비고에 합의안(decisions ⑦). OPT-10 쪽 수정은 `보류: OPT 몫` \| |
| `04-review/RUN.md:34` | RUN | 보류 2건 — OPT-10 의 `(Field)` 판정 문구(`보류: OPT 몫`) · PRJ-19 에 `m_categoryWidgetMap` 등재(`보류: PRJ 몫`). |
| `04-review/UIC.md:47` | UIC | \| `보류: OPT 몫` \| `DashOptimizerWidget.cpp:1519-1522` 표 셀 1곳의 범위 검증 — 같은 기제 \| |
| `03-items/PER.md:29` | PER | . 각 항목의 "`DashJsonFile`" 문구는 "`DashSaveSystem` 헬퍼(공용 진입점)" 로 바뀐다 — PRJ-31 · RUN-32 · OPT-24 는 미치환(**보류: PRJ · RUN · OPT 몫**) |
| `03-items/RUN.md:152` | RUN | r.cpp:29 · DashModelBuilderWidget.cpp:1089·1681 · DashOptimizerWidget.cpp:556·867. OPT-10 쪽 문구 수정은 `보류: OPT 몫`. 어느 쪽이 정본인지는 Model Builder 의 model_info 기록 규칙에 달림 — 접점 BLD |
| `03-items/UIC.md:300` | UIC | leWidgetItem::text()` 파싱이라 델리게이트 기제. DoeSamplerResampleWidget 2곳 → DOE · OptimizerWidget 1곳 → OPT (`보류: DOE · OPT 몫`) \| |

## → PRE (6행)

| 출처 | 넘긴 모듈 | 내용 |
|---|---|---|
| `04-review/DOE.md:7` | DOE | -16 · PRE-14 · PRE-15 · PRE-27 · PRE-32 · PR #651 추가 · 비고 "스냅샷 쪽으로 정하면 소멸" 분기 삭제(PER 검토 #3 과 일치). **보류: PRE 몫** — PRE-32 가 스냅샷 `parameterizationId` 를 읽고 재계산을 버린다 · `geometryDeck` 은 스냅샷 `parameterization.geometry.deck` 에서 \| 반영 (DOE-16 완료 기준 (4)·변경 범위·충돌 추가, 비고 분기 삭제). 전파 키는 `parameterizationId`·`geom |
| `04-review/PER.md:36` | PER | - 보류 — PER-02 문구 치환 미완 `보류: PRJ · RUN · OPT 몫`(3건이 아직 "DashJsonFile" 로 적혀 있다) · CON-11 의 `선행: PER-05` 제거 `보류: CON 몫` · PRE-28·29 가 PER-03 을 선행으로 참조 `보류: PRE 몫`. mapping.md·deps.md 재생성은 D-1 몫. |
| `03-items/DOE.md:141` | DOE | onfigManager.cpp:5-6); `test_doe_selection`·`test_analysis_launcher_config` 는 둘 다 Qt Core only 다. **보류: PRE 몫** — PRE-32 가 스냅샷 `parameterizationId` 를 읽어 `derivedId` 재계산을 버리고 `geometryDeck` 을 스냅샷에서 가져오도록 완료 기준·`선행: DOE-16` 을 고치는 일. #368 주 모듈은 PER |
| `03-items/DOE.md:212` | DOE | \| PER-06 ① (`kSnapshotKeys` allowlist, c64) \| DOE-16 \| C-2 결정 ⑤ — 기록 측 한 모듈에 귀속. 읽는 쪽 PRE-32 는 보류: PRE 몫 \| |
| `03-items/PER.md:41` | PER | 2. 이 기록을 선행으로 참조하는 항목 — PRJ-32(⑥ `variant` 와의 역할 분리, 등재 확인) · 결과 XML 의 키 작성 PRE-28·29(미등재 — **보류: PRE 몫**) · 채번 키 자리 RUN-10(c16) |

## → RUN (6행)

| 출처 | 넘긴 모듈 | 내용 |
|---|---|---|
| `04-review/PER.md:36` | PER | - 보류 — PER-02 문구 치환 미완 `보류: PRJ · RUN · OPT 몫`(3건이 아직 "DashJsonFile" 로 적혀 있다) · CON-11 의 `선행: PER-05` 제거 `보류: CON 몫` · PRE-28·29 가 PER-03 을 선행으로 참조 `보류: PRE 몫`. mapping.md·deps.md 재생성은 D-1 몫. |
| `04-review/UIC.md:11` | UIC | -24 → RUN-24" 로 확정 \| 반영 — UIC-24 충돌란에 `RUN-24 (같은 함수 — UIC-24 를 먼저)` 추가 + 비고에 순서 근거. RUN-24 대칭 기재는 `보류: RUN 몫` \| |
| `04-review/UIC.md:45` | UIC | \| `보류: RUN 몫` \| RUN-24 충돌란에 `UIC-24 (먼저)` 대칭 기재 (decisions ⑦) \| |
| `03-items/OPT.md:84` | OPT | 자**를 제안한다. `(Field)` 판정 5곳 중 OPT 몫은 `DashOptimizerWidget.cpp:556`·`:867`. RUN-15 쪽 변경 범위·완료 기준 보강은 `보류: RUN 몫`. |
| `03-items/PER.md:29` | PER | . 각 항목의 "`DashJsonFile`" 문구는 "`DashSaveSystem` 헬퍼(공용 진입점)" 로 바뀐다 — PRJ-31 · RUN-32 · OPT-24 는 미치환(**보류: PRJ · RUN · OPT 몫**) |
| `03-items/UIC.md:266` | UIC | :53`·`:185`)와 자기 재귀(`:1465`)·람다 캡처(`:2006`)를 바꾸므로 먼저 랜딩해야 RUN-24 가 좁아진 시그니처 위에서 작업한다. RUN 쪽 대칭 기재는 `보류: RUN 몫`. |

## → LCH (6행)

| 출처 | 넘긴 모듈 | 내용 |
|---|---|---|
| `04-review/PRE.md:8` | PRE | 반영 — 검증 지점을 `loadPreprocessInputs`(priorSamples 출처 스냅샷 id 대조, `test_launcher_runs`)로 교체. Start 거절은 `보류: LCH 몫`(`snapshotDoeTable` 호출부) \| |
| `04-review/PRE.md:15` | PRE | 채택: `bool` + `QString* error` 출력 인자로 LCH 호출부 4곳 무변경. 변경 범위에서 "LCH 호출부" 를 빼고 테스트를 넣었다. LCH 쪽 모달 노출은 `보류: LCH 몫` \| |
| `04-review/PRJ.md:26` | PRJ | RJ-21 비고에 LCH-29 소비자 등록("사장 → 신규 0 / 현행 유지 → 원장 편입 항목 1건"), 대응표에 `LCH-29 (DEC, 접점) → 항목 없음` 행 추가. **보류: LCH 몫** — LCH-29 의 선행 목록에 PRJ 추가와 결정문 조항 \| |
| `03-items/PRE.md:151` | PRE | 7(같은 호출부를 executor 로 모으는 중)과 동시 수술이 된다. 그래서 출력 인자 방식을 택했다 — LCH-07 과 순서 무관. 사유를 LCH 쪽 모달에도 띄우려면 그때 `보류: LCH 몫` 으로 따로 받는다 |
| `03-items/PRE.md:322` | PRE | 지점은 priorSamples(다른 DOE Sampler Set 의 스냅샷)뿐이라 검증을 거기로 잡았다. Start 가 다른 id 의 Table 을 스냅샷하지 못하게 막는 몫은 `보류: LCH 몫`(`snapshotDoeTable` 호출부 — view/DashAnalysisLauncherWidgetLauncher.cpp:220). `model_info` 자리는 D26 확정이라 PRE-29 는 선행이 아니다(PRE-29 는 Set uuid 키의 병기만 정한다 — PRE-30 과 같은 dict 를 건드리므로 충돌로만 둔다). model |
| `03-items/PRJ.md:6` | PRJ | > 보류: CON 몫 — CON-03 의 목표를 "`addReferenceFile` 재로드 성공 뒤 핀 deck 일치 시 `refreshFromFile`" 로 교정하고 "진입점 노출" 문구 삭제(이미 public), CON-03·04·06·07 충돌란의 `PRJ-20` 제거(CLOSE 됨), CON-05 에 `선행: PRJ-08`(역순 허용) 기재. 보류: L |

## → DOE (5행)

| 출처 | 넘긴 모듈 | 내용 |
|---|---|---|
| `04-review/CON.md:20` | CON | ) \| Code-Map 본문도 원천이므로 claims 1행(범위밖 → DOE, 소유자) 또는 CON-06b 에 "setParent 2줄 삭제" 로 흡수. CAD 접점 표기 \| **보류: DOE 몫** — claims `CON-c27`(범위밖 → DOE) 1행만 추가. 코드 재확인(`DashManager.cpp:81` 부모 없이 `new`, dtor :104-124 가 만지지 않음 · CON :331 · CAD :310). 소유자를 누가 쥐는지가 `DashDesignVariableModel`(소속 DOE, DOE-10) 결정이라 `s |
| `04-review/UIC.md:46` | UIC | \| `보류: DOE 몫` \| `DashDoeSamplerResampleWidget.cpp:300-309` 표 셀 2곳의 범위 검증 — 델리게이트 기제 (검토 #10, UIC-c41(b)) \| |
| `03-items/CON.md:66` | CON |  순서 조정으로 흡수한다(항목 분할은 하지 않는다). `setParent(this)` 로 공용 DV 모델 소유권을 빼앗는 줄(:331, CON-c27)은 여기 넣지 않았다 — **보류: DOE 몫**(소유자 결정이 `DashDesignVariableModel` 소관). `saveSettings` 빈 슬롯과 미사용 `JsonKeys` 네임스페이스도 같은 파일에 있으나 원천 밖이라 언급만 한다. |
| `03-items/CON.md:147` | CON | \| Code-Map CON 3-1 (공용 DV 모델 `setParent`) \| 범위밖 → DOE \| 검토 #12 — CON-c27. **보류: DOE 몫** (`DashDesignVariableModel` 소유자 결정). CAD 접점 \| |
| `03-items/UIC.md:300` | UIC | leWidgetItem::text()` 파싱이라 델리게이트 기제. DoeSamplerResampleWidget 2곳 → DOE · OptimizerWidget 1곳 → OPT (`보류: DOE · OPT 몫`) \| |

## → EXE (4행)

| 출처 | 넘긴 모듈 | 내용 |
|---|---|---|
| `04-review/CAD.md:17` | CAD | 14 → "CAD-10 EXE-12" \| 실작업은 CAD-10 단일, EXE-12 는 "데몬 4종 준수 표" 에서 CAD-10 참조만. 한쪽 흡수 목록에서 CAD-D14 제거 \| 보류: EXE 몫 — EXE-12 흡수 목록·대응표에서 CAD-D14 제거는 EXE 파일 수정. CAD 쪽은 CAD-10 비고·대응표에 "실작업 CAD-10 단일 · 보류: EXE 몫" 기재 \| |
| `03-items/CAD.md:127` | CAD |  "CAD-10 과 중복 기록 — Phase B 병합" 미이행) — **실작업은 본 항목 단일**이고 EXE-12 는 "데몬 4종 준수 표" 에서 본 항목을 참조만 해야 한다. `보류: EXE 몫`(EXE-12 흡수 목록·대응표에서 CAD-D14 제거). |
| `03-items/CAD.md:201` | CAD | \| CAD-D14 \| CAD-10 \| EXT. EXE-12 흡수 목록에도 이중 등재 — 실작업은 CAD-10 단일, `보류: EXE 몫` \| |

## → PER (4행)

| 출처 | 넘긴 모듈 | 내용 |
|---|---|---|
| `04-review/DOE.md:16` | DOE |  만 PER-05 헬퍼 사용으로(3번과 함께 축소) · 비고에 "읽기 사본 `loadJsonRoot`·`loadSettings` 는 PER-c03 집계 추가 대상" 1줄 (PER 보류) \| 반영 (`선행: PER-05` 제거 — 3번과 함께 완료 기준 (3) 을 수동 확인으로. 읽기 사본 2곳은 비고 + claims c61 에 기재, `보류: PER 몫`) \| |
| `04-review/LCH.md:13` | LCH | 안 함), #444·PRJ-c07·PRJ-c60 을 LCH-08 에서 이관, "모듈 로드 통째로 읽음" 반쪽은 로드 실측을 재검토 조건으로 기재. PER-03 ⑦ 참조처 치환은 `보류: PER 몫` \| |
| `03-items/DOE.md:151` | DOE | p:28-40` 익명 `loadJsonRoot` — Resample 경로 입구 · `DashDoeConfigManager::loadSettings:59`)도 같이 이행한다 — **보류: PER 몫** (PER-c03 읽기 헬퍼 집계에 이 2곳 추가). `saveToJsonFiles` 는 DV JSON 2종(Geometry·Condition)을 전체 재기록 — 헬퍼 치환만, 절 판정은 DOE-10. DOE Table 전체 재기록 2곳은 유지 — run 단위 id 는 PER-06 결정. `saveDoeToCsv` 는 JSON 이 아니라 |
| `03-items/LCH.md:312` | LCH | - 비고: PER-03 ⑦ "LCH-08 이 분할을 택할 때만" 의 참조처는 이 항목이다 — PER 쪽 문구 치환은 `보류: PER 몫`. 분할 단위 설계를 공유하던 #441 은 LCH-08·LCH-09 로 갔다 |

## → BLD (3행)

| 출처 | 넘긴 모듈 | 내용 |
|---|---|---|
| `04-review/PRE.md:22` | PRE | ct 동형) 기재(신설 행 대신 기존 행 보강 — c59 는 이미 BLD-c34 로 흡수돼 있다) · PRE-29 결정 입력 · PRE-30·31 완료 기준·비고. 파서 변경은 `보류: BLD 몫`·`보류: ANA 몫` \| |
| `03-items/PRE.md:294` | PRE | 답 2개 · 응답 추가가 `root` 첫 자식(학습 데이터)과 샘플 dict 동형을 깨지 않는다(DeepOpt 계약) · 식별자 불일치 시 규칙대로 동작 · BLD 로더 수용은 `보류: BLD 몫`(BLD-14) · ANA 파서는 `보류: ANA 몫` |
| `03-items/PRE.md:304` | PRE |  에만 위상을 두어도 샘플 dict 동형 전제를 깨지 않음을 DeepOpt 계약과 대조(PRE-29 결정) · `TestResultXmlWriter` 통과 · 파서 쪽 수용 — `보류: BLD 몫`(샘플 0 위상으로 나머지 읽기) · `보류: ANA 몫`(`DashXmlParser`) |

## → CAD (2행)

| 출처 | 넘긴 모듈 | 내용 |
|---|---|---|
| `04-review/LCH.md:7` | LCH |  영향 — **LCH-06**: `jobFinished` 방출 2곳이 전부 Journal 경로라 (c) 면 Journal TU 삭제 PR 에 흡수(시그널 자체 삭제), (b) 면 보류(2회 `analysisFinished` 는 `setLauncherIdle(true)`·표 재구축 2회로 무해) · **LCH-27**: (c) 소멸, (b) LCH-19(a) "다중 큐잉 안 함" 으로 `startDirectAnsysJournalJobs` 시그니처를 파일 1개로 좁히는 쪽이 더 작다 · **LCH-28**: 포맷 무관(`setLaunc |
| `03-items/LCH.md:282` | LCH | 경로 수정분을 뺄지) · **LCH-06** · **LCH-27** · **PRJ**(`.wbpj`·`.stli` 원장 편입이 PRJ 코드). CAD 쪽 항목의 `선행` 등록은 `보류: CAD 몫`, PRJ 소비자 등록은 `보류: PRJ 몫`. 축소 내용 — (c) 면 LCH-06 은 Journal TU 삭제 PR 에 흡수(시그널 자체 삭제), LCH-27 은 소멸, PR #651·#652 의 wbpj 분기와 #640 wbpj 사용처(PRE)를 되돌린다 / (b) 면 LCH-27 은 LCH-19(a) 로 대체. **LCH-28 은  |

## → REN (2행)

| 출처 | 넘긴 모듈 | 내용 |
|---|---|---|
| `04-review/OPT.md:17` | OPT | 5·08·09·10·12 추가. 비고에 REN-10 이 OPT-01 을 선행으로 두므로 RM 직렬 사슬에서 OPT-01 이 앞이라는 관계를 적음. REN 직렬 규칙 목록 등재는 `보류: REN 몫` \| |
| `03-items/OPT.md:15` | OPT | ngManager 직렬 사슬에서 OPT-01 이 REN-10 보다 앞에 온다 — REN 의 직렬 규칙 목록(REN-05·07·08·09·10·12)에 OPT-01 을 넣는 것은 `보류: REN 몫`. 소유자 태그·질의는 #318 몫 — 여기서는 태그 없이 성립. #315(Load 재클릭 게이트) 의 선행. |

## → MOR (1행)

| 출처 | 넘긴 모듈 | 내용 |
|---|---|---|
| `04-review/PRJ.md:12` | PRJ | 뿐 \| PRJ-04 목표·완료 기준·변경 범위에 두 접근자와 두 멤버를 추가한다(한 개념 — DashManager 의 씬·인터랙션 접근 경로 끊기). MOR 이 소유를 주장하면 `보류: MOR 몫` 으로 넘기되 호출부가 PRJ 파일이므로 PRJ-04 가 맞다 \| 반영 — PRJ-04 의 목표·완료 기준 (1)·변경 범위에 `GetHandlePickingInteraction`·`GetHandleVisualizer` 와 `m_handlePicking`·`m_handleVisualizer` 를 넣고 `view/DashMainWindow. |

