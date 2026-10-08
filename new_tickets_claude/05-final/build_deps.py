#!/usr/bin/env python3
"""모듈 간 선행·충돌 계산.

  python3 build_deps.py --apply   03-items 의 `충돌:` 줄에 파일 교집합(항목·열린 PR)을 `B2 교집합:` 꼬리로 써 넣는다 (재실행 시 꼬리를 갈아 끼움)
  python3 build_deps.py           05-final/deps.md 생성 (표 · 선행 순환 · PR 대기 · 즉시 착수)
"""
import os, re, sys
from collections import OrderedDict, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from items_index import ROOT, MODS, load_items, load_open_prs, OPEN_PRS

TAIL = 'B2 교집합:'


BY_KEY = defaultdict(list)


def compute(items, prs):
    by_key = BY_KEY
    for it in items.values():
        for k in it['keys']:
            by_key[k].append(it['id'])
    conf = {i: OrderedDict() for i in items}          # id -> other id -> [files]
    for k in sorted(by_key):
        ids = by_key[k]
        for a in ids:
            for b in ids:
                if a != b:
                    conf[a].setdefault(b, []).append(k)
    pr_conf = {i: OrderedDict() for i in items}       # id -> pr -> [files]
    for it in items.values():
        for pr, files in prs.items():
            hit = sorted(it['keys'] & files)
            if hit:
                pr_conf[it['id']][pr] = hit
    return conf, pr_conf


HUB = 10  # 이 수 이상이 만지는 파일은 ID 를 나열하지 않고 deps.md 5절을 가리킨다


def tail_text(it, conf, pr_conf, by_key):
    """파일별로 묶는다 — `파일 → ID …`. 이미 `충돌:`·`선행:` 에 있는 ID 는 뺀다."""
    known = set(it['conf_ids']) | set(it['pre_ids'])
    per_file = OrderedDict()
    for other, files in conf[it['id']].items():
        if other in known: continue
        for f in files: per_file.setdefault(f, []).append(other)
    parts = []
    for f in sorted(per_file, key=lambda k: (-len(by_key[k]), k)):  # 결정적 순서 — 재실행 멱등
        if len(by_key[f]) >= HUB:
            parts.append(f"{f} → 공유 {len(by_key[f])}건(deps.md 5절)")
        else:
            parts.append(f"{f} → {' '.join(sorted(per_file[f]))}")
    known_pr = set(it['conf_prs']) | set(it['pre_prs'])
    for pr, files in pr_conf[it['id']].items():
        if pr not in known_pr:
            parts.append(f"PR #{pr}({'·'.join(files)})")
    return ' · '.join(parts)


def apply(items, conf, pr_conf):
    n = 0
    for mod in MODS:
        p = os.path.join(ROOT, '03-items', f'{mod}.md')
        lines = open(p, encoding='utf-8').read().split('\n')
        cur = None
        for i, ln in enumerate(lines):
            m = re.match(r'^###\s+([A-Z]{3}-\d{2,3})\b', ln)
            if m: cur = m.group(1)
            if ln.startswith('## 대응표'): cur = None
            if cur and ln.startswith('- 충돌:'):
                base = re.sub(r'\s*·?\s*' + re.escape(TAIL) + r'.*$', '', ln).rstrip()
                if base == '- 충돌:': base = '- 충돌: -'
                # 꼬리를 뗀 본문으로 다시 계산해야 재실행이 멱등이다
                it = items[cur]
                body = base[len('- 충돌:'):].strip()
                from items_index import ids_in, prs_in
                it['conf_ids'] = [x for x in ids_in(body) if x != cur]
                it['conf_prs'] = prs_in(body)
                t = tail_text(it, conf, pr_conf, BY_KEY)
                if t:
                    new = (f'- 충돌: {TAIL} {t}' if body == '-' else f'{base} · {TAIL} {t}')
                else:
                    new = base
                if new != ln:
                    lines[i] = new; n += 1
        open(p, 'w', encoding='utf-8').write('\n'.join(lines))
    return n


def find_cycles(items):
    graph = {i: [p for p in it['pre_ids'] if p in items] for i, it in items.items()}
    color = {i: 0 for i in items}; stack = []; cycles = []
    def dfs(u):
        color[u] = 1; stack.append(u)
        for v in graph[u]:
            if color[v] == 1:
                cycles.append(stack[stack.index(v):] + [v])
            elif color[v] == 0:
                dfs(v)
        stack.pop(); color[u] = 2
    for i in items:
        if color[i] == 0: dfs(i)
    return cycles


def main():
    items = load_items(); prs = load_open_prs()
    conf, pr_conf = compute(items, prs)
    if '--apply' in sys.argv:
        print('충돌 줄 갱신', apply(items, conf, pr_conf))
        return
    out = []
    out.append('# 모듈 간 선행·충돌 (B2)\n')
    out.append('> `python3 05-final/build_deps.py` 생성. 기준 03-items (dev @ b08a91b3). 충돌(항목) = `충돌:` 줄의 ID ∪ `변경 범위` 파일 교집합(basename 기준, 약칭 W/M/PM 등 해석). 충돌(PR) = `충돌:`·`선행:` 의 열린 PR ∪ 파일 교집합. 선행의 `PR #N` 은 머지 대기.\n')
    out.append('> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.\n')
    # 1. 표
    out.append('## 1. 항목별 선행 · 충돌\n')
    out.append('| 항목 | 종류 | 선행 | 충돌(항목) | 충돌(PR) |')
    out.append('|---|---|---|---|---|')
    pr_wait_pre = defaultdict(list); pr_wait_file = defaultdict(list); ready = []
    for i, it in items.items():
        pre = list(it['pre_ids']) + [f'PR #{p}' for p in it['pre_prs']]
        cids = sorted(set(it['conf_ids']) | set(conf[i].keys()))
        cprs = sorted(set(it['conf_prs']) | set(pr_conf[i].keys()) | set(it['pre_prs']), reverse=True)
        out.append(f"| {i} | {it['kind']} | {' '.join(pre) or '-'} | {' '.join(cids) or '-'} | {' '.join('#'+p for p in cprs) or '-'} |")
        for p in it['pre_prs']: pr_wait_pre[p].append(i)
        for p in set(it['conf_prs']) | set(pr_conf[i].keys()):
            if p not in it['pre_prs']: pr_wait_file[p].append(i)
        if not it['pre_ids'] and not it['pre_prs'] and not cprs:
            ready.append(i)
    # 2. 순환
    out.append('\n## 2. 선행 그래프 순환\n')
    cycles = find_cycles(items)
    if cycles:
        for c in cycles:
            out.append(f"- 순환: {' → '.join(c)}")
    else:
        out.append('- 순환 없음 (선행 그래프는 DAG).')
    bad = sorted({p for it in items.values() for p in it['pre_ids'] if p not in items})
    out.append(f"- 선행에 적혔으나 존재하지 않는 ID: {' '.join(bad) or '없음'}")
    # 3. PR 대기
    out.append('\n## 3. 열린 PR 머지 전 착수 불가\n')
    out.append('(a) `선행:` 에 PR 머지를 명시한 항목 — 머지 전 착수 불가. (b) 파일만 겹치는 항목 — 동시 수술 금지(1-2절)라 머지 후 리베이스 전제로 착수, 또는 PR 랜딩 뒤 착수.\n')
    for p in OPEN_PRS:
        a = sorted(set(pr_wait_pre[p])); b = sorted(set(pr_wait_file[p]) - set(a))
        out.append(f"### PR #{p} — 선행 명시 {len(a)} · 파일 겹침 {len(b)}")
        out.append(f"- (a) {' '.join(a) or '-'}")
        out.append(f"- (b) {' '.join(b) or '-'}")
    allwait = sorted({i for v in pr_wait_pre.values() for i in v} | {i for v in pr_wait_file.values() for i in v})
    out.append(f"\n합계(중복 제거): PR 대기 {len(allwait)} (선행 명시 {len({i for v in pr_wait_pre.values() for i in v})} · 파일 겹침만 {len(allwait) - len({i for v in pr_wait_pre.values() for i in v})})")
    # 4. 즉시 착수
    out.append('\n## 4. 즉시 착수 가능 — 선행 없음 · 열린 PR 과 파일 겹침 없음\n')
    bymod = defaultdict(list)
    for i in ready: bymod[items[i]['mod']].append(f"{i}({items[i]['kind']})")
    out.append(f"합계 {len(ready)} / {len(items)}\n")
    for m in MODS:
        if bymod[m]: out.append(f"- {m} ({len(bymod[m])}): {' '.join(bymod[m])}")
    # 5. 선행만 있고 PR 겹침 없는 항목 (참고)
    out.append(f'\n## 5. 파일 겹침 상위 파일 (충돌 꼬리가 "공유 N건" 으로 가리키는 허브 — {HUB}건 이상)\n')
    by_key = BY_KEY
    top = [kv for kv in sorted(by_key.items(), key=lambda kv: -len(kv[1])) if len(kv[1]) >= HUB]
    out.append('| 파일 | 항목 수 | 항목 |')
    out.append('|---|---|---|')
    for k, ids in top:
        out.append(f"| {k} | {len(ids)} | {' '.join(sorted(ids))} |")
    open(os.path.join(ROOT, '05-final', 'deps.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print(f"deps.md: items {len(items)} · 순환 {len(cycles)} · PR 대기 {len(allwait)} · 즉시 착수 {len(ready)}")


if __name__ == '__main__':
    main()
