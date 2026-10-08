# DEV 작업 목록

> dev @ b08a91b3. 담당 이슈의 열린 PR 없음. 열린 PR 7건 중 머지 대상 6건(#651 #652 #654 #655 #656 #658, decisions ⑩ — #530 은 재업로드 노선이라 제외) 가운데 DEV 파일을 만지는 것: #655(tests/CMakeLists.txt · docs/test-levels.md · DashGeometryParameterWidget.cpp −1,722줄 4파일 분할 · DashMainWindow.cpp) · #654(CMakeLists.txt · tests/CMakeLists.txt · vcpkg-configuration.json · docs/test-levels.md · DashGeometryParameterWidget.cpp · DashMainWindow.cpp · DashMorphingBar.cpp) · #652(tests/CMakeLists.txt · DashMainWindow.cpp) · #651(tests/CMakeLists.txt · DashMainWindow.cpp · DashModelingTreeWidget.cpp). #530 은 머지하지 않으므로(C-2 결정 ②) 충돌·선행에서 뺀다. #655 는 base 가 `refactor/332-handle-state-integration` 인 스택 PR 이라 #654 뒤에 온다. CI 는 아직 없다 — #372 계열은 DEV-14 → 15 → 16 순.
> Phase B1 흡수(범위밖 이관, DEV-c38): PRE-c58(#411 결정 1, vtkIOHDF 가용 여부) → DEV-25(신규 INV).
>
> **공통 제약 (소스 파일을 고치는 전 항목 — DEV-10 · DEV-19 는 제외하고 DEV-20 · DEV-21 · DEV-22 · DEV-24 에 그대로 걸린다)**: pre-commit 훅이 스테이지된 C/C++ 파일 **전체**의 `.clang-format` 일치를 요구하는데(`scripts/hooks/run-format-checks.sh:7`) 저장소는 97% 미포맷이다(`:19`, PR #329). 한 줄만 고쳐도 파일 전체 재포맷 diff 가 따라오므로 **파일별로 "재포맷 커밋 → 변경 커밋" 2단**으로 간다. 한두 줄만 고치는 DEV-20(`TopOptPostprocessDialog.cpp`)·DEV-22(`AboutDialog.cpp`)는 이걸 안 하면 변경이 재포맷에 완전히 묻힌다.

### DEV-01 · VS/MSVC 버전 운영 정책을 넷 중 하나로 확정한다
- 종류: DEC | 규모: S | 태그: F · docs
- 목표: MSVC 상향이 vcpkg `triplet_abi` 를 바꿔 캐시 전량 miss 가 되는 문제에 대해 A(전원 상향) · B(영구 고정 + 오프라인 레이아웃) · C(구 환경 병행 공급) · D(triplet abi 하위 호환) 중 하나를 고르고 근거·유지 비용·해제 조건을 기록한다. 어느 쪽이든 결정 전까지 18.9.2 고정은 유지한다.
- 완료 기준: 결정 기록(docs/development-environment-setup.md 2.1 또는 README Prerequisites 에 정책 1문단) · 선택지에 따른 후속 항목(DEV-02 상시 · DEV-03 은 C/D 일 때만) 확정
- 변경 범위: README.md · docs/development-environment-setup.md (기록만)
- 선행: -
- 충돌: B2 교집합: README.md → DEV-02 DEV-12 DEV-21 DEV-24 MOR-07 · development-environment-setup.md → DEV-02 DEV-12
- 흡수: #330 · DEV-c01, c02, c03, c04, c05
- 비고: 이슈 본문 권고는 B. D 는 레지스트리·메타 저장소 triplet 정본을 바꾸는 EXT 이고 ABI 위험을 CI 가 잡는다는 전제가 필요하다.

### DEV-02 · VS 18.9.2 오프라인 설치 레이아웃을 보관하고 README 의 부트스트래퍼 TODO 를 대체한다
- 종류: PR | 규모: S | 태그: F, G · docs
- 목표: `--layout` 으로 18.9.2 + MSVC 14.51.36231 레이아웃을 떠 툴체인 버킷에 올리고, README 의 "fixed-version 부트스트래퍼" 항목과 TODO 를 레이아웃 경로·설치 명령으로 바꾼다. setup-environment.ps1 의 FAIL 메시지가 그 레이아웃을 안내하게 한다.
- 완료 기준: 1. README.md:25-27 TODO 블록 제거, 레이아웃 경로·`vs_setup --noweb` 계열 설치 명령 기재 2. 새 PC 에서 레이아웃만으로 setup-environment.ps1 `Visual Studio` 항목 OK 3. 레이아웃 산출 명령이 문서에 남아 다음 버전에서 재현 가능
- 변경 범위: README.md · scripts/setup-environment.ps1 · docs/development-environment-setup.md
- 선행: -
- 충돌: B2 교집합: README.md → DEV-01 DEV-12 DEV-21 DEV-24 MOR-07 · development-environment-setup.md → DEV-01 DEV-12
- 흡수: #330 · DEV-c06
- 비고: **DEV-01 과 무관하다** — 이슈 Must Know 가 "정책과 무관하게 지금 버전의 layout 을 따 놔야 한다" 로 못 박은 즉시 조치다. 정책이 A(전원 상향)로 가도 18.9.2 레이아웃은 과거 빌드 재현용으로 남는다. 레이아웃 업로드 자체는 버킷 쓰기 권한(CI 서비스 계정) 이 필요한 ops — 저장소 변경은 문서·스크립트뿐.

### DEV-03 · 선택된 정책(C 또는 D)을 레지스트리·메타 저장소에 구현한다
- 종류: EXT | 규모: M | 태그: F
- 목표: DEV-01 이 C(구 환경 병행 공급) 또는 D(abi 하위 호환 triplet) 를 고르면 DashOpti_Registry CI 또는 메타 저장소 `DashOpti` 의 custom triplet 을 바꾸고 캐시를 재워밍한다. A/B 면 이 항목은 닫는다.
- 완료 기준: 외부 저장소 PR + GUI 쪽 triplets/x64-windows-dashopti.cmake 동기(필요 시 1줄) · `local-msvc-release` 콜드 configure 캐시 히트
- 변경 범위: (외부) DashOpti_Registry · DashOpti 메타 · (GUI) triplets/x64-windows-dashopti.cmake
- 선행: DEV-01
- 충돌: PR #654(vcpkg-configuration.json 변경 — baseline 범프와 순서 조율)
- 흡수: #330 · DEV-c04, c05
- 비고: GUI 는 추적만.

### DEV-04 · mesh-ops portfile 의 intel-mkl 핀 주석을 현재 사실로 고친다
- 종류: EXT | 규모: S | 태그: F · docs
- 목표: `ports/mesh-ops/portfile.cmake` 의 "2023.2.0 핀 필수 · 실패는 빌드 오류" 주석을 삭제하거나 "핀 없음 · 캐시는 2025.2.0#1" 로 갱신한다.
- 완료 기준: 외부 저장소 PR(DashOpti_Registry) 1줄
- 변경 범위: (외부) DashOpti_Registry ports/mesh-ops/portfile.cmake
- 선행: -
- 충돌: -
- 흡수: #335-1 · DEV-c07
- 비고: GUI vcpkg.json 에 intel-mkl 핀이 없으므로 GUI 측 변경 없음.

### DEV-05 · mesh-ops 2026-09-07.0 의 재작성된 git-tree 를 처분한다
- 종류: EXT | 규모: S | 태그: F, A
- 목표: versions DB 의 `2026-09-07.0` 을 (a) 제거 (b) 올바른 tree(`954d73eae3d3`) 로 되돌림 (c) baseline `46e3915` 사용 금지 공지 중 하나로 처리한다.
- 완료 기준: 외부 저장소 PR 또는 공지 기록 · GUI baseline(`c80fb330`) 이 영향 밖임을 확인한 메모
- 변경 범위: (외부) DashOpti_Registry versions/
- 선행: -
- 충돌: -
- 흡수: #335-2 · DEV-c08
- 비고: GUI 는 추적만.

### DEV-06 · preprocessor 를 메타 저장소에 등록하고 GUI 의 feature 선택을 정본에 맞춘다
- 종류: EXT | 규모: S | 태그: F
- 목표: 메타 `repos.json`·`vcpkg.json` 에 `preprocessor` 를 등록해 feature 정본과 CI 교차 검증을 만들고, 확정된 feature 로 GUI vcpkg.json 의 `preprocessor` 항목(현재 `["test"]` 유추값)을 맞춘다.
- 완료 기준: 외부 저장소 PR · GUI vcpkg.json 1줄 동기 · `--only-binarycaching` 콜드 configure 히트
- 변경 범위: (외부) DashOpti 메타 · (GUI) vcpkg.json
- 선행: -
- 충돌: B2 교집합: vcpkg.json → DEV-21 · PR #658(vcpkg.json)
- 흡수: #335-3 · DEV-c09
- 비고: feature 가 어긋나면 ABI 해시가 달라 hard fail — GUI 동기가 같은 PR 묶음이어야 한다.

### DEV-07 · 현장 Abaqus 지원 버전을 확정한다
- 종류: DEC | 규모: S | 태그: F
- 목표: 2024 만 / 2020+2024 중 공급 대상을 정한다. 러너 디스크·Abaqus 라이선스 제약을 같이 확인한다.
- 완료 기준: 결정 기록(#335 코멘트 또는 레지스트리 docs)
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #335-4 · DEV-c10
- 비고: DEV-08 의 선행.

### DEV-08 · SSOT 러너에 Abaqus 2024 SDK 스냅샷을 두고 preprocessor 포트를 2024 포함으로 재발급한다
- 종류: EXT | 규모: M | 태그: F
- 목표: 러너에 `win_b64/code/{include,lib}` 스냅샷 배치 → 포트 `DASH_PR_ABAQUS_VERSIONS "2020;2024"` + `ABAQUS_BASE_DIR_2024` → 새 버전 발급·캐시 재워밍 → portfile 주석 갱신 → GUI baseline 범프.
- 완료 기준: 외부 저장소 PR · GUI 빌드 `bin/` 에 `Preprocessor_Abaqus_V2024.dll` 도착 · vcpkg-configuration.json baseline 1줄 범프
- 변경 범위: (외부) DashOpti_Registry ports/preprocessor · (GUI) vcpkg-configuration.json
- 선행: DEV-07
- 충돌: PR #654(vcpkg-configuration.json) · B2 교집합: PR #658(vcpkg-configuration.json)
- 흡수: #335-4 · DEV-c10
- 비고: GUI 는 추적 + baseline 범프만.

> **DEV-09 — 결번.** external/ 폐기의 저장소 변경이 `docs/scratchpad/build-environment.md` 1건뿐이고 DEV-12 가 같은 파일을 `docs/build-environment.md` 로 옮긴다 — 개념상 하나(= 그 파일의 최종 상태)인데 잘게 나뉘어 있었다(00-plan 1-2). **DEV-12 에 병합**(#336-1 · DEV-c11). 확인 불가한 완료 기준(공지 발송 · 클린 빌드 1회)은 DEV-12 비고의 선행 ops 로 내렸다. 번호는 재사용하지 않는다.

### DEV-10 · Qt6 deprecated globalPos() 남은 곳을 globalPosition() 으로 바꾼다
- 종류: PR | 규모: M | 태그: F · refactor
- 목표: 실코드를 `globalPosition().toPoint()`(정수 좌표 필요처) 로, DashMorphingBar.cpp:125 의 주석 코드는 삭제한다. 동작 불변. 현재 14곳(실코드 13 + 주석 1) 중 2곳은 PR #655 가 먼저 치운다 — **착수 시점 대상은 12곳(실코드 11 + 주석 1)**.
- 완료 기준: 1. `git grep -n "globalPos()" -- '*.cpp' '*.h'` 0건 2. 빌드 경고에 `globalPos` deprecated 0건 3. 창 드래그·리사이즈(DashTitleBar·DashMainWindow)·트리 컨텍스트 메뉴·플롯 툴팁 수동 확인
- 변경 범위: view/DashMainWindow.cpp · view/DashModelingTreeWidget.cpp · view/DashProjectWidget.cpp · view/DashTitleBar.cpp · view/analyzer/DashScatter2DWidget.cpp · view/analyzer/DashShapDependenceWidget.cpp · view/overlay/DashMorphingBar.cpp · (#655 미머지 시에만) view/DashGeometryParameterWidget.cpp
- 선행: PR #655 머지 (`DashGeometryParameterWidget.cpp:2146·2150` 을 `view/common/DashHandleTree.cpp` 로 옮기면서 이미 `globalPosition()` 으로 바꾼다 — 먼저 손대면 1,722줄 삭제와 정면 충돌하고 치환이 버려진다), PR #654·#652·#651 머지
- 충돌: PR #655(DashGeometryParameterWidget.cpp · DashMainWindow.cpp) · #654(DashGeometryParameterWidget.cpp · DashMainWindow.cpp · DashMorphingBar.cpp) · #651(DashModelingTreeWidget.cpp · DashMainWindow.cpp) · #652(DashMainWindow.cpp) · UIC 의 창·DPI 항목(DashTitleBar · DashMainWindow resize 경로) · B2 교집합: DashMainWindow.cpp → 공유 49건(deps.md 5절) · DashGeometryParameterWidget.cpp → MOR-01 MOR-02 MOR-03 MOR-17 MOR-22 MOR-23 UIC-20 · DashMorphingBar.cpp → MOR-05 MOR-14 UIC-07 · DashModelingTreeWidget.cpp → PRJ-04 REN-12 · DashProjectWidget.cpp → PRJ-33 UIC-19 · DashTitleBar.cpp → UIC-09
- 흡수: #336-2 · DEV-c12
- 비고: #321 이 머지돼 순서 제약은 사라졌다. clang-format 공통 제약(파일 머리말)이 그대로 걸리므로 파일별 "재포맷 커밋 → 치환 커밋" 2단으로 간다. **좌표는 열린 PR 4건 머지 뒤 재확인한다** — #655 가 `DashGeometryParameterWidget.cpp` 를 1,722줄 걷어내고 4파일로 분할하므로 그 파일의 2곳은 사라지고, #654·#651·#652 가 `DashMainWindow.cpp`·`DashModelingTreeWidget.cpp` 를 함께 고친다.

### DEV-11 · CRT 배포의 수동 glob 을 InstallRequiredSystemLibraries 로 되돌린다
- 종류: PR | 규모: S | 태그: F, G
- 목표: `CMakeLists.txt:15-36` 의 툴셋 경로 수동 glob 과 :11-14 의 TODO 를 지우고 `include(InstallRequiredSystemLibraries)`(+ `CMAKE_INSTALL_OPENMP_LIBRARIES`) 로 대체한다. 차단 조건은 이미 해제됐다 — CMake 4.3.3 의 `Modules/InstallRequiredSystemLibraries.cmake:252-254` 가 `MSVC_TOOLSET_VERSION 145 → VC145`·`_MSVC_IDE_VERSION 18` 을 알고 :297-312 가 `VS_18_DIR/VC/Redist/MSVC/*` 를 글롭하고 :610-621 이 `Microsoft.VC145.OPENMP/vcomp140.dll` 을 담는다. 같이 `cmake_minimum_required` 를 VC145 를 아는 최소 버전으로 범프한다(현 하한 3.25 로는 3.25~3.31 configure 에서 `MSVC_REDIST_DIR-NOTFOUND` 가 그대로 난다).
- 완료 기준: 1. `git grep -n "Redist/MSVC" CMakeLists.txt` 0건 · TODO 블록 제거 2. `cmake_minimum_required` 가 VC145 지원 하한 이상(또는 그 미만에서 glob 폴백을 남기는 버전 가드를 둔 근거를 비고에) 3. **소비처 2곳 모두** 산출물 동일 — 앱 `bin/`(:463-469) 과 `DashUiPreview_package`(:288-293) 에 CRT DLL + `vcomp140.dll` 이 치환 전과 같은 집합 4. Windows 빌드 1회로 (3) 대조
- 변경 범위: CMakeLists.txt · CMakePresets.json(`"version": 6` 이 3.25 하한 — 범프 폭에 따라)
- 선행: -
- 충돌: PR #654(CMakeLists.txt) · DEV-21(CMakeLists.txt) · B2 교집합: CMakeLists.txt → DEV-24 DEV-25 MOR-06 MOR-07 UIC-02 · PR #658(CMakeLists.txt)
- 흡수: #336-3 · DEV-c13
- 비고: 이슈의 "CMake 3.31 이 모른다" 는 이행 당시 실측 — 로컬 `cmake --version` = 4.3.3 에서 해제를 직접 확인했다(DEV-c13). VC145 를 처음 아는 CMake 버전은 릴리스 노트에서 확정한다 — 그 값이 하한 범프의 숫자다. `CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS` 는 변수 하나이므로 두 POST_BUILD 가 그것을 참조하도록 바꾸면 소비처 2곳이 한 번에 덮인다.

### DEV-12 · vcpkg 이행 문서 2건을 삭제하고 build-environment.md 를 external 잔재 없이 docs/ 정식 위치로 승격한다
- 종류: PR | 규모: S | 태그: F · docs
- 목표: `docs/vcpkg-migration-scope.md` · `docs/vcpkg-migration-code-changes.md` 삭제(정본은 PR #313 본문). `docs/scratchpad/build-environment.md` 는 운영 지식이므로 `docs/build-environment.md` 로 옮기고 `../` 링크 제거, 삭제 문서를 가리키던 3곳(:12·44·345) 정리, docs/index.md 「공통 문서」 등록, README.md:60 · development-environment-setup.md 7곳의 경로 갱신. 같은 파일에서 **external/ 전제 서술도 걷는다**(DEV-09 병합) — 2.7 절 "낡은 external/ 트리 의심" 과 :34-35·:327-329. CMake 의 `EXTERNAL_DIR`(:73) 과 가드된 extension exe 2곳(:374-375·477·505)은 그대로 둔다.
- 완료 기준: 1. `git grep -n "vcpkg-migration"` 0건 2. `git grep -n "scratchpad/build-environment"` 0건 3. docs/index.md 에 build-environment 항목 존재 4. `git grep -n "external/" -- docs/` 가 진단 절차를 가리키지 않음(비추적 로컬 트리라는 사실 서술만 남음)
- 변경 범위: docs/vcpkg-migration-scope.md(삭제) · docs/vcpkg-migration-code-changes.md(삭제) · docs/scratchpad/build-environment.md → docs/build-environment.md · docs/index.md · docs/development-environment-setup.md · README.md
- 선행: -
- 충돌: DEV-13(docs/index.md) · B2 교집합: README.md → DEV-01 DEV-02 DEV-21 DEV-24 MOR-07 · development-environment-setup.md → DEV-01 DEV-02 · index.md → EXE-05
- 흡수: #336-1 · #336-4 · DEV-c11, c14, c15, c16, c17
- 비고: 선행 ops(항목 아님) — 팀 공지로 로컬 `external/` 삭제를 알린다(수 GB 회수). 저장소에는 지울 것이 없다: `external/` 은 비추적(.gitignore:482-484)이고 현 체크아웃에 부재다. "운영 지식 추출" 별도 티켓은 만들지 않는다 — CRT·MKL 복사 근거는 CMakeLists.txt:9-36·420-445 주석이 정본이고, build-environment.md 가 그 위치를 가리키면 된다.

### DEV-13 · 테스트·문서 색인의 낡은 수치와 깨진 링크를 현행화한다
- 종류: PR | 규모: S | 태그: F · docs
- 목표: docs/test-levels.md 9절(실행 파일 14 · 서브테스트 191) 과 docs/test-execution.md:13("실행 파일 6개") 을 add_test 54건 기준으로 고치고, docs/index.md 가 가리키는 부재 문서(io-controller.md · modules/* · dialogs/*) 링크를 제거하거나 실제 문서로 잇는다.
- 완료 기준: 1. docs/index.md 의 상대 링크 전부 존재 2. test-levels.md 9절·test-execution.md 의 실행 파일 수가 `ctest -N` 과 일치(또는 수치를 빼고 "tests/CMakeLists.txt 가 정본" 으로 치환)
- 변경 범위: docs/test-levels.md · docs/test-execution.md · docs/index.md
- 선행: -
- 충돌: PR #655 · #654(docs/test-levels.md 9절 표를 둘 다 고친다 — #654 가 191→203, #655 가 203→233 · 타깃 개명 `TestSampledHandleTree`→`TestHandleTree` + `TestHandleEditing` 추가) · DEV-12(docs/index.md) · B2 교집합: index.md → EXE-05 · test-execution.md → DEV-14 DEV-18 · test-levels.md → PER-05
- 흡수: DEV-c21
- 비고: 원천 이슈 없는 부수 발견. 9절 전수 표는 "두 곳에 두면 갱신이 갈라진다" 고 스스로 적었으니 실행 파일별 수치를 빼는 쪽을 권장 — #654·#655 가 둘 다 그 표의 숫자를 손으로 고치고 있는 것이 그 근거다. `docs/index.md:6` 이 본문에서 `io-controller.md` 를 "모든 파일 경로 규칙의 기준" 으로 선언한 줄도 함께 처리 대상이다.

### DEV-14 · CI 플랫폼과 러너 구성을 결정한다
- 종류: DEC | 규모: S | 태그: F
- 목표: 플랫폼(GitHub Actions 추정) · 러너(VS 18.9.2 + MSVC 14.51.36231 고정 self-hosted Windows, vcpkg 바이너리 캐시 읽기 권한, Ninja) · 레인 트리거(PR 에 Level 1·2 / 야간 또는 수동 Level 3) · 앱 빌드 포함 여부를 정한다. 앱 빌드 여부의 쟁점은 하나다 — **Level 3 레인이 `tests/e2e` 를 빌드·등록하는가.** `tests/` 본체는 독립 CMake 프로젝트라 앱 없이 빌드되지만(모핑·preprocessor 테스트만 `CMAKE_PREFIX_PATH` 로 vcpkg_installed 필요), `tests/e2e` 는 별도 프로젝트(`project(DashOptiRealExeE2E)`)이고 `-DDASH_BIN_DIR=<build>/bin` 이 필수라 `bin/extensions/` 의 실 extension exe = **앱 빌드 전체**를 요구한다. 이것이 CI 에 앱 빌드를 넣을 유일한 이유다.
- 완료 기준: 결정 기록 1곳 — `docs/test-execution.md` 신설 절(README 와 양자택일로 두지 않는다. DEV-13·DEV-18 도 이 파일을 고치므로 교집합이 한 곳으로 모인다) · `tests/e2e` 의 Level 3 등록 여부와 그 결론이 요구하는 앱 빌드 비용(러너 디스크·시간)이 그 절에 적힘
- 변경 범위: docs/test-execution.md (기록만)
- 선행: -
- 충돌: B2 교집합: test-execution.md → DEV-13 DEV-18
- 흡수: #372(선행 조건) · #373(닫힘 — "훅 우회는 CI 게이트로만") · DEV-c18
- 비고: DEV-01 은 **차단 선행이 아니다** — 정책이 미확정이어도 러너는 현 핀(18.9.2)으로 세울 수 있다. 단 DEV-01 이 A(전원 상향)로 가면 러너 핀 갱신이 운영 비용으로 따라오므로 결정 기록에 그 연결을 남긴다. 플랫폼이 GitHub 가 아니면 DEV-15 의 변경 범위가 바뀐다. `tests/e2e/test_e2e_real_exe.cpp` 가 "ctest 에 등록돼 있지 않다 … 등록 여부는 별건"(docs/test-levels.md 9절 말미)으로 미뤄 둔 그 "별건"이 이 결정이다.

### DEV-15 · 테스트 레인 CI 워크플로를 신설한다
- 종류: PR | 규모: M | 태그: F · feature
- 목표: PR·push 에 `tests/` 를 configure·build 하고 `DASH_TEST_LEVEL=1`·`2` 로 ctest 를 돌리는 워크플로, 야간(또는 수동) Level 3 워크플로를 만든다. 훅이 `--no-verify` 로 우회된 커밋을 여기서 막는다(#373 결정). 서식 검사(run-format-checks.sh 의 clang-format 부분)도 같은 레인에 둔다. Level 3 레인은 DEV-14 가 `tests/e2e` 등록을 결정한 경우 앱을 빌드하고 `cmake -S tests/e2e -B build-e2e -DDASH_BIN_DIR=<build>/bin` 단계를 추가한다.
- 완료 기준: 1. PR 에 Level 1·2 레인이 돌고 실패가 머지를 막는다 2. 야간 Level 3 레인이 돈다 3. 레인 로그에 `ctest -V` 실행 파일별 시간이 남는다(DEV-16 입력) 4. `tests/e2e` 는 DEV-14 결정대로 — 등록이면 Level 3 레인에서 앱 빌드 + `bin/extensions/` 배치 뒤 `test_e2e_real_exe` 가 실행되고, 미등록이면 그 사유가 워크플로 주석과 docs/test-execution.md 에 남는다
- 변경 범위: .github/workflows/tests-level-1-2.yml · .github/workflows/tests-level-3.yml (신규) · scripts/run_tests.ps1(`-Level` 인자 이미 있음 — 비대화형 옵션 보강 시) · (e2e 등록 시) tests/e2e/CMakeLists.txt 에 `add_test` 또는 레인 스크립트
- 선행: DEV-14
- 충돌: B2 교집합: tests-level-1-2.yml → DEV-16
- 흡수: #372(선행 조건) · DEV-c18
- 비고: 레벨 게이트·스크립트는 #359 가 다 세웠다(tests/TestLevel.h · scripts/hooks/run-test-level.sh). 워크플로는 그 명령을 그대로 부른다. `tests/e2e` 는 `tests/CMakeLists.txt:17` 이 "built separately" 로 분리 선언한 별도 프로젝트라 `add_subdirectory` 가 아니라 레인의 독립 configure 단계다.

### DEV-16 · Level 1 레인 소요 시간을 측정하고 5분 초과 시 알린다
- 종류: PR | 규모: S | 태그: F · feature
- 목표: Level 1 워크플로에서 `ctest` 구간만 벽시계로 재고, 임시 한도 5분을 넘으면 빌드를 깨지 않고 경고(annotation/요약)를 낸다. 경고에 `ctest -V` 에서 뽑은 실행 파일별 소요 시간 상위 목록을 붙인다.
- 완료 기준: 1. 측정 구간이 빌드를 제외한 ctest 실행만임이 스크립트에서 드러남 2. 한도 초과가 실패가 아닌 경고로 표시됨(의도적 초과 테스트로 1회 확인) 3. 경고에 실행 파일별 시간 포함 4. 한도 값이 워크플로 변수 1곳
- 변경 범위: .github/workflows/tests-level-1-2.yml · scripts/ci/ctest-timing.py (신규)
- 선행: DEV-15
- 충돌: -
- 흡수: #372 · DEV-c19, c20
- 비고: Level 2·3 한도는 두지 않는다(docs/test-levels.md 6절 결정 유지). 기준선이 쌓이면 5분을 조인다. 빌드 시간 감시는 별건.

### DEV-17 · 네이밍 정렬의 방식·단위·속도를 결정한다
- 종류: DEC | 규모: S | 태그: F, E
- 목표: #386 재착수 1단계. 비테스트 소스 `m_` 접두 이름 1,161종(13,383회) 를 `.clang-tidy` 규칙(접미 `_`) 으로 정렬할 방식을 정한다 — 전수 일괄(열린 PR #655·#654·#652·#651 과 충돌·blame 덮음) vs 점진(파일/모듈 단위, 어떤 속도로, 어느 PR 에 얹을지) vs 보류 연장. 정렬 완료 판정(전체 clang-tidy 위반 0)과 그 뒤 검사 위치(훅/CI)는 결정에 포함하되 구현은 별도.
- 완료 기준: 결정 기록(docs/coding-convention.md 네이밍 절 갱신) · 점진이면 첫 단위와 순서 명시
- 변경 범위: docs/coding-convention.md (기록만)
- 선행: -
- 충돌: B2 교집합: coding-convention.md → UIC-14 UIC-18 UIC-21
- 흡수: #386 · DEV-c22, c23
- 비고: 보류 결정 자체는 기록 완료(해소됨). 검사기는 이전 구현(`0e3b7e7`)을 잇지 않고 새로 짠다 — 이슈 본문의 함정 목록이 그때의 입력. 정렬 전까지 #386 은 결정 기록으로 열어 둬도 된다. 파일 머리말의 clang-format 공통 제약과 같은 함정 — 정렬 커밋은 재포맷 커밋과 분리해야 blame 이 두 번 덮이지 않는다.

### DEV-18 · 산재 카운트 grep 게이트를 만들어 Level 1 레인에 건다
- 종류: PR | 규모: S | 태그: F, E · feature
- 목표: 패턴별 기준값 파일(`scripts/hooks/grep-gate.txt`)과 검사 스크립트를 만든다. 하드(증가 시 실패): `processEvents`(model 41 · view 14) · model→view include(2). 소프트(추세 출력만): `Mgr()`(245). 기준값 갱신은 같은 PR 에서 사유와 함께. 모든 종료 경로가 패턴별 개수를 항상 출력한다(PR #329 교훈 — "출력 없음" 과 "검사 없음" 을 구분).
- 완료 기준: 1단계(이 항목) — 1. pre-commit 에서 실행 2. 기준값 초과 시 rc≠0, 통과 시에도 개수 출력 3. tests/hooks/ 에 시나리오(초과·동일·감소·빈 입력) 자체검사 4. **기준값은 착수 커밋에서 스크립트로 생성하고, 생성 명령을 기준값 파일 머리말에 남긴다**(위 수치는 b08a91b3 스냅샷이고 열린 PR 4건이 `model/`·`view/` 를 대량 수정하므로 착수 시점에 다시 떠야 한다). 2단계 — CI Level 1 레인 등록(DEV-15 가 레인을 세운 뒤)
- 변경 범위: scripts/hooks/run-grep-gate.sh · scripts/hooks/grep-gate.txt (신규) · .githooks/pre-commit · tests/hooks/test-grep-gate.py (신규) · docs/test-execution.md
- 선행: -
- 충돌: 열린 PR 전부(#655 #654 #652 #651 — 기준값 재생성 필요) · B2 교집합: test-execution.md → DEV-13 DEV-14
- 흡수: #489(F1 "grep 게이트") · DEV-c26
- 비고: **DEV-15 는 차단 선행이 아니다** — 훅 쪽 1단계는 CI 없이 독립으로 랜딩하고, 레인 등록만 DEV-15 뒤다(완료 기준의 2단계). 기준값 자체는 EXE(펌핑 제거)·PRJ(`Mgr()` 주입 전환) 항목이 내리면서 갱신한다. 도메인 커버리지 확장(CAD-U5 · OPT-U3 · BLD · RUN · DOE)은 각 모듈 항목 — DEV 는 인프라(게이트·등록 헬퍼)만 맡는다.

### DEV-19 · tests/CMakeLists.txt 의 환경 변수 타깃 수동 나열을 DEFER 자동 수집으로 바꾼다
- 종류: PR | 규모: S | 태그: F · refactor
- 목표: `:383` 의 `set_tests_properties(<타깃 30개 나열> PROPERTIES ENVIRONMENT_MODIFICATION "PATH=…;QT_LOGGING_TO_CONSOLE=set:1")` 에서 손으로 든 30개 목록을 없애고, 같은 파일이 이미 쓰는 선례 — `:904` `_dash_attach_known_failures` + `:921` `cmake_language(DEFER CALL …)` 가 `BUILDSYSTEM_TARGETS` 로 `test_*` 를 훑는 방식 — 을 재사용해 **그 블록이 덮던 타깃 집합에만** 같은 환경 변수를 붙인다. ":393-394 목록에 안 넣으면 로더가 0xc0000135" 함정이 사라진다. 동작 불변.
- 완료 기준: 1. `ctest -N` 목록이 전후 동일(현행 54건) 2. **각 타깃의 `ENVIRONMENT_MODIFICATION` 값이 전후 동일** — 지금 그 변수가 붙은 타깃 집합과 붙지 않은 타깃 집합이 둘 다 그대로다(가드 안 24개는 `_dash_snapshot_path_ops`·`_dash_rw_path_ops`·`QT_QPA_PLATFORM` 가 서로 달라 건드리지 않는다) 3. Level 1·2 레인 통과
- 변경 범위: tests/CMakeLists.txt
- 선행: PR #655 머지 (`:392-404` hunk 가 `test_handle_array_names` 제거 · `test_sampled_handle_tree`→`test_handle_tree` 개명 · `test_handle_editing` 추가로 타깃 집합을 바꾼다)
- 충돌: PR #655 · #654 · #652 · #651(tests/CMakeLists.txt) · 각 모듈의 테스트 추가 항목(같은 파일) · B2 교집합: tests/CMakeLists.txt → 공유 12건(deps.md 5절)
- 흡수: #489(커버리지 확장의 인프라 비용) · DEV-c27
- 비고: 선택 항목. 열린 PR 4건 머지 뒤, 모듈 테스트 추가가 몰리기 전에 넣어야 충돌이 적다. **54개 등록 전면을 `dash_add_qtest` 래퍼 하나로 바꾸는 것은 이 항목이 아니다** — :383 의 30개만 Qt Core+Test 전용 한 블록을 공유하고 나머지 24개는 `if(VTK_FOUND)`·`core-lib`·`mesh-ops` 가드 안에서 링크 목록·`vtk_module_autoinit`·환경 변수가 전부 다르다(921줄 · `add_executable` 55 · `set_tests_properties` 26블록 · `QT_LOGGING_TO_CONSOLE` 14회). 전면 래퍼화는 `M` 이상의 별건이고, 그 쪽이 필요해지는 시점은 가드별 변종이 공통 규칙으로 수렴한 뒤다.

### DEV-20 · 출고물의 개발자 로컬 경로를 제거한다
- 종류: PR | 규모: S | 태그: G · bug
- 목표: TopOptPostprocessDialog::onProgressTimer 의 `C:\Users\MIIIING\Downloads\TO\repaired_surface_7.stl` 하드코딩 렌더를 실제 산출물 경로(후처리 결과 STL) 로 바꾸거나, 산출물이 없으면 그 단계를 제거한다.
- 완료 기준: 1. `git grep -nIE '"[A-Za-z]:[/\\]' -- '*.cpp' '*.h' '*.ui' ':!tests'` 0건(주석 제외) 2. TopOpt 후처리 진행 마지막 단계에서 로컬 경로 없이 결과 렌더 또는 무동작
- 변경 범위: view/dialog/TopOptPostprocessDialog.cpp
- 선행: -
- 충돌: B2 교집합: TopOptPostprocessDialog.cpp → EXE-09 PRJ-26 REN-07
- 흡수: #483 · DEV-c28, c29, c31, c32
- 비고: 접점 PRJ(view/dialog). 변경이 한두 줄이라 **파일 머리말의 clang-format 공통 제약이 가장 세게 걸린다** — 재포맷 커밋을 먼저 분리하지 않으면 변경이 완전히 묻힌다. 플레이스홀더 문구·Dev 자산 경로는 해소됨(Release 미포함). Optimizer 샘플 제약 행(`r1 <= 163.23`)은 저장 왕복에 섞이므로 OPT 로 보냄(DEV-c30).

### DEV-21 · 버전을 한 곳에서 exe 리소스와 Qt 앱 메타에 주입한다
- 종류: PR | 규모: S | 태그: G · feature
- 목표: CMake 에 숫자 버전(`DASH_VERSION_MAJOR/MINOR/PATCH`) 을 두고 `resources/resources.rc.in` 을 configure 해 `VERSIONINFO`(FILEVERSION · PRODUCTVERSION · ProductName · FileDescription · LegalCopyright) 를 넣는다. main.cpp 에서 `QCoreApplication::setApplicationName/Version` 을 호출해 저장 문서의 `createdAppVersion`·`modifiedAppVersion` 이 채워지게 한다. vcpkg.json `version-string` 은 같은 값으로 맞춘다.
- 완료 기준: 1. `DashOpti.exe` 속성창 「자세히」에 버전·제품명 표시 2. 새로 저장한 프로젝트 JSON 의 `createdAppVersion` 이 `DASH_VERSION` 과 같음 3. 버전 문자열 정의가 CMakeLists.txt 1곳 4. README.md 의 CMake 옵션 표·예제(:133 · :144)가 신설한 숫자 버전 변수를 반영
- 변경 범위: CMakeLists.txt · resources/resources.rc → resources/resources.rc.in · main.cpp · vcpkg.json · README.md
- 선행: -
- 충돌: PR #654(CMakeLists.txt) · DEV-11(CMakeLists.txt) · DEV-24(README.md 의 같은 옵션 표) · B2 교집합: main.cpp → EXE-02 EXE-06 PRJ-06 PRJ-14 UIC-05 UIC-26 · CMakeLists.txt → DEV-25 MOR-06 MOR-07 UIC-02 · README.md → DEV-01 DEV-02 DEV-12 MOR-07 · vcpkg.json → DEV-06 · PR #658(CMakeLists.txt·vcpkg.json)
- 흡수: #484-1 · DEV-c33, c34
- 비고: 접점 PER — `createdAppVersion` 이 비어 있던 기존 문서는 그대로 둔다(마이그레이션 없음). 파일 머리말의 clang-format 공통 제약이 `main.cpp` 에 걸린다.

### DEV-22 · About 의 Build Date 가 항상 "어제" 로 표시되는 덮어쓰기를 지운다
- 종류: PR | 규모: S | 태그: G · bug
- 목표: AboutDialog::getBuildDate 에서 `__DATE__` 파싱 결과를 `QDate::currentDate().addDays(-1)` 로 덮는 2줄을 제거해 실제 빌드 날짜를 보인다.
- 완료 기준: About 의 Build Date 가 `__DATE__` 와 일치(다른 날 실행해도 불변)
- 변경 범위: view/dialog/AboutDialog.cpp
- 선행: -
- 충돌: DEV-24(같은 파일) · B2 교집합: AboutDialog.cpp → PRJ-14
- 흡수: #484(부수) · DEV-c36
- 비고: `addDays(-1)` 가 빌드 날짜 쪽에도 붙어 있다(:103) — 의도 불명, 같이 제거. 2줄 변경이라 **파일 머리말의 clang-format 공통 제약이 가장 세게 걸린다** — 재포맷 커밋을 먼저 분리한다. 같은 파일을 고치는 DEV-24 와 묶으면 재포맷을 한 번만 치른다.

### DEV-23 · 라이선스 만료일 런타임화의 형식과 강제 여부를 결정한다
- 종류: DEC | 규모: S | 태그: G, A
- 목표: 현재 만료일은 컴파일 상수(`2026-08-31`, 경과) 이고 About 표시 전용이며 타입만 QSettings 런타임이다. (1) 형식 — 서명 파일(발급 도구 + 검증, W17 원안) vs 설정 키/단순 파일, (2) 만료 시 동작 — 표시만 vs 기동 차단, (3) 발급 주체·갱신 절차를 정한다.
- 완료 기준: 결정 기록 · DEV-24 의 규모(S/M) 확정
- 변경 범위: -
- 선행: -
- 충돌: -
- 흡수: #484-2 · DEV-c35
- 비고: 되돌리기 비용이 큰 결정(저장 포맷·발급 절차) — "나중에 교체" 전제로 정하지 않는다.

### DEV-24 · 라이선스 만료일을 런타임 소스에서 읽는다
- 종류: PR | 규모: M | 태그: G, A · feature
- 목표: DEV-23 결정대로 로더(`utils/DashLicense` 신설)를 만들고 AboutDialog 가 그것을 읽는다. `DASH_LICENSE_EXPIRY_DATE` 컴파일 정의와 CMake 캐시 변수를 제거한다. 서명 파일이면 발급 도구(tools/) 와 검증을 포함한다.
- 완료 기준: 1. 재빌드 없이 만료일 변경이 About 에 반영 2. `git grep -n DASH_LICENSE_EXPIRY_DATE` 0건 — **README.md:134(옵션 표) · :145(예제) 포함** 3. 손상·부재 입력의 동작이 DEV-23 결정과 일치(단위 테스트 1건, Level 1) 4. README 의 라이선스 옵션 서술이 CMake 정의와 일치 — 지금 표의 기본값 `"2026-06-30"` 이 `CMakeLists.txt:107` 의 `"2026-08-31"` 과 어긋나 있다(DEV-c39)
- 변경 범위: utils/DashLicense.{h,cpp} (신규) · view/dialog/AboutDialog.{h,cpp} · CMakeLists.txt · README.md · main.cpp(기동 차단 시) · tests/ (신규 1건) · tools/ (서명 발급 시)
- 선행: DEV-23
- 충돌: DEV-21(CMakeLists.txt · README.md 의 같은 옵션 표) · DEV-11(CMakeLists.txt) · DEV-22(AboutDialog.cpp) · B2 교집합: main.cpp → EXE-02 EXE-06 PRJ-06 PRJ-14 UIC-05 UIC-26 · CMakeLists.txt → DEV-25 MOR-06 MOR-07 UIC-02 · README.md → DEV-01 DEV-02 DEV-12 MOR-07 · AboutDialog.cpp → PRJ-14 · PR #658(CMakeLists.txt) · PR #654(CMakeLists.txt)
- 흡수: #484-2 · DEV-c35, c39
- 비고: 설정 키 형식이면 S 로 줄어든다. `DEFAULT_LICENSE_TYPE` 도 같은 소스로 옮긴다 — README 표의 세 줄(:133-135)과 예제(:144-146)가 한 덩어리라 같이 걷는다. 파일 머리말의 clang-format 공통 제약이 `AboutDialog.cpp`·`main.cpp` 에 걸린다.

### DEV-25 · 현 vcpkg VTK 포트에 `IOHDF` 모듈이 있는지 실측한다 (#411 결정 1)
- 종류: INV | 규모: S | 태그: F
- 목표: GUI 는 VTK 를 직접 선언하지 않고 mesh-ops/preprocessor 포트를 통해 default registry baseline `04a9d8e5` 의 vtk 9.3(feature `ioocct opengl openmp qt tbb utf8`) 을 받는다. Windows 빌드 트리의 `vcpkg_installed/x64-windows-dashopti/lib` 에 `vtkIOHDF-9.3.lib` 과 VTK targets 의 `VTK::IOHDF` 가 있는지 확인한다. 있으면 `find_package(VTK COMPONENTS …)` 에 `IOHDF` 1줄 추가로 끝. 없으면 vtk 포트 feature 추가가 mesh-ops/preprocessor 의 feature 문자열(ABI)에도 들어가야 하므로 메타 저장소·캐시 재워밍 비용을 기록한다.
- 완료 기준: 실측 기록(lib·타깃 유무 · VTK 버전) · 있으면 CMake 1줄 PR 범위 명시 / 없으면 EXT(메타 저장소 feature 추가 + 재워밍) 항목 발행 여부와 비용 — PRE-29 의 입력
- 변경 범위: 실측만 — 후속 시 CMakeLists.txt:300-329 (`find_package(VTK REQUIRED COMPONENTS …)` 28종) 1줄
- 선행: -
- 충돌: PR #654(CMakeLists.txt — 후속 PR 시) · DEV-11 · DEV-21(CMakeLists.txt) · B2 교집합: CMakeLists.txt → DEV-24 MOR-06 MOR-07 UIC-02 · PR #658(CMakeLists.txt)
- 흡수: #411 결정 1 (DEV 몫, PRE-c58 이관) · DEV-c38
- 비고: 현 macOS 체크아웃에는 vcpkg_installed 가 없어 Windows 러너에서 본다. GUI 단독 feature 추가는 불가 — CMakeLists.txt:297-299 주석("다른 VTK 를 가리키면 두 포트와 ABI 가 갈린다").

## 대응표

| 원천 | 항목 | 비고 |
|---|---|---|
| #330 | DEV-01 · DEV-02 · DEV-03 | 정책 DEC + 즉시 조치(레이아웃) + 선택지 C/D 의 EXT |
| #335 | DEV-04 · DEV-05 · DEV-06 · DEV-07 · DEV-08 | 4건 전부 EXT(DashOpti_Registry · 메타). #335-4 는 DEC 선행 |
| #335-1 | DEV-04 | |
| #335-2 | DEV-05 | |
| #335-3 | DEV-06 | GUI vcpkg.json 1줄 동기 포함 |
| #335-4 | DEV-07 · DEV-08 | |
| #336 | DEV-10 · DEV-11 · DEV-12 | DEV-09 는 결번(DEV-12 병합) |
| #336-1 | DEV-12 | 저장소 삭제 대상 없음 — 공지(ops) + 같은 파일의 external 서술 정리. 구 DEV-09 결번 |
| #336-2 | DEV-10 | 현재 14곳(실코드 13 + 주석 1), PR #655 머지 뒤 12곳 |
| #336-3 | DEV-11 | PR — CMake 4.3.3 이 VC145 를 알아 차단 해제(구 INV). `cmake_minimum_required` 범프 동반 |
| #336-4 | DEV-12 | 2건 삭제 + build-environment.md 승격. 운영 지식 추출 티켓은 불요(CMake 주석이 정본) |
| #372 | DEV-14 · DEV-15 · DEV-16 | CI 부재 — 결정 → 워크플로 → 측정 순. 3단 분할 유지(#372 본문이 "CI 구축 자체 = 선행 조건 · 범위 밖" 으로 못 박아 개념이 둘). `tests/e2e` 의 Level 3 등록 여부는 DEV-14 결정 · DEV-15 완료 기준 4. Level 2·3 한도는 두지 않음(DEV-16 비고) |
| #386 | DEV-17 | 보류 결정은 기록 완료(해소됨). 남은 것은 정렬 착수 방식 DEC |
| #489 | DEV-18 · DEV-19 | 분할 유지 — **DEV = 인프라**(grep 게이트 · 환경 변수 등록 자동 수집), **커버리지 = 각 모듈**. 도메인 커버리지(CAD-U5 · OPT-U3 · BLD · RUN · DOE)는 범위밖 → 각 모듈(CAD-11 · OPT-20 존재, DEV-c24). CON-U5 는 해소됨(#565, DEV-c25) |
| #483 | DEV-20 | 로컬 STL 경로 1건. 플레이스홀더 문구·기본 경로·Dev 자산은 해소됨. Optimizer 샘플 제약 행은 범위밖 → OPT(DEV-c30) |
| #484 | DEV-21 · DEV-22 · DEV-23 · DEV-24 | 버전 리소스 + 앱 메타 · Build Date 버그 · 만료일 DEC + 로더 |
| #484-3 타임아웃 상수화 | 항목 없음 | 27곳 12파일, 대부분 UI 지연·애니메이션 간격 — 공용 헤더 중앙화 가치 낮음. 프로세스 대기 8곳(AnsysMotion 6 · ExtensionProcess 1 · ProcessKill 1)은 EXE 외부 프로세스 표준 소관(DEV-c37) |
| DEV-c21(부수) | DEV-13 | 원천 이슈 없음 — 깨진 링크·낡은 수치가 실재해 유지(검토 확인) |
| DEV-c39(부수) | DEV-24 · DEV-21 | 원천 이슈 없음 — README 옵션 표 기본값이 CMake 와 불일치. DEV-24 의 `DASH_LICENSE_EXPIRY_DATE` 0건 기준이 README 를 포함해야 성립 |
| #411 결정 1 (PRE-c58 이관) | DEV-25 | vtkIOHDF 가용 실측 — PRE-29 입력 (DEV-c38) |
