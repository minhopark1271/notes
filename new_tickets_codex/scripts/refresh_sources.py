"""Read-only GitHub snapshot. Authentication is process-local; no token is persisted."""
import json, os, subprocess, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
env = os.environ.copy()
env['GH_TOKEN'] = subprocess.check_output(['gh', 'auth', 'token', '--user', 'minhopark-lgtm'], text=True).strip()

def gh(*args):
    return subprocess.check_output(['gh', *args], env=env, text=True)

def save(name, value):
    (ROOT/'sources'/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

items = json.loads(gh('project','item-list','16','--owner','NumeRealWorks','--format','json','--limit','500'))
save('items.json', items)
save('open-prs.json', json.loads(gh('pr','list','--repo','NumeRealWorks/DashOpti_GUI','--state','open','--limit','100','--json','number,title,body,baseRefName,headRefName,isDraft,url,updatedAt,files')))
save('remote-dev.json', json.loads(gh('api','repos/NumeRealWorks/DashOpti_GUI/commits/dev','--jq','{sha: .sha, date: .commit.committer.date, message: .commit.message}')))
query = 'query($endCursor:String) { organization(login:"NumeRealWorks") { projectV2(number:16) { items(first:100,after:$endCursor) { pageInfo { hasNextPage endCursor } nodes { id isArchived content { ... on Issue { number state stateReason updatedAt closedAt parent { number title } subIssues(first:100) { totalCount nodes { number state title } } comments { totalCount } } } } } } } }'
raw=gh('api','graphql','--paginate','-f','query='+query)
decoder=json.JSONDecoder(); nodes=[]
while raw.strip():
    value,end=decoder.raw_decode(raw.lstrip()); raw=raw.lstrip()[end:]
    nodes.extend(value['data']['organization']['projectV2']['items']['nodes'])
save('metadata.json',nodes)
numbers=[n['content']['number'] for n in nodes if n['content']['comments']['totalCount']]
comments={}
for start in range(0,len(numbers),25):
    query='query { repository(owner:"NumeRealWorks",name:"DashOpti_GUI") {'+' '.join('i%d:issue(number:%d){number comments(last:100){totalCount nodes{body createdAt}}}'%(n,n) for n in numbers[start:start+25])+'} }'
    comments.update(json.loads(gh('api','graphql','-f','query='+query))['data']['repository'])
save('comments.json',{'data':{'repository':comments}})
for i in items['items']:
    c=i['content'];n=c['number']
    body=f'# #{n} {i["title"]}\n\n- URL: {c.get("url","")}\n- Board status: {i.get("status","unset")}\n- Labels: {i.get("labels",[])}\n\n'+c.get('body','')
    for cm in comments.get('i'+str(n),{}).get('comments',{}).get('nodes',[]):
        body+='\n\n---\nComment '+cm['createdAt']+'\n\n'+cm['body']
    (ROOT/'sources/issues'/f'{n}.md').write_text(body)
save('snapshot.json', {'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'items':len(items['items']),'comment_limit_per_issue':100,'comments_truncated':[v['number'] for v in comments.values() if v['comments']['totalCount']>100]})
print('Read-only snapshot refreshed:',len(items['items']),'items;',len(numbers),'issues with comments')
