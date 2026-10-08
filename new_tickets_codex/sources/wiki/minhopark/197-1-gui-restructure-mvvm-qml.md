# GUI 재구성 — MVVM 개선점과 Qt Widgets → QML 전환 평가

> 원본: 사전조사 Issue #197 — 본문을 이 페이지로 이관한 뒤 Issue 삭제 (2026-08-24). **본 페이지가 정본**
> 이관 주석: 아래 머리글의 `상태:` (Wiki 미연동·원격 미생성) 는 이관 전 시점 표기

> 상태: 로컬 초안 (GitHub Issue / Wiki 미연동)
> 관련 문서: [[192-1-architecture-analysis-mvc-mvvm]] — MVC/MVVM 전면 판정 근거 · [[202-1-view-qt-designer-vs-code-cleanup]] — view 정리 전략 실측 · [[198-1-improvement-roadmap]] — Phase 5 (ViewModel 수렴)
> 트랙 C-1\~C-3 정의: main repo `docs/plan-nx-cpp-porting-match-nset.md` — "트랙 C — Qt Designer / 공통 UI 분리"
> 작성일: 2026-07-07

---

## 개요

GUI 재구성 논의를 두 축으로 정리한다.

1. MVVM이 MVC 대비 실제로 가져오는 핵심 개선점은 무엇인가 (1절)
2. 그 개선점을 얻기 위해 Qt Widgets에서 QML로 전환하자는 제안의 찬/반 근거는 무엇이고, 전환 없이 현재 구조 안에서 같은 이득을 확보할 방법은 무엇인가 (2절, 3절)

결론: **QML 전환은 비용은 확실하고 이득은 현재 구조 내 정리 작업(트랙 C + presenter 분리)으로 대체 가능** — 3절 참조.

---

## 1. MVVM이 MVC 대비 가져온 핵심 개선점

- **View–Model 종속성 절단**: View는 ViewModel 속성에 선언적 바인딩만, ViewModel은 View를 모름. Controller가 View를 직접 조작하던 양방향 참조 제거, 갱신 전파는 프레임워크 담당
- **View의 모델 참조 효율화**: 화면용 가공 로직이 ViewModel 속성으로 이동. View는 표시용 형태만 참조, 속성 단위 통지로 바뀐 부분만 갱신
- **상태 관리 분리**: 선택·활성화·편집값·유효성 등 화면 상태가 위젯이 아닌 ViewModel에 존재. View 재생성에도 상태 유지, UI 없이 단위 테스트 가능
- **입력의 커맨드화**: 클릭이 ViewModel Command에 바인딩, 실행 조건(CanExecute)까지 상태로 관리 → 버튼 활성 로직을 UI 밖에서 검증

---

## 2. Qt Widgets → QML 전환 찬/반 근거

### 2-1. 찬성

- **바인딩 프레임워크 확보**: MVVM 이득(View–Model 절단, 상태 분리)을 프레임워크가 제공
- **스타일 일원화**: inline stylesheet 난립을 테마 시스템으로 구조적 해결
- **UI/로직 분리 강제**: QML과 C++ 백엔드가 물리적으로 분리됨
- **장기 방향성**: Qt 신규 투자는 QML 쪽, Widgets는 유지 모드
- **모던 UI 표현력**: 애니메이션·HiDPI·커스텀 룩

### 2-2. 반대

- **3D 뷰포트 통합이 최난관**: VTK/OCCT를 QML에 넣으려면 FBO/RHI 통합 직접 구현. 여기서 막히면 전체 좌초 — 최우선 검증 지점
- **규모·일정 충돌**: view 51개 파일 재작성은 수개월+. NX 포팅·Match NSET 일정과 정면 충돌
- **암묵 스펙 유실**: UI 테스트 부재 상태의 big-bang rewrite → 회귀 양산 전형
- **테이블/트리 UI는 Widgets가 우세**: QML TableView는 편집·헤더 기능이 빈약, 구현량 오히려 증가 가능
- **이득이 도메인과 불일치**: 애니메이션·터치 불필요한 엔지니어링 도구, 동적 View 수요도 적음
- **팀 스택 전환 비용**: QML/JS 학습 + 경계 설계 + 디버깅 도구 변경

---

## 3. 판정 — 비용은 확실, 이득은 현재 구조 내에서 대체 가능

QML 전환이 약속하는 이득 각각을 현재 구조(Qt Widgets) 안의 정리 작업으로 매핑하면:

| QML이 풀려던 문제 | 현재 구조 내 대체 수단 | 실행 단위 |
|---|---|---|
| 헬퍼 12곳 중복 | `ModelBuilderUIHelper`로 통합 | 트랙 C-1 (즉시 가능) |
| 스타일 하드코딩 | inline 제거, `qtheme_light.qss` 단일화 + 색상 토큰 | 트랙 C-2 |
| 레이아웃 코드 장황 | 신규 화면부터 `.ui` 적용 | 트랙 C-3 파일럿 |
| 프레젠테이션 로직 혼재 | presenter 클래스로 분리(humble object), 위젯은 표시만. UI 없이 단위 테스트 — MVVM 핵심 이득 확보 | Phase 5 계열 |
| 상태가 위젯에 박힘 | presenter로 이동 + 시그널 통지. Qt 6 `QProperty`로 부분 바인딩 가능 | Phase 5 계열 |

- 1절의 MVVM 핵심 이득 중 **상태 관리 분리·UI 없는 단위 테스트**는 presenter(humble object) 분리로, **속성 단위 통지·부분 바인딩**은 시그널 통지 + Qt 6 `QProperty`로 QML 없이 확보 가능하다.
- 반면 QML 전환의 비용(3D 뷰포트 통합 리스크, 51개 파일 재작성, 회귀 양산, 팀 스택 전환)은 회피 불가능한 확정 비용이다.
