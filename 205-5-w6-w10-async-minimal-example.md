# DashGUI2 W6·W10 비동기 처리 최소 구현 예제 — 소스코드 구성 (드래프트)

> 원본: 사전조사 Issue #205 — 본문을 이 페이지로 이관한 뒤 Issue 삭제 (2026-08-24). **본 페이지가 정본**
> 파생 문서: [205-1-w6-w10-ticket-summary](205-1-w6-w10-ticket-summary.md) · [205-2-w6-w10-change-log-and-remaining-design](205-2-w6-w10-change-log-and-remaining-design.md)

> 상태: 드래프트 개정 3 (GitHub Issue [#205](205-5-w6-w10-async-minimal-example.md) 와 동기화)\
> 연관 Issue: #64 (Crash Debug)\
> 기반 문서: [206-1-w6-w10-thread-execution-design](206-1-w6-w10-thread-execution-design.md) (스레드·전달 메커니즘 도식 — 본 문서는 그 **코드 레벨 자매**) · [194-1-async-execution-patterns](194-1-async-execution-patterns.md) (판정·상세) · [193-1-async-execution-models](193-1-async-execution-models.md) (개념)\
> 목적: "W6·W10이 목표하는 비동기 처리를 **가장 간단한 예제로 직접 구현**한다면 소스코드가 어떻게 구성되나"를 실제 Qt 5.15 C++ 로 보인다. 프로덕션 코드가 아니라 **최소 골격** — 실제 클래스명(`DashMR::`·`DashExtensionProcess` 등)은 예시 배선용

> **한 줄 요약 — W6·W10 큰 그림**\
> W6·W10은 크게 **동기 실행 체인과 `processEvents`를 제거하고 두 비동기 실행 표면을 구현**하는 작업이다. 다만 W6=외부·W10=내부 구도가 아니라 **구조 선행(W6) → 행위 전환(W10)** 으로 갈린다.\
> **W6**(구조 선행, 1.5주) = 단일 one-shot **외부 프로세스 실행부**를 공용 엔진 **위임(composition)** 으로 수렴 — 대기 모델은 불변, W10의 전제 (개정 2: 엔진 = `ProcessJob : public Job` 일체형, `Job.h` 동반 도입 — 2-1절).\
> → **W10**(행위 전환, 4주) = 동기 실행 체인·`processEvents`(model 41곳)·파일 폴링을 **시그널 구동 Job 상태머신**으로 뒤집고, 그 위에 두 실행 표면을 구현 — **(1) 외부 프로세스 → `ProcessJob`(스레드 0 — W6 도입분 활용)** · **(2) 선별된 in-process 블로킹 작업 → `WorkerJob`(스레드 O, 워커 선결 5건 게이트)**.\
> `DashJobRunner`의 다중 프로세스·C API 런처·파일 폴링은 W6 범위 밖 → W10/W20 이연(개정 28).

> **개정 3 (2026-07-22) — 3-3절 축소·재서술**\
> 3-3절 전체(구 3-3-1·3-3-2 포함)를 두 요지만 남기고 재서술 — ⑴ 기동 완료를 이벤트로 수신(`bool startDaemon()` → `void start()` + `ready()`/`died()` 시그널) ⑵ 데몬 명령은 기존과 동일(큐 경로·도메인 파사드 소비 무변경). 삭제분(DaemonHost 골격·전환 지점 순서도·실측 2건·책임 경계 원칙·예열 아이디어)은 이슈 이력(개정 2 판)에 보존 — 유용 요지 3건(기동 중 간섭 규칙·host 보증 원칙·예열)만 3-3절 말미에 축약 잔존, 예열은 #212 개정 블록에도 기록. 3-6절 갈래 ③(데몬) 도식도 제거 — 기존 구조를 그대로 쓰는 갈래라 수정 대상이 아님.

> **개정 2 (2026-07-21) — 검토 반영 5건** (동일자 1차 개정 = DaemonCommandJob 갈래 신설)\
> ⑴ **ProcessRunner·ProcessJob 병합** — 실행 엔진이 Job 표면과 일체(`ProcessJob : public Job`, 1회용)가 되고 `Job.h`가 W6으로 이동. one-shot 소비자의 이중 재배선(W6 러너 시그널 → W10 Job 시그널) 제거 (2-1절·3-2절).\
> ⑵ **DaemonCommandJob 폐기** — `DaemonHost`는 그대로 진행, 데몬 명령의 소비 표면은 기존 도메인 파사드 4곳 유지. 늦은 결과 폐기·취소는 host로 흡수 (3-3절).\
> ⑶ **`Job::setState` 터미널 상태 잠금** — 취소 후 늦은 완료가 `finished`를 이중 방송하는 버그 차단 (3-1절).\
> ⑷ **범위 밖 명문화** — JobManager·스케줄러·우선순위 큐·Job 트리·재시도 정책은 도입하지 않는다. 5장 파일 목록이 인프라의 전부.\
> ⑸ **3-3절 정리** — 폐기 확정된 DaemonCommandJob 골격을 요약으로 축소(원문은 이슈 이력), 현행 `startDaemon` → DaemonHost 전환 지점 4건 추가.

---

## 0. 이 문서의 범위

- **다루는 것**: Qt 정상 사용 패턴(1장) → W6 실행 클래스 골격(2장) → W10 Job 표면 — 실행 주체 3갈래(3장) → W10 갈래 전체 지도(4장) → 파일 구성(5장). 1~3장은 각 단계의 **최소 컴파일 가능 골격**.
- **안 다루는 것**: 취소/실패 정책 P1~P5, 서브시스템별 직렬 풀 운영, 워커 선결 조건 5건, 진행 마커 규약(`[PROGRESS]`), DLL 3등급 판별 — 전부 [194-1-async-execution-patterns](194-1-async-execution-patterns.md) 로 위임. 6장에 "뺀 것" 목록.
- **읽는 법**: 세 단계는 **누적**이다. 1장 규칙 위에 2장이 실행을 모으고, 그 위에 3장이 Job 표면을 씌운다. 4장은 그 갈래 전체를 지도로 조망한다.

전제 (한 줄): 모든 예제의 공통 목표는 **메인 스레드를 `app.exec()`에 상주시키는 것** — `waitFor*`/`processEvents`/`msleep`로 이벤트 루프를 멈추지 않는다.

---

## 1. 출발점 — Qt 정상 사용 패턴 (baseline)

W6·W10을 얹기 전에, "정상적인 Qt 비동기"가 무엇인지부터. 핵심은 **QProcess는 본래 비동기**라는 것 — 우리가 할 일은 새 병렬성을 만드는 게 아니라 **대기를 시그널로 바꾸는 것**뿐이다.

### 1-1. 같은 일을 두 방식으로 — 안티패턴 vs 정상 패턴

```cpp
// [안티패턴 · 현재] 블로킹 — 이벤트 루프 정지 (waitForFile 폴링과 동류)
bool runSolverBlocking(const QString& exe, const QStringList& args) {
    QProcess proc;
    proc.start(exe, args);
    proc.waitForFinished(-1);              // ★ 여기서 메인 스레드 정지 → 화면 프리즈
    return proc.exitCode() == 0;
}
```

```cpp
// [정상 패턴] 시그널 구동 — 즉시 반환, 이벤트 루프 상주
void MyClass::runSolverAsync(const QString& exe, const QStringList& args) {
    auto* proc = new QProcess(this);

    // connect 먼저 — 완료를 "기다리지 않고" 구독
    connect(proc, qOverload<int, QProcess::ExitStatus>(&QProcess::finished),
            this, [this, proc](int code, QProcess::ExitStatus) {
        onSolverDone(code == 0);           // 완료 시 메인 스레드에서 이 슬롯 실행
        proc->deleteLater();
    });

    proc->start(exe, args);                // start 나중 — 즉시 반환
    // 메인 스레드는 곧장 app.exec() 로 복귀 → 화면 정상
}
```

두 함수의 **줄 수는 비슷**하지만 결과는 정반대다. 아래(정상 패턴)에는 `waitFor*`가 없고, 완료 처리가 별도 슬롯으로 분리됐을 뿐이다. 이것이 코드베이스에 이미 있는 `DashModelRunner`(QProcess 16회·`waitFor*` 0회)의 형태다.

### 1-2. 정상 패턴의 3규칙 (이후 전부의 토대)

```
[규칙 1] connect 먼저, start 나중
   │   시그널은 관찰자 패턴 — emit 순간 연결 안 돼 있으면 통지 유실 (재생 없음)
   ▼
[규칙 2] GUI 스레드에서 waitFor* / processEvents / msleep 금지
   │   기다림은 "능동 대기"가 아니라 "시그널 구독"으로
   ▼
[규칙 3] 완료 처리는 슬롯에서 — 완료 시점에 수신자가 살아 있으면 자동 호출
       수신자 QObject 소멸 시 connect 자동 해제 → dangling 콜백 크래시 원천 제거
```

### 1-3. C API 경계 — 콜백은 즉시 시그널로 변환

FE 솔버처럼 C 콜백만 주는 외부 계약은 그대로 쓰되, **콜백 본문에서 아무것도 만지지 않고** 시그널 문맥으로 넘긴다. 콜백은 어느 스레드에서 불릴지 불명이기 때문이다.

```cpp
// C 콜백 (호출 스레드 문맥 불명) — 경계 어댑터 한 줄
static void onNativeComplete(int code, void* user) {
    auto* self = static_cast<MyClass*>(user);
    QMetaObject::invokeMethod(self, [self, code] {   // Qt::QueuedConnection:
        self->handleCompletion(code);                // 메인 스레드 이벤트 루프가 안전 실행
    }, Qt::QueuedConnection);
}
```

콜백 발화부터 액션 전파까지 4단계:

```
[① 라이브러리 스레드] C 콜백 발화 — 어느 스레드인지 불명
   │   위젯·Qt 객체를 만지면 스레드 계약 위반 → 아무것도 안 만지고 넘기기만
   ▼
[② 경계 마샬링] invokeMethod(self, 람다, QueuedConnection)
   │   지금 실행 안 함 — QMetaCallEvent로 포장해 self 스레드(= 메인)의 이벤트 큐에 post
   ▼
[③ 메인 이벤트 루프] app.exec() 가 dequeue → 람다 실행 (메인 문맥, 위젯 접근 안전)
   ▼
[④ 액션 전파] 도메인 시그널 emit → 진행바(W11)·로그·다음 단계 구독자로 전파
```

핵심은 "시그널이냐 invokeMethod냐"가 아니라 **`QueuedConnection`** — 완료를 수신자(메인) 스레드 큐로 되돌리는 "completion-back" 경로다. 완료 원천에 따라 이 경로가 갈린다: QProcess `finished`(본래 메인 이벤트로 배달) · `QFutureWatcher::finished`(워커→메인 마샬링) · **C 콜백 → `invokeMethod(QueuedConnection)`**(이 경우).

> **어댑터 실행 ≠ 실제 로직 직접 붙이기** — 어댑터는 *일을 하는 게 아니라 일을 할 스레드·시점을 바꾼다*. 완료 로직을 콜백에 직접 붙이면 그 로직은 콜백 스레드(불명·워커일 수 있음)에서 **동기** 실행돼, **뷰(위젯 스레드 어피니티)·공유 상태를 메인과 동시 접근 → 레이스·크래시**(#64)다. 어댑터를 거치면 실작업은 메인 이벤트 루프에서 **순차** 실행되어 락 없이 안전하다. 즉 `QueuedConnection`은 다중 스레드 접근을 "단일 스레드 순차"로 수렴시키는 장치다.

**이미 올바른 구현이 코드에 있다** — 확인(2026-07-18, `dev`): FELauncher C 콜백 트램폴린 `DashJobRunner.cpp:2171-2175`(captureless 람다가 `void* ud`→`self` 캐스트 후 `handleTaskCompletion` 호출) → 마샬링 `:1161-1176`(`invokeMethod(this, 람다, Qt::QueuedConnection)`) → 메인 슬롯 `:1178 onFeTaskCompletedQueued`. 실제 코드는 위 스케치보다 한 겹 깊게(트램폴린 → `handleTaskCompletion`에서 마샬링) 나뉘지만 골격은 동일하다. 같은 트램폴린→마샬 패턴이 **런처 3종에 걸쳐 6곳 반복**된다(재확인 2026-07-21, `dev`): Ansys는 `handleTaskCompletion` 경유(`:2000`·`:2119`·`:2171`), Abaqus·FESafe는 트램폴린 본문에서 직접 마샬(`:1770`·`:2205`·`:314`) — 마샬링 스타일 2종이 섞였으나 "콜백 본문은 캐스트·핸드오프만, 실작업은 `QueuedConnection`으로 메인에서"라는 계약은 전 지점 동일하다(공용 어댑터로 추출돼 있진 않고 등록부마다 반복). 이 경계 뒤로는 전부 시그널 세계 규칙(1-2절)을 따른다.

---

## 2. W6 형태 — 실행을 한 곳으로: `ProcessRunner` 최소 골격

W6은 **동작이 아니라 구조**를 바꾼다. 1장의 정상 패턴을 6개 클래스가 제각각 재구현하던 것을, 공통 책임(exe 검증·env·UTF-8·라인 조립·중복 가드·취소·정리)을 흡수한 **실행 클래스 하나**로 모은다. 여전히 스레드 0개, 여전히 시그널 구동.

> **개정 2**: 아래 `ProcessRunner` 골격은 검토 결과 **`ProcessJob`과 병합**된다 — 근거·병합 골격은 2-1절. 공통 책임 목록·소비자 축소 형태·DoD는 그대로 유효하다.

```cpp
// controller/async/ProcessRunner.h  (기존 DashExtensionProcess 계열이 흡수하는 형태)
#pragma once
#include <QObject>
#include <QProcess>
#include <QStringList>

class ProcessRunner : public QObject {
    Q_OBJECT
public:
    explicit ProcessRunner(QObject* parent = nullptr) : QObject(parent) {}

    // W6: runAsync = 비동기 one-shot (부분 수신 버그 수리 대상). 반환 없음 — 완료는 시그널.
    void runAsync(const QString& exe, const QStringList& args);
    void cancel();

signals:
    void finished(bool ok, int exitCode, QString stdoutText);
    void failed(QString reason);           // exe 없음·기동 실패 등 (W12 통지 대상)

private:
    QProcess* m_proc = nullptr;
    QString   m_buf;                       // UTF-8 라인 조립 버퍼
    bool      m_running = false;           // 중복 실행 가드
};
```

```cpp
// controller/async/ProcessRunner.cpp
#include "ProcessRunner.h"
#include <QFileInfo>

void ProcessRunner::runAsync(const QString& exe, const QStringList& args) {
    if (m_running) return;                            // [공통책임] 중복 가드
    if (!QFileInfo::exists(exe)) {                    // [공통책임] exe 검증
        emit failed(QStringLiteral("실행 파일 없음: %1").arg(exe));
        return;
    }

    m_proc = new QProcess(this);
    m_proc->setProcessChannelMode(QProcess::MergedChannels);
    // [공통책임] env·인코딩은 여기 한 곳에서 (예: 한글 로그 위해 UTF-8 강제)

    connect(m_proc, &QProcess::readyReadStandardOutput, this, [this] {
        m_buf += QString::fromUtf8(m_proc->readAllStandardOutput());   // [공통책임] UTF-8 라인 조립
    });
    connect(m_proc, qOverload<int, QProcess::ExitStatus>(&QProcess::finished),
            this, [this](int code, QProcess::ExitStatus st) {
        m_running = false;
        emit finished(st == QProcess::NormalExit && code == 0, code, m_buf);
    });
    connect(m_proc, &QProcess::errorOccurred, this, [this] {
        m_running = false;
        emit failed(m_proc->errorString());
    });

    m_running = true;
    m_proc->start(exe, args);                         // 즉시 반환 — 스레드 0개
}

void ProcessRunner::cancel() {
    if (m_running && m_proc)
        m_proc->kill();                               // [공통책임] 추적 PID kill
}                                                     // (killOrphans 광역 taskkill → 자기 PID 축소)
```

**W6이 지운 것**: 단일 one-shot 소비자 5개(`DashModelBuilder`·`DashModelRunner`·`DashOptimizer` + view 2종 `DashOptimizerWidget`·`TopOptPostprocessDialog`)가 각자 갖던 `QProcess* m_process`와 그 주변 배선. (`DashJobRunner`는 motion-launcher QProcess 실행부만 부분 수렴 — 다중 프로세스(`QHash`)·C API 런처(`DashFL_*`)·파일 폴링(`waitForFile`)은 단일 one-shot 모델과 불일치라 W10/W20 이연, 개정 28.) 각 호출부는 아래 한 줄로 축소된다:

```cpp
// 6개 클래스의 "QProcess 직접 소유" → 공통 러너 위임
auto* runner = new ProcessRunner(this);
connect(runner, &ProcessRunner::finished, this, &X::onDone);   // connect 먼저
runner->runAsync(solverExe, args);                             // start 나중
```

DoD(개정 28): grep 카운트(`QProcess`→0)가 아니라 **구조·행위 판정** — 단일 one-shot 소비자가 자체 `QProcess`를 생성·기동하지 않고 엔진에 위임하는가. `DashJobRunner`의 C API·다중 프로세스가 정당히 잔존하므로 `QProcess` 리터럴 0을 목표로 하지 않는다(W9 grep 게이트도 하드 '→0'에서 신규 산재만 막는 소프트 추세 가드로 조정). **대기 모델은 아직 그대로** — 이 러너를 블로킹으로 감싸 쓰는 호출부가 남아 있을 수 있고, 그걸 시그널 구동으로 뒤집는 것이 W10이다.

### 2-1. 개정 2 — 병합: ProcessRunner 가 곧 ProcessJob 이다

원안은 W6의 `ProcessRunner`(재사용 서비스)를 W10의 `ProcessJob`(1회용 Job)이 감싸는 2층이었다. 검토 결과 **한 클래스로 병합**한다 — 근거 4가지:

1. **이중 재배선 제거** — 원안대로면 one-shot 소비자 5~6곳이 두 번 배선된다 (W6: 러너 `finished(bool,int,QString)` → W10: `Job::finished(State,QString)`). 병합하면 W6에서 Job 계약으로 1회 배선이 끝나고, **W10 ① 갈래는 "호출부 블로킹 래퍼 제거"만 남는다**.
2. **층의 정당성 부재** — W10 완료 후 러너의 유일 소비자는 ProcessJob이다 (`DaemonHost`는 명시적 비재사용 — 3-3절). 소비자 1개짜리 층은 층이 아니다.
3. **1회용 의미론이 버그 계급을 없앤다** — 실행마다 `new ProcessJob`: 재사용 러너의 잔류 상태(`m_buf` 미클리어)와 jobId 다중화(`m_oneShotJobId` 에코백)가 원천 불요 — **객체 자체가 식별자**다. 중복 실행 가드도 `state() != Pending` 검사로 자연 대체.
4. **`Job.h`는 행위 없는 구조** — 상태머신 35줄을 W6에 동반 도입해도 "대기 모델 불변" DoD를 건드리지 않는다.

시그널 충돌 해소: `Job::finished(State, QString)`와 러너 고유 `finished(bool, int, QString)`가 오버로드로 공존하면 connect마다 `qOverload` 강제 — 러너 고유 finished/failed를 폐기하고 **결과 페이로드는 pull 접근자**로 (finished 슬롯 시점엔 객체 생존 — `deleteLater` 전). 단 라이브 로그는 pull 불가 — one-shot 소비자 6파일 전부가 `readyReadStandardOutput`을 라이브 구독 중(레포 실측 2026-07-21)이므로 **`outputLine` 시그널은 유지**한다.

```cpp
// controller/async/ProcessJob.h — 개정 2: 러너·Job 일체형 (W6 도입, 1회용)
#pragma once
#include "Job.h"
#include <QProcess>

class ProcessJob : public Job {
    Q_OBJECT
public:
    ProcessJob(QString exe, QStringList args, QObject* parent = nullptr)
        : Job(parent), m_exe(std::move(exe)), m_args(std::move(args)) {}

    void start() override;      // .cpp — 구 ProcessRunner::runAsync 본문 그대로:
                                // exe 검증 → env·채널 모드·UTF-8 → connect 먼저 → QProcess::start
    void cancel() override {    // 추적 PID kill — 상태는 즉시 Cancelled, 늦은 finished 는 터미널 잠금이 삼킨다
        if (state() != State::Running) return;
        if (m_proc) m_proc->kill();
        setState(State::Cancelled, QStringLiteral("사용자 취소"));
    }

    // 결과 페이로드는 pull — finished 슬롯 시점(객체 생존 중)에 읽는다
    int exitCode() const { return m_exitCode; }
    QString stdoutText() const { return m_buf; }

signals:
    void outputLine(QString line);   // 라이브 로그 스트리밍 (소비자 6파일 실측 필요분)

private:
    QString m_exe; QStringList m_args;
    QProcess* m_proc = nullptr;
    QString m_buf;                   // UTF-8 라인 조립 버퍼 (1회용 — 잔류 상태 불가)
    int m_exitCode = -1;
};
```

env 특수화(추가 env·채널 모드 Merged/Separate)는 생성 파라미터/세터로 준다 — 1회용 객체라 상속 특수화가 불요하다. 호출부는 2장의 "한 줄 축소"가 Job 계약으로 바뀔 뿐이다:

```cpp
auto* job = new ProcessJob(solverExe, args, this);
connect(job, &Job::finished, this, &X::onDone);        // connect 먼저
connect(job, &ProcessJob::outputLine, this, &X::onLog);
job->start();                                          // start 나중 — W10 전에도 이미 Job 계약
```

`cancel()`의 안전성은 3-1절 터미널 잠금이 보증한다 — `Cancelled` 전이 후 kill 여파로 도착하는 `QProcess::finished`가 `Failed` 재전이를 시도해도 잠금이 무시한다 (병합 전 스케치에는 이 가드가 없어 `finished` 이중 방송 버그가 있었다 — 3-1절 개정 참조).

---

## 3. W10 형태 — Job 표면: 상태머신 + ProcessJob + DaemonHost + WorkerJob

W10은 **동작**을 바꾼다. 호출자가 "이게 외부 exe인지 데몬 명령인지 워커 스레드인지" 모르게 하는 **Job 표면 하나**를 만들고, 구현을 실행 주체 기준 세 갈래(ProcessJob·DaemonHost·WorkerJob)로 가른다.

> **개정 2**: 실행 주체 3갈래 구도는 유지되나 **Job 서브클래스는 2종** — ProcessJob(2-1절 — W6에서 러너와 일체로 도입)·WorkerJob(3-4절). 데몬 갈래는 DaemonHost + 도메인 파사드로 간다 (3-3절).

### 3-1. Job 베이스 — 상태머신 + 시그널 (최소)

```cpp
// controller/async/Job.h
#pragma once
#include <QObject>
#include <QString>

class Job : public QObject {
    Q_OBJECT
public:
    enum class State { Pending, Running, Succeeded, Failed, Cancelled };
    Q_ENUM(State)

    explicit Job(QObject* parent = nullptr) : QObject(parent) {}
    State state() const { return m_state; }      // 늦은 구독자용 pull (통지 유실 대비)

    virtual void start()  = 0;                   // 각 구현이 정의
    virtual void cancel() {}                     // 협조적 취소 (기본 no-op)

signals:
    void started();
    void progressed(int percent);                // -1 = 불확정(indeterminate)
    void finished(State result, QString reason);

protected:
    void setState(State s, const QString& reason = {}) {
        if (m_state == s) return;
        if (m_state == State::Succeeded || m_state == State::Failed
            || m_state == State::Cancelled) return;  // 개정 2: 터미널 잠금 — 늦은 완료의 재전이 무시
        m_state = s;                             // 상태 변경은 이 한 곳에서만 (불법 전이 차단)
        if (s == State::Running) emit started();
        if (s == State::Succeeded || s == State::Failed || s == State::Cancelled)
            emit finished(s, reason);            // 전이 지점 = 시그널 방송 지점
    }
private:
    State m_state = State::Pending;
};
```

> **개정 2 — 터미널 잠금**: 위 `setState`의 둘째 가드가 없으면 `cancel()`이 `Cancelled`로 전이(= `finished` 방송)한 뒤, kill 여파로 늦게 도착한 `QProcess::finished`가 `Failed` 재전이를 통과시켜 **`finished`가 두 번 방송**된다 (검토 중 발견 — 원 스케치의 실버그. DaemonCommandJob 스케치엔 `state() != Running` 가드가 있었으나 ProcessJob 스케치엔 없었다). 터미널 도달 후 모든 전이를 이 한 곳에서 무시하면, 각 Job 구현의 늦은-결과 가드는 이중 안전장치로 강등된다.

### 3-2. ProcessJob — 외부 exe (스레드 0개)

> **개정 2 — 본 절은 2-1절 병합으로 대체**: ProcessJob은 러너를 소유하지 않고 스스로 QProcess를 구동한다 (일체형·W6 도입). 아래 원문은 병합 전 2층 형태의 보존본 — "번역만 한다"는 관찰이 곧 병합의 근거였다.

2장의 `ProcessRunner`를 Job 상태로 **번역**만 한다. 새 스레드 없음.

```cpp
// controller/async/ProcessJob.h
#pragma once
#include "Job.h"
#include "ProcessRunner.h"

class ProcessJob : public Job {
    Q_OBJECT
public:
    ProcessJob(QString exe, QStringList args, QObject* parent = nullptr)
        : Job(parent), m_exe(std::move(exe)), m_args(std::move(args)) {}

    void start() override {
        if (state() != State::Pending) return;
        m_runner = new ProcessRunner(this);
        connect(m_runner, &ProcessRunner::finished, this, [this](bool ok, int code, QString) {
            ok ? setState(State::Succeeded)
               : setState(State::Failed, QStringLiteral("종료 코드 %1").arg(code));
        });
        connect(m_runner, &ProcessRunner::failed, this, [this](const QString& r) {
            setState(State::Failed, r);
        });
        setState(State::Running);
        m_runner->runAsync(m_exe, m_args);       // QProcess 비동기 — 스레드 0개
    }
    void cancel() override {
        if (state() != State::Running) return;
        if (m_runner) m_runner->cancel();
        setState(State::Cancelled, QStringLiteral("사용자 취소"));
    }
private:
    QString m_exe; QStringList m_args;
    ProcessRunner* m_runner = nullptr;
};
```

### 3-3. DaemonHost — 외부 데몬 명령 (스레드 0개, 프로세스는 장수)

NX·Journal·MCU·Sensitivity 데몬은 프로세스가 오래 살며 명령을 반복 처리한다 — one-shot(2-1절)과 달리 프로세스 종료는 완료가 아니라 **사망**이고, 완료 사건은 명령 1건 단위로 온다. 그래서 `ProcessJob`을 재사용하지 않고, 데몬 수명·명령 큐를 맡는 장수 객체 **`DaemonHost`** 를 따로 둔다 — 신설이 아니라 기존 `DashExtensionProcess` 데몬 부분의 이식이다.

**변경점 — 기동 완료를 이벤트로 수신 (`bool startDaemon()` 재계약, P8)**

현행 `bool startDaemon()`은 "true 반환 = 지금 ready"를 약속하는 동기 계약이라, 반환할 때까지 메인 스레드가 `waitForStarted(30000)`와 `[READY]` busy-wait(NX 최대 120초)에 정지한다. 이 계약 하나를 걷어낸다:

```cpp
// 현행 — 반환값이 ready 를 보증: 반환까지 메인 스레드 프리즈 (NX 최대 120s)
bool startDaemon();

// 변경 — 즉시 반환: 기동 완료는 시그널로 통지
void start();
signals:
    void ready();   // "[READY]" 라인 수신 시
    void died();    // 프로세스 종료 시 — 데몬에서 종료는 완료가 아니라 사망.
                    //   진행 중·대기 명령은 commandFailed 로 drain
```

`readyReadStandardOutput → onDaemonReadyRead` connect 는 이미 있다 — busy-wait 루프 2곳(`:97-108`·`:150-159`)과 `waitForStarted`(`:143`)만 삭제하면, 이미 연결된 시그널 경로가 `[READY]`를 배달한다. NX 데몬 최초 기동의 120초 프리즈가 소멸하는 지점이 여기다.

**Daemon 명령 — 기존과 동일 (무변경)**

- **명령 경로**: "무조건 enqueue → ready 전이면 큐 대기 → `[READY]` 수신 시 flush"가 기존재한다 (`sendCommand`·`trySendNext`·`handleDaemonLine`의 `m_commandQueue` 경로). 그대로 쓴다 — 기동이 비동기가 되어도 명령 순서는 이 큐가 흡수한다.
- **소비 표면**: 명령 완료는 지금처럼 기존 도메인 파사드 4곳(`DashSolverNxCad` 등)이 `commandCompleted`를 도메인 시그널(`loadPrtCompleted` 등)로 번역한다. 명령 1건을 Job 으로 감싸는 `DaemonCommandJob`은 도입하지 않는다 (개정 2 — Job 서브클래스는 ProcessJob·WorkerJob 2종). 취소·늦은 결과 폐기는 host 가 흡수 — `DaemonHost::cancel(id)`: 큐 미전송이면 제거, 전송 중이면 결과 폐기.

**유의점·후속 아이디어 (요지)**

- **기동 중 간섭 2건 — 규칙 필요**: 동기 프리즈가 암묵적 전역 락이어서 불가능했던 "Starting 중 종료·설정 변경"이 비동기화로 가능해진다. ⑴ Starting 중 `stop()` = kill + 대기 명령 `commandFailed` drain ⑵ 설정 변경은 **기동 시점 스냅샷**으로 무간섭화(`start()` 순간 exe·args 지역 복사 — 변경은 다음 기동부터 적용). W10-c(#212) DoD 보강 권고.
- **호출 순서 안전은 host 가 보증**: 어떤 순서로 공개 메서드가 불려도 깨지지 않는 것은 상태머신의 책임 — view 버튼 비활성화(W11)는 표시일 뿐 정확성 수단이 아니다 (기동 진입점 7곳 대부분이 버튼 아닌 프로그램적 경로 — 8-2절).
- **데몬 예열(pre-boot)**: 기동이 비동기·큐잉 기반이 되면 앱 시작·NX 경로 설정 등 이른 시점의 `start()` 선행 호출로 부팅 120초를 사용자 유휴 시간과 겹칠 수 있다 — W10-c 범위 밖, 백로그 후보(#212 에 기록).

### 3-4. WorkerJob — in-process 무거운 작업 (스레드 O)

검토의견의 "비동기 래퍼"의 실체. `QtConcurrent::run`으로 지정 풀에 오프로딩하고, `QFutureWatcher`가 완료를 시그널로 되돌린다. **여기서 처음으로 스레드가 등장**한다.

```cpp
// controller/async/WorkerJob.h
#pragma once
#include "Job.h"
#include <QFutureWatcher>
#include <QThreadPool>
#include <functional>

struct WorkerResult { bool ok = false; QString reason; };

class WorkerJob : public Job {
    Q_OBJECT
public:
    // task: 워커 스레드에서 실행 — 입력 스냅샷만 캡처, 위젯/GUI 접근 금지
    WorkerJob(std::function<WorkerResult()> task, QThreadPool* pool, QObject* parent = nullptr)
        : Job(parent), m_task(std::move(task)), m_pool(pool) {}

    void start() override {
        if (state() != State::Pending) return;
        // QFutureWatcher 는 자기(메인) 스레드에서 finished 를 emit → 슬롯도 메인에서 (마샬링 자동)
        connect(&m_watcher, &QFutureWatcher<WorkerResult>::finished, this, [this] {
            const WorkerResult r = m_watcher.result();
            r.ok ? setState(State::Succeeded) : setState(State::Failed, r.reason);
            // 취소 후 도착한 늦은 결과라면 위 setState 는 터미널 잠금(3-1절)이 무시한다
        });
        setState(State::Running);
        m_watcher.setFuture(QtConcurrent::run(m_pool, m_task));   // 지정 풀에 오프로딩
    }
    // 협조적 취소: DLL 실행 도중엔 중단 불가 → 상태는 즉시 Cancelled, 늦은 결과는 폐기.
    // 폴링 가능한 task(8-5절 DOE 배치 등)가 생기면 shared_ptr<atomic<bool>> 취소 채널을
    // task 인자로 추가한다 — 맨 멤버 플래그는 금지 (즉시 Cancelled 방송 → 호출부 deleteLater
    // 후에도 task 가 참조 → use-after-free)
    void cancel() override {
        setState(State::Cancelled, QStringLiteral("사용자 취소"));
    }

private:
    std::function<WorkerResult()> m_task;
    QThreadPool* m_pool;
    QFutureWatcher<WorkerResult> m_watcher;
};
```

```cpp
// WorkerJob.cpp (include 만)
#include "WorkerJob.h"
#include <QtConcurrent/QtConcurrent>
```

무거운 DLL 작업을 `WorkerJob`으로 감싸는 배선 — **입력 스냅샷**을 람다에 캡처해 워커로 넘기는 것이 핵심(실행 중 위젯 상태 변화와 무관해진다):

```cpp
// 모핑 DLL(비재진입 등급 2) → 모핑 전용 직렬 풀(maxThreadCount=1)에서 실행
Job* makeMorphJob(const MorphParams& snapshot) {
    return new WorkerJob([snapshot]() -> WorkerResult {
        // ── 여기는 워커 스레드 ── 스냅샷만 사용, 위젯 접근 절대 금지
        DashMR::OperatorMorph op;
        const bool ok = op.Morph(snapshot.points, snapshot.handles);
        return { ok, ok ? QString() : QStringLiteral("모핑 실패") };
    }, morphingSerialPool());              // 직렬 풀 → 같은 서브시스템 작업이 줄 선다 (락 불요)
}
```

### 3-5. 호출부 — 종류 무관하게 동일한 사용법

위젯 슬롯은 Job이 ProcessJob인지 DaemonCommandJob인지 WorkerJob인지 **모른다**. 코드가 동일하다:

```cpp
// view/SomeWidget.cpp
void SomeWidget::onRunClicked() {
    if (m_running) return;                     // 재진입 가드 (실행 중 버튼 비활성은 W11)

    const MorphParams snapshot = collectFromWidgets();   // 1. 입력 스냅샷 (메인 스레드)

    Job* job = makeMorphJob(snapshot);         // 2. Job 생성 (내부 구현 비가시)
    //   또는  new ProcessJob(solverExe(), args);          ← 아래 connect/start 코드는 완전히 동일
    //   또는  new DaemonCommandJob(nxDaemonHost(), cmd);  ← 마찬가지

    // 3. connect 먼저 (start 전에!)
    connect(job, &Job::started, this, [this] {
        m_running = true; m_runBtn->setEnabled(false);
    });
    connect(job, &Job::progressed, this, [this](int pct) {
        m_progress->setValue(pct);
    });
    connect(job, &Job::finished, this, [this, job](Job::State s, const QString& reason) {
        m_running = false; m_runBtn->setEnabled(true);
        if      (s == Job::State::Succeeded) showResult();
        else if (s == Job::State::Failed)    notifyError(reason);   // W12 통지 규칙
        job->deleteLater();
    });

    job->start();                              // 4. start 나중 — 즉시 반환, 이벤트 루프 상주
}
```

취소 버튼도 종류 무관하게 `job->cancel();` 한 줄. ProcessJob이면 PID kill, DaemonCommandJob이면 늦은 결과 폐기, WorkerJob이면 협조적 플래그로 갈라지지만 호출부는 모른다.

> **개정 2**: 위 "3종 동일"은 **2종(ProcessJob·WorkerJob)** 으로 준다 — `new DaemonCommandJob(...)` 예시행은 폐기 (3-3절). 데몬 작업의 위젯 소비는 지금처럼 도메인 파사드 시그널(`loadPrtCompleted` 등) 구독이다. 실행 방식이 실제로 다른 두 갈래(외부 프로세스 vs 스레드 풀)에 대한 표면 통일 — W11 진행·W12 통지·일괄 취소 — 은 그대로 성립한다.

### 3-6. 호출·구독 관계 도식 — 갈래별 층 구조와 상태

3장 전체의 호출(↓)·구독(↑) 관계를 갈래별로 나눈 도식. 공통 원칙 — **호출은 아래로만, 시그널은 위로만**, 아래층은 위층을 모른다(역참조 0). 읽는 법: `▼` 가 층 경계이고, 경계 **직전의 `↓ 호출` / `↑ 구독` 쌍이 그 경계를 건너는 것의 전부**다(쌍 밖에서는 아무것도 경계를 넘지 않는다). 층 안의 `상태` 줄은 그 층이 가질 수 있는 상태의 전부이며, `상태(소유)` 가 붙은 층이 그 갈래의 상태머신 소유자다.

**갈래 ① ProcessJob — one-shot exe (전 층 메인 스레드, 실행만 별도 프로세스)**

```
[표면] 호출부 — 위젯/컨트롤러 슬롯 (메인 스레드 · 3-5절)
   │   상태: 없음 — 버튼 비활성 등 UI 가드는 Job 시그널에서 파생 (W11)
   │   ※ 상세값(exitCode·stdout)은 finished 수신 후 pull 접근자로 (2-1절)
   │
   │   ↓ 호출   job->start() / job->cancel()
   │   ↑ 구독   started() / progressed(int) / finished(State, reason)
   ▼

[Job] ProcessJob — 러너 일체형 번역 어댑터 (메인 스레드 · 2-1절)
   │   상태(소유): Pending → Running → {Succeeded | Failed | Cancelled}
   │      터미널 도달 후 모든 재전이 무시 — 터미널 잠금 (3-1절)
   │   ※ 번역 규칙: 정상 종료 code 0 → Succeeded · 그 외 → Failed
   │      kill 뒤 늦게 오는 finished 는 터미널 잠금이 삼킨다
   │
   │   ↓ 호출   m_proc.start(exe, args) · cancel() 시 m_proc.kill()
   │   ↑ 구독   QProcess::finished / errorOccurred / readyReadStandardOutput
   ▼

[실행부] one-shot exe — 별도 프로세스 (QProcess 가 대리)
       상태: NotRunning → Starting → Running → NotRunning (QProcess::state)
       산출: exitCode · exitStatus · stdout — 종료가 곧 완료 (one-shot 계약)
       자기 주소 공간 → cancel = kill 이 안전한 이유 (프로세스 격리)
```

**갈래 ② WorkerJob — in-process 무거운 작업 (실행부만 워커 스레드)**

```
[표면] 호출부 — ① 과 완전 동일, 코드까지 동일 (3-5절)
   │   상태: 없음
   │
   │   ↓ 호출   job->start() / job->cancel()
   │   ↑ 구독   started() / progressed(int) / finished(State, reason)
   ▼

[Job] WorkerJob — 오프로딩 + 마샬링 어댑터 (메인 스레드 · 3-4절)
   │   상태(소유): Pending → Running → {Succeeded | Failed | Cancelled}
   │      cancel() 은 즉시 Cancelled 확정 — 늦은 결과는 터미널 잠금이 삼킨다
   │   ※ 단 DLL 은 반환할 때까지 계속 돌며 그동안 직렬 풀을 점유한다
   │
   │   ↓ 호출   QtConcurrent::run(전용 풀, task) — 값 스냅샷만 캡처해 투입
   │      cancel() 은 이 경계를 내려가지 않는다 (Job 층에서 종결)
   │   ↑ 구독   QFutureWatcher::finished — watcher 가 메인 스레드 소속이라
   │      emit 도 메인에서 (스레드 경계 마샬링이 이 경계에서 끝난다)
   ▼

[실행부] task 본문 — 전용 풀의 워커 스레드 (DLL 전용 아님 — 8-5절 전수)
       상태: 풀 큐 대기 → 실행 중 → 반환(WorkerResult)
       대상: 모핑 DLL(순위 1·2) · FE/RST·KPI 파싱(3·4) · export·VTU/CSV 쓰기(5·6)
       풀 배정: 서브시스템의 숨은 공유 상태 기준 — 모핑 직렬 · RW 직렬 (8-5절 표)
       경계 통과물: 내려갈 땐 값 스냅샷 · 올라올 땐 반환값 — 공유 상태 0
       주소 공간 공유 → 강제 중단 불가 (① 의 kill 과의 차이):
       불투명 호출(DLL·reader.Update)은 늦은 결과 폐기만, 폴링 가능한
       파싱 루프는 협조적 취소 확장 여지 (3-4절 cancel 주석)
```

갈래 ③(데몬 — `DaemonHost` + 도메인 파사드)은 **기존 구조를 그대로 쓰는 갈래라 도식하지 않는다** (3-3절 — 명령 경로·소비 표면 무변경, 변경은 기동 완료의 이벤트 수신뿐).

두 갈래의 공통 구조:

- **표면 - Job - 실행부 3층**. 상태머신은 Job 한 곳 — 실행부의 원시 상태(QProcess state·task 진행)를 Job 이 5-상태 어휘로 번역해 위로 올린다.
- **표면은 상태를 갖지 않는다** — 표면의 표시/비활성(W11)은 아래층 시그널의 파생물일 뿐, 정확성은 아래층 상태머신이 책임진다.

---

## 4. W10 비동기 구현 갈래 — 실행 주체 3갈래 + 완료 변형 2

3장까지의 코드가 보인 실행 주체 3갈래가 곧 W10의 구조 전부다:

| # | 갈래 | 핵심 구조 | 본 문서 |
|:---:|---|---|---|
| ① | 외부 one-shot exe | `QProcess::finished` → `ProcessJob` (스레드 0 — 러너 일체형, W6 도입) | 2-1절 (개정 2) |
| ② | 외부 데몬 명령 | 명령 큐 `commandCompleted`·`daemonReady` → `DaemonHost` + **도메인 파사드** (스레드 0 — 개정 2: `DaemonCommandJob` 폐기) | 3-3절 |
| ③ | in-process 워커 | `QFutureWatcher::finished` → `WorkerJob` (직렬 풀) | 3-4절 |

여기에 **완료 원천·판정 변형 2건**이 얹히는데, 새 갈래가 아니라 ①~③ Job의 내부 디테일이다:

- **C API 런처 완료** — C 콜백 → `invokeMethod(QueuedConnection)` 마샬 → Job 번역. 완료 원천만 다른 ProcessJob 변형이며, 경계 어댑터는 실코드 6곳에 기존재 (1-3절).
- **파일 완료 판정 — 폴링 → 완료 이벤트 구독** — `waitForFile` 폴링 제거의 본질은 **작업 완료 시그널 구독 → 파일 검증** 순서("파일 존재"가 아니라 시그널이 완료의 근거). 파일럿의 `updatePrtGeometryCompleted` 구독이 바로 ②의 완료 시그널이다. 완료 시그널이 없는 외부 산출물에 한해 `QFileSystemWatcher`/`QTimer` 콜백을 **보조 수단**으로 쓴다 (예제 없음 — 6장 표).

백로그 축 대응: 외부 축 = ①·② + 완료 변형 2건, 워커 축 = ③.

---

## 5. 파일 구성 요약 — 무엇이 어디에 놓이나

```
controller/async/            ← W6·W10 신설 (실행 관심사 한 곳) — 개정 2: 이 목록이 인프라의 전부
├── Job.h                    (W6·개정 2) 상태머신 + 시그널 3종(started·progressed·finished) — 터미널 잠금 포함
├── ProcessJob.h/.cpp        (W6·개정 2) QProcess 실행 + Job 표면 일체형 (구 ProcessRunner 병합) · outputLine
├── DaemonHost.h/.cpp        (W10) 데몬 수명·명령 큐 — 비동기 기동(ready → 큐 flush) · cancel(id) (개정 2)
├── WorkerJob.h/.cpp         (W10) in-process 작업 → 풀 오프로딩, 완료를 Job 시그널로
└── ThreadPools.h/.cpp       (W10) 서브시스템별 직렬 풀 접근자 (morphingSerialPool 등)

(개정 2: DaemonCommandJob.h 는 도입하지 않는다 — 3-3절. JobManager·스케줄러·우선순위 큐·
 Job 트리·재시도 정책의 부재는 누락이 아니라 설계 의도 — 직렬성은 직렬 풀과 host 큐가 이미 제공)

기존 파일의 변화
├── model/DashJobRunner.cpp        waitForFile 폴링 → 완료 이벤트 구독 (4장 "파일 완료 판정")
├── controller/DashExtensionProcess.*  one-shot 경로 수리 → ProcessJob 로 추출·병합 (개정 2) · 데몬 큐/startDaemon → DaemonHost 형태로 이식(busy-wait 제거)
├── controller/DashManager.cpp     ExecuteMorphing 코어는 그대로(이미 파라미터화) — WorkerJob 람다가 호출
└── view/*Widget.cpp               QProcess 직접 소유 제거 → Job 생성/구독 (3-5절 형태)
```

호출 방향 (의존은 view → controller 단방향 유지):

```
[view] 위젯 슬롯
   │   Job 생성 · 시그널 구독 · start (3-5절) — 데몬 작업은 도메인 파사드 시그널 구독 (개정 2)
   ▼
[controller/async] Job (표면)
   │   ProcessJob → QProcess (스레드 0 — 러너 일체형, 개정 2)
   │   WorkerJob  → QtConcurrent → QThreadPool (직렬 풀) → DLL
   │   (데몬)     → 도메인 파사드 → DaemonHost 명령 큐 → 장수 QProcess (스레드 0 — Job 아님, 개정 2)
   ▼
[완료] Job::finished / 파사드 도메인 시그널 → 메인 스레드 슬롯 → UI 갱신
```

---

## 6. 이 최소 예제가 뺀 것 (프로덕션과의 격차)

최소 골격을 실제 W10으로 키울 때 채워야 하는 것들 — 전부 [194-1-async-execution-patterns](194-1-async-execution-patterns.md) 에 상세:

| 뺀 것 | 최소 예제의 처리 | 실제 필요 |
|---|---|---|
| 워커 선결 조건 5건 | 없음 | 싱글톤 락·모핑 상태 분리·컨텍스트 규약·cout 스왑 제거·GUI/VTK 규칙 (5-3절) — **WorkerJob 투입의 게이트** |
| DLL 스레드 안전 3등급 | 무조건 직렬 풀 가정 | 등급 판별 후 풀 배정 (5-2절) — 등급 3(NXOpen)은 외부 프로세스 격리 |
| 진행 보고 | `progressed` 시그널만 정의 | 외부 = `[PROGRESS] n%` additive 마커, 내부 = DLL 진행 콜백 → 시그널 (W11) |
| 취소/실패 정책 | 상태 전이만 | P1~P5 (부분 결과 보존·배치 취소 범위·continue-on-error·재시도 없음 — 4-1절) |
| 파일 완료 판정 | 4장 완료 변형 요약만 | 완료 시그널 구독 → 파일 검증 순서(원칙) · 시그널 없는 외부 산출물만 `QFileSystemWatcher`/`QTimer` 보조 콜백 |
| 데몬 프로토콜·이식 | 3-3절 골격 (기동 비동기·큐 flush) | 기존 `DashExtensionProcess` 이식 — 마커 프로토콜 파싱·`bool startDaemon()`→`void` 재계약·`stopDaemon` 동기 종료 대기 제거 ([201-1-qprocess-antipattern-catalog](201-1-qprocess-antipattern-catalog.md) P1·P2·P8) |
| 배치 오케스트레이션 | 단건만 | Job 연쇄(참조: `runDirectJobs` `loadPrtCompleted` 구독) — 파일럿 = DOE 배치 |

**요지**: 위 골격(1~3장)은 "코드가 어떻게 생겼나"를 보여주는 최소치다. `ProcessJob`·`DaemonHost`(개정 2 — DaemonCommandJob 폐기)는 선결 조건과 무관하게 거의 그대로 쓸 수 있지만(외부 축 = 스레드 0), `WorkerJob`은 5-3절 게이트를 통과한 뒤에만 실제 투입한다 — 안 그러면 "프리즈가 레이스로 바뀐다".

---

## 7. 참고

- 스레드·전달 메커니즘 도식: [206-1-w6-w10-thread-execution-design](206-1-w6-w10-thread-execution-design.md)
- 판정·상세 설계(완료 처리 3방식·DLL 3등급·선결 5건·서브태스크 a\~f·정책 P1\~P5): [194-1-async-execution-patterns](194-1-async-execution-patterns.md)
- QProcess 블로킹 지점 전수(P1~P8 — 데몬 기동 P1·동기 종료 P2·API 계약 P8): [201-1-qprocess-antipattern-catalog](201-1-qprocess-antipattern-catalog.md)
- 개념(이벤트 루프·시그널·Job·스레드 층위): [193-1-async-execution-models](193-1-async-execution-models.md)
- 실행 순서·규모: [200-3-prioritized-backlog](200-3-prioritized-backlog.md) 5-1절
- 코드 모범 선례: `model/DashModelRunner.cpp`(완전 시그널 구동) · `model/DashJobRunner.cpp:2326-2336`(`loadPrtCompleted` 연쇄) · `:1170`(C 콜백 마샬링) · `controller/DashAnalysisLauncher.cpp:233`(QtConcurrent + QFutureWatcher = WorkerJob 원형)
- Qt 5.15 문서: `QProcess`(본래 비동기)·`QtConcurrent::run`(풀 지정 오버로드)·`QFutureWatcher`·`QMetaObject::invokeMethod`(콜백 마샬링)

---

## 8. 부록 — 동기 → 비동기 전환 대상 전수 목록 (종류별)

> 출처: [206-1-w6-w10-thread-execution-design](206-1-w6-w10-thread-execution-design.md) 1-3절(3패턴)·2-2절(6클래스) · [201-1-qprocess-antipattern-catalog](201-1-qprocess-antipattern-catalog.md) P1~P8(지점 전수) · [194-1-async-execution-patterns](194-1-async-execution-patterns.md) 2-2·2-3·5-4절(우선순위). 라인 앵커는 분석 시점(2026-07-15/16) `dev` 기준.\
> 레포 직접 재검증(2026-07-21, `dev` `52965e4`): `waitFor*` **23곳/4파일**(ExtensionProcess 11 · JobRunner 7 · ModelBuilder 3 · TopOptPostprocessDialog 2 — 카탈로그 24곳 대비 1곳 감소) · `msleep` **5곳**(전부 JobRunner) · `processEvents` **58곳/10파일**(실호출 — model 41 + view 17).\
> 신규 종류 부재 확인(동일 재검증): 중첩 `QEventLoop::exec` 0 · `QProcess::execute`/`system()`/`popen` 0 · `std::async`/`std::future` 0 · `QThread::wait`/`QSemaphore`/`QWaitCondition` 0. `QFutureWatcher::result()`(`DashAnalysisLauncher.cpp:590`)는 `finished` 슬롯 내부 호출이라 비차단 — 대상 아님.

### 8-1. one-shot 동기 완주·기동 확인 대기 (P3·P4) → ProcessJob (3-2절)

| 지점 | 내용 | 최대 블로킹 |
|---|---|:---:|
| `DashExtensionProcess::runBlocking` `:335-366` | `waitForStarted`+`waitForFinished(300s)` — 호출처 0, 휴면 지뢰 (삭제 후보) | 300s |
| `DashJobRunner::runMotionWriter` `:666-729` | `waitForFinished(500)`+`processEvents` 5분 반복 — motion-launcher 큐(`:751-858` 모범)로 이식 | 300s |
| `DashExtensionProcess::killOrphans` `:52-69` | 광역 taskkill 후 `waitForFinished(3000)` — W6에서 PID 추적 kill로 축소 | 3s |
| `start()` 직후 `waitForStarted` 5곳 — `DashModelBuilder:637` · `DashJobRunner:685,848` · `TopOptPostprocessDialog:1794` · `DashExtensionProcess:354` | `errorOccurred(FailedToStart)` 시그널로 대체 (선례 `DashModelRunner.cpp:184-201`) | 3~30s |

### 8-2. 데몬 기동 동기 대기 (P1) → DaemonHost 비동기 기동 + `daemonReady` → 큐 flush (3-3절)

| 지점 | 내용 | 최대 블로킹 |
|---|---|:---:|
| `DashExtensionProcess::startDaemon` `:143` | `waitForStarted(30000)` | 30s |
| 같은 함수 `:151-159` · 이중 기동 가드 `:97-108` | `[READY]` busy-wait — 기본 15s, NX 120s(`DashSolverNxCad.cpp:16`) | 120s |
| `DashSolverNxCad::enqueueLoadPrt`/`enqueueUpdatePrtGeometry` `:124-126,147-149` | 첫 enqueue가 동기 부팅 유발 | 120s |
| 호출자 — `DashSolverNxCad:115` · `DashManager::enqueueLaunch:157` · `DashModelRunner:240` · `DashModelBuilderMCU:120` + 위젯 직접 3곳(`DashModelBuilderMCUWidget:193` · `DashModelRunnerMCUWidget:197-198` · `DashModelRunnerWidget:244`) | 동기 부팅 경로 진입점 7곳 | — |

### 8-3. 동기 종료·취소 대기 (P2) → kill 발사 후 즉시 반환, 정리는 `finished` 슬롯

| 지점 | 내용 | 최대 블로킹 |
|---|---|:---:|
| `DashExtensionProcess::stopDaemon` `:178-183` + 소멸자 `:18-21` | write("exit") → `waitFor*` 연쇄 — 앱 종료 시 데몬 수만큼 직렬 누적 | 8s×N |
| `DashExtensionProcess::runAsync` 도입부 `:379-384` | 이전 프로세스 kill+`waitForFinished(2000)` | 2s |
| `DashModelBuilder::stopTraining` `:1237-1243` | terminate→kill 재대기 | 6s |
| `DashJobRunner` 소멸자 `:455-462` · `cancelAllRuns` `:946-948` · motion-writer 타임아웃 `:711-714` | 인자 없는 `waitForFinished()`=30s/프로세스 · kill→terminate 에스컬레이션 역전 | 30s×N |
| `TopOptPostprocessDialog` 소멸자 `:2155-2157` | 다이얼로그 닫기 정지 | 3s |

### 8-4. 파일 폴링·고정 슬립 — 완료 이벤트 무시 (P5·P6) → **완료 시그널 구독 → 파일 검증** (4장 완료 변형)

| 지점 | 내용 | 최대 블로킹 |
|---|---|:---:|
| `DashJobRunner::waitForFile` `:2351-2364` ← `runWbpjDoeAsync:2670-2673` | `updatePrtGeometryCompleted` 시그널 무시하고 STP 폴링 — **W10 파일럿**. 비동기 등가물이 같은 파일에 실존(`runDirectJobs:2326-2336`) | 600s/케이스 |
| `DashJobRunner::waitForVtuFileComplete` `:598-664` | `msleep(100)`+`processEvents` 폴링 + 크기 0.5s 안정화 휴리스틱(오판 레이스 내장) | 60s |
| `DashJobRunner.cpp:1576` | `msleep(1000)` 고정 슬립 — dfsxml 모핑+MBD 루프(`:1561-1676`) 도입부 | 반복 |

### 8-5. in-process 동기 실행 (GUI 스레드 점유) → WorkerJob + 직렬 풀 (3-4절 — 선결 5건 게이트 후, 5-4절 우선순위 순)

| 순위 | 작업 | 진입 경로 | 풀 |
|:---:|---|---|---|
| 1 | DOE 배치 모핑 루프 | `DashMorphingDoeExecutor::Execute` `:304-375` → `MorphFromDoeSamples`(`DashManager.cpp:870`) — `processEvents`조차 없는 완전 정지 | 모핑 직렬 |
| 2 | 단건 모핑·프리뷰 N루프 | `DashManager::ExecuteMorphing` `:314-343` · `DashOptimizer.cpp:1286`(+`processEvents:1913,1938`) · 위젯 내 모핑 루프 `DashGeometryParameterWidget.cpp:1500-1565` | 모핑 직렬 |
| 3 | FE 모델 파싱 | `reader.Update()`(`DashAnalysisModelContext.cpp:312`) · `load_contents`(`:855`) | RW 직렬 |
| 4 | RST/KPI 파싱 7종 | `DashDataProcessor` process* `:1466,2049,3049,3491,3823,4104,4383` — `processEvents` 13곳 산재 | RW 직렬/분할 |
| 5 | export/serialize/메시 갱신 | `abaqusExportInp:460` · `abaqusUpdateMeshPoints:434` 등 컨텍스트 write 계열 | RW 직렬(1번과 순서 보장) |
| 6 | VTU/VTK·CSV 쓰기 | `DashManager.cpp:862` · `DashAnalysisLauncher.cpp:1477,972` | 소형 — 여력 시 |

### 8-6. `processEvents` 재진입 창 (P7) → 별도 수리가 아니라 8-1~8-5 전환의 부산물로 제거

- **model 41곳** — `DashJobRunner` 19 · `DashDataProcessor` 14 · `DashResultProcessor` 8. DoD "`model/` processEvents 0건"이 봉인 게이트 (#64 재진입 크래시 계급의 원천).
- **view 17곳** (레포 재검증 보강 — 전수는 [201-1-qprocess-antipattern-catalog](201-1-qprocess-antipattern-catalog.md) 8절 개정 1): `TopOptPostprocessDialog` 6(`:470,532,648,794,1318,2092`) · `DashDataProcessorWidget` 3(`:1517,1526,1538`) · `DashOptimizerWidget` 2(`:1913,1938` — 모핑 프리뷰 루프) · `DashGeometryParameterWidget` 2(`:1532,1572` — 위젯 모핑 루프) · `DashViewOptionsWidget` 2(`:175,187`) · `DashMainWindow` 1(`:2111`) · `DashMeshQualityDialog` 1(`:284`). 두 아종 — **동기 루프 안의 펌핑**(모핑 프리뷰·위젯 모핑 — 재진입 위험 높음, 8-5와 함께 소멸)과 **단발 강제 리페인트**("UI 새로고침 강제" 주석류 — 동기 처리 제거 후 불필요해지는 잔재).

### 8-7. 동기 반환 API 계약 (P8) → 시그널 계약으로 재설계 (지점 수리와 동행 필수)

| API | 현재 계약 | 전환 |
|---|---|---|
| `bool DashExtensionProcess::startDaemon()` | 반환 시점에 ready 확정 — 의존 호출자 4곳(`DashManager:156-162` 등) | `void` + `daemonReady`/`daemonStopped` 시그널, 호출자는 "미기동 시 큐잉 + ready 시 flush" |
| `bool runBlocking(...)` | 반환값 = 프로세스 결과 | 호출처 0 — 삭제 또는 워커 전용 assert |
| `bool DashJobRunner::runMotionWriter(...)` | 반환값 = 성공 여부 — 모핑+MBD 루프 `:1645` 의존 | motion-launcher 큐 형태로 이식 |

**동반 사항 2건** (동기→비동기가 아니라 구조 전제 — W6): 수제 QProcess 6클래스 수렴(2장), 뷰 소유 QProcess 2건(`DashOptimizerWidget::m_fitProcess:2418` · `TopOptPostprocessDialog::m_postprocessProcess:1749` — 유일한 "창 닫힘 = 작업 사망" 지점)의 소유 이전.

**착수 성질**: 8-1~8-4·8-7은 외부 축 — 스레드 없이 즉시 착수 가능. 8-5만 워커 선결 조건 5건 게이트 뒤에 선다. 8-6은 독립 작업이 아니라 나머지 전환의 결과로 소멸한다.

---

## 부록 — Issue 코멘트 이관

본문 발행 후 [#205](205-5-w6-w10-async-minimal-example.md) 에 달린 코멘트 중 **본문을 보충·정정하는 것**만 옮겼다. 파생 위키 페이지 발행 공지 코멘트는 머리글 `파생 문서` 링크로 대체.

### 코멘트 1 — 2026-07-23

3-6절 갈래별 층 구조 도식의 이미지 판 2장 (Obsidian 렌더).

**갈래 ① ProcessJob — one-shot exe (전 층 메인 스레드, 실행만 별도 프로세스)**

<img width="2720" height="1880" alt="갈래 ① ProcessJob 층 구조" src="https://github.com/user-attachments/assets/e01334e1-3793-4e7a-9bbc-8d787f085407" />

**갈래 ② WorkerJob — in-process 무거운 작업 (실행부만 워커 스레드)**

<img width="2720" height="1960" alt="갈래 ② WorkerJob 층 구조" src="https://github.com/user-attachments/assets/b37bfc10-f300-4431-becd-1afd1b6e497a" />

### 코멘트 2 — 2026-07-23

메인 루프 타임라인 대비 도판 2장 — 현재(직렬·블로킹) vs Job 구조(비동기) (Obsidian 렌더).

**현재 — 직렬 (동기 완주 대기) — 계산 중 UI 정지**

<img width="2720" height="1600" alt="현재 — 직렬 타임라인" src="https://github.com/user-attachments/assets/3f62cc57-f24c-443b-b506-586277d335eb" />

**Job 구조 — 비동기 (즉시 반환 · 완료는 시그널)**

<img width="2720" height="1880" alt="Job 구조 — 비동기 타임라인" src="https://github.com/user-attachments/assets/076c99e1-592d-4769-acfd-d0abd1bc59f4" />

### 코멘트 3 — 2026-07-28

#### 검토 — "호출부-Job-실행부" 3층 vs "호출부-실행부" 2층(상태머신 제거) 대안

> 요청: 현행 `호출부 → ProcessJob/WorkerJob → 실행부` 구도를 `호출부 → 실행부(one-shot exe)` · `호출부 → task` 로 줄이고 **Job 상태머신을 제거**하는 안이 더 간단한지 검토.
>
> **결론: 공통 Job 상태머신 구현 결정 유지.**

##### 1. 재구성 — 쟁점은 "층 수"가 아니라 "공통 상태머신"

"실행부"는 우리 클래스가 아니라 `QProcess`(별도 OS 프로세스) 또는 워커 스레드의 DLL 호출이다. 호출부가 여기에 "직접" 붙는다는 건 두 해석으로 갈린다:

- **문자 그대로**(위젯이 `QProcess`/스레드를 직접 소유·배선) = W6 이전 안티패턴(6클래스 각자 배선) 그 자체 → 원점 회귀.
- **합리적 해석**(호출부 → 얇은 러너, 공통 베이스·상태머신만 제거) = 검토 가치 있는 안.

중간 객체는 connect-먼저-start-나중 · UTF-8 라인조립 · C콜백 마샬링 · 늦은-완료 가드를 담아야 하므로 **불가피**하다. 따라서 진짜 쟁점은 "3층↔2층"이 아니라 **불가피한 중간 러너가 공통 상태머신을 공유하느냐**이다.

##### 2. 갈래별 분석 — 답이 비대칭이다 (`cancel` 의미론에서 갈림)

**① exe 갈래 — 상태머신 단독 이득은 약함 (제거 논거가 성립하는 쪽)**

`QProcess`는 이미 비동기 상태머신(state + exitCode + finished/errorOccurred)이다. 그 위 5-상태는 "상태머신 위 상태머신"이고, 3-1절 "이중 방송" 버그는 이 덧layer가 자초한 것:

```
Job 有:  cancel() → Cancelled 방송 ┐
         kill 여파 → finished → Failed 방송 ┘  = finished 2회 → 터미널 잠금 가드 필요
Job 無:  cancel() = kill → finished 1회 → 끝   = 이중 방송 자체가 없음
```

exe에서 취소 = kill = 프로세스 즉시 정지·finished 1회. 상태머신을 걷어내면 그것이 막던 버그도 같이 사라진다. **단**, W6 수렴(exe 검증·UTF-8·env·중복가드)은 유지해야 한다 — 호출부 5~6곳에 `QProcess` 인라인 산포는 안티패턴 복귀. 정답 형태는 "상태머신 없는 얇은 러너"(= 개정 2 병합 전 원래 `ProcessRunner`).

**② worker 갈래 — 상태 가드가 본질적으로 필수 (제거하면 위험)**

취소해도 task(DLL)는 안 멈춘다 → `QFutureWatcher::finished`가 **늦게** 발화 → 호출부가 취소 시점에 이미 `deleteLater` 했으면 죽은 수신자 참조 = **use-after-free (#64 크래시 계급)**. 이 늦은-결과 안전 처리는 덧layer가 자초한 게 아니라 **실행부 성질에서 나오는 본질적 문제**라 제거 불가.

또한 "호출부 → task 직접"은 성립하지 않는다 — 동기면 GUI 프리즈(없애려던 원죄), 비동기면 호출부가 watcher·스냅샷·마샬링·늦은결과 가드를 소유해야 하고 그 "소유하는 객체"가 곧 `WorkerJob`이다. 호출부마다 인라인 복제 = #64를 갈래마다 재생산.

##### 3. 결론 — 공통 Job 상태머신 유지

비대칭은 사실이나, **공통 구현을 유지**한다. 근거:

- **worker 갈래가 안전-필수 상태 가드(터미널 잠금 = 늦은 결과 UAF 차단)를 요구**한다. 이 correctness-critical 로직을 공통 베이스에 **1회** 구현하는 편이 두 러너에 복제하는 것보다 안전하다.
- **exe만 단독으로 얇게 가면 두 갈래가 서로 다른 완료 계약**(`finished(bool,int,QString)` vs 가드형)을 갖게 된다 → 상위 소비자(W11 진행 · W12 통지 · DOE 배치 연쇄·일괄취소)가 갈래별로 분기 처리해야 한다. 공통 5-상태 표면은 종류 무관 단일 소비를 제공한다.
- exe의 "이중 방송" 비용(터미널 잠금 가드 필요)은 인정하나, 공통화의 **안전성·표면 일관성** 이득이 이를 상회한다.

**트레이드오프 명시**: exe 갈래에서 5-상태 상태머신은 국소적으로 과할 수 있다(`QProcess`가 이미 상태 보유). 그럼에도 (a) 전체 표면 일관성과 (b) worker 안전 가드의 단일 구현을 위해 **공통 상태머신 유지**를 택한다. 후속으로 표면 파편화 부담이 커지지 않는 한 이 결정을 뒤집지 않는다.
