"""Route/economy model with real ARM64 execution of the reserved saved-state bridges.

Genesis expression parsing, banking and scene rendering are modeled boundaries.
This catches progression, missing properties, double rewards and skipped costs.
"""
import copy,csv,hashlib,io,json,math,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native_v29'))
import test_native
test_native.ROOT=ROOT
from test_release20 import ReleaseMachine

class Model:
    def __init__(self,binary,age=18,bank=1000000,country='Brazil'):
        self.machine=ReleaseMachine(binary,0);self.props=self.machine.props;self.age=age;self.bank=bank;self.scene='';self.random=50
        self.machine.w(self.machine.hero+0x20,age);self.machine.location('Town',country);
        if 6<=age<=24:self.machine.student(1 if age<18 else 2,age=age)
        self.machine.run('NativeWorldSync20',1,'world20');self.assets=json.loads((ROOT/'assets.json').read_text())
        self.rows={r['ScenarioID']:r for r in csv.DictReader(io.StringIO(self.assets['genesis_activities_v18']))};self.schemas={}
        for name,value in {**json.load(open('analysis/base_assets.json')),**self.assets}.items():
            if re.match(r'genesis_v\d+_defaults_',name):self.schemas[re.sub(r'genesis_v\d+_defaults_','',name)]={r['key']:r for r in csv.DictReader(io.StringIO(value))}
    @property
    def p(self):return self.props['community35']
    def token(self,value):
        if value=='hero:age':return self.age
        if value.startswith('GFC.'):
            _,owner,key=value.split('.',2);assert key in self.props[owner],(owner,key);return self.props[owner][key]
        if value.startswith('function:'):
            _,name,*args=value.split(':');args=[float(x)for x in args]
            return {'add':lambda:sum(args),'sub':lambda:args[0]-sum(args[1:]),'mul':lambda:math.prod(args),'div':lambda:args[0]/args[1],
                'clamp':lambda:max(args[1],min(args[2],args[0])),'max':lambda:max(args),'min':lambda:min(args),'abs':lambda:abs(args[0])}[name]()
        raise AssertionError('Unknown token '+value)
    def resolve(self,value):
        pattern=r'<((?:GFC\.|hero:|function:)[^<>]+)>'
        while re.search(pattern,value):value=re.sub(pattern,lambda m:str(self.token(m[1])),value)
        return value
    def number(self,value):return float(self.resolve(str(value)))
    def condition(self,test):
        if 'filter'in test:
            expr=self.resolve(test['filter']).strip('[]').replace('finance.bankBalance',str(self.bank));return bool(eval(expr,{'__builtins__':{}},{}))
        expr=self.resolve(test.get('expression','True')).replace('&&',' and ').replace('||',' or ')
        return bool(eval(expr,{'__builtins__':{}},{}))
    def advanced(self,data):
        for case in data['cases']:
            if self.condition(case['if']):return case['then']['route_options'][0]['route_to']
        return data['else_when_no_matches']['route_options'][0]['route_to']
    def split(self,route):
        parts=[];start=0;depth=0;n=0
        while n<len(route):
            if route[n]=='<':depth+=1
            elif route[n]=='>'and depth:depth-=1
            elif route[n:n+2]=='>>'and not depth:parts.append(route[start:n]);n+=2;start=n;continue
            n+=1
        parts.append(route[start:]);return parts
    def route(self,route):
        for part in self.split(route):
            if not part:continue
            if part.startswith('BP_GFC_MODIFY_PROPERTY='):
                owner,key,operation=part.split('=',1)[1].split(':',2);schema=self.schemas[owner][key];values=self.props[owner]
                value=self.number(operation[1:]);value=value if operation[0]=='='else values[key]+value if operation[0]=='+'else values[key]-value
                values[key]=max(int(schema['minimum']),min(int(schema['maximum']),int(value)))
                if key.startswith('Native'):
                    self.machine.rolls=[self.random]*20;self.machine.w(self.machine.hero+0x20,self.age)
                    if key=='NativeCupRoll':
                        # The older random-roll bridge lies after the v18 hook.
                        # Execute that retained chain instead of stopping early.
                        self.machine.q(self.machine.bp+24,self.machine.managed(key))
                        self.machine.execute(self.machine.end,0x63194c0,{0:1,19:self.machine.bp,20:values[key],21:self.machine.ctx(owner)})
                    else:self.machine.run(key,values[key],owner)
            elif part.startswith('BP_GFC_SET_STRING='):
                owner,key,value=part.split('=',1)[1].split(':',2);assert self.schemas[owner][key]['type']=='string';self.props[owner][key]=self.resolve(value)
            elif part.startswith('BP_BANK_BALANCE='):self.bank+=int(self.number(part.split('=',1)[1]))
            elif part.startswith('BP_SHOW_LIST='):
                target=part.split('=',1)[1];assert target in self.assets or target in json.load(open('analysis/base_assets.json'));self.scene=target
            elif part.startswith('scenario.'):
                assert part in self.rows,part;self.scene=part
            else:raise AssertionError('Unknown blueprint '+part)
    def choose(self,key,index=1):
        row=self.rows['scenario.activitiesV18.c35_'+key];assert row[f'Choice{index}_Text'],(key,index)
        logic=row[f'Choice{index}_AdvancedLogic'];self.route(self.advanced(json.loads(logic))if logic else row[f'Choice{index}_RouteTo']);return self.scene.rsplit('.',1)[-1]
    def ageup(self):
        self.age+=1;self.machine.w(self.machine.hero+0x20,self.age)
        for owner,schemas in self.schemas.items():
            for key,row in schemas.items():
                if row['reset_on_ageup']=='true':self.props[owner][key]=int(row['value'])if row['type']=='int'else row['value']
    def snapshot(self):return json.loads(json.dumps({'age':self.age,'bank':self.bank,'props':self.props}))

def validate(path):
    binary=Path(path).read_bytes();m=Model(binary);checks=0;assets=m.assets
    all_rows=list(m.rows.values());old_ids={r['ScenarioID']for r in csv.DictReader(io.StringIO(json.load(open(ROOT.parent/'native_v34/assets.json'))['genesis_activities_v18']))};new=[r for r in all_rows if r['ScenarioID']not in old_ids]
    assert len(new)==json.load(open(ROOT/'community35_authoring.json'))['new_scenarios'] and len(m.rows)==len(all_rows);checks+=1
    for row in new:
        assert row['HasDismissButton']=='true';assert sum(bool(row[f'Choice{n}_Text'])for n in range(1,5))in range(1,5);checks+=1
        for owner,key in re.findall(r'<GFC\.([^.>]+)\.([^>]+)>',str(row)):assert key in m.schemas[owner];checks+=1
        for name in re.findall(r'<function:([^:<>]+):',str(row)):assert name in {'add','sub','mul','div','clamp','max','min','abs'};checks+=1
    # Every newly authored route resolves to an existing scene/list and property.
    def routes(row):
        result=[]
        for n in range(1,5):
            if row[f'Choice{n}_RouteTo']:result.append(row[f'Choice{n}_RouteTo'])
            if row[f'Choice{n}_AdvancedLogic']:
                data=json.loads(row[f'Choice{n}_AdvancedLogic']);result += [c['then']['route_options'][0]['route_to']for c in data['cases']]+[data['else_when_no_matches']['route_options'][0]['route_to']]
        return result
    for row in new:
        for route in routes(row):
            for part in m.split(route):
                if part.startswith('scenario.'):assert part in m.rows
                if part.startswith('BP_GFC_'):
                    owner,key=part.split('=',1)[1].split(':',2)[:2];assert key in m.schemas[owner]
            checks+=1
    # Traits have a visible name and an actual effect, without changing old IDs.
    m=Model(binary,age=18);m.choose('trait8');before=m.p['MangaQuality'];m.choose('manga_work',1);assert m.p['MangaQuality']==before+7;checks+=1
    m.choose('trait6');before=m.p['Relative0Connection'];m.choose('relative0');assert m.p['Relative0Connection']==before+12;checks+=1
    m.choose('trait4');before=m.p['SchoolSupport'];m.choose('school_social');assert m.p['SchoolSupport']==before+12;checks+=1
    # Pitch, assistants, chapters, catalogue, adaptation and duplicate royalties.
    m=Model(binary,age=16,bank=1000000);m.choose('manga_work');m.choose('manga_work');m.choose('manga_work');m.choose('manga_concept');m.choose('manga_genre');m.choose('manga_pitch');assert m.p['MangaActive']==1 and m.bank==999750;checks+=1
    before=m.bank;m.choose('manga_deadline');assert m.p['MangaAssistants']==1 and m.bank==before-500;checks+=1
    m.choose('manga_deadline',2);before=m.bank;m.choose('manga_publish');assert m.p['MangaWeek']==1 and m.bank==before-200;checks+=1
    before=m.bank;m.choose('manga_record');assert m.bank>before;paid=m.bank;m.choose('manga_record');assert m.bank==paid;checks+=1
    m.p['MangaSales']=2000000;m.age=18;m.p['MangaWork']=0;m.choose('anime_studio',2);m.choose('anime_cast',2)
    for n in range(12):
        if m.p['MangaWork']==8:m.ageup()
        m.choose('anime',3)
    assert m.p['AnimeEpisodes']==12;checks+=1;m.choose('anime_complete');assert m.p['AnimeSeries']==1;checks+=1
    before=m.snapshot();m.choose('anime_complete');assert m.snapshot()==before;checks+=1
    m=Model(binary,age=18,bank=0);m.p.update(MangaQuality=50);before=m.snapshot();m.choose('manga_pitch');assert m.snapshot()==before;checks+=1
    # Television: complete/renewed and canceled seasons, limits and payments.
    m=Model(binary);m.choose('tv_pitch');m.choose('tv_network');m.choose('tv_cast');m.choose('tv_cast')
    for n in range(6):m.choose('tv_episode_plan',2)
    assert m.p['TVEpisode']==6;checks+=1;m.choose('tv_review');assert m.p['TVActive']==1 and m.p['TVSeason']==2 and m.p['TVCompleted']==1;checks+=1
    m.choose('tv_review',2);before=m.bank;m.choose('tv_review',2);assert m.bank==before;checks+=1
    m.ageup();m.p.update(TVEpisode=6,TVRating=0);m.choose('tv_review');assert m.p['TVCanceled']==1 and m.p['TVActive']==0;checks+=1
    # Country-aware farming, insurance, no early harvest, loss and bankruptcy.
    m=Model(binary,country='Australia');m.route('BP_GFC_MODIFY_PROPERTY=world20:NativeWorldSync20:=1');assert m.p['FarmClimate']==2 and m.p['FarmHemisphere']==1;checks+=1
    m.choose('farm_setup');assert m.bank==950000 and m.p['FarmCountry']=='Australia';checks+=1
    for n in range(3):m.choose('farm_setup',3)
    m.choose('farm_water');m.choose('farm_plant');m.choose('farm_water',2)
    before=m.snapshot();assert m.choose('farm_calendar',2)=='c35_farm_early'and m.snapshot()==before;checks+=1
    m.random=99;m.choose('farm_calendar');m.choose('farm_weather');m.choose('farm_calendar');m.choose('farm_weather');m.choose('farm_calendar',2)
    assert m.p['FarmHarvests']==1 and m.p['FarmPlanted']==0 and m.p['FarmYield']>0;checks+=1
    before=m.bank;m.choose('farm_calendar',2);assert m.bank==before;checks+=1
    m=Model(binary);m.p.update(FarmLand=1,FarmPlanted=1,FarmCropStage=2,FarmPlantAge=18,FarmWeather=0,FarmRisk=95,FarmDebt=24000,FarmMachines=2,FarmIrrigation=1)
    m.choose('farm_calendar',2);assert m.p['FarmBankrupt']==1 and m.p['FarmLand']==0 and m.p['FarmMachines']==0 and m.p['FarmDebt']==0;checks+=1
    # School bullying, support, fights, campus voting and finite project budget.
    m=Model(binary,age=15);m.random=0;m.choose('school',2);m.choose('school_encounter');assert m.scene.endswith('school_bully');checks+=1
    m.choose('school_bully',3);assert m.p['SchoolWarnings']==1 and m.p['SchoolStress']>0;checks+=1
    m.choose('school',3);m.choose('campus');m.choose('campus_campaign');m.choose('campus_campaign');m.choose('campus',2);m.choose('campus_vote');assert m.p['CampusPresident']==1 and m.p['CampusBudget']==5000;checks+=1
    m.choose('campus_projects');assert m.p['CampusBudget']==4000 and m.p['CampusProjects']==1;checks+=1
    before=m.snapshot();m.choose('campus_vote');assert m.snapshot()==before;checks+=1
    m.ageup();m.choose('school',3);assert m.p['CampusPresident']==0;checks+=1
    m=Model(binary,age=0);before=m.snapshot();m.choose('relative5');assert m.snapshot()==before and m.scene.endswith('relative_unborn');checks+=1
    m=Model(binary,age=60);before=m.snapshot();m.choose('relative0');assert m.snapshot()==before and m.scene.endswith('relative_memorial');checks+=1
    # Direct shops: age/affordability/inventory guards, risk and recovery.
    for age,bank in [(17,10000),(18,0)]:
        m=Model(binary,age=age,bank=bank);before=m.snapshot();m.choose('drug0');assert m.snapshot()==before;checks+=1
    m=Model(binary);m.choose('drug2');assert m.p['Drug2']==1 and m.bank==999880;checks+=1
    m.choose('drug2',2);assert m.p['Drug2']==0 and m.p['Dependence']==10;checks+=1
    before=m.snapshot();m.choose('drug2',2);assert m.snapshot()==before;checks+=1
    m.p.update(Dependence=80,ShopSessions=0);m.choose('drug_inventory');assert m.p['Dependence']==60;checks+=1
    m.choose('weapon4');assert m.p['Weapon4']==1;before=m.bank;m.choose('weapon4',2);assert m.p['Weapon4']==0 and m.bank==before+1600;checks+=1
    before=m.snapshot();m.choose('weapon4',2);assert m.snapshot()==before;checks+=1
    # Child soccer: age gates, explicit acceptance, match stats and Brazil 16.
    m=Model(binary,age=5);before=m.snapshot();m.choose('soccer');assert m.snapshot()==before;checks+=1
    m.age=6
    for n in range(3):m.choose('soccer')
    m.age=8;m.p['SoccerSessions']=0;m.choose('soccer',2);assert m.p['SoccerAcademy']==0;checks+=1
    m.choose('soccer_offer');assert m.p['SoccerAcademy']==1;checks+=1
    for n in range(4):m.choose('soccer_academy')
    assert m.p['SoccerYouthCaps']==4 and m.p['SoccerGoals']>0;checks+=1
    m.age=16;m.p['SoccerScouts']=25;m.route('BP_GFC_MODIFY_PROPERTY=world20:NativeWorldSync20:=1');m.choose('soccer_contract');assert m.p['SoccerSigned']==1;checks+=1
    before=m.bank;m.choose('soccer_contract');assert m.bank==before;checks+=1
    # International branches and recurring income cannot be bought/claimed twice.
    m=Model(binary);m.choose('branch1_0');assert m.p['BusinessBranches']==1 and m.p['Branch1_0']==1;checks+=1
    before=m.snapshot();m.choose('branch1_0');assert m.snapshot()==before;checks+=1
    before=m.bank;m.choose('business',3);assert m.bank==before+4000;checks+=1
    before=m.bank;m.choose('business',3);assert m.bank==before;checks+=1
    m.ageup();m.choose('business',3);assert m.bank==before+4000;checks+=1
    # Ordinary saved strings/integers round-trip without runtime object pointers.
    saved=m.snapshot();restored=Model(binary,age=m.age,bank=m.bank);restored.props.clear();restored.props.update(saved['props']);assert restored.snapshot()==saved;checks+=1
    report=dict(passed=True,binary_sha256=hashlib.sha256(binary).hexdigest(),assets_sha256=hashlib.sha256((ROOT/'assets.json').read_bytes()).hexdigest(),model_checks=checks,new_scenarios=len(new),cost_age_and_inventory_guards_checked=True,duplicate_income_and_rewards_checked=True,
      crop_bankruptcy_commits_before_dialog_close=True,academy_enrollment_requires_acceptance=True,reserved_native_triggers_executed_in_ARM64=True,scene_expression_parser_banking_and_serialization_modeled=True,device_runtime_tested=False)
    (ROOT/'gameplay35_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

if __name__=='__main__':validate(sys.argv[1])
