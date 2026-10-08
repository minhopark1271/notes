# 작업 목록 재작성 — 계획·틀·형식

> 목적: GitHub Projects #16 (refactoring) 의 미종결 이슈 112건을 참고 자료로 삼아, **모듈별 작업 목록을 처음부터 다시 쓴다.** 작업 1건 = PR 1건 크기를 지향한다. 구 분류 축(A~G)은 각 작업이 어느 측면과 관련 있는지 재는 **태그**로만 쓴다.
> 산출물은 전부 이 폴더(`notes/new_tickets_claude/`)에 둔다. **이슈·위키·PR 발행 금지. 코드 수정 금지.** `gh` 는 읽기 전용(`issue view`·`pr list`·`pr view`)만 허용.
> 코드 기준: `DashOpti_GUI` `dev` @ `b08a91b3` (2026-10-05). 모든 좌표는 이 커밋에서 재확인한 것만 적는다.

## 1. 틀 (결정)

### 1-1. 모듈 축 (16종)

| 코드 | 모듈 | 코드 영역 (주요) | 결함 색인 prefix |
|---|---|---|---|
| MOR | Geometry Parameterization — Morphing | `view/DashGeometryParameterWidget*`, `viewmodel/DashGeometryParameterPresentationModel`, `model/DashGeometryParameter`, `controller/DashMorphing*`, `controller/DashHandle*`, `controller/DashGizmoPlane`, `controller/DashFixed*`, `controller/DashMeshQc*`, `controller/DashPreview*`, `libs/DashGizmo`, `libs/DashMarchingPlane`, `view/overlay/DashMorphingSettings` | MOR |
| CAD | Geometry Parameterization — CAD (NX) | `view/DashGeometryParameterCADWidget`, `viewmodel/*CADPresentationModel`, `model/DashGeometryParameterCAD`, `controller/DashSolverNxCad`, `view/DashOcctViewWidget` | CAD |
| CON | Condition Parameterization | `view/DashConditionParameterizationWidget`, `viewmodel/*ConditionParameterizationPresentationModel`, `model/DashConditionParameterization`, `view/delegate/*FeCondition*` | CON |
| DOE | DOE Sampler (Init · Resample) | `view/DashDoeSampler*`, `viewmodel/DashDoeSamplerPresentationModel`, `model/DashDoeSampler`, `model/DashDoeSelection`, `model/DashDoeConfigManager`, `model/DashDesignVariableModel`(CON·CAD·MOR 공용 — 소속 DOE, B2) | DOE (샘플링 부분) |
| LCH | Analysis Launcher — Launcher 탭 · 배치 실행 · Direct Launch | `view/DashAnalysisLauncherWidget*`, `view/DashDoeCasesWidget`, `view/DashReferenceFileWidget`, `model/DashJobRunner*`, `model/DashAnalysisLaunchExecutor`, `controller/DashDoeBatchChain`, `controller/DashMorphingDoeExecutor`(배치 호출부), `model/DashAnalysisLauncher`(실행 경로) | DOE (실행 부분) |
| PRE | Analysis Launcher — Preprocess 탭 · 결과 리더 · 응답 카탈로그 · 질의 · 결과 XML 작성 · KPI | `model/DashAnalysisLauncher`(결과 처리 경로), `model/DashAnalysisLauncherKPI`, `model/preprocessor/*`, `model/extensions/*`, `view/DashAnalysisLauncherWidget`(Preprocess 탭) | PRE |
| BLD | Model Builder (Sim · MCU) | `view/DashModelBuilder*`, `viewmodel/DashModelBuilderPresentationModel`, `model/DashModelBuilder*`, `model/builder/*` | BLD |
| RUN | Model Runner (Sim · MCU) | `view/DashModelRunner*`, `viewmodel/DashModelRunner*PresentationModel`, `model/DashModelRunner*` | RUN |
| ANA | Results Analyzer (임베디드 패널 · 플로터 · XML 파서) | `view/DashResultsAnalyzerWidget`, `view/analyzer/*`, `model/analyzer/*` | ANA |
| OPT | Optimizer | `view/DashOptimizerWidget`, `viewmodel/DashOptimizerPresentationModel`, `model/DashOptimizer`, `viewmodel/DashSurrogateModelCommon` | OPT |
| PRJ | Project · Set 수명 · Project Assets · Module Tree · MainWindow 셸 · 메뉴 다이얼로그 | `view/DashMainWindow`, `view/DashProjectWidget`, `view/DashModelingTreeWidget`, `view/DashTitleBar`, `view/dialog/*`, `controller/DashProjectManager`, `controller/DashManager`, `controller/DashIOController`, `model/DashProject`, `model/DashSet*`, `model/DashReferenceModelLedger`, `model/DashUpstreamStaleness`, `persistence/*` | — |
| REN | VTK 씬 · 렌더링 매니저 · actor 소유권 | `controller/DashRenderingManager`, `controller/DashAnalysisModelContext*`, `controller/DashVtkLogBridge`, `controller/DashInteractorStyleSelection`, `view/overlay/DashViewOptionsWidget` | — |
| EXE | 실행 기반 — 비동기 Job · 워커 · 외부 프로세스 · 데몬 · 진행 표시 표준 · 스레드 계약 | `controller/async/*`, `controller/DashExtensionProcess`, `controller/DashDaemonLifecycle`, `controller/DashThreadAffinity`, `controller/DashCpuTopology`, `controller/DashRwActor*`, `controller/DashRwDocument*`, `controller/DashTopOptPostprocessRunner`, `model/DashJobRunnerCae` 공통부 | — |
| PER | 영속화 · 식별자 · 산출물 대장 · 저장 포맷 | `utils/DashGadgetCodec`, `persistence/*`(포맷 규칙), JSON 읽기·쓰기 헬퍼, 산출물 스탬프·대장 | — |
| UIC | UI 공통 — 창·레이아웃·DPI · 통지 래퍼 · 입력 검증 · 표 헬퍼 · i18n · 툴바 | `view/common/*`, `view/DashWheelScrollSuppressor`, `ui/*`, `resources/*`, `view/log/*` | — |
| DEV | 개발 환경 · 빌드 · CI · 테스트 인프라 · 출고 품질 | `CMakeLists.txt`, `cmake/`, `scripts/`, `tests/`(인프라), `vcpkg*`, `triplets/`, `tools/`, `docs/` | — |

배정 규칙 — 작업이 여러 모듈을 지나면 **변경 파일이 가장 많은 모듈**이 주 모듈, 나머지는 `접점` 으로 적는다. 결함 색인 `DOE-*` 는 샘플링이면 DOE, 실행이면 LCH 로 항목마다 판단한다.

### 1-2. 작업 단위

- **1 작업 = 모듈 1개 · 기제 1개 · 끝에서 빌드·테스트 통과 · 동작 변경과 리팩터 혼합 금지.** 크기 상한은 두지 않는다. 기제가 둘 이상이면 나눈다.
- 분할 기준은 **개념적 응집** (2026-10-06 보정). 엄밀한 1기제 분리보다 개념적으로 잘 나뉘는지가 우선 — 한 개념 덩어리로 읽히면 기제가 둘이거나 동작 변경·리팩터가 일부 섞여도 쪼개지 않는다. 쪼개는 것은 개념이 둘일 때, 합치는 것은 개념상 하나인데 잘게 나뉘었을 때.
- 규모는 `S`(파일 3개 이하 · 반나절) / `M`(파일 8개 이하 · 1~3일) / `L`(그 이상) 로만 표기한다. `L` 은 분할 사유가 없을 때만 허용하고 사유를 적는다.
- 종류 5종:

| 종류 | 뜻 |
|---|---|
| `PR` | 코드 변경 1건 |
| `DEC` | 결정만 필요. 산출물은 기록된 결정 |
| `INV` | 실측·재현·조사가 선행. 결과에 따라 PR 이 생긴다 |
| `EXT` | 다른 저장소(Registry · 메타 · mesh-ops · DashOptiMBD · Preprocessor)의 작업. GUI 쪽은 추적만 |
| `CLOSE` | 새 목록에 실작업이 없는 기존 이슈 — 추적 전용 · 해소됨 · 중복. 닫기 제안 사유를 적는다 |

### 1-3. 진행 중 작업

In progress(#281 #433 #434 #443) · In review(#368 #604 #616)는 열린 PR 을 그대로 두고 **잔여분만** 새 항목으로 쓴다. 잔여 판정은 `gh pr list --state open` 과 본문의 체크리스트로 한다.

### 1-4. 태그

구 분류 축을 태그로 쓴다. 항목마다 1개 이상.

| 태그 | 측면 |
|---|---|
| A | 데이터 무결성 — 저장·로드 왕복, 파일 파손, 상태 격리 |
| B | 실행 모델 — 스레드, 펌핑, 프로세스, 배치 관리, 진행 표시 |
| C | 데이터 모델·식별자 — Set·산출물·기준 모델의 id·원장·스탬프 |
| D | UI 표준화 — 창·레이아웃, 통지, 입력 검증, 표 |
| E | 코드 구조 — 책임 분해, 의존 방향, 중복 제거, 죽은 코드 |
| F | 개발 인프라 — 빌드, CI, 테스트, 의존성 |
| G | 출고 품질 — 개발 잔재, 버전, 라이선스, i18n |

보조 태그: `bug`(현재 오동작) · `feature`(없는 기능) · `refactor`(동작 불변) · `perf` · `docs`.

### 1-5. 금지

이슈·PR·위키·코멘트 발행 금지. 코드 수정 금지. 보드 변경 금지. `gh` 쓰기 금지. 이 폴더 밖에 파일을 만들지 않는다.

## 2. 원천 자료

| 경로 | 내용 | 신뢰도 |
|---|---|---|
| `01-sources/open_issues/<N>.md` | 미종결 이슈 113건 전문 + 메타(status · iteration · labels · parent · sub-issues). #442 는 GitHub 에서 닫혔으나 보드에 남음 | 정의는 정확, **좌표(행 번호)·건수·전제는 낡음**. 특히 LCH·PRE 는 #617·#433 스택 이후 크게 바뀜 |
| `01-sources/closed_issues.md` | Done 74 · Won't do 20 | "이미 해소/기각" 판정 사전 |
| `01-sources/relations.json` | 부모·자식 관계 | 정확 |
| `01-sources/defects/<PREFIX>.md` | 위키 Cross-Module-Defect-Index 201건을 모듈 prefix 로 분할 | `cf44c25` 기준 정적 판정. **런타임 검증 없음, 이후 수정분 미반영.** 현행 코드 재검증 필수 |
| `01-sources/wiki/Code-Map-User-Flow-*.md` | 모듈 9종 사용자 플로우 ↔ 코드 대응 (결함 색인의 원문, 좌표 포함) | 좌표 낡음. 결함 설명 전문은 여기서 본다 |
| `01-sources/wiki/Cross-Module-Defect-Index.md` | 결함 색인 원본 (성격 17종) | 위와 같음 |
| `01-sources/wiki/Backlog-Reclassification-And-Status.md` | 구 분류 A~G 정의 · 35건 상태 | 태그 정의의 정본 |
| `01-sources/wiki/Backlog-Issue-Publication-Plan.md` | 64건 발행 계획 · 중복 판정 | 이슈 간 관계 참고 |
| `01-sources/wiki/Multi-Display-DPI-Scaling-Breakage.md` | 창·DPI 결함 25건 카탈로그 | UIC 의 원천 |
| `01-sources/wiki/215-2-sync-pumping-to-async-conversion-checklist.md` | 펌핑 제거 체크리스트 | EXE·모듈별 펌핑 항목 참고 |
| `01-sources/wiki/Project-Manifest-*.md`, `Handle-Data-View-Separation.md`, `281-1-*.md`, `246-1-*.md`, `269-1-*.md`, `Code-Map-Data-Ownership.md` | 설계 결정 문서 | 결정 내용은 유효, 상태 열은 낡음 |
| 코드 `dev` @ `b08a91b3` | 유일한 현재 사실 | — |

## 3. 과정

```
[Phase A] 모듈별 수집·검증·항목화 (모듈당 subagent 1개, 병렬)
   │   1. 담당 이슈(6절 배정표)와 결함 색인을 원자 항목으로 분해 → 02-claims/<MOD>.md
   │   2. 항목마다 dev HEAD 에서 재확인 — 심볼·패턴 검색으로 판정(유효/해소됨/미확인)과 현행 좌표 기록
   │   3. 유효 항목을 1-2 규칙으로 작업 단위로 묶음 → 03-items/<MOD>.md
   │   4. 보고는 10줄 이내 — 결과는 파일에만
   │   검증: 담당 이슈 전부가 claims 에 나타나고, items 의 흡수 원천이 claims 를 전부 덮는다
   ▼

[Phase B] 횡단 정합 (orchestrator + subagent 1개)
   │   1. 모듈 간 중복 항목 병합 · 주 모듈 재배정
   │   2. 모듈 간 선행·같은 파일 동시 수술 금지 쌍 → 05-final/deps.md
   │   3. 구 이슈 112건 → 새 항목 대응표, 결함 201건 → 새 항목 대응표 → 05-final/mapping.md (스크립트로 누락 검사)
   ▼

[Phase C] 독립 검토 (모듈당 reviewer subagent 1개, 병렬)
   │   1. 원천 대비 누락 · 이미 해소된 항목 잔존 · 기제 혼합 · 근거 없는 좌표 지적 → 04-review/<MOD>.md
   │   2. 지적 반영 (수정 subagent) → 03-items 갱신
   ▼

[Phase D] 납품
       05-final/FINAL.md — 모듈별 작업 목록 전체 + 요약 표 + 대응표 + 의존표
```

진행 상태는 `00-progress.md` 에 기록한다. orchestrator 는 결과 파일을 통째로 읽지 않고 요약·검증 스크립트 출력만 본다.

## 4. 형식

### 4-1. `02-claims/<MOD>.md`

```
# <MOD> 원자 항목

| CID | 현상 / 목표 | 근거 (dev @ b08a91b3 파일:함수) | 원천 | 판정 | 비고 |
|---|---|---|---|---|---|
| MOR-c01 | ... | controller/DashMorphingController.cpp:selectHandlesGreedyByUnit | #332-2 · MOR-D3 | 유효 | ... |
```

- `CID` = `<MOD>-cNN`. 이슈 1건이 여러 원자 항목이면 전부 분리한다 (#319 4건 · #331 3건 · #336 4건 · #370 부수 4건 · #514 5건 등).
- `원천` = 이슈 번호(하위 항목이면 `#331-2`), 결함 ID(`RUN-D34`), 위키 페이지명. 여러 개면 `·` 로 잇는다.
- `판정` = `유효` (코드에 아직 있음) / `해소됨` (dev 에서 이미 고쳐짐 — 근거 커밋·PR 또는 코드 부재) / `미확인` (런타임 재현 필요 · 외부 환경 필요) / `범위밖` (다른 모듈 소관 — 어느 모듈인지 비고에).
- 담당 이슈 중 추적 전용 부모(실작업 없음)는 CID 1행으로 적고 판정 `CLOSE`.

### 4-2. `03-items/<MOD>.md`

항목마다 아래 블록. 번호는 `<MOD>-NN` (01부터).

```
### MOR-01 · <제목: 동사형 한 문장>
- 종류: PR | 규모: M | 태그: A, E · refactor
- 목표: 한두 문장. 무엇이 어떻게 달라지는가
- 완료 기준: 확인 가능한 조건 1~3개
- 변경 범위: 파일 목록 (dev @ b08a91b3 에서 확인한 것만)
- 선행: MOR-03, PER-01 (없으면 `-`)
- 충돌: 같은 파일을 고치는 다른 항목 · 진행 중 PR (없으면 `-`)
- 흡수: #332-2 · MOR-D3 · MOR-c01, MOR-c07
- 비고: 설계 논점, 대안, 주의 (선택)
```

- `DEC`·`INV`·`EXT`·`CLOSE` 도 같은 블록을 쓰되 `완료 기준` 에 "결정 기록" / "실측 결과" / "외부 저장소 PR" / "닫기 사유" 를 적는다.
- 파일 끝에 `## 대응표` — `원천 → 항목` 표. 담당 이슈·결함 ID 전부가 한 행씩 있어야 한다 (항목 없음이면 사유).

### 4-3. `04-review/<MOD>.md`

| # | 대상 (항목 ID 또는 "누락") | 지적 | 근거 | 조치 제안 |
|---|---|---|---|---|

## 5. subagent 운용

- 종류 `general-purpose`. 프롬프트는 `00-prompts.md` 의 템플릿에 모듈 코드만 바꿔 넣는다. 템플릿은 이 문서를 먼저 읽게 한다.
- 결과는 파일로만. 보고는 10줄 이내(항목 수 · 판정 분포 · 미확인 사유 · 주 모듈 재배정 제안).
- 코드 조회는 `Grep`·`Read`·`git grep`·`git log -S` 로. 심볼 단위 조회가 필요하면 Serena 를 쓴다. 코드 수정·빌드 금지.
- `gh` 는 `issue view`·`pr list`·`pr view`·`pr diff` 만. **항상 `--repo NumeRealWorks/DashOpti_GUI` 를 붙인다** (원격이 SSH alias 라 자동 해석 실패). 열린 PR 과 변경 파일 목록은 `01-sources/open_prs.md` 에 있다.

## 6. 모듈별 담당 이슈 배정

주 모듈 1개에만 담당으로 넣는다. 접점은 참고용. 괄호 `(추적)` 은 실작업 없는 부모 — `CLOSE` 후보.

| MOD | 담당 이슈 | 접점 이슈 | 결함 | 추가 원천 (01-sources/wiki/) |
|---|---|---|---|---|
| MOR | #281 #512 #563 #499 #332 #430 #427(추적) #322 #331 #557 #423 | #316 #318 #319 #403(닫힘) | MOR | Handle-Data-View-Separation · 281-1 |
| CAD | #249 #464 | #457 (OPT-D19 가 #249 태그 왕복에 의존) | CAD | Project-Manifest-CAD-Path-Disposition |
| CON | — | #645 #551 | CON | Code-Map-User-Flow-Condition-Parameterization |
| DOE | #615 #649(추적) | #502 #443 #368 | DOE (샘플링) | Project-Manifest-3 · 4 |
| LCH | #456 #580 #438(추적) #439 #440 #441 #444 #442(닫힘) #502 #604 #616 #647 #648 #639 #646 | #433 #454 #470 #368 #269(닫힘) | DOE (실행) | Project-Manifest-4 (G8·G9) · 269-1 |
| PRE | #433 #454 #494 #630 #631 #634 #635 #636 #637 #638 #643 #411 | #368 #405 #459 #413(닫힘) | PRE | Code-Map-User-Flow-Data-Preprocessor · Preprocessor-XML-Generation-And-Provenance |
| BLD | — | #643 #650 #368 | BLD | Code-Map-User-Flow-Model-Builder · Model-Builder-XML-DeepOpt-Pipeline |
| RUN | #369 #370 #513 #473(추적) #474 #475 #477 #653 | #368 #514 #458 | RUN | Project-Manifest-4 (G10) |
| ANA | #405 #519 #459 #305 | #411 #553 | ANA | — |
| OPT | #316 #457 | #653 #249 #368 #281 | OPT | — |
| PRJ | #443 #562 #551 #431 #432 #434 #376 #645 #650 #485 #486 #481 #488 #455 #246(추적) #247(추적) #239(추적) | #320 #433 #444 #615 | — | 246-1 · Project-Manifest-Set-Identity-And-Decision-Revisions · Code-Map-Data-Ownership |
| REN | #318 #319 #320 | #316 #322 #430 | — | — |
| EXE | #451(추적) #460(추적) #461 #462 #463 #465(추적) #466 #467 #468 #469 #543 #553 #458 #552(보드 밖) | #454 #456 #457 #512 #513 #281 | — | 215-2 · 203-2 |
| PER | #478 #479 #480 #470(추적) #471 #368 | #443 #473 #638 | — | Project-Manifest-Set-Identity-And-Decision-Revisions |
| UIC | #446(추적) #447 #448 #449 #450 #482 #487 #490 #508 #514 | #466 #370(부수 4건) | — | Multi-Display-DPI-Scaling-Breakage |
| DEV | #330 #335 #336 #372 #386 #489 #483 #484 | — | — | — |

B2 배정 변경(2026-10-05): #368 LCH→PER(PER-06·07, 홉별 T27→DOE-16 · T21→PRE-32 · T22→BLD(PR #530) · T23→RUN·OPT 접점) · #444 PRJ→LCH(LCH-08) · #458 RUN→EXE(EXE-22, dfsxml 몫 LCH-12) · #552(보드 밖) EXE(EXE-02) · #281 MOR 에서 CLOSE(MOR-18, 잔여 OPT-04·22) · DOE-01→PRJ-33 · DOE-04→PRJ-24 병합 · `DashDesignVariableModel` 소속 DOE(CON-08→DOE-10 병합).

횡단 모듈(PRJ · REN · EXE · PER · UIC · DEV)은 결함 prefix 가 없다. 사용자 모듈 담당이 `범위밖` 으로 넘긴 결함을 Phase B 에서 횡단 모듈 항목에 흡수한다.
