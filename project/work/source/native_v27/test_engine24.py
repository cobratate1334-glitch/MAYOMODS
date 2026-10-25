"""Exercise actual delegate Invoke, visible profile order and Unity animation.

ARM64 tests execute the patched native library and the shipped animator code.
Unity/IL2CPP boundary APIs are modeled with verified native field layouts;
this is not an Android device or a substitute for a phone runtime test.
"""
import hashlib,json,os,struct,sys
from pathlib import Path
from test_release21 import Release21
from test_native import X,Q,ROOT
from native_relationship21 import RELATIONS,PROFILE_SITES
from native_ui21 import TRAITS
from unicorn.arm64_const import UC_ARM64_REG_PC,UC_ARM64_REG_SP,UC_ARM64_REG_S0

class Engine24(Release21):
 def __init__(self,binary,bias):
  super().__init__(binary,bias)
  self.visible={};self.active={};self.dead=set();self.rendered=[];self.components=[];self.frames=[];self.names={};self.sprites={};self.textures={};self.deltas=.08
  self.ui24={0x223e768,0x55725ac,0x5575664,0x5575198,0x3089aac,0x2f83804,0x2f731f8,0x2f7748c,0x55779e0,0x2f7c898,0x2ff8360,0x2f7d220,0xf0002030,0x2bad908,0x553b564,0x223e48c,0x223e490,0x223df90,0x223dfc8,0x223e070,0x223e93c,0x5575330,0x4df3450,0x568af7c,0x5571d30,0x557fa28,0x4dff58c,0x2e05ec4,0x2c2e2fc,0x557269c,0x2f5bc48}
  for a in self.ui24:self.map(a+bias,4)
  # Execute the real Action.Invoke and real AnimationImageSequence methods.
  for begin,length in [(0x4ec656c,20),(0x2ec424c,0x154)]:
   self.map(begin+bias,length);self.u.mem_write(begin+bias,self.load(begin,length))
  self.q(self.game+0x90,self.manager)
  self.darkly_canvas=self.alloc();self.list_manager=self.alloc();self.q(self.manager+0x38,self.darkly_canvas);self.q(self.manager+0x60,self.list_manager)
  self.active[self.darkly_canvas+0x400]=1;self.current_list_title=''
  self.reflected_class='';self.fitter=self.alloc();self.drivers=[];self.driver_arrays=[]
 def alloc(self,size=0x500):
  a=self.ptr;self.ptr+=(size+15)&~15;return a
 def rq(self,a):return int.from_bytes(self.u.mem_read(a,8),'little')
 def sprite(self,token):
  if token not in self.sprites:
   self.sprites[token]=self.alloc();self.textures[self.sprites[token]]=self.alloc()
  return self.sprites[token]
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if self.gate_mode and va in [self.gate_start,self.gate_end]:return super().mock(u,pc,size,data)
  if va==0x2c44914 and u.reg_read(X[0]) in self.names:
   lr=u.reg_read(X[30]);result=self.managed(self.names[u.reg_read(X[0])]);self.finish_api(lr,result);return
  if va==0x2f72230:
   existing=u.reg_read(X[1]);super().mock(u,pc,size,data)
   if not existing:
    button=u.reg_read(X[0]);self.q(button+0x28,button+0x300);self.active[button+0x400]=0
   return
  if va not in self.ui24:return super().mock(u,pc,size,data)
  a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30]);result=0
  if va==0x223e768:assert a[1]>=a[0] and a[1]<a[0]+0x500;self.q(a[1],a[2])
  elif va==0x55725ac:result=a[0]+0x400
  elif va==0x5575664:assert a[1]in[0,1]and a[2]==0;self.active[a[0]]=a[1]
  elif va==0x5575198:result=int(bool(a[0])and a[0]not in self.dead)
  elif va==0x3089aac:
   assert a[1:5]==[0,1,1,0],a
   target=self.str(a[0]);assert target in json.load(open(ROOT/'assets.json'))
   self.opened.append((va,target,a[1:5]))
   self.current_list_title=json.load(open(ROOT/'assets.json'))[target];self.current_list_title=json.loads(self.current_list_title)['Title'];result=1
  elif va==0x55779e0:assert a[0]in[self.manager,self.list_manager]and a[1]==0;self.actions.append(('stop_coroutines',a[0]))
  elif va==0x2f7c898:assert a[0]==self.list_manager and a[1]==0;self.current_list_title='';self.actions.append(('dismiss_lists_now',a[0]))
  elif va in[0x2ff8360,0x2f7d220]:result=self.managed(self.current_list_title)
  elif va in[0x2f83804,0x2f731f8,0x2f7748c]:
   assert a[0]==self.manager
   if va==0x2f731f8:assert a[1:3]==[5,0]
   self.actions.append((va,a[:3]))
  elif va==0xf0002030:
   assert a[0]in self.visible;key=self.str(a[1]);self.visible[a[0]].append(key)
  elif va==0x2bad908:
   token=self.str(a[0]);assert token.startswith('v24-tornado-');i=int(token.rsplit('-',1)[1]);assert 0<=i<120
   result=self.sprite(token)
  elif va==0x553b564:result=self.textures.get(a[0],0)
  elif va==0x223e48c:result=self.heap+0x141000
  elif va==0x223e490:assert a[0]==self.heap+0x141000 and self.cstring(a[1])=='Assembly-CSharp.dll';result=self.heap+0x141100
  elif va==0x223df90:assert a[0]==self.heap+0x141100;result=self.heap+0x141200
  elif va==0x223dfc8:
   self.reflected_class=self.cstring(a[2]);namespaces={'AnimationImageSequence':'','ConstraintContentSizeFitter':'BitLife.UI.Utils'}
   assert a[0]==self.heap+0x141200 and self.reflected_class in namespaces and self.cstring(a[1])==namespaces[self.reflected_class];result=self.heap+0x141300
  elif va==0x223e070:assert a[0]==self.heap+0x141300;result=self.heap+0x141400
  elif va==0x223e93c:assert a[0]==self.heap+0x141400;result=self.heap+0x141500
  elif va==0x5575330:
   assert a[1:3]==[self.heap+0x141500,0]and self.reflected_class=='AnimationImageSequence';result=self.alloc();self.components.append((a[0],result))
  elif va==0x557269c:
   assert a[0]==self.heap+0x128400 and a[1:3]==[self.heap+0x141500,0]and self.reflected_class=='ConstraintContentSizeFitter';result=self.fitter
  elif va==0x2f5bc48:
   assert a[0]==self.fitter and a[1]not in self.drivers and a[2]==0
   self.drivers.append(a[1]);array=self.alloc(0x20+len(self.drivers)*8);self.q(array+0x18,len(self.drivers))
   for i,driver in enumerate(self.drivers):self.q(array+0x20+i*8,driver)
   self.q(self.fitter+0x28,array);self.driver_arrays.append(array)
  elif va==0x4df3450:result=self.managed(self.str(a[0])+self.str(a[1]))
  elif va==0x568af7c:
   token=next(k for k,v in self.sprites.items()if v==a[1]);self.frames.append((a[0],int(token.rsplit('-',1)[1])))
  elif va==0x5571d30:assert a[1:3]==[1,0]
  elif va==0x557fa28:pass
  elif va==0x4dff58c:result=int(not self.str(a[0]))
  elif va==0x2e05ec4:assert a[0]==self.game and a[1]==0;self.rendered.append(len(self.frames))
  elif va==0x2c2e2fc:result=self.rq(a[0]+0x10)
  self.finish_api(lr,result)
  if va==0x557fa28:u.reg_write(UC_ARM64_REG_S0,struct.unpack('<I',struct.pack('<f',self.deltas))[0])
 def finish_api(self,lr,result):
  for i in range(18):self.u.reg_write(X[i],0xdead00+i)
  for i in range(8):self.u.reg_write(Q[i],0xfeed00+i)
  self.u.reg_write(X[0],result);self.u.reg_write(X[30],lr);self.u.reg_write(UC_ARM64_REG_PC,lr)
 def native_call(self,address,inputs):
  self.gate_mode=True;self.gate_start=address;self.gate_end=self.exit;self.stopped=False
  self.u.reg_write(X[30],self.exit+self.bias);sp=self.heap+0x1fff000;self.u.reg_write(UC_ARM64_REG_SP,sp)
  for reg,value in inputs.items():self.u.reg_write(X[reg],value)
  callee={i:self.u.reg_read(X[i])for i in range(19,30)}
  self.u.emu_start(address+self.bias,0,count=800000)
  assert self.stopped and self.u.reg_read(UC_ARM64_REG_SP)==sp
  assert all(self.u.reg_read(X[i])==v for i,v in callee.items())
  self.gate_mode=False;return self.u.reg_read(X[0])
 def table(self,profile):
  dictionary=self.alloc();order=self.alloc();klass=self.alloc();self.q(profile+0xa0,dictionary);self.q(profile+0xa8,order);self.q(order,klass)
  self.q(klass+0x308,0xf0002030+self.bias);self.q(klass+0x310,0)
  self.tables[dictionary]={'Gender:':'Male','Age:':'18'};self.visible[order]=['Gender:','Age:']
  self.q(profile+0x98,0x1234) # unrelated field must stay untouched
  return dictionary,order
 def display(self,profile):
  values=self.tables[self.rq(profile+0xa0)];order=self.visible[self.rq(profile+0xa8)]
  assert len(order)==len(set(order))and self.rq(profile+0x98)==0x1234
  return {key:values[key]for key in order}

def validate(path):
 binary=Path(path).read_bytes();checks=0
 for bias in [0,0x1000000000]:
  m=Engine24(binary,bias);l=m.props['life_v18'];state=m.d['states']['newlife24']['va']+bias
  controller=m.alloc();m.q(controller+0x20,m.manager);m.q(controller+0xd0,m.alloc())
  original=dict(l);m.stub('v21_new_life_native_buttons',{19:controller})
  assert l==original and [title for _,title in m.buttons]==['Body & Genetic Traits','US Map & Regions'];assert len(m.handles)==3
  assert len(m.drivers)==2 and all(m.active[button+0x400]==1 for button,_ in m.buttons);checks+=1
  m.stub('v21_new_life_native_buttons',{19:controller});assert len(m.buttons)==2 and len(m.handles)==3 and len(m.drivers)==2;checks+=1
  # Actual shipped Action.Invoke calls the new game callbacks with the target.
  for index,(_,title) in enumerate(m.buttons):
   button=m.buttons[index][0];action=m.rq(button+0xa0);assert m.rq(action+0x40)==controller
   m.native_call(0x4ec656c,{0:action});assert m.active[controller+0x400]==0
   assert m.opened[-1][1]==['genesis_v18_newlife24','genesis_v18_newlife_map24'][index];checks+=1
   m.run('NativeReturn24',0,'newlife24');assert m.active[controller+0x400]==0
   m.run('NativeReturn24',1,'newlife24');assert m.active[controller+0x400]==1;checks+=1
  pending=m.props['newlife24'];pending.update(AdultHeight=198,AdultWeight=95,Reach=12,InheritedTrait21=1,Personality=2,RareAppearance21=3)
  m.run('NativeStage24',0,'newlife24');assert m.rw(state+4)==178
  m.run('NativeStage24',1,'newlife24');assert m.rw(state+4)==198 and pending['AdultWingspan']==210 and pending['TraitName']=='Genius';checks+=1
  m.stub('v21_new_life_native_buttons',{19:controller});assert m.rw(state+4)==198 and len(m.buttons)==2;checks+=1
  m.w(m.hero+0x20,0);m.u.mem_write(m.hero+0x90,struct.pack('<f',30))
  m.stub('v21_apply_body_after_hero_generation',{19:m.game})
  assert(l['AdultHeight'],l['AdultWeight'],l['Reach'],l['Height'],l['Wingspan'],l['Weight'])==(198,95,12,50,53,3)
  assert struct.unpack('<f',m.u.mem_read(m.hero+0x90,4))[0]==95 and l['Genius']==1 and not m.handles and m.rw(state)==0;checks+=1
  before=dict(l);m.stub('v21_apply_body_after_hero_generation',{19:m.game});assert l==before;checks+=1
  # All trait selections change the verified native attribute, once at birth.
  for trait,field,minval in [(1,0x90,95),(2,0xb8,85),(3,0x90,75),(4,0xa8,80),(5,0x9c,80),(6,0x90,80),(7,0xa8,90)]:
   c=m.alloc();m.q(c+0x20,m.manager);m.q(c+0xd0,m.alloc());m.stub('v21_new_life_native_buttons',{19:c})
   pending.update(InheritedTrait21=trait);m.run('NativeStage24',1,'newlife24');m.u.mem_write(m.hero+field,struct.pack('<f',12))
   m.stub('v21_apply_body_after_hero_generation',{19:m.game});assert struct.unpack('<f',m.u.mem_read(m.hero+field,4))[0]==minval and l['TraitName']==TRAITS[trait];checks+=1
   m.u.mem_write(m.hero+field,struct.pack('<f',17));m.stub('v21_apply_body_after_hero_generation',{19:m.game});assert struct.unpack('<f',m.u.mem_read(m.hero+field,4))[0]==17;checks+=1
  # Growth, actual profile render order, repeated native RefreshScenario.
  profile=m.alloc()
  for adult in [140,178,198,225,235]:
   l.update(AdultHeight=adult,AdultWeight=95,Reach=12);heights=[]
   for age in range(19):
    m.w(m.hero+0x20,age);m.table(profile);m.stub('v21_native_hero_profile_measurements',{28:profile});shown=m.display(profile)
    assert shown['Height:']==str(l['Height'])+' cm' and shown['Weight:']==str(l['Weight'])+' kg' and shown['Wingspan:']==str(l['Wingspan'])+' cm'and shown['Age:']=='18';heights.append(l['Height']);checks+=1
   assert heights[0]==50 and heights[-1]==adult and heights==sorted(heights);checks+=1
  # Every character profile type gets its own build, age and stable life story.
  npc=m.alloc();m.names[npc]='Jordan Rivera';m.w(npc+0x20,14);m.w(npc+0x188,7);m.u.mem_write(npc+0x118,struct.pack('<f',89));m.w(m.hero+0x20,14)
  wrapper=m.alloc();m.q(wrapper+0x10,npc)
  for label,site,offset,isfriend in PROFILE_SITES:
   m.table(profile);m.q(profile+offset,wrapper if label=='StreetPerson'else npc)
   m.stub('v21_native_'+label.lower()+'_profile_story',{19:profile});shown=m.display(profile);p=m.props['relationship21']
   assert shown['Height:']==str(p['Height'])+' cm' and shown['Weight:']==str(p['Weight'])+' kg'and shown['Life story:']==p['Story']and shown['Personality:']==p['Personality'];checks+=1
   if isfriend:assert shown['Years as friends:']=='7'and shown['Your age when you met:']=='7';checks+=1
  stable=dict(p);m.w(npc+0x20,15);m.w(npc+0x188,8);m.w(m.hero+0x20,15);m.table(profile);m.q(profile+0x170,npc);m.stub('v21_native_friend_profile_story',{19:profile});shown=m.display(profile)
  assert shown['Years as friends:']=='8'and all(p[k]==stable[k]for k in['Hobby','Story','Personality','AdultHeight','AdultWeight'])and p['Height']>stable['Height'];checks+=1
  # Native Watch Tornado prepares the report image, then Unity animates it.
  career=m.props['careers_v18'];career.update(Role=1,Tours=1);m.w(m.hero+0x20,18)
  m.run('NativeStormReplay21',0,'careers_v18');animation_state=m.d['states']['tornado_animation24']['va']+bias;assert m.rw(animation_state)==0;checks+=1
  m.run('NativeStormReplay21',1,'careers_v18');assert m.rw(animation_state)==1;checks+=1
  candy=m.alloc();image=m.alloc();m.q(candy+0x28,image);m.q(candy+0x58,m.textures[m.sprite('v24-tornado-0')])
  m.stub('v24_native_tornado_image',{19:candy});assert len(m.components)==1 and m.frames[-1]==(image,0);anim=m.components[-1][1];checks+=1
  for _ in range(120):m.native_call(0x2ec424c,{0:anim})
  assert [f for _,f in m.frames[-120:]]==list(range(120)),m.frames[-10:]
  assert bytes(m.u.mem_read(anim+0x3c,1))==b'\0'and len(m.rendered)==len(m.frames);checks+=1
  m.run('NativeStormReplay21',1,'careers_v18');m.stub('v24_native_tornado_image',{19:candy});assert len(m.components)==1 and m.frames[-1]==(image,0);checks+=1
  ordinary=m.alloc();m.q(ordinary+0x28,image);m.q(ordinary+0x58,m.alloc());m.run('NativeStormReplay21',1,'careers_v18');before=len(m.frames);m.stub('v24_native_tornado_image',{19:ordinary});assert len(m.frames)==before and m.rw(animation_state)==1;checks+=1
  for age,role,tours,allowed in [(17,1,1,False),(18,5,1,False),(18,6,1,False),(18,1,0,False),(18,1,1,True)]:
   m.w(animation_state,0);m.w(m.hero+0x20,age);career.update(Role=role,Tours=tours);m.run('NativeStormReplay21',1,'careers_v18');assert bool(m.rw(animation_state))==allowed;checks+=1
  # Opening the season dashboard itself removes a bracket from an old school
  # or career, even at the same age; its old unfinished playoffs cannot block.
  season=m.props['seasons_v18']
  for oldlevel,newlevel in [(1,2),(1,3),(2,3),(3,4)]:
   season.update(Level=oldlevel,Active=1,Games=14,Phase=1,PlayoffRound=2,PlayoffDone=0,SeasonAge=20)
   if newlevel==2:m.student(11,age=20)
   else:m.professional(2 if newlevel==3 else 1,20)
   m.stub('v24_reconcile_native_sports_list',{0:m.managed('genesis_v18_seasons_v18')})
   assert season['Level']==season['Active']==season['Games']==season['PlayoffRound']==0 and season['SeasonAge']==-1;checks+=1
   m.run('NativeSeasonStart',newlevel,'seasons_v18');assert season['Level']==newlevel and season['Active']==1 and season['Error']==0;checks+=1
   before=dict(season);m.stub('v24_reconcile_native_sports_list',{0:m.managed('genesis_v18_seasons_v18')});assert season==before;checks+=1
  # House reports animate only the actual local tornado incident, once.
  world=m.props['world20'];lst=m.alloc();array=m.alloc();house=m.alloc();place=m.alloc();m.q(m.life+0x158,lst);m.q(lst+0x10,array);m.w(lst+0x18,1);m.q(array+0x20,house);m.q(house+0x28,place)
  for city,homecity,event,allowed in [('Wichita','Wichita',1,True),('Wichita','Miami',1,False),('Wichita','Wichita',2,False),('Phoenix','Phoenix',2,False)]:
   m.location(city);m.q(place+0x88,m.managed(homecity));m.q(place+0x90,m.managed('US'));m.u.mem_write(house+0x20,struct.pack('<f',85));world.update(Event=event,Resolved=0,HouseDamaged21=0);m.rolls=[0];m.w(animation_state,0)
   m.run('NativeDisasterResolve20',1,'world20');assert bool(world['HouseDamaged21'])==allowed,(city,homecity,event,world);checks+=1
   m.run('NativeHouseReplay21',0,'world20');assert m.rw(animation_state)==0
   m.run('NativeHouseReplay21',1,'world20');assert bool(m.rw(animation_state))==allowed;checks+=1
   m.w(animation_state,0);m.run('NativeHouseReplay21',1,'world20');assert m.rw(animation_state)==0;checks+=1
  assert not any(h['site']in[0x2fa8524,0x2fa8790]for h in m.d['hooks']);checks+=1
 report=dict(arm64_cases=checks,binary_sha256=hashlib.sha256(binary).hexdigest(),aslr_biases=[0,0x1000000000],actual_Action_Invoke_executed=True,native_New_Life_rounded_buttons=True,ordered_native_profile_rows=True,relationship_profile_types=len(PROFILE_SITES),birth_size_and_monotone_growth=True,actual_native_genetic_attributes=True,stock_Start_methods_unhooked=True,actual_Unity_Update_and_frame_advance_executed=True,all_120_frames_and_render_requests=True,pooled_animator_reused=True,role_and_age_gates=True,device_runtime_tested=False)
 (ROOT/'engine24_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':validate(sys.argv[1]);os._exit(0)
