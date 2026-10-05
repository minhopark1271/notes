# 키 단위 쓰기·읽기 왕복 대장 — 저장 구조 현황

> **이 문서는 단독으로 읽힌다.** 아래는 근거의 출처이지 서술의 일부가 아니다 — 인용할 사실은 본문에 다시 적었다.
>
> * [Project-Store-Design-Layer-Cut](Project-Store-Design-Layer-Cut.md) — 검증 대상 설계 (계층 재단과 배치) · [Project-Store-Design-Rationale](Project-Store-Design-Rationale.md) — 그 설계의 근거
> * [Project-Store-Survey-Inputs-Payloads-Runtime](Project-Store-Survey-Inputs-Payloads-Runtime.md) — 이 대장의 **여집합**. 입력 셋(Morphing/CAD) · 페이로드 내부 형식 · 실행 상태가 파일에 닿는 경로
>
> 관련 Issue: #239
> 측정 시점: `dev` @ `4c7608e` — 라인 앵커 전부 이 커밋 기준. 선행 조사의 승계가 아니라 **재측정**이다
> 검증 수준: 정적 코드 근거만 — 빌드·실행 검증 없음 · 외부 도구(exe) 내부 미확인 · "리더 0곳" 은 키 리터럴 grep 기준이라 변수로 조립되는 접근은 놓칠 수 있다 · 페이로드 파일 **내부** 구조는 범위 밖 (가리키는 키만 잰다)

## 개요

GUI 가 프로젝트에 **무엇을 저장하고 그중 무엇을 다시 읽는지**를 키 단위로 전수 조사한 대장이다. 묻는 것은 하나 — 쓰는 키 하나하나에 그 값을 다시 읽는 코드가 있는가.

**파일 12패턴에 키 65개를 쓰고, 그중 13개는 읽는 코드가 0곳이다.** 읽히지 않는 13개가 "저장했는데 다시 열면 복원되지 않는다" 계열의 파일 측 실체이고, 라이터가 2벌 이상인 파일 4종이 "같은 값이 두 경로로 써진다" 계열의 실체다.

싣는 것 — 읽는 법(0절) · 저장물 인벤토리(1절) · 모듈별 키 전수(2절) · 왕복 대장(3절) · 다중 라이터(4절) · I/O 시점(5절) · 귀속·성격 분류(6절).

---

## 0. 읽는 법

**판정 4값** — **왕복**: 쓰고 읽는다 · **일방**: 쓰기만 하고 리더 0곳 · **역방향**: GUI 는 읽기만 하고 라이터는 외부 도구 · **고아**: 리더만 있고 라이터가 없다. "리더 0곳" 은 **그 값이 프로그램의 어떤 동작에도 영향을 주지 않는다**는 뜻이다 (파일에는 남는다. 외부 도구의 소비 가능성은 3.3 에서 따로).

**좌표** — `MB:773` = 클래스 약칭 + 줄번호. `PM` 은 해당 모듈의 PresentationModel(`viewmodel/`), `MB`·`MCU`·`MR`·`Opt`·`AL` 은 `DashModelBuilder`·`DashModelBuilderMCU`·`DashModelRunner`·`DashOptimizer`·`DashAnalysisLauncher`, `helper` 는 `model/builder/ModelBuilderConfigHelper.cpp`, `{Set}` 은 Set 이름(`Set1-Morphing` 등)이다.

**`MOR-D5` 류 코드**는 별도 결함 대장의 번호다. "이 실측이 그 결함의 파일 측 근거" 라는 표시로만 인용하고 내용은 다시 설명하지 않는다 — 번호를 몰라도 본문은 완결된다.

**키** = JSON 필드 하나 (중첩은 `DOE Table.samples[].status` 경로 표기), **config** = `{Module}_{Set}.json`, **페이로드** = config 가 가리키는 불투명한 대용량 파일, **variant** = 같은 모듈의 갈래.

---

## 1. 저장물 인벤토리

### 1.1 루트 3개와 배정

| 루트 | 경로 | 들어가는 것 |
|---|---|---|
| 숨김 config | `{Root}/.{Project}.dproj/configs/` | `{Module}_{Set}.json` 전 9종 + Morphing `.vtp` + 복사된 `.dat`·`.prt` |
| 숨김 산출 | `{Root}/.{Project}.dproj/ModelBuilder_{Set}/` | ModelBuilder **Sim** 산출물만 |
| 사용자 루트 | `{Root}/` | 나머지 전 모듈 산출 + ModelBuilder **MCU** 산출 + [Add File] 한 원본 |

**"어느 모듈 산출물이 숨김이고 어느 것이 사용자 루트인가" 에 답하는 자리가 넷인데 서로 다른 답을 낸다.** 실질 쟁점은 Optimizer 하나, 예외로 MCU 가 붙는다.

| # | 자리 | 무엇이라고 말하나 |
|---|---|---|
| 1 | `ModuleType` enum 주석 (`controller/DashIOController.h:22-24`) | `// Internal Data: Uses ProjectPath (hidden from user)` 그룹에 **ModelBuilder 와 Optimizer 둘 다** |
| 2 | doc-comment 2곳 (`:38-40` · `:64-65`) | `Internal Data` 와 `User Output` **두 분류에 같은 경로**를 적어 구분이 무의미하다 |
| 3 | `getModuleDir()` 구현 (`.cpp:31`) | `if (type == ModuleType::ModelBuilder)` 한 줄만 숨김 → **Optimizer 는 사용자 루트** |
| 4 | `isUserOutputType()` (`.cpp:106-112`) | AnalysisLauncher·DataPreprocessor·ModelRunner·ResultsAnalyzer 만 true → **Optimizer 제외** (3번과 반대) |

**실제 거동은 3번 + MCU 우회다** — MCU 는 `getModuleDir()` 을 건너뛰고 `getUserPath()` 에 직접 `ModelBuilder_{Set}` 을 붙여(`model/DashModelBuilderMCU.cpp:554-562`) **같은 `ModelBuilder_` 접두사 디렉토리가 숨김측(Sim)과 사용자측(MCU) 양쪽에 갈려 존재한다.** 4번이 지금 무해한 이유는 **호출부가 0곳**이기 때문이고(참조는 선언 `:131`·정의 `:106` 뿐), 그 doc-comment 는 `@return true if module uses ProjectRootDir, false if uses ProjectRootDir`(`:130`) — **참과 거짓의 설명이 같은 문자열**이다.

### 1.2 파일 패턴 12종

| # | 파일 패턴 | 루트 | 포맷 | 생산자 | 소비자 |
|---|---|---|---|---|---|
| 1 | `GeometryParameter_{Set}.json` | configs | JSON | GUI 2곳 + DV 모델 | GUI 8곳 |
| 2 | `GeometryParameter_{Set}.vtp` | configs | VTK XML PolyData | GUI 1곳 | GUI 2곳 |
| 3 | `ConditionParameter_{Set}.json` | configs | JSON | GUI 1곳 + DV 모델 | GUI 4곳 |
| 4 | `AnalysisLauncher_{Set}.json` | configs | JSON | GUI **6곳** | GUI 9곳 |
| 5 | `DataPreprocessor_{Set}.json` | configs | JSON | GUI 4곳 | GUI 1곳(스냅샷만) |
| 6 | `ModelBuilder_{Set}.json` | configs | JSON | GUI 3곳 + **외부 도구** | GUI 4곳 + 외부 도구 |
| 7 | `ModelRunner_{Set}.json` | configs | JSON | GUI 4곳 | GUI 2곳 + 외부 도구 |
| 8 | `Optimizer_{Set}.json` | configs | JSON | GUI 1곳 | GUI 3곳 + 외부 도구 |
| 9 | `AIGeometryGeneration_{Set}.json` | configs | JSON | 경로 하드코딩 (IOController 우회) | — |
| 10 | `model_info.json` | 모듈 산출 dir | JSON (**비표준** — NaN·Infinity) | GUI + **외부 도구** | GUI 4곳 |
| 11 | `optimum.json` | `Optimizer_{Set}/` | JSON | **외부 도구 전용** | GUI 4곳 |
| 12 | `doe_table_{base}.csv` · `*.xml` · `*.pt` · `*.vtu` · 케이스 입력·결과 | 사용자 루트 | 혼합 6종 | GUI · 솔버 · 외부 도구 | (내부 구조는 범위 밖) |

`ResultsAnalyzer_{Set}` 은 **config 도 산출 디렉토리도 없다.** `getModuleDir(ResultsAnalyzer, …)` 의 유일한 용도는 플롯 내보내기 다이얼로그의 초기 디렉토리다(`view/DashResultsAnalyzerWidget.cpp:3302`).

### 1.3 프로젝트 매니페스트는 없다

`.dproj/` 안에 프로젝트를 기술하는 파일이 없다. Set 목록은 `configs/*.json` 글로빙으로 복원한다(`model/DashProject.cpp:1088-1210`).

```
[프로젝트 열기] configs/*.json 전량 스캔
   │   파일명 접두사 → 모듈 · 접두사 뒤 전체 → Set 이름 (하이픈 접미사 포함)
   ▼
[variant 판정] detectGeometryVariant (:621) 3단 폴백
   │   1. JSON "variant" 키 (Set 생성 시 createModuleJsonFile 이 써 둔 값)
   │   2. 최상위 "Morphing" 객체 존재 여부 / DV-Geometry 의 source 접두사
   │   3. Set 이름 접미사 ("-CAD" 이면 CAD, 아니면 Morphing)
   ▼
[모델 인스턴스] variant 별로 다른 C++ 클래스를 new
```

`detectBuilderVariant`(`:658`) · `detectRunnerVariant`(`:673`) · `detectLauncherVariant`(`:690`) 는 1·3단만 쓴다 — JSON 내용으로 구별 불가라고 주석에 명시(`:656-657`). AnalysisLauncher 는 여기서 **variant 3종**(`Init`·`Resample`·`Direct`)을 갖는다.

---

## 2. 모듈별 상세

### 2.1 Geometry — Morphing

`configs/GeometryParameter_{Set}.json` · `.vtp` · `{part}.dat`(복사본)

| 키 | 라이터 · 시점 | 리더 · 시점 | 판정 |
|---|---|---|---|
| `variant` (`"Morphing"` 고정) | PM `:374` DV 저장 · `DashProject:604` Set 생성 | `DashProject:629` 열기 | 왕복 |
| `Morphing.handles_vtp` (경로 아닌 파일명) | PM `:367` | PM `:432` 진입 · `DashMorphingDoeExecutor:295` DOE | 왕복 |
| `Morphing.radius` (RBF 커널 반경) | PM `:369` · **위젯 `:654` 스핀박스 편집 즉시** | `DashGeometryParameter:157` · `MorphingDoeExecutor:299` · `Opt:1379` · `MR:2164` | 왕복 (라이터 2벌) |
| `Morphing.straight_sided` | PM `:372` | `MorphingDoeExecutor:830` — DOE 실행 시만 | 왕복 |
| `Morphing.constraints[]` `{name, node_ids[]}` | **없음** | PM `:451` 진입 | **고아** (MOR-D10) |
| `DV-Geometry.{paramN}` (순번 키) | PM `:105-165` DV 저장 · `DashDesignVariableModel:432-465` | 아래 8곳 | 왕복 |

| `DV-Geometry` 하위 키 | 값 | 리더 |
|---|---|---|
| `boolean` | 항상 `true` (체크된 행만 기록) | `DashGeometryParameter:171` 체크 복원 · `DesignVariableModel:320` · `MorphingDoeExecutor:526` |
| `source` | `"Morphing\|{dat}\|{컴포넌트}"` 파이프 3분할 | `DashProject:640` variant 판정 · `AL:1313` · `Opt:1291/1315` · `MR:854/1522` · `DoeConfigManager:242` (`split("\|")[1]` 이 실행 폴더 이름이 된다) |
| `type` | `"continuous"` 고정 | `DesignVariableModel:325` |
| `meta.min` · `meta.max` | DV 범위 | `DesignVariableModel:332-333` · `DashDataProcessor:2931` |
| `meta.default` | 항상 `0.0` 리터럴 | 0곳 — **일방** |
| `meta["design value"]` | 항상 `0.0` 리터럴 | `MorphingDoeExecutor:632` 가 읽지만 같은 실행이 `:286` 에서 `0.0` 으로 덮은 뒤라 도달 불가 — **실질 일방** |
| `meta["handle id"]`·`["group id"]`·`["bound index"]` | 핸들 좌표 | `MorphingDoeExecutor:269-279` handlesArray 구성 |

**VTP 페이로드** — `vtkXMLPolyDataWriter` 로 쓰는 point data 11종(`controller/DashHandleTypes.h:8-20`): `LocalNormal`·`HandleNormal`·`SelectionScalars`·`GroupIds`·`PlaneIds`·`ActiveStatus`·`LowerRange`·`UpperRange`·`Bounds`·`LocalToGlobal`·`HandleType` + field data `AllFixedVolumeIds`(PM `:313-319`). **핸들 이름은 어디에도 없다** — 트리 아이템 텍스트와 세션 한정 `QMap` 에만 존재(MOR-D5).

**`.dat` 복사본** — PM `:75-76` 이 활성 컨텍스트의 `.dat` 을 `configs/` 로 `remove` 후 `copy`. DV 저장의 부수효과이고 별도 기록은 남지 않는다.

**저장 시점** — 전부 [Set Design Variable] 1회(`view/DashGeometryParameterWidget.cpp:939` → `:1187`). 예외가 radius 로, 스핀박스를 고칠 때마다 파일을 통째로 재작성한다(`:643-661`).

### 2.2 Geometry — CAD

`configs/GeometryParameter_{Set}-CAD.json` · `{part}.prt`(복사본)

| 키 | 라이터 · 시점 | 리더 · 시점 | 판정 |
|---|---|---|---|
| `variant` | `CADPM:48` DV 저장 | `DashProject:629` | 왕복 |
| `Independent Parameter` — 6배열 병렬 (`Name`·`Part`·`Type`·`Value`·`Lower`·`Upper`) | `CAD:247` `toSettingsJsonObject` → `CADPM:50` | `CAD:298` `applyNxCadParameterJson` 진입 | 왕복 |
| `Dependent Parameter` — 4배열 병렬 (`Name`·`Part`·`Type`·`Value`) | `CAD:283` | `CAD:342` | 왕복 |
| `DV-Geometry.{name}` (`source` = `"CAD\|{part}"`) | `CADPM:14` `buildDvGeometryJson` | `CAD:417` 체크 복원 · `DesignVariableModel:314` · 하위 모듈 | 왕복 |

Morphing 과 다른 세 가지.

- **키가 파라미터 이름 자체**다 — `dvGeometryObj[row.name]`(`CADPM:39`). 이름이 곧 조인 키라 rename 이 곧 파괴다.
- **6개 병렬 배열**은 인덱스로만 정렬이 유지되고, 길이 불일치를 막는 것은 로더의 `qMin(…)`(`CAD:306`) 뿐이다.
- **`DashGeometryParameterCAD::saveSettings()`(`:117-120`) 는 `qDebug` 한 줄이 전부다** — 실제 쓰기는 전부 위젯 → PM 경로다.

**체크 상태 복원 순서 문제** — `loadFromJson`(`:407-430`)이 `boolean` 으로 `param.isChecked` 를 세우는데, 직후 캐시 재적용이 전 행을 덮는 경로가 남아 있다(CAD-D4). **`.prt` 복사본**(`view/DashGeometryParameterCADWidget.cpp:622-637`)은 `configs/` 에 놓일 뿐, **어느 Set 이 어느 prt 를 쓰는지 기록하는 키가 없다.**

### 2.3 Condition

`configs/ConditionParameter_{Set}.json`

| 키 | 라이터 · 시점 | 리더 · 시점 | 판정 |
|---|---|---|---|
| `DV-Condition.{dvKey}` (`boolean`·`source`·`type`·`meta.default/min/max`) | `CondPM:117` `saveDvCondition` ← 위젯 `:502` 체크 sync · `DesignVariableModel:432-465` | `Condition:448` 진입 · `DesignVariableModel:314` · `AL:1257` · `MorphingDoeExecutor:449/526` | 왕복 |
| `…{uuid, entry_ptr, param}` | `CondPM:84-86` | `Condition:466-479` 4세대 폴백 바인딩 | 왕복 |
| `…meta.case[]` (discrete·categorical 만) | `CondPM:109` | `DesignVariableModel:339/345` | 왕복 |

**`variant` 키가 없다** — Condition 은 variant 를 갖지 않는 유일한 DV 모듈이다.

**4세대 식별자 폴백** — 로더(`Condition:435-447` 주석)가 gen1(이름) → gen2(uuid) → gen3(+entry_ptr) → gen4(+param) 를 모두 받고 라이터는 항상 gen4 를 쓴다. 읽는 쪽이 네 벌의 스키마를 아는, **마이그레이션이 명시적으로 설계된 코드베이스 유일 자리**다.

**Value 인라인 편집의 저장 자리가 없다** — 델리게이트가 부르는 `commitEntryValue`(`Condition:339-379`)는 표가 아니라 **해석 모델 컨텍스트를 먼저 고치고**(`ctx->editFeConditionEntry`, `:362`) 정규화된 값을 되읽어 표에 반영한다. 즉 정의 편집이 아니라 입력파일 편집인데, config 에 그 값을 담는 키가 없어 모듈을 떠나면 사라진다(CON-D5).

**주석에만 있는 섹션** — `"FE Condition"` 문자열은 레포 전체에서 **주석 2줄뿐**이다(`CondPM:121` "다른 섹션 보존" · `CondPM.h:57`). 쓰는 코드도 읽는 코드도 없다.

### 2.4 Analysis Launcher

`configs/AnalysisLauncher_{Set}.json` · 산출 `{Root}/AnalysisLauncher_{Set}/{analysisType}/runs{K}/` · `doe_table_{base}.csv`

| 키 | 라이터 · 시점 | 리더 · 시점 | 판정 |
|---|---|---|---|
| `variant` | `DashProject:604` Set 생성 1회 | `DashProject:696` 열기 | 왕복 |
| `DOE configuration.Selected Design Variables` | `AL:799` · `DoeConfigManager:115` — **[Run] 시** | `DoeConfigManager:80` 진입 · `DashJobRunner:2227` | 왕복 |
| `DOE configuration.Auto-configuration` · `Manual-configuration` | 동상 | `DoeConfigManager:~85` | 왕복 |
| `input_files[]` `{name, target_component, path}` | `DoeConfigManager:150` ← `ReferenceFileWidget:1132` 표 변경 시 | `ReferenceFileWidget:1044` 진입 · `JobRunner:1235`(ODB) `:1380`(wbpj) `:1488`(타깃 파트) | 왕복 |
| `DOE Table.headers`·`samples`(`{key, values, slice, active, status…}`)·`input`·`output`·`rawSamples`·`source`·`min`·`max`·`mean`·`std` | `DoeConfigManager:389-402` `saveResultsAsDvTable` — 샘플링 성공 직후 **전량 재작성** | `DoeConfigManager:494/503/599` · `AL:977/1047/1397/1510` · `JobRunner:834/1218` · `DataProcessor:2780` | 왕복 |
| `DOE Table.samples[].status` · `status_{type}` | `DoeConfigManager:544` · `AL:994` — **전이 1회마다** | `DoeCasesWidget:247` 재기동 복원 · `DataProcessor:3016` 후처리 게이팅 · `JobRunner:824` | 왕복 (라이터 2벌) |
| `DOE Analysis.method.{boxplot\|scatter2d\|scatter3d\|pearson\|parallel}` | `DoeConfigManager:463` · `AL:1205` — 플롯 설정 변경 시 | **0곳** | **일방** |

**`DOE Analysis` 가 일방인 근거** — 플롯을 그리는 `DashPlotSpecBuilder::build`(`model/analyzer/DashPlotSpecBuilder.cpp:6`)는 config 경로를 받지만 **존재 여부만 확인하고 내용을 파싱하지 않는다**(`:15-23`). 실제 설정은 인자로 받은 메모리 `settings` 에서 온다(`:42-43`). 파일에 쌓이는 축·색·스타일은 다음 세션에서 아무도 보지 않는다(ANA-D9).

**전량 재작성 비용** — `setSampleStatus`(`DoeConfigManager:528-556`)는 전이 1건마다 전문을 파싱하고 samples 를 순회해 한 항목을 고친 뒤 전문을 다시 직렬화한다. 전이가 케이스 수 N 에 비례하므로 총 I/O 가 **N 의 제곱**이다.

**상태 키의 충돌 가능성** — `status` 는 `analysisType` 이 비면 평문 키, 아니면 `status_{type}` 이 된다(`:540`). Direct Launcher 는 빈 `analysisType` 으로 방출하므로(`JobRunner:1960`) 항상 평문 키를 쓴다. direct 키는 입력 파일 basename(`:1951`·`:1977`)이고 DOE 케이스 입력은 `runs{K}` 이름이라, **DOE 가 만든 케이스를 Direct 로 재실행하면 키가 정확히 일치한다.**

**케이스 단위로 남지 않는 것 둘** — 라이터 전수(`:389-402`·`:544`)에 **실패 사유 키가 없다.** 그리고 스테이지 전이(입력 생성 → 솔버 실행)는 `setStageState` 로 관리되지만 파일에는 **케이스당 문자열 하나**로 평탄화돼, "입력은 됐는데 해석에서 죽었다" 를 파일만으로 구별할 수 없다.

### 2.5 Data Preprocessor

`configs/DataPreprocessor_{Set}.json` · 산출 `{Root}/DataPreprocessor_{Set}/*.xml`

| 키 | 라이터 · 시점 | 리더 · 시점 | 판정 |
|---|---|---|---|
| `Dataset.Selected DV-Table` · `Selected Analysis File` | `DataProcessor:2670-2671` — 해석 파일 선택 시 | **0곳** | **일방** (PRE-D7) |
| `DOE Table.samples` · `headers` | `:2714-2715` — 데이터셋 스캔 직후 | `:1515-1516` · `:3117-3118` (동형 블록 `:3524`·`:3854`·`:4136`) | 왕복 |
| `DOE Table.output.{analysisType}` | `:2718` | `:1519` · `:3121` — 결과 처리 착수 시 | 왕복 |
| `Output Response[]` `{component, loadStep, name}` | `DataProcessorPM:127` — 표 확정 시 | **0곳** | **일방** |
| `Data Analysis.method.*` | `:2630` | **0곳** | **일방** |

**`DOE Table` 사본은 스냅샷이 아니라 결과 파일 인덱스다.** 새로 생기는 정보는 디스크 스캔으로 찾은 `output[analysisType]` 하나뿐이고, `samples`·`headers` 는 AnalysisLauncher 원본의 무변환 복사로 그 인덱스를 얹을 **조인 키** 역할이다. AL config 가 없으면 `{key: runDir, values: []}` 가짜 샘플을 합성해서까지 채운다(`:626-637`). 이 사본은 실제로 읽힌다 — `processResults`(`:1500-1531`)와 Modal KPI(`:3106-3128`)가 1순위로 읽고 없을 때만 `m_dataset` 스캔으로 합성한다(`:1533`·`:3130`). 다만 무변환 복사라 원본의 `status_*` 가 딸려오고, **그 사본을 읽는 코드는 0곳**이다 (정본은 언제나 AL 쪽).

**Output Response 가 일방인 의미** — 사용자가 정의한 응답 표가 파일에 남지만 재진입 시 복원되지 않는다. `Selected DV-Table`·`Selected Analysis File` 과 합치면 **이 모듈은 자기가 무엇을 대상으로 무엇을 뽑았는지를 전부 쓰기만 한다.**

### 2.6 Model Builder — Sim

`configs/ModelBuilder_{Set}.json` · 산출 `.dproj/ModelBuilder_{Set}/`(`model_info.json`·`*.pt`·`rendered_results/*.vtu`)

| 키 | 라이터 · 시점 | 리더 · 시점 | 판정 |
|---|---|---|---|
| `variant` | `MB:477` 학습 착수 · `DashProject:604` Set 생성 | `DashProject:664` | 왕복 |
| `Data Label.Dataset` (XML 절대경로 문자열) | `MB:859` — Data Label 확정 시 (경로를 프로젝트 루트로 교정) | `MB:773` 진입 | 왕복 |
| `Data Label.Input.{label}.reduction` | `helper:33` | `MB:784` | 왕복 |
| `Data Label.Output.{label}.reduction` | `helper:44` | `MB:793` | 왕복 |
| `Data Label.Output.{label}.transformation` | `helper:45` | **실사용 로더가 버린다** — `MB:793` 은 `{"", reduction}` 2필드만 만들고, 3필드로 읽는 `helper:95` 는 호출부 0곳 | **실질 일방** (BLD-D8) |
| `Configuration.{model}.<하이퍼파라미터>` | `MB:456-465` 학습 착수 | `MB:800` → `m_loadedModelConfig` → 위젯 표 복원 | 왕복 |
| `Configuration.{model}.status` | GUI `MB:468`(빈값) `:645`(`"In Progress"`) `:1448`(`"Failed"`) + **외부 도구가 `"Done"`** | `MB:1364`·`:1384` **1초 폴링** · `MB:2023` | 왕복 (라이터가 프로세스 밖에 1곳) |
| `Configuration.{model}.error` | `MB:471` 초기화만 | 표시 경로 | 왕복 |

**dead code 2건** — `ModelBuilderConfigHelper::parseDataLabelSection`(`:51`) · `parseConfigurationSection`(`:105`) 는 레포 전체에서 호출부 0곳이다. 실사용 로더는 `DashModelBuilder::loadDataLabelConfig`(`:747`)이고, 두 구현이 다른 것이 위 `transformation` 결손의 원인이다(BLD-U3 · BLD-D8 이 같은 뿌리).

**`Done` 보존 규칙** — 재학습 시 기존 `Configuration` 중 `status == "Done"` 인 항목만 살아남고 나머지는 새 옵션으로 교체된다(`MB:442-450`). **정의(하이퍼파라미터)의 수명이 상태 값에 종속된다.**

**`model_info.json`** — GUI 가 XML 에서 뽑은 `parameter`·`selected_response` 를 쓰고(`MB:545/550`), 외부 도구가 `errors` 를 채운다(`MB:1072` 가 읽는다). NaN·Infinity 를 담을 수 있어 읽기 전 정규식으로 `null` 치환한다(`MB:1044-1046`) — 표준 JSON 이 아니라는 증거다.

### 2.7 Model Builder — MCU

`configs/ModelBuilder_{Set}-MCU.json` · 산출 `{Root}/ModelBuilder_{Set}/`(사용자 루트 우회) + 인코딩된 C 헤더

Sim 과 같은 스키마를 쓰되 세 자리가 갈린다.

| 키 | Sim | MCU |
|---|---|---|
| `Data Label.Dataset` | 문자열 1개 | **배열** `[{path, mode}]` (`MBPM:315`) |
| `Configuration.{model}.status` 착수값 | `"In Progress"` (`MB:645`) | `"Running"` (`MCU:699`) — 같은 패밀리에서 어휘 불일치 |
| 산출 루트 | `.dproj/` | 사용자 루트 (`MCU:554-562` 우회) |

**MCU 의 데이터셋 표는 저장되지만 복원되지 않는다.** MCU 는 로더를 상속하는데(`MCU:733` 주석) 그 로더가 `m_datasetPath = dataLabelObj["Dataset"].toString()`(`MB:773`) 이라 배열에 대해 빈 문자열을 낸다. 그래서 `DashModelBuilderMCUWidget::onConfigLoaded`(`:419-434`)가 `isEmpty()` 분기로 떨어져 **고정 헤더 테이블을 새로 만든다.** 배열을 읽을 줄 아는 `helper:65-78` 은 호출되지 않는다.

**상태 소스가 3벌이다** — config 의 `Configuration.{model}.status`(`:699`) · `model_info.json` 의 `models[].status`(`:227-231`) · 프로세스 종료 시 세우는 메모리 전용 `"Interrupted"`(`:413`, 어느 파일에도 안 남는다). `model_info.json` 에는 `model_sizes`(생성된 C 헤더 경로, `:243-249`)도 붙는다.

### 2.8 Model Runner

`configs/ModelRunner_{Set}.json` · 산출 `{Root}/ModelRunner_{Set}/`

| 키 | 라이터 · 시점 | 리더 · 시점 | 판정 |
|---|---|---|---|
| `variant` | `MR:560` | `DashProject:679` | 왕복 |
| `Model upload.Output Response[]` `{set(절대경로), response, model}` | `MR:1054`(단일) · `:1148`(복수) — 모델 선택 변경 시 | `MR:2445`·`:2469` 갱신 경로 · **외부 도구** | 왕복 |
| `Model upload.Input Design Variables` `{label[], value[], min[], max[]}` | `MR:1083`·`:1162`·`:1239` | `MR:1213-1214` 자기 갱신 · **외부 도구** | 왕복 |
| `Analysis Input Files` | — | — | 저장 시 **제거**되는 레거시 (`MR:1034-1035`) |

**정의 파일이 곧 CLI 인자다** — `test-model-1d {configPath}`(`MR:890`) · `test-model-nd {configPath} {outputDir}`(`:1703`) · `test-model-1d {configPath} {outputDir}`(`:1779`). ModelBuilder 와 같은 구조이되 도구가 이 파일을 **되쓴다는 증거는 없다** (GUI 가 쓰지 않는데 바뀌는 키도, 그것을 전제한 폴링·방어 코드도 없다).

**산출물 포인터가 없다** — 예측 산출물 경로를 적는 키가 없다. 출력은 `--output-dir` 로 넘긴 디렉토리에 도구가 쓰고 GUI 는 경로 규약으로 다시 조립해 찾는다. 몇 번째 예측인지 적는 키도 없어 — **파일에 셀 수 있는 자리가 없으므로** — 회차 상태는 세션과 함께 사라진다(RUN-D34).

> 선행 측정(2026-08-18 · `refactor/async-execution` @ `fc167bd`)이 기록한 역기입 키 `{morris\|sobol\|shap}_datapath` · `reliability_datapath` · `convergence_history_datapath` 는 **`dev` @ `4c7608e` 레포 전체에서 0건**이다. 남은 `datapath` 는 ResultsAnalyzer 가 플롯 스펙에 넣는 `xml_datapath`(`view/DashResultsAnalyzerWidget.cpp:2085` → `DashPlotSpecBuilder.cpp:135`) 하나이고 메모리 전달이라 파일에 남지 않는다. 브랜치 차이인지 이후 삭제인지는 확인하지 않았다.

### 2.9 Optimizer

`configs/Optimizer_{Set}.json` · 산출 `{Root}/Optimizer_{Set}/optimum.json` · `optimization_log/convergence_history.png`

| 키 | 라이터 · 시점 | 리더 · 시점 | 판정 |
|---|---|---|---|
| `Optimization.trained_surrogate_model[]` `{model, response, symbol}` | `Opt:365` — **[Run] 시** (`:199`) | `Opt:829` `loadSurrogateModels` 진입 | 왕복 |
| `Optimization.design_variables[]` `{symbol, parameter, value, min, max, mean, std, optimize}` | `Opt:366` | 진입 시 로더 | 왕복 |
| `Optimization.sampling_mode` | `Opt:370` — SORA 일 때만, 아니면 `remove` | 외부 도구 | 왕복 |
| `optimization_settings.methods` · `configs`(`max_budget`·`max_cycles`·`design_tolerance`·`shift_tolerance`·`inverse_form_solver`·`statistics_sample`) · `objective_function` · `use_constrained_function` · `constrained_functions[]` | `Opt:473-499` | `Opt:770-825` `loadOptimizationSettings` — 레거시 배열 형태까지 받는다 | 왕복 |
| `Results Analysis` | — | — | 저장 시 **제거**되는 레거시 (`Opt:358`) |

**config 키가 전부 왕복하는 유일한 모듈이다** — 일방 키가 0개다. 대신 **저장 시점이 [Run] 하나**여서(`runOptimization:199` 이 `saveSettings()` 를 부르는 유일 경로) 목적함수·구속식을 입력하고 실행하지 않은 채 떠나면 전부 사라진다(OPT-D12·OPT-D6). AnalysisLauncher 도 같다(`AL:233`).

**`optimum.json` 은 역방향 파일이다** — 외부 도구만 쓰고 GUI 는 읽기만 한다. 구조는 `{ meta: { item: [헤더…] }, data: [ { name: "Optimum"\|"Neighbor", value: […] } ] }`(`Opt:1071-1099`). 리더 4곳: `Opt:1053` · `DashResultsAnalyzerWidget:432`·`:952`·`:2635`.

### 2.10 Results Analyzer

**config 파일이 없다.** 축·색·스타일·표시 옵션은 `methodObj` 로 조립돼 **호스트 모듈의 config** 에 얹힌다 — DOE 계열은 `AnalysisLauncher_{Set}.json` 의 `DOE Analysis`, 데이터 계열은 `DataPreprocessor_{Set}.json` 의 `Data Analysis`. 그 두 블록이 2.4·2.5 의 **일방** 키다.

쓰는 항목(`view/DashResultsAnalyzerWidget.cpp`): `variables`·`display_options`·`regression_line`·`group_settings`(`:1942-1945`) · `box_colors`·`scatter_colors`·`line_colors`(`:2250-2252`) · `input_variables`·`output_variables`(`:2127-2128`) · `save_json_path`(`:2187`) · `model_path`(`:2989`) · `xml_datapath`(`:2085`). 읽는 쪽은 없고 플롯 데이터 자체도 파일 표현이 없어, **이 모듈은 상태를 어디에도 남기지 않는다.**

### 2.11 프로젝트 레벨 · 프로젝트 밖

| 대상 | 저장 자리 | 내용 | 판정 |
|---|---|---|---|
| 프로젝트 정체성 | **없음** | 폴더명 + `configs/` 파일명 집합이 대신한다 (1.3) | — |
| Set 목록 | **없음** | `configs/*.json` 글로빙 (`DashProject:1088`) | — |
| 기준 해석 파일 등록 | **없음** | `[Add File]` 은 루트로 복사만 한다(`DashMainWindow:2179`). 어느 모듈이 어느 파일 기준인지 적는 자리가 없다 | — |
| 활성 해석 모델 | **메모리 전용** | `DashAnalysisModelContextRegistry`(107줄)에 파일 쓰기가 0줄. active 는 `m_activeFilePath` 1개이고 직렬화되지 않는다 | — |
| `AIGeometryGeneration_{Set}.json` | configs (경로 하드코딩 `DashAIGeometryGeneration.cpp:41`) | 생성만 되고(`DashProject.cpp:86`) 읽는 코드 없음 | 일방 |
| 솔버 실행 경로 | `QSettings("YourCompany","DashApp")` → `Solvers/{name}` | 머신 전역 — 프로젝트를 옮기면 따라가지 않는다 | 왕복 (프로젝트 밖) |
| UI 배율 · 마지막 프로젝트 경로 | `QSettings("NohLab","DashOptiAnalyzer")` → `UI/scaleFactor`·`Paths/lastProjectDir` | 조직명이 솔버 경로와 다르다 | 왕복 (프로젝트 밖) |
| FE-safe 재료 설정 | **원본 파일 직접 수정** | `.stlx`·`.dbase` 를 제자리에서 고치고 `.bak_{yyyyMMdd_HHmmss}` 백업 (`MaterialSetupDialog:196`·`:577`) | 프로젝트에 기록 없음 |

**`SaveProject()` 는 `return true` 한 줄이다**(`controller/DashProjectManager.cpp:164-167`). 모든 쓰기가 이미 즉시 반영이라 무해하지만 "저장했다" 는 기대와 어긋난다. **`SaveProjectAs()`(`:169-210`) 는 숨김 `.dproj` 만 재귀 복사한다** — 사용자 루트의 산출 디렉토리와 [Add File] 원본이 전부 빠지고, config 안의 절대경로는 옛 경로를 가리킨 채 복사된다.

---

## 3. 왕복 대장

### 3.1 쓰기만 하고 읽는 코드가 0곳인 키 — 13개

| # | 파일 | 키 | 무엇을 잃는가 | 결함 ID |
|---|---|---|---|---|
| 1 | AnalysisLauncher | `DOE Analysis.method.*` | DOE 플롯의 축·색·스타일 | ANA-D9 |
| 2 | DataPreprocessor | `Data Analysis.method.*` | 데이터 플롯의 축·색·스타일 | ANA-D9 |
| 3 | DataPreprocessor | `Dataset.Selected DV-Table` | 이 전처리가 어느 DOE 기준인가 | PRE-D7 |
| 4 | DataPreprocessor | `Dataset.Selected Analysis File` | 어느 해석 타입을 골랐는가 | PRE-D7 |
| 5 | DataPreprocessor | `Output Response[]` | 사용자가 정의한 응답 표 전체 | — |
| 6 | DataPreprocessor | `DOE Table.samples[].status_*` (사본) | (원래 쓸모가 없다 — 무변환 복사의 부작용) | — |
| 7 | ModelBuilder | `Data Label.Output.*.transformation` | 출력 변환 선택 | BLD-D8 |
| 8 | ModelBuilder MCU | `Data Label.Dataset[]` | 데이터셋 파일 표 (배열/문자열 스키마 분기) | 신규 |
| 9 | Geometry Morphing | `DV-Geometry.*.meta.default` | (항상 `0.0` 리터럴) | — |
| 10 | Geometry Morphing | `DV-Geometry.*.meta["design value"]` | (실행 시 `0.0` 으로 덮여 도달 불가) | — |
| 11 | Geometry CAD | `.prt` 복사본의 소속 | 어느 Set 이 어느 파트를 쓰는가 | — |
| 12 | 프로젝트 | `AIGeometryGeneration_{Set}.json` 전체 | 생성만 되고 아무도 안 읽는다 | — |
| 13 | ResultsAnalyzer | (자기 config 없음 — 1·2 로 흡수) | 패널 상태 전부 | ANA-D9 |

### 3.2 리더만 있고 라이터가 없는 키 — 1개

`GeometryParameter_{Set}.json` 의 `Morphing.constraints[]` `{name, node_ids[]}` — 파서(`GeometryParameterPM:451-471`)가 완비돼 있고 쓰는 코드만 레포에 없다. 손으로 넣으면 동작한다 (MOR-D10).

### 3.3 프로세스 경계를 넘는 것

| 파일 | 키 | 생산자 | GUI 리더 |
|---|---|---|---|
| `ModelBuilder_{Set}.json` | `Configuration.{model}.status = "Done"` | DeepOpt · MCU | 1초 폴링 (`MB:1364`) |
| `model_info.json` | `errors` | DeepOpt | `MB:1072` · `MR:734` |
| `model_info.json` | `models[].status` · `model_sizes` | MCU | `MCU:227` |
| `optimum.json` | `meta.item` · `data[]` | DeepOpt | 4곳 |

반대 방향(**GUI 가 쓴 값을 외부 도구가 읽는다**)은 `ModelBuilder_{Set}.json`·`ModelRunner_{Set}.json`·`Optimizer_{Set}.json` 3종이며 셋 다 **config 경로 자체가 CLI 인자**다. 즉 정의 파일이 프로세스 경계를 넘는 것이 3모듈 공통이고, 그중 되쓰기까지 하는 것은 ModelBuilder 계열뿐이다.

---

## 4. 라이터가 여럿인 파일

| 파일 | 라이터 | 성격 |
|---|---|---|
| `AnalysisLauncher_{Set}.json` | ① `AL:780` ② `DoeConfigManager:95` ③ `:140` ④ `:180` ⑤ `:528`+`AL:994` ⑥ `:418`+`AL:1174` | ①②는 같은 내용을 쓰는 **복제 구현**(`oldStatus` 반환 유무만 다르다), ⑤⑥은 각각 상태·플롯 설정의 **이중 경로** |
| `GeometryParameter_{Set}.json` | ① PM `:325` ② 위젯 `:654`(radius) ③ `DesignVariableModel:375` | ③은 **다른 모듈**(AnalysisLauncher)의 표에서 상위 모듈 파일에 쓴다 |
| `ConditionParameter_{Set}.json` | ① CondPM `:117` ② `DesignVariableModel:375` | 동상 |
| `ModelBuilder_{Set}.json` | ① `MB:480` ② `:656`(상태) ③ `:1456`(마감) ④ **외부 도구** | ④가 프로세스 밖이라 라이터를 GUI 한 곳으로 줄일 수 없다 |

**모듈 경계를 넘는 쓰기가 실재한다.** `DashDesignVariableModel::saveToJsonFiles`(`model/DashDesignVariableModel.cpp:375-485`)는 DV 표에서 편집한 `type`·`meta.min/max/mean/std/case` 를 **원 소유 모듈의 config 에 되쓴다.** 호출부는 셋 — AnalysisLauncher 위젯 `:746` · Condition 위젯 `:649` · CAD 위젯 `:766` — 이고, 대상 섹션은 **파일명 문자열 매칭**으로 고른다(`:411-417` — "Geometry" 면 `DV-Geometry`, "Condition" 이면 `DV-Condition`).

즉 **AnalysisLauncher 화면에서 DV 범위를 고치면 Geometry·Condition 정의 파일이 바뀐다.** 파일 소유 관점에서는 경계 침범이지만 사용자 동선으로는 자연스럽다 — "파일마다 라이터 하나" 를 규약으로 세우려면 이 경로를 금지할지 명시적 경로로 승격할지를 먼저 정해야 한다. `mean`·`std` 는 이 경로에서만 생겨난다(`:446-449`, `"None"` 문자열 또는 숫자).

---

## 5. 시점

### 5.1 쓰기 트리거

| 트리거 | 대상 | 모듈 |
|---|---|---|
| **[Set Design Variable]** | 정의 전량 + VTP + `.dat`·`.prt` 복사 | Geometry Morphing · CAD |
| **체크박스 sync** | `DV-Condition` 전량 재작성 | Condition |
| **[Run]** | `DOE configuration` · `Optimization` 전량 | AnalysisLauncher · Optimizer |
| **샘플링 성공 직후** | `DOE Table` 전량 | AnalysisLauncher |
| **케이스 상태 전이 1회** | 파일 전문 재작성 | AnalysisLauncher |
| **스핀박스 편집 1회** | 파일 전문 재작성 | Geometry Morphing (radius) |
| **해석 파일 선택** | `Dataset` · `DOE Table` 스냅샷 | DataPreprocessor |
| **학습 착수** | `Configuration` + `status` + `model_info.json` | ModelBuilder |
| **모델 선택 변경** | `Model upload` | ModelRunner |
| **Set 생성** | `{"variant": …}` 한 줄짜리 빈 파일 | 전 모듈 (`DashProject:592`) |

**양극단이 공존한다** — 셀 편집 1회에 파일 전문을 쓰는 자리(상태 전이·radius)와 [Run] 을 눌러야만 저장되는 자리(AL·Optimizer)가 같은 코드베이스에 있다. 중간(dirty 신호 + 디바운스)은 없다.

### 5.2 읽기 트리거

| 트리거 | 대상 |
|---|---|
| 프로젝트 열기 | `configs/*.json` 글로빙 + 각 파일의 `variant` 키 (내용은 안 읽는다) |
| 모듈 진입 (`setSetName` → `loadFromJson`) | 해당 모듈 config 1회 |
| DOE 실행 착수 | 상위 Geometry·Condition config 를 **직접 파일로** (`MorphingDoeExecutor:255-311`, `AL:1257/1305`) |
| **1초 폴링** | `ModelBuilder_{Set}.json` 의 `Configuration.*.status` |
| 파일워처 | `AnalysisLauncher_{Set}.json` 1곳뿐(`DashDoeCasesWidget:102-105`) — 자기 쓰기가 자기 재구축을 유발 |
| 결과 처리 착수 | `DataPreprocessor_{Set}.json` 의 `DOE Table`, 없으면 디스크 스캔 |
| 플롯 렌더 | config 파일 **존재만** 확인, 내용은 메모리에서 (`DashPlotSpecBuilder:15-23`) |

**하류 모듈이 상류 config 를 파일 경로로 직접 연다.** 상위 선택을 기록하는 키가 없거나(ModelBuilder·Optimizer) 있어도 읽지 않으니(DataPreprocessor), 경로를 관례로 조립하거나 **목록의 첫 항목을 기본값으로 삼는** 구조가 나온다 — `folders.first()` 로 떨어지는 자리가 `view/DashModelRunnerWidget.cpp:744` 와 `view/DashOptimizerWidget.cpp:660-662` 둘이다. 사용자가 고른 것이 아니라 **정렬 순서가 고른 것**이 상위 바인딩이 된다.

---

## 6. 귀속과 성격으로 갈라 보면

**귀속**은 값이 무엇에 매달려 무엇과 함께 사라지는가(프로젝트·Set·실행 1회), **성격**은 구조화된 소량(메타)인가 불투명한 대용량(벌크)인가다.

| | **메타** — 구조화 · 가변 | **벌크** — 불투명 · 생성 후 불변 |
|---|---|---|
| **프로젝트 귀속** | **비어 있다** | `[Add File]` 원본 · `configs/` 의 `.dat`·`.prt` 복사본 (**어디에도 등록되지 않는다**) |
| **Set 귀속** | `{Module}_{Set}.json` 9종 전부 | `GeometryParameter_{Set}.vtp` |
| **실행 귀속** | **독립 파일이 없다** | 케이스 입력·결과 · `*.xml`·`*.pt`·`*.vtu`·`*.csv` · `optimum.json` · `.png` |

**프로젝트 메타가 없다.** 정체성은 폴더 이름과 `configs/` 파일명 집합이 대신한다(1.3). 그래서 프로젝트 귀속 벌크(복사된 입력파일)를 가리키는 자리도 함께 없다.

**실행 메타가 Set 메타 파일 안에 눌려 있다.** 케이스별 상태는 `AnalysisLauncher_{Set}.json` 의 `DOE Table.samples[].status*`, 학습 상태·오류는 `ModelBuilder_{Set}.json` 의 `Configuration.{model}.status`·`.error`, MCU 학습 상태는 `model_info.json` 의 `models[].status` — 전부 정의 파일 또는 산출 디렉토리 안이다. 케이스 실패 사유와 스테이지별 진행은 담는 키 자체가 없다(2.4). 여기서 셋이 따라 나온다.

1. **실행이 정의를 덮는다** — 같은 파일이니 상태 전이가 정의 파일 전문을 재작성한다(2.4·5.1).
2. **실행 이력이 남지 않는다** — 재실행이 이전 값을 덮고, "이 결과가 어느 실행에서 나왔는가" 를 적을 자리가 없다.
3. **정의의 수명이 상태에 종속된다** — ModelBuilder 는 재학습 시 `status == "Done"` 항목의 하이퍼파라미터만 살린다(2.6).

**실행 벌크를 가리키는 인덱스가 2곳뿐이다** — `AnalysisLauncher.DOE Table.input`/`output` 과 `DataPreprocessor.DOE Table.output`, 둘 다 DOE 케이스 목록이다. 나머지 산출물(학습 모델·예측 결과·최적화 로그·렌더 결과)은 **경로 규약으로 조립하거나 디스크를 스캔해서** 찾으므로, 스캔 필터와 생성 시 경로가 어긋나면 조용히 빈 결과가 된다.

**상위 선택(계보)은 별도 칸이 아니라 Set 메타 안의 몇 개 키이고, 대부분 읽히지 않는다.**

| 모듈 | 상위 선택을 적는 키 | 리더 |
|---|---|---|
| AnalysisLauncher | `DOE configuration.Selected Design Variables` | 있다 (`DoeConfigManager:80` · `JobRunner:2227`) |
| DataPreprocessor | `Dataset.Selected DV-Table` · `Selected Analysis File` | **0곳** |
| ModelRunner | `Model upload.Output Response[].set` (절대경로) | 자기 갱신 경로에서만 |
| ModelBuilder · Optimizer | **키 자체가 없다** | — |

"이 Set 은 무엇을 기준으로 만들어졌는가" 를 **적는 자리조차 없는 모듈이 둘, 적지만 안 읽는 모듈이 하나** — 없는 것이 자리인지 리더인지가 모듈마다 다르다는 점이 이 축의 실측 결론이다.
