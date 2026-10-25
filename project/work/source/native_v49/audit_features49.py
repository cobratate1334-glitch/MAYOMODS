"""Execute the game's feature-support constructor to avoid guessed enum IDs."""
import json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE/'native_v29')]
from test_native49 import Machine,X
from inspect_game27 import Game
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm64_const import UC_ARM64_REG_PC
class ConstructorMachine(Machine):
 def mock(self,u,pc,size,data):
  if pc==self.stop_at or pc==getattr(self,'exit',0)+self.bias:self.stopped=True;u.emu_stop();return
  if 0x2f337c0<=pc<0x2f34138:return
  a=[u.reg_read(r)for r in X[:4]];lr=u.reg_read(X[30]);value=0
  if pc in [0x2236f1c,0x4f76cb4]:pass
  elif pc==0x2237158:value=self.alloc()
  elif pc==0x4edba28:
   other=self.list([]);self.q(a[0],self.rq(other));self.q(a[0]+16,self.rq(other+16));self.w(a[0]+24,0);self.listvalues[a[0]]=[]
  elif pc==0xf0003000:
   self.listvalues[a[0]].append(a[1]);self.w(a[0]+24,len(self.listvalues[a[0]]))
  elif pc==0xf0003020:value=self.listvalues[a[0]][a[1]]
  elif pc==0x2237044:value=self.alloc();self.w(value+16,self.rw(a[1]))
  elif pc==0x4df1164:value=self.managed(self.str(a[0]).format(self.rw(a[1]+16)))
  elif pc==0x2f34138:value=self.face+0x1000
  elif pc==0x2f341a0:value=self.palette49
  else:raise AssertionError(('unexpected constructor call',hex(pc),'from',hex(lr)))
  self.finish_api(lr,value)
def audit(binary,metadata):
 raw=Path(binary).read_bytes();g=Game(binary,metadata);m=ConstructorMachine(raw,0)
 first=next(s for s in g.loads if s['p_vaddr']==0);m.map(0,first['p_filesz']);m.u.mem_write(0,g.lib[:first['p_filesz']])
 # Resolve real encoded string-literal usages from this v39 metadata. Keep
 # class/type usages at the explicit managed-allocation boundary.
 for va,pointer in g.reloc.items():
  if not 0x5c00000<=va<0x5c80000:continue
  try:value=g.ptr(pointer)
  except (StopIteration,struct.error):continue
  if value>>29!=5:continue
  index=(value&0x1fffffff)>>1;start,end=struct.unpack_from('<II',g.meta,380+index*4);value=g.meta[284792+start:284792+end].decode('utf-8');m.map(va,8);m.map(pointer,8);m.q(va,pointer);m.q(pointer,m.managed(value))
 for va,n in [(0x2f337c0,0x978),(0xfc4000,0x1000)]:m.map(va,n);m.u.mem_write(va,g.lib[g.off(va):g.off(va)+n])
 for va in [0x4f76cb4,0x2f341a0]:m.map(va,4)
 palette=m.list([m.managed('FFFFFF')]);m.palette49=palette
 def boundary(u,pc,size,data):
  if pc==0x4f76cb4:m.finish_api(u.reg_read(X[30]),0)
  elif pc==0x2f341a0:m.finish_api(u.reg_read(X[30]),palette)
 m.u.hook_add(UC_HOOK_CODE,boundary);m.sorting49=True;rows=[]
 def invalid(u,access,address,size,value,data):print('unmapped',hex(address),'pc',hex(u.reg_read(UC_ARM64_REG_PC)),flush=True);return False
 m.u.hook_add(UC_HOOK_MEM_INVALID,invalid)
 for feature in range(15):
  obj=m.alloc();m.execute42(0x2f337c0,{0:obj,1:feature});rows.append(dict(feature=feature,name=m.str(m.rq(obj+0x30)),segment=m.str(m.rq(obj+0x48)),folder=m.str(m.rq(obj+0x40)),layer=m.rw(obj+0x20),default_colour=m.str(m.rq(obj+0x28))))
 (ROOT/'feature_map49.json').write_text(json.dumps(dict(native_constructor=hex(0x2f337c0),binary_sha256=__import__('hashlib').sha256(raw).hexdigest(),features=rows),indent=2)+'\n');print(json.dumps(rows,indent=2),flush=True)
if __name__=='__main__':
 try:audit(*sys.argv[1:])
 except BaseException:__import__('traceback').print_exc();sys.stdout.flush();sys.stderr.flush();__import__('os')._exit(1)
 sys.stdout.flush();__import__('os')._exit(0)
