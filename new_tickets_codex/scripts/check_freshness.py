"""Read-only final source comparison; preserve the original research snapshot."""
import datetime,json,os,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
env=os.environ.copy()
env['GH_TOKEN']=subprocess.check_output(['gh','auth','token','--user','minhopark-lgtm'],text=True).strip()
def gh(*a):return subprocess.check_output(['gh',*a],text=True,env=env)
query='query { repository(owner:"NumeRealWorks",name:"DashOpti_GUI") { ref(qualifiedName:"refs/heads/dev"){ target { oid }} '+ ' '.join(f'p{n}:pullRequest(number:{n}){{number state headRefOid updatedAt}}' for n in [530,651,652,654])+' } organization(login:"NumeRealWorks"){projectV2(number:16){items{totalCount} updatedAt}}}'
now=json.loads(gh('api','graphql','-f','query='+query))['data']
changes=[];repo=now['repository']
old=json.loads((R/'sources/remote-dev.json').read_text())
if repo['ref']['target']['oid']!=old['sha']:changes.append('remote dev changed')
for n in [530,651,652,654]:
    oldpr=json.loads((R/f'sources/pr-{n}.json').read_text());new=repo[f'p{n}']
    if (new['state'],new['headRefOid'])!=(oldpr['state'],oldpr['headRefOid']):changes.append(f'PR{n} state/head changed')
fresh=json.loads(gh('project','item-list','16','--owner','NumeRealWorks','--format','json','--limit','500'))
previous=json.loads((R/'sources/items.json').read_text())
if fresh!=previous:changes.append('board items/issue bodies/fields changed')
report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'changes':changes,'result':'UNCHANGED' if not changes else 'CHANGED','current':now}
(R/'sources/final-freshness.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
if changes:(R/'sources/items-final.json').write_text(json.dumps(fresh,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'result':report['result'],'changes':changes},ensure_ascii=False))
