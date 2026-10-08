# 모듈별 기준 deck 소유 — 매니페스트 도입 · 설계

> 작업 묶음: 프로젝트 매니페스트 도입과 모듈 의존성 관리
> 관련 Issue: #239
> 마스터: [[Project-Manifest-0-Work-Order]] — 착수 순서와 문서 배치
> 기반 문서: [[Project-Manifest-1-Context-Registry-And-Model-Identity]] (원장 스키마·단계) · [[Project-Manifest-2-Active-Cursor-Data-Coupling]] (좌표 1·2·9 · C-1·C-2)
> 착수 계획: [[Project-Manifest-4-Ticket-Slicing]] — [작업 3] 티켓은 이 문서 기준으로 추가한다

## 개요

**각 모듈이 자기 기준 deck 을 소유하고 자기 JSON({Set}.json) 에 영속화한다.** 원장(`referenceModels.json`)에서 모듈까지 경로를 잇는 마지막 단계다.

앞선 문서가 확정한 것 둘.

| 사실 | 출처 |
|---|---|
| Set 의 영속 정의 어디에도 기준 deck 이 없다 — 유일한 출처가 전역 커서이고, 진입 시점의 커서가 Set 의 deck 을 정한다 | [[Project-Manifest-2-Active-Cursor-Data-Coupling]] A절 |
| 원장은 숨김 configs 의 `referenceModels.json` — 키는 content uuid(D24), `path` 는 프로젝트 루트 상대경로 필드다 | [[Project-Manifest-1-Context-Registry-And-Model-Identity]] 6절 |

**열린 질문은 전부 닫혔다.** [작업 3] 티켓은 [[Project-Manifest-4-Ticket-Slicing]] 의 T14\~T27 이다. G8·G9 티켓 재스펙은 문서 4.

## 용어

이 문서 전체에서 아래 뜻으로 쓴다.

| 용어 | 뜻 |
|---|---|
| 기준 deck | Set 이 편집·해석의 기준으로 삼는 해석 deck 파일. 모듈 JSON 의 키 이름은 `referenceModel`(D14) |
| 원장 | 숨김 configs 의 `referenceModels.json`. 키는 content uuid, `path` 는 루트 상대경로 필드 (문서 1) |
| content uuid (D24) | 원장 키. 현행 산식은 루트 상대경로의 v5 파생 — 내용 기반(sha256) 이관은 마스터 후속작업 4 로 유보 |
| 조합 | DOE 조합 — **Geometry Set 1 + Condition Set N** 묶음(D23). 파이프라인 불변식의 단위. JSON 표현은 D25, 산출물 표현은 D26 |
| 조합 id | 조합에서 파생하는 문자열 하나 — `{geometry setId}+{condition setId 정렬 연접 ","}`(SI-5 · D26 확정). 홉별 검증 = 이 값의 비교 |
| setId | Set 의 안정 식별자 — 12자리 랜덤 hex, 각 `{Module}_{Set}.json` 의 `setId` 키가 정본(SI-1\~SI-2). 원문은 [[Project-Manifest-Set-Identity-And-Decision-Revisions]] |
| 핀 | Set 이 자기 기준을 `{Set}.json` 에 1회 고정하고 이후 바꾸지 않는 것. Condition·Morphing 은 **deck 핀**(생성 시점 전역 커서의 deck), Preprocessor·Builder·Runner·Optimizer 는 **조합 핀**(최초 입력 연결 시점의 조합 id) |
| 스탬프 | 산출물 파일에 write-once 로 박히는 생성 시점 조합 id(+ 형상 deck) — 산출물의 출생 기록. 자리는 D26 |
| 기록 | Launcher 의 조합 저장 — 핀이 아니다. DOE 선택이 바뀌면 다시 쓰고 검증도 없다(D21) |

## 결정

번호는 [[Project-Manifest-0-Work-Order]] 결정 사항 표의 연번이고 개정 이력도 그 표가 정본이다 — 여기는 현재 판만 적는다. D12·D22·D24 는 다른 문서 소관이라 빠진다(D24 는 용어 절). **2026-09-21 개정분(D15 재개정·D16 3차 개정·D20 재개정·D21 부속·D26 산식 확정·D27 재개정·D28 폐기·setId)의 원문·사유는 [[Project-Manifest-Set-Identity-And-Decision-Revisions]] 가 갖는다.**

### Set 의 기준 deck — 저장·주입·이행·표시

| # | 질문 | 결정 |
|---|---|---|
| D11 (개정) | Set 은 기준 deck 참조를 어떤 값으로 드나 | **uuid 1차 + path 병기**(D24). uuid 로 원장을 직조회하고, path 는 표시·디버깅·원장 유실 폴백이다. 두 값이 갈리면 원장이 정본이고 모듈 저장값을 backfill 한다 |
| D13 | `referenceModel` 값을 누가·언제 Set 모델에 주입하나 | **생성·복원 시점.** 신규 Set 은 생성 핸들러가 그 시점의 전역 reference 를 핀하고, 기존 Set 은 `loadFromJson` 이 채운다. 위젯 `setModel` 은 모델 값만 읽는다 |
| D14 (개정) | 모듈 `{Set}.json` 의 어느 키·어떤 스키마로 쓰나 | **`referenceModel` 객체 하나**에 `uuid`(조인 키 — D24)·`path`(표시·폴백). 스키마 버전은 올리지 않는다 — 키 부재가 곧 구버전 판정이다 |
| D15 (재개정) | 키가 없는 구프로젝트는 어떻게 이행하나 | **Lazy backfill — 핀 출처는 Set 자신의 DV `source`.** 진입 시 자기 데이터에서 deck 을 유도해 핀하고 다음 저장 때 backfill. 유도 실패 시에만 전역 폴백, 빈 값이면 핀하지 않는다. **multi-source json 은 진입 시 1회 자동 분할** — 아래 D15 절 |
| D16 (3차 개정) | 저장된 참조가 원장·파일로 해석되지 않으면 | uuid 직조회(히트 시 `path` 의 파일 존재·적재 검사) → 미스면 **v5(path) 재파생 조회 1회**(원장 스캔·uuid backfill 제거) → 실패·파일 부재 시 **미지정 + 로그.** 재Load 회복은 원장 유실·손편집 한정 — 아래 D16 절 |
| D17 | 기준 deck 을 바꾸는 UI 를 두나, 어디에 보여주나 | **변경 UI 불요 확정** — 기준 deck 은 생성 시점에 고정된다. 표시는 Parameters 도크 제목줄 |
| D28 (폐기) | 구버전 multi-source Condition json 의 핀 deck 밖 DV 행을 어떻게 보이나 | **폐기 — multi-source 자동 분할(D15 재개정) 후 핀 deck 밖 행이 성립하지 않는다.** 회색·잠금·툴팁 기계장치는 함께 걷는다 — 아래 D15 절. 원문·사유는 [[Project-Manifest-Set-Identity-And-Decision-Revisions]] |

### DOE 조합과 파이프라인 불변식

| # | 질문 | 결정 |
|---|---|---|
| D18 (재개정) | 기준을 소유하는 모듈 집합은 | **파이프라인 8모듈 — Condition · Morphing(deck 핀) · CAD(핀 없음 — 부속 2) · Launcher(DOE 선택 시 조합 기록 — 부속) + Preprocessor · Builder · Runner · Optimizer(조합 핀).** Analyzer·AIGeo 만 제외. ModelRunner 의 NodeSet 소스는 별도 키로 존치. 근거는 "전수 조사"·"파이프라인 스탬프" 절 |
| D18 부속 2 | CAD Set 도 `referenceModel` 키를 받나 | **받지 않는다 — `referenceModel` 미지정 허용(마스터 M5 제외)이고 형상 출처 `cadSource` 는 유보다(마스터 D31 — 후속작업 13 동반).** 해석 deck 소비가 없다는 실측(#366 — `m_loadedFilePath` 판독 0·표는 `applyNxCadParameterJson`)이 근거다. wbpj DOE 실행 경로는 사장 판정이라 조합·스탬프 개념 밖이다(마스터 D32·D33 철회 — [[Project-Manifest-CAD-Path-Disposition]]) |
| D18 부속 | Launcher Set 은 무엇을 드나 | **`referenceModel` 을 두지 않고 `parameterization` 하나를 든다.** 기준 deck 은 `parameterization.geometry.deck` 이다. deck 핀이 성립하지 않는 것은 실측이다 — Launcher Set 생성은 variant 만 쓰고 DV 선택이 없어 그 시점에 핀할 값이 없다. 조합은 DOE 선택(T24)이 채우고 선택이 바뀌면 다시 쓴다(기록 — D21) |
| D19 (개정) | 파이프라인 전 구간이 같은 기준임을 무엇으로 보장하나 | **산출물 스탬프 + Set 핀 + 홉별 검증.** 단위는 deck 이 아니라 **조합**이다. Preprocessor 가 dataset XML 에, Builder 가 model_info.json 에 생성 시점 조합 id 를 write-once 로 찍고, 각 모듈은 최초 연결 시 핀한 id 와 입력 스탬프의 일치를 검증한다 |
| D20 (재개정) | 스탬프와 핀이 불일치하면 | **차단.** 판정 기준은 **조합 일치**다 — 서로 다른 deck 의 입력이라도 같은 조합이면 정상. 불일치 시 거부하고 "다른 조합이면 새 Set" 안내 — D17 동형. **구버전 폴백 불도입 — 무스탬프 산출물은 연결 차단** + "스탬프 없는 구산출물 — 재실행 필요" 안내(차단 문형 동형). 핀은 id 를 든 첫 입력에서 걸린다 |
| D21 (재개정) | Launcher 도 검증하나 | **기록만, 검증 없음.** 기록 단위는 조합(D23)이다. DV 는 기준 deck 에서 생성하고 형상·조건 동일 변종 deck(해석 설정 수정)을 해석하는 워크플로우 수용은 유지. 부속(실행 템플릿 deck 기록)은 **철회**(2026-09-22 — PR #530 리뷰) — 원문·사유는 [[Project-Manifest-Set-Identity-And-Decision-Revisions]] |
| D23 | Set·DOE 와 기준 deck 의 카디널리티는 | **Condition·Geometry Set : referenceModel = 1:1 확정 + DOE 는 Geometry Set 1 · Condition Set N 을 참조**(PR #389 A안). batch run 단위는 **고유 조건 deck**(deck 공유 Set 은 한 run, run 수 = 고유 deck 수 — 공유 deck 겹침 차단은 D27). Condition DV 표의 deck 쌓기(`source` 구분)는 폐기 — DOE 샘플링이 N개 Set 의 DV 를 합산한다. C안(batch run 1 통합)은 추후 확장. 조합의 표현은 D25. 정본은 문서 0 결정표 |
| D25 (개정) | 조합을 JSON 으로 어떻게 적나 | **형상 1 + 조건 맵** — `geometry` 객체 하나와 Condition Set 의 **setId 를 키로 하는(`name` 병기 — SI-4)** `conditions` 맵. deck 당 3요소 묶음 목록은 버린다 — **모든 기준 deck 의 형상은 같고 해석조건만 다르다**는 전제가 확정돼 형상 중복의 근거가 사라졌다. 평평한 튜플 배제는 유지. 상세는 "조합의 표현" 절 |
| D26 (산식 확정) | 산출물에는 조합의 무엇을 박나 | **조합 id + 형상 deck 둘만.** dataset XML 의 `model_info` 섹션과 `model_info.json` 최상위에 `parameterizationId`(검증용)와 `geometryDeck`(morph 원본 — uuid·path 병기)을 쓴다. id 산식은 **SI-5 확정** — 정렬 setId 연접("산출물이 드는 것" 절). 조합 정의는 Launcher `{Set}.json` 이 갖고, 조합 상세·DV 키 매핑은 **후속**으로 미룬다 |
| D27 (재개정) | Condition Set 다중 선택 UI 와 DV 이름 충돌은 어떻게 푸나 | **체크 가능 콤보 + Set 접두 이름 + `{set: setId(+name 병기), key: bare}` 복합 참조(SI-4).** DV 표시·키는 `{Set 이름}.{DV 이름}`, deck 치환은 그 run 의 deck 을 공유하는 Set 들의 DV 만 bare key 로(공유 deck 의 bare 이름 겹침은 선택 시 차단). 접두가 필수인 근거와 동반 수정 3건(morph 매칭 포함)은 "DOE 다중 선택과 DV 이름" 절 |

부속 결정 1건 — Morphing 모델의 죽은 멤버 `m_fileName`(`DashGeometryParameter.h:50`, 호출부 0)은 자리 신설 시 **삭제**한다.

## 소유자 — 파이프라인 8모듈

소유자 집합은 D18 — Analyzer·AIGeo 만 제외한 8모듈. 앞단(Condition·Morphing)은 deck 핀, CAD 는 핀 없음, Launcher 는 조합 기록, 후단 4모듈은 조합 핀이다. 근거는 이 장의 "파이프라인 스탬프"·"전수 조사" 절이다.

### 진입 1회 읽기 3좌표

세 좌표가 같은 형태다. 진입 시 커서를 1회 읽어 모델에 핀하고 그 뒤 다시 읽지 않는다. 이 문서는 **그 1회의 출처만** Set 키로 바꾼다 — 단 좌표 2(CAD)는 소비 사슬이 무산출이라(#366 실측) **죽은 전역 읽기 제거로 끝**이고(문서 4 T16 — D18 부속 2), 출처 교체는 좌표 1·9 둘이다.

| 좌표  | 자리                                              | 모듈        |
| --- | ----------------------------------------------- | --------- |
| 1   | `DashConditionParameterizationWidget:313-315`   | Condition |
| 2   | `DashGeometryParameterCADWidget:345-347`        | CAD       |
| 9   | `DashMainWindow:3271`(`onStartMorphingClicked`) | Morphing  |

좌표 9 는 Morphing 모델 자리 신설([[Project-Manifest-2-Active-Cursor-Data-Coupling]] C-1)이 경로 핀을 더한 뒤라야 나머지 둘과 같은 형태가 된다. Start Morphing 클릭이 Morphing 모델의 유일한 데이터 주입 지점이므로, 그 시점의 핀이 곧 D13 의 생성 시점 핀이다.

### ModelRunner 의 NodeSet 소스 — 별도 키 (D18)

형태가 다르다 — 진입 1회 읽기가 아니라 **비영속 사용자 선택의 영속화**다.

| 사실 | 좌표 |
|---|---|
| part/NodeSet 콤보는 Morphing 기준 deck 의 configs 복사본에서 채워진다 | `DashModelRunnerWidget.cpp:1029-1031` |
| NodeSet 소스 `m_datFilePath` 는 파일다이얼로그로만 채워지고(필터 = `SupportedInputs`), Set 재진입 시 매번 클리어된다 | `:1020` · `:1958-1961` |
| 다이얼로그 없이 콤보에서 NodeSet 을 고르면 빈 경로로 morph 가 실패한다 | `DashModelRunner.cpp:2207-2209` |
| NSET 라벨 조회는 원본 deck 우선, 없으면 morphed deck 폴백 | `DashMorphingUtils.cpp:374-380` |

처분 — `ModelRunner_{Set}.json` 에 D14 와 같은 `path`·`uuid` 객체로 영속화하되 키는 **별도 키(가칭 `nodeSetSource`)** 다. D18 재개정으로 `referenceModel` 은 전 모듈에서 기준 deck 을 뜻하고, ModelRunner 의 그 키는 상위 deck 핀이 가져간다(아래 파이프라인 스탬프 절). 쓰기 지점은 다이얼로그 핸들러(`onDatFileEditClicked`) 하나이고, `updateReferenceFileAndPart` 의 무조건 클리어(`:1020`)는 저장값 복원으로 바뀐다. 키 부재·빈 값이면 morph 시 콤보를 채운 deck 으로 폴백한다 — 빈 경로 실패 결함이 함께 닫힌다. 사용자가 콤보 deck 과 다른 파일을 고르면 NSET 라벨이 어긋날 수 있는데, 그 위험은 영속화와 함께 수용한다(결정).

해석·표현(해소 필요 사항 3 · T18 스펙 수정) — 읽기는 D16 트리(원장 조회)를 타지 않는 **경로 직접 사용 + 존재 검사**다. 표현은 **루트 상대경로만** — 루트 밖 파일을 고르면 프로젝트 안으로 복사 후 상대경로를 저장한다(P1 동형 — 복사 위치는 Add Files to Project 관례인 프로젝트 루트). 절대경로 영속은 없다 — G6 이 닫은 결함 부류(프로젝트 이동 시 파괴)의 재도입이고 경로 규약의 유일한 신규 예외였다([[Project-Manifest-Set-Identity-And-Decision-Revisions]]). uuid 는 T12 산식으로 파생만 하고 원장에 쓰지 않는다.

### 파이프라인 스탬프 — 전 구간 동일 조합 (D19\~D21 · D23)

요구 불변식 — Launcher 가 뱉은 데이터를 Preprocessor 가 파싱하고, Builder 가 학습하고, Runner·Optimizer 가 구동하는 전 과정이 **동일 조합 기준**이어야 한다. deck 단일성은 불변식이 아니다 — 해석 종류(인장·압축·피로)별 deck N 개가 한 DOE 에 들어오는 것이 정상 워크플로우다(PR #389 A안).

**메커니즘은 두 줄이다**(D19).

1. 산출물은 생성 시점의 조합 id 를 스탬프로 받는다 — write-once, 재스탬프 없음.
2. 각 모듈 Set 은 최초 연결한 입력의 id 를 핀하고, 이후 다른 id 의 입력·연결·사용을 차단한다(D20).

홉별 검증은 그 문자열 비교 1회다. 산출물이 드는 것은 조합 전체가 아니라 id + 형상 deck 이고(D26 — "산출물이 드는 것" 절), 조합의 JSON 표현은 형상 1 + 조건 맵이다(D25 — "조합의 표현" 절).

| 모듈 | 핀 ({Set}.json) | 스탬프 (산출물, write-once) | 검증 |
|---|---|---|---|
| Launcher | **DOE 선택 시 조합 기록** — 형상 1 + 조건 맵(D23·D25). deck uuid 는 각 Set 의 `referenceModel` 에서 전사. `input_files` 는 실행 대상 목록으로 유지·병기(`DashReferenceFileWidget.cpp:1107-1132`) | 실행 시점에 계산한 조합 id 를 **DOE Table 에** 기록 — 그 Table 이 곧 이 run 묶음의 정의다 | 없음 — 기록만(D21) |
| Preprocessor | 최초 입력 연결 시 조합 id 핀 | dataset XML `model_info` 섹션의 `parameterizationId` + `geometryDeck` | 입력(Launcher 의 조합 id)과 자기 핀 일치 — 불일치 차단(D20). **같은 조합 안의 deck 이 서로 달라도 정상이다** |
| Builder | 최초 dataset 연결 시 | `model_info.json` 최상위에 두 키 전사 | dataset id 와 자기 핀 일치 — 차단. MCU(사용자 CSV)는 deck-무관 소비 추적으로 미지정 허용 |
| Runner · Optimizer | 최초 model_info 연결 시(`m_viewSourceContext` 대입 `DashModelRunner.cpp:1333` · `loadModelInfoFromFolder` `DashOptimizer.cpp:701-710`) | — | model_info id 와 자기 핀 일치 + morph 대상 deck 이 조합의 Geometry Set deck 과 일치 — 차단 |

**스탬프에 Set 이름을 쓰지 않는 이유.** 산출물에 문자열 Set 이름을 박으면 rename·빈 번호 재사용으로 검증이 무너진다 — write-once 라 갱신 경로도 없다. 그래서 스탬프가 드는 것은 Set 이름이 아니라 **조합 id 하나**이고, 산식은 SI-5(정렬 setId 연접 — D26 확정)다. 이 이름 배제 근거는 setId(SI-4)가 Set 참조 전반으로 일반화했다.

규칙 넷.
- **핀은 최초 연결 1회.** 이후 다른 조합의 입력·연결·사용은 차단하고 "다른 조합이면 새 Set" 을 안내한다(D20) — D17 과 동형. "연결 시점 갱신" 개념은 없다.
- **핀은 연결 즉시 저장한다** — 다음 저장 대기는 핀 없는 산출물 창(검증 기준값 부재)을 만든다. 연결 전 신규 Set 은 키 부재(미지정)가 정상이다. 차단 문구는 한 문형으로 통일한다 — "이 Set 은 {조합} 기준으로 고정되어 있습니다. 다른 기준 조합은 새 Set 을 만들어 사용하세요."
- **Launcher 만 검증이 없다**(D21) — DV 는 기준 deck 에서 생성하고 형상·조건 동일 변종 deck 을 해석하는 워크플로우를 수용한다. 변종 실행 결과도 조합 스탬프로 하류에 흐르며, 그 동일성 판단은 사용자 몫이다.
- **구버전 폴백 불도입**(D20 재개정) — 무스탬프 산출물은 연결을 차단하고 "스탬프 없는 구산출물 — 재실행 필요" 를 안내한다(차단 문형 동형). 라이브 체인은 part 명 조회 용도만 잔존한다. 폴백 유지 + "출처 미검증" 표시보다 코드가 적고, 무경고 재바인딩 결함이 구산출물에서 신호가 아니라 소멸로 닫힌다. 라이브 `parameterization` 에서 id 를 계산해 핀하는 것은 금지(D26 — 편집 상태 기준 불가), 산출물 재스탬프도 없다(불변) — 재생성 시에만 찍는다. 내용 드리프트(파일 덮어씀) 탐지는 uuid 가 상대경로 v5 파생인 현행에선 불가 — sha256 이관(마스터 후속작업 4) 유보.

**도입 근거 — 현행은 deck 정체가 홉에서 유실된다.** 현행 구현은 조합은커녕 deck 정체조차 보장하지 못한다 — 중간 홉에서 유실되고 가변 간접 참조로 대체된다.

| 홉 | 검증된 사실 |
|---|---|
| Launcher 산출 | deck 정체 존재 — DOE Table `source[]` 에 `Morphing\|deck\|part` 라벨, run 폴더명도 deck basename 파생(`DashDoeConfigManager.cpp:206-258`) |
| Preprocessor 파싱 — **유실 지점** | 라벨을 모듈 JSON 파일명("GeometryParameter_SetN.json")으로 치환해 dataset XML 의 source 로 기록(`DashDataProcessor.cpp:2825-2838`) |
| Builder | 치환된 source 를 무해석 운반(`DashModelBuilder.cpp:545-556`) |
| Runner·Optimizer 사용 | 그 파일명으로 **사용 시점에 configs 의 라이브 JSON 을 다시 열어** deck 을 해석(`DashModelRunner.cpp:1507-1527`) |

산출물이 싣는 것은 deck 정체가 아니라 **살아있는 Set JSON 참조**다. `deleteSet` 이 UI 에 배선되어 있어(`DashProject.h:47` · `DashMainWindow.cpp:550-551`) Geometry Set 을 지우고 동명으로 다른 deck 기준 Set 을 만들면 기존 학습 산출물 전부가 무경고 재바인딩된다 — 어느 홉에도 일치 검증이 없고 uuid 도 없어 탐지 불가.

스키마 자리(D26) — dataset XML 은 **`model_info` 섹션 안의 `parameterizationId` 문자열 + `geometryDeck` dict** 다. 루트 직하가 아닌 이유는 Builder 가 그 섹션만 head/tail 로 찾아 읽고 전사하기 때문이다(`DashModelBuilder.cpp:546-556` · `:1565-1620`) — 밖에 두면 새 스캔 경로가 생긴다. `model_info.json` 은 최상위 같은 이름 키이고, 전사는 기존 read-merge-write 에 한 줄이다. Launcher 쪽은 `{Set}.json` 의 `parameterization` 이 정의이고 `DOE Table` 이 실행 시점 id 를 든다("산출물이 드는 것" 절). 조합 상세·DV 키 매핑 사이드카는 후속이다.

부수 효과 — Runner·Optimizer 의 deck 1차 출처가 라이브 체인에서 model_info 스탬프로 바뀌고 라이브 체인(`getReferenceFileAndPart`)은 part 명 조회 용도만 잔존한다(D20 재개정 — 구버전 폴백 불도입). Launcher 의 `getMorphingSourceInfo` 대체(작업 항목 4)는 자기 `parameterization.geometry.deck` 이 출처가 되고, 해소 필요 사항 5 의 Geometry Set 매핑도 그 참조로 좁혀진다. Optimizer 프리뷰의 전수 스캔·전량 morph(`DashOptimizerWidget.cpp:1468-1493`)는 `geometryDeck` 1건 morph 로 닫힌다.

### 전수 조사 — 모듈별 deck 출처와 판정

Set 단위 모듈 전수(`restoreExistingModules` 의 접두사 맵, `DashProject.cpp:1245-1258`)에 대해 deck 경로의 출처를 역추적했다. 전역 커서를 deck 출처로 읽는 Set 모델이 3좌표뿐이라는 것은 문서 2 의 전수와 일치하고, 이 조사는 커서 밖 출처를 분류한 것이다.

| 모듈 | 모델 | deck 출처 | 판정 (개정) |
|---|---|---|---|
| Morphing · Condition | `DashGeometryParameter` · `DashConditionParameterization` | 전역 커서 (좌표 1·9) | 소유 대상 — 기확정 |
| CAD | `DashGeometryParameterCAD` | 전역 커서 (좌표 2 — 무산출 사슬, #366) | 키 미도입 — #366 봉합까지. 형상 출처 `cadSource` 는 유보(마스터 D31·D18 부속 2) |
| Analysis Launcher | `DashAnalysisLauncher` | 자기 Set JSON — `input_files[].path`(상대경로, `DashReferenceFileWidget.cpp:1107-1132`) · `DOE Table.source` | **소유 대상** — 자기 포맷뿐이고 uuid·원장 연동이 없다. `parameterization` 조합으로 표준화(D18 부속 · 파이프라인 스탬프 절) |
| Model Runner | `DashModelRunner` | model_info → GeometryParameter JSON 체인(`getReferenceFileAndPart`, `DashModelRunner.cpp:1473-1562`) + NodeSet 소스만 비영속 다이얼로그 | **소유 대상** — model_info 스탬프 핀(파이프라인 스탬프 절) + NodeSet 소스 별도 키(D18) |
| Optimizer | `DashOptimizer` | 같은 체인(`resolveGeometrySource`, `DashOptimizerWidget.cpp:1444-1450`) — 단 프리뷰는 configs `*.dat`·`*.inp` 전수 스캔 후 **전량 morph**(`:1468-1493`) | **소유 대상** — model_info 스탬프 핀(파이프라인 스탬프 절). 스캔 결함도 핀 1건 morph 로 닫힌다 |
| Data Preprocessor · Model Builder(+MCU) | `DashDataProcessor` · `DashModelBuilder(MCU)` | deck 기능 사용 없음 — 재검증 확정(본문 확인 포함). 입력이 해석 결과(`.rst/.odb/.dfr/.op2`)·학습 데이터(xml/csv)뿐 | **소유 대상 (재개정)** — deck 을 쓰지 않으나 불변식의 검증·전달 홉. 핀 + 산출물 스탬프(파이프라인 스탬프 절) |
| Results Analyzer · AI Geometry Generation | — | Set JSON 없음 / 복원 미등재 — 재검증 확정. Analyzer 는 Launcher `DOE Table.source` 라벨 문자열 파싱만 하고 deck 파일 접근이 없다(`DashResultsAnalyzerWidget.cpp:1173-1210`). AIGeo 는 미배선 스텁(`DashProject.cpp:292-299`, `setProjectDirectory` 호출부 0) | 대상 아님 |

각주 — ModelBuilder 산출물 `model_info.json` 은 하류(Optimizer·ModelRunner) deck 해석 체인의 유일한 운반 매체다(`DashModelBuilder.cpp:545-548` 이 데이터셋 XML 의 `parameter` 서브트리를 무해석 복사). 이 운반이 가변 간접 참조뿐이라는 점이 파이프라인 스탬프(D19)의 도입 근거다.

번복 기록 — 릴레이 소유안은 배제했다가 같은 날 파이프라인 불변식 요구로 번복했다. 배제 근거 둘 다 무너졌다 — "소유 = 사용 위배"는 홉별 검증이 소비자가 되며 해소, "leaf 핀이 단절을 흡수한다"는 leaf 핀이 생성 시점 provenance 를 동결하지 못해(위 유실 지점) 결함. 현 결정은 파이프라인 스탬프 절.

Launcher 에 딸린 결함 1건 — `DashReferenceFileWidget::getMorphingSourceInfo()`(`:543-604`)가 Launcher JSON 에 존재하지 않는 `DV-Geometry`/`ConditionParameter` 섹션을 읽어 항상 빈 값을 돌려주고, deck 자동 추천과 part 노드수 매칭(`:617`·`:637`·`:869`)이 무작동이다. **[작업 3]-4 에 포함** — 소유자 모델에서 직접 읽도록 교체하면 살아난다.

## 설계

### D13 — 주입은 생성·복원 시점

채움 지점이 둘이고, 위젯은 어느 쪽도 아니다.

| 경로 | 채움 |
|---|---|
| 기존 Set 복원 | `loadFromJson` 이 `referenceModel` 키를 읽어 모델에 핀 |
| 신규 Set 생성 | 생성 핸들러가 그 시점의 전역 `referenceFilePath()` 를 핀. Morphing 은 좌표 9 의 1회 읽기가 그 자리다 |

위젯 `setModel`(좌표 1)은 모델 값만 읽는다 — 위젯의 전역 읽기가 사라진다. Condition 은 기존 `m_loadedFilePath` + `refreshFromLoadedAnalysis()` 형태를 유지하고 영속 키(`path`·`uuid`) 멤버를 더한다. CAD 는 키를 받지 않는다(D18 부속 2 — `cadSource` 는 마스터 D31 유보). Morphing 은 C-1 대로 같은 형태를 신설하고 C-2 로 `DashMorphingSettings` 에 모델을 주입한다 — 주입이 오면 [작업 1]에서 옮겨 둔 `referenceModelChanged` 구독은 제거된다.

생성자 인자 방식은 배제했다 — 생성 호출부 전부에 인자가 추가되고 복원 경로(`loadFromJson`)와 이원화된다. setModel 말미 lazy 핀은 위젯에 한 번도 바인딩되지 않은 Set 이 deck 미지정인 채 저장될 수 있어 배제했다. 단 D15 의 backfill 은 이 lazy 형태를 **구버전 한정으로** 쓴다.

### D14 — 스키마: `referenceModel` 객체 하나

```json
{
  "variant": "…기존 키…",
  "referenceModel": {
    "path": "models/wing.dat",
    "uuid": "a3f2c1e0-…"
  }
}
```

| 항목      | 내용                                                               |
| ------- | ---------------------------------------------------------------- |
| 낱말      | 원장 `referenceModels.json` 과 맞춘다. 두 값이 한 덩어리로 붙어 다닌다              |
| `uuid`  | 원장 키 = content uuid(D24). **1차 조인 키** — 이 값으로 원장을 직조회한다           |
| `path`  | 프로젝트 루트 상대경로 = 원장 `path` 필드와 같은 문자열(D3). 표시·디버깅·원장 유실 폴백         |
| 스키마 버전  | 올리지 않는다. additive 변경이라 키 부재가 구버전 판정이고, 그 판정이 D15 의 backfill 트리거다 |
| 두 값 불일치 | uuid 로 찾힌 원장 항목의 `path` 가 저장값과 다르면 원장 값으로 backfill — 원장이 정본이다(D11). **후속작업 4(sha256 이관) 전까지 유보** — uuid ≡ v5(path)인 동안 발화 조건이 없다(D16 3차 개정) |

### D15 — 마이그레이션: lazy backfill (재개정)

키가 없으면(구프로젝트) 진입 시 **Set 자신의 DV `source` 에서 deck 을 유도**해 핀하고 다음 저장 때 backfill 한다. 유도 실패 시에만 전역 reference 폴백, 빈 값이면 핀하지 않는다 — 현행 `ConditionWidget:314` 가드와 동형이다. 소급은 없다 — 이미 핀된 Set 은 불문한다.

| 항목 | 내용 |
|---|---|
| 유도 — Condition | DV `source` 의 상대경로 그대로 |
| 유도 — Morphing | bare filename 을 configs 복사본 → 원장 `path` → 루트 스캔 순으로 해석. 복수 히트는 없다고 가정 — 결정적 1건(정렬 후 첫번째) + 로그 |
| 전역 폴백 | 유도 실패 시에만. 빈 값이면 핀하지 않음(유지) |
| 원장 등록 | 유도분은 원장에 등록한 뒤 핀한다 — "등록 지점은 Load 핸들러 하나(M3·P4)" 의 유일한 예외. 등록 없이는 다음 열기의 D16 1단이 미스라 backfill 이 자기 자신을 못 넘긴다. 등록 실패 시 핀하지 않고 다음 진입에 재시도 |

전역 출처를 버린 사유 — 전역은 첫 진입 시점의 우연(다른 deck Load 상태)을 영구 동결한다. G7 이 닫은 대표 결함이 마이그레이션 코호트에서 1회 재현된 채 D17(변경 UI 불요)로 정정 불가가 된다. 종전 현행은 매 진입 재평가라 복구 가능했으므로 이 케이스에 한해 개악이었다 — Set 자신의 DV `source` 가 더 충실한 역사적 증거다. 원문은 [[Project-Manifest-Set-Identity-And-Decision-Revisions]].

| 근거 | 내용 |
|---|---|
| 선례 | DV-Condition 로더가 어긋난 uuid 를 이름으로 대신 붙이고(`DashConditionParameterization.cpp:495-497`) 다음 저장 때 backfill 한다(`:444-447`) |
| 일괄 변환 배제 | 구프로젝트는 원장 자체가 비어 있다 — Load 전에는 열기 시점에 채울 원천이 없다. lazy 규약은 유지되고 출처만 바뀐다 |
| 체감 | Set 이 원래 만들어진 deck 으로 복원된다 — 진입 시점의 전역 상태와 무관 |

마스터 과도기 동작 1(“Set 먼저 클릭, Load 나중” 순서)의 복구 경로는 전역 폴백이 겸한다 — Load 뒤 Set 재진입 시 핀이 걸린다.

**구프로젝트의 multi-source Condition json**(한 json 에 여러 deck 의 조건이 `source` 로 구분 — D23 이전의 정상 워크플로우)은 **진입 시 1회 자동 분할한다** — deck 별로 Set 을 갈라 쓰고 원본은 `.bak` 으로 보존하며 결과를 통지한다(선택지 없음). D27 다중 선택이 같은 워크플로우의 정식 대체로 dev 에 있어, 상시 하위호환 기계장치 대신 1회 마이그레이션으로 치환한다.

분할 후 핀 deck 밖 행(foreign 행)이 성립하지 않으므로 **D28 은 폐기**됐고 그 기계장치를 함께 걷는다 — `DashDesignVariableModel` 의 회색·잠금·툴팁 처리, `loadFromJsons` 의 핀 deck 인자, `FECondition` 예외 판정, DOE 의 구 multi-source 읽기 경로.

쓰기 자리(해소 필요 사항 2 확정) — `referenceModel` 키는 실 라이터에 얹는다. 라이터 3종(`saveDvCondition`·`saveDvGeometry`·`saveMorphingSettings`)이 전부 read-merge-write 라는 실측은 유지하되, **G7 이 얹는 것은 2종**이다 — `saveDvGeometry`(CAD)는 키 미도입으로 빠진다(D18 부속 2). 빈 스텁 `saveSettings`(호출부 0)는 구현하지 않는다 — "다음 저장 때"는 실 라이터의 다음 실행을 뜻한다.

### D16 — 해석 실패 참조: 미지정 + 로그 (3차 개정 · 해소 필요 사항 1)

D5 대로 해제 지점이 없으므로 이 상태는 **앱 밖 조작으로만** 생긴다. 원인이 둘로 갈린다 — 원장 유실·JSON 손편집은 **미등재**를 만들고, 파일 rename·삭제는 원장이 단조 증가(D5)라 항목이 남아 **등재 + 파일 부재**를 만든다.

```
referenceModel 해석
├─ 1. uuid 로 원장 직조회 (D24) → 히트 시 path 의 파일 존재·적재 검사
│      └─ 파일 부재·적재 실패 → 핀하지 않고 로그 (stale 원장 항목)
├─ 2. 미스면 v5(path) 재파생 조회 1회 — 원장 스캔·uuid backfill 없음 (3차 개정)
└─ 3. 둘 다 실패 → 핀하지 않고 로그. Set 은 deck 미지정 상태로 열린다
```

스캔 분기를 걷은 사유 — uuid ≡ v5(상대경로)인 동안 "uuid 미스 + path 히트"는 손편집·부분 손상에서만 성립한다. "원장 유실 한정" 명분은 유실된 원장을 스캔할 수 없어 자기모순 — 발화 조건 없는 분기였다. 진짜 스캔 폴백은 sha256 이관(마스터 후속작업 4)이 uuid ≠ v5(path) 상태를 실제로 만들 때 도입하고, D11 의 "두 값 갈림 → 원장 정본 backfill" 규칙도 그때까지 유보다. 원문은 [[Project-Manifest-Set-Identity-And-Decision-Revisions]].

자동 재등록은 두지 않는다 — 등록 지점은 Load 핸들러 하나다(M3·P4). 유일한 예외는 D15 의 구버전 backfill — DV `source` 에서 유도한 deck 은 원장에 등록한 뒤 핀한다. 등록 없이는 다음 열기의 D16 1단이 미스라 backfill 이 자기 자신을 못 넘긴다. 등록 실패 시엔 핀하지 않고 다음 진입에 재시도. 재Load 자동 회복은 **원장 유실·손편집(같은 상대경로 복귀) 한정**이다 — 같은 상대경로 키와 같은 uuid(상대경로 v5 파생)가 재생된다. rename 은 새 경로로 새 항목이 생길 뿐 옛 참조가 돌아오지 않는다 — rename 회복은 마스터 후속작업 4(sha256 이관) 전까지 없다.

### D17 — 표시: Parameters 도크 제목줄

Set 의 기준 deck 을 바꾸는 UI 는 두지 않는다 — 생성 시점 고정이고, 바꾸려면 Set 을 다시 만든다. 대신 지금 보는 Set 이 어느 deck 에 붙어 있는지를 Parameters 도크 제목줄에 띄운다.

| 자리 | 사실 |
|---|---|
| `m_rightDock` | `new QDockWidget("Parameters", this)`(`DashMainWindow.cpp:464`). 앞단 3위젯을 포함한 모듈 위젯 전부가 이 도크의 `m_rightStackedWidget` 에 산다(`:470-519`). 제목은 리터럴 고정 — 갱신 지점 0건 |
| 선례 | `m_leftDock->setWindowTitle(...)`(`:3008`·`:3068`) |
| 갱신 시점 | Set 진입(모델 바인딩) 시. 소유 모델의 deck 파일명을 붙이고, 미지정이면 기본 "Parameters" |

D7(Mesh View 도크 = 렌더 파일명)과 짝이다 — 렌더와 기준이 다른 상태가 두 제목줄로 드러난다.

적용 범위(해소 필요 사항 4 확정 · #366 개정) — 표시는 **앞단 3모듈(Condition·Morphing·Launcher)만.** CAD 는 표시할 해석 deck 이 없어 기본 "Parameters" 다(#366 봉합 — `cadSource` 표기 여부는 마스터 D31 유보와 함께 후속). Launcher 는 deck 핀이 아니라 조합 기록이지만(D18 부속) 사용자가 직접 기준을 고르는 앞단이라 표시 대상으로 남는다. 파이프라인 후단 4모듈(Preprocessor·Builder·Runner·Optimizer)과 비소유 모듈 진입 시 기본 "Parameters" 로 복귀한다 — 후단은 연결 전 키 부재(미지정)가 정상 상태이고, deck 이 편집 기준이 아니라 소비 추적 속성이라 제목줄 정보가치가 낮다.

**Launcher 는 조합이라 파일명 하나가 안 나온다**(D25 이후). 표기는 `{geometry.deck 파일명} +{조건 Set 수}` 다 — 형상은 조합 전체에 하나이므로 대표성이 있고, 접미는 조건 Set 개수를 알린다. 개수 단위가 deck 이 아닌 것은 **형상·조건 deck 의 겹침이 강제되지 않아서다** — DOE 실행의 morph 는 run 템플릿 deck 자체에 적용되고(`MorphFromDoeSamples` 에 `templatePath` 전달, `DashJobRunner.cpp:1702-1716`) 형상 핸들 정의 deck 과 템플릿이 다른 변종 워크플로우(D21)가 허용되므로, deck 수 산술(−1)은 전제가 없다. 접미의 수는 DOE 체크 콤보의 "N Sets selected" 와 같은 값이다. 예외 하나 — 조건 Set 이 1개이고 그 deck 이 `geometry.deck` 과 같으면(uuid 비교 — 사실상 단일 deck) 접미를 생략해 다른 앞단 모듈과 같은 표시가 된다. `parameterization` 이 비어 있으면(선택 전·구프로젝트) 기본 "Parameters".

### 조합의 표현 — 형상 1 + 조건 맵 (D25)

**모든 기준 deck 의 형상은 같고 해석조건만 다르다**는 것이 전제다. 해석별로 다른 형상을 쓰는 확장은 고려하지 않는다 — deck 당 3요소 묶음 목록을 버리는 근거가 이것이다.

```
✗ 평평한 튜플     { geometrySet, conditionSets[N], deckUuids[N] }
✗ deck 당 묶음    [ { deck, geometry, condition }, … N ]        ← 형상이 N번 중복
✓ 형상 1 + 조건 맵
  {
    "geometry":   { "set": <setId>, "name": <Set 이름>, "deck": { "uuid": …, "path": … } },
    "conditions": { "<setId>": { "name": <Set 이름>, "deck": { "uuid": …, "path": … } }, … }
  }
```

조인 키는 setId + `name` 병기다(SI-4 — `referenceModel` 의 `{uuid, path}` 동형). 불일치 시 Set json 이 정본이다.

근거 넷.

| | |
|---|---|
| 소비자가 조인을 안 한다 | 각 조건 항목이 자기 deck 을 들고 있어 배열 위치로 짝지을 일이 없다 — 평평한 튜플을 배제한 근거는 그대로 산다 |
| 중복이 없다 | 형상이 조합 전체에 1개다. deck 당 묶음은 같은 형상 참조를 N번 적는데, 그 중복을 정당화하던 "해석별 다른 형상" 확장이 고려 대상에서 빠졌다 |
| 순서·중복이 구조로 막힌다 | `conditions` 가 Set 키 맵이라 같은 Set 이 두 번 들어갈 수 없고, 조합 비교가 키 집합 비교가 된다 |
| XML 이 배열을 못 적는다 | dataset XML 어휘가 `dict_item`·`dict`·`string`·`float` 뿐이다(`DashResultXmlWriter.cpp:935-974`). 맵은 그대로 전사되고 배열은 인덱스 키로 우회해야 한다 |

#### 누가 갖고 누가 쓰나

| 역할 | 주체 | 자리 | 하는 일 |
|---|---|---|---|
| 정의·소유 | Launcher Set | `AnalysisLauncher_{Set}.json` 의 `parameterization` | 스키마·읽기·쓰기는 T20, 값을 채우는 것은 DOE 선택(T24)이다. 선택이 바뀌면 다시 쓴다 — 핀이 아니고 검증도 없다(D21) |
| 동결 | Launcher 실행 | 그 Set 의 `DOE Table.parameterizationId` | 실행 시점 조합으로 id 를 계산해 Table 에 박는다. 하류가 읽는 것은 이 값이다 — 편집 중인 `parameterization` 이 아니다 |
| 1차 소비 | Launcher 실행 | — | `conditions` 의 고유 deck 마다 batch run 생성(deck 공유 Set 은 한 run — D23 개정), `geometry.deck` 은 morph 원본 |
| 검증·전달 | Preprocessor | dataset XML + 자기 핀 | 입력 run 의 조합 id 와 자기 핀 비교 → 불일치 차단. XML 에 id·`geometryDeck` 전사 |
| 전달 | Builder | `model_info.json` + 자기 핀 | XML 의 id 검증 후 두 키 전사 |
| 최종 소비 | Runner · Optimizer | 자기 핀 | `model_info` 의 id 검증. `geometryDeck` 이 프리뷰 morph 대상 1건 |

**조합의 정의를 읽는 것은 Launcher 뿐이다** — 하류 4모듈이 조합에서 쓰는 것은 동일성 판정(id)과 morph 원본(`geometry.deck`) 둘뿐이고, 그 둘은 산출물에 전사돼 따라온다(D26). `conditions` 상세를 해석할 이유가 하류에는 없다.

#### 산출물이 드는 것 — 조합 id + 형상 deck (D26)

산출물에 박히는 것은 조합 전체가 아니라 두 값이다.

| 키 | 값 | 쓰는 쪽 |
|---|---|---|
| `parameterizationId` | 조합 id 문자열 | 홉별 일치 검증 — Preprocessor·Builder·Runner·Optimizer |
| `geometryDeck` | `{uuid, path}` — 조합의 `geometry.deck` 전사 | Runner·Optimizer 의 morph 원본. Optimizer 프리뷰가 이 1건만 morph 한다 |

id 산식은 **SI-5 로 확정**됐다 — `{geometry setId}+{condition setId 정렬 연접 ","}`, 예: `a3f2c1e0b7d4+1f9e2a6c0d38,8b07c5e1f2a9`. 해시 없음 — 홉별 검증은 그대로 문자열 비교 1회, 멱등(같은 Set 집합 = 같은 문자열), 길이 13×(N+1). 자기 기술적이라 산출물만 열어도 구성 setId 가 보인다. **id 파싱은 금지** — 조인은 병기 필드다(`geometryDeck` 별도 동봉 유지). deck uuid 파생 후보는 폐기 — 조합 동일성 단위를 deck 집합으로 붕괴시켜 D23 정의(Set 참조)와 어긋난다. 원문은 [[Project-Manifest-Set-Identity-And-Decision-Revisions]].

**계산·저장 시점은 DOE 실행이고 자리는 그 Set 의 `DOE Table` 이다.** Launcher 의 `parameterization` 은 사용자가 바꿀 수 있는 편집 상태라 하류의 기준이 될 수 없다 — 선택을 바꾸면 과거 run 의 출처까지 소급해 달라 보인다. DOE Table 은 실행마다 통째로 재기록되므로(`DashDoeConfigManager.cpp:433-443`) Table 하나가 곧 run 묶음 하나이고, id 를 거기 두면 그 묶음에 고정된다. 하류(Preprocessor)는 입력 run 이 속한 Table 의 id 를 읽는다.

남는 위험 — 같은 Set 에서 DOE 를 다시 돌리면 Table 이 교체되는데 **옛 run 폴더는 디스크에 남는다.** 그 폴더들이 새 id 아래 묶여 보인다. run 단위 식별자가 없어서 생기는 것이고 이 묶음의 범위 밖이다(후속).

**`geometryDeck` 을 함께 박는 이유** — 하류가 조합에서 실제로 소비하는 것은 동일성 판정과 morph 원본 둘뿐인데, id 는 파생값이라 deck 으로 되풀리지 않는다. 대안은 id 로 Launcher Set 을 역조회하는 것인데, `deleteSet` 으로 그 Set 이 사라지면 산출물이 deck 을 잃는다 — 라이브 참조를 끊으려던 D19 가 되돌아온다. uuid·path 병기는 D11 과 같은 형태다.

| | |
|---|---|
| 얻는 것 | 홉별 검증이 문자열 비교 1회다. XML 어휘 제약을 안 탄다. 학습 쪽 파서가 그 섹션을 읽어도 영향이 최소다 |
| 잃는 것 | 산출물의 id 에서 구성 setId 는 읽히나(SI-5 자기 기술) Set 이름·상세는 Launcher `{Set}.json` 에만 있다. 조합 상세·DV 키 매핑의 자리는 **후속**이다(아래) |
| 발급 시점 | id 는 DOE 실행(T27)에서 처음 계산된다 — 산식은 SI-5(D26 확정) |

**조합 상세를 어디에 두나 — 산출물 단위의 문제다.** Set 단위 설정(`{Set}.json`)은 살아 있어 rename·이관 때 함께 갱신되므로 이 문제가 없다. 자리가 필요한 것은 나중에 못 고치는 산출물 쪽이고, **후속으로 미룬다**(D26). 지금 결정은 어느 방안과도 양립한다 — 산출물이 드는 `parameterizationId` 가 조인 키이므로, 상세가 어디에 오든 그 값으로 이어 붙는다.

### DOE 다중 선택과 DV 이름 (D27)

Condition Set N 개 선택은 UI 한 곳이 아니라 **다섯 자리**를 함께 바꾼다. 실측으로 드러난 세 자리(영속 포맷·실행 루프·morph 매칭)는 티켓 T25·T26 으로 갈려(morph 매칭은 T26 동승) 같은 PR(G8)에 들어온다.

| 자리 | 현행 | 처분 |
|---|---|---|
| 선택 UI | `dvConditionCombo` 단일 선택(`DashAnalysisLauncherWidget.cpp:511-518`) | **체크 가능 콤보** — 닫힌 상태는 "N Sets selected". 가로 레이아웃(콤보 2 + Set 버튼)과 Set 버튼 흐름을 유지한다. Geometry 콤보는 단일 유지 |
| DV 합산 | `loadFromJsons(QStringList, dir)` 가 이미 복수 파일을 받아 append 한다(`DashDesignVariableModel.cpp:313-352`) | 목록만 늘린다. 합산 자체는 추가 설계가 없다 |
| 영속 포맷 | `"Selected Design Variables"` 가 **2원소 배열**[condition, geometry](`DashAnalysisLauncher.cpp:1140-1143`)이고 Preprocessor 가 위치로 읽는다(`DashDataProcessor.cpp:2800-2830`) | geometry 1 + conditions N 을 담는 형태로 바꾸고 **그 판독기를 같은 티켓에서 고친다** — 가르면 디스크에 두 포맷이 공존한다 |
| 실행 루프 | `generateInputCases` 가 템플릿 목록을 받고 `.first()` 만 쓴다(`DashJobRunner.cpp:1285-1290`) | **고유 조건 deck 별 루프** — deck 공유 Set 은 한 run 으로 합쳐진다(D23 개정). run 폴더명은 현행(deck basename 파생) 그대로 충돌이 없다 |
| morph 매칭 | `DashMorphingDoeExecutor` 가 DOE Table `headers` 를 bare 이름과 문자열 매칭한다 — 형상 핸들 `updateHandlesWithDoeValues`(`:1099-1102`) · 조건 DV `attachConditionDvValues`(`:511-513`). 접두 headers 는 전부 미스라 형상 morph·조건 DV 부착이 통째로 죽는다 | 열별 `{set, key}` 로 소속 Set 의 핸들·DV 맵을 찾아 bare key 로 매칭 — 접두 도입과 같은 PR(T26 동승) |

**DV 이름 규칙 — 항상 `{Set 이름}.{DV 이름}` 접두.** 접두가 선택이 아닌 이유는 치환기에 있다 — `writeCaseDat` 은 headers 전체를 순회하며 `${이름}` 을 치환하므로(`DashJobRunner.cpp:468-474`), 서로 다른 deck 의 Set 이 같은 DV 이름을 가지면 **앞 열 값이 양쪽 deck 에 박히고 뒤 열은 무시된다.** 조건 DV 이름은 deck 의 조건 이름 파생이고 GUI 편집 경로가 없어(Name 열 비편집) 사용자 rename 으로 피할 수도 없다.

**deck 을 공유하는 Set 간 bare 이름 겹침은 선택 시 차단한다.** deck 공유 Set 은 한 run 으로 합쳐지므로(D23 개정) 같은 `${토큰}` 에 샘플 값 두 개가 경합해 물리적으로 성립하지 않는다. T24 의 체크 콤보가 deck(uuid) 공유 Set 들의 체크 DV bare 이름 교집합을 검사해 겹치면 선택을 거부하고 안내한다(D20 문형 동형). 다른 deck 간 겹침은 접두·`{set, key}` 로 이미 안전하다.

| 층 | 표현 |
|---|---|
| 표시 · DOE Table `headers` · `model_info` parameter 키 | `{Set 이름}.{DV 이름}` — 선택 Set 수와 무관하게 항상. 이름이 선택 조합에 따라 달라지지 않아야 resample·dataset 비교가 성립한다 |
| 내부 참조 | `{ set: <setId>, name: <Set 이름 병기>, key: <bare 이름> }` 복합(SI-4 — 불일치 시 Set json 정본). DV 전용 id 는 두지 않는다 — DV 이름 변경은 deck 수정과 동치라 재파라미터화가 전제다 |
| deck 치환 | 그 run 이 속한 Condition Set 의 DV 만 **bare key** 로 치환한다. 형상 DV 는 전 run 공통 |

구프로젝트의 DOE Table 은 접두 없는 headers 를 그대로 읽는다 — 기록된 headers 로 해석하므로 규칙 변경이 소급되지 않는다. 구 Table 의 `{set: 이름}` 도 기록된 대로 해석한다 — 이름 폴백, 재기록 없음(SI-4).

## 작업 항목 — [작업 3]

마스터 순서 절의 [작업 3] 목록과 같다. 선행은 [작업 1](3좌표가 전역 `referenceFilePath()` 로 옮겨져 있을 것) · [작업 2](원장과 `DashProject` API).

| # | 항목 | 결정 |
|---|---|---|
| 1 | Morphing 모델 자리 신설(C-1) + `DashMorphingSettings::setModel` 신설·주입(C-2) + `m_fileName` 삭제 + `referenceModelChanged` 구독 제거 | — |
| 2 | Condition·Morphing 2모듈에 `referenceModel` 멤버 + {Set}.json 영속화 + 생성·복원 주입 + 구버전 backfill — CAD 는 키 없음(D18 부속 2·#366 봉합) | D13 · D14 · D15 |
| 3 | 좌표 1·9 의 1회 읽기 출처를 전역 reference 에서 Set 키로 — 좌표 2(CAD)는 죽은 전역 읽기 제거(#366 봉합). 전역 읽기는 신규 생성 시점과 backfill 에만 남는다 | D13 · D16 |
| 4 | Reference File 콤보를 원장 조회로 · DV `source` 를 상대경로로 · `getMorphingSourceInfo` 를 소유자 조회로 교체 | — |
| 5 | ModelRunner NodeSet 소스 소유 — 다이얼로그 선택 영속화(별도 키) + 빈 값 폴백 | D18 |
| 6 | Parameters 도크 제목줄 표시 | D17 |
| 7 | 파이프라인 스탬프·핀·검증(조합 id 단위 — D26) — Launcher 조합 기록(검증 없음) → 조합 id 발급 → Preprocessor 검증·핀 + dataset XML 에 `parameterizationId` → Builder 검증·핀 + model_info 전사 → Runner·Optimizer 스탬프 1차 핀 + morph 일치 검증. 티켓 = 문서 4 의 T20(G8) · T27·T21\~T23(G9). **G8 부터 setId 뒤다** — 조합 키가 setId 이고 id 가 setId 파생(SI-5)이다. setId 정본은 [[Project-Manifest-Set-Identity-And-Decision-Revisions]] | D14 · D19 · D20 · D21 · D23 · D25 · D26 |
| 8 | DOE 샘플링의 Condition Set 다중 선택 — 체크 가능 콤보로 Condition Set N 개 선택 + DV 합산 샘플링 + DV 이름 Set 접두 + deck 별 batch run 루프(deck 공유 Set 은 한 run) + 공유 deck 의 bare 이름 겹침 차단. Condition DV 표의 deck 쌓기(`source` 구분)를 대체한다. 동반 수정 3건(`"Selected Design Variables"` 포맷과 그 판독기 · `generateInputCases` 의 `.first()` · morph 실행기 헤더 매칭)은 T25·T26 — 같은 PR(G8) | D23 · D27 |

### 함께 정리되는 결함

| 결함 | 좌표 | 해소 자리 |
|---|---|---|
| NodeSet 선택 시 빈 소스 경로로 morph 실패 | `DashModelRunner.cpp:2207-2209` | 항목 5 |
| NodeSet 소스가 세션마다 재선택 필요(비영속) | `DashModelRunnerWidget.cpp:1020` | 항목 5 |
| `getMorphingSourceInfo` 무작동 — deck 자동 추천·part 매칭 죽음 | `DashReferenceFileWidget.cpp:543-604` | 항목 4 |
| bare filename 재해석 중복 4곳 · `findAnalysisFiles` 파일명 dedup | 문서 1 8절 | 항목 4 |
| “Set 먼저 클릭, Load 나중” 복구 경로 부재(과도기 동작 1) | 마스터 과도기 표 | 항목 2 의 backfill |
| Optimizer 프리뷰가 configs 의 무관 deck 까지 전량 morph | `DashOptimizerWidget.cpp:1468-1493` | 항목 7 — 핀된 deck 1건 morph |
| 학습 산출물의 deck 참조가 라이브 Set JSON 이라 Set 삭제·동명 재생성 시 무경고 재바인딩 | `DashModelRunner.cpp:1507-1527` · `DashProject.h:47` | 항목 7 — 스탬프 검증이 탐지·차단 |

마스터 **후속작업 9**(Optimizer 전수 스캔·전량 morph)는 항목 7 에 **편입 확정**됐다(해소 필요 사항 9) — 핀이 곧 프리뷰 선택 출처다. 마스터 후속작업 표가 편입을 기록한다.

## 해소 필요 사항 — 전부 해소

재검토(코드 대조)가 남긴 쟁점 10건. 전부 해소됐다 — 상세는 각 반영처가 정본이다.

| # | 쟁점 | 확정 | 반영처 |
|---|---|---|---|
| 1 | ~~D16 "원장 히트 + 파일 부재" 분기 부재~~ | D16 개정 — 히트 시 파일 존재·적재 검사, 부재면 미지정 + 로그 | D16 절 · T15 |
| 2 | ~~D15 "다음 저장 때" 의 쓰기 자리~~ | 실 라이터 3종에 얹는다 — 빈 스텁 `saveSettings` 는 구현하지 않는다 | D15 절 · T15 |
| 3 | ~~NodeSet 소스 키의 해석·표현~~ | 경로 직접 사용 + 존재 검사 · 별도 키 `nodeSetSource`. 표현은 T18 스펙 수정으로 재개정 — 루트 밖은 복사 후 상대, 절대경로 영속 없음([[Project-Manifest-Set-Identity-And-Decision-Revisions]]) | NodeSet 소유자 절 · T18 |
| 4 | ~~D17 표시 범위~~ | 앞단 3모듈만(#366 개정으로 CAD 제외) — 그 외 기본 "Parameters" | D17 절 · T19(3모듈)·T20(Launcher 표기) |
| 5 | ~~`getMorphingSourceInfo` 대체 소유자~~ | Launcher 자기 `parameterization.geometry.deck` | T17 |
| 6 | ~~좌표 9 파트-핀 미스매치 · 빈 경로 가드~~ | 미스매치 = 경고 후 중단 · 빈 경로 = 콤보 deck 폴백 | T16 · T18 |
| 7 | ~~파생 소유자의 갱신·불일치 처리~~ | 최초 연결 1회 핀 + 연결 즉시 저장 + 이후 차단 — 갱신 개념 없음 | 파이프라인 스탬프 절 · T21\~T23 |
| 8 | ~~Launcher 키와 `input_files` 의 구분~~ | 기록만·검증 없음(D21) — Launcher 의 키는 `parameterization`(D18 부속), `input_files` 는 실행 대상 목록 | 파이프라인 스탬프 절 · T20 |
| 9 | ~~D18 재개정의 문서 동기화~~ | 실행 완료 — 문서 0·문서 4 갱신 | 문서 0 · 문서 4 |
| 10 | ~~스탬프 스키마·부작용 상세~~ | 구스키마는 D23 재개정으로 무효 — D26 이 대체(`parameterizationId`·`geometryDeck`). `loadLabelMetadata` 키 필터는 유효 | 파이프라인 스탬프 절 · T21·T22 |

## 재개정으로 열린 사항 — 전부 해소

D23·D24 반영이 열었던 미결 3건. 전부 해소됐다.

| # | 쟁점 | 확정 | 반영처 |
|---|---|---|---|
| 11 | ~~DOE 조합 스탬프의 스키마 상세~~ | D25 개정 + D26 — 형상 1 + 조건 맵, 산출물에는 `parameterizationId` + `geometryDeck` 둘. 상세·DV 키 매핑은 후속 | "조합의 표현"·"산출물이 드는 것" 절 · T21\~T23 |
| 12 | ~~다중 선택 UI 와 DV 이름 충돌~~ | D27 — 체크 콤보 · `{Set 이름}.{DV 이름}` 접두 · `{set, key}` 복합 참조 · run 소속 Set 만 치환. 동반 수정은 T25·T26 | "DOE 다중 선택과 DV 이름" 절 · T24\~T26 |
| 13 | ~~읽기 전용 행 표시 UX~~ | D28 로 확정했다가 **폐기(2026-09-21)** — multi-source 자동 분할(D15 재개정)로 foreign 행 자체가 불성립 | D15 절 · [[Project-Manifest-Set-Identity-And-Decision-Revisions]] |

## 검증

| 항목 | 확인 |
|---|---|
| Morphing Set 두 개를 번갈아 열어도 각자의 deck 을 유지한다 | 문서 2 검증 승계 |
| DV `source` 문자열과 configs 로 복사된 dat 이 그 Set 의 deck 을 가리킨다 — 디스크 확인 | 좌표 4 |
| 구프로젝트를 열고 Set 진입 → 자기 DV `source` 의 deck 이 핀되고(전역 상태 무관) 다음 저장 후 {Set}.json 에 `referenceModel` 키가 생긴다 | D15 |
| {Set}.json 의 `path` 를 원장에 없는 값으로 손편집 → 진입 시 미지정 + 로그, 그 deck 을 Load 하고 재진입하면 회복 | D16 |
| 트리 체크박스·Optimizer 프리뷰가 진입한 Set 의 deck 을 못 바꾼다 | [작업 1] 검증 재확인 |
| ModelRunner: 다이얼로그 없이 NodeSet morph 가 성공(폴백)하고, 다이얼로그 선택이 재기동 후 유지된다 | D18 |
| Set 전환마다 Parameters 도크 제목이 그 Set 의 deck 파일명을 띄운다 | D17 |
| Launcher: DOE 선택 후 {Set}.json 에 `parameterization` 이 생기고 `input_files` 는 그대로다. 선택을 바꾸면 다시 쓰인다 | D18 부속 |
| Launcher: Parameters 도크 제목이 `{형상 deck 파일명} +{조건 Set 수}` 를 띄운다 — 단일 deck(조건 Set 1개 = 형상 deck)이면 접미 없음, 선택 전에는 "Parameters" | D17 |
| DOE 를 실행하면 그 Set 의 `DOE Table` 에 조합 id 가 박히고, 선택을 바꿔 다시 실행하면 새 Table 이 새 id 를 받는다 | D26 |
| Launcher: 조합의 deck 과 다른 변종 deck 을 골라 실행해도 허용되고 기록은 유지된다 | D21 |
| DOE 샘플링에서 Condition Set N 개를 선택하면 각 Set 의 DV 가 합산 샘플링되고 batch run 이 고유 deck 별로 돈다 — deck 공유 Set 은 한 run 의 case 파일에 함께 치환된다 | D23 · D27 |
| deck 을 공유하는 Set 2개가 같은 bare DV 이름을 체크한 채 동시 선택하면 차단된다 | D27 |
| 접두 headers 로 DOE 를 실행해도 형상 morph 와 조건 DV 부착이 동작한다 — morph 매칭이 `{set, key}` 를 탄다 | D27 |
| 서로 다른 deck 의 Condition Set 2개가 같은 DV 이름을 가져도 **두 값이 각자의 deck 에 따로 박힌다** — run 별 case 파일을 열어 치환값 확인 | D27 |
| 같은 Set 을 단독 선택했을 때와 다중 선택했을 때 DV 이름이 같다(항상 접두) | D27 |
| Preprocessor: 다른 조합 id 의 run 폴더 입력은 차단되고, 같은 조합은 — deck 이 서로 달라도 — 파싱 성공 + dataset XML `model_info` 에 `parameterizationId` 가 생긴다 | D19 · D20 · D23 · D26 |
| Builder: 핀과 다른 조합 id 의 dataset 선택이 차단되고, model_info.json 최상위에 id 가 전사된다 | D19 · D20 · D26 |
| Runner·Optimizer: 다른 조합 id 의 model_info 연결·사용은 차단되고, 같은 id 는 진행된다. id 없는 구산출물은 연결 차단 + "재실행 필요" 안내 | D19 · D20 · D26 |
| 같은 Set 조합으로 DOE 를 다시 만들면 조합 id 가 같은 값으로 재생된다 — 파생 산식의 멱등 | D26 |
| 구프로젝트 multi-source Condition json: 진입 시 deck 별 Set 으로 자동 분할되고 `.bak` 이 남고 통지가 뜬다 — 분할 후 어느 Set 의 DV 표에도 foreign 행이 없다 | D15 재개정 |
| Geometry Set 을 지우고 동명·다른 deck 으로 재생성해도 기존 model_info 사용이 차단된다 — 재바인딩 탐지 | D19 · D20 |
| Optimizer: 프리뷰가 `geometryDeck` 1건만 morph 한다 — configs 의 무관 deck 은 건드리지 않는다 | D18 재개정 · D26 |

## 검증 한계

| 항목 | 근거 강도 | 비고 |
|---|---|---|
| 결정 D13\~D21 · D23 · D25\~D28 | — | 결정이다. 실측이 아니다 |
| DV 이름이 deck 템플릿의 치환 토큰 | **강** | `DashJobRunner.cpp:447-478` 본문 확인 — headers 전수 순회 `replace("${name}")`. 이름 생성 규칙은 `DashConditionParameterization.cpp:188-204`(`dvKey`), Name 열 비편집은 `DashDesignVariableModel.cpp:84-104` |
| dataset XML 어휘가 dict_item·dict·string·float 뿐 | **강** | `DashResultXmlWriter.cpp` 의 `createElement` 전수 — 4종 30건. 스탬프가 맵이어야 하는 근거 |
| Builder 가 model_info 섹션만 찾아 전사 | **강** | `DashModelBuilder.cpp:546-556`(전사) · `:1565-1620`(head/tail 로케이터 + 첫 sample 키 대조) 본문 확인 |
| `"Selected Design Variables"` 2원소 배열과 위치 판독 | **강** | 쓰기 `DashAnalysisLauncher.cpp:1140-1143` · 읽기 `DashDataProcessor.cpp:2800-2830` 본문 확인 |
| `generateInputCases` 가 템플릿 1개만 사용 | **강** | `DashJobRunner.cpp:1285-1290` — 목록을 받아 `.first()` 만 쓴다 |
| morph 실행기의 headers bare-이름 매칭 2곳 | **강** | `DashMorphingDoeExecutor.cpp` 본문 확인 — `updateHandlesWithDoeValues`(`:1099-1102`)가 headers 를 핸들 param name 과, `attachConditionDvValues`(`:511-513`)가 DV-Condition 키와 문자열 매칭. D27 동반 수정 3건째의 근거 |
| DOE morph 대상 = run 템플릿 deck 자체 | **강** | `DashJobRunner.cpp:1702-1716` — `MorphFromDoeSamples` 에 `templatePath`(canonical) 전달 본문 확인. 형상 핸들 정의 deck 과 템플릿의 겹침을 강제하는 장치 없음 — D17 표기 단위(조건 Set 수)의 근거 |
| Condition 위젯이 모델 역할 3종을 미러링 | **강** | `DashConditionParameterizationWidget.cpp:438-450` 본문 확인 — flags·ForegroundRole·ToolTipRole |
| Launcher Set 생성 시점에 조합을 핀할 값이 없음 | **강** | `createNewSet` 이 variant 만 쓰고(`DashProject.cpp:592`) DV 선택은 위젯 콤보에서 온다 — D18 부속의 근거 |
| DOE Table 이 실행마다 통째로 재기록 | **강** | `DashDoeConfigManager.cpp:433-443` 본문 확인 — headers·min·max·source 를 참조 Set 에서 재시드. 조합 id 를 Table 에 두는 근거 |
| resample 이 참조 Set 의 headers 로 prior 를 평평화 | **강** | `DashAnalysisLauncher.cpp:115-125` 본문 확인 — DV 이름 규칙 변경이 이 경로에 걸린다(T25) |
| 좌표 1·2·9 · Set 영속 정의에 deck 없음 | **강** | 문서 2 의 전수. `dev` @ `c989257` |
| ModelRunner NodeSet 경로 4건 | **강** | `DashModelRunnerWidget.cpp:361-391`·`:1006-1044`·`:1944-1964` · `DashModelRunner.cpp:2200-2219` · `DashMorphingUtils.cpp:352-385` 본문 확인 |
| Optimizer 전수 스캔·전량 morph | **강** | `DashOptimizerWidget.cpp:1440-1493` 본문 확인 |
| `m_rightDock` 리터럴 고정·스택 구성 | **강** | `DashMainWindow.cpp:460-481` 본문 확인 |
| Set 모듈 전수 열거 · Launcher `input_files` 영속 · 출처 분류 | **강** | 2026-09-13 재검증 — Launcher 라이터(`DashReferenceFileWidget.cpp:1084-1133`)·ModelRunner 체인(`DashModelRunner.cpp:1473-1562`)·Optimizer 연결(`DashOptimizer.cpp:697-757`)·프리뷰 유일 호출부(`DashOptimizerWidget.cpp:1489`) 본문 확인 |
| Preprocessor · Analyzer · AIGeo 의 deck 기능 사용 없음 | **중\~강** | 탐색 에이전트 2건의 전수 grep(부정 증거) + 입력 포맷 확인(결과 파일·학습 데이터 전용) |
| ModelBuilder 의 deck 기능 사용 없음 | **강** | 본문 재확인 — 유일한 configs 접근 `loadLabelMetadata`(`:1149-1226`)는 write-only 멤버로 소비 0, 운반 복사 `:545-556`, 학습 실행 인자 `:599-609`, 테스트셋 vtu 는 자기 산출물(`:1945-1965`) |
| 파이프라인 deck 정체 유실 구조 | **강** | 본문 확인 — DOE 라벨·run 폴더명(`DashDoeConfigManager.cpp:206-258`) · source 치환(`DashDataProcessor.cpp:2800-2874`) · 라이브 재해석(`DashModelRunner.cpp:1507-1527`) · `deleteSet` UI 배선(`DashProject.h:47` · `DashMainWindow.cpp:550-551`) |
| `getMorphingSourceInfo` 무작동 | **중** | 함수 본문 확인(`:543-604`, 2026-09-13) — `DV-Geometry`·`ConditionParameter` 섹션 읽기는 실재. Launcher JSON 에 그 섹션이 없다는 쪽은 라이터 재확인 안 함 |
| 각 모듈 {Set}.json 라이터 좌표 | **중** | 문서 4 T15 가 실측. Condition·CAD 의 `saveSettings` 는 빈 스텁·호출부 0 — 쓰기 자리는 실 라이터 3종으로 확정(해소 필요 사항 2) |
| 빌드·실행 | **없음** | 정적 근거만 |
