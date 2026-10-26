"""Physical-line tokenizer, literal routes and complete native page templates."""
import csv,hashlib,io,json,sys,re
from pathlib import Path
from native_immersion.content import build,route,OPEN
from native_immersion.protocol import KEYS
from ui_integrity.validate_content import native_tokens

def validate(basepath,out):
 base=json.loads(Path(basepath).read_text());overlay=build(base);allassets=dict(base,**overlay);checks=[]
 def ck(test,label):assert test,label;checks.append(label)
 rows=list(csv.DictReader(io.StringIO(overlay['genesis_life_rework'])));by={r['ScenarioID']:r for r in rows};schema={r['key']:r for r in csv.DictReader(io.StringIO(overlay['genesis_rework_defaults']))}
 for key in KEYS:ck(key in schema and schema[key]['type']=='string','native projection string declared '+key)
 for n in range(1,5):
  for image in [False,True]:
   r=by[route('panel'+str(n)+('image'if image else''))]
   ck(r['Title']=='<GFC.life_rework.MTitle1109>'and r['Body']=='<GFC.life_rework.MBody1109>','original popup projects text')
   for i in range(1,5):ck((r['Choice'+str(i)+'_Text']=='<GFC.life_rework.MChoice'+str(i)+'1109>')if i<=n else not r['Choice'+str(i)+'_Text'],'exact active choice count')
   for i in range(n):ck(r['Choice'+str(i+1)+'_RouteTo']==route('choose_'+str(i)),'literal dispatch route')
   ck(bool(r['BigImageString'])==image,'plain popup needs no image placeholder')
 for name,text in overlay.items():
  if text.startswith('ScenarioID,'):
   header=text.splitlines()[0];count=len(next(csv.reader([header])))
   for line in text.splitlines()[1:]:
    if not line:continue
    parsed=native_tokens(line);ck(len(parsed)==count,'native physical record parses '+name)
 root=json.loads(overlay['genesis_military1108']);ck(len(root['Items'])==7,'original Genesis service list has seven real entries')
 ck(all('native_'in json.dumps(r) for r in root['Items']),'all service list entries use native dispatch IDs')
 auto=list(csv.DictReader(io.StringIO(overlay['genesis_native_automatic1109'])));ck(sum(not r['Filter']for r in auto)==1,'one automatic entry and no random continuation')
 ck(all('MayoMods'not in by[route('panel'+str(n))]['ExteriorTitle']for n in range(1,5)),'context labels remain relevant to the activity')
 report=dict(passed=True,checks=len(checks),authored_assets_sha256=hashlib.sha256(json.dumps(overlay,sort_keys=True).encode()).hexdigest(),physical_native_CSV_records_checked=True,original_Genesis_and_ScenarioBase=True,phone_rendering_tested=False);Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
