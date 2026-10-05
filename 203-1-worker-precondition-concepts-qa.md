# 워커 선결 조건 용어 해설 — magic static · lazy-init 레이스 · Registry/Context · try_emplace · rdbuf 스왑 ([#203](203-2-worker-preconditions-analysis.md) 개념 Q&A)

> 관련 Issue: [#203](203-2-worker-preconditions-analysis.md)
> 기반 문서(요약표): [205-1-w6-w10-ticket-summary](205-1-w6-w10-ticket-summary.md) — D1~D5 게이트 및 서브태스크 d(#213)·e(#214) 정의를 한 표로 요약
> 원본 문서: [203-2-worker-preconditions-analysis](203-2-worker-preconditions-analysis.md) — [#203](203-2-worker-preconditions-analysis.md) 본문 이관본 (D1\~D5 실측·처방 정본)

## 개요

Issue [#203](203-2-worker-preconditions-analysis.md)(워커 투입 선결 조건 D1~D5 분석)을 읽다가 나온 C++/동시성 용어들을 **개념 → 사용법 → 비교군** 순서로 풀어쓴 학습용 Q&A 문서다. 각 답변은 실제 코드 앵커(2026-08-01 dev 기준)에 근거를 두었고, 개념이 [#203](203-2-worker-preconditions-analysis.md) 의 어느 선결 조건(D1~D5)에서 나왔는지 함께 표시했다.

**질문 → 절 인덱스** (요청한 순서 그대로 찾기):

| # | 질문 | 답 위치 | 연관 선결조건 |
|:--:|---|---|:--:|
| 1 | magic static 이 뭔지 (개념·사용·비교군) | <1>절 | D1 |
| 2 | cout rdbuf 스왑이 뭐지 | <6>절 | D4 |
| 3 | 초기화 직렬화 보장이 뭐야 | <1>절 "직렬화 보장" | D1 |
| 4 | 메인과 워커가 동시에 `m_instance==nullptr` 관찰은 무슨 뜻 | <2>절 | D1 |
| 5 | `atexit(Destroy)` 이중등록 → 이중해제가 실제로? | <2>절 "이중해제" | D1 |
| 6 | 레지스트리·컨텍스트가 각각 뭐야 | <3>절 | D3 |
| 7 | `try_emplace` 가 뭐지 | <4>절 | D3 |
| 8 | D3 접근 규약은 문제가 뭐지 | <5>절 | D3 |
| 9 | 전역 `std::cout` rdbuf 스왑이 뭐야 | <6>절 (질문 2 와 통합) | D4 |
| 10 | "D5 규약은 e 의 모든 Job 에 동시 적용" 의 e 가 뭐야 | <7>절 | D5 |

> **한 가지 사전 정정**: D4 의 `rdbuf` 스왑 코드는 [#203](203-2-worker-preconditions-analysis.md) 재검증 시점(2026-07-28, commit `4388c57`)엔 남아 있었으나, 그 뒤 리팩터로 **현재 dev 코드에서는 이미 사라졌다**(repo 전역 `rdbuf` 스왑 grep 0). 그래도 개념 자체는 알아둘 값이 있어 이슈 인용본으로 설명한다. 상세는 <8>절(현재 코드 대조) 참조.

---

## 1. magic static — 개념·사용법·비교군 (질문 1, 3)

### 개념

**magic static** = 함수 내부에 선언한 `static` 지역 변수. 함수 실행이 그 선언 줄에 **처음 도달할 때 딱 한 번** 초기화된다. "magic"이라 부르는 이유는 **C++11 부터 컴파일러가 그 초기화에 숨은 가드를 자동으로 끼워 넣기** 때문이다 — 여러 스레드가 동시에 첫 진입해도 **하나만 초기화하고 나머지는 초기화가 끝날 때까지 블록**한다. (Itanium ABI 에서는 `__cxa_guard_acquire` / `__cxa_guard_release` 와 1바이트 가드 변수로 구현.) 별칭은 **Meyers' Singleton**.

소멸도 자동이다 — 프로그램 종료 시 정적 소멸 순서(생성의 역순)로 소멸자가 불린다. 즉 `new` / `delete` / `atexit` 를 손으로 관리할 필요가 없다.

### 사용법

```cpp
DashManager& DashManager::Mgr() {
    static DashManager instance;   // magic static — 최초 호출 때 1회 생성, 이후엔 그대로 반환
    return instance;               // 참조 반환 (heap 포인터 아님)
}
```

이 코드베이스에 **이미 쓰이는 선례**가 있다 — 레지스트리가 정확히 이 방식이다:

```cpp
// controller/DashAnalysisModelContextRegistry.cpp:10-13
DashAnalysisModelContextRegistry& DashAnalysisModelContextRegistry::Instance() {
    static DashAnalysisModelContextRegistry inst; // thread-safe since C++11
    return inst;
}
```

반면 `DashManager` 는 아직 **수동 lazy-init**(D1 의 문제 코드)이다:

```cpp
// controller/DashManager.cpp:208-215
DashManager *DashManager::Mgr() {
  if (m_instance == nullptr) {        // 락 없는 검사
    m_instance = new DashManager();   // 락 없는 생성·발행
    atexit(Destroy);
  }
  return m_instance;
}
```

### 직렬화 보장 (질문 3 — "초기화 직렬화 보장이 뭐야")

magic static 의 스레드 안전은 C++11 표준 문구(`[stmt.dcl]/4`)에서 나온다:

> "변수가 초기화되는 **도중에** 다른 실행 흐름이 동시에 그 선언에 진입하면, 그 동시 실행은 **초기화 완료를 기다린다**."

즉 컴파일러가 **동시 초기화들을 한 줄로 세워(serialize)** 하나만 실제로 초기화하고 나머지는 그 완료를 기다리게 한다. 결과는 **정확히 1회 초기화 + happens-before 성립**(초기화가 끝난 뒤에야 다른 스레드가 완성된 객체를 본다).

여기서 "직렬화"는 데이터를 바이트로 바꾸는 그 직렬화(serialization/마샬링)가 **아니다**. **여러 스레드의 동시 초기화를 순차(serial) 실행으로 강제**한다는 뜻이다. 수동 lazy-init(`if(p==null) p=new`)에는 이 보장이 없어서, 두 스레드가 모두 null 을 보고 둘 다 `new` 하는 사고(<2>절)가 난다.

### 비교군

| 방식 | 스레드 안전 | 코드량 | 소멸 관리 | 이 프로젝트에서 |
|---|:--:|:--:|---|---|
| 수동 lazy `if(p==null) p=new` | ✗ | 소 | 수동 `atexit`/`Destroy` | 현 `DashManager` — **D1 문제 원인** |
| **magic static** `static T inst;` | ✓ (언어 보장) | 최소 | **자동**(정적 소멸) | `Registry` 선례, **D1 처방 B** |
| double-checked locking + mutex | ✓ | 중 | 수동 | C++11 이전 관용구, 이젠 장황 |
| `std::call_once` | ✓ | 중 | 수동 | 명시적이나 magic static 이 더 간결 |
| eager pre-init (`main()` 에서 1회 호출) | ✓ (스레드 생성 전이면) | 최소 | 기존 그대로 | **D1 처방 A** — 즉효, 비용 0 |

**주의 — DashManager 를 magic static 으로 바꿀 때의 걸림돌**: `Mgr()` 은 지금 **포인터**(`DashManager*`)를 반환하고 `Destroy` 가 `delete m_instance` 를 전제로 한다. magic static 은 객체가 heap 이 아니라 정적 저장소에 살아서 `delete` 대상이 아니다. 따라서 (a) 반환 타입·호출부 조정 또는 내부 `static` + 주소 반환, (b) `atexit(Destroy)` / `delete` 경로 제거(정적 소멸로 이관)가 필요하다. 그래서 [#203](203-2-worker-preconditions-analysis.md) 은 처방 A(선-초기화, 즉효)를 1차로, magic static(B)을 "2차·additive"로 둔다.

---

## 2. 싱글톤 lazy-init 레이스 — nullptr 동시 관찰 · atexit 이중해제 (질문 4, 5)

### "메인과 워커가 동시에 `m_instance==nullptr` 를 관찰" (질문 4)

"**관찰(observe)**" = 스레드가 `m_instance` 의 값을 **읽어서 조건을 평가**한다는 뜻. 문제는 `if (m_instance == nullptr)` 의 **읽기**와 `m_instance = new ...` 의 **쓰기** 사이가 아무 보호도 없다는 것이다. 그 틈에 다른 스레드가 끼면 둘 다 "아직 null"을 본다:

```
     메인 스레드                          워커 스레드
t1   if (m_instance==nullptr) → true
t2                                        if (m_instance==nullptr) → true   ← 메인이 아직 대입 전
t3   m_instance = new DashManager()  →  인스턴스 A
t4                                        m_instance = new DashManager()  →  인스턴스 B  (A 를 덮어씀)
t5   atexit(Destroy)                      atexit(Destroy)                   ← 이중 등록
```

두 스레드가 **같은 null 을 관찰**했기 때문에 벌어지는 일:

1. **이중 생성** — 인스턴스가 2개 만들어지고, 늦은 대입(t4)이 이른 것(t3)을 덮어써 **인스턴스 A 는 누수**. 이후 t3 이전에 A 를 잡아 둔 코드와 t4 이후 B 를 잡는 코드가 **서로 다른 싱글톤을 참조**(상태 분열).
2. **미완성 발행** — `m_instance = ...` 대입이 **생성자 완료보다 먼저 관찰**될 수 있다(비원자 포인터 + 메모리 순서 미보장). 다른 스레드가 아직 초기화 중인 객체의 멤버를 읽는다.
3. **atexit 이중 등록** → 종료 시 이중 해제(아래).

`Mgr()` 호출이 코드 전역에 290회(28파일) 흩어져 있어([#203](203-2-worker-preconditions-analysis.md) 재검증) "워커에서는 절대 첫 호출이 안 되게 하자"를 리뷰만으로 보장하기는 비현실적 → 구조적 장치(선-초기화 또는 magic static)가 필요하다.

### `atexit(Destroy)` 이중등록 → 이중해제가 실제로 일어나는가? (질문 5)

먼저 `atexit` 부터: `atexit(f)` 는 **정상 종료 시 f 를 실행하도록 예약**한다. 같은 함수를 두 번 등록하면 종료 시 **두 번 실행**된다(등록의 역순).

위 레이스로 두 스레드가 `if` 블록에 모두 진입하면 `atexit(Destroy)` 가 **2회 등록** → 종료 시 `Destroy()` 가 **2회 호출**된다. 그럼 이중해제(double-free)가 실제로 나느냐 — **`Destroy` 의 구현에 달렸다.** 현재 코드는:

```cpp
// controller/DashManager.h:65-67
static void Destroy(){
    delete m_instance;      // ← delete 뒤에 m_instance = nullptr 가 없다!
}
```

`delete` 후 포인터를 null 로 만들지 않으므로, **두 번째 `Destroy()` 가 이미 해제된 포인터를 다시 `delete` → 진짜 double-free(UB, 크래시 가능)**.

만약 `delete m_instance; m_instance = nullptr;` 였다면 두 번째 호출은 `delete nullptr`(표준상 no-op) → 안전(멱등). 즉:

- **질문에 대한 직답**: 이중등록이 일어나면, **현재 `Destroy` 코드에서는 이중해제가 실제로 일어난다**(멱등 가드가 없어서). 
- 단, 이중등록 **자체가 D1 레이스(질문 4)를 전제**로 하므로, 지금처럼 단일(GUI) 스레드 정상 경로에서는 블록이 1회만 돌아 등록도 1회 → 발생하지 않는다. **워커(두 번째 스레드)를 넣는 순간 현실화**된다.
- 처방(선-초기화 / magic static)이 레이스를 없애면 이 경로도 함께 닫힌다. 응급으로 `m_instance = nullptr;` 한 줄만 넣어도 double-free 는 막히지만, **근본은 레이스 제거**다(그래야 상태 분열·미완성 발행도 함께 사라진다).

---

## 3. 레지스트리 vs 컨텍스트 (질문 6)

둘은 "캐시 관리자"와 "데이터 한 덩어리"의 관계다.

### DashAnalysisModelContext — "컨텍스트" = 데이터 한 덩어리

해석 모델(analysis model) **하나**의 리소스 묶음이다. 외부 reader-writer 패키지가 파싱한 결과를 담는다 — 파트 목록, 메시(`vtkUnstructuredGrid`), FE 조건 엔트리(`DashFeConditionEntry`), 시각화 액터 등.

```cpp
// controller/DashAnalysisModelContext.h:51-52
// Context of analysis-model resources backed by the external reader-writer package
class DashAnalysisModelContext { ... };
```

핵심 성질: **내부 동기화가 0건**(`mutex`/`atomic` 없음). "모델 파일 1개 = Context 1개"이고, 같은 Context 인스턴스를 여러 소비자가 공유한다.

### DashAnalysisModelContextRegistry — "레지스트리" = 파일→컨텍스트 캐시(싱글톤)

파일 경로를 키로 Context 를 캐시·관리하는 **싱글톤 등록소**. 헤더 주석 그대로 `// filePath -> DashAnalysisModelContext`:

```cpp
// controller/DashAnalysisModelContextRegistry.h:22-54 (발췌)
class DashAnalysisModelContextRegistry : public QObject {
    static DashAnalysisModelContextRegistry& Instance();       // magic static
    DashAnalysisModelContext* getOrLoad(const QString& filePath); // 있으면 캐시, 없으면 로드
    ...
    std::mutex m_mutex;                                          // 맵 조작만 보호
    std::unordered_map<QString, std::unique_ptr<DashAnalysisModelContext>, QStringHash> m_contexts; // :54
};
```

역할 두 가지가 한 클래스에 섞여 있다: (1) **로드/캐시**(`getOrLoad`, `get`), (2) **활성 컨텍스트·렌더러 조작**(`setActiveContext`, `updateActor`, `activeActor`). 이 혼재가 D3 문제의 일부다(<5>절 4번).

### 한눈 비교

| | DashAnalysisModelContext | DashAnalysisModelContextRegistry |
|---|---|---|
| 정체 | 모델 1개의 데이터 묶음 | 경로→Context 캐시 관리자 |
| 개수 | 로드된 모델 수만큼 여럿 | 프로세스에 1개(싱글톤, magic static) |
| 소유 | Registry 의 `unique_ptr` 가 소유 | Context 들을 `m_contexts` 로 소유 |
| 내부 락 | 없음 | `m_mutex`(맵 조작만) |
| 비유 | 실제 책 한 권 | 도서관 프런트(대출/로드 목록 관리) |

---

## 4. `try_emplace` vs `emplace` (질문 7)

둘 다 `map` / `unordered_map` 에 요소를 **넣으려 시도**하는 함수다. 차이는 **키가 이미 있을 때**의 동작이다.

| | `emplace(key, args...)` (C++11) | `try_emplace(key, args...)` (C++17) |
|---|---|---|
| 키가 **새로움** | value 생성·삽입 | value 생성·삽입 (동일) |
| 키가 **이미 존재** | value 노드를 **일단 생성했다가 파괴** 가능 → 넘긴 인자가 **move 로 소비될 수 있음** | **아무것도 안 함** — value 생성 X, 인자 move X |

즉 `emplace` 는 "중복이면 만들었다 버린다"라서 그 과정에 `std::move(x)` 로 넘긴 `x` 가 **이미 옮겨져 껍데기(moved-from)** 가 될 수 있다. `try_emplace` 는 "**중복이면 손도 안 댄다**"를 보장한다.

### D3 dangling 버그와의 연결

`getOrLoad` 의 꼬리 부분이 정확히 이 함정을 밟는다:

```cpp
// controller/DashAnalysisModelContextRegistry.cpp:40-46
DashAnalysisModelContext* raw = ctx.get();      // (1) 방금 로드한 객체 주소를 미리 저장
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_contexts.emplace(canon, std::move(ctx));  // (2) 경합 상대가 먼저 넣었으면 키 중복
}
return raw;                                       // (3) ← 죽은 객체를 가리킬 수 있음
```

락 밖에서 파일을 파싱하는 수 초 사이 **다른 스레드가 같은 키를 먼저 삽입**하면, (2)의 `emplace` 는 실패한다. 그런데 실패 전에 `std::move(ctx)` 로 소유권이 임시 노드로 넘어가 그 노드가 **파괴되면서 Context 를 `delete`** → (1)에서 떠 둔 `raw` 는 **파괴된 객체를 가리킨 채**(3)에서 반환된다. 단일 스레드에서는 경합이 없어 발현하지 않지만, **코드 형태로는 이미 심긴 지뢰**다.

`try_emplace` 로 바꾸면 키 중복 시 **move 가 아예 안 일어나** `ctx` 가 살아 있어 이 dangling 이 사라진다(이슈가 말한 "안전핀"). 다만 **완전한 수리는 반환값도 맵이 소유한 요소로 바꿔야** 한다:

```cpp
auto [it, inserted] = m_contexts.try_emplace(canon, std::move(ctx));
return it->second.get();   // 새로 넣었으면 내 ctx, 이미 있으면 캐시본 — 어느 쪽이든 맵이 소유한 살아있는 요소
```

미리 떠 둔 `raw` 를 반환하는 현 방식 자체가 취약점이라, **`try_emplace` + iterator 요소 반환**이 정석이다. 참고로 [#203](203-2-worker-preconditions-analysis.md) 은 이 `try_emplace` 를 "즉효 1줄 안전핀"으로 두고, **이중 파싱까지 없애는 근본 처방**(경로별 `shared_future` 로 로드 1회 보장)은 별도로 둔다(<5>절).

---

## 5. D3 — DashAnalysisModelContext 접근 규약의 문제 (질문 8)

한 문장으로: **"누가(어느 스레드) 어떤 방식으로 Context 에 접근한다"는 규약이 아예 없다**는 것 자체가 문제다. 워커가 붙으면 이 부재가 네 갈래로 터진다:

1. **이중 파싱** — `getOrLoad` 는 `락 → 캐시 확인 → 언락 → (락 밖에서 수 초 파싱) → 락 → emplace` 구조라, 두 스레드가 동시에 캐시 miss 하면 **같은 파일을 두 번 파싱**(수 초 × 2).
2. **dangling 반환** — 위 경합 + `raw` 선저장(<4>절) → **죽은 컨텍스트 반환**. 지금도(단일 스레드 정상 경로만 아니면) 잠재.
3. **읽기-변이 레이스** — 배치(워커)가 `setFeConditionValue` 로 캐시 인스턴스를 변이하는 동안 메인 위젯이 **같은 인스턴스**의 파트 트리를 순회. Context 내부 락이 0 이라 컨테이너 리해시/재할당 중 읽기 = UB.
4. **워커발 렌더러 접근** — 워커의 `getOrLoad` 가 `setActiveContext → updateActor` 로 이어지면 **렌더러 조작이 워커 스레드에서** 실행 → D5(GUI/VTK 는 메인 스레드 전용) 위반. 로드 책임과 렌더 책임이 한 클래스에 있어서 생기는 결합.

즉 근본 원인은 (a) **로드 1회 보장 없음**, (b) **읽기/변이의 스레드 경계 규칙 없음**, (c) **데이터 로드와 렌더러 조작(`updateActor`)이 한 클래스에 혼재**. 처방도 두 층이다:

- **로드 경합(코드로)**: `try_emplace` 안전핀(즉효) → 경로별 `shared_future<Context*>` 로 "첫 스레드만 파싱, 나머지는 같은 future 대기"(이중 파싱·dangling 원천 제거).
- **접근(소유권 규약으로)**: "**컨텍스트 심층 접근(read/변이/export)은 RW 직렬 풀에서만**", 메인(위젯·렌더)은 **읽기 전용 스냅샷**(값 복사 요약)만 받음, `updateActor` 계열엔 **메인 스레드 assert** 부착.

한 줄 답: **워커 없이도 이미 dangling·이중 파싱 소지가 있고, 워커가 붙으면 읽기-변이·렌더러 경계까지 4중으로 깨지는데 이를 통제할 "접근 규약"이 부재한 것**이 D3 의 문제다.

---

## 6. 전역 `std::cout` rdbuf 스왑 (질문 2, 9 — 통합)

두 질문("cout rdbuf 스왑" / "전역 cout rdbuf 스왑")은 같은 것이라 함께 답한다. 뒤 질문의 "전역"이 핵심 포인트다.

### rdbuf 란

`std::cout` 은 **프로세스 전역** `std::ostream` **하나**다. 내부에 실제 입출력을 수행하는 `std::streambuf`(버퍼) **포인터**를 들고 있다.

- `cout.rdbuf()` (인자 없음) → 현재 streambuf 포인터를 **반환**.
- `cout.rdbuf(newBuf)` → streambuf 를 `newBuf` 로 **교체**하고 이전 것을 반환.

"**cout rdbuf 스왑**" = cout 의 출력 버퍼를 잠깐 다른 것(보통 널 싱크)으로 갈아끼웠다가 되돌리는 기법. 시끄러운 라이브러리의 콘솔 출력을 잠시 삼키려는 용도다. [#203](203-2-worker-preconditions-analysis.md) D4 가 인용한 코드:

```cpp
// (#203 인용본 — 시끄러운 reader.Update() 로그를 잠깐 삼키려는 의도)
std::streambuf* coutBuf = std::cout.rdbuf();     // 원본 저장
std::ostringstream nullStream;                    // 지역 변수 (스코프 끝나면 파괴됨)
std::cout.rdbuf(nullStream.rdbuf());              // 널 싱크로 스왑 — 프로세스 전역 상태 변이
bool updateResult = reader.Update();              // 수 초 파싱 (throw 가능)
std::cout.rdbuf(coutBuf);                          // 원본 복원
```

### "전역"이 왜 문제인가

cout 은 프로세스에 하나뿐이라, 이 스왑은 **이 함수/이 스레드만이 아니라 프로세스 전체**의 cout 에 영향을 준다. 그래서 세 가지가 터진다:

1. **다른 스레드 출력까지 삼킴** — 스왑 구간 동안 무관한 스레드의 **정당한 cout 출력도 널 싱크로 사라진다**(전역이므로).
2. **예외 시 dangling(단일 스레드에서도 잠재 버그)** — `reader.Update()` 가 throw 하면(이 함수는 throw 를 상정해 try-catch 로 감싸여 있다) **복원 두 줄을 건너뛰고** catch 로 점프한다. 스택 해제로 지역 변수 `nullStream` 이 파괴되고, `std::cout` 은 **파괴된 streambuf 를 가리킨 채** 남는다 → 이후 프로세스 어디서든 cout 출력 시 UB.
3. **워커 투입 시 save/restore 인터리브** — 두 스레드가 저장/복원을 엇갈리면, 한쪽이 **널 싱크를 "원본"으로 저장**해 복원해 버려 → 파싱이 끝났는데도 cout 이 곧 파괴될 널 싱크를 영구히 가리킴(로그 영구 유실 + 2번의 dangling).

### 처방

| 방식 | 요지 | 판정 |
|---|---|---|
| A. 라이브러리 자체 로그 억제 API | 원인 지점에서 끄기 — 전역 상태 무접촉 | **1순위**(API 존재 시) |
| B. 앱 시작 시 전역 1회 널 싱크 고정(복원 없음) | GUI 앱은 콘솔이 없으니 스왑·복원 자체를 없앰. **정적 수명 싱크라 dangling 불가** | A 부재 시 채택 |
| C. RAII 가드 + 전역 뮤텍스로 스왑 유지 | 예외 안전은 되나 "타 스레드 출력 삼킴" 부작용 잔존 + 락 추가 | 기각 |

D4 는 다른 4건과 의존성이 없고 규모가 가장 작으며 이미 잠재 버그라, 원래 "즉시 착수" 권장 항목이었다. (그리고 실제로 그 사이 제거된 것으로 보인다 — <8>절.)

---

## 7. 서브태스크 "e" 가 뭐야 (질문 10)

"D5 규약은 **e 의 모든 Job 에 동시 적용**"의 `e` 는 **W10 작업을 쪼갠 서브태스크 중 하나**다. 요약표([205-1-w6-w10-ticket-summary](205-1-w6-w10-ticket-summary.md))가 글자↔티켓을 명시한다:

| 서브태스크 | 티켓 | 내용 | 스레드 생성? |
|:--:|:--:|---|:--:|
| a~c (외부 프로세스 축) | #207~#210, #212 등 | ProcessJob 추출·파일 폴링 제거·데몬 비동기화 | ✗ (스레드 안 만듦) |
| **d** | **#213** | **WorkerJob 투입 전 공유상태 선결조건 D1~D5 해소 게이트** — **이 [#203](203-2-worker-preconditions-analysis.md) 문서가 그 d 의 설계 명세** | ✗ (본 티켓은 스레드 미생성) |
| **e** | **#214** | **`WorkerJob`(QtConcurrent + QFutureWatcher → Job 번역) + 서브시스템 직렬 풀 2종(모핑·RW, `maxThreadCount=1`) 인프라 신설 + 파일럿 1건(DOE 배치 모핑) 워커화** | ✅ **여기서 두 번째 스레드가 실제로 생김** |
| f | #215 | 워커 후보 순위 2~6 순차 Job 화 + dfsxml 루프 전환 + 잔여 `processEvents` 제거 | ✅ |

그래서 그 문장의 뜻은:

- **d(#213)** = 게이트. 스레드를 넣기 **전에** D1~D5 를 정리하는 선결 조건 단계(이 [#203](203-2-worker-preconditions-analysis.md) 이 그 설계).
- **e(#214)** = 게이트를 통과한 뒤 **실제 워커 Job 을 만드는 단계**. 두 번째 스레드가 여기서 처음 등장한다.
- **"D5 규약은 e 의 모든 Job 에 동시 적용"** = D5(GUI/VTK 스레드 규칙)는 코드 한 줄 고치는 diff 가 아니라 **규약(집행 가능한 규칙 + assert)** 이라서, 실제 Job 이 생기는 **e 단계의 모든 Job 에 빠짐없이 적용**해야 한다는 의미다.
- 착수 순서: **d(#213) → e(#214) → f(#215)**.

---

## 8. 현재 dev 코드 대조 (2026-08-01 확인)

이 문서의 코드 근거는 [#203](203-2-worker-preconditions-analysis.md) 재검증(2026-07-28, `4388c57`) 이후의 현재 dev(`22e33e3` 시점)에서 다시 확인했다. 요점만:

| 항목 | 현재 상태 | 근거 |
|---|---|---|
| D1 `Mgr()` 수동 lazy-init | **현존** | `controller/DashManager.cpp:208-215` |
| D1 `Destroy()` null-out 없음 (double-free 가능) | **현존** | `controller/DashManager.h:65-67` — `delete m_instance;` 만 |
| D1 Registry magic static 선례 | 현존 | `controller/DashAnalysisModelContextRegistry.cpp:10-13` |
| D3 `getOrLoad` `emplace` + `raw` 반환 dangling | **현존** | `...Registry.cpp:40-46` (컨테이너는 `unordered_map`, `...Registry.h:54`) |
| D4 `cout` rdbuf 스왑 | **이미 제거됨** | `controller/DashAnalysisModelContext.cpp` 및 repo 전역에서 `rdbuf` 스왑 grep 0 — 재검증 이후 리팩터로 소멸 |

→ 개념 학습 목적에는 D4 설명도 그대로 유효하되, **"지금 고쳐야 할 코드"로 오해하지 말 것**. D1·D3 은 현재도 이슈 분석대로 남아 있다.

## 참고 자료

- 내부: [#203](203-2-worker-preconditions-analysis.md)(선결 조건 D1~D5 원 분석) · [205-1-w6-w10-ticket-summary](205-1-w6-w10-ticket-summary.md)(W6·W10 티켓 요약 — 서브태스크 d/e 정의) · 관련 티켓 #213(d)·#214(e)·#215(f)
- 코드 앵커: `controller/DashManager.{h,cpp}` · `controller/DashAnalysisModelContextRegistry.{h,cpp}` · `controller/DashAnalysisModelContext.{h,cpp}`
- 외부 개념: C++ 표준 — 함수 지역 static 의 초기화 직렬화(`[stmt.dcl]/4`, C++11) · `map`/`unordered_map` 의 `emplace` vs `try_emplace`(C++17) · `std::ios::rdbuf` / `std::streambuf` · `std::atexit` 등록·실행 순서 / Qt — QObject 스레드 어피니티·QWidget 메인 스레드 제약 / VTK — 파이프라인 객체 스레드 비공유(참조 카운트만 원자적)
