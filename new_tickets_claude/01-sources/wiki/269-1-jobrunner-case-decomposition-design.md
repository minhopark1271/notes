# DashJobRunner 케이스별 분해 설계

> 관련 Issue: #269
> 기반 문서: [205-2-w6-w10-change-log-and-remaining-design](205-2-w6-w10-change-log-and-remaining-design.md) (#269 절의 방향 2안)

## 개요

`model/DashJobRunner.cpp` 의 `generateInputCases` 와 `runDirectJobs` 를 확장자 5종(.stli / .wbpj / .dfsxml / .inp / .dat)별 함수로 분해하고, 한 클래스를 케이스별 translation unit 6개로 나누는 설계다. #269 의 방향 2안(함수 분해)을 택했다.

**기계적 분해가 기본이다.** Extract Method 와 파일 이동뿐이고 배선(분기 순서 · 상태 보고 · 런처 초기화 · 로그) 은 원문 그대로다. 예외는 하나 — 폴백 분기가 엉뚱한 케이스로 지정돼 명백히 동작하지 않는 경로 2곳은 ERROR 로그 + return 으로 바꾼다. 공용부 추출(run dir 경로 · 상태 보고 · 결과 파일 탐색 등)은 이번에 하지 않고 후속에서 일괄 정리한다.

측정 기준: `dev` @ `ca68a57` (2026-09-28). 줄 번호는 서식 커밋(Phase 0) **이전**의 `model/DashJobRunner.cpp`.

## 배경

`generateInputCases` (1225-2023, 800줄) 는 이름과 달리 입력 생성과 솔버 제출을 함께 한다. 케이스 5종이 한 본문에 중첩돼 있고, 공통 전처리에 특정 케이스만 쓰는 계산이 섞여 있다. `runDirectJobs` (2025-2181) 도 같은 5종을 한 본문에서 분기한다. 호출자는 `model/DashAnalysisLauncher.cpp` 하나이고 테스트는 없다 (`tests/` 는 Qt Core 전용이라 이 클래스를 올릴 수 없다).

### 현재 구현 분석

```
[A] 공통 전처리 1227-1393
   │   프로젝트·IO 가드, DOE JSON 읽기(headers/samples), userPath/moduleDir
   │   odbSourceAnalysisTypes (stli 전용), columns → bareKeys, substitutionTokens (dat 치환 전용)
   │   전 active 샘플 Enqueued 시그널
   ▼
[B] .stli 1400-1473   ODB 복사 → launchFeSafePost (샘플마다 생성+제출 교차)
[C] .wbpj 1476-1521   input_files 조회 → runWbpjDoeAsync
[D] 모핑 1526-1941    DashManager 있고 cachedSamples 비어있지 않을 때
   │   D0 1527-1614  ensureLauncherInitialized (inp 제외), referenceDatName, activeKeys, samplesForMorphing, targetPart 주입
   │   D1 1618-1783  .dfsxml+모핑: MorphFromDoeSamples(sourceDat) → VTU 대기 → motion-writer → motion-launcher 큐
   │   D2 1787-1798  그 외: MorphFromDoeSamples(template)
   │   D3 1801-1865  .inp: Abaqus 제출
   │   D4 1867-1936  .dat (모핑 없는 dfsxml 포함): MAPDL 제출
   ▼
[E] 치환 폴백 1943-2022   템플릿 ${token} 치환 → {key}.dat → MAPDL 제출
       cachedSamples 비거나 DashManager 없을 때. 확장자 무관하게 .dat 로 씀
```

관찰:

| 항목 | 사실 |
|---|---|
| 케이스 전용 계산의 위치 | `odbSourceAnalysisTypes` (1274-1298) 는 stli 만, `substitutionTokens` (1331-1379) 는 [E] 의 `writeCaseDat` (1996) 만 쓴다. `bareKeys` 는 토큰 계산과 wbpj (1518) 가 쓴다 |
| 상태 보고 | JSON 영속만: 모핑 dat/inp/dfsxml 실패 (1700/1716/1740/1750/1767, 1836/1845/1853, 1895/1908/1927/1931, 1987-2018). 영속 + 시그널: stli, inp 제출. 시그널이 빠진 실패는 `DashAnalysisLauncher::onCaseStatusUpdated` 의 완료 추적에 닿지 않는다 — **이번엔 그대로 둔다** (후속) |
| 오작동 경로 ① | `.inp`/`.dfsxml` 템플릿에 rawSamples 가 없으면 [E] 로 흘러 템플릿 본문을 토큰 치환해 `{key}.dat` (파일명 1981 고정) 로 쓰고 MAPDL 에 제출한다. Abaqus 덱 · Motion XML 을 MAPDL 이 읽는다 |
| 오작동 경로 ② | 모핑 없는 `.dfsxml` 은 D2 → D4 로 흘러 dfsxml 을 partConfig 로 모핑한 뒤 `{key}.dat` 를 찾는다. 모핑 실행기는 dfsxml suffix 에 `.dat` 를 쓰지 않으므로 (`controller/DashMorphingDoeExecutor.cpp:481-497`) D4 의 "Generated file missing" 으로 전 샘플 Failed 확정 |
| 도달 불가 | `referenceDatName != analysisType` WARN (1556-1559) — 둘 다 template basename. 그대로 둔다 |
| 죽은 코드 | `createRunsFolders` (502-531), anon `copyFilesToDirectory` (241-269), 지역 `rawSamples` (1300) — 컴파일러가 미호출을 보증하는 3건만 삭제 |
| 외부 사용 | `DashAnalysisLauncher.cpp` 143-151 (시그널), 186 (`applyLauncherCPUCoreCount`), 250-252 · 290-291 · 1268 (setter), 1269 (`generateInputCases`), 1479 (`runDirectJobs`), 1518 (`cancelAllRuns`) |

## 설계

### 핵심 아이디어

`generateInputCases` 의 원문 블록을 그대로 함수로 뽑고 (Extract Method), 디스패처 `runDoeJobs` 가 원본 분기 순서 그대로 부른다. 공통 전처리 결과는 `DoeRunContext` 스냅샷에, 모핑 준비 결과는 `MorphingPrep` 에 담아 넘긴다. 케이스 함수끼리 서로 부르지 않고 디스패처만 순서를 안다. 클래스 · 시그널 · 런처 상태 · task 맵은 그대로 두고, 정의만 케이스별 .cpp 로 나눈다.

### 대안 검토

| 방식 | 장점 | 단점 | 선택 |
|---|---|---|---|
| A. 단일 파일, 케이스별 섹션 재배치 | 파일 이동 없음, diff 최소 | 2800줄이 한 파일에 그대로. 케이스 파일 단위 재컴파일·리뷰 불가 | 기각 |
| B. 함수 분해 + 케이스별 TU (한 클래스, .cpp 6개) | 클래스 API·시그널·멤버 그대로. 선례 `model/DashDataProcessorKPI.cpp` (#435). CMake `GLOB_RECURSE` 라 등록 불필요 | 익명 네임스페이스 헬퍼가 파일 단위로 갈려 공용 3개는 내부 헤더 필요 | 채택 |
| C. 케이스별 전략 클래스 (#269 원안 ⑴) | 계약을 구조로 강제 | 런처 · task 맵 · 시그널 · 취소를 공유하는 설계가 추가로 필요. `DashBatchLedger` 선례가 dev 에 없어 전제가 사라짐 | 기각 — 후속 판단 |

B 를 고른 근거: 호출자가 하나이고 공개 표면이 5종뿐이라 클래스 경계를 바꿀 이유가 없다. C 가 필요해지면 B 의 케이스 함수가 그대로 전략 구현체의 본문이 된다.

### 디스패처

```cpp
void DashJobRunner::runDoeJobs(templateFilePaths, cachedSamples, targetPartName)   // 구 generateInputCases
{
    auto ctx = makeDoeRunContext(templateFilePaths);      // [A] 1227-1383 원문. 실패 시 nullopt
    if (!ctx) return;
    emitEnqueued(*ctx);                                   // 1385-1393
    if (ctx->isStli) { runStliDoe(*ctx); return; }        // [B]
    if (ctx->isWbpj) { runWbpjDoe(*ctx); return; }        // [C]
    const QJsonArray sourceArray = ctx->doeTableObj.value("source").toArray();   // 1523
    const bool hasMorphing = isDfsxmlWithMorphing(ctx->templatePath, sourceArray); // 1524
    if (!ctx->templatePath.isEmpty() && !cachedSamples.isEmpty()) {              // 1526
        if (auto mgr = DashManager::Mgr()) {                                     // 1527
            if (ctx->isDfsxml && !hasMorphing) { ERROR; return; }               // 신규 ②
            MorphingPrep prep = prepareMorphingBatch(*ctx, cachedSamples, targetPartName);   // D0
            if (ctx->isDfsxml) { runDfsxmlMorphingDoe(*ctx, prep, sourceArray); return; }    // D1
            morphFromTemplate(*ctx, prep);                                       // D2
            if (ctx->isInp) { submitMorphedInpJobs(*ctx); return; }              // D3
            if (!prep.ansysReady) { WARN 1868; return; }                         // 1867-1870
            submitMorphedDatJobs(*ctx); return;                                  // D4
        }
        DASH_LOG_INFO 1939;                                                      // 1938-1940
    }
    if (ctx->isInp || ctx->isDfsxml) { ERROR; return; }                          // 신규 ①
    runTemplateFallback(*ctx);                                                   // [E] — .dat 전용
}
```

신규 return 2곳은 기존 조기 return (1306-1308, 1402-1404, 1498-1505) 과 같은 형식 — `DASH_LOG_ERROR(Analysis)` 한 줄, 상태 갱신 없음 (샘플은 Enqueued 로 남는다. `.stli` 부재 시와 같은 현행 방식).

### 자료 구조

```cpp
// DashJobRunner.h — private 중첩. [A] 공통 전처리 결과. 원문 지역변수를 이름 그대로 옮긴다.
struct DoeRunContext {
    DashIOController* ioCtrl = nullptr;
    QString doeJsonPathSnapshot, setNameSnapshot, userPath, moduleDir;
    QString templatePath, analysisType, templateSuffix;
    bool isStli = false, isDfsxml = false, isWbpj = false, isInp = false;
    QJsonObject root, doeTableObj;
    QStringList headers;
    QJsonArray samples;
    QSet<QString> odbSourceAnalysisTypes;   // 1274-1298 (stli 만 씀 — 계산 위치 불변)
    QList<DashDvColumn> columns;
    QStringList bareKeys;                   // 1325-1329
    QStringList substitutionTokens;         // 1331-1379 (경고 3종 포함, 시점 불변)
};

// [D0] 결과. dat/inp/dfsxml 이 공유.
struct MorphingPrep {
    bool ansysReady = false;                // 1533-1547 (dfsxml 도 MAPDL 런처 초기화 — 원문 유지)
    QString morphingProjectPath;            // 1549
    QString referenceDatName;               // 1550-1559 (도달 불가 WARN 포함, 원문 유지)
    QSet<QString> activeKeys;               // 1563-1571
    QJsonArray samplesForMorphing;          // 1573-1611 (effectiveTargetPart 주입까지)
};
```

`DashDoeConfigManager configManager` (1302-1303) 는 각 케이스 함수가 원문처럼 지역으로 만든다 (상태 없는 객체). 헤더 추가: `<optional>`, `class DashIOController;`, `"model/DashDoeSelection.h"`. 구조체는 그것을 쓰는 멤버 선언보다 앞에 둔다.

### 파일 구성

| 파일 | 담당 | 옮겨갈 기존 정의 (줄) |
|---|---|---|
| `model/DashJobRunner.h` | 클래스 선언. private 절을 "공통 / Dat / Inp / Dfsxml / Wbpj / Stli" 로 재배치, `private slots:` 블록 2개 병합. 공개/비공개 변경 없음 | — |
| `model/DashJobRunnerCae.h` (신규) | cae-launcher 공용 inline 3개. `Q_OBJECT` 없음, .cpp 없음 | `toFsPath` 37, `caeErrorText` 57, `caeTerminalStatusText` 62 |
| `model/DashJobRunner.cpp` | ctor/dtor, setter, 취소, dispatcher, `makeDoeRunContext`, `emitEnqueued`, `prepareMorphingBatch`, `morphFromTemplate`, `runDirectJobs` 골격. 파일명 유지 — AUTOMOC 이 헤더와 basename 으로 짝지음 | 273-284, 415-462, 890-976, 1078-1085, 1227-1393, 1523-1614, 1787-1798, 1938-1940, 2025-2040 + 2178-2181 |
| `model/DashJobRunnerDat.cpp` | ANSYS MAPDL: `submitMorphedDatJobs` (D4), `runTemplateFallback` (E), `writeCaseDat`, 런처 3함수, `submitDirectDatJobs` | 43-55, 73-150, 464-500, 978-1026, 1087-1115, 1150-1166, 1867-1936, 1943-2022, 2042-2065 |
| `model/DashJobRunnerInp.cpp` | Abaqus: `submitMorphedInpJobs` (D3), 런처 3함수, `submitDirectInpJobs` | 153-183, 1028-1076, 1117-1148, 1168-1223, 1801-1865, 2068-2093 |
| `model/DashJobRunnerDfsxml.cpp` | ANSYS Motion: `runDfsxmlMorphingDoe` (D1), motion 6함수, `queueDirectDfsxmlJobs` | 533-888, 1618-1783, 2096-2119 |
| `model/DashJobRunnerWbpj.cpp` | `runWbpjDoe` (C), `runWbpjDoeAsync`, STP 슬롯 5개, `launchWbpjJournal`, `launchAnsysJournalDirect`, `startDirectWbpjJobs` | 1476-1521, 2122-2176, 2187-2801 |
| `model/DashJobRunnerStli.cpp` | fe-safe: `runStliDoe` (B), 런처 4함수 | 185-239, 286-413, 1400-1473 |

TU 분리 규칙:

- 새 .cpp 는 `"model/DashJobRunner.h"` 를 최상단에 두고 `Q_OBJECT` 를 담지 않는다. include 순서는 `docs/coding-convention.md` "헤더와 include".
- anonymous namespace 함수는 private 중첩 타입(`DoeRunContext`, `MorphingPrep`, `MotionLauncherTask`, `StpCase`)을 이름할 수 없으므로 원시 타입만 받는다. ctx 가 필요한 것은 private 멤버 함수.
- private slot 은 헤더 선언 그대로. `QMetaObject::invokeMethod(this, "startNextMotionLauncher", …)` (793, 842, 2117) 는 메타 오브젝트로 해석되므로 정의 파일과 무관.

### 함수 inventory

모두 원문 블록의 Extract Method 다. "원문" 열의 줄 범위가 그대로 본문이 된다.

| 함수 | 원문 | 비고 |
|---|---|---|
| `std::optional<DoeRunContext> makeDoeRunContext(templateFilePaths)` | 1227-1383 | 가드 return 은 nullopt. `m_feSafeTemplateProjectAbsPath.clear()` (1272) · `m_currentAnalysisType` (1318) · isStli 시 경로 설정 (1381-1383) 도 원문 위치 그대로 안에서 수행 |
| `void emitEnqueued(ctx)` | 1385-1393 | |
| `void runStliDoe(ctx)` | 1400-1472 | 샘플마다 ODB 복사 + `launchFeSafePost` 교차, 원문 그대로 |
| `void runWbpjDoe(ctx)` | 1476-1520 | `runWbpjDoeAsync(…, ctx.bareKeys, ctx.samples, ctx.doeTableObj, …)` |
| `MorphingPrep prepareMorphingBatch(ctx, cachedSamples, targetPartName)` | 1530-1614 | |
| `void runDfsxmlMorphingDoe(ctx, prep, sourceArray)` | 1618-1783 | `msleep`/`processEvents` 포함 원문. 스냅샷 3개 설정 (1772-1774) 포함 |
| `void morphFromTemplate(ctx, prep)` | 1787-1798 | |
| `void submitMorphedInpJobs(ctx)` | 1801-1864 | |
| `void submitMorphedDatJobs(ctx)` | 1872-1936 | |
| `void runTemplateFallback(ctx)` | 1943-2022 | 샘플마다 `writeCaseDat` + `submitAnsysTask` 교차, 원문 그대로 |
| `int submitDirectDatJobs(files)` · `int submitDirectInpJobs(files)` · `int queueDirectDfsxmlJobs(files)` · `int startDirectWbpjJobs(files, targetFiles)` | 2042-2065 · 2068-2093 · 2096-2119 · 2122-2176 | 각 버킷 블록. 반환값 = 그 블록의 taskCount 증분 |
| anon `loadInitialIndependentParameter(doeJsonPath)` · anon `stpCaseConfig(headersJson, initIndParam, sampleValues)` · anon `journalLaunchConfig(initIndParam, rawDoeTableObj, wbpjAbsPath, targetComponentName)` | 2321-2354 · 2426-2454 · 2657-2718 | 순수 JSON 조립 블록 |
| `void onWbpjJournalCompleted(activeRunKeys, outputDir, analysisType, doeJsonPath)` | 2739-2774 | 완료 람다 본문. 람다는 disconnect/delete 후 이 메서드를 부른다. 실패 람다 (2787-2796, 10줄) 는 그대로 |

그 외 기존 메서드(런처 초기화 · submit · terminal · motion · STP 슬롯 · `launchAnsysJournalDirect` · `cancelAllRuns` 등) 는 본문 변경 없이 파일만 옮긴다.

### 동작 변경 2건 (오작동 경로 → ERROR)

| # | 경로 | 현행 | 왜 명백히 오작동인가 | 이 판 |
|---|---|---|---|---|
| ① | `.inp` / `.dfsxml` 템플릿, rawSamples 없음 (또는 DashManager 없음) | [E] 로 흘러 `.inp`/`.dfsxml` 본문을 토큰 치환해 `{key}.dat` 로 쓰고 MAPDL 에 제출 (1943-2022, 파일명 1981 고정) | Abaqus 덱 · Motion XML 을 MAPDL 이 읽는다. 결과물이 나올 수 없다 | 디스패처에서 `isInp \|\| isDfsxml` 이면 ERROR + return. `.dat` 는 폴백 유지 |
| ② | `.dfsxml` 템플릿, source 에 `Morphing` 없음 | D2 가 dfsxml 을 partConfig 로 모핑 → D4 가 `{key}.dat` 를 찾음 | 모핑 실행기는 dfsxml suffix 에 `.dat` 를 쓰지 않는다 (`controller/DashMorphingDoeExecutor.cpp:481-497`). D4 의 "Generated file missing" 으로 전 샘플 Failed 확정 | [D] 진입 직후 `isDfsxml && !hasMorphing` 이면 ERROR + return. 모핑 · 런처 초기화 전 |

### 철회한 동작 변경 6건 (이전 판 → 이 판)

이전 판은 분해하는 김에 배선까지 고치려 했다. 기계적 분해 원칙에 따라 전부 철회하고 후속으로 돌린다.

| # | 이전 판 제안 | 이 판 | 보존 방법 |
|---|---|---|---|
| 3 | 상태 보고 헬퍼 통일 (영속 + 시그널) | 사이트마다 원문 (영속만 / 둘 다) | 헬퍼 없음 |
| 4 | 조건 Set 경고를 dat 경로로 이동 | 모든 케이스에서 계산·경고 | `substitutionTokens` 를 `makeDoeRunContext` 에서 계산 |
| 5 | 전 샘플 생성 → 전 샘플 제출 | 샘플마다 교차 | 루프를 쪼개지 않음 |
| 6 | dfsxml 의 MAPDL 런처 초기화 제거 | 유지 | `prepareMorphingBatch` 에 원문 포함 |
| 7 | active 판정 통일 | 루프마다 원문 판정 | `activeKeys` 필드 없음, 루프 원문 |
| 8 | 도달 불가 WARN 삭제 | 유지 | `prepareMorphingBatch` 에 원문 포함 |

`ensureRunDir` · `reportCaseStatus` · `resolveMorphPartName` 헬퍼도 도입하지 않는다 (사이트마다 로그 문구가 달라 통일하면 로그가 바뀐다).

### 보존 규칙

- `templateFilePaths.first()` 만 사용 ([Project-Manifest-3-Module-Deck-Ownership](Project-Manifest-3-Module-Deck-Ownership.md)). 다중 deck 은 수동 전환.
- `processEvents` · `msleep` 16곳 위치 그대로 (DOE-D11, #456 소유).
- 로그 모듈 `Analysis`, 자식 프로세스 태그 `[job=runKey proc=…]` (`docs/unified-logger.md`).
- 쓰기 → 읽기 순서 원문 그대로: `m_currentAnalysisType` (1318, ctx 생성 중) → 모핑 콜백 · `m_feSafeTemplateProjectAbsPath` (1382) → `launchFeSafePost` · 스냅샷 (1772-1774) → `startNextMotionLauncher` · `m_abaqusRunDirs.insert` (1829) → `submitAbaqusTask`.
- Direct `.wbpj` 시그널 체인 (2152-2172) 과 2166-2167 의 disconnect 원문.
- `.stli` 부재 시 Enqueued 로 남는 현행 (1385-1393 이 1401 검사보다 앞) 유지.
- 새 이름은 `docs/coding-convention.md` (camelCase, 새 멤버 `_` 접미). 기존 `m_` 멤버 그대로 (#386 정렬 작업 몫).

### 삭제

컴파일러가 미호출을 보증하는 것만.

| 대상 | 근거 |
|---|---|
| `DashJobRunner::createRunsFolders` (502-531) + 선언 h:46 | 호출부 없음 |
| anon `copyFilesToDirectory` (241-269) | 호출부 없음 (stli 복사는 1432-1450 인라인) |
| 지역 `rawSamples` (1300) | 미사용 |

`DashAnalysisLauncher::writeCaseDat` 래퍼 · `m_setNameSnapshot` · `DashAnalysisLauncher` 의 중복 2건은 건드리지 않는다 (공개 표면 · 다른 파일). 범위 밖이라 언급만: `DashAnalysisLauncher::createRunsFolders` (중복·미호출), `DashAnalysisLauncher::isDfsxmlWithMorphing` (동일 구현 중복), `m_designVariableModel` · `m_inputReferenceFileName` (setter 가 불리나 이 클래스는 읽지 않음), 1627 의 로컬 `DashAnalysisLauncher` 생성.

### 작업 순서

Phase 는 빌드 지점이자 커밋 단위다 (ticket-implement Phase 6.7, `pr.merge_method: merge`). 서식 커밋 분리는 `docs/coding-convention.md` "적용 범위".

```
[Phase 0] 서식 커밋
   │   1. clang-format -i: DashJobRunner.{h,cpp}, DashAnalysisLauncher.{h,cpp}
   │      (InsertBraces · 탭/공백 혼재로 대부분 줄이 바뀜. 기능 변경과 분리)
   │   ※ blame 을 쓰면 .git-blame-ignore-revs 에 이 커밋 등록
   ▼

[Phase 1] 문서 정합
   │   1. Issue #269 본문 · 이 페이지를 확정판(동작 변경 2건 + 철회 6건, 헬퍼 없음)으로 갱신
   ▼

[Phase 2] 케이스 함수 추출 (빌드 지점 5개)
   │   1. 죽은 코드 3건 삭제
   │   2. DoeRunContext + makeDoeRunContext + emitEnqueued. 구 본문은 ctx 필드를 읽도록만 교체
   │   3. runStliDoe, runWbpjDoe 추출. 구 본문의 분기를 호출 1줄로 교체
   │   4. MorphingPrep + prepareMorphingBatch, runDfsxmlMorphingDoe, morphFromTemplate,
   │      submitMorphedInpJobs, submitMorphedDatJobs 추출
   │   5. runTemplateFallback 추출 → 구 본문이 위 디스패처 형태로 남음.
   │      오작동 경로 2곳 ERROR return 삽입. generateInputCases → runDoeJobs 개명
   │      (DashJobRunner.h:38 · 주석 h:20, DashAnalysisLauncher.h:130 · .cpp 1261/1269/1428)
   │   ※ 각 단계 뒤 git diff 로 옮긴 블록이 원문과 같은지 확인 (--color-moved)
   ▼

[Phase 3] runDirectJobs 분해
   │   1. 버킷 4개 → submitDirect* / queueDirect* / startDirect*. taskCount 합산 · jobStarted 원문
   ▼

[Phase 4] wbpj 내부 분해
   │   1. loadInitialIndependentParameter, stpCaseConfig, journalLaunchConfig
   │   2. onWbpjJournalCompleted (완료 람다 본문 → 메서드)
   ▼

[Phase 5] TU 분리 (로직 변경 없음)
   │   1. DashJobRunnerCae.h 생성, 케이스별 .cpp 5개로 정의 이동
   │   2. 헤더 private 절 케이스별 재배치, private slots 블록 병합
   │   ※ git diff -M --color-moved 로 이동만인지 확인. GLOB_RECURSE 라 configure 재실행
   ▼

[완료] 검증 후 PR
       PR 본문에 "동작 변경 2건" 표를 옮겨 적고, 나머지는 Extract Method 와 파일 이동뿐임을 밝힌다
```

### 의존성 및 영향 범위

| 대상 | 영향 |
|---|---|
| `model/DashAnalysisLauncher.{h,cpp}` | `generateInputCases` → `runDoeJobs` 개명뿐 (h:130, cpp 1261/1269/1428) |
| `CMakeLists.txt` | 변경 없음 — `GLOB_RECURSE … CONFIGURE_DEPENDS` 가 새 .cpp 를 잡는다 |
| `tests/` | 변경 없음 |
| 뷰 | 변경 없음 — `DashAnalysisLauncher` 를 거친다 |
| Wiki `Code-Map-User-Flow-Analysis-Launcher` · `Code-Map-User-Flow` · `minhopark-Index` | 줄 번호 · 분기도 · "738줄 / 16곳" 서술이 깨짐. 완료 후 갱신 |
| #452 | 범위 포함 (.stli·.wbpj·.dfsxml 추출). "동작 불변" 에 오작동 경로 2건의 ERROR 화가 예외 |
| #456 | 후행. 정규 경로 비동기 전환을 케이스 함수 단위로 착수 가능 |

## 검증

앱 빌드는 Windows 전용 (vcpkg x64-windows). 이번 변경은 `tests/` 를 건드리지 않는다.

1. Phase 마다 Windows 빌드 통과. 링커가 중복 정의 · 누락 정의를 잡는다.
2. 정의 수 대조: 헤더 선언 수 = `grep -c "DashJobRunner::" model/DashJobRunner*.cpp` 합.
3. 이동 검증: Phase 2-5 각각 `git diff -M --color-moved=dimmed-zebra` 로 옮긴 블록이 원문과 동일한지 확인. 다른 줄은 ctx 필드 참조 · 함수 경계뿐이어야 한다.
4. 수동 실행 — 현행과 동일 동작이 기준. 샘플 2개 중 1개 inactive:

| 케이스 | 현행과 같아야 하는 것 |
|---|---|
| .dat 치환 (rawSamples 없음) | `{key}.dat` 생성 → MAPDL 제출, 샘플마다 교차 |
| .dat 모핑 | `{key}.dat` + `{key}.vtu`, MAPDL 제출 |
| .inp | 모핑된 `{key}.inp`, Abaqus 제출 |
| .inp / .dfsxml, rawSamples 없음 | ERROR 1줄, 폴백 없음, 파일 생성 없음 (동작 변경 ①) |
| .dfsxml 모핑 | `{key}.vtu` → `{key}.dfsxml` → motion-launcher 순차 |
| .dfsxml 모핑 없음 | ERROR 1줄, 모핑 실행 없음 (동작 변경 ②) |
| .wbpj | STP 배치 → Journal → RST 판정. 중간 취소 시 잔여 Cancelled |
| .stli | 출처 `.odb` 복사 → fe-safe. 출처 없으면 Failed |
| Direct 4종 | 각 1개 파일로 제출 |
| 취소 | 각 케이스 실행 중 `cancelAllRuns` → Cancelled |

5. 로그: 케이스마다 실행 전후 로그를 비교해 문구·순서가 같은지 확인 (헬퍼를 넣지 않았으므로 같아야 한다).

## 후속 (범위 밖)

- **공용부 추출 일괄 정리** — 이번에 하지 않는다. 동작 불변으로 뽑을 수 있다고 본 후보: run 디렉터리 경로 계산 2줄 (6곳: 1422, 1433, 1692, 1825, 1886, 1979) · `resolveAbaqusExecutablePath`/`resolveFeSafeExecutablePath` 병합 (후보 파일명만 다름) · wbpj 결과 파일 탐색 `entryList` + `QDirIterator` 폴백 (2245, 2745, 2758) · DOE JSON 읽기 (1249, 860, 2323, 2337). 보류로 본 것: mkpath+로그 5곳 (문구 상이), `setSampleStatus`+`emit` 쌍 10곳 (순서 2종), 런처 초기화·submit·terminal 3벌 (차이가 본질), Journal 연결 수명 보일러플레이트 2벌, active 샘플 루프 7곳 (판정 2종).
- 상태 보고 불일치 (모핑 실패가 `analysisFinished` 에 닿지 않음), dfsxml 의 불필요한 MAPDL 초기화, 도달 불가 WARN — 별도 티켓.
- `processEvents` 폴링 → 시그널 전환 (DOE-D11, #456). 케이스 함수 단위로 다룰 수 있다.
- Direct `.wbpj` 2166-2167 광역 disconnect 버그.
- `DashAnalysisLauncher::writeCaseDat` 래퍼 · `createRunsFolders` · `isDfsxmlWithMorphing` 중복, `m_setNameSnapshot` 등 쓰기 전용 멤버.
- 케이스별 전략 클래스(대안 C)는 케이스 함수를 구현체 본문으로 삼아 후속 판단.
- Wiki `Code-Map-User-Flow-Analysis-Launcher` 줄 번호·분기도 갱신.

## 참고 자료

- [205-2-w6-w10-change-log-and-remaining-design](205-2-w6-w10-change-log-and-remaining-design.md) — #269 절, 방향 2안
- [Code-Map-User-Flow-Analysis-Launcher](Code-Map-User-Flow-Analysis-Launcher.md) — 현행 분기도 (완료 후 갱신 대상)
- [194-1-async-execution-patterns](194-1-async-execution-patterns.md) — Direct `.wbpj` 시그널 체인 참조 구현
- [264-2-batch-stage-ledger-concepts](264-2-batch-stage-ledger-concepts.md) — 워크플로별 단계 수
- [Project-Manifest-3-Module-Deck-Ownership](Project-Manifest-3-Module-Deck-Ownership.md) · [Project-Manifest-4-Ticket-Slicing](Project-Manifest-4-Ticket-Slicing.md) — `.first()` 결정, 브랜치·커밋 규칙
- `docs/coding-convention.md`, `docs/unified-logger.md`
