# 착수 순서와 병합 단위

> **2026-10-08 개정 반영** — [이슈 개정 이력](../Issue-Revision-History.md). 설계 반영과 구현 완료는 구분한다.

현재 설계 순서는 #368(PRJ-03) → #685(PRJ-04)다. #650(PRJ-11 및 모듈 버전 카드)은 별도 작업이다. PRJ-05·IO-10·IO-11은 철회 기록으로 실행 단계에서 제외한다. #473(RUN-03)·#369(RUN-04)·개명 결함(PRJ-02)은 출처 전환을 기다리지 않는다. #444(AL-05)의 비용 확인·필요시 분리 후 #441의 재시작 복구(AL-06)를 진행한다.

우선순위는 위험도 제안이며 기존 board Priority와 무관하다. 같은 파일을 바꾸는 작업은 별도 순서 조정이 필요하다. 아래 위상 단계는 논리적 선행 관계만 뜻하며 날짜/인력/공수를 산정하지 않았다.

## 과거 조사 PR과 현재 착수 시 확인할 범위

| PR | 새 추적 작업 | 주의 |
|---|---|---|
| #530 | 현재 실행 대상 아님 | 2026-10-07 조회에서 미병합 CLOSED. 옛 조합 핀 재이식 요구는 폐기하고 #368→#685 계약을 적용 |
| #651 | AL-09 | AST-002를 합쳤다. Assets+Launcher+fe-safe 한 PR이며 AST-001 실패 복구는 별도 |
| #652 | DIR-01 | Direct 입력 표 삭제 이후 UI-06 수정 범위 재확인 |
| #654 | GEO-001 | 구 형식 거부/새 핸들 상태기; GEO 후속은 통합 뒤 진행 |

## 바로 착수할 수 있는 P1

- [GEO-006](03_TASK_CATALOG.md#geo-006): QC 결과 창을 닫아도 저장 작업이 대기 상태에 갇히지 않게 한다
- [VIS-001](03_TASK_CATALOG.md#vis-001): Optimizer 프리뷰가 자기 actor만 교체하도록 한다
- [VIS-002](03_TASK_CATALOG.md#vis-002): FE actor의 숨김·복원·등록 수명과 카메라 갱신을 바로잡는다
- [VIS-004](03_TASK_CATALOG.md#vis-004): split view 이탈과 ghost 외형·범례 복원을 씬 전환에 연결한다
- [AST-001](03_TASK_CATALOG.md#ast-001): 파일·폴더 묶음의 덮어쓰기를 실패 시 복구 가능한 교체로 만든다
- [AL-01](03_TASK_CATALOG.md#al-01): Target Part 로딩 중 실행을 막고 실패 시 저장된 선택을 보존한다
- [AL-02](03_TASK_CATALOG.md#al-02): 빈 설정 파일을 복구하고 저장 실패 이유와 실행 거부를 연결한다
- [AL-03](03_TASK_CATALOG.md#al-03): 모든 제출 실패와 프로젝트 전환이 케이스를 종결하게 한다
- [AL-04](03_TASK_CATALOG.md#al-04): Stop이 Motion 대기 큐와 진행 작업을 함께 취소한다
- [AL-07](03_TASK_CATALOG.md#al-07): Re-run 실패와 취소에서 이전 결과와 기록을 보존한다
- [RES-01](03_TASK_CATALOG.md#res-01): 선택 시점의 응답만 카탈로그와 필드 추출에 사용한다
- [RES-06](03_TASK_CATALOG.md#res-06): Side Force 계산 실패를 정상 0과 구분한다
- [BLD-02](03_TASK_CATALOG.md#bld-02): 학습 시작 거절·실패·취소를 하나의 종료 상태로 화면에 반영한다
- [RUN-01](03_TASK_CATALOG.md#run-01): 해석 파일 없는 1D 예측에 사용자가 입력한 DV 값을 전달한다
- [RUN-03](03_TASK_CATALOG.md#run-03): 결과 항목의 표 연결·덮어쓰기 방지·삭제 정합을 수정한다
- [RUN-07](03_TASK_CATALOG.md#run-07): 입력 생성 요청을 Set에 고정하고 늦은 완료·취소를 처리한다
- [RUN-09](03_TASK_CATALOG.md#run-09): 유효한 0 DV와 입력 경계를 보존한다
- [OPT-02](03_TASK_CATALOG.md#opt-02): 프리뷰 요청 완료를 호출 Set으로 돌려주고 취소·재진입을 처리한다
- [OPT-03](03_TASK_CATALOG.md#opt-03): 최적화 진행·실패·취소를 Run 버튼과 결과 화면에 연결한다
- [BLD-04](03_TASK_CATALOG.md#bld-04): 학습 모델 삭제가 설정·메타데이터·파일에 함께 반영되게 한다
- [RUN-10](03_TASK_CATALOG.md#run-10): 혼합 Geometry·Condition 모델의 생성 소스를 명시적으로 해석한다
- [OPT-06](03_TASK_CATALOG.md#opt-06): 목적·제약 수식의 심볼을 응답·DV 식별자에 고정한다
- [PRJ-01](03_TASK_CATALOG.md#prj-01): 프로젝트 교체 전에 모든 모듈의 모델 연결과 진행 중 요청을 정리한다
- [PRJ-02](03_TASK_CATALOG.md#prj-02): Set 개명 시 설정·산출물·참조를 함께 바꾸고 실패를 되돌린다
- [PRJ-03](03_TASK_CATALOG.md#prj-03): Sampler·Launcher·Builder의 입력 참조와 산출물 출처 기록 계약을 적용한다
- [PRJ-06](03_TASK_CATALOG.md#prj-06): Save와 Save As의 성공 판정을 실제 저장 결과와 일치시킨다
- [PRJ-08](03_TASK_CATALOG.md#prj-08): 같은 프로젝트를 두 앱이 수정하지 못하도록 잠근다
- [ASY-03](03_TASK_CATALOG.md#asy-03): 데몬 명령 응답에 요청별 시한과 종결 처리를 둔다
- [UI-06](03_TASK_CATALOG.md#ui-06): 삭제 가능한 표의 콜백을 현재 항목에 결합한다

## 선행 관계별 묶음

### 단계 0

[AL-01](03_TASK_CATALOG.md#al-01) (착수 가능), [AL-02](03_TASK_CATALOG.md#al-02) (착수 가능), [AL-03](03_TASK_CATALOG.md#al-03) (착수 가능), [AL-04](03_TASK_CATALOG.md#al-04) (착수 가능), [AL-05](03_TASK_CATALOG.md#al-05) (착수 가능), [AL-07](03_TASK_CATALOG.md#al-07) (착수 가능), [AL-08](03_TASK_CATALOG.md#al-08) (착수 가능), [AL-09](03_TASK_CATALOG.md#al-09) (PR 진행 중), [AL-10](03_TASK_CATALOG.md#al-10) (착수 가능), [AL-12](03_TASK_CATALOG.md#al-12) (착수 가능), [AL-13](03_TASK_CATALOG.md#al-13) (결정 필요), [AL-14](03_TASK_CATALOG.md#al-14) (보류), [ANA-01](03_TASK_CATALOG.md#ana-01) (결정 필요), [ANA-02](03_TASK_CATALOG.md#ana-02) (착수 가능), [ANA-04](03_TASK_CATALOG.md#ana-04) (착수 가능), [ANA-05](03_TASK_CATALOG.md#ana-05) (보류), [ANA-06](03_TASK_CATALOG.md#ana-06) (착수 가능), [ANA-07](03_TASK_CATALOG.md#ana-07) (착수 가능), [ANA-08](03_TASK_CATALOG.md#ana-08) (착수 가능), [AST-001](03_TASK_CATALOG.md#ast-001) (착수 가능), [AST-003](03_TASK_CATALOG.md#ast-003) (보류), [ASY-01](03_TASK_CATALOG.md#asy-01) (착수 가능), [ASY-02](03_TASK_CATALOG.md#asy-02) (착수 가능), [ASY-03](03_TASK_CATALOG.md#asy-03) (착수 가능), [ASY-04](03_TASK_CATALOG.md#asy-04) (착수 가능), [ASY-05](03_TASK_CATALOG.md#asy-05) (착수 가능), [BLD-02](03_TASK_CATALOG.md#bld-02) (착수 가능), [BLD-03](03_TASK_CATALOG.md#bld-03) (착수 가능), [BLD-04](03_TASK_CATALOG.md#bld-04) (착수 가능), [CAD-001](03_TASK_CATALOG.md#cad-001) (보류), [CAD-002](03_TASK_CATALOG.md#cad-002) (착수 가능), [CAD-003](03_TASK_CATALOG.md#cad-003) (착수 가능), [CON-002](03_TASK_CATALOG.md#con-002) (착수 가능), [DEV-01](03_TASK_CATALOG.md#dev-01) (착수 가능), [DEV-02](03_TASK_CATALOG.md#dev-02) (실측 필요), [DEV-03](03_TASK_CATALOG.md#dev-03) (착수 가능), [DEV-04](03_TASK_CATALOG.md#dev-04) (실측 필요), [DEV-05](03_TASK_CATALOG.md#dev-05) (실측 필요), [DEV-06](03_TASK_CATALOG.md#dev-06) (보류), [DEV-07](03_TASK_CATALOG.md#dev-07) (결정 필요), [DIR-01](03_TASK_CATALOG.md#dir-01) (PR 진행 중), [DOE-01](03_TASK_CATALOG.md#doe-01) (결정 필요), [DOE-02](03_TASK_CATALOG.md#doe-02) (결정 필요), [DOE-04](03_TASK_CATALOG.md#doe-04) (착수 가능), [GEO-001](03_TASK_CATALOG.md#geo-001) (PR 진행 중), [GEO-006](03_TASK_CATALOG.md#geo-006) (착수 가능), [IO-01](03_TASK_CATALOG.md#io-01) (착수 가능), [IO-06](03_TASK_CATALOG.md#io-06) (착수 가능), [OPT-02](03_TASK_CATALOG.md#opt-02) (착수 가능), [OPT-03](03_TASK_CATALOG.md#opt-03) (착수 가능), [OPT-04](03_TASK_CATALOG.md#opt-04) (착수 가능), [OPT-05](03_TASK_CATALOG.md#opt-05) (착수 가능), [OPT-06](03_TASK_CATALOG.md#opt-06) (착수 가능), [PRJ-01](03_TASK_CATALOG.md#prj-01) (착수 가능), [PRJ-02](03_TASK_CATALOG.md#prj-02) (착수 가능), [PRJ-03](03_TASK_CATALOG.md#prj-03) (착수 가능), [PRJ-06](03_TASK_CATALOG.md#prj-06) (착수 가능), [PRJ-08](03_TASK_CATALOG.md#prj-08) (착수 가능), [PRJ-09](03_TASK_CATALOG.md#prj-09) (착수 가능), [PRJ-10](03_TASK_CATALOG.md#prj-10) (착수 가능), [PRJ-11](03_TASK_CATALOG.md#prj-11) (결정 필요), [RES-01](03_TASK_CATALOG.md#res-01) (착수 가능), [RES-03](03_TASK_CATALOG.md#res-03) (착수 가능), [RES-06](03_TASK_CATALOG.md#res-06) (착수 가능), [RES-07](03_TASK_CATALOG.md#res-07) (착수 가능), [RES-08](03_TASK_CATALOG.md#res-08) (착수 가능), [RES-10](03_TASK_CATALOG.md#res-10) (착수 가능), [RES-12](03_TASK_CATALOG.md#res-12) (결정 필요), [RUN-01](03_TASK_CATALOG.md#run-01) (착수 가능), [RUN-03](03_TASK_CATALOG.md#run-03) (착수 가능), [RUN-04](03_TASK_CATALOG.md#run-04) (착수 가능), [RUN-06](03_TASK_CATALOG.md#run-06) (착수 가능), [RUN-07](03_TASK_CATALOG.md#run-07) (착수 가능), [RUN-09](03_TASK_CATALOG.md#run-09) (착수 가능), [RUN-10](03_TASK_CATALOG.md#run-10) (착수 가능), [UI-01](03_TASK_CATALOG.md#ui-01) (실측 필요), [UI-02](03_TASK_CATALOG.md#ui-02) (착수 가능), [UI-03](03_TASK_CATALOG.md#ui-03) (착수 가능), [UI-04](03_TASK_CATALOG.md#ui-04) (착수 가능), [UI-05](03_TASK_CATALOG.md#ui-05) (착수 가능), [UI-06](03_TASK_CATALOG.md#ui-06) (착수 가능), [UI-07](03_TASK_CATALOG.md#ui-07) (착수 가능), [UI-08](03_TASK_CATALOG.md#ui-08) (착수 가능), [VIS-001](03_TASK_CATALOG.md#vis-001) (착수 가능), [VIS-002](03_TASK_CATALOG.md#vis-002) (착수 가능), [VIS-004](03_TASK_CATALOG.md#vis-004) (착수 가능), [VIS-006](03_TASK_CATALOG.md#vis-006) (착수 가능), [VIS-007](03_TASK_CATALOG.md#vis-007) (착수 가능)

### 단계 1

[AL-06](03_TASK_CATALOG.md#al-06) (결정 필요), [ANA-03](03_TASK_CATALOG.md#ana-03) (선행 작업 후), [BLD-01](03_TASK_CATALOG.md#bld-01) (선행 작업 후), [CON-001](03_TASK_CATALOG.md#con-001) (선행 작업 후), [DOE-03](03_TASK_CATALOG.md#doe-03) (선행 작업 후), [GEO-002](03_TASK_CATALOG.md#geo-002) (선행 작업 후), [GEO-003](03_TASK_CATALOG.md#geo-003) (선행 작업 후), [GEO-007](03_TASK_CATALOG.md#geo-007) (실측 필요), [IO-02](03_TASK_CATALOG.md#io-02) (선행 작업 후), [IO-03](03_TASK_CATALOG.md#io-03) (선행 작업 후), [IO-04](03_TASK_CATALOG.md#io-04) (선행 작업 후), [IO-07](03_TASK_CATALOG.md#io-07) (선행 작업 후), [IO-08](03_TASK_CATALOG.md#io-08) (선행 작업 후), [IO-09](03_TASK_CATALOG.md#io-09) (선행 작업 후), [OPT-07](03_TASK_CATALOG.md#opt-07) (보류), [PRJ-04](03_TASK_CATALOG.md#prj-04) (선행 작업 후), [PRJ-07](03_TASK_CATALOG.md#prj-07) (선행 작업 후), [RES-02](03_TASK_CATALOG.md#res-02) (선행 작업 후), [RES-04](03_TASK_CATALOG.md#res-04) (선행 작업 후), [RES-05](03_TASK_CATALOG.md#res-05) (선행 작업 후), [RES-09](03_TASK_CATALOG.md#res-09) (선행 작업 후), [RES-13](03_TASK_CATALOG.md#res-13) (결정 필요), [RUN-02](03_TASK_CATALOG.md#run-02) (선행 작업 후), [RUN-08](03_TASK_CATALOG.md#run-08) (선행 작업 후), [RUN-11](03_TASK_CATALOG.md#run-11) (보류), [VIS-003](03_TASK_CATALOG.md#vis-003) (선행 작업 후)

### 단계 2

[GEO-004](03_TASK_CATALOG.md#geo-004) (선행 작업 후), [GEO-005](03_TASK_CATALOG.md#geo-005) (선행 작업 후), [OPT-01](03_TASK_CATALOG.md#opt-01) (선행 작업 후), [RES-11](03_TASK_CATALOG.md#res-11) (실측 필요), [RUN-05](03_TASK_CATALOG.md#run-05) (선행 작업 후), [VIS-005](03_TASK_CATALOG.md#vis-005) (선행 작업 후)

## 충돌·합치기 판단

- `DashMainWindow` / 프로젝트 전환: PRJ-01·06·07, AST-001/CON-001, UI-01~06은 큰 동시 변경을 피하고 작은 완료 묶음으로 순차 통합한다.
- `DashAnalysisLauncher` / result 처리: AL-01~08·RES-08~10·IO-03·IO-08은 같은 파일을 바꾼다. 구조 경계 정리와 worker 이관을 구분하되 수정량이 작은 소비자 치환은 묶어도 된다.
- 입력 질의: RES-03의 응답 식별 계약 뒤 RES-04/05를 진행한다. 별개의 Side Force/완료 신호 결함은 무조건 기다릴 이유가 없다.
- `Geometry/interaction`: GEO-001 이후 GEO-002/003, 그 뒤 생성기 작업. 값 모델과 renderer 소유권은 별도 완료 조건이다.
- 저장: IO-01을 적용 가능한 최소 계약으로 완성한 뒤 IO-02/03/04에 확산한다. 도메인 결함인 OPT-05·AL-02 등을 전체 persistence 이행 때문에 막지 않는다.
- 참조·출처: PRJ-03(#368) 생산 계약 뒤 PRJ-04(#685) 소비 전환을 진행한다. 현재 Set ID는 유지하고 상류 setId 참조 변경을 허용한다. 선택 변경만으로 출처를 수정하지 않고 재실행 덮어쓰기 때 실제 출처를 함께 갱신한다. 별도 대장과 전체 이력 보존은 요구하지 않는다.
- 버전·최신성: PRJ-11(#650)에서 의미·비교 불가·판정 규칙을 정의한 뒤 모듈별 적용을 진행한다. 생산 Set 기록, 소비 Set 판정, 프로젝트 호출·집계, VM 표시의 책임을 지킨다.
- 공통 규약: ASY-01/02와 UI-05는 실제 모듈 결함 수정의 무조건 선행이 아니다. 첫 소비와 함께 계약을 확정하고 나머지는 점진 적용한다.
- DEV-02/04/05는 외부 공급/실행 환경을 확인해야 한다. GUI PR 하나로 SDK 공급·외부 registry 작업까지 완료됐다고 표시하지 않는다.

## 정책·실측 관문

- [GEO-007](03_TASK_CATALOG.md#geo-007) — 실측 필요: 검증 게이트 성격의 작업이다. 통과하면 구현 PR이 필요 없을 수 있으며 미검증을 결함으로 단정하지 않는다. Optimizer/Runner 요청 ID·취소 구현은 downstream 카드 소유.
- [AST-003](03_TASK_CATALOG.md#ast-003) — 보류: 이슈 Deferred 유지. registry의 기존 generation/dedup은 보존한다. co_await API여도 DashRwDocumentHandle은 GUI actor에서 suspend 전 동기 완료될 수 있으므로 AL-12 이후 남는 RW 작업의 실제 thread 이관도 여기서 소유한다. VTK actor는 GUI에 연결한다. ANSYS Motion 자체 solver 경로 개편은 범위 밖.
- [CAD-001](03_TASK_CATALOG.md#cad-001) — 보류: 현재 Deferred 우선도를 유지한다. Direct Launch/Workbench job 중복·구독 전량 해제 정리는 execution 담당이 별도로 판단한다. 새 CAD 기능이나 CAD 프로젝트 누수 해결(#560 완료)은 포함하지 않는다.
- [DOE-01](03_TASK_CATALOG.md#doe-01) — 결정 필요: #615의 추가 개정 계획은 GitHub 미반영이다. 번호는 표시·초기 선택 규칙이며 참조의 정체성이 아니다. Resample 간 자동 선택 정책은 #368·#685의 확정 참조 범위와 분리해 논의한다.
- [DOE-02](03_TASK_CATALOG.md#doe-02) — 결정 필요: 현재 #615는 active 저장 위치만 지정한다. 어느 Launcher Set의 active가 샘플의 유효성을 결정하는지 확정해야 구현이 단정되지 않는다.
- [AL-06](03_TASK_CATALOG.md#al-06) — 결정 필요: 재연결 불가능한 solver를 새로 실행할지 묵시적으로 정하지 않는다. 프로세스 생존 판정과 사용자 재시도 정책을 먼저 확정한다.
- [AL-13](03_TASK_CATALOG.md#al-13) — 결정 필요: 자동 마이그레이션을 임의 추가하지 않는다. PR654가 해당 입력을 전부 거부한다면 새 구현 없이 대체됨으로 종료할 수 있다.
- [AL-14](03_TASK_CATALOG.md#al-14) — 보류: 편의 기능이며 기존 결과 정합성 수정의 선행이 아니다. 현재 범위에서는 결정 작업만 확정한다.
- [RES-11](03_TASK_CATALOG.md#res-11) — 실측 필요: 실제 SDK/fixture 필요, 이번 조사에서 실행하지 않았다. 도메인 검증은 먼저 할 수 있으며 worker 전체 완료를 기다리지 않는다. 최종 후속경계 승인은 RES-02/07/09 완료 후 해당 검증을 충족해야 한다.
- [RES-12](03_TASK_CATALOG.md#res-12) — 결정 필요: #643·#411의 추가 개정은 팀 논의용이며 GitHub 미반영이다. 본 작업은 저장 구조·중복 제거·포맷 검토를 담당하고 출처는 PRJ-03(#368), 버전은 PRJ-11(#650)과 접점을 맞춘다. 포맷 전환과 출처 기록은 서로의 불필요한 선행이 아니다. #411 독립 유지/흡수와 이어쓰기 기준은 미결이다.
- [RES-13](03_TASK_CATALOG.md#res-13) — 결정 필요: HDF5 또는 USD 구현을 이미 승인된 확정 작업으로 세지 않는다. XML 유지도 유효한 결론이다.
- [ANA-01](03_TASK_CATALOG.md#ana-01) — 결정 필요: 결정 질문: MCU SHAP를 제품 지원 기능으로 되살릴 것인가, 현재의 명시적 미지원 정책을 유지할 것인가? #459를 단순 콤보 누락 fix로 확정하지 않는다.
- [ANA-05](03_TASK_CATALOG.md#ana-05) — 보류: #305 자체가 독립 추진을 권하지 않는 조건부 정리다. Eigen 전체 제거/성능 향상을 확정 목표로 삼지 않는다. 본 목록에서 즉시 실행 업무로 집계하지 않는다.
- [RUN-11](03_TASK_CATALOG.md#run-11) — 보류: 공유 NX 계약 CAD-001의 보류를 승계한다. 모핑 요청 수명 수정은 이 작업과 독립적으로 먼저 진행한다.
- [OPT-07](03_TASK_CATALOG.md#opt-07) — 보류: 공유 NX 계약 CAD-001의 보류를 승계한다. 모핑 요청 수명 수정은 이 작업과 독립적으로 먼저 진행한다.
- [UI-01](03_TASK_CATALOG.md#ui-01) — 실측 필요: macOS 정적 조사에서 Windows 프리즈를 실증하지 않았다. 프레임리스/중첩 QMainWindow 전체 교체는 필요성 입증 뒤 선택; 즉시 필수 작업으로 확정하지 않는다.
- [DEV-02](03_TASK_CATALOG.md#dev-02) — 실측 필요: 이슈의 MSVC 18.10.0을 최신 권장 버전으로 단정하지 않는다. 현재 공급 runner 지문 확인이 착수 조건이다.
- [DEV-04](03_TASK_CATALOG.md#dev-04) — 실측 필요: 옛 CMake 업스트림 대기를 현재 blocker로 확정하지 않는다. DEV-02 toolset 선택 결과와 맞춘다.
- [DEV-05](03_TASK_CATALOG.md#dev-05) — 실측 필요: 여러 저장소에 걸친 공급/소비 묶음이라 2 PR로 나뉠 수 있다. 외부 SDK 설치·지원 버전은 본 조사에서 실증하지 못했다. 현재 snapshot에서 meta 등록과 과거 MKL pin 지시는 해소됐고 preprocessor 포트의 2020 기본/2024 opt-in 설명은 남아 있다.
- [DEV-06](03_TASK_CATALOG.md#dev-06) — 보류: 전수 정렬 속도·범위를 먼저 결정해야 한다. 완료 전 gate 활성화는 기존 보류 결정을 위반한다. 이 카드는 전체 리네이밍을 1PR로 요구하지 않는다.
- [DEV-07](03_TASK_CATALOG.md#dev-07) — 결정 필요: 설정 전달/수정 권한·검증 정책은 제품 결정 필요. 현재 날짜를 보고 사용자 라이선스 상태를 추정하지 않는다.
- [PRJ-11](03_TASK_CATALOG.md#prj-11) — 결정 필요: 버전 의미·비교 불가 상태·판정 규칙은 #650의 미결 설계다. 출처(#368→#685)와 별도 진행하며 RES-12 포맷 전환이나 철회된 대장을 선행으로 두지 않는다. 생산·소비 Set 및 프로젝트 조회 API의 접점은 팀 논의 사항이다.
