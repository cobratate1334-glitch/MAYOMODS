"""Run all new ARM64 bridges at two load bases with volatile-clobbering engine calls."""
import io,json,re,struct,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
ROOT=Path(__file__).resolve().parent
def validate(binary,d,packbytes):
 loads=[s for s in ELFFile(io.BytesIO(binary)).iter_segments()if s['p_type']=='PT_LOAD'];checks=0
 def read(va,n):
  s=next(s for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']);o=s['p_offset']+va-s['p_vaddr'];return binary[o:o+n]
 for bias in [0,0x1000000000]:
  def case(name,key='NativeGovernmentSync',kind=6,special=1,office=4,country='us',nativeapproval=63,impact=1,success=1,filedata=packbytes,index=None,ints=None,texts=None,missing=False):
   nonlocal checks
   h=next(h for h in d['hooks']if h['name']==name);u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);mapped=set();heap=0x7000000000
   def mapat(a,n):
    for p in range(a&~4095,(a+n+4095)&~4095,4096):
     if p not in mapped:u.mem_map(p,4096);mapped.add(p)
   def q(a,v):u.mem_write(a,struct.pack('<Q',v))
   def w(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
   mapat(d['segment_va']+bias,d['segment_size']);u.mem_write(d['segment_va']+bias,binary[d['segment_offset']:d['segment_offset']+d['segment_size']]);mapat(heap,0x90000);mapat(0x5c23c90+bias,8)
   slot,klass,statics,game,life,hero,occ,politician,bp,owner,gov,obj,place=[heap+i*0x500 for i in range(13)]
   q(0x5c23c90+bias,slot);q(slot,klass);q(klass+0xb8,statics);q(statics,game);q(game+0x20,life);q(game+0x28,hero);w(hero+0x20,30);q(life+0x138,occ);w(occ+0x10,kind);q(occ+0x28,politician);w(politician+0x10,special);w(politician+0x20,office)
   if missing:q(game+0x20,0)
   nxt=heap+0x10000
   def managed(t):
    nonlocal nxt
    p=nxt;nxt+=0x200;encoded=t.encode('utf-16-le');w(p+0x10,len(encoded)//2);u.mem_write(p+0x14,encoded);return p
   def st(p):return bytes(u.mem_read(p+0x14,struct.unpack('<I',u.mem_read(p+0x10,4))[0]*2)).decode('utf-16-le')
   def signed(x):return struct.unpack('<i',struct.pack('<I',x&0xffffffff))[0]
   q(bp+0x18,managed(key));stock=managed('Original team');q(obj+0x10,stock);q(obj+0x20,stock)
   offset=0x20 if name in ['team_display_name','team_saved_name']else 0x10
   w(obj+offset,index if index is not None else(5000 if name=='league_database_name'else 5001))
   gotcalls={};mockaddr=heap+0x70000
   for j,(k,va)in enumerate(d['got'].items()):mapat(va+bias,8);q(va+bias,mockaddr+j*0x100);gotcalls[mockaddr+j*0x100]=k
   original=int(re.search(r'0x[0-9a-f]+',h['original'])[0],16)if name=='government_and_pack_pulses'else h['resume']
   sentinel=heap+0x80000;exits=[original+bias,sentinel]
   callees=[0x223e8cc,0x3059ee0,0x3059f90,0x3059934,0x3059d08,0x2c1ffa8,0x2c1c4e0,0x2a27250,0x2c21704,0x32800fc]
   for a in [h['site']]+callees:mapat(a+bias,4)
   for a in exits:mapat(a,4)
   u.mem_write(h['site']+bias,read(h['site'],4));sp=heap+0x8ff00
   for i in range(31):u.reg_write(globals()['UC_ARM64_REG_X'+str(i)],0x550000+i)
   for i in range(8):u.reg_write(globals()['UC_ARM64_REG_Q'+str(i)],(0xabcdef<<80)+i)
   u.reg_write(UC_ARM64_REG_SP,sp);u.reg_write(UC_ARM64_REG_X30,sentinel)
   if name=='government_and_pack_pulses':u.reg_write(UC_ARM64_REG_X19,bp);u.reg_write(UC_ARM64_REG_X21,owner);u.reg_write(UC_ARM64_REG_W20,impact&0xffffffff);u.reg_write(UC_ARM64_REG_W0,success)
   else:u.reg_write(UC_ARM64_REG_X0,obj)
   before=[u.reg_read(globals()['UC_ARM64_REG_X'+str(i)])for i in range(31)];qb=[u.reg_read(globals()['UC_ARM64_REG_Q'+str(i)])for i in range(8)]
   values=dict(ints or {});strings=dict(texts or {});writes={};effects=[];ended=[];pos=0;opened=0;closed=0
   def mock(uc,pc,size,_):
    nonlocal pos,opened,closed
    if pc in exits:ended.append(pc);uc.emu_stop();return
    va=pc-bias
    if va not in callees and pc not in gotcalls:return
    a=[uc.reg_read(globals()['UC_ARM64_REG_X'+str(i)])for i in range(5)];ret=0
    if pc in gotcalls:
     which=gotcalls[pc]
     if which=='fopen':
      assert bytes(uc.mem_read(a[0],100)).split(b'\0')[0].decode()=='/data/data/com.candywriter.bitlife/files/namepack-active.bin'
      ret=0 if filedata is None else heap+0x60000;opened+=int(ret!=0);pos=0
     elif which=='fclose':closed+=1;ret=0
     elif which=='fseek':pos=a[1];ret=0
     else:
      assert a[1]==1;chunk=filedata[pos:pos+a[2]];uc.mem_write(a[0],chunk);pos+=len(chunk);ret=len(chunk)
    elif va==0x223e8cc:ret=managed(bytes(uc.mem_read(a[0],256)).split(b'\0')[0].decode())
    elif va==0x3059ee0:ret=({'WarOpponent':5,'WarProgress':35}if a[0]==gov else values).get(st(a[1]),signed(a[2]))
    elif va==0x3059f90:assert a[0]==owner and a[3]==0;writes[st(a[1])]=signed(a[2]);values[st(a[1])]=signed(a[2]);ret=1
    elif va==0x3059934:
     value=strings.get(st(a[1]));ret=managed(value)if value is not None else 0
    elif va==0x3059d08:assert a[0]==owner and a[3]==0;strings[st(a[1])]=st(a[2])
    elif va==0x2c1ffa8:assert a[0]==politician and a[1]==0;ret=nativeapproval&0xffffffff
    elif va==0x2c1c4e0:assert a[0]==politician;ret=place
    elif va==0x2a27250:assert a[0]==place;ret=managed(country)
    elif va==0x2c21704:assert a[0]==politician and a[2]==0;effects.append(signed(a[1]))
    elif va==0x32800fc:assert a[0]==life and st(a[1])=='government_v13'and a[2:4]==[30,0];ret=gov
    lr=uc.reg_read(UC_ARM64_REG_X30)
    for i in range(18):uc.reg_write(globals()['UC_ARM64_REG_X'+str(i)],0xdead000+i)
    for i in range(8):uc.reg_write(globals()['UC_ARM64_REG_Q'+str(i)],0xdead000+i)
    uc.reg_write(UC_ARM64_REG_X0,ret&0xffffffffffffffff);uc.reg_write(UC_ARM64_REG_X30,lr);uc.reg_write(UC_ARM64_REG_PC,lr)
   u.hook_add(UC_HOOK_CODE,mock);u.emu_start(h['site']+bias,0,count=60000);assert ended,(name,key);assert opened==closed,(opened,closed)
   after=[u.reg_read(globals()['UC_ARM64_REG_X'+str(i)])for i in range(31)];expected=before[:];expected_sp=sp
   valid=kind==6 and special==1 and office==4 and not missing
   if name=='government_and_pack_pulses':
    assert ended==[original+bias]and after==expected
    if success and key=='NativeGovernmentSync':
     ci=next((i for i,x in enumerate(d['countries'])if x['code']==country),-1)
     assert writes==dict(President=int(valid),HomeCountry=ci if valid else-1,NativeApproval=max(0,min(100,nativeapproval))if valid else 0,Office=office if kind==6 and special==1 and not missing else 0),writes
    elif success and key=='NativeGovApproval':assert effects==([impact]if valid and -3<=impact<=3 else[])
    elif success and key=='NativeWarSync'and not missing:assert writes=={'WarOpponent':5,'WarProgress':35}
    elif key!='NativePackNames' or not success:assert not writes
   else:
    if ended==[sentinel]:assert st(after[0]) in ['Harbour FC','National Soccer League'];expected[0]=after[0]
    else:
     if name=='team_display_name':expected_sp-=32
     elif name=='team_saved_name':expected[0]=stock
     else:expected[0]=stock
    assert after==expected,(name,'registers')
   assert u.reg_read(UC_ARM64_REG_SP)==expected_sp;assert[u.reg_read(globals()['UC_ARM64_REG_Q'+str(i)])for i in range(8)]==qb
   checks+=1;return strings,values,ended
  for n in ['team_display_name','team_database_name','league_database_name']:
   case(n);case(n,filedata=None);case(n,filedata=b'broken');case(n,filedata=packbytes[:50]);case(n,index=9999);case(n,index=0);case(n,index=-1)
  for country in d['countries']:case('government_and_pack_pulses',country=country['code'])
  for kind in range(8):case('government_and_pack_pulses',kind=kind)
  for office in range(1,5):case('government_and_pack_pulses',office=office)
  for a in [-100,0,100,1000]:case('government_and_pack_pulses',nativeapproval=a)
  case('government_and_pack_pulses',special=2);case('government_and_pack_pulses',missing=True);case('government_and_pack_pulses',country='xx');case('government_and_pack_pulses',success=0)
  for i in range(-4,5):case('government_and_pack_pulses',key='NativeGovApproval',impact=i)
  case('government_and_pack_pulses',key='NativeGovApproval',office=3);case('government_and_pack_pulses',key='NativeWarSync');case('government_and_pack_pulses',key='NativeWarSync',missing=True);case('government_and_pack_pulses',key='NativeSoccerSync')
  states=dict(Cup=1,TeamIndex=5001,CurrentOpponentID=1,T1ID=1,T2ID=2,T3ID=3)
  names=dict(TeamName='London Wanderers',Opponent='Base opponent',T1Name='Base first',T2Name='Base second',T3Name='Base third')
  result,_,_=case('government_and_pack_pulses',key='NativePackNames',ints=states,texts=names)
  assert result['TeamName']=='Harbour FC'and result['CupName1']=='Continental Champions'and result['OriginalTeamName']=='London Wanderers'
  restored,_,_=case('government_and_pack_pulses',key='NativePackNames',ints=states,texts=result,filedata=None)
  assert restored['TeamName']=='London Wanderers'and restored['CupName1']=='Champions League'and restored['Competition']=='Champions League'
  world,_,_=case('government_and_pack_pulses',key='NativePackNames',ints=dict(states,Cup=4),texts=dict(names,TeamName='Brazil'))
  assert world['TeamName']=='Brazil'and world['Competition']=='Nations World Cup'
 result=dict(instruction_cases=checks,load_addresses=2,volatile_registers_clobbered=True,file_descriptors_closed=True,device_runtime_tested=False)
 (ROOT/'native_validation.json').write_text(json.dumps(result,indent=2));print(result);return result
if __name__=='__main__':validate(Path(sys.argv[1]).read_bytes(),json.load(open(ROOT/'native_hooks.json')),Path(sys.argv[2]).read_bytes())
