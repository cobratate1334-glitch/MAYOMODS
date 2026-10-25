"""Execute candidate ARM64 with hostile managed/Unity API test doubles."""
import csv,hashlib,io,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent;sys.path[:0]=[str(SOURCE),str(SOURCE/'native_v29')]
from web_experience.validate_web import Machine as Previous,prior
from test_native import X,Q
from elftools.elf.elffile import ELFFile
class Machine(Previous):
 def __init__(self,raw,bias):
  super().__init__(raw,bias)
  off,va,n=self.d['life_rework_rx'];self.map(va+bias,n);self.u.mem_write(va+bias,raw[off:off+n])
  self.schema55['life_rework']={r['key']:r for r in csv.DictReader(io.StringIO(json.loads((prior.ROOT/'assets.json').read_text())['genesis_rework_defaults']))};self.ctx('life_rework')
  for k,r in self.schema55['life_rework'].items():self.props['life_rework'][k]=int(r['value'])if r['type']=='int'else r['value']
  self.props['life_v18']['HeightRevision1104']=0
  self.grade=[];self.fight=[];self.destroyed=set();self.texture_pixels={};self.clones=[];self.bad_copy=False
  self.extra_rework={0x2b6eb28,0x2abfe88,0x2abfe58,0x2ac4144,0x2ac418c,0x2ac41d4,0x2ac421c,0x2ac1a84,0x2c46ad0,0x557b2cc,0x2bcb384,0x2c5d484,0x2c5ca40,0x26d23a0}
  for va in self.extra_rework:self.map(va+bias,4)
  self.rankdata=self.alloc(128);self.w(self.rankdata+16,1);self.w(self.rankdata+20,1);self.w(self.rankdata+0x68,19200);self.milclass=self.alloc();self.soldier=0;self.army_enum=4;self.enlistments=0;self.enlist_model=False
  for va in [0x27fe4c4,0x27fe124,0x27fe560,0x2b6affc,0x2b6af2c,0x2b6af3c,0x2b6af5c,0x2b6af6c,0x2b6b298,0x2a7dd40,0x2b6af94,0x2b6af9c,0x2b6afac]:self.map(va+bias,4)
  self.club=self.alloc();self.stats=self.alloc();self.team=self.alloc();self.data_team=self.alloc();self.q(self.life+0x6f0,self.club);self.joined=True;self.medical=[];self.urls=[]
  self.map(0x553d724+bias,4)
 def routine42(self,name,inputs=None):
  before=getattr(self,'enlist_model',False);self.enlist_model=name=='life_rework_native_action'and(inputs or {}).get(0)==31
  try:return super().routine42(name,inputs)
  finally:self.enlist_model=before
 def mock(self,u,pc,size,data):
  va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
  if va==0x553d724:assert a[1]==0;self.urls.append(self.str(a[0]));self.finish_api(lr,0);return
  if va==0x2c38288:self.finish_api(lr,self.locations.get(a[0],self.country44));return
  if va==0x27fe4c4:assert a[1]==0;self.finish_api(lr,self.managed('Army'if a[0]==self.army_enum else'Other'));return
  if va==0x27fe124:assert a[:3]==[1,1,0];self.finish_api(lr,self.rankdata);return
  if va in [0x223e48c,0x223e490,0x223df90,0x223dfc8]and self.enlist_model:
   if va==0x223dfc8:assert self.cstr(a[2])=='SimOccupationMilitary'
   self.finish_api(lr,self.milclass);return
  if va==0x2237158 and a[0]==self.milclass:self.soldier=self.alloc(160);self.finish_api(lr,self.soldier);return
  if va==0x2b6affc:assert a[0]==self.soldier;self.w(a[0]+16,3);self.finish_api(lr,0);return
  if va in [0x2b6af2c,0x2b6af3c,0x2b6af5c,0x2b6af6c]:
   assert a[0]==self.soldier and a[2]==0;off={0x2b6af2c:0x28,0x2b6af3c:0x2c,0x2b6af5c:0x34,0x2b6af6c:0x38}[va];(self.q if off==0x38 else self.w)(a[0]+off,a[1]);self.finish_api(lr,0);return
  if va==0x27fe560:assert a[:5]==[1,1,self.army_enum,0,0];self.finish_api(lr,self.managed('Private'));return
  if va==0x2b6b298:
   assert a[0]==self.soldier and a[1]and a[2]==0;v=struct.unpack('<f',u.reg_read(Q[0]).to_bytes(16,'little')[:4])[0];assert v==19200.;u.mem_write(a[0]+20,struct.pack('<f',v));self.finish_api(lr,0);return
  if va==0x2a7dd40:
   assert a[:3]==[self.hero,self.soldier,0];assert self.rw(self.soldier+0x28)==self.army_enum and self.rw(self.soldier+0x2c)==1 and self.rw(self.soldier+0x34)==1 and self.str(self.rq(self.soldier+0x38))=='Private';self.occ=self.soldier;self.q(self.life+0x138,self.occ);self.enlistments+=1;self.finish_api(lr,0);return
  if va in [0x2b6af94,0x2b6af9c,0x2b6afac]:
   assert a[0]==self.occ
   if va==0x2b6af94:self.finish_api(lr,self.rw(a[0]+0x50));return
   self.w(a[0]+(0x50 if va==0x2b6af9c else 0x54),a[1]);self.finish_api(lr,0);return
  if va==0x3059f90:
   owner=next((k for k,v in self.contexts.items()if v==a[0]),None);key=self.str(a[1])
   if owner=='life_rework':
    s=self.schema55[owner][key];v=a[2]&0xffffffff;v=v if v<0x80000000 else v-0x100000000;self.props[owner][key]=max(int(s['minimum']),min(int(s['maximum']),v));self.finish_api(lr,1);return
  if va==0x2b6eb28:assert a[0]==self.occ and a[2]==0;self.grade.append(a[1]&0xffffffff);self.finish_api(lr,0);return
  if va==0x2abfe88:assert a[0]==self.club;self.finish_api(lr,int(self.joined));return
  if va==0x2abfe58:assert a[0]==self.club;self.finish_api(lr,self.stats);return
  if va in [0x2ac4144,0x2ac418c,0x2ac41d4,0x2ac421c,0x2ac1a84]:
   assert a[0]==self.stats and a[1]==0;v=struct.unpack('<f',u.reg_read(Q[0]).to_bytes(16,'little')[:4])[0];self.fight.append((va,v));self.finish_api(lr,0);return
  if va==0x2c46ad0:assert a[0]==self.hero;self.finish_api(lr,0);return
  if va==0x557b2cc:self.destroyed.add(a[0]);self.finish_api(lr,0);return
  if va==0x5575198 and a[1]==0:self.finish_api(lr,int(a[0]!=0 and a[0]not in self.destroyed));return
  if va==0x2f43414:
   assert a[0]==self.face+0x1000 and a[2:5]==[2,2,0];p=self.alloc();self.texture_pixels[p]=[0]*4 if self.bad_copy else [0xff123456]*4;self.clones.append(p);self.finish_api(lr,p);return
  if va==0x5559d18 and a[0]in self.texture_pixels:
   p=self.alloc(48);self.q(p,self.alloc());self.q(p+24,4);u.mem_write(p+32,struct.pack('<4I',*self.texture_pixels[a[0]]));self.finish_api(lr,p);return
  if va==0x2bcb384:assert a[0]==self.team and a[1]==0;self.finish_api(lr,self.data_team);return
  if va==0x26d23a0:assert self.str(a[0])=='sickle cell disease'and a[1]==0;self.finish_api(lr,0x123400);return
  if va==0x2c5d484:assert a[1]==0x123400;self.finish_api(lr,0);return
  if va==0x2c5ca40:assert a[1]==0x123400 and a[3]==0;self.medical.append(a[:3]);self.finish_api(lr,0);return
  return super().mock(u,pc,size,data)

def validate(binary,fixture,out):
 prior.ROOT=Path(fixture);raw=Path(binary).read_bytes();checks=[]
 def check(v,label):assert v,label;checks.append(label)
 d=json.loads((prior.ROOT/'native_hooks.json').read_text());check(d['binary_sha256']==hashlib.sha256(raw).hexdigest(),'hash binding')
 elf=ELFFile(io.BytesIO(raw));segments=[s for s in elf.iter_segments()if s['p_type']=='PT_LOAD'];check(all(s['p_flags']&3!=3 for s in segments),'no writable executable segment');check(all(s['p_offset']%0x4000==s['p_vaddr']%0x4000 for s in segments),'16KB ELF alignment')
 for bias in [0,0x1000000000]:
  m=Machine(raw,bias)
  for style,start in enumerate(__import__('life_rework.era_genetics',fromlist=['STARTS']).STARTS):
   for y in [1900,1940,1960,1980,2000,2010,2020]:check(m.routine42('life_rework_hair_available_in_year',{0:style,1:y})==int(y>=start),'era hair '+str((style,y)))
  m.student(1,age=15);m.routine42('life_rework_native_action',{0:11});check(m.grade==[5],'exam modifies native student grades');m.w(m.hero+32,25);m.routine42('life_rework_native_action',{0:21});check(m.fight==[(0x2ac421c,3.0),(0x2ac41d4,2.0)],'camp calls native technique/agility with FLOAT ABI')
  m.w(m.hero+32,4);m.routine42('life_rework_native_action',{0:22});check(len(m.fight)==2,'child camp command rejected at native boundary')
  for index in [1016,2020,5001,6100,7031]:
   m.w(m.data_team+16,index);r=next(r for r in m.d['hooks']if r['name']=='life_rework_real_team_badges');value=m.execute42(r['stub'],{0:m.team});check(m.str(value)=='mayomods1104/teams/'+str(index),'real badge by stable team index')
  community=m.alloc(128);m.w(community+0x44,0);r=next(r for r in m.d['hooks']if r['name']=='life_rework_home_community_opens_reddit');m.execute42(r['stub'],{0:community});check(m.urls==['https://www.reddit.com/r/BitlifeModdingScene/'],'original community CTA opens requested subreddit')
  texture=m.alloc();copy_=m.routine42('life_rework_validated_header_texture',{0:texture});check(copy_!=texture and copy_ in m.texture_pixels,'header owns a distinct validated copy');m.destroyed.add(texture);again=m.routine42('life_rework_validated_header_texture',{0:texture});check(again==copy_ and again not in m.destroyed,'destroying shared cache preserves header pixels');m.bad_copy=True;again=m.routine42('life_rework_validated_header_texture',{0:m.alloc()});check(again==copy_ and m.clones[-1]in m.destroyed,'black replacement rejected and destroyed');m.life_id='new-life';again=m.routine42('life_rework_validated_header_texture',{0:0});check(again==0,'no old-life portrait fallback');m.bad_copy=False;m.routine42('life_rework_validated_header_texture',{0:m.alloc()});check(copy_ in m.destroyed,'old owned texture disposed on life switch')
  m.w(m.hero+32,20);m.props['era44']['BirthYear']=1924;m.country(m.hero,'United States');m.routine42('life_rework_refresh_context');check(m.props['life_rework']['War']==2 and 'Normandy'in m.props['life_rework']['Front'],'1944 American Normandy context');m.props['era44']['BirthYear']=1924;m.country(m.hero,'Switzerland');m.routine42('life_rework_refresh_context');check(m.props['life_rework']['WarSide']==0,'neutral country cannot be drafted')
  m.props['life_rework'].update(War=2,WarSide=1,DraftAge=-1);m.w(m.hero+32,25);m.w(m.occ+16,0);m.routine42('life_rework_native_action',{0:31});check(m.enlistments==1 and m.props['life_rework']['Deployed']==1,'enlistment initializes actual branch, status, rank, title, country salary and native occupation');check(m.rw(m.occ+0x50)==1,'native deployment count increments');m.routine42('life_rework_native_action',{0:31});check(m.enlistments==1 and m.rw(m.occ+0x50)==1,'same-age call-up cannot duplicate service');m.w(m.hero+32,4);m.props['life_rework']['DraftAge']=-1;m.routine42('life_rework_native_action',{0:31});check(m.enlistments==1,'child cannot enlist through native command')
  m.w(m.hero+32,25);m.props['era44']['BirthYear']=1900-25;bank=m.balance;joined=m.props['roblox_social']['Joined'];m.command(1);check(m.balance==bank and m.props['roblox_social']['Joined']==joined and m.rw(m.web+28)==5,'open website cannot mutate a life before 2006')
  for year in [1900,1940,1960,1980,2000,2010,2020]:
   m.props['era44']['BirthYear']=year-25;m.routine42('v44_calendar_and_stock');check(str(year)[:3]in m.props['era44']['EraName'],'seven era labels follow calendar');check(m.props['era44']['Available27']==0 if year<2000 else True,'snapbacks unavailable before 2000')
  npc=m.alloc(256);script=m.alloc(256);m.w(npc+32,12)
  def mixed(n):
   n=((n^(n>>16))*0x7feb352d)&0xffffffff;n=((n^(n>>15))*0x846ca68b)&0xffffffff;return (n^(n>>16))&0x7fffffff
  for i in range(20000):
   name='Classmate '+str(i);v=5381
   for ch in name:v=(v*33+ord(ch))&0xffffffff
   if mixed(v)%400==0:break
  m.people[npc]=name;check(m.routine42('v52_person_seed',{0:npc})%400==0,'stable native seed selects health variation');m.hook42('life_rework_npc_native_genetic_condition',{19:npc,20:script});check(m.medical[-1]==[script,0x123400,12],'condition uses actual NPC script, disease object and age');before=len(m.medical);m.w(npc+32,2);m.hook42('life_rework_npc_native_genetic_condition',{19:npc,20:script});check(len(m.medical)==before,'young child excluded by native condition age boundary')
  # Exercise the actual country/parent projection, not a copy of its formula.
  from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
  ins=next(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(m.load(0x2c42454,4),0x2c42454));genderoff=int(ins.op_str.split('#')[1].split(']')[0],0)
  father=m.alloc(256);mother=m.alloc(256);m.q(m.life+0xa8,father);m.q(m.life+0xb8,mother);m.w(father+32,42);m.w(mother+32,39);m.w(father+24,1);m.w(mother+24,1);m.w(father+genderoff,0);m.w(mother+genderoff,1)
  heights=[]
  for i,country in enumerate(['Netherlands','Nepal','United States','Japan']*3):
   m.people.update({m.hero:'Child '+str(i),father:'Father '+str(i),mother:'Mother '+str(i)});m.country(m.hero,country);m.country(father,country);m.country(mother,country);m.w(m.hero+genderoff,i%2);m.w(m.hero+32,20);m.props['era44']['BirthYear']=1996;m.props['life_v18'].update(HeightSource51=1,HeightRevision1104=0,HeightModel52=52,AdultHeight=179)
   m.routine42('life_rework_finalize_live_family_height');height=m.props['life_v18']['AdultHeight'];heights.append(height);check(120<=height<=250 and m.props['life_v18']['HeightRevision1104']==1104,'live parent/country height is finalized once')
   m.routine42('life_rework_finalize_live_family_height');check(m.props['life_v18']['AdultHeight']==height,'height stable on repeated header refresh')
  check(len(set(heights))>=7,'varied countries, parents and birth sex do not all become 179 cm')
  m.props['life_v18'].update(HeightSource51=2,HeightRevision1104=0,AdultHeight=194);m.routine42('life_rework_finalize_live_family_height');check(m.props['life_v18']['AdultHeight']==194,'explicitly selected height preserved')
  print('Executed rework ARM64',hex(bias),flush=True)
 report=dict(passed=True,checks=len(checks),binary_sha256=hashlib.sha256(raw).hexdigest(),managed_APIs_modeled=True,Unity_rendering_tested=False,ART_tested=False,phone_tested=False);Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
