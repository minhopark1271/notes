# dash-opti-dev 스킬 구조 정리

> 관련 Issue: #793

## 개요

`skills/dash-opti-dev` 는 DashOpti UI/백엔드 개발용 Claude Code 스킬이다. #793 (Dash UI 표준 흐름 고정) 구현 커밋 `04eebd75` 에서 도입됐고, `skills/ordo-use` 를 require 한다. 이 노트는 두 스킬의 파일 구성, 각 문서의 역할과 핵심 규칙, 문서 간 참조 관계, 설치 경로를 정리한다. 기준 시점은 dev `676aad39` (2026-10-19).

스킬의 설계 원칙은 4가지다.

| 원칙 | 구현 |
|---|---|
| 카탈로그형 진입 | `SKILL.md` 는 규칙 본문이 아니라 라우터. 요청 유형 → 읽을 문서 1개를 표로 안내 |
| 증상 기반 함정 색인 | 함정 노트는 폴더별 `README.md` 에 "증상 → 노트" 한 행. SKILL.md 는 폴더 인덱스만 링크하므로 노트가 늘어도 카탈로그는 안 커짐 |
| 양식 2종 고정 | 절차 문서는 `sample-general.md`, 함정 노트는 `sample-pitfall.md` 양식 |
| 지식 입장 기준 | 재사용 근거 · 비도출성 · 일반성 · 비중복 4조건 통과 + 사용자 승인 후에만 노트 추가 |

## 파일 구성

```
skills/
├── dash-opti-dev/                      (26 파일, 1,550 줄)
│   ├── SKILL.md                        115  카탈로그 (진입점)
│   ├── sample-general.md                51  절차 문서 양식
│   ├── sample-pitfall.md                63  함정 노트 양식
│   ├── development/
│   │   ├── general.md                  174  상시 개발 규칙 + Launcher 구현 맵
│   │   ├── dash-ui-recipe.md            99  신규 기능 11단계 절차
│   │   ├── qt/        README + 4 노트  176  Qt 함정
│   │   ├── build/     README + 6 노트  234  빌드·툴체인 함정
│   │   ├── reader/    README + 1 노트   38  Preprocessor SDK 함정
│   │   └── debug/     README + 3 노트  115  크래시·진단 함정
│   ├── workflow/
│   │   ├── dash-ui-migration.md        114  레거시 전환 8 Phase
│   │   └── commit.md                   134  LOG.md 기반 커밋 절차
│   └── verification/
│       └── gui-probe.md                137  GUI probe 실행·작성 규칙
└── ordo-use/                           (5 파일, 768 줄)
    ├── SKILL.md                         79  멘탈 모델 + 4 역할 + 라우터
    ├── conventions.md                  137  네이밍·레이아웃·bootstrap·스레딩
    ├── patterns.md                     376  역할별 코드 패턴 + 헤더 표
    ├── post-verify.md                   97  구현 후 체크리스트 6항
    └── integration/AGENTS-snippet.md    79  AGENTS.md 붙여넣기 블록
```

## SKILL.md 섹션 해부

| 섹션 | 역할 | 내용 |
|---|---|---|
| frontmatter | 트리거 | `name: dash-opti-dev`, description 에 활성화 문구 (Dash UI 표준 흐름, 마이그레이션, GUI probe, LOG.md 커밋) |
| Dash UI Standard Flow | 용어 정의 | `Widget → Presenter → Command → Dash<Domain>Agent → DashIODispatcher job/executor → Fact → Presenter → Widget`. Ordo 위에 구축. 흐름 이름은 Dash, API 이름은 Ordo |
| Core Development Rules | 7개 불변 규칙 | Command 단일 진입, Fact 기본 결과, thin Command, 백엔드의 화면 조작 금지, `Dash<Domain>Agent` 네이밍, `DashIODispatcher` 기본 I/O 경로 |
| Development Catalog | 라우팅 | 신규 → recipe, 변경·리뷰 → general, 레거시 전환 → migration |
| Pitfall Catalog | 라우팅 | qt / build / reader / debug 폴더 인덱스 4개 |
| Verification Catalog | 라우팅 | UI 변경 검증 → gui-probe |
| Working Rules | 응답 규칙 | `Class::function` 표기, 결과 먼저, 관찰·소스확인·추론 분리, 분석은 편집 권한 아님, probe 통과 = done, Git 변경 명령은 요청 시만 |
| Workflow Catalog | 라우팅 | LOG.md 커밋 → commit.md. "commit" 은 push 미포함 |
| Knowledge Upkeep | 노트 관리 | 입장 기준 4조건, 서브에이전트 KB 후보 수확, 낡은 노트 즉시 삭제, 분석 지식 추가 조건 |
| Reference Format | 양식 지정 | 절차 → sample-general, 함정 → sample-pitfall, 보조 문서는 frontmatter 불요 |

요청 문구 → 절차 매핑이 SKILL.md 에 명시돼 있다.

| 요청 예 | 절차 |
|---|---|
| "Dash UI 표준 흐름으로 ○○ 다이얼로그 구현해" | `development/dash-ui-recipe.md` |
| "Dash UI 표준 흐름으로 ○○ 화면을 전환해" | `workflow/dash-ui-migration.md` |
| "Dash UI 표준 흐름으로 ○○ 처리를 executor로 옮겨" | migration 의 "Moving a synchronous engine to an executor" |

## 절차 문서 상세

### development/general.md: 상시 규칙

신규·변경·리뷰 모두에 적용되는 목표 규칙. 레거시 화면이 이미 따른다는 주장이 아니므로 관찰 서술 시 소스 확인을 요구한다.

| 하위 섹션 | 핵심 규칙 |
|---|---|
| Command entry and Fact results | 카탈로그 읽기·계산·export·저장·취소 모두 Command 경유. Direct receiver 는 예외 경로이며 사유·수신자·스레드·수명·식별자·stale 처리를 기록 (VTK render gate 가 예) |
| Layer responsibilities | 8개 레이어별 Knows / Must not know 표. 비즈니스 정책은 Command 가 아니라 Agent 의 QCoro flow 에 둔다 (Launcher 결정 D8, Ordo 기본 지침과 의도적으로 다름) |
| Backend UI separation | `processEvents()`, 로컬 `QEventLoop::exec()` 금지. 백엔드 Qt 사용 자체는 허용, 책임으로 판단 |
| Agent naming | `Dash<Domain>Agent` 만 flow owner. 헬퍼·executor 는 실제 책임명. `...Service` 레이어는 구체적 필요 시만 |
| Contracts and identity | 값 전용 header-only payload, `eventName` constexpr. intent 는 `Requested`, fact 는 과거형. `setName` + `projectGeneration` + `bindingId`, 장기 작업은 `operationId`, 인덱스 선택은 리스트 revision. 파일 revision (size, mtime, hash) 은 새 load 만 채택 |
| I/O and ordering | `controller/async/DashIODispatcher` 기본. 같은 파일 writer 는 같은 큐. read-validate-backup-write-restore 는 1 job. 파일당 store 1개, `QSaveFile` + Windows 잠금 재시도. 삭제 전 큐 drain. UI 스레드 파일 읽기 금지 (로깅 포함) |
| Concurrency and lifetime | check-and-claim 사이 suspension 없음. 확인 대화상자는 `QMessageBox::open()` + 답변 intent. 단명 다이얼로그는 세션 수명 presenter 에 `QPointer` 부착. fact 유발 팝업은 queued. 취소 ≠ 정지 (quiescence) |
| QCoro and dispatcher pitfalls | capture lambda 를 coroutine 으로 만들지 않음. `co_await` 후 weak 재획득. ticket 은 `awaitIO` 로 1회 소비. `co_return member` 는 move. QCoro 는 eager 시작 |
| Verification | 폴더 이동만으로 경계 증명 불가 (repo root 가 include path). `ui_boundary_check` OBJECT 라이브러리 + `WILL_FAIL` negative control. 단위 테스트는 fake port. GUI probe 1 run/step, 3-run gate 1회 |
| Pitfalls | moc 심볼 누락 → autogen timestamp 삭제. 실행 중 exe 는 다른 이름으로 링크. 코드페이지 불일치 → `scripts/build-app.ps1` 만 사용 |
| Current Launcher implementation map | 패턴별 실제 파일 경로 표 (Events, Agent, Ports, Adapters, Commands, Presenter, Session, Dispatcher, Order point, Probe, Preprocess engine, Material, Records) |

### development/dash-ui-recipe.md: 신규 기능 절차

참조 구현을 먼저 고르고 (Material / Preprocess engine / Results Analyzer / Direct Launch), 11단계를 순서대로 진행한다.

```
[1] Contracts        contracts/<module>/<module>_events.h
   │   값 전용, eventName, 식별자 4종 (receiver, projectGeneration, requestId, operationId)
   ▼

[2] Pure functions   model/<module>/
   │   I/O·싱글턴 없는 변환 → 단위 테스트·워커 실행 가능
   ▼

[3] Agent            model/Dash<Domain>Agent
   │   ordo::core::Agent + enable_shared_from_this, QCoro 멤버 코루틴, onRemove 취소
   ▼

[4] Execution
   │   파일 I/O = 세션 DashIODispatcher 1 job / 긴 작업 = 전용 executor + whenQuiescent()
   │   job 은 복사된 값만 받음. 경로·설정은 port/adapter 가 UI 스레드에서 캡처
   ▼

[5] Commands         controller/<module>_commands   (agent 조회 후 호출만)
   ▼

[6] Presenter        view/Dash<Domain>Presenter
   │   signal → intent, fact 필터 (receiver·generation·Set·request), 팝업 queued
   ▼

[7] Widget           signal + display method 만. model/·controller/ include 금지
   ▼

[8] App assembly     app/DashAppSession   등록·역순 해제, isPreprocessBusy / whenPreprocessQuiescent
   ▼

[9] Boundary         tests/CMakeLists.txt ui_boundary_check 에 추가, negative control 유지
   ▼

[10] Tests           pure 함수 (LF fixture) + agent (fake port + real dispatcher) + 실데이터는 env gate
   ▼

[11] Probe           변경 행동당 1 시나리오 (성공·실패·stale·slow I/O·작업 중 삭제)
       완료 기준: 빌드·전체 suite·boundary check 통과, processEvents/waitForFinished 없음, 3-run gate
```

서브에이전트 위임 프롬프트 필수 항목: Git 변경 명령 금지, `scripts/build-app.ps1` / `scripts/run_tests.ps1` 만 사용, 전체 파일 clang-format, 단계 끝 전체 probe 1회, 출력에 **KB candidates**.

### workflow/dash-ui-migration.md: 레거시 전환 절차

| Phase | 완료 기준 |
|---|---|
| 1 Audit | 진입점별 model signal·getter·호출·싱글턴·파일 I/O·`processEvents`·include·wiring·테스트를 `file:line` 으로 나열 |
| 2 Design | 계약·식별자·소유권·수명·order point·컴파일 검사 확정. 불충분 대안 명시 |
| 3 Gather writes | 설정 파일별 writer 전부 `DashIODispatcher` 의 store 1개로 |
| 4 Move business flow | 결정·순서를 Command 뒤 Agent 로. 확인은 fact → View dialog → intent |
| 5 Move reads | View 는 fact 값만 그림. 읽기는 워커 |
| 6 Remove model from View | `setModel`, Model 포인터·signal·호출 제거 |
| 7 Prove boundary | 격리 컴파일 통과 + negative control 실패 |
| 8 Verify and share | fake port 단위 테스트, probe 3회 green, 팀 가이드 갱신 |

Audit 체크리스트는 Launcher 전환에서 놓친 사례를 항목화했다: presentation model 의 `saveOutputResponse` 가 store 우회, 대화상자 헤더의 숨은 model include, 결과 무시된 write (Material `.stlx` 성공 후 `.dbase` 실패에도 "success"), VTK 결과가 widget 을 우회해 main window 로 간 것, 자식 위젯의 plot factory·export 경로.

"Insufficient alternatives" 7항은 완료로 인정하지 않는 패턴 목록이다: signal 연결만 이동, Model 포인터를 presenter 로 이동, PIMPL/`QVariant` 로 숨김, 헤더 이동만, 빌드 성공을 근거로 독립 주장, 동기 엔진을 command 에서 호출하고 async 라 칭함, 백엔드 서비스 인터페이스를 Widget 에 주입.

동기 엔진 → executor 이동은 Preprocess 엔진이 밟은 5단계 (executor primitive → 동작 동등 추출 → port 뒤 비동기화 → stop-before-destroy → 실파일 검증) 를 그대로 따른다.

### verification/gui-probe.md: GUI probe

| 항목 | 값 |
|---|---|
| 실행 | `DashOpti.exe --gui-probe *> temp\probe.out.txt` |
| 필터 | `--gui-probe-only a,b` (디버깅 전용, gate 아님) |
| 가시 실행 | `--gui-probe-visible` (사용자 동의 필수) |
| exit | 0 통과 / 1 실패 / 2 플래그 오류 / 3 watchdog |
| watchdog | 시나리오당 60 s, 전체 900 s backstop |
| 출력 | `PASS:`/`FAIL:` 행, `TIME: <scenario> <ms>`, `PROBE: <passed>/<ran>` |

실행 횟수 규칙은 역할별로 고정돼 있다.

| 시점 | 실행 | 주체 |
|---|---|---|
| 개발 중 | 영향 시나리오만 | 구현자 |
| 단계 끝 | 전체 1회 | 구현자 (서브에이전트) |
| 인계 전 (리뷰·커밋·goal task 체크) | 전체 3회 연속 | 서브에이전트 구현 시 메인 에이전트 |

시나리오는 drive → settle → assert → capture 순서로 짜고, 상태 복원은 시작 시, 정리는 scope guard 에서 한다. Probe 전용 seam 은 세션 또는 adapter 에만 추가하며 기본값은 no-op (`setLaunchModelPortDecorator`, `setIoJobDelayForTesting`, `holdPreprocessExecutorForTesting`, `newProjectForTesting` 등). 실패 주입은 가장 약한 도구를 고른다: save 만 막는 `GENERIC_READ` + `FILE_SHARE_READ` 잠금, 배타 잠금, 사용 직전 파일 삭제, I/O 지연 + 20 ms 타이머.

주의 규칙 중 반복 재발형: MSVC 는 인자를 우→좌 평가하므로 `check(action(), describe())` 는 action 전 값을 찍을 수 있음, 오프스크린은 GL 미지원이라 plot 캡처가 비어 `exportToJson()` 으로 단언, `MessageBoxWatcher` 는 pass-through 목록 외 박스를 escape 로 닫음, 삭제 직후 `isGeneralIoQuiescent()` 단언 금지.

### workflow/commit.md: LOG.md 기반 커밋

명시적 요청 시만 실행. "commit" 은 push 를 포함하지 않고, amend·rebase·force push·`--no-verify` 는 권한 밖이다.

```
[1] Inventory     LOG.md 엔트리별 Commit status + git status + branch -vv
   │   경로를 Committable / Already committed / Never tracked / Gone 으로 분류
   │   엔트리에 없는 작업 파일은 보고만 (stage 안 함)
   ▼

[2] Group         토픽당 1 커밋. hunk 분할 금지. vendored → code+tests → docs 순
   ▼

[3] Pre-flight    staged .h/.cpp 를 pinned clang-format --dry-run -Werror
   │   third_party/ 는 포맷 제외. diff --cached --check (trailing space 등)
   ▼

[4] Commit/Push   git add -- <명시 경로>, git commit --file, push 는 요청 시만
   │   hook 실패 = 커밋 안 됨 → 원인 수정 후 새 커밋. amend 금지
   ▼

[5] Update LOG    pushed → 엔트리 삭제 / 미push → status·hash 기록
   ▼

[6] Report        hash·제목·파일수, hook 결과, push range, 제외 파일과 사유
```

## 함정 노트 카탈로그

노트는 `Symptom:` / `Rule:` 두 줄로 시작해 검색 가능한 오류 문구를 담는다. 본문은 Problem / Context (프로젝트 내 증거 file:line, 커밋, 날짜) / Solution / Verification / Recurrence / Summary.

### qt/

| 노트 | 증상 | 규칙 |
|---|---|---|
| nested-event-loop-reentrancy | 겹치면 안 되는 작업이 겹침, `exec()` 복귀 후 객체 소멸 | 비즈니스 flow 안에서 nested loop 금지. `open()` + 답변 intent. 레거시가 돌면 삭제 액션 거부 |
| qprocess-owner-thread-stop | Stop 이 UI 를 멈춤, 이전 프로세스 종료 전 새 run 시작 | QProcess 는 소유 스레드에서만. terminate → finished/timer → kill. 실제 종료까지 예약 유지 |
| qsavefile-windows-replace-retry | `QSaveFile::commit()` 간헐 실패, 방금 쓴 파일 삭제 불가 | 1 큐에서 QSaveFile, 실패 시 짧게 재시도 (store 는 3회, 50/100 ms) |
| canonicalfilepath-missing-file-empty | 없는 파일 둘이 "같은 파일" 판정 | `canonicalFilePath()` 는 미존재 시 빈 문자열. 비교 전 존재 확인 |

Planned (아직 노트 없음): `QFuture` 단일 continuation, `Q_OBJECT` 추가 후 moc 누락.

### build/

| 노트 | 증상 | 규칙 |
|---|---|---|
| msvc-ninja-showincludes-codepage | 헤더 수정이 재빌드 안 됨, `#deps 0`, 가짜 SEGFAULT | `msvc_deps_prefix` 가 코드페이지에 묶임. 같은 코드페이지로 configure/build. `scripts/build-app.ps1` 만 사용 |
| test-qt-dll-path-popup | `Qt6Core.dll 없음` 박스, exit `0xc0000135` | `tests/CMakeLists.txt` 가 PATH 추가. 테스트는 `scripts/run_tests.ps1` 로만 |
| precommit-whole-file-format | 안 건드린 줄 때문에 `place(s) not formatted` | 건드린 C/C++ 파일은 전체 포맷 후 stage |
| test-fixture-line-endings | byte-parity 테스트가 checkout 후 CRLF/LF 로 실패 | fixture 는 LF 저장, 플랫폼 텍스트 변환 기준으로 비교 |
| vcpkg-reinstall-gcs-auth | `ReauthUnattendedError`, 패키지가 `vcpkg_installed` 에서 사라짐 | 브랜치 전환 후 첫 빌드 전 `gcloud auth login` 갱신 (사용자만 가능) |
| git-archive-autocrlf | vendored 파일이 CRLF, blob hash 불일치 | `git -c core.autocrlf=false -c core.eol=lf archive` + hash 검증 (Ordo v0.1.0 vendoring 때 26 파일 903 CRLF) |

Planned: 실행 중 `DashOpti.exe` 가 링크를 잠금.

### reader/

| 노트 | 증상 | 규칙 |
|---|---|---|
| selector-path-spelling | `time selector is absent from this file`, batch 에서 Missing 집계 | SDK selector 가 읽을 때의 경로 문자열을 품음. `DashPreprocessor::spelled()` 로 경로 1종 통일, 우회 금지 |

### debug/

| 노트 | 증상 | 규칙 |
|---|---|---|
| msvc-crash-reports | `0xc0000409`/`0xc0000005`/`0xc00000fd`, qFatal 흔적 없음 | `DashCrash` 가 쓰는 `DashOpti_crash_<time>_<pid>.txt/.dmp` (`%LOCALAPPDATA%\NumeReal\Logs`) 를 읽음. Qt 6 `qAbort()` 는 `__fastfail` 이라 SEH 우회 |
| gl-context-qpixmap-at-exit | 가시 실행이 종료 시 `QPixmap: Must construct a QGuiApplication` qFatal | GL 위젯을 가진 창은 `QApplication` 생존 중 삭제 |
| mcp-shim-not-connecting | `dashopti` MCP `CONNECTION_CLOSED`, `No module named 'mcp'` | `.mcp.json` 이 쓰는 Python 에 `pip install mcp`, 그 전엔 `tools/mcp-shim/call_tools.py` |

## 지식 관리 규칙 (Knowledge Upkeep)

```
[후보 발생]  구현 중 트랩 / 서브에이전트 출력의 "KB candidates" (symptom → cause → fix)
   │   ※ 서브에이전트 후보는 주장이지 사실 아님. 메인 에이전트가 소스로 검증
   ▼

[입장 심사]  4조건 모두 통과해야 제안
   │   1. 재사용 근거: 재발했거나 진행·예정 작업이 다시 만남 (작업명 명시)
   │   2. 비도출: 코드·API 문서·주석·기존 노트에서 빨리 못 얻음
   │   3. 일반성: 1회 실행·1모듈 현 상태·1티켓 넘어 유효
   │   4. 비중복: 기존 노트가 있으면 Recurrence 추가로 대체
   ▼

[제안·승인]  재사용 근거 1줄과 함께 사용자에게 제안. 승인 없으면 미기록
   ▼

[기록]  트랩 → sample-pitfall 양식 + 폴더 README 행 / 규칙 → 해당 절차 문서
   ▼

[정리]  낡거나 틀린 지침은 즉시 삭제·교정. goal 아카이브 시 Recurrence 없는 노트 병합·삭제
       대부분의 후보는 걸러지고 "none" 이 정상 결과
```

## ordo-use 와의 관계

| 구분 | dash-opti-dev | ordo-use |
|---|---|---|
| 대상 | DashOpti 프로젝트 고유 규칙·절차·함정 | Ordo 프레임워크 위에 앱을 만드는 일반 규칙 |
| 흐름 명칭 | Dash UI 표준 흐름, `Dash<Domain>Agent`, `DashIODispatcher` | Event / Agent / Command / View adapter, `Kernel`, `ViewHost` |
| 비즈니스 정책 위치 | Agent 의 QCoro flow (Launcher D8) | Command (Ordo 기본) |
| 참조 방향 | general / recipe / migration 이 `../../ordo-use/SKILL.md` 를 링크 | DashOpti 를 모름. 자기완결 |
| 검증 | GUI probe 3-run gate | `--smoke` 헤드리스 자가 점검 + post-verify 6항 |

ordo-use 는 "스킬과 헤더가 다르면 헤더가 이긴다" 를 명시하고, `patterns.md` 의 헤더 표로 시그니처를 교차 확인하게 한다. dash-opti-dev 는 Ordo 기본 지침과 의도적으로 다른 지점 (정책 위치) 을 general.md 에 기록해 두 스킬이 충돌할 때 어느 쪽을 따를지 정해 뒀다.

## 설치와 배포

| 항목 | 값 |
|---|---|
| 원본 | `skills/` (편집 대상). 설치본은 생성물 |
| 설치기 | `tools/install_skills.ps1` → `tools/skills/install_skills.py` (Python 3.9+). macOS 에서는 `.py` 직접 실행 |
| 의존 선언 | `tools/skills/skills.json`: `dash-opti-dev.requires = ["ordo-use"]` → 자동 동반 설치 |
| 플랫폼 | claude `.claude/skills/`, codex `.agents/skills/`, antigravity `.agent/skills/` (user scope 는 `~/` 하위) |
| 모드 | copy (기본, 재실행으로 갱신, 로컬 편집 시 `--force` 필요) / link (junction 또는 symlink) |
| 기록 | `<root>/.dash-skills.json`. 설치기는 여기 적힌 스킬만 건드림 |
| git | `.git/info/exclude` 에 `# >>> dash skill installer` 블록으로 설치본·기록 파일 제외 |
| 상태 값 | `-`, `up to date`, `outdated`, `modified`, `linked`, `broken link`, `unmanaged` |

이 저장소 (macOS) 에서 2026-10-19 설치한 명령과 결과:

```
python3 tools/skills/install_skills.py --platform claude --skill dash-opti-dev --yes
# [claude/project] ordo-use: installed - copied 5 files
# [claude/project] dash-opti-dev: installed - copied 26 files
```

## 관찰

- 절차 문서의 명령 예시는 전부 PowerShell (`scripts/build-app.ps1`, `Select-String`, `$LASTEXITCODE`) 이다. macOS 에서 빌드·probe 를 돌리는 경로는 스킬에 없다.
- `qt/README.md`, `build/README.md` 의 Planned 항목 3개는 general.md 한 줄 규칙으로만 존재한다. 재발 시 노트 승격 대상이다.
- gui-probe.md 의 "Never start a solver" 규칙에 개인 승인 예외 (San, 2026-10-14, `PING.EXE` 대체) 가 본문에 박혀 있다. 규칙 문서에 1회성 결정이 섞인 사례다.
- `general.md` 의 Launcher 구현 맵은 파일 경로 스냅샷이라 리팩터링 때 같이 갱신해야 한다. 스킬 자체가 "소스로 재확인" 을 요구하므로 낡아도 치명적이진 않다.
