"""Build reviewable Markdown/JSON deliverables; no network or application mutation."""
import json, collections, re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(path): return json.loads((R/path).read_text())
def write(path,obj): (R/path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
states={'ready':'착수 가능','after_dependency':'선행 작업 후','in_flight':'PR 진행 중','needs_decision':'결정 필요','needs_runtime_check':'실측 필요','deferred':'보류','withdrawn':'철회 기록(실행 제외)'}
tags={'A':'데이터 무결성','B':'실행 모델','C':'데이터 모델·식별자','D':'UI 표준화','E':'코드 구조','F':'개발 인프라','G':'출고 품질'}
order=['geometry','execution','downstream','common']
cards=[]
for owner in order:
    for card in read(f'modules/{owner}.json'):
        card['owner_document']=f'modules/{owner}.md'
        cards.append(card)
byid={c['id']:c for c in cards}
aliases={'AST-002':'AL-09'}
# PR651 is one implementation/integration unit crossing two product modules.
src=byid['AST-002'];dst=byid['AL-09']
dst['title']='특수 입력 포맷의 Assets·Set·Launcher·fe-safe ODB 연결을 통합·검증한다'
dst['module']='Project Assets / Analysis Launcher 특수포맷'
dst['outcome']='dfsxml/wbpj/stli가 약정 복사 단위·Set 정책·실행 입력으로 등록되고 실행된다.'
for field in ['scope','acceptance','validation','sources','evidence','tags']:
    dst[field]=list(dict.fromkeys(src[field]+dst[field]))
dst['notes']='PR651 하나의 통합 작업이다. 담당 초안 AST-002(Assets)와 AL-09(실행)를 합쳤다. 실제 solver 검증은 아직 하지 않았다. 덮어쓰기 실패 안전성(AST-001)은 별도 잔여이며 해결됐다고 계산하지 않는다.'
cards=[c for c in cards if c['id'] not in aliases]
for c in cards:
    c['dependencies']=list(dict.fromkeys(aliases.get(d,d) for d in c['dependencies']))
    c['sources']=sorted(set(c['sources']))
    c['tags']=sorted(set(c['tags']))
byid={c['id']:c for c in cards}
write('03_TASK_CATALOG.json',cards)
# research의 과거 스냅샷은 재생성하지 않는다.

def link(id):return f'[{id}](#{id.lower()})'
def cell(text):return str(text).replace('|','\\|').replace('\n',' ')
def issue(n):return f'[#{n}](https://github.com/NumeRealWorks/DashOpti_GUI/issues/{n})'
def detail(c,level='##'):
    lines=[f'{level} {c["id"]}', '',f'**{c["title"]}**','',f'- 모듈: {c["module"]}',f'- 판정: {states[c["status"]]} · 제안 우선순위 {c["priority"]} · 측면 태그 {", ".join(c["tags"])}',f'- 사용자 결과: {c["outcome"]}',f'- 선행: {", ".join(c["dependencies"]) or "없음"}',f'- 기존 이슈: {", ".join(issue(n) for n in c["sources"]) or "코드 흐름 독립 조사에서 도출"}','', '**변경 범위**','']
    lines += ['- '+s for s in c['scope']]
    lines += ['', '**완료 조건**','']+['- '+s for s in c['acceptance']]
    lines += ['', '**검증 방법**','']+['- '+s for s in c['validation']]
    lines += ['', '**근거**','']+['- `'+s+'`' for s in c['evidence']]
    if c['notes']:lines+=['', '**범위·결정 메모**', '',c['notes']]
    return '\n'.join(lines)+'\n'

counts=collections.Counter(c['status'] for c in cards)
notice='> **2026-10-08 개정 반영** — [이슈 개정 이력](../Issue-Revision-History.md). 설계 반영과 구현 완료는 구분한다.'
text=['# 모듈별 새 작업 목록','',notice,'',f'코드 조사 기준: 2026-10-05, dev `b08a91b39bbdb7c3b75796ff2cd7f663d53258ef`. **{len(cards)}개 추적 단위(철회 기록 {sum(c["status"]=="withdrawn" for c in cards)}개 포함)**다. 확정 구현뿐 아니라 진행 PR·정책 결정·실측·보류 항목을 포함한다. 모든 항목이 즉시 만들 PR이라는 뜻이 아니다.','',
'각 작업은 하나의 일관된 변경/검증 결과를 목표로 한다. 규모가 크면 기록한 경계로 나눌 수 있고 같은 파일·완료 조건의 인접 작업은 합칠 수 있다. 다음 표의 수는 공수나 PR 개수의 약속이 아니다.','',
'PRJ-03은 #368 생산·공통 판독, PRJ-04는 #685 소비 전환으로 재정의했다. PRJ-05·IO-10·IO-11은 문서 내 철회 처분이며 실행 대상이 아니다. GitHub 상태 변경을 의미하지 않는다. #685는 과거 207개 보드 스냅샷 밖 후속 이슈다.','',
'현재 코드 근거는 조사 시점 정적 확인이다. 카드의 **검증 방법은 앞으로 수행할 완료 조건**이며 이번 조사에서 실행해 통과했다는 뜻이 아니다.','',
'기존 A~G는 복수 측면 태그다. 모듈 소속·우선순위·진행 상태와 독립이며, 태그 수를 점수/완성률로 사용하지 않는다.','',
'| 판정 | 개수 |','|---|---:|']
text += [f'| {states[k]} | {counts[k]} |' for k in states]
text += ['', '| 태그 | 측면 |','|---|---|']+[f'| {k} | {v} |' for k,v in tags.items()]
text+=['','## 전체 색인','','| ID | 모듈 | 작업 | 판정 | 순위 | 태그 |','|---|---|---|---|---|---|']
for c in cards:text.append(f'| {link(c["id"])} | {cell(c["module"])} | {cell(c["title"])} | {states[c["status"]]} | {c["priority"]} | {", ".join(c["tags"])} |')
text+=['','## 상세 작업 카드','']+[detail(c,'###') for c in cards]
(R/'03_TASK_CATALOG.md').write_text('\n'.join(text))
# 개정 범위의 모듈만 다시 만든다. geometry와 과거 조사 스냅샷은 보존한다.
for owner in ['common','execution','downstream']:
    title={'common':'공통 영역','geometry':'Geometry·CAD·Condition·Assets·VTK','execution':'DOE·Analysis Launcher·결과 처리','downstream':'Builder·Runner·Optimizer·Analyzer'}[owner]
    content=f'# {title} 작업 카드\n\n> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md). 설계 반영과 구현 완료는 구분한다.\n\n교차검토 반영본. 최종 통합 정본은 [전체 목록](../03_TASK_CATALOG.md)이다.\n\n'
    if owner=='geometry':content+='담당 초안 AST-002는 동일 PR651 작업인 [AL-09](../03_TASK_CATALOG.md#al-09)에 합쳤다. JSON 원본의 AST-002는 추적용으로만 남긴다.\n\n'
    content+='\n'.join(detail(c) for c in cards if c['owner_document']==f'modules/{owner}.md')
    (R/f'modules/{owner}.md').write_text(content)

# 2026-10-08 이후 모듈 JSON과 개정된 대응 JSON이 정본이다.
# research/sources의 과거 처분으로 현재 결정을 덮어쓰지 않는다.
cross=read('05_ISSUE_CROSSWALK.json')
items=read('sources/items.json')['items']
disp_labels={'mapped':'재정의 반영','partial':'일부 반영·범위 변경','resolved':'현재 코드 해결 확인','superseded':'새 구조로 대체','withdrawn':'철회','historical':'과거 이력 보존','needs_check':'확인 필요','cross_owner':'다른 담당 연결'}
x=['# 기존 보드 이슈 전수 대응','',notice,'',f'보드 {len(items)}개 전수. 열린 이슈 {sum(c["issue_state"]=="OPEN" for c in cross)}개. 2026-10-05 조사 당시 보드 상태·이슈 상태·close reason은 보존하고 설계 처분·관계는 2026-10-08 결정으로 갱신했다. 부모/자식·겹치는 요구는 다대다 연결이며 각 행을 별도 공수로 세지 않는다.','',
'`과거 이력 보존`은 이미 닫힌 이슈를 재발행하지 않았다는 처분이며 현재 코드 전체 재검증 완료의 뜻이 아니다. `현재 코드 해결 확인`은 구체 코드 근거를 대조한 경우다. 보드 밖 후속 #685 및 참고 #577/#584/#394/#407은 별도 소스이며 아래 207개 분모에 넣지 않았다.','',
'| 이슈 | 기존 제목 | 과거 보드 / 이슈 상태 | 처분 | 새 작업 | 근거·이유 |','|---|---|---|---|---|---|']
for c in cross:
    links=', '.join(f'[{t}](03_TASK_CATALOG.md#{t.lower()})' for t in c['tasks']) or '—'
    x.append(f'| {issue(c["issue"])} | {cell(c["title"])} | {c["board_status"]} / {c["issue_state"]} {c["state_reason"] or ""} | {disp_labels.get(c["disposition"],c["disposition"])} | {links} | {cell(c["reason"])} |')
x += ['', '## 보드 스냅샷 밖 후속', '', '[#685](https://github.com/NumeRealWorks/DashOpti_GUI/issues/685)는 #443 하위의 후속 이슈로 [PRJ-04](03_TASK_CATALOG.md#prj-04)에 연결한다. #368(PRJ-03)의 공통 출처 계약 뒤 Runner·Optimizer가 Builder setId를 저장·복원하고 산출물을 검증해 실행·조회·프리뷰에 사용한다. 위 207개 보드 분모와 과거 상태에는 추가하지 않았다.']
(R/'05_ISSUE_CROSSWALK.md').write_text('\n'.join(x)+'\n')

# Dependency layers are descriptive; policy/runtime/deferred gates still apply within a layer.
layers=[];remaining={t for t,c in byid.items() if c['status']!='withdrawn'};done=set()
while remaining:
    layer=sorted(t for t in remaining if set(byid[t]['dependencies']) <= done)
    if not layer:raise ValueError('Cycle or unknown dependency: '+str(remaining))
    layers.append(layer);done.update(layer);remaining.difference_update(layer)
schedule=['# 착수 순서와 병합 단위','',notice,'',
'현재 설계 순서는 #368(PRJ-03) → #685(PRJ-04)다. #650(PRJ-11 및 모듈 버전 카드)은 별도 작업이다. PRJ-05·IO-10·IO-11은 철회 기록으로 실행 단계에서 제외한다. #473(RUN-03)·#369(RUN-04)·개명 결함(PRJ-02)은 출처 전환을 기다리지 않는다. #444(AL-05)의 비용 확인·필요시 분리 후 #441의 재시작 복구(AL-06)를 진행한다.','',
'우선순위는 위험도 제안이며 기존 board Priority와 무관하다. 같은 파일을 바꾸는 작업은 별도 순서 조정이 필요하다. 아래 위상 단계는 논리적 선행 관계만 뜻하며 날짜/인력/공수를 산정하지 않았다.','',
'## 과거 조사 PR과 현재 착수 시 확인할 범위','',
'| PR | 새 추적 작업 | 주의 |','|---|---|---|',
'| #530 | 현재 실행 대상 아님 | 2026-10-07 조회에서 미병합 CLOSED. 옛 조합 핀 재이식 요구는 폐기하고 #368→#685 계약을 적용 |',
'| #651 | AL-09 | AST-002를 합쳤다. Assets+Launcher+fe-safe 한 PR이며 AST-001 실패 복구는 별도 |',
'| #652 | DIR-01 | Direct 입력 표 삭제 이후 UI-06 수정 범위 재확인 |',
'| #654 | GEO-001 | 구 형식 거부/새 핸들 상태기; GEO 후속은 통합 뒤 진행 |','',
'## 바로 착수할 수 있는 P1','']
for c in cards:
    if c['status']=='ready' and c['priority']=='P1':schedule.append(f'- [{c["id"]}](03_TASK_CATALOG.md#{c["id"].lower()}): {c["title"]}')
schedule+=['','## 선행 관계별 묶음','']
for index,layer in enumerate(layers):
    schedule += [f'### 단계 {index}', '',', '.join(f'[{t}](03_TASK_CATALOG.md#{t.lower()}) ({states[byid[t]["status"]]})' for t in layer),'']
schedule+=['## 충돌·합치기 판단','',
'- `DashMainWindow` / 프로젝트 전환: PRJ-01·06·07, AST-001/CON-001, UI-01~06은 큰 동시 변경을 피하고 작은 완료 묶음으로 순차 통합한다.',
'- `DashAnalysisLauncher` / result 처리: AL-01~08·RES-08~10·IO-03·IO-08은 같은 파일을 바꾼다. 구조 경계 정리와 worker 이관을 구분하되 수정량이 작은 소비자 치환은 묶어도 된다.',
'- 입력 질의: RES-03의 응답 식별 계약 뒤 RES-04/05를 진행한다. 별개의 Side Force/완료 신호 결함은 무조건 기다릴 이유가 없다.',
'- `Geometry/interaction`: GEO-001 이후 GEO-002/003, 그 뒤 생성기 작업. 값 모델과 renderer 소유권은 별도 완료 조건이다.',
'- 저장: IO-01을 적용 가능한 최소 계약으로 완성한 뒤 IO-02/03/04에 확산한다. 도메인 결함인 OPT-05·AL-02 등을 전체 persistence 이행 때문에 막지 않는다.',
'- 참조·출처: PRJ-03(#368) 생산 계약 뒤 PRJ-04(#685) 소비 전환을 진행한다. 현재 Set ID는 유지하고 상류 setId 참조 변경을 허용한다. 선택 변경만으로 출처를 수정하지 않고 재실행 덮어쓰기 때 실제 출처를 함께 갱신한다. 별도 대장과 전체 이력 보존은 요구하지 않는다.',
'- 버전·최신성: PRJ-11(#650)에서 의미·비교 불가·판정 규칙을 정의한 뒤 모듈별 적용을 진행한다. 생산 Set 기록, 소비 Set 판정, 프로젝트 호출·집계, VM 표시의 책임을 지킨다.',
'- 공통 규약: ASY-01/02와 UI-05는 실제 모듈 결함 수정의 무조건 선행이 아니다. 첫 소비와 함께 계약을 확정하고 나머지는 점진 적용한다.',
'- DEV-02/04/05는 외부 공급/실행 환경을 확인해야 한다. GUI PR 하나로 SDK 공급·외부 registry 작업까지 완료됐다고 표시하지 않는다.','',
'## 정책·실측 관문','']
for c in cards:
    if c['status'] in ['needs_decision','needs_runtime_check','deferred']:
        schedule.append(f'- [{c["id"]}](03_TASK_CATALOG.md#{c["id"].lower()}) — {states[c["status"]]}: {c["notes"]}')
(R/'04_EXECUTION_ORDER.md').write_text('\n'.join(schedule)+'\n')
print(json.dumps({'tasks':len(cards),'status':dict(counts),'board_issues':len(cross)},ensure_ascii=False))
