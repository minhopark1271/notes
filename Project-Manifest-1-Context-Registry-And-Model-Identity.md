# ContextRegistry 소비자 전수와 모델 식별자 저장소 — 매니페스트 도입 · 조사

> 작업 묶음: 프로젝트 매니페스트 도입과 모듈 의존성 관리
> 관련 Issue: #239
> 마스터: [Project-Manifest-0-Work-Order](Project-Manifest-0-Work-Order.md) — 착수 순서와 문서 배치
> 기반 문서: [Project-Manifest-2-Active-Cursor-Data-Coupling](Project-Manifest-2-Active-Cursor-Data-Coupling.md) · [Project-Store-Design-Wiring-Project-To-Launcher](Project-Store-Design-Wiring-Project-To-Launcher.md)
> 착수 계획: [Project-Manifest-4-Ticket-Slicing](Project-Manifest-4-Ticket-Slicing.md) — 7절 단계 1~5 가 T9~T13 이다

## 개요

세 가지를 잰다 — ① `DashAnalysisModelContextRegistry` 싱글턴 소비자 전수 ② 프로젝트 열기가 그 레지스트리를 채우는 장치가 있는지 ③ `AnalysisModelIdentity.json` 이 실제로 무엇을 하고 있는지. 좌표 기준은 `dev` @ `c989257` 정적 실측이고 빌드·실행 검증은 없다.

**1\~3절은 실측 사실이고 4\~7절은 구상이다.** 구상부는 기존 설계 계열([Project-Store-Design-Wiring-Project-To-Launcher](Project-Store-Design-Wiring-Project-To-Launcher.md))을 참고하되 그것을 전제로 삼지 않는다 — 더 단순한 안이 서면 그쪽을 취한다.

## 기존 설계와의 관계

이 문서의 구상부는 [Project-Store-Design-Wiring-Project-To-Launcher](Project-Store-Design-Wiring-Project-To-Launcher.md) 가 다루는 `reference.json` 과 같은 자리를 다룬다. 그 문서를 근거로 삼지는 않되, 그 자리에 남아 있던 문제 셋과 이 문서가 그것을 어떻게 닫는지를 적어 둔다.

| 쟁점 | 남아 있던 문제 | 이 문서의 방향과 결과 |
|---|---|---|
| 지문 갱신 | 현행 코드가 매 open 지문을 덮어써(`DashRwSession.cpp:1138`) "바인딩 이후 변경" 이 아니라 "직전 open 이후 변경" 을 재고 스스로 지운다. 기존 설계는 동결로 정했으나 그 파일 자체는 남겨 둔다(4.3) | 지문을 원장 한 벌로 두고 등록 시 동결. 변경 감지가 저장값과 그때 계산한 값의 비교로 성립하고, 동결본·갱신본이 갈리는 문제가 사라진다 |
| `.stli` 지위 | 실체가 부모 폴더인데 그것을 가리키는 필드가 없다 — 자매 조사가 지적한 자리 | 편입 자체는 맞다고 본다. 다만 지문을 폴더에 어떻게 매길지가 미설계라 이 문서는 `.dat`·`.inp` 로 범위를 끊는다 |
| content uuid 키 | `ref_` 는 프로젝트 상대경로 v5 파생인데 content uuid 만 canonical 절대경로다(`:1107-1110`). DV-Condition 이 매달린 id 가 프로젝트 이동에 깨진다 — 기존 설계 미결 14 | `ref_` 가 content uuid 를 겸하고 발급은 상대경로 v5 1회. id 가 한 벌이 되고 `AnalysisModelIdentity.json` 은 할 일을 잃어 폐기된다 |

`ContextRegistry` 소비자 좌표는 [Project-Manifest-2-Active-Cursor-Data-Coupling](Project-Manifest-2-Active-Cursor-Data-Coupling.md) 이 이미 21(커서 API) + 20(경로 조회) + 4(시그널) 로 전수한다. 1절은 그것을 `Instance()` 호출 지점 단위로 다시 센 것이고 값이 상충하지 않는다 — 한 `auto& registry = ...Instance()` 줄이 여러 API 호출을 받으므로 단위가 다르다.

## 1. ContextRegistry 소비자 전수

| 항목 | 수치 |
|---|---|
| 참조 파일 | 18 |
| 실제 호출 파일 | 15 |
| `Instance()` 호출 지점 | 34 |
| include 만 있고 미사용 | 3 |
| 시그널 구독 클래스 | 3 (connect 4개) |
| 테스트 코드 참조 | 0 |

쓰기 API(`setActiveContext`) 호출처는 4곳이고 전부 view 계층이다. `count()` 는 호출처가 없다.

| 계층 | 파일 | 사용 API | 용도 |
|---|---|---|---|
| controller | `DashManager.cpp:1027` | `getOrLoad` | `MorphFromDoeSamples` 에서 원본 deck 로드 |
| model | `DashGeometryParameterCAD.cpp:99`·`106` | `get`, `getOrLoad` | `getContext` / `refreshFromLoadedAnalysis` |
| model | `DashConditionParameterization.cpp:111`·`118` | `get`, `getOrLoad` | 동일 패턴 |
| model | `DashOptimizer.cpp:1399` | `getOrLoad` | `performMorphing` 대상 deck |
| model | `DashModelRunner.cpp:1974` | `getOrLoad` | `performMorphing` 대상 deck |
| model | `geometry/DashMorphingUtils.cpp:311`·`357` | `getOrLoad` ×3 (`:312`·`:360`·`:375`) | 원본·morphed deck 컨텍스트 |
| viewmodel | `DashGeometryParameterPresentationModel.cpp:45` | `activeFilePath`, `activeContext` | `buildDvGeometry` |
| view | `DashMainWindow.cpp:375`·`395`·`431`·`2208`·`2415`·`2603`·`3270`·`3310` | `get` ×2, `activeContext` ×4, `activeFilePath` ×2, `activeActor` ×2, `setActiveContext` ×3, 시그널 ×2 | 색상·투명도 변경, 파일 로드, 트리 체크, morphing 시작 |
| view | `DashReferenceFileWidget.cpp:616`·`636`·`783`·`868` | `getOrLoad` ×4 | part 노드 수 조회, best-match part 탐색 |
| view | `DashModelingTreeWidget.cpp:139`·`357`·`411` | `getOrLoad`, `get`, `activeContextChanged` | 트리 구축 + 활성 컨텍스트 동기화 |
| view | `DashModelRunnerWidget.cpp:1464`·`1973` | `getOrLoad` ×2 | 입력파일 검증, part 콤보 채우기 |
| view | `DashMorphingSettings.cpp:90`·`562`·`636` | `activeContext` ×2, `activeContextChanged` | node set 목록 갱신 |
| view | `DashOptimizerWidget.cpp:1528` | `activeActor`, `setActiveContext`, `activeContext` | `onPreviewButtonClicked` 결과 미리보기 |
| view | `DashConditionParameterizationWidget.cpp:222`·`313` | `activeContext`, `activeFilePath` | FE 조건 선택, 모델 세팅 |
| view | `DashGeometryParameterCADWidget.cpp:345` | `activeFilePath` | 모델 세팅 |

### 시그널 구독자

| 구독자 | 시그널 | 동작 |
|---|---|---|
| `DashMainWindow.cpp:432` | `activeActorUpdated` | `DashManager::Redraw()` |
| `DashMainWindow.cpp:433` | `activeContextChanged` | 로그 + Condition Parameterization 위젯 refresh |
| `DashModelingTreeWidget.cpp:139` | `activeContextChanged` | `onActiveContextChanged` |
| `DashMorphingSettings.cpp:90` | `activeContextChanged` | `loadNodeSetList()` |

### 미사용 include

| 파일 | 상태 |
|---|---|
| `controller/DashMorphingDoeExecutor.cpp:4` | Registry 미사용 (Context 는 사용) |
| `model/DashAnalysisLauncher.cpp:7-8` | Registry·Context 둘 다 미사용 |
| `view/DashGeometryParameterWidget.cpp:11-12` | Registry·Context 둘 다 미사용 |

기반 문서는 이 셋을 Registry include 줄만으로 센다. 실측하면 뒤의 둘은 Context include 도 호출부가 0이다.

### 레지스트리 자체의 성질 3건

- **캐시 무효화·제거 경로 부재.** `m_contexts` 에 `erase` 가 없다. 같은 경로를 morphing 으로 덮어써도 `getOrLoad` 는 캐시 히트를 반환해 낡은 컨텍스트를 쓴다. DOE 샘플처럼 경로가 매번 다르면 프로세스 수명 동안 무한 누적된다.
- **부분적 mutex 보호.** `m_contexts` 는 보호되지만 `m_activeFilePath`·`m_activeActor` 는 `setActiveContext`/`activeFilePath`/`activeActor` 어디서도 락을 잡지 않는다. 같은 뮤텍스로 감쌀 수 없다 — `activeContext()` 가 `get()` 을 부르고 그쪽이 이미 잠그므로 자기 잠금이 된다. 처분은 후속작업(마스터 D10).
- **`getOrLoad` 의 double-load 경합** (`.cpp:24-47`). 락 해제 구간에서 로드하므로 두 스레드가 같은 경로를 동시 요청하면 둘 다 로드하고 뒤늦은 `emplace` 가 실패한다. 이때 반환되는 `raw` 는 맵에 들어가지 못한 채 소멸한 객체를 가리킨다. 다만 세션 생성 경로가 GUI 스레드 단정(`DASH_ASSERT_MAIN_THREAD`)을 통과하므로 현행에서 실제로 재현되는지는 확인하지 않았다.

## 2. 프로젝트 열기가 레지스트리를 채우는가 — 없다

```
DashMainWindow::onFileOpen()                      view/DashMainWindow.cpp:3035
├─ PrjMgr()->CloseProject()                       레지스트리 접근 없음
├─ PrjMgr()->OpenProjectFromFolder(directory)     controller/DashProjectManager.cpp:97
│  ├─ findDprojFolder / SetProjectDirectory       경로 설정만
│  └─ GetProject()->restoreExistingModules()      model/DashProject.cpp:1213
│     └─ configs/*.json 파일명 파싱 -> 모듈 객체 new + addXxx()
│        (모듈 JSON 만 읽음 — variant 키, 부재 시 구조 키 폴백. .dat/.inp 는 열지 않음)
├─ m_fileSystemModel->setRootPath(directory)      파일 트리 루트만 지정
└─ m_projectWidget->setModel(getTreeModel())      모듈 트리 갱신
```

`restoreExistingModules` 는 파일명 접두사로 모듈 타입·set 이름을, 모듈 JSON 의 `variant` 키로 변형을 복원한다(`detectGeometryVariant` `DashProject.cpp:621` · `detectRunnerVariant` `:673` · `detectLauncherVariant` `:690`). `.dat`/`.inp` 를 여는 지점은 전혀 없다. `CloseProject`(`DashProjectManager.cpp:212-221`)도 레지스트리를 비우지 않아 프로젝트 A 를 닫고 B 를 열어도 A 의 컨텍스트와 활성 actor 가 남는다.

### 실제 적재 시점 — 전부 사용자 조작 이후

| 진입점 | 트리거 |
|---|---|
| `DashMainWindow.cpp:341` → `onProjectFileLoadClicked:2140` → `addFileToTreeWithStructure` → `loadDatFileAndChildren:357` | 파일 트리의 파일별 Load 버튼 |
| `DashConditionParameterizationWidget.cpp:375` / `DashGeometryParameterCADWidget.cpp:416` → `refreshFromLoadedAnalysis` | 위젯에서 해석 파일 지정 |
| `DashReferenceFileWidget`, `DashModelRunnerWidget` | reference file·part 조회 |
| `DashMorphingUtils`, `DashOptimizer`, `DashModelRunner`, `DashManager` | morphing 실행 |

### 일괄 적재 함수는 있으나 죽어 있다

`DashModelingTreeWidget::populate(const QString& path)`(`view/DashModelingTreeWidget.cpp:369`)은 디렉터리를 재귀 순회하며 `*.dat *.inp *.vtu *.vtk` 를 전부 트리에 넣고 `loadDatFileAndChildren` 를 탄다. 호출되면 프로젝트 전체 deck 을 레지스트리에 적재한다. 그런데 호출처가 헤더 선언(`:25`)과 정의뿐이다.

기반 문서 4.4 가 지목한 죽은 스캐너 `loadSetsFromConfigs()` 와는 다른 함수다. **죽은 스캐너가 둘이고 처분이 갈린다** — `loadSetsFromConfigs` 는 `restoreExistingModules` 와 기능이 겹치는 쌍둥이라 삭제하고(8절), `populate` 는 인자를 활성 기준모델로 바꿔 단계 3 에 쓴다.

### 트리가 둘이라 용어가 갈린다

| 트리 | 정체 | 프로젝트 재오픈 시 |
|---|---|---|
| Project Tree (좌측 dock) | `QFileSystemModel`. nameFilters 12종(`DashMainWindow.cpp:321-324`), 루트 = 프로젝트 폴더 | 자동 복원 — `setRootPath(directory)`(`:3070`) |
| Modeling Tree (`m_modelingTreeWidget`) | `QStandardItemModel`. 실제 로드된 모델의 part/component 구조 | **빈 채로 시작** |

Project Tree 는 지원 확장자 파일을 **나열**만 하고, 행마다 그려지는 Load 버튼(`ProjectFileTreeDelegate`)을 눌러야 적재가 돈다. Modeling Tree 를 채우는 호출은 그 경로(`:2262`)와 STEP 자식 추가(`:2324`·`:2350`), 그리고 커서 이동이다 — `onActiveContextChanged`(`DashModelingTreeWidget.cpp:481`)가 미등재 파일을 추가하므로 Optimizer 프리뷰 산출물 같은 비 Load 파일도 트리에 들어온다.

**따라서 빠진 것은 발견이 아니라 채택 기록이다.** 파일이 거기 있다는 것은 파일시스템이 이미 알려주고, 그중 무엇을 이 프로젝트의 입력모델로 삼았는지가 어디에도 남지 않는다.

## 3. `AnalysisModelIdentity.json` 실태 — 읽지만 읽은 값이 결과를 못 바꾼다

```
Registry::getOrLoad(path)
└─ DashAnalysisModelContext::loadAnalysisModelFromFile   controller/DashAnalysisModelContext.cpp:63
   └─ DashRwSession::open(filePath)                      1-arg, DASH_ASSERT_MAIN_THREAD
      └─ load() -> rwResolveContentIdentity()            controller/DashRwSession.cpp:1092
         └─ {configs}/AnalysisModelIdentity.json read-modify-write
```

```json
{ "models": { "<canonical absolute path>": { "uuid": "...", "sha256": "..." } } }
```

| 산출물 | 소비자 |
|---|---|
| 저장 `uuid` | 읽어서 세션 `contentUuid` 로 쓴다(`:1127-1130`·`:1389`). 그런데 키가 canonical 경로이고 신규 항목은 그 경로에서 파생한 값으로 채워지므로(`:1107-1110`·`:1134`) 저장값이 **항상** 경로 파생값과 같다. 파일을 지워도 결과가 동일하다 |
| 저장 `sha256` → `deckChanged` | 읽어서 파일 해시와 견주고(`:1131-1132`) 불일치 시 경고 로그 한 줄(`:1391-1393`). 값 자체는 `DashRwSession::referenceModelChangedOnDisk()`(`.h:141`) → `DashAnalysisModelContext::referenceModelChangedOnDisk()`(`.cpp:276`) 까지 노출되나 **호출처 0** |

| 성질 | 현재 동작 | 근거 |
|---|---|---|
| 읽기 | 저장 `uuid`·`sha256` 을 읽어 세션 uuid 와 `deckChanged` 를 채운다 | `:1119-1132` |
| 쓰기 시점 | deck 을 여는 **모든** 경로에서 무조건 | `:1137-1146` |
| 덮어쓰기 | uuid 는 기존 값 보존, sha256 만 갱신 | `:1129-1138` |
| 삭제 | 없음 (단조 증가) | `erase` 호출 없음 |
| 키 | canonical 절대경로 | `:1124` |
| 직렬화 | 전역 static mutex | `:1098-1099` |

저장소를 안 읽는 게 아니라 읽은 두 값이 결과를 못 바꾼다 — uuid 는 파생값과 늘 같고 `sha256` 불일치는 경고 로그에서 끝난다. uuid 보존 정책 자체는 올바르다. 무의미하게 만드는 것은 **키가 곧 산식의 입력이고, 키가 바뀔 때 옛 항목을 이어받지 않는다**는 점이다. 경로가 바뀌면 새 항목에 새 uuid 가 발급되고 옛 항목은 남은 채 잊힌다.

### 경로 규약이 셋으로 갈라져 있다

| 규약 | 쓰는 곳 |
|---|---|
| 프로젝트 루트 상대경로 | Reference File 목록(`DashReferenceFileWidget.cpp:438-497`, 해석은 `:140`·`:191`·`:705`), DV-Condition `source`(`DashConditionParameterizationPresentationModel.cpp:16-38`) |
| configs 복사 + bare filename | DV-Geometry(`DashGeometryParameterPresentationModel.cpp:72-82`), deck 재해석 4곳(`DashModelRunnerWidget.cpp:1444-1450`·`1460-1463`, `DashAnalysisLauncher.cpp:1612`·`1736`) |
| canonical 절대경로 | identity store |

`DashModelRunner.cpp:2049` 도 bare filename 을 해석하지만 대상이 deck 이 아니라 모듈 JSON(`GeometryParameter_*.json`)이라 원장 범위 밖이다.

**"configs" 도 두 곳이다.**

| 경로 | 쓰는 곳 |
|---|---|
| `{root}/configs` | `findAnalysisFiles` 의 `"configs/..."` 상대경로(`:466-474`) |
| `{root}/.{name}.dproj/configs` | `getConfigsDirectory()`(`DashIOController.cpp:113-120`) — 모듈 JSON, DV-Geometry dat 복사본 |

`{root}/configs` 는 리더만 있다. `getUserPath()`=`m_projectRootDir`, `getProjectPath()`=`m_internalConfigDir` 이고 `DashProject::m_projectPath` 도 `SetProjectDirectory`(`DashProjectManager.cpp:47`·`:51`)에서 `.dproj` 를 받으므로, 쓰는 쪽은 전부 숨김 configs 다. 비숨김 `{root}/configs` 에 쓰는 코드는 없다.

DV-Geometry 가 configs 로 복사한 deck 은 원본과 **다른 uuid 를 받는다** — uuid 가 canonical 경로 파생이므로 `{원본}/wing.dat` 와 `{configs}/wing.dat` 가 서로 다른 모델로 잡히고, 원본 기준으로 저장된 symbol uuid 바인딩이 복사본에 적용되지 않는다.

이 결함은 4절 구상으로 닫히지 않는다 — 상대경로로 바꿔도 두 경로는 여전히 다르다. **복사본을 없애야** 닫히므로 후속작업 3으로 둔다.

## 4. 구상 — 경로·uuid 정책

⚠ **구상 — 구현 전.** 기존 설계와 다르게 판단한 3건은 위 "기존 설계와의 관계" 표에 있다.

| # | 정책 | 근거 |
|---|---|---|
| P1 | 경로는 프로젝트 루트 상대경로만. 외부 파일은 프로젝트 안으로 복사 후 등록 | 기존 규약의 일반화 — reference file·DV-Condition 이 이미 상대경로, `.stli`·reference·DV-Geometry dat 이 이미 복사 방식 |
| P2 | content uuid 는 **최초 1회만** 발급(상대경로 파생)하고 이후 원장 값을 쓴다. 이 uuid 가 원장의 1차 키다(D24) — 경로와 식별자를 갈라 두는 것이 이관(후속작업 1)의 전제다 | 프로젝트 이동·`SaveProjectAs` 에 견딤. rename 내성은 이관 도입 후 |
| P3 (재개정) | 원장 대상을 `.dat`·`.inp` 로 한정한다 — **현행 유지.** `kind` 확장(`.prt` 형상 출처)은 마스터 D29 유보(후속작업 13 동반), `.wbpj`·`.stli` 확장은 이 문서 범위 밖 | RW 세션을 여는 확장자가 그 둘뿐이라(`DashRwSession.cpp:1363-1372`) content uuid 와 part 조회가 성립하는 범위와 일치한다 |
| P4 | 등록은 **Load 버튼 핸들러 한 곳**에서 `registerReferenceModel(relPath)` 을 명시적으로 부른다. `getOrLoad` 는 자격을 판정하지 않는 순수 캐시 조회로 남는다 | 마스터 방침 M3·M4 의 귀결. 등록 경로가 UI 동작 하나와 1:1 이라 우회가 없다 |
| P5 | 프로젝트 열기 시 **등록만**, 적재는 lazy 유지 | 해싱+파싱이 열기 시간에 실리는 것을 방지 |

P1 의 전제인 "외부 파일은 복사" 는 이미 관행이다 — `.stli` 는 부모 폴더째(`DashMainWindow.cpp:2088-2089`), reference 파일은 `copyReferenceFileToConfigs`, DV-Geometry 는 dat 을 configs 로(`DashGeometryParameterPresentationModel.cpp:75-76`).

외부 파일 진입점은 둘이고 P1 이 규율할 것은 하나다. `Add Files to Project`(`DashMainWindow.cpp:2080`)는 루트로 복사하므로 이미 P1 을 따른다. Direct Launcher 의 Input Cases(`DashAnalysisLauncherDirectWidget.cpp:218`)는 임의 절대경로를 받지만 복사·영속화·레지스트리 등재 없이 `runDirectJobs` 로 직행하므로 원장 밖이다 — 깨질 id 가 없어 P1 대상이 아니다.

P1 을 적용하면 숨김 폴더 내부 경로가 `".Car.dproj/configs/wing.dat"` 가 되어 프로젝트 이름이 경로에 박힌다. `SaveProjectAs` 가 `"." + m_projectName + ".dproj"` 로 이름을 유지하므로(`DashProjectManager.cpp:180`) 깨지지 않는다.

### 등록 지점 — 한 곳

**등록은 Load 버튼 핸들러가 한다.** `onProjectFileLoadClicked`(`DashMainWindow.cpp:2140`)가 `registerReferenceModel(relPath)` → `setReferenceModel(relPath)` → `setDisplayedContext(relPath)` 를 순서대로 부른다. 셋을 겸하고 멱등이다(마스터 결정 D4) — 이미 등재된 모델을 다시 Load 하면 등록은 no-op 이고 기준과 렌더만 이동한다.

**`getOrLoad` 는 자격을 판정하지 않는다.** 호출부 16곳 어디에도 인자를 더하지 않고 전부 순수 캐시 조회로 남는다. 좌표는 등록 자격이 아니라 **캐시 수명·무효화**(1절 "레지스트리 자체의 성질" 첫 항목)를 볼 때 쓴다.

**인자는 절대경로로 남는다.** `get`·`getOrLoad` 는 인자를 `canonicalFilePath()` 로 정규화해 캐시 키로 쓰고(`.cpp:16-48`), 상대경로를 절대경로로 푸는 자리는 `referenceContext()`·`setReferenceModel()` 안이다(마스터 결정 D9). 두 함수 위쪽만 상대경로 규약이고 캐시는 그대로다.

| 좌표 | 용도 |
|---|---|
| `DashAnalysisModelContextRegistry.cpp:51` | 커서 이동 내부. 분리 후 `setDisplayedContext` 전용이 된다 |
| `DashModelingTreeWidget.cpp:357` | 트리 part 행 구성. Load 버튼과 커서 이동 두 경로에서 도달하나 둘 다 등록과 무관하다 |
| `DashConditionParameterization.cpp:118` · `DashGeometryParameterCAD.cpp:106` | 모듈의 기준 deck 적재 |
| `DashReferenceFileWidget.cpp:617`·`637`·`784`·`869` | reference 행 part 조회 |
| `DashModelRunnerWidget.cpp:1464`·`1973` | 입력 검증 · part 콤보 |
| `DashManager.cpp:1028` · `DashOptimizer.cpp:1400` · `DashModelRunner.cpp:1975` | morphing 원본 조회 |
| `DashMorphingUtils.cpp:312`·`360`·`375` | 산출물·원본 조회 |

DV-Geometry(Morphing)는 자기 deck 을 지정하지 않고 전역 커서를 빌려 쓴다(`DashGeometryParameterPresentationModel.cpp:45`). [작업 1]이 그 자리를 `referenceFilePath()` 로 옮기고, [작업 3]이 Set 키로 내린다.

`get()`(5곳)은 그대로 둔다 — 미등재 파일에 `nullptr` 을 주는 것이 정확한 동작이다.

### 해제 지점 — 두지 않는다

마스터 결정 D5 다 — 트리 삭제는 화면 정리이고, 트리와 원장은 어느 쪽도 상대를 포함하지 않아 한쪽 삭제를 다른 쪽 해제로 쓸 수 없다. 근거·좌표는 마스터 "D5 의 근거" 절. 필요해지면 프로젝트 트리(Add File·Load 가 있는 곳)의 우클릭에 둔다.

### 스키마

원장 파일은 숨김 configs 의 `referenceModels.json` 이다. 코드가 deck 을 "reference model" 로 부르고(`DashRwSession.h:140`) 7절 API 와 낱말이 같다. AL 의 Input Reference File·`input_files` 는 `.stli`·`.wbpj` 를 포함하는 다른 집합이므로 이름을 공유하지 않는다.

```json
{
  "schemaVersion": 1,
  "activeModel": "a3f2c1e0-…",
  "models": {
    "a3f2c1e0-…": {
      "path": "models/wing.dat",
      "sha256": "9f86d0…",
      "size": 184320112,
      "mtimeMs": 1757400000000
    }
  }
}
```

| 필드 | 역할 | 없으면 |
|---|---|---|
| `activeModel` (최상위) | 전역 활성 기준모델(M2) — `models` 키(uuid) 중 하나 또는 빈 값(D22·D24). Load 핸들러 경유 `setReferenceModel` 이 갱신하고(D4) 열기 복원(단계 2)이 읽는다 | 재오픈 시 전역 기준모델이 빈 상태로 선다 — 과도기 동작 2가 상시화된다 |
| 키 = uuid | RW content uuid — 등록 시 상대경로 v5 파생 1회(P2), 이후 재계산 금지. 모듈 조인·스탬프·`activeModel` 이 이 방향으로 찾으므로 주 조회가 O(1) 이다. rename·이동 복구가 `path` 필드 1개 갱신으로 좁혀진다(D24) — 모듈 JSON 불변 | 원장이 지문 캐시로 퇴화하고 후속작업 1(rename 복구)이 불가능해진다 |
| `path` | 프로젝트 루트 상대경로. 파일 접근·표시·원장 유실 폴백용. P1 대로 외부 파일은 복사 후 등록하므로 절대경로 항목은 생기지 않는다. Load 등록의 멱등 판정은 이 필드를 훑는다 — 원장이 한 자리수라 선형 스캔으로 족하다 | 파일을 열 수 없다 — 항목이 성립하지 않는다 |
| `sha256` | 등록 시점 지문. 계산 후 **동결**한다 — 현재 해시는 언제든 얻으므로 저장할 값은 과거뿐이다 | 지금처럼 "직전 open 이후 변경" 만 재고 스스로 지운다 |
| `size`·`mtimeMs` | 등록 시점 stat. 적재 시 현재 stat 과 같으면 해싱을 건너뛴다 — `rwFileSha256` 의 프로세스 내 memo(`:1034-1051`)를 **프로세스 간으로** 확장하는 것 | 프로세스를 새로 띄울 때마다 적재 deck 전부 재해싱 |

**비교 시점은 deck 적재(RW 세션 open) 시다.** 프로젝트 열기는 P5 대로 원장 복원만 하고 stat 도 해싱도 하지 않는다.

`role` 같은 분류 필드를 두지 않는 것이 P4 의 귀결이다 — 원장에 들어오는 것이 이미 채택된 deck 뿐이라 구분할 대상이 없다.

**지문 불일치를 어떻게 처리할지는 별개 작업이다** — 여기서는 판정에 필요한 값을 남기는 데까지만 한다.

## 5. uuid 발급 — 파생 1회 + 경로·식별자 분리

차이는 산식도 조회 키도 아니라 **키가 바뀔 때 항목을 잇느냐**다.

| | 현재 | 이관 도입 후 |
|---|---|---|
| uuid 의 정의 | 경로의 함수 | 원장의 레코드 |
| 경로가 바뀌면 | 새 항목 + 새 uuid. 옛 항목은 잊힌다 | 항목을 새 키로 옮기고 uuid 를 이어받는다 |
| 원장의 지위 | 캐시 — 지워도 동작 동일 | 원장 — 지우면 rename 을 겪은 deck 의 식별자 상실 |

이관이 생기면 "저장된 uuid ≠ 지금 경로로 계산한 uuid" 인 상태가 처음으로 생기고, 저장값이 이긴다. 이 문서 범위(단계 1\~5)는 그 자리를 만드는 데까지다 — uuid 를 키로, `path` 를 필드로 두면(D24) 프로젝트 이동에는 견디고, rename 내성은 후속작업 1 이 얹는다(원장 `path` 필드 1개 갱신 — 모듈 JSON 불변).

```
resolveUuid(relPath)                          — 등록 시점 전용
├─ 1. 원장의 path 필드 스캔 -> 히트면 그 항목의 키(uuid) — 재Load 멱등 판정
└─ 2. 미스면 신규 발급: from_namespace(ns, relPath) 로 키 생성 + path 기록
      └─ 이 시점 이후 이 값은 다시 계산되지 않음
```

**주 조회는 uuid 직조회다**(D24) — 모듈·스탬프·`activeModel` 이 uuid 로 원장 항목을 O(1) 로 찾고 `path` 필드로 파일에 닿는다. path 방향 조회는 위 등록 멱등 판정과 원장 유실 폴백(D16)에서만 쓴다. 원장이 프로젝트당 한 자리수라 선형 스캔으로 족하고 별도 인덱스를 두지 않는다.

**원장에 없는 deck 도 RW 세션에 content uuid 를 넘겨야 한다** — morph 산출물·프리뷰처럼 등록 대상이 아닌 것들이다. 같은 산식으로 파생하되 원장에 쓰지 않는다. 산출물의 symbol uuid 는 영속화되지 않으므로 재계산돼도 무방하다.

### 왜 난수가 아니라 파생인가

난수여도 되지만, 파생이면 원장이 유실되거나 같은 경로로 재등록해도 같은 값이 나온다. 기존 설계의 v5 발급과 같고 네임스페이스 입력만 절대경로 → 상대경로다.

### 생명주기

칸은 그 사건에서 원장에 **다시 쓰는** 값이다. `—` 는 쓰지 않음.

| 사건 | 키 (uuid) · `path` 필드 | `uuid` 발급 | `sha256` |
|---|---|---|---|
| 최초 등록 | 삽입 | **발급** | 기록 |
| 같은 파일 재로드 | — | — | — |
| deck 내용 편집·덮어쓰기 | — | — | — (현재 해시와 어긋남) |
| 앱 안에서 rename·이동 | — | — | — (기능 없음. 파일을 옮기는 코드는 `renameSet` `DashProject.cpp:1430` 의 모듈 JSON 뿐) |
| 앱 밖에서 rename | — (항목이 끊어진다. 다시 등록해야 한다) | — | — |
| 프로젝트 폴더 복사·이동 | — (상대경로라 불변) | — | — |

**항목이 지워지는 사건은 없다** — D5 대로 해제 지점을 두지 않으므로 원장은 단조 증가한다. 3절이 지적한 `AnalysisModelIdentity.json` 의 무한 증식과는 다르다 — 그쪽은 deck 을 여는 **모든** 경로에서 기록해 morph 산출물·프리뷰까지 쌓였고, 원장은 Load 버튼 클릭 수만큼만 는다. 해제 UI 가 생기면 그 핸들러가 항목을 지우는 행이 이 표에 붙는다.

`uuid` 이관은 이 표의 어느 행에서도 아직 일어나지 않는다. 후속작업 1 이 앱 밖 rename 을 sha256 으로 추적해 이관을 도입한다.

### 대가

원장 파일이 **유실되면 안 되는 자산**이 된다. 지금 `AnalysisModelIdentity.json` 은 지워도 아무 일이 없지만, 구상 구조에서는 지우면 rename 을 겪은 deck 의 식별자가 끊긴다. 숨김 폴더 안 `configs/` 에 두면 `SaveProjectAs` 의 전체 복사(`DashProjectManager.cpp:184-204`)에 따라간다.

앱 밖 rename 도 같은 값을 치른다. 원장이 옛 경로를 가리켜 항목이 끊어지고, 다시 등록하면 새 상대경로로 **새 uuid 가 발급되어** 그 deck 에 매달린 DV-Condition 바인딩이 무효가 된다. sha256 으로 옮겨간 파일을 찾아 항목을 새 키로 이관하는 복구는 후속작업 1 과 같은 자리다.

### 코드에서 바뀌는 지점

uuid 가 모듈로 흘러가는 경로는 한 줄기다.

```
contentUuid
└─ ContentInfo{ path, fileName, contentUuid }        DashRwSession.cpp:1396-1400
   ├─ client.loadContent(info)
   └─ client.getSymbolTree(contentUuid)              :1408
      └─ 여기서 나오는 모든 symbol uuid 가 contentUuid 에서 파생
         └─ DV-Condition 의 "uuid" 로 영속화          DashConditionParameterizationPresentationModel.cpp:84
```

content uuid 는 모듈이 **돌려주는 값이 아니라 받는 값**이다. 발급처 이전이 시그니처 하나로 끝나는 근거가 이것이다.

```
현재:  DashRwSession::open(filePath, identityStoreDir)
       └─ 내부에서 rwResolveContentIdentity() 가 store 를 읽고 uuid 를 정함

구상:  DashRwSession::open(filePath, contentUuid)
       └─ rwResolveContentIdentity() 삭제. 호출자가 uuid 를 정해서 넘김
```

`rwResolveContentIdentity`(`:1092-1148`)·`rwIdentityStorePath`(`:1070`)·`rwConfigsDirFromProject`(`:1080`)가 함께 사라지고, `rwFileSha256`(`:1032`)은 호출자 쪽으로 옮겨 지문 계산에 계속 쓴다. `DashRwSession::open` 의 2-인자 오버로드는 1-인자 오버로드의 위임(`:1155`) 외 직접 호출처가 0이다.

## 6. Input Reference File — deck 부터, 나머지는 추후

`.dat`/`.inp` reference file 은 이미 레지스트리를 거친다 — `getPartNodeCount`(`:617`) · `findBestMatchingPart`(`:637`) · `updateRowTargetPart`(`:784`·`:869`). **같은 객체를 두 체계가 각자 관리하는 상태**이므로 여기부터 통합한다.

섹션이 있는 곳은 Init DOE(`DashAnalysisLauncherWidget.ui:415`)와 Resample DOE(`...ResampleWidget.ui:535`, `#ifdef DASH_BUILD_DEV`)뿐이고 Direct Launch 에는 없다.

Name 열 콤보의 `.dat`·`.inp` 후보를 원장 조회로 바꾼다. 지금은 `findAnalysisFiles()` 폴더 스캔이라 출처를 가리지 않는다. 등재는 Load 버튼에서 이미 끝나므로 이 자리는 읽기만 한다 — `getOrLoad` 4곳은 part 조회용 그대로 남는다.

원장 밖인 `.stli`·`.wbpj`·`.cdb`·`.dfsxml` 은 후속작업 2 까지 스캔을 유지한다. **콤보 후보는 그때까지 원장·스캔 두 소스를 합친 것이 된다.**

| 확장자 | 성격 | 원장 |
|---|---|---|
| `.dat`, `.inp` | 해석 deck. RW 세션이 열린다 | 1차 대상 |
| `.stli` | FE-safe 템플릿. 실체가 부모 폴더다 — `project_root`(`DashJobRunner.cpp:1315`), 복사도 폴더째(`DashMainWindow.cpp:2107`) | 추후 — 지문을 폴더에 어떻게 매길지 미설계 |
| `.prt` | CAD 형상 출처 | 유보 — 마스터 D29\~D31(후속작업 13 동반) |
| `.wbpj`, `.dfsxml`, `.cdb` | 솔버 프로젝트·입력 파일 | 추후 — `.wbpj` 는 사장 경로 소속([Project-Manifest-CAD-Path-Disposition](Project-Manifest-CAD-Path-Disposition.md)) |

함께 손볼 것 하나 — `findAnalysisFiles` 는 **파일명 기준**으로 중복을 제거한다(`:456-460`·`:469-473`·`:488-492`). 다른 폴더의 동명 파일이 조용히 사라진다. `.dat`·`.inp` 는 원장 조회로 빠지므로 남는 확장자에만 걸리지만, 상대경로를 1차 키로 삼는 이상 이 dedup 은 제거해야 한다.

## 7. 단계 — [작업 2]

번호는 [Project-Manifest-0-Work-Order](Project-Manifest-0-Work-Order.md) 의 [작업 2]-1\~5 와 같다.

**선행 조건** — `setActiveContext` 가 내부에서 `getOrLoad` 를 부르고(`DashAnalysisModelContextRegistry.cpp:51`) `DashOptimizerWidget:1528` 이 방금 생성한 출력 파일을 active 로 세팅하므로, 커서를 가르지 않은 채로는 렌더 이동이 등록을 유발한다. [작업 1]이 그 경로를 막은 뒤에 원장을 올린다.

[작업 1]이 커서 값을 **프로젝트 루트 상대경로**로 들고(D3) 절대경로 해석을 Registry 안에서 끝내므로(D9), 이 절에 경로 변환이 없다 — 원장 `path` 필드와 `referenceFilePath()` 반환값이 같은 문자열이다. reference 커서의 내부 표현은 단계 2의 구현 교체와 함께 uuid 로 전환된다(D12 개정 · D24).

| 단계 | 범위 | 검증 |
|---|---|---|
| 1 | 원장 클래스 + `referenceModels.json` + `DashProject` API 2개(`registerReferenceModel` · `referenceModelPath`). 등록 호출은 Load 버튼 핸들러 한 곳이고 멱등이다. `getOrLoad` 시그니처는 손대지 않는다 | Load 시 항목 생성, 같은 파일 재Load 시 중복 없음 |
| 2 | `referenceFilePath()` 구현을 Registry 멤버에서 원장 `activeModel`(uuid — D22·D24) 조회로 교체하고 `setReferenceModel` 이 그 키를 갱신 + 열기 시 복원 — Load 버튼 활성 표시(D7) 동기화 포함. 호출부는 불변(마스터 결정 D2) — 접근자가 uuid 를 원장 `path` 로 풀어 돌려준다 | 재오픈 후에도 전역 기준모델이 유지됨 |
| 3 | `Registry::clear` + `CloseProject` 연결 + Modeling Tree 재구성 — `populate` 의 인자를 디렉터리에서 활성 기준모델 1건으로 바꿔 되살린다(`addFileToTreeWithStructure` 는 그대로). 원장 전량을 넘기지 않는 것은 D5 로 해제 지점이 없어 원장이 단조 증가하기 때문이다 — 한 번이라도 Load 한 deck 을 재오픈마다 전부 파싱하게 된다. 트리는 저장본 복원이 아니라 **재파싱**이다. 죽은 스캐너 `loadSetsFromConfigs`(`DashProject.cpp:1066`)를 함께 삭제한다 | 재오픈 시 활성 기준모델의 트리가 다시 뜸. 프로젝트 A 를 닫고 B 를 열면 A 컨텍스트가 남지 않음 |
| 4 | 원장 키를 uuid 로(D24) — 경로는 `path` 필드로 프로젝트 루트 상대 통일(P1) + content uuid 영속(P2) | 프로젝트 폴더를 옮겨도 원장 항목이 유효 |
| 5 | `id` 를 content uuid 로 넘기도록 `DashRwSession::open` 시그니처 변경 + `rwResolveContentIdentity` 삭제. 딸려 나오는 정리 — `rwIdentityStorePath`·`rwConfigsDirFromProject` 는 호출부가 0이 되고, `rwFileSha256` 는 호출자 쪽으로 옮긴다. `AnalysisModelIdentity.json` 폐기 | 기존 프로젝트의 DV-Condition 체크 상태 유지 |

**해제 API 는 만들지 않는다** — D5. API 가 둘인 이유가 이것이다.

**단계 5 는 4 를 전제로 하되 1\~4 와 같은 커밋일 필요가 없다.**

Reference File 콤보와 DV `source` 정규화는 [작업 3]-4 소유다. 그 이득이 가장 잘 보이는 자리는 `DashAnalysisLauncher.cpp:1742-1748` 이다 — 파일명 하나로 경로 후보 넷을 순서대로 시도하는 코드가 조회 하나로 바뀐다.

**마이그레이션 코드는 필요 없다.** DV-Condition 항목은 조건 이름으로 키가 잡혀 있고 uuid 는 항목 안의 위치 지정 필드다 — content uuid 산식이 바뀌면 그 필드만 어긋나고 값이 딸린 항목은 이름으로 그대로 찾힌다. 로더는 어긋난 uuid 를 이름으로 대신 붙이고(`DashConditionParameterization.cpp:495-497`) 다음 저장 때 `syncDvFromCheckedFeConditions` 가 새 uuid 를 backfill 한다(`:444-447`). DOE 샘플로 중계된 uuid(`DashMorphingDoeExecutor.cpp:528`)도 소비 측에 같은 폴백이 있고(`:451-453`) 실행마다 재생성된다.

**reader-writer DLL 은 손대지 않는다.** `ContentInfo::uuid`(`IRWModule.hpp:106-115`)는 `dash::core::UUID` 타입이고, 주석이 "하위 심볼 UUID 의 결정적 네임스페이스 루트 — 호출자가 덱 파일당 안정적으로 유지·제공할 책임" 이라고 계약을 못박는다. 원장이 그 책임을 지는 자리다. 상대경로를 그 자리에 넣을 수 없고 symbol uuid 도 모듈이 돌려주는 값이라, 바뀌는 것은 SDK 경계 바깥뿐이다.

## 8. 함께 정리되는 결함

| 결함 | 해소 자리 |
|---|---|
| 재오픈 시 Modeling Tree 가 빔 | 단계 3 |
| `CloseProject` 가 레지스트리를 안 비움 — 프로젝트 A 컨텍스트가 B 에 잔존 | 단계 3 |
| 절대경로 키 — 프로젝트 이동 시 전 항목 무효 | 단계 4\~5 (`AnalysisModelIdentity.json` 폐기 시점) |
| identity store 무한 증식 | 단계 5 (P4 로 원장에는 애초에 기록 안 함) |
| `referenceModelChangedOnDisk()` 사문화 | 단계 5 + 후속작업 1 |
| bare filename 재해석 중복 4곳 | [작업 3]-4 |
| Reference File 콤보가 출처를 안 가림 — 미채택 파일·산출물이 후보로 뜸 | [작업 3]-4 |
| `findAnalysisFiles` 의 파일명 기준 dedup | [작업 3]-4 |
| 모델링 트리 체크박스가 모듈의 기준 deck 을 바꿈 | [작업 1] — [Project-Manifest-2-Active-Cursor-Data-Coupling](Project-Manifest-2-Active-Cursor-Data-Coupling.md) |

범위 밖이나 같은 파일에 있는 것 — `getOrLoad` double-load 경합(`.cpp:24-47`) · `m_activeFilePath`·`m_activeActor` 의 mutex 밖 접근(`:50-75`) · 죽은 include 3건 · `loadSetsFromConfigs()`(`DashProject.cpp:1066`) 삭제. 마지막 것은 `restoreExistingModules()`(`:1213`)와 스캔 대상·복원 방식·variant 판정이 모두 같은 쌍둥이이고, live 쪽만 접두사 맵으로 `_` 가 든 set 이름을 처리한다(`:1250`).

## 9. 후속 작업

미결은 없다. 아래는 이 문서 범위 밖으로 미룬 것이다.

| #   | 항목                                                                                                                                              |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| 0   | Registry 의 스레드 안전 — 커서 멤버 보호(마스터 D10)와 `m_contexts` double-load 경합(`.cpp:24-47`)을 한 자리에서. 캐시 무효화 경로 부재도 같은 자리다 |
| 1   | 지문 불일치 처리 — Stale 배지 · 착수 차단 · 바인딩 재검증 중 무엇을 얹을지. sha256 은 값 편집과 구조 편집을 구별하지 못한다(`DashRwSession.cpp:1025-1027`). 앱 밖 rename 복구도 같은 자리다(5절 "대가"). **D11 의 uuid 폴백이 값을 갖는 시점이 여기다** |
| 2   | 형태 확장 — `.stli` 는 지문을 폴더에 어떻게 매길지. `.prt` 는 마스터 D29\~D31 유보와 한 묶음("파일 둘이 한 항목" 스케치는 폐기), `.wbpj` 는 사장 경로 소속이라 보류 — 근거는 [Project-Manifest-CAD-Path-Disposition](Project-Manifest-CAD-Path-Disposition.md)                                                                           |
| 3   | 정본 일원화 — 프로젝트 루트의 `.dat`·`.inp` 를 정본으로 두고 configs 복사본을 없앤다. 복사는 bare filename 을 해소할 자리가 configs 뿐이라 생긴 것이고, 참조가 상대경로로 통일되면 이유가 사라진다          |
| 4   | 모듈 JSON 의 deck 참조를 전부 프로젝트 상대경로로 통일. 단계 1\~3 만 끝나면 착수 가능하고, [작업 3]-4 가 아래 넷 중 둘을 먼저 처리한다                                                                |

3번의 복사처는 둘이고 난이도가 다르다.

| 복사처                                                                                                           | 시점                             | 제거                                                                    |
| ------------------------------------------------------------------------------------------------------------- | ------------------------------ | --------------------------------------------------------------------- |
| DV-Geometry(`DashGeometryParameterPresentationModel.cpp:75-76`)                                               | DV 저장 시 active deck 1개         | `Morphing\|<bare filename>` 을 상대경로로 올리면 불필요해진다. 재해석 4곳이 함께 바뀐다     |
| AL `copyReferenceFileToConfigs`(`DashAnalysisLauncher.cpp:1410`, 호출 `DashAnalysisLauncherWidgetBase.cpp:209`) | DOE 실행 직전 등록 reference file 전량 | 실행 스테이징이라 job runner 의 입력 경로 규약을 함께 봐야 한다. 확장자도 `.dat`·`.inp` 밖까지 걸친다 |

4번의 전환 단위는 **쓰는 곳 넷**이다. 읽는 곳은 여러 파일에 흩어져 있으나 형식이 이 넷으로 닫힌다.

| 영속 형식                                           | 쓰는 곳                                                    | 대상                        | 전환                     |
| ----------------------------------------------- | ------------------------------------------------------- | ------------------------- | ---------------------- |
| DV `source` = `Morphing\|<datFileName>\|<part>` | `DashGeometryParameterPresentationModel.cpp:107`        | deck (bare filename)      | [작업 3]-4               |
| `input_files[].path` = 상대경로                     | `DashReferenceFileWidget.cpp:1126`                      | deck + `.stli`·`.wbpj` 혼재 | [작업 3]-4 (deck 분만)     |
| DV `source` = 상대경로                              | `DashConditionParameterizationPresentationModel.cpp:72` | deck                      | 이미 부합 — 검증만       |
| DV `source` = `CAD\|<prtFileName>`              | `DashGeometryParameterCADPresentationModel.cpp:28`      | `.prt`                    | 불개입 — 사장 경로 소속(마스터 D32 철회) |

소비자 값이 원장 키와 같아지므로 역조회도 uuid 마이그레이션도 없다. bare filename 만 상대경로로 올리면 되고, 그 값으로 `QDir(root).filePath()` 가 바로 성립해 `DashAnalysisLauncher.cpp:1742-1748` 의 경로 후보 4개 추측이 사라진다.

대가 — 앱에 deck rename 기능이 생기면 그 핸들러가 원장과 모듈 JSON 을 함께 갱신해야 한다. 지금은 그 기능이 없다.

## 10. 검증 한계

| 항목 | 근거 강도 | 비고 |
|---|---|---|
| 소비자 34지점 · 시그널 4 · 죽은 include 3 | **강** | `dev` @ `c989257` 전수 grep. 단위는 `Instance()` 호출 지점이고 API 호출 수와 다르다 |
| 좌표 재실측 (2026-09-14) | **강** | `5caf8b0..c989257` 변경 175파일. 전 인용 좌표를 diff 라인 매핑으로 재계산했고, 커서 API·핵심 심볼(getOrLoad·rwResolveContentIdentity·populate 등)을 담은 라인의 추가·삭제가 0이라 집계(34지점·시그널 4·죽은 include 3·getOrLoad 16 등)는 불변이다. 이동의 주원인은 로깅 마이그레이션(qDebug→DASH_LOG) |
| 열기 경로가 레지스트리를 안 건드림 | **강** | `onFileOpen` → `OpenProjectFromFolder` → `restoreExistingModules` 본문 확인 |
| identity store 읽기 무효 판정 | **강** | 저장 uuid = 경로 파생값이라 읽어도 같은 값(`:1107-1134`), `sha256` 불일치는 경고 로그 1줄(`:1391-1393`)에서 끝나고 `referenceModelChangedOnDisk()` 호출부 0 |
| `populate()` 호출부 0 | **강** | 선언·정의 2곳뿐 |
| 경로 규약 3종 · configs 이중성 | **강** | 라이터·리더 좌표 확인. `{root}/configs` 는 리더만 존재 |
| `getOrLoad` 호출부 16곳 | **강** | 전수 — 외부 15 + 레지스트리 내부 자기호출 1(`.cpp:51`). 인자가 전부 프로젝트 내부 경로임을 호출자별 확인. 1절의 34지점 집계는 `Instance()` 단위라 `:51` 을 세지 않는다 |
| `get`·`getOrLoad` 가 인자를 canonical 절대경로로 정규화 | **강** | `.cpp:16-48` 본문. `m_contexts` 키가 canonical 절대경로다 |
| 트리 삭제가 등록 해제가 아님 | **강** | `deleteSelectedItem`(`DashModelingTreeWidget.cpp:506-528`)과 핸들러(`DashMainWindow.cpp:411-428`) 본문 확인. 레지스트리 접근 0 |
| SDK 의 content uuid 계약 | **강** | `IRWModule.hpp:106-115` — 타입 `dash::core::UUID`, "호출자가 덱 파일당 안정적으로 유지·제공할 책임" |
| 앱 내 deck rename 부재 | **강** | 파일을 옮기는 코드 3곳 전수(`DashProject.cpp:1430` 모듈 JSON, `DashModelBuilderMCU.cpp:364`·`371` 헤더 스왑) |
| deck 참조 영속 형식 4개 | **강** | `"source"` 53건 · `"path"` 12건 · `"input_files"` 18건에서 쓰는 곳과 읽는 곳을 갈라 확인 |
| 마이그레이션 불요 (7절) | **강** | `"uuid"` JSON 키 사용처가 4파일뿐 — DV-Condition·DOE 계열 3 + 폐기 대상 identity store(`DashRwSession.cpp`). 로더 폴백(`DashConditionParameterization.cpp:495-497`) · backfill(`DashConditionParameterizationWidget.cpp:548`) · DOE 폴백(`DashMorphingDoeExecutor.cpp:451-453`) 본문 확인 |
| `getOrLoad` double-load 경합 | **중** | 코드 구조상 성립. 실제 재현은 미확인 — 세션 생성이 GUI 스레드 단정을 통과한다 |
| 5단계 계획과 검증 항목 | **중** | 제안이다. 각 확인이 현행 UI 로 수행 가능한지는 재현하지 않았다 |
| 기존 설계와의 갈림 3건 | **중** | 기존 문서 해당 절 본문 대조. 어느 쪽이 맞는지는 판정하지 않았다 |
| 빌드·실행 | **없음** | 정적 근거만 |
