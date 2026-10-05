# 프로젝트 → AnalysisLauncher — 저장 구조 설계 · 구현 배선

> 관련 Issue: #239
>
> **이 문서는 자료 설계가 아니라 배선 설계다.** 무엇을 저장할지는 아래 문서가 이미 정했고, 여기서는 **그것이 현행 코드의 어느 함수에 어떤 순서로 들어가는지**를 앞단 동선 6단계에 한정해 적는다.
>
> * [Project-Store-Design-Definition-Version-Minimal](Project-Store-Design-Definition-Version-Minimal.md) — **자료·판정 설계의 정본.** 목적 3항목(매니페스트 · 정의 버전 · 상위 의존성)의 스키마 · 지문 규칙 · `consumed` 계산 · 배지 2종이 전부 그쪽에 있다. 이 문서는 그 설계의 목적지를 바꾸지 않는다
> * [Project-Store-Design-Alpha-Minimal](Project-Store-Design-Alpha-Minimal.md) — 같은 계열의 형제안(지문 없음 · `instances[]` 색인 있음). 이 문서는 정본 쪽을 따르므로 `instances[]` 를 만들지 않는다
> * [Project-Store-Design-Dependency-State-Display](Project-Store-Design-Dependency-State-Display.md) — 배지의 화면 층
> * [Code-Map-User-Flow-Geometry-Parameterization-Morphing](Code-Map-User-Flow-Geometry-Parameterization-Morphing.md) · [Code-Map-User-Flow-Geometry-Parameterization-CAD](Code-Map-User-Flow-Geometry-Parameterization-CAD.md) · [Code-Map-User-Flow-Condition-Parameterization](Code-Map-User-Flow-Condition-Parameterization.md) · [Code-Map-User-Flow-Analysis-Launcher](Code-Map-User-Flow-Analysis-Launcher.md) — 앞단 4모듈의 동선 실측
> * [Project-Manifest-2-Active-Cursor-Data-Coupling](Project-Manifest-2-Active-Cursor-Data-Coupling.md) — **2.3 의 사실관계 분석.** 커서 API 21건 + 시그널 payload 1건에서 데이터 결합 9좌표를 적시하고, 출처를 바꾸지 않고 뗄 수 있는 7좌표에만 처분을 단다. 유지 12건 · 조회 20건(부속 2 + 대상 아님 18). deck 출처 배선은 후속 설계 소유
>
> 실측 기준: `dev` @ `7024e04`. 위 설계 문서 셋은 `4c7608e` 기준이라 **좌표가 갈리는 곳이 있다 — 0.3 에 전수 정리했다.** 빌드·실행 검증 없음, 정적 근거만.

> ## ⚠ 문서 상태: 구상 — 확정 아님
>
> 팀 합의 전 · 착수 승인 전. 여기의 좌표는 실측이고 **배선 판정은 제안**이다.

## 개요

**요청 5항목 중 1·2·3 만 넣고 4·5 를 후속으로 뗐으며, 그 셋을 다시 파이프라인 앞단으로 한 번 더 잘랐다.**

| | 항목 | 이 문서 |
|---|---|---|
| 넣는다 | 1. 프로젝트 매니페스트 — 해석 기준 모델을 정의하는 객체와 파일 | 2.1 · 2.2 |
| 넣는다 | 2. 모듈의 정의·버전 기록과 ID 부여 | 2.4 · 2.5 |
| 넣는다 | 3. 모듈 Set 별 상위 의존성 기록과 최신성 확인 | 2.3 · 2.6 · 3절 |
| **뗀다** | 4. 정의와 실행 상태가 한 파일에 있는 구조 해소 (도구 되쓰기 · 폴링 포함) | 6절 — 절단선만 긋는다 |
| **뗀다** | 5. 프로젝트 상태를 하나의 root 에 모듈 단위로 분해 | 6절 — 0건 건드린다 |

동선 범위는 **프로젝트 생성 → [Add File] → 파싱 → Geometry Parameterization → Condition Parameterization → Analysis Launcher** 여섯이고, DataPreprocessor 이하 넷은 범위 밖이다.

**앞단으로 자르면 판정 설계가 절반으로 준다.** Geometry·Condition 은 실행이 없어 지문 제외 키가 **비어 있고**, 계보 크기가 1이며, `Stale` 해소가 재저장 한 번이다. 실행 있는 모듈은 AnalysisLauncher 하나뿐이다.

**그러나 승격 한 항목만은 앞단으로 자를 수 없다**(4절). 열기가 `configs/` 전량을 훑으므로 모듈별로 나눌 자리가 없다.

**6.2 는 이 배선을 두 개념으로 되짚은 것이다** — "다음 모듈이 참조하는 정보를 생산자 산출에 박제" · "복구용 정의 요소도 산출에 포함". 결론은 **앞단에 execution 엣지가 0건이라 충돌이 없고**, W4 의 `consumed` 범위 한 항목만 조건부다.

---

## 0. 범위와 전제

### 0.1 동선 6단계

```
[1] 프로젝트 생성
   │   DashProjectManager::CreateNewProject
   │   .{name}.dproj/configs/ 까지 mkpath
   ▼

[2] [Add File] — 기준 입력 등록
   │   DashMainWindow::onAddFileClicked
   │   프로젝트 루트로 복사 (.stli 는 부모 폴더째)
   ▼

[3] 파싱 — 파일 트리에서 Load 버튼 클릭
   │   DashMainWindow::onProjectFileLoadClicked
   │   registry.setActiveContext(filePath) 가 파싱을 유발
   ▼

[4] Geometry Parameterization — Set 생성 후 DV 확정
   │   Morphing 또는 CAD. 정의 = DV-Geometry + Morphing.*
   ▼

[5] Condition Parameterization — Set 생성 후 DV 확정
   │   정의 = DV-Condition
   ▼

[6] Analysis Launcher — 상위 둘을 고르고 DOE 설정
       정의 = DOE configuration + input_files[]
       여기서 처음으로 definition 엣지가 선다
```

### 0.2 이 문서가 만드는 것 — 전수

| # | 신설물 | 자리 | 근거 |
|---|---|---|---|
| 0 | (신설 아님) 전역 ID 2종 | `dash::core::UUID` — **이미 프로젝트에 있는 타입**(1.3) | `QUuid` 를 도입하지 않는다 |
| 1 | `.dproj/reference.json` | 프로젝트 루트 숨김 폴더 | 유일한 신설 **파일** |
| 2 | Reference 스토어 (접근자) | `model/` 또는 `controller/` — `DashProject` 옆 | 라이터 1곳 = 프로젝트 컨트롤러 |
| 3 | 정의 저장 헬퍼 (접근자) | 동상 | 정의 라이터 전량이 통과 |
| 4 | SM 최상위 키 6개 | 기존 `configs/{Module}_{Set}.json` | `$schema` · `id` · `module` · `variant` · `definitionVersion` · `upstream` |

**정의 본문은 한 줄도 건드리지 않는다.** `DV-Geometry` · `DV-Condition` · `Morphing.*` · `DOE configuration` · `input_files[]` 전부 현행 스키마 그대로다.

### 0.3 실측 기준 갱신 — 기반 문서와 갈리는 4건

기반 설계 셋은 `4c7608e` 기준이고 이 문서는 `7024e04` 다. **1\~4 는 재실측이고 5·6 은 결정이다.** 첫째가 배선 판정을 실제로 바꾼다.

| # | 기반 문서의 기술 | `7024e04` 실측 | 영향 |
|---|---|---|---|
| **1** | 열기 시 파일명 판정의 자리 = `DashProject::loadSetsFromConfigs()` | **그 함수는 호출부가 0곳이다.** 열기 경로의 실체는 `DashProject::restoreExistingModules()`(`model/DashProject.cpp:1213-`)이고 유일한 호출부가 `controller/DashProjectManager.cpp:122` 다. 둘은 같은 접두사 판정을 하는 근친 중복이다 | **승격을 붙일 자리가 바뀐다**(4절). 기반 문서가 지목한 함수를 고치면 동작이 변하지 않는다 |
| 2 | variant 검출기 2종 (`detectGeometryVariant` · `detectBuilderVariant`) | **4종** — `detectRunnerVariant`(`:673`) · `detectLauncherVariant`(`:690`)가 늘었다. 넷 다 `variant` 키 1순위 + 이름 접미사 폴백 구조가 같다 | 승격이 써 넣어야 할 키가 늘고, **앞단만 자를 수 없는 근거**가 된다(4절) |
| 3 | `[Add File]` = `view/DashMainWindow.cpp:2106-2189`, 필터 `:2118` | `:2114-2197`, 필터 `:2126-2127`. 필터 12종은 동일 | 좌표만 |
| 4 | AL 의 definition 엣지 = 미기록 | **이미 존재하되 config 파일명 배열이다** — `DOE configuration.Selected Design Variables` 는 `[condition, geometry]` 고정 2원소이고(`model/DashDoeConfigManager.cpp:111-115`), 리더 4곳이 각자 부분문자열로 모듈을 되짚는다 | 2.6 — "신설" 이 아니라 **조인 키 교체**다 |
| **5** | 전역 ID = `QUuid` 접두사 + 12-hex 난수 · "레포에 `QUuid` 사용 0건이라 첫 사용" | **`QUuid` 를 쓰지 않는다.** 프로젝트에 이미 ID 타입이 있다 — `dash::core::UUID`(`CoreLib/UUID.hpp`)가 `AnalysisModelIdentity.json` 의 `uuid` 값이고 RW 세션의 symbol uuid 전량(content · part · FE condition)이 이 타입이다(`controller/DashRwSession.cpp:1086-1135`) | **1.3 — 발급 함수와 형식이 갈린다.** 12-hex 절단도 함께 기각된다 |
| **6** | 지문 값 = `"sha256:1c07af…"` (`algo:` 접두사) | **접두사를 벗긴다 — bare hex 64자.** 현행 코드가 bare 를 만들고 bare 로 저장하며(`controller/DashRwSession.cpp:1059`·`:1136`) 접두사 선례가 0건이다 | **2.2 — `references[].fingerprint` · `definitionVersion` · `consumed` 값 전부.** Identity 와 문자열 동등 비교로 대조된다 |

---

## 1. 앞단에서 서는 형태

### 1.1 `reference.json` 항목 — 앞단은 A·B·C 셋

기반 문서 1.2 의 형태 4종 중 `material`(D)만 앞단에 없다 — FE-safe 재료 설정이 AL 실행 준비 단계라 이 동선 밖이다.

| 형태 | `kind` | `files` | 앞단에서 누가 드나 |
|---|---|---|---|
| **A** | `fe` | `deck` 1개 (`.inp`·`.dat`·`.dfsxml`) | Geometry Morphing · Condition · AL(Morphing 경로). **대부분이 이것이다** |
| **B** | `cad` | `part`(`.prt`) + `template`(`.wbpj`) | Geometry CAD · AL(CAD 경로) |
| **C** | `fe` | `template`(`.stli`) | AL(FE-safe 경로) |

### 1.2 SM 최상위 키 — 앞단 4인스턴스의 실제 값

```json
{
  "$schema": 1,
  "id": "inst_4d19b2a7-0e55-5c31-8f2a-1b04de9b41e0",
  "module": "AnalysisLauncher",
  "variant": "Init",
  "definitionVersion": "1c07af…",
  "upstream": {
    "references":  ["ref_9b41e0c3-f2a1-5d0a-9c6f-2e8b5a1d4c70"],
    "definitions": ["inst_7f3a2c1b-04de-5a17-b3e9-6c2d8f014b55",
                    "inst_1e55da62-c9f7-5b8e-a04c-3d7f1e2a6809"],
    "executions":  [],
    "consumed": {
      "inst_7f3a2c1b-04de-5a17-b3e9-6c2d8f014b55": "1c07af…",
      "inst_1e55da62-c9f7-5b8e-a04c-3d7f1e2a6809": "44b2d0…",
      "ref_9b41e0c3-f2a1-5d0a-9c6f-2e8b5a1d4c70":  "9b41e0…"
    }
  },

  "DOE configuration": { },
  "input_files": [ ]
}
```

**ID 형식은 접두사 + 표준 36자다** — 절단하지 않는다(1.3). **지문 형식은 bare hex 64자다** — `sha256:` 접두사를 붙이지 않는다(2.2).

| 인스턴스 | `references[]` | `definitions[]` | `executions[]` | `consumed` 크기 | 지문 제외 키 |
|---|---|---|:---:|:---:|---|
| Geometry · Morphing | `ref_` deck | — | — | 1 | **없다** |
| Geometry · CAD | `ref_` part | — | — | 1 | **없다** |
| Condition | `ref_` deck | — | — | 1 | **없다** |
| AnalysisLauncher | `ref_` — variant 별로 갈린다(2.6) | `inst_` Geo · `inst_` Cond | — | 3 | `DOE Table` · `DOE Analysis` |

**앞단 4 중 3 이 제외 목록 없이 전문 해시다.** 지문 계산기의 경로 패턴 제거 로직은 AL 한 곳에서만 실제로 도는데, 그래도 **처음부터 넣어야 한다** — 빼면 AL 이 DOE 를 80케이스 돌리는 동안 하류가 실행 내내 낡은 것으로 보인다(기반 문서 1.4).

**AL 의 `executions[]` 가 비어 있다.** 앞단에는 상류 산출을 먹는 모듈이 없다. execution 엣지의 첫 소비자는 DataPreprocessor 이고 그것이 범위 밖이므로, **이 문서가 배선하는 엣지는 reference 와 definition 둘뿐이다.**

### 1.3 ID 2종 — `dash::core::UUID`

**기반 문서 셋은 `QUuid` 를 지목했으나 이 문서는 `dash::core::UUID` 를 쓴다**(0.3-5). 근거는 새 타입을 고르는 것이 아니라 **이미 이 프로젝트의 ID 어휘라는 것**이다 — `AnalysisModelIdentity.json` 의 `uuid` 값이 이 타입이고(`controller/DashRwSession.cpp:1125-1135`), RW 세션의 symbol uuid 전량이 이 타입이며(`:43` · `:46` · `:52` · `:225`), 헤더가 이미 링크에 들어 있다(`controller/DashRwClient.h:17` — `#include <CoreLib/UUID.hpp>`). `QUuid` 를 쓰면 **한 프로젝트에 ID 표현이 두 벌 생긴다.**

#### 발급 — 두 ID 가 다른 함수를 쓴다

| ID | 발급 | 시점 | 근거 |
|---|---|---|---|
| `ref_` | `UUID::from_namespace(ns_ref, 프로젝트상대경로)` | `[Add File]` 등록 · 승격 | **경로가 곧 유일 키다** — [Add File] 은 이름을 바꾸지 않고(`view/DashMainWindow.cpp:2176`) 같은 이름이면 덮어쓸지 묻는다(`:2178-2185`). 같은 경로에 항목이 둘일 수 없다 |
| `inst_` | `UUID::from_namespace(ns_inst, "{Module}_{Set}")` | Set 생성 · 승격 | **승격이 멱등해진다** — 아래 |

**둘 다 v5(네임스페이스)이고 난수 발급(`create()`)을 쓰지 않는다.** 네임스페이스 UUID 는 하드코딩 상수 2개이고, **같은 패턴의 선례가 같은 파일에 있다** — `rwResolveContentIdentity` 가 하드코딩 `ns` + canonicalPath 로 deck 의 content uuid 를 만든다(`controller/DashRwSession.cpp:1105-1108`).

#### 왜 난수가 아니라 멱등인가

**기반 문서 3.5 의 "되돌리기가 싸다" 가 난수 발급에서는 성립하지 않는다.** 그 문서는 "`reference.json` 을 지우고 키를 무시하면 현행 경로로 복귀한다" 고 적었는데, 되돌린 뒤 다시 승격하면 —

| 발급 | 재승격 결과 |
|---|---|
| 난수 (`create()`) | **새 ID 가 난다.** 그 사이 config 에 남아 있던 `upstream`·`consumed` 가 전부 옛 ID 를 가리켜 **소비자 전량이 `✕ Broken`** 이 된다. 되돌리기가 파괴적이다 |
| 네임스페이스 | **같은 ID 가 난다.** 엣지가 그대로 살아 있다 |

`upstream` 은 config 파일 안에 살고 `reference.json` 은 별도 파일이므로, **둘의 수명이 갈리는 순간이 실제로 있다** — 되돌리기뿐 아니라 `reference.json` 손상·부분 복원·프로젝트 복사(`DashProjectManager::SaveProjectAs` `:169-`)가 전부 같은 자리다. 멱등 발급이면 그 전부가 무해하다.

#### `ref_` 는 Identity 의 content uuid 와 같은 값인가 — 아니고, 통일하지 않는다

**지금 안에서는 다르다.** v5 는 `(ns, name)` 쌍의 함수인데 **둘 다 갈린다.**

| | Identity content uuid | `ref_` |
|---|---|---|
| `ns` | 하드코딩 `f3d1c9a2-7b4e-4d0a-9c6f-2e8b5a1d4c70`(`controller/DashRwSession.cpp:1105-1106`) | `ns_ref` — 별개 상수 |
| `name` | **canonical 절대경로**(`:1108` · `:1386`) | **프로젝트 상대경로** |

**통일 자체는 가능하다.** `ref_` 를 `from_namespace(ns_identity, canonicalPath)` 로 발급하면 같은 값이 나오고, [Add File] 시점에 파일이 이미 복사돼 있어 canonical 경로를 얻을 수 있다. 얻는 것도 실재한다 — 조인 키가 하나가 되고 Identity 흡수 경로가 열린다.

**막는 것은 하나다 — Identity 의 키가 절대 canonical 경로다.**

```
[T0] 등록          ref_  = f(ns, /old/proj/bracket.inp)   ← reference.json 에 저장
                   content uuid = 같은 값                   ← Identity 에 저장
                   두 값이 같다
   ▼

[T1] 프로젝트 이동  reference.json 은 값을 들고 따라간다 — ref_ 불변
                   Identity 는 models 키가 옛 절대경로라 미스
                   → pathUuid 를 새 경로로 재계산해 새 uuid 발급
   ▼

[T2] 결과          두 값이 갈린다. "같다" 는 계약이 조용히 깨진다
```

**처음엔 맞다가 나중에 틀리는 계약이 가장 나쁘다.** 그 계약에 기대는 코드가 생기면 이동 후 무증상으로 어긋난다. 그래서 **어긋날 수 있는 "같음" 보다 명시적 "다름" 을 계약으로 둔다.**

통일하려면 **Identity 의 키를 프로젝트 상대경로로 먼저 바꿔야 하는데**, Identity 는 프로젝트 없이도 서야 하고(`storePath` 빈 경우 `:1110-1112`) 프로젝트 밖에서 연 deck 도 담으므로 상대경로가 없는 항목이 남는다. **키 규칙을 안/밖 둘로 가르면 같은 파일이 두 이름을 갖는다** — 프로젝트에 넣기 전과 후.

**그리고 이 배포에는 통일의 이득이 도착하지 않는다.**

| 통일의 이득 | 이 배포에서 |
|---|---|
| 두 파일을 ID 로 조인 | **필요 없다.** 2.2 의 결정은 GUI 가 동결 지문을 **파라미터로 주입**하는 것이라 조회 자체가 없다 |
| Identity 흡수 | **후속이다** — 미결 14 |

대가는 둘 더 있다. **`ref_` 재발급이 symbol 바인딩을 끌고 간다** — 값이 같으면 Reference 를 새 것으로 취급하는 순간 content uuid 도 갈려 persisted symbol uuid 가 무효화된다. 그리고 **노출이 늘어난다** — `rwFileSha256` 에 더해 `ns` 상수와 발급 경로까지 RW 밖으로 꺼내야 한다.

**판정: 이 배포는 분리, 통일은 Identity 키 규칙 재설계와 한 묶음으로 후속**(미결 14). 상대경로를 고른 것이 그 후속의 방향이기도 하다 — **프로젝트를 옮겨도 `ref_` 가 불변**이고, 그것이 Identity 가 지금 갖지 못한 성질이다.

#### 형식 — 접두사 + 표준 36자, 절단하지 않는다

기반 문서는 `toString(QUuid::Id128).left(12)` 로 12-hex 절단을 정하고 근거로 "전체 UUID(41자)는 맵 키·로그 본문으로 읽히지 않는다" 를 들었다. **절단하면 이 타입을 쓰는 이유가 사라진다.**

| 절단 시 잃는 것 | |
|---|---|
| `from_string()` 왕복 | `Result<UUID>` 로 파싱 실패가 타입에 드러나는 것이 매니페스트를 손으로 고칠 수 있는 파일로 두는 전제에서 필요하다. `QUuid::fromString` 은 실패 시 null 을 조용히 돌려준다 |
| `version_number()` · `is_nil()` | 손상된 값과 미발급 값을 구별하는 수단 |
| `AnalysisModelIdentity.json` 과 같은 형태 | 두 파일의 uuid 를 사람이 대조할 수 없게 된다 |
| 후속 이득 (아래) | v7 로 갈아탈 여지가 닫힌다 |

**접두사는 유지한다.** 배지 판정이 `consumed` 맵을 순회하며 **ID 접두사로 현재 값의 자리를 고르기** 때문이다 — `ref_` 는 `reference.json` 에서, `inst_` 는 config 에서 찾는다. 접두사를 빼려면 `consumed` 를 종류별 맵 둘로 갈라야 하고 그것은 기반 문서의 스키마 변경이다.

#### v7 은 지금 쓰지 않는다 — 가용성 미확인

CoreLib 의 UUID v7 API(`from_current_time()` · `from_timestamp()` · `timestamp()` · `Presentation` · `to_string(Presentation)` · `operator<=>` · `std::formatter`)는 **`feat/uuid-v7` 브랜치의 최근 3커밋이고 `origin/main` 에 없으며 태그도 없다.** GUI 는 CoreLib 을 소스가 아니라 벤더된 패키지로 링크하므로(`CMakeLists.txt:438-440` — `external/packages/core-lib/`), 실제 링크되는 판에 v7 이 있는지는 이 문서가 확인하지 못했다(8절).

**그래서 v7 에 의존하지 않게 설계한다.** 위 발급 둘은 전부 v7 이전부터 있는 API 다 — `from_namespace` · `from_string` · `to_string()` · `version_number()` · `is_nil()`.

v7 이 벤더되면 열리는 것 둘. **둘 다 후속 4·5번의 자리이지 이 문서의 자리가 아니다.**

| 후속 | v7 이 주는 것 |
|---|---|
| 4. 정의·실행 분리 — `exec_` 발급 | `from_current_time()` 이면 **실행 ID 자체가 생성 시각을 담는다**(상위 48bit). run 파일에 별도 timestamp 필드가 필요 없고 `timestamp()` 가 되돌려준다. byte 사전식 순서 = 실행 순서 |
| 5. 단일 root — `executions/{label}/` 의 `label` | `to_string(ReadableUtc)` 는 `YYYYMMDDTHHMMSS.mmmZ_{20-hex}` 이고 **Windows 파일명 금지 문자를 포함하지 않는다.** 사람이 읽고 정렬되며 `from_string()` 으로 원본 16 byte 를 복원한다 |

---

## 2. 동선별 배선

### 2.1 [1] 프로젝트 생성 — 빈 `reference.json`

| | |
|---|---|
| 현행 | `DashProjectManager::CreateNewProject` `controller/DashProjectManager.cpp:128-162`. `configs` 까지 `mkpath`(`:145`) → 숨김 속성(`:151`) → `SetProjectDirectory`(`:158`) |
| 신 | `:158` **직후** `reference.json` 을 빈 형태로 쓴다 |

```json
{ "$schema": 1, "references": [] }
```

**`:158` 뒤인 근거는 IOController 다.** `SetProjectDirectory`(`:39-66`)가 `DashIOController` 를 새로 세우고(`:63`) 그 객체가 configs·root 경로 접근자를 준다. 그 앞에 두면 경로를 문자열로 다시 조립해야 하고, 그것이 5절 경로 규약 불일치의 재생산이다.

**`OpenProjectFromFolder`(`:97-126`)에는 넣지 않는다.** 구프로젝트에 파일을 만드는 것은 승격의 일이고 승격은 4절이 담당한다.

### 2.2 [2] [Add File] — Reference 등록

**현행은 복사만 하고 아무 기록도 남기지 않는다.** `DashMainWindow::onAddFileClicked`(`view/DashMainWindow.cpp:2114-2197`)의 루프가 끝나면 하는 일이 파일시스템 트리 리프레시(`:2194-2196`)뿐이다.

| 등록 지점 | 좌표 | 대상 |
|---|---|---|
| `.stli` 폴더 복사 성공 | `:2166` (`copyDirectoryRecursively` 참) | 형태 C |
| 그 외 파일 복사 성공 | `:2187` (`QFile::copy` 참) | 형태 A · B 의 `part` |

발급하는 필드 다섯.

| 필드 | 값의 출처 | 비고 |
|---|---|---|
| `id` | `UUID::from_namespace(ns_ref, 프로젝트상대경로)` | 1.3. **`QUuid` 가 아니다** — 이 프로젝트의 ID 타입은 `dash::core::UUID` 이고 경로 기반이라 재등록·재승격이 멱등이다 |
| `label` | `fileInfo.baseName()` | |
| `kind` | 확장자 → `fe`\|`cad` | 아래 표 |
| `files` | 확장자 → 역할 맵 | 아래 표 |
| `origin` | `filePath`(`:2143` 의 루프 변수) | **현행이 복사 직후 버리는 값이다.** 등록 순간에만 손에 있다 |
| `fingerprint` | `rwFileSha256(destPath 의 canonical 형)` — **여기서 처음 계산된다** | 아래. canonical 로 고정하는 것이 계약이다 |

#### 지문은 이 시점에 "이미 있는 값" 이 아니다

**재사용되는 것은 함수이지 값이 아니다.** 둘을 가르지 않으면 [Add File] 이 공짜로 보인다.

| | `rwFileSha256` | `rwResolveContentIdentity` |
|---|---|---|
| 좌표 | `controller/DashRwSession.cpp:1030-1066` | `:1090-1146` |
| 하는 일 | 경로를 받아 스트리밍 sha256. `(size, mtime)` 메모이즈 | Identity 저장소 read-modify-write + uuid 해석 |
| `AnalysisModelIdentity.json` | **읽지도 쓰지도 않는다** | **이 함수가 만든다**(`:1140-1144`) |
| 처음 도는 시점 | 우리가 부르는 곳 | 파싱 — `DashRwSession::load`(`:1386`) |

**그래서 [Add File] 시점에 Identity 저장소가 없어도 무관하다** — `rwFileSha256` 은 그 파일을 참조하지 않는 순수 함수다. 새 프로젝트에서 `AnalysisModelIdentity.json` 은 **아직 존재하지 않고**, 동선 [3] 에서 deck 을 처음 열 때 생긴다.

```
[2] [Add File]
   │   destPath 로 복사
   │   rwFileSha256(destPath) — 캐시 콜드, 파일 전문 1회 읽기
   │   references[].fingerprint 에 저장하고 동결
   │   ※ AnalysisModelIdentity.json 은 아직 없다
   ▼

[3] 파싱 — setActiveContext → DashRwSession::load
       rwResolveContentIdentity(fi.canonicalFilePath(), configsDir)
       그 안에서 rwFileSha256 이 또 1회
       AnalysisModelIdentity.json 이 여기서 생긴다
```

**비용은 감당 가능하다.** [Add File] 은 그 순간 같은 파일을 복사하느라 이미 I/O 바운드이므로 해시 1회가 새 병목을 만들지 않는다. 등록 1회 계산 후 동결이라 이후에는 돌지 않는다.

**다만 같은 파일이 두 번 해싱된다.** 메모 캐시 키가 raw `QString` 경로인데(`:1037` · `:1045`) [Add File] 은 `destPath`(`QDir::filePath` — 비정규화)를, 파싱은 `fi.canonicalFilePath()` 를 넘긴다. 문자열이 다르면 캐시가 빗나간다. **키를 canonical 로 정규화하면 [3] 이 stat 1회로 접힌다** → 미결 13.

**함수 노출이 필요하다.** `rwFileSha256` 은 `DashRwSession.cpp` 의 파일 `static` 이라 `DashMainWindow` 에서 부를 수 없다 — 이것이 이 동선에서 유일한 기존 유틸 승격이다.

#### 두 지문은 같은 값인가

**다이제스트는 같고 저장 문자열과 갱신 규칙이 갈린다.** `rwResolveContentIdentity` 는 자기 해시를 따로 만들지 않고 **같은 함수를 부른다**(`:1099`).

| | `reference.json.fingerprint` | `AnalysisModelIdentity.json.models[].sha256` |
|---|---|---|
| 산출 | `rwFileSha256` | **같은 함수** (`:1099`) |
| 다이제스트 | 같다 — 같은 내용이면 경로 문자열과 무관하게 동일 | 같다 |
| 저장 문자열 | **bare hex 64자** — 이 문서의 결정(아래) | **bare hex** — `toHex()` 결과 그대로(`:1059` · `:1136`) |
| 갱신 | 등록 1회 후 **동결** | **매 open 마다 현재 해시로 덮어씀**(`:1136`, 무조건) |

**형식을 맞추면 대조가 문자열 동등 비교 하나로 끝난다.** 남는 차이는 마지막 행 하나이고, **동결본과 갱신본이라 시간이 지나면 값 자체가 갈린다** — 이것이 기반 문서가 Identity 를 흡수하지 않은 근거이고 형식 통일이 없애지 못하는 것이다.

#### 지문 형식 — bare hex 로 통일한다

**기반 문서 셋은 `"sha256:1c07af…"` 접두사를 쓰는데 이 문서는 벗긴다.** 적용 대상은 지문이 실리는 자리 전부다 — `references[].fingerprint` · SM 의 `definitionVersion` · `upstream.consumed` 의 값.

| 근거 | |
|---|---|
| **코드에 근거가 없다** | `rwFileSha256` 이 bare hex 를 반환하고(`:1059`) Identity 가 그대로 저장한다(`:1136`). 접두사는 설계 문서가 예시에 붙인 것이고 현행 실측에 선례가 0건이다 |
| **붙이고 벗기는 코드가 사라진다** | 라이터마다 접두사를 붙이고 리더마다 벗겨야 한다. 함수 반환값을 그대로 저장하면 그 짝이 없다 |
| **Identity 와 직접 대조된다** | 두 파일의 값을 사람이 눈으로, 코드가 동등 비교로 견줄 수 있다. 미결이던 형식 불일치가 소멸한다 |
| **쓰지 않는 확장을 위한 표기다** | `algo:` 접두사는 알고리즘이 여럿일 때 값을 하는데 이 설계에 하나뿐이고, 교체 시 구분은 `$schema` 번호가 이미 담당한다 |

**키 이름은 바꾸지 않는다.** `fingerprint` · `definitionVersion` 은 **역할 이름**이라 알고리즘 중립적이고, Identity 의 `sha256` 은 이 문서가 손대지 않는 파일의 키다(기반 문서 1.2 — 제자리 유지). **알고리즘을 이름에 박는 자리를 늘리지 않는 것이 접두사를 벗기는 것과 같은 판단이다** — `sha256` 이 값이든 키든 문자열로 남으면 교체 시 그만큼 고칠 자리가 생긴다.

포기하는 것 하나 — **값만 보고 알고리즘을 알 수 없다.** 그 답은 스키마가 갖는다(`$schema: 1` 에서 지문 = sha256 소문자 hex 64자). 소비자가 코드이지 사람이 아니므로 값의 자기서술성이 필요한 자리가 아니다.

#### contentIdentity 판정을 앞단으로 옮기나 — 가르는 것이 맞다

**통째로 옮기는 것은 성립하지 않는다.** 한 함수가 두 일을 하고 있고 둘의 제약이 다르다.

| `rwResolveContentIdentity` 의 일 | 앞단으로 | 근거 |
|---|---|---|
| **content uuid 발급·해석** — symbol uuid 의 네임스페이스(`:1020-1021`) | **못 옮긴다** | RW 는 **프로젝트 없이도 서야 한다** — `storePath` 가 비면 path 유래 uuid 로 폴백하고(`:1110-1112`) 워커·배치는 디렉토리를 인자로 받는다(`:1076-1077`). 반면 Reference 등록은 프로젝트가 열려 있어야 한다(`view/DashMainWindow.cpp:2116` 의 `IsProjectOpen()` 가드). **RW 는 Reference 로 등록되지 않은 deck 도 연다** |
| **변경 판정** — 저장 해시 vs 현재 해시 → `deckChanged` | **옮긴다** | 아래 |

**변경 판정 쪽은 옮기는 편이 낫고, 비용이 0이다.**

| 근거 | |
|---|---|
| **지금 소비자가 0곳이다** | `DashRwSession::referenceModelChangedOnDisk()`(`:1014`) → `DashAnalysisModelContext::referenceModelChangedOnDisk()`(`controller/DashAnalysisModelContext.cpp:276`) 로 **두 계층에 노출돼 있는데 `view/`·`viewmodel/`·`model/` 어디서도 읽지 않는다.** 지금 지워도 회귀가 없다 |
| **판정이 자기 근거를 지운다** | 비교 직후 현재 해시로 덮으므로(`:1136`) 같은 변경이 **두 번째 열기부터 false** 다. 한 번만 뜨는 경고는 배지가 될 수 없다 |
| **추가 I/O 가 0이다** | RW 는 deck 을 열 때 어차피 `rwFileSha256` 을 돈다(`:1099`). 비교 대상만 자기 저장값에서 **앞단 동결 지문**으로 바꾸면 된다 |

**이것이 실제로 여는 것.** 기반 문서 2.3 은 "기준 파일의 제자리 수정" 을 **완화 없는 사각**으로 남겼다 — 배지 판정이 저장 값 둘만 견주므로(파일을 열지 않는다) 앱 밖에서 deck 을 고쳐도 어느 지문도 움직이지 않기 때문이다. RW 가 동결 지문과 견주면 **덮어쓰지 않으므로 열 때마다 반복해서 뜬다.**

**단 RW 가 여는 확장자에 한한다** — `deck`(`.inp`·`.dat`·`.dfsxml`)만이다. `part`(`.prt`) · `template`(`.wbpj`·`.stli`) · `material` 은 RW 가 열지 않아 여전히 사각이고, FE-safe 재료의 제자리 편집 채널이 정확히 그쪽이다.

**이 배포에는 넣지 않는다.** W1 이 동결 지문을 만들면 정본은 앞단에 생기고, RW 가 자기 `sha256` 을 계속 들어도 값이 같고 용도가 달라 **해가 없다.** 제거는 중복 정리이지 결함 수정이 아니다 → 미결 14.

#### 확장자 → 역할 대응 — 앞단에서 자리가 있는 5종

| 확장자 | `kind` | 역할 | 등록 |
|---|---|---|---|
| `.inp` `.dat` `.dfsxml` | `fe` | `deck` | **한다** |
| `.prt` | `cad` | `part` | **한다** |
| `.stli` | `fe` | `template` | **한다** — 복사 단위가 부모 폴더라 `files.template` 이 1단계 하위 경로다. **지문 대상은 미정**(미결 12) |
| `.vtk` `.vtu` `.rst` `.odb` `.csv` `.stp` `.step` | — | **없다** | **안 한다 — 복사만** |

**역할 없는 7종을 등록하지 않는 것이 이 문서의 결정이다.** 근거는 소비자 부재다 — 그 일곱은 후보 스캔(`view/DashReferenceFileWidget.cpp:448` — `.dat .cdb .inp .dfsxml .wbpj .stli` 6종)에도 없어 어느 모듈도 기준 파일로 받지 못한다. `[Add File]` 필터 12종(`:2126-2127`)과 역할 4종의 어긋남은 남되, **남는 것이 "등록 안 됨" 이지 "잘못 등록됨" 이 아니다.**

**`.wbpj` 는 [Add File] 로 들어오지 못한다** — 필터에 없어 사용자가 손으로 프로젝트 폴더에 넣는다. 형태 B 는 그래서 이 경로로 완성되지 않고, 후보 스캔이 발견하는 시점(`view/DashReferenceFileWidget.cpp:313`)에 등록해야 한다. **그 시점은 사용자 조작이 아니라 스캔이라 "PM 쓰기는 전부 사용자 조작" 규약과 어긋난다** → 미결 2.

### 2.3 [3] 파싱 — 전역 활성 컨텍스트를 자기 `upstream` 으로

**이 자리가 앞단 배선에서 가장 중요한 분기다.** 지금은 파싱 대상(세션 상태)과 Reference 지목(저장 상태)이 같은 필드 `m_activeFilePath` 를 쓴다 — 화면 조작이 데이터 결합을 바꾼다.

| | 대상 | 처분 |
|---|---|---|
| **저장** — 이 Set 은 어느 기준 파일 기준인가 | `upstream.references[]` | 신설 |
| **세션** — 화면에 렌더된 대상 · 트리 선택 | `m_activeFilePath` | **유지** |

**레지스트리는 손대지 않는다.** `DashAnalysisModelContextRegistry`(`controller/DashAnalysisModelContextRegistry.h`)는 이미 `filePath → context` 맵이고 `getOrLoad(path)` 를 노출한다. 바꾸는 것은 **뷰·PM 층이 그 경로를 어디서 얻나** 뿐이다.

#### 호출부 처분 — 앞단 전수

| 좌표 | 현행 | 처분 |
|---|---|---|
| `viewmodel/DashGeometryParameterPresentationModel.cpp:46` | `registry.activeFilePath()` → DV `source` 문자열의 dat 파일명이 된다 | **교체 + 신설.** `DashGeometryParameter` 에 자리가 없다 — 아래 |
| `viewmodel/DashGeometryParameterPresentationModel.cpp:58` | `registry.activeContext()` → 파트 이름 폴백 | 동상 |
| `view/DashConditionParameterizationWidget.cpp:222` | `activeContext()` | **교체 — 한 줄.** `mModel->getContext()` 가 이미 있다 |
| `view/DashConditionParameterizationWidget.cpp:313-315` | `activeFilePath()` → `refreshFromFile()` → `:375` | **교체 — 출처만.** `refreshFromLoadedAnalysis()` 는 그대로 |
| `view/DashGeometryParameterCADWidget.cpp:345` | `activeFilePath()` | **교체 — 출처만**(`:416` 이 같은 진입점을 부른다). `upstream.references[part]` |
| `view/overlay/DashMorphingSettings.cpp:562` · `:636` | `activeContext()` | **교체** — 호스트 인스턴스의 `upstream` 경유 |
| `view/DashMainWindow.cpp:2326` | `setActiveContext(filePath)` — 파싱 트리거 | **유지** |
| `view/DashMainWindow.cpp:2496-2499` · `:2523-2527` · `:2664` · `:3331` | 렌더·트리 선택 | **유지** |

교체의 형태는 여섯 곳 다 같다.

```
현행:  registry.activeFilePath()
신:    refStore.resolve(inst.upstream.references[0], "deck")  →  registry.getOrLoad(path)
```

#### 컨텍스트를 누가 소유하고 누가 드나

**컨텍스트 객체는 아무도 멤버로 들지 않는다 — 레지스트리가 소유한다.**

| | |
|---|---|
| 소유 | `DashAnalysisModelContextRegistry::m_contexts` — `unordered_map<QString, unique_ptr<Context>>`(`controller/DashAnalysisModelContextRegistry.h:54`) |
| 반환 | `getOrLoad`·`get` 은 **raw non-owning 포인터**(`.cpp:20` · `:30` · `:47`) |
| 인스턴스가 드는 것 | **컨텍스트가 아니라 키(경로)다.** 조회는 매번 `get(경로)` |
| 키 | `getOrLoad` 가 스스로 canonical 화한다(`.cpp:18` · `:24`) — 2.2 의 canonical 계약과 맞는다 |

**포인터를 멤버로 캐시하지 않는 것이 맞다.** 지금 레지스트리에 `erase`·`clear` 가 **0건**이라 포인터가 죽지는 않지만, 그것은 **프로젝트를 닫아도 캐시가 안 비워진다**는 뜻이기도 하다(미결 15).

#### 드는 주체는 model 이다 — view·viewmodel 이 아니고, 이미 그렇다

**신 배선의 자료구조가 두 모델에 이미 완성돼 있다.**

| 모델 | 멤버 | 인스턴스별 조회 | 경로 주입 진입점 |
|---|---|---|---|
| `DashConditionParameterization` | `m_loadedFilePath`(`.h:82`) | `getContext()` = `registry.get(m_loadedFilePath)`(`.cpp:109-112`) | `refreshFromLoadedAnalysis(filePath)`(`.cpp:114-126`) |
| `DashGeometryParameterCAD` | `m_loadedFilePath`(`.h:64`) | `getContext()`(`.cpp:97-100`) | `refreshFromLoadedAnalysis()`(`.cpp:102-115`) |

**그래서 이 둘은 "배선 교체" 가 아니라 "우회 제거" 다.** 모델이 자기 경로로 컨텍스트를 받는 길이 이미 있고 내부 소비자도 있는데(`DashConditionParameterization.cpp:332` · `:352` 가 `getContext()` 를 쓴다), **뷰가 그 길을 두고 전역 커서를 읽는다.** 남은 것은 `refreshFromLoadedAnalysis` 에 넘길 `filePath` 의 출처를 화면 상태에서 `upstream` 으로 바꾸는 것 하나다 — 호출부가 `view/DashConditionParameterizationWidget.cpp:375` · `view/DashGeometryParameterCADWidget.cpp:416` 둘이다.

**Morphing 만 자리가 없다.** `DashGeometryParameter` 에는 `m_loadedFilePath` 도 `getContext()` 도 없고, 비슷해 보이는 `m_fileName` 은 **setter·getter 만 있고 호출부가 0곳**인 죽은 멤버다(`model/DashGeometryParameter.h:23` · `:32` · `:50`). **앞단 3모듈 중 신설이 필요한 것은 이 하나다.**

**view·viewmodel 은 들 자리가 아니다.**

| 층 | 실측 |
|---|---|
| view | `DashConditionParameterizationWidget` 의 멤버가 `m_highlightedCondition` · `m_blockDvWatcher` **둘뿐**이다(`.h:93` · `:105`) — 전부 화면 상태이고 모델은 `setModel()` 로 주입받는다 |
| viewmodel | `DashGeometryParameterPresentationModel` 은 **상태가 아예 없다.** 생성자가 `parent` 만 받고 `buildDvGeometry(rows, model, ioCtrl)` 처럼 model 을 인자로 받는 무상태 헬퍼다 |

근거는 층 구조만이 아니다 — **`upstream` 은 정의 파일의 내용**이므로 정의를 소유하는 model 이 드는 것이 맞다. view·viewmodel 이 들면 기반 문서가 동반 축으로 든 "소유 경계 12건 — 뷰가 정본인 문제" 를 새로 하나 만드는 것이다.

#### `m_activeFilePath` 는 커서 하나다 — 맵은 계속 공유한다

**등록된 것은 `m_contexts` 맵이고 `m_activeFilePath` 는 그중 하나를 가리키는 커서다.** 신 배선은 **맵을 그대로 쓰고 커서만 안 읽는다** — 컨텍스트를 새로 만드는 것이 아니라 같은 캐시에서 자기 키로 받는다.

| | 현행 | 신 |
|---|---|---|
| 컨텍스트 캐시 | `m_contexts` | **같다 — 공유** |
| 어느 것을 볼지 | `m_activeFilePath` 커서 1개 | 인스턴스마다 자기 `m_loadedFilePath` |
| 렌더 대상 | `m_activeFilePath` | **같다 — 유지** |

**`setActiveContext` 를 남기는 근거가 코드에 있다.** 그 함수는 커서만 옮기지 않고 `updateActor()` 를 부른다 — 이전 actor 제거 · 새 actor 추가 · **카메라 리셋**까지 한다(`.cpp:50-63` · `:77-107`). `getOrLoad` 단독은 렌더를 건드리지 않는다. **그래서 "데이터 결합은 `getOrLoad`, 화면은 `setActiveContext`" 라는 분리가 층의 취향이 아니라 함수의 부작용 유무와 정확히 맞는다.**

**따라오는 것 하나 — 같은 deck 을 보는 두 Set 은 컨텍스트를 공유한다.** 캐시 히트이므로 파싱이 두 번 돌지 않는 것이 이득인데, Condition 의 Value 편집이 표가 아니라 deck 으로 먼저 가는 구조라 **한쪽 편집이 다른 쪽에 보인다.** 활성 컨텍스트가 하나인 현행에서도 같으므로 회귀는 아니지만, "Set 이 독립됐다" 로 오해할 수 있는 자리다(미결 16).

**교체가 실제로 여는 것.** 지금은 커서가 하나라 **Geometry Set 둘이 서로 다른 deck 을 동시에 볼 수 없다.** 교체 후에는 각 Set 이 자기 키로 조회하므로 동시에 다른 deck 을 본다 — 레지스트리가 이미 다중 컨텍스트를 들고 있어 **자료구조 변경이 0이다.**

**이미 경로를 인자로 받는 곳은 건드리지 않는다.** 모델 계층은 대부분 이미 경로를 넘긴다 — 바뀌는 것은 그 경로가 화면 상태에서 오느냐 정의에서 오느냐다.

### 2.4 [4]·[5] Set 생성 — `inst_` 발급

**가장 싼 자리가 이미 있다.** `DashProject::createModuleJsonFile`(`model/DashProject.cpp:592-616`)이 7모듈 전부의 config 생성을 통과하고, `moduleName` · `setName` · `variant` 세 인자를 이미 받아 `rootObj["variant"]` 를 쓴다.

```cpp
// 현행 :602-605
QJsonObject rootObj;
if (!variant.isEmpty()) {
    rootObj["variant"] = variant;
}
```

여기에 다섯 줄을 더한다.

```json
{
  "$schema": 1,
  "id": "inst_…",
  "module": "GeometryParameter",
  "variant": "Morphing",
  "definitionVersion": "…",
  "upstream": { "references": [], "definitions": [], "executions": [], "consumed": {} }
}
```

| 항목 | 판정 |
|---|---|
| `id` | `UUID::from_namespace(ns_inst, "{moduleName}_{setName}")`(1.3). **인자 둘로 이미 조립 가능하다** — 이 함수가 그 이름으로 파일을 만들고 있다(`:599`) |
| `module` | 인자 `moduleName` 그대로. 어휘 정본은 `ModuleType` enum(`controller/DashIOController.h:17-30`)과 `getModuleName()` |
| `variant` | 인자 그대로. **키를 새로 만드는 것이 아니라 폴백을 없애는 것**이다 — 현행에도 이미 1순위 입력이다 |
| `upstream` | 빈 배열 셋 + 빈 `consumed`. **생략하지 않는다** — 판정이 "키가 있나" 를 먼저 묻지 않아야 한다 |
| `definitionVersion` | 이 시점의 빈 정의를 해시한 값 |

호출 경로: `view/DashMainWindow.cpp:625` → `DashProject::createNewSet`(`:705-800`) → `createModuleJsonFile`. **앞단만 특별 취급하지 않는다** — 7모듈 전부가 같은 함수를 통과하므로 하류도 같은 6키를 갖고 시작하고, 다만 `upstream` 을 채우는 배선이 앞단에만 붙는다.

Set 삭제(`:802-`)·rename(`:1416-`)은 **손대지 않는다.** 인스턴스 색인이 없으므로(기반 문서 1.2) 동기화할 자리가 없다 — Set 이름은 파일명이 계속 들고, config 파일이 지워지면 그 `inst_` 도 함께 사라진다.

### 2.5 [4]·[5] 정의 저장 — 헬퍼 통과와 지문

앞단 정의 라이터는 넷이고 **형태가 넷 다 같다** — 파일 전문 읽기 → 섹션 교체 → 전문 재작성. 헬퍼로 감싸는 것이 기계적이다.

| 모듈 | 라이터 | 좌표 | 쓰는 섹션 |
|---|---|---|---|
| Geometry Morphing | `saveMorphingSettings` | `viewmodel/DashGeometryParameterPresentationModel.cpp:325-390` | `Morphing.*` |
| Geometry (양 variant) | `DashDesignVariableModel::saveToJsonFiles` | `model/DashDesignVariableModel.cpp:375-487` | `DV-Geometry` |
| Condition | `saveDvCondition` | `viewmodel/DashConditionParameterizationPresentationModel.cpp:117-140` | `DV-Condition` |
| AnalysisLauncher | `saveSettings` · `saveInputFileSettings` | `model/DashAnalysisLauncher.cpp:780-827` · `:829-` → `model/DashDoeConfigManager.cpp:115·150` | `DOE configuration` · `input_files` |

헬퍼가 하는 일 넷 — ① 제외 키 패턴을 지운 사본의 sha256 계산 ② `definitionVersion` 갱신 ③ 실행 없는 모듈이면 `consumed` 갱신 ④ temp + rename.

#### `saveToJsonFiles` 가 앞단에서 유일하게 특이하다

**AL 화면이 상위 Geometry·Condition 파일을 되쓴다.** DV 표에서 min/max/type 을 고치면 그 값이 상위 정의 파일로 간다(`model/DashDesignVariableModel.cpp:469-481`).

따라오는 것 둘.

- **그 Geometry 의 `definitionVersion` 이 AL 조작으로 움직인다. 그것이 옳다** — 내용이 실제로 바뀐 것이다. AL 자신은 그 뒤 자기 `consumed` 를 현재 값으로 다시 적으므로 자기 배지가 뜨지 않고, **같은 Geometry 를 든 다른 AL Set 에는 `⚠ Stale` 이 뜬다.** 그것도 사실이다.
- **섹션 판정이 파일명 부분문자열로 남는다** — `fileName.contains("GeometryParameter") || contains("Geometry")` → `DV-Geometry`, 아니면 `DV-Condition`, **둘 다 아니면 기본값이 `DV-Condition`**(`:411-417`). 헬퍼를 통과시켜도 이 판정은 그대로다. 항목 단위 조인이라 로컬 ID 축이고 이 문서 밖이다 → 미결 5.

#### `consumed` 갱신 시점 — 앞단 2종

| 모듈 | 소비 = | 시점 | 좌표 |
|---|---|---|---|
| Geometry · Condition | 정의를 만드는 것 | **자기 정의 저장** | 위 표의 라이터 안 |
| AnalysisLauncher | 실행 | **실행 착수** | `runDoeAsync`(`model/DashAnalysisLauncher.h:88`) |

**상위 선택 변경은 갱신 시점이 아니다.** 엣지 배열에만 적고 `consumed` 는 건드리지 않는다 — 고르는 것은 의도이지 소비가 아니다.

### 2.6 [6] AnalysisLauncher — definition 엣지는 신설이 아니라 교체

**현행에 이미 definition 엣지가 있고, 값이 config 파일명이다.**

```
DOE configuration.Selected Design Variables = [ "ConditionParameter_Set1.json",
                                                "GeometryParameter_Set1.json" ]
```

라이터가 그것을 **고정 2원소 배열**로 쓴다(`model/DashDoeConfigManager.cpp:111-115` — `[condition, geometry]` 순, 빈 자리는 `"None"`). 그런데 **읽는 쪽 넷이 위치를 믿지 않고 각자 부분문자열로 되짚는다.**

| 리더 | 좌표 | 판정 | 범위 |
|---|---|---|---|
| `DashDoeConfigManager::loadSettings` | `model/DashDoeConfigManager.cpp:70-` | `contains("cond") \|\| contains("Condition")` | **앞단** |
| `DashAnalysisLauncher::findAndEmitSourceFiles` | `model/DashAnalysisLauncher.cpp:1236-1294` | 동상 + `contains("Geometry") \|\| contains("geom")`, **첫 일치에서 `break`** | **앞단** |
| `DashMorphingDoeExecutor` | `controller/DashMorphingDoeExecutor.cpp:124-136` | 동상 | 실행 — 밖 |
| `DashDataProcessor` | `model/DashDataProcessor.cpp:2824-` | 동상 | 하류 — 밖 |

**`break` 가 결함의 실체다.** Geometry Set 이 둘이면 `Selected Design Variables` 순회의 첫 일치가 이기고, 사용자가 고른 것이 아니라 배열 순서가 이긴다. 이름에 `Geometry` 도 `geom` 도 없는 Set 이름은 아예 안 잡힌다.

#### 신 — 정본을 `upstream.definitions[]` 로 옮긴다

```json
"upstream": {
  "references":  ["ref_9b41e0c3f2a1"],
  "definitions": ["inst_7f3a2c1b04de", "inst_1e55da62c9f7"],
  "executions":  []
}
```

| 항목 | 처분 |
|---|---|
| `Selected Design Variables` | **파일에 남기되 읽지 않는다.** 폐기는 4·5번 후속 |
| 앞단 리더 2곳 | `upstream.definitions[]` 조회로 교체 |
| 범위 밖 리더 2곳 | **현행 유지** — 그 구간에 정본이 둘이 된다 → 미결 4 |
| 쓰기 지점 | `DashDoeConfigManager.cpp:115` 에서 두 키를 함께 쓴다 — 파일명과 `inst_` 를 같은 저장 1회에 적어 어긋날 창을 없앤다 |

**정본이 둘인 구간을 감수하는 근거는 순서다.** 하류 리더 둘을 함께 고치면 이 배포가 DataPreprocessor·Morphing 실행 경로까지 끌고 들어가는데, 그 둘은 execution 엣지 축이라 앞단 절단선 밖이다. 같은 저장 1회에 두 키를 함께 쓰면 **두 정본이 어긋나지 않으므로** 하류가 옛 키를 읽어도 결과가 같다.

#### `references[]` — variant 별로 갈리는 자리

기반 문서 7.2-8 이 "역할별 실측이 아직 없다" 로 남긴 항목이다. 앞단 실측으로 한 칸 좁힌다.

| 실측 | 좌표 |
|---|---|
| `input_files[]` 원소가 `{name, target_component, path}` 3필드다 | `view/DashReferenceFileWidget.cpp:1125` · `:1153` |
| 라이터 1 · 리더 4 | 쓰기 `model/DashDoeConfigManager.cpp:150` / 읽기 `:173-174` · `model/DashJobRunner.cpp:1235` · `:1380` · `:1488` |
| N행 중 라디오로 고른 1행이 실행 템플릿 | `view/DashReferenceFileWidget.cpp:1043-1045` 이 복원한다 |
| 역할은 필드로 적히지 않고 **확장자로 유도된다** | 후보 스캔 6종(`:448`)마다 target 해석 분기가 따로 있다 |

**결정: `input_files[]` 를 그대로 두고 `upstream.references[]` 는 그 N행이 가리키는 `ref_` 목록으로 둔다.** 역할 이름을 AL 이 다시 적지 않는 이유는 `reference.json` 항목이 이미 `files` 맵으로 들고 있기 때문이다 — 역할을 두 곳에 적으면 어긋날 자리가 생긴다.

`references[]` 가 배열인 것은 FE-safe 때문이다 — 같은 Set 안 다른 템플릿이 낸 ODB 를 입력으로 받으므로 단수로는 그 모듈이 서지 않는다. **뒤에 배열로 바꾸는 것은 스키마 변경이라 지금 배열로 둔다.**

---

## 3. 배지 — 앞단에서 실제로 뜨는 것

```
소비자 upstream.consumed[ID]     vs     그 대상의 현재 버전
   (마지막으로 소비한 판)                (지금 무엇인가)
   ▼
다르면           ⚠ Stale
가리킨 ID 가 없다  ✕ Broken
그 외            무배지
```

| 인스턴스 | 뜰 수 있는 사유 | 해소 | 착수 차단 |
|---|---|---|---|
| Geometry (양 variant) | `ref_` 직속 — "기준 파일이 교체됐습니다" | **재저장** | `Broken` 만 |
| Condition | 동상 | **재저장** | 동상 |
| AnalysisLauncher | `ref_` 직속 · `inst_` 직속(definition) — "상위 정의가 바뀌었습니다" · **상속** — Geometry·Condition 경유 deck | **재실행** | 동상 |

**앞단은 계보가 얕아 사유 4갈래 중 셋만 선다.** 상속 갈래("{조상}이 바뀌었습니다 ({직속} 경유)")가 서는 것은 AL 하나이고, 그것도 deck 하나뿐이다 — AL 이 deck 에 직속으로도 닿고 Geometry·Condition 경유로도 닿는데 **같은 시점에 계산하므로 값이 같고 키가 하나로 접힌다.** 이것이 `consumed` 를 배열이 아니라 맵으로 두는 근거다.

**Geometry·Condition 의 `Stale` 이 재저장으로 풀리는 것이 앞단의 성질이다.** 실행이 없어 "소비 = 정의를 만드는 것" 이므로 해소 단수가 1이고, 상속이 섞일 자리가 없다.

화면 층은 [Project-Store-Design-Dependency-State-Display](Project-Store-Design-Dependency-State-Display.md) 의 3층 중 **트리 아이콘과 착수 차단 둘만** 쓴다 — 배지가 2종으로 줄면 우측 독 스트립이 담을 것이 없다.

---

## 4. 승격 — 앞단으로 자를 수 없는 유일한 항목

### 4.1 분기 지점이 기반 문서와 다르다

기반 문서 3.5 는 `loadSetsFromConfigs()` 를 승격 경로로 옮기라고 적었는데, **그 함수는 `7024e04` 에서 호출부가 0곳이다**(0.3-1). 열기의 실체는 이쪽이다.

```
[열기] DashProjectManager::OpenProjectFromFolder    controller/DashProjectManager.cpp:97-126
   │   findDprojFolder 로 .{name}.dproj 탐색            :102
   │   SetProjectDirectory — IOController 생성          :118
   │   restoreExistingModules 호출                      :122
   ▼

[판정] DashProject::restoreExistingModules          model/DashProject.cpp:1213-
   │   configs/*.json 전량 스캔                          :1240-1243
   │   접두사 7종 테이블로 모듈 판정                       :1250-1271
   │   모듈별 variant 검출기 호출                          :1277 :1320 :1339 :1366
   ▼

[신] 분기
   │   모든 config 에 id 가 있다 ──▶ 내용으로 판정. 파일명·접미사를 읽지 않는다
   │   없는 config 가 있다 ──────▶ 승격 1회
   ▼

[승격] 그 파일에 대해 현행 판정을 1회 돌린다
       id · module · variant 를 써 넣는다
       definitionVersion 첫 계산
       upstream 은 빈 배열 셋 + 빈 consumed
       reference.json 이 없으면 만든다 (4.3)
```

**판정 코드가 사라지지 않고 호출부가 옮겨간다.** 상시 유지되는 하위호환 분기가 아니라 1회 실행되는 입구다.

### 4.2 앞단만 자를 수 없는 근거

**열기가 `configs/` 전량을 한 번에 훑는다.** 모듈별로 자를 자리가 없으므로 승격 1회가 variant 검출기 **4종 전부**를 통과한다.

| 검출기 | 좌표 | 범위 | 승격 시 |
|---|---|---|---|
| `detectGeometryVariant` | `model/DashProject.cpp:621-653` | 앞단 | 4단 폴백 → `variant` 키 1줄 |
| `detectLauncherVariant` | `:690-703` | 앞단 | 2단 폴백 → 동상 |
| `detectBuilderVariant` | `:658-670` | 하류 | 동상 — **범위 밖이지만 함께 처리된다** |
| `detectRunnerVariant` | `:673-685` | 하류 | 동상 |

**밖에 남는 판정 호출부 3곳은 손대지 않는다** — `view/DashResultsAnalyzerWidget.cpp:569` · `view/DashMainWindow.cpp:792` · `:1455` 가 `detectBuilderVariant`·`detectRunnerVariant` 를 직접 부른다. 승격이 `variant` 키를 채워 두면 이 셋도 1순위에서 답을 얻으므로 **폴백에 도달하지 않는다** — 고치지 않아도 폴백이 죽는다.

### 4.3 `references[]` 씨앗

승격이 배열을 비우지 않는다. `{configs}/AnalysisModelIdentity.json` 의 `models` 키가 곧 **이 프로젝트에서 열린 적 있는 deck 의 canonical 경로 목록**이다(`controller/DashRwSession.cpp:1068-1073` · `:1090-`).

| 필드 | 승격 시 값 |
|---|---|
| `id` | 새 발급 |
| `files` | 확장자로 역할 판정. **씨앗이 덱뿐이라 형태 A 만 난다** — B·C 는 사용자가 다시 등록해야 선다 |
| `origin` | 비운다 — 원본 경로를 모른다 |
| `fingerprint` | **여기서 1회 계산한다.** Identity 의 저장 값을 옮기지 않는다 — 그 값은 세션 open 마다 현재 해시로 덮이므로 "등록 시점" 을 기억하지 못한다 |
| `label` | 파일 basename |

**`AnalysisModelIdentity.json` 을 흡수하지 않고 제자리에 둔다.** 재사용할 것은 값이 아니라 함수(`rwFileSha256`)다.

### 4.4 선행 — 죽은 스캐너 하나를 먼저 지운다

`loadSetsFromConfigs()`(`:1066-1211`)와 `restoreExistingModules()`(`:1213-`)는 같은 접두사 판정을 하는 근친 중복이고 **앞의 것은 호출부가 0곳**이다. 승격을 어느 쪽에 붙이느냐를 정하기 전에 하나를 지우는 것이 선행이다 — 남겨 두면 다음 사람이 죽은 쪽을 고친다.

**승격된 프로젝트는 전부 무배지다.** `consumed` 가 비어 비교 대상이 없다. 사용자가 상위를 한 번 고르고 한 번 돌리면 그때부터 배지가 선다 — 현행과 동등하다.

---

## 5. 순서 — 4단계

각 단계 종료 시 빌드·실행 가능하다.

```
[W1] reference.json · Reference 스토어 · [Add File] 등록          [현행 동작 무변경]
   │   rwFileSha256 노출 · dash::core::UUID v5 발급 (1.3)
   │   아무도 읽지 않는 상태로 먼저 만든다 — write-only
   │   verify: 파일 3개 등록 후 references[] 가 실체와 일치
   │           같은 파일을 다시 열어도 fingerprint 가 재계산되지 않는다
   │           reference.json 을 지우고 다시 만들면 ref_ 가 같다   ← 1.3 의 핵심 검증
   ▼

[W2] SM 최상위 키 6개 + 승격 + 열기 경로 교체                      [전 모듈 — 앞단만 자를 수 없다]
   │   선행: 죽은 loadSetsFromConfigs() 처분 (4.4)
   │   verify: 구프로젝트 열기 → 전 config 에 id·module·variant 생성
   │           재열기에서 restoreExistingModules 의 접두사 판정 미실행
   │           reference.json 이 Identity 씨앗으로 채워진다
   │           -MCU · -CAD Set 이 각 모듈에서 정상 진입
   │           id 를 지우고 재승격하면 같은 inst_ 가 난다      ← 1.3 의 핵심 검증
   ▼

[W3] upstream 3배열 + 읽기 배선 교체 6곳 + AL definition 엣지      [상위 선택이 복원된다]
   │   verify: 상위를 고르고 프로젝트를 닫았다 열면 선택이 복원된다
   │           Geometry Set 두 개가 서로 다른 deck 을 동시에 본다   ← 2.3 의 핵심 검증
   │           이름에 "Geometry" 가 없는 Set 을 AL 이 상위로 잡는다  ← 2.6 의 핵심 검증
   │           상위 Set 을 지우면 소비자가 ✕ Broken
   ▼

[W4] 정의 저장 헬퍼 + definitionVersion + consumed + 배지 2종      [낡음이 화면에 뜬다]
       verify: 상위 Geometry 를 고치면 AL 이 ⚠ "상위 정의가 바뀌었습니다"
               기준 파일을 다시 등록하면 ⚠ "기준 파일이 교체됐습니다"
               DOE 를 80케이스 돌리는 동안 AL 배지가 움직이지 않는다   ← 1.2 의 핵심 검증
               Geometry·Condition 은 재저장으로, AL 은 재실행으로 풀린다
```

**기반 문서 5절과 갈리는 것 둘.**

| 기반 문서 | 이 문서 | 근거 |
|---|---|---|
| S3 = variant 판정 교체 (별 단계) | **W2 에 흡수** | 승격이 `variant` 를 4종 전부 써 넣으면 그 시점부터 폴백에 도달하는 경로가 없다 — 따로 자를 것이 남지 않는다 |
| S4 에 `folders.first()` 제거 포함 | **밖** | 그 자리가 ModelRunner·Optimizer(`view/DashModelRunnerWidget.cpp` · `view/DashOptimizerWidget.cpp`)라 하류다 |

**W3 까지만 해도 현행보다 낫다** — 상위 바인딩이 복원되고, Geometry Set 둘이 서로 다른 deck 을 보며, AL 의 상위 지목이 이름 매칭에서 ID 조회로 바뀐다. W4 가 사용자에게 보이는 나머지를 만든다.

---

## 6. 후속 4·5번과의 절단선

### 6.1 무엇이 남나

| 후속 | 이 문서가 남기는 것 | 앞단 몫 |
|---|---|---|
| **4. 정의·실행 상태 분리** | **지문 제외 키 목록이 곧 절단선이다** — 지금 지문에서 빼는 키가 그때 실행 메타로 나갈 키다 | **AL 하나** — `DOE Table` · `DOE Analysis` 둘. Geometry·Condition 은 제외 목록이 비어 있어 나갈 것이 없다 |
| **5. 단일 root 재배치** | **0건 건드린다** — 경로 조립 함수와 그 호출부를 손대지 않는다. `configs/` 도 3루트도 그대로다 | 없다 |

**4번의 부속인 도구 계약 변경도 앞단에 걸리지 않는다.** 외부 도구가 SM 을 되쓰는 것은 ModelBuilder 축이고(`Configuration.*.status`), 앞단 4모듈에는 그 채널이 없다.

### 6.2 두 개념과의 대조 — 산출 박제 · 복구 스냅샷

선후행은 **Geometry · Condition → AnalysisLauncher → DataPreprocessor → ModelBuilder → ModelRunner → Optimizer** 여섯 단이다. 그 사슬 위에 두 개념을 얹어 본다.

| | 개념 | 요구하는 저장물 |
|---|---|---|
| **①** | 다음 모듈이 참조하는 정보를 **생산자의 산출에 박제** | 인스턴스마다 산출 메타 파일 1종 — 그 안에 산출 좌표와 "무엇의 몇 번째 판인가" |
| **②** | 산출 생성 시점의 **필수 정의 요소를 산출에 포함** (복구용) | 같은 파일 안 또는 옆에 **정의 본문 스냅샷** |

#### 계열 3안 중 어디에 있나

| | 개념 ① 산출 박제 | 개념 ② 복구 스냅샷 |
|---|---|---|
| **정의 버전 최소안** (이 문서의 기반) | **없다.** 산출 파일 자체가 없고, 박제 자리가 생산자가 아니라 **소비자 SM** 이다(`upstream.consumed`) | **없다.** 지문 1종뿐 — 해시는 "바뀌었나" 에 답하고 "무엇이었나" 에 답하지 못한다 |
| [Project-Store-Design-Edge-Complete-Minimal](Project-Store-Design-Edge-Complete-Minimal.md) | **있다** — `.dproj/outputs/{inst}.json` 에 산출 `rev` 와 `consumed` | **명시적으로 뺐다** — "지문은 그때와 같은가에, 스냅샷은 그때 무엇이었나에 답하는데 이 안이 필요한 것은 앞엣것뿐" |
| [Project-Store-Design-Layer-Cut](Project-Store-Design-Layer-Cut.md) (안 β) | **있다** — `executions/{label}/execution.json` | **있다** — `executions/{label}/input.json` = 정의 본문 스냅샷, **전 모듈** |

**두 개념을 동시에 만족시키는 안은 안 β 하나다.** 개념 ① 만이면 엣지 3종 안으로 선다. **이 문서의 기반인 정의 버전 최소안은 둘 다 아니다** — 박제의 방향이 반대(소비자 소유)이고 스냅샷이 없다.

#### 앞단에서는 판정이 서지 않는다

**이 문서 범위에 execution 엣지가 0건이라 두 개념이 적용될 자리가 없다**(1.2).

| 모듈 | 산출 | 개념 ①·② 적용 |
|---|---|---|
| Geometry (양 variant) · Condition | **없다** — 실행이 없고 산출이 곧 정의 파일이다 | 박제할 대상이 없다. 소비자는 정의 파일을 직접 본다 |
| AnalysisLauncher | 있다 — 케이스 디렉토리 | **소비자가 범위 밖**(DataPreprocessor)이라 박제 대상이 정해지지 않는다 |

**그래서 이 배선은 두 개념과 충돌하지 않는다 — 판정 재료가 범위 밖에 있다.** 첫 충돌 지점은 AL → DataPreprocessor 다.

#### 채택 시 이 문서에서 갈리는 것 1건

| 항목 | 개념 ① 채택 시 |
|---|---|
| `reference.json` · `ref_` · `inst_` · `module`·`variant` 자기신고 · 승격 (W1·W2) | **그대로 쓰인다** — Reference 는 프로젝트 귀속이라 모듈 산출 축과 무관하다 |
| `upstream` 3배열 (W3) | **그대로 쓰인다** — 직속 의도는 여전히 소비자의 정의다 |
| `definitionVersion` (W4) | **그대로 쓰인다** — 산출에 "무엇의 몇 번째 판" 을 적으려면 판 식별자가 필요하고 그것이 이 지문이다 |
| **`consumed` 를 조상 전량으로 채우는 규칙** (W4) | **버려진다** — 산출 지문이 있으면 전파가 재실행을 따라 한 칸씩 내려가므로 **직속만 들면 된다** |

기반 문서가 "범위를 이렇게 자르면 강제된다" 고 적은 설계 둘 중 **둘째(계보 = 조상 전량)가 개념 ① 채택으로 무효화된다.** 첫째(버전은 쓰기 트리거가 아니라 내용)는 남는다.

계보 크기 대조 — 앞단 손실이 작은 것이 순서 판단의 근거다.

| 인스턴스 | 조상 전량 (현행 설계) | 직속만 (개념 ① 채택) |
|---|:---:|:---:|
| Geometry · Condition | 1 | 1 |
| **AnalysisLauncher** | **3** | **3** |
| DataPreprocessor | 4 | 1 |
| ModelBuilder | 5 | 1 |
| ModelRunner · Optimizer | 6 | 1 |

**앞단 셋은 두 방식의 값이 같다.** 조상 전량 규칙이 실제로 값을 만드는 것은 DataPreprocessor 부터이므로, **W4 에서 `consumed` 를 직속만 담게 두고 조상 전량 여부를 DataPreprocessor 착수 시점에 정하면 버려지는 작업이 0이 된다.**

#### 개념 ① 은 후속 4번의 절반을 선행으로 요구한다

**산출 메타 파일이 생긴다는 것이 곧 실행 상태가 정의 파일에서 떨어져 나온다는 뜻이다.** 개념 ① 은 4번 없이 성립하지 않는다 — 다만 4번 전량이 아니라 앞쪽 절반이다.

| 4번의 성분 | 개념 ① 이 요구하나 |
|---|---|
| 산출 좌표와 판 식별자를 정의 파일 밖으로 | **요구한다** |
| 케이스 상태 · 실패 사유 · 스테이지를 실행 메타로 | 요구하지 않는다 |
| 외부 도구 되쓰기 · 1초 폴링 해소 | 요구하지 않는다 |

**앞단에서 그 몫이 AnalysisLauncher 하나다**(6.1). 개념 ① 을 채택하면 6.1 이 후속으로 밀어 둔 그 하나가 이번 배포로 올라온다 — `DOE Table` 의 산출 포인터가 SM 을 떠난다.

#### 개념 ② 의 앞단 난점 — Morphing 의 SB

**정의 본문 스냅샷은 SM 만 담고 SB 를 담지 못한다.** Geometry Morphing 의 "필수 정의 요소" 에는 핸들 배열 `.vtp`(SB)가 들어가는데, 그것이 수백 MB 급이라 실행마다 복사하는 것이 성립하지 않는다. 안 β 도 이것을 미결로 남겼다 — 스냅샷에 넣을지 지문만 박을지.

**개념 ② 를 문자 그대로 앞단에 적용하면 이 구멍이 바로 나온다.** 지문 축에서도 같은 자리가 이미 사각이다 — 핸들 위치만 옮긴 편집은 SM 바이트를 바꾸지 않아 `definitionVersion` 이 움직이지 않는다. **개념 ② 를 채택하려면 SB 처분을 먼저 정해야 하고, 그것이 이 문서 범위에서 가장 비싼 미결이다.**

#### 판정

| # | 판정 |
|---|---|
| 1 | **두 개념을 다 원하면 목적지는 안 β 다.** 정의 버전 최소안은 경유지이지 종점이 아니다 |
| 2 | **앞단 배선(W1\~W3)은 두 개념 어느 쪽에서도 버려지지 않는다.** 개념과 무관한 축(Reference · ID · 자기신고 · 승격)이라 지금 착수해도 길이 막히지 않는다 |
| 3 | **W4 만 조건부다.** `consumed` 를 직속만 담게 두면 손실이 0이고, 조상 전량으로 채우면 개념 ① 채택 시 그 부분이 버려진다 — **앞단 손실은 AL 1건뿐이라 작지만 0은 아니다** |
| 4 | **개념 ① 채택은 후속 4번의 앞쪽 절반을 이번 배포로 끌어올린다.** 앞단 몫이 AL 하나라 감당 가능한 크기다 |
| 5 | **개념 ② 는 SB 처분이 선결이다.** 그 답 없이 착수하면 Morphing 스냅샷이 반쪽이 되고, 반쪽 스냅샷은 복구를 보장하지 못해 개념 자체가 서지 않는다 |

---

## 7. 미결 — 앞단 한정 16건

| # | 항목 | 정해야 할 것 |
|---|---|---|
| 1 | **죽은 스캐너 처분** | `loadSetsFromConfigs()`(호출부 0곳)와 `restoreExistingModules()` 중 하나를 지우는 것이 W2 의 선행이다. 어느 쪽을 남길지 |
| 2 | **`.wbpj` 등록 시점** | `[Add File]` 필터에 없어 손으로 들어온다. 후보 스캔이 발견하는 시점에 등록하면 **PM 쓰기가 사용자 조작이 아니게 된다.** 필터에 `.wbpj` 를 넣을지, 스캔 등록을 예외로 인정할지 |
| 3 | **역할 없는 7종** | `[Add File]` 필터 12종 중 `.vtk .vtu .rst .odb .csv .stp .step` 는 등록하지 않고 복사만 하기로 정했다(2.2). 필터에서 빼는 것이 맞는지, 후보 스캔 6종 · `SupportedInputs` 5종(`model/AnalysisFileDefines.h`)과 목록 셋을 하나로 모을지 |
| 4 | **`Selected Design Variables` 정본 이중 구간** | 하류 리더 2곳(`DashMorphingDoeExecutor` · `DashDataProcessor`)이 옛 키를 계속 읽는다. 같은 저장 1회에 두 키를 함께 써서 어긋남을 막기로 했으나, 그 상태를 몇 판 유지할지 |
| 5 | **`saveToJsonFiles` 섹션 판정** | `contains("Geometry")` 실패 시 기본값이 `DV-Condition` 이다(`model/DashDesignVariableModel.cpp:411-417`) — 이름에 둘 다 없는 Set 의 DV 가 Condition 섹션으로 간다. 항목 단위 조인이라 로컬 ID 축이고 이 문서 밖이지만 **`inst_` 를 쓰면 이 판정도 없앨 수 있다** |
| 6 | **`.prt` 의 두 자리** | CAD 가 NX 로드분을 `configs/` 로 복사한다(`view/DashGeometryParameterCADWidget.cpp:626-633`). `[Add File]` 복사본(루트)과 이 복사본(configs) 중 어느 것을 `files.part` 가 가리키는지 |
| **7** | **`consumed` 의 범위를 W4 에서 정할지 미룰지** | 6.2 의 판정 3. 앞단 셋은 조상 전량과 직속만의 값이 같으므로 **직속만 담고 DataPreprocessor 착수 시점에 정하면 버려지는 작업이 0**이다. 지금 정하면 개념 ① 채택 시 AL 1건이 버려진다 |
| **8** | **Morphing SB(`.vtp`)의 처분** | 6.2. 복구 스냅샷(개념 ②)의 선결이자 `definitionVersion` 의 현재 사각이다 — 핸들 위치만 옮긴 편집이 SM 을 바꾸지 않아 지문이 움직이지 않는다. 스냅샷에 넣을지 · 지문만 박을지 · `(size, mtime)` 을 섞을지 |
| **9** | **벤더된 CoreLib 의 UUID API 판** | 1.3. v7 은 `feat/uuid-v7` 브랜치에만 있고 `origin/main` 에 없으며 태그도 없다. GUI 는 `external/packages/core-lib/` 의 **빌드 산물**을 링크하므로 그 판을 확인해야 한다 — v5 발급만 쓰는 이 안은 어느 판에서도 서지만, 후속에서 `exec_` 를 v7 로 두려면 CoreLib 릴리스가 선행이다 |
| **10** | **네임스페이스 UUID 상수 2개의 자리** | `ns_ref` · `ns_inst` 를 어디에 두나. `rwResolveContentIdentity` 는 함수 안 `static` 으로 하드코딩했다(`controller/DashRwSession.cpp:1105-1106`). Reference 스토어와 정의 저장 헬퍼가 각각 들지, 한 헤더에 모을지 |
| **11** | **같은 파일 중복 등록 규칙** | 기반 문서 1.2 는 "같은 파일을 두 번 등록 — 다른 `id` · 같은 `fingerprint`. 막지 않는다" 로 정했는데, **경로 기반 발급(1.3)에서는 같은 ID 가 나 항목이 하나로 접힌다.** 앞단 [Add File] 은 이름을 바꾸지 않고 같은 이름이면 덮어쓸지 물으므로 그 케이스가 생기지 않지만, `.wbpj` 손 배치·`material` 브라우즈처럼 다른 등록 창구가 열리면 재판정이 필요하다 |
| **12** | **형태 B·C 의 `fingerprint` 대상** | `fingerprint` 는 스칼라 하나인데 **B 는 파일이 둘**(`part` + `template`)이고 **C 는 실체가 폴더**다. `rwFileSha256` 은 디렉토리에서 `QFile::open` 이 실패해 **빈 문자열**을 낸다(`controller/DashRwSession.cpp:1051-1054`) — 형태 C 를 그대로 등록하면 지문이 빈다. 역할별 지문 맵으로 바꿀지 · 대표 파일 하나만 잡을지 · 폴더 전량을 해싱할지(등록 1회 비용이 폴더 크기에 걸린다) |
| **13** | **메모 캐시 키 정규화** | `rwFileSha256` 의 캐시 키가 raw `QString` 이라 [Add File] 의 `destPath` 와 파싱의 `canonicalFilePath()` 가 갈리면 같은 파일을 두 번 해싱한다(2.2). **이 문서는 호출부에서 canonical 을 넘기는 것으로 계약을 정했으나**, 함수 안에서 정규화할지(호출부 실수를 막지만 노출 함수 계약이 바뀐다) 밖에 둘지는 미정 |
| **14** | **RW 쪽 `sha256`·`deckChanged` 처분과 Identity 키 규칙** | 2.2 · 1.3. 소비자가 0곳이라 `deckChanged` 는 지금 지워도 회귀가 없고, 비교 대상을 앞단 동결 지문으로 바꾸면 **제자리 수정이 반복해서 잡힌다**(추가 I/O 0). **`ref_` 와 content uuid 의 통일은 이것과 한 묶음**이고 선결이 **Identity `models` 의 키다** — 지금 절대 canonical 경로라 프로젝트를 옮기면 저장소 전량이 미스가 되고, 상대경로로 바꾸면 프로젝트 밖 deck 을 담지 못한다. 이 문서는 **셋 다 후속으로 뗐다** |
| **15** | **레지스트리 캐시의 수명** | 2.3. `DashAnalysisModelContextRegistry` 에 `erase`·`clear` 가 **0건**이라 컨텍스트가 프로세스 수명이다. 포인터가 죽지 않는 이득이 있지만 **프로젝트를 닫아도 이전 프로젝트의 deck 이 캐시에 남는다.** 닫을 때 비울지 · 비운다면 raw 포인터를 든 곳이 있는지 먼저 재야 한다 |
| **16** | **같은 deck 을 보는 두 Set 의 편집 공유** | 2.3. 캐시 히트로 컨텍스트를 공유하는데 Condition 의 Value 편집이 deck 으로 먼저 가므로 한쪽 편집이 다른 쪽에 보인다. 현행과 같아 회귀는 아니지만, `upstream` 분리 후 "Set 이 독립됐다" 로 읽히는 자리다. 의도된 공유로 둘지 · 경고를 띄울지 |

---

## 8. 검증 한계

| 항목 | 근거 강도 | 비고 |
|---|---|---|
| 0.3-1 — `loadSetsFromConfigs()` 호출부 0곳 | **강** | `7024e04` 전 레포 grep. `QMetaObject::invokeMethod` 경유 호출은 미확인 |
| 0.3-2 · 4.2 — variant 검출기 4종과 호출부 | **강** | 정의 4 · 호출부 8(내부) + 3(외부) 전수 |
| 0.3-4 · 2.6 — `Selected Design Variables` 라이터 2 · 리더 4 | **강** | 키 문자열 전 레포 grep |
| 2.2 — `[Add File]` 등록 지점 2곳과 버려지는 `origin` | **강** | 함수 전문 확인 |
| 2.2 — 두 함수의 역할 분리 · Identity 저장소 생성 시점 | **강** | `rwFileSha256`(`:1030-1066`)은 Identity 저장소를 참조하지 않고, 그 파일은 `rwResolveContentIdentity`(`:1140-1144`)가 만들며 호출부가 `DashRwSession::load`(`:1386`) 하나다 |
| 2.2 — 두 지문의 다이제스트 동일 · 갱신 규칙 갈림 | **강** | `rwResolveContentIdentity` 가 `rwFileSha256` 을 부르는 것(`:1099`), bare hex 저장(`:1059`·`:1136`), 매 open 무조건 덮어쓰기(`:1136`) 전부 본문 확인 |
| 2.2 — bare hex 통일 (0.3-6) | **중** | 현행이 bare 라는 것과 접두사 선례 0건은 실측이고 **통일 판정은 결정**이다. 되돌리기 어려운 축(첫 배포 후 형식 변경 = 스키마 변경)이라 배포 전 확정 대상이다 |
| 2.2 — `deckChanged` 의 GUI 소비자 0곳 | **강** | `view/` · `viewmodel/` · `model/` 전량 grep. 노출은 `DashRwSession.h:141` · `DashAnalysisModelContext.h:95` 둘 |
| 2.2 — "RW 가 동결 지문과 견주면 제자리 수정이 잡힌다" | **중** | **제안이다.** RW 가 열 때 현재 해시를 이미 계산한다는 것은 실측이고, 비교 대상 교체가 실제로 그 효과를 내는지는 실행으로 확인하지 않았다 |
| 2.2 — 같은 파일 2회 해싱 | **중** | 캐시 키가 raw `QString`(`:1037`·`:1045`)이고 파싱이 `canonicalFilePath()` 를 넘기는 것(`:1386`)은 실측이다. **두 경로 문자열이 실제로 갈리는지는 플랫폼별 실행으로 확인하지 않았다** — Windows 대소문자·구분자 정규화에 따라 히트할 수도 있다 |
| 2.3 — 활성 컨텍스트 호출부 처분 | **중** | 좌표는 실측이고 **유지/교체 판정은 제안**이다. `view/DashOptimizerWidget.cpp:1556-1557` 은 하류라 세지 않았다 |
| 2.3 — 레지스트리 소유·수명 · `setActiveContext` 의 렌더 부작용 | **강** | `unique_ptr` 맵(`.h:54`) · raw 반환(`.cpp:20`·`:30`·`:47`) · `erase`/`clear` 0건 · `updateActor` 가 actor 교체와 카메라 리셋(`.cpp:77-107`) 전부 본문 확인 |
| 2.3 — Condition·CAD 모델의 기존 인스턴스별 배선 | **강** | `m_loadedFilePath` · `getContext()` · `refreshFromLoadedAnalysis` 정의와 호출부(`view/…Widget.cpp:375`·`:416`) 확인 |
| 2.3 — `DashGeometryParameter::m_fileName` 호출부 0곳 | **강** | 헤더 인라인 setter·getter 둘뿐이고 `.cpp` 대입 0건, 전 레포 호출부 0건 |
| 2.5 — 정의 라이터 4종 | **중** | 앞단 한정. 같은 파일을 쓰는 다른 경로가 있는지는 재지 않았다 |
| 2.6 — `input_files[]` 역할 실측 | **중** | 필드 3종과 라이터·리더 좌표는 실측이고, **역할별 개수는 여전히 미측**이다 (기반 문서 7.2-8 이 그대로 남는다) |
| 3절 배지 전수 | **중** | 계보 크기에서 유도한 것이고 건별 재판정은 하지 않았다 |
| 5절 순서와 verify | **중** | 제안이다. 각 verify 가 현행 UI 로 실제 수행 가능한지는 확인하지 않았다 |
| 6.2 계열 3안 대조 | **강** | 세 문서의 명시 진술을 인용한 것이다 — 안 β `input.json`(정의 본문 스냅샷 · 전 모듈) · 엣지 3종 안이 스냅샷을 뺀 근거 · 정의 버전 최소안의 지문 1종 |
| 6.2 판정 5항 | **중** | 대조는 실측이고 **판정은 제안**이다. 특히 3항의 "손실 AL 1건" 은 앞단 계보 크기에서 유도한 것이고 실제 구현량으로 재지 않았다 |
| 1.3 — `dash::core::UUID` 가 현행 ID 타입 · 헤더가 링크에 있음 | **강** | `controller/DashRwSession.cpp` 사용처와 `controller/DashRwClient.h:17` include 확인 |
| 1.3 — v5 API 가 v7 이전부터 있음 · v7 은 `feat/uuid-v7` 미머지 | **강** | CoreLib 워킹카피에서 `dc8c9be^` 헤더와 `git branch --contains` 대조. 태그 0개 |
| 1.3 — **벤더된 판에 무엇이 있나** | **없음** | `external/` 이 이 머신에 없어(gitignore `:475-477`) 확인 못 했다. 미결 9 |
| 1.3 발급 판정 (v5 · 경로/이름 기반) | **중** | 근거는 실측이고 **판정은 제안**이다. 네임스페이스 상수 2개의 자리와 중복 등록 규칙이 미결 10·11 로 남는다 |
| 1.3 — Identity 키가 절대 canonical 경로 · 이동 시 미스 | **강** | 키 삽입(`controller/DashRwSession.cpp:1122`·`:1137`)과 호출부 인자(`:1386` — `fi.canonicalFilePath()`) 확인. **이동 후 거동을 실행으로 재현하지는 않았다** |
| 실행 검증 | **없음** | 빌드 · 실행 없이 정적 근거만 |

## 관련 문서

[Project-Manifest-1-Context-Registry-And-Model-Identity](Project-Manifest-1-Context-Registry-And-Model-Identity.md) — 미결 14(Identity 키 규칙)를 닫는다. `ref_` 가 content uuid 를 겸하면 `AnalysisModelIdentity.json` 이 할 일을 잃는다.
