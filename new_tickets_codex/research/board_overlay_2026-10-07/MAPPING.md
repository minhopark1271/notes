# board.txt 전수 대응표

원본 62개 이슈의 계층·배정·상태·우선순위를 보존한다. 주된 대응도 반드시 완전 동등 범위는 아니다. `부분`·`재판정`과 주의사항을 함께 읽는다.

**관계:** 직접=핵심 목표 대응, 분할=여러 작업으로 나눔, 통합=다른 이슈와 한 작업으로 모음, 부모=하위 완료 추적, 부분=일부만 겹침, 재판정=설계·병합 후 잔여 재확정, 제외=새 구현으로 변환하지 않음.

`핵심 축`은 이번 대화의 6대 꼭지이며 기존 A~G 태그를 대체하지 않는다. `주변개선`은 6대 꼭지 밖의 기능·사용성·구조 개선이다.

## 표시 53 · #246 [W20] God-object 해체 — DataProcessor·DashManager·DashProjectManager

### [#246](https://github.com/NumeRealWorks/DashOpti_GUI/issues/246) · 부모

- 원본: W4 10/05–10/11 / Backlog / High
- 핵심 축: 수명안정 / 실행계약
- 주된 대응: [PRJ-01](../../03_TASK_CATALOG.md#prj-01), [PRJ-09](../../03_TASK_CATALOG.md#prj-09), [PRJ-10](../../03_TASK_CATALOG.md#prj-10), [IO-07](../../03_TASK_CATALOG.md#io-07), [IO-08](../../03_TASK_CATALOG.md#io-08), [IO-09](../../03_TASK_CATALOG.md#io-09), [RES-10](../../03_TASK_CATALOG.md#res-10), [RES-11](../../03_TASK_CATALOG.md#res-11)
- 보조 관련: [GEO-001](../../03_TASK_CATALOG.md#geo-001), [VIS-003](../../03_TASK_CATALOG.md#vis-003)
- 변환 범위: W20 자체를 새 거대 PR로 만들지 않고 수명/프로젝트 의존/서비스 소유/결과 처리 분해의 잔여 자식 작업을 집계한다. 완료된 KPI 분리나 이미 분해된 클래스는 새로 구현하지 않는다.
- 주의: baseline의 PRJ-01/09/10 세 개는 부모 전체와 동일 범위가 아니다. #433 자식의 잔여는 RES-10/11 및 관련 결과별 결함 작업에 분산되어 있다. RES-10 관련 PR656은 최신 스냅샷 MERGED이므로 병합분과 실제 잔여를 구분해야 한다. 부모와 자식의 작업량을 중복 합산하지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#431](https://github.com/NumeRealWorks/DashOpti_GUI/issues/431) · 통합

- 원본: 미배정 / Backlog / High
- 핵심 축: 수명안정
- 주된 대응: [PRJ-01](../../03_TASK_CATALOG.md#prj-01)
- 보조 관련: [RUN-07](../../03_TASK_CATALOG.md#run-07), [OPT-02](../../03_TASK_CATALOG.md#opt-02)
- 변환 범위: setModel(nullptr)/clear·연결 해제·모델 삭제 순서·늦은 완료 폐기를 공통 프로젝트 전환 계약과 실제 적용으로 묶는다.
- 주의: #431 원문은 문서/리뷰 게이트 중심이지만 PRJ-01은 #551 등의 실제 수선까지 포함한다. 요청별 ID·Set 세대 처리는 RUN-07/OPT-02가 담당하며 PRJ-01 하나로 모두 끝난다고 보지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#432](https://github.com/NumeRealWorks/DashOpti_GUI/issues/432) · 분할

- 원본: 미배정 / Backlog / High
- 핵심 축: 수명안정 / 저장계약
- 주된 대응: [PRJ-09](../../03_TASK_CATALOG.md#prj-09), [IO-07](../../03_TASK_CATALOG.md#io-07), [IO-08](../../03_TASK_CATALOG.md#io-08), [IO-09](../../03_TASK_CATALOG.md#io-09)
- 보조 관련: [PRJ-06](../../03_TASK_CATALOG.md#prj-06)
- 변환 범위: DashProject 네 IO 경계의 첫 주입 후 파라미터, DOE/Launcher, 학습/예측/최적화 모델의 전역 ProjectManager 역접근을 소비자군별로 이행한다.
- 주의: PRJ-06은 저장 성공/Save As의 관련 기능 결함이며 #432의 의존 주입 자체와 동일 작업이 아니다. Claude PRJ-34 공통 베이스 결정은 다른 구현 전략이며 Codex의 작은 계면 주입에 자동 강제 선행으로 추가하지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#433](https://github.com/NumeRealWorks/DashOpti_GUI/issues/433) · 부분

- 원본: W3 09/28–10/04 / In progress / High
- 핵심 축: 정확성 / 실행계약
- 주된 대응: [RES-04](../../03_TASK_CATALOG.md#res-04), [RES-05](../../03_TASK_CATALOG.md#res-05), [RES-11](../../03_TASK_CATALOG.md#res-11)
- 보조 관련: [RES-03](../../03_TASK_CATALOG.md#res-03), [RES-09](../../03_TASK_CATALOG.md#res-09), [RES-10](../../03_TASK_CATALOG.md#res-10)
- 변환 범위: 이미 끝난 클래스 분해를 반복하지 않고 Motion component/Kind, Modal 선택 및 실파일 회귀의 남은 완료 조건을 추적한다. 응답 키와 worker 이관은 각각의 후속 작업으로 연결한다.
- 주의: PR656 병합으로 RES-10의 modalNames/직렬화/TimeSteps 공통화는 새 구현 후보에서 제외한다. PR662의 State 통일도 완료이며 RES-04 전체를 잔여로 세지 않는다. PR663/665/658 통합과 실파일 검증을 구별한다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#434](https://github.com/NumeRealWorks/DashOpti_GUI/issues/434) · 부분

- 원본: W3 09/28–10/04 / In progress / High
- 핵심 축: 수명안정 / 실행계약
- 주된 대응: [PRJ-10](../../03_TASK_CATALOG.md#prj-10)
- 보조 관련: [PRJ-09](../../03_TASK_CATALOG.md#prj-09), [IO-07](../../03_TASK_CATALOG.md#io-07), [IO-08](../../03_TASK_CATALOG.md#io-08), [IO-09](../../03_TASK_CATALOG.md#io-09), [VIS-003](../../03_TASK_CATALOG.md#vis-003), [GEO-001](../../03_TASK_CATALOG.md#geo-001)
- 변환 범위: 현재 DashManager가 보유하는 프로세스·설정 소유와 실제 소비자 접근을 명시적으로 이관한다. renderer/interaction과 morphing 데이터 소유는 해당 모듈 접점으로 분리한다.
- 주의: PRJ-10은 #434 전체 4단계 중 프로세스·설정 중심이다. VIS-003의 씬 소유권이 모든 renderer/interaction 의존 주입과 같지는 않으므로 전체 전역 접근 제거 완료로 환산할 수 없다. 전면 해체는 최신 남은 접근 목록을 기준으로 판정한다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

## 표시 54 · #427 DOE 배치·Generate·프리뷰 실행을 화면 편집 상태에서 격리

### [#427](https://github.com/NumeRealWorks/DashOpti_GUI/issues/427) · 부모

- 원본: W4 10/05–10/11 / Backlog / High
- 핵심 축: 정확성 / 수명안정 / 실행계약
- 주된 대응: —
- 보조 관련: [GEO-002](../../03_TASK_CATALOG.md#geo-002), [GEO-007](../../03_TASK_CATALOG.md#geo-007), [VIS-001](../../03_TASK_CATALOG.md#vis-001), [VIS-002](../../03_TASK_CATALOG.md#vis-002), [VIS-003](../../03_TASK_CATALOG.md#vis-003), [VIS-004](../../03_TASK_CATALOG.md#vis-004)
- 변환 범위: 실행 snapshot과 편집/표시 상태의 격리 완결을 추적하는 부모로 유지하거나, 각 자식의 새 작업으로 이관한 근거를 남겨 추적을 종료한다. 부모 자체를 새 구현 PR로 추가 집계하지 않는다.
- 주의: Claude MOR-19는 원복 코드가 이미 없다는 판정과 잔여 자식 이관을 제안한다. 최신 PR655 본문은 원복 코드 삭제를 아직 부모 몫으로 남겨 서로 서술이 다르므로 통합 기준에서 잔여 확인 후 처분한다. renderer 축은 별도 미완료이고 PR655도 OPEN이므로 부모 목표 전체 완료를 단정하지 않는다. baseline crosswalk의 task들은 부모의 자식 범위이며 모두 직접 구현 범위라는 뜻이 아니다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#430](https://github.com/NumeRealWorks/DashOpti_GUI/issues/430) · 직접

- 원본: W4 10/05–10/11 / In progress / Medium
- 핵심 축: 정확성 / 저장계약 / 식별계약 / 수명안정
- 주된 대응: [GEO-002](../../03_TASK_CATALOG.md#geo-002)
- 보조 관련: [GEO-001](../../03_TASK_CATALOG.md#geo-001)
- 변환 범위: GEO-002를 신규 구현 예정에서 PR655의 구현 검토·통합·회귀 확인으로 변환한다. 실제 선행은 PR654/GEO-001이며, entry 상태가 렌더·피킹·편집·Done 저장의 정본인지 확인한다.
- 주의: 옛 DashHandleData 타입/VTP 5-read·2-write 통합은 적용하지 않는다. PR655는 polydata를 projection 캐시로 남기는 수준을 넘어 m_handleGeometry·DashHandleImport·GizmoGroup 등을 삭제하고 DashHandleDefinition/DisplacementPolicy를 정본으로 둔다. GEO-002 문구도 최신 구현에 맞게 갱신 필요. PR655에 흡수된 VIS-007(구 #322)은 supporting_task로 추가 구현하지 않는다. #654/#655의 version 1 형식 차이는 #654 단독 릴리스가 없다는 전제를 확인해야 한다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#318](https://github.com/NumeRealWorks/DashOpti_GUI/issues/318) · 분할

- 원본: W4 10/05–10/11 / Backlog / High
- 핵심 축: 수명안정 / 실행계약
- 주된 대응: [VIS-003](../../03_TASK_CATALOG.md#vis-003), [VIS-004](../../03_TASK_CATALOG.md#vis-004)
- 보조 관련: [VIS-001](../../03_TASK_CATALOG.md#vis-001), [VIS-002](../../03_TASK_CATALOG.md#vis-002), [VIS-005](../../03_TASK_CATALOG.md#vis-005)
- 변환 범위: 현재 행을 (1) 모듈·문서별 scene 등록/인수/해제 계약과 문서 보존(VIS-003), (2) split view·ghost·범례 복원(VIS-004)으로 나눈다. 독립 결함 복구는 먼저 하고 소유권 확산은 소비자군별 검증으로 완성한다.
- 주의: VIS-001/#316과 VIS-002/#319는 별도 자식·파일럿이며 같은 구현을 여기서 다시 집계하지 않는다. VIS-005/#320은 같은 기반의 후속 표시 토글 작업이지 #318에 자동 포함할 직접 범위가 아니다. 최신 PR655가 핸들 렌더 내부를 바꾸어도 공유 씬/문서 소유권 요구가 자동 해결되지는 않는다. 원문의 12곳·5종 actor 등 수치는 최신 코드 실측값으로 재인용하지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#316](https://github.com/NumeRealWorks/DashOpti_GUI/issues/316) · 직접

- 원본: W4 10/05–10/11 / Backlog / 우선순위 미기재
- 핵심 축: 수명안정 / 실행계약
- 주된 대응: [VIS-001](../../03_TASK_CATALOG.md#vis-001)
- 보조 관련: [OPT-02](../../03_TASK_CATALOG.md#opt-02), [VIS-003](../../03_TASK_CATALOG.md#vis-003)
- 변환 범위: Optimizer preview만 overlay로 등록·교체·해제하며 기존 FE 문서/핸들의 표시, camera, registry 표시 커서를 유지한다. 다음 Load·요청 무효화에서 자기 preview만 제거한다.
- 주의: OPT-02의 요청 ID/취소/늦은 완료는 같은 사용자 흐름이지만 별도 실행 계약이다. VIS-003의 일반 모듈 인수 시 숨김 정책을 preview에 적용해 기존 actor를 숨기지 않는다. PR655 이후 핸들 actor 구성은 바뀌므로 옛 5종 복구불가 목록을 고정 acceptance로 삼지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#319](https://github.com/NumeRealWorks/DashOpti_GUI/issues/319) · 직접

- 원본: W4 10/05–10/11 / Backlog / High
- 핵심 축: 수명안정
- 주된 대응: [VIS-002](../../03_TASK_CATALOG.md#vis-002)
- 보조 관련: [VIS-003](../../03_TASK_CATALOG.md#vis-003), [VIS-004](../../03_TASK_CATALOG.md#vis-004)
- 변환 범위: FE actor 숨김 후 복원, Runner preview의 FE 겹침 방지, Geometry actor 등록/해제의 단일 창구, 불필요한 camera reset 제거를 한 일관된 결함 수정으로 잡는다.
- 주의: #318을 기다려야 하는 후행이 아니라 현재 API로 먼저 가능한 선행·파일럿이다. clearAllLayers에 문서 actor 전체 삭제를 추가하는 처방은 문서 보존 계약에 어긋난다. split view 전체 복구는 VIS-004의 별도 목적이므로 함께 중복 집계하지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#281](https://github.com/NumeRealWorks/DashOpti_GUI/issues/281) · 재판정

- 원본: W4 10/05–10/11 / In progress / High
- 핵심 축: 정확성 / 수명안정 / 실행계약
- 주된 대응: [OPT-02](../../03_TASK_CATALOG.md#opt-02), [GEO-007](../../03_TASK_CATALOG.md#geo-007)
- 보조 관련: [GEO-006](../../03_TASK_CATALOG.md#geo-006), [RUN-07](../../03_TASK_CATALOG.md#run-07), [AST-003](../../03_TASK_CATALOG.md#ast-003), [GEO-001](../../03_TASK_CATALOG.md#geo-001), [GEO-002](../../03_TASK_CATALOG.md#geo-002)
- 변환 범위: 옛 모핑 워커화 Phase를 그대로 변환하지 않고 완료된 값 경계/서비스 이관을 제거한다. 실제 잔여가 확인되는 Optimizer 요청·펌핑/취소는 OPT-02, 모핑 교차 모듈·프로젝트 전환 검증은 GEO-007로 받는다. 범위 이관 근거를 남긴 뒤 기존 광역 이슈 종료 여부를 판단한다.
- 주의: 기존 crosswalk의 GEO-006은 QC 결과창의 별도 #512 결함이라 단순 #281 직접 대체가 아니다. Runner 요청 귀속 RUN-07, RW 실제 clone/edit/export GUI 이탈 AST-003도 연결된 독립 잔여다. Claude MOR-18은 본체 완료·잔여 OPT 이관을 제안하지만 MOR-16 계측·MOR-04 dead code 등 부수 요구는 기존 Codex 카드와 1:1 대응하지 않으므로 필요 여부를 따로 확인한다. 최신 PR654/655는 이 이슈 전부를 닫는 PR가 아니다.
- 대응 확신: 중간 (실행 성공 여부와 별개)

## 표시 55 · #446 창·레이아웃 크기 관리를 Qt 표준으로 전환

### [#446](https://github.com/NumeRealWorks/DashOpti_GUI/issues/446) · 부모

- 원본: W4 10/05–10/11 / Backlog / High
- 핵심 축: 수명안정 / 저장계약 / 주변개선
- 주된 대응: —
- 보조 관련: [UI-01](../../03_TASK_CATALOG.md#ui-01), [UI-02](../../03_TASK_CATALOG.md#ui-02), [UI-03](../../03_TASK_CATALOG.md#ui-03)
- 변환 범위: 배율·창 복구(UI-01), 배치 저장/복원(UI-02), 레이아웃 크기 소유(UI-03)를 추적하는 묶음으로 쓴다. 부모와 #447~450을 각각 별도 구현량으로 더하지 않는다.
- 주의: Claude UIC-25 역시 고유 작업 없는 부모로 처리한다. #450의 native-frame/중첩 MainWindow 선택은 Codex UI-01의 조건부 검토에 일부만 들어 있으므로 UI-01~03 매핑만으로 #450 전체 구현이 확정되었다고 보지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#447](https://github.com/NumeRealWorks/DashOpti_GUI/issues/447) · 직접

- 원본: 미배정 / Backlog / High
- 핵심 축: 수명안정
- 주된 대응: [UI-01](../../03_TASK_CATALOG.md#ui-01)
- 보조 관련: [UI-02](../../03_TASK_CATALOG.md#ui-02), [UI-03](../../03_TASK_CATALOG.md#ui-03)
- 변환 범위: 혼합 DPI 실기 재현→정지 지배 구간 확인→화면 밖 복구 불가/재진입 차단으로 변환한다. runtime 검증 항목으로 두고 검증된 원인에 필요한 안전 조치만 적용한다.
- 주의: 원 이슈의 Round 정책 처방은 현 Qt 정책을 확인한 뒤 적용해야 한다. Claude UIC-02는 Qt6 전환 뒤 옛 rounding 가정 대신 DPI awareness와 프로파일 실측을 강조한다. UI-02의 기동 시 off-screen 복원, UI-03의 상시 크기 재분배 제거는 접점이며 #447과 동일 범위가 아니다. 최신 W4 입력의 하위 행은 별도 iteration이 없다는 이유로 자동 미선정 처리하지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#448](https://github.com/NumeRealWorks/DashOpti_GUI/issues/448) · 직접

- 원본: 미배정 / Backlog / High
- 핵심 축: 저장계약 / 주변개선
- 주된 대응: [UI-02](../../03_TASK_CATALOG.md#ui-02)
- 보조 관련: [UI-01](../../03_TASK_CATALOG.md#ui-01), [UI-03](../../03_TASK_CATALOG.md#ui-03), [UI-04](../../03_TASK_CATALOG.md#ui-04)
- 변환 범위: 창 geometry와 outer/inner dock state를 version 있는 설정 키로 저장·복원하고, 모니터 제거/해상도 변경/손상 상태 시 안전한 초기 배치로 복구한다.
- 주의: UI-04 전체 최근 프로젝트 메뉴 기능은 이 이슈 범위가 아니다. 설정 키 namespace 부분만 접점이다. 강제 resize가 복원값을 덮는다면 UI-03의 해당 부분을 먼저 또는 같은 PR에 적용한다. Claude UIC-05가 명시한 이 순서는 Codex UI-02의 독립 완료 가능성 검토에 유용하다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#449](https://github.com/NumeRealWorks/DashOpti_GUI/issues/449) · 부분

- 원본: 미배정 / Backlog / Medium
- 핵심 축: 수명안정 / 주변개선
- 주된 대응: [UI-03](../../03_TASK_CATALOG.md#ui-03)
- 보조 관련: [UI-01](../../03_TASK_CATALOG.md#ui-01), [UI-02](../../03_TASK_CATALOG.md#ui-02)
- 변환 범위: MainWindow dock 재분배·ViewOptions 강제 flush·동적 표 크기라는 확인된 소비 지점부터 레이아웃/sizePolicy로 돌린다. 앱 shell과 동적 표 개선을 필요하면 별 PR로 나눈다.
- 주의: 원 이슈의 25건 카탈로그 전체가 Codex UI-03 한 카드와 정확히 같지는 않다. Claude는 UI Scale 유지/제거·stylesheet px 정책·DPI cache 등 결정/후속을 더 분리한다. 모든 setFixedSize·px가 결함은 아니며 UI Scale 제거를 자동 확정하지 않는다. 현재 사용자 흐름에 해당하는 잔여를 목록화한 후 나머지를 후순위로 두는 부분 변환이다.
- 대응 확신: 중간 (실행 성공 여부와 별개)

### [#450](https://github.com/NumeRealWorks/DashOpti_GUI/issues/450) · 재판정

- 원본: 미배정 / Backlog / Low
- 핵심 축: 수명안정 / 주변개선
- 주된 대응: [UI-01](../../03_TASK_CATALOG.md#ui-01)
- 보조 관련: [UI-02](../../03_TASK_CATALOG.md#ui-02), [UI-03](../../03_TASK_CATALOG.md#ui-03)
- 변환 범위: UI-01 실측과 UI-03 개선 후에도 남는 문제를 근거로 (1) frame OS 위임 경로 선택, (2) 중첩 QMainWindow 유지/단일화 여부를 각각 결정한다. 선택된 경우에만 구체 구현 작업으로 확장한다.
- 주의: UI-01은 재현·제한된 안전조치와 필요성 판단을 포함하지만 Win32 nativeEvent 구현이나 nested MainWindow 해체 전체를 확정 범위로 담고 있지는 않다. 따라서 UI-01 완료=#450 전체 완료가 아니다. Claude UIC-08/09/11의 결정·조건부 구현 분리는 참고할 수 있으나 그 구체 Win32 방안을 이미 승인된 해법으로 가져오지 않는다.
- 대응 확신: 중간 (실행 성공 여부와 별개)

## 표시 56 · #451 GUI 스레드 동기 실행과 이벤트 펌핑 제거

### [#451](https://github.com/NumeRealWorks/DashOpti_GUI/issues/451) · 부모

- 원본: W4 10/05–10/11 / Backlog / Medium
- 핵심 축: 수명안정 / 실행계약
- 주된 대응: —
- 보조 관련: [RES-08](../../03_TASK_CATALOG.md#res-08), [RES-09](../../03_TASK_CATALOG.md#res-09), [ASY-05](../../03_TASK_CATALOG.md#asy-05), [UI-03](../../03_TASK_CATALOG.md#ui-03), [AL-12](../../03_TASK_CATALOG.md#al-12), [OPT-02](../../03_TASK_CATALOG.md#opt-02), [OPT-07](../../03_TASK_CATALOG.md#opt-07), [GEO-006](../../03_TASK_CATALOG.md#geo-006), [RUN-06](../../03_TASK_CATALOG.md#run-06)
- 변환 범위: Load/Process/FEM/레이아웃/모핑 결정 신호/폴더 스캔 등 자식의 구체 경로별 완료를 롤업한다.
- 주의: 별도 구현량 없음. ASY-01 훅 재설계는 관련 공통 작업이지만 이 부모의 직접 변환이나 모든 worker 이관의 필수 선행이 아니다. 옛 펌핑 개수와 이미 비동기인 경로를 목표로 쓰지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#454](https://github.com/NumeRealWorks/DashOpti_GUI/issues/454) · 분할

- 원본: 미배정 / Backlog / High
- 핵심 축: 수명안정 / 실행계약
- 주된 대응: [RES-08](../../03_TASK_CATALOG.md#res-08), [RES-09](../../03_TASK_CATALOG.md#res-09)
- 보조 관련: [ASY-02](../../03_TASK_CATALOG.md#asy-02)
- 변환 범위: 결과 Load·Preview와 일반 배치 Process·XML 생성을 각각 작업 소유 입력/reader, GUI 결과 적용, 취소·전환·오류 복구 단위로 나눈다.
- 주의: KPI 경로는 원 이슈 제외 범위를 유지한다. 16곳 제거 자체가 완료 조건은 아니며 renderer 접근과 비취소 SDK 경계를 보존한다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#455](https://github.com/NumeRealWorks/DashOpti_GUI/issues/455) · 분할

- 원본: 미배정 / Backlog / Medium
- 핵심 축: 수명안정 / 실행계약 / 주변개선
- 주된 대응: [ASY-05](../../03_TASK_CATALOG.md#asy-05), [UI-03](../../03_TASK_CATALOG.md#ui-03)
- 보조 관련: [GEO-006](../../03_TASK_CATALOG.md#geo-006)
- 변환 범위: TopOpt FEM 파싱의 worker/창 수명과 앱·오버레이 레이아웃의 강제 이벤트 flush 제거로 구분한다.
- 주의: GEO 결정 신호 유실은 #512/GEO-006 소유로 중복 발행하지 않는다. UI-03 전체 동적 표 개선이 #455와 동일한 범위는 아니다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#456](https://github.com/NumeRealWorks/DashOpti_GUI/issues/456) · 재판정

- 원본: 미배정 / Backlog / Low
- 핵심 축: 수명안정 / 실행계약
- 주된 대응: [AL-12](../../03_TASK_CATALOG.md#al-12)
- 보조 관련: —
- 변환 범위: AL-12의 동기 dat fallback·파일 준비 중 GUI 점유가 실제 남은 부분만 확인하여 worker 이관 후보로 유지한다.
- 주의: 모핑/export 전체 동기라는 옛 전제는 폐기한다. Claude FINAL LCH-20은 #456을 해소로 판정하므로 AL-12를 확정 신규 작업으로 세기 전에 해당 fallback의 현재 호출 경로·점유를 재대조해야 한다.
- 대응 확신: 중간 (실행 성공 여부와 별개)

### [#457](https://github.com/NumeRealWorks/DashOpti_GUI/issues/457) · 분할

- 원본: 미배정 / Backlog / Medium
- 핵심 축: 수명안정 / 식별계약 / 실행계약
- 주된 대응: [OPT-02](../../03_TASK_CATALOG.md#opt-02), [OPT-07](../../03_TASK_CATALOG.md#opt-07)
- 보조 관련: [CAD-001](../../03_TASK_CATALOG.md#cad-001)
- 변환 범위: Optimizer 모핑 preview의 요청 귀속·펌핑 제거와 NX 응답 태그 소비자 전환을 분리한다.
- 주의: 모핑 본체 worker는 이미 존재한다. OPT-07 NX 소비자는 CAD-001 공통 태그 계약 결정 후의 deferred 범위이며 OPT-02 전체를 기다리게 하지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#512](https://github.com/NumeRealWorks/DashOpti_GUI/issues/512) · 직접

- 원본: W2 09/21–09/27 / Backlog / 우선순위 미기재
- 핵심 축: 수명안정 / 실행계약
- 주된 대응: [GEO-006](../../03_TASK_CATALOG.md#geo-006)
- 보조 관련: —
- 변환 범위: setResults의 이벤트 펌핑과 QC 결정 finished 신호 대기 순서를 정리하여 빠른 결정·닫기에서 결과/취소 신호가 유실되지 않게 한다.
- 주의: 계산 worker를 새로 만들거나 모핑 상태기 전체를 이 이슈에 귀속하지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#513](https://github.com/NumeRealWorks/DashOpti_GUI/issues/513) · 직접

- 원본: 미배정 / Backlog / 우선순위 미기재
- 핵심 축: 수명안정 / 실행계약
- 주된 대응: [RUN-06](../../03_TASK_CATALOG.md#run-06)
- 보조 관련: [AST-003](../../03_TASK_CATALOG.md#ast-003)
- 변환 범위: Model Runner 폴더 메타데이터 스캔을 요청별 snapshot 작업으로 옮기고 재선택·닫기 때 오래된 결과 적용을 차단한다.
- 주의: AST-003의 공통 RW 적재와 다른 경로이며 별도 전체 워커 기반 신설은 필요하지 않다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

## 표시 57 · #473 실행 산출물 항목의 식별자 결합

### [#473](https://github.com/NumeRealWorks/DashOpti_GUI/issues/473) · 부모

- 원본: W4 10/05–10/11 / Backlog / Medium
- 핵심 축: 손실방지 / 식별계약
- 주된 대응: [RUN-03](../../03_TASK_CATALOG.md#run-03), [UI-06](../../03_TASK_CATALOG.md#ui-06)
- 보조 관련: —
- 변환 범위: 채번·케이스 저장/복원·정확한 파일 삭제는 RUN-03, 셀 위젯 행 해석은 UI-06으로 묶고 이 부모는 진행 집계만 남긴다.
- 주의: baseline이 UI-06만 가리키는 것은 자식 #475/#477를 빠뜨린다. #476 대장 조회 화면은 철회된 범위로 되살리지 않는다. DOE 표시 텍스트→케이스 키의 잔여는 #474에서 따로 명시해야 한다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#474](https://github.com/NumeRealWorks/DashOpti_GUI/issues/474) · 부분

- 원본: W2 09/21–09/27 / Backlog / High
- 핵심 축: 정확성 / 식별계약
- 주된 대응: [RUN-03](../../03_TASK_CATALOG.md#run-03), [UI-06](../../03_TASK_CATALOG.md#ui-06)
- 보조 관련: —
- 변환 범위: Runner 케이스 도메인 키와 MCU Builder/Runner 표의 삭제 후 현재 항목 해석을 구분해 적용한다.
- 주의: UI-06은 widget→현재 row 해석이고 모든 표를 영속 ID 모델로 바꾸는 작업은 아니다. 원문의 DOE-D8 표시 텍스트 파싱 제거에 직접 대응하는 명시적 Codex 카드가 없어 전체 동일범위로 처리하지 않는다. Runner preview row는 이미 미사용 인자여서 다른 케이스 preview라는 옛 증상을 그대로 재발행하지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#475](https://github.com/NumeRealWorks/DashOpti_GUI/issues/475) · 통합

- 원본: W2 09/21–09/27 / Backlog / High
- 핵심 축: 손실방지 / 저장계약
- 주된 대응: [RUN-03](../../03_TASK_CATALOG.md#run-03)
- 보조 관련: —
- 변환 범위: 예측 케이스의 영속 ID·다음 번호 또는 충돌 회피를 생성/재진입/삭제와 같은 저장 레코드 안에서 해결한다.
- 주의: RUN-03은 #475보다 넓으며 #477 및 DV·경로 복원 결함도 함께 다룬다. 서로 다른 이슈가 같은 한 작업을 가리키므로 PR 수를 중복 세지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#477](https://github.com/NumeRealWorks/DashOpti_GUI/issues/477) · 통합

- 원본: W2 09/21–09/27 / Backlog / High
- 핵심 축: 손실방지 / 식별계약
- 주된 대응: [RUN-03](../../03_TASK_CATALOG.md#run-03)
- 보조 관련: —
- 변환 범위: 접두사 glob 삭제를 케이스별 소유 파일 목록으로 바꾸고 생성 VTU와 재조회 dat/inp의 경로·DV 정합을 복원한다.
- 주의: 범위는 실제 케이스 파일 소유와 재조회이다. #471의 전체 파이프라인 산출물 대장이 없어도 수정 가능하며 대장 설계를 하드 선행시키지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

## 표시 58 · #438 배치 계산의 취소·진행 표시·재시작 복구를 완결

### [#438](https://github.com/NumeRealWorks/DashOpti_GUI/issues/438) · 부모

- 원본: W4 10/05–10/11 / Backlog / High
- 핵심 축: 손실방지 / 수명안정 / 저장계약 / 실행계약
- 주된 대응: —
- 보조 관련: [AL-03](../../03_TASK_CATALOG.md#al-03), [AL-04](../../03_TASK_CATALOG.md#al-04), [AL-05](../../03_TASK_CATALOG.md#al-05), [AL-06](../../03_TASK_CATALOG.md#al-06), [DIR-01](../../03_TASK_CATALOG.md#dir-01)
- 변환 범위: 배치 제출 terminal·대기 큐 취소·상태 기록·재시작 복구의 자식 완료를 롤업한다.
- 주의: 부모 별도 구현량 없음. DIR-01은 PR652 병합 뒤 잔여 검증만, AL-05 파일 분할은 #444 현행 결정과 충돌하므로 조건부, AL-06은 복구 정책 결정 필요. 실행 이력 목록 #442는 부활시키지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#439](https://github.com/NumeRealWorks/DashOpti_GUI/issues/439) · 직접

- 원본: 미배정 / Backlog / High
- 핵심 축: 수명안정 / 실행계약
- 주된 대응: [AL-04](../../03_TASK_CATALOG.md#al-04)
- 보조 관련: [AL-03](../../03_TASK_CATALOG.md#al-03)
- 변환 범위: Stop이 현재 Motion 실행뿐 아니라 pending 큐의 후속 제출도 막고 모든 추적 케이스를 terminal로 정리하게 한다.
- 주의: 제출 실패 terminal은 AL-03과 맞추되 별도 러너 전면 통합이나 영속 이력 기능을 넣지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#440](https://github.com/NumeRealWorks/DashOpti_GUI/issues/440) · 재판정

- 원본: 미배정 / Backlog / High
- 핵심 축: 실행계약
- 주된 대응: —
- 보조 관련: [DIR-01](../../03_TASK_CATALOG.md#dir-01)
- 변환 범위: 정규 Launcher 상태 연결과 새 Direct Output Cases 상태를 확인하여 이슈 완료/잔여 결함을 판정한다.
- 주의: 정규 경로는 기존 연결이 있고 옛 Direct Set 경로는 PR652 병합으로 대체되었다. DIR-01 전체를 다시 구현하는 변환은 부적절하며 현재 UI 검증 전 완료를 단정하지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#441](https://github.com/NumeRealWorks/DashOpti_GUI/issues/441) · 분할

- 원본: 미배정 / Backlog / Medium
- 핵심 축: 손실방지 / 저장계약 / 실행계약
- 주된 대응: [AL-05](../../03_TASK_CATALOG.md#al-05), [AL-06](../../03_TASK_CATALOG.md#al-06)
- 보조 관련: [AL-07](../../03_TASK_CATALOG.md#al-07), [IO-03](../../03_TASK_CATALOG.md#io-03)
- 변환 범위: 단일 상태 writer·변경 행 갱신과 재시작 시 Interrupted 판정·명시적 재시도를 분리한다.
- 주의: AL-05의 물리 파일 분할 전제는 Claude LCH-32의 분할하지 않음과 충돌한다. 기존 파일 내 쓰기 중복/표 재구축 억제와 복구가 가능한지 먼저 계약을 조정하며 새 journal을 자동 요구하지 않는다. 원자적 IO는 IO-03, 결과 보존은 AL-07 소유.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#442](https://github.com/NumeRealWorks/DashOpti_GUI/issues/442) · 제외

- 원본: 미배정 / 미기재 / Low  (not planned)
- 핵심 축: 
- 주된 대응: —
- 보조 관련: —
- 변환 범위: CLOSED/NOT_PLANNED인 실행 이력 목록은 이력으로만 보존한다.
- 주의: 재시작 상태 복구(AL-06)를 이유로 별도 실행 이력 UI/관리 기능을 되살리지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

## 표시 59 · #443 Set 에 식별자를 부여하고 원장으로 관리

### [#443](https://github.com/NumeRealWorks/DashOpti_GUI/issues/443) · 부분

- 원본: W4 10/05–10/11 / In progress / High
- 핵심 축: 손실방지 / 식별계약
- 주된 대응: [PRJ-04](../../03_TASK_CATALOG.md#prj-04), [PRJ-02](../../03_TASK_CATALOG.md#prj-02)
- 보조 관련: [RUN-05](../../03_TASK_CATALOG.md#run-05), [OPT-01](../../03_TASK_CATALOG.md#opt-01)
- 변환 범위: 기존 setId 발급은 재구현하지 않고 Set 정본/복원과 허용된 Set의 산출물 동반 개명을 나누어 평가한다.
- 주의: PRJ-02는 개명/롤백으로 Claude PRJ-18에 대응한다. Claude PRJ-16 삭제 시 산출물 제거와 PRJ-17 생성 시 고아 폴더 거부는 별도 요구이며 기존 Codex 카드에 명시적 완료 조건이 없다. PRJ-04의 원장 도입은 Claude의 현재 config 기반 보존 전략과 동일하지 않아 설계 선택을 확인해야 한다.
- 대응 확신: 중간 (실행 성공 여부와 별개)

### [#444](https://github.com/NumeRealWorks/DashOpti_GUI/issues/444) · 재판정

- 원본: 미배정 / Backlog / Medium
- 핵심 축: 저장계약
- 주된 대응: [AL-05](../../03_TASK_CATALOG.md#al-05)
- 보조 관련: —
- 변환 범위: 파일 분할 구현을 바로 발행하지 않고 기존 AL-05에서 단일 writer·행 갱신과 물리 파일 분할을 분리하여 처분을 다시 정한다.
- 주의: 명시적 문서 충돌: Codex AL-05는 설정/상태 분리, Claude FINAL LCH-32는 분할하지 않음. 후자는 단일 writer·재구축 억제로 비용을 줄이고 로드 실측 없이는 분할하지 않는 결정이다. 이 행의 task_ids는 수정 대상이지 신규 구현 승인 표시가 아니다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

## 표시 60 · #460 실행 진행 표시·취소·중복 실행 가드의 표준화

### [#460](https://github.com/NumeRealWorks/DashOpti_GUI/issues/460) · 부모

- 원본: W4 10/05–10/11 / Backlog / Medium
- 핵심 축: 수명안정 / 실행계약
- 주된 대응: —
- 보조 관련: [ASY-02](../../03_TASK_CATALOG.md#asy-02), [BLD-02](../../03_TASK_CATALOG.md#bld-02), [OPT-03](../../03_TASK_CATALOG.md#opt-03), [RUN-02](../../03_TASK_CATALOG.md#run-02), [RES-08](../../03_TASK_CATALOG.md#res-08), [RES-09](../../03_TASK_CATALOG.md#res-09), [AL-12](../../03_TASK_CATALOG.md#al-12), [CAD-002](../../03_TASK_CATALOG.md#cad-002)
- 변환 범위: 공통 상태→진행/입력차단 규약과 각 모듈의 실제 busy·terminal·취소 지원 적용을 롤업한다.
- 주의: 부모 별도 구현량 없음. RUN-02의 ND/1D 동시선택 등 모듈 고유 기능은 부분 관련일 뿐 이 부모의 직접 전체 변환이 아니다. 공통 규약이 작은 종료/버튼 결함의 강제 선행은 아니다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#461](https://github.com/NumeRealWorks/DashOpti_GUI/issues/461) · 분할

- 원본: 미배정 / Backlog / Medium
- 핵심 축: 손실방지 / 실행계약
- 주된 대응: [BLD-02](../../03_TASK_CATALOG.md#bld-02), [OPT-03](../../03_TASK_CATALOG.md#opt-03)
- 보조 관련: [ASY-02](../../03_TASK_CATALOG.md#asy-02), [AL-03](../../03_TASK_CATALOG.md#al-03)
- 변환 범위: Builder 시작 거절/실제 job 종료와 Optimizer 중복 설정 제출을 버튼 상태·terminal에 연결한다.
- 주의: ASY-02는 규약/Analyzer 첫 적용의 보조 근거다. Load 재클릭·모듈 진입 계약은 명시적 제외이며 전체 모듈 실행 가드가 이 두 카드로 모두 커버된다고 보지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#462](https://github.com/NumeRealWorks/DashOpti_GUI/issues/462) · 부분

- 원본: 미배정 / Backlog / Medium
- 핵심 축: 실행계약
- 주된 대응: [ASY-02](../../03_TASK_CATALOG.md#asy-02)
- 보조 관련: —
- 변환 범위: ASY-02 안에서 상태·유한/무한 진행·반려·취소 가능 표시 규약을 정하는 부분으로 흡수한다.
- 주의: 원 이슈는 규약 정의다. ASY-02의 Analyzer 첫 구현과 창 이동/리사이즈 개선까지 동일 이슈의 원 요구였다고 확장하지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#463](https://github.com/NumeRealWorks/DashOpti_GUI/issues/463) · 분할

- 원본: 미배정 / Backlog / Medium
- 핵심 축: 수명안정 / 실행계약
- 주된 대응: [ASY-02](../../03_TASK_CATALOG.md#asy-02), [RES-08](../../03_TASK_CATALOG.md#res-08), [RES-09](../../03_TASK_CATALOG.md#res-09), [AL-12](../../03_TASK_CATALOG.md#al-12), [BLD-02](../../03_TASK_CATALOG.md#bld-02), [OPT-03](../../03_TASK_CATALOG.md#opt-03), [CAD-002](../../03_TASK_CATALOG.md#cad-002)
- 보조 관련: [RUN-02](../../03_TASK_CATALOG.md#run-02), [RUN-07](../../03_TASK_CATALOG.md#run-07), [OPT-02](../../03_TASK_CATALOG.md#opt-02)
- 변환 범위: Analyzer 공통 UI 적용과 Preprocess/Launcher/Builder/Optimizer/CAD의 작업별 진행·취소·가드를 해당 카드 안에서 적용한다.
- 주의: 확산만 별도 중복 발행하지 않는다. 각 카드의 일부 범위이며 전체 모듈 일괄 완료 대응은 아니다. 취소 불가 SDK에는 취소 버튼을 약속하지 않으며 AL-12는 #456 재판정 후 채택한다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#464](https://github.com/NumeRealWorks/DashOpti_GUI/issues/464) · 부분

- 원본: 미배정 / Backlog / Low
- 핵심 축: 실행계약 / 주변개선
- 주된 대응: [CAD-002](../../03_TASK_CATALOG.md#cad-002)
- 보조 관련: [ASY-02](../../03_TASK_CATALOG.md#asy-02)
- 변환 범위: CAD preview 시작 표시와 STEP 표시 실패의 종료 누락 등 실제 남은 진행 표시 비대칭을 좁혀 수정한다.
- 주의: Codex의 성공 stop 부재 진단과 달리 Claude CAD-07은 stepFileLoaded 성공 stop을 이미 해결로 판정한다. 성공 경로 신규 구현은 재확인 전 제외하고 preview 시작/실패 반환 경로에 집중한다.
- 대응 확신: 중간 (실행 성공 여부와 별개)

## 표시 61 · #465 외부 프로세스 안전핀 일괄 — 무음 실패·타임아웃·인코딩·널 가드

### [#465](https://github.com/NumeRealWorks/DashOpti_GUI/issues/465) · 부모

- 원본: W4 10/05–10/11 / Backlog / Medium
- 핵심 축: 수명안정 / 실행계약
- 주된 대응: —
- 보조 관련: [UI-05](../../03_TASK_CATALOG.md#ui-05), [ASY-03](../../03_TASK_CATALOG.md#asy-03), [ASY-04](../../03_TASK_CATALOG.md#asy-04), [BLD-02](../../03_TASK_CATALOG.md#bld-02), [OPT-03](../../03_TASK_CATALOG.md#opt-03), [ANA-07](../../03_TASK_CATALOG.md#ana-07)
- 변환 범위: 통지 규칙/실제 무음 실패, 명령 응답 timeout, nullable·인코딩 경계의 자식 작업을 롤업한다.
- 주의: 별도 일괄 안전핀 PR 없음. 기동 timeout 부재나 모든 포인터 가드 필요라는 옛 진단을 유지하지 않는다. 실제 모듈 오류는 개별 terminal 카드에 배분한다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#466](https://github.com/NumeRealWorks/DashOpti_GUI/issues/466) · 통합

- 원본: 미배정 / Backlog / High
- 핵심 축: 실행계약 / 주변개선
- 주된 대응: [UI-05](../../03_TASK_CATALOG.md#ui-05)
- 보조 관련: [BLD-02](../../03_TASK_CATALOG.md#bld-02), [OPT-03](../../03_TASK_CATALOG.md#opt-03), [ANA-07](../../03_TASK_CATALOG.md#ana-07), [AL-03](../../03_TASK_CATALOG.md#al-03)
- 변환 범위: #482와 공유하는 실패 통지 규약을 UI-05에 통합하고 실제 실패 연결 누락은 모듈 카드의 적용 근거로 연결한다.
- 주의: 원 이슈는 규칙만이고 개별 수정은 제외한다. 따라서 BLD/OPT/ANA/AL 카드는 보조 적용처이며 전부 #466의 주된 변환으로 중복 계산하지 않는다. UI-05의 영어 표기/일반 확인 대화상자 전체도 #466보다 넓다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#467](https://github.com/NumeRealWorks/DashOpti_GUI/issues/467) · 부분

- 원본: 미배정 / Backlog / Medium
- 핵심 축: 수명안정 / 실행계약
- 주된 대응: [ASY-03](../../03_TASK_CATALOG.md#asy-03)
- 보조 관련: —
- 변환 범위: 이미 존재하는 ready/stop timeout을 유지하고 명령 제출 후 무응답 시한·늦은 응답 격리·한 번의 terminal 처리를 추가한다.
- 주의: 기동 timeout을 신규로 만드는 작업은 제외한다. 시한과 timeout 뒤 데몬 재사용/대기 큐 정책은 명령 종류별 결정이 필요하다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#468](https://github.com/NumeRealWorks/DashOpti_GUI/issues/468) · 부분

- 원본: 미배정 / Backlog / High
- 핵심 축: 수명안정 / 실행계약
- 주된 대응: [ASY-04](../../03_TASK_CATALOG.md#asy-04)
- 보조 관련: [PRJ-09](../../03_TASK_CATALOG.md#prj-09), [PRJ-10](../../03_TASK_CATALOG.md#prj-10)
- 변환 범위: 실제로 null 가능한 process/session 경계만 실패를 명시적으로 전달하도록 보강한다.
- 주의: 항상 존재하는 singleton에 기계적으로 가드를 더하지 않는다. 소유권/의존 주입은 PRJ 카드의 별도 범위이며 ASY-04의 인코딩 절반은 #469 소유다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#469](https://github.com/NumeRealWorks/DashOpti_GUI/issues/469) · 부분

- 원본: 미배정 / Backlog / Medium
- 핵심 축: 정확성 / 실행계약
- 주된 대응: [ASY-04](../../03_TASK_CATALOG.md#asy-04)
- 보조 관련: —
- 변환 범위: 한글·공백 경로와 분할된 멀티바이트 출력을 보존하도록 외부 exe별 실제 인코딩 계약과 경계 어댑터를 정리한다.
- 주의: 이미 UTF-8인 ProcessJob/ExtensionProcess 경로를 반복 수정하지 않는다. 외부 SDK가 다른 인코딩이면 전역 UTF-8 치환 대신 해당 경계에서 명시적으로 처리한다. #468과 같은 카드의 다른 부분이다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

## 표시 62 · #470 실행 산출물의 유래 추적 — 스탬프와 대장

### [#470](https://github.com/NumeRealWorks/DashOpti_GUI/issues/470) · 부모

- 원본: W4 10/05–10/11 / Backlog / Medium
- 핵심 축: 정확성 / 식별계약
- 주된 대응: [PRJ-03](../../03_TASK_CATALOG.md#prj-03), [PRJ-05](../../03_TASK_CATALOG.md#prj-05), [IO-10](../../03_TASK_CATALOG.md#io-10), [IO-11](../../03_TASK_CATALOG.md#io-11)
- 보조 관련: [PRJ-11](../../03_TASK_CATALOG.md#prj-11)
- 변환 범위: 유래 추적 부모를 조합 스탬프(#368), 산출물 세대, 과거 생산/소비 대장(#471)의 서로 다른 목적별 집계로 바꾼다.
- 주의: Claude는 PER-09 부모 CLOSE와 PER-11 대장 CLOSE를 제안하고 Codex는 대장 구현을 유지한다. 부모와 자식 중복 집계 금지. 대장 세 작업이 Claude에서는 제거 대상이므로 의존 수/작업 수를 단순 비교하지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#471](https://github.com/NumeRealWorks/DashOpti_GUI/issues/471) · 재판정

- 원본: 미배정 / Backlog / High
- 핵심 축: 식별계약
- 주된 대응: [PRJ-05](../../03_TASK_CATALOG.md#prj-05), [IO-10](../../03_TASK_CATALOG.md#io-10), [IO-11](../../03_TASK_CATALOG.md#io-11)
- 보조 관련: [PRJ-11](../../03_TASK_CATALOG.md#prj-11)
- 변환 범위: Codex 변환은 파일 대장 기반과 AL→Builder 첫 연결, Builder 모델 생산/소비, DOE/예측/최적화/Analyzer 확산이다. 시행 전에 과거 run별 소비 이력 요구를 유지할지 명시적으로 재판정한다.
- 주의: Claude FINAL PER-11은 대장 불요 CLOSE 제안이다. 조합 핀/현재 tableId 참조 스캔으로 알 수 있는 현재 관계와 과거 실행별 소비 이력은 동일 정보가 아니므로 자동으로 동등 대체됐다고 보지 않는다. 대장을 제외하더라도 #650의 산출물 세대 경고(PRJ-11)는 독립 목적이므로 함께 제외하지 않는다. 이번 overlay는 원 이슈를 닫거나 Codex 정본을 변경하지 않는다.
- 대응 확신: 중간 (실행 성공 여부와 별개)

### [#368](https://github.com/NumeRealWorks/DashOpti_GUI/issues/368) · 재판정

- 원본: 미배정 / Backlog / High
- 핵심 축: 정확성 / 식별계약
- 주된 대응: [PRJ-03](../../03_TASK_CATALOG.md#prj-03)
- 보조 관련: [BLD-01](../../03_TASK_CATALOG.md#bld-01), [RUN-05](../../03_TASK_CATALOG.md#run-05), [OPT-01](../../03_TASK_CATALOG.md#opt-01), [PRJ-11](../../03_TASK_CATALOG.md#prj-11)
- 변환 범위: PRJ-03의 조합 스탬프 생산→snapshot 전파→Preprocess/Builder/Runner/Optimizer 핀·검증이라는 기능 범위는 유지하되, 폐기된 PR530 병합 대신 현재 dev에 필요한 공통부와 홉별 변경을 재이식·통합 검증하는 작업으로 읽는다.
- 주의: 2026-10-07 relevant-prs.json에서 PR530 CLOSED, mergedAt=null. 기존 카탈로그 in_flight/병합 추적 설명은 오래됨. Claude PER-06/07＋DOE-16/PRE-32/BLD-20/RUN-34/OPT-26은 재이식 분할이다. BLD-01/RUN-05/OPT-01은 #650 세대 경고 후속이므로 #368의 직접 구현과 중복 집계하지 않는다. DOE 기록-only, MCU 예외, templateDecks 철회, kSnapshotKeys 전파를 보존한다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

## 표시 63 · #514 표 셀 위젯이 캡처한 행 번호가 삭제 후 어긋난다 — 전수조사 잔여 5건과 행 해석 규칙 통일 (#503 계열)

### [#514](https://github.com/NumeRealWorks/DashOpti_GUI/issues/514) · 직접

- 원본: W4 10/05–10/11 / Backlog / High
- 핵심 축: 정확성 / 식별계약
- 주된 대응: [UI-06](../../03_TASK_CATALOG.md#ui-06)
- 보조 관련: [RUN-03](../../03_TASK_CATALOG.md#run-03)
- 변환 범위: 살아 있는 MCU Builder/Runner Browse 캡처를 현재 행으로 해석하고 공용 헬퍼 및 Runner preview의 죽은 row 인자를 정리한다.
- 주의: 삭제된 ReferenceFileWidget과 PR652에서 제거된 Direct 입력표의 구 결함은 재생성하지 않는다. 최신 PR652 MERGED. RUN-03의 영속 케이스 ID는 연관되지만 다른 변경 범위다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

## 표시 64 · #543 비동기 작업 중 UI 차단·진행 표시의 UI/UX 정리

### [#543](https://github.com/NumeRealWorks/DashOpti_GUI/issues/543) · 통합

- 원본: W4 10/05–10/11 / Backlog / Medium
- 핵심 축: 수명안정 / 실행계약 / 주변개선
- 주된 대응: [ASY-02](../../03_TASK_CATALOG.md#asy-02)
- 보조 관련: [UI-03](../../03_TASK_CATALOG.md#ui-03)
- 변환 범위: 기존 비동기 작업의 내용 입력 차단·작업 문구·진행 표시·반려/종료 복구를 표준화하고 창 이동/리사이즈를 유지한다.
- 주의: #462 및 #460 공통 UI 부분과 한 번만 구현한다. 비동기 실행기 자체 신설이나 리소스별 scheduler·협력취소 API 구현을 이 UI 항목의 선행으로 부풀리지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

## 표시 65 · #551 프로젝트 전환 시 나머지 모듈 위젯 7곳도 해제된 모델을 역참조한다 — #549 전수조사 잔여

### [#551](https://github.com/NumeRealWorks/DashOpti_GUI/issues/551) · 통합

- 원본: W4 10/05–10/11 / Backlog / 우선순위 미기재
- 핵심 축: 수명안정
- 주된 대응: [PRJ-01](../../03_TASK_CATALOG.md#prj-01)
- 보조 관련: [RUN-07](../../03_TASK_CATALOG.md#run-07), [OPT-02](../../03_TASK_CATALOG.md#opt-02)
- 변환 범위: 프로젝트 모델 삭제 전 위젯 연결/포인터/외부 sender 콜백을 정리해 새 프로젝트 진입 시 해제 모델 접근을 막는다.
- 주의: #551의 나머지 7곳 수정은 PRJ-01의 공통 수명 계약 안에 흡수된다. #549로 이미 끝난 Runner QPointer 교체를 다시 세지 않는다. 비동기 결과의 Set 귀속은 지원 카드 범위다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

## 표시 66 · #499 morphing: mesh-ops 버전 범프 수용 — 신규 handle 생성기 API 와 고립 handle 옵션

### [#499](https://github.com/NumeRealWorks/DashOpti_GUI/issues/499) · 분할

- 원본: W4 10/05–10/11 / Backlog / High
- 핵심 축: 정확성 / 저장계약 / 주변개선
- 주된 대응: [GEO-004](../../03_TASK_CATALOG.md#geo-004), [GEO-005](../../03_TASK_CATALOG.md#geo-005)
- 보조 관련: [GEO-001](../../03_TASK_CATALOG.md#geo-001), [GEO-002](../../03_TASK_CATALOG.md#geo-002)
- 변환 범위: 이미 끝난 baseline 범프·isolated handles 통로와 PR654의 sampling/section 상태기 몫을 제외한다. 남은 것은 Box FFD 생성·면 DV·저장/DOE 흐름(GEO-004), 단면 추출기 section_frames 직접 소비와 사내 MarchingPlaneBound 제거(GEO-005)다.
- 주의: PR655는 old shell box GUI 경로를 삭제하고 Box JSON entry만 남긴다고 보고하므로 GEO-004는 단순 어댑터 이관이 아니라 새 생성 UI 연결이다. #577의 신규 FFD 방향은 유지하되 실제 UI 세부·baseline 편집 범위는 결정해야 한다. Claude MOR-05는 기능 채택까지 DEC로 재평가하지만 최신 #577 요구가 철회됐다는 증거는 아니므로 신규 FFD 요구 자체를 취소/미승인으로 단정하지 않는다. GEO-005도 PR655 이후 실제 section producer 좌표를 다시 확인해야 하며 기존 중심점→격자 변경을 반복 구현하지 않는다.
- 대응 확신: 중간 (실행 성공 여부와 별개)

## 표시 68 · #635 결과 XML 작성기가 Motion 컴포넌트의 entity_name 을 질의에 싣지 않아 전체 모델을 읽는다

### [#635](https://github.com/NumeRealWorks/DashOpti_GUI/issues/635) · 부분

- 원본: W4 10/05–10/11 / In progress / 우선순위 미기재
- 핵심 축: 정확성
- 주된 대응: [RES-04](../../03_TASK_CATALOG.md#res-04)
- 보조 관련: [RES-11](../../03_TASK_CATALOG.md#res-11), [RES-03](../../03_TASK_CATALOG.md#res-03)
- 변환 범위: RES-04 중 writer component 항의 entity_name 보존과 명시적 Motion Kind 전달을 PR663 범위로 마무리한다.
- 주의: RES-04의 State 해석 부분은 PR662 완료이므로 새로 세지 않는다. PR663은 OPEN이고 PR658과 writer/Kind 접점 조정 및 실제 dfr BODY 선택 검증이 남는다. RES-03 전체가 이 좁은 수정의 절대 선행은 아니다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

## 표시 69 · #649 DOE Sampler·Analysis Launcher 재구성 후속 — Set 정책·입력 포맷·화면 갱신

### [#649](https://github.com/NumeRealWorks/DashOpti_GUI/issues/649) · 부모

- 원본: W4 10/05–10/11 / Backlog / 우선순위 미기재
- 핵심 축: 손실방지 / 정확성 / 실행계약 / 식별계약
- 주된 대응: [DOE-01](../../03_TASK_CATALOG.md#doe-01), [DOE-02](../../03_TASK_CATALOG.md#doe-02), [AL-01](../../03_TASK_CATALOG.md#al-01), [AL-07](../../03_TASK_CATALOG.md#al-07), [AL-08](../../03_TASK_CATALOG.md#al-08), [AL-09](../../03_TASK_CATALOG.md#al-09), [AL-10](../../03_TASK_CATALOG.md#al-10), [AST-001](../../03_TASK_CATALOG.md#ast-001), [CON-001](../../03_TASK_CATALOG.md#con-001), [RES-12](../../03_TASK_CATALOG.md#res-12), [RES-13](../../03_TASK_CATALOG.md#res-13), [DIR-01](../../03_TASK_CATALOG.md#dir-01), [PRJ-11](../../03_TASK_CATALOG.md#prj-11), [BLD-01](../../03_TASK_CATALOG.md#bld-01), [RUN-05](../../03_TASK_CATALOG.md#run-05), [OPT-01](../../03_TASK_CATALOG.md#opt-01), [ANA-03](../../03_TASK_CATALOG.md#ana-03), [DOE-03](../../03_TASK_CATALOG.md#doe-03)
- 보조 관련: [PRJ-03](../../03_TASK_CATALOG.md#prj-03)
- 변환 범위: 재구성 후속 부모는 각 자식의 실제 변경과 완료 상태를 모으는 집계로 유지한다. 입력정책/특수 solver, 재실행, 자산교체, XML, Set/세대 경고를 별도 작업군으로 읽는다.
- 주의: 추적 부모 자체 PR를 만들지 않는다. baseline 목록에 빠진 #647의 AL-10을 포함한다. PR651·652 MERGED이므로 AL-09/DIR-01의 병합 대기는 검증/잔여 판정으로 바뀐다. 자식 작업 수와 부모 롤업을 중복 집계하지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#643](https://github.com/NumeRealWorks/DashOpti_GUI/issues/643) · 분할

- 원본: W5 10/12–10/18 / Backlog / 우선순위 미기재
- 핵심 축: 저장계약 / 식별계약
- 주된 대응: [RES-12](../../03_TASK_CATALOG.md#res-12), [RES-13](../../03_TASK_CATALOG.md#res-13)
- 보조 관련: [PRJ-11](../../03_TASK_CATALOG.md#prj-11), [BLD-01](../../03_TASK_CATALOG.md#bld-01), [ANA-03](../../03_TASK_CATALOG.md#ana-03)
- 변환 범위: Set 단위 결과 작성과 생산자/Builder·Analyzer 소비자 포맷 이행을 RES-12로 묶고, 증분 정책·XML/HDF5/USD 선택의 측정과 결정을 RES-13으로 구분한다.
- 주의: HDF5/USD 채택은 확정 요구가 아니다. 1차도 서로 다른 uuid/tableId를 섞지 않는 최소 교체 규칙은 먼저 필요하다. PRJ-11의 포맷 중립 generation 계약을 쓰며 PR530 전체 병합이나 최종 포맷 선택이 모든 stale 경고의 하드 선행은 아니다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#645](https://github.com/NumeRealWorks/DashOpti_GUI/issues/645) · 분할

- 원본: W4 10/05–10/11 / Backlog / 우선순위 미기재
- 핵심 축: 손실방지 / 정확성
- 주된 대응: [AST-001](../../03_TASK_CATALOG.md#ast-001), [CON-001](../../03_TASK_CATALOG.md#con-001)
- 보조 관련: —
- 변환 범위: 파일/동반 폴더 교체를 실패 복구 가능하게 만든 뒤 성공 통지를 통해 Condition 문서·DV 바인딩을 갱신한다.
- 주의: PR651의 특수 포맷 병합은 이 덮어쓰기 실패 안전성과 Condition 내용 갱신까지 완료했다는 증거가 아니다. 기존 조사에서 직접 삭제가 확인된 것은 file/context/tree이며 원장 유실이라는 원문 표현은 런타임 확인 없이 확정하지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#646](https://github.com/NumeRealWorks/DashOpti_GUI/issues/646) · 분할

- 원본: W4 10/05–10/11 / Backlog / 우선순위 미기재
- 핵심 축: 손실방지 / 정확성
- 주된 대응: [AL-07](../../03_TASK_CATALOG.md#al-07), [AL-08](../../03_TASK_CATALOG.md#al-08)
- 보조 관련: —
- 변환 범위: 재실행 실패/취소 시 이전 결과 보존과 완료 뒤 Preprocess 입력·선택 목록 갱신을 별도로 완결한다. Skip 안내는 실제 정책에 맞춰 AL-07에 포함한다.
- 주의: 안내 문구만 수정하면 데이터 손실·옛 결과 재사용 문제가 남는다. 기존 Skip 설명은 일부 있으므로 설명 PR를 별도로 늘리지 않는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#615](https://github.com/NumeRealWorks/DashOpti_GUI/issues/615) · 분할

- 원본: W4 10/05–10/11 / Backlog / 우선순위 미기재
- 핵심 축: 정확성 / 실행계약
- 주된 대응: [DOE-01](../../03_TASK_CATALOG.md#doe-01), [DOE-02](../../03_TASK_CATALOG.md#doe-02)
- 보조 관련: —
- 변환 범위: ResampleN 추가/채번/기본 참조와 이전 케이스 active 반영을 구분한다.
- 주의: DOE-02는 복수 Launcher Set의 active가 다를 때 어느 것을 샘플 유효성 기준으로 쓸지 결정 필요. DOE-01 Set 번호와 RUN-03 예측 산출물 번호는 전혀 다른 채번이다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#647](https://github.com/NumeRealWorks/DashOpti_GUI/issues/647) · 직접

- 원본: W4 10/05–10/11 / Backlog / 우선순위 미기재
- 핵심 축: 정확성 / 실행계약
- 주된 대응: [AL-10](../../03_TASK_CATALOG.md#al-10)
- 보조 관련: —
- 변환 범위: GUI의 특정 LGE 모델 하드코딩을 제거하고 모델별 규칙을 외부 AnsysMotion 처리와 조율하여 run별 입력 묶음 생성/실패를 완결한다.
- 주의: 외부 DashOptiMBD 저장소 변경·실제 Motion 파일 검증이 필요할 수 있다. GUI 경로만 옮기거나 .dfsxml 입력을 허용하는 PR651 병합만으로 완료가 아니다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#648](https://github.com/NumeRealWorks/DashOpti_GUI/issues/648) · 재판정

- 원본: W4 10/05–10/11 / Backlog / 우선순위 미기재
- 핵심 축: 정확성 / 실행계약
- 주된 대응: [AL-09](../../03_TASK_CATALOG.md#al-09)
- 보조 관련: —
- 변환 범위: 선택 Source Set의 같은 DoeSet/runKey ODB 연결·복사와 누락/미완료/삭제/복사 실패를 병합된 구현에서 확인하고 남은 결함만 수정한다.
- 주의: 2026-10-07 relevant-prs.json PR651 MERGED, mergedAt=2026-10-07T04:56:46Z. 따라서 새 동일 구현이나 병합 대기 작업이 아니라 병합 완료 후 #648 범위 검증으로 변환한다. 이슈 OPEN은 구현 미병합을 뜻하지 않으며 실제 solver 회귀 통과 자료는 이 스냅샷에 없다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#639](https://github.com/NumeRealWorks/DashOpti_GUI/issues/639) · 직접

- 원본: W4 10/05–10/11 / Backlog / 우선순위 미기재
- 핵심 축: 손실방지 / 실행계약
- 주된 대응: [AL-01](../../03_TASK_CATALOG.md#al-01)
- 보조 관련: —
- 변환 범위: Target Part loading/ready/failed를 Start 게이트와 연결하고 실패/빈 후보에서 저장된 target pin을 보존한다.
- 주의: 일반 진행 표시 작업으로 축소하면 빈 target 저장 결함이 남는다. 이미 있는 Set generation 가드는 보존하며 독립적으로 검증한다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

### [#650](https://github.com/NumeRealWorks/DashOpti_GUI/issues/650) · 분할

- 원본: W5 10/12–10/18 / Backlog / 우선순위 미기재
- 핵심 축: 정확성 / 식별계약
- 주된 대응: [PRJ-11](../../03_TASK_CATALOG.md#prj-11), [BLD-01](../../03_TASK_CATALOG.md#bld-01), [RUN-05](../../03_TASK_CATALOG.md#run-05), [OPT-01](../../03_TASK_CATALOG.md#opt-01), [ANA-03](../../03_TASK_CATALOG.md#ana-03), [DOE-03](../../03_TASK_CATALOG.md#doe-03)
- 보조 관련: [PRJ-03](../../03_TASK_CATALOG.md#prj-03)
- 변환 범위: 조합 id와 다른 산출물 generation 계약, 모듈별 upstream 참조 저장/복원, 공통 검사와 트리 경고 적용으로 나눈다.
- 주의: PRJ-03은 관련 조합 핀 기반이지 #650 전 범위와 동일하지 않다. Claude PRJ-23은 Geometry/Condition→DOE 세대 결정으로 Codex PRJ-11의 AL 결과 generation 첫 적용과 부분 대응이다. 과거 소비 대장(#471)을 제외해도 현재 stale 경고 요구는 남는다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

## 표시 70 · #664 Motion 미리보기가 응답 키 없이 조회해 래퍼 불일치·배열 선택 실패로 끝난다

### [#664](https://github.com/NumeRealWorks/DashOpti_GUI/issues/664) · 부분

- 원본: W4 10/05–10/11 / In progress / 우선순위 미기재
- 핵심 축: 정확성
- 주된 대응: [RES-03](../../03_TASK_CATALOG.md#res-03)
- 보조 관련: [RES-04](../../03_TASK_CATALOG.md#res-04), [RES-11](../../03_TASK_CATALOG.md#res-11)
- 변환 범위: 카탈로그 이후 신설된 이슈를 RES-03의 Motion Preview 응답 leaf/operator/field_output_name 및 배열 선택 후보 누락 부분에 새로 대응한다.
- 주의: RES-03 전체 응답 질의 공통화와 동일하지 않다. PR665는 PR663 위의 OPEN 스택이며 PR658 putResponseTerm 통합 후 호출을 맞출 필요가 있다. #634/PR662 완료를 재작업하지 않고 실제 dfr Preview 검증을 남긴다.
- 대응 확신: 높음 (실행 성공 여부와 별개)

## 역방향: 기존 작업 위에 겹친 이슈

행 수는 신규 PR 개수가 아니다. 관련 참조만 있는 카드는 실행 대상으로 자동 편입하지 않는다.

| 기존 작업 | 직접 범위 대조 이슈 | 부모 묶음 | 보조 관련 |
|---|---|---|---|
| [GEO-001](../../03_TASK_CATALOG.md#geo-001) 핸들 편집·실행·저장을 Setup/Configuration 값 모델로 전환한다 | — | #246 | #434, #430, #281, #499 |
| [GEO-002](../../03_TASK_CATALOG.md#geo-002) 핸들 interaction이 값 모델의 투영만 편집하도록 소유권을 마무리한다 | #430 | #427 | #281, #499 |
| [GEO-004](../../03_TASK_CATALOG.md#geo-004) Hexahedron을 BoxHandles FFD 생성·면 DV 흐름으로 제공한다 | #499 | — | — |
| [GEO-005](../../03_TASK_CATALOG.md#geo-005) 단면 추출·핸들 생성을 mesh-ops 공개 API로 끝까지 이관한다 | #499 | — | — |
| [GEO-006](../../03_TASK_CATALOG.md#geo-006) QC 결과 창을 닫아도 저장 작업이 대기 상태에 갇히지 않게 한다 | #512 | #451 | #281, #455 |
| [GEO-007](../../03_TASK_CATALOG.md#geo-007) 모핑 값 경계의 미검증 교차 모듈 시나리오를 검증하고 발견된 회귀를 닫는다 | #281 | #427 | — |
| [VIS-001](../../03_TASK_CATALOG.md#vis-001) Optimizer 프리뷰가 자기 actor만 교체하도록 한다 | #316 | #427 | #318 |
| [VIS-002](../../03_TASK_CATALOG.md#vis-002) FE actor의 숨김·복원·등록 수명과 카메라 갱신을 바로잡는다 | #319 | #427 | #318 |
| [VIS-003](../../03_TASK_CATALOG.md#vis-003) 씬 콘텐츠를 모듈·문서 단위로 등록하고 전환 시 보존 정책을 적용한다 | #318 | #246, #427 | #434, #316, #319 |
| [VIS-004](../../03_TASK_CATALOG.md#vis-004) split view 이탈과 ghost 외형·범례 복원을 씬 전환에 연결한다 | #318 | #427 | #319 |
| [VIS-005](../../03_TASK_CATALOG.md#vis-005) VTK/VTU 파일별 표시 핸들을 등록하여 눈 토글을 구현한다 | — | — | #318 |
| [AST-001](../../03_TASK_CATALOG.md#ast-001) 파일·폴더 묶음의 덮어쓰기를 실패 시 복구 가능한 교체로 만든다 | #645 | #649 | — |
| [AST-003](../../03_TASK_CATALOG.md#ast-003) RW 파싱과 문서 수집을 GUI 밖에서 실행하고 적재 수명을 보장한다 | — | — | #281, #513 |
| [CON-001](../../03_TASK_CATALOG.md#con-001) 참조 파일 교체 후 조건 목록과 DV 바인딩을 새 문서로 갱신한다 | #645 | #649 | — |
| [CAD-001](../../03_TASK_CATALOG.md#cad-001) CAD 요청의 의도와 완료 결과를 동일한 요청 식별자로 왕복시킨다 | — | — | #457 |
| [CAD-002](../../03_TASK_CATALOG.md#cad-002) CAD 로드·프리뷰의 진행 표시 시작과 종료를 요청 수명에 맞춘다 | #463, #464 | #460 | — |
| [DOE-01](../../03_TASK_CATALOG.md#doe-01) 번호가 있는 Resample Set을 추가하고 참조 Set을 기본 연결한다 | #615 | #649 | — |
| [DOE-02](../../03_TASK_CATALOG.md#doe-02) Resample 이력에서 실제 비활성 케이스를 제외한다 | #615 | #649 | — |
| [DOE-03](../../03_TASK_CATALOG.md#doe-03) DOE Set에서 상류 형상·조건 변경 경고를 표시한다 | #650 | #649 | — |
| [AL-01](../../03_TASK_CATALOG.md#al-01) Target Part 로딩 중 실행을 막고 실패 시 저장된 선택을 보존한다 | #639 | #649 | — |
| [AL-03](../../03_TASK_CATALOG.md#al-03) 모든 제출 실패와 프로젝트 전환이 케이스를 종결하게 한다 | — | #438 | #439, #461, #466 |
| [AL-04](../../03_TASK_CATALOG.md#al-04) Stop이 Motion 대기 큐와 진행 작업을 함께 취소한다 | #439 | #438 | — |
| [AL-05](../../03_TASK_CATALOG.md#al-05) 케이스 상태를 증분 기록하고 표의 변경 행만 갱신한다 | #441, #444 | #438 | — |
| [AL-06](../../03_TASK_CATALOG.md#al-06) 재시작 시 중단된 배치를 식별하고 안전한 재시도를 제공한다 | #441 | #438 | — |
| [AL-07](../../03_TASK_CATALOG.md#al-07) Re-run 실패와 취소에서 이전 결과와 기록을 보존한다 | #646 | #649 | #441 |
| [AL-08](../../03_TASK_CATALOG.md#al-08) 실행 완료 후 Preprocess 입력과 선택 목록을 새 결과로 갱신한다 | #646 | #649 | — |
| [AL-09](../../03_TASK_CATALOG.md#al-09) 특수 입력 포맷의 Assets·Set·Launcher·fe-safe ODB 연결을 통합·검증한다 | #648 | #649 | — |
| [AL-10](../../03_TASK_CATALOG.md#al-10) Motion 모델별 생성 규칙을 Python으로 옮기고 run 입력 묶음을 완성한다 | #647 | #649 | — |
| [AL-12](../../03_TASK_CATALOG.md#al-12) 남은 동기 입력 준비와 dat fallback을 취소 가능한 작업으로 옮긴다 | #456, #463 | #451, #460 | — |
| [DIR-01](../../03_TASK_CATALOG.md#dir-01) Tool 메뉴 Direct Launch와 Result Preview를 통합·검증한다 | — | #438, #649 | #440 |
| [RES-03](../../03_TASK_CATALOG.md#res-03) 응답 이름과 operator를 함께 전달해 올바른 필드를 선택한다 | #664 | — | #433, #635 |
| [RES-04](../../03_TASK_CATALOG.md#res-04) Motion의 State와 Component를 Preview·배치에서 동일하게 해석한다 | #433, #635 | — | #664 |
| [RES-05](../../03_TASK_CATALOG.md#res-05) Modal 변위 응답을 하나의 규칙으로 선택하고 모든 성분을 처리한다 | #433 | — | — |
| [RES-08](../../03_TASK_CATALOG.md#res-08) 결과 파일 Load와 일반 Preview 조회를 워커 실행으로 옮긴다 | #454, #463 | #451, #460 | — |
| [RES-09](../../03_TASK_CATALOG.md#res-09) 일반 배치 처리·XML 생성을 워커로 옮기고 이벤트 펌핑을 제거한다 | #454, #463 | #451, #460 | #433 |
| [RES-10](../../03_TASK_CATALOG.md#res-10) 남은 시점·모달 이름·직렬화 사본을 검증된 질의 함수로 모은다 | — | #246 | #433 |
| [RES-11](../../03_TASK_CATALOG.md#res-11) Modal·Motion·fe-safe 실제 파일 회귀와 처리 경계 검증을 완성한다 | #433 | #246 | #635, #664 |
| [RES-12](../../03_TASK_CATALOG.md#res-12) 응답별 XML을 Set 단위 결과 파일로 전환하고 소비자를 함께 이행한다 | #643 | #649 | — |
| [RES-13](../../03_TASK_CATALOG.md#res-13) Set 결과의 이어쓰기·덮어쓰기와 XML/HDF5/USD 방향을 측정해 결정한다 | #643 | #649 | — |
| [BLD-01](../../03_TASK_CATALOG.md#bld-01) 학습 입력과 생성 모델의 Set·산출물 버전을 기록하고 상류 변경을 표시한다 | #650 | #649 | #368, #643 |
| [BLD-02](../../03_TASK_CATALOG.md#bld-02) 학습 시작 거절·실패·취소를 하나의 종료 상태로 화면에 반영한다 | #461, #463 | #460, #465 | #466 |
| [RUN-02](../../03_TASK_CATALOG.md#run-02) ND·1D 동시 선택을 실행별 입력 스냅샷과 결과로 처리한다 | — | #460 | #463 |
| [RUN-03](../../03_TASK_CATALOG.md#run-03) 예측 케이스와 산출물 목록을 영속 식별자로 생성·복원·삭제한다 | #474, #475, #477 | #473 | #514 |
| [RUN-05](../../03_TASK_CATALOG.md#run-05) 선택한 학습 Set·모델 버전을 복원하고 재학습 변경을 표시한다 | #650 | #649 | #443, #368 |
| [RUN-06](../../03_TASK_CATALOG.md#run-06) 모델 폴더 로드를 비동기 스냅샷으로 바꾸고 중복 읽기를 줄인다 | #513 | #451 | — |
| [RUN-07](../../03_TASK_CATALOG.md#run-07) 입력 생성 요청을 Set에 고정하고 늦은 완료·취소를 처리한다 | — | — | #431, #281, #463, #551 |
| [OPT-01](../../03_TASK_CATALOG.md#opt-01) 학습 모델·Geometry·Condition 참조 버전을 기록하고 변경을 표시한다 | #650 | #649 | #443, #368 |
| [OPT-02](../../03_TASK_CATALOG.md#opt-02) 프리뷰 요청 완료를 호출 Set으로 돌려주고 취소·재진입을 처리한다 | #281, #457 | #451 | #431, #316, #463, #551 |
| [OPT-03](../../03_TASK_CATALOG.md#opt-03) 최적화 진행·실패·취소를 Run 버튼과 결과 화면에 연결한다 | #461, #463 | #460, #465 | #466 |
| [ANA-03](../../03_TASK_CATALOG.md#ana-03) 표시 중인 결과의 출처 Set과 상류 버전 경고를 보여준다 | #650 | #649 | #643 |
| [ANA-07](../../03_TASK_CATALOG.md#ana-07) 플롯 생성·내보내기 실패를 표시하고 지원하는 메뉴만 활성화한다 | — | #465 | #466 |
| [OPT-07](../../03_TASK_CATALOG.md#opt-07) NX CAD 프리뷰 완료를 Optimizer 요청으로 수신한다 | #457 | #451 | — |
| [PRJ-01](../../03_TASK_CATALOG.md#prj-01) 프로젝트 교체 전에 모든 모듈의 모델 연결과 진행 중 요청을 정리한다 | #431, #551 | #246 | — |
| [PRJ-02](../../03_TASK_CATALOG.md#prj-02) Set 개명 시 설정·산출물·참조를 함께 바꾸고 실패를 되돌린다 | #443 | — | — |
| [PRJ-03](../../03_TASK_CATALOG.md#prj-03) 진행 중인 조합 스탬프 PR을 현재 파이프라인에 통합하고 전 구간 검증한다 | #368 | #470, #649 | #650 |
| [PRJ-04](../../03_TASK_CATALOG.md#prj-04) Set 목록의 정본을 파일명 탐색에서 setId 원장으로 옮긴다 | #443 | — | — |
| [PRJ-05](../../03_TASK_CATALOG.md#prj-05) 실행과 산출물의 생성·소비 관계를 파일 대장에 기록한다 | #471 | #470 | — |
| [PRJ-06](../../03_TASK_CATALOG.md#prj-06) Save와 Save As의 성공 판정을 실제 저장 결과와 일치시킨다 | — | — | #432 |
| [PRJ-09](../../03_TASK_CATALOG.md#prj-09) 프로젝트의 Set 복원·개명·참조 조회에 필요한 IO 경계를 명시한다 | #432 | #246 | #434, #468 |
| [PRJ-10](../../03_TASK_CATALOG.md#prj-10) DashManager의 프로세스·설정 접근을 명시적인 소유자로 이관한다 | #434 | #246 | #468 |
| [IO-03](../../03_TASK_CATALOG.md#io-03) DOE·Launcher 설정과 결과 메타데이터의 쓰기 실패를 보존·보고한다 | — | — | #441 |
| [ASY-02](../../03_TASK_CATALOG.md#asy-02) 작업 상태에 따른 진행 표시·입력 차단·취소 표시를 한 방식으로 연결한다 | #462, #463, #543 | #460 | #454, #461, #464 |
| [ASY-03](../../03_TASK_CATALOG.md#asy-03) 데몬 명령 응답에 요청별 시한과 종결 처리를 둔다 | #467 | #465 | — |
| [ASY-04](../../03_TASK_CATALOG.md#asy-04) 외부 프로그램 인코딩·nullable 서비스 경계를 실제 호출 계약에 맞춘다 | #468, #469 | #465 | — |
| [ASY-05](../../03_TASK_CATALOG.md#asy-05) FEM 읽기·변환을 워커로 옮기고 진행 중 창 수명을 분리한다 | #455 | #451 | — |
| [UI-01](../../03_TASK_CATALOG.md#ui-01) 혼합 DPI 이동과 도크 재배치의 재진입·화면 이탈을 막는다 | #447, #450 | #446 | #448, #449 |
| [UI-02](../../03_TASK_CATALOG.md#ui-02) 창 위치·크기·도크 구성을 저장하고 안전하게 복원한다 | #448 | #446 | #447, #449, #450 |
| [UI-03](../../03_TASK_CATALOG.md#ui-03) 내용 크기와 도크 크기 결정을 레이아웃에 맡기고 강제 이벤트 flush를 없앤다 | #449, #455 | #446, #451 | #447, #448, #450, #543 |
| [UI-04](../../03_TASK_CATALOG.md#ui-04) QSettings 위치를 통일하고 최근 프로젝트를 다시 열 수 있게 한다 | — | — | #448 |
| [UI-05](../../03_TASK_CATALOG.md#ui-05) 실패·정보·확인의 통지 규칙과 공통 호출 표면을 맞춘다 | #466 | #465 | — |
| [UI-06](../../03_TASK_CATALOG.md#ui-06) 삭제 가능한 표의 콜백을 현재 항목에 결합한다 | #474, #514 | #473 | — |
| [IO-07](../../03_TASK_CATALOG.md#io-07) 모델의 프로젝트 경로와 참조 조회를 전달된 계면으로 바꾼다 | #432 | #246 | #434 |
| [IO-08](../../03_TASK_CATALOG.md#io-08) 모델의 프로젝트 경로와 참조 조회를 전달된 계면으로 바꾼다 | #432 | #246 | #434 |
| [IO-09](../../03_TASK_CATALOG.md#io-09) 모델의 프로젝트 경로와 참조 조회를 전달된 계면으로 바꾼다 | #432 | #246 | #434 |
| [IO-10](../../03_TASK_CATALOG.md#io-10) 학습 모델 생산과 Runner·Optimizer 소비를 대장에 연결한다 | #471 | #470 | — |
| [IO-11](../../03_TASK_CATALOG.md#io-11) DOE 입력과 예측·최적화 결과의 생산·소비 기록을 완결한다 | #471 | #470 | — |
| [PRJ-11](../../03_TASK_CATALOG.md#prj-11) 포맷과 독립적인 산출물 세대 계약을 만들고 결과 생성에 적용한다 | #650 | #470, #649 | #471, #368, #643 |
