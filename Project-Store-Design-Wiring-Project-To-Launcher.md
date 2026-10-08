# 프로젝트 → Analysis Launcher — 기존 Set 신원을 사용하는 배선

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

## 1. 범위와 기준

프로젝트 생성 → 입력 등록 → 파싱 → Geometry·Condition 선택 → DOE Sampler → Analysis Launcher의 입력 선택·생산 출처 배선을 다룬다. #368의 전체 완료 경계는 Builder `model_info.json`까지이므로 앞단 완료만으로 #368 전체가 끝나지는 않는다. Builder를 소비하는 Runner·Optimizer는 #685다.

이전 `dev` @ `7024e04` 동선 조사는 당시 좌표로 보존한다. 당시 Geometry·Condition을 Launcher가 직접 고르던 경로가 현재 확정 참조 관계를 대체하지 않는다.

| 참조를 바꾸는 소비 모듈 | 변경 가능한 상류 입력 | 담당 |
|---|---|---|
| DOE Sampler | Geometry Parameterization·Condition Parameterization Set | #368 |
| Analysis Launcher | DOE Sampler Set | #368 |
| Model Builder | 데이터셋을 생성한 Analysis Launcher Set | #368 |
| Model Runner | 학습 산출물을 생성한 Model Builder Set | #685 |
| Optimizer | 학습 산출물을 생성한 Model Builder Set | #685 |

데이터셋·응답·모델·part 등의 세부 선택은 함께 유지한다. 데이터셋 파일을 처리하는 모듈과 그 데이터의 출처 Set은 구분한다. 기존 DataPreprocessor 경로 실측이 위 확정 참조 관계를 대체하지 않는다. Resample 간 참조·자동 선택(#615)은 추가 개정 계획의 팀 논의 사항이다.

## 2. 신원과 자료 소유

신규 Set은 기존 #520 발급 경로를 사용하고 열기에서는 기존 ID 복원을 유지한다. 기존 `setId`를 `id`로 옮기거나 모듈명·Set명에서 `UUID::from_namespace`로 다시 만들지 않는다. 같은 이름 재생성은 새 Set이고, 개명은 같은 Set이기 때문이다.

| 대상 | 소유·연결 |
|---|---|
| Set 신원 | Set JSON의 기존 `setId` |
| Set·경로 조회 | 프로젝트의 Set 기반 색인 |
| 현재 선택 | 소비 Set 설정의 상류 ID·세부 선택 |
| deck·심볼 신원 | 기존 identity 및 공통 출처 계약 |
| 생성 당시 출처 | 산출물 내부 |
| 컨텍스트 캐시 | 기존 경로별 registry |

`dash::core::UUID`의 기존 사용은 새 Set ID 체계를 도입할 근거가 아니다. v5·12자리 절단·v7 전환·새 namespace 상수는 이 배선의 요구에서 제외한다. Reference ID와 content UUID를 같게 만들거나 서로 변환하는 규칙도 임의로 추가하지 않는다.

## 3. 프로젝트 생성·열기

| 동선 | 적용할 배선 | 검증 |
|---|---|---|
| 생성 | 기존 config 경로·Set 생성 기반 사용 | 새 `reference.json` 생성이 모든 작업의 선행이 아님 |
| 열기 | 기존 Set ID 복원·조회색인 구성·현재 선택 복원 | 기존 ID가 보존됨 |
| 개명 | 같은 ID 유지, 실제 경로 해석 갱신 | 다른 이름으로 열어도 같은 입력 |
| 동명 재생성 | 신규 Set의 새 ID 사용 | 삭제된 대상의 참조를 자동 복구하지 않음 |
| 구산출물 소비 | 필수 출처 검사 | 누락이면 재생성, 추론 보충 없음 |

`project.json`이 없다고 거부하거나 전량 승격하지 않는다. 현재 참조 deck은 `referenceModels.json`에서 조회한다. G6(#365·#416)에서 폐기한 `AnalysisModelIdentity.json`의 경로 목록으로 과거 산출물 출처를 만들지 않는다.

### 열기 경로의 과거 실측 수정

| 항목 | `7024e04` 당시 관찰 | 현재 적용할 교훈 |
|---|---|---|
| `loadSetsFromConfigs()` | 호출 0곳 | 함수 이름만으로 열기 배선을 정하지 않음 |
| `restoreExistingModules()` | 실제 복원 경로, `DashProjectManager.cpp:122` 호출 | 현재 호출 경로와 #520 복원을 함께 확인 |
| variant 검출 | Geometry·Builder 외 Runner·Launcher도 존재 | 앞단만 고칠 때 공용 경로 영향을 확인 |
| Add File 좌표 | `DashMainWindow.cpp:2114-2197`, 필터 `:2126-2127` | 기반 조사와 줄 번호가 달랐음 |
| Launcher 선택 | `Selected Design Variables`가 `[condition, geometry]` 파일명 배열 | 새 참조 계약 적용 시 관련 리더를 함께 점검 |

이 관찰을 죽은 스캐너 제거·전 variant 재작성의 필수 선행으로 바꾸지 않는다.

## 4. Add File·Reference·파싱

당시 Add File은 파일 복사 후 트리를 새로 고쳤다. `.stli`는 부모 폴더째 복사했고 다른 입력은 파일을 복사했다. 등록 시 원본 경로와 프로젝트 안 실제 파일을 구분하는 정보는 유용하지만, Reference registry 파일 형식·별도 발급 규칙은 아직 설계 항목이다.

| 확장자 | 당시 경로·역할 | 현재 검토 |
|---|---|---|
| `.inp`·`.dat`·`.dfsxml` | deck, Add File과 후보 스캔 | 공통 출처의 실제 deck 정보와 연결 |
| `.prt` | CAD part | 다부품·Workbench 조합 확인 |
| `.stli` | template, 폴더 복사 | 인접 파일 변경 범위 확인 |
| `.wbpj` | 후보 스캔에만 있음 | 발견과 사용자 선택을 구분 |
| `.dbase`·`.msc`·`.stlx` | 재료 브라우즈·제자리 수정 | 변경 감지·기록 범위 별도 |
| `.vtk`·`.vtu`·`.rst`·`.odb`·`.csv`·`.stp`·`.step` | Add File 가능, 동일 참조 역할 아님 | 복사를 deck 등록과 혼동하지 않음 |

### 해시·Identity 조사에서 유지할 사실

아래는 `7024e04` 당시 조사다. 현재는 G6(#365·#416)에서 구 identity 저장·해석 함수를 폐기하고 `referenceModels.json` 기반으로 전환했다. 아래의 함수명·저장 시점을 현행 배선으로 사용하지 않는다.

`rwFileSha256`(`DashRwSession.cpp:1030-1066`)은 스트리밍 해시·size/mtime 메모이즈 함수였고, `rwResolveContentIdentity`(`:1090-1146`)가 identity 저장소를 읽고 썼다. 해시 함수와 저장된 해시 값의 재사용은 다르다. 당시 새 프로젝트의 identity는 실제 파싱 시 생길 수 있어 Add File 시 이미 있는 값이 아니었다.

캐시 키가 raw 경로인 경우 비정규 경로와 canonical 경로가 다르면 다시 해시할 수 있다. 함수 노출·경로 정규화·대용량 파일 비용을 실제 구현에서 확인한다. 복사 중이므로 추가 해시 비용이 없다고 단정하지 않는다.

구 Identity는 open 때 현재 값으로 갱신했으므로 등록 당시 정보·생성 당시 출처를 대신할 수 없었다. 해시 문자열의 bare hex·접두사, 등록 지문 동결, 재등록 방식은 #368·#650의 필드 규칙으로 자동 승격하지 않는다.

## 5. 컨텍스트 배선 — 공유 맵과 활성 커서

영속 입력 선택과 화면 활성 파일은 분리한다. 경로별 `DashAnalysisModelContextRegistry` 자체를 폐기하지 않는다.

```text
데이터: Set의 명시적 선택 → 참조 해석·검증 → 실제 경로 → registry 조회
화면:   렌더·프리뷰 선택 → setDisplayedContext → actor·카메라 갱신
Load:   명시적 기준 지정 → setReferenceModel → 기준 deck 등록·선택
```

프로젝트는 Set 조회·집계, 각 모델은 자기 입력·실행을 소유한다. VM은 동작을 전달하고 화면을 갱신한다. 구체 resolve 함수명·인자·반환형은 이 문서의 확정 API가 아니다.

### 기존 컨텍스트 소유 조사

| 대상 | `7024e04` 당시 구조 | 배선 시 보존할 의미 |
|---|---|---|
| registry | `m_contexts`: 경로 → `unique_ptr<Context>` | 캐시가 컨텍스트 소유 |
| `getOrLoad`·`get` | 비소유 포인터 반환, canonical 경로 처리 | 중복 컨텍스트를 새로 만들 필요 없음 |
| `setActiveContext` | actor 제거·추가, 카메라 리셋 | 데이터 조회에 렌더 부작용을 끼우지 않음 |
| Condition 모델 | `m_loadedFilePath`, `getContext`, `refreshFromLoadedAnalysis` | 기존 모델 경로 주입 사용 가능 |
| CAD 모델 | `m_loadedFilePath`, `getContext` | #366에서 무산출 사슬의 죽은 읽기 제거. 형상 출처 영속화는 D31 유보 |
| Morphing 모델 | 동일한 조회 자리 없음, `m_fileName` 호출 0 | 필요한 모델 경계를 확인 |

| 당시 호출 좌표 | 관찰 | 적용 방향 |
|---|---|---|
| `DashGeometryParameterPresentationModel.cpp:46`, `:58` | active 경로·context로 DV source·part 처리 | 현재 Set의 검증된 입력에서 얻음 |
| `DashConditionParameterizationWidget.cpp:222`, `:313-315` | 뷰가 전역 context·경로 사용 | 기존 모델 조회 경로와 연결 |
| `DashGeometryParameterCADWidget.cpp:345`, `:416` | 전역 경로를 refresh에 전달 | #366의 죽은 전역 읽기 제거까지. Set 형상 출처 연결은 D31 유보 |
| `DashMorphingSettings.cpp:562`, `:636` | active context 사용 | 호스트 Set 입력 조회 확인 |
| `DashMainWindow.cpp:2326` | 당시 Load 파싱·렌더 트리거 | 현재 Load 기준 지정과 displayed 렌더 동작을 분리 |
| `DashMainWindow.cpp:2496-2499`, `:2523-2527`, `:2664`, `:3331` | 렌더·트리 선택 | 세션 상태로 유지 |

CAD는 이번 묶음에서 #366 봉합(M5 제외·죽은 읽기 제거)까지다. `referenceModel` 키를 추가하거나 CAD 형상 출처를 새로 영속 연결하지 않는다. D31의 형상 출처는 [CAD 경로 처분](Project-Manifest-CAD-Path-Disposition.md)에 따라 유보한다.

같은 deck을 보는 Set은 캐시를 공유할 수 있다. Condition Value 편집이 deck을 직접 바꾸던 경로가 있으므로 Set 입력 선택을 분리했다고 편집 데이터까지 격리됐다고 보지 않는다. 프로젝트 종료 시 캐시 해제와 비소유 포인터 수명도 별도 점검한다.

원래 active-cursor의 세부 사실관계는 [활성 커서와 데이터 결합](Project-Manifest-2-Active-Cursor-Data-Coupling.md)에 있다. 기존 조사에서 출처 변경 없이 분리할 수 있던 경로와 새 출처 배선의 범위를 구분한다.

## 6. 정의 저장·DOE 선택·생성

| 당시 라이터 | 쓰던 것 | 현재 점검 |
|---|---|---|
| `saveMorphingSettings` | `Morphing.*` | 자기 Set 신원·선택 유지 |
| `DashDesignVariableModel::saveToJsonFiles` | `DV-Geometry` 및 Condition 정의 | AL 화면에서 상위 정의를 수정하는 경로 확인 |
| `saveDvCondition` | `DV-Condition` | 실제 대상 deck·Set과 일치 |
| `saveSettings`·`saveInputFileSettings` | `DOE configuration`·`input_files` | 현재 선택과 생성 당시 출처를 분리 |

전 라이터에 정의 해시·`consumed` 갱신을 넣는 일괄 헬퍼는 요구하지 않는다. #650의 버전 의미가 정해진 뒤 관련 생산 변경 경로를 연결한다.

당시 `Selected Design Variables`는 파일명 배열이었고 리더는 `DashDoeConfigManager::loadSettings`, `DashAnalysisLauncher::findAndEmitSourceFiles`, `DashMorphingDoeExecutor`, `DashDataProcessor`에 흩어졌다. 일부만 ID로 바꾸고 다른 리더를 이름 원본으로 남겨 두면 정합성이 깨질 수 있다. 적용 범위의 리더·라이터를 함께 확인하고 임시 호환 필드가 필요하면 파생값·제거 조건을 명시한다. 두 값을 모두 원본이라고 선언하지 않는다.

현재 참조 관계는 DOE Sampler가 Geometry·Condition을 선택하고 Launcher는 DOE Sampler를 선택하는 #368 범위다. 기존 경로에 남은 직접 참조·파일명 리더를 이 경계에 맞춘다. `input_files[]`의 `{name, target_component, path}` 및 선택 행은 실제 deck·part 기록으로 이어지며, 리스트 전체와 실행에 실제 사용한 항목을 혼동하지 않는다.

### 개념 예시

```text
DOE Sampler S: 기존 setId 유지, Geometry G1 → G2 선택 변경
Launcher L:   기존 setId 유지, DOE Sampler S1 → S2 선택 변경
기존 산출물:  변경 전 실제 사용한 입력 출처 유지
재실행 교체:  실제 선택·검증된 입력과 새 결과의 출처를 함께 기록
```

위 기호는 설명용이며 저장 필드·ID 형식이 아니다. 조합 ID·첫 입력 영구 핀은 없다.

## 7. 표시와 검증

참조·필수 출처 검증은 실행·조회·프리뷰의 공통 경계에서 사용한다. 최신성 배지는 #650의 개별 Set 판정 결과를 프로젝트가 집계하고 VM이 표시한다. #368만으로 Geometry 저장 후 Launcher가 `Stale`이 된다고 확정하지 않는다.

검증 사례는 Set 개명, 삭제 후 동명 재생성, 상류 교체 후 재실행 전 출처 유지, 재실행 결과·출처 일치, 출처 없는 구산출물 재생성 안내다. 프리뷰·렌더 전환만으로 입력 선택이나 기존 출처가 바뀌지 않아야 한다.

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

## 8. 미결과 조사 한계

출처 필수 정보·판독 API(#368), 생산 완료·교체 경계, Reference 역할·복수 파일, 캐시 수명·공유 편집 영향, 버전 계약(#650)은 구체화가 필요하다. #513 비동기화와 #685의 경계, #684 예측 모듈 호출 책임은 추가 개정 계획의 논의 내용이다. 관련 코드 공유만으로 새 선행 관계를 추가하지 않는다.

원래 CoreLib v7 API 가용성 조사와 stdin/stdout 전환안은 이번 참조 배선의 선행이 아니므로 실행 단계에서 제거했다. 저장 레이아웃·상태 파일 분리는 #441·#444의 필요성 검토로 다룬다. 좌표는 당시 정적 관찰이며 이번 개정에서 빌드·실행하지 않았다.

관련: [자료·버전 검토](Project-Store-Design-Definition-Version-Minimal.md) · [현재 계층과 배치](Project-Store-Design-Layer-Cut.md) · [화면 표시](Project-Store-Design-Dependency-State-Display.md).
