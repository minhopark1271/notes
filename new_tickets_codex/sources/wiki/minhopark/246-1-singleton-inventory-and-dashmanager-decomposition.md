# 싱글톤 4종 실측과 DashManager 분해 순서

> 관련 Issue: #246
> 기반 문서: [[204-1-entity-ownership-hierarchy]] (소유 계층 · W20 배경) · [[195-1-backlog-code-evidence]] (W19 근거)
> 측정 기준: 브랜치 `dev`, `4c7608e`, 2026-09-04. 호출수는 `grep -r --include="*.cpp" --include="*.h"` 실측 (라인 앵커는 측정 시점 기준)

## 0. 결론 먼저

1. **싱글톤은 4개, 그중 분해 대상은 `DashManager` 하나** — 나머지 셋은 형태를 유지한다.
2. **DashManager 의 문제는 크기가 아니라 전역 접근 경로가 하나로 수렴한 것** — `Mgr()` 311회 중 상위 2종(`GetHandlePickingInteraction` 58, `Redraw` 49)이 순수 접근자다. 호출부가 필요로 하는 건 DashManager 가 아니라 그 뒤의 객체다.
3. **판정 기준은 "싱글톤이냐"가 아니라 "인터페이스가 몇 축이냐"** — `DashProjectManager` 는 호출수 227건으로 비슷한데도 문제가 되지 않는다 (아래 2절).
4. **추출은 이미 절반 끝났다** — `DashRenderingManager` · `DashMorphingEngine` · `DashHandleVisualizer` · `DashSolverNxCad` 가 이미 별도 클래스다. DashManager 는 그 소유자 겸 유일한 접근 통로로 남아 있다. 남은 작업은 클래스 쪼개기가 아니라 접근 경로 끊기.

## 1. 싱글톤 인벤토리

| 클래스 | 진입점 | 구현 | public API | 호출수 | 판정 |
|---|---|---|---|---:|---|
| `DashRwActor` | `instance()` | Meyers (함수 내 static) | `openSession` 1개 | 1 | 유지 |
| `DashAnalysisModelContextRegistry` | `Instance()` | Meyers | `getOrLoad` · `get` · `activeContext` · `activeFilePath` · `activeActor` | 35 | 유지 |
| `DashProjectManager` | `Instance()` | static 포인터 + `Destroy` | 17개, 전부 경로/프로젝트 수명 | 227 | 유지 |
| `DashManager` | `Mgr()` | static 포인터 + `atexit(Destroy)` | 40개 이상, 책임 10종 | 311 | **분해** |

`DashProjectManager` 호출수 227 = `DashProjectManager::Instance()` 179 + `DashManager::PrjMgr()` 48. 후자는 전자로 리다이렉트할 뿐이다 (`DashManager.cpp:214`).

`DashRwActor` 는 싱글톤이 편의가 아니라 **본질**이다. RW DLL 을 단일 스레드에 감금하는 유일 소유자이고, 헤더의 LEAF RULE 주석(`DashRwActor.h:31-33`)이 DashManager · 렌더링 · view 를 절대 참조하지 않는다고 못박아 둔 상태다. 인스턴스를 늘리면 감금 자체가 깨진다.

### 싱글톤이 아닌 전역 static (별도 축)

| 위치 | 대상 | 성격 |
|---|---|---|
| `controller/async/ProcessJob.cpp:17` | `static QSet<ProcessJob*> jobs` | 실행 중 job 레지스트리 |
| `controller/DashExtensionProcess.cpp:13` | 익명 namespace 의 데몬 PID 맵 (exe basename 키) | 자기가 띄운 자식만 회수하기 위한 장부 |

둘 다 전역 상태이긴 하나 싱글톤 객체를 제공하는 클래스가 아니다. W20 스코프와 분리해 다룬다.

## 2. 판정 기준 — 인터페이스 축 수

`DashProjectManager` 와 `DashManager` 는 호출수가 227 대 311 로 같은 급인데 유지보수 부담이 다르다. 차이는 헤더가 노출하는 것에서 나온다.

| 항목 | DashProjectManager | DashManager |
|---|---|---|
| 헤더 줄수 | 62 | 250 |
| 헤더 의존 | `QString` + 전방선언 2 | vtk 헤더 8종 + Qt 6종 + 전방선언 12 |
| 인터페이스 축 | 1 (경로 · 프로젝트 수명) | 10 (3절) |
| 구현 줄수 | 319 | 1040 |

호출수가 아니라 축의 수가 비용을 만든다. 넓은 인터페이스를 전역으로 열어 두면 호출부 하나가 필요로 하는 멤버는 하나여도 헤더 전체를 컴파일 의존으로 끌고 들어온다.

## 3. DashManager 가 지고 있는 책임 10종

| # | 책임 | 대표 멤버 |
|---|---|---|
| 1 | VTK 렌더 인프라 | `m_renWin` · `m_renderer` · `m_camWidget` · `m_lut` · `Redraw` |
| 2 | 인터랙션 소유 | `m_handlePicking` · `m_interactorStyleRubberBand` |
| 3 | 모핑 도메인 상태·알고리즘 | `m_inputVTU` · `m_linearizedVTU` · `m_midNodeMap` · 2차 요소 선형화/복원 · bound size · step · preview · DOE |
| 4 | 프리뷰 외관 상태 | `m_savedUpperColor` · `m_savedLowerOpacity` 등 4개 |
| 5 | 외부 프로세스 수명 | `DashSolverNxCad` + `DashExtensionProcess` 3종 + `DashTopOptPostprocessRunner` |
| 6 | 전역 설정 | `m_solverPaths` (QSettings 로딩) · `m_cpuCoreCount` |
| 7 | 공유 모델 소유 | `m_designVariableModel` |
| 8 | 뷰 포인터 역참조 | `m_geometryParameterWidget` · `m_morphingSettingsWidget` |
| 9 | NX CAD 파라미터 캐시 | `m_lastNxCadParameterJson` + `applyLastNxCadParameterJsonToGeometryModels()` |
| 10 | 타 싱글톤 재노출 | `PrjMgr()` |

8번은 [[204-1-entity-ownership-hierarchy]] 5절이 계층 역전으로 지목한 것과 같은 멤버다.

### Mgr() 멤버별 호출 빈도 (상위 12)

| 멤버 | 호출수 | 책임 # |
|---|---:|---:|
| `GetHandlePickingInteraction` | 58 | 2 |
| `Redraw` | 49 | 1 |
| `GetRenderer` | 16 | 1 |
| `GetRenderingManager` | 14 | 1 |
| `UpdatePreviewMorphing` | 13 | 3 |
| `GetInputVTU` | 13 | 3 |
| `GetHandleVisualizer` | 11 | 3 |
| `GetModelBoundSize` | 10 | 3 |
| `solverNxCad` | 9 | 5 |
| `GetGeometryParameterWidget` | 8 | 8 |
| `mcuDaemon` | 6 | 5 |
| `getSolverPath` | 6 | 6 |

책임 1 + 2 (렌더 · 인터랙션) 합계가 140건으로 전체 311건의 45퍼센트다.

### 호출 집중 파일 (상위 6)

| 파일 | Mgr() 호출수 |
|---|---:|
| `view/DashGeometryParameterWidget.cpp` | 67 |
| `view/DashMainWindow.cpp` | 49 |
| `view/overlay/DashMorphingSettings.cpp` | 40 |
| `controller/DashHandlePickingInteraction.cpp` | 36 |
| `controller/DashMorphingController.cpp` | 25 |
| `model/DashJobRunner.cpp` | 13 |

## 4. 유지보수 비용이 나오는 지점

- **헤더 팬아웃** — `DashManager.h` 가 vtk 8종 + Qt 6종을 노출한다. 한 줄만 고쳐도 30개 파일이 재빌드된다.
- **테스트 불가** — `Mgr()` 최초 호출이 생성자(`DashManager.cpp:57-124`)에서 외부 프로세스 4개 + QSettings + `vtkGenericOpenGLRenderWindow` 를 만든다. DashManager 를 거치는 어떤 단위도 데몬을 띄우지 않고는 인스턴스화할 수 없다.
- **서비스 로케이터화** — 호출 상위 2종이 순수 접근자다. 의존을 생성자에 드러내지 않고 호출 시점에 전역에서 당겨 쓰므로, 어떤 클래스가 무엇에 의존하는지 헤더만 봐서는 알 수 없다.

## 5. 분해 순서

되돌리기 비용이 낮은 순. 각 단계 종료 시 빌드 가능 상태를 유지한다.

```
[1단계] PrjMgr() 제거
   │   1. 48곳을 DashProjectManager::Instance() 로 기계적 치환
   │   2. DashManager.h / .cpp 에서 PrjMgr 선언·정의 삭제
   │   ※ 동일 대상 진입점 2개를 없애는 것 — 동작 변화 없음
   │      verify: 빌드 통과 + PrjMgr 심볼 0건
   ▼

[2단계] 렌더·인터랙션 주입 전환
   │   1. Redraw · GetRenderer · GetRenderingManager 를
   │      DashRenderingManager 참조 주입으로 대체
   │   2. GetHandlePickingInteraction 을 생성자/세터 주입으로 대체
   │   3. 호출 집중 3파일(GeometryParameterWidget · MainWindow ·
   │      MorphingSettings, 합계 156건)을 먼저 처리
   │   ※ 311건 중 140건이 사라짐
   │      verify: Mgr() 호출수 180건 미만
   ▼

[3단계] 프로세스·설정 소유권 이관
   │   1. DashExtensionProcess 3종 + DashSolverNxCad +
   │      DashTopOptPostprocessRunner 를 별도 소유자로 이동
   │   2. m_solverPaths(QSettings) · m_cpuCoreCount 동반 이동
   │   ※ 생성자에서 프로세스가 뜨지 않게 하는 것이 테스트 가능성의 분기점
   │      verify: DashManager 생성자에 new DashExtensionProcess 0건
   ▼

[4단계] 모핑 상태를 DashMorphingEngine 으로
   │   1. m_inputVTU · m_linearizedVTU · m_midNodeMap ·
   │      m_originalQuadraticCells 이관
   │   2. HasQuadraticElements · CreateLinearizedVTU ·
   │      RecomputeQuadraticMidPoints · ComputeModelBoundSize ·
   │      ComputeMorphingSingleStep 이관
   │   3. MorphingPreview · UpdatePreviewMorphing · MorphFromDoe* 이관
   │   ※ DashManager.cpp 1040줄 중 최대 덩어리 (278-630, 657-1040)
   ▼

[손익분기] 통증 지점에 따라 중단 가능
       빌드 시간이 문제면 2단계까지, 테스트 도입이 목표면 3단계까지로 충분.
       4단계는 앞 세 단계를 마친 뒤 통증이 남아 있을 때 착수.
```

## 6. 204-1 과의 차이

| 항목 | [[204-1-entity-ownership-hierarchy]] (2026-07-20 `dev`) | 본 문서 (2026-09-04 `4c7608e`) |
|---|---|---|
| `Mgr()` 호출수 | 344 | 311 |
| 모핑 엔진 이름 | `DashMR::OperatorMorph` | `DashMorphingEngine` |
| `DashProjectManager` 판정 | pull 결합 해소를 W20 스코프에 편입 | 싱글톤 형태 유지 |

세 번째 항목은 모순이 아니라 축이 다르다. 204-1 이 지목한 것은 **model 계층이 경로를 전역에서 pull 하는 결합**이고, 본 문서가 판정한 것은 **싱글톤 형태 자체의 유지 여부**다. 경로를 생성 시 주입으로 바꾸는 작업은 `Instance()` 를 없애지 않고도 가능하므로 두 판정은 양립한다.

pull 결합은 재측정 결과 model 에만 있는 것이 아니다.

| 디렉토리 | `DashProjectManager::Instance()` 참조 파일수 |
|---|---:|
| `view/` | 16 |
| `model/` | 14 |
| `controller/` | 4 |
| `viewmodel/` | 1 |

`model/DashProject.cpp` 의 `SaveProject()` 역호출 7곳은 204-1 측정 그대로다.

## 7. 곁가지 (본 스코프 밖, 지우지 않고 기록)

- `controller/DashManager.h:127` `m_treeView` — 선언 1건, 참조 0건. 죽은 멤버.
- `controller/DashManager.cpp:208` `atexit(Destroy)` — QApplication 파괴 이후 시점에 Qt/VTK 객체를 delete 한다. 5절 3단계에서 소멸 순서를 손볼 때 같이 볼 지점.
- `m_designVariableModel` 이 소멸자에서 해제되지 않는다. 프로세스 종료 경로라 실무 영향은 없다.

## 8. 다음 단계

- [ ] Issue #246 의 체크박스에 5절 4단계를 반영 (착수 시점은 #215 W10-f 완결 이후)
- [ ] 1단계(PrjMgr 제거)를 별도 소이슈로 분리 — W10 과 파일 표면이 겹치지 않고 단독 착수 가능
- [ ] 2단계 착수 전 `view/DashGeometryParameterWidget.cpp` 67건의 실제 의존 대상 분류 (렌더 / 인터랙션 / 모핑 상태)
