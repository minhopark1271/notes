# DashGUI2 백로그 W1\~W21 코드 실증 — 무엇이 왜 문제이고, 어떻게 고쳐야 하는가

> 원본: 사전조사 Issue #195 — 본문을 이 페이지로 이관한 뒤 Issue 삭제 (2026-08-24). **본 페이지가 정본**
> 이관 주석: 아래 머리글의 `상태:` (Wiki 미연동·원격 미생성) 는 이관 전 시점 표기

> 연관 Issue: #64\
> 상태: 로컬 초안 (GitHub Issue / Wiki 미연동 — wiki 원격 미생성 상태)\
> 기반 문서: [[200-3-prioritized-backlog]] (W 번호 체계·티어·클러스터) · [[198-1-improvement-roadmap]] (Phase 진단) · [[202-1-view-qt-designer-vs-code-cleanup]] (view 실측)\
> 분석 시점: 2026-07-13, 브랜치 `dev` 워킹트리 — **전 앵커를 코드 원문 기준으로 재검증·발췌** (라인 번호는 이 시점 기준, 유효기간 있음)\
> 번호 주의: 요청 표기 "W1\~22"의 W22는 개정 3 시점 번호. 개정 4 재부여 후 최종 항목은 **W21**이며, 구 W22에 해당하는 `.ui` 파일럿 이관은 클러스터 D의 종착 작업으로 2-4절에서 다룬다.\
> 개정 1: 2026-07-13 — 백로그 개정 8·문서 개명 반영: W12 집계 기준(213 호출형 / 226 전체 출현)과 래퍼 선교체 전제 2건, W13 결정분의 W9 게이트 동결·델타 재확인, W18 방향 결정의 C 시기 선행 이동, W7 실행 중 종료의 Job 취소 통합, 5-2절 비유 정밀화(공구 정리·경보기 선교체·골조 보강·배수 역류·가전 설치·거주 중 리모델링) 반영\
> 개정 2: 2026-07-13 — W9 정밀화: grep 게이트 2등급(하드 = 대안 존재 패턴만 / 소프트 = 추세 리포트, 대안 완성 시 승급) + 우회 밸브(기준값 파일 PR 갱신) 운영 명시 — "정리 전 개발 차단" 부작용 해소; 테스트 선정 기준 상향(외부 의존 0 + **사고 전력 또는 수술 예정**) — `DashAnalyzerUtils` 제외, 마커 판정·라인 조립(W3·W6 수술 로직) 편입\
> 개정 3: 2026-07-13 — 서술 구조 재편: 케이스가 여럿인 항목(W2\~W6·W10\~W14·W16·W17·W19·W20)을 케이스별 "코드 → 문제 → 개선" 묶음으로 재배열 (사실·수치·판정 변경 없음) + W18에 배경 문단 추가(i18n 용어·Qt 번역 파이프라인 설명)\
> 개정 4: 2026-07-13 — W18 진행률 실측 추가(명목 래핑 \~15% · 실효 0%) 및 방향 결론 기록: 현 수준은 있으나 마나 → **기존 tr() 제거·영어 고정, 다국어 필요 시점에 전면 도입** (W12 래퍼가 재도입 비용을 낮추는 관문)\
> 개정 5: 2026-07-13 — W19 배경 설명 보강: 계층 의존 방향 규칙(view→model 단방향)과 그 이유 3가지·주방/홀 비유·DTO 용어를 도입부에 추가, 케이스 ①\~④의 문제/개선 해설을 무배경 독자 기준으로 확장, 작업 순서(③→①→②→④) 명시\
> 개정 6: 2026-07-13 — W10 도입부에 배경 문단 + 순서도 2종 추가: processEvents 재진입 크래시 경로 vs 시그널 구동 경로 대비\
> 개정 7: 2026-07-14 — 백로그 개정 12 동기화: W7 클러스터 A→F 이동·여력 시 이연 반영 (2절 클러스터 A·F 해설, 5-2절 공정 대응, 1절 W7 항목 — "다섯 증상" 인과 연쇄는 유효하므로 유지, 소속 표기만 변경)\
> 개정 8: 2026-07-14 — 백로그 개정 13(착수 창 확정) 동기화: 선행분이 [사전 개선] 창으로 확대되어 W8·W12 래퍼·W13 시공·W16이 A 착수 전 완료로 변경된 사실을 2절 클러스터 C 해설에 반영 (잔여 항목 A 완료 후 일괄 이연)\
> 개정 9: 2026-07-14 — 백로그 개정 14 동기화: W18 처분 실행의 [사전 개선] 선행 이동을 2절 클러스터 F 해설에 반영 (W12 래퍼 선교체 전 tr() 청소)\
> 개정 10: 2026-07-14 — 백로그 개정 15 동기화: 백로그 5-2절(리모델링 비유 뷰) 삭제에 따라 2절 말미 "5-2절 공정 뷰와의 대응" 절 제거, 본문 공정 비유 참조 3곳(W12·W13·W15)을 백로그 5-1절 착수 순서 차트(단계 ①\~⑥) 기준으로 재지정\
> 개정 11: 2026-07-14 — 백로그 개정 19(두괄식 재편·절 번호 재부여) 동기화: 백로그 참조 절 번호 갱신 (5절 요약 표→1절 · 5-1절 클러스터 뷰→1-1절)\
> 개정 12: 2026-07-21 — CI 미진행 결정(백로그 개정 29) 동기화: W9의 grep 게이트·CI를 **선택 항목**으로 강등 — "W9 게이트로 봉인" 표현을 "grep 수동 검증(자동 게이트는 선택)"으로 완화(공통 절 3곳), ③ 최소 CI·클러스터 C ② 착수 게이트의 W9 필수 선결 해제. W9 항목·실측 내용 자체는 불변 — 프레이밍만 조정

---

## 0. 이 문서의 위치와 읽는 법

백로그([[200-3-prioritized-backlog]]) 1절 요약 표는 "무엇을 한다"를 한 줄로 압축했다. 이 문서는 그 각 행에 대해 세 가지를 보인다:

1. **문제의 코드** — 실제 저장소에서 발췌한 원문 (요약·의역 아님)
2. **왜 문제인가** — 그 코드가 만들어내는 구체적 증상
3. **올바른 개선** — 어떤 상태가 되어야 맞는지 (가능하면 코드 안의 올바른 선례로)

케이스가 여럿인 항목은 이 세 가지를 **케이스별로 "코드 → 문제 → 개선" 한 묶음**으로 배열하고, 케이스를 관통하는 진단·처방·순서는 도입부 또는 말미의 **공통** 단락에 둔다 (개정 3). 케이스가 하나뿐인 항목(W1·W7·W8·W15·W18·W21)과 자체 구조를 가진 W9는 기존 3단 구성을 유지한다.

구성:
- **1절** — W1\~W21 항목별 실증 (백로그 1절 요약 표 순서)
- **2절** — 클러스터 단위 묶음 설명 (백로그 1-1절 A\~F 기준)
- **3절** — 재검증에서 발견한 기존 문서 대비 갱신 사항 (수치·앵커·사실 관계)

---

## 1. 항목별 실증 — W1\~W21

### 티어 0 — 즉효·무위험

#### W1. 파일 로깅 싱크 설치

> **완료 2026-09-11** (#314 · PR [#317](https://github.com/NumeRealWorks/DashOpti_GUI/pull/317)). 아래 "올바른 개선"의 원안(`qInstallMessageHandler` 1개로 호출부 무수정 회수)이 아니라 **직접 치환**한 통합 Logger로 이행됐다 — 설계·결정 전문은 [docs/unified-logger.md](https://github.com/NumeRealWorks/DashOpti_GUI/blob/dev/docs/unified-logger.md), 백로그 판정 갱신은 [[200-3-prioritized-backlog]] 개정 31. 아래 실증 수치는 조사 시점(2026-07) 실측으로 보존한다.

**문제의 코드** — 문제는 "있는 코드"가 아니라 "없는 코드"다. 프로젝트 전체에서:

- `qInstallMessageHandler` — **0건** (재확인 완료)
- 반면 로그 호출은 `qDebug/qWarning/qCritical` **약 1,193건 / 57파일** (최다: `DashModelRunner.cpp` 140, `DashDataProcessor.cpp` 102, `DashOptimizerWidget.cpp` 93)

**왜 문제인가** — 릴리즈는 콘솔 없는 GUI 앱이므로(`CMakeLists.txt:75-79`의 `WIN32` 분기) 로그는 파일로 남겨야 하는데, 그 파일 싱크가 없다. 1,193건의 로그가 릴리즈에서 전부 증발하고, Issue #64 같은 필드 크래시가 나도 "직전에 무슨 일이 있었는지"를 받을 수단이 없다 — 모든 안정화 작업의 효과 검증도 불가능한 상태.

**올바른 개선** — `main.cpp`의 `QApplication` 생성 직후에 `qInstallMessageHandler` 1개 설치, 로그 파일은 `QStandardPaths::AppDataLocation` 하위 `logs/`에 기록: 스레드 안전(뮤텍스), 크기 기반 회전(예: 5MB x 3개), 세션 시작 시 버전·타임스탬프 헤더. 기존 1,193건은 **코드 수정 없이** 전부 파일로 흘러들어온다. 반나절 작업으로 이후 모든 티어의 진단 기반이 생기는, 백로그 전체 최고 ROI 항목.

#### W2. 개발 잔재 3건 정리

중요도 낮은 화면 구석에 남은 개발 잔재 3건이다. 심각한 결함이라기보다 다듬지 않은 인상을 주는 잔재로, 셋 다 합쳐 시간 단위의 단순 정리 작업.

**① 개발자 로컬 다운로드 폴더 절대경로** — `view/dialog/TopOptPostprocessDialog.cpp:2139-2141`:

```cpp
// STL 파일 렌더링
QString stlFilePath = "C:\\Users\\MIIIING\\Downloads\\TO\\repaired_surface_7.stl";
renderStlFile(stlFilePath);
```

- **문제**: 개발자 머신 밖에는 존재하지 않는 경로라 해당 렌더링만 동작하지 않는다.
- **개선**: 실제 산출물 경로 또는 파일 선택으로 교체.

**② 하드코딩 기본 경로** — `view/DashAIGeometryGenerationWidget.cpp:129`:

```cpp
trainedModelPath = new QLineEdit("C:\\Users\\Program\\Documents\\trained_model.mdl");
```

- **문제**: 잘못된 기본값이 사용자 눈에 그대로 보인다.
- **개선**: 빈 값 + `setPlaceholderText` (마지막 경로 기억은 W4).

**③ 개발자 TODO 문구가 UI 라벨로 노출** — `view/dialog/DashMeshQualityDialog.cpp:110`:

```cpp
m_progressLabel = new QLabel("Please write code to update progress here", statusBarWidget);
```

- **문제**: 개발자 메모가 사용자 눈에 그대로 보인다.
- **개선**: 초기 상태 문구("Ready" 등)로 교체 (진행 표시 연동은 W11).

#### W3. 안전핀 일괄 — 크래시·큐 정지·무음 실패 차단

로드맵 Phase 0에서 W1·W2를 뺀 나머지(2\~8항)다. 대표 3건(①\~③)은 원문으로, 잔여 3건(④\~⑥)은 앵커로 보인다 (전체 목록은 로드맵 Phase 0 표). 각각이 필드에서 "설명 불가능한 증상"으로 나타나며, 개선은 전부 additive·국소 수정이다.

**① 데몬 크래시를 의도적으로 무시** — `controller/DashExtensionProcess.cpp:320-331`:

```cpp
void DashExtensionProcess::onDaemonProcessError(QProcess::ProcessError error)
{
    if (m_waitingFinished) {
        const QString id = m_waitingFinished ? m_currentCommandId : QString();
        ...
        if (error != QProcess::Crashed) {
            emit commandFailed(id, ...);
        }
    }
}
```

`error != QProcess::Crashed` 가드 때문에, 명령 실행 중 데몬이 **크래시했을 때만** `commandFailed`가 방출되지 않는다 — 가장 통지가 필요한 경우가 무음이다.

- **문제**: 데몬 크래시 → UI가 영원히 대기 중으로 보임 (무음 실패).
- **개선**: Crashed 가드 제거 — 크래시일수록 통지.

**② `[ERROR]` 마커를 부분 문자열로 판정** — `controller/DashExtensionProcess.cpp:280-281`:

```cpp
if (trimmed.contains(QStringLiteral("[ERROR]"))) {
    const QString msg = trimmed.mid(trimmed.indexOf(QStringLiteral("[ERROR]")) + 7).trimmed();
```

정상 출력 라인에 `[ERROR]` 문자열이 섞이기만 해도(예: 로그 경로를 에코) 성공 명령이 실패 처리된다. 완료 판정(`[FINISHED]`)이 영영 안 오면 아래 게이트에서 큐 전체가 영구 정지한다 — `:204-217`:

```cpp
void DashExtensionProcess::trySendNext()
{
    if (m_waitingFinished || m_commandQueue.isEmpty()) {
        return;      // m_waitingFinished 해제 조건 = [FINISHED]/[ERROR]/프로세스 사망뿐 — 타임아웃 없음
    }
    ...
    m_waitingFinished = true;
```

- **문제**: 마커 오탐/미수신 → 이후 모든 명령이 조용히 무시됨 (큐 영구 정지).
- **개선**: `[ERROR]`/`[FINISHED]` 라인 정확 매칭(`trimmed == "[FINISHED]"` 방식으로 통일) + 명령 단위 QTimer 워치독(초과 시 실패 처리·큐 해제).

**③ 인코딩 반쪽 통일** — 자식 프로세스는 `PYTHONIOENCODING=utf-8`로 실행하면서 수신부 18곳/5파일(`DashJobRunner` 8, `DashModelRunner` 3, `DashModelBuilder` 3, `DashOptimizer` 3, `TopOptPostprocessDialog` 1)은 `fromLocal8Bit`로 디코드한다. 올바른 선례는 같은 저장소에 있다 — `DashExtensionProcess.cpp:412`:

```cpp
const QString chunk = QString::fromUtf8(m_oneShotProcess->readAllStandardOutput());
```

- **문제**: 인코딩 불일치 → 한글 로그 깨짐.
- **개선**: `fromLocal8Bit` 18곳 → `fromUtf8`.

**④ 무인자 `waitForStarted()`** — `DashJobRunner.cpp:848`: 타임아웃 기본값 30초 (3절 갱신표 참조).

- **문제**: 프로세스 기동이 지연되면 그동안 GUI 블로킹 — 최대 30초 멈춤.
- **개선**: `waitForStarted()`에 짧은 타임아웃 명시.

**⑤ 미가드 Qt accessor 역참조** — 로드맵 4-4절 목록.

- **문제**: 널 역참조 → "선택 없이 실행" 같은 평범한 조작에서 즉시 크래시 (accessor가 정상적으로 null을 반환해도 검사 없이 접근).
- **개선**: 널 가드 일괄 — 위젯 보유 포인터는 `QPointer`.

**⑥ 앱 종료 시 one-shot 자식 미정리** — `main.cpp:74`의 메인윈도우가 `delete`되지 않아 정리 경로가 없고, `atexit` 정리는 데몬 4종만.

- **문제**: 앱 종료 후 자식 프로세스 잔존.
- **개선**: `aboutToQuit` 훅에서 실행 중 자식 정리.

#### W4. 설정 영속화 정비

**①\~③ QSettings 스코프 3종 분열** — **재검증 결과 백로그 표기와 파일 대응이 반대**였다 (3절 갱신표):

① 솔버 경로 저장이 **플레이스홀더 스코프** — `controller/DashManager.cpp:79-81` (`:540`에서도 동일):

```cpp
// Solver Paths
QSettings settings("YourCompany", "DashApp");
QStringList solvers = {"Abaqus", "Ansys", "NASTRAN", "NX"};
```

② UI 스케일은 제품 스코프 — `view/DashMainWindow.cpp:192-193` (main.cpp:25도 동일):

```cpp
QSettings uiSettings("NohLab", "DashOptiAnalyzer");
double currentScale = uiSettings.value("UI/scaleFactor", 1.0).toDouble();
```

③ 라이선스 타입은 무인자 기본 스코프 — `view/dialog/AboutDialog.cpp:168-171`:

```cpp
QSettings settings;
QString licenseTypeStr = settings.value("License/Type", DEFAULT_LICENSE_TYPE).toString();
```

- **문제**: 설정이 레지스트리의 서로 다른 세 위치(`YourCompany\DashApp`, `NohLab\DashOptiAnalyzer`, OS 기본)에 파편화되어 있다. "YourCompany"는 Qt 튜토리얼 예제의 플레이스홀더가 그대로 출고된 것이다.
- **개선**: `main.cpp`에서 `QCoreApplication::setOrganizationName("NohLab")` + `setApplicationName("DashOptiAnalyzer")`을 1회 설정하고 **전 코드가 무인자 `QSettings`를 쓰도록 통일** (③이 사실상 정답 형태였고 스코프 선언만 없었던 것). 기존 `YourCompany\DashApp` 키는 1회 마이그레이션.

**④ 창·레이아웃 저장 전무** — `saveGeometry|saveState|restoreGeometry` grep **0건**, 매 실행마다 화면 80%로 강제 — `main.cpp:74-79`:

```cpp
DashMainWindow* mainWindow = new DashMainWindow();
int width  = int(screenGeometry.width()  * 0.80);
int height = int(screenGeometry.height() * 0.80);
mainWindow->resize(width, height);
```

- **문제**: 사용자가 창 크기·도크 배치를 조정해도 다음 실행에서 전부 초기화된다. 최근 프로젝트(MRU) 목록도 없어 매번 파일 다이얼로그부터 시작한다.
- **개선**: `closeEvent`(W7과 결합)에서 `saveGeometry()/saveState()`, 기동 시 복원. QFileDialog 30곳의 마지막 경로 기억 일관화 + MRU 메뉴.

#### W5. 개발 위생 묶음

전부 `CMakeLists.txt`와 저장소 루트에서 확인. 지금 당장 제품 오류를 만드는 항목은 없다 — ①·④는 실수를 부르거나 숨기는 함정이고, 나머지는 쌓여 가는 지저분함이다. 여섯 건 합쳐 0.5일; 이후 모든 PR의 기반 위생(빌드 신뢰·경고망·스타일 일관성)이 확보된다.

**① stale 빌드 함정** — `CMakeLists.txt:63-67`, `CONFIGURE_DEPENDS` 없음:

```cmake
file(GLOB_RECURSE SRC_FILES
        ${CMAKE_CURRENT_SOURCE_DIR}/controller/*.cpp
        ${CMAKE_CURRENT_SOURCE_DIR}/model/*.cpp
        ${CMAKE_CURRENT_SOURCE_DIR}/view/*.cpp
)
```

- **문제**: 소스 목록 스캔이 설정 시점 1회뿐 → 파일 추가/삭제가 빌드에 자동 반영되지 않음 — "분명 고쳤는데 반영이 안 되는" 유령 증상.
- **개선**: `CONFIGURE_DEPENDS` 추가.

**② C++ 표준 이중 지정 + 타깃명 하드코딩** — `:10`과 `:122-123`:

```cmake
set(CMAKE_CXX_STANDARD 23)
...
if (MSVC)
    target_compile_options(DashOptGUI PRIVATE "/Zc:char8_t-" "/std:c++latest")
```

- **문제**: 표준 지정이 두 경로로 갈라짐 → 한쪽만 바꾸면 조용히 어긋남. 하드코딩 타깃명은 프로젝트명 변경 시 그 줄만 깨짐.
- **개선**: 표준 지정 일원화 + 타깃명을 `${PROJECT_NAME}`으로.

**③ VTK 컴포넌트 중복 나열** — `:175`에서 `FiltersCore FiltersExtraction FiltersGeometry`가 `:168-170`과 중복.

- **문제**: 동작엔 무해하나 컴포넌트 목록의 정확성을 믿을 수 없게 됨.
- **개선**: 중복 컴포넌트 제거.

**④ 경고 레벨 미지정** — `/W4|/W3|-Wall` grep 0건 (MSVC 기본 = 사실상 /W1).

- **문제**: 컴파일러가 공짜로 잡아줄 실수(미초기화, 축소 변환 등)가 전부 통과.
- **개선**: `/W4` 상향 (신규 경고는 단계적 처리).

**⑤ `.clang-format`·`.editorconfig` 없음**

- **문제**: 스타일 유지가 사람의 주의에만 의존 → 드리프트를 막을 장치 없음.
- **개선**: 현행 스타일(m_+camelCase)을 캡처한 `.clang-format`+`.editorconfig` 커밋.

**⑥ 죽은 코드** — `view/DashAnalysisLauncherWidget.cpp:821-898`, 통째로 주석 처리된 `updateDvTable()` 78줄 (호출처 없음, 내부에 중괄호 불일치 버그까지 잔존):

```cpp
//void DashAnalysisLauncherWidget::updateDvTable()
//{
//    if (m_projectPath.isEmpty() || !m_analysisLauncher) {
...
//}
```

- **문제**: 치우는 규칙(⑤)이 없으니 이런 잔재가 계속 쌓임.
- **개선**: 삭제.

### 티어 1 — 선행 구조

#### W6. 실행 경로 일원화

공용 엔진이 있는데 쓰이지 않고, 각 클래스가 수제 QProcess를 굴린다. **공통 진단은 구현 파편화**: 같은 책임(외부 exe 실행)이 6곳에 흩어져 있으니 타임아웃·인코딩·중복 가드·정리 로직을 고칠 때마다 6번 고치고 6번 회귀 테스트해야 한다. 산재는 진행형이다(QProcess 123→137회).

**① 공용 비동기 경로는 거의 비어 있다** — `controller/DashExtensionProcess.cpp:335,370`:

```cpp
bool DashExtensionProcess::runBlocking(const QStringList& args, QString* stdoutOut, int timeoutMs)  // 호출자 0건
void DashExtensionProcess::runAsync(const QStringList& args, const QString& jobId)                  // 호출자 1건 (MCU encode 경로)
```

재검증: `runAsync`는 `model/DashModelBuilderMCU.cpp:361`에 첫 호출자가 생겼다(3절 갱신표). 나머지 one-shot 실행은 여전히 6개 클래스 수제 — 전체 `QProcess` 토큰 **137회/19파일** (view 포함: `DashOptimizerWidget` 13, `TopOptPostprocessDialog` 10).

- **문제**: 정본이 있는데 쓰이지 않아 파편화가 유지된다 — 공통 로직 수정 = 6곳 수정 + 6곳 회귀 테스트.
- **개선**: 공통 책임(exe 검증·env·UTF-8·라인 조립·중복 가드·취소·정리)을 `DashExtensionProcess`에 흡수(새 발명이 아니라 기존 실행 전담 클래스로의 수렴)하고, 수제 6클래스를 `runAsync` 호출로 치환 — 각 클래스의 완료/로그 시그널 표면은 유지(소비자 무수정). 경로는 카탈로그(`DashExtensionProcess.h`)로 일원화.

**② 수제 경로의 품질 편차** — `model/DashModelRunner.cpp:1802-1836` (경로 문자열 concat + exe 존재 미검증 start + 결과 확인은 qDebug뿐):

```cpp
QString executablePath = QCoreApplication::applicationDirPath() + "/extensions/deep_opt/DashOptiDeepOpt.exe";
...
m_process->start(executablePath, arguments);
// Error handling is done via errorOccurred signal connection in constructor
qDebug() << "[DashModelRunner] runNDPrediction: Process start called, state:" << m_process->state();
```

대조적으로 뷰인 `DashOptimizerWidget.cpp:2396-2424`는 exe 존재를 검증한다 — 같은 실행이 클래스마다 다른 품질로 구현되어 있다는 증거. (단 뷰가 QProcess를 직접 굴리는 것 자체가 레이어 위반이다.)

- **문제**: 정본이 없으니 한 곳의 개선이 다른 곳에 전파되지 않는다 — 파편화의 직접 증거.
- **개선**: ①의 일원화로 해소 — 최고 품질 구현(exe 검증 등)을 공용 경로 한 곳에만 두면 전 호출자가 공유한다.

**③ 광역 오살** — `controller/DashExtensionProcess.cpp:52-69` (`:112-114`에서 매 기동마다 호출):

```cpp
proc.start(QStringLiteral("taskkill"), {QStringLiteral("/F"), QStringLiteral("/IM"), exeName});
proc.waitForFinished(3000);
```

- **문제**: `taskkill /F /IM`은 이미지 이름이 같은 **시스템 전역 프로세스**를 죽인다 — 같은 exe를 쓰는 별도 인스턴스·타 세션 포함, 고객 환경에서 "다른 세션의 해석이 갑자기 죽는" 사고로 나타날 수 있다. 게다가 `waitForFinished(3000)`으로 GUI를 3초 블로킹. 이 몰살은 버그라기보다 보상 코드다 — 실행이 수제로 흩어져 자식 PID를 기록·정리하는 주체가 없으니(W3 ⑥), 고아를 치우려면 이름으로 전부 죽이는 수밖에 없었던 것.
- **개선**: `killOrphans`를 자기가 띄운 PID 추적 kill로 축소. 단 수명 관리만 따로 고치는 것은 답이 아니다 — PID 장부가 의미 있으려면 spawn 6곳 전부가 등록해야 하니 어차피 전부를 손대야 하고, 수명은 6벌로 중복된 공통 책임 중 하나일 뿐이다. 그래서 ①의 일원화가 선행 처방이다.

**④ 휴면 버그 — 부분 수신 split** — 출력은 라인 경계와 무관한 덩어리(chunk)로 도착하는데, `runAsync` 수신부(`:407-418`)는 덩어리를 그 자리에서 라인으로 잘라 방출한다.

- **문제**: 한 줄이 두 덩어리에 나뉘어 도착하면 가짜 라인 2개가 되어 `[FINISHED]` 같은 마커 인식이 깨진다. 파이프에 연결된 stdout은 블록 버퍼링(보통 4\~8KB)으로 바뀌므로 출력이 많은 실행에서는 라인 중간 절단이 드물지 않고, 하필 마커가 잘리는 한 번이 큐 영구 정지다.
- **개선**: 잔여 버퍼를 다음 read로 캐리 — 수리는 간단하지만 `runAsync` 확산(①) **전에** 선행해야 한다.

**공통 — 순서와 DoD** — ④ 선수리(필수 선행) → 공통 책임 흡수(①·②) → 단일 one-shot 소비자 **위임(composition)** 전환(①) → `killOrphans` 축소(③). DoD는 **구조·행위 판정**(grep 카운트 비의존, 백로그 개정 28): 대상 소비자가 자체 QProcess 없이 엔진 위임 + 부분 수신 버그 재현 테스트 통과 + 기존 워크플로 무회귀. 구성은 상속이 아니라 위임(선례 MCU `m_encodeHeaderProc`), 상속은 경로·환경 특수화 한정(선례 NxCad). `DashJobRunner`의 다중 프로세스·C API 런처 핸들·파일 폴링은 단일 one-shot 모델과 불일치 — motion-launcher QProcess 부분만 부분 수렴, 나머지는 W10(폴링→워처)/W20(God-object 분해) 이연.

#### W7. 미저장 변경 가드

**문제의 코드** — 없는 코드가 문제다. view 전체 grep:

- `closeEvent` 오버라이드 — **0건**
- `isModified|isDirty|maybeSave` — **0건**
- 자동저장/복구 — 없음

**왜 문제인가** — 사용자가 X 버튼을 누르면 미저장 작업물이 **경고 한 번 없이** 소실된다. 티어 2 완료 전까지 크래시가 남아 있는 동안엔 더 치명적이다 — 크래시 = 즉시 작업물 소실. 데이터 손실은 크래시보다도 사용자 신뢰를 크게 깎는 계급의 결함이다.

**올바른 개선** — ① dirty 플래그 단일 소스: 프로젝트 변경 지점(파라미터 편집·테이블 수정 등)이 한 곳의 `setModified(true)`로 수렴, `QWidget::setWindowModified`로 타이틀바 `*` 표시. ② `DashMainWindow::closeEvent` 오버라이드: dirty면 저장/무시/취소 3버튼 다이얼로그, 취소 시 `event->ignore()`. 이 훅은 W4의 `saveGeometry` 저장 지점이기도 하다. 실행 중 종료(Job 진행 중의 closeEvent)는 W10의 Job 취소 경로와 통합해 처리한다 — W11 사이클 (백로그 개정 8). ③ 여력 시 주기 자동저장 + 기동 시 복구 제안. W6과 무관하므로 티어 0 직후부터 병행 가능. (백로그 개정 12: 클러스터 A→F 이동, 착수는 여력 시로 이연 — 무거운 결함이나 구조 결함이 산재해 후순위 수용)

#### W8. 공통 UI 헬퍼 통합 + Builder 위임

**문제의 코드** — 정본 헬퍼가 있는데 16개 파일이 같은 함수를 로컬 복사본으로 보유한다.

정본 — `view/builder/ModelBuilderUIHelper.cpp:13-35`:

```cpp
QLabel* ModelBuilderUIHelper::createSectionLabel(const QString& text, QWidget* parent)
{
    QLabel* label = new QLabel(parent);
    QFont font = label->font();
    font.setBold(true);
    label->setFont(font);

    QPixmap bulletPixmap(":/style/svg_12px/label_bullet.svg");
    ...
}
```

복사본 (16곳 중 하나) — `view/DashOptimizerWidget.cpp:163-170`, 클래스명만 다르고 본문 동일:

```cpp
QLabel* DashOptimizerWidget::createSectionLabel(const QString& text, QWidget* parent)
{
    QLabel* label = new QLabel(parent);
    QFont font = label->font();
    font.setBold(true);
    ...
}
```

같은 패턴이 반복된다: `createMainButton` 12곳, `QSplitter::handle` 스타일 22블록/9파일, 센터링 셀 17회, `getStatusIcon` **바이트 동일 4사본 + 독립 변종 1** (`DashAnalysisLauncherWidget.cpp:94`, `DashDoeCasesWidget.cpp:119`, `DashModelBuilderWidget.cpp:1956`, `DashModelBuilderMCUWidget.cpp:1613` + `DashMeshQualityDialog.cpp:192`의 switch 변종). 비-MCU Builder는 `ModelBuilderLabelTableHelper`가 있는데도 동일 로직 약 400줄을 인라인 유지 — MCU 쪽이 위임 방식을 이미 검증했다.

**왜 문제인가** — 이 복사본들은 "16곳을 똑같이 고쳐야 하는" 유지비이자, 드리프트의 발원지다(실제로 `#34BDFF` 오타가 복사본을 타고 28회 전파 — W13). 새 위젯을 만들 때마다 또 복사된다. 정본 도입 후 치환이 미완이었든, 정본이 있는데도 복사가 관행이었든 — 이력과 무관하게 진단은 **정본과 사본의 공존**이고 처방은 같다.

**올바른 개선** — 방향은 "반복되는 UI 요소를 전부 공용으로 모은다"이되, 위험도 순으로 분할 실행한다: **동일 사본은 W8**(무감 치환) · 같은 의도의 변종은 W13(시각 승인 필요) · 같은 구조의 복제는 W14(회귀 확인) — 한 번에 하면 무감 치환과 시각 변경이 한 커밋에 섞여 회귀 추적이 안 된다. W8 몫은: `view/common` 헬퍼로 모으고 16+12곳을 호출 1줄로 치환, 비-MCU Builder는 MCU가 검증한 위임 경로로 전환(\~400줄). 합계 순삭제 \~1,500줄/24+파일, 본문이 바이트 동일하므로 **시각 변화 0** — 파일 단위 독립 커밋으로 병행 가능한 저위험 기계 치환. 재발(다음 위젯의 재복사)은 W9 게이트에 "로컬 복사본 0건"을 고정해 봉인한다. W14 구조 통합과 D 클러스터 `.ui` 이관의 정지 작업.

#### W9. 회귀 안전망 구축

**문제의 코드** — 저장소 사실 관계:

- `enable_testing`/`add_test` — CMakeLists.txt에 **0건**, 테스트 파일 0개
- `.github/` 디렉토리 — **없음** (CI 워크플로 부재)
- `.clang-format` — 없음 (W5와 공유)

**왜 문제인가** — 티어 2(실행 모델 전환)는 이 코드베이스 최대의 수술인데, 지금은 "고쳤다가 다시 나빠져도 아무도 모르는" 상태다. 실제로 산재 수치는 문서 작성 사이에도 늘었다(`Mgr()` 339→344, QProcess 123→137). 사람의 리뷰만으로는 역행을 못 잡는다는 실증이다. "정리 후 테스트"의 순서는 여기서 성립하지 않는다 — 그 정리(W6·W10·W20)가 바로 회귀 위험이 가장 큰 수술이라, 테스트 골격과 게이트는 수술 전에 서 있어야 한다.

**올바른 개선** — 착수 순서대로 4꼭지:

**① 테스트 인프라 개설** — `enable_testing()` + 첫 QTest 3건. 선정 기준은 **외부 의존 0 + 사고 전력 또는 수술 예정** (개정 2 — 자명한 유틸의 명목상 테스트는 두지 않는다; 인프라 개통 확인은 어차피 첫 테스트 실행으로 달성):

- **마커 판정·라인 조립** — W3(`[ERROR]` contains 오탐)·W6(부분 수신 split)이 고치는 바로 그 로직. 수정 시 순수 함수로 추출해 "버그 재현 테스트 → 수정 → 통과" 순서로, 해당 티켓과 같은 커밋에서
- **`MeshQualityCheck.hpp`** — 크래시 전력이 있는 영역(`bad5814` — 비설계영역 부재 시 팅김)의 수치 계산
- **`ModelBuilderConfigHelper`** — 외부 exe와의 config JSON 계약: create→parse 왕복 보존·특수문자/`sanitizeString`. 깨지면 무음으로 잘못 학습되고, W14 수술 인접

지저분한 영역은 ②가 커버하고, 확장은 구조가 정리되는 순서대로(Validator 패턴 → W10 Job 전이 표 → W21 VM 테스트).

**② grep 게이트** — 산재 카운트를 현재값으로 동결, 증가 시 실패 (티어 2 착수 전 필수). 단 **개발 차단이 되지 않게 2등급 운영**: 올바른 대안이 **이미 있는** 패턴만 하드(실패), 대안이 아직 없는 패턴은 소프트(추세 리포트만 — 대안이 생기면 하드 승급). 하드도 기준값 파일을 같은 PR에서 사유 한 줄과 함께 올리면 통과 — 차단하는 것은 "몰래 증가"뿐 (우회 밸브).

| 게이트 | 동결 기준값 (2026-07-13 실측) | 등급 (근거: 대안 존재 여부) | 하향 시점 |
|---|---|---|---|
| `model/` 내 `processEvents` | 41 | 하드 — 시그널 구동 선례 존재 | W10 완료 → 0 |
| `DashExtensionProcess.cpp` 외 `QProcess` | 137토큰/19파일 | **소프트 — 추세 가드(신규 산재 방지)**; W6 DoD는 구조 판정으로 전환(백로그 개정 28) | 리터럴 0 비목표 — JobRunner C API·다중 프로세스 정당 잔존 |
| model→view `#include` | 24건/13파일 | 소프트 — 데이터 반환 경로는 W19 산출 | W19 완료 → 0 + 하드 승급 |
| `::Mgr()` 직접 호출 | 291회/28파일 (정확 매칭) | 소프트 — 대체 API는 W20 산출 | W20 진행 따라 하향 + 승급 |

**③ 최소 CI** (선택 — CI 파이프라인 미구축 결정 2026-07-21, 개정 12; grep 게이트는 CI 없이 로컬 훅으로도 가능) — 가능 시점 순: clang-format·grep 게이트는 cloud runner에서 즉시(저장소 텍스트만 필요) / cmake configure는 vcpkg 전환 전까지 로컬 훅(pre-commit/pre-push) / 풀빌드는 CoreLib·Registry에서 검증된 vcpkg manifest+커스텀 레지스트리 패턴 확장 + 바이너리 캐싱 (상세는 [[196-1-ci-todo]]).

**④ 달성 즉시 봉인** — 게이트는 테스트가 아니라 "패턴 + 허용 상한" 한 줄짜리 규칙이고, 정리가 진행될수록 이 **규칙 목록이 늘고 상한이 조여진다**는 뜻: 티어 DoD 달성 순간 상한 하향(W6 완료 → QProcess 0), 신규 규칙 추가(W8 완료 → 로컬 복사본 0건, W13 팔레트 확정 → 신규 hex 색 리터럴 동결 — 개정 8), 소프트 → 하드 승급(W19·W20 완료 시). 유지보수 대상은 기준값 파일의 숫자 몇 줄뿐. 이후의 역행은 사람이 아니라 기계가 잡는다.

### 티어 2 — 실행 모델 전환

#### W10. 이벤트 구동 전환

재진입 크래시 계급(#64)의 원천. 세 가지 형태(+선결 조건 1건)가 공존한다. **공통 진단**: 크래시의 최대 계급은 코드 실수가 아니라 실행 모델이다 — `processEvents` 펌핑이 존재하는 한 재진입 크래시는 지점을 하나 고쳐도 다른 지점에서 재발한다. **종(class) 자체를 없애야** 한다. QProcess와 파일 감시는 본래 비동기다: 블로킹은 `waitFor*`/폴링으로 자초한 것이다.

배경 — `processEvents()`는 "지금 이 자리에서 멈추고 밀린 이벤트를 강제로 처리하고 와라"이다. GUI 스레드가 긴 작업을 붙잡아 이벤트 루프로 못 돌아갈 때(= "응답 없음") UI를 살려 보이게 하는 진통제인데, 그 순간 **큐에 있던 임의 이벤트(사용자 클릭 포함)가 함수 한가운데서 실행**되는 것이 재진입 구멍이다. 크래시 경로와 올바른 경로의 대비 (개정 6):

```
[1. 실행 요청] 사용자가 실행 버튼 클릭 → waitForFile() 진입 (GUI 스레드)
   │   1. 파일 있나 확인 — 아직 없음
   │   2. msleep(2000) — GUI 스레드 2초 잠듦
   │      (이 동안 클릭·화면 갱신 전부 정지 = "응답 없음" 증상)
   │   3. processEvents() 호출 — 증상 가리기: "밀린 이벤트 지금 강제 처리"
   ▼

[2. 재진입 구멍] 함수가 절반 실행된 상태에서, 큐의 이벤트가 그 자리에서 실행됨
   │   1. 사용자가 그 사이 누른 것이 무엇이든 여기서 실행된다
   │   2. 예: 창 닫기 클릭 → 루프가 쓰던 위젯·데이터 객체가 해제(delete)됨
   │   ※ 취소·프로젝트 전환·실행 재클릭(같은 함수 재진입)도 같은 구멍으로 진입
   ▼

[3. 복귀] processEvents()가 끝나고 루프로 돌아옴
   │   1. 루프는 방금 해제된 객체를 계속 참조 (dangling 포인터)
   │   2. 다음 접근 순간 해제된 메모리 역참조
   ▼

[크래시] #64 계열 — 로그 싱크(W1)도 없어 "왜 죽었는지" 기록조차 없음
       model/에만 이 구멍이 41곳 — 한 곳을 고쳐도 다른 40곳에서 재발.
       그래서 지점 수정이 아니라 종(class) 제거가 처방
```

```
[1. 실행 요청] 사용자가 실행 버튼 클릭
   │   1. QFileSystemWatcher에 "파일 생기면 알려줘" 등록
   │   2. 즉시 return — GUI 스레드는 이벤트 루프로 복귀
   ▼

[2. 평상 운행] 기다리는 동안 UI는 평소처럼 동작
   │   1. 멈춤이 없으니 processEvents로 살려낼 필요 자체가 없음
   │   2. 창 닫기·취소도 "정상 이벤트"로 처리 → Job 취소 경로에서 안전하게 정리
   ▼

[3. 알림 도착] 파일 생성 → 시그널 발생 → 후속 처리 슬롯 호출
       함수 중간에 임의 코드가 끼어들 지점이 없음 — 재진입 구멍 자체가 소멸.
       사내 선례 = DashModelRunner (시그널 구동, 블로킹 0)
```

**① 폴링 + 펌핑** — `model/DashJobRunner.cpp:2351-2364`:

```cpp
bool DashJobRunner::waitForFile(const QString& path, int maxWaitSeconds)
{
    const int pollIntervalMs = 2000;
    const int maxIterations = (maxWaitSeconds * 1000) / pollIntervalMs;

    for (int i = 0; i < maxIterations; ++i) {
        QCoreApplication::processEvents();
        if (QFile::exists(path)) {
            return true;
        }
        QThread::msleep(pollIntervalMs);
    }
    return QFile::exists(path);
}
```

- **문제**: GUI 스레드가 2초 잠들었다 깨어나 `processEvents()`로 이벤트를 억지로 펌핑한다. 이 순간 사용자 입력(취소·창 닫기·다른 실행)이 처리되고 — 진행 중 루프가 참조하던 객체가 해제되면 복귀 시 dangling 역참조 = 크래시. `model/` 계층에만 `processEvents` **41곳** (JobRunner 19 / DataProcessor 14 / ResultProcessor 8), `msleep` 5곳.
- **개선**: 파일 대기 폴링 → `QFileSystemWatcher`/`QTimer` 콜백. `processEvents` 41곳 제거 — 시그널 구동 선례는 같은 저장소의 `DashModelRunner`(QProcess 사용처 중 유일하게 블로킹 0).

**② 데몬 기동 블로킹** — `controller/DashExtensionProcess.cpp:150-161`:

```cpp
QElapsedTimer timer;
timer.start();
while (!m_daemonReady
       && timer.elapsed() < m_readyTimeoutMs
       && m_daemonProcess
       && m_daemonProcess->state() == QProcess::Running) {
    m_daemonProcess->waitForReadyRead(300);
    onDaemonReadyRead();
}
```

- **문제**: `m_readyTimeoutMs`는 NX의 경우 **120,000ms** (`DashSolverNxCad.cpp:16`: `setReadyTimeoutMs(120000);`) — 최악의 경우 UI가 2분간 완전히 굳는다.
- **개선**: 데몬 기동 비동기화 — 블로킹 루프를 ready 시그널로 (120s 프리즈 소멸, 기동 중 상태는 UI에 표시).

**③ 이름만 비동기** — `model/DashAnalysisLauncher.cpp:1044-1067`:

```cpp
void DashAnalysisLauncher::runDoeAsync()
{
    ...
    emit analysisStarted();
    generateInputCases(m_referenceTemplates);   // GUI 스레드에서 동기 실행
}
```

같은 파일 `:233`에는 올바른 선례가 있다:

```cpp
QFuture<bool> future = QtConcurrent::run(this, &DashAnalysisLauncher::runAnalysisInThread);
m_analysisWatcher.setFuture(future);
```

- **문제**: 이름은 Async인데 GUI 스레드에서 동기 실행된다 — 호출자는 비동기라 믿는 함수가 UI를 굳힌다.
- **개선**: in-process 장시간 연산만 선별해 `QtConcurrent` 워커로 (`:233` 선례 패턴).

**④ 부수 선결 조건 — 락 없는 lazy-init 싱글톤** — `controller/DashProjectManager.cpp:13-18`:

```cpp
DashProjectManager* DashProjectManager::Instance() {
    if (!m_instance) {
        m_instance = new DashProjectManager();
    }
    return m_instance;
}
```

- **문제**: 워커 스레드 확대(③) 전에 안전화하지 않으면 경쟁 초기화 위험.
- **개선**: 싱글톤 메인 스레드 선-초기화 + 락.

**공통 — 처방의 골격** — 새 발명이 아니라 수렴: 경량 Job 상태머신(Pending→Running→Succeeded/Failed/Cancelled, 도메인 enum + 시그널)을 도입하고 위 케이스들을 그 위로 옮긴다. 파일럿 = DOE 배치 경로(JobRunner, 크래시 밀도 최고 지점) → 검증 후 확산. DoD: `model/` processEvents 0건, GUI 스레드 `waitFor*`/`msleep` 0건 — grep 수동 검증(W9 자동 게이트는 선택).

#### W11. Job 기반 진행 UX

진행 표시가 5방식으로 흩어져 있고, 정작 결정형 진행바는 0건이다. UX 통일은 W10과 같은 사이클에서 처리한다 — 이 산출이 W13의 "진행 표시 정규형"이 된다.

**① 유일한 전역 표시 = 상태바 16x16 무한 스피너** — `view/DashMainWindow.cpp:1864-1872`:

```cpp
m_loadingLabel = new QLabel(this);
m_loadingMovie = new QMovie(":/icons/loading.gif", QByteArray(), this);
m_loadingLabel->setMovie(m_loadingMovie);
m_loadingLabel->setFixedSize(16, 16);
```

- **문제**: 무한 스피너는 "행(hang)"과 "느린 정상 실행"을 구분해주지 못한다.
- **개선**: 상태바 스피너를 Job 상태 연동으로 교체, 진행률 산출 가능 작업은 결정형 `QProgressBar`로.

**② 버튼 텍스트 교체식** — `view/DashOptimizerWidget.cpp:2414-2415`:

```cpp
lgeSpringFitVariablesBtn->setEnabled(false);
lgeSpringFitVariablesBtn->setText("Fitting...");
```

- **문제**: 실행중 상태가 위젯별 로컬 처리로 흩어지고, 취소 버튼도 일관되게 제공되지 않아 사용자가 할 수 있는 일은 강제 종료뿐 — 그러면 W7 공백과 결합해 작업물이 소실된다.
- **개선**: 실행중 상태 단일 소스 → 버튼 비활성화+사유 툴팁 통일, 취소 버튼 일관 제공.

**③ `QProgressBar`/`QProgressDialog` — 코드 0건** — 흥미로운 사실: `qtheme_light.qss`에 QProgressBar 스타일 규칙이 3건 있다 — **스타일은 준비돼 있는데 위젯을 한 번도 안 만든 것**. 그 외 테이블 아이콘, 퍼센트 문자열(`TopOptPostprocessDialog`), 아무 표시 없음까지 5방식 혼재 (W2의 플레이스홀더 라벨도 이 공백의 산물).

- **문제**: 진행 표시가 모듈마다 다른 것은 같은 앱이 화면마다 다른 UX 언어를 쓴다는 뜻이다 — 진행바 0건의 근본 원인은 연결할 진행 상태 자체가 없기 때문 (2절 클러스터 A).
- **개선**: W10의 Job 상태머신이 만든 상태·진행 시그널 위에 진행 UX를 얹는다. 외부 프로세스 진행 보고는 **additive 마커 규약 1종**(`[PROGRESS] n%` + 하트비트 — TopOpt 기존 형식 확장)으로 합의해 확산: 계약 변경(JSON-RPC) 없이 5방식 혼재를 해소한다.

#### W12. 실패 통지 승격

> **부분 이행 2026-09-11** (#314 · PR [#317](https://github.com/NumeRealWorks/DashOpti_GUI/pull/317)). 통지 규칙은 섰고 시스템 실패 79콜이 `DashNotify::error/warning`(팝업 + ERROR/WARN 로그)로 옮겨졌다. **호출형 213건의 정적 래퍼 표준화는 미이행** — `QMessageBox` 156건 존치. 아래 예시의 `emit logMessage(...)` 채널은 삭제됐다(전량 `DASH_LOG_*`). 상세는 [[200-3-prioritized-backlog]] 개정 31·5-4절 W12.

실패가 로그에만 남고 사용자에게 도달하지 않는다.

**① catch가 qDebug만 남기고 계속 진행** — `model/preprocessor/DashResultXmlWriter.cpp:820-822`:

```cpp
} catch (const std::exception& e) {
    qDebug() << "Warning: displacement query failed for" << targetComp << "key" << key << ":" << e.what();
}
```

- **문제**: 예외가 로그 한 줄로 삼켜지고 흐름은 계속 진행된다 — 게다가 W1 전까지는 그 로그마저 릴리즈에서 증발한다 (**이중 무음**).
- **개선**: 통지 규칙의 "그 외" 분기로 승격 — 로그 도크 + 상태 표시.

**② 실패 분기가 로그 후 조용히 return** — `model/DashModelRunner.cpp:1750-1754`:

```cpp
if (m_runtimeContext.modelBuilderPath.isEmpty()) {
    qWarning() << "[DashModelRunner] runNDPrediction: No model builder folder selected.";
    emit logMessage("ERROR: No model builder folder selected.");
    return;
}
```

- **문제**: 사용자 관점에서 "버튼을 눌렀는데 아무 일도 안 일어남"이 된다 — 결과 창이 안 뜨는 이유를 알 방법이 없다.
- **개선**: 통지 규칙의 개입 분기 — **사용자 개입이 필요한 실패 → 모달**.

**공통 — 정량과 처방** — 로그 호출 \~1,193건 vs `QMessageBox::` 전체 출현 227건/17파일 (그중 래퍼 치환 대상인 warning/critical 등 **호출형은 213건** — 집계 기준은 백로그 개정 8에서 명시) — 로그 전용 에러가 UI 통지의 5배. 모듈마다 통지 여부가 다르니(어떤 곳은 모달, 어떤 곳은 로그만) 같은 실수가 화면마다 다른 경험을 만든다. 처방은 규칙 수립(**사용자 개입이 필요한 실패 → 모달, 그 외 → 로그 도크 + 상태 표시**) + 호출형 213건의 `DashDialogs::warn/confirm` 정적 래퍼 표준화(제목·부모·아이콘·언어 통일). 래퍼 표준화분은 무감 치환이라 **티어 0\~1 시기에 선행**하되(백로그 1-1절 [③ 사전 개선] — A 착수 전 완료) 전제 2건(개정 8): 래퍼 API는 W18 방향 결정 반영 후 확정하고, W6/W10 수술 대상 파일(`DashModelRunner`·`DashOptimizerWidget` 등 — 대상의 약 1/5)은 선교체에서 제외해 해당 수술 커밋에 동승시킨다(충돌 방지). 통지 규칙 적용은 W10의 `commandFailed` 계열 정비와 같은 사이클이 자연스럽다.

### 티어 3 — 중복·정규화

#### W13. 디자인 정규화 (스타일 토큰 + 드리프트 수렴)

"의도된 특화"가 아니라 오타와 복붙이 만든 분기라는 직접 증거들 — ①이 기준선, ②·③이 드리프트의 증거다.

**① 정규 팔레트는 QSS에 선언되어 있다** — `resources/style/qtheme_light.qss:1-8`:

```qss
/* =====
    요청하신 색상 맵 적용 (
    기본 배경: #FFFFFF,
    내부 박스/보조 배경: #F9FBFC,
    외곽선: #E5F0F6,
    기본 텍스트: #000000,
    강조색: #34BCFF
) ===== */
```

기준선 — 문제가 아니라 아래 두 케이스의 비교 기준이다.

**② 그런데 헬퍼 정본이 1글자 오타 색을 하드코딩** — `view/builder/ModelBuilderUIHelper.cpp:47-56`:

```cpp
btn->setStyleSheet(
    "QPushButton {"
    "    background-color: #34BDFF;"      // 정규 #34BCFF의 BC→BD 오타
    ...
    "QPushButton:hover {"
    "    background-color: #2A9FD9;"
```

- **문제**: 이 오타가 W8의 복사본 12개를 타고 **28회 전파**됐다 — 같은 의도(액센트 파랑)가 화면마다 다른 값으로 구현된, 의도 없는 드리프트.
- **개선**: 정본을 정규 팔레트 값으로 정정 — W8 통합이 선행되면 1곳 수정으로 끝난다 (역순이면 28곳 수정 후 재통합 — 2절 클러스터 D의 순서 논리).

**③ 같은 파일 안에서 오타 변수명과 정상 변수명이 공존** — `view/overlay/DashMorphingSettings.cpp:1182` vs `:1347`:

```cpp
QString highlighStyle = "background-color: #FFFF99; color: black";    // :1182 — 오타 변수명
QString highlightStyle = "background-color: #FFFF99; color: black;";  // :1347 — 세미콜론 유무도 다름
```

- **문제**: 같은 의도(편집 하이라이트)의 정의가 한 파일 안에서도 갈라져 있다 — 분기가 디자인 결정이 아니라 **의도 없는 드리프트**라는 직접 증거.
- **개선**: 같은 의도는 같은 정의 1곳으로 — 팔레트 상수/QSS 셀렉터로 수렴.

**공통 — 실측과 처방** — 전체 실측: view .cpp의 hex 색 **고유 60종** vs QSS 정규 팔레트 8종, 간격 스케일 9값, 다이얼로그 버튼행 8개 중 7개 수동 조립, 섹션 구분 4방식 — 디자인을 바꾸려면 60종의 정의를 추적해야 한다. 처방은 인라인 반복 그룹을 `qtheme_light.qss` 셀렉터/팔레트 상수 네임스페이스로 수렴: 색 정의 60종 → UI 크롬 \~15종, 간격 9값→4값, 버튼행 7곳→`QDialogButtonBox`, 진행 표시는 W11 산출을 정규형으로. **예외**: analyzer 플롯 서브시스템(tab10 팔레트·`PlotFont` 토큰)은 이미 정규화된 모범 사례 — 건드리면 후퇴. 주의: W8과 달리 **시각 변화 25\~30곳** 포함 — 팔레트 \~15종·간격 스케일 4값 확정안과 승인 주체·고객사 빌드 분기(`DASH_BUILD_*`) 확인은 코드 0줄 결정 사안이므로 티어 0\~1 시기에 선행하고(백로그 1-1절 [② 게이트] 시기 첫날 킥오프 — 합의 리드타임이 지배), 확정 즉시 **W9 게이트에 신규 hex 리터럴 카운트를 고정**해 결정의 부패(stale)를 막는다. 시공은 착수 시 델타 1회 재확인 + 승인 후 (개정 8).

#### W14. view 구조 통합 4건

상속할 곳에 복붙이 있다 — 같은 구조의 복제 2계열.

**① Builder 쌍둥이** — `view/DashModelBuilderWidget.cpp:1292-1302`와 `view/DashModelBuilderMCUWidget.cpp:1249-1259`, 클래스명만 다르고 **verbatim 동일**:

```cpp
void DashModelBuilderWidget::onStopTrainingClicked()      // MCU 버전도 본문 완전 동일
{
    if (!m_modelBuilder) {
        return;
    }

    m_modelBuilder->stopTraining();

    if (startButton) startButton->setEnabled(true);
    if (stopButton) stopButton->setEnabled(false);
}
```

결정적 대비 — model 계층은 이미 상속으로 풀었다, `model/DashModelBuilderMCU.h:22`:

```cpp
class DashModelBuilderMCU : public DashModelBuilder {
```

같은 쌍인데 model은 상속 재사용, view는 2,506줄 vs 2,514줄 통째 복제(중복 70\~75%) — 재사용 전략이 계층 간에 불일치한다.

- **문제**: 한쪽 버그 수정이 다른 쪽에 반영되지 않는 구조이고, 실제 churn 상위 파일이라 이자가 매주 붙는다.
- **개선**: Builder template-method 베이스(\~1,300줄, MCU 전용 요소는 가상 훅) — 난이도 최고라 공통 순서의 마지막.

**② analyzer GL 11종 골격 복붙** — `DashBoxWidget.h:74-93`과 `DashScatter2DWidget.h:123-134`에 동일 멤버가 각자 선언:

```cpp
float m_textSize = 12.0f;
int   m_sigFigs  = 3;
int m_hoverIdx = -1;
int ML = 90, MR = 40, MT = 36, MB = 66;   // 11종 위젯에 반복
```

`generateTicks`("nice number" 알고리즘)는 6개 위젯 .cpp에 각각 별도 구현 (`DashMorrisWidget.cpp:37`, `DashConvergenceWidget.cpp:152`, `DashBoxWidget.cpp:185`, `DashScatter2DWidget.cpp:390`, `DashParetoWidget.cpp:97`, `DashShapDependenceWidget.cpp:304`).

- **문제**: 축·틱·마진 로직을 바꾸려면 11곳을 고쳐야 한다.
- **개선**: `DashPlotWidgetBase : QOpenGLWidget` 베이스클래스(\~500줄, 렌더 시각 회귀 확인).

**공통 — 실행 순서와 범위** — 난이도 오름차순으로: Runner surrogate 코어 헬퍼(\~400줄 — Runner 쌍은 model 결합이 합성이라 베이스클래스 부적합, 헬퍼 추출이 정석) → PlotWidgetFactory 내부 정리(\~350줄) → ② GL 베이스 → ① Builder 베이스. **Geometry 쌍은 쌍둥이가 아니므로 통합 금지** (독립 저작, 중복 2\~3%). 합계 순삭제 \~2,100-2,700줄.

#### W15. 입력 검증 + 툴팁

**문제의 코드** — Qt 표준 검증기가 한 번도 부착되지 않았다.

- `QValidator|setValidator` — **0건** (입력 위젯 916건 대비)
- `setToolTip|setStatusTip|setWhatsThis` — **17건/7파일** (97k LOC 대비)

반면 좋은 패턴이 1개 존재한다 — `view/DashModelRunnerValidator.cpp:42-52`:

```cpp
bool DashModelRunnerValidator::validateBaseParams(
    DashModelRunner* modelRunner,
    QTableWidget* surrogateTable, ...)
{
    if (!modelRunner) {
        emit validationError("Error", "Model runner is not initialized.");
        return false;
    }
```

단계별 위임(`validateReferenceFile` → `validateBaseParams` → …) + `validationError` 시그널로 명시적 통지 — 확산되지 않았을 뿐 방향은 옳다.

**왜 문제인가** — 잘못된 값(음수 두께, 문자가 섞인 숫자 필드)이 실행 시점에야 발견되어 QMessageBox로 사후 튕긴다. 긴 해석을 걸어놓고 나서야 입력 오류를 알게 되는 UX다.

**올바른 개선** — 숫자 필드에 `QDoubleValidator`/`QSpinBox` range 일괄 적용(입력 시점 차단), `DashModelRunnerValidator` 패턴을 타 모듈로 확산(실행 직전 종합 검증), 핵심 실행 버튼·필드 툴팁 보강. W11과 같은 사이클이면 "실행 전 검증 → 실행 중 상태 → 실패 통지"의 전 주기가 완성된다. 단 **W14 이전에 916곳 전면 적용은 금물** — 곧 통합될 중복 위젯에 같은 작업을 두 번 하게 된다 (백로그 개정 13 — W14 이후로 이연).

#### W16. 빌드 시간 단축

**① VTK 헤더가 계층 무관하게 헤더 파일로 전파** — `#include <vtk`를 가진 `.h` 파일 **23개** (view 5, model 6, controller 12). 대표 — `controller/DashManager.h:13-24`, 싱글톤 헤더가 VTK 헤더 12개를 직접 include:

```cpp
#include <vtkGenericOpenGLRenderWindow.h>
#include <vtkOpenGLRenderer.h>
#include <vtkRenderer.h>
#include <vtkActor.h>
#include <vtkSmartPointer.h>
#include <vtkPolyData.h>
...
```

역설적 증거 — 같은 헤더가 view 클래스는 이미 전방선언으로 처리한다 (`:39-40`):

```cpp
class DashGeometryParameterWidget;
class DashMorphingSettings;
```

전방선언 기법을 아는 코드다 — VTK에 적용하지 않았을 뿐.

- **문제**: `DashManager.h`는 `Mgr()` 접근 때문에 사실상 전 계층이 include한다. 이 헤더가 VTK 12개를 끌고 오므로, DashManager를 만지면 **간접 포함하는 모든 TU가 VTK 헤더를 재파싱**한다. 매주 만지는 God 파일들(W20)이 대상이라 증분 빌드 대기가 일상 비용이다.
- **개선**: 헤더 23개의 VTK include를 전방선언(`class vtkRenderer;`)/pimpl로 다이어트 — .cpp로 include를 내림.

**② `target_precompile_headers` 부재**

- **개선**: PCH 도입 — Qt/VTK/Eigen 안정 헤더.

**③ DLL 복사 인라인 \~231줄** — `CMakeLists.txt:262-492`가 동일 `foreach+copy_if_different` 패턴 반복.

- **개선**: DLL 복사를 함수/매크로화.

**공통** — W20(God 해체) 전에 ①의 헤더 다이어트만 선행해도 증분 빌드가 즉시 단축된다.

#### W17. 버전/릴리즈 정비

**① exe에 버전 메타데이터가 없다** — `resources/resources.rc` **전체 내용이 1줄**:

```
IDI_ICON1   ICON    "icon/app_icon.ico"
```

- **문제**: VERSIONINFO 블록 부재 → exe 속성창의 버전 탭이 공란 — 고객사에서 "지금 설치된 게 어느 버전인지"를 exe 속성으로 확인할 수 없어 이슈 재현·릴리즈 추적이 안 된다.
- **개선**: `.rc`에 VERSIONINFO 추가 + 버전을 단일 헤더(CMake `configure_file`)로 중앙화 → About·`.rc`·로그 헤더(W1)가 같은 원천 사용.

**② 라이선스 만료일이 컴파일타임 define** — `view/dialog/AboutDialog.cpp:23-25`, `:153`:

```cpp
static const QString VERSION              = DASH_VERSION;
static const QString LICENSE_EXPIRY_DATE  = DASH_LICENSE_EXPIRY_DATE;
static const QString DEFAULT_LICENSE_TYPE = DASH_DEFAULT_LICENSE_TYPE;
...
QDate expireDate = QDate::fromString(LICENSE_EXPIRY_DATE, "yyyy-MM-dd");
```

- **문제**: 라이선스 연장 = 전체 재빌드+재배포다.
- **개선**: 만료일을 **런타임 서명 파일**로 이전(연장 = 파일 교체).

**③ 빌드 날짜 표기가 실행 시점 날짜로 덮인다** (재검증 신규 발견) — `:144-145`에서 `__DATE__` 기반 값 대신 `QDate::currentDate()` 사용.

- **문제**: About 창의 "빌드 날짜"가 사실은 오늘 날짜다 — 오도성 표기.
- **개선**: 실제 빌드 시점 값(①의 버전 단일 헤더 원천)으로 수정.

**④ 타임아웃 하드코딩 28곳** — `waitForFinished(3000/5000/...)`, `setInterval(...)` 산재 (`DashExtensionProcess.cpp:61,67` 등), 중앙 상수 파일 없음.

- **문제**: 타임아웃 튜닝이 28곳 수색 작업이 된다.
- **개선**: 의미 있는 이름의 상수 헤더로 중앙화.

#### W18. i18n 방향 확정

배경 — i18n(internationalization) = 앱을 다국어로 서비스할 수 있게 만드는 작업. Qt의 방식: 사용자에게 노출되는 문자열을 `tr("...")`로 감싸면 번역 대상으로 표시되고, `lupdate` 도구가 소스를 스캔해 `.ts` 번역 카탈로그 파일을 생성하며, 번역가가 채운 것을 `lrelease`로 컴파일해 앱이 로드하면 화면 문자열이 해당 언어로 바뀐다. 즉 **`tr()`은 입구, `.ts` 파이프라인이 본체** — 둘 다 있어야 번역이 동작한다.

**문제의 코드** — 어중간한 상태의 실측 (view 기준, 2026-07-13 재측정):

- `tr()` 호출 **112건/8파일** — 그중 65건이 `DashMainWindow.cpp`에 집중, 나머지 대다수 위젯은 raw 문자열
- `.ts` 번역 파일 — **0건** (매치는 external/Qt 예제뿐) → tr()로 감싸도 번역이 로드될 수 없음
- `QMessageBox::` 227건은 대부분 미래핑
- (개정 4) 전면 적용 기준 진행률 실측: **명목 래핑률 약 13\~17%** — 래핑 112줄(140출현) vs 미래핑 사용자 노출 사이트 **약 670곳** (`QMessageBox` 213, `new QLabel("...")` 117, 버튼류 생성자 124, `setText` 51, `QTableWidgetItem` 39, `addTab` 32, `setPlaceholderText` 31, `addItem` 28, 기타 \~35). **실효 진행률 0%** — `.ts`가 0건이라 래핑된 112건조차 번역이 동작하지 않는다. 래핑 분포도 8파일 편중(`DashMainWindow` 65, `KPIConfigDialog` 17, `ShortcutsDialog` 16) — 코드베이스 관행이 아니라 몇 개 화면의 부분 적용

**왜 문제인가** — 지금 상태는 양쪽의 비용만 지불한다: tr() 호출의 런타임/유지 비용은 내면서 번역은 불가능하고, 새 코드는 어느 쪽을 따라야 할지 기준이 없다.

**올바른 개선** — 이것은 코드 작업 전에 **의사결정 사안**이다: (a) 다국어 계획이 있으면 → UI 문자열 전면 tr() + `.ts` 파이프라인(`lupdate`/`lrelease`) 구축, (b) 없으면 → tr() 제거·영어 고정을 문서화. 방향 결정(코드 0줄)은 **티어 0\~1 시기(클러스터 C 시기)에 선행**한다(개정 8) — `.ui` 문자열의 번역 처리 방식이 클러스터 D의 이관 형식에, 문구 통일 정책이 W12 래퍼 API에 직결되기 때문. 처분 작업(전면 적용 또는 제거)은 티어 3 — 단 폐기 방향이면 청소 수준이지만, 전면 적용 방향이면 마감 시공급으로 커진다(개정 8 — 방향 결정이 작업 크기를 정한다).

**결론 (개정 4)** — 현재 진행 수준(명목 \~15%, 실효 0%)은 있으나 마나 한 상태다. **(b) 방향을 채택한다: 기존 `tr()`을 걷어내고 영어 고정을 문서화**하고, 다국어가 실제로 필요해지는 시점에 전면 도입을 별도 작업으로 착수한다. 이로써 W12 래퍼 API는 tr() 없이 확정 가능하고, 클러스터 D의 `.ui` 이관도 번역 속성 부담 없이 진행한다. 후일 전면 도입의 비용을 낮추는 장치는 W12 래퍼 자체다 — 사용자 통지 문자열이 `DashDialogs` 한 관문을 지나게 해두면 재도입 시 래퍼 내부 1곳에서 일괄 처리된다 (미래핑 최대 단일 계급인 `QMessageBox` 213건이 이 경로). 티어 3의 W18 처분 작업은 "tr() 제거 청소" 수준으로 확정.

### 티어 4 — 경계 복원·해체

#### W19. 플로터 레이어 역전 제거

배경 — 이 프로젝트는 폴더부터 `model / view / controller`로 나뉜다: **model = 데이터와 계산**(박스플롯 통계, 해석 결과 파싱 — 화면 없이도 성립하는 것), **view = 화면 부품**(QWidget, 버튼, 플롯 위젯 — 보여주는 것). 계층 규칙은 화살표 하나다: **view → model 단방향**. 화면은 데이터를 알아야 그리지만, **계산은 화면을 몰라야** 한다. 이유 세 가지 — ⑴ 테스트: model이 화면을 모르면 GUI 없이(창을 띄우지 않고) 계산만 돌려 검증할 수 있다. ⑵ 교체 자유: 화면을 갈아엎어도(위젯 교체·`.ui` 이관·MVVM 전환) model은 무수정. ⑶ 빌드 파급: 단방향이면 model 수정 → view만 재컴파일, 양방향이면 어느 쪽을 고쳐도 둘 다 재컴파일. 비유하면 model은 주방, view는 홀이다 — 홀이 주방에 주문을 넣는 건 정상이지만, 주방장이 홀에 나와 테이블 배치와 서빙까지 하면 주방만 따로 검사할 수 없고, 홀 인테리어를 바꾸려면 주방장 교육부터 다시 해야 한다. 아래 네 케이스는 전부 "주방장이 홀 일을 하는" 현장이다. W10과 독립적이므로(로드맵 5-2절 판정) 여력 시 티어 2\~3과 병행 가능.

**① model이 위젯을 생성해 반환** — `model/analyzer/DashBoxPlotter.cpp:3`과 `:169-181`:

```cpp
#include "view/analyzer/DashBoxWidget.h"
...
QWidget* DashBoxPlotter::plot()
{
    auto* w = new DashBoxWidget();
    w->setTextOptions(textSize, significantFigures);
    ...
    w->setData(boxes, yMin, yMax);
    return w;
}
```

같은 골격이 플로터 전체에 반복 — model→view include **24건/13파일** (`DashParetoPlotter` 3, `DashShapPlotter` 3, `DashConvergencePlotter` 2, …).

- **문제**: `DashBoxPlotter`는 박스플롯 통계를 계산하는 클래스인데 반환물이 숫자가 아니라 **완성된 화면 부품**이다. 이 순간 "계산이 맞는지" 테스트에도 위젯 생성이 끼어 GUI 환경이 필요해지고, 플롯 위젯을 바꾸려면 model 코드를 열어야 하며, ViewModel이 들어설 자리(표현 상태의 거처)가 생기지 않는다 — W21의 선결 조건.
- **개선**: `plot()`의 반환형을 `QWidget*` → **`BoxData`(계산 결과 데이터)**로. "데이터 → 위젯" 변환은 view 쪽 팩토리 함수가 담당 — 호출부는 `show(plotter.plot())`이 `show(makeBoxWidget(plotter.plot()))` 꼴로 바뀌는 정도다.

**② model이 위젯을 시그널로 방출** — `model/DashDataProcessor.h:130`:

```cpp
void plotWindowReady(QWidget* plotContainer);
```

- **문제**: ①과 같은 역전인데 더 나쁜 형태다. 시그널은 클래스의 **공개 계약**이라, 시그니처에 `QWidget*`가 박히는 순간 이 model의 모든 소비자가 "model이 위젯을 만들어 준다"는 전제에 묶인다. ①은 함수 하나를 고치면 되지만 ②는 발신·수신 양쪽 계약을 함께 바꿔야 한다.
- **개선**: `plotWindowReady(QWidget*)` 폐기 — `plotDataReady(PlotData)` 같은 **데이터 방송**으로 교체하고, 수신측(view)이 ①의 팩토리로 위젯을 만든다.

**③ 역방향도 존재 = 양방향 순환** — `view/analyzer/DashBoxWidget.h:8`:

```cpp
#include "model/analyzer/DashBoxPlotter.h"  // BoxData
```

view 위젯이 `BoxData` 때문에 model 플로터 헤더를 include — ①과 합치면 model↔view가 **서로를** include한다.

- **문제**: `BoxData`(로직 없는 순수 데이터 구조체)가 하필 model 플로터 헤더 안에 정의되어 있어 view가 model 헤더를 include하게 됐다. 순환이 되면 어느 한쪽을 수정해도 양쪽이 재컴파일되고(빌드 의존 오염), 한쪽만 떼어내 테스트·리팩토링할 수 없게 서로를 묶는다.
- **개선**: 데이터 구조체들을 **제3의 가벼운 헤더** `model/analyzer/DashPlotData.h`(로직 없이 구조체만)로 분리. 화살표가 `플로터 → PlotData ← 위젯`으로 바뀌어 순환이 사라진다. 이런 "양쪽이 공유하는 로직 없는 데이터 묶음"을 DTO(Data Transfer Object)라 부른다.

**④ 극단 사례** — `model/DashModelRunner.cpp:2`:

```cpp
#include "view/DashMainWindow.h"
```

- **문제**: ①이 플롯 위젯 하나를 아는 수준이라면, 이것은 model이 **앱 최상위 화면 전체**를 아는 것이다. `DashMainWindow.h`는 사실상 모든 화면을 끌고 들어오는 헤더라 결합 폭이 최대이고, "계산 클래스가 메인 창의 무언가를 직접 부른다"는 뜻이라 호출 경로 추적도 최악이 된다.
- **개선**: MainWindow에서 얻으려던 것(통지·상태 갱신 등)을 시그널 방출로 대체하고 include 삭제 — "model은 소리치기만 하고, 누가 듣는지는 모른다"가 올바른 형태. 24건 제거 범위에 포함.

**공통 — 작업 순서와 DoD** — ③ DTO 분리(순환부터 끊는다 — 다른 단계의 선행 조건) → ① `plot()` 데이터 반환 + view 팩토리 신설 → ② 시그널 교체 → ④ 포함 잔여 model→view include 전부 제거. DoD는 grep 판정: `model/`에서 `#include "view/` grep **0건** (수동 확인 — W9 자동 게이트는 선택). 이것이 끝나야 W21에서 표현 로직이 들어설 자리가 생긴다 — model이 위젯을 직접 만드는 동안엔 중간층(VM)을 끼워 넣을 틈이 없다.

#### W20. God-object 해체

**① `model/DashDataProcessor.cpp` — 4,667줄, 3개월 churn 1위(35회)** — 한 클래스가 담당하는 책임의 단면 (실측 메서드):

- IO/설정: `setProjectDirectory`, `loadDvTable`, `loadRstDataDirectly`, `updateConfigFile`
- 파싱: `parseLoadStep`, `buildIndexMapping`, `loadParameterInfo`
- 플롯 오케스트레이션: `processResults`, `requestPlot`, `requestVtkPreview`
- KPI 도메인 계산 5종: `processModalFrequencyKPI`, `processSideForceKPI`, `processCriticalBucklingLoadKPI`, `processMaxPEEQKPI`, `processMinFatigueLifeKPI`

고객사 조건부 컴파일이 파일 내 혼재 — `#ifdef DASH_BUILD_LGE_COMPSPRING` / `DASH_BUILD_ILJIN_TENSIONLINK` 4블록 (파일 끝 `:4667`이 `#endif // DASH_BUILD_ILJIN_TENSIONLINK`로 끝난다 — 파일의 마지막 880줄이 고객 분기).

- **문제**: churn 1위 파일이 God 1위라는 것은 매주 지불하는 현재 진행형 비용이다 — 어느 책임을 고치든 4,667줄 TU가 재컴파일되고(W16과 결합), 리뷰 diff가 커지고, 회귀 표면이 넓다.
- **개선**: 책임 단위 분해 — IO / 파싱 / KPI 규칙 / 플롯 오케스트레이션. 고객 `#ifdef`는 기존 `extensions/enterprise` rule 클래스 패턴으로 흡수(선례 존재).

**② 싱글톤 컨트롤러가 뷰 위젯을 소유** — `controller/DashManager.h:105-113`, `:170-174`:

```cpp
DashGeometryParameterWidget* m_geometryParameterWidget;
DashMorphingSettings* m_morphingSettingsWidget;
QTreeView *m_treeView;
...
DashGeometryParameterWidget* GetGeometryParameterWidget() const { return m_geometryParameterWidget; }
```

이 게터를 통해 전 계층이 뷰에 도달한다 — `Mgr()` 직접 호출 **291회/28파일** (`::Mgr()` 정확 매칭, 상위: `DashGeometryParameterWidget.cpp` 82, `DashMainWindow.cpp` 46, `DashMorphingSettings.cpp` 39). `DashProjectManager::Instance()` 177회/32파일이 별도로 존재.

- **문제**: `Mgr()->GetGeometryParameterWidget()->...` 체인은 널/댕글링 크래시 표면이자(#64 계열, 프로젝트 재로드 시 재주입 누락 의심 — use-after-free) 테스트 불가능한 결합이다.
- **개선**: DashManager 점진 해체 — 뷰 포인터 3종 제거(시그널로 대체) → 데몬 소유를 ExtensionService로 분리. 모델 수명 계약 명문화(재로드 시 재주입 검증) + 비위젯 계층 부모 없는 raw new 감사.

**공통 — 진행 방식** — 모듈 1개 단위 + 스모크 테스트로 점진 진행. DoD: `Mgr()` 추이 감소 (grep 수동 검증 — W9 자동 게이트는 선택).

### 티어 5 — ViewModel 수렴

#### W21. VM 도입

**문제의 코드** — 위젯 안에 도메인 오케스트레이션이 산다. 대표 — `view/DashGeometryParameterWidget.cpp:1518-1523`, `:1556-1566`:

```cpp
// === 다이얼로그 미리 띄우기 ===
DashMeshQualityDialog dialog(this);
...
dialog.show(); // 빈 창 띄우기
QApplication::processEvents(); // UI 새로고침 강제 실행!
...
for (int testType = 0; testType < 2; ++testType) {
    QString testName = (testType == 0) ? "LOWER RANGE" : "UPPER RANGE";
    ...
    dialog.setProgressText(QString("Step %1/2: Simulating and evaluating %2...")...);
    QApplication::processEvents(); // UI 새로고침!

    vtkNew<vtkUnstructuredGrid> testMesh;
    testMesh->DeepCopy(volumeMesh);
```

**위젯이** 모핑 시뮬레이션 루프를 직접 돌리고, VTK 그리드를 복사하고, `processEvents`로 UI를 수동 펌핑한다. view:model 규모 비 1.66배(52,379 : 31,623)가 이 패턴의 총량이다.

**왜 문제인가** — 표현(진행 텍스트·버튼 상태)과 도메인(메시 품질 평가)이 한 메서드에 붙어 있어 어느 쪽도 단위 테스트할 수 없고, W10이 없애려는 `processEvents`가 view에서 재생산된다. 신규 화면도 이 패턴을 복사하며 자란다.

**올바른 개선** — 형태 목표는 MVVM이되 **결과물로 수렴**시킨다: ① W10의 Job 상태 enum을 전 모듈로 확산(문자열 "Running" 방출 대체). ② 모듈당 얇은 Presenter(VM) 도입 — statusText/색/진행률 등 표현 가공을 위젯에서 VM으로, VM 단위 테스트 작성. ③ Fat Widget 로직 추출 — 위 모핑 루프 등은 model/VM으로. ④ 신규 화면은 View(껍데기)+VM 골격 기본. Qt Widgets는 자동 바인딩이 없으므로 "얇은 Presenter"가 현실적 — 전면 QML/빅뱅 재작성 비권장 판정 계승. 파일럿 모듈 1개의 위젯이 표현 전용(도메인 로직 0)이 되는 것이 DoD.

---

## 2. 클러스터 단위 묶음 설명 — 백로그 1-1절 A\~F 기준

각 클러스터가 "왜 한 묶음인가"를 1절의 코드 증거로 다시 설명한다. 중요도 순서는 백로그 1-1절, 착수 순서는 그 말미 흐름을 따른다.

### 클러스터 A — 실행 모델·Job 수렴 (W6 → W10 → W11·W12) — 중요도 1위

**하나의 결함, 다섯 개의 증상.** 이 증상들은 전부 같은 뿌리에서 나온다 — "긴 작업을 GUI 스레드에서 동기 실행한다"는 실행 모델 (다섯째 증상의 W7은 백로그 개정 12에서 클러스터 F로 이동했지만 증상 연쇄 자체는 유효):

```
[뿌리] GUI 스레드 동기 실행
   │   1. UI가 굳음 → processEvents 펌핑 (W10의 41곳) → 재진입 크래시 (#64)
   │   2. 실행 관리가 없음 → 클래스마다 수제 QProcess (W6의 6클래스)
   │   3. "실행 중"이라는 일급 상태가 없음 → 진행 표시 5방식 혼재 (W11)
   │   4. 실패가 일급 이벤트가 아님 → qDebug만 남고 무음 (W12)
   │   5. 크래시가 남아 있는 동안 → 미저장 작업물 즉시 소실 (W7 — 소속은 F, 백로그 개정 12)
```

W6이 먼저인 이유는 코드에서 직접 읽힌다: `waitForFile`(W10 ①) 같은 폴링을 이벤트 구동으로 바꾸려면 실행이 **한 곳**(runAsync)에 모여 있어야 한 번만 고친다. 산재 상태에서 W10을 하면 6곳을 각각 전환해야 한다. W11·W12가 W10과 같은 사이클인 이유도 코드에 있다: 진행바가 0건인 것은 위젯을 깜빡해서가 아니라 **연결할 진행 상태 자체가 없기 때문**이다(QSS에 스타일만 준비된 채 방치된 것이 그 증거). Job 상태머신이 생기는 순간 진행바·취소·실패 통지는 그 위에 자연스럽게 얹힌다. 이 순서를 어기고 W11을 먼저 하면 동기 실행 모델 위에 만든 UX를 W10 후 재작업하게 된다.

**완성 후 상태**: 재진입 크래시 계급 소멸(#64 해소), 120s 프리즈 소멸, "검증(W15)→진행·취소(W11)→통지(W12)" 실행 전 주기의 뼈대 완성. JSON-RPC 승급은 이 클러스터에 조건부로만 연결된다(재작성 계기 발생 시 동승 — 원칙 6).

### 클러스터 B — 관측·안전핀 (W1·W2·W3) — 중요도 2위, 착수 1순위

**"보이게 만들고, 터지지 않게 묶는다."** 세 항목의 공통점은 코드 원문에서 드러나듯 전부 **국소·additive 수정**이라는 것이다 — W1은 main.cpp 한 곳, W2는 세 줄, W3은 가드/타임아웃/인코딩의 지점 수정. 구조를 건드리지 않으므로 회귀 위험이 사실상 없다.

중요도 대비 착수가 가장 빠른 이유: A의 효과는 B 없이 **측정 불가능**하다. `WIN32` + 핸들러 부재(W1)의 조합은 "필드에서 무슨 일이 일어나는지 아무것도 모르는" 상태를 뜻하고, Crashed 무음 처리(W3 ①)는 데몬이 죽어도 UI가 모르게 만든다. #64를 진단하려면 이 눈가리개부터 벗겨야 한다. 합계 \~3일.

### 클러스터 C — 회귀 안전망·개발 위생 (W5·W9) — 중요도 3위, 착수 2순위

**"고친 것이 다시 나빠지지 않게."** 근거는 실측 추이다: 문서 작성 나흘 사이 `Mgr()` 339→344, QProcess 123→137 — 사람의 주의만으로는 산재가 늘어나는 것을 못 막는다는 직접 증거. W9의 grep 게이트는 A 클러스터의 DoD(processEvents 0건, QProcess는 DashExtensionProcess만)를 **기계가 지키는 규칙**으로 바꾼다. W5는 그 게이트가 돌아갈 기반 위생(포매터·CMake 함정 제거)이다. 골조 공사(A) 직전의 감리 계약 — 합계 \~2일이라 A를 지연시키지 않는다. 개정 8부터 이 시기에 **선행분의 병행 킥오프**도 배치된다: W13 팔레트·W18 방향 결정(코드 0줄, 합의 리드타임이 지배 — 첫날 킥오프)과 W8 공구 정리·W12 래퍼 선교체(무감 치환, 파일 단위 병행). 단 ② 착수 게이트는 W5 완료뿐(W9는 선택 항목으로 착수 게이트에서 제외 — 개정 12) — 선행분 잔여는 A와 병행 지속. (백로그 개정 13: 선행분이 [사전 개선] 창으로 확대 — W8·W12 래퍼·W13 시공·W16을 **A 착수 전 완료**로 변경, 잔여 항목은 A 완료 후 일괄 이연)

### 클러스터 D — view 정리 → Qt Designer 이관 (W8 → W13 → W14 → .ui 파일럿) — 중요도 4위

**"복붙을 걷어낸 뒤에 옮긴다."** 세 단계가 한 트랙인 이유는 대상이 같아서다 — 전부 view의 "같은 것이 여러 벌" 문제이고, 난이도와 리스크가 단조 증가한다:

| 단계 | 대상 | 시각 변화 | 리스크 |
|---|---|---|---|
| W8 | 바이트 동일 복사본 (섹션 라벨 16, 버튼 12, getStatusIcon 4+1, …) | 없음 | 최저 — 기계 치환 |
| W13 | 같은 의도의 변종 (색 60종, 오타 색 28곳, highlighStyle, …) | 25\~30곳 | 승인 필요 |
| W14 | 같은 구조의 복제 (Builder 쌍둥이 70\~75%, GL 11종 골격) | 렌더 회귀 확인 | 중 |

순서의 논리도 코드에 있다: `#34BDFF` 오타(W13)는 W8의 복사본을 **타고** 28회 전파됐다 — 복사본을 먼저 1곳으로 모으면(W8) 색 정정(W13)은 그 1곳 수정이 된다. 역순이면 28곳을 고치고 나서 다시 통합한다. `.ui` 이관이 종착인 이유도 같다: 중복을 정리하지 않고 이관하면 중복이 XML로 그대로 복사된다("정리 먼저 → 이관 나중" — 도입 자체는 확정, 개정 5). W14까지 끝나면 위젯이 표현 전용에 가까워져 이관이 기계 작업이 된다. 순삭제 합계 \~4,000줄(view .cpp의 9\~10%).

### 클러스터 E — 경계 복원·해체 (W16 선행 → W19 → W20 → W21) — 중요도 5위

**"의존의 방향을 바로잡는다."** 네 항목은 전부 **잘못된 방향의 의존**이라는 한 가지 문제의 크기별 발현이다:

- W16: VTK 헤더가 헤더 파일로 전파 (물리적 의존 — 23개 .h)
- W19: model이 view 위젯을 생성 (계층 역전 — 24 include, 양방향 순환)
- W20: 싱글톤이 뷰 포인터 보유, 한 클래스가 5개 책임 (소유 역전·응집 실패)
- W21: 위젯이 도메인 루프 실행 (로직의 거처 오류)

W16이 선행인 이유: 이 클러스터는 헤더를 대량으로 만지는 작업인데, VTK include가 헤더에 있는 동안엔 매 수정이 대규모 재컴파일을 유발한다 — 배선 정리를 먼저 해야 나머지 공사가 빨라진다. W19가 W20보다 앞인 이유: 플로터 역전은 W10과 독립적이라(로드맵 판정) 조기 병행이 가능하고, `plotWindowReady(QWidget*)` 폐기가 DashDataProcessor 분해(W20)의 플롯 오케스트레이션 절단면을 미리 만들어준다. W21이 마지막인 이유: model이 위젯을 만들고(W19) 컨트롤러가 위젯을 쥐고 있는(W20) 한 표현 상태를 모을 자리가 없다 — 앞 단계가 문자 그대로 선결 조건이다.

**완성 후 상태**: model→view 0건, God 파일 분해, 파일럿 모듈이 View+VM 형태 — MVVM이 "목적지"가 아니라 "결과물"로 도달된다.

### 클러스터 F — 독립 소형 편의 (W4·W7·W15·W17·W18) — 중요도 6위, 틈새 배치

**"의존이 없어서 언제든 끼워 넣는 것들."** 다섯 항목의 공통점은 다른 작업과 코드가 겹치지 않는다는 것 — QSettings 스코프(W4), 미저장 가드(W7), 검증기 부착(W15), .rc/라이선스(W17), i18n 결정(W18)은 서로도, A\~E와도 파일이 거의 안 겹친다. 그래서 중요도가 아니라 **시기 적합성**으로 배치한다: W4는 티어 0 시기(0.5일), W7은 여력 시(백로그 개정 12 A→F 이동 — 가드 본체(dirty 추적·closeEvent 다이얼로그·자동저장)는 A와 무의존이고 closeEvent 훅은 W4와 공유, 실행 중 종료 처리만 W10의 Job 취소 경로 완성 후 구현에 포함), W15는 W11 사이클(전 주기 완성) 단 W14 이후(중복 위젯 이중 작업 방지), W17은 릴리즈 시점, W18은 방향 결정이 C 시기 선행으로 이동(개정 8 — W12 래퍼 API·D의 `.ui` 이관 형식에 직결)했고, 처분 실행도 백로그 개정 14에서 [사전 개선] 창으로 선행됐다(폐기 방향 확정으로 의존이 사라짐 — W12 래퍼 선교체 전 tr() 청소).

---

## 3. 재검증 갱신 사항 (2026-07-13, 기존 문서 대비)

이번 코드 원문 재검증에서 발견한, 백로그·로드맵 표기와 다른 사실들. **판정을 뒤집는 항목은 없고** 전부 수치·앵커·세부 사실의 갱신이다.

| # | 항목 | 기존 문서 표기 | 재검증 실측 | 영향 |
|---|---|---|---|---|
| 1 | `runAsync` 호출자 | 0건 (로드맵/백로그) | **1건** — `model/DashModelBuilderMCU.cpp:361` (MCU encode 경로) | W6 서술 보정 — 공용 경로의 첫 사용자가 생겼다는 긍정 신호. 수리 대상(부분 수신 버그)은 동일 |
| 2 | QSettings 스코프 파일 대응 | DashManager = `"NohLab"`, DashMainWindow = `"YourCompany"` | **반대** — DashManager.cpp:80 = `"YourCompany"/"DashApp"`(플레이스홀더), DashMainWindow.cpp:192 = `"NohLab"/"DashOptiAnalyzer"` | W4 마이그레이션 대상 키가 솔버 경로 쪽. 3종 분열 판정 자체는 동일 |
| 3 | `waitForStarted()` 무인자 | "무한 대기" (로드맵) | Qt 기본값 **30초** 블로킹 (`DashJobRunner.cpp:848`) | 무한은 아니나 GUI 스레드 30초 정지 — 타임아웃 명시+비동기화 필요성 동일 |
| 4 | `getStatusIcon` 사본 앵커 | `DashModelBuilderWidget.cpp:1901` | **:1956** (드리프트) | W8 앵커 갱신 |
| 5 | `Mgr()` 호출 수 | 344회/29파일 (느슨한 패턴) | **291회/28파일** (`::Mgr()` 정확 매칭) | 측정 정규식 차이 — W9 게이트 기준값은 정확 매칭 기준으로 고정 권장 |
| 6 | `tr()` 건수 | 163건 (전체 기준) | view 기준 **112건/8파일**, 65건이 DashMainWindow 집중 | W18 편중 실태 구체화 |
| 7 | `QMessageBox::` 건수 | U5 226건 / 래퍼 대상 213건 | 전체 출현 **227건/17파일** | 백로그 개정 8이 집계 기준 명시(213 = warning/critical 등 호출형, 226 = 전체 출현) — 두 수치는 기준 차이이며 실질 변동 없음 |
| 8 | 죽은 코드 범위 | `:821-907` | **:821-898** (78줄) + 내부 중괄호 불일치 버그 잔존 | W5 삭제 범위 갱신 |
| 9 | DashDataProcessor 내 catch | (로드맵: 단일 파일 36개) | **19블록** (`catch` grep 기준) | 측정 방식 차이로 추정 — God 판정 불변 |
| 10 | 로그 호출 총수 | 1,195건 | **\~1,193건/57파일** | 실질 동일 |
| 11 | (신규 발견) About 빌드 날짜 | — | `__DATE__`가 아니라 `QDate::currentDate()`로 표시 (`AboutDialog.cpp:144-145`) — 실행일이 빌드일로 오표기 | W17에 수정 항목 추가 |
| 12 | (신규 발견) QProgressBar QSS | — | `qtheme_light.qss`에 스타일 3건 존재, 위젯 인스턴스 0건 | W11 — 스타일은 준비된 채 위젯만 부재 |

라인 앵커 전반: `DashExtensionProcess.cpp`(워킹트리 수정 상태 포함) 등 주요 앵커는 ±수 라인 이내로 유효 확인. 본 문서의 라인 번호는 전부 2026-07-13 기준.

---

## 다음 단계

- [ ] 티어 0 Issue 분할(백로그 다음 단계 1항) 시 본 문서의 해당 W 절을 각 Issue 본문의 "근거 코드" 섹션으로 인용
- [ ] W9 grep 게이트 기준값은 3절 갱신표의 정확-매칭 수치로 고정 (`::Mgr()` 291, model processEvents 41, model→view 24, QProcess 파일 목록)
- [ ] 3절 11번(빌드 날짜 오표기)은 W17 착수 시 작업 항목에 포함
- [ ] wiki 원격 생성 시 본 문서 push + Issue #64에 링크 comment (백로그 다음 단계와 동일 조건)
