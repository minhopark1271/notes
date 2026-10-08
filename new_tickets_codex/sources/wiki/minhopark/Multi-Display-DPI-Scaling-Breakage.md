# 창·레이아웃 크기 관리 — 문제 전수 분석과 Qt 표준 패턴 기반 개선 방향

> 관련 Issue: 없음 (독립 문서). L0-5 / L1-1 의 Frameless·중첩 QMainWindow 구조는 #14 "전체 레이아웃 업데이트" 에서 도입됨.
> 상태: **정적 코드 분석 결과** — 실기 재현 검증 미수행 ("검증되지 않은 항목" 참조)
> 사내 선례(`DashOpti_Analyzer` `refactor/base`)의 동일 계열 수정을 코드 대조로 검토해 부록에 정리했다. 채택 대상 4건, 결함 5건, 사실 정정 1건.
> 처방이 VTK · OCCT · OpenGL 플롯 · 파이썬 계층과 충돌하는지 별도로 검토했다 ("렌더링·파이썬 스택 호환 검토"). **차단 요인 없음**, 접점 결함 5건.

## 개요

크기 관련 증상이 세 갈래로 보고되었다.

| 증상 | 발생 조건 | 심각도 |
|---|---|---|
| **응답 정지 후 창이 화면 밖까지 커져 복구 불가** | 배율이 다른 모니터로 이동 시 | **치명** |
| 창 전체의 크기·위치가 어긋남 | 배율이 다른 모니터 간 이동 시 | 높음 |
| 메인 창 내부 dock 폭·높이가 제멋대로 변함 | 상시 | 높음 |
| 같은 조작인데 결과가 매번 다름 | 상시, 비결정적 | 중간 |

첫 번째 증상은 **작업 중인 프로젝트를 저장하지 못하고 강제 종료해야 하는 상태**로 이어지므로 별도로 다룬다 (바로 아래 절).

개별 버그를 하나씩 고치는 방식으로는 수렴하지 않는다. 확인된 문제 25건 중 대부분이 **하나의 공통 뿌리**에서 파생되기 때문이다.

> **크기를 결정하는 권한이 Qt 레이아웃 시스템이 아니라 명령형 코드 여기저기에 흩어져 있다.**

따라서 이 문서는 "Qt 가 원래 제공하는 크기 관리 패턴" 을 준거로 먼저 세우고(1부), 현재 코드의 문제를 그 원칙에서 벗어난 정도에 따라 근본에서 지엽 순으로 배치한다(2부). 각 항목은 **문제와 해법을 함께** 기술한다.

---

# 0부 — 치명 발현: 프리즈 후 복구 불가

배율이 다른 모니터로 창을 옮기면 **응답이 수 초에서 수십 초간 멈춘 뒤, 창이 화면 밖까지 커진 채로 조작 불가 상태**가 된다. 개별 원인들이 최악의 순서로 연쇄한 결과다.

```
[1] DPI 전환 — 논리 크기 유지, 물리 크기 폭증
   │   Round 정책(L0-3)으로 DPR 이 1.0 → 2.0 급변
   │   Qt 는 논리 크기를 유지하므로 물리 픽셀은 가로·세로 각 2배 = 면적 4배
   │   창이 이미 화면의 80%(L2-7) 였다면 물리 크기는 화면을 크게 초과
   ▼

[2] GL 프레임버퍼와 네이티브 창이 각각 재구성
   │   QVTKOpenGLNativeWidget (DashMainWindow.cpp:1496) 은 QOpenGLWidget 파생이라
   │   별도 HWND 가 아니라 FBO 다. 표시 중인 2D 플롯도 같은 성격 (전부 QOpenGLWidget)
   │   → 논리 크기가 같아도 면적 4배면 FBO 도 4배. GPU 메모리 재할당이 여기서 발생
   │   진짜 네이티브 HWND 는 m_cadContainer / m_occtViewWidget (:1669-1672) 한 계통뿐
   │   → Per-Monitor V1 의 "자식 HWND 로 DPI 미전파" 는 이쪽에만 해당
   ▼

[3] 레이아웃 폭풍
   │   1. resizeEvent → applyDockResize + applyInnerModuleRenderSplit (L2-1)
   │   2. 중첩 QMainWindow 이중 패스 (L1-1) — 한 번에 수렴하지 않음
   │   3. QStackedWidget 의 모든 페이지가 계산 대상 (L1-2)
   │      현재 보이지 않는 9개 모듈까지 minimumSize/sizeHint 재계산
   ▼

[4] 테이블 열 폭 전면 재계산
   │   폰트 메트릭이 바뀌었으므로 ResizeToContents 열 40여 곳이 무효화 (L3-9)
   │   각 열이 전체 행을 스캔 — 행이 많은 테이블에서 O(행 × 열)
   │   [3] 의 레이아웃 패스마다 반복
   ▼

[5] 응답 정지
       [2]~[4] 가 UI 스레드에서 직렬 수행된다
       이벤트 루프가 돌지 못해 창이 흰 화면으로 멈춘 것처럼 보인다
   ▼

[6] 복구 불가 상태로 착지
       창은 화면 밖까지 커져 있고, 아래 네 가지가 모두 막혀 있다
```

## 왜 복구할 수 없는가

크기가 커진 것 자체보다, **되돌릴 수단이 전부 막혀 있다는 점**이 문제다.

| 통상적 복구 수단 | 차단 이유 |
|---|---|
| 창 가장자리를 끌어 축소 | `RESIZE_MARGIN = 8` 논리 px 인 가장자리가 화면 밖 (`DashMainWindow.h:287`) |
| 타이틀바의 최대화·복원 버튼 | 프레임리스 커스텀 타이틀바가 화면 밖으로 밀려남 |
| 타이틀바를 끌어 창 이동 | 위와 동일. 잡을 지점이 화면에 없음 |
| Windows 시스템 메뉴 (`Alt+Space` → 이동) | `Qt::FramelessWindowHint` 라 OS 가 시스템 메뉴를 제공하지 않음 |

여기에 창 크기를 화면 안으로 되돌리는 클램프가 어디에도 없다 — `availableGeometry()` 를 참조하는 코드가 **0건**이다 (L0-5, L0-6).

## 지금 당장 쓸 수 있는 회피책

**F11 을 누른다.** `m_fullscreenAction` (`DashMainWindow.cpp:172-179`) 이 `Qt::Key_F11` 에 바인딩되어 있고, 동작은 `isMaximized() ? showNormal() : showMaximized()` 다.

```cpp
connect(m_fullscreenAction, &QAction::triggered, this, [this]() {
    if (isMaximized()) showNormal(); else showMaximized();
    m_fullscreenAction->setChecked(isMaximized());
});
```

창이 화면 밖에 있어도 **키보드 포커스는 유지**되므로 단축키는 전달된다. `showMaximized()` 가 창을 현재 걸쳐 있는 화면의 작업 영역에 맞추므로 화면 안으로 돌아온다.

한계가 두 가지 있다. 어느 모니터로 최대화될지는 창이 어느 화면에 더 많이 걸쳐 있는지에 달려 예측하기 어렵고, 프리즈([5])가 끝난 뒤에야 키 입력이 처리된다.

## 이 발현에 대한 처방

세 단계로 나뉜다. 3부 로드맵 참조.

- **응급 (Stage 0)**: `moveEvent` / `resizeEvent` 에서 창 geometry 를 `availableGeometry()` 로 클램프한다. 창이 화면 밖으로 나가는 것 자체를 막으므로 복구 불가 상태가 성립하지 않는다. 수십 줄 규모이며 다른 변경과 독립적이다.
- **복구 경로 복원 (Stage 4)**: 위 표에서 막혀 있는 네 가지는 전부 `Qt::FramelessWindowHint` 가 OS 창 관리를 포기한 결과다. `Qt::Window` + `WM_NCCALCSIZE` 로 전환하면 시스템 메뉴·스냅·OS 리사이즈가 되살아나 **창이 커지더라도 복구할 수단이 남는다.** 원칙 4 참조.
- **원인 축소 (Stage 3)**: `PassThrough` 로 [1] 의 크기 폭증을 없앤다. DPR 이 1.0 → 1.5 로 완만히 변하면 [2]\~[4] 의 비용도 그만큼 줄어든다.

프리즈 자체를 완전히 없애려면 L1-1(중첩 QMainWindow)·L1-2(단일 스택)·L3-9(ResizeToContents)까지 손봐야 하지만, 응급 조치만으로도 "복구 불가" 라는 최악의 결과는 차단된다.

---

# 1부 — 준거: Qt 의 표준 크기 관리 패턴

Qt 위젯 애플리케이션에는 크기·배치에 관한 확립된 관용구가 있다. 아래 5개 원칙이 그 골자다.

## 원칙 1 — 크기는 레이아웃이 결정한다

위젯이 자기 크기를 직접 정하지 않는다. 위젯은 **의사만 표명**하고, 실제 크기는 부모 레이아웃이 계산한다.

| 표명 수단 | 의미 |
|---|---|
| `sizeHint()` | "이 정도가 적당하다" |
| `minimumSizeHint()` | "이보다 작으면 못 쓴다" |
| `QSizePolicy` | 남는 공간을 가져갈지(`Expanding`), 유지할지(`Preferred`), 고정할지(`Fixed`) |
| `setStretchFactor()` | 형제들과 공간을 나누는 비율 |

`setFixedSize()` / `resize()` / `setGeometry()` 를 직접 호출하는 것은 이 협상을 건너뛰는 행위다. 최상위 창의 초기 크기 지정 정도가 정당한 용례이고, 그 외에는 대개 레이아웃 설정 실패를 덮는 우회로다.

**핵심**: 비율로 공간을 나누고 싶다면 `resizeDocks()` 를 반복 호출하는 게 아니라 `setStretchFactor()` 로 **한 번 선언**한다.

## 원칙 2 — 창·dock 상태 영속화는 전용 API 로

`QMainWindow` 는 dock 배치와 크기를 통째로 직렬화하는 표준 API 를 제공한다.

```cpp
// 종료 시
settings.setValue("MainWindow/geometry", saveGeometry());
settings.setValue("MainWindow/state",    saveState());

// 시작 시 — 모든 dock 을 생성·추가한 뒤에 호출
restoreGeometry(settings.value("MainWindow/geometry").toByteArray());
restoreState   (settings.value("MainWindow/state").toByteArray());
```

`saveGeometry()` 는 **어느 화면에 있었는지까지 기록**하며, `restoreGeometry()` 는 복원 시 그 화면이 사라졌으면 알아서 보정한다. 멀티디스플레이 대응이 공짜로 따라온다.

이 API 를 쓰면 "로그 dock 높이 비율" 같은 값을 수동 추적할 이유가 사라진다.

## 원칙 3 — High-DPI 는 정책 선언 1회, 이후 코드는 논리 단위만

애플리케이션 시작 시 정책을 선언하고, 그 뒤로는 **모든 코드가 논리 픽셀만 다룬다.**

```cpp
QGuiApplication::setHighDpiScaleFactorRoundingPolicy(
    Qt::HighDpiScaleFactorRoundingPolicy::PassThrough);
QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
QCoreApplication::setAttribute(Qt::AA_UseHighDpiPixmaps);
```

물리 픽셀이 필요한 곳은 OpenGL 뷰포트 계산 정도이며, 거기서만 `devicePixelRatioF()` 를 곱한다.

전역 배율 조정이 필요하면 `QT_SCALE_FACTOR`(화면별 DPI 와 곱해지는 전역 상수)가 아니라 **애플리케이션 폰트 크기**를 조정한다. Qt 위젯의 기본 메트릭은 폰트에 연동되어 있으므로 폰트만 키워도 레이아웃 전체가 따라 커진다.

다만 이 마지막 문장은 크기 제약이 폰트에 연동돼 있을 때만 성립한다. QSS 와 `.ui` 에 px 고정이 많이 남아 있으면 폰트만 키웠을 때 일부만 따라 커져 오히려 어긋난다 (L0-4).

## 원칙 4 — 창 프레임 관리는 OS 에 위임한다

프레임리스 창을 만들더라도 이동·리사이즈를 직접 계산하지 않는다. 위임 경로가 두 갈래이며, **되찾을 수 있는 범위가 다르다.**

### 경로 A — Qt 레벨 위임 (`startSystemMove` / `startSystemResize`)

```cpp
// 타이틀바 mousePressEvent 안에서
window()->windowHandle()->startSystemMove();
// 가장자리 리사이즈
window()->windowHandle()->startSystemResize(Qt::LeftEdge | Qt::TopEdge);
```

Qt 5.15 의 크로스 플랫폼 API 로, 드래그를 OS 의 이동·리사이즈 모달 루프에 넘긴다. 직접 계산이 사라지므로 낡은 오프셋과 좌표계 전환 문제가 없어지고, 드래그 중 화면 경계 처리도 OS 가 맡는다.

**되찾지 못하는 것이 있다.** `Qt::FramelessWindowHint` 는 Win32 창 스타일에서 `WS_CAPTION`·`WS_THICKFRAME`·`WS_SYSMENU` 를 걷어낸다. Windows 의 창 관리 기능은 이 스타일 비트를 보고 동작하므로, 드래그 구현을 고쳐도 아래는 여전히 없다.

| 기능 | 요구 조건 |
|---|---|
| Win+방향키 스냅 | `WS_THICKFRAME` + `WS_MAXIMIZEBOX` |
| 화면 가장자리로 끌어 스냅 | 동일 |
| Windows 11 스냅 레이아웃 | 비클라이언트 영역 + `HTMAXBUTTON` 히트테스트 |
| `Alt+Space` 시스템 메뉴 | `WS_SYSMENU` |
| 작업표시줄 썸네일 우클릭의 이동·크기 조절 | `WS_SYSMENU` |

즉 경로 A 는 **구현 버그를 없애는 데 그치고, OS 창 관리 자체는 돌아오지 않는다.** 0부의 복구 수단 표에서 막혀 있던 항목들이 그대로 막혀 있다.

### 경로 B — Win32 레벨 위임 (`WM_NCCALCSIZE` 로 프레임 크기만 0 으로)

창은 보통의 최상위 창으로 두고, **비클라이언트 영역의 크기만** 없앤다.

```cpp
setWindowFlags(Qt::Window);        // FramelessWindowHint 대신 — 스타일 비트를 살려둔다
```

```cpp
// WM_NCCALCSIZE: "이 창 사각형에서 클라이언트 영역은 어디냐"
// 기본 처리기는 프레임과 캡션을 깎아낸다.
// 제안된 사각형을 그대로 두면 클라이언트 == 창 전체가 되어 프레임이 화면에서 사라진다.
if (msg->message == WM_NCCALCSIZE && msg->wParam == TRUE) {
    *result = 0;                   // rgrc[0] 을 건드리지 않음
    return true;
}
```

OS 입장에서 이 창은 **캡션과 리사이즈 테두리를 가진 정상 창**이다. 단지 그 프레임이 그려지지 않을 뿐이다. 스타일 비트가 남아 있으므로 위 표의 기능이 전부 살아 있고, DPI 전환 시에도 OS 가 정상 창으로서 프레임을 처리한다.

프레임이 보이지 않으니 OS 는 "이 지점이 캡션인지 테두리인지" 를 물어봐야 한다. 그 계약이 `WM_NCHITTEST` 다.

| 좌표 위치 | 반환값 | OS 가 대신 해주는 일 |
|---|---|---|
| 가장자리 8px | `HTLEFT` `HTTOP` `HTBOTTOMRIGHT` … | 리사이즈 모달 루프, 커서 모양, 경계 클램프 |
| 타이틀바 (빈 영역) | `HTCAPTION` | 드래그 이동, 더블클릭 최대화, 우클릭 시스템 메뉴, 가장자리 스냅 |
| 타이틀바 (메뉴·버튼) | `HTCLIENT` | — (클릭 이벤트가 위젯에 전달됨) |
| 그 외 전부 | `HTCLIENT` | — |

애플리케이션이 작성하는 코드는 **좌표를 영역 상수로 매핑하는 함수 하나**뿐이다. 이동·리사이즈 루프 자체는 한 줄도 쓰지 않는다.

### 두 경로의 선택

| | 경로 A (`startSystemMove`) | 경로 B (`WM_NCCALCSIZE`) |
|---|---|---|
| 드래그·리사이즈 구현 버그 | 해소 | 해소 |
| OS 스냅 / 시스템 메뉴 | ✗ | ✓ |
| 화면 밖 이탈 방지 | 드래그 중에만 | 항상 (OS 창 관리) |
| DPI 전환 시 프레임 | Qt 경유 | OS 가 정상 창으로 처리 |
| 플랫폼 | 크로스 플랫폼 | Windows 전용 (`#ifdef Q_OS_WIN`) |
| 추가 코드 | 호출 2곳 | 히트테스트 핸들러 (60줄 내외) |

이 프로젝트는 MSVC/Windows 전용 빌드이므로 경로 B 의 플랫폼 제약이 실질 비용이 되지 않는다. **0부의 복구 불가 상태가 "OS 창 관리 부재" 에서 비롯된 이상, 경로 B 가 증상에 직접 대응한다.** 사내 선례도 경로 B 로 수렴했다 (부록 참조).

## 원칙 5 — 오버레이는 부모의 `resizeEvent` 에서 재배치한다

레이아웃에 넣을 수 없는 떠 있는 위젯(플로팅 툴바 등)은 부모의 `resizeEvent`(또는 부모에 설치한 이벤트 필터)에서 **매번** 위치를 다시 계산한다. 최초 1회만 배치하면 부모가 줄어들 때 화면 밖으로 나간다.

## 현재 코드의 준수 현황

| 원칙 | 준수 | 근거 |
|---|:---:|---|
| 1. 레이아웃에 위임 | ✗ | `resizeDocks` 강제 호출, `setFixed*` 60여 곳 |
| 2. `saveState`/`restoreState` | ✗ | **호출 0건.** 대신 `m_logHeightRatio` 하나만 수동 추적하고 그마저 오작동 |
| 3. DPI 정책 선언 | ✗ | rounding policy 미설정, `QT_SCALE_FACTOR` 사용 |
| 4. OS 위임 | ✗ | `move()` / `setGeometry()` 로 직접 구현. `FramelessWindowHint` 라 스냅·시스템 메뉴도 부재 |
| 5. 오버레이 재배치 | △ | CAD 쪽은 매번, 렌더 쪽은 최초 1회만 — 비대칭 |

원칙 3의 `devicePixelRatioF()` 사용은 `DashAnalyzerHelpers.cpp:186,202` 에서 올바르게 되어 있다. 코드베이스에서 크기 처리가 정석대로 된 몇 안 되는 지점이다.

---

# 2부 — 문제: 근본에서 지엽으로

| 계층 | 성격 | 건수 |
|---|---|---|
| **L0** | 설계 원칙 이탈 — 다른 모든 문제의 뿌리 | 6 |
| **L1** | 구조적 선택 — L0 를 고쳐도 남는 구조 문제 | 4 |
| **L2** | 메커니즘 오용 — 구조는 두고 고칠 수 있는 것 | 7 |
| **L3** | 국소 결함 — 개별 수정 가능 | 8 |
| **R** | 렌더링 스택 접점 — DPR 이 1 이 아닐 때만 드러남 (2부 뒤 별도 절) | 5 |

---

## L0 — 설계 원칙 이탈 (근본)

### L0-1. 크기 결정 권한이 명령형 코드에 분산됨

**문제.** 크기를 강제하는 코드가 서로 다른 계층에 흩어져 같은 위젯을 두고 경쟁한다.

| 주체 | 위치 | 강제 대상 |
|---|---|---|
| `resizeEvent` 훅 | `DashMainWindow.cpp:3603-3608` | 우측 dock, 모듈/렌더 분할 |
| 트리 선택 핸들러 | `:568-575` | 위와 동일 |
| 타이머 콜백 4개 | `:1625, 1630, 2386, 3619` | 로그 dock, 모듈/렌더 분할 |
| `setFixed*` 하드코딩 | 60여 곳 | 개별 위젯 |
| `.ui` 기본 geometry | 13개 파일 | 모듈 위젯 전체 |
| QSS 크기 제약 | 52곳 | 스타일 대상 전체 |

어느 것이 마지막에 실행되느냐로 최종 크기가 정해진다. **"같은 조작인데 결과가 다르다" 의 근본 원인**이며, L2 의 개별 증상 대부분이 여기서 파생된다.

**해법.** 강제 지점을 없애고 선언으로 대체한다.

```cpp
// 현재: 매 resize 마다 1:4 를 재계산해 강제
m_innerMainWindow->resizeDocks({m_moduleDock, m_renderDock}, {moduleW, renderW}, Qt::Horizontal);

// 목표: 최초 1회 선언 — 이후 Qt 가 유지
m_moduleDock->widget()->setSizePolicy(QSizePolicy::Preferred,  QSizePolicy::Expanding);
m_renderDock->widget()->setSizePolicy(QSizePolicy::Expanding,  QSizePolicy::Expanding);
```

`resizeDocks()` 는 초기 배치 1회로 한정하고, 이후에는 호출하지 않는다.

### L0-2. 창·dock 상태 영속화 부재

**문제.** `saveState()` / `restoreState()` / `saveGeometry()` / `restoreGeometry()` 호출이 **코드베이스 전체에 0건**이다. 앱을 껐다 켜면 레이아웃이 초기화되고, 실행 중에도 사용자 조정값을 보존할 수단이 없다.

유일한 대체 수단이 `m_logHeightRatio` (`DashMainWindow.h:295`) 하나인데, 그것을 갱신하는 경로마저 잘못 연결되어 있다 (L2-4).

**해법.** 원칙 2의 표준 API 를 도입한다. `closeEvent` 에서 저장하고, dock 생성이 모두 끝난 뒤 복원한다.

```cpp
void DashMainWindow::closeEvent(QCloseEvent* e) {
    QSettings s("NohLab", "DashOptiAnalyzer");
    s.setValue("MainWindow/geometry", saveGeometry());
    s.setValue("MainWindow/state",    saveState());
    QMainWindow::closeEvent(e);
}
```

중첩 `QMainWindow` 를 쓰므로 inner 쪽도 별도 키로 저장해야 한다 (L1-1 참조). `restoreState()` 는 `objectName` 이 설정된 dock 만 복원하므로, 모든 `QDockWidget` 에 `setObjectName()` 을 부여하는 선행 작업이 필요하다 — 현재 지정되어 있지 않다.

`saveState(version)` 의 버전 인자를 반드시 쓴다. dock 구성이 바뀌면 번호를 올려야 하고, `restoreState()` 가 `false` 를 반환하면 기본 배치로 폴백한다. 저장된 상태가 남아 있는 채로 dock 구성이 바뀌면 레이아웃이 깨진다 (사내 선례에서 실제로 발생, 부록 참조).

**주의 — 이 항목만 단독 적용하면 효과가 없다.** 복원 직후에 `resizeDocks()` 강제 재분배(L2-1)가 남아 있으면 복원된 크기가 같은 프레임에서 덮어써진다. 사내 선례가 정확히 이 상태다 (부록 "베끼면 안 되는 것 a"). L0-2 는 L2-1 제거와 **함께** 적용해야 한다.

두 가지를 같이 적용하면 L2-1, L2-2, L2-4, L2-5 의 존재 이유가 대부분 사라진다.

### L0-3. High-DPI 정책 미선언

**문제.** `main.cpp:22` 에서 `AA_EnableHighDpiScaling` 만 켜고 rounding policy 를 지정하지 않았다. **Qt 5.15 의 기본값은 `Round`** 다 (Qt 6 부터 `PassThrough` 로 변경됨).

| Windows 표시 배율 | Round 적용 후 DPR | 오차 |
|---|---|---|
| 100% | 1.0 | — |
| 125% | 1.0 | -20% |
| **150%** | **2.0** | **+33%** |
| 175% | 2.0 | +14% |

Qt 는 화면이 바뀌어도 창의 **논리** 크기를 유지하려 한다. 100% → 150% 이동 시 DPR 이 1 에서 2로 뛰므로 물리 크기가 그대로 2배가 된다.

부수적으로, Qt 5.15 windows 플러그인은 `PROCESS_PER_MONITOR_DPI_AWARE`(V1)만 설정한다. V2 와 달리 OS 가 자식 HWND 로 DPI 변경을 전파하지 않아 `QVTKOpenGLNativeWidget` 이 영향을 받는다. 실행 파일 manifest 에도 DPI 선언이 없다 (`resources/resources.rc` 는 아이콘 1줄뿐).

**해법.** 원칙 3의 3줄. `QApplication` 생성 전이어야 하며, 현재 22행 위치가 조건을 만족한다.

API 는 이 프로젝트가 쓰는 Qt 트리에 존재한다 — `external/Qt-5.15.16/include/QtGui/qguiapplication.h:159`. 사내 선례가 "이 빌드에 API 가 없다" 고 기록해 두었으나 함수명 오기였다 (부록 "사실 정정" 참조).

### L0-4. UI 배율을 전역 곱연산으로 구현

**문제.** View 메뉴의 UI Scale (`DashMainWindow.cpp:189-209`) 이 `QT_SCALE_FACTOR` 를 설정한다.

```cpp
// main.cpp:24-29
double scaleFactor = settings.value("UI/scaleFactor", 1.0).toDouble();
if (!qFuzzyCompare(scaleFactor, 1.0))
    qputenv("QT_SCALE_FACTOR", QByteArray::number(scaleFactor, 'f', 2));
```

이 환경변수는 화면별 DPI 와 **곱해지는 전역 상수**라 화면마다 다른 값을 줄 수 없다.

| 상황 | 실효 배율 |
|---|---|
| UI Scale 130% + 150% 모니터 (Round 후 2.0) | 1.3 × 2.0 = **2.6** |
| 같은 창을 100% 모니터로 이동 | 1.3 × 1.0 = **1.3** |

L0-3 의 격차를 배수로 키운다. 재시작을 요구하는 것(`:206-207`)도 이 방식의 제약이다.

**해법 — 세 선택지.** 이 항목은 단독으로 치명 발현에 기여하지 않으므로 우선순위가 낮다.

| 선택지 | 내용 | 비용 | 평가 |
|---|---|---|---|
| **a. 기능 제거** | UI Scale 메뉴를 없애고 OS 표시 배율에 위임 | 메뉴 1개 삭제 | **가장 단순.** Windows 표시 배율이 같은 일을 하며 화면별로 다르게 적용된다 |
| b. 현행 유지 | `QT_SCALE_FACTOR` 를 두되 한계를 명시 | 0 | L0-3 만 고쳐도 150% 모니터의 실효 배율이 2.6 → 1.95 로, 화면 간 격차가 2.0배 → 1.5배로 완화된다 |
| c. 폰트 전환 | `app.setFont()` 포인트 크기에 배율을 곱함 | QSS 52곳 px→em 선행 (L3-8) | 재시작 없이 반영되나, 선행 작업이 이 문서 전체에서 가장 큰 기계적 변경이다 |

```cpp
// c 의 실제 변경은 한 줄이다 — 비용은 전부 선행 QSS 작업에 있다
app.setFont(QFont("Pretendard", qRound(9 * scaleFactor)));
```

**권장은 a**, 차선은 b 다. UI Scale 이 실제로 쓰이는지부터 확인한다. c 는 QSS px→em 전환을 별도 과제로 끝낸 뒤에나 의미가 있다 — 폰트만 키우고 QSS 가 남아 있으면 위젯 일부만 커져 지금보다 나빠진다.

### L0-5. 프레임리스 창의 이동·리사이즈 자체 구현

**문제.** `DashMainWindow.cpp:122` 의 `Qt::FramelessWindowHint` 와 함께 창 조작을 직접 구현했다.

*드래그* (`DashTitleBar.cpp:91,104`)

```cpp
m_dragPosition = event->globalPos() - m_mainWindow->frameGeometry().topLeft();  // press 시점 캡처
m_mainWindow->move(event->globalPos() - m_dragPosition);                        // move 시점 사용
```

드래그 중 DPI 가 바뀌면 Qt 가 창 크기를 재조정하는데, 코드는 **T0 시점의 낡은 오프셋으로 계속 `move()`** 한다. 창이 커서에서 이탈해 점프한다.

*리사이즈* (`DashMainWindow.cpp:2874-2905`)

`m_originalGeometry` + `globalPos` 델타 방식이라 화면 경계를 넘으면 좌표계 스케일이 바뀌어 델타가 무의미해진다. `availableGeometry()` 클램프도 없어 창이 화면 밖으로 나갈 수 있다.

**해법.** 원칙 4의 두 경로 중 하나로 교체한다. 어느 쪽이든 `getResizeEdge()` / `handleResize()` / `getCursorForEdge()` 와 `m_isResizing` / `m_resizeEdge` / `m_originalGeometry` / `m_resizeStartPos` 상태를 전부 제거할 수 있다.

*경로 A — 최소 변경*

```cpp
void DashTitleBar::mousePressEvent(QMouseEvent* e) {
    if (e->button() == Qt::LeftButton && !m_mainWindow->isMaximized()) {
        if (auto* h = m_mainWindow->windowHandle()) { h->startSystemMove(); e->accept(); }
    }
}
```

드래그 버그는 사라지지만 창 스타일은 그대로라 스냅·시스템 메뉴는 돌아오지 않는다. **0부의 복구 수단 표 4행 중 3행이 여전히 막혀 있다.**

*경로 B — 권장*

`:122` 를 `setWindowFlags(Qt::Window)` 로 바꾸고 `nativeEvent()` 에서 `WM_NCCALCSIZE` + `WM_NCHITTEST` 를 처리한다. 커스텀 타이틀바 외형은 그대로 유지되면서 OS 창 관리가 전부 복원된다. 검증된 참조 구현이 사내에 있다 (부록 "채택할 만한 것 1").

경로 B 를 택하면 `DashTitleBar` 의 마우스 핸들러 4개(`mousePressEvent` / `mouseMoveEvent` / `mouseReleaseEvent` / `mouseDoubleClickEvent`)와 `m_isDragging` / `m_dragPosition` 도 함께 사라진다. 남는 것은 "이 좌표가 클릭 가능한 위젯 위인가" 를 판정하는 함수 하나다.

**선행 확인 사항**: 현재 `DashMainWindow.cpp:1764-1768` 이 창에 `QGraphicsDropShadowEffect` 를 걸고 있다. 경로 B 로 가면 창이 불투명 전체 사각형이 되므로 Qt 측 그림자와 충돌한다. DWM 이 정상 창에 그림자를 그려주므로 Qt 그림자를 제거하는 방향이 맞지만, 실기 확인이 필요하다.

### L0-6. 창을 화면 안으로 되돌리는 경로가 없음

**문제.** 창 geometry 를 화면 작업 영역으로 제한하는 코드가 전혀 없다. `availableGeometry()` 참조가 **코드베이스 전체에 0건**이다.

정상적인 창은 이것이 없어도 OS 가 최소한의 보호를 해준다 — 타이틀바를 화면 밖으로 완전히 끌어낼 수 없고, 시스템 메뉴로 언제든 이동/크기 조절을 호출할 수 있다. `Qt::FramelessWindowHint` 는 그 보호를 전부 포기한다.

따라서 프레임리스 창에서는 **클램프가 선택이 아니라 필수**다. 0부의 복구 불가 상태는 이 부재의 직접적 결과다.

**해법.** 두 지점에서 클램프한다.

```cpp
void DashMainWindow::clampToScreen()
{
    QScreen* sc = windowHandle() ? windowHandle()->screen() : qApp->primaryScreen();
    if (!sc) return;
    const QRect a = sc->availableGeometry();

    QRect g = frameGeometry();
    g.setSize(g.size().boundedTo(a.size()));          // 화면보다 커지지 않게
    if (g.right()  > a.right())  g.moveRight(a.right());
    if (g.bottom() > a.bottom()) g.moveBottom(a.bottom());
    if (g.left()   < a.left())   g.moveLeft(a.left());
    if (g.top()    < a.top())    g.moveTop(a.top());  // 타이틀바가 화면 위로 못 나가게

    if (g != frameGeometry()) setGeometry(g);
}
```

`moveEvent` / `resizeEvent` 에서 호출하되, `setGeometry` 가 다시 이벤트를 부르므로 **재진입 가드**가 필요하다.

```cpp
if (m_inClamp) return;
QScopedValueRollback<bool> guard(m_inClamp, true);
clampToScreen();
```

L0-5 의 경로 B 로 전환하면 OS 가 클램프를 대신 처리하므로 이 코드도 제거할 수 있다. 다만 **응급 조치로는 이쪽이 훨씬 작고 독립적**이라 먼저 넣을 값어치가 있다.

경로 B 에서 최대화 시 창이 화면을 넘치는 문제는 별도로 다뤄야 한다. `WS_THICKFRAME` 창을 최대화하면 Windows 는 프레임 두께만큼 부풀린 크기로 잡는데, 비클라이언트 인셋을 0 으로 만들었으니 그 두께가 그대로 넘침이 된다. **정공법은 넘친 두께만큼 안쪽으로 깎는 것**이다.

```cpp
// WM_NCCALCSIZE, 최대화 상태
const UINT dpi = GetDpiForWindow(msg->hwnd);
const int cx = GetSystemMetricsForDpi(SM_CXSIZEFRAME, dpi)
             + GetSystemMetricsForDpi(SM_CXPADDEDBORDER, dpi);
const int cy = GetSystemMetricsForDpi(SM_CYSIZEFRAME, dpi)
             + GetSystemMetricsForDpi(SM_CXPADDEDBORDER, dpi);
InflateRect(&params->rgrc[0], -cx, -cy);
```

작업 영역(`rcWork`)으로 통째 교체하는 방식은 자동 숨김 작업표시줄과 모니터 오판 문제를 만든다 — 부록 "베끼면 안 되는 것 c" 참조.

---

## L1 — 구조적 선택

L0 를 고쳐도 남는다. 개선하려면 구조를 손대야 한다.

### L1-1. 중첩 QMainWindow 의 이중 레이아웃 패스

**문제.** outer 의 `centralWidget` 이 또 다른 `QMainWindow` 다 (`DashMainWindow.cpp:277-280`).

```
Outer QMainWindow (DashMainWindow)
   │   menuWidget      = DashTitleBar
   │   RightDockArea   = m_rightDock ── QStackedWidget (모듈 10개)
   │   BottomDockArea  = m_logDock
   │   setCorner(BottomLeft → Bottom), setCorner(BottomRight → Right)
   ▼

centralWidget = Inner QMainWindow (m_innerMainWindow)
   │   setWindowFlags(Qt::Widget), setDockNestingEnabled(true)
   │   LeftDockArea  = m_leftDock / m_modelingDock / m_moduleDock (수직 3분할)
   │   RightDockArea = m_renderDock + csv/plot/cad (탭 중첩)
   ▼

[귀결] inner 폭은 outer 레이아웃이 확정된 뒤에야 정해지는데
       resizeEvent 는 두 계층의 resizeDocks 를 같은 이벤트에서 연속 호출한다
       → 한 번의 패스로 수렴하지 않는다
```

`setDockNestingEnabled(true)` (`:279`) 가 inner 계산을 더 복잡하게 만든다.

**해법.** 세 가지 선택지가 있다.

| 방식 | 내용 | 평가 |
|---|---|---|
| A. 단일 QMainWindow | dock area 와 `setCorner` 조합으로 같은 배치를 재현 | 가장 정석. 구조 단순화 폭이 큼 |
| B. inner 를 `QSplitter` 로 | 좌측 트리 / 렌더를 splitter 로 대체 — dock 기능 포기 | 사용자가 렌더 영역을 떼어낼 필요가 없다면 유효 |
| C. 유지 + 상태 분리 저장 | inner 도 `saveState()` 대상에 포함 | 최소 변경. 근본 해결은 아님 |

현재 dock 배치가 outer/inner 로 갈린 이유는 **로그 dock 이 우측 dock 아래로 침범하지 않게** 하려는 것으로 보이는데, 이는 A 의 `setCorner` 로 단일 창에서도 표현 가능하다. 실제로 `:1598-1599` 에 이미 `setCorner` 를 쓰고 있다.

**기본 선택은 C 다.** A 는 정석이지만 dock 10여 개의 배치를 전부 다시 맞춰야 하고 회귀 범위가 넓다. L0-1·L2-1 을 걷어내면 이중 패스가 매 resize 마다 돌지 않게 되므로, 그 뒤에도 프로파일링에서 이중 패스가 지배 요인으로 남을 때에만 A 에 착수한다.

### L1-2. QStackedWidget 단일 스택의 최소 크기 전파

**문제.** 모듈 위젯 10개가 하나의 `QStackedWidget` 에 들어간다 (`DashMainWindow.cpp:433-479`).

`QStackedLayout::minimumSize()` 와 `sizeHint()` 는 **현재 페이지가 아니라 모든 페이지의 최대값**을 반환한다. 따라서

- 가장 큰 위젯 하나가 우측 dock 전체의 최소 폭을 결정한다
- 개별 모듈의 하드코딩 최소 크기(`DashGeometryParameterWidget.cpp:194` `setMinimumSize(300,30)`, `:197` `setMinimumSize(200,40)`)가 **모든 모듈에 전파**된다
- 어느 한 위젯이 지연 로딩으로 커지면 그 시점에 dock 폭이 튄다

**해법.** 두 갈래.

- 각 모듈 위젯을 `QScrollArea` 로 감싸 `setWidgetResizable(true)` 를 준다. 최소 크기 요구가 스크롤로 흡수되어 전파가 끊긴다.
- 또는 모듈 전환 시 현재 페이지 외의 `sizePolicy` 를 `Ignored` 로 낮춘다.

전자가 표준적이고, L3-1 의 하드코딩 최소 크기를 당장 걷어내지 않아도 된다는 이점이 있다. 모듈을 스택에 추가하는 지점이 한 곳(`DashMainWindow.cpp:433-479`)이므로 래핑도 그 루프 안에서 끝난다 — 위젯 10개를 각각 고치는 작업이 아니다.

### L1-3. `.ui` 기본 geometry 가 런타임 기준 크기로 승격

**문제.** `ui->setupUi(this)` 는 `.ui` 최상위의 `geometry` 값으로 위젯을 `resize()` 한다. Qt Designer 의 미리보기 크기가 그대로 런타임 기준이 된다.

| `.ui` 파일 | 기본 크기 |
|---|---|
| `DashAnalysisLauncherWidget.ui` | **700×800** |
| `DashGeometryParameterWidget.ui` | 620×760 |
| `DashModelBuilderWidget.ui` / `MCU` | 620×760 |
| `DashModelRunnerWidget.ui` | 620×760 |
| `DashOptimizerWidget.ui` | 620×760 |
| `DashGeometryParameterCADWidget.ui` | 600×700 |
| `DashConditionParameterizationWidget.ui` | 560×600 |
| `DashDataProcessorWidget.ui` | 520×680 |

L1-2 와 결합하면 **700×800 이 우측 dock 의 사실상 기준 크기**가 된다. `RIGHT_DOCK_MIN = 550` (`DashMainWindow.h:290`) 과 무관하게 작동하는 또 하나의 크기 결정자다.

**해법.** `.ui` 의 최상위 `geometry` 는 레이아웃이 제대로 걸려 있으면 런타임에 영향이 없어야 정상이다. 각 `.ui` 의 최상위에 레이아웃이 설정되어 있는지, 자식들의 `sizePolicy` 가 `Expanding` 으로 열려 있는지 점검한다. L1-2 의 `QScrollArea` 도입 시 함께 해소된다.

### L1-4. inner 폭이 outer dock 가시성에 종속

**문제.**

```cpp
// DashMainWindow.cpp:525-538
const int w = m_innerMainWindow->width();          // ← rightDock 열림/닫힘에 따라 변함
int moduleW = (w * INNER_MODULE_WEIGHT) / totalW;  // w × 1/5
m_innerMainWindow->resizeDocks({m_moduleDock, m_renderDock}, {moduleW, renderW}, Qt::Horizontal);
```

절대폭이 아니라 비율로 계산하므로 rightDock 을 토글할 때마다 왼쪽 모듈 트리 폭이 다른 값이 된다. L2-2 와 결합하면 트리에서 부모↔자식을 오갈 때마다 왼쪽 폭이 두 값 사이를 왕복한다.

**해법.** L0-1 의 `setStretchFactor` 선언으로 대체하면 소멸한다. 좌측 트리는 `Preferred`, 렌더는 `Expanding` 으로 두면 rightDock 개폐 시 렌더 영역만 신축한다 — 이것이 대개 사용자가 기대하는 동작이다.

---

## L2 — 메커니즘 오용

구조를 두고도 고칠 수 있다.

### L2-1. `resizeEvent` 마다 무조건 강제 재분배

**문제.**

```cpp
// DashMainWindow.cpp:3603-3608
void DashMainWindow::resizeEvent(QResizeEvent* event)
{
    QMainWindow::resizeEvent(event);
    applyDockResize();               // 우측 dock 폭 강제
    applyInnerModuleRenderSplit();   // 모듈/렌더를 1:4 로 강제
}
```

창 크기가 1px 만 변해도 실행된다. **사용자가 조정해 둔 dock 폭이 다음 resize 한 번에 전부 원복된다.** 창 리사이즈·최대화·복원·DPI 전환이 모두 이 경로로 들어온다.

**해법.** L0-1 적용 후 두 호출을 제거한다. 과도기적으로는 사용자 조정 여부를 플래그로 추적해 조정 후에는 강제하지 않는다.

### L2-2. 트리 항목 선택마다 dock 재계산

**문제.**

```cpp
// DashMainWindow.cpp:568-575
if (current.parent().isValid()) { handleSubItemSelection(current); showRightDock(); }
else                            { hideRightDock(); }
```

두 경로 모두 `applyInnerModuleRenderSplit()` 을 호출하므로 트리를 클릭할 때마다 왼쪽 트리 폭이 1/5 로 리셋된다. `showRightDock()` 은 early return 이 있지만(`:542`), `hideRightDock()` 은 조건 없이 매번 실행된다(`:549-553`).

**해법.** 두 함수에서 `applyInnerModuleRenderSplit()` 호출을 제거한다. 우측 dock 가시성은 왼쪽 트리 폭과 무관해야 한다. `hideRightDock()` 에도 대칭인 early return 을 넣는다.

### L2-3. `resizeDocks` 를 레이아웃 활성화 전에 호출

**문제.**

```cpp
// DashMainWindow.cpp:540-547
m_rightDock->setVisible(true);
this->resizeDocks({m_rightDock}, {rightWidth}, Qt::Horizontal);   // ← 즉시
```

Qt 문서상 `resizeDocks` 는 **대상 dock 이 visible 이고 레이아웃이 activate 된 뒤**에만 반영된다. `setVisible(true)` 직후에는 레이아웃 갱신이 큐에 들어간 상태라 적용될 수도, 무시될 수도 있다. 무시되면 L1-2 의 stacked widget 최대값이 폭을 결정한다.

**"같은 조작인데 결과가 다르다" 의 직접적 발현 지점**이다.

**해법.** 근본적으로는 L0-1 로 제거하고, **폭 제약은 `setMinimumWidth()` 로 옮긴다.**

사내 선례가 이 지점을 실기로 확증했다.

> `resizeDocks()` 는 서로 다른 dock area 에 있는 도크들 사이에서 비신뢰적으로 동작. 2-call 패턴이 원래 설계였으나 right dock 의 동적 크기 조절에는 효과 없음. **`setMinimumWidth()` 가 유일하게 신뢰 가능한 너비 제약 수단.**
> — `DashOpti_Analyzer` `docs/tickets/032-ui-spacing-and-quit-menu.md:85`

즉 "레이아웃 활성화 후에 호출하면 된다" 는 부분적 해법이다. 서로 다른 dock area 간에는 시점을 맞춰도 반영되지 않는 경우가 있다. `RIGHT_DOCK_MIN` 을 `m_rightDock->setMinimumWidth()` 로 선언하고 `resizeDocks()` 호출 자체를 없애는 쪽이 확실하다.

그래도 `resizeDocks()` 를 남겨야 한다면 다음 이벤트 루프 턴으로 미룬다.

```cpp
QTimer::singleShot(0, this, [this, rightWidth] {
    resizeDocks({m_rightDock}, {rightWidth}, Qt::Horizontal);
});
```

`0` 은 L2-5 의 임의 지연과 달리 "현재 이벤트 처리 완료 직후" 를 보장한다.

### L2-4. splitter 연결이 엉뚱한 대상에 걸림

**문제.**

```cpp
// DashMainWindow.cpp:1630-1643
QTimer::singleShot(200, this, [this]() {
    QList<QSplitter*> splitters = this->findChildren<QSplitter*>();
    for (QSplitter* splitter : splitters) {
        if (splitter->orientation() == Qt::Vertical) {
            connect(splitter, &QSplitter::splitterMoved, this, [this]() {
                m_logHeightRatio = (double)m_logDock->height() / this->height();
                m_logHeightRatio = qBound(0.05, m_logHeightRatio, 0.5);
            });
            break;      // ← 첫 번째 하나만
        }
    }
});
```

**`QMainWindow` 의 dock 경계는 `QSplitter` 가 아니다.** `QMainWindowLayout` 내부의 separator 로 구현되어 `findChildren<QSplitter*>()` 에 잡히지 않는다. 실제로 잡히는 것은 모듈 위젯 내부의 splitter 다.

| 후보 | 위치 |
|---|---|
| morphing 탭 splitter | `DashGeometryParameterWidget.cpp:699`, `:893` |
| 플롯 축/스타일 splitter (9개) | `DashPlotWidgetFactory.cpp:219, 417, 554, 693, 865, 1177, 1371, 1499, 1693` |
| CAD splitter | `DashGeometryParameterCADWidget.cpp:170` |

결과가 양방향으로 잘못된다.

- 로그 dock 경계를 드래그해도 `m_logHeightRatio` 가 저장되지 않는다
- **무관한 플롯 splitter 를 움직이면 로그 dock 높이 비율이 갱신된다** — 모듈 안에서 축 설정을 조정했을 뿐인데 하단 로그 창 높이가 바뀐다

`break` 때문에 어떤 splitter 가 잡히는지는 위젯 생성 순서에 의존하며, 200ms 시점에 미생성인 것은 후보에서 빠진다.

**해법.** 이 블록을 삭제한다. 의도한 동작을 전혀 하지 않으면서 부작용만 만든다. dock 크기 보존은 L0-2 의 `saveState()` 가 담당한다.

### L2-5. `QTimer::singleShot` 초기화 레이스

**문제.** 임의 지연값에 순서를 의존한다.

| 위치 | 지연 | 내용 |
|---|---|---|
| `DashMainWindow.cpp:1625` | 100ms | `adjustLogDockHeight()` + `applyInnerModuleRenderSplit()` |
| `:1630` | 200ms | splitter connect (L2-4) |
| `:2386` | 50ms | `adjustLogDockHeight()` |
| `:3619` | 50ms | `resetLayout()` 내 재분배 |

머신 성능과 프로젝트 로딩 시간에 따라 결과가 달라진다. `adjustLogDockHeight()` 에는 매직 폴백도 있다.

```cpp
// DashMainWindow.cpp:3594-3598
int totalHeight = this->height();
if (totalHeight < 100) totalHeight = 800;     // 레이아웃 전이면 800 가정
int logHeight = totalHeight * m_logHeightRatio;
int mainHeight = totalHeight - logHeight;     // ← 계산만 하고 미사용 (dead code)
```

레이아웃 전에 호출되면 실제 창 높이와 무관한 800 기준으로 로그 dock 높이가 정해진다.

**해법.** L0-2 도입 후 이 타이머들은 불필요해진다. 남는 초기 배치는 `showEvent()` 의 최초 1회 처리로 옮긴다 — 그 시점에는 레이아웃이 이미 확정되어 있어 매직 폴백이 필요 없다.

### L2-6. DPI 변경 알림을 수신하는 코드 없음

**문제.** `QWindow::screenChanged` / `QScreen::logicalDotsPerInchChanged` 연결이 **0건**이다. `changeEvent` (`DashMainWindow.cpp:3517-3528`) 는 `WindowStateChange` 만 처리하고 `QEvent::ScreenChangeInternal` 을 무시한다. 화면이 바뀌어도 재계산되는 것이 없다.

**해법.** L0-3 의 `PassThrough` 를 적용하면 대부분 Qt 가 알아서 처리한다. 명시 대응이 필요한 것은 L3-2 의 폰트 기반 고정 크기 재계산 정도다.

```cpp
connect(windowHandle(), &QWindow::screenChanged, this, [this](QScreen*) {
    /* 폰트 메트릭 의존 고정 크기 재계산 */
});
```

`windowHandle()` 은 `show()` 이후에만 유효하므로 `showEvent()` 에서 연결한다.

### L2-7. 초기 크기가 주모니터 기준

**문제.**

```cpp
// main.cpp:53, 71, 75-79
QScreen* screen = QApplication::primaryScreen();
QRect screenGeometry = screen->geometry();       // availableGeometry() 아님
mainWindow->resize(int(screenGeometry.width() * 0.80), int(screenGeometry.height() * 0.80));
mainWindow->show();                              // resize 가 show 보다 먼저
```

- `geometry()` 는 작업표시줄을 포함한다
- 항상 주모니터 기준이라 앱이 보조 모니터에 뜨면 무관한 크기가 된다
- `show()` 전에 크기를 정하므로 화면 배정 후 재조정이 한 번 더 발생한다

**해법.** L0-2 의 `restoreGeometry()` 가 이 코드를 대체한다. 저장된 상태가 없을 때만 폴백으로 크기를 계산하되, `availableGeometry()` 를 쓴다.

```cpp
if (!mainWindow->restoreGeometry(s.value("MainWindow/geometry").toByteArray())) {
    const QRect a = screen->availableGeometry();
    mainWindow->resize(a.width() * 0.8, a.height() * 0.8);
}
```

---

## L3 — 국소 결함

개별로 고칠 수 있다. 다만 L0-1 이 남아 있으면 재발한다.

### L3-1. `setFixed*` 하드코딩 60여 곳

**문제.** `setFixedSize` / `setFixedWidth` / `setFixedHeight` 가 60여 곳에 있다. 논리 px 이므로 Qt 스케일링 자체는 받지만, 레이아웃 협상을 차단해 L1-2 의 최소 크기 전파에 기여한다.

대표 사례: `DashMainWindow.cpp:1959` (`m_iconToolBar->setFixedWidth(48)`), `:1982` (`btn->setFixedSize(48,48)`), `DashTitleBar.cpp:15,26,47,53,58`.

**해법.** 아이콘 버튼처럼 실제로 정사각형이어야 하는 것은 유지하되, 폰트에 연동해야 할 것은 `QFontMetrics` 기반으로 바꾼다. 컨테이너 성격의 위젯에서는 `setFixed*` 대신 `sizePolicy` + `minimumSize` 조합을 쓴다.

### L3-2. 1회 계산 후 고정되는 폰트 의존 크기

**문제.** `fontMetrics()` 나 header height 로 계산한 값을 `setFixedHeight()` 로 굳힌다. 배율이나 폰트가 바뀌어도 재계산되지 않아 내용이 잘린다.

| 위치 | 계산 근거 |
|---|---|
| `ShortcutsDialog.cpp:31,38` | `rowCount * 26 + header height` |
| `DashMeshQualityDialog.cpp:58` | 행 높이 누적 합 |
| `DashResultsAnalyzerWidget.cpp:172` | `verticalHeader()->length() + ...` |
| `DashResultsAnalyzerWidget.cpp:185` | `fontMetrics().height() * 2` |
| `DashPlotWidgetFactory.cpp:94` | `tableContentHeight(table)` |
| `DashAnalyzerUtils.cpp:281` | 계산된 `idealH` |

**해법.** `changeEvent` 에서 `QEvent::FontChange` / `QEvent::ScreenChangeInternal` 을 받아 재계산하거나, `sizeHint()` 를 오버라이드해 Qt 가 필요할 때마다 물어보게 한다. 후자가 정석이다.

### L3-3. `ZoomableScrollArea` 의 크기 정책 불일치

**문제.** 같은 클래스의 두 메서드가 서로 다른 정책을 쓴다.

```cpp
// DashAnalyzerHelpers.cpp:144-153 — min == max 로 완전 고정
widget->resize(newSize);
widget->setMinimumSize(newSize);
widget->setMaximumSize(newSize);

// DashAnalyzerHelpers.cpp:155-175 — min 은 원본, max 는 무제한
w->setMinimumSize(m_originalSize);
w->setMaximumSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX);
w->resize(newSize);
```

어느 쪽이 마지막에 호출되느냐로 위젯의 신축성이 달라진다. `setWidgetResizable(false)` (`:47`) 와 맞물려 동작이 예측하기 어렵다. 동일 패턴이 `DashResultsAnalyzerWidget.cpp:3466-3472` 에도 있다.

**해법.** 줌 상태 관리를 한 메서드로 통일하고, 최대 크기는 항상 `QWIDGETSIZE_MAX` 로 두되 `resize()` 로만 실제 크기를 바꾼다.

### L3-4. 오버레이 재배치의 비대칭

**문제.** 같은 `eventFilter` 안에서 CAD 오버레이와 렌더 오버레이가 다르게 처리된다.

```cpp
// DashMainWindow.cpp:3535-3539 — CAD: 매 resize 마다 재배치
m_cadViewOptions->move(10, s.height() - m_cadViewOptions->height() - 10);

// DashMainWindow.cpp:3544-3552 — 렌더: 최초 1회만
if (!m_viewOptionsPositioned) {
    m_viewOptionsWidget->move(10, y);
    m_viewOptionsPositioned = true;      // ← 이후 영구히 갱신 안 됨
}
```

렌더 뷰를 줄이면 view options 오버레이가 영역 밖으로 나가거나 잘린다. 원칙 5 위반이다.

**해법.** `m_viewOptionsPositioned` 플래그를 제거하고 CAD 쪽과 동일하게 매번 재배치한다. 사용자가 오버레이를 드래그로 옮길 수 있게 하려던 의도라면, 플래그 대신 "사용자가 옮긴 상대 위치" 를 저장해 부모 크기에 비례 재배치한다.

### L3-5. 모핑 설정 창의 전역 좌표 배치

**문제.**

```cpp
// DashMainWindow.cpp:1833-1838
QPoint barGlobalPos = m_morphingBar->mapToGlobal(QPoint(0, 0));
int x = barGlobalPos.x() + (m_morphingBar->width() - m_morphingSettings->width()) / 2;
int y = barGlobalPos.y() + m_morphingBar->height() + 10;
m_morphingSettings->move(x, y);
```

`m_morphingSettings` 는 `Qt::Tool | FramelessWindowHint | WindowStaysOnTopHint` 독립 창이다 (`DashMorphingSettings.cpp:59`). 전역 좌표로 한 번 배치될 뿐, 메인 창을 옮기거나 리사이즈해도 따라오지 않는다.

**해법.** 메인 창의 `moveEvent` / `resizeEvent` 에서 표시 중인 설정 창을 재배치하거나, 독립 창 대신 렌더 위젯의 자식 오버레이로 바꾼다.

### L3-6. 오버레이 드래그에 경계 클램프 없음

**문제.** `DashMorphingBar.cpp:124` 의 `move(this->pos() + event->pos() - m_dragPosition)` 에 부모 영역 클램프가 없다. 오버레이를 부모 밖으로 끌어내면 되돌릴 수단이 없다.

**해법.** 이동 결과를 `parentWidget()->rect()` 로 클램프한다. 부모 리사이즈 시에도 클램프를 재적용한다 (L3-4 와 같은 처리).

### L3-7. 다이얼로그 크기 하드코딩

**문제.** `DashMeshQualityDialog.cpp:27` `resize(550, 300)`, `MaterialSetupDialog.cpp:47` `resize(500, 450)`. 논리 px 이라 스케일링은 받지만, 작은 화면이나 고배율에서 화면을 넘길 수 있다.

**해법.** `resize()` 를 제거하고 레이아웃의 `sizeHint()` 에 맡긴다. 크기 지정이 꼭 필요하면 `availableGeometry()` 로 상한을 건다.

### L3-8. QSS 와 `.ui` 의 px 크기 제약

**문제.** `resources/style/qtheme_light.qss` 에 크기 제약 48곳, `morphing_toolbar.css` 에 4곳이 있다. 상당수는 `em` 을 써서 폰트에 연동되어 있으나(`min-height: 1.5em` 등 — 양호), px 고정도 섞여 있다. `.ui` 파일에도 `maximumSize` 30×30 / 24×24 아이콘 버튼 다수와 최상위 기본 geometry (L1-3) 가 있다.

`QMenuBar` 의 `max-width: 3000px` (`qtheme_light.qss:1294`) 은 근거가 불분명한 값이다.

**해법.** L0-4 의 폰트 기반 배율로 전환하려면 px 제약을 `em` 으로 바꾸는 작업이 선행돼야 한다. `max-width: 3000px` 은 의도를 확인한 뒤 제거를 검토한다.

### L3-9. `ResizeToContents` 열이 만드는 폭 변동

**문제.** `QHeaderView::ResizeToContents` 가 40여 곳에 쓰인다 (`DashModelRunnerWidget.cpp:281-324`, `DashOptimizerWidget.cpp:283-316` 등). 데이터가 로드되면 열 폭이 내용에 맞춰 넓어지고, 그것이 테이블 → 모듈 위젯 → `QStackedWidget`(L1-2) → 우측 dock 순으로 전파돼 **데이터 로드 시점에 dock 폭이 튄다**.

`setSizes()` 하드코딩도 같은 맥락이다: `{150,150,150}` (`DashModelRunnerWidget.cpp:272`), `{200,200}` (`DashModelBuilderWidget.cpp:265`), `{400,200}` (`:304`), `{300,100}` (`DashGeometryParameterWidget.cpp:1166`, `DashGeometryParameterCADWidget.cpp:172`).

**해법.** L1-2 의 `QScrollArea` 도입으로 전파를 끊는 것이 우선이다. 추가로 긴 텍스트가 들어가는 열은 `Interactive` + `setDefaultSectionSize()` 로 바꾸고, `setSizes()` 는 비율 기반으로 계산한다.

---

# 렌더링·파이썬 스택 호환 검토

이 문서의 처방은 DPI 정책(Stage 3)과 창 프레임 모델(Stage 4)을 바꾼다. 둘 다 그리기 계층에 닿는 변경이므로 실제 스택과 대조했다.

| 계층 | 구현 | 화면 좌표계 접점 |
|---|---|---|
| 3D 메시 렌더 · 3D 플롯 | `QVTKOpenGLNativeWidget` (VTK 9.4) — **`QOpenGLWidget` 파생, FBO** | VTK 가 DPR 을 직접 관리 |
| 2D 플롯 11종 | `DashPlotWidgetBase` 파생 10 + `DashTimeSeriesGLWidget` — 그리기는 전부 `QPainter` | `resizeGL` 의 `glViewport` |
| CAD 뷰 | OCCT 7.9.1 + `WA_NativeWindow` HWND | `WNT_Window` 가 HWND 클라이언트 사각형을 직접 읽음 |
| 수렴 히스토리 그림 | 파이썬(matplotlib)이 만든 PNG 파일 | `QPixmap` 로드 후 표시 |
| 아이콘 · 설명 이미지 | SVG + DPR 2.0 고정 PNG | 자산이 해상도 독립 |
| 파이썬 계층 | 프리즈드 `deep_opt` (aiohttp 데몬) — 별도 프로세스, 산출물은 파일 | **없음** |

## 판정 — 차단 요인 없음

- **VTK 9.4 는 비정수 DPR 을 다룬다.** `setCustomDevicePixelRatio(double)` / `effectiveDevicePixelRatio()` (`QVTKOpenGLNativeWidget.h:179-181`), `QVTKInteractorAdapter::SetDevicePixelRatio(float)` (`:44`). `PassThrough` 의 1.5 가 정수로 잘리지 않는다. 이상이 생기면 이 위젯만 고정 DPR 로 두는 탈출구도 있다.
- **컨텍스트 재생성을 VTK 가 스스로 처리한다.** *"Qt 가 OpenGL 컨텍스트를 다시 만들어야 했던 경우 `paintGL` 이 `renderVTK` 를 호출해 다시 그린다"* (`QVTKOpenGLNativeWidget.h:77-80`). Stage 1 의 `restoreState()` 가 dock 을 floating 으로 복원해 GL 위젯이 재부모화되는 경로가 안전하다는 뜻이다 — `AA_ShareOpenGLContexts` 를 추가할 이유가 없다.
- **2D 플롯은 GL 리소스를 들고 있지 않다.** 11종 전부 `paintGL` 안에서 `QPainter` 로 그린다. `QPainter` 는 논리 좌표로 동작하며 DPR 을 스스로 처리한다.
- **파이썬 계층은 화면과 무관하다.** 별도 프로세스이고 파일로만 주고받는다. 접점은 R5 하나다.

대신 **지금은 DPR 이 1.0 이라 드러나지 않는 접점 결함 5건**이 있다. DPR 이 1 이 아닌 순간 함께 나타나므로, Stage 3 와 같은 변경으로 처리한다. 다섯 건의 수정량 합계가 10줄 남짓이다.

## R1. CAD 뷰가 논리 좌표를 OCCT 에 그대로 넘긴다

```cpp
// DashOcctViewWidget.cpp:458, 472 — event->x() 는 Qt 논리 px
m_view->StartRotation(event->x(), event->y());
m_view->Rotation(event->x(), event->y());
```

Windows 에서는 `WNT_Window(HWND)` 가 클라이언트 사각형을 직접 읽으므로 **뷰 크기는 물리 px** 이다. 마우스만 논리 px 로 들어간다. DPR 2.0 이면 회전 피벗이 커서의 절반 위치가 된다. 선례의 `WM_NCHITTEST` 200% 버그(부록 "채택할 만한 것 4")와 같은 형태다.

**해법.** 회전·팬 좌표 전달부에서 `devicePixelRatioF()` 를 곱한다.

## R2. 플롯 확대 배율에 물리 픽셀 상한이 없다

```cpp
// DashAnalyzerHelpers.cpp:120, 149
m_zoomFactor = qBound(0.5, m_zoomFactor, 10.0);
QSize newSize = m_originalSize * m_zoomFactor;   // 최대 8000×6000 논리 px
```

`QOpenGLWidget` 의 FBO 는 여기에 DPR 이 한 번 더 곱해진다. DPR 1.0 에서 약 192MB, **DPR 2.0 에서 16000×12000 = 약 768MB.** 같은 조작의 비용이 배율에 따라 4배가 된다.

**해법.** 상한을 물리 픽셀 기준으로 바꾼다 — `qBound(0.5, m_zoomFactor, 10.0 / devicePixelRatioF())`.

## R3. PNG 내보내기에서 물리·논리 좌표가 섞인다

```cpp
// DashAnalyzerHelpers.cpp:77-86
QImage image = glWidget->grabFramebuffer();                  // 물리 픽셀 크기
QPainter p(&image);
for (QWidget* child : ...) child->render(&p, child->pos());  // 논리 좌표
```

DPR 2.0 에서 범례 등 오버레이가 절반 위치에 절반 크기로 찍힌다. **해법**: `p.scale(dpr, dpr)` 한 줄.

## R4. 뷰포트 계산 관행이 두 가지다

`DashTimeSeriesWidget.cpp:65` 는 `resizeGL` 인자를 그대로 쓰고(`glViewport(0,0,w,h)`), `DashPlotWidgetBase.cpp:32` 를 비롯한 나머지는 `calculateViewport()` 로 `논리 크기 × DPR` 을 재계산한다. DPR 1.0 에서는 두 값이 같지만, 1 이 아니면 **둘 중 하나는 반드시 틀리다.** 재계산 쪽은 `static_cast<int>` 절삭이라 DPR 1.5 에서 FBO 와 1px 어긋나기도 한다.

실제 표시 영향은 작을 것으로 본다 — 그리기가 전부 `QPainter` 라 `QPainter` 가 자기 뷰포트를 다시 잡고, `glClear` 는 뷰포트가 아니라 시저를 따르기 때문이다. **가장 단순한 정리는 이 코드를 지우는 것**이고, 그 다음이 `resizeGL` 인자 쪽으로 통일하는 것이다. DPR 2.0 에서 한 번 확인한 뒤 정한다.

## R5. 파이썬이 만든 그림을 800×600 고정으로 표시한다

```cpp
// DashOptimizerWidget.cpp:613
imageLabel->setPixmap(pixmap.scaled(800, 600, Qt::KeepAspectRatio, Qt::SmoothTransformation));
```

matplotlib PNG 를 논리 800×600 으로 줄여 넣는다. DPR 2.0 화면에서는 물리 1600×1200 자리에 800×600 이미지가 들어가 흐려진다. 작은 화면에서 다이얼로그가 화면을 넘칠 수 있는 것은 L3-7 과 같은 성격이다.

**해법.** `scaled(QSize(800,600) * dpr, ...)` 후 `setDevicePixelRatio(dpr)`. 파이썬 쪽은 손대지 않는다.

---

# 3부 — 개선 로드맵

원칙을 되찾는 순서로 배치했다. 각 단계는 앞 단계를 전제한다. 증상 대비 비용이 크게 다르므로 등급을 먼저 둔다.

| 단계 | 등급 | 근거 |
|---|---|---|
| Stage 0 응급 클램프 | **필수** | 치명 발현을 단독으로 차단. 수십 줄, 다른 변경과 독립 |
| Stage 1+2 세션 복원 · 강제 재분배 제거 | **필수** | 상시 증상의 대부분. 반드시 한 묶음 |
| Stage 3 DPI 정책 · 접점 결함 | **필수** | 멀티디스플레이 증상. 변경량 자체는 작다 |
| Stage 4 창 프레임 OS 위임 | **조건부** | 복구 경로를 되살린다. 순서는 아래 "순서에 관한 제약" |
| Stage 5 오버레이 | 선택 | 국소. 언제 해도 무방 |
| Stage 6 구조 (L1) | 선택 | 프로파일링 근거가 나온 뒤 |
| Stage 7 국소 (L3) | 선택 | 재발 방지는 Stage 2 가 담당 |

Stage 6\~7 을 앞당기지 않는다. L0-1 이 남아 있는 상태에서 개별 위젯을 고치면 되돌아온다.

```
[Stage 0] 응급 — 복구 불가 상태 차단 (L0-6)
   │   1. clampToScreen() 추가 — availableGeometry() 로 창 크기·위치 제한
   │   2. moveEvent / resizeEvent 에서 호출, 재진입 가드 필수
   │   ※ 다른 스테이지와 독립. 단독 선행 적용 가능
   │   ※ 프리즈 자체는 남지만 "조작 불가" 라는 최악의 결과는 사라진다
   ▼

[Stage 1] 표준 API 도입 — 원칙 2 회복
   │   1. 모든 QDockWidget 에 setObjectName() 부여 (restoreState 전제 조건)
   │   2. closeEvent 에서 saveGeometry()/saveState(v), 시작 시 restore + 실패 시 폴백
   │   3. L2-4 splitter connect 블록(1630-1643) 삭제
   │   4. m_logHeightRatio 및 adjustLogDockHeight() 제거
   │   ※ inner QMainWindow 상태는 별도 키로 저장
   │   ※ Stage 2 와 반드시 같은 변경으로 묶는다 — 아래 주석 참조
   ▼

[Stage 2] 강제 재분배 제거 — 원칙 1 회복
   │   1. resizeEvent 에서 applyDockResize/applyInnerModuleRenderSplit 호출 제거
   │   2. showRightDock/hideRightDock 에서 applyInnerModuleRenderSplit 제거
   │   3. sizePolicy + setStretchFactor 로 초기 1회 선언
   │   4. QTimer::singleShot 4개를 showEvent 최초 1회 처리로 통합
   ▼

[Stage 3] DPI 정책 선언 — 원칙 3 회복
   │   1. setHighDpiScaleFactorRoundingPolicy(PassThrough) + AA_UseHighDpiPixmaps
   │   2. 접점 결함 R1~R5 를 같은 변경에 포함 (합계 10줄 남짓)
   │      DPR≠1 이 되는 순간 다섯 건이 함께 드러나므로 분리하지 않는다
   │   3. UI Scale 처리 결정 — L0-4 의 a(기능 제거) 또는 b(현행 유지)
   │   ※ QSS px→em 전환(L0-4 의 c)은 여기 포함하지 않는다 — 별도 과제
   ▼

[Stage 4] 창 조작 OS 위임 — 원칙 4 회복 (경로 B)
   │   1. :122 를 setWindowFlags(Qt::Window) 로 교체
   │   2. nativeEvent 에 WM_NCCALCSIZE (프레임 제거 + 최대화 시 프레임 두께만큼 인셋)
   │   3. nativeEvent 에 WM_NCHITTEST (좌표 → 영역 상수 매핑)
   │   4. getResizeEdge/handleResize/getCursorForEdge 및 관련 상태 제거
   │   5. DashTitleBar 마우스 핸들러 4개 제거, 클릭 판정 함수만 남김
   │   6. QGraphicsDropShadowEffect(:1764-1768) 제거 여부 판단
   │   ※ 경로 A(startSystemMove)로 축소하면 1·2·3·6 이 빠지지만
   │     스냅·시스템 메뉴는 복원되지 않는다
   ▼

[Stage 5] 오버레이 정리 — 원칙 5 회복
   │   1. m_viewOptionsPositioned 제거, 매 resize 재배치
   │   2. DashMorphingBar 드래그에 부모 경계 클램프 추가
   │   3. m_morphingSettings 를 moveEvent/resizeEvent 에서 추적
   ▼

[Stage 6] 구조 개선 — L1 계층
   │   1. 모듈 위젯을 QScrollArea(setWidgetResizable) 로 감싸 최소 크기 전파 차단
   │   2. .ui 최상위 레이아웃/sizePolicy 점검
   │   3. 중첩 QMainWindow 단일화 검토 (별도 판단 필요)
   ▼

[Stage 7] 국소 정리 — L3 잔여
       setFixed* 재검토 · sizeHint() 오버라이드 전환 · ZoomableScrollArea 정책 통일
       ResizeToContents 열 조정 · 다이얼로그 resize 제거
```

**Stage 0 을 가장 먼저, 단독으로 적용한다.** 다른 어떤 변경과도 독립적이며, 치명 발현(0부)을 그것만으로 차단한다.

Stage 1\~2 만으로 상시 증상(dock 이 날아다니는 현상)이 대부분 해소될 것으로 예상한다. Stage 3 이 멀티디스플레이 증상과 프리즈 지속 시간을 담당한다.

## 순서에 관한 제약

**Stage 1 과 Stage 2 를 분리하지 않는다.** `restoreState()` 로 복원한 dock 크기는 `resizeEvent` 의 강제 재분배가 남아 있으면 같은 프레임에서 상수 비율로 덮어써진다. 사내 선례가 정확히 이 상태이며, 세션 복원이 위치·가시성만 살리고 크기는 살리지 못한다 (부록 "베끼면 안 되는 것 a"). Stage 1 만 적용하면 "구현했는데 동작하지 않는" 결과가 된다.

**Stage 3 을 Stage 2 보다 먼저 하지 않는다.** `PassThrough` 로 바꾸면 비정수 DPR(1.5)이 들어오는데, 강제 재분배가 남아 있으면 반올림 오차가 매 resize 마다 누적되어 오히려 진동이 심해질 수 있다.

**Stage 4 를 Stage 1 앞으로 당기는 선택지가 있다.** 경로 B 는 창의 프레임 모델을 바꾸므로 `saveGeometry()` 가 기록하는 값의 의미가 달라진다. Stage 1 을 먼저 하면 나중에 state 버전을 올리고 사용자의 저장된 레이아웃을 버려야 한다. 반대로 Stage 4 를 먼저 하면 Stage 0 의 `clampToScreen()` 도 불필요해진다.

| 순서 | 이점 | 비용 |
|---|---|---|
| 0 → 1+2 → 3 → 4 (기본) | 위험이 낮은 것부터. 상시 증상이 먼저 해소됨 | Stage 4 에서 state 버전 번프 1회 |
| 0 → 4 → 1+2 → 3 | 프레임 모델 확정 후 영속화. 치명 발현이 근본적으로 차단됨 | 가장 큰 변경을 초기에 감수 |

Stage 4 의 리스크는 선례 덕분에 "설계부터 해야 하는 작업" 이 아니라 **검증된 구현을 결함 3건을 고쳐 이식하는 작업**으로 내려갔다. 두 순서 모두 현실적이며, 실기 재현으로 상시 증상과 치명 발현 중 어느 쪽이 더 급한지 확인한 뒤 정하는 것이 맞다.

---

# 부록 — 선례 검토: DashOpti_Analyzer

사내 `DashOpti_Analyzer` (`refactor/base` 브랜치) 가 2026-03\~04 에 동일 계열 문제를 겪고 수정했다. 설계 문서·티켓·구현이 모두 남아 있다.

다만 **점진적 대응이 누적된 결과라 방향이 최적이라는 보장이 없고, 문서와 구현이 어긋난 곳도 있다.** 아래는 코드를 직접 대조한 검증 결과다. 채택할 것과 그러지 말아야 할 것을 구분해 둔다.

## 참조 위치

| 자료 | 내용 |
|---|---|
| `docs/notes/020-1-window-layout-architecture.md` | 설계 — nativeEvent · dock 비율 · 세션 복원 |
| `docs/notes/028-1-dpi-coordinate-systems.md` | 물리/논리 px 좌표계 정리 |
| `docs/tickets/020` · `021` · `028` | 구현 결과 · 교훈 · 재오픈 이력 |
| `view/DashMainWindow.cpp:1218-1427` | `adjustAllDockRatios` · 세션 복원 · `nativeEvent` |
| `view/DashTitleBar.cpp` | 마우스 핸들러 제거 후의 모습 |

## 채택할 만한 것

### 1. 경로 B 전환 — 원칙 4 (L0-5)

`Qt::FramelessWindowHint` 를 폐기하고 `Qt::Window` + `WM_NCCALCSIZE` 로 갔다.

```cpp
// view/DashMainWindow.cpp:73-75
// Use WM_NCCALCSIZE to remove frame (not FramelessWindowHint)
// This preserves native window management: snap, drag, maximize, etc.
setWindowFlags(Qt::Window);
```

`WM_NCHITTEST` 핸들러는 DPI 보정까지 포함해 60줄 내외이며, 그 대가로 커스텀 마우스 핸들러가 전부 사라졌다. 이 프로젝트에서 지워질 대상과 정확히 대응한다.

```cpp
// 물리 px(Win32) → 논리 px(Qt) 변환 후 비교 — 200% 환경에서 필수
POINT pt = { GET_X_LPARAM(msg->lParam), GET_Y_LPARAM(msg->lParam) };
ScreenToClient(msg->hwnd, &pt);
const qreal dpr = devicePixelRatioF();
int x = static_cast<int>(pt.x / dpr);
int y = static_cast<int>(pt.y / dpr);
```

### 2. 세션 저장/복원 골격 — 원칙 2 (L0-2)

버전 인자와 실패 폴백, 그리고 **오프스크린 검증**까지 갖춰져 있다.

```cpp
if (!geo.isEmpty()) {
    restoreGeometry(geo);
    QRect restored = frameGeometry();
    bool visible = false;
    for (QScreen* scr : QApplication::screens()) {
        if (scr->availableGeometry().intersects(restored)) { visible = true; break; }
    }
    if (!visible || restored.width() < 400 || restored.height() < 300)
        applyDefaultGeometry();
}
if (!state.isEmpty() && !restoreState(state, 2)) resetLayout();
```

L0-6 의 `clampToScreen()` 이 상시 클램프라면 이쪽은 **시작 시 1회 검증**이다. 성격이 달라 둘 다 필요하다 — 저장된 geometry 가 지금은 없는 모니터를 가리키는 경우를 상시 클램프는 잡지 못한다.

`state` 버전은 실제로 1 → 2 로 올린 이력이 있다 (`032`). dock 구성 변경 시 번프가 필요하다는 것이 실증되었다.

### 3. `resizeDocks` 불신 — 실기 확증 (L2-3)

L2-3 에 인용한 `032` 의 교훈이다. 정적 분석으로 짚은 "레이아웃 활성화 전 호출" 을 넘어서, **서로 다른 dock area 간에는 시점을 맞춰도 반영되지 않는다**는 것이 실기에서 확인되었다. 처방을 `setMinimumWidth()` 로 옮긴 근거다.

### 4. 200% 에서만 드러나는 좌표 혼용 (검증 방법)

`028` 은 100% + 125% 에서 통과시키고 *"Phase 1 만으로 충분, Phase 2\~5 불필요"* 로 종결했다가 8일 뒤 200% 디스플레이에서 재오픈됐다. 원인은 `WM_NCHITTEST` 의 `pt.x / dpr` 누락으로, 창 우측·하단 절반이 리사이즈 영역으로 판정되고 타이틀바 버튼이 클릭되지 않았다.

> Qt 5.15 가 125% 까지는 내부 좌표 변환을 부분 지원하지만 200% 에서 물리/논리 px 혼용이 노출됨. **High-DPI 수정은 반드시 200% 환경에서 테스트 필요.**

## 베끼면 안 되는 것

### a. 세션 복원이 직후에 무효화된다

```cpp
// view/DashMainWindow.cpp:630-633
QTimer::singleShot(100, this, [this]() {
    restoreWindowLayout();     // 저장된 dock 크기 복원
    adjustAllDockRatios();     // ← 상수 비율로 즉시 덮어씀
});
```

`adjustAllDockRatios()` 는 `LEFT_DOCK_RATIO` 등 `static constexpr` 상수로 `resizeDocks()` 를 호출한다. 복원된 dock **크기**는 같은 콜백에서 사라지고 위치·가시성·탭 구성만 남는다. `resizeEvent` 도 같은 함수를 부르므로 이후 리사이즈마다 다시 덮어써진다.

세션 복원이 "구현되어 있으나 크기에 대해서는 동작하지 않는" 상태다. **이 문서의 Stage 1 을 Stage 2 없이 적용하면 같은 결과가 된다** — 3부 "순서에 관한 제약" 에 반영했다.

### b. 설계 문서가 약속한 것이 구현에 없다

| `020-1` 설계 | 실제 구현 |
|---|---|
| `m_dockRatioTimer` 100ms debounce | **없음** — `resizeEvent` 가 매 프레임 `adjustAllDockRatios()` 를 직접 호출 |
| 사용자 조정 비율 추적 (`m_moduleWidthRatio` 가변, `m_userAdjustedLayout`) | **없음** — 비율은 `static constexpr` 고정 |
| splitter 이동 시 비율 저장 | **없음** — `splitterMoved` 연결 0건 |
| `m_logHeightRatio` 를 사용자 조정에 따라 갱신 | **없음** — 읽기 1곳뿐, 쓰기 0건 |

완료 요약 문서(`260330_complete-summary-013-033.md:192`)에는 "debounce 적용 (`QTimer::singleShot 100ms`)" 이라 적혀 있다. **문서를 근거로 삼지 말고 코드를 확인해야 한다.**

결과적으로 Analyzer 의 dock 비율 계층은 이 문서가 L0-1 · L2-1 로 지적한 것과 **같은 안티패턴**이다 — `resizeEvent` 에서 매번 상수 비율을 강제 재분배. 네이티브/프레임 계층만 참조하고 이 계층은 참조하지 않는다.

### c. 최대화 클램프 방식이 거칠다

```cpp
if (IsZoomed(msg->hwnd)) {
    HMONITOR hMon = MonitorFromWindow(msg->hwnd, MONITOR_DEFAULTTONEAREST);
    GetMonitorInfo(hMon, &mi);
    params->rgrc[0] = mi.rcWork;      // 제안 사각형을 통째로 교체
}
```

최대화 시 클라이언트가 화면을 넘치는 것은 사실이나, 정공법은 **넘친 프레임 두께만큼 안쪽으로 깎는 것**이다 (L0-6 해법 참조). 작업 영역으로 통째 교체하면 세 가지 문제가 생긴다.

| 부작용 | 내용 |
|---|---|
| 자동 숨김 작업표시줄 | 자동 숨김이면 `rcWork == rcMonitor` 라 클라이언트가 화면 가장자리를 덮는다 → 작업표시줄을 불러낼 수 없다. 통상 해당 변에 1px 을 남긴다 |
| 모니터 오판 | 모니터 전환 중 `MONITOR_DEFAULTTONEAREST` 가 **이전 모니터**를 반환할 수 있다. 배율이 다른 모니터로 넘어가는 바로 그 순간이 취약 구간이며, 이 문서가 다루는 증상과 정확히 겹친다 |
| 권한 중복 | 같은 파일의 `WM_GETMINMAXINFO` 핸들러가 이미 `rcWork` 로 최대 크기를 제한한다. 두 메커니즘이 같은 일을 한다 — L0-1 이 지적한 "권한 분산" 의 축소판 |

### d. Qt6 이행 시 깨지는 시그니처

`nativeEvent(const QByteArray&, void*, long*)` 는 Qt5 전용이다. Qt6 은 `qintptr* result` 다. Analyzer 자신의 `027-1-migration-stack-analysis.md` 가 Qt6 업그레이드를 1순위 경로로 꼽고 있으므로, 채택 시 이 지점을 알고 들어가야 한다.

### e. 타이틀바 히트테스트가 하드코딩 화이트리스트다

```cpp
bool DashTitleBar::isInteractiveWidget(const QPoint& pos) const {
    return m_menuBar->geometry().contains(pos)
        || m_minimizeButton->geometry().contains(pos)
        || m_maximizeButton->geometry().contains(pos)
        || m_closeButton->geometry().contains(pos);
}
```

타이틀바에 위젯을 추가할 때마다 여기 등록하지 않으면 클릭이 막힌다. `childAt(pos)` 기반 판정으로 두면 유지보수 부담이 없다. 또한 영역 판정이 `y < m_titleBar->height()` 로 x 를 보지 않아 계약이 헐겁다 — `m_titleBar->geometry().contains()` 가 정확하다.

## 사실 정정 — `setHighDpiScaleFactorRoundingPolicy`

`028` 티켓은 *"`setHighDpiScaleRoundingPolicy` API 가 Qt 5.15.16 빌드에 없음 → 제거로 해결"* 로 기록하고 `PassThrough` 를 포기했다. **함수명 오기다.** 실제 API 는 `Factor` 가 들어간 이름이고, 이 프로젝트가 쓰는 동일한 Qt 트리에 존재한다.

```
external/Qt-5.15.16/include/QtGui/qguiapplication.h:159
    static void setHighDpiScaleFactorRoundingPolicy(Qt::HighDpiScaleFactorRoundingPolicy policy);
```

L0-3 / Stage 3 의 `PassThrough` 처방에 API 상 장애물은 없다. Analyzer 쪽도 정정 가능한 항목이다.

## 선례가 없는 영역

구조가 달라 참조 대상이 아예 없는 항목들이다. 이 문서의 고유 분석 영역이다.

| 항목 | 차이 |
|---|---|
| 0부 프리즈 | Analyzer 는 VTK 위젯만. 이 프로젝트는 VTK + OCCT 네이티브 HWND 2개 |
| L1-1 중첩 QMainWindow | Analyzer 에 없음 |
| L1-2 10페이지 QStackedWidget | Analyzer 에 없음 |
| L2-6 DPI 변경 알림 | Analyzer 도 `WM_DPICHANGED` 를 처리하지 않는다 (`028` Phase 5 스킵). **경로 B 로 가도 이 항목은 남는다** |
| L0-4 `QT_SCALE_FACTOR` | Analyzer 는 수동 배율(`height/1080`)을 전량 제거하는 쪽으로 갔고, UI Scale 메뉴에 해당하는 기능 자체가 없다 |
| dock 상수 | 창 구성이 달라 값 재사용 불가 (Analyzer: LEFT 0.15/200/350, RIGHT 0.30/550) |

---

# 검증 방법

## Stage 0 (치명 발현 차단)

- 배율이 다른 모니터로 창을 옮긴 뒤, 창이 화면 작업 영역 안에 남아 있는가
- 타이틀바와 네 모서리가 모두 마우스로 접근 가능한 위치에 있는가
- 창을 화면 밖으로 끌어내려 시도했을 때 클램프가 작동하는가
- 클램프 재진입 가드가 동작하는가 (창 이동 시 CPU 점유가 튀지 않는가)
- 프리즈가 끝난 뒤 F11 없이도 정상 조작이 가능한가

## Stage 1\~2 (상시 증상)

- 모듈 내부 플롯 splitter 를 움직였을 때 하단 로그 dock 높이가 **변하지 않는가**
- 로그 dock 경계를 드래그한 뒤 창을 리사이즈했을 때 조정한 높이가 유지되는가
- 프로젝트 트리에서 부모↔자식 항목을 반복 클릭했을 때 왼쪽 트리 폭이 고정되는가
- 우측 dock 을 열고 닫기를 반복했을 때 왼쪽 트리 폭이 고정되는가
- 같은 모듈을 반복 진입했을 때 우측 dock 폭이 매번 같은 값인가
- 앱을 껐다 켰을 때 이전 레이아웃이 복원되는가
- 데이터가 많은 테이블을 로드했을 때 우측 dock 폭이 튀지 않는가

## Stage 3 (멀티디스플레이)

**200% 배율 환경을 반드시 포함한다.** 100% + 125% 조합에서는 물리/논리 px 혼용 버그가 드러나지 않는다. 사내 선례가 100% + 125% 로 검증하고 "완료" 처리했다가 8일 뒤 200% 환경에서 좌표 오프셋으로 재오픈했다 (부록 "채택할 만한 것 4").

- 100% 모니터와 150% 모니터 간 창 이동 시 물리 크기가 육안상 유지되는가
- **200% 모니터에서 창 우측·하단 절반이 리사이즈 영역으로 오판되지 않는가**
- **200% 모니터에서 타이틀바 버튼이 클릭되는가**
- UI Scale 을 130% 로 두고 위 항목 재확인 (선택지 b 를 택한 경우)
- 비정수 DPR(1.5)에서 1px 경계선·구분선이 사라지거나 두꺼워지지 않는가

렌더링 스택 접점 (전부 200% 에서만 드러난다):

- **CAD 뷰 회전 피벗이 커서를 따라오는가** (R1)
- 플롯을 최대 배율까지 확대했을 때 응답성과 GPU 메모리가 버티는가 (R2)
- 플롯 PNG 저장 시 범례 오버레이의 위치·크기가 화면과 같은가 (R3)
- 플롯 hover 표시가 실제 데이터 점 위에 뜨는가 (R4)
- 수렴 히스토리 그림이 흐려지지 않는가 (R5)

## Stage 4\~5

- 드래그 중 커서가 타이틀바의 같은 지점을 유지하는가
- 화면 가장자리로 끌었을 때 스냅이 동작하는가
- **Win+방향키 스냅이 동작하는가** (경로 B 에서만 기대 가능)
- **`Alt+Space` 시스템 메뉴가 뜨는가** (경로 B 에서만 기대 가능)
- 최대화 시 창이 작업 영역에 정확히 맞는가 (넘치지도, 모자라지도 않는가)
- **작업표시줄을 자동 숨김으로 설정한 뒤 최대화했을 때, 가장자리로 작업표시줄을 불러낼 수 있는가**
- 배율이 다른 모니터에서 최대화했을 때 그 모니터의 작업 영역에 맞는가
- 렌더 뷰를 최소 크기까지 줄였을 때 view options 오버레이가 영역 안에 남는가
- 모핑 설정 창이 메인 창 이동을 따라오는가
- 창 그림자가 정상적으로 그려지는가 (Qt 그림자 제거 후 DWM 그림자로 대체되었는가)

---

# 검증되지 않은 항목

이 문서는 정적 코드 분석만으로 작성되었다.

- **실기 재현 미수행** — 증상을 재현하고 각 원인의 기여도를 분리 측정하지 않았다. L0\~L3 중 무엇이 지배적인지는 확인되지 않았다.
- **프리즈 원인 미프로파일링** — 0부의 [2]\~[4] 는 코드 구조에서 도출한 추론이다. 실제로 시간을 소모하는 지점이 OpenGL 재할당인지, 레이아웃 패스인지, 테이블 열 재계산인지는 프로파일러로 확인해야 한다. 셋의 비중에 따라 Stage 6\~7 의 우선순위가 달라진다.
- **F11 회피책의 신뢰성** — 프리즈 중 키 입력이 큐에 쌓였다가 처리되는지, 어느 모니터로 최대화되는지 실기 확인이 필요하다.
- **L2-4 의 실제 연결 대상** — `findChildren` 이 200ms 시점에 어떤 splitter 를 잡는지는 런타임 `qDebug()` 확인이 필요하다. 표는 후보 목록일 뿐이다.
- **L1-2 의 지배 위젯** — 10개 모듈 중 어느 것이 우측 dock 최소 폭을 결정하는지 측정하지 않았다. `.ui` 기본 크기로는 `DashAnalysisLauncherWidget`(700×800)이 유력하나 런타임 `sizeHint` 는 다를 수 있다.
- **VTK 의 비정수 DPR 실동작** — API 가 `double`/`float` 로 받는 것은 헤더로 확인했으나, DPR 1.5 에서 픽킹 좌표와 스칼라 바 배치가 어긋나지 않는지는 실기 확인이 필요하다.
- **`QOpenGLWidget::resizeGL` 인자 단위** — Qt 5.15 가 논리 px 를 넘기는지 물리 px 를 넘기는지 확정하지 않았다. R4 의 두 관행 중 어느 쪽이 옳은지가 여기서 갈린다. DPR 2.0 에서 값 하나만 찍어 보면 끝난다.
- **`glViewport` 삭제 가능 여부** — 2D 플롯이 전부 `QPainter` 라 뷰포트 설정이 무의미해 보이지만, 지웠을 때 화면이 동일한지는 확인하지 않았다.
- **matplotlib 산출 PNG 의 원본 해상도** — R5 의 처방은 원본이 800×600 보다 크다는 전제에서만 의미가 있다. 파이썬 쪽 `savefig` DPI 를 확인하지 않았다.
- **UI Scale 실사용 여부** — L0-4 의 권장(a: 기능 제거)은 이 메뉴를 쓰는 사용자가 없다는 가정에 기댄다. 확인되지 않았다.
- **프로세스 DPI awareness 의 실제 값** — 실행 파일 manifest 에 DPI 선언이 없는 것은 확인했다 (`resources/resources.rc` 는 아이콘 1줄, CMake 에 manifest 지정 없음). 따라서 Qt 5.15 windows 플러그인이 런타임에 설정하는 값이 그대로 적용되는데, 그것이 Per-Monitor V1 인지 V2 인지는 확인하지 않았다. 0부 [2] 의 전제이므로 실기 확인이 필요하다 — manifest 로 명시 선언하면 추측 자체가 불필요해진다.
- **경로 A 의 한계 범위** — `FramelessWindowHint` 가 제거하는 Win32 스타일 비트와, 그로 인해 어느 OS 기능이 정확히 죽는지는 스타일 계약에서 도출한 것이다. 이 빌드에서 `startSystemMove()` 적용 후 Win+방향키 스냅이 실제로 동작하는지는 확인하지 않았다.
- **경로 B 와 기존 그림자 구현의 충돌** — `QGraphicsDropShadowEffect`(`DashMainWindow.cpp:1764-1768`)를 제거하고 DWM 그림자로 대체하는 것이 맞는지, QSS 의 창 테두리 스타일이 어떻게 보이는지는 실기 확인이 필요하다.
- **`PassThrough` 전환의 부작용** — 비정수 DPR 에서 고정 px 레이아웃(L3-1)이 어떻게 보이는지 확인이 필요하다. 반올림 오차로 1px 경계선이 사라지거나 두꺼워지는 현상이 알려져 있다.
- **중첩 QMainWindow 단일화 가능 여부** — L1-1 의 방식 A 가 현재 배치를 온전히 재현할 수 있는지 검증하지 않았다. `setCorner` 만으로 충분한지 실험이 필요하다.
- **`.ui` 파일 내부 레이아웃 상태** — 13개 `.ui` 의 최상위 레이아웃 유무와 자식 `sizePolicy` 를 개별 확인하지 않았다. 기본 geometry 값만 추출했다.
- **다이얼로그 계열 전반** — `view/dialog/` 는 크기 하드코딩만 확인했고 화면 이동 시 동작은 조사하지 않았다.

# 다음 단계

- [ ] **Stage 0 응급 패치 우선 적용** — `clampToScreen()` 도입 (L0-6)
- [ ] 프리즈 구간 프로파일링 — OpenGL / 레이아웃 / 테이블 중 지배 요인 특정
- [ ] 상시 증상과 치명 발현 중 어느 쪽이 급한지 판단 → Stage 4 선행 여부 결정
- [ ] 프로세스 DPI awareness 실측 후 manifest 로 명시 선언
- [ ] L2-4 실제 연결 대상을 런타임 로그로 확인
- [ ] 모든 `QDockWidget` 의 `objectName` 부여 (Stage 1 전제 조건)
- [ ] Stage 1+2 를 하나의 변경으로 적용 후 상시 증상 재현 여부 재확인
- [ ] 실기 듀얼 모니터에서 Stage 3 검증 — **200% 배율 포함 필수**
- [ ] UI Scale 메뉴 실사용 여부 확인 → L0-4 선택지 a / b 결정
- [ ] `resizeGL` 인자 단위를 DPR 2.0 에서 1회 확인 → R4 정리 방향 확정
- [ ] L1-1 중첩 QMainWindow 단일화 실험
- [ ] 수정 착수 시 Issue 생성 및 이 문서 연동
- [ ] (선례 측) Analyzer 의 `setHighDpiScaleFactorRoundingPolicy` 오기 정정 공유
