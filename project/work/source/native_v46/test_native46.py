"""Exercise real v46 ARM64 entry points, native column bounds and UI recovery.

 Unity/Android rendering, allocation and managed APIs remain explicit mocks.
 In particular these tests do not claim a phone or a full Unity engine run.
"""
import csv,hashlib,io,json,struct,sys,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v45'),str(SOURCE/'native_v29')]
from native_v45 import test_native45 as old
from native_v45.assets45 import codec
from native_v46.patch_native46 import PALETTES,COLOR_GROUPS
from test_native import X,Q
from unicorn.arm64_const import UC_ARM64_REG_PC,UC_ARM64_REG_SP
for mod in [old,old.old,old.old.old,old.old.old.previous,old.old.old.previous.test_native]:mod.ROOT=ROOT
for name in ['portrait42_catalog.json','portrait43_catalog.json','selector34_options.json']:
 if not (ROOT/name).exists():shutil.copyfile(SOURCE/'native_v45'/name,ROOT/name)
class Machine(old.Machine):
 def __init__(self,raw,bias):
  super().__init__(raw,bias);self.next_scenes=[];self.shown_lists=[];self.theme_updates=[];self.fonts={};self.native_icons=[];self.panel_shows=[];self.activations=[];self.bounds_hit=False;self.safe_stop=None
  self.extra46={0x30a2278,0x2a21414,0x3089aac,0x30247c8,0x2f809bc,0xf0003010,0xf0003020,0x26ae06c,0x2f7db1c,0x2f7e424,0x2f8144c,0x2f7e530,0x2f7e5a0,0x5575728}
  for a in self.extra46:self.map(a+bias,4)
  self.controller46=self.alloc();self.hud46=self.alloc();self.dark46=self.alloc();self.list46=self.alloc();self.scenario46=self.alloc()
  self.q(self.game+0x90,self.hud46);self.q(self.hud46+0xa0,self.dark46);self.q(self.dark46+0xc8,self.list([]));self.q(self.hud46+0x60,self.list46);self.q(self.hud46+0x80,self.scenario46);self.q(self.list46+0x20,self.alloc());self.q(self.list46+0x88,self.list([]))
  self.u.mem_write(self.list46+0x80,b'\0\0')
  for off in [0x38,0x40,0x68,0x70]:
   comp=self.alloc();self.q(self.hud46+off,comp);go=comp+0x400;self.active[go]=0
  for a,n in [(0x26d3530,0x58)]:self.map(a+bias,n);self.u.mem_write(a+bias,self.load(a,n))
  self.map(0x26d3fb4+bias,4)
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if self.safe_stop is not None and va in [self.safe_stop,0x26d3fb4]:
   self.bounds_hit=va==0x26d3fb4;self.stopped=True;u.emu_stop();return
  a=[u.reg_read(r)for r in X[:5]];lr=u.reg_read(X[30]);value=0
  if va==0x3ed1638:
   path=self.str(a[0])
   if '/a16_emoji-mayo45-'not in path:
    self.native_icons.append(path);self.finish_api(lr,self.sprite(path));return
  if va==0x5577470 and a[0]==self.list46:
   self.u.mem_write(self.list46+0x81,b'\1');self.panel_shows.append(a[1]);self.finish_api(lr,1);return
  if va==0x55779e0 and a[0]==self.rq(self.list46+0x20):self.finish_api(lr,0);return
  if va not in getattr(self,'extra46',set()):return super().mock(u,pc,size,data)
  if va==0x30a2278:
   assert a[0]==self.controller46 and a[2]==0
   name=self.str(a[1]);assert name.startswith('scenario.activitiesV18.era44_')
   value=self.alloc();self.next_scenes.append((value,name))
  elif va==0x2a21414:self.q(a[0]+0x128,a[1])
  elif va==0x3089aac:
   assert a[1]==self.controller46 and a[2:5]==[0,1,0];self.shown_lists.append(self.str(a[0]))
  elif va==0x30247c8:self.fonts[a[0]]=struct.unpack('<f',u.reg_read(Q[0]).to_bytes(16,'little')[:4])[0]
  elif va==0x2f809bc:self.theme_updates.append(a[0])
  elif va==0xf0003010:value=self.rw(a[0]+0x18)
  elif va==0xf0003020:
   assert a[1]<self.rw(a[0]+0x18);value=self.rq(self.rq(a[0]+0x10)+32+a[1]*8)
  elif va==0x26ae06c:value=a[0]
  elif va==0x5575728:value=self.active.get(a[0],0)
  elif va==0x2f7db1c:value=self.alloc()
  elif va in [0x2f7e424,0x2f8144c,0x2f7e530,0x2f7e5a0]:self.activations.append((va,a[:3]))
  self.finish_api(lr,value)
 def list(self,values):
  p=super().list(values);k=self.rq(p);self.q(k+0x298,0xf0003010+self.bias);self.q(k+0x2a0,0);self.q(k+0x2e8,0xf0003020+self.bias);self.q(k+0x2f0,0);return p
 def scene(self,key):
  obj=self.alloc();self.q(obj+0x190,self.controller46)
  self.hook42('v46_bind_native_dealer_scenario',{0:obj,2:self.managed('scenario.activitiesV18.era44_'+key)})
  return obj
 def choose(self,key,index,entry=0):
  obj=self.scene(key);record=next(r for r in self.d['hooks']if r['name']=='v46_native_choice_entry_'+str(entry))
  self.execute42(record['stub'],{0:obj,1:index});return obj
 def columns(self,values):
  arr=self.alloc(32+8*len(values));self.q(arr+24,len(values))
  for n,v in enumerate(values):self.q(arr+32+8*n,self.managed(v))
  model=self.alloc();self.safe_stop=0x26d3588;self.bounds_hit=False;self.stopped=False
  for n in range(31):self.u.reg_write(X[n],0)
  self.u.reg_write(X[21],arr);self.u.reg_write(X[20],model);self.u.reg_write(UC_ARM64_REG_SP,self.heap+0x1fff000)
  self.u.emu_start(0x26d3530+self.bias,0,count=3000);assert self.stopped
  self.safe_stop=None;return self.bounds_hit,model

def validate(path):
 raw=Path(path).read_bytes();d=json.loads((ROOT/'native_hooks.json').read_text());checks=0
 def check(ok,label):
  nonlocal checks
  assert ok,label;checks+=1
 check(hashlib.sha256(raw).hexdigest()==d['binary_sha256'],'binary binding')
 decode,_=codec();assets=json.loads((ROOT/'assets.json').read_text());bad=json.loads((SOURCE/'native_v45/assets.json').read_text())
 resources={p for p,_ in json.loads(Path('analysis/base_resources.json').read_text())['m_Container']}
 for bias in [0,0x1000000000]:
  m=Machine(raw,bias);p=m.props['era44'];m.w(m.hero+32,30);p['BirthYear']=1996
  # Native first-three-column bounds checks reproduce the exact blank-row
  # IndexOutOfRange path. Positive cases include the last real appended car.
  for k in ['a16_car-models-enc','a16_house-types-enc']:
   text=decode(assets[k]);rows=text.split('\n');header=next(csv.reader([rows[0]]))
   check(not text.endswith(('\r','\n'))and all(len(next(csv.reader([r])))==len(header)for r in rows),'native CSV framing '+k)
  original=decode(bad['a16_car-models-enc']).split('\n')
  hit,_=m.columns(next(csv.reader([original[-1]]))or['']);check(hit,'negative v45 trailing-row native bounds failure')
  for row in decode(assets['a16_car-models-enc']).split('\n')[1:]:
   values=next(csv.reader([row]));hit,obj=m.columns(values)
   check(not hit and m.str(m.rq(obj+16))==values[0]and m.str(m.rq(obj+24))==values[1],'actual native model identity reads '+values[0]+' '+values[1])
  # The corrected calendar row survives a full CSV read with all choices.
  for sheet in ['genesis_activities_v18','genesis_activities_v12']:
   rr=list(csv.DictReader(io.StringIO(assets[sheet])));check(all(None not in r for r in rr),'no shifted scenario columns '+sheet)
   row=next(r for r in rr if r['ScenarioID']=='scenario.activitiesV18.era44_calendar');check(row['Choice1_Text']=='Back to the dealer'and row['TableRows'].startswith('['),'calendar routes and table remain in correct columns')
  # Real ScenarioBase choice hooks, both overloads. They use the saved native
  # owner/controller, not a global current scene string or an Android overlay.
  for year,era in [(1900,0),(1930,1),(1960,2),(2026,3)]:
   m.year45(year);m.routine42('v44_calendar_and_stock');m.choose('home',0,era%2)
   check(m.shown_lists[-1]=='genesis_v18_era44_stock'+str(era),'native current-collection click '+str(year))
   m.choose('vintage',0);check(m.shown_lists[-1]=='genesis_v18_era44_vintage'+str(era),'native vintage click')
  for n,key in [(1,'vintage'),(2,'wardrobe'),(3,'calendar')]:
   obj=m.choose('home',n);check(m.next_scenes[-1][1].endswith('_'+key)and m.rq(obj+0x128)==m.next_scenes[-1][0],'native home choice '+key)
  m.choose('wardrobe',0);check(m.shown_lists[-1]=='genesis_v18_era44_owned','owned collection native list')
  # Every visible scene button must have a real native navigation side effect.
  routes=json.loads((ROOT/'dealer_routes46.json').read_text())
  for row in routes:
   for index,label in enumerate(row['choices']):
    before=len(m.next_scenes)+len(m.shown_lists);m.choose(row['id'].rsplit('era44_',1)[1],index,index%2)
    check(len(m.next_scenes)+len(m.shown_lists)==before+1,'working native button '+label)
  for n in range(1,28):
   obj=m.alloc();m.q(obj+0x190,m.controller46)
   m.hook42('v46_bind_native_dealer_scenario',{0:obj,2:m.managed('scenario.activitiesV18.era46_item_'+str(n))})
   check(p['Selected']==n and p['ItemName']!='Choose an accessory','native item list action selects '+str(n))
  m.year45(2026);m.props['era44']['Selected']=19;m.balance=100000;obj=m.choose('item',1);check(p['Owned19']==1 and p['Head']==19 and m.balance<100000,'actual dealer click purchases and wears')
  balance=m.balance;m.choose('item',1);check(m.balance==balance,'duplicate owned purchase cannot charge again')
  m.choose('outfit1',0);check(p['Outfit1Saved']==1,'save outfit button')
  m.choose('remove',0);check(p['Head']==0,'remove headwear button')
  m.choose('outfit1',1);check(p['Head']==19,'wear saved outfit button')
  # A stale click on a replaced popup cannot spend money or navigate.
  stale=m.scene('item');m.scene('home');before=m.balance;check(m.routine42('v46_native_dealer_choice',{0:stale,1:1})==0 and m.balance==before,'stale popup choice rejected')
  # Region filtering uses the native virtual Count/Item interface and the
  # country attached to the subgroup. Deliberately poison caller x24.
  group=m.alloc();country=m.alloc();m.q(country+16,m.managed('United States'));m.q(group+0x58,country)
  original=m.list([m.managed('Phoenix'),m.managed('New York'),m.managed('Seattle'),0])
  m.w(d['states']['regions42']['va']+bias,9)
  r=next(r for r in d['hooks']if r['name']=='v46_filter_native_city_choices')
  result=m.execute42(r['stub'],{0:original,19:group,24:0x11},end=0x2faa1a8)
  expected=[v for v in m.listvalues[original]if v and m.routine42('v42_city_in_region',{0:v,1:9})]
  check(m.listvalues[result]==expected and bool(expected),'bounded region filter with actual subgroup country')
  m.q(m.rq(original+16)+24,1);result=m.execute42(r['stub'],{0:original,19:group},end=0x2faa1a8);check(result==original,'malformed list capacity preserves original fallback')
  for ptr in [0,1,0x11,0xffffffffffffffff]:check(m.routine42('v42_city_in_region',{0:ptr,1:9})==0,'invalid/null city safely rejected')
  # Assign actual packaged textures to both custom native picker headers.
  for name,icon in [('v44_starting_year_title','calendar'),('v42_regions_title','earth')]:
   group=m.alloc()
   for off in [0x38,0x60,0x68]:m.q(group+off,m.alloc())
   m.routine42(name,{0:group});check(m.rq(m.rq(group+0x60)+0x58)!=0 and m.fonts[m.rq(group+0x68)]==18,'header texture and readable caption '+icon)
  for k in ['calendar','earth','brain','eye','chart-up','flex','running-shoe','handshake','index-cards','top-hat']:
   check('emoji/normal/a16_emoji-'+k in resources,'verified existing native icon '+k)
  # Four real Unity Color return values and automatic era boundary refresh.
  for year,era in [(1900,0),(1929,0),(1930,1),(1959,1),(1960,2),(1989,2),(1990,3),(2026,3)]:
   m.year45(year);m.routine42('v46_refresh_era_theme',{0:m.hud46});check(m.rw(d['states']['ui46']['va']+bias+20)==era+1,'theme follows actual calendar')
   r=next(r for r in d['hooks']if r['name']=='v46_native_era_theme_colors')
   for group,ids in COLOR_GROUPS.items():
    m.execute42(r['stub'],{0:ids[0],1:0xffffffff})
    got=[round(struct.unpack('<f',(m.u.reg_read(Q[i])&0xffffffff).to_bytes(4,'little'))[0]*255)for i in range(4)]
    check(got==list(bytes.fromhex(PALETTES[era][group][1:]))+[255],'native theme color ABI '+group)
  # Closing menus restores position and all four native HUD groups once.
  m.routine42('v46_restore_native_hud',{0:m.hud46});check(len(m.panel_shows)==1 and len(m.activations)==4,'restore lower panel and nav, hero, toolbar, stats')
  m.routine42('v46_restore_native_hud',{0:m.hud46});check(len(m.panel_shows)==1 and len(m.activations)==4,'HUD recovery idempotent')
  # ShowLowerPanel marks itself visible before its slide finishes. A canceled
  # slide can therefore have visible=true while its real transform is hidden.
  m.w(d['states']['menu_generation41']['va']+bias,55)
  m.routine42('v46_restore_native_hud',{0:m.hud46});check(len(m.panel_shows)==2,'new close generation settles an interrupted visible=true slide')
  m.routine42('v46_restore_native_hud',{0:m.hud46});check(len(m.panel_shows)==2,'settled generation is not replayed on refresh')
  for owner,off,value in [(m.list46,0x80,1),(m.dark46,0x110,1)]:
   m.u.mem_write(owner+off,bytes([value]));before=len(m.panel_shows);m.u.mem_write(m.list46+0x81,b'\0');m.routine42('v46_restore_native_hud',{0:m.hud46});check(len(m.panel_shows)==before,'live list/transition blocks HUD restoration');m.u.mem_write(owner+off,b'\0')
 report=dict(passed=True,binary_sha256=hashlib.sha256(raw).hexdigest(),checks=checks,ASLR_bases=[0,0x1000000000],native_ScenarioBase_choice_entries_tested=True,all_dealer_buttons_navigate=True,native_car_column_bounds_negative_control=True,region_country_register_negative_control=True,native_theme_Color_ABI_checked=True,modeled_boundaries=['Unity rendering and prefab allocation','managed APIs','Genesis scenario loader/list presentation','bank adjustment'],full_Unity_engine_tested=False,physical_device_tested=False)
 (ROOT/'native46_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':validate(sys.argv[1])
