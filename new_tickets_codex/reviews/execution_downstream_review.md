# downstream 작업 독립 재검토

기준: local dev b08a91b 및 현재 modules/downstream.json 28개. 코드 읽기·PR530 diff/설명 대조만 수행했고 실행·구현 변경 없음.

중요 수정 권고 3건(모두 medium). 신규 발견 카드의 핵심 결함은 실제 코드에 있으며 기능을 부풀렸다고 판정하지 않았다.

## EXD-01 · BLD-01, ANA-03

상류 버전 경고에 RES-12의 Set 단위 XML 포맷 전체 이행을 하드 선행으로 두어, 포맷 선택/외부 학습 reader 합의가 끝날 때까지 독립적인 stale 표시도 착수 불가가 된다. 현재 응답별 XML에도 metadata/generation을 기록할 수 있어 이 의존은 코드나 기존 요구에서 필수로 도출되지 않는다.

근거:

- modules/downstream.json:BLD-01/ANA-03 dependencies=[PRJ-03,RES-12]
- modules/execution.json:RES-12는 Set 단위 writer/parser/외부 Builder reader/다중 part/구형식 호환을 함께 다루는 needs_decision 작업
- sources/pr-530.json:T21 writeModelInfoToXml의 공통 metadata 기록 위치가 현재 응답별 XML에도 존재
- model/DashProject.cpp:1657/refreshUpstreamStaleness는 metadata 기반 검사 확산 위치

권고: 포맷에 독립적인 artifact id/generation 계약(PRJ-03 및 새 대장 적용 작업)에 의존하도록 바꾸고, RES-12는 포맷 이행 때 동일 필드를 보존해야 하는 통합 접점으로 둔다. 실제로 Set XML부터 구현하기로 한 순서 선택이면 기술적 필수 의존이 아니라 권장 순서로 명시한다.

## EXD-02 · ANA-07

입력 부족 시 Plot 실패를 사용자에게 알리는 목표는 타당하지만 수동 Plot과 자동 debounce 재플롯을 구분하지 않았다. onPlotButtonClicked가 자동 재플롯에서도 호출되므로 완료 조건을 그대로 적용하면 컨트롤 편집 중 잠깐 불완전한 입력마다 오류 통지가 생긴다. 반대로 실제 build()가 null인 두 경로는 여전히 무음인데 카드 범위에 명시되지 않았다.

근거:

- view/DashResultsAnalyzerWidget.cpp:3950/debouncedReplot → onPlotButtonClicked; 주석은 불완전 입력 시 요청을 내지 않는 계약
- view/DashResultsAnalyzerWidget.cpp:1997 processed false/command empty return
- view/DashResultsAnalyzerWidget.cpp:3558,3571 DashPlotRequestHandler::build null 시 return
- view/DashResultsAnalyzerWidget.cpp:3590 jobId null 주석: reactive 변경마다 모달을 내지 않는 의도적 정책

권고: 사용자가 누른 Plot의 실패는 명시적으로 안내하되 자동 재플롯의 일시적 입력 부족/busy는 비모달 필드 상태·로그 등으로 처리한다는 구분을 추가한다. 요청 생성 이후 build null·지원하지 않는 command도 완료 조건에 넣고 중복 통지를 방지한다.

## EXD-03 · OPT-02, RUN-07, CAD-001

Optimizer/Runner 카드가 NX CAD 요청 ID를 왕복시키는 서비스 계약을 각각 ready 범위에 포함하고, 같은 서비스 계약은 CAD-001에서 deferred 작업으로 따로 남아 있다. 결과적으로 공유 NxCad API 변경의 소유자와 완료 범위가 중복되고, 모듈 카드가 그 계약을 기다리는지 자체 구현하는지 불명확하다.

근거:

- modules/downstream.json:OPT-02 scope 2 모핑·NX CAD 요청 id/Set generation 왕복
- modules/downstream.json:RUN-07 scope 1·3 CAD 완료/실패를 해당 요청으로 회수
- modules/geometry.json:CAD-001 request ID/출처/경로·load/update 성공/실패 왕복, deferred
- controller/DashSolverNxCad.h:27 enqueue 계면, :31 setBatchMode, :36 결과 signals에는 새 요청 식별 계약 없음

권고: 모핑의 모듈별 귀속 수정은 ready로 유지한다. 공유 NxCad request/result 계약은 CAD-001 한 곳이 소유하고 OPT-02/RUN-07은 그 소비 부분임을 명시한다. 작은 현행 방어로 CAD-001 없이 처리할 범위가 있다면 그 범위와 정식 request ID 이행을 분리해서 의존을 표현한다.

## 새 조사 카드별 확인 결과

| 카드 | 코드 판정 |
|---|---|
| BLD-04 | deleteTrainedModel은 파일·model_info.errors만 처리하고 config의 Done 항목은 남긴다. 학습 시작이 기존 Done을 보존하므로 재등장 시나리오가 성립한다. 단일 원자적 삭제를 요구하지 않아 타당하다. |
| RUN-10 | params.keys() 순회 중 첫 Condition 소스가 sourceType을 설정하고 break한다. Geometry가 뒤에 있어도 ND가 Condition-only로 해석된다. PR530의 stampedDeckPath만으로 종류 판정이 고쳐지지 않는다는 설명과 맞는다. |
| OPT-05 | saveSettings의 생산 호출은 runOptimization 1곳이며 DV fixed/value는 Run에서 수집한다. UI만 바꾸는 피팅 값도 확인된다. IO-04 저장 엔진과 도메인 편집 동기화 범위가 구분된다. |
| OPT-06 | UI는 r(i+1), 직렬화는 model.symbol, 복원은 저장 symbol이어서 순서 변경 시 불일치가 가능하다. 로컬 응답/DV 매핑 보강 목적이 타당하며 전역 ID 기능을 강제하지 않았다. |
| ANA-06 | 함수 static recentCalls가 widget/project를 키에 넣지 않는다. 호스트 Set 미일치시 첫 항목 선택 및 Set1 fallback도 실제 존재한다. 명시 비교 선택을 보존하여 불필요한 제품 제한을 추가하지 않았다. |
| ANA-07 | Plot/CSV/JSON의 무음 return·쓰기 결과 무시가 있다. 미지원 export 구현 자체를 요구하지 않는다. 자동 재플롯 안내 정책은 EXD-02 보완 필요. |
| ANA-08 | 모든 SpinBox를 style/data handler 양쪽에 연결한다. 직접 setter 없는 항목은 재생성을 유지한다고 명시하여 일괄 연결 제거 회귀를 피했다. |

## 그 밖의 확인

- RUN-01/02: file-empty 필터와 ND·1D 연속 제출→단일 m_currentJob busy 거절이 코드에 있다. 순차 처리로 현 다중 선택 UI를 완결하는 요구이며 병렬 실행 신기능이 아니다.
- RUN-03/09: 채번 초기화/표 재조회와 valid-zero midpoint·max-0.0001 문제가 현재 코드에 있다.
- RUN-04: nodeSetSourcePath를 검사하고도 reference Document로 lookup하는 잔여를 함께 다룬 점은 타당하다. 별도 소스 일치 검증 정책을 임의 도입하지 않았다.
- BLD-03/OPT-04: 실제 QLineEdit 및 parse 실패→0 경로가 있고 숫자 string 필드/알고리즘별 범위를 구분했다.
- ANA-01은 MCU SHAP 명시 미지원과 옛 요구의 충돌을 needs_decision으로 둬 타당하다.
- ANA-02의 동일 파일명 map과 currentText 복원은 다른 Set의 XML을 합치는 경로다. 경로 ID 전환은 실제 식별 결함 수정이다.
- ANA-04: reduceStd가 살아 있는 extractAllReducedValues에서 호출되는 점을 확인했다. 무작정 모두 삭제하지 않는 카드가 타당하다.
- 삭제된 파일을 현재 코드 근거로 쓰거나 PR530 조합 핀을 독립 신구현으로 중복 세는 추가 사례는 발견하지 못했다.
