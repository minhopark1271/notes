# 정의 버전 최소안 — 자료 설계와 배선 설계

> 관련 Issue: #239
>
> **이 문서는 단독으로 읽힌다.** 범위 7항목의 스키마 · 판정 · 배선 · 순서가 전부 여기 있다.
>
> * [[Project-Store-Design-Edge-Complete-Minimal]] — 이 안의 **직계 상위**. 매니페스트 · 전역 ID 2종 · 엣지 3종 · 승격을 그대로 받고 **run 파일(`.dproj/outputs/{inst}.json`)을 뺀다.** 그 결과 지문이 3종에서 1종으로 줄고, 지문의 자리가 계보 파일이 아니라 소비자 SM 안이 되며, 배지가 6종에서 2종이 된다. **계보의 범위도 갈린다** — 그쪽은 산출 `rev` 가 상류 재실행마다 올라 전파가 한 칸씩 내려가므로 직속만 들면 되지만, 이 안은 그 값이 없어 계보가 **조상 전량**이어야 한다(1.5)
> * [[Project-Store-Design-Alpha-Minimal]] — 이 안의 **하위**. 그쪽은 지문이 아예 없어 상위 변경이 화면에 드러나지 않는다. 이 안은 정의 지문 하나로 그 자리를 연다
> * [[Project-Store-Design-Layer-Cut]] — 본체(안 β). 물리 재배치 · 실행 개체화 · 로컬 ID 6종이 그쪽이고 이 안은 셋 다 받지 않는다
> * [[Project-Store-Design-Dependency-State-Display]] — 배지의 화면 층. 배지를 2종으로 줄이면 그쪽 3층 중 트리 아이콘과 착수 차단만 남는다
> * [[Project-Store-Design-Wiring-Project-To-Launcher]] — 이 안의 **배선 파생**. 자료·판정 설계를 그대로 받고 동선을 프로젝트 생성 → [Add File] → 파싱 → Geometry → Condition → AnalysisLauncher 여섯으로 잘라 함수 좌표에 앉힌다. `7024e04` 재실측으로 **3.5 가 지목한 `loadSetsFromConfigs()` 는 호출부가 0곳**이고 열기의 실체가 `restoreExistingModules()` 임이 드러났다 · variant 검출기 2종 → 4종 · 7.2-8 의 AL `references[]` 실측을 `input_files[]` 3필드까지 좁힘 · 앞단은 지문 제외 키가 AL 하나뿐이라 나머지 셋이 전문 해시
>
> 실측 기준: `dev` @ `4c7608e`. 빌드·실행 검증 없음, 정적 근거만.

> ## ⚠ 문서 상태: 구상 — 확정 아님
>
> 팀 합의 전 · 착수 승인 전. 여기의 키 이름을 계약으로 인용하지 않는다.

## 개요

**목적 셋만 범위에 넣고 둘을 후속으로 뗀 판이다.**

|        | 목적                                         | 이 안       |
| ------ | ------------------------------------------ | --------- |
| 넣는다    | 프로젝트 매니페스트 — 해석 기준 모델이 무엇인지 정의하는 객체와 파일    | 1.2 · 3.3 |
| 넣는다    | 모듈의 정의·버전 기록과 ID 부여                        | 1.3 · 1.4 |
| 넣는다    | 모듈 Set 별 상위 의존성 기록과 최신성 확인                 | 1.5 · 2절  |
| **뗀다** | 정의와 실행 상태가 한 파일에 있는 구조 해소 (도구 되쓰기 · 폴링 포함) | 6절        |
| **뗀다** | 프로젝트 상태를 하나의 root 에 모듈 단위로 분해              | 6절        |

신설 파일은 **`.dproj/reference.json` 하나**이고, 나머지는 전부 현행 `configs/{Module}_{Set}.json` 에 최상위 키 6개를 더하는 것이다(그중 `variant` 는 이미 쓰이는 키다 — 1.3). 파일을 옮기지도 지우지도 않으므로 구프로젝트를 거부하지 않고 **승격으로 1회 흡수**한다.

**범위를 이렇게 자르면 설계 둘이 강제된다.** 자유롭게 고를 수 있는 자리가 아니다.

| 강제되는 것                       | 왜                                                                                                                                                       |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **버전은 쓰기 트리거가 아니라 내용이어야 한다** | 실행 상태가 정의와 같은 파일에 남으므로(뗀 첫째), 버전을 "저장 횟수" 나 "저장 시각" 으로 세면 상태 전이 한 번마다 올라 하류가 실행 내내 낡은 것으로 보인다. `definitionVersion` = SM 에서 실행 상태 키를 뺀 나머지의 sha256 (1.4) |
| **계보는 직속이 아니라 조상 전량이어야 한다**  | 산출 지문을 담을 run 파일이 없으므로(0.2), 직속만 들면 조상의 정의 변경이 하류에 **영구히** 닿지 않는다. 상위가 재실행할 때 오르는 값이 없어 전파가 따라 내려갈 것도 없다. `consumed` 가 조상 전량을 든다 (1.5)                  |

---

## 0. 전제

### 0.1 범위 7항목

| #   | 항목                                                          | 자리              |
| --- | ----------------------------------------------------------- | --------------- |
| 1   | `reference.json` + Reference 관리 인스턴스                        | 1.2 · 3.1 · 3.3 |
| 2   | 모듈 config 에 `id` 부여                                         | 1.3 · 1.6       |
| 3   | `definitionVersion` = 정의 블록 지문 (실행 상태 키 제외)                 | 1.4             |
| 4   | `upstream` 에 상위 ID + 소비 시점 버전 기록                            | 1.5             |
| 5   | 읽기 배선 — 열기 시 상위 복원 · 모듈 진입 시 전역 대신 자기 `upstream.references` | 3.3             |
| 6   | 최신성 판정 + 배지 2종 + `consumed` 갱신 시점                           | 2절              |
| 7   | 열기 시 `id` 미보유 config 승격                                     | 3.5             |

### 0.2 변경 영향

| 축                     | **이 안**                         |
| --------------------- | ------------------------------- |
| 신설 파일                 | **`reference.json` 1종**         |
| 인스턴스 색인               | **없다 — config 자기신고**            |
| 지문                    | **1종 — 정의 sha256**              |
| 실행 추적                 | **없다**                          |
| 배지                    | **2종 — `⚠ Stale` · `✕ Broken`** |
| 계보의 범위                | **조상 전량** — 직속 + 그 위 전부         |
| 상위 재실행 감지             | **못 한다** — 2.3                  |
| 파일 이동 · 도구 계약 · 로컬 ID | **안 한다**                        |
| 기존 프로젝트               | **승격**                          |

### 0.3 이미 레포에 있는 것 — 신설이 아니라 이관인 것 셋

착수 전에 알아야 할 실측이다. **셋 다 이 안이 처음 만드는 것이 아니다.**

| 있는 것                                   | 좌표                                                                                                                                                                     | 이 안에서                                                                     |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| **스트리밍 sha256 + `(size, mtime)` 메모이즈** | `rwFileSha256()` `controller/DashRwSession.cpp:1029-1065`                                                                                                              | `[Add File]` 지문 계산에 그대로 쓴다. 파일 static 이라 노출만 필요하다                         |
| **deck 파일마다 안정 UUID + 지문 저장소**         | `{configs}/AnalysisModelIdentity.json` — `rwIdentityStorePath()` `:1067-1073` · `rwResolveContentIdentity()` `:1090-1146`. 형식은 `models{canonicalPath: {uuid, sha256}}` | **흡수하지 않고 그대로 둔다**(1.2 말미). 다만 승격이 그 키 목록을 `references[]` 의 씨앗으로 읽는다(3.5) |
| **파일 경로별 해석모델 컨텍스트 레지스트리**             | `DashAnalysisModelContextRegistry` `controller/DashAnalysisModelContextRegistry.h` — `filePath → context` 맵 + `setActiveContext`/`activeContext`/`activeFilePath`      | **이미 다중 컨텍스트를 지원한다.** 5번 배선이 바꾸는 것은 자료구조가 아니라 "어느 경로를 넘기나" 뿐이다(3.3)       |

---

## 1. 자료 설계

### 1.1 물리 배치

```
{ProjectRoot}/
   .{Project}.dproj/
      reference.json                     ★ 신설 — 기준 해석 파일 대장            PM
      configs/
         GeometryParameter_Set1.json        현행 + 최상위 키 6개                 SM
         GeometryParameter_Set1.vtp         현행 그대로 — 핸들 배열              SB
         ConditionParameter_Set1.json       동상                                 SM
         AnalysisLauncher_Set1.json         동상                                 SM
         DataPreprocessor_Set1.json         동상                                 SM
         ModelBuilder_Set1.json             동상                                 SM
         ModelRunner_Set1.json              동상                                 SM
         Optimizer_Set1.json                동상                                 SM
         AnalysisModelIdentity.json         제자리 유지 — 손대지 않는다          --
         bracket_v3.dat  spring.prt         두 번째 복사본 — 남는다              PB
      ModelBuilder_Set1/                    현행 그대로 — Sim 학습 산출          EB
   bracket_v3.inp                           [Add File] 복사본 — 자리 유지        PB
   AnalysisLauncher_Set1/                   현행 그대로 — 케이스 디렉토리와 산출 EB
   ...
```

**`references/` 디렉토리를 만들지 않는다.** `[Add File]` 은 지금처럼 `{Root}/` 로 복사하고(`DashMainWindow::onAddFileClicked` `view/DashMainWindow.cpp:2106-2189`) `references[].files` 가 그 자리를 프로젝트 상대경로로 가리킨다.

**파일명은 `{Module}_{Set}.json` 그대로다.** 승격 이후에는 그 이름을 **읽지 않는다** — 모듈·variant 판정이 전부 파일 내용에서 나온다(1.3). 이름을 ID 로 바꾸는 것은 안 β 의 디렉토리 ID 화와 같은 자리를 건드리므로 그때 한 번에 한다.

### 1.2 `reference.json` — PM

```json
{
  "$schema": 1,
  "references": [
    {
      "id": "ref_9b41e0c3f2a1",
      "label": "Bracket v3",
      "kind": "fe",
      "files": {
        "deck": "bracket_v3.inp"
      },
      "origin": "C:/work/bracket_v3.inp",
      "fingerprint": "sha256:9b41e0…"
    }
  ]
}
```

| 필드 | 내용 |
|---|---|
| `id` | `ref_` + 12-hex 난수 (1.6) |
| `kind` | `fe` \| `cad`. 모듈이 고를 수 있는 Reference 를 거르는 축 — Morphing·Condition 은 `fe` 만, CAD 는 `cad` 만 후보로 본다 |
| `files` | **역할 → 프로젝트 상대경로 맵.** 역할 어휘 4종 고정 — `deck` · `part` · `template` · `material`. Morphing 은 `.inp`(또는 `.dat`) 하나가 형상·FE 조건·해석 템플릿 3역 겸직이고, CAD 는 `.prt` + `.wbpj` 가 형상 / 템플릿으로 갈린다 |
| `origin` | 출처 기록. **해석에 쓰지 않는다** — 없어도 프로젝트가 돈다. 등록 순간에만 손에 있는 값이고 현행은 복사한 뒤 버린다 |
| `fingerprint` | 복사본 전문의 sha256. **등록 1회 계산 후 동결** |

**대장만 담고 인스턴스를 색인하지 않는다.** 여기 남을 자격은 하나다 — 인스턴스가 소유할 수 없는 것. Reference 는 인스턴스 여럿이 공유하므로(Geometry Set1 과 Set2 가 같은 `.inp` 를 본다) 그 기준을 통과하고, 인스턴스의 신원은 인스턴스 자신이 담을 수 있으므로 통과하지 못한다. 얻는 것 셋 — Set 생성·삭제·rename 이 PM 을 건드리지 않아 동기화 자리가 없고, PM 손상의 피해가 Reference 로 한정되며, 파일 이름이 `reference.json` 인 것과 내용이 일치한다.

**`AnalysisModelIdentity.json` 을 흡수하지 않는다.** 같은 파일의 sha256 을 둘이 각자 들지만 답하는 질문과 갱신 규칙이 다르다.

| | `AnalysisModelIdentity.json` | `reference.json` |
|---|---|---|
| 답하는 질문 | 이 deck 이 **지난 open 이후** 바뀌었나 — 심볼 uuid 재검증용 | 이 기준 파일이 **등록 이후** 교체됐나 — 하류 무효화용 |
| 갱신 | 세션 open 마다. `rwResolveContentIdentity` 가 비교 직후 현재 해시로 덮어쓴다(`:1136-1139`) | `[Add File]` · [다시 가져오기] 1회 |

**둘째 행이 흡수를 막는 근거다.** Identity 의 값은 매 open 마다 최신으로 갱신되므로 "등록 시점" 을 기억하지 못한다. 재사용할 것은 값이 아니라 **함수**(`rwFileSha256`)다.

#### 파일 전체 형태는 둘뿐이다

`references` 가 배열이라 항목 0개도 정상이고, 프로젝트 생성이 이 형태를 쓴다(4절). 나머지는 항목 N개다 — 항목 사이에 순서 의미가 없고 상호 참조도 없다.

```json
{
  "$schema": 1,
  "references": []
}
```

#### 항목 형태 전수 — 4종

**조합이 자유롭지 않다.** `kind` 2종 × 역할 부분집합 15가지 = 30 조합 중 실제로 서는 것은 4종이다. 후보 스캔이 확장자로 한 번 거르고(`DashReferenceFileWidget::findAnalysisFiles` `view/DashReferenceFileWidget.cpp:438-448`), 골라진 확장자마다 target 해석 분기가 따로 있어(`:666-918`) 파이프라인 진입 경로가 그만큼뿐이기 때문이다.

**A. `fe` · `deck` 1개** — 단일 해석 덱. Morphing Geometry · Condition · AL(Morphing 경로)이 드는 형태이고, **전체의 대부분이 이것이다.**

```json
{
  "id": "ref_9b41e0c3f2a1",
  "label": "Bracket v3",
  "kind": "fe",
  "files": {
    "deck": "bracket_v3.inp"
  },
  "origin": "C:/work/bracket_v3.inp",
  "fingerprint": "sha256:9b41e0…"
}
```

**B. `cad` · `part` + `template`** — NX `.prt` + Workbench `.wbpj`. AL 의 CAD 경로가 든다.

```json
{
  "id": "ref_3c7d18ab04f5",
  "label": "Spring WB",
  "kind": "cad",
  "files": {
    "template": "wb/spring.wbpj",
    "part": "wb/geom/spring.prt"
  },
  "origin": "",
  "fingerprint": "sha256:3c7d18…"
}
```

`.wbpj` 는 `[Add File]` 필터에 없어(`view/DashMainWindow.cpp:2118`) 프로젝트 폴더에 손으로 들어온다. 그리고 현행은 `.prt` 를 **`.wbpj` 디렉토리 기준 상대경로**로 적는데(`view/DashReferenceFileWidget.cpp:818-828` · 재구성은 `model/DashJobRunner.cpp:1408-1410`), `files` 는 프로젝트 상대경로라 **기준점이 다르다** — 승격이 한 번 변환한다(3.5).

**C. `fe` · `template` 1개** — FE-safe `.stli`. `[Add File]` 이 `.stli` 만 **부모 디렉토리째** 복사하므로(`view/DashMainWindow.cpp:2140-2163`) 경로가 항상 1단계 하위다.

```json
{
  "id": "ref_5e02c9d7813b",
  "label": "FeSafe Bracket",
  "kind": "fe",
  "files": {
    "template": "fesafe_bracket/project.stli"
  },
  "origin": "",
  "fingerprint": "sha256:5e02c9…"
}
```

실체가 폴더인데 `fingerprint` 는 파일 전문 sha256 이라 **`.stli` 옆 파일이 바뀌면 잡히지 않는다**(7.2-10).

**D. `fe` · `template` + `material`** — C 에 사용자 재료를 얹은 형태. **현행에 라이터가 0곳이다** — `.stlx`·`.dbase`·`.msc` 를 다이얼로그에서 파일시스템 브라우즈로 고르고 **제자리 편집**하며(`view/dialog/MaterialSetupDialog.cpp:123-152` · `:181-213`, 원본은 `.bak_{timestamp}` 로 남는다) 프로젝트 어느 파일에도 기록되지 않는다. 이 안이 처음 만드는 상태이고, 제자리 편집이라 `fingerprint` 동결과 충돌한다(7.2-11).

```json
{
  "id": "ref_a41f77b0925c",
  "label": "FeSafe Bracket · UserMat",
  "kind": "fe",
  "files": {
    "template": "fesafe_bracket/project.stli",
    "material": "fesafe_bracket/steel.dbase"
  },
  "origin": "",
  "fingerprint": "sha256:a41f77…"
}
```

#### 역할 · 확장자 대응

| 역할 | 확장자 | 후보로 뜨는 경로 | target 해석 |
|---|---|---|---|
| `deck` | `.inp` | 스캔 + `[Add File]` | instance(part) 선택 — **유무가 하류 morphing 분기 키**(`view/DashReferenceFileWidget.cpp:781-806`) |
| `deck` | `.dat` | 스캔 + `[Add File]` | part 선택 + 마스터 노드수로 자동 매칭 (`:863-918`) |
| `deck` | `.dfsxml` | 스캔 + `[Add File]` | `CBLOCK` 고정 (`:759-776`) |
| `template` | `.wbpj` | **스캔만** | 같은 트리의 `.prt` 목록 (`:811-830`) |
| `template` | `.stli` | 스캔 + `[Add File]` | 없음 — 템플릿이 자기 형상을 든다 (`:711-747`) |
| `part` | `.prt` | 스캔에 없다 — `[Add File]` 또는 `.wbpj` 의 part 콤보. CAD 는 NX 로드분을 configs 로 복사 (`view/DashGeometryParameterCADWidget.cpp:624-633`) | — |
| `material` | `.dbase`(+`.msc`·`.stlx`) | **없다** — 다이얼로그 브라우즈 | — |

**후보 목록의 정본이 셋이고 서로 다르다.** 형태를 세는 데 이것이 걸림돌이다.

| 목록 | 좌표 | 내용 |
|---|---|---|
| `[Add File]` 필터 | `view/DashMainWindow.cpp:2118-2119` | 12종 |
| 참조 후보 스캔 | `view/DashReferenceFileWidget.cpp:448` | 6종 — `.dat` `.cdb` `.inp` `.dfsxml` `.wbpj` `.stli` |
| `SupportedInputs` | `model/AnalysisFileDefines.h:28-34` | 5종 — `.dat` `.dfsxml` `.inp` `.bdf` `.wbpj` |

셋의 교집합은 `.dat`·`.inp`·`.dfsxml` 뿐이다. `.cdb` 는 스캔에만 있고 소비자가 없으며 `.bdf` 는 정의표에만 있어 화면에 뜨지 않는다 — **둘 다 형태를 만들지 못한다.** 스캔 범위는 루트 + `configs/` + 1단계 하위 디렉토리라(`:446-493`) `files` 의 경로도 그 세 자리 중 하나다.

#### 같은 형태가 여럿 서는 자리

| 형태 | 서는가 | 근거 |
|---|---|---|
| 같은 파일을 두 번 등록 — 다른 `id` · **같은 `fingerprint`** | **선다. 막지 않는다** | 라벨과 등록 시점이 다를 수 있고, 소비자는 `ref_` 로만 견주므로(2.1) 중복이 판정을 흐리지 않는다 |
| 한 AL Set 이 Reference 여럿을 듦 | **선다** | `input_files[]` 가 N행이고 라디오로 고른 1행만 실행 템플릿이다 (`view/DashReferenceFileWidget.cpp:1090-1132` · `view/DashAnalysisLauncherWidgetBase.cpp:195-215`). `upstream.references[]` 가 그만큼 길어진다 |
| 같은 역할 파일이 한 항목에 둘 (`.prt` 2개) | **못 선다** | `files` 가 역할 → 경로 **맵**이다 (7.2-5) |
| 역할 없는 확장자 (`.vtk` `.vtu` `.rst` `.odb` `.csv` `.stp` `.step`) | **못 선다** | `[Add File]` 로 들어오지만 역할 어휘 4종에 자리가 없다 (7.2-2) |

**승격이 만드는 것은 A 뿐이다.** 씨앗인 Identity `models` 가 rw 세션이 연 덱만 담고(`controller/DashRwSession.cpp:1385`), 키가 canonical 절대경로라 프로젝트 밖에서 연 덱은 상대화되지 않아 버려진다. B·C·D 는 사용자가 다시 등록해야 선다.

### 1.3 SM 에 더하는 최상위 키 6개

정의 본문은 한 줄도 건드리지 않는다. `DV-Geometry` · `DV-Condition` · `Morphing.*` · `Independent/Dependent Parameter` · `DOE configuration` · `Dataset` · `Data Label` · `Configuration` · `Model upload` · `Optimization` 전부 현행 스키마 그대로다.

```json
{
  "$schema": 1,
  "id": "inst_4d19b2a70e55",
  "module": "AnalysisLauncher",
  "variant": "Init",
  "definitionVersion": "sha256:1c07af…",
  "upstream": { … },

  "DOE configuration": { … }        // 현행 본문 — 손대지 않는다
}
```

| 키 | 내용 |
|---|---|
| `$schema` | `1` 부터 |
| `id` | `inst_` + 12-hex 난수. Set 생성 시 발급 |
| `module` · `variant` | **자기신고.** 승격 이후 판정이 전부 여기서 나온다. `variant` 는 현행에도 이미 쓰이고 있다 — `DashModelBuilder.cpp:475` 가 `rootObj["variant"] = "Sim"` 을 쓰고 `detectBuilderVariant`(`DashProject.cpp:658`)가 그것을 1순위로 본다. **이 안은 키를 새로 만드는 것이 아니라 폴백을 없앤다** |
| `definitionVersion` | 1.4 |
| `upstream` | 1.5 |

**`label` 은 두지 않는다.** Set 이름은 파일명이 계속 들고 rename 은 현행대로 파일 rename 이다(`DashProject::renameSet` `model/DashProject.h:87`). 라벨을 필드로 옮기는 것은 파일명 ID 화와 한 묶음이라 이 안 밖이다.

**모듈 어휘는 현행 유지.** `GeometryParameter` · `ConditionParameter` · `AnalysisLauncher` · `DataPreprocessor` · `ModelBuilder` · `ModelRunner` · `Optimizer`. 정본은 `DashIOController::getModuleName()` 과 `ModuleType` enum 이다.

### 1.4 `definitionVersion` — 정의 블록 지문

**값 = SM 에서 실행 상태 키와 계보를 뺀 나머지를 정규 직렬화한 것의 sha256.** 저장 필드이고, 정의 저장 헬퍼가 쓰기 직전에 계산해 넣는다(3.4).

#### 무엇이 들어가고 무엇이 빠지나

| | 대상 | 근거 |
|---|---|---|
| **포함** | 모듈 정의 본문 | 이 값이 답하는 것이 "정의가 바뀌었나" 다 |
| **포함** | `upstream` 의 3배열 | **빼면 안 된다.** 상위 재선택이 지문을 움직이지 않으면, 하류가 든 계보(1.5)가 낡은 조상을 가리킨 채 "안 바뀌었다" 로 판정한다 — AL 이 상위 Geometry 를 Set1→Set2 로 바꿨는데 Set1 이 그대로면 DP 가 최신이라고 본다 |
| **제외** | 실행 상태 키 | 아래 표. 전이마다 지문이 움직이면 안 된다 |
| **제외** | `upstream.consumed` | 계보는 정의가 아니다. 포함하면 실행 착수가 지문을 올리는데, **추가로 잡히는 것이 없다** — 조상이 바뀌어 `consumed` 값이 달라졌다면 하류는 이미 자기 계보로 그것을 잡고, 안 달라졌다면 해시도 그대로다 |
| 제외 | `definitionVersion` 자신 | 자기 참조 |

#### 제외 키 — 블랙리스트

| 모듈 | 제외하는 키 | 실측 |
|---|---|---|
| GeometryParameter (Morphing · CAD) | 없다 — 실행이 없다 | — |
| ConditionParameter | 없다 | — |
| AnalysisLauncher | `DOE Table` · `DOE Analysis` | 케이스 상태가 `DOE Table.samples[].status` 또는 `status_{analysisType}` 에 산다. 라이터는 `DashDoeConfigManager::setSampleStatus()` `model/DashDoeConfigManager.cpp:527-556` — 전이 1회마다 SM 전문을 read-modify-write 한다 |
| DataPreprocessor | `DOE Table` · `Data Analysis` | `saveDoeTableSnapshot` 이 상류 DOE 표와 `output[analysisType]` 을 자기 config 에 복사해 넣는다(`model/DashDataProcessor.cpp:2700-2727`). 최상위 키는 `Dataset` · `DOE Table` · `Data Analysis` 셋뿐이라 정의는 `Dataset` 하나다 |
| ModelBuilder (Sim · MCU) | `Configuration.*.status` · `Configuration.*.error` | **최상위 블록이 아니라 중첩 키다.** `Configuration.{model}` 한 객체 안에 학습 옵션(정의)과 `status`·`error`(실행 상태)가 섞여 있다 — `DashModelBuilder.cpp:461-471`(기본값 삽입) · `:645`(`"In Progress"`) · `:1445-1448`(`finalizeStaleStatuses` → `"Failed"`) · MCU 는 `DashModelBuilderMCU.cpp:511-512` · `:590` · `:699` |
| ModelRunner · Optimizer | — | 소비자가 없어 비교되지 않는다. 필드는 붙되 읽히지 않는다 |

**블랙리스트인 이유는 실패 방향이다.** 화이트리스트로 정의 키를 열거하면 새 정의 키를 추가하는 사람이 목록을 잊었을 때 그 변경이 지문에 안 잡혀 **하류가 낡은 줄 모른다**(미탐). 블랙리스트면 모르는 키가 정의로 간주돼 **헛된 `Stale`** 이 뜬다(오탐). 배지는 착수를 막지 않는 경고이므로 오탐 쪽으로 실패해야 한다.

**`Configuration.*` 의 중첩 제외가 이 목록에서 유일하게 단순 최상위 키가 아니다.** 제외 규칙을 `("Configuration", "*", "status")` 같은 경로 패턴 목록으로 두고, 지문 계산기가 그 패턴에 걸리는 노드만 지운 사본을 해시한다.

#### 왜 지문인가 — 카운터를 쓸 수 없는 이유

[[Project-Store-Design-Edge-Complete-Minimal]] 4.3 은 정의 버전을 단조 정수 `rev` 로 두고 정의 저장 헬퍼가 +1 한다. **그 안에서는 성립하지만 이 안에서는 성립하지 않는다.**

| | `rev` 카운터 | 정의 블록 지문 |
|---|---|---|
| 근거 | **쓰기 트리거** — 저장하면 오른다 | **내용** — 정의가 달라져야 바뀐다 |
| 실행 상태가 같은 파일에 있을 때 | 케이스 전이 · 학습 상태 전이마다 오른다. DOE 80케이스면 실행 1회에 80회 이상 | 실행 상태 키를 뺐으므로 **움직이지 않는다** |
| 값을 고쳤다 되돌리면 | 두 칸 올라 헛된 `Stale` | 같은 값 — 오탐 없음 |
| SB(`.vtp`) 변경 | 정의 저장이 곧 `.vtp` 재작성이라 함께 덮인다 | **못 잡는다** — 핸들 위치만 옮겨 SM 바이트가 그대로면 지문이 같다 |
| 계산 비용 | 0 | SM 1개 파싱 + 해시. 수 KB\~수백 KB 라 무시 가능. **SB 는 해시 대상이 아니다** |

**첫 두 행이 결정한다.** 정의와 실행 상태 분리를 후속으로 뗀 것이 이 안의 전제이므로, 버전은 대상 기반이어야 한다. 저장 시점·mtime 도 같은 이유로 기각된다 — 실행 상태 쓰기가 그 값을 올린다.

**넷째 행이 대가다.** Morphing 핸들의 선택 집합이 바뀌면 `filterSelectedHandles`(`viewmodel/DashGeometryParameterPresentationModel.cpp:171-323`)가 SM 의 handle id 를 새 인덱스로 치환하므로 지문이 움직인다. 위치만 옮긴 편집은 SB 에만 남아 사각이다. SB 를 지문 대상에 넣으려면 수백 MB 파일을 저장마다 해시해야 하므로 넣지 않고, 잡으려면 `(size, mtime)` 을 지문에 섞는 방법이 있으나 프로젝트 복사가 mtime 을 어떻게 다루는지에 결과가 달려 **미결로 남긴다**(7절 3번).

**정규 직렬화 규칙이 필요 없다.** 값이 한 자리(정의 저장 헬퍼)에서만 생산되고 소비자는 그 문자열을 그대로 복사해 비교하므로, Qt 버전이 바뀌어 직렬화가 달라져도 다음 저장 때 양쪽이 함께 움직인다. 읽기 시점에 계산하는 방식이었다면 정규화가 계약이 됐을 것이다.

**제외 키 목록이 버려지는 작업이 아니다.** 그 목록이 곧 후속 "정의와 실행 상태 분리" 의 절단선이다 — 지금 지문에서 빼는 키가 그때 실행 메타로 나갈 키다.

### 1.5 `upstream` — 엣지와 계보

**두 역할을 한 블록에 담되 형과 범위를 가른다** — 3배열은 **직속 의도**(사용자가 그 화면에서 고른 것)이고 `consumed` 는 **계보 전량**(직속뿐 아니라 그 위로 도달하는 조상 전부)이다.

DataPreprocessor 예시. 직속은 AnalysisLauncher 하나인데 `consumed` 는 넷을 든다.

```json
"upstream": {
  "references":  [],
  "definitions": [],
  "executions":  ["inst_4d19b2a70e55"],
  "consumed": {
    "inst_4d19b2a70e55": "sha256:0a7c31…",   // AnalysisLauncher — 직속
    "inst_7f3a2c1b04de": "sha256:1c07af…",   // Geometry         — 상속
    "inst_1e55da62c9f7": "sha256:44b2d0…",   // Condition        — 상속
    "ref_9b41e0c3f2a1":  "sha256:9b41e0…"    // deck             — 상속
  }
}
```

| 키 | 형 | 범위 | 갱신 |
|---|---|---|---|
| `references` · `definitions` · `executions` | 배열 · 순수 ID | **직속만** | 고르는 순간 |
| `consumed` | 맵 · ID → 버전 | **소비 시점의 조상 전량** | 마지막 소비 시점 1회 (2.2) |

**`consumed` 의 키 집합은 3배열의 초집합이다.** 조상이 직속 배열에 없이 여기에만 있는 것이 정상이다.

**"조상 전량" 에는 시점이 붙는다 — 스냅샷이지 현재 상위의 조상 목록이 아니다.** 내가 소비한 순간의 조상이 들어 있고, **그 이후 상위가 새로 얻은 조상은 들어오지 않는다.** 라이브 뷰로 읽으면 2.1 의 `Broken` 판정을 오해한다.

**계산은 두 항이고 값의 출처가 서로 다르다.**

```
내 consumed = { 직속 각각 : 그 직속의 현재 definitionVersion }   ← 지금 내가 소비했으므로 현재 값
            ∪ { 직속들의 consumed 를 그대로 }                     ← 직속이 소비한 판 = 내가 간접 소비한 판
```

**둘째 항을 "조상을 훑어 현재 값으로 채우기" 로 바꾸면 설계가 무너진다.** 그러면 Geometry → AL → DP 사슬에서 AL 을 건너뛰고 DP 만 재실행해도 DP 가 최신 Geometry 버전을 적어 `Stale` 이 풀리는데, AL 산출은 여전히 옛 Geometry 기반이다. 물려받는 방식이면 AL 이 아직 옛 값을 들고 있으므로 DP 도 옛 값을 받아 **`Stale` 이 풀리지 않는다** — 순서를 강제하는 코드 없이 순서가 지켜진다(2.2).

**빈 배열을 생략하지 않는다.** 판정이 "키가 있나" 를 먼저 묻지 않아야 한다. 하위 키를 모듈별 이름(`design_space` · `dv_table` · `model_source` …)이 아니라 엣지 종류별 공통 키로 두는 것도 같은 이유다.

**엣지 저장 규칙 셋.** 소비자가 소유한다(생산자는 자기 소비자를 모른다) · 역방향은 저장하지 않고 로드 시 계산한다 · 경로·파일명·Set 이름이 아니라 ID 를 가리킨다.

#### 직속 엣지 — 사용자가 무엇을 고르나

| 소비자 SM | `references[]` | `definitions[]` | `executions[]` |
|---|:---:|:---:|:---:|
| `GeometryParameter_{Set}.json` · Morphing | O — `deck` | — | — |
| `GeometryParameter_{Set}.json` · CAD | O — `part` | — | — |
| `ConditionParameter_{Set}.json` | O — `deck` | — | — |
| `AnalysisLauncher_{Set}.json` | O — variant 별로 갈린다 | O — Geometry · Condition | — |
| `DataPreprocessor_{Set}.json` | — | — | O — AnalysisLauncher |
| `ModelBuilder_{Set}.json` | — | — | O — DataPreprocessor |
| `ModelRunner_{Set}.json` | — | — | O — ModelBuilder |
| `Optimizer_{Set}.json` | — | — | O — ModelBuilder |

**앞선 판의 표를 세 자리 고쳤다.** [[Project-Store-Design-Edge-Complete-Minimal]] 6.2 는 ModelRunner 에 `references[]`(deck) · `definitions[]`(Geometry) 를 주고 Optimizer 에는 주지 않으며, Geometry 의 두 variant 를 한 행에 뭉친다. 실측으로 보면 **ModelRunner 와 Optimizer 가 같고, 둘 다 직속이 아니다.**

| 실측 | 좌표 |
|---|---|
| ModelRunner 와 Optimizer 는 **같은 일을 하는 다른 함수로** Geometry 정의 · 그 `.vtp` · deck 셋 다에 닿는다 — 표가 Optimizer 를 빠뜨렸다 | `DashModelRunner::resolveReferenceFileInfo` `model/DashModelRunner.cpp:1505-1568` · `findGeometryParameterFile` `model/DashOptimizer.cpp:1310-1341` |
| 그 경로가 **상위가 낸 EB 파일에 박힌 파일명 조인**이다 | `model_info.json.parameter[*].source` 가 `"GeometryParameter_Set1.json"` 같은 **파일명**이고 그것을 configs 디렉토리와 조립해 연다(`DashModelRunner.cpp:1512-1513` · `DashOptimizer.cpp:1318-1322`) |
| deck 은 거기서 한 단 더 들어간다 | 연 Geometry 정의의 `DV-Geometry[*].source` = `"Morphing\|part1.dat\|COMPONENT-1"` 의 **둘째 마디가 deck 파일명**이다(`DashModelRunner.cpp:1525-1533`). `.vtp` 는 같은 basename(`:1521` · `DashOptimizer.cpp:1329-1331`) |
| Condition 도 같은 순회에서 읽는다 | `else if` 가지가 `ConditionParameter_*.json` 의 `DV-Condition[*].source` 를 연다(`DashModelRunner.cpp:1549-1566`) |

**그래서 그 셋은 직속이 아니라 상속으로 들어온다.** 두 화면에서 사용자가 고르는 것은 ModelBuilder 폴더 하나뿐이고 Geometry·Condition·deck 은 고르지 않은 채 따라온다. 직속 배열에 적으려면 고르는 UI 를 새로 만들어야 하는데 그것은 이 안 밖이다. **`consumed` 가 지금 그 파일명 조인이 하던 일을 ID 조인으로 대체한다** — 파일명이 스키마 노릇 하는 자리가 여기서 하나 닫힌다(3.2-7).

**`AnalysisLauncher` 의 `references[]` 는 variant 별로 갈린다.** Morphing 경로는 `deck` 하나가 형상·FE 조건·해석 템플릿 3역을 겸하고, CAD 경로는 `part` + `template`(`.wbpj`), FE-safe 는 `template`(`.stli`) + `material` 이다. 현행은 이것이 `input_files[]` 의 `{name, target_component, path}` 와 확장자 분기에 흩어져 있어 **역할별 실측이 아직 없다** — 7.2-8 로 남긴다.

**`references[]` 가 배열인 것은 FE-safe 때문이다.** 같은 Set 안 다른 템플릿이 낸 ODB 를 입력으로 받으므로 단수로는 그 모듈이 서지 않는다. 뒤에 배열로 바꾸는 것은 스키마 변경이다.

#### `consumed` 전량 — 인스턴스마다 무엇이 들어가나

Morphing 경로 기준이다. **각 행이 앞 행을 포함한다** — 상속분이 직속의 `consumed` 를 그대로 물려받기 때문이다.

| 인스턴스 | 직속 (3배열) | 상속 (직속의 `consumed`) | 크기 |
|---|---|---|:---:|
| Geometry · Morphing | `ref_`deck | — | 1 |
| Geometry · CAD | `ref_`part | — | 1 |
| Condition | `ref_`deck | — | 1 |
| AnalysisLauncher | `ref_`deck · `inst_`Geo · `inst_`Cond | `ref_`deck — **직속과 같은 것이라 접힌다** | 3 |
| DataPreprocessor | `inst_`AL | `ref_`deck · `inst_`Geo · `inst_`Cond | 4 |
| ModelBuilder | `inst_`DP | 위 + `inst_`AL | 5 |
| ModelRunner | `inst_`MB | 위 + `inst_`DP | 6 |
| Optimizer | `inst_`MB | 위 + `inst_`DP | 6 |

**AnalysisLauncher 행이 맵이라는 형을 정당화한다.** deck 에 직속으로도 닿고 Geometry·Condition 경유로도 닿는데, 같은 시점에 계산하므로 값이 같고 키가 하나로 접힌다. 배열이면 같은 deck 이 세 번 들어간다.

**ModelRunner 와 Optimizer 는 형제라 서로를 담지 않는다.** 둘 다 6이고 집합이 같다 — 파이프라인 말단 둘이 같은 ModelBuilder 실행을 보기 때문이다.

**CAD·FE-safe 경로는 한두 항목이 더 붙는다.** AnalysisLauncher 의 직속이 `part` + `template`(+ FE-safe 는 `material`) 로 갈리고 Condition 이 그 경로에 붙는지가 아직 미측이라(7.2-8) 하류 넷의 크기가 7 또는 8이 된다. **AL 이 계보의 뿌리라 그 실측이 이 표 전체를 정한다.**

#### 직속만으로는 왜 안 되나

**직속만 들면 조상의 내용 변경이 하류에 닿지 않는다.** DataPreprocessor 를 예로 무엇이 바뀔 때 AnalysisLauncher 의 `definitionVersion` 이 움직이는지 세면 구멍이 정확히 두 줄이다.

| 바뀌는 것 | AL 의 `definitionVersion` | 직속만 들 때 DP 가 아는가 |
|---|---|---|
| AL 의 `DOE configuration` | 바뀐다 | 안다 |
| AL 이 상위를 재선택 | 바뀐다 — `upstream` 3배열이 지문 대상이다(1.4) | 안다 |
| deck 을 새로 등록 (새 `ref_`) | 바뀐다 — AL 의 `references[]` 원소가 갈린다 | 안다 |
| **Geometry·Condition 정의 내용** | **안 바뀐다** — AL 이 든 것은 ID 이고 ID 는 그대로다 | **모른다** |
| **deck [다시 가져오기]** (ID 유지 · 지문만 갱신) | **안 바뀐다** | **모른다** |

**굵은 두 줄이 계보를 전량으로 두는 근거 전부다.** `consumed` 에 조상이 다 있으면 둘 다 자기 파일 비교에서 잡히고, 판정에 그래프 순회가 없다.

| 항목 | 내용 |
|---|---|
| **한 단만 내려간다** | 직속의 `consumed` 를 읽으면 그 안에 이미 전량이 있다. 재귀가 아니고, 여는 파일 수가 직속 수와 같다 |
| **`consumed` 가 낡을 수 있다** | 상위가 자기 상위를 재선택한 뒤 내가 아직 안 돌렸으면 내 `consumed` 는 옛 조상을 가리킨다. 그때 상위의 `definitionVersion` 이 이미 바뀌었으므로 **`⚠ Stale` 은 그대로 뜬다** — 낡은 계보가 오판을 만드는 방향이 아니다 |
| **`Broken` 이 넓어진다** | 직속이 아닌 조상이 지워져도 뜬다. 문구가 경유 경로를 함께 말해야 한다(2.1) |

#### 왜 이것으로 닫히나 — 불변식 하나

**조상 집합 자체가 바뀌는 경우는 반드시 내 `consumed` 안의 어떤 노드가 자기 `upstream` 배열을 바꾼 데서 시작한다.** 그 변경은 그 노드의 `definitionVersion` 을 움직이고(1.4 가 `upstream` 을 지문 대상에 넣은 이유), 그 노드는 내 `consumed` 안에 있으므로 내가 잡는다. "새로 추가된 조상은 내 계보에 없어서 못 잡는다" 가 성립하지 않는 이유다 — **추가한 당사자가 계보 안에 있다.**

케이스 전수. 마지막 한 줄만 남고 일곱이 자기 파일 비교로 닫힌다.

| 바뀌는 것 | 어디서 잡히나 |
|---|---|
| 직속의 정의 본문 | 직속 항목 |
| 직속의 `upstream` 배열 — 조상 추가·교체·제거 | 직속 항목 (배열이 지문 대상이다) |
| 상속 조상의 정의 본문 | 그 상속 항목 |
| 상속 조상의 `upstream` 배열 | 그 상속 항목 |
| deck 신규 등록 (새 `ref_`) | 그것을 든 노드의 항목 — 배열 원소가 갈린다 |
| deck [다시 가져오기] (ID 유지) | `ref_` 항목 — `fingerprint` 가 갈린다 |
| 직속이 재실행 + 그 사이 조상이 바뀜 | 그 조상 항목 |
| **직속이 같은 정의로 재실행** | **못 잡는다** — 2.3 의 기지 한계 |

**"직속의 `definitionVersion` 은 그대로인데 그 직속의 `consumed` 가 바뀐" 경우에 별도 처리가 없다.** `consumed` 는 지문 대상이 아니므로(1.4) 그 상황이 실제로 생기는데, 내 `consumed` 는 물려받은 옛 값을 들고 있고 그 값이 어긋나 있으면 위 표의 셋째·일곱째 행에서 이미 잡힌다. 어긋나 있지 않다면 내 결과도 여전히 유효하다. **위쪽 두 행으로 환원되고 새 규칙이 필요 없다.**

#### 세 엣지 모두 `definitionVersion` 을 견준다

run 파일이 없으므로 "산출이 몇 번 덮였나" 를 세는 자리가 없다. 비교 대상은 ID 접두사로만 갈린다.

| ID | 현재 값을 어디서 |
|---|---|
| `ref_` | `reference.json` → `references[].fingerprint` |
| `inst_` | 그 SM 의 `definitionVersion` — **definition 엣지든 execution 엣지든 같다** |

**둘째 행이 이 안의 대가다.** 상위 정의가 바뀌면 하류가 알고, 상위가 **같은 정의로 재실행**하면 하류가 모른다(2.3).

### 1.6 ID 2종

| ID | 발급처 | 시점 |
|---|---|---|
| `ref_` | 프로젝트 컨트롤러 | `[Add File]` 등록 |
| `inst_` | 프로젝트 컨트롤러 | Set 생성 (`DashProject::createModuleJsonFile()` `model/DashProject.cpp:592`) |

**형식은 접두사 + 12-hex 난수** — `QUuid::createUuid().toString(QUuid::Id128).left(12)`. Qt 네이티브라 새 의존성이 아니고 레포에 `QUuid` 사용이 0건이라 첫 사용이다. 48비트라 항목 10⁴개에서 충돌이 약 2×10⁻⁷ 이고, 전체 UUID(41자)는 맵 키이자 로그 본문으로 읽히지 않아 쓰지 않는다.

**로컬 ID(`dv` · `rsp` · `mdl`)는 두지 않는다.** 의존성 단위가 인스턴스이므로 항목 단위 조인은 현행 이름 조인을 유지한다. 그 교체는 자료구조 교체라 영향이 호출부 전체로 퍼진다.

---

## 2. 판정 설계

### 2.1 배지 2종

```
소비자 upstream.consumed[ID]     vs     그 대상의 현재 버전
   (마지막으로 소비한 판)                (지금 무엇인가)
   ▼
다르면        ⚠ Stale    — 소비한 뒤에 상위가 바뀌었다
가리킨 ID 가 없다  ✕ Broken   — 끊긴 참조
그 외          무배지
```

| 배지 | 조건 | 착수 |
|---|---|---|
| `✕ Broken` | `upstream` 3배열 또는 `consumed` 의 키 중 하나가 `reference.json` 에도 어느 config 의 `id` 에도 없다 | **막는다** — 직속이 없으면 `consumed` 를 만들 수 없어 물리적 불능이고, 상속 키가 끊긴 경우는 가능하지만 끊긴 계보 위에 쌓는 것이라 정책으로 막는다 (아래) |
| `⚠ Stale` | `consumed` 의 값 중 하나라도 현재와 다르다 | **막지 않는다** — 착수가 `upstream` 을 그 시점의 현재로 해석해 `consumed` 를 다시 고정하므로 실행은 언제나 최신 상위를 읽는다 |

**판정 입력이 자기 파일 + 각 조상의 저장 값 하나씩이다.** `consumed` 가 조상 전량이므로(1.5) 그래프를 타고 올라가지 않는다 — 맵을 순회하며 ID 접두사로 현재 값의 자리만 고른다.

**진행도 배지 넷(`Empty` · `Draft` · `Ready` · `Complete`)을 두지 않는다.** 그것은 "상류가 준비됐나 · 내가 돌렸나" 를 말하는데, 산출 상태를 담는 자리가 이 안에 없어 판정 입력이 디스크 스캔이 된다. 최신성과 무관한 축이므로 함께 뺀다.

#### `⚠ Stale` 은 두 종류이고 해소 단수가 다르다

**어긋난 항목이 직속인지 상속인지가 그대로 규칙이다.** 상속분은 직속에서 물려받으므로(1.5), 직속이 아직 옛 값을 들고 있으면 내가 돌려도 그 옛 값을 다시 받는다.

| 어긋난 항목 | 해소 | 내가 지금 착수하면 |
|---|---|---|
| **직속뿐** | 내가 돌리면 된다 | 직속의 현재 `definitionVersion` 을 적으므로 **풀린다** |
| **상속이 섞였다** | **상위부터** | 상속분을 직속에서 다시 물려받는데 그 값이 그대로라 **풀리지 않는다** |

Geometry V1→V2 에서 AL 을 건너뛰고 DP 만 돌리면 DP 는 AL 의 `consumed{Geo:V1}` 을 그대로 받아 여전히 `Stale` 이다. AL 을 먼저 돌려 그쪽 `consumed[Geo]` 가 V2 가 되고, 그 다음 DP 가 그것을 물려받아 풀린다.

**둘째 줄에서 착수를 막지는 않되 문구로 안내한다** — 막으면 착수 경로에 판정 분기가 하나 더 붙고, `Stale` 이 경고이지 차단이 아니라는 규칙(아래)이 깨진다. 안내하지 않으면 사용자가 헛돌린다. 문구는 사유 표의 넷째 갈래가 이미 경유 경로를 말하므로 거기에 "먼저 **{직속 상위}** 를 다시 실행하세요" 를 붙인다.

#### 직속의 배지가 나에게 어떻게 옮겨오나

**전파 규칙을 따로 두지 않는다.** 아래는 계보 비교에서 저절로 나오는 결과다.

**`Broken` 은 원인이 두 갈래이고 그 갈래가 내 판정을 가른다** — 없는 ID 가 직속의 **`consumed`** 에 있는지 **`upstream` 배열**에만 있는지다. 앞은 직속이 이미 소비한 조상이 지워진 것이고, 뒤는 아직 소비하지 않은 새 상위가 지워진 것이다.

| 직속의 상태 | 나 | 왜 |
|---|---|---|
| `⚠ Stale` | **`⚠ Stale`** | 직속을 낡게 만든 항목이 내 계보에도 상속으로 있고 내가 든 값은 직속이 물려준 옛 값이라 함께 어긋난다. 참조가 끊긴 것이 아니므로 `Broken` 이 아니다 |
| `✕ Broken` — 직속의 `consumed` 키가 사라짐 | **`✕ Broken`** | 내가 그 키를 상속으로 들고 있다. 다시 소비해도 직속에서 같은 끊긴 키를 또 물려받으므로 풀리지 않는다 |
| `✕ Broken` — 직속 자신이 지워짐 | **`✕ Broken`** | 내 직속 항목의 키가 없다 |
| `✕ Broken` — 직속의 `upstream` 배열만 끊김 | **`⚠ Stale`** | 그 ID 는 직속의 `consumed` 에 없어 내게 옮겨오지 않는다. `consumed` 가 스냅샷이라(1.5) 애초에 내 계보에 든 적이 없고, 내가 보는 것은 직속의 배열 변경이 만든 `definitionVersion` 차이뿐이다 |

```
T0  내가 소비                        내 consumed = {AL:A1, GeoSet1:V1, deck:R1}
T1  AL 이 GeoSet2 를 추가로 고름       AL.definitionVersion  A1 → A2
T2  GeoSet2 삭제                     AL = ✕ Broken (배열 갈래)
    ▼
    내 키 넷은 전부 실존하고 AL 하나만 값이 어긋난다  →  ⚠ Stale
```

**넷째 행이 옳은 판정이다.** 내 결과는 AL 이 **실제로 낸 산출** 기반이고 그 산출은 GeoSet1 로 만들어졌다. AL 이 GeoSet2 를 쓰겠다는 것은 아직 의도이고 돌지 않았으므로, 내 결과가 무효한 것이 아니라 낡았다. **`Broken` 은 "다시 지목해야 한다" 이고 `Stale` 은 "다시 돌려야 한다" 인데, 여기서 지목을 고쳐야 하는 쪽은 AL 이고 그 배지는 AL 화면에 뜬다.**

**넷째 행에서 내 착수를 막지 않는다.** 착수해도 물려받는 것은 직속의 `consumed`(끊긴 키가 없다)이므로 내 계보는 온전하게 다시 고정된다 — 착수가 상태를 악화시키지 않는다. 다만 물려받는 값이 그대로라 배지는 풀리고 실질 변화가 없다. **위쪽 "상속이 섞였다" 행과 같은 처지이므로 문구만 붙인다.**

**둘째·셋째 행에서는 막는다.** 근거가 서로 다르다 — 셋째는 직속 파일이 없어 `consumed` 를 만들 수 없는 **물리적 불능**이고, 둘째는 착수가 가능하지만 **끊긴 계보 위에 새 산출을 쌓는 것**이라 정책으로 막는다. 2.1 배지 표의 "물리적으로 불가능하다" 는 셋째 행만 설명한다.

**사유는 네 갈래이고 문구를 가른다.** 어긋난 키가 **접두사와 직속 여부** 두 축으로 갈린다.

| 어긋난 것 | 문구 |
|---|---|
| `ref_` · 직속 | "기준 파일이 교체됐습니다" |
| `inst_` · 직속 (definition 엣지) | "상위 정의가 바뀌었습니다" |
| `inst_` · 직속 (execution 엣지) | "상류 설정이 바뀌었습니다" |
| **상속 — 직속 배열에 없는 조상** | "**{조상 라벨}** 이 바뀌었습니다 (**{직속 상위 라벨}** 경유). 먼저 **{직속 상위 라벨}** 을 다시 실행하세요" |

**넷째 행이 전이 전파를 대신한다.** 계보에 조상이 다 있으므로 어느 조상이 어긋났는지 알고, 직속 배열과 견주면 경유 경로도 한 단 말할 수 있다. 전파를 불리언으로 올리는 방식은 이 정보를 잃는다.

셋째 문구가 α-edge 와 다르다. 그쪽은 "상류 결과가 다시 만들어졌습니다" 인데 이 안은 결과가 아니라 **설정** 변경만 잡으므로 문구가 사실을 넘지 않아야 한다.

### 2.2 `consumed` 갱신 시점

**`consumed` 는 "이 인스턴스가 상위를 마지막으로 소비한 판" 이고, 소비의 정의가 모듈에 따라 갈린다.**

| 모듈 | 소비 = | 갱신 시점 |
|---|---|---|
| Geometry · Condition (실행 없음) | 정의를 만드는 것 | **자기 정의 저장** |
| AnalysisLauncher · DataPreprocessor · ModelBuilder · ModelRunner · Optimizer | 실행 | **실행 착수** |

**계보 전량의 계산이 이 시점에 함께 일어난다.** 직속 조상의 파일을 여는 것이 어차피 이 시점이고, 거기서 그들의 `consumed` 를 물려받으면 전량이 나온다(1.5). 갱신 지점이 둘이 아니라 하나다.

**상위 선택 변경은 갱신 시점이 아니다.** 엣지 배열에 원소를 더하되 `consumed` 에는 적지 않는다 — 고르는 것은 의도이지 소비가 아니기 때문이다. 실행 있는 모듈에서 상위를 새로 고를 때 `consumed` 를 함께 갱신하면, 산출은 옛 상위로 만들어진 채 배지만 풀려 **거짓 안심**이 된다.

이것이 0.1 에서 어휘를 고친 근거다. "바인딩 시점" 을 적으면 배지가 답하는 질문이 "내 바인딩이 낡았나" 가 되는데, 사용자가 알아야 하는 것은 **"지금 보이는 이 결과가 최신 상위로 만들어진 것인가"** 다.

**따라 나오는 것 둘.**

- **`Stale` 해소 경로가 모듈마다 하나씩이다** — 정의 모듈은 다시 저장, 실행 모듈은 재실행. 별도 [확인] 버튼을 만들지 않는다.
- **상위를 처음 고른 직후는 무배지다.** `consumed` 에 그 키가 없어 비교 대상이 없다. 아직 돌리지 않았다는 사실은 배지 2종이 말하지 않는다(2.1).
- **해소 순서가 저절로 위에서 아래로 강제된다.** 상속분을 직속의 `consumed` 에서 물려받으므로(1.5), 중간을 건너뛰고 하류만 다시 돌려도 직속이 아직 든 옛 값을 물려받아 `Stale` 이 풀리지 않는다. Geometry 를 고쳤으면 AL 을 먼저 돌려야 DP 가 풀린다 — **순서를 검사하는 코드가 없는데 순서가 지켜진다.**

### 2.3 무엇을 못 잡나

| 못 잡는 것 | 왜 | 완화 |
|---|---|---|
| **상위의 정의 무변경 재실행** | 산출 지문의 자리가 없다. 실패 케이스 재실행 · DOE 이어달리기 · 같은 설정 재학습이 여기 해당한다 | 없다. run 파일을 넣으면 닫힌다(α-edge 5.2) — **이 안이 지불하는 유일한 축이다** |
| **SB(`.vtp`) 단독 변경** | 지문 대상이 SM 뿐이다. 핸들 선택 집합이 바뀌면 SM 도 바뀌어 잡히고, 위치만 옮긴 편집이 사각이다 | 미결 (7절 3번) |
| **기준 파일의 제자리 수정** | 지문이 등록 시 동결이다. FE-safe 재료 설정이 `.stlx`·`.dbase` 를 앱 밖에서 직접 고치는 채널이 실재한다 | `DashAnalysisModelContext::referenceModelChangedOnDisk()`(`controller/DashAnalysisModelContext.cpp:276-278`)가 이미 이것을 탐지하지만 **배지 입력으로 쓰지 않는다** — Identity 저장소가 비교 직후 현재 해시로 덮어써서 같은 변경이 두 번째 열기부터는 false 가 된다. 한 번만 뜨는 경고는 배지로 부적절하다 |
| **어느 항목이 바뀌었나** | 지문은 "바뀌었나" 까지만 답한다. 어느 DV·어느 응답인지는 로컬 ID 가 있어야 한다 | 이 안 밖 |

**전이 전파는 "안 하는" 것이 아니라 저장 값에 접혀 있다.** [[Project-Store-Design-Edge-Complete-Minimal]] 6.3 은 전파를 하지 않는 근거로 "하류가 먹은 것은 상류의 산출이고 그 산출의 `rev` 는 상류의 상위가 바뀌었다고 오르지 않는다" 를 든다. **그 근거는 run 파일이 있는 안에서만 성립한다** — 산출 `rev` 가 상류 재실행마다 오르므로 전파가 재실행을 따라 한 칸씩 내려간다. 산출 지문이 없는 이 안에서 같은 문구를 쓰면 조상 변경이 하류에 영구히 닿지 않으므로, 계보 전량(1.5)이 그 자리를 대신한다 — 판정에는 순회가 없고 계보에 조상이 다 있다.

---

## 3. 배선 설계

### 3.1 신설 — 접근자 2종

| 접근자 | 라이터 | API |
|---|---|---|
| **Reference 스토어** | **1곳** — 프로젝트 컨트롤러. 모듈은 읽기만 | 로드 · 저장(temp + rename) · `references` 조회(id) · 항목 추가·제거 · 역할별 경로 해석 |
| **정의 저장 헬퍼** | 정의 라이터 전량이 통과 | 루트 객체를 받아 ① 제외 키를 지운 사본의 sha256 계산 ② `definitionVersion` 갱신 ③ `consumed` 갱신(실행 없는 모듈만) ④ temp + rename |

자리는 `model/` 또는 `controller/` — `DashProject` 가 이미 Set 귀속 데이터를 들고 있으므로 그 옆이다.

**인스턴스 색인 접근자가 없다.** 열기 시 `configs/*.json` 을 읽으면서 각 파일의 `id`·`module`·`variant` 를 모아 메모리 맵(`inst_` → config 경로)을 만든다. 그 읽기는 배지 판정에 어차피 필요하므로 추가 비용이 아니다.

### 3.2 판정 주체 교체

| # | 현행 판정 | 좌표 | 신 |
|---|---|---|---|
| 1 | 파일명 접두사로 모듈 판정 | `DashProject::loadSetsFromConfigs()` `model/DashProject.cpp:1066-1211` | config 의 `module` 자기신고 |
| 2 | Geometry variant 4단 폴백 — JSON `variant` → 최상위 `Morphing` 객체 → DV source 접두 → 이름 접미사 | `DashProject::detectGeometryVariant()` `:621-656` | config 의 `variant` 한 줄. **폴백 3단이 사라진다** |
| 3 | Builder variant 3단 폴백 — JSON `variant` → `endsWith("-MCU")` → `Sim` | `DashProject::detectBuilderVariant()` `:658-702` | 동상 |
| 4 | 접미사 직접 판정 — `endsWith("-MCU")` 계열 | `DashProject.cpp` · `DashMainWindow.cpp` · `DashModelRunner.cpp` · `DashModelRunnerMCU.cpp` · `DashSurrogateModelCommon.cpp` | `variant` 조회 |
| 5 | 트리 아이템 `Qt::UserRole+2` — variant 를 bool·string 두 형으로 병행 보관 | `view/DashMainWindow.cpp` | 트리는 `inst_` 를 들고 variant 는 config 가 답한다 |
| 6 | **상위 산출 디렉토리를 정렬 순서가 고른다** — `folders.first()` | `view/DashModelRunnerWidget.cpp:744` · `view/DashOptimizerWidget.cpp:660-662` | `upstream.executions[]` |
| 7 | **조상을 파일명 문자열로 되짚는다** — `model_info.json.parameter[*].source` 가 `"GeometryParameter_Set1.json"` 이고 그 안의 `DV-Geometry[*].source` 둘째 마디가 deck 파일명이다 | `model/DashModelRunner.cpp:1505-1568` · `model/DashOptimizer.cpp:1310-1341` | `upstream.consumed` 의 `inst_`·`ref_` 키 (1.5) |

**6번이 이 안의 첫 체감 이득이다.** 지금은 콤보 선택이 비어 있으면 `folders.first()` 가 상위 바인딩이 된다 — 사용자가 고른 것이 아니라 정렬 순서가 고른 것이다.

**7번이 계보를 전량으로 둬서 얻는 부수 이득이다.** ModelRunner·Optimizer 가 조상을 찾는 유일한 수단이 지금은 파일명 조인이라 Set rename 이나 파일 이동을 막을 수 없다. 계보가 ID 를 들고 있으면 그 조인이 사라진다. **단 두 함수의 나머지 일(part 이름 · component · `.vtp` basename 추출)은 항목 단위 조인이라 남는다** — 로컬 ID 가 이 안 밖이기 때문이다.

**2·3번의 성격이 다른 넷과 다르다.** 판정 함수가 사라지는 것이 아니라 **폴백 단이 사라진다.** `variant` 키는 이미 1순위 입력이므로, 승격이 폴백 결과를 config 에 한 번 써 넣고 나면 그 뒤로 폴백에 도달하는 경로가 없다.

### 3.3 전역 활성 컨텍스트 → 자기 `upstream.references`

**레지스트리를 바꾸지 않는다.** `DashAnalysisModelContextRegistry` 는 이미 `filePath → context` 맵이고 모델 계층은 이미 경로를 넘긴다. 바꾸는 것은 **뷰·PM 층이 그 경로를 어디서 얻나** 뿐이다.

| 호출부 | 현행 | 신 |
|---|---|---|
| `viewmodel/DashGeometryParameterPresentationModel.cpp:46` · `:58` | `registry.activeFilePath()` · `activeContext()` | `upstream.references[deck]` → 경로 → `getOrLoad()` |
| `view/DashConditionParameterizationWidget.cpp:222` · `:313` | 동상 | 동상 |
| `view/DashGeometryParameterCADWidget.cpp:345` | `activeFilePath()` | `upstream.references[part]` |
| `view/overlay/DashMorphingSettings.cpp:562` · `:636` | `activeContext()` | 호스트 인스턴스의 `upstream` |
| `view/DashOptimizerWidget.cpp:1556-1557` | `setActiveContext()` + `activeContext()` | 렌더 목적이면 유지, 데이터 결합이면 교체 — **호출 목적 확인 필요** |
| `view/DashMainWindow.cpp:2318` · `:2488-2491` · `:2515-2519` · `:2656` · `:3323` | `setActiveContext()` / `activeContext()` | **유지** — 트리 선택과 렌더 대상은 세션 상태다 |

**이미 경로를 넘기는 곳은 건드리지 않는다** — `DashGeometryParameterCAD.cpp:106` · `DashConditionParameterization.cpp:118` · `DashOptimizer.cpp:1404` · `DashModelRunner.cpp:1980` · `DashMorphingUtils.cpp:325`·`:373`·`:388` · `DashReferenceFileWidget.cpp:617`·`:637`·`:784`·`:869` · `DashModelRunnerWidget.cpp:1463`·`:1972` · `DashModelingTreeWidget.cpp:358` · `DashManager.cpp:1028`. 이들이 받는 경로가 어디서 오는지가 실제 배선이고, 지금은 config 안 절대경로 문자열이거나 화면 상태다.

**가르는 선.**

| 구분 | 대상 |
|---|---|
| 프로젝트에 저장 (`upstream.references`) | 이 Set 은 어느 기준 파일 기준인가 |
| 세션 전용 (저장 안 함) | 화면에 렌더된 대상 · 트리 선택 · 카메라 · 스크롤 |

현행은 둘이 같은 필드(`m_activeFilePath`)를 써서 **화면 조작이 데이터 결합을 바꾼다.** CAD 쪽은 더 나가 있다 — `DashManager::applyLastNxCadParameterJsonToGeometryModels()`(`controller/DashManager.cpp:187-195`)가 마지막 NX 응답을 전 CAD 인스턴스에 일괄 적용한다.

**열기 시 상위 복원이 5번 항목의 나머지 절반이다.** 현행은 상위 선택을 적는 키가 일부 모듈에 없고, 있는 곳도 읽는 코드가 0곳이거나 절대경로다. `upstream` 을 만들어도 읽는 자리를 붙이지 않으면 0.2-5 가 그대로 남는다 — **자리와 리더는 별개 작업이다.**

### 3.4 정의 라이터 → 정의 저장 헬퍼

| 모듈 | 정의 라이터 | 좌표 |
|---|---|---|
| Geometry Morphing | 설정 저장 | `viewmodel/DashGeometryParameterPresentationModel.cpp:379` |
| Geometry (양 variant) | DV 표 저장 — **AL 화면에서 상위 Geometry 파일을 되쓰는 경로** | `model/DashDesignVariableModel.cpp:414-485` |
| Condition | DV-Condition 섹션 | `viewmodel/DashConditionParameterizationPresentationModel.cpp:130-131` |
| AnalysisLauncher | DOE 설정 | `model/DashAnalysisLauncher.cpp:822` · `:1207` |
| DataPreprocessor | Dataset | `model/DashDataProcessor.cpp:2634` · `:2674` |
| ModelBuilder Sim | Configuration | `model/DashModelBuilder.cpp:480` |
| ModelBuilder MCU | 동상 | `model/DashModelBuilderMCU.cpp:524` |
| ModelRunner | Model upload | `model/DashModelRunner.cpp:552` |
| Optimizer | Optimization | `model/DashOptimizer.cpp:389` |

**헬퍼를 통과시키는 것이 지문 때문에 생기는 유일한 기존 코드 수정이다.** "파일을 직접 쓴다" 를 "헬퍼를 부른다" 로 바꾸는 기계적 변경이고, 얻는 것 셋 — 지문 계산이 한 자리에 있어 나중에 라이터를 붙이는 사람이 잊을 수 없고, 원자적 쓰기(temp + rename)가 같은 작업에서 서며, 정의 칸의 라이터가 실질적으로 하나가 된다.

**실행 상태 라이터는 헬퍼를 통과시키지 않아도 된다.** 지문이 내용 기반이라 통과해도 값이 바뀌지 않기 때문이다(1.4). 다만 통과시키면 원자적 쓰기를 함께 얻으므로, 통과 여부는 성능·경합 판단에 맡긴다 — `setSampleStatus` 는 이미 전용 뮤텍스를 들고 있다(`model/DashDoeConfigManager.cpp:529`).

**ModelBuilder SM 은 외부 도구가 되쓴다.** 학습 도구가 `Configuration.{model}.status` 를 `"Done"` 으로 바꾸고 GUI 가 1초 타이머로 되읽는다(`model/DashModelBuilder.cpp:1364`·`:1384`). **이 안은 그 경로를 바꾸지 않는다.** 도구가 쓰는 키가 지문 제외 목록에 있으므로, 도구의 되쓰기가 `definitionVersion` 을 움직이지 않는다 — 지문을 내용 기반으로 둔 것이 여기서 한 번 더 값을 한다.

### 3.5 승격

```
[열기] .{name}.dproj 탐색  (현행 findDprojFolder 그대로)
   │
   ├─ 모든 config 에 id 가 있다 ──▶ 내용으로 판정. 파일명·접미사를 읽지 않는다
   │
   └─ 없는 config 가 있다 ──▶ [승격] 그 파일에 대해 현행 판정을 1회 돌린다
                 │   loadSetsFromConfigs / detectGeometryVariant / detectBuilderVariant
                 │   결과를 id · module · variant 로 써 넣는다
                 │   definitionVersion  첫 계산해 써 넣는다
                 │   upstream           빈 배열 셋 + 빈 consumed
                 │   reference.json     없으면 만든다 (아래)
                 ▼
              이후 열기는 위쪽 갈래
```

**판정 코드가 사라지지 않고 호출부가 옮겨간다.** 상시 유지되는 하위호환 분기가 아니라 **1회 실행되는 입구**다. 승격이 끝나면 그 함수들은 열기 경로에서 불리지 않는다.

**`references[]` 를 비우지 않고 씨앗을 쓴다.** `{configs}/AnalysisModelIdentity.json` 의 `models` 키가 곧 **이 프로젝트에서 열린 적 있는 deck 의 canonical path 목록**이다(0.3). 승격이 그것을 읽어 항목을 만들면 사용자가 기준 파일을 다시 등록하지 않아도 된다.

| 필드 | 승격 시 값 |
|---|---|
| `id` | 새 발급 |
| `files` | 확장자로 역할 판정. **씨앗이 덱뿐이라 `.inp`·`.dat`·`.dfsxml` → `deck` 만 난다** — B·C·D 형태는 승격이 만들지 못한다(1.2) |
| `origin` | 비운다 — 원본 경로를 모른다 |
| `fingerprint` | **여기서 1회 계산한다.** Identity 의 저장 값을 그대로 옮기지 않는다 — 그 값의 갱신 규칙이 다르다(1.2) |
| `label` | 파일 basename |

**승격된 프로젝트는 전부 무배지다.** `consumed` 가 비어 있어 비교 대상이 없다. 사용자가 상위를 한 번 고르고 한 번 돌리면 그때부터 배지가 선다. 현행과 동등하다 — 지금은 열 때마다 다시 고른다.

**되돌리기가 싸다.** 물리 변화가 파일 하나 추가와 최상위 키 6개 추가뿐이라, 승격 코드가 남아 있는 동안은 `reference.json` 을 지우고 키를 무시하면 현행 경로로 복귀한다.

---

## 4. I/O 시점

| 사용자 행위 | PM `reference.json` | SM `configs/*.json` |
|---|---|---|
| 프로젝트 생성 | **쓰기** — 빈 배열 | — |
| 프로젝트 열기 | 읽기 1회 | 읽기 전량 — `id`·`module`·`variant`·`definitionVersion`·`upstream`. **위상 순서가 필요 없다** — 계보가 저장 값이라 각 파일이 독립적으로 판정된다 |
| `[Add File]` | **쓰기** — `references[]` 1항목 + **해시 1회** | — |
| Set 생성 | — | **쓰기** — 빈 정의 + `id` 발급 |
| Set 삭제 | — | 삭제 (현행 그대로) |
| Set rename | — | 파일 rename (현행 그대로) |
| 모듈 진입 | — | 읽기 + 배지 판정 |
| 상위 선택 변경 | — | **쓰기** — `upstream` 배열만. `consumed` 는 건드리지 않는다 |
| 정의 편집 | — | **쓰기** — 현행 트리거 유지 + `definitionVersion` 재계산 (+ 실행 없는 모듈은 조상 읽기 → `consumed` 갱신) |
| 실행 착수 | — | **쓰기** — 직속 조상 읽기 → `consumed` 전량 고정. 직속 수만큼 파일을 열고 그 이상은 열지 않는다 |
| 실행 중 전이 | — | 현행 유지. **`definitionVersion` 은 움직이지 않는다** |
| 실행 종결 | — | 현행 유지 |

셋이 따라 나온다.

- **PM 쓰기는 2지점이고 전부 사용자 조작이다.** 실행 중에는 한 번도 쓰이지 않는다.
- **배지 판정에 파일 해시가 없다.** 두 지문이 전부 저장 값이라 읽기만 한다 — 수백 MB 급 `.vtp` 와 deck 을 배지 때문에 여는 일이 없다. 해시가 도는 자리는 `[Add File]` 1회(그때 같은 파일을 복사하느라 이미 I/O 바운드다)와 정의 저장 시 SM 1개뿐이다.
- **폴링이 늘지 않는다.** ModelBuilder 1초 폴링은 그대로 남는다 — 도구 계약이 이 안 밖이다.

---

## 5. 순서 — 5단계

각 단계 종료 시 빌드·실행 가능하다.

```
S1  reference.json · Reference 스토어 · [Add File] 쓰기        [현행 동작 무변경]
    │  아무도 읽지 않는 상태로 먼저 만든다 — write-only
    │  verify: 파일 3개 등록 후 references[] 가 실체와 일치, 지문이 재계산되지 않는다
    ▼
S2  SM 최상위 키 6개 + 승격 + 열기 경로 교체                    [글로빙 호출부 이동]
    │  verify: 구프로젝트 열기 → 전 config 에 id·module·variant 생성
    │          재열기에서 loadSetsFromConfigs 미실행
    │          reference.json 이 Identity 씨앗으로 채워진다
    ▼
S3  variant 판정 교체 — 3.2 의 2~5번                            [접미사 판정 소멸]
    │  verify: -MCU · -CAD Set 이 각 모듈에서 정상 진입
    │          config 의 variant 를 손으로 고치면 판정이 따라온다
    ▼
S4  upstream 3배열 + 읽기 배선 + folders.first() 제거           [상위 선택이 복원된다]
    │  verify: 상위를 고르고 프로젝트를 닫았다 열면 선택이 복원된다
    │          Geometry Set 두 개가 서로 다른 deck 을 동시에 본다
    │          상위 Set 을 지우면 소비자가 ✕ Broken
    ▼
S5  정의 저장 헬퍼 + definitionVersion + consumed 전량 + 배지 2종  [낡음이 화면에 뜬다]
       verify: 상위 Geometry 를 고치면 AL 이 ⚠ "상위 정의가 바뀌었습니다"
               기준 파일을 다시 등록하면 ⚠ "기준 파일이 교체됐습니다"
               DOE 를 80케이스 돌리는 동안 하류 배지가 움직이지 않는다   ← 1.4 의 핵심 검증
               같은 Geometry 수정으로 DP·MB·MR·OPT 넷이 동시에 뜬다     ← 1.5 의 핵심 검증
               각각 재실행(또는 재저장)하면 배지가 풀린다
```

**S5 의 셋째·넷째 verify 가 이 안의 두 설계를 각각 검증하는 자리다.** 버전을 저장 시점이나 카운터로 뒀다면 셋째가 실패하고, 계보를 직속만 들었다면 넷째가 AL 하나만 띄운다.

**S4 까지만 해도 현행보다 낫다** — 상위 바인딩이 복원되고 정렬 순서가 상위를 고르는 일이 없어진다. S5 가 사용자에게 보이는 나머지를 만든다.

---

## 6. 범위 밖 — 후속으로 뗀 둘과 그 부속

**자리를 미리 만들지 않는다.** 쓰지 않은 필드를 비워 두는 것은 계약이 아니다.

| 뺀 것 | 근거 |
|---|---|
| **정의와 실행 상태 분리** — run 파일 · 실행 메타 · 케이스 실패 사유 · 스테이지 상태 | 후속 1. 이 안은 지문 제외 목록으로 절단선만 그어 둔다(1.4) |
| **도구 계약 변경** — 상태를 stdout 으로, 도구 쓰기를 실행 벌크 안에 가둠 | 후속 1의 부속. ModelBuilder 1초 폴링과 도구의 SM 되쓰기가 남는다. 도구를 함께 릴리스해야 하는 순서 제약이 이 안에 없다는 뜻이기도 하다 |
| **하나의 root 로 재배치** — 인스턴스 디렉토리 · `references/` · `configs/` 폐기 | 후속 2. 3루트 유지가 전제이고, 경로 조립 함수 4개와 호출부 25곳을 건드리지 않는다 |
| 실행 ID · 실행 이력 · 산출물 대장 | 실행을 개체로 두지 않는다 |
| 로컬 ID — `dv` · `rsp` · `mdl` | 의존성 단위가 인스턴스다 |
| 파일명 ID 화 · Set 라벨의 필드화 | 후속 2와 같은 자리를 건드린다(1.3) |
| 진행도 배지 4종 | 판정 입력이 디스크 스캔이 된다(2.1) |
| `Stale` 전이 전파 · 항목 단위 지문 해석 | 2.3 |
| Results Analyzer 뷰 설정 · 파생 캐시 | 지금 들어갈 것이 없다. 리더가 0곳인 `DOE Analysis`·`Data Analysis` 블록은 지문 제외 목록에 넣어 두고 폐기는 후속으로 미룬다 |
| 마이그레이션 · 구버전 거부 | 승격으로 대체한다(3.5) |

---

## 7. 되돌리기 어려운 결정 · 미결

### 7.1 배포 전에 확정할 것

| # | 결정 | 답 |
|---|---|---|
| 1 | `$schema` 번호 축 | `1` |
| 2 | 전역 ID 형식 | 접두사 + 12-hex 난수 |
| 3 | `upstream` 키 이름과 원소 형 | `references` · `definitions` · `executions` 배열(순수 ID) + `consumed` 맵(ID → 버전) |
| 4 | 버전의 방식 | **정의 블록 sha256 · 저장 값.** 카운터·시각을 쓰지 않는다 (1.4) |
| 5 | 지문 계산 대상 | 정의 본문 + **`upstream` 3배열 포함** · 실행 상태 키와 `consumed` 제외. 제외는 경로 패턴 목록이고 `Configuration.*.status`·`.error` 가 유일한 중첩 (1.4) |
| **5-1** | **`consumed` 의 범위** | **조상 전량** — 직속 3배열의 초집합. 직속만 들면 조상의 내용 변경과 deck [다시 가져오기]가 하류에 영구히 닿지 않는다 (1.5) |
| **5-2** | **`consumed` 의 계산 규칙** | 소비 시점 1회. **직속은 현재 값 · 상속은 직속의 `consumed` 를 그대로 물려받는다** — 조상을 훑어 현재 값으로 채우면 중간을 건너뛴 재실행이 헛되이 `Stale` 을 푼다. 판정 시점에는 계산도 순회도 없다 (1.5 · 2.1) |
| **5-3** | **직속 엣지의 범위** | 사용자가 그 화면에서 고르는 것만. ModelRunner·Optimizer 는 **ModelBuilder 하나**이고 Geometry·Condition·deck 은 상속으로 들어온다 (1.5) |
| 6 | `consumed` 갱신 시점 | 실행 있는 모듈은 착수, 없는 모듈은 정의 저장. **상위 선택 변경은 아니다** (2.2) |
| **6-1** | **`consumed` 는 스냅샷이다** | 소비 **시점**의 조상 전량. 그 이후 상위가 새로 얻은 조상은 들어오지 않는다. 라이브 뷰로 읽으면 `Broken` 전파를 오해한다 (1.5 · 2.1) |
| **6-2** | **`Stale` 의 두 종류** | 어긋난 항목이 **직속뿐**이면 내가 돌려 풀리고, **상속이 섞였으면** 상위부터다. 후자에서 착수를 막지 않고 문구로 안내한다 (2.1) |
| **6-3** | **`Broken` 의 두 갈래와 전파** | 없는 ID 가 직속의 `consumed` 에 있으면 내가 상속해 `Broken`, 직속의 `upstream` 배열에만 있으면 내게 옮겨오지 않아 **`Stale`**. 착수는 앞의 것만 막는다 (2.1) |
| 7 | 경로 기준 | 프로젝트 루트 상대 |
| 8 | `reference.json` 의 자리와 범위 | `.dproj/reference.json` · 기준 해석 파일 대장만. 인스턴스를 색인하지 않는다 |

### 7.2 미결

| # | 항목 | 정해야 할 것 |
|---|---|---|
| 1 | **다중 인스턴스** | 같은 프로젝트를 두 창에서 여는 경우. 잠금 파일·단일 인스턴스 가드가 현행 레포에 0건이다. 이 안은 PM 쓰기가 2지점(전부 사용자 조작)이라 창이 좁지만 0 은 아니다 |
| 2 | **`[Add File]` 필터와 역할 어휘의 어긋남** | 넣는 쪽이 12종(`view/DashMainWindow.cpp:2117-2120` — `.dat .inp .vtk .vtu .rst .odb .csv .dfsxml .prt .stp .step .stli`)인데 역할은 4종이다. `.vtu`·`.odb`·`.csv` 가 갈 자리가 없다 |
| 3 | **SB 변경 탐지** | 핸들 위치만 옮긴 편집이 지문에 안 잡힌다(1.4). `(size, mtime)` 을 지문에 섞는 방법이 있으나 프로젝트 복사·이관이 mtime 을 어떻게 다루는지에 헛된 `Stale` 여부가 달린다 |
| 4 | **`view/DashOptimizerWidget.cpp:1556-1557` 의 호출 목적** | `setActiveContext` + `activeContext` 가 렌더 때문인지 데이터 결합 때문인지에 따라 3.3 의 처리가 갈린다 |
| 5 | **Reference 하나에 같은 역할 파일이 둘** | 다부품 어셈블리에서 `.prt` 가 둘이면 `files` 역할 맵이 깨진다. 깨지면 `files` 가 배열이 되고 로컬 ID 가 하나 생긴다 |
| 6 | **`kind` 어휘** | `fe`\|`cad` 둘로 충분한지. FE-safe 가 세 번째인지 `fe` 의 하위인지 |
| 7 | **정의 무변경 재실행을 언제 닫나** | 2.3 의 유일한 지불 축이다. run 파일을 넣는 것이 답이고 그것은 α-edge 다 — 이 안 다음의 자연스러운 한 걸음이라 순서를 미리 적어 둔다 |
| 8 | **AnalysisLauncher 의 `references[]` 역할 실측** | 1.5 가 variant 별로 갈린다고만 적었다. Morphing / CAD / FE-safe 가 각각 어느 역할을 몇 개 드는지는 `input_files[]` 의 `{name, target_component, path}` 와 확장자 분기에 흩어져 있어 아직 재지 않았다. **AL 이 계보의 뿌리라 이 표가 하류 넷의 `consumed` 크기를 정한다** |
| 9 | **계보가 담을 최대 크기의 상한** | 현행 파이프라인은 Morphing 경로 6 · CAD 경로 7\~8(1.5)이지만 Optimizer 후보해를 ModelRunner 로 되돌리는 수동 왕복이 정식화되면 사이클이 아니라 깊이가 늘어난다. 상한을 두지 않을지, 두고 초과 시 어떻게 할지 |
| 10 | **`.stli` 항목의 지문 대상** | 실체가 폴더인데 `fingerprint` 는 파일 전문 sha256 이다(1.2-C). `.stli` 하나만 해싱하면 옆 파일 교체가 안 잡히고, 폴더 전량을 해싱하면 등록 1회 비용이 폴더 크기에 걸린다 |
| 11 | **`material` 역할의 라이터와 제자리 편집** | 현행은 `.stlx`·`.dbase`·`.msc` 를 브라우즈해 제자리로 고친다(1.2-D). 역할을 세우려면 ① 그 파일들을 프로젝트로 복사할지 ② 편집이 `fingerprint` 를 갱신하게 할지 ③ 아니면 `material` 을 어휘에서 뺄지를 정해야 한다 |
| 12 | **`.cdb` · `.bdf` 의 자리** | 후보 스캔에는 `.cdb` 가, `SupportedInputs` 에는 `.bdf` 가 있는데 양쪽 다 반대편과 `[Add File]` 필터에 없어 형태를 만들지 못한다(1.2). 목록 셋을 하나로 모을지, 둘을 뺄지 |
