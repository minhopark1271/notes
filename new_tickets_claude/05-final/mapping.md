# 대응표 (B2)

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> `python3 05-final/build_mapping.py` 생성. 항목 = 03-items `흡수:` 에 원천이 적힌 항목. CLOSE 는 항목 제목이 닫기 사유.

## (a) 열린 이슈 117건 → 항목

| 이슈 | 제목 | 주 모듈 | 항목 | 비고 |
|---|---|---|---|---|
| #239 | Track B(구조 리팩터) 현황 | PRJ | PRJ-29 | CLOSE — Track B 현황 문서 이슈를 닫는다 |
| #246 | [W20] God-object 해체 — DataProcessor·DashManager·DashProjectM | PRJ | PRJ-27 | CLOSE — God-object 해체 부모를 닫는다 |
| #247 | [W21] Presentation Model 개선 단계 | PRJ | PRJ-28 | CLOSE — Presentation Model 개선 단계 부모를 닫는다 |
| #249 | NX CAD 파사드 완료 통지 일반화 — 요청 태그 왕복 + m_batchMode 제거 | CAD | CAD-01 CAD-15 LCH-27 EXE-12 |  |
| #281 | 단건 모핑 워커화 — QC·Optimizer·ModelRunner 진입점 이관 + 값 경계·전용 세션 (구  | MOR | MOR-04 MOR-16 MOR-18 OPT-22 OPT-26 EXE-14 | CLOSE(부모/본체) + 잔여 항목 — 닫기 — 모핑 축 진입점 이관은 끝났고 잔여는 OPT 측 펌핑 2곳뿐 |
| #305 | refactor: analyzer의 Eigen::VectorXf 컨테이너 용도 사용 정리 검토 (std::v | ANA | MOR-20 ANA-16 ANA-17 | CLOSE(부모/본체) + 잔여 항목 — 닫기 — PR #654 가 2번(sampling 치환)을 실행하고 1번(per-handle 반경)을 결정으로 종결했다 |
| #316 | Optimizer Preview 의 전체 actor 일괄 삭제 — 핸들 5종 복구 불가, 비파괴 오버레이로  | OPT | CAD-12 OPT-01 OPT-02 |  |
| #318 | 공유 VTK 씬에 모듈 소유권 도입 — 덮어쓰기 12곳 정리, 인수는 파괴가 아니라 숨김 | REN | CAD-12 OPT-01 REN-05 REN-06 REN-07 REN-08 REN-10 |  |
| #319 | 레이어 체계 밖 actor 의 수명·상태 결함 4건 — FE actor 숨김 방치 · 무조건 카메라 리셋 · | REN | REN-01 REN-02 REN-03 REN-04 |  |
| #320 | Modeling Tree 의 .vtk/.vtu 표시 토글 무동작 — m_vtuVtkActors 가 채워지지  | REN | REN-11 REN-12 |  |
| #322 | refactor: GizmoGroup 의 인덱스 병렬 컨테이너 3개 정리 — checked/백업 상태를 Da | MOR | MOR-09 | CLOSE — 닫기 — PR #655 가 `GizmoGroup` 을 삭제해 정리할 컨테이너가 없어진다 |
| #330 | 최신 MSVC version (18.10.0) 에서, vcpkg 를 통해 build artifact 가 공급 | DEV | DEV-01 DEV-02 DEV-03 |  |
| #331 | libs/ 임시 배치 해소 — DashGizmo 단일 빌드 재배치 · MarchingPlaneBound 상류 | MOR | MOR-06 MOR-07 MOR-08 |  |
| #332 | morphing — mesh-ops 공개 표면으로의 잔여 이관 2건 | MOR | MOR-20 | CLOSE — 닫기 — PR #654 가 2번(sampling 치환)을 실행하고 1번(per-handle 반경)을 결정으로 종결했다 |
| #335 | registry / meta 저장소 정합 4건 — portfile 주석 · git-tree · preproc | DEV | DEV-04 DEV-05 DEV-06 DEV-07 DEV-08 |  |
| #336 | vcpkg 이행 마무리 정리 4건 — external/ 삭제 · globalPos() · CRT 배포 · m | DEV | DEV-10 DEV-11 DEV-12 |  |
| #368 | 출처 기록과 공통 판독 계약 | PER | DOE-16 LCH-33 PRE-32 BLD-20 PER-06 PER-07 |  |
| #369 | NodeSet 선택 저장 — 독립 작업 | RUN | RUN-01 |  |
| #370 | ModelRunner: 1D 모델 Run AI Prediction 이 reference analysis fi | RUN | RUN-05 RUN-06 RUN-07 RUN-14 UIC-16 |  |
| #372 | CI: Level 1 레인 소요 시간 감시 — 건강 한도(임시 5분) 초과 시 알림 | DEV | DEV-14 DEV-15 DEV-16 |  |
| #376 | 프로젝트 열기 시 미열림 상태가 ERROR로 오탐지되는 문제 수정 | PRJ | PRJ-30 | CLOSE — IsProjectOpen ERROR 오탐을 닫는다 |
| #386 | clang-tidy 네이밍 검사: 저장소 소스가 컨벤션에 정렬된 뒤로 보류 | DEV | DEV-17 |  |
| #405 | DashXmlParser: FieldStatistics 계열이 호출자 0건 — 살릴지 지울지 결정 필요 | ANA | ANA-02 |  |
| #411 | DOE 산출 XML 포맷 교체 검토 — HDF5(vtkHDF) 등 스트리밍 가능 포맷 | PRE | PRE-28 PRE-29 PRE-31 BLD-16 PER-03 DEV-25 |  |
| #423 | 설정 초기값(default) 정책 — 소유자 · 진입점 · 대역 로그를 앱 전반에 세운다 (계기: 모핑 반경 | MOR | MOR-11 PER-10 |  |
| #427 | DOE 배치·Generate·프리뷰 실행을 화면 편집 상태에서 격리 | MOR | MOR-19 | CLOSE — 닫기 — 추적 전용 부모, 격리 몫은 끝났다 |
| #430 | 핸들 데이터 전용 타입 DashHandleData 신설 — VTP 읽기 5곳·쓰기 2곳 일원화 | MOR | MOR-15 | CLOSE — 닫기 — PR #655 가 interaction 의 핸들 소유를 해제했다 |
| #431 | 모델 교체·세트 전환 시 위젯 정리 규칙 문서화 | PRJ | PRJ-02 |  |
| #432 | 모델 계층이 프로젝트 관리자를 되부르는 의존 제거 | PRJ | PRJ-08 PRJ-09 |  |
| #433 | 데이터 처리 클래스 분해 | PRE | PRE-01 PRE-02 PRE-03 PRE-04 PRE-07 PRE-20 | CLOSE(부모/본체) + 잔여 항목 — 런처·초기화기의 질의 직렬화와 모달 Name 리터럴 공용화 — PR #656 이 구현 |
| #434 | 전역 관리 객체 해체 | PRJ | PRJ-03 PRJ-04 PRJ-05 PRJ-06 PRJ-07 |  |
| #438 | 배치 계산의 취소·진행 표시·재시작 복구를 완결 | LCH | LCH-22 | CLOSE — 닫기 — 추적 전용 부모 |
| #439 | 배치 취소가 대기 큐까지 비우게 완결 | LCH | LCH-03 |  |
| #440 | 실행 케이스마다 현재 상태가 표에 보이게 | LCH | LCH-23 | CLOSE — 닫기 — PR #652 가 Direct 표의 상태 배선을 해소한다 |
| #441 | 상태 기록과 재시작 복구 | LCH | LCH-08 LCH-09 |  |
| #442 | 실행 이력 목록 관리 | LCH | LCH-24 | CLOSE — 기록 — GitHub 에서 이미 닫힘 · gh-state CLOSED |
| #443 | Set 입력 참조 | PRJ | DOE-16 LCH-33 PRE-32 BLD-20 RUN-34 OPT-26 PER-06 PER-07 |  |
| #444 | Set 기록 분리 — 비용 검증 후 조건부 | LCH | LCH-32 |  |
| #446 | 창·레이아웃 크기 관리를 Qt 표준으로 전환 | UIC | UIC-25 | CLOSE — 을 닫는다 — 추적 부모, 실작업 없음 |
| #447 | 배율 다른 모니터로 이동 시 프리즈·복구 불가 차단 | UIC | CAD-14 ANA-19 ANA-20 OPT-25 UIC-01 UIC-02 |  |
| #448 | 창 위치·크기·도크 배치의 저장·복원 도입 | UIC | PRJ-14 UIC-05 |  |
| #449 | 명령형 크기 지정 제거 — 레이아웃에 크기 결정권 반환 | UIC | ANA-21 UIC-03 UIC-06 UIC-10 UIC-12 UIC-13 UIC-14 UIC-15 UIC-26 |  |
| #450 | 테두리 없는 창과 중첩 메인 윈도우 구조 재검토 | UIC | UIC-08 UIC-09 UIC-11 |  |
| #451 | GUI 스레드 동기 실행과 이벤트 펌핑 제거 | EXE | EXE-01 EXE-04 EXE-05 EXE-14 EXE-18 | CLOSE(부모/본체) + 잔여 항목 — GUI 스레드 동기 실행과 이벤트 펌핑 제거 — 추적 부모를 닫는다 |
| #454 | Data Preprocessor — 동기 실행 워커 이관과 펌핑 16곳 제거 | PRE | PRE-02 PRE-23 PRE-24 EXE-04 |  |
| #455 | 모듈 외 잔여 view 펌핑 10곳 분류·제거 | PRJ | MOR-01 PRJ-26 REN-13 |  |
| #456 | Analysis Launcher 정규 경로(.inp·ANSYS) — [Start] 동기 실행 워커 이관 | LCH | LCH-20 EXE-04 | CLOSE(부모/본체) + 잔여 항목 — 닫기 — 정규 경로 [Start] 는 이미 워커·시그널 구동이다 |
| #457 | Optimizer — 펌핑 2곳 제거와 요청 식별자 왕복 (OPT-D19) | OPT | CAD-01 OPT-22 OPT-26 |  |
| #458 | 해석 모델 적재를 워커로 이관 | EXE | LCH-12 EXE-14 EXE-22 |  |
| #459 | MCU Set 에서 SHAP Feature 콤보가 채워지지 않는 문제 복구 | ANA | ANA-03 |  |
| #460 | 실행 진행 표시·취소·중복 실행 가드의 표준화 | EXE | EXE-19 | CLOSE — 실행 진행 표시·취소·중복 실행 가드의 표준화 — 추적 부모를 닫는다 |
| #461 | 실행 중 재클릭·재진입 차단 | EXE | EXE-09 |  |
| #462 | 진행 표시 표준 1종 정의 | EXE | EXE-07 |  |
| #463 | 모듈별 진행바·취소 버튼 확산 | EXE | MOR-01 CAD-07 LCH-28 PRE-23 BLD-10 RUN-05 RUN-25 ANA-22 OPT-05 OPT-22 EXE-15 | CLOSE(부모/본체) + 잔여 항목 — 모듈별 진행바·취소 버튼 확산 — 모듈 항목으로 분산하고 닫는다 |
| #464 | 기존 진행 표시 결함 정리 — 스피너 비대칭 | CAD | CAD-07 |  |
| #465 | 외부 프로세스 안전핀 일괄 — 무음 실패·타임아웃·인코딩·널 가드 | EXE | EXE-20 | CLOSE — 외부 프로세스 안전핀 일괄 — 추적 부모를 닫는다 |
| #466 | 프로세스 무음 실패의 통지 규칙 수립 | EXE | EXE-10 UIC-16 |  |
| #467 | 데몬 기동·응답 타임아웃 도입 | EXE | EXE-11 |  |
| #468 | 외부 프로세스 호출부 널 가드 일괄 | EXE | EXE-16 | CLOSE — 외부 프로세스 호출부 널 가드 — 해소됨으로 닫는다 |
| #469 | 프로세스 인자·출력 인코딩 UTF-8 통일 | EXE | EXE-17 | CLOSE — 프로세스 인자·출력 인코딩 UTF-8 통일 — 본선 완료로 닫는다 |
| #470 | 출처 추적 상위 목표 유지 | PER | PER-09 |  |
| #471 | 독립 산출물·소비 대장 취소 유지 | PER | PER-11 | CLOSE — 독립 산출물·소비 대장 취소를 유지한다 |
| #473 | 결과 항목 조작 오류 수정 | RUN | RUN-02 |  |
| #474 | 표 행과 항목 연결 | RUN | RUN-12 UIC-23 |  |
| #475 | 예측 결과 덮어쓰기 방지 | RUN | RUN-10 |  |
| #477 | 삭제와 파일 해석 | RUN | RUN-11 RUN-13 |  |
| #478 | JSON 변환 헬퍼 표준화와 왕복 동일성 게이트 | PER | MOR-22 CAD-13 CON-11 DOE-17 PRE-27 BLD-17 RUN-32 OPT-24 PRJ-31 PER-01 PER-02 PER-05 |  |
| #479 | 파일 쓰기 원자성 — 저장 중 크래시에도 파일 보존 | PER | MOR-22 CAD-13 CON-11 DOE-17 PRE-27 BLD-17 RUN-32 OPT-24 PRJ-31 PER-02 |  |
| #480 | 저장 포맷에 버전 키 도입 | PER | MOR-22 CAD-13 CON-11 DOE-17 BLD-17 RUN-32 OPT-24 PRJ-31 PER-03 PER-04 |  |
| #481 | QSettings 스코프 통일과 최근 프로젝트 메뉴 | PRJ | PRJ-14 PRJ-15 |  |
| #482 | 사용자 통지 규칙 수립과 메시지 박스 래퍼 표준화 | UIC | UIC-16 UIC-17 |  |
| #483 | 출고물의 개발 잔재 제거 — 로컬 경로·플레이스홀더 문구 | DEV | OPT-12 DEV-20 |  |
| #484 | 릴리즈 식별·연장 — exe 버전 정보·만료일 런타임화 | DEV | DEV-21 DEV-22 DEV-23 DEV-24 |  |
| #485 | 종료 시 저장 확인 — 변경 추적과 닫기 이벤트 | PRJ | PRJ-10 PRJ-11 |  |
| #486 | 프로젝트 동시 열기 잠금 | PRJ | PRJ-13 |  |
| #487 | 숫자 입력 검증 일괄 — 범위 검증과 툴팁 | UIC | DOE-20 UIC-21 |  |
| #488 | 동작 없는 Undo/Redo 버튼 제거 | PRJ | PRJ-19 |  |
| #489 | 도메인 로직 테스트 커버리지 확장 | DEV | CAD-11 DOE-07 BLD-19 RUN-33 OPT-20 DEV-18 DEV-19 |  |
| #490 | 부분 적용된 다국어 처리 제거 — 영어 고정 | UIC | UIC-18 |  |
| #494 | 레거시 JSON 어댑터가 시간 선택자와 sub-result 를 버린다 — 응답 카탈로그 범위·성분 축 신설 | PRE | PRE-17 PRE-18 PRE-19 |  |
| #499 | morphing: mesh-ops 버전 범프 수용 — 신규 handle 생성기 API 와 고립 handle  | MOR | MOR-05 MOR-06 |  |
| #502 | 실행 1회로 조건 해석파일별 batch run 자동 반복 (T26 루프) | LCH | LCH-21 | CLOSE — 닫기 — 라디오 단일 선택 전제가 사라졌고 범위 밖으로 확정됐다 |
| #508 | 싱글턴 접근자 직후 도달 불가 null 가드 제거 — Instance()·Mgr()·GetProject()· | UIC | UIC-19 UIC-20 |  |
| #512 | Geometry Parameterization(Morphing) — setResults 펌핑 제거와 결정 시 | MOR | MOR-01 |  |
| #513 | Model Runner — 폴더 선택 동기 스캔 워커 이관 | RUN | RUN-25 EXE-04 |  |
| #514 | 표 셀 위젯이 캡처한 행 번호가 삭제 후 어긋난다 — 전수조사 잔여 5건과 행 해석 규칙 통일 (#503 계 | UIC | UIC-22 UIC-23 UIC-24 |  |
| #519 | DashPlotWidgetFactory: 열 수 없는 XML 경로를 콤보 조작마다 재시도한다 | ANA | ANA-01 |  |
| #543 | 비동기 작업 중 UI 차단·진행 표시의 UI/UX 정리 | EXE | EXE-02 EXE-07 EXE-08 |  |
| #551 | 프로젝트 전환 시 나머지 모듈 위젯 7곳도 해제된 모델을 역참조한다 — #549 전수조사 잔여 | PRJ | CON-04 PRJ-01 |  |
| #553 | DashAsyncJobRunner: 콜백 3개를 준비/실행/완료 훅 구조로 재구성한다 | EXE | EXE-03 |  |
| #557 | #500 후속 — DV-Geometry source 가 없는 GP 세트는 Target Component 비교 | MOR | MOR-10 |  |
| #562 | Set Rename 시 산출물 폴더·vtp 사이드카·Launcher Selected Design Variab | PRJ | DOE-18 PRJ-18 |  |
| #563 | Geometry Parameter Non-design(Constraints) 영역이 재진입·Set 전환 시  | MOR | MOR-02 MOR-03 MOR-04 |  |
| #580 | DOE Enqueued 이후 상태 없는 co_return 이 런 추적을 멈춘다 (stall 4곳) | LCH | LCH-02 |  |
| #604 | Tool 메뉴: Direct Launch를 별도 Dialog로 분리한다 | LCH | LCH-19 LCH-25 | CLOSE(부모/본체) + 잔여 항목 — 닫기 — PR #652 머지로 종결, 잔여는 LCH-14·LCH-19 |
| #615 | DOE Sampler: Add Set을 복원하되 Resample만 번호를 붙여 추가한다 | DOE | DOE-02 DOE-03 PRJ-33 |  |
| #616 | 입력 파일 정책: RW 미지원 포맷(.dfsxml/.wbpj/.stli)의 Project Assets·Con | LCH | LCH-26 LCH-29 | CLOSE(부모/본체) + 잔여 항목 — 닫기 — PR #651 머지로 종결, 잔여는 #647·#648 |
| #630 | 필드 출력 질의가 응답을 operator 로만 지정해 같은 operator 의 응답을 구분하지 못한다 | PRE | PRE-06 |  |
| #631 | Side Force KPI 가 Force X/Y operator 를 찾지 못하면 0 을 결과로 쓴다 | PRE | PRE-11 |  |
| #634 | Motion 의 Load Step 이 'States / State N' 으로 넘어가 배치는 state 1 만 | PRE | PRE-05 |  |
| #635 | 결과 XML 작성기가 Motion 컴포넌트의 entity_name 을 질의에 싣지 않아 전체 모델을 읽는다 | PRE | PRE-07 PRE-20 |  |
| #636 | Modal Frequency KPI 가 완료 신호를 직접 내 Success 팝업이 두 번 뜬다 | PRE | PRE-12 PRE-13 |  |
| #637 | Mode Shape 가 변위 결과를 하위 키·이름 순서·고정 키로 찾아 미리보기와 배치가 실패한다 | PRE | PRE-01 PRE-09 PRE-10 |  |
| #638 | Analysis Launcher 설정 저장이 0바이트 파일을 거절하고 실패 사유를 알리지 않는다 | PRE | LCH-34 PRE-14 PRE-15 PRE-16 PER-02 |  |
| #639 | Analysis Launcher: Target Part 로딩 중 Start를 누르면 빈 target이 저장되 | LCH | LCH-01 |  |
| #643 | Analysis Launcher: Preprocess XML을 Set 단위로 쓰고 중복 정보를 없앤다 (HD | PRE | PRE-29 PRE-30 PRE-31 BLD-14 ANA-23 |  |
| #645 | Project Assets: Add File로 덮어쓴 파일이 Condition 화면에 반영되지 않고 복사 실 | PRJ | CON-03 PRJ-20 PRJ-21 | CLOSE(부모/본체) + 잔여 항목 — (CLOSE) Add File 덮어쓰기 뒤 Condition 재읽기를 CON-03 에 넘긴다 |
| #646 | Analysis Launcher: 재실행 뒤 Preprocess 목록 미갱신, Re-run 실패 시 기존 결 | LCH | LCH-15 LCH-16 LCH-17 |  |
| #647 | Ansys Motion: dfsxml 실행이 LGE 압축기 예제에 하드코딩되어 있고 run마다 dfmm·df | LCH | LCH-10 LCH-11 |  |
| #648 | fe-safe: Set이 파일 하나에 묶인 뒤 입력 ODB 위치를 찾지 못한다 | LCH | LCH-18 LCH-30 |  |
| #649 | DOE Sampler·Analysis Launcher 재구성 후속 — Set 정책·입력 포맷·화면 갱신 | DOE | DOE-15 | CLOSE — 를 추적 부모로 닫는다 |
| #650 | 산출물 버전과 최신성 | PRJ | BLD-15 BLD-18 RUN-31 ANA-06 OPT-23 PRJ-22 PRJ-23 |  |
| #653 | Model Runner·Optimizer: FE Validation 버튼으로 Set의 입력 파일을 Direc | RUN | RUN-30 OPT-21 |  |
| #552 | DashAsyncJobContext 취소 불가 — 보드 밖 OPEN (#553 선행) | EXE | EXE-02 | gh-state OPEN(보드 밖) |
| #404 | Analyzer: "(std)" 축약이 표준편차가 아니라 최댓값으로 조용히 떨어진다 — 보드 밖 OPEN ( | ANA | ANA-02 | gh-state OPEN(보드 밖) |
| #394 | SaveProjectAs 가 모든 실패를 무시하고 true 를 반환하는 문제 — 보드 밖 OPEN | PRJ | PRJ-12 PRJ-36 | gh-state OPEN(보드 밖) |
| #577 | fix(view): Volume 핸들 생성기 — cylinder 삭제, Hexahedron 은 mesh-op | MOR | MOR-05 | gh-state OPEN(보드 밖) |

집계: 작업 항목 89 · CLOSE 19 · CLOSE+잔여 9 · 항목 없음 0

## (a-1) 원천 보드 snapshot 이후 확정된 소비 계약

| 이슈 | 항목 | 현재 범위 |
|---|---|---|
| #685 | RUN-34 · OPT-26 (OPT-15 저장 접점) | #443 하위. #368 생산·공통 계약 선행, Builder setId 참조·검증·실행·조회·프리뷰. #681 머지 조건 아님 |

위 (a)의 보드 수·gh-state는 당시 수집 기록이다. #443은 별도 Set 원장 구축을 요구하지 않고 #444·#369를 하위에서 분리한다. #444는 #441 하위, #473은 참조 전환과 독립이며 #470은 유지한다. 추가 개정 계획의 보드 정리·종료 후보는 이 표에서 실행하지 않는다.

## (b) 결함 201건 → 항목 또는 판정

| 결함 | 색인 요약 | 항목 | 판정 · 근거 CID |
|---|---|---|---|
| ANA-D6 | 색 값의 정본이 스타일시트 문자열이고 읽는 방식이 문자열 절단·정규식 2가지 | ANA-10 | 유효(ANA-c14) |
| ANA-D9 | 설정 JSON 의 `DOE Analysis`·`Data Analysis` 블록이 write-only | 항목 없음 | 해소됨(ANA-c17) |
| ANA-D3 | `applyReduction` 분기가 Max/Min/Mean 3종이고 나머지는 `reduceMax` 폴백 | ANA-02 | 유효(ANA-c02) 해소됨(ANA-c11) |
| ANA-D10 | spec 조립 실패·command 미매치·조기 반환이 UI 에 아무 변화를 주지 않음 | ANA-15 | 유효(ANA-c19) |
| ANA-D14 | 타깃 콤보 스캔이 Set 필터 없이 전량을 나열하고 항상 0번을 자동 선택 | ANA-06 | 유효(ANA-c24) |
| ANA-D12 | Save 메뉴 3종이 위젯 종류와 무관하게 뜨고 `dynamic_cast` 실패 시 무반응 | CAD-07 LCH-23 OPT-05 UIC-16 | CID 경유 — 해소됨(ANA-c22) 해소됨(ANA-c39) 해소됨(ANA-c40) 범위밖(EXE-c44) 범위밖(UIC-c56) |
| ANA-D2 | 중복 억제 캐시가 함수-로컬 `static` 이고 키에 인스턴스가 없다 | ANA-05 | 유효(ANA-c10) |
| ANA-D5 | 타깃 3콤보 등 5종이 `objectName` + `findChild` 문자열 계약 (25회) | ANA-08 | 유효(ANA-c13) |
| ANA-D11 | 랭킹 표를 반환 타입 밖의 숨은 자식으로 실어 보내고 `objectName` 으로 꺼낸다 | ANA-12 ANA-13 | 유효(ANA-c20) |
| ANA-D1 | `m_methodWidgets` 가 `QMap` 이라 Method 콤보가 키 알파벳 순 | ANA-04 | 유효(ANA-c09) 유효(ANA-c42) |
| ANA-D8 | `methodKey` 매핑 5줄이 세 파일에 각각 존재 | 항목 없음 | 해소됨(ANA-c16) |
| ANA-D15 | `m_setName` 이 비면 `"Set1"` 로 대체하는 폴백 삼항이 7회 복제 | ANA-07 | 유효(ANA-c25) 유효(PRJ-c55) |
| ANA-D4 | XML 변수 스캔이 매번 문서 전체를 GUI 스레드에서 파싱하고 폴백 경로는 결과가 다르다 | 항목 없음 | 해소됨(ANA-c12) |
| ANA-D13 | 스핀박스가 스타일 setter 와 디바운스 재플롯 양쪽에 연결돼 있다 | ANA-11 | 유효(ANA-c23) |
| ANA-D7 | 타입 핸들 `textStyleGroup` 에 9곳이 대입하고 읽는 코드는 0건 | ANA-09 | 유효(ANA-c15) |
| ANA-U1 | `onTargetDataChanged` 의 모듈 판별 4갈래가 도달 불가 | ANA-14 | 유효(ANA-c26) |
| ANA-U2 | `settings.parallel.save_json_path` 를 읽는 코드가 레포 전체 0건 | ANA-14 | 유효(ANA-c27) |
| ANA-U3 | `DashDoeConfigManager::updateConfigFile` 55줄의 호출처가 0건 | 항목 없음 | 해소됨(ANA-c18) |
| ANA-U5 | 호출부 없는 진입점 4개 (약 106·110·111·16줄) | ANA-12 ANA-14 | 유효(ANA-c21) 유효(ANA-c28) |
| BLD-D1 | Set 갈림 근거가 `UserRole+2` · JSON `variant` · 이름 접미사 3벌 | PRJ-32 | 범위밖(BLD-c01) 유효(PRJ-c63) |
| BLD-D4 | 라벨 키의 쓰기는 sanitize, 읽기는 원문 | BLD-02 | 유효(BLD-c04) |
| BLD-D7 | 저장된 Response 는 sanitize 된 이름, 콤보 표시는 원문 기반 | BLD-03 | 유효(BLD-c05) |
| BLD-D8 | Output `transformation` 은 쓰기만 되고 읽기에서 값이 버려진다 | BLD-02 | 유효(BLD-c06) |
| BLD-D12 | MCU 는 `Data Label.Dataset` 을 배열로 쓰는데 베이스 로더는 `toString()` | BLD-01 | 유효(BLD-c08) |
| BLD-D14 | MCU 의 `stopTraining` 이 `virtual` 이 아니라 베이스 no-op 이 불린다 | BLD-10 | 해소됨(BLD-c21) 해소됨(EXE-c40) |
| BLD-D2 | [Load] 의 위젯↔모델 계약이 `"dir|file"` 구분자 문자열 | BLD-04 | 유효(BLD-c02) |
| BLD-D3 | 차원 판정의 정본이 파싱 결과가 아니라 shape 문자열의 쉼표 개수 | BLD-05 | 유효(BLD-c03) |
| BLD-D5 | 설정값 왕복이 카탈로그 리스트 i번째와 `QFormLayout` i번째 `FieldRole` 의 짝 | BLD-06 | 유효(BLD-c09) 유효(BLD-c40) |
| BLD-D10 | MCU 파일 행의 [...] 람다가 생성 시점 `row` 를 값 캡처 | UIC-23 | 유효(BLD-c18) 유효(BLD-c35) 유효(BLD-c35) 범위밖(RUN-c14) 유효(UIC-c51) |
| BLD-D9 | Sim / MCU 쌍둥이 경로의 계약이 6곳에서 어긋난다 | BLD-01 BLD-11 BLD-12 | 유효(BLD-c11) 유효(BLD-c12) 유효(BLD-c13) 유효(BLD-c14) 유효(BLD-c15) 유효(BLD-c16) 유효(BLD-c17) |
| BLD-D6 | [Delete] 가 `model_info.json` 과 디스크만 지우고 설정 JSON 항목을 남긴다 | BLD-07 | 유효(BLD-c10) |
| BLD-D15 | MCU 위젯이 버튼 잠금을 되돌리지 않고 성공·실패 시그널도 연결하지 않는다 | BLD-10 | 유효(BLD-c22) |
| BLD-D11 | 헤더 검증의 기준 파일 출처가 넷이고 전부 조작 순서에 종속 | BLD-09 | 유효(BLD-c19) |
| BLD-D13 | MCU 가 쓰지 않는 1Hz 상태 폴링 타이머를 켠 채 두고 멈추는 경로도 안 탄다 | BLD-10 | 유효(BLD-c20) 유효(BLD-c37) 범위밖(EXE-c37) |
| BLD-U1 | 죽은 코드가 세 층에 남아 있다 (헬퍼 8개 중 실사용 4개 · `m_datasetFiles` 스캔 38줄 등) | BLD-13 | 유효(BLD-c23) |
| BLD-U3 | `parseDataLabelSection`·`parseConfigurationSection` 의 호출처가 0 | BLD-02 | 유효(BLD-c07) |
| CAD-D12 | 범위값의 정본이 모델이 아니라 셀 위젯의 스핀박스 | CAD-04 | 유효(CAD-c28) |
| CAD-D10 | `meta.default` 에 현재값이 아니라 Lower 열 값이 들어감 | CAD-05 | 유효(CAD-c26) |
| CAD-D11 | `Independent Parameter.Value` 저장은 `upper`, 로드는 "현재값" 으로 해석 | CAD-05 | 유효(CAD-c27) |
| CAD-D17 | Set ↔ `.prt` 결합이 어느 저장 경로에도 없다 (프로젝트 전역 1개) | CAD-09 | 유효(CAD-c34) |
| CAD-D14 | NX 표현식 적용 실패가 ListingWindow 에만 기록되고 stdout 으로 안 나감 | CAD-10 | 유효(CAD-c30) |
| CAD-D1 | `.prt` 성공 경로에 로딩 스피너 정지 호출이 없다 (실패 경로에만 있음) | CAD-07 | 해소됨(CAD-c17) 유효(CAD-c18) 유효(CAD-c49) 범위밖(EXE-c44) 범위밖(UIC-c56) |
| CAD-D9 | NX CAD 스피너가 비대칭 — 프리뷰 완료 경로에 대응하는 시작 호출이 없다 | CAD-07 | 유효(CAD-c19) 유효(CAD-c49) 범위밖(EXE-c44) 범위밖(UIC-c56) |
| CAD-D3 | 한 명령의 두 산출물(파라미터 JSON · STEP)이 다른 채널로 도착하고 합류점이 없다 | CAD-01 | 유효(CAD-c04) 유효(CAD-c44) 범위밖(EXE-c42) |
| CAD-D7 | 전송 계층은 `commandId` 를 갖지만 파사드의 `emitFailure` 에 경로 인자가 없다 | CAD-01 | 유효(CAD-c03) 유효(CAD-c44) 범위밖(EXE-c42) |
| CAD-D8 | 방출 대상이 요청 단위가 아니라 전역 `m_batchMode` 1비트로 스위칭 | CAD-01 | 유효(CAD-c01) 유효(CAD-c02) 유효(CAD-c44) 범위밖(EXE-c42) |
| CAD-U4 | 데몬 성공·실패 판정이 `[FINISHED]` 전체 일치와 `[ERROR]` 부분 일치 | EXE-12 | 범위밖(CAD-c31) 유효(EXE-c29) 유효(EXE-c57) |
| CAD-D6 | 정렬 방어가 이름 매칭 2 · 시각 행 인덱스 2 · 채우기 시점 캡처 1로 갈린다 | CAD-04 | 유효(CAD-c25) 유효(CAD-c51) |
| CAD-D13 | Set 삭제 시 위젯이 `mModel` 을 정리하지 않고 직후 `deleteLater()` 가 걸린다 | 항목 없음 | 해소됨(CAD-c29) 해소됨(PRJ-c57) |
| CAD-D15 | `loadPrt` 의 temp 정리가 승격이 복사해 둔 `.prt` 보관본과 같은 경로를 지운다 | CAD-09 | 유효(CAD-c32) |
| CAD-D16 | GUI 가 `--no-cleanup` 을 항상 붙이고 일괄 정리는 `.stp` 만 글로빙 | CAD-08 | 유효(CAD-c33) |
| CAD-D4 | `loadFromJson` 복원 직후 캐시 재적용이 전 행을 `isChecked = false` 로 재구성 | CAD-03 | 유효(CAD-c21) 유효(CAD-c23) 유효(CAD-c52) |
| CAD-D2 | `.prt` 진입 초입의 `processEvents` 가 큐된 슬롯·타이머를 실행 | PRJ-26 | 범위밖(CAD-c20) 유효(PRJ-c64) 범위밖(EXE-c43) |
| CAD-D5 | Set 진입마다 도는 해석 덱 유입 경로의 결과를 읽는 곳이 0 | 항목 없음 | 해소됨(CAD-c24) |
| CAD-U3 | 도달하지 않는 선언·정의 — `saveSettings` no-op · `getContext`/`getLoadedFilePath` | CAD-06 | 유효(CAD-c11) 유효(CAD-c35) |
| CAD-U5 | `tests/` 전체에 `NxCad`·`GeometryParameter` 참조 0건 | CAD-11 | 유효(CAD-c36) 유효(CAD-c47) 유효(CAD-c48) 범위밖(UIC-c57) 범위밖(DEV-c24) |
| CON-D4 | `.ui` 의 열 선언 5열과 모델 7열이 드리프트 | CON-06 | 유효(CON-c04) |
| CON-D5 | Value 인라인 편집이 메모리 deck 만 바꾸고 설정 JSON 에 대응 키가 없다 | CON-10 | 유효(CON-c05) |
| CON-D10 | 대상 deck 이 전역 active context 1개뿐, Set 별 저장 필드가 없다 | 항목 없음 | 해소됨(CON-c10) |
| CON-D13 | ResultsAnalyzer 가 `paramObj["checked"]` 를 읽는데 그 키를 쓰는 코드가 없다 | ANA-14 | 범위밖(CON-c13) 유효(ANA-c31) |
| CON-D12 | 조건 DV 주입 실패 3종이 전부 `continue` | 항목 없음 | 해소됨(CON-c12) |
| CON-D6 | GUI 편집과 DOE 배치가 같은 RW 세션을 공유하는데 상호 배제가 없다 | 항목 없음 | 해소됨(CON-c06) |
| CON-D2 | `getOrLoad` 의 실제 로드가 뮤텍스 밖에서 돈다 | DOE-07 EXE-05 PER-02 | CID 경유 — 해소됨(CON-c02) 해소됨(REN-c35) 해소됨(EXE-c09) 범위밖(EXE-c41) |
| CON-D1 | `setProjectDirectory` 가 인자를 쓰지 않고 경로를 다시 유도한다 | CON-05 | 유효(CON-c01) |
| CON-D8 | DV 섹션 판정이 파일명에 `"Condition"` 이 포함되는지 | DOE-10 | 유효(CON-c08) |
| CON-D3 | `m_params` 가 한 번도 clear 되지 않는다 | CON-02 | 유효(CON-c03) |
| CON-D7 | `loadFromJson` 이 행을 만드는 `refreshFromLoadedAnalysis` 보다 먼저 돈다 | CON-01 | 유효(CON-c07) |
| CON-D9 | 자기 쓰기 억제 플래그를 되돌린 다음 줄의 모달이 중첩 이벤트 루프를 돈다 | CON-07 | 유효(CON-c09) 유효(CON-c24) 범위밖(EXE-c43) |
| CON-D11 | `get_symbol_detail` 이 캐시되지 않는다 | CON-07 LCH-08 LCH-12 LCH-20 PRE-23 PRJ-26 | CID 경유 — 해소됨(CON-c11) 범위밖(EXE-c43) |
| CON-U1 | `setModel` 오버로드의 유일한 호출 인자가 항상 `nullptr` | CON-06 | 유효(CON-c14) |
| CON-U3 | 디렉토리 워처의 `directoryChanged` 연결이 레포 전체 0곳 | CON-06 | 유효(CON-c15) |
| CON-U5 | `tests/` 전체에 RW 관련 5심볼 참조 0건 | CON-09 EXE-21 | 유효(CON-c16) 범위밖(CON-c17) 유효(CON-c25) 유효(EXE-c58) 범위밖(UIC-c57) 해소됨(DEV-c25) |
| DOE-D5 | 같은 샘플이 위치 기반 `samples[]` 와 이름 기반 `rawSamples[]` 두 형태로 저장 | DOE-14 | 유효(DOE-c15) 유효(DOE-c57) 범위밖(LCH-c61) |
| DOE-D2 | Probabilistic Min/Max 가 모델에 되쓰이지 않고 샘플링에만 전달 | DOE-06 | 유효(DOE-c11) 유효(DOE-c12) 유효(DOE-c54) 범위밖(LCH-c58) |
| DOE-D26 | 제약식은 설정 JSON 에 영속화되는데 그 토큰인 `v{n}` 은 행 인덱스에서 매번 재생성 | DOE-09 | 유효(DOE-c20) 유효(DOE-c59) 범위밖(LCH-c63) |
| DOE-D12 | FE-safe 의 ODB 소스 판정이 파일 존재만 보고 워크플로 실행 여부를 안 본다 | LCH-30 | 범위밖(DOE-c41) 유효(LCH-c23) 미확인(LCH-c29) 유효(LCH-c76) |
| DOE-D15 | motion-launcher 가 `.dfr` 이 없으면 하드코딩 XML 7줄로 만들어 낸다 | LCH-04 | 범위밖(DOE-c44) 유효(LCH-c39) 유효(LCH-c79) |
| DOE-D19 | condition DV 적용 실패 3경로가 warning 후 `continue`, 호출부가 결과 미검사 | 항목 없음 | 범위밖(DOE-c48) 해소됨(LCH-c52) 해소됨(LCH-c83) |
| DOE-D25 | 릴리스 빌드는 Resample 위젯을 생성하지 않는데 트리의 그 variant Set 은 남아 있다 | PRJ-24 | 유효(DOE-c19) 유효(DOE-c58) 범위밖(LCH-c62) 유효(PRJ-c52) |
| DOE-U2 | Direct Output Cases 표가 `setModel` 도 상태 시그널도 받지 않고 Status 를 `"Enqueued"` | LCH-23 | 범위밖(DOE-c35) 유효(LCH-c10) 유효(LCH-c70) 유효(LCH-c94) 유효(LCH-c95) 범위밖(EXE-c44) 범위밖(UIC-c56) |
| DOE-D17 | 모핑 배치가 GUI 소유 싱글턴 핸들 인스턴스에 VTP 를 `DeepCopy` | 항목 없음 | 범위밖(DOE-c46) 해소됨(LCH-c50) 해소됨(LCH-c81) |
| DOE-D18 | 배치가 GUI 와 공유된 해석 컨텍스트를 in-place 변이하고 원복 두 줄에 의존 | 항목 없음 | 범위밖(DOE-c47) 해소됨(LCH-c51) 해소됨(LCH-c82) |
| DOE-D16 | `.dfsxml` 경로의 완료 판정 주체가 `finished` 람다와 stdout 감시 둘 | LCH-05 | 범위밖(DOE-c45) 유효(LCH-c40) 유효(LCH-c80) 유효(LCH-c96) 범위밖(EXE-c42) |
| DOE-D21 | 종결이 키 집합 소진 집계와 `jobFinished` 직접 방출 두 갈래 | LCH-06 | 범위밖(DOE-c49) 유효(LCH-c41) 유효(LCH-c84) 유효(LCH-c96) 범위밖(EXE-c42) |
| DOE-D4 | 워커가 GUI 소유 `QAbstractItemModel` 을 직접 읽는다 (결과 기록도 모델 포인터 경유) | DOE-07 | 유효(DOE-c14) 유효(DOE-c56) 유효(DOE-c62) 범위밖(LCH-c60) 범위밖(EXE-c41) |
| DOE-D22 | 설정 JSON read-modify-write 8곳 중 뮤텍스를 지나는 것이 1곳이고 그마저 인스턴스 멤버 | DOE-07 PER-02 | 유효(DOE-c17) 범위밖(DOE-c18) 유효(DOE-c62) 해소됨(LCH-c46) 해소됨(LCH-c65) 범위밖(EXE-c41) 유효(PER-c08) 유효(PER-c33) |
| DOE-D3 | Purpose 판정이 문장 완전일치이고 리터럴이 두 곳에 이중 정의 | DOE-08 | 유효(DOE-c13) 유효(DOE-c55) 범위밖(LCH-c59) |
| DOE-D8 | 표 행 ↔ 케이스 결합이 Case Name 열 표시 텍스트 파싱 (`UserRole` 없음) | 항목 없음 | 범위밖(DOE-c37) 해소됨(LCH-c47) 해소됨(LCH-c72) 해소됨(LCH-c88) 해소됨(LCH-c88) 범위밖(RUN-c13) |
| DOE-D24 | Direct Launcher 가 `analysisType` 을 빈 문자열로 넘겨 현재 Set 의 DOE JSON 을 연다 | LCH-23 LCH-25 | CID 경유 — 범위밖(DOE-c35) 해소됨(LCH-c48) 유효(LCH-c70) |
| DOE-D6 | Geometry/Condition 판별을 세 곳이 대소문자 구분·무시·정규식으로 각자 구현 | DOE-10 | 유효(DOE-c16) 해소됨(LCH-c49) |
| DOE-D10 | 말단 6경로가 착수·상태보고·종결을 각자 구현 | LCH-07 | 범위밖(DOE-c39) 유효(LCH-c42) 유효(LCH-c74) |
| DOE-D13 | 경로 조립기 두 개의 일치를 경고-후-덮어쓰기 한 줄이 강제 | LCH-13 | 범위밖(DOE-c42) 유효(LCH-c44) 유효(LCH-c77) |
| DOE-D23 | `cancelAllRuns` 가 진행 중 프로세스만 죽이고 motion 큐를 비우지 않는다 | LCH-03 | 범위밖(DOE-c50) 유효(LCH-c09) 유효(LCH-c85) 유효(LCH-c90) 범위밖(EXE-c33) |
| DOE-D1 | `loadSettings` 가 진입 1회에 3번 호출되고 앞 둘은 시그널 연결 전 | DOE-05 | 유효(DOE-c10) 유효(DOE-c53) 범위밖(LCH-c57) |
| DOE-D7 | 케이스 상태 1건마다 JSON 전문 재기록 → 워처가 표를 전량 재구축 | LCH-08 | 범위밖(DOE-c36) 유효(LCH-c11) 유효(LCH-c71) 유효(LCH-c89) 유효(LCH-c93) 범위밖(PRJ-c07) 범위밖(EXE-c43) |
| DOE-D9 | `runDoeAsync` 가 이름과 달리 동기 — `generateInputCases` 738줄이 GUI 스레드 | LCH-20 | 범위밖(DOE-c38) 해소됨(LCH-c01) 해소됨(LCH-c73) 유효(LCH-c93) 범위밖(EXE-c43) |
| DOE-D11 | `processEvents` 16곳이 동기 대기의 대체물 (전량 `DashJobRunner.cpp`) | LCH-12 EXE-09 | 범위밖(DOE-c40) 유효(LCH-c43) 유효(LCH-c75) 유효(LCH-c93) 유효(EXE-c22) 범위밖(EXE-c43) |
| DOE-D14 | `msleep(1000)` 이 이미 끝난 동기 호출 뒤에 있다 | LCH-12 | CID 경유 — 범위밖(DOE-c43) 해소됨(LCH-c45) 해소됨(LCH-c78) 유효(3곳)(LCH-c91) 범위밖(EXE-c39) |
| DOE-U3 | `visibleParamIndices` 가 계산되지만 표는 4열 고정이라 반영될 열이 없다 | 항목 없음 | 범위밖(DOE-c51) 해소됨(LCH-c53) 해소됨(LCH-c86) |
| DOE-U4 | 호출부가 0인 함수 8종 (`createRunsFolders` 2종 · `getStatusFromFileSystem` 53줄  | DOE-11 LCH-14 | 유효(DOE-c21) 범위밖(DOE-c22) 유효(1건)(LCH-c54) 유효(1건)(LCH-c66) |
| DOE-U5 | 도달하지 않는 연결·계산 3종 (`connLog` 빈 람다 · `.ui` 콤보 2항목 · `firstPartName`) | DOE-08 LCH-14 | 유효(DOE-c13) 유효(DOE-c23) 범위밖(DOE-c24) 유효(1건)(LCH-c56) 유효(1건)(LCH-c67) |
| MOR-D5 | 핸들 이름의 정본이 트리 아이템 텍스트와 세션 한정 `QMap` 뿐 | MOR-17 | 유효(MOR-c51) |
| MOR-D9 | 범위값의 정본이 polydata 배열이 아니라 트리 셀 위젯 | MOR-17 | 유효(MOR-c55) |
| MOR-D6 | θ 는 방향 벡터로만 저장되고 표시값은 기즈모 Euler 의 역산 | MOR-17 | 유효(MOR-c52) 유효(MOR-c87) |
| MOR-D10 | `Morphing.constraints` 는 파서만 있고 writer 가 레포에 없다 | MOR-02 | 유효(MOR-c18) 유효(MOR-c56) 유효(MOR-c87) |
| MOR-D11 | 대상 파트가 어느 저장 경로에도 기록되지 않음 | 항목 없음 | 해소됨(MOR-c57) 유효(MOR-c87) |
| MOR-D2 | geometry 부재 시 파트 검증 없이 렌더링 매니저의 base actor 로 대체 | 항목 없음 | 해소됨(MOR-c48) 해소됨(MOR-c81) 범위밖(REN-c33) |
| MOR-U1 | `MODE_PHYSICS` 가 `SetInteractionMode` 의 `switch` 에서 누락 | MOR-13 | 유효(MOR-c61) |
| MOR-D3 | Generate 분기가 타입 키가 아니라 7단 `isVisible()` 캐스케이드 | MOR-12 | 유효(MOR-c49) |
| MOR-D14 | Geometry 카테고리는 트리 루트 1개에 모델 배열 2벌인데 Morphing 갈래만 행 인덱스로 조회 | 항목 없음 | 해소됨(MOR-c60) 해소됨(MOR-c84) 해소됨(PRJ-c53) |
| MOR-D12 | 명시적 리셋이 Set 이 바뀔 때만 돌고 `appendConstraintTable` 은 무조건 `insertRow` | 항목 없음 | 해소됨(MOR-c58) |
| MOR-D1 | 초기화 체인 전체가 `dataLoaded` emit 에 걸려 있고 화면 전환이 먼저 일어난다 | 항목 없음 | 해소됨(MOR-c47) |
| MOR-D7 | 프리뷰 모핑이 GUI 스레드 동기 실행 | MOR-18 CON-07 LCH-08 LCH-12 LCH-20 PRE-23 PRJ-26 | CID 경유 — 해소됨(MOR-c09) 해소됨(MOR-c53) 해소됨(MOR-c85) 범위밖(EXE-c43) |
| MOR-D8 | `processEvents` 가 모핑 루프 안 2곳 | CON-07 LCH-08 LCH-12 LCH-20 PRE-23 PRJ-26 | CID 경유 — 해소됨(MOR-c54) 해소됨(MOR-c85) 범위밖(EXE-c43) |
| MOR-U2 | 툴바 Prev/Next 가 emit 만 하고 수신처가 없다 | MOR-14 | 유효(MOR-c62) 유효(PRJ-c44) |
| MOR-D4 | `DashHandlePickingInteraction` 3,121줄이 픽킹·기즈모·핸들 데이터·구속 오버레이 4역 | MOR-15 | 유효(MOR-c33) 유효(MOR-c50) |
| MOR-D13 | 컨트롤러가 뷰 포인터를 무가드로 역참조하는 곳 6군데 | 항목 없음 | 해소됨(MOR-c59) |
| OPT-D22 | 피팅 결과가 DV 표 위젯에만 쓰이고 `m_designVariables` 에 도달하지 않음 | OPT-06 | 유효(OPT-c34) |
| OPT-D24 | 심볼의 표시분은 행 인덱스 재생성, 모델분은 JSON `symbol`, 복원 매칭은 응답 이름 | OPT-08 | 유효(OPT-c28) |
| OPT-D5 | 최적화 모드 2차 판정이 1 로 올리기만 하고 0 으로 내리지 않는다 | OPT-11 | 유효(OPT-c15) 유효(OPT-c52) |
| OPT-D6 | Fixed 체크와 Init. Value 편집이 모델에 도달하지 않음 (시그널 미연결) | OPT-06 | 유효(OPT-c16) 유효(OPT-c52) |
| OPT-D7 | Minimize/Maximize 콤보에 수신 슬롯이 없다 | OPT-06 | 유효(OPT-c17) 유효(OPT-c52) |
| OPT-D12 | `saveSettings()` 호출처가 `runOptimization` 하나 | OPT-07 | 유효(OPT-c22) 유효(OPT-c52) |
| OPT-D21 | `m_activeModelBuilderFolder` 에 설정 JSON 왕복이 없다 | OPT-15 | 유효(OPT-c33) 유효(OPT-c52) |
| OPT-D8 | [+] 가 심는 예시 구속이 회색 placeholder 가 아니라 보통 아이템이고 즉시 모델에 들어간다 | OPT-12 | 유효(OPT-c18) |
| OPT-D11 | `optimizationFailed` 의 `connect` 가 레포 전체에 없다 | OPT-05 EXE-10 | 유효(OPT-c21) 유효(OPT-c50) 유효(EXE-c24) 범위밖(EXE-c44) |
| OPT-D13 | 중복 실행 방지가 모델의 `m_currentJob` 가드뿐이고 버튼은 열려 있다 | OPT-05 EXE-07 EXE-09 | 유효(OPT-c23) 유효(OPT-c48) 유효(OPT-c50) 유효(EXE-c22) 범위밖(EXE-c44) 범위밖(UIC-c55) |
| OPT-D18 | [Render Preview] 가 핸들 배열·렌더러 액터·전역 active context 3종을 갈아끼우고 복구 코드가 없다 | OPT-01 | 유효(OPT-c01) 유효(OPT-c03) 해소됨(OPT-c29) 유효(OPT-c43) 유효(OPT-c45) 범위밖(REN-c19) 범위밖(REN-c32) |
| OPT-D19 | 요청에 태그가 없고 완료 수신처가 `DashMainWindow` | CAD-01 OPT-22 | 유효(CAD-c41) 범위밖(OPT-c10) 유효(OPT-c39) 범위밖(EXE-c42) |
| OPT-D4 | 1D / ND 열 가시성이 첫 행 응답 이름의 `"(Field)"` 부분문자열로 정해진다 | OPT-10 | 유효(OPT-c14) |
| OPT-D14 | 검증 표 헤더 분류가 `startsWith("r")` + 두 번째 글자 숫자 규칙 | OPT-14 | 유효(OPT-c24) |
| OPT-D20 | 설정 JSON 이 실데이터가 아닌데 플롯의 실재 게이트로 쓰인다 | ANA-15 | 유효(ANA-c32) 범위밖(OPT-c30) |
| OPT-D15 | 프리뷰가 `templateFileName` 필터를 무시하고 configs 의 deck 전량을 순회 | OPT-26 | 유효(OPT-c25) 유효(OPT-c56) 유효(OPT-c57) |
| OPT-D1 | 같은 `model_info.json` 을 두 로더가 읽고 NaN 정화 수준이 다르다 | OPT-16 | 유효(OPT-c11) |
| OPT-D2 | Set 삭제 후 `setModel(nullptr)` 이 표 내용과 `setEnabled(true)` 를 그대로 둔다 | OPT-17 | 유효(OPT-c12) 유효(OPT-c42) 범위밖(PRJ-c58) |
| OPT-D3 | 폴더 변경 슬롯이 두 표만 재구성하고 `populateOptimizationSettings` 를 안 부른다 | OPT-09 | 유효(OPT-c13) |
| OPT-D10 | 방법 선택마다 옵션 칸에 기본값을 주입하고, 저장값 복원은 그 직후 덮어쓰는 순서로만 성립 | OPT-13 | 유효(OPT-c20) |
| OPT-D16 | 프리뷰 모핑이 GUI 스레드 동기이고 이 모듈 `processEvents` 2곳이 모두 그 루프 안 | OPT-26 | 유효(OPT-c09) 해소됨(OPT-c26) 유효(OPT-c57) |
| OPT-D17 | `performMorphing` 이 만든 `.vtu` 2종을 호출부가 곧바로 지운다 | OPT-01 | 유효(OPT-c27) |
| OPT-U2 | 도달하지 않는 선언 4종 | OPT-18 | 유효(OPT-c31) |
| OPT-U3 | `tests/` 전체에 Optimizer 참조 0건 | OPT-20 | 유효(OPT-c32) 유효(OPT-c54) 유효(OPT-c55) 범위밖(UIC-c57) 범위밖(DEV-c24) |
| OPT-D9 | `[popOS]` 디버그 `qDebug` 27줄과 `showEvent` 7줄이 빌드 가드 없이 남아 있다 | OPT-18 | 해소됨(OPT-c19) 유효(OPT-c31) |
| OPT-D23 | 피팅의 학습 모델 경로가 `ModelBuilder_LGE_Spring_Fitting` 하드코딩 | OPT-19 | 유효(OPT-c35) |
| PRE-D7 | 설정 JSON 4섹션 중 `Dataset`·`Output Response` 를 읽는 코드가 없다 | PRE-26 PRE-27 | 유효(PRE-c51) 유효(PRE-c61) |
| PRE-D8 | KPI 행 추가만 `saveOutputResponseToJson` 을 부르지 않는다 | PRE-26 PRE-27 | 유효(PRE-c62) |
| PRE-D10 | 모든 run 이 비-Done 이면 `Done` 필터 결과를 버리고 원본 배열을 쓴다 | PRE-16 | 해소됨(PRE-c63) |
| PRE-U1 | `.op2` 가 확장자 목록·파일 대화상자 필터·솔버 목록에는 있고 라우팅 분기에 NASTRAN 이 없다 | PRE-25 | 유효(PRE-c64) |
| PRE-D4 | Modal 판정이 `contains("modal")` 이고 대상이 단일 파일 모드에서는 basename | PRE-09 | 유효(PRE-c44) 해소됨(PRE-c65) |
| PRE-D5 | `isAnsysMotion` 플래그에 `hasFunctionExpression` 이 실린다 | PRE-08 | 유효(PRE-c66) |
| PRE-D11 | KPI 5종이 배치 입력 로딩(스냅샷-또는-합성) 블록을 각자 복제 | PRE-22 | 유효(PRE-c67) |
| PRE-D1 | `setModel` 에 Output Response 표 초기화가 없다 | 항목 없음 | 해소됨(PRE-c68) |
| PRE-D2 | `onAnalysisFileSelected` 의 조기 반환 4곳이 `endProcessing()` 을 건너뛴다 | 항목 없음 | 해소됨(PRE-c69) |
| PRE-D6 | 배치 후 DLL 상태 복원 블록이 5곳에 있고 일반 배치·Modal KPI·조회 경로에는 없다 | PRE-21 | 유효(PRE-c70) |
| PRE-D3 | 전용 워커·직렬 풀·게이트 0건이고 `processEvents` 25곳이 응답성을 대신한다 | PRE-23 | 유효(PRE-c11) 유효(PRE-c12) 유효(PRE-c71) 유효(PRE-c80) 범위밖(EXE-c43) |
| PRE-D9 | KPI 경로가 `m_isProcessing = true` 보다 앞에서 반환해 재진입 가드 밖에 있다 | CON-07 LCH-08 LCH-12 LCH-20 PRE-23 PRE-24 PRJ-26 | CID 경유 — 해소됨(PRE-c72) 유효(PRE-c80) 범위밖(EXE-c43) |
| PRE-U2 | `initializePreprocessor` 의 `res`·`dfsxml` 분기가 도달하지 않는다 | PRE-25 | 유효(PRE-c73) |
| PRE-U3 | `m_dynamicTables` 는 채우고 비우기만 하고 읽는 코드가 없다 | 항목 없음 | 해소됨(PRE-c74) |
| PRE-D12 | `DashDataProcessor.cpp` 4,671줄이 스캔·질의·XML·KPI 4역 (코드베이스 단일 최대) | 항목 없음 | 해소됨(PRE-c75) |
| RUN-D2 | `variant` 가 JSON 키와 Set 이름 접미사에 이중 보관 | RUN-26 | 유효(RUN-c20) |
| RUN-D10 | 설계변수 값의 정본이 모델이 아니라 셀 위젯 (시그널 결선 없이 폴링) | RUN-17 | 유효(RUN-c27) |
| RUN-D20 | NodeSet 판정 근거가 `Qt::UserRole` 과 이름 목록 2벌이고 후자는 미호출 | 항목 없음 | 해소됨(RUN-c36) |
| RUN-D24 | 두 번째 `updateModelUploadConfig` 가 첫 번째의 `Output Response` 를 덮음 | RUN-05 | 유효(RUN-c38) |
| RUN-D26 | `updateModelUploadConfig` 가 `model_info.json` 을 재파싱해 사용자 입력값을 기본값으로 덮음 | RUN-04 | 유효(RUN-c40) |
| RUN-D33 | 설정 JSON 의 `Prediction Cases`·`Output Response`·`Input Design Variables` | RUN-13 | 유효(RUN-c47) |
| RUN-D34 | `m_predictionCount` 가 세션을 넘기지 못하고 0 에서 재시작 | RUN-10 | 유효(RUN-c15) |
| RUN-D35 | Morphing 생성은 `.vtu` 경로를 싣고 디스크 스캔은 `*.dat`·`*.inp` 를 집는다 | RUN-13 | 유효(RUN-c17) |
| RUN-D14 | `SetBoxHandles` 가 렌더러 부재 시 데이터 없이 반환, 최종 가드는 "비어 있지 않은가" 뿐 | 항목 없음 | 해소됨(RUN-c31) 유효(RUN-c69) 범위밖(REN-c33) |
| RUN-D23 | `startPredictionJob` 의 거절 반환값을 호출부 3곳이 검사하지 않는다 | RUN-05 | 유효(RUN-c07) |
| RUN-D29 | 민감도 콤보가 다른 계층의 키를 기대하고 4단 중첩 `if` 에 로그가 없다 | ANA-18 | 유효(RUN-c43) |
| RUN-D30 | 민감도 폴더 열거에 Set 필터가 없다 | ANA-06 | 유효(RUN-c44) |
| RUN-D13 | Generate 가 Geometry Parameterization 의 공용 핸들 인스턴스를 제자리 교체 | 항목 없음 | 해소됨(RUN-c30) |
| RUN-D15 | `enqueueUpdatePrtGeometry` 가 요청 식별자를 돌려주지 않고 짝짓기가 멤버 문자열 비교 | CAD-01 RUN-09 | 유효(CAD-c39) 범위밖(RUN-c32) 유효(RUN-c70) 범위밖(EXE-c42) |
| RUN-D11 | 스핀박스 상한을 `max - 0.0001` 로 깎고 미설정 판정을 `value != 0.0` 으로 한다 | RUN-16 | 유효(RUN-c28) |
| RUN-D12 | Part 콤보가 모핑 대상이 아니라 `_input_geometry.vtu` 추출 대상만 고른다 | RUN-03 | 유효(RUN-c29) |
| RUN-D18 | 템플릿 치환이 `QMap` 사전순 전역 텍스트 치환 | RUN-18 | 유효(RUN-c34) |
| RUN-D21 | 행 삭제 범위가 `completeBaseName()` 접두사 매칭 | RUN-11 | 유효(RUN-c16) |
| RUN-D37 | MCU 민감도가 이미 `-MCU` 로 끝나는 이름에 접미사를 다시 붙인다 | RUN-22 | 유효(RUN-c49) |
| RUN-D8 | 소스 종류 판정이 `parameter` 딕셔너리 순회 중 첫 매치에서 `break` | RUN-14 | 유효(RUN-c05) 유효(RUN-c68) |
| RUN-D22 | `[Preview]` 만 람다 캡처된 `row` 를 쓴다 (`[X]` 는 매번 재계산) | UIC-24 | 범위밖(RUN-c37) 유효(UIC-c53) 유효(UIC-c62) |
| RUN-D25 | `m_lastPreviewedVtuPath` 를 루프 끝에서 한 번만 세운다 | RUN-20 | 유효(RUN-c39) 유효(RUN-c68) 유효(RUN-c69) 범위밖(REN-c33) |
| RUN-D6 | ND 판정이 응답 이름 부분문자열과 모델 이름 접두사 화이트리스트 2벌 | BLD-21 RUN-15 | 유효(BLD-c45) 유효(RUN-c24) |
| RUN-D9 | `Source` 열 라벨이 같은 JSON 을 다시 열어 별개로 판정하고 실패 3경로가 한 값 | RUN-14 | 유효(RUN-c26) |
| RUN-D19 | 정규화 config 파싱 실패의 처리가 경로마다 다르다 | RUN-08 | 유효(RUN-c35) |
| RUN-D4 | 공용 데몬 수명이 Set 전환에만 묶이고 모듈 이탈에는 안 묶인다 | 항목 없음 | 해소됨(RUN-c22) 해소됨(EXE-c34) |
| RUN-D16 | `m_pendingCadStpPath` 가 완료 슬롯 진입 직후에만 지워진다 | RUN-09 | 유효(RUN-c33) |
| RUN-D17 | CAD 완료 처리가 파일 표를 통째로 재구축한다 | RUN-07 | 유효(RUN-c04) |
| RUN-D31 | 민감도 캐시 키에 모델 내용이 없고 캐시를 비우는 곳이 2곳뿐 | 항목 없음 | 해소됨(RUN-c45) |
| RUN-D32 | 민감도 실패 4경로가 `m_pendingCommand` 를 지우지 않는다 | 항목 없음 | 해소됨(RUN-c46) 해소됨(RUN-c60) 범위밖(EXE-c35) |
| RUN-D36 | `clearAllTables` 가 `m_predictionCount`·`m_pendingCadStpPath`·`m_pendin` | RUN-09 RUN-10 | 유효(RUN-c15) 유효(RUN-c48) |
| RUN-D38 | Set 불일치 시 표를 비우는 방어에 `!currentSetName.isEmpty()` 예외가 붙어 있다 | RUN-21 | 유효(RUN-c50) |
| RUN-D5 | 모델 적재 전 구간이 GUI 스레드 직렬이고 같은 파일을 계층마다 다시 읽는다 | RUN-24 RUN-25 EXE-22 | 유효(RUN-c08) 범위밖(RUN-c09) 유효(RUN-c23) 유효(EXE-c59) |
| RUN-D3 | `daemonReady` 유실 보정이 3벌 중복이고 폴링이 실효 경로 | 항목 없음 | 해소됨(RUN-c21) 해소됨(RUN-c61) 범위밖(EXE-c36) |
| RUN-D27 | 1D 결과 대기가 고정 500ms 뒤 `lastModified` 최대 CSV 선택 | RUN-19 EXE-12 | 유효(RUN-c41) 유효(RUN-c62) 유효(EXE-c29) 범위밖(EXE-c38) |
| RUN-D7 | `configsDir` 이 양쪽 컨텍스트에 Set 무관 전역 경로로 들어가 삼항 폴백이 무의미 | RUN-27 | 유효(RUN-c25) |
| RUN-U1 | `syncFileTableToJson` 이 주석뿐인 빈 본문인데 3곳에서 호출된다 | RUN-13 | 유효(RUN-c51) |
| RUN-U2 | 체크 행 일괄 삭제 39줄이 구현돼 있으나 `connect` 0건이고 버튼도 없다 | RUN-29 | 유효(RUN-c52) |
| RUN-U3 | `params.fileTableFiles` 와 그 유일한 소비 함수가 도달 불가 | RUN-29 | 유효(RUN-c53) |
| RUN-U4 | 구버전 CLI 형태(출력 디렉터리 인자 없음)의 예측 슬롯이 남아 있다 | RUN-29 | 유효(RUN-c54) |
| RUN-U5 | 도메인 신호 4종의 수신처가 0곳 | RUN-29 | 유효(RUN-c55) |
| RUN-U6 | 도달하지 않는 정의 18종 | RUN-29 | 유효(RUN-c56) |
| RUN-D28 | 뷰가 `DashMainWindow` 를 부모 거슬러 4벌로 찾는다 | RUN-28 PRJ-25 | 유효(RUN-c42) 유효(PRJ-c54) |

집계: 항목 159 · 해소됨 21 · 항목(CID 경유) 8 · 범위밖/해소됨 8 · CLOSE 3 · 유효/해소됨 1 · 범위밖/유효/해소됨 1

