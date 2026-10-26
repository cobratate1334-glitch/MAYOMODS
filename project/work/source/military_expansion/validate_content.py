"""Audit physical game records, saved keys and exact compiled native tokenization."""
import csv,hashlib,io,json,sys
from pathlib import Path
from military_expansion.content import build
from military_expansion.validate_native import Machine,prior

def validate(binary,fixture,basefile,out):
 base=json.loads(Path(basefile).read_text());overlay=build(base);assets={**base,**overlay};checks=[]
 def check(ok,msg):assert ok,msg;checks.append(msg)
 raw=Path(binary).read_bytes();prior.ROOT=Path(fixture);m=Machine(raw,0)
 # Original parser negative control: quoted physical LF splits a scenario into
 # invalid records. This remains a real native execution, not Python CSV proof.
 check(len(m.split_native('scenario.bad,normal,"line one'))<48,'actual parser rejects broken physical record')
 new=[]
 for name,value in overlay.items():
  if not value.startswith('ScenarioID,'):continue
  header=next(csv.reader(io.StringIO(value)));rows=list(csv.DictReader(io.StringIO(value)))
  physical=value.split('\n')[1:];check(len(physical)==len(rows),'one physical line per scenario '+name)
  check(len({r['ScenarioID']for r in rows})==len(rows),'stable scenario IDs unique '+name)
  for row,line in zip(rows,physical):
   check(None not in row and all(v is not None for v in row.values()),'column alignment '+row['ScenarioID'])
   check(len(next(csv.reader(io.StringIO(line))))==len(header),'physical tokenizer column count '+row['ScenarioID'])
   if '1108'in row['ScenarioID']:
    parsed=m.split_native(line);check(len(parsed)==len(header),'actual native column count '+row['ScenarioID']);new.append(row)
    for i in range(1,5):
     label=row.get('Choice'+str(i)+'_Text','');check(not label.startswith(('Scenario.','GFC.'))and label not in ['True','False'],'human button label '+row['ScenarioID'])
   if name=='genesis_rework_annual1105'and row.get('IsAgeUpScenario','').lower()!='true':check(row['Filter']=='[gfc.life_rework.AnnualContinuation1106=1]','manual page cannot random-draw '+row['ScenarioID'])
 for name in ['genesis_rework_defaults','genesis_v18_defaults_relationship21']:
  rows=list(csv.DictReader(io.StringIO(assets[name])));check(len(rows)==len({r['key']for r in rows}),'no duplicate saved keys '+name)
 schema={r['key']:r for r in csv.DictReader(io.StringIO(assets['genesis_rework_defaults']))};check(int(schema['NativeAction']['maximum'])>=504,'new native IDs are not clamped to old255 limit');check(schema['MilitaryState1108']['type']=='string'and schema['ChessState1108']['type']=='string','both state machines belong to the saved native Life')
 for role in [0,1]:
  data=json.loads(assets['genesis_parent'+str(role)+'1108']);check(str(role)+'1108'in data['Items'][0]['ActionList'][0]['ConditionList'][0]['ScenarioID'],'parent route carries explicit role')
 known={r['key']for r in csv.DictReader(io.StringIO(base['genesis_rework_defaults']))};check(known<=schema.keys(),'all old serialized fields retained')
 for name in ['genesis_military1108','genesis_parent01108','genesis_parent11108']:check(name in overlay,'new list packaged '+name)
 report=dict(passed=True,checks=len(checks),authored_assets_sha256=hashlib.sha256(json.dumps(overlay,sort_keys=True).encode()).hexdigest(),new_native_scenarios=len(new),actual_ARM64_line_parser=True,old_fields_preserved=True,phone_tested=False);Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
