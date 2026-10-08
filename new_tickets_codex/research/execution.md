# DOE·실행·결과 처리 조사

기준: local dev `b08a91b39bbdb7c3b75796ff2cd7f663d53258ef`, 2026-10-05. 코드·이슈 본문/댓글·`sources/open-prs.json`을 대조했다. 코드 수정·빌드·실제 solver 실행은 하지 않았다. `.odb/.rst/.dfr`, Windows SDK/라이선스 환경 실측은 후속 검증 조건이다. 과거 PR의 PASS는 이번 실행의 PASS가 아니다.

## 현재 흐름과 소유권

| 흐름 | 현재 구현 | 남은 일 |
|---|---|---|
| DOE 선택→Init/Resample→저장 | `DashDoeSampler`, `DashDoeConfigManager`, `DashDoeSelection`, `DashDoeTableFile`; tableId 발행·번호 최대 Resample 선택 있음 | 번호별 Add Set, Launcher로 이동한 active 반영, 상류 조합 스탬프 |
| Launcher Set 진입→부품 조회→Start | `DashAnalysisLauncherWidgetLauncher`, Set별 `DashAnalysisLaunchExecutor` | 조회 중 Start 가드·실패 시 pin 보존, 저장 실패 실행 중단 |
| 입력 생성→solver 제출 | `DashJobRunner`/solver별 TU, `DashMorphingDoeExecutor`, `DashDoeBatchChain` | dat 동기 fallback, terminal 누락, Motion 예제 규칙, fe-safe 연계 |
| 상태→취소→재실행→재개 | `Launcher Cases` JSON·`caseStatusUpdated`·`DashDoeCasesWidget` | Motion 대기 큐 취소, 증분 상태 기록, 중단 복구 정책, 기존 결과 보존 |
| Done→Preprocess→시점/응답 선택→Preview/Process | `DashLauncherRuns`가 resultFiles를 읽음; ReaderSession은 작업별 reader; ResultQuery/Batch/Writer/Initializer | 재실행 후 재조회, 카탈로그 시점·성분, Modal/Motion 질의 정합, 일반 경로 워커 |
| KPI→완료 통지 | `DashAnalysisLauncherKPI`, `LGE_SpringRule`, 래퍼 | Side Force의 무효 0 제거, 단일 완료 통지 |
| XML→Builder/Analyzer | 응답별 XML·DashXmlParser | Set 단위 포맷 생산자/소비자 동시 이행, append/포맷 후보 결정 |
| Direct Tool Dialog | dev는 옛 Direct Set; PR652가 Tool dialog/앱 수명 runner 구현 | PR652 병합·GUI 실측, downstream FE validation은 별도 담당 |

## 오래된 이슈와 코드 차이

- #456의 `generateInputCases` 거대 동기 함수는 현 dev에 없다. `DashJobRunner.cpp:607,764`는 `runDoeBatchForSet`을 await하고 `DashDoeBatchChain.cpp:108,126,206,248,328`은 워커/actor 기반 모핑·export를 await한다. 전체를 다시 비동기화하는 카드 대신 동기로 남은 `runTemplateFallback`과 준비·복사 경계만 대상으로 한다.
- #615의 번호 최대 Resample 선택은 `DashDoeTableFile.cpp:25-65`에 이미 있다. 그러나 `collectReferencePoints`와 이전 이력 경로(`DashDoeSampler.cpp:112,453`)는 옛 샘플 active를 읽는 TODO가 남아 있다. Launcher Set별 active가 다를 때 어떤 Set을 기준으로 삼는지는 정책 질문이다.
- #638 `DashAnalysisLauncherConfig.cpp:44`의 쓰기는 이미 QSaveFile이다. 빈 파일 판별과 실패 이유 전파가 잔여다. snapshot 실패에서 `cancelAllRuns`를 호출하지만 `runAccepted`는 void 신호이고 러너가 이어서 `emitEnqueued`·특수 solver 실행으로 들어갈 수 있으므로 실패가 실행 진입을 실제 차단하는 경계도 검증해야 한다.
- #580의 프로젝트 전환/ansysReady/Motion source 조기 반환이 남아 있다. #651은 stli/wbpj 추가 경로, #652는 Direct 0-submit 경로를 고친다고 기술한다. 원인별 잔여를 독립 확인하고 미병합 코드를 완료로 취급하지 않는다.
- #440 정규 Launcher는 `WidgetLauncher.cpp:205`에서 status 신호를 배선한다. 미배선 Direct 경로는 PR652가 흡수한다. 별도 고정 Enqueued 카드 불필요.
- #646 Re-run 전에 `discardResults`가 실제 파일을 지운다(`DashAnalysisLaunchExecutor.cpp:136-168`). 완료 콜백은 Cases만 갱신하고 Preprocess를 갱신하지 않는다(`WidgetLauncher.cpp:223`). Skip 본문에는 이미 `or skip them?` 설명이 있으므로 별도 기능 PR 대신 재실행 UI 검증에 포함한다.
- #433 1~7 분해와 #642의 writer responseLeaf/frequency/compact 공통화는 코드에 있다. 나머지 시점·component·Modal·KPI 결함은 각 구체 카드로 나누고 별도 거대 '클래스 분해' 카드로 중복 계산하지 않는다.
- `LegacyJsonPreprocessor.cpp:374-376,485,496`는 시간 선택자를 버리고 sub-result를 건너뛴다. `DashResultQuery.cpp:138` ModeShape는 최초 성분 키로 찾고, writer `:384`는 Displacement 고정 키를 사용한다. 정적 응답 operator 중복은 실제 파일 재현 미확인으로 강도를 낮춰 기록한다.
- #412의 폐기된 사이드카/축약값 전면 설계는 복원하지 않는다. #643의 최신 요구만 범위로 사용하며 HDF5를 확정하지 않는다. USD도 후보 비교에 포함한다.
- #502의 라디오 전환/한 Set 복수 템플릿 전제는 #601로 사라졌다. 복수 Launcher Set 일괄 실행의 제품 가치·범위를 다시 결정하는 deferred 항목으로 남긴다.

## 관련 미병합 PR

- PR651: #616 특수포맷 정책·fe-safe source Set 선택/복사와 stli/wbpj terminal 보완. 문서상의 55/55는 작성자 보고이고 GUI 확인은 예정이다. AST 담당은 복사/원장/Condition 미생성, AL-09는 Launcher+fe-safe 소비를 소유한다. #648은 이 구현 뒤 실제 solver로 잔여 원인을 판정한다.
- PR652: #604 Direct Tool Dialog, 메모리 상태·runSerial·실행 상호배제·Result Preview. 문서상의 56/56은 작성자 보고이고 GUI 확인은 예정이다. DIR-01에 통합한다. #653은 downstream 카드가 DIR-01을 소비한다.
- PR654: 모핑 Configuration·legacy archive 거부가 #557 입력 호환에 영향을 준다. 해당 분기가 실제로 source 없는 과도기 Set을 모두 차단하는지는 병합 후 재확인한다.
- PR530: 공통 식별 스탬프 작업의 미병합 구현이다. PRJ-03이 pipeline 전체 스탬프 생산·검증 이행을 소유하며 DOE-03은 DOE 경고 UI 적용만 담당한다. 미병합 구현을 검증된 공통 계약으로 가정하지 않는다.

## 조사 제약·결정 질문

1. Resample prior가 여러 Launcher Set의 서로 다른 active를 만날 때 기준 Set/교집합/합집합 중 무엇인가. 최신 #615는 저장 위치만 지시하여 정책을 확정하지 못한다.
2. 앱 재시작 후 남은 Running의 의미: 기존 프로세스에 재연결할 수 있는가, Interrupted로 확정 후 명시적 재시도하는가. 임의 자동 재실행은 확정하지 않는다.
3. #557 source 없는 GP Set을 재저장 유도 실패로 할지 경고로 유지할지. PR654의 legacy 거부와 일치시켜야 한다.
4. Set XML v1: 외부 Builder 학습 도구의 reader 수정 가능 여부·multi-part 포맷·old XML 읽기 지원 기간 확인 필요. RES-12의 결정 게이트이며 앱 내부 parser만 바꾸고 완료할 수 없다.
5. Modal `.rst/.odb`, Abaqus >=2023 fe-safe step, Motion `.dfr`, SideForce fixture의 실제 데이터 검증이 필요하다. 기존 정적 fixture만으로 이 경로들을 검증했다고 볼 수 없다.

## 자체 검토

- 증분 저장은 공통 IO-01/IO-03을 소비하되 이미 QSaveFile인 config를 중복 원자화하지 않는다. AL-05는 status record 분할/단일 소유·행 단위 갱신, AL-06은 재시작 의미를 소유한다.
- 코드 공통화는 구체 결과 질의 수정에 묶었다. 예외는 동작 비교·실제 파일 matrix RES-11이며 #433 미검증 잔여의 완료 근거를 생산한다.
- 일반 처리 워커화는 KPI 전체의 새 워커화를 포함하지 않는다(#454의 명시 제외). KPI 완료 통지/무효값 결함은 별도 카드로 처리한다.
- 결과 파일 교체·설정·status snapshot은 원자성만으로 충분하지 않다. AL-07은 성공한 세대와 실패한 새 실행의 기록까지 함께 보존하는 단위다.
