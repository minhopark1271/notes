# PR 단위 티켓 분할 — 매니페스트 도입 · 착수 계획

> **2026-10-08 개정 반영** — [이슈 개정 이력](Issue-Revision-History.md)의 확정된 참조·출처 정책과 작업 경계를 본문에 반영했다. 추가 개정 계획은 미반영 팀 논의로 구분한다.

> 작업 묶음: 프로젝트 매니페스트 도입과 모듈 의존성 관리
> 관련 Issue: #239
> 마스터: [Project-Manifest-0-Work-Order](Project-Manifest-0-Work-Order.md) — 구조 방침과 결정 사항
> 기반 문서: [Project-Manifest-2-Active-Cursor-Data-Coupling](Project-Manifest-2-Active-Cursor-Data-Coupling.md) ([작업 1] 좌표) · [Project-Manifest-1-Context-Registry-And-Model-Identity](Project-Manifest-1-Context-Registry-And-Model-Identity.md) ([작업 2] 단계) · [Project-Manifest-3-Module-Deck-Ownership](Project-Manifest-3-Module-Deck-Ownership.md) ([작업 3] 항목·D13\~D21)

**[작업 1]\~[작업 3]의 티켓과 완료 이력을 보존한다.** 현재 남은 참조 전환은 **#368 → #685**이며 #520은 완료된 기반이다. 이하 과거 회차·브랜치 상태는 당시 기록이며 최신 완료 상태나 새 머지 조건을 뜻하지 않는다. PR 10개(G1\~G10 — G10 은 범위 밖 확정), 티켓 T1\~T27(T6 결번) + 개정 반영 2건(G11 #520 · G12 #526 — T28\~T31) — 문서 간 참조는 T번호로 한다. `dev` 반영은 3회("dev 반영 — 3회" 절)이고, G1\~G4 는 1회차 반영 완료(#389)라 불변이고, **2회차(G5 #415 `32dda58` · G6 #416 `11de72a` · G7 #472 `9549c9b` · G8 절단분 #491)는 `dev` 반영 완료다(#507)**. G8 은 2026-09-20 재절단으로 발행 2건(#491·#367)이다 — G8 절이 정본이다. **T26 루프(#502)는 2026-09-22 범위 밖 결정 유지. #369(G10·T18)는 당시 묶음 밖이었으며 현재는 #443에서 분리된 독립 선택 저장·복원 작업이다.** **#367 도 구현 완료다(#510 — 통합 브랜치 머지, dev 3회차 반영 대기).** **2026-09-21 결정 개정(setId · D15·D16·D20·D21·D26·D27·D28·T18 — 원문·사유는 [Project-Manifest-Set-Identity-And-Decision-Revisions](Project-Manifest-Set-Identity-And-Decision-Revisions.md))의 반영 절차·티켓은 "2026-09-21 개정 반영 절차" 절이 정본이다.**

## PR 분할 — 완료 이력과 현재 후속 작업

`좌표` 는 [Project-Manifest-2-Active-Cursor-Data-Coupling](Project-Manifest-2-Active-Cursor-Data-Coupling.md) 의 번호다.

`검토 부담` 은 파일 수로 안 드러나는 차이를 적은 **판단**이다 — **낮음** 삭제·한 자리 수정 · **보통** 여러 파일의 배선 교체 · **높음** 넓다 — 기계적 전면 개명(G3)이거나 동승 티켓이 많다(G8).
`되돌리기` 는 머지 후 원복 비용이다 — `쉬움` 코드만 · `주의` 사용자 데이터나 저장 포맷이 걸린다. 파일 수는 티켓별 목록의 이름 dedup 합집합이고 `~` 는 추정이다.

| # | PR | 티켓 | 파일 | 검토 부담 | 되돌리기 | 선행 |
|---|---|---|---:|:---:|:---:|---|
| **G1** | 기준모델을 전역 상태로 분리하고 사용처를 옮긴다 | T1 · T3 · T4 | 9 | 보통 | 쉬움 | — |
| **G2** | 화면 표시 파일 경로를 상대경로로 저장 | T2 | 4 | 보통 | 쉬움 | G1 |
| **G3** | API 이름 변경 `active*` → `displayed*` | T5 | 9 | 높음 | 쉬움 | G2 |
| **G4** | 도크 제목에 파일명 표시 + 안 쓰는 코드 삭제 | T7 · T8 | 7 | 낮음 | 쉬움 | G3 |
| **G5·#364** | 기준모델 목록 파일(원장) 도입 | T9 · T10 · T11 | ~9 | 보통 | **주의** — 사용자 프로젝트에 `referenceModels.json` 이 생긴다 | G1 |
| **G6·#365** | 파일 식별자를 uuid 로 통일 + 구 식별자 파일 삭제 | T12 · T13 | ~6 | 보통 | **주의** — 발급 uuid 에 DV 바인딩 · `AnalysisModelIdentity.json` 폐기 | G5 |
| **G7·#366** | Set 마다 자기 기준모델을 저장하고 사용 | T14 · T15 · T16 · T19 | 14 | 보통 | **주의** — 사용자 {Set}.json 에 새 키 | G6 |
| **G8·#491** | DOE 조건 세트 다중 선택 — 선택 UI·저장 형식·실행 시 값 적용 | T24 · T25 · T26 치환부 | ~9 | **높음** | **주의** — DOE 설정 저장 형식 변경 | G7 |
| **G8·#367** | Launcher 가 형상·조건 조합을 기록 + 화면 데이터 출처 교체 | T20 · T17 | ~10 | 보통 | **주의** — 새 키 + DV `source` 표기 변경 | #491 · G7 |
| **G9·#368** | 실제 입력 출처 기록과 공통 판독 계약 | T27 · T21 · T22 | 착수 시 산정 | 보통 | **주의** — 산출물 출처 기록 변경 | 완료된 #491·#367·#520 기반 |
| **#685** | Runner·Optimizer Builder 참조·검증·프리뷰 | T23 | 착수 시 산정 | 보통 | **주의** — 소비 Set의 입력 참조 전환 | #368 |

G1\~G4 가 [작업 1], G5·G6 이 [작업 2], G7\~G9 가 [작업 3]이다 — 작업 경계와 PR 경계가 일치한다. **G10(#369 — T18)은 독립 작업이라 이 참조·출처 PR 표에서 제외한다** — 아래 G10 절. #368·#685의 선행이나 완료 조건으로 두지 않는다. PR 선행은 티켓 선행의 전이 축약이다: T14 는 T4(G1)만 기다리지만 같은 PR 의 T15 가 T12(G6)를 요구해 G7 의 선행은 G6 이고, T20 은 T12(G6)만 기다리나 채움 지점이 #491 의 선택 핸들러라 #367 의 선행은 #491 이다.

**T6 은 결번이다** — 독립 티켓이 못 되는 규모라 그 범위는 T2(널 검사 2곳 — T2 가 고치는 `:2436`·`:2463` 과 같은 블록)와 T3(`get`→`getOrLoad` 2좌표 — T3 이 약화시키는 불변식의 보강)에 있다. 번호는 문서 간 참조 안정성을 위해 재사용하지 않는다.

### 티켓 T1\~T27

PR 순서로 정렬했다 — T 번호는 발행 순이라 PR 순서와 어긋나는 자리가 다섯이다(T2 · T20 · T17 · T21 · T18 — T20 은 G8 재절단으로 T24\~T26 뒤로 밀렸다). `선행` 은 티켓 단위이고, PR 단위 선행(위 표)은 그것의 전이 축약이다.

| # | PR | 티켓 | 하는 것 | 선행 |
|---|:---:|---|---|:---:|
| T1 | G1 | Registry 에 기준모델 전역 상태 신설 | 멤버 · 접근자 상대·절대 쌍 · `referenceModelChanged` 신설, Load 핸들러가 `setReferenceModel` 호출. 동작 변화 0 | — |
| T3 | G1 | Condition·CAD 가 새 상태를 읽게 전환 | 좌표 8·3·1·2 를 기준모델 층으로 + `get`→`getOrLoad` 2좌표 | T1 |
| T4 | G1 | Morphing 이 새 상태를 읽게 전환 | 좌표 4·5·6·7·9 이동 + 구독을 `referenceModelChanged` 로 교체 | T1 |
| T2 | G2 | 화면 표시 파일 경로를 상대경로로 저장 | `setActiveContext` 저장 규약 통일 · `isDisplaying()` 신설 · 널 검사 2곳 | T3 · T4 |
| T5 | G3 | API 이름 변경 `active*` → `displayed*` | API 등장 61건 / 9 파일. 기계적, 동작 변화 0 | T2 |
| T7 | G4 | Mesh View 도크 제목에 표시 중인 파일명 | `m_renderDock` 제목에 현재 렌더 파일명 (D7) | T5 |
| T8 | G4 | 안 쓰는 코드 삭제 | include 3 · 함수 4 · 오버로드 1 · 인자 1. `populate` 는 존치(T11 이 되살린다) | T5 |
| T9 | G5 | 기준모델 목록 파일(원장) 신설 | `referenceModels.json` + `registerReferenceModel`·`referenceModelPath`. **키 = uuid**(D24) — 등록 시 상대경로 v5 파생 1회로 발급, `path` 필드에 루트 상대경로. 등록은 멱등(path 스캔 판정) | T1 |
| T10 | G5 | 기준모델 경로 조회를 목록 파일 기반으로 | 최상위 `activeModel` 키(uuid — D22·D24) 조회·갱신 · 열기 복원 · Load 버튼 표시 동기화. 호출부 불변 — 접근자가 uuid 를 `path` 로 푼다 | T9 |
| T11 | G5 | 초기화·프로젝트 닫기·트리 갱신 정리 | `Registry::clear`(캐시 + 렌더 커서 2개) · `populate` 인자를 활성 기준모델로 · 죽은 스캐너 삭제 | T9 |
| T12 | G6 | 파일 식별자(uuid) 사용 통일 | 세션·모듈이 원장 키(uuid)를 content uuid 로 소비 — 경로 파생 재계산 제거, `resolveUuid` 정착. 원장 밖 파일은 파생만 | T9 |
| T13 | G6 | 세션 열기 시그니처 변경 + 구 식별자 파일 삭제 | `open(filePath, contentUuid)` · 해석 3함수 삭제 · `AnalysisModelIdentity.json` 폐기 | T12 |
| T14 | G7 | Morphing 모델에 기준모델 보관 자리 신설 | C-1 자리 + C-2 `setModel` 주입 · 죽은 멤버 `m_fileName` · T4 구독 제거 | T4 |
| T15 | G7 | Condition·Morphing Set 파일에 기준모델 저장 | D14 스키마(uuid 조인 — D24)를 Condition·Morphing {Set}.json 에 — 생성·복원 주입 + 구버전 backfill + D16 해석 + multi-source 읽기 전용 처분. 공유 코드는 `DashSetReferenceModel` 신설. CAD 는 키 없음(#366 봉합 — `cadSource` 는 D31 유보) | T12 · T14 |
| T16 | G7 | 화면 진입 시 Set 저장값을 읽게 전환 + CAD 최소 정리(봉합) | 좌표 1·9 의 출처를 전역에서 모델 보관값으로 · 좌표 2(CAD)는 죽은 전역 읽기 제거 + 생성 가드 CAD variant 제외(M5 · #366 봉합) + 파트-핀 미스매치 가드 + **과도기 3 연결 제거**(`referenceModelChanged` → Condition refresh) | T15 |
| T19 | G7 | Parameters 도크 제목에 Set 의 기준모델 파일명 | `m_rightDock` 제목에 Set 의 deck 파일명 — 앞단 2모듈(Condition·Morphing) + 그 외 기본 복귀. Launcher 표기는 T20, CAD 는 기본값(#366 봉합) (D17) | T16 |
| T24 | G8·#491 | DOE 조건 세트 다중 선택 UI + 변수 합산 | 체크 콤보로 Condition Set N 선택 + DV 합산 + DV 이름 Set 접두 + deck 공유 Set 간 bare 이름 겹침 차단 (D27) | T15 |
| T25 | G8·#491 | 다중 선택의 저장 형식과 읽기 코드 | `"Selected Design Variables"` 2원소 배열을 geometry 1 + conditions N 으로 + Preprocessor 위치 판독기 교체 + DOE Table 열별 `{set, key}` 기록 (D27) | T24 |
| T26 | G8·#491 | 실행 시 해당 세트의 변수만 값 치환 | 치환·morph 매칭을 열별 `{set, key}` 기반으로, run 대상 deck(라디오 선택) 소속 Set 의 DV 만 bare key 로 (D23·D27). 루프 갈래는 범위 밖 | T24 · T25 |
| T20 | G8·#367 | Launcher 선택 기록 — 완료 이력 | 당시 `parameterization` 형상 1 + 조건 맵·선택 핸들러·도크 표시 구현. backfill 생략 등 실제 반영 차이는 T20 상세 기록 참조. 현재 생산 출처 검증은 #368이며 당시 검증 없는 선택 저장과 구분 | 당시 T12·T24 |
| T17 | G8·#367 | Launcher 화면의 데이터 출처를 목록 파일·Set 저장값으로 교체 | Reference File 콤보 · DV `source` 상대경로화(조인 키는 `referenceModel.uuid` — D24) · `getMorphingSourceInfo` 를 자기 핀 조회로 | T15 · T20 |
| T27 | G9·#368 | Sampler·Launcher 실제 입력 출처 기록 | #520 기반 개별 Set ID와 세부 선택·실제 deck 정보를 생성 당시 산출물에 기록. 조합 ID 생성 없음 | 완료된 T20·T25·T29 기반 |
| T21 | G9·#368 | dataset 입력 출처 검증·전달 | 해석 결과의 출처를 검증해 dataset XML에 전달. 최초 입력 핀 없음. 필수 출처 없는 입력은 재생성 안내 | T27 |
| T22 | G9·#368 | Builder 참조·검증·model_info 기록 | 실제 Launcher ID·데이터셋·응답 선택을 검증·기록하고 공통 기록·판독 계약 제공 | T21 |
| T23 | #685 | Runner·Optimizer 소비 전환 | Builder ID 저장·복원·출처 검증·실행·조회·프리뷰. 상류 입력 변경 허용, 현재 Set ID 유지 | #368(T22) |
| T18 | 독립 #369 | ModelRunner NodeSet 선택 저장 | 기존 `nodeSetSource` 저장·복원과 경로 처리 설계 유지. #443 하위에서 분리 | 기존 T12 기반, #368·#685 독립 |

## 현재 구현 순서

1. 완료된 #520의 Set ID 발급·복원·역조회와 #367·#491의 선택 기록을 활용한다.
2. #368(T27 → T21 → T22)은 Sampler·Launcher·dataset 생성 경로·Builder까지 실제 출처와 공통 판독 계약을 제공한다.
3. #685(T23)은 Builder 산출물 소비 경계부터 ID 참조·검증·실행·조회·프리뷰를 전환한다.

#369는 독립 선택 저장, #444는 #441 하위의 조건부 기록 파일 분리, #473은 결과 항목 오류 수정으로 별도 진행한다. #650은 생산 Set의 버전 기록·소비 Set의 최신성 판정·Project 집계·VM 표시를 별도 설계한다. #368·#685는 PR #681의 머지 조건이 아니다.

## 2026-09 계획의 회차 순서 — 역사적 기록

```
[G1~G4] 기준모델 전역 상태 분리 + 표시 경로·이름 변경·도크·코드 정리
   │   완료 — dev 반영 1회차 (#389 squash 59518f1)
   ▼

[기준모델 갈래] G5 → G6 → G7 → G8(#491) — 완료, dev 2회차 반영 (#507)
   │   1. G5 기준모델 목록 파일(원장) 도입 — 완료 (#415 32dda58)
   │   2. G6 파일 식별자 uuid 통일 — 완료 (#416 11de72a)
   │   3. G7 Set 별 기준모델 저장·사용 — 완료 (#472 9549c9b)
   │   4. G8·#491 다중 선택 UI(T24) → 저장 형식(T25) → 실행 값 적용(T26 치환부)
   │      — 완료. 여기까지가 dev 2회차 (쌓기 대체재)
   ▼

[3회차 갈래 — 2회차 뒤 통합 브랜치에 이어 쌓아 1회 merge]
   │   ※ 2026-09-21 개정 반영분(G11·G12)의 티켓·배치 근거는
   │      "2026-09-21 개정 반영 절차" 절
   │   5. #367(G8) 조합 기록(T20) → 화면 출처 교체(T17)
   │      — 구현 완료 (#510, 통합 브랜치 머지 · dev 3회차 대기).
   │      parameterization 은 이름 키로 구현 — setId 전환은 G11 정정 범위
   │   6. G11 setId 도입 + #491·#367 후속 정정 (#520 재스펙 — T28·T29)
   │   7. G12 G7 후속 정정 (#526 — T30·T31) — G11 뒤 권장, 기술 독립
   │   8. #368(G9) 당시 조합 스탬프 계획 — 현재 실제 출처 기록으로 대체.
   │      현재 T27 생산 기록 → dataset → Builder(#368), Runner·Optimizer는 #685
   │      (#367 T20 의 기록을 소비)
   ▼

[완료] 화면 표시 상태와 기준모델이 분리되고, 전역 기준모델이 목록 파일의
       한 항목을 가리키고, Set 은 각자의 기준모델 키를 갖고, 파이프라인
       산출물이 실제 사용한 입력 출처를 기록한다. 조합 동일성·최신성 보장은 별개다
```

**그래프는 권장 순서이고 기술적 의존은 선행 열이 갖는다.**

## 당시 브랜치 운영 기록

**통합 브랜치 1개 + 발행별 브랜치(G5\~G12 — G8 은 재절단으로 발행 2건, G10 은 범위 밖 확정, G11·G12 는 2026-09-21 개정 반영분).** 발행 PR 은 `feat/reference-model-manifest` 를 향하고, 그 브랜치가 `dev` 로 들어간다.

```
dev
 └─ feat/reference-model-manifest          ← 통합 (#239) — dev 에서 분기
     ├─ feat/reference-model-ledger        G5  T9·T10·T11 — 완료 (#415)
     ├─ refactor/uuid-to-ledger            G6  T12·T13 — 완료 (#416)
     ├─ feat/set-reference-model           G7  T14·T15·T16·T19 — 완료 (#472)
     ├─ feat/doe-multi-condition-set       G8  #491 T24·T25·T26 치환부 — 완료 (dev #507)
     ├─ feat/launcher-parameterization     G8  #367 T20·T17 — 완료 (#510, dev 반영 대기)
     ├─ feat/set-identity                  G11 #520 T28·T29 — setId 도입 + #491·#367 정정
     ├─ fix/set-reference-backfill         G12 #526 T30·T31 — G7 후속 정정
     └─ feat/pipeline-deck-stamp           G9  당시 #368 T27·T21·T22·T23 (현재 T23은 #685)
```

G1\~G4 는 같은 이름의 앞선 통합 브랜치로 이미 `dev` 에 들어갔다(#389 — squash `59518f1`). 지금 브랜치는 그 뒤 `dev` 에서 새로 딴 것이고 이력이 겹치지 않는다 — 옛 브랜치를 로컬에 들고 있으면 지운다(`git branch -D`).

10개를 한 브랜치에 직접 쌓지 않는 이유는 검증 단위(각 PR 끝 상태)와 리뷰 단위가 브랜치 하나에 뭉개지기 때문이다. G별 브랜치는 각자 끝에서 빌드·동작한다.

**머지는 두 층 모두 merge 다 — squash 아님.** 티켓 1개 = 커밋 1개 전제를 지킨다 — squash 는 다중 티켓 G-PR 의 티켓 커밋을 뭉갠다. 되돌리기 단위는 merge 커밋 revert 로 G 1개(통합 브랜치) · 반영 1회(`dev`)다. 이미 squash 로 반영된 회차·PR 은 이력 확정이라 그대로 둔다.

`.claude/ticket-skill-configs.yaml` 의 `pr.merge_method: merge` 가 두 층에 그대로 쓰인다.

접두는 변경의 종류를 따른다 — G3 은 순수 개명, G6 은 저장 포맷 이관이라 `refactor/`, G12 는 기반영분 정정이라 `fix/`, 나머지는 `feat/`. 통합 브랜치명의 `manifest` 는 이 문서 시리즈명과 산출물 `referenceModels.json` 양쪽을 가리킨다.

브랜치 순서는 "순서" 절을 따른다.

### dev 를 따라가는 법

통합 브랜치는 오래 산다. `dev` 가 앞서가면 **`git merge origin/dev` 로 받는다** — rebase 는 열린 G-PR 의 base 를 통째로 갈아 전부 다시 밀게 만든다.

### 당시 dev 반영 — 3회

**회차 재정의 (2026-09-20, G8 재절단)** — 당초 2회차가 G5\~G10 전체였다. 재절단으로 2회차는 **"쌓기 제거"(G7 T16)의 대체 기능이 포함되는 최소 단위(#491)** 까지로 줄었고, 나머지는 3회차 한 묶음으로 간다. 3회차 작업은 전부 기록·화면·편의라 실행 결과의 정합성과 무관하다 — 2회차와 갈라도 사용자 워크플로우가 끊기지 않는다.

| 회차 | 범위 (issue) | 상태 |
|---|---|---|
| 1회 | G1\~G4 렌더 커서 정리 | **완료** — PR #389 squash (`59518f1`) |
| 2회 | #364(G5) · #365(G6) · #366(G7) · **#491**(G8 절단분) — 기준모델 목록 · Set 별 기준모델 · DOE 다중 선택(쌓기 대체) | **완료** — 통합 브랜치 1회 merge (#507) |
| 3회 | **#367**(G8 — T20·T17, **구현 완료 #510** — 반영만 대기) · **G11·#520**(setId 도입 + #491·#367 정정) · **G12·#526**(G7 후속 정정) · **#368**(G9) | 예정 — 2회차 뒤 통합 브랜치에 이어 쌓아 1회 merge. #367 은 통합 브랜치에 머지됨(#510) |

당시 3회차 내부 순서는 **G11 → #368**이었다. 현재 G11(#520)은 완료됐고 #368이 개별 Set 출처 계약을 정의한 뒤 #685가 소비한다. 조합 ID 파생은 폐기했다. G12 는 기술 독립이나 이른 배치(G11 직후 권장)다 — 근거는 "2026-09-21 개정 반영 절차" 절.

`dev` 에서는 반영 1개 = merge 커밋 1개 = 되돌리기 단위(`revert -m`)이고, 티켓 단위 이력이 커밋으로 남는다.

QA 는 회차당 한 패스다. 2회차 — 프로젝트 열기/닫기/재오픈·폴더 이동(#364·#365) · Set 기준모델 고정(#366) · DOE 다중 선택 + 해석파일별 수동 실행(#491). 3회차 — setId 발급·복원·rename 내성(G11) · 구프로젝트 마이그레이션: source 유도 핀·multi-source 자동 분할(G12) · Launcher 조합 기록·화면 출처(#367) · 산출물 출처 기록·검증(#368), 소비 전환은 #685에서 별도 검증.

## 2026-09-21 개정 반영 절차 — 당시 계획과 현재 처분

[Project-Manifest-Set-Identity-And-Decision-Revisions](Project-Manifest-Set-Identity-And-Decision-Revisions.md)(처분 문서 — setId SI-1\~SI-6a · 개정 8건의 원문·사유)를 티켓과 순서로 옮긴 실행 계획이다. 원칙 하나 — **구현 완료분은 불변이다.** dev 반영분(1·2회차)과 통합 브랜치 머지분(#367 — #510)의 이력·티켓 본문(T15·T16·T24\~T26·T20·T17)은 구현 시점 기록으로 두고, 개정은 전부 신규 발행(G11·G12)과 미발행분 스펙 반영으로 처리한다.

### 대응 분류

| 분류 | 대상 | 대응 |
|---|---|---|
| 완료 — 불변 | dev 반영분(G1\~G7 · #491) + 통합 브랜치 머지분(#367 — #510, dev 3회차 대기)의 이력·티켓 본문 | 그대로 둔다 — 소급 수정 없음 |
| 기반영분 정정 | G7 구현(D15 재개정 · D16 3차 개정 · D28 폐기) · #491 구현(DOE Table `{set, key}` 조인) · #367 구현(`parameterization` 이름 키 조인 — #510) | **신규 발행 G12(#526) · G11(#520 재스펙 — T29)** |
| 미구현분 스펙 반영 | #368의 당시 SI-5·핀 요구 | 현재 폐기. 개별 Set 출처의 생산·공통 계약(#368)과 소비(#685)로 대체 |
| 범위 밖 | 산출물 폴더 식별(SI-6a — 폴더명 유지 · setId 색인 역조회) | 현재 #443의 #368→#685 참조 전환 및 개명 오류 수정과 접점 조율. G9 일괄 머지를 조건으로 두지 않음 |
| 범위 밖 | T26 루프 — 해석파일별 자동 반복 실행(#502) | **착수하지 않는다**(2026-09-22 확정). 편의 자동화이고 수동 라디오 전환·재실행이 같은 결과를 낸다 — 아래 "T26 루프 — 범위 밖" 절 |
| 독립 작업 | T18 NodeSet 소스 영속화(#369) | 당시 묶음 제외 이력 유지. 현재 #443에서 분리한 선택 저장·복원 작업으로 아래 G10 절 참조 |

### 순서와 배치 근거

```
[구현 완료 — dev 반영만 대기]
#367 (G8)   T20 조합 기록 + T17 화면 출처 교체 — #510 통합 브랜치 머지.
   │        parameterization 은 이름 키로 구현 — setId 전환은 G11 이 정정
   ▼
[정정 — 기반영분 대응]
G11 setId 도입 + #491·#367 후속 정정   T28 발급·영속·복원 → T29 조인 setId 전환
   │   당시 #368 선행 기반 — 현재 #520 완료, T27은 개별 Set 출처를 읽는다.
   │   발행 완료 — #520 재스펙 (2026-09-22, 아래 G11 절)
   ▼
G12 G7 후속 정정 (#526)                T30 D15 재개정 + D28 제거 → T31 D16 3차 개정
   │   G11 과 기술 독립 · G11 뒤 권장 · 소급 없음이라 이른 배치
   ▼
[미구현 — 개정 스펙으로 발행·착수]
#368 (G9)   현재 출처 계약으로 대체: T27 → T21 → T22. T23은 #685로 분리

[범위 밖]
산출물 폴더 식별 (SI-6a) — 폴더명 유지, 현재 #368→#685 및 개명 수정과 조율
T26 루프 (#502) — 착수하지 않는다 (2026-09-22 확정)
T18 NodeSet 소스 영속화 (#369 — G10) — 당시 제외, 현재 독립 작업
```

배치 근거 셋.

| # | 근거 |
|---|---|
| 1 | **G11 의 정정 반경은 기반영 2건** — #491 의 DOE Table `{set, key}` 와 #367(#510)의 `parameterization` 이름 키 조인. 둘 다 이름 조인이라 rename·동명 재생성에서 무너지는 같은 결함 부류이고, SI-4 가 setId + `name` 병기로 바꾼다. 당시 구 기록 이름 판독은 보존하되 새 필수 출처를 추론하는 경로로 사용하지 않음 |
| 2 | **G12 는 이르게** — D15 재개정은 소급이 없어(기존 핀 불문), 정정 전 `dev` 로 구프로젝트를 열 때마다 전역-기반 오핀 코호트가 늘고 그 핀은 D17(변경 UI 불요)로 영구다. 지연 = 손실. G11 뒤가 권장인 것은 자동 분할이 만드는 신규 Set 이 생성 시점에 setId 를 받기 때문(SI-3)이고, 앞이어도 성립한다 — 구버전 발급 경로가 흡수한다 |
| 3 | **현재 #368은 완료된 #520을 사용한다.** 개별 Set 참조·실제 출처를 Builder까지 기록하고 공통 계약을 제공한다. SI-5 조합 ID와 최초 입력 핀은 폐기했고 T23 소비는 #685로 분리했다 |

회차 편성 — 정정 2건(G11·G12)은 **3회차 편입, 내부 맨 앞**이다. 3회차 착수가 늦어지면 둘만 먼저 `dev` 1회 반영(중간 회차)해도 된다 — 판단 기준은 근거 2 의 오핀 코호트 누적이다.

### G11 — setId 도입 + #491·#367 후속 정정 (#520 완료 기록)

아래 T28·T29는 완료된 발급·영속·복원·역조회 기반의 구현 기록이다. 구 기록의 이름 판독은 새 출처 계약을 충족시키지 않으며 필수 출처 없는 산출물은 재생성한다.

| | |
|---|---|
| 티켓 순서 | T28 발급·영속·복원 → T29 조인 setId 전환 |
| 묶은 근거 | 조인 전환(T29)은 setId 도입(T28)이 선행이라 한 묶음(처분 문서 "이슈·구현" 표) |
| 선행 | 없음 — #510 머지 상태의 통합 브랜치에서 착수 가능. #368 앞 필수(배치 근거 3) |
| 발행 방법 | **#520 재스펙 완료(2026-09-22)** — #520(#510 리뷰 후속)이 같은 자리(발급·백필·`parameterization` 동봉·검증 조인)를 이미 들고 있어 별도 발행하면 두 겹이 된다. 결정 충돌 2건은 처분 문서 정본으로 정정 — ① 형식: #520 의 `QUuid` v4 전체·`setUuid` 키 → **SI-1 12자리 hex(v4 절단) + 발급 시 중복 검사·`setId` 키** ② 조인 지위: #520 의 "이름 주소 + uuid 검증 전용" → **SI-4 setId 조인 + `name` 병기**(불일치 시 Set json 정본). DOE Table `{set, key}` 전환은 #520 범위 밖이라 재스펙에 편입했다. 종전 본문은 #520 편집 이력이 갖는다 |
| 되돌리기 | **주의** — 각 `{Module}_{Set}.json` 에 `setId` 키 · DOE Table 열 메타데이터·`parameterization` 조인 형식 변경 |

#### T28 — setId 발급·영속·복원 (SI-1\~SI-3)

| | |
|---|---|
| 하는 것 | **발급**(SI-1) — 12자리 랜덤 hex(v4 절단) + 발급 시 프로젝트 내 중복 검사. 생성 순서는 id 에 싣지 않는다. **영속**(SI-2) — 각 `{Module}_{Set}.json` 의 `setId` 키가 정본, 별도 Set 원장 없음. setId → Set 역조회는 열기 시 전 Set 스캔(`restoreExistingModules` 가 이미 전 파일을 읽는다 — `DashProject.cpp:1245-1258`). 열기 시 중복 감지(json 손 복제) → 나중 파일 재발급 + 로그. **시점**(SI-3) — 신규 Set 은 생성 핸들러(`createNewSet`, `DashProject.cpp:705` — json 이 어차피 써진다), 구버전 Set(키 부재)은 열기 복원 시 발급 + 즉시 write-back 1회. 쓰기 실패 = 로그 + 메모리 유지, 다음 열기 재발급 |
| 검증 | 신규 Set 생성 → json 에 `setId` · 구프로젝트 열기 1회에 전 Set 발급 + write-back, 재열기에 값 불변 · json 을 손 복제해 열면 나중 파일이 재발급받고 로그가 남는다 |

#### T29 — 조인 setId 전환 (SI-4 — #491·#367 후속 정정)

| | |
|---|---|
| 하는 것 | **DOE Table(#491 기반영분)** — T25 가 기록하는 열별 `{set, key}` 를 `{set: setId, name: Set 이름 병기, key: bare}` 로(SI-4 — 불일치 시 Set json 정본). 소비자 해석 전환 — T26 치환부의 소속 판정(`DashJobRunner`) · morph 매칭(`DashMorphingDoeExecutor`) · Preprocessor 판독기(`DashDataProcessor`)가 setId → Set json → `referenceModel.uuid` 로 푼다. **`parameterization`(#367 기반영분 — #510)** — `geometry.set` 과 `conditions` 맵 키를 이름에서 setId 로 + `name` 병기(`DashParameterization`·`DashDoeSelection`·`DashAnalysisLauncher` — #510 신설 자리). `getMorphingSourceInfo` 등 소비자의 Set 조인도 setId 우선으로 — #520 이 지적한 동명 재생성 오조인이 여기서 닫힌다. **구 기록(`{set: 이름}` Table · 이름 키 parameterization)은 기록된 대로 해석 — 이름 폴백, 재기록 없음.** 좌표는 #491·#510 반영분 기준으로 착수 시 재실측 |
| 검증 | 신규 DOE Table 열·`parameterization` 이 setId·name 을 든다 · **Set rename·동명 재생성 뒤에도 치환·morph 매칭·part 추천이 옛 실체에 조인되지 않는다**(이름 조인이 죽는 케이스 — D27 재개정·#520 의 재현 검증) · 구 기록은 이름 폴백으로 그대로 동작한다 |

### G12 — G7 후속 정정 (#526)

| | |
|---|---|
| 티켓 순서 | T30 D15 재개정 + D28 기계장치 제거 → T31 D16 3차 개정 |
| 선행 | 없음 — G11 과 기술 독립, G11 뒤 권장(배치 근거 2) |
| 되돌리기 | **주의** — 사용자의 multi-source json 을 자동 분할한다. `.bak` 보존이 완화 장치 |

#### T30 — D15 재개정 + D28 기계장치 제거

| | |
|---|---|
| 하는 것 | **backfill 핀 출처 교체** — 전역 reference 에서 Set 자신의 DV `source` 유도로. Condition 은 상대경로 그대로, Morphing 은 bare filename 을 configs 복사본 → 원장 `path` → 루트 스캔 순 해석(복수 히트는 정렬 후 첫번째 + 로그). 유도 실패 시에만 전역 폴백, 빈 값이면 핀 안 함, 소급 없음. **multi-source json 진입 시 1회 자동 분할** — deck 별 Set + `.bak` 보존 + 결과 통지(선택지 없음). **D28 기계장치 제거** — `DashDesignVariableModel` 의 회색·잠금·툴팁 처리 · `loadFromJsons` 의 핀 deck 인자 · `FECondition` 예외 판정 · DOE 의 구 multi-source 읽기 경로. 분할이 제거의 전제라 한 티켓이다. 자리는 T15·T16 반영분(`DashSetReferenceModel` · `DashDesignVariableModel` · Condition·Morphing 모델/PM) — 착수 시 재실측 |
| 검증 | 구프로젝트 Set 진입 → 자기 DV `source` 의 deck 이 핀된다(전역 상태 무관) · multi-source json 진입 → deck 별 Set 자동 분할 + `.bak` + 통지, 분할 후 어느 Set 에도 foreign 행 없음 · 유도 실패 케이스만 전역 폴백 |

#### T31 — D16 3차 개정 — 스캔 분기 제거

| | |
|---|---|
| 하는 것 | `referenceModel` 해석 2단(path 원장 스캔 + uuid backfill)을 **v5(path) 재파생 조회 1회**로 교체 — T15 의 해석 트리(`DashSetReferenceModel`) 한 곳. D11 의 "두 값 갈림 → 원장 정본 backfill" 도 후속작업 4(sha256 이관) 전까지 유보 — uuid ≡ v5(path)인 동안 발화 조건이 없다 |
| 검증 | `path` 를 원장에 없는 값으로 손편집 → 미지정 + 로그 · 그 deck 재Load 후 재진입 시 회복(v5 재파생이 재생 uuid 에 히트) |

## PR 상세

PR 단위 근거는 각 PR 머리에, 티켓 단위 근거는 각 티켓에 남긴다.

### G1 — 기준모델을 전역 상태로 분리하고 사용처를 옮긴다

| | |
|---|---|
| 티켓 순서 | T1 층 신설 → T3 Condition·CAD → T4 Morphing |
| 묶은 근거 | 신설과 소비자 이동 동승. 이득: PR 2개 감소 + T1→T3·T4 rebase 연쇄 제거. 완화: 티켓 3분할 — "레이어 설계" 와 "9좌표 라우팅" 을 티켓 경계로 가른다 |

#### T1 — Registry 에 기준모델 전역 상태 신설

| | |
|---|---|
| 파일 | `controller/DashAnalysisModelContextRegistry.h`·`.cpp` · `view/DashMainWindow.cpp` |
| 하는 것 | `m_referenceFilePath` 멤버 · `setReferenceModel()` · `referenceContext()` · `referenceFilePath()`(상대) · `referenceAbsolutePath()`(절대) · `referenceModelChanged` 시그널 신설. D9 대로 `getProjectRootDir()` 로 해석하는 **내부 헬퍼 1개**를 두고 nullptr 가드를 건다. Load 핸들러(`DashMainWindow.cpp:2140`)가 기존 `setActiveContext`(`:2267`)에 더해 `setReferenceModel` 을 부른다 |
| 안 하는 것 | 소비자 이동 — 다음 티켓(T3·T4)의 몫이다. 이 티켓 시점에 `referenceContext()` 를 읽는 곳이 0 이다 |
| 검증 | 빌드 통과 · Load 후 `referenceFilePath()` 가 프로젝트 루트 상대경로를 돌려준다(로그 1줄) · 프로젝트 미개방 상태에서 `referenceContext()` 가 nullptr |
| 검토 포인트 | **이 티켓의 동작 변화가 0 이어야 한다.** 기존 경로에 호출 한 줄만 붙는다 |

#### T3 — Condition·CAD 가 새 상태를 읽게 전환

| 좌표 | 자리 | 처분 |
|---|---|---|
| 8 | `DashMainWindow.cpp:433-442` | 람다에서 `refreshFromFile(fp)` 제거. 널 검사 분기(`:436-441`)가 목적을 잃어 `logMessage` 한 줄로 준다 |
| 3 | `DashConditionParameterizationWidget.cpp:222` | `activeContext()` → `mModel->getContext()` |
| 1 | `DashConditionParameterizationWidget.cpp:313-315` | 출처를 `referenceAbsolutePath()` 로 — `:314` 의 `QFile::exists` 와 `refreshFromFile` 이 절대경로를 요구한다. 상대 형태(`referenceFilePath()`)는 영속·키 용도다 |
| 2 | `DashGeometryParameterCADWidget.cpp:345-347` | 동상 |
| — | `DashConditionParameterization.cpp:111` · `DashGeometryParameterCAD.cpp:99` | `getContext()` 의 `get` → `getOrLoad` (T6 흡수분). `get` 이 안전한 것은 "`m_loadedFilePath` 대입자가 곧 로더" 라는 불변식 덕인데, 이 티켓이 그 대입 경로의 출처를 바꾸므로 같은 자리에서 미스 자가 복구로 보강한다 |

**좌표 3·8 은 묶는다.** 좌표 8 만 떼면 표는 모델의 `m_loadedFilePath` 를, 하이라이트는 커서를 보게 되어 한 PR 동안 다른 deck 을 가리킨다. 쪼개서 얻는 이득이 0 이다.

| | |
|---|---|
| 묶은 근거 | `get`→`getOrLoad` 2좌표 동승. 2줄 규모이고 이 티켓이 약화시키는 불변식의 보강이라 주제가 같다. 같은 티켓으로 함께 가고 PR 설명에 경계를 명시한다 |
| 검증 | Condition Set 을 연 뒤 모델링 트리 체크박스를 토글해도 표의 대상 deck 이 안 바뀐다 · 같은 조작 뒤 조건 행을 클릭하면 3D 하이라이트가 표와 같은 deck 에 걸린다 · Optimizer 프리뷰를 돌려도 Condition·CAD 대상이 유지된다 |
| 동작 변화 | "Set 을 먼저 클릭하고 나중에 Load" 순서에서 복구 경로가 없어져 Set 재클릭이 필요하다. G7 이 닫을 때까지 남는 문서화된 과도기 동작이다(D8) |

#### T4 — Morphing 이 새 상태를 읽게 전환

| 좌표 | 자리 | 처분 |
|---|---|---|
| 4 | `DashGeometryParameterPresentationModel.cpp:46` | `activeFilePath()` → `referenceAbsolutePath()` — 반환값이 `QFile::copy` 의 원본 경로로 쓰인다(`:76`). DV `source` 문자열에는 파일명만 들어가 표현 무관 |
| 5 | 동 `:58` | `activeContext()` → `referenceContext()` (폴백 경로) |
| 6 | `DashMorphingSettings.cpp:562` | 동상 |
| 7 | 동 `:636` | 동상 |
| 9 | `DashMainWindow.cpp:3271` | 동상 |
| — | `DashMorphingSettings.cpp:90` | 구독을 `activeContextChanged` → `referenceModelChanged` 로 **교체**. 소멸이 아니다 — 기준모델이 바뀌면 node set 목록이 갱신돼야 한다 |

| | |
|---|---|
| 검증 | 체크박스 토글·프리뷰 뒤에도 Morphing 대상이 유지된다 · **좌표 4 는 디스크를 본다** — DV `source` 문자열과 configs 로 복사된 dat 이 기준모델을 가리키는지 파일로 확인. UI 확인만으로 끝내면 안 된다 |
| 검토 포인트 | 구독 교체가 빠지면 기준모델을 바꿔도 node set 목록이 안 따라온다 |

### G2 — 화면 표시 파일 경로를 상대경로로 저장 (T2)

T1 이 만든 해석 헬퍼를 렌더 층에도 적용해 **Registry 의 저장 규약을 하나로 만든다**(D12).

**G1 이 선행인 이유.** `activeFilePath()` 의 외부 소비자 5곳 중 3곳(좌표 1·2·4)은 반환값을 `QFile::exists`·`refreshFromFile`·`QFile::copy` 에 쓰고, 좌표 8 람다는 `activeContextChanged` payload 를 `refreshFromFile` 에 민다. 상대경로 전환이 이들보다 먼저 가면 경로가 CWD 기준으로 풀려 그 PR 끝에서 동작하지 않는다. T3·T4 가 넷을 기준모델 층으로 옮긴 뒤에는 남는 소비자가 이 PR 이 손대는 자리와 정확히 일치한다.

| 자리 | 처분 |
|---|---|
| `Registry.cpp:54-60` | `setActiveContext` 가 canonical 절대경로 대신 상대경로를 저장한다. 정규화 지점은 그대로 이 함수 하나다 |
| `Registry.h:32` | `activeFilePath()`(상대) 옆에 `activeAbsolutePath()`(절대)를 둔다. `activeContext()` 는 내부에서 해석해 `get()` 에 절대경로를 넘긴다 |
| 신설 | `isDisplaying(const QString& path)` — 인자를 상대·절대 가리지 않고 정규화해 비교한다 |
| `MainWindow:2436`·`:2463` | `activeFilePath() != filePath` → `!registry.isDisplaying(filePath)` |
| `ModelingTreeWidget:472-489` | `onActiveContextChanged` 진입에서 payload 를 절대화한다 — `:481` `addFileToTreeWithStructure` 의 `exists()` 검사와 `:485` `UserRole` 비교가 절대경로를 요구한다. `:477` 은 파일명 비교라 표현 무관 |
| `MainWindow:2439-2440`·`:2467-2468` | `activeContext()` 반환에 널 검사 + early return (T6 흡수분). `setActiveContext` 가 `getOrLoad` 실패 시 조용히 반환해(`Registry.cpp:52`) 커서가 이전 deck 에 남으면 엉뚱한 deck 이나 nullptr 를 역참조하는 경로다 |

| | |
|---|---|
| 묶은 근거 | 널 검사 2곳 동승. 4줄 규모라 실변경이 안 묻히고, 이 PR 이 바로 위 `:2436`·`:2463` 을 고치는 유일한 기회다. 별도 티켓으로 분리한다 |
| 검증 | 같은 deck 의 체크박스를 다시 토글해도 **카메라가 리셋되지 않는다** · 같은 파일을 다시 Load 해도 트리에 중복 노드가 안 생긴다 · 프리뷰 산출물이 트리에 뜨고 렌더된다 |
| 검토 포인트 | 호출자가 표현을 몰라도 되게 하는 것이 목적이다. 호출부에 `QDir(...).relativeFilePath(...)` 가 보이면 잘못 간 것이다 |

**딸린 이득 1건.** 현행은 `m_activeFilePath` 가 canonical 인데 트리 `UserRole` 은 `setData(filePath, ...)`(`ModelingTreeWidget.cpp:248`)로 raw 를 넣는다. 같은 값이 흘러 들어가 우연히 맞고 있을 뿐이다. `isDisplaying` 이 양쪽을 정규화하면 그 우연에 안 기댄다.

**같은 함수의 `:477` 은 건드리지 않는다.** `onActiveContextChanged` 가 `:477` 에서 이름으로(`findItems`), `:485` 에서 경로로 판정해 갈라져 있는데, 그것은 표현 문제가 아니라 로직 결함이라 이 PR 에 섞으면 한 PR 이 두 종류의 변경을 하게 된다. 후속작업이다.

미세한 검토 포인트(정규화·널 검사·UserRole)가 많아 다른 티켓과 병합하지 않는다 — 묻히면 안 되는 diff 다.

### G3 — API 이름 변경 `active*` → `displayed*` (T5)

| | |
|---|---|
| 대상 | `m_activeFilePath`·`m_activeActor` → `m_displayedFilePath`·`m_displayedActor` · `setActiveContext` → `setDisplayedContext` · `activeContext`/`activeFilePath`/`activeAbsolutePath`/`activeActor` → `displayed*` · `activeContextChanged`/`activeActorUpdated` → `displayed*` |
| 규모 | API 등장 61건 / 9 파일. `DashOcctViewWidget` 의 `m_context`·`AIS_InteractiveContext` 는 이름만 비슷한 남이다 — 대상 아님 |
| 검증 | 빌드 + 전 기능 회귀. **동작 변화가 0 이어야 한다** |
| 검토 포인트 | LSP rename 으로 기계적이다. diff 에 rename 외의 변경이 섞이면 반려 |

크지만 기계적이라 단독 PR 로 둔다 — **병합 하한이다.** 기계적 변경이 diff 과반이면 어떤 실변경과도 못 묶고, 쪼개면 절반만 개명된 중간 상태가 PR 끝에서 동작하지 않는다.

### G4 — 도크 제목에 파일명 표시 + 안 쓰는 코드 삭제

| | |
|---|---|
| 티켓 순서 | T7 도크 제목줄 → T8 죽은 코드 제거 |
| 묶은 근거 | 소기능(T7)과 삭제(T8) 동승. 둘 다 검토 부담 낮음·규모 미미. 완화: 티켓 분리. 삭제 티켓이 갈래 맨 뒤에 온다 |

#### T7 — Mesh View 도크 제목에 표시 중인 파일명

`m_renderDock`(`DashMainWindow.cpp:1569`)의 제목줄에 현재 렌더 파일명을 띄운다. `displayedContextChanged` 를 구독한다. 같은 패턴이 이미 있다 — `m_leftDock->setWindowTitle(projectName)`(`:3008`·`:3068`).

기준모델은 Load 버튼의 활성 상태로 표시한다(D7).

#### T8 — 안 쓰는 코드 삭제

| 종류 | 좌표 |
|---|---|
| include | `DashMorphingDoeExecutor.cpp:4` · `DashAnalysisLauncher.cpp:7-8` · `DashGeometryParameterWidget.cpp:11-12` |
| 함수 | `DashMainWindow::updateCheckedPartsGeometry`(`:2598-`) · `DashModelingTreeWidget::addFileToTree`(`:493`)·`buildTreeRecursive`(`:497`)·`parseVtmFile`(`:502`) |
| 오버로드 | `DashGeometryParameterCADWidget::setModel(DashGeometryParameterCAD*)`(`:351`) |
| 인자 | 2인자 `setModel` 의 `projectPath` — `Q_UNUSED`(`ConditionWidget:271`) |

`DashModelingTreeWidget::populate`(`:369`)는 **지우지 않는다** — T11 이 인자를 활성 기준모델로 바꿔 되살린다.

G3 앞으로 당기는 안은 이득이 모자란다 — 얻는 rename 절감이 1\~2건이다. `updateCheckedPartsGeometry` 는 살릴 경우 그 자체가 결함이다 — 인자 `filePath` 를 받아 놓고 컨텍스트는 `activeContext()`(`:2604`)로 얻는다.

### G5 — 기준모델 목록 파일(원장) 도입

| | |
|---|---|
| 티켓 순서 | T9 원장 신설 → T10 조회 전환 → T11 clear·재파싱 |
| 묶은 근거 | 신설(T9)과 소비자(T10·T11) 동승. 이득: PR 2개 감소 + rebase 연쇄 제거. 완화: 티켓 3분할 — 원장 생명주기(생성→조회→소거) 한 주제다 |

#### T9 — 기준모델 목록 파일(원장) 신설

| | |
|---|---|
| 하는 것 | 원장 클래스 + 숨김 configs 의 `referenceModels.json` + `DashProject` API 2개(`registerReferenceModel` — uuid 반환 · `referenceModelPath` — uuid→path). Load 핸들러가 등록을 부르고 **멱등**이다 |
| 스키마 | **키 = uuid**(D24) — 등록 시 상대경로 v5 파생 1회로 발급(T12 산식의 선반영), 값 = `path`(루트 상대)·`sha256`·`size`·`mtimeMs` + 최상위 `activeModel`(D22 — uuid). 이 티켓에서는 `activeModel` 을 비우고 T10 이 채운다 |
| 안 하는 것 | `unregisterReferenceModel` — D5 대로 해제 지점을 두지 않는다. `getOrLoad` 시그니처는 손대지 않는다 |
| 검증 | Load 시 항목 생성 · 같은 파일 재Load 시 중복 없음 · `SaveProjectAs` 후 파일이 따라간다 |

T1 이 `m_referenceFilePath` 를 상대경로로 들게 해 뒀으므로 `referenceFilePath()` 반환값이 **원장 `path` 필드와 같은 문자열**이다(키는 uuid — D24). G2 는 렌더 커서 쪽이라 이 PR 의 선행이 아니다.

#### T10 — 기준모델 경로 조회(`referenceFilePath()`)를 목록 파일 기반으로

Registry 멤버에서 원장 최상위 `activeModel` 키(uuid — D22·D24) 조회로 구현만 바꾸고, `setReferenceModel` 이 그 키를 갱신한다. 접근자는 uuid 를 원장 `path` 로 풀어 돌려주므로 **호출부는 불변**이다(D2) — T1 이 접근자 이름을 고정해 둔 값이 여기서 나온다. reference 커서의 내부 표현이 이 티켓에서 uuid 로 전환된다(D12 개정). 프로젝트 열기 시 `activeModel` 로 활성 기준모델을 복원하고, Load 버튼 활성 표시(D7 — `ProjectFileTreeDelegate` 의 `m_selectedIndex`, 활성 스타일은 기존 구현)를 함께 동기화한다.

검증 — 재오픈 후에도 전역 기준모델이 유지된다 · Load 버튼 활성 표시가 복원된 기준모델을 가리킨다.

#### T11 — 초기화·프로젝트 닫기·트리 갱신 정리

| 하는 것 | 좌표 |
|---|---|
| `Registry::clear` 신설 + `CloseProject` 연결 | `DashProjectManager.cpp:212-221` |
| `clear` 가 비우는 것 | 컨텍스트 캐시 + **렌더 커서 2개**(경로 · actor). 렌더 커서를 안 비우면 D9 의 "루트 교체" 요건이 안 닫힌다 — 프로젝트가 바뀌면 같은 상대경로가 다른 파일을 가리킨다. 기준모델 경로는 T10 이 멤버를 원장 `activeModel` 조회로 대체해 비울 것이 없다 — 프로젝트가 닫히면 원장 접근이 끊겨 `referenceContext()` 가 nullptr 로 선다(D9 가드) |
| `populate` 인자를 디렉터리에서 **활성 기준모델 1건**으로 | `DashModelingTreeWidget.cpp:369` |
| 원장 전량을 안 넘기는 이유 | D5 로 해제 지점이 없어 원장이 단조 증가한다 — 전량을 넘기면 한 번이라도 Load 한 deck 을 재오픈마다 전부 파싱한다. 등재 목록 API(`referenceModels`)를 두지 않는 근거이기도 하다 |
| 죽은 스캐너 삭제 | `DashProject.cpp:1066` `loadSetsFromConfigs` |

**트리는 저장본 복원이 아니라 재파싱이다** — 모델링 트리는 영속화되지 않는다.

검증 — 재오픈 시 활성 기준모델의 트리가 다시 뜬다 · 프로젝트 A 를 닫고 B 를 열면 A 컨텍스트가 남지 않는다 · **A 와 같은 상대경로를 가진 B 의 deck 이 A 의 컨텍스트로 안 잡힌다**.

### G6 — 파일 식별자를 uuid 로 통일 + 구 식별자 파일 삭제

| | |
|---|---|
| 티켓 순서 | T12 uuid 소비 전환 → T13 RwSession 시그니처·identity store 폐기 |
| 묶은 근거 | uuid 가 identity store 에서 원장으로 옮겨가는 **한 포맷 이동의 두 반쪽**이다. 가르면 두 저장소가 공존하는 과도기가 생긴다 |

#### T12 — 파일 식별자(content uuid) 사용 통일

발급·영속은 T9 가 한다(키 = uuid — D24). 이 티켓은 **소비 측 전환**이다 — 세션·모듈이 원장 키를 content uuid 로 받아 쓰고 경로 파생 재계산 경로를 없앤다. `resolveUuid(relPath)` 정착 — 원장 `path` 스캔이 히트하면 그 키, 미스면 상대경로 v5 파생 1회. 원장에 없는 deck(morph 산출물·프리뷰)도 같은 산식으로 파생하되 원장에 쓰지 않는다.

검증 — 프로젝트 폴더를 옮겨도 원장 항목이 유효하고 DV-Condition uuid 바인딩이 유지된다.

#### T13 — 세션 열기(RwSession) 시그니처 변경 + 구 식별자 파일 삭제

| | |
|---|---|
| 하는 것 | `DashRwSession::open(filePath, contentUuid)` 로 시그니처 변경. `rwResolveContentIdentity`(`:1092-1148`)·`rwIdentityStorePath`(`:1070`)·`rwConfigsDirFromProject`(`:1080`) 삭제. `rwFileSha256`(`:1032`)은 호출자 쪽으로 옮긴다. `AnalysisModelIdentity.json` 폐기 |
| 검증 | 기존 프로젝트의 DV-Condition 체크 상태 유지 |
| 검토 포인트 | **SDK 경계에 가장 가깝다.** reader-writer DLL 은 손대지 않는다 — `ContentInfo::uuid`(`IRWModule.hpp:106-115`)의 계약이 "호출자가 덱 파일당 안정적으로 유지·제공할 책임" 이고, 원장이 그 책임을 진다 |

마이그레이션 코드는 필요 없다 — DV-Condition 은 조건 이름으로 키가 잡혀 있고 로더 폴백(`DashConditionParameterization.cpp:495-497`)과 backfill(`:444-447`)이 이미 있다.

### G7 — Set 마다 자기 기준모델을 저장하고 사용

| | |
|---|---|
| 티켓 순서 | T14 Morphing 자리 신설 → T15 2모듈 영속화 → T16 진입 읽기 교체 + CAD 봉합 → T19 도크 제목줄 |
| 묶은 근거 | 네 티켓 동승. 전부 "Set 이 자기 deck 을 소유한다" 한 주제다. 완화: 티켓 4분할. T15 시점의 과도기({Set}.json 은 Set 의 deck 을 기록하는데 화면은 전역을 따름)는 같은 PR 의 T16 이 닫아 PR 밖으로 노출되지 않는다 |
| 선행 | T14 자체는 T4(G1)만 기다리나, T15 가 T12(G6)를 요구해 PR 단위 선행은 G6 이다 |
| 상태 · 후속 정정 (2026-09-21) | **구현 완료(#472 — dev #507).** 이후 결정 개정 — D15 재개정(backfill 출처를 전역에서 Set 자신의 DV `source` 로 + multi-source 진입 시 1회 자동 분할) · D28 폐기(회색·잠금·툴팁 기계장치 제거) · D16 3차 개정(원장 스캔·backfill 분기 제거) — 은 이 PR 의 소급 수정이 아니라 **G12(T30·T31 — "2026-09-21 개정 반영 절차" 절)** 로 처리한다. 원문·사유는 [Project-Manifest-Set-Identity-And-Decision-Revisions](Project-Manifest-Set-Identity-And-Decision-Revisions.md) — 아래 T15·T16 본문은 구현 시점 스펙 기록이다 |
| CAD 처분 (2026-09-18 재스펙) | CAD 는 해석 deck 을 소비하지 않는다(#366 실측 — `getContext()` 는 #389 가 삭제 · `m_loadedFilePath` 읽는 곳 0 · 표는 `applyNxCadParameterJson`). 이 PR 은 **봉합만** — 생성 가드 CAD variant 제외(T16 — #389 `c3072bc` 회귀 닫힘) · 진입 시 죽은 전역 읽기 제거(T16) · 키 미도입(도크 제목 기본 "Parameters"). T15 영속화·T19 표시가 Condition·Morphing 2모듈로 좁혀진다. CAD 형상 출처 영속화(D29\~D31 — `cadSource`)는 **유보 — 이 묶음에 CAD PR 없음**(후속작업 13 동반 · D32·D33 철회 — [Project-Manifest-CAD-Path-Disposition](Project-Manifest-CAD-Path-Disposition.md)). G7 좌표는 #366 이 2026-09-18 재실측(`:3271`→`:3181` 등) |

#### T14 — Morphing 모델에 기준모델 보관 자리 신설

| | |
|---|---|
| 파일 | `model/DashGeometryParameter.h`·`.cpp` · `view/overlay/DashMorphingSettings.h`·`.cpp` · `view/DashMainWindow.cpp` |
| 하는 것 | C-1 — Morphing 모델에 Condition·CAD 와 동형의 자리(`m_loadedFilePath` + `getContext()` + `refreshFromLoadedAnalysis()`) 신설. C-2 — `DashMorphingSettings::setModel` 신설, `onStartMorphingClicked`(`DashMainWindow.cpp:3181`, 좌표 9)가 그 시점의 전역 reference 를 모델에 핀하고 모델을 주입. 죽은 멤버 `m_fileName`(`DashGeometryParameter.h:50`, 호출부 0) 삭제. T4 가 옮겨 둔 `referenceModelChanged` 구독(`DashMorphingSettings.cpp:90`) 제거 — 주입이 대체한다 |
| 묶은 근거 | 멤버 삭제·구독 제거 동승. 주입이 구독을 대체하고 신설 자리가 죽은 멤버와 같은 파일이라 주제가 같다 |
| 주입 지점 | **2곳** — Start Morphing 외에 Set 재진입 분기(`handleGeometryParameterSelection` 의 `isAlreadyStarted`, `DashMainWindow.cpp:1188`)도 모델을 바인딩한다. 여기서 주입하지 않으면 Set 을 바꿔도 오버레이가 이전 Set 의 node set 목록을 계속 보인다 — 구독 제거의 대체가 불완전해진다 |
| 동작 변화 | 오버레이가 열린 채 전역 기준모델을 바꿔도 node set 목록이 실시간 갱신되지 않는다 — Set deck 고정이라는 종착 동작의 선반영. Start Morphing 재클릭이 갱신 경로다 |
| 검증 | Morphing Set 두 개를 번갈아 열어도 세션 내에서 각자의 deck 을 유지한다 · Start Morphing 후 오버레이 node set 목록이 핀된 deck 을 따른다 |

#### T15 — Condition·Morphing 의 Set 파일에 기준모델(`referenceModel`) 저장

> **구현 완료 — 후속 정정 있음.** backfill 출처(전역 → Set 자신의 DV `source`)·multi-source 처분(읽기 전용 보존 → 진입 시 1회 자동 분할)·D28 기계장치 제거는 **G12·T30** 소관("2026-09-21 개정 반영 절차" 절 · [Project-Manifest-Set-Identity-And-Decision-Revisions](Project-Manifest-Set-Identity-And-Decision-Revisions.md)). 아래는 구현 시점 스펙이다.

D14 스키마(uuid 조인 + path 병기 — D24)를 **Condition·Morphing 2모듈** {Set}.json 에 넣는다(CAD 는 키 없음 — #366 봉합, `cadSource` 는 D31 유보) — 키 읽기·쓰기·backfill·원장 해석이 디스크 포맷 한 몸이라 쪼개지 않고, 두 모델이 공유하는 `DashSetReferenceModel`(신설) 한 곳에 둔다. 구프로젝트의 multi-source Condition json 처분(핀 deck 외 `source` 행을 보존하되 읽기 전용)도 같은 티켓이다(문서 3 D15 절). 표시는 **모델 한 곳**이고(D28 개정 — #366 실측) 그 모델은 **`DashDesignVariableModel`** 이다 — `flags()` 에서 편집 플래그를 떼고 `data()` 에 `ForegroundRole`(`DashPalette::TextMuted`)·`ToolTipRole` 을 더한다. 핀 deck 은 `loadFromJsons` 의 기본값 있는 인자로 넘겨 호출별로 스코프하므로 공유 모델에 상태가 남지 않고 Geometry·Launcher 호출부는 무변경이다. **`DashConditionParameterization` 은 대상이 아니다** — FE Condition 표의 행은 `refreshFromLoadedAnalysis` 로만 생기는데 T16 이후 진입이 핀 deck 하나만 적재해 핀 deck 밖 `source` 행이 성립하지 않는다. 구 json 의 multi-source 행이 보이고 인라인 편집이 `saveToJsonFiles()` 로 되써지는 자리는 DV-Condition 탭이다(문서 3 D15 절 "표시").

| 채움 경로(D13) | 자리 |
|---|---|
| 신규 Set — Condition | `DashProject::createNewSet`(`DashProject.cpp:705`, Condition `:724-728`)이 생성 직후 그 시점의 전역 `referenceFilePath()` 를 핀 |
| 신규 Set — Morphing | 좌표 9 의 Start Morphing 핀(T14)이 그 자리다 — 유일한 데이터 주입 지점이라 그 시점 핀이 곧 생성 시점 핀 |
| 기존 Set 복원 | `loadFromJson` **2곳**이 키를 읽어 핀 — Condition(`:405`) · Morphing(`DashGeometryParameter.cpp:127`). 생성자·`setSetName` 경로가 부른다. CAD(`:376`)는 키가 없어 제외(#366 봉합) |
| 구버전 backfill(D15) | 키 부재 시 위젯 진입(`setModel`)에서 전역을 1회 핀(구버전 한정). Morphing 은 Start Morphing 핀이 겸한다. 다음 저장이 키를 만든다 |

| 쓰기(실측 · 해소 필요 사항 2 확정) | 자리 |
|---|---|
| Condition | `saveDvCondition`(CondPM `:117-141`) — `saveSettings`(`:212`)는 qDebug 빈 스텁·호출부 0 이라 대상 아님 |
| CAD | 대상 아님(#366 봉합) — `saveDvGeometry`(CADPM `:55-79`)에 키를 얹지 않는다. `saveSettings`(`:117`)는 빈 스텁이라는 실측은 유지 |
| Morphing | `DashGeometryParameterPresentationModel::saveMorphingSettings`(`:326`)가 유일 라이터, 호출자 `DashGeometryParameterWidget.cpp:1186` |

| | |
|---|---|
| 파일 | `model/DashSetReferenceModel.h`·`.cpp`(신설) · Condition·Morphing 모델 h/cpp 4 · `DashProject.cpp` · PM 2(`DashConditionParameterizationPresentationModel.cpp`·`DashGeometryParameterPresentationModel.cpp` — 쓰기 표의 실 라이터 2종) · Condition 위젯 |
| D16 해석 (재개정) | 키를 읽을 때 — uuid 로 원장 직조회(D24) → 히트 시 `path` 의 파일 존재·적재 검사(부재면 미지정 + 로그) → 미스면 path 로 원장 스캔(원장 유실·구버전 한정, 찾으면 uuid backfill + 같은 존재 검사) → 둘 다 실패면 미지정 + 로그 |
| 안 하는 것 | 위젯 읽기 교체 — 좌표 1·2·9 는 이 티켓 시점엔 여전히 전역을 읽는다(다음 티켓 T16). 스키마 버전 증가 없음 — 키 부재가 구버전 판정이다(D14) |
| 과도기 | 이 티켓 시점에 {Set}.json 은 Set 의 deck 을 기록하는데 화면은 전역을 따른다. 같은 PR 의 T16 이 닫아 **PR 밖으로 노출되지 않는다** |
| 검증 | 신규 Set 생성 → {Set}.json 에 그 시점 전역이 `referenceModel` 로 남는다 · 구프로젝트 Set 진입 → 다음 저장 후 키가 생긴다(D15) · `path` 를 원장에 없는 값으로 손편집 → 진입 시 미지정 + 로그, 그 deck 재Load 후 재진입 시 회복(D16) · 이 티켓의 화면 동작 변화 0 |
| 검토 포인트 | 라이터 `saveDvCondition`(CondPM `:117-141`)·`saveMorphingSettings` 둘 다 read-merge-write 라 다른 경로가 쓴 키를 지우지 않는다 — 본문 확인(#366 이 `saveDvGeometry` 포함 3종 전부 재확인). 새 라이터를 만들면 안 된다 |

문서 3 검증 한계의 "{Set}.json 라이터 좌표 미실측" 은 이 문서에서 실측해 닫았다.

#### T16 — 화면 진입 시 Set 저장값을 읽게 전환 + CAD 최소 정리(봉합)

> **구현 완료 — 후속 정정 있음.** backfill 의 전역 읽기가 D15 재개정으로 Set 자신의 DV `source` 유도(전역은 폴백)로 바뀐다 — **G12·T30** 소관("2026-09-21 개정 반영 절차" 절). 아래는 구현 시점 스펙이다.

| 좌표 | 자리 | 처분 |
|---|---|---|
| 1 | `DashConditionParameterizationWidget.cpp:313-315` | 출처를 전역 `referenceAbsolutePath()` 에서 모델 보관값(절대 해석)으로. 전역 읽기는 backfill(구버전) 경로에만 남는다 |
| 2 | `DashGeometryParameterCADWidget.cpp:345-347` | **죽은 전역 읽기 제거로 끝**(#366 봉합) — 대체할 Set 키가 없다. CAD 의 키는 D31 유보 |
| 9 | `DashMainWindow.cpp:3181` | Start Morphing 핀에 가드 — 모델이 이미 핀을 들면(복원·backfill) 덮지 않는다. 전역 읽기는 미핀(신규·구버전)일 때만. 파트-핀 미스매치 가드 동승 — `selectedPartName` 이 핀 deck 에 없으면 **경고 후 중단**(문서 3 해소 필요 사항 6) |
| — | `DashMainWindow.cpp` 시그널 배선 | **과도기 연결 제거** — `referenceModelChanged` → `m_conditionParameterizationWidget->refreshFromFile(...)`(PR #389 `f1a859d`)를 지운다. Set 키 읽기가 대체한다 |
| — | `DashMainWindow.cpp:623` | **생성 가드에서 CAD variant 제외**(M5 · #366 봉합 — 판정은 `DashProject.cpp:709` 와 동일 `variant == "CAD" \|\| "cad"`) — #389 `c3072bc` 회귀(CAD Set 생성이 무관한 해석 deck 을 요구)가 닫힌다. Condition·Morphing 은 전역 요구 유지 |

| | |
|---|---|
| 동작 변화 | Set 의 deck 이 생성 시점 고정이 된다 — 진입 시점의 전역이 Set 의 deck 을 정하던 현행 체감이 사라진다(의도된 종착). 과도기 동작 1("Set 먼저 클릭, Load 나중")이 T15 의 backfill 과 함께 닫히고, **과도기 동작 3**(Load 마다 표 갱신·쌓기)이 여기서 닫힌다 — 대체재인 DOE 다중 선택(T24 — 같은 G8)이 함께 나간다 |
| 검증 | Set A(deck X)·Set B(deck Y)를 번갈아 진입해도 각자 deck 유지 — **재기동 후에도** · 전역 기준모델을 바꾼 뒤 기존 Set 재진입 시 deck 이 안 바뀐다 · 신규 Set 은 생성 시점 전역을 받는다 |

#### T19 — Parameters 도크 제목에 Set 의 기준모델 파일명

`m_rightDock`(`DashMainWindow.cpp:464`, 리터럴 고정 — 갱신 지점 0건)의 제목에 Set 진입(모델 바인딩) 시 소유 모델의 deck 파일명을 붙이고, 미지정이면 기본 "Parameters". 선례 `m_leftDock->setWindowTitle(...)`(`:3008`·`:3068`).

이 티켓의 표시는 **앞단 2모듈(Condition·Morphing)** 이다 — CAD(#366 봉합 — 표시할 해석 deck 이 없다)·Launcher·파이프라인 후단 4모듈·비소유 모듈 진입 시 기본 "Parameters" 로 복귀한다. **Launcher 표기는 T20(G8)으로 옮겼다** — 읽는 `parameterization` 스키마와 같은 티켓이라야 G7 이 G8 의 키를 앞서 읽지 않는다. 표기 형태(`{형상 deck 파일명} +{조건 Set 수}` · 단일 deck 접미 생략 · 빈 값 기본 복귀)는 D17 그대로다(문서 3 해소 필요 사항 4).

D7(Mesh View 도크 = 렌더 파일명, T7)과 짝이다 — 렌더와 기준이 다른 상태가 두 제목줄로 드러난다. 파일 1개짜리라 같은 PR 에서 T16 뒤에 붙는다.

### G8 — DOE 다중 선택 · Launcher 조합 기록 · 화면 출처 교체 (재절단: 발행 2건)

**재절단 (2026-09-20)** — 발행 3건이었고, 그중 #502(T26 루프)가 2026-09-22 범위 밖으로 확정돼 발행 2건이다. G7(T16)이 없앤 "Condition 표의 deck 쌓기"의 대체 경로는 T24\~T26 인데, 그 전부가 아니라 **정합성 갈래만이 dev 2회차의 최소 단위**임이 실측으로 확인돼 아래처럼 갈랐다. 구판 단일 PR(T20 → T24 → T25 → T26 → T17)은 폐기.

**#491 은 dev 반영 완료(#507 — 2회차), #367 은 구현 완료·통합 브랜치 머지(#510 — dev 3회차 대기)다. 후속 정정 (2026-09-21)** — T25 의 열별 `{set, key}` 와 T20 의 `parameterization` 조인(둘 다 이름 키로 구현)은 setId + `name` 병기로 전환된다(SI-4). setId 도입(SI-1\~SI-3)이 선행이라 **G11(T28·T29 — "2026-09-21 개정 반영 절차" 절)** 로 한 묶음 처리한다 — 원문은 [Project-Manifest-Set-Identity-And-Decision-Revisions](Project-Manifest-Set-Identity-And-Decision-Revisions.md). 구 기록(`{set: 이름}` Table · 이름 키 parameterization)은 기록된 대로 해석 — 이름 폴백, 재기록 없음.

| 발행 | 티켓 | 범위 | 선행 | dev 제약 |
|---|---|---|---|---|
| **#491** | T24 · T25 · T26 치환부 | 조건 세트 다중 선택 UI + 변수 합산·접두·D27 차단 + 저장 형식·읽기 코드·열 `{set, key}` + 실행 시 해당 세트의 변수만 값 치환·morph 매칭 전환 | G7 | **#366 "같은 dev 반영 회차" 를 단독 승계** — 2회차 최소 단위의 끝 |
| **#367** (구현 완료 — #510) | T20 · T17 | `parameterization` 조합 기록 + 도크 Launcher 표기 + 화면 데이터 출처 교체(목록 파일 콤보 · `source` 상대경로 · `getMorphingSourceInfo`) | #491(T20 채움 지점) · G7(T17 이 T15 요구) | 없음 — 점진 |

**사실관계 (2026-09-20 실측)** — 재절단의 근거가 된 as-is:
- 자동 루프는 원래 없던 로직이다 — Reference File 라디오가 단일 선택이라(`getSelectedReferenceFiles` `DashReferenceFileWidget.cpp:101-130`) `generateInputCases` 의 `.first()`(`DashJobRunner.cpp:1290`)는 실질 무손실. 다중 deck 은 라디오 전환 + 재실행(수동)이었다
- 쌓인 타 deck DV 는 설계된 필터가 아니라 적용 단계 매칭 실패로 걸러졌다 — `rwApplyConditionDvs` WARN+skip, uuid 미스 시 이름 폴백(`DashMorphingDoeExecutor.cpp:446`)의 타 deck 오적용 위험 동반(D28 방어 계열)
- 접두 도입 시 실행기의 bare 이름 조회(`attachConditionDvValues` `:511-513` · `updateHandlesWithDoeValues` `:1099-1102`)는 **경고 없이 전부 미스** — 조건 DV 무적용 산출물이 나온다

**설계 결정**:
- **정합성과 편의를 가른다** — 치환 스코프(정합성)는 #491 이 담고, 루프(편의 자동화)는 범위 밖이다("T26 루프 — 범위 밖" 절). 루프 없이도 수동 라디오 워크플로우가 옳은 결과를 낸다 = 문서 0 D8 "현행과 같게". 구판 "T25·T26 을 PR 로 가르지 않는다(중간 상태가 틀린 결과)" 논거는 치환부의 #491 동승으로 해소 — 이 절단이 대체한다
- **#491 이 한 덩어리인 이유** — T24 단독이면 접두 헤더가 bare 매칭에서 조용히 전부 미스(위 사실관계 3)이고 2원소 배열이 N 선택을 못 담는다. 셋 중 하나가 빠진 중간 상태가 전부 틀린 결과다
- **티켓 순서 역전** — 구판 "스키마(T20)가 먼저" → T24 가 먼저 가고, T20 은 후행에서 채움 지점(DOE 선택 핸들러)을 재개봉한다. T20 없는 동안 선택은 DOE 설정과 DOE Table 에만 남는다
- **치환 스코프 규칙** — run 대상 deck = 라디오 선택 템플릿 1개. 소속 판정 = 열 `{set}` 의 `referenceModel.uuid`(T15) == 템플릿 deck uuid(원장 경유). deck 공유 Set 은 같은 run 에 함께 적용(D23) — bare 겹침은 T24 의 D27 차단이 선방어. 일치 0건이면 조건 DV 0건 + 경고 로그(D21 — 실행은 막지 않는다). **접두 문자열 파싱 금지** — 조인은 `{set, key}` 메타데이터, 접두는 표시 전용(Set·DV 이름의 `.` 오염)

#### T24 — 조건 세트 다중 선택 UI + 변수 합산 + 세트 이름 접두 (#491)

| | |
|---|---|
| 파일 | `view/DashAnalysisLauncherWidget.*` · Resample 위젯 · `model/DashDoeConfigManager.cpp` |
| 하는 것 | Init DOE·Resample DOE 의 `dvConditionCombo`(`DashAnalysisLauncherWidget.cpp:511-518`)를 **체크 가능 콤보**로 — 닫힌 상태는 "N Sets selected". 선택 Set 들의 DV 합산은 `loadFromJsons(QStringList, dir)` 에 목록을 늘리면 된다(`DashDesignVariableModel.cpp:313-352` — 이미 복수 파일을 append 한다). DV 표시·`headers` 이름에 `{Set 이름}.` 접두를 붙인다(`DashDoeConfigManager.cpp:206-236` 의 `spec.label` 자리). **deck 공유 Set 간 겹침 차단** — 체크된 Set 들에서 같은 deck(uuid)을 공유하는 조합의 체크 DV bare 이름이 겹치면 선택을 거부하고 안내한다(D27 · D20 문형) — 한 run 으로 합쳐질 같은 `${토큰}` 에 두 값이 경합한다 |
| 안 하는 것 | Geometry 콤보의 다중 선택 — 형상은 조합 전체에 1개다(D25) |
| 검증 | Set 2개 선택 → 표에 두 Set 의 DV 가 합산되고 이름이 접두로 구분된다 · 단독 선택과 다중 선택의 DV 이름이 같다 · 같은 deck 의 Set 2개가 같은 bare DV 를 체크한 상태의 동시 선택이 차단된다 |

#### T25 — 다중 선택의 저장 형식과 읽기 코드 (#491)

| | |
|---|---|
| 파일 | `model/DashAnalysisLauncher.cpp` · `model/DashDataProcessor.cpp` |
| 하는 것 | `"Selected Design Variables"` 가 **2원소 배열**[condition, geometry]이고(`DashAnalysisLauncher.cpp:1140-1143`) Preprocessor 가 그것을 위치로 읽는다(`DashDataProcessor.cpp:2800-2830`). geometry 1 + conditions N 을 담는 형태로 바꾸고 **판독기를 같은 티켓에서** 고친다 — 가르면 디스크에 두 포맷이 공존한다. 저장된 선택은 후행 T20(#367)의 `parameterization.conditions` 와 같은 내용을 가리키게 된다 |
| DV 열의 Set 참조 | DOE Table 이 지금 드는 열 정보는 `headers`(이름)와 `source`(deck\|part 라벨)뿐이라 **어느 Set 에서 온 DV 인지가 없다** — 같은 deck 을 쓰는 Condition Set 이 둘이면 `source` 로 구별되지 않는다. 열마다 Set 참조를 함께 기록한다(D27 의 `{set, key}`). T26 의 치환·morph 매칭과 Preprocessor 판독기가 이 값을 읽는다 — 접두 문자열을 다시 쪼개 쓰면 이름 기반으로 되돌아간다 |
| resample 호환 | resample 은 참조 Set 의 `headers` 로 prior sample 을 평평화한다(`DashAnalysisLauncher.cpp:115-125`). 참조 Set 이 접두 없는 구 Table 이면 새 이름과 안 맞아 prior 가 통째로 버려진다 — 구 Table 의 열은 그 Set 의 단일 Condition Set 접두를 붙여 해석한다 |
| 구버전 | 2원소 배열을 읽는 경로는 남긴다 — 구프로젝트의 DOE 설정이 그 형태다 |
| 검증 | 다중 선택 후 재기동 → 선택이 복원된다 · 구프로젝트 DOE 설정이 그대로 열린다 · Preprocessor 가 새 포맷의 DV 를 옳은 소스 파일에 매핑한다 · **같은 deck 을 쓰는 Condition Set 2개를 골라도 열이 Set 별로 구분된다** · 구 Table 을 참조 Set 으로 한 resample 이 prior 를 잃지 않는다 |

#### T26 치환부 — 실행 시 해당 세트의 변수만 값 치환 (#491)

| | |
|---|---|
| 파일 | `model/DashJobRunner.cpp`(`writeCaseDat` — `.first()` 는 유지) · `controller/DashMorphingDoeExecutor.cpp` |
| 하는 것 | 치환 — `writeCaseDat` 의 headers 전수 순회(`:468-474`)를 **run 대상 deck(라디오 선택 템플릿)을 공유하는 Set 들의 DV 로 한정**하고 접두를 뗀 bare key 로 친다. 소속 판정은 T25 의 열별 `{set, key}` → `referenceModel.uuid`. **morph 매칭 전환 동승** — `DashMorphingDoeExecutor` 가 headers 를 bare 이름과 문자열 매칭하는 두 곳(형상 핸들 `updateHandlesWithDoeValues` `:1099-1102` · 조건 DV `attachConditionDvValues` `:511-513`)을 열별 `{set, key}` 해석으로 바꾼다 — 그대로 두면 접두 headers 가 전부 미스라 형상 morph 와 조건 DV 부착이 통째로 죽는다(D27 동반 수정 3건째). 일치 Set 0건(조합 밖 deck 선택)이면 조건 DV 0건 + 경고 로그 |
| 왜 한정이 필요한가 | 전수 순회면 접두 이름은 어느 템플릿에도 안 맞아 치환이 통째로 죽는다. 접두를 그냥 떼기만 하면 다른 deck 의 같은 이름 DV 에서 앞 열 값이 양쪽 deck 에 박힌다 — deck 필터와 접두 제거는 한 쌍이고, 같은 deck 안의 겹침은 T24 가 선택 시 차단한다 |
| 검증 | 다른 deck 의 Set 2개 선택 → 라디오 A 실행 시 A 소속 DV 만 치환, 라디오 B 전환 재실행 시 B 값 치환(파일 확인) · 같은 deck 의 Set 2개 선택 → 한 run 의 case 파일에 두 Set 의 DV 가 함께 치환된다(파일 확인) · **다른 deck 의 같은 DV 이름에서 각 run 이 자기 Set 값으로 치환된다**(파일 확인) · 접두 headers 로 형상 morph 와 조건 DV 부착이 동작한다 · 조합 밖 deck 선택 시 경고 로그 + 조건 DV 0건 |

#### T26 루프 — 범위 밖 (2026-09-22 확정)

**실행 1회로 해석파일별 자동 반복 실행(구 #502)은 착수하지 않는다.** `generateInputCases` 의 `.first()`(`DashJobRunner.cpp:1290`)는 그대로 둔다 — 다중 deck 은 Reference File 라디오 전환 + 재실행(수동)이 현행이고, 위 사실관계 1 대로 실질 무손실이다. 편의 자동화라 결과 정합성에 걸리는 것이 없고(D8 "현행과 같게"), 착수 게이트였던 라디오 처분 문제 — 루프가 조합에서 deck 을 도출하면 라디오의 "실행 템플릿 지정" 역할과 겹친다 — 도 함께 닫힌다. 이 판단을 뒤집으려면 별개 이슈로 새로 발행한다.

#### T20 — Launcher 에 형상·조건 세트 조합 저장 (#367)

> **구현 완료(#510 — 통합 브랜치 머지, dev 3회차 대기) — 후속 정정 있음.** `parameterization` 의 Set 조인이 이름 키로 구현됐다 — setId + `name` 병기 전환(SI-4)은 **G11·T29** 소관. as-built 차이 — 구버전 backfill 생략(키 없는 옛 파일은 empty 로 열리고 첫 DOE 선택이 기록을 만든다 — #510 결정). 아래는 발행 시점 스펙이다.

당시에는 파이프라인 조합 스탬프의 원천으로 계획했다. 현재 후속은 #368·#685의 개별 Set 참조·실제 출처 기록이며 아래 T20은 완료 당시 발행 기록이다.

| | |
|---|---|
| 파일 | `model/DashAnalysisLauncher.h`·`.cpp` · `model/DashProject.cpp`(생성 핸들러) · `view/DashAnalysisLauncherWidget.cpp`(#491 의 DOE 선택 핸들러에 채움 연결) · `view/DashMainWindow.cpp`(Parameters 도크 Launcher 표기) |
| 하는 것 | `AnalysisLauncher_{Set}.json` 에 `parameterization` 키 신설 — `geometry` 객체 1개 + Condition Set 키의 `conditions` 맵(D23·D25), 각 항목이 `{deck{uuid, path}}`. deck uuid 는 각 Set 의 `referenceModel`(T15)에서 전사한다. 스키마·쓰기·읽기·구버전 backfill 이 한 몸이라 쪼개지 않는다. 검증은 없다(D21) — `input_files` 라디오 선택은 자유이고 조합을 바꾸지 않는다. **Parameters 도크 제목의 Launcher 표기 동승**(T19 에서 이동 — D17) — `{geometry.deck 파일명} +{조건 Set 수}`, 단일 deck(조건 Set 1개 = 형상 deck, uuid 비교)이면 접미 생략, `parameterization` 이 비면 기본 "Parameters" |
| **핀이 아니다** | 값을 채우는 것은 DOE 선택(#491 T24)이고 선택이 바뀌면 다시 쓴다 — **#491 이 먼저 들어가 있어 채움 지점(선택 핸들러)을 재개봉한다.** Launcher Set 생성 시점에 핀할 값이 없다 — `createNewSet` 은 variant 만 쓰고(`DashProject.cpp:592`) DV 선택은 위젯 콤보에서 온다. **D18 의 "Launcher = 생성 시점 커서 핀" 을 이 티켓이 대체한다**(D18 부속) — Launcher 는 `referenceModel` 키를 두지 않고 기준 deck 을 `parameterization.geometry.deck` 으로 든다 |
| 표현 근거 | 형상은 조합 전체에 1개다 — 모든 기준 deck 의 형상이 같고 해석조건만 다르다는 전제. 평평한 튜플(배열 위치 조인)과 deck 당 묶음(형상 N번 중복) 둘 다 배제(D25) |
| Set 참조 | Set 이름(구현 시점 — #510). setId + `name` 병기 전환(SI-4 — D25 재개정)은 G11·T29 소관. 당시 조합 id 발급 계획은 폐기됐고 T27은 실제 출처 기록으로 개정 |
| 안 하는 것 | `input_files[].path` 에 uuid 병기(범위 제외) · 실행 차단 · 당시 조합 id 계산(현재 폐기) |
| 검증 | DOE 선택 후 {Set}.json 에 조합이 남는다 · 선택을 바꾸면 다시 쓰인다 · 조합과 다른 변종 deck 을 골라 실행해도 허용되고 기록이 유지된다 · 구프로젝트 진입 → backfill · Parameters 도크 제목이 Launcher 표기를 띄운다(선택 전 기본값) |

#### T17 — Launcher 화면의 데이터 출처를 목록 파일·Set 저장값으로 교체 (#367)

> **구현 완료(#510).** as-built 상세·동작 변화 3건(Start Morphing 입구 정렬 · morphing 덱 원본 우선 · geometry 콤보 index 0 결함 수정)과 follow-up 후보는 PR #510 본문이 갖는다.

| 갈래 | 처분 |
|---|---|
| Reference File 콤보 | deck(`.dat`·`.inp`) 후보를 원장 조회로. 원장 밖 확장자(`.stli`·`.wbpj`·`.cdb`·`.dfsxml`)는 후속작업 2 까지 스캔 유지 — 콤보는 두 소스의 합(문서 1 6절) |
| DV `source` | bare filename → 프로젝트 루트 상대경로(= 원장 `path` 필드). **조인·검증 키는 `referenceModel.uuid`**(D24)이고 `source` 는 표시·재해석용 경로로 남는다. 쓰는 자리는 `buildDvGeometry`(`DashGeometryParameterPresentationModel.cpp:107`), 읽는 재해석 4곳과 `findAnalysisFiles` 파일명 dedup 을 같은 티켓에서 교체(문서 1 8절) — 쓰기·읽기를 가르면 디스크에 두 표현이 공존한다 |
| `getMorphingSourceInfo` | `DashReferenceFileWidget.cpp:543-604` 가 Launcher JSON 에 존재하지 않는 섹션을 읽어 항상 빈 값 — **Launcher 자기 `parameterization`(T20) 조회로 교체**(문서 3 해소 필요 사항 5). deck 이 N 개이므로 추천·매칭의 기준은 **`geometry.deck`** 이다 — morph 원본이 그것이고 형상은 조합 전체에 하나다(D25). deck 추천 = 그 파일명, part 매칭 = 그 deck 의 파트. Geometry Set 특정이 필요한 자리는 referenceModel 일치 필터. 무작동이던 deck 자동 추천·part 노드수 매칭(`:617`·`:637`·`:869`)이 살아난다 |

| | |
|---|---|
| 묶은 근거 | 세 갈래 동승. 전부 "모듈이 가리키는 값의 출처 교체" 한 종류다(마스터 순서 절). 갈래별 분리 |
| 검증 | 콤보의 deck 후보 = 원장 항목(원장 밖 확장자는 스캔분 유지) · deck 자동 추천·part 매칭이 동작한다(현행 무작동 → 부활) · 새로 저장된 DV `source` 가 상대경로이고 DOE 실행이 그 값을 해석한다 · 구 JSON 의 bare filename 도 계속 열린다 |
| 검토 포인트 | 구형 bare filename 읽기 호환이 남아야 한다 — 구프로젝트의 DV `source` 는 이 PR 뒤에도 bare 다 |

### G9·#368 — 생산 측 출처 기록과 공통 판독 계약

완료된 #520의 `setId` 발급·영속·복원·역조회와 #367·#491의 선택 기록을 사용한다. `parameterizationId` 생성·전파·비교와 최초 입력 영구 핀은 폐기한다. 이 작업의 완료 지점은 Builder `model_info.json`과 공통 기록·판독 계약까지이며 T23 소비는 #685다.

| 항목 | 계약 |
|---|---|
| 티켓 순서 | T27 Sampler·Launcher 생산 → T21 dataset 검증·전달 → T22 Builder 생산·공통 계약 |
| 입력 변경 | 현재 Set 자체의 ID를 유지하며 기존 선택 UI에서 상류 입력 Set을 다른 `setId`로 바꿀 수 있음. 데이터셋·응답·모델·part 등 세부 선택 유지 |
| 산출물 출처 | 실제 사용한 개별 Set ID·세부 선택·deck 정보를 기록. 현재 선택만 바뀌면 기존 출처는 유지하고 재실행 덮어쓰기 때 실제 출처도 함께 갱신 |
| 구산출물 | 필수 출처가 없으면 재생성. 이름·경로 추론이나 자동 마이그레이션으로 출처를 채우지 않음. 기존 Set ID 복원 유지 |
| 범위 밖 | 별도 Set 원장·산출물/소비 이력 대장, 과거 전체 이력 보존, 버전·최신성(#650). 세부 직렬화 키는 이 문서에서 새로 확정하지 않음 |

#### T27 — Sampler·Launcher 실제 입력 출처 기록

| 항목 | 내용 |
|---|---|
| 구현 접점 | 당시 `DashAnalysisLauncher`·`DashDoeConfigManager`와 DOE 기록 경로를 근거로 현재 Sampler·Launcher 분리 구조의 실제 쓰기 지점을 확인 |
| 현재 참조 | Sampler는 Geometry·Condition Parameterization Set ID, Launcher는 Sampler Set ID를 저장·복원 |
| 생성 기록 | 실행에 실제 사용한 선택·개별 Set·deck 출처를 산출물에 기록. 편집 중인 라이브 설정을 옛 산출물 출처로 대체하지 않음 |
| 저장 경계 | DOE Table 전면 재기록과 남아 있는 옛 run 폴더는 당시 실측 사실. 새 Table이 옛 run의 출처를 바꾸지 않도록 산출물과 기록을 대응시키며 실제 재생성분만 함께 갱신 |
| 검증 | 다른 상류 ID로 전환해도 현재 Set ID 유지, 선택만 변경 시 기존 출처 불변, 재실행 덮어쓰기 시 실제 출처 동반 갱신. 동명 재생성 Set으로 자동 연결되지 않음 |

#### T21 — dataset 입력 출처 검증·전달

| 항목 | 내용 |
|---|---|
| 구현 접점 | `DashDataProcessor`·dataset XML 생성 경로. 당시 source 치환(`DashDataProcessor.cpp:2825-2838`)은 실측 근거이며 새 출처 판독의 대체물이 아님 |
| 하는 것 | 실제 해석 결과의 Launcher 출처와 세부 입력을 공통 계약으로 검증해 dataset에 전달. 최초 연결 조합 핀·문자열 ID 비교를 추가하지 않음 |
| 구버전 | 필수 출처가 없으면 사용 차단·재생성 안내. 구포맷을 읽을 수 있다는 이유로 출처 검증을 생략하지 않음 |
| 검증 | 유효한 입력 전환·전달, 서로 다른 조건 deck의 정상 입력 처리, 필수 출처 누락 및 선택과 출처 불일치 차단, 현재 설정으로 과거 출처를 덮지 않음 |

#### T22 — Builder 입력 참조·검증·model_info 출처 기록

| 항목 | 내용 |
|---|---|
| 구현 접점 | `DashModelBuilder`의 dataset 판독·`model_info.json` 생성. 당시 `model_info` 섹션 전사(`:545-556`·`:1565-1620`) 경로를 기준으로 확인 |
| 하는 것 | 데이터셋을 생성한 Launcher Set을 `setId`로 참조하고 데이터셋·응답 선택과 출처를 검증. 실제 출처를 Builder 산출물에 기록하고 #685가 재사용할 공통 판독 계약 제공 |
| 입력 변경 | Launcher 참조를 다른 ID로 바꿔도 Builder 자신의 ID 유지. 새 입력으로 학습 산출물을 덮어쓸 때 출처도 함께 갱신 |
| 메타데이터 | 출처 필드가 학습 parameter·응답 키로 오인되지 않도록 XML 전사와 `loadLabelMetadata` 소비 경계를 검증. 직렬화 키는 공통 계약에서 정의 |
| MCU | 기존 CSV 학습·deck 비사용 경로 보존. 출처 필수인 경로를 MCU 예외로 우회하지 않음. 적용 경계는 계약에 명시 |
| 검증 | 새 Launcher 입력의 정상 사용, `model_info.json`과 실제 입력 일치, 필수 출처 누락 차단·재생성 안내, 기존 MCU 학습 영향 확인 |

### #685·T23 — Runner·Optimizer Builder 참조·소비 전환

#368 선행, #443 하위 관계를 유지한다. 생산 형식을 중복 정의하지 않으며 #681의 머지 조건으로 두지 않는다.

| 항목 | 내용 |
|---|---|
| 구현 접점 | `DashModelRunner`·`DashOptimizer`·프리뷰 위젯. 당시 `m_viewSourceContext` 대입·`loadModelInfoFromFolder`·configs 전수 스캔 좌표는 착수 시 재확인 |
| 참조 | Builder를 `setId`로 저장·복원. 현재 Runner·Optimizer ID를 유지하며 Builder 참조를 다른 ID로 바꾸고 모델·응답·part 세부 선택 유지 |
| 소비 | #368 공통 계약으로 선택과 산출물 출처 검증. 실행·조회·프리뷰에 같은 해석 결과 사용. 외부 실행에는 ID로 해석한 실제 경로 전달 |
| 프리뷰 | 출처로 검증한 형상 deck을 사용해 morph. configs의 무관 deck 전수 처리 제거. part 조회를 위해 라이브 Set을 읽더라도 ID를 확인하며 이름·경로로 누락 출처를 추론하지 않음 |
| 갱신 | 입력 선택만으로 기존 산출물 출처는 바꾸지 않고 재실행 덮어쓰기 때 실제 출처도 함께 갱신. 이전 전체 이력 보존 불요 |
| 검증 | 다른 Builder ID 선택·재열기, 현재 Set ID 유지, 동명 재생성 오연결 차단, 외부 실행 경로·조회·프리뷰 정합, 출처 없는 model_info 재생성 안내 |

### G10·T18 — 독립 #369 NodeSet 선택 저장·복원

2026-09-22에 이 매니페스트 묶음에서 제외한 이력은 유지한다. 2026-10-08의 현재 관계는 #443 부모에서 분리된 독립 Runner 선택 저장·복원 작업이며 #443·#368·#685의 선행이나 완료 조건이 아니다.

| 항목 | 내용 |
|---|---|
| 기존 설계 | 다이얼로그의 `nodeSetSource`를 저장·복원. 경로 직접 사용·존재 검사, 프로젝트 밖 파일은 안으로 복사 후 상대경로 저장. 빈 값은 콤보를 채운 deck 폴백 |
| 실측 배경 | `m_datFilePath`가 메모리에만 남고 `updateReferenceFileAndPart`가 초기화(`DashModelRunnerWidget.cpp:1020`). 빈 경로 morph 실패(`DashModelRunner.cpp:2206-2209`) |
| 검증 | 선택 후 재진입·재시작 복원, 프로젝트 이동 후 상대경로 해석, 루트 밖 파일 복사, 빈 값 폴백과 파일 부재 처리 |

### 별도 작업과 아직 반영하지 않은 후속 계획

#650은 생산 Set이 버전을 기록하고 소비 Set이 실제 사용한 입력 버전으로 최신성을 판정한다. Project는 호출·집계, VM은 표시를 담당한다. 버전 의미·비교 불가 상태·산식은 먼저 정의해야 하며 이 문서에서 확정하지 않는다.

#643의 저장 구조·이어쓰기, #615 자동 선택, #646 결과 교체 시점, #513 워커 이관과 #685의 공유 코드 순서 등은 [추가 개정 계획](Issue-Revision-History.md)의 미반영 팀 논의다. 연관 코드가 같다는 이유로 각 오류 수정에 전체 구조 전환을 선행으로 추가하지 않는다.

## 이 문서에서 나온 결정 1건

**D12(개정 — D24)** — displayed 커서는 프로젝트 루트 상대, reference 커서는 uuid(T10 전환). 표·근거·성립 조건·대가는 문서 0 의 D12 근거 절이 정본이다. 이 문서에 남는 함의는 **G2 의 선행이 G1** 이라는 것이다 — 렌더 커서 경로의 외부 소비자 5곳 중 3곳(좌표 1·2·4)이 T3·T4 에서 기준모델 층으로 떠난 뒤에야 상대경로 전환이 안전하고, 남는 비교 2곳은 T2 가 `isDisplaying()` 으로 감싼다.

## 검증 한계

| 항목 | 근거 강도 | 비고 |
|---|---|---|
| 좌표·파일 목록 | **강** | `dev` @ `c989257`. 출처는 문서 1·2. G7 좌표는 #366 이 2026-09-18 통합 브랜치에서 재실측(`:3271`→`:3181` · 주입 지점 `:1188` 추가). G8 실행 경로(라디오 단일 선택 · `.first()` · bare 매칭 · 이름 폴백 `:446`)는 2026-09-20 통합 브랜치에서 재실측 |
| 커서 API 등장 61건 / 9 파일 | **강** | API 별 전수 grep. `DashOcctViewWidget` 은 오탐이라 제외 |
| `activeFilePath()` 외부 호출부 5곳 | **강** | 전수 grep 재실측. `Instance().activeFilePath()` 한 줄 형태 2곳(`CondWidget:313`·`CADWidget:345`)이 초기 집계에서 빠졌었다 — 문서 1 의 소비자 전수표와 이제 일치한다. Registry 내부 사용은 `.cpp:55`·`:60`·`:61`·`:66`·`:70` |
| 쓰기 4곳이 루트 내부 | **중** | 각 호출부의 경로 출처를 따라갔다. 런타임 확인은 안 했다 |
| 트리 `UserRole` 이 raw 경로 | **강** | `DashModelingTreeWidget.cpp:248` `setData(filePath, Qt::UserRole)` |
| 10개 병합과 선행 관계 | **중** | 제안이다. PR 파일 수는 티켓별 파일 목록의 이름 dedup 합집합 — G5·G6·G8 은 티켓별 파일 목록이 개수만 있어 추정(`~`)이고, **실제 diff 줄 수는 재지 않았다**. T20\~T23 의 파일 목록은 문서 3 의 2026-09-13 재검증 좌표 기반 |
| dev 반영 2회 경계 | **중** | 결정이다. 1회차는 반영 완료(#389), 2회차 QA 시나리오는 재현하지 않았다 |
| {Set}.json 라이터·로더·생성 핸들러 좌표 | **강** | 이 문서에서 실측(`dev` @ `c989257`) — `saveSettings` 2곳 · `saveMorphingSettings` · `read/writeConfigFile` · `loadFromJson` 3곳 · `createNewSet`. 세 모듈 라이터의 read-merge-write 본문 확인. 문서 3 의 미실측 항목을 닫았다 |
| 검토 부담 등급 | — | 판단이다. 측정값이 아니다 |
| 되돌리기 등급 | **중** | 사용자 데이터·저장 포맷에 닿는지로 갈랐다. 실제 원복 절차는 세우지 않았다 |
| 각 티켓의 검증 항목 | **중** | 현행 UI 로 수행 가능한지 재현하지 않았다 — 세 문서 공통 한계다 |
| T3·T4 티켓 독립성 | **중** | 겹치는 파일이 `DashMainWindow.cpp` 하나이고 라인이 멀다는 판단이다. 같은 PR 의 티켓이라 충돌해도 해소 비용이 작다 |
| 빌드·실행 | **없음** | 정적 근거만 |
