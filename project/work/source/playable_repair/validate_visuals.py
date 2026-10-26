"""Strict ARM64 resource contracts at the shipped UI consumers.

Executes original SetupScenario load/BL instructions rather than invoking an
invented bridge. Managed Resources.Load and Unity engine calls remain doubles;
this proves argument/return types and register/stack behavior, not GPU output.
"""
import csv,hashlib,io,json,struct
from pathlib import Path
from connected_life.validate_native import Machine as Previous, prior, X

class Machine(Previous):
 def __init__(self,raw,bias):
  super().__init__(raw,bias)
  off,va,n=self.d['playable_repair_rx'];self.map(va+bias,n);self.u.mem_write(va+bias,raw[off:off+n])
  self.resources={};self.resource_calls=[];self.sprite_textures={};self.kinds={};self.engine_calls=[]
  self.method_ref=self.alloc();self.method_info=self.alloc();self.map(0x5c56ad8+bias,8);self.q(0x5c56ad8+bias,self.method_ref);self.q(self.method_ref,self.method_info)
  for va in [0x2bad908,0x2bad7a8,0x3ed1638,0x553b564,0x568af7c,0x3024808,0x30223cc,0x5581f90]:self.map(va+bias,4)
  # Real CandyButton.SetColor dispatches through its own Image at +0x30.
  self.u.mem_write(0x2bad908+bias,self.load(0x2bad908,4));self.u.mem_write(0x2bad7a8+bias,self.load(0x2bad7a8,4))
  self.u.mem_write(0x30223cc+bias,self.load(0x30223cc,0x20));self.color_impl=0xfed1111+bias;self.map(self.color_impl,4)
 def resource(self,name,kind='Sprite'):
  obj=self.alloc(0x200);self.kinds[obj]=kind;self.resources[name]=obj
  if kind=='Sprite':
   texture=self.alloc(0x200);self.kinds[texture]='Texture2D';self.sprite_textures[obj]=texture
  return obj
 def image(self):
  image=self.alloc(0x200);klass=self.alloc(0x400);self.kinds[image]='Image';self.q(image,klass);self.q(klass+0x2a8,self.color_impl);self.q(klass+0x2b0,0);return image
 def mock(self,u,pc,size,data):
  va=pc-self.bias;a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
  if va in [0x2bad908,0x2bad7a8]:return # execute the actual API entry branches
  if va==0x30223cc:return # execute the actual CandyButton Image receiver dispatch
  if va==0x3ed1638:
   assert a[1]==self.method_info,'Resources.Load<Sprite> requires its MethodInfo'
   name=self.str(a[0]);obj=self.resources.get(name,0);self.resource_calls.append(name)
   # Model generic cast: a Texture2D is not a Sprite resource.
   self.finish_api(lr,obj if self.kinds.get(obj)=='Sprite'else 0);return
  if va==0x553b564:
   assert self.kinds.get(a[0])=='Sprite','Sprite.texture received a non-Sprite'
   self.engine_calls.append(('Sprite.texture',a[0]));self.finish_api(lr,self.sprite_textures[a[0]]);return
  if va==0x568af7c:
   assert self.kinds.get(a[0])=='Image'and self.kinds.get(a[1])=='Sprite','Image.set_sprite has typed receivers'
   self.engine_calls.append(('Image.set_sprite',a[0],a[1]));self.q(a[0]+0xd8,a[1]);self.finish_api(lr,0);return
  if pc==self.color_impl:
   assert self.kinds.get(a[0])=='Image';self.engine_calls.append(('Image.color',a[0]));self.finish_api(lr,0);return
  if va in [0x3024808,0x5581f90]:self.finish_api(lr,0);return
  return super().mock(u,pc,size,data)

def validate(binary,fixture,out):
 prior.ROOT=Path(fixture);raw=Path(binary).read_bytes();checks=[]
 base_assets=json.loads((Path(fixture).parent/'base_assets.json').read_text())
 authored=list(csv.DictReader(io.StringIO(base_assets['genesis_native_automatic1109'])))
 military_tag=next(r['BigImageString'] for r in authored if r['ScenarioID']=='scenario.lifeRework.native_automatic1109')
 assert military_tag=='<GFC.life_rework.MImage1109>',military_tag
 def ck(v,label):assert v,label;checks.append(label)
 for bias in [0,0x1000000000]:
  m=Machine(raw,bias);records={r['name']:r for r in m.d['routines']+m.d['hooks']}
  resolver=records['playable_owned_sprite_resource']['stub']
  owned=['native1110/photos/ww1','native1110/era/1896','native1109/flight2/0','native1111/school/01_school_menu_icons_02','native1111/school/02_school_events_07']
  for name in owned:
   sprite=m.resource(name);ck(m.execute42(0x2bad908,{0:m.managed(name)})==sprite,'actual EmojiHub Sprite API '+name)
  wrong=m.resource('native1111/wrong_type','Texture2D');ck(m.execute42(resolver,{0:m.managed('native1111/wrong_type')})==0,'Texture2D cannot pass Sprite generic cast')
  before=len(m.resource_calls);ck(m.execute42(resolver,{0:m.managed('rescue-helmet')})==0 and len(m.resource_calls)==before,'stock icons are not intercepted')
  m.props['life_rework']['NewsImage1110']='native1110/photos/ww1'
  # Execute the exact original BigImage receiver read and call in SetupScenario.
  # The native producer copies this raw string without running text interpolation.
  site=0x2f8c8e4;m.map(site+bias,0x20);m.u.mem_write(site+bias,m.load(site,0xc))
  scenario=m.alloc(0x400);token=m.managed('<GFC.life_rework.NewsImage1110>');m.q(scenario+0x40,token)
  result=m.execute42(site,{22:scenario},end=site+0xc)
  ck(result==m.sprite_textures[m.resources['native1110/photos/ww1']]and m.kinds[result]=='Texture2D','ORIGINAL BigImage consumer receives Texture2D for raw GFC tag')
  # Use the exact authored native military card's raw field, not an invented
  # MIImage alias. Emitted compare instructions and GFC key must agree with it.
  m.props['life_rework']['MImage1109']='native1109/flight2/0'
  ck(m.execute42(resolver,{0:m.managed(military_tag)})==m.resources['native1109/flight2/0'],'emitted resolver compares authored MImage1109 and reads exact GFC key')
  ck(m.execute42(resolver,{0:m.managed('<GFC.life_rework.MIImage1109>')})==0,'invented MIImage1109 alias does not resolve')
  m.q(scenario+0x40,m.managed(military_tag))
  result=m.execute42(site,{22:scenario},end=site+0xc)
  ck(result==m.sprite_textures[m.resources['native1109/flight2/0']] and m.kinds[result]=='Texture2D','ORIGINAL BigImage consumer resolves authored MImage1109 military tag')
  # Original header image path calls the same texture entry with x28.
  site=0x2f8c1f4;m.map(site+bias,0x20);m.u.mem_write(site+bias,m.load(site,0xc))
  result=m.execute42(site,{28:m.managed('native1111/school/02_school_events_07')},end=site+0xc)
  ck(m.kinds[result]=='Texture2D','ORIGINAL header image consumer receives Texture2D')
  # Exercise real CandyButton +0x30 and the real native color dispatcher.
  button=m.alloc(0x200);image=m.image();m.q(button+0x30,image)
  for off in [0x50,0x58]:m.q(button+off,0)
  m.w(m.d['states']['newlife31']['va']+bias+64,8)
  from connected_life.era_catalog import ERAS
  style=next(r for r in reversed(m.d['routines'])if r['name'].startswith('connected_style_owned_picker_buttons_1111'))
  m.execute42(style['stub'],{0:button,1:m.managed(ERAS[0][1])})
  ck(m.rq(image+0xd8)==m.resources['native1110/era/1896'],'era photo reaches audited CandyButton Image field')
  ck(any(c[0]=='Image.color'and c[1]==image for c in m.engine_calls),'actual CandyButton.SetColor dispatches to its Image')
 report=dict(passed=True,checks=len(checks),binary_sha256=hashlib.sha256(raw).hexdigest(),aslr_biases=[0,0x1000000000],original_big_image_consumer_executed=True,actual_candybutton_image_receiver_executed=True,typed_resource_negative_control=True,authored_military_image_tag=military_tag,authored_military_image_consumer_executed=True,Unity_GPU_rendering_tested=False,phone_tested=False)
 Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)

if __name__=='__main__':
 import sys
 validate(*sys.argv[1:])
