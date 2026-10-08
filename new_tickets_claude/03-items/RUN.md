# RUN 작업 목록

> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.

> 기준: dev @ b08a91b3. 원자 항목은 `02-claims/RUN.md`. 파일 접두는 그 문서와 같다 (`W:`·`M:`·`PM:`·`MW:`·`AW:`).
> 열린 PR 7건 중 머지 대상 6건 (#651 #652 #654 #655 #656 #658) — #530 은 재업로드 노선이라 머지 대상이 아니다 (05-final/decisions.md ⑩·②). RUN **본체 파일**(M · W · PM · MW)을 만지는 것은 **PR #654**(#332 — M.cpp performMorphing) 하나뿐이고, 머지될 때까지 M:performMorphing 을 만지는 항목은 뒤로 둔다. 접점 파일만 겹치는 것 — `model/DashProject.cpp`(#651 #652) · `view/DashMainWindow.cpp`(#651 #652 #654 #655) · `tests/CMakeLists.txt`(#651 #652 #654 #655) · `view/dialog/DashDirectLaunchDialog`(#652 — RUN-30 의 선행). **#656·#658 은 RUN 항목의 변경 범위와 교집합 0** 이라 선행 추가 없음 (#656 = 런처·preprocessor 공용 함수 · #658 = RW 문서·preprocessor v3).
> 구 #368 T23 소비 범위는 #685의 RUN-34로 이관됐다. PR #530 hunk는 수정 지점 참고이며 조합 핀을 그대로 이식하지 않는다. #513 워커 이관·#650 최신성·결과 오류 수정은 각각의 목표로 진행한다.

### RUN-01 · NodeSet 선택을 독립적으로 저장·복원한다 (#369)
- 종류: PR | 규모: S | 태그: A · feature
- 목표: 기존 nodeSetSource 저장·경로 처리 설계에 따라 Runner의 NodeSet 선택을 저장·복원한다. #443의 하위에서 분리된 독립 작업으로 유지한다.
- 완료 기준: 선택 저장 후 재진입·재시작에 같은 nodeSetSource 복원, 빈 선택·해석 불가 경로의 기존 처리 검증. #443·#368·#685를 선행이나 완료 조건으로 요구하지 않는다.
- 변경 범위: model/DashModelRunner.cpp · model/DashModelRunner.h · view/DashModelRunnerWidget.cpp
- 선행: -
- 충돌: -
- 흡수: #369 · RUN-c01
- 비고: 과거 범위 밖·종료 제안은 현행 독립 작업 결정으로 대체됐다. RUN-03의 컨트롤 의미 논의와 실제 저장·복원을 구분한다.

### RUN-02 · #473 결과 항목 조작 오류 수정 묶음을 유지한다
- 종류: DEC | 규모: S | 태그: C
- 목표: #474 표 연결, #475 덮어쓰기 방지, #477 삭제·파일 해석의 구체적 오류 수정을 묶는다. 기존 열린 부모 상태를 유지한다.
- 완료 기준: RUN-10·RUN-11·RUN-12·RUN-13의 범위를 대응시키고 #443·#368·#685 선행을 두지 않는다. 별도 대장·버전 추적·최신성 경고·목록 전용 UI는 제외한다.
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #473 · RUN-c11

### RUN-03 · Reference 줄·Part 콤보·NodeSet 소스 파일의 의미를 확정한다
- 종류: DEC | 규모: S | 태그: C, D
- 목표: 세 컨트롤이 실제로 결정하는 것을 정한다 — (1) Part 콤보가 모핑 대상인가 `_input_geometry.vtu` 추출 대상인가 (현행: 추출 전용, 모핑은 JSON 의 `actualPartName`), (2) 브라우즈한 NodeSet 소스 파일이 콤보 deck 과 다를 때의 정책 (현행: 라벨은 브라우즈 파일, 격자는 deck — 불일치 시 조용히 누락), (3) 빈 경로 게이트 존치 여부 (현행: 조회는 이미 deck 문서로 하고 경로는 검사에만 쓴다).
- 완료 기준: 결정 기록 — 각 컨트롤의 의미 1줄 · 게이트/다이얼로그 존치 여부 · 라벨 문구. 결정이 "다이얼로그 제거 + 게이트 삭제" 면 S PR 1건이 뒤따른다.
- 변경 범위: 결정 기록 (후속 PR 후보: W:updateReferenceFileAndPart · onDatFileEditClicked · M:performMorphing :2382-2415 · ui 라벨)
- 선행: -
- 충돌: PR #654(performMorphing) · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절)
- 흡수: RUN-c02 · RUN-D12 · RUN-c29 · TODO(#559 리뷰 7)
- 비고: #369는 기존 nodeSetSource 저장·경로 처리 설계를 유지하는 독립 작업이다. 이 DEC에서 저장·복원 요구를 취소하거나 #685 완료를 요구하지 않는다.

### RUN-04 · updateModelUploadConfig 가 사용자 DV 값을 model_info 기본값으로 덮지 않게 한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: 실행 직전 계약 파일 기록이 `model_info.json` 을 재파싱해 `m_designVariables` 를 `meta.default` 로 교체하는 것을 멈춘다. Generate 때 `saveInputDesignVariableValues` 가 세운 값이 그대로 `Input Design Variables.value` 에 간다. 재파싱은 메타(min·max·라벨)만 쓰거나 아예 하지 않는다.
- 완료 기준: DV 를 바꿔 Generate → Run 하면 `ModelRunner_{Set}.json` 의 `Input Design Variables.value` 가 화면 값과 같다 · 기존 TestModelRunner 류 통과
- 변경 범위: M:updateModelUploadConfig (:1045 · :1168) · M:loadDesignVariables (:834, 필요 시 값 보존 인자)
- 선행: -
- 충돌: RUN-05 · RUN-17 · RUN-29 (같은 함수) · B2 교집합: DashModelRunner.cpp → 공유 19건(deps.md 5절) · PR #654(DashModelRunner.cpp)
- 흡수: RUN-D26 · RUN-c40
- 비고: #370 "주의" 절이 짚은 조용한 오답의 원인. RUN-06 의 선행

### RUN-05 · ND·1D 동시 체크 실행을 직렬화하고 거절을 통지한다
- 종류: PR | 규모: S | 태그: B, A · bug
- 목표: ND 그룹과 1D 그룹을 한 번의 Run 에서 **순차** 실행한다 — 첫 Job `finished` 뒤 두 번째 그룹의 계약 파일을 쓰고 기동한다. `startPredictionJob` 의 거절(false)은 `runNDPrediction`·`run1DPrediction` 반환값으로 올려 위젯이 모달로 알린다.
- 완료 기준: ND+1D 동시 체크 → 두 결과가 모두 나오고 각 실행 시점의 JSON `Output Response` 가 그 그룹만 가리킨다 · 실행 중 Run 재클릭 → 거절 안내
- 변경 범위: M:startPredictionJob (:186) · runNDPrediction (:1768) · run1DPrediction (:1848) · updateModelUploadConfig(pairs) (:1168) · M.h · W:onRunAIPredictionClicked (:1330-1348)
- 선행: -
- 충돌: RUN-04 · RUN-06 · RUN-29 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashModelRunner.h → RUN-12 RUN-13 RUN-14 RUN-16 RUN-27 RUN-31 RUN-34 · PR #654(DashModelRunner.cpp)
- 흡수: #370-4 · RUN-D23 · RUN-D24 · RUN-c07 · RUN-c38 · #463(RUN 몫 — 예측 재클릭 가드·거절 안내) · EXE-c23 · RUN-c67
- 비고: 대안 — 두 번째 그룹을 거부하고 안내만. 결과 2종을 한 번에 원하는 것이 #370 의 기대 동작이라 직렬화를 택한다. 1D CSV 뷰어 미개방도 이 항목으로 해소

### RUN-06 · 1D 모델은 파일 없는 DV-only 케이스로 Run AI Prediction 을 허용한다
- 종류: PR | 규모: S | 태그: A, D · bug
- 목표: ND 만 파일 케이스 필수. 1D 는 체크된 케이스 중 파일이 빈 DV-only 행을 그대로 Prediction Case 로 싣고(값은 행별 DV), 케이스가 전혀 없으면 dvTable 현재값으로 1건 만들어 실행한다.
- 완료 기준: 1D 모델 · 파일 행 없음 → Run 이 실행되고 CSV 가 열린다 · ND 모델 · 파일 행 없음 → 기존 에러 유지 · DV-only 행의 값이 JSON `Prediction Cases[].values` 에 그대로 간다
- 변경 범위: W:onRunAIPredictionClicked (:1278-1290) · W:collectPredictionCases (:1812) · PM:validatePredictParams (:196)
- 선행: RUN-04
- 충돌: RUN-05 · RUN-13 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunnerPresentationModel.cpp → RUN-10 RUN-11 RUN-12 RUN-15 RUN-17 RUN-29
- 흡수: #370 · RUN-c03
- 비고: Python 1D 경로(`DeepOpt/main.py` test-model-1d)가 `file` 을 로그에만 쓴다는 #370 의 확인을 전제

### RUN-07 · Condition·CAD 생성 경로가 표를 재구축하지 않고 행을 추가한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `refreshFileTableFromDisk()` 호출 2곳을 Morphing 경로와 같은 `createFileTableRow` 행 추가로 바꾼다. 기존 행의 DV 값·체크 상태·Morphing `.vtu` 행이 생성 1회로 사라지지 않는다.
- 완료 기준: Morphing 케이스 A 생성 → Condition(또는 CAD) 케이스 B 생성 → A 행이 남고 A 선택 시 A 의 DV 값이 역주입된다
- 변경 범위: W:onGenerateInputFileClicked Condition 분기 (:591-618) · W:onCadFileReadyForFileTable (:650-676)
- 선행: -
- 충돌: RUN-08 · RUN-09 · RUN-12 (같은 함수) · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절)
- 흡수: #370-1 · RUN-D17 · RUN-c04
- 비고: 경로 일치 행을 선형 탐색하던 코드(:600-616 · :660-676)가 함께 사라진다

### RUN-08 · 정규화 config 파싱 실패 경고를 CAD·Condition 생성 경로에도 낸다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `readModelNormalizationFromConfig` 결과가 `!valid && fileExists` 일 때의 `DashNotify::error` 를 생성 4경로가 공유한다 — 현재는 Morphing·DV-only 2경로에만 있고 CAD·Condition 은 무경고다. 보정 없이 통과하는 값이 사용자에게 보인다.
- 완료 기준: config.yaml 을 깨뜨린 모델로 CAD·Condition 생성 → 같은 경고가 뜬다
- 변경 범위: W:onGenerateInputFileClicked Condition (:596-597 무경고) · W:onCadFileReadyForFileTable (:658-659 무경고) · W:addDvOnlyRowToFileTable (:1674-1683 경고 보유) · W:performMorphingAndAddToFileTable (:1757-1766 경고 보유) — 공통 헬퍼 1개
- 선행: -
- 충돌: RUN-07 (같은 함수) — RUN-07 뒤에 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절)
- 흡수: RUN-D19 · RUN-c35
- 비고: RUN-07 과의 병합 제안(검토 7)은 기각 — 개념이 둘이다 (RUN-07 = 표 재구축으로 사라지는 행 상태, RUN-08 = 깨진 config 의 무경고 통과). 같은 두 함수를 고치는 것은 파일 교집합일 뿐이고 완료 기준·흡수 결함(D17 vs D19)이 갈린다

### RUN-09 · CAD 생성 실패와 Set 전환에서 대기 상태를 정리한다
- 종류: PR | 규모: S | 태그: A, B · bug
- 목표: NX CAD 업데이트 실패 신호를 구독해 `m_pendingCadStpPath`·`m_pendingCadParams` 를 비우고 상태 애니메이션을 멈춘다. `clearAllTables` 도 같은 두 멤버를 비워 이전 Set 의 완료 통지가 새 Set 표에 행을 만들지 못하게 한다. 완료 통지 짝짓기(:643 경로 문자열 비교)는 CAD-01 이 요청 태그를 돌려주면 태그 비교로 바꾼다(RUN-D15 소비측).
- 완료 기준: CAD 업데이트 실패 → 애니메이션 종료 + 에러 안내 + 이후 같은 경로의 완료 통지가 행을 만들지 않는다 · 요청 중 Set 전환 → 완료 통지가 새 Set 표에 반영되지 않는다
- 변경 범위: W:setModel (:259-262 connect) · W:onCadFileReadyForFileTable (:641) · W:clearAllTables (:1599) · W.h
- 선행: - (태그 비교 전환만 CAD-01 뒤 — 그 전엔 현행 경로 문자열 짝짓기 유지)
- 충돌: RUN-07 · RUN-10 (clearAllTables) · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunnerWidget.h → PRJ-25 RUN-15 RUN-28 RUN-29 RUN-30 UIC-24
- 흡수: RUN-D16 · RUN-D36(pending 부분) · RUN-c33 · RUN-c48(일부) · RUN-D15(소비측) · EXE-c42 · RUN-c70
- 비고: 비배치 update 실패가 `loadPrtFailed` 로 나가는 것(controller/DashSolverNxCad.cpp:224)은 CAD 소관 — 신호 이름 정정 전까지는 그 신호를 구독한다. 접점 CAD

### RUN-10 · 예측 산출물 채번을 디스크에서 유도해 재진입·Set 전환 뒤에도 이어간다
- 종류: PR | 규모: S | 태그: A, C · bug
- 목표: 현재 Set 폴더의 기존 결과를 조사해 다음 채번 후보를 얻고 실제 생성 대상 파일의 충돌을 확인한 뒤 생성한다. 재시작·재진입 후 기존 결과를 보존하는 것이 목표이며 프로젝트 전역 카운터는 요구하지 않는다.
- 완료 기준: 재시작·Set 재진입·Set 전환 후 기존 파일 내용 보존. 후보 이름이 이미 존재하면 충돌 없는 대상으로 생성하며 파일 종류별 충돌도 확인한다. 채번 파싱과 실제 파일 충돌 사례를 검증한다.
- 변경 범위: W (생성자 :73 · populateFileTable :1114 · clearAllTables :1599 · 증가 4곳) · PM:predictBaseName (:20) 역파싱 추가 · tests/TestModelRunnerPresentationModel
- 선행: -
- 충돌: RUN-09 · RUN-12 · RUN-13 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunnerPresentationModel.cpp → RUN-06 RUN-11 RUN-15 RUN-17 RUN-29 · TestModelRunnerPresentationModel.cpp → RUN-11 RUN-15 RUN-33
- 흡수: #475 · RUN-D34 · RUN-D36(카운터 부분) · RUN-c15 · RUN-c48(일부)
- 비고: 디스크 최대 번호는 후보 계산 방식이다. 번호 재사용 금지 자체나 영속 카운터 구축을 완료 조건으로 삼지 않는다. RUN-11과 파일 소속·명명 접점만 조율하며 독립 진행 가능하다.

### RUN-11 · 행 삭제 범위를 접두사 매칭에서 정확 매칭으로 바꾼다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: 기존 모듈·산출물 기록의 항목 키로 선택 항목에 속한 파일만 삭제한다. 입력 파일과 프리뷰 파일의 용도를 구분하고 생성 직후와 재열기 후에 같은 항목으로 해석한다.
- 완료 기준: 선택 항목의 입력·프리뷰만 삭제되고 유사 접두 이름의 다른 항목 파일은 보존된다. 생성 직후·재열기 후 동일한 소속 판정과 삭제 결과를 검증한다.
- 변경 범위: PM:relatedFilePathsForDeletion (:40) · tests/TestModelRunnerPresentationModel
- 선행: -
- 충돌: B2 교집합: DashModelRunnerPresentationModel.cpp → RUN-06 RUN-10 RUN-12 RUN-15 RUN-17 RUN-29 · TestModelRunnerPresentationModel.cpp → RUN-10 RUN-15 RUN-33
- 흡수: #477(D21 부분) · RUN-D21 · RUN-c16
- 비고: RUN-12와 최소 항목 키·재열기 식별 기준, RUN-10과 명명·충돌 접점을 공유한다. 별도 UUID·전역 대장을 도입하지 않는다.

### RUN-12 · 파일 표 행과 케이스를 식별자 하나로 결합한다
- 종류: PR | 규모: M | 태그: C, A · bug
- 목표: 케이스 식별자 = 기본 이름(`Predict_NN_{resp}_{model}`, DV-only 포함). 행 `Qt::UserRole` 에 식별자를 두고 `m_fileTableDvValues` 를 식별자 키로, JSON `Prediction Cases` 의 추가·활성·삭제를 식별자 조회로 바꾼다. 행 번호 재키잉·표시 이름 매칭이 사라진다.
- 완료 기준: 중간 행 삭제·정렬 후 콜백·조회·갱신·DV 보조 상태가 같은 데이터 항목을 가리킨다. 재열기 후 RUN-11과 같은 식별 기준을 사용하며 표시 이름 변경에도 결합이 유지된다. 기존 안정 키를 우선 사용하고 별도 UUID·전역 대장을 요구하지 않는다.
- 변경 범위: W:createFileTableRow (:1982) · onFileTableRowSelected (:1229) · 생성 3경로의 DV 기록 · M:appendPredictionCaseToJson (:2666) · updatePredictionCasesActiveStates (:2693) · removePredictionCasesFromJson (:2723) · M.h(PredictionCase 에 id) · PM
- 선행: -
- 충돌: RUN-07 · RUN-13 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashModelRunner.h → RUN-05 RUN-14 RUN-16 RUN-27 RUN-29 RUN-31 RUN-34 · DashModelRunnerPresentationModel.cpp → RUN-06 RUN-11 RUN-15 RUN-17 RUN-29 · PR #654(DashModelRunner.cpp)
- 흡수: #474(RUN 축) · RUN-c12
- 비고: 파일 경로를 키로 쓰면 DV-only 행(파일 없음)이 빠진다 — 기본 이름이 유일 키. DOE-D8 은 LCH, BLD-D10 은 BLD(BLD-c18)

### RUN-13 · 재진입 복원을 디스크 스캔에서 JSON Prediction Cases 읽기로 바꾼다
- 종류: PR | 규모: M | 태그: A · bug
- 목표: `populateFileTable` 이 `ModelRunner_{Set}.json` 의 `Prediction Cases[]`(id · file · values · active) 로 행을 되살리고, 디스크 스캔은 JSON 에 없는 파일의 보충에만 쓴다. 체크 토글은 `syncFileTableToJson` 을 구현해(`updatePredictionCasesActiveStates`) JSON `active` 를 즉시 쓴다. 행 경로는 생성 시 기록한 것(.vtu 포함)이 그대로 복원된다.
- 완료 기준: 케이스 2건(DV 다르게) 생성 · 1건 체크 해제 → 재기동 → 행 2건 · DV 값 각각 · 체크 상태 유지 · Morphing 행 경로가 `.vtu` 그대로 · DV-only 행도 복원
- 변경 범위: W:populateFileTable (:1114) · syncFileTableToJson (:1158) · createFileTableRow · M: `readPredictionCases` 신설 (readConfigFile :554 재사용) · M.h
- 선행: RUN-12
- 충돌: RUN-07 · RUN-10 · RUN-29 (syncFileTableToJson 은 여기서 구현하므로 삭제 대상에서 제외) · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashModelRunner.h → RUN-05 RUN-14 RUN-16 RUN-27 RUN-31 RUN-34 · PR #654(DashModelRunner.cpp)
- 흡수: #477(D35 부분) · RUN-D33 · RUN-D35 · RUN-U1 · RUN-c17 · RUN-c47 · RUN-c51
- 비고: `Output Response`·`Input Design Variables` 의 되읽기(선택 모델·DV 입력값 복원)는 범위 밖 — 별도 feature 로 판단

### RUN-14 · 파라미터 소스 해석을 하나로 모아 혼합 Set 을 전수 판정한다
- 종류: PR | 규모: S | 태그: C, E · bug
- 목표: `getReferenceFileAndPart` 의 첫 매치 `break` 와 `resolveParameterSourceLabel` 의 병행 판정을 파라미터별 결과를 돌려주는 해석기 하나로 바꾼다. Reference 줄·Part 콤보 활성은 전수 결과(형상 소스 존재 여부)로 정하고, `Source` 열은 판정 실패를 `"FE Cond"` 가 아니라 빈 값/`Unknown` 으로 구분한다.
- 완료 기준: Morphing+Condition 혼합 model_info 로 ND Generate → 거짓 거부 없음 · 키 순서를 바꿔도 같은 결과 · `source` 가 깨진 파라미터의 `Source` 열이 FE Cond 와 구분된다 · 단위 테스트 1건
- 변경 범위: M:getReferenceFileAndPart (:1584) · resolveParameterSourceLabel (:887) · loadDesignVariables (:882) · M.h · tests
- 선행: -
- 충돌: RUN-27 · RUN-25 · B2 교집합: DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashModelRunner.h → RUN-05 RUN-12 RUN-13 RUN-16 RUN-29 RUN-31 · PR #654(DashModelRunner.cpp)
- 흡수: #370-2 · RUN-D8 · RUN-D9 · RUN-c05 · RUN-c26

### RUN-15 · ND 판정 규칙을 하나로 한다
- 종류: PR | 규모: M | 태그: C · bug
- 목표: ND 판정의 정본을 **응답 속성**(model_info 의 응답 표시 이름에 실린 `(Field)`)으로 확정하고, 응답 표시 이름을 받는 술어 1개를 `DashSurrogateModelCommon` 에 둔다. 모델 이름 접두사 판정(`isNDModel`)은 RUN 에서 걷어낸다. 보이는 열(헤더·행 지표)과 타는 경로(생성 분기·예측 그룹)가 어긋나지 않는다.
- 완료 기준: (1) RUN 파일과 `view/common/SurrogateTableController.cpp` 에 `contains("(Field)")` 직접 판정 0건 — 전부 공용 술어 호출 (2) 응답에 `(Field)` 가 있고 모델 이름이 `ndModelNames()` 밖인 model_info(또는 반대)에서 헤더·행 지표·생성 분기·예측 그룹이 같은 판정 (3) `DashSurrogateModelCommon::isNDModel` 삭제 — RUN 밖 호출처 0 (`ndModelNames()` 는 BLD 가 쓰므로 남긴다) (4) 술어 단위 테스트 1건 (RUN-33 TU)
- 변경 범위: W:populateSurrogateTable (:962) · updateTableHeadersForModelType (:822) · `isNDModel` 래퍼 (:817 삭제) · 모델 이름 판정 호출부 2곳 (:536 Condition 분기 거절 · :624 Unknown 폴백) · W.h (:105) · view/common/SurrogateTableController.cpp:createRow (:29 — RUN 전용 표 컨트롤러) · viewmodel/DashSurrogateModelCommon.cpp/.h (:93 `isNDModel` 삭제 · 응답 술어 신설 · `ndModelNames` :73 유지) · PM:groupCheckedPairs (:64) · tests/TestModelRunnerPresentationModel (RUN-33)
- 선행: -
- 충돌: RUN-25 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunnerPresentationModel.cpp → RUN-06 RUN-10 RUN-11 RUN-12 RUN-17 RUN-29 · DashModelRunnerWidget.h → PRJ-25 RUN-09 RUN-28 RUN-29 RUN-30 UIC-24 · TestModelRunnerPresentationModel.cpp → RUN-10 RUN-11 RUN-33
- 흡수: RUN-D6 · RUN-c24
- 비고: 정본 확정 — decisions ⑦ 의 "한 규칙으로" 를 코드 근거로 닫는다. ① Model Builder 가 `(Field)` 를 `baseDim == 3 && reduction == "None"` 에서 붙이고(`viewmodel/DashModelBuilderPresentationModel.cpp:174`) 같은 술어가 `effectiveModelDimension`(:188) 의 `isND` 다. 그 표시 이름이 `getOutputResponseList`(`view/DashModelBuilderWidgetBase.cpp:299`) → `Output Response` → model_info `errors` 키로 간다 — 즉 `(Field)` 는 **학습 시점에 기록된 ND 결정**이다. ② 모델 이름 목록 `ndModelNames()` 5건은 Model Builder 가 실제 제공하는 3D 모델 `DashModelBuilder::getModelsForDimension(3)` = `{"StableNet"}` 1건과 이미 어긋난 중복이라 정본이 아니다. ③ 전환에 배선 추가가 없다 — `GenerateInputFileParams::responseText` · `CheckedModelRow::responseText` 가 이미 응답 표시 이름을 들고 있다. 귀속 — `SurrogateTableController` 는 RUN·BLD·OPT 공용이 아니라 **RUN 전용**이다(소비자는 `DashModelRunnerWidget`·`DashModelRunnerMCUWidget` 2곳뿐, 전수 grep) → 다툼 없이 RUN-15 가 맡고 OPT-10 은 파일 교집합 없이 `선행: RUN-15` 로 술어만 소비한다(충돌 아님). `(Field)` 판정은 5곳이 아니라 **6곳**(+ 생산 1곳) — RUN W:962 · SurrogateTableController.cpp:29 / BLD DashModelBuilderWidget.cpp:1089·:1681 / OPT DashOptimizerWidget.cpp:556·:867 / 생산 DashModelBuilderPresentationModel.cpp:178. BLD 에는 대응 항목이 없어 BLD 2곳은 이 항목 밖(접점 BLD — 술어가 생기면 호출로 바꿀 자리). `DashModelRunnerMCUWidget::isNDModel`(:868)은 `return false` 상수 스텁에 호출처 0 — RUN-29 몫

### RUN-16 · DV 스핀박스 범위와 초기값 규칙을 바로잡는다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: 상한을 `max` 그대로 두고(Max 열과 같은 값 입력 가능), 미설정 판정을 `value != 0.0` 대신 "저장값 존재" 로 한다 — 정확히 0.0 인 DV 가 중앙값으로 바뀌지 않는다.
- 완료 기준: Max 값을 그대로 입력할 수 있다 · DV 0.0 저장 후 재진입 → 0.0 유지
- 변경 범위: W:populateDesignVariableTable (:1096-1106) · DesignVariableInfo(M.h) 에 설정 여부 또는 `std::optional`
- 선행: -
- 충돌: RUN-17 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunner.h → RUN-05 RUN-12 RUN-13 RUN-14 RUN-27 RUN-29 RUN-31 RUN-34
- 흡수: RUN-D11 · RUN-c28

### RUN-17 · 설계변수 값의 정본을 셀 위젯에서 모델로 옮긴다
- 종류: PR | 규모: M | 태그: E, A · refactor
- 목표: 스핀박스 `valueChanged` → `DashModelRunner::setDesignVariableValue` 결선. `collectSurrogateSelection`·Download·Generate 가 표를 폴링하지 않고 모델을 읽는다. 모델만 바꾸는 경로가 있어도 화면·저장이 갈리지 않는다.
- 완료 기준: 동작 불변 — Generate·Download·Run 결과가 이전과 같다 · `cellWidget(` 로 스핀박스를 읽는 곳 0
- 변경 범위: W:populateDesignVariableTable · collectSurrogateSelection (:1856) · collectDvRows · onDvUploadButtonClicked · M (setter·신호) · PM
- 선행: RUN-04 (모델이 값을 덮지 않아야 정본이 성립)
- 충돌: RUN-16 · RUN-29 (`designVariablesChanged` 신호 — RUN-29 가 지우면 여기서 재도입) · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashModelRunnerPresentationModel.cpp → RUN-06 RUN-10 RUN-11 RUN-12 RUN-15 · PR #654(DashModelRunner.cpp)
- 흡수: RUN-D10 · RUN-c27

### RUN-18 · DV 치환값의 유효숫자 절삭을 없앤다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `QString::number(it.value())`(M:1717) 의 기본 포맷 'g'·유효숫자 6자리 절삭을 없앤다 — `QString::number(v, 'g', 17)` 또는 입력 자릿수 유지로 쓴다. **토큰 경계는 건드리지 않는다** — 치환 토큰이 닫는 `}` 를 포함한 완전 일치(M:1716 `QString("${%1}").arg(key)`)라 접두사 충돌·`QMap` 순서 의존이 애초에 없다.
- 완료 기준: `0.1234567` 을 넣은 DV 가 `.dat` 에 6자리로 잘리지 않고 그대로 간다 · 단위 테스트 1건
- 변경 범위: M:generateDatFile (:1715-1718) · tests
- 선행: -
- 충돌: B2 교집합: DashModelRunner.cpp → 공유 19건(deps.md 5절) · PR #654(DashModelRunner.cpp)
- 흡수: RUN-D18 · RUN-c34
- 비고: 결함 색인 RUN-D18 의 "치환 순서에 달린다" 절반은 무효 (검토 5) — `${L}` 은 `${L1}` 의 부분문자열이 아니다. 정규식 토큰화는 하지 않는다

### RUN-19 · 1D 결과 CSV 선택을 고정 지연·최신 파일에서 결정적 규칙으로 바꾼다
- 종류: PR | 규모: S | 태그: B · bug
- 목표: `singleShot(500)` 을 없애고 Job `finished`(프로세스 종료) 시점에 "실행 시작 시각 이후 생성·수정된 CSV" 를 고른다. 쓰기가 늦어도 놓치지 않고 이전 결과를 최신으로 오인하지 않는다.
- 완료 기준: 두 번 연속 1D 예측 → 각각 자기 CSV 가 열린다 · 결과 파일이 없으면 안내 · ND 경로(VTU 자동 렌더)는 무영향
- 변경 범위: W:onRunAIPredictionClicked (시작 시각 기록) · onPredictionSucceeded (:1352-1399)
- 선행: -
- 충돌: RUN-05 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절)
- 흡수: RUN-D27 · RUN-c41 · EXE-c38 · RUN-c62
- 비고: DeepOpt 가 출력 파일명을 고정 규약으로 낸다면 그 경로를 직접 연다 — 규약 확인 뒤 택일. RUN-20 과의 병합 제안(검토 8)은 기각 — 개념이 둘이다 (RUN-19 = 1D CSV 를 고르는 타이밍·경쟁, RUN-20 = ND 렌더 대상 선택 정책). 같은 두 함수를 고치는 것은 파일 교집합

### RUN-20 · 예측 완료 자동 렌더 대상을 정한다
- 종류: PR | 규모: S | 태그: D · bug
- 목표: 마지막 케이스 고정 대신 "선택된 행이 체크 케이스면 그 행, 아니면 첫 체크 케이스" 를 렌더한다.
- 완료 기준: 케이스 3건 체크 · 2번째 행 선택 → 2번째 결과가 렌더 · 선택 없음 → 1번째
- 변경 범위: W:onRunAIPredictionClicked (:1320) · onPredictionSucceeded (:1400-1405)
- 선행: -
- 충돌: RUN-05 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절)
- 흡수: RUN-D25 · RUN-c39

### RUN-21 · Set 불일치 방어가 최초 진입에서도 돌게 한다
- 종류: PR | 규모: S | 태그: A · bug
- 목표: `onSurrogateCheckBoxChanged` 의 `&& !currentSetName.isEmpty()` 예외를 없애고, Set 이름이 비어 있으면 표를 비우거나 체크를 거부한다.
- 완료 기준: 새 세션 최초 진입에서 다른 Set 폴더의 모델을 체크 → 이전 파일 표가 남지 않는다
- 변경 범위: W:onSurrogateCheckBoxChanged (:1006-1013)
- 선행: -
- 충돌: B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절)
- 흡수: RUN-D38 · RUN-c50

### RUN-22 · 민감도 패널 진입 시 MCU Set 이름에 접미사를 다시 붙이지 않는다
- 종류: PR | 규모: S | 태그: C · bug
- 목표: `MW:setModel` 이 이미 `-MCU` 로 끝나는 Set 이름에 `+ "-MCU"` 를 붙여 `ModelBuilder_Set1-MCU-MCU` 를 찾게 하던 것을 Set 이름 그대로 넘긴다 (MCU Set 이름은 model/DashProject.cpp:1080·:1095 가 이미 접미사를 붙인다).
- 완료 기준: MCU Set 진입 → 민감도 패널 콤보가 `ModelBuilder_{Set}` 을 선택한다 (`-MCU-MCU` 탐색 없음)
- 변경 범위: MW:setModel (:177)
- 선행: -
- 충돌: B2 교집합: DashModelRunnerMCUWidget.cpp → UIC-20 UIC-23
- 흡수: RUN-D37 · RUN-c49
- 비고: 매치 실패 시 0번 폴백(RUN-D30 · RUN-c44)은 변경 파일이 AW 뿐이라 ANA-06 으로 이관. 변수 목록 원천(RUN-D29 · RUN-c43, 구 RUN-23)도 ANA-18 로 이관 — RUN-23 은 삭제(번호 결번)

### RUN-24 · 결과 열람의 VTU 중복 파싱을 없앤다
- 종류: PR | 규모: S | 태그: B · perf
- 목표: `checkFieldExistsInVtu` 가 존재 확인만을 위해 VTU 를 다시 읽지 않는다 — 한 번 읽은 데이터에서 필드 유무를 보고 그 데이터를 렌더에 넘긴다.
- 완료 기준: 열람 1회당 같은 VTU 읽기 1회 (로그 또는 카운터로 확인) · 렌더 결과 불변
- 변경 범위: W:performPreviewLogic (:1448-1557) · checkFieldExistsInVtu (:1558)
- 선행: -
- 충돌: RUN-28 · UIC-24 (같은 함수 `performPreviewLogic` W:1448 — UIC-24 가 시그니처에서 죽은 `row` 인자를 뺀다) · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절)
- 흡수: RUN-D5(열람 축) · RUN-c23
- 비고: 순서 — **UIC-24 가 먼저** (decisions ⑦). 시그니처 정리 뒤에 본문을 재작성한다

### RUN-25 · 폴더 선택 스캔을 워커로 옮긴다
- 종류: PR | 규모: M | 태그: B · perf
- 목표: 폴더 열거 · `model_info.json` 파싱 · 메트릭 조회 · DV 별 GeometryParameter JSON 파싱을 `DashAsyncJobRunner`(#544) 작업 1건으로 묶어 결과 구조체를 GUI 로 넘기고, 위젯은 받은 구조체로 표 3종을 채운다. 진행 중 상태 표시. `model_info.json` 은 1회만 읽는다.
- 완료 기준: 폴더 선택 중 창이 응답한다 · 같은 폴더 선택 1회에 `model_info.json` 읽기 1회 · 진행 중 Generate/Run 비활성 · 표 내용 불변
- 변경 범위: W:populateModelBuilderFolderComboBox (:782) · populateSurrogateTable (:844) · onModelDataLoaded (:389) · M:getModelBuilderFolders (:1335) · loadModelInfoFromFolder (:1379) · loadDesignVariables (:834) · view/common/SurrogateTableController.cpp:updateModelErrorRow (:98)
- 선행: RUN-14
- 충돌: RUN-17 · RUN-27 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절) · SurrogateTableController.cpp → RUN-15 · PR #654(DashModelRunner.cpp)
- 흡수: #513 · RUN-D5(적재 축) · RUN-c08 · #463(RUN 몫 — 적재 진행 표시·버튼 비활성) · EXE-c23 · RUN-c67
- 비고: deck 파싱(`registry.load`) 몫은 EXE #458(RW 액터 스레드 이주) 이후 자동으로 워커로 간다 — 이 항목은 JSON·폴더 축만. MCU 경로는 비범위(#513). 진행 표시·버튼 비활성·반려 안내는 EXE-07 규약과 EXE-09 `DashJobGuard` 가 있으면 그것으로 — 없으면 현행 상태 애니메이션

### RUN-26 · variant 정본을 JSON 키 하나로 한다
- 종류: PR | 규모: S | 태그: C · bug
- 목표: `writeConfigFile` 이 Set 이름 접미사로 `variant` 를 매번 덮지 않는다 — 기존 키가 있으면 유지, 없을 때(생성 시)만 기록. `detectRunnerVariant` 의 이름 접미사 폴백은 키 부재 파일이 더 없음을 확인한 뒤 제거한다.
- 완료 기준: JSON `variant` 를 손으로 바꿔도 저장이 되돌리지 않는다 · 신규 Set 생성 시 키가 기록된다
- 변경 범위: M:writeConfigFile (:576-599) · model/DashProject.cpp:detectRunnerVariant (:976)
- 선행: -
- 충돌: B2 교집합: DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · PR #654(DashModelRunner.cpp) · PR #652(DashProject.cpp) · PR #651(DashProject.cpp)
- 흡수: RUN-D2 · RUN-c20
- 비고: 접점 PRJ. 폴백 제거 여부는 기존 프로젝트 파일 조사 뒤 — 하위호환 분기를 쌓지 않는다

### RUN-27 · view-source 컨텍스트 폴백 접근자를 하나로 만들고 `configsDir` 삼항을 지운다
- 종류: PR | 규모: S | 태그: E · refactor
- 목표: `m_viewSourceContext.X.isEmpty() ? m_runtimeContext.X : m_viewSourceContext.X` 반복을 `viewSource()` 접근자 하나로, Set 무관 전역인 `configsDir` 은 RuntimeContext 에서 빼고 `getConfigsDirectory()` 직접 호출로 바꾼다.
- 완료 기준: 동작 불변 · 삼항 폴백 0건 · `RuntimeContext::configsDir` 삭제
- 변경 범위: M:calculateRuntimeContext (:476) · resolveParameterSourceLabel (:898) · getReferenceFileAndPart (:1593) · performMorphing (:2219) · readModelNormalizationFromConfig (:2487) · M.h RuntimeContext
- 선행: PR #654 (같은 함수 적용 순서)
- 충돌: RUN-14 · RUN-25 · B2 교집합: DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashModelRunner.h → RUN-05 RUN-12 RUN-13 RUN-16 RUN-29 RUN-31
- 흡수: RUN-D7 · RUN-c25

### RUN-28 · 뷰의 MainWindow 부모 탐색·findChild·QMessageBox 결합을 걷어낸다
- 종류: PR | 규모: M | 태그: E, D · refactor
- 목표: `DashMainWindow` 를 부모 거슬러 찾는 4벌을 상태 애니메이션·CSV 뷰어·STEP 프리뷰 요청 신호(또는 주입된 인터페이스 1개)로 바꾸고, `findChild<` 5곳을 멤버 포인터로, 남은 `QMessageBox::` 7곳을 `DashNotify` 로 통일한다.
- 완료 기준: W 에서 `qobject_cast<DashMainWindow*>` 0 · `findChild<` 0 · `QMessageBox::` 0 · 동작 불변
- 변경 범위: W (:433-439 · :1383 · :1469 · :1550 · findChild 5곳 · QMessageBox 7곳) · W.h · view/DashMainWindow (신호 수신 결선)
- 선행: -
- 충돌: RUN-24 (performPreviewLogic) · UIC-17 (통지 래퍼) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunnerWidget.h → PRJ-25 RUN-09 RUN-15 RUN-29 RUN-30 UIC-24 · PR #655(DashMainWindow.cpp) · PR #654(DashMainWindow.cpp) · PR #652(DashMainWindow.cpp) · PR #651(DashMainWindow.cpp)
- 흡수: RUN-D28 · RUN-c42
- 비고: 접점 PRJ(MainWindow) · UIC(통지). 다른 모듈 위젯에도 같은 패턴이 있으면 Phase B 에서 횡단 항목으로 승격 가능

### RUN-29 · Model Runner 의 죽은 코드를 지운다
- 종류: PR | 규모: M | 태그: E · refactor
- 목표: 호출처 0 인 정의 14종, 수신처 0 인 신호 4종, 도달 불가 `fileTableFiles` 와 1-인자 `updateModelUploadConfig`, `runFESolver` 전용 멤버·헤더를 삭제한다.
- 완료 기준: 빌드·테스트 통과 · 삭제 목록 — M: onPredictButtonClicked · onResponseSurfaceButtonClicked · runFESolver(+`m_ansysLauncher`·`m_abaqusLauncher`·cae-launcher include) · savePartAsVtu · getXmlFiles · getModelList · getAvailableResponses · initializeSetConfig · getRuntimeContextForSet · updateSelectedModel(+`surrogateModelUpdated`) · 신호 `designVariablesChanged`·`surrogateModelsChanged`·`fileTableUpdated` · 1-인자 updateModelUploadConfig. W: onDeleteButtonClicked · populateAllWidgets · updateDesignVariablesFromModelInfo · syncAnalysisInputFilesToJson. PM: `fileTableFiles`
- 변경 범위: M.cpp/.h · W.cpp/.h · PM.cpp/.h
- 선행: -
- 충돌: RUN-04 · RUN-05 (updateModelUploadConfig) · RUN-13 (`syncFileTableToJson` 은 구현 대상이라 제외) · RUN-17 (`designVariablesChanged` 재도입 가능) · PR #654 · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashModelRunner.h → RUN-12 RUN-14 RUN-16 RUN-27 RUN-31 RUN-34 · DashModelRunnerPresentationModel.cpp → RUN-06 RUN-10 RUN-11 RUN-12 RUN-15 · DashModelRunnerWidget.h → PRJ-25 RUN-09 RUN-15 RUN-28 RUN-30 UIC-24
- 흡수: RUN-U2 · RUN-U3 · RUN-U4 · RUN-U5 · RUN-U6 · RUN-c52 · RUN-c53 · RUN-c54 · RUN-c55 · RUN-c56
- 비고: `onDeleteButtonClicked`(체크 행 일괄 삭제)를 기능으로 원하면 별도 feature — 지금은 삭제. `runFESolver` 는 FE 실행 버튼이 없고 #653 이 Direct Launch 로 같은 요구를 덮는다

### RUN-30 · Model Runner 에 FE Validation 버튼을 두고 Direct Launch 다이얼로그에 입력을 채워 연다
- 종류: PR | 규모: M | 태그: B, D · feature
- 목표: 버튼 클릭 → 현재 Set 의 입력 파일(체크된 케이스 1건 또는 선택 행)·Target Part·출력 폴더 `{ModelRunner_{Set}}/FEValidation/` 을 다이얼로그 `prefill(inputPath, targetPart, outputFolder)` 로 넘겨 Launcher 페이지로 연다. Done 뒤 Result Preview 자동 선택과 Direct↔Analysis Launcher 상호 배제는 #604 동작 그대로.
- 완료 기준: 버튼으로 연 다이얼로그에 세 값이 채워져 있다 · 실행 Done 뒤 Result Preview 가 열린다 · 입력 파일 생성은 이 버튼이 하지 않는다
- 변경 범위: W.cpp/.h · ui/DashModelRunnerWidget.ui · view/dialog/DashDirectLaunchDialog.cpp/.h (PR #652 의 파일 — `prefill` 진입점 신설)
- 선행: #604 (PR #652) 머지
- 충돌: RUN-28 (MainWindow 접근) · OPT-21 (같은 버튼 — prefill 진입점 공용, 먼저 머지되는 쪽이 만든다) · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunnerWidget.h → PRJ-25 RUN-09 RUN-15 RUN-29 UIC-24 · DashDirectLaunchDialog.cpp → LCH-19
- 흡수: #653(RUN 축) · RUN-c18
- 비고: 접점 LCH(다이얼로그) · OPT(동형 버튼 — RUN-c19 범위밖). 결과 처리(Set 설정으로 KPI) 는 #433 뒤 별도

### RUN-31 · Runner가 실제 사용한 Builder 산출물 버전으로 최신성을 판정한다
- 종류: PR | 규모: M | 태그: C, A · feature
- 목표: #650 규칙으로 실제 실행에 사용한 Builder setId와 모델 버전을 기록하고 DashModelRunner::upstreamStaleReasons가 현재 생산 버전과 비교한다. Builder 참조 저장·복원·개명 해석은 RUN-34(#685) 계약을 사용한다.
- 완료 기준: 실제 사용 버전 기록·왕복, 동일 Builder 재학습 후 최신성 사유, 버전 누락·비교 불가의 PRJ-23 규칙 적용. 참조 선택만 바꿀 때 기존 결과의 출처·소비 버전은 불변이며 프로젝트 집계·VM 표시로 전달한다.
- 변경 범위: model/DashModelRunner.h (RuntimeContext · 소비 버전 기록), model/DashModelRunner.cpp (calculateRuntimeContext :476-500 · loadModelInfoFromFolder :1379-1440 · writeConfigFile 호출), (PRJ 소관) model/DashProject.cpp refreshUpstreamStaleness 쌍 추가
- 선행: BLD-18 · PRJ-23
- 충돌: RUN-14 · RUN-25 · RUN-27 (loadModelInfoFromFolder) · RUN-26 · RUN-32 (writeConfigFile) · B2 교집합: DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashProject.cpp → 공유 14건(deps.md 5절) · DashModelRunner.h → RUN-05 RUN-12 RUN-13 RUN-16 RUN-29 · PR #654(DashModelRunner.cpp) · PR #652(DashProject.cpp) · PR #651(DashProject.cpp)
- 흡수: #650(RUN 몫) · PRJ-c37 · RUN-c58
- 비고: RUN-34와 공통 저장 경로를 조율하되 조합 핀이나 setId+이름 fallback을 도입하지 않는다. PRJ-22는 Set 판정을 호출·집계하며 VM은 표시만 한다. 참조·출처 유효성과 최신성 판정은 별개다.

### RUN-32 · writeConfigFile·readConfigFile 을 DashSaveSystem 헬퍼로 이행한다
- 종류: PR | 규모: S | 태그: A · refactor
- 목표: `M:writeConfigFile`(:576-620 — `QFile` WriteOnly+Truncate · flush·길이 검사 직접 구현, 원자성 없음) 본문을 PER-02 가 공용 진입점으로 승격하는 **DashSaveSystem 헬퍼**(`DashSaveSystem::writeJsonFile`, `persistence/DashSaveSystem.h:59`) 호출로, `readConfigFile`(:554) 을 `readJsonFile`(:60) 로 바꾼다. 호출 9곳(:1082·:1158·:1192·:1250·:1332·:2473·:2690·:2720·:2744)과 RUN-34 의 참조 저장 호출은 시그니처 그대로. QSaveFile 원자성·0바이트/손상 구분·사유 반환·(PER-04 뒤) 버전 키가 따라온다.
- 완료 기준: M.cpp 에 `QIODevice::WriteOnly` 가 generateDatFile(:1748 .dat 산출물) 1곳뿐 / 쓰기 실패(읽기 전용 경로) 시 기존 JSON 바이트 동일 + WARN 사유 / 기존 저장·복원 동작 불변
- 변경 범위: model/DashModelRunner.cpp (writeConfigFile :576 · readConfigFile :554)
- 선행: PER-02
- 충돌: RUN-26 (writeConfigFile variant 분기) · RUN-13 (readConfigFile 재사용) · RUN-31 · RUN-34 (writeConfigFile 호출 추가) · B2 교집합: DashModelRunner.cpp → 공유 19건(deps.md 5절) · PR #654(DashModelRunner.cpp)
- 흡수: #479(RUN 몫) · #478(RUN 몫) · #480(RUN 몫) · PER-c28 · RUN-c64
- 비고: 신설 `utils/DashJsonFile` 은 중복이라 폐기 — PER-02 가 기존 `DashSaveSystem::read/writeJsonFile`(QSaveFile · Result 반환 · 테스트 보유)을 공용 진입점으로 승격한다 (decisions 3절)

### RUN-33 · Model Runner PM 순수 함수에 단위 테스트 타깃을 둔다
- 종류: PR | 규모: S | 태그: F · refactor
- 목표: `tests/` 의 `DashModelRunner` 언급은 TestProcessRuntime 의 모듈명 문자열뿐(#489 · DEV-c24) — RUN-10 · RUN-11 이 전제한 `tests/TestModelRunnerPresentationModel.cpp` 가 없다. PM 순수 함수(`predictBaseName` · `relatedFilePathsForDeletion` · `groupCheckedPairs` · `validatePredictParams`)와 `viewmodel/DashSurrogateModelCommon::isNDModel` 을 TU 1개로 고정한다.
- 완료 기준: tests/CMakeLists.txt 에 `test_model_runner_presentation_model` 등록 · ctest 통과 / RUN-10 · RUN-11 · RUN-15 · RUN-18 의 테스트 완료 기준이 이 TU 에 들어간다
- 변경 범위: tests/CMakeLists.txt, tests/TestModelRunnerPresentationModel.cpp (신규)
- 선행: -
- 충돌: RUN-10 · RUN-11 · RUN-14 · RUN-15 · RUN-18 (고정하는 동작 — 먼저 쓰고 각 PR 이 갱신) · DEV 의 tests 인프라 항목 · B2 교집합: tests/CMakeLists.txt → 공유 12건(deps.md 5절) · PR #655(tests/CMakeLists.txt) · PR #654(tests/CMakeLists.txt) · PR #652(tests/CMakeLists.txt) · PR #651(tests/CMakeLists.txt)
- 흡수: #489(RUN 몫) · DEV-c24(RUN) · RUN-c71
- 비고: `DashModelRunner` 본체는 `DashProjectManager::Instance()` 역참조 — 모델 함수(generateDatFile 치환 등)는 경로 주입(PRJ-09) 뒤. CAD-11 · OPT-20 과 같은 형태

### RUN-34 · Runner가 Builder를 setId로 참조하고 출처 검증 후 실행·조회·프리뷰에 사용한다 (#685)
- 종류: PR | 규모: S | 태그: C, A · feature
- 목표: #685의 소비 경계에서 Builder setId와 응답·모델·part 등 선택을 ModelRunner_{Set}.json에 저장·복원한다. #368의 공통 판독으로 Builder 산출물 출처를 검증하고 deck은 산출물 기록에서 해석한다. 현재 Runner Set의 ID를 유지하면서 다른 Builder를 선택할 수 있으며 외부 실행에는 ID로 해석한 실제 경로를 전달한다.
- 완료 기준: ① Builder 개명 후 동일 setId 참조 복원, 동명 재생성의 다른 setId와 구분 ② 다른 유효 Builder 선택·실행 가능 ③ 선택 변경만으로 기존 결과 출처 불변, 재실행 결과 덮어쓰기 때 실제 출처 갱신 ④ 필수 출처 누락·해석 불가 model_info는 재생성 안내, live parameter·이름·경로 추론 fallback과 자동 이관 금지 ⑤ 실행·조회·프리뷰가 같은 검증된 선택과 deck을 사용 ⑥ MCU 등 deck 비해당 유형은 공통 계약의 적용 관계로 판정하고 필수 출처 검증을 일괄 면제하지 않음.
- 변경 범위: model/DashModelRunner.cpp · model/DashModelRunner.h · view/DashModelRunnerWidget.cpp
- 선행: BLD-20 (#368 생산·공통 계약 완료)
- 충돌: RUN-14 · RUN-25 · RUN-27 · RUN-31 (`getReferenceFileAndPart`·`loadModelInfoFromFolder`) · RUN-32 (`writeConfigFile` 호출 추가) · B2 교집합: DashModelRunnerWidget.cpp → 공유 29건(deps.md 5절) · DashModelRunner.cpp → 공유 19건(deps.md 5절) · DashModelRunner.h → RUN-05 RUN-12 RUN-13 RUN-16 RUN-29 · PR #654(DashModelRunner.cpp)
- 흡수: #685 (구 #368 T23 RUN 소비 몫) · #443 SI-6a ②(RUN 참조 축) · PRJ-c04(RUN 축) · RUN-c59 · RUN-c57 · LCH-c38
- 비고: PR #530은 당시 재업로드 결정 기록이며 옛 조합 ID 핀 코드를 그대로 이식하지 않는다. 생산 계약은 PER-07·BLD-20에서 재사용한다. #650 버전·최신성과 #473 결과 조작은 별도 목표이고 #681 머지 조건으로 두지 않는다. #513 워커 이관과는 공유 코드 순서만 조율하며 별도 영속 참조 체계를 만들지 않는다. 공통 검증 테스트와 Set 참조 왕복·프리뷰 수동 검증을 병행한다.

## 대응표

| 원천 | 항목 | 비고 |
|---|---|---|
| #369 | RUN-01 (PR) · RUN-03(컨트롤 논의) | nodeSetSource 저장·복원 독립 작업. #443·#368·#685 선행 없음 |
| #370 | RUN-06 (본건) · RUN-07 (부수1) · RUN-14 (부수2) · RUN-05 (부수4) | 부수3 해소됨 (198a294c) · ← UIC-c40 (RUN-c65) |
| #513 | RUN-25 | — |
| #458 (B2 에서 담당 EXE) | → EXE-22 · LCH-12(#458-b) | 범위밖 — deck 파서 워커는 EXE(DashRwActor 이주), dfsxml ProcessJob 수렴은 LCH. RUN 소비측은 이미 co_await |
| #473 | RUN-02 (DEC) · RUN-10~13 | 표 연결·덮어쓰기 방지·삭제 정합 묶음 유지, 참조 전환과 독립 |
| #474 | RUN-12 (식별자 결합) · UIC-24 (RUN-D22 — 행 번호 캡처) · UIC-23 (BLD-D10) · LCH (DOE-D8) | 원 항목 C4a = DOE-D8 · RUN-D22 · BLD-D10 (검토 10) |
| #475 | RUN-10 | — |
| #477 | RUN-11 (D21) · RUN-13 (D35) | — |
| #653 | RUN-30 | Optimizer 버튼 → OPT |
| RUN-D1 | 항목 없음 | 범위밖 → PRJ (`m_categoryWidgetMap` 죽은 코드 · RUN-c72). 결함 색인에 D1 행이 빠져 전 모듈 누락이었다 (검토 9) — 보류: PRJ 몫 (PRJ-19 등재) |
| RUN-D2 | RUN-26 | — |
| RUN-D3 | 항목 없음 | 해소됨 0894cac9(#437) · ← EXE-c36 (RUN-c61) |
| RUN-D4 | 항목 없음 | 해소됨 0e6b4994(#436) |
| RUN-D5 | RUN-25 (적재) · RUN-24 (열람) | deck 파서 축 → EXE #458 |
| RUN-D6 | RUN-15 | — |
| RUN-D7 | RUN-27 | — |
| RUN-D8 | RUN-14 | ← UIC-c58 (RUN-c68) |
| RUN-D9 | RUN-14 | — |
| RUN-D10 | RUN-17 | — |
| RUN-D11 | RUN-16 | — |
| RUN-D12 | RUN-03 (DEC) | — |
| RUN-D13 | 항목 없음 | 해소됨 c9c9dedb(#403) |
| RUN-D14 | 항목 없음 | 해소됨 c9c9dedb(#403) · ← REN-c33 (RUN-c69) |
| RUN-D15 | CAD-01 (파사드) · RUN-09 (소비측 짝짓기) | 범위밖 → CAD (#452 기각 기록) · ← EXE-c42 (RUN-c70). CAD-01 흡수에 RUN-D15 등재 확인(B2) |
| RUN-D16 | RUN-09 | — |
| RUN-D17 | RUN-07 | — |
| RUN-D18 | RUN-18 | — |
| RUN-D19 | RUN-08 | — |
| RUN-D20 | 항목 없음 | 해소됨 (적재 await 후 선택 · isNodeSetPart 삭제) |
| RUN-D21 | RUN-11 | — |
| RUN-D22 | 항목 없음 | 범위밖 → UIC #514 Phase 4 (죽은 인자, 실해 없음) |
| RUN-D23 | RUN-05 | — |
| RUN-D24 | RUN-05 | — |
| RUN-D25 | RUN-20 | ← UIC-c58 · REN-c33 (RUN-c68 · c69) |
| RUN-D26 | RUN-04 | — |
| RUN-D27 | RUN-19 | ← EXE-c38 (RUN-c62) |
| RUN-D28 | RUN-28 | — |
| RUN-D29 | → ANA-18 | RUN-23 이관 (삭제) — 변경 파일이 AW(ANA) 뿐 |
| RUN-D30 | → ANA-06 | RUN-22 의 AW 몫 이관 — MCU 접미사(D37)만 RUN-22 잔류 |
| RUN-D31 | 항목 없음 | 해소됨 0e6b4994(#436) 진입마다 캐시 폐기 |
| RUN-D32 | 항목 없음 | 해소됨 0e6b4994(#436) 요청 id 표 · ← EXE-c35 (RUN-c60) |
| RUN-D33 | RUN-13 | — |
| RUN-D34 | RUN-10 | — |
| RUN-D35 | RUN-13 | — |
| RUN-D36 | RUN-10 (카운터) · RUN-09 (pending) | — |
| RUN-D37 | RUN-22 | — |
| RUN-D38 | RUN-21 | — |
| RUN-U1 | RUN-13 | 구현 (삭제 아님) |
| RUN-U2 | RUN-29 | — |
| RUN-U3 | RUN-29 | — |
| RUN-U4 | RUN-29 | — |
| RUN-U5 | RUN-29 | RUN-17 이 필요 시 재도입 |
| RUN-U6 | RUN-29 | 잔여 14종 (PM 3종은 이미 삭제됨) |
| #685 (소비 · RUN 몫) | RUN-34 | Builder setId 참조·공통 출처 검증·실행·조회·프리뷰. 선행 BLD-20(#368) |
| #650 (RUN 몫) | RUN-31 | 실제 사용 버전 판정, 생산은 BLD-18. Set 참조는 RUN-34(#685) |
| #479 · #478 · #480 (RUN 몫) | RUN-32 | ← PER-c28 (RUN-c64) |
| #478 부록 A (RUN 5건 D24·D26·D33·D34·D35) | RUN-05 · RUN-04 · RUN-13 · RUN-10 · RUN-13 | ← PER-c05 (RUN-c66) |
| #463 (RUN 몫) | RUN-25 · RUN-05 | ← EXE-c23 (RUN-c67) |
| #489 (RUN 몫) | RUN-33 | ← DEV-c24 (RUN-c71) |

집계 — 항목 33 (RUN-23 결번): CLOSE 0 · DEC 2 · PR 31 (S 21 · M 9). 태그 bug 19 · refactor 6 · feature 4 · perf 2.
