# W6·W10 티켓 요약표 (총 9건 · [#211](https://github.com/NumeRealWorks/DashOpti_GUI/issues/211) 폐기 → 활성 8건)

> 관련 Issue: [#205](205-5-w6-w10-async-minimal-example.md)
> 기반 문서: [200-1-release-phasing-plan](200-1-release-phasing-plan.md)
> 원본 문서: [205-5-w6-w10-async-minimal-example](205-5-w6-w10-async-minimal-example.md) — [#205](205-5-w6-w10-async-minimal-example.md) 개념설계 본문 이관본 (최소 구현 골격)

개념설계 [#205](205-5-w6-w10-async-minimal-example.md)(개정 2) 에서 파생된 W6(실행 경로 일원화 — 구조/where) · W10(대기→통지 이벤트 구동 전환 — 행위/how) 티켓 9건([#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207)~[#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215))의 한 줄 요약. **[#211](https://github.com/NumeRealWorks/DashOpti_GUI/issues/211) 은 실질 독립분 부재로 폐기(not planned) — 활성 8건. 상세는 아래 #211 행·Q&A.**

| 티켓 | 분할 | 한 줄 요약 | 선행 |
|---|---|---|---|
| [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207) | W6-1 | 기존 `runAsync` one-shot 경로를 공통 책임(exe 검증·env·UTF-8 라인조립·취소·자식정리) 집약한 `ProcessJob : Job` 일체형(1회용)으로 추출 + `runAsync` 부분수신 버그 수리(필수 선행) + `killOrphans` 자기 PID 한정 | — |
| [#208](https://github.com/NumeRealWorks/DashOpti_GUI/issues/208) | W6-2 | one-shot 소비자 6 중 model 3종(`DashModelRunner`·`DashModelBuilder`·`DashOptimizer`) 자체 `QProcess` 소유 제거 → 엔진([#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207)) 위임, 도메인 시그널 표면·동작 불변 | [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207) |
| [#209](https://github.com/NumeRealWorks/DashOpti_GUI/issues/209) | W6-3 | one-shot 소비자 6 중 뷰 소유 `QProcess` 2곳(`DashOptimizerWidget`·`TopOptPostprocessDialog`) controller/model 이전 → "창 닫힘 = 작업 사망" + 계층 위반 동시 해소 (MCU 1곳은 [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207) 에서 재배선) | [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207) |
| [#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) | W10-a | 파일럿 DOE 배치(`runWbpjDoeAsync`) `waitForFile` 폴링 → 완료 시그널 구독(+구 #211 폐기로 유일 호출자 소멸한 죽은 `waitForFile` 정의 삭제) + 배치 오케스트레이션(기술자 큐·팩토리·완료슬롯 연쇄), 취소·실패 정책 P1~P3·P5 구현(P4 는 [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214)) | [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207)~[#209](https://github.com/NumeRealWorks/DashOpti_GUI/issues/209) |
| [#211](https://github.com/NumeRealWorks/DashOpti_GUI/issues/211) | ~~W10-b~~ **폐기** | ~~파일 폴링 → 완료 시그널 구독~~ — **실질 독립분 부재로 폐기(not planned)**: 4곳 중 `waitForFile` 죽은 정의는 [#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210), `waitForVtuFileComplete`·`runMotionWriter`·dfsxml 루프는 모핑(in-process) 산출물 대기라 워커 축과 불가분 → [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) Phase 6 로 흡수 | — |
| [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) | W10-c | 데몬 기동 `bool startDaemon()` → `void start()` + `ready()`/`died()` 재계약(P8) + `DaemonHost`(수명·명령 큐 장수 객체) 신설 + 진입점 7곳 큐잉 전환 + `died` 시 명령 일괄 Failed drain — NX 120초 프리즈 소멸, 명령 경로·파사드 무변경(`DaemonCommandJob` 폐기) | [#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) (병렬) |
| [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) | W10-d | WorkerJob 투입 전 공유상태 선결조건 5건(D1~D5: cout rdbuf 스왑·싱글톤 lazy-init·ExecuteMorphing 상태·컨텍스트 접근규약·GUI/VTK 규칙) 해소 게이트 + 잠재 버그 2건 수리 — 스레드 없이 "프리즈→레이스" 차단(본 티켓은 스레드 미생성) | — (외부축과 직교) |
| [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) | W10-e | `WorkerJob`(QtConcurrent+QFutureWatcher→Job 번역) + 서브시스템 직렬 풀 2종(모핑·RW, `maxThreadCount=1`) **인프라** 신설, 파일럿 **1건 = DOE 배치 모핑** 워커화(RW 풀 실소비는 [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215)) — 목표는 동시성 아닌 응답성 | [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) |
| [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) | W10-f | 워커 후보 순위 2~6 순차 Job화 + **dfsxml 모핑+MBD 루프(구 [#211](https://github.com/NumeRealWorks/DashOpti_GUI/issues/211)) 완료 시그널 구독 전환(Phase 6)** + model 계층 잔여 `processEvents` 41곳 → 0(+view 일부), W10 최종 DoD 수동 grep 봉인 = [#64](https://github.com/NumeRealWorks/DashOpti_GUI/issues/64) 재진입 크래시 계급 소멸 | [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) |

**의존 관계**: [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207) → [#208](https://github.com/NumeRealWorks/DashOpti_GUI/issues/208)·[#209](https://github.com/NumeRealWorks/DashOpti_GUI/issues/209) (W6) → [#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) → [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) (외부 축) / [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) → [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) → [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) (워커 축, 외부 축과 직교·병행 가능). 구 [#211](https://github.com/NumeRealWorks/DashOpti_GUI/issues/211) 폐기 — 파일 폴링 전환은 #210(`waitForFile`)·#215(dfsxml 루프)로 흡수.

**진척** (2026-08-20): 머지 **13건** — [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207)\~[#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210)·[#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212)·[#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213)(1차) + [#260](https://github.com/NumeRealWorks/DashOpti_GUI/issues/260)·[#251](https://github.com/NumeRealWorks/DashOpti_GUI/issues/251)·[#264](https://github.com/NumeRealWorks/DashOpti_GUI/issues/264)·[#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214)·[#265](https://github.com/NumeRealWorks/DashOpti_GUI/issues/265)·[#274](https://github.com/NumeRealWorks/DashOpti_GUI/issues/274)(2차) + [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277)(3차). 위 표의 [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) 는 구현되지 않고 **부모 티켓**이 되어 축으로 5분할됐고([#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277)·[#280](https://github.com/NumeRealWorks/DashOpti_GUI/issues/280)·[#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281)·[#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282)·[#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279)), 그중 [#277](https://github.com/NumeRealWorks/DashOpti_GUI/issues/277) 이 **`model` 계층 `processEvents` 41 → 3 을 달성**했다(잔여 3곳 = `DashJobRunner`, 담당 [#282](https://github.com/NumeRealWorks/DashOpti_GUI/issues/282) 2 · [#279](https://github.com/NumeRealWorks/DashOpti_GUI/issues/279) 1). 실제 변경 항목·진행 중·별건은 [205-2-w6-w10-change-log-and-remaining-design](205-2-w6-w10-change-log-and-remaining-design.md) 참조.

---

## 코드 정의

### 취소·실패 정책 P1~P5 ([#194](194-1-async-execution-patterns.md) `async-execution-patterns` 4-1절)

배치/워커 실행의 취소·실패 처리 정책. 소비: [#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210)(P1~P3·P5) · [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214)(P4).

| 코드  | 정책                                 | 의미                                                                                     |
| --- | ---------------------------------- | -------------------------------------------------------------------------------------- |
| P1  | 완료분 보존·중단분 폐기                      | 배치 중 이미 끝난 케이스 결과는 살리고, 중단 시점에 진행 중이던 케이스만 버림                                          |
| P2  | 가장 이른 지점 중단 + 잔여 미시작               | 배치 취소 = 현재 케이스를 가장 이른 안전 지점에서 멈추고, 아직 시작 안 한 잔여 케이스는 시작하지 않음                           |
| P3  | continue-on-error + 연쇄 실패 차단기(k=3) | 케이스 1건 실패해도 배치는 계속, 단 같은 유형 연속 3건 실패면 배치 중단                                            |
| P4  | 협조적 취소                             | (워커) 취소 = 즉시 Cancelled + UI 즉시 해방, DLL 실행 도중엔 중단 불가 → 늦은 결과 폐기. "UI 해방"이지 "CPU 해방"이 아님 |
| P5  | 자동 재시도 없음                          | 실패 케이스를 자동으로 다시 돌리지 않음(재시도는 사용자 판단)                                                    |

**단순화 검토 (P1 제거·P3 fail-fast?)** — 파일럿이 **DOE(설계실험) 배치**라는 점이 관건. "일부만 쓸 케이스가 없으면 제거"라는 전제가 DOE 에는 성립하지 않는다 — 부분 결과·부분 실패가 DOE 의 1차 용도다.

- **P1(완료분 보존) — 유지 권장.** DOE 는 파라미터 샘플 N건 결과 수집이 목적 자체, 케이스마다 외부 솔버(분 단위) 실행. 60/100 에서 취소 시 완료 60건을 버리면 수 시간 계산 낭비. 구현상 "완료 시 결과 append"는 어차피 하는 일이라 P1 은 **거의 공짜**이고, 제거하면 오히려 능동적으로 결과를 버리는 더 나쁜 동작.
- **P3 continue-on-error — 유지 권장.** DOE 는 개별 샘플 실패(나쁜 파라미터 조합 → 솔버 발산·메시 실패)가 **예상된 정상 범위**. fail-fast(1건 실패=전체 실패)면 나쁜 샘플 하나가 실험 전체를 죽여 나머지 유효 케이스를 잃음 → DOE 목적 훼손.

즉 DOE 파일럿에선 P1·P3-continue 가 **투기적 코드가 아니라 도메인 요구**다. 다른 배치 종류가 all-or-nothing 을 원하면 그때 **배치별 정책**으로 분기 — 지금 일괄 제거는 DOE 에서 손해.

### 워커 선결 조건 D1~D5 ([#203](203-2-worker-preconditions-analysis.md) `worker-preconditions-analysis`)

WorkerJob(두 번째 스레드) 투입 전 반드시 해소해야 할 공유 상태 5건. 지금 사고가 안 나는 유일한 이유는 전 코드가 GUI 스레드 하나에서 자동 직렬화되기 때문 — 이 정리 없이 스레드를 넣으면 프리즈가 레이스로 바뀐다. 착수 순서 = `D4 → D1 → D2 → D3 → D5`.

| 코드 | 대상(위치) | 문제 | 처방 |
|---|---|---|---|
| D1 | 싱글톤 lazy-init (`DashManager::Mgr()` :210-215 · `DashProjectManager::Instance()` :13-18) | 락 없는 지연 생성 → 두 스레드 동시 진입 시 이중 생성/레이스 | 메인 스레드 선-초기화 + 초기화 락 |
| D2 | `ExecuteMorphing` 공유 상태 (`m_morphingOperator`, `DashManager.cpp:314-343`) | 싱글톤 멤버를 mutex 없이 비원자 6단계로 변이 | 소유권을 실행 단위 로컬(또는 직렬 워커 소유)로 분리 |
| D3 | `DashAnalysisModelContext` 접근 규약 | 레지스트리 락이 맵만 보호(무거운 로드는 락 밖 → 이중 파싱), 컨텍스트 내부 mutex 전무 | 직렬 워커 전용 접근 또는 읽기 스냅샷 전달 (+ `getOrLoad` dangling 수리) |
| D4 | 전역 `std::cout` rdbuf 스왑 (`DashAnalysisModelContext.cpp:306-316`) | `reader.Update()` 동안 프로세스 전역 cout/cerr 임시 교체·복원 → 두 스레드 동시 로드 시 save/restore 레이스 → 영구 오리다이렉션/크래시 | DLL 로그레벨 API·널 싱크로 교체 (+ 예외 복원 누락 수리) |
| D5 | GUI·VTK 객체 규칙 | QWidget 메인 스레드 전용(Qt 계약) · VTK 파이프라인 스레드 공유 금지 | 워커 산출물은 소유권 이전으로 메인에 전달, 병합·렌더는 메인에서만 (규칙 명문화) |

착수 순서 근거: D4(전역 오염, 가장 위험) → D1(초기화) → D2·D3(도메인 상태) → D5(규칙). 부수 발견 잠재 버그 2건: `getOrLoad` emplace 실패 시 dangling 반환 · cout rdbuf 예외 시 복원 누락.

> 용어 해설: magic static · lazy-init 레이스 · Registry/Context · `try_emplace` · rdbuf 스왑 개념 Q&A → [203-1-worker-precondition-concepts-qa](203-1-worker-precondition-concepts-qa.md)

---

## 개념 풀이

### ProcessJob 소비자 ≠ 전체 QProcess 소유자

코드에서 QProcess 를 쓰는 곳이 전부 ProcessJob 으로 바뀌는 게 아니다. `ProcessJob` 은 "exe 1회 실행 = 프로세스 종료가 곧 완료"인 **단일 one-shot** 모델. 이 틀에 안 맞는 두 곳은 W6 범위 밖:
- `DashJobRunner` — 여러 프로세스를 `QHash` 로 동시 관리 + C API 런처(`DashFL_*`) + 파일 폴링(`waitForFile`). 단일 one-shot 과 불일치.
- motion-launcher — 다중 레지스트리(`m_motionProcesses[runKey]`) 소속 + 이미 시그널 구동. 수렴 실익 없음.

단 `DashJobRunner` 는 W10-a 에서 배치 오케스트레이터로서 ProcessJob 을 **팩토리로 생성·소비**한다 — 자기가 QProcess 를 직접 소유하는 것과는 다름.

### 배치 오케스트레이션 (기술자 큐·팩토리·완료슬롯 연쇄)

DOE 배치처럼 대상·횟수·순서가 런타임에 정해지는 반복 실행을, 동기 for 루프가 아니라 **이벤트 구동 루프**로 재구성하는 패턴. 3요소:
- **기술자 큐** — 실행 계획을 데이터로 든 목록(`QList<CaseDescriptor>`). "무엇을 몇 번 돌릴지"를 콜스택이 아니라 멤버로 보관.
- **팩토리** — 기술자 1건 → Job 1개 생성(`makeJobFor(descriptor)` → ProcessJob/WorkerJob). Job 을 미리 붙이지 않고 그때그때 만든다.
- **완료슬롯 연쇄** — Job 의 `finished` 슬롯이 결과를 기록하고 **다음 케이스를 시작**한다. 순서의 실체가 for 루프가 아니라 "완료가 다음을 부르는" 연쇄. 반복 사이마다 이벤트 루프가 돌아 UI 가 살아있음.

```
startNextCase()
├─ 큐 비었거나 취소됨? → finishBatch()
├─ m_current = makeJobFor(큐.takeFirst())                              (팩토리)
├─ connect(m_current.finished → 결과 기록 → 차단기 검사 → startNextCase())   (연쇄)
└─ m_current.start()                                                  (즉시 반환 — UI 생존)
```

**대안 검토 — 더 나은 설계가 있나?** 현재안은 Qt 5.15 + I/O 바운드(외부 프로세스/데몬) 오케스트레이션에 대한 **최소 적합해**다.

| 대안 | 평가 |
|---|---|
| 코루틴 `co_await` | **유일하게 더 읽기 좋음** — `for (d : cases) co_await runJob(d);` 로 선형화. 그러나 Qt 5.15 어댑터 부재(QCoro 최신판 Qt 6.8+ 전용, [#194](194-1-async-execution-patterns.md) 3-3절). 지금 넣으면 같은 코드 2회 재작성 → **Qt 6 이행 시 additive 승격**으로 보류 |
| `QFuture::then()` 체이닝 | Qt 6.0+ 기능 — 5.15 미지원. 런타임 가변 N단계 체이닝은 표현력도 부족 |
| `QStateMachine`(Qt 상태머신 FW) | 선형 큐에 과함 — 프레임워크 무게 + "다음 케이스 런타임 결정" 표현이 오히려 번거로움. 현재 수기 슬롯 연쇄가 이미 최소 상태머신 |
| 워커 스레드 + 동기 for 루프 | 루프 안 블로킹 대기로 코드는 선형화되나 (a) 각 케이스가 외부 프로세스/데몬이라 CPU 이득 0(I/O 바운드) (b) 오케스트레이션이 GUI 공유 상태(DashManager 등) 접근 시 D1~D5 스레드 안전 문제 자초 (c) 취소·진행 보고는 여전히 마샬링 필요 → 슬롯 연쇄 복잡도를 **스레드 안전 복잡도로 맞바꿀 뿐** |
| 재사용 `BatchRunner` 추출 | 다른 설계가 아니라 같은 패턴의 리팩터. 파일럿 1건뿐이라 지금 추출은 조기 추상화([#205](205-5-w6-w10-async-minimal-example.md) JobManager/스케줄러 배제 원칙과도 정합). **오케스트레이터 3곳+ 중복 시(rule of three) 얇은 헬퍼로 재검토** |

**결론**: 현재안 유지. I/O 바운드 외부 프로세스 오케스트레이션엔 이벤트 구동이 관용적이고 스레드를 아예 안 쓴다(스레드는 CPU 바운드 워커 축의 몫 — 별개 축). 엄밀히 더 나은 유일한 형태는 코루틴이나 Qt 5.15 가 막고 있으며 이미 additive 미래 업그레이드로 기록됨([#194](194-1-async-execution-patterns.md) 3-3절).

### BatchRunner 추출 — 적용성·유지보수성 검토 (코드 실측 2026-07-28)

**적용 가능 지점 = 3곳** (모두 DOE 배치, "샘플 순회 → 케이스당 1건 실행 → 상태 방송" 골격):

| 지점 | 케이스당 작업 | 단계 | 티켓 | 실행 종류 |
|---|---|---|---|---|
| `runWbpjDoeAsync` (`DashJobRunner:2459`) | STP 생성(데몬) → Journal(전체) | 2단계 | [#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) | ProcessJob+데몬 |
| `DashMorphingDoeExecutor::Execute` (`:302`) | 모핑+export (in-process) | 1단계 | [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214)·[#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) | WorkerJob |
| dfsxml 모핑+MBD 루프 (`DashJobRunner:1587`) | 모핑 → vtu 대기 → motion-writer → motion-launcher | 3단계 중첩 | [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) (구 [#211](https://github.com/NumeRealWorks/DashOpti_GUI/issues/211) 흡수) | WorkerJob+ProcessJob+데몬 |

**현재-대상 아님 (4곳)**: `runDirectJobs`(`:2149`) · motion-launcher 큐(`:751`) · `runDoeAsync`(`:1044`) · DOE 샘플링(`DashAnalysisLauncher:233`) — 각 제외 사유와 "확장하면 포함되나?"는 아래 [비대상 재검토] 참조. (실측 결과 motion-launcher 는 실은 **순차 체인**이라 잠재 4번째 채택처로 재분류)

**공통(추출로 1회화 — 실측상 3곳 동일)**:
- `active` 필터 → `runKey` 추출 → runDir mkpath
- **케이스 상태 방송 `caseStatusUpdated(runKey, status, analysisType)` — 3곳 시그널 표면 동일**
- 케이스 실패 시 `continue` + `setSampleStatus("Failed")` = **P3 continue-on-error 가 이미 3곳의 사실상 동작**
- 결과 누적 · 취소(현재 3곳 다 부재 → 추출 시 1회 구현)

**가변(팩토리로 주입)**: 케이스당 작업(STP/모핑/모핑+MBD) · 기술자 형태 · 단계 깊이(1~3단계).

**유지보수성 판정**:
- **추출 찬성** — (1) 3곳 = rule of three 충족 (2) 도메인 표면 동일(위 공통 5종) = 보일러플레이트가 실제 반복 (3) **취소·수명 안전([#64](https://github.com/NumeRealWorks/DashOpti_GUI/issues/64) UAF 계급)을 1회만 정확히 구현** — 가장 큰 안전 이득 (4) P1·P3 정책 중앙화(특히 차단기 k=3 은 현재 **어디에도 없음** → 추출 시 1회 도입)
- **추출 주의** — (1) F 의 3단계 중첩·A 의 배치 종료 후처리(Journal)로 "케이스=Job 1개" 단순 루프론 부족 → 팩토리가 `Job*` 또는 미니 파이프라인 반환 + 배치 finalize 훅 필요(인터페이스 증가) (2) [#205](205-5-w6-w10-async-minimal-example.md) 가 JobManager/스케줄러 금지 → **얇은 순차 체인+정책 보유자**로 한정(우선순위·트리·동시성 금지) (3) 전달 순서상 A([#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210)) 먼저·C·F([#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214)/[#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215)) 나중 → 세 곳이 [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) 시점에야 공존

**결론 — 타이밍**: [#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) 시점 추출은 인스턴스 1개라 조기 추상화(기각). A·C·F 를 같은 골격으로 인라인 구현하고, **세 곳이 공존하는 [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215)(W10-f) 마무리에서** 체인+취소+정책 코어의 3중복을 확인한 뒤 얇은 `BatchRunner` 로 추출. 근거: 취소/수명 로직이 UAF 계급이라 단일 구현의 안전 이득이 가장 크다.

```cpp
// 추출 시 얇은 형태 (스케줄러 아님 — 순차 체인 + 정책만)
class BatchRunner : public QObject {
    void run(QVector<Descriptor> cases, std::function<Job*(const Descriptor&)> factory);
    void cancel();                              // 취소·수명 안전 1회 구현 (#64 계급)
signals:
    void caseFinished(QString key, Job::State, QString reason);
    void batchFinished(QVector<CaseResult>);    // P1 결과 보존
};
// 정책 내장: P3 continue-on-error + 차단기(k), P5 재시도 없음.  A 의 Journal-전체 단계는 batchFinished 훅에서
```

#### 비대상 재검토 — 확장(병렬 등)으로 포함 가능한가

"비대상"을 (1) 왜 비대상인지 (2) BatchRunner 를 더 일반적 형태(순차뿐 아니라 **병렬 fan-out·레지스트리·join** 까지)로 확장하면 포함되는지 재검토. ("확장" = 현재 고려한 얇은 순차형 이상의 기능/구조까지.)

| 대상 | 왜 (현재) 비대상 | 일반화 BatchRunner 로 포함 가능? |
|---|---|---|
| **motion-launcher 큐** (`:751` `startNextMotionLauncher`) | **(정정) 패턴이 다르지 않음** — `finished → startNextMotionLauncher` 로 **한 번에 하나씩** 도는 순차 체인 = 수기 BatchRunner. W6 ProcessJob 수렴 관점에서만 제외였음(이미 시그널 구동이라) | **포함 가능·확장 불요** — 지금의 얇은 순차형으로 그대로 흡수. 이미 잘 도니 급하진 않으나 **잠재 4번째 채택처**(손댈 때 기회적 통합) → 카운트 3→**4** |
| **runDirectJobs** (`:2149`) | 파일 suffix 별 **전건 동시 제출**(C 런처 `DashFL_*`) + `m_activeTasks` QHash 추적 = **병렬 fan-out**. 완료 원천이 Job 시그널 아닌 **C 콜백** | **일반화하면 구조상 담기나 값이 안 맞음** — 병렬 모드(전건 제출+레지스트리+join) 추가 시 담긴다. 그러나 (a) 그 병렬성은 **이미 C 런처가 제공** → 덮어도 런처 잔존, **순감 없음** (b) 각 C 태스크를 Job 으로 래핑 필요([#209](https://github.com/NumeRealWorks/DashOpti_GUI/issues/209) 가 C 런처를 통째 범위 밖으로 둠) (c) 병렬+레지스트리+join = **[#205](205-5-w6-w10-async-minimal-example.md) 가 명시 배제한 JobManager/스케줄러 영역**. 의도된 병렬(N개 드롭=동시 실행)이라 순차화하면 동작도 바뀜 |
| **runDoeAsync** (`:1044`) | 배치 루프가 아니라 **디스패처** — expected 키 추적 후 `generateInputCases` 위임. 케이스당 Job 없음 | **불가(아무리 일반화해도)** — 순회할 케이스가 없음. 배치를 **호출**하는 쪽이고 그 배치(A/C/F)는 이미 대상 |
| **DOE 샘플링** (`:233`) | **단일** QtConcurrent 1건(WorkerJob 원형). 배치 아님 | **불가(무의미)** — 1개짜리 배치는 배치가 아님. 이건 BatchRunner 가 아니라 **WorkerJob** 자체 |

**일반화 비용 곡선**:
- **얇은 순차형** → A·C·F + motion-launcher = **4곳** 흡수, [#205](205-5-w6-w10-async-minimal-example.md) 정합(순차 체인+정책만). ← 권장
- **병렬 일반형**(순차+병렬+레지스트리+join) → +runDirectJobs = 5곳이나 **[#205](205-5-w6-w10-async-minimal-example.md) 가 닫은 JobManager 결정을 재개봉**. runDirectJobs 병렬은 이미 C 런처가 처리라 통합 순감 없음
- **runDoeAsync·DOE 샘플링** = 배치가 아예 아님 → 일반화 수준과 무관하게 영구 비대상

**판정**: "포함 가능하냐"만 보면 6곳 중 **5곳까지** 담을 수 있다. 그러나 5번째(runDirectJobs)를 담는 일반화가 곧 **[#205](205-5-w6-w10-async-minimal-example.md) 가 의도적으로 기각한 스케줄러**라, 능력 문제가 아니라 **범위 결정 문제**다. 4곳을 담는 얇은 순차형이 최소 비용·[#205](205-5-w6-w10-async-minimal-example.md) 정합. runDirectJobs 는 C 런처가 이미 병렬을 제공(통합 순감 없음)하므로 **의도적 비대상 유지**.

### 후속 작업 (기록)

- [ ] **[#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215)(W10-f) 또는 후속 티켓에서 `BatchRunner` 추출 검토** — 세 배치(A `runWbpjDoeAsync`·C `DashMorphingDoeExecutor`·F dfsxml 루프)가 공존하는 시점에 체인+취소+정책 3중복 확인 후 **얇은 순차형**으로 추출. motion-launcher 큐(`:751`)는 **기회적 4번째 채택처**로 편입 검토.
- [ ] **(별도 안건) 병렬 일반형 확장은 보류** — runDirectJobs 까지 흡수하려면 병렬 모드+레지스트리+join 이 필요하고 이는 [#205](205-5-w6-w10-async-minimal-example.md) 의 JobManager/스케줄러 배제 결정을 재검토하는 일. 통합 순감(C 런처가 이미 병렬 제공)이 없어 현재는 열지 않음. 다른 병렬 배치 수요가 실제로 생기면 그때 안건화.

### motion-writer → motion-launcher 큐로 이식

둘 다 같은 파일(`DashJobRunner.cpp`) 안에 있다. `runMotionWriter`(:666-729)는 `waitForFinished(500)+processEvents` 폴링(나쁜 방식)이고, 바로 옆 motion-launcher 큐(:751-858)는 **이미 시그널 구동 + 완료 연쇄**로 잘 돈다(좋은 선례). "이식" = motion-writer 의 폴링 로직을 걷어내고 **같은 파일에 이미 있는 잘 된 큐 메커니즘에 태우는 것** — 새로 만드는 게 아니라 옆의 모범 경로로 옮겨 붙임.

### 풀 구조 — [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 직렬 풀 vs [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) (병렬 풀 아님)

병렬 풀은 도입되지 않는다.
- **[#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214)** = 직렬 풀 **2종 신설**(모핑 풀·RW 풀, 각 `maxThreadCount=1`) + 파일럿 1건.
- **[#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215)** = **새 풀 없음** — [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 의 같은 직렬 풀 2종에 나머지 워커 후보를 태울 뿐.
- "병렬"이 성립하는 건 **풀 사이**뿐 — 모핑 풀 ↔ RW 풀은 서로 병렬로 돈다. 각 풀 **내부는 직렬**(같은 서브시스템 작업은 구조적으로 동시 실행 불가 → DLL 락 불요). 즉 [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) 를 "병렬 풀"로 보면 틀림.

### [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) vs [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) — 무엇이 구분 기준인가

구분 기준 = **"메커니즘 신설 + 1건 검증"(214) vs "그 메커니즘을 나머지에 일괄 확산 + 마무리"(215)** — 전형적 파일럿→확산 분리.

| | [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) (W10-e) | [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) (W10-f) |
|---|---|---|
| 인프라 | WorkerJob·직렬 풀 2종 **신설** | **신설 없음** — [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 것 재사용 |
| 적용 범위 | 파일럿 **1건**(DOE 배치 모핑, [#194](194-1-async-execution-patterns.md) 5-4절 순위 1) | 나머지 후보 **순위 2~6 전부** |
| 추가 몫 | (메커니즘 증명) | model `processEvents` 41→0 + DoD 수동 grep 봉인 |

**왜 이렇게 자르나 — 리스크 관리.** WorkerJob 은 스레드를 새로 들이는 작업이라 스레드 안전·취소·UAF 등 함정이 많다(그래서 [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) 게이트가 선행). 대표 1건(가장 우선순위 높은 DOE 배치 모핑)으로 메커니즘을 먼저 증명한 뒤, 문제 없으면 [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) 에서 5+곳으로 기계적 확산. 함정을 6곳이 아니라 1곳에서 발견하려는 것.

### 워커 안전 4대 개념 ([#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214))

**① DLL 스레드 안전 3등급 판정** — 무거운 DLL 작업(모핑 `Morph()`·파싱 `reader.Update()`)을 워커 스레드로 넘길 때, 그 DLL 을 비-GUI 스레드에서 불러도 되는지·동시 호출해도 되는지 알아야 한다. 벤더 문서 근거가 없으면 보수적으로 판정:

```
등급 1  재진입/thread-safe  — 여러 스레드 동시 호출 안전
등급 2  비재진입           — 워커에서 호출 OK, 단 동시 호출은 레이스 → 직렬화 필수
등급 3  thread-hostile     — 스레드 밖으로 못 뺌(NXOpen) → 외부 프로세스로 격리
```

- 근거 없으면 **등급 2 가정**(비관적).
- 등급 2 처방 = **서브시스템 전용 직렬 풀(maxThreadCount=1)**. 풀이 직렬이라 같은 서브시스템 작업 2건이 **구조적으로** 동시에 못 돈다 → DLL 안에서 데이터 레이스가 원천 불가 → **DLL 호출부에 락을 걸 필요 없음**. 풀의 직렬성이 곧 동시성 제어.
- 등급 3(NXOpen)은 이미 외부 프로세스 격리로 처리 중(데몬/ProcessJob 축).
- 실측해 등급 1 로 승급 안 하는 이유 — MSVC 엔 TSAN(스레드 새니타이저)이 없어 "돌아가는 것 같다"로 승급하면 위험. 보수 유지.

**② Job 경계 절단 3규칙** — WorkerJob 은 `task` 를 워커 스레드에서 실행한다. GUI 스레드 ↔ 워커 스레드 **경계를 깨끗이 자르는** 규칙 3개([#64](https://github.com/NumeRealWorks/DashOpti_GUI/issues/64) 크래시 계급 = 이 경계를 안 자른 데서 나옴):

```
1. 입력 스냅샷    start() 시점에 GUI 스레드에서 task 가 쓸 입력을 파라미터 구조체로 복사.
                워커는 이 스냅샷만 읽음 — GUI 스레드가 동시 변이하는 라이브 상태를 안 읽음
2. 본문 위젯 금지  워커 본문은 QWidget/GUI 접근 금지(Qt: 위젯은 메인 스레드 전용).
                스냅샷 + 자기 소유 데이터만
3. 출력은 시그널   결과는 finished 시그널로 → 위젯 반영은 메인 스레드 슬롯(QueuedConnection 마샬링).
                워커가 위젯에 직접 쓰지 않음
```

= 스냅샷 넣고(1), 도중 위젯 안 만지고(2), 시그널로 빼낸다(3). 코드베이스가 전반적으로 thread-safe 하지 않기에 이 규율이 스레딩을 안전하게 만든다.

**③ 취소 채널 UAF 규칙 (개정 2)** — 폴링 가능한 task 에 협조적 취소를 붙일 때, 순진한 방법(Job 의 bool 멤버 플래그)은 use-after-free 를 부른다:

```
[버그]  cancel() → 플래그 set + 즉시 Cancelled 방송
              → 호출부 finished 슬롯 → Job.deleteLater()
       그런데 task 는 아직 워커에서 실행 중(DLL 은 도중 중단 불가)
              → 나중에 멤버 플래그 폴링 = 죽은 객체 멤버 참조 = use-after-free (#64)
[처방]  bool 멤버 대신 shared_ptr<atomic<bool>> 취소 채널을 task 인자로 전달.
       Job 과 task 가 같은 atomic 을 shared_ptr 로 공유 →
       Job 이 삭제돼도 atomic 은 task 가 든 shared_ptr 로 생존 → 폴링이 유효 객체를 읽음.
       atomic 이라 스레드 간 읽기/쓰기도 정의됨.
```

핵심: 취소 플래그가 **Job 보다 오래 살아야** 안전 → 맨 멤버 금지, 공유 소유 채널.

**④ 목표 = 동시성 아닌 응답성** — WorkerJob 의 목적은 여러 작업을 병렬로 돌려 **빠르게**(throughput/동시성) 하는 게 아니라, 무거운 블로킹 1건을 GUI 스레드 밖으로 빼 **UI 를 안 얼리는**(응답성) 것. 그래서 직렬 풀(maxThreadCount=1)로 충분 — 모핑 8건 동시 실행이 목표가 아니라 그 1건이 UI 를 안 멈추게 하는 것. 이는 등급 2 DLL 안전(직렬 = 동시 호출 없음)과도 맞물린다. 동시성(무거운 작업 여러 개 동시)은 명시적 비목표 — 응답성 이득 없이 DLL 안전 문제만 되살림.

---

## 티켓별 세부 확인 (Q&A)

> 이슈 본문([#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207)~[#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215)) 근거. 질문의 전제가 어긋난 곳은 **보정**으로 표기.

### [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207) — `runAsync` 와 `ProcessJob : Job` 추출의 관계

`runAsync` 는 `DashExtensionProcess` 의 기존 one-shot 비동기 실행 메서드(`controller/DashExtensionProcess.h:111`). `ProcessJob` 은 **바로 그 runAsync 경로를 1회용 Job 클래스로 추출·재구성**한 것 — 같은 실행 경로의 before(`runAsync`) / after(`ProcessJob`) 다.

핵심 연관: `runAsync` 에 stdout 결과 라인 **부분수신(마커 잘림) 버그**가 있어, 추출 전에 먼저 수리해야 한다. 안 고치고 소비자를 확산하면 버그가 전 소비자로 번지므로 **필수 선행**. 그래서 한 티켓에 `runAsync 버그 수리(Phase 1) → Job.h·ProcessJob 추출(Phase 2)` 이 묶였다.

### [#208](https://github.com/NumeRealWorks/DashOpti_GUI/issues/208)·[#209](https://github.com/NumeRealWorks/DashOpti_GUI/issues/209) — model 3종 + view 2종 = ProcessJob 소비자 전체?

**보정: 아니다 — 1개 빠졌다.** one-shot exe 소비자는 총 **6파일**:

```
one-shot exe 소비자 6
├─ DashModelBuilderMCU      → #207 에서 재배선 (이미 runAsync 위임 소비자 = 추출 선례)
├─ DashModelRunner          ┐
├─ DashModelBuilder         ├ #208 (model 3종)
├─ DashOptimizer            ┘
├─ DashOptimizerWidget      ┐
└─ TopOptPostprocessDialog  ┘ #209 (view 2종)
```

model 3 + view 2 = 5 에 **MCU 1** 을 더해야 전체. MCU 는 [#207](https://github.com/NumeRealWorks/DashOpti_GUI/issues/207) 자체에서 재배선(위임 선례라 엔진 티켓에 포함).

추가 유의 — **ProcessJob 소비자 ≠ 전체 QProcess 소유자**:
- `DashJobRunner`(다중 프로세스 QHash·C API 런처·파일 폴링)·motion-launcher 는 W6 **범위 밖**. 단 `DashJobRunner` 는 W10-a([#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210))에서 배치 오케스트레이터로 ProcessJob 을 **팩토리 생성·소비**(직접 소유 전환은 아님).
- 데몬 갈래는 ProcessJob 미사용 — `DaemonHost`([#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212)).

### [#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) — runWbpjDoeAsync 파일럿 + 정책 P1·P2·P3·P5?

**맞다.** `runWbpjDoeAsync` 를 파일럿으로: `waitForFile` 폴링 → `updatePrtGeometryCompleted` 구독 + 배치 오케스트레이션(기술자 큐·팩토리·완료슬롯 연쇄). 정책도 이 티켓에 구현:
- P1 완료분 보존·중단분 폐기 (케이스별 종료 상태 기록)
- P2 배치 취소 = 가장 이른 지점 중단 + 잔여 미시작
- P3 continue-on-error + 연쇄 실패 차단기 k=3
- P5 자동 재시도 없음

**보정**: P4(협조적 취소)는 이 티켓 아님 — 워커용이라 W10-e([#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214)).

### [#211](https://github.com/NumeRealWorks/DashOpti_GUI/issues/211) — 폐기 (구 W10-b · 파일 폴링 → 완료 시그널 구독)

**폐기(not planned).** 소비처 실측 결과 실질 독립분이 붕괴 — "파일 폴링 4곳" 이 사실상 두 갈래로만 나뉘고 둘 다 다른 티켓 소유가 옳다:
- `waitForFile` — 유일 호출자가 [#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) 파일럿(`runWbpjDoeAsync`)의 완료 시그널 전환으로 사라짐 → 죽은 정의 삭제까지 **[#210](https://github.com/NumeRealWorks/DashOpti_GUI/issues/210) 이 흡수**.
- `waitForVtuFileComplete`·`runMotionWriter`·dfsxml 루프 — 전부 dfsxml 모핑+MBD 루프 하나에 모임. 이 루프의 VTU 는 `MorphFromDoeSamples`(**in-process 모핑**) 산출물이라 워처/타이머 보조로는 flush 레이스를 못 없앤다 — **모핑 per-sample 완료 시그널 구독**이 정답이고, 그건 [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214)가 모핑을 워커화해 완료를 방출한 뒤에야 성립 → 워커 축 **[#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) Phase 6 로 흡수**.

즉 외부 축 단독(구 #211)으로 처리할 수 있는 순수 파일 폴링분이 남지 않아 티켓 자체를 폐기. ("완료 시그널 → 파일 검증" 원칙·워처는 보조라는 판정 자체는 유지 — 소유 티켓만 재배치.)

### [#212](https://github.com/NumeRealWorks/DashOpti_GUI/issues/212) — 기동 비동기화 외 작업 / P8 정의

**P8** = `dashgui2-qprocess-antipattern-catalog` 의 항목 = **"동기 bool 반환 기동 API" 안티패턴**. `bool startDaemon()` 이 반환까지 메인 스레드를 정지시키고 반환값이 ready 를 보증하는 형태 → **재계약: `void start()` + `ready()`/`died()` 시그널**.

기동 비동기화 외 작업:
- **DaemonHost 신설** — 데몬 수명·명령 큐 담당 장수 객체(상태머신 `NotRunning→Starting→Ready` + 명령 큐 이식). ProcessJob 재사용 안 함(데몬은 종료=사망이라 `finished`=완료 계약과 불일치).
- **진입점 7곳 큐잉 전환** — 첫 enqueue 동기 부팅 대기 제거, 미기동이어도 enqueue → ready 후 flush(명령 유실 없음).
- **종료·취소 재계약 + 기동 중 간섭 2건 규칙(개정 3)** — `stopDaemon` 동기 대기 제거(P2), `cancel(id)` host 흡수, Starting 중 `stop()`=kill+drain, 설정은 기동 시점 스냅샷.
- **사망·기동실패·타임아웃 통지** — `died` 시 진행 중·대기 명령 일괄 Failed drain + 사용자 통지(무음 실패 금지).
- **소비 표면 무변경** — 명령 경로·도메인 파사드 4곳(`loadPrtCompleted` 등) 무수정(`DaemonCommandJob` 폐기).

### [#213](https://github.com/NumeRealWorks/DashOpti_GUI/issues/213) — 선결 조건 대상·해소 방식 모두 정해졌나?

**대상·순서·건별 처방·검증 기준까지 정본 [#203](203-2-worker-preconditions-analysis.md) 에 확정.** 대상 5건(D1~D5), 착수 순서 `D4 → D1 → D2 → D3 → D5`, 건별 처방은 위 "워커 선결 조건 D1~D5" 정의표 참조.

**유의**: 완전 단일 확정은 아님 — D2·D3 는 2가지 처방 중 **택일(구현 시 확정)**, D5 는 코드 수정보다 규칙 명문화 + 위반 지점 정리 성격. 부수적으로 조사 중 발견한 잠재 버그 2건(`getOrLoad` dangling·rdbuf 예외 복원 누락) 동시 수리. **본 티켓은 스레드를 만들지 않음**(단일 스레드 무회귀).

### [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) — WorkerJob 구현 + 모핑·RW 파일럿?

**보정: 모핑·RW 는 파일럿 대상이 아니라 인프라(직렬 풀 2종).** 구성:
- `WorkerJob` 구현(`QtConcurrent::run(pool)` + `QFutureWatcher` → Job 시그널 번역, 협조적 취소)
- 직렬 풀 2종 신설 — 모핑 풀·RW 풀(각 `maxThreadCount=1`)
- **파일럿 1건 = DOE 배치 모핑 루프**뿐. RW 풀은 만들되 실소비는 W10-f([#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215)).

그 외 주요 내용(상세는 위 "워커 안전 4대 개념 ([#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214))" 참조):
- **DLL 스레드 안전 3등급** 판정 — 근거 없으면 등급 2(비재진입) → 서브시스템 전용 직렬 풀이라 DLL 쪽 락 불요
- **Job 경계 절단 3규칙** — 입력 스냅샷·본문 위젯 접근 금지·출력은 시그널
- **협조적 취소 P4** + **취소 채널 UAF 규칙(개정 2)** — `shared_ptr<atomic<bool>>` 채널(맨 멤버 플래그 금지)
- 목표 = 동시성 아닌 **응답성**

### [#215](https://github.com/NumeRealWorks/DashOpti_GUI/issues/215) — 워커 후보 나머지 전부?

**맞다 + 그 이상.** 워커 후보 순위 2~6 나머지 전부 순차 Job화(순위 1 DOE 배치 모핑은 [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 파일럿에서 완료):

```
2 단건 모핑·프리뷰 → 3 FE 모델 파싱 → 4 RST/KPI 파싱 7종
→ 5 export·serialize·메시 갱신 → 6 VTU/CSV 쓰기(여력 시 = 조건부)
```

워커화만이 아니라 **W10 최종 마무리**:
- **dfsxml 모핑+MBD 배치 루프(구 [#211](https://github.com/NumeRealWorks/DashOpti_GUI/issues/211)) 흡수** — VTU 대기·motion-writer 폴링·고정 슬립을 모핑 완료 시그널 구독으로 전환(Phase 6). VTU 가 모핑(in-process) 산출물이라 [#214](https://github.com/NumeRealWorks/DashOpti_GUI/issues/214) 후행이 전제
- model 계층 잔여 `processEvents` **41곳 → 0**(DashJobRunner 19·DashDataProcessor 14·DashResultProcessor 8) = W10 최종 DoD
- view 17곳 중 "동기 루프 펌핑" 아종은 워커화 부산물로 소멸, "단발 강제 리페인트"는 잔재 정리
- 마지막에 수동 grep 검증으로 봉인(model `processEvents` 0·GUI `waitFor*`/`msleep` 0) → **[#64](https://github.com/NumeRealWorks/DashOpti_GUI/issues/64) 재진입 크래시 계급 소멸 = W10 종료**
