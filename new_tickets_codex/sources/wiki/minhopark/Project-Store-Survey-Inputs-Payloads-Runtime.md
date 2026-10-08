# 입력 셋 · 페이로드 · 실행 경로 — 저장 구조 현황

> **이 문서는 [[Project-Store-Survey-Key-IO-Ledger]] 의 여집합이다.** 대장이 키 단위로 잰 것(파일 12패턴 · 키 65개 · 왕복 판정 · I/O 시점)은 여기에 없다. 대장이 축 밖으로 뺀 셋을 잰다 — 프로젝트를 시작하는 데 필요한 **입력 셋**, config 가 가리키는 **페이로드 내부**, 상태가 파일에 닿기까지의 **실행 경로**.
>
> 통합 출처: `Project-Store-Survey-Layout-and-Sets`(2026-08-09) · `Project-Store-Survey-Config-Field-Layers`(2026-08-18) · `Project-Store-Survey-Artifact-Formats`(2026-08-19) 3종의 고유분. 중복분은 대장으로 넘기고 원본은 폐기했다.
> 측정 시점: `dev` @ `4c7608e` — **구 3문서의 승계가 아니라 전 앵커 재확인**이다. 구 측정과 달라진 것은 8절.
> 검증 수준: 정적 코드 근거만 — 빌드·실행 검증 없음 · 외부 도구(exe) 내부 미확인 · 실측 파일 크기·피크 메모리 미수집

## 개요

| 축 | 묻는 것 | 절 |
|---|---|---|
| **입력 셋** | 프로젝트를 시작하려면 무엇이 있어야 하고, 무엇이 1급 개체가 아닌가 | 1\~2 |
| **페이로드** | 계산이 만든 대용량 데이터는 어떤 형식으로 얼마나 쌓이는가 | 3\~4 |
| **실행 경로** | 케이스 상태가 파일에 닿기까지 몇 벌의 쓰기를 거치는가 | 5\~6 |

한 줄씩 — **Morphing 은 `.inp` 1개로 서지만 CAD 는 2파일 + 솔버 2종이고 해석조건 연결이 미구현이다.** **DataPreprocessor XML 은 base64 텐서를 담은 자체 컨테이너이며 샘플마다 connectivity 를 재기록한다.** **케이스 상태는 한 전이마다 두 벌로 써지고, 실패 사유는 어떤 파일에도 남지 않는다.**

---

## 1. 최초 입력 셋

### 1.1 Morphing — `.inp` 하나로 충분하다

형상·해석조건에 관한 한 충분하다. `.inp` 는 reader-writer 백엔드로 로드돼 넷을 공급한다.

| 공급 항목 | 소비처 |
|---|---|
| 파트/인스턴스 메시 | Modeling Tree · VTK 렌더 · 모핑 대상 |
| NSET / ELSET | 핸들 고정점 · Constraint |
| FE condition (하중·경계조건) + 편집 스키마 | Condition Parameterization → `DV-Condition` |
| 역방향 쓰기 (`updateMeshPoints` · `exportSolverInput`) | 샘플별 새 `.inp` 생성 |

**받는 확장자는 둘뿐이다** — `controller/DashRwSession.cpp:1360-1370` 이 `.inp` → Abaqus, `.dat` → AnsysMechanical 로 가르고 나머지는 `Unsupported file format` 으로 실패한다. `[Add File]` 필터는 12종을 받으므로(`view/DashMainWindow.cpp:316-317`) **파일은 프로젝트에 들어오지만 컨텍스트가 생기지 않는 조합이 있다.**

핸들·그룹·모핑 함수·constraint·DV 범위는 원본에서 읽는 것이 아니라 GUI 에서 저작돼 config + VTP 에 저장된다.

`.inp` 밖에서 따로 공급해야 하는 것 셋 — 솔버 실행 경로(`QSettings` 머신 전역, **프로젝트 밖**) · KPI/response 정의(DataPreprocessor config) · FE-safe 한정 `.stli` 템플릿과 Material(`input_files`).

### 1.2 CAD — 단일 파일로 성립하지 않는다

```
[형상] .prt (NX 파트)
   │   [Add File] → NX 데몬 stdin: loadPrt "<prt>" "<configs/*.stp>" (controller/DashSolverNxCad.cpp:142-144)
   │   → STP 생성 → OCCT 뷰로 분기 렌더 → 데몬 stdout 의 파라미터 JSON → 독립·종속 파라미터 표
   ▼
[해석 템플릿] .wbpj (Ansys Workbench)
   │   Reference File 행으로 등록. target_component 콤보 = .wbpj 주변 디렉토리 재귀 스캔한 .prt 목록
   │   (view/DashReferenceFileWidget.cpp:810-817)
   ▼
[솔버] NX + Ansys 둘 다 설정돼야 그 행이 "Set" 판정
```

**해석조건 연결이 없다.** Morphing 은 메시를 변형하므로 노드 번호가 보존돼 원본 NSET 이 그대로 유효하지만, CAD 는 형상 재생성 → 재메싱이라 NSET 이 무효화된다. 그 격차를 메우는 **Match NSET 탭은 `DASH_BUILD_DEV` 빌드에만 노출되고 로직이 없다**(`view/DashGeometryParameterCADWidget.cpp:128-139` — 릴리스 빌드는 `removeTab` + `delete`). 같은 dev 블록에 있던 Meshing 은 탭에서 `view/dialog/DashMeshingDialog` 로 분리됐으나 진입 버튼은 여전히 dev 한정이다(`:297-300`).

결과적으로 **CAD + Abaqus `.inp` 조합은 end-to-end 로 동작하지 않고**, `.wbpj`(Ansys Journal) 경로만 DoE 연동이 존재한다.

### 1.3 대조

| 항목 | Morphing | CAD |
|---|---|---|
| 형상 원본 | `.inp` (또는 `.dat`) | `.prt` |
| 해석 템플릿 | 같은 파일이 겸함 | `.wbpj` 별도 |
| 해석조건 원천 | `.inp` 의 FE condition | **없음** (NSET 매칭 미구현) |
| 필요 솔버 | Abaqus 또는 Ansys | NX **+** Ansys |
| 최소 파일 수 | **1** | **2** |
| 형상 변형 | 메시 직접 변형 (노드 번호 보존) | 재생성 → 재메싱 (노드 번호 무효) |

---

## 2. Set 단위와 다중성

### 2.1 Set 번호는 카테고리마다 독립이다

`generateNextSetName()`(`model/DashProject.cpp:559`)은 **해당 카테고리 트리만** 스캔해 빈 번호를 채운다. Geometry `Set1` 과 AnalysisLauncher `Set1` 사이에 결합은 없다 — **이름이 같은 것은 우연이다.** 그런데 하류가 상류를 못 찾을 때 이 이름 관례로 추정하는 자리가 있다(2.4).

### 2.2 복수 해석 모델 — 지원되나 1급 개체가 아니다

| 지점 | 구현 |
|---|---|
| Project Tree | 프로젝트 루트의 파일시스템 뷰 — `.inp` 를 몇 개든 복사 가능 |
| Registry | `filePath → Context` 해시로 복수 보유. **eviction 없고 active 는 항상 1개** (`controller/DashAnalysisModelContextRegistry.h:54`) |
| Reference File 표 | 행 다중 추가, `input_files[]` 에 저장, 라디오로 1개 active |
| 실행 폴더 분리 | `analysisType` = 템플릿 basename → `AnalysisLauncher_{Set}/{refBase}/runs*/` |

**어떤 Set 이 어떤 `.inp` 에 속하는지 적는 필드가 없다.** 결합은 DV 의 `source` 문자열에 파일명이 박혀 있는 것뿐이고, 그 문자열을 `split("|")` 한 결과가 곧 실행 폴더 이름이 된다 — **디렉토리 구조가 문자열 파싱 결과에 의존한다.** 게다가 active context 는 직렬화되지 않아 재오픈 시 "이 Set 은 어느 파일 기준인가" 가 복원되지 않는다.

### 2.3 복수 샘플 셋 — 덮어쓴다

같은 Set 에서 DOE 를 다시 [Run] 하면 이전 샘플 셋은 사라진다. `DOE Table` 섹션이 새 배열로 **통째 대입**되기 때문이다.

| 사실 | 결과 |
|---|---|
| run 키는 항상 `runs1..runsN` 재발급 | 이전 실행과 키 충돌 |
| `createRunsFolders()`(`model/DashAnalysisLauncher.cpp:916`)는 **없는 폴더만 생성**, 기존 삭제 없음 | 50샘플 → 20샘플 재실행 시 `runs21..runs50` 이 JSON 에서 사라졌는데 **디스크에는 잔존** |

**Resample 은 껍데기까지 왔고 로직만 없다.** variant 3종의 하나로 승격됐고(`DashProject.cpp:687-700`), 전용 위젯(`view/DashAnalysisLauncherResampleWidget`)과 컨텍스트 메뉴 "Resample DOE"(`view/DashProjectWidget.cpp:233-240`)와 `Set{N}-Resample` 생성 경로(`:735-737`)까지 있다. 그런데 위젯 구현은 **63줄의 UI 배선뿐이고 `mResampleRunButton` 에 `connect` 가 레포 전체에서 0곳**이며 모델 측 구현도 없다. 여러 샘플 셋을 보존하는 방법은 여전히 Set 을 새로 만드는 것뿐이다.

### 2.4 상위 의존성의 UI 노출

각 모듈이 소비하는 상위 산출물이 (a) 파일에 기록되는지 (b) 재진입 시 복원되는지 (c) 해결 실패를 알리는지.

| 모듈 | 상위 의존성 | 기록 | 복원 | 미해결 시 |
|---|---|---|:---:|---|
| AnalysisLauncher | Geometry·Condition config | `Selected Design Variables` | O | 조용히 미선택 |
| AnalysisLauncher | 기준 해석파일 | `input_files[]` | O | 행에서 사라짐 |
| DataPreprocessor | AnalysisLauncher + analysisType | `Dataset.*` | **X** | 항상 플레이스홀더 |
| ModelBuilder | `DataPreprocessor_{Set}/*.xml` | `Data Label.Dataset` | O | 디렉토리명 규약 어긋나면 콤보 `-1` |
| ModelRunner | `ModelBuilder_{Set}` 폴더 | **없음** | **X** | 첫 폴더 무조건 선택 |
| Optimizer | `ModelBuilder_{Set}` 폴더 | **없음** | 부분 | 세션 잔존값 → 이름 관례 → 첫 폴더 |

**기록은 하는데 아무도 읽지 않는다** — DataPreprocessor 위젯은 콤보를 채운 직후 무조건 선택을 해제한다(`view/DashDataProcessorWidget.cpp:142`·`:151`). 복원 로직처럼 보이는 `runKpiAutoTest()` 는 `--test-kpi` 인자 전용 자동 테스트 경로다.

**조용한 기본값** — ModelRunner 는 세션 잔존값이 없으면 `setCurrentIndex(0)`(`view/DashModelRunnerWidget.cpp:670-676`), 로드 시점에도 `folders.first()`(`:744`). Optimizer 는 3단 추정이다 — 이전 선택 → `ModelBuilder_{자기 SetName}` **이름 관례** → `folders.first()`(`viewmodel/DashOptimizerPresentationModel.cpp:152-158`, 위젯 측 `view/DashOptimizerWidget.cpp:660-662`). 2.1 에서 봤듯 Set 번호는 카테고리마다 독립이라 그 관례는 보장되지 않는다. **잘못 선택돼도 화면에 아무 표시가 없다.**

**화면 어디에도 계보가 없다** — 사이드바는 카테고리별 평면 목록이고 상위/하위를 표시하는 요소가 없다. 정방향은 모듈 탭을 열어 콤보를 봐야 하고(그 값조차 위 두 문제로 신뢰할 수 없다), 역방향은 `configs/*.json` 을 직접 열어야 하며, 상위 파일이 삭제·개명돼도 경고가 없다.

---

## 3. 페이로드 인벤토리와 포맷

### 3.1 계산이 만드는 파일

| 단계 | 산출물 | 형식 |
|---|---|---|
| 케이스 입력 | `runs{K}.vtu` (모핑 메시, `vtkXMLUnstructuredGridWriter` · `controller/DashMorphingDoeExecutor.cpp:865`) | VTU |
| 케이스 입력 | `runs{K}.dat` / `.inp` (조건값 inject → export → 즉시 restore) · `.dfsxml`(motion-writer) · `.stp`(NX 데몬) | 솔버 네이티브 |
| 솔버 실행 | `runs{K}.rst` / `.odb` / `.dfr` / `.op2` | 바이너리, 원위치 유지 |
| 솔버 실행 | `runs{K}/logs/*` — `*.log *.msg *.sta *.dat *.prt *.com *.rec *.txt *.json` (`model/DashJobRunner.cpp:1163`) | 텍스트 |
| 전처리 | `DataPreprocessor_{Set}/*.xml` | **XML + base64 텐서** — 4절 |
| 학습 | `model_info.json` · `{response}/{model}_*/config.yaml` · `{response}/*.pt` · `rendered_results/*.vtu` | JSON·YAML·PyTorch·VTU |
| 예측 | `ModelRunner_{Set}/{base}.dat` · `.vtu` · `{base}_input_geometry.vtu` · `*.csv` | 혼합 |
| 최적화 | `optimum.json` · `optimization_log/convergence_history.png` | JSON · PNG |
| MCU (Excel 입력) | `{temp}/dashopti_mcu_val_{base}_{epochMs}.csv` | CSV — 프로젝트 밖이나 호출부 2곳이 `QFile::remove` 로 회수 |

### 3.2 포맷 6종 적합성

| 형식 | 담는 것 | 판정 |
|---|---|---|
| JSON | 설정 · DV 메타 · DOE 표 · 케이스 상태 · 최적해 | 설정에는 적합. 상태·대용량 표가 같은 파일인 것이 문제 |
| **XML + base64** | DataPreprocessor 데이터셋 | **부적합** — 텍스트 봉투에 바이너리 텐서 (4절) |
| VTU / VTP | 메시 · 핸들 · 렌더 필드 | 적합 — 이미 파일 분리 + 표준 포맷 |
| CSV | DOE 내보내기 · MCU 데이터셋 · 플롯 내보내기 | 적합 (보조 전용) |
| 솔버 네이티브 | `.rst` `.odb` `.inp` `.dfsxml` `.stp` 등 | 적합 — 원본 보존이 목적 |
| YAML / PT / PNG | 외부 도구 산출 | GUI 는 읽기만 — 선택권 없음 |

**참조할 선례** — GeometryParameter 는 바이너리 페이로드를 VTP 로 빼고 JSON 은 파일명만 든다. 프로젝트에서 "정의 메타 ↔ 대용량 페이로드" 를 분리한 유일한 사례다.

---

## 4. XML 컨테이너 정밀 측정

### 4.1 구조

`DataPreprocessor_{Set}/` 아래 XML 1개 = **result request 1건**(component × loadStep × response) × **전 샘플**.

```
<root><dict>
  <dict_item key="0">          ← 샘플 0
    <dict_item key="{param}">       DV 값        float32[1]
    <dict_item key="node_location">  절점 좌표    float32[P, 3]
    <dict_item key="connectivity">   위상        int32[C, pad]
    <dict_item key="{response}">     결과 필드    float32[P, ncomp]
  <dict_item key="1"> … 같은 구조 반복
  <dict_item key="model_info"> …
</dict></root>
```

모든 텐서는 `<tensor dtype shape><base64>…</base64></tensor>` 다. **XML 은 스키마가 아니라 봉투이고 실질은 자체 정의 바이너리 직렬화다.**

### 4.2 샘플마다 connectivity 재기록

`DashResultXmlWriter` 는 `m_nodeLocationWritten` · `m_connectivityWritten` 플래그로 중복을 막게 설계됐는데 두 지점에서 무력화된다 — `appendSample()` 진입부가 두 플래그를 `false` 로 리셋하고(`model/preprocessor/DashResultXmlWriter.cpp:985-986`), `processSingleSample()` 이 샘플마다 writer 를 새로 만든다(`model/preprocessor/DashResultProcessor.cpp:309`).

판정은 갈린다 — **`node_location`** 은 모핑 DOE 에서 샘플마다 실제로 다르므로 필수다(조건-only·CAD DOE 에서는 전 샘플 동일). **`connectivity`** 는 모핑이 위상을 보존하므로 **전 샘플 동일한 순수 중복**이다.

### 4.3 connectivity 패딩이 tet 메시에서 2배

`int paddingTarget = (maxStride < 8) ? 8 : maxStride;` (`DashResultXmlWriter.cpp:94`·`:165`) — 셀당 `paddingTarget` 개 int32 를 쓰고 부족분은 `-1` 로 채운다.

| 셀 종류 | 실제 절점 | `paddingTarget` | 낭비 |
|---|---|---|---|
| 선형 tet | 4 | 8 | **50%** |
| 선형 hex | 8 | 8 | 0 |
| 2차 tet | 10 | 10 | 0 |

### 4.4 증폭 3겹

| 겹 | 배율 | 근거 |
|---|---|---|
| base64 | ×4/3 | 디스크·메모리 양쪽 |
| `QDomDocument` 누적 | ×2 + 노드 오버헤드 | 전 샘플을 DOM 에 쌓은 뒤 `doc.save()`. `QDomText` 는 UTF-16 이라 base64 문자열이 2바이트/문자 |
| request 수 | ×M | request 마다 별 XML → 지오메트리가 파일 수만큼 재중복 |

```
size ≈ (4/3) × N × [ P·3·4 (node_location) + C·pad·4 (connectivity) + P·ncomp·4 (field) ]
```

생성 피크 메모리는 대략 그 2배 이상. 실측값은 수집하지 않았다.

### 4.5 소비 측이 대칭으로 같다

**ModelBuilder (경량 — 잘 된 사례)** — `QXmlStreamReader` 로 훑으며 `model_info` 가 아닌 노드를 `skipCurrentElement()` 로 건너뛴다. 거대 텐서를 만지지 않고, 학습 본체는 외부 도구가 파일을 직접 읽는다.

**ResultsAnalyzer (중량 — 문제)** — `DashXmlParser::loadFromXml`(`model/analyzer/DashXmlParser.cpp:14`)이 파일 전체를 재귀 트리로 복원하며 **모든 텐서를 base64 디코드해 `Eigen::MatrixXf` 로 실체화**하고(`:122`), 그 다음 `extractReducedValues`(`model/analyzer/DashDataLoader.cpp:136`)가 변수당 스칼라 1개로 축약한다. **스칼라 하나를 얻으려고 데이터셋 전량을 펼치고**, 캐시가 없어 플롯 요청마다 반복한다.

생산(DOM 누적 → 일괄 저장)과 소비(일괄 로드 → 전량 복원) 양쪽이 스트리밍이 아니다.

### 4.6 파일명 규약 2종 혼재

| 경로 | 규약 | 근거 |
|---|---|---|
| 일반 result request | `{comp}_{step}_{substep}_{name}.xml` (4파트) | `model/DashDataProcessor.cpp:1828`·`:1841` |
| KPI 경로 (Modal · Circularity · PEEQ · Buckling · Fatigue) | `{comp}_{loadStep}_{name}.xml` (3파트) | `:3269`·`:3653`·`:3970`·`:4252`·`:4535` |

소비 측이 파일명에서 의미를 되읽어야 하는데 파트 수가 경로마다 다르다.

---

## 5. 실행 상태가 파일에 닿는 경로

### 5.1 한 전이에 두 벌이 써진다

```
DashJobRunner (전이 발생)
├─ configManager.setSampleStatus(...)          ← 1차 쓰기 · 레포 30곳에서 직접 호출
└─ emit caseStatusUpdated(key, status, type)   ← 39곳
      └─ DashAnalysisLauncher.cpp:56 connect → onCaseStatusUpdated (:1020)
           └─ setSampleStatus (:966)           ← 2차 쓰기 · 같은 파일
                ├─ QMutexLocker (:971)  — 무락인 1차 쓰기와 짝이 맞지 않는다
                ├─ oldStatus 기반 전역 로그 4종 (:1002-1015)
                └─ emit caseStatusUpdated(key, status) (:1017) → 위젯 표 (WidgetBase:89)
```

`DashDoeConfigManager::setSampleStatus`(`model/DashDoeConfigManager.cpp:528`)와 `DashAnalysisLauncher::setSampleStatus`(`:966`)는 **같은 JSON 쓰기를 두 벌로 복제**한 것이다 (`oldStatus` 반환 유무만 다르다). 둘 다 전문을 파싱해 samples 를 순회하고 전문을 다시 직렬화한다.

### 5.2 Direct Launcher 는 평문 키를 쓴다

`runDirectJobs`(`model/DashJobRunner.cpp:1924`)는 `analysisType` 을 빈 문자열로 방출한다(`:2012` — `emit caseStatusUpdated(key, "Pending", QString())`). 런처 릴레이는 그것을 받아 `status_{type}` 이 아닌 **평문 `"status"` 키**에 쓴다.

**키 충돌은 이론이 아니라 정상 워크플로다.** direct 키는 입력 파일의 `completeBaseName()`(`:1951`·`:1977`·`:2008`·`:2040`)이고 DOE 케이스 입력은 `runs{K}` 이름으로 생성되므로, **DOE 가 만든 케이스 파일을 Direct 로 재실행하면 키가 정확히 일치**해 direct 실행 상태가 DOE 표에 기록된다.

### 5.3 `"Enqueued"` 가 이전 실행을 리셋한다

배치 착수 시 활성 키 전량에 대해 `emit caseStatusUpdated(runKey, "Enqueued", analysisType)`(`:1292`)가 나가고, 릴레이를 타고 JSON 에 써진다. **이것이 직전 실행의 `Done`/`Failed` 를 파일에서 지우는 지점이다.** 라이터를 단일화하거나 런처를 순수 릴레이로 바꿀 때, 이 쓰기를 착수 시점의 명시적 쓰기로 승격하지 않으면 이전 실행의 `Done` 이 잔류해 후처리 게이팅(5.4)이 실행 중인 케이스를 완료로 읽는다.

### 5.4 리더 3곳 — 하나는 조용히 오작동한다

| 리더 | 용도 | 상태 필드가 빌 때 |
|---|---|---|
| `view/DashDoeCasesWidget.cpp:250` | 재기동 후 Status 열 복원 | 항상 `"Enqueued"` 표시 |
| `model/DashDataProcessor.cpp:3016` `statusForRunKey` / `:3040` `isRunKeyDone` | 후처리 게이팅 | **조용한 거동 변화** — 관용구가 `st.isEmpty() \|\| isRunKeyDone(k)` 라(`:3206`·`:3609`·`:3930` 등) 빈 값 = 통과. 에러도 로그도 없이 실패 케이스까지 후처리한다 |
| `model/DashJobRunner.cpp:816` `monitorMotionLauncherOutput` | 자기가 쓴 값을 되읽어 조기 완료 판정 | — |

셋 중 `DashDataProcessor` 의 실패 모드가 가장 나쁘다 — **에러 없이 잘못된 결과**를 낸다.

### 5.5 상태 어휘 9종

리터럴 집계(`dev` @ `4c7608e`): `Failed`(53) `Done`(34) `Running`(23) `Success`(11) `Cancelled`(11) `In Progress`(10) `Enqueued`(4) `Interrupted`(2) `Pending`(1).

같은 파일 패밀리 안에서도 갈린다 — ModelBuilder 착수값 `"In Progress"` vs MCU `"Running"`. 어휘 정본을 세우는 설계는 [[Project-Store-Design-Layer-Cut]] 2절(5종 고정)에 있다.

---

## 6. 파일 표현이 없는 상태 9건

| 보유처 | 내용 | 소실 시점 | 파일 표현 |
|---|---|---|---|
| `DashAnalysisModelContextRegistry` | 파싱된 FE 덱 전량 + 멀티블록 + 인덱스 캐시. **eviction 없음** | 앱 종료 | 원본 재파싱으로 복원 |
| `DashManager` | `m_inputVTU` · `m_linearizedVTU` · `m_originalQuadraticCells` · `m_midNodeMap` · 프리뷰 지오메트리 | 앱 종료 | 부분적 (`m_midNodeMap` 은 재계산) |
| `DashMorphingBatchHandle` | 배치 스냅샷 (DeepCopy 메시 일습) | 배치 종료 | 재생성 가능 |
| `DashDataProcessor` | `m_geometries` · `m_availableResponses` · `m_dvTableRoot` · `m_dataset` · `m_modalDefs` · `m_frequencies` | Set 전환 | 재질의로 복원 |
| preprocessor wrapper | 로드된 `.rst`/`.odb` 핸들 | `Clear()` · Set 전환 | 원본 존재 |
| `DashAnalysisLauncher` | `m_cachedSamples`(`model/DashAnalysisLauncher.h:165`) · `m_dvSnapshot` | Set 전환 | `rawSamples` 필드에 사본 |
| 스테이지별 진행 | 케이스 × 스테이지 격자 | 실행 종료 | **케이스당 문자열 1개로 평탄화** — "입력은 됐는데 해석에서 죽었다" 를 구별 못 함 |
| **케이스 실패 사유** | `caseLogUpdated(key, reason)` 로 흐르는 전이 사유 | **앱 종료** | **없다** |
| ResultsAnalyzer 플로터 | 파싱 트리 + 축약 열 | 플롯 재요청마다 폐기 | 원본 XML |

**진짜로 소실되는 것은 하나다.** 9건 중 7건은 원본 파일이나 config 필드에서 복원 가능한 캐시다. `caseLogUpdated` 의 수신부는 런처 릴레이(`model/DashAnalysisLauncher.cpp:57-59`)와 위젯 테이블(`view/DashAnalysisLauncherWidgetBase.cpp:91`)뿐이고 **파일 쓰기 경로가 0곳**이다 — 배치가 실패한 이유를 다음 세션에서 확인할 방법이 없다. 이 둘(실패 사유 · 스테이지 진행)이 설계안에서 어느 자리를 받는지는 [[Project-Store-Design-Rationale]] 1절에 있다.

---

## 7. 부수 발견과 정리 후보

### 7.1 중복·사장 코드

| 항목 | 상태 |
|---|---|
| `DashDoeConfigManager::saveDoeToCsv()` (`:558`) | **호출부 0곳.** 실제로 쓰이는 것은 `DashAnalysisLauncher::saveDoeToCsv()`(`:1477`, 호출 `:271`). 죽은 쪽이 분할 CSV 만 쓰는 기능 적은 구버전 |
| `DashResultProcessor::processSamples()` 의 `xmlWriter`(`:29`) | 생성 후 미참조 dead 객체 |
| `samples` / `rawSamples` 이중화 | `DashDoeConfigManager.cpp:394` 가 같은 샘플 집합을 두 키에 나란히 쓴다 (`samples` 는 `slice`·`active`·`status_*`, `rawSamples` 는 `partName` 이 더 붙는다). `model/DashJobRunner.cpp:2115`·`:2569-2595` 도 같은 키를 쓴다. DOE 표가 커질수록 파일이 2배가 되고, 5.1 의 전량 재작성 비용에 그대로 곱해진다 |
| `mResampleRunButton` | UI 만 있고 `connect` 0곳 (2.3) |
| `model_config.json` | 제외 필터에만 등장, 쓰는 코드 없음 |
| `DataPreprocessor_{Set}/parallel.json` | 플롯 스펙에 `save_json_path` 로 전달되나 네이티브 렌더러 전환 후 소비 지점 미확인 |

### 7.2 측정에서 직접 따라 나오는 후보

설계·우선순위는 범위 밖이다.

| # | 후보 | 근거 | 성격 |
|---|---|---|---|
| 1 | `connectivity` 를 파일당 1회로 (모핑은 위상 불변) | 4.2 | 순수 중복 제거 |
| 2 | `paddingTarget` 을 실제 `maxStride` 로 | 4.3 | tet 메시 50% 절감 |
| 3 | 조건-only · CAD DOE 에서 `node_location` 도 파일당 1회로 | 4.2 | 조건부 중복 제거 |
| 4 | XML → 스트리밍 가능 포맷 | 4.4·4.5 | 포맷 교체. **의존 추가 없이 가능한지는 미확인** (8절 5번) |
| 5 | ResultsAnalyzer 소비 경로에 축약값 캐시 또는 부분 로드 | 4.5 | 재파싱 제거 |
| 6 | XML 파일명 규약 단일화 | 4.6 | 규약 정리 |
| 7 | **케이스 실패 사유 영속화** | 6 | 유일하게 데이터가 소실되는 항목 |
| 8 | 스테이지별 상태 영속화 | 6 | 7번과 같은 자리에서 결정 |
| 9 | `rawSamples` 제거 또는 `samples` 와 통합 | 7.1 | 파일 크기 2배 요인 |
| 10 | 상태 라이터 단일화 — 단 `"Enqueued"` 리셋을 명시 쓰기로 승격 | 5.1·5.3 | 승격 없이 하면 회귀 |
| 11 | DataPreprocessor 상위 선택 복원 (데이터는 이미 파일에 있다) | 2.4 | **소** — 계보 단절 1건 즉시 해소 |
| 12 | ModelRunner·Optimizer 의 ModelBuilder 폴더 선택 기록·복원 | 2.4 | 조용한 오선택 제거 |
| 13 | Set rename 시 데이터 디렉토리 동반 rename (`renameSet` 은 config 파일명만 고친다 — `model/DashProject.cpp:1416`) | 2.1 | 고아 디렉토리 방지 |
| 14 | Resample 미구현 처분 — 구현하거나 진입점을 내리거나 | 2.3 | 현재는 눌러도 아무 일이 없다 |
| 15 | dead code 3건 삭제 | 7.1 | 정리 |

1\~3번은 포맷을 바꾸지 않고 기록 내용만 줄이는 변경이라 4번과 독립적으로 선행 가능하다. 단 **소비 측(외부 학습 도구)이 `node_location`·`connectivity` 를 샘플마다 있다고 가정하는지 확인이 선행 조건**이다 — GUI 측 파서는 확인했으나 도구 내부는 미확인이다.

---

## 8. 구 측정과 달라진 것 5건

구 3문서(`refactor/async-execution` @ `b97e23a`·`fc167bd`·`b579bcf`)가 기록한 것 중 `dev` @ `4c7608e` 에서 다르게 측정된 것이다.

| # | 구 기록 | 본 측정 |
|---|---|---|
| 1 | 상태 이중 쓰기가 `DashJobRunner::setStageState` → 배치 장부(`DashBatchLedger`) 경유 | **`setStageState` 도 `DashBatchLedger` 도 레포에 없다.** 장부 없이 `configManager.setSampleStatus` 직접 호출 30곳 + `emit caseStatusUpdated` 39곳 구조다. 이중 쓰기라는 **현상은 유지**되나 경로 서술은 전면 교체했다 (5.1). "`Pending` not-applied" 를 근거로 한 구 회귀 분석도 함께 폐기했다 |
| 2 | Resampling 은 탭 하나가 UI 만 존재 | **variant 3종의 하나로 승격**됐고 전용 위젯·컨텍스트 메뉴·Set 생성 경로까지 생겼다. 로직이 없는 것은 같다 — `mResampleRunButton` 에 `connect` 0곳 (2.3) |
| 3 | `docs/Module_Configuration_Files.md` 의 기술 오류 3건 (`Model Upload` 섹션 · XML 파일명 규칙 · `.dashopti` 표기) | **그 문서가 삭제됐다** (`docs/` 에 `index.md` 만 남음, `4c7608e`). 정정 대상이 사라져 관련 후보 3건을 폐기했다 |
| 4 | CAD 위젯의 Meshing·Match NSET 두 탭이 `DASH_BUILD_DEV` 한정 | Meshing 은 `view/dialog/DashMeshingDialog` 로 분리됐고 진입 버튼만 dev 한정으로 남았다. Match NSET 탭은 그대로 (1.2) |
| 5 | `vtkHDFWriter`/`vtkIOHDF` 가 이미 빌드에 포함돼 외부 의존 추가 없이 XML 대체 가능 | **`external/` 디렉토리 자체가 레포에 없다.** 로컬 SDK 로 빠진 것으로 보이며, 이 근거는 현재 확인 불가다 — 7.2 의 4번을 "미확인" 으로 낮췄다 |

구 3문서가 기록한 나머지 사실 중 **파일·키·경로 축은 전부 [[Project-Store-Survey-Key-IO-Ledger]] 로 이관**했다 (루트 3개와 경로 규약 불일치 · config 파일 인벤토리 · 매니페스트 부재 · variant 판정 · DataPreprocessor 사본의 정체 · 외부 도구 양방향 IPC · 전량 재작성 비용 등).

---

## 9. 검증 한계

| 항목 | 근거 강도 | 비고 |
|---|---|---|
| 산출물 인벤토리 · 포맷 (3절) | **강** | 쓰기 지점 전수 grep + 호출부 확인 |
| XML 구조 · connectivity 재기록 · 패딩 (4.1\~4.3) | **강** | writer 전문 + 플래그 리셋·per-sample 생성 2면 대조. **실측 메시로 재현하지 않음** |
| 증폭 3겹 · 크기 산식 (4.4) | **중** | 코드 구조에서 유도. **실측 파일 크기·피크 메모리 미수집** — 태그·들여쓰기 오버헤드 제외한 상한 추정 |
| 이중 쓰기 경로 · direct 평문 키 (5.1\~5.2) | **강** | 시그널·슬롯 양방향 grep + 호출 건수 집계. **실기 재현 미수행** |
| `"Enqueued"` 리셋 (5.3) | **중** | 방출 지점과 릴레이 경로는 확인. 리셋 결과를 실행으로 확인하지 않았다 |
| 리더 3곳의 실패 모드 (5.4) | **강** | 관용구 리터럴 전수 |
| 케이스 사유 미영속 (6절) | **강** | `caseLogUpdated` 수신부 전수 grep — 파일 쓰기 0곳 |
| 메모리 전용 9건 (6절) | **중\~강** | 멤버 선언·eviction 부재는 강. "복원 가능" 판정은 코드 구조 추론 |
| `.inp` 공급 범위 (1.1) | **중** | reader-writer 공개 API 기준. 외부 DLL 내부 미확인 |
| CAD 입력 셋 (1.2) | **중** | NX 데몬 프로토콜은 호출측 코드로만 확인 |
| 상태 어휘 집계 (5.5) | **중** | 리터럴 grep 기준. 변수로 조립되는 값은 누락 가능 |
| 외부 도구가 XML 을 어떻게 읽는가 | **없음** | 바이너리 내부 미확인 — 7.2 의 1\~3번 선행 조건 |
| 실행 검증 | **없음** | 빌드·실행 없이 정적 근거만 |
