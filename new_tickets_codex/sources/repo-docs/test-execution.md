# 테스트 실행 경로

> 상태: 도입 (2026-09-14)
> 구현 이슈: [#359](https://github.com/NumeRealWorks/DashOpti_GUI/issues/359)
> 레벨 정의와 분류 기준: [test-levels.md](test-levels.md)

테스트를 무엇이 빌드하고 무엇이 실행하는지, 각 스크립트가 정확히 무슨 일을 하는지 정리한다. 레벨을 **어떻게 나누는지**는 [test-levels.md](test-levels.md) 가 다룬다. 이 문서는 **어떻게 돌리는지**만 다룬다.

## 1. 구성 요소

| 파일 | 역할 |
|---|---|
| `tests/CMakeLists.txt` | 독립 CMake 프로젝트(`DashOptiTests`). 실행 파일 6개와 `add_test` 등록. Qt Core + Test 만 쓰고 VTK/OCCT 를 안 쓴다 — **앱 빌드 없이도 어느 호스트에서나 빌드·실행된다** |
| `tests/TestLevel.h` | 레벨 게이트. `DASH_TEST_LEVEL` 을 읽어 각 서브테스트의 `QSKIP` 여부를 정한다 |
| `tests/BLACKLIST` | 알려진 실패 (#536). 여기 적힌 케이스는 실패해도 BFAIL 로 보고되고 실행을 실패시키지 않는다. 등록·해제는 사람이 한다 |
| `scripts/run_tests.ps1` | 전체 경로. configure → build → ctest 를 한 번에 한다 |
| `scripts/hooks/run-test-level.sh` | 경량 경로. 이미 구성된 빌드 트리를 재사용해 build → ctest 만 한다 |
| `scripts/hooks/run-format-checks.sh` | 스테이지된 C/C++ 파일의 서식·인코딩 검사 (#321). 테스트와 무관하며 여기서는 호출 순서만 다룬다 |
| `.githooks/pre-commit` | `run-format-checks.sh` 뒤에 `run-test-level.sh` 를 Level 1 로 호출 |
| `.githooks/pre-push` | `run-test-level.sh` 를 Level 2 로 호출 |

`tests/` 는 루트 `CMakeLists.txt` 에 `add_subdirectory` 되어 있지 **않다.** 의도된 분리다 — 앱 빌드(VTK/OCCT/vcpkg 트리 필요)와 테스트 빌드가 서로를 요구하지 않는다.

## 2. 두 갈래

| | `run_tests.ps1` | `run-test-level.sh` |
|---|---|---|
| configure | **한다** (매번) | 안 한다 |
| build | 한다 | 한다 |
| ctest | 한다 | 한다 |
| Qt 경로 해석 | 자동 탐색 | 불필요 (캐시에 이미 있음) |
| 쓰는 곳 | 첫 구성, `CMakeLists.txt` 변경 후, 수동 실행 | git 훅, 반복 확인 |

**같은 빌드로 여러 번 돌릴 때 `run_tests.ps1` 을 반복해서 쓰면 안 된다.** 매 실행마다 configure 를 다시 하므로 레벨이나 필터만 바꿔 가며 확인하는 용도로는 비싸다.

## 3. `scripts/run_tests.ps1`

어디서 실행해도 된다. 경로는 스크립트 위치(`<repo>/scripts`) 기준으로 해석된다.

### 파라미터

| 파라미터 | 기본값 | 설명 |
|---|---|---|
| `-Config` | `Release` | `Release` / `Debug` / `RelWithDebInfo` |
| `-Level` | 미설정 | 누적 서브테스트 레벨 1~3. 미설정이면 **전부 실행** |
| `-Filter` | 없음 | `ctest -R` 에 넘길 정규식. 실행 **파일**을 고른다 |
| `-QtDir` | 자동 | Qt 설치 접두. 아래 자동 탐색 참고 |
| `-BuildDir` | `tests/build-tests` | CMake 빌드 트리 |
| `-Clean` | off | 구성 전에 빌드 트리를 지운다 |
| `-Detail` | off | 모든 출력을 보여준다. 끄면 결과 줄만 남긴다 |
| `-CMakeArgs` | 없음 | configure 단계에 그대로 덧붙일 인자 |

`-Level` 과 `-Filter` 는 **직교한다.** `-Level` 은 실행 파일 *안의* 서브테스트를 거르고(`DASH_TEST_LEVEL` → `TestLevel.h`), `-Filter` 는 ctest 가 어떤 실행 *파일*을 돌릴지 고른다. 함께 주면 둘 다 적용된다.

### 하는 일

1. **Qt 탐색** — `-QtDir` 이 없으면 `out/build/*/vcpkg_installed/x64-windows-dashopti` 의 첫 항목을 쓴다. 앱이 쓰는 Qt 와 같은 것을 테스트도 쓰게 하려는 것이다. 앱을 한 번도 configure 하지 않았으면 여기서 멈추고 `-QtDir` 을 요구한다.
2. **cmake/ctest 탐색** — PATH 에서 찾고, 없으면 `vswhere` 로 Visual Studio 설치 경로를 찾아 번들된 cmake 를 쓴다. ctest 는 cmake 옆에서 찾고, 없으면(scoop·Chocolatey 의 shim 인 경우) PATH 로 되돌아간다.
3. **configure** — `cmake -S tests -B <BuildDir> -DCMAKE_PREFIX_PATH=<QtDir>`
4. **build** — `cmake --build <BuildDir> --config <Config>`
5. **ctest** — `--test-dir <BuildDir> -C <Config> -V`. `-V` 는 **항상** 켠다. QTest 는 서브테스트(함수) 단위 결과를 실행 파일의 표준 출력으로 내보내는데, ctest 가 `-V` 없이는 그걸 숨기기 때문이다.
6. **출력 정리** — `-Detail` 이 없으면 `PASS` / `FAIL!` / `SKIP` / `Totals` / 실패 위치 줄만 남기고, ctest 자체의 진행 잡음과 실행 파일의 기타 출력(QWARN, stderr 폴백 등)은 버린다.

각 단계는 종료 코드를 확인하고 실패하면 그 코드로 즉시 끝낸다.

> PowerShell 5.1 특이사항: 네이티브 도구가 진행 상황과 오류를 stderr 로 내보내는데, `$ErrorActionPreference = 'Stop'` 상태에서는 그게 종료 코드 검사 전에 종료 오류로 바뀐다. 그래서 외부 명령을 부르기 직전에 `Continue` 로 낮춘다.

## 4. `scripts/hooks/run-test-level.sh`

POSIX sh. 인자 하나(레벨)를 받는다. 훅이 부르지만 직접 불러도 된다.

```sh
./scripts/hooks/run-test-level.sh 1
```

### vcvars 가 필요 없는 이유

빌드 트리의 생성기가 **Visual Studio(msbuild)** 다. msbuild 가 생성된 프로젝트 파일에서 툴체인을 스스로 잡으므로, MSVC 개발자 환경(`vcvars64.bat`)을 미리 잡을 필요가 없다. Ninja 생성기였다면 필요했을 것이다.

cmake 와 ctest 의 절대 경로는 `CMakeCache.txt` 가 들고 있다 (`CMAKE_COMMAND`, `CMAKE_CTEST_COMMAND`). 그래서 **PATH 에 아무것도 없는 Git Bash 에서 그대로 동작한다.** git 훅이 도는 환경이 정확히 그렇다.

### 하는 일

1. 저장소 루트와 빌드 디렉터리를 정한다 (`git config hooks.testBuildDir`, 기본 `tests/build-tests`).
2. `CMakeCache.txt` 가 없으면 **안내 한 줄을 내고 통과한다** (아래 정책).
3. 캐시에서 cmake/ctest 경로를 읽는다. 유효하지 않으면 역시 통과한다.
4. `cmake --build` — 실패하면 **차단**하고, 오류를 볼 수 있는 명령을 그대로 출력한다.
5. `DASH_TEST_LEVEL=<레벨> ctest --output-on-failure` — 실패하면 **차단**한다.

### 실패 정책

| 상황 | 동작 | 이유 |
|---|---|---|
| 빌드 디렉터리 없음 | 안내 후 **통과** | 환경 문제다. 막으면 팀원이 곧바로 `--no-verify` 를 습관화해 훅 전체가 무력화된다 |
| `CMakeCache.txt` 의 cmake/ctest 경로가 깨짐 | 안내 후 **통과** | 위와 같음 |
| 빌드 실패 | **차단** | 코드 문제다 |
| 테스트 실패 | **차단** | 코드 문제다 |

### 재정의

| `git config` 키 | 기본값 |
|---|---|
| `hooks.testBuildDir` | `tests/build-tests` |
| `hooks.testConfig` | `Release` |

## 5. git 훅

한 클론당 1회:

```bash
git config core.hooksPath .githooks
```

| 훅 | 하는 일 |
|---|---|
| `.githooks/pre-commit` | `run-format-checks.sh` → `run-test-level.sh 1` |
| `.githooks/pre-push` | `run-test-level.sh 2` |

`pre-commit` 의 순서는 비용순이다. 서식 검사가 먼저 걸리면 증분 빌드를 시작하지도 않는다. `pre-push` 는 git 이 stdin 으로 넘기는 ref 목록을 읽어서 버린다 — 안 읽으면 git 쪽 쓰기가 막힐 수 있다.

**훅은 게이트가 아니다.** `--no-verify` 로 우회된다. 훅은 실수 방지이고, 강제는 CI 가 한다. 둘은 대체가 아니라 계층이다.

### 비용

훅 비용의 대부분은 테스트 실행이 아니라 **그 앞의 증분 빌드**다. Level 1 은 프로세스도 스레드도 쓰지 않아 실행이 사실상 공짜이고, 남는 것은 빌드 시간이다. 그 빌드가 컴파일 오류를 먼저 잡아준다는 점에서 그 자체로 값이 있다.

절대 시간은 기계마다 다르므로 여기 적지 않는다. 각자 기계에서 한 번 재 보고, 감당하기 어려우면 `hooks.testBuildDir` 를 조정하거나 훅을 끄면 된다.

## 6. 알려진 실패 (`tests/BLACKLIST`)

고칠 때까지 실패하는 것이 정상인 케이스를 적어 두는 곳이다. 적힌 케이스는 **BFAIL** 로 보고되고 실행을 실패시키지 않는다.

```
[lanesRunConcurrently]
*
```

- Qt Test 가 `:/BLACKLIST` 리소스에서 읽는다. `tests/CMakeLists.txt` 의 블록이 이 파일 하나를 모든 `test_*` 실행 파일에 넣는다(`cmake_language(DEFER)` 라 그 블록의 위치는 상관없다) — 항목이 **함수 이름**으로 매칭되므로 실행 파일별로 나눌 필요가 없다.
- 조건 줄(`*`)은 환경을 좁힐 수 있다: `windows`, `linux`, `macos`, `msvc` 등.
- `-skipblacklisted` 를 실행 파일에 주면 BFAIL 로 돌리는 대신 아예 건너뛴다.

**등록도 해제도 사람이 한다.** 무엇도 자동으로 붙거나 떨어지지 않는다. 등록할 때 이슈 번호와 증상을 주석으로 같이 남긴다 — 고쳐진 등록은 `BPASS` 로 **조용히** 남으므로(실행을 실패시키지 않는다) 그 주석이 유일한 해제 창구다.

```
BPASS  : TestMorphingService::solverBudgetSplitsPhysicalCoresAcrossLanes()
Totals: 13 passed, 0 failed, 0 skipped, 1 blacklisted
```

`0 failed` 다. BPASS 는 실행을 실패시키지 않는다 — 그래서 조용하다.

**등록은 그 케이스 전체를 덮는다.** 적어 둔 사유와 무관한 새 실패도 같이 묻힌다 — 어떤 이슈 때문에 등록해 둔 케이스가 나중에 널 역참조로 죽어도 `BFAIL` 한 줄로 지나간다. 오래 두지 말고 이슈를 닫을 때 같이 지운다.

**조건 줄은 반드시 `[...]` 다음에 온다.** 블록 없이 조건 줄만 적으면 그 실행 파일이 통째로 걸린다 — `*` 한 줄이 `test_morphing_service` 를 `2 passed, 12 blacklisted` 로 만들고 ctest 는 100% 통과로 보고했다.

## 7. 스크립트 없이 직접 실행

이미 구성된 빌드 트리가 있을 때.

```powershell
# cmake/ctest 경로는 CMakeCache.txt 에서 얻는다 (PATH 에 없어도 된다)
$cmake = (Select-String '^CMAKE_COMMAND:INTERNAL=' tests/build-tests/CMakeCache.txt).Line -replace '.*='
$ctest = (Select-String '^CMAKE_CTEST_COMMAND:INTERNAL=' tests/build-tests/CMakeCache.txt).Line -replace '.*='

& $cmake --build tests/build-tests --config Release
$env:DASH_TEST_LEVEL = '1'
& $ctest --test-dir tests/build-tests -C Release -V
$env:DASH_TEST_LEVEL = ''
```

`DASH_TEST_LEVEL` 이 없거나 1~3 밖의 값이면 **전부 실행**한다. 기존 동작이 기본이다.

## 8. 빌드 디렉터리

`tests/build-tests` 다. `build-*/` 패턴으로 git 에서 제외된다.

지워도 된다 — `run_tests.ps1` 이 다시 구성한다. 다만 지운 직후에는 훅이 "빌드 디렉터리 없음" 으로 통과만 하므로, 한 번은 `run_tests.ps1` 을 돌려 재구성해야 훅이 다시 일한다.

앱 본체 빌드(`out/build/...`, vcpkg 트리)와는 별개다. 테스트 빌드 트리를 지워도 앱 빌드에는 영향이 없다.
