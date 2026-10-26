"""Execute repaired native boundaries, with strict typed managed API doubles.

These checks exercise ARM64 and include the exact old crash sites. They do not
execute Unity, the complete fighting simulation or Android/ART.
"""
import csv,hashlib,io,json,re,sys
from pathlib import Path
from life_followup.validate_native import Machine as Previous,prior,X


class Machine(Previous):
    def __init__(self,raw,bias):
        super().__init__(raw,bias);off,va,n=self.d['life_repair_rx'];self.map(va+bias,n);self.u.mem_write(va+bias,raw[off:off+n])
        self.schema55['relationship21']=self.schemas_all['genesis_v18_defaults_relationship21']
        for k,r in self.schema55['relationship21'].items():self.props['relationship21'].setdefault(k,int(r['value'])if r['type']=='int'else r['value'])
        self.models={};self.lookups=[];self.class_names={};self.allocated={};self.new_scenarios=[];self.resolve_calls=0;self.strict_gym=0;self.blueprint_model=False
        self.enum_field=self.alloc();self.q(self.hero+0x70,self.alloc(0x1000))
        for va in [0x30611d0,0x33518d8,0x2800d7c,0x308ddb0,0x4e04a8c,0x3833b6c,0x39a09d4,0x223dfe8,0x223e680,0x3209d28,0x3209f1c,0xf0e00000]:self.map(va+bias,4)
        self.u.mem_write(0x33518d8+bias,self.load(0x33518d8,20))
    def mock(self,u,pc,size,data):
        va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
        if va==0x30611d0 and a[0]==self.strict_gym and self.strict_gym:raise TypeError('ArrayList injector received the native typed fighting gym list')
        if va==0xf0e00000:raise IndexError('empty weighted ArrayList indexed at zero')
        if va==0x2800d7c:
            make,name=self.str(a[0]),self.str(a[1]);assert make=='Mayo'and a[2]==0;self.lookups.append(name);self.finish_api(lr,self.models.setdefault(name,self.alloc()));return
        if va==0x308ddb0:
            value=self.str(a[0]);self.resolve_calls+=1
            value=re.sub(r'<GFC\.([^.>]+)\.([^>]+)>',lambda m:str(self.props[m[1]][m[2]]),value)
            self.finish_api(lr,self.managed(value));return
        if va==0x4e04a8c:assert a[2]==0;self.finish_api(lr,int(self.str(a[1])in self.str(a[0])));return
        if self.blueprint_model and va in [0x223e48c,0x223e490,0x223df90]:self.finish_api(lr,self.ctor_class);return
        if self.blueprint_model and va==0x223dfc8:
            name=self.cstr(a[2]);assert name in ['ScenarioCustomAttack','ScenarioMilitaryDeployment','DEATH_TYPE','BluePrintHeroDeath']
            pointer=next((p for p,n in self.class_names.items()if n==name),None)or self.alloc();self.class_names[pointer]=name;self.finish_api(lr,pointer);return
        if self.blueprint_model and va==0x2237158 and a[0]in self.class_names:
            name=self.class_names[a[0]];assert name!='DEATH_TYPE','enum field lookup needs class, not boxed enum object';pointer=self.alloc(0x400);self.allocated[pointer]=name;self.finish_api(lr,pointer);return
        if va==0x223dfe8:assert self.class_names[a[0]]=='DEATH_TYPE'and self.cstr(a[1])=='MILITARY_DEPLOYMENT';self.finish_api(lr,self.enum_field);return
        if va==0x223e680:assert a[0]==self.enum_field;self.w(a[1],17);self.finish_api(lr,0);return
        if va in [0x3833b6c,0x39a09d4]:
            name=self.allocated[a[0]];assert a[2]==0 if va==0x3833b6c else a[1]==0
            if va==0x3833b6c:assert name=='ScenarioCustomAttack'and a[1]in self.people;self.q(a[0]+0x1c8,a[1])
            else:assert name=='ScenarioMilitaryDeployment'
            self.new_scenarios.append((name,a[0]));self.finish_api(lr,0);return
        if va==0x3209d28:assert self.allocated[a[0]]=='BluePrintHeroDeath'and a[1]==0;self.finish_api(lr,0);return
        if va==0x3209f1c:
            assert self.allocated[a[0]]=='BluePrintHeroDeath'and self.rw(a[0]+0x1c)==17
            self.w(self.hero+24,0);death=self.alloc();self.new_scenarios.append(('ScenarioDeathHero',death));self.finish_api(lr,death);return
        return super().mock(u,pc,size,data)
    def bridge(self,key):
        self.blueprint_model=True;field=self.alloc();ctx=self.alloc();self.q(field+24,self.managed(key));self.q(ctx+16,self.managed('life_rework'))
        row=next(r for r in self.d['hooks']if r['name']=='repair_original_school_combat_and_minefield')
        return self.execute42(row['stub'],{19:field,21:ctx})


def validate(binary,base,fixture,out):
    prior.ROOT=Path(fixture);raw=Path(binary).read_bytes();old=Path(base).read_bytes();checks=[]
    def check(v,label):assert v,label;checks.append(label)
    for bias in [0,0x1000000000]:
        m=Machine(raw,bias);r=m.props['life_rework']
        for year,expected in [(1880,'1880 Road carriage'),(1900,'1900 Brass Carriage'),(1940,'1940 Workshop Pickup'),(1980,'1980 Metro Hatch')]:
            m.year45(year);result=m.hook42('repair_empty_period_car_pool',{0:0},custom=True)
            check(m.lookups[-1]==expected and result!=0,'empty pool resolves an actual period model '+str(year))
        # Both old supplied failures use known native sites. Fail the old
        # implementation at the typed API boundary rather than accepting any pointer.
        bad=Machine(old,bias);typed=bad.alloc();bad.strict_gym=typed
        try:bad.execute42(0x33518d8,{20:typed},end=0x33518e0)
        except TypeError:check(True,'negative control: 1105 typed gym injection reproduces invalid receiver')
        else:raise AssertionError('negative control did not reach reported injection')
        typed=m.alloc();m.strict_gym=typed;result=m.execute42(0x33518d8,{20:typed},end=0x33518e0)
        check(result==typed,'repaired gym returns original typed list without Genesis injection')
        r.update(History='The Western Front',Country='France',Front='Somme',NewsBody1105='<GFC.life_rework.History> in <GFC.life_rework.Country>; <GFC.life_rework.Front>.')
        result=m.hook42('repair_nested_saved_text_before_display',{0:m.managed('<GFC.life_rework.NewsBody1105>')})
        check(m.str(result)=='The Western Front in France; Somme.'and m.resolve_calls==2,'nested saved GFC text is materialized in bounded pure passes')
        parent=m.alloc(0x400);m.people[parent]='Michael Roberts';m.w(parent+32,61);m.props['relationship21']['Age']=33;m.props['relationship21']['Name']='Other person'
        m.routine42('selected_relationship_details21',{0:parent,1:0})
        check(m.props['relationship21']['Age']==61 and m.props['relationship21']['Name']=='Michael Roberts','story finalizes actual selected person age and name after derived work')
        check(m.props['relationship21']['SelectedAge1106']==61 and m.props['relationship21']['SelectedName1106']=='Michael Roberts','story-specific fields agree with the live selected person')
        for year,flag,want in [(1914,'🇩🇪','de_imperial'),(1939,'🇩🇪','de_nazi'),(1944,'🇺🇸','us48'),(1940,'🇮🇹','it_royal')]:
            m.year45(year);result=m.hook42('repair_header_flags_follow_calendar',{1:m.managed(flag)},custom=True)
            check(m.str(result)=='scene1106-flag-'+want,'historical header flag '+flag+' '+str(year))
        for key,path in [('scene1106-art','emoji/normal/scene1106-art'),('scene1106-flag-de_nazi','mayomods1106/inlineflags/de_nazi'),('mayomods1106/flags/jp_naval','mayomods1106/flags/jp_naval')]:
            row=next(r for r in m.d['hooks']if r['name']=='repair_typed_activity_and_historical_art')
            result=m.execute42(row['stub'],{0:m.managed(key)})
            check(result==m.texture55 and m.resources55[-1]==path,'registered artwork uses typed Resources.Load<Sprite>: '+key)
        m.w(m.hero+32,33);m.props['life_v18'].update(AdultHeight=185,HeightManual1105=1,HeightRevision1105=1105);profile=m.alloc(0x400);dictionary,order=m.table(profile);m.hook42('repair_compact_native_profile',{28:profile})
        keys=m.display(profile);check('MayoMods build:'not in keys and 'Projected adult height:'not in keys,'adult profile omits build branding and duplicate height')
        check(m.tables[dictionary]['Height:']=='185 cm','compact profile still uses actual measurements')
        m.w(m.hero+32,14);m.w(m.occ+16,1);school=m.alloc();m.q(m.occ+0x20,school);peer=m.alloc(0x400);m.people[peer]='Current classmate';m.classmates=m.make_list([peer]);r['SchoolCombatAge1106']=-1
        result=m.bridge('SchoolNativeFight1106');check(result and m.rq(result+0x1c8)==peer,'school choice returns original punch/kick attack scenario and actual classmate')
        check(r['SchoolCombatAge1106']==14 and r['SchoolBullyStage']==3,'native fight commitment records one encounter and follow-up')
        m.hook42('repair_record_actual_school_fight_popularity');check(r['SchoolCombatDoneAge1106']==14 and r['SchoolReputation1106']==45,'actual stock popularity call records completed fight')
        m.w(m.occ+16,3);m.w(m.hero+32,25);r.update(War=2,WarSide=1,WarNativeMissionAge1106=-1)
        result=m.bridge('NativeMinefield1106');check(result and m.new_scenarios[-1][0]=='ScenarioMilitaryDeployment','real military deployment opens original minefield flow')
        result=m.bridge('WarFatal1106');check(result and m.new_scenarios[-1][0]=='ScenarioDeathHero'and m.rw(m.hero+24)==0,'fatal battle returns native death screen with runtime-resolved military enum')
        # Era/country controls, resource income and one-year puzzle stability.
        m.w(m.hero+24,1);m.w(m.hero+32,25);m.props['era44']['BirthYear']=1914;m.country(m.hero,'Germany');r.update(AnnualAge1105=-1,MissionBriefAge1106=-1,CommandActive1106=1,CommandBuildAge1106=-1)
        m.routine42('life_rework_refresh_context');check(r['WarGovernment1106']=='Nazi Germany'and r['WarFlag1106'].endswith('de_nazi'),'Germany 1939 gets historical government and flag')
        check(r['CommandPermit01106']==1 and r['CommandPermit31106']==0,'German command cannot order Japan’s Pacific campaign')
        puzzles=[r[k]for k in ['TrenchSafe11106','TrenchSafe21106','TrenchSafe31106']];budget=r['CommandBudget1106'];m.routine42('life_rework_refresh_context');check(r['CommandBudget1106']==budget and [r[k]for k in ['TrenchSafe11106','TrenchSafe21106','TrenchSafe31106']]==puzzles,'same-age menu reopen cannot farm production or reroll mission clues')
        event=m.alloc();m.q(event+24,m.managed('An airliner was hijacked.'));m.year45(1901);row=next(r for r in m.d['hooks']if r['name']=='repair_period_technology_in_world_news');result=m.execute42(row['stub'],{0:event,1:0})
        check('airliner'not in m.str(result).lower(),'1901 stock news replaces impossible airliner story with period news')
        print('Repaired native boundaries passed at',hex(bias),flush=True)
    report=dict(passed=True,checks=len(checks),binary_sha256=hashlib.sha256(raw).hexdigest(),supplied_base_sha256=hashlib.sha256(old).hexdigest(),negative_control_typed_fight_list=True,managed_APIs_modeled=True,phone_tested=False,ART_tested=False,Unity_rendering_tested=False)
    Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
