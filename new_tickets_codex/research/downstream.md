# Downstream 조사·판정 기록

## 기준과 방법

- 담당: Model Builder(Sim/MCU), Model Runner(Sim/MCU), Optimizer, Results Analyzer.
- 기준 local dev `b08a91b39bbdb7c3b75796ff2cd7f663d53258ef`, 2026-10-05 조사.
- 읽은 자료: `sources/issues/`의 담당 이슈 본문·최신 댓글, `sources/wiki/minhopark/Cross-Module-Defect-Index.md` 및 발행 계획/manifest 결정 문서, `sources/pr-530.{json,diff}`, `sources/pr-652.json`, 현 구현과 테스트 소스.
- 작업 방식: UI 입력/로드 → 모델 입력 변환 → 저장 → 외부 job/daemon → 완료/preview → Set 재진입/프로젝트 전환 순으로 호출을 따라갔다. 이슈의 줄 번호는 현 코드에 적용하지 않고 심벌과 분기를 다시 읽었다.
- 산출물: `modules/downstream.json`/`.md` 28개 카드, `research/downstream_dispositions.json` 40개 기존 이슈 판정.
- 앱/외부 도구 실행·테스트·빌드 **미수행**. 본 보고의 코드 확정은 정적 제어 흐름/호출·쓰기/읽기 근거이며 런타임 재현 완료를 뜻하지 않는다. 각 카드 validation은 향후 수행할 확인이다.

## 현재 워크플로 지도와 책임 경계

| 모듈 | 확인한 사용자 흐름 | 판정/작업 |
|---|---|---|
| Builder Sim | Launcher dataset 선택 → XML model_info/labels 읽기 → input/output/transform 설정 → 학습 모델 설정 → ProcessJob → test result → 삭제·재진입 | 조합 스탬프는 PR530 진행 중; BLD-01 상류 generation, BLD-02 학습 종결, BLD-03 수치 검증, BLD-04 삭제 정합 |
| Builder MCU | CSV 다중 입력 → 헤더 검증 → 라벨/모델 설정 → 공용 MCU daemon 학습 → Stop 재기동 → test result | 기존 Dataset array 읽기/virtual Stop/daemon-ready 복구는 존재. browse 행은 UI-06, 모델 수명 PRJ-01. BLD-02/03은 MCU 소비자 포함 |
| Runner Sim | Builder 폴더 선택 → 응답/모델·DV → Morphing/CAD/Condition/DV-only 생성 → 케이스 선택 → 1D/ND 예측 → CSV/VTU preview → 삭제·재진입 | RUN-01~10으로 무파일 1D·혼합 jobs·케이스·NodeSet·upstream·load·요청 수명·FE validation·범위·source 해석 |
| Runner MCU | 다중 Builder 모델 병합 → CSV 입력 행/대표 행 선택 → wrapper→MCU testModel1D → preview·sensitivity | QPointer/daemon ready는 있음. UI-06 browse 행, RUN-05 upstream provenance, ANA-01 MCU SHAP 정책 |
| Optimizer | Builder 선택 → 응답/DV/목적·제약/방법 → Run → optimum/neighbor/trajectory/MPP → Morphing/CAD preview → 결과 분석 | OPT-01~06 upstream·preview request·실행 종결·수치·설정 왕복·수식 심볼. 비파괴 렌더는 VIS-001 |
| Analyzer | host Set 주입 → target/secondary/model/dataset 선택 → metadata → plot spec 또는 sensitivity daemon → reactive style/data → export | ANA-01~08 지원 정책·dataset 선택·버전 경고·legacy parser·조건부 컨테이너·초기화·오류/내보내기·스타일 갱신 |
| 공통 경계 | project open/close/Set swap, persistence, async lane, result format | PRJ-01/03/09, IO-04, ASY-02/03, AST-003, RES-12가 소유. 본 담당에서는 동일 기반을 별도 구현 카드로 복제하지 않음 |

## 기존 이슈를 그대로 쓰면 틀리는 중요한 차이

### #368은 기존 PR530의 통합 작업이다

PR530 OPEN head `0bbcc9c63d544f4e1eeb4daa558fbfde46b24f5f`의 diff/본문을 대조했다. Builder `parseModelInfoStream` 두 키 보존·dataset 핀·model_info 전사, Runner/Optimizer model_info 핀, Optimizer geometryDeck 1건 preview가 구현되어 있다. dev에는 아직 없다. 이 범위를 새 BLD/RUN/OPT 카드로 다시 구현하지 않고 root **PRJ-03**에서 통합·수동 검증을 소유한다.

PR530 본문의 최신 결정은 옛 #368과 다르다. templateDecks 기록은 소비자가 없어 철회됐고, MCU 무스탬프는 정상 예외다. Geometry Set가 삭제돼도 deck 열거는 가능하지만 performMorphing 내부 part/handle 라이브 의존은 잔존한다고 PR 본문이 명시한다. 새 목록에서 라이브 의존의 완전 제거를 합의 완료 요구로 만들지 않는다.

#650의 `모델을 재학습했다`는 generation 변경은 SI-5 조합 id와 다른 개념이다. 동일 조합에서 XML/모델이 새로 생성돼도 조합 id는 바뀌지 않는다. BLD-01/RUN-05/OPT-01/ANA-03은 이 추가 provenance/staleness 소비자를 맡는다. XML Set 단위화는 **RES-12** 생산자/소비자 이행 카드에 묶는다.

### #370의 본문 안에서도 남은 부분과 해결된 부분이 다르다

- **남음:** `onRunAIPredictionClicked:1286`가 파일 빈 케이스를 제외. `updateModelUploadConfig:1235`는 model_info 기본 DV를 다시 쓴다. RUN-01은 값 전달까지 고친다.
- **남음:** Widget `:1341` ND→1D 연속 시작, Model `:191` 단일 m_currentJob guard. 두 번째 설정이 첫 실행 중 재작성되고 1D는 거절될 수 있다. RUN-02.
- **남음:** populateFileTable `:1114`가 DV map을 비우고 VTU를 스캔하지 않는다. 생성 경로 `:1753`은 VTU row를 만든다. RUN-03.
- **남음:** getReferenceFileAndPart가 `params.keys()` 첫 source를 선택한다. Condition이 먼저면 ND를 거절한다. PR530도 stampedDeckPath만 추가하여 sourceType 첫 매치를 해결하지 않는다. RUN-10.
- **해결됨:** Condition 생성은 현재 `const bool generated`를 확인하고 실패면 return한다(`view/DashModelRunnerWidget.cpp:577`). 이를 별도 실패 무시 카드로 넣지 않았다.

### #369의 NodeSet 경로는 현재 reader 계약을 다시 따라야 한다

`updateReferenceFileAndPart:1185`는 `m_datFilePath.clear()`를 계속 실행한다. browse는 메모리에만 기록하고 NodeSet empty source는 `model/DashModelRunner.cpp:2396`에서 실패한다. 이후 extractComponentVtuFromDat는 `nodeSetSourcePath` 파일을 읽는 대신 이미 확보한 `reference` Document를 전달한다. 즉 선택 영속화뿐 아니라 실제 NodeSet lookup의 source도 일치시켜야 한다. 원문의 `다른 파일과 deck의 라벨 일치 검증 강제하지 않음` 결정은 보존한다.

### #457/#281의 모핑 계산은 이미 비동기다

`DashMorphingUtils::performMorphingAndExport`가 `freezeDoeBatch`/`runDoeBatch`를 co_await한다. #586 서비스 값 경계가 dev에 있다. 옛 동기 계산 전체를 다시 워커화하지 않는다. 그러나 stop_token은 기본값 고정이고 view는 위젯 생존만 검사하며 현재 Set identity를 검사하지 않는다. Optimizer `processEvents` 두 곳과 NX 무태그 완료도 남는다. RUN-07/OPT-02는 **요청 수명/취소/결과 귀속**이다.

### #459 MCU SHAP는 지원 정책 충돌이다

현재 `DashResultsAnalyzerWidget::setModelBuilderBasePath:645`는 MCU에서 SHAP가 미지원이라고 명시하고 `removeMethodWidget("SHAP")`를 호출한다. 반면 후반에는 MCU CSV dataset 열거가 남고 factory feature 콜백은 XML-only다. 따라서 콤보만 채우는 수정은 실제 지원 기능을 복구한다고 보장할 수 없다. ANA-01을 `needs_decision`으로 분류했다. 결정은 지금 사용자에게 묻지 않고 문서에 남겼다.

### #405의 옛 위험·삭제 범위를 교정했다

`extractFieldStatistics`는 현 dev에서 null/type 가드가 생겼다. 호출자 0은 **production** 기준이고 TestXmlParser에는 해당 API를 직접 부르는 테스트가 있다. `reduceStd`는 새 `extractAllReducedValues:546`가 사용하므로 삭제하면 정상 `(std)` 경로가 깨진다. ANA-04는 legacy API와 테스트 계약을 정리하고 살아 있는 reduction을 보존한다. #305는 조건부 container cleanup이며 ANA-05 deferred로 유지한다.

### 완료·철회 범위는 되살리지 않는다

- #548: base `stopTraining` virtual, MCU override 존재.
- #549: Runner Sim/MCU 모델 멤버 QPointer 및 주요 버튼 null guard 존재. Builder/Optimizer raw pointer는 #551→PRJ-01.
- #436/#437: shared daemon detach/idle lifecycle, observeDaemonReady 즉시 현재값 전달이 이미 존재.
- #402/#409/#410/#544: XML 경계 검사·metadata/reduction cache·async 실행층이 있음. cache가 있다고 SHAP caller의 path guard까지 끝난 것은 아님.
- Builder `ModelBuilderConfigHelper::parseDataLabelSection`은 Dataset string/array를 읽고 output transformation을 보존한다. 옛 BLD-D8/D12를 그대로 새 작업으로 만들지 않았다.
- #476은 Done이지만 실제 최신 댓글은 `대장·목록 화면은 필요해지면 재발행`이라는 범위 철회다. RUN-03 내부 케이스 record를 위한 별도 목록 UI는 만들지 않는다.
- Analyzer Condition `checked` vs `boolean` 지적은 여전히 코드에 보이나 해당 generic branch의 현재 target 열거는 DOE 전용이다. 살아 있는 경로로 입증하지 못해 사용자 결함 확정 카드로 넣지 않았다.

## 독립 코드 점검으로 확인한 잔여

| 문제 | 정적 근거 | 작업 |
|---|---|---|
| Builder 시작 버튼을 끈 뒤 config 파일 open 실패가 trainingFailed 없이 return | Widget :958 → Model :522 | BLD-02 |
| Builder Delete가 config의 Done 항목을 남기고 다음 Start가 Done을 다시 보존 | Base widget :93 / model :2269 / :482 | BLD-04 |
| Runner 유효한 0 DV를 중간값으로 치환, max를 무조건 0.0001 깎음 | Widget :1098, :1104 | RUN-09 |
| Optimizer parse 실패 숫자를 0으로 전송 | PM buildMethodOptions :75 | OPT-04 |
| Optimizer Run에서만 saveSettings, Fixed/초깃값/방향/피팅 값 일부는 제출 시에만 모델 동기화 | Model :208 / Widget :470, :1030, :2330 | OPT-05 |
| Optimizer 표시 rN은 행 번호지만 JSON은 model.symbol | Widget :866 / Model :420, :878 | OPT-06 |
| SHAP 같은 이름 XML을 fileName 키로 합쳐 하나 누락 | Analyzer :1902 | ANA-02 |
| 초기화 100ms 캐시가 static이고 키에 인스턴스·프로젝트 없음 | Analyzer :458 | ANA-06 |
| host 대상 없으면 첫 폴더/Set1로 자동 폴백 | Analyzer :510, :595, :620 | ANA-06 |
| CSV/JSON export 메뉴는 항상 보이나 DashExportable cast 실패면 무음 return | Analyzer :3766, :3788 | ANA-07 |
| 모든 SpinBox는 style setter와 data replot에 동시에 연결 | Analyzer :3860 이후 | ANA-08 |

이 중 일부는 옛 wiki 색인에도 있으나, 현재 구현에서 다시 입증된 경로만 작업으로 채택했다. 희망적 전면 MVVM 이행이나 dead-code 전수 제거를 신규 목적에 추가하지 않았다.

## 검증 자산과 실행 gate

확인한 기존 테스트 소스: `TestXmlParser`, `TestAnalyzerUtilsCache`, `TestDataLoaderCache`, `TestFileResourceRegistry`, `TestAsyncJob`, `TestDaemonLifecycle`, `TestMorphingService`, `TestMorphingRun`, `TestResultXmlWriter`. 이것은 테스트 존재 확인이며 이번 조사에서 통과 결과를 얻었다는 뜻이 아니다.

- **Windows 앱/외부 실행 gate:** 1D/ND DeepOpt 예측, MCU 학습/Stop/사고사, NX preview 성공/실패·Set 전환, solver FEValidation, 실제 VTU/CSV preview.
- **metadata/저장 gate:** 조합 동일·산출물 generation만 변경, XML/model_info 무스탬프/다른 핀, 프로젝트 이동, 읽기 전용 경로, 재시작 왕복.
- **GUI 수명 gate:** Generate/Preview/metadata load 중 Set 변경·프로젝트 닫기, 두 Analyzer 인스턴스 연속 초기화, 중간 row 삭제.
- **수치 gate:** 0/음수/좁은 구간/경계/NaN·Inf, normalization 부호와 순서, invalid range가 0으로 바뀌지 않음.

## 결정·제약

1. **ANA-01:** MCU SHAP 기능 지원을 복원할지, 현 명시적 미지원 정책을 유지할지 결정 필요.
2. **ANA-05:** 컨테이너 교체는 측정/연계 변경이 있을 때만 착수(deferred).
3. **RUN-09 / BLD-03 / OPT-04:** 경계 포함 여부·알고리즘별 허용 범위는 실제 backend 계약으로 확인한다. 숫자 한 벌의 범위를 임의 공통화하지 않는다.
4. **RUN-02:** 첫 예측 job 실패 시 후속 종류 계속 여부는 실행 계약에 명시. 조용히 버리는 현재 동작은 허용하지 않는다.
5. **RUN-04:** 보드 Deferred였지만 요구 자체는 구체적이다. 재정의한 착수 순위에서 선택할 수 있도록 작업을 보존했다.
6. **ANA-02:** exists/isFile는 ACL/긴 경로 오류 모두를 판별하지 않는다. 고정 실패를 전역 cache해 회복을 막는 해법은 쓰지 않는다.
7. `ready`는 정적 근거와 범위가 구체적이라는 뜻이다. 이미 런타임 검증되어 바로 배포 가능하다는 뜻이 아니다.

## 자체 검토

- 28개 작업 ID 고유, PLAN 필드 모두 있음.
- PR530 전체 구현은 PRJ-03에 귀속, 소비자 후속은 #650 generation만 범위.
- PR652 신규 Direct dialog와 RUN-08 integration 구분.
- #316 overlay와 OPT-02 요청 수명 구분; #458 RW lane과 RUN-06 폴더 메타데이터 구분.
- #514 행 콜백은 UI-06, RUN-03 도메인 케이스 ID는 별개.
- UI 숫자 검증 카드는 기존 SpinBox 범위를 인정하고 실제 빈틈에 한정.
- 파일 원자성/버전은 IO-04; OPT-05 설정 필드 왕복은 별개.
- 성능 숫자와 수동 재현 결과를 만들어 넣지 않았다.
- GitHub mutation, commit, build, 코드 변경 없음. 작성 파일은 담당 4개뿐이다.
