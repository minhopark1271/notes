# 공통 영역 작업 카드

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md). 설계 반영과 구현 완료는 구분한다.

교차검토 반영본. 최종 통합 정본은 [전체 목록](../03_TASK_CATALOG.md)이다.

## PRJ-01

**프로젝트 교체 전에 모든 모듈의 모델 연결과 진행 중 요청을 정리한다**

- 모듈: 프로젝트 / 모듈 수명
- 판정: 착수 가능 · 제안 우선순위 P1 · 측면 태그 A, B, E
- 사용자 결과: 프로젝트 A의 모델·비동기 결과가 프로젝트 B의 화면에 사용되지 않는다.
- 선행: 없음
- 기존 이슈: [#246](https://github.com/NumeRealWorks/DashOpti_GUI/issues/246), [#431](https://github.com/NumeRealWorks/DashOpti_GUI/issues/431), [#551](https://github.com/NumeRealWorks/DashOpti_GUI/issues/551)

**변경 범위**

- Open/New/Close 경로에서 모델 삭제 전 모듈 위젯·PM 해제 순서를 한곳에 둔다
- Analysis Launcher/Builder/Runner/Optimizer/Condition/CAD/Geometry의 setModel(nullptr)·clear 계약과 null 진입을 맞춘다
- 기존 Runner QPointer·Morphing reset을 보존하고 실행 중 전환의 차단/취소/결과폐기 경계를 기록한다

**완료 조건**

- 어느 모듈을 연 상태에서도 A→B→A 전환에 해제 모델 역참조·중복 연결이 없다
- 실패한 프로젝트 열기 뒤에도 이전 화면/선택을 새 프로젝트 상태로 오인하지 않는다
- 늦은 완료 콜백은 삭제된 Set/이전 프로젝트에 쓰지 않는다

**검증 방법**

- 모듈별 전환·Set 삭제 QSignalSpy/수명 테스트
- 느린 작업 완료 직전 프로젝트 전환 Windows GUI 회귀

**근거**

- `model/DashProject.cpp:60 SetProjectPath, :1350 clearAllSets`
- `controller/DashProjectManager.cpp:115 OpenProjectFromFolder`
- `view/DashMainWindow.cpp:985 setModel(nullptr), :4209 resetMorphingEntry`

**범위·결정 메모**

Runner/Optimizer 개별 실행의 요청 귀속은 downstream 카드가 소유한다. 옛 7개라는 수를 고정하지 않고 현재 모듈 목록으로 검증한다.

## PRJ-02

**Set 개명 시 설정·산출물·참조를 함께 바꾸고 실패를 되돌린다**

- 모듈: 프로젝트 / Set 관리
- 판정: 착수 가능 · 제안 우선순위 P1 · 측면 태그 A, C, D
- 사용자 결과: 허용된 Set의 개명 뒤 기존 결과와 참조를 계속 사용할 수 있다.
- 선행: 없음
- 기존 이슈: [#562](https://github.com/NumeRealWorks/DashOpti_GUI/issues/562)

**변경 범위**

- 현재 Rename 허용 모듈만 대상으로 config·모듈 폴더·참조 표기 변경 계획을 계산한다
- 파일 작업 성공 후 메모리·트리 이름을 전환하고 중간 실패는 복구한다
- setId를 유지하고 동명 충돌·부분 변경·없는 설정파일의 의미를 명확히 한다

**완료 조건**

- 변경 후 재시작해도 이전 결과/상류 참조를 찾는다
- 폴더 충돌·권한 실패 시 기존 이름/파일/참조가 모두 유지된다
- 고정명 Geometry/DOE의 Rename 금지 정책을 유지한다

**검증 방법**

- 임시 디렉터리에서 중간 실패 주입 및 rename 왕복
- Builder/Runner/Optimizer Set 개명 후 실행/조회

**근거**

- `model/DashProject.cpp:1700 renameSet`
- `sources/pr-654.diff: VTP 영속 제거 예정`
- `sources/issues/599.md: 고정 Set명`

**범위·결정 메모**

PR654 이후 Geometry VTP를 새로 개명하는 코드를 만들지 않는다. 파일 이름 기준 저장을 유지하는 모듈의 실제 잔여만 대상으로 한다. #562 본문의 추가 개정과 PR681 완료 조건 정합은 팀 논의용 계획이며 아직 GitHub 반영 완료로 보지 않는다. 개명 결함 수정에 #368·#685를 선행으로 두지 않는다.

## PRJ-03

**Sampler·Launcher·Builder의 입력 참조와 산출물 출처 기록 계약을 적용한다**

- 모듈: 프로젝트 / 파이프라인 참조
- 판정: 착수 가능 · 제안 우선순위 P1 · 측면 태그 A, C
- 사용자 결과: 현재 입력 선택과 생성 당시 실제 출처를 구분하고 Builder model_info.json까지 공통 형식으로 기록한다.
- 선행: 없음
- 기존 이슈: [#368](https://github.com/NumeRealWorks/DashOpti_GUI/issues/368), [#443](https://github.com/NumeRealWorks/DashOpti_GUI/issues/443), [#470](https://github.com/NumeRealWorks/DashOpti_GUI/issues/470)

**변경 범위**

- 완료된 #520의 Set JSON setId 발급·영속·역조회를 사용한다. 조합 ID와 최초 입력 영구 고정은 폐기한다.
- DOE Sampler의 Geometry·Condition, Launcher의 DOE Sampler, Builder의 Analysis Launcher 입력 참조를 setId로 저장·복원한다.
- 실제 사용한 개별 setId·deck·데이터셋·응답·모델·part 선택 정보를 산출물에 기록하고 공통 판독·검증 계약을 제공한다.
- Builder model_info.json 생성까지 담당하며 Runner·Optimizer 소비 경계는 PRJ-04(#685)로 넘긴다.

**완료 조건**

- 현재 Set의 setId는 유지하고 상류 입력 참조는 다른 setId로 변경할 수 있다. 선택 변경만으로 기존 산출물 출처를 수정하지 않으며 재실행 덮어쓰기 때 실제 입력 출처도 함께 갱신한다. 과거 산출물·출처의 전체 이력 보존은 요구하지 않는다.
- 삭제 후 동명 재생성한 Set은 기존 입력으로 자동 연결하지 않고 개명한 기존 Set은 같은 ID로 찾는다.
- 필수 출처 없는 구버전 산출물은 재생성을 안내하고 사용을 거부한다. 이름·경로 추론 및 자동 출처 이관은 하지 않으며 기존 Set ID 발급·복원은 유지한다.
- 선택 입력과 산출물은 공통 출처 검증을 통과해야 실행할 수 있다. 출처 검증 자체를 같은 Set 재실행 여부·최신성 보장으로 설명하지 않는다.

**검증 방법**

- 상류 A→B 선택 변경 후 현재 참조와 기존 산출물 출처 분리, 재실행 덮어쓰기 후 실제 출처 동시 갱신 검증
- 개명·동명 재생성·출처 누락·프로젝트 재열기 및 DOE→Launcher→Builder model_info.json 왕복 검증

**근거**

- `Issue-Revision-History.md: 2026-10-08 개정 반영 및 현재 방향`
- `model/DashSetIdentity.cpp: ensureAll`
- `model/DashModelBuilder.cpp: model_info.json 생성`

**범위·결정 메모**

PR530은 2026-10-07 조회에서 미병합 CLOSED인 과거 참고다. 옛 조합 스탬프 구현의 재이식을 완료 조건으로 삼지 않는다. #650 버전·최신성, #369 NodeSet, #473 결과 조작은 별도 작업이며 #681 머지 조건으로 묶지 않는다.

## PRJ-04

**Runner·Optimizer의 Builder 참조를 setId로 전환하고 출처를 검증한다**

- 모듈: Runner / Optimizer 입력 참조
- 판정: 선행 작업 후 · 제안 우선순위 P1 · 측면 태그 A, C, E
- 사용자 결과: Builder 입력을 개명·재시작에도 같은 Set으로 복원하고 검증된 산출물을 실행·조회·프리뷰에 사용한다.
- 선행: PRJ-03
- 기존 이슈: [#443](https://github.com/NumeRealWorks/DashOpti_GUI/issues/443), [#685](https://github.com/NumeRealWorks/DashOpti_GUI/issues/685)

**변경 범위**

- #368(PRJ-03)의 공통 판독 계약으로 Builder model_info.json을 소비한다. 생산 계약을 중복 정의하지 않는다.
- Builder setId와 데이터셋·응답·모델·part 선택을 저장·복원하며 다른 Builder setId로 변경을 허용한다.
- 출처 검증 후 ID로 해석한 실제 경로를 외부 실행에 전달하고 실행·조회·프리뷰가 같은 출처를 사용하게 한다.

**완료 조건**

- 현재 Set의 setId는 유지하고 상류 입력 참조는 다른 setId로 변경할 수 있다. 선택 변경만으로 기존 산출물 출처를 수정하지 않으며 재실행 덮어쓰기 때 실제 입력 출처도 함께 갱신한다. 과거 산출물·출처의 전체 이력 보존은 요구하지 않는다.
- 개명은 같은 ID로 복원하고 삭제·동명 재생성에는 자동 재바인딩하지 않는다. 필수 출처 없는 구모델은 재생성을 요구한다.
- Runner·Optimizer 실행·조회·프리뷰에서 공통 출처 판독 결과와 세부 선택이 일치한다. 이름·경로로 누락 출처를 추정하지 않는다.

**검증 방법**

- Builder A→B 변경·재열기·개명·동명 재생성·필수 출처 누락 회귀
- Sim/MCU 모델 선택과 Optimizer 실행·프리뷰의 실제 전달 경로 및 출처 대조

**근거**

- `Issue-Revision-History.md: 2026-10-08 개정 반영 및 현재 방향`
- `model/DashModelRunner.cpp: loadModelInfoFromFolder`
- `model/DashOptimizer.cpp: Builder 선택·프리뷰`

**범위·결정 메모**

#685는 #443 하위이며 #368 선행이다. 기존 #520 Set JSON과 역조회를 사용하며 별도 Set 원장·ID 폴더 전환은 도입하지 않는다. #650 버전 판정은 PRJ-11과 모듈별 버전 카드 소관이다. #513의 비동기 로드, #562의 개명 결함과 접점만 조율하고 #681 머지 선행으로 두지 않는다.

## PRJ-05

**철회: 별도 실행·산출물 대장 구축**

- 모듈: 프로젝트 / 산출물 기록
- 판정: 철회 기록(실행 제외) · 제안 우선순위 P2 · 측면 태그 A, C
- 사용자 결과: 2026-10-08 #471 취소 결정에 따라 별도 대장 구현과 과거 소비 이력 보존을 요구하지 않는다.
- 선행: 없음
- 기존 이슈: [#471](https://github.com/NumeRealWorks/DashOpti_GUI/issues/471)

**변경 범위**

- 이 ID는 이전 목록과의 추적을 위해 철회 기록으로만 보존한다. 현재 실행 작업이 아니다.

**완료 조건**

- 별도 생산·소비 대장, 새로운 전역 산출물 ID 체계, 전체 이력 보존을 완료 조건에서 제거한다.

**검증 방법**

- 활성 카드·이슈 대응·의존 순서에서 이 철회 카드를 구현 작업으로 참조하지 않는지 검사한다.

**근거**

- `Issue-Revision-History.md: 2026-10-08 개정 반영 및 현재 방향`

**범위·결정 메모**

출처 추적 상위 #470은 유지한다. 현재 Set·산출물 기록은 PRJ-03(#368)→PRJ-04(#685), 버전·최신성은 PRJ-11(#650)에서 다룬다. 프로젝트는 원본 기록을 조회·집계하며 중복 원장을 만들지 않는다.

## PRJ-06

**Save와 Save As의 성공 판정을 실제 저장 결과와 일치시킨다**

- 모듈: 프로젝트 / 저장·열기
- 판정: 착수 가능 · 제안 우선순위 P1 · 측면 태그 A, D
- 사용자 결과: 저장 실패를 성공으로 표시하지 않고 복사 실패로 원본/대상 프로젝트를 잃지 않는다.
- 선행: 없음
- 기존 이슈: [#394](https://github.com/NumeRealWorks/DashOpti_GUI/issues/394), [#432](https://github.com/NumeRealWorks/DashOpti_GUI/issues/432), [#485](https://github.com/NumeRealWorks/DashOpti_GUI/issues/485)

**변경 범위**

- SaveProject() true 고정의 의미를 명시하고 모듈의 미저장 편집을 실제 저장하거나 실패를 반환한다
- Save As에서 원본/동일·하위 대상 경로를 검사하고 임시 대상에 완성한 뒤 교체한다
- 파일별 복사 결과·외부 참조/프로젝트 assets 포함 범위를 검증하고 전부 성공한 뒤 프로젝트 root를 전환한다

**완료 조건**

- 복사 실패 시 활성 프로젝트 경로와 기존 대상이 보존된다
- 동일 경로/원본 하위 경로 저장이 원본 삭제나 무한 재귀를 만들지 않는다
- 새 위치에서 열었을 때 설정뿐 아니라 참조 파일·결과를 찾는다

**검증 방법**

- 임시 디렉터리 동일경로/권한실패/기존대상/부분복사 테스트
- Save As 뒤 원래 폴더 접근 없이 새 프로젝트 재열기

**근거**

- `controller/DashProjectManager.cpp:181 SaveProject, :186 SaveProjectAs`
- `view/DashMainWindow.cpp:4415 onFileSave, :4458 onFileSaveAs`
- `sources/issues/394.md`

**범위·결정 메모**

#394는 보드 밖 추가 근거. 파괴적 대상 선삭제와 오류 무시는 코드로 확인, 실제 복사 실험은 하지 않았다.

## PRJ-07

**미저장 변경이 있는 종료·프로젝트 교체에 저장 선택을 제공한다**

- 모듈: 프로젝트 / 종료
- 판정: 선행 작업 후 · 제안 우선순위 P1 · 측면 태그 A, D
- 사용자 결과: 사용자가 편집을 잃는 지점에서 저장/버리기/취소를 선택한다.
- 선행: PRJ-06, PRJ-01
- 기존 이슈: [#485](https://github.com/NumeRealWorks/DashOpti_GUI/issues/485)

**변경 범위**

- 편집/저장 성공에 따른 dirty 상태를 프로젝트로 집계한다
- 타이틀바·Alt+F4·New/Open/Close에 같은 전환 확인을 연결한다
- 저장 실패와 사용자 취소는 종료/교체를 막는다

**완료 조건**

- 읽기·선택만으로 dirty가 되지 않고 저장 성공 후에만 해제된다
- 종료/교체 취소 시 기존 화면·모델·실행이 유지된다
- 진행 중 작업의 결과 저장 정책과 충돌하지 않는다

**검증 방법**

- dirty 상태 전이 테스트
- 저장실패·취소·작업중 종료 GUI 시나리오

**근거**

- `controller/DashProjectManager.cpp:181 SaveProject`
- `view/DashTitleBar.cpp:166 onCloseClicked`
- `view/DashMainWindow.h: closeEvent override 부재`

## PRJ-08

**같은 프로젝트를 두 앱이 수정하지 못하도록 잠근다**

- 모듈: 프로젝트 / 동시 접근
- 판정: 착수 가능 · 제안 우선순위 P1 · 측면 태그 A
- 사용자 결과: 두 인스턴스의 저장·워처 처리가 같은 파일을 덮어쓰지 않는다.
- 선행: 없음
- 기존 이슈: [#486](https://github.com/NumeRealWorks/DashOpti_GUI/issues/486)

**변경 범위**

- 프로젝트 root에 QLockFile 소유를 두고 Open/Create/Close/Save As에 연결한다
- 잠금 충돌과 stale lock의 사용자 처리 기준을 명시한다

**완료 조건**

- 두 번째 인스턴스는 원본 파일을 쓰기 전에 진단한다
- 정상 종료 후 재열기 가능하고 비정상 종료의 잔여 잠금을 구별한다

**검증 방법**

- 서브프로세스 두 개의 잠금 충돌/정상해제 테스트
- 크래시 잔여 잠금 재열기 수동검증

**근거**

- `controller/DashProjectManager.cpp:115, :141, :235`
- `research/root_evidence_storage.txt: QLockFile 생산코드 없음`

## PRJ-09

**프로젝트의 Set 복원·개명·참조 조회에 필요한 IO 경계를 명시한다**

- 모듈: 프로젝트 / 모델 의존
- 판정: 착수 가능 · 제안 우선순위 P2 · 측면 태그 A, E
- 사용자 결과: 모델 로직이 전역 ProjectManager를 되불러 다른 프로젝트 상태를 읽지 않는다.
- 선행: 없음
- 기존 이슈: [#246](https://github.com/NumeRealWorks/DashOpti_GUI/issues/246), [#432](https://github.com/NumeRealWorks/DashOpti_GUI/issues/432), [#508](https://github.com/NumeRealWorks/DashOpti_GUI/issues/508)

**변경 범위**

- DashProject의 registerReferenceModel/referenceModelChangedOnDisk/restoreExistingModules/renameSet에서 필요한 root·config·참조 파일 조회를 생성 시 주입한다.
- DashProjectManager의 SetProjectDirectory에서 DashIOController와 DashProject의 초기화 순서를 정리하고 root 교체 시 전달값을 갱신한다.
- 모델별 소비 이관용 작은 계면을 이 첫 실제 소비와 함께 정의한다; 전역 객체를 하나 더 포장하는 서비스 로케이터는 만들지 않는다.

**완료 조건**

- 위 네 경로가 전역 ProjectManager를 읽지 않고 전달된 프로젝트 IO만 사용한다.
- 두 root fixture에서 복원·참조 등록·개명이 격리되어 동작한다.
- 실패 가능한 IO의 오류가 호출자에게 반환되고 PRJ-02·PRJ-06의 실패 정책과 맞는다.

**검증 방법**

- 프로젝트 두 개의 경로 격리 단위검증
- 변경한 모델의 저장/실행 기존 테스트

**근거**

- `research/root_evidence_project_dependency.txt`
- `controller/DashIOController.cpp`
- `model/DashProject.cpp:97 registerReferenceModel`

**범위·결정 메모**

첫 완결 경계를 DashProject의 네 함수와 생성/전환부로 고정했다. 모듈 소비 이관은 IO-07~09가 소유한다. #570 대기는 해소됨.

## PRJ-10

**DashManager의 프로세스·설정 접근을 명시적인 소유자로 이관한다**

- 모듈: 공통 서비스 / 소유권
- 판정: 착수 가능 · 제안 우선순위 P2 · 측면 태그 B, E
- 사용자 결과: 모핑 이관 뒤 남은 전역 서비스 접근의 수명과 생성 순서가 드러난다.
- 선행: 없음
- 기존 이슈: [#246](https://github.com/NumeRealWorks/DashOpti_GUI/issues/246), [#434](https://github.com/NumeRealWorks/DashOpti_GUI/issues/434), [#508](https://github.com/NumeRealWorks/DashOpti_GUI/issues/508)

**변경 범위**

- 현재 남은 NxCad/journal/MCU/sensitivity daemon·solver paths·CPU 설정 접근을 소비자 생성부에 주입한다
- 실행 서비스의 앱 수명과 창 닫힘 후 지속 계약을 유지한다
- render/interaction은 VIS 작업과, 프로젝트 경로는 PRJ-09와 경계를 나눈다

**완료 조건**

- 창 닫힘이 실행을 죽이지 않고 앱 종료만 모든 프로세스를 회수한다
- 한 소비자 교체가 다른 서비스의 준비 상태를 바꾸지 않는다
- 이미 제거된 morphing facade/service lane을 다시 만들지 않는다

**검증 방법**

- TestDaemonLifecycle/TestProcessRuntime
- NX/MCU/sensitivity 소비자 생성·종료 smoke

**근거**

- `controller/DashManager.h:88 daemon members, :119 solver paths`
- `sources/issues/586.md`
- `sources/issues/605.md`

**범위·결정 메모**

광범위 God-object 해체 부모를 유지하지 않고 현존 소유 묶음만 다룬다. 렌더 주입은 geometry 보고와 통합한다.

## IO-01

**기존 저장 기반의 버전 판별·오류 반환·왕복 검증 계약을 완성한다**

- 모듈: 공통 저장
- 판정: 착수 가능 · 제안 우선순위 P2 · 측면 태그 A, C, E
- 사용자 결과: 저장 기반을 새로 만들지 않고 소비자가 안전하게 사용할 조건을 갖춘다.
- 선행: 없음
- 기존 이슈: [#247](https://github.com/NumeRealWorks/DashOpti_GUI/issues/247), [#478](https://github.com/NumeRealWorks/DashOpti_GUI/issues/478), [#479](https://github.com/NumeRealWorks/DashOpti_GUI/issues/479), [#480](https://github.com/NumeRealWorks/DashOpti_GUI/issues/480), [#584](https://github.com/NumeRealWorks/DashOpti_GUI/issues/584)

**변경 범위**

- DashSaveSystem의 지원 format/class version 검증과 문서 오류 반환을 명확히 한다
- legacy QJsonObject 파일의 기존 키/부분 갱신 보존과 typed 문서 이행 경계를 정한다
- 첫 legacy 소비자를 기존 writeJsonFile/QSaveFile 경계로 연결하고 오류 경로를 회귀검증한다

**완료 조건**

- 미지원 버전은 변경 전에 거절되며 원본 파일이 보존된다
- 저장→로드→재저장으로 의미 값과 id가 같고 잘못된 타입을 묵살하지 않는다
- 기존 GadgetCodec과 SaveSystem을 동시에 확산하는 새 중복 체계를 만들지 않는다

**검증 방법**

- TestGadgetCodec/TestMvvmBase 및 persistence 버전·쓰기실패 fixture
- zero-byte/corrupt/object-vs-array 정책 분리 테스트

**근거**

- `persistence/DashSaveSystem.cpp:521 loadDocument, :569 writeJsonFile`
- `persistence/DashSaveData.h:57`
- `docs/persistence.md: codec 미사용 및 비원자적 load 설명`

**범위·결정 메모**

QSaveFile과 version 필드는 이미 있다. registered-object 참조 누락 qFatal는 명시된 설계이므로 임의 변경하지 않고 도메인 적용 시 잘못된 파일의 선검증/오류 경계를 결정한다.

## IO-02

**파라미터 설정의 저장·복원·부분 갱신을 공용 계약으로 맞춘다**

- 모듈: Geometry / Condition 설정 저장
- 판정: 선행 작업 후 · 제안 우선순위 P2 · 측면 태그 A, C
- 사용자 결과: Geometry/CAD/Condition 설정을 다시 열어도 사용자가 지정한 값과 참조가 유지된다.
- 선행: IO-01
- 기존 이슈: [#478](https://github.com/NumeRealWorks/DashOpti_GUI/issues/478), [#479](https://github.com/NumeRealWorks/DashOpti_GUI/issues/479), [#480](https://github.com/NumeRealWorks/DashOpti_GUI/issues/480)

**변경 범위**

- 현재 GP/CP QSaveFile 사용은 보존하고 CAD/레거시 직접 쓰기와 누락 필드를 적용 대상으로 대조한다
- GEO 상태기 JSON 정책을 따른 뒤 모듈별 설정 round-trip fixture를 만든다
- unknown/미지원 버전·읽기실패에서 기본값으로 원본을 덮어쓰지 않게 한다

**완료 조건**

- 모듈별 실제 설정을 저장/재열기/재저장해 비교한다
- 실패 시 원본과 마지막 유효 모델 상태가 유지된다
- 핸들/Constraints 도메인 변경은 GEO 카드와 중복 구현하지 않는다

**검증 방법**

- GP/CAD/CP fixture 왕복·손상파일·부분갱신 테스트

**근거**

- `model/DashGeometryParameter.cpp:289`
- `model/DashConditionParameterization.cpp:645`
- `model/DashGeometryParameterCAD.cpp: settings persistence`
- `viewmodel/DashGeometryParameterPresentationModel.cpp`

**범위·결정 메모**

typed object 전면 이행은 완료 조건이 아니다. 기존 파일 호환·무손실 왕복을 우선한다.

## IO-03

**DOE·Launcher 설정과 결과 메타데이터의 쓰기 실패를 보존·보고한다**

- 모듈: DOE / Analysis Launcher 설정 저장
- 판정: 선행 작업 후 · 제안 우선순위 P2 · 측면 태그 A, C
- 사용자 결과: 실행 설정 저장이 실패했는데 성공한 설정으로 실행하거나 원본을 손상하지 않는다.
- 선행: IO-01
- 기존 이슈: [#478](https://github.com/NumeRealWorks/DashOpti_GUI/issues/478), [#479](https://github.com/NumeRealWorks/DashOpti_GUI/issues/479), [#480](https://github.com/NumeRealWorks/DashOpti_GUI/issues/480)

**변경 범위**

- DOE 직접 Truncate 쓰기와 Launcher의 이미 원자화된 Config 계면을 같은 오류 계약으로 연결한다
- 실행 state journal과 설정 저장의 책임을 AL 상태분리 카드와 맞춘다
- 모듈 JSON의 version/round-trip coverage를 추가한다

**완료 조건**

- 공간 부족·쓰기실패에서 이전 설정 유지 및 실행 전 오류 보고
- 케이스 상태 갱신이 정적 설정/선택 DV를 덮어쓰지 않는다

**검증 방법**

- DOE/Launcher 설정 왕복·쓰기실패·동시 상태갱신 fixture

**근거**

- `model/DashDoeSampler.cpp:1310`
- `model/preprocessor/DashAnalysisLauncherConfig.cpp:44 QSaveFile`

**범위·결정 메모**

#638 empty-file/error 문구는 RES/AL specific 카드가 소유한다. 이미 구현된 QSaveFile을 재도입하지 않는다.

## IO-04

**학습·예측·최적화 설정의 저장을 원자화하고 왕복 검증한다**

- 모듈: Builder / Runner / Optimizer 설정 저장
- 판정: 선행 작업 후 · 제안 우선순위 P1 · 측면 태그 A, C
- 사용자 결과: 중단·저장 실패 후에도 기존 설정과 모델 메타데이터가 유효하다.
- 선행: IO-01
- 기존 이슈: [#478](https://github.com/NumeRealWorks/DashOpti_GUI/issues/478), [#479](https://github.com/NumeRealWorks/DashOpti_GUI/issues/479), [#480](https://github.com/NumeRealWorks/DashOpti_GUI/issues/480)

**변경 범위**

- Builder config/model_info, Runner settings, Optimizer settings의 직접 Truncate 쓰기를 공용 파일 계약으로 치환한다
- 현재 실제 쓰는 동적 파라미터·Dataset/Data Label·모델 메타데이터 파일의 원자성/버전/오류 전파와 fixture만 대조한다. 삭제된 Analyzer 설정 영속화는 되살리지 않는다.
- 필드 누락의 기능 수정은 downstream 카드에 두고 저장기제와 fixture를 통합한다

**완료 조건**

- 각 모듈 대표 설정의 왕복 값/타입/id가 유지된다
- 실패한 쓰기 뒤 이전 파일과 사용자 편집이 보존된다
- 설정 실패를 후속 프로세스 실행 성공으로 오인하지 않는다

**검증 방법**

- 모듈별 파일 실패주입·schema migration·왕복 fixture

**근거**

- `model/DashModelBuilder.cpp:520, :602, :934`
- `model/DashModelRunner.cpp:589`
- `model/DashOptimizer.cpp:395`

## IO-06

**설정 기본값의 소유자와 누락·오류·사용자값 구분을 통일한다**

- 모듈: 공통 설정
- 판정: 착수 가능 · 제안 우선순위 P2 · 측면 태그 A, C
- 사용자 결과: 같은 설정이 진입 경로마다 다른 기본값으로 조용히 바뀌지 않는다.
- 선행: 없음
- 기존 이슈: [#423](https://github.com/NumeRealWorks/DashOpti_GUI/issues/423)

**변경 범위**

- 모핑 반경·solver 옵션을 첫 적용 대상으로 도메인 기본값 한곳을 정한다
- UI 초기표시/새 Set/기존 파일 누락/잘못된 값의 처리 표를 만든다
- 기본값으로 대체한 경우 이유·필드를 로그에 남기고 valid zero와 missing을 구분한다

**완료 조건**

- 동일 Set을 다른 진입 경로로 열어도 기본값/저장값이 같다
- 잘못된 값과 누락이 명시된 정책대로 처리되고 정상 0을 잃지 않는다

**검증 방법**

- 파라미터 기본값 표 기반 load/new/reopen 회귀

**근거**

- `sources/issues/423.md`
- `controller/DashMorphingRun.h`
- `model/DashGeometryParameter.cpp`

**범위·결정 메모**

모든 숫자의 기본값을 이 PR에서 한 번에 이동하지 않는다. Runner valid-zero·범위 결함은 RUN 카드가 독립 수정한다.

## ASY-01

**비동기 작업의 준비·실행·완료 계약과 제출 결과를 명시한다**

- 모듈: 공통 비동기 실행기
- 판정: 착수 가능 · 제안 우선순위 P2 · 측면 태그 B, E
- 사용자 결과: 호출자가 준비 실패·생략·반려·실행 완료를 구분하고 스레드 경계를 읽을 수 있다.
- 선행: 없음
- 기존 이슈: [#451](https://github.com/NumeRealWorks/DashOpti_GUI/issues/451), [#553](https://github.com/NumeRealWorks/DashOpti_GUI/issues/553)

**변경 범위**

- run의 위치 람다 세 개를 명시된 job/hook 구조로 재구성하고 Analyzer 첫 소비자를 함께 치환한다
- Skipped/Aborted 등 상태 확장은 기존 ProcessJob의 terminal 동작과 충돌 없이 검증한다
- 준비 단계의 동기 실행 판단과 null submission 반려 결과를 호출자에게 노출한다
- preExecution이 던진 예외를 GUI 이벤트 루프 밖으로 내보내지 않고 표준 실패로 정규화한다.

**완료 조건**

- GUI/worker 훅이 지정 스레드에서만 실행된다
- 성공·실패·준비중단·생략·busy 반려 모두 slot/UI를 남기지 않는다
- 공유 ProcessJob 테스트가 깨지지 않는다
- 준비 훅 예외에도 slot/UI가 정확히 회수되고 실행 훅이 호출되지 않는다; worker/완료 훅의 예외 계약은 별도 명시한다.

**검증 방법**

- TestAsyncJob/TestJobState 실패·반려·빠른 완료·shutdown 검증
- prepare가 예외를 던지는 테스트: failure 1회·UI unblock·다음 제출 가능

**근거**

- `controller/async/DashAsyncJobRunner.h:48 run`
- `controller/async/DashAsyncJobRunner.cpp:26 run`
- `controller/async/Job.h`

**범위·결정 메모**

이미 비동기 기반은 존재한다. 각 모듈 worker 이관의 무조건 선행으로 삼지 않는다.

## ASY-02

**작업 상태에 따른 진행 표시·입력 차단·취소 표시를 한 방식으로 연결한다**

- 모듈: 공통 실행 UI
- 판정: 착수 가능 · 제안 우선순위 P2 · 측면 태그 B, D
- 사용자 결과: 어떤 작업이 도는지 보이고 작업 중에도 창을 움직일 수 있다.
- 선행: 없음
- 기존 이슈: [#460](https://github.com/NumeRealWorks/DashOpti_GUI/issues/460), [#461](https://github.com/NumeRealWorks/DashOpti_GUI/issues/461), [#462](https://github.com/NumeRealWorks/DashOpti_GUI/issues/462), [#463](https://github.com/NumeRealWorks/DashOpti_GUI/issues/463), [#543](https://github.com/NumeRealWorks/DashOpti_GUI/issues/543)

**변경 범위**

- DashAsyncJobRunner block hooks와 MainWindow setUIEnabled/loading 표시의 중복 책임을 정리한다
- 작업 문구·유한/무한 진행·반려 안내·중복 실행 가드 계약을 정하고 Analyzer에 적용한다
- 실제 취소를 지원하는 작업에만 취소 버튼을 연결한다

**완료 조건**

- 성공/실패/반려/프로젝트 종료 후 UI가 항상 복구된다
- 제목줄 이동·리사이즈를 작업 입력과 분리한다
- 취소 불가 SDK 작업에 작동하지 않는 취소 버튼을 내지 않는다

**검증 방법**

- 빠른 완료/실패/중복제출 UI 테스트
- Analyzer 큰 XML 작업 중 창 이동 및 종료 수동검증

**근거**

- `controller/async/DashAsyncJobRunner.cpp:59 onUnblock`
- `view/DashMainWindow.cpp: setUiBlockHooks, setUIEnabled`
- `sources/issues/543.md`

**범위·결정 메모**

BLD/RUN/OPT/AL 각 실행 배선은 모듈 카드 소유. 작업 진행률 생산 API의 없는 기능을 UI만으로 약속하지 않는다.

## ASY-03

**데몬 명령 응답에 요청별 시한과 종결 처리를 둔다**

- 모듈: 공통 데몬 실행
- 판정: 착수 가능 · 제안 우선순위 P1 · 측면 태그 B
- 사용자 결과: 준비된 데몬이 응답을 잃어도 current command와 대기열이 영구 정지하지 않는다.
- 선행: 없음
- 기존 이슈: [#465](https://github.com/NumeRealWorks/DashOpti_GUI/issues/465), [#467](https://github.com/NumeRealWorks/DashOpti_GUI/issues/467)

**변경 범위**

- 이미 있는 ready/stop timeout은 유지하고 trySendNext 이후 명령 시한을 적용한다
- timeout 시 한 번의 failure와 현재/대기 요청 처리 정책을 연결한다
- timeout 이후 도착한 응답을 다음 요청의 성공으로 소비하지 않는다

**완료 조건**

- 무응답 명령은 유한 시간 안에 사유와 함께 종결된다
- 늦은 결과·강제 종료·재기동에서 중복 완료/다음 요청 오염이 없다

**검증 방법**

- daemon stub 무응답·늦은응답·재기동·queue cancel 테스트

**근거**

- `controller/DashExtensionProcess.cpp:288 ready timeout, :391 trySendNext`
- `controller/DashExtensionProcess.h: m_waitingFinished`

**범위·결정 메모**

기동 타임아웃 부재라는 옛 진단은 해결됨. 정책상 길이와 timeout 후 daemon 재사용 여부는 명령 종류별로 결정한다.

## ASY-04

**외부 프로그램 인코딩·nullable 서비스 경계를 실제 호출 계약에 맞춘다**

- 모듈: 외부 프로세스 공통
- 판정: 착수 가능 · 제안 우선순위 P2 · 측면 태그 B
- 사용자 결과: 한글 경로/실패 출력을 보존하고 초기화되지 않은 서비스 호출을 명시적으로 거절한다.
- 선행: 없음
- 기존 이슈: [#465](https://github.com/NumeRealWorks/DashOpti_GUI/issues/465), [#468](https://github.com/NumeRealWorks/DashOpti_GUI/issues/468), [#469](https://github.com/NumeRealWorks/DashOpti_GUI/issues/469)

**변경 범위**

- ProcessJob·ExtensionProcess의 이미 UTF-8인 경로를 기준으로 남은 fromLocal8Bit/명령줄 조립을 분류한다
- SDK/외부 exe가 다른 인코딩이면 경계 어댑터에 명시하고 임의 전역 치환을 피한다
- 실제로 null 가능한 process/session 경계만 가드하고 오류를 모듈에 전달한다

**완료 조건**

- 한글·공백 경로와 멀티바이트 분할 출력이 손상되지 않는다
- 미기동/종료중 서비스 호출은 crash나 무음 무시 대신 실패로 귀결된다

**검증 방법**

- LineAssembler/ProcessRuntime 비ASCII·split-byte 테스트
- 대상 exe별 Windows 출력 인코딩 smoke

**근거**

- `controller/DashExtensionProcess.cpp:414 toUtf8`
- `controller/async/LineAssembler.h`
- `research/root_evidence_process.txt`

**범위·결정 메모**

외부 SDK/exe별 실측 필요. 항상 존재하는 singleton 가드 제거(#508)는 PRJ 의존 주입/접근계약 변경에 흡수한다.

## ASY-05

**FEM 읽기·변환을 워커로 옮기고 진행 중 창 수명을 분리한다**

- 모듈: TopOpt 후처리 도구
- 판정: 착수 가능 · 제안 우선순위 P2 · 측면 태그 B, D
- 사용자 결과: TopOpt 도구에서 큰 FEM을 열 때 이벤트 펌핑 없이 UI가 응답한다.
- 선행: 없음
- 기존 이슈: [#451](https://github.com/NumeRealWorks/DashOpti_GUI/issues/451), [#455](https://github.com/NumeRealWorks/DashOpti_GUI/issues/455)

**변경 범위**

- onBrowseFem/parseFemToUnstructuredGrid의 입력 스냅샷·워커 파싱·GUI 반영을 분리한다
- showProgressMessage의 processEvents를 상태 신호로 바꾼다
- 닫힘/재선택/실패 시 늦은 결과와 진행 표시를 정리한다

**완료 조건**

- 긴 파싱 중 창 조작이 가능하고 이전 요청 결과가 새 선택을 덮지 않는다
- 오류/닫힘 후 작업·스피너·메모리가 정상 정리된다

**검증 방법**

- 유효/손상 FEM 파싱 테스트
- 큰 FEM 로드 중 닫기·재선택 Windows GUI 검증

**근거**

- `view/dialog/TopOptPostprocessDialog.cpp:240, :418, :1088, :1811`

**범위·결정 메모**

VTK 순수 데이터 생성과 renderer 반영 경계는 VIS 소유권 규칙을 따른다. 카운트 10곳을 목표로 하지 않는다.

## UI-01

**혼합 DPI 이동과 도크 재배치의 재진입·화면 이탈을 막는다**

- 모듈: 앱 창 / 도크
- 판정: 실측 필요 · 제안 우선순위 P1 · 측면 태그 D
- 사용자 결과: 배율이 다른 모니터 이동 후 창과 도크가 조작 가능한 영역에 남는다.
- 선행: 없음
- 기존 이슈: [#446](https://github.com/NumeRealWorks/DashOpti_GUI/issues/446), [#447](https://github.com/NumeRealWorks/DashOpti_GUI/issues/447), [#450](https://github.com/NumeRealWorks/DashOpti_GUI/issues/450)

**변경 범위**

- 수제 drag/resize 및 resizeDocks 재호출을 실제 mixed-DPI 시나리오로 재현한다
- 창 이동의 Qt/OS 위임과 재배치 중첩 방지·availableGeometry 보정을 적용한다
- 기동 QT_SCALE_FACTOR와 모니터 DPR 적용이 겹치는 경계를 정리한다

**완료 조건**

- 100/150/200% 모니터 왕복·최대화·복원·도킹에서 멈춤/팽창이 없다
- VTK/OCCT 뷰와 마우스 picking 좌표가 정합하다

**검증 방법**

- Windows 다중모니터 재현 행렬/수정전후 영상 또는 로그
- 크기 경계 계산 단위테스트

**근거**

- `view/DashTitleBar.cpp:82 mousePressEvent, :103 mouseMoveEvent`
- `view/DashMainWindow.cpp:5033 resizeEvent`
- `main.cpp:67 UI/scaleFactor`

**범위·결정 메모**

macOS 정적 조사에서 Windows 프리즈를 실증하지 않았다. 프레임리스/중첩 QMainWindow 전체 교체는 필요성 입증 뒤 선택; 즉시 필수 작업으로 확정하지 않는다.

## UI-02

**창 위치·크기·도크 구성을 저장하고 안전하게 복원한다**

- 모듈: 앱 창 / 도크
- 판정: 착수 가능 · 제안 우선순위 P2 · 측면 태그 D
- 사용자 결과: 재기동 후 사용자 작업 배치가 복원되고 없는 모니터로 창이 사라지지 않는다.
- 선행: 없음
- 기존 이슈: [#446](https://github.com/NumeRealWorks/DashOpti_GUI/issues/446), [#448](https://github.com/NumeRealWorks/DashOpti_GUI/issues/448)

**변경 범위**

- saveGeometry/saveState와 버전 있는 QSettings 키로 저장·복원한다
- 도크 objectName과 초기 생성 순서를 고정한다
- 배치 초기화 및 모니터 제거/해상도 변경 복구를 제공한다

**완료 조건**

- 재기동 후 도크/창 배치가 유지된다
- 손상·구버전 설정이나 모니터 제거 시 화면 내 기본 배치로 복원된다

**검증 방법**

- 설정 round-trip/구버전·손상값 테스트
- 도크 분리·다중모니터 제거 후 재기동

**근거**

- `view/DashMainWindow.cpp:4299 QSettings, :5040 resetLayout`
- `research/root_evidence_storage.txt: geometry/state 저장 부재`

## UI-03

**내용 크기와 도크 크기 결정을 레이아웃에 맡기고 강제 이벤트 flush를 없앤다**

- 모듈: 앱 레이아웃 / 오버레이
- 판정: 착수 가능 · 제안 우선순위 P2 · 측면 태그 D, E
- 사용자 결과: 모듈 전환·창 크기 변경에서 표와 오버레이가 일관되게 배치된다.
- 선행: 없음
- 기존 이슈: [#446](https://github.com/NumeRealWorks/DashOpti_GUI/issues/446), [#449](https://github.com/NumeRealWorks/DashOpti_GUI/issues/449), [#455](https://github.com/NumeRealWorks/DashOpti_GUI/issues/455)

**변경 범위**

- MainWindow 도크·ViewOptions adjustSize/processEvents·동적 표 높이를 우선 대상으로 sizeHint/sizePolicy로 정리한다
- 명령형 고정 크기 중 아이콘·디자인 토큰 의도값과 내용 의존값을 구분한다
- Geometry/CAD 동적 행 및 Analyzer 표의 잘림을 현재 구조로 회귀 확인한다

**완료 조건**

- 모듈 전환·글꼴 배율·도크 폭 변경에서 내용이 복구 불가능하게 잘리지 않는다
- ViewOptions 강제 processEvents 두 곳이 제거되고 다음 이벤트에서 올바르게 배치된다

**검증 방법**

- 대표 모듈 small/large font·resize screenshot 비교
- overlay show/hide/resize 반복 smoke

**근거**

- `view/overlay/DashViewOptionsWidget.cpp:82, :94`
- `view/DashMainWindow.cpp:4956 eventFilter`
- `research/root_evidence_ui.txt`

**범위·결정 메모**

모든 setFixedSize 호출을 결함으로 간주하지 않는다. 작업이 커지면 앱 shell과 동적 표 묶음으로 PR을 나눌 수 있다.

## UI-04

**QSettings 위치를 통일하고 최근 프로젝트를 다시 열 수 있게 한다**

- 모듈: 앱 설정 / 최근 프로젝트
- 판정: 착수 가능 · 제안 우선순위 P2 · 측면 태그 D
- 사용자 결과: 앱·UI·로그 설정이 한 정책을 따르고 최근 프로젝트 접근이 가능하다.
- 선행: 없음
- 기존 이슈: [#481](https://github.com/NumeRealWorks/DashOpti_GUI/issues/481)

**변경 범위**

- NohLab/DashOptiAnalyzer와 NumeReal/DashOpti 키의 이전/호환 규칙을 둔다
- 최근 프로젝트 목록의 중복·사라진 경로 처리를 File 메뉴에 연결한다
- 새로 열기 실패 시 현재 프로젝트 처리 정책을 기존 전환 계약과 맞춘다

**완료 조건**

- 기존 설정을 한 번 이관해 UI 배율/최근 경로를 잃지 않는다
- 최근 항목 삭제·없는 경로·같은 경로 표기 차이를 처리한다

**검증 방법**

- QSettings 임시 store migration 및 목록 테스트
- 최근 항목 열기 성공/실패 GUI 확인

**근거**

- `main.cpp:41, :67 QSettings`
- `view/DashMainWindow.cpp:259, :4299`

## UI-05

**실패·정보·확인의 통지 규칙과 공통 호출 표면을 맞춘다**

- 모듈: 사용자 통지
- 판정: 착수 가능 · 제안 우선순위 P2 · 측면 태그 D, G
- 사용자 결과: 같은 실패가 로그에만 숨거나 중복 모달로 나타나지 않는다.
- 선행: 없음
- 기존 이슈: [#466](https://github.com/NumeRealWorks/DashOpti_GUI/issues/466), [#482](https://github.com/NumeRealWorks/DashOpti_GUI/issues/482), [#490](https://github.com/NumeRealWorks/DashOpti_GUI/issues/490)

**변경 범위**

- 이미 있는 DashNotify를 사용하고 process/system failure·입력검증·사용자 확인을 구분한다
- MainWindow 파일 조작과 공통 다이얼로그의 직접 QMessageBox를 첫 적용 대상으로 정리한다
- 영어 고정 정책에 따라 바꾸는 호출부의 불완전 tr을 함께 정리한다

**완료 조건**

- 실패가 실행당 적절한 위치에서 한 번 보고되고 상세 사유를 확인할 수 있다
- 확인 대화상자의 Yes/No/Cancel 흐름이 유지된다
- 모듈별 terminal 실패 누락은 해당 BLD/OPT/AL 카드로 추적한다

**검증 방법**

- 파일열기/저장실패 및 취소 UI 시나리오
- 변경한 메시지 호출/중복 알림 점검

**근거**

- `utils/log/DashNotify.h`
- `view/DashMainWindow.cpp:4415 onFileSave`
- `research/root_evidence_process.txt`

**범위·결정 메모**

래퍼를 또 만들지 않는다. 이미 처리된 시스템 실패 79콜이나 현재 미확인 212콜 수를 새 완료 기준으로 쓰지 않는다.

## UI-06

**삭제 가능한 표의 콜백을 현재 항목에 결합한다**

- 모듈: 공통 표 위젯
- 판정: 착수 가능 · 제안 우선순위 P1 · 측면 태그 A, C, D
- 사용자 결과: 중간 행 삭제 후 Browse·미리보기·콤보가 다른 항목을 수정하지 않는다.
- 선행: 없음
- 기존 이슈: [#514](https://github.com/NumeRealWorks/DashOpti_GUI/issues/514)

**변경 범위**

- 공용 cell widget→현재 행 조회를 추가하고 MCU Builder/Runner의 Browse row 캡처를 치환한다.
- Runner preview의 미사용 row 인자를 제거하고 살아 있는 constraint/physics 행 해석 헬퍼를 정리한다.
- ReferenceFileWidget 삭제와 PR652 Direct 입력표 삭제로 소멸한 결함은 완료/대체로 처분한다. 새 단일파일 Dialog에 없는 행별 Browse를 구현하지 않는다.

**완료 조건**

- 중간 행 삭제 후 아래 행 조작은 그 항목만 변경한다
- 분리/삭제된 위젯 콜백은 파일선택·저장 등 부수효과 전에 중단한다

**검증 방법**

- 중첩 cellWidget descendant 행 해석 테스트
- MCU Builder/Runner 중간 행 삭제 후 Browse·Runner preview 회귀
- PR652 반영 후 옛 Direct 입력표 제거 확인

**근거**

- `view/DashModelRunnerMCUWidget.cpp:321`
- `view/DashModelBuilderMCUWidget.cpp:1515`
- `view/DashDoeSamplerDirectWidget.cpp:180`
- `view/DashModelRunnerWidget.cpp:2005`
- `sources/pr-652.diff`

**범위·결정 메모**

항목 자체의 id/산출물 삭제는 RUN/BLD 카드 소유. PR652가 삭제할 위젯에 먼저 수정하지 말고 머지 대상 구조로 옮긴다. #514와 #474의 중복 담당 확정은 GitHub 미반영 추가 개정 계획이다. 모든 표에 새 영속 ID를 추가하지 않는다.

## UI-07

**동작 없는 Undo/Redo와 출고용 플레이스홀더를 제거한다**

- 모듈: 앱 메뉴 / 도구
- 판정: 착수 가능 · 제안 우선순위 P3 · 측면 태그 D, G
- 사용자 결과: 사용자가 수행할 수 없는 동작이 작동하는 기능처럼 노출되지 않는다.
- 선행: 없음
- 기존 이슈: [#483](https://github.com/NumeRealWorks/DashOpti_GUI/issues/483), [#488](https://github.com/NumeRealWorks/DashOpti_GUI/issues/488)

**변경 범위**

- MainWindow Undo/Redo와 mesh 도구 emit-only 배선을 실제 수신 여부로 점검 후 제거한다
- 출고 빌드의 dummy action·개발자 로컬 경로·플레이스홀더 텍스트를 제거 또는 올바른 동작으로 연결한다
- 데모/테스트 자료와 실제 출고 경로를 구분한다

**완료 조건**

- Undo stack 없는 버튼/단축키/메뉴가 사용자 흐름에 남지 않는다
- Release smoke에서 개발자 경로·빈 기능이 노출되지 않는다

**검증 방법**

- action 연결 정적 점검 및 Release 메뉴 smoke

**근거**

- `view/DashMainWindow.cpp:4800 onEditUndo, :4806 onEditRedo`
- `view/dialog/MeshExportDialog.cpp:142 handleUndo`
- `view/dialog/PreprocessingWidget.cpp:166`

## UI-08

**남은 부분 번역 경로를 영어 고정 정책으로 정리한다**

- 모듈: 앱 표시 언어
- 판정: 착수 가능 · 제안 우선순위 P3 · 측면 태그 G
- 사용자 결과: 표시 언어 정책이 코드/리소스 전반에서 일관된다.
- 선행: 없음
- 기존 이슈: [#490](https://github.com/NumeRealWorks/DashOpti_GUI/issues/490)

**변경 범위**

- UI-05 변경 외 잔여 tr/QTranslator/.ts/.qm 사용을 다시 계수하고 영어 문자열로 수렴한다
- 영문 텍스트의 내부 키 사용·objectName 비교와 사용자 표시를 구분한다

**완료 조건**

- 표시 문자열 변경이 enum/key/저장 데이터 해석을 바꾸지 않는다
- 번역 리소스 없는 부분 적용이 남지 않는다

**검증 방법**

- 텍스트 검색 및 변경 모듈 UI smoke

**근거**

- `research/root_evidence_ui.txt`
- `view/DashMainWindow.cpp: tr 호출`
- `sources/issues/490.md`

**범위·결정 메모**

실제 다국어 기능 신설은 요청 범위 밖. UI-05와 한 PR에 합쳐도 된다.

## DEV-01

**Windows 빌드와 기존 테스트 레벨을 CI에 연결하고 시간을 기록한다**

- 모듈: 빌드 / CI
- 판정: 착수 가능 · 제안 우선순위 P2 · 측면 태그 F
- 사용자 결과: 개발자 훅을 우회해도 공용 환경에서 빌드·도메인 회귀를 확인한다.
- 선행: 없음
- 기존 이슈: [#372](https://github.com/NumeRealWorks/DashOpti_GUI/issues/372), [#489](https://github.com/NumeRealWorks/DashOpti_GUI/issues/489)

**변경 범위**

- GUI 저장소에 없는 CI 실행 정의를 지원 Windows toolchain/바이너리 캐시로 구성한다
- Level1/2 및 리소스 가능한 Level3를 구분하고 SKIP 사유/개수를 보고한다
- ctest 구간 시간을 기록하고 Level1 임시 건강 한도 초과는 알림으로 처리한다

**완료 조건**

- 깨끗한 checkout에서 app/test build와 선택 레벨이 실행된다
- 테스트가 0개이거나 필수 fixture 누락인데 성공인 척하지 않는다
- 시간 경고를 기능 테스트 실패와 구분한다

**검증 방법**

- 성공/실패/fixture 누락의 CI dry-run 및 결과 artifact 확인

**근거**

- `docs/test-levels.md: CI 연결 후속`
- `vcpkg-configuration.json: GUI는 CI 없는 leaf 소비자`
- `CMakePresets.json`
- `scripts/hooks/run-test-level.sh`

**범위·결정 메모**

러너·캐시·라이선스 제공은 환경 의존. macOS 조사에서 Windows 빌드를 실행하지 않았다. 도메인 테스트 추가는 각 모듈 카드의 수용 검증으로 분산한다.

## DEV-02

**지원 MSVC 도구 체인과 공급 캐시의 ABI를 맞춘다**

- 모듈: 빌드 / 의존성
- 판정: 실측 필요 · 제안 우선순위 P2 · 측면 태그 F
- 사용자 결과: 지원 개발 환경에서 의존성 바이너리를 일관되게 받을 수 있다.
- 선행: 없음
- 기존 이슈: [#330](https://github.com/NumeRealWorks/DashOpti_GUI/issues/330)

**변경 범위**

- 공급자와 소비자의 compiler/toolset/CRT/triplet/features 지문을 기록한다
- 지원 toolset 고정 또는 신규 cache 공급을 선택하고 setup 스크립트로 오류를 일찍 알린다
- GUI baseline 갱신과 clean machine 설치 절차를 함께 검증한다

**완료 조건**

- 지원 프리셋의 cold install이 의도한 binary cache를 쓴다
- 지원 밖 도구 체인은 알아볼 수 있는 진단을 낸다

**검증 방법**

- Windows clean cache configure/install/build 및 ABI 로그 비교

**근거**

- `CMakePresets.json: --x-abi-tools-use-exact-versions`
- `triplets/x64-windows-dashopti.cmake`
- `sources/issues/330.md`

**범위·결정 메모**

이슈의 MSVC 18.10.0을 최신 권장 버전으로 단정하지 않는다. 현재 공급 runner 지문 확인이 착수 조건이다.

## DEV-03

**vcpkg 이행 잔재를 정리하고 운영 문서를 현재 빌드에 맞춘다**

- 모듈: 빌드 / 배포
- 판정: 착수 가능 · 제안 우선순위 P3 · 측면 태그 F, G
- 사용자 결과: 사용되지 않는 헤더와 낡은 migration 설명이 새 개발자를 잘못 이끌지 않는다.
- 선행: 없음
- 기존 이슈: [#336](https://github.com/NumeRealWorks/DashOpti_GUI/issues/336)

**변경 범위**

- 추적/비추적 external 헤더와 CMake include 도달성을 확인해 미사용 경로를 제거 대상으로 명시한다
- migration 문서의 운영 지식만 현재 setup/deploy 문서로 보존한다
- Qt6 globalPosition 사용을 남은 수제 타이틀바에 적용한다

**완료 조건**

- clean checkout에 레거시 external이 없어도 빌드/런타임 배포가 성립한다
- 현 포트 feature/baseline/CRT 배포와 문서가 맞는다

**검증 방법**

- rg include 도달성·clean Windows build
- 한글경로/타이틀바 drag GUI smoke

**근거**

- `docs/vcpkg-migration-scope.md`
- `docs/vcpkg-migration-code-changes.md`
- `view/DashTitleBar.cpp:99, :112 globalPos`
- `CMakeLists.txt`

**범위·결정 메모**

비추적 개발자 개인 파일을 이번 조사에서 삭제하지 않는다. DashGizmo/MarchingPlane 배치는 VIS/GEO 카드 소유.

## DEV-04

**지원 Windows 배포물의 CRT 탐색을 표준 경로로 검증·정리한다**

- 모듈: 배포 / CRT
- 판정: 실측 필요 · 제안 우선순위 P2 · 측면 태그 F, G
- 사용자 결과: 개발 도구가 없는 PC에서도 배포물이 실행된다.
- 선행: 없음
- 기존 이슈: [#336](https://github.com/NumeRealWorks/DashOpti_GUI/issues/336)

**변경 범위**

- 현재 CMake/선택 toolset에서 InstallRequiredSystemLibraries 지원 여부를 확인한다
- 표준 모듈이 지원하면 수동 glob을 교체하고 미지원이면 실패 진단과 검증 가능한 fallback을 유지한다
- 실제 복사된 CRT/OpenMP/Qt plugin 목록을 패키지 검증에 넣는다

**완료 조건**

- 지원 toolset마다 필요한 runtime이 배포되고 개발 PC 시스템 DLL에 기대지 않는다
- 없는 redist 디렉터리를 조용히 건너뛰지 않는다

**검증 방법**

- Visual Studio 없는 Windows VM package smoke 및 DLL 로드 확인

**근거**

- `CMakeLists.txt: CRT/redist 복사`
- `sources/issues/336.md: 당시 CMake 3.31 제약`

**범위·결정 메모**

옛 CMake 업스트림 대기를 현재 blocker로 확정하지 않는다. DEV-02 toolset 선택 결과와 맞춘다.

## DEV-05

**registry 과거 버전·주석과 필요한 해석 SDK 공급을 정합화한다**

- 모듈: 외부 registry / SDK 공급
- 판정: 실측 필요 · 제안 우선순위 P2 · 측면 태그 F
- 사용자 결과: 지원 baseline과 현장 ODB 버전에서 올바른 바이너리 조합을 공급한다.
- 선행: 없음
- 기존 이슈: [#335](https://github.com/NumeRealWorks/DashOpti_GUI/issues/335)

**변경 범위**

- 현재 외부 snapshot에서 해결된 MKL pin 주석·preprocessor 메타 등록은 제외하고, 과거 mesh-ops 2026-09-07.0 tree/baseline 처리 정책만 재확인한다.
- 현장 지원 Abaqus 버전과 provider SDK/port options를 맞춰 새 아티팩트를 검증한다
- GUI baseline/시험 fixture를 공급된 버전으로 갱신한다

**완료 조건**

- 지원 ODB fixture가 skip 아닌 실제 reader 시험을 통과한다
- 옛 깨진 baseline 처리 정책을 문서화하고 버전 이력을 임의 덮어쓰지 않는다
- 이미 등록된 preprocessor 메타 항목을 중복 작업으로 세지 않는다

**검증 방법**

- 공급 repository CI와 GUI 실제 ODB read smoke
- versions tree/baseline 대조

**근거**

- `sources/external/`
- `vcpkg.json: preprocessor[test]`
- `sources/issues/335.md: 최신 댓글`

**범위·결정 메모**

여러 저장소에 걸친 공급/소비 묶음이라 2 PR로 나뉠 수 있다. 외부 SDK 설치·지원 버전은 본 조사에서 실증하지 못했다. 현재 snapshot에서 meta 등록과 과거 MKL pin 지시는 해소됐고 preprocessor 포트의 2020 기본/2024 opt-in 설명은 남아 있다.

## DEV-06

**네이밍 정렬 범위를 측정하고 합의된 범위부터 정렬한다**

- 모듈: 개발 규칙
- 판정: 보류 · 제안 우선순위 P3 · 측면 태그 E, F
- 사용자 결과: 호출자 변경이 끝없이 번지지 않는 단위로 naming debt를 줄인다.
- 선행: 없음
- 기존 이슈: [#386](https://github.com/NumeRealWorks/DashOpti_GUI/issues/386)

**변경 범위**

- Ninja compile_commands 기반 진단을 측정용으로 수집한다
- 진행 PR과 겹치지 않는 한 모듈/공개 API 묶음을 정해 호출자를 함께 개명한다
- 정렬 전 naming gate 재도입은 하지 않는다

**완료 조건**

- 선택 범위의 naming 위반이 0이고 호출/Qt metaobject 연결이 정상이다
- 다음 적용 범위와 전체 잔여가 측정 결과로 남는다

**검증 방법**

- clang-tidy 입력 TU 수·진단 수 검증
- 개명 범위 build/test 및 signal 연결 확인

**근거**

- `.clang-tidy`
- `docs/coding-convention.md`
- `sources/issues/386.md`

**범위·결정 메모**

전수 정렬 속도·범위를 먼저 결정해야 한다. 완료 전 gate 활성화는 기존 보류 결정을 위반한다. 이 카드는 전체 리네이밍을 1PR로 요구하지 않는다.

## DEV-07

**실행 파일 버전과 만료 설정을 배포 식별자로 관리한다**

- 모듈: 릴리즈 설정
- 판정: 결정 필요 · 제안 우선순위 P3 · 측면 태그 G
- 사용자 결과: 출고본 버전을 확인하고 승인된 만료 연장을 재빌드 없이 반영할 수 있다.
- 선행: 없음
- 기존 이슈: [#484](https://github.com/NumeRealWorks/DashOpti_GUI/issues/484)

**변경 범위**

- DASH_VERSION과 Windows exe VERSIONINFO를 같은 빌드 정보로 만든다
- 만료값의 런타임 입력·누락/손상/우선순위 정책을 정하고 현재 compile-time 기본값과 호환한다
- 고객별 build target과 Dev bypass를 구분해 검증한다

**완료 조건**

- 파일 속성/앱 정보/로그의 버전이 일치한다
- 잘못된 만료 설정을 임의 무제한 사용으로 해석하지 않는다
- 동일 실행 파일에서 허용된 연장 설정을 반영한다

**검증 방법**

- 날짜 경계·설정 누락/손상 테스트
- 각 build target package 정보 확인

**근거**

- `CMakeLists.txt:106 DASH_VERSION, :107 DASH_LICENSE_EXPIRY_DATE`
- `main.cpp:50 log header`

**범위·결정 메모**

설정 전달/수정 권한·검증 정책은 제품 결정 필요. 현재 날짜를 보고 사용자 라이선스 상태를 추정하지 않는다.

## IO-07

**모델의 프로젝트 경로와 참조 조회를 전달된 계면으로 바꾼다**

- 모듈: Geometry / Condition 모델 경계
- 판정: 선행 작업 후 · 제안 우선순위 P2 · 측면 태그 A, E
- 사용자 결과: 모델이 전역 현재 프로젝트 대신 자기 Set에 속한 IO/참조를 사용한다.
- 선행: PRJ-09
- 기존 이슈: [#247](https://github.com/NumeRealWorks/DashOpti_GUI/issues/247), [#432](https://github.com/NumeRealWorks/DashOpti_GUI/issues/432), [#508](https://github.com/NumeRealWorks/DashOpti_GUI/issues/508)

**변경 범위**

- DashGeometryParameter·DashGeometryParameterCAD·DashConditionParameterization의 ProjectManager/PrjMgr 접근을 PRJ-09 계면 또는 기존 함수 인자로 치환한다.
- 모델 생성·프로젝트 교체 시 의존을 갱신하고 PM/위젯의 직접 전역 경유 호출도 같은 경계로 이동한다.
- 항상 유효한 접근과 실제 실패 가능한 접근을 구분해 중복 null 가드를 제거한다.

**완료 조건**

- 대상 모델의 프로젝트 경로·참조 획득에서 전역 ProjectManager 접근이 남지 않는다.
- 새 프로젝트를 열어도 이전 모델/요청이 새 root에 쓰지 않는다.
- 알고리즘·파일 형식·GUI 정책은 바뀌지 않는다.

**검증 방법**

- 설정 왕복·참조파일 교체·프로젝트 두 개의 경로 격리
- 변경 경로 rg 잔여 확인과 compile/test

**근거**

- `model/DashGeometryParameter.cpp`
- `model/DashGeometryParameterCAD.cpp`
- `model/DashConditionParameterization.cpp`
- `research/root_evidence_project_dependency.txt`

**범위·결정 메모**

저장 파일 원자화(IO-02~04)와 다른 책임이다. 변경 표면이 겹치면 한 PR로 합칠 수 있고 적용 클래스별 독립 증분도 허용한다.

## IO-08

**모델의 프로젝트 경로와 참조 조회를 전달된 계면으로 바꾼다**

- 모듈: DOE / Analysis Launcher 모델 경계
- 판정: 선행 작업 후 · 제안 우선순위 P2 · 측면 태그 A, E
- 사용자 결과: 모델이 전역 현재 프로젝트 대신 자기 Set에 속한 IO/참조를 사용한다.
- 선행: PRJ-09
- 기존 이슈: [#247](https://github.com/NumeRealWorks/DashOpti_GUI/issues/247), [#432](https://github.com/NumeRealWorks/DashOpti_GUI/issues/432), [#508](https://github.com/NumeRealWorks/DashOpti_GUI/issues/508)

**변경 범위**

- DashDoeSampler·DashAnalysisLauncher·DashAnalysisLaunchExecutor·DashJobRunner 및 solver TU의 ProjectManager/PrjMgr 접근을 PRJ-09 계면 또는 기존 함수 인자로 치환한다.
- 모델 생성·프로젝트 교체 시 의존을 갱신하고 PM/위젯의 직접 전역 경유 호출도 같은 경계로 이동한다.
- 항상 유효한 접근과 실제 실패 가능한 접근을 구분해 중복 null 가드를 제거한다.

**완료 조건**

- 대상 모델의 프로젝트 경로·참조 획득에서 전역 ProjectManager 접근이 남지 않는다.
- 새 프로젝트를 열어도 이전 모델/요청이 새 root에 쓰지 않는다.
- 알고리즘·파일 형식·GUI 정책은 바뀌지 않는다.

**검증 방법**

- DOE 입력 생성·solver 실행경로·결과읽기를 두 프로젝트 fixture로 검증
- 변경 경로 rg 잔여 확인과 compile/test

**근거**

- `model/DashDoeSampler.cpp`
- `model/DashAnalysisLauncher.cpp`
- `model/DashAnalysisLaunchExecutor.cpp`
- `model/DashJobRunner.cpp`
- `research/root_evidence_project_dependency.txt`

**범위·결정 메모**

저장 파일 원자화(IO-02~04)와 다른 책임이다. 변경 표면이 겹치면 한 PR로 합칠 수 있고 적용 클래스별 독립 증분도 허용한다.

## IO-09

**모델의 프로젝트 경로와 참조 조회를 전달된 계면으로 바꾼다**

- 모듈: Builder / Runner / Optimizer 모델 경계
- 판정: 선행 작업 후 · 제안 우선순위 P2 · 측면 태그 A, E
- 사용자 결과: 모델이 전역 현재 프로젝트 대신 자기 Set에 속한 IO/참조를 사용한다.
- 선행: PRJ-09
- 기존 이슈: [#247](https://github.com/NumeRealWorks/DashOpti_GUI/issues/247), [#432](https://github.com/NumeRealWorks/DashOpti_GUI/issues/432), [#508](https://github.com/NumeRealWorks/DashOpti_GUI/issues/508)

**변경 범위**

- DashModelBuilder·DashModelBuilderMCU·DashModelRunner·DashOptimizer의 ProjectManager/PrjMgr 접근을 PRJ-09 계면 또는 기존 함수 인자로 치환한다.
- 모델 생성·프로젝트 교체 시 의존을 갱신하고 PM/위젯의 직접 전역 경유 호출도 같은 경계로 이동한다.
- 항상 유효한 접근과 실제 실패 가능한 접근을 구분해 중복 null 가드를 제거한다.

**완료 조건**

- 대상 모델의 프로젝트 경로·참조 획득에서 전역 ProjectManager 접근이 남지 않는다.
- 새 프로젝트를 열어도 이전 모델/요청이 새 root에 쓰지 않는다.
- 알고리즘·파일 형식·GUI 정책은 바뀌지 않는다.

**검증 방법**

- 학습·예측·최적화 설정/산출물 경로 격리 및 해당 module 회귀
- 변경 경로 rg 잔여 확인과 compile/test

**근거**

- `model/DashModelBuilder.cpp`
- `model/DashModelBuilderMCU.cpp`
- `model/DashModelRunner.cpp`
- `model/DashOptimizer.cpp`
- `research/root_evidence_project_dependency.txt`

**범위·결정 메모**

저장 파일 원자화(IO-02~04)와 다른 책임이다. 변경 표면이 겹치면 한 PR로 합칠 수 있고 적용 클래스별 독립 증분도 허용한다.

## IO-10

**철회: 학습 모델 생산·소비 이력 대장**

- 모듈: Model Builder / 산출물 대장
- 판정: 철회 기록(실행 제외) · 제안 우선순위 P2 · 측면 태그 A, C
- 사용자 결과: 2026-10-08 #471 취소 결정에 따라 별도 대장 구현과 과거 소비 이력 보존을 요구하지 않는다.
- 선행: 없음
- 기존 이슈: [#471](https://github.com/NumeRealWorks/DashOpti_GUI/issues/471)

**변경 범위**

- 이 ID는 이전 목록과의 추적을 위해 철회 기록으로만 보존한다. 현재 실행 작업이 아니다.

**완료 조건**

- 별도 생산·소비 대장, 새로운 전역 산출물 ID 체계, 전체 이력 보존을 완료 조건에서 제거한다.

**검증 방법**

- 활성 카드·이슈 대응·의존 순서에서 이 철회 카드를 구현 작업으로 참조하지 않는지 검사한다.

**근거**

- `Issue-Revision-History.md: 2026-10-08 개정 반영 및 현재 방향`

**범위·결정 메모**

출처 추적 상위 #470은 유지한다. 현재 Set·산출물 기록은 PRJ-03(#368)→PRJ-04(#685), 버전·최신성은 PRJ-11(#650)에서 다룬다. 프로젝트는 원본 기록을 조회·집계하며 중복 원장을 만들지 않는다.

## IO-11

**철회: 파이프라인 생산·소비 이력 대장**

- 모듈: DOE / Runner / Optimizer / Analyzer 산출물 대장
- 판정: 철회 기록(실행 제외) · 제안 우선순위 P2 · 측면 태그 A, C
- 사용자 결과: 2026-10-08 #471 취소 결정에 따라 별도 대장 구현과 과거 소비 이력 보존을 요구하지 않는다.
- 선행: 없음
- 기존 이슈: [#471](https://github.com/NumeRealWorks/DashOpti_GUI/issues/471)

**변경 범위**

- 이 ID는 이전 목록과의 추적을 위해 철회 기록으로만 보존한다. 현재 실행 작업이 아니다.

**완료 조건**

- 별도 생산·소비 대장, 새로운 전역 산출물 ID 체계, 전체 이력 보존을 완료 조건에서 제거한다.

**검증 방법**

- 활성 카드·이슈 대응·의존 순서에서 이 철회 카드를 구현 작업으로 참조하지 않는지 검사한다.

**근거**

- `Issue-Revision-History.md: 2026-10-08 개정 반영 및 현재 방향`

**범위·결정 메모**

출처 추적 상위 #470은 유지한다. 현재 Set·산출물 기록은 PRJ-03(#368)→PRJ-04(#685), 버전·최신성은 PRJ-11(#650)에서 다룬다. 프로젝트는 원본 기록을 조회·집계하며 중복 원장을 만들지 않는다.

## PRJ-11

**산출물 버전 의미와 최신성 판정 책임을 정의하고 생산 Set에 적용한다**

- 모듈: 산출물 버전 / 최신성
- 판정: 결정 필요 · 제안 우선순위 P2 · 측면 태그 A, C
- 사용자 결과: 같은 Set에서 재생성된 입력 버전을 소비 Set이 구분하고 최신성·비교 불가 이유를 설명한다.
- 선행: 없음
- 기존 이슈: [#650](https://github.com/NumeRealWorks/DashOpti_GUI/issues/650)

**변경 범위**

- setId는 Set 식별, 항목 키는 결과 식별, 버전은 재생성 전후 구분으로 분리한다. 버전 의미·비교 불가 상태·판정 규칙을 먼저 정의한다.
- 생산 Set이 산출물 버전을 기록하고 소비 Set이 실제 사용한 입력 버전으로 최신성을 판정한다. 프로젝트는 판정을 호출·집계하고 VM은 표시·동작 전달을 맡는다.
- 첫 생산 경계에 버전 기록을 적용하고 DOE-03·BLD-01·RUN-05·OPT-01·ANA-03의 판정/표시 계약을 제공한다.

**완료 조건**

- 동일 setId의 산출물을 재생성하면 실제 소비한 버전과 현재 버전을 비교할 수 있다. 비교할 수 없는 경우 정의된 별도 상태를 사용한다.
- 실패·취소·미완료 쓰기에서 유효 버전의 갱신 시점을 명확히 하고 검증한다.
- 출처 참조 변경·검증을 버전 판정으로 대신하지 않으며 프로젝트나 VM에 소비 Set의 판정 책임을 옮기지 않는다.

**검증 방법**

- 동일 Set 재생성·실패·취소·비교 불가 입력 및 버전 왕복 fixture
- 소비 Set 판정→프로젝트 호출·집계→VM 표시의 책임 및 결과 일치 확인

**근거**

- `Issue-Revision-History.md: 2026-10-08 개정 반영 및 현재 방향`
- `model/DashProject.cpp: refreshUpstreamStaleness`

**범위·결정 메모**

버전 의미·비교 불가 상태·판정 규칙은 #650의 미결 설계다. 출처(#368→#685)와 별도 진행하며 RES-12 포맷 전환이나 철회된 대장을 선행으로 두지 않는다. 생산·소비 Set 및 프로젝트 조회 API의 접점은 팀 논의 사항이다.
