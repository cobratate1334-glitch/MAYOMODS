"""Execute the new native controls, Actions and engine transitions with ASLR.

Unity drawing, prefab instantiation, list cleanup and transition timing remain
modeled boundaries. This is an instruction regression, not a device run.
"""
import hashlib, json, os, shutil, struct, sys
from pathlib import Path
from unicorn.arm64_const import UC_ARM64_REG_SP, UC_ARM64_REG_PC
ROOT=Path(__file__).resolve().parent
V29=ROOT.parent/'native_v29'
sys.path.insert(0,str(V29))
import test_native
from test_engine24 import Engine24
from test_native import X
from patch_native31 import LABELS, OPTIONS

# The retained game assets are only a fixture for saved property defaults.
test_native.ROOT=ROOT
if not (ROOT/'assets.json').exists():shutil.copyfile(V29/'assets.json',ROOT/'assets.json')

class NewLife31(Engine24):
    def __init__(self,binary,bias):
        super().__init__(binary,bias)
        self.owned={};self.parents={};self.captions={};self.live_options=[];self.transitions=[];self.cleaned=[]
        self.fitter_drivers={self.fitter:self.drivers};self.scroll=self.alloc();self.q(self.scroll+0x28,self.alloc())
        self.newapi={0x2fa97ac,0x3024244,0x49901a4}
        for va in self.newapi:self.map(va+bias,4)
        for hook in self.d['hooks']:
            if hook.get('custom_resume'):self.map(hook['custom_resume']+bias,4)
        # The exact generic MethodInfo route used by the shipped subgroup.
        slot=self.alloc();klass=self.alloc();generic=self.alloc();table=self.alloc();info=self.alloc()
        self.map(0x5c6d1a8+bias,8);self.q(0x5c6d1a8+bias,slot);self.q(slot,klass);self.q(klass+0x20,generic);self.q(generic+0xc0,table);self.q(table+0x70,info);self.list_info=info
        self.w(self.manager+0xb4,5)
        # Execute the new transition hook, with the stock transition body a
        # modeled boundary. The root Setup extension is also real ARM64.
        self.map(0x2f731f8+bias,8);self.u.mem_write(0x2f731f8+bias,self.load(0x2f731f8,4))
        for va in [0x2fa6cb4,0x2fa7168,0x2fa7b74]:self.map(va+bias,12)
        self.u.mem_write(0x2fa6cb4+bias,self.load(0x2fa6cb4,12))
        from native_hooks import h
        hook=next(x for x in self.d['hooks']if x['name']=='v21_new_life_native_buttons')
        self.refresh_veneer=0x6800000+bias
        code=h.asm(f'stp x19,x30,[sp,#-16]!\nmov x19,x0\nbl {hook["stub"]+bias:#x}\nldp x19,x30,[sp],#16\nret',self.refresh_veneer)
        self.map(self.refresh_veneer,len(code));self.u.mem_write(self.refresh_veneer,code)

    def mock(self,u,pc,size,data):
        va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
        if va==0x2f72230:
            assert a[0]==self.manager and a[3]in[0,1]
            title=self.str(a[5]);subtitle=self.str(int.from_bytes(u.mem_read(u.reg_read(UC_ARM64_REG_SP),8),'little'))
            button=a[1]
            if not button:
                button=self.alloc();self.q(button+0x28,button+0x300);self.active[button+0x400]=0
                if a[3]==1:self.buttons.append((button,title))
                else:self.live_options.append(button)
            self.captions[button]=(title,subtitle,a[4],a[3]);self.finish_api(lr,button);return
        if va==0x5584430:
            assert 8<=a[1]<=14 and a[2]==0;self.actions.append(('index',a[:3]));self.finish_api(lr,0);return
        if va==0x2f731f8:return
        if va==0x2fa7168:
            u.reg_write(UC_ARM64_REG_PC,self.refresh_veneer);return
        if va==0x2fa7b74:
            self.finish_api(lr,0);return
        if va==0x2f731fc:
            assert a[0]==self.manager and a[1]in[5,6]and a[2]==0
            u.reg_write(UC_ARM64_REG_SP,u.reg_read(UC_ARM64_REG_SP)+0xc0)
            self.transitions.append(a[1]);self.w(self.manager+0xb4,a[1]);self.finish_api(lr,0);return
        if va==0x2fa97ac:
            group=a[0]
            old=self.rq(group+0xe0)
            for go in self.owned.get(old,[]):self.cleaned.append(go);self.active[go]=0
            owner=self.alloc();self.owned[owner]=[];self.q(group+0xe0,owner)
            fitter=self.rq(group+0x90);self.fitter_drivers[fitter]=[];self.q(fitter+0x28,0)
            self.live_options=[];self.finish_api(lr,0);return
        if va==0x49901a4:
            assert a[0]in self.owned and a[2]==self.list_info
            self.owned[a[0]].append(a[1]);self.w(a[0]+0x18,len(self.owned[a[0]]));self.finish_api(lr,0);return
        if va==0x3024244:
            self.captions[a[0]]=self.str(a[1]);assert a[2]==0;self.finish_api(lr,0);return
        if va==0x2f5bc48:
            assert a[0]in self.fitter_drivers and a[2]==0
            drivers=self.fitter_drivers[a[0]];assert a[1]not in drivers;drivers.append(a[1]);array=self.alloc(0x20+len(drivers)*8);self.q(array+0x18,len(drivers))
            for i,driver in enumerate(drivers):self.q(array+0x20+i*8,driver)
            self.q(a[0]+0x28,array);self.finish_api(lr,0);return
        super().mock(u,pc,size,data)

    def root(self,controller=None):
        if controller is None:
            controller=self.alloc();self.q(controller+0x20,self.manager);self.q(controller+0xd0,self.alloc());self.w(controller+0x128,0)
        self.w(self.manager+0xb4,5);self.stub('v21_new_life_native_buttons',{19:controller});return controller

    def picker(self,group=None):
        if group is None:
            group=self.alloc();self.q(group+0x20,self.manager)
            for off in[0x38,0x68,0x70,0x90]:self.q(group+off,self.alloc())
            self.q(group+0xa0,self.scroll)
            self.fitter_drivers[self.rq(group+0x90)]=[]
        hook=next(x for x in self.d['hooks']if x['name']=='v31_native_rounded_selector_setup')
        self.hook(hook['name'],{19:group},end=hook['custom_resume']);return group

    def click(self,button):self.native_call(0x4ec656c,{0:self.rq(button+0xa0)})

    def birth(self):
        previous=next(x for x in json.loads((V29/'native_hooks.json').read_text())['hooks']if x['name']=='v21_apply_body_after_hero_generation')
        self.hook('v31_birth_release_selector_roots',{19:self.game},end=previous['stub']+previous['length']-8)

def validate(path):
    binary=Path(path).read_bytes();checks=0
    opts=json.loads((ROOT/'selector31_options.json').read_text())
    for bias in[0,0x1000000000]:
        m=NewLife31(binary,bias);state=m.d['states']['newlife24']['va']+bias;extra=m.d['states']['newlife31']['va']+bias
        life=dict(m.props['life_v18']);c=m.root()
        assert len(m.buttons)==7 and len(m.handles)==8 and m.props['life_v18']==life;checks+=1
        assert [m.captions[b][1]for b,_ in m.buttons]==LABELS+['Regions'];checks+=1
        assert [m.captions[b][0]for b,_ in m.buttons][:3]==['178 cm','72 kg','180 cm'];checks+=1
        assert len(m.drivers)==7 and all(m.active[b+0x400]==1 for b,_ in m.buttons);checks+=1
        m.root(c);assert len(m.buttons)==7 and len(m.handles)==8 and len(m.drivers)==7;checks+=1
        group=None
        for repeat in range(3):
            for n,row in enumerate(opts['options']):
                m.click(m.buttons[n][0]);assert m.transitions[-1]==6 and m.rw(extra+64)==n+1;checks+=1
                before=len(m.transitions);m.click(m.buttons[(n+1)%6][0]);assert len(m.transitions)==before;checks+=1
                group=m.picker(group);assert len(m.live_options)==len(row);checks+=1
                assert m.captions[m.rq(group+0x38)]==LABELS[n];checks+=1
                assert len(m.owned[m.rq(group+0xe0)])==len(row)and len(m.fitter_drivers[m.rq(group+0x90)])==len(row);checks+=1
                assert all(len(m.captions[b][0])<=22 and m.captions[b][1]=='' and m.captions[b][3]==0 for b in m.live_options);checks+=1
                # Selected value is green; alternatives use the stock yellow.
                selected=m.rw(state+[4,8,12,16,20,24][n]);selected=selected if selected<0x80000000 else selected-0x100000000
                assert [m.captions[b][2]for b in m.live_options]==[int(v!=selected)for v,_,_ in row];checks+=1
                pick=[len(row)-1,0,len(row)//2][repeat];value=row[pick][0]
                stale=m.rq(m.live_options[pick]+0xa0)
                m.click(m.live_options[pick]);assert m.rw(state+[4,8,12,16,20,24][n])==(value&0xffffffff)and m.transitions[-1]==5 and m.rw(extra+64)==0;checks+=1
                assert m.props['life_v18']==life;checks+=1
                m.root(c);assert len(m.handles)==8 and len(m.buttons)==7;checks+=1
                before=dict(m.props['newlife24']);m.native_call(0x4ec656c,{0:stale});assert m.props['newlife24']==before;checks+=1
        # Execute every fixed choice callback, including all numeric endpoints.
        for n,row in enumerate(opts['options']):
            m.click(m.buttons[n][0]);group=m.picker(group)
            action_handles=[m.rq(b+0xa0)for b in m.live_options]
            for (value,_,_),a in zip(row,action_handles):
                m.w(extra+64,n+1);m.w(m.manager+0xb4,6)
                if not m.rq(extra+72):
                    handle=m.next_handle;m.next_handle+=8;m.handles[handle]=group;m.q(extra+72,handle)
                m.native_call(0x4ec656c,{0:a})
                assert m.rw(state+[4,8,12,16,20,24][n])==(value&0xffffffff);checks+=1
            m.root(c)
        # Back returns through the stock type-5 path; stale routing is reset.
        for _ in range(10):
            m.click(m.buttons[0][0]);group=m.picker(group)
            m.native_call(0x2f731f8,{0:m.manager,1:5,2:0})
            assert m.rw(extra+64)==0 and m.rw(state+60)==0 and m.rw(state+56)==1 and len(m.handles)==8,(m.rw(extra+64),m.rw(state+60),m.rw(state+56),len(m.handles));checks+=1
        # Root X cancels the genotype; reopening the SAME controller works.
        m.stub('v31_cancel_newlife_draft',{0:m.manager});assert m.rw(state)==0 and m.rw(state+56)==0 and m.rw(extra+64)==0;checks+=1
        m.root(c);assert m.rw(state)==1;m.click(m.buttons[0][0]);assert m.transitions[-1]==6;checks+=1
        m.root(c)
        # Dismiss destroys every retained root. Fresh page gets defaults, even
        # if the managed controller object is reused by the stock engine.
        m.stub('v23_dismiss_android_setup_panel',{0:m.manager});assert not m.handles and not m.rw(state+56)and not m.rw(extra+64);checks+=1
        m.root(c);assert m.rw(state+4)==178 and len(m.handles)==8;checks+=1
        # Birth still consumes exact adult genes once and starts at baby size.
        p=m.props['newlife24'];p.update(AdultHeight=198,AdultWeight=95,Reach=12,InheritedTrait21=1,Personality=2,RareAppearance21=3)
        m.run('NativeStage24',1,'newlife24');m.w(m.hero+0x20,0);m.birth();l=m.props['life_v18']
        assert(l['AdultHeight'],l['AdultWeight'],l['Reach'],l['Height'],l['Weight'],l['Wingspan'])==(198,95,12,50,3,53);checks+=1
        assert l['TraitName']=='Genius'and struct.unpack('<f',m.u.mem_read(m.hero+0x90,4))[0]==95 and not m.handles;checks+=1
        before=dict(l);m.birth();assert l==before;checks+=1
        for age in range(19):m.w(m.hero+0x20,age);m.run('NativeLifeSync',1,'life_v18');assert l['Height']<=198;checks+=1
        assert(l['Height'],l['Weight'],l['Wingspan'])==(198,95,210);checks+=1
        assert m.cleaned and not any(h['site']in[0x2fa8524,0x2fa8790]for h in m.d['hooks']);checks+=1
    report=dict(binary_sha256=hashlib.sha256(binary).hexdigest(),arm64_cases=checks,aslr_biases=[0,0x1000000000],actual_Action_Invoke_executed=True,actual_return_hook_and_RefreshSetup_executed=True,all_293_choices_executed=True,six_fields_directly_in_New_Life=True,stock_rounded_selector_prefab_and_scroller=True,short_labels=True,rapid_repeat_edits_and_stale_Actions_checked=True,same_controller_close_reopen_checked=True,all_UI_GC_roots_released_on_dismiss_and_birth=True,existing_genetic_engine_and_baby_growth_preserved=True,stock_Start_methods_unhooked=True,Unity_prefabs_collections_and_transition_timing_modeled=True,device_runtime_tested=False,BlueStacks_runtime_tested=False)
    (ROOT/'native31_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

if __name__=='__main__':validate(sys.argv[1]);os._exit(0)
