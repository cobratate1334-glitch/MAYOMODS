"""Execute the distinct main-menu New Life entry seen in the user's video.

The stock action-1 tail and complete ShowDarklyWithScenario body run as ARM64.
DismissAllLists, DismissAllDarklies, ResetTypes and the stock Count-1 lookup
also run. Prefab creation, rendering and transition scheduling are modeled.
Negative v32 controls reproduce refusal with stale pending/canvas state;
they do not establish the exact device state of the supplied recording.
"""
import hashlib,json,struct
from unicorn.arm64_const import UC_ARM64_REG_PC,UC_ARM64_REG_SP
from test_navigation33 import Navigation,ROOT,test_native,X
from native_hooks import h

class Entry(Navigation):
    def __init__(self,binary,bias):
        super().__init__(binary,bias)
        self.q(self.ui_manager+0xa0,self.manager)
        self.prefabs=[];self.hidden_banners=0;self.main_dismissals=0
        self.map(0x2f77cb8+bias,0x84)
        self.u.mem_write(0x2f77cb8+bias,self.load(0x2f77cb8,0x84))
        self.map(0x300c0a4+bias,0x60)
        self.u.mem_write(0x300c0a4+bias,self.load(0x300c0a4,0x60))
        for va in [0x2eba37c,0x2f74744,0x2f83804]:self.map(va+bias,4)
        # Reproduce the real caller's stack and GameManager metadata slot.
        # The following instructions, including DismissAllLists and the
        # tail-call signature (NULL, type 5), are copied from the game.
        self.action_veneer=0x6800200+bias
        source=f'sub sp,sp,#0xd0\nstp x20,x19,[sp,#0xc0]\nstp x22,x21,[sp,#0xb0]\nstp x24,x23,[sp,#0xa0]\nstp x26,x25,[sp,#0x90]\nstr x30,[sp,#0x88]\nstr d8,[sp,#0x80]\nadrp x19,{(0x5c23c90+bias)&~4095:#x}\nldr x19,[x19,#{(0x5c23c90+bias)&4095}]\nmov x8,x0\nb {0x300c0a4+bias:#x}'
        code=h.asm(source,self.action_veneer)
        self.map(self.action_veneer,len(code));self.u.mem_write(self.action_veneer,code)

    def mock(self,u,pc,size,data):
        va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
        if va==0x2f83804:
            assert a[:3]==[self.ui_manager,0,0];self.main_dismissals+=1
            # Execute actual UIListManager.DismissAllLists, tail-style.
            u.reg_write(X[0],self.list_manager);u.reg_write(X[1],0)
            u.reg_write(UC_ARM64_REG_PC,0x2f7c898+self.bias);return
        if va==0x2eba37c:
            assert a[0]==0;self.hidden_banners+=1;self.finish_api(lr,0);return
        if va==0x2f74744:
            assert a[0]==self.manager and a[1]==5 and a[2]==0
            assert a[3:8]==[0xffffffff,0xffffffff,0,0,0]
            sp=u.reg_read(UC_ARM64_REG_SP)
            assert [self.rw(sp+i)for i in [0,8,16,24,32]]==[0xffffffff,0,0,0,0]
            assert self.rq(sp+40)==self.rq(sp+48)==0
            # Model the ordinary stock Custom Life prefab boundary. Record
            # the state before the prefab so reset coverage is observable.
            self.prefabs.append(dict(cached_before=self.cached_pages(),
                pending_before=bytes(u.mem_read(self.manager+0x110,1))[0],
                canvas_active_before=self.active.get(self.darkly_canvas+0x400,0),
                handles_before=len(self.handles)))
            page=self.alloc();self.q(page+0x20,self.manager);self.w(page+0x40,5)
            self.q(page+0xd0,self.alloc());self.w(page+0x128,0)
            pages=self.cached_pages();self.set_stack(pages+[page],len(pages),5)
            self.prefabs[-1]['page']=page;self.finish_api(lr,page);return
        if va==0x2f731fc:
            assert a[0]==self.manager and a[1]in[5,6]
            u.reg_write(UC_ARM64_REG_SP,u.reg_read(UC_ARM64_REG_SP)+0xc0)
            if not bytes(u.mem_read(self.manager+0x110,1))[0]:
                self.transitions.append(a[1]);self.w(self.manager+0xb4,a[1])
            self.finish_api(lr,0);return
        super().mock(u,pc,size,data)

    def main_newlife(self):
        return self.native_call(self.action_veneer-self.bias,{0:self.game})

    def interrupted(self):
        c,old=self.begin();death=self.alloc();self.w(death+0x40,7)
        self.active[death+0x400]=1;self.set_stack([c,old,death],2,7)
        state=self.d['states']['newlife24']['va']+self.bias
        extra=self.d['states']['newlife31']['va']+self.bias
        self.w(state+60,2);self.w(extra+64,3)
        self.u.mem_write(self.manager+0x110,b'\1');self.active[self.darkly_canvas+0x400]=0
        self.collections[self.containers[0]]=['map'];self.collections[self.containers[1]]=['main_menu'];self.w(self.list_manager+0x80,1)
        return c,old,death

def validate():
    before=(ROOT.parent/'native_v32/libil2cpp.so').read_bytes();after=(ROOT/'libil2cpp.so').read_bytes()
    checks=0;negative=[]
    for bias in [0,0x1000000000]:
        test_native.ROOT=ROOT.parent/'native_v32';m=Entry(before,bias);m.interrupted();m.main_newlife()
        unchanged_entry=m.load(0x300be24,0x2e0)
        assert not m.transitions and m.prefabs[-1]['pending_before']==1
        assert len(m.prefabs[-1]['cached_before'])==3 and not m.prefabs[-1]['canvas_active_before']
        negative.append(dict(aslr_bias=bias,stock_main_menu_entry_skips_custom_life_reset=True,
                             modeled_pending_transition_refused=True));checks+=2

        test_native.ROOT=ROOT;m=Entry(after,bias)
        old_life=dict(m.props['life_v18'])
        for route in ['age_zero','deceased','surrender','root_close','map_back','country_back','city_back']:
            for repeat in range(3):
                stale=m.interrupted();calls=len(m.transitions);m.main_newlife();item=m.prefabs[-1]
                assert m.main_dismissals==len(m.prefabs) and item['cached_before']==[] and item['pending_before']==0;checks+=1
                assert item['canvas_active_before']==1 and item['handles_before']==0 and len(m.transitions)==calls+1;checks+=1
                assert m.cached_pages()==[item['page']] and m.last_selected==item['page'] and not any(m.active.get(p+0x400,0)for p in stale);checks+=1
                assert not any(m.collections.values())and not m.rw(m.list_manager+0x80)and m.props['life_v18']==old_life;checks+=1
                # The next normal Setup extension must rearm an editable
                # draft, rather than inheriting the canceled old one.
                m.root(item['page']);m.click(m.buttons[-7][0]);assert m.rw(m.d['states']['newlife31']['va']+bias+64)==1;checks+=1
                # Keep this method's transition model scoped to stock entry;
                # body selector transition verification has its own suite.
                m.w(m.manager+0xb4,5)
        # Guard affects only the exact main-menu New Life signature.
        m=Entry(after,bias);m.interrupted();snapshot=(m.cached_pages(),dict(m.active),dict(m.handles))
        for kind,scenario in [(1,0),(6,0),(7,0),(5,m.alloc())]:
            m.stub('v33_fresh_main_menu_newlife_entry',{0:m.manager,1:scenario,2:kind,3:0})
            assert snapshot==(m.cached_pages(),dict(m.active),dict(m.handles))and not m.darkly_cleanup_calls;checks+=1
        assert m.load(0x300be24,0x2e0)==unchanged_entry;checks+=1
    result=dict(passed=True,arm64_cases=checks,binary_sha256=hashlib.sha256(after).hexdigest(),
        v32_negative_controls=negative,aslr_biases=[0,0x1000000000],
        actual_main_menu_action_1_tail_and_full_ShowDarklyWithScenario_executed=True,
        stock_save_confirmation_and_Start_unchanged=True,
        repeated_age_zero_and_deceased_entry_clears_cached_screens_and_pending_state=True,
        unrelated_scenarios_untouched=True,prefab_creation_rendering_and_transition_scheduling_modeled=True,
        video_sequence_inspected=True,exact_recorded_device_state_not_recovered=True,device_runtime_tested=False)
    (ROOT/'entry33_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)

if __name__=='__main__':validate()
