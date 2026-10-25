"""Run the new ARM64 world bridges at two ASLR bases; Unity APIs are modeled."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v44'),str(SOURCE/'native_v29')]
from native_v44 import test_native44 as old
from test_native import X
from catalog45 import CARS,HOUSES,HOUSE_YEARS,PLATFORMS,ART_KEYS,car_allowed,house_allowed,type_supported
old.ROOT=ROOT;old.old.ROOT=ROOT;old.old.previous.ROOT=ROOT;old.old.previous.test_native.ROOT=ROOT
class Machine(old.Machine):
 def __init__(self,raw,bias):
  super().__init__(raw,bias);self.cars45={};self.houses45={};self.resources45=[];self.sprites45={}
  self.refreshes45=[]
  self.new45={0x2b0cfc4,0x2b19b10,0x3ed1638,0x4dfe080,0x2a3030c,0x2a31778,0x2ae3250,0x2af2e88}
  for a in self.new45:self.map(a+bias,4)
  self.sprite_info45=self.alloc();slot=self.alloc();self.map(0x5c56ad8+bias,8);self.q(0x5c56ad8+bias,slot);self.q(slot,self.sprite_info45)
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if va not in getattr(self,'new45',set()):return super().mock(u,pc,size,data)
  a=[u.reg_read(r)for r in X[:3]];lr=u.reg_read(X[30])
  if va==0x2b0cfc4:value=self.cars45[a[0]]
  elif va==0x2b19b10:value=self.houses45[a[0]]
  elif va==0x4dfe080:value=int(self.str(a[0])==self.str(a[1]))
  elif va in [0x2a3030c,0x2a31778,0x2ae3250,0x2af2e88]:
   assert a[0] and a[1]==0;self.refreshes45.append((va,a[0]));value=0
  else:
   path=self.str(a[0]);assert a[1]==self.sprite_info45 and path.startswith('emoji/normal/a16_emoji-mayo45-')
   key=path.split('mayo45-')[-1];assert key in ART_KEYS
   value=self.sprites45.setdefault(path,self.alloc());self.resources45.append(path)
  self.finish_api(lr,value)
 def model45(self,item):
  p=self.alloc();self.q(p+0x10,self.managed('Ford' if item is None else item['make']));self.q(p+0x18,self.managed('Bronco' if item is None else item['model']));return p
 def house45(self,name):
  p=self.alloc();self.q(p+0x10,self.managed(name));self.q(p+0x18,self.managed(next(('mayo45-'+x['art'] for x in HOUSES if x['name']==name),'house1')));return p
 def year45(self,year,age=30):
  self.w(self.hero+32,age);self.props['era44']['BirthYear']=year-age;self.props['era44']['Year']=1234

def validate(path,before):
 raw=Path(path).read_bytes();base=Path(before).read_bytes();d=json.loads((ROOT/'native_hooks.json').read_text());checks=0
 def check(ok,label):
  nonlocal checks
  assert ok,label;checks+=1
 check(hashlib.sha256(raw).hexdigest()==d['binary_sha256'],'binary binding');check(hashlib.sha256(base).hexdigest()==d['base_v44_sha256'],'base binding')
 # The native lookup, financial, repair, value and saved serialization entry
 # points must remain byte-identical, independent of selection filtering.
 from native_v29.inspect_game27 import Game
 g=Game(path,ROOT.parents[2]/'global-metadata.dat')
 for va,n in [(0x2800d7c,100),(0x2802794,100),(0x2b0dfb4,100),(0x2b0e278,100),(0x2b0e850,100),(0x2b19e64,100),(0x2b1b838,100),(0x3543ecc,24),(0x3556304,24),(0x37c7abc,24)]:
  off=g.off(va);check(raw[off:off+n]==base[off:off+n],'retained owned asset and purchase route '+hex(va))
 for bias in [0,0x1000000000]:
  m=Machine(raw,bias);models={c['id']:m.model45(c)for c in CARS};stock=m.model45(None)
  for c in CARS:check(m.routine42('v45_model_id',{0:models[c['id']]})==c['id'],'exact native model ID '+c['model'])
  check(m.routine42('v45_model_id',{0:stock})==0,'stock model ID');check(m.routine42('v45_model_id',{0:0})==0,'null model ID')
  unknown=m.model45(dict(make='Mayo',model='Unrecognized saved custom model'))
  check(m.routine42('v45_model_id',{0:unknown})==0,'unknown Mayo model safe fallback')
  long=m.model45(dict(make='Mayo',model='x'*129));check(m.routine42('v45_model_id',{0:long})==0,'bounded string hash')
  years=sorted({1900,1929,1930,1959,1960,1989,1990,2025,2026,2100}|{n for c in CARS for n in [c['start']-1,c['start'],c['start']+1]+([]if c['end']==9999 else[c['end'],c['end']+1]) if n>=1900})
  for year in years:
   m.year45(year);check(m.routine42('v45_current_year')==year,'birth+actual age overrides stale year')
   check(m.routine42('v45_car_allowed',{0:stock})==int(year>=2026),'contemporary stock edition gate '+str(year))
   for c in CARS:check(m.routine42('v45_car_allowed',{0:models[c['id']]})==int(car_allowed(c,year)),'model availability '+str(year)+' '+c['model'])
   for luxury in [False,True]:check(any(car_allowed(c,year)and c['luxury']==luxury and not c['race_only']for c in CARS),'nonempty normal/luxury pool')
   for typ in ['Formula','Stock Car']:
    for cls in 'CBAS':check(any(car_allowed(c,year)and c['type']==typ and c['racing_class']==cls and c['race_only']for c in CARS),'nonempty racing pool '+typ+cls)
  for year in [1900,1920,1940,1960,1980,1990,2000,2026]:
   m.year45(year)
   for typ in range(14):
    for luxury,cls,race in [(False,'',0),(True,'',0),(False,'C',1),(False,'S',1)]:
     args={0:int(luxury),1:m.managed(cls),2:race,3:typ};ok=type_supported(year,typ,luxury,cls,race)
     check(m.routine42('v45_specific_car_type_supported',args)==int(ok),'nonempty specific-type request guard')
     m.hook42('v45_specific_car_type_fallback',args)
     check(m.u.reg_read(X[3])==(typ if ok else 0)and m.u.reg_read(X[0])==int(luxury)and m.u.reg_read(X[1])==args[1]and m.u.reg_read(X[2])==race,'fallback preserves all native arguments except unsupported type')
  # Exercise every real selection guard's allow/skip continuation.
  for year in [1900,1929,1960,2025,2026]:
   m.year45(year)
   for c in [CARS[0],CARS[6],CARS[22],None]:
    model=stock if c is None else models[c['id']];ok=car_allowed(c,year)
    m.hook42('v45_dealership_catalog_gate',{24:model},custom=not ok);check(True,'dealership continuation')
    m.hook42('v45_free_car_catalog_gate',{20:model},custom=not ok);check(True,'free-car continuation')
    if ok and c is not None:m.hook42('v45_free_car_period_models',{20:model},custom=True);check(True,'free-car make whitelist bypass')
  houses={name:m.house45(name)for name in HOUSE_YEARS}
  for year in [1900,1910,1920,1930,1940,1950,1960,1970,1990,2000,2010,2026,2029,2030]:
   m.year45(year)
   for name,obj in houses.items():
    check(m.routine42('v45_house_start_year',{0:obj})==HOUSE_YEARS[name],'house style release lookup')
    check(m.routine42('v45_house_allowed',{0:obj})==int(house_allowed(name,year)),'house year filter '+name)
   for n,reg in [('normal',20),('landlord',8),('vampire',20)]:
    for name in ['bungalow','futuristic']:
     m.hook42('v45_house_'+n+'_gate',{reg:houses[name]},custom=not house_allowed(name,year));check(True,'house pool guard '+n)
  # Real constructor post-processing: ages never precede the model/style.
  for c in CARS:
   car=m.alloc();m.cars45[car]=models[c['id']];m.w(car+0x10,99);m.w(car+0x38,1);m.year45(c['start']+2)
   m.routine42('v45_finalize_new_car',{0:car});check(m.rw(car+0x10)==2 and m.rw(car+0x38)==c['color'],'new car construction and fixed artwork colour')
   key='mayo45-'+c['art'];hook=next(r for r in d['hooks']if r['name']=='v45_car_emoji')
   for year in [1900,2026,2100]:
    m.year45(year);got=m.execute42(hook['stub'],{0:car});check(m.str(got)==key,'owned car icon independent of current year')
  for name,obj in houses.items():
   house=m.alloc();m.houses45[house]=obj;m.w(house+0x18,1000);m.year45(max(1900,HOUSE_YEARS[name])+2)
   m.routine42('v45_finalize_new_house',{0:house});check(m.rw(house+0x18)==min(1000,max(1900,HOUSE_YEARS[name])+2-HOUSE_YEARS[name]),'house construction age cap')
  for h in HOUSES:
   house=m.alloc();m.houses45[house]=houses[h['name']];hook=next(r for r in d['hooks']if r['name']=='v45_house_emoji')
   check(m.str(m.execute42(hook['stub'],{0:house}))=='mayo45-'+h['art'],'owned custom house icon')
  for key in ART_KEYS:
   hook=next(r for r in d['hooks']if r['name']=='v45_custom_asset_sprite');result=m.execute42(hook['stub'],{0:m.managed('mayo45-'+key)})
   path='emoji/normal/a16_emoji-mayo45-'+key;check(m.resources45[-1]==path and result==m.sprites45[path],'native typed sprite resource '+key)
  m.hook42('v45_custom_asset_sprite',{0:m.managed('car-sedan-blue')});check(True,'stock sprite route retained')
  for platform,year in PLATFORMS.items():
   for actual in [1900,year-1,year,year+1,2026]:
    m.year45(actual);m.hook42('v45_social_'+platform,custom=actual<year);check(True,'platform menu boundary '+platform+str(actual))
  place=m.alloc();m.q(place+0x88,m.managed('Melbourne'));m.q(place+0x90,m.managed('Australia'));m.year45(1900)
  m.routine42('v45_ensure_place_market',{0:place});check(m.refreshes45[-2:]==[(0x2a3030c,place),(0x2a31778,place)],'migrated life refreshes cars and homes')
  count=len(m.refreshes45);m.routine42('v45_ensure_place_market',{0:place});check(len(m.refreshes45)==count,'same-year same-place menus preserve cached stock')
  m.year45(1901);m.routine42('v45_ensure_place_market',{0:place});check(len(m.refreshes45)==count+2,'new calendar year refreshes both markets')
  m.q(place+0x88,m.managed('Sydney'));m.routine42('v45_ensure_place_market',{0:place});check(len(m.refreshes45)==count+4,'city change refreshes market')
  m.q(place+0x90,m.managed('Canada'));m.routine42('v45_ensure_place_market',{0:place});check(len(m.refreshes45)==count+6,'country change refreshes market')
  m.year45(1900);m.routine42('v45_ensure_place_market',{0:place});check(len(m.refreshes45)==count+8,'time-machine rewind refreshes future cached stock')
  for name,method in [('luxury',0x2ae3250),('racing',0x2af2e88)]:
   obj=m.alloc();m.year45(1900);m.routine42('v45_ensure_'+name+'_market',{0:obj});check(m.refreshes45[-1]==(method,obj),'migrated '+name+' market')
   count=len(m.refreshes45);m.routine42('v45_ensure_'+name+'_market',{0:obj});check(len(m.refreshes45)==count,'stable '+name+' cached stock')
   m.year45(1901);m.routine42('v45_ensure_'+name+'_market',{0:obj});check(len(m.refreshes45)==count+1,'new '+name+' stock for new year')
  # A migrated life defaults to 2026; different heroes do not share a cache.
  m.props['era44']['BirthYear']=0;check(m.routine42('v45_current_year')==2026,'unconverted save fallback')
 report=dict(passed=True,binary_sha256=hashlib.sha256(raw).hexdigest(),arm64_checks=checks,ASLR_bases=[0,0x1000000000],new_car_models=40,new_house_types=8,new_sprite_routes=17,native_finance_and_owned_lookups_unchanged=True,modeled_boundaries=['Genesis storage','Unity Resources.Load<Sprite>','native car/house lookup'],physical_device_tested=False,Unity_rendering_tested=False)
 (ROOT/'native45_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':validate(*sys.argv[1:])
