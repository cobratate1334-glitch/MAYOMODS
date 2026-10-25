"""Reproduce cached picker overlap and execute the v33 shared navigation fix.

Uses real ARM64 Actions, the exact stock RevealDarkly Count-1 instructions,
DismissAllLists, DismissAllDarklies and ResetTypes. Unity rendering, generic
collection operations, coroutine scheduling and fresh prefab creation are
modeled boundaries. No phone or BlueStacks runtime is available here.
"""
import hashlib,json,struct,sys
from pathlib import Path
from unicorn.arm64_const import UC_ARM64_REG_PC,UC_ARM64_REG_SP,UC_ARM64_REG_S0,UC_ARM64_REG_S1
from test_native34 import NewLife31,ROOT,test_native,X
from native_hooks import h

class Navigation(NewLife31):
    REAL={0x2f7c898:0x1c8,0x2f770ec:0x1a4,0x2f77290:12,0x2f77580:0x24}
    API={0x2eabd98,0x2fd7d88,0x2ffb090,0x2ff7e38,0x2e87cec,0x4f5a490,
         0x498fee4,0x49919c8,0x557b2cc,0x2f838cc,0x2eba3e4,
         0x2f99f14,0x5881294,0x2f5fb20,0x2f758a0}
    def __init__(self,binary,bias):
        super().__init__(binary,bias)
        self.ui_manager=self.alloc();self.q(self.game+0x90,self.ui_manager);self.q(self.ui_manager+0x60,self.list_manager)
        self.ticker=self.alloc();self.q(self.ui_manager+0x88,self.ticker)
        self.containers=[self.alloc(),self.alloc()];self.collections={c:[]for c in self.containers}
        self.q(self.list_manager+0x30,self.containers[0]);self.q(self.list_manager+0x38,self.containers[1]);self.q(self.list_manager+0x78,self.containers[0])
        self.breadcrumbs=self.alloc();self.q(self.list_manager+0x88,self.breadcrumbs)
        self.shade=self.alloc();self.controls=self.alloc();self.q(self.manager+0x40,self.shade);self.q(self.manager+0x48,self.controls)
        self.positions={};self.destroyed=[];self.stops=[];self.restored=[];self.last_selected=None;self.fail_next_list=False
        self.stock_cleanup_calls=0;self.darkly_cleanup_calls=0;self.lookup_calls=0
        for va in self.API:self.map(va+bias,4)
        for va,n in self.REAL.items():self.map(va+bias,n);self.u.mem_write(va+bias,self.load(va,n))
        self.ui24.discard(0x2f7c898)
        for va in [0x60c3b0b,0x60c3ad7]:self.map(va+bias,1);self.u.mem_write(va+bias,b'\1')
        for va in [0x5c242c0,0x5c23248,0x5c788c0,0x5c78dd0]:self.meta(va)
        self.lookup_closure=self.alloc();self.lookup_veneer=0x6800100+bias
        code=h.asm(f'stp x19,x20,[sp,#-0x20]!\nstp x30,x21,[sp,#0x10]\nmov x19,x0\nmovz x20,#{self.lookup_closure&65535}\nmovk x20,#{self.lookup_closure>>16&65535},lsl #16\nmovk x20,#{self.lookup_closure>>32&65535},lsl #32\nb {0x2f77580+bias:#x}',self.lookup_veneer)
        self.map(self.lookup_veneer,len(code));self.u.mem_write(self.lookup_veneer,code)
        self.darklies=self.alloc();self.q(self.manager+0xc8,self.darklies);self.set_stack([])
    def meta(self,va):
        slot=self.alloc();klass=self.alloc();self.w(klass+0xe4,1)
        self.map(va+self.bias,8);self.q(va+self.bias,slot);self.q(slot,klass)
    def set_stack(self,pages,index=0,kind=5):
        arr=self.alloc(0x20+8*max(1,len(pages)));self.q(arr+0x18,len(pages))
        for n,page in enumerate(pages):self.q(arr+0x20+8*n,page)
        self.q(self.darklies+0x10,arr);self.w(self.darklies+0x18,len(pages));self.w(self.manager+0xbc,index);self.w(self.manager+0xc0,index);self.w(self.manager+0xb4,kind)
    def cached_pages(self):
        return [self.rq(self.rq(self.darklies+0x10)+0x20+8*n)for n in range(self.rw(self.darklies+0x18))]
    def begin(self,cached=True):
        c=self.root();self.w(c+0x40,5);self.active[c+0x400]=1;self.positions[c]=(0,-5)
        other=self.alloc();self.q(other+0x20,self.manager);self.w(other+0x40,6);self.active[other+0x400]=1;self.positions[other]=(120,0)
        self.set_stack([c,other]if cached else[c]);return c,other
    def mock(self,u,pc,size,data):
        va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
        if va==0x2f731fc and bytes(u.mem_read(self.manager+0x110,1))==b'\1':
            u.reg_write(UC_ARM64_REG_SP,u.reg_read(UC_ARM64_REG_SP)+0xc0);self.finish_api(lr,0);return
        if va==0x2f7748c:
            u.reg_write(UC_ARM64_REG_PC,self.lookup_veneer);return
        if va==0x2f775a0:
            self.lookup_calls+=1;self.last_selected=a[0];self.active[a[0]+0x400]=1;self.positions[a[0]]=(0,-5)
            sp=u.reg_read(UC_ARM64_REG_SP);saved=struct.unpack('<QQQQ',u.mem_read(sp,32))
            u.reg_write(X[19],saved[0]);u.reg_write(X[20],saved[1]);u.reg_write(X[21],saved[3]);u.reg_write(UC_ARM64_REG_SP,sp+32)
            self.finish_api(saved[2],0);return
        if va==0x2f770ec:self.darkly_cleanup_calls+=1
        if va==0x2f7c898:self.stock_cleanup_calls+=1
        if va==0x55779e0:
            assert a[0]in [self.manager,self.list_manager,*self.containers]and a[1]==0;self.stops.append(a[0]);self.finish_api(lr,0);return
        if va==0x3089aac and self.fail_next_list:
            self.fail_next_list=False;self.finish_api(lr,0);return
        if va in self.API:
            result=0
            if va==0x2eabd98:assert a[:2]==[self.ticker,0]
            elif va==0x2ffb090:
                assert a[0]in self.containers;self.collections[a[0]]=[]
            elif va==0x2ff7e38:
                assert a[0]in self.containers;self.current_list_title=''
            elif va==0x4f5a490:assert a[0]!=0
            elif va==0x498fee4:
                assert a[0]==self.darklies;result=self.cached_pages()[a[1]]
            elif va==0x49919c8:
                assert a[0]==self.darklies;pages=self.cached_pages();pages.pop(a[1]);self.set_stack(pages,self.rw(self.manager+0xbc),self.rw(self.manager+0xb4))
            elif va==0x557b2cc:
                self.destroyed.append(a[0]);self.active[a[0]]=0;self.dead.add(a[0]-0x400)
            elif va==0x2f99f14:
                self.positions[a[0]]=tuple(struct.unpack('<f',struct.pack('<I',u.reg_read(reg)))[0]for reg in [UC_ARM64_REG_S0,UC_ARM64_REG_S1])
            elif va==0x5881294:assert a[0]==self.darkly_canvas and a[1]==0
            elif va==0x2f5fb20:assert a[0]==self.controls and a[1]==0
            elif va==0x2f758a0:
                assert a[:4]==[self.manager,5,5,0];self.restored.append(self.rw(self.manager+0xbc))
            self.finish_api(lr,result);return
        super().mock(u,pc,size,data)
        if va==0x3089aac:
            self.w(self.list_manager+0x80,1);self.collections[self.containers[0]].append(self.current_list_title)
    def map_open(self):self.click(self.buttons[6][0])
    def back(self,exit='back'):
        name='v27_editor_root_'+exit;obj=self.containers[0]if exit=='back'else self.list_manager
        self.hook(name,{0:obj,1:0,2:1},end=self.exit)
    def run_routine(self,name,args):
        va=next(r['stub']for r in self.d['routines']if r['name']==name)
        return self.native_call(va,args)

# v34 validation is in test_regressions34.py.
