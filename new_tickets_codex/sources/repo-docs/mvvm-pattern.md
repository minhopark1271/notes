# MVVM 패턴

> 상태: 초안 (2026-09-30). 실제 프로젝트에 적용하면서 결함을 고치거나 동작을 바꿀 수 있다. 지금 구현은 첫 도입본이다.
> 이슈: [#584](https://github.com/NumeRealWorks/DashOpti_GUI/issues/584)

## 왜 함께 들여오나

MVVM 의 Model 은 화면에 보일 값이면서 파일로 저장할 대상이다. Model 기반을 설계하며 저장, 다른 Model 참조, 복원을 함께 정해야 했고, 그 과정에서 저장과 개체 등록은 MVVM 을 몰라도 되는 일이라 persistence 층으로 떼어 냈다. 두 층은 따로 쓸 수 있지만 persistence 층의 첫 사용자가 MVVM Model 이고 Model 은 persistence 층 없이는 저장되지 않으므로 한 번에 들여온다. persistence 층은 [persistence.md](persistence.md) 에 있다.

사람과 코드 생성 에이전트가 새 화면을 MVVM 으로 짤 때 따르는 규칙이다. 범위는 MVVM 메커니즘까지다. 이 구조를 쓰는 앱이 무엇을 소유하는지는 여기서 정하지 않는다.

파일은 다음과 같다. persistence 쪽 파일은 [persistence.md](persistence.md) 에 있다.

- `model/DashMvvmModelBase.h`, `.cpp`: Model 기반과 필드 매크로
- `viewmodel/DashMvvmViewModelBase.h`, `.cpp`: ViewModel 기반
- 예시 Model 과 ViewModel 은 `tests/TestMvvmBase.cpp` 안에 있다.

## 0. 층

층은 둘이다.

- persistence 층: registered object, registry, save data, save system. MVVM 과 무관하다. [persistence.md](persistence.md) 를 따른다.
- MVVM 층: `DashMvvmModelBase`, ViewModel 기반. persistence 층을 쓴다.

상속은 `QObject` → `DashRegisteredObject` → `DashMvvmModelBase` → 파생 Model 이다. Model 은 registered object 이므로 저장, 참조, 복원, 개체 등록은 persistence 문서의 규칙을 그대로 따른다.

MVVM 층의 책임은 다음과 같다.
- **Model**: 데이터와 도메인 규칙을 가진다. 저장과 불러오기 대상이다. 화면을 모른다.
- **ViewModel**: Model 을 읽어 View 가 보여 줄 값을 내놓는다. 값이 바뀌면 signal 을 보낸다. View 의 입력을 Model 로 넘긴다. View 를 모른다.
- **View**: 위젯이다. ViewModel 만 안다.

View 는 Model 을 include 하지 않는다. Model 은 Qt Widgets 를 include 하지 않는다. Widgets View 만 쓴다.

## 1. Model 기반 `DashMvvmModelBase`

`DashRegisteredObject` 를 상속하고 `Q_OBJECT` 를 둔다. 템플릿이 아니다. 단일 스레드를 가정한다.

### 필드

- stored field 는 `DASH_MVVM_FIELD(Class, Type, name, Name, defaultValue)` 로 선언한다. `Q_PROPERTY(READ, WRITE, BINDABLE)` 와 bindable property 로 펼쳐진다. 저장, 불러오기, `assignPropertiesFrom` 이 이 property 목록을 따라가므로 필드마다 따로 짤 코드가 없다.
- stored field 에는 binding 을 걸지 않는다.
- `DASH_MVVM_TRANSIENT_FIELD` 는 cache 가 꼭 필요한 파생 값에만 쓴다. `WRITE` 가 없고 `STORED false` 다. 그 binding 은 개체가 다 만들어진 뒤에 건다.
- 파생 값은 보통 `valid()` 처럼 필드로 계산하는 평범한 함수로 둔다.
- 매크로는 private 절에서 끝난다. 그 뒤에 access specifier 를 쓴다. `defaultValue` 는 식이어야 한다 (`{}` 대신 `QList<int>()`).
- `DASH_MVVM_FIELD` 에 쓰는 enum 은 그 앞에 선언하고 `Q_ENUM` 을 붙인다.

### valid

- `virtual bool valid() const = 0;` 는 public 이다. 파생이 필드로 계산한다. 저장된 사본은 없다.

### 값 옮기기

`assignPropertiesFrom(const DashMvvmModelBase* other)` 는 protected 다. 파생이 `void assignFrom(const Self* other) { assignPropertiesFrom(other); }` 로 노출한다.

- `other` 가 null 이거나 클래스가 다르면 `qFatal()` 이다 (릴리스에서도). 자기 자신이면 아무것도 하지 않는다.
- `DashRegisteredObject` 의 property 다음부터 `isStored() && isWritable()` 인 property 만 update group 안에서 옮긴다.
- hook 은 부르지 않고 직렬화도 거치지 않는다.

## 2. ViewModel 기반 `DashMvvmViewModelBase`

ViewModel 은 View 와 함께 오래 살고, Model 은 컨테이너에서 추가되고 삭제되며 짧게 산다. 그래서 Model 은 `QPointer` 로 가리키고 붙잡지 않는다.

- `setModel(DashMvvmModelBase* model)`:
  1. 옛 Model 의 `destroyed` 연결과 mirror binding 을 끊는다 (파생 hook `unbindModel()`).
  2. update group 안에서 새 Model 로 다시 건다 (파생 hook `bindModel()`).
  3. group 이 닫힌 뒤 `modelChanged()` 를 보낸다.
  4. null 이면 빈 상태로 둔다.
- Model 이 소멸하면 `destroyed` 를 받아 binding 을 끊고 빈 상태로 둔 뒤 `modelChanged()` 를 보낸다.
- `valid` mirror 는 기반이 둔다. Model 의 `valid()` 를 읽는 binding 이다.
- 파생 ViewModel 은 필드마다 bindable property 와 NOTIFY signal 을 두고, `bindModel()` 에서 Model 필드에 binding 한다. `unbindModel()` 에서는 값을 대입해 binding 을 끊고 빈 값으로 되돌린다.
- setter 는 Model setter 를 부르고, Model 이 없으면 아무것도 하지 않는다. mirror property 에는 초기화와 `unbindModel()` 말고는 직접 대입하지 않는다 (binding 이 끊긴다).
- 새 signal 을 선언하는 층은 템플릿이 아닌 `Q_OBJECT` 클래스여야 한다 (moc 제약).

## 3. 새 Model 을 만드는 절차

1. `DashMvvmModelBase` 를 상속한 `final` 클래스에 `Q_OBJECT` 를 둔다.
2. 필드를 `DASH_MVVM_FIELD` 로 선언한다.
3. `valid()` 를 필드로 계산해 구현한다.
4. 생성자, 하위 Model 소유, 다른 Model 참조, `DASH_REGISTER_OBJECT`, 짝 `.cpp` 는 [persistence.md](persistence.md) 의 「새 registered object 를 만드는 절차」를 따른다.

## 4. 기존 데이터를 관리되는 Model 로 옮기기

지금 코드에 있는 데이터(plain struct, Q_GADGET, 위젯이 들고 있는 값)를 `DashMvvmModelBase` 파생 Model 로 옮기는 절차다. 저장, 참조, 등록 규칙은 다시 쓰지 않는다. [persistence.md](persistence.md) 의 「Registry」, 「Save system」, 「새 registered object 를 만드는 절차」를 따른다.

1. 옮길 대상의 필드를 훑는다. 저장하고 화면에 보일 값은 stored field 로 옮긴다. 다른 필드로 계산되는 값은 `valid()` 같은 평범한 함수로 둔다. cache 가 꼭 필요한 파생 값만 transient field 로 둔다. stored field 의 타입은 [persistence.md](persistence.md) 의 「값 변환」이 지원하는 것이어야 한다.
2. Model class 를 만든다. `final` 클래스에 `Q_OBJECT`, 필드마다 `DASH_MVVM_FIELD`, `Q_INVOKABLE explicit X(DashObjectRegistry*)`, `valid()` 를 두고, 짝 `.cpp` 에 `DASH_REGISTER_OBJECT(X)` 를 둔다. 같은 타입끼리 값을 복사할 일이 있으면 `assignFrom` 을 둔다. 헤더만 있는 `Q_OBJECT` 클래스는 짝 `.cpp` 를 둔다.
3. 기존 값을 Model 로 옮긴다. registry 로 `spawn<T>()` 한 뒤 setter 로 채운다. 여러 setter 는 `QScopedPropertyUpdateGroup` 으로 묶어 알림을 한 번에 보낸다.
4. 기존 코드가 값을 직접 들던 곳을 Model 을 보도록 바꾼다. 소유하는 쪽은 `std::shared_ptr<X>` 를 든다. 소유하지 않는 쪽은 id 를 들고, 필요하면 `QPointer` 로 cache 한다. 소유 규칙은 [persistence.md](persistence.md) 의 「Registry」에 있다.
5. ViewModel 을 만들어 `setModel()` 로 붙인다. View 는 ViewModel 만 본다. 위젯이 들던 값은 ViewModel property 로 바뀐다.
6. 저장이 필요하면 save system 으로 저장한다 ([persistence.md](persistence.md) 의 「Save system」). 기존 파일 형식을 읽어야 하면 옛 형식에서 Model 로 옮기는 변환을 한 번만 하는 가져오기 경로로 두고, 새 저장은 save system 형식으로 한다.
7. 옮긴 뒤 확인한다. 저장 후 불러오기로 값이 돌아오는가, `valid()` 가 기대대로인가, ViewModel 의 mirror 가 Model 의 변경을 따라오는가.

예시 이름은 가상이다. 옮기기 전이다.

```cpp
struct LegacyMeshSettings
{
    double elementSize = 1.0;
    int maxIterations = 50;
    QString solverName;
};
```

옮긴 뒤의 Model 이다.

```cpp
class DashMeshSettingsModel final : public DashMvvmModelBase
{
    Q_OBJECT

    DASH_MVVM_FIELD(DashMeshSettingsModel, double, elementSize, ElementSize, 1.0)
    DASH_MVVM_FIELD(DashMeshSettingsModel, int, maxIterations, MaxIterations, 50)
    DASH_MVVM_FIELD(DashMeshSettingsModel, QString, solverName, SolverName, QString())

public:
    Q_INVOKABLE explicit DashMeshSettingsModel(DashObjectRegistry* registry)
        : DashMvvmModelBase(registry)
    {
    }

    void assignFrom(const DashMeshSettingsModel* other) { assignPropertiesFrom(other); }

    bool valid() const override { return elementSize() > 0.0 && maxIterations() > 0; }
};
```

`DASH_REGISTER_OBJECT(DashMeshSettingsModel)` 는 헤더가 아니라 짝 `DashMeshSettingsModel.cpp` 에 둔다. 매크로가 익명 namespace 변수로 펼쳐져서, 헤더에 두면 include 하는 translation unit 마다 등록 코드가 생긴다.

기존 값으로 Model 을 채우는 호출부다.

```cpp
std::shared_ptr<DashMeshSettingsModel> toModel(DashObjectRegistry& registry,
                                               const LegacyMeshSettings& legacy)
{
    auto model = registry.spawn<DashMeshSettingsModel>();
    const QScopedPropertyUpdateGroup group;
    model->setElementSize(legacy.elementSize);
    model->setMaxIterations(legacy.maxIterations);
    model->setSolverName(legacy.solverName);
    return model;
}
```

소유하는 쪽은 돌려받은 `shared_ptr` 를 멤버로 든다. 저장은 `DashSaveSystem::saveDocument({ model.get() })` 와 `DashSaveSystem::writeJsonFile()` 로 한다. 둘 다 `dash::core::Result` 를 돌려주므로 반환값을 검사한다. 왕복 확인 코드의 예는 `tests/TestMvvmBase.cpp` 의 `roundTrip` 이다.

## 5. `qFatal` 규칙

릴리스에서도 멈춘다.

- null 이거나 클래스가 다른 `assignPropertiesFrom`

registered object 생성, 참조, id 에 관한 규칙은 [persistence.md](persistence.md) 에 있다.

## 6. 범위 밖

- 기존 `viewmodel/` 의 `Dash*PresentationModel` 은 아직 이 기반으로 옮기지 않는다.
- Project, Session 같은 앱 계층의 소유 구조는 이 문서가 정하지 않는다.
