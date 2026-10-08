# 구성 실측과 connect 배선의 타입 경계 전환

> 관련 Issue: #239
> 관련 문서: [[192-1-architecture-analysis-mvc-mvvm]] (아키텍처 정본, 97k 시점) · [[246-1-singleton-inventory-and-dashmanager-decomposition]] (W20 분해 순서) · [[281-1-morphing-entry-points-and-isolation-design-options]] (#281 설계)
> 측정 기준: `dev` @ `a2222cc`, 2026-09-22. 줄수는 `find`+`wc`, 결합 지표는 `grep` 실측 (재현 명령은 7절)

## 0. 결론 먼저

1. **13.6만 줄의 정체는 GUI 가 아니라 CAE 파이프라인 전체다** — 화면 코드(view 5.2만)보다 그 뒤의 도메인 엔진(model 3.5만)과 3D 인터랙션(controller 2.1만)이 함께 산다.
2. **뷰가 적은데 줄이 긴 이유는 화면 수가 아니라 화면당 밀도다** — 위젯 한 파일이 UI 구성·스타일·배선·검증·도메인 호출·상태 동기화를 전부 담는다.
3. **응집도·결합도 개선이 어려운 구조적 사실은 넷이다** — 모든 실행 경로를 관장하는 MainWindow 허브(싱글턴 축은 DashManager), 인터페이스 없이 구체 클래스를 직접 include·호출하는 계층 결합, 담는 타입 없이 connect 배선과 흩어진 멤버로만 존재하는 상태(Status), 테스트 0으로 안전망이 없는 화면 로직.
4. **처방은 connect 제거가 아니라 connect 가 나르는 것을 바꾸는 것이다** — 상태를 타입으로 승격한다. 선례가 이미 저장소 안에 있다: 모핑 승격 모델(`a2222cc`, `docs/morphing-request-service.md`).
5. **정적 경계의 수단은 셋이다** — 값 타입 시그니처(컴파일러가 검사), 진입점 고정(링커가 다른 통로를 없앤다), CMake 타깃 분리(빌드가 침식을 막는다).

## 1. 구성 실측 — 13.6만 줄의 정체

총 136,008줄(`*.cpp` `*.h` `*.hpp` `*.cc` `*.ui` `*.py`, build·third_party 제외), 그중 앱 코드(view+model+controller+viewmodel+utils+libs)가 약 11.6만 줄이다.

| 디렉터리 | 줄수 | 파일 | 내용 |
|---|---:|---:|---|
| view | 51,745 | 166 | 모듈별 위젯 20여 개. setupUI 손코딩, 인라인 `setStyleSheet` 139곳, 슬롯·상태 동기화 |
| model | 34,644 | 105 | 도메인 엔진 — 솔버 입력 생성, 잡 실행·프로세스 관리, 결과 파싱, KPI 계산, 최적화, 프로젝트 직렬화 |
| controller | 20,868 | 70 | VTK/OCCT 3D 인터랙션 — picking(3,101줄), 렌더링 매니저, 모핑 컨트롤러·서비스·DOE 실행기 |
| ui | 10,702 | 40 | Qt Designer `.ui` XML |
| tests | 9,097 | 21 | 유틸·프로세스 계열 + 모핑 상태 계열 (3절 4항) |
| viewmodel | 3,135 | 20 | Presentation Model 9모듈 (W21 선행분) |
| utils · libs · tools · scripts | 6,240 | 33 | 로거·코덱·Gizmo 등 |

이름은 GUI 지만 내용은 파이프라인이다. 형상 파라미터화 → 해석 실행 → 데이터 전처리 → 대리모델 학습·실행 → 최적화 → 결과 분석의 전 단계가 한 저장소에 있고, 각 단계의 화면(view)·엔진(model)·3D 조작(controller)이 세로로 쌓여 있다. [[192-1-architecture-analysis-mvc-mvvm]] 시점(97k) 대비 약 +39k 인데, 이는 기능 추가(모핑 승격 모델·기준모델 원장·KPI 이관 등)와 테스트 신설이 만든 자연 증가다.

## 2. 뷰가 적은데 줄이 긴 이유

화면당 밀도가 원인이다. 위젯 한 `.cpp` 가 레이아웃 생성(setupUI 손코딩), 인라인 QSS, 시그널 배선, 입력 검증, 도메인 객체 호출, 다른 위젯과의 상태 동기화를 전부 담는다. 대표 사례로 `view/DashResultsAnalyzerWidget.cpp` 가 3,801줄, `view/DashMainWindow.cpp` 가 3,670줄(헤더 313줄, 메서드 90+)이다. Qt Designer `.ui` 는 10.7k 줄이 별도로 있지만 view 본체 5.2만 줄의 주류는 C++ 손코딩이다.

여기에 뷰 뒤의 비-뷰 코드가 뷰보다 크다. `model/DashDataProcessor.cpp` 3,166줄, `DashJobRunner.cpp` 2,799줄, `DashModelRunner.cpp` 2,736줄은 화면이 아니라 파서·프로세스 오케스트레이션이고, `controller/DashHandlePickingInteraction.cpp` 3,101줄은 3D 조작이다. 마지막으로 유사 화면의 복제가 있다 — ModelBuilder/ModelRunner 의 MCU 변형이 view·model 양쪽에 각 2쌍씩 존재한다.

## 3. 개선이 어려운 구조적 사실 넷

**첫째, MainWindow 가 허브다.** `DashMainWindow.cpp` 는 include 123개로 구체 위젯·컨트롤러 20여 종을 직접 알고, 파일 IO·트리·도킹·애니메이션·모듈 선택 핸들러까지 90+ 메서드로 관장한다. connect 도 파일 단위 최다(87개)다. 어떤 절단선을 그어도 MainWindow 를 지나간다. 싱글턴 축의 같은 문제(DashManager `Mgr()` 311회)는 [[246-1-singleton-inventory-and-dashmanager-decomposition]] 이 실측했다.

**둘째, 계층 결합이 전부 구체 타입이다.** view 가 model 헤더를 91곳, controller 헤더를 83곳에서 직접 include 한다. include 방향 자체는 MVC 규율대로라 192-1 의 "경계 규율 양호" 판정과 모순되지 않는다 — 문제는 방향이 아니라 결합의 종류다. 인터페이스가 없어 절단면이 없고, 빌드 단위를 나눌 수 없다. W21 선행으로 Presentation Model 이 9모듈에 도입돼(view 17파일이 include) 호출 지점을 모으기 시작했지만, 직접 결합 경로와 병존한다.

**셋째, 상태가 배선 그래프에만 존재한다.** connect 는 앱 전체 689개다. 다수(위젯당 20~40개)는 버튼→슬롯 같은 위젯 내부 플러밍이라 문제가 아니다. 문제는 계층을 넘는 connect — "모델이 바뀌었으니 콤보를 갱신하라, 그러면 다른 위젯도 갱신하라"는 체인이다. "지금 시스템이 어떤 상태인가"가 어떤 타입에도 없고, 여러 위젯·매니저에 흩어진 멤버와 배선의 부수효과를 전부 따라가야만 재구성된다. 정적 분석도 테스트도 이 그래프 위에 경계를 그을 수 없다.

**넷째, 화면 로직의 안전망이 없다.** 테스트 17개 타깃은 유틸·프로세스 계열(Logger·XmlParser·GadgetCodec·JobState·LineAssembler·ProcessRuntime)과 모핑 상태 계열(MorphingBasis·MorphingService·PreviewStates·MeshQcStates·StateSnapshot·FixedMarkerSelection), 원장 계열(doe_selection·reference_model_ledger·set_reference_model)이다. 위젯·화면 로직 테스트는 0이다 — 분리 작업의 회귀를 잡을 수단이 수동 실행뿐이다 (#489).

한 문장으로: **분리할 이음새(인터페이스)가 코드에 없고, 잘라도 됐는지 확인할 테스트도 없어서, 모든 리팩토링이 "전체를 이해한 사람의 수작업 + 수동 검증"이 된다.**

## 4. 처방 — connect 가 나르는 것을 바꾼다

connect 를 없애는 것이 목표가 아니다. 이벤트 버스나 Redux 류 도입도 답이 아니다 — 배선을 다른 곳으로 옮길 뿐이다. 목표는 배선이 암묵적으로 유지하던 상태를 타입으로 승격해, 배선에는 "비동기 결말을 GUI 스레드로 돌려받는 마지막 한 칸"만 남기는 것이다.

먼저 connect 를 셋으로 분류한다. 위젯 내부 UI 플러밍은 유지한다. 계층 간 상태 동기화 체인이 제거 대상이다. MainWindow 의 모듈 간 오케스트레이션(87개)은 마지막에 처리한다.

승격의 선례가 저장소 안에 있다 — 모핑 승격 모델(`a2222cc`, `docs/morphing-request-service.md`). 종전 모핑도 시그널 체인이었지만 지금은 다음과 같다.

| 시그널 체인 방식 (종전) | 승격 모델 (현재 모핑) |
|---|---|
| 상태 = 여러 위젯·매니저에 흩어진 멤버 + 배선의 부수효과 | 상태 = 개별 C++ 타입 (`DashPreviewArmed` → `Frozen` → `Shown`) |
| 전이 = 시그널 발사 → 어딘가의 슬롯이 받아서 처리 | 전이 = 멤버 함수. `co_await armed.freeze(...)` 가 다음 상태 타입을 반환 |
| 검증 = 슬롯마다 방어 코드 | 검증 안 된 상태는 생성 자체가 안 됨 (`create() → Result<T>`) |
| 경계를 넘는 것 = live 객체 포인터 | 경계를 넘는 것 = 값 (`DashHandleBlock`, 요청은 DeepCopy) |
| 진입점 = connect 된 만큼 여러 곳 | 진입점 = `submitFreeze` / `submitMorph` 둘 |
| 실패 = 시그널로 흩어지거나 침묵 | 실패 = `Result<T>` 의 `ErrorCode` 로 호출 지점에 돌아옴 |

이 모델을 모듈당 다음 절차로 일반화한다. ① connect 분류(위 3종). ② 암묵 상태를 값 타입으로 — 예컨대 ResultsAnalyzer 의 `onMethodChanged → updateSecondaryCombo → updateTrainedModelCombo` 체인이 암묵적으로 유지하는 "현재 유효한 선택 조합"을 struct 로 만들고, 유효하지 않은 조합은 생성을 거부한다. ③ 경계를 함수 시그니처로 — 위젯은 요청을 값으로 제출하고 결과를 값으로 받는다. 중간 동기화 시그널이 사라지고 "무엇이 오가는지"가 헤더의 타입에 나타난다. ④ 시그널 수렴 — 모듈 파사드가 `stateChanged(const State&)` 하나만 노출하면 N 위젯 × M 시그널의 M×N 그래프가 M+N 으로 준다. ⑤ 테스트로 봉인 — 상태 타입은 GUI 없이 테스트된다(모핑의 5개 타깃이 선례).

W21 의 Presentation Model 과는 직교·상보다. PM 은 호출 **지점**을 모으는 층이고, 승격 모델은 **상태**를 타입으로 만드는 것이다. PM 이 모아 둔 호출부는 승격 시 수술 부위가 이미 정리돼 있다는 이점이 된다 (#239 본문의 W21 리스크 박스와 같은 결론).

## 5. 정적 경계의 세 수단

| 수단 | 강제 주체 |
|---|---|
| 경계를 넘는 데이터가 값 타입 시그니처에 나타남 | 컴파일러 (타입 검사) |
| 모듈당 진입점을 함수 몇 개로 고정 (`submit*` 패턴) | 코드 리뷰 + 링커 (다른 통로가 없음) |
| 디렉터리별 CMake 타깃 분리, `target_link_libraries` 로 허용 의존만 링크 | 빌드 시스템 — 위반 include 가 컴파일 실패 |

셋째가 핵심이다. 지금은 단일 타깃이라 view→model 직접 include 91곳이 전부 통과한다. 타깃을 나누면 위반이 컴파일 에러가 되어, 이후의 침식을 사람이 아니라 빌드가 막는다. 단, 타깃 분리는 2절의 구체 타입 결합이 값 타입·인터페이스로 끊긴 모듈부터만 가능하다 — 순서상 4절의 승격이 먼저다.

## 6. 적용 순서

새로 손대는 모듈부터 적용하고 MainWindow 는 마지막이다. 다음 사례는 이미 티켓과 설계가 있다 — #281 (DOE 배치의 동기 모핑 경로 이관)이 `docs/morphing-request-service.md` 7절에 이관 형태(`DashDoeSampleArmed` → 배치당 1회 freeze → 샘플별 Background 레인 morph)까지 설계돼 있어, 승격 모델을 두 번째 모듈에 복제하는 첫 사례로 적합하다. W20 (#246, god-object 해체) 착수 시에는 [[246-1-singleton-inventory-and-dashmanager-decomposition]] 의 "접근 경로 끊기" 와 본 문서 5절의 타깃 분리를 병행한다.

## 7. 측정 재현

```bash
# 줄수 분포 (build·third_party 제외)
find . -type f \( -name "*.cpp" -o -name "*.h" -o -name "*.hpp" -o -name "*.cc" \
  -o -name "*.ui" -o -name "*.py" \) -not -path "*/build*" -not -path "*/.git/*" \
  -not -path "*/third_party/*" | xargs wc -l | sort -rn | head -40

# connect 총수 / 파일별 상위
grep -rcE "\bconnect\(" view controller model viewmodel --include="*.cpp" | sort -t: -k2 -rn | head

# 계층 간 직접 include
grep -rE '#include "(\.\./)?model/' view --include="*.cpp" --include="*.h" | wc -l       # 91
grep -rE '#include "(\.\./)?controller/' view --include="*.cpp" --include="*.h" | wc -l  # 83
grep -rlE '#include "(\.\./)?viewmodel/' view --include="*.cpp" --include="*.h" | wc -l  # 17

# 인라인 스타일 / MainWindow 허브
grep -rn "setStyleSheet" view --include="*.cpp" | wc -l    # 139
grep -c '#include' view/DashMainWindow.cpp                 # 123
```
