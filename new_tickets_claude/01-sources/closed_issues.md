# 닫힌 이슈 (보드 Done · Won't do) — 해소/제외 판정 사전

| # | Status | 제목 | 라벨 |
|---|---|---|---|
| #207 | Done | W6-1: 공용 실행 엔진 정비 — runAsync 수리·공통 책임 집약·killOrphans PID 축소 | refactor,split-group:207 |
| #208 | Done | W6-2: model 소비자 3종 실행 엔진 위임 전환 | in-progress,refactor,split-group:207 |
| #209 | Done | W6-3: view 소유 QProcess 2곳 controller 이전 — 창 닫힘 = 작업 사망 해소 | refactor,split-group:207 |
| #210 | Done | W10-a: DOE 배치 파일럿 — 데몬 파사드 이벤트 구동 전환 (갈래② · Job 미생성) | refactor,split-group:210 |
| #211 | Won't do | W10-b: 파일 폴링 → 완료 시그널 구독 전환 (워처/타이머는 보조) | refactor,split-group:210 |
| #212 | Done | W10-c: 데몬 기동 비동기화 — DaemonHost 이식 (기동 이벤트 수신·명령 경로 무변경) | refactor,split-group:210 |
| #213 | Won't do | W10-d: 워커 선결 조건 6건 해소 (WorkerJob 게이트) | refactor,split-group:210 |
| #214 | Won't do | W10-e: WorkerJob + 서브시스템 직렬 풀 2종 도입 | feature,split-group:210 |
| #215 | Won't do | W10-f (부모): 워커 후보 적용 + model processEvents 전량 제거 — 실측·설계 검토·3분할 근거 | refactor,split-group:210 |
| #224 | Done | N1-a: 증분 빌드 시간 단축 — extensions 트리 배포 게이팅 (636s -> 60s 목표) | performance,infra |
| #241 | Done | [W13] 미세 색 변화 2건 시각 QA | refactor |
| #242 | Done | [W13] 디자인 정규화·Figma 디자인 요소 이관 | refactor |
| #243 | Done | [W14] Geometry 위젯 .ui 드리프트 재평가·재적용 | refactor |
| #244 | Done | [W19] ResultsAnalyzer dead 코드·잔여 코드 정리 (P3b) | refactor |
| #245 | Done | [W19] 팩토리↔ResultsAnalyzer 위젯 friend 디커플링 | refactor |
| #251 | Won't do | DOE 2단계 배치의 이벤트·상태 처리 표준 수립 | refactor |
| #258 | Done | [W19] 팩토리↔ResultsAnalyzer objectName/findChild 문자열 계약 해소 (#245b) | refactor |
| #260 | Won't do | W10-e0: 모핑 DOE 배치 per-sample 분해 파일럿 (#214 선행) | refactor,split-group:210 |
| #264 | Won't do | 장부 밖 경로를 장부로 통합 — 종결 지점 2곳 확정 · 런처 키 카운터 삭제 | bug |
| #265 | Won't do | 솔버 제출 로직 중복 통합 — ANSYS 3벌 · Abaqus 2벌 · direct wbpj 배치 승격 | refactor |
| #266 | Won't do | DOE JSON 설정/실행상태 분리 — 케이스 상태 단일 라이터 | refactor |
| #267 | Won't do | Direct 경로 케이스 상태 키 분열 — status vs status_<stale> | bug |
| #268 | Won't do | STP 타임아웃 후 데몬 무응답 시 A 배치 영구 정지 — 워치독 재무장 부재 | bug |
| #269 | Done | DashJobRunner 케이스별 분해 — .stli·.wbpj·.dfsxml·.inp·.dat 생성·제출 함수 분리 + TU 6개 | in-progress,refactor |
| #274 | Won't do | 274 모핑 국면 가드를 #214 확정 설계에 맞추기 — 게이트 증명화 · 판정 단일화 · 종료 오케스트레이션 | bugfix |
| #277 | Won't do | W10-f-1: RST/KPI 파싱 워커화 + preprocessor 직렬 풀·게이트 신설 | refactor,split-group:215 |
| #278 | Won't do | W10-f-2: 모핑·RW·프로세스·view 축 워커화 잔여 6 Phase | refactor,split-group:215 |
| #279 | Won't do | W10-f-3: 잔여 processEvents 일소 + view 아종 분류 + W10 DoD 봉인 | refactor,split-group:215 |
| #280 | Won't do | W10-f-2a: RW 격리·감금 잔여 정리 — 읽기 캐시 승격, 레지스트리 키 폴백, 배제 기제 선택 규칙 | refactor,split-group:215 |
| #282 | Won't do | W10-f-2c: dfsxml stage 1·2 ProcessJob 수렴 + FEM 파서 워커화 — 독립 축 2건 | refactor,split-group:215 |
| #283 | Won't do | W10-f 후속: VTU/CSV 쓰기 축 재판정 — dead code 2곳 삭제, 잔여는 워커화 불요 | backlog,refactor |
| #290 | Won't do | feat/rw-actor 를 refactor/async-execution 으로 흡수 — RW 격리 채택, rwSerialPool·RwGate 폐기 | refactor,split-group:215 |
| #321 | Done | Coding convention 고정 및 pre-commit, clang-format, clang-tidy | refactor,area:DevEnv |
| #360 | Done | G1 기준모델 층 신설 + 소비자 이동 (T1·T3·T4) | feature,split-group:360 |
| #361 | Done | G2 렌더 커서 저장을 프로젝트 루트 상대경로로 통일 (T2) | feature,split-group:360 |
| #362 | Done | G3 렌더 커서 개명 active* → displayed* (T5) | refactor,split-group:360 |
| #363 | Done | G4 Mesh View 도크 제목줄 + 죽은 코드 제거 (T7·T8) | feature,split-group:360 |
| #364 | Done | G5 기준모델 목록 파일(referenceModels.json) 도입 (T9·T10·T11) | in-progress,feature,split-group:360 |
| #365 | Done | G6 파일 식별자를 uuid 로 통일 + 구 식별자 파일 삭제 (T12·T13) | in-progress,refactor,split-group:360 |
| #366 | Done | G7 각 Set 이 자기 기준모델을 저장하고 사용 (T14·T15·T16·T19) | in-progress,feature,split-group:360 |
| #367 | Done | G8 Launcher 가 형상·조건 세트 조합을 기록 + 화면 데이터 출처 교체 (T20·T17) | feature,split-group:360,needreview |
| #388 | Done | 로컬 설정 절차를 조사해 모으고 스크립트 하나로 만든다 | area:DevEnv |
| #402 | Done | DashXmlParser: 텐서 파싱이 블롭 크기의 5~6배를 복사한다 (int32 미처리·경계 검사 누락 동반) | in-progress,performance,split-group:413 |
| #403 | Done | 모핑 엔진 소유권 분리 + 고정점 마커 영속화 — #281 결합 ⑴⑵⑶ 선행 해소 | refactor,split-group:215 |
| #408 | Done | Morphing 요청 서비스 — 레인 스케줄링·스레드 예산·결과 반환 | refactor,split-group:215 |
| #409 | Done | DashXmlParser: 필요한 것만 읽는 경로가 없다 — 변수 목록·축약값에도 전량 디코딩이 붙는다 | performance,split-group:413 |
| #410 | Done | Analyzer: 한 번의 UI 조작이 같은 XML 을 2회 이상 파싱한다 — 한시 캐시 도입 | performance,split-group:413 |
| #412 | Done | Analyzer 가 데이터셋 XML 을 열지 않아도 되게 — 메타데이터·축약값 분리 (방향성) | backlog,refactor,split-group:413 |
| #413 | Done | XML 접근 경로 성능 개선 통합 — 파싱 비용 · 선택적 로드 · 중복 파싱 · 포맷 (부모) | performance |
| #422 | Done | DashMorphingBasis::Morph 가 수치 실패를 nullptr 로 접는다 — 실패 사유를 호출자에게 전달 | refactor,split-group:215 |
| #428 | Done | 모핑 핸들 데이터와 표시 코드의 결합 절단 — 타입 신설 없이 단독 커밋 가능한 4건 | refactor,split-group:427 |
| #429 | Done | 해석 결과 읽기 캐시의 화면·실행 공유 해소 — registry 소비 6곳을 실행 단위 소유로 | refactor,split-group:427 |
| #435 | Done | 고객사 전용 KPI 계산 코드 분리 | refactor |
| #436 | Done | 공용 데몬의 기동·재기동·종료 시점 규칙 정립 | bugfix |
| #437 | Done | 데몬 준비 신호와 현재 상태 조회의 계약 일원화 | refactor |
| #445 | Done | Set 목록 화면과 소비 추적 | feature,split-group:443 |
| #452 | Done | 격리: Analysis Launcher 갈래 분리 — .stli·.wbpj·.dfsxml 추출 (동작 불변) | refactor,split-group:451 |
| #453 | Won't do | - | docs,split-group:451 |
| #476 | Done | 항목 대장·목록 화면 | feature,split-group:473 |
| #491 | Done | DOE 조건 세트 다중 선택 — 선택 UI·저장 형식·실행 시 값 적용 (T24·T25·T26 치환부) | feature,split-group:360 |
| #493 | Done | 미리보기에서 어댑터 예외를 아무도 받지 않아 프로세스가 abort 된다 | bugfix,refactor,source:QC |
| #500 | Done | DOE Launcher: Target Component 를 바꿔도 모핑 메시는 GP 세트 part 로 고정 — edit_mesh 위상 불일치로 해석 입력 생성 전 케이스 실패 | bugfix,source:QC |
| #503 | Done | Morphing Settings physics 파일 표: browse 버튼이 캡처한 행 번호가 삭제 후 어긋나 엉뚱한 행 기록 또는 크래시 (#419 와 같은 결함) | bug,refactor |
| #520 | Done | G11 setId 도입 + #491·#367 조인 setId 전환 (T28·T29) | in-progress,feature,refactor,split-group:360 |
| #521 | Done | 해석 deck 적재 시 가시성 적용이 actor 생성보다 먼저 일어나 표시 상태가 유실된다 |  |
| #522 | Done | Data Preprocessor:  Data Upload 탭에서 run마다 이름이 다른 .rst 파일이 파일별로 테이블 분리됨 | bug,refactor,source:QC |
| #523 | Done | Data Preprocessor: AnsysMotion .dfr 단일 파일 import 시 결과가 렌더링되지 않음 | bug,source:QC |
| #525 | Done | Morphing: Geometry Parameterization 세트를 열지 않은 세션에서 DOE 모핑이 핸들을 복원하지 못해 전 샘플 실패 | bug,source:QC |
| #526 | Done | G12 G7 후속 정정 — backfill 핀 출처 교체 + multi-source 자동 분할 + 해석 스캔 분기 제거 (T30·T31) | bugfix,refactor,split-group:360 |
| #544 | Done | 비동기 실행층 도입과 대용량 XML 파싱 워커 이관 | refactor |
| #546 | Done | Morphing Handle 트리: Delete·Group 결함 정리 — 선택 모델 UI 명시·정렬·No.·그룹 유령 멤버십/번호 증가 | bug,in-progress,refactor |
| #548 | Done | MCU Model Builder 의 Stop 이 학습 중지·데몬 재기동에 도달하지 않는다 — DashModelBuilder::stopTraining() 비가상 hiding | bugfix,refactor |
| #549 | Done | 프로젝트 전환 시 Model Runner 위젯이 해제된 DashModelRunner 를 계속 가리킨다 — clearAllSets() 뒤 setModel 재진입에서 use-after-free | bugfix,refactor |
| #556 | Done | DashVolumeMeshSet::assembleVolume 의 순서 — 중간절점 재계산 뒤 고정점 원복이라 고정 코너 옆 중간절점이 어긋난다 | backlog |
| #560 | Done | 프로젝트 전환 시 CAD 형상 모델만 정리되지 않는다 — clearAllSets() 누락으로 누수와 교차 프로젝트 오염 | bugfix,refactor |
| #565 | Done | 조건 파라미터화 모델이 자기가 보여 주는 문서를 값으로 들게 한다 — 전역 원장 방송 의존을 걷는다 | refactor |
| #568 | Done | Data Upload 결과 표 구성 실패 시 로딩 스피너가 꺼지지 않는다 — onAnalysisFileSelected 오류 반환 4곳이 endProcessing() 누락 | bugfix,refactor |
| #569 | Done | DashDataProcessor 절단면 1 — Data Upload 데이터셋 스캐너를 순수 함수로 추출 (동작 불변) | refactor,split-group:433 |
| #573 | Done | Data Upload: 새 결과 읽기 작업마다 리더 재생성 | refactor |
| #581 | Done | Analysis Launcher: Orthogonal Array 의 Level 옵션이 표시되지 않음 (QStackedWidget 경고) | bugfix,refactor |
| #586 | Done | 모핑 local 화 — 서비스 레인 제거·실행 본체 통합·입력 수집기 분리 |  |
| #589 | Done | Data Upload: 빈 응답 목록이면 다음 결과 파일 탐색 | in-progress,bugfix,refactor |
| #590 | Done | 원형도 계산: 대상 부품 누락 시 샘플 제외 | in-progress,bugfix,refactor |
| #597 | Done | DOE Sampler·Analysis Launcher 재구성 — Launcher 탭 이관, Project Files 트리, Set명 고정 | feature,refactor |
| #598 | Done | 클래스명 정리 — DashAnalysisLauncher→DashDoeSampler, DashDataProcessor→DashAnalysisLauncher | refactor |
| #599 | Done | Module Tree: Geometry Parameter·DOE Sampler Set명을 고정하고 중복 생성을 막는다 | feature,refactor |
| #600 | Done | 모듈명 변경 — Analysis Launcher→DOE Sampler, Data Preprocessor→Analysis Launcher | refactor |
| #601 | Done | Analysis Launcher: DOE Launcher 탭을 첫 탭으로 이관하고 Data Upload 탭을 제거한다 | feature,refactor |
| #602 | Done | Modeling Tree: 프로젝트 파일 관리 트리(Project Assets)로 전환한다 | feature,refactor |
| #603 | Done | Condition Parameter: Reference File과 Set을 1:1로 연동한다 | feature,refactor |
| #605 | Done | 모핑 상태 이관 완결 — DashManager 협력자 등록·시그널 정리와 DOE 실행 facade 이탈 |  |
| #623 | Done | Ansys 배치가 카탈로그의 field 이름 키를 못 읽어 모든 샘플을 건너뛴다 | bug,refactor |
| #633 | Done | Module Tree: 상류 DOE Table id가 바뀐 Analysis Launcher Set에 경고 아이콘을 표시한다 | feature,refactor |
| #640 | Done | Analysis Launcher: 런처가 Done 시점에 결과 파일을 기록하고 Preprocess는 추측 없이 그 기록을 쓴다 (Target file 선택) | bug,refactor |
