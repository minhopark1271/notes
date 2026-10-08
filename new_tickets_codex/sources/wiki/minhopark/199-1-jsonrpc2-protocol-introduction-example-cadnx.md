# JSON-RPC 2.0 가이드 — CadNx 케이스 최소 사용예

> 원본: 사전조사 Issue #199 — 본문을 이 페이지로 이관한 뒤 Issue 삭제 (2026-08-24). **본 페이지가 정본**
> 이관 주석: 아래 머리글의 `상태:` (Wiki 미연동·원격 미생성) 는 이관 전 시점 표기
> 미이관 참조: `cadnx-integration-architecture` · `cadnx-cpp-port-analysis` — 위키 미이관(Obsidian 로컬). 본문에서 백틱 표기로 남김

> 상태: 로컬 초안 (GitHub Issue / Wiki 미연동)
> 기반 문서: `cadnx-integration-architecture` — 특히 "7. 프로토콜 개선 제안" 절의 권장안(JSON-RPC 2.0 over JSON Lines)을 구체화한 실무 가이드
> 목적: JSON-RPC 2.0 명세의 핵심을 요약하고, 현행 CadNx 프로토콜(`loadPrt`/`updatePrtGeometry`/daemon)을 대입한 **가장 단순한 형태의 동작 예제**를 제공

---

## 개요

JSON-RPC 2.0은 "JSON으로 원격 호출(요청/응답/알림)을 표현하는 필드 규약"이다. 공식 명세([jsonrpc.org/specification](https://www.jsonrpc.org/specification))가 **7쪽** 분량으로, 전송(transport)과 프레이밍(메시지 경계)은 정의하지 않는다 — 그래서 stdio·소켓·HTTP 어디에나 얹을 수 있고, CadNx처럼 **stdin/stdout + JSON Lines(한 줄 = 메시지 하나)** 위에 얹는 것이 가장 단순한 조합이다.

라이브러리가 필요 없다. 아래 규약대로 JSON 필드를 채우고 `json.dumps`/`QJsonDocument`로 직렬화하면 그것이 곧 구현이다.

---

## 1. 명세 핵심 — 메시지는 3종뿐

### 1-1. Request (요청) — 응답을 기대함

```json
{"jsonrpc": "2.0", "id": 1, "method": "loadPrt", "params": {"prt": "C:\\a.prt", "out": "C:\\a.stp"}}
```

| 필드 | 규칙 |
|---|---|
| `jsonrpc` | 문자열 `"2.0"` 고정 (버전 식별) |
| `id` | 숫자 또는 문자열. **응답과 짝짓는 키.** 클라이언트가 부여(단조 증가 카운터면 충분). `null` 사용 지양 |
| `method` | 호출할 메서드 이름 (문자열). `rpc.` 접두는 예약어 |
| `params` | 객체(이름 기반) 또는 배열(위치 기반). **생략 가능.** 객체 형태 권장 |

### 1-2. Response (응답) — Request의 id를 되돌려줌

성공과 실패는 **상호 배타** — `result`와 `error`는 동시에 있을 수 없다.

```json
{"jsonrpc": "2.0", "id": 1, "result": {"step": "C:\\a.stp"}}
{"jsonrpc": "2.0", "id": 1, "error": {"code": -32001, "message": "NX session not available"}}
```

| 필드 | 규칙 |
|---|---|
| `id` | **대응하는 Request의 id 그대로** (파싱조차 불가능해 id를 모를 때만 `null`) |
| `result` | 성공 시. 임의의 JSON 값 |
| `error` | 실패 시. `{code(정수), message(문자열), data(선택)}` 구조 고정 |

### 1-3. Notification (알림) — `id` 없는 Request, 응답 금지

```json
{"jsonrpc": "2.0", "method": "log", "params": {"level": "debug", "msg": "SaveAs C:\\a.prt"}}
```

- `id`가 **없다**는 것이 유일한 차이. 수신 측은 절대 응답하지 않는다.
- 진행 로그·이벤트처럼 "던지고 잊는" 메시지에 사용 — 현행 `[GUI] ...` 로그 라인의 정확한 대체물.

### 1-4. 표준 에러 코드

| 코드 | 의미 | CadNx 관점 |
|---|---|---|
| -32700 | Parse error (JSON 자체가 깨짐) | 깨진 stdin 라인 |
| -32600 | Invalid Request (필드 규약 위반) | `method` 누락 등 |
| -32601 | Method not found | 오타 명령 |
| -32602 | Invalid params | Name/Value 길이 불일치 등 |
| -32603 | Internal error | 예기치 못한 예외 |
| **-32000 \~ -32099** | **Server error (구현 정의 예약 구간)** | **도메인 에러를 여기에 정의** (2-3 참조) |

### 1-5. 명세에 있지만 CadNx에 불필요한 것

- **Batch** (배열로 여러 요청 묶기): 순차 1명령 워크로드라 불필요. 채택하지 않으면 파서가 더 단순해진다.
- **위치 기반 params** (배열): 이름 기반(객체)만 쓰면 가독성·확장성이 낫다.

### 1-6. 프레이밍 — JSON Lines와의 결합

명세가 정하지 않는 "메시지 경계"는 JSON Lines로 해결한다: **한 줄 = 완전한 JSON 메시지 하나, 개행으로 구분.** 표준 직렬화기는 문자열 내 개행을 `\n`으로 이스케이프하므로 이 보장은 공짜다. 송신 측은 매 메시지 후 flush 필수 (현행 `PYTHONUNBUFFERED=1` 관례 유지).

---

## 2. CadNx 대입 — 메서드·에러 설계

### 2-1. 메서드 매핑 (현행 명령 → JSON-RPC)

| 현행 | JSON-RPC | 종류 | 방향 |
|---|---|---|---|
| daemon ready 감지 (`isReadyLine`) | `ready` | Notification | exe → GUI (기동 직후 1회, `version` 포함) |
| `loadPrt "<prt>" "<stp>"` | `loadPrt` | Request | GUI → exe |
| `updatePrtGeometry ... --config-json ... --no-cleanup` | `updatePrtGeometry` | Request | GUI → exe |
| `[GUI] ...` 로그 라인 | `log` | Notification | exe → GUI |
| `exit` | `shutdown` | Notification | GUI → exe |

### 2-2. params / result 스키마 (현행 계약 최대 보존)

`loadPrt` — 설계변수 JSON(Independent/Dependent 분류)을 `result`에 그대로 싣는다:

```json
// 요청
{"jsonrpc":"2.0","id":1,"method":"loadPrt","params":{"prt":"C:\\proj\\model.prt","out":"C:\\proj\\.configs\\model.stp"}}

// 성공 응답 — 현행 stdout JSON 한 줄이 result 필드로 이동
{"jsonrpc":"2.0","id":1,"result":{
  "designVariables":{
    "Independent Parameter":{"Name":["D_ratio","d","e_ratio"],"Part":["REF_SPRING","REF_SPRING","REF_SPRING"],"Type":["NX CAD","NX CAD","NX CAD"],"Value":[0.82,1.78,0.295]},
    "Dependent Parameter":{"Name":["L_total"],"Part":["REF_SPRING"],"Type":["NX CAD"],"Value":["d*12"]}
  },
  "step":"C:\\proj\\.configs\\model.stp"
}}
```

`updatePrtGeometry` — `--config-json`의 이중 이스케이프가 사라지고 params 안의 평범한 JSON 객체가 된다:

```json
// 요청 (현행 --no-cleanup 플래그는 params 필드로)
{"jsonrpc":"2.0","id":2,"method":"updatePrtGeometry","params":{
  "prt":"C:\\proj\\model.prt","out":"C:\\out\\run1.stp",
  "independent":{"Name":["D_ratio","d"],"Value":[0.85,1.80]},
  "noCleanup":true
}}

// 성공 응답
{"jsonrpc":"2.0","id":2,"result":{"step":"C:\\out\\run1.stp","tempPrt":"C:\\out\\run1.prt"}}
```

### 2-3. 도메인 에러 코드 (-32000번대, 현행 실패 케이스 대응)

| 코드 | 이름 | 현행 대응 |
|---|---|---|
| -32001 | NX_SESSION_UNAVAILABLE | `RuntimeError("NX session not available")` |
| -32002 | PRT_OPEN_FAILED | `Failed to open PRT` |
| -32003 | PARAM_CONTRACT_VIOLATION | Name/Value 길이 불일치·빈 리스트 (표준 -32602로 대체 가능) |
| -32004 | STEP_EXPORT_FAILED | export 후 STEP 미생성/크기 검증 실패 |

---

## 3. 지금 vs 개선안 — 같은 세션의 전체 왕복 비교

동일한 시나리오(기동 → loadPrt 성공 → updatePrtGeometry 실패 → 종료)를 현재 실제 구현(`DashExtensionProcess`/`DashSolverNxCad` 소스 기준)과 개선안으로 나란히 재현한다.

### 3-1. 지금 (Before) — 실제 stdin/stdout 왕복

```
[기동] GUI가 exe 실행: DashOptiCADNX.exe daemon --nx-base "C:\SIEMENS\NX2506"
   │   exe → [GUI] UGII_BASE_DIR=C:\SIEMENS\NX2506 ...
   │   ※ ready 판정 = 라인에 "[GUI]" 또는 "UGII_BASE_DIR" 포함 여부(isReadyLine) — 버전·상태 정보 없는 자유 형식 문자열 매칭
   ▼

[명령 1] loadPrt 왕복 — 성공 케이스
   │   GUI → loadPrt "C:\a.prt" "C:\a.stp"
   │      (quoteForStdin: 경로를 큰따옴표로 감싸고 내부 " 만 이스케이프한 CLI 인자 한 줄)
   │   exe → [GUI] Opening part...
   │   exe → {"designVariables":{"Independent Parameter":{...}},"step":"C:\\a.stp"}
   │      (완료 마커와 무관한 별도 채널 — tryParseJsonFromLine 이 라인마다 "{" 시작 여부·파싱 성공 여부를 계속 누적 시도)
   │   exe → [FINISHED]
   │   ※ 성공 판정은 이 문자열과의 정확한 일치(`trimmed == "[FINISHED]"`) 뿐. commandCompleted 의 output 인자는 실제로는 쓰이지 않고, GUI 는 stpPath 파일이 디스크에 실존하는지(`QFileInfo::exists`)로 성공을 다시 검증
   ▼

[명령 2] updatePrtGeometry 왕복 — 실패 케이스
   │   GUI → updatePrtGeometry "C:\a.prt" "C:\r1.stp" --config-json "{\"independent\":{\"Name\":[\"Typo_Name\"],\"Value\":[1.0]}}" --no-cleanup
   │      (--config-json 값은 JSON 문자열을 quoteJsonForStdin 으로 다시 한 번 이스케이프 — 이중 이스케이프 계층)
   │   exe → [GUI] [ERROR] STEP not created
   │   ※ 실패 판정은 라인 어디든 "[ERROR]" 포함(contains) 여부. 메시지 본문에 우연히 이 문자열이 섞여도 오판정될 수 있는 구조
   │   ※ 에러 후에도 데몬은 생존 — 다음 명령 계속 수신
   ▼

[종료] GUI → exit
       exe 가 5초 안에 안 죽으면 GUI 가 강제 kill() — 정상 종료 응답 규약 없음
```

### 3-2. 개선안 (After) — JSON-RPC 왕복

```
[기동] GUI가 exe 실행: DashOptiCADNX.exe daemon --nx-base "C:\SIEMENS\NX2506"
   │   exe → {"jsonrpc":"2.0","method":"ready","params":{"version":"1.0","nxBase":"C:\\SIEMENS\\NX2506"}}
   ▼

[명령 1] loadPrt 왕복 (id=1)
   │   GUI → {"jsonrpc":"2.0","id":1,"method":"loadPrt","params":{"prt":"C:\\a.prt","out":"C:\\a.stp"}}
   │   exe → {"jsonrpc":"2.0","method":"log","params":{"level":"info","msg":"Opening part..."}}
   │   exe → {"jsonrpc":"2.0","id":1,"result":{"designVariables":{...},"step":"C:\\a.stp"}}
   │   ※ id=1 응답 수신 = 현행 [FINISHED] 대체. result 도착 = 성공 확정
   ▼

[명령 2] updatePrtGeometry 왕복 — 실패 케이스 (id=2)
   │   GUI → {"jsonrpc":"2.0","id":2,"method":"updatePrtGeometry","params":{"prt":"C:\\a.prt","out":"C:\\r1.stp","independent":{"Name":["Typo_Name"],"Value":[1.0]}}}
   │   exe → {"jsonrpc":"2.0","id":2,"error":{"code":-32004,"message":"STEP not created","data":{"out":"C:\\r1.stp"}}}
   │   ※ 에러여도 데몬은 생존 — 다음 명령 계속 수신 (현행과 동일 규약)
   ▼

[종료] GUI → {"jsonrpc":"2.0","method":"shutdown"}
       exe는 응답 없이 정리 후 exit 0
```

핵심 관찰 3가지 (3-1 → 3-2 비교):

1. **성공/실패 판정이 문자열 매칭에서 필드 존재로** 바뀐다 — `result`냐 `error`냐. 현행 `[ERROR]` contains 매칭의 오판정 여지가 구조적으로 사라진다.
2. **로그는 id 없는 알림**이라 데이터·제어와 절대 섞이지 않는다.
3. **이스케이프 계층이 하나**다 — JSON 직렬화기만. shlex/quoteForStdin 호환 문제 소멸.

---

## 4. 최소 구현 스케치

### 4-1. Python 데몬 측 (\~40줄, 표준 라이브러리만)

현행 `main.py`의 daemon 루프(`shlex.split` → `cli.main`)를 대체하는 골격:

```python
import sys, json

def rpc_loadPrt(params):
    # 기존 load_prt 본체 호출 (nx_helpers 그대로 재사용)
    dv, step = do_load_prt(params["prt"], params["out"])
    return {"designVariables": dv, "step": step}

def rpc_updatePrtGeometry(params):
    step, temp = do_update(params["prt"], params["out"],
                           params["independent"], params.get("noCleanup", False))
    return {"step": step, "tempPrt": temp}

METHODS = {"loadPrt": rpc_loadPrt, "updatePrtGeometry": rpc_updatePrtGeometry}

def send(obj):
    print(json.dumps(obj, ensure_ascii=False), flush=True)   # flush 필수

def notify(method, params):
    send({"jsonrpc": "2.0", "method": method, "params": params})

def daemon_loop():
    notify("ready", {"version": "1.0"})
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            send({"jsonrpc": "2.0", "id": None,
                  "error": {"code": -32700, "message": f"Parse error: {e}"}})
            continue
        if msg.get("method") == "shutdown":          # 알림 — 응답 없이 종료
            return
        rid, name = msg.get("id"), msg.get("method")
        fn = METHODS.get(name)
        if fn is None:
            send({"jsonrpc": "2.0", "id": rid,
                  "error": {"code": -32601, "message": f"Method not found: {name}"}})
            continue
        try:
            send({"jsonrpc": "2.0", "id": rid, "result": fn(msg.get("params", {}))})
        except Exception as e:                        # 데몬 생존 규약 유지
            send({"jsonrpc": "2.0", "id": rid,
                  "error": {"code": -32000, "message": str(e)}})
```

주목할 점: click도 shlex도 등장하지 않는다. `try/except` 한 겹이 현행 "명령 실패해도 데몬 생존" 규약을 그대로 구현한다. NX 작업 함수(`nx_helpers.py`)는 무수정 재사용.

### 4-2. C++ GUI 측 핵심 (QProcess + QJsonDocument)

`DashExtensionProcess::handleDaemonLine`의 마커 분기를 대체하는 골격:

```cpp
// 송신 — quoteForStdin/quoteJsonForStdin 불필요
void sendRequest(int id, const QString& method, const QJsonObject& params) {
    QJsonObject msg{{"jsonrpc","2.0"},{"id",id},{"method",method},{"params",params}};
    m_process->write(QJsonDocument(msg).toJson(QJsonDocument::Compact) + "\n");
    m_pending.insert(id, method);   // id → 어떤 요청이었는지 기억
}

// 수신 — 한 줄 = 메시지 하나 (누적 버퍼·2MB 리셋 불필요)
void handleLine(const QByteArray& line) {
    const QJsonObject msg = QJsonDocument::fromJson(line).object();
    if (!msg.contains("id")) {                       // Notification
        if (msg["method"] == "ready")  emit daemonReady();
        if (msg["method"] == "log")    emit logLine(msg["params"]["msg"].toString());
        return;
    }
    const int id = msg["id"].toInt();                // Response
    const QString method = m_pending.take(id);
    if (msg.contains("error"))
        emit commandFailed(method, msg["error"]["message"].toString());
    else
        emit commandCompleted(method, msg["result"].toObject());
}
```

`isReadyLine`/`[FINISHED]`/`[ERROR]` contains 매칭·JSON 누적 파싱이 전부 사라지고, 기존 시그널 체계(`commandCompleted`/`commandFailed`/`logLine`)는 그대로 유지된다.

---

## 5. 현행 → JSON-RPC 이관 대응표 (요약)

| 현행 요소 | JSON-RPC 대체 | 검증 지점 |
|---|---|---|
| stdin CLI 문법 라인 + `shlex.split` | 한 줄 JSON Request | `tests/unit/test_daemon_protocol.py` 재작성 |
| `[FINISHED]` (라인 전체 일치) | `result` 응답 (id 짝) | `test_daemon_sequence.ps1`의 "정확히 2회" 단언 → "id 1·2 응답 각 1회" |
| `[GUI] [ERROR]` (contains 매칭) | `error` 객체 | `test_update_negative.ps1` — 깨진 입력 → -32700/-32602 |
| `[GUI]` 로그 | `log` Notification | — |
| ready 감지 휴리스틱 | `ready` Notification + `version` | 기동 타임아웃(120s) 규약은 동일 유지 |
| `--config-json` 이중 이스케이프 | params 내 일반 JSON 객체 | `quoteJsonForStdin` 삭제 |
| 파일 규약 (.stp 산출·temp .prt·batchMode 파일 폴링) | **변경 없음** — 프로토콜 층과 무관 | — |

---

## 6. 참고 자료

- JSON-RPC 2.0 공식 명세: https://www.jsonrpc.org/specification (7쪽)
- 채택 사례: LSP(Language Server Protocol)·DAP — JSON-RPC over stdio의 대규모 검증 사례
- `cadnx-integration-architecture` — 7절 "프로토콜 개선 제안" (본 가이드의 배경: 층위 분석·대안 비교·적용 시점 판단)
- `cadnx-cpp-port-analysis` — C++ 포팅 계획 (본 프로토콜 승급의 자연스러운 적용 시점)
