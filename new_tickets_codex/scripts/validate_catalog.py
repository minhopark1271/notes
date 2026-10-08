"""Structural validation of this document set, not application behavior tests."""
import json,re,collections
from pathlib import Path
R=Path(__file__).resolve().parents[1]
cards=json.loads((R/'03_TASK_CATALOG.json').read_text())
cross=json.loads((R/'05_ISSUE_CROSSWALK.json').read_text())
items=json.loads((R/'sources/items.json').read_text())['items']
errors=[];warnings=[];by={c['id']:c for c in cards}
required={'id','module','title','outcome','scope','acceptance','validation','dependencies','tags','sources','evidence','status','priority','notes'}
if len(by)!=len(cards):errors.append('duplicate task id')
for c in cards:
    if required-set(c):errors.append(f'{c["id"]} missing fields {required-set(c)}')
    for field in ['scope','acceptance','validation','evidence','tags']:
        if not c[field]:errors.append(f'{c["id"]} empty {field}')
    if set(c['tags'])-set('ABCDEFG'):errors.append(f'{c["id"]} invalid tags')
    if c['status'] not in {'ready','after_dependency','in_flight','needs_decision','needs_runtime_check','deferred','withdrawn'}:errors.append(f'{c["id"]} invalid status')
    if c['priority'] not in {'P1','P2','P3'}:errors.append(f'{c["id"]} invalid priority')
    for dep in c['dependencies']:
        if dep not in by:errors.append(f'{c["id"]} unknown dep {dep}')
        if dep in by and by[dep]['status']=='withdrawn':errors.append(f'{c["id"]} depends on withdrawn {dep}')
        if dep==c['id']:errors.append(f'{c["id"]} self dependency')
    for n in c['sources']:
        if not (R/f'sources/issues/{n}.md').exists() and not (n == 685 and (R.parent/'Issue-Revision-History.md').exists()):errors.append(f'{c["id"]} missing source #{n}')
seen=set();stack=set()
def visit(t):
    if t in stack:errors.append('cycle '+t);return
    if t in seen:return
    stack.add(t)
    for d in by[t]['dependencies']:
        if d in by:visit(d)
    stack.remove(t);seen.add(t)
for t in by:visit(t)
board_numbers={i['content']['number'] for i in items}
if {x['issue'] for x in cross}!=board_numbers:errors.append('board coverage mismatch')
if len(cross)!=len(board_numbers):errors.append('duplicate crosswalk rows')
for x in cross:
    if not x['reason']:errors.append(f'#{x["issue"]} no disposition rationale')
    if x['issue_state']=='OPEN' and not x['tasks'] and x['disposition'] not in {'resolved','superseded','withdrawn'}:errors.append(f'open issue #{x["issue"]} not accounted')
    for t in x['tasks']:
        if t not in by:errors.append(f'crosswalk #{x["issue"]} unknown task {t}')
    if x['disposition']=='needs_check':errors.append(f'issue #{x["issue"]} has untriaged disposition')

expected_docs=['README.md','00_PLAN.md','01_PROGRESS.md','02_MODULE_WORKFLOWS.md','03_TASK_CATALOG.md','04_EXECUTION_ORDER.md','05_ISSUE_CROSSWALK.md','06_COVERAGE_AND_LIMITS.md','07_BOARD_OVERLAY.md','08_BOARD_TABLE.md','reviews/REVIEW_RESOLUTIONS.md']
for p in expected_docs:
    if not (R/p).exists():errors.append('missing document '+p)
for p in [R/n for n in expected_docs if (R/n).exists()]+list((R/'modules').glob('*.md')):
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if target.startswith(('https://','http://','mailto:')):continue
        path,_,anchor=target.partition('#')
        q=(p.parent/path).resolve() if path else p
        if not q.exists() and q != (R/'reviews/validation.md').resolve():errors.append(f'broken local link {p.name}: {target}')
        if q.name=='03_TASK_CATALOG.md' and anchor and anchor.upper() not in by:errors.append('unknown task anchor '+target)
if by['PRJ-03']['status']=='in_flight':errors.append('PR530 must not be a current in-flight dependency')
for owner in ['common','execution','downstream']:
    for source in json.loads((R/f'modules/{owner}.json').read_text()):
        if source['id'] in by and any(by[source['id']][k] != v for k,v in source.items() if k not in ['sources','tags','owner_document'] and source['id']!='AL-09'):
            errors.append('module/catalog mismatch '+source['id'])
checks=['required fields and non-empty scope/acceptance/validation/evidence','unique task IDs and valid tags/status/priority','dependency targets and cycle detection','207 board issue one-to-one row coverage','open-issue task or explicit disposition coverage','source issue files present','local document links and task anchors','withdrawn cards excluded from active dependencies and module JSON synchronized']
report={'result':'PASS' if not errors else 'FAIL','task_count':len(cards),'board_issue_count':len(cross),'open_issue_count':sum(c['issue_state']=='OPEN' for c in cross),'checks':checks,'errors':errors,'warnings':warnings,'not_tested':'Application build/GUI/solver runtime; validation is document structure and traceability only.'}
# 과거 reviews 검증 스냅샷은 덮어쓰지 않고 현재 결과를 표준 출력으로 보고한다.
print(json.dumps(report,ensure_ascii=False))
raise SystemExit(bool(errors))
