# 엔티티 모델 개편안 — 현재 적용 범위와 과거 비교

> **2026-10-08 개정 반영.** [이슈 개정 이력](Issue-Revision-History.md)의 반영된 결정을 본문에 적용했다. 추가 개정 계획과 미정 계약은 제안으로 구분한다.

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

## 1. 문제와 목표

초안(2026-08-09, `refactor/async-execution` @ `b97e23a`)은 이름·경로로 추정하는 연결과 정의·산출 혼재를 진단했다. #520 이전의 “Set은 식별자가 없다”는 설명은 현재 전제로 사용하지 않는다. 목표는 기존 신원으로 입력 참조를 복원하고 산출물이 실제 사용한 출처를 읽을 수 있게 하는 것이다.

| 당시 진단 | 현재 적용할 해법 | 확대하지 않을 범위 |
|---|---|---|
| 이름·관례·`folders[0]`로 추정 | Set 설정의 `setId` 선택·역조회 | 별도 엔티티 원장 |
| 고정 경로 결과의 출처 불명확 | 결과와 실제 출처를 함께 교체 | 모든 실행 누적·복구 스냅샷 |
| 정의·상태가 같은 JSON | #444 비용·기존 구조 개선 확인 | 모든 Set 파일 분리 |
| DV·응답을 sanitizer로 조인 | 기존 안정 키·항목별 계약 점검 | 모든 로컬 ID 개편을 Set 작업에 포함 |

의도한 재실행 결과 교체와 #475의 원치 않는 예측 결과 덮어쓰기를 구분한다. 후자는 재시작·재진입 후에도 기존 결과를 보존하고 실제 파일 충돌을 확인해야 한다.

## 2. 엔티티와 소유 범위

| 대상 | 식별·소유 기준 |
|---|---|
| Set | 기존 JSON의 `setId`, 프로젝트는 조회 |
| 현재 입력 참조 | 소비 Set 설정의 상류 `setId`·세부 선택 |
| 산출물 | 생산자가 실제 출처를 산출물에 기록 |
| 결과 항목 | #474·#477에서 기존 안정 키와 재열기 기준 검토 |
| 버전 | #650 의미·발급·비교 계약 |
| 기준 deck·FE 심볼 | 기존 identity·registry와 공통 출처 계약 |
| Solver 경로 | 머신 환경 |

`Definition → Run[]`을 모든 모듈의 공통 구조로 강제하지 않는다. dataset·response·model·part 선택은 Set보다 세밀하므로 함께 보존한다.

## 3. 개편 3안 비교의 현재 지위

과거 A/B/C는 아이디에이션이며 새 확정 계약이 아니다.

| 안 | 당시 구상 | 유효한 비교점 | 현재 적용 |
|---|---|---|---|
| A | 기존 JSON에 헤더·참조 추가 | 변경은 작지만 DV·Response 이름 키 문제는 별도 | 기존 `setId`의 점진 참조 전환 |
| B | ID 디렉토리·실행 스토어 | 집약 가능, 수동 검사·이관 비용 | 필수 선행 제외 |
| C | 내용에 ID, 경로는 표시명, 별도 실행 인덱스 | 관찰 가능성과 개념 분리 | 현행 경로 유지 가능, 실행 인덱스·출처 자동 이관은 미채택 |

C안 추천과 “산출은 반드시 누적”·“구버전은 마이그레이터로 변환”은 현재 채택안이 아니다. Run·Definition·Surrogate ID 일괄 발급도 요구하지 않는다.

## 4. 현재 기록 예시

다음 JSON은 **소유 위치를 설명하는 개념 예시**다. `setId`만 기존 신원 키이며, `inputSelection`·`source` 등 나머지 키·중첩·표기와 판독 API는 #368·#685에서 확정한다. ID 예시는 #520의 현행 12자리 hex 형식이며, 각각 기존 Set JSON에서 읽어 온 값으로 가정한다. 새 발급 규칙을 뜻하지 않는다.

소비 Set 설정 — 현재 Builder 선택:

```json
{
  "setId": "b7ad0de237d1",
  "inputSelection": {
    "setId": "36e874bd7b5d",
    "response": "Max_Mises",
    "model": "StableNet"
  }
}
```

그 소비 Set의 기존 산출물 — 생성 당시에는 다른 Builder를 사용한 경우:

```json
{
  "source": {
    "setId": "0b503615d34a",
    "response": "Max_Mises",
    "model": "StableNet",
    "deck": "실제로 사용한 deck의 공통 계약 정보"
  }
}
```

두 값이 다를 수 있는 이유는 입력 선택만 바뀌고 아직 재실행하지 않았기 때문이다. 실행 전에 선택과 산출물의 공통 출처를 검증한다. 새 산출물로 교체할 때 그 실행이 실제 사용한 출처를 기록한다. 버전 정보는 이 예시에 임의로 추가하지 않는다.

## 5. 사용자 시나리오와 보장

| 조작 | 유지할 것 | 바꿀 것·확인할 것 |
|---|---|---|
| 같은 Set의 상류 교체 | 현재 Set ID, 재실행 전 기존 출처 | 현재 참조·세부 선택 |
| 상류 개명 | 상류 ID와 연결 | 경로·표시명 조회 |
| 삭제 후 동명 생성 | 이전 참조 기록 | 자동 재연결하지 않음 |
| 재실행·덮어쓰기 | 현재 Set 신원 | 결과와 실제 출처 |
| 상류 같은 ID 재생성 | ID 연결 | 최신성은 #650으로 별도 판단 |
| 구산출물 조회 | 기존 Set ID | 필수 출처 없으면 재생성 |

샘플 추가·형상안 비교·응답 추가·알고리즘 비교·목적함수 변경은 유효한 시나리오다. 실행 이력 UI·그래프 복제·공통 분기 메뉴를 완료 조건으로 포함하지 않는다. #615의 번호·자동 선택, #646의 교체 시점은 팀 논의가 남아 있다.

## 6. UI 아이디어의 경계

기존 선택 UI에서 입력 변경을 허용하고 현재 선택과 생성 당시 출처를 구분해 표시할 수 있다. `Stale` 표시에는 #650의 소비 Set 판정 결과가 필요하다. VM에서 이름·시간·지문을 독자 비교하지 않는다. 실행 이력·산출물 전용 목록은 현재 요구에서 빠졌고 표 연결·충돌 방지·삭제는 #473의 오류 수정으로 진행한다.

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

## 7. 보존한 코드 조사

다음 좌표·수치는 원래 시점의 기록이다. 현재 완료 여부가 아니며 “ID가 필요한데 없는 것”은 당시 후보 분류다.

### 이미 제대로 된 선례 — FE Condition

먼저 짚을 것: **FE Condition 은 이미 안정 식별자를 가지고 있다.**

```cpp
// controller/DashAnalysisModelContext.h:88
// Deterministic symbol uuid of the condition (persistable across sessions as
// long as the content identity and deck structure are unchanged)
QString getFeConditionUuid(const QString& condName) const;
```

게다가 편집 좌표가 `(uuid, entryPtr, param)` 삼중항이고 `entryPtr` 은 JSON Pointer 다 (`"" = whole node`, `"/entries/N"`). 기존 식별자를 활용할 선례다. 모든 Set·결과를 이 패턴으로 바꾸는 결정은 아니다.

### 당시 항목 식별 조사

| 엔티티 | 현재 식별 방식 | 깨지는 지점 | 심각도 |
|---|---|---|---|
| **DesignVariable** | 이름 문자열 | `sanitizeString()` 비가역 변환. 핸들 rename 시 상·하류 연결 단절 | **상** |
| **Response** | 이름 문자열 (+ component · loadstep 과 합쳐 파일명이 됨) | 동일. 추가로 **두 벌로 중복된 sanitizer 가 계약 없이 일치해야만** XML key ↔ config response 매칭이 성립 (3.2.1) | **상** |
| 실행 배치 | 별도 신원 없음 | 고정 경로 덮어쓰기를 당시 문제로 분류 | 전체 이력 보존은 현재 요구 아님 |
| **Surrogate** | `(response, model)` 쌍 | 재학습 시 같은 쌍이 다른 산출물을 가리킴 → 최적화 결과 재현 불가 | **중** |
| **Model** (기준 해석 모델) | 없음 (Registry 메모리 전용) | 재오픈 시 "이 Set 은 어느 모델 기준" 소실 | **상** |

**DV·Response 의 근거 — 이름 변형은 실제로 손실이다** (`model/builder/ModelBuilderConfigHelper.cpp:12-25`):

```cpp
QString ModelBuilderConfigHelper::sanitizeString(const QString& str) {
    QString result = str;
    result.replace(" ", "_");   result.replace("/", "_");   result.replace("\\", "_");
    result.replace(":", "_");   result.replace("\"", "_");  result.replace("<", "_");
    result.replace(">", "_");   result.replace("|", "_");   result.replace("?", "_");
    result.replace("*", "_");
    return result;
}
```

`"Max Stress"` 와 `"Max/Stress"` 가 둘 다 `"Max_Stress"` 가 된다. 역변환 불가다. 그리고 UI 는 이미 이 충돌과 싸우고 있다 — `DashModelBuilderWidget.cpp:1070-1071` 은 `findText(displayResp)` 가 실패하면 `findText(diskResp)` 로 재시도한다. **이름이 식별자 역할을 하는데 경로 중간에서 이름이 변형된다.**

#### 더 심각한 것 — sanitizer 가 두 벌이다

당시 XML 파일명 조사 과정에서 확인된 사항. **바이트 단위로 동일한 `sanitizeString` 이 서로 다른 모듈에 각각 존재하고, 학습 파이프라인은 이 둘의 출력이 일치한다는 전제 위에서만 동작한다.**

| 구현 | 위치 | 용도 |
|---|---|---|
| `DashPR::Utils::sanitizeString` | `model/preprocessor/DashUtils.cpp:18-32` | XML 의 `dict_item key` 생성 (`DashResultXmlWriter.cpp:309·423·443·581·702`) |
| `ModelBuilderConfigHelper::sanitizeString` | `model/builder/ModelBuilderConfigHelper.cpp:12-25` | config 의 `Configuration.{model}.response` 값 생성 |

외부 학습 프로세스는 config 의 `response` 로 XML 안의 key 를 찾는다. 두 함수 중 **한쪽만 수정되면 매칭이 깨지고 조용히 실패**한다. 이것은 계약이 아니라 우연한 코드 중복으로 유지되는 결합이다.

(같은 종류의 중복: `filterSplitFiles` 가 `DashDataProcessor` · `DashFileLocator` · `DashResponseInitializer` 3곳에 존재. 이쪽은 결과파일 필터라 파이프라인 정합성과는 무관.)

Response 식별을 개편한다면 sanitizer 계약도 검토해야 한다. 새 ID 형식·일괄 전환은 확정하지 않았다.

### XML 파일명 조사 — XML 파일명은 아무도 파싱하지 않는다

**질문 전제부터 틀렸다.** `docs/Module_Configuration_Files.md` 는 파일명을 `{response_name}.xml` 로 기술하지만 실제는 KPI 정의 삼중항의 인코딩이다.

| 경로 | 규칙 | 근거 |
|---|---|---|
| 일반 | `{component}_{step}_{substep}_{name}.xml` | `DashDataProcessor.cpp:1844` |
| BORE/BOSS 그룹 | `{BORE\|BOSS}_{step}_{substep}_{originalName}.xml` | `:1831` |
| Modal | `{component}_{stat}_{modeName}.xml` | `:3266` |
| Custom KPI | `{component}_{loadstep}_{name}.xml` | `:3650` · `:3967` · `:4249` · `:4532` |

**결론: 파일명을 파싱하는 코드가 없다.** XML 참조 지점 전수 조사 결과 전부 `*.xml` 글롭 + 경로 전달이다.

| 소비처 | 동작 |
|---|---|
| `DashModelBuilder.cpp:89 · 107 · 190` | `entryList("*.xml")` — 목록 나열만 |
| `DashModelRunner.cpp:1552` | 동일 |
| `DashResultsAnalyzerWidget.cpp:1303 · 1822` | 동일 (콤보 표시용) |
| `DashModelBuilder::onLoadButtonClicked()` `:268-308` | 파일명으로 **경로만 조립**, 이후 파일을 열어 내용 파싱 |

`completeBaseName()` 을 쓰는 유일한 지점(`DashResponseInitializer.cpp:336`)은 `.odb`/`.rst` 결과파일 분할 필터로 XML 과 무관하다.

응답 식별은 **XML 내부 `dict_item key`** 로 이뤄지고, 외부 학습 프로세스는 config JSON 을 통해 경로와 응답명을 **별도로** 받는다:

```
DashOptiDeepOpt.exe train-model-1d "<ModelBuilder_{Set}.json>" --output-dir "<…>"
                                          ├─ "Data Label" > "Dataset"          = XML 절대경로
                                          └─ "Configuration".{model}."response" = 응답명(sanitized)
```

당시 GUI 조사에서는 XML 파일명 파싱 의존을 찾지 못했다. 전체 외부 도구의 이름 변경 안전성을 보장한 것은 아니다.

**단서 2가지**:
- `extensions/deep_opt/DashOptiDeepOpt.exe` 는 이 저장소에 없어 내부 동작은 미확인이다. 위 결론은 **인터페이스 기반 추론**이며 exe 확보 시 재확인이 필요하다 (필요한 정보를 별도로 받으므로 파일명을 파싱할 구조적 이유가 없다는 근거).
- 조사 중 **진짜 위험은 파일명이 아니라 sanitizer 이중화**임이 드러났다 (위 sanitizer 조사). Response ID 도입의 실제 작업 대상은 그쪽이다.

---
## 8. 남은 결정과 검증 한계

공통 출처 필드·검증(#368), 소비 경계(#685), 버전(#650), 항목 키(#474·#477), Reference 역할·다부품을 정한다. Set ID 재발급 방식·전체 Run 보존·구산출물 출처 마이그레이션을 착수 전 질문으로 다시 열지 않는다.

시나리오 빈도는 실사용 로그로 검증하지 않았고 UI는 프로토타입 미검증이다. 이번 개정은 문서의 책임·예시·단계 정합화이며 빌드·실행 검증을 수행하지 않았다.
