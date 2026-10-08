# vcpkg 이행 작업 분량 (Qt5→Qt6, VTK 9.4→9.3)

> 최초 조사: 2026-09-03 · 갱신: 2026-09-08 (Phase 0 착수 시 재조사)
>
> 원 문서의 전제였던 "사내 레지스트리에 VTK 9.4 포트도 Qt5 포트도 없다" 는 유효하다.
> 방향은 그대로 **Qt6 로 올리고 VTK 9.3 으로 내린다**.
>
> 이 문서는 **단계·일정·외부 모듈 재빌드**를 소유한다. GUI 저장소 안의 파일 단위 수정 지점은
> [vcpkg-migration-code-changes.md](vcpkg-migration-code-changes.md) 가 소유하며, 그 문서가
> §5 의 `preprocessor` upstream 판정을 정정한다.

## 진행 상태 (2026-09-08)

| 단계 | 범위 | 상태 |
|---|---|---|
| **Phase 0** | `core-lib` · `cae-launcher` 를 사내 레지스트리에서 받는다. vcpkg 매니페스트 · 트리플릿 오버레이 · 프리셋 도입 | **완료** |
| Phase 0b | `doe` (구 `DashOptiDOE-1.0.1`) | **막힘** — 아래 §0 |
| Phase 1 | `mesh-ops` — 포트의 `vcpkg-vtk` feature 를 끄면 external VTK 9.4 를 유지한 채 이행 가능 | 미착수 |
| Phase 2 | VTK 9.3 + Qt6 + `reader-writer` · `preprocessor` · Morphing · Legacy Preprocessor + 앱 코드 ~33곳 | 미착수 (원자적) |

Phase 2 를 쪼갤 수 없는 이유: `reader-writer` · `mesh-ops` · `preprocessor` 의 공개 헤더가
`vtkSmartPointer<vtkUnstructuredGrid>` 를 주고받고(`ProxyTypes.hpp`, `MeshOps/Types.hpp`),
vcpkg `vtk` 포트의 `qt` feature 는 `qtbase`(Qt6)만 의존한다 — Qt5 로는 `VTK::GUISupportQt` 를
얻을 방법이 없다.

## 0. spdlog / fmt 상호 배제 — 이후 단계 전체를 제약한다

**`external/` 의 사전빌드 모듈과 vcpkg 는 `spdlog.dll` / `fmt.dll` 을 공유할 수 없다.**

| | 번들 사본 | vcpkg |
|---|---|---|
| `fmt` inline namespace 태그 | `@v11@fmt@@` | `@v12@fmt@@` (12.2.0) |
| `spdlog` | 번들 | 1.17.0 (`fmt.dll` 의존) |

`external/DashOptiPreprocessor-1.2.2/bin/DashOptiPreprocessor.dll` 과
`DashOptiMorphing-0.0.4/bin/DashOptiMorphing.dll` 이 둘 다 `spdlog.dll` + `fmt.dll` 을
implicit import 한다 (`main()` 전 로드). `bin/` 에 그 이름의 파일은 하나만 놓일 수 있으므로,
vcpkg 쪽 사본을 끌어오는 패키지가 하나라도 링크되면 **어느 쪽이 이겨도 EXE 가 시작되지 않는다.**
복사 순서로는 해결되지 않는다.

Phase 0 가 통과한 이유는 `core-lib` 과 `cae-launcher` 가 spdlog/fmt 를 **전혀 import 하지
않기** 때문이다 (`CoreLib_CoreLib.dll` 은 `CONTROL` 에 spdlog 의존이 있어도 static 흡수한다).
그래서 applocal 이 vcpkg 의 spdlog/fmt 를 `bin/` 으로 복사할 이유가 없고, Preprocessor 의 v11
쌍이 그대로 남는다. 빌드 후 실측으로 확인했다.

`doe` 는 반대다. 소스가 `target_link_libraries(DOE_DOE PRIVATE spdlog::spdlog)` 이고 dynamic
트리플릿이므로 `DOE_DOE.dll` → `spdlog.dll` → `fmt.dll`(v12) 를 끌어온다.

**해법(1줄):** `DashOpti_DOE/DashOptiDOE/CMakeLists.txt` 에서 `spdlog::spdlog` →
`spdlog::spdlog_header_only` (이게 `fmt::fmt-header-only` 를 함께 끌어온다). `core-lib` 이
이미 이 방식이라 선례가 있다. 공개 표면에 spdlog 타입이 없고(`JsonWrapper.h` 가 `Json::Value`
를 전방 선언 + Pimpl 로 끊는다) 전부 PRIVATE 링크라 부작용이 없다. 그 뒤 레지스트리 포트
version-date 범 + 캐시 워밍이 필요하다. 검증은 `dumpbin -dependents DOE_DOE.dll` 에
`spdlog.dll` / `fmt.dll` 이 없는 것.

이 제약은 `DashOptiMorphing` / `DashOptiPreprocessor` 를 **언제 재패키징할 수 있는지**도
결정한다. 둘 중 하나라도 vcpkg 로 옮기는 순간 나머지 하나도 같이 옮겨야 한다.

## 0b. Phase 0b — `doe` 이행 시 GUI 쪽 작업

포트는 이미 레지스트리 `main` 에 있다 (`versions/d-/doe.json`, `baseline.json` 모두 등록,
`2026-09-07.0`). §0 해법이 머지되면 GUI 쪽은 순수 개명이다. 시그니처 변경 0건.

| 축 | 구 (`DashOptiDOE-1.0.1`) | 신 (`doe`) |
|---|---|---|
| `find_package` / 타깃 | `DashOptiDOE` / `DashOptiDOE::DashOptiDOE` | `doe` (`1.0`) / `doe::doe` |
| config 위치 | `lib/cmake/DashOptiDOE/` | `share/doe/` |
| 헤더 루트 | `<DashOptiDOE/X.h>` | `<DOE/X.h>` |
| C++ 네임스페이스 | `DashDOE` | `dash::doe` |
| DLL | `DashOptiDOE.dll` + vendored 8종 | `DOE_DOE.dll` 단독 |

개명 4패스:
1. `<DashOptiDOE/X.h>` → `<DOE/X.h>` — `model/DashDoeSampler.cpp:28-39` (12곳),
   `model/DashDoeConfigManager.cpp:18`. `LatinHypercube.h` 는 죽은 include 이므로 삭제.
2. `DashDOE::` → `dash::doe::` — 17곳.
3. 전방 선언 — `model/DashDoeSampler.h:14`, `model/DashDoeConfigManager.h:14` 재조정.
   `model/DashDoeConfigManager.cpp:20` 은 같은 파일 18행이 실제 헤더를 include 하므로 삭제.
4. 주석 — `model/DashDoeSampler.h:185`.

주의: `IDesignSampler` 와 그 중첩 타입(`ContinuousRange` / `IntegerRange` / `CategoricalSet`)은
구·신 모두 **전역 네임스페이스**다. `dash::doe::` 를 붙이면 안 된다. 다만 GUI 는 이 이름을
어디서도 언급하지 않으므로 실제로 걸릴 일은 없다.

유일한 API 회귀는 `OrthogonalArray::SetNumSamples(size_t)` 삭제이고, GUI 의 OA 분기
(`model/DashDoeSampler.cpp:485-500`)는 `SetLevel` 만 호출하므로 무관하다. 포트를 다시
핀할 때 재확인할 항목.

## 요약

| 항목 | 값 |
|---|---|
| 앱 코드 규모 | 99,261줄 / 294 파일 / `.ui` 26개 |
| 앱 코드 수정 지점 | **~33곳 / 24파일** |
| 앱 쪽 총 소요 | **2~3일** |
| 전체 일정 결정 요인 | 외부 모듈 VTK 9.3 재빌드 (조직 작업) |

핵심 판정 두 가지:

- **Qt6 전환은 앱 단독으로 완결된다.** 사전빌드 바이너리 중 Qt5 에 의존하는 것이 **하나도 없음**.
  (Qt5 를 import 하는 건 CMakeLists 가 소비조차 않는 `DashOptiReaderWriter-1.0.0` 내부의 vtkGUISupportQt 뿐)
- **VTK 다운그레이드는 조직 차원의 재빌드가 필요하다.** 앱 코드 수정은 1줄뿐이지만,
  VTK 9.4 를 import 하는 사전빌드 모듈 5종을 같이 내려야 한다.

## 1. 앱 코드 수정

| 작업 | 곳 | 파일 | 난이도 |
|---|---|---|---|
| `QTextStream::setCodec("UTF-8")` → `setEncoding(QStringConverter::Utf8)` (또는 삭제) | 13 | 8 | 기계적 |
| `globalPos()` → `globalPosition().toPoint()` | ~10 | 8 | 기계적 (deprecated, 안 고쳐도 컴파일됨) |
| `QVariant::type()` → `typeId()` | 4 | 2 | 기계적 (안 고쳐도 컴파일됨) |
| `AA_EnableHighDpiScaling` 삭제 | 2 | 2 | 기계적 |
| `QtConcurrent::run(this, &C::m)` → `run(&C::m, this)` | 1 | 1 | **필수** (Qt6 에서 제거된 오버로드) |
| `QFontDatabase db;` → static 호출 | 1 | 1 | **필수** (Qt6 는 전부 static) |
| `.values().toVector()` → `.values()` | 1 | 1 | **필수** (Qt6 는 QVector==QList) |
| `vtkGenerateIds` → `vtkIdFilter` | 1 | 1 | **필수** (VTK 9.3 에 없는 클래스) |
| `/Zc:char8_t-` 제거 후 재컴파일 검증 | — | 전체 | 리스크 (u8 리터럴 0건이라 무해할 전망) |

**합계 ~33곳 / 24파일 — 반나절.**

### 수정 불필요 (확인 완료)

| 항목 | 결과 |
|---|---|
| `SIGNAL()/SLOT()` 매크로 | **0건** — 전부 new-style connect |
| `QRegExp` | **0건** — `QRegularExpression` 이미 24곳 사용 |
| `QTextCodec` / `QStringRef` / `QLinkedList` / `QDesktopWidget` | 0건 |
| `qSort` / `QSet::toSet` / `insertMulti` / `QString::null` / `qrand` | 0건 |
| `Qt::MidButton` / `QFontMetrics::width()` / `QSignalMapper` / `QGLWidget` | 0건 |
| `Qt::SkipEmptyParts` | 이미 사용 (10곳) |
| `angleDelta()` | 이미 사용 (`delta()` 0건) |
| `.ui` 파일 26개 | `QGLWidget`/`QRegExpValidator` 없음, 전부 표준 `version="4.0"` |
| `QAxObject` 5곳 | vcpkg `qtactiveqt` 6.10.2 존재, API 동일 |

### 주요 수정 위치

| 항목 | 위치 |
|---|---|
| `QtConcurrent::run` | `model/DashDoeSampler.cpp:230` |
| `QFontDatabase` 인스턴스화 | `view/DashOcctViewWidget.cpp:92` |
| `toVector()` | `view/dialog/TopOptPostprocessDialog.cpp:1714` |
| `vtkGenerateIds` | `controller/DashHandlePickingInteraction.cpp:295` |
| `AA_EnableHighDpiScaling` | `main.cpp:24`, `tools/uipreview/main.cpp:178` |

## 2. CMakeLists.txt

| 작업 | 난이도 |
|---|---|
| ~~`cmake_minimum_required` 3.10 → 3.21~~ | **완료** (Phase 0 에서 3.25) |
| `Qt5` → `Qt6` (`find_package`, `Qt5::`→`Qt6::`, UiTools) | 소 |
| VTK COMPONENTS 정정 (아래 표 참조) | 소 |
| windeployqt 경로 → `tools/Qt6/bin` + PATH 패치 로직 수정 | 중 |
| DLL 복사 블록 정리 (VTK glob, OCCT 3rdparty 6종, `external/additional`) | 삭제 위주 |
| `cmake/stdext_compat.h` + `/FI` 지시 삭제 (Qt 5.15 전용 shim) | 삭제 |
| ~~vcpkg toolchain / CMakePresets 도입~~ | **완료** (Phase 0) |

**하루.**

### VTK COMPONENTS 정정

현재는 통짜 VTK 설치라 우연히 동작 중. vcpkg 는 요청한 컴포넌트 타깃만 주므로
그대로 두면 링크 / `vtk_module_autoinit` 에서 실패한다.

| 조치 | 모듈 | 사유 |
|---|---|---|
| **추가** | `FiltersGeneral` | `vtkClipDataSet`, `vtkCurvatures` |
| **추가** | `FiltersPoints` | `vtkPoissonDiskSampler`, `vtkEuclideanClusterExtraction` |
| **추가** | `FiltersVerdict` | `vtkMeshQuality` |
| **제거** | `IOOCCT` | 소스에서 미사용 (opencascade↔vtk 순환 의존도 회피) |
| **제거** | `jsoncpp` | vcpkg 는 `VTK_USE_EXTERNAL=ON` 이라 `VTK::jsoncpp` 타깃 자체가 없음 |
| **제거** | `RenderingQt`, `RenderingGL2PSOpenGL2`, `FiltersParallel`, `RenderingContextOpenGL2` | 소스에서 미사용 |

## 3. vcpkg 설정 (신규)

| 작업 | 비고 |
|---|---|
| `vcpkg.json` 작성 — `vtk[opengl,qt]`, `qtbase`/`qtsvg`/`qttools`/`qtactiveqt`, `opencascade`, `eigen3` | — |
| `eigen3` → 3.4.0 `overrides` 핀 | GUI 가 eigen 을 vcpkg 에서 받는 **Phase 2 에서만** 문제다. baseline 은 5.0.1. Phase 0 에서는 넣지 않았다 — `overrides` 는 전이 의존의 ABI 해시를 바꿔 바이너리 캐시를 무효화하고, `--only-binarycaching` 을 쓰는 읽기 전용 개발자에게 하드 실패가 된다. 지금은 `external/eigen-3.4.0` 을 직접 include 하고 vcpkg eigen 은 `include/eigen3/Eigen` 에 깔려 서로 가리지 않는다 |
| `default-features:false` 로 cgns/netcdf/proj/seacas/libharu/libtheora 제거 | 빌드 시간 대폭 절감. 단 `qt` feature 가 `sql` 을 요구 |
| ~~사내 registry 연결~~ | **완료** (Phase 0) — `vcpkg-configuration.json` 이 레지스트리 baseline `d64551f` 를 고정한다. 트리플릿은 `x64-windows-dashopti` 오버레이 |
| 바이너리 캐시 세팅 | **대부분 해소.** VTK 9.3 · Qt6 · OCCT · eigen3 가 `x64-windows-dashopti` 로 이미 빌드돼 GCS 캐시에 있다. 단 개발자 계정에 버킷 읽기 권한(`storage.objects.list`)이 부여돼 있어야 한다 |

**하루 + 초회 빌드 대기.**

> `opengl` 은 default-feature 가 아니므로 명시해야 한다.
> portfile 의 `if("paraview" OR "opengl")` 분기가 `RenderingAnnotation=YES` 도 함께 켜주므로,
> 무거운 `paraview` feature 를 피할 수 있다.

## 4. 외부 모듈 재빌드 (앱 외부 작업 · 임계 경로)

| 패키지 | vcpkg 빌드 | VTK 9.4 의존 | 필요 조치 |
|---|---|---|---|
| ~~`core-lib`~~ | 레지스트리 포트 | 없음 | **완료** (Phase 0) |
| ~~`cae-launcher`~~ | 레지스트리 포트 | 없음 | **완료** (Phase 0) |
| `DashOptiDOE-1.0.1` → `doe` | 레지스트리 포트 존재 (`2026-09-07.0`) | 없음 | §0 의 spdlog/fmt 충돌 해소 후 이행 (Phase 0b) |
| `mesh-ops` | 레지스트리 포트 존재 (`2026-09-07.0`) | 공개 헤더가 VTK 타입 노출, 빌드 기준 9.4.1 | 포트의 `vcpkg-vtk` feature 를 끄면(`-DDASH_MO_VTK_EXTERNAL=ON`) external VTK 9.4 를 유지한 채 이행 가능 — **탈출구가 설계돼 있다** |
| `reader-writer` | 레지스트리 포트 존재. 포트가 이미 `vtk >= 9.3.0-pv5.12.0#4` + `qt` feature 를 요구 | 7개 모듈 import | **재빌드 불필요** — 포트를 쓰면 9.3 으로 온다. 단 `qt` feature 가 Qt6 를 끌어오므로 Phase 2 와 원자적 |
| `preprocessor` | 포트 없음 (`lib/cmake` 레이아웃) | import | VTK 9.3 재빌드 + vcpkg 패키징. **upstream 저장소가 없다** — 로컬 `/d/DashOpti_Preprocessor` 에 remote 가 없고 GitHub 조직에도 없다. 가장 앞선 blocker |
| `DashOptiMorphing-0.0.4` | X | 9.4 풀세트 동봉 | VTK 9.3 재빌드 + vcpkg 패키징 |
| `DashOptiPreprocessor-1.2.2` | X | import | VTK 9.3 재빌드 + vcpkg 패키징 |
| ~~`DashGizmo`~~ | — | — | **해소됨.** 소스를 `libs/DashGizmo` 로 이행 (2026-09-07) — 앱과 같은 VTK 로 함께 빌드되므로 별도 재빌드 대상이 아니다 |

> 원 문서의 "`mesh-ops` 는 CMakeLists 가 소비하지 않으므로 대상 외" 는 **틀렸다** — `find_package(mesh-ops)` 가
> 있고 `mesh-ops::mesh-ops` 를 링크한다. 위 표에 포함했다.
>
> `DashOptiMorphing` 소스는 `NumeRealWorks/DashOpti_Morphing` 에 있고, `DashOptiPreprocessor-1.2.2` 는
> `DashOpti_Preprocessor_Legacy` 가 archived 상태다.

## 5. 선행 확인 — 2건 모두 해소

| 확인 항목 | 결과 |
|---|---|
| ~~registry 빌드들의 VTK 버전~~ | **해소.** 레지스트리의 `reader-writer` · `mesh-ops` 포트가 이미 `vtk >= 9.3.0-pv5.12.0#4` 를 요구한다 — 재빌드 4건 중 2건이 실제로 소멸했다 |
| ~~DashGizmo 소스 확보~~ | **완료** — `libs/DashGizmo` 로 이행 |

### 남은 blocker (Phase 2)

1. **`preprocessor` 의 upstream 저장소가 없다** — 레지스트리 portfile 이 가리킬 URL 자체가 없다. 임계 경로.
2. `DashOptiMorphing-0.0.4` — 포트 없음. 소스는 `NumeRealWorks/DashOpti_Morphing`.
3. `DashOptiPreprocessor-1.2.2` — 포트 없음, 소스 저장소 archived. VTK 9.4 + OCCT ABI 양쪽에 물림.
4. §0 의 spdlog/fmt 상호 배제 — 2·3 을 vcpkg 로 옮기는 순서를 제약한다.

## 6. 부수 효과 (정리되는 것)

- `external/reader-writer/bin/_bundled-extras` 419개 DLL 소멸
- OCCT 3rdparty DLL 복사 블록 6종 (`jemalloc`/`ffmpeg`/`freeimage`/`openvr`/`freetype`/`tbb`) 삭제
- 패키지별 DLL 복사 `foreach` 루프 전부 삭제
- `external/additional` 오버라이드 해킹 삭제
- `cmake/stdext_compat.h` shim 삭제
- `/Zc:char8_t-` 삭제 (Qt5 시절 잔재)

## 7. 권장 순서

1. ~~Phase 0 — `core-lib` · `cae-launcher` + vcpkg 배관~~ **완료**
2. Phase 0b — `doe`. 선행: §0 의 상류 1줄 수정 + 레지스트리 포트 범
3. Phase 1 — `mesh-ops`. `vcpkg-vtk` feature 를 끈 채 이행하면 external VTK 9.4 를 유지할 수 있어 독립적으로 진행 가능
4. `preprocessor` 의 upstream 저장소 확보 — Phase 2 의 임계 경로. 여기부터는 조직 작업
5. Phase 2 — VTK 9.3 + Qt6 + 앱 코드 ~33곳 + CMakeLists 재작성 (원자적)

4번을 기다리는 동안 2·3번과 앱 코드 ~33곳(§1)은 병행 가능하다. §1 의 수정 대부분은
Qt5 에서도 컴파일되므로 Phase 2 전에 미리 넣어 둘 수 있다.
