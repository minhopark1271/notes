# 개발 환경 셋업

> 구현 이슈: [#388](https://github.com/NumeRealWorks/DashOpti_GUI/issues/388)
> 배경과 규칙: [build-environment.md](scratchpad/build-environment.md)

새 PC 에서 첫 빌드까지 가는 절차를 적는다. 사람과 에이전트가 함께 참조한다. 절차는 두 스크립트가 나눠 맡는다.

- `scripts\setup-environment.ps1`: 선행 조건을 확인하고 로컬 설정을 한다. configure 와 build 는 하지 않는다.
- `scripts\build-app.ps1`: `local-msvc-release` 를 configure 하고 build 한다.

## 1. 이 문서의 범위

이 문서가 다루는 것:

- 사람이 먼저 갖춰야 하는 것
- 두 스크립트의 실행 순서, 출력 읽는 법
- 막혔을 때 증상에서 조치로 가는 길
- 에이전트가 실행할 때만 다른 제약

다른 문서로 넘기는 것:

- 환경 조건의 배경과 규칙, 오류 문구별 진단: [build-environment.md](scratchpad/build-environment.md)
- 툴셋 버전, vcpkg 커밋 같은 고정값과 각 정본 위치의 목록: build-environment.md 의 환경 요구사항 표
- 빌드 옵션과 preset 종류: 루트 `README.md` 의 How to Build
- git 훅과 테스트 실행: [test-execution.md](test-execution.md)
- clang-format 규칙: [coding-convention.md](coding-convention.md)

## 2. 사람이 먼저 해야 하는 것

스크립트는 아래를 확인만 한다. 설치하거나 로그인해 주지 않는다. 빠져 있으면 스크립트가 FAIL 과 안내를 찍는다.

### 2.1 Visual Studio 2026 (18.9.2) Build Tools

이 문서가 말하는 VS 버전(18.9.2)의 정본은 `README.md` 의 Prerequisites 아래 "VS 설치 파일" 항목이다. `README.md` 표의 "Visual Studio 2026" 이 이것이다.

1. 2.3 과 2.6 을 먼저 끝낸 뒤, 사내 버킷에서 설치 파일을 받는다. 버킷은 gcloud 로그인과 읽기 권한이 있어야 열린다. 위치와 명령은 `README.md` 의 "VS 설치 파일" 을 따른다.
2. 설치할 때 "C++ CMake tools for Windows" 구성요소를 고른다. Ninja 와 cmake 가 여기 들어 있다.
3. MSVC 툴셋 `14.51.36231` 을 추가한다. 값의 정본은 `triplets/x64-windows-dashopti.cmake` 다.
4. 설치 뒤 자동 업데이트를 끈다.

버전을 고정하는 이유는 하나다. MSVC 버전이 vcpkg ABI 해시의 입력이라서, 버전이 달라지면 바이너리 캐시가 전부 miss 된다. 자세한 것은 [build-environment.md](scratchpad/build-environment.md) 를 본다.

안 하면: `Visual Studio` 항목이 FAIL 이다. 설치가 없는지, 빠진 구성요소가 무엇인지 함께 알려 준다. 자동 업데이트는 판별할 수 없어서 항상 안내 줄만 나온다.

### 2.2 Git for Windows

`git` 이 PATH 에 있어야 한다. git 훅이 쓰는 `sh` 도 Git for Windows 에 들어 있다.

안 하면: `git` 항목이 FAIL 이다. `sh` 만 없으면 안내 줄만 나온다. 빌드에는 영향이 없고 커밋 때 훅이 실패한다.

### 2.3 Google Cloud SDK 와 gsutil

Cloud SDK 를 설치하고 `gcloud components update` 로 gsutil 을 요구 버전 이상으로 올린다. 요구 버전의 정본은 `<VCPKG_ROOT>/scripts/vcpkg-tools.json` 이다. 버전이 낮으면 vcpkg 가 자체 SDK 를 받다가 실패한다.

안 하면: `gsutil` 항목이 FAIL 이고, PATH 에 없거나 버전이 낮다는 뜻이다. `gcloud` 가 없으면 `gcloud` 항목이 FAIL 이다.

### 2.4 vcpkg 클론과 VCPKG_ROOT

1. vcpkg 를 클론한다.
2. lock 이 고정한 커밋으로 detach 한다. 커밋의 정본은 메타 저장소 `DashOpti` 의 `toolchain-lock.json` 이다.
3. `git pull` 은 하지 않는다.
4. 클론 경로를 `VCPKG_ROOT` 환경변수에 넣는다. 환경변수 대신 `-VcpkgRoot` 매개변수로 줘도 된다.

안 하면: `vcpkg root` 항목이 FAIL 이다. 경로가 비었거나, 없거나, vcpkg 클론이 아니면 모두 FAIL 이다. 스크립트는 커밋까지는 확인하지 않는다.

### 2.5 GitHub 자격증명

사내 포트는 `DashOpti_Registry` 에서 온다. configure 중에 vcpkg 가 이 저장소를 프롬프트 없이 받는다.

1. 터미널에서 `git ls-remote https://github.com/NumeRealWorks/DashOpti_Registry.git` 를 한 번 실행한다.
2. 뜨는 Git Credential Manager 창에서 GitHub 에 로그인한다.
3. 로그인 뒤에도 실패하면 저장소 읽기 권한을 관리자에게 요청한다.

안 하면: `git 자격증명 (DashOpti_Registry)` 항목이 FAIL 이다.

### 2.6 gcloud 로그인과 GCS 읽기 권한

1. `gcloud auth login <계정>@numereal.ai` 로 로그인한다. 어느 계정을 확인하는지는 3.1 을 본다.
2. 읽기 권한은 Workspace 그룹 `dashopti-dev@numereal.ai` 에 있다. 권한이 없으면 저장소 관리자에게 요청한다.

이 권한은 선택이 아니다. 사내 포트는 캐시 hit 로만 받을 수 있다. VS 설치 파일을 받는 버킷도 같은 권한을 쓴다.

안 하면: `gcloud access token` 항목이 FAIL 이고 재인증 안내가 나온다. 토큰은 있는데 권한이 없는 경우는 스크립트가 알아내지 못한다. configure 로그에서 드러난다. 5절을 본다.

### 2.7 실행 정책

새 PC 의 기본값은 Restricted 라서 `.ps1` 을 바로 실행할 수 없다. 처음에는 `-ExecutionPolicy Bypass` 로 실행한다. 이후 그냥 실행하려면 한 번만 다음을 실행한다.

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

안 하면: 스크립트가 막히고 PowerShell 이 직접 오류를 낸다.

### 2.8 python (선택)

커밋 전에 clang-format 을 쓰려면 실제 python 이 필요하다. 빌드에는 필요 없다. Microsoft Store 로 안내만 하는 WindowsApps 스텁은 python 으로 치지 않는다.

안 하면: 안내 줄만 나오고 clang-format 설치를 건너뛴다. 나중에 python 을 깔고 스크립트를 다시 실행하면 된다.

## 3. setup-environment.ps1

클론당 한 번 실행한다. 저장소 루트에서 다음처럼 실행한다.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup-environment.ps1
```

### 3.1 매개변수

- `-VcpkgRoot <경로>`: vcpkg 클론 경로. 기본값은 `VCPKG_ROOT` 환경변수다. `CMakeUserPresets.json` 이 이미 있으면 그 파일의 값이 우선한다. 실제 configure 가 그 파일을 쓰기 때문이다.
- `-Account <계정>`: `CMakeUserPresets.json` 에 넣을 `CLOUDSDK_CORE_ACCOUNT`.

계정은 기존 `CMakeUserPresets.json` 의 `CLOUDSDK_CORE_ACCOUNT`, `-Account`, gcloud 활성 계정 순으로 정한다. 토큰 확인도 이 계정으로 한다. 실제 configure 가 그 파일의 계정을 쓰기 때문이다.
- `-SkipClangFormat`: clang-format 단계를 건너뛴다.

### 3.2 단계

스크립트는 2절의 선행 조건을 확인한다. VS(MSVC 툴셋, Ninja, cmake 포함), git 자격증명, vcpkg 클론, gsutil 버전, gcloud access token 이다. 그리고 로컬 설정을 한다. git 훅 경로를 `.githooks` 로 맞추고, `CMakeUserPresets.json` 이 없으면 template 에서 만들고, clang-format 이 없으면 pip 로 설치한다. `sh` 와 git 의 `user.name`, `user.email` 은 없으면 안내 줄만 나온다. Ninja 와 cmake 는 VS 설치 안에서 직접 찾으므로 스크립트로 빌드할 때는 PATH 에 넣지 않아도 된다. build-environment.md 의 Ninja PATH 요구는 손으로 실행할 때 기준이다.

`CMakeUserPresets.json` 을 만드는 조건은 셋이다. vcpkg root 확인이 통과해야 하고, 계정을 알아야 하고, 치환 뒤 자리표시자가 남지 않아야 한다. 하나라도 어긋나면 파일을 만들지 않는다. 틀린 값으로 만든 파일을 다음 실행이 "이미 있음" 으로 넘기는 것을 막기 위해서다.

clang-format 은 PATH 에 있는 것을 먼저 쓴다. 훅도 같은 순서로 찾는다. PATH 의 것이 요구 버전이 아니면 FAIL 이다. 요구 버전의 정본은 `docs/coding-convention.md` 다.

### 3.3 출력 읽는 법

각 줄은 상태 표시로 시작한다.

- `[OK]`: 조건이 이미 충족됐다.
- `[SKIP]`: 이미 되어 있거나, 선행 조건이 없어 일부러 건너뛰었다.
- `[DO]`: 스크립트가 이번에 실제로 바꿨다.
- `[FAIL]`: 조건이 안 맞는다. 같은 줄에 조치가 붙는다.

`안내:` 로 시작하는 줄은 상태가 아니다. 요약에 세지 않고 exit code 에도 영향이 없다. 하지만 읽어야 한다. 자동 업데이트 확인이 항상 여기 나온다.

마지막 줄은 요약이다. OK, SKIP, DO, FAIL 의 개수가 나온다. FAIL 이 0 이면 그 위에 다음 할 일 줄이 나온다.

exit code 는 FAIL 이 하나라도 있으면 1, 없으면 0 이다. 예외가 나도 FAIL 로 세고 요약줄과 exit 1 로 끝난다.

### 3.4 다시 실행해도 되는 이유

이미 된 단계는 `[OK]` 나 `[SKIP]` 이 되고 아무것도 바꾸지 않는다. 그러므로 FAIL 을 고칠 때마다 다시 실행하면 된다. 기존 `CMakeUserPresets.json` 은 덮어쓰지 않는다. 값을 바꾸려면 파일을 직접 고치거나 지우고 다시 실행한다.

선행 조건이 FAIL 이어도 로컬 단계(git 훅, `CMakeUserPresets.json`, clang-format)는 끝까지 한다. 훅이 빠진 채로 남으면 커밋 검사가 조용히 안 돌기 때문이다. 한 번의 실행에서 FAIL 을 전부 볼 수 있다.

스크립트는 커밋도 push 도 하지 않는다. 임시로 바꾸는 환경변수는 실패해도 원래대로 되돌린다.

## 4. build-app.ps1

```powershell
.\scripts\build-app.ps1
.\scripts\build-app.ps1 -Configure
```

실행 정책이 막으면 3절과 같이 `powershell -ExecutionPolicy Bypass -File` 로 실행한다.

### 4.1 configure 와 build

`out\build\local-msvc-release\build.ninja` 가 없으면 configure 를 먼저 한다. 있으면 configure 를 건너뛰고 build 만 한다. build 는 매번 돌고 증분이다.

`-Configure` 는 `build.ninja` 가 있어도 configure 를 강제로 다시 한다. `CMakeLists.txt`, preset, `vcpkg.json` 을 바꾼 뒤에 쓴다.

완료 판정에 `CMakeCache.txt` 가 아니라 `build.ninja` 를 쓰는 이유가 있다. CMake 는 configure 가 실패해도 캐시 파일을 남긴다. 캐시로 판정하면 인증 실패 뒤에 재인증하고 다시 돌릴 때 configure 를 건너뛰고, build 는 `build.ninja` 가 없어 계속 실패한다.

### 4.2 configure 직전의 setup

configure 를 돌릴 때만 그 직전에 `setup-environment.ps1` 을 다시 불러 같은 확인을 한다. 실패하면 configure 를 걸지 않는다.

### 4.3 로그와 Restored N

configure 출력은 콘솔이 아니라 `out\build-app-configure.log` 에 쌓인다. build 출력은 콘솔에 그대로 나온다.

configure 가 끝나면 로그에서 GCS 에서 몇 개를 복원했는지 뽑아 보여 준다. 이 숫자가 인증이 살아 있는지 알려 주는 유일하게 확실한 신호다.

- N 이 0보다 크다: 캐시를 읽었다.
- N 이 0이고 실패: 인증 만료이거나 캐시 miss 다. 5절을 본다.
- 복원 줄이 없고 성공: 받을 것이 없었다. 이미 설치됐거나 로컬 캐시로 충분했다.

소요 시간으로는 성공과 실패를 구분할 수 없다.

### 4.4 결과

성공하면 `[build] 완료` 줄과 산출물 경로가 나온다. 산출물은 `out\build\local-msvc-release\bin\DashOpti.exe` 다. 실패하면 단계 이름이 붙은 줄이 나오고 exit code 는 1 이다.

## 5. 막혔을 때

### 5.1 토큰은 OK 인데 configure 가 수 분 뒤 실패한다

원인은 대개 RAPT 만료다. gcloud 의 access token 과 RAPT(재인증 증명)는 따로 만료된다. `gcloud auth print-access-token` 은 앞의 것만 본다. RAPT 는 버킷에 실제로 접근할 때만 확인된다. 그래서 사전 확인이 통과하고도 수 분 뒤에 실패한다.

증상은 로그에 나온다.

- `ReauthUnattendedError` 가 있다.
- `Restored 0 package(s) from GCS` 가 있다.
- 마지막 오류는 "Ninja 를 찾을 수 없다" 로 나올 수 있다. 원인은 Ninja 가 아니라 인증이다. `--only-binarycaching` 인 preset 은 캐시 miss 를 즉시 실패로 만든다. 캐시를 못 받으면 vcpkg install 이 실패하고, configure 가 그 뒤에서 Ninja 오류로 끝난다.

`ReauthUnattendedError` 가 있으면 5.2 로 간다. 없는데 N 이 0이면 5.6 을 본다.

### 5.2 재인증

1. 사람이 자기 터미널에서 다음을 실행한다.

   ```powershell
   gcloud auth login <계정>@numereal.ai --force
   ```

   계정은 스크립트 안내에 찍힌 계정이다.

2. 브라우저 로그인과 비밀번호 입력을 끝낸다.
3. `%APPDATA%\gcloud\credentials.db` 의 수정 시각이 방금으로 바뀌었는지 확인한다.
4. `build-app.ps1` 을 다시 실행한다. 로그의 `Restored N` 에서 N 이 0보다 큰지 본다.

`--force` 가 필요한 이유는 이렇다. 없으면 gcloud 는 "저장된 자격증명을 재사용한다" 는 메시지와 함께 로그인에 성공한 것처럼 끝난다. 하지만 RAPT 는 갱신되지 않는다.

사람이 자기 터미널에서 해야 하는 이유는 이렇다. 재인증은 비밀번호를 콘솔로 묻는다. stdin 이 없는 셸에서는 그 프롬프트에서 멈춘다.

수정 시각 확인은 "방금 로그인이 자격증명을 새로 썼는가" 를 판별한다. 인증이 지금 살아 있는지는 알려 주지 못한다. 재사용 때는 시각이 바뀌지 않는다.

### 5.3 gcloud 를 못 찾는다

Cloud SDK 를 설치했는데 못 찾으면 이미 떠 있던 터미널이 옛 PATH 를 들고 있는 것이다. 새 터미널을 열어 다시 실행한다. 그래도 없으면 SDK 가 설치되지 않았거나 PATH 에 등록되지 않은 것이다.

gcloud 를 못 찾는 것은 인증 만료가 아니다. 둘을 섞어 판단하지 않는다.

### 5.4 DashOpti_Registry 접근 실패

사전 확인의 `git 자격증명` 이 FAIL 이거나, configure 로그에 `core-lib does not exist` 류가 보인다. 포트가 없는 것이 아니라 인증이 막힌 것이다.

1. 자기 터미널에서 `git ls-remote https://github.com/NumeRealWorks/DashOpti_Registry.git` 를 실행한다.
2. Git Credential Manager 로 GitHub 에 로그인한다.
3. 로그인 뒤에도 실패하면 저장소 읽기 권한을 관리자에게 요청한다.

증상 설명은 [build-environment.md](scratchpad/build-environment.md) 2.3 에 있다.

### 5.5 실행 정책에 막힌다

`.ps1 파일을 로드할 수 없다` 류 오류가 나오면 실행 정책이 막은 것이다. 2.7 대로 `-ExecutionPolicy Bypass` 로 실행하거나 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` 를 한 번 실행한다.

### 5.6 Restored 0 이 인증이 아니라 캐시 miss 다

`ReauthUnattendedError` 가 로그에 없고 N 이 0이면 캐시 miss 일 수 있다. 다음 순서로 본다.

1. 권한이 없는가. `AccessDeniedException` 이나 `403` 이 있으면 5.7 의 GCS 권한이다.
2. 전량이 miss 인가. 트리플릿 줄바꿈, vcpkg 커밋, VS 버전이 원인일 수 있다. [build-environment.md](scratchpad/build-environment.md) 2.6 의 순서대로 확인한다.
3. 특정 포트 한둘만 miss 인가. 캐시 워밍 누락일 수 있다. 버킷에 직접 올리지 말고 워밍을 요청한다.

### 5.7 그 밖의 증상

아래는 이미 다른 문서에 있다. 여기 복사하지 않는다.

- VS 최신 업데이트, gsutil 버전, `git pull`, CRLF, 이행 전 빌드 트리: `README.md` 의 함정 표
- `Invalid triplet`: [build-environment.md](scratchpad/build-environment.md) 2.4
- 오류 문구별 진단 전체: [build-environment.md](scratchpad/build-environment.md) 2절
- GCS 권한 오류(`AccessDeniedException`, `403`): 같은 문서 2.5. 저장소 관리자에게 권한을 요청한다.

## 6. 에이전트가 실행할 때

사람과 다른 제약만 적는다. 나머지 절차는 같다.

- 에이전트 셸에는 stdin 이 없다. `gcloud auth login` 과 재인증(5.2)은 에이전트가 할 수 없다. 사람에게 요청하고, 사람이 끝냈다고 알리면 `build-app.ps1` 을 다시 실행한다.
- `gsutil ls gs://...` 처럼 버킷을 직접 찔러 확인하지 않는다. RAPT 가 만료됐으면 reauth 프롬프트에서 무한정 멈춘다.
- 판정은 스크립트의 요약줄과 exit code 로 한다. 출력이 비었다고 깨끗하다고 보지 않는다.
- `print-access-token` 이 성공해도 인증이 살아 있다고 보지 않는다. 확실한 판별은 configure 로그의 `Restored N` 이다.
- `VCPKG_ROOT` 가 가리키는 vcpkg 클론을 건드리지 않는다. 한 PC 의 여러 세션이 같이 쓸 수 있다. `downloads\tools` 를 포함해 이름 변경, 정션, 삭제를 하지 않는다.
- configure 를 cmd 한 줄에서 PATH 를 직접 조립해 부르지 않는다. `vcvars64.bat` 뒤에 `set PATH=...;%PATH%` 를 잇으면 `%PATH%` 가 vcvars 실행 전의 값으로 미리 치환되어 `cl.exe` 경로가 사라진다. 스크립트를 쓴다.
- 이 문서는 공개 저장소에 있다. 특정 PC 의 경로나 개인 계정을 문서, 커밋, 이슈에 적지 않는다.
