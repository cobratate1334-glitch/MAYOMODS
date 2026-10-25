"""Execute v14 ARM64 bridges with adversarial caller-register clobbering."""
import io,json,struct,re
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
  def case(name,key='',values=None,operand=1,age=30,kind=6,specialkind=2,success=1,oldstage=0,missing=False,minorowner='music_studio'):
   nonlocal checks
   values=dict(values or {});h=next(x for x in details['hooks']if x['name']==name);u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);mapped=set();heap=0x7000000000
   def mapat(a,n):
    for p in range(a&~4095,(a+n+4095)&~4095,4096):
     if p not in mapped:u.mem_map(p,4096);mapped.add(p)
   def q(a,v):u.mem_write(a,struct.pack('<Q',v))
   def d(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
   mapat(details['segment_va']+bias,details['segment_size']);u.mem_write(details['segment_va']+bias,binary[details['segment_offset']:details['segment_offset']+details['segment_size']])
   mapat(heap,0x300000);mapat(0x5c23c90+bias,8)
   callees=[0x223e8cc,0x3059f90,0x3059ee0,0x3059d08,0x3059934,0x32800fc,0x308c384,0x30611d0,0x2bfa594,0x2bf6c7c,0x6329000,0x2b6ae5c]
   original_branch=int(re.search(r'0x[0-9a-f]+',h['original'])[0],16)if h['original'].startswith('b ')else None
   exits=[h['resume']]+([heap+0x7000]if name=='adult_nested_grey'else[])+([original_branch]if original_branch else[])
   for va in exits+callees+[h['site']]:mapat(va+bias,4)
   u.mem_write(h['site']+bias,read(h['site'],4))
   slot,klass,static,game,life,hero,occ,bp,owner,athlete,team,career,oldowner,family,item=[heap+i*0x500 for i in range(15)]
   q(0x5c23c90+bias,slot);q(slot,klass);q(klass+0xb8,static);q(static,game);q(game+0x20,life);q(game+0x28,hero);d(hero+0x20,age);q(life+0x138,occ);d(occ+0x10,kind);q(occ+0x28,athlete);d(athlete+0x10,specialkind);q(athlete+0x30,team);d(team+0x20,5115);d(athlete+0x28,4);q(athlete+0x20,family);q(occ+0x40,career);d(career+0x10,123)
   if missing:q(game+0x20,0)
   nxt=heap+0x10000
   def managed(t):
    nonlocal nxt
    p=nxt;nxt+=max(0x100,(len(t)*2+100+15)&~15);d(p+0x10,len(t));u.mem_write(p+0x14,t.encode('utf-16-le'));return p
   def st(p):
    if p==0:return ''
    n=struct.unpack('<I',u.mem_read(p+0x10,4))[0];return bytes(u.mem_read(p+0x14,n*2)).decode('utf-16-le')
   q(bp+0x18,managed(key));q(owner+0x10,managed(minorowner));sp=heap+0x2fff00
   for i in range(31):u.reg_write(globals()['UC_ARM64_REG_X'+str(i)],0x550000+i)
   for i in range(8):u.reg_write(globals()['UC_ARM64_REG_Q'+str(i)],(0xabcdef<<80)+i)
   u.reg_write(UC_ARM64_REG_SP,sp)
   if name=='adult_nested_grey':u.reg_write(UC_ARM64_REG_X30,heap+0x7000+bias);u.reg_write(UC_ARM64_REG_X1,managed('v14-adult'))
   if name=='v14_saved_activity_pulses':u.reg_write(UC_ARM64_REG_X19,bp);u.reg_write(UC_ARM64_REG_X21,owner);u.reg_write(UC_ARM64_REG_W20,operand);u.reg_write(UC_ARM64_REG_W0,success)
   elif name=='resolve_condition_tags':u.reg_write(UC_ARM64_REG_X19,managed('(<function:add:1:<function:add:2:3>> > <GFC.soccer_v12.Roll>)'));u.reg_write(UC_ARM64_REG_X20,life)
   elif name=='adult_entry_grey':u.reg_write(UC_ARM64_REG_X19,owner);u.reg_write(UC_ARM64_REG_X21,item);u.reg_write(UC_ARM64_REG_X20,1)
   else:u.reg_write(UC_ARM64_REG_X19,owner);u.reg_write(UC_ARM64_REG_X26,owner)
   before=[u.reg_read(globals()['UC_ARM64_REG_X'+str(i)])for i in range(31)];qb=[u.reg_read(globals()['UC_ARM64_REG_Q'+str(i)])for i in range(8)];calls=[];writes={};exited=[];oldwrites={};texts={}
   def mock(uc,pc,size,data):
    va=pc-bias
    if va in exits:exited.append(va);uc.emu_stop();return
    if va not in callees:return
    a=[uc.reg_read(globals()['UC_ARM64_REG_X'+str(i)])for i in range(5)];calls.append((va,a));ret=0
    if va==0x223e8cc:ret=managed(bytes(uc.mem_read(a[0],512)).split(b'\0')[0].decode())
    elif va==0x32800fc:assert a[0]==life and st(a[1])=='soccer_v11'and a[2]==age and a[3]==0;ret=oldowner
    elif va==0x3059ee0:
     assert a[0]in [owner,oldowner]and a[3]==0
     k=st(a[1]);ret=({'Stage':oldstage}|oldwrites).get(k,a[2])if a[0]==oldowner else values.get(k,a[2])
    elif va==0x3059f90:
     assert a[0]in [owner,oldowner]and a[3]==0
     v=struct.unpack('<i',struct.pack('<I',a[2]&0xffffffff))[0];k=st(a[1]);(oldwrites if a[0]==oldowner else writes)[k]=v
     if a[0]==owner:values[k]=v
     ret=1
    elif va==0x3059d08:assert a[0]==owner and a[3]==0;texts[st(a[1])]=st(a[2]);ret=1
    elif va==0x3059934:assert a[0]==owner and a[3]==0;ret=managed(texts.get(st(a[1]),''))
    elif va==0x308c384:assert st(a[0]).startswith('(<function:add:')and a[1]==life;ret=managed('(6 > 5)')
    elif va==0x30611d0:assert a[0]==owner and a[2]==0;assert st(a[1])in ['SportsPeople','MafiaOperations','MusicPeople','WorkplaceRoles']
    elif va==0x6329000:assert a[0]in [5115,5012,5999]and a[1]==0;ret=0
    elif va==0x2b6ae5c:assert a[0]==occ and a[2]==0;assert a[1]&0xffffffff== (2 if values['CompanyPerformance']>=65 else -1 if values['CompanyPerformance']<40 else 1)&0xffffffff
    elif va==0x2bfa594:assert a[0]==athlete and a[1]==operand and a[2]==0
    elif va==0x2bf6c7c:assert a[0]==family and a[1]==operand and a[2]==0
    lr=uc.reg_read(UC_ARM64_REG_X30)
    for i in range(18):uc.reg_write(globals()['UC_ARM64_REG_X'+str(i)],0xdead000+i)
    for i in range(8):uc.reg_write(globals()['UC_ARM64_REG_Q'+str(i)],0xdead000+i)
    uc.reg_write(UC_ARM64_REG_X0,ret);uc.reg_write(UC_ARM64_REG_X30,lr);uc.reg_write(UC_ARM64_REG_PC,lr)
   u.hook_add(UC_HOOK_CODE,mock);u.emu_start(h['site']+bias,0,count=100000);assert exited,(name,key,values)
   expected=before[:]
   if name=='resolve_condition_tags':expected[19]=u.reg_read(UC_ARM64_REG_X19);assert st(expected[19])=='(6 > 5)';expected[0]=expected[19]
   elif name=='adult_nested_grey':expected[0]=int(age>=18)
   elif name=='adult_entry_grey':assert u.mem_read(item+0xd0,1)==(b'\1'if age<18 and minorowner in ['music_studio','parole_v11']else b'\0')
   elif not original_branch:expected[8]=((h['site']+4)&~4095)+0x0 if h['original'].startswith('adrp x8')else expected[8]
   if h['original'].startswith('adrp x8'):expected[8]=0x5c24000+bias
   assert [u.reg_read(globals()['UC_ARM64_REG_X'+str(i)])for i in range(31)]==expected,(name,'register corruption')
   assert u.reg_read(UC_ARM64_REG_SP)==sp and [u.reg_read(globals()['UC_ARM64_REG_Q'+str(i)])for i in range(8)]==qb
   checks+=1;return values,writes,texts,oldwrites,calls
  case('resolve_condition_tags')
  for age in [0,17,18,30]:
   case('adult_nested_grey',age=age)
   for owner in ['music_studio','parole_v11','soccer_v12']:case('adult_entry_grey',age=age,minorowner=owner)
  for name in ['all_sports_people','mafia_operations_menu','music_people_menu','workplace_roles_menu']:case(name)
  name='v14_saved_activity_pulses'
  for cup in range(1,5):
   for own in [-1,0,62,63,64,65]:
    for seed in [0,65]:
     v,w,t,o,_=case(name,'NativeCupDraw',{'Cup':cup,'TeamPool':own,'TeamIndex':-1,'Lookup':seed,'T1ID':-1,'T2ID':-1,'T3ID':-1},operand=1)
     picked=[v['T'+str(i)+'ID']for i in range(1,4)];assert len(set(picked))==3 and own not in picked and v['Phase']==0 and v['Return']==0,(cup,own,seed,picked,v)
     assert all(0<=x<(63 if cup==4 else 66)for x in picked)
     v2,_,_,_,_=case(name,'NativeCupDraw',v|{'Lookup':seed},operand=2);assert v2['CurrentOpponentID']not in picked+[own]
  for roll in [0,1,2,50,97,99]:
   v,w,t,o,_=case(name,'NativeScoreDetails',{'LastFor':2,'LastAgainst':1,'Roll':roll});assert v.get('PlayerGoals',0)+v.get('TeammateGoals',0)+v.get('OpponentOwnGoals',0)==2
   assert v.get('OpponentGoals',0)+v.get('OwnGoals',0)==1
   v2,w2,_,_,_=case(name,'NativeScoreDetails',v);assert not w2
   v3,w3,_,_,_=case(name,'NativeScoreDetails',v,operand=0);assert all(v3[k]==0 for k in ['PlayerGoals','TeammateGoals','OpponentGoals','OwnGoals','OpponentOwnGoals'])
  for stage in range(8):
   v,w,t,o,_=case(name,'NativeCupCompletion',{'Stage':stage},oldstage=5);assert v['Stage']==(0 if stage==7 else stage);assert o==dict(Stage=0,Pending=0)
  for kind in range(8):
   for sk in [1,2,4]:
    _,w,_,_,_=case(name,'NativePeopleSync',kind=kind,specialkind=sk);assert w['Eligible']==int(kind==6 and sk==2)
    _,w,_,_,_=case(name,'NativeMafiaSync',kind=kind,specialkind=sk);assert w['Eligible']==int(kind==6 and sk==4)
    _,w,_,_,_=case(name,'NativeOfficeSync',kind=kind,specialkind=sk);assert w['Eligible']==int(kind==2)
  case(name,'NativeMafiaImpact',specialkind=4,operand=2)
  for perf in [0,39,40,64,65,100]:case(name,'NativeOfficeImpact',{'CompanyPerformance':perf},kind=2)
  for id_,logo in details['logo_by_id'].items():
   v,w,t,o,_=case(name,'NativeCupLabels',{'Cup':1,'TeamIndex':int(id_),'CurrentOpponentID':details['pool_ids'].index(int(id_)) if int(id_)in details['pool_ids']else-1});assert t['TeamFlag']=='v14-'+logo
  _,w,t,_,_=case(name,'NativeCupLabels',{'Cup':4});assert not t
  _,w,_,_,calls=case(name,'NativeScoreDetails',success=0);assert not w and not calls
 import hashlib
 result=dict(binary_sha256=hashlib.sha256(binary).hexdigest(),instruction_cases=checks,load_addresses=2,registers_preserved=True,device_runtime_tested=False);(ROOT/'native_validation.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':
 import sys
 print(validate(Path(sys.argv[1]).read_bytes(),json.loads((ROOT/'native_hooks.json').read_text())))
