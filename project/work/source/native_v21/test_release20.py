"""Execute v20 hooks with ASLR and hostile API register clobbering."""
import hashlib,json,sys,os,random,re
from test_eligibility import GateMachine
from test_native import X,Q,ROOT
from unicorn.arm64_const import UC_ARM64_REG_PC
from geography20 import PROFILES,HAZARDS
from basketball20 import ATTRIBUTES
PENDING=0 # Resolved from the compiled allocation record in validate().
class ReleaseMachine(GateMachine):
 def __init__(self,binary,bias):
  super().__init__(binary,bias);self.place=self.heap+0x19000;self.opened=[];self.started=0
  self.location('Phoenix');self.u.mem_write(self.hero+0x18,b'\1')
  self.apis|={0x2c38288,0x30838cc,0x308480c,0x2fa8524}
  for a in self.apis:self.map(a+bias,4)
 def location(self,city,country='US'):
  self.q(self.place+0x88,self.managed(city));self.q(self.place+0x90,self.managed(country))
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if self.gate_mode and (va==self.gate_end or va==self.gate_start):return super().mock(u,pc,size,data)
  if va in [0x2c38288,0x30838cc,0x308480c,0x2fa8524]:
   lr=u.reg_read(X[30]);args=[u.reg_read(r)for r in X[:5]];result=0
   if va==0x2c38288:assert args[:2]==[self.hero,0];result=self.place
   elif va==0x2fa8524:assert self.rw(PENDING+self.bias+8)==1;self.started+=1
   else:self.opened.append((va,self.str(args[0]),args[1:]));assert args[1:]==[1,1,0,0]
   for i in range(18):u.reg_write(X[i],0xdead00+i)
   for i in range(8):u.reg_write(Q[i],0xfeed00+i)
   u.reg_write(X[0],result);u.reg_write(X[30],lr);u.reg_write(UC_ARM64_REG_PC,lr);return
  super().mock(u,pc,size,data)
 def call_routine(self,name):
  hook=next(r for r in self.d['routines']if r['name']==name)
  self.execute(hook['stub'],self.exit,{},outputs=(0,))

def validate(path):
 global PENDING
 PENDING=json.load(open(ROOT/'native_hooks.json'))['states']['new_life_body20']['va']
 binary=open(path,'rb').read();checks=0
 for bias in [0,0x1000000000]:
  m=ReleaseMachine(binary,bias);l=m.props['life_v18'];s=m.props['seasons_v18'];w=m.props['world20'];pending=m.props['newlife_body20']
  assert m.u.mem_read(PENDING+bias,32)==b'\0'*32;checks+=1
  # New Life body editor is a step before Start, and never edits the current life.
  controller=m.heap+0x1a000
  old=dict(l);m.hook('v20_custom_life_body_step',{0:controller},end=m.exit)
  assert l==old and m.opened[-1][1]=='genesis_v18_newlife_body20';checks+=1
  pending.update(Height=225,Weight=95,Reach=10);m.run('NativeBodyCommit20',1,'newlife_body20');assert m.started==1 and l==old;checks+=1
  m.hook('v20_apply_new_life_body',{19:m.game},outputs=(0,));assert (l['AdultHeight'],l['AdultWeight'],l['Reach'])==(225,95,10) and m.rw(PENDING+bias+8)==0;checks+=1
  heights=[]
  for age in [0,5,10,14,17,18]:
   m.w(m.hero+0x20,age);m.run('NativeLifeSync',1,'life_v18');heights.append(l['Height']);assert l['Wingspan']==l['Height']+10;checks+=1
  assert heights==[50,80,180,198,211,225];checks+=1
  # Geography updates from actual residence, not the preview city.
  for city,pr in PROFILES.items():
   m.location(city);m.run('NativeWorldSync20',1,'world20');assert w['City']==city and all(w[k]==pr[k]for k in HAZARDS);checks+=1
  for city in ['Phoenix','Wichita','Denver','Portland','Fairbanks','Orlando']:
   m.location(city);m.run('NativeWorldSync20',1,'world20');assert w['Hurricane']==w['Tsunami']==0;checks+=1
  for city,country in [('Miami','FR'),('Unknown place','US')]:
   m.location(city,country);m.run('NativeWorldSync20',1,'world20');assert not any(w[k]for k in HAZARDS);checks+=1
  # One warning per age; viewing never rerolls; known coastal events work.
  m.w(m.hero+0x20,20);m.location('Wichita');m.rolls=[0];m.call_routine('annual_regional_warning20');assert w['Event']==1 and w['LastAge']==20;checks+=1
  before=dict(w);count=len(m.opened);m.call_routine('annual_regional_warning20');m.run('NativeWorldSync20',1,'world20');assert w==before and len(m.opened)==count;checks+=1
  m.run('NativeDisasterResolve20',1,'world20');assert w['Resolved']==1;before=dict(w);m.run('NativeDisasterResolve20',3,'world20');assert w==before;checks+=1
  for city,event,roll in [('Miami',2,21),('Honolulu',3,14),('Hilo',4,20),('Phoenix',7,65)]:
   w['LastAge']=-1;m.location(city);m.rolls=[roll];m.call_routine('annual_regional_warning20');assert w['Event']==event,(city,w);checks+=1
  # Native landlord coastal/volcanic disasters cannot bypass the residence filter.
  event_data=m.heap+0x1f000
  for city,kind,keep in [('Phoenix','Hurricane',False),('Wichita','Tsunami',False),('Portland','Tsunami',False),('Honolulu','Volcano',False),('Miami','Hurricane',True),('Hilo','Volcano',True),('Seattle','Tsunami',True)]:
   m.location(city);m.q(event_data+0x10,m.managed(kind));m.hook('v20_native_landlord_coastal_filter',{0:event_data},outputs=(0,19,20));assert m.u.reg_read(X[0])==(event_data if keep else 0);checks+=1
  # Removed portrait IDs map to existing stock IDs, and ordinary IDs pass through.
  for row in json.load(open(ROOT/'hair_catalog.json'))+json.load(open(ROOT/'genetic_catalog.json')):
   oldid=row['name'].rsplit('-',1)[1];m.hook('v20_retired_portrait_id_migration',{1:m.managed(oldid)},stack_change=-0x30,outputs=(1,));newid=m.str(m.u.reg_read(X[1]));assert newid!=oldid;checks+=1
  id_=m.managed('00349');m.hook('v20_retired_portrait_id_migration',{1:id_},stack_change=-0x30);checks+=1
  # Career gates, one-time build and capped training.
  m.professional(1);assert m.eligible(13)==0;m.run('NativeBuild20',1,'seasons_v18');assert s['BuildChosen20']==0;checks+=1
  m.student(2);assert m.eligible(13)==1;m.run('NativeBuild20',1,'seasons_v18');assert s['Inside20']==70 and s['PerimeterDefense20']==65;checks+=1
  before={k:s[k]for k,_ in [(k+'20',v)for k,v in ATTRIBUTES]};m.run('NativeBuild20',2,'seasons_v18');assert all(s[k]==v for k,v in before.items());checks+=1
  s['Training']=0;s['ThreePoint20']=93
  for i in range(6):m.run('NativeBasketTrain20',2,'seasons_v18')
  assert s['ThreePoint20']==95 and s['Training']==6;old=dict(s);m.run('NativeBasketTrain20',2,'seasons_v18');assert s['Training']==6 and s['ThreePoint20']==95;checks+=1
  m.run('NativeBasketRefresh20',1,'seasons_v18');assert s['ThreePointBadge20']=='Elite Spot-up Shooter';checks+=1
  # Fixed random stream proves ratings matter, and that NFL scores are untouched.
  def game(level,rating,boost=0):
   m.professional(2 if level==3 else 1);m.w(m.hero+0x20,20);l.update(Height=190,Weight=81,Wingspan=195)
   s.update(Active=1,Level=level,Games=0,SeasonLength=82,Phase=0,Plan=2,Skill=45,TakeoverActive20=boost)
   for k,_ in ATTRIBUTES:s[k+'20']=rating
   m.rng=random.Random(101);m.run('NativeSeasonHalf',1,'seasons_v18');return s['FirstFor'],s['FirstAgainst']
  low=game(3,25);high=game(3,95);assert high[0]>low[0] and high[1]<low[1];checks+=1
  assert game(4,25)==game(4,95);checks+=1
  normal=game(3,55);boosted=game(3,55,1);assert boosted[0]==normal[0]+6;checks+=1
  m.run('NativeSeasonHalf',2,'seasons_v18');assert s['TakeoverActive20']==0 and s['TakeoverCharge20']<=100;checks+=1
  for k,a in [('FGMade','FGAttempt'),('ThreeMade','ThreeAttempt'),('FTMade','FTAttempt')]:assert s[k]<=s[a];checks+=1
  # Actual native friend years and persistent fictional profile details.
  npc=m.heap+0x1b000;lst=m.heap+0x1c000;arr=m.heap+0x1d000
  m.q(m.life+0x198,lst);m.w(lst+0x18,1);m.q(lst+0x10,arr);m.q(arr+0x20,npc);m.u.mem_write(npc+0x18,b'\1');m.w(npc+0x20,14);m.w(npc+0x188,7)
  m.run('NativeSocialSync',1,'social_v18');p=m.props['social_v18'];assert p['C5YearsFriends']==7 and p['C5Age']==14 and p['C5Personality20']!='Not yet known';checks+=1
  stable={k:p[k]for k in ['C5ProfileId20','C5Personality20','C5Hobby20','C5Ambition20','C5Belief20','C5Story20']};m.w(npc+0x20,15);m.w(npc+0x188,8);m.run('NativeSocialSync',1,'social_v18');assert all(p[k]==v for k,v in stable.items()) and p['C5YearsFriends']==8;checks+=1
 result=dict(arm64_cases=checks,new_life_body_step=True,current_residence_geography=True,once_per_age_disasters=True,inland_ocean_hazards_excluded=True,retired_portrait_save_migration=True,basketball_attributes_affect_gameplay=True,NFL_unaffected_by_basketball_attributes=True,stable_character_profiles=True,native_friendship_years=True,aslr_biases=[0,0x1000000000],binary_sha256=hashlib.sha256(binary).hexdigest(),device_runtime_tested=False)
 (ROOT/'release20_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
if __name__=='__main__':validate(sys.argv[1]);os._exit(0)
