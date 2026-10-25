"""Actual ARM64 tests with clobbered caller registers, ASLR and saved state."""
import io,json,struct,re,hashlib,random
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm64_const import *
ROOT=Path(__file__).resolve().parent
X=[globals()['UC_ARM64_REG_X'+str(i)]for i in range(31)];Q=[globals()['UC_ARM64_REG_Q'+str(i)]for i in range(8)]
def validate(binary,d,rocket,rd):
 checks=0;rand=random.Random(15)
 cached_loads={}
 for blob in (binary,rocket):
  elf=ELFFile(io.BytesIO(blob));cached_loads[id(blob)]=[dict(s.header) for s in elf.iter_segments()if s['p_type']=='PT_LOAD']
 def run(binary,d,name,values={},key='',owner='soccer_v12',id_='',kind=0,feedback=None,shown=True,bias=0):
  loads=cached_loads[id(binary)];h=next((v for v in d.get('hooks',[])if v['name']==name),d);u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);mapped=set();heap=0x7000000000;nextptr=heap+0x10000;v=dict(values);calls=[];exits=[];links=[]
  def mapat(a,n):
   for p in range(a&~4095,(a+n+4095)&~4095,4096):
    if p not in mapped:u.mem_map(p,4096);mapped.add(p)
  def putq(a,v):u.mem_write(a,struct.pack('<Q',v))
  def putw(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def rq(a):return struct.unpack('<Q',u.mem_read(a,8))[0]
  def rw(a):return struct.unpack('<I',u.mem_read(a,4))[0]
  def managed(t):
   nonlocal nextptr
   p=nextptr;nextptr+=max(512,len(t)*2+80);putw(p+16,len(t));u.mem_write(p+20,t.encode('utf-16-le'));return p
  def st(p):return bytes(u.mem_read(p+20,rw(p+16)*2)).decode('utf-16-le')if p else''
  def load(va,n):
   s=next(s for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']);p=s['p_offset']+va-s['p_vaddr'];return binary[p:p+n]
  mapat(d['segment_va']+bias,d['segment_size']);u.mem_write(d['segment_va']+bias,binary[d['segment_offset']:d['segment_offset']+d['segment_size']]);mapat(heap,0x300000);mapat(0x6306200+bias,32);mapat(0x5c24320+bias,8)
  state=0x6306200+bias;bp=heap;own=heap+0x500;manager=heap+0x1000;iterator=heap+0x1500;listobj=heap+0x2000;listklass=heap+0x2500;slot=heap+0x3000;type_=heap+0x3500
  putq(bp+24,managed(key));putq(own+16,managed(owner));putq(state,manager);putq(0x5c24320+bias,slot);putq(slot,type_);putq(listobj,listklass);putq(listklass+0x308,0x4edbadd+bias);putq(listklass+0x310,heap+0x4000)
  if feedback:putq(state+8,iterator if feedback['ours']else iterator+64);putw(state+16,feedback['pending']);putw(iterator+16,-1)
  apis=[0x223e8cc,0x3059ee0,0x3059f90,0x2f8abe0,0x5577470,0x2236f1c,0x2237158,0x4edba28,0x2f2c750,0x4edbadd,0x1b2d70,0x1b2d90]
  branch=int(re.search(r'0x[0-9a-f]+',h.get('original',''))[0],16)if h.get('original','').startswith('b ')else None
  ends=[h['resume']]+([branch]if branch else[])+[0xf0000000]
  for va in apis+ends+[h['site']]:mapat(va+bias,4)
  u.mem_write(h['site']+bias,load(h['site'],4));sp=heap+0x2fff00
  for i,r in enumerate(X):u.reg_write(r,0xaabb00+i)
  for i,r in enumerate(Q):u.reg_write(r,0xdef000+i)
  u.reg_write(UC_ARM64_REG_SP,sp);u.reg_write(UC_ARM64_REG_X30,0xf0000000+bias)
  if name=='v15_saved_activity_pulses':u.reg_write(X[19],bp);u.reg_write(X[21],own);u.reg_write(X[0],1)
  elif name=='remember_scenario_manager':u.reg_write(X[0],manager)
  elif name=='scoring_feedback_queue':u.reg_write(X[19],iterator)
  elif name=='custom_hair_evolution':u.reg_write(X[0],managed(id_));u.reg_write(X[1],kind)
  elif name=='logo':u.reg_write(X[19],own);u.reg_write(X[23],heap+0x4567)
  before=[u.reg_read(r)for r in X];qbefore=[u.reg_read(r)for r in Q]
  def mock(uc,pc,size,data):
   va=pc-bias
   if va in ends:exits.append(va);uc.emu_stop();return
   if va not in apis:return
   a=[uc.reg_read(r)for r in X[:4]];calls.append((va,a));result=0
   if va==0x223e8cc:result=managed(bytes(uc.mem_read(a[0],512)).split(b'\0')[0].decode())
   elif va==0x3059ee0:assert a[0]==own and a[3]==0;result=v.get(st(a[1]),a[2])
   elif va==0x3059f90:assert a[0]==own and a[3]==0;v[st(a[1])]=a[2]&0xffffffff;result=1
   elif va==0x2f8abe0:assert a[:4]==[manager,1,1,0];result=iterator
   elif va==0x5577470:assert a[:3]==[manager,iterator,0]
   elif va==0x2236f1c:assert a[0]==slot
   elif va==0x2237158:assert a[0]==type_;result=listobj
   elif va==0x4edba28:assert a[:2]==[listobj,0]
   elif va==0x2f2c750:links.append((st(a[0]),a[1]));result=heap+0x5000
   elif va==0x4edbadd:assert a[:3]==[listobj,heap+0x5000,heap+0x4000]
   elif va==0x1b2d70:assert bytes(uc.mem_read(a[0],100)).split(b'\0')[0].decode()==rd['marker'];result=0 if shown else heap+0x6000
   elif va==0x1b2d90:assert a[0]==heap+0x6000
   lr=uc.reg_read(X[30])
   for i in range(18):uc.reg_write(X[i],0xdead00+i)
   for i in range(8):uc.reg_write(Q[i],0xdead00+i)
   uc.reg_write(X[0],result);uc.reg_write(X[30],lr);uc.reg_write(UC_ARM64_REG_PC,lr)
  hook=u.hook_add(UC_HOOK_CODE,mock);u.emu_start(h['site']+bias,0,count=200000);u.hook_del(hook);assert exits,(name,id_,key)
  expected=before[:]
  if name=='remember_scenario_manager':# Original prologue changes SP; verify payload and preserved registers before resumed body.
   assert rq(state)==manager
  elif name=='scoring_feedback_queue':expected[20]=1 if feedback['ours']and feedback['pending']else 0
  elif name=='custom_hair_evolution'and links:expected[0]=listobj
  elif name=='logo':expected[0]=own+12;expected[23]=before[23]if shown else 0
  assert [u.reg_read(r)for r in X]==expected,(name,'registers')
  assert [u.reg_read(r)for r in Q]==qbefore
  if name!='remember_scenario_manager':
   expected_sp=sp-0x30 if name=='custom_hair_evolution'and not links else sp
   assert u.reg_read(UC_ARM64_REG_SP)==expected_sp
  return v,calls,links,dict(iterator=rq(state+8),pending=rw(state+16),state=rw(iterator+16)),exits
 for bias in [0,0x1000000000]:
  run(binary,d,'remember_scenario_manager',bias=bias);checks+=1
  for _ in range(256):
   teams=[(rand.randint(0,9),rand.randint(0,20),rand.randint(0,20))for i in range(4)];values={'Stage':1,'Phase':rand.randint(11,14),'GroupRound':rand.randint(1,3)}
   for i,(p,f,a)in enumerate(teams):values.update({f'T{i}P':p,f'T{i}GF':f,f'T{i}GA':a})
   own=teams[0];rank=1+sum((p,f-a,f)>=(own[0],own[1]-own[2],own[1])for p,f,a in teams[1:]);v,_,_,_,_=run(binary,d,'v15_saved_activity_pulses',values,'NativeGroupRank',bias=bias);assert v['GroupRank']==rank and v['Phase']==14;checks+=1
  for stage,phase in [(0,0),(2,14),(1,10),(1,15)]:
   vs={'Stage':stage,'Phase':phase,'GroupRank':2};v,_,_,_,_=run(binary,d,'v15_saved_activity_pulses',vs,'NativeGroupRank',bias=bias);assert v==vs;checks+=1
  for owner,ks in d['scores'].items():
   for key in ks:
    for current,seen in [(0,0),(1,0),(3,1),(3,3),(0,3),(5,4)]:
     v,c,_,s,_=run(binary,d,'v15_saved_activity_pulses',{key:current,'V15Sound_'+key:seen},key,owner,bias=bias);assert v['V15Sound_'+key]==current;count=min(max(current-seen,0),24);assert len([x for x in c if x[0]==0x2f8abe0])==bool(count);assert s['pending']==max(count-1,0);checks+=1
  for ours in [True,False]:
   for pending in [0,1,5]:
    _,_,_,s,_=run(binary,d,'scoring_feedback_queue',feedback=dict(ours=ours,pending=pending),bias=bias);assert s['pending']==(max(0,pending-1)if ours else pending);assert s['state']==(0 if ours and pending else 0xffffffff);checks+=1
  for style in range(9):
   for gender in range(2):
    for stage in range(6):
     for kind in [0,1]:
      id_=98000+style*100+gender*10+stage;_,_,links,_,_=run(binary,d,'custom_hair_evolution',id_=str(id_),kind=kind,bias=bias);target=98000+style*100+gender*10+min(stage+1,5)if kind==0 else 98000+style*100+(1-gender)*10+stage;assert links==[(str(target),100)];checks+=1
  for id_ in ['00792','97999','98999','', '9800']:
   _,_,links,_,_=run(binary,d,'custom_hair_evolution',id_=id_,bias=bias);assert not links;checks+=1
  for shown in [True,False]:run(rocket,rd,'logo',shown=shown,bias=bias);checks+=1
 result=dict(arm64_cases=checks,aslr_biases=[0,0x1000000000],rank_calculation_actual_arm64=True,score_queue_actual_arm64=True,hair_evolution_actual_arm64=True,logo_visibility_actual_arm64=True,binary_sha256=hashlib.sha256(binary).hexdigest(),device_runtime_tested=False)
 (ROOT/'native_validation.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':print(validate(Path('analysis/patched15.so').read_bytes(),json.loads((ROOT/'native_hooks.json').read_text()),Path('analysis/rocket15.so').read_bytes(),json.loads((ROOT/'logo_validation.json').read_text())))
