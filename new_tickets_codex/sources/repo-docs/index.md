# DashOpti Documentation

## 개요

DashOpti GUI의 사용자 흐름(user flow) 중심 문서 인덱스입니다.
모든 파일 경로 규칙은 [io-controller.md](io-controller.md)를 기준으로 합니다.

## 공통 문서

- [Coding Convention](coding-convention.md) — 서식(clang-format), 네이밍(Qt 스타일, clang-tidy), 인코딩, git 훅 설정
- [I/O Controller — 경로 관리 체계](io-controller.md) — 두 루트 경로, config/모듈 디렉토리 규칙, ModuleType ↔ 파일명 매핑
- [통합 Logger 설계 결정](unified-logger.md) — 모듈 enum·6레벨·라우팅·비동기 큐·파일 포맷·치환 범위, 백로그 W1/W12 대응
- [테스트 레벨](test-levels.md) — 서브테스트를 Level 1~3 으로 누적 실행. 분류 기준, 기본값 규칙, 새 테스트 추가 절차
- [테스트 실행 경로](test-execution.md) — `run_tests.ps1`·훅 스크립트·git 훅의 구성과 동작, 실패 정책
- [개발 환경 셋업](development-environment-setup.md) — 새 PC 에서 첫 빌드까지. 사람이 먼저 할 일, `setup-environment.ps1`·`build-app.ps1` 실행, 막혔을 때, 에이전트 제약
- [Persistence](persistence.md) — registered object·registry·save data·save system, 새 registered object 절차, qFatal 규칙 (초안)
- [MVVM 패턴](mvvm-pattern.md) — Model·ViewModel 공통 기반, 새 Model 절차 (초안)

## Modules (메인 모듈 — 탭 기준 user flow)

모듈당 문서 1개. 변형(CAD/MCU/DOE Sampler 종류)은 별도 파일로 분리.

- [Geometry Parameterization (Morphing)](modules/geometry-parameterization-morphing.md)
- [Geometry Parameterization (CAD)](modules/geometry-parameterization-cad.md)
- [Condition Parameterization](modules/condition-parameterization.md)
- [DOE Sampler (Init)](modules/doe-sampler-init.md)
- [DOE Sampler (Resample)](modules/doe-sampler-resample.md)
- [DOE Sampler (Direct)](modules/doe-sampler-direct.md)
- [Analysis Launcher](modules/analysis-launcher.md)
- [Model Builder](modules/model-builder.md)
- [Model Builder (MCU)](modules/model-builder-mcu.md)
- [Model Runner](modules/model-runner.md)
- [Model Runner (MCU)](modules/model-runner-mcu.md)
- [Optimizer](modules/optimizer.md)
- [Results Analyzer](modules/results-analyzer.md) — 탭이 아닌 임베디드 패널 (DOE Sampler, Analysis Launcher, Model Runner, Model Runner MCU, Optimizer 위젯 내부)

## Dialogs (서브 모듈 — 다이얼로그 기준 user flow)

- [Solver Settings](dialogs/solver-settings.md)
- [TopOpt Post-Process](dialogs/topopt-postprocess.md)
- [Fe-safe Material Setup](dialogs/material-setup.md)
- [KPI Configuration](dialogs/kpi-configuration.md)
- [Mesh Quality Check](dialogs/mesh-quality.md)

## 문서 작성 규칙

각 문서는 다음 형식을 따릅니다.

1. **파일 I/O 요약** — 문서 최상단. 모듈이 읽고 쓰는 모든 파일을 표로 정리:
   `| 구분(Read/Write) | 파일 | 경로 (IOController 기준) | 발생 시점 |`
2. **탭/다이얼로그 단위 섹션** — 메인 모듈은 위젯의 실제 탭 타이틀(`## {N}. Tab: {제목}`),
   서브 모듈은 다이얼로그 단위. 다이얼로그 문서는 상단에 진입 경로(어느 메뉴/버튼에서 열리는지) 명시.
3. **사용자 인터랙션 순서대로 서브 섹션** — 탭 번호를 이어받아 `### {N}.1 {UI 라벨} 선택` →
   `### {N}.2 ...` → 마지막은 메인 버튼 `### {N}.{M} [버튼명] 클릭`
   (예: `## 1. Tab: Optimization` → `### 1.1 ...` → `### 1.8 [Run Optimizer] 클릭`)
   - 콤보박스: 리스트업 규칙(어떤 파일/폴더의 무엇을 읽는지, 확장자 제거 등 가공 규칙) 명시
   - Set/Apply류 버튼: 발생 동작과 기록되는 파일·키 명시
4. **탭 최하단 Main Button** — 클릭 시 동작 시퀀스 정리. 외부 호출(DLL/EXE)은 내부 로직 없이
   "무엇을 실행, 어떤 입력, 어떤 출력 파일" 수준으로만 간략 서술.
5. **디테일 수준 — 기획 문서 레벨 유지** — 코드 수정 시마다 문서를 고치지 않아도 되는 수준으로 작성.
   - 유지: 파일명·경로 규칙·JSON 키 구조, 리스트업/가공 규칙, 동작 시퀀스
   - 배제: C++ 함수명, 위젯 objectName, 클래스명, 파일:라인 참조, 시그널/슬롯 등 코드 내부 사정
   - 섹션 제목은 사용자가 화면에서 보는 UI 라벨 기준
6. **Appendix: 파일 포맷** — 문서 최하단. 모듈이 읽고 쓰는 파일별로 JSON 키 구조(예시 JSON 블록
   또는 키/타입/의미 표)를 정리. 본문 흐름 섹션에는 인터랙션 규칙에 필수적인 키 1~2개만 언급하고
   상세 포맷은 Appendix로 링크.
7. **언어** — 본문은 한국어, UI 문자열·파일명·JSON 키는 English backtick.
