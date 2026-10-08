# 작업 순서와 문서 배치 — 매니페스트 도입 · 마스터

> 작업 묶음: 프로젝트 매니페스트 도입과 모듈 의존성 관리
> 관련 Issue: #239

**이 묶음의 진입 문서다.** 구조 방침과 착수 순서만 적는다 — 좌표와 근거는 각 문서가 갖는다.

프로젝트 수준 파일(기준 모델 목록 · Set 계보 · 스키마 버전)의 부재가 원인이고, 귀속 근거는 [[Cross-Module-Defect-Menifest-Axis]] — 결함 73건이 이 축이다.

## 구조 방침

`m_activeFilePath` 하나가 **렌더 대상**과 **모듈이 가리켜야 할 기준 파일** 두 역할을 겸한다. 그 겸업을 끊는 것이 이 묶음의 축이다.

| 층           | 현행                  | 분리 후                                      |
| ----------- | ------------------- | ----------------------------------------- |
| 렌더 대상       | `m_activeFilePath`  | `m_displayedFilePath` — 커서. 단수인 것이 설계다    |
| 전역 기준모델     | 같은 멤버를 겸업           | `m_referenceFilePath` — 등록된 N개 중 한 시점에 1개 |
| 등록 가능한 기준모델 | 개념 없음               | 원장(`referenceModels.json`)에 N개            |
| Set 별 기준모델  | 없음 — 진입 시점의 커서가 정한다 | 모듈 JSON({Set}.json)의 키                    |

| # | 방침 |
|---|---|
| M1 | 전역(모든 사용자 모듈)에서 기준이 될 수 있는 모델은 **N개 등록**을 허용한다 |
| M2 | 등록된 N개 중 프로젝트가 한 시점에 지정하는 **전역 활성 기준모델은 1개**이고, 렌더와 분리한다 |
| M3 | 전역 기준모델 지정은 Load 버튼 형태를 유지하고 **유일한 지정 방식**으로 쓴다 |
| M4 | Load 버튼 외의 경로(모델링 트리 체크박스 · Optimizer 프리뷰)는 **렌더 대상만** 바꾼다 |
| M5 | 전역 기준모델 핀은 파라미터화 Set 생성의 **사전요건**이다 — 미핀 상태에서는 Set 생성을 거부하고 Load 를 안내한다. **CAD variant 는 제외**(#366 · D31 유보) |

**등록 지점은 Load 핸들러 하나다.** M3·M4 가 등록 경로를 UI 동작 하나와 1:1 로 묶으므로 `getOrLoad` 는 자격을 판정하지 않는 순수 캐시 조회로 남고, 등록은 그 핸들러가 `registerReferenceModel` 을 명시적으로 부른다.

**원장 운영 정책 P1\~P5** — 근거·좌표는 [[Project-Manifest-1-Context-Registry-And-Model-Identity]] 4절이 갖는다.

| # | 정책 |
|---|---|
| P1 | 경로는 프로젝트 루트 상대경로만 — 외부 파일은 프로젝트 안으로 복사 후 등록 |
| P2 | content uuid 는 최초 1회만 발급(상대경로 v5 파생)하고 이후 원장 값을 쓴다 — 원장의 1차 키(D24). 경로와 식별자 분리가 rename 이관(후속작업 1)의 전제 |
| P3 (재개정) | 원장 대상은 `.dat`·`.inp` 한정 — **현행 유지.** RW 세션이 열리는 확장자와 일치. `kind` 확장(`.prt` 형상 출처 — D29)은 **유보**(후속작업 13 동반)이고, `.wbpj`·`.stli` 편입은 범위 밖 유지(후속작업 5) |
| P4 | 등록은 Load 버튼 핸들러 한 곳의 `registerReferenceModel` 명시 호출 — `getOrLoad` 는 자격을 판정하지 않는 순수 캐시 조회로 남는다. 원장에 `role` 분류 필드를 두지 않는 근거이기도 하다 |
| P5 | 프로젝트 열기는 등록(원장 복원)만 — 적재·해싱은 lazy 유지 |

## 결정 사항

**이 절이 결정의 세이브포인트다.** 문서 5 와 이슈는 구조 방침(M1\~M5)·원장 정책(P1\~P5)·아래 표(D1\~D34)를 참조로 끝낸다 — 문서 1\~3 으로 내려가는 것은 근거·코드 좌표가 필요할 때뿐이다.

| #         | 항목                           | 결정                                                                                                                                                                                                                           |
| --------- | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| D1        | 개명 낱말                        | **`displayed`** — `m_displayedFilePath` · `setDisplayedContext()` · `displayedContext()` · `displayedContextChanged` |
| D2 (개정)  | `m_referenceFilePath` 소유 클래스 | [작업 1]에서 **Registry**. 접근자 이름을 `referenceFilePath()` 로 고정하고 [작업 2]에서 구현만 원장 조회로 교체한다. 소유권의 프로젝트 세션 이전은 후속작업 11(PR #389 리뷰)                                                                                                  |
| D3 (개정)  | 값 표현                         | **영속 조인 키는 uuid, 경로는 프로젝트 루트 상대경로**(D24). 원장 키·모듈 JSON 조인 키·`activeModel` 이 uuid 이고, 상대경로는 원장 `path` 필드·표시·파일 접근용이다. 루트는 현행에서도 프로젝트 생성 시점에 정해진다                                                                              |
| D4        | Load 버튼의 겸업 범위               | **등록 · 전역 기준 지정 · 렌더 이동 셋을 한 번에** 하고 **멱등**이다. 이미 등록된 모델을 다시 Load 하면 등록은 no-op 이고 기준과 렌더만 이동한다                                                                                                                               |
| D5        | 등록 해제 지점                     | **두지 않는다.** 모델링 트리 삭제는 등록 해제가 아니다. 필요해지면 프로젝트 트리(Add File·Load 가 있는 곳)의 우클릭에 둔다                                                                                                                                              |
| D6        | 활성 전환 UI                     | **불요.** Load 재클릭이 유일 경로다                                                                                                                                                                                                     |
| D7        | 기준 ≠ 렌더 상태의 표시               | Mesh View 도크 제목줄에 **현재 렌더 중인 파일명**을 띄운다. 기준모델은 **Load 버튼의 활성 상태**로 표시한다                                                                                                                                                      |
| D8        | 과도기 동작                       | 구현 중간 구간은 현행과 동일하게 둔다. 완료 시점에 맞으면 된다                                                                                                                                                                                         |
| D9        | 상대경로 해석 지점                   | **Registry 안**. 컨텍스트 접근자와 세터가 `DashManager::PrjMgr()->GetIOController()->getProjectRootDir()` 로 루트를 얻어 붙인다. `m_contexts` 캐시 키는 canonical 절대경로 그대로 둔다                                                                         |
| D10       | 커서 멤버의 mutex 보호              | **후속작업.** 같은 뮤텍스로는 교착이고, 현행에 막을 경합이 없다(아래 근거)                                                                                                                                                                                |
| D11 (개정) | 모듈이 드는 값                     | **uuid 1차 + path 병기.** 모듈 JSON 에 둘 다 쓰고 uuid 로 원장을 직조회한다. path 는 표시·디버깅·원장 유실 폴백이고, 원장 항목의 path 와 다르면 원장 값으로 backfill 한다(원장 정본)                                                                                              |
| D12 (개정) | 커서의 값 표현                     | **displayed 커서는 프로젝트 루트 상대경로**(원장 미등재 파일 — 프리뷰 산출물 — 도 렌더한다), **reference 커서는 uuid**(원장 키·`activeModel` 과 동일, [작업 2] 구현 교체 시 전환 — 그 전까지 상대경로). 두 층 모두 상대·절대 경로 접근자를 노출하고 표현은 Registry 안의 구현 세부로 남는다                            |
| D13       | Set deck 을 모델에 채우는 지점        | **생성·복원 시점.** 신규 Set 은 생성 핸들러가 전역 reference 를 핀, 기존 Set 은 `loadFromJson`. 위젯 `setModel` 은 모델 값만 읽는다                                                                                                                          |
| D14 (개정) | 모듈 JSON 스키마                  | **`referenceModel` 객체 하나**에 `uuid`(조인 키)·`path`(표시·폴백 — D24). 스키마 버전은 올리지 않고 키 부재를 구버전 판정으로 쓴다                                                                                                                              |
| D15 (재개정)  | 구프로젝트 마이그레이션                 | **Lazy backfill — 핀 출처는 Set 자신의 DV `source`.** 키 없으면 진입 1회 자기 DV `source` 에서 유도해 핀 + 다음 저장 backfill — Condition 은 상대경로 그대로, Morphing 은 bare filename 을 configs 복사본 → 원장 `path` → 루트 스캔 순으로 해석(복수 히트는 정렬 후 첫번째 + 로그). 유도 실패 시에만 전역 폴백, 빈 값이면 핀 안 함. 소급 없음 — 기존 핀 불문. **multi-source json 은 진입 시 1회 자동 분할**(deck 별 Set) + `.bak` 보존 + 결과 통지. 라이터는 Condition·Morphing 2종(문서 3 D15 절) — CAD 는 키 미도입(D31 유보)                                                                                                                 |
| D16 (3차 개정) | 해석 실패 참조                     | **uuid 직조회 → 미스면 v5(path) 재파생 조회 1회 → 실패·파일 부재 시 미지정 + 로그.** path 원장 스캔·uuid backfill 은 제거 — uuid ≡ v5(상대경로)인 동안 발화 조건 없는 분기다. D11 의 "두 값 갈림 → 원장 정본 backfill" 은 후속작업 4(sha256 이관) 전까지 유보. rename 회복도 후속작업 4 전까지 없다                                  |
| D17       | Set deck 변경 UI               | **불요 확정.** 생성 시점 고정. Parameters 도크 제목줄에 현재 Set 의 deck 파일명 표시 — 앞단 4모듈(Condition·CAD·Morphing·Launcher) 한정. Launcher 는 `{형상 deck 파일명} +{조건 Set 수}`, 단일 deck 이면 접미 생략(근거는 문서 3 D17 절). CAD 는 기본 "Parameters"(#366 봉합 · D31 유보)                                                                         |
| D18 (재개정) | 소유자 집합                       | **파이프라인 8모듈 — Condition·Morphing(생성 시점 핀) · CAD(키 미도입 — #366 · D31 유보) · Launcher(`referenceModel` 대신 `parameterization` — DOE 선택 시 조합 기록) + Preprocessor·Builder·Runner·Optimizer(최초 연결 시점 핀).** Analyzer·AIGeo 만 제외. ModelRunner 의 NodeSet 소스는 별도 키. 근거는 [[Project-Manifest-3-Module-Deck-Ownership]] "소유자" 절  |
| D19 (개정)  | 파이프라인 불변식 보장                 | **산출물 스탬프 + Set 핀 + 홉별 검증.** 불변식은 단일 deck 이 아니라 **DOE 조합**(Geometry Set 1 + Condition Set N — D23)의 동일성이다. 산출물 스탬프의 형태는 D26 이 정한다(조합 id + 형상 deck). 상세는 문서 3 "파이프라인 스탬프" 절 |
| D20 (재개정)  | 스탬프·핀 불일치 시                  | **차단.** 판정 기준은 deck 단일성이 아니라 **DOE 조합 일치**(D23)다 — 서로 다른 deck 의 입력이라도 같은 조합이면 정상이다. 불일치 시 거부하고 "다른 조합이면 새 Set" 안내 — D17 동형. **구버전 폴백 불도입 — 무스탬프 산출물은 연결 차단** + "스탬프 없는 구산출물 — 재실행 필요" 안내(차단 문형 동형). 라이브 체인은 part 명 조회 용도만 잔존. 핀은 id 를 든 첫 입력에서 걸린다                                                              |
| D21 (재개정)  | Launcher 만 예외                | **기록만, 검증 없음.** 핀 대상이 단일 deck 에서 DOE 조합(D23)으로 바뀐다. DV 는 기준 deck 에서 생성하고 형상·조건 동일 변종 deck 을 해석하는 워크플로우 수용은 유지. 부속(실행 템플릿 deck 기록)은 **철회**(2026-09-22 — PR #530 리뷰) — 원문·사유는 [[Project-Manifest-Set-Identity-And-Decision-Revisions]]                                                                                                                |
| D22 (개정)  | 전역 활성 기준모델의 영속               | **원장 최상위 `activeModel` 키 — 값은 uuid**(D24). 등록 N개 중 활성 1개(M2)의 영속 자리 — Load 핸들러 경유 `setReferenceModel` 이 갱신하고(D4) [작업 2] 열기 복원이 읽는다. 복원 시 Load 버튼 활성 표시(D7)도 동기화한다. 스키마 정본은 문서 1 "스키마" 절                                           |
| D23 (개정) | Set : 기준모델 카디널리티             | **Condition·Geometry(CAD·Morphing) Set : referenceModel = 1:1 확정. 다해석 워크플로우는 DOE 가 Geometry Set 1 + Condition Set N 을 참조**하는 것으로 담는다(PR #389 A안). Builder·Optimizer 1 = DOE 1. Condition DV 표에 여러 deck 을 쌓던 현행(`source` 구분)은 폐기 — batch run 병합 규칙 등 상세는 문서 3 |
| D24       | 영속 조인 키                      | **uuid 를 1차 키로.** 원장 키·모듈 JSON `referenceModel` 조인·`activeModel`·reference 커서·파이프라인 스탬프가 uuid 로 통일된다. 발급은 등록 시 상대경로 v5 파생 1회(P2). displayed 커서와 `m_contexts` 캐시 키는 제외(각각 D12 · "캐시 키" 절) |
| D25 (개정) | 조합의 표현                       | **형상 1 + 조건 맵** — `geometry` 객체 하나 + Condition Set 키의 `conditions` 맵. 평평한 튜플(배열 위치 조인)과 deck 당 3요소 묶음(형상 N번 중복) 둘 다 배제한다 — **모든 기준 deck 의 형상은 같고 해석조건만 다르다**는 전제가 확정돼 중복의 근거가 사라졌다. 소유·소비는 문서 3 "조합의 표현" |
| D26 (산식 확정) | 조합 스탬프의 배치                   | **산출물에는 조합 id + 형상 deck 둘만** — `parameterizationId`(검증용) · `geometryDeck`{uuid, path}(morph 원본). 자리는 dataset XML `model_info` 섹션 안 + `model_info.json` 최상위, 홉별 검증은 id 문자열 비교(근거 문서 3). 조합 정의는 Launcher `{Set}.json` 소유, DV 키 매핑의 산출물 동봉은 범위 밖(후속). id 파생 산식은 **SI-5 로 확정** — `{geometry setId}+{condition setId 정렬 연접 ","}`, 해시 없음·멱등·**id 파싱 금지**(조인은 병기 필드), 계산·저장은 DOE 실행 시점의 `DOE Table` |
| D27 (재개정) | DOE 다중 선택과 DV 이름              | **체크 가능 콤보 · DV 이름 항상 `{Set 이름}.{DV 이름}` 접두 · 내부 참조는 `{set: setId + name 병기, key: bare 이름}` 복합(SI-4 — 불일치 시 Set json 정본) · deck 치환은 그 run 의 deck 을 공유하는 Set 들의 DV 만 bare key 로.** 공유 deck 안의 bare 이름 겹침은 선택 시 차단. DV 전용 id 는 두지 않는다. 구 DOE Table(`{set: 이름}`)은 기록된 대로 해석 — 이름 폴백, 재기록 없음. 접두 필연성 근거와 동반 수정 3건(G8 — T25·T26)은 문서 3·4 소유 |
| D28 (폐기) | 읽기 전용 행 표시                    | **폐기 — multi-source 자동 분할(D15 재개정) 후 핀 deck 밖 행이 성립하지 않는다.** 함께 걷는 것: `DashDesignVariableModel` 의 회색·잠금·툴팁 처리, `loadFromJsons` 의 핀 deck 인자, `FECondition` 예외 판정, DOE 의 구 multi-source 읽기 경로 |
| D29\~D31 (유보) | CAD 형상 출처 | **유보 — 이 묶음의 CAD 처분은 #366 봉합(M5 제외·죽은 전역 읽기 제거)까지이고, 원장은 `deck` 전용(P3 현행)을 유지한다.** 방향 세이브(원장 `kind` · Load 핸들러 `.prt` 분기 · CAD Set 의 `cadSource`)와 근거는 [[Project-Manifest-CAD-Path-Disposition]] — 착수는 후속작업 13 |
| D32·D33 (철회) | wbpj 경로 결부 결정 | **철회 — 근거가 사장 판정된 wbpj 경로에 있었다.** DV `source` 의 `CAD\|<part>` 교체(D32)와 조합·스탬프의 형상 kind 일반화(D33)를 거둔다 — D25·D26 원안(deck 단일) 유지 · `CAD\|` 소비 불개입. 근거는 [[Project-Manifest-CAD-Path-Disposition]] |
| D34 (신설) | setId — Set 의 안정 식별자 | **12자리 랜덤 hex(v4 절단) + 각 `{Module}_{Set}.json` 의 `setId` 키 정본(별도 Set 원장 없음) + 생성 핸들러·열기 복원 시 발급 + 영속 조인은 setId·`name` 병기 + 조합 id 는 정렬 setId 연접 + 산출물 폴더명은 `{Module}_{Set}` 유지 — 소비자가 setId 를 들고 색인 역조회(SI-6a · 후속작업 14).** 원문 SI-1\~SI-6a 는 [[Project-Manifest-Set-Identity-And-Decision-Revisions]] |

D13\~D21 · D23 · D25\~D28 의 근거는 [[Project-Manifest-3-Module-Deck-Ownership]], D22 의 스키마는 [[Project-Manifest-1-Context-Registry-And-Model-Identity]], G5 이후 티켓 재스펙은 [[Project-Manifest-4-Ticket-Slicing]] 소유다.

표 안 D5·D9\~D12·D24 의 근거는 아래 "결정 근거" 절이, D29\~D33(CAD 경로)의 원문·근거는 [[Project-Manifest-CAD-Path-Disposition]] 이 갖는다. **2026-09-21 개정분 — D15 재개정·D16 3차 개정·D20 재개정·D21 부속·D26 산식 확정·D27 재개정·D28 폐기·D34(setId) — 의 원문·사유는 [[Project-Manifest-Set-Identity-And-Decision-Revisions]] 가 갖는다.** G7(#472)·#491 이 dev 반영 뒤라 기반영분의 개정은 구현 후속 정정 티켓으로 처리한다 — 같은 문서 "반영 대상" 절.

## 문서 4종

| #   | 문서                                                         | 성격      | 갖는 것                                                                         | 대응 작업              |
| --- | ---------------------------------------------------------- | ------- | ---------------------------------------------------------------------------- | ------------------ |
| 1   | [[Project-Manifest-1-Context-Registry-And-Model-Identity]] | 조사 · 구상 | 레지스트리 소비자 전수 · 원장 스키마 · content uuid 정책                                      | [작업 2]             |
| 2   | [[Project-Manifest-2-Active-Cursor-Data-Coupling]]         | 조사      | 모듈이 커서를 데이터 소스로 읽는 결합 9좌표 · 유지 12건 + 시그널 2건                                  | [작업 1] · [작업 3] 일부 |
| 3   | [[Project-Manifest-3-Module-Deck-Ownership]]               | 설계      | D13\~D21·D23·D25\~D28 근거 · 소유자 8모듈(전수 조사·파이프라인 스탬프) · `referenceModel`·조합 스키마 · [작업 3] 항목 8개 | [작업 3]             |
| 4   | [[Project-Manifest-4-Ticket-Slicing]]                      | 착수 계획   | [작업 1]\~[작업 3]을 PR 10개(G1\~G10 — 티켓 T1\~T27, T6 결번)로 분할                | [작업 1]\~[작업 3]     |

**번호는 배치 순서이고 착수 순서가 아니다.** 착수는 문서 2 → 문서 1 → 문서 3 순이고, 문서 4 가 그것을 PR·커밋으로 자른다. 네 문서 모두 작성 완료 — 남은 것은 PR 실행이다. 표 밖의 [[Project-Manifest-5-Scope-and-Follow-up]](완료 범위·후속 정리) · [[Project-Manifest-Todo-List]](진행 관리)는 정본이 아니다.

## 순서

```
[작업 1] 전역 기준모델 커서와 렌더 커서 분리 — 완료 (#389)
   │   1. Registry 멤버·API 분화
   │      m_displayedFilePath·m_displayedActor / m_referenceFilePath
   │      setDisplayedContext() / setReferenceModel() · 시그널 2 종 분화
   │      두 층 다 상대경로 저장 + 상대·절대 접근자 쌍 (D12)
   │   2. 쓰기 4 곳 배정 — Load(MainWindow:2267) 만 setReferenceModel,
   │      체크박스 :2437·:2464 와 프리뷰 OptimizerWidget:1558 은 setDisplayedContext
   │   3. 읽기 라우팅 — 문서 2 의 좌표표대로 데이터 결합 9 좌표는 reference,
   │      렌더 12 건 + 시그널 2 건은 displayed
   │   4. 부속 — get→getOrLoad 2 좌표 · nullptr 역참조 2 곳
   │   5. 표시 — Mesh View 도크 제목줄에 현재 렌더 파일명 (D7)
   │   6. 죽은 코드 제거 — 문서 2 "죽은 코드" 표의 include 3 · 함수 4 ·
   │      오버로드 1 · 인자 1. 같은 파일을 건드리는 유일한 기회다
   │   ※ 개명이 이 작업에 흡수된다 — 별도 단계로 남지 않는다
   ▼

[작업 2] 원장 도입
   │   1. 원장 클래스 + referenceModels.json — DashProject 하위 또는 같은 레벨
   │   2. referenceFilePath() 구현을 원장 조회로 교체 · 프로젝트 열기 시 복원
   │   3. Registry::clear + CloseProject 연결 · 활성 기준모델로 Modeling Tree 재파싱
   │      죽은 스캐너 loadSetsFromConfigs(DashProject.cpp:1066) 삭제
   │   4. 원장 키를 uuid 로(D24) — 경로는 path 필드로 통일 + content uuid 영속
   │   5. DashRwSession::open 시그니처 변경 · AnalysisModelIdentity.json 폐기
   │   ※ 5 는 4 를 전제로 하되 1~4 와 같은 커밋일 필요가 없다
   ▼

[작업 3] 모듈 Set 별 기준모델 키
   │   1. Morphing 모델에 기준 deck 자리 신설(C-1) + DashMorphingSettings
   │      주입(C-2) + 죽은 멤버 m_fileName 삭제 + referenceModelChanged 구독 제거
   │   2. 3 모듈에 referenceModel 멤버 + {Set}.json 영속화 + 생성·복원 주입
   │      + 구버전 backfill (D13 · D14 · D15)
   │   3. 진입 1 회 읽기의 출처를 전역 reference 에서 Set 키로 — 좌표 1·9.
   │      좌표 2(CAD)는 죽은 전역 읽기 제거로 끝(#366 봉합 · D31) —
   │      전역 읽기는 신규 생성 시점과 backfill 에만 남는다 (D13 · D16)
   │   4. Reference File 콤보를 원장 조회로 · DV source 를 상대경로로
   │      · getMorphingSourceInfo 를 소유자 조회로 교체
   │   5. ModelRunner NodeSet 소스 소유 — 다이얼로그 선택 영속화(별도 키) + 빈 값 폴백 (D18)
   │   6. Parameters 도크 제목줄에 현재 Set 의 deck 파일명 표시 — 앞단 4모듈 (D17)
   │   7. 파이프라인 스탬프·핀·검증 (조합 id 단위 — D26) — Launcher 조합 기록 →
   │      조합 id 발급 → Preprocessor·Builder 검증·핀·전사 → Runner·Optimizer
   │      스탬프 1차 핀 + 일치 검증 (D19~D21)
   │   8. DOE 샘플링의 Condition Set 다중 선택 — 체크 콤보 + DV 합산 +
   │      Set 접두 이름 + deck 별 batch run 루프 — 공유 deck 은 한 run (D23·D27)
   │   ※ CAD 는 이 묶음 범위 밖 — #366 봉합까지만. D29~D31 유보 (후속작업 13) ·
   │      D32·D33 철회 · 사장 경로 (wbpj DOE · CAD| 소비) 불개입 — CAD-Path-Disposition 문서
   ▼

[완료 상태] 커서가 순수 렌더 커서로 남는다
       전역 기준모델은 원장의 한 항목을 가리키고, Set 은 각자의 키를 갖는다
```

**블록 안 항목 번호는 구성 요소 열거이고 실행 순서가 아니다** — PR·커밋 순서는 문서 4 소유. 특히 렌더 커서의 상대경로 전환([작업 1]-1 의 D12)은 소비자 이동([작업 1]-2·3) 뒤에 온다(문서 4 — G1 뒤 G2). CAD 분(D29\~D31)은 유보라 이 묶음에 PR 이 없다 — 착수는 후속작업 13 이다.

| 관계 | 성립 | 근거 |
|---|---|---|
| [작업 1] 단독 성립 | 예 | 원장 없이 선다. 접근자 이름을 `referenceFilePath()` 로 고정하면 [작업 2]가 **구현만** 갈아끼우고 호출부는 불변이다 |
| [작업 1] → [작업 2] | 예 | 커서가 갈려야 등록 지점이 Load 핸들러 하나로 좁혀진다. 분리 전에는 렌더 커서 이동이 등록을 유발한다 |
| [작업 2] → [작업 3] | 예 | 원장이 있어야 Set 이 가리킬 대상이 생긴다 |
| [작업 1] → [작업 3] | 예 | Morphing 5좌표가 reference 로 옮겨져 있어야 Set 별로 내려갈 자리가 생긴다 |
| [작업 2]-5 | 단계 4 에만 의존 | uuid 영속이 전제이고, 그 뒤로는 시점이 자유롭다 |

**Morphing 모델 자리 신설은 [작업 3]이다**(문서 2 의 C-1·C-2). [작업 1]에서는 Morphing 5좌표가 전역 `referenceContext()` 를 읽는 것으로 충분하고, Set 별 소유는 [작업 3]에서 Condition·Morphing 2모듈이 같은 형태로 내려가고, CAD 는 이 묶음 범위 밖이다(D29\~D31 유보 — 후속작업 13). 이렇게 두면 [작업 1]이 "커서 분리 + 라우팅" 한 가지만 한다.

**Reference File 콤보와 DV `source` 정규화도 [작업 3]이다.** 모듈이 가리키는 값을 바꾸는 일이라 Set 키 도입과 같은 자리다.

**`buildDvGeometry` 안의 두 좌표가 같은 방향을 본다.** `DashGeometryParameterPresentationModel.cpp:46` 이 경로를 정하고 `:107` 이 그것을 DV `source` 로 쓴다 — 현행은 bare filename 이고 [작업 3]-4 가 이 자리를 상대경로로 정규화한다. [작업 1]이 `:46` 을 reference 로 먼저 옮겨야 그 정규화가 옳은 경로를 대상으로 삼는다.

## 과도기 동작 변화 3건

D8 대로 구현 중간 구간은 현행과 같게 둔다.

| | 내용 |
|---|---|
| 1 | `MainWindow:438`(문서 2 의 좌표 8)을 떼면 "Set 을 먼저 클릭하고 나중에 Load" 순서에서 복구 경로가 없어져 Set 재클릭이 필요하다. [작업 1]\~[작업 2] 구간에만 남고 [작업 3]이 닫는다 |
| 2 | [작업 2] 전까지 전역 기준모델이 영속화되지 않아 프로젝트를 다시 열면 0개 상태로 선다. 현행 커서와 같으므로 그대로 둔다 — 진입 1회 읽기가 빈 값이면 핀을 걸지 않는다(`ConditionWidget:314` 가드) |
| 3 | PR #389 리뷰 회귀의 복원 — `referenceModelChanged` → Condition `refreshFromFile(referenceAbsolutePath())` 연결로 "Load 마다 표 갱신(쌓기)" 을 되살린다(명시적 Load 에만 발화 — 체크박스 오염 수정 유지). D23 종착과 반대 방향인 의도된 과도기다 — G7(T16)이 연결을 제거하고 대체 워크플로우(DOE 다중 선택 — T24, G8)가 **같은 dev 반영 회차**여야 하며, G5\~G10 의 1회 반영으로 충족(문서 4) |

## 후속작업

이 묶음 밖으로 미룬 것이다.

| # | 항목 | 좌표·소유 |
|---|---|---|
| 1 | Registry 의 스레드 안전 — 커서 멤버 보호(D10)와 `m_contexts` double-load 경합을 한 자리에서 | `Registry.cpp:24-47`·`:50-75` |
| 2 | 캐시 무효화 경로 부재 — `m_contexts` 에 `erase` 가 없어 같은 경로를 덮어써도 낡은 컨텍스트를 쓴다 | 문서 1 의 1절 |
| 3 | 프리뷰 산출물 누적 — 순회 중 `.vtu` 만 지우고 `.dat`·`.inp` 는 Optimizer 디렉터리에 남는다 | `OptimizerWidget:1505-1513` |
| 4 | 지문 불일치 처리 · 앱 밖 rename 이관 | 문서 1 9절 후속작업 1 |
| 5 | 형태 확장 — `.stli` · `.wbpj`. `.prt` 분은 **후속작업 13 동반**(D29\~D31 유보 — 원장 kind + `cadSource`) | 문서 1 9절 후속작업 2 |
| 6 | 정본 일원화 — configs 복사본 제거. 리더만 있는 `{root}/configs` 정리도 여기서 | 문서 1 9절 후속작업 3 |
| 7 | `onActiveContextChanged` 의 판정 분열 — `:477` 은 이름으로(`findItems`), `:485` 은 경로로 판정한다. 이름이 같고 경로가 다른 항목이 트리에 있으면 파일이 추가되지 않는다. 발현 조건이 좁다(프리뷰 산출물명이 타임스탬프로 유일) | `DashModelingTreeWidget.cpp:472-489` |
| 8 | `SaveProjectAs` 부분 복사 — 복사 원본이 `GetProjectPath()` = 숨김 `.dproj` 폴더라 루트 레벨 영속 파일(deck·모듈 산출물)이 새 프로젝트에 복제되지 않는다. 루트 내 영속 파일 전수를 복제해야 한다 | `DashProjectManager.cpp:169-210` · `:244-253` |
| 9 | ~~Optimizer 프리뷰 전수 스캔·전량 morph~~ **편입 — [작업 3] 항목 7(D19)이 흡수했다.** Optimizer 가 model_info 의 `geometryDeck` 1건만 morph 한다(조합 id 핀 — D26 · 문서 4 T23) | `DashOptimizerWidget.cpp:1468-1493` |
| 10 | 모듈 JSON 의 deck 참조 전면 상대경로 통일 — 영속 형식 4개 중 [작업 3]-4 가 둘(DV `source` bare filename · `input_files` 의 deck 분)을 처리하고, `CAD\|` 형식 분은 **사장 경로 소속이라 제외한다**(D32 철회 — 불개입). `input_files` 비-deck 분(`.wbpj`·`.stli`)만 잔여 — 후속작업 5 이후 | 문서 1 9절 후속작업 4 |
| 11 | Registry state 소유권 이전(PR #389 리뷰 — DCode) — `displayed*`+`m_displayedActor` 는 `DashRenderingManager` 로(모델 캐시가 렌더러를 미는 레이어 역전 해소 — 액터 생성·교체는 `displayedContextChanged` 구독으로), `reference*` 는 프로젝트 세션으로(기준모델과 시그널만 담는 작은 QObject 를 `DashProjectManager` 가 `m_ioController` 패턴으로 소유, `CloseProject` 에서 clear). 이전이 오면 T11 의 `Registry::clear` 는 자연 소멸하고 #364 계열이 발생 불가가 된다. #364 자체는 계획대로 T11 로 먼저 닫는다 | `DashAnalysisModelContextRegistry` · `DashProjectManager` |
| 13 | **CAD 경로의 일반화 — 기준 deck 으로의 수렴.** CAD 생성 형상을 GUI 안에서 meshing(`DashMeshingDialog` 방향)하고 파트·NSET 을 매칭해 `.inp`/`.dat` 을 생성, 그 deck 을 기준 deck 으로 등록해 정규 경로에 합류시킨다. 생성 deck 의 등록 지점과 P4(Load 단일 규약)의 관계 · 재메싱으로 무효화되는 NSET 의 재부착이 이 설계의 소관이고, **유보한 D29\~D31(원장 kind · `.prt` 등록 · `cadSource`)이 여기 동반한다** | 코드맵 CAD 3-6 절 · [[Project-Manifest-CAD-Path-Disposition]] |
| 14 | **산출물 폴더 식별(SI-6a)** — 폴더명 `{Module}_{Set}` 유지, 변환 없음. 소비자는 setId 보유 + `DashProject::m_setIds` 역조회로 현행 `getModuleDir` 조립. 성립 조건 셋 — `renameSet` 의 산출물 폴더 동반 개명 · Set 참조 보관 자리의 setId 전환(Runner `modelBuilderFolder` · Optimizer 폴더 콤보 · 폴더명 역파싱 3곳) · 삭제 시 폴더 동반 삭제 + 생성 시 동명 폴더 거부. 선행 G9(#530) 머지. 규모 실측은 SI-6a | [[Project-Manifest-Set-Identity-And-Decision-Revisions]] |

## 결정 근거

### D5 의 근거

해제가 필요한 자리가 아직 없다는 것이 1차 근거이고, 코드가 뒷받침하는 것은 **트리 삭제의 성격**이다. `deleteSelectedItem`(`DashModelingTreeWidget.cpp:506-528`)은 트리 행을 지우고 `itemDeleteRequested` 를 쏘며, 핸들러(`DashMainWindow.cpp:411-428`)는 렌더 레이어를 clear 한다 — **화면에서 치우는 동작**이지 프로젝트 정의를 바꾸는 동작이 아니다.

**두 집합이 서로를 포함하지 않는다는 것이 2차 근거다.** 한쪽 삭제를 다른 쪽 해제로 쓰면 대상이 어긋난다.

| 한쪽에만 있는 것 | 사례 |
|---|---|
| 트리에만 | `.vtk`·`.vtu`(`vtk_parent`) · STEP·`.prt`(`cad_prt_parent`) · 프리뷰 산출물. 원장 대상은 Load 된 `.dat`·`.inp` 뿐이다(P3) |
| 원장에만 | 트리에서 지운 뒤 — `deleteSelectedItem` 이 원장을 건드리지 않는다 |

노드 종류는 `addFileToTreeWithStructure` 가 확장자로 가른다(`DashModelingTreeWidget.cpp:239-241`).

### D9 의 근거와 요건

D3 이 값 표현을 상대경로로 정했는데, 레지스트리의 두 조회 함수는 인자를 절대경로로 가정한다 — `get`(`Registry.cpp:16-21`)·`getOrLoad`(`:23-48`)가 `QFileInfo(filePath).canonicalFilePath()` 를 캐시 키로 쓴다. 상대경로를 그대로 넘기면 프로세스 CWD 기준으로 풀려 어긋나므로, 루트를 붙이는 자리가 필요하다.

**주입은 불필요하다.** 루트가 정적으로 닿는다.

```
DashManager::PrjMgr()          controller/DashManager.h:93          static
└─ GetIOController()           DashProjectManager.cpp:316-319
   └─ getProjectRootDir()      DashIOController.h:91                m_projectRootDir
```

`m_projectRootDir` 은 `SetProjectDirectory` 가 `.dproj` 의 상위 폴더로 계산한다(`DashProjectManager.cpp:55-57`). `.dproj` 가 루트 아래에 있으므로 숨김 폴더 안의 deck 도 `".Car.dproj/configs/wing.dat"` 로 한 규약에 들어온다.

**요건 2건.**

| | |
|---|---|
| nullptr 가드 | 프로젝트가 없으면 `m_ioController` 가 nullptr 이다(`DashProjectManager.cpp:26` 초기값, `CloseProject:217-219`). 그때는 기준모델도 없으므로 `referenceContext()` 가 nullptr 을 주는 것이 옳은 동작이다 |
| 루트 교체 | `SetProjectDirectory` 가 IOController 를 매번 새로 만든다(`:60-63`). 호출부 3곳 중 둘(`OpenProjectFromFolder:118` · `CreateNewProject:158`)은 `CloseProject` 를 거치므로 [작업 2]-3 의 `Registry::clear` 가 닫는다. **`SaveProjectAs:207` 은 안 거친다** — 그 경로는 아래 캐시 키 규약이 감당한다 |

`getUserPath()`(`DashIOController.h:97`)가 같은 멤버를 돌려주나, 뜻이 드러나는 `getProjectRootDir()` 을 쓴다.

### 캐시 키를 절대경로로 남기는 이유

`m_contexts` 는 D3·D12 의 상대경로 규약에서 **제외한다**. 역할이 다르다.

| 대상 | 역할 | 표현 |
|---|---|---|
| reference 커서 · 원장 키 · 모듈 조인 | 영속·세션 간 식별자 — 프로젝트 이동·rename 에도 같은 것을 가리켜야 한다 | uuid — 경로는 원장 `path` 필드(D24) |
| displayed 커서 | 세션 내 렌더 대상 — 원장 미등재 파일 포함 | 프로젝트 루트 상대 |
| `m_contexts` 키 | 프로세스 내 파일 객체 dedup — 디스크의 그 파일 자체를 가리켜야 한다 | canonical 절대 |

**`SaveProjectAs` 가 결정적이다.** 숨김 `.dproj` 폴더를 복사해 루트만 바꾸고 `CloseProject` 를 안 거치므로(`DashProjectManager.cpp:169-207`, 복사 원본 = `GetProjectPath()` = 숨김 폴더 `:244-253`), 옛 프로젝트의 `.dproj` 내부 상대경로가 새 프로젝트에 똑같이 존재하는 상태에서 캐시가 살아 있다. 루트 레벨 영속 파일이 복사되지 않는 것은 현행 결함이다 — 후속작업 8.

| 캐시 키 | SaveProjectAs 직후 |
|---|---|
| 상대경로 | 새 프로젝트의 `.Car.dproj/configs/wing.dat` 조회가 **옛 컨텍스트에 히트**한다. 충돌이 보장된다 |
| canonical 절대 | 옛 항목이 새 조회와 안 맞아 미스 → 새로 로드. 남는 것은 옛 항목 누수뿐이고 그것은 이미 알려진 "캐시 무효화 경로 부재" 결함이다 |

**영속 참조가 상대경로(원장 `path` 경유)로 풀리고 캐시가 절대인 조합이라서 `SaveProjectAs` 가 자동으로 맞는다** — reference 커서의 uuid 가 복사되어 온 원장에서 `.Car.dproj/configs/wing.dat` 로 풀려 새 루트로 해석되고, 캐시는 미스가 나 그 새 파일을 읽는다. `referenceModels.json` 도 숨김 폴더 복사에 따라간다. 루트 레벨 deck 은 후속작업 8 이 복사를 고쳐야 같은 논리에 들어온다.

덤으로 `canonicalFilePath()` 는 심볼릭 링크를 푼다. 상대경로 키라면 같은 파일을 가리키는 다른 표기가 두 번 캐시된다.

### D10 의 근거

**같은 뮤텍스로는 교착이다.** `activeContext()` 가 `get(m_activeFilePath)` 인데(`Registry.cpp:65-67`) `get()` 이 이미 `m_mutex` 를 잡는다(`:17`). `std::mutex` 는 재귀가 아니므로 커서 멤버를 같은 락으로 감싸면 자기 잠금이 된다. `setActiveContext` 도 `getOrLoad`(잠금) → `m_activeFilePath` 대입 순서라 같은 함정이 있다. 별도 뮤텍스나 잠금 순서 규약이 필요하고, 커서가 셋으로 늘면 그 규약이 더 커진다.

**현행에 막을 경합이 없다.** 커서 접근자 21건이 전부 view·viewmodel 계층이고, 캐시 미스 경로가 `DashRwSession::open` 의 `DASH_ASSERT_MAIN_THREAD`(`:1154`)로 GUI 스레드를 강제한다. 워커 스레드가 커서를 건드리면 그 단정에서 먼저 걸린다.

같은 파일의 `m_contexts` double-load 경합(`.cpp:24-47`)이 더 실질적이고, 둘을 한 자리에서 함께 봐야 제대로 된 처분이 나온다.

### D11 · D24 의 근거와 대가

rename 내성과 이관 반경이 이유다. path 를 1차 키로 들면 앱 밖 rename 에 원장 항목과 모듈 참조가 **함께** 끊기고, 후속작업 4(sha256 추적 이관)가 원장과 모듈 JSON 양쪽을 고쳐야 한다. uuid 를 1차 키로 들면 이관이 **원장 `path` 필드 1개 갱신**으로 좁혀지고 모듈 JSON 은 불변이다.

기존 코드에 같은 패턴이 있다 — DV-Condition 로더가 어긋난 uuid 를 이름으로 대신 붙이고(`DashConditionParameterization.cpp:495-497`) 다음 저장 때 backfill 한다(`:444-447`).

| 대가 | 내용 |
|---|---|
| path 방향 조회가 생긴다 | Load 등록의 멱등 판정과 원장 유실 폴백에 한해 path → 항목 스캔이 생긴다. 원장이 프로젝트당 한 자리수라 선형 스캔으로 족하다 |
| 두 값이 갈릴 수 있다 | uuid 로 찾힌 원장 항목의 `path` 가 모듈 저장값과 다르면 원장 값으로 backfill 한다 — 원장이 정본이다 |
| 사람이 못 읽는 키 | 원장·모듈 JSON 을 손으로 열면 uuid 만으로는 대상을 알 수 없다 — `path` 병기가 그 보완이다 |

모듈 JSON 의 스키마는 D14 가 확정했다 — `referenceModel` 객체 하나에 `uuid`(조인 키)·`path`(표시·폴백). 근거는 [[Project-Manifest-3-Module-Deck-Ownership]].

### D12 의 근거와 성립 조건

```
저장   m_displayedFilePath                         프로젝트 루트 상대
       reference 커서                              uuid — 원장 키와 동일 ([작업 2] 전환 전까지 상대경로)
노출   displayedFilePath()   / referenceFilePath()        상대
       displayedAbsolutePath() / referenceAbsolutePath()  절대
비교   isDisplaying(path)                                 인자 표현 무관
```

**층마다 저장 규약이 하나여야 한다.** displayed 는 원장 미등재 파일(프리뷰 산출물)도 렌더하므로 uuid 키가 성립하지 않아 상대경로로 남고, reference 는 원장 키와 같은 uuid 다(D24). 두 표현 모두 Registry 안의 구현 세부이고 호출자는 경로 접근자만 본다 — D9 가 해석 헬퍼를 이미 만들므로 절대 접근자는 그것의 재사용 한 줄이다.

**렌더 커서 경로의 외부 소비자는 5곳이고, 분리 후 남는 것은 비교 2곳이다.** `DashConditionParameterizationWidget.cpp:313`(좌표 1) · `DashGeometryParameterCADWidget.cpp:345`(좌표 2) · `DashGeometryParameterPresentationModel.cpp:46`(좌표 4)은 기준모델 층으로 떠나고, `DashMainWindow.cpp:2436`·`:2463`(비교)만 남는다. 비교 둘을 `isDisplaying()` 으로 감싸면 호출자가 표현을 아예 안 본다.

**성립 조건** — 커서에 꽂히는 경로가 전부 프로젝트 루트 내부여야 한다. 쓰기 4곳을 실측했다.

| 쓰기 | 경로 출처 |
|---|---|
| `MainWindow:2267` Load | 프로젝트 트리(`QFileSystemModel`, 루트 = 프로젝트 폴더) |
| `MainWindow:2437`·`:2464` 체크박스 | 트리 아이템 — Load 로 들어온 경로 |
| `OptimizerWidget:1558` 프리뷰 | `QDir(optimizerDir).filePath(...)`, `optimizerDir` = `{ProjectRootDir}/{Module}_{Set}/` |

**딸린 이득 1건.** 현행은 `m_activeFilePath` 가 `canonicalFilePath()` 인데 트리 `UserRole` 은 `setData(filePath, ...)`(`DashModelingTreeWidget.cpp:248`)로 raw 를 넣는다. 같은 값이 흘러 들어가 우연히 맞고 있을 뿐이고, `isDisplaying` 이 양쪽을 정규화하면 그 우연에 안 기댄다.

**대가** — 루트 밖 경로가 들어오면 `../` 로 표현된다. 현행에 그 사례가 없다는 것은 정적 확인이다.

## 원장과 모델링 트리 — 레벨이 다르다

**모델링 트리는 저장되지 않는다.** `loadDatFileAndChildren`(`DashModelingTreeWidget.cpp:354-367`)이 `context->getPartNames()` 로 deck 을 파싱해 그 자리에서 만든다. 색(`Qt::DecorationRole`) · 체크(`Qt::UserRole`) · 투명도(`Qt::UserRole+11`)도 트리 아이템에만 살고 영속화하는 코드가 없다. 재오픈 시 트리가 비는 것은 저장본이 없어서가 아니라 **파싱을 다시 하지 않기 때문**이다.

따라서 [작업 2]-3 은 복원이 아니라 **활성 기준모델 재파싱**이다. 원장 전량이 아닌 것은 D5 로 해제 지점이 없어 원장이 단조 증가하기 때문이다.

| | 원장 | 모델링 트리 |
|---|---|---|
| 단위 | 기준모델 N개 | 각 기준모델을 파싱한 part·component 구조 |
| 담는 것 | `.dat`·`.inp` | `dat_parent` + `vtk_parent`(결과) + `cad_prt_parent`(CAD) 3종 |
| 영속 | `referenceModels.json` | 없음 — 런타임 전용 |

**두 집합은 교차하되 어느 쪽도 상대를 포함하지 않는다** — 트리에는 원장 대상이 아닌 노드 종류가 있고, 원장에는 트리에서 지워진 항목이 남는다. 트리 삭제를 등록 해제로 쓸 수 없는 이유다(D5).

## 검증 한계

| 항목 | 근거 강도 | 비고 |
|---|---|---|
| 구조 방침 M1\~M5 · 결정 D1\~D34 | — | 결정이다. 실측이 아니다 |
| 커서가 GUI 스레드 전용 | **중** | 접근자 21건이 view·viewmodel 이고 캐시 미스가 `DashRwSession.cpp:1154` 단정을 통과한다. 워커 스레드에서의 캐시 히트 읽기는 정적으로만 배제했다 |
| `get`·`getOrLoad` 가 인자를 canonical 절대경로로 정규화 | **강** | `DashAnalysisModelContextRegistry.cpp:16-48` 본문 확인. D9 의 근거다 |
| 프로젝트 루트가 정적으로 닿음 | **강** | `DashManager.h:93` → `DashProjectManager.cpp:316-319` → `DashIOController.h:91`. 루트는 `.dproj` 의 상위(`DashProjectManager.cpp:55-57`) |
| Mesh View 도크 존재 | **강** | `DashMainWindow.cpp:1569` `m_renderDock`. 제목줄 갱신 선례는 `:3008`·`:3068` |
| 트리 삭제가 등록 해제가 아님 | **강** | `deleteSelectedItem`(`DashModelingTreeWidget.cpp:506-528`)과 핸들러(`DashMainWindow.cpp:411-428`) 본문 확인. 레지스트리 접근 0 |
| 모델링 트리 비영속 | **강** | `loadDatFileAndChildren`(`:354-367`)이 `getPartNames()` 파싱으로 생성. 색은 `DecorationRole`(`:205`) · 체크는 `UserRole`(`:198`) · 투명도는 `UserRole+11`(`:211`) 뿐이고 직렬화 코드 0 |
| 좌표 일반 | **강** | 문서 0\~4 전부 `dev` @ `c989257` 기준 — 2026-09-14 에 `5caf8b0..c989257` diff 라인 매핑으로 전 좌표를 재실측했다. 커서 API·핵심 심볼 라인의 추가·삭제 0 — 집계·주장 불변 |
| 의존 관계 5건 | **중** | 산출물 요구 관계로 유도했다. 구현 중 뒤집힐 여지가 있다 |
| 빌드·실행 | **없음** | 정적 근거만 |
