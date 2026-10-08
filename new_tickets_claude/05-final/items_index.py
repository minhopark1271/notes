#!/usr/bin/env python3
"""03-items 파서 — 항목 블록을 구조화하고 `변경 범위` 를 파일 집합으로 푼다.

build_deps.py · build_mapping.py 가 import 한다. 단독 실행(`--dump`)은 항목 요약을 stdout 에 쓴다.
"""
import os, re, sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODS = ['MOR','CAD','CON','DOE','LCH','PRE','BLD','RUN','ANA','OPT','PRJ','REN','EXE','PER','UIC','DEV']
ITEM_RE = re.compile(r'^###\s+([A-Z]{3}-\d{2,3})\s*·\s*(.*)')
ID_RE = re.compile(r'\b([A-Z]{3}-\d{2,3})\b')
PR_RE = re.compile(r'#(\d{3})\b')
EXT = r'(?:cpp|h|hpp|ui|txt|md|py|cmake|json|qrc|yml|yaml|sh|in|cfg|toml|ts)'

# 모듈별 약칭 (02-claims 머리말과 03-items 머리말 기준)
ABBR = {
    'RUN': {'W': 'view/DashModelRunnerWidget.cpp', 'M': 'model/DashModelRunner.cpp',
            'PM': 'viewmodel/DashModelRunnerPresentationModel.cpp', 'MW': 'view/DashModelRunnerMCUWidget.cpp',
            'AW': 'view/DashResultsAnalyzerWidget.cpp'},
    'OPT': {'W': 'view/DashOptimizerWidget.cpp', 'Wh': 'view/DashOptimizerWidget.h',
            'M': 'model/DashOptimizer.cpp', 'Mh': 'model/DashOptimizer.h',
            'PM': 'viewmodel/DashOptimizerPresentationModel.cpp'},
    'BLD': {'M': 'model/DashModelBuilder.cpp', 'MCU': 'model/DashModelBuilderMCU.cpp',
            'W': 'view/DashModelBuilderWidget.cpp', 'MW': 'view/DashModelBuilderMCUWidget.cpp',
            'Base': 'view/DashModelBuilderWidgetBase.cpp', 'PM': 'viewmodel/DashModelBuilderPresentationModel.cpp',
            'CH': 'model/builder/ModelBuilderConfigHelper.cpp', 'LTH': 'model/builder/ModelBuilderLabelTableHelper.cpp'},
}
DIRS = r'(?:view|model|controller|viewmodel|utils|persistence|libs|ui|tests|scripts|cmake|docs|tools|resources)'


def norm_key(path):
    """충돌 비교 키 — 디렉터리 없는 표기와 맞추기 위해 basename. CMakeLists.txt 만 경로 유지."""
    b = path.rsplit('/', 1)[-1]
    if b == 'CMakeLists.txt':
        return path if '/' in path else 'CMakeLists.txt'
    return b


def expand(tok):
    """`X.cpp/.h` · `X.{h,cpp}` · `{A,B}.h` · `X.*` · `X.cpp` 를 파일 목록으로."""
    tok = tok.strip('`\'"').replace('*.', '.')  # `X*.cpp` 는 X.cpp 로 본다
    m = re.search(r'\{([^{}]+)\}', tok)       # `X.{h,cpp}` · `{A,B}.h`
    if m:
        out = []
        for alt in m.group(1).split(','):
            out += expand(tok[:m.start()] + alt + tok[m.end():])
        return out
    m = re.match(r'^(.*)\.(' + EXT + r')/\.(' + EXT + r')$', tok)
    if m:
        return [f'{m.group(1)}.{m.group(2)}', f'{m.group(1)}.{m.group(3)}']
    m = re.match(r'^(.*)\.\*$', tok)
    if m:
        return [f'{m.group(1)}.cpp', f'{m.group(1)}.h']
    if re.match(r'^.*\.' + EXT + r'$', tok):
        return [tok]
    return []


def parse_files(mod, text):
    files = OrderedDict()
    abbr = ABBR.get(mod, {})
    # 1) 확장자 있는 경로 토큰
    for tok in re.findall(r'[A-Za-z0-9_][A-Za-z0-9_/.{},*-]*\.(?:\{[a-z,]+\}|\*|' + EXT + r'(?:/\.' + EXT + r')?)', text):
        tok = tok.rstrip('.,')
        for f in expand(tok):
            root = f.rsplit('/', 1)[-1].split('.')[0]
            if root in abbr:  # `M.h` `W.cpp/.h` 같은 약칭+확장자
                base = abbr[root].rsplit('.', 1)[0]
                f = base + '.' + f.rsplit('.', 1)[1]
            files[f] = True
    # 2) 디렉터리는 있고 확장자 없는 토큰 → .cpp
    for tok in re.findall(r'(?<![\w/.])(' + DIRS + r'/[A-Za-z0-9_/]+)(?![\w/.])', text):
        if tok.endswith('/') or tok.split('/')[-1] in ('', 'builder', 'async', 'common', 'overlay', 'dialog', 'preprocessor', 'analyzer', 'geometry', 'extensions', 'log'):
            continue
        if tok.split('/')[-1][0].islower() and '/' in tok and tok.split('/')[-1] not in ('main',):
            continue
        files.setdefault(tok + '.cpp', True)
    # 3) 모듈 약칭 (`W` `Wh` `M:` `PM` ...)
    for tok in re.findall(r'(?<![\w/.`])([A-Za-z]{1,4})(?=[\s:,·()]|$)', text):
        if tok in abbr:
            files.setdefault(abbr[tok], True)
    return list(files)


# #530 은 머지하지 않는다 (decisions.md ②) — 재업로드 노선이라 '머지 대기' 대상이 아니다.
OPEN_PRS = ('658', '656', '655', '654', '652', '651')
PR_ALIAS = {'430-handle-sets-render': '655', '433-launcher-common': '656', 'registry-82-consumer-adaptation': '658', 'feat/616': '651',
            'input-format-policy': '651', 'feat/604': '652', 'direct-launch-dialog': '652', '332-handle-state': '654'}
RANGE_RE = re.compile(r'\b([A-Z]{3})-(\d{2,3})\s*~\s*(?:\1-)?(\d{2,3})\b')


def strip_parens(text):
    """`(…)` 안은 조건·설명이지 선행이 아니다 (PRE-14 `- (PER-02 헬퍼가 먼저 랜딩하면 …)` 사례). 중첩 괄호도 벗긴다."""
    prev = None
    while prev != text:
        prev, text = text, re.sub(r'\([^()]*\)', ' ', text)
    return text


def ids_in(text):
    """`ANA-05 ~ ANA-15` 같은 범위 표기도 펼친다."""
    out = []
    for mod, a, b in RANGE_RE.findall(text):
        for n in range(int(a), int(b) + 1):
            out.append(f'{mod}-{n:02d}')
    out += ID_RE.findall(text)
    seen = []
    for x in out:
        if x not in seen: seen.append(x)
    return seen


def prs_in(text):
    """열린 PR 6건만 인식한다 — 이슈 번호(#368 #433 ...)는 PR 이 아니다."""
    out = [n for n in PR_RE.findall(text) if n in OPEN_PRS]
    for k, v in PR_ALIAS.items():
        if k in text and v not in out: out.append(v)
    return out


def load_items():
    items = OrderedDict()
    for mod in MODS:
        p = os.path.join(ROOT, '03-items', f'{mod}.md')
        if not os.path.exists(p):
            continue
        cur = None
        for ln in open(p, encoding='utf-8'):
            if ln.startswith('## 대응표'):
                cur = None
                continue
            m = ITEM_RE.match(ln)
            if m:
                cur = m.group(1)
                items[cur] = dict(id=cur, mod=mod, title=m.group(2).strip(), fields=OrderedDict(), kind='', size='')
                continue
            if cur and ln.startswith('- '):
                k, _, v = ln[2:].partition(':')
                k = k.strip(); v = v.strip()
                items[cur]['fields'][k] = v
                if k == '종류':
                    parts = [x.strip() for x in v.split('|')]
                    items[cur]['kind'] = parts[0]
                    for part in parts[1:]:
                        kk, _, vv = part.partition(':')
                        if kk.strip() == '규모': items[cur]['size'] = vv.strip()
    for it in items.values():
        f = it['fields']
        it['files'] = parse_files(it['mod'], f.get('변경 범위', ''))
        it['keys'] = {norm_key(x) for x in it['files']}
        it['pre_ids'] = [x for x in ids_in(strip_parens(f.get('선행', ''))) if x != it['id']]
        it['pre_prs'] = prs_in(f.get('선행', ''))
        it['conf_ids'] = [x for x in ids_in(f.get('충돌', '')) if x != it['id']]
        it['conf_prs'] = prs_in(f.get('충돌', ''))
    return items


def load_open_prs():
    """open_prs.md 의 PR 중 OPEN_PRS 에 있는 것만 — #530 은 머지하지 않으므로 대기 계산에서 뺀다 (decisions.md ②)."""
    prs = OrderedDict()
    cur = None
    for ln in open(os.path.join(ROOT, '01-sources', 'open_prs.md'), encoding='utf-8'):
        m = re.match(r'^## PR #(\d+)', ln)
        if m:
            cur = m.group(1) if m.group(1) in OPEN_PRS else None
            if cur: prs[cur] = set()
            continue
        m = re.match(r'^\s+- (\S+) \(\+', ln)
        if m and cur:
            prs[cur].add(norm_key(m.group(1)))
    return prs


if __name__ == '__main__':
    items = load_items()
    if '--dump' in sys.argv:
        mods = [a for a in sys.argv[1:] if a in MODS]
        for it in items.values():
            if mods and it['mod'] not in mods: continue
            f = it['fields']
            print(f"{it['id']} [{it['kind']}/{it['size']}] {it['title']}")
            print(f"   files: {' '.join(it['files']) or '-'}")
            print(f"   선행: {f.get('선행','')[:200]}")
            print(f"   충돌: {f.get('충돌','')[:300]}")
            print(f"   흡수: {f.get('흡수','')[:300]}")
    else:
        print(len(items), 'items')
