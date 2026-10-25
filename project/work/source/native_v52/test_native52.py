"""Execute the released ARM64 callbacks, with explicit managed/Unity boundaries.

No Android, graphics driver, Unity layout or physical phone is simulated here.
Assertions cover real compiled control flow and the API arguments it produces.
"""
import copy,csv,hashlib,io,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from native_v51 import test_native51 as prior
from native_v48.test_native48 import roots
from test_native import X,Q
from unicorn.arm64_const import UC_ARM64_REG_PC,UC_ARM64_REG_SP
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
from content52 import PREFIX,ACTIONS
ROOT=Path(__file__).resolve().parent

class Machine(prior.Machine):
 def managed(self,s):
  p=super().managed(s)
  if getattr(self,'string_class52',0):self.q(p,self.string_class52)
  return p
 def __init__(self,raw,bias):
  roots(ROOT);prior.ROOT=ROOT;super().__init__(raw,bias)
  self.locations={};self.stat_calls=[];self.sizes52={};self.extra52={0x2c3e7ac,0x4e00114,0x2c9e0d0,0x2ca1024,0x5581f90}
  self.stat52={0x2c46584,0x2c46670,0x2c46750,0x2c46830,0x2c469f0,0x2c46c1c,0x2c46e28}
  for va in self.extra52|self.stat52:self.map(va+bias,4)
  for va in [0x2fa9fcc,0x2faaf34,0x2cb228c,0x2cb3bd0,0x2cb58e4,0x2c9dbac]:self.map(va+bias,4);self.u.mem_write(va+bias,self.load(va,4))
  for va,n in [(0x2c420f4,8),(0x2c423a4,8),(0x2a27280,0x84),(0x251f4a4,8)]:self.map(va+bias,n);self.u.mem_write(va+bias,self.load(va,n))
  self.real51|={0x2c420f4,0x2c423a4,0x2a27280,0x251f4a4}
  self.map(0x60c1000+bias,0x1000);self.u.mem_write(0x60c1d8e+bias,b'\1')
  self.u.mem_write(self.hero+0x90,struct.pack('<f',60));self.u.mem_write(self.hero+0xb8,struct.pack('<f',50))
  self.snapshots={};self.clone_faces={};self.clone_emoji={};self.typed={};self.next52=[]
  self.string_class52=self.alloc()
  for pointer in self.strings.values():self.q(pointer,self.string_class52)
  default_country=self.alloc();self.q(default_country+16,self.managed('United States'));self.q(self.country44+0x90,self.managed('US'));self.q(self.country44+0xa0,default_country)
  assets=json.loads((ROOT/'assets.json').read_text())
  for key,value in assets.items():
   if key.startswith('genesis')and value.startswith('key,type,value'):
    for row in csv.DictReader(io.StringIO(value)):
     if row['type']=='int'and row.get('minimum')and row.get('maximum'):self.typed.setdefault(row['key'],(int(row['minimum']),int(row['maximum'])))
 def country(self,person,name):
  place=self.alloc();country=self.alloc();self.q(country+16,self.managed(name));self.q(place+0x90,self.managed('COUNTRY_CODE'));self.q(place+0xa0,country);self.locations[person]=place;return place
 def mock(self,u,pc,size,data):
  va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
  if va in getattr(self,'real51',set()):return
  if va==0x5584430:
   assert 0<=a[1]<64 and a[2]==0;self.actions.append(('index',a[:3]));self.finish_api(lr,0);return
  if va==0x59c70c0:
   fmt=self.cstr(a[2])
   if fmt in [' · Year: %d','Birth year: %d']:
    payload=(fmt%(a[3]&0xffffffff)).encode();assert len(payload)<a[1];u.mem_write(a[0],payload+b'\0');self.finish_api(lr,len(payload));return
  if va in getattr(self,'stat52',set()):
   assert a[0]==self.hero and a[2]==0;score=a[1]if a[1]<0x80000000 else a[1]-0x100000000
   self.stat_calls.append((va,score));self.finish_api(lr,0);return
  if va==0x2a6eb5c:
   assert a[0]==self.finances and a[1]==0
   amount=struct.unpack('<d',u.reg_read(Q[0]).to_bytes(16,'little')[:8])[0];self.balance+=amount;self.finish_api(lr,0);return
  if va==0x2c3e7ac:self.finish_api(lr,self.locations.get(a[0],0));return
  if va==0x4e00114:self.finish_api(lr,self.managed(''.join(self.str(p)for p in a[:3]if p)));return
  if va==0x30a2278 and self.str(a[1]).startswith(PREFIX):
   assert a[0]==self.controller46 and a[2]==0
   obj=self.alloc();self.q(obj+0x190,self.controller46);self.next_scenes.append((obj,self.str(a[1])));self.finish_api(lr,obj);return
  if va==0x2f3b1d8 and a[0]in getattr(self,'clone_faces',{}):self.finish_api(lr,self.clone_faces[a[0]][a[1]]);return
  if va==0x2f36ae4 and a[0]in getattr(self,'clone_faces',{}):self.acc[(a[0],a[1])]=a[2];self.finish_api(lr,0);return
  if va==0x2c9dfa4 and a[0]in getattr(self,'clone_emoji',{}):
   face=self.clone_emoji[a[0]];snap={f:bytes(u.mem_read(c,40)).hex()for f,c in self.clone_faces[face].items()};token=self.managed(json.dumps(snap,sort_keys=True));self.snapshots[token]=snap;self.finish_api(lr,token);return
  if va==0x2c9e0d0:
   assert a[0]in self.clone_emoji and a[1]in self.snapshots
   for f,payload in self.snapshots[a[1]].items():u.mem_write(self.clone_faces[self.clone_emoji[a[0]]][int(f)],bytes.fromhex(payload))
   self.finish_api(lr,0);return
  if va==0x2ca1024:self.finish_api(lr,self.managed('draft52-face'));return
  if va==0x5581f90:
   assert a[1]==0;self.sizes52[a[0]]=tuple(struct.unpack('<f',u.reg_read(Q[i]).to_bytes(16,'little')[:4])[0]for i in [0,1]);self.finish_api(lr,0);return
  if va==0x2fa9d40 and a[1]==0:
   self.rebuilt.append(a[:5]);self.q(a[0]+0x58,a[2]);self.w(a[0]+0xb0,a[3]);self.q(a[0]+0xc0,a[4]);self.finish_api(lr,0);return
  # Model the same finite integer bounds observed in TrySetInt, rather than
  # accepting arbitrary fields or values in newly registered containers.
  if va==0x3059f90:
   owner=next((k for k,v in self.contexts.items()if v==a[0]),None);key=self.str(a[1])
   if owner=='gameplay52':
    defs={r['key']:r for r in csv.DictReader(io.StringIO(json.loads((ROOT/'assets.json').read_text())['genesis_v18_defaults_gameplay52']))}
    assert key in defs and defs[key]['type']=='int',key
    value=a[2]if a[2]<0x80000000 else a[2]-0x100000000;r=defs[key];self.props[owner][key]=max(int(r['minimum']),min(int(r['maximum']),value));self.finish_api(lr,1);return
  return super().mock(u,pc,size,data)
 def clone_preview(self,root):
  self.prepare49();face=self.alloc();attr=self.alloc();self.u.mem_write(attr,bytes(self.u.mem_read(self.attributes,64)));self.q(face+32,attr)
  comps={}
  for f,c in self.component.items():p=self.alloc();self.u.mem_write(p,bytes(self.u.mem_read(c,64)));comps[f]=p
  self.clone_faces[face]=comps;self.q(face+24,self.list(list(comps.values())))
  emoji=self.alloc();self.q(emoji+48,face);self.clone_emoji[emoji]=face
  config=self.alloc();self.q(config+48,emoji);self.q(root+0x118,config);return emoji,face,comps
 def hook42(self,name,inputs=None,custom=False):
  r=next((r for r in self.d['hooks']if r['name']==name),None)
  if r and r['source'].startswith('b 0x'):
   original=r
   while r['source'].startswith('b 0x'):
    target=int(r['source'].split()[1],16);r=next(x for x in self.d['routines']+self.d['hooks']if x['stub']==target)
   ins=list(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(self.load(r['stub'],r['length']),r['stub']))
   ending=next(i.address-4 for i in ins if i.mnemonic=='b'and int(i.op_str.lstrip('#'),16)==original['resume'])
   return self.execute42(original['stub'],inputs,end=ending)
  return super().hook42(name,inputs,custom)
 def root(self,controller=None):
  if controller is None:controller=self.alloc();self.q(controller+32,self.manager);self.q(controller+0xd0,self.alloc());self.w(controller+0x128,0)
  self.w(self.manager+0xb4,5);self.hook42('v21_new_life_native_buttons',{19:controller});return controller
 def picker52(self,country,group=None):
  if group is None:
   group=self.alloc();self.q(group+32,self.manager)
   for off in [0x38,0x60,0x68,0x70,0x90]:self.q(group+off,self.alloc())
   self.q(group+0xa0,self.scroll);self.fitter_drivers[self.rq(group+0x90)]=[]
  self.q(group+0x58,country);self.w(group+0xb0,0);self.q(group+0xc0,self.managed('New York'))
  self.execute42(0x2fa9fcc,{19:group},end=0x2faaf34);return group
 def activity(self,code,index=0,entry=0):
  obj=self.alloc();self.q(obj+0x190,self.controller46)
  self.hook42('v52_bind_real_activity_scenario',{0:obj,2:self.managed(PREFIX+str(code))})
  self.execute42([0x2cb228c,0x2cb3bd0][entry],{0:obj,1:index});return obj

def validate(binary):
 raw=Path(binary).read_bytes();d=json.loads((ROOT/'native_hooks.json').read_text());checks=[]
 def check(ok,label):assert ok,label;checks.append(label)
 check(hashlib.sha256(raw).hexdigest()==d['binary_sha256'],'frozen binary binding')
 genetic=json.loads((ROOT/'portrait49_genetic_catalog.json').read_text())
 for bias in [0,0x1000000000]:
  m=Machine(raw,bias);m.year45(2026);m.people[m.hero]='Test Character';m.country(m.hero,'United States')
  # Execute real cache/serialization apply entries with every custom ordinary
  # pair. Mismatched colour choices normalize; explicit patterns remain exact.
  for stage in ([2]if '--quick'in sys.argv else range(6)):
   for gender in [0,1]:
    p=m.prepare49(stage,gender);m.props['life_v18']['RareAppearance21']=0
    for left in ([4]if '--quick'in sys.argv else range(1,7)):
     for right in ([6]if '--quick'in sys.argv else range(1,7)):
      p.update(LeftEye=left,RightEye=right);m.routine42('v42_apply_current_hero_appearance',{0:m.face})
      expected=str(80000+((left-1)*7)*12+gender*6+stage)
      check(m.current49(1)==expected,'ordinary equal irises '+str((bias,stage,gender,left,right)))
    for trait in [5,12,13]:
     m.props['life_v18']['RareAppearance21']=trait;m.routine42('v42_apply_current_hero_appearance',{0:m.face})
     expected=next(r['id']for r in genetic if(r['trait'],r['gender'],r['stage'])==(trait,gender,stage))
     check(m.current49(1)==expected,'explicit genetic eyes '+str((stage,gender,trait)))
     for dest in range(6):
      result=m.routine42('v52_portrait_id_for_stage',{0:m.managed(expected),1:dest,2:1-gender})
      target=next(r['id']for r in genetic if(r['trait'],r['gender'],r['stage'])==(trait,1-gender,dest))
      check(m.str(result)==target,'age/gender semantic style mapping')
  print('appearance callbacks passed at '+hex(bias),flush=True)
  m.props['life_v18']['RareAppearance21']=0;m.prepare49()
  # Actual GetCountry root field +0x140 differs from person-config +0x118.
  root=m.root();country=m.alloc();m.q(country+16,m.managed('United States'));config=m.alloc();m.q(config+16,0x11)
  m.q(root+0x118,config);m.q(root+0x140,country);m.q(root+0x120,m.managed('New York'))
  m.click(m.buttons[6][0]);check(m.transitions[-1]==6,'Regions accepts native country while config contains a non-string enum')
  group=m.picker52(country);m.routine42('v42_region_choice_1',{0:group});check(m.rebuilt[-1][2]==country,'region selection passes DataCountry rather than GodModePersonConfig')
  m.w(d['states']['regions42']['va']+bias,1);cities=m.list([m.managed('Oklahoma City'),m.managed('Tokyo'),m.alloc(),0x11])
  filt=next(r for r in m.d['hooks']if r['name']=='v46_filter_native_city_choices')
  value=m.execute42(filt['stub'],{0:cities,19:group},end=0x2faa1a8)
  check([m.str(v)for v in m.listvalues[value]]==['Oklahoma City'],'region filter accepts real strings and skips non-string/low-pointer elements')
  # Displayed ASCII label must reach the journal callback.
  scenario=m.alloc();choice=m.alloc();m.q(choice+16,m.managed('Life journal'));m.q(scenario+0x108,m.list([choice]))
  m.q(m.game+0x90,m.manager);m.hook42('v42_select_living_journal',{0:scenario,1:0});m.q(m.game+0x90,m.hud46);check(bool(m.journals),'visible Life journal button opens journal')
  # All 16 added/retained New Life controls have rooted native callbacks.
  check(len(m.buttons)==16,'New Life retains body/traits/year and adds all eight asset categories')
  emoji,face,comps=m.clone_preview(root);root=m.root(root);props=copy.deepcopy(m.props)
  st=d['states']['ui52']['va']+bias;ns=d['states']['newlife24']['va']+bias
  m.w(st,101);m.w(st+4,3);sprite=m.routine42('v52_render_newlife_preview',{0:root})
  check(bool(sprite),'New Life preview resolves a native sprite')
  check(m.props==props,'preview leaves the current life save containers unchanged')
  m.w(st,109);m.w(st+4,12);m.routine42('v52_render_newlife_preview',{0:root})
  ident=m.str(m.routine42('v49_current_component_id',{0:comps[1]}));check(ident=='88502','temporary sectoral trait renders in isolated preview')
  m.w(st+4,0);m.routine42('v52_render_newlife_preview',{0:root});ident=m.str(m.routine42('v49_current_component_id',{0:comps[1]}));check(ident!='88502','None removes temporary genetic pattern using the original baseline')
  extra=d['states']['newlife31']['va']+bias
  m.root(root);m.routine42('v52_open_draft_Hair',{0:root});group=m.picker52(country)
  check(len(m.live_options)==17 and m.transitions[-1]==6,'real native hair picker contains Apply and sixteen previews')
  m.routine42('v52_preview_Hair_3',{0:group});check(m.rw(st+4)==3 and m.rw(st+32)==0,'native preview callback stays temporary')
  m.routine42('v52_apply_draft_Hair',{0:group});check(m.rw(st+32)==3 and m.transitions[-1]==5,'native Apply commits hair and returns to New Life')
  m.root(root);m.routine42('newlife31_open_5',{0:root});group=m.picker52(country)
  m.routine42('v52_preview_Mark_12',{0:group});m.routine42('v52_apply_draft_Mark',{0:group})
  check(m.rw(ns+24)==12 and m.rw(st+44)==0,'existing Genetics control commits a previewed sectoral pattern')
  m.root(root);m.routine42('v52_open_draft_EyeColour',{0:root});group=m.picker52(country);m.routine42('v52_preview_EyeColour_4',{0:group});m.routine42('v52_apply_draft_EyeColour',{0:group})
  check(m.rw(st+44)==4 and m.rw(ns+24)==0,'ordinary colour Apply clears only conflicting genetic eye patterns')
  m.root(root);m.routine42('v52_open_draft_Scar',{0:root});group=m.picker52(country);m.routine42('v52_preview_Scar_8',{0:group});m.root(root)
  check(m.rw(st+48)==0,'returning without Apply discards temporary scar')
  native_edit=m.alloc();m.q(native_edit+32,m.manager);prefs=m.alloc(32);m.w(prefs,2)
  m.routine42('v52_apply_draft_appearance',{0:face,1:prefs});m.w(m.manager+0xb4,9)
  m.hook42('v52_adopt_saved_native_base_appearance',{0:native_edit})
  check(all(m.rw(st+off)==0 for off in [32,36,40,44])and m.rq(st+16)==0,'native appearance Save adopts the edited base face')
  m.root(root);check(m.str(m.routine42('v49_current_component_id',{0:comps[8]}))=='78026','new root preview retains saved native hairstyle')
  emoji2,face2,comps2=m.clone_preview(root);m.root(root)
  check(m.str(m.routine42('v49_current_component_id',{0:comps2[8]}))!='78026','replaced native emoji invalidates the previous draft baseline')
  # Adult NPC creation must still work while the New Life screen is active;
  # only the explicit draft-construction flag blocks random NPC layers.
  m.w(ns+56,1);m.rolls=[0,99,0];before=copy.deepcopy(m.props);m.hook42('v52_npc_assets_before_native_serialization',{25:face,21:42})
  check((face,8)in m.acc and m.acc[face,8]==49101 and m.props==before,'parent/adult NPC gets a saved scar without borrowing hero preferences')
  m.w(st+72,1);before=copy.deepcopy(m.acc);m.rolls=[0,0,0];m.hook42('v52_npc_assets_before_native_serialization',{25:face,21:42});check(m.acc==before and m.rolls==[0,0,0],'draft portrait construction does not randomize NPC layers');m.w(st+72,0)
  # Calendar derives each historical row from its own age.
  m.props['era44']['BirthYear']=1990;m.w(m.hero+32,30)
  for age in [0,1,14,20,30]:
   result=m.routine42('v52_append_calendar_to_age_header',{0:m.managed('Age: '+str(age)),1:age})
   check(m.str(result)==f'Age: {age} · Year: {1990+age}','historical age/year '+str(age))
  m.root(root);m.click(m.buttons[7][0]);group=m.picker52(country);m.routine42('v52_open_custom_year',{0:group});m.picker52(country,group)
  era=d['states']['era44']['va']+bias;previous=m.rw(era);m.routine42('v52_custom_year_minus100',{0:group});m.routine42('v52_custom_year_plus1',{0:group})
  check(m.rw(era)==previous and m.rw(st+4)==previous-99,'year adjustment is temporary')
  m.routine42('v52_apply_custom_year',{0:group});check(m.rw(era)==previous-99 and m.transitions[-1]==5,'custom birth year applies through real native callbacks')
  print('New Life, Regions, journal and calendar passed at '+hex(bias),flush=True)
  # Country model preserves national variation and individual outliers.
  means=[]
  for c in ['Netherlands','Guatemala','Japan','United States']:
   v=m.routine42('v52_country_cohort_mean',{0:m.managed(c),1:0,2:1996});means.append(v)
  check(max(means)-min(means)>100,'population means differ across source countries')
  heights=[]
  for i in range(100 if '--quick'in sys.argv else 500):
   p=m.person('Individual '+str(i),30,0);m.country(p,'Netherlands');heights.append(m.routine42('v52_person_adult_height',{0:p}))
  check(len(set(heights))>20 and min(heights)<175 and max(heights)>195,'country population has broad individual variation '+str((min(heights),max(heights),len(set(heights)))))
  father=m.person('Father Example',40,0);mother=m.person('Mother Example',5,1)
  m.q(m.life+0xa8,father);m.q(m.life+0xb8,mother);m.w(m.hero+32,10);m.country(father,'Netherlands');m.country(mother,'Netherlands')
  m.routine42('v52_repair_impossible_parent_ages');check(m.rw(mother+32)>=28 and m.rw(father+32)==40,'impossible living-parent age repaired; plausible father retained')
  friends=[m.person('Friend '+str(n),20+n,n%2)for n in range(6)]
  for friend in friends:m.country(friend,'Japan')
  m.q(m.life+0x198,m.list(friends));m.run('NativeSocialSync',1,'social_v18');social=m.props['social_v18']
  check(social['C2Age']==m.rw(mother+32),'actual native social sync reports repaired mother age')
  expected=m.routine42('v52_person_adult_height',{0:mother});check(social['C2AdultHeight20']==expected,'actual first social sync uses native country/sex height after old initializer')
  check(len({social['C'+str(n)+'Preference20']for n in range(5,11)})>1,'actual social sync produces varied preferences')
  life=m.props['life_v18'];life.update(HeightModel52=0,HeightSource51=0,AdultHeight=178)
  m.routine42('v51_ensure_family_projection');target=life['AdultHeight'];check(120<=target<=250 and life['HeightSource51']==1,'parent/country projection persists')
  m.routine42('v51_ensure_family_projection');check(life['AdultHeight']==target,'projection stable on repeat')
  life.update(HeightModel52=0,HeightSource51=2,AdultHeight=198);m.routine42('v51_ensure_family_projection');check(life['AdultHeight']==198,'explicit height retained')
  life.update(HeightModel52=0,HeightSource51=0,AdultHeight=203);m.routine42('v51_ensure_family_projection');check(life['AdultHeight']==203 and life['HeightSource51']==2,'legacy nondefault selected height retained')
  # Real native ScenarioBase dispatch: outcomes call actual stat/bank APIs,
  # persist counters, enforce age/school/fatigue/funds and support both entry overloads.
  p=m.props['gameplay52'];m.w(m.hero+32,20);m.w(m.occ+16,0);p.update(ActionsUsed=0,LastAge=20)
  m.activity(1);check(p['ActionsUsed']==0 and p['Projects']==0,'school rejection costs no quota')
  m.student(1,age=20);m.rolls=[0];m.activity(1,0,1);check(p['Projects']==1 and(0x2c46830,1)in m.stat_calls,'completed school project saves progress and impacts Smarts')
  m.props['life_v18'].update(Personality=3,InheritedTrait21=0);m.rolls=[72];count=p['Projects'];m.activity(12,0);check(p['Projects']==count+1,'thoughtful personality improves a prepared school approach')
  m.props['life_v18']['Personality']=0;m.rolls=[72];count=p['Projects'];m.activity(12,0);check(p['Projects']==count,'same roll without matching personality has a different school outcome')
  p.update(ActionsUsed=0,Fatigue=90);m.activity(21);check(p['ActionsUsed']==0,'fatigue rejection costs no quota')
  m.activity(26);check(p['Fatigue']==55,'recovery reduces saved fatigue')
  p.update(ActionsUsed=0,Fatigue=0);balance=m.balance;m.rolls=[0];obj=m.activity(27);check(p['Wins']==1 and m.balance==balance+250,'circuit win credits native bank')
  m.execute42(0x2cb228c,{0:obj,1:0});check(p['Wins']==1 and m.balance==balance+250,'repeated callback cannot duplicate circuit payout')
  p.update(ActionsUsed=0,Fatigue=0);m.rolls=[99];m.activity(27);check(p['Losses']==1 and(0x2c46670,-1)in m.stat_calls,'circuit loss impacts native Health')
  p.update(ActionsUsed=0);m.balance=10;m.activity(45);check(m.balance==10 and p['ActionsUsed']==0,'fundraiser rejects insufficient funds without quota or debit')
  m.balance=100;m.activity(45);check(m.balance==75 and p['ChurchVisits']==1,'church donation and visits persist')
  p.update(ActionsUsed=0);m.activity(81);m.props['music_studio']['Active']=1;m.activity(82);check(m.props['music_studio']['Started']==1 and m.props['music_studio']['Progress']>=8,'studio practice uses existing saved production system')
  p.update(ActionsUsed=8);count=len(m.stat_calls);m.activity(21);check(len(m.stat_calls)==count,'per-age activity quota enforced')
  for name,menu in [('intro','FightIntro52'),('gym','FightGym52')]:
   native_list=m.list([]);m.hook42('v52_fighter_circuit_in_native_'+name,{0:native_list});check(m.injected47[-1]==(native_list,menu),'native Fight menu appends the circuit using the returned typed list')
  m.w(m.hero+32,21);m.activity(21);check(p['ActionsUsed']==1,'Age Up refreshes community activity quota')
  # Final close must still reach the retained recovery with typed receivers.
  m.w(m.hero+24,1);first,second,canceled,yielded,third=m.close51()
  check((first,second,canceled,third)==(1,1,False,0),'real native close completes through lower-panel yield')
  print('country heights and gameplay passed at '+hex(bias),flush=True)
 result=dict(passed=True,binary_sha256=hashlib.sha256(raw).hexdigest(),checks=len(checks),exhaustive='--quick'not in sys.argv,cases=checks,ASLR_bases=[0,0x1000000000],physical_device_tested=False,Unity_rendering_tested=False,modeled_boundaries=['managed strings/collections, allocation and typed Genesis storage','Unity image/layout and native portrait serialization','native stat and bank API boundaries','Android lifecycle'])
 (ROOT/'native52_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=len(checks))),flush=True)

if __name__=='__main__':
 try:validate(sys.argv[1])
 except BaseException:__import__('traceback').print_exc();sys.stdout.flush();sys.stderr.flush();__import__('os')._exit(1)
 sys.stdout.flush();__import__('os')._exit(0)
