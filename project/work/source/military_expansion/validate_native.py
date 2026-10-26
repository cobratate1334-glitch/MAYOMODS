"""Execute actual identity, persistence and equipment ARM64, with typed API doubles."""
import hashlib,json,struct,sys
from pathlib import Path
from ui_integrity.validate_native import Machine as Previous,prior,X
from unicorn.arm64_const import UC_ARM64_REG_Q0
from military_expansion.jni import BOX,TEXT,PNG

class Machine(Previous):
 def __init__(self,raw,bias):
  super().__init__(raw,bias);off,va,n=self.d['military_expansion_rx'];self.map(va+bias,n);self.u.mem_write(va+bias,raw[off:off+n]);self.box=self.alloc(0xb5000);self.injected=[];self.stat_people=[];self.encode_calls=[];self.encode_size=11;self.png_lookup=False;self.png_exception=False;self.png_method=self.alloc()
  for va in [0x2c42324,0x2c423d4,0x2c42384,0x2c422f4,0x2c42304,0x223df64,0x2a27240,0xfad1108]:self.map(va+bias,4)
 def mock(self,u,pc,size,data):
  va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
  if va==getattr(self,'resolve',0)and self.cstr(a[0])=='mayo_military':self.finish_api(lr,self.box);return
  if va==0x30611d0 and getattr(self,'capture_menu',False):self.injected.append((a[0],self.str(a[1])));self.finish_api(lr,0);return
  if va in [0x2c42324,0x2c423d4,0x2c42384,0x2c422f4,0x2c42304]:
   value={0x2c42324:76,0x2c423d4:63,0x2c42384:84,0x2c422f4:80,0x2c42304:70}[va];self.stat_people.append(a[0]);self.finish_api(lr,0);u.reg_write(UC_ARM64_REG_Q0,int.from_bytes(struct.pack('<f',value)+b'\0'*12,'little'));return
  if va==0x2a27240:self.finish_api(lr,self.managed('London'));return
  if va==0x223e490 and self.cstr(a[1])=='UnityEngine.ImageConversionModule':self.png_lookup=True;self.finish_api(lr,self.png_method);return
  if self.png_lookup and va in [0x223df90,0x223dfc8,0x223dff0]:
   if va==0x223dfc8:assert self.cstr(a[1])=='UnityEngine'and self.cstr(a[2])=='ImageConversion'
   if va==0x223dff0:assert self.cstr(a[1])=='EncodeToPNG'and a[2]==1
   self.finish_api(lr,self.png_method);return
  if va==0x223e8b0 and a[0]==self.png_method:
   assert a[1]==0;self.png_lookup=False
   if self.png_exception:self.q(a[3],123);self.finish_api(lr,0);return
   a[0]=self.rq(a[2])
   self.encode_calls.append(a[0]);arr=self.alloc(64);self.q(arr+24,self.encode_size);u.mem_write(arr+32,b'live-face!!');self.finish_api(lr,arr);return
  return super().mock(u,pc,size,data)
 def put_text(self,index,value):self.u.mem_write(self.box+TEXT[index]-BOX,value.encode('utf-16-le')+b'\0\0')
 def text(self,index):
  p=self.box+TEXT[index]-BOX;raw=bytearray()
  while True:
   b=bytes(self.u.mem_read(p,2));p+=2
   if b==b'\0\0':return raw.decode('utf-16-le')
   raw+=b

def validate(binary,fixture,out):
 prior.ROOT=Path(fixture);raw=Path(binary).read_bytes();checks=[]
 def check(ok,msg):assert ok,msg;checks.append(msg)
 for bias in [0,0x1000000000]:
  m=Machine(raw,bias);state=m.d['states']['military_expansion']['va']+bias
  father=m.person('Michael Roberts',61,0);mother=m.person('Ava Roberts',57,1);other=m.person('Other preview',33,0);m.q(m.life+0xa8,father);m.q(m.life+0xb8,mother)
  closure=m.alloc();m.q(closure+16,father);menu=m.alloc();m.capture_menu=True;m.hook42('military1108_parent_role_menu',{19:menu,20:closure});m.capture_menu=False
  check(m.injected[-1]==(menu,'FatherStory1108'),'actual parent closure injects father-bound action')
  m.routine42('relationship34_capture_menu_person',{0:other,1:0});m.routine42('selected_relationship_details21',{0:other,1:0});check(m.props['relationship21']['SelectedAge1106']==33,'negative control: shared preview cache can be overwritten')
  m.hook42('military1108_resolve_bound_parent',{2:m.managed('scenario.lifeRework.parent_01108')})
  r=m.props['relationship21'];check(r['SelectedAge1106']==61 and r['SelectedName1106']=='Michael Roberts','father page resolves actual father despite different preview');check(r['Discipline1108']==76 and father in m.stat_people and r['ParentCharacter1108'].startswith('Focused'),'personality uses selected native attributes')
  m.q(closure+16,mother);m.capture_menu=True;m.hook42('military1108_parent_role_menu',{19:menu,20:closure});m.capture_menu=False;check(m.injected[-1][1]=='MotherStory1108','mother has an independent binding')
  m.hook42('military1108_resolve_bound_parent',{2:m.managed('scenario.lifeRework.parent_11108')});check(r['SelectedName1106']=='Ava Roberts'and r['SelectedAge1106']==57,'mother page is not father or player')
  m.w(mother+24,0);m.hook42('military1108_resolve_bound_parent',{2:m.managed('scenario.lifeRework.parent_11108')});check('have died'in r['ParentAvailability1108']and r['SelectedName1106']=='Ava Roberts','deceased parent retains own record')
  previous_hero=m.hero;new_hero=m.person('Another life',25,0);m.q(m.game+0x28,new_hero);m.hook42('military1108_resolve_bound_parent',{2:m.managed('scenario.lifeRework.parent_01108')});check(r['SelectedName1106']=='Parent record unavailable','old parent callback rejected after hero replacement');m.q(m.game+0x28,previous_hero)
  # Pre-entry US induction uses the exact native object constructor, not the
  # old generic campaign action that incremented deployment immediately.
  m.w(m.hero+32,25);m.country(m.hero,'United States');m.year45(1940,25);m.props['life_rework'].update(WarSide=0,DraftAge=25);m.enlist_model=True
  m.execute42(next(r['stub']for r in m.d['routines']if r['name']=='military1108_construct_native_service_once'))
  check(m.enlistments==1 and m.rw(m.occ+16)==3,'1940 US pre-entry induction creates actual native military post');check(m.rw(m.occ+0x50)==0,'induction does not increment deployment');m.execute42(next(r['stub']for r in m.d['routines']if r['name']=='military1108_construct_native_service_once'));check(m.enlistments==1,'existing military post is not duplicated');m.enlist_model=False
  m.routine42('military1108_snapshot');check(m.rw(m.box+32)==1940 and m.rw(m.box+36)==25 and m.rw(m.box+44)==1,'snapshot uses actual reached year, age and occupation: '+str([m.rw(m.box+x)for x in [32,36,44]]));token=m.routine42('web_current_life_token');m.q(m.box+16,token);m.w(m.box,8);m.w(m.box+24,1);m.w(m.box+4,1);m.w(m.box+8,0);m.w(m.box+12,1)
  m.w(m.box+24,0);m.put_text(11,'v=1&stage=5');m.put_text(12,'v=1&moves=e2e4');m.put_text(13,'I wrote home from training.');before=len(m.native_journal);m.routine42('military1108_execute_mailbox')
  check(m.props['life_rework']['MilitaryState1108']=='v=1&stage=5'and m.props['life_rework']['ChessState1108']=='v=1&moves=e2e4','frame commits both actual life strings');check(m.rw(m.box+8)==1 and len(m.native_journal)==before+1,'already submitted action commits once after window closes');m.routine42('military1108_execute_mailbox');check(len(m.native_journal)==before+1,'same request cannot journal twice')
  m.w(m.box+4,2);m.q(m.box+16,token+1);m.put_text(11,'SHOULD NOT SAVE');m.routine42('military1108_execute_mailbox');check(m.props['life_rework']['MilitaryState1108']=='v=1&stage=5'and m.rw(m.box+28)==3,'stale life token rejected before mutation')
  # Equipment display exports the same validated texture, copying bytes only.
  face=m.alloc();handle=0x100000123;m.handles[handle]=face;portrait=m.d['states']['life_rework']['va']+bias;m.q(portrait+16,token);m.q(portrait+8,handle);m.routine42('military1108_copy_live_face');check(m.encode_calls[-1]==face and m.rw(m.box+72)==11,'equipment export uses current owned native face');check(bytes(m.u.mem_read(m.box+PNG-BOX,11))==b'live-face!!','portrait bytes copied into bounded independent mailbox');m.png_exception=True;m.routine42('military1108_copy_live_face');check(m.rw(m.box+72)==0,'managed PNG exception caught without changing portrait');m.png_exception=False;m.encode_size=0x80001;m.routine42('military1108_copy_live_face');check(m.rw(m.box+72)==0,'oversize face copy rejected')
  # Temporary theme restores by recomputation, not editing Config.ThemeName.
  for year,want,side,country in [(1915,1,1,'United Kingdom'),(1918,2,1,'United Kingdom'),(1919,2,0,'United Kingdom'),(1940,3,1,'United Kingdom'),(1945,4,1,'United Kingdom'),(1946,4,0,'United Kingdom'),(2026,0,0,'United Kingdom'),(1940,0,0,'Switzerland'),(1940,3,1,'United Kingdom')]:
   m.year45(year);m.country(m.hero,country);m.q(m.locations.get(m.hero,m.country44)+0x90,m.managed('ch' if country=='Switzerland' else 'gb'));m.props['life_rework'].update(Year=year,WarSide=side,Country=country);m.routine42('military1108_refresh_theme',{0:m.hud46});check(m.rw(state+64)==want,'native temporary phase '+str((year,country)))
  for reached,want in [(1917,1),(1918,0),(1939,2),(1945,0)]:
   m.year45(reached,25);m.country(m.hero,'United Kingdom');m.routine42('life_rework_refresh_context');check(m.props['life_rework']['War']==want,'retained native combat follows annual ceasefire '+str(reached))
  print('Military native checks passed at',hex(bias),flush=True)
 report=dict(passed=True,checks=len(checks),binary_sha256=hashlib.sha256(raw).hexdigest(),ARM64_executed=True,managed_Unity_APIs_modeled=True,ART_tested=False,Unity_rendering_tested=False,phone_tested=False);Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
