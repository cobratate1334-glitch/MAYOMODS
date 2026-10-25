"""Execute the distinct main-menu New Life entry seen in the user's video.

The stock action-1 tail and complete ShowDarklyWithScenario body run as ARM64.
DismissAllLists, DismissAllDarklies, ResetTypes and the stock Count-1 lookup
also run. Prefab creation, rendering and transition scheduling are modeled.
Negative v32 controls reproduce refusal with stale pending/canvas state;
they do not establish the exact device state of the supplied recording.
"""
import hashlib,json,struct
from unicorn.arm64_const import UC_ARM64_REG_PC,UC_ARM64_REG_SP
from test_navigation34 import Navigation,ROOT,test_native,X
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

# v34 validation is in test_regressions34.py.
