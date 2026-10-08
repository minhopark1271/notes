# CAD 경로의 위상 — D29\~D33 처분 근거

> 작업 묶음: 프로젝트 매니페스트 도입과 모듈 의존성 관리
> 소관: [[Project-Manifest-0-Work-Order]] 결정 표 D29\~D31(유보) · D32·D33(철회)의 원문과 근거. 착수는 마스터 후속작업 13(미래 CAD 경로)

## 결정 원문

마스터 결정 표에서 이관했다. M·P·D·후속작업 번호는 [[Project-Manifest-0-Work-Order]] 소유다.

| # | 항목 | 결정 |
|---|---|---|
| D29 (유보) | 원장의 종류 확장 | **유보 — 이 묶음은 원장을 `deck` 전용(P3 현행)으로 유지한다.** `.prt` 는 지금 고려하지 않는다(아래 "근거" 절). 설계 방향만 세이브 — 원장 항목에 `kind`(`deck`·`prt`)를 두되 기준모델 자격은 `deck` 한정, `.prt` 의 위상은 형상 출처(provenance). 착수는 후속작업 13(미래 CAD 경로)과 함께. 문서 1 9절의 "파일 둘이 한 항목" 스케치는 폐기 유지 — 두 파일의 소비 주체가 갈린다 |
| D30 (유보) | `.prt` 의 등록 지점 | **유보 — D29 동반.** 방향만 세이브 — Load 핸들러의 `.prt` 분기 한 곳(P4 동형), 커서·`activeModel` 불변(커서를 만지는 것은 `dat`·`inp`·`dfsxml` 분기뿐 — `DashMainWindow.cpp:2283`) |
| D31 (유보) | CAD Set 의 형상 출처 키 | **유보 — 이 묶음의 CAD 처분은 #366 봉합(M5 제외·죽은 전역 읽기 제거)까지다.** 방향만 세이브 — `referenceModel`(미지정 허용)과 별개의 `cadSource`(가칭) {uuid, path}, 최초 승격 1회 핀, 다른 `.prt` 재승격 차단(D17·D20 문형). configs `.prt` 복사·재Load 보관본 삭제(코드맵 D15)·Set↔`.prt` 미저장(D17)은 전부 **불개입** — 사장 경로와 함께 격리되고, 결합의 영속화는 미래 CAD 경로(후속작업 13)에서 생성 deck 의 출처 기록으로 닫는다 |
| D32 (철회) | DV `source` 의 `CAD\|<part>` | **철회 — wbpj 경로 사장 판정(아래 "근거" 절).** 라벨-locator 겸업(표시명에 `.prt` 를 붙여 configs 를 여는 `DashOptimizerPresentationModel.cpp:19-24` → `DashOptimizerWidget.cpp:1606` · `DashModelRunner.cpp:1530`)은 실측 결함이나 소비자 전부가 사장 경로다 — 교체하지 않고 `CAD\|` 형식·소비 불개입 |
| D33 (철회) | 조합·스탬프의 형상 일반화 | **철회 — 조합·스탬프는 D25·D26 원안(deck 단일)을 유지한다.** kind 일반화(`geometry.source`·`geometrySource`)와 CAD 조합 `conditions` ∅(wbpj 배치가 형상 파라미터만 Journal 에 싣는다 — `DashJobRunner.cpp:2579-2617`)는 wbpj 경로를 조합 개념에 수용하려던 특례인데 그 경로가 사장 판정을 받았다. 미래 CAD 경로는 기준 deck 으로 수렴하므로(후속작업 13) 조합의 형상 원본은 그때도 deck 이다 |

## 근거 — CAD 경로의 위상

**경로의 위상 판정이 결정의 출발점이다**(2026-09-18 제품 방침). 형상 파라미터화 갈래가 둘인데 지위가 다르다 — 실측 전문은 [[Code-Map-User-Flow-Geometry-Parameterization-CAD]] 소유이고, 이 문서의 CAD 경로 좌표는 `feat/reference-model-manifest` @ `32dda58` 기준이다.

| 경로 | 내용 | 처분 |
|---|---|---|
| 정규 경로 | `.inp`·`.dat` 을 parameterize — **기준 deck** 이 원장·커서·Set 키·조합·스탬프의 대상이다 | 이 묶음의 개선 대상 |
| 현행 CAD 실행 경로 | `.prt`→`.stp` 재생성 + `.wbpj` 조합 + ANSYS Journal(`DashJobRunner.cpp:1395-1435`). **deck 층을 통째로 우회한다** — 조건은 `.wbpj` 안에 동결되고(Journal 설정에 형상 파라미터만 실린다 — `:2579-2617`) 케이스 deck 은 Journal 산출물일 뿐 파이프라인의 기준이 아니다 | **특화된 일회성 경로 — 사장 예정, 개선 불개입** |
| 미래 CAD 경로 | CAD 생성 형상 → meshing → 파트·NSET 매칭 → `.inp`/`.dat` 생성 → **기준 deck 으로 등록해 정규 경로에 합류** | 후속작업 13. 코드맵 3-6(Meshing 다이얼로그·Match NSET 자리표시자)이 이 방향의 착수 흔적이다 |

```
[미래 CAD 경로] 기준 deck 으로의 수렴
   │   1. .prt 파라미터화 — 형상 생성 (NX)
   │   2. meshing — 현행 GUI 밖 Journal 몫이 GUI 안으로
   │   3. 파트·NSET 매칭 — 재메싱으로 무효화된 노드 집합을 재부착
   │   4. .inp/.dat 생성 → 기준 deck 으로 등록
   ▼

[합류 후] 정규 경로와 동일
       원장(kind deck)·Set referenceModel·조합·스탬프에 CAD 분기가 없다
```

수렴이 성립하면 **CAD 는 기준 deck 의 업스트림 생성기**이고 deck 층 이후 개념에 CAD 분기가 없다. 그래서 **이 묶음은 CAD 에 손대지 않는다** — 처분은 #366 봉합(M5 제외·죽은 전역 읽기 제거)까지이고, 형상 출처 영속화(D29\~D31)는 유보해 미래 경로 설계(후속작업 13)에 동반시키며, 실행 경로에 붙였던 결정(D32·D33)은 철회했다. `.prt` 는 지금 고려하지 않는다.

| | Morphing 갈래 | CAD 갈래 |
|---|---|---|
| 형상 원본 | 기준 deck — `referenceModel` 이 곧 형상 | `.prt` — deck 과 별개 파일. 미래 경로에서 기준 deck 의 출처가 된다 |
| Set 의 해석 기준 | `referenceModel` (D14·D18) | **미지정 허용**(M5 제외·#366) — 좌표 2(`DashGeometryParameterCADWidget.cpp:345`)의 소비 사슬은 현행 무산출이다(코드맵 D5) |
| 렌더 | VTK — displayed 커서 | OCCT(STEP) — 커서 2층 밖 |
| 형상 원본의 영속 결합 | `referenceModel.{uuid, path}` | 현행 **없음** — 승격 시 configs 복사가 유일한 흔적이고 재Load 가 지운다(코드맵 D15·D17). 유보된 D31 의 `cadSource` 가 후속작업 13 에서 닫는다 |

**D29(유보) — kind 로 넓히되 자격은 좁게 유지한다.** uuid 산식은 상대경로 v5 파생(P2)이라 RW 와 무관하게 성립하고, 등록·복원·rename 이관(D24)의 논리도 kind 무관이다. 반면 기준모델 자격의 근거(RW 세션 확장자·part 조회·커서 렌더)는 `.prt` 에서 성립하지 않으므로, 원장을 "프로젝트가 채택한 입력 원본" 목록으로 일반화하되 자격을 kind 로 가른다. 32dda58 항목은 `{path, sha256, size, mtimeMs}` 뿐이라(`DashReferenceModelLedger.cpp:99-101`) kind 는 후속작업 13 착수 시 도입하고 부재 = `deck` 로 무이관 판정한다. 문서 1 9절의 "`.prt`+`.wbpj` 는 파일 둘이 한 항목" 스케치는 채택하지 않는다 — 두 파일의 소비 주체가 갈리고(`.prt` 는 CAD 모듈·NX 데몬, `.wbpj` 는 사장 경로의 Launcher·Journal) 조인은 `input_files` 의 `target_component` 가 이미 든다(`DashReferenceFileWidget.cpp:1125`).

**D31(유보) — 핀 시점이 생성이 아니라 승격인 이유.** 생성 시점에는 핀할 값이 없다 — `.prt` 는 Set 과 무관한 세션 전역 1개(`DashSolverNxCad.h:69` `m_originalPrtPath`)이고 Set 생성 전에 로드됐다는 보장이 없다. Launcher 가 `referenceModel` 대신 `parameterization` 을 DOE 선택 시점에 기록하는 것(D18 부속)과 같은 형태다. 승격([Set Design Variable])은 이 모듈의 유일한 영속화 지점이라, 그 시점 핀이 곧 "값이 처음 생기는 시점" 핀이다. configs `.prt` 복사는 현행 유지다 — 사장 경로(Optimizer CAD 프리뷰의 configs 조회 `DashOptimizerWidget.cpp:1606` · wbpj DOE)가 읽는 값이라 불개입이고, 결합의 정본이 `cadSource` 로 바뀌므로 재Load 보관본 삭제(코드맵 D15)는 사장 경로 안의 결함으로 격리된다.

**D32·D33 철회 — 근거가 사장 경로에 있었다.** D32 가 끊으려던 라벨-locator 겸업(`<part>` 는 NX 파트 표시명인데 — 데몬 `main.py:159` `DisplayName ?: Name ?: "A"` 폴백 — 소비자가 `.prt` 를 붙여 configs 파일명으로 쓴다: `DashOptimizerPresentationModel.cpp:19-24` → `DashOptimizerWidget.cpp:1606` · `DashModelRunner.cpp:1530`)은 실측 결함이지만, 소비자 전부가 사장 경로라 교체 없이 경로째 제외한다. D33 의 조합·스탬프 kind 일반화와 CAD 조합 `conditions` ∅ 는 wbpj 경로를 조합 개념에 수용하려던 특례라 함께 철회한다 — D25·D26 은 원안(deck 단일)이고, 미래 경로 합류 후에도 조합의 형상 원본은 deck 이다.

**이 묶음에서 닫히는 것은 없다 — 전부 격리·유보다.**

| | 항목 |
|---|---|
| 유보 — 후속작업 13 동반 | Set↔`.prt` 미저장(코드맵 D17 — `cadSource` 가 닫을 예정) · 원장 kind · `.prt` 등록(D29\~D31) |
| 사장 경로로 격리 — 불개입 | 재Load 보관본 삭제(코드맵 D15) · 표시명-파일명 겸업(D32 철회) · temp `.prt` 누적(코드맵 D16) · wbpj DOE 전체 |
| 범위 밖 유지 | `.prt` 캐시 전역 1개(문서 5 B절) · `.wbpj`·`.stli` 원장 편입(후속작업 5) · 미래 경로 본 설계(후속작업 13 — 생성 deck 의 등록 지점과 P4 관계 · NSET 재부착) |

## 검증 한계

| 항목 | 근거 강도 | 비고 |
|---|---|---|
| `.prt` Load 가 커서 밖 | **강** | 커서·기준 지정은 `dat`·`inp`·`dfsxml` 분기뿐(`DashMainWindow.cpp:2283`). `.prt` 분기는 NX 큐잉·OCCT 렌더만 — CAD 경로 좌표는 전부 `feat/reference-model-manifest` @ `32dda58` 기준 |
| Set↔`.prt` 결합 부재 · 보관본 삭제 | **강** | [[Code-Map-User-Flow-Geometry-Parameterization-CAD]] 3-8 절 · D15·D17 — 본문 확인 실측 문서 |
| wbpj DOE 의 조건 미참여 | **강** | Journal 설정이 CAD Independent 파라미터만 싣는다(`DashJobRunner.cpp:2579-2617`) — deck 치환 홉 없음 |
| 원장 kind 미반영 | **강** | 항목 = `{path, sha256, size, mtimeMs}`(`DashReferenceModelLedger.cpp:99-101`) — "근거" 절에 기록 |
| wbpj 경로 사장·기준 deck 수렴 방향 | — | 제품 방침 결정(2026-09-18)이다. 실측이 아니다 — 코드맵 3-6(Meshing 다이얼로그·Match NSET 자리표시자)이 방향을 뒷받침한다 |
