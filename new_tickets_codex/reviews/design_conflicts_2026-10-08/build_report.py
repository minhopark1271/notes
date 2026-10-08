"""분담 검토와 교차검토 교정을 통합한다. 조사 원문은 수정하지 않는다."""
import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE.parent.parent
NOTES = CATALOG.parent


def read(name):
    return json.loads((HERE / name).read_text())


def save(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


findings = []
coverage = []
for owner in ['downstream', 'execution', 'geometry', 'root']:
    findings.extend(dict(f, reviewer=owner) for f in read(f'{owner}_findings.json'))
    coverage.extend(dict(c, reviewer=owner) for c in read(f'{owner}_coverage.json'))
overrides = read('root_overrides.json')
for f in findings:
    correction = overrides.get(f['id'], {})
    f['evidence'].extend(correction.get('append_evidence', []))
    f.update({k: v for k, v in correction.items() if k != 'append_evidence'})
    f['cross_review_corrected'] = bool(correction)

errors = []
known = set()
for f in findings:
    if f['id'] in known:
        errors.append(f"중복 ID: {f['id']}")
    known.add(f['id'])
    for e in f['evidence']:
        p = NOTES / e['path']
        if not p.exists():
            errors.append(f"근거 파일 없음: {e['path']}")
            continue
        lines = p.read_text().splitlines()
        if not (1 <= e['line'] <= e.get('end_line', e['line']) <= len(lines)):
            errors.append(f"근거 좌표 오류: {f['id']} {e['path']}:{e['line']}")
        e['actual_lines_at_review'] = '\n'.join(lines[e['line']-1:e.get('end_line', e['line'])])

inventory = read('inventory.json')
input_hashes = inventory + read('additional_input_hashes.json')
changed = [r['path'] for r in input_hashes if hashlib.sha256((NOTES / r['path']).read_bytes()).hexdigest() != r['sha256']]
covered = {c['path'] for c in coverage}
missing = [r['path'] for r in inventory if r['path'] not in covered]
if missing:
    errors.append(f'루트 문서 검토 누락: {missing}')
if changed:
    errors.append(f'조사 중 입력 변경: {changed}')

save('findings.json', findings)
save('coverage.json', coverage)
class_names = {'document_drift': '개정 미전파·문구 정합성', 'active_conflict': '설계안의 적용 범위 불일치', 'proposal_alternative': '명시적 대안·추가 결정', 'historical_resolved': '역사·시점 차이 / 현재 충돌 제외'}
severity_names = {'high': '높음', 'medium': '중간', 'low': '낮음'}


def link(path, line=None):
    target = os.path.relpath(NOTES / path, CATALOG)
    name = Path(path).name + (f':{line}' if line else '')
    return f'[{name}]({target})'


main = [f for f in findings if f['classification'] in ['document_drift', 'active_conflict']]
excluded = [f for f in findings if f not in main]
priority = ['DS-01', 'DS-02', 'DS-03', 'DS-04', 'EXDC-01', 'EXDC-03', 'GDC-01', 'GDC-02', 'GDC-03', 'GDC-04', 'EXDC-02', 'DS-05', 'GDC-05']
main.sort(key=lambda f: priority.index(f['id']) if f['id'] in priority else 99)
lines = [
    '# notes 설계 충돌·개정 미전파 검토 — 2026-10-08', '',
    '**같은 문서들을 현재 작업 지시로 함께 읽으면 충돌하는 내용이 있다. 가장 큰 원인은 명시된 개정이 오래된 Manifest·작업 목록·대응표에 전파되지 않은 것이다.** 특히 오늘 개정 이력의 입력 참조·출처 정책은 10월5~7일 Claude/Codex 작업 정의와 다르다. 별도 Set 원장 요구는 더 오래된 9월21일 결정도 놓친 Codex 작성 오류다.', '',
    '이번 결과는 문서 대조다. GitHub 이슈가 실제로 현재 어떤 내용인지, 최신 코드/PR의 구현이 어느 정책을 따르는지는 재조회·빌드·실행하지 않았다. `Issue-Revision-History.md`의 **개정 반영/기존 개정 수록**과 **추가 개정 계획(아직 미반영)**을 구분했다. 최신 날짜만 보고 모든 문장을 확정 설계로 취급하지 않았다.', '',
    '## 지금 착수 기준에서 먼저 정렬할 내용', '',
    '| 주제 | 남아 있는 옛 요구 | 문서상 현재 방향 / 필요한 처리 |',
    '|---|---|---|',
    '| 입력 참조·출처 | 조합 ID 생성과 최초 입력 영구핀, 다른 조합 차단 | 개별 setId로 입력 참조 변경 허용. 이미 생성된 산출물 출처는 선택 변경만으로 바꾸지 않고 재실행 성공 시 실제 출처와 함께 갱신 |',
    '| 산출물 대장 | PRJ-05·IO-10·IO-11의 별도 생산/소비 이력 대장 | #471 취소. Set·산출물이 원본 기록을 보유하고 프로젝트가 조회·집계. 과거 이력 보존은 요구하지 않음 |',
    '| Set 원장 | PRJ-04의 별도 Set 원장으로 정본 전환 | 기존 setId 발급/파일 영속/역조회 활용. 별도 원장 불도입은 9월21일 SI-2에도 이미 있음 |',
    '| 작업 경계 | G9/PR530 전체를 하나의 이행·선행으로 취급 | #368은 Builder 산출 기록까지, 소비 측은 #685. #473 결과 조작·#369 NodeSet 저장은 독립. #650 최신성과도 분리 |',
    '| 상태 기록 | 기록 책임 분리와 파일 분할을 같은 것으로 해석 | #444는 비용 확인 후 필요한 경우만 파일 분리. AL-05와 LCH-32가 서로 반대의 물리 분할 확정안이라고 단정하지 않음 |',
    '| 핸들/모핑 | DashHandleData·VTP/기존 GizmoGroup을 수정하는 계획 | 최신 작업 문서의 상태기·entry 모델 및 삭제 예정 범위와 대조한 뒤 잔여만 남김. PR 현재 상태를 이번에 실증한 것은 아님 |', '',
    '정책 근거: ' + link('Issue-Revision-History.md', 9) + ', ' + link('Issue-Revision-History.md', 21) + ', ' + link('Issue-Revision-History.md', 61) + ', ' + link('Project-Manifest-Set-Identity-And-Decision-Revisions.md', 29) + '.', '',
    '**특히 어제의 `07_BOARD_OVERLAY.md`는 10월7일 기준으로 보존해야 한다.** 그 문서의 “#471 존폐 미결”, “#368 조합 스탬프 기능 유지”, 원장 요구를 현재 설계로 그대로 인용하면 안 된다. 오늘 검토에서 AL-05를 물리 파일 분할 확정으로 해석한 과장도 교정했다.', '',
    '## 주요 정합성 지적', '',
    f'{len(main)}개 후보를 기록했다. 모두 같은 무게의 확정 설계 오류는 아니다. 개정 미전파, 범위 승계 차이, 완료 조건의 모호성을 구분하며 실제 제품 정책의 채택 여부가 필요한 곳은 명시한다.', '',
    '| ID | 영향 | 분류 | 내용 |', '|---|---|---|---|',
]
for f in main:
    lines.append(f"| [{f['id']}](#{f['id'].lower()}) | {severity_names[f['severity']]} | {class_names[f['classification']]} | {f['title']} |")
for f in main:
    lines.extend(['', f"<a id=\"{f['id'].lower()}\"></a>", f"### {f['id']} · {f['title']}", '', f['summary'], '', f"- 영향: {f['impact']}", f"- 제안: {f['recommendation']}", f"- 확신: {f['confidence']} (문서 비교의 확신이며 구현 검증이 아님)", '- 근거:'])
    for e in f['evidence']:
        excerpt = e.get('excerpt', '').replace('\n', ' ').replace('|', '\\|')
        excerpt = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', excerpt)
        if len(excerpt) > 450:
            excerpt = excerpt[:450] + '…'
        for special in ['\\', '`', '*', '_', '[', ']', '<', '>']:
            excerpt = excerpt.replace(special, '\\' + special)
        lines.append(f"  - {link(e['path'], e['line'])} — {e.get('role', '근거')}: {excerpt}")

lines += ['', '## 실제 충돌로 집계하지 않은 차이', '',
          '미확정 대안을 나란히 검토하거나 역사적 설계를 보존하는 것은 자체로 오류가 아니다. 아래는 현행 확정 계약 충돌에서 제외했다.', '',
          '| ID | 구분 | 판단 |', '|---|---|---|']
for f in excluded:
    lines.append(f"| {f['id']} | {class_names[f['classification']]} | {f['summary'].replace('|', '/') } |")
lines += ['', '대표적으로 Store α/β·정의 버전안·ID 발급안은 Index부터 미확정이다. 스키마 버전과 산출물 버전도 같은 개념이 아니다. 폐기된 W6/W10 설계, rc 임시 수선, 고정 커밋의 Code Map, 현재 구현 예시와 확장 구상이 섞인 drawio 도면도 구분해 읽었다.', '',
          '## 문서 정리 권고', '',
          '1. 현재 참조·출처·버전의 책임을 한 문서에서 선언하고, 이전 Manifest 결정에는 대체된 조항과 날짜를 표시한다. 기존 이력을 삭제하거나 완료 당시 구현을 소급 수정하지 않는다.',
          '2. Codex PRJ-03/04/05·IO-10/11 및 Claude PER-06/07·홉별 스탬프 작업·LCH-33부터 오늘 정책에 대조한다. 상세 자동 재작성은 이번 검토 범위가 아니다.',
          '3. 보존할 조사·제안·과거 설계에는 기준 커밋/날짜와 지위를 명시한다. “정본”도 조사 사실의 정본인지 현재 구현 계약의 정본인지 구분한다.',
          '4. #643 append/덮어쓰기, #615 자동 선택, 버전 비교 규칙 등 추가 계획을 이미 확정된 요구처럼 선행 그래프에 넣지 않는다.',
          '5. 하위 계약의 부분 겹침은 담당과 테스트 경계로 조율한다. 파일이 겹친다는 이유만으로 모든 결함 수정에 전체 구조 이행을 선행시키지 않는다.', '',
          '## 검토 범위와 산출물', '',
          '- 루트 Markdown68개를 목록화하고 문서별 머리말·개정·주제 구간을 검토했다. 읽기 깊이는 coverage에 구분했다. 전 문서의 모든 문장을 완독했다는 뜻은 아니다.',
          '- drawio2개의 도형 레이블을 확인했다. PNG는 같은 도면의 중복 표현으로 별도 검증하지 않았다.',
          '- Claude/Codex 최종 작업 정의와 관련 결정·대응표를 대조했다. sources/wiki 및 이슈 복제본은 독립 현행 설계로 중복 집계하지 않았다.',
          '- 세 agent 분담 검토와 두 차례 교차검토를 거쳤다. 교차검토에서 확정 정책/미반영 계획, 논리 계약/물리 분할, 테스트 범위의 혼동을 보정했다.',
          '- 원문 설계·기존 작업 정의·GitHub는 수정하지 않았다. 이 보고서와 조사 산출물만 추가했다.', '',
          '[통합 지적 JSON](reviews/design_conflicts_2026-10-08/findings.json) · [문서별 검토 범위](reviews/design_conflicts_2026-10-08/coverage.json) · [검증 결과](reviews/design_conflicts_2026-10-08/validation.json) · [교차검토 1](reviews/design_conflicts_2026-10-08/cross_review_execution.md) · [교차검토 2](reviews/design_conflicts_2026-10-08/cross_review_downstream.md)', '']
report = CATALOG / '08_DESIGN_CONFLICT_REVIEW.md'
report.write_text('\n'.join(lines))
for target in re.findall(r'(?<!\\)\]\(([^)\n]+)\)', report.read_text()):
    if '://' in target or target.startswith('#'):
        continue
    if not (report.parent / target.split('#')[0]).exists():
        errors.append(f'보고서 링크 오류: {target}')
result = {'result': 'FAIL' if errors else 'PASS', 'root_markdown_inventory': len(inventory), 'root_markdown_covered': len(set(r['path'] for r in inventory) & covered), 'findings': len(findings), 'main_findings': len(main), 'classification_counts': dict(Counter(f['classification'] for f in findings)), 'cross_review_corrections': list(overrides), 'source_files_changed': changed, 'errors': errors, 'not_tested': '원격 상태·최신 구현·빌드·GUI·solver; 문서 검토만 수행'}
save('validation.json', result)
print(json.dumps(result, ensure_ascii=False))
if errors:
    raise SystemExit(1)
