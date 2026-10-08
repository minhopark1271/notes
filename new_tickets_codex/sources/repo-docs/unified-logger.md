# 통합 Logger 설계 결정

> 상태: 결정 확정 (2026-09-08). 14절 작업 순서 1~7 구현 완료(feat/unified-logger). 뷰어 고도화(강조·검색 고도화·과거 파일 열기)는 후속
> 관련 백로그: [200-3-prioritized-backlog](https://github.com/NumeRealWorks/DashOpti_GUI/wiki/200-3-prioritized-backlog) — W1 · W3(일부) · W4(일부) · W12 · 부록 코멘트 6
> 구현 이슈: [#314](https://github.com/NumeRealWorks/DashOpti_GUI/issues/314)
> 관련 이슈: #220 (W1, 미구현 종결 — 본 설계가 대체) · #64 (Crash Debug)

## 1. 배경

앱의 진단 출력은 현재 두 채널로 갈라져 있고, 둘 다 디스크에 남지 않는다.

| 채널 | 호출 지점 | 릴리스(WIN32)에서의 운명 |
|---|---|---|
| `qDebug` / `qWarning` / `qCritical` / `qInfo` | 약 1,090 | 콘솔이 없어 전부 소실 |
| `std::cout` / `std::cerr` (대부분 controller/Morphing) | 74 | 소실 |
| model → view `logMessage(QString)` 시그널 → Log dock | emit 414, connect 약 20 | 종료 시 소실, 표시 전 경로 문자열 제거 |
| `QMessageBox` (warning 172 · information 30 · critical 23 · question 4) | 277 | 사용자에게만 보이고 기록 없음 |
| Qt 내부 경고 (`QObject::connect` 실패, 스레드 경고 등) | - | 소실 |
| VTK 내부 오류 (`vtkErrorMacro`) | - | 별도 네이티브 창 팝업 |

앱이 직접 만드는 로그 파일은 없다. 코드에 보이는 `logs/` 경로는 전부 외부 솔버(Abaqus·ANSYS)가 `run/<runKey>/` 아래 남긴 산출물을 읽거나 안내하는 것이다.

`qInstallMessageHandler`, `vtkOutputWindow` 오버라이드, `QT_MESSAGELOGCONTEXT` 정의는 모두 0건이다.

## 2. 목표

1. 모듈(enum)과 레벨로 구분되는 단일 Logger.
2. 레벨에 따라 파일 / Log dock / 팝업으로 라우팅.
3. 호출 스레드를 막지 않는 비동기 처리.
4. 위의 모든 채널을 신규 Logger로 흡수. 호출부는 wrap하지 않고 전부 직접 치환한다.
5. 후속으로 Log dock을 필터 가능한 뷰어로 개선.

## 3. 결정 요약

| # | 항목 | 결정 |
|---|---|---|
| 1 | 모듈 정의 | enum 고정 |
| 2 | 모듈 목록 | GUI 모듈 21개 + 외부 실행 파일 모듈 8개(Ext*), 4절 참조. MCU 계열은 별도 모듈, Rendering은 View와 분리, Qt·Vtk 포함. 자식 출력 원문의 발신자는 exe 자체이므로 exe마다 카테고리를 둔다 |
| 3 | 레벨 | TRACE, DEBUG, INFO, WARN, ERROR, FATAL (6단계) |
| 4 | 라우팅 | 파일 TRACE+(2026-09-09, 파일은 원본), dock INFO+. Logger는 팝업을 띄우지 않는다 — 팝업은 별도 notify API의 명시 호출로만 |
| 5 | API | `<<` 스트림 매크로, 접두어 `DASH_LOG_` |
| 6 | 레코드 포맷 | 텍스트 라인 v2, `[시각 / 레벨 / 모듈]` + 탭 + 스레드 + 탭 + 호출 지점 `Class::func (File.cpp:line)` + 탭 + 메시지. 헤더 `# Version : 2`, 없으면 Legacy(v1, 호출 지점 없음). 호출 지점은 파일·외부 뷰어용이며 dock에는 표시하지 않는다 |
| 7 | 파일 | `%LOCALAPPDATA%\NumeReal\Logs\DashOpti_YYYYMMDD_HHMMSS_PID.log`, 최근 30개 보존 |
| 8 | 설정 | QSettings(`NumeReal/DashOpti` 스코프) 저장, 실행 인자 `--log-*` override(환경변수는 두지 않는다 — VS 디버거 명령 인수로 콘솔 없이 쓰기 위함), 모듈별 레벨 지원 |
| 9 | 큐 | 유한이지만 넉넉하게: 256k + WARN 이상 예비 16k(레코드 약 300B → 최악 80MB 남짓). 어떤 레벨도 호출 스레드를 막지 않는다(생산자가 GUI 스레드일 수 있다 — 2026-09-10에 "INFO+ 손실 없음" 보장을 철회). 가득 차면 버리고, 워커가 다음 배치 끝에 WARN(App) 노트 한 줄로 레벨 구간별 건수와 유실 시각 구간을 남긴다(유실 위치 = 노트와 다음 줄 사이). 유실을 피해야 하면 자식 출력 읽기를 GUI 스레드에서 떼어 역압을 거는 것이 후속 선택지 |
| 10 | 외부 프로세스 출력 | Logger로만. 외부 프로그램의 줄은 레벨을 판정할 수 없으므로 stdout은 INFO, stderr는 ERROR로 두어 사용자 UI에 노출한다. 카테고리는 발신자인 exe가 정한다(`DashLog::moduleForExecutable`, ProcessJob·DashExtensionProcess가 exe 이름으로 Ext* 모듈 선택, 모르는 exe는 Process). 메시지는 원문 그대로(exe와 채널은 모듈·레벨 컬럼이 말해 준다). 모르는 exe(Process 모듈)만 `[proc=exe]`/`[daemon=exe]` 태그로 이름을 남기고, DashJobRunner는 `[job=runKey proc=…]`로 잡 컨텍스트를 남긴다. 수신부는 원문을 재기록하지 않고 도구 규약(`[GUI]`→INFO, `[PROGRESS]`, JSON)만 해석 |
| 11 | dock | 링 버퍼(2만 건) 보관, 타이머 배치 append. 사용자 창이므로 표시 범위 고정(2026-09-09 내부 공유): INFO 이상, 오픈소스 라이브러리(Qt·Vtk, `isExternalLibraryModule`)만 제외하고 외부 실행 파일(Ext*) 출력은 INFO라 보인다, 컬럼은 Time·Level·Module·Message. 레벨·모듈 필터 컨트롤과 Thread 열은 두지 않는다(외부 뷰어에서 본다). 검색(메시지 원문·레벨·모듈. 숨긴 Thread 열과 시각은 대상이 아니다)·자동 스크롤·Clear·Ctrl+C만. Time·Level·Module 폭은 실제 출력 문자열을 재서 고정하고, Message는 남은 폭을 채우는 고정 폭(2026-09-10: 세로 스크롤바 항상 표시로 뷰포트 폭을 안정시킴. 내용 폭 측정은 스크롤 위치에 따라 흔들려 폐기). 긴 메시지는 툴팁·Ctrl+C·외부 뷰어로 본다. 글자는 본문보다 1pt 작게. 모드 전환 자동 필터 없음. ModelSink도 Qt·Vtk 레코드는 보관하지 않는다(프록시가 늘 거부할 레코드로 링 버퍼가 밀리는 것을 막는다) |
| 12 | dock 경로 숨김 | 기본 켜짐, dock에 토글 없음. 숨김은 표시 셀에만 적용되고 툴팁·Ctrl+C 복사·파일은 원문이다. 개발자는 실행 인자 `--log-show-paths` 또는 QSettings `Log/DockStripPaths=false`로 켠다(인자 > 설정) |
| 13 | 구현 방식 | 자체 구현, Qt Core만 의존. 외부 라이브러리 없음 |
| 14 | 비정상 종료 flush | `QtFatalMsg` + `std::set_terminate` + `SetUnhandledExceptionFilter` 세 곳. FATAL은 곧 종료: 큐를 거치지 않고 호출 스레드에서 동기 기록하며, 공유 sink는 잠금을 잡았을 때만 쓴다(못 잡으면 예비 핸들로 FATAL 한 줄만). 직전 레코드 보존은 최선 노력, 보장 대상은 FATAL 한 줄 |
| 15 | QMessageBox 277곳 | 선별. 시스템 실패 통지만 notify API로 옮겨 ERROR 로그 동반. 입력 검증·information·question은 그대로. 경계 사례: 계산 도중 드러나는 요청 불가(예: Morphing K가 가용 노드 수를 넘음)는 입력 검증이 아니라 실패 통지로 보아 `DashNotify::error`(2026-09-10) |
| 16 | std::cout/cerr 74곳 | cout→DEBUG(구분선 삭제, 다중 줄 병합), cerr→ERROR(수동 접두어 제거), 내용상 경고는 WARN |

## 4. 모듈 목록

| 모듈 | 대응 코드 |
|---|---|
| App | main.cpp, DashManager, DashGadgetCodec, 테마·설정·스플래시, Logger 자체 메시지 |
| Project | DashProject, DashProjectManager, DashIOController, DashProjectWidget |
| Geometry | DashGeometryParameter(CAD), DashAIGeometryGeneration, model/geometry(DashMorphingUtils 제외), model/extensions/enterprise 컴포넌트 규칙, DashOcctViewWidget |
| Morphing | DashMorphingController, DashMorphingEngine, DashMorphingDoeExecutor, Handle·Gizmo 계열, DashNonDesignUtils, model/geometry/DashMorphingUtils, DashMorphingSettings |
| Condition | DashConditionParameterization |
| DataProcessor | DashAnalysisLauncher |
| ModelBuilder | DashModelBuilder, model/builder |
| ModelBuilderMCU | DashModelBuilderMCU |
| ModelRunner | DashModelRunner, DashDesignVariableModel |
| ModelRunnerMCU | DashModelRunnerMCU |
| Optimizer | DashOptimizer, DashTopOptPostprocessRunner |
| Analysis | DashDoeSampler, DashJobRunner, DashDoeConfigManager, DashAnalysisModelContext, model/preprocessor |
| Analyzer | model/analyzer, DashResultsAnalyzerWidget, view/analyzer |
| Process | controller/async(ProcessJob, ProcessKill), DashExtensionProcess(daemon) 자체 메시지와 카탈로그에 없는 exe의 원문 |
| NxCad | DashSolverNxCad |
| Rw | DashRwActor, DashRwDocument, DashRwDocumentHandle |
| Rendering | DashRenderingManager, InteractorStyle, Picking |
| View | DashMainWindow, 공용 위젯·dialog·delegate |
| Threading | DashThreadAffinity |
| Qt | `qInstallMessageHandler`로 유입되는 Qt 내부 메시지 |
| Vtk | `vtkOutputWindow`로 유입되는 VTK 내부 메시지 |
| ExtJournalLauncher | `DashOptiJournalLauncher.exe` (daemon) 원문 |
| ExtMcu | `DashOptiMCU.exe` (daemon) 원문 |
| ExtSensitivity | `DashOptiSensitivityEngine.exe` (daemon) 원문 |
| ExtMbd | `DashOptiMBD.exe` motion-writer/launcher 원문 |
| ExtDeepOpt | `DashOptiDeepOpt.exe` 원문 (ModelBuilder·ModelRunner·Optimizer가 실행) |
| ExtTopOpt | `DashOptiTopOptPostprocessor.exe` 원문 |
| ExtEncodeHeader | `encode_header_tool.exe` 원문 |
| ExtCadNx | `DashOptiCADNX.exe` (daemon) 원문. GUI 파사드의 상태 메시지는 NxCad |

기존 dock의 모듈 태그(ModelBuilder / ModelBuilderMCU / ModelRunner / ModelRunnerMCU / AnalysisLauncher / DataProcessor / ResultsAnalyzer / NX CAD)와 1:1로 대응한다. 같은 기능의 model과 widget은 같은 모듈에 속한다. 레이어는 모듈이 아니다.

## 5. 레벨과 매핑

| 레벨 | 용도 | 기존 호출의 매핑 |
|---|---|---|
| TRACE | 최하위 진단. 앱 코드에서 현재 쓰는 곳 없음 | 외부 프로세스 출력은 stdout INFO / stderr ERROR로 기록해 사용자 UI에 노출한다 |
| DEBUG | 개발자 진단 | `qDebug`, `std::cout` |
| INFO | 사용자에게 보이는 진행 상황 | `emit logMessage(...)` 414곳 |
| WARN | 계속 진행 가능한 이상 | `qWarning` |
| ERROR | 실패 | `qCritical`, `std::cerr`, notify API의 error |
| FATAL | 이후 프로세스가 종료됨. 동기 flush 트리거 | `qFatal`, set_terminate, SEH |

INFO 이상이 dock에 보이므로 기존 `qWarning`/`qCritical` 578곳이 처음으로 사용자 화면에 노출된다. 치환 시 문구를 함께 검토한다.

## 6. 라우팅

| sink | 최소 레벨(기본) | 비고 |
|---|---|---|
| 파일 | TRACE | 전부 기록(자식 프로세스 출력 원문 포함). 파일은 원본이고 걸러 보는 것은 외부 뷰어의 일이다(2026-09-09 내부 공유). 줄이려면 설정·실행 인자로 하한을 올린다 |
| Log dock | INFO 고정 | 오픈소스 라이브러리(Qt·Vtk)만 제외. 외부 실행 파일(Ext*) 출력은 INFO라 그대로 보인다. 표시 필터 컨트롤 없음, 걸러 보는 것은 외부 뷰어 |
| 팝업 | 자동 없음 | notify API(`DashNotify::error/warning`) 명시 호출로만. FATAL도 팝업하지 않는다(크래시 컨텍스트에서 Qt 위젯을 쓰지 않는다) |

notify API(`DashNotify::error / warning`)는 QMessageBox 표시와 ERROR/WARN 로그 기록을 함께 수행하고, 워커 스레드에서 호출되면 GUI 스레드로 마샬링한다. Logger는 팝업을 띄우지 않는다. 배치(DoE) 실행 중 모달 폭주를 막기 위한 분리다.

## 7. API

```cpp
DASH_LOG_TRACE(Process) << line;
DASH_LOG_DEBUG(Analyzer) << "Need at least 2 variables, got" << N;
DASH_LOG_INFO(Project)   << QString("Failed to create new Set in %1").arg(categoryName);
DASH_LOG_WARN(Analysis)  << ...;
DASH_LOG_ERROR(Morphing) << ...;
DASH_LOG_FATAL(App)      << ...;
```

- 내부는 `QDebug(&QString)`이라 기존 `qDebug`에 넣던 모든 타입이 그대로 동작한다.
- 매크로가 `Logger::enabled(level, module)`을 먼저 검사하므로 비활성 레벨에서는 우변 평가가 일어나지 않는다.
- 호출 지점(`__FILE__/__LINE__/__FUNCTION__`)은 매크로가 채워 파일 포맷 v2의 세 번째 컬럼에 기록된다(8절). dock에는 표시하지 않으므로 사용자 노출 문구는 모듈과 문구만으로도 발생 지점이 구분되게 다듬는다.
- 기존 `"[DashPearsonPlotter]"` 류 수동 접두어는 모듈 필드가 대신하므로 제거한다.

## 8. 레코드 포맷

```
[2026-09-08 14:02:11.482 / WARN / Analyzer]	1a2c	DashPlotter::build (DashPlotter.cpp:88)	Need at least 2 variables, got 1
[2026-09-08 14:02:15.907 / ERROR / Vtk]	5f10		vtkXMLUnstructuredGridReader (000001F3A2B4C5D0): Error opening file D:/proj/case_003.vtu\nERROR: In vtkXMLUnstructuredGridReader.cxx, line 289
[2026-09-08 14:03:02.115 / INFO / ExtMbd]	1a2c		[job=doe_017 case=case_003] Iteration 12  residual 3.2e-5
```

- 포맷 v2(2026-09-09). 컬럼 4개, 탭 구분: `[시각 / 레벨 / 모듈]`, 스레드 ID(hex), 호출 지점 `Class::func (File.cpp:line)`, 메시지. 호출 지점은 `DASH_LOG_*` 매크로가 `__FILE__/__LINE__/__FUNCTION__`으로 채우고(파일은 이름만), Qt 핸들러는 `QMessageLogContext`를 넘긴다. 자식 프로세스 출력처럼 출처가 없는 레코드는 빈 컬럼이다. dock에는 이 컬럼을 표시하지 않는다(파일과 외부 뷰어용). 메시지에는 탭이 올 수 있으므로 파서는 앞의 세 탭까지만 컬럼으로 자른다.
- 세션 헤더 둘째 줄에 `# Version : 2`를 쓴다. 이 줄이 없는 파일은 Legacy(v1, 호출 지점 컬럼 없는 3컬럼)로 읽는다.
- 패딩하지 않는다. 구분자는 ` / ` 한 칸씩. 비고정폭 폰트(메모장)에서는 패딩이 오히려 `]` 위치를 어긋나게 해 제거했다(2026-09-08 테스트 후 결정).
- 메시지 안의 개행은 `\n`으로 이스케이프해 한 줄 한 레코드를 유지한다.
- 컨텍스트(jobId 등)는 메시지 앞 `[key=value]` 태그로 넣는다. 컬럼은 v2의 호출 지점까지로 고정하고 더 늘리지 않는다. 늘려야 하면 `# Version`을 올린다.
- 인코딩 UTF-8. 파일 첫 줄에 세션 헤더(앱 버전, 빌드 구성, Qt/VTK 버전, OS)를 기록한다.
- 시각과 스레드 ID는 `log()` 호출 시점에 캡처한다. 큐 대기 시간이 기록 시각에 섞이지 않게 하기 위함이다. 호출 지점 문자열은 매크로의 정적 리터럴이면 `QByteArray::fromRawData` 참조(레코드마다 복사 없음), Qt 핸들러의 `QMessageLogContext`처럼 호출 동안만 유효한 문자열이면 깊은 복사로 담는다.
- 스레드 식별: 스레드가 세션에서 처음 기록하는 레코드 바로 앞에 `# Thread  : <tid> = <name>` 줄을 쓴다. 이름은 `DashLog::setThreadName()`으로 지정한 값 → GUI 스레드(정확히는 `Logger::start()`를 호출한 스레드) `main` → `QThread::objectName()` → QThread 클래스명 순으로 정한다. Qt6는 메인 스레드 objectName을 "Qt mainThread"로 자동으로 채우므로 main 판정이 objectName보다 앞선다. 레코드 컬럼은 tid(hex) 그대로이고 컬럼을 늘리지 않는다. 외부 뷰어와 dock의 Thread 열(기본 숨김. Ctrl+C 복사에는 포함)은 이 표로 tid 대신 이름을 보이며, 표에 없으면 tid를 그대로 보인다. QtConcurrent 풀 스레드는 작업 범위에서 `ThreadNameScope`로 이름을 붙여 역할을 알리고 작업이 끝나면 되돌린다(예: DOE analysis).
- dock은 파일을 파싱하지 않는다. Logger 스레드가 `LogRecord` 구조체를 dock sink에 직접 전달하고, 직렬화는 파일 sink에서만 일어난다.

## 9. 파일과 보존

- 디렉터리: `%LOCALAPPDATA%\NumeReal\Logs\`
- 파일명: `DashOpti_YYYYMMDD_HHMMSS_PID.log`. 실행 1회 = 파일 1개. 동시 실행은 PID로 분리된다.
- 보존: 시작 직후 Logger 스레드에서 오래된 파일부터 삭제해 최근 30개만 남긴다. `start()`의 소요 시간을 늘리지 않기 위해 워커에서 한다.
- 크기 상한은 두지 않는다. 기본 하한이 TRACE라 자식 프로세스 출력만큼 커지는 것은 감수한다. 보존 30개로 총량을 제한한다.
- 세 값 모두 QSettings 키로 두되 이번 단계에서 UI는 만들지 않는다.
- dock에 로그 폴더 열기 액션은 두지 않는다. 파일 열람은 외부 뷰어(`tools/logviewer/dash_log_viewer.py`)로 한다.

## 10. 설정

| 항목 | 저장 | override (실행 인자) |
|---|---|---|
| 로그 디렉터리 | QSettings `NumeReal/DashOpti` → `Log/Directory` | `--log-dir=<path>` |
| 파일 sink 레벨 | `Log/FileLevel` | `--log-level=<TRACE..FATAL\|OFF>` |
| dock 표시 레벨 | 고정 INFO(설정 없음). 링 버퍼 저장 하한 `Log/DockBufferLevel`(기본 INFO) | - |
| dock 경로 숨김 | `Log/DockStripPaths` (기본 true) | `--log-show-paths` |
| 모듈별 레벨 | `Log/Module/<Name>` | `--log-modules=Process=TRACE,Analysis=DEBUG` |
| 링 버퍼 크기 | `Log/DockBufferSize` (기본 20000) | - |
| dock 자동 스크롤 | `Log/DockAutoScroll` (기본 true, dock 체크박스가 저장) | - |
| 보존 개수 | `Log/KeepFiles` (기본 30) | `--log-keep=<N>` |

환경변수는 두지 않는다. 실행 인자는 Visual Studio 디버거의 "명령 인수"에 그대로 넣을 수 있어 콘솔을 열지 않고 쓸 수 있다. 형식은 `--옵션=값` 하나로 통일하고 모르는 인자는 무시한다. Logger는 QApplication 생성 전에 시작하므로 `main()`이 `argv`에서 직접 QStringList를 만들어 넘긴다.

기존 QSettings 스코프(`NohLab/DashOptiAnalyzer`, `YourCompany/DashApp`)는 쓰지 않는다. 스코프 통일은 W4의 몫이며 Logger는 그 분열에 의존하지 않는다.

## 11. 구조

```
utils/log/
  DashLog.h            진입 헤더(매크로·Logger·모듈·레벨을 한 번에 include)
  DashLogModule.{h,cpp} enum class + 이름 테이블, moduleForExecutable / isExternalLibraryModule
  DashLogLevel.{h,cpp} enum class + 이름 테이블·파싱
  DashLogSink.h        sink 인터페이스(minLevel / write / flush)
  DashLogFormat.{h,cpp} 레코드 직렬화(formatLine / formatHeader / formatSource), 개행 이스케이프
  DashLogRecord.h      { ts, level, module, threadId, message, srcFile/srcLine/srcFunction(호출 지점. QByteArray — 매크로의 정적 리터럴은 fromRawData 참조, Qt 핸들러의 QMessageLogContext는 깊은 복사), threadName(첫 레코드에만) }
  DashLogger.{h,cpp}   싱글톤. 큐, 워커 스레드, sink 등록, enabled(), writeFatal()
  DashLogMacros.h      DASH_LOG_* 매크로, 스트림 프록시
  DashLogFileSink.{h,cpp}
  DashLogQtHandler.{h,cpp}   qInstallMessageHandler 연결 (재진입 가드). Logger::start()/stop()이 Config::captureQtMessages로 설치·해제
  DashLogCrashFlush.{h,cpp}  set_terminate / SEH 필터. Logger::start()/stop()이 Config::captureCrashes로 설치·해제
  DashLogRecordModel.{h,cpp} 링 버퍼 QAbstractTableModel(RecordModel) + 표시 필터(FilterProxy). Qt Core만
  DashLogModelSink.{h,cpp}   Logger 스레드 → 타이머 배치 → RecordModel::appendBatch (GUI 스레드)
view/log/
  DashLogDockWidget.{h,cpp}  기존 m_logDock/m_logWidget 대체. 표시 범위 고정(INFO 이상, Qt·Vtk 제외, Time·Level·Module·Message),
                             검색 필터(메시지·레벨·모듈), 자동 스크롤, Clear, Ctrl+C 복사, 경로 숨김(설정 전용). 레벨별 색은 delegate.
                             Message 열은 남은 폭을 채우는 고정 폭(세로 스크롤바 항상 표시)
view/common/
  DashNotify.{h,cpp}         notify API. error/warning(module, parent, title, text): "[popup] title: text"를
                             ERROR/WARN으로 기록하고 QMessageBox 표시. 워커 스레드에서는 팝업을 GUI 스레드에 큐잉
controller/
  DashVtkLogBridge.{h,cpp}   vtkOutputWindow 서브클래스
tools/logviewer/
  dash_log_viewer.py         tkinter 단일 파일 뷰어(v1/v2 판별, 레벨·모듈·스레드 필터, 검색, Follow, --dir, --selftest)
```

- `utils/log/`는 QtWidgets·VTK를 include하지 않는다. tests/에 Qt Core만으로 링크된다.
- 호출 스레드가 하는 일: 레벨·모듈 검사 → QString 조립 → 레코드 이동 → mutex 1회 → 큐 push.
- Logger 스레드가 하는 일: 큐 drain → 각 sink write(파일 sink는 직렬화·쓰기, dock sink는 모아서 타이머 배치로 GUI 스레드에 넘김) → flush.
- 큐는 mutex + condition variable. lock-free는 쓰지 않는다.
- Logger는 최근 레코드(`Config::replayCapacity`, 기본 5000)를 보관한다. dock처럼 기동 도중에 만들어지는 sink는
  `addSink(sink, replayRecent=true)`로 그 이전 기록(앱 시작, 위젯 생성 경고 등)을 먼저 받는다.
- Logger 미시작 상태(테스트 실행 파일, DashUiPreview, 정적 소멸자 이후)의 호출은 stderr fallback으로 안전하게 처리한다.

## 12. 수명

```
main()
  Logger::start(config)            // QApplication 생성 전. 파일 열기, 보존 정리 예약, 핸들러 설치
  QApplication app
  ...
  int rc = app.exec();             // aboutToQuit 핸들러(ProcessJob::cancelAllRunning)는 반환 전에 완료
  Logger::stop();                  // 관문 복원, 큐 drain, 종료 표식 기록 (mainWindow는 delete하지 않는다 — 아래 참조)
  return rc;
```

관문(Qt 메시지 핸들러, 크래시 핸들러)은 `Config::captureQtMessages`·`chainQtHandler`·`captureCrashes`로 `start()`가 설치하고 `stop()`이 이전 핸들러로 되돌린다. 기본값은 모두 false다 — QTest처럼 자체 메시지 핸들러를 쓰는 실행 파일이 `start()`만으로 관문을 잃지 않게 하기 위함이며, `main()`이 셋을 켠다. 설치는 `m_running`을 세운 뒤에 한다(설치 직후 들어오는 Qt 경고가 fallback이 아니라 큐로 가도록). 파일 열기에 실패하면 `start()`는 false를 돌리되 워커는 시작하고, 사유를 ERROR(App) 레코드로 재생 버퍼에 직접 넣는다 — 파일 sink가 없으면 게이트가 전부 Off라 매크로로는 남길 수 없기 때문이다. 기동 뒤 만들어지는 dock이 `addSink(replayRecent=true)`로 이 레코드를 받는다. 큐 mutex가 `timed_mutex`인 것은 `writeFatal()`이 크래시 컨텍스트에서 시간 제한으로만 잠금을 시도하기 위해서다. `stop()`은 큐 잠금 아래에서 `m_running`을 내리고 `log()`는 같은 잠금 아래에서 재확인하므로, 첫 검사와 push 사이에 `stop()`이 끝난 생산자의 레코드는 큐에 남지 않고 미시작 fallback(stderr)으로 간다. `start()`는 큐를 비운 채 시작한다.

비정상 종료 세 지점(`QtFatalMsg` 핸들러, `std::set_terminate`, `SetUnhandledExceptionFilter`)은 Fatal 레코드 한 줄을 `log()`에 넘기고 곧 abort한다. Fatal은 큐에 넣지 않는다(가득 찬 큐에서의 대기, 죽은 워커에 대한 의존이 없다). `writeFatal()`은 sink 잠금을 100ms 시도해 성공하면 큐를 비우고 FATAL을 sink로 정상 기록하고(직전 레코드 보존, 워커와 경합 없음), 실패하면 — 워커가 sink를 쓰는 중이거나 잠금을 쥔 채 죽었거나 워커 스레드 자신이 크래시한 경우 — sink 상태를 건드리지 않고 `start()`에서 미리 열어 둔 예비 append 디스크립터로 FATAL 한 줄만 파일 끝에 붙인다. 워커 스레드 자신이 크래시한 경우는 자기 소유 잠금에 `try_lock`을 시도하지 않고 바로 이 경로로 간다. 어느 경우도 동기화 없는 메모리 동시 쓰기와 무한 대기가 없고, 파일 자체는 본 핸들과 예비 핸들을 모두 OS append 전용(`FILE_APPEND_DATA` / `O_APPEND`)으로 열어 두 핸들의 쓰기가 서로 덮어쓰지 않는다(`openAppendFd`). 크래시 컨텍스트에서의 힙 할당과 Qt 호출은 최선 노력이다. 메시지 조립은 C 포맷팅으로 하되 레코드 직렬화 자체는 QString을 거친다. 미니덤프 생성은 범위 밖이다.

검증: Dev 빌드에서 실행 인자 `--log-crash-test=av|terminate|qfatal`로 실행하면 Logger 시작 직후 레코드 6줄을 남기고 해당 방식으로 죽는다(`runCrashSelfTestIfRequested`). 세 경로 모두 직전 레코드와 FATAL 한 줄이 파일에 남고 `# Stopped` 푸터가 없는 것을 2026-09-08에 확인했다(당시는 큐 flush 방식). 잠금 성공·실패 두 경로는 `test_dash_logger`의 `fatalIsSynchronousAndLockSafe`가 검증한다. 미처리 C++ 예외는 MSVC에서 SEH 필터(0xE06D7363)와 set_terminate가 순서대로 둘 다 호출되어 FATAL이 두 줄 남는다. C++ `try/catch`는 access violation을 잡지 못하므로(`/EHa` 없음) 검증 대상은 핸들러 자체다.

mainWindow는 기존 코드와 같이 `delete`하지 않는다(종료 시 소멸자 경로가 한 번도 실행된 적이 없어 별도 검증이 필요한 변경이다). Logger는 `exec()` 반환 직후 멈춘다.

## 13. 치환 범위

| 대상                                     | 수량         | 처리                                       |                   |
| -------------------------------------- | ---------- | ---------------------------------------- | ----------------- |
| `qDebug/qWarning/qCritical/qInfo`      | 약 1,090    | `DASH_LOG_*` 직접 치환, 모듈은 디렉터리·클래스 매핑표로 부여 |                   |
| `std::cout/cerr`                       | 74         | DEBUG/ERROR 치환, 구분선 삭제                   |                   |
| `emit logMessage(...)` 및 시그널 선언        | 414 + 8클래스 | `DASH_LOG_INFO` 치환, 시그널 삭제               |                   |
| DashMainWindow의 connect/disconnect 블록  | 24          | 삭제                                       |                   |
| `DashMainWindow::logMessage()`         | 1          | dock sink로 대체                            |                   |
| `QMessageBox` 호출 | 277 | 선별하여 notify API로 이동: critical 23 전부 + 시스템 실패 통지 warning 54 = 77곳. 입력 검증·information·question은 그대로 |
| 자식 프로세스 출력 줄 | 3 지점 | ProcessJob과 DashExtensionProcess는 exe 이름으로 정한 Ext* 모듈로 원문을 stdout INFO / stderr ERROR로 기록(태그 없음. 모르는 exe → Process 모듈일 때만 `[proc=exe]`/`[daemon=exe]`), DashJobRunner의 motion-writer/launcher는 INFO(ExtMbd, stderr는 ERROR) + `[job=runKey proc=…]`. 수신부(ModelBuilder·ModelRunner·Optimizer·TopOpt)의 원문 DEBUG 재기록은 제거. DashSolverNxCad의 logLine은 원문이 아닌 상태 메시지라 INFO(NxCad) 유지 |
| `DASH_ASSERT_MAIN_THREAD`의 `qCritical` | 1          | `DASH_LOG_ERROR(Threading)`              |                   |

## 14. 작업 순서

1. `utils/log/` 코어 + 파일 sink + 단위 테스트(순서 보존, 스레드 안전, 레벨·모듈 필터, 큐 overflow 정책). tests/CMakeLists.txt에 추가.
2. main.cpp 수명 연결, Qt 메시지 핸들러, 비정상 종료 flush, VTK 브리지. 이 시점부터 릴리스에서 파일 로그가 남기 시작한다.
3. dock sink와 dock 위젯 교체(링 버퍼, 배치 append, 검색, 경로 숨김 기본 켜짐·설정으로만 해제).
4. 호출부 치환. 디렉터리 단위로 진행하고, 한 디렉터리 안에서 qDebug 계열 → cout 계열 → logMessage 시그널 제거 순서.
5. notify API와 QMessageBox 선별 이동.
6. 자식 프로세스 출력 연결(stdout INFO / stderr ERROR, Ext* 모듈).
7. 뷰어 개선(강조 표시, 검색, 자동 스크롤 일시정지, 과거 파일 열기)은 후속.

## 15. 백로그 대응

| 백로그 항목 | 관계 |
|---|---|
| W1 파일 로깅 싱크 (#220) | #220은 코드 병합 없이 종결됨. 본 설계가 W1을 대체한다. "호출부 무수정 회수"에서 "직접 치환"으로 방식이 바뀌고, 호출 지점은 `DASH_LOG_*` 매크로가 직접 채우므로 `QT_MESSAGELOGCONTEXT`는 정의하지 않는다(Qt 내부 경고의 호출 지점은 Debug 빌드에서만 채워진다) |
| W3 외부 프로세스 안전핀 | 자식 출력 `fromLocal8Bit→fromUtf8` 18곳은 자식 출력 유입 경로의 디코딩 문제. 데몬 Crashed 무음 실패는 ERROR 로그와 notify로 가시화된다 |
| W4 설정 영속화 | Logger 설정은 새 스코프 `NumeReal/DashOpti`에 둔다. 기존 두 스코프의 통일은 W4에서 |
| W12 실패 통지 승격 | notify API가 W12의 정적 래퍼에 해당한다. "사용자 개입 필요 → 모달, 그 외 → dock"의 규칙이 라우팅 결정 4·15와 일치한다 |
| 부록 코멘트 6 (stderr 처리) | 자식 stdout은 INFO, stderr는 ERROR로 전량 기록하므로 실패 메시지 조립과 무관하게 원문이 파일에 남는다. 무제한 누적 버퍼 문제는 유한 큐와 링 버퍼로 Logger 측에서는 발생하지 않는다. 소비자 측 `m_errorOutput` 상한은 W12 범위 |
| W9 회귀 안전망 | Logger 코어 단위 테스트를 tests/에 추가한다 |
| #64 Crash Debug | FATAL flush 세 지점이 크래시 직전 로그를 보존한다 |

## 16. 범위 밖

- 미니덤프 생성
- 잡별 로그 파일
- 로그 설정 UI
- QSettings 스코프 통일(W4)
- 다국어(W18)
