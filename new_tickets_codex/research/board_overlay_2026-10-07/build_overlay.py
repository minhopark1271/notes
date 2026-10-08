"""문서 스냅샷만 읽어 대응표와 검토용 작업 뷰를 생성한다. 외부 변경 없음."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATALOG = ROOT.parent.parent


def read(path):
    return json.loads(path.read_text())


def save(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def cell(value):
    if isinstance(value, list):
        value = ' / '.join(str(v) for v in value)
    return str(value).replace('|', '\\|').replace('\n', '<br>')


def links(ids):
    return ', '.join(f'[{i}](../../03_TASK_CATALOG.md#{i.lower()})' for i in ids) or '—'


inputs = read(ROOT / 'input_rows.json')
catalog = {t['id']: t for t in read(CATALOG / '03_TASK_CATALOG.json')}
reviews = []
for owner in ['geometry', 'execution', 'downstream']:
    part = read(ROOT / f'{owner}_mapping.json')
    if isinstance(part, dict):
        part = part.get('mappings', part.get('rows', []))
    reviews.extend(dict(r, reviewer=owner) for r in part)

errors = []
counts = Counter(r['issue'] for r in reviews)
expected = {r['issue'] for r in inputs}
if set(counts) != expected:
    errors.append(f'원본 대응 불일치: 누락={sorted(expected-set(counts))}, 추가={sorted(set(counts)-expected)}')
if any(n != 1 for n in counts.values()):
    errors.append('담당 간 이슈 중복')
relations = {'직접', '분할', '통합', '부모', '부분', '재판정', '제외'}
axes = {'손실방지', '정확성', '수명안정', '저장계약', '식별계약', '실행계약', '주변개선'}
for row in reviews:
    for key in ['task_ids', 'supporting_task_ids', 'relation', 'core_axes', 'proposed_scope', 'caveat', 'confidence']:
        if key not in row:
            errors.append(f"#{row['issue']} 필드 누락: {key}")
    if row.get('relation') not in relations:
        errors.append(f"#{row['issue']} 관계 값 오류")
    if not set(row.get('core_axes', [])).issubset(axes):
        errors.append(f"#{row['issue']} 핵심 축 값 오류")
    if not row.get('proposed_scope'):
        errors.append(f"#{row['issue']} 범위 설명 없음")
    primary = row.get('task_ids', [])
    secondary = row.get('supporting_task_ids', [])
    if set(primary) & set(secondary):
        errors.append(f"#{row['issue']} 주/보조 대응 중복")
    for task_id in primary + secondary:
        if task_id not in catalog:
            errors.append(f"#{row['issue']} 미존재 작업: {task_id}")

if errors:
    save('validation.json', {'result': 'FAIL', 'errors': errors})
    raise SystemExit('\n'.join(errors))

by_issue = {r['issue']: r for r in reviews}
snapshot = {r['number']: r for r in read(ROOT.parent / 'w4_review_2026-10-07/issues.json')}
rows = []
for source in inputs:
    issue = source['issue']
    row = {k: v for k, v in source.items() if k != 'baseline_crosswalk'}
    row.update(by_issue[issue])
    row['baseline_related_task_ids'] = (source.get('baseline_crosswalk') or {}).get('tasks', [])
    row['snapshot_2026_10_07'] = ({k: snapshot[issue][k] for k in ['state', 'updatedAt', 'parent', 'closedByPullRequestsReferences']} if issue in snapshot else None)
    row['input_url'] = f'https://github.com/NumeRealWorks/DashOpti_GUI/issues/{issue}'
    rows.append(row)
save('mapping.json', rows)

overlay = []
for task_id, task in catalog.items():
    direct = [r for r in rows if task_id in r['task_ids'] and r['relation'] not in ['부모', '제외']]
    parents = [r for r in rows if task_id in r['task_ids'] + r['supporting_task_ids'] and r['relation'] == '부모']
    supporting = [r for r in rows if task_id in r['supporting_task_ids'] and r['relation'] != '부모']
    if not (direct or parents or supporting):
        continue
    overlay.append({
        'task_id': task_id,
        'title': task['title'],
        'view_role': '범위 대조 대상' if direct else '묶음/관련 참조만',
        'catalog_status_2026_10_05': task['status'],
        'catalog_priority': task['priority'],
        'mapped_issues': [r['issue'] for r in direct],
        'parent_rollups': [r['issue'] for r in parents],
        'supporting_issues': [r['issue'] for r in supporting],
        'scope_proposals': [{'issue': r['issue'], 'relation': r['relation'], 'scope': r['proposed_scope'], 'caveat': r['caveat']} for r in direct],
        'catalog_definition': task,
        'conversion_note': '검토용 대응 뷰. 원본 카드 전체를 W4 범위로 가져오거나 새로 발행하라는 뜻이 아니다. source별 범위 제안은 이슈 전체를 설명할 수 있으므로 분할 대응은 카드별 범위를 다시 확인한다.',
    })
save('task_overlay.json', overlay)

lines = ['# board.txt 전수 대응표', '',
         '원본 62개 이슈의 계층·배정·상태·우선순위를 보존한다. 주된 대응도 반드시 완전 동등 범위는 아니다. `부분`·`재판정`과 주의사항을 함께 읽는다.', '',
         '**관계:** 직접=핵심 목표 대응, 분할=여러 작업으로 나눔, 통합=다른 이슈와 한 작업으로 모음, 부모=하위 완료 추적, 부분=일부만 겹침, 재판정=설계·병합 후 잔여 재확정, 제외=새 구현으로 변환하지 않음.', '',
         '`핵심 축`은 이번 대화의 6대 꼭지이며 기존 A~G 태그를 대체하지 않는다. `주변개선`은 6대 꼭지 밖의 기능·사용성·구조 개선이다.', '']
for row in rows:
    if row['board_row'] is not None:
        lines.extend([f"## 표시 {row['board_row']} · #{row['issue']} {row['title']}", ''])
    lines.extend([
        f"### [#{row['issue']}]({row['input_url']}) · {row['relation']}", '',
        f"- 원본: {row['iteration'] or '미배정'} / {row['status'] or '미기재'} / {row['board_priority'] or '우선순위 미기재'}",
        f"- 핵심 축: {cell(row['core_axes'])}",
        f"- 주된 대응: {links(row['task_ids'])}",
        f"- 보조 관련: {links(row['supporting_task_ids'])}",
        f"- 변환 범위: {cell(row['proposed_scope'])}",
        f"- 주의: {cell(row['caveat']) or '없음'}",
        f"- 대응 확신: {row['confidence']} (실행 성공 여부와 별개)", '',
    ])
lines += ['## 역방향: 기존 작업 위에 겹친 이슈', '',
          '행 수는 신규 PR 개수가 아니다. 관련 참조만 있는 카드는 실행 대상으로 자동 편입하지 않는다.', '',
          '| 기존 작업 | 직접 범위 대조 이슈 | 부모 묶음 | 보조 관련 |',
          '|---|---|---|---|']
for t in overlay:
    fmt = lambda nums: ', '.join(f'#{n}' for n in nums) or '—'
    lines.append(f"| {links([t['task_id']])} {cell(t['title'])} | {fmt(t['mapped_issues'])} | {fmt(t['parent_rollups'])} | {fmt(t['supporting_issues'])} |")
(ROOT / 'MAPPING.md').write_text('\n'.join(lines) + '\n')

result = {
    'result': 'PASS', 'source_issue_count': len(inputs), 'top_level_display_count': sum(r['board_row'] is not None for r in inputs),
    'mapped_issue_count': len(rows), 'relation_counts': dict(Counter(r['relation'] for r in rows)),
    'task_reference_count': len(overlay),
    'task_scope_comparison_count': sum(t['view_role'] == '범위 대조 대상' for t in overlay),
    'checks': ['62개 원본 전수/중복 없음', '모든 기존 작업 ID 유효', '주된 대응과 보조 관련 분리', '핵심 축 및 관계 값 검증', '원본 반복/상태/우선순위 무수정 보존'],
    'errors': [], 'limitations': ['구조와 참조 무결성 검사이며 범위 동등성의 자동 증명이 아니다.', '최신 코드 빌드/GUI/solver 실행 미수행.', '관련 문서의 상태/정책 차이는 caveat에 보존하고 원본을 덮어쓰지 않음.'],
}
save('validation.json', result)
print(json.dumps(result, ensure_ascii=False))
