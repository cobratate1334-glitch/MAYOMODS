"""Execute ARM64 v8 branches at two load addresses. Callees are ABI mocks.
Not an Android runtime or full game test.
"""
import io,json,struct
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
ROOT=Path(__file__).resolve().parent

def validate(binary,details):
 e=ELFFile(io.BytesIO(binary));loads=[s for s in e.iter_segments()if s['p_type']=='PT_LOAD'];checks=0
 def read(va,size):
  s=next(s for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']);p=s['p_offset']+va-s['p_vaddr'];return binary[p:p+size]
 for bias in (0,0x1000000000):
  def case(name,kind=2,age=18,key='',score=1,success=1,sport=5,school=930257,index=2,text='Offer peer support',missing=False):
   nonlocal checks
   h=next(x for x in details['hooks']if x['name']==name);u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);mapped=set();heap=0x7000000000
   def mapat(a,n):
    for p in range(a&~4095,(a+n+4095)&~4095,4096):
     if p not in mapped:u.mem_map(p,4096);mapped.add(p)
   def put(a,v):u.mem_write(a,struct.pack('<Q',v))
   def p32(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
   def get(a):return struct.unpack('<Q',u.mem_read(a,8))[0]
   mapat(details['segment_va']+bias,details['segment_size']);u.mem_write(details['segment_va']+bias,binary[details['segment_offset']:details['segment_offset']+details['segment_size']])
   mapat(heap,0x30000);mapat(0x5c23c90+bias,8)
   oldbridge=int(h['original'].split()[-1],16)if name=='stat_bridge_v8'else None
   callees=[0x223e8cc,0x30611d0,0x31542f0,0x2b6b318,0x2c21704,0x2bc2cd4,0x2bc2d7c,0x3059f90,0x2237158,0x2a1bcf0,0x2c48a44,0x2b6cb40,0x30838cc,0x4000100]
   exits=[h['resume'],0x4000200]+([oldbridge]if oldbridge else[])
   for va in callees+exits+[h['site']]:mapat(va+bias,4)
   u.mem_write(h['site']+bias,read(h['site'],4))
   slot,klass,static,game,life,hero,occ,job,skills,owner,bp,profile,inmate,choices,arr,choice,newchoice=[heap+i*0x500 for i in range(17)]
   put(0x5c23c90+bias,slot);put(slot,klass);put(klass+0xb8,static);put(static,game);put(game+0x20,life);put(game+0x28,hero);put(life+0x138,occ)
   p32(hero+0x20,age);p32(occ+0x10,kind);put(occ+0x28,job);p32(job+0x10,1 if key=='NativeApprovalImpact'else 2);put(job+0x60,skills)
   stringnext=heap+0x10000
   def managed(t):
    nonlocal stringnext
    p=stringnext;stringnext+=0x100;p32(p+0x10,len(t));u.mem_write(p+0x14,t.encode('utf-16-le'));return p
   def st(p):
    n=struct.unpack('<I',u.mem_read(p+0x10,4))[0];return bytes(u.mem_read(p+0x14,n*2)).decode('utf-16-le')
   put(bp+0x18,managed(key));put(profile+0x180,inmate);put(profile+0x170,occ);put(profile+0x108,choices)
   put(choices,klass);put(klass+0x308,0x4000100+bias);put(klass+0x310,0x123456);p32(choices+0x18,3);put(choices+0x10,arr)
   for i in range(3):put(arr+0x20+i*8,choice)
   put(choice,klass);put(choice+0x10,managed(text));put(heap+0x8200,0x88887777);p32(heap+0x8500+0x10,school)
   if missing:put(slot,0)
   sp=heap+0x2ff00
   for i in range(31):u.reg_write(globals()['UC_ARM64_REG_X'+str(i)],0x550000+i)
   for i in range(8):u.reg_write(globals()['UC_ARM64_REG_Q'+str(i)],(0xabcde<<80)+i)
   u.reg_write(UC_ARM64_REG_SP,sp);u.reg_write(UC_ARM64_REG_X30,0x4000200+bias)
   if name in ('military_menu','politics_menu','shopping_menu'):u.reg_write(UC_ARM64_REG_X19,choices)
   if name=='football_menu':u.reg_write(UC_ARM64_REG_X26,choices);u.reg_write(UC_ARM64_REG_X25,heap+0x8200)
   if name=='entry_gates':u.reg_write(UC_ARM64_REG_X0,choices);u.reg_write(UC_ARM64_REG_X1,managed(key))
   if name=='stat_bridge_v8':
    u.reg_write(UC_ARM64_REG_X19,bp);u.reg_write(UC_ARM64_REG_X21,owner);u.reg_write(UC_ARM64_REG_W20,score&0xffffffff);u.reg_write(UC_ARM64_REG_W0,success);put(sp+0x20,0xabc);put(sp+0x28,0xdef)
   if name=='school_icons':u.reg_write(UC_ARM64_REG_X0,heap+0x8500)
   if name=='inmate_choice_add':u.reg_write(UC_ARM64_REG_X19,profile);u.reg_write(UC_ARM64_REG_X20,choices);u.reg_write(UC_ARM64_REG_X24,heap+0x8200)
   if name=='inmate_choice_select':u.reg_write(UC_ARM64_REG_X0,profile);u.reg_write(UC_ARM64_REG_W1,index)
   before=[u.reg_read(globals()['UC_ARM64_REG_X'+str(i)])for i in range(31)];qbefore=[u.reg_read(globals()['UC_ARM64_REG_Q'+str(i)])for i in range(8)];calls=[];exited=[];entry_seen=False
   def mock(uc,pc,size,data):
    nonlocal entry_seen
    va=pc-bias
    if name=='entry_gates'and va==h['site']and not entry_seen:entry_seen=True;return
    if va in exits:exited.append(va);uc.emu_stop();return
    if va not in callees:return
    args=[uc.reg_read(globals()['UC_ARM64_REG_X'+str(i)])for i in range(5)];calls.append((va,args));ret=0
    if va==0x223e8cc:ret=managed(bytes(uc.mem_read(args[0],96)).split(b'\0')[0].decode())
    elif va==0x31542f0:ret=sport
    elif va==0x2237158:assert args[0]==klass;ret=newchoice
    elif va==0x2a1bcf0:assert args[:5]==[newchoice,args[1],0,1,0];assert st(args[1])=='Offer peer support';put(newchoice+0x10,args[1])
    elif va==0x4000100:assert args[:3]==[choices,newchoice,0x123456]
    lr=uc.reg_read(UC_ARM64_REG_X30)
    for i in range(18):uc.reg_write(globals()['UC_ARM64_REG_X'+str(i)],0xdead000+i)
    for i in range(8):uc.reg_write(globals()['UC_ARM64_REG_Q'+str(i)],0xdead000+i)
    uc.reg_write(UC_ARM64_REG_X0,ret);uc.reg_write(UC_ARM64_REG_X30,lr);uc.reg_write(UC_ARM64_REG_PC,lr)
   u.hook_add(UC_HOOK_CODE,mock);u.emu_start(h['site']+bias,0,count=3000);assert exited,'no return '+name
   expected=before[:];expectsp=sp;exitva=exited[0]
   if exitva==h['resume']:
    if name in ('military_menu','politics_menu','shopping_menu'):expected[8]=0x5c24000+bias
    if name=='football_menu' or name=='inmate_choice_add':expected[0]=0x88887777
    if name in ('school_icons','inmate_choice_select'):expectsp=sp-(0x20 if name=='school_icons'else 0x60)
    if name=='entry_gates':expectsp=sp-0xd0
    if name=='stat_bridge_v8':expected[20]=0xabc;expected[19]=0xdef
   elif name=='school_icons':expected[0]=next(a for v,a in calls if v==0x223e8cc)[0] # resolve managed result below
   after=[u.reg_read(globals()['UC_ARM64_REG_X'+str(i)])for i in range(31)]
   if name=='school_icons'and exitva!=h['resume']:
    assert st(after[0])==details['school_icons'][str(school)]if str(school)in details['school_icons']else st(after[0])==details['school_icons'][school]
    expected[0]=after[0]
   assert after==expected,(name,'register corruption',[(i,hex(a),hex(b))for i,(a,b)in enumerate(zip(after,expected))if a!=b])
   assert u.reg_read(UC_ARM64_REG_SP)==expectsp and [u.reg_read(globals()['UC_ARM64_REG_Q'+str(i)])for i in range(8)]==qbefore
   injections=[st(a[1])for v,a in calls if v==INJECT]
   if name in ('military_menu','politics_menu','shopping_menu'):assert injections==[{'military_menu':'Military','politics_menu':'Politics','shopping_menu':'Shopping'}[name]]
   if name=='football_menu':assert injections==(['Football']if sport==5 else[])
   if name=='entry_gates':
    assert (exitva==0x4000200)==(key=='SpecialCareers'and age<18 and not missing)
    assert injections==(['StudioOutsidePrison']if key=='T1'and kind!=4 and not missing else[])
   if name=='stat_bridge_v8':
    effects=[(v,a)for v,a in calls if v in (0x2b6b318,0x2c21704,0x2bc2cd4,0x2bc2d7c)]
    eligible=success==1 and not missing and -3<=score<=3 and((key=='NativeMilitaryImpact'and kind==3)or(key in ('NativeApprovalImpact','NativeFitnessImpact','NativeRespectImpact')and kind==6))
    assert len(effects)==int(eligible),(key,kind,score,calls)
    for v,a in effects:assert a[0]==(occ if key=='NativeMilitaryImpact'else job if key=='NativeApprovalImpact'else skills)and a[1]&0xffffffff==score&0xffffffff and a[2]==0
    writes=[a for v,a in calls if v==0x3059f90]
    if key in ('NativeHireF1','NativeHireTV')and age<18 and success==1 and not missing:assert len(writes)==1 and st(writes[0][1])=='NativeHireResult'and writes[0][2]==0 and exitva==h['resume']
    else:assert exitva==oldbridge
   if name=='inmate_choice_select':
    selected=index==2 and text=='Offer peer support'
    assert any(v==0x2c48a44 for v,a in calls)==selected
    assert exitva==(0x4000200 if selected else h['resume'])
    for v,a in calls:
     if v==0x2c48a44:assert a[:3]==[inmate,1,0]
     if v==0x2b6cb40:assert a[:3]==[occ,1,0]
     if v==0x30838cc:assert st(a[0])=='genesis_v8_inmate_support'and a[1:5]==[1,1,0,0]
   checks+=1
  for n in ('military_menu','politics_menu','shopping_menu','inmate_choice_add'):case(n)
  for sport in range(8):case('football_menu',sport=sport)
  for key in ('SpecialCareers','T1','UnrelatedMenu'):
   for age in (0,17,18,80):
    for kind in (0,2,4):case('entry_gates',key=key,age=age,kind=kind)
  for key in ('NativeMilitaryImpact','NativeApprovalImpact','NativeFitnessImpact','NativeRespectImpact','UnrelatedProperty'):
   for kind in (0,2,3,4,6):
    for score in (-4,-3,0,3,4):case('stat_bridge_v8',key=key,kind=kind,score=score)
   case('stat_bridge_v8',key=key,kind=6,missing=True);case('stat_bridge_v8',key=key,kind=6,success=0)
  for key in ('NativeHireF1','NativeHireTV'):
   for age in (0,17,18,70):case('stat_bridge_v8',key=key,age=age)
  for school in list(range(930257,930277))+[0,1,115,930256,930277]:case('school_icons',school=school)
  for index in (-1,0,1,2,3):
   for text in ('Offer peer support','Original action'):case('inmate_choice_select',index=index,text=text)
 result=dict(instruction_cases=checks,aslr_addresses=2,android_runtime_tested=False);(ROOT/'native_validation.json').write_text(json.dumps(result,indent=2)+'\n');return result
INJECT=0x30611d0
if __name__=='__main__':
 import sys
 b=Path(sys.argv[1]).read_bytes();d=json.loads((ROOT/'native_hooks.json').read_text());print(validate(b,d))
