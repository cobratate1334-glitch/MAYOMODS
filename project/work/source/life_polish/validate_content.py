"""Validate exact native physical records, references and annual continuations."""
import csv,hashlib,io,json,re,sys
from pathlib import Path
from collections import Counter
from life_polish.content import build
from ui_integrity.validate_content import native_tokens


def validate(basepath,out):
    base=json.loads(Path(basepath).read_text());overlay=build(base);assets={**base,**overlay};checks=[]
    def ck(value,label):assert value,label;checks.append(label)
    schemas={}
    text=assets['genesis_feature_containers'];registry=list(csv.DictReader(io.StringIO(text[text.index('ContainerId,'):])))
    for row in registry:
        sheet=assets.get(row.get('InitDataSheet'),'')
        if sheet.startswith('key,'):schemas[row['ContainerId']]={r['key']for r in csv.DictReader(io.StringIO(sheet))}
    scenes={}
    for name,value in assets.items():
        if value.startswith('ScenarioID,'):
            rows=list(csv.DictReader(io.StringIO(value)));scenes.update({r['ScenarioID']:r for r in rows})
    for name,value in overlay.items():
        if value.startswith('ScenarioID,'):
            rows=list(csv.DictReader(io.StringIO(value)));width=len(next(csv.reader([value.splitlines()[0]])))
            ck(not [k for k,n in Counter(r['ScenarioID']for r in rows).items()if n>1],name+' has unique scenarios')
            for line in value.splitlines()[1:]:
                if line:ck(len(native_tokens(line))==width,name+' physical native record')
            for row in rows:
                for owner,key in re.findall(r'<GFC\.([^.>]+)\.([^>]+)>',str(row)):
                    ck(key in schemas.get(owner,set()),'registered field '+owner+'.'+key)
                for field in [k for k in row if k.endswith(('_RouteTo','_AdvancedLogic'))]:
                    value=row[field]
                    for target in re.findall(r'scenario\.[A-Za-z0-9_.]+',value):ck(target in scenes,'scene '+target)
                    for owner,key in re.findall(r'BP_GFC_(?:MODIFY_PROPERTY|SET_STRING)=([^:>]+):([^:>]+):',value):
                        ck(key in schemas.get(owner,set()),'write '+owner+'.'+key)
                    for target in re.findall(r'BP_SHOW_LIST=([A-Za-z0-9_]+)',value):ck(target in assets,'list '+target)
        elif value.startswith('{'):
            data=json.loads(value)
            for tile in data.get('Items',data.get('ListItems',[])):
                for action in tile.get('ActionList',[]):
                    for condition in action.get('ConditionList',[]):
                        if 'ListID'in condition:ck(condition['ListID']in assets,'tile list '+condition['ListID'])
                        if 'ScenarioID'in condition:ck(condition['ScenarioID']in scenes,'tile scene '+condition['ScenarioID'])
    # Each annual sheet needs local copies: native continuations stay inside
    # their controller, so a globally repaired row alone is insufficient.
    for name in ['genesis_chronicle1110','genesis_school1110','genesis_callup1110','genesis_prison1110','genesis_service1110']:
        rows=list(csv.DictReader(io.StringIO(assets[name])));local={r['ScenarioID']for r in rows}
        for row in rows:
            for target in re.findall(r'scenario\.[A-Za-z0-9_.]+',' '.join(v for k,v in row.items()if k.endswith(('_RouteTo','_AdvancedLogic')))):
                # Original queued native panels intentionally use a separate
                # fresh resource/controller; all school authored children local.
                if 'school'in target.lower() or 'exam_'in target.lower():ck(target in local,name+' local continuation '+target)
            if row.get('IsAgeUpScenario','').lower()!='true':
                ck(row.get('Filter')=='[gfc.life_rework.AnnualContinuation1106=1]',name+' manual row cannot draw randomly')
    report=dict(passed=True,checks=len(checks),authored_assets_sha256=hashlib.sha256(json.dumps(overlay,sort_keys=True).encode()).hexdigest(),changed_text_assets=len(overlay),physical_native_records=True,reference_closure=True,phone_tested=False)
    Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
