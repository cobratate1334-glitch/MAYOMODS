"""Regression cases from the v49 device report, including real coroutine phases.

Compiled ARM64 runs under two load biases. Managed collections, allocation,
Unity transforms and Android remain modeled boundaries, stated in the report.
"""
import copy,csv,hashlib,io,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(SOURCE),str(SOURCE/'native_v29')]
from native_v50 import test_native50 as previous
from native_v48.test_native48 import roots
from test_native import X,Q
from unicorn.arm64_const import UC_ARM64_REG_SP
ROOT=Path(__file__).resolve().parent

def namehash(name):
    value=5381
    for ch in name:value=(value*33+ord(ch))&0xffffffff
    return value&0x7fffffff
def parent_height(name):return 155+namehash(name)%55
def projection(father,mother,gender,name):
    mean=((parent_height(father)if father else 178)+(parent_height(mother)if mother else 165)+(13 if gender==0 else -13))//2
    return max(140,min(235,mean+namehash(name)%13-6))

class Machine(previous.Machine):
    def __init__(self,raw,bias):
        previous.ROOT=ROOT;roots(ROOT);super().__init__(raw,bias)
        self.people={};self.canceled=False;self.in_close=False;self.splits=[];self.loads51=[]
        self.dismiss_resume=next(r for r in self.d['hooks']if r['name']=='v41_dismiss_invalidates_pending_presentations')['resume']
        self.real51={0x2f7f0bc,0x2f7c898}
        for a,n in [(0x2f7f0bc,0xac),(0x2f7c898,4),(0x30652e0,0x300),(0x3048dd4,0x6b0),(0x2c42454,8)]:
            self.map(a+bias,n);self.u.mem_write(a+bias,self.load(a,n))
        for a in [0xfad000,0xfa7000]:
            self.map(a+bias,0x1000);self.u.mem_write(a+bias,self.load(a,0x1000))
        self.extra51={self.dismiss_resume,0x2ffbf5c,0x4e02a30,0x4e046e0,0x4f360c4,0x4dfe724,0x4dff5a8,0x3086ef8}
        for a in self.extra51:self.map(a+bias,4)
        # Load the actual getter, rather than modeling the birth-sex field.
        self.apis.discard(0x2c42454)
        self.map(0x60c4000+bias,0x2000)
        self.u.mem_write(0x60c4043+bias,b'\1')
        self.ref51(0x5c7db40,self.managed('BP_'))
        k=self.alloc();self.w(k+0xe4,1);self.ref51(0x5c5ab68,k)
        self.ref51(0x5c7fef8,k)
        self.dismissed=0
    def ref51(self,slot,value):
        p=self.alloc();self.map(slot+self.bias,8);self.q(slot+self.bias,p);self.q(p,value)
    def person(self,name,age=40,gender=0):
        p=self.alloc();self.people[p]=name;self.w(p+0x18,1);self.w(p+0x20,age);self.w(p+0x60,gender)
        # Decode the pinned native getter's actual offset; no guessed struct.
        from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
        ins=next(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(self.load(0x2c42454,4),0x2c42454))
        off=int(ins.op_str.split('#')[1].split(']')[0],0)
        self.w(p+off,gender);return p
    def mock(self,u,pc,size,data):
        va=pc-self.bias;a=[u.reg_read(r)for r in X[:7]];lr=u.reg_read(X[30])
        if va in getattr(self,'real51',set()):return
        if va==0x2c44914 and a[0]in getattr(self,'people',{}):self.finish_api(lr,self.managed(self.people[a[0]]));return
        if va==0x55779e0 and self.in_close:
            assert a[0]in[self.list46,self.rq(self.list46+0x30),self.rq(self.list46+0x38)]
            if a[0]==self.list46:self.canceled=True
            self.finish_api(lr,0);return
        if va not in getattr(self,'extra51',set()):return super().mock(u,pc,size,data)
        value=0
        if va==self.dismiss_resume:
            # The native cleanup body is the boundary. The real injected
            # cancellation hook above has already run in the same stack.
            sp=u.reg_read(UC_ARM64_REG_SP);lr=self.rq(sp)
            u.reg_write(X[21],self.rq(sp+8));u.reg_write(UC_ARM64_REG_SP,sp+0x20)
            self.u.mem_write(self.list46+0x80,b'\0');self.dismissed+=1
        elif va==0x2ffbf5c:value=self.alloc()
        elif va==0x4e02a30:
            assert a[1:4]==[44,0,0]
            columns=self.str(a[0]).split(',');self.splits.append(columns)
            value=self.array51([self.managed(s)for s in columns])
        elif va==0x4e046e0:value=self.managed(self.str(a[0]).strip())
        elif va==0x4f360c4:
            try:self.w(a[1],int(self.str(a[0])));value=1
            except ValueError:pass
        elif va==0x4dfe724:value=int(self.str(a[0]).startswith(self.str(a[1])))
        elif va==0x4dff5a8:value=int(not self.str(a[0]).strip())
        elif va==0x3086ef8:
            self.loads51.append((self.str(a[0]),self.str(a[1]),a[2]));value=self.alloc()
        self.finish_api(lr,value)
    def array51(self,values):
        p=self.alloc(32+len(values)*8);self.q(p+24,len(values))
        for i,v in enumerate(values):self.q(p+32+i*8,v)
        return p
    def registry51(self,line):
        self.execute42(0x30652e0,{20:self.managed(line)},end=0x3065308)
        arr=self.u.reg_read(X[21]);definition=self.alloc()
        self.execute42(0x306531c,{0:arr,21:arr,20:definition,22:self.rq(0x5c7fef8+self.bias)},end=0x3065550)
        return self.str(self.rq(definition+0x68)),self.str(self.rq(definition+0x78))
    def close51(self,negative=None):
        old=next(r for r in self.d['hooks']if r['name']=='v41_dismiss_invalidates_pending_presentations')
        patch=None
        if negative is not None:
            p=old['stub'];patch=bytes(self.u.mem_read(p+self.bias,4))
            self.u.mem_write(p+self.bias,negative[self.fileoff51(p):self.fileoff51(p)+4]);self.u.ctl_remove_cache(p+self.bias,p+self.bias+4)
        epoch=self.d['states']['menu_generation41']['va']+self.bias;self.w(epoch,9)
        obj=self.alloc();self.w(obj+16,0);self.w(obj+20,9);self.q(obj+32,self.list46)
        self.q(self.list46+0x78,self.alloc());self.q(self.list46+0x30,self.alloc());self.q(self.list46+0x38,self.alloc())
        self.u.mem_write(self.list46+0x80,b'\1\0');self.canceled=False
        self.in_close=True
        try:
            first=self.execute42(0x2f7f0bc,{0:obj});second=self.execute42(0x2f7f0bc,{0:obj})
            canceled_before_yield=self.canceled;yielded=self.rq(obj+24)
            third=None
            if not canceled_before_yield:
                # Unity's scheduler/transform animation is modeled here.
                # The parent must stay scheduled until its final phase.
                self.u.mem_write(self.list46+0x81,b'\1');self.in_close=False
                third=self.execute42(0x2f7f0bc,{0:obj})
        finally:
            self.in_close=False
            if patch:self.u.mem_write(old['stub']+self.bias,patch);self.u.ctl_remove_cache(old['stub']+self.bias,old['stub']+self.bias+4)
        return first,second,canceled_before_yield,yielded,third
    def fileoff51(self,va):return next(s['p_offset']+va-s['p_vaddr']for s in self.loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz'])
    def resolve51(self,condition):
        obj=self.alloc();self.q(obj+0x48,self.managed(condition['ScenarioID']));self.q(obj+0x50,self.managed(condition['ScenarioFile']))
        flags=self.alloc();return self.execute42(0x3048dd4,{0:self.controller46,1:obj,2:0,3:0,4:flags,5:flags+1,6:flags+2})
    def hook42(self,name,inputs=None,custom=False):
        if name=='v44_birth_calendar'and not any(r['name']==name for r in self.d['hooks']):
            # v51 now owns this chain entry. Exercise the retained calendar
            # body at its unchanged stub; the v51 birth body has its own test.
            from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
            base=json.loads((SOURCE/'native_v50/native_hooks.json').read_text())
            r=next(r for r in base['hooks']if r['name']==name)
            ins=list(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(self.load(r['stub'],r['length']),r['stub']))
            end=next(i.address-4 for i in ins if i.mnemonic=='b'and int(i.op_str.lstrip('#'),16)==r['resume'])
            return self.execute42(r['stub'],inputs,end=end)
        return super().hook42(name,inputs,custom)

def validate(binary,baseline):
    raw=Path(binary).read_bytes();before=Path(baseline).read_bytes();checks=[]
    def check(ok,label):assert ok,label;checks.append(label)
    d=json.loads((ROOT/'native_hooks.json').read_text());a=json.loads((ROOT/'assets.json').read_text());old=json.loads((SOURCE/'native_v50/assets.json').read_text())
    check(hashlib.sha256(raw).hexdigest()==d['binary_sha256'],'binary binding')
    for bias in [0,0x1000000000]:
        m=Machine(raw,bias)
        bad=next(s for s in old['genesis_feature_containers'].splitlines()if s.startswith('expansions46,'))
        sub,dest=m.registry51(bad);check(sub=='"Community'and dest=='0','old native registry parser reproduces the screenshot')
        for row in a['genesis_feature_containers'].splitlines():
            if row.startswith(('expansions46,','era44,')):
                sub,dest=m.registry51(row);check(dest.startswith('genesis_v18_')and'"'not in sub,'actual registry field extraction '+row.split(',')[0])
        first,second,canceled,yielded,third=m.close51(before)
        check((first,second,canceled)==(1,1,True),'old DismissAllLists cancels the close before yielded lower-panel restore')
        first,second,canceled,yielded,third=m.close51()
        check((first,second,canceled)==(1,1,False)and yielded,'native close reaches its lower-panel yield without canceling itself')
        check(third==0 and bytes(m.u.mem_read(m.list46+0x81,1))==b'\1','close completes and lower panel remains shown')
        check(all(m.active[m.rq(m.hud46+off)+0x400]for off in[0x38,0x40,0x68,0x70]),'completed close restores nav, profile header, toolbar and stats')
        epoch=d['states']['menu_generation41']['va']+bias
        check(m.rw(epoch)==10,'dismiss retains deferred-callback generation invalidation')
        stale=m.alloc();m.w(stale+20,9)
        guard=next(r for r in m.d['hooks']if r['name']=='v41_guard_translation_0')
        check(m.execute42(guard['stub'],{0:stale})==0,'translation callback from the closed screen is rejected')
        # A completed close still reaches the retained, typed HUD repair.
        for off in [0x38,0x40,0x68,0x70]:m.active[m.rq(m.hud46+off)+0x400]=1
        count=len(m.activations);m.routine42('v46_restore_native_hud',{0:m.hud46})
        check(len(m.activations)==count,'settled visible HUD does not replay native activation')
        # Native ResolveScenario must deliver the declared file/controller.
        for key in ['genesis_v18_comments47_00','genesis_v18_comments47_01','genesis_v18_social_v18']:
            for item in json.loads(a[key])['Items']:
                condition=item['ActionList'][0]['ConditionList'][0]
                if condition.get('ScenarioID','').startswith('scenario.'):
                    value=m.resolve51(condition)
                    check(value!=0 and m.loads51[-1]==(condition['ScenarioID'],condition['ScenarioFile'],m.controller46),'actual native scenario action '+item['Title'])
        father=m.person('Michael Morris',45,0);mother=m.person('Elizabeth Morris',42,1)
        m.q(m.life+0xa8,father);m.q(m.life+0xb8,mother)
        m.people[m.hero]='Breanna Morris'
        # Bind the real getter's sex field in the hero too.
        from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
        ins=next(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(m.load(0x2c42454,4),0x2c42454));genderoff=int(ins.op_str.split('#')[1].split(']')[0],0)
        l=m.props['life_v18']
        for gender in [0,1]:
            m.w(m.hero+genderoff,gender);l.update(HeightSource51=0,AdultHeight=178)
            m.routine42('v51_ensure_family_projection')
            expected=projection('Michael Morris','Elizabeth Morris',gender,'Breanna Morris')
            check(l['AdultHeight']==expected and l['HeightSource51']==1,'both parental heights determine stable child projection')
            for age in range(19):
                m.w(m.hero+32,age);m.routine42('measurements_at_current_age21')
                check(l['AdultHeight']==expected and l['Height']<=expected,'Age Up retains projection '+str(age))
            check(l['Height']==expected,'adult reaches inherited target')
        for target in [140,178,198,235]:
            l.update(AdultHeight=target,HeightSource51=2);m.routine42('v51_ensure_family_projection')
            check(l['AdultHeight']==target,'explicit height preserved '+str(target))
        targets=set();m.w(m.hero+genderoff,1)
        for mother_name in ['Elizabeth Morris','Martha Buckley','Parent Example']:
            m.people[mother]=mother_name;l.update(AdultHeight=178,HeightSource51=0)
            m.routine42('v51_ensure_family_projection');targets.add(l['AdultHeight'])
            check(l['AdultHeight']==projection('Michael Morris',mother_name,1,'Breanna Morris'),'changing parent data changes the family estimate')
        check(len(targets)>1,'projection is sensitive to parental height instead of a fixed 178')
        m.people[mother]='Elizabeth Morris'
        for known_father,known_mother in [(False,True),(True,False),(False,False)]:
            m.q(m.life+0xa8,father if known_father else 0);m.q(m.life+0xb8,mother if known_mother else 0)
            l.update(AdultHeight=178,HeightSource51=0);m.routine42('v51_ensure_family_projection')
            check(l['AdultHeight']==projection('Michael Morris'if known_father else None,'Elizabeth Morris'if known_mother else None,1,'Breanna Morris'),'missing-parent baseline is deterministic')
        m.q(m.life+0xa8,father);m.q(m.life+0xb8,mother)
        l.update(AdultHeight=198,HeightSource51=0);m.routine42('v51_ensure_family_projection')
        check(l['AdultHeight']==198 and l['HeightSource51']==2,'old nondefault height preserved')
        m.run('NativeSocialSync',1,'social_v18')
        p=m.props['social_v18'];check(p['C2AdultHeight20']==parent_height('Elizabeth Morris'),'social and native parent heights agree')
        # Exercise a real retained New Life callback, including v33's busy
        # guard that returns to the hooked height store.
        state=m.d['states']['newlife24']['va']+bias
        controller=m.root()
        check(m.captions[m.buttons[0][0]][0]=='Height: Family estimate','existing height control identifies the family default')
        m.click(m.buttons[0][0]);group=m.picker()
        m.routine42('newlife31_choice_0_178',{0:group})
        check(m.rw(state+4)==178 and m.rw(state+28)==1,'validated explicit 178 cm choice records provenance')
        l['AdultHeight']=178;m.hook42('v51_birth_height_provenance')
        check(l['HeightSource51']==2 and l['AdultHeight']==178 and m.rw(state+28)==0,'birth retains selected 178 cm and consumes draft flag')
        # Returning to another field and opening a fresh draft are distinct.
        m.w(state+28,1);m.w(state+56,0);m.hook42('v51_fresh_height_draft')
        check(m.rw(state+28)==0,'fresh draft does not inherit prior manual flag')
        # Same persisted projection survives a reconstructed process fixture.
        saved=copy.deepcopy(m.props);expected=l['AdultHeight'];del m
        m=Machine(raw,bias);m.props=copy.deepcopy(saved);m.people[m.hero]='Breanna Morris';m.routine42('v51_ensure_family_projection')
        check(m.props['life_v18']['AdultHeight']==expected,'save/reload does not reroll height')
    result=dict(passed=True,binary_sha256=hashlib.sha256(raw).hexdigest(),checks=len(checks),cases=checks,
        ASLR_bases=[0,0x1000000000],actual_registry_column_extraction=True,
        actual_native_close_MoveNext_phases=True,actual_native_ResolveScenario=True,
        negative_controls=['quoted registry fields shift destination','dismiss stops its own coroutine'],
        modeled_boundaries=['managed strings/collections and allocation','native cleanup body','Unity transform rendering','JSON deserialization','blueprint atomic chain executor','Android lifecycle'],
        physical_device_tested=False,full_Unity_engine_tested=False)
    (ROOT/'native51_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=len(checks))))

if __name__=='__main__':validate(*sys.argv[1:])
