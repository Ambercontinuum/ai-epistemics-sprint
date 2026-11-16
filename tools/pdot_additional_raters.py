"""Additional same-case Astra/Fable passes; never overwrite earlier runs."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request
import urllib.error
import pdot_api_raters as api
import pdot_eval as ev
from openai_spend_guard import assert_openai_allowed

CONFIG = {
 'Astra': {'model':'gpt-6-astra','endpoint':'https://api.openai.com/v1/responses','key':'OPENAI_API_KEY','settings':{'reasoning':{'effort':'low'},'max_output_tokens':4096,'store':False}},
 'Fable': {'model':'claude-fable-5-2','endpoint':'https://api.anthropic.com/v1/messages','key':'ANTHROPIC_API_KEY','settings':{'max_tokens':4096,'output_config':{'effort':'low'}}},
}

def body(name,rubric,messages):
 c=CONFIG[name];content=api.request_body('Meta',rubric,messages)['messages'][1]['content']
 if name=='Astra':return {'model':c['model'],'instructions':api.ENVELOPE,'input':[{'role':'user','content':content}],**c['settings']}
 if name=='Fable':return {'model':c['model'],'system':api.ENVELOPE,'messages':[{'role':'user','content':content}],**c['settings']}
 raise ValueError('Unsupported provider')

def read_keys(path):
 keys={}
 for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
  k,sep,v=line.partition('=');k=k.strip().removeprefix('export ')
  if sep and k in [c['key'] for c in CONFIG.values()]:keys[k]=v.strip().strip('"\'')
 for c in CONFIG.values():keys[c['key']]=os.environ.get(c['key']) or keys.get(c['key'])
 if not all(keys.get(c['key']) for c in CONFIG.values()):raise ValueError('Required credential missing')
 return keys

def sync_gate(scratchpad):
 git=lambda *a:subprocess.check_output(['git','-C',str(scratchpad),*a],text=True).strip()
 if git('remote','get-url','origin')!='https://github.com/Ambercontinuum/ai-epistemics-scratchpad.git' or git('branch','--show-current')!='main' or git('diff','--name-only') or git('diff','--cached','--name-only'):raise ValueError('Unsynced scratchpad')
 head=git('rev-parse','HEAD')
 if head!=git('ls-remote','origin','refs/heads/main').split()[0]:raise ValueError('Remote mismatch')
 return head

def response_text(name,value):
 if name=='Astra':
  return ''.join(part.get('text','') for item in value.get('output',[]) if item.get('type')=='message' for part in item.get('content',[]) if part.get('type')=='output_text'),value.get('status'),value.get('model'),value.get('usage')
 if name=='Fable':return ''.join(b.get('text','') for b in value.get('content',[]) if b.get('type')=='text'),value.get('stop_reason'),value.get('model'),value.get('usage')
 raise ValueError('Unsupported provider')

def call(name,payload,keys,destination,case,packet_hash,rubric_hash):
 assert_openai_allowed(name,CONFIG[name]['endpoint'],CONFIG[name]['model'])
 c=CONFIG[name];key=keys[c['key']];headers={'Content-Type':'application/json'}
 headers.update({'x-api-key':key,'anthropic-version':'2023-06-01'} if name=='Fable' else {'Authorization':'Bearer '+key})
 prefix=Path(destination)/(name.lower()+'-'+case);start=time.time();ev.write_json(str(prefix)+'.attempt.json',{'started_unix':start,'request_sha256':api.digest(payload)})
 result={'provider':name,'case_id':case,'status':'failed','request_sha256':api.digest(payload)};raw=b'';row=None
 try:
  request=urllib.request.Request(c['endpoint'],data=payload,headers=headers,method='POST')
  with urllib.request.build_opener(api.NoRedirect).open(request,timeout=600) as response:raw=response.read();result['http_status']=response.status
  value=json.loads(raw);text,finish,model,usage=response_text(name,value);result.update(returned_model=model,finish_reason=finish,usage=usage)
  if finish!={'Astra':'completed','Fable':'end_turn'}[name] or model!=c['model']:raise ValueError('Incomplete/model mismatch')
  row=api.parse_rating(text,{'provider':name,'case_id':case},packet_hash,rubric_hash);result['status']='parsed'
 except urllib.error.HTTPError as error:raw=error.read();result.update(http_status=error.code,error_kind='HTTPError')
 except Exception as error:result['error_kind']=type(error).__name__
 for secret in keys.values():raw=raw.replace(secret.encode(),b'[REDACTED]')
 Path(str(prefix)+'.response.private.json').write_bytes(raw);result.update(elapsed_seconds=round(time.time()-start,3),response_sha256=api.digest(raw));ev.write_json(str(prefix)+'.outcome.private.json',result)
 return result,row

def prepare(root,output):
 root=Path(root);old=root/'data/private-conversation-archive/pdot-api-bundle-v2';oldspec,binding=api.verify_bundle(old)
 dataset,rmanifest=ev.validate_dataset(root/'data/private-conversation-archive/pdot-pilot-v1',root/'references/PDOT-public-172b115/templates/rater_guide.md');source={r['sample_id']:r['messages'] for r in dataset}
 tasks=ev.read_rows(root/'data/private-conversation-archive/pdot-alite-amber-v1/tasks.private.jsonl');rubric=(root/'references/PDOT-public-172b115/templates/rater_guide.md').read_bytes().decode()
 if len(tasks)!=20 or len({t['case_id'] for t in tasks})!=20:raise ValueError('Selection changed')
 for t in tasks:
  if t['window']!='T3' or t['messages']!=source[binding['case_map'][t['case_id']]]:raise ValueError('Window changed')
 output=api.private_dir(output);rb={'case_map':binding['case_map'],'raters':list(CONFIG),'windows':{'T3':[1,25]},'rubric_sha256':oldspec['rubric_sha256']};ev.write_json(output/'packet_manifest.private.json',rb);requests=[]
 for name in CONFIG:
  for t in tasks:
   payload=api.encoded(body(name,rubric,t['messages']));file=name.lower()+'-'+t['case_id']+'.request.private.json';(output/file).write_bytes(payload);requests.append({'provider':name,'case_id':t['case_id'],'file':file,'sha256':api.digest(payload)})
 spec={'version':'additional-panel-v2','runner_sha256':ev.sha(__file__),'helper_sha256':ev.sha(Path(__file__).with_name('pdot_api_raters.py')),'harness_sha256':ev.sha(Path(__file__).with_name('pdot_eval.py')),'config':CONFIG,'envelope_sha256':api.digest(api.ENVELOPE.encode()),'rubric_sha256':oldspec['rubric_sha256'],'rating_packet_sha256':ev.sha(output/'packet_manifest.private.json'),'requests':requests,'timeout':600,'retries':0}
 (output/'bundle.private.json').write_bytes(api.encoded(spec));return {'bundle_sha256':ev.sha(output/'bundle.private.json'),'requests':40}

def execute(folder,output,scratchpad,claude,muse,authorization,env):
 for name,config in CONFIG.items():assert_openai_allowed(name,config['endpoint'],config['model'])
 folder=Path(folder);spec=ev.read_json(folder/'bundle.private.json');h=ev.sha(folder/'bundle.private.json')
 for who,r in [('claude',claude),('muse',muse)]:
  if r.get('reviewer')!=who or r.get('status')!='CLEAR' or r.get('scope')!='execution' or r.get('bundle_sha256')!=h or not r.get('limitations') or not r.get('receipt_reference'):raise ValueError('Both exact-bundle execution clears required')
 if authorization.get('decision_owner')!='amber' or authorization.get('bundle_sha256')!=h or authorization.get('providers')!=['OpenAI','Anthropic'] or authorization.get('max_requests')!=40 or authorization.get('authorize_private_send_and_launch') is not True or not authorization.get('exact_user_wording'):raise ValueError('Exact-bundle private-send/launch authorization required')
 if spec['runner_sha256']!=ev.sha(__file__) or spec['helper_sha256']!=ev.sha(Path(__file__).with_name('pdot_api_raters.py')) or spec['harness_sha256']!=ev.sha(Path(__file__).with_name('pdot_eval.py')) or spec['config']!=CONFIG or spec['envelope_sha256']!=api.digest(api.ENVELOPE.encode()) or spec['timeout']!=600 or spec['retries']!=0:raise ValueError('Reviewed code/spec changed')
 binding=ev.read_json(folder/'packet_manifest.private.json')
 if ev.sha(folder/'packet_manifest.private.json')!=spec['rating_packet_sha256']:raise ValueError('Binding changed')
 seen=set()
 for r in spec['requests']:
  key=(r['provider'],r['case_id'])
  if key in seen or key[0] not in CONFIG or key[1] not in binding['case_map'] or Path(r['file']).name!=r['file'] or ev.sha(folder/r['file'])!=r['sha256']:raise ValueError('Invalid request')
  seen.add(key)
 if seen!={(name,case) for name in CONFIG for case in binding['case_map']} or len(seen)!=40:raise ValueError('Wrong request set')
 head=sync_gate(scratchpad);keys=read_keys(env)
 with (folder/'EXECUTION-STARTED.private.json').open('x') as f:json.dump({'started_unix':time.time(),'bundle_sha256':h,'scratchpad_commit':head},f)
 output=api.private_dir(output);ratings=[];outcomes=[];blocked=set()
 for r in spec['requests']:
  if r['provider'] in blocked:continue
  result,row=call(r['provider'],(folder/r['file']).read_bytes(),keys,output,r['case_id'],spec['rating_packet_sha256'],spec['rubric_sha256']);outcomes.append(result)
  if row is not None:ratings.append(row)
  if result.get('http_status') in (400,401,403,404,429):blocked.add(r['provider'])
  ev.write_rows(output/'ratings.private.jsonl',ratings);ev.write_json(output/'progress.private.json',{'outcomes':outcomes,'unattempted':40-len(outcomes)})
  print(json.dumps({'provider':r['provider'],'attempted':len(outcomes),'parsed':len(ratings),'failed':len(outcomes)-len(ratings)}),flush=True)
 ev.write_json(output/'run.private.json',{'bundle_sha256':h,'scratchpad_commit':head,'outcomes':outcomes,'unattempted':40-len(outcomes)});ev.write_json(output/'report.private.json',ev.summarize(ratings,binding,spec['rating_packet_sha256']))

if __name__=='__main__':
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='command',required=True);a=sub.add_parser('prepare');a.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a.add_argument('--output',type=Path,required=True);a=sub.add_parser('execute')
 for k in ['bundle','output','scratchpad','claude','muse','authorization','env']:a.add_argument('--'+k,type=Path,required=True)
 args=ap.parse_args()
 try:
  if args.command=='prepare':print(json.dumps(prepare(args.root,args.output)))
  else:execute(args.bundle,args.output,args.scratchpad,ev.read_json(args.claude),ev.read_json(args.muse),ev.read_json(args.authorization),args.env)
 except Exception:print(json.dumps({'error':'Operation failed; no retries. Inspect local metadata without adjudicating scores.'}));raise SystemExit(2)
