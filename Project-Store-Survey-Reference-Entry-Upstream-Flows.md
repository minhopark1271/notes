# 진입 파일 5종의 상류 동선 — 저장 구조 현황

> **이 문서는 단독으로 읽힌다.** 아래는 근거의 출처이지 서술의 일부가 아니다 — 인용할 사실은 본문에 다시 적었다.
>
> * [Code-Map-User-Flow-Analysis-Launcher](Code-Map-User-Flow-Analysis-Launcher.md) — AL **내부** 동선(진입 · DV 확정 · 샘플링 · 분기 판정 이후 · 상태 종결). 본 문서는 그 3-6 절 분기의 **전사**만 잰다
> * [Code-Map-User-Flow-Geometry-Parameterization-Morphing](Code-Map-User-Flow-Geometry-Parameterization-Morphing.md) · [Code-Map-User-Flow-Geometry-Parameterization-CAD](Code-Map-User-Flow-Geometry-Parameterization-CAD.md) · [Code-Map-User-Flow-Condition-Parameterization](Code-Map-User-Flow-Condition-Parameterization.md) — 각 상류 모듈의 내부 동선과 산출 파일
> * [Project-Store-Survey-Inputs-Payloads-Runtime](Project-Store-Survey-Inputs-Payloads-Runtime.md) — 입력 셋을 이미 잰 문서(Morphing 은 1파일 · CAD 는 `.prt`+`.wbpj` 2파일). 본 문서는 같은 대상을 **진입 파일 5종 × 짝 지정 기제**로 다시 가른다
> * [Cross-Module-Defect-Menifest-Axis](Cross-Module-Defect-Menifest-Axis.md) — 매니페스트 축 정의. 6-2 가 그 축의 "파일명이 스키마" 항목에 닿는다
>
> 측정 시점: `dev` @ `4c7608e` — 라인 앵커 전부 이 커밋 기준
> 검증 수준: 정적 코드 근거만 — 빌드·실행 검증 없음 · 외부 도구(NX CAD · Ansys Journal · DashOptiMBD · fe-safe) 내부 미확인 · 화면 조작 순서는 위젯·모델 코드에서 유도한 것이고 실사용 관찰이 아니다

## 개요

AL 이 실행 템플릿으로 받는 진입 파일은 확장자 5종이고 (`.inp` `.dat` `.dfsxml` `.wbpj` `.stli`), **그 5종이 성립하기까지 밟는 상류 모듈과 남기는 파일이 서로 다르다.** 확장자가 워크플로를 정한다는 사실은 AL 안에서 관찰되지만, 그 확장자를 쓸 자격이 상류에서 어떻게 갖춰지는지는 어디에도 기록되지 않는다.

측정 결과 셋.

- **자동 등록은 2종만** — Reference File 표의 자동 수집이 Geometry DV 의 `source` 문자열을 확장자로 거르므로 `.dat`·`.inp` 만 올라오고, 나머지 3종은 전부 수동 추가다
- **짝 지정 기제가 3종으로 갈려 있다** — 상류 모듈의 DV 문자열(`.dfsxml`) · AL 표의 행 속성(`.wbpj`) · 표 전체에서 유도되는 집합(`.stli`). 저장 위치도 깨지는 조건도 서로 무관하다
- **폴더가 단위인 것이 2종** — `.dfsxml`·`.stli` 는 파일 하나가 아니라 부모 폴더가 실체인데, 매니페스트에 해당하는 `input_files[]` 는 파일 경로만 들고 있다

범위는 상류 모듈 진입부터 AL `[Start]` 착수까지다. 실행 이후(솔버 제출 · 상태 되쓰기 · 결과 열람)는 AL 대응표 3-6\~3-8 절에 있다.

---

## 1. 공통 준비

5종 모두 밟는다.

```
[프로젝트] 열기 → 파일 추가 (view/DashMainWindow.cpp:2131)
   │   ※ .stli 만 예외 — 파일이 아니라 부모 폴더가 통째로 복사된다 (:2140-2164)
   ▼

[Solver Settings] 해당 솔버 경로 등록
   │   Ansys · Abaqus(SIMULIA 루트) · NX
   │   ※ fe-safe 는 별도 키가 없고 Abaqus 루트에서 실행 파일을 유도한다
   ▼

[Analysis Launcher] Set 생성 → DV 콤보 2개 선택 → [Set] → 샘플링 설정 → [Run]
       여기까지가 케이스 무관. 이후가 갈린다
```

Reference File 표는 세 경로로 채워지는데(AL 대응표 3-5), 케이스별로 갈리는 것은 **자동 수집** 경로다. 자동 수집은 Geometry DV 의 `source` 에서 두 번째 토막을 꺼내 확장자가 `dat|inp|bdf|dfsxml|stli` 인 것만 후보로 삼는다 (`model/DashAnalysisLauncher.cpp:1318-1333`). 그래서 `.dat`·`.inp` 만 자동으로 올라온다.

---

## 2. `.inp` / `.dat` — 템플릿 자신이 morph 대상

두 케이스는 확장자만 다르고 동선이 같다. 상류가 5종 중 가장 짧다.

```
[프로젝트 트리] .dat / .inp 클릭 → Active Context 설정 (view/DashMainWindow.cpp:2317)
   │   ※ RwSession 이 파싱하는 것은 inp·dat 뿐 (controller/DashRwSession.cpp:1363-1370)
   ▼

[Geometry Parameterization (Morphing)] 핸들 배치 → 범위 편집 → [Set]
   │   1. 활성 deck 을 configs/ 로 복사 (viewmodel/DashGeometryParameterPresentationModel.cpp:72-77)
   │   2. DV source = "Morphing|{파일명}|{part}" 를 각 DV 에 기록 (:79-82)
   │   산출: configs/GeometryParameter_Set{N}.json + 동명 .vtp
   ▼

[Condition Parameterization] (선택) FE 조건 승격
   │   산출: configs/ConditionParameter_Set{N}.json 의 DV-Condition
   │   ※ 형상 DV 없이 조건 DV 만으로도 실행된다 — condition-only export 경로
   ▼

[Analysis Launcher] Reference File 표에 deck 이 자동 등록됨
   │   라디오로 그 행을 고르면 곧 실행 템플릿
   ▼

[Start] morph 대상 = 템플릿 자신
       .dat → Ansys MAPDL(.rst) · .inp → Abaqus(.odb)
```

짝 파일이 없다. `.inp` 는 target part 를 그 행에서 지정해야 morph 가 돌고, 비어 있으면 전 샘플이 skip 된다 (`model/DashJobRunner.cpp:1511-1513`).

---

## 3. `.dfsxml` — 상류는 `.dat` 로 서고 템플릿만 얹는다

상류가 2절과 **완전히 같다.** 파라미터화는 `.dat` 기준으로 하고, `.dfsxml` 은 그 위에 실행 템플릿으로 얹는다.

```
[2절과 동일] .dat 로 Morphing 파라미터화 → DV source = "Morphing|{dat}|{part}"
   ▼

[프로젝트] MBD 템플릿 폴더 추가 (.dfsxml + 그 폴더의 참조 파일들)
   │   ※ 트리에 뜨지만 여는 수단이 없다 — Load 버튼이 그려지는 확장자 목록에
   │      .dfsxml 이 없고 (view/delegate/ProjectFileTreeDelegate.cpp:47), 그 버튼이
   │      유일한 진입점이라 (view/DashMainWindow.cpp:335) 렌더 독을 여는
   │      dfsxml 분기 (:2317-2321) 는 도달하지 않는다
   ▼

[Analysis Launcher] .dfsxml 을 수동 추가 → 라디오를 .dfsxml 로 이동
   │   .dat 행은 자동 등록으로 남아 있다 — 지우지 않는다
   │   part 콤보는 "CBLOCK" 고정·비활성 (view/DashReferenceFileWidget.cpp:759-762)
   ▼

[Start] morph 대상 = DV source 가 가리키는 .dat (configs 에서 이름으로 찾는다)
       motion-writer 참조 = .dfsxml 의 부모 폴더 — 파일이 아니라 폴더가 인자다
       → 케이스별 .dfsxml 생성 → motion-launcher → .dfr
```

진입 조건이 하나 숨어 있다. 이 갈래는 `DOE Table.source` 에 `Morphing|` 항목이 있을 때만 성립하고 (`model/DashJobRunner.cpp:509-523`), CAD DV 나 조건 DV 만으로 `.dfsxml` 을 고르면 모핑 폴백 분기로 떨어져 전 케이스가 `Generated file missing` 으로 실패한다.

`.dfsxml` **자체를 읽는 코드는 없다.** 쓰이는 것은 확장자(갈래 판정) · basename(`analysisType`) · 부모 폴더(외부 도구 인자) 셋이고, 내용을 파싱하는 것은 외부 `motion-writer` 뿐이다.

---

## 4. `.wbpj` — 상류가 CAD 계열로 갈린다

메시 morph 가 없고 설계변수가 NX CAD 파라미터라, 상류 모듈이 Morphing 이 아니라 CAD 쪽이다.

```
[사전] Solver Settings 에 NX 경로 → NX CAD 데몬 기동
   ▼

[Geometry Parameterization (CAD)] .prt 등록 — 한 명령으로 파라미터 추출 + .prt 복사본
   │   CAD Parameter 탭에서 값·범위 편집 → [Set]
   │   산출: configs/GeometryParameter_Set{N}-CAD.json (variant "CAD") + 같은 폴더의 .prt 복사본
   │   DV source = "CAD|{part}" — 파일 경로가 아니다
   ▼

[Analysis Launcher] .wbpj 를 수동 추가 → 같은 행의 target part 로 .prt 지정
   │   자동 등록이 안 되는 이유: "CAD|..." 는 확장자가 없어 후보에서 탈락
   │      (model/DashAnalysisLauncher.cpp:1324-1333)
   │   라디오를 .wbpj 로 두면 CPU 라벨·스핀박스가 비활성
   │      (view/DashAnalysisLauncherWidgetBase.cpp:274-276)
   ▼

[Start] morph 없음
       Step 1: Independent Parameter 를 NX 로 보내 케이스별 .stp 재생성 (직렬)
       Step 2: Ansys Journal 을 배치 1회 실행 → .dat · .rst 존재로 케이스 성패 판정
```

짝 파일 지정이 5종 중 유일하게 AL 안에서 닫힌다 — `input_files[].target_component` 가 그 행에 붙어 있어, 바꾸려면 그 행에서 다시 고르면 된다. 반면 `Independent Parameter` 의 초기값 표는 상류의 `GeometryParameter_*.json` 에서 읽으므로 (`model/DashJobRunner.cpp:2238-2251`), CAD 파라미터화를 건너뛰면 경고만 내고 파라미터 없이 진행한다.

---

## 5. `.stli` — 상류가 AL 자신이다

다른 모듈이 아니라 같은 모듈을 두 번 실행한다.

```
[1 pass] 같은 Set 에서 .inp 를 라디오로 골라 [Start] → 완료 대기
   │   산출: {moduleDir}/{Set}/{analysisType}/{runKey}/{runKey}.odb
   │   ※ 다른 Set 이 아니다 — ODB 탐색이 현재 Set 이름을 그대로 쓴다
   │      (model/DashJobRunner.cpp:1333)
   ▼

[프로젝트] .stli 추가 → 부모 폴더가 통째로 복사됨 (view/DashMainWindow.cpp:2140-2164)
   │   ※ .dfsxml 과 같은 이유로 트리에서 여는 수단이 없다 — Load 버튼 대상 확장자가
   │      아니어서 (view/delegate/ProjectFileTreeDelegate.cpp:47) "Reference Files 에서
   │      고르라" 는 안내 분기 (:2217-2222) 도 도달하지 않는다
   ▼

[Analysis Launcher] .stli 수동 추가 → 라디오를 .stli 로 이동
   │   part 콤보 비활성 — 템플릿이 자기 형상을 쓴다 (view/DashReferenceFileWidget.cpp:711-716)
   │   선택된 행이 .stli 일 때만 Material 버튼이 보인다 (:1184) → 재료 설정
   │   ※ 1 pass 에 쓴 .inp 행을 표에서 지우면 안 된다 — ODB 소스 목록을
   │      input_files 의 dat/inp/dfsxml/wbpj basename 집합에서 만든다 (:1253)
   ▼

[2 pass] [Start] → 같은 runKey 의 다른 analysisType 폴더에서 ODB 를 복사해 배치
       → FeSafeLauncher 제출 → {runDir}/{runKey}.odb
       ※ ODB 를 못 찾으면 대기가 아니라 그 케이스 즉시 Failed (:1352-1358)
```

DOE 샘플의 `values` 를 읽지 않는 유일한 진입 파일이다 — `key` 와 `active` 만 본다. 설계변수 파라미터화 없이도 성립하지만, Set 의 DV 표가 비면 샘플 자체가 없으므로 1 pass 가 서지 않는다.

---

## 6. 대조

### 6-1. 상류 요건

| 진입 파일 | 상류 모듈 | 상류 산출물 | AL 표 등록 | 짝 지정 위치 | morph 대상 |
|---|---|---|---|---|---|
| `.inp` | Geometry(Morphing) [+ Condition] | `GeometryParameter_Set{N}.json` + `.vtp` + configs 의 deck 복사본 | **자동** | 없음 (target part 만) | 템플릿 자신 |
| `.dat` | 동일 | 동일 | **자동** | 없음 | 템플릿 자신 |
| `.dfsxml` | 동일 + MBD 템플릿 폴더 | 동일 | 수동 (`.dat` 은 자동) | 상류 DV 의 `source` 문자열 | `source` 의 `.dat` |
| `.wbpj` | Geometry(CAD) | `GeometryParameter_Set{N}-CAD.json` + `.prt` 복사본 | 수동 | AL 그 행의 `target_component` | 없음 |
| `.stli` | **AL 1 pass** | 같은 Set 의 `{analysisType}/{runKey}/{runKey}.odb` | 수동 | `input_files` basename 집합 − 자기 | 없음 |

### 6-2. 짝 지정 기제 3종

같은 "이 파일에는 저 파일이 딸린다" 를 세 자리가 서로 다른 형식으로 들고 있다.

| 기제 | 대상 | 저장 위치 | 쓰는 주체 | 깨지는 조건 |
|---|---|---|---|---|
| DV source 문자열 | `.dfsxml` → `.dat` | `GeometryParameter_Set{N}.json` 의 각 DV `source` | 상류 모듈의 `[Set]` | configs 의 `.dat` 복사본이 없어지면 실행 중단. 바꾸려면 설계변수를 다시 정의 |
| 행 속성 | `.wbpj` → `.prt` | `AnalysisLauncher_{Set}.json` 의 `input_files[].target_component` | AL 표의 그 행 | 값이 비면 착수 전 중단. `.prt` 경로는 `.wbpj` 디렉토리 기준 상대 |
| 표 전체에서 유도 | `.stli` → 상류 `.odb` | 저장되지 않음 — `input_files[]` 의 basename 집합에서 자기 제외로 매번 계산 | 없음 (파생) | 상류 템플릿 행을 표에서 지우면 소스가 사라진다. ODB 부재는 대기가 아니라 즉시 Failed |

셋 다 **파일명·확장자가 계약을 대신한다.** `analysisType` 이 basename 이고, ODB 소스 판정도 basename 집합이며, 갈래 판정도 확장자다. 폴더가 실체인 2종(`.dfsxml`·`.stli`)은 그 폴더를 가리키는 필드가 없어 부모 디렉토리로 유도되므로, 사용자가 폴더를 옮기면 설정 파일은 유효한 채로 실행만 깨진다. 이 성격이 [Cross-Module-Defect-Menifest-Axis](Cross-Module-Defect-Menifest-Axis.md) 의 "기준 모델·계보 미기록" · "파일명이 스키마" 두 축에 해당한다.
