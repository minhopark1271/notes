# 트라이얼 릴리스 작업 배분

> 기반 문서: [[Cross-Module-Defect-Index]] · [[Cross-Module-Defect-Axis-Candidates]] · [[Cross-Module-Defect-Menifest-Axis]] · [[Code-Map-User-Flow]]
> 좌표 기준: 결함 건수는 색인 201건판(`cf44c25`), 공유 자원 건수는 206건판(재측정 안 됨 — 1절 주). 정적 근거만 — 빌드·실행 검증 없음
> 성격: 배분안. 결함 건수는 기반 문서의 실측이고, 구간·자원·작업 배정은 본 문서가 부여한 것이다

---

## 1. 모듈별 결함 수와 가중

| 구간 | 모듈 | 결함 | 공유 자원 |
|---|---|--:|---|
| 앞단 | Morphing 16 · CAD 20 · Condition 16 | **52** | 핸들·렌더 자원 16 · RW 세션 12 · NX 데몬 23 |
| 중단 | Analysis Launcher 29 · Data Preprocessor 15 | **44** | FE 솔버·런처 큐 11 · preprocessor DLL 9 |
| 뒷단 | Model Builder 17 · Model Runner 43 · Results Analyzer 19 · Optimizer 26 | **105** | 외부 학습·최적화 exe 13 |

**건수는 균등 배분의 근거가 못 된다.** 뒷단 105건 중 죽은 코드가 상당수이고(RUN-U1\~U6 6건 · ANA-U1·U2·U3·U5 4건 · OPT-U2), 죽은 코드는 삭제 판정이라 건당 비용이 왕복 결함의 몇 분의 일이다. 반대로 앞단 52건은 핸들 싱글턴과 RW 액터라는 **가장 두꺼운 공유 자원 2종** 을 통과한다.

201건판에서 줄어든 것은 앞단뿐이다(57→52) — 제외된 예정 기능 갈래 11건 중 8건이 Morphing·CAD·Condition 의 미착수 UI 였다. 중단·뒷단은 제외와 신설이 상계돼 총량이 그대로다. 공유 자원 열은 [[Cross-Module-Defect-Axis-Candidates]] 4장의 206건판 측정값이고, 그 문서가 자원별 ID 목록을 열거하지 않아 이번에 재측정하지 않았다.

---

## 2. 3인 배분

| 담당 | 구간 | 소유 모듈 | 소유 공유 자원 | 결함 | 주 작업 |
|---|---|---|---|--:|---|
| **A** | 앞단 — 형상·조건 | Morphing · CAD · Condition | 핸들·렌더 자원 · RW 세션·액터 · NX 데몬 | 52 | T2 진입·재진입 크래시 봉인 · T3 모핑 핸들 인덱스 · T11 Set 전환·삭제 정리 계약(앞단분) · T14 요청↔완료 상관자(NX) · T22 소유 경계 |
| **B** | 중단 — 실행·데이터·플롯 | Analysis Launcher · Data Preprocessor · Results Analyzer | FE 솔버·런처 큐 · preprocessor DLL · 민감도 데몬 | 63 | T10 설정 왕복 복구(중단분) · T15 프리즈 구간 제거 · T19 실행 모델 전환 잔여 · T26 `DashJobRunner` 분기 해체 · T13 판정 규칙(파일명 스키마) |
| **C** | 뒷단 — 학습·예측·최적화 | Model Builder · Model Runner · Optimizer | 외부 학습·최적화 exe | 86 | T10 설정 왕복 복구(뒷단분) · T12 정본 이중화 해소 · T13 판정 규칙(헤더·차원) · T23 배선 완결성 |

Results Analyzer 19건을 B 에 둔 근거 — 패널이 6곳에 임베드되지만 파일 실체는 `view/analyzer/` 하나이고, 민감도 3종이 쓰는 상주 데몬이 B 의 자원 목록에 이미 있다. 이에 따라 Model Runner 의 민감도 축 5건(RUN-D29 · D30 · D31 · D32 · D37)도 C 가 아니라 **B 로 넘긴다** — 같은 데몬·같은 폴더 열거 문제다. 조정 후 실질은 A 52 · B 68 · C 81 다.

A 의 주 작업에서 **T5(미구현 UI 판정)가 빠졌다** — 그 대상이던 앞단 미착수 UI 8건이 201건판에서 예정 기능 갈래로 제외됐다. 판정이 필요한 것은 결함 목록이 아니라 릴리스 범위 결정이므로 이 배분표 밖이다.

---
