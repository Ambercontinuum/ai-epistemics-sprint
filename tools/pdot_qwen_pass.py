"""Separate Qwen pass; preserves original run. No network on prepare/import."""
import os
import argparse
import json
from pathlib import Path
import subprocess
import time
import urllib.request
import urllib.error
import pdot_api_raters as api
import pdot_eval as ev

URL = os.environ.get('PDOT_QWEN_ENDPOINT','https://REDACTED-modal-endpoint/v1/chat/completions')
MODEL='Qwen/Qwen3.8-2.4T-A95B'
SETTINGS={'temperature':0,'max_tokens':4096,'reasoning_effort':'low','stream':False}


def body(rubric,messages):
    original=api.request_body('Meta',rubric,messages)
    return {'model':MODEL,'messages':[{'role':'system','content':api.ENVELOPE},original['messages'][1]],**SETTINGS}


def prepare(root,output):
    root=Path(root);output=Path(output)
    old=root/'data/private-conversation-archive/pdot-api-bundle-v2'
    bundle,binding=api.verify_bundle(old)
    tasks=ev.read_rows(root/'data/private-conversation-archive/pdot-alite-amber-v1/tasks.private.jsonl')
    rubric=(root/'references/PDOT-public-172b115/templates/rater_guide.md').read_bytes().decode()
    if api.digest(rubric.encode())!=bundle['rubric_sha256']:raise ValueError('Rubric changed')
    dataset,_=ev.validate_dataset(root/'data/private-conversation-archive/pdot-pilot-v1',root/'references/PDOT-public-172b115/templates/rater_guide.md')
    source={r['sample_id']:r['messages'] for r in dataset}
    if len(tasks)!=20 or len({t['case_id'] for t in tasks})!=20:raise ValueError('Expected20 cases')
    for t in tasks:
        if t['window']!='T3' or t['messages']!=source[binding['case_map'][t['case_id']]]:raise ValueError('Window changed')
    api.private_dir(output)
    rb={'case_map':binding['case_map'],'raters':['Qwen'],'windows':{'T3':[1,25]},'rubric_sha256':bundle['rubric_sha256']}
    ev.write_json(output/'packet_manifest.private.json',rb)
    requests=[]
    for t in tasks:
        payload=api.encoded(body(rubric,t['messages']));name=t['case_id']+'.request.private.json'
        (output/name).write_bytes(payload);requests.append({'case_id':t['case_id'],'file':name,'sha256':api.digest(payload)})
    spec={'version':'qwen-separate-pass-v1','runner_sha256':ev.sha(__file__),'api_helper_sha256':ev.sha(Path(__file__).with_name('pdot_api_raters.py')),'harness_sha256':ev.sha(Path(__file__).with_name('pdot_eval.py')),'endpoint':URL,'model':MODEL,'settings':SETTINGS,'envelope_sha256':api.digest(api.ENVELOPE.encode()),'rubric_sha256':bundle['rubric_sha256'],'rating_packet_sha256':ev.sha(output/'packet_manifest.private.json'),'requests':requests,'retries':0,'timeout_seconds':600}
    (output/'bundle.private.json').write_bytes(api.encoded(spec))
    return {'bundle_sha256':ev.sha(output/'bundle.private.json'),'requests':20}


def execute(folder,output,scratchpad,claude,muse,authorization,credential):
    folder=Path(folder);spec=ev.read_json(folder/'bundle.private.json');h=ev.sha(folder/'bundle.private.json')
    for who,receipt in [('claude',claude),('muse',muse)]:
        if receipt.get('reviewer')!=who or receipt.get('scope')!='execution' or receipt.get('status')!='CLEAR' or receipt.get('bundle_sha256')!=h or not receipt.get('limitations') or not receipt.get('receipt_reference'):raise ValueError('Both exact-bundle execution receipts required')
    if authorization.get('decision_owner')!='amber' or authorization.get('bundle_sha256')!=h or authorization.get('provider')!='Modal' or authorization.get('max_requests')!=20 or authorization.get('authorize_private_send_and_launch') is not True or not authorization.get('exact_user_wording'):raise ValueError('Exact Modal20-case authorization required')
    if spec['runner_sha256']!=ev.sha(__file__) or spec['api_helper_sha256']!=ev.sha(Path(__file__).with_name('pdot_api_raters.py')) or spec['harness_sha256']!=ev.sha(Path(__file__).with_name('pdot_eval.py')):raise ValueError('Code changed')
    if spec['endpoint']!=URL or spec['model']!=MODEL or spec['settings']!=SETTINGS or spec['envelope_sha256']!=api.digest(api.ENVELOPE.encode()) or spec['retries']!=0 or spec['timeout_seconds']!=600:raise ValueError('Spec changed')
    binding=ev.read_json(folder/'packet_manifest.private.json')
    if ev.sha(folder/'packet_manifest.private.json')!=spec['rating_packet_sha256']:raise ValueError('Binding changed')
    if len(spec['requests'])!=20 or {r['case_id'] for r in spec['requests']}!=set(binding['case_map']):raise ValueError('Selection changed')
    for r in spec['requests']:
        if Path(r['file']).name!=r['file'] or ev.sha(folder/r['file'])!=r['sha256']:raise ValueError('Payload changed')
    git=lambda *a:subprocess.check_output(['git','-C',str(scratchpad),*a],text=True).strip()
    if git('remote','get-url','origin')!='https://github.com/Ambercontinuum/ai-epistemics-scratchpad.git' or git('branch','--show-current')!='main' or git('diff','--name-only') or git('diff','--cached','--name-only'):raise ValueError('Unsynced scratchpad')
    head=git('rev-parse','HEAD')
    if head!=git('ls-remote','origin','refs/heads/main').split()[0]:raise ValueError('Remote mismatch')
    creds=ev.read_json(credential)
    with (folder/'EXECUTION-STARTED.private.json').open('x') as f:json.dump({'bundle_sha256':h,'scratchpad_commit':head,'started_unix':time.time()},f)
    output=api.private_dir(output);opener=urllib.request.build_opener(api.NoRedirect);outcomes=[];ratings=[]
    for item in spec['requests']:
        with (output/(item['case_id']+'.attempt.json')).open('x') as f:json.dump({'started_unix':time.time(),'request_sha256':item['sha256']},f)
        result={'case_id':item['case_id'],'provider':'Qwen','status':'failed'};raw=b''
        try:
            request=urllib.request.Request(URL,data=(folder/item['file']).read_bytes(),headers={'Authorization':creds['Authorization'],'Content-Type':'application/json'},method='POST')
            with opener.open(request,timeout=600) as response:raw=response.read();result['http_status']=response.status
            value=json.loads(raw);choice=value['choices'][0];result.update(returned_model=value.get('model'),usage=value.get('usage'),finish_reason=choice.get('finish_reason'))
            if result['returned_model']!=MODEL or result['finish_reason']!='stop':raise ValueError('Incomplete/model mismatch')
            ratings.append(api.parse_rating(choice['message']['content'],{'case_id':item['case_id'],'provider':'Qwen'},spec['rating_packet_sha256'],spec['rubric_sha256']));result['status']='parsed'
        except urllib.error.HTTPError as e:raw=e.read();result.update(http_status=e.code,error_kind='HTTPError')
        except Exception as e:result['error_kind']=type(e).__name__
        for secret in creds.values():
            if isinstance(secret,str):raw=raw.replace(secret.encode(),b'[REDACTED]')
        (output/(item['case_id']+'.response.private.json')).write_bytes(raw);result['response_sha256']=api.digest(raw);ev.write_json(output/(item['case_id']+'.outcome.private.json'),result);outcomes.append(result);ev.write_rows(output/'ratings.private.jsonl',ratings)
        print(json.dumps({'attempted':len(outcomes),'parsed':len(ratings),'failed':len(outcomes)-len(ratings)}),flush=True)
        if result.get('http_status') in (400,401,403,404,429):break
    ev.write_json(output/'run.private.json',{'bundle_sha256':h,'scratchpad_commit':head,'outcomes':outcomes,'unattempted':20-len(outcomes)})
    ev.write_json(output/'report.private.json',ev.summarize(ratings,binding,spec['rating_packet_sha256']))


if __name__=='__main__':
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True);a=sub.add_parser('prepare');a.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a.add_argument('--output',type=Path,required=True);a=sub.add_parser('execute')
    for k in ['bundle','output','scratchpad','claude','muse','authorization','credential']:a.add_argument('--'+k,type=Path,required=True)
    args=ap.parse_args()
    try:
        if args.cmd=='prepare':print(json.dumps(prepare(args.root,args.output)))
        else:execute(args.bundle,args.output,args.scratchpad,ev.read_json(args.claude),ev.read_json(args.muse),ev.read_json(args.authorization),args.credential)
    except Exception:
        print(json.dumps({'error':'Operation failed. No automatic retry. Inspect private receipts without grading model outputs.'}));raise SystemExit(2)
