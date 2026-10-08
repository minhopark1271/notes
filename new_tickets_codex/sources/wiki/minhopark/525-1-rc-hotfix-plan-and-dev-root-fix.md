# DOE 모핑 모듈-독립 실행 — rc 핫픽스 계획 + dev 근본 해소 스펙

> 관련 Issue: #525
> 참조: PR #406(`c9c9ded`, dev 2026-09-18 — 부분 해소), 매니페스트 티켓과는 무관([[Project-Manifest-4-Ticket-Slicing]] 범위 밖 확인)
> **성격**: 처분·계획 문서. rc 핫픽스 착수와 dev 근본 해소 발행의 출발점.
> 좌표 기준: rc = `origin/rc` @ `acf3788` · dev 계열 = `feat/reference-model-manifest` 작업 트리 (2026-09-22 실측)

## 결함 구조 — 모듈 개방 의존 3겹

#525 의 증상(모듈 미개방 세션에서 Launcher Start → 전 샘플 `Missing currentHandles or ug` 실패)은 한 겹이 아니라 3겹이다. 이슈 본문의 원인 좌표는 rc 와 정확히 일치하고, dev 는 #406 이 2겹만 풀었다.

| 겹 | rc | dev | 해소 커밋 |
|---|---|---|---|
| 핸들 polydata | live 핸들 null → 조용히 skip → 샘플별 WARN (직접 원인, `DashMorphingDoeExecutor.cpp:1060`) | 해소 — VTP 스냅샷 직접 읽기 + 실패 시 루프 전 ERROR 중단 (`:339-345`) | `c9180d3` |
| 고정점 마커 | live interaction 재계산 — surface null 이면 **에러 없이 마커 없이 진행** (`:781-795`) | 신 VTP 는 해소(마커 영속화). 구 VTP 는 모듈 개방 필요 — 명시 ERROR + 재저장 안내 | `9e42cc0` (+`0553b64`) |
| morph 볼륨 | `RunVolumeMorphing` 이 `GetInputVTU()` 무가드 소비 — null 역참조 **크래시 경로** (`DashManager.cpp:486` 갈래 2곳) | **미해소** — 같은 `m_inputVTU` 소비 (`DashManager.cpp:572`), null 가드·사유 전달만 있음 | 없음 |

`SetInputVTU` 호출처는 양쪽 모두 `DashGeometryParameterWidget::UpdateTargetGeometry` 한 곳(dev `:2159`)이다. 즉 기대 동작(모듈 개방 무관 실행)은 **dev 에도 아직 없다** — `c9180d3` 커밋 본문이 이 잔여를 명시적으로 범위 밖으로 남겼다.

핸들 복원 자체의 정당성 — VTP 는 페이로드 전부(포인트 + HandleType·GroupId·HandleNormal·L2G·Bound + `AllFixedVolumeIds`)를 싣고, rc 의 현행 계약이 이미 "실행 시 VTP 가 정본"(live 핸들을 VTP 로 덮고 실행 — `c9180d3` 이 고친 GUI 오염 버그의 원인)이며, DOE 조인 키(handle id·group id)는 VTP 와 DV-Geometry JSON 을 같은 Save 가 함께 쓴다. 스냅샷 복원은 가능하고 live 보다 옳다. **단 핸들만 고치면 실패 지점이 마커 무경고 통과 → 볼륨 크래시로 내려가 악화된다** — 3겹을 한 세트로 풀어야 한다.

## rc 핫픽스 계획 (A안 — 배치 진입 시 모듈 선행조건 재현)

**원칙: backmerge 최소 표면.** rc 는 추후 dev 로 backmerge 되므로, rc 가 건드리지 않은 영역은 dev 것이 무충돌로 들어온다. dev 기반영 내용(#406 트리오)을 rc 에 중복 반영하지 않고, rc 고유 변경을 신규 블록으로 격리해 최소로 좁힌다.

설계 기준은 "모듈-개방 세션에서 실행한 것과 동등한 결과"다. `SetInputVTU` 가 선형화·`InitializeHandlePicking`(핸들 그릇 + surface·NonDesign 구축)까지 해 주므로, 부트스트랩 하나로 3겹이 같이 풀리고 기존 복원·마커 코드가 무수정으로 동작한다.

| # | 변경 | 자리 | 형태 |
|---|---|---|---|
| 1 | 부트스트랩 — `GetMorphingHandles()` null 이면 `analysisContext` 파트 ug 로 `SetInputVTU` + Morphing JSON constraint 를 interaction 에 복원(`SetVisibleConstraintIds` 경로). `hpi->Show()` 는 부르지 않는다 | `MorphFromDoeSamples` 또는 `Execute` 진입부, condition-only 제외 | 신규 블록/함수로 격리 |
| 2 | 핸들 복원 실패 시 샘플 루프 전 ERROR + 즉시 중단 | `Execute` 복원 직후 | 가드 수 줄 |
| 3 | `RunVolumeMorphing` 입력 null 가드 (크래시 방어) | `DashManager.cpp:486` 갈래 2곳 | 가드 수 줄 |

구현 시 확인할 잔점 2건 — `InitializeHandlePicking` 의 `InitializePipeline` 이 null renderer 에 내성이 있는지, constraint 의 JSON nodeIds → surface cell id 변환을 위젯 `updateConstraintVisualization` 과 같은 코드로 태우는 것.

```
[준비] rc 에서 fix 브랜치 분기 (fix/525-doe-module-free)
   ▼

[구현] 변경 3건 — 커밋 1~2개 (부트스트랩 / 가드), revert 단위 유지
   │   ※ 커밋 메시지·코드 주석에 처분 명시:
   │     "#525 rc 핫픽스 — dev 근본 해소(볼륨 컨텍스트 소유권) 반영 시 드롭"
   ▼

[QA] 4 시나리오
   │   1. 새 세션 · 모듈 미개방 · Launcher Start → 전 샘플 성공 + 해석 입력 생성
   │   2. 모듈-개방 실행과 morph 산출물(.vtu/.dat) 동등 — constraint 있는 프로젝트 포함
   │   3. VTP 부재·손상 → 샘플 루프 전 ERROR 1줄 + 즉시 중단
   │   4. 기존 워크플로우(모듈 개방 후 실행) 회귀 없음
   ▼

[반영] rc PR 머지 → #525 에 "qc 대응 완료 + dev 근본 해소 링크" 코멘트
```

### backmerge 처분 규칙

| backmerge 시점 상황 | 처분 |
|---|---|
| dev 근본 해소 완료됨 | rc 조각 드롭 — 충돌 시 dev 측 채택 |
| dev 근본 해소 미완료 | rc 부트스트랩을 dev 구조(`Result` 반환·basis 분리)에 맞게 이식하고 근본 해소 작업에 승계 기록 |

이 규칙이 성립하려면 dev 근본 해소가 계획으로 먼저 존재해야 한다 — 아래 절이 그 스펙이다.

## dev 근본 해소 스펙 — 볼륨 컨텍스트 소유권 분리

#406(엔진 소유권 분리)이 엔진에서 한 일을 볼륨 쪽으로 확장하는 후속이다. 비자립분은 응집된 한 덩어리다 — 전부 입력 메시 하나에서 `SetInputVTU` 가 파생하고, 소비자가 3함수뿐이라 값 타입 하나로 추출 가능하다.

| 항목 | 내용 |
|---|---|
| 추출 대상 | `DashManager` 멤버 5종(`m_inputVTU`·`m_linearizedVTU`·`m_originalQuadraticCells`·`m_midNodeMap`·bound/step, `DashManager.cpp:295-326`) + 파생·소비 함수(`CreateLinearizedVTU` `:366` · `CreateRestoredQuadraticVTU` `:447` · `assembleVolumeMesh` `:519` · `RunVolumeMorphing` `:572`) — 볼륨 실행 컨텍스트 타입 신설, ~300줄 이동 |
| 실행기 전환 | 잔존 `Mgr()` 2곳(`DashMorphingDoeExecutor.cpp:625` ug 폴백 · `:928` morph 호출)이 컨텍스트를 인자로 받는다 |
| 구축 시점 | Start 진입 시 lazy — `analysisContext` 파트에서 구축. GUI 경로는 `SetInputVTU` 시 같은 타입을 만들어 보관(기존 동작 유지) |
| 소유자 | Launcher(UI·모델)가 아니라 실행기/요청 서비스 — 데이터 수명이 실행 요청과 같고 #506 승격 모델 갈래와 정합 |
| 잔여 | 구 VTP 의 legacy 마커 경로(interaction 채집)는 기존 정책(재저장 안내) 유지 |
| 회귀 반경 | 프리뷰·MeshQC·ModelRunner·Optimizer 단건까지 볼륨 상태 소비자 전부 — #406 과 같은 수순(테스트 동반) 필요. **rc 에 넣지 않는 근거** |

**프로젝트 열기 시 전량 로드는 배제한다.** 독립성은 소유권이 주는 것이지 로드 시점이 주는 것이 아니다 — deck 파싱·선형화가 무거워 열기 시간이 세트 수 × 덱 크기에 비례하고(같은 이유로 매니페스트 T11 도 열기 시 전량 파싱을 배제), 안 쓰는 세션의 메모리 상주와 열기 이후 변경의 무효화 문제가 새로 생긴다.

## 기각 대안

| 안 | 기각 사유 |
|---|---|
| #406 선두 3커밋(`0553b64`·`9e42cc0`·`c9180d3`) rc 체리픽 | 워크트리 시험으로 충돌 0 은 확인했으나, 단독으로는 증상 미해결(마커·볼륨 겹 잔존 — 구 VTP 는 명시 실패, 신 VTP 는 rc 무가드 볼륨에서 크래시)이고 backmerge 충돌 표면만 넓힌다 |
| 핸들 스냅샷화 단독 | 실패 지점이 조기 WARN → 마커 무경고 통과 → 볼륨 크래시로 내려가 악화 |
| 루프 전 중단 + "모듈을 먼저 여세요" 안내만 | 몇 줄로 끝나지만 기대(모듈 무관 실행) 미충족 — 워크어라운드의 안내화 |

## 검증 한계

| 항목 | 근거 강도 |
|---|---|
| 3겹 구조·좌표 (rc `acf3788` · dev 작업 트리) | 강 — 소스 전수 확인. interaction 소비는 rc 실행기 grep 전수(핸들 4 · 마커 2) |
| 트리오 체리픽 충돌 0 | 강 — 스크래치 워크트리에서 실제 수행 (빌드는 미수행) |
| A안의 모듈-개방 동등성 | 중 — `UpdateTargetGeometry`·`InitializeHandlePicking` 본문 확인 기반의 설계 판단. renderer null 내성·constraint 변환 2건은 구현 시 실측 |
| 빌드·런타임 | 없음 — 정적 근거만 |
