"""Execute rebuilt ARM64 paths; managed APIs are explicitly modeled boundaries."""
import csv,hashlib,io,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from native_v54 import test_native54 as prior
from test_native import X
ROOT=Path(__file__).resolve().parent

class Machine(prior.Machine):
 def __init__(self,raw,bias):
  prior.ROOT=ROOT;super().__init__(raw,bias);self.native_journal=[];self.resources55=[];self.cpu_pixels=[];self.texture55=self.alloc();self.readable55=True;self.pixels55=[0xff123456,0xffaabbcc,0xff102030,0xffa0b0c0]
  off,va,n=self.d['v55_added_rx'];self.map(va+bias,n);self.u.mem_write(va+bias,raw[off:off+n])
  for slot in [0x5c56ae0,0x5c56ad8]:
   pointer=self.alloc();value=self.alloc();self.types[slot]=value;self.map(slot+bias,8);self.q(slot+bias,pointer);self.q(pointer,value)
  self.api55={0x327d194,0x335bca4,0x5558c70,0x5557b04,0x5557b40,0x5559d18,0x223df80,0x555a078,0x555a634,0x555a4a8,0x3ed1638,0x553b564}
  for va in self.api55:self.map(va+bias,4)
  self.schema55=json.loads((ROOT/'schemas.json').read_text())
  for owner in ['f1_career','tv_host','music_studio']:
   self.ctx(owner)
   for k,r in self.schema55[owner].items():self.props[owner].setdefault(k,int(r['value'])if r['type']=='int'else r['value'])
 def mock(self,u,pc,size,data):
  va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
  if va==0x327d194:assert a[0]==self.life and a[1]==0;self.finish_api(lr,self.log);return
  if va==0x335bca4:assert a[0]==self.log and a[2]==0;self.native_journal.append(self.str(a[1]));self.finish_api(lr,0);return
  if va==0x59c70c0:
   fmt=self.cstr(a[2])
   if fmt.startswith('I '):
    vals=tuple(a[3+i]&0xffffffff for i in range(fmt.count('%d')));payload=(fmt%vals).encode();assert len(payload)<a[1];u.mem_write(a[0],payload+b'\0');self.finish_api(lr,len(payload));return
  if va==0x3059f90:
   owner=next((k for k,v in self.contexts.items()if v==a[0]),None);key=self.str(a[1])
   if owner in ['gameplay52','comments47','f1_career','tv_host','music_studio']:
    defs=self.schema55[owner];assert key in defs and defs[key]['type']=='int',(owner,key)
    r=defs[key];val=a[2]&0xffffffff;val=val if val<0x80000000 else val-0x100000000;self.props[owner][key]=max(int(r['minimum']),min(int(r['maximum']),val));self.finish_api(lr,1);return
  if va==0x5558c70:self.finish_api(lr,int(self.readable55));return
  if va in [0x5557b04,0x5557b40]:self.finish_api(lr,2);return
  if va==0x5559d18:
   p=self.alloc(48);self.q(p,self.alloc());self.q(p+24,4)
   for i,v in enumerate(self.pixels55):self.w(p+32+i*4,v)
   self.finish_api(lr,p);return
  if va==0x223df80:
   p=self.alloc(32+a[1]*4);self.q(p,a[0]);self.q(p+24,a[1]);self.finish_api(lr,p);return
  if va==0x555a078:self.finish_api(lr,0);return
  if va==0x555a634:
   assert a[2:4]==[0,0];n=self.rq(a[1]+24);self.cpu_pixels=[self.rw(a[1]+32+i*4)for i in range(n)];self.finish_api(lr,0);return
  if va==0x555a4a8:assert a[1:4]==[0,0,0];self.finish_api(lr,0);return
  if va==0x3ed1638:
   assert a[1]==self.types[0x5c56ad8];self.resources55.append(self.str(a[0]));self.finish_api(lr,self.texture55);return
  if va==0x553b564 and a[0]==self.texture55:assert a[1]==0;self.finish_api(lr,self.texture55);return
  return super().mock(u,pc,size,data)

def validate(path):
 raw=Path(path).read_bytes();d=json.loads((ROOT/'native_hooks.json').read_text());checks=[]
 def check(v,msg):assert v,msg;checks.append(msg)
 check(hashlib.sha256(raw).hexdigest()==d['binary_sha256'],'candidate hash binding')
 events=json.loads((ROOT/'receipts55.json').read_text())
 for bias in [0,0x1000000000]:
  m=Machine(raw,bias);m.w(m.hero+32,20);m.routine42('v55_append_native_life_journal',{0:m.managed('I completed a saved test activity.')});check(m.native_journal[-1]=='I completed a saved test activity.','real native life log API receives outcome')
  for owner in ['f1_career','tv_host','music_studio']:
   ev=next(e for e in events if e['owner']==owner);m.props[owner].update(Skill=61,Points=18,BonusDue=4500,Preparation=84,Episodes=2,Audience=5000,Progress=82,Quality=70,TotalReleases=1)
   prop=m.alloc();m.q(prop+24,m.managed('Receipt55'));before=len(m.native_journal)
   m.routine42('v55_successful_blueprint_receipt',{0:0,19:prop,20:ev['id'],21:m.contexts[owner]});check(len(m.native_journal)==before,'rejected setter cannot journal '+owner)
   m.routine42('v55_successful_blueprint_receipt',{0:1,19:prop,20:ev['id'],21:m.contexts[owner]});check(len(m.native_journal)==before+1 and ev['text']in m.native_journal[-1],'successful receipt records actual '+owner+' outcome')
   check(m.props['gameplay52']['ResultBody55']==m.native_journal[-1],'result panel and journal agree '+owner)
  m.props['comments47'].update(SelectedSlot=1,SelectedComment=1,SelectedId=7,PlayerName='Test Character',P1C0Count=1,P1C1Reply=0)
  for choice in range(3):
   p=m.props['comments47'];p.update(P1C0Count=1,P1C1Reply=0);before=len(m.native_journal)
   m.routine42('v55_append_real_conversation_reply',{0:choice});check(p['P1C0Count']==3 and p['P1C2Parent']==1 and p['P1C3Parent']==2,'real parent-linked reply pair '+str(choice));check(p['P1C1Reply']==choice+1 and p['P1C2Name']=='Test Character','player identity and reply flag '+str(choice));check(len(m.native_journal)==before+1,'reply is a real journal deed '+str(choice));m.routine42('v55_append_real_conversation_reply',{0:choice});check(p['P1C0Count']==3 and len(m.native_journal)==before+1,'duplicate reply blocked '+str(choice))
  p.update(P1C0Count=17,P1C1Reply=0);m.routine42('v55_append_real_conversation_reply',{0:0});check(p['P1C0Count']==17 and p['P1C1Reply']==0,'full thread preserves existing messages')
  m.prepare49();view=m.alloc();m.q(view+40,m.face)
  for ident,feature,expected in [('80000',1,0),('88800',1,0),('90005',1,0),('99999',4,0),('00123',1,1),('80000',8,1)]:
   comp=m.component[feature];entry=m.alloc();m.q(entry+16,m.managed(ident));m.q(comp+32,m.list([entry]));m.w(comp+20,0)
   got=m.hook42('v55_preserve_coloured_portrait_pixels',{0:1,19:view,25:feature});check(got==expected,'coloured-layer tint flag '+str((ident,feature)))
  def custom(name,args):return m.execute42(next(r['stub']for r in m.d['hooks']if r['name']==name),args)
  custom('v55_resize_readable_portrait_on_cpu',{1:m.texture55,2:3,3:2});check(m.cpu_pixels==[m.pixels55[0],m.pixels55[0],m.pixels55[1],m.pixels55[2],m.pixels55[2],m.pixels55[3]],'emitted bounded CPU resampler preserves exact RGBA pixels')
  for path in ['mayomods49/icons/49-priest','mayomods49/icons/49-basilica']:
   custom('v55_full_owned_image_paths',{0:m.managed(path)});check(m.resources55[-1]==path,'typed full icon path '+path)
  for alias,target in [('49-gate','seminary'),('49-conclave','conclave'),('49-pope','square'),('49-smoke','smoke'),('books','seminary')]:
   custom('v55_supplied_church_story_images',{0:m.managed('mayomods49/icons/'+alias)});check(m.resources55[-1]=='mayomods55/church/'+target,'old saved story path resolves supplied illustration '+alias)
  props=m.props['gameplay52'];props.update(ClergyInitialized54=54,ClergyRank=3,ParishFunds=0,ClergyActions=0,ClergyAge=20,ActionsUsed=0,LastAge=20);before=len(m.native_journal);m.activity(108);check(props['ClergyActions']==0 and len(m.native_journal)==before,'unfunded church choice consumes no quota and creates no deed')
  m.activity(93);check(len(m.native_journal)==before+1,'successful church study appends to the real journal');before=len(m.native_journal);m.activity(91);check(len(m.native_journal)==before,'status view is not a deed')
  print('v55 paths passed at '+hex(bias),flush=True)
 report=dict(passed=True,binary_sha256=hashlib.sha256(raw).hexdigest(),checks=len(checks),cases=checks,ASLR_bases=[0,0x1000000000],physical_phone_tested=False,ART_tested=False,Unity_rendering_tested=False,modeled_boundaries=['Managed GFC storage and API calls','Unity texture API, allocation and resource loading','LifeLog.Log native-to-managed boundary'])
 (ROOT/'native55_validation.json').write_text(json.dumps(report,indent=2)+'\n');print({'passed':True,'checks':len(checks)},flush=True)
if __name__=='__main__':
 try:validate(sys.argv[1])
 except BaseException:__import__('traceback').print_exc();sys.stdout.flush();sys.stderr.flush();__import__('os')._exit(1)
 sys.stdout.flush();sys.stderr.flush();__import__('os')._exit(0)
