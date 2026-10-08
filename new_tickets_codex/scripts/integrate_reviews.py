raise SystemExit('2026-10-08: 이 과거 초안 변환기는 사용 중단. modules/*.json과 05_ISSUE_CROSSWALK.json을 편집한 뒤 build_catalog.py를 실행하세요.')
"""Apply recorded cross-review resolutions to authored module cards, idempotently."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def load(owner): return json.loads((R/f'modules/{owner}.json').read_text())
def save(owner,cards): (R/f'modules/{owner}.json').write_text(json.dumps(cards,ensure_ascii=False,indent=2)+'\n')
g=load('geometry');e=load('execution');d=load('downstream')
by={c['id']:c for c in g+e+d}
v=by['VIS-001']
v['outcome']='기존 문서·핸들·카메라를 그대로 보존하면서 Optimizer 프리뷰만 겹쳐 표시한다.'
v['scope'][1]='기존 FE 문서·핸들·피킹 actor의 visibility, registry 표시 커서와 카메라를 유지한다. overlay actor만 등록·해제한다.'
v['acceptance'][0]='기존 로드 모델·핸들이 계속 보이고 표시커서·카메라가 변하지 않으며 preview만 겹친다.'
if not any('다음 Load' in s for s in v['acceptance']):v['acceptance'].append('다음 Load와 요청 무효화에서 preview actor만 제거하고 새로운 기준 씬에 낡은 overlay가 남지 않는다.')
a=by['AST-003']
a['scope'][0]='DashRwActor의 SDK 소유 스레드를 GUI에서 전용 실행 영역으로 옮기고 open/clone/read/edit/export/close·종료 순서를 명시한다.'
a['acceptance'][0]='대형 deck 적재 및 DOE exportDoeSample→clone/edit/export 소비 경로의 무거운 SDK 작업이 GUI에서 실행되지 않음을 thread/time trace로 확인한다.'
a['notes']='이슈 Deferred 유지. registry의 기존 generation/dedup은 보존한다. co_await API여도 DashRwDocumentHandle은 GUI actor에서 suspend 전 동기 완료될 수 있으므로 AL-12 이후 남는 RW 작업의 실제 thread 이관도 여기서 소유한다. VTK actor는 GUI에 연결한다. ANSYS Motion 자체 solver 경로 개편은 범위 밖.'
a['evidence']=list(dict.fromkeys(a['evidence']+['controller/DashRwDocumentHandle.cpp:60 GUI actor 동기 실행 주석; :141 exportContent; :151 clone','controller/DashDoeBatchChain.cpp:216 exportDoeSample']))
a=by['AL-12']
a['outcome']='파일 준비·dat fallback의 GUI 정지를 줄이고 해당 작업의 취소를 전달한다.'
a['scope'][2]='기존 모핑/조건 export의 값·await 호출 경계는 재사용한다. 실제 RW clone/edit/export GUI 실행 이관은 AST-003이 별도로 소유한다.'
a['acceptance'][0]='큰 파일 준비/dat fallback 구간에서 GUI event가 처리되며 취소 후 새 solver 제출이 없다; 전체 RW export 응답성은 AST-003 이후 별도 검증한다.'
a['notes']='독립 파일 준비에는 AST-003 하드선행이 없다. co_await 존재만으로 전체 입력 생성이 GUI 밖에서 돈다고 판정하지 않는다. RW 이관이 Deferred인 동안 남는 GUI 구간을 측정 결과에 명시한다.'
r=by['RES-12'];r['dependencies']=[]
r['scope']=list(dict.fromkeys(r['scope']+['1차 구현 전에 전체 재생성·원자 교체 또는 증분 추가 중 최소 정책을 확정하고, 다른 uuid/tableId 결과에 병합하지 않는 규칙을 포함한다.','USD 원본/내보내기 후보의 논리 구조를 검토하되 1차 구현에 HDF5/USD 채택을 강제하지 않는다.']))
r['acceptance']=list(dict.fromkeys(r['acceptance']+['실패/취소에 기존 완료 파일을 보존하고 서로 다른 실행/참조 식별자의 결과를 한 Set 파일에 섞지 않는다.']))
r['notes']='현재 referenceModel.uuid/tableId로 1차 정책을 세울 수 있으므로 PR530 전체 통합은 하드선행이 아니다. PRJ-11의 산출물 세대 의미를 보존하고 PR530 stamp와 접점을 맞춘다. 외부 reader·multi-part·호환 정책은 구현 관문이며 PR 크기는 생산자/소비자 일관성 기준으로 유연하게 잡는다.'
r=by['RES-13']
r['scope'][0]='RES-12에서 정한 1차 안전한 교체/충돌 방지를 유지하며, 식별자 기반 증분 append/overwrite 확장 정책을 실측으로 정한다.'
r=by['RES-11']
r['acceptance'][1]='현재 분해 경계의 실파일 검증 결과를 남긴다. RES-02/07/09가 미완료면 sub-result/완료집계/worker 경계 최종 승인은 미검증으로 표시하고 완료 뒤 해당 시나리오를 재검증한다.'
r['notes']='실제 SDK/fixture 필요, 이번 조사에서 실행하지 않았다. 도메인 검증은 먼저 할 수 있으며 worker 전체 완료를 기다리지 않는다. 최종 후속경계 승인은 RES-02/07/09 완료 후 해당 검증을 충족해야 한다.'
for tid in ['BLD-01','ANA-03']:
    c=by[tid];c['dependencies']=['PRJ-03','PRJ-11']
    c['notes']='PR530 조합 검증과 PRJ-11의 포맷 중립 산출물 세대 계약을 사용한다. RES-12 전체 포맷 전환을 하드선행으로 두지 않고 새 포맷에서도 같은 metadata를 보존하는 접점만 둔다. '+('MCU deck-무관 예외를 유지한다.' if tid=='BLD-01' else '별도 Analyzer Set을 새로 만들지 않고 현재 호스트 UI에 표시한다.')
c=by['ANA-07']
c['scope'][0]='수동 Plot의 요청 작성 실패와 build() null/미지원 command를 구조화된 사유로 알린다. 자동 debounce의 일시적 입력부족·busy는 비모달 상태/로그로 처리한다.'
c['acceptance'][1]='수동 Plot 실패는 원인을 안내하고 자동 재플롯의 편집 중 입력부족에는 반복 모달을 띄우지 않는다; 실제 build 실패도 무음으로 버리지 않는다.'
c['validation']=list(dict.fromkeys(c['validation']+['수동 클릭과 자동 debounce 각각의 입력부족·busy·build null·연속 실패 통지 횟수 검증']))
# NX shared contract remains deferred; keep independent morph fixes executable.
c=by['RUN-07'];c['outcome']='모핑 입력 생성 중 Set을 바꾸어도 이전 결과가 새 Set의 행이나 상태를 변경하지 않는다.'
c['scope'][2]='모핑 실행의 취소 token과 상태 표시를 요청별로 회수한다. 공유 NX 서비스 계약과 그 소비 이행은 RUN-11이 소유한다.'
c['validation']=['지연 morph callback 및 실패 주입','NodeSet/morph 수동 실행과 Set 전환; NX 왕복은 RUN-11 검증']
c=by['OPT-02'];c['scope'][1]='모핑 요청 id/Set generation과 취소 가능성을 UI에 연결한다. 공유 NX request/result 계면 변경은 CAD-001 및 OPT-07이 소유한다.'
c['acceptance'][1]='모핑 완료/실패가 해당 Optimizer 요청을 한 번만 종결한다.'
c['validation']=['지연 모핑 완료·실패·취소·두 입력 경합 fixture','NX 이외 프리뷰 반복/Set 전환 GUI 회귀; NX는 OPT-07']
for ident,module,title,source,parent,evidence in [
 ('RUN-11','Model Runner / CAD','NX CAD 생성 요청을 저장한 Set과 완료 결과에 결합한다',[249,281,460],'RUN-07','view/DashModelRunnerWidget.cpp:520 m_pendingCadParams'),
 ('OPT-07','Optimizer / CAD','NX CAD 프리뷰 완료를 Optimizer 요청으로 수신한다',[249,457,460],'OPT-02','view/DashOptimizerWidget.cpp:1864 enqueueUpdatePrtGeometry')]:
    if ident not in by:
        d.append(dict(id=ident,module=module,title=title,outcome='NX의 늦은 완료·실패가 다른 Set/요청의 화면과 결과를 바꾸지 않는다.',
          scope=['CAD-001의 공유 요청 id·의도·결과 계면을 소비자에 배선한다.','Set generation·출력 경로·진행 상태를 요청에 보관하고 취소/전환 시 결과를 무효화한다.','공유 서비스 계면을 모듈별로 중복 구현하지 않는다.'],
          acceptance=['동시/연속 NX 요청 완료가 해당 소비자에게만 적용된다.','실패·취소·프로젝트 전환에서 성공 표시와 오래된 결과 적용이 없다.'],
          validation=['NX 수동 load/update 성공·실패·취소·전환 회귀','지연 결과 요청 귀속 fixture'],dependencies=['CAD-001',parent],tags=['A','B','C'],sources=source,evidence=[evidence,'controller/DashSolverNxCad.h:enqueue 및 signal 계면'],status='deferred',priority='P2',notes='공유 NX 계약 CAD-001의 보류를 승계한다. 모핑 요청 수명 수정은 이 작업과 독립적으로 먼저 진행한다.'))
save('geometry',g);save('execution',e);save('downstream',d)
print('Cross-review fixes applied')
