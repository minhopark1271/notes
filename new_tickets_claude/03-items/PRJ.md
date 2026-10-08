# PRJ 작업 목록

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> 기준: dev @ b08a91b3. 원자 항목은 02-claims/PRJ.md. 열린 PR 7건 중 머지 대상 6건 — #651 #652 #654 #655 #656 #658 (#530 은 재업로드 노선이라 제외, decisions ②⑩). PRJ 겹침 — #654(controller/DashManager.cpp · view/DashMainWindow.cpp) · #652(controller/DashManager.* · view/DashMainWindow.* · model/DashProject.cpp · view/DashDoeSamplerDirectWidget.*) · #651(model/DashProject.* · view/DashMainWindow.cpp · view/DashModelingTreeWidget.cpp) · #655(view/DashMainWindow.cpp — 1파일·20항목) · #656·#658(model/DashAnalysisLauncher.cpp·.h — PRJ-03·09·22). 충돌란은 D-1 의 `build_deps.py --apply` 가 자동 기입한다.
> **선행이어야 할 PRJ 항목은 6건 어디에도 없다** — #655 의 MainWindow hunk 3개는 모두 모핑 핸들 배선이다. #656 의 hunk 는 `loadResultKeys`·`previewNaturalFrequency`·`requestVtkGeometry`, #658 은 `requestVtkPreview`·`previewNaturalFrequency` 인데, PRJ-03·09 가 치환할 `DashProjectManager::Instance()` 5곳은 `ioController`(:91)·`processResults`(:862·:972)·`loadParameterInfo`(:1478)·`refreshLaunchTarget`(:1514) 로 전부 다른 함수다(행 드리프트만 생긴다). #656 의 `.h` hunk 는 진입점 설명 주석뿐이라 PRJ-22 가 옮길 `upstreamStaleReasons()` 선언을 건드리지 않는다.
> Phase B: #444 담당 PRJ → LCH. 이관 흡수 — CON-c19 → PRJ-21 · PER-c20 → PRJ-16/17/18 · CAD-c20 → PRJ-26 · 신규 PRJ-31(PER-c30 직쓰기) · PRJ-32(BLD-c01 variant 3벌). B2: DOE-01 → PRJ-33(이관) · DOE-04 → PRJ-24(병합) · UIC-04 → PRJ-14(병합). `DashMainWindow` 레이아웃·프레임 함수군은 UIC 소유 — PRJ-03·04·11·14 충돌에 UIC 항목 명시.
> C' 반영 (2026-10-06, 04-review/PRJ.md + 05-final/decisions.md): 신규 **PRJ-34**(DEC — Set 모델 공통 베이스, ⑧) · **PRJ-35**(Save As 가 Set·트리를 전멸시킨다, 검토 2) · **PRJ-36**(#394 자기 덮어쓰기 소실, ⑨). **PRJ-20 은 CLOSE** — #645-1 집행은 CON-03 (⑦). 제거 — 충돌란의 `#530`·`pipeline-deck-stamp` (②, #530 은 머지하지 않는다). PRJ-31 의 "DashJsonFile" → "DashSaveSystem 헬퍼" (③). `.wbpj`·`.stli` 원장 편입은 LCH-29(DEC) 결과 대기 — PRJ 는 소비자(①): 사장 확정이면 PRJ 신규 항목 0, 현행 유지면 원장 편입 항목 1건이 새로 필요하다.
> 보류: CON 몫 — CON-03 의 목표를 "`addReferenceFile` 재로드 성공 뒤 핀 deck 일치 시 `refreshFromFile`" 로 교정하고 "진입점 노출" 문구 삭제(이미 public), CON-03·04·06·07 충돌란의 `PRJ-20` 제거(CLOSE 됨), CON-05 에 `선행: PRJ-08`(역순 허용) 기재. 보류: LCH 몫 — LCH-29 의 선행·영향 목록에 PRJ 추가와 결정문의 "사장 → `.wbpj`·`.stli` 원장 비편입(PRJ 무작업) / 현행 유지 → PRJ 원장 편입 항목 신설" 조항.
> C' 2차 반영 (2026-10-06, 05-final/deferred.md `→ PRJ` 8행): BLD 몫 `checks[]` 쌍 1건을 PRJ-22 비고에 흡수로 기재. RUN 몫(`m_categoryWidgetMap` → PRJ-c69 · PRJ-19) · PER 몫(PRJ-31 의 "DashJsonFile" → `DashSaveSystem` 헬퍼) · LCH 몫(LCH-29 소비자 등록 — PRJ-21 비고 · 대응표)은 1차 C' 에서 이미 반영. 항목 수 변화 0.

## Set 수명 · 프로젝트 전환

### PRJ-01 · 프로젝트 전환 전에 모듈 위젯 전부를 setModel(nullptr) 로 해제한다
- 종류: PR | 규모: S | 태그: A, E · bug
- 목표: `onFileOpen`·`onFileNew` 가 `OpenProjectFromFolder`/`CreateNewProject` 를 부르기 전에 모든 모듈 위젯의 모델을 끊는다 — `unbindSetWidgets` 의 카테고리 분기를 Set 무관 전체 해제 함수로 묶어 호출. `clearAllSets` 가 모델을 지운 뒤 위젯이 옛 포인터로 disconnect 하는 UAF 7곳이 사라진다
- 완료 기준: (1) 프로젝트 A → B 전환 후 모든 카테고리 Set 클릭에 크래시·ASan 보고 0 (2) `DashProjectManager::SetProjectDirectory` 호출 전 모든 위젯 `m_model == nullptr` — 소멸 지점이 `SetProjectDirectory → SetProjectPath(new) → clearAllSets` 하나이고 Save As 도 같은 함수를 타므로, 해제 함수가 그 앞을 지킨다 (3) #549 가 QPointer 로 막은 Model Runner 2곳도 같은 경로를 탄다
- 변경 범위: view/DashMainWindow.cpp, view/DashMainWindow.h
- 선행: -
- 충돌: PRJ-03 · PRJ-04 · PRJ-25 · PRJ-35 (같은 파일 · 같은 해제 함수를 Save As 경로에서 재사용) · PR #654 #652 #651 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashMainWindow.h → 공유 11건(deps.md 5절) · PR #655(DashMainWindow.cpp)
- 흡수: #551 · PRJ-c12 · PRJ-c13 · PRJ-c14 · PRJ-c15 · PRJ-c16 · PRJ-c17 · PRJ-c18
- 비고: 위젯별 `QPointer` 방어(#551 to-be)는 각 모듈 선택 — 계약(PRJ-02)이 서면 불필요. c19(delegate) 는 CON, c20 은 해소됨. c12 가 적었던 `CloseProject → SetProjectPath("")` 사슬은 성립하지 않는다(빈 경로 조기 반환) — 교정 근거는 c12

### PRJ-02 · 위젯 모델 교체·Set 전환·프로젝트 전환 정리 규칙을 문서로 정하고 리뷰 항목에 넣는다
- 종류: DEC | 규모: S | 태그: E, A · docs
- 목표: "어디서 끊고(wholesale disconnect + 모델이 sender 가 아닌 연결), 무엇을 비우고(표·콤보·pending 상태), 언제 초기화하는지(Set 삭제·전환·프로젝트 전환)" 를 docs/ 한 장으로 고정하고 PR 체크리스트 항목으로 둔다
- 완료 기준: 결정 기록 — docs/widget-lifecycle.md(가칭) + 리뷰 체크 문구. 사례로 c12-c18 · OPT-D2 · RUN-D36 · PRE-D1 을 인용
- 변경 범위: docs/ (신규 1), .github 템플릿이 있으면 그것
- 선행: -
- 충돌: -
- 흡수: #431 · PRJ-c21
- 비고: #407 전수조사 결과를 실측 근거로 편입. 코드 수정은 각 모듈 항목

### PRJ-16 · Set 삭제가 산출물 폴더를 함께 지우고 삭제 전에 확인한다
- 종류: PR | 규모: S | 태그: A, C · bug
- 목표: `deleteSet` 이 json 과 함께 `{Module}_{Set}` 폴더를 지운다. MainWindow 삭제 경로가 폴더 경로·내용 유무를 보여 주는 확인 다이얼로그를 거친다 (참조 자산 삭제와 같은 문형). 실행 중이면 거부 — 판정은 공용 질의(가칭 `isBusy()`)로 두고 Builder·Runner·Optimizer 는 `m_currentJob` 으로 구현, `DashModelBuilderMCU` 는 그 상태가 없어 새로 둔다
- 완료 기준: (1) 삭제 후 `getModuleDir` 경로 부재 (2) 삭제 취소 시 json·폴더 불변 (3) 동명 재생성 후 옛 산출물이 보이지 않음 (4) rename 가능 4종 전부(**MCU Builder 포함**)가 실행 중 삭제를 거부
- 변경 범위: model/DashProject.cpp, view/DashMainWindow.cpp
- 선행: -
- 충돌: PRJ-17 · PRJ-18 · PRJ-19 · PRJ-31 · PRJ-32 (DashProject.cpp) · PR #652 #651 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp)
- 흡수: #443 SI-6a ③a · PRJ-c05 · Set-Identity SI-6a(PER 이관 — 삭제 동반) · PER-c20 · PRJ-c61
- 비고: SI-6a 가 "둘 다" 로 확정한 두 규칙 중 하나. 다른 하나는 PRJ-17. `DashModelBuilderMCU` 에는 `m_currentJob`·`isRunning` 이 없고 ProcessJob 이 `runTraining` 지역 변수라(c03) 공용 질의를 그 클래스에 신설하는 몫이 PRJ-16·18 에 함께 든다 — 접점 BLD

### PRJ-17 · Set 생성 시 동명 산출물 폴더가 있으면 거부하고 안내한다
- 종류: PR | 규모: S | 태그: A, C · bug
- 목표: `createNewSet` 이 `hasSetNamed` 에 더해 `getModuleDir(type, name)` 존재를 검사해 거부하고, `onNewSetRequested` 가 "외부 복사·구 프로젝트 고아 폴더" 안내를 띄운다
- 완료 기준: (1) 고아 폴더가 있는 이름으로 Add Set → 생성 0 + 안내 (2) 폴더 제거 후 같은 이름 생성 성공
- 변경 범위: model/DashProject.cpp, view/DashMainWindow.cpp
- 선행: -
- 충돌: PRJ-16 · PRJ-18 · PRJ-19 · PRJ-31 · PRJ-32 · PR #652 #651 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp)
- 흡수: #443 SI-6a ③b · PRJ-c06 · PER-c20 · PRJ-c61 (동명 폴더 거부)

> #562·PR #681의 현행 수정 범위 재확인은 추가 개정 계획이다. 아래 코드 실측은 작성 당시 기록이며 #368·#685를 #681 머지 조건으로 적용하지 않는다.

### PRJ-18 · Set rename 이 산출물 폴더를 함께 개명하고 실패 시 롤백한다
- 종류: PR | 규모: M | 태그: A, C · bug
- 목표: `renameSet` 이 json rename 과 `QDir::rename` 을 한 단위로 — 폴더 개명 실패 시 json 을 되돌리고 false. 모델이 실행 중이면 거부 — 판정은 PRJ-16 과 같은 공용 질의(`isBusy()`)이고 `DashModelBuilderMCU` 는 그 상태를 새로 둔다. 대상은 rename 가능한 ModelBuilder·MCU·ModelRunner·Optimizer
- 완료 기준: (1) rename 후 옛 폴더 0·새 폴더에 기존 run 결과 (2) 폴더 잠금 상태에서 rename → json 이름 불변 + 경고 (3) 실행 중 rename → 트리 텍스트 원복, rename 가능 4종 전부(**MCU Builder 포함**)
- 변경 범위: model/DashProject.cpp, model/DashProject.h, view/DashMainWindow.cpp
- 선행: PRJ-19 (죽은 분기 제거 후 손대는 편이 작다 — 선택)
- 충돌: PRJ-16 · PRJ-17 · PRJ-19 · PRJ-31 · PRJ-32 · PR #652 #651 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · DashProject.h → PRJ-08 PRJ-11 PRJ-22 PRJ-33 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp)
- 흡수: #562-1 · #443 SI-6a ① · PRJ-c03 · Set-Identity SI-6a(PER 이관 — rename 동반 개명) · PER-c20 · PRJ-c61
- 비고: #562-2·-4 는 Geometry 이름 고정(#599)으로 소멸(c08·c10), #562-3 은 DOE 소관(c09). Rename 시그널 미발행은 폴더를 참조하는 Runner·Optimizer(c04, RUN·OPT) 가 setId 를 들게 되면 불필요

## Add File · Project Assets

### PRJ-20 · (CLOSE) Add File 덮어쓰기 뒤 Condition 재읽기를 CON-03 에 넘긴다
- 종류: CLOSE | 규모: - | 태그: A · bug
- 목표: #645-1 을 CON-03 과 중복 항목화한 것을 정리한다 — PRJ 몫 실작업 0
- 완료 기준: 닫기 사유 — 같은 변경(MainWindow 훅 + 위젯 `refreshFromFile`)을 두 모듈이 각각 항목화했고, decisions ⑦ 이 **CON-03 에 남긴다**로 확정했다. PRJ-20 의 `DashConditionParameterizationWidget.h (refresh 진입점 공개)` 는 불필요(`refreshFromFile`·`pinnedDeckFileName` 이 이미 public, `view/DashMainWindow.cpp:777` 이 이미 호출) → 실질 1파일이라 변경 파일 수로도 CON-03 이 본체다. 단 **호출 자리는 PRJ-20 의 서술이 맞다** — `discardLoadedReferenceFile(:2713)` 은 `QFile::remove(:2715)`·`QFile::copy(:2718)` 보다 앞에 돌아 덮어쓰기 전 내용(또는 삭제된 파일)을 읽으므로, 훅은 호출자의 `co_await addReferenceFile(:2694)` → `registry.load(:2766)` 성공 **뒤**여야 한다
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #645-1 · PRJ-c32 (집행은 CON-03)
- 비고: 보류: CON 몫 — CON-03 목표의 훅 위치 교정과 "진입점 노출" 문구 삭제, CON-03·04·06·07 충돌란의 `PRJ-20` 제거. 레지스트리는 invalidate 후 load 를 첫 로드로 보아 `documentChanged` 를 내지 않고(REN), CON 모델은 #565 로 방송 구독을 걷었다 — 통지 책임은 덮어쓰기를 집행한 MainWindow 이고 그 호출 1줄이 CON-03 의 MainWindow 변경분이다. ID 는 CON 항목 4건이 충돌란에서 참조하므로 결번으로 비우지 않고 CLOSE 로 남긴다

### PRJ-21 · Add File 복사를 원자화해 실패 시 기존 파일·등록을 보존한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `copyFileIntoProject` 가 임시 이름으로 복사한 뒤 성공했을 때만 `discardLoadedReferenceFile` + 교체(rename). 실패하면 기존 파일·컨텍스트·트리 행·원장·Set 이 그대로이고 사유를 알린다
- 완료 기준: (1) 읽기 불가 원본으로 덮어쓰기 → 기존 파일 내용·트리 행·Condition 화면 불변 + 오류 통지 (2) 성공 경로의 동작 불변
- 변경 범위: view/DashMainWindow.cpp
- 선행: -
- 충돌: CON-03 (같은 함수 — 복사 성공 뒤 재로드 훅이 이 원자화 뒤에 얹힌다) · PR #651 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #652(DashMainWindow.cpp)
- 흡수: #645-2 · PRJ-c33 · CON-c19 · PRJ-c59
- 비고: 같은 자리의 `releaseGeometryWidgetFor(:2738)` 는 복사 성공 후에도 Geometry 위젯을 start page 로 남기는데, Geometry 재진입 규칙은 #645 범위 밖이다. `.wbpj`·`.stli` 원장 편입(CAD-Path-Disposition 후속작업 5)이 이 함수에서 일어나므로 **LCH-29(DEC) 의 소비자** — 현행 유지로 결정되면 원장 편입 항목 1건이 새로 필요하다

### PRJ-24 · 릴리스 빌드에서 Resample Set 클릭이 무음으로 끝나지 않게 한다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: `handleDoeSamplerSelectionForVariant` 가 위젯이 없는 variant 를 만나면 "이 빌드에서 지원하지 않는 Set" 통지 + 로그를 내고 dock 을 비운다 (또는 restore 시 그 Set 을 비활성 표시)
- 완료 기준: (1) 릴리스 빌드에서 DEV 프로젝트의 Resample Set 클릭 → 통지 1회 + 직전 모듈 화면 잔류 없음 (2) DEV 빌드 동작 불변
- 변경 범위: view/DashMainWindow.cpp (handleDoeSamplerSelectionForVariant)
- 선행: -
- 충돌: PRJ-01 · PR #652 · PR #651 · PR #654 (DashMainWindow.cpp) · DOE-05 (같은 함수) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · PR #655(DashMainWindow.cpp)
- 흡수: DOE-D25 · PRJ-c52 · DOE-c19 · LCH-c62(DOE-c58) (DOE-04 병합, B2)
- 비고: DOE-04 와 병합(B2, 같은 파일·같은 널 가드 자리). DOE 안은 "통지 후 dock 은 직전 화면 유지" — 통지 1회가 핵심이고 dock 처리는 구현 시 택일. #615 가 Resample 의 DEV 전용 유지를 명시 (숨김은 Set 삭제 경로까지 걸려 택하지 않음)

## 전역 접근 해체

### PRJ-03 · DashManager::PrjMgr() 별칭을 제거한다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: `PrjMgr()` 68줄(호출 65 · 선언 1 · 정의 2 — dev 실측 `git grep -c 'PrjMgr()'`: MainWindow 58 · ContextRegistry 5 · tests 2 · DashManager.cpp 2 · .h 1)을 `DashProjectManager::Instance()` 로 기계 치환하고 선언·정의를 지운다. 동작 변화 0
- 완료 기준: (1) `PrjMgr` 심볼 0 (2) 빌드·tests 통과
- 변경 범위: view/DashMainWindow.cpp, controller/DashAnalysisModelContextRegistry.cpp, controller/DashManager.cpp, controller/DashManager.h, tests/TestMorphingPreviewDriver.cpp
- 선행: -
- 충돌: PRJ-01 · PRJ-04 · PRJ-06 · PR #654 #652 #651 (MainWindow·DashManager 광역 치환이라 머지 직후에) · UIC-01 · UIC-03 · UIC-05 · UIC-09 (DashMainWindow 레이아웃·프레임 함수군은 UIC 소유 — 광역 치환은 UIC 항목 랜딩 사이에) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashManager.cpp → CAD-03 CAD-06 DOE-19 EXE-06 PRJ-14 REN-07 · DashAnalysisModelContextRegistry.cpp → EXE-22 REN-01 REN-02 REN-07 UIC-19 · DashManager.h → CAD-06 PRJ-19 · PR #655(DashMainWindow.cpp)
- 흡수: #434-1 · PRJ-c26
- 비고: 246-1 5절 1단계. #432(PRJ-08/09) 와 호출부가 겹치지 않도록 먼저 **D-1 정정(2026-10-06)** — `model/DashAnalysisLauncher.cpp` 는 이미 `DashProjectManager::Instance()` 5곳이고 `PrjMgr()` 0건이라 변경 범위에서 뺐다. 71 → 68 은 dev 실측.

### PRJ-04 · DashManager 의 렌더 인프라를 DashRenderingManager 로 옮기고 PRJ 호출부를 주입으로 바꾼다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: `m_renWin`·`m_renderer`·`m_camWidget`·`m_interactorStyleRubberBand`·`m_originalActor` 와 `Redraw`·`GetRenderWindow`·`AddCamWidget`·`Set/GetCurrentActor`·`updateOriginalActor` 를 DashRenderingManager 소유로. 같은 기제의 **인터랙션 주입**(246-1 2단계 2번)도 함께 — `m_handlePicking`·`m_handleVisualizer` 와 접근자 `GetHandlePickingInteraction`·`GetHandleVisualizer` 를 걷고, 유일한 호출부인 `view/DashMainWindow.cpp:542-543`(`morphingInteraction_`·`morphingVisualizer_` 초기화)을 생성자/세터 주입으로 바꾼다. DashManager 접근자는 전달만 남겨 다른 모듈 호출부가 그대로 컴파일된다. MainWindow 39(렌더 37 + 핸들 2) · ModelingTree 2 곳은 MainWindow 가 든 `DashRenderingManager&` 로 치환
- 완료 기준: (1) `Mgr()->Redraw|GetRenderer|GetRenderWindow|GetRenderingManager|*CurrentActor|AddCamWidget|updateOriginalActor|GetHandlePickingInteraction|GetHandleVisualizer` 가 view/DashMainWindow.cpp·DashModelingTreeWidget.cpp 에서 0 (2) DashManager.h 의 vtk include 가 handle 관련만 (3) 렌더 회귀 0 (Load·모핑 프리뷰·Set 전환) + 핸들 피킹·가시화 회귀 0
- 변경 범위: controller/DashManager.cpp, controller/DashManager.h, controller/DashRenderingManager.cpp, controller/DashRenderingManager.h, view/DashMainWindow.cpp, view/DashMainWindow.h (주입된 `morphingInteraction_`·`morphingVisualizer_` 의 출처 변경), view/DashModelingTreeWidget.cpp
- 선행: PRJ-03
- 충돌: PRJ-01 · PRJ-06 · PRJ-19 · PR #654 (DashManager.cpp·MainWindow.cpp) · #652 · #651 · UIC-03 · UIC-05 · UIC-07 (`Redraw` 호출부가 resize·오버레이 배치 함수군에 걸치면 — UIC 소유) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashMainWindow.h → 공유 11건(deps.md 5절) · DashRenderingManager.cpp → 공유 10건(deps.md 5절) · DashManager.cpp → CAD-03 CAD-06 DOE-19 EXE-06 PRJ-14 REN-07 · DashRenderingManager.h → OPT-01 REN-07 REN-08 REN-09 REN-10 REN-12 · DashManager.h → CAD-06 · DashModelingTreeWidget.cpp → DEV-10 REN-12 · PR #655(DashMainWindow.cpp)
- 흡수: #434-2 · PRJ-c27 (PRJ 분 41곳 — MainWindow 39 + ModelingTree 2) · PRJ-c30 (m_originalActor) · 246-1 5절 2단계 2번(인터랙션 주입)
- 비고: 접점 REN(DashRenderingManager 소유) · MOR(`DashHandlePickingInteraction`·`DashHandleVisualizer` 가 MOR 소관 타입이나 소유·주입 자리가 PRJ 파일이고 호출부가 `DashMainWindow.cpp` 2곳뿐이라 PRJ 가 맡는다 — 04-review 5). MOR 호출부 54곳(c27) · BLD 1 · RUN 2 · OPT 3 · REN 6 은 각 모듈이 전달 접근자를 주입으로 바꾼다 — Phase B 재배정. 246-1 "2단계 verify: Mgr() 180건 미만" 은 이미 182 → 본 항목 후 약 140. PR #655 의 MainWindow hunk 는 `:542-543` 을 건드리지 않는다

### PRJ-05 · 데몬·외부 프로세스·솔버 설정의 소유자를 정한다
- 종류: DEC | 규모: S | 태그: E, B
- 목표: DashManager 생성자가 만드는 journal·MCU·sensitivity 데몬, DashSolverNxCad, DashTopOptPostprocessRunner, `m_solverPaths`(QSettings), `m_cpuCoreCount` 의 목적지 — ① DashDaemonLifecycle 확장 ② 신설 프로세스 허브 ③ 소비 모듈 소유 — 중 하나로 결정
- 완료 기준: 결정 기록 (소유자 · 생성 시점 · 종료 순서 · `atexit(Destroy)` 대체)
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #434-3 · PRJ-c28
- 비고: DashDaemonLifecycle 은 sensitivity·MCU 만 다루고 Journal·NxCad 는 배치·세션 수명이 따로라고 못박았다(.h:21-23) — ① 은 그 전제를 바꾼다. 테스트 가능성의 분기점은 "DashManager 생성자에서 프로세스가 뜨지 않는 것"

### PRJ-06 · 프로세스·설정 생성을 DashManager 생성자 밖으로 옮긴다
- 종류: PR | 규모: M | 태그: E, B · refactor
- 목표: PRJ-05 결정대로 생성·소멸을 소유자로 이동. DashManager 접근자(`mcuDaemon()` 등 38곳 소비)는 전달만 남긴다. `atexit(Destroy)` 를 MainWindow 소멸 순서로 대체
- 완료 기준: (1) `DashManager::DashManager()` 에 `new DashExtensionProcess`·`new DashSolverNxCad`·`QSettings` 0 (2) 앱 종료 시 데몬 고아 0 (3) tests 의 `Mgr()` 최초 호출이 프로세스를 띄우지 않음
- 변경 범위: controller/DashManager.cpp, controller/DashManager.h, 소유자 파일(PRJ-05 결정), main.cpp 또는 view/DashMainWindow.cpp
- 선행: PRJ-05 · PRJ-03
- 충돌: PRJ-04 · PR #654 #652 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashManager.cpp → CAD-03 CAD-06 DOE-19 EXE-06 PRJ-14 REN-07 · main.cpp → DEV-21 DEV-24 EXE-02 EXE-06 PRJ-14 UIC-05 UIC-26 · DashManager.h → CAD-06 PRJ-19 · PR #655(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: #434-3 · PRJ-c28 · PRJ-c30 (atexit)
- 비고: 소비자 38곳/15파일의 접근자 치환은 각 모듈 — Phase B 재배정

### PRJ-07 · 공유 DV 모델과 NX CAD 파라미터 캐시의 소유자를 정한다
- 종류: DEC | 규모: S | 태그: E, C
- 목표: `m_designVariableModel`(CON·CAD 위젯 + DoeSampler·JobRunner 소비) 과 `m_lastNxCadParameterJson`(CAD 위젯 소비 1, `applyLast…` 가 PrjMgr 역참조) 의 목적지 — 프로젝트 수명 객체(DashProject) 또는 소비 모듈 — 결정
- 완료 기준: 결정 기록
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #434 · PRJ-c30 (DV 모델 · NX 캐시)
- 비고: 결정 후 이동 PR 은 CON·CAD 접점 — 결정이 "소비 모듈" 이면 CAD 항목

### PRJ-34 · Set 모델에 공통 베이스를 둘지, 둔다면 어느 층에 둘지 정한다
- 종류: DEC | 규모: S | 태그: E, C
- 목표: Set 모델 10종에 공통 진입점(경로 주입 API · `upstreamStaleReasons()` 같은 가상 함수 · Run-완료 공통 시그널)을 둘 자리를 정한다. `DashMvvmModelBase` 는 production 상속자가 0이고(tests 7개 클래스뿐) Set 모델은 `QObject`(AnalysisLauncher·DoeSampler·ModelBuilder·ModelRunner·ModelRunnerMCU·Optimizer·AIGeometryGeneration) · `QAbstractTableModel`(ConditionParameterization·GeometryParameterCAD) · `QStandardItemModel`(GeometryParameter) 로 갈려 있어, 지금은 베이스를 고쳐도 닿는 코드가 없다. 선택지 — ① 비-QObject 인터페이스(`DashSetModel`/`DashSetPaths` 류)를 다중상속 ② 10클래스 각자 세터·가상 함수 ③ `DashMvvmModelBase` 로 재부모화(QObject 계열만 가능 → 표 모델 2종은 예외 처리)
- 완료 기준: 결정 기록 — 선택지 1개 · 그 자리에 둘 멤버 목록(경로 주입 API · `upstreamStaleReasons()` · Run-완료 시그널) · 표 모델 2종(`QAbstractTableModel`)과 `QStandardItemModel` 1종의 처분 · `DashMvvmModelBase` 를 쓰지 않기로 하면 그 클래스의 존속 여부
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: PRJ-c68
- 비고: decisions ⑧ 이 신설을 지시한 항목. 이 결정 없이는 PRJ-08(주입 API 1개)·PRJ-09(그 API 로의 치환)·PRJ-22(가상 함수 1개 + 공통 시그널)의 규모·완료 기준이 성립하지 않는다. `DashModelRunnerMCU::setProjectDirectory(userPath, projectPath)` 가 2-인자 변종이라 공통 계약이 이것까지 덮어야 한다. CON-05 가 PRJ-08 을 기다리므로 이 결정이 늦으면 CON 모델 1종 선행(역순)을 허용한다 — PRJ-05·07 과 같은 결정 전용 항목

### PRJ-08 · DashProject 가 Set 모델에 경로 접근을 주입하고 자신의 ProjectManager 역호출을 없앤다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: Set 모델 생성(`add*`·`restoreExistingModules`) 시 `DashIOController*`(또는 경로 묶음)를 넘기는 공용 진입점을 **PRJ-34 가 정한 자리**에 두고, DashProject 자신의 `Instance()` 20건을 멤버 주입으로 바꾼다. no-op `SaveProject` 역호출 6건은 삭제
- 완료 기준: (1) model/DashProject.cpp 에 `DashProjectManager::Instance` 0 (2) 주입 API 1개 + `setProjectDirectory` **9클래스**(단일 인자 8 + `DashModelRunnerMCU` 2-인자 1)의 처분(유지·개명·삭제)이 PR 본문에 기록 — 인자 사용 양상이 갈려 있다(`DashModelBuilder.cpp:65`·`DashOptimizer.cpp:133` 은 "NO FALLBACKS" 로 인자 무시, `DashModelRunner.cpp:735`·`DashAIGeometryGeneration.cpp:15` 은 `m_projectPath = path` 저장) (3) 빌드·tests 통과, 프로젝트 열기·Set 생성 동작 불변
- 변경 범위: model/DashProject.cpp, model/DashProject.h, controller/DashProjectManager.cpp, PRJ-34 가 정한 주입 자리의 파일(공통 베이스를 두면 `model/DashMvvmModelBase.*`, 비-QObject 인터페이스면 그 신규 헤더, 각자 세터면 Set 모델 9종의 `.h`)
- 선행: PRJ-34 (주입 자리 결정) · PRJ-03
- 충돌: PRJ-16 · PRJ-17 · PRJ-18 · PRJ-19 · CON-05 (`setProjectDirectory` 계약의 CON 적용분) · PR #652 #651 · B2 교집합: DashProject.cpp → 공유 14건(deps.md 5절) · DashProject.h → PRJ-11 PRJ-22 PRJ-31 PRJ-32 PRJ-33 · DashProjectManager.cpp → EXE-06 PRJ-12 PRJ-13 PRJ-35 PRJ-36 REN-10
- 흡수: #432 · PRJ-c22 (DashProject 분) · PRJ-c23
- 비고: 9개 모델 클래스의 `setProjectDirectory` 가 이미 경로 주입의 절반이다 — 그 자리에 IOController 주입을 얹는다. `GetIOController` 가 94/112 이라 IOController 주입 하나로 대부분 닫힌다. **별도 DEC 로 쪼개지 않는다** — `setProjectDirectory` 계약은 이 항목이 코드로 정하는 한 개념이고(decisions ⑦, 00-plan 1-2), CON-05 는 그 적용분이라 `선행: PRJ-08` 이다. 단 PRJ-34 가 늦어 CON-05 가 블록되면 CON 모델 1종만 먼저 고치고 PRJ-08 이 일반화할 때 맞추는 역순을 허용한다. 보류: CON 몫(CON-05 에 선행 기재)

### PRJ-09 · 모듈 모델 12파일의 DashProjectManager 전역 접근을 주입된 IOController 로 치환한다
- 종류: PR | 규모: L | 태그: E · refactor
- 목표: PRJ-08 의 진입점으로 `Instance()` 92건(+`PrjMgr` 3)을 치환. `IsProjectOpen` 10건은 주입 포인터 null 검사로, `GetProject` 9건은 필요한 값(setIds·referenceModel) 전달로
- 완료 기준: (1) `git grep DashProjectManager::Instance -- model/` 0 (2) tests 통과 (3) 모듈별 Set 진입·Run 회귀 0
- 변경 범위: model/DashModelBuilder.cpp, model/DashModelRunner.cpp, model/DashDoeSampler.cpp, model/DashOptimizer.cpp, model/DashModelBuilderMCU.cpp, model/DashJobRunner.cpp, model/DashAnalysisLauncherKPI.cpp, model/DashAnalysisLauncher.cpp, model/DashGeometryParameter.cpp, model/DashConditionParameterization.cpp, model/DashGeometryParameterCAD.cpp, model/DashAnalysisLaunchExecutor.cpp, model/DashJobRunnerAnsysMotion.cpp
- 선행: PRJ-08
- 충돌: PR #652 (DashAnalysisLauncher·DashDoeSampler) · #651 (DashAnalysisLauncher·DashJobRunner*) · #654 (DashModelRunner·DashOptimizer) · #433 스택(PRE 의 DashAnalysisLauncher 분해) · B2 교집합: DashAnalysisLauncher.cpp → 공유 20건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashOptimizer.cpp → 공유 17건(deps.md 5절) · DashDoeSampler.cpp → 공유 15건(deps.md 5절) · DashModelBuilder.cpp → 공유 13건(deps.md 5절) · DashJobRunnerAnsysMotion.cpp → 공유 11건(deps.md 5절) · DashAnalysisLaunchExecutor.cpp → LCH-06 LCH-07 LCH-14 LCH-16 LCH-28 LCH-34 UIC-20 · DashModelBuilderMCU.cpp → BLD-01 BLD-10 BLD-12 BLD-13 BLD-17 BLD-18 UIC-20 · DashJobRunner.cpp → LCH-02 LCH-03 LCH-07 LCH-13 LCH-14 UIC-20 · DashAnalysisLauncherKPI.cpp → PRE-11 PRE-12 PRE-21 PRE-22 UIC-20 · DashConditionParameterization.cpp → CON-01 CON-02 CON-05 CON-06 UIC-20 · DashGeometryParameterCAD.cpp → CAD-03 CAD-05 CAD-06 CAD-09 UIC-20 · DashGeometryParameter.cpp → MOR-11 UIC-20 · PR #658(DashAnalysisLauncher.cpp) · PR #656(DashAnalysisLauncher.cpp)
- 흡수: #432 · PRJ-c22 (모듈 모델 분)
- 비고: 선행 PRJ-08 은 PRJ-34 결정 뒤에 선다 — 공통 베이스 부재(c68) 때문에 본 항목의 "주입된 IOController" 자리가 결정에 종속된다. L 사유 — 기제 1개의 기계적 치환이고 파일별로 쪼개면 두 접근 경로가 공존하는 중간 상태가 길어진다. 모듈별 PR(BLD 2 · RUN 1 · DOE 1 · OPT 1 · LCH/PRE 4 · MOR/CAD 2 · CON 1) 로 분할해도 무방 — 그 경우 각 모듈 접점

## 저장 · 프로젝트 파일

### PRJ-10 · 즉시 저장 체계에서 Save · Save As · 종료 확인의 의미를 정한다
- 종류: DEC | 규모: S | 태그: A, D
- 목표: 모듈 json 은 편집 즉시 쓰고 `SaveProject` 는 no-op 인데 Save 메뉴는 성공을 보고한다. ① Save 메뉴·SaveProject 제거(즉시 저장 명시) ② dirty 추적 도입 + 명시 저장 — 중 하나. 종료 확인(#485)은 ② 일 때만 성립
- 완료 기준: 결정 기록 + c40 실측(모듈별 "편집 → 디스크" 지연 지점 목록)
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #485 · PRJ-c24 · PRJ-c40
- 비고: 접점 #394(저장 실패 무시)는 보드·원천에 없다

### PRJ-11 · 종료 시 미저장 변경을 확인한다
- 종류: PR | 규모: S | 태그: A, D · feature
- 목표: PRJ-10 이 ② 이면 — DashProject 가 dirty 를 들고 `DashMainWindow::closeEvent` 가 저장/버리기/취소를 묻는다. ① 이면 본 항목은 닫는다
- 완료 기준: (1) 미저장 상태에서 닫기 → 다이얼로그, 취소 시 창 유지 (2) 저장 직후 닫기 → 다이얼로그 없음
- 변경 범위: view/DashMainWindow.cpp, view/DashMainWindow.h, model/DashProject.h
- 선행: PRJ-10
- 충돌: PRJ-01 · PRJ-15 · UIC-05 (`closeEvent` 신설 공유 — geometry 저장은 UIC 소유, 저장 확인 분기는 그 안에 얹는다) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashMainWindow.h → 공유 11건(deps.md 5절) · DashProject.h → PRJ-08 PRJ-18 PRJ-19 PRJ-22 PRJ-31 PRJ-32 PRJ-33 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #652(DashMainWindow.cpp·DashMainWindow.h) · PR #651(DashMainWindow.cpp·DashProject.h)
- 흡수: #485 · PRJ-c40

### PRJ-12 · Save As 가 프로젝트 루트 전체를 복사하고 실패를 보고한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `SaveProjectAs` 의 복사 원천을 `.dproj` 에서 프로젝트 루트로 넓혀 참조 파일·`{Module}_{Set}` 산출물 폴더를 포함하고, `removeRecursively`·`QFile::copy` 의 반환을 모아 실패하면 false 로 반환한다 (지금은 전부 버리고 무조건 `return true` 라 호출부의 "Failed to save project." 분기가 도달 불가다)
- 완료 기준: (1) Save As 결과 폴더에서 열기 → Set·참조 파일·run 결과 전부 보임 (2) 쓰기 불가 대상 → 오류 통지 + 원본 불변 (3) `SaveProjectAs` 안에 반환값을 버리는 파일 연산 0 · 한 건이라도 실패하면 false
- 변경 범위: controller/DashProjectManager.cpp, view/DashMainWindow.cpp
- 선행: -
- 충돌: PRJ-13 (같은 파일) · PRJ-35 · PRJ-36 (같은 함수 `SaveProjectAs`) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProjectManager.cpp → EXE-06 PRJ-08 PRJ-19 REN-10 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #652(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: PRJ-c25 · #394 (실패 무시·성공 오보 몫 — 자기 덮어쓰기 소실은 PRJ-36)
- 비고: 자체 실측. 접점 PER(복사 범위 규약). "기존 대상 폴더 `removeRecursively` 는 사용자 확인 뒤에만" 은 **해법에서 뺐다** — #394 본문이 "삭제를 시작한 시점에 이미 안전한 fallback 이 없다"(TOCTOU · 부분 성공)로 확인 다이얼로그를 기각했고, 기본값대로 확인만 하면 원본이 지워지는 케이스는 PRJ-36 이 거부로 막는다. 순서는 PRJ-36 → PRJ-12

### PRJ-35 · Save As 뒤에 Set 모델과 Module Tree 를 복원한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `SaveProjectAs` 가 복사 뒤 `SetProjectDirectory(newProjectPath)` 를 불러 `clearAllSets()` 로 Set 10종을 `qDeleteAll` 하고 트리 행을 지우는데, `restoreExistingModules()` 재호출도 위젯 unbind 도 없다 — 저장 직후 화면에 Set 이 하나도 없고 위젯은 해제된 모델을 들고 있다. Save As 경로가 프로젝트 전환과 같은 순서를 타게 한다: 전체 위젯 해제(PRJ-01 의 해제 함수) → 경로 전환 → `restoreExistingModules()`
- 완료 기준: (1) Save As 직후 Module Tree 에 전환 전과 같은 Set 목록이 보인다 (2) Save As 직후 모든 카테고리 Set 클릭에 크래시·ASan 보고 0 (3) `SetProjectDirectory` 호출부 3곳(Open·New·Save As) 중 복원이 빠진 곳 0
- 변경 범위: controller/DashProjectManager.cpp, view/DashMainWindow.cpp
- 선행: PRJ-01 (전체 해제 함수를 Save As 경로에서 재사용)
- 충돌: PRJ-12 · PRJ-36 (같은 함수 `SaveProjectAs`) · PRJ-13 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProjectManager.cpp → EXE-06 PRJ-08 PRJ-19 REN-10 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #652(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: PRJ-c65
- 비고: 04-review 2 의 누락 지적. 대안은 "Save As 가 경로만 갱신하고 Set 을 지우지 않는다" — `SetProjectPath` 가 `clearAllSets(); addNewSetItems();` 를 무조건 하므로 그쪽을 고치면 Open·New 경로에 영향이 가고 범위가 커진다. c12 의 잘못된 인과 사슬(`CloseProject → SetProjectPath("")`)이 이 경로를 가렸다

### PRJ-36 · Save As 가 현재 프로젝트를 가리키면 거부하고 삭제 전에 복사를 끝낸다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `SaveProjectAs` 가 대상 폴더를 받으면 (a) 그 폴더가 현재 프로젝트 루트이거나 그 상·하위면 거부하고 사유를 알린다 (b) 어느 경우에도 복사를 끝낸 뒤에만 기존 대상을 치운다 — 지금은 `destBaseDir.removeRecursively()` 가 먼저 돌고, 원본(`sourceProjectDir = GetProjectPath()`)이 대상 폴더 안에 있으면 그것을 지운 다음 빈 `.dproj` 를 순회해 0개를 복사하고 성공을 보고한다. 두 다이얼로그 기본값이 정확히 현재 프로젝트를 가리켜 "확인만" 으로 재현된다
- 완료 기준: (1) Save As 를 두 다이얼로그 기본값대로 확인 → 거부 + 사유 통지, 원본 프로젝트 파일 전부 보존 (2) 대상이 현재 프로젝트의 상위·하위 경로여도 거부 (3) 정상 대상에서는 복사 완료 전에 기존 대상 삭제가 일어나지 않는다 (임시 위치 → 교체)
- 변경 범위: controller/DashProjectManager.cpp, view/DashMainWindow.cpp (`onFileSaveAs` 의 거부 통지)
- 선행: -
- 충돌: PRJ-12 · PRJ-35 (같은 함수 `SaveProjectAs`) · PRJ-13 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProjectManager.cpp → EXE-06 PRJ-08 PRJ-19 REN-10 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #652(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: #394 (자기 덮어쓰기 데이터 소실 몫) · PRJ-c66
- 비고: 보드 밖 OPEN 이슈 4건 편입 중 PRJ 몫(decisions ⑨). #394 본문이 "삭제를 시작한 시점에 이미 안전한 fallback 이 없다"(권한 사전 검사는 TOCTOU · `removeRecursively` 부분 성공 · Windows 핸들 점유)로 확인 다이얼로그 해법을 기각했으므로 PRJ-12 의 "사용자 확인 뒤 `removeRecursively`" 로는 막지 못한다 — 거부와 순서 역전이 본체다. 실패 반환 수집·성공 오보 제거는 PRJ-12. 이슈 본문의 "Overwrite 동작 제거가 정책상 수용 가능한지" 는 아직 미회신이라, 거부 범위를 "자기·상·하위" 로 좁혀 기존 덮어쓰기 기능 자체는 남긴다

### PRJ-13 · 프로젝트를 QLockFile 로 잠가 동시 열기를 막는다
- 종류: PR | 규모: S | 태그: A · feature
- 목표: `OpenProjectFromFolder`·`CreateNewProject` 가 `.dproj/.lock` 을 `QLockFile` 로 잡고 실패 시 false + 잠근 PID 안내; `CloseProject` 가 해제. stale 잠금은 QLockFile 기본 처리
- 완료 기준: (1) 두 인스턴스에서 같은 프로젝트 열기 → 두 번째 거부 + 안내 (2) 비정상 종료 뒤 재열기 성공
- 변경 범위: controller/DashProjectManager.cpp, controller/DashProjectManager.h, view/DashMainWindow.cpp
- 선행: -
- 충돌: PRJ-12 · PRJ-08 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProjectManager.cpp → EXE-06 PRJ-19 PRJ-35 PRJ-36 REN-10 · DashProjectManager.h → PRJ-19 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #652(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: #486 · PRJ-c41

### PRJ-14 · QSettings 스코프를 하나로 통일한다
- 종류: PR | 규모: M | 태그: G, D · refactor
- 목표: main.cpp 에서 `setOrganizationName`/`setApplicationName` 을 한 번 정하고 인자 있는 생성 14곳이 기본 생성자 `QSettings()` 를 쓴다. 채택 스코프(`("NohLab","DashOptiAnalyzer")` 5곳 · `("YourCompany","DashApp")` 5곳 · `("NumeReal","DashOpti")` 4곳 중 하나)는 이 PR 에서 정해 본문에 기록한다 (UIC-04 병합 — 되돌리기 비용이 큰 결정이라 PR 본문에 결정 근거를 남긴다). 구 스코프 키 마이그레이션은 두지 않는다 — 솔버 경로·최근 폴더는 재입력
- 완료 기준: (0) 채택 스코프 · 이관 없음 · 레거시 스코프 방치 결정이 PR 본문에 기록 (1) `QSettings(` 인자 있는 생성 0 (2) 솔버 경로 저장·재기동 복원 동작 (3) 로그 설정(DashLogger::loadSettings) 동작 불변
- 변경 범위: main.cpp, controller/DashManager.cpp, model/DashJobRunnerFeSafe.cpp, view/dialog/SolverSettingsDialog.cpp, view/DashMainWindow.cpp, view/dialog/AboutDialog.cpp, view/log/DashLogDockWidget.cpp
- 선행: -
- 충돌: PRJ-06 (DashManager.cpp 솔버 경로 이동) · PRJ-15 · UIC-05 (창·dock 상태 키가 이 스코프를 쓴다) · UIC-06 (DashMainWindow scaleMenu `UI/scaleFactor` 키) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashManager.cpp → CAD-03 CAD-06 DOE-19 EXE-06 PRJ-03 PRJ-04 REN-07 · main.cpp → DEV-21 DEV-24 EXE-02 EXE-06 UIC-26 · DashJobRunnerFeSafe.cpp → LCH-07 LCH-14 LCH-18 LCH-30 UIC-19 · AboutDialog.cpp → DEV-22 DEV-24 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp·DashManager.cpp) · PR #652(DashMainWindow.cpp·DashManager.cpp) · PR #651(DashJobRunnerFeSafe.cpp·DashMainWindow.cpp)
- 흡수: #481 · PRJ-c42 · #448(스코프 결정 몫) · UIC-c07 (UIC-04 병합, B2)
- 비고: 접점 UIC(로그 dock) · LCH(FeSafe). PRJ-06 이 솔버 경로를 옮기면 그 파일 대신 소유자에서. UIC-05 의 창·dock 상태 키도 이 스코프에 쓴다

### PRJ-15 · Project 메뉴에 최근 프로젝트 목록을 붙인다
- 종류: PR | 규모: S | 태그: D · feature
- 목표: 열기·생성 성공 시 루트 경로를 QSettings 목록(최대 10)에 올리고 Project 메뉴 "Open Recent" 서브메뉴로 보여 준다. 없는 경로는 선택 시 목록에서 제거
- 완료 기준: (1) 열기 후 재기동 → 목록에 있음 (2) 삭제된 경로 선택 → 안내 + 목록 제거
- 변경 범위: view/DashMainWindow.cpp, view/DashMainWindow.h
- 선행: PRJ-14
- 충돌: PRJ-01 · PRJ-11 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashMainWindow.h → 공유 11건(deps.md 5절) · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #652(DashMainWindow.cpp·DashMainWindow.h) · PR #651(DashMainWindow.cpp)
- 흡수: #481 · PRJ-c43
- 비고: 메뉴 구성이 `DashMainWindow` 생성자 인라인(:179-300, Project 메뉴 :179-204)이라 `setupMenus` 같은 함수가 없다 — UIC-05·06 과 같은 블록을 만지므로 랜딩 순서를 맞춘다

## Module Tree · 상류 불일치

### PRJ-22 · 상류 불일치 검사를 모듈별 쌍 등록 구조로 일반화하고 Set 선택 시에도 갱신한다
- 종류: PR | 규모: M | 태그: C, E · refactor
- 목표: `refreshUpstreamStaleness` 의 고정 `checks[]` 를 "카테고리 루트 × 모델의 `upstreamStaleReasons()`" 일반 순회로 바꾸고, 그 가상 함수를 **PRJ-34 가 정한 자리**(공통 베이스 또는 비-QObject 인터페이스)에 기본 빈 구현으로 둔다. **갱신 시점 3개를 모두 일반화** — 프로젝트 열 때(`restoreExistingModules`)·각 모듈 Run 완료·Set 선택. Run 완료는 지금 `addDoeSampler`(`csvFileGenerated`·`analysisFinished` :486-487) 와 `addAnalysisLauncher`(`doeTableSnapshotted` :539) 의 손배선 `connect` 로만 돌아가므로, 쌍 등록이 그 시그널까지 포함하거나 모델이 공통 시그널 1개를 내게 한다. MainWindow 의 Set 선택(`handleSubItemSelection`)에서도 갱신. 동작 변화 0 — Analysis Launcher 쌍만 그대로 돈다
- 완료 기준: (1) tests/TestUpstreamStaleness 통과 + Analysis Launcher ⚠ 회귀 0 (2) 새 쌍 추가가 해당 모델 1파일 변경으로 끝남 — **`DashProject.cpp` 의 `add*()` 에 `connect` 를 손으로 더하지 않아도 Run 완료 갱신이 돈다** (3) Set 선택 직후 ⚠ 갱신 (4) 프로젝트 열기 직후 ⚠ 갱신
- 변경 범위: model/DashProject.cpp, model/DashProject.h, model/DashAnalysisLauncher.h, view/DashMainWindow.cpp, PRJ-34 가 정한 가상 함수·공통 시그널 자리의 파일
- 선행: PRJ-34 (`upstreamStaleReasons()` 와 Run-완료 공통 시그널을 어디에 둘지 — PRJ-08 과 같은 축)
- 충돌: PRJ-08 (DashMvvmModelBase·DashProject) · PR #652 #651 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · DashAnalysisLauncher.h → LCH-33 PRE-03 PRE-08 PRE-16 PRE-23 PRE-24 PRE-32 · DashProject.h → PRJ-11 PRJ-18 PRJ-19 PRJ-31 PRJ-32 PRJ-33 · PR #656(DashAnalysisLauncher.h) · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp)
- 흡수: #650 · PRJ-c34
- 비고: #650 책임: 소비 Set이 실제 사용한 입력 버전의 최신성을 판정하고 프로젝트 객체는 판정을 호출·집계하며 VM은 표시·동작 전달만 맡는다. 버전 규칙은 PRJ-23, 소비 구현은 BLD-15·RUN-31·OPT-23 등이다. #368은 PER-07 → DOE-16 → PRE-32 → BLD-20 생산·공통 판독, #685는 RUN-34·OPT-26 소비이며 조합 ID 산식이나 최초 핀을 도입하지 않는다.

### PRJ-23 · 산출물 버전·비교 불가 상태와 최신성 판정 규칙을 정한다
- 종류: DEC | 규모: S | 태그: C, A
- 목표: #650에서 setId(동일 Set 식별), 산출물 버전(재생성 전후), 결과 항목 키를 구분한다. 생산 Set이 버전을 기록하고 소비 Set이 실제 사용한 입력 버전으로 최신성을 판정한다. 프로젝트는 호출·집계, VM은 표시를 담당한다.
- 완료 기준: 버전 의미·갱신 시점·필수 버전 누락 등 비교 불가 상태·판정 규칙을 먼저 결정한다. 비교 불가를 정상 최신으로 간주하는 정책을 선결하지 않는다. setId·deck 출처만으로 재생성 최신성을 보장하지 않으며 파일 시간·경로·임시 해시로 대체하지 않는다.
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #650 · PRJ-c35
- 비고: #368·#685 출처 계약과 별도 목표다. 필수 출처 누락 구산출물의 재생성 정책과 버전 비교 불가 상태를 구분한다. 후속 구현은 생산 Set의 버전 기록과 소비 Set별 판정, 프로젝트 집계·VM 표시로 나눈다.

## 셸 정리

### PRJ-19 · PRJ 영역의 죽은 코드를 지운다
- 종류: PR | 규모: M | 태그: E, G · refactor
- 목표: 호출·연결이 0인 것을 한 번에 — `DashMainWindow::onEditUndo/onEditRedo`(.cpp:4800·4806 · .h:177-178), `DashMainWindow::m_categoryWidgetMap`(.h:338 선언 · .cpp:652-659 쓰기 7곳 · 읽기 0), `DashProject::addDummyData`, `renameSet` 의 rename 불가 카테고리 분기 4개, `DashProjectManager::GetModuleDataPath/GetModuleConfigPath/GetConfigsDirectory`, `DashManager::m_treeView`
- 완료 기준: (1) 위 심볼 0 (2) 빌드·tests 통과 (3) `"Set1"` 리터럴이 PRJ 파일에서 generateNextSetName 1건만 — `controller/DashIOController.h` 의 3건은 doxygen 예시 주석이라 대상 아님
- 변경 범위: view/DashMainWindow.cpp, view/DashMainWindow.h, model/DashProject.cpp, model/DashProject.h, controller/DashProjectManager.cpp, controller/DashProjectManager.h, controller/DashManager.h
- 선행: -
- 충돌: PRJ-03 · PRJ-04 · PRJ-08 · PRJ-16 · PRJ-17 · PRJ-18 · PR #654 #652 #651 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · DashMainWindow.h → 공유 11건(deps.md 5절) · DashProject.h → PRJ-11 PRJ-22 PRJ-31 PRJ-32 PRJ-33 · DashProjectManager.cpp → EXE-06 PRJ-12 PRJ-13 PRJ-35 PRJ-36 REN-10 · DashManager.h → CAD-06 PRJ-06 · DashProjectManager.h → PRJ-13 · PR #655(DashMainWindow.cpp)
- 흡수: #488 · PRJ-c44 · PRJ-c11 · PRJ-c55 · PRJ-c56 · PRJ-c30 (m_treeView) · RUN-D1 · RUN-c72 → PRJ-c69 (`m_categoryWidgetMap`)
- 비고: #488 은 "결정 완료, 실행만" — 툴바 버튼은 이미 없고 슬롯 2개만 남았다. MorphingBar 의 Undo/Redo 라벨 버튼은 모핑 단계 이동(MOR). `m_categoryWidgetMap` 은 RUN 이 `범위밖 → PRJ` 로 넘긴 것(RUN-c72) — 결함 색인에 RUN-D1 행이 빠져 전 모듈 claims 에서 0건이었다. 메뉴 구성이 `DashMainWindow` 생성자 인라인(:179-300)이라 `setupMenus` 심볼은 없다 — 슬롯 2개 삭제는 메뉴 블록과 무관

### PRJ-25 · 위젯의 DashMainWindow 부모 역참조를 시그널로 바꾼다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: `qobject_cast<DashMainWindow*>` 로 부모를 거슬러 MainWindow 메서드를 부르는 12곳(ModelRunnerWidget 8 · DoeSamplerWidgetBase 2 · OptimizerWidget 2)을 위젯 시그널 + MainWindow connect 로. MainWindow 의 공개 슬롯은 그대로
- 완료 기준: (1) view/ 에 `qobject_cast<DashMainWindow*>` 0 (2) CSV 생성 → Project Assets 갱신 등 기존 경로 동작 불변
- 변경 범위: view/DashMainWindow.cpp, view/DashModelRunnerWidget.cpp, view/DashModelRunnerWidget.h, view/DashDoeSamplerWidgetBase.cpp, view/DashDoeSamplerWidgetBase.h, view/DashOptimizerWidget.cpp, view/DashOptimizerWidget.h
- 선행: -
- 충돌: PRJ-01 · PR #654 (DashOptimizer) · #652 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashOptimizerWidget.cpp → 공유 23건(deps.md 5절) · DashOptimizerWidget.h → OPT-01 OPT-05 OPT-06 OPT-13 OPT-18 OPT-21 OPT-22 UIC-22 · DashModelRunnerWidget.h → RUN-09 RUN-15 RUN-28 RUN-29 RUN-30 UIC-24 · DashDoeSamplerWidgetBase.cpp → ANA-07 DOE-05 DOE-11 · DashDoeSamplerWidgetBase.h → DOE-11 · PR #655(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: RUN-D28 · PRJ-c54
- 비고: 접점 RUN · DOE · OPT. RUN 목록의 RUN-D28 항목과 중복이면 Phase B 에서 한쪽에 합친다

### PRJ-26 · 메뉴 다이얼로그·셸의 이벤트 펌핑 7곳을 제거한다
- 종류: PR | 규모: S | 태그: B · refactor
- 목표: TopOptPostprocessDialog 6곳(onBrowseFem 2 · parseFemToUnstructuredGrid 3 · showProgressMessage 1)과 `DashMainWindow::openFileInViewport` 1곳. 레이아웃 flush 는 `QCoreApplication::sendPostedEvents`/`adjustSize` 로, 파싱 루프의 진행 표시는 워커 또는 `QTimer` 단발로, 코루틴 안의 1곳은 `co_await` yield 로
- 완료 기준: (1) 두 파일 `processEvents` 0 (2) .fem 파싱 중 진행 메시지 표시 유지 (3) Load 스피너가 첫 프레임에 보임
- 변경 범위: view/dialog/TopOptPostprocessDialog.cpp, view/DashMainWindow.cpp
- 선행: -
- 충돌: PRJ-01 · PR #651 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · TopOptPostprocessDialog.cpp → DEV-20 EXE-09 REN-07 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #652(DashMainWindow.cpp)
- 흡수: #455 · PRJ-c45 · PRJ-c47 · CAD-D2 · CAD-c20 · EXE-c43(CAD-D2) · PRJ-c64
- 비고: 완료 판정은 #453(닫힘) 기준. c46(ViewOptions 2) 은 REN, c48(MeshQualityDialog 1) 은 MOR. 접점 EXE(워커 기반). `openFileInViewport` 1곳은 CAD-D2(데몬 stdout 재진입) 의 원인 지점 — `.prt` 경로 회귀를 완료 기준 (3) 에 포함

## 닫기

### PRJ-27 · #246 God-object 해체 부모를 닫는다
- 종류: CLOSE | 규모: - | 태그: E
- 목표: 추적 전용
- 완료 기준: 닫기 사유 — 실작업이 #431(PRJ-02) · #432(PRJ-08/09) · #434(PRJ-03~07) · #433(PRE) 로 전부 분해됨
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #246 · PRJ-c49

### PRJ-28 · #247 Presentation Model 개선 단계 부모를 닫는다
- 종류: CLOSE | 규모: - | 태그: E
- 목표: 추적 전용
- 완료 기준: 닫기 사유 — 착수 전제(#451·#246) 미완이고 본문 작업 3건은 각각 #434(PM 호출부)·모듈 항목·#489(DEV) 에 흡수
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #247 · PRJ-c50

### PRJ-29 · #239 Track B 현황 문서 이슈를 닫는다
- 종류: CLOSE | 규모: - | 태그: E
- 목표: 추적 전용
- 완료 기준: 닫기 사유 — 현황표(2026-08-21)가 낡았고 새 목록이 대체한다
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #239 · PRJ-c51

### PRJ-30 · #376 IsProjectOpen ERROR 오탐을 닫는다
- 종류: CLOSE | 규모: - | 태그: G
- 목표: 해소됨
- 완료 기준: 닫기 사유 — 59df1ee7(#377) 로 `IsProjectOpen` 이 멤버를 직접 검사 (controller/DashProjectManager.cpp:251)
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #376 · PRJ-c31

## Phase B 이관 (PER · BLD · DOE)

### PRJ-31 · DashProject 의 Set json 직접 I/O 를 공용 헬퍼로 옮긴다
- 종류: PR | 규모: S | 태그: A, E · refactor
- 목표: `createModuleJsonFile`(:883-912, 쓰기 :906)·`writeSetReferenceModel`(:199-245, 읽기 :216 · 쓰기 :242) 의 `QFile` 직접 I/O 를 PER-02 가 공용 진입점으로 승격한 **`DashSaveSystem` 헬퍼**(`read/writeJsonFile` — QSaveFile · Result 반환)로 바꾼다 — 원자 쓰기 · 쓰기 실패 시 Set 생성 중단 + 사유 로그(현행은 WARN 뒤 진행) · RMW 의 읽기 규칙(손상 파일 보존)은 헬퍼 계약을 따른다. 같은 파일의 직접 읽기 — `referenceUuidForSet`(:277)·검출기 4벌(:921·:960·:979·:1000) — 도 같이 치환해 두 경로가 공존하지 않게 한다. 동작 변화는 실패 경로뿐
- 완료 기준: (1) model/DashProject.cpp 에 `QIODevice::(WriteOnly|ReadOnly)` 0 (2) 쓰기 불가 configs/ 에서 Add Set → Set 생성 0 + 사유 로그 (3) tests/test_set_identity.cpp 통과 · PER-05 왕복 게이트 적용 (4) 손상된 Set json 에서 검출기가 폴백으로 내려가는 동작 불변
- 변경 범위: model/DashProject.cpp, model/DashProject.h
- 선행: PER-02 (헬퍼)
- 충돌: PRJ-08 · PRJ-16 · PRJ-17 · PRJ-18 · PRJ-19 · PRJ-32 (DashProject.cpp) · PR #652 #651 · B2 교집합: DashProject.cpp → 공유 14건(deps.md 5절) · DashProject.h → PRJ-11 PRJ-22 PRJ-33
- 흡수: #479 · #478 · #480(버전 키는 헬퍼가 자동 기록 — PER-04) · PER-c30 · PRJ-c62
- 비고: PER-02 가 치환하는 `DashSetIdentity.cpp` 사본과 같은 PR 에 실어도 된다(PER 접점). 직쓰기 22지점/14파일 중 PRJ 몫 2지점이고 읽기 6곳이 같은 파일에 있다. 검출기 4벌의 읽기는 PRJ-32 가 그 4벌을 하나로 합치면 자리가 줄어든다 — 두 항목 중 먼저 랜딩하는 쪽이 치환하고 다른 쪽은 결과를 받는다

### PRJ-32 · Set 의 variant 정본을 JSON `variant` 하나로 고정하고 접미사·트리 역할 판별을 없앤다 (BLD-D1)
- 종류: PR | 규모: M | 태그: C, E · refactor
- 목표: 판별 근거를 Set json 의 `variant`(생성 시 기록, 구 파일은 검출기 폴백을 로드 1회 write-back 으로 승격 — SI-3 선례) 하나로 두고, 모델이 `getVariant()` 로 들며 트리 `UserRole+2` 는 그 값을 비추는 캐시(문자열 1종)로 통일한다. 대상 검출기는 **4벌** — `detectGeometryVariant`(:918, 4단 우선순위 `variant` 키 → `Morphing` 객체 → DV source 접두 → 이름 접미) · `detectBuilderVariant`(:957) · `detectRunnerVariant`(:976) · `detectDoeSamplerVariant`(:997). `endsWith("-MCU"/"-CAD")` 판정 12곳과 `UserRole+2` bool/문자열 혼재를 제거하고, **`UserRole+2` 의 비-variant 3번째 용도**(카테고리 루트의 원래 이름, :764 기록 · :1286 복원)도 함께 정리한다 — 루트를 `setEditable(false)`(:763) 로 바꾸고 `UserRole+2` 저장과 `onItemChanged` 의 도달 불가한 `!parentItem` 복원 분기를 지운다. Set 이름의 접미사는 표시 관례로만 남긴다(이름 고정 규칙 #599 변경 없음)
- 완료 기준: (1) `git grep -nE 'endsWith\("-(MCU|CAD)"\)' model/DashProject.cpp view/DashMainWindow.cpp` 0 (2) `UserRole + 2` 의 setData 가 **variant 를 갖는 카테고리에서 문자열 1종, 나머지(Optimizer 는 현재도 미설정 · 카테고리 루트)는 미설정** (3) Sim/MCU · Morphing/CAD · Init/Resample Set 생성·복원·선택·삭제·rename 회귀 0 — 접미사 없는 구 프로젝트 복원 포함 (4) `variant` 폴백·write-back 케이스 테스트가 **검출기별 1개**(4개) (5) 카테고리 루트를 더블클릭해도 편집이 시작되지 않음 — 루트 개명 후 Set rename·delete·Add Set 이 조용히 실패하는 경로가 사라진다
- 변경 범위: model/DashProject.cpp, model/DashProject.h, view/DashMainWindow.cpp (모델 `getVariant` 접근자가 없는 ModelBuilder·ModelRunner 는 접점 BLD·RUN)
- 선행: PRJ-19 (renameSet 죽은 분기 제거) · PER-03 (`variant` 와 버전 키의 역할 분리 ⑥)
- 충돌: PRJ-16 · PRJ-17 · PRJ-18 · PRJ-24 · PRJ-08 · PRJ-31 (DashProject) · PRJ-01 (MainWindow 라우팅) · PR #652 #651 #654 · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · DashProject.h → PRJ-11 PRJ-22 PRJ-33 · PR #655(DashMainWindow.cpp)
- 흡수: BLD-D1 · BLD-c01 · PRJ-c63 · PRJ-c67 (카테고리 루트 개명 · 도달 불가 가드)
- 비고: BLD 가 "변경 파일이 전부 PRJ" 로 이관. Runner(`-MCU`)·Geometry(`-CAD`)·DoeSampler 가 같은 구조라 횡단 1건. 접미사 자체를 이름에서 떼는 것은 범위 밖(이름 고정 #599 와 얽힘). 루트 개명(c67)을 여기에 넣은 이유는 그 `UserRole+2` 가 variant 와 역할이 겹치는 3번째 용도라서다 — 완료 기준 (2) 가 그 정리 없이는 성립하지 않는다. `DashProjectWidget` 은 `setEditTriggers` 를 두지 않아 기본값(DoubleClicked)으로 루트 편집이 열린다

### PRJ-33 · Add Set 을 복원해 Resample 을 `ResampleN` 번호로 추가한다 (DOE-01 이관)
- 종류: PR | 규모: M | 태그: C, D · feature
- 목표: DOE Sampler 의 Add Set 메뉴에서 Init 은 1개 고정(있으면 비활성), Resample 은 항상 활성이며 비어 있는 가장 작은 번호의 `ResampleN` 으로 만든다. 누르면 "Resample Set이 추가됩니다" 안내를 띄운다. variant 폴백도 `ResampleN` 을 인식한다. Rename 불가·DEV 전용 가드는 그대로.
- 완료 기준: Init 있는 프로젝트에서 Resample 을 3번 추가하면 `Resample1·2·3`, `Resample2` 삭제 후 추가하면 `Resample2` · 안내 팝업 1회 · `variant` 키 없는 `DoeSampler_Resample2.json` 이 Resample 로 열린다 · 번호 규칙 단위 테스트
- 변경 범위: view/DashProjectWidget.cpp · model/DashProject.cpp · model/DashProject.h · model/preprocessor/DashDoeTableFile.cpp/.h(다음 번호 헬퍼 — `selectDoeSamplerSet` 의 `ResampleN` 파싱 재사용) · tests/TestDoeTableFile.cpp
- 선행: -
- 충돌: PR #652 · PR #651 (DashProject.cpp) · DOE-05 (DashProject.cpp:addDoeSampler) · PRJ-08 · PRJ-16 · PRJ-17 · PRJ-18 · PRJ-19 · PRJ-31 · PRJ-32 (DashProject.cpp) · DOE-02 (DashDoeTableFile 번호 헬퍼 공용) · B2 교집합: DashProject.cpp → 공유 14건(deps.md 5절) · DashProject.h → PRJ-11 PRJ-22 · DashDoeTableFile.cpp → PER-02 · DashProjectWidget.cpp → DEV-10 UIC-19
- 흡수: #615-1 · #615-2 · #615-3 · DOE-c01, DOE-c02, DOE-c03, DOE-c07, DOE-c08
- 비고: DOE-01 에서 이관(B2) — 변경 파일이 PRJ 소유(DashProjectWidget · DashProject). 접점 DOE(#615 담당, DOE-02 가 번호 헬퍼를 공용). 안내 팝업은 UIC 통지 규칙(#482)을 따른다 (DashNotify)

## 대응표

| 원천 | 항목 | 비고 |
|---|---|---|
| #443 | PER-06 · PER-07 · DOE-16 · PRE-32 · BLD-20 · RUN-34 · OPT-26 | #520 완료 기반 #368 → #685 참조 전환. 별도 Set 원장 불도입, #444·#369 하위 분리 |
| #444 | LCH-32 | #441 하위. 저장·읽기·화면 갱신 비용을 검증하고 필요한 경우에만 분리 |
| Set-Identity SI-6a (PER 이관) | PRJ-16 · PRJ-17 · PRJ-18 | PER-c20 → PRJ-c61 |
| #645 (CON 이관) | PRJ-21 | CON-c19 → PRJ-c59 |
| #479 · #478 · #480 (PER 직쓰기 이행 — PRJ 몫) | PRJ-31 | PER-c30 → PRJ-c62 (createModuleJsonFile · writeSetReferenceModel) |
| BLD-D1 (BLD 이관) | PRJ-32 | BLD-c01 → PRJ-c63 — variant 판별 3벌 (Builder·Runner·Geometry·DoeSampler) |
| CAD-D2 (CAD·EXE·UIC 이관) | PRJ-26 | CAD-c20 · EXE-c43 → PRJ-c64 — `openFileInViewport` 펌핑 1곳 |
| #562 | PRJ-18 | -1 만 유효. -2·-4 는 Geometry 이름 고정으로 소멸(c08·c10), -3 은 DOE(c09). 죽은 분기는 PRJ-19 |
| #551 | PRJ-01 | 위젯 7곳 전부 유효. delegate 는 CON(c19), CAD 누수는 #560 해소(c20) |
| #431 | PRJ-02 | |
| #432 | PRJ-08 · PRJ-09 | SaveProject 역호출 6건은 no-op 삭제 |
| #434 | PRJ-03 · PRJ-04 · PRJ-05 · PRJ-06 · PRJ-07 | 4단계 해소(c29). 246-1 5절 2단계 2번(인터랙션 주입)은 PRJ-04 에 포함(04-review 5). 타 모듈 호출부(MOR 54 · 소비자 38)는 Phase B 재배정 |
| #376 | PRJ-30 | 해소됨 |
| #645 | PRJ-21 · PRJ-20(CLOSE) | -1 재읽기 집행은 CON-03 (decisions ⑦) — PRJ-20 은 중복이라 CLOSE, 호출 자리는 `addReferenceFile` 재로드 뒤 |
| #650 | PRJ-22 · PRJ-23 | 생산 Set 버전 기록·소비 Set 판정·프로젝트 호출/집계·VM 표시. BLD-15·18, RUN-31, OPT-23 |
| #394 (보드 밖 OPEN) | PRJ-36 · PRJ-12 | decisions ⑨ 의 편입 4건 중 PRJ 몫. 자기 덮어쓰기 소실 → PRJ-36, 실패 무시·성공 오보 → PRJ-12 (c66) |
| LCH-29 (DEC, 접점) | 항목 없음 | PRJ 는 소비자 — `.wbpj`·`.stli` 원장 편입이 PRJ 코드(`copyFileIntoProject`·`DashReferenceModelLedger`·Project Assets 트리). 사장 확정이면 신규 0, 현행 유지면 원장 편입 항목 1건 신설 (decisions ①). PRJ-21 비고에 기재 |
| RUN-D1 (RUN 이관) | PRJ-19 | RUN-c72 → PRJ-c69 — `m_categoryWidgetMap` 쓰기 7곳·읽기 0 |
| #485 | PRJ-10 · PRJ-11 | 저장 모델 결정 선행 |
| #486 | PRJ-13 | |
| #481 | PRJ-14 · PRJ-15 | |
| #488 | PRJ-19 | 죽은 슬롯 2개 |
| #455 | PRJ-26 | ViewOptions 2 → REN(c46), MeshQualityDialog 1 → MOR(c48) |
| #246 | PRJ-27 | CLOSE |
| #247 | PRJ-28 | CLOSE |
| #239 | PRJ-29 | CLOSE |
| #320 (접점) | 항목 없음 | REN 소관 — `m_vtuVtkActors` 미구현은 MainWindow 파일이나 씬·actor 소유 축 |
| #433 (접점) | 항목 없음 | PRE 소관. PRJ-09 가 model/DashAnalysisLauncher.cpp 를 건드려 충돌만 기록 |
| DOE-D25 | PRJ-24 | DOE-04 병합(B2) — DOE-c19 · LCH-c62 동반 |
| #615-1 · #615-2 · #615-3 (DOE 담당, 접점) | PRJ-33 | DOE-01 이관(B2) — 변경 파일 PRJ 소유 |
| MOR-D14 | 항목 없음 | 해소됨 (c53) |
| RUN-D28 | PRJ-25 | RUN 과 중복 시 Phase B 병합 |
| ANA-D15 | PRJ-19 (PRJ 몫) | 나머지 "Set1" 59건은 각 모듈 (c55) |
| CAD-D13 | 항목 없음 | 해소됨 (c57) |
| OPT-D2 | 항목 없음 | 범위밖 → OPT (c58), PRJ-02 계약 사례 |
| 자체 실측 | PRJ-10 · PRJ-12 · PRJ-34 · PRJ-35 | Save no-op 보고(c24) · Save As 범위(c25) · Set 모델 공통 베이스 부재(c68, decisions ⑧) · Save As 가 Set·트리를 전멸시킴(c65) · 카테고리 루트 개명(c67) 은 PRJ-32 |
