# Downstream 관점 교차 검토

검토 기준: 2026-10-05 작성 중인 common/geometry/execution/downstream JSON, 현 코드 및 sources 이슈/PR 스냅샷. 다른 담당 구현을 실행한 결과가 아닌 계획 타당성 검토다. 타 담당 파일은 수정하지 않았다.

## 결과

### DS-X01 · P1 · VIS-001

기존 actor를 숨기는 scope가 #316의 확정된 비파괴 overlay 요구와 다르다.

- `modules/geometry.json VIS-001 scope: 기존 FE 문서·핸들·피킹 actor는 숨김/복원`
- `sources/issues/316.md: 기존 씬 위 preview actor 겹침, 로드된 모델이 씬에 남음, 표시커서·카메라 유지, 다음 Load에서 무효화`

권고: VIS-001에서는 기존 actor의 visibility·registry 표시커서·camera를 보존하고 preview actor만 교체한다. 일반 모듈 전환 숨김 정책은 VIS-003으로 분리한다. 완료 조건에 현재 로드 모델/핸들 유지·camera 유지·다음 Load 무효화를 명시한다.

### DS-X02 · P2 · PRJ-03

전 구간에서 모든 다른 조합을 차단한다는 문장이 DOE 기록-only와 MCU 무스탬프 예외를 덮는다.

- `modules/common.json PRJ-03 acceptance: 모든 단계에서 유효한 조합은 통과하고 다른 조합은 차단`
- `sources/issues/368.md D21: DOE는 기록만, MCU는 조합 미지정 허용`
- `sources/pr-530.json T22 requiresParameterizationPin/MCU 예외 및 templateDecks 철회`

권고: 생산 단계는 조합 기록, Sim 소비 단계만 최초 핀/다른 조합/무스탬프 차단, MCU 예외를 별도 acceptance로 구분한다. templateDecks 기록 철회도 최신 PR 결정으로 인정한다.

### DS-X03 · P2 · PRJ-05, RUN-03, BLD-01, RUN-05, OPT-01, ANA-03

AL 생산→Builder 첫 소비의 대장만으로 #471 전체 소비 추적의 나머지 모듈 작업이 비어 있다.

- `modules/common.json PRJ-05 scope 첫 AL→Builder만 연결`
- `sources/issues/471.md 산출물 대장과 어디에 소비됐는지 기록`
- `#650 downstream 카드들은 generation 경고이며 전체 run/artifact 소비 대장은 아님`

권고: root가 계획한 모듈별 대장 adoption 후속을 명시한다. DOE 생산, Builder 모델 생산, Runner/Optimizer 생산·소비, Analyzer 읽기 소비를 포함하고 id·경로·Set·종결 상태 계약은 PRJ-05를 재사용한다. RUN-03 local case record를 대장 스키마와 조인하되 채번/삭제 결함의 착수를 대장 전체 구현 뒤로 미루지 않는다.

### DS-X04 · P2 · IO-04, OPT-05

IO-04의 시각화 설정 저장/복원 표현은 저장 기제 이행을 넘어 삭제된 legacy Analyzer 설정 영속화를 다시 만드는 요구로 해석될 수 있다.

- `modules/common.json IO-04 scope 동적 파라미터·Dataset/Data Label·시각화 설정 저장/복원 대조`
- `model/DashOptimizer.cpp:362 legacy Results Analysis 섹션을 native 처리로 제거`
- `view/DashResultsAnalyzerWidget.cpp 현 plot 경로는 settings DTO 요청; 오래된 write-only JSON 경로와 다름`

권고: IO-04는 현재 실제로 쓰는 설정 파일의 원자성/버전/오류 전파와 fixture로 한정한다. OPT-05는 편집→모델 정본→저장 필드 왕복을 소유한다. Analyzer 설정 보존이 별도 제품 요구로 확인되기 전 광범위 신규 persistence를 완료 조건에 넣지 않는다.

### DS-X05 · P2 · RUN-04

NodeSet source 영속화만 구현하면 현 코드의 source Document 선택 문제를 놓칠 수 있다.

- `model/DashModelRunner.cpp:2396 nodeSetSourcePath empty 검사`
- `model/DashModelRunner.cpp:2405 extractComponentVtuFromDat에는 nodeSetSourcePath가 아니라 생성 기준 reference 전달`
- `sources/issues/369.md 별도 파일 선택을 저장하고 콤보 재적재 요구`

권고: 이미 RUN-04 scope/notes에 반영했다. 저장·복원되는 파일과 NodeSet lookup에 쓰는 Document를 함께 검증하되 기존 허용 정책(별도 파일과 기준 deck 라벨 일치 검증 강제 안 함)을 임의 변경하지 않는다.

## 중복이 아닌 것으로 확인한 접점

- PRJ-01은 프로젝트 모델 해제 순서, RUN-07/OPT-02는 모듈 요청 id·세대와 결과 귀속이다. 서로 대체하지 않는다.
- VIS-001은 기존 씬 보존, OPT-02는 비동기 terminal/취소다. 서로 하드 선행 불필요.
- AST-003은 RW SDK 스레드/문서 수집, RUN-06은 폴더·metadata load 스냅샷이다.
- RES-12는 Set XML 생산자/모든 소비자 포맷 이행, BLD-01/ANA-03은 상류 generation 및 표시다.
- UI-06은 cell widget→현재 행, RUN-03은 생성/재진입/삭제에서 domain case 식별이다.
- DIR-01은 PR652 통합, RUN-08은 Runner/Optimizer prefill 진입점이다.
- BLD-02/OPT-03/ANA-07은 실제 누락된 실패·terminal 배선, ASY-02/UI-05는 공통 상태/통지 계약이다.

## 범위 회귀 방지

- #476 조회 대장 화면은 최신 댓글상 철회이다. 파일 대장 adoption을 하더라도 독립 목록 UI를 되살리지 않는다.
- #548/#549/#436/#437 및 XML metadata/cache/async 기반을 다시 구현 카드로 만들지 않는다.
- #459의 MCU SHAP는 현재 미지원 메뉴 숨김과 충돌하므로 ANA-01 decision gate를 유지한다.
- #405의 reduceStd는 현재 살아 있는 API라 legacy 정리에서 삭제하지 않는다.

## 자체 파일 확인

28개 카드 ID 고유 및 필수 필드 확인. 외부 선행 ID들은 현재 다른 모듈 JSON에 존재한다. 담당 40개 이슈 disposition은 다수 카드/공통 작업 연결을 허용한다. 런타임·빌드·tests 미실행은 research/downstream.md에 명시했다.

## 담당자 회신과 최종 통합 요청

- DS-X01: geometry 담당자가 지적을 수용했다. root가 최종 VIS-001에 overlay·표시커서·camera 보존/다음 Load 무효화를 반영하기로 했다. 원본 geometry 파일을 본 검토자가 직접 수정하지 않았다.
- DS-X02: root가 Sim/MCU·DOE 예외 AC를 추가했다. 다만 후속 JSON 조회에 template deck 기록/변종 경고가 남아 다시 알렸다. **PR530 최신 본문의 templateDecks 철회**까지 반영해야 완료다. 과거 #368 원문을 최신 PR 결정 위에 놓지 않는다.
- DS-X03: root가 **IO-10(Builder 모델 생산·Runner/Optimizer 소비)**, **IO-11(DOE 입력·Runner/Optimizer 결과·Analyzer 소비)**을 추가한 것을 확인했다. 대장 범위 누락은 해결됐으며 local case record와의 조인은 구현 시 검증한다.
- DS-X04: root가 Analyzer plot persistence 요구를 제외하기로 회신했다. 작성 중인 원본 IO-04 문구에는 아직 시각화 설정이 남아 있어 최종 통합에서 삭제를 확인하도록 전달했다.
- DS-X05: RUN-04 카드/연구 문서에 이미 반영했다. 별도 새 카드가 필요하지 않다.
