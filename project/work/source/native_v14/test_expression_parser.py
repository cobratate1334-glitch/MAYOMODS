"""Exercise the actual ARM64 decimal scanner, with managed BCL calls stubbed.

This reproduces the nested-token rejection in the original game parser and
checks the numeric input emitted by v14's pre-expansion bridge is accepted.
It is an instruction test, not an Android/Unity runtime test.
"""
import io,json,struct,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
ROOT=Path(__file__).resolve().parent
def validate(binary):
 loads=[s for s in ELFFile(io.BytesIO(binary)).iter_segments()if s['p_type']=='PT_LOAD']
 def read(a,n):
  s=next(s for s in loads if s['p_vaddr']<=a<s['p_vaddr']+s['p_filesz']);o=s['p_offset']+a-s['p_vaddr'];return binary[o:o+n]
 def case(expr,bias):
  u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);pages=set();heap=0x7000000000;nxt=heap+0x10000;out=[];builder=heap+0x8000;accepted=[]
  def mapat(a,n):
   for p in range(a&~4095,(a+n+4095)&~4095,4096):
    if p not in pages:u.mem_map(p,4096);pages.add(p)
  def q(a,v):u.mem_write(a,struct.pack('<Q',v))
  def d(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  mapat(heap,0x40000)
  def managed(t):
   nonlocal nxt
   p=nxt;nxt+=0x1000;d(p+0x10,len(t));u.mem_write(p+0x14,t.encode('utf-16-le'));return p
  def st(p):return ''if not p else bytes(u.mem_read(p+0x14,struct.unpack('<I',u.mem_read(p+0x10,4))[0]*2)).decode('utf-16-le')
  a=0x3038ec8;mapat(a+bias,0x724);u.mem_write(a+bias,read(a,0x724))
  calls=[0x4dff5a8,0x2237158,0x4e0a104,0x4dfa448,0x4eca154,0x4ec6310,0x4ecc570,0x4e04b18,0x4e04b24,0x4e021e4,0x30395ec,0x303970c,0x4e0b950,0x4e0c26c,0x4df129c,0x3039934]
  for c in calls:mapat(c+bias,4)
  for a,n in [(0x60c3fd1,1),(0x5c232c8,8),(0x5c23110,8),(0x5c6bb20,8),(0x5c7de20,64)]:mapat(a+bias,n)
  u.mem_write(0x60c3fd1+bias,b'\1');klass=heap+0x1000;slot=heap+0x2000;types=heap+0x3000
  q(slot,klass);d(klass+0xe4,1);q(types+0x88,klass);q(0x5c23110+bias,types);q(0x5c232c8+bias,slot);q(0x5c6bb20+bias,slot)
  for j,t in enumerate(['==','!=','>=','(','<=','&&',')','||']):
   cell=heap+0x9000+j*8;q(cell,managed(t));q(0x5c7de20+bias+j*8,cell)
  u.reg_write(UC_ARM64_REG_TPIDR_EL0,heap+0x35000);u.reg_write(UC_ARM64_REG_SP,heap+0x3ff00)
  u.reg_write(UC_ARM64_REG_X0,managed(expr));u.reg_write(UC_ARM64_REG_X1,heap+0x5000);u.reg_write(UC_ARM64_REG_X2,heap+0x6000)
  def hook(uc,pc,size,_):
   va=pc-bias
   if va in [0x303956c,0x30395a0]:
    sp=uc.reg_read(UC_ARM64_REG_SP);balance=struct.unpack('<I',uc.mem_read(sp+4,4))[0]
    accepted.append(va==0x30395a0 and balance==0 and uc.reg_read(UC_ARM64_REG_W28)>0);uc.emu_stop();return
   if va not in calls:return
   x=[uc.reg_read(globals()['UC_ARM64_REG_X'+str(i)])for i in range(5)];ret=0
   if va==0x4dff5a8:ret=int(not st(x[0]).strip())
   elif va==0x2237158:ret=builder
   elif va==0x4e0a104:ret=0
   elif va==0x4dfa448:ret=ord(st(x[0])[x[1]])
   elif va==0x4eca154:ret=int(chr(x[0]).isspace())
   elif va==0x4ec6310:ret=int(chr(x[0]).isdigit())
   elif va==0x4ecc570:ret=int(chr(x[0]).isalpha())
   elif va in [0x4e04b18,0x4e04b24]:
    t=st(x[0]);end=len(t)if va==0x4e04b18 else x[2]+x[3];ret=t.find(chr(x[1]),x[2],end)&0xffffffff
   elif va==0x4e021e4:ret=managed(st(x[0])[x[1]:x[1]+x[2]])
   elif va==0x30395ec:
    val=int(st(x[0]));q(x[1],val);q(x[1]+8,0);ret=1
   elif va==0x303970c:out.append(str(x[1]));ret=builder
   elif va==0x4e0b950:out.append(st(x[1]));ret=builder
   elif va==0x4e0c26c:out.append(chr(x[1]));ret=builder
   elif va==0x4df129c:ret=int(st(x[0])==st(x[1]))
   elif va==0x3039934:raise AssertionError('unexpected nested token reached resolver')
   lr=uc.reg_read(UC_ARM64_REG_X30)
   for i in range(18):uc.reg_write(globals()['UC_ARM64_REG_X'+str(i)],0xdead000+i)
   uc.reg_write(UC_ARM64_REG_X0,ret);uc.reg_write(UC_ARM64_REG_PC,lr)
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x3038ec8+bias,0,count=10000)
  assert len(accepted)==1;return accepted[0],''.join(out)
 checks=0
 for bias in [0,0x1000000000]:
  for nested,resolved in [('<function:add:1:<function:add:2:3>> > 5','6 > 5'),('(<function:clamp:<function:add:40:20>:10:90>> > 50)','(60 > 50)'),('(<function:div:<GFC.workplace_roles_v14.CorePrestige>:4>> >= 10)','(20 >= 10)')]:
   assert not case(nested,bias)[0],nested;assert case(resolved,bias)[0],(resolved,case(resolved,bias));checks+=2
 result=dict(instruction_cases=checks,nested_rejection_reproduced=True,expanded_input_accepted=True,device_runtime_tested=False)
 (ROOT/'expression_validation.json').write_text(json.dumps(result,indent=2));print(result);return result
if __name__=='__main__':validate(Path(sys.argv[1]).read_bytes())
