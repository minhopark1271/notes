# Persistence

> 상태: 초안 (2026-09-30). 실제 프로젝트에 적용하면서 결함을 고치거나 동작을 바꿀 수 있다. 지금 구현은 첫 도입본이다.
> 이슈: [#584](https://github.com/NumeRealWorks/DashOpti_GUI/issues/584)

## 왜 함께 들여오나

MVVM 의 Model 은 화면에 보일 값이면서 파일로 저장할 대상이다. Model 기반을 설계하며 저장, 다른 Model 참조, 복원을 함께 정해야 했고, 그 과정에서 저장과 개체 등록은 MVVM 을 몰라도 되는 일이라 persistence 층으로 떼어 냈다. 두 층은 따로 쓸 수 있지만 persistence 층의 첫 사용자가 MVVM Model 이고 Model 은 persistence 층 없이는 저장되지 않으므로 한 번에 들여온다. MVVM 층은 [mvvm-pattern.md](mvvm-pattern.md) 에 있다.

registered object 를 저장하고 id 로 참조하고 불러오는 규칙이다. 범위는 persistence 메커니즘까지다. 이 구조를 쓰는 앱이 무엇을 소유하는지는 여기서 정하지 않는다. 첫 사용자는 MVVM Model 이다.

파일은 다음과 같다. 모두 최상위 `persistence/` 폴더에 있다.

- `DashRegisteredObject.h`, `.cpp`: registered object 기반, save/load hook
- `DashObjectRegistry.h`, `.cpp`: registered object 를 만들고 id 로 index 를 두는 registry
- `DashSaveData.h`, `.cpp`: save data gadget (`.cpp` 는 AUTOMOC 용 짝 파일)
- `DashSaveSystem.h`, `.cpp`: 저장과 불러오기

상속은 `QObject` → `DashRegisteredObject` 이다.

결정:

- save hook 이 `DashRegisteredObject` 에 있어서 registered object 가 save 타입(`DashSaveVersion`)을 안다. 영속화하는 개체가 치르는 비용으로 받아들인다.
- 다른 Qt base(예: `QAbstractItemModel`)를 상속한 registered object 가 필요해지면 그때 공통부를 일반 C++ class 로 뗀다. 지금은 하지 않는다.

## 1. Registered object 기반 `DashRegisteredObject`

`QObject` 를 상속하고 `Q_OBJECT` 를 둔다. 템플릿이 아니다. 단일 스레드를 가정한다.

### 정체성과 생성

- `QUuid id()` 는 public 으로 읽는다. `setId()` 는 public 이고 registry index 도 함께 옮긴다. id 가 같으면 아무것도 하지 않고, 같은 id 가 살아 있는 다른 개체에 있으면 `qFatal()` 이다. 불러오기가 저장된 id 를 반영할 때도 이것을 쓴다.
- 생성자는 `Q_INVOKABLE explicit X(DashObjectRegistry* registry)` 이다. 파생 클래스는 `final` 로 두고 `DASH_REGISTER_OBJECT(X)` 를 클래스의 짝 `.cpp` 에 한 줄 둔다.
- registered object 는 registry 의 `spawn()` 으로만 만든다. 그 밖에서 만들면 `qFatal()` 로 멈춘다.
- QObject parent 는 주지 않는다. lifetime 은 `std::shared_ptr` 만 관리한다.
- `virtual void onInitialize()` 는 registry 가 새로 `spawn()` 할 때만 불린다. 불러오기 경로에서는 부르지 않는다. 개수가 정해진 하위 object 는 여기서 `registry()->spawn<T>()` 로 만든다. 생성자에서 만들지 않는다. 불러오기에서는 하위가 저장 데이터로 다시 만들어지므로, 여기서 만들면 중복된다.

### save/load hook

hook 은 모두 public virtual 이고 기본 구현은 아무것도 하지 않는다. 부모가 자기가 소유한 하위에 대해 직접 부를 수 있어야 하기 때문이다.

- `bool onPreSave(QString& outErrorMessage)`
  - pointer reference 를 id 로 바꾼다.
  - 소유한 하위마다 `DashSaveSystem::saveObject()` 를 불러 그 결과를 stored field(`QList<DashObjectSaveData>`)에 담는다.
  - 저장은 개체를 망가뜨리지 않는다. 하위 인스턴스나 런타임 상태를 건드리지 않는다.
- `bool onPostLoad(const DashSaveVersion& version, QString& outErrorMessage)`
  - stored field의 중첩 하위 데이터로 하위를 만들고 채운다. `spawnObject()`, 이미 있는 하위면 `loadObject()`.
  - reference 는 id 로만 들고 여기서 풀지 않는다.
  - 옛 버전 데이터는 여기서 변환한다.
  - 다 쓴 직렬화 정보 필드는 비운다.
- `void onResolveReferences()`
  - 불러오기 2단계에서 불린다. id 를 pointer 로 바꾼다. 대상이 없으면 `qFatal()` 이다.

hook 이 `false` 를 돌려주면서 `outErrorMessage` 에 넣은 문장은 save system 이 `Result` 의 오류 메시지로 싣는다.

`loaded()` signal 은 불러오기가 성공으로 끝난 뒤에 save system 이 모아서 보낸다. `loadDocument()` 에서는 1단계와 2단계(`onResolveReferences()`)가 모두 끝난 뒤이고, 실패하면 하나도 보내지 않는다.

### 클래스 버전

`Q_CLASSINFO("DashClassVersion", "N")` 로 둔다. 없으면 1이다.

## 2. Save data

Q_GADGET 이다. save system 이 다른 값과 같은 경로로 변환한다.

- `DashObjectSaveData`: `objectClass`, `id`, `objectData`(stored field tree)
- `DashSaveVersion`: `formatVersion`, `classVersions`(클래스 이름에서 int 로), `classVersion(className)`
- `DashSaveDocument`: `formatVersion`, `createdAppVersion`, `modifiedAppVersion`, `classVersions`, `roots`

소유한 하위는 부모의 `objectData` 안에 중첩된다. 다른 registered object 에 대한 reference 는 id 로만 저장한다.

## 3. 값 변환

save system 안에서 format 중립 `QVariant` tree 까지만 변환한다. JSON 은 파일 층만 안다.

- 스칼라: bool, int(범위 안의 정수), double, `QString`, `QUuid`(문자열), `Q_ENUM`(key 이름)
- 순차 컨테이너: `QSequentialIterable` 로 볼 수 있고 끝에 원소를 붙일 수 있는 것 (`QList`, `QStringList`, `std::vector`). 원소 타입으로 재귀한다.
- Q_GADGET: 메타오브젝트로 재귀한다.
- `QVariantList`, `QVariantMap`: 원소(맵은 값)마다 그 원소의 실제 meta type 으로 재귀해 검사하고 변환한다. 하나라도 실패하면 필드 전체가 실패하고 오류에 키나 인덱스가 경로로 들어간다 (`nested: [1]: ...`).
- 연관 컨테이너(`QMap`, `QHash`, `std::map`)는 지원하지 않는다. 지원하지 않는 타입이면 저장과 불러오기가 필드 이름과 함께 실패한다.
- 불러올 때 파일에 없는 필드는 그대로 두고, 타입이 틀린 필드는 실패한다.

### `utils/DashGadgetCodec` 과의 차이

`utils/DashGadgetCodec` 은 save system 이 쓰지 않는다. 코드에서 확인되는 차이는 다음과 같다. 저장소에서 codec 을 부르는 곳은 `tests/TestGadgetCodec.cpp` 뿐이다.

- 대상: codec 은 Q_GADGET 구조체만 다룬다 (`void*` 와 타입 id 를 받는다). save system 은 registered object(QObject)의 stored property 를 돌고, 그 안의 gadget 은 재귀로 다룬다.
- 입출력: codec 은 `QVariantMap` 이나 `QJsonObject` 로 바꾸고, 실패는 로그와 `DashGadgetLoadReport` 로 알린다. save system 은 `QVariant` tree 로 바꾸고, 실패는 `Result` 오류로 돌려준다.
- 불러오기 실패: codec 은 키가 없거나 변환에 실패한 속성을 건너뛰고 기존 값을 둔 채 `true` 를 돌려준다. save system 은 타입이 틀린 필드가 있으면 실패한다.
- 컨테이너: codec 은 내장 변환이 없는 컨테이너마다 `registerGadgetContainer<T>()` 를 시작 때 불러야 읽힌다. save system 은 `QSequentialIterable` 로 보고 등록이 필요 없다.
- 값 형식: codec 은 Q_FLAG 와 이름 없는 enum 값(정수로 기록)을 다루고 `int` 외의 정수 타입도 받는다. save system 은 bool, int, double, `QString`, `QUuid` 와 key 가 있는 `Q_ENUM` 만 받고, key 가 없는 값은 실패한다. 반대로 codec 은 `QUuid` 를 문자열로 바꾸지 않고, 유한하지 않은 double 도 검사하지 않는다.

## 4. Registry `DashObjectRegistry`

`QObject` 다. 개체를 소유하지 않고 id 에서 `std::weak_ptr` 로 가는 index 만 든다. registry 는 자기 개체들보다 오래 산다.

- `spawn(const QMetaObject&)` 와 `spawn<T>()` 는 새 registered object 를 만들고 `onInitialize()` 를 부른다. 마지막 `shared_ptr` 가 사라지면 index 에서 항목을 지운 뒤 개체를 지운다.
- ownership: 소유하는 쪽(부모, 최상위를 드는 쪽)이 `shared_ptr` 를 든다. 소유하지 않는 reference 는 id 로 들고, 필요하면 `QPointer` 로 cache 한다. 누군가 `shared_ptr` 를 들지 않으면 개체는 사라진다.
- `find(id)` 는 없으면 null 이다. `require(id)` 는 없으면 `qFatal()` 이다.
- `reindex(object, previous)` 는 `setId()` 가 id 를 바꾼 뒤 부른다. `previous` 키의 항목을 `object.id()` 키로 옮긴다. `previous` 키의 항목이 그 개체가 아니면 `qFatal()` 이다.
- class table는 클래스 이름에서 `QMetaObject` 로 가는 표다. `DASH_REGISTER_OBJECT(Class)` 가 정적 초기화에서 채운다.

## 5. Save system `DashSaveSystem`

모든 public 함수는 `dash::core::Result<T>` 를 돌려준다. 호출하는 쪽은 반환값을 검사하고, 실패하면 `error().message()` 를 사용자에게 보이거나 로그로 남기고 이어서 실행하지 않는다.

오류 코드는 다음과 같다.

- `OperationFailed`: hook 이 실패했다 (hook 의 메시지가 실린다). 파일을 열지 못했거나 쓰기와 교체에 실패했다.
- `InvalidArgument`: 값이 object 에 맞지 않는다 (타입 오류, 지원하지 않는 타입, 등록되지 않았거나 다른 클래스). JSON 파싱 오류. 최상위가 JSON 객체가 아니다.

함수는 다음과 같다.

- `saveObject(object, out)`: `onPreSave()`, stored field, `objectClass`와 `id` 순서다.
- `loadObject(object, data, version)`: 기존 인스턴스에 채운다. 순서는 클래스 확인, update group, stored field, `onPostLoad()`, id 반영, group 닫기, 알림이다. 알림(`loaded` signal)은 모아 둔다. `loadDocument()` 밖에서 부른 경우 가장 바깥 호출이 group 을 닫은 뒤, 그 호출이 성공했을 때만 보내고 실패하면 버린다. 중첩 깊이를 센다.
- `spawnObject(registry, data, version)`: class table로 찾아 `onInitialize()` 없이 spawn 한 뒤 `loadObject()` 를 부른다.
- `saveDocument(roots)`: 문서 전체를 메모리에 완성한다. 하나라도 실패하면 아무것도 돌려주지 않는다.
- `loadDocument(registry, data)`:
  1. roots 를 `spawnObject()` 한다. 하위는 각 `onPostLoad()` 가 만든다. 이번 불러오기에서 spawn 된 인스턴스는 모두 임시 목록에 `shared_ptr` 로 붙잡는다.
  2. 그 인스턴스마다 `onResolveReferences()` 를 부른다.
  3. 모아 둔 `loaded` 알림을 한 번에 보낸다. 1단계가 실패하면 하나도 보내지 않는다.
  4. 임시 목록을 놓는다. 아무도 소유하지 않은 인스턴스는 자연 소멸한다.
- `writeJsonFile(document, path)`: `QSaveFile` 로 쓴다. 실패해도 기존 파일이 남는다.
- `readJsonFile(path)`: 파싱 오류 메시지에 errorString 과 offset 이 들어간다.

저장은 원자적이다. 문서를 다 만든 뒤 파일을 원자적으로 교체하고 object 는 바뀌지 않는다. 불러오기는 원자적이지 않다. 파일이 있는지는 호출하는 쪽이 확인한다. 열기 실패는 없는 파일과 권한 문제를 구분하지 않는다.

## 6. 새 registered object 를 만드는 절차

1. `DashRegisteredObject` 를 상속한 `final` 클래스에 `Q_OBJECT` 를 둔다. (MVVM Model 은 `DashMvvmModelBase` 를 거친다.)
2. `Q_INVOKABLE explicit X(DashObjectRegistry*)` 생성자를 둔다.
3. 하위 object 를 소유하면 stored field를 `QList<DashObjectSaveData>` 로 두고 `onPreSave()` 와 `onPostLoad()` 에서 채우고 비운다. 개수가 정해졌으면 `onInitialize()` 에서 만든다.
4. 다른 registered object 를 가리키면 id 필드를 두고 `onPreSave()` 에서 채우고 `onResolveReferences()` 에서 pointer 로 푼다.
5. 짝 `.cpp` 에 `DASH_REGISTER_OBJECT(X)` 를 둔다. 헤더에 두지 않는다. 매크로가 익명 namespace 변수로 펼쳐져서, 헤더에 두면 그 헤더를 include 하는 translation unit 마다 등록 코드가 생긴다.
6. 헤더에만 있는 `Q_OBJECT` 나 `Q_GADGET` 클래스는 짝 `.cpp` 를 둔다. 루트 CMake 가 `.cpp` 만 GLOB 해서, 짝이 없으면 AUTOMOC 이 헤더를 처리하지 않는다.

## 7. `qFatal` 규칙

릴리스에서도 멈춘다.

- `spawn` 밖에서 registered object 생성
- `newInstance()` 실패 (생성자에 `Q_INVOKABLE` 누락)
- 참조 대상 id 를 찾지 못함. 불러오기 중이든 실행 중이든 같다.
- 같은 id 가 살아 있는 두 개체에 생김
