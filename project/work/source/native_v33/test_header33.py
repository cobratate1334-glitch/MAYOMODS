"""Run the real UIManager.RefreshUI with modeled Unity/widget boundaries.

The v32 negative control leaves a hidden navigation GameObject hidden. The v33
entry hook repairs that state only after the dialog and other UI owners close.
This does not reproduce a complete therapist visit or render Unity on a phone.
"""
import hashlib,json,os
from unicorn.arm64_const import UC_ARM64_REG_PC
from test_navigation33 import Navigation,ROOT,test_native,X

class Header(Navigation):
    UI_API={0x5575728,0x2f7e424,0x2f62bfc,0x3017ccc,0x2fedafc,
            0x2ff350c,0x30210ac,0x2f6e1b4,0x2f70c10,0x301f368,
            0x2f62f68,0x3021840,0x2f83b18,0x2f81d60,0x2f81c8c}
    def __init__(self,binary,bias):
        super().__init__(binary,bias)
        self.scenario=self.alloc();self.nav=self.alloc();self.menu_open=False
        self.accessibility=False;self.null_go=False;self.nav_writes=[];self.focus=[];self.widgets=[]
        self.q(self.ui_manager+0xa0,self.manager);self.q(self.ui_manager+0x80,self.scenario)
        self.q(self.ui_manager+0x38,self.nav);self.active[self.nav+0x400]=0
        self.set_stack([],kind=0)
        for off in [0x40,0x50,0x68,0xd0,0x70,0xb8,0xd8]:self.q(self.ui_manager+off,self.alloc())
        for va in self.UI_API:self.map(va+bias,4)
        self.map(0x2f83be8+bias,468);self.u.mem_write(0x2f83be8+bias,self.load(0x2f83be8,468))
        self.map(0x60c3b57+bias,1);self.u.mem_write(0x60c3b57+bias,b'\1')
        for va in [0x5c6b780,0x5c24508,0x5c23c90]:
            self.meta(va);slot=self.rq(va+bias);klass=self.rq(slot);static=self.alloc();self.q(klass+0xb8,static)
            self.q(static,self.game if va==0x5c23c90 else self.rq(self.ui_manager+0xd0))
        self.refresh_inputs={0:self.ui_manager,1:4,2:self.alloc(),3:self.alloc(),4:self.alloc(),5:self.alloc(),6:self.alloc()}
    def mock(self,u,pc,size,data):
        va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
        if va==0x5575664 and a[0]==self.nav+0x400:
            assert a[1]==1 and a[2]==0;self.nav_writes.append(a[1])
        if va==0x55725ac and a[0]==self.nav and self.null_go:
            self.finish_api(lr,0);return
        if va in [0x2f838cc,0x2e87cec]:
            assert a[1]==0
            if va==0x2f838cc:assert a[0]==self.ui_manager
            else:assert a[0]==0
            self.finish_api(lr,int(self.menu_open if va==0x2f838cc else self.accessibility));return
        if va in self.UI_API:
            result=0
            if va==0x5575728:
                assert a[:2]==[self.nav+0x400,0];result=self.active[a[0]]
            elif va==0x2f7e424:
                assert a[:3]==[self.ui_manager,1,0];self.focus.append(a[:3])
            else:
                self.widgets.append(va)
                if va==0x3017ccc:assert a[:2]==[self.nav,0]
                elif va==0x2fedafc:
                    assert a[0]==self.rq(self.ui_manager+0x40)
                    assert a[1:6]==[self.refresh_inputs[i]for i in range(2,7)]and a[6]==0
                elif va==0x30210ac:assert a[:3]==[self.rq(self.ui_manager+0x68),4,0]
                elif va==0x2f81c8c:assert a[0]==self.rq(self.ui_manager+0xd8)
            self.finish_api(lr,result);return
        super().mock(u,pc,size,data)
    def refresh(self):
        self.native_call(0x2f83be8,self.refresh_inputs)
        assert 0x3017ccc in self.widgets and 0x2fedafc in self.widgets and 0x2f81c8c in self.widgets

def validate():
    before=(ROOT.parent/'native_v32/libil2cpp.so').read_bytes();after=(ROOT/'libil2cpp.so').read_bytes()
    checks=0;negative=[]
    for bias in [0,0x1000000000]:
        test_native.ROOT=ROOT.parent/'native_v32';m=Header(before,bias);m.refresh()
        assert not m.active[m.nav+0x400]and not m.nav_writes;checks+=1
        negative.append(dict(aslr_bias=bias,actual_stock_RefreshUI_executed=True,hidden_nav_remained_hidden=True))
        test_native.ROOT=ROOT;m=Header(after,bias)
        m.refresh();assert m.active[m.nav+0x400]and m.nav_writes==[1]and not m.focus;checks+=1
        for _ in range(20):m.refresh();assert m.nav_writes==[1]and m.active[m.nav+0x400];checks+=1
        # Closing a scenario, cached Darkly, or menu is a shared recovery path;
        # refreshing while that owner still exists never reveals the bar.
        for owner in ['dialog','darkly','menu','translation']:
            m.active[m.nav+0x400]=0;n=len(m.nav_writes)
            if owner=='dialog':m.q(m.scenario+0x1c8,m.alloc())
            elif owner=='darkly':m.set_stack([m.alloc()],kind=6)
            elif owner=='menu':m.menu_open=True
            else:m.u.mem_write(m.manager+0x110,b'\1')
            m.refresh();assert not m.active[m.nav+0x400]and len(m.nav_writes)==n;checks+=1
            if owner=='dialog':m.q(m.scenario+0x1c8,0)
            elif owner=='darkly':m.set_stack([],kind=0)
            elif owner=='menu':m.menu_open=False
            else:m.u.mem_write(m.manager+0x110,b'\0')
            m.refresh();assert m.active[m.nav+0x400]and len(m.nav_writes)==n+1;checks+=1
        m.accessibility=True;m.active[m.nav+0x400]=0;m.refresh()
        assert m.focus==[[m.ui_manager,1,0]];checks+=1
        for _ in range(5):m.refresh();assert len(m.focus)==1;checks+=1
        # Guard-only null/destroyed inputs retain the original caller ABI.
        for field in [0xa0,0x80,0x38]:
            old=m.rq(m.ui_manager+field);m.q(m.ui_manager+field,0);n=len(m.nav_writes)
            m.stub('v33_recover_hidden_top_menu_after_dialog',m.refresh_inputs)
            assert len(m.nav_writes)==n;m.q(m.ui_manager+field,old);checks+=1
        old=m.rq(m.manager+0xc8);m.q(m.manager+0xc8,0);n=len(m.nav_writes)
        m.stub('v33_recover_hidden_top_menu_after_dialog',m.refresh_inputs)
        assert len(m.nav_writes)==n;m.q(m.manager+0xc8,old);checks+=1
        m.active[m.nav+0x400]=0;m.dead.add(m.nav);m.stub('v33_recover_hidden_top_menu_after_dialog',m.refresh_inputs)
        assert not m.active[m.nav+0x400];m.dead.remove(m.nav);checks+=1
        m.null_go=True;m.stub('v33_recover_hidden_top_menu_after_dialog',m.refresh_inputs)
        assert not m.active[m.nav+0x400];m.null_go=False;checks+=1
        m.stub('v33_recover_hidden_top_menu_after_dialog',{0:0});checks+=1
    result=dict(passed=True,arm64_cases=checks,binary_sha256=hashlib.sha256(after).hexdigest(),
        aslr_biases=[0,0x1000000000],v32_negative_controls=negative,
        actual_UIManager_RefreshUI_body_executed=True,stock_widget_updates_and_caller_arguments_preserved=True,
        hidden_top_menu_restored_after_dialog_or_menu_closes=True,repeated_refresh_is_idempotent=True,
        active_scenario_Darkly_menu_and_pending_translation_do_not_reveal_nav=True,
        accessibility_focus_only_on_recovery=True,null_and_destroyed_component_guards_checked=True,
        Unity_and_child_widget_boundaries_modeled=True,complete_therapist_event_reproduced=False,
        device_runtime_tested=False,BlueStacks_runtime_tested=False)
    (ROOT/'header33_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)

if __name__=='__main__':validate();os._exit(0)
