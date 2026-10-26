"""Execute emitted native presentation boundaries with explicit Unity API doubles."""
import hashlib,json,sys,struct
from pathlib import Path
from military_expansion.validate_native import Machine as Previous,prior,X
from native_immersion.protocol import BOX,FIELDS,KEYS

class Machine(Previous):
 def __init__(self,raw,bias):
  super().__init__(raw,bias);off,va,n=self.d['native_immersion_rx'];self.map(va+bias,n);self.u.mem_write(va+bias,raw[off:off+n]);self.box=self.alloc(0x16c000);self.shown_pages=[];self.sprites={};self.image_changes=[];self.background_colors=[];self.intercept_backend=False;self.root_list=[];self.upload_mode=False;self.loaded_images=[];self.upload_exception=False
  for address in [0x568af7c,0x30274b0,0x223df5c,0x223df7c,0x3089aac,0x308480c]:self.map(address+bias,4)
 def mock(self,u,pc,size,data):
  va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
  if getattr(self,'backend_packet',None) is not None and va==next(r['stub']for r in self.d['routines']if r['name']=='persist_new_life_checkpoint23'):
   self.backend_calls.append(a[0]);values,kind=self.backend_packet;serial=self.rw(self.box+8)+1
   for i,text in enumerate(values):u.mem_write(self.box+FIELDS-BOX+i*8192,text.encode('utf-16-le')+b'\0\0')
   self.put_text(11,'v=1&stage=1');self.put_text(12,'');self.put_text(13,'I registered at the service desk.')
   self.w(self.box+144,serial);self.w(self.box+148,kind);self.w(self.box+12,1);self.w(self.box+4,serial)
   self.finish_api(lr,0);return
  if va==0x223df5c:self.upload_mode=True;self.finish_api(lr,1);return
  if self.upload_mode and va==0x223dfc8:
   self.finish_api(lr,2);return
  if self.upload_mode and va==0x223df7c:
   arr=self.alloc(a[1]+64);self.q(arr+24,a[1]);self.finish_api(lr,arr);return
  if self.upload_mode and va in [0x223e490,0x223df90,0x223dff0]:
   if va==0x223dff0:assert self.cstr(a[1])=='LoadImage'and a[2]==3
   self.finish_api(lr,self.png_method);return
  if self.upload_mode and va==0x223e8b0:
   self.upload_mode=False;texture=self.rq(a[2]);arr=self.rq(a[2]+8);self.loaded_images.append((texture,bytes(u.mem_read(arr+32,self.rq(arr+24)))))
   assert self.rw(self.rq(a[2]+16))==0
   if self.upload_exception:self.q(a[3],123)
   self.finish_api(lr,0);return
  if va==0x553b564 and hasattr(self,'live_texture'):self.finish_api(lr,self.live_texture);return
  if va==0x3ed1638:
   name=self.str(a[0]);self.finish_api(lr,self.sprites.get(name,0));return
  if va==0x568af7c:self.image_changes.append((a[0],a[1]));self.q(a[0]+0xd8,a[1]);self.finish_api(lr,0);return
  if va==0x30274b0:
   import unicorn.arm64_const as R
   self.background_colors.append([struct.unpack('<f',int(u.reg_read(getattr(R,'UC_ARM64_REG_Q'+str(i)))).to_bytes(16,'little')[:4])[0]for i in range(4)]);self.finish_api(lr,0);return
  if va==0x3089aac:self.root_list.append((self.str(a[0]),a[1]));self.finish_api(lr,0);return
  if va==0x308480c:self.shown_pages.append(self.str(a[0]));self.finish_api(lr,0);return
  return super().mock(u,pc,size,data)
 def project(self,values,kind,serial=1):
  for i,text in enumerate(values):self.u.mem_write(self.box+FIELDS-BOX+i*8192,text.encode('utf-16-le')+b'\0\0')
  self.w(self.box+144,serial);self.w(self.box+148,kind);self.w(self.box+8,serial);self.w(self.box+28,1)

def validate(binary,fixture,out):
 prior.ROOT=Path(fixture);raw=Path(binary).read_bytes();checks=[]
 def ck(test,label):assert test,label;checks.append(label)
 for bias in [0,0x1000000000]:
  m=Machine(raw,bias);st=m.d['states']['native_immersion']['va']+bias
  fields=['World news','World War II begins','1 September 1939<br><br>Germany invades Poland.','native1109/news/ww2','Continue','Draft & service','','']
  m.project(fields,2);m.routine42('immersion1109_apply_projection')
  ck(all(m.props['life_rework'][k]==v for k,v in zip(KEYS,fields)),'all native fields bind exact text/labels '+str(bias))
  ck(m.rw(st+8)==2 and m.rw(m.box+172)==1,'projection published only after game acknowledgement')
  before=dict(m.props['life_rework']);m.w(m.box+144,2);m.w(m.box+148,4);m.routine42('immersion1109_apply_projection');ck(before==m.props['life_rework'],'unacknowledged projection cannot overwrite visible labels')
  m.w(m.box+8,2);m.w(m.box+28,3);m.routine42('immersion1109_apply_projection');ck(before==m.props['life_rework'],'rejected life transaction cannot publish stale controls')
  # Full original Load handoff calls the headless data engine synchronously,
  # then commits and publishes only after the Unity mailbox acknowledgement.
  m.backend_packet=(fields,2);m.backend_calls=[];m.year45(1940,25);m.w(m.hero+32,25)
  before_journal=len(m.native_journal);m.routine42('immersion1109_prepare_native_page',{0:10,1:1})
  ck(m.backend_calls==[2310],'native UI boundary calls headless data preparation synchronously')
  ck(m.rw(m.box+8)==1 and m.rw(m.box+172)==1,'same native boundary acknowledges before presenting')
  ck(m.props['life_rework']['MilitaryState1108']=='v=1&stage=1'and len(m.native_journal)==before_journal+1,'native preparation saves actual Life and journals once')
  m.backend_packet=None
  # Journal illustration owns an existing Image, restoring its original Sprite.
  log=m.alloc();scroller=m.alloc();image=m.alloc(512);original=m.alloc();m.q(log+0x30,scroller);m.q(scroller+0x30,image);m.q(image+0xd8,original)
  phase=m.d['states']['military_expansion']['va']+bias+64
  sprites=[m.alloc()for _ in range(4)];m.sprites.update({'native1109/background/'+n:p for n,p in zip(['ww1','post1','ww2','post2'],sprites)})
  for i,sprite in enumerate(sprites,1):
   m.w(phase,i);m.hook42('immersion1109_native_journal_background',{19:log});ck(m.image_changes[-1]==(image,sprite),'native log uses correct illustration phase '+str(i));ck(abs(m.background_colors[-1][3]-.3)<.001 and m.background_colors[-1][:3]==[1.,1.,1.],'art uses readable alpha and original colors')
  m.w(phase,0);m.hook42('immersion1109_native_journal_background',{19:log});ck(m.image_changes[-1]==(image,original),'ordinary year restores actual original background Sprite')
  m.w(phase,1);m.sprites.clear();m.hook42('immersion1109_native_journal_background',{19:log});ck(m.image_changes[-1]==(image,original),'missing artwork falls back to original background')
  # LoadImage is invoked with a managed exception slot and a private texture.
  live_sprite=m.alloc();live_texture=m.alloc();m.sprites['native1109/live']=live_sprite
  # Existing Sprite.texture getter is modeled by the retained image registry.
  m.live_texture=live_texture
  payload=b'PNG-only-owned-texture';m.u.mem_write(m.box+0xe0000-BOX,payload);m.w(m.box+160,1);m.w(m.box+164,len(payload));m.w(m.box+8,1)
  m.routine42('immersion1109_upload_owned_image');ck(m.loaded_images[-1]==(live_texture,payload),'private dynamic image uses bounded byte array and correct texture');ck(m.rw(m.box+164)==0,'successful owned image consumes its pending bytes')
  m.upload_exception=True;m.w(m.box+164,len(payload));m.routine42('immersion1109_upload_owned_image');ck(m.rw(m.box+164)==len(payload),'managed image exception is contained without publishing success')
  # Native aircraft animation is armed for its own texture only. The normal
  # Unity component owns playback; no Android scene or polling loop is used.
  m.w(m.box+148,66);m.props['life_rework']['MImage1109']='native1109/flight1/0';flight_sprite=m.alloc();m.sprites['native1109/flight1/0']=flight_sprite
  m.routine42('immersion1109_prepare_native_flight');animation=st+512
  ck(m.rw(animation)==1 and m.rq(animation+8)!=0,'native aircraft sequence arms the first-frame texture')
  ck(m.str(m.handles[m.rq(animation+24)])=='native1109/flight1/','native animator retains the correct era prefix')
  m.w(m.box+148,2);m.routine42('immersion1109_prepare_native_flight');ck(m.rw(animation)==0 and m.rq(animation+8)==0,'reduced-motion/static page cannot start aircraft animation')
  # Root is a Genesis list and invalidates the temporary ScenarioBase before
  # LoadScenario checks IsValidForPresentation. No empty dialog is constructed.
  scenario=m.alloc(512);controller=m.alloc();m.w(st+8,128);m.hook42('immersion1109_bind_original_scenario',{0:scenario,1:controller,2:m.managed('scenario.lifeRework.native_automatic1109')});ck(m.root_list[-1]==('genesis_military1108',controller)and m.rw(scenario+0x180)==0,'root redirects to original list without blank card')
  # A full popup ID resolves to a template that exists in the same controller.
  m.w(st+8,2);m.props['life_rework']['MImage1109']='native1109/news/ww2';m.hook42('immersion1109_bind_original_scenario',{0:scenario,1:controller,2:m.managed('scenario.lifeRework.native_automatic1109')});ck(m.str(m.u.reg_read(X[2]))=='scenario.lifeRework.native_panel2image1109','dynamic original popup selects matching two-button image template')
 report=dict(passed=True,checks=len(checks),binary_sha256=hashlib.sha256(raw).hexdigest(),ARM64_executed=True,managed_Unity_APIs_modeled=True,ART_tested=False,Unity_rendering_tested=False,phone_tested=False);Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
