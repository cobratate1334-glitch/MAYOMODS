"""Check the game's physical-line CSV contract, actual routes and era transactions."""
import csv,hashlib,io,json,re,sys
from pathlib import Path
from ui_integrity.content import build
from life_repair.validate_content import Model as Previous
from social_roblox.test_content import Model as Foundation
from life_rework.content import scene


def native_tokens(line):
    remaining=line.count('"');start=0;parts=[]
    for i,ch in enumerate(line):
        if ch=='"':remaining-=1
        elif ch==','and remaining%2==0:parts.append(line[start:i]);start=i+1
    parts.append(line[start:]);return parts


class Model(Previous):
 def __init__(self,base,age=20):
    Foundation.__init__(self,age);self.assets={**base,**build(base)};self.rows={};self.native=[]
    for name,value in self.assets.items():
        if value.startswith('ScenarioID,'):self.rows.update({r['ScenarioID']:r for r in csv.DictReader(io.StringIO(value))})
    lines=self.assets['genesis_feature_containers'].splitlines();start=next(i for i,s in enumerate(lines)if s.startswith('ContainerId,'));self.registry=list(csv.DictReader(io.StringIO('\n'.join(lines[start:]))))
    for row in self.registry:
        sheet=row.get('InitDataSheet')
        if not sheet or not self.assets.get(sheet,'').startswith('key,'):continue
        defs={r['key']:r for r in csv.DictReader(io.StringIO(self.assets[sheet]))};self.schemas[row['ContainerId']]=defs
        self.props[row['ContainerId']]={k:int(r['value'])if r['type']=='int'else r['value']for k,r in defs.items()}


def validate(base_path,out):
    base=json.loads(Path(base_path).read_text());overlay=build(base);assets={**base,**overlay};m=Model(base);checks=[];physical=0
    def check(v,label):assert v,label;checks.append(label)
    old=next(l for l in base['genesis_life_rework'].split('\n')if l.startswith('scenario.lifeRework.command_home1106,'))
    check(len(native_tokens(old))<48,'negative control reproduces native column loss in old command popup')
    for name,text in overlay.items():
        if not text.startswith('ScenarioID,'):continue
        lines=text.split('\n');header=next(csv.reader([lines[0]]));logical=list(csv.reader(io.StringIO(text)))
        check(len(lines)==len(logical),'one physical line per scenario: '+name)
        for line,expected in zip(lines[1:],logical[1:]):
            parts=native_tokens(line);physical+=1
            check(len(parts)==len(header),'native field count '+name+' '+expected[0])
        for row in csv.DictReader(io.StringIO(text)):
            for col,value in row.items():
                if col.endswith('_AdvancedLogic')and value:json.loads(value)
    entity=list(csv.reader(io.StringIO(assets['genesis_entity_defs'])));check(all(r[1]in ['npc','object']and isinstance(json.loads(r[7]or'{}'),dict)for r in entity),'entity records contain neither comment preamble nor mistaken header NPC')
    regular=list(csv.DictReader(io.StringIO(assets['genesis_life_rework'])));annual=list(csv.DictReader(io.StringIO(assets['genesis_rework_annual1105'])))
    for row in regular:
        for i in range(1,5):
            label=row.get(f'Choice{i}_Text','');check(not(label.startswith('scenario.')or label.lower()in ['true','false']),'human button label '+row['ScenarioID'])
            routes=[row.get(f'Choice{i}_RouteTo','')];advanced=row.get(f'Choice{i}_AdvancedLogic','')
            if advanced:
                data=json.loads(advanced);routes=[c['then']['route_options'][0]['route_to']for c in data['cases']]+[data['else_when_no_matches']['route_options'][0]['route_to']]
                for c in data['cases']:m.condition(c['if'])
            for route in routes:
                for part in m.split(route):
                    if part.startswith('scenario.'):check(part in m.rows,'real scenario target '+part)
                    if part.startswith('BP_SHOW_LIST='):check(part.split('=',1)[1]in assets,'real parent menu '+part)
    # Physical-row selectors: an infant in 2026/2028 cannot draw manual war pages.
    entries=[r for r in annual if r.get('IsAgeUpScenario','').lower()=='true'];manual=[r for r in annual if r not in entries]
    check(all(r['Filter']=='[gfc.life_rework.AnnualContinuation1106=1]'for r in manual),'all manual annual copies are excluded by the real raw Filter field')
    for year in [2026,2028]:
        t=Model(base,2);t.r.update(Year=year,War=0,WarSide=0,SchoolEligible=0,SchoolEvent1105=0,WarNews1105=0,DraftEligible1105=0,WorldEncounter1106=0,WarExtraNews1106=0)
        t.choose('command_home1106',2);check(t.scene==scene('war_unavailable1107'),'infant cannot open command economy in '+str(year))
    t=Model(base,30);t.r.update(Year=2026,War=0,WarSide=0);t.choose('command_start1106');check(t.r['CommandActive1106']==0 and t.scene==scene('war_unavailable1107'),'peacetime adult cannot activate the WWII command')
    for year,shelf,contains in [(1900,1900,'Typewriter'),(1940,1920,'Table radio'),(1980,1920,'Table radio'),(1985,1983,'Mobile phone'),(2000,1989,'Laptop'),(2010,2007,'iPhone'),(2018,2017,'Nintendo Switch'),(2026,2020,'PlayStation 5')]:
        t=Model(base,30);t.r['Year']=year;t.choose('period_shop1107');check(t.scene==scene('device_shelf1107_'+str(shelf)),'era selects only its shelf '+str(year))
        page=t.rows[t.scene];labels=[page.get('Choice'+str(i)+'_Text')for i in range(1,4)];check(contains in labels,'expected period technology '+str(year))
    t=Model(base,20);t.bank=2000;t.r.update(Year=2026,NativeBank1105=2000);t.choose('item1107_iphone');check(t.bank==1301 and t.r['Owned1107_iphone']==1,'real bank debit and saved iPhone ownership')
    t.choose('item1107_iphone');check(t.bank==1301,'duplicate purchase cannot debit twice');t.choose('item1107_iphone',2);check(111 in t.native,'owned item use invokes actual native wellbeing action');before=len(t.native);t.choose('item1107_iphone',2);check(len(t.native)==before,'item use cannot be farmed in the same year')
    for year,age,key in [(1900,30,'iphone'),(2010,30,'switch'),(2026,12,'vape')]:
        t=Model(base,age);t.bank=10000;t.r.update(Year=year,NativeBank1105=10000);t.choose('item1107_'+key);check(t.bank==10000 and t.r['Owned1107_'+key]==0,'stale direct purchase blocked '+key+' '+str(year))
    report=dict(passed=True,checks=len(checks),physical_scenario_records=physical,authored_assets_sha256=hashlib.sha256(json.dumps(overlay,sort_keys=True).encode()).hexdigest(),CSV_token_model_matches_native_probe=True,Genesis_API_modeled=True,phone_tested=False)
    Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
