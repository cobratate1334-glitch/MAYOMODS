"""Exercise custody, parole availability, yearly warrants and native route calls.

Native prison conduct instructions run unmodified. The arrest helper and
scene allocator are explicit mocks; this is not an Android/Unity UI test.
"""
import copy,csv,hashlib,io,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native_v40'));sys.path.insert(0,str(ROOT.parent/'native_v29'))
import test_native40 as previous
previous.test_native.ROOT=ROOT
from test_native40 import X,Q
from unicorn.arm64_const import UC_ARM64_REG_PC
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN

class Machine(previous.Machine):
 def __init__(self,raw,bias=0):
  super().__init__(raw,bias);self.extra|={0x2a788a8,0x2b6cf10,0x2b6b610};self.extra.remove(0x2b6cb40)
  for a in [0x2a788a8,0x2b6cf10,0x2b6b610]:self.map(a+bias,4)
  self.map(0x2b6cb40+bias,0xa8);self.u.mem_write(0x2b6cb40+bias,self.load(0x2b6cb40,0xa8));self.u.mem_write(0x60c2643+bias,b'\1')
  self.reject_arrest=False;self.life_sentence=False
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if getattr(self,'scene_boundary',None)==va:
   u.reg_write(X[0],0);self.stopped=True;u.emu_stop();return
  if va not in {0x2a788a8,0x2b6cf10,0x2b6b610}:return super().mock(u,pc,size,data)
  args=[u.reg_read(r)for r in X[:4]];lr=u.reg_read(X[30]);self.native_calls.append((va,args))
  if va==0x2a788a8:assert args[:3]==[self.hero,23,0];value=0 if self.reject_arrest else self.alloc()
  elif va==0x2b6cf10:assert args[:2]==[self.occ,0];value=int(self.life_sentence)
  else:assert args[:2]==[self.occ,0];value=self.country
  for i in range(18):u.reg_write(X[i],0xdead00+i)
  for i in range(8):u.reg_write(Q[i],0xfeed00+i)
  u.reg_write(X[0],value);u.reg_write(X[30],lr);u.reg_write(UC_ARM64_REG_PC,lr)
 def eligible_parole(self):
  r=next(r for r in self.d['routines']if r['name']=='parole_eligible41');return self.execute(r['stub'],self.exit,{},result=True)
 def scene41(self,key,owner='parole_v11'):
  self.q(self.bp+0x10,self.managed(owner));self.q(self.bp+0x18,self.managed(key));self.q(self.bp+0x20,self.managed('=1'));self.u.mem_write(self.bp+0x30,b'\1')
  r=next(r for r in self.d['hooks']if r['name']=='v41_native_parole_scenarios');self.scene_boundary=next(ins.address-4 for ins in Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(self.load(r['stub'],r['length']),r['stub'])if ins.mnemonic=='b'and int(ins.op_str[1:],16)==r['resume']);value=self.execute(r['stub'],self.exit,{0:self.bp},result=True);self.scene_boundary=None;return value

def validate(path,metadata):
 binary=Path(path).read_bytes();checks=0
 def check(ok,label):
  nonlocal checks
  assert ok,label;checks+=1
 meta=Path(metadata).read_bytes();defaults={fi:di for fi,ty,di in (struct.unpack_from('<IHi',meta,10846652+i*10)for i in range(21045))}
 check(meta[11057104+defaults[7497]]==46,'compressed metadata DISOBEY_OFFICER enum is 23')
 for bias in [0,0x1000000000]:
  m=Machine(binary,bias);p=m.props['parole_v11'];m.w(m.hero+0x20,30);m.employment(0);initial=copy.deepcopy(p)
  check(m.eligible_parole()==0,'free adult without grant cannot use parole')
  p.update(EndAge=35,Active=1,Releases=0);check(m.eligible_parole()==0,'fabricated active/end-age cannot unlock')
  p.update(Releases=1,StartAge=30,EndAge=33,Warrant41=0,LastCheckAge=-1);check(m.eligible_parole()==1,'successful release enables supervision')
  m.employment(4);check(m.eligible_parole()==0,'custody disables parole');m.employment(0)
  for age in [17,30,32,33,100]:
   m.w(m.hero+0x20,age);check(bool(m.eligible_parole())==(18<=age<33),'current age eligibility')
  m.w(m.hero+0x20,30);m.run('NativeParoleSync41',1,'parole_v11');check(p['Active']==1 and p['Remaining']==3,'status reads current release clock')
  m.run('NativeCheckin41',1,'parole_v11');check(p['LastCheckAge']==30 and p['CheckStatus41']==1 and p['CheckIns']==1,'check-in commits once')
  n=p['CheckIns'];discipline=p['Discipline'];m.run('NativeCheckin41',1,'parole_v11');check(p['CheckStatus41']==2 and p['CheckIns']==n and p['Discipline']==discipline,'duplicate check-in has no reward')
  m.w(m.hero+0x20,31);m.call_routine('annual_parole_warrant41');check(p['Warrant41']==0,'checked prior year causes no warrant')
  m.w(m.hero+0x20,32);m.call_routine('annual_parole_warrant41');check(p['Warrant41']==1 and p['MissedAge41']==31 and p['WarningAge41']==32,'missing prior-age check-in issues saved warrant')
  check(m.opened[-1][1]=='genesis_v41_parole_events','notice queued through native annual pipeline')
  notices=len(m.opened);saved=copy.deepcopy(p);m.call_routine('annual_parole_warrant41');check(p==saved and len(m.opened)==notices,'notice is idempotent')
  m.run('NativeCheckin41',1,'parole_v11');check(p['Warrant41']==1 and p['CheckStatus41']==3 and p['LastCheckAge']==30,'late check-in cannot erase warrant')
  m.w(m.hero+0x20,34);check(m.eligible_parole()==1,'unresolved warrant survives scheduled end age')
  m.reject_arrest=True;m.native_calls=[];r=m.scene41('NativeWarrantHearing41');check(r==0 and p['Warrant41']==1,'failed native arrest creation retains warrant')
  m.reject_arrest=False;r=m.scene41('NativeWarrantHearing41');check(r!=0 and p['Warrant41']==0 and p['Hearing41']==1,'successful resolution returns native arrest scenario')
  calls=len([x for x in m.native_calls if x[0]==0x2a788a8]);check(m.scene41('NativeWarrantHearing41')==0 and len([x for x in m.native_calls if x[0]==0x2a788a8])==calls,'resolved warrant does not create repeated arrests')
  p.update(Warrant41=0,StartAge=30,EndAge=33,LastCheckAge=31);m.w(m.hero+0x20,33);m.call_routine('annual_parole_warrant41');check(p['Warrant41']==1 and p['MissedAge41']==32,'last supervision year also requires check-in')
  p.update(Warrant41=0,LastCheckAge=32);m.call_routine('annual_parole_warrant41');m.run('NativeParoleSync41',1,'parole_v11');check(p['Active']==0 and p['Remaining']==0,'completed supervision closes normally')
  m.w(m.hero+0x20,31);p.update(Warrant41=0,LastCheckAge=-1);m.employment(4);m.call_routine('annual_parole_warrant41');check(p['Warrant41']==0,'no free-living check-in while incarcerated')
  p.update(Warrant41=1,MissedAge41=29);m.hook('v41_parole_release_reset',{8:m.game},outputs=(8,));check(p['Warrant41']==0 and p['MissedAge41']==-1,'native new release resets old supervision notice')
  # Both visible entry and nested action use current native custody/grant state.
  item=m.heap+0x8500;m.employment(0);m.w(m.hero+0x20,31);p.update(Releases=0,EndAge=35)
  m.u.mem_write(item+0xd0,b'\0');r=next(x for x in m.d['hooks']if x['name']=='v41_parole_entry_gate');m.execute(r['stub'],r['resume'],{19:m.ctx('parole_v11'),21:item},stack_change=-0x180)
  check(m.u.mem_read(item+0xd0,1)==b'\1','unreleased native menu entry greyed out')
  r=next(x for x in m.d['hooks']if x['name']=='v41_parole_nested_gate');check(m.execute(r['stub'],m.exit,{1:m.managed('v41-parole')},result=True)==0,'nested action greyed out')
  p['Releases']=1;check(m.execute(r['stub'],m.exit,{1:m.managed('v41-parole')},result=True)==1,'nested action unlocks after release')
  # Exact stock parole timing/conduct/country thresholds, not invented half-time.
  m.employment(4);m.u.mem_write(m.occ+0x40,b'\0');m.life_sentence=False
  for total,left,conduct,strict,expected in [(7,2,80,2,False),(8,2,50,3,True),(8,2,49,3,False),(8,2,0,2,True),(15,5,50,3,True),(15,5,49,3,False),(15,2,30,3,True),(30,10,50,3,True),(30,5,30,3,True),(30,2,10,3,True),(30,4,100,2,False),(30,2,100,4,False)]:
   m.props['worlds39']['BoardAge41']=-1;m.w(m.occ+0x38,total-left);m.w(m.occ+0x3c,left);m.f(m.occ+0x98,conduct);m.w(m.country+0x78,strict);check(bool(m.scene41('NativePrisonParole41','worlds39'))==expected,'stock board threshold '+str((total,left,conduct,strict)))
  m.props['worlds39']['BoardAge41']=-1;m.w(m.occ+0x38,13);m.w(m.occ+0x3c,2);m.f(m.occ+0x98,70);m.w(m.country+0x78,2);check(bool(m.scene41('NativePrisonParole41','worlds39')) and m.scene41('NativePrisonParole41','worlds39')==0,'board cannot reroll at same age')
  board=m.alloc();m.props['worlds39']['BoardAge41']=-1;m.u.mem_write(board+0x28,b'\1');m.hook('v41_record_stock_board_age',{19:board})
  check(m.props['worlds39']['BoardAge41']==31 and m.u.mem_read(board+0x28,1)==b'\0','stock-offered board records age and preserves original constructor instruction')
  check(m.scene41('NativePrisonParole41','worlds39')==0,'stock offer also blocks same-age custom reroll')
  m.props['worlds39']['BoardAge41']=-1;m.life_sentence=True;check(m.scene41('NativePrisonParole41','worlds39')==0,'life sentence cannot bypass board');m.life_sentence=False;m.u.mem_write(m.occ+0x40,b'\1');check(m.scene41('NativePrisonParole41','worlds39')==0,'death row cannot bypass board')
  m.u.mem_write(m.occ+0x40,b'\0');m.f(m.occ+0x98,60);m.run('NativePrisonConduct40',1,'worlds39');check(m.rf(m.occ+0x98)>60,'original stock prison conduct method executes')
 result=dict(passed=True,arm64_checks=checks,binary_sha256=hashlib.sha256(binary).hexdigest(),test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),real_prison_conduct_instructions_executed=True,arrest_creation_and_Unity_UI_mocked=True,parole_board_matches_disassembled_stock_thresholds=True,checkin_warrant_and_expiry_checked=True,aslr_biases=[0,0x1000000000],device_runtime_tested=False)
 (ROOT/'gameplay41_native_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':validate(*sys.argv[1:])
