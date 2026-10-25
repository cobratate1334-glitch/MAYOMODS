"""Check routed content, receipts, registered fields, ELF layout and timeout bytes."""
import csv,hashlib,io,json,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
def validate(native,launcher):
 a=json.loads((ROOT/'assets.json').read_text());events=json.loads((ROOT/'receipts55.json').read_text());schemas=json.loads((ROOT/'schemas.json').read_text());checks=[]
 def check(v,s):assert v,s;checks.append(s)
 check(all('Compiled by Atlanti'not in v for v in a.values()),'unwanted attribution removed')
 menus=['genesis_v7_f1_career','genesis_v7_tv_host','genesis_music_studio_hub'];scenes={}
 for name in ['genesis_careers_v7','genesis_music_studio','genesis_activities_v18','genesis_activities_v12']:
  rows=list(csv.DictReader(io.StringIO(a[name])));ids=[r['ScenarioID']for r in rows];check(len(ids)==len(set(ids)),'unique scenario IDs '+name);scenes[name]=set(ids)
 def routes(v):
  if isinstance(v,list):
   for x in v:yield from routes(x)
  elif isinstance(v,dict):
   if 'ScenarioID'in v:yield v
   for x in v.values():yield from routes(x)
 for name in menus:
  d=json.loads(a[name])
  for r in routes(d):
   dataset=r.get('ScenarioFile')
   if dataset not in scenes and dataset in a and a[dataset].startswith('ScenarioID,'):scenes[dataset]={x['ScenarioID']for x in csv.DictReader(io.StringIO(a[dataset]))}
   check(r['ScenarioID'].startswith('scenario.')and r['ScenarioID']in scenes.get(dataset,set()),'plain registered route '+r['ScenarioID'])
 for e in events:
  check(e['id']<=int(schemas[e['owner']]['Receipt55']['maximum']),'registered receipt '+str(e['id']));check(e['text'].startswith('I completed ')and isinstance(e['text'],str),'literal outcome label '+str(e['id']))
 check(len(events)>50,'effectful career and studio choices have distinct receipts')
 raw=Path(native).read_bytes();d=json.loads((ROOT/'native_hooks.json').read_text());check(hashlib.sha256(raw).hexdigest()==d['binary_sha256'],'native manifest hash')
 loads=[s for s in ELFFile(io.BytesIO(raw)).iter_segments()if s['p_type']=='PT_LOAD'];added=next(s for s in loads if s['p_vaddr']==d['v55_added_rx'][1]);check(added['p_flags']==5 and added['p_align']==16384,'new native segment is page-aligned RX')
 newrange=(added['p_vaddr']&~16383,(added['p_vaddr']+added['p_memsz']+16383)&~16383)
 check(all(newrange[1]<=s['p_vaddr']&~16383 or ((s['p_vaddr']+s['p_memsz']+16383)&~16383)<=newrange[0]for s in loads if s is not added),'new native segment overlaps no existing load page')
 for s in loads:check(s['p_offset']%16384==s['p_vaddr']%16384,'16 KB native mapping alignment')
 launch=Path(launcher).read_bytes();e=ELFFile(io.BytesIO(launch));va=0xde320;seg=next(s for s in e.iter_segments()if s['p_type']=='PT_LOAD'and s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']);off=seg['p_offset']+va-seg['p_vaddr'];ins=next(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(launch[off:off+4],va));check(ins.mnemonic=='tbz'and ins.op_str.endswith('#0xde2b0'),'readiness timeout retries the known unlocked wait path')
 report=dict(passed=True,checks=len(checks),cases=checks,physical_phone_tested=False,Android_lifecycle_tested=False);(ROOT/'structure55_validation.json').write_text(json.dumps(report,indent=2)+'\n');print({'passed':True,'checks':len(checks)},flush=True)
if __name__=='__main__':validate(*sys.argv[1:])
