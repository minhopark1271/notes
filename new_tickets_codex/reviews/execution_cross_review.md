# execution 담당 독립 교차검토

검토 기준: local dev b08a91b, modules/common.json 35개·geometry.json 19개 및 현재 PR530/651/652/654 스냅샷. 애플리케이션 수정·빌드·실제 solver 실행 없음.

5건: high 1, medium 3, low 1. geometry 카드에서 수정 필수로 판정할 추가 결함은 찾지 못했다.

## EXR-01 · high · PRJ-03

완료 조건의 "모든 단계 … 다른 조합은 차단"이 Launcher 기록-only 및 MCU 무스탬프 예외를 지워 새 정책처럼 읽힌다. 현재 모듈명에서는 Analysis Launcher가 실행 탭과 Preprocess를 함께 가지므로 두 입구를 구분하지 않으면 정상 solver 실행이나 MCU 흐름을 차단할 수 있다.

근거:

- sources/issues/368.md:57-62 홉별 표 — Launcher 검증 없음(D21), Builder MCU 미지정 허용
- sources/issues/368.md:not-to-be — MCU 검증/스탬프 제외·deck 단일성 강제 금지
- sources/pr-530.json: MCU requiresParameterizationPin 예외·Runner/Optimizer -MCU 구조 예외; 차단은 Preprocessor/Builder/Runner/Optimizer 최초 연결

권고: PRJ-03 수용기준을 DOE 기록 / Launcher solver 실행 / Preprocess 입력 연결 / Builder 및 Runner·Optimizer로 나눠 쓰고, MCU 예외·같은 조합의 여러 deck 허용·동결 스탬프를 명시한다. PR530 범위는 그대로 유지한다.

## EXR-02 · medium · PRJ-05

산출물 대장 요구를 Launcher 생산→Builder 첫 소비까지만 목록화하고 나머지 생산/소비 적용을 "downstream 확산"으로 미뤘지만 그에 대응하는 작업이 없다. 전체 목록 관점에서 학습 모델 생산·Runner/Optimizer 소비를 대장에 넣는 일이 누락된다.

근거:

- sources/issues/471.md: 어떤 산출물이 어디에 소비됐는지 대장에 기록
- modules/common.json:PRJ-05 scope 2 및 notes
- modules/downstream.json: PRJ-05/471/대장 적용 카드 없음(검토 시점 검색)

권고: PRJ-05를 최소 기반+첫 적용으로 유지하되 Builder 모델 생산→Runner/Optimizer 소비 기록 적용 카드를 추가하거나 기존 BLD/RUN/OPT 카드에 PRJ-05 의존과 완료 조건을 명시한다. 제품 범위에서 첫 구간만 원한다면 요구 처분에 나머지 deferred 정책 결정을 명확히 남긴다.

## EXR-03 · medium · ASY-01

새 preExecution이 GUI에서 동기 실행될 때의 예외 정규화가 카드 범위·완료 조건·검증에서 빠졌다. 이 훅 도입 시 예외가 UI 차단/슬롯 예약을 남기는 것은 #553이 반드시 같이 해결하도록 지정한 실제 경계다.

근거:

- sources/issues/553.md: 반드시 같이 할 것 — preExecution 예외가 GUI 이벤트 루프로 빠져 UI/slot 고착
- controller/async/DashAsyncJobRunner.cpp:31-79 입력 검사→contexts insert→onBlock→start 순서
- modules/common.json:ASY-01 acceptance는 준비중단/busy만 열거

권고: preExecution throw를 표준 실패로 변환하고 slot/UI/finish 회수를 보장한다는 범위·수용 기준을 추가한다. prepare에서 throw하는 테스트를 포함하고 execution/finish 예외 계약과 구분한다.

## EXR-04 · low · UI-06

PR652 이후에도 Direct 입력 표의 중간 행 삭제/Browse 회귀를 요구하지만 새 Dialog는 단일 Input file과 읽기용 Case/Status/Log 표다. 옛 Direct 입력 행 위젯은 PR에서 삭제하므로 그 수정 단위는 소멸한다.

근거:

- sources/pr-652.diff:1229 옛 m_inputCasesTable 삭제
- sources/pr-652.diff:1475 단일 inputBrowseButton·1502 casesTable 추가
- sources/pr-652.diff:2730 onBrowseInput, :2862 Case/Status/Log 행 렌더; per-row Browse 없음
- modules/common.json:UI-06 scope/validation

권고: UI-06의 실제 구현 대상을 MCU Builder/Runner 살아 있는 row callback으로 한정한다. Direct는 PR652 반영 후 그 유형이 제거됐음을 처분으로 남기고, 필요하면 double-click 현재 행 해석을 짧은 통합 점검으로만 유지한다.

## EXR-05 · medium · PRJ-09

첫 구현 묶음의 모듈·함수 집합이 정해지지 않아 어떤 PR이 이 작업을 완료하는지 판정하기 어렵다. "저장·rename·실행 입력 준비 경로"와 "모듈별 생성부"는 거의 전 모듈을 포함하고, 완료 조건의 "치환한 호출 경로"는 하나만 바꿔도 충족할 수 있다.

근거:

- modules/common.json:PRJ-09 scope 2와 acceptance 2
- research/root_evidence_project_dependency.txt: 여러 모델의 전역 ProjectManager/IO 접근 목록
- model/DashAnalysisLaunchExecutor.cpp:270/findAndEmitSourceFiles 및 model/DashAnalysisLauncher.cpp:ioController 등 실행 소유자의 접근도 포함될 수 있음

권고: 유연한 PR 크기는 유지하되 첫 완결 묶음을 예: Project Set rename/restore의 경로 서비스와 그 직접 호출자로 이름 붙여 고정한다. 남은 실행/모델 소비자는 별도 후속 카드 또는 명시한 적용 표로 남겨 전수 요구가 사라지지 않게 한다.

## 확인하여 지적하지 않은 항목

- IO-03은 직접 truncate 설정 저장/오류/버전, AL-05는 빈번한 case record 구조와 writer 소유/행 갱신, AL-02는 empty/malformed·실패 사유/시작 거부로 나뉘어 있어 구현 중 경계 협의는 필요하지만 현재 카드의 목적은 중복이 아니다. AL-05의 journal 형식이 확정되기 전에 IO-03이 별도 상태 저장 스키마를 만들지만 않으면 된다.
- GEO-001은 PR654 미병합 구현, GEO-002/003/004/005는 PR 명시 잔여로 구분되어 있다. 구 VTP 자동 이행·cylinder 복구·per-handle 반경을 되살리지 않았다.
- GEO-006의 setResults processEvents와 finished 수신 등록 사이 재진입은 실제 코드에 있다. QC 계산 워커화와 혼동하지 않았다.
- VIS-001의 전체 actor 제거, AST-001의 기존 파일 선삭제, AST-003의 RW GUI affinity, CAD-003의 bounds 무검증, CON-002의 number 스키마 범위 미반영을 현 코드에서 확인했다.
- AST-002와 AL-09는 같은 PR651의 다른 소유 영역이며 둘 다 in_flight라 완료로 오인하지 않았다. AST-001은 PR651의 실패 안전성 잔여를 별도로 다뤄 타당하다.
- geometry 카드의 source 위치를 대표 경로에서 확인했다. PR diff 줄은 스냅샷 좌표이고 dev 줄로 표시하지 않아 오래된 구현을 현재 사실로 오인할 문제는 찾지 못했다.
- 조건부/실측 필요 카드가 있다는 이유만으로 불필요한 분할·승인 절차를 요구하지 않았다.
