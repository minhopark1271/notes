# DashGUI2 비동기 실행 패턴 — 외부 프로세스·내부 장시간 작업 통합 설계 검토 (W6·W10 상세)

> 원본: 사전조사 Issue #194 — 본문을 이 페이지로 이관한 뒤 Issue 삭제 (2026-08-24). **본 페이지가 정본**

> 연관 Issue: #64 (Crash Debug — 재진입 크래시 계급의 원천이 본 문서의 대상 실행 모델)\
> 기반 문서: [200-3-prioritized-backlog](200-3-prioritized-backlog.md) (W6·W10 — 본 문서는 그 상세 설계) · [198-1-improvement-roadmap](198-1-improvement-roadmap.md) (진단 ②·Phase 1\~2) · [195-1-backlog-code-evidence](195-1-backlog-code-evidence.md) (W6·W10 실증)\
> 자매 문서: [193-1-async-execution-models](193-1-async-execution-models.md) — 본 문서 용어(이벤트·Job·코루틴·스레드의 층위 구분, Qt 시그널, 콜백 발생 경우, Job 상태머신)의 개념 해설 (개정 2) · [201-1-qprocess-antipattern-catalog](201-1-qprocess-antipattern-catalog.md) — 2-2절 표의 패턴 축 전개: QProcess 우회 지점 전수 카탈로그 P1\~P8 (개정 6)\
> 분석 시점: 2026-07-14, 브랜치 `dev` — 실행 경로·스레딩 인프라 전수 재조사 (라인 앵커는 분석 시점 워킹트리 기준, 유효기간 있음)\
> 발단: 검토의견 — "W6·W10은 외부 모듈을 비동기로 실행(Job→콜백 / 이벤트 / 코루틴)하고 메인스레드는 언제든 대기 상태로 두는 것이 목표로 이해됨. 이때 외부 프로세스 외에 내부에도 오래 걸리는 작업(read·write·변환 — DLL 실행도 포함?)이 있고, 이를 비동기 래퍼로 싸서 실행하는 패턴도 있어야 할 것"\
> 개정 1: 2026-07-14 — 판정 ④ 신설(6절): "뷰·컨트롤러가 타이트하게 결합돼 있어 컨트롤러 실행부를 떼기 어렵지 않은가"라는 추가 검토의견에 대해, 뷰 분리(W19\~W21)를 미룬 채 실행부만 선행 비동기 전환하는 것이 **가능**하다고 판정 — 실행 평면의 뷰 접촉 실측(배치 오케스트레이터 위젯 참조 0건), 시그널 구동은 스레드를 만들지 않아 결합을 건드리지 않음, 워커 축만 Job 경계 국소 절단 3규칙으로 해결. 이후 절 번호 1칸 이동(구 6절→7절, 구 7절→8절)\
> 개정 2: 2026-07-14 — 개념 해설 자매 문서 [193-1-async-execution-models](193-1-async-execution-models.md) 신설·상호 링크 (본 문서 내용 불변 — 헤더 링크만 추가)\
> 개정 3: 2026-07-14 — 4절 Job 계약에 "구독" 추가 (3종→4종): 시그널의 통지 유실성(관찰자 패턴 — 재생 없음)에서 귀결되는 규칙 3건 — "connect 먼저 start 나중" · 상태 pull(`state()`) 병행 제공 · 토픽형 전역 이벤트 버스 금지(객체 짝 연결 유지 — 전역 결합의 이벤트 평면 재현 방지). 원리 해설은 자매 문서 3-4절(개정 1)과 동기화\
> 개정 4: 2026-07-14 — 4-1절 "취소·실패 사용자 정책" 신설: 검토 피드백("사용자의 작업 취소 및 실패 관리 정책이 중요") 대응 — 계약 4종(메커니즘) 위의 **정책 계층** 5건 판정(P1 완료분 보존·중단분 산출물 폐기, P2 배치 취소 = 가장 이른 중단 지점 + 잔여 케이스 미시작, P3 continue-on-error + 연쇄 실패 차단기, P4 취소 UX 즉시 반응 — "UI 즉시 해방"만 약속, P5 자동 재시도 없음). 0절 질문 5·1절 결론 표 7행 추가\
> 개정 5: 2026-07-15 — 검토 질문 2건 반영: 5-1절에 일괄 래핑 배제 근거 추가("오래 걸리건 말건 전부 래핑이 유지관리에 유리하지 않은가" — 아니다: 짧은 호출 래핑 = 재진입 창 재배포, 균일성은 **"메커니즘은 선별, 형태는 일괄"** 로 확보), 5-3절에 "워커 투입" 정의 명시(= WorkerJob 도입, 서브태스크 e — 외부 축 무관)\
> 개정 6: 2026-07-15 — 검토 질문("현재 잘못 구현된 QProcess 패턴 전수 나열") 대응 자매 문서 [201-1-qprocess-antipattern-catalog](201-1-qprocess-antipattern-catalog.md) 신설·상호 링크: 2-2절 위치·우선순위 축 목록을 패턴 축(P1 기동 동기 대기 \~ P8 동기 반환 API 계약) 8종으로 재편성 + 지점 전수 보강 (본 문서 내용 불변 — 헤더 링크만 추가)\
> 개정 7: 2026-07-15 — 검토의견("5-3절 선결 조건 5건은 별도 과제로 면밀히 분석·처방된 다음에 접근") 채택: 5건을 실측·실패 시나리오·처방 대안 비교·검증 기준 수준으로 전개한 [203-2-worker-preconditions-analysis](203-2-worker-preconditions-analysis.md) 신설 (서브태스크 d 의 상세 설계 = 서브태스크 e 의 게이트). 조사 중 **현재도 잠재하는 버그 2건 신규 발견** — Registry `getOrLoad` 의 emplace 실패 시 dangling 반환 경로, cout rdbuf 스왑의 예외 시 복원 누락 (본 문서 내용 불변 — 헤더·5-3절 링크만 추가)\
> 개정 8: 2026-07-20 — 7절 서브태스크 목록 a\~f 각 항목에 출처·상세 문서 교차 참조 부기 (a\~c 외부 축 = 6-2절·[201-1-qprocess-antipattern-catalog](201-1-qprocess-antipattern-catalog.md), d = 5-3절→[203-2-worker-preconditions-analysis](203-2-worker-preconditions-analysis.md) D1\~D5, e = 5-3절 개정 5 "워커 투입" 정의, f = 5-4절). 항목 내용 불변 — 참조 표기만 추가\
> 개정 9: 2026-07-20 — 7절 서브태스크 목록 앞에 W10 계층도 추가 (2축 분기 = 외부 ProcessJob·스레드 0 / 워커 WorkerJob·스레드 풀, Job 상태머신 = 공통 시그널 표면, d 선결 조건 = 워커 축 게이트). 서브태스크 a\~f·의존 관계 불변 — 시각화만 추가\
> 개정 10: 2026-07-21 — CI 미진행 결정(백로그 개정 29) 반영: 5-4절 W10 DoD의 "W9 게이트 봉인"을 "grep 수동 검증(W9 자동 게이트는 선택)"으로 완화. 판정·설계 불변 — 표기만 조정

---

## 0. 목적과 범위 — 다섯 가지 질문

이 문서는 위 검토의견을 코드 실측으로 검증하고, 다음 다섯 질문에 판정을 기록한다.

1. **이해 확인** — "외부 모듈 비동기 실행 + 메인스레드 상시 대기 상태"가 W6·W10의 목표가 맞는가?
2. **완료 처리 방식** — Job을 던지고 콜백을 받는 것 / 이벤트(시그널)로 처리하는 것 / 코루틴으로 처리하는 것 중 무엇을 표준으로 삼는가?
3. **내부 작업 비동기 래퍼** — 외부 프로세스가 아닌 내부 장시간 작업(read·write·변환)도 비동기 래퍼가 필요한가? **DLL 실행도 포함인가?**
4. **(개정 1) 실행부 선행 전환 가능성** — 뷰와 컨트롤러가 타이트하게 결합된 현 상태에서, 뷰를 떼는 작업은 W19\~W21로 두고 **컨트롤러의 실행부만 먼저 비동기로 전환하는 것이 가능한가?**
5. **(개정 4) 취소·실패 사용자 정책** — 작업 취소와 실패 관리에 대한 **사용자 관점 정책**(취소 시 부분 결과 처리·배치 취소 범위·실패 시 계속/중단·재시도)이 설계에 고려되어 있는가?

범위 주의: 본 문서는 백로그의 작업 항목·착수 창·freeze 산정을 **바꾸지 않는다**. W10 본문의 한 줄("in-process 장시간 연산만 선별 워커화")을 상세 설계로 푼 것이며, 검토의견의 채택 기록이다.

## 1. 결론 먼저

| # | 질문 | 판정 |
|---|---|---|
| 1 | 목표 이해 | **맞음** + 정밀화 1건: "비동기 실행"의 1차 수단은 스레드가 아니라 **시그널 구동**(QProcess는 본래 비동기 — 로드맵 원칙 2). "메인스레드 대기 상태" = 이벤트 루프 상주(응답 가능), blocked 대기가 아님 |
| 2 | 완료 처리 방식 | **Qt 시그널(이벤트) 기반 Job 상태머신이 표준** (W10 정의 그대로). C 콜백은 외부 API 경계 어댑터로만(수신 즉시 시그널 변환), 코루틴은 **보류**(Qt 5.15 + QCoro 최신판 Qt 6.8+ 전용 — 배타적 선택이 아니므로 나중에 additive 승격 가능) |
| 3 | 내부 작업 래퍼 | **검토의견 타당 — 실측으로 강하게 뒷받침** (모프 DLL·reader DLL·KPI 파싱 전부 위젯 슬롯에서 GUI 스레드 동기 실행, 2-3절). 단 "전부 래퍼"가 아니라 **4분류 선별**(5-1절). **DLL 실행 포함** — 스레드 안전성 3등급으로 처리(5-2절) |
| 4 | 실행부 선행 전환 (개정 1) | **가능** — 외부 축(시그널 구동)은 스레드를 만들지 않아 뷰 결합을 아예 건드리지 않고, 실행 평면의 뷰 접촉은 실측상 이미 거의 없다(배치 오케스트레이터 위젯 참조 0건). 워커 축만 Job 경계 국소 절단 3규칙(입력 스냅샷·실행 중 위젯 접근 금지·출력 시그널)이면 충분 — 전면 뷰 분리(W19\~W21) 선행 불요, 오히려 실행부 비동기화가 뷰 분리의 정지 작업(6절) |
| 5 | 선결 조건 | 워커 투입 전 공유 상태 정리 5건 필수(5-3절) — 이것 없이 스레드부터 넣으면 **프리즈가 레이스로 바뀐다** |
| 6 | 백로그 영향 | 새 작업 항목 없음 — W10 내부 구조화(서브태스크 분할 제안 7절). 착수 창·freeze 불변 |
| 7 | 취소·실패 사용자 정책 (개정 4) | **메커니즘(전파·통지)은 기존 계약 4종이 커버, 사용자 정책 계층 5건은 공백이었음 — 4-1절로 신설**: 완료분 보존·중단분 폐기(P1), 배치 취소 = 가장 이른 지점 중단 + 잔여 미시작(P2), continue-on-error + 연쇄 실패 차단기(P3), 취소 UX 즉시 반응 — "UI 즉시 해방"만 약속(P4), 자동 재시도 없음(P5) |

## 2. 실측 — 현재 무엇이 어디서 막히나 (2026-07-14 재조사)

### 2-1. 스레드 구조 한 장 요약

| 프리미티브 | 사용량 | 비고 |
|---|---|---|
| `QtConcurrent::run` + `QFutureWatcher` | **1곳** — `DashAnalysisLauncher.cpp:233` (DOE 샘플링 수학 연산) | 유일한 진짜 워커. 정작 무거운 DLL 작업은 미포함 |
| `moveToThread` / `QThread` 서브클래스 / `QThreadPool` / `QRunnable` / `std::thread` / `std::async` | **0건** (grep 전수 확인) | 동시성 전략 사실상 부재 |
| `std::mutex` | 1곳 — 컨텍스트 레지스트리 **맵만** 보호 (`DashAnalysisModelContextRegistry.cpp:16,25,42`) | 내용물·DLL 로드는 락 밖 |
| `QMutex` | 1곳 — DOE 상태 JSON read-modify-write (`DashAnalysisLauncher.cpp:977`) | |
| `processEvents` | 59회/10파일 (모델 계층 41회) | 프리즈 위장 계층 — 2-4절 |
| `QProgressDialog` / `setOverrideCursor` | **0건** | 정식 진행 UI 부재 |

### 2-2. 외부 프로세스 축 (W6) — 인프라는 이미 비동기, 호출자가 우회한다

완성형 비동기 인프라가 **이미 존재**한다:

- `DashExtensionProcess`: 직렬 명령 큐(`sendCommand`→`m_commandQueue`) + 완료 시그널(`commandCompleted`/`commandFailed`), 마커 파싱은 `readyReadStandardOutput` 슬롯에서 (`DashExtensionProcess.cpp:135-140, 256-289`).
- `DashSolverNxCad`: 도메인 큐 API(`enqueueLoadPrt:122`/`enqueueUpdatePrtGeometry:144`) + 도메인 완료 시그널(`loadPrtCompleted`/`updatePrtGeometryCompleted`).
- FE 솔버(Ansys/Abaqus/fe-safe): C API 완료 콜백 → `QMetaObject::invokeMethod(Qt::QueuedConnection)` 마샬링 → 메인 슬롯 (`DashJobRunner.cpp:2015, 1170, 1178`) — **GUI 블로킹 0, 모범 사례**.

문제는 이 시그널을 **우회하는 호출자들**이다. GUI 스레드 블로킹 지점 총목록(재조사):

| 우선순위 | 위치 | 블로킹 유형 | 최대 지속 | 담당 |
|:---:|---|---|:---:|:---:|
| ★★★ | `DashMorphingDoeExecutor.cpp:304-375` `Execute` 루프 | 순수 동기 CPU(모핑) — `processEvents`조차 없음, UI 완전 정지 | N케이스 × 수초\~ | W10 |
| ★★★ | `DashJobRunner.cpp:2670-2673` `runWbpjDoeAsync` | `enqueueUpdatePrtGeometry` 직후 **`waitForFile` 폴링** — 완료 시그널 무시, 파일시스템으로 감지 | 케이스당 600s | W6 |
| ★★★ | `DashExtensionProcess.cpp:153-159` `startDaemon` | `waitForReadyRead(300)` busy-wait 루프 — `[READY]` 대기 | NX 120s (`DashSolverNxCad.cpp:16`) | W6 |
| ★★☆ | `DashJobRunner.cpp:696-707` motion-writer | `waitForFinished(500)`+`processEvents` 루프 | 300s | W10 |
| ★★☆ | `DashJobRunner.cpp:604-657` `waitForVtuFileComplete` | `msleep(100)`+`processEvents` 폴링 | 60s | W10 |
| ★★☆ | `DashJobRunner.cpp:1561-1676` dfsxml 모핑+MBD 루프 | 동기 호출+폴링 조합, `msleep(1000)` 고정 슬립 포함(`:1576`) | 누적 | W10 |
| ★☆☆ | `DashSolverNxCad.cpp:124-126,147-149` 첫 enqueue | 데몬 미기동 시 `startDaemon` 동기 부팅 유발 | 120s | W6 |
| ★☆☆ | `DashManager.cpp:157` `enqueueLaunch` | Journal 데몬 부팅 busy-wait | 15s | W6 |
| ★☆☆ | `DashExtensionProcess.cpp:143,179-182,354,359,381` | 기동/종료/one-shot `waitFor*` | 2\~300s | W6 |
| ☆ | `DashJobRunner.cpp:459,685,848,948` / `DashModelBuilder.cpp:637,1239` / `TopOptPostprocessDialog.cpp:1794,2157` | 기동·종료·취소 `waitFor*` | 3\~30s | W6/W10 |

핵심 대비 — **같은 파일 안에 정답이 이미 있다**: `runDirectJobs`의 .wbpj 경로는 `enqueueLoadPrt` 후 `loadPrtCompleted` 시그널에 람다를 `Qt::QueuedConnection`으로 연결해 완료 시 다음 단계를 진행한다 (`DashJobRunner.cpp:2326-2336`) — GUI 블로킹 0. `runWbpjDoeAsync`(`waitForFile` 폴링)와 목적이 같은 **비동기 참조 구현**이다.

잠재 위험 API 1건: `runBlocking`은 헤더 주석에 "Caller must NOT be the GUI thread"(`DashExtensionProcess.h:106`)라고 명시돼 있으나 워커 스레드가 0개인 현 구조에서 호출자는 결국 GUI 스레드가 된다 (현재 직접 호출처 없음 — 휴면 지뢰).

### 2-3. 내부 작업 축 (검토의견 대상) — GUI 스레드에서 도는 장시간 작업 전수

| # | 작업 | 진입 경로 (전부 GUI 스레드) | DLL/라이브러리 |
|---|---|---|---|
| 1 | 모핑 실행(단건) | 버튼 슬롯 `DashModelRunnerWidget.cpp:501` → `DashModelRunner.cpp:2121` → `DashManager::ExecuteMorphing`(`DashManager.cpp:314-343`) → `Morph()` 동기 호출 | `DashMR::OperatorMorph` |
| 2 | 모핑 프리뷰(N개 루프) | `DashOptimizerWidget.cpp:1911` → `DashOptimizer.cpp:1286` — 루프에 `processEvents`(`:1913,1938`) | `DashMR::` |
| 3 | 모핑 배치 DOE | `DashJobRunner.cpp:1561` → `MorphFromDoeSamples`(`DashManager.cpp:870`) → `ExecuteOneSample` 순차 루프 | `DashMR::` |
| 4 | FE 모델 파싱(.dat) | 위젯 10여 곳 → `Registry::getOrLoad` → `loadAnalysisModelFromFile` → `reader.Update()`(`DashAnalysisModelContext.cpp:312`) | `DashRW::AnalysisReader` |
| 5 | Abaqus .inp 로드 | 동일 → `module->load_contents`(`:855`) | `dash::rw::` |
| 6 | INP/DAT 내보내기·직렬화·메시 갱신 | `abaqusExportInp:460`·`serialize`·`exportToAnalysisInput`·`abaqusUpdateMeshPoints:434`·`UpdatePartFromName` | `DashRW::`/`dash::rw::` |
| 7 | 결과(RST) 파싱·KPI 추출 | `DashDataProcessor.cpp` process* 7종(`:1466,2049,3049,3491,3823,4104,4383`) — `processEvents` 13곳 산재 | 내부 preprocessor |
| 8 | VTU/VTK 쓰기 | `DashManager.cpp:862` `writer->Write()` 등 | VTK writer |
| 9 | CSV/상태 JSON 저장 | `DashAnalysisLauncher.cpp:1477, 972` | Qt I/O |

판정: 검토의견이 지목한 read(4·5)·write(6·8·9)·변환(6·7)에 더해 **DLL 실행(1\~6)이 가장 큰 정지원**이다. 유일한 워커(DOE 샘플링)는 정작 가벼운 축이고, 무거운 DLL 작업은 전부 GUI 스레드에 있다.

### 2-4. 프리즈 위장 계층 — 왜 지금까지 "비동기처럼" 보였나

- `processEvents` 50+ 개소가 정지를 가린다 — 모델 계층 41곳(`DashJobRunner` 19 / `DashDataProcessor` 14 / `DashResultProcessor` 8) + 위젯 다수. 이것이 재진입 크래시 계급(#64)의 원천 (실증 문서 W10).
- **깨진 진행 표시** — 상태바 점 애니메이션(`DashMainWindow.cpp:3446-3475`, QTimer 기반)을 동기 모핑 직전/직후에 start/stop 하는데(`DashModelRunnerWidget.cpp:529-538`), 모핑이 이벤트 루프를 막는 동안 QTimer가 발화하지 못해 **애니메이션 자체가 얼어붙는다**. "정식 진행 표시가 필요했으나 동기 설계가 이를 무력화"한 직접 증거.
- 정식 장치(`QProgressDialog`·모래시계 커서)는 0건 — 진행 UX 부재는 W11이 채운다.

### 2-5. 코드 안의 모범 선례 — 수렴 목표 (새 발명 불요)

| 선례 | 위치 | 무엇이 옳은가 |
|---|---|---|
| `DashModelRunner` | `model/DashModelRunner.cpp` | QProcess 16회 사용에 `waitFor*`/`processEvents`/`msleep` 0회 — 완전 시그널 구동 |
| `runDirectJobs` .wbpj 경로 | `DashJobRunner.cpp:2326-2336` | `loadPrtCompleted` 시그널 구독으로 다음 단계 연쇄 — 배치 루프로 일반화할 참조 구현 |
| FELauncher 콜백 마샬링 | `DashJobRunner.cpp:1170` | C 콜백 → `invokeMethod(Qt::QueuedConnection)` — 경계 어댑터의 정석 |
| DOE 샘플링 워커 | `DashAnalysisLauncher.cpp:233,64` | `QtConcurrent::run` + `QFutureWatcher::finished` → 메인 슬롯 — WorkerJob의 원형 |
| MBD motion-launcher | `DashJobRunner.cpp:751-841` | QProcess 비동기 시그널 + 순차 큐 — motion-writer(동기 루프)에 이식할 패턴 |

## 3. 판정 ① — 완료 처리 3방식: 콜백 vs 이벤트(시그널) vs 코루틴

먼저 개념 구분: 셋은 "작업을 **어디서** 실행하나"(외부 프로세스 / 워커 스레드)가 아니라 "완료를 **어떻게 되돌려 받나**"의 선택지다. 실행 주체와 직교하므로, 실행 주체별 처방(4·5절)과 별개로 통지 표준을 하나 정한다.

| 방식 | 장점 | 단점 | 네이티브 | 판정 |
|---|---|---|:---:|---|
| C 콜백 (함수 포인터) | 언어 무관 — C API 경계에서 유일한 선택지 | 콜백 실행 스레드 문맥 불명 · 수신자 수명 관리 수동(dangling 위험) · 일대일 | X | **경계 어댑터로만** — 수신 즉시 시그널 변환 |
| Qt 시그널/슬롯 (이벤트) | 네이티브 · `QueuedConnection` 자동 스레드 마샬링 · 수신자 소멸 시 자동 disconnect · 일대다 구독 | 흐름이 코드상 분산 (Job 상태머신으로 보완) | O | **표준 채택** |
| 코루틴 (`co_await`) | 순차 오케스트레이션이 선형 코드로 읽힘 | Qt 5.15에는 어댑터 없음 — 사실상 표준인 QCoro 최신판은 **Qt 6.8+ 전용**(Qt5는 유지보수 끝난 구버전 고정) · 디버깅 스택 단절 · 취소 전파 학습 비용 | X (Qt 5.15) | **보류** — Qt 6 이행 시 재평가 |
| `std::thread`/`std::async` 생 사용 | 표준 라이브러리만으로 가능 | 이벤트 루프 통합·마샬링을 수제 구현해야 함 (현 코드 0건) | △ | 기각 — Qt 도구로 충분 |

### 3-1. 왜 시그널이 표준인가 — 근거 4

1. **스레드 경계 자동 처리** — `Qt::QueuedConnection`이 완료 통지를 수신자 스레드의 이벤트 루프로 자동 마샬링. 수제 마샬링 코드가 소멸한다.
2. **수명 안전** — QObject 수신자가 소멸하면 연결이 자동 해제된다. 콜백 방식의 "완료 시점에 수신자가 살아 있는가" 문제가 구조적으로 사라진다 (크래시 계급 소멸이라는 W10 목적과 직결).
3. **일대다 구독** — 같은 완료/진행 시그널을 진행바·상태바·로그 도크가 동시 구독(W11), Presentation Model의 시그널 표면(W21)과 같은 문법 — 후속 티어와 이음새 없음.
4. **검증된 내부 선례** — 2-5절 5종. 로드맵 원칙 2("이벤트 구동 전환 > 워커 스레드 전면 도입") 그대로 — 새 발명이 아니라 수렴.

### 3-2. 콜백의 자리 — 경계 어댑터 한정

FELauncher C API처럼 콜백만 제공하는 외부 계약은 그대로 쓰되, 규칙은 하나: **콜백 본문에서는 아무것도 만지지 않고 `invokeMethod(Qt::QueuedConnection)`으로 시그널 문맥에 넘긴다**. 이미 올바른 구현이 있다 (`DashJobRunner.cpp:1170`). 내부 DLL이 주는 진행 콜백(모핑 `statusCallback` 등)도 동일 — 워커 문맥에서 오므로 시그널 변환 필수.

### 3-3. 코루틴 판정 상세 — 왜 지금은 아닌가

- 언어는 준비돼 있다(C++23, MSVC 코루틴 지원). 문제는 어댑터 라이브러리: Qt 5.15에는 시그널/`QFuture`를 `co_await` 가능하게 하는 표준 수단이 없고, 사실상 표준인 QCoro는 최신판이 Qt 6.8+ 전용이라 Qt5 지원 구버전을 고정(유지보수 종료)해야 한다.
- 코루틴이 이득인 지점은 정확히 "DOE 배치처럼 순차 의존 단계가 긴 오케스트레이션"인데, 그 계층은 W10에서 Job 상태머신으로 재작성될 대상이다 — 지금 코루틴을 넣으면 같은 코드를 두 번 재작성한다.
- 시그널 기반 Job이 완성된 뒤에는 Job 완료 시그널을 awaiter로 감싸는 어댑터만으로 코루틴을 **additive**하게 얹을 수 있다 — 배타적 선택이 아니므로 지금 결정할 필요가 없다 (백로그 원칙 6 "계약 변경은 재작성 기회에 동승"과 동형의 보류).

## 4. 판정 ② — 통합 설계: Job 표면 하나로 외부·내부를 덮는다

핵심 아이디어: 호출자(위젯/PM)가 "이 작업이 외부 exe인지 워커 스레드인지"를 **모르게** 한다. W10의 Job 상태머신(Pending → Running → Succeeded/Failed(reason)/Cancelled + progress + cancel, 전부 시그널 방송)이 그 공통 표면이고, 구현이 두 갈래로 갈라진다.

- **ProcessJob** — 외부 exe. **스레드 0개** (QProcess는 본래 비동기). 데몬 큐(`commandCompleted`)·`runAsync`·C 콜백 어댑터를 Job 상태로 번역만 한다.
- **WorkerJob** — in-process 작업. `QtConcurrent::run`(지정 풀) + `QFutureWatcher`로 오프로딩하고 완료·진행을 Job 시그널로 번역한다. **검토의견의 "비동기 래퍼"가 바로 이것** — 선례는 DOE 샘플링 워커(2-5절).
- 파일 생성 대기는 Job의 내부 구현 디테일 — `QFileSystemWatcher`/`QTimer` 콜백으로 처리(폴링 아님). 완료 판정은 "파일 존재"가 아니라 "완료 시그널 수신 → 파일 검증" 순서 (flush 레이스 오탐 방지 — 로드맵 3-2절).

```
[요청] 위젯/PM이 Job 생성 — 종류 무관하게 시그널만 구독
   │   1. started / progress / finished(state) 연결
   │   2. 호출은 즉시 반환 — 메인스레드는 이벤트 루프 상주
   ▼

[실행] Job 구현이 갈라짐 — 호출자에게는 비가시
   │   1. ProcessJob: 데몬 큐 enqueue 또는 runAsync — 스레드 0개
   │   2. WorkerJob: 지정 스레드 풀에 함수 오프로딩
   │   ※ 완료 원천(QProcess 시그널·C 콜백·QFutureWatcher·파일 워처)은
   │      Job 내부에서 흡수 — 밖으로는 Job 시그널 한 종류만
   ▼

[완료] Job이 상태 시그널 방송 — 메인스레드 문맥 보장
       진행바(W11) · 실패 통지(W12) · PM(W21)이 같은 시그널을 구독
```

계약 4종 (Job 표면에 고정 — 개정 3에서 "구독" 추가) — **시그널 개수가 아니라 계약 차원**이다(실제 시그널은 `started`·`progressed`·`finished` 3종이며, 취소=`cancel()` 메서드·구독=배선 규칙·실패=`finished`의 파라미터로 실현):

- **취소** — 협조적 취소. ProcessJob = 추적 PID kill(W6의 killOrphans 축소와 결합). WorkerJob = `std::atomic<bool>` 체크 지점 — 단 **DLL 함수 실행 도중에는 중단 불가**(비협조 코드)이므로 "취소 = 상태는 즉시 Cancelled, 늦게 도착한 결과는 폐기" 의미론을 명시한다. DLL이 취소 콜백을 제공하면 활용.
- **진행** — 외부 = `[PROGRESS] n%` additive 마커(W11 규약, TopOpt 형식 확산). 내부 = DLL 진행 콜백 → 시그널 변환, 콜백이 없으면 불확정(indeterminate) 진행바.
- **실패** — 도메인 enum + reason 문자열. W12 통지 규칙(사용자 개입 필요 → 모달, 그 외 → 로그 도크)에 직결.
- **구독** (개정 3) — 시그널은 관찰자 패턴이라 **재생(replay)이 없다**: emit 순간 연결돼 있지 않으면 통지는 유실된다 (원리는 [193-1-async-execution-models](193-1-async-execution-models.md) 3-4절). 귀결 3규칙:
    1. **"connect 먼저, start 나중"** — Job 시그널 구독은 반드시 `start()` 호출 전에 완료. 코드 리뷰 체크 항목으로 고정.
    2. **상태는 pull 병행** — Job은 `state()`/`progress()` 동기 조회를 시그널과 함께 제공 — 늦게 구독한 소비자(나중에 열린 다이얼로그 등)가 현재 상태를 복구할 수 있게.
    3. **전역 이벤트 버스 금지** — 배선은 객체 짝 연결(관찰자)을 유지하고, 토픽형 전역 버스(진짜 pub/sub) 도입은 지양한다. "아무나 발행·아무나 구독"은 `Mgr()` 전역 접근 549회가 만든 추적 불가 결합을 이벤트 평면에 재현하는 것 — **Job을 건네받은 소비자만 구독**한다는 제약이 의존 관계를 코드에 보이게 유지한다.

### 4-1. 취소·실패 사용자 정책 — 계약 위의 정책 계층 (개정 4)

발단: 검토 피드백 — "사용자의 작업 취소 및 실패 관리 정책이 중요하다". 위 계약의 "취소"·"실패"는 **메커니즘**(취소가 어떻게 전파되고 실패가 어떻게 통지되나)을 정의했지만, 그 위의 **정책**(사용자에게 무엇을 약속하나 — 취소하면 지금까지의 결과는? 한 케이스가 실패하면 나머지는?)은 미기록 공백이었다. 아래 5건으로 고정한다.

| # | 정책 질문 | 판정 (기본값) |
|---|---|---|
| P1 | 취소 시 **부분 결과물**은? | 완료된 케이스의 결과는 **보존** — 배치 결과에 케이스별 종료 상태(Succeeded/Failed/Cancelled/NotRun)를 기록해 어디까지 유효한지 보이게 한다. 취소로 **중단된 케이스**의 쓰다 만 산출물(kill된 외부 프로세스의 미완성 파일 등)은 **폐기 또는 격리** — "파일 존재 = 완료" 오탐으로 다음 실행을 오염시키지 않게 (로드맵 3-2절 flush 레이스와 동류 위험) |
| P2 | 배치 취소의 **범위와 시점**은? | 배치 취소 = 배치 전체 중단: 잔여 케이스는 시작하지 않고, 진행 중 케이스는 **가능한 가장 이른 지점**에서 중단 — ProcessJob 구간이면 즉시 kill, WorkerJob이면 다음 취소 체크 지점, DLL 호출 도중이면 완주 후 결과 폐기(계약의 협조적 취소 그대로). 케이스 단위 선택 취소는 도입하지 않음(단순성). 실행 중 앱 종료(W7)는 이 경로의 특수 호출자 — closeEvent가 같은 배치 취소를 호출한다 |
| P3 | 케이스 **실패 시 배치**는 계속? 중단? | **계속(continue-on-error)이 기본** — DOE 케이스는 상호 독립이라 하나의 실패가 나머지의 가치를 없애지 않는다 (현행 암묵 동작 `DashJobRunner.cpp:2673`의 명문화). 실패는 케이스 상태로 기록하고 배치 종료 시 **실패 요약**으로 통지 — W12 규칙 적용(전건 실패 등 개입 필요 → 모달, 부분 실패 → 로그 도크). 예외 — **연쇄 실패 차단기**: 동일 유형 실패가 연속 k건(제안 3)이면 배치 중단 — 환경 원인(데몬 사망·라이선스)으로 밤새 전 케이스가 케이스당 600s 타임아웃만 소진하는 낭비 방지 |
| P4 | **취소 불가 구간**(DLL 실행 중)의 UX는? | 취소 클릭에 UI는 **즉시** 반응: 버튼 비활성 + "취소됨" 표시 + Job 상태 즉시 Cancelled(계약 그대로). WorkerJob의 잔여 DLL 실행은 백그라운드에서 소진되고 결과는 폐기된다 — 사용자에게 약속하는 것은 **"취소 = UI 즉시 해방"이지 "CPU 즉시 해방"이 아님**을 명시적으로 수용한다(협조적 취소의 대가). 소진 중 동일 서브시스템 재실행은 직렬 풀(5-2절)이 자연스럽게 뒤에 줄 세운다 |
| P5 | 실패 후 **재시도**는? | 자동 재시도 **없음** — 실패 원인(입력 오류·환경)을 모른 채 반복하면 낭비만 는다. 실패 케이스 목록은 요약·상태 기록에 남겨 사용자가 원인 확인 후 재실행한다. "실패분만 선별 재실행" UI는 본 설계 범위 밖 — 후속 후보로만 기록 |

구현 귀속: P1·P2·P3·P5 = Job·배치 오케스트레이터의 구현 규칙(W10 서브태스크 a·f에 흡수), P4 = 진행 UX(W11), 통지 형식 = W12. **백로그 항목 신설 없음** — 기존 항목의 수용 기준을 정밀화한 것이다.

## 5. 판정 ③ — 내부 작업 선별 기준: 무엇을 싸고, 무엇은 안 싸나

### 5-1. 작업 유형 4분류 결정표

| 유형 | 예 (2-3절 실측) | 처방 | 추가 스레드 |
|---|---|---|:---:|
| 외부 exe 실행·대기 | NX STP 생성, Journal, FE 솔버, MBD | ProcessJob — 시그널 구동 | 0 |
| 파일 생성·안정화 대기 | VTU/STP/RST 대기 | 워처/타이머 콜백 (Job 내부) | 0 |
| in-process CPU·I/O | RST/KPI 파싱, CSV, VTU 쓰기, 직렬화 | WorkerJob | 풀 |
| in-process DLL 호출 | DashMR 모프, DashRW/dash::rw read·write | WorkerJob + 5-2 등급 규칙 | 등급별 |

선별 문턱 (전부 래핑 금지 — 단순성 원칙): **사용자가 체감하는 정지를 만드는 작업만** — 대략 100ms를 넘거나 입력 크기(메시·케이스 수)에 비례해 자라는 작업. 2-3절 실측 목록이 곧 1차 대상이다. 신규 코드는 기본 동기로 작성하고, 느려질 때 Job으로 승격하면 된다 — 짧은 호출의 래핑은 복잡도만 산다.

(개정 5) "오래 걸리건 말건 일괄 래핑이 유지관리에 더 유리하지 않은가"에 대한 판정 — **아니다, 근거 2**:

1. **재진입 창 재배포** — 짧은 동기 호출은 원자적이다(실행 중 이벤트 루프가 돌지 않아 끼어들 입력이 없음). 래핑하는 순간 start와 완료 슬롯 사이에 이벤트 루프가 돌아 재진입 창이 열린다 — W10이 제거하려는 `processEvents` 재진입 창(#64 크래시 계급의 원천)을 모든 호출 지점에 재배포하는 셈이며, 래핑마다 재진입 가드·계약 4종·정책 P1\~P5 의무가 청구된다.
2. **균일성의 올바른 층위** — 유지관리 균일성은 래퍼가 아니라 **승격 가능 형태**의 일괄 규율로 확보한다: 6-4절 절단 3규칙(입력 스냅샷·본문 위젯 무접촉·출력 시그널)을 신규 코드 전반에 적용하면, 느려진 함수는 호출부 국소 수정만으로 Job에 승격된다. 요약 — **메커니즘(Job)은 선별, 형태(파라미터화)는 일괄**.

단, 코루틴 도입 시(3-3절) 래핑 비용의 주범인 제어 흐름 분절이 급감하므로 이 문턱 자체가 재평가 대상이다.

### 5-2. "DLL 실행도 포함인가?" — 포함. 스레드 안전성 3등급으로

판정: **포함한다.** DLL 함수 호출은 우리 프로세스 안에서 호출 스레드를 점유하는 일반 함수 호출이므로, 오래 걸리면 read/write와 똑같이 GUI를 얼린다 — 실측에서도 가장 큰 정지원이 `Morph()`와 `reader.Update()`였다(2-3절). "DLL이라서" 특별한 것이 아니라, **"그 DLL을 다른 스레드에서 불러도 되는가"** 가 유일한 추가 질문이며, 답에 따라 등급이 갈린다.

| 등급 | 조건 | 처방 | 본 코드베이스 해당 |
|:---:|---|---|---|
| 1 — 스레드 안전 | 무상태·재진입 가능 (벤더 문서로 확인된 경우만) | 공용 풀에서 병렬 실행 | 확인된 것 없음 — 문서 확인 전 부여 금지 |
| 2 — 비재진입 | 전역/공유 상태 보유, 단일 호출자 전제 | **서브시스템 전용 직렬 워커** — `QThreadPool` 1개(maxThreadCount=1). 같은 서브시스템 작업은 구조적으로 동시 실행 불가 → DLL 쪽 락 불요. GUI는 자유 | `DashMR::`(operator 내부가 이미 16스레드 병렬 — `DashManager.cpp:310` — 래퍼는 단일 호출자 전제) · `DashRW::`/`dash::rw`(플러그인 이름 조회 → 전역 레지스트리 의심) — **기본값** |
| 3 — 격리 필요 | 스레드 어피니티·COM·라이선스·프로세스 전역 오염 | 외부 프로세스로 격리 | NXOpen — **이미 그렇게 하고 있다** (`DashOptiCADNX.exe` 데몬 = 등급 3 처방의 기존 선례) |

판별 절차: 벤더 문서/헤더 계약 확인 → 근거가 없으면 **보수적으로 등급 2**. MSVC 환경이라 TSAN이 없으므로 실측으로 등급 1 승급하는 것은 비권장. 등급 2만으로도 목표(GUI 응답성)는 완전히 달성된다 — **동시성이 아니라 응답성이 목표**이기 때문이다. 모핑 풀과 RW 풀은 서로는 병렬로 돈다.

### 5-3. 선결 조건 5건 — 워커 투입 전 반드시 (없으면 프리즈가 레이스로 바뀐다)

> (개정 7) 본 5건은 [203-2-worker-preconditions-analysis](203-2-worker-preconditions-analysis.md) 로 **별도 과제화** — 건별 실측·실패 시나리오·처방 대안 비교·검증 기준·착수 순서(D4→D1→D2→D3→D5)는 그 문서가 정본이며, 서브태스크 e 는 그 게이트 통과 후 착수한다. 아래 목록은 요약으로 유지.

(개정 5) **워커 투입** = WorkerJob·직렬 풀 도입(7절 서브태스크 e) — 외부 축(ProcessJob, 서브태스크 a\~c)은 스레드를 만들지 않으므로 본 선결 조건과 무관하게 즉시 착수 가능하다. 아래 5건이 지금 사고를 안 내는 유일한 이유는 모든 코드가 GUI 스레드 하나에서 돌아 자동 직렬화되기 때문(프리즈가 안전장치 역할) — 두 번째 스레드 등장 순간 그 보호가 사라진다. 순서 강제: d(본 절) → e.

1. **싱글톤 lazy-init 안전화** — `DashManager::Mgr()`(`DashManager.cpp:210-215`)·`DashProjectManager::Instance()`(`DashProjectManager.cpp:13-18`) 모두 락 없는 지연 생성. 메인스레드 선-초기화 보장 + 초기화 락 (W10 다섯 번째 항목 그대로).
2. **`ExecuteMorphing` 공유 상태 분리** — 싱글톤 멤버 `m_morphingOperator`를 mutex 없이 비원자 6단계 시퀀스로 변이(`DashManager.cpp:314-343`). 모핑 실행 상태를 Job 로컬(또는 직렬 워커 소유)로 이전한다. 직렬 풀이 1차 방어지만, 프리뷰(GUI 경로)와 배치(워커)가 같은 operator를 만지는 조합이 남으므로 소유권 분리가 정답.
3. **`DashAnalysisModelContext` 접근 규약** — 레지스트리가 같은 경로에 동일 캐시 인스턴스를 반환하는데 컨텍스트 내부 mutex 전무, 레지스트리 락은 맵만 보호(무거운 로드는 락 밖 — 이중 파싱 가능). 규칙: "컨텍스트는 배정된 직렬 워커에서만 접근" 또는 읽기 전용 스냅샷 전달 — 결과는 시그널로 메인에 복귀 후 병합.
4. **전역 `std::cout` rdbuf 스왑 제거** — `reader.Update()` 동안 프로세스 전역 cout/cerr을 임시 교체 후 복원(`DashAnalysisModelContext.cpp:306-316`). 두 스레드 동시 로드 시 save/restore 레이스 → 영구 오리다이렉션/크래시. 스레드화 전에 다른 억제 수단(DLL 로그 레벨 API·널 싱크)으로 교체.
5. **GUI·VTK 객체 규칙** — QWidget 등 GUI 클래스는 메인스레드 전용(Qt 계약). VTK 파이프라인 객체는 스레드 간 공유 금지 — 워커가 만든 `vtkPoints` 등은 소유권 이전으로 메인에 넘기고, 병합·렌더링은 메인에서만.

### 5-4. 적용 후보와 우선순위 (실측 기반)

| 순위 | 작업 | 현 상태 | 패턴 | 비고 |
|:---:|---|---|---|---|
| 1 | DOE 배치 모핑 루프 | `MorphFromDoeSamples`→`Execute` 완전 동기 — `processEvents`조차 없어 UI 완전 정지 | WorkerJob(모핑 직렬 풀) + 케이스별 진행 시그널 | W10 파일럿(JobRunner 배치)과 같은 사이클 |
| 2 | 단건 모핑·프리뷰 | ModelRunner/Optimizer 버튼 슬롯에서 동기 | 동일 | 깨진 상태 애니메이션(2-4절)이 살아난다 |
| 3 | FE 모델 파싱 `Update()`/`load_contents` | `getOrLoad` 경유 GUI 스레드 | WorkerJob(RW 직렬 풀) | 선결 3·4 필수 |
| 4 | RST/KPI 파싱 7종 | `DashDataProcessor` — `processEvents` 13곳 | WorkerJob 또는 분할 처리 | `processEvents` 제거와 동시 (W10 세 번째 항목) |
| 5 | export/serialize/메시 갱신 | 컨텍스트 write 계열 | WorkerJob(RW 직렬 풀) | 모핑 배치가 케이스마다 호출 — 1번과 같은 풀 순서 보장 필요 |
| 6 | VTU/VTK·CSV 쓰기 | `DashManager.cpp:862` 등 | WorkerJob | 소형 — 여력 시 |

## 6. 판정 ④ — 뷰 분리(W19\~W21) 없이 실행부만 먼저 비동기 전환할 수 있는가 (개정 1)

### 6-1. 우려의 재구성

우려: "뷰와 컨트롤러가 타이트하게 묶여 있어서, 컨트롤러의 메인스레드가 하위를 병렬 실행하도록 떼는 것이 뷰와 묶인 부분 때문에 어렵다." 결합 자체는 실측 사실이다 — 싱글톤 직접 호출 549회, `DashManager`가 뷰 위젯 포인터 2종+렌더윈도 보유(`DashManager.h:105,107,96`), 뷰가 QProcess를 직접 실행(`DashOptimizerWidget` 8회·`TopOptPostprocessDialog` 7회), 위젯 안 모핑 루프(`DashGeometryParameterWidget.cpp:1500-1565`).

그러나 이 우려는 **"비동기화 = 스레드로 병렬 실행"이라는 전제** 위에서 성립한다. 채택된 방식(3절 — 시그널 구동)은 그 전제 자체를 제거하므로, 결합이 실제로 문제 되는 범위가 크게 줄어든다. 아래에서 축별로 가른다.

### 6-2. 외부 축(W6·ProcessJob·폴링 제거·데몬 비동기화) — 뷰 결합과 무관하게 가능

- **스레드를 하나도 만들지 않는다.** 외부 exe는 이미 OS 수준에서 병렬(별도 프로세스)이다 — 새로 만들 병렬성이 없고, 없앨 것은 메인스레드의 **대기**뿐이다. 전환 전후 모든 코드가 메인스레드에 남는다.
- 바뀌는 것은 제어 흐름 하나: "여기서 멈춰 기다린다(`waitFor*`/폴링)" → "시그널 오면 이어서 실행(슬롯)". **재개 슬롯도 메인스레드에서 실행**되므로, 그 안에서 위젯을 만지는 기존 코드는 지금과 똑같이 합법이다. 뷰 결합(위젯 직접 갱신·`Mgr()` 호출·뷰 포인터)을 한 줄도 건드리지 않고 전환할 수 있다.
- 같은 결합 상태의 이 코드베이스에서 **이미 작동 중인 반증 선례**가 있다(2-5절): `DashModelRunner`(완전 시그널 구동), `runDirectJobs` 시그널 연쇄, FE C 콜백 마샬링 — 전부 뷰 분리 없이 공존한다.

### 6-3. 실행 평면의 뷰 접촉 실측 — 이미 거의 떨어져 있다

"컨트롤러 실행부"가 실제로 뷰를 얼마나 만지는지 재조사한 결과, **결합은 상호작용·프리뷰·결과 표현 평면에 몰려 있고 배치 실행 평면은 이미 깨끗하다**:

| 실행 평면 (전환 대상) | 뷰 접촉 실측 |
|---|---|
| `DashJobRunner.cpp` (최대 배치 오케스트레이터, W10 파일럿) | Widget·MainWindow 참조 **0건** |
| `DashMorphingDoeExecutor.cpp` (모핑 배치) | Widget 참조 **0건** |
| `DashManager::ExecuteMorphing` 본문 (`DashManager.cpp:314-343`) | 위젯 무접촉 — 입력(points·handles)을 **파라미터로 받아** 결과를 반환하는 이미 파라미터화된 코어 |

| 결합 평면 (전환 대상 아님 — W19\~21 몫) | 실측 |
|---|---|
| `DashManager` 뷰 포인터의 실제 소비자 | `DashHandlePickingInteraction.cpp:407,1664,2001,2152`(3D 피킹 상호작용) + `DashMorphingSettings.cpp:1198,1207,1364,1373`(오버레이 UI) — 배치 실행 경로에서는 읽지 않음 |
| `DashModelRunner.cpp`의 model→view 접촉 | `plotWindowReady(QWidget*)` 결과 표현 역전(`:311-322,420-431` — W19 대상)이지, 실행·대기 메커니즘이 아님. 실행부(QProcess 16회)는 이미 시그널 구동 |

즉 "실행부를 떼는" 작업의 대상 코드에는 떼어낼 뷰 결합이 애초에 거의 없다. 결합이 짙은 곳(피킹·오버레이·플로터)은 실행부 전환의 대상이 아니다.

### 6-4. 워커 축(WorkerJob)에서만 결합이 실제 장애물 — 처방은 국소 절단 3규칙

내부 DLL 작업을 워커로 옮길 때는 뷰 접촉이 진짜 장애물이 된다(워커에서 위젯 접근 = Qt 계약 위반). 그러나 필요한 것은 전면 뷰 분리가 아니라 **Job 경계에서의 절단 3규칙**이다:

1. **입력 스냅샷** — 실행 시작 시점(메인스레드)에 위젯·컨텍스트에서 값을 읽어 파라미터 구조체로 고정. 실행 중 위젯 상태 변화와 무관해진다(`ExecuteMorphing`은 이미 이 형태, `--config-json` 관행도 동형).
2. **실행 중 위젯 접근 금지** — 워커 함수 본문은 스냅샷과 자기 소유 데이터만 사용.
3. **출력은 시그널로** — 결과·진행을 Job 시그널로 방송, 위젯 반영은 메인스레드 슬롯에서.

판별 리트머스: 그 코드가 위젯을 만지는 순간이 **시작 시점**(입력 수집 → 규칙 1로 흡수) / **종료 시점**(결과 반영 → 완료 슬롯으로 이동) / **실행 중**(진행 로그 직접 append·`processEvents` 갱신 → 진행 시그널로 대체)인가 — 세 경우 모두 Job 표면(4절)이 이미 제공하는 것으로 치환되며, 함수 시그니처 수준의 절단이지 아키텍처 이동이 아니다.

뷰가 직접 실행하는 곳(`DashOptimizerWidget` QProcess 8회 등)도 마찬가지 — 호출부 한 줄을 Job 생성으로 교체하는 W6 치환 작업이지, 뷰 구조 변경이 아니다.

### 6-5. 판정과 잔여 조건

**판정: 가능하다 — 그리고 이것이 이미 백로그의 전제다.** 티어 1\~2(W6·W10 실행 모델)가 티어 4\~5(W19\~W21 구조)보다 먼저인 순서 자체가 "실행부 전환은 뷰 분리에 의존하지 않는다"는 판단 위에 서 있다(로드맵 원칙 1 "크래시 계급 > 구조 계급"). 의존은 오히려 역방향이다 — 실행부가 만든 **Job 시그널 표면이 나중에 PM(W21)의 구독 대상**이 되므로, 실행부 선행 전환은 뷰 분리의 정지 작업이다.

잔여 조건 2건 (둘 다 기존 항목 범위 내):

- **스냅샷 규율** — 재개 슬롯이 위젯의 "현재" 상태를 다시 읽으면, 실행 중 사용자가 값을 바꿨을 때 시작 시점과 다른 입력이 섞인다. Job이 시작 스냅샷을 보유하는 규칙 1로 차단.
- **재진입 가드** — 비동기화되면 실행 중에도 버튼이 살아 있으므로 중복 실행 가드(W6 베이스 공통 책임)와 실행 중 버튼 비활성화(W11)가 짝으로 필요 — 이미 해당 항목 범위에 포함돼 있다.

## 7. 백로그 반영 — 무엇이 바뀌고, 무엇이 안 바뀌나

**바뀌지 않는 것**: 작업 항목·착수 창 ①\~⑥·freeze 산정(백로그 1-2절) 전부 불변. 본 문서는 W10 본문 여섯 번째 항목("in-process 장시간 연산만 선별 워커화")의 상세 설계이자, 검토의견("내부 작업도 비동기 래퍼 필요")의 **채택** 기록이다.

**W10 티켓 분할 시 서브태스크 제안** (의존: a → b·c 병행, d → e → f 직렬):

```
W10 이벤트 구동 전환  (호출자가 시그널만 보게 만든다)
└─ Job 상태머신 = 공통 시그널 표면 (Pending→Running→Succeeded/Failed/Cancelled + progress + cancel)
   │  완료 처리 표준 = Qt 시그널 · C 콜백은 경계 어댑터 (3절)
   ├─ 외부 축 · ProcessJob (스레드 0개 — QProcess는 본래 비동기)
   │   ├─ a. 상태머신 골격 + ProcessJob 전환 (파일럿 = DOE 배치)
   │   ├─ b. 파일 폴링 → 워처/타이머 콜백
   │   └─ c. 데몬 기동 비동기화 (NX 120초 프리즈 소멸)
   └─ 워커 축 · WorkerJob (스레드 풀 — in-process 장시간 작업 선별 오프로딩)
       ├─ d. 선결 조건 5건  ← 게이트(공유상태 정리), 상태머신과 직교
       ├─ e. WorkerJob 래퍼 + 직렬 풀 2종(모핑·RW)
       └─ f. 5-4 후보 적용 + 잔여 processEvents 41곳 제거

의존: a → (b·c 병행) · d → e → f
```

- a. Job 상태머신 + ProcessJob 전환 — 파일럿 = DOE 배치 경로(`runWbpjDoeAsync`의 `waitForFile` → `updatePrtGeometryCompleted` 구독, 참조 구현 `runDirectJobs`) 〔외부 축 — 판정·근거 6-2절, QProcess 지점 전수 [201-1-qprocess-antipattern-catalog](201-1-qprocess-antipattern-catalog.md)〕
- b. 파일 폴링 → 워처/타이머 (`waitForFile`·`waitForVtuFileComplete`·motion-writer 루프) 〔외부 축 — 6-2절〕
- c. 데몬 기동 비동기화 — `startDaemon` busy-wait 제거 → `daemonReady` 시그널 → 큐 flush (NX 120s 프리즈 소멸) 〔외부 축 — 6-2절〕
- d. 선결 조건 5-3 — 싱글톤 락·모핑 상태 분리·컨텍스트 규약·cout 스왑 제거 〔워커 축 게이트 — 요약 5-3절, 상세 D1\~D5 [203-2-worker-preconditions-analysis](203-2-worker-preconditions-analysis.md)〕
- e. WorkerJob 래퍼 + 직렬 풀 2종(모핑·RW) 도입 〔"워커 투입" 정의 5-3절(개정 5) — d 게이트 통과 후 착수〕
- f. 5-4 후보 순차 적용 + 잔여 `processEvents` 제거 〔후보·우선순위 표 5-4절〕

**DoD** — 기존 W10 DoD(`model/` processEvents 0건, GUI 스레드 `waitFor*`/`msleep` 0건 — grep 수동 검증, W9 자동 게이트는 선택)가 내부 작업까지 이미 커버한다. 확인 항목 1줄만 추가 제안: "5-4 후보 작업 실행 중 창 이동·리사이즈·취소 정상 동작".

**코루틴 재평가 트리거**: Qt 6 이행 결정 시 (QCoro 최신판 Qt 6.8+ — 3-3절).

## 8. 참고 자료

- 내부: [198-1-improvement-roadmap](198-1-improvement-roadmap.md) 2절(동기/비동기 실측)·3-2절(프로토콜 취약점)·Phase 1\~2 / [195-1-backlog-code-evidence](195-1-backlog-code-evidence.md) W6·W10 / [200-3-prioritized-backlog](200-3-prioritized-backlog.md) 1-2절(연동 freeze — 시그널 표면 보존 원칙)
- 외부: QCoro 공식 문서·저장소 (최신판 Qt 6.8+ 요구 — Qt5는 구버전 계열 한정), Qt 5.15 문서 `QProcess`·`QtConcurrent::run`(풀 지정 오버로드는 5.15부터)·`QFutureWatcher`·`QFileSystemWatcher`
