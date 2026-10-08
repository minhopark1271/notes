# 공통 영역 조사

기준: dev `b08a91b39bbdb7c3b75796ff2cd7f663d53258ef`, 2026-10-05. 원격 dev와 일치한다. Windows 앱 실행 없이 코드·기존 테스트·문서·PR diff를 대조했다. 원문 grep 결과는 `root_evidence_*.txt`에 보존했다.

## 프로젝트 흐름

`MainWindow New/Open → ProjectManager → SetProjectPath → clearAllSets → restoreExistingModules → 모듈 setModel` 순서다. `clearAllSets`가 모델을 지우는 반면 모듈 위젯은 앱 수명이며, 호출 전 해제 계약은 Morphing 전용 reset과 Set 삭제 경로에 부분적으로 있다. 따라서 PRJ-01은 새 수명 프레임워크가 아니라 프로젝트 전환 경계의 실제 정리 작업이다. Runner에 이미 들어간 QPointer 보호는 보존한다.

`SaveProject()`는 현재 true만 반환한다. `SaveProjectAs()`는 대상 폴더를 먼저 재귀 삭제하고 복사 성공을 검사하지 않으며 root를 바꾼 뒤 true를 반환한다. UI는 기존 대상 덮어쓰기를 묻지만 동일/하위 원본 경로 안전성과 실패 복구는 없다. 또한 .dproj 설정 영역 복사만으로 프로젝트 바깥의 참조/결과까지 충분한지 검증해야 한다. #394(보드 밖)를 추가 근거로 확보했고 PRJ-06을 데이터 손실 위험 P1로 잡았다. 이번 조사에서는 파괴적 재현을 실행하지 않았다.

`IsProjectOpen()`는 이미 필드와 ioController만 검사한다. #376의 GetProjectPath 오류 로그 문제는 dev에서 해결되어 새 카드가 없다.

Set UUID는 `DashSetIdentity`에 구현되어 있고 config 파일명→id 메모리 맵도 있다. #443을 UUID 도입으로 재발행하면 중복이다. 원장·표시명 분리의 잔여(PRJ-04), rename 실패 원자성(PRJ-02), 조합 스탬프(PRJ-03)를 구분했다. PR530은 pipeline producer/consumer를 이미 한 draft PR로 구현 중이므로 그 전체를 통합 작업 1건으로 잡는다. #650의 상류 산출물 재생성 경고는 모듈별 후속이며 PR530과 같은 작업으로 계산하지 않는다.

## 저장 기반

`persistence/DashSaveSystem`과 registered-object 기반이 이미 존재한다. `writeJsonFile`은 QSaveFile이며 formatVersion/classVersions도 있다. `DashReferenceModelLedger`에는 schemaVersion과 QSaveFile이 있고 GP·CP·Launcher config도 일부 원자화돼 있다. 따라서 ‘QSaveFile 2파일’, ‘버전 키 0’ 같은 옛 수치를 쓰지 않는다.

남은 문제는 `loadDocument`에서 formatVersion을 읽어 전달하지만 지원 여부를 전역적으로 거절하지 않는 점, 도메인 legacy 파일의 개별 읽기/쓰기·누락·오류 계약, Builder/Runner/Optimizer/DOE의 직접 Truncate 쓰기다. IO-01은 이미 있는 기반의 소비 계약, IO-02/03/04는 모듈별 적용이다. typed QObject 모델로 전면 이행을 강제하지 않는다. 도메인 필드 유실의 개별 수정은 각 모듈 카드가 소유하며 동일 수정량을 두 번 세지 않는다.

`docs/persistence.md`는 참조 누락 qFatal와 비원자적 object load를 현재 설계로 명시한다. 이 정책을 조사자가 임의로 뒤집지 않았다. 새 consumer가 손상 입력을 어떻게 선검증하는지는 적용 시 결정해야 한다. #584는 보드 밖 기반 이력으로 별도 스냅샷을 저장했다.

## 실행기·통지

`DashAsyncJobRunner`는 단일 실행·GUI/worker 경계·UI block hook·shutdown drain을 이미 제공한다. #553은 API/hook 구성 개선이지 워커 기반 최초 도입이 아니다. ASY-01을 모듈 비동기화 전체의 필수 선행으로 만들지 않았다.

`DashExtensionProcess`는 ready 및 stop timeout, UTF-8 write, 대기 요청 cancel, 죽음 fan-out을 이미 갖는다. `trySendNext` 이후 `m_waitingFinished`의 명령 응답 기한은 별개라 ASY-03으로 좁혔다. ASY-04는 외부 프로그램 인코딩 실측 후 경계 보정이며 fromLocal8Bit 검색 결과를 전부 버그로 단정하지 않는다. 실제 GUI 실패 미배선은 OPT/BLD/AL 담당 카드다.

TopOpt 도구의 FEM 파싱과 MainWindow/ViewOptions의 layout flush는 모핑·Preprocess 펌핑과 다른 사용자 흐름이므로 ASY-05/UI-03으로 나눴다. 철회된 W10 WorkerJob/직렬 pool 설계를 재도입하지 않는다.

## UI·개발 환경

MainWindow는 수제 frameless 이동/리사이즈와 resizeDocks를 사용하고 geometry/state 저장은 없다. 혼합 DPI 프리즈는 Windows 실측이 필요하므로 UI-01은 재현 관문을 갖는다. 고정된 버튼 아이콘 치수는 문제로 간주하지 않으며 UI-03은 내용 기반 크기와 강제 event flush만 대상으로 한다. 창 구조 전면 교체는 조건부 대안이다.

MCU Builder/Runner Browse lambda는 row를 캡처한다. 옛 ReferenceFileWidget은 현 트리에서 사라졌고 Direct는 PR652가 이동한다. UI-06은 살아 있는 표로 범위를 다시 정했다. 항목 id/산출물 삭제는 downstream 작업이고 셀 위젯 행 조회는 공통 표 작업이다.

GUI 저장소에 `.github` CI가 없고 test-levels 문서와 vcpkg-configuration 주석 모두 GUI CI 미연결을 명시한다. 테스트 자체는 이미 다수 있으므로 ‘테스트 0’ 대신 DEV-01 CI 연결과 각 모듈의 구체 회귀검증을 제안한다.

#386의 naming gate 보류를 유지했다. 전수 위반 정렬 전 새로운 gate를 켜는 일을 계획하지 않는다. #336의 CMake 업스트림 대기는 당시 버전의 진단이므로 현재 blocker로 단정하지 않고 DEV-04 clean Windows 검증으로 분류했다.

## 외부 저장소 읽기 확인

`sources/external`에 Registry의 mesh-ops/preprocessor portfile, mesh-ops versions, meta repos/vcpkg 및 blob SHA를 저장했다. 현재 preprocessor는 meta에 등록되어 있다. mesh-ops의 과거 MKL pin 지시 문구는 최신 portfile에서 사라졌으므로 이를 다시 수정하는 작업은 제외한다. preprocessor portfile은 여전히 Abaqus 2020 기본/2024 opt-in 설명이다. 실제 공급 runner SDK 설치와 package 내용은 확인하지 않았으므로 지원 버전 확정·실제 ODB 시험은 환경 확인 관문으로 남겼다.

## 이번 조사에서 하지 않은 검증

- Windows 앱 빌드/GUI 실행, 실제 solver/라이선스 실행, 대형 결과 파일 성능 실측.
- 외부 provider runner 접근이나 설치 변경.
- 보드 이외 모든 이슈의 전수 읽기. 보드 207개는 전수 대응하고 필수 접점 #577/#584/#394/#407만 추가 확보.
- 모든 소스 라인의 형식적 안전성 증명. 핵심 사용자 흐름·기존 요구·교차 모듈 경계에 집중했다.

따라서 이 목록은 현재 요구와 조사 범위의 전체 작업 초안이며, 미관찰 버그가 없다는 보증이나 모든 조건부 정책의 확정안은 아니다.
