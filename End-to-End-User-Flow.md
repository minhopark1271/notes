
> 좌표 기준: `dev` 커밋 `4c7608e` 실측 (2026-08-31 전면 재검토)
> 검증 수준: **정적 코드 근거만** — 빌드·실행 검증 없음. 런타임 조건부 표시·활성화는 반영 누락 가능
> 모듈 내부에서 도는 코드는 [Code-Map-User-Flow](Code-Map-User-Flow.md), 저장 단위와 Set 계보는 [Project-Store-Survey-Inputs-Payloads-Runtime](Project-Store-Survey-Inputs-Payloads-Runtime.md) 2절, 키 단위 입출력은 [Project-Store-Survey-Key-IO-Ledger](Project-Store-Survey-Key-IO-Ledger.md)

Phase 순서는 사이드바 모듈 트리의 카테고리 등록 순서(`DashProject.cpp:62-69`)다. 다만 모듈 간 결합은 호출이 아니라 **선행 산출물 파일 스캔**이라, 순서는 강제가 아니라 "선행 산출물이 있으면 진행 가능" 이라는 느슨한 제약으로만 구현되어 있다.

## 전체 흐름

```
[Phase 0] 프로젝트 준비
   │   1. Project > New — `{parent}/{ProjectName}/` 과 숨김 폴더 `.{ProjectName}.dproj/configs/` 생성
   │      프로젝트 파일(`.dashopti` 등)은 존재하지 않는다. Open 은 폴더를 골라 `.*.dproj` 를 찾는다
   │   2. [Add File] 로 원본 모델을 프로젝트 루트에 복사 → Project 트리 (파일 시스템 뷰)
   │      필터 12종: .dat .inp .vtk .vtu .rst .odb .csv .dfsxml .prt .stp .step .stli
   │   3. Project 트리 행의 [Load] 버튼으로 파일을 연다 (체크박스가 아니다)
   │      .dat/.inp → Modeling 트리 전개 + Mesh View 렌더 + Active Context 등록
   │      .prt → NX 데몬이 STEP 으로 변환 → CAD View(OCCT) 렌더 + CAD Parameter 표 채움
   │      .stli → 로드 대상이 아니라는 안내만 (Analysis Launcher 의 Reference File 로 등록할 것)
   │   4. 사이드바 Solver Path 아이콘 → SolverSettingsDialog 에 솔버 경로 입력
   │      QSettings 에 머신 전역으로 저장 — 프로젝트를 옮기면 따라가지 않는다
   │   ※ Active Context 는 항상 1개다. 바뀌면 Condition Parameterization 위젯이 갱신된다
   ▼

[Phase 1] Geometry Parameterization — Set 생성 시 for Morphing / for CAD 선택
   │   [Morphing] `Morphing` · `DV-Geometry` 2탭
   │      진입 화면 "Select a part from the Modeling Tree..." — Modeling 트리에서 PART 를 골라야
   │      [▶ Start Morphing] 이 활성화된다 (파일 항목을 고르면 눌러도 경고만 뜬다)
   │      Morphing 탭 — Mesh View 위 모드 툴바 6종(Constraints · Manual · Surface · Volume ·
   │                    Physics · Appearance)으로 픽킹 → [Done] 으로 핸들 확정
   │                    Morphing Function: Global Support | Compact Support
   │                    Morphing Handle: Kernel Radius · Straight Sided Element
   │                    핸들 표(No. · Name · Lower · Upper · θy · θz)
   │                    → [Group] · [Ungroup] · [Reset] · [Delete],
   │                       Add Values to Checked Rows → [Apply] 로 체크 행 일괄 가산
   │                    [Lower Preview] · [Upper Preview] 토글로 변형 범위 확인
   │                    → [Set Design Variable] — 이 모듈이 디스크에 쓰는 유일한 지점
   │      DV-Geometry 탭 — 확정된 설계변수 열람
   │   [CAD] `CAD Parameter` · `DV-Geometry` 2탭 (개발 빌드에서만 `Match NSET` 이 추가된다)
   │      CAD Parameter 탭 — Independent Parameter 표에서 행 체크 + Lower/Upper 입력
   │                         Dependent Parameter 는 Value 열람 전용 — 갈림은 NX 데몬이 정한다
   │                         Add Values to Checked Rows → [Apply],
   │                         [Lower Preview] · [Upper Preview] (토글이 아니라 단발)
   │                         → [Set Design Variable] — 원본 `.prt` 를 configs 로 복사한다
   │      ※ Meshing 은 탭이 아니라 Match NSET 탭 안의 버튼(다이얼로그)이고, Match NSET 자체가
   │         `DASH_BUILD_DEV` 전용 + 로직 미구현이다. 즉 CAD 경로에는 해석조건 연결이 없다
   │   산출물: configs/GeometryParameter_Set{N}-Morphing.json + {Set}.vtp
   │           configs/GeometryParameter_Set{N}-CAD.json + configs 로 복사된 .prt
   ▼

[Phase 2] Condition Parameterization  (선택 단계 — 형상만 변수화할 경우 생략)
   │   FE Condition 탭 — Active Context(.inp/.dat)의 조건 표(Source · Name · Type · Value)에서
   │                     Value 인라인 편집 · 행 체크 → [Set Design Variable]
   │                     ※ 편집 스키마가 Continuous 로 분류된 항목만 표에 오른다 (나머지는 부재)
   │   DV-Condition 탭 — Min/Max/Cases 조정
   │   산출물: configs/ConditionParameter_Set{N}.json
   ▼

[Phase 3] Analysis Launcher — Set 생성 시 (기본) / Resample DOE / Direct Launch 선택
   │   [기본 = Init] `DOE configuration` · `DOE Analysis` · `DOE Launcher` 3탭
   │      DOE configuration — Select DV-Geometry / Select DV-Condition 콤보 → [Set] 으로 DV 표 병합
   │                          Sampling Mode: General | Probabilistic (+ Sigma level)
   │                          DV 표(Symbol · Name · Source · Type · Min · Max · Cases)는
   │                             CSV [Download] / [Upload] 로 왕복 편집
   │                          Auto-configuration — Purpose(Training with progressive updating |
   │                             Linear sensitivity analysis) + Sampling scale(Low · Mid · High) → [Set]
   │                          Manual-configuration — Methods 5종 + Use Greedy Algorithm + Option 1·2
   │                             Optimal Latin Hyper Cube / Optimal Latin Hyper Volume /
   │                             Monte Carlo / Orthogonal Array /
   │                             Translational Propagation Latin Hyper Cube
   │                          → [Run] 으로 DOE 표 생성
   │                             같은 Set 에서 다시 [Run] 하면 이전 샘플 셋은 통째로 교체된다
   │      DOE Launcher — Input Reference File 표(Name · Target Component · Solver State · Material)
   │                     에서 템플릿 1개를 라디오로 확정 → Output Cases 표 + CPU cores → [Start]/[Stop]
   │                     ※ 템플릿의 확장자가 실행 워크플로를, basename 이 analysisType(출력 폴더명)
   │                        을 정한다
   │      DOE Analysis — Box Plot · Pair Plot · Scatter Plot
   │   [Resample DOE] `Resampling` · `DOE Analysis` · `DOE Launcher`
   │      Resampling 탭은 UI 만 있고 로직이 없다 — 기존 DOE 에 샘플 추가는 현재 동작하지 않는다
   │   [Direct Launch] 탭 없는 단일 화면 — Input Cases 표(File Name · Solver State · Material)에
   │      [Add Input File] 로 해석 파일을 직접 나열 → CPU cores → [Start]/[Stop]
   │      DOE 생성을 건너뛰는 우회 경로다
   │   산출물: AnalysisLauncher_Set{N}/{analysisType}/runs1..N/
   ▼

[Phase 4] Data Preprocessor
   │   Data Upload — Selected DOE 콤보 → Select Analysis File 콤보
   │                 → "Analysis Type : *" 그룹 체크 → [Load Raw Dataset]
   │                 ※ DOE 콤보 맨 위의 "Import single file ..." 은 Phase 1~3 을 통째로 건너뛰고
   │                    결과 파일 1건만 전처리하는 우회 진입점이다
   │                 ※ 후보 판정은 JSON 이 아니라 파일시스템이 한다 — `runs{N}` 폴더가 있으면 후보다
   │   Preprocess — Component / Load step / Name 을 골라 [▼] 로 Output Response 행을 쌓고
   │                [▲] 로 제거 → [Preview] → [Process]
   │                General ↔ Custom KPI 토글 — KPI 목록은 빌드 타깃이 정하고 개발 빌드에는 없다
   │                   LGE_CompCBlock: Circularity
   │                   LGE_CompSpring: Max. Side Force · Modal Frequency
   │                   ILJIN_TensionLink: Max. PEEQ · Critical Buckling Load · Min. Fatigue Life
   │   Data Analysis — Box · Scatter · Parallel · Pair Plot
   │   산출물: DataPreprocessor_Set{N}/{Component}_{step}_{substep}_{Name}.xml
   ▼

[Phase 5] Model Builder — Set 생성 시 for General / for MCU 선택
   │   Data Label — Select DataPreprocessor Directory + Select Dataset (.xml) → [Load]
   │                → shape 차원으로 갈린 Input / Output 표(Name · Shape · Reduction,
   │                   Output 은 Transformation 추가)를 [▲][▼] 로 옮기고 체크 → [Set Dataset]
   │                MCU 는 CSV/Excel 파일 표 — [Add] 로 행을 늘리면 헤더 검증 결과가 State 에 뜬다
   │   Configuration — Available Models 표에 [Add] / [Delete] + 모델·하이퍼파라미터 지정
   │                   → [Start AI Training] / [Stop]
   │                   실제 학습은 외부 도구(`DashOptiDeepOpt.exe`, MCU 는 상주 데몬)가 한다.
   │                   GUI 는 프로세스 종료 통지와 JSON 의 status 로만 진행을 안다
   │   Test Results — Configuration 에 ND 모델이 있을 때만 활성화된다
   │                  Output Response · Trained Model · Test Dataset → [Preview]
   │   산출물: .dproj/ModelBuilder_Set{N}/ 의 model_info.json + 학습된 대리모델
   │           MCU 는 프로젝트 루트 쪽에 쌓이고 인코딩된 C 헤더가 함께 나온다
   ▼

[Phase 6] Model Runner — 예측·민감도 (for General / for MCU)
   │   Model Upload — ModelBuilder 폴더 콤보 → 대리모델 표(Symbol · Response · Model ·
   │                     R2 · MAPE 계열)에서 사용할 행 체크
   │                  → Input Design Variables 표(Parameter · Source · Value · Min · Max) 입력
   │                     (CSV [Download] / [Upload])
   │                  → [Generate Input File] — 파일을 만드는 유일한 지점. 설계변수 출처에 따라
   │                     Morphing · CAD · Condition 으로 갈려 VTU 와 해석 입력파일을 만든다
   │                  → Analysis Input Files 표에서 [Preview] 로 형상 확인 → [Run AI Prediction]
   │                  MCU 는 입력 CSV + Smoothing Window Size 를 지정해 시계열을 예측한다
   │   Sensitivity Analysis — Sobol Indices · Morris Method · SHAP
   │   산출물: ModelRunner_Set{N}/ 의 VTU·해석 입력파일
   │           예측값과 민감도 플롯은 화면에만 남는다
   ▼

[Phase 7] Optimizer
   │   Optimization — ModelBuilder 폴더 + 응답별 대리모델 선택
   │                  Design Variables 표에서 Fixed 체크 · Init. Value 입력
   │                     (Min · Max · Mean · Std 는 읽기 전용 — 상류에서 정해져 내려온다)
   │                  Configuration — Objective Function(Minimize | Maximize) + 수식,
   │                     Constrained Functions [+] / [-], Methods + Option 1·2
   │                  → [Run Optimizer] — 계산은 외부 도구(`DashOptiDeepOpt.exe`)가 한다
   │                  ※ Deterministic / Reliability-based 는 UI 선택지가 아니다. 모드 콤보는
   │                     숨겨져 있고, model_info.json 의 파라미터 메타에 mean·std 가 숫자로
   │                     있으면 RBO 로 잠긴다 — Phase 3 의 Probabilistic 선택이 여기까지 이어진다
   │   Validation — Objective & Constraints · Design Variables · Response 표에 후보해를 이어 붙인다
   │                Add Candidate Solution: [Add Neighbor] · [Add Trajectory] ·
   │                [Add MPP](RBO 일 때만 노출) → DV 열을 골라 [Render Preview]
   │   Results Analysis — Convergence History · Pareto Front
   │   산출물: Optimizer_Set{N}/optimum.json + [Render Preview] 가 만든 Preview_*.dat/.inp/.stp
   ▼

[운영 관점] 모든 모듈은 Set 단위 다중 구성
       설정은 configs/{Module}_{Set}.json 에, 산출물은 프로젝트 루트의 {Module}_{Set}/ 에
       쌓인다 (ModelBuilder 산출물만 숨김 폴더 안쪽). 프로젝트 재오픈 시 복원은
       DashProject::loadSetsFromConfigs() 의 configs 파일명 접두사 스캔이 전부여서 어느
       Phase 든 재진입은 되지만, Set 번호는 카테고리마다 독립이고 상·하류 Set 의 연결은
       화면 어디에도 표시되지 않는다
```
