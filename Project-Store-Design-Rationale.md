# 결함 축 대응과 읽기 배선 — 현재 책임에 맞춘 설계 근거

> **2026-10-08 개정 반영.** [이슈 개정 이력](Issue-Revision-History.md)의 반영된 결정을 본문에 적용했다. 추가 개정 계획과 미정 계약은 제안으로 구분한다.

이 문서는 [계층과 배치](Project-Store-Design-Layer-Cut.md)의 근거다. 원래 조사의 좌표·수치와 현재 적용할 해결 경계를 구분한다. 과거 실측은 주로 `dev` @ `4c7608e` 기준이며 현재 코드 전수 재검증 결과가 아니다.

## 적용 기준과 책임

Set 신원의 원본은 기존 Set JSON의 `setId`다. #520에서 마련한 발급·영속·복원·역조회를 사용하고, 새 `inst_` ID나 이름 기반 v5 Set ID로 바꾸지 않는다. 프로젝트 객체의 색인은 Set 기록에서 얻는 조회용 정보다. 별도 Set 원장과 산출물·소비 이력 대장은 만들지 않는다(#443·#471).

| 정보 | 원본과 책임 | 담당 |
|---|---|---|
| 현재 선택한 상류 Set | 소비 Set 설정에 개별 `setId`와 세부 선택 저장 | #368 → #685 |
| 산출물 생성 당시 출처 | 실제 사용한 Set·입력 선택·deck 정보를 산출물에 저장 | #368 공통 기록·판독 계약, #685 소비 |
| 산출물 버전 | 생산 Set이 기록. 의미와 발급·비교 규칙은 별도 확정 | #650 |
| 최신성 | 소비 Set이 실제 사용한 입력 버전으로 판정 | #650 |
| 조회·집계·표시 | 프로젝트가 Set·의존관계를 조회하고 개별 판정을 호출·집계, VM이 표시·동작 전달 | 구체 API는 미정 |

현재 Set의 `setId`를 유지하면서 상류 입력을 다른 `setId`의 Set으로 바꿀 수 있다. 선택만 바꾸면 기존 산출물의 출처는 바뀌지 않는다. 재실행으로 산출물을 덮어쓸 때 실제 출처도 함께 갱신하며, 이전 산출물과 출처의 전체 이력 보존은 요구하지 않는다. `parameterizationId`와 최초 입력 영구 고정은 폐기됐다.

필수 출처가 없는 구산출물은 재생성이 필요하다. 이름·경로·현재 선택으로 과거 출처를 추론하거나 자동 이관하지 않는다. 이 정책은 기존 Set ID 발급·복원을 중단하거나 구프로젝트 전체의 열기를 거부한다는 뜻이 아니다.

## 1. 파일 표현과 책임

| 당시 미기록·혼재 데이터 | 현재 검토할 저장·해결 위치 |
|---|---|
| 케이스 실패 사유·스테이지 상태 | #441·#444의 상태 기록·복구. 실제 비용 확인 후 필요한 저장 경계 결정 |
| 프로젝트·Set 신원 | #520 Set JSON의 `setId`와 프로젝트 조회색인. 새 원장 불요 |
| 기준 해석 파일·활성 컨텍스트 | 기존 identity·registry와 Set 입력 선택의 연결. 화면 커서와 분리 |
| 상위 선택 | 소비 Set 설정에 현재 참조·세부 선택, 읽기 배선 추가 |
| 생성 당시 출처 | 산출물 내부 #368 공통 기록·판독 계약 |
| 실행·소비 이력 | 별도 대장 취소. 전체 이력 보존 요구 없음 |
| Condition Value | 모듈이 소유할 편집 기록. 구체 오버레이 형식은 별도 검토 |
| 예측 번호·파일 충돌 | #475의 기존 결과 보존. 전역 카운터 구축이 목표 아님 |

## 2. 읽기 배선 15건 — 과거 관찰과 현재 대응

현황 열은 선행 조사 당시의 관찰이다. 저장 자리가 있어도 복원·조회 리더가 연결되지 않으면 결함이 해결되지 않는다는 근거를 유지한다. 괄호의 결함 ID는 원래 조사 좌표다.

| # | 대상·당시 관찰 | 현재 대응과 범위 |
|---|---|---|
| 1 | DataPreprocessor `Selected DV-Table`·`Selected Analysis File` 리더 0곳 (PRE-D7) | 모듈 선택 복원. 파일 처리 위치와 확정 출처 Set 관계를 구분 |
| 2 | Runner·Optimizer Builder 선택 미기록, 첫 폴더·관례 추정 (RUN-D8·OPT-D21) | #685에서 `setId` 저장·복원, 산출물 출처 검증 |
| 3 | ResultsAnalyzer 축·색·스타일 write-only (ANA-D9) | 기존 뷰 설정 복원. 별도 `view.json` 신설은 필수 아님 |
| 4 | Runner 예측 3섹션 write-only (RUN-D33) | 기존 Set 설정 로더 배선 |
| 5 | 예측 카운터 메모리 전용, 재시작 0 (RUN-D34) | #475 기존 결과 보존·파일 충돌 확인. 실행 대장 불요 |
| 6 | 모핑 대상 part 저장 경로 없음 (MOR-D11) | 현재 입력·part 선택 저장. 실제 산출 출처와 구분 |
| 7 | 핸들 이름은 트리 텍스트·세션 QMap (MOR-D5) | 소유 모델의 설정/벌크 기록을 검토 |
| 8 | Morphing constraints 파서만 있고 라이터 없음 (MOR-D10) | 모듈 저장 배선의 개별 결함 |
| 9 | Condition deck은 전역 active context (CON-D10) | Set의 입력 선택으로 해석, registry 유지 |
| 10 | Builder transformation을 로더 2벌 중 하나가 버림 (BLD-D8) | 기존 로더 정합화 |
| 11 | parseDataLabelSection·parseConfigurationSection 호출 0 (BLD-U3) | 기존 설정 로드에 연결 |
| 12 | MCU Dataset 배열을 `.toString()`으로 읽어 빈 값 | 배열 판독 계약·호출 경로 정합화 |
| 13 | CAD 체크 복원 후 캐시가 false로 덮음 (CAD-D4) | 복원·캐시 적용 순서 수정 |
| 14 | 활성 해석 모델 경로 미직렬화 (PDM 5-2) | 데이터 선택은 Set, 렌더 활성은 세션 상태 |
| 15 | 산출 경로를 스캔, 생성·스캔 규칙 어긋남 (RUN-D35·ANA-U1) | #477 기존 기록·파일 소속·재열기 해석 일치. 공통 출처 소비는 #685 |

`Selected Analysis File`은 이름과 달리 해석 타입으로 쓰이던 경로도 있다(`DashDataProcessor.cpp:1224`). 이름만 보고 새 Set 참조 필드로 옮기지 않는다. 자세한 원 관찰은 [키 I/O 조사](Project-Store-Survey-Key-IO-Ledger.md)를 따른다.

## 3. 결함 축 A~G와의 대응

69건은 당시 분류 수다. 아래 대응은 해결 책임이며 완료 판정이나 현존 건수 재집계가 아니다.

| 축 | 당시 건수 | 현재 대응 |
|---|---|---|
| A 기준 모델·상위 선택 미기록 | 12 | Set 선택 저장·리더 연결, 산출물 출처 분리 |
| B 파일명·경로가 스키마 역할 | 11 | Set 연결은 기존 ID, 위치는 프로젝트 조회. 항목·경로 문제는 별도 |
| C variant 휴리스틱 분산 | 6 | 기존 Set 기록과 판독 경로 정합화. 새 원장 단일화 요구 아님 |
| D 키·형·저장 자리 불일치 | 15 | 해당 기록 소유자의 계약·로더·라이터 수정 |
| E 자산·부산물·실패 구별 부족 | 8 | #473의 구체 항목 조작과 #441 상태 기록. 별도 산출물 대장 취소 |
| F Set 신원·수명·범위 불명확 | 11 | #520 신원 활용, 참조·삭제·재생성 경계 검증 |
| G 설정 쓰기 주체·시점 불명확 | 6 | #441·#444와 모듈별 라이터 조정. 전면 도구 교체 필수 아님 |

저장 설계만으로 결함이 자동으로 닫히지는 않는다. 과거에는 41건을 스키마 결정 연관, 28건을 동반 축 필요로 나눴다. 동반 축은 소유 경계 12건(뷰가 원본), 실행 모델 9건(워커·배치), 요청↔완료 7건(외부 데몬·DLL)이었다. 이 분류를 현재 모든 오류 수정의 대형 스키마 선행 조건으로 사용하지 않는다.

`startsWith("r")`·숫자·쉼표 수·`contains("modal")` 같은 판정 규칙 18건도 저장 위치만으로 해결되지 않는 별도 문제다.

## 진행 순서와 독립 작업

1. #520의 기존 `setId` 발급·복원·역조회와 개명·동명 재생성 동작을 기반으로 사용한다.
2. #368에서 생산 측 출처 기록과 공통 판독·검증 계약을 구현한다. 완료 경계는 Builder의 `model_info.json` 생성이다.
3. #685에서 Runner·Optimizer의 Builder 선택 저장·복원, 출처 검증, 실행·조회·프리뷰를 연결한다. 외부 실행에는 ID로 해석한 실제 경로를 전달한다.
4. #650에서 버전의 의미·비교 불가 상태·판정 규칙을 먼저 정하고 생산 Set 기록·소비 Set 판정·프로젝트 집계·VM 표시를 연결한다. 출처 작업의 완료 조건에 이 설계를 섞지 않는다.

| 독립 작업 | 이 문서와의 경계 |
|---|---|
| #473 → #474·#475·#477 | 표 항목 연결·덮어쓰기 방지·삭제 정합. #443·#368·#685를 선행으로 두지 않고 기존 안정 키·기록을 우선 사용 |
| #475 | 재시작·재진입 후 기존 결과 보존과 실제 대상 파일 충돌 확인이 기준. 프로젝트 전역 카운터는 필수 아님 |
| #441 → #444 | #444는 상태 갱신 비용과 기존 구조 개선을 먼저 확인하고 필요할 때만 파일 분리. #441이 증분 갱신·재시작 복구를 사용 |
| #369 | Runner NodeSet 선택 저장·복원. 기존 `nodeSetSource` 설계 유지, 참조 전환의 선행 아님 |
| #643·#411 | 포맷·이어쓰기 담당 정리는 팀 논의 중. 출처 계약을 중복 정의하지 않음 |
| #562·#681 | 개명 오류 수정과 참조 전환을 구분. #368·#685를 #681의 머지 조건으로 추가하지 않음 |

폴더명을 ID로 바꾸는 작업, 모든 Set JSON의 분할, 전면 스토어 교체를 위 작업들의 필수 선행으로 두지 않는다.

## 4. 어휘 실측 — `Reference` 명명의 근거

당시 설계안은 기준 해석 파일 엔티티를 `Reference` 로 부른다. 초판은 `Model` 이라 불렀고, 후보 4종을 실측해 바꿨다. (`dev` @ `4c7608e`, `external/` 제외)

| 용어 | 코드 | 무엇을 가리키나 | 사용자 노출 |
|---|---|---|---|
| `model` 단독 | `setModel(` **91회** · `model/` 디렉토리 · surrogate 계열 **293회** | **MVC 계층** + **대리모델** 두 뜻으로 포화 | UI 문자열 14종 — Trained Surrogate Model · Available Models · Model Upload · Model Type · Select Model … **거의 전부 대리모델** |
| `AnalysisModelContext` | 174회 | 파싱된 해석 덱 | 0 |
| `deck` | 40회 · **전부 주석, 식별자 0건** · 11파일 | 솔버 입력 텍스트 (`.inp`·`.dat`) | 0 |
| `input` | `inputFiles` 64 · `input_files` 35 · `InputFilePathes` 25 · `inputFilePath` 16 | **3중 충돌** | UI 8종, 역시 3뜻 |
| **`reference`** | `referenceFile` 48 · `refFile` 29 = **77회** | 기준 해석 파일과 그 템플릿 행 | Input Reference File · Add Reference File · Reference Set: |

**`Model` 기각** — 해석 덱 뜻으로 쓰이는 것은 `DashAnalysisModelContext` 복합어 하나뿐이고 단독 "Model" 은 MVC 와 대리모델이 이미 차지했다. 화면에 뜨는 "Model" 이 거의 전부 대리모델이라 사용자 혼동 위험이 가장 크다.

**`deck` 기각** — 충돌은 0이지만 `.prt`(NX 파트)·`.wbpj`(WB 프로젝트)를 담지 못하고, 설계안이 이미 **역할 이름**으로 쓰고 있어 엔티티로 올리면 `Deck.files.deck` 이 된다.

**`input` 기각** — 넷 중 가장 나쁘다. 이미 세 뜻으로 갈려 있다.

| 뜻 | 쓰이는 곳 |
|---|---|
| 기준 해석 파일 | "Input Reference File" · `input_files[]` |
| DOE 가 생성한 케이스 입력 파일 | "Analysis Input Files" · "Generate Input File" · "Input Cases" |
| 학습 입력 변수 | "Input Design Variables" |

여기에 `InputFilePathes`(25회)는 preprocessor DLL 의 **결과** 파일 경로라 이름과 뜻이 이미 어긋나 있다.

**당시 `Reference` 명명 근거** — 기존 식별자 77회와 UI 라벨이 전부 이 뜻이라 새 어휘를 만들지 않는다 · 기존 Reference File 행이 이미 `{name, target_component, path}` 로 **파일 묶음**이라 개념이 연속적이다 · "기준" 은 형식 중립이라 FE·CAD 양쪽을 담는다.

| 자리 | 채택 |
|---|---|
| 엔티티 · ID · 색인 키 · 디렉토리 | `Reference` · `ref_*` · `references[]` · `references/` |
| 엣지 | `upstream.reference` |
| `files` 안 역할 이름 | `deck` · `part` · `template` · `material` — **변경 없음** |
| 사용자 라벨 | 기준 해석 파일 |
| C++ 타입 | `DashAnalysisModelContext` 계열 **유지** — 174회 선례이고 내부 전용이라 UI 충돌이 없다 |

AnalysisLauncher의 `input_files[]` 개명은 당시 제안이며 현재 출처 계약의 필수 변경이 아니다. 위 ID·색인 키·디렉토리 표기도 당시 어휘안으로, 저장 스키마의 채택을 뜻하지 않는다.

---

## 5. 경로 규약 불일치 5곳

질문은 하나다 — **"어느 모듈의 산출물이 숨김 `.dproj` 로 가고 어느 것이 사용자 루트로 가나".** 여기에 답하는 자리가 다섯인데 서로 다른 답을 낸다. 실질 쟁점은 **Optimizer 하나**이고 MCU 가 예외로 붙는다.

| # | 자리 | 무엇이라고 말하나 | 좌표 |
|---|---|---|---|
| 1 | `ModuleType` enum 주석 | `// Internal Data: Uses ProjectPath (hidden from user)` 그룹에 **ModelBuilder 와 Optimizer 둘 다** 들어 있다 | `DashIOController.h:22-24` |
| 2 | 클래스·함수 doc-comment | `Internal Data: In {ProjectRootDir}/…` — 이름은 "Internal" 인데 경로는 사용자 루트이고, **User Output 과 같은 경로**를 적어 둬 구분 자체가 무의미하다 | `DashIOController.h:39-40` · `:63-65` |
| 3 | `getModuleDir()` 구현 | `if (type == ModuleType::ModelBuilder)` 만 internal → **Optimizer 는 UserRoot** | `DashIOController.cpp:31` |
| 4 | MCU 역방향 예외 | `getModuleDir()` 자체를 우회해 `getUserPath()` 에 직접 `ModelBuilder_{Set}` 를 붙인다. 주석 — *"MCU training results must live under userPath, not the hidden projectPath (.dproj)"* | `DashModelBuilderMCU.cpp:554-562` |
| 5 | `isUserOutputType()` | AnalysisLauncher · DataPreprocessor · ModelRunner · ResultsAnalyzer 만 true → **Optimizer 를 제외**한다 (3번 구현과 반대) | `DashIOController.cpp:106-112` |

Optimizer 에 대해 1번은 "숨김", 3번은 "사용자 루트", 5번은 "user output 아님" 이라고 각각 말한다. 2번은 두 분류의 경로를 같게 적어 구분을 무너뜨린다.

**실제 거동은 3번 + 4번**이다 — ModelBuilder Sim 만 `.dproj` 안, 나머지 전부 사용자 루트, MCU 는 우회.

5번이 지금 무해한 이유는 **`isUserOutputType()` 호출부가 0곳**이기 때문이다. 참조는 선언(`.h:131`)과 정의(`.cpp:106`) 둘뿐이다. **그 함수를 신뢰하는 코드가 생기는 순간 결함이 된다.**

이 조사는 단일 루트를 검토한 근거다. 현재는 경로 규칙을 개별 정합화할 수 있으며 루트 통합을 필수 선행으로 두지 않는다.

---
## 6. 검증 한계

경로·어휘 실측은 원래 커밋 기준으로 보존했다. “호출 0곳”은 당시 정적 검색 결과이고 동적 경로나 현재 상태를 보장하지 않는다. 현재 대응은 이슈 개정의 책임 경계를 적용한 것으로 건별 완료 재판정이 아니다. 문서 링크·표·폐기 전제 정합성을 확인하며 빌드·실행은 수행하지 않았다.
