# RW 문서 게이트 — actor 유지, 상호작용 코루틴화, 불변 공유 · 가변 유일

> **제안 문서 (planned, 현재 동작 아님).** `proposal-parameterized-model` 브랜치의 설계 제안이며
> `docs/scratchpad/` 에 있으므로 `docs/index.md` 가 색인하지 않는다. 구현이 dev 에 들어가면
> `docs/rw-document-gate.md` 로 옮기고 아래 "현재" 절을 지운 뒤 인덱스 「공통 문서」에 등록한다.

## Responsibility
- 이 문서가 소유하는 것: reader-writer 모듈과 GUI 사이 경계의 계약 — 인스턴스 소유·스레드,
  게이트를 넘는 값의 복사 규칙, 불변 문서와 가변 문서의 구분과 세대, 동기/비동기 구분, 배치
  격리(clone), 소비자 호출 방식
- 이 문서가 소유하지 않는 것: 모핑 승격 모델과 레인·취소·스레드 예산
  (→ [모핑 승격 모델과 요청 서비스](../morphing-request-service.md)), 기준모델 원장과 Set 별 pin,
  reader-writer SDK 의 payload·edit 계약(외부 저장소 `DashOpti_ReaderWriter` 의 `IRWModule.hpp`)

## Must-Know Rules
- `IRWModule` 인스턴스는 `DashRwActor` 만 소유하고 actor 스레드에서만 호출된다. actor 는 GUI 와
  다른 자기 `QThread` 를 가진다. 다른 스레드에서 모듈 포인터에 닿는 코드는 assert 로 죽는다.
- 게이트를 넘는 격자는 **양방향 DeepCopy** 다. `get_data` 결과(Mesh · `Set::mapped_mesh` ·
  FECondition 조각)는 actor 스레드에서 복사된 GUI 소유 값으로 돌아오고, `edit_mesh` 입력은 actor
  쪽 사본으로 들어간다. GUI 쪽 어떤 포인터도 모듈 메모리를 가리키지 않는다.
- 모듈 호출은 전부 `QCoro::Task<dash::core::Result<T>>` 다. 호출 스레드를 막는 경로 —
  `BlockingQueuedConnection` · `processEvents` · `waitForFinished` — 는 RW 층에 존재하지 않는다.
- 문서는 두 타입이다. `DashRwDocument` 는 **불변**이며 복사 가능하고 공유된다. `DashRwMutableDocument`
  는 **가변**이며 move-only 로 유일하다. 가변은 `seal() &&` 로 불변이 되고(소비), 불변에서 가변을 얻는
  길은 `clone()` 하나다. 불변을 제자리에서 바꾸는 연산은 존재하지 않는다.
- `DashRwDocument` 의 모든 읽기는 동기이고 GUI 소유 사본만 읽는다. 사본은 불변이라 어느 스레드에서
  읽어도 안전하다. 없는 값은 빈 값으로 답하며, 채우려면 `fetch*()` Task 가 새 불변 문서를 돌려준다.
- 편집은 세대를 만든다. 레지스트리는 경로별 **현재 세대 하나**만 들고 `documentChanged` 를 낸다. 옛 세대는
  마지막 핸들과 함께 닫힌다. 옛 핸들을 든 소비자는 옛 세대를 일관되게 본다 — 최신을 보려면 다시 묻는다.
- 배치(DOE · ModelRunner · Optimizer)는 `clone()` 으로 얻은 `DashRwMutableDocument` 에만 쓴다. 표시
  문서는 불변이라 닿을 수 없다. 원복 코드는 없다. DV 주입 하나가 실패하면 그 샘플은 실패다.
- `clone()` 은 배치당 1회, GUI 편집 세대당 1회다. 복제 실패(`LogicError`)는 그 배치·편집의 실패이고
  현재 세대는 바뀌지 않는다.
- 실패는 `dash::core::Result<T>` 의 `ErrorState` 로만 돌아온다. 예외를 삼켜 빈 결과를 돌려주는
  경로는 없다.
- `co_await` 뒤에는 `QPointer` 로 자기 수명을 확인하고, 람다 코루틴은 쓰지 않는다 — 호출자 계약은
  [모핑 문서 8절](../morphing-request-service.md#8-호출자-계약)이 소유하며 RW 도 같은 규칙이다.

## Related Docs
- [문서 인덱스](../index.md)
- [모핑 승격 모델과 요청 서비스](../morphing-request-service.md) — 같은 코루틴 게이트 모양의 선례이며 배치가
  타게 되는 서비스. 이 제안이 구현되면 1절의 "RW actor 는 호출자를 `BlockingQueuedConnection` 으로 막는다"
  문장과 7절 "미이관 경로" 가 삭제된다
- 이슈 #429 · #324 · #521 · #427 · #281 — 아래 2절

---

## 1. 의도

**표시 중인 문서와 실행이 쓰는 문서를 타입으로 분리하고, GUI 가 모듈 메모리를 들고 있지 않게 하며, RW
호출이 GUI 스레드를 막지 않게 한다.** 셋은 한 결정에서 나온다 — 게이트에서 격자를 복사하면 actor 가 GUI
스레드를 떠날 수 있고, 떠나면 호출은 비동기여야 하며, 불변 문서와 유일한 가변 문서로 나누면 "실행이
화면을 바꾼다 · 화면이 실행을 바꾼다" 두 방향이 컴파일 타임에 막힌다.

이 문서는 parameterized model(RW · Morphing · FE Condition 병합)의 선행 단계다. 병합 뒤
`materialize(values)` 가 "clone → morph → `edit_mesh` → `edit_data` × N → `export`" 를 한 코루틴
안에서 잇는데, 그 사슬의 RW 절반이 여기서 정해진다. 불변 문서의 part 격자는 스레드를 넘을 수 있으므로
모핑 상태 타입이 문서를 값으로 드는 것도 여기서 가능해진다.

### 현재 (dev, 2026-09-22)

| 항목 | 현재 |
|---|---|
| actor 스레드 | GUI 스레드. `invokeOnActor` 는 same-thread 직접 호출, cross-thread 는 `BlockingQueuedConnection` |
| 격자 소유 | 모듈 소유 격자의 별칭을 GUI 가 그대로 든다 — `getPartData()` raw 포인터가 view 6곳으로, `buildPolySurfaceMultiBlock` 이 그 격자를 `vtkGeometryFilter` 에, 조건 형상이 `mapped_mesh()` 를 별칭 |
| 호출 | 전부 동기. `QAbstractTableModel::data()` 안에서도 모듈 왕복(편집 스키마·detail) |
| 가변성 | 세션 하나가 읽기와 편집을 겸한다. 조건 값 편집은 표시 중인 세션을 제자리에서 바꾼다 |
| 배치 | 표시 중인 세션을 `edit_data`/`edit_mesh` 로 변이하고 export 뒤 원복. 원복 실패는 WARN 만 남고 화면이 오염된다 |
| 문서 하나의 이름 | `DashRwClient` · `DashRwSession` · `DashAnalysisModelContext` 셋 |

## 2. 이슈

### 닫힘

| 이슈 | 판정 | 근거 |
|---|---|---|
| #429 해석 결과 읽기 캐시의 화면·실행 공유 해소 | **close** | 실행 경로의 `registry.getOrLoad` 소비 6곳이 `clone()` 또는 함수 스코프 임시 문서로 바뀐다. 실행 산출물이 레지스트리에 누적되는 경로가 사라진다 |
| #324 `catch(...)` 가 사유 없이 빈 결과 | **close** | 게이트가 `Result<T>` 만 돌려주고, 세션의 예외 삼킴 두 곳은 불변 사본 읽기로 대체되어 모듈 호출이 아니다 |
| #521 deck 적재 시 가시성 적용이 actor 생성보다 먼저 | **close** | `getOrLoad` 가 Task 가 되면서 `loadDatFileAndChildren` 이 코루틴 슬롯이 되고, 가시성 적용은 `co_await` 뒤 — 문서와 렌더 표현이 모두 만들어진 뒤 — 로 옮겨진다. 로드 경로를 다시 쓰는 커밋에서 같이 끝난다 |
| #427 DOE 배치·Generate·프리뷰 실행을 화면 편집 상태에서 격리 | **RW 축 항목 close** | "격리 완결 후 원복 코드 삭제" 항목이 여기서 끝난다. 핸들 축(#428 · #430)과 렌더러 액터 축(#316 · #318 · #319)은 남으므로 부모는 열려 있다 |
| #281 단건 모핑 워커화 | **close 가능** | B2(전용 세션)는 `clone()`, B1(값 경계)은 불변 문서 격자와 `DashVolumeMeshSet`, C·D·E(배치·Optimizer·ModelRunner 진입점의 비동기화)는 세 경로가 같은 실행기를 통해 Background 레인을 타는 것으로 충족된다. 이슈가 전제한 `WorkerJob` · `morphingSerialPool` · `MorphingGate` 는 #292 롤백으로 사라졌고 #408 의 서비스가 그 자리다. 잔여 — `DashOptimizerWidget` 의 `processEvents` 2곳은 #457, 죽은 진입점 `MorphFromDoeDirectory` 삭제는 이 커밋에서 함께 한다. 프리뷰 축은 이슈 스스로 범위 밖이다 |

### 함께 잡으면 좋은 것

| 이슈 | 이유 | 범위 |
|---|---|---|
| #534 part 캐시의 instance(world)·part(local) 혼입 | 스냅샷 적재 루프를 다시 쓰는 커밋이다. 불변 문서에는 렌더용 `partData(name)`(instance 포함), 가변 문서에는 `MeshEditable` part 만 받는 `updateMeshPoints` — 이슈의 선택지 2 가 타입 구분에 그대로 얹힌다 | 결정 1건 + 항등 아닌 instance transform 덱으로 확인. 미루면 `partDataUuids` 를 그대로 옮겨야 한다 |
| #500 Target Component 와 모핑 소스 불일치 | 이슈의 선택지 1(정합성 검증)이 "폴백을 실패로 승격" 과 같은 커밋 성격이다. `partNames.first()` 폴백 삭제로 증상은 이미 더 일찍 드러난다 | 배치 시작 전 Target part 와 GP 세트 part 이름 비교 → 다르면 배치 시작 실패. 선택지 2(모핑 소스 통일)는 #281 B1 의 `DashVolumeMeshSet` 몫이라 여기서 하지 않는다 |

접점만 있는 이슈. #525(핸들 복원이 interaction 에 의존)는 핸들 축이고, #451 은 RW 호출의 비동기화가
서브 이슈들의 워커 이관과 정합한다는 관계만 있다.

## 3. 설계 변경점

1. `DashRwActor` 는 자기 `QThread` 에서 살고 모든 `IRWModule` 을 소유한다. 메시지는 큐로만 들어간다.
   가변/불변은 GUI 층 타입 구분이고 actor 는 인스턴스를 id 로만 든다.
2. `DashRwClient` → `DashRwDocumentHandle`. actor 안의 인스턴스 하나를 가리키는 핸들이며 모든 메서드가
   `Task<Result<T>>` 다. 두 문서 타입이 이것을 감싼다. 위젯은 들지 않는다.
3. 게이트 복사 — 반환 payload 의 격자는 actor 스레드에서 DeepCopy 한 뒤 넘기고, `editMesh` 입력도
   복사해 넘긴다. `DashRwDataPayload` 는 GUI 소유 값이 된다.
4. `DashRwSession` → **`DashRwDocument`(불변 · 공유) 와 `DashRwMutableDocument`(가변 · 유일)**.
   불변 문서 = 핸들 + GUI 소유 불변 사본(part 격자 · uuid 맵 · 조건 엔트리 · 편집 스키마 · 조건 형상).
   가변 문서 = 핸들 + clone 시점에 복사한 uuid 맵. 사본 갱신 규칙은 없다 — 편집은 새 세대다.
5. 불변 문서의 읽기는 전부 동기·선적재다: 심볼 트리 · part 격자 · 조건 이름·uuid·caps · 조건 엔트리 ·
   편집 스키마. 조건 형상만 조건당 `get_data` 가 무거워 `fetchFeConditionShape` 로 미루며, 그 결과는
   형상이 채워진 **새 불변 문서**다(같은 인스턴스, 사본만 추가).
6. 세대 — `clone() → edit → seal()` 이 새 `DashRwDocument` 를 만들고, 레지스트리가 경로의 현재 세대를
   교체해 `documentChanged(path, doc)` 를 낸다. `DashAnalysisModelContext` 는 문서를 갈아 끼우고 렌더
   표현은 바뀐 것만 다시 만든다(조건 값 편집은 형상을 바꾸지 않으므로 형상 캐시 무효화로 끝난다).
7. `DashRwDocument::clone()` — `IRWModule::clone()` 을 actor 에서 부르고 uuid 맵을 복사한 가변 문서를
   돌려준다. 심볼 uuid 가 승계되므로 저장된 DV 바인딩이 그대로 맞는다.
8. 배치 실행기(`DashMorphingDoeExecutor` · `DashMorphingUtils`)는 `DashRwMutableDocument&&` 만 받는다.
   렌더 상태와 표시 문서에 컴파일 타임으로 닿지 못하고, 유일성 때문에 누구도 중간 상태를 볼 수 없다.
9. 원복 코드 삭제 — 조건 원본값 포착·되쓰기, `basePart` DeepCopy·되쓰기, `ug->SetPoints` 제자리 변환,
   `partNames.first()` 폴백. 주입 실패·part 불일치는 샘플 실패, Target part 불일치는 배치 시작 실패다.
10. `DashAnalysisModelContextRegistry::getOrLoad` · `setReferenceModel` · `restoreReferenceModel` 은
    `Task<Result<…>>` 가 되고, 조회(`get` · `referenceContext` · `current(path)`)는 동기로 남는다.

## 4. 소비자 접근 함수

`DashRwActor` 는 `DashRwMutableDocument::open` 과 `clone` 만 부른다. 소비자는 actor 에 직접 닿지 않는다.

### `DashRwDocumentHandle` — 게이트. 전부 비동기

| 함수 | 반환 | 비고 |
|---|---|---|
| `isValid()` | `bool` | 동기. 유일한 동기 멤버 |
| `getSymbolTree()` | `Task<Result<unique_ptr<SymbolTreeNode>>>` | |
| `getData(uuid)` | `Task<Result<DashRwDataPayload>>` | 격자는 사본 |
| `getSymbolDetail(uuid)` · `getEditSchema(uuid, key)` | `Task<Result<std::string>>` | |
| `editData(uuid, key, json)` · `editMesh(uuid, grid)` | `Task<Result<void>>` | `editMesh` 는 입력을 복사해 넘긴다 |
| `exportContent(path)` | `Task<Result<void>>` | |
| `clone()` | `Task<Result<DashRwDocumentHandle>>` | actor 가 새 id 로 등록 |
| `hasFunction(name)` · `callFunction(name, args)` | `Task<…>` | 모듈 확장 함수 |

### `DashRwDocument` — 불변 · 복사 가능 · 공유. 읽기 전부 동기

| 함수 | 동기/비동기 | 비고 |
|---|---|---|
| `static empty()` | 동기 | 로드되지 않은 문서. 모든 접근자가 빈 값 |
| `clone()` | 비동기 `Task<Result<DashRwMutableDocument>>` | 불변에서 가변을 얻는 유일한 길 |
| `isLoaded()` · `pluginName()` · `loadedFilePath()` · `contentUuid()` | 동기 | |
| `partNames()` · `partData(name)` | 동기 | 렌더용 목록. `partData` 는 불변 사본의 `const vtkUnstructuredGrid*`. 워커에서 읽어도 된다 |
| `editablePartNames()` | 동기 | `MeshEditable` part 만 (#534 선택지 2) |
| `nodeSetNames()` · `setIndicesByName(name)` | 동기 | |
| `feConditionNames()` · `feConditionUuid(name)` · `feConditionNameByUuid(uuid)` | 동기 | |
| `feConditionEntries(name)` · `isFeConditionEditable(name)` | 동기 | 선적재 |
| `feConditionEditSchema(name, entryPtr)` · `feConditionParamSchema(name, entryPtr, param)` | 동기 | 선적재. 델리게이트가 부른다 |
| `feConditionShape(name)` | 동기 `std::optional<DashFeConditionShape>` | 채워져 있을 때만 값 |
| `fetchFeConditionShape(name)` | 비동기 `Task<Result<DashRwDocument>>` | 형상이 채워진 새 불변 문서 |

### `DashRwMutableDocument` — 가변 · move-only · 유일

| 함수 | 동기/비동기 | 비고 |
|---|---|---|
| `static open(path, contentUuid)` | 비동기 `Task<Result<DashRwMutableDocument>>` | 열기. 발행하려면 `seal()` |
| `seal() &&` | 동기 | 불변 문서로 소비. 선적재를 위해 내부에서 Task 를 잇는다면 `Task<Result<DashRwDocument>>` |
| `editablePartNames()` · `contentUuid()` | 동기 | clone 시점에 복사한 맵 |
| `updateMeshPoints(part, grid)` | 비동기 `Task<Result<void>>` | `MeshEditable` part 가 아니면 `InvalidArgument` |
| `editFeConditionEntry(name, entryPtr, changes)` | 비동기 `Task<Result<void>>` | |
| `exportSolverInput(path)` | 비동기 `Task<Result<void>>` | |

가변 문서에는 격자 읽기가 없다. 모핑 소스는 불변 문서의 `partData` 에서 가져온다.

### `DashAnalysisModelContext` · 레지스트리

| 함수 | 동기/비동기 |
|---|---|
| `DashAnalysisModelContext::load(path, contentUuid)` | 비동기 `Task<Result<void>>` — `open` → `seal` → 렌더 표현 조립 |
| `document()` | 동기. 현재 세대 `DashRwDocument` (값 복사) |
| `replaceDocument(DashRwDocument)` | 동기. 세대 교체 + 바뀐 렌더 표현만 재조립. 레지스트리만 부른다 |
| `createVisualActor()` · `controlVisibility()` · `setPartColor()` · 읽기 파사드 | 동기 |
| `Registry::getOrLoad(path)` · `setReferenceModel(path)` · `restoreReferenceModel()` | 비동기 `Task<Result<DashAnalysisModelContext*>>` |
| `Registry::publish(path, DashRwDocument)` | 동기. 현재 세대 교체 → `documentChanged(path, doc)` |
| `Registry::get(path)` · `referenceContext()` · `displayedContext()` | 동기 |

## 5. 소비자가 접근하는 방식

세 가지 모양만 있다.

**읽기 — 동기, 불변 사본.** 테이블 모델·델리게이트·렌더 조립은 바뀌지 않는다. 문서 값을 멤버에 들어도
되지만 그것은 그 세대다 — 최신이 필요하면 `documentChanged` 를 받거나 레지스트리에 다시 묻는다.

```cpp
QVariant DashConditionParameterization::data(const QModelIndex& index, int role) const
{
    const auto entries = m_document.feConditionEntries(row.name);   // 모듈 왕복 없음
    ...
}
```

**GUI 편집 — 세대 하나를 만드는 코루틴 슬롯.** `clone → edit → seal → publish`. 실패하면 현재 세대가
그대로다. 연속 편집이 잦아 clone 비용이 문제면 위젯이 가변 문서 하나를 Apply 까지 들고 있어도 된다 —
유일성은 그대로 성립한다.

```cpp
QCoro::Task<> DashConditionParameterizationWidget::commitEntryValue(int row, QJsonValue value)
{
    QPointer<DashConditionParameterizationWidget> self(this);
    DASH_REF_OR_CO_RETURN(draft, co_await m_model->document().clone());
    if (!self) co_return;
    if (auto r = co_await draft.editFeConditionEntry(name, entryPtr, { { param, value } }); !r) {
        DashNotify::warning(describe(r.error())); co_return;               // 세대 불변
    }
    if (!self) co_return;
    DASH_REF_OR_CO_RETURN(sealed, co_await std::move(draft).seal());
    DashAnalysisModelContextRegistry::Instance().publish(path, sealed);    // documentChanged → 표 갱신
}
```

**배치 — 유일한 가변 문서 위의 코루틴 사슬.** 표시 문서에는 타입상 닿을 수 없고, 원복이 없고, 실패는
샘플 상태에 실린다.

```cpp
QCoro::Task<> DashManager::MorphFromDoeSamples(QJsonArray samples, ...)
{
    const DashRwDocument reference = referenceContext->document();          // 이 배치가 보는 세대
    if (!reference.editablePartNames().contains(targetPart)) { fail("target part"); co_return; }   // #500 선택지 1
    DASH_REF_OR_CO_RETURN(doc, co_await reference.clone());                  // 배치당 1회
    DASH_REF_OR_CO_RETURN(volume, DashVolumeMeshSet::fromGrid(reference.partData(targetPart)));   // 배치당 1회
    DASH_REF_OR_CO_RETURN(frozen, co_await awaitResult(service.submitFreeze(Background, freezeRequest)));   // 배치당 1회
    for (const auto& sample : samples) {
        for (const auto& dv : conditionDvs(sample)) {
            const auto r = co_await doc.editFeConditionEntry(dv.name, dv.entryPtr, { { dv.param, dv.value } });
            if (!r) { status(runKey, failed("condition", r.error())); goto next; }
        }
        DashMorphRequest request{ volume.sourcePoints(ss), motionFor(sample, frozen), fixedIds };
        const auto moved = co_await awaitResult(service.submitMorph(Background, frozen, request));
        if (!moved) { if (moved.error().code() != Canceled) status(runKey, failed("morphing", moved.error())); continue; }
        auto morphed = volume.assembleVolume(*moved, fixedIds, ss);
        if (auto r = co_await doc.updateMeshPoints(targetPart, morphed); !r) { status(...); continue; }
        if (auto r = co_await doc.exportSolverInput(outputPath); !r)        { status(...); continue; }
        status(runKey, "Done");
    }
}   // doc 소멸 → 복제 인스턴스 닫힘. reference 는 이 함수가 든 세대이고, GUI 가 앞서 갔어도 영향이 없다
```

ModelRunner · Optimizer 의 `performMorphingAndExport` 도 같은 사슬이다. 반복마다 여는 임시 문서는 함수
스코프에서 `open()` 하고 레지스트리에 발행하지 않는다.

## 6. 범위 밖과 후속

- **볼륨 메시는 이 범위에서 `DashManager` 를 떠난다.** 볼륨 메시 4종(`m_inputVTU` · `m_linearizedVTU` ·
  `m_originalQuadraticCells` · `m_midNodeMap`)은 격자 하나에서 결정적으로 유도되는 순수 함수의 결과이고
  다른 GUI 상태를 읽지 않는다. 이를 값 타입 `DashVolumeMeshSet : DashVolumeMeshAccess` 로 묶어
  `fromGrid(const vtkUnstructuredGrid*)` 로 만들고, `DashManager` 는 멤버 세트 하나에 위임하며, 배치는
  `document().partData(targetPart)` 에서 **배치당 1회** 만들어 샘플마다 인자로 넘긴다. 유도에 DeepCopy 와
  셀 순회가 들어가므로 샘플마다 격자에서 다시 만들지 않는다. `DashManager::RunVolumeMorphing` 은 삭제되고
  실행기 안의 `basis.Morph(set.sourcePoints(ss), …)` + `set.assembleVolume(…)` 두 줄이 된다.
  `fromGrid` 는 `VTK_QUADRATIC_TETRA` 외의 2차 셀을 `InvalidArgument` 로 거절한다 — 현재 코드는 그 셀을
  선형화하지 않은 채 `VTK_TETRA` 로 라벨한다.
- **배치 모핑은 `DashMorphingService` Background 레인을 탄다. 동기 모핑 호출은 남지 않는다.** 실행기는
  설계 점군과 마커 점군을 `DashHandleBlock` 둘로 만들어 배치당 1회 `submitFreeze` 하고, 샘플마다 target −
  baseline 으로 `DashHandleMotion` 을 만들어 마커 몫을 `appendZeros` 한 뒤 `submitMorph` 한다. 서비스·요청·
  응답 타입은 [모핑 문서 2절](../morphing-request-service.md#2-게이트-계약--서비스-경계를-넘는-타입)의 것
  그대로다. 귀결 — `DashMorphingBasis` 의 점군·target 오버로드와 모핑 문서 7절 "미이관 경로" 가 삭제된다.
  스레드 예산은 코어 전량(`threads = 0`)에서 서비스 예산(레인당 코어/2)으로 바뀌고, 배치 취소가
  `std::stop_source` 하나로 모핑 경계에서 성립한다. 핸들과 `volumeFixedIds` 는 GP 세트 메시 인덱스
  기준이라 Target part 가 다르면 어긋난다 — 2절의 #500 선택지 1 검사가 그대로 필요하다.
- 핸들 폴리데이터의 데이터·표시 분리 — #428 · #430.
- Set JSON 스키마 병합과 DOE 선택 계약 — parameterized model 본 단계.
- CAD(NX) 변형 — 외부 프로세스 이벤트 구동 경로. 이 게이트를 쓰지 않는다.
