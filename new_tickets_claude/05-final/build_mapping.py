#!/usr/bin/env python3
"""05-final/mapping.md 생성 — (a) 열린 이슈 113 + 보드 밖 4건(#552 #404 #394 #577) → 항목 · (b) 결함 201 → 항목 또는 판정."""
import os, re, sys, glob
from collections import OrderedDict, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from items_index import ROOT, MODS, load_items

DEFECT_RE = re.compile(r'\b([A-Z]{3}-[DU]\d+)\b')
CID_RE = re.compile(r'\b([A-Z]{3}-c\d{2,3})\b')
ISSUE_RE = re.compile(r'#(\d{2,4})\b')
# 보드 밖 OPEN 이슈 — 검토가 집어낸 4건만 편입 (decisions.md ⑨, 사용자 결정 2026-10-06). 나머지 22건은 01-sources/open_issues_offboard.md 에만.
EXTRA_ISSUES = {552: 'DashAsyncJobContext 취소 불가 — 보드 밖 OPEN (#553 선행)',
                404: 'Analyzer: "(std)" 축약이 표준편차가 아니라 최댓값으로 조용히 떨어진다 — 보드 밖 OPEN (#405 선행)',
                394: 'SaveProjectAs 가 모든 실패를 무시하고 true 를 반환하는 문제 — 보드 밖 OPEN',
                577: 'fix(view): Volume 핸들 생성기 — cylinder 삭제, Hexahedron 은 mesh-ops BoxHandles FFD 로 신규 — 보드 밖 OPEN'}


def split_row(ln):
    s = ln.strip().strip('|'); cells, buf, in_code, i = [], '', False, 0
    while i < len(s):
        ch = s[i]
        if ch == '`': in_code = not in_code
        if ch == '\\' and i + 1 < len(s) and s[i+1] == '|': buf += '|'; i += 2; continue
        if ch == '|' and not in_code: cells.append(buf.strip()); buf = ''
        else: buf += ch
        i += 1
    cells.append(buf.strip()); return cells


def load_claims():
    claims = OrderedDict()
    for mod in MODS:
        p = os.path.join(ROOT, '02-claims', f'{mod}.md')
        for ln in open(p, encoding='utf-8'):
            if not ln.startswith('|'): continue
            c = split_row(ln)
            if len(c) >= 5 and CID_RE.match(c[0]):
                claims[c[0]] = dict(mod=mod, src=c[3], verdict=c[4], note=c[5] if len(c) > 5 else '', what=c[1])
    return claims


def load_issues():
    issues = OrderedDict()
    for f in sorted(glob.glob(os.path.join(ROOT, '01-sources', 'open_issues', '*.md')), key=lambda x: int(os.path.basename(x)[:-3])):
        n = int(os.path.basename(f)[:-3]); title = ''; state = ''
        for ln in open(f, encoding='utf-8'):
            if ln.startswith('# '): title = re.sub(r'^#\s*#\d+\s*', '', ln.strip())
            if ln.startswith('- gh-state:'): state = ln.split(':', 1)[1].strip()
            if title and state: break
        issues[n] = (title, state)
    return issues


def load_defects():
    defects = OrderedDict()
    for f in sorted(glob.glob(os.path.join(ROOT, '01-sources', 'defects', '*.md'))):
        for ln in open(f, encoding='utf-8'):
            if not ln.startswith('|'): continue
            c = split_row(ln)
            did = c[1].strip('* ') if len(c) > 1 else ''   # 색인은 `**ID**` 로 적는다
            if len(c) >= 3 and DEFECT_RE.fullmatch(did):
                summary = c[2][:70]
                # 요약을 자르며 열린 코드 표기가 남으면 표 셀 경계를 닫는다.
                defects[did] = summary + ('`' if summary.count('`') % 2 else '')
    return defects


def assign_table():
    """00-plan 6절 — 이슈 → 주 모듈."""
    owner = {}
    txt = open(os.path.join(ROOT, '00-plan.md'), encoding='utf-8').read()
    sec = txt.split('## 6. 모듈별 담당 이슈 배정')[1]
    for ln in sec.splitlines():
        c = split_row(ln) if ln.startswith('|') else None
        if c and c[0] in MODS:
            for n in ISSUE_RE.findall(c[1]): owner[int(n)] = c[0]
    return owner


def main():
    items = load_items(); claims = load_claims(); issues = load_issues(); defects = load_defects(); owner = assign_table()
    for n, t in EXTRA_ISSUES.items(): issues[n] = (t, 'OPEN(보드 밖)')
    # 2026-10-08 확정 범위만 갱신한다. 원천 snapshot의 상태·완료 이력은 보존한다.
    current_titles = {
        368: '출처 기록과 공통 판독 계약', 443: 'Set 입력 참조',
        473: '결과 항목 조작 오류 수정', 474: '표 행과 항목 연결',
        475: '예측 결과 덮어쓰기 방지', 477: '삭제와 파일 해석',
        444: 'Set 기록 분리 — 비용 검증 후 조건부', 441: '상태 기록과 재시작 복구',
        369: 'NodeSet 선택 저장 — 독립 작업', 650: '산출물 버전과 최신성',
        470: '출처 추적 상위 목표 유지', 471: '독립 산출물·소비 대장 취소 유지',
    }
    for n, title in current_titles.items():
        if n in issues: issues[n] = (title, issues[n][1])
    # 역색인
    issue_items = defaultdict(list); defect_items = defaultdict(list); cid_items = defaultdict(list)
    for i, it in items.items():
        ab = it['fields'].get('흡수', '')
        for n in ISSUE_RE.findall(ab): issue_items[int(n)].append(i)
        for d in DEFECT_RE.findall(ab): defect_items[d].append(i)
        for c in CID_RE.findall(ab): cid_items[c].append(i)
    # 역사적 흡수 행을 현재 이슈의 완료 범위로 다시 확장하지 않는다.
    issue_items[368] = ['PER-06', 'PER-07', 'DOE-16', 'LCH-33', 'PRE-32', 'BLD-20']
    issue_items[443] = issue_items[368] + ['RUN-34', 'OPT-26']
    issue_items[470] = ['PER-09']
    issue_items[471] = ['PER-11']
    defect_claims = defaultdict(list)
    for c, cl in claims.items():
        for d in DEFECT_RE.findall(cl['src']): defect_claims[d].append(c)
    # 대응표 행 (항목 없음 사유)
    map_rows = defaultdict(list)
    for mod in MODS:
        txt = open(os.path.join(ROOT, '03-items', f'{mod}.md'), encoding='utf-8').read()
        tail = txt.split('## 대응표')[-1] if '## 대응표' in txt else ''
        for ln in tail.splitlines():
            if not ln.startswith('|'): continue
            c = split_row(ln)
            if len(c) >= 2:
                for n in ISSUE_RE.findall(c[0]): map_rows[int(n)].append((mod, c[1], c[2] if len(c) > 2 else ''))

    out = ['# 대응표 (B2)\n', '> `python3 05-final/build_mapping.py` 생성. 항목 = 03-items `흡수:` 에 원천이 적힌 항목. CLOSE 는 항목 제목이 닫기 사유.\n']
    out.append('> **2026-10-08 개정 반영** — [이슈 개정 이력](../../Issue-Revision-History.md)의 반영된 결정에 맞췄다. 추가 개정 계획은 팀 논의 사항으로 구분한다.\n')
    # (a)
    out.append(f'## (a) 열린 이슈 {len(issues)}건 → 항목\n')
    out.append('| 이슈 | 제목 | 주 모듈 | 항목 | 비고 |'); out.append('|---|---|---|---|---|')
    stat = defaultdict(int)
    for n, (title, state) in issues.items():
        ids = sorted(set(issue_items[n]), key=lambda x: (MODS.index(x[:3]), x))
        closes = [i for i in ids if items[i]['kind'] == 'CLOSE']
        work = [i for i in ids if items[i]['kind'] != 'CLOSE']
        note = ''
        if closes and not work:
            note = 'CLOSE — ' + '; '.join(re.sub(r'^#\d+\s*', '', items[i]['title']) for i in closes); stat['CLOSE'] += 1
        elif closes:
            note = 'CLOSE(부모/본체) + 잔여 항목 — ' + '; '.join(re.sub(r'^#\d+\s*', '', items[i]['title']) for i in closes); stat['CLOSE+잔여'] += 1
        elif work:
            stat['항목'] += 1
        else:
            rows = map_rows.get(n, [])
            note = ' / '.join(f"{m}: {a} {b}".strip() for m, a, b in rows)[:200] or '대응표 행 없음'; stat['항목 없음'] += 1
        if state and state != 'OPEN': note = (note + ' · ' if note else '') + f'gh-state {state}'
        own = owner.get(n) or (ids[0][:3] if ids else '-')   # 보드 밖 이슈는 배정표에 없다 — 첫 항목의 모듈
        out.append(f"| #{n} | {title[:60]} | {own} | {' '.join(ids) or '항목 없음'} | {note} |")
    out.append(f"\n집계: 작업 항목 {stat['항목']} · CLOSE {stat['CLOSE']} · CLOSE+잔여 {stat['CLOSE+잔여']} · 항목 없음 {stat['항목 없음']}\n")
    out.append('## (a-1) 원천 보드 snapshot 이후 확정된 소비 계약\n')
    out.append('| 이슈 | 항목 | 현재 범위 |')
    out.append('|---|---|---|')
    out.append('| #685 | RUN-34 · OPT-26 (OPT-15 저장 접점) | #443 하위. #368 생산·공통 계약 선행, Builder setId 참조·검증·실행·조회·프리뷰. #681 머지 조건 아님 |\n')
    out.append('위 (a)의 보드 수·gh-state는 당시 수집 기록이다. #443은 별도 Set 원장 구축을 요구하지 않고 #444·#369를 하위에서 분리한다. #444는 #441 하위, #473은 참조 전환과 독립이며 #470은 유지한다. 추가 개정 계획의 보드 정리·종료 후보는 이 표에서 실행하지 않는다.\n')
    # (b)
    out.append(f'## (b) 결함 {len(defects)}건 → 항목 또는 판정\n')
    out.append('| 결함 | 색인 요약 | 항목 | 판정 · 근거 CID |'); out.append('|---|---|---|---|')
    dstat = defaultdict(int)
    for d, summary in defects.items():
        ids = sorted(set(defect_items[d]), key=lambda x: (MODS.index(x[:3]), x))
        cids = defect_claims.get(d, [])
        # 범위밖 CID 가 B1 에서 타 모듈 항목에 흡수된 경우
        via = sorted({i for c in cids for i in cid_items.get(c, []) if i not in ids}, key=lambda x: (MODS.index(x[:3]), x))
        verdicts = []
        for c in cids:
            v = claims[c]['verdict'].split()[0]
            verdicts.append(f"{v}({c})")
        if ids:
            kind = 'CLOSE' if all(items[i]['kind'] == 'CLOSE' for i in ids) else '항목'
            dstat[kind] += 1
            out.append(f"| {d} | {summary} | {' '.join(ids)} | {' '.join(verdicts)} |")
        elif via:
            dstat['항목(CID 경유)'] += 1
            out.append(f"| {d} | {summary} | {' '.join(via)} | CID 경유 — {' '.join(verdicts)} |")
        else:
            vs = {v.split('(')[0] for v in verdicts}
            key = '해소됨' if vs == {'해소됨'} else ('미확인' if '미확인' in vs else '/'.join(sorted(vs)) or '?')
            dstat[key] += 1
            out.append(f"| {d} | {summary} | 항목 없음 | {' '.join(verdicts) or 'claims 없음'} |")
    out.append('\n집계: ' + ' · '.join(f'{k} {v}' for k, v in sorted(dstat.items(), key=lambda kv: -kv[1])) + '\n')
    open(os.path.join(ROOT, '05-final', 'mapping.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print('mapping.md:', dict(stat), dict(dstat))


if __name__ == '__main__':
    main()
