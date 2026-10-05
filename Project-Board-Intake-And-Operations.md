# 프로젝트 16 편입 스캔과 보드 운영 — 열린 이슈 56건 전수 분류 · 필드·뷰·자동화 설정 (2026-09-17)

> 관련 문서: [215-1-w10-f-design-decision-review-snapshot](215-1-w10-f-design-decision-review-snapshot.md) — 여기서 다룬 #279·#280·#281·#282 중 #281 을 뺀 셋이 본 문서의 폐기 14건에 포함된다 · [Backlog-Reclassification-And-Status](Backlog-Reclassification-And-Status.md) — 2026-09-15 백로그 상태 실측(항목 축), 본 문서는 보드 편입 축 · [Backlog-Issue-Publication-Plan](Backlog-Issue-Publication-Plan.md) — 미발행 백로그 28건을 보드에 올리는 발행 계획. 본 문서의 폐기 14건이 그 계획의 "부활" 11건을 만든다

> **좌표 기준**: 2026-09-17 실측. 조직 프로젝트 [refactoring (#16)](https://github.com/orgs/NumeRealWorks/projects/16) · `DashOpti_GUI` 열린 이슈 **56건** · 스캔 시점 프로젝트 소속 35항목.
>
> ✅ **2026-09-17 집행 완료.** 아래 분류에 따라 **A\~E 29건을 편입**했고(보드 70항목), `#63`·`#64` 를 `not_planned` 로 폐기했다. 라벨 축 정리는 1·2차까지 끝났고, 접근권(`dev-team`)·Iteration 필드·뷰 2건도 설정됐다. 집행 내역은 "편입 결과"·"2-3 접근권"·"2-4 라벨 축 정리"·"2-5 필드와 뷰 구성"·"조치 체크리스트" 에 있다. **아래 표의 라벨 이름은 스캔 시점 값**이라 그 뒤 개명·삭제된 것이 섞여 있다(`VTKRenderer` → `area:VTKRenderer`, `priority:*` 삭제 등).

## 배경 및 동기

`refactor/async-execution` 의 dev PR [#256](https://github.com/NumeRealWorks/DashOpti_GUI/pull/256) 이 머지 없이 닫히고 [#292](https://github.com/NumeRealWorks/DashOpti_GUI/pull/292)(rollback)가 W10-c 이후를 배제한 채 들어가면서, 프로젝트 16 의 `Done` 중 9건이 dev 에 존재하지 않는 상태로 남아 있었다. 그 9건과 같은 좌표를 본문에 박고 있던 `Deferred` 5건까지 **총 14건을 2026-09-17 에 `not_planned` + `Won't do` 로 폐기**하고 각 Issue 에 사유·코드 좌표를 코멘트로 고정했다.

폐기 후 프로젝트 16 에 남은 활성 항목은 6건뿐이다. 반면 저장소에는 열린 이슈가 56건 있다. **보드가 실제 작업량을 대표하지 못한다.** 이 문서는 두 가지를 정리한다.

- **1부** — 열린 이슈 56건을 전수 훑어 프로젝트 16 편입 여부를 근거 강도순으로 분류
- **2부** — 보드 운영: 자동 편입, 팀원에게 공유할 규칙, 접근권, 라벨 축, 필드·뷰 구성(주 단위 추적 포함)

---

# 1부. 편입 검토 — 열린 이슈 56건 전수 분류

## 스캔 결과

| 구분 | 건수 | 권고 | 집행 |
|---|---:|---|---|
| 프로젝트 16 소속 | 6 | — | — |
| **A** 분할 그룹이 갈려 있음 | 5 | 편입 확실 | ✅ 편입 |
| **B** 리팩터 트랙 본류 | 11 | 편입 유력 | ✅ 편입 |
| **C** `split-group:413` | 5 | 그룹 단위 판단 | ✅ 편입 |
| **D** `split-group:318` 잔여 | 2 | 그룹 단위 판단 | ✅ 편입 |
| **E** 인프라·개발환경 | 6 | 축이 다름 — 별도 프로젝트 권고 | ✅ 편입 (권고 기각) |
| **F** 단발 결함·기능 | 21 | 편입 대상 아님 | 제외 · 그중 `#63`·`#64` 폐기 |
| 합계 | 56 | | 편입 29 · 폐기 2 |

> **E 는 권고와 다르게 편입했다.** 인프라·개발환경 축이 리팩터 트랙과 성격이 달라 프로젝트 분리를 권했으나, 한 보드에서 같이 굴리기로 결정됐다. 축이 섞이는 대가는 남아 있으므로 보드가 커지면 재검토 대상이다.

## 스캔 시점 프로젝트 16 소속 (6건)

| # | 라벨 | 제목 | 한 줄 |
|---|---|---|---|
| [#249](https://github.com/NumeRealWorks/DashOpti_GUI/issues/249) | refactor | NX CAD 파사드 완료 통지 일반화 | 요청 태그 왕복으로 `m_batchMode` 제거 |
| [#269](https://github.com/NumeRealWorks/DashOpti_GUI/issues/269) | refactor | DashJobRunner 워크플로 분기 해체 | `generateInputCases` 562줄 · 워크플로 4종 분리 |
| [#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281) | refactor, split-group:215 | W10-f-2b 단건 모핑 워커화 | 폐기 대상이었으나 되살림 — [#403](https://github.com/NumeRealWorks/DashOpti_GUI/issues/403)·PR [#406](https://github.com/NumeRealWorks/DashOpti_GUI/pull/406) 이 결합 ⑴⑵ 승계 |
| [#364](https://github.com/NumeRealWorks/DashOpti_GUI/issues/364) | feature, split-group:360 | G5 기준모델 원장 도입 일체 | `feat/reference-model-ledger` 에 5커밋 진행 중 |
| [#403](https://github.com/NumeRealWorks/DashOpti_GUI/issues/403) | refactor, split-group:215 | 모핑 엔진 소유권 분리 + 고정점 마커 영속화 | #281 결합 ⑴⑵⑶ 선행 해소 |
| [#408](https://github.com/NumeRealWorks/DashOpti_GUI/issues/408) | refactor, split-group:215 | Morphing 요청 스케줄링·스레드 예산 | worker 계층 |

## A. 편입 확실 — 분할 그룹이 갈려 있음 (5건)

`split-group:360`(매니페스트 도입 G1\~G10) 중 **G1\~G5([#360](https://github.com/NumeRealWorks/DashOpti_GUI/issues/360)\~[#364](https://github.com/NumeRealWorks/DashOpti_GUI/issues/364))는 프로젝트 안에 있는데 G6\~G10 은 밖에 있다.** 같은 분할 그룹이 반으로 쪼개진 상태라 보드로 진척을 읽을 수 없다.

| # | 라벨 | 제목 | 한 줄 |
|---|---|---|---|
| [#365](https://github.com/NumeRealWorks/DashOpti_GUI/issues/365) | refactor | G6 content uuid 원장 이관 + identity store 폐기 (T12·T13) | 원장 1차 키를 uuid 로 옮기고 구 신원 저장소 제거 |
| [#366](https://github.com/NumeRealWorks/DashOpti_GUI/issues/366) | feature | G7 Set 별 referenceModel 소유 (T14·T15·T16·T19) | 기준모델 소유를 Set 단위로 내림 |
| [#367](https://github.com/NumeRealWorks/DashOpti_GUI/issues/367) | feature | G8 Launcher 조합 핀 + DOE Condition Set 다중 선택 + 배선 (T20·T24·T17) | 런처가 조합을 고정하고 Condition Set 다중 선택 지원 |
| [#368](https://github.com/NumeRealWorks/DashOpti_GUI/issues/368) | feature | G9 파이프라인 조합 스탬프 전파·검증 (T21·T22·T23) | setId 선행 해소([Project-Manifest-Set-Identity-And-Decision-Revisions](Project-Manifest-Set-Identity-And-Decision-Revisions.md)) — 재스펙 반영 완료(2026-09-22), G11(#520) 뒤 착수 · 조합 스탬프를 파이프라인 전 구간에 전파 |
| [#369](https://github.com/NumeRealWorks/DashOpti_GUI/issues/369) | feature | G10 ModelRunner NodeSet 소스 소유 (T18) | NodeSet 소스를 ModelRunner 소유로 |

## B. 편입 유력 — 리팩터 트랙 본류 (11건)

프로젝트 안이 W6·W10 계열인데 `[W20]`·`[W21]` 이 밖에 있다. [#239](https://github.com/NumeRealWorks/DashOpti_GUI/issues/239) 는 그 트랙의 추적 티켓 자체다.

| # | 라벨 | 제목 | 한 줄 |
|---|---|---|---|
| [#239](https://github.com/NumeRealWorks/DashOpti_GUI/issues/239) | docs, refactor, in-progress | Track B(구조 리팩터) 현황 | W8·W13·W14·W16·W19·W20·W21 진척 표 — 본문이 2026-08-21 기준이라 폐기 14건 미반영 |
| [#246](https://github.com/NumeRealWorks/DashOpti_GUI/issues/246) | backlog, refactor | [W20] God-object 해체 — DataProcessor·DashManager·DashProjectManager | Track B 최대 항목 · W10 완결 대기 |
| [#247](https://github.com/NumeRealWorks/DashOpti_GUI/issues/247) | backlog, refactor | [W21] Presentation Model 개선 단계 | 8개 모듈 선행 완료 · W20 후속 |
| [#318](https://github.com/NumeRealWorks/DashOpti_GUI/issues/318) | VTKRenderer, refactor, priority:high | 공유 VTK 씬에 소유권이 없음 | 인수 지점 13곳 · split view 복구 불가 · `split-group:318` 부모 |
| [#331](https://github.com/NumeRealWorks/DashOpti_GUI/issues/331) | VTKRenderer, refactor | libs/ 임시 배치 해소 | DashGizmo 단일 빌드 재배치 · MarchingPlaneBound 상류 환원 |
| [#332](https://github.com/NumeRealWorks/DashOpti_GUI/issues/332) | refactor | morphing — mesh-ops 공개 표면으로의 잔여 이관 2건 | 모핑 로직의 라이브러리 경계 정리 |
| [#322](https://github.com/NumeRealWorks/DashOpti_GUI/issues/322) | VTKRenderer, refactor | GizmoGroup 의 인덱스 병렬 컨테이너 3개 정리 | checked/백업 상태를 DashGizmo 소유로 이관 |
| [#405](https://github.com/NumeRealWorks/DashOpti_GUI/issues/405) | refactor | DashXmlParser FieldStatistics 계열이 호출자 0건 | 살릴지 지울지 결정 필요 |
| [#321](https://github.com/NumeRealWorks/DashOpti_GUI/issues/321) | refactor, DevEnv | Coding convention 고정 및 pre-commit, clang-format, clang-tidy | E 축과 겹치나 `refactor` 를 겸함 |
| [#305](https://github.com/NumeRealWorks/DashOpti_GUI/issues/305) | backlog, refactor, priority:low | analyzer 의 `Eigen::VectorXf` 컨테이너 용도 사용 정리 | `std::vector<float>` 대체 가능 여부 검토 |
| [#412](https://github.com/NumeRealWorks/DashOpti_GUI/issues/412) | backlog, refactor, split-group:413 | Analyzer 가 데이터셋 XML 을 열지 않아도 되게 | 메타데이터·축약값 분리 (방향성) — C 그룹 소속이기도 함 |

## C. 그룹 단위 판단 — `split-group:413` (5건)

XML 접근 경로 개선 묶음. `#412` 만 `refactor` 고 나머지는 `performance` 지만 내용은 **파서 구조 개선**이다. 부모 [#413](https://github.com/NumeRealWorks/DashOpti_GUI/issues/413) 을 포함해 통째로 넣거나 통째로 빼는 편이 맞다.

| # | 라벨 | 제목 | 한 줄 |
|---|---|---|---|
| [#413](https://github.com/NumeRealWorks/DashOpti_GUI/issues/413) | performance | XML 접근 경로 성능 개선 통합 (부모) | 파싱 비용 · 선택적 로드 · 중복 파싱 · 포맷 4축 묶음 |
| [#409](https://github.com/NumeRealWorks/DashOpti_GUI/issues/409) | performance | DashXmlParser: 필요한 것만 읽는 경로가 없다 | 변수 목록·축약값에도 전량 디코딩이 붙는다 |
| [#410](https://github.com/NumeRealWorks/DashOpti_GUI/issues/410) | performance | 한 번의 UI 조작이 같은 XML 을 2회 이상 파싱한다 | 한시 캐시 도입 |
| [#411](https://github.com/NumeRealWorks/DashOpti_GUI/issues/411) | backlog, performance | DOE 산출 XML 포맷 교체 검토 | HDF5(vtkHDF) 등 스트리밍 가능 포맷 |
| [#402](https://github.com/NumeRealWorks/DashOpti_GUI/issues/402) | in-progress, performance | DashXmlParser: 텐서 파싱이 블롭 크기의 5\~6배를 복사한다 | int32 미처리·경계 검사 누락 동반 |

## D. 그룹 단위 판단 — `split-group:318` 잔여 (2건)

부모 `#318` 은 B 에 있다. 아래 둘은 `bugfix` 라벨이지만 같은 전수 조사에서 갈라져 나왔다. 부모만 편입하면 그룹이 또 갈린다.

| # | 라벨 | 제목 | 한 줄 |
|---|---|---|---|
| [#319](https://github.com/NumeRealWorks/DashOpti_GUI/issues/319) | VTKRenderer, bugfix | 레이어 체계 밖 actor 의 상태 결함 4건 | FE actor 숨김 방치 · 무조건 카메라 리셋 · 정리 누락 |
| [#320](https://github.com/NumeRealWorks/DashOpti_GUI/issues/320) | MainWindow, bugfix, blocked | Modeling Tree 의 .vtk/.vtu 표시 토글 무동작 | `m_vtuVtkActors` 가 채워지지 않음 |

## E. 축이 다름 — 인프라·개발환경 (6건)

빌드·CI·개발환경 축이다. 리팩터 트랙과 성격이 달라 **프로젝트를 나누는 편이 낫다.**

| # | 라벨 | 제목 | 한 줄 |
|---|---|---|---|
| [#388](https://github.com/NumeRealWorks/DashOpti_GUI/issues/388) | DevEnv | 로컬 설정 절차를 조사해 모으고 스크립트 하나로 만든다 | 최초 셋업 자동화 |
| [#386](https://github.com/NumeRealWorks/DashOpti_GUI/issues/386) | backlog, infra, DevEnv | clang-tidy 네이밍 검사 | 저장소 소스가 컨벤션에 정렬된 뒤로 보류 |
| [#372](https://github.com/NumeRealWorks/DashOpti_GUI/issues/372) | backlog, DevEnv | CI: Level 1 레인 소요 시간 감시 | 건강 한도(임시 5분) 초과 시 알림 |
| [#336](https://github.com/NumeRealWorks/DashOpti_GUI/issues/336) | infra, DevEnv | vcpkg 이행 마무리 정리 4건 | external/ 삭제 · globalPos() · CRT 배포 · migration docs 삭제 |
| [#335](https://github.com/NumeRealWorks/DashOpti_GUI/issues/335) | infra | registry / meta 저장소 정합 4건 | portfile 주석 · git-tree · preprocessor 미등록 · Abaqus SDK 부재 |
| [#330](https://github.com/NumeRealWorks/DashOpti_GUI/issues/330) | DevEnv | 최신 MSVC(18.10.0)에서 vcpkg build artifact 미공급 | 툴체인 호환 |

## F. 편입 대상 아님 — 단발 결함·기능 (21건 → 제외 19 · 폐기 2)

구조 변경이 아니라 개별 결함 수정·기능이다. 표 마지막 두 행(`#64`·`#63`)은 폐기했다.

| # | 라벨 | 제목 | 한 줄 |
|---|---|---|---|
| [#407](https://github.com/NumeRealWorks/DashOpti_GUI/issues/407) | bug, in-progress | 모델 교체 시 wholesale disconnect 에 안 걸리는 시그널 연결 누적 | 패턴 기준 전수조사 (#401 후속) |
| [#404](https://github.com/NumeRealWorks/DashOpti_GUI/issues/404) | bug | Analyzer: "(std)" 축약이 표준편차가 아니라 최댓값으로 떨어진다 | 조용한 오산출 |
| [#400](https://github.com/NumeRealWorks/DashOpti_GUI/issues/400) | bugfix, source:QC | Model Builder: Data Label 탭 체크 해제가 학습 대상에 미반영 | MCU 변종은 정상 |
| [#394](https://github.com/NumeRealWorks/DashOpti_GUI/issues/394) | bug | SaveProjectAs 가 모든 실패를 무시하고 true 반환 | 저장 실패 은폐 |
| [#393](https://github.com/NumeRealWorks/DashOpti_GUI/issues/393) | — | GenerateMarkerPointsFromSurfaceIds 의 실패·빈 결과가 호출부 3곳에서 무시 | #325 후속 |
| [#376](https://github.com/NumeRealWorks/DashOpti_GUI/issues/376) | in-progress, bugfix | 프로젝트 열기 시 미열림 상태가 ERROR 로 오탐지 | 로그 오탐 |
| [#375](https://github.com/NumeRealWorks/DashOpti_GUI/issues/375) | bug | Surface handle selection 이 drag selection 시 전 영역을 못 덮음 | 선택 누락 |
| [#370](https://github.com/NumeRealWorks/DashOpti_GUI/issues/370) | bugfix, source:QC | ModelRunner: 1D 모델 Run AI Prediction 이 reference analysis file 없으면 차단 | 불필요한 선행 요구 |
| [#337](https://github.com/NumeRealWorks/DashOpti_GUI/issues/337) | docs, blocked | 이행 산출 운영 지식을 상설 문서로 추출 | docs format 확정 선행 |
| [#334](https://github.com/NumeRealWorks/DashOpti_GUI/issues/334) | bugfix | preprocessor 레거시 어댑터 — Ansys Motion 축 2건 미발행 | 축 누락 |
| [#328](https://github.com/NumeRealWorks/DashOpti_GUI/issues/328) | — | Logger: 스레드 이름 알림이 sink 필터에 걸리면 이름 줄 유실 | 필터 경계 |
| [#327](https://github.com/NumeRealWorks/DashOpti_GUI/issues/327) | — | onGenerateAutomaticHandles: K 클램프가 고정점 제거 전에 이뤄짐 | 오류 판정·팝업 수치 어긋남 |
| [#326](https://github.com/NumeRealWorks/DashOpti_GUI/issues/326) | — | readCSVFile: 비수치 밀도 값에서 `std::stod` 예외 미포착 | 앱 종료 |
| [#324](https://github.com/NumeRealWorks/DashOpti_GUI/issues/324) | — | DashRwSession: `catch(...)` 가 사유 없이 빈 결과 반환 | 실패 은폐 |
| [#323](https://github.com/NumeRealWorks/DashOpti_GUI/issues/323) | — | Morphing 설정 저장 실패가 사용자에게 안 알려짐 | DashGeometryParameterWidget |
| [#316](https://github.com/NumeRealWorks/DashOpti_GUI/issues/316) | VTKRenderer, bugfix, blocked | Optimizer Preview 가 공유 renderer 의 actor 를 전부 제거 | 로드된 모델 덮어씀 |
| [#315](https://github.com/NumeRealWorks/DashOpti_GUI/issues/315) | MainWindow, LeftPanel, bugfix, blocked, priority:high | Load 버튼 재클릭 시 하이라이트 유지하고 재로드 무시 | 재클릭 동작 계약 |
| [#307](https://github.com/NumeRealWorks/DashOpti_GUI/issues/307) | — | AI 채팅 데모 기능 | 좌측 AI 버튼 + 우측 채팅 패널 + 대본 재생 |
| [#221](https://github.com/NumeRealWorks/DashOpti_GUI/issues/221) | bugfix, priority:high | 모핑 모듈 진입·재진입 크래시 | 진입 상태 계약 확립 |
| ~~[#64](https://github.com/NumeRealWorks/DashOpti_GUI/issues/64)~~ | — | Crash Debug | **폐기** — 체크리스트 2건 모두 완료 표시. 포괄 제목의 상설 티켓이라 범위가 닫히지 않는다 |
| ~~[#63](https://github.com/NumeRealWorks/DashOpti_GUI/issues/63)~~ | bug | 모핑 실행할 때 핸들 인덱스 불일치 | **폐기** — 2025-11-29 등록 후 10개월 진척 0. 본문의 `RunMorphing()` 교체안이 현 모핑 구조에 안 앉는다 |

## 편입 결과

**A\~E 29건 전량 편입.** `#63`·`#64` 는 `not_planned` 로 폐기하고 사유를 코멘트로 고정했다. 나머지 F 19건은 제외했다.

편입분은 전부 **Backlog** 로 자동 배정됐다 — 프로젝트에 `Item added to project → Backlog` 워크플로가 이미 걸려 있다. 편입 후 보드는 **70항목**이다.

| Status | 건수 | 비고 |
|---|---:|---|
| Backlog | 29 | 이번 편입분 |
| Won't do | 19 | 폐기 14건 + 기존 6건 − #281 복귀 |
| Done | 16 | 기존 10 + 세션 중 추가된 6건(#241\~#245·#258 — W13·W14·W19 잔여, 타인 추가) |
| In progress | 3 | #281(복귀)·#403 포함 |
| Deferred | 2 | #249 · #269 |
| In review | 1 | #364 |

> ⚠ **`#63` 은 문제 자체가 해소됐다는 증거 없이 닫혔다.** 모핑이 model(`vtkUnstructuredGrid`) 기준인데 핸들 생성은 surface 기준이라는 인덱스 불일치가 dev 에서 재현되면 재실측해 새 티켓으로 발행해야 한다. `#64` 는 체크박스가 모두 완료라 `not_planned` 보다 `completed` 가 사실에 가깝다.

---

# 2부. 보드 운영 조치

## 2-1. 자동 편입 (auto-add)

조직 플랜이 `team` 이라 **프로젝트당 워크플로 5개**까지 쓸 수 있다. 현재 auto-add 는 설정돼 있지 않다.

**auto-add 는 UI 에서만 설정된다.** GraphQL 스키마에 워크플로 생성·수정 mutation 이 없다(뷰용 `updateProjectV2View` 는 있으나 워크플로용은 없음). CLI 로 자동화할 수 없다.

설정 경로 — 프로젝트 16 → 우상단 `⋯` → **Workflows** → `Auto-add to project` → Edit:

```
레포:  NumeRealWorks/DashOpti_GUI
필터:  is:issue,is:open,label:refactor
```

프로젝트 creator 가 `minhopark-lgtm` 이므로 권한은 있다.

**제약 2가지.**

| 제약 | 내용 |
|---|---|
| 소급 적용 없음 | 활성화해도 기존 50건은 들어오지 않는다. 1부의 편입 대상은 수동 추가해야 한다 |
| Issue Type 필터 불가 | 조직에 Issue Types(Task/Bug/Feature)가 있지만 **auto-add 필터는 Issue Type 을 지원하지 않는다.** 트리거는 반드시 라벨이어야 한다 |

## 2-2. 팀원에게 공유할 것

**규칙은 하나다 — 구조 리팩터 이슈에는 `refactor` 라벨을 단다.** auto-add 가 보는 것은 이것뿐이고, 라벨이 없으면 보드에 들어오지 않는다.

Priority 는 라벨이 아니라 **조직 Issue Field** 다. `priority:high` 라벨을 달아도 필드는 채워지지 않고, 이슈 생성 시점에는 필드를 지정할 수 없다(템플릿의 `projects:` 키도 등재만 하고 필드값은 못 채운다). 생성 후 보드나 이슈 사이드바에서 직접 고른다.

### Priority 읽는 법 — 영문 4단계 유지

조직 Issue Field 수정은 org owner 권한이고 `minhopark-lgtm` 은 member 라 개명할 수 없다. 옵션 이름은 영문 그대로 두고 의미만 아래로 읽는다.

| 필드 값 | 의미 | 대응 라벨(폐지 예정) |
|---|---|---|
| Urgent | 최우선 | `priority:urgent` |
| High | 우선 | `priority:high` |
| Medium | 중요 | — |
| Low | 필요 | `priority:low` |

2026-09-17 에 라벨 기준으로 30건을 backfill 했다(High 28 · Low 2). 프로젝트 16 의 활성 6건은 아직 미설정이다.

> 개명이 필요하면 org owner 에게 Organization Settings → Planning → Issue fields → Priority 에서 **UI 로** 요청한다. GraphQL `updateIssueField` 는 옵션 입력에 `id` 가 없어 개명이 전면 교체로 처리될 수 있고, 그러면 기존 값이 날아간다.

## 2-3. 접근권

프로젝트 16 은 private 이라 레포 협업자에게 접근이 자동으로 따라가지 않는다. 스캔 시점에는 팀이 하나도 붙어 있지 않아 팀원이 보드를 볼 수 없었고, **2026-09-17 에 `dev-team` 이 부여됐다.**

| 사람 | `dev-team` | 레포 | 보드 |
|---|:---:|---|:---:|
| Miiiing-J | ✅ | admin | ✅ |
| Yoonha403 | ✅ | admin | ✅ |
| minhopark-lgtm | ✅ | admin | ✅ |
| BeomjinPark1212 · TP228N · DCode-NumeReal · hyunkyu-yirang | ✅ | write | ✅ |
| **gunwoonoh** | ❌ | **admin** (조직 멤버) | ❌ |
| **kimdh3529** | ❌ | **write** (외부 협업자) | ❌ |
| inyeongkang1 | ✅ | 협업자 목록에 없음 | ✅ |

**두 사람이 빈다.** `gunwoonoh` 는 조직 멤버라 팀에 넣으면 되고, `kimdh3529` 는 **외부 협업자**(조직 멤버 아님)라 팀 추가가 안 되므로 프로젝트에 개인으로 초대해야 한다.

> **API 로 확인 불가 2건** — GitHub 은 프로젝트의 개인 단위 접근자와 권한 레벨(Read/Write/Admin)을 노출하지 않는다(`ProjectV2` 에 `teams` 필드뿐). `dev-team` 에 준 권한이 Write 인지, 위 두 사람이 개인으로 초대돼 있는지는 `⋯` → Manage access 에서 눈으로 봐야 한다. Read 면 팀원이 보기만 하고 Status·Priority 를 못 바꾼다.

이슈 템플릿의 `projects:` 키 방식도 있으나 **이슈를 만드는 사람이 프로젝트 쓰기 권한을 가져야만 동작**해서 같은 접근권 문제가 남는다. auto-add 쪽이 깔끔하다.

## 2-4. 라벨 축 정리 (후속)

라벨이 타입·상태·우선순위를 한 축에 섞고 있었다. **1·2차까지 집행해 34종 → 23종.** 개명은 붙어 있는 이슈를 유지하므로 무손실이고, 삭제는 그 라벨이 달린 모든 이슈에서 사라지는 비가역 작업이다.

| 축 | 조치 | 상태 |
|---|---|---|
| 미사용 | `duplicate` `help wanted` `invalid` `needreview` `priority:urgent` `wontfix` 삭제 (사용 0건) | ✅ 1차 |
| 타입 중복 | `enhancement` 삭제 (`feature` 와 중복, 열린 건 0) | ✅ 1차 |
| 영역 | `MainWindow` `LeftPanel` `LightPanel` `VTKRenderer` `DevEnv` → `area:*`, `UI/UX` → `area:UI-UX` (개명) | ✅ 1차 |
| 우선순위 | `priority:high`(28) `:low`(2) 삭제 — 30건 전수를 Priority 필드값과 대조해 불일치 0 확인 후 | ✅ 2차 |
| 상태 | `in-progress`(열림 5) `backlog`(열림 7) 삭제 · `blocked` 유지 | ⬜ 3차 — **편입 완료 후** |
| 타입 중복 | `bug`(10) / `bugfix`(13) 통합 — `bugfix` 에 `bug` 를 먼저 달고 삭제하는 순서 | ⬜ 3차 |
| 임시 | `split-group:207`(열림 0) `:210`(열림 0) 삭제 가능 · 나머지 4종은 진행 중 | ⬜ 3차 |

> **우선순위 라벨 삭제의 대가** — `label:priority:high` 이슈 검색을 못 쓰게 된다. 조직 Issue Field 는 검색 문법이 라벨과 다르다.

> **3차가 편입 뒤로 밀린 이유** — 스캔 시점에 열린 56건 중 6건만 보드에 있어, 나머지 50건은 Status 필드가 없고 `in-progress`·`backlog` 라벨이 유일한 상태 표시였다. A\~E 편입으로 이 전제는 해소됐다.

규모 축(`Effort` 조직 필드 High/Medium/Low, `Size` 프로젝트 필드 XS\~XL)이 두 벌이라 하나로 정해야 한다.

## 2-5. 필드와 뷰 구성

### 필드

| 필드 | 종류 | 값 | 용도 |
|---|---|---|---|
| Status | 프로젝트 단일선택 | Deferred · Backlog · Ready · In progress · In review · Done · Won't do | 진행 상태 |
| Priority | **조직 Issue Field** | Urgent · High · Medium · Low | 우선순위. 조직 전역이라 프로젝트 밖 이슈도 값을 가진다 |
| **Iteration** | 프로젝트 iteration | W0(아카이브) · W1\~W12 (월 시작 · 7일) | **주 단위 추적** — 2026-09-17 신설 |
| Size · Estimate | 프로젝트 / 조직 | XS\~XL / 수치 | 미사용 |
| Effort | 조직 Issue Field | High · Medium · Low | 미사용 |
| Start date · Target date | 조직 Issue Field | 날짜 | 미사용. Iteration 과 다른 축(항목 단위 날짜) |

> **규모 축이 세 벌이다** — `Size`(프로젝트) · `Estimate` · `Effort`(조직). 전부 미사용이므로 쓰기 시작하기 전에 하나로 정한다.

Iteration 은 **보드 수준 설정**이다. 시작일과 기간으로 주차 눈금이 정해지고, 이슈는 그 눈금 중 하나를 고를 뿐이다. API 는 UI 와 달리 주차를 자동 생성하지 않아 눈금을 명시해 만들었다 — 소진되면 `updateProjectV2Field` 로 추가한다. 단 **iteration 입력에 `id` 가 없어 목록 갱신은 전면 교체**이므로, 항목이 배정된 뒤에는 기존 주차를 그대로 다시 실어 보내야 한다.

| | 기간 | | | 기간 |
|---|---|---|---|---|
| **W0 이전 완료** | **07/27–09/13 (49일)** | | W6 | 10/19–10/25 |
| W1 | 09/14–09/20 | | W7 | 10/26–11/01 |
| W2 | 09/21–09/27 | | W8 | 11/02–11/08 |
| W3 | 09/28–10/04 | | W9 | 11/09–11/15 |
| W4 | 10/05–10/11 | | W10 | 11/16–11/22 |
| W5 | 10/12–10/18 | | W11 | 11/23–11/29 |
| | | | W12 | 11/30–12/06 |

`W0` 는 추적 시작 이전 항목을 담는 아카이브 칸이다. 시작일이 과거라 GitHub 이 `completedIterations` 로 자동 분류하고, 완료 iteration 에도 항목 배정은 된다. 기간은 보드 내 최초 종료일(2026-07-29)을 덮고 W1 시작에 정확히 맞닿게 잡았다.

### Iteration 배정 현황 (2026-09-17)

| Iteration | 건수 | 내역 |
|---|---:|---|
| W0 이전 완료 | 33 | Done 12 · Won't do 19 · Deferred 2 |
| W1 09/14–09/20 | 4 | Done 4 — #360 #361 #362 #363 |
| 미설정 | 33 | Backlog 29 · In progress 3 · In review 1 |

`#360`\~`#363` 은 실제 종료일이 09/14\~09/15 라 W0 가 아니라 W1 에 넣었다. **주차는 실적이 잡히는 칸이므로 종료일과 어긋나면 안 된다.**

> **폐기·보류 항목에 주차를 붙인 이유** — `Won't do` 19건과 `Deferred` 2건은 "완료" 가 아니라 원칙적으로 주차를 붙일 대상이 아니다. W0 가 실적 칸이 아니라 "추적 이전" 아카이브이고 그 안에서 Status 로 성격이 갈리므로 예외로 뒀다. **W1 이후에는 이 예외를 적용하지 않는다** — 붙이면 "그 주에 폐기했다" 는 없는 사실이 생긴다.

### 뷰

| # | 이름 | 레이아웃 | 필터 | group by | 용도 |
|---|---|---|---|---|---|
| 1 | Backlog | Board | — | — | 전체 |
| 2 | Priority board | Board | — | Priority | 우선순위별 |
| 3 | Team items | Table | — | Status | 상태별 목록 |
| 4 | Roadmap | Roadmap | — | — | 시간축 |
| 5 | My items | Table | `assignee:@me` | — | 내 항목 |
| **7** | **This week** | Board | `iteration:@current` | ⬜ **Status 지정 필요** | **이번 주 예정/진행/완료** |
| **8** | **By week** | Table | — | ⬜ **Iteration 지정 필요** | **주차별 전체 조망** |

7·8 은 2026-09-17 신설. `@current` 는 오늘이 속한 주차를 가리키므로 주가 바뀌면 내용이 따라간다.

### API 로 되는 것과 안 되는 것

보드 설정을 자동화할 때 경계가 갈린다.

| 작업 | API |
|---|:---:|
| 필드 생성 (iteration 포함) · 항목별 필드값 지정 | ✅ |
| 뷰 생성·삭제 · 이름 · 레이아웃 · 필터 · 표시 열 | ✅ |
| 프로젝트에 항목 추가 | ✅ |
| **group by · sort by · Roadmap 시간축** | ❌ UI |
| **워크플로 (auto-add · auto-archive)** | ❌ UI |
| **조직 Issue Field 옵션 수정** | ❌ org owner |
| **개인 단위 프로젝트 접근자·권한 레벨 조회** | ❌ 미노출 |

> **필터 문자열은 검증되지 않는다.** `updateProjectV2View` 는 어떤 문자열이든 그대로 저장한다 — 문법이 틀려도 mutation 은 성공하므로 실제 동작은 UI 에서 확인해야 한다.

### 완료 항목 숨기기

| 원하는 것 | 방법 | 비고 |
|---|---|---|
| 완료 전부 숨김 | 뷰 필터 `-status:Done,"Won't do"` | 70 → 35항목. API 로 즉시 가능 |
| 완료 후 N주 지난 것만 숨김 | Auto-archive 워크플로 (`is:closed updated:<@today-2w`) | UI 전용. 아카이브는 모든 뷰에서 제거되고 복원 가능 |

**뷰 필터로는 "시점" 기준을 만들 수 없다.** 프로젝트 필터는 필드를 넘나드는 OR 를 지원하지 않는다(콤마 = 같은 필드 내 OR, 공백 = AND). "열려 있는 것 **또는** 최근 2주 내 완료된 것" 은 두 필드에 걸친 OR 라 한 줄로 표현되지 않는다. 시점 기준이 목적이면 auto-archive 가 정공법이다.

### 주차 이력의 한계

어떤 항목이 몇 주차에 끝났는지는 **그 항목의 Iteration 값이 그대로 남아 있을 때만** 보인다. 미완료분을 다음 주로 넘기면(carry over) 원래 주차 기록이 지워진다. 주차별 완료량 추이를 남기려면 **Insights** 의 burn-up 을 써야 하는데, 조회·설정 모두 API 로 안 되고 UI 전용이다.

## 조치 체크리스트

- [x] A\~E 29건 편입 — 전량 Backlog 자동 배정, 보드 70항목
- [x] `#63`·`#64` 폐기 (`not_planned` + 사유 코멘트)
- [x] 라벨 축 1차 — 미사용 6종 + `enhancement` 삭제, 영역 6종 `area:` 개명
- [x] 라벨 축 2차 — `priority:high`·`:low` 삭제 (필드 대조 후)
- [x] 프로젝트 접근권 — `dev-team` 부여
- [x] Iteration 필드 신설 (W1\~W12 · 2026-09-14 월 시작 · 7일) + `W0 이전 완료` 아카이브 칸
- [x] 뷰 신설 — `This week`(Board · `iteration:@current`) · `By week`(Table)
- [x] 과거 항목 37건 Iteration 배정 — W0 33건(Done 12 · Won't do 19 · Deferred 2) · W1 4건(#360\~#363)

**UI 에서 (API 불가)**

- [ ] `This week` → `Group by: Status` · `By week` → `Group by: Iteration` **(안 하면 두 뷰가 무의미)**
- [ ] Manage access 확인 — `dev-team` 권한이 Write 인지, `gunwoonoh`(팀 추가) · `kimdh3529`(외부 협업자 → 개인 초대)
- [ ] Workflows → Auto-add to project (`is:issue,is:open,label:refactor`) — 라벨 개명을 끝냈으므로 지금이 적기
- [ ] Workflows → Auto-archive items (시점 기준 숨김을 원할 때)
- [ ] Roadmap 뷰 시간축을 Iteration 으로 (선택)

**내가 할 수 있는 것**

- [ ] 편입 29건 Status 재배정 — 전량 Backlog 로 들어왔으나 `in-progress` 라벨 보유분은 In progress 가 맞다
- [ ] Priority 값 지정 (현재 보드 대부분 미설정 — `Priority board` 가 `No Priority` 한 칸이 된다)
- [ ] 활성 33건 Iteration 배정 (Backlog 29 · In progress 3 · In review 1) — 주차 계획이 정해지면 일괄
- [ ] 완료 숨김 필터 — `Backlog`·`Priority board`·`By week` 에 `-status:Done,"Won't do"`
- [ ] 라벨 축 3차 — `in-progress`·`backlog` 삭제 · `bug`/`bugfix` 통합 · `split-group:207`·`:210` 삭제

**판단 필요**

- [ ] 팀에 `refactor` 라벨 규칙 + Priority 의미 표 공지
- [ ] 규모 축 단일화 (`Size` · `Estimate` · `Effort` 세 벌)
- [ ] `#63` 인덱스 불일치 재현 여부 확인 후 필요 시 재발행
