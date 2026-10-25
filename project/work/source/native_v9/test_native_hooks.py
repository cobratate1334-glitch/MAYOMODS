"""Execute new ARM64 instructions with ABI mocks at two load addresses."""
import io,json,struct
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
ROOT=Path(__file__).resolve().parent
def validate(binary,details):
 e=ELFFile(io.BytesIO(binary));loads=[s for s in e.iter_segments()if s['p_type']=='PT_LOAD'];checks=0
 def read(va,n):
  s=next(s for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']);o=s['p_offset']+va-s['p_vaddr'];return binary[o:o+n]
 for bias in [0,0x1000000000]:
  def case(name,sport=2,kind=3,branch=1,key='NativeMilitarySync',success=1,missing=False,resource='genesis_v7_prison'):
   nonlocal checks
   h=next(x for x in details['hooks']if x['name']==name);u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);mapped=set();heap=0x7000000000
   def mapat(a,n):
    for p in range(a&~4095,(a+n+4095)&~4095,4096):
     if p not in mapped:u.mem_map(p,4096);mapped.add(p)
   def put(a,v):u.mem_write(a,struct.pack('<Q',v))
   def p32(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
   mapat(details['segment_va']+bias,details['segment_size']);u.mem_write(details['segment_va']+bias,binary[details['segment_offset']:details['segment_offset']+details['segment_size']])
   mapat(heap,0x30000);mapat(0x5c23c90+bias,8)
   old=int(h['original'].split()[-1],16)if name in ('sports_menus','military_branch_sync')else None
   exits=[h['resume'],0x3089aac,0x30895ac]+([old]if old else[]);callees=[0x223e8cc,0x30611d0,0x31542f0,0x3059f90]
   for va in exits+callees+[h['site']]:mapat(va+bias,4)
   u.mem_write(h['site']+bias,read(h['site'],4))
   slot,klass,static,game,life,occ,bp,owner,collection=[heap+i*0x500 for i in range(9)]
   put(0x5c23c90+bias,slot);put(slot,klass);put(klass+0xb8,static);put(static,game);put(game+0x20,life);put(life+0x138,occ);p32(occ+0x10,kind);p32(occ+0x28,branch)
   if missing:put(life+0x138,0)
   nxt=heap+0x10000
   def managed(t):
    nonlocal nxt
    p=nxt;nxt+=0x100;p32(p+0x10,len(t));u.mem_write(p+0x14,t.encode('utf-16-le'));return p
   def st(p):
    n=struct.unpack('<I',u.mem_read(p+0x10,4))[0];return bytes(u.mem_read(p+0x14,n*2)).decode('utf-16-le')
   put(bp+0x18,managed(key));sp=heap+0x2ff00
   for i in range(31):u.reg_write(globals()['UC_ARM64_REG_X'+str(i)],0x550000+i)
   for i in range(8):u.reg_write(globals()['UC_ARM64_REG_Q'+str(i)],(0xabcde<<80)+i)
   u.reg_write(UC_ARM64_REG_SP,sp)
   if name=='entry_presentation':u.reg_write(UC_ARM64_REG_X0,managed(resource));u.reg_write(UC_ARM64_REG_X1,0)
   if name=='school_menu':u.reg_write(UC_ARM64_REG_X19,collection)
   if name=='sports_menus':u.reg_write(UC_ARM64_REG_X26,collection)
   if name=='military_branch_sync':u.reg_write(UC_ARM64_REG_X19,bp);u.reg_write(UC_ARM64_REG_X21,owner);u.reg_write(UC_ARM64_REG_W0,success)
   before=[u.reg_read(globals()['UC_ARM64_REG_X'+str(i)])for i in range(31)];qb=[u.reg_read(globals()['UC_ARM64_REG_Q'+str(i)])for i in range(8)];calls=[];exited=[]
   def mock(uc,pc,size,data):
    va=pc-bias
    if va in exits:exited.append(va);uc.emu_stop();return
    if va not in callees:return
    args=[uc.reg_read(globals()['UC_ARM64_REG_X'+str(i)])for i in range(5)];calls.append((va,args));ret=0
    if va==0x223e8cc:ret=managed(bytes(uc.mem_read(args[0],96)).split(b'\0')[0].decode())
    if va==0x31542f0:ret=sport
    lr=uc.reg_read(UC_ARM64_REG_X30)
    for i in range(18):uc.reg_write(globals()['UC_ARM64_REG_X'+str(i)],0xdead000+i)
    for i in range(8):uc.reg_write(globals()['UC_ARM64_REG_Q'+str(i)],0xdead000+i)
    uc.reg_write(UC_ARM64_REG_X0,ret);uc.reg_write(UC_ARM64_REG_X30,lr);uc.reg_write(UC_ARM64_REG_PC,lr)
   u.hook_add(UC_HOOK_CODE,mock);u.emu_start(h['site']+bias,0,count=3000);assert exited
   after=[u.reg_read(globals()['UC_ARM64_REG_X'+str(i)])for i in range(31)];expected=before[:]
   if name=='entry_presentation':
    custom=resource.startswith(('genesis_v7','genesis_v8','genesis_v9'))or resource=='genesis_music_studio_hub'
    if custom:expected[2]=1;expected[3]=0;expected[4]=0
    assert exited==[0x3089aac if custom else 0x30895ac]and not calls
   if name=='school_menu':expected[8]=0x5c24000+bias
   assert after==expected,(name,'register corruption')
   assert u.reg_read(UC_ARM64_REG_SP)==sp and [u.reg_read(globals()['UC_ARM64_REG_Q'+str(i)])for i in range(8)]==qb
   injections=[(a[0],st(a[1]))for va,a in calls if va==0x30611d0]
   if name=='school_menu':assert injections==[(collection,'School')]
   if name=='sports_menus':assert injections==([(collection,{2:'Basketball',6:'Rugby'}[sport])]if sport in (2,6)else[])and exited==[old]
   if name=='military_branch_sync':
    writes=[(a[0],st(a[1]),a[2],a[3])for va,a in calls if va==0x3059f90]
    valid=kind==3 and 1<=branch<=5 and not missing
    expectedwrites=[(owner,'Branch',branch if valid else 0,0),(owner,'Serving',int(valid),0)]if key=='NativeMilitarySync'and success==1 else[]
    assert writes==expectedwrites and exited==[old],(kind,branch,key,success,writes)
   checks+=1
  for resource in ['genesis_v7_prison','genesis_v8_football_v8','genesis_v9_military_v9','genesis_music_studio_hub','genesis_movie_director_hub','Unrelated','genesis_v6_not_custom']:case('entry_presentation',resource=resource)
  case('school_menu')
  for sport in range(9):case('sports_menus',sport=sport)
  for kind in range(8):
   for branch in range(7):case('military_branch_sync',kind=kind,branch=branch)
  case('military_branch_sync',missing=True);case('military_branch_sync',success=0);case('military_branch_sync',key='UnrelatedProperty')
 result=dict(instruction_cases=checks,load_addresses=2,android_runtime_tested=False)
 (ROOT/'native_validation.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':
 import sys
 print(validate(Path(sys.argv[1]).read_bytes(),json.loads((ROOT/'native_hooks.json').read_text())))
