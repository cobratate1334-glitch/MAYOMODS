"""Reproduce missing New Life buttons using the shipped prefab and fitter.

Executes stock ARM64 GetComponent(Type), AddDriver and UpdateConstraint.
Unity engine calls and generic List allocation/copying are modeled boundaries.
The old v25 output is a negative control. This is not a device rendering test.
"""
import hashlib, io, json, os, struct, sys, zipfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from test_engine24 import Engine24
from test_native import ROOT, X
from unicorn.arm64_const import UC_ARM64_REG_PC, UC_ARM64_REG_S0, UC_ARM64_REG_S1

FIXTURE=json.loads((ROOT/'newlife_layout_fixture26.json').read_text())

def verify_fixture(apk, original):
 import UnityPy
 assert hashlib.sha256(Path(apk).read_bytes()).hexdigest()==FIXTURE['base_apk_sha256']
 with zipfile.ZipFile(apk) as z:
  metadata=z.read('assets/bin/Data/Managed/Metadata/global-metadata.dat')
  env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'))
  data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'))
 assert hashlib.sha256(metadata).hexdigest()==FIXTURE['metadata_sha256']
 f=next(f for f in env.assets if f.name=='resources.assets')
 assert f.objects[20995].read().m_IsActive is False
 raw=f.objects[32394].get_raw_data()
 assert hashlib.sha256(raw).hexdigest()==FIXTURE['fitter_raw_sha256']
 assert struct.unpack_from('<I',raw,44)[0]==len(FIXTURE['drivers'])==12
 for i,driver in enumerate(FIXTURE['drivers']):
  file_id,path_id=struct.unpack_from('<iq',raw,48+i*12)
  assert file_id==0 and path_id==(driver['path_id'] if driver else 0)
  if driver:
   rect=f.objects[path_id].read();go=rect.m_GameObject.deref().read()
   assert go.m_IsActive==driver['active'] and rect.m_SizeDelta.y==driver['height']
 assert struct.unpack_from('<f',f.objects[32391].get_raw_data(),52)[0]==FIXTURE['spacing']
 container=dict(next(o for o in data.objects if o.type.name=='ResourceManager').read_typetree()['m_Container'])
 assert container[FIXTURE['prefab_path']]['m_PathID']==20995
 def name(index):
  a=2173460+index;return metadata[a:metadata.index(b'\0',a)].decode()
 namespaces={}
 for i in range(21614):
  p=15793280+i*76;cls=name(struct.unpack_from('<I',metadata,p)[0])
  if cls in FIXTURE['namespaces']:namespaces[cls]=name(struct.unpack_from('<I',metadata,p+4)[0])
 assert namespaces==FIXTURE['namespaces']
 # Resolve the public managed GameObject.GetComponent overloads from the actual
 # UnityEngine.CoreModule token table. An injected IntPtr API is not equivalent.
 lib=Path(original).read_bytes();elf=ELFFile(io.BytesIO(lib))
 loads=[s for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
 reloc={r['r_offset']:r['r_addend'] for r in elf.get_section_by_name('.rela.dyn').iter_relocations()}
 def ptr(va):
  seg=next(s for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz'])
  return reloc.get(va,struct.unpack_from('<Q',lib,seg['p_offset']+va-seg['p_vaddr'])[0])
 methods=[]
 for i in range(149917):
  p=6323900+i*30
  if struct.unpack_from('<H',metadata,p+4)[0]==14758 and name(struct.unpack_from('<I',metadata,p)[0])=='GetComponent':
   rid=struct.unpack_from('<I',metadata,p+18)[0]&0xffffff;methods.append(ptr(0x607bfc0+(rid-1)*8))
 assert 0x557269c in methods and 0x5574b80 not in methods
 return 6+len(FIXTURE['drivers'])

class Layout26(Engine24):
 REAL={0x557269c:0xa4,0x2f5bc48:0x140,0x2f5b52c:0x67c}
 BOUNDARY={0xf0002100,0x5536ee4,0x498f9a8,0x49903ac,0x4991d48,
           0x5576804,0x5575728,0x5581ec4,0x5581f90}
 def __init__(self,binary,bias):
  super().__init__(binary,bias)
  self.geometry={};self.rect_go={};self.adds=0;self.getcomponents=0;self.updates=0
  self.content=self.alloc();self.layout=self.alloc();self.list_class=self.alloc();self.type_class=self.alloc()
  self.parent_native=self.alloc();self.go=self.heap+0x128400
  self.q(self.go+0x10,self.parent_native)
  for va,size in self.REAL.items():self.map(va+bias,size);self.u.mem_write(va+bias,self.load(va,size))
  for va in self.BOUNDARY:self.map(va+bias,4)
  for va in [0x60d0e78,0x60c3a1a,0x60c3a1b]:self.map(va+bias,1);self.u.mem_write(va+bias,b'\1')
  self.qslot(0x5cfb300,self.type_class);self.qslot(0x5c23248,self.type_class);self.w(self.type_class+0xe4,1)
  self.map(0x60d0e98+bias,8);self.q(0x60d0e98+bias,0xf0002100+bias)
  self.qslot(0x5c24258,self.list_class)
  for va in [0x5c24250,0x5c24240,0x5c24248,0x5c780f8]:self.qslot(va,self.type_class)
  self.q(self.fitter+0x38,self.content);self.q(self.fitter+0x50,self.layout)
  self.u.mem_write(self.fitter+0x20,bytes([1,0,1]))
  self.float(self.layout+0x60,FIXTURE['spacing']);self.geometry[self.content]=(1109.,300.)
  for driver in FIXTURE['drivers']:
   if driver:
    rect=self.alloc();go=self.alloc();self.rect_go[rect]=go;self.active[go]=int(driver['active']);self.geometry[rect]=(driver['width'],driver['height'])
   else:rect=0
   self.drivers.append(rect)
  self.q(self.fitter+0x28,self.array(self.drivers));self.royal=self.drivers[4]
 def float(self,addr,value):self.u.mem_write(addr,struct.pack('<f',value))
 def qslot(self,addr,value):
  slot=self.alloc();self.q(slot,value);self.map(addr+self.bias,8);self.q(addr+self.bias,slot)
 def array(self,values,capacity=None):
  array=self.alloc(0x20+8*(capacity or len(values)));self.q(array+0x18,capacity or len(values))
  for i,value in enumerate(values):self.q(array+0x20+8*i,value)
  return array
 def values(self,array):return [self.rq(array+0x20+i*8) for i in range(self.rq(array+0x18))]
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if va in self.REAL:return # execute actual stock function body
  a=[u.reg_read(r) for r in X[:4]];lr=u.reg_read(X[30]);ret=0;fp=None
  if va==0x2f72230:
   existing=a[1];super().mock(u,pc,size,data);button=u.reg_read(X[0]);rect=self.rq(button+0x28)
   self.rect_go[rect]=button+0x400;self.geometry[rect]=(1109.,230.)
   if not existing:assert not self.active[button+0x400]
   return
  if va==0x55725ac and a[0] in self.rect_go:ret=self.rect_go[a[0]]
  elif va==0x2237158 and a[0]==self.list_class:ret=self.alloc()
  elif va not in self.BOUNDARY:return super().mock(u,pc,size,data)
  elif va==0xf0002100:
   assert a[:2]==[self.parent_native,self.heap+0x141500] and self.reflected_class=='ConstraintContentSizeFitter'
   self.getcomponents+=1;ret=self.parent_native+16
  elif va==0x5536ee4:assert a[:2]==[self.parent_native+16,self.type_class];ret=self.fitter
  elif va==0x498f9a8:self.q(a[0]+0x10,self.array([],64));self.w(a[0]+0x18,0)
  elif va==0x49903ac:
   values=self.values(a[1]);arr=self.rq(a[0]+0x10)
   for i,v in enumerate(values):self.q(arr+0x20+i*8,v)
   self.w(a[0]+0x18,len(values))
  elif va==0x4991d48:
   arr=self.rq(a[0]+0x10);values=[self.rq(arr+0x20+i*8) for i in range(self.rw(a[0]+0x18))]
   self.drivers=values;ret=self.array(values);self.adds+=1
  elif va==0x5576804:ret=int(a[0]==a[1])
  elif va==0x5575728:ret=self.active.get(a[0],0)
  elif va==0x5581ec4:fp=self.geometry[a[0]]
  elif va==0x5581f90:
   def f(r):return struct.unpack('<f',struct.pack('<I',u.reg_read(r)))[0]
   self.geometry[a[0]]=(f(UC_ARM64_REG_S0),f(UC_ARM64_REG_S1));self.updates+=1
  self.finish_api(lr,ret)
  if fp:
   for reg,value in zip([UC_ARM64_REG_S0,UC_ARM64_REG_S1],fp):u.reg_write(reg,struct.unpack('<I',struct.pack('<f',value))[0])
 def height(self):
  self.native_call(0x2f5b52c,{0:self.fitter});return self.geometry[self.content][1]

def validate(path,oldpath,apk,original):
 checks=verify_fixture(apk,original);manifest=ROOT/'native_hooks.json';current=manifest.read_bytes()
 oldmanifest=ROOT.parent/'native_v25/native_hooks.json'
 try:
  manifest.write_bytes(oldmanifest.read_bytes());old=Layout26(Path(oldpath).read_bytes(),0)
  controller=old.alloc();old.q(controller+0x20,old.manager);old.q(controller+0xd0,old.alloc());before=old.height()
  old.stub('v21_new_life_native_buttons',{19:controller})
  assert len(old.buttons)==2 and all(not old.active[b+0x400] for b,_ in old.buttons)
  assert len(old.drivers)==12 and old.height()==before;checks+=2
 finally:manifest.write_bytes(current)
 for bias in [0,0x1000000000]:
  m=Layout26(Path(path).read_bytes(),bias);controller=m.alloc();m.q(controller+0x20,m.manager);m.q(controller+0xd0,m.alloc())
  for royalty in [False,True,False]:
   m.active[m.rect_go[m.royal]]=int(royalty);before=m.height()
   m.stub('v21_new_life_native_buttons',{19:controller})
   assert len(m.buttons)==2 and len(m.drivers)==14 and m.adds==2
   assert len(set(v for v in m.drivers if v))==13
   assert all(m.active[b+0x400] for b,_ in m.buttons)
   after=m.height();assert after>before if m.getcomponents==2 else after==before
   # Real stock fitter measures exactly two extra full button heights/spaces.
   expected=sum(m.geometry[r][1]+(FIXTURE['spacing'] if i<len(m.drivers)-1 else 0)
                for i,r in enumerate(m.drivers) if r and m.active.get(m.rect_go[r],0))
   assert after==expected
   for _ in range(5):m.stub('v21_new_life_native_buttons',{19:controller});assert m.height()==after and m.adds==2
   checks+=10
  assert m.getcomponents==36 and len(m.handles)==3;checks+=1
 report=dict(binary_sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),arm64_cases=checks,
   actual_prefab_and_metadata_verified=True,old_v25_missing_buttons_reproduced=True,
   exact_fitter_namespace_verified=True,actual_public_GetComponent_executed=True,
   actual_stock_AddDriver_executed=True,actual_stock_UpdateConstraint_executed=True,
   hidden_prefab_activated=True,both_controls_in_scroll_height=True,royalty_visibility_changes=True,
   repeated_refresh_without_duplicates=True,aslr_biases=[0,0x1000000000],device_runtime_tested=False)
 (ROOT/'layout26_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':validate(*sys.argv[1:]);os._exit(0)
