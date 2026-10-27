"""Execute real UI transitions with explicit Unity object/slide/widget doubles."""
import io,json,struct
from pathlib import Path
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
from unicorn.arm64_const import UC_ARM64_REG_PC,UC_ARM64_REG_SP
from menu_repair.native import Patch
from native_hooks import h
from playable_repair.tests.test_navigation import NavigationMachine as Previous,X,Q

class Machine(Previous):
 def __init__(self,raw,d,bias=0):
  super().__init__(raw,d,bias)
  for seg in self.loads:
   if seg['p_flags']&1:
    self.map(seg['p_vaddr']+bias,seg['p_memsz']);self.u.mem_write(seg['p_vaddr']+bias,raw[seg['p_offset']:seg['p_offset']+seg['p_filesz']])
  self.map_code(0xfad000,4096) # Original ShowListPanel animation-duration constant.
  self.u.mem_write(0x3089aac+bias,h.asm(f'b {self.defer["stub"]+bias:#x}',0x3089aac+bias))
  for state in d['states'].values():self.map(state['va']+bias,state['size'])
  self.map(self.HEAP,0x1000000);self.allocptr=self.HEAP+0x40000;self.active={};self.components={};self.slides=[];self.stop_calls=[];self.moves=[];self.widgets=[]
  self.game=self.alloc();self.life=self.alloc();self.hero=self.alloc();self.ui=self.alloc();self.dark=self.alloc();self.sc=self.alloc();self.lm=self.alloc();self.nav=self.alloc();self.hbar=self.alloc();self.container=self.alloc();self.rect=self.alloc();self.normal_list=self.alloc()
  slot=0x5c23c90+bias;self.map(slot,8);ref=self.alloc();klass=self.alloc();static=self.alloc();self.q(slot,ref);self.q(ref,klass);self.q(klass+0xb8,static);self.q(static,self.game)
  self.q(self.game+0x20,self.life);self.q(self.game+0x28,self.hero);self.q(self.game+0x90,self.ui);self.q(self.ui+0x38,self.nav);self.q(self.ui+0x40,self.hbar);self.q(self.ui+0x60,self.lm);self.q(self.ui+0x80,self.sc);self.q(self.ui+0xa0,self.dark);self.q(self.dark+0xc8,self.alloc());self.q(self.lm+0x78,self.container)
  self.q(self.container+0x20,self.rect);self.q(self.container+0xa0,self.ui);self.q(self.container+0x88,self.hbar);nested=self.alloc();self.q(nested+0x28,self.rect);self.q(self.container+0x90,nested)
  self.list_widget=self.alloc();self.list_collection=self.alloc();self.q(self.list_widget+0x90,self.normal_list);self.q(self.container+0xc0,self.list_collection);self.w(self.container+0x110,0)
  self.w(self.list_collection+0x18,1);self.map(0x5c7c9d0+bias,8);ref=self.alloc();self.q(0x5c7c9d0+bias,ref);self.q(ref,self.alloc())
  for off in [0x68,0x70,0xc0]:self.q(self.ui+off,self.alloc())
  for comp in [self.nav,self.hbar,self.rq(self.ui+0x68),self.rq(self.ui+0x70)]:self.components[comp]=self.alloc();self.active[self.components[comp]]=True
  self.active[self.components[self.nav]]=False;self.hbar_swapped=True;self.w(self.hero+0x18,1);self.w(self.hero+0x20,20)
  for a in [0x60c3b4c,0x60c3e7b,0x60c3e7d,0x60c2f03,0x60c3e08]:self.map(a+bias,1);self.u.mem_write(a+bias,b'\1')
  for slot in [0x5c713c8,0x5c6dd18,0x5c2a0b0,0x5c7cb20]:
   self.map(slot+bias,8);ref=self.alloc();klass=self.alloc();static=self.alloc();self.q(slot+bias,ref);self.q(ref,klass);self.q(klass+0xb8,static);self.q(static,self.alloc());self.w(klass+0xe4,1)
  self.apis={0x55725ac,0x5575728,0x55757dc,0x5575664,0x5575198,0x2f838cc,0x2e87cec,0x2fee170,0x588b85c,0x2f82a5c,0x5577470,0x55779e0,0x2f7db1c,0x2f7e424,0x2f8144c,0x2f7e530,0x2f7e5a0,0x2f5fb20,0x2f5d028,0x2fee01c,0x5581ec4,0x2237158,0x4ec64e4,0x2f5f89c,0x2f5f7a0,0x2f7d268}
  self.apis.remove(0x2f7d268);self.apis.update([0x498fee4,0x2fd7d88]) # Generic list lookup and non-holiday clock boundary.
  for a in self.apis:self.map(a+bias,4)
 def map(self,address,size):
  start=None;end=None
  for page in range(address&~4095,(address+size+4095)&~4095,4096):
   if page not in self.pages:
    self.pages.add(page)
    if start is None:start=page
    end=page+4096
   elif start is not None:self.u.mem_map(start,end-start);start=None
  if start is not None:self.u.mem_map(start,end-start)
 def alloc(self,n=0x500):p=self.allocptr;self.allocptr=(p+n+15)&~15;return p
 def w(self,p,n):self.u.mem_write(p,struct.pack('<I',n&0xffffffff))
 def rw(self,p):return struct.unpack('<I',self.u.mem_read(p,4))[0]
 def f(self,p,n):self.u.mem_write(p,struct.pack('<f',n))
 def code_hook(self,u,pc,size,data):
  if pc-self.bias in [0x2f939dc,0x2f93a20] and getattr(self,'choice_scene',None):u.reg_write(X[0],self.choice_scene)
  if pc-self.bias==self.CHOICE and getattr(self,'empty_choice',False):self.finish_api(u.reg_read(X[30]),0);return
  if pc==getattr(self,'stop_end',None):self.stopped=True;u.emu_stop();return
  va=pc-self.bias;a=[u.reg_read(r)for r in X[:6]];lr=u.reg_read(X[30])
  if va not in getattr(self,'apis',set()):return super().code_hook(u,pc,size,data)
  result=0
  if va==0x55725ac:result=self.components.get(a[0],a[0])
  elif va in [0x5575728,0x55757dc]:result=int(self.active.get(a[0],False))
  elif va==0x5575664:self.active[a[0]]=bool(a[1]);self.events.append(('active',a[0],bool(a[1])))
  elif va==0x5575198:result=int(bool(a[0]))
  elif va==0x2fee170:
   assert a[0]==self.hbar;self.hbar_swapped=not self.hbar_swapped
   if getattr(self,'new_transition_during_callback',False):
    epoch=self.d['states']['menu_generation41']['va']+self.bias;self.w(epoch,self.rw(epoch)+1)
    slot=self.d['states']['menu_repair']['va']+self.bias+256+8*32;self.w(slot,1);self.w(slot+4,self.rw(epoch))
  elif va==0x2f838cc:assert a[0]==self.ui;result=0
  elif va==0x2e87cec:result=0
  elif va==0x55779e0:self.stop_calls.append(a[0]);self.slides=[]
  elif va==0x2f7db1c:assert a[0]==self.lm;result=self.alloc()
  elif va in [0x2f7e424,0x2f8144c,0x2f7e530,0x2f7e5a0]:assert a[0]==self.ui;self.widgets.append(va)
  elif va==0x2f5fb20:self.moves.append(a[0])
  elif va==0x2237158:result=self.alloc()
  elif va==0x498fee4:assert a[0]==self.list_collection and a[1]==0;result=self.list_widget
  elif va==0x4ec64e4:assert a[1]==self.ui
  elif va==0x2f5f89c:self.slides.append('swap');result=self.alloc()
  elif va==0x2f5f7a0:self.slides.append('move');result=self.alloc()
  elif va in [0x5577470,0x2f82a5c]:result=self.alloc()
  self.finish_api(lr,result)
  if va in [0x2f5d028,0x2fee01c,0x5581ec4]:
   values=[0.,100.]if va!=0x2f5d028 else[0.]
   for i,value in enumerate(values):u.reg_write(Q[i],int.from_bytes(struct.pack('<f',value),'little'))
 def call(self,address,args=None,skip_first_stack=False,end=None):
  for i in range(31):self.u.reg_write(X[i],0x880000+i)
  for i,v in (args or {}).items():self.u.reg_write(X[i],v)
  sp=self.HEAP+0xf00000;self.u.reg_write(UC_ARM64_REG_SP,sp-(0x180 if skip_first_stack else 0));self.u.reg_write(X[30],self.EXIT);self.stopped=False
  self.stop_end=end+self.bias if end is not None else None
  self.u.emu_start(address+self.bias,0,count=500000);assert self.stopped,hex(self.u.reg_read(UC_ARM64_REG_PC));assert self.u.reg_read(UC_ARM64_REG_SP)==sp
  return self.u.reg_read(X[0])
 def routine(self,name,args=None):return self.call(self.records[name]['stub'],args)
 def refresh_recovery(self):
  # Real chained call resumes after the displaced SUB SP of the v33 hook.
  r=self.records['v33_recover_hidden_top_menu_after_dialog'];return self.call(r['stub']+4,{0:self.ui},True,r['stub']+r['length']-8)
 def hide(self,animated=False):
  it=self.alloc();self.w(it+0x10,0);self.w(it+0x14,self.rw(self.d['states']['menu_generation41']['va']+self.bias));self.q(it+0x20,self.container);self.f(it+0x28,.2 if animated else 0.);self.u.mem_write(it+0x2c,b'\1');self.f(self.container+0xd0,-1000.)
  return it,self.call(0x3010750,{0:it})
 def run_slide_callback(self):
  assert 'swap'in self.slides;self.slides.remove('swap');self.call(0x2f832ec,{0:self.ui})
 def begin_show(self):
  it=self.alloc();self.w(it+0x10,0);self.w(it+0x14,self.rw(self.d['states']['menu_generation41']['va']+self.bias));self.q(it+0x20,self.container);self.u.mem_write(it+0x28,b'\1')
  return it,self.call(0x3010dcc,{0:it})
