"""Execute actual emitted profile, queue, inheritance and effect paths in ARM64.

Managed/Unity calls are explicit hostile ABI doubles. This is not Android/ART.
"""
import csv,hashlib,io,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(SOURCE),str(SOURCE/'native_v29')]
from life_rework.validate_native import Machine as Previous,prior
from test_native import X,Q
from unicorn.arm64_const import UC_ARM64_REG_PC


class Machine(Previous):
    def __init__(self,raw,bias):
        super().__init__(raw,bias)
        off,va,size=self.d['life_followup_rx'];self.map(va+bias,size);self.u.mem_write(va+bias,raw[off:off+size])
        self.q(self.life+0x88,self.hero);self.relationship_impacts=[];self.behaviour=[];self.athlete_impacts=[]
        self.snprintf=0x59c70c0
        self.native_notices=[];self.scenarios=[];self.context_records={};self.other_props={}
        assets=json.loads((prior.ROOT/'assets.json').read_text());self.schemas_all={}
        for name,text in assets.items():
            if text.startswith('key,type,value,'):
                rows={r['key']:r for r in csv.DictReader(io.StringIO(text))}
                self.schemas_all[name]=rows
        self.schema55['life_rework']=self.schemas_all['genesis_rework_defaults']
        self.schema55['life_v18']=self.schemas_all['genesis_v18_defaults_life_v18']
        for owner,sheet in [('life_rework','genesis_rework_defaults'),('life_v18','genesis_v18_defaults_life_v18')]:
            for k,r in self.schemas_all[sheet].items():self.props[owner].setdefault(k,int(r['value'])if r['type']=='int'else r['value'])
        self.ctor_class=self.alloc();self.family_lives={self.life:self.hero};self.classmates=0
        self.prison=self.alloc();self.prison_company=self.alloc();self.q(self.prison+16,self.prison_company);self.w(self.prison_company+16,72);self.prisoners=0
        for va in [0x223e8d4,0x2c48a44,0x2b388b0,0x327d39c,0x327d45c,0x327d938,0x329a720,0x2c32748,0x327dddc,0x2c42394,0x2b6cb40,0x2b6b788,0x2b6b790,0x2b6b540,0x2b3697c,0x35f1608,0x2b367bc,0x2b368e0,0x2bc2fa4,0x2bc2cd4,0x2bc2d7c,0x3dad9a0,0x3911584,0x308480c,0x30838cc,0x2a6a854,0x2c642f4]:self.map(va+bias,4)
    def make_list(self,values):
        arr=self.alloc(32+8*len(values));self.q(arr+24,len(values))
        for i,value in enumerate(values):self.q(arr+32+i*8,value)
        result=self.alloc();self.q(result+16,arr);self.w(result+24,len(values));return result
    def mock(self,u,pc,size,data):
        va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
        if va==self.snprintf and self.cstr(a[2]).startswith('%s: '):
            import re
            match=re.search(r'\.\%0([1-4])d',self.cstr(a[2]));fraction=('.'+str(a[5]).zfill(int(match[1])))if match else''
            value=(self.cstr(a[3])+f': {a[4]}'+fraction+'%\n').encode();assert len(value)<a[1];u.mem_write(a[0],value+b'\0');self.finish_api(lr,len(value));return
        if getattr(self,'divorce_model',False) and va in [0x223e48c,0x223e490,0x223df90,0x223dfc8]:
            if va==0x223dfc8:assert self.cstr(a[2])=='ScenarioLoverDivorce'
            self.finish_api(lr,self.ctor_class);return
        if getattr(self,'divorce_model',False) and va==0x2237158 and a[0]==self.ctor_class:
            self.finish_api(lr,self.alloc(0x300));return
        if va==0x223e8d4:
            self.finish_api(lr,self.managed(bytes(u.mem_read(a[0],a[1]*2)).decode('utf-16-le')));return
        if va==self.snprintf and self.cstr(a[2])=='%lld':
            n=a[3]if a[3]<1<<63 else a[3]-(1<<64);value=str(n).encode();u.mem_write(a[0],value+b'\0');self.finish_api(lr,len(value));return
        if va==0x32800fc and a[0]!=self.life:
            owner=self.str(a[1]);key=(a[0],owner)
            if key not in self.other_props:
                schema=self.schema55[owner];ctx=self.alloc();self.context_records[ctx]=key
                self.other_props[key]=({k:int(r['value'])if r['type']=='int'else r['value']for k,r in schema.items()},ctx)
            self.finish_api(lr,self.other_props[key][1]);return
        if va in [0x3059ee0,0x3059f90,0x3059934,0x3059d08]and a[0]in self.context_records:
            key=self.context_records[a[0]];props=self.other_props[key][0];name=self.str(a[1]);schema=self.schema55[key[1]][name]
            if va==0x3059ee0:value=props[name]
            elif va==0x3059934:value=self.managed(props[name])
            elif va==0x3059f90:
                n=a[2]&0xffffffff;n=n if n<0x80000000 else n-0x100000000;props[name]=max(int(schema['minimum']),min(int(schema['maximum']),n));value=1
            else:props[name]=self.str(a[2]);value=1
            self.finish_api(lr,value);return
        if va==0x2c48a44:assert a[2]==0;self.relationship_impacts.append((a[0],a[1]&0xffffffff));self.finish_api(lr,0);return
        if va==0x2b388b0:self.finish_api(lr,self.classmates);return
        if va==0x327d39c:self.finish_api(lr,self.rq(a[0]+0x88));return
        if va in [0x327d45c,0x327d938,0x329a720]:
            off={0x327d45c:0xe0,0x327d938:0xf0,0x329a720:0x100}[va];self.finish_api(lr,self.rq(a[0]+off));return
        if va==0x2c32748:self.finish_api(lr,self.rw(a[0]+0x224));return
        if va==0x327dddc:self.finish_api(lr,getattr(self,'cheats',0));return
        if va==0x2c42394:
            value=self.rw(a[0]+0xf0);self.finish_api(lr,0);u.reg_write(Q[0],struct.unpack('<I',struct.pack('<f',float(value)))[0]);return
        if va in [0x2a6a854,0x2c642f4]:
            value=self.balance if va==0x2a6a854 else 1000.;self.finish_api(lr,0);u.reg_write(Q[0],int.from_bytes(struct.pack('<d',value),'little'));return
        if va==0x2b6cb40:assert a[0]==self.occ and a[2]==0;self.behaviour.append(a[1]&0xffffffff);self.finish_api(lr,0);return
        if va==0x2b6b788:self.finish_api(lr,self.rw(a[0]+0x3c));return
        if va==0x2b6b790:self.w(a[0]+0x3c,a[1]);self.finish_api(lr,0);return
        if va==0x2b6b540:assert a[0]==self.occ;self.finish_api(lr,self.prison);return
        if va==0x2b3697c:self.finish_api(lr,self.rw(self.rq(a[0]+16)+16)-71);return
        if va==0x35f1608:
            assert 72<=a[0]<=74 and a[1:3]==[0,0];company=self.alloc();self.w(company+16,a[0]);self.finish_api(lr,company);return
        if va==0x2b367bc:assert a[0]==self.prison;self.q(a[0]+16,a[1]);self.finish_api(lr,0);return
        if va==0x2b368e0:self.finish_api(lr,self.prisoners);return
        if va==0x2bc2fa4:self.finish_api(lr,self.rq(a[0]+0x60));return
        if va in [0x2bc2cd4,0x2bc2d7c]:assert a[2]==0;self.athlete_impacts.append((a[0],va,a[1]));self.finish_api(lr,0);return
        if va==0x3dad9a0:self.tables.setdefault(a[0],{})[self.str(a[2])]=self.str(a[1]);self.finish_api(lr,0);return
        if va in [0x308480c,0x30838cc]:self.native_notices.append((va,self.str(a[0])));self.finish_api(lr,0);return
        if va==0x3911584:self.q(a[0]+0x170,a[1]);self.scenarios.append((a[0],a[1]));self.finish_api(lr,0);return
        return super().mock(u,pc,size,data)


def validate(binary,fixture,out):
    prior.ROOT=Path(fixture);raw=Path(binary).read_bytes();checks=[]
    def check(value,label):assert value,label;checks.append(label)
    for bias in [0,0x1000000000]:
        m=Machine(raw,bias);r=m.props['life_rework'];life=m.props['life_v18']
        for name,country in [('Juanita Hardwood','United States'),('Abrisham Popalzai','Afghanistan'),('Samantha Seaman','United Kingdom')]:
            m.people[m.hero]=name;m.country(m.hero,country);m.w(m.hero+0xf8,1);m.w(m.hero+32,0)
            life.update(AdultHeight=178,HeightSource51=2,HeightManual1105=0,HeightRevision1105=0,HeightModel52=52)
            profile=m.alloc(0x200);dictionary,order=m.table(profile)
            m.hook42('v21_native_hero_profile_measurements',{28:profile})
            check(life['AdultHeight']!=178,'actual female profile repairs default: '+country)
            check(m.tables.get(dictionary,{}).get('Projected adult height:')==str(life['AdultHeight'])+' cm','visible table agrees with actual height '+country)
            check('Projected adult height:'in m.display(profile),'height row belongs to the visible native order')
        life.update(AdultHeight=178,HeightSource51=2,HeightManual1105=1,HeightRevision1105=0)
        m.routine42('followup_initialize_actual_profile_height');check(life['AdultHeight']==178,'explicit 178 cm selection preserved')
        m.w(m.hero+32,25);m.props['era44']['BirthYear']=1914-25;m.country(m.hero,'United Kingdom');r['AnnualAge1105']=-1
        m.routine42('life_rework_refresh_context')
        check(r['WarNews1105']==1 and 'World War I'in r['NewsTitle1105'],'1914 queues explicit war headline')
        check(r['DraftEligible1105']==1,'eligible participant receives call-up')
        check(not m.native_notices,'refresh does not parse a filename as CSV or replace live scenario UI')
        before=len(m.native_journal);m.routine42('life_rework_refresh_context');check(len(m.native_journal)==before,'same-age context cannot duplicate annual war journal')
        m.w(m.hero+32,26);m.props['era44']['BirthYear']=1939-26;m.country(m.hero,'Switzerland');m.routine42('life_rework_refresh_context')
        check('World War II'in r['NewsTitle1105']and r['DraftEligible1105']==0,'1939 announcement includes neutral countries without false draft')
        m.w(m.hero+32,27);m.props['era44']['BirthYear']=1944-27;m.country(m.hero,'United States');m.routine42('life_rework_refresh_context')
        check('D-Day'in r['NewsTitle1105'],'1944 Normandy news')
        m.w(m.hero+32,28);m.props['era44']['BirthYear']=1920-28;r['Deployed']=1;m.routine42('life_rework_refresh_context')
        check(r['Deployed']==0 and r['DraftEligible1105']==0,'peacetime ends custom deployment and cannot draft')
        m.w(m.occ+16,4);m.w(m.occ+0x3c,8);m.routine42('followup_perform_typed_game_action',{0:125})
        check(m.rw(m.occ+0x3c)==9 and m.behaviour[-1]==0xfffffffd,'guard setup affects real sentence and behaviour')
        check(m.rw(m.rq(m.prison+16)+16)==73,'serious misconduct transfers into a real higher-security prison company')
        m.w(m.occ+16,0);n=len(m.behaviour);m.routine42('followup_perform_typed_game_action',{0:125});check(len(m.behaviour)==n,'prison command cannot mutate a free character')
        m.balance=500;r.update(MarriageSupport1105=300,MarriageSupportAge1105=-1);m.routine42('followup_perform_typed_game_action',{0:147});check(m.balance==200,'support payment uses actual bank')
        m.routine42('followup_perform_typed_game_action',{0:147});check(m.balance==200,'support cannot double-charge')
        # Execute the real cross-generation transfer helper, keeping the two
        # native Life contexts distinct. This catches lost percentages.
        from life_followup.family import COUNTRIES
        countries={iso:i for i,(iso,label)in enumerate(COUNTRIES)}
        life['AdultHeight']=194
        ancestry={'RUS':1000000}
        for nation,iso in [('France','FRA'),('Japan','JPN'),('Nigeria','NGA')]:
            for code,_ in COUNTRIES:r['Ancestor_'+code]=ancestry.get(code,0)
            r['AncestryReady1105']=1;r['Ancestry1105']='Recorded previous ancestry'
            newlife=m.alloc(0x1000);child=m.alloc(0x400);other=m.alloc(0x400)
            m.q(newlife+0x88,child);m.q(newlife+0xa8,m.hero);m.q(newlife+0xb8,other);m.people[child]='Next generation';m.people[other]='Other parent';m.country(other,nation)
            m.hook42('followup_capture_real_generation_transition',{0:newlife,1:child,2:m.life})
            m.routine42('followup_inherit_actual_parent_country_ancestry')
            target=m.other_props[(newlife,'life_rework')][0]
            check(m.other_props[(newlife,'life_v18')][0]['PlayedFatherHeight1105']==194,'played father keeps chosen height '+nation)
            check(target['FamilyHistory1105'].endswith('\x1e'),'played ancestor is archived '+nation)
            ancestry={key:value//2 for key,value in ancestry.items()};ancestry[iso]=ancestry.get(iso,0)+500000
            check(all(target['Ancestor_'+code]==ancestry.get(code,0)for code,_ in COUNTRIES),'native halves + other parent: '+nation)
            check(sum(target['Ancestor_'+code]for code,_ in COUNTRIES)==1000000,'ancestry totals 100% '+nation)
        check(ancestry==dict(RUS=125000,FRA=125000,JPN=250000,NGA=500000),'four-country inheritance matches the requested example')
        r['FamilyHistory1105']='First ancestor\nRussia: 100%\n\x1eSecond ancestor\nFrance: 50%\n\x1e';r['FamilyArchiveIndex1105']=1
        m.routine42('followup_refresh_selected_ancestor')
        check(r['FamilyArchiveCount1105']==2 and r['FamilyArchiveSelected1105'].startswith('Second ancestor'),'archive reads selected UTF-16 ancestor')
        r['FamilyArchiveIndex1105']=99;m.routine42('followup_refresh_selected_ancestor')
        check(r['FamilyArchiveSelected1105'].startswith('Second ancestor'),'ancestor pagination wraps to a recorded person')
        lover=m.alloc(0x400);m.q(m.life+0xd8,lover);m.w(lover+0x224,3);field=m.alloc();context=m.alloc();m.q(field+24,m.managed('NativeDivorce1105'));m.q(context+16,m.managed('life_rework'))
        r.update(MarriagePhase1105=2,MarriageFiledAge1105=20);m.w(m.hero+32,30);m.divorce_model=True
        result=m.execute42(next(row['stub']for row in m.d['hooks']if row['name']=='followup_original_divorce_scenario_return'),{19:field,21:context})
        check(result!=0 and m.rq(result+0x170)==lover,'finalization returns original divorce scenario with actual spouse')
        print('Native follow-up boundaries passed at',hex(bias),flush=True)
    report=dict(passed=True,checks=len(checks),binary_sha256=hashlib.sha256(raw).hexdigest(),managed_APIs_modeled=True,ART_tested=False,Unity_rendering_tested=False,phone_tested=False)
    Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)


if __name__=='__main__':validate(*sys.argv[1:])
