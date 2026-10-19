# DashOpti PR 794 주요 변경 요약

PR #794는 파일 입출력과 결과 계산 때문에 UI가 멈추던 문제를 줄이기 위해, Launcher·Preprocess·Analyzer·Material·Direct Launch의 요청 경로와 작업 실행 위치를 함께 바꾸는 리팩터링이다. 화면과 백엔드를 분리하고 취소·종료·실패 처리까지 정리하는 것이 핵심이다.

기준: 2026년 10월 15일 확인한 커밋 `e9306e7`. 당시 상태는 OPEN, 대상 브랜치는 `dev`이다. [PR #794 원문](https://github.com/NumeRealWorks/DashOpti_GUI/pull/794)

## 핵심 구조 변경

기존에는 화면 코드가 Manager·Project·Set 모델을 직접 호출하면서 무거운 작업도 UI 스레드에서 실행했다. 처리 도중 화면을 갱신하려고 호출한 `processEvents()` 때문에 다른 입력이 끼어드는 재진입 문제도 있었다.

변경 후에는 화면 요청이 아래 경로를 따른다.

`Widget → Presenter → Command → Agent → 작업 스레드`

작업 결과는 Fact라는 값으로 Presenter에 돌아오고, Presenter가 화면에 반영한다. Agent는 작업 상태와 취소를 관리한다. 요청에는 화면·프로젝트 세대·요청 번호를 붙여, Set이나 프로젝트를 바꾼 뒤 도착한 오래된 결과가 현재 화면에 반영되지 않도록 한다.

이 흐름에 Ordo v0.1.2를 도입하고, `DashAppSession`이 구성 요소의 생성·연결·수명을 관리한다. 설정 쓰기는 직렬 큐에서, 결과 처리와 플롯 계산은 executor에서 실행한다. 대상 UI가 backend를 직접 참조하는 패턴으로 돌아가지 않도록 컴파일·링크 검사도 추가한다. [표준 흐름 설명](https://github.com/NumeRealWorks/DashOpti_GUI/blob/e9306e7cd59b0e8f27c4ba5941427d06f4103cf8/docs/dash-ui-standard-flow.md)

## 영역별 주요 변경

| 영역 | 주요 변경 |
| --- | --- |
| Launcher | 설정 저장을 제출 순서대로 실행하는 큐로 옮기고 Start·Stop·Re-run 경로를 통일한다. 이전 결과 보존·복원도 같은 큐를 사용한다. |
| Preprocess | 결과 읽기·처리·KPI 계산을 별도 엔진으로 분리해 작업 스레드에서 실행한다. 동시 실행은 최대 2개이며 나머지는 순서대로 대기한다. 상태바에서 취소할 수 있다. 경로 표기 차이로 샘플이 빠지던 문제도 수정한다. |
| Analyzer | 플롯 계산·목록 조회·내보내기를 비동기로 전환한다. 계산 중에도 창을 사용할 수 있고, 내보내기 실패를 화면에 알린다. |
| Material | 검증·백업·저장·실패 시 복원을 하나의 작업으로 묶는다. 검증 실패 시 파일을 쓰지 않고, 외부 변경을 확인하며, 바뀐 내용이 없으면 저장하지 않는다. |
| Direct Launch | 입력 확인·실행 준비·결과 미리보기를 비동기로 전환한다. Stop 이후 실제 종료까지 실행 예약을 유지해 중복 실행을 막는다. |

## 사용자가 체감하는 동작 변화

- **처리 중 화면 응답과 취소:** Preprocess와 Analyzer의 무거운 작업을 화면 밖에서 실행하며, Preprocess는 상태바 Cancel로 취소한다.

- **Set 삭제와 프로젝트 전환:** 처리 중 Set 삭제·New·Open·닫기를 요청하면 먼저 작업을 취소하고, “Stopping running processing” 안내 후 작업 종료를 확인해 요청한 동작을 수행한다. 안내에서 Cancel을 누르면 해당 삭제·전환·닫기 요청을 취소한다. 닫기는 최대 10초까지 기다린다.

- **Analyzer 목록:** 목록을 비동기로 채운다. 상위 선택을 바꾸면 하위 콤보는 로딩 중 비워진다.

- **Direct Launch Stop:** “Stopping…”을 표시하고 프로세스가 종료될 때까지 Start와 Launcher 실행을 거절한다. 준비 중인 시작은 Stop이나 프로젝트 전환으로 취소한다. 미리보기를 다시 Load하면 이전 Load를 취소한다.

- **Launcher Target KPI:** 처리 중 Target KPI를 선택하면 안내와 함께 거절하고 General 모드로 돌아간다.

따라서 구조 정리와 함께 취소·종료·실패 시의 사용자 동작도 달라지는 PR이다.

## 변경량이 큰 이유

전체 변경은 **466개 파일, 65,895줄 추가, 8,004줄 삭제**이다. 추가 줄 수에는 테스트 데이터와 문서도 포함된다.

| 변경 묶음 | 추가 줄 수 | 의미 |
| --- | ---: | --- |
| tests와 probe | 25,757 | 전체 추가 줄의 약 39%. 단위 테스트, UI 경계 검사, GUI 시나리오와 테스트 데이터 |
| model과 controller | 16,722 | Agent, 비동기 작업 조율, 분리된 엔진과 기존 모델 연결 |
| view | 7,485 | Presenter 추가와 화면 요청·표시 경로 전환 |
| 기타 | 15,931 | 요청·결과 타입, 앱 연결, 로그·크래시 처리, Ordo, 문서·스킬·도구 등 |

Analyzer 테스트 데이터만 76개 파일이다. 단순 파일 이동 외에 각 영역의 연결 코드와 검증 기반이 함께 추가되어 변경량이 커졌다.

별도로 크래시 보고서 `.txt`·`.dmp`, SetFlow·DVFlow 호출 흐름 로그, MSVC 출력 코드 페이지 고정, 개발 규칙과 스킬도 포함한다.

## 검증 결과와 남은 확인 사항

**PR 작성자가 보고한 결과**는 앱 빌드 성공, 테스트 118/118 통과, GUI probe 67/67을 3회 연속 통과이다. 실제 Ansys `.rst`와 Abaqus `.odb`를 사용하는 Load·Process·미리보기·플롯 시나리오를 포함한다. UI 전용 링크 검사, 금지된 backend include를 검출하는 negative control, Presenter 테스트 5개도 추가했다.

**QC에서 남은 항목**은 다음과 같다.

- Motion `.dfr`, modal·buckling 실제 결과의 Load·Process·KPI

- Re-run 시 이전 결과 보존·복원 전체 흐름

- 실제 창에서 GL 플롯 표시. Offscreen probe는 플롯 데이터를 검사한다.

**명시된 한계**도 있다.

- 실행 조율, morphing 대기, 일부 종료·프로젝트 연결부의 UI 스레드 감사 항목은 후속 범위로 남아 있다.

- Material `.dbase` 열 이름이 실제 Fe-safe DB와 달라 갱신이 “no change”로 끝나는 기존 문제가 남아 있다.

- Motion Stop 후 최대 10초 동안 Start가 거절될 수 있다. Abaqus·Ansys·FE-safe는 종료 콜백이 오지 않으면 실행 예약이 앱 종료까지 유지될 수 있다.

- 작성자는 `test_control_endpoint`의 기존 간헐 실패도 기록했다.

이 검증 결과는 PR에 기록된 보고이며, 전체 UI의 무중단 동작이나 모든 실제 솔버 경로의 검증 완료를 의미하지 않는다.

## 관련 자료

- [PR #794 설명과 변경 파일](https://github.com/NumeRealWorks/DashOpti_GUI/pull/794)

- [연결 이슈 #793](https://github.com/NumeRealWorks/DashOpti_GUI/issues/793)

- [Dash UI 표준 흐름](https://github.com/NumeRealWorks/DashOpti_GUI/blob/e9306e7cd59b0e8f27c4ba5941427d06f4103cf8/docs/dash-ui-standard-flow.md)

구현을 찾아볼 때는 PR의 영역별 커밋 안내를 이용하면 된다. 공용 연결 파일이 후반 커밋에 모여 있어, 중간 커밋 각각의 단독 빌드는 보장하지 않는다.
