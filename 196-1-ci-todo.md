# DashGUI2 CI 구축 TODO — lint 즉시 가동 → vcpkg 전환 → 캐싱 → 빌드 CI

> 원본: 사전조사 Issue #196 — 본문을 이 페이지로 이관한 뒤 Issue 삭제 (2026-08-24). **본 페이지가 정본**

> 연관 Issue: #64
> 상태: **보류 (2026-07-21) — CI 파이프라인 미구축 결정(백로그 개정 29).** 본 문서는 CI 착수 시 선택 참고자료로 존치. W9·grep 게이트는 CI 없이 로컬 훅/수동으로도 가능. 단 ②③(vcpkg 전환)은 CI와 무관한 N1(의존성 관리) 몫이므로 그 부분은 유효 — 로컬 초안 (GitHub Wiki 원격 미생성)
> 기반 문서: [200-3-prioritized-backlog](200-3-prioritized-backlog.md) (W9 · 보류 ③) · [195-1-backlog-code-evidence](195-1-backlog-code-evidence.md) (W9 실증)
> 조사 시점: 2026-07-13 — `DashGUI2/CMakeLists.txt` · `DashOpti_CoreLib` · `DashOpti_Registry` 실측

---

## 0. 결론 먼저

CI는 4단계로 세우며, 각 단계는 앞 단계 없이 착수할 수 없는 순서다:

| 단계 | 내용 | 착수 가능 시점 | 규모 |
|---|---|---|---|
| ① lint CI | clang-format 검사 + grep 게이트 (cloud runner) | **즉시** — 전제는 `.clang-format` 커밋(W5)뿐 | 0.5일 |
| ② vcpkg 전환 | GUI를 manifest 모드로, 내부 모듈은 레지스트리 포트로 | CoreLib 패턴 복제 — 바로 시작 가능 | 2\~4일 + 내부 포트 리드타임 |
| ③ 바이너리 캐싱 | GitHub Packages NuGet 피드 권장 | ②와 병행 | 0.5\~1일 |
| ④ configure→build→test CI | cloud runner에서 풀빌드 + ctest | ②·③ 완료 후 | 1\~2일 |

**핵심 발견 3가지** (이 문서의 요지):

1. **정답 패턴이 이미 사내에 있다** — `DashOpti_CoreLib`(vcpkg manifest + `CMakePresets.json`)와 `DashOpti_Registry`(커스텀 vcpkg git 레지스트리, `core-lib`·`reader-writer` 포트 운영 중). GUI의 전환은 발명이 아니라 **기존 패턴으로의 합류**다.
2. **GUI는 이미 레지스트리에 있는 패키지를 수동 드롭으로 소비 중** — `core-lib`·`reader-writer`를 `external/`의 HINTS 경로로 받는다. 인프라판 "정본과 사본의 공존"(W8과 동형)이며, 이 두 개는 포트 작성조차 필요 없이 소비 방식만 바꾸면 된다.
3. **오픈소스 의존 4종(Qt·VTK·OCCT·Eigen)은 전부 vcpkg 공식 포트가 존재** — 관건은 포트 유무가 아니라 빌드 시간이고, 그 답이 ③ 바이너리 캐싱이다.

self-hosted runner는 **지금 결정할 필요가 없다** — 2-5절 한 단락 참조.

---

## 1. 현황 실측

### 1-1. 의존성 전수 — `external/` 수동 드롭 14종

`CMakeLists.txt:142-224` 기준. "OneDrive 수동 배포"의 실체가 이 목록이다:

| 분류 | 이름 (버전) | vcpkg 경로 | 처리 |
|---|---|---|---|
| 오픈소스 | Qt 5.15.16 (Core·Gui·Widgets·Xml·Svg·AxContainer·Concurrent) | 공식 `qt5-base`·`qt5-svg`·`qt5-activeqt` | manifest 선언. vcpkg qt5는 KDE 유지 5.15 패치 계열 — 5.15.16과의 패치 격차 확인 |
| 오픈소스 | VTK 9.4 (21 컴포넌트, `GUISupportQt`·`RenderingQt`·`IOOCCT` 포함) | 공식 `vtk` (+`qt` feature) | manifest 선언. `IOOCCT` 모듈의 feature 노출 여부 확인 — 없으면 overlay port로 보강 |
| 오픈소스 | OpenCASCADE 7.9.1 | 공식 `opencascade` | manifest 선언 |
| 오픈소스 | Eigen 3.4.0 (헤더 온리) | 공식 `eigen3` | manifest 선언 |
| 내부 (포트 있음) | `core-lib` · `reader-writer` | **레지스트리에 이미 존재** (baseline 2026-04-15.1 / 2026-05-03.0) | HINTS 제거, 레지스트리 소비로 전환 — 즉시 가능 |
| 내부 (포트 없음) | DashOptiMorphing 0.0.4 · DashOptiDOE 1.0.1 · DashOptiReaderWriter 1.0.0 · DashOptiFELauncher 1.0.0 · DashOptiPreprocessor 1.2.2 · DashGizmo · preprocessor | — | 레지스트리 포트 신규 작성 7종 — Registry README의 미결 항목(RW·FL 등)과 같은 트랙 |
| 도구 (EXE) | DashOptiPythonExtensions · EncodeHeaderTool · `additional/` | — | 포트화 또는 GitHub Release 아티팩트로 — 빌드에 링크되지 않으므로 후순위 |

### 1-2. 이미 보유한 자산 (재사용 대상)

- **Registry** — git 레지스트리 구조(`ports/` + `versions/baseline.json`), `vcpkg_from_git` 포트 패턴(REF 고정), `pr-update-ports.yml`(REF 검증 자동화 워크플로) 운영 중.
- **CoreLib** — `vcpkg.json`(manifest) + `vcpkg-configuration.json`(MS 기본 레지스트리 + 커스텀 레지스트리) + `CMakePresets.json`(`$env{VCPKG_ROOT}` 툴체인, Ninja/MSVC, 테스트 프리셋까지). GUI에 이식할 원본.
- **GUI에 없는 것** — `vcpkg.json`, `CMakePresets.json`, `.github/` 전부 부재. `cmake_minimum_required 3.10`은 프리셋(3.19+)·manifest 사용 전 상향 필요.

---

## 2. 단계별 TODO

### 2-1. 단계 ① — lint CI (즉시)

`.github/workflows/lint.yml` 하나. 컴파일이 없어 외부 라이브러리와 무관하고, 텍스트 검사라 `ubuntu-latest`가 가장 빠르고 저렴하다.

```yaml
name: lint
on: [pull_request, push]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: clang-format check
        run: |
          clang-format --version   # 러너 기본 탑재. 버전 고정 필요 시 설치 스텝 추가
          git ls-files '*.cpp' '*.h' '*.hpp' | xargs clang-format --dry-run --Werror
      - name: grep gate
        run: ./scripts/grep-gate.sh
```

선행 산출물 2개:

- `.clang-format` — 현행 스타일(m_+camelCase) 캡처본 (W5 산출물, 이 파일이 없으면 검사 자체가 무의미)
- `scripts/grep-gate.sh` — W9 ②의 카운트 4종을 기준값과 비교, 증가 시 exit 1: `model/` processEvents(41) · `DashExtensionProcess.cpp` 외 QProcess · model→view include(24) · `::Mgr()`(291). 기준값은 스크립트 상수가 아닌 별도 baseline 파일로 두어 티어 DoD 달성 시 갱신 커밋이 명시적으로 남게 한다.

주의: clang-format은 **버전에 따라 포맷 결과가 달라진다** — 러너 기본 버전을 확인해 로컬과 메이저 버전을 맞추거나, 워크플로에서 버전을 고정 설치.

### 2-2. 단계 ② — vcpkg manifest 전환

GUI 저장소에 3개 파일 추가 (CoreLib에서 복제 후 수정):

1. `vcpkg.json` — 골격:

```json
{
    "name": "dashopt-gui",
    "version-string": "dev",
    "dependencies": [
        "qt5-base", "qt5-svg", "qt5-activeqt",
        { "name": "vtk", "features": ["qt"] },
        "opencascade", "eigen3",
        "core-lib", "reader-writer"
    ]
}
```

2. `vcpkg-configuration.json` — CoreLib 것을 그대로 복사하고 `packages`에 GUI가 쓸 내부 패키지들을 추가.
3. `CMakePresets.json` — CoreLib 패턴 복제 (`CMAKE_TOOLCHAIN_FILE = $env{VCPKG_ROOT}/...`, `VCPKG_MANIFEST_MODE=ON`). 로컬과 CI가 같은 프리셋을 쓰는 것이 재현성의 핵심.

CMakeLists 수정 — 전부 "경로 하드코딩 제거" 방향:

- `set(Qt5_DIR ...)` `HINTS ${EXTERNAL_DIR}/...` 류 제거 → 툴체인이 `find_package`를 해석
- DLL 복사 \~220행(`:261-480`) → vcpkg applocal 배포 + `windeployqt`로 대체 (W5의 "DLL 복사 함수화"가 아예 불필요해짐)
- `cmake_minimum_required` 3.10 → 3.25+ 상향

내부 포트 7종 작성 — 기존 `core-lib` 포트가 템플릿(`vcpkg_from_git` + REF 고정 + `versions/` 등재). 전제: 각 모듈 저장소가 `cmake_install`로 config 패키지를 내보낼 것 (이미 `find_package(... CONFIG)`로 소비되고 있으므로 대부분 충족). **리드타임이 지배하는 작업**이라 (모듈별 저장소 협의) 가장 먼저 킥오프.

전환은 빅뱅이 아니어도 된다: **오픈소스 4종 먼저 vcpkg로 옮기고 내부 모듈은 `external/` HINTS를 임시 유지**하는 혼합 단계가 가능 — configure CI는 이 시점부터 이미 동작한다(내부 모듈 드롭을 CI 캐시에 넣는 편법 없이 가려면 내부 포트 완료 필요).

### 2-3. 단계 ③ — 바이너리 캐싱

Qt+VTK+OCCT를 CI에서 소스 빌드하면 시간 단위 → 캐싱 없이는 ④가 비실용적. 선택지:

| 방식 | 설정 | 용량/보존 | 판정 |
|---|---|---|---|
| GitHub Packages NuGet 피드 | `VCPKG_BINARY_SOURCES`에 nuget 소스 + `GITHUB_TOKEN` | 조직 공유, 무기한 | **권장** — 러너·로컬 모두에서 재사용 |
| GitHub Actions 캐시 (`x-gha`) | 워크플로에서 토큰 export 한 스텝 | repo당 10GB, 7일 미접근 시 삭제 | 보조 — 설정 최소지만 Qt+VTK 규모에 빠듯 |
| 파일 공유 (`files,...`) | 네트워크 드라이브 경로 | 사내 자원 | 로컬 개발자 간 공유엔 유효, CI에는 부적합 |

설정은 환경변수 한 줄이다:

```
VCPKG_BINARY_SOURCES=clear;nuget,https://nuget.pkg.github.com/NumeRealWorks/index.json,readwrite
```

**첫 시딩은 로컬 개발 PC에서 가능** — 어차피 로컬에서 한 번 빌드하므로, 같은 triplet(`x64-windows`)이면 그 산출물을 피드에 올려 CI가 첫 실행부터 복원하게 할 수 있다.

### 2-4. 단계 ④ — configure → build → test CI

②·③이 끝나면 `build.yml`은 정형이다:

```
[trigger] pull_request (경로 필터: *.cpp *.h CMakeLists.txt vcpkg.json)
   ▼
[job: windows-latest]
   │   1. checkout + vcpkg 준비 (baseline 커밋 고정)
   │   2. cmake --preset msvc-release   ← configure 검사는 이 단계가 겸함
   │   3. cmake --build --preset ...    ← 캐시 히트 시 GUI 코드만 컴파일
   │   4. ctest --preset ...            ← W9의 QTest 3건부터
   ▼
[gate] 실패 시 merge 차단 (branch protection)
```

- ② 완료 전까지 configure 검사는 **로컬 pre-commit 훅으로 임시 운영** (라이브러리가 있는 개발 PC에서만 유효).
- 티어 DoD 달성 시마다 grep-gate baseline 갱신 — 백로그 6절 "게이트 봉인"의 실행 지점이 이 저장소의 baseline 파일이 된다.

### 2-5. self-hosted runner — 간단 언급

지금 결정할 사안이 아니다. 필요해지는 조건은 둘뿐 — 재배포 불가 상용 SDK(NX 계열 등)가 빌드에 필요해질 때, 또는 cloud runner 비용/시간을 사내 유휴 PC로 흡수하고 싶을 때. private 저장소라 보안 리스크는 낮고, 등록은 Settings → Actions → Runners의 스크립트 실행 + `runs-on: [self-hosted, windows]` 라우팅이 전부다. cloud + 캐싱으로 시작하고, 위 조건이 실제로 발생하면 그때 추가한다.

---

## 3. 실행 순서 요약

```
[즉시] ① lint CI
   │   .clang-format(W5) + grep-gate 스크립트 → lint.yml (ubuntu-latest)
   │   ※ 내부 포트 7종 킥오프도 지금 — 리드타임이 지배 (W13/W18 결정분과 같은 논리)
   ▼

[단기] ② vcpkg 전환 (혼합 단계 허용)
   │   1. GUI에 manifest·configuration·presets 3파일 (CoreLib 복제)
   │   2. 오픈소스 4종 먼저 → core-lib·reader-writer 소비 전환 → 내부 포트 순차 합류
   │   3. CMakeLists 경로 하드코딩·DLL 복사 제거
   ▼

[병행] ③ 바이너리 캐싱
   │   GitHub Packages NuGet 피드 + 로컬 첫 시딩
   ▼

[승격] ④ build.yml — configure·build·ctest + branch protection
       티어 DoD 달성 → grep-gate baseline 갱신 (게이트 봉인)
```

---

## 다음 단계

- [ ] `.clang-format` 캡처·커밋 (W5) → lint.yml 작성 (단계 ①)
- [ ] grep-gate 스크립트 + baseline 파일 작성 (W9 ②)
- [ ] 내부 모듈 7종 포트화 킥오프 — 모듈별 저장소 install/export 상태 확인 (Registry 미결 항목과 합류)
- [ ] GUI `vcpkg.json`·`vcpkg-configuration.json`·`CMakePresets.json` 작성 (CoreLib 복제)
- [ ] Qt 5.15.16 vs vcpkg qt5 패치 격차 · VTK `IOOCCT` feature 노출 여부 확인 (1-1절 미결 2건)
- [ ] GitHub Packages NuGet 피드 생성 + `VCPKG_BINARY_SOURCES` 배선
- [ ] wiki 원격 생성 시 본 문서 push + Issue #64에 링크 comment
