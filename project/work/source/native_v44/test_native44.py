"""Execute the v44 ARM64 bridges at two load addresses.

Genesis storage/string APIs, the game's bank adjustment and native accessory
collection calls are hostile ABI boundaries. All v44 branches execute in ARM64.
"""
import hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v43'),str(SOURCE/'native_v42'),str(SOURCE/'native_v34'),str(SOURCE/'native_v29')]
from native_v43 import test_native43 as old
from test_native import X,Q
from catalog44 import ITEMS,START_YEARS,offer
old.ROOT=ROOT;old.previous.ROOT=ROOT;old.previous.test_native.ROOT=ROOT

class Machine(old.Machine):
 def __init__(self,raw,bias):
  super().__init__(raw,bias);self.acc={};self.debits=[];self.finances=self.alloc();self.q(self.life+0xe8,self.finances);self.balance=10000
  self.country44=self.alloc();self.q(self.country44+0x90,self.managed('United States'))
  self.new44={0x2c38288,0x2f36824,0x2f36ae4,0x2a6eb5c,0x5584430}
  for a in self.new44:self.map(a+bias,4)
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if va not in getattr(self,'new44',set()):return super().mock(u,pc,size,data)
  a=[u.reg_read(r)for r in X[:4]];lr=u.reg_read(X[30]);value=0
  if va==0x2c38288:value=self.country44
  elif va==0x2f36824:value=self.acc.get((a[0],a[1]),0)
  elif va==0x2f36ae4:
   assert a[0]==self.face and a[1]in [0,6,7]and a[3]==0,(a,'accessory native arguments')
   self.acc[(a[0],a[1])]=a[2]
  elif va==0x2a6eb5c:
   amount=struct.unpack('<d',u.reg_read(Q[0]).to_bytes(16,'little')[:8])[0]
   assert a[0]==self.finances and a[1]==0 and amount<0
   self.debits.append(amount);self.balance+=amount
  elif va==0x5584430:
   assert 8<=a[1]<=15 and a[2]==0
   self.actions.append(('index',a[:3]))
  self.finish_api(lr,value)
 @property
 def balance(self):return struct.unpack('<d',self.u.mem_read(self.finances+0x10,8))[0]
 @balance.setter
 def balance(self,v):self.u.mem_write(self.finances+0x10,struct.pack('<d',v))
 def action(self,value):
  self.props['era44']['Action']=value
  self.run('Action',value,'era44')
  return self.props['era44']

def validate(path,before):
 raw=Path(path).read_bytes();base=Path(before).read_bytes();d=json.loads((ROOT/'native_hooks.json').read_text());checks=0
 def check(ok,label):
  nonlocal checks
  assert ok,label;checks+=1
 check(hashlib.sha256(raw).hexdigest()==d['binary_sha256'],'binary binding')
 check(hashlib.sha256(base).hexdigest()==d['base_v43_sha256'],'base binding')
 for bias in [0,0x1000000000]:
  m=Machine(raw,bias);p=m.props['era44'];state=d['states']['era44']['va']+bias
  for age in [0,20,150]:
   p['BirthYear']=0;m.w(m.hero+32,age);m.action(1)
   check(p['Year']==2026 and p['BirthYear']==2026-age,'existing save calendar migration')
   m.w(m.hero+32,age+1);m.action(1);m.action(1)
   check(p['Year']==2027,'age and repeated refresh do not double count')
  for year,era in [(1900,0),(1929,0),(1930,1),(1959,1),(1960,2),(1989,2),(1990,3),(2026,3)]:
   m.w(m.hero+32,30);p['BirthYear']=year-30;m.action(1)
   check(p['Year']==year and p['Era']==era,'era boundary '+str(year))
   for i in ITEMS:
    available,price=offer(i,year,30,True)
    check((p['Available'+str(i['id'])],p['Price'+str(i['id'])])==(available,price),'stock/price boundary '+str(year)+'/'+str(i['id']))
  m.w(m.hero+32,30);p['BirthYear']=1996;m.q(m.country44+0x90,m.managed('France'));m.action(1)
  check(p['Regional']==0 and p['Available13']==0 and p['Available15']==0,'country excludes regional hats')
  m.q(m.country44+0x90,m.managed('Australia'));m.action(1)
  check(p['Regional']==1 and p['Available13']==1 and p['Available15']==1,'Australian cowboy collection')
  m.action(119);price=p['Price'];m.balance=price-1;before_debits=len(m.debits);m.action(2)
  check(p['Owned19']==0 and p['BuyStatus']==4 and len(m.debits)==before_debits and m.balance==price-1,'insufficient funds atomic failure')
  m.balance=price;m.action(2)
  check(p['Owned19']==1 and p['Head']==19 and m.balance==0 and m.acc[(m.face,6)]==44019,'exact balance purchase equips actual portrait')
  count=len(m.debits);m.action(2);m.action(2)
  check(len(m.debits)==count and p['Owned19']==1,'repeated purchase cannot charge twice')
  m.action(601);m.action(400);check(p['Head']==0 and m.acc[(m.face,6)]==0,'unequip clears native mod layer')
  m.action(611);check(p['Head']==19 and m.acc[(m.face,6)]==44019,'saved outfit restores')
  old_head=p['Head'];m.action(612);check(p['Head']==old_head,'empty outfit cannot erase outfit')
  m.action(116);before_debits=len(m.debits);m.action(2)
  check(p['BuyStatus']==3 and len(m.debits)==before_debits,'unavailable vintage stock cannot charge')
  m.w(m.hero+32,17);p['BirthYear']=2009;m.action(101);m.action(2)
  check(p['Owned1']==0 and p['BuyStatus']==3,'minor cannot purchase mouth item')
  # Purchase every original and new design in its original collection.
  m.w(m.hero+32,30);m.q(m.country44+0x90,m.managed('United States'))
  for item in ITEMS:
   p['BirthYear']=[1900,1930,1960,2026][item['era']]-30;m.balance=100000
   m.action(100+item['id']);before_balance=m.balance;owned=p['Owned'+str(item['id'])];price=p['Price'];m.action(2)
   check(p['Owned'+str(item['id'])]==1 and m.balance==before_balance-(0 if owned else price),'purchase '+item['name'])
   slot='Mouth'if item['slot']=='Mouth'else'Head';native=7 if slot=='Mouth'else 6
   check(p[slot]==item['id']and m.acc[(m.face,native)]==44000+item['id'],'native equip '+item['name'])
  # Older owned pieces are wearable regardless of the current stock rotation.
  p['BirthYear']=1996;m.action(109);m.action(3)
  check(p['Head']==9 and p['Owned9']==1,'owned vintage top hat survives era change')
  p['Outfit1Head']=9;p['Outfit1Mouth']=17;p['Outfit1Saved']=1;m.action(611)
  check(m.acc[(m.face,6)]==44009 and m.acc[(m.face,7)]==44017,'independent simultaneous slots')
  # A free preview changes only the displayed layer; canonical serialization
  # restores owned slots, and reopening the image restores the preview.
  m.action(119);saved_head=p['Head'];m.action(4)
  check(p['Head']==saved_head and m.rw(state+24)==19 and m.acc[(m.face,6)]==44019,'preview does not overwrite equipped slot')
  m.routine42('v44_apply_wardrobe',{0:m.face,1:0})
  check(m.acc[(m.face,6)]==44000+saved_head,'canonical save excludes preview')
  m.routine42('v44_apply_wardrobe',{0:m.face,1:1})
  check(m.acc[(m.face,6)]==44019,'image request can display preview')
  m.action(5);check(m.rw(state+24)==0 and m.acc[(m.face,6)]==44000+saved_head,'finish preview restores outfit')
  m.action(402);m.acc[(m.face,0)]=123;m.action(109);m.action(3)
  check(m.acc[(m.face,0)]==0 and p['NativeHead']==123,'stock headwear safely retained under mod hat')
  m.action(400);check(m.acc[(m.face,0)]==123 and p['NativeHeadSaved']==0,'stock headwear restored on removal')
  # Copy only the serialized properties into a fresh process fixture.
  saved=json.loads(json.dumps(p));fresh=Machine(raw,bias);fresh.props['era44'].update(saved);fresh.w(fresh.hero+32,31);fresh.action(1)
  check(fresh.props['era44']['Year']==2027 and all(fresh.props['era44']['Owned'+str(i['id'])]==1 for i in ITEMS),'reload preserves ownership and calendar')
  # Custom filenames and geometry routes do not steal any stock styles.
  for item in ITEMS:
   accessory=m.alloc();m.w(accessory+0x10,7 if item['slot']=='Mouth'else 6);m.w(accessory+0x14,44000+item['id'])
   result=m.hook42('v44_accessory_filename',{0:accessory})
   check(m.str(result)==f'a44_accessory_{item["id"]:02d}','registered native filename '+str(item['id']))
   for g in [0,1]:
    for stage in range(6):
     m.hook42('v44_accessory_position',{0:accessory,1:g,2:stage})
     v=[struct.unpack('<f',(m.u.reg_read(Q[n])&0xffffffff).to_bytes(4,'little'))[0]for n in [0,1]]
     check(all(0<=q<=1 for q in v),'position within native fractions')
  # Native root, rounded picker, selected callback and birth copy.
  root=m.root();check(len(m.buttons)==8,'eight compact controls')
  check(m.captions[m.buttons[7][0]][0]=='Year: 2026','year caption')
  country=m.alloc();m.q(country+16,m.managed('United States'));m.q(root+0x118,country);m.q(root+0x120,m.managed('New York'))
  m.click(m.buttons[6][0]);extra=d['states']['newlife31']['va']+bias
  check(m.rw(extra+64)==7,'Regions still opens native subtype')
  region=m.alloc();m.q(region+32,m.manager)
  for off in [0x38,0x60,0x68,0x70,0x90]:m.q(region+off,m.alloc())
  m.q(region+0xa0,m.scroll);m.q(region+0xe0,m.alloc());m.fitter_drivers[m.rq(region+0x90)]=[]
  m.hook42('v31_native_rounded_selector_setup',{19:region},custom=True)
  check(len(m.live_options)==20,'retained Regions builder reached through current setup chain')
  m.click(m.live_options[0]);m.root(root)
  m.click(m.buttons[7][0]);extra=d['states']['newlife31']['va']+bias
  check(m.transitions[-1]==6 and m.rw(extra+64)==8,'year picker stays native')
  group=m.alloc();m.q(group+32,m.manager)
  for off in [0x38,0x60,0x68,0x70,0x90]:m.q(group+off,m.alloc())
  m.q(group+0xa0,m.scroll);m.q(group+0xe0,m.alloc());m.fitter_drivers[m.rq(group+0x90)]=[]
  m.hook42('v31_native_rounded_selector_setup',{19:group},custom=True)
  check(len(m.live_options)==len(START_YEARS),'starting years populate')
  selected=m.live_options[START_YEARS.index(1930)];m.click(selected)
  check(m.rw(state)==1930 and m.transitions[-1]==5,'year callback persists draft')
  m.root(root);check(m.captions[m.buttons[7][0]][0]=='Year: 1930','return preserves selected year')
  m.w(m.hero+32,0);m.hook42('v44_birth_calendar')
  check(p['BirthYear']==1930 and p['Year']==1930 and p['Era']==1,'birth commits selected calendar')
  # A stale callback after leaving its subgroup cannot mutate a new draft.
  m.w(state,2026);m.click(selected);check(m.rw(state)==2026,'stale year callback rejected')
 report=dict(passed=True,binary_sha256=hashlib.sha256(raw).hexdigest(),arm64_checks=checks,ASLR_biases=[0,0x1000000000],all_27_purchase_and_equip_paths=True,era_boundaries_and_rotating_stock=True,atomic_funds_and_duplicate_purchase_guards=True,independent_slots_and_three_outfits=True,preview_excluded_from_saved_outfit=True,starting_year_native_picker=True,serialized_save_reload_fixture=True,Unity_managed_APIs_and_bank_implementation_mocked=True,physical_device_tested=False)
 (ROOT/'native44_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':validate(*sys.argv[1:])
