# Coding Convention

DashOpti_GUI C++ 코드 작성 규칙 (issue #321). 사람과 코드 생성 에이전트 모두 이 문서를 따른다.
문서와 설정 파일이 다르면 설정 파일이 우선한다.

## 무엇이 기계적으로 강제되는가

**커밋 시점**(`.githooks/pre-commit` → `scripts/hooks/run-format-checks.sh`)에 도는 것은 셋이다.

| 검사 | 대상 | 동작 | 설정 |
|---|---|---|---|
| 줄 끝 공백, 탭 앞 공백 | 스테이지된 모든 파일 | 거부 | — |
| BOM 없는 UTF-8 | **C/C++ 소스만** | 거부가 아니라 **자동 수정** | — |
| clang-format | **C/C++ 소스만** | 거부. 파일 전체가 일치해야 한다 | `.clang-format` |
| 줄바꿈 LF | **모든 텍스트 파일** (`.bat`/`.cmd` 제외) | git 이 커밋·체크아웃 시 **자동 변환** | `.gitattributes` |

**네이밍은 기계적으로 강제하지 않는다.** 이 문서와 코드 리뷰로 다룬다.

> **결정**: clang-tidy 로 네이밍 컨벤션을 검사하는 것은 **저장소 소스 전반이 네이밍 컨벤션에 일관되게
> 정렬된 뒤로 보류한다**(이슈 #386). 어디서 돌릴지(훅, CI)의 문제가 아니라 **언제 시작할지**의 문제다.

정렬 전에 검사를 켜면 이름 하나를 고칠 때 호출자가 열리고, 그 파일의 기존 위반이 요구되고, 그 호출자가 또
열린다. 종료 조건이 없다. 그 연쇄를 막으려면 "이번 변경이 새로 만든 이름만" 같은 장치가 필요한데, 그 장치가
다시 검토 대상이 되어 검사가 끝없이 확장된다. 정렬이 끝나면 그 장치가 통째로 필요 없어진다. 모든 이름이
규칙을 지키는지만 보면 되고, 그것은 어디서 돌리든 단순하다.

규칙 자체는 `.clang-tidy` 에 기계가독 형태로 남아 있어서 Visual Studio 와 VS Code 가 편집 중에 그대로 쓴다.

줄바꿈 문자는 **LF** 다 (2026-09-15 결정). 사유는 대부분의 코드 생성 에이전트가 쓰는 기본 도구가
LF 기준이기 때문이다. 훅이 아니라 `.gitattributes` 가 커밋과 체크아웃 양쪽에서 고정한다.

## 적용 범위

- 전수 재포맷은 하지 않는다. **커밋에 올라온 파일**에 파일 단위로 규칙을 적용한다.
  기존 파일을 처음 손대는 커밋에서 그 파일 전체를 규칙에 맞춘다. 파일 단위로 옛 스타일과 새 스타일이 공존한다.
  서식 정리와 기능 변경은 커밋을 분리한다 (서식 커밋 → 기능 커밋).
- 외부 라이브러리(Qt, VTK, vcpkg 패키지)의 이름과 코드는 대상이 아니다.

## 파일

- 인코딩: BOM 없는 UTF-8. **C/C++ 소스에 한해** 훅이 커밋 시 **자동으로 변환**한다(인덱스와 작업 파일 모두):
  UTF-8 BOM 제거, UTF-16 LE/BE(Visual Studio의 "Unicode 1200/1201") → UTF-8, CP949("한국어 949") → UTF-8.
  사용자가 손댈 것은 없다. 이 셋 중 어느 것으로도 해석되지 않는 파일만 거부된다 — 추측해서 고치지 않는다.
  CP949로 오류 없이 디코드되더라도 한국어로 보이지 않으면(Shift-JIS 등) 거부한다. 조용히 다른 글자로
  바꾸는 것이 고치지 않는 것보다 나쁘기 때문이다.

  다른 확장자(`.md`, `.ui`, `.ps1`, `.rc`, `.bat`, `.txt` 등)는 **대상이 아니다.** 실제로 문제가 생기는 곳이
  C/C++ 편집이고(Visual Studio가 `.h`/`.cpp`를 CP949나 UTF-16으로 저장한다), 임의의 파일을 다루려면
  바이너리를 골라내는 장치가 필요한데 그 장치 자체가 파일을 잘못 고칠 위험이 된다. 파일을 쓰는 유일한
  경로라서 범위를 좁게 둔다. `.ps1`/`.rc`/`.bat`는 Windows에서 BOM이 의미를 가지므로(PowerShell 5.1이
  BOM 없는 `.ps1`을 시스템 코드페이지로 읽는 등) 계속 ASCII로만 작성한다.
- 줄 끝 공백, 탭 앞 공백 금지.
- 줄바꿈: **LF**. `.gitattributes` 의 `* text=auto eol=lf` 가 저장소의 모든 텍스트 파일을 대상으로
  하며(바이너리는 git 이 스스로 제외한다), 커밋뿐 아니라 **체크아웃까지** LF 로 고정한다. 각자의
  `core.autocrlf` 설정은 무시된다. 예외는 `.bat`/`.cmd` 로, Windows 배치는 CRLF 를 유지한다.

  양쪽을 LF 로 못박는 이유는 git 이 매번 내던 `LF will be replaced by CRLF` 경고를 없애기
  위해서다. 작업 파일과 체크아웃 결과가 다를 때만 나는 경고이고, 사람도 에이전트도 그 경고를
  보고 줄바꿈을 고치려 드는 헛수고를 한다.

  **머지 직후 한 번은 반대 방향 경고**(`CRLF will be replaced by LF`)가 난다. 작업 파일이 아직
  CRLF 이기 때문이다. 아래를 한 번 돌리면 없어진다.

  ```bash
  git rm --cached -r . && git reset --hard
  ```

## 서식 (clang-format)

조직 표준 `.clang-format`(Mozilla 기반)을 그대로 쓴다. 저장소 루트의 `.clang-format`이 기준이며, 주요 특징:

- 들여쓰기 4칸(조직 표준 Mozilla의 2칸을 덮어씀. 현행 코드 95%가 4칸), 한 줄 100자.
- 반환형은 함수 이름과 같은 줄에 둔다. 줄이 100자를 넘을 때만 자동으로 나눈다 (조직 표준의 "항상 별도 줄"을 덮어씀).
- `if`/`for` 등 한 줄 본문에도 중괄호를 붙인다. **clang-format 이 직접 삽입한다**
  (`InsertBraces: true`). 서식 옵션 중 유일하게 코드를 고치는 쪽이며, 삽입만 하고 제거는 하지
  않는다. 저장소 전체로는 140 파일에 중괄호 2,379 개가 들어가고, 파일 단위로 맞추는 방식이라
  커밋마다 diff 로 보게 된다.
- 이항 연산자로 줄을 나눌 때 연산자를 줄 앞에 둔다.
- include 순서는 clang-format 이 건드리지 않는다 (`SortIncludes: Never`). 순서 의존 헤더가 있어
  자동 정렬은 켜지 않는다. 손으로 맞추는 규칙은 아래 "헤더와 include" 절에 있다.

파일을 맞추는 명령(훅이 거부 시 파일마다 정확히 출력한다):

```bash
clang-format -i "<파일>" && git add "<파일>"
```

그 파일에 미스테이지 변경도 있으면 `git add` 대신 `git add -p "<파일>"`을 쓴다(그 변경까지
통째로 스테이지시키지 않기 위해). 공백이 있는 경로도 그대로 쓸 수 있도록 항상 따옴표를 붙인다.

## 네이밍 (clang-tidy `readability-identifier-naming`)

Qt 스타일. **매크로를 제외한 모든 식별자에 UPPER_CASE 금지.**

**기계적으로 검사하지 않는다. 리뷰에서 본다.** clang-tidy 검사는 저장소 소스가 이 규칙에 일관되게
정렬된 뒤에 시작한다(#386).

**리뷰 규칙도 같다. 이번 변경이 새로 만든 이름만 본다.** 호출자 파일에 원래 있던 위반은 이 변경의
책임이 아니므로 요구하지 않는다. 기존 위반은 누군가 그 이름을 직접 고칠 때 사라진다. 속도는 팀이 정한다.

규칙 자체는 `.clang-tidy` 에 기계가독 형태로 있고 Visual Studio 와 VS Code 가 편집 중에 그대로 쓰므로,
새 코드를 쓸 때 IDE 가 먼저 알려준다. 저장소를 정렬할 때도 이 파일이 기준이 된다.

| 대상 | 규칙 | 예 |
|---|---|---|
| 클래스, 구조체, enum, 네임스페이스, typedef/alias, 템플릿 파라미터 | PascalCase | `DashModelRunner`, `Utils` |
| enum 값 | PascalCase | `RunState::Idle` |
| 함수, 메서드 | camelCase | `setModel()`, `runVolumeMorphing()` |
| 지역변수, 파라미터, 전역/정적 변수 | camelCase | `projectPath` |
| 상수 (`const`, `constexpr`, static const) | camelCase | `maxRetryCount` (`k` 접두와 UPPER_CASE 모두 금지) |
| 멤버 변수 (private, protected) | camelCase + **`_` 접미** | `preprocessor_`, `jobPool_` |
| 멤버 변수 (public) | camelCase. **접미 없음** | `commandId`, `filePath` |
| 매크로 | UPPER_CASE | `DASH_BUILD_DEV` |

**접두는 배제하고 접미 `_` 를 쓴다** (2026-09-15 결정). 헝가리안 접두(`m_`, `p`, `str` 등)와 private
표시용 접두 `_`, 상수용 `k` 접두 모두 금지다. Qt Designer 가 생성하는 `ui->` 멤버가 접두 없는
camelCase 라서 `m_` 강제는 한 클래스 안에 두 규칙을 혼재시킨다.

접두를 뺀 자리에 접미 `_` 를 남긴 이유는 따로다. 멤버 변수와 지역 변수를 이름만 보고 구별할 수 없으면
사람도 코드 생성 에이전트도 둘을 헷갈린다. `_` 는 그 구별을 이름 끝에 두어 `ui->` 와 충돌하지 않는다.

**public 멤버는 접미를 붙이지 않는다.** 구별이 필요한 것은 클래스 안에서 지역 변수와 섞이는 이름이고,
public 필드는 바깥에서 `obj.field` 로 접근하니 그 구별이 이미 문법에 있다. 순수 데이터 `struct` 가
`point.x_` 가 되는 것도 막는다.

기존 `m_` 이름 10,087 건은 정렬 작업(#386)에서 함께 다룬다.

예외:
- Qt/VTK가 정한 이름을 그대로 써야 하는 것(오버라이드, `vtkTypeMacro` 계열, `Q_OBJECT` 등)은 규칙 대상이 아니다.
  오버라이드 메서드는 기반 클래스 이름을 따른다.
- 외부 API 콜백처럼 어쩔 수 없는 경우는 `// NOLINT(readability-identifier-naming)` 을 해당 줄에 붙여 둔다.
  지금은 아무것도 그것을 읽지 않지만, IDE 와 나중의 정렬 작업이 같은 표시를 쓴다.
- 자동 수정(`clang-tidy -fix`)은 쓰지 않는다. 한 파일에서 이름을 바꾸면 다른 파일의 호출자가 깨진다.
  이름 변경은 호출자까지 함께 고친다.

## 코드 작성 규칙

서식·네이밍과 달리 기계가 검사하지 않는다. 리뷰에서 본다. 모두 2026-09-15 결정이다.

### getter / setter

getter 는 필드 이름을 그대로 쓴다. `get_` 접두를 붙이지 않는다. setter 는 동사로 시작한다.

```cpp
std::vector<int> items() const;      // getter — 필드명 그대로
void setItems(std::vector<int> v);   // setter — set 접두 필수
```

동명 오버로드(`items(v)` 로 설정, `items()` 로 조회)는 쓰지 않는다. `list.item(1)` 이 첫 번째 항목을
읽는 것인지 1을 넣는 것인지 호출부만 보고 알 수 없다. 멤버에 `_` 접미가 붙으므로 `items()` 와 `items_`
가 충돌하지도 않는다.

### 헤더와 include

**기계가 강제하지 않는다.** `.clang-format` 은 `SortIncludes: Never` 그대로고 훅도 이 절을 보지 않는다.
새로 쓰는 파일과 이미 손대고 있는 파일에 자발적으로 맞추는 규칙이다.

- 헤더는 `#pragma once` 로 시작한다.
- 디렉터리 경로를 표기한다. flatten 하지 않는다 — 경로가 모듈 구분을 드러낸다.
- **이 프로젝트에서 작성한 파일은 `"..."`, 나머지는 `<...>`.**
- **`<...>` 를 먼저, `"..."` 를 그 아래에 둔다.** 외부가 위, 우리 코드가 아래다.
- **각 묶음 안에서는 ASCII 순으로 정렬한다.** 대문자가 소문자보다 앞선다 — `"Utilities/..."` 가
  `"controller/..."` 보다 위다. 디렉터리 이름의 대소문자를 골라 순서를 의도적으로 정할 수 있다.
- `.cpp` 는 **자기 헤더를 최상단**에 둔다. 묶음 구분보다 위다. 그 헤더가 홀로 컴파일되는지
  그 자리에서 드러난다.
- **include 사이에 빈 줄을 넣지 않는다.** 묶음이 갈려도 한 덩어리로 붙여 쓴다.

```cpp
// DashScatterPlotter.cpp
#include "model/analyzer/DashScatterPlotter.h"
#include <QWidget>
#include <algorithm>
#include <vtkChartXY.h>
#include "Utilities/Logger.h"
#include "controller/DashManager.h"
```

순서에 의존하는 헤더가 있으면 정렬하지 말고 그 자리에 이유를 주석으로 남긴다. 그런 헤더가 남아 있어서
clang-format 의 자동 정렬은 켜지 않는다.

### 빈 매개변수

`void` 를 적지 않는다.

```cpp
void start();       // O
void start(void);   // X — C 시절 표기
```

### 후행 반환 타입

**허용하되 필수는 아니다.** 반환 타입이 인자에 의존할 때는 후행 표기가 유일한 방법이므로 그때는 쓴다.

```cpp
auto push(Job j) -> dash::core::Result<void>;   // 허용
dash::core::Result<void> push(Job j);           // 허용
```

전면 필수로 하지 않은 이유는 추론이 더 읽기 쉬운 자리가 있기 때문이다 — perfect forwarding 의
`-> decltype(handle(std::forward<decltype(x)>(x)))`, `std::visit` 의 분기 람다처럼 후행 타입을 쓰면
오히려 길어지거나 아예 적을 수 없는 경우다. 람다의 반환 타입은 의도가 애매할 때 명시하기를 권한다.

### 오류 처리

`std::expected` 단일 체계다. 예외를 오류 전달 수단으로 쓰지 않는다.

**오류 타입에 `std::string` 을 쓰지 않는다.** 이미 있는 것을 쓴다 —
vcpkg core-lib 포트의 `#include <CoreLib/Error.hpp>` 에 있는 `dash::core::Result<T>` 가
`std::expected<T, dash::core::ErrorState>` 이고, `make_unexpected(ErrorCode, ...)` 생성 헬퍼와
`std::formatter` 특수화까지 들어 있다.

```cpp
dash::core::Result<void> start()
{
    if (!ready_) {
        return dash::core::make_unexpected(dash::core::ErrorCode::LogicError, "not ready");
    }
    return {};                                  // 성공
}

auto res = start();
if (!res) {
    return std::unexpected(res.error());        // 하위 오류는 삼키지 말고 전파
}
```

비동기·콜백 경로에서 `throw` 를 넘기지 않는다. 외부 라이브러리가 던지면 그 경계에서 `try/catch` 로
받아 `Result` 로 변환한다.

### 시그널·슬롯 연결

`setModel()` 류(멤버 모델 포인터에 대입하면서 `connect()` 를 거는 함수)는 재호출마다 새 연결을
쌓기 쉽다. 연결이 N개 쌓이면 시그널 1회에 슬롯이 N번 돈다.

- 함수 앞머리의 `disconnect(model_, nullptr, this, nullptr)` 같은 wholesale disconnect 는
  **sender 가 교체되는 그 모델이고 receiver 가 `this` 인 연결만** 끊는다. 두 조건을 다 만족하는
  연결은 이것만으로 막힌다. 그리고 이 disconnect 는 **멤버를 교체하기 전**에 있어야 한다 —
  교체 뒤에 있으면 새 모델을 끊는 것이라 이전 모델의 연결이 그대로 남는다.
- **sender 가 교체되지 않는 자식 위젯**(버튼·테이블·내부 위젯)이면 wholesale 에 안 걸린다. 슬롯이
  PMF 면 `Qt::UniqueConnection` 으로 막는다.
- **슬롯이 람다면 `Qt::UniqueConnection` 이 무효다.** PMF 슬롯에만 유효하고, Qt6 Debug 빌드는 그
  조합을 `Q_ASSERT` 로 즉시 잡는다. 표적 `disconnect(sender, signal, receiver, nullptr)` 를
  connect 앞에 둔다. 그러려면 람다 connect 에 context object(`this`)를 넘겨야 한다.
- **sender 나 receiver 가 교체되는 그 멤버인데 반대쪽 끝이 `this` 가 아니면**(모델 → 자식 위젯 등)
  `Qt::UniqueConnection` 으로는 부족하다. 그 토큰은 **새** 모델에 대한 중복만 막고 이전 모델의 연결은
  그대로 남긴다. 슬롯 형태와 무관하게, 교체 **전에** 이전 모델을 대상으로 표적 `disconnect` 를 둔다.
- 와일드카드 `disconnect(sender, nullptr, this, nullptr)` 로 뭉뚱그리지 않는다. 같은 sender 의 다른
  연결을 함께 끊는다.

```cpp
void Widget::setModel(Model* model)
{
    if (model_) {
        disconnect(model_, nullptr, this, nullptr);          // sender=model_, receiver=this
        disconnect(model_, &Model::ready,                    // 반대쪽 끝이 this 가 아닌 것은 따로
                   child_, &Child::onReady);                 // 받는 슬롯까지 명시한다
    }
    model_ = model;                                          // 교체는 disconnect 뒤

    connect(button_, &QPushButton::clicked,                  // 자식 sender + PMF
            this, &Widget::onClicked, Qt::UniqueConnection);
    disconnect(button_, &QPushButton::toggled, this, nullptr);
    connect(button_, &QPushButton::toggled, this, [this](bool on) { ... });  // 람다는 표적 disconnect
}
```

## 로컬 설정 (clone당 1회)

`scripts\setup-environment.ps1` 이 `core.hooksPath` 설정과 `clang-format` 설치를 대신 해 준다 (`README.md` 참고). 수동으로 하려면:

```bash
pip install clang-format==22.1.8
git config core.hooksPath .githooks
```

`pre-commit` 은 서식 검사에 이어 Level 1 테스트도 돌린다 (#359, `docs/test-levels.md`). 서식 검사가 먼저다 — 걸리면 테스트 빌드를 시작하지도 않는다.

서식 검사가 쓰는 외부 도구는 **`python` 과 `clang-format` 둘뿐**이다. 버전을 고정하는 이유는 clang-format 출력이
버전에 따라 달라지면 다른 사람이 포맷한 파일을 훅이 거부하기 때문이다. 훅은 PATH 에서 찾고, 없으면 pip 의
scripts 디렉터리를 본다.

clang-tidy 는 설치하지 않아도 된다. 네이밍 검사가 보류 상태라 훅도 빌드도 그것을 부르지 않는다. IDE 에서
편집 중에 네이밍 힌트를 받고 싶으면 따로 설치하면 되고, 그때 `.clang-tidy` 를 규칙으로 읽는다.

**아무것도 실행하지 않는다고 해서 틀려도 되는 파일은 아니다.** IDE 가 읽고, 각자 손으로도 돌릴 수
있으므로 규칙이 틀리면 이름을 반대로 고치라고 안내하게 된다. 실제로 그런 일이 있었다 — const·static
멤버에서 접미 규칙이 뒤집혀 있었다. 설정이 의도대로 동작하는지는 아래로 확인한다(clang-tidy 가 없으면
통과가 아니라 **건너뜀**으로 종료 코드 2를 낸다).

```bash
python tests/hooks/test-clang-tidy-config.py
```

`.clang-tidy` 가 표현하지 못해 **리뷰에서만 잡히는 규칙이 둘** 있다.

- `k` 접두. `kCap` 은 문법적으로 올바른 camelBack 이라 어떤 Case 규칙에도 안 걸리고, clang-tidy 에는
  "이 접두는 금지" 를 적을 옵션이 없다.
- public 멤버의 접미 면제 중 const·static 인 것. 이 옵션들은 접근 수준이 아니라 **종류**로 갈려서,
  public `const int limit` 에도 `_` 를 요구한다. private 쪽이 압도적으로 흔해 접미 규칙을 살렸다.

훅이 커밋을 거부하면 출력된 수정 명령을 그대로 실행하고 다시 커밋한다.

## IDE에서 서식 적용

Visual Studio와 VS Code 모두 저장소 루트의 `.clang-format`을 자동으로 찾아 쓴다. 저장소에 IDE별 설정 파일은 두지 않는다.

| | Visual Studio | VS Code |
|---|---|---|
| 문서 서식 | `Ctrl+K, Ctrl+D` | `Shift+Alt+F` |
| 선택 영역 서식 | `Ctrl+K, Ctrl+F` | `Ctrl+K, Ctrl+F` |
| 전제 | "ClangFormat 지원 사용" 옵션(기본 켬) | C/C++ 확장(`ms-vscode.cpptools`), 스타일 설정 기본값 `file` |

VS는 `.clang-format`을 파일을 열 때 읽어 캐시한다. 규칙 파일이 바뀐 뒤에는 파일이나 솔루션을 다시 열어야 훅과 일치한다.

## 에이전트용 요약

코드를 생성·수정할 때:
1. 새로 쓰는 코드는 위 네이밍 표와 `.clang-format`을 따른다. 주변 옛 코드의 스타일을 따라가지 않는다.
2. 기존 파일을 수정하면 그 파일은 커밋 전에 `clang-format -i`로 전체를 맞춘다. 서식 커밋과 기능 커밋은 분리한다.
   수정하지 않는 파일은 건드리지 않는다.
3. 식별자 이름을 바꿀 때는 모든 호출자를 함께 고친다.
4. UTF-8(BOM 없음), 줄바꿈 LF, 줄 끝 공백 없음.
5. 멤버 변수는 `_` 접미. getter 는 필드명, setter 는 `setX()`. 헤더는 `#pragma once`,
   include 는 경로 표기 · 우리 코드만 `"..."` · `<...>` 가 위 · 묶음 안에서 ASCII 순 · 빈 줄 없이.
   오류는 `dash::core::Result<T>` 로 돌린다 — 오류 타입에 `std::string` 을 쓰지 않는다.
6. 모델을 교체하는 함수에서 `connect()` 를 걸 때는 재호출로 연결이 쌓이지 않는지 본다.
   슬롯이 람다면 `Qt::UniqueConnection` 이 무효라 표적 `disconnect` 가 필요하다.
