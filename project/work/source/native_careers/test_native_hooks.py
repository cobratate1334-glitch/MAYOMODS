"""Execute the patched instructions; model existing native callees at their ABI.

This verifies branches, pointer checks, ASLR and register preservation. It is
not a substitute for a phone test of the existing Unity/native callees.
"""
import io,json,struct,zipfile,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
from native_hooks import patch
ROOT=Path(__file__).resolve().parent
def validate(binary,details):
 elf=ELFFile(io.BytesIO(binary));loads=[s for s in elf.iter_segments()if s['p_type']=='PT_LOAD'];checks=0
 def read(va,size):
  seg=next(s for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']);p=seg['p_offset']+va-seg['p_vaddr'];return binary[p:p+size]
 for bias in (0,0x1000000000):
  def case(name,key='',kind=2,score=1,success=1,missing='',expected='Podcast Producer',actual='Podcast Producer',blocked=False):
   nonlocal checks
   h=next(x for x in details['hooks']if x['name']==name)
   u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);mapped=set()
   def map_at(address,size):
    for p in range(address&~4095,(address+size+4095)&~4095,4096):
     if p not in mapped:u.mem_map(p,4096);mapped.add(p)
   def put(address,value):u.mem_write(address,struct.pack('<Q',value))
   def put32(address,value):u.mem_write(address,struct.pack('<I',value&0xffffffff))
   map_at(details['segment_va']+bias,details['segment_size']);u.mem_write(details['segment_va']+bias,binary[details['segment_offset']:details['segment_offset']+details['segment_size']])
   for va in [h['site'],h['resume']]:map_at(va+bias,4);u.mem_write(va+bias,read(va,4))
   callees=[0x30611d0,0x223e8cc,0x2b6ae5c,0x2b6cb40,0x3059f90,0x27fb07c,0x2a6ffcc,0x2c38288,0x2a27280,0x2236f1c,0x2237158,0x2b1e454,0x2b1e28c,0x2a2cfac,0x2a7e098,0x3059934]
   for va in callees:map_at(va+bias,4)
   map_at(0x5c23c90+bias,8);map_at(0x5c370d0+bias,8)
   heap=0x7000000000;map_at(heap,0x20000)
   slot,klass,static,game,life,occ,job,owner,bp,hero,place,country,career,newjob,company,jclassslot,jclass=[heap+i*0x500 for i in range(17)]
   put(0x5c23c90+bias,slot);put(slot,klass);put(klass+0xb8,static);put(static,game);put(game+0x20,life);put(game+0x28,hero);put(life+0x138,occ)
   put32(occ+0x10,kind);put(occ+0x40,job);put32(occ+0x3c,7);u.mem_write(occ+0x98,struct.pack('<f',73.5));put32(career+0x18,12)
   put(0x5c370d0+bias,jclassslot);put(jclassslot,jclass)
   stringnext=heap+0x9000
   def managed(text):
    nonlocal stringnext
    p=stringnext;stringnext+=0x200;put32(p+0x10,len(text));u.mem_write(p+0x14,text.encode('utf-16-le'));return p
   def getstring(p):
    if not p:return None
    length=struct.unpack('<I',u.mem_read(p+0x10,4))[0];return bytes(u.mem_read(p+0x14,length*2)).decode('utf-16-le')
   put(job+0x18,managed(actual));put(bp+0x18,managed(key));expectedptr=managed(expected)
   chain={'slot':0x5c23c90+bias,'class':slot,'statics':klass+0xb8,'game':static,'life':game+0x20,'occupation':life+0x138,'job':occ+0x40,'name':job+0x18,'hero':game+0x28,'job_class_slot':0x5c370d0+bias,'job_class':jclassslot}
   if missing in chain:put(chain[missing],0)
   sp=heap+0x1ff00
   for i in range(31):u.reg_write(globals()['UC_ARM64_REG_X'+str(i)],0x550000+i)
   for i in range(8):u.reg_write(globals()['UC_ARM64_REG_Q'+str(i)],(0xabcde<<80)+i)
   u.reg_write(UC_ARM64_REG_SP,sp);u.reg_write(UC_ARM64_REG_X29,heap+0x8500);put(heap+0x8500,0x88887777)
   if name=='job_menu':u.reg_write(UC_ARM64_REG_X19,heap+0x8200)
   elif name=='special_careers':u.reg_write(UC_ARM64_REG_X21,heap+0x8200)
   elif name=='prison_menu':u.reg_write(UC_ARM64_REG_X19,heap+0x8200)
   else:
    u.reg_write(UC_ARM64_REG_X19,bp);u.reg_write(UC_ARM64_REG_X21,owner);u.reg_write(UC_ARM64_REG_W20,score&0xffffffff);u.reg_write(UC_ARM64_REG_W0,success)
    put(sp+0x20,0x12340020);put(sp+0x28,0x12340019)
   before=[u.reg_read(globals()['UC_ARM64_REG_X'+str(i)])for i in range(31)];vectors=[u.reg_read(globals()['UC_ARM64_REG_Q'+str(i)])for i in range(8)];calls=[];writes=[];exited=[]
   def mock(uc,pc,size,userdata):
    va=pc-bias
    if va==h['resume']:exited.append(va);uc.emu_stop();return
    if va not in callees:return
    args=[uc.reg_read(globals()['UC_ARM64_REG_X'+str(i)])for i in range(4)];calls.append((va,args))
    ret=0
    if va==0x223e8cc:
     a=args[0];raw=bytes(uc.mem_read(a,64)).split(b'\0',1)[0];ret=managed(raw.decode())
    elif va==0x30611d0:assert args[0]==heap+0x8200 and args[2]==0
    elif va in (0x2b6ae5c,0x2b6cb40):assert args[0]==occ and args[1]&0xffffffff==score&0xffffffff and args[2]==0
    elif va==0x3059f90:
     assert args[0]==owner and args[3]==0;writes.append((getstring(args[1]),args[2]&0xffffffff));ret=1
    elif va==0x3059934:assert args[0]==owner and getstring(args[1])=='ExpectedCareer';ret=expectedptr
    elif va==0x27fb07c:
     assert getstring(args[0])==('F1 Driver'if key=='NativeHireF1'else'Reality TV Host')and args[1]==0;ret=0 if missing=='career'else career
    elif va==0x2a6ffcc:assert args[0]==hero;ret=int(blocked)
    elif va==0x2c38288:assert args[0]==hero;ret=0 if missing=='place'else place
    elif va==0x2a27280:assert args[0]==place;ret=0 if missing=='country'else country
    elif va==0x2236f1c:assert args[0]==jclassslot
    elif va==0x2237158:assert args[0]==jclass;ret=0 if missing=='allocation'else newjob
    elif va==0x2b1e454:assert args[:3]==[newjob,country,0]
    elif va==0x2b1e28c:assert args[:3]==[newjob,career,0]
    elif va==0x2a2cfac:assert args[:3]==[place,12,0];ret=0 if missing=='company'else company
    elif va==0x2a7e098:assert args[:3]==[hero,newjob,0]and struct.unpack('<Q',uc.mem_read(newjob+0x28,8))[0]==company
    lr=uc.reg_read(UC_ARM64_REG_X30)
    # AAPCS64 caller-saved registers deliberately clobbered by each callee.
    for i in range(18):uc.reg_write(globals()['UC_ARM64_REG_X'+str(i)],0xdead000+i)
    for i in range(8):uc.reg_write(globals()['UC_ARM64_REG_Q'+str(i)],0xdead000+i)
    uc.reg_write(UC_ARM64_REG_X0,ret);uc.reg_write(UC_ARM64_REG_X30,lr);uc.reg_write(UC_ARM64_REG_PC,lr)
   u.hook_add(UC_HOOK_CODE,mock);u.emu_start(h['site']+bias,0,count=2000)
   assert exited==[h['resume']],'trampoline did not resume'
   after=[u.reg_read(globals()['UC_ARM64_REG_X'+str(i)])for i in range(31)]
   expectedregs=before[:]
   if name in ('job_menu','special_careers'):expectedregs[8]=0x5c24000+bias
   elif name=='prison_menu':expectedregs[0]=0x88887777
   else:expectedregs[20]=0x12340020;expectedregs[19]=0x12340019
   assert after==expectedregs,(name,'register corruption')
   assert u.reg_read(UC_ARM64_REG_SP)==sp and vectors==[u.reg_read(globals()['UC_ARM64_REG_Q'+str(i)])for i in range(8)]
   if name in ('special_careers','prison_menu'):
    assert getstring(next(a for va,a in calls if va==0x30611d0)[1])==('Prison'if name=='prison_menu'else'SpecialCareers')
   elif name=='job_menu':
    injections=[a for va,a in calls if va==0x30611d0];assert bool(injections)==(kind==2 and not missing)
    if injections:assert getstring(injections[0][1])==actual
   elif success!=1 or key=='UnrelatedProperty':assert not calls
   elif key=='NativeWorkImpact':assert len(calls)==int(kind==2 and -3<=score<=3 and not missing)
   elif key=='NativePrisonConduct':assert len(calls)==int(kind==4 and -3<=score<=3 and not missing)
   elif key=='NativePrisonSync':assert writes==([('YearsRemaining',7),('NativeBehavior',73)]if kind==4 and not missing else[])
   elif key=='NativeCareerSync':assert writes==[('Active',int(kind==2 and not missing and actual==expected))]
   elif key in ('NativeHireF1','NativeHireTV'):
    hired=any(va==0x2a7e098 for va,a in calls);assert hired==(not missing and not blocked)
    assert writes==([('NativeHireResult',1),('Active',1)]if hired else[])
   checks+=1
  for name in ('special_careers','prison_menu'):case(name)
  for kind in (0,2,4):case('job_menu',kind=kind)
  for missing in ('slot','class','statics','game','life','occupation','job','name'):case('job_menu',missing=missing)
  for key,kind in [('NativeWorkImpact',2),('NativePrisonConduct',4)]:
   for score in (-4,-3,-1,0,1,3,4):case('native_stat_bridge',key,kind,score)
   for kind2 in (0,2,4):case('native_stat_bridge',key,kind2)
   case('native_stat_bridge',key,kind,success=0)
   for missing in ('slot','class','statics','game','life','occupation'):case('native_stat_bridge',key,kind,missing=missing)
  for kind in (0,2,4):case('native_stat_bridge','NativePrisonSync',kind)
  for missing in ('slot','class','statics','game','life','occupation'):case('native_stat_bridge','NativePrisonSync',4,missing=missing)
  for kind in (0,2,4):
   for actual in ('Podcast Producer','Different Job'):case('native_stat_bridge','NativeCareerSync',kind,actual=actual)
  for missing in ('slot','class','statics','game','life','occupation','job','name'):case('native_stat_bridge','NativeCareerSync',missing=missing)
  case('native_stat_bridge','UnrelatedProperty');case('native_stat_bridge','NativeHireF1',success=0)
  for key in ('NativeHireF1','NativeHireTV'):
   case('native_stat_bridge',key);case('native_stat_bridge',key,blocked=True)
   for missing in ('career','slot','class','statics','game','hero','place','country','job_class_slot','job_class','allocation','company'):case('native_stat_bridge',key,missing=missing)
 return dict(status='passed',instruction_emulation_cases=checks,aslr_biases=['0','0x1000000000'],android_runtime_tested=False)
if __name__=='__main__':
 with zipfile.ZipFile(sys.argv[1])as z:native=z.read('lib/arm64-v8a/libil2cpp.so')
 binary,details=patch(native);result=validate(binary,details);(ROOT/'native_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
