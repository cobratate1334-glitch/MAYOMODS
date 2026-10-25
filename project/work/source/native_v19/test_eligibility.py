"""Exercise current-career, school-team, region and native menu guards in ARM64."""
import hashlib,json,os,re,struct,sys
from pathlib import Path
from test_native import Machine,X,Q,ROOT
from unicorn.arm64_const import UC_ARM64_REG_PC,UC_ARM64_REG_SP

class GateMachine(Machine):
 def __init__(self,binary,bias):
  self.gate_mode=False;self.gate_end=None;self.gate_start=None;self.injected=[];self.profile_opened=[]
  super().__init__(binary,bias)
  self.exit=0xf0000000;self.map(self.exit+bias,4)
  for hook in self.d['hooks']:
   self.map(hook['site']+bias,4);self.u.mem_write(hook['site']+bias,self.load(hook['site'],4))
   if hook['original'].startswith('b '):self.map(int(re.search('0x[0-9a-f]+',hook['original'])[0],16)+bias,4)
  self.apis.add(0x30611d0);self.map(0x30611d0+bias,4)
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if self.gate_mode and va==self.gate_end:self.stopped=True;u.emu_stop();return
  if self.gate_mode and va==self.gate_start:return
  if self.gate_mode and va==0x30611d0 and self.gate_end==0x30611d4:return
  if self.gate_mode and va==0x30611d0 and self.gate_end!=0x30611d4:
   self.injected.append(self.str(u.reg_read(X[1])));lr=u.reg_read(X[30])
   for i in range(18):u.reg_write(X[i],0xdead00+i)
   for i in range(8):u.reg_write(Q[i],0xfeed00+i)
   u.reg_write(X[30],lr);u.reg_write(UC_ARM64_REG_PC,lr);return
  if self.gate_mode and va in{0x2237158,0x2a1bcf0,0xf0001000,0x30838cc}:
   a=[u.reg_read(r)for r in X[:5]];lr=u.reg_read(X[30]);result=0
   if va==0x2237158:assert a[0]==self.choice_klass;result=self.new_choice
   elif va==0x2a1bcf0:assert a[0]==self.new_choice and a[2:]==[0,1,0];self.q(a[0]+0x10,a[1])
   elif va==0xf0001000:
    assert a[:3]==[self.profile_list,self.new_choice,0];count=self.rw(self.profile_list+0x18);self.q(self.profile_array+0x20+count*8,self.new_choice);self.w(self.profile_list+0x18,count+1)
   else:self.profile_opened.append((self.str(a[0]),a[1:]))
   for i in range(18):u.reg_write(X[i],0xdead00+i)
   for i in range(8):u.reg_write(Q[i],0xfeed00+i)
   u.reg_write(X[0],result);u.reg_write(X[30],lr);u.reg_write(UC_ARM64_REG_PC,lr);return
  super().mock(u,pc,size,data)
 def execute(self,site,end,inputs,result=False,stack_change=0,outputs=()):
  self.gate_mode=True;self.gate_end=end;self.gate_start=site;self.stopped=False;self.calls=[];self.injected=[]
  for i,r in enumerate(X):self.u.reg_write(r,0xaabb00+i)
  for i,r in enumerate(Q):self.u.reg_write(r,0xdef000+i)
  self.u.reg_write(X[30],self.exit+self.bias)
  for reg,value in inputs.items():self.u.reg_write(X[reg],value)
  sp=self.heap+0x1fff000;self.u.reg_write(UC_ARM64_REG_SP,sp)
  before=[self.u.reg_read(r)for r in X];vectors=[self.u.reg_read(r)for r in Q]
  self.u.emu_start(site+self.bias,0,count=400000)
  assert self.stopped,('missing return',hex(self.u.reg_read(UC_ARM64_REG_PC)))
  value=self.u.reg_read(X[0]);after=[self.u.reg_read(r)for r in X]
  if result:before[0]=value
  for reg in outputs:before[reg]=after[reg]
  assert after==before,('register corruption',site)
  assert[self.u.reg_read(r)for r in Q]==vectors
  assert self.u.reg_read(UC_ARM64_REG_SP)==sp+stack_change
  self.gate_mode=False;return value
 def eligible(self,kind):
  address=next(r['stub']for r in self.d['routines']if r['name']=='current_eligibility19')
  return self.execute(address,self.exit,{0:kind},True)
 def hook(self,name,inputs,result=False,stack_change=0,end=None,outputs=()):
  hook=next(h for h in self.d['hooks']if h['name']==name)
  if end is None:
   end=self.exit if result else int(re.search('0x[0-9a-f]+',hook['original'])[0],16)if hook['original'].startswith('b ')else hook['resume']
  return self.execute(hook['site'],end,inputs,result,stack_change,outputs)

def validate(path):
 binary=Path(path).read_bytes();checks=0
 nations=json.loads((ROOT.parent/'native_v13/assets/pools.json').read_text())['nationalpool']
 region=lambda flag:next(i for i,(_,f)in enumerate(nations)if f=='flag-'+flag)
 for bias in[0,0x1000000000]:
  m=GateMachine(binary,bias);cup=m.props['soccer_v12'];season=m.props['seasons_v18']
  for sport in[0,1,2,3,4,5]:
   m.professional(sport)
   for kind,expected in[(1,sport==5),(2,sport==2),(3,sport==1),(6,sport in[1,2]),(4,False),(5,False),(7,False)]:
    assert m.eligible(kind)==expected,(sport,kind);checks+=1
  m.w(m.occ+0x10,0)
  for kind in[1,2,3,4,5,6,7,9,10]:assert m.eligible(kind)==0;checks+=1
  m.professional(2,17)
  for kind in[2,6,11]:assert m.eligible(kind)==0;checks+=1
  for age in[0,12,13,17,18,80]:
   m.w(m.hero+0x20,age)
   for kind,expected in[(11,age>=18),(12,age>=13)]:assert m.eligible(kind)==expected;checks+=1
  for school in[0,1,2,3,10,11,12,13]:
   for joined in[False,True]:
    m.student(school,joined,age=20 if school in[11,12]else 16)
    for kind,expected in[(4,school==2 and joined),(5,school in[11,12]and joined),(7,school in[2,11,12]and joined)]:assert m.eligible(kind)==expected,(school,joined,kind);checks+=1
  for activity in['Basketball','Basketball Team','basketball','Soccer','Chess']:
   m.student(2,activity=activity);assert m.eligible(4)==(activity in['Basketball','Basketball Team','basketball']);checks+=1
  for level in[1,2,3,4]:
   season['Level']=level;m.professional(2)
   assert m.eligible(8)==(level==3);checks+=1
   m.professional(1);assert m.eligible(8)==(level==4);checks+=1
   m.student(2);assert m.eligible(8)==(level==1);checks+=1
   m.student(12,age=22);assert m.eligible(8)==(level==2);checks+=1
  m.professional(5);cup['CountryChosen']=1
  for flag in['no','fr','ar','br','us','jp']:
   cup['CountryPool']=region(flag)
   assert m.eligible(9)==(flag in['no','fr']);checks+=1
   assert m.eligible(10)==(flag in['ar','br']);checks+=1
  cup['CountryChosen']=0
  for kind in[9,10]:assert m.eligible(kind)==0;checks+=1
  m.professional(2);cup.update(CountryChosen=1,CountryPool=region('ar'))
  for kind in[9,10]:assert m.eligible(kind)==0;checks+=1
  # Disallowed saved entry paths cannot start or advance a match.
  season.update(Active=0,Games=0,Phase=0,Level=1);m.student(2,joined=False)
  m.run('NativeSeasonStart',1,'seasons_v18');assert season['Active']==0 and season['Error']==3;checks+=1
  season.update(Active=1,Level=1,Phase=0)
  m.run('NativeSeasonHalf',1,'seasons_v18');assert season['Games']==0 and season['Phase']==0;checks+=1
  m.student(2);m.run('NativeSeasonStart',2,'seasons_v18');assert season['Error']==3;checks+=1
  cup.update(Stage=0,Playing=1,CountryChosen=1,CountryPool=region('ar'));m.professional(2)
  m.run('NativeCupStart18',4);assert cup['Stage']==0 and cup['EntryError18']==5;checks+=1
  # The native IsEnabled callbacks return a current-state boolean.
  for marker,kind in[('v19-soccer',1),('v19-nba',2),('v19-nfl',3),('v19-highschool-basketball',4),('v19-college-basketball',5),('v19-pro-seasons',6),('v19-school-basketball',7),('v19-current-season',8),('v19-euros',9),('v19-copa',10),('v19-adult',11),('v19-social',12)]:
   m.professional(5);cup.update(CountryChosen=1,CountryPool=region('ar'))
   expected=m.eligible(kind)
   assert m.hook('v19_grey_nested_requirements',{0:m.ctx('social_v18'),1:m.managed(marker)},True)==expected;checks+=1
  entry=m.heap+0x8500
  for owner,sport,expected in[('cup_access18',5,False),('cup_access18',2,True),('pro_sports18',2,False),('pro_sports18',5,True),('school_sports18',2,True)]:
   m.professional(sport);m.u.mem_write(entry+0xd0,b'\0')
   m.hook('v19_grey_entry_requirements',{19:m.ctx(owner),21:entry})
   assert bool(m.u.mem_read(entry+0xd0,1)[0])==expected;checks+=1
  for age in[17,18]:
   m.w(m.hero+0x20,age)
   for owner in['storm_career19','coach_career19','manager_career19','racer_career19']:
    m.u.mem_write(entry+0xd0,b'\0');m.hook('v19_grey_entry_requirements',{19:m.ctx(owner),21:entry});assert bool(m.u.mem_read(entry+0xd0,1)[0])==(age<18);checks+=1
  # Social Media and its seven native account menus get the intended keys.
  for name,key,reg in[('v19_native_social_tab','SocialMedia',21)]+[('v19_native_following_'+str(i),'SocialFollowing'+str(i),19)for i in range(2,9)]:
   hook=next(h for h in m.d['hooks']if h['name']==name)
   m.hook(name,{reg:entry},end=hook['stub']+hook['length']-8);assert m.injected==[key];checks+=1
  m.hook('v19_visible_special_careers',{0:entry,1:m.managed('SpecialCareers')},stack_change=-0xd0,end=0x30611d4);checks+=1
  # Only our score iterator loses queued repeats; ordinary injuries keep theirs.
  m.q(0x6306208+bias,m.iterator)
  for iterator,pending,expected in[(m.iterator,60,0),(m.iterator,1,0),(m.iterator+0x100,60,60)]:
   m.w(0x6306210+bias,pending);m.hook('v19_feedback_no_replay',{19:iterator});assert m.rw(0x6306210+bias)==expected;checks+=1
  # The two native trait tabs expose all styles, label them and show arrows.
  for feature in[1,3]:
   assert m.hook('v19_appearance_trait_arrows',{1:feature},True)==1;checks+=1
   assert m.hook('v19_expose_all_trait_styles',{1:feature},True)==0;checks+=1
  support=m.heap+0x9800
  for feature,labels in[(3,['No added trait','Vitiligo','Freckles','Birthmark','Dimples','Albinism']),(1,['Matching eyes','Heterochromia'])]:
   m.w(support+0x18,feature)
   for style,label in enumerate(labels):
    ptr=m.hook('v19_native_trait_names',{0:support,1:style},True);assert m.str(ptr)==label;checks+=1
  m.hook('v19_skin_traits_tab',{0:m.managed('Skin'),21:3},True,end=0x2f9aaac,outputs=(1,));assert m.str(m.u.reg_read(X[0]))==m.str(m.u.reg_read(X[1]))=='Skin & Traits';checks+=1
  m.hook('v19_albinism_colors',{0:m.face,1:5,2:3},stack_change=-0x30)
  colors=[(a[2],m.str(a[1]))for va,a in m.calls if va==0x2f3e068];assert colors==[(3,'fff0e3'),(8,'f5f0e8'),(1,'c8d9e6')];checks+=1
  component=m.heap+0x9900;eye_color=m.managed('583818')
  for feature,style,expected in[(1,1,'ffffff'),(1,0,'583818'),(3,1,'583818')]:
   m.w(component+0x14,style);m.hook('v19_multicolor_iris_tint',{1:eye_color,19:eye_color,20:component,21:feature},end=0x2f474ec,outputs=(1,));assert m.str(m.u.reg_read(X[1]))==expected and m.u.reg_read(X[19])==eye_color;checks+=1
  profile=m.heap+0xb000;activity=m.heap+0xb800;m.profile_list=m.heap+0xc000;m.profile_array=m.heap+0xc800;old_choice=m.heap+0xd000;m.new_choice=m.heap+0xd800;m.choice_klass=m.heap+0xe000;list_klass=m.heap+0xe800
  m.q(profile+0x170,activity);m.q(activity+0x10,m.managed('Basketball'));m.w(activity+0x18,1);m.q(m.profile_list,list_klass);m.q(m.profile_list+0x10,m.profile_array);m.w(m.profile_list+0x18,1);m.q(m.profile_array+0x20,old_choice);m.q(old_choice,m.choice_klass);m.q(old_choice+0x10,m.managed('Practice harder'));m.q(list_klass+0x308,0xf0001000+bias);m.q(list_klass+0x310,0)
  for a in[0x2237158,0x2a1bcf0,0xf0001000,0x30838cc]:m.map(a+bias,4)
  hook=next(h for h in m.d['hooks']if h['name']=='v19_school_basketball_action')
  m.hook(hook['name'],{19:profile,20:m.profile_list},end=hook['stub']+hook['length']-8)
  assert m.rw(m.profile_list+0x18)==2 and m.str(int.from_bytes(m.u.mem_read(m.new_choice+0x10,8),'little'))=='Basketball season & games';checks+=1
  m.q(profile+0x108,m.profile_array);m.w(m.profile_array+0x18,2)
  m.hook('v19_school_basketball_select',{0:profile,1:1},end=m.exit)
  assert m.profile_opened==[('genesis_v18_school_sports18',[1,1,0,0])];checks+=1
  m.hook('v19_school_basketball_select',{0:profile,1:0},stack_change=-0x40)
  assert len(m.profile_opened)==1;checks+=1
 result=dict(arm64_cases=checks,current_native_occupation=True,joined_school_team_required=True,euros_european_nations_only=True,copa_south_american_nations_only=True,grey_native_entries_and_tiles=True,native_social_menu_integration=True,legacy_score_replay_dropped=True,ordinary_injury_queue_unchanged=True,aslr_biases=[0,0x1000000000],binary_sha256=hashlib.sha256(binary).hexdigest(),device_runtime_tested=False)
 (ROOT/'eligibility_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
if __name__=='__main__':validate(sys.argv[1]);os._exit(0)
