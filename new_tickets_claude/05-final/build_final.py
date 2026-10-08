#!/usr/bin/env python3
"""03-items/*.md + 05-final/{deps,mapping}.md 를 05-final/FINAL.md 로 조립한다.

구성
1. 개요 — 기준·틀 요약·집계표(모듈 × 종류, 규모, 태그)
2. 모듈별 작업 목록 — 03-items 본문을 모듈 순서대로 (대응표 절은 제외)
3. 의존·충돌 — deps.md 본문
4. 대응표 — mapping.md 본문
"""
import os, re
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODS = [('MOR','Geometry Parameterization — Morphing'),('CAD','Geometry Parameterization — CAD'),
        ('CON','Condition Parameterization'),('DOE','DOE Sampler'),
        ('LCH','Analysis Launcher — Launcher·배치·Direct'),('PRE','Analysis Launcher — Preprocess·결과 처리'),
        ('BLD','Model Builder'),('RUN','Model Runner'),('ANA','Results Analyzer'),('OPT','Optimizer'),
        ('PRJ','Project · Set · Assets · Module Tree · 셸'),('REN','VTK 씬 · 렌더링'),
        ('EXE','실행 기반'),('PER','영속화 · 식별자'),('UIC','UI 공통'),('DEV','개발 환경 · 빌드 · CI · 출고')]
ITEM_RE = re.compile(r'^###\s+([A-Z]{3}-\d{2,3})\b')

def read(p):
    return open(p, encoding='utf-8').read() if os.path.exists(p) else ''

items_by_mod = {}; kinds = Counter(); sizes = Counter(); tags = Counter(); per_mod = defaultdict(Counter)
bodies = {}
for mod, _ in MODS:
    txt = read(os.path.join(ROOT, '03-items', f'{mod}.md'))
    body = txt.split('## 대응표')[0]
    # drop the leading H1 line
    body = re.sub(r'^#\s[^\n]*\n', '', body, count=1).strip()
    bodies[mod] = body
    n = 0
    cur = None
    for ln in txt.splitlines():
        m = ITEM_RE.match(ln)
        if m: cur = m.group(1); n += 1; continue
        if cur and ln.startswith('- 종류'):
            for part in ln[2:].split('|'):
                k, _, v = part.partition(':'); k = k.strip(); v = v.strip()
                if k == '종류': kinds[(mod, v)] += 1; per_mod[mod][v] += 1
                elif k == '규모': sizes[(mod, v)] += 1
                elif k == '태그':
                    for t in re.findall(r'\b[A-G]\b', v): tags[t] += 1
        if ln.startswith('## 대응표'): cur = None
    items_by_mod[mod] = n

KINDS = ['PR','DEC','INV','EXT','CLOSE']
out = []
out.append('# DashOpti_GUI 작업 목록 (재작성) — 모듈별\n')
out.append('> 기준: `dev` @ `b08a91b3` (2026-10-05). 원천: Projects #16 미종결 이슈 113건 · 결함 색인 201건 · 위키 설계 문서 · 현행 코드 대조. 틀·형식·과정은 `00-plan.md`.')
out.append('> 작업 단위: 모듈 1 · 기제 1 · 동작 변경과 리팩터 혼합 금지. 종류 PR / DEC(결정) / INV(실측 선행) / EXT(외부 저장소) / CLOSE(기존 이슈 닫기 제안). 규모 S/M/L 는 추정. 태그 A~G 는 구 분류 축(데이터 무결성 · 실행 모델 · 데이터 모델·식별자 · UI 표준화 · 코드 구조 · 개발 인프라 · 출고 품질).\n')
out.append('> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.\n')
out.append('## 1. 집계\n')
out.append('| MOD | 모듈 | 항목 | ' + ' | '.join(KINDS) + ' | S | M | L |')
out.append('|---|---|---|' + '---|' * (len(KINDS) + 3))
tot = Counter()
for mod, name in MODS:
    row = [mod, name, str(items_by_mod[mod])] + [str(per_mod[mod].get(k, 0)) for k in KINDS] + [str(sizes.get((mod, s), 0)) for s in 'SML']
    out.append('| ' + ' | '.join(row) + ' |')
    tot['n'] += items_by_mod[mod]
    for k in KINDS: tot[k] += per_mod[mod].get(k, 0)
    for s in 'SML': tot[s] += sizes.get((mod, s), 0)
out.append('| **합계** | | **' + str(tot['n']) + '** | ' + ' | '.join(str(tot[k]) for k in KINDS) + ' | ' + ' | '.join(str(tot[s]) for s in 'SML') + ' |')
out.append('')
out.append('태그 분포 (항목당 복수): ' + ' · '.join(f'{t} {tags[t]}' for t in 'ABCDEFG') + '\n')
out.append('## 2. 모듈별 작업 목록\n')
for mod, name in MODS:
    out.append(f'### {mod} — {name}\n')
    # demote item headings from ### to #### so module headings stay at ###
    body = re.sub(r'^###\s', '#### ', bodies[mod], flags=re.M)
    body = re.sub(r'^##\s', '##### ', body, flags=re.M)
    out.append(body + '\n')
deps = read(os.path.join(ROOT, '05-final', 'deps.md'))
mapping = read(os.path.join(ROOT, '05-final', 'mapping.md'))
out.append('## 3. 의존 · 충돌\n')
out.append(re.sub(r'^#\s[^\n]*\n', '', deps, count=1).strip() if deps else '(deps.md 없음)')
out.append('\n## 4. 대응표 (구 이슈 · 결함 → 새 항목)\n')
out.append(re.sub(r'^#\s[^\n]*\n', '', mapping, count=1).strip() if mapping else '(mapping.md 없음)')
open(os.path.join(ROOT, '05-final', 'FINAL.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('FINAL.md written —', tot['n'], 'items;', {k: tot[k] for k in KINDS})
