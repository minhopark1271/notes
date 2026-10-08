# 활성 커서와 모듈 데이터 소스 분리 — 매니페스트 도입 · 조사

> 작업 묶음: 프로젝트 매니페스트 도입과 모듈 의존성 관리
> 관련 Issue: #239
> 마스터: [[Project-Manifest-0-Work-Order]] — 착수 순서와 문서 배치
> 기반 문서: [[Project-Store-Design-Wiring-Project-To-Launcher]] (2.3 이 이 작업의 설계 근거)
> 착수 계획: [[Project-Manifest-4-Ticket-Slicing]] — 9좌표가 T3(1·2·3·8)·T4(4·5·6·7·9)로 갈린다

## 요약

| 낱말 | 코드 |
|---|---|
| **모듈** | 위젯(프로세스당 1개) + 모델(Set 마다 1개) 한 쌍 |
| **커서** | `m_activeFilePath` · `m_activeActor` · `activeFilePath()` · `activeContext()` · `setActiveContext()` · `activeContextChanged` |
| **저장소** | `m_contexts` — N개 보관. 커서가 아니고 이 문서의 대상도 아니다 |
| **데이터 소스** (reference model · deck) | `m_loadedFilePath` |
| **결합** | `m_loadedFilePath` 를 써야 할 자리에서 `m_activeFilePath` 를 읽는 것 |

| 갈래 | 좌표 | 무엇이 어긋나나 |
|---|---|---|
| 커서를 직접 읽는다 | 3 · 4 · 5 · 6 · 7 | `mModel->getContext()` 대신 `Registry::activeContext()` — 4 만 `activeFilePath()` |
| 커서 값을 시그널 인자로 받아 모델에 쓴다 | 8 | `activeContextChanged(fp)` → `refreshFromLoadedAnalysis(fp)` |
| 커서에서 데이터를 떠서 모델에 박는다 | 9 | `activeContext()->getPartData()` → `setGeometry()` |
| 진입 시 커서를 1회 읽어 핀한다 | 1 · 2 | 형태는 맞으나 출처가 커서다 (적시만) |

## 개요

**앞단 3모듈이 "내 기준 파일" 을 전역 커서에 묻는 것을 끊고, 모델이 자기 경로를 소유하게 한다.** 이 문서는 **수정부의 위치만** 적는다 — 구현 코드는 담지 않는다.

`DashAnalysisModelContextRegistry` 는 컨텍스트를 `unordered_map` 으로 **N개 들고 있고**(`.h:54`), 단수인 것은 `m_activeFilePath` **커서 하나**다. `activeContext()` 는 `get(m_activeFilePath)` 일 뿐이다(`.cpp:65-67`). 문제는 저장소가 아니라 **소비자가 소유하지 않은 커서를 데이터 결합으로 읽는 것**이다.

가장 뾰족한 증상 — **모델링 트리 체크박스를 껐다 켜면**(`DashMainWindow::onTreeFileCheckChanged` `:2437`·`:2464`) Geometry·Condition 의 데이터 결합이 바뀐다. 순수 표시 동작이 정의에 영향을 준다.

## 배경

### 커서 하나가 두 역할을 겸한다

`m_activeFilePath` 가 동시에 두 가지를 가리킨다.

| 역할 | 소비자 | 단수여야 하나 |
|---|---|---|
| **렌더 대상** — 화면에 그려지는 deck | `updateActor()` · actor 3건 · 시그널 2건 | 예. actor 가 하나다(`.h:57`) |
| **데이터 소스** — 앞단 3모듈이 파싱해 표에 채우는 deck | 9좌표 | 아니오. 모듈마다 달라야 한다 |

렌더 대상이 단수인 것은 설계다. **끌려 들어간 것은 두 번째 역할이고, 이 문서는 그것만 걷어낸다.**

### 커서를 옮기는 4곳은 전부 렌더를 의도한다

| 좌표 | 계기 |
|---|---|
| `MainWindow:2267` | 파일 트리 Load |
| `MainWindow:2437` | 모델링 트리 View 열 토글 — `dat_parent` |
| `MainWindow:2464` | 동 — `dat_part` |
| `OptimizerWidget:1558` | Validation 탭 Preview |

**체크박스를 `getOrLoad` 로 대체할 수 없다.** `controlVisibility()` 는 컨텍스트 객체가 아니라 `m_visualActor` 를 요구하고(`Context.cpp:171-174`), 그 actor 는 `createVisualActor()` 로만 생기며 외부 호출부가 `Registry::updateActor()` 하나다(`Registry.cpp:96`). 거기 닿는 길은 `setActiveContext()` 뿐이다. 자가 생성 경로가 하나 있다 — `setPartColor()` 가 actor 부재 시 스스로 만들고(`Context.cpp:206-209`, 외부 호출부 `MainWindow:379`·`:399`) 렌더러에는 붙이지 않으므로, 결론은 같다.

```
setActiveContext(filePath)
   └─ updateActor(ctx)
        └─ ctx->createVisualActor()   → m_visualActor 생성
             └─ controlVisibility() 가 비로소 동작
```

`getOrLoad` 단독은 actor 를 건드리지 않는다. 치환하면 체크박스가 경고만 남기고 반환한다.

### 결함은 write 가 아니라 read 다

체크박스가 커서를 옮기는 것 자체는 정당하다. 문제는 커서가 옮겨진 순간 **Condition·CAD·Morphing 이 보는 deck 도 함께 바뀐다**는 것이다. Preview 도 같다 — configs 템플릿을 모핑해 `Preview_<열>_<base>_<타임스탬프>.dat` 를 새로 쓰고 그것을 커서에 꽂으므로(`OptimizerWidget:1469-1558`), 앞단 모듈의 기준 파일이 프리뷰 산출물이 된다.

9좌표를 모델 소유로 옮기면 커서는 순수 렌더 커서가 되고, 위 4곳은 전부 정당해진다.

**단서**: 프리뷰는 순회 중 `.vtu` 만 지우고 `.dat`·`.inp` 는 Optimizer 디렉터리에 남긴다(`OptimizerWidget:1505-1513`). 별개 이슈다.

### 모듈은 Set 단위 위젯이 아니다

앞단 3모듈의 위젯은 프로세스당 1개다(`MainWindow:471`·`:474`·`:477`). Set 을 클릭하면 위젯이 생기는 것이 아니라 **모델이 교체된다.**

| 모듈 | 모델 | 바인딩 지점 |
|---|---|---|
| Condition | `DashConditionParameterization` | `MainWindow:1119` |
| CAD | `DashGeometryParameterCAD` | `MainWindow:933` · `:1144` |
| Morphing | `DashGeometryParameter` | `MainWindow:1182` · `:3282` |

기준 파일을 소유할 주체는 위젯이 아니라 모델이고, 핀할 시점은 `setModel()` 말미다. 수정부 A 가 여기다.

## 범위

| | |
|---|---|
| **갖는다** | 커서 API 호출 21건(데이터 8 · 렌더 12 · 죽은 코드 1 — `MainWindow:2604`) + 시그널 payload 결합 1건 중 **데이터 결합 9좌표**(API 8 + payload 1)의 좌표와 근거 |
| **갖는다** | Morphing 모델에 신설할 자리(C-1·C-2) — 형태는 CAD·Condition 과 같다 |
| **갖지 않는다** | 렌더 계열 12건 + 렌더 시그널 2건 — 데이터 결합이 아니다. 2곳에 널 검사만 덧댄다(부속) |
| **갖지 않는다** | 경로 조회 20건 중 18건 — 이미 키를 인자·멤버로 갖고 조회한다. 나머지 2건은 부속 대상 |
| **갖지 않는다** | deck 출처 배선 — 원장을 모듈로 이어보내 인자로 소유시키고 모듈 JSON 에 영속화하는 것은 [[Project-Manifest-3-Module-Deck-Ownership]] 소유. 원장 스키마는 [[Project-Manifest-1-Context-Registry-And-Model-Identity]] |

**이 문서는 좌표와 근거를 갖고 실행은 갖지 않는다.** 9좌표의 작업 배정은 아래 "순서" 절에 있고, 착수 순서는 [[Project-Manifest-0-Work-Order]] 소유다.

**분리만으로도 체감 변화가 있다** — 모듈이 열린 뒤에는 트리 체크박스·Optimizer 프리뷰가 그 모듈의 대상을 못 바꾼다.

---

## 수정부 — 9좌표

### A. 진입 배선 — 2좌표

둘 다 **2인자 `setModel()` 말미**의 같은 형태다. 1인자 오버로드에는 없다 — 구현 시 주의.

| # | 파일 | 함수 | 라인 | 현행 |
|---|---|---|---|---|
| 1 | `view/DashConditionParameterizationWidget.cpp` | `setModel(QAbstractTableModel*, QString)`(`:269`) | `313-315` | `activeFilePath()` → `refreshFromFile()` |
| 2 | `view/DashGeometryParameterCADWidget.cpp` | `setModel(QAbstractTableModel*, QString)`(`:303`) | `345-347` | 동상 |

**형태는 이미 목표에 닿아 있다** — 진입 시 1회 읽어 모델에 핀하고, 그 뒤 커서를 다시 읽지 않는다. 남은 문제는 **그 1회의 출처**다. Set 이 자기 deck 을 갖지 않으므로 커서가 가리키던 아무 deck 에나 붙는다.

확인한 사실 — 현재 Set 의 영속 정의 어디에도 기준 deck 이 없다.

| 자리 | 확인 |
|---|---|
| 모델 멤버 | `m_loadedFilePath` 뿐. deck 을 지정하는 필드 없음 |
| `saveSettings()` | Condition 은 빈 함수다(`.cpp:212-215`) |
| `loadFromJson()` | `DV-Condition` 체크 상태만 읽는다. source·reference 키 없음 |
| `ParameterRow::source` | refresh 때 deck 에서 채우는 런타임 값이고 파일**명**이다(`.cpp:125`·`:174`) |

**출처 교체는 두 걸음이다.** [작업 1]이 전역 `referenceFilePath()` 로 한 번 바꾸고, [[Project-Manifest-3-Module-Deck-Ownership]] 이 그것을 Set 키로 내린다 — 단 좌표 2(CAD)의 두 번째 걸음은 Set 키가 아니라 죽은 전역 읽기 제거다(#366 재스펙 — 문서 3). 형태는 두 번 다 그대로이고, 여기서는 좌표만 적시한다.

**CAD 는 이 좌표가 커서와 닿는 유일한 자리다.** 진입 후에는 커서가 움직여도 CAD 대상이 안 바뀐다 — Condition 과 달리 재바인딩 경로(좌표 8)가 없다.

**모델 쪽은 손대지 않는다.** 두 모델이 이미 `m_loadedFilePath` + `getContext()` + `refreshFromLoadedAnalysis()` 를 갖고 있다.

| 모델 | 멤버 | 조회 | 주입 진입점 | 내부 소비자 |
|---|---|---|---|---|
| `model/DashConditionParameterization` | `.h:82` | `.cpp:109-112` | `.cpp:114-126` | `.cpp:332` · `:352` |
| `model/DashGeometryParameterCAD` | `.h:64` | `.cpp:97-100` | `.cpp:102-115` | — |

호출부는 `view/DashConditionParameterizationWidget.cpp:375` · `view/DashGeometryParameterCADWidget.cpp:416`.

### B. 기존 접근자로 교체 — 1좌표

| # | 파일 | 라인 | 현행 | 처분 |
|---|---|---|---|---|
| 3 | `view/DashConditionParameterizationWidget.cpp` | `222` | `activeContext()` → `getFeConditionShape()` | 적시만. 교체는 [작업 1] 소유 |

**한 줄이다.** 접근자가 이미 있고 nullptr 폴백(`clearFeConditionHighlight()`)도 이미 있다.

**실행은 [작업 1]이 갖는다.** 좌표 8 을 떼면 표는 모델의 `m_loadedFilePath` 를, 하이라이트는 커서를 보게 되어 둘이 갈린다. 현행에서 어긋나지 않는 것은 좌표 8 이 커서 이동마다 모델을 밀기 때문이다. 두 좌표를 같은 묶음에서 처리해야 분열 구간이 생기지 않는다.

### C. Morphing — 5좌표 + 자리 신설

| # | 파일 | 라인 | 현행 |
|---|---|---|---|
| 4 | `viewmodel/DashGeometryParameterPresentationModel.cpp` | `46` | `activeFilePath()` → DV `source` 문자열에 박히고, **같은 함수가 dat 을 configs 로 복사**한다 |
| 5 | `viewmodel/DashGeometryParameterPresentationModel.cpp` | `58` | `activeContext()` → `getPartNames().first()`. `model->getPartName()` 이 빌 때만 도는 **폴백** |
| 6 | `view/overlay/DashMorphingSettings.cpp` | `562` | `activeContext()` → `getSetIndicesByName()` |
| 7 | `view/overlay/DashMorphingSettings.cpp` | `636` | `activeContext()` → `getNodeSetNames()` |
| 9 | `view/DashMainWindow.cpp` | `3271` | `activeContext()` → `getPartData()` → `newModel->setGeometry()`(`:3279`) |

**좌표 9 가 이 절의 본체다.** `onStartMorphingClicked` 은 사용자 액션 1회이므로 **이미 진입 1회 읽기**다 — 좌표 1·2 와 같은 형태다. 다른 점은 읽은 경로를 남기지 않고 `vtkUnstructuredGrid` 만 모델에 박는다는 것이고(`:3279`), 그래서 나중에 도는 좌표 4·5·6·7 이 커서로 되돌아간다.

처분은 결합 제거가 아니라 **이미 하는 1회 읽기에 경로 핀을 더하는 것**이다. 그러면 좌표 1·2·9 가 같은 형태로 수렴하고, [작업 3]-3 이 좌표 1·9 의 출처를 교체한다(좌표 2 는 죽은 읽기 제거 — #366).

`selectedPartName` 은 모델링 트리 선택에서 오므로(`:3221-3227`) 파트와 deck 의 짝이 여기서 확정된다.

**좌표 4 는 디스크에 남는다.** DV `source` 문자열과 configs 로 복사되는 dat 이 이 경로로 결정되므로, 검증을 UI 확인만으로 끝내면 안 된다.

#### C-1. 모델 자리 신설

| 파일 | 무엇을 |
|---|---|
| `model/DashGeometryParameter.h` · `.cpp` | `m_loadedFilePath` + `getContext()` 를 **CAD·Condition 과 같은 형태로** 신설 |
| 주입 진입점 | 좌표 9 (`MainWindow:3271-3280`). Morphing 모델의 데이터 주입 경로는 **여기 하나뿐**이다 — `setGeometry`·`setPartName` 호출부 전수 확인 |

**죽은 멤버가 하나 있다** — `m_fileName`(`.h:50`)은 인라인 setter·getter 만 있고(`:23`·`:32`) `.cpp` 대입 0건, 전 레포 호출부 0건이다. 처분은 **삭제**로 확정됐다 — [[Project-Manifest-3-Module-Deck-Ownership]] 부속 결정, 실행은 문서 4 T14.

#### C-2. 오버레이 호스트 주입

`DashMorphingSettings` 는 인스턴스별 위젯이 아니다.

| 자리 | 사실 |
|---|---|
| `view/DashMainWindow.cpp:1778` | `new DashMorphingSettings(this)` — **프로세스당 1개**. `setupMorphingBar()`(`:1769`) 안 |
| `view/DashMainWindow.cpp:1780` | `DashManager::SetMorphingSettingsWidget()` 로 전역 등록 |
| `view/overlay/DashMorphingSettings.h:33` | 생성자가 `QWidget* parent` 만 받는다 — **호스트를 모른다** |

**주입 경로는 `onStartMorphingClicked` 이다.** 그 함수 안에서 `m_morphingSettings` 와 `newModel` 이 동시에 손에 있고, 같은 함수가 `setupMorphingBar()` 를 호출해 오버레이를 만든다(`:3288` 부근). 그 뒤에 모델을 넘긴다.

남는 작업은 수신 자리 하나 — `DashMorphingSettings` 에 `setModel(DashGeometryParameter*)` 를 신설한다. `DashGeometryParameterWidget` 경유는 불필요하다.

### D. 시그널 payload 경유 — 1좌표

| # | 파일 | 라인 | 현행 | 처분 |
|---|---|---|---|---|
| 8 | `view/DashMainWindow.cpp` | `433-442` | `activeContextChanged` 핸들러가 `ConditionWidget::refreshFromFile(fp)` | 적시만. 제거는 [작업 1] 소유 |

**Condition 을 커서에서 떼는 것은 이 좌표다.** 핸들러가 `mModel->refreshFromLoadedAnalysis(fp)` 로(`ConditionWidget:375`) 모델의 `m_loadedFilePath` 를 덮어쓰므로, 진입 시 핀을 해도 커서가 움직일 때마다 다시 밀린다. 좌표 1 은 이미 목표 형태이므로, **Condition 의 재바인딩 결함은 여기 하나다.** 남는 좌표 3 은 재바인딩이 아니라 하이라이트의 읽기 출처이고, 이 좌표를 떼는 순간 짝이 된다.

**실행은 [작업 1]이 갖는다.** 커서가 두 층으로 갈리면 이 핸들러는 렌더 시그널의 구독자가 되고, Condition 위젯이 그것을 구독할 이유가 사라진다. 좌표 3 과 한 묶음이라 같은 작업에서 닫힌다 — 순서와 제거에 딸리는 동작 변화(커서가 빈 상태의 복구 경로 소멸)는 [[Project-Manifest-0-Work-Order]] 가 적는다.

이 결합은 `activeContext()`·`activeFilePath()` 호출이 아니라 시그널 payload(`const QString& fp`)를 탄다. **커서 API 를 훑는 방식으로는 잡히지 않으므로, 좌표 전수는 싱크 쪽에서 확정한다.**

```
m_loadedFilePath 대입 2곳  (CAD:112 · Condition:126, 둘 다 refreshFromLoadedAnalysis 내부)
   └─ refreshFromLoadedAnalysis 호출부 2곳  (ConditionWidget:375 · CADWidget:416)
        └─ refreshFromFile 호출부 3곳
             ├─ ConditionWidget:315   → 좌표 1
             ├─ CADWidget:347         → 좌표 2
             └─ MainWindow:438        → 좌표 8
```

Condition·CAD 의 기준 파일을 바꿀 경로는 이 3개가 전부다. Morphing 은 `setGeometry`·`setPartName` 호출부가 `MainWindow:3279-3280` 하나뿐이다(좌표 9). 레지스트리 시그널은 2종·구독 4곳이 전부다.

---

## 부속 — [작업 1] 에서 함께 처리

9좌표와 별개이나 같은 라인·같은 불변식을 건드리므로 함께 처리하는 편이 낫다.

### `get` → `getOrLoad` 2좌표

| 파일 | 라인 | 현행 |
|---|---|---|
| `model/DashConditionParameterization.cpp` | `111` | `getContext()` 가 `get(m_loadedFilePath)` |
| `model/DashGeometryParameterCAD.cpp` | `99` | 동상 |

**근거.** 캐시 히트 경로가 `get` 과 동일하고(둘 다 `canonicalFilePath()` + mutex + find — `.cpp:18` vs `:24`), 미스에서 자가 복구한다. 현행에서 `get` 이 안전한 것은 "`m_loadedFilePath` 대입자가 곧 로더" 라는 불변식 덕인데, **A 가 그 대입 경로를 늘리면 불변식이 깨질 수 있다.**

`get` 의 nullptr 이 실제로 어떻게 소비되는지도 근거가 된다 — `DashConditionParameterization.cpp:352` `commitEntryValue` 가 **"Analysis model is not loaded" 로 사용자 편집을 거절**한다. 로드를 시도했어야 맞는 자리다.

**단서**: 미스 시 동기 파싱이 그 자리에서 돈다. 진입 시 1회 워밍업(A 가 이미 하는 일)을 유지해 미스가 UI 상호작용 도중에 터지지 않게 한다.

### 유지 2곳의 nullptr 역참조

`MainWindow:2439` · `:2467` 이 `activeContext()` 반환을 검사 없이 역참조한다 — 역참조 지점은 각각 자식 루프 안 `:2451`, 바로 다음 줄 `:2468`.

`setActiveContext` 는 `getOrLoad` 실패 시 조용히 반환한다(`Registry.cpp:52`). 그러면 커서가 이전 deck 에 남고, `activeContext()` 가 **엉뚱한 deck** 을 돌려주며, 거기에 새 deck 의 `partName` 으로 `controlVisibility` 가 걸린다. 활성 컨텍스트가 한 번도 없었으면 nullptr 역참조다.

**처분**: 널 검사 + early return. 커서 유지 방침과 충돌하지 않는다 — 호출 자체는 그대로 둔다.

---

## 데이터 결합이 아닌 곳 — 커서 계열 12 + 시그널 2

명시해 두지 않으면 "커서를 없앤다" 로 읽힌다. **커서는 남는다.**

**"유지" 는 데이터 결합 제거 대상이 아니라는 뜻이다.** 아래 12건은 전부 [작업 1]에서 `displayed*` 로 개명되고, `setActiveContext` 4곳 중 Load 하나는 `setReferenceModel` 로, 나머지 셋은 `setDisplayedContext` 로 갈린다. 읽는 대상이 렌더 커서라는 것만 안 바뀐다.

| 계열 | 건 | 좌표 |
|---|---:|---|
| `setActiveContext()` | 4 | `MainWindow:2267`(파일 Load) · `:2437` · `:2464`(체크박스 토글) · `OptimizerWidget:1558`(렌더 프리뷰) |
| `activeContext()` | 3 | `MainWindow:2439` · `:2467` · `OptimizerWidget:1559` |
| `activeFilePath()` | 2 | `MainWindow:2436` · `:2463` |
| `activeActor()` | 3 | `MainWindow:2211` · `:3310` · `OptimizerWidget:1536` |
| 시그널 connect | 2 | `MainWindow:432`(`activeActorUpdated` → Redraw) · `ModelingTreeWidget:139`(트리에 파일 노드 추가) |

### 시그널 구독 4건의 처분

콜백 본문 기준으로 절반이 데이터 결합이다.

| 좌표 | 콜백이 하는 일 | 처분 |
|---|---|---|
| `MainWindow:432` | `Redraw()` | 렌더 시그널로 유지 |
| `ModelingTreeWidget:139` | `onActiveContextChanged` — 트리에 파일 노드 추가(`:472-489`) | 렌더 시그널로 유지 |
| `MainWindow:433` | `logMessage` + `refreshFromFile(fp)` | **좌표 8** — 데이터 결합만 제거하고 로그는 렌더 시그널로 유지 |
| `MorphingSettings:90` | `loadNodeSetList()` 하나뿐(`:92`), 그 본체가 좌표 7(`:628-651`) | **시그널 교체** — [작업 1]에서 `referenceModelChanged` 구독으로 옮긴다. [작업 3]에서 모델 주입이 오면 그때 구독이 사라진다 |

**`MorphingSettings:90` 은 소멸이 아니라 교체다.** 좌표 7 이 `referenceContext()` 로 옮겨져도 콜백 본문은 남고, **기준모델이 바뀌면 node set 목록이 갱신돼야** 하므로 구독이 필요하다. 구독이 비는 것은 [작업 3]에서 그 위젯이 Set 의 모델을 주입받은 뒤다.

**`setActiveContext` 를 남기는 근거가 코드에 있다.** 그 함수는 커서만 옮기지 않고 `updateActor()` 를 부른다 — 이전 actor 제거 · 새 actor 추가 · **카메라 리셋**(`.cpp:50-63` · `:77-107`). `getOrLoad` 단독은 렌더를 건드리지 않는다. 데이터 결합을 떼고 나면 체크박스 토글은 **렌더 대상만 바꾸는 정당한 호출**이 된다.

### 대상이 아닌 것 — 경로 조회 18

조회는 20건(`getOrLoad` 15 + `get` 5)이고, 그중 2건은 부속의 수정 대상이다.

| 갈래 | 건 | 좌표 |
|---|---:|---|
| 부속 대상 (`get` → `getOrLoad`) | 2 | `ConditionParameterization:111` · `GeometryParameterCAD:99` |
| 대상 아님 | 18 | 아래 |

`DashManager:1028` · `DashOptimizer:1400` · `DashModelRunner:1975` · `MorphingUtils:312`·`360`·`375` · `ReferenceFileWidget:617`·`637`·`784`·`869` · `ModelRunnerWidget:1464`·`1973` · `ModelingTreeWidget:357`·`412` · `MainWindow:376`·`396` · `GeometryParameterCAD:106` · `ConditionParameterization:118`

이미 키를 인자·멤버로 갖고 조회한다. **손댈 것이 없다.**

### 죽은 코드 — [작업 1]-6 에서 제거

호출 0건. 목적은 아니나 [작업 1]이 같은 파일을 건드리는 유일한 기회라 함께 지운다.

| 종류 | 좌표 |
|---|---|
| include | `DashMorphingDoeExecutor.cpp:4` · `DashAnalysisLauncher.cpp:7-8` · `DashGeometryParameterWidget.cpp:11-12` |
| 함수 | `DashMainWindow::updateCheckedPartsGeometry`(`:2598-`) — 유일 호출부가 `:2459` 에 주석 처리 |
| 함수 | `DashModelingTreeWidget::addFileToTree`(`:493`) — `addFileToTreeWithStructure` 래퍼, 외부 호출 0 |
| 함수 | `DashModelingTreeWidget::buildTreeRecursive`(`:497`) · `parseVtmFile`(`:502`) — 본문이 주석뿐인 빈 구현 |
| 오버로드 | `DashGeometryParameterCADWidget::setModel(DashGeometryParameterCAD*)`(`:351`) — 호출부 0건. MainWindow 는 전부 2인자를 부른다 |
| 인자 | 2인자 `setModel` 의 `projectPath` — `Q_UNUSED`(`ConditionWidget:271`) |

`DashModelingTreeWidget::populate`(`:369`)도 현재 호출부가 0이나 [작업 2]-3 에서 인자를 활성 기준모델로 바꿔 되살리므로 이 표에 넣지 않는다.

`updateCheckedPartsGeometry` 는 살릴 경우 그 자체가 결함이다. 인자로 `filePath` 를 받아 놓고 컨텍스트는 `activeContext()`(`:2604`)로 얻어, 커서와 인자가 다르면 **엉뚱한 deck 의 파트를 읽는다.** 죽어 있어 실해는 없다.

**`onActiveContextChanged` 의 파일 존재 판정이 갈라져 있다.** `:477` 은 `findItems(파일명, MatchRecursive)` 로 이름만 보고, `:485` 은 `item->data(UserRole) == filePath` 로 경로를 본다. 이름이 같고 경로가 다른 항목이 트리에 있으면 `:479` 의 `items.isEmpty()` 가 false 라 else 로 빠지고, `:485` 에서 경로가 안 맞아 파일이 트리에 추가되지 않는다. `addFileToTreeWithStructure:233-237` 은 이름과 경로 쌍으로 판정하므로 그쪽에 위임하면 사라진다. 현행 발현 조건은 좁다 — 커서에 꽂히는 프리뷰 산출물명이 타임스탬프로 유일하다.

---

## 순서

**이 문서의 9좌표가 두 작업에 갈려 들어간다.** 배정은 [[Project-Manifest-0-Work-Order]] 소유이고, 여기서는 좌표별 행선지만 적는다.

```
[작업 1] 커서 분리 — 9 좌표 중 8 개가 여기서 닫힌다
   │   1. 좌표 3·8 — Condition 을 커서에서 뗀다 (한 묶음)
   │   2. 좌표 1·2 — 진입 1 회 읽기의 출처를 referenceAbsolutePath() 로
   │      (QFile::exists·refreshFromFile 이 절대경로를 요구 — 문서 4 T3)
   │   3. 좌표 4~7·9 — Morphing 소비부를 referenceContext() 로
   │      (좌표 4 만 경로라 referenceAbsolutePath() — 문서 4 T4)
   │      모델 자리 없이 전역 기준모델을 읽는 데까지만 간다
   │      MorphingSettings:90 구독을 referenceModelChanged 로 옮긴다
   │   4. 부속 — get→getOrLoad 2 좌표 · nullptr 역참조 2 곳
   │   5. 개명 — 커서 분리가 곧 개명이다 (아래 "개명" 절)
   │   6. 표시 — Mesh View 도크 제목줄에 현재 렌더 파일명 (마스터 D7)
   │      기준모델은 Load 버튼의 활성 상태로 표시한다
   │   7. 죽은 코드 제거 — 아래 "죽은 코드" 표
   ▼

[작업 3] Set 별 기준모델 키 — Morphing 모델 자리 신설
   │   1. C-1 — DashGeometryParameter 에 Condition·CAD 와 같은 형태로 신설
   │      MainWindow:3271 의 1 회 읽기에 경로 핀을 더한다 · m_fileName 삭제(문서 3 확정)
   │   2. C-2 — DashMorphingSettings::setModel 신설 + onStartMorphingClicked 에서 주입
   │   3. 좌표 1·9 의 출처를 전역 reference 에서 Set 키로 내린다
   │      좌표 2(CAD)는 죽은 전역 읽기 제거로 끝 (#366 재스펙 — 문서 3)
   ▼

[결과] 커서가 순수 렌더 커서로 남는다
       Set 은 각자의 기준모델 키를 갖고, 전역 커서를 읽지 않는다
```

**Condition 의 분리는 [작업 1]-1 에서 끝난다.** 좌표 8·3 을 떼면 Condition 이 표와 하이라이트 양쪽에서 커서와 떨어지고, CAD 는 이미 떨어져 있다.

**Morphing 은 두 걸음이다.** [작업 1]이 5좌표를 전역 기준모델로 돌려 커서에서 떼고, [작업 3]이 모델 자리를 만들어 Set 별로 내린다. 중간 구간에서는 Morphing Set 두 개가 같은 전역 기준을 공유하는데, 현행과 같으므로 회귀가 아니다.

## 개명 — [작업 1] 에 흡수

`active` 는 **무엇에 대해 active 인지**를 말하지 않는다. 그 빈칸이 9개 소비자가 각자 다른 의미를 붙일 여지를 줬다. 커서 2층 분리가 그 빈칸을 두 이름으로 채우므로, 분리와 개명이 같은 작업이다.

| 현행 | 렌더 층 | 기준모델 층 |
|---|---|---|
| `m_activeFilePath` | `m_displayedFilePath` | `m_referenceFilePath` |
| `m_activeActor` | `m_displayedActor` | — actor 는 렌더 전용이다 |
| `setActiveContext(path)` | `setDisplayedContext(path)` | `setReferenceModel(path)` |
| `activeContext()` · `activeFilePath()` · `activeActor()` | `displayedContext()` · `displayedFilePath()` · `displayedActor()` | `referenceContext()` · `referenceFilePath()` |
| `activeContextChanged` · `activeActorUpdated` | `displayedContextChanged` · `displayedActorUpdated` | `referenceModelChanged` |

**렌더 층은 `displayed` 로 확정했다**([[Project-Manifest-0-Work-Order]] 결정 D1). `render*` 는 그래픽스에서 render target 이 프레임버퍼를 뜻해 충돌하고, `visible*` 은 `controlVisibility()` 의 파트 단위 가시성과 겹쳐 배제했다. 세터는 `setReferenceModel` 과 짝을 맞춰 `setDisplayedContext` 로 둔다.

**개명이 [작업 1] 안에 있어야 하는 이유.** 데이터 소비자가 아직 커서에 붙어 있는 동안 이름을 바꾸면 이름이 거짓말을 한다. [작업 1]이 9좌표의 라우팅과 개명을 같은 작업에서 하므로 이름이 붙는 시점에 이미 참이다. 대상은 커서 API 21건 + 시그널 2건이고, LSP rename 으로 기계적이다.

## 검증

| 단계 | 확인 |
|---|---|
| [작업 1] | Condition Set 을 연 뒤 **모델링 트리 체크박스를 토글해도** 표의 대상 deck 이 안 바뀐다 (좌표 8) |
| [작업 1] | 같은 조작 뒤 조건 행을 클릭하면 3D 하이라이트가 표와 같은 deck 에 걸린다 (좌표 3) |
| [작업 1] | Optimizer 프리뷰(`OptimizerWidget:1558`)를 돌려도 Condition·CAD·Morphing 대상이 유지된다 |
| [작업 1] | CAD 는 **현행에서 이미 통과한다**(커서 접촉이 좌표 2 하나). 회귀만 확인 |
| [작업 3] | Morphing Set 두 개를 번갈아 열어도 각자의 deck 을 유지한다 (동시 표시는 구조상 불가 — 공유 오버레이 1개) |
| [작업 3] | DV `source` 문자열과 configs 로 복사된 dat 이 그 Set 의 deck 을 가리킨다 (좌표 4) |
| 전 단계 | 렌더·모델링 트리·카메라 동작이 현행과 동일 (커서 유지분 회귀 없음) |

## 검증 한계

| 항목 | 근거 강도 | 비고 |
|---|---|---|
| 커서 API 21건 전수 | **강** | `c989257` API 별 grep |
| 경로 조회 20건(`getOrLoad` 15 + `get` 5) | **강** | `c989257` 집계 |
| 좌표 9 — `MainWindow:3271` | **강** | `onStartMorphingClicked` 본문 · `setGeometry`·`setPartName` 호출부 전수 |
| 싱크 쪽 봉쇄 (결합 경로 전수) | **강** | `m_loadedFilePath` 대입 2 → `refreshFromLoadedAnalysis` 2 → `refreshFromFile` 3. Morphing 싱크 1 |
| `updateCheckedPartsGeometry` 죽음 | **강** | 유일 호출부 `:2459` 주석 처리 |
| Set 에 deck 정의가 없음 | **강** | 모델 헤더 · `saveSettings` · `loadFromJson` · `ParameterRow::source` 확인 |
| CAD 가 이미 분리돼 있음 | **강** | CAD 의 커서 접촉은 좌표 2 하나, `refreshFromFile` 호출부 1곳 |
| `setModel` 오버로드 2종 | **강** | 정의 4개 · MainWindow 호출부 8곳 인자 수 확인 |
| 좌표 8 — 시그널 payload 경유 결합 | **강** | `MainWindow:433-442` → `ConditionWidget:375` → `refreshFromLoadedAnalysis` 본문 확인 |
| 좌표 3·8 의 실행 소유 | — | 판단이다. 같은 한 줄이고 8 을 떼는 순간 분열이 생기므로 한 묶음이라야 한다. 커서 분리와 같은 작업에 뒀다 |
| 좌표 8 제거가 좌표 3 과 분열을 만듦 | **강** | `ConditionWidget:222` 가 `activeContext()`, 표는 모델의 `m_loadedFilePath` |
| 시그널 4건의 콜백 본문 | **강** | `MainWindow:432`·`:433` · `ModelingTreeWidget:472-489` · `MorphingSettings:92`·`:628-651` |
| 레지스트리 소유·`updateActor` 부작용 | **강** | `.h:54` · `.cpp:18`·`:24`·`:50-63`·`:65-67`·`:77-107` 본문 확인 |
| `controlVisibility` 의 actor 의존 | **강** | `Context.cpp:171-174` 요구 · `createVisualActor` 외부 호출부 1곳(`Registry.cpp:96`) · `setPartColor` 자가 생성(`:206-209`)은 렌더러 미부착 확인 |
| 앞단 3위젯 단일 인스턴스·모델 교체 | **강** | `new` 각 1곳 · `setModel` 호출부 전수 |
| 유지 2곳 nullptr 역참조 | **강** | 정적 확인. 실패 분기 실제 재현은 안 했다 |
| Condition·CAD 의 기존 배선 3종 | **강** | 멤버·접근자·진입점 정의와 호출부 확인 |
| `m_fileName` 호출부 0곳 | **강** | 헤더 인라인 둘뿐, `.cpp` 대입 0, 전 레포 호출부 0 |
| `DashMorphingSettings` 단일 인스턴스 | **강** | `new` 1곳(`MainWindow:1778`) · 전역 등록(`:1780`) · 생성자 인자 `parent` 뿐 |
| 좌표의 작업 배정과 검증 항목 | **중** | 제안이다. 각 확인이 현행 UI 로 실제 수행 가능한지는 재현하지 않았다 |
| 개명의 낱말 선택 | — | 결정이다 — 마스터 D1. 실측이 아니다 |
| C-2 주입 경로 | **중** | 주입 지점은 확정. `setupMorphingBar()` 와의 호출 순서는 정적으로만 봤다 |
| 빌드·실행 | **없음** | 정적 근거만 |

## 관련 문서

[[Project-Manifest-1-Context-Registry-And-Model-Identity]] — 같은 레지스트리를 `Instance()` 호출 지점 단위로 다시 세고(34지점), **열기가 레지스트리를 채우지 않는다**는 것과 `AnalysisModelIdentity.json` 은 읽히기는 하나 읽은 값이 결과를 못 바꾼다는 것을 잰다. 이 문서가 범위 밖으로 둔 경로 조회 18건의 출처가 거기서 다뤄진다.

**대조 시 주의.** 34지점 집계와 이 문서의 41건(커서 21 + 조회 20)은 세는 단위가 다르다 — 한 `Instance()` 줄이 여러 API 호출을 받는다. 좌표 기준 커밋은 둘 다 `c989257` 이다.
