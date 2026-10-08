#!/usr/bin/env python3
"""02-claims · 03-items 정합 검사. 인자 없이 실행하면 요약을 stdout 에 쓴다.

검사 항목
- 열린 이슈 113건이 claims 원천 또는 items 흡수·대응표에 전부 나타나는가
- 결함 201건이 claims 원천에 전부 나타나는가 (판정 포함)
- items ID 중복 · 선행/충돌 참조가 존재하는 ID 인가
- claims 판정 분포 · 범위밖 이관 목록 (대상 모듈별)
- items 종류·규모·태그 분포
"""
import os, re, sys, glob
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODS = ['MOR','CAD','CON','DOE','LCH','PRE','BLD','RUN','ANA','OPT','PRJ','REN','EXE','PER','UIC','DEV']
ISSUE_RE = re.compile(r'#(\d{2,4})\b')
DEFECT_RE = re.compile(r'\b([A-Z]{3}-[DU]\d+)\b')
ITEM_RE = re.compile(r'^###\s+([A-Z]{3}-\d{2,3})\b')
CID_RE = re.compile(r'\b([A-Z]{3}-c\d{2,3})\b')

open_issues = {int(f[:-3]) for f in os.listdir(os.path.join(ROOT,'01-sources','open_issues'))}
defects = set()
for f in glob.glob(os.path.join(ROOT,'01-sources','defects','*.md')):
    defects |= set(DEFECT_RE.findall(open(f,encoding='utf-8').read()))

def split_row(ln):
    # 셀 안의 이스케이프 파이프(\\|)와 백틱 코드 안의 파이프는 구분자가 아니다
    s = ln.strip().strip('|')
    cells, buf, in_code, i = [], '', False, 0
    while i < len(s):
        ch = s[i]
        if ch == '`': in_code = not in_code
        if ch == '\\' and i + 1 < len(s) and s[i+1] == '|':
            buf += '|'; i += 2; continue
        if ch == '|' and not in_code:
            cells.append(buf.strip()); buf = ''
        else:
            buf += ch
        i += 1
    cells.append(buf.strip())
    return cells

# ---- claims
claims = {}            # cid -> dict
claim_issue_cov = defaultdict(set); claim_defect_cov = defaultdict(set)
verdicts = Counter(); out_of_scope = defaultdict(list)
for mod in MODS:
    p = os.path.join(ROOT,'02-claims',f'{mod}.md')
    if not os.path.exists(p): print(f'[claims] {mod}: 파일 없음'); continue
    for ln in open(p,encoding='utf-8'):
        if not ln.startswith('|'): continue
        cells = split_row(ln)
        if len(cells) < 5 or not CID_RE.match(cells[0]): continue
        cid = cells[0]; src = cells[3]; verdict = cells[4]
        claims[cid] = dict(mod=mod, src=src, verdict=verdict, row=cells)
        for n in ISSUE_RE.findall(src): claim_issue_cov[int(n)].add(cid)
        for d in DEFECT_RE.findall(src): claim_defect_cov[d].add(cid)
        verdicts[(mod, verdict.split()[0] if verdict else '')] += 1
        if verdict.startswith('범위밖'):
            blob = verdict + ' ' + (cells[5] if len(cells)>5 else '')
            m = re.search(r'→\s*([A-Z]{3})', blob)
            tgt = m.group(1) if m else None
            if tgt not in MODS:
                found = [x for x in MODS if re.search(r'\b'+x+r'\b', blob) and x != mod]
                tgt = '/'.join(found) if found else '?'
            out_of_scope[tgt].append((cid, mod, cells[1][:60]))

# ---- items
items = {}; item_issue_cov = defaultdict(set); item_defect_cov = defaultdict(set)
kinds = Counter(); sizes = Counter(); tags = Counter(); refs = []
for mod in MODS:
    p = os.path.join(ROOT,'03-items',f'{mod}.md')
    if not os.path.exists(p): print(f'[items] {mod}: 파일 없음'); continue
    cur = None
    for ln in open(p,encoding='utf-8'):
        m = ITEM_RE.match(ln)
        if m:
            cur = m.group(1)
            if cur in items: print(f'[items] 중복 ID {cur} ({mod})')
            items[cur] = dict(mod=mod, title=ln.strip()[4:], fields={})
            continue
        if cur and ln.startswith('- '):
            k, _, v = ln[2:].partition(':')
            k = k.strip(); v = v.strip()
            items[cur]['fields'][k] = v
            if k == '종류':
                for part in v.split('|'):
                    kk, _, vv = part.partition(':')
                    kk = kk.strip(); vv = vv.strip()
                    if kk == '종류': kinds[(mod, vv)] += 1
                    elif kk == '규모': sizes[(mod, vv)] += 1
                    elif kk == '태그':
                        for t in re.findall(r'\b[A-G]\b', vv): tags[t] += 1
            if k == '흡수':
                for n in ISSUE_RE.findall(v): item_issue_cov[int(n)].add(cur)
                for d in DEFECT_RE.findall(v): item_defect_cov[d].add(cur)
            if k in ('선행','충돌'):
                for r in re.findall(r'\b[A-Z]{3}-\d{2,3}\b', v): refs.append((cur, k, r))
        if ln.startswith('## 대응표'): cur = None
    # 대응표 rows also count as coverage
    txt = open(p,encoding='utf-8').read()
    tail = txt.split('## 대응표')[-1] if '## 대응표' in txt else ''
    for ln in tail.splitlines():
        if not ln.startswith('|'): continue
        for n in ISSUE_RE.findall(ln): item_issue_cov[int(n)].add(f'{mod}:대응표')
        for d in DEFECT_RE.findall(ln): item_defect_cov[d].add(f'{mod}:대응표')

# ---- report
print('== claims', len(claims), '| items', len(items))
print('\n== 판정 분포 (모듈, 판정)')
for (mod, v), c in sorted(verdicts.items()): print(f'  {mod:4} {v:8} {c}')
print('\n== items 종류 / 규모')
for (mod, v), c in sorted(kinds.items()): print(f'  {mod:4} {v:6} {c}')
for (mod, v), c in sorted(sizes.items()): print(f'  {mod:4} 규모 {v:3} {c}')
print('  태그', dict(tags))

miss_i_claim = sorted(open_issues - set(claim_issue_cov))
miss_i_item = sorted(open_issues - set(item_issue_cov))
print('\n== 열린 이슈 누락 — claims 원천에 없음:', miss_i_claim or '없음')
print('== 열린 이슈 누락 — items 흡수·대응표에 없음:', miss_i_item or '없음')
miss_d_claim = sorted(defects - set(claim_defect_cov))
print(f'\n== 결함 누락 — claims 원천에 없음 ({len(miss_d_claim)}):', ' '.join(miss_d_claim) or '없음')
miss_d_item = sorted(defects - set(item_defect_cov))
print(f'== 결함 누락 — items 흡수·대응표에 없음 ({len(miss_d_item)}):', ' '.join(miss_d_item) or '없음')

bad = [(i,k,r) for i,k,r in refs if r not in items]
print('\n== 선행/충돌 참조 중 존재하지 않는 ID:', bad or '없음')

# 범위밖 행이 다른 모듈 파일(claims 비고 "← CID" 또는 items 흡수)에 흡수됐는지 대조
alltext = {}
for mod in MODS:
    for sub in ('02-claims','03-items'):
        p = os.path.join(ROOT, sub, f'{mod}.md')
        if os.path.exists(p): alltext[(sub, mod)] = open(p, encoding='utf-8').read()
absorbed, unabsorbed = [], []
for tgt, rows in out_of_scope.items():
    for cid, mod, s in rows:
        hits = [f'{m}' for (sub, m), txt in alltext.items() if m != mod and re.search(r'(?<![A-Za-z0-9-])' + re.escape(cid) + r'(?![0-9])', txt)]
        (absorbed if hits else unabsorbed).append((cid, mod, tgt, sorted(set(hits)), s))
print(f'\n== 범위밖 이관 — 흡수됨 {len(absorbed)} · 미흡수 {len(unabsorbed)}')
for cid, mod, tgt, hits, s in unabsorbed:
    print(f'  미흡수 {cid:10} {mod:4} → {tgt:12} {s}')
if '-v' in sys.argv:
    for cid, mod, tgt, hits, s in absorbed:
        print(f'  흡수   {cid:10} {mod:4} → {tgt:12} by {",".join(hits)}')

no_kind = [i for i,d in items.items() if '종류' not in d['fields']]
if no_kind: print('\n== 종류 줄이 없는 항목:', no_kind)
