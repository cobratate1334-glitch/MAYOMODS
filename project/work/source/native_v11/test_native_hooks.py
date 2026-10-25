"""Execute added ARM64 instructions, with engine calls mocked, at two bases."""
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
  def case(name,key='NativeSoccerSync',kind=6,athletekind=2,sport=5,rank=5,age=30,end=0,choice=0,roll=4,success=1,missing=False):
   nonlocal checks
   h=next(x for x in details['hooks']if x['name']==name);u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);mapped=set();heap=0x7000000000
   def mapat(a,n):
    for p in range(a&~4095,(a+n+4095)&~4095,4096):
     if p not in mapped:u.mem_map(p,4096);mapped.add(p)
   def q(a,v):u.mem_write(a,struct.pack('<Q',v))
   def d(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
   mapat(details['segment_va']+bias,details['segment_size']);u.mem_write(details['segment_va']+bias,binary[details['segment_offset']:details['segment_offset']+details['segment_size']])
   mapat(heap,0x50000);mapat(0x5c23c90+bias,8)
   old=abs(int(__import__('re').search(r'-?0x[0-9a-f]+',h['original'])[0],16))if name=='soccer_and_parole_pulses'else None
   sentinel=heap+0x40000;exits=[h['resume'],sentinel-bias]+([old]if old else[])
   callees=[0x223e8cc,0x3059f90,0x3059ee0,0x32800fc,0x2e0b54c,0x2bc2e24,0x30838cc]
   for va in exits+callees+[h['site']]:mapat(va+bias,4)
   u.mem_write(h['site']+bias,read(h['site'],4))
   slot,klass,static,game,life,hero,occ,bp,owner,athlete,team,record,dsport=[heap+i*0x500 for i in range(13)]
   q(0x5c23c90+bias,slot);q(slot,klass);q(klass+0xb8,static);q(static,game);q(game+0x20,life);q(game+0x28,hero);d(hero+0x20,age);q(life+0x138,occ);d(occ+0x10,kind);q(occ+0x28,athlete);d(athlete+0x10,athletekind);q(athlete+0x30,team);d(team+0x20,123);q(team+0x28,record);d(record+0x1c,rank);d(dsport+0x10,sport)
   if missing:q(game+0x20,0)
   nxt=heap+0x10000
   def managed(t):
    nonlocal nxt
    p=nxt;nxt+=0x200;d(p+0x10,len(t));u.mem_write(p+0x14,t.encode('utf-16-le'));return p
   def st(p):
    n=struct.unpack('<I',u.mem_read(p+0x10,4))[0];return bytes(u.mem_read(p+0x14,n*2)).decode('utf-16-le')
   q(bp+0x18,managed(key));sp=heap+0x4ff00
   for i in range(31):u.reg_write(globals()['UC_ARM64_REG_X'+str(i)],0x550000+i)
   for i in range(8):u.reg_write(globals()['UC_ARM64_REG_Q'+str(i)],(0xabcdef<<80)+i)
   u.reg_write(UC_ARM64_REG_SP,sp);u.reg_write(UC_ARM64_REG_X30,sentinel)
   if name=='soccer_and_parole_pulses':u.reg_write(UC_ARM64_REG_X19,bp);u.reg_write(UC_ARM64_REG_X21,owner);u.reg_write(UC_ARM64_REG_W0,success)
   elif name=='successful_parole_house_arrest':u.reg_write(UC_ARM64_REG_X25,static);q(static,game)
   else:u.reg_write(UC_ARM64_REG_W1,choice&0xffffffff)
   before=[u.reg_read(globals()['UC_ARM64_REG_X'+str(i)])for i in range(31)];qb=[u.reg_read(globals()['UC_ARM64_REG_Q'+str(i)])for i in range(8)];calls=[];writes={};exited=[]
   def mock(uc,pc,size,data):
    va=pc-bias
    if va in exits:exited.append(va);uc.emu_stop();return
    if va not in callees:return
    a=[uc.reg_read(globals()['UC_ARM64_REG_X'+str(i)])for i in range(5)];calls.append((va,a));ret=0
    if va==0x223e8cc:ret=managed(bytes(uc.mem_read(a[0],100)).split(b'\0')[0].decode())
    elif va==0x32800fc:assert a[:3]==[life,a[1],age]and st(a[1])=='parole_v11'and a[3]==0;ret=owner
    elif va==0x3059ee0:assert a[0]==owner and a[3]==0;ret={'EndAge':end,'Releases':2}.get(st(a[1]),a[2])
    elif va==0x3059f90:assert a[0]==owner and a[3]==0;writes[st(a[1])]=struct.unpack('<i',struct.pack('<I',a[2]&0xffffffff))[0];ret=1
    elif va==0x2e0b54c:assert a[:3]==([3,6,0]if name=='successful_parole_house_arrest'else[0,100,0]);ret=roll&0xffffffff
    elif va==0x2bc2e24:assert a[0]==athlete and a[1]==0;ret=dsport
    elif va==0x30838cc:assert st(a[0])=='genesis_v11_house_arrest_travel'and a[1:5]==[1,0,0,0]
    lr=uc.reg_read(UC_ARM64_REG_X30)
    for i in range(18):uc.reg_write(globals()['UC_ARM64_REG_X'+str(i)],0xdead000+i)
    for i in range(8):uc.reg_write(globals()['UC_ARM64_REG_Q'+str(i)],0xdead000+i)
    uc.reg_write(UC_ARM64_REG_X0,ret);uc.reg_write(UC_ARM64_REG_X30,lr);uc.reg_write(UC_ARM64_REG_PC,lr)
   u.hook_add(UC_HOOK_CODE,mock);u.emu_start(h['site']+bias,0,count=6000);assert exited,(name,key)
   expected=before[:];expected_sp=sp
   if name=='soccer_and_parole_pulses':
    assert exited==[old]
    if key=='NativeSoccerSync'and success:
     valid=kind==6 and athletekind==2 and sport==5 and not missing
     cup=1 if 1<=rank<=4 else 2 if rank==5 else 3 if rank==6 else 0
     assert writes==dict(Playing=int(valid),LeagueRank=rank if valid else 0,TeamIndex=123 if valid else-1,QualifiedCup=cup if valid else 0),writes
    elif key=='NativeCupRoll'and success:assert writes=={'Roll':max(0,min(99,roll))}
    elif key=='NativeParoleSync'and success and not missing:assert writes==dict(Remaining=max(0,min(5,end-age)),Active=int(end>age and kind!=4))
    else:assert not writes
   elif name=='successful_parole_house_arrest':
    expected[8]=game
    if not missing:
     duration=max(3,min(5,roll));assert writes==dict(StartAge=age,EndAge=age+duration,SentenceYears=duration,Remaining=duration,Active=1,Sessions=0,LastCheckAge=-1,Releases=3),writes
    else:assert not writes
   else:
    blocked=choice>=0 and end>age and not missing
    assert exited==[sentinel-bias if blocked else h['resume']]
    assert bool([a for v,a in calls if v==0x30838cc])==blocked and not writes
    if not blocked:expected_sp-=abs(int(__import__('re').search(r'-?0x[0-9a-f]+',h['original'])[0],16))
   assert [u.reg_read(globals()['UC_ARM64_REG_X'+str(i)])for i in range(31)]==expected,(name,'register corruption')
   assert u.reg_read(UC_ARM64_REG_SP)==expected_sp
   assert [u.reg_read(globals()['UC_ARM64_REG_Q'+str(i)])for i in range(8)]==qb
   checks+=1
  for rank in range(10):case('soccer_and_parole_pulses',rank=rank)
  for kind in range(8):case('soccer_and_parole_pulses',kind=kind)
  for sport in range(9):case('soccer_and_parole_pulses',sport=sport)
  case('soccer_and_parole_pulses',athletekind=1)
  case('soccer_and_parole_pulses',success=0);case('soccer_and_parole_pulses',missing=True);case('soccer_and_parole_pulses',key='NativeMilitarySync')
  for roll in [-100,0,50,99,100]:case('soccer_and_parole_pulses',key='NativeCupRoll',roll=roll)
  for kind in [0,2,4,6]:
   for end in [0,29,30,31,35]:case('soccer_and_parole_pulses',key='NativeParoleSync',kind=kind,end=end)
  for roll in [3,4,5,6,-100]:case('successful_parole_house_arrest',roll=roll)
  case('successful_parole_house_arrest',missing=True)
  for h in details['hooks'][2:]:
   for end in [0,29,30,31,35]:
    for choice in [-1,0,1,2,3]:case(h['name'],end=end,choice=choice)
   case(h['name'],end=35,missing=True)
 result=dict(instruction_cases=checks,load_addresses=2,device_runtime_tested=False)
 (ROOT/'native_validation.json').write_text(json.dumps(result,indent=2));return result
