"""Run reported regression paths in ARM64, including writable UI state."""
import hashlib,json,sys,os,struct,re
from pathlib import Path
from elftools.elf.elffile import ELFFile
from test_release20 import ReleaseMachine
from test_native import X,Q,ROOT
from native_relationship21 import RELATIONS
from unicorn import UC_PROT_READ,UC_PROT_EXEC,UC_PROT_WRITE
from unicorn.arm64_const import UC_ARM64_REG_PC,UC_ARM64_REG_SP
def a_context_valid(m,u):return u.reg_read(X[0]) in m.contexts.values()
class Release21(ReleaseMachine):
 def __init__(self,binary,bias):
  super().__init__(binary,bias);self.handles={};self.next_handle=1;self.buttons=[];self.tables={};self.actions=[]
  self.config=self.heap+0x126000;self.weak_controller=0;self.ui_calls=[]
  self.exports={'mayo21_config':self.config,'mayo21_reset':0xf0002010+bias,'mayo21_ui':0xf0002020+bias}
  self.u.mem_write(self.config,struct.pack('<7i',0,178,72,2,0,0,0))
  self.dlopen=self.d['imports']['dlopen']['plt'];self.dlsym=self.d['imports']['dlsym']['plt']
  self.extra={self.dlopen,self.dlsym,0x223e704,0x223e708,0x223e73c,0x223e784,0x55724dc,0x55844f4,0x5582ca4,0x5584430,0x2f72230,0x2237158,0x4ec64e4,0x3dad9a0,0xf0002010,0xf0002020,0x2b3e754}
  for a in self.extra:self.map(a+bias,4)
  # Metadata usage double pointers used by the original Setup routine.
  self.action_class=self.heap+0x127000;self.action_info=self.heap+0x127100
  for va,value in [(0x5c2a0b0,self.action_class),(0x5c7a528,self.action_info),(0x5c27b40,self.action_info)]:
   self.map(va+bias,8);slot=self.ptr;self.ptr+=32;self.q(slot,value);self.q(va+bias,slot)
  code_start=self.d['segment_va']+bias;code_size=(self.d['segment_size']+4095)&~4095;self.u.mem_protect(code_start,code_size,UC_PROT_READ|UC_PROT_EXEC)
  for state in self.d['states'].values():
   a=state['va']+bias;self.u.mem_protect(a&~4095,((a+state['size']+4095)&~4095)-(a&~4095),UC_PROT_READ|UC_PROT_WRITE)
 def cstring(self,p):
  s=bytearray()
  while self.u.mem_read(p,1)!=b'\0':s+=self.u.mem_read(p,1);p+=1
  return s.decode()
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if va not in self.extra:
   if va in [0x3059ee0,0x3059f90,0x3059934,0x3059d08]:assert a_context_valid(self,u), (hex(va),hex(u.reg_read(X[0])),self.contexts,hex(self.ptr))
   return super().mock(u,pc,size,data)
  a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30]);ret=0
  if va==self.dlopen:assert self.cstring(a[0])=='libmayo21.so'and a[1]==2;ret=0x777001
  elif va==self.dlsym:assert a[0]==0x777001;ret=self.exports.get(self.cstring(a[1]),0)
  elif va in [0x223e704,0x223e708]:ret=self.next_handle;self.next_handle+=1;self.handles[ret]=a[0]
  elif va==0x223e73c:ret=self.handles.get(a[0],0)
  elif va==0x223e784:self.handles.pop(a[0],None)
  elif va==0x55724dc:ret=a[0]+0x400
  elif va==0x55844f4:ret=7
  elif va==0x5582ca4:ret=self.heap+0x128000
  elif va==0x5584430:self.actions.append(('index',a[:3]));assert a[1]in [8,9]
  elif va==0x2f72230:
   assert a[0]==self.manager and a[2]==self.heap+0x128000 and a[3:5]==[1,4]
   title=self.str(a[5]);sp=u.reg_read(UC_ARM64_REG_SP);subtitle=self.str(int.from_bytes(u.mem_read(sp,8),'little'));assert subtitle
   ret=a[1]
   if not ret:ret=self.ptr;self.ptr+=0x500;self.buttons.append((ret,title))
  elif va==0x2237158:assert a[0]==self.action_class;ret=self.ptr;self.ptr+=0x100
  elif va==0x4ec64e4:assert a[2]==self.action_info;self.q(a[0]+0x20,a[1]);self.q(a[0]+0x28,a[2]);self.q(a[0]+0x40,a[1])
  elif va==0x3dad9a0:self.tables.setdefault(a[0],{})[self.str(a[2])]=self.str(a[1])
  elif va==0xf0002010:self.u.mem_write(self.config,struct.pack('<7i',0,178,72,2,0,0,0))
  elif va==0xf0002020:self.ui_calls.append(a[0])
  elif va==0x2b3e754:assert a[1:3]==[1,0];self.performance_changed=a[0]
  for n in range(18):u.reg_write(X[n],0xdead00+n)
  for n in range(8):u.reg_write(Q[n],0xfeed00+n)
  u.reg_write(X[0],ret);u.reg_write(X[30],lr);u.reg_write(UC_ARM64_REG_PC,lr)
 def stub(self,name,inputs):
  hook=next(r for r in self.d['hooks']if r['name']==name)
  return self.hook(name,inputs,end=hook['stub']+hook['length']-8)

def validate(path):
 binary=Path(path).read_bytes();checks=0
 for bias in [0,0x1000000000]:
  m=Release21(binary,bias);l=m.props['life_v18'];s=m.props['seasons_v18'];w=m.props['world20']
  assert not any(h['site']==0x2fa8524 for h in m.d['hooks']);assert 'new_life_body20'not in m.d['states'];checks+=1
  controller=m.heap+0x129000;m.q(controller+0x20,m.manager);m.q(controller+0xd0,m.heap+0x12a000)
  old=dict(l);m.stub('v21_new_life_native_buttons',{19:controller});assert l==old and len(m.buttons)==2 and len(m.handles)==3;checks+=1
  m.stub('v21_new_life_native_buttons',{19:controller});assert len(m.buttons)==2 and len(m.handles)==3;checks+=1
  for n,(button,title)in enumerate(m.buttons):
   callback=int.from_bytes(m.u.mem_read(button+0xa0,8),'little');pointer=int.from_bytes(m.u.mem_read(callback+0x18,8),'little');m.execute(pointer-bias,m.exit,{0:controller},outputs=(0,));assert m.ui_calls[-1]==n+1;checks+=1
  m.u.mem_write(m.config,struct.pack('<7i',1,225,95,10,1,2,3));m.w(m.hero+0x20,0);m.stub('v21_apply_body_after_hero_generation',{19:m.game});assert(l['AdultHeight'],l['AdultWeight'],l['Reach'],l['Height'],l['Weight'],l['Wingspan'])==(225,95,10,50,3,52);assert m.rw(m.config)==0 and l['TraitName']=='Genius'and l['RareAppearanceName21']=='Vitiligo';checks+=1
  assert struct.unpack('<f',m.u.mem_read(m.hero+0x90,4))[0]==95;checks+=1
  before=dict(l);m.stub('v21_apply_body_after_hero_generation',{19:m.game});assert l==before;checks+=1
  for adult in [140,178,198,225,235]:
   l.update(AdultHeight=adult,AdultWeight=72,Reach=8);heights=[];weights=[]
   for age in range(19):
    m.w(m.hero+0x20,age);m.run('NativeLifeSync',1,'life_v18');heights.append(l['Height']);weights.append(l['Weight']);assert l['Wingspan']>=l['Height'];checks+=1
   assert heights[0]==50 and heights[-1]==adult and heights==sorted(heights)and weights==sorted(weights);checks+=1
  profile=m.heap+0x12b000;dictionary=m.heap+0x12c000;m.q(profile+0x98,dictionary);m.q(profile+0xa0,m.heap+0x12d000);m.tables[dictionary]={'Gender:':'Male','Age:':'18'}
  m.stub('v21_native_hero_profile_measurements',{28:profile});assert m.tables[dictionary]['Height:']=='235 cm'and m.tables[dictionary]['Wingspan:']=='243 cm'and m.tables[dictionary]['Weight:']=='72 kg'and m.tables[dictionary]['Gender:']=='Male';assert int.from_bytes(m.u.mem_read(profile+0xa0,8),'little')==0;checks+=1
  # Each education/career transition discards unfinished old brackets and allows
  # a matching season at the same age. A valid current bracket survives.
  for oldlevel,newlevel in [(1,2),(1,3),(2,3),(2,4),(3,4)]:
   s.update(Level=oldlevel,Active=1,Games=14,Phase=1,PlayoffRound=2,PlayoffDone=0,SeasonAge=20)
   if newlevel==2:m.student(11,age=20)
   else:m.professional(2 if newlevel==3 else 1,20)
   m.run('NativeSeasonReconcile21',1,'seasons_v18');assert s['Level']==s['Active']==s['Games']==s['PlayoffRound']==0 and s['SeasonAge']==-1;checks+=1
   m.run('NativeSeasonStart',newlevel,'seasons_v18');assert s['Level']==newlevel and s['Active']==1 and s['Error']==0;checks+=1
   before=dict(s);m.run('NativeSeasonReconcile21',1,'seasons_v18');assert s==before;checks+=1
  # The selected native relationship is not limited to social-following slots.
  npc=m.heap+0x131000;m.w(npc+0x20,14);m.w(npc+0x188,7);m.u.mem_write(npc+0x118,struct.pack('<f',89.0));m.w(m.hero+0x20,14)
  for label,entry,site,reg,isfriend in RELATIONS:
   m.stub('v21_relationship_snapshot_'+label,{1:npc});m.stub('v21_relationship_story_menu_'+label,{int(reg[1:]):m.heap+0x130000});assert m.injected==['PersonStory21'];checks+=1;p=m.props['relationship21'];assert p['Age']==14 and p['Connection']==89 and p['Personality']and p['Hobby'];checks+=1
   if isfriend:assert p['YearsFriends']==7 and p['FirstMetAge']==7;checks+=1
  m.stub('v21_relationship_snapshot_Friend',{1:npc});p=m.props['relationship21'];stable={k:p[k]for k in ['Personality','Hobby','Ambition','Clubs','Belief','Story']};m.w(npc+0x20,15);m.w(npc+0x188,8);m.w(m.hero+0x20,15);m.stub('v21_relationship_snapshot_Friend',{1:npc});assert all(p[k]==v for k,v in stable.items())and p['YearsFriends']==8;checks+=1
  m.q(profile+0x170,npc);m.stub('v21_native_friend_profile_story',{19:profile});assert m.tables[dictionary].get('Years as friends:')=='8'and m.tables[dictionary].get('Personality:')==p['Personality'],(m.tables,hex(m.ptr),m.props['relationship21']);checks+=1
  # No repeated notice is queued; the entity's normal alive state is untouched.
  entity=m.heap+0x132000;m.u.mem_write(entity+0x330,b'\1');m.u.mem_write(entity+0x18,b'\0');assert m.hook('v21_silent_departed_notice',{0:entity},True)==0 and bytes(m.u.mem_read(entity+0x330,1))==b'\0';checks+=1
  # Animation requires a real local owned home and a tornado-eligible city.
  lst=m.heap+0x133000;arr=m.heap+0x134000;house=m.heap+0x135000;place=m.heap+0x136000
  m.q(m.life+0x158,lst);m.q(lst+0x10,arr);m.w(lst+0x18,1);m.q(arr+0x20,house);m.q(house+0x28,place)
  for hero_city,house_city,event,expect in [('Wichita','Wichita',1,True),('Wichita','Miami',1,False),('Wichita','Wichita',2,False),('Miami','Wichita',1,False)]:
   m.location(hero_city);m.q(place+0x88,m.managed(house_city));m.q(place+0x90,m.managed('US'));m.u.mem_write(house+0x20,struct.pack('<f',85.0));w.update(Event=event,Resolved=0,HouseDamaged21=0);m.rolls=[0];m.run('NativeDisasterResolve20',1,'world20');assert bool(w['HouseDamaged21'])==expect;checks+=1
   count=len(m.ui_calls);m.run('NativeHouseReplay21',1,'world20');assert len(m.ui_calls)==count+int(expect);checks+=1
   m.run('NativeHouseReplay21',1,'world20');assert len(m.ui_calls)==count+int(expect);checks+=1
  m.w(lst+0x18,0);m.location('Wichita');w.update(Event=1,Resolved=0);m.rolls=[0];m.run('NativeDisasterResolve20',1,'world20');assert not w['HouseDamaged21'];checks+=1
  c=m.props['careers_v18'];c.update(Role=1,Tours=1)
  for age,role,allowed in [(17,1,False),(18,1,True),(18,5,False),(18,6,False),(18,0,False)]:
   m.w(m.hero+0x20,age);c['Role']=role;count=len(m.ui_calls);m.run('NativeStormReplay21',1,'careers_v18');assert len(m.ui_calls)==count+int(allowed);checks+=1
  # Every native school club icon maps to a registered, nonblank stock token.
  clubs=json.load(open(ROOT.parent/'life_content.json'))['a16_school-activities-enc'];activity=m.heap+0x137000
  for row in clubs:m.w(activity+0x10,int(row['Index']));icon=m.hook('v21_icons_existing_school_clubs',{0:activity},True);assert m.str(icon);checks+=1
  # Projects modify the currently joined native club, cap the annual schedule,
  # and reject a removed club or an adult whose occupation is no longer school.
  m.student(2,activity='Podcast Club');p=m.props['school_v9'];p.update(Sessions21=0,ClubName21='Podcast Club')
  for choice in [1,2,3,1,2,3]:
   before=p['Projects'];m.run('NativeClubProject21',choice,'school_v9');assert p['Projects']==before+1 and m.performance_changed==m.heap+0x7000;checks+=1
  before=dict(p);m.run('NativeClubProject21',1,'school_v9');assert p==before;checks+=1
  p['Sessions21']=0;m.student(2,joined=False,activity='Podcast Club');before=dict(p);m.run('NativeClubProject21',1,'school_v9');assert p==before;checks+=1
  m.professional(2);before=dict(p);m.run('NativeClubProject21',1,'school_v9');assert p==before;checks+=1
 result=dict(arm64_cases=checks,binary_sha256=hashlib.sha256(binary).hexdigest(),new_life_native_buttons=True,no_start_interception=True,writable_settings_and_GC_handles=True,birth_and_age_growth=True,native_profile_measurements_visible=True,retired_school_seasons=True,direct_relationship_details=True,actual_friendship_duration=True,quiet_incidental_death_notices=True,local_owned_home_damage_only=True,transparent_video_scoped=True,all_extended_school_icons=True,aslr_biases=[0,0x1000000000],device_runtime_tested=False)
 (ROOT/'release21_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
if __name__=='__main__':validate(sys.argv[1]);os._exit(0)
