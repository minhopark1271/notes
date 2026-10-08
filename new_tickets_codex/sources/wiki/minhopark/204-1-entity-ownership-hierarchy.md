# DashGUI2 엔티티 소유 계층 — 누가 누구를 소유·참조하나 (드래프트)

> 원본: 사전조사 Issue #204 — 본문을 이 페이지로 이관한 뒤 Issue 삭제 (2026-08-24). **본 페이지가 정본**
> 이관 주석: 아래 머리글의 `상태:` (Wiki 미연동·원격 미생성) 는 이관 전 시점 표기

> 상태: 로컬 드래프트 (GitHub Issue·Wiki 미생성 — 검토용)\
> 연관 Issue: #64 (Crash Debug — 계층 역전·God-object가 재진입/파급의 배경)\
> 자매 문서: [[192-1-architecture-analysis-mvc-mvvm]] (MVC/MVVM 패턴 판정) · [[206-1-w6-w10-thread-execution-design]] (실행 모델) · [[200-3-prioritized-backlog]] 5-2절 (W19\~W21 — 계층 역전·God-object 해소)\
> 후속 문서: [[Code-Map-Domain-Diagram]] — 같은 소유 계층을 **사내 6 도메인 구조도의 박스 이름에 맞춰** 다시 그린 축약본(5절) + 구조도 박스 ↔ 파일 전량 대조. 본 문서가 세운 "최상위는 셋" 구조는 유지되고, 구조도에 없는 `viewmodel/` 계층과 사문화 `DashModelRunnerMCU` 를 추가 보고\
> 후속 문서: [[246-1-singleton-inventory-and-dashmanager-decomposition]] — 싱글톤 4종 인벤토리 + `Mgr()` 호출 재측정(344 → 311)과 `DashManager` 분해 4단계. 본 문서 5절이 지목한 계층 역전을 W20 착수 순서로 구체화하고, `DashProjectManager` 는 pull 결합만 해소하고 싱글톤 형태는 유지하는 것으로 판정 조정\
> 목적: "DashModelRunner·DashJobRunner가 엔티티 구조상 상위 레벨 개념인가"라는 질문에서 출발해, 프로젝트의 **엔티티 소유/참조 계층**을 코드 실측으로 도식화한다\
> 분석 시점: 2026-07-20, 브랜치 `dev` — 소유 관계는 헤더 멤버 선언 실측 (라인 앵커는 분석 시점 기준, 유효기간 있음)

---

## 0. 결론 먼저

1. **최상위는 셋** — `main()`이 직접 세운다: `DashMainWindow`(뷰 루트) · `DashManager`(서비스 싱글톤) · `DashProjectManager`→`DashProject`(데이터 루트).
2. **모델의 진짜 루트 = `DashProject`** — 프로젝트가 열리면 그 안에 모델 인스턴스들이 리스트로 담긴다.
3. **DashModelRunner ≠ DashJobRunner (다른 층)** — `DashModelRunner`는 `DashProject` **직속 모델**(Optimizer·DataProcessor·AnalysisLauncher와 peer), `DashJobRunner`는 `DashAnalysisLauncher`가 소유하는 **하위 실행 엔진**. 규모(배치 오케스트레이터)는 크지만 계층은 한 단계 아래다 — **규모 ≠ 계층**.
4. **소유는 아래로, 참조는 위로도 (⚠ 양방향 역결합)** — 1절 트리는 composition(수명)만 그리지만, model 14파일이 `DashProjectManager::Instance()`로 경로를 pull하고 `DashProject`가 소유자의 `SaveProject()`를 역호출한다. `DashManager`→뷰 역참조와 같은 계급의 싱글톤 역결합 — **W20 스코프**(백로그 개정 30)에서 경로 주입 + dirty 시그널로 해소(5절).

## 1. 엔티티 소유 계층 (도식)

```
main()  [main.cpp]
├── QApplication app                    (이벤트 루프 — app.exec(), :83)
│
├── DashMainWindow   ★뷰 루트           (모든 위젯·도크를 소유, main.cpp:74)
│   ├── DashProjectWidget
│   ├── DashGeometryParameterWidget
│   ├── DashAnalysisLauncherWidget      ┈참조(setModel)┈▶ DashAnalysisLauncher
│   ├── DashModelRunnerWidget           ┈참조(setModel)┈▶ DashModelRunner
│   ├── DashOptimizerWidget             ┈참조(setModel)┈▶ DashOptimizer
│   ├── DashDataProcessorWidget         ┈참조(setModel)┈▶ DashDataProcessor
│   └── DashModelBuilder(MCU)Widget · DashOcctViewWidget · 각종 QDockWidget
│
├── DashManager::Mgr()   ★컨트롤러 싱글톤 (서비스 허브 — Mgr() 344회 호출)
│   ├── DashRenderingManager            (소유)
│   ├── DashMR::OperatorMorph           (모핑 엔진, 소유)
│   ├── DashSolverNxCad                 (NX 데몬 래퍼, 소유)
│   ├── DashExtensionProcess × 3        (journal·mcu·sensitivity 데몬, 소유)
│   ├── DashDesignVariableModel         (공유 모델, 소유)
│   └── ┈역참조┈▶ 일부 뷰 위젯 포인터 (m_geometryParameterWidget 등)  ← ⚠ 계층 역전
│
└── DashProjectManager::Instance()   ★데이터 싱글톤  (PrjMgr())
    └── DashProject   ★모델 루트 (프로젝트 데이터를 QList로 소유)
        ├── QList<DashModelRunner>        ← 프로젝트 직속 모델 (peer)
        ├── QList<DashOptimizer>          ← peer
        ├── QList<DashDataProcessor>      ← peer  (God-object 4,667줄)
        ├── QList<DashModelBuilder(MCU)>  ← peer
        ├── QList<DashGeometryParameter(CAD)> · Condition · AIGeometry  ← peer
        └── QList<DashAnalysisLauncher>   ← peer
                └── DashJobRunner         ◀── ★ 여기! AnalysisLauncher가 소유
                        (+ DashResultsAnalyzer, QFutureWatcher m_analysisWatcher)
```

**범례**: `├──` 트리 = **소유(composition, 수명 관리 주체)** · `┈참조┈▶` = **참조(포인터 보유, 비소유)** · `★` = 루트/싱글톤 · `⚠` = 계층 규칙 위반.

> ⚠ **트리 밖 역결합**: 위 트리는 **composition(수명)만** 표시한다. 실제로는 model 14파일이 `DashProjectManager::Instance()`로 경로·`DashIOController`를 **pull**하고, `DashProject`가 소유자의 `SaveProject()`를 **역호출**하는 model→싱글톤 상향 참조가 있다(5절). 소유(하향)와 접근(상향)이 얽힌 양방향 결합 — 도식이 깨끗해 보이는 것과 별개다.

## 2. 세 개의 최상위 — main()이 직접 세운다

| 루트 | 정체 | 역할 | 앵커 |
|---|---|---|---|
| `DashMainWindow` | 뷰 루트 | 모든 위젯·도크 소유 | `main.cpp:74`, 멤버 `view/DashMainWindow.h:216-233` |
| `DashManager::Mgr()` | 컨트롤러 싱글톤 | 렌더링·모핑·솔버·데몬·공유모델 등 **서비스 허브** | `controller/DashManager.h:83`(Mgr), `:129-132`(데몬), `:116`(morph), `:127`(공유모델) |
| `DashProjectManager::Instance()` | 데이터 싱글톤 | `DashProject`(모델 루트) 소유 | `controller/DashProjectManager.h:18`(Instance), `:27`(m_project) |

- **모델의 진짜 루트는 `DashProject`** — 모델 인스턴스들의 수명은 여기 QList가 관리한다 (`model/DashProject.h:107-113`).
- 두 싱글톤은 **역할이 갈린다**: `DashManager` = 서비스/실행 자원(렌더러·모핑 엔진·솔버·데몬), `DashProjectManager` = 데이터(프로젝트).

## 3. 소유 vs 참조 — 뷰↔모델 관계

위젯은 모델을 **참조만** 하지 소유하지 않는다. 소유는 `DashProject`, 위젯 자신의 소유는 `DashMainWindow`. 이것이 MVC의 view→model 단방향이다.

| 위젯 (DashMainWindow 소유) | 참조하는 모델 (DashProject 소유) | 배선 |
|---|---|---|
| `DashModelRunnerWidget` (`:113`) | `DashModelRunner` | `setModel()` `:30` |
| `DashOptimizerWidget` (`:103`) | `DashOptimizer` | `setModel()` `:31` |
| `DashAnalysisLauncherWidget` (`:102`) · `DashReferenceFileWidget` · `DashDoeCasesWidget` | `DashAnalysisLauncher` | `setModel()` `:43` 등 |
| `DashDataProcessorWidget` (`:74`) | `DashDataProcessor` | `setModel()` `:34` |

## 4. DashModelRunner vs DashJobRunner — 왜 다른 층인가

| | DashModelRunner | DashJobRunner |
|---|---|---|
| 소유자 | `DashProject` (`QList<DashModelRunner*>`, `:111`) | `DashAnalysisLauncher` (`m_jobRunner`, `:187`) |
| 계층 위치 | **프로젝트 직속 모델** (peer) | AnalysisLauncher의 **하위 실행 엔진** |
| 소유처 개수 | 프로젝트당 다수 | 전수 검색 결과 **AnalysisLauncher 하나뿐** |
| 역할 | 단건 모델 예측 실행 (MCU/DeepOpt exe — 완전 시그널 구동, 모범) | 배치(DOE) 오케스트레이션·FE 솔버 실행 (최대 규모) |

**핵심**: 이름은 둘 다 "Runner"지만 **형제가 아니라 다른 층**이다. DashJobRunner가 커 보이는 건 배치 실행 로직이 몰려서지 계층이 높아서가 아니다. W6·W10은 바로 이 실행 로직을 `ProcessJob`/`Job`으로 빼내는 작업이다([[206-1-w6-w10-thread-execution-design]]).

## 5. 계층 역전 — W19\~W21이 겨냥하는 것 (⚠)

`DashManager`(컨트롤러 싱글톤)가 **뷰 위젯 포인터를 역참조로 보유**한다 (`m_geometryParameterWidget` `:105`, `m_morphingSettingsWidget` `:107`). 계층 규칙(view → model 단방향)을 거스르는 model→view 방향이다. 이것이 백로그 5-2절 **W19(플로터 레이어 역전 제거)·W20(God-object 해체)·W21(Presentation Model 도입)**이 해소하려는 순환의 실체다. 무배경 해설은 [[195-1-backlog-code-evidence]] W19.

**두 번째 역결합 — `DashProjectManager ↔ DashProject` (⚠, 1절 트리 밖)**: 소유는 아래로(Manager→Project) 옳지만 **참조가 위로도 흐른다**. model 14파일이 `DashProjectManager::Instance()`로 경로·`DashIOController`를 **pull**(전역 싱글톤 의존)하고, `DashProject.cpp`가 자기 **소유자**의 `SaveProject()`를 7곳에서 **역호출**(자식→부모 lifecycle 호출)한다. `DashManager`→뷰 역참조와 **같은 계급의 싱글톤 역결합**이다. 처방: ⑴ 경로·`DashIOController`를 생성 시 **주입**(모델이 싱글톤을 모르게) ⑵ `SaveProject` 역호출 → model은 **dirty 시그널만 상향**, 저장 구동은 매니저/컨트롤러가(자식→부모 역호출 제거). 이 해소는 **W20 스코프에 편입**(백로그 개정 30) — `DashManager` 해체와 동일 대수술 창. #213(W10-d)/D1은 이 싱글톤에 **락만 추가(존치)**하므로 스레드 안전만 확보할 뿐, 주입 전환은 W20이 담당한다.

## 6. 코드 앵커 (검증, 2026-07-20 · `dev`)

- 최상위: `main.cpp:31`(QApplication)·`:74`(DashMainWindow)
- 서비스 싱글톤: `controller/DashManager.h:83`(Mgr), `:63`(rendering), `:116`(morph operator), `:127`(design variable model), `:129-132`(NxCad·journal·mcu·sensitivity), `:105`·`:107`(뷰 역참조 — 계층 역전)
- 데이터 싱글톤·모델 루트: `controller/DashProjectManager.h:18`(Instance)·`:27`(m_project) → `model/DashProject.h:107-113`(모델 QList 소유)
- 역결합(트리 밖, W20 대상): `model/DashProject.cpp`의 `DashProjectManager::Instance()` 참조 다수 + `SaveProject()` 역호출 7곳(`:691`·`:698`·`:705`·`:713`·`:729`·`:743`·`:750`) · model 14파일이 매니저 역참조(어휘 스캔 `grep -rl DashProjectManager model/`, 2026-07-21 `dev`)
- 하위 실행 엔진: `model/DashAnalysisLauncher.h:187`(DashJobRunner m_jobRunner)
- 뷰 루트·위젯: `view/DashMainWindow.h:216-233`
- 뷰→모델 참조: `view/DashModelRunnerWidget.h:30,113` · `DashOptimizerWidget.h:31,103` · `DashAnalysisLauncherWidget.h:43,102` · `DashDataProcessorWidget.h:34,74`
