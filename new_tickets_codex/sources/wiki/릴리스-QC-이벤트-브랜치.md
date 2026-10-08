# Release / QC 이벤트 브랜치

[[저장소-관리-수칙]] 하위 문건. 브랜치·PR 일반 규칙은 그쪽에 있고, 여기는 릴리스 한 번의 절차다.

병합은 한 방향으로만 흐른다. **`dev` → QC → `main` → `dev`.** 아래는 `v1.2.0` 기준이다.

## 1. QC 브랜치 개설

`main..dev`가 이번 릴리스에 들어갈 목록이다. 여기 없어야 할 게 있으면 지금 정리한다.

```
git switch dev && git pull
git log --oneline main..dev
git switch -c rc/v1.2.0
git tag -a v1.2.0-rc0 -m "v1.2.0 rc0"
git push -u origin rc/v1.2.0 && git push origin v1.2.0-rc0
```

## 2. QC 이슈 처리

QC 브랜치에서 분기해 QC 브랜치로 돌아온다. `dev`에 바로 넣지 않는다 —
QC 대응 커밋마다 빌드하지 않기 위해서고, QC 테스트 절차를 버전 단위로 관리하기 위해서다.

- PR의 **base는 `dev`가 아니라 `rc/v1.2.0`이다.** 기본값이 `dev`라 자주 틀린다.
- 리뷰 후 squash merge (수칙 2절 4항과 같다). 브랜치는 `-D`로 지운다 — `-d`는 거부한다(수칙 2절 5항).

## 3. rc 전달

QC에 바이너리를 넘길 때마다 rc 번호를 하나 올린다. 2와 3을 QC가 끝날 때까지 반복한다.

```
git tag -a v1.2.0-rc1 -m "v1.2.0 rc1" && git push origin v1.2.0-rc1
```

## 4. 릴리스

이 커밋으로 패키지를 만들어 Archive한다.

```
git switch main && git pull
git merge --no-ff rc/v1.2.0 -m "main: release v1.2.0"
git tag -a v1.2.0 -m "release v1.2.0"
git push && git push origin v1.2.0
```

- **`--squash`나 cherry-pick을 쓰면 안 된다.** 아래 "squash의 경계" 참고.
- 태그는 annotated(`-a`)다. 경량 태그는 `git describe`가 기본으로 잡지 않고, 누가 언제 릴리스했는지도 안 남는다.

## 5. `dev` 복귀와 정리

QC 브랜치가 아니라 **`main`을** `dev`로 되돌린다.

```
git switch dev && git pull
git merge --no-ff main -m "dev: merge main back"
git push
git branch -d rc/v1.2.0
```

지우는 것은 **로컬 브랜치뿐이다.** 원격 `rc/<version>`은 남겨 둔다 — 어느 커밋이 어느
릴리스였는지 origin 에서 그대로 보인다.

QC 브랜치를 `dev`로 직접 머지하면 정식 버전 태그가 `main`의 병합 커밋에 붙어 있어 `dev`에서 영영 안 보인다.
`main`을 거치면 그 커밋째로 들어오므로 `dev`에서도 `git describe`가 `v1.2.0-4-g…`
(마지막 릴리스 + 그 뒤 4커밋)처럼 답하고, `main..dev`가 다시 **릴리스 안 된 것만** 답한다.
이게 다음 릴리스의 1절 입력이다.

한 바퀴 돌린 결과다. `dev`에서 갈라진 `rc/v1.2.0`이 `main`으로 들어가고, 그 `main`이 다시 `dev`로 내려온다.

![릴리스 한 바퀴](images/flow-01-release-cycle.png)

## 6. 핫픽스

`main`에서 분기해 PR base `main`으로 돌아온 뒤, 태그를 달고 5절과 같은 방식으로 `dev`에 내린다.

![핫픽스](images/flow-02-hotfix.png)

핫픽스 브랜치는 `main`에 한 번 들어가고 버려지는 잎이라 squash해도 된다. 7절 참고.

## 7. squash의 경계

> **한 번 들어가고 버려지는 잎 브랜치를 합칠 때만 쓴다** — 작업 브랜치 → `dev`,
> QC 작업 브랜치 → QC 브랜치, 핫픽스 브랜치 → `main`.
> 병합 후에도 살아남아 또 병합될 브랜치(QC → `main`, `main` → `dev`)에는 쓰지 않는다.
> 기준은 받는 쪽이 아니라 **합쳐 넣는 쪽**이다.

`git merge --squash`와 cherry-pick은 **병합했다는 사실을 기록하지 않는다.** 결과 파일만 한 커밋으로
남기고 부모 연결은 만들지 않는다. 그래서 git 입장에서 `main`과 QC 브랜치는 여전히 갈라진 적 없는
남남이고, 두 브랜치의 공통 조상이 한 발짝도 전진하지 않는다.

**실패는 이번 릴리스가 아니라 다음 사이클에 나타난다.** 다음 릴리스에서 git이 "지난번 이후의 변경"을
계산할 때 공통 조상이 최초 커밋에 멈춰 있으니, 이미 릴리스한 변경까지 전부 새 변경으로 취급해
같은 파일에 두 번 손댄 지점마다 충돌을 낸다. 4절을 `--squash`로 바꿔 릴리스를 두 번 돌리면
2차에서 충돌하고, `main..dev`는 릴리스된 것까지 세고, `main` 핫픽스도 `dev`로 못 내려간다.

작업 브랜치는 한 번 들어가고 삭제되니 이력이 사라져도 다시 병합될 일이 없다. `main`은 다음
릴리스에도 핫픽스에도 계속 병합 대상이 된다. 여기서 이력을 끊으면 그 다음 병합이 전부 틀어진다.

4절을 `--squash`로 바꿔 돌린 그래프다. `main: release v1.2.0`에 **들어오는 선이 없다.**
git이 보기에 `main`과 `dev`는 아직 갈라진 적이 없고, 그래서 다음 릴리스
(`rc/v1.3.0`)를 합치려는 순간 `VERSION`에서 충돌한다.

![트렁크에 squash](images/flow-03-squash-to-trunk.png)

## 8. 어긋나는 경우

### 8.1 QC 브랜치를 `dev`로 직접 되돌린다 (5절 위반)

`main`과 `dev` 양쪽에 같은 `rc` 팁이 들어가 이력은 멀쩡하지만, 정식 태그 `v1.2.0`은
`main`의 병합 커밋에 붙어 있어 `dev`에서 보이지 않는다.

![rc 를 dev 로 직접](images/flow-04-rc-back-to-dev.png)

```
$ git describe --tags dev
v1.2.0-rc0-8-g1fbea01         # 정식 태그가 아니라 rc 를 짚는다
$ git log --oneline dev..main
c310d44 main: release v1.2.0  # dev 가 모르는 릴리스 커밋
```

### 8.2 QC 이슈를 `dev`에 바로 넣는다 (2절 위반)

수정은 `dev`에만 들어가고 QC 브랜치에는 없다. 릴리스는 **고쳐지지 않은 채로 나간다.**

![QC 이슈를 dev 에](images/flow-05-qc-fix-into-dev.png)

```
$ git show v1.2.0:src/export.py
def export(rows):
    return len(rows)          # 가드가 없다 — QC 가 확인한 바이너리와 다르다
```

### 8.3 QC 브랜치를 `main`에서 딴다 (1절 위반)

`main`에서 따려면 `dev`를 먼저 `main`에 올려야 한다. QC를 거치지 않은 작업이 `main`에
먼저 도착하고, QC가 그중 하나를 반려하면 `main`에는 넣은 기록과 뺀 기록이 함께 남는다.

![rc 를 main 에서](images/flow-06-rc-from-main.png)

```
$ git log --oneline main
956a73b main: release v1.2.0
c2d38fc fix: 시간대 고정 (#421)
60a50d8 fix: 인코딩 고정 (#417)
916809b fix: 실험 기능 제외 (#412)
a0d7785 main: merge dev
d1bf164 feat: 실험 기능 (#405)      # QC 전에 이미 main 에 있었다
```

## 9. 직접 돌려보기

[git-repo-flow](https://github.com/NumeRealWorks/git-repo-flow)에 위 그래프를 그대로 만드는
스크립트가 들어 있다. 실제 저장소를 건드리지 않고 한 단계씩 재생할 수 있다.

| 스크립트 | 대응 |
|---|---|
| `01 절차 · 릴리스 한 바퀴` | 1~5절 |
| `02 절차 · 핫픽스` | 6절 |
| `03 실패 · 트렁크에 squash merge` | 7절 — **충돌로 끝난다** |
| `04 실패 · rc 를 dev 로 직접 되돌린다` | 8.1 |
| `05 실패 · QC 이슈를 dev 에 바로 넣는다` | 8.2 |
| `06 실패 · rc 를 main 에서 딴다` | 8.3 |
