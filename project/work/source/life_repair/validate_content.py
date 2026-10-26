"""Route, schema and gameplay regression checks using the actual content overlay."""
import copy,csv,hashlib,io,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent;sys.path[:0]=[str(SOURCE)]
from life_repair.content import build
from life_rework.content import scene
from life_rework.validate_content import Model as Previous
from social_roblox.test_content import Model as Foundation


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
    base=json.loads(Path(base_path).read_text());m=Model(base);checks=[]
    def check(value,label):assert value,label;checks.append(label)
    icons={r['EmojiString']for r in csv.DictReader(io.StringIO(m.assets['genesis_lookup_emoji_visuals']))}
    for name,value in build(base).items():
        if not value.startswith('{'):continue
        data=json.loads(value)
        for item in data.get('Items',data.get('ListItems',[])):
            for action in item.get('ActionList',[]):
                for condition in action.get('ConditionList',[]):
                    if 'ScenarioID'in condition:
                        target=condition['ScenarioID'];check(target in m.rows,'list row has a real registered scenario '+str(target))
                    if 'ListID'in condition:check(condition['ListID']in m.assets,'list row has a registered child list')
    for row in [r for k,r in m.rows.items()if k.startswith('scenario.lifeRework.')]:
        check(row['EmojiString']in icons or row['EmojiString'].startswith(('mayomods49/','mayomods1104/')),'registered icon '+row['EmojiString'])
        for owner,key in re.findall(r'<GFC\.([^.>]+)\.([^>]+)>',str(row)):check(key in m.schemas[owner],'readable field '+owner+'.'+key)
        for i in range(1,5):
            if not row.get(f'Choice{i}_Text'):continue
            advanced=row[f'Choice{i}_AdvancedLogic'];routes=[row[f'Choice{i}_RouteTo']]
            if advanced:
                data=json.loads(advanced);routes=[c['then']['route_options'][0]['route_to']for c in data['cases']]+[data['else_when_no_matches']['route_options'][0]['route_to']]
                for c in data['cases']:m.condition(c['if'])
            for route in routes:
                check(isinstance(route,str),'flat Genesis destination')
                for part in m.split(route):
                    if part.startswith('scenario.'):check(part in m.rows,'registered scene '+part)
                    if part.startswith('BP_SHOW_LIST='):check(part.split('=',1)[1]in m.assets,'registered parent '+part)
                    if part.startswith('BP_GFC_'):
                        owner,key=part.split('=',1)[1].split(':',2)[:2];check(key in m.schemas[owner],'registered write '+owner+'.'+key)
    # New flow tests use the same authored routes as the packaged game.
    t=Model(base,25);t.r.update(Year=1939,NativeInPrison1105=0,NativeBank1105=10000);t.bank=10000
    t.choose('heist_crew1106',1);check(t.r['HeistCrew1106']==1,'join is saved inside the crew hub')
    t.choose('heist_offer1106_1',1);check(t.bank==9900 and t.r['HeistStage1106']==1,'job preparation debits the real bank route')
    for stage in range(1,4):t.choose('heist_round1106_'+str(stage),1)
    t.r.update(HeistSkill1106=70,Roll=80);t.choose('heist_finish1106');check(t.r['HeistMissionAge1106']==25,'job completion consumes the yearly attempt')
    t.choose('heist_split1106',1);check(t.bank==10200 and t.r['HeistLoot1106']==0,'fair share is exactly 25 percent and the pot is consumed')
    bank=t.bank;t.choose('heist_split1106',1);check(t.bank==bank,'stale split cannot pay twice')
    t=Model(base,4);t.r.update(Year=1939,NativeBank1105=10000);t.choose('heist_crew1106',1);check(t.r['HeistCrew1106']==0,'young child cannot join or start a heist')
    t=Model(base,14);t.r.update(SchoolEligible=1,SchoolPeerPresent1105=1);t.choose('school_fight1106');check(t.r['SchoolNativeFight1106']==1,'school fight routes to native attack bridge')
    t=Model(base,7);t.r.update(SchoolEligible=1);t.choose('school_case1106_7',1);check(112 in t.native,'childhood event changes actual classmate relationship')
    t=Model(base,25);t.r.update(War=2,WarSide=1,NativeMilitary=1,Deployed=1,NativeInPrison1105=0,Year=1941,Roll=50)
    t.choose('trench_start1106');t.r['TrenchSafe11106']=0;t.choose('trench_round1106_1',1);check(t.r['WarAmmo1106']==3 and t.r['TrenchScore1106']==1,'trench decisions spend ammunition and score a clear approach')
    t.r['WarAmmo1106']=1;t.r['TrenchSafe21106']=0;t.choose('trench_round1106_2',1);check(t.r['TrenchStage1106']==1,'empty magazine prevents firing another volley')
    t.r['WarSupplies']=20;t.choose('trench_pause1106_2',1);check(t.r['WarAmmo1106']==5 and t.r['WarSupplies']==18,'reload consumes supplies and restores period magazine')
    t=Model(base,25);t.r.update(War=2,WarSide=1,CommandActive1106=1,CommandBudget1106=100,CommandReadiness1106=100,CommandLogistics1106=100,Year=1939,CommandPermit01106=0)
    t.choose('command_offer1106_0');check(t.r['CommandTurnAge1106']==-1,'stale foreign-country offer cannot order an invasion')
    t.r['CommandPermit01106']=1;t.choose('command_offer1106_0');check(t.r['CommandBudget1106']==75 and t.r['CommandTerritories1106']==1,'prepared campaign spends treasury and records territory')
    value=t.r.copy();t.choose('command_offer1106_0');check(t.r==value,'campaign cannot repeat in the same year')
    annual=list(csv.DictReader(io.StringIO(m.assets['genesis_rework_annual1105'])));ids={r['ScenarioID']for r in annual}
    check(len([r for r in annual if r['ScenarioID'].startswith('scenario.lifeRework.annual_school1106_')])==18,'eighteen additional age-specific annual school stories')
    entry_ids={r['ScenarioID']for r in annual if r.get('IsAgeUpScenario','').lower()=='true'}
    for r in annual:
        if r['ScenarioID'] in entry_ids:
            for i in range(1,5):
                target=r.get('Choice'+str(i)+'_RouteTo','')
                for part in m.split(target):
                    if part.startswith('scenario.'):check(part in ids,'annual controller contains its explicit continuation '+part)
    check(all(r.get('Filter')=='[gfc.life_rework.AnnualContinuation1106=1]'for r in annual if r['ScenarioID']not in entry_ids)and m.schemas['life_rework']['AnnualContinuation1106']['maximum']=='0','raw annual filter excludes manual pages using an immutable zero field')
    check(all('[gfc.life_rework.WarNews1105=0]'in r['Filter']for r in annual if r['ScenarioID']in entry_ids and r['ScenarioID']!=scene('annual_world1105')),'war headline cannot lose selection to unrelated yearly entries')
    t=Model(base,25);t.r.update(DraftEligible1105=1,WarNews1105=1);t.choose('annual_world1105');check(t.scene==scene('annual_callup_prompt1105'),'war headline continues into an eligible call-up')
    t=Model(base,14);t.r.update(DraftEligible1105=0,WarExtraNews1106=0,SchoolEligible=1,SchoolEvent1105=13);t.choose('annual_world1105');check(t.scene==scene('annual_school1106_13'),'war news still continues into the student school event')
    t=Model(base,25);t.r.update(War=2,WarSide=1);t.choose('spy_start1106');t.choose('spy_round1106_1',2);t.choose('spy_round1106_2',1);t.choose('spy_round1106_3',3);before=t.r['WarIntel'];t.choose('spy_result1106');check(t.r['WarIntel']==before+15,'decoded intelligence improves the saved campaign briefing')
    value=t.r.copy();t.choose('spy_result1106');check(t.r==value,'intelligence result cannot be replayed')
    for r in m.rows.values():
        if r['ScenarioID'].startswith('scenario.lifeRework.'):
            check('mayomods'not in r.get('ExteriorTitle','').lower(),'contextual popup heading '+r['ScenarioID'])
    r=m.rows['scenario.lifeRework.storm_record'];check('scenario.lifeRework.storm_report_wait1106'in r['Choice1_AdvancedLogic'],'report rejection has a distinct popup instead of a self-route')
    report=dict(passed=True,checks=len(checks),scenarios=sum(k.startswith('scenario.lifeRework.')for k in m.rows),authored_assets_sha256=hashlib.sha256(json.dumps(build(base),sort_keys=True).encode()).hexdigest(),Genesis_API_modeled=True,phone_tested=False)
    Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)


if __name__=='__main__':validate(*sys.argv[1:])
