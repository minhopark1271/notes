# 모듈 9종 결함 통합 색인 — 성격별 분류

> 좌표 기준: 201건 판정은 `cf44c25` 실측. 줄 번호는 원문서 좌표(`ac6e4e6` 또는 `4c7608e`)이고 전수 재측정하지 않았다 — 런타임 검증은 어느 항목에도 없다

모듈별 사용자 플로우 ↔ 코드 대응 9종의 "결함 목록" 절을 한 표로 합쳤다. **201건** — 잘못 구현된 것(`D`) 172건, 구현되지 않은 것(`U`) 29건.

ID 는 `{모듈}-{원문서 ID}` 다. 좌표(파일·줄)와 근거 전문은 원문서의 같은 ID 를 보면 된다.

`MOR` [[Morphing|Code-Map-User-Flow-Geometry-Parameterization-Morphing]] (D14·U2) · `CAD` [[CAD|Code-Map-User-Flow-Geometry-Parameterization-CAD]] (D17·U3) · `CON` [[Condition Parameterization|Code-Map-User-Flow-Condition-Parameterization]] (D13·U3) · `DOE` [[Analysis Launcher|Code-Map-User-Flow-Analysis-Launcher]] (D25·U4) · `PRE` [[Data Preprocessor|Code-Map-User-Flow-Data-Preprocessor]] (D12·U3) · `BLD` [[Model Builder|Code-Map-User-Flow-Model-Builder]] (D15·U2) · `RUN` [[Model Runner|Code-Map-User-Flow-Model-Runner]] (D37·U6) · `ANA` [[Results Analyzer|Code-Map-User-Flow-Results-Analyzer]] (D15·U4) · `OPT` [[Optimizer|Code-Map-User-Flow-Optimizer]] (D24·U2)

**후속 문서 3종은 201건판으로 재측정했다.**

| 문서 | 재측정 결과 | 남은 206건판 |
|---|---|---|
| [[Cross-Module-Defect-Menifest-Axis]] | 매니페스트 귀속 70 → **73건** · 7축 A 13·B 11·C 5·D 15·E 8·F 15·G 6 · 동반 29/독립 44 · Set 제거 시뮬레이션 21→26건 · Sim/MCU 14→13건 | 없음 |
| [[Cross-Module-Defect-Axis-Candidates]] | 배타 배정 전수 재작성 — 매니페스트 72 · 소유 33 · 배선 30 · 통지 23 · 실행 19 · 판정 18 · 진입 6 | 중복 집계(1-2) · 주축·부축 비(1-3) · 부축 비대칭(3-2) · 공유 자원 절단(4장) — **부축·자원의 ID별 배정이 어느 문서에도 없어 델타 계산이 불가능하다** |
| [[Trial-Release-Work-Breakdown-and-Axes]] | 앞단 57 → **52** (중단 44 · 뒷단 105 는 상계) · 3인 배분 A 52/B 68/C 81 | 공유 자원 건수 열 |

---

## 결함 통합 색인

원문서는 각각 진입·수명 / 데이터 정본 / 구조·결합 / 실행 모델 4분류를 쓴다. 이 표는 그 축을 버리고 **모듈 경계를 가로지르는 기제**로 다시 묶었다 — 같은 성격이 여러 모듈에서 반복되는지 보기 위해서다. 원문서의 분류와 1:1 대응하지 않는다. 우선순위 판정은 하지 않는다.

성격 17종의 분포 — 왕복 단절 28 · 죽은 코드 25 · 암묵 계약 21 · 조용한 실패 19 · 수명·정리 누락 19 · 동기 실행·재진입 15 · 정본 이중화 12 · 규칙 중복 11 · 위치·순서 결합 9 · 통지 미결합 7 · 순서 의존 7 · 피드백 부재 6 · 공유 상태 오염 6 · 구조 잔여 6 · 고정 지연·폴링 4 · 스레드 경계 3 · 검증 부재 3.

| 성격 | ID | 결함 | 귀결 |
|---|---|---|---|
| 1 정본 이중화 | MOR-D5 | 핸들 이름의 정본이 트리 아이템 텍스트와 세션 한정 `QMap` 뿐 | VTP 배열 11종에도 JSON 에도 없어 세션을 넘기지 못한다 |
| 1 정본 이중화 | MOR-D9 | 범위값의 정본이 polydata 배열이 아니라 트리 셀 위젯 | 셀 위젯에 되쓰지 않는 배열 변경 경로는 저장값과 어긋난다 |
| 1 정본 이중화 | CAD-D12 | 범위값의 정본이 모델이 아니라 셀 위젯의 스핀박스 | 위젯을 거치지 않고 모델만 바꾸는 경로가 생기면 저장값과 어긋난다 |
| 1 정본 이중화 | CON-D4 | `.ui` 의 열 선언 5열과 모델 7열이 드리프트 | 런타임은 모델이 덮어써 증상이 없지만 디자이너 편집이 무효다 |
| 1 정본 이중화 | DOE-D5 | 같은 샘플이 위치 기반 `samples[]` 와 이름 기반 `rawSamples[]` 두 형태로 저장 | `.wbpj` 경로만 후자를 읽어, 한쪽만 갱신하는 변경이 경로별로 다르게 보인다 |
| 1 정본 이중화 | BLD-D1 | Set 갈림 근거가 `UserRole+2` · JSON `variant` · 이름 접미사 3벌 | 읽는 5곳이 각각 다른 기준을 봐, 어긋나면 같은 Set 이 경로마다 다른 종류가 된다 |
| 1 정본 이중화 | RUN-D2 | `variant` 가 JSON 키와 Set 이름 접미사에 이중 보관 | 두 값이 어긋나면 저장이 매번 이름 쪽으로 덮는다 |
| 1 정본 이중화 | RUN-D10 | 설계변수 값의 정본이 모델이 아니라 셀 위젯 (시그널 결선 없이 폴링) | 모델만 바꾸는 경로(RUN-D26)가 실제로 존재해 화면과 저장이 갈린다 |
| 1 정본 이중화 | RUN-D20 | NodeSet 판정 근거가 `Qt::UserRole` 과 이름 목록 2벌이고 후자는 미호출 | 콤보 텍스트만 세우는 경로에서 UserRole 이 비어 NodeSet 이 Part 로 취급된다 |
| 1 정본 이중화 | ANA-D6 | 색 값의 정본이 스타일시트 문자열이고 읽는 방식이 문자열 절단·정규식 2가지 | 정규식 쪽은 색 이름 표기를 매치하지 못해 같은 버튼을 두 경로가 다르게 읽는다 |
| 1 정본 이중화 | OPT-D22 | 피팅 결과가 DV 표 위젯에만 쓰이고 `m_designVariables` 에 도달하지 않음 | Run 없이 Set 을 전환하면 피팅 결과가 소멸한다 |
| 1 정본 이중화 | **OPT-D24** | 심볼의 표시분은 행 인덱스 재생성, 모델분은 JSON `symbol`, 복원 매칭은 응답 이름 | 응답이 추가·삭제되면 목적·구속 수식의 토큰이 사용자가 지목한 응답과 다른 것을 가리키고 화면에 표시가 없다 |
| 2 왕복 단절 | MOR-D6 | θ 는 방향 벡터로만 저장되고 표시값은 기즈모 Euler 의 역산 | 표시되는 θy/θz 가 사용자가 입력했던 값과 같다는 보장이 없다 |
| 2 왕복 단절 | MOR-D10 | `Morphing.constraints` 는 파서만 있고 writer 가 레포에 없다 | Constraints 모드 산출물이 세션을 넘기지 못한다 |
| 2 왕복 단절 | MOR-D11 | 대상 파트가 어느 저장 경로에도 기록되지 않음 | 재로드 후 설정 완료 Set 도 시작 페이지로 떨어지고 MOR-D2 와 연쇄한다 |
| 2 왕복 단절 | CAD-D10 | `meta.default` 에 현재값이 아니라 Lower 열 값이 들어감 | 원본 현재값이 DV JSON 에 전달되는 경로가 아예 없다 |
| 2 왕복 단절 | CAD-D11 | `Independent Parameter.Value` 저장은 `upper`, 로드는 "현재값" 으로 해석 | 데몬 JSON 만으로 채워진 행은 Lower = Upper = 현재값에서 출발한다 |
| 2 왕복 단절 | **CAD-D17** | Set ↔ `.prt` 결합이 어느 저장 경로에도 없다 (프로젝트 전역 1개) | 재로드 후 이 Set 의 대상 `.prt` 를 복원할 수단이 없고, 유일한 흔적인 configs 복사본은 CAD-D15 가 지운다 |
| 2 왕복 단절 | CON-D5 | Value 인라인 편집이 메모리 deck 만 바꾸고 설정 JSON 에 대응 키가 없다 | 모듈을 떠났다 돌아오면 편집이 사라지고 되돌리기 경로도 없다 |
| 2 왕복 단절 | CON-D10 | 대상 deck 이 전역 active context 1개뿐, Set 별 저장 필드가 없다 | 프로젝트를 재로드하면 사용자가 deck 을 다시 열어야 표가 채워진다 |
| 2 왕복 단절 | CON-D13 | ResultsAnalyzer 가 `paramObj["checked"]` 를 읽는데 그 키를 쓰는 코드가 없다 | 조건 DV 는 그 변수 목록에 절대 들어가지 않는다 (실제 키는 `boolean`) |
| 2 왕복 단절 | DOE-D2 | Probabilistic Min/Max 가 모델에 되쓰이지 않고 샘플링에만 전달 | 표의 편집값이 다음 진입 때 사라지고, 워커는 크기 가드 없이 위치 첨자로 읽는다 |
| 2 왕복 단절 | **DOE-D26** | 제약식은 설정 JSON 에 영속화되는데 그 토큰인 `v{n}` 은 행 인덱스에서 매번 재생성 | DV 행을 추가·삭제·재정렬하면 저장된 제약식이 다른 변수를 가리킨다 (OPT-D24 와 같은 기제) |
| 2 왕복 단절 | PRE-D7 | 설정 JSON 4섹션 중 `Dataset`·`Output Response` 를 읽는 코드가 없다 | Add·Remove 마다 파일 I/O 를 쓰고도 재진입 시 DOE·해석 타입·응답이 전부 초기화된다 |
| 2 왕복 단절 | PRE-D8 | KPI 행 추가만 `saveOutputResponseToJson` 을 부르지 않는다 | KPI 행은 표에만 존재해, 기록 경로의 유무가 행 종류마다 다르다 |
| 2 왕복 단절 | BLD-D4 | 라벨 키의 쓰기는 sanitize, 읽기는 원문 | 공백·`/`·`:` 가 든 라벨은 저장된 배치·체크·reduction 을 잃고 기본 규칙으로 떨어진다 |
| 2 왕복 단절 | BLD-D7 | 저장된 Response 는 sanitize 된 이름, 콤보 표시는 원문 기반 | `findText` 가 -1 을 돌려 Response 가 항상 0번 항목으로 남는다 |
| 2 왕복 단절 | BLD-D8 | Output `transformation` 은 쓰기만 되고 읽기에서 값이 버려진다 | 재진입 시 콤보가 항상 `None` 으로 되돌아간다 |
| 2 왕복 단절 | BLD-D12 | MCU 는 `Data Label.Dataset` 을 배열로 쓰는데 베이스 로더는 `toString()` | Input/Output 체크 소실 · XML 이식 누락 · 파일 표가 빈 표로 복귀 3연쇄 |
| 2 왕복 단절 | RUN-D24 | 두 번째 `updateModelUploadConfig` 가 첫 번째의 `Output Response` 를 덮음 | 실제로 돈 것은 ND 인데 계약 파일은 1D 를 가리킨다 |
| 2 왕복 단절 | RUN-D26 | `updateModelUploadConfig` 가 `model_info.json` 을 재파싱해 사용자 입력값을 기본값으로 덮음 | 외부 실행파일이 읽는 계약 파일이 화면과 다른 값을 담는다 |
| 2 왕복 단절 | RUN-D33 | 설정 JSON 의 `Prediction Cases`·`Output Response`·`Input Design Variables` 가 쓰기 전용 | 재진입 후 [Run AI Prediction] 이면 모든 행이 현재 dvTable 값 한 벌을 공유한다 |
| 2 왕복 단절 | RUN-D34 | `m_predictionCount` 가 세션을 넘기지 못하고 0 에서 재시작 | 재진입 후 Generate 가 기존 `Predict_01_*` 을 같은 이름으로 덮어쓴다 |
| 2 왕복 단절 | RUN-D35 | Morphing 생성은 `.vtu` 경로를 싣고 디스크 스캔은 `*.dat`·`*.inp` 를 집는다 | 재진입 뒤 같은 케이스의 행 경로가 바뀌고 열람이 동명 리다이렉트에 의존한다 |
| 2 왕복 단절 | ANA-D9 | 설정 JSON 의 `DOE Analysis`·`Data Analysis` 블록이 write-only | 매 Plot 이 축·색·스타일을 파일에 쓰지만 재기동 후 화면에 돌아오지 않는다 |
| 2 왕복 단절 | OPT-D5 | 최적화 모드 2차 판정이 1 로 올리기만 하고 0 으로 내리지 않는다 | 한 번 mean/std 가 기록되면 신뢰도기반으로 고정되고 UI 에 내릴 수단이 없다 |
| 2 왕복 단절 | OPT-D6 | Fixed 체크와 Init. Value 편집이 모델에 도달하지 않음 (시그널 미연결) | 두 값을 고치고 Run 없이 Set 을 전환하면 파일에도 모델에도 남지 않는다 |
| 2 왕복 단절 | OPT-D7 | Minimize/Maximize 콤보에 수신 슬롯이 없다 | 방향만 바꾸면 모델의 `direction` 이 낡은 값으로 남고 Run 시 강제 동기화로만 메워진다 |
| 2 왕복 단절 | OPT-D12 | `saveSettings()` 호출처가 `runOptimization` 하나 | 설정을 다듬고 Run 없이 나가면 전부 소멸한다 |
| 2 왕복 단절 | OPT-D21 | `m_activeModelBuilderFolder` 에 설정 JSON 왕복이 없다 | 앱을 다시 띄우면 사용자가 고른 학습 결과가 아닌 폴더로 되돌아갈 수 있다 |
| 3 조용한 실패 | MOR-D2 | geometry 부재 시 파트 검증 없이 렌더링 매니저의 base actor 로 대체 | VTP 에서 복원된 핸들 인덱스가 다른 파트 표면을 가리킬 수 있다 |
| 3 조용한 실패 | MOR-U1 | `MODE_PHYSICS` 가 `SetInteractionMode` 의 `switch` 에서 누락 | 툴바로 도달하는 살아 있는 모드인데 `default: break` 로 떨어져 픽킹 방식이 직전 모드에서 이월된다 |
| 3 조용한 실패 | CAD-D14 | NX 표현식 적용 실패가 ListingWindow 에만 기록되고 stdout 으로 안 나감 | 값이 반영되지 않은 STEP 이 성공으로 처리되고, DOE 배치는 전 케이스가 같은 형상을 낼 수 있다 |
| 3 조용한 실패 | CON-D12 | 조건 DV 주입 실패 3종이 전부 `continue` | 조건 DV 가 하나도 적용되지 않아도 기준값 그대로 export 되고 성공으로 집계된다 |
| 3 조용한 실패 | DOE-D12 | FE-safe 의 ODB 소스 판정이 파일 존재만 보고 워크플로 실행 여부를 안 본다 | 레퍼런스 표에 남아 있기만 하면 소스로 잡히고, 현재 DOE 의 것인지 검사하지 않는다 |
| 3 조용한 실패 | DOE-D15 | motion-launcher 가 `.dfr` 이 없으면 하드코딩 XML 7줄로 만들어 낸다 | 산출물 존재로 성공을 판정하는 하류가 실패를 성공으로 읽는다 |
| 3 조용한 실패 | DOE-D19 | condition DV 적용 실패 3경로가 warning 후 `continue`, 호출부가 결과 미검사 | 해당 필드만 레퍼런스 값으로 export 된 deck 이 성공한 실행으로 남는다 |
| 3 조용한 실패 | **DOE-D25** | 릴리스 빌드는 Resample 위젯을 생성하지 않는데 트리의 그 variant Set 은 남아 있다 | DEV 에서 만든 프로젝트를 릴리스로 열면 그 Set 클릭이 dock 을 직전 모듈 화면에 남기고 경고도 로그도 없다 |
| 3 조용한 실패 | PRE-D10 | 모든 run 이 비-Done 이면 `Done` 필터 결과를 버리고 원본 배열을 쓴다 | 실패한 run 전량이 배치 입력이 되고 XML 이 값 없는 샘플로 채워진다 |
| 3 조용한 실패 | PRE-U1 | `.op2` 가 확장자 목록·파일 대화상자 필터·솔버 목록에는 있고 라우팅 분기에 NASTRAN 이 없다 | UI 에 열어 둔 확장자가 경고 없이 `AnsysMechanical` 로 처리된다 (솔버 경로 입력 UI 는 주석 처리돼 있다) |
| 3 조용한 실패 | BLD-D14 | MCU 의 `stopTraining` 이 `virtual` 이 아니라 베이스 no-op 이 불린다 | [Stop] 이 데몬을 멈추지 못하고 아무 일도 하지 않는다 |
| 3 조용한 실패 | RUN-D14 | `SetBoxHandles` 가 렌더러 부재 시 데이터 없이 반환, 최종 가드는 "비어 있지 않은가" 뿐 | 직전 Set 의 핸들이 남아 있으면 `true` 를 돌려주고 그 핸들로 모핑이 돈다 |
| 3 조용한 실패 | RUN-D23 | `startPredictionJob` 의 거절 반환값을 호출부 3곳이 검사하지 않는다 | ND 와 1D 를 함께 실행하면 1D 가 모달 경고 없이 누락된다 |
| 3 조용한 실패 | RUN-D29 | 민감도 콤보가 다른 계층의 키를 기대하고 4단 중첩 `if` 에 로그가 없다 | 키가 없으면 플롯 패널의 변수 목록이 조용히 빈다 |
| 3 조용한 실패 | RUN-D30 | 민감도 폴더 열거에 Set 필터가 없다 | 다른 Set 의 학습 결과가 목록에 뜨고, 매치 실패 시 0번이 선택돼 무관한 Set 으로 플롯이 나간다 |
| 3 조용한 실패 | ANA-D3 | `applyReduction` 분기가 Max/Min/Mean 3종이고 나머지는 `reduceMax` 폴백 | `(std)` 를 고르면 표준편차가 아니라 최댓값이 그려진다 |
| 3 조용한 실패 | ANA-D10 | spec 조립 실패·command 미매치·조기 반환이 UI 에 아무 변화를 주지 않음 | [Plot] 을 눌러도 아무 일이 없는 상태가 세 계층에서 만들어진다 |
| 3 조용한 실패 | **ANA-D14** | 타깃 콤보 스캔이 Set 필터 없이 전량을 나열하고 항상 0번을 자동 선택 | 다른 Set 의 산출물이 콤보에 섞이고, 진입 직후 뜨는 것은 현재 Set 이 아니라 이름순 첫 Set 이다 (RUN-D30 이 그 ModelRunner 사례) |
| 3 조용한 실패 | OPT-D8 | [+] 가 심는 예시 구속이 회색 placeholder 가 아니라 보통 아이템이고 즉시 모델에 들어간다 | 편집하지 않으면 의도하지 않은 구속이 그대로 실행에 실린다 |
| 4 피드백 부재 | CAD-D1 | `.prt` 성공 경로에 로딩 스피너 정지 호출이 없다 (실패 경로에만 있음) | 로드가 성공하면 상태바가 "Loading …" 에 머문다 |
| 4 피드백 부재 | CAD-D9 | NX CAD 스피너가 비대칭 — 프리뷰 완료 경로에 대응하는 시작 호출이 없다 | 대화형 프리뷰는 진행 표시 없이 돌고 끝날 때만 완료 메시지가 뜬다 |
| 4 피드백 부재 | DOE-U2 | Direct Output Cases 표가 `setModel` 도 상태 시그널도 받지 않고 Status 를 `"Enqueued"` 로 고정 기입 | 실행 중에도 표가 움직이지 않아 진행 상황을 화면에서 알 수 없다 |
| 4 피드백 부재 | ANA-D12 | Save 메뉴 3종이 위젯 종류와 무관하게 뜨고 `dynamic_cast` 실패 시 무반응 | `DashExportable` 미구현 11종에서 메뉴가 아무 일도 하지 않는다 |
| 4 피드백 부재 | OPT-D11 | `optimizationFailed` 의 `connect` 가 레포 전체에 없다 | 외부 실행파일이 죽어도 위젯이 반응하지 않아, 사용자가 보는 실패 신호는 "아무 일도 안 일어남" 뿐이다 |
| 4 피드백 부재 | OPT-D13 | 중복 실행 방지가 모델의 `m_currentJob` 가드뿐이고 버튼은 열려 있다 | 로그 dock 이 닫혀 있으면 연타가 무시된 것인지 진행 중인지 화면으로 구분할 수 없다 |
| 5 공유 상태 오염 | CON-D6 | GUI 편집과 DOE 배치가 같은 RW 세션을 공유하는데 상호 배제가 없다 | 원복 실패 시 GUI 세션에 주입값이 남아 화면 표시와 이후 샘플 export 가 오염된다 |
| 5 공유 상태 오염 | DOE-D17 | 모핑 배치가 GUI 소유 싱글턴 핸들 인스턴스에 VTP 를 `DeepCopy` | DOE 를 한 번 돌리면 열려 있는 Set 의 핸들 배열이 그 Set 의 VTP 내용으로 교체된다 |
| 5 공유 상태 오염 | DOE-D18 | 배치가 GUI 와 공유된 해석 컨텍스트를 in-place 변이하고 원복 두 줄에 의존 | export·원복 중 하나만 실패해도 세션이 오염된 채 남는다 |
| 5 공유 상태 오염 | RUN-D13 | Generate 가 Geometry Parameterization 의 공용 핸들 인스턴스를 제자리 교체 | Model Runner 의 Generate 1회가 Morphing 탭이 편집 중이던 핸들 배열을 덮는다 |
| 5 공유 상태 오염 | ANA-D2 | 중복 억제 캐시가 함수-로컬 `static` 이고 키에 인스턴스가 없다 | 같은 ViewType 을 공유하는 ModelRunner Sim·MCU 두 인스턴스가 100ms 창을 공유한다 |
| 5 공유 상태 오염 | OPT-D18 | [Render Preview] 가 핸들 배열·렌더러 액터·전역 active context 3종을 갈아끼우고 복구 코드가 없다 | 프리뷰 1회 후 전역 활성 해석 모델이 원본이 아니라 `Preview_*.dat` 이 된다 |
| 6 통지 미결합 | CAD-D3 | 한 명령의 두 산출물(파라미터 JSON · STEP)이 다른 채널로 도착하고 합류점이 없다 | 표가 채워진 시점과 형상이 뜬 시점의 선후를 코드가 보장하지 않는다 |
| 6 통지 미결합 | CAD-D7 | 전송 계층은 `commandId` 를 갖지만 파사드의 `emitFailure` 에 경로 인자가 없다 | `loadPrtFailed` 하나가 load 실패와 대화형 update 실패를 겸용한다 |
| 6 통지 미결합 | CAD-D8 | 방출 대상이 요청 단위가 아니라 전역 `m_batchMode` 1비트로 스위칭 | 배치 진행 중 프리뷰 버튼을 누르면 그 완료도 배치 시그널로 나간다 |
| 6 통지 미결합 | DOE-D16 | `.dfsxml` 경로의 완료 판정 주체가 `finished` 람다와 stdout 감시 둘 | 판정 근거가 엇갈릴 때 어느 쪽이 남는지는 도착 순서로 정해진다 |
| 6 통지 미결합 | DOE-D21 | 종결이 키 집합 소진 집계와 `jobFinished` 직접 방출 두 갈래 | 경로마다 방출 조합이 달라 수신처 3곳이 종결을 여러 번 받는다 |
| 6 통지 미결합 | RUN-D15 | `enqueueUpdatePrtGeometry` 가 요청 식별자를 돌려주지 않고 짝짓기가 멤버 문자열 비교 | 다른 모듈이 배치 모드를 켠 채면 완료 통지가 오지 않고 행도 JSON 도 안 생긴다 |
| 6 통지 미결합 | OPT-D19 | 요청에 태그가 없고 완료 수신처가 `DashMainWindow` | Optimizer 위젯이 자기 요청의 완료를 알지 못하고, 부모 탐색도 조용히 실패한다 |
| 7 스레드 경계 | CON-D2 | `getOrLoad` 의 실제 로드가 뮤텍스 밖에서 돈다 | 같은 미캐시 deck 을 동시 요청하면 파싱이 두 번 돌고 하나가 버려진다 |
| 7 스레드 경계 | DOE-D4 | 워커가 GUI 소유 `QAbstractItemModel` 을 직접 읽는다 (결과 기록도 모델 포인터 경유) | `feat/rw-actor` 의 값 스냅샷 3심볼이 dev 에 전부 없다 |
| 7 스레드 경계 | DOE-D22 | 설정 JSON read-modify-write 8곳 중 뮤텍스를 지나는 것이 1곳이고 그마저 인스턴스 멤버 | 완료 콜백 두 건이 겹치면 전문 재기록끼리 덮어쓴다 |
| 8 암묵 계약 | MOR-D3 | Generate 분기가 타입 키가 아니라 7단 `isVisible()` 캐스케이드 | 페이지를 추가하면 캐스케이드 순서가 그대로 계약이 된다 |
| 8 암묵 계약 | CAD-U4 | 데몬 성공·실패 판정이 `[FINISHED]` 전체 일치와 `[ERROR]` 부분 일치 | 프로토콜 계약이 코드가 아니라 로그 포맷이고, `[ERROR]` 를 stdout 에 안 쓰는 실패는 성공으로 마감된다 (CAD-D14) |
| 8 암묵 계약 | CON-D1 | `setProjectDirectory` 가 인자를 쓰지 않고 경로를 다시 유도한다 | 호출 3곳이 서로 다른 값을 넘기며, 인자를 신뢰한 호출이 추가되면 조용히 무시된다 |
| 8 암묵 계약 | CON-D8 | DV 섹션 판정이 파일명에 `"Condition"` 이 포함되는지 | 매칭되지 않는 파일명은 경고 없이 `DV-Condition` 으로 기본 처리된다 |
| 8 암묵 계약 | DOE-D3 | Purpose 판정이 문장 완전일치이고 리터럴이 두 곳에 이중 정의 | 어긋나면 `else { return; }` — [Set] 을 눌러도 갱신도 경고도 없다 |
| 8 암묵 계약 | DOE-D8 | 표 행 ↔ 케이스 결합이 Case Name 열 표시 텍스트 파싱 (`UserRole` 없음) | 표시 규칙이 바뀌면 결합이 끊긴다 |
| 8 암묵 계약 | DOE-D24 | Direct Launcher 가 `analysisType` 을 빈 문자열로 넘겨 현재 Set 의 DOE JSON 을 연다 | 케이스 키가 사용자 파일명이라 맞을 이유가 없고, 안 맞으면 갱신 없이 전문 재기록만 된다 |
| 8 암묵 계약 | PRE-D4 | Modal 판정이 `contains("modal")` 이고 대상이 단일 파일 모드에서는 basename | 이름에 modal 이 든 파일 하나로 모듈 전체가 Modal 모드로 넘어간다 |
| 8 암묵 계약 | PRE-D5 | `isAnsysMotion` 플래그에 `hasFunctionExpression` 이 실린다 | 필드 이름과 실제 의미가 어긋난 채 계약이 성립해, 진짜 판정이 필요해지면 재사용할 수 없다 |
| 8 암묵 계약 | BLD-D2 | [Load] 의 위젯↔모델 계약이 `"dir\|file"` 구분자 문자열 | 경로에 구분자가 들어가면 조립이 깨진다 |
| 8 암묵 계약 | BLD-D3 | 차원 판정의 정본이 파싱 결과가 아니라 shape 문자열의 쉼표 개수 | 자동 분배·모델 목록·머리글 교체·특수 행 활성화가 모두 이 셈 하나에 걸린다 |
| 8 암묵 계약 | RUN-D11 | 스핀박스 상한을 `max - 0.0001` 로 깎고 미설정 판정을 `value != 0.0` 으로 한다 | 표시된 상한을 입력할 수 없고, 정확히 `0.0` 인 DV 는 매 진입마다 중앙값으로 대체된다 |
| 8 암묵 계약 | RUN-D12 | Part 콤보가 모핑 대상이 아니라 `_input_geometry.vtu` 추출 대상만 고른다 | 라벨(`Select Set / NodeSet`)과 실제 효과가 어긋난다 |
| 8 암묵 계약 | RUN-D18 | 템플릿 치환이 `QMap` 사전순 전역 텍스트 치환 | 이름이 다른 이름의 접두사면 결과가 순서에 달리고, 값이 유효숫자 6자리로 잘린다 |
| 8 암묵 계약 | RUN-D21 | 행 삭제 범위가 `completeBaseName()` 접두사 매칭 | `Predict_1` 이 `Predict_1x` 를 함께 잡고, RUN-D34 로 카운터가 리셋되면 충돌이 앞당겨진다 |
| 8 암묵 계약 | RUN-D37 | MCU 민감도가 이미 `-MCU` 로 끝나는 이름에 접미사를 다시 붙인다 | 대상 폴더를 찾지 못해 목록 0번이 선택된다 (RUN-D30 과 연쇄) |
| 8 암묵 계약 | ANA-D5 | 타깃 3콤보 등 5종이 `objectName` + `findChild` 문자열 계약 (25회) | 컴파일러가 검증하지 않는 이름이 ViewType 4갈래의 분기 조건을 겸한다 |
| 8 암묵 계약 | ANA-D11 | 랭킹 표를 반환 타입 밖의 숨은 자식으로 실어 보내고 `objectName` 으로 꺼낸다 | 결합 결과 표가 `outer` 의 형제가 되어 PNG 저장 대상에서 빠진다 |
| 8 암묵 계약 | OPT-D4 | 1D / ND 열 가시성이 첫 행 응답 이름의 `"(Field)"` 부분문자열로 정해진다 | 행마다 차원이 섞이면 나머지 행의 지표가 보이지 않는다 |
| 8 암묵 계약 | OPT-D14 | 검증 표 헤더 분류가 `startsWith("r")` + 두 번째 글자 숫자 규칙 | `r2_thickness` 같은 이름이 응답으로 오분류되고 그대로 프리뷰의 DV 열 선택까지 간다 |
| 8 암묵 계약 | OPT-D20 | 설정 JSON 이 실데이터가 아닌데 플롯의 실재 게이트로 쓰인다 | `optimum.json` 이 멀쩡해도 설정 JSON 이 없으면 플롯이 거부된다 |
| 9 위치·순서 결합 | **MOR-D14** | Geometry 카테고리는 트리 루트 1개에 모델 배열 2벌인데 Morphing 갈래만 행 인덱스로 조회 | `-CAD` Set 이 앞에 오면 뒤의 Morphing Set 이 `rowIndex >= size` 로 조기 반환돼 클릭해도 경고 없이 열리지 않는다 |
| 9 위치·순서 결합 | CAD-D6 | 정렬 방어가 이름 매칭 2 · 시각 행 인덱스 2 · 채우기 시점 캡처 1로 갈린다 | `sortItems` 개입 뒤 셋이 같은 행을 가리킨다는 보장이 없다 |
| 9 위치·순서 결합 | BLD-D5 | 설정값 왕복이 카탈로그 리스트 i번째와 `QFormLayout` i번째 `FieldRole` 의 짝 | 항목 순서를 바꾸거나 중간 삽입하면 값이 다른 키로 오간다 |
| 9 위치·순서 결합 | BLD-D10 | MCU 파일 행의 [...] 람다가 생성 시점 `row` 를 값 캡처 | 중간 행 삭제 후 [...] 가 어긋난 행에 경로를 쓴다 |
| 9 위치·순서 결합 | RUN-D8 | 소스 종류 판정이 `parameter` 딕셔너리 순회 중 첫 매치에서 `break` | 혼합 Set 에서는 키 순서가 소스 종류와 Reference 줄·Part 콤보 활성까지 정한다 |
| 9 위치·순서 결합 | RUN-D22 | `[Preview]` 만 람다 캡처된 `row` 를 쓴다 (`[X]` 는 매번 재계산) | 앞 행이 지워진 뒤 Preview 를 누르면 다른 케이스가 열린다 |
| 9 위치·순서 결합 | RUN-D25 | `m_lastPreviewedVtuPath` 를 루프 끝에서 한 번만 세운다 | 케이스가 여러 건이어도 자동 렌더는 마지막 1건뿐이다 |
| 9 위치·순서 결합 | ANA-D1 | `m_methodWidgets` 가 `QMap` 이라 Method 콤보가 키 알파벳 순 | 배열 순서를 계약으로 적어 둔 주석과 실제 표시가 불일치한다 |
| 9 위치·순서 결합 | OPT-D15 | 프리뷰가 `templateFileName` 필터를 무시하고 configs 의 deck 전량을 순회 | 템플릿이 N 개면 모핑이 N 회 돌고 마지막 하나만 화면에 뜬다 |
| 10 규칙 중복 | DOE-D6 | Geometry/Condition 판별을 세 곳이 대소문자 구분·무시·정규식으로 각자 구현 | 파일명 접두나 대소문자가 바뀌면 세 지점의 판정이 갈린다 |
| 10 규칙 중복 | DOE-D10 | 말단 6경로가 착수·상태보고·종결을 각자 구현 | 공통 계약이 코드로 강제되지 않아 경로 추가 시 정답 조합을 코드가 말해 주지 않는다 |
| 10 규칙 중복 | DOE-D13 | 경로 조립기 두 개의 일치를 경고-후-덮어쓰기 한 줄이 강제 | 그 한 줄이 빠지면 모핑 산출물과 제출 경로가 다른 디렉터리를 가리킨다 |
| 10 규칙 중복 | PRE-D11 | KPI 5종이 배치 입력 로딩(스냅샷-또는-합성) 블록을 각자 복제 | 스냅샷 스키마가 바뀌면 고칠 지점이 6곳이다 |
| 10 규칙 중복 | BLD-D9 | Sim / MCU 쌍둥이 경로의 계약이 6곳에서 어긋난다 | status 문자열·저장 위치·산출 루트·`Dataset` 형·쓰는 계층·탭 활성 조건이 전부 다르다 |
| 10 규칙 중복 | RUN-D6 | ND 판정이 응답 이름 부분문자열과 모델 이름 접두사 화이트리스트 2벌 | 한쪽만 ND 로 판정되면 화면의 열과 실제 예측 경로가 어긋난다 |
| 10 규칙 중복 | RUN-D9 | `Source` 열 라벨이 같은 JSON 을 다시 열어 별개로 판정하고 실패 3경로가 한 값 | 판정 실패와 실제 ConditionParameter 가 화면에서 구분되지 않는다 |
| 10 규칙 중복 | RUN-D19 | 정규화 config 파싱 실패의 처리가 경로마다 다르다 | 경고가 Morphing 경로에만 있어 CAD·ConditionParameter 는 부호 보정 실패를 알리지 않는다 |
| 10 규칙 중복 | ANA-D8 | `methodKey` 매핑 5줄이 세 파일에 각각 존재 | command 를 추가하면 세 곳을 함께 고쳐야 한다 |
| 10 규칙 중복 | **ANA-D15** | `m_setName` 이 비면 `"Set1"` 로 대체하는 폴백 삼항이 7회 복제 | 호스트가 Set 을 주입하기 전 어느 경로든 밟히면 무관한 `Set1` 의 산출물을 경고 없이 읽는다 |
| 10 규칙 중복 | OPT-D1 | 같은 `model_info.json` 을 두 로더가 읽고 NaN 정화 수준이 다르다 | Python 이 NaN 을 쓴 파일은 한쪽에서만 조용히 빈 문서로 떨어진다 |
| 11 수명·정리 누락 | MOR-D12 | 명시적 리셋이 Set 이 바뀔 때만 돌고 `appendConstraintTable` 은 무조건 `insertRow` | N 회 재진입이면 구속 행이 N 배가 되어 그대로 `vtkExtractSelection` 에 투입된다 |
| 11 수명·정리 누락 | CAD-D13 | Set 삭제 시 위젯이 `mModel` 을 정리하지 않고 직후 `deleteLater()` 가 걸린다 | 살아 있는 `QFileSystemWatcher` 가 죽은 모델을 역참조할 수 있다 |
| 11 수명·정리 누락 | CAD-D15 | `loadPrt` 의 temp 정리가 승격이 복사해 둔 `.prt` 보관본과 같은 경로를 지운다 | 승격 후 같은 `.prt` 를 다시 Load 하면 0.5초 뒤 DOE 재현용 보관본이 사라진다 |
| 11 수명·정리 누락 | CAD-D16 | GUI 가 `--no-cleanup` 을 항상 붙이고 일괄 정리는 `.stp` 만 글로빙 | 프리뷰 1회마다 temp `.prt` 가 하나씩 남고 지우는 경로가 없다 |
| 11 수명·정리 누락 | CON-D3 | `m_params` 가 한 번도 clear 되지 않는다 | 어떤 deck 의 행이 표에 남아 있는지는 `source` 열로만 구분된다 |
| 11 수명·정리 누락 | DOE-D23 | `cancelAllRuns` 가 진행 중 프로세스만 죽이고 motion 큐를 비우지 않는다 | 취소 후 잔여 큐가 이어서 돈다 |
| 11 수명·정리 누락 | PRE-D1 | `setModel` 에 Output Response 표 초기화가 없다 | 이전 Set 의 행이 새 Set 의 요청으로 만들어진다 |
| 11 수명·정리 누락 | PRE-D2 | `onAnalysisFileSelected` 의 조기 반환 4곳이 `endProcessing()` 을 건너뛴다 | `m_loadingDepth` 가 0 으로 안 돌아와 인디케이터가 남고 이후 emit 도 막힌다 |
| 11 수명·정리 누락 | PRE-D6 | 배치 후 DLL 상태 복원 블록이 5곳에 있고 일반 배치·Modal KPI·조회 경로에는 없다 | 일반 Process 뒤의 선택은 마지막 run 파일 하나 위에서 질의하고, 증상이 조작 순서로 갈린다 |
| 11 수명·정리 누락 | BLD-D6 | [Delete] 가 `model_info.json` 과 디스크만 지우고 설정 JSON 항목을 남긴다 | 지운 모델이 `status:"Done"` 인 채 다음 [Start] 에서 되살아나 외부 도구에 넘어간다 |
| 11 수명·정리 누락 | BLD-D15 | MCU 위젯이 버튼 잠금을 되돌리지 않고 성공·실패 시그널도 연결하지 않는다 | 학습이 정상 종료해도 Start 버튼이 잠긴 채 남는다 |
| 11 수명·정리 누락 | RUN-D4 | 공용 데몬 수명이 Set 전환에만 묶이고 모듈 이탈에는 안 묶인다 | Set 전환 1회 = 공용 데몬 재기동 1회 + 결과 캐시 폐기, 이탈 시엔 데몬이 남는다 |
| 11 수명·정리 누락 | RUN-D16 | `m_pendingCadStpPath` 가 완료 슬롯 진입 직후에만 지워진다 | 생성 실패 시 이전 대기 경로가 남아 흘러간 요청이 되살아날 수 있다 |
| 11 수명·정리 누락 | RUN-D17 | CAD 완료 처리가 파일 표를 통째로 재구축한다 | 요청과 완료 사이에 손으로 넣은 체크와 `m_fileTableDvValues` 전량이 사라진다 |
| 11 수명·정리 누락 | RUN-D31 | 민감도 캐시 키에 모델 내용이 없고 캐시를 비우는 곳이 2곳뿐 | 같은 경로에서 모델이 재학습되면 캐시가 낡은 결과를 낸다 |
| 11 수명·정리 누락 | RUN-D32 | 민감도 실패 4경로가 `m_pendingCommand` 를 지우지 않는다 | 공용 데몬 브로드캐스트 구조에서 다음 응답이 이 러너의 것으로 오인 수신될 수 있다 |
| 11 수명·정리 누락 | RUN-D36 | `clearAllTables` 가 `m_predictionCount`·`m_pendingCadStpPath`·`m_pendingCadParams` 를 남긴다 | 진행 중이던 CAD 요청의 완료가 새 Set 의 표에 이전 Set 의 DV 값으로 행을 만든다 |
| 11 수명·정리 누락 | OPT-D2 | Set 삭제 후 `setModel(nullptr)` 이 표 내용과 `setEnabled(true)` 를 그대로 둔다 | 삭제된 Set 의 값이 화면에 남고 그 상태로 Run 이 눌리면 조용히 반환된다 |
| 11 수명·정리 누락 | OPT-D3 | 폴더 변경 슬롯이 두 표만 재구성하고 `populateOptimizationSettings` 를 안 부른다 | 응답 심볼이 바뀌어도 수식 문자열이 직전 폴더의 것으로 남고 드러나지 않는다 |
| 12 순서 의존 | MOR-D1 | 초기화 체인 전체가 `dataLoaded` emit 에 걸려 있고 화면 전환이 먼저 일어난다 | 설정 JSON 이 없는 신규 Set 은 화면이 뜬 채 초기화 전량이 건너뛰어진다 |
| 12 순서 의존 | CAD-D4 | `loadFromJson` 복원 직후 캐시 재적용이 전 행을 `isChecked = false` 로 재구성 | `.prt` 를 한 번이라도 로드한 세션에서 저장된 체크가 사라지고 승격이 풀린다 |
| 12 순서 의존 | CON-D7 | `loadFromJson` 이 행을 만드는 `refreshFromLoadedAnalysis` 보다 먼저 돈다 | 세션 최초 진입에서 FE 탭 체크가 전부 해제돼 보이고, 그 상태의 [Set Design Variable] 이 절을 빈 객체로 덮는다 |
| 12 순서 의존 | DOE-D1 | `loadSettings` 가 진입 1회에 3번 호출되고 앞 둘은 시그널 연결 전 | 같은 파일을 3번 읽고 2번은 버린다. 연결 시점이 바뀌면 세 호출의 의미가 함께 바뀐다 |
| 12 순서 의존 | BLD-D11 | 헤더 검증의 기준 파일 출처가 넷이고 전부 조작 순서에 종속 | 같은 파일 집합이라도 지정 순서에 따라 통과·실패가 갈린다 |
| 12 순서 의존 | **RUN-D38** | Set 불일치 시 표를 비우는 방어에 `!currentSetName.isEmpty()` 예외가 붙어 있다 | Set 이름이 아직 비어 있는 최초 진입에서 방어가 돌지 않아 이전 표가 남고 Generate 가 섞인 입력을 만든다 |
| 12 순서 의존 | OPT-D10 | 방법 선택마다 옵션 칸에 기본값을 주입하고, 저장값 복원은 그 직후 덮어쓰는 순서로만 성립 | 방법을 바꿨다 되돌리면 편집값이 기본값으로 돌아가고, 호출 순서가 바뀌면 복원이 깨진다 |
| 13 동기 실행·재진입 | MOR-D7 | 프리뷰 모핑이 GUI 스레드 동기 실행 | 프리뷰 중 스핀박스·기즈모 입력 1회마다 모핑 1회가 돈다 |
| 13 동기 실행·재진입 | MOR-D8 | `processEvents` 가 모핑 루프 안 2곳 | 볼륨 모핑 2회가 도는 사이 사용자 입력이 재진입한다 |
| 13 동기 실행·재진입 | CAD-D2 | `.prt` 진입 초입의 `processEvents` 가 큐된 슬롯·타이머를 실행 | 데몬 stdout 처리가 재진입해 모델을 갈아엎을 수 있다 |
| 13 동기 실행·재진입 | CON-D9 | 자기 쓰기 억제 플래그를 되돌린 다음 줄의 모달이 중첩 이벤트 루프를 돈다 | 방금 쓴 파일의 `fileChanged` 가 그 안에서 배달돼 리로드가 한 번 더 유발된다 |
| 13 동기 실행·재진입 | CON-D11 | `get_symbol_detail` 이 캐시되지 않는다 | 표 1회 구축에 조건당 최소 3회의 RW 왕복이 발생한다 |
| 13 동기 실행·재진입 | DOE-D7 | 케이스 상태 1건마다 JSON 전문 재기록 → 워처가 표를 전량 재구축 | N 케이스 실행이면 표 전면 재구축 N 회 |
| 13 동기 실행·재진입 | DOE-D9 | `runDoeAsync` 가 이름과 달리 동기 — `generateInputCases` 738줄이 GUI 스레드 | 워커로 나가는 것은 [Run] 의 샘플링뿐이고 모핑·파일 생성·프로세스 대기는 전부 동기다 |
| 13 동기 실행·재진입 | DOE-D11 | `processEvents` 16곳이 동기 대기의 대체물 (전량 `DashJobRunner.cpp`) | 재진입 차단이 2곳뿐이라 [Start] 재클릭·탭 전환·`setModel` 재진입이 실행 중에 들어온다 |
| 13 동기 실행·재진입 | PRE-D3 | 전용 워커·직렬 풀·게이트 0건이고 `processEvents` 25곳이 응답성을 대신한다 | 스캔·질의·배치가 도는 동안 이벤트 루프가 열려 사용자 입력이 재진입한다 (PRE-D9 와 연쇄) |
| 13 동기 실행·재진입 | PRE-D9 | KPI 경로가 `m_isProcessing = true` 보다 앞에서 반환해 재진입 가드 밖에 있다 | KPI 배치 중 Add/Remove/Preview 가 그대로 재진입한다 |
| 13 동기 실행·재진입 | RUN-D5 | 모델 적재 전 구간이 GUI 스레드 직렬이고 같은 파일을 계층마다 다시 읽는다 | `QThread` 0곳·`processEvents` 0곳이라 1\~20초 프리즈 구간에 진행 표시조차 없다 |
| 13 동기 실행·재진입 | ANA-D4 | XML 변수 스캔이 매번 문서 전체를 GUI 스레드에서 파싱하고 폴백 경로는 결과가 다르다 | 같은 파일이라도 파서 성공 여부에 따라 리덕션 항목이 나타나거나 사라진다 |
| 13 동기 실행·재진입 | ANA-D13 | 스핀박스가 스타일 setter 와 디바운스 재플롯 양쪽에 연결돼 있다 | 값 하나를 바꾸면 스타일 반영 후 200ms 뒤 전체 재플롯(파일 재파싱 또는 데몬 왕복)이 한 번 더 돈다 |
| 13 동기 실행·재진입 | OPT-D16 | 프리뷰 모핑이 GUI 스레드 동기이고 이 모듈 `processEvents` 2곳이 모두 그 루프 안 | 정합성이 원복 두 줄에만 기대고, 실패 시 공유 세션이 오염된 채 남는다 |
| 13 동기 실행·재진입 | OPT-D17 | `performMorphing` 이 만든 `.vtu` 2종을 호출부가 곧바로 지운다 | 두 번의 디스크 왕복이 산출물 없이 끝난다 |
| 14 고정 지연·폴링 | DOE-D14 | `msleep(1000)` 이 이미 끝난 동기 호출 뒤에 있다 | 실행 순서와 주석이 어긋난, 케이스 수와 무관한 고정 지연이다 |
| 14 고정 지연·폴링 | BLD-D13 | MCU 가 쓰지 않는 1Hz 상태 폴링 타이머를 켠 채 두고 멈추는 경로도 안 탄다 | 슬롯이 매번 즉시 반환하는 타이머가 계속 돈다 |
| 14 고정 지연·폴링 | RUN-D3 | `daemonReady` 유실 보정이 3벌 중복이고 폴링이 실효 경로 | 신호 계약이 아니라 현재 상태 재조회가 실제 동작이다 |
| 14 고정 지연·폴링 | RUN-D27 | 1D 결과 대기가 고정 500ms 뒤 `lastModified` 최대 CSV 선택 | 쓰기가 더 걸리면 이번 결과를 놓치고 다음 예측에서 이전 파일이 최신으로 잡힌다 |
| 15 죽은 코드 | MOR-U2 | 툴바 Prev/Next 가 emit 만 하고 수신처가 없다 | `onEditUndo/onEditRedo` 의 TODO 와 짝 — 버튼은 눌리는데 아무 일도 없다 |
| 15 죽은 코드 | CAD-D5 | Set 진입마다 도는 해석 덱 유입 경로의 결과를 읽는 곳이 0 | 매 진입의 레지스트리 로드가 아무 산출도 내지 않고 실패해도 `qWarning` 뿐이다 |
| 15 죽은 코드 | CAD-U3 | 도달하지 않는 선언·정의 — `saveSettings` no-op · `getContext`/`getLoadedFilePath` · `setModel` 오버로드 · `enum class JobType` | 앞의 셋이 CAD-D5 가 말하는 "결과를 읽는 쪽이 없는" 그 지점이고, `JobType` 은 주석이 `commandId` 로 대체됐다고 적어 둠 |
| 15 죽은 코드 | CON-U1 | `setModel` 오버로드의 유일한 호출 인자가 항상 `nullptr` | `dataChanged`·`dataLoaded` 를 거는 유일한 지점이 건너뛰어져 수신처가 0곳이다 |
| 15 죽은 코드 | CON-U3 | 디렉토리 워처의 `directoryChanged` 연결이 레포 전체 0곳 | `onDvJsonChanged` 의 `else` 분기와 `onDirChanged` 가 도달 불가다 |
| 15 죽은 코드 | DOE-U3 | `visibleParamIndices` 가 계산되지만 표는 4열 고정이라 반영될 열이 없다 | 하나도 안 맞으면 전 인덱스를 다시 넣는 폴백까지 있다 |
| 15 죽은 코드 | DOE-U4 | 호출부가 0인 함수 8종 (`createRunsFolders` 2종 · `getStatusFromFileSystem` 53줄 등) | `applySmartSelectionRules` 는 플래그를 세웠다 즉시 내리는 빈 스텁 |
| 15 죽은 코드 | DOE-U5 | 도달하지 않는 연결·계산 3종 (`connLog` 빈 람다 · `.ui` 콤보 2항목 · `firstPartName`) | 전부 생성 직후 덮이거나 읽히지 않는다 |
| 15 죽은 코드 | PRE-U2 | `initializePreprocessor` 의 `res`·`dfsxml` 분기가 도달하지 않는다 | 스캐너가 등록하는 Motion 결과 확장자는 `.dfr` 하나이고 `.dfsxml` 은 입력 소속이다 |
| 15 죽은 코드 | PRE-U3 | `m_dynamicTables` 는 채우고 비우기만 하고 읽는 코드가 없다 | 같은 `type` 그룹이 둘 이상이면 마지막 표만 남는데 남아도 쓰이지 않는다 |
| 15 죽은 코드 | BLD-U1 | 죽은 코드가 세 층에 남아 있다 (헬퍼 8개 중 실사용 4개 · `m_datasetFiles` 스캔 38줄 등) | `m_datasetFiles` 를 채우는 스캔은 Set 선택마다 실행된다 |
| 15 죽은 코드 | BLD-U3 | `parseDataLabelSection`·`parseConfigurationSection` 의 호출처가 0 | 깨진 왕복 3종(BLD-D4·D8·D12)의 읽기 측 구현이 존재한 채 연결만 빠져 있다 |
| 15 죽은 코드 | RUN-D7 | `configsDir` 이 양쪽 컨텍스트에 Set 무관 전역 경로로 들어가 삼항 폴백이 무의미 | 나머지 4곳의 삼항과 형태만 같고 효과가 없다 |
| 15 죽은 코드 | RUN-U1 | `syncFileTableToJson` 이 주석뿐인 빈 본문인데 3곳에서 호출된다 | 체크 상태가 메모리에만 있고 재진입에서 소실된다 (RUN-D33) |
| 15 죽은 코드 | RUN-U2 | 체크 행 일괄 삭제 39줄이 구현돼 있으나 `connect` 0건이고 버튼도 없다 | 행 삭제는 행별 `[X]` 하나뿐이다 |
| 15 죽은 코드 | RUN-U3 | `params.fileTableFiles` 와 그 유일한 소비 함수가 도달 불가 | 두 목록의 필터가 다른데 그 불일치를 소비할 함수의 호출처가 0곳이다 |
| 15 죽은 코드 | RUN-U4 | 구버전 CLI 형태(출력 디렉터리 인자 없음)의 예측 슬롯이 남아 있다 | 호출처 0곳이고 현행 두 경로와 인자 개수가 다르다 |
| 15 죽은 코드 | RUN-U5 | 도메인 신호 4종의 수신처가 0곳 | 모델→뷰 갱신이 신호가 아니라 `dataLoaded` 재사용 + 플래그로 좁혀진다 |
| 15 죽은 코드 | RUN-U6 | 도달하지 않는 정의 18종 | `runFESolver` 는 런처 DLL 을 직접 열고 모델 계층에서 `QMessageBox` 를 4회 띄운다 |
| 15 죽은 코드 | ANA-D7 | 타입 핸들 `textStyleGroup` 에 9곳이 대입하고 읽는 코드는 0건 | 위젯은 `findChild` 13회 + 도달 불가한 폴백 캐스케이드를 쓴다 (Method 분기마다 복제) |
| 15 죽은 코드 | ANA-U1 | `onTargetDataChanged` 의 모듈 판별 4갈래가 도달 불가 | 타깃 콤보를 채우는 코드가 `AnalysisLauncher_*.json` 만 나열한다 |
| 15 죽은 코드 | ANA-U2 | `settings.parallel.save_json_path` 를 읽는 코드가 레포 전체 0건 | 기록만 되고 소비되지 않는다 |
| 15 죽은 코드 | ANA-U3 | `DashDoeConfigManager::updateConfigFile` 55줄의 호출처가 0건 | `methodKey` 매핑을 담은 세 번째 사본이다 |
| 15 죽은 코드 | ANA-U5 | 호출부 없는 진입점 4개 (약 106·110·111·16줄) | 앞 3개는 헤더 선언까지 있고 `ViewSpec` 어디에도 등록돼 있지 않다 |
| 15 죽은 코드 | OPT-U2 | 도달하지 않는 선언 4종 | `predictBtn` 은 `.ui` 에도 없고 초기화 목록에도 없는 **초기화되지 않은 포인터 멤버** |
| 16 검증 부재 | CAD-U5 | `tests/` 전체에 `NxCad`·`GeometryParameter` 참조 0건 | CAD 파사드의 분기 · 배치 오케스트레이션 · DV 승격 왕복이 덮여 있지 않다 |
| 16 검증 부재 | CON-U5 | `tests/` 전체에 RW 관련 5심볼 참조 0건 | 액터 마샬링·엔트리 분해·dvKey 채번·DOE 주입·원복이 전부 미검증이다 |
| 16 검증 부재 | OPT-U3 | `tests/` 전체에 Optimizer 참조 0건 | 설정 JSON 왕복·헤더 분류 규칙·프리뷰 분기가 전부 자동 검증 밖이다 |
| 17 구조 잔여 | MOR-D4 | `DashHandlePickingInteraction` 3,121줄이 픽킹·기즈모·핸들 데이터·구속 오버레이 4역 | 도메인 타입 없이 polydata 배열 11종이 사실상 모델 노릇을 한다 (헤더 TODO 가 분리를 적어 둠) |
| 17 구조 잔여 | MOR-D13 | 컨트롤러가 뷰 포인터를 무가드로 역참조하는 곳 6군데 | 한 지점은 같은 포인터의 널 가드가 사용보다 뒤에 온다 |
| 17 구조 잔여 | PRE-D12 | `DashDataProcessor.cpp` 4,671줄이 스캔·질의·XML·KPI 4역 (코드베이스 단일 최대) | 고객사 KPI 전용 5함수가 1,625줄 — 파일의 35%. 빌드 가드는 3파일 9블록에 흩어져 있다 |
| 17 구조 잔여 | RUN-D28 | 뷰가 `DashMainWindow` 를 부모 거슬러 4벌로 찾는다 | 같은 파일의 `findChild` 5회 · 뷰에서 직접 띄우는 `QMessageBox` 15회와 함께 반복된다 |
| 17 구조 잔여 | OPT-D9 | `[popOS]` 디버그 `qDebug` 27줄과 `showEvent` 7줄이 빌드 가드 없이 남아 있다 | 릴리스에 그대로 들어간다 |
| 17 구조 잔여 | OPT-D23 | 피팅의 학습 모델 경로가 `ModelBuilder_LGE_Spring_Fitting` 하드코딩 | 폴더 이름이 다르면 도달할 방법이 없다 |

---
