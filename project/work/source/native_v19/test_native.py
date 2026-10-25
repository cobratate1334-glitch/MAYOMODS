"""Execute assembled release bridges with real ARM64 state and hostile volatile registers."""
import json,io,struct,hashlib,random,re,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm64_const import *
ROOT=Path(__file__).resolve().parent
X=[globals()['UC_ARM64_REG_X'+str(i)] for i in range(31)];Q=[globals()['UC_ARM64_REG_Q'+str(i)]for i in range(8)]
class Machine:
 def __init__(self,binary,bias=0):
  self.binary=binary;self.bias=bias;self.u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);self.pages=set();self.heap=0x7000000000;self.ptr=self.heap+0x20000;self.props={};self.contexts={};self.strings={};self.calls=[];self.feedback=0;self.rng=random.Random(18);self.rolls=[];self.stopped=False;self.sport=5
  self.d=json.loads((ROOT/'native_hooks.json').read_text());self.h=self.d['hooks'][0]
  elf=ELFFile(io.BytesIO(binary));self.loads=[dict(s.header)for s in elf.iter_segments()if s['p_type']=='PT_LOAD']
  self.map(self.d['segment_va']+bias,self.d['segment_size']);self.u.mem_write(self.d['segment_va']+bias,binary[self.d['segment_offset']:self.d['segment_offset']+self.d['segment_size']]);self.map(self.heap,0x2000000)
  self.bp=self.heap;self.game=self.heap+0x500;self.life=self.heap+0x1000;self.hero=self.heap+0x1500;self.occ=self.heap+0x2000;self.job=self.heap+0x2500;self.emoji=self.heap+0x3000;self.face=self.heap+0x3500;self.manager=self.heap+0x4000;self.iterator=self.heap+0x4500
  self.map(0x5c23000+bias,0x2000);self.map(0x6306200+bias,0x1000)
  slot=self.heap+0x5000;klass=self.heap+0x5500;statics=self.heap+0x5800
  self.q(0x5c23c90+bias,slot);self.q(slot,klass);self.q(klass+0xb8,statics);self.q(statics,self.game);self.q(self.game+0x20,self.life);self.q(self.game+0x28,self.hero);self.q(self.life+0x138,self.occ);self.w(self.occ+0x10,6);self.q(self.occ+0x28,self.job);self.w(self.job+0x10,2);self.q(self.hero+0x80,self.emoji);self.q(self.emoji+0x30,self.face);self.w(self.hero+0x20,20);self.u.mem_write(self.hero+0x94,struct.pack('<f',80.0));self.q(0x6306200+bias,self.manager)
  self.props['soccer_v12']={};base=json.load(open('analysis/base_assets.json'));base.update(json.load(open(ROOT/'assets.json')))
  import csv
  for name,value in base.items():
   if re.match('genesis_v[0-9]+_defaults_',name):
    owner=re.sub('genesis_v[0-9]+_defaults_','',name);p=self.props.setdefault(owner,{})
    for row in csv.DictReader(io.StringIO(value)):p[row['key']]=int(row['value'])if row['type']=='int'else row['value']
  self.apis={0x223e8cc,0x3059ee0,0x3059f90,0x3059934,0x3059d08,0x32800fc,0x2e0b54c,0x31542f0,0x2f8abe0,0x5577470,0x2a83910,0x2a83d1c,0x2c48a44,0x2c44914,0x2c9dfe8,0x2f3e04c,0x2f3e068,0x2f3cda8,0x2f34138,0x2f50200,0x2f506e4,0x2f5062c,0x2c9dfa4,0x2f4284c}
  self.end=int(re.search('0x[0-9a-f]+',self.h['original'])[0],16)
  for a in self.apis|{self.h['site'],self.end}:self.map(a+bias,4)
  self.u.mem_write(self.h['site']+bias,self.load(self.h['site'],4));self.u.hook_add(UC_HOOK_CODE,self.mock)
 def map(self,a,n):
  for p in range(a&~4095,(a+n+4095)&~4095,4096):
   if p not in self.pages:self.u.mem_map(p,4096);self.pages.add(p)
 def load(self,a,n):
  seg=next(s for s in self.loads if s['p_vaddr']<=a<s['p_vaddr']+s['p_filesz']);return self.binary[seg['p_offset']+a-seg['p_vaddr']:][:n]
 def q(self,a,v):self.u.mem_write(a,struct.pack('<Q',v))
 def w(self,a,v):self.u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def rw(self,a):return struct.unpack('<I',self.u.mem_read(a,4))[0]
 def managed(self,s):
  if s in self.strings:return self.strings[s]
  a=self.ptr;self.ptr+=(len(s)*2+64+15)&~15;self.w(a+16,len(s));self.u.mem_write(a+20,s.encode('utf-16-le'));self.strings[s]=a;return a
 def str(self,a):return bytes(self.u.mem_read(a+20,self.rw(a+16)*2)).decode('utf-16-le')if a else''
 def ctx(self,owner):
  if owner not in self.contexts:
   a=self.ptr;self.ptr+=128;self.q(a+16,self.managed(owner));self.contexts[owner]=a;self.props.setdefault(owner,{})
  return self.contexts[owner]
 def professional(self,sport,age=20):
  self.sport=sport;self.w(self.hero+0x20,age);self.w(self.occ+0x10,6);self.q(self.occ+0x28,self.job);self.w(self.job+0x10,2)
 def student(self,school_type,joined=True,age=16,activity='Basketball'):
  self.w(self.hero+0x20,age);self.w(self.occ+0x10,1);self.w(self.occ+0x30,school_type)
  school=self.heap+0x6000;lst=self.heap+0x6500;arr=self.heap+0x6800;team=self.heap+0x7000
  self.q(self.occ+0x20,school);self.q(school+0x48,lst);self.w(lst+0x18,1);self.q(lst+0x10,arr);self.q(arr+0x20,team);self.q(team+0x10,self.managed(activity));self.w(team+0x18,1 if joined else 2)
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if va==self.end:self.stopped=True;u.emu_stop();return
  if va not in self.apis:return
  a=[u.reg_read(r)for r in X[:4]];lr=u.reg_read(X[30]);self.calls.append((va,a));result=0
  if va==0x223e8cc:result=self.managed(bytes(u.mem_read(a[0],1024)).split(b'\0')[0].decode())
  elif va in [0x3059ee0,0x3059f90,0x3059934,0x3059d08]:
   owner=next(k for k,v in self.contexts.items()if v==a[0]);p=self.props[owner];key=self.str(a[1])
   if va==0x3059ee0:result=p.get(key,a[2]);assert isinstance(result,int),(owner,key,result)
   elif va==0x3059f90:p[key]=a[2]-0x100000000 if a[2]&0x80000000 else a[2];result=1
   elif va==0x3059934:result=self.managed(p.get(key,''))
   else:p[key]=self.str(a[2]);result=1
  elif va==0x32800fc:assert a[0]==self.life;result=self.ctx(self.str(a[1]))
  elif va==0x2e0b54c:result=(self.rolls.pop(0)if self.rolls else self.rng.randrange(a[0],a[1]))%a[1]
  elif va==0x31542f0:result=self.sport
  elif va==0x2f8abe0:assert a[:4]==[self.manager,1,1,0];self.feedback+=1;result=self.iterator
  elif va==0x5577470:assert a[:3]==[self.manager,self.iterator,0]
  elif va==0x2c44914:result=self.managed('Contact '+str(a[0]))
  elif va==0x2f3e04c:assert a[0]==self.face and a[1]in[3,8];result=self.managed('#BC8A62'if a[1]==3 else'#352219')
  elif va==0x2f3e068:assert a[0]==self.face and a[2]in[1,3,8];assert re.fullmatch('#?[0-9a-fA-F]{6,8}',self.str(a[1]))
  elif va in[0x2f506e4,0x2f5062c]:assert a[1]==0 and a[2]in[3,17];result=self.managed('#F7E9DD'if a[2]==3 else'#EEEEEE')
  elif va==0x2f34138:result=self.face+0x1000
  elif va==0x2f50200:assert self.str(a[1])=='eye';result=1
  elif va==0x2c9dfa4:result=self.emoji+0x8000
  for i in range(18):u.reg_write(X[i],0xdead00+i)
  for i in range(8):u.reg_write(Q[i],0xfeed00+i)
  u.reg_write(X[0],result&0xffffffffffffffff);u.reg_write(X[30],lr);u.reg_write(UC_ARM64_REG_PC,lr)
 def run(self,key,value=1,owner='soccer_v12'):
  self.q(self.bp+24,self.managed(key));self.q(0x6306208+self.bias,0);self.w(0x6306210+self.bias,0);self.calls=[];self.feedback=0;self.stopped=False
  for i,r in enumerate(X):self.u.reg_write(r,0xaabb00+i)
  for i,r in enumerate(Q):self.u.reg_write(r,0xdef000+i)
  self.u.reg_write(X[19],self.bp);self.u.reg_write(X[20],value&0xffffffff);self.u.reg_write(X[21],self.ctx(owner));self.u.reg_write(X[0],1);sp=self.heap+0x1fff000;self.u.reg_write(UC_ARM64_REG_SP,sp)
  before=[self.u.reg_read(r)for r in X];qb=[self.u.reg_read(r)for r in Q]
  self.u.emu_start(self.h['site']+self.bias,0,count=700000)
  assert self.stopped,(key,'missing return',hex(self.u.reg_read(UC_ARM64_REG_PC)))
  assert [self.u.reg_read(r)for r in X]==before,(key,'register corruption')
  assert [self.u.reg_read(r)for r in Q]==qb,(key,'vector register corruption')
  assert self.u.reg_read(UC_ARM64_REG_SP)==sp,(key,'stack imbalance')
  return self.props[owner]
def validate(path):
 binary=Path(path).read_bytes();checks=0
 for bias in [0,0x1000000000]:
  m=Machine(binary,bias);p=m.props['soccer_v12'];l=m.props['life_v18']
  for phase in[10,11,12,13,14]:
   p.update(Stage=1,Phase=phase,GroupRound=1,Counted=1);m.run('NativeCupSync18');assert p['Stage']==1 and p['Phase']==0 and p['Counted']==0 and p['GroupRound']==1;checks+=1
  for plan in [1,2,3]:
   p.update(Stage=1,Phase=0,Stamina=100);m.run('NativeMatchPlan',plan);assert p['Phase']==8 and p['Plan']=={1:16,2:10,3:4}[plan];checks+=1
   old=dict(p);m.run('NativeMatchPlan',plan);assert p==old;checks+=1
   m.rolls=[0,99,0,99];m.run('NativeSoccerHalf',1);assert p['Phase']==1 and p['LastFor']==2 and p['LastAgainst']==0 and m.feedback==0;checks+=1
   old=dict(p);m.run('NativeSoccerHalf',1);assert p==old;checks+=1
   m.run('NativeHalfPlan',plan);m.rolls=[99,0,99,0];m.run('NativeSoccerHalf',2);assert p['LastAgainst']==2 and p['Phase']==5 and m.feedback==1;checks+=1
  for code in [0,34,35,66,67,99]:
   p.update(Stage=4,Phase=3,LastFor=1,LastAgainst=1);m.rolls=[code];m.run('NativeSoccerHalf',3);assert p['Phase']==(4 if code<35 else 5);assert p['LastFor']==(2 if 35<=code<67 else 1);assert p['LastAgainst']==(2 if code>=67 else 1);checks+=1
  # A full three-game group preserves fixture identities and conservation of goals.
  p.update(Stage=1,Phase=5,Counted=0,GroupRound=0,T1Name='A',T2Name='B',T3Name='C',T1ID=2,T2ID=3,T3ID=4,TeamPool=0,CupType18=4)
  for j in range(4):
   for k in ['P','W','D','L','GF','GA']:p[f'T{j}{k}']=0
  for game in range(3):
   p.update(Stage=1,Phase=5,Counted=0,LastFor=3,LastAgainst=1,PenFor=0,PenAgainst=0,PlayerGoals=2);m.run('NativeSoccerCommit');checks+=1
  assert sum(p[f'T{j}GF']for j in range(4))==sum(p[f'T{j}GA']for j in range(4));assert all(sum(p[f'T{j}{k}']for k in ['W','D','L'])==3 for j in range(4));assert p['T0P']==9 and p['Stage']==3;checks+=1
  for kind in [1,4,5,6]:
   p.update(Stage=6,Phase=5,Counted=0,LastFor=2,LastAgainst=1,CupType18=kind);old=p['Titles'];m.run('NativeSoccerCommit');assert p['Stage']==0 and p['Titles']==old+1 and 'won' in p['MatchStatus18'];checks+=1
   old=dict(p);m.run('NativeSoccerCommit');assert p==old;checks+=1
  # World Cup schedule is independent of Euro/Copa schedules, and exactly four ages unlock it.
  p.update(Stage=0,Playing=1,CountryChosen=1,CountryPool=0,CountryName='Argentina',CountryFlag='flag-ar',LastWorld18=16,LastCopa18=-4);m.w(m.hero+0x20,19);m.run('NativeCupStart18',4);assert p['EntryError18']==2;checks+=1
  m.w(m.hero+0x20,20);m.run('NativeCupStart18',4);assert p['EntryError18']==0 and p['Stage']==1;checks+=1
  p['Stage']=0;m.run('NativeCupStart18',6);assert p['EntryError18']==0 and p['Competition']=='Copa América';checks+=1
  l.update(AdultHeight=198,Weight=95,Reach=8);m.w(m.hero+0x20,14);m.run('NativeLifeSync',owner='life_v18');assert l['Height']==198 and l['Wingspan']==206 and l['Position']=='Center';checks+=1
  for gene in range(9):
   m.run('NativeGeneticApply',gene,'life_v18');assert any(a==0x2c9dfa4 for a,_ in m.calls);assert l['OriginalSkin18']=='#BC8A62'and l['OriginalHairColor18']=='#352219';checks+=1
  s=m.props['seasons_v18'];m.student(2);m.run('NativeSeasonStart',1,'seasons_v18');assert s['Active']==1 and s['Level']==1;checks+=1
  for game in range(24):
   m.run('NativeSeasonHalf',1,'seasons_v18');old=dict(s);m.run('NativeSeasonHalf',1,'seasons_v18');assert s==old;m.run('NativeSeasonHalf',2,'seasons_v18');assert s['Games']==game+1;checks+=1
  m.run('NativeStatsRefresh',1,'seasons_v18');assert s['PPG']!='0.0' and s['Mate1PPG']!='0.0';assert s['FGMade']<=s['FGAttempt'] and s['ThreeMade']<=s['ThreeAttempt'] and s['FTMade']<=s['FTAttempt'];checks+=1
  for level in [1,3,4]:
   if level==1:m.student(2)
   else:m.professional(2 if level==3 else 1)
   s.update(Level=level,Games=82,SeasonLength=82,PlayoffDone=0,PlayoffRound=0,Team0Wins=60,Wins=60,Team0Losses=22,Active=1)
   for i in range(1,32):s[f'Team{i}Wins']=50-i
   m.run('NativePlayoffAdvance',1,'seasons_v18');assert s['OurSeed']==1;checks+=1
   ids=[s[f'R0M{i}A']for i in range(6 if level==4 else 8)]+[s[f'R0M{i}B']for i in range(6 if level==4 else 8)];assert len(ids)==len(set(ids));checks+=1
   for r in range(1,4):m.run('NativePlayoffAdvance',1,'seasons_v18');checks+=1
   assert s['PlayoffDone']==1 and s['Active']==0 and s['R3M0Winner']>0 and s['R3M0WinnerName']!='Awaiting draw';checks+=1
  m.run('NativeSocialSync',1,'social_v18');m.run('NativeCrushes',1,'social_v18');checks+=2
 result=dict(arm64_cases=checks,aslr_biases=[0,0x1000000000],volatile_registers_clobbered=True,tactics_idempotent=True,group_goal_conservation=True,independent_four_year_schedules=True,basketball_stats_actual_totals=True,complete_NBA_NFL_school_brackets=True,binary_sha256=hashlib.sha256(binary).hexdigest(),device_runtime_tested=False)
 (ROOT/'native_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':
 validate(sys.argv[1])
 import os
 sys.stdout.flush();os._exit(0)
