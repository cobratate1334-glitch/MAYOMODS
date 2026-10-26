"""Execute the real game's line parser and added resource/car ARM64 boundaries.

Managed strings/list allocations are explicit API doubles; the tokenizing loop
and all branches below execute from the candidate native library at two biases.
"""
import csv,hashlib,io,json,sys
from pathlib import Path
from life_repair.validate_native import Machine as Previous,prior,X


class Machine(Previous):
 def __init__(self,raw,bias):
  super().__init__(raw,bias);off,va,n=self.d['ui_integrity_rx'];self.map(va+bias,n);self.u.mem_write(va+bias,raw[off:off+n]);self.csv_mode=False
  self.map(0x3083094+bias,0x274);self.u.mem_write(0x3083094+bias,self.load(0x3083094,0x274));self.map(0x60c424b+bias,1);self.u.mem_write(0x60c424b+bias,b'\1')
  for slot in [0x5c22990,0x5c237f8,0x5c237c8,0x5c32f10]:
   self.map(slot+bias,8);self.q(slot+bias,self.alloc())
  for va in [0x498f9a8,0x4dfa448,0x4e021e4,0x4e042d8,0x4991d48]:self.map(va+bias,4)
 def mock(self,u,pc,size,data):
  if self.csv_mode:
   va=pc-self.bias;a=[u.reg_read(r)for r in X[:4]];lr=u.reg_read(X[30])
   if va==0x2237158:self.finish_api(lr,self.alloc());return
   if va==0x498f9a8:
    arr=self.alloc(32+1024*8);self.q(arr+24,1024);self.q(a[0]+16,arr);self.w(a[0]+24,0);self.w(a[0]+28,0);self.finish_api(lr,0);return
   if va==0x4dfa448:self.finish_api(lr,int.from_bytes(u.mem_read(a[0]+20+a[1]*2,2),'little'));return
   if va in [0x4e021e4,0x4e042d8]:
    s=self.str(a[0]);self.finish_api(lr,self.managed(s[a[1]:a[1]+a[2]]if va==0x4e021e4 else s[a[1]:]));return
   if va==0x4991d48:
    n=self.rw(a[0]+24);arr=self.rq(a[0]+16);result=self.alloc(32+n*8);self.q(result+24,n);u.mem_write(result+32,bytes(u.mem_read(arr+32,n*8)));self.finish_api(lr,result);return
  return super().mock(u,pc,size,data)
 def split_native(self,line):
  self.csv_mode=True
  try:
   result=self.execute42(0x3083094,{0:self.managed(line),1:0});n=self.rq(result+24);return [self.str(self.rq(result+32+i*8))for i in range(n)]
  finally:self.csv_mode=False


def validate(binary,fixture,base_assets,content_path,out):
 prior.ROOT=Path(fixture);raw=Path(binary).read_bytes();old=json.loads(Path(base_assets).read_text());overlay=json.loads(Path(content_path).read_text());assets={**old,**overlay};checks=[]
 def check(ok,label):assert ok,label;checks.append(label)
 for bias in [0,0x1000000000]:
  m=Machine(raw,bias)
  # Reproduce the owner's actual failure with the original library's parser.
  bad=next(l for l in old['genesis_life_rework'].split('\n')if l.startswith('scenario.lifeRework.command_home1106,'))
  check(len(m.split_native(bad))<48,'negative control: old multiline command row is invalid in real native CSV parser')
  for key in ['command_home1106','period_shop1107','item1107_iphone','purchase1107_switch_result','war_hub1106']:
   line=next(l for l in assets['genesis_life_rework'].split('\n')if l.startswith('scenario.lifeRework.'+key+','));values=m.split_native(line)
   check(len(values)==53,'real native parser reads 53 columns for '+key)
   expected=next(csv.reader(io.StringIO(line)));values=[v.rstrip('\r')for v in values];actual=[v[1:-1].replace('""','"')if v.startswith('"')and v.endswith('"')else v for v in values]
   check(actual==expected,'all native-parsed columns agree, including labels and routes: '+key)
  for year,want in [(1939,False),(2015,False),(2016,True),(2026,True)]:
   model=m.model45(dict(make='Bugatti',model='Chiron'));m.year45(year);value=m.routine42('v45_car_allowed',{0:model});check(bool(value)==want,'Chiron native stock year restriction '+str(year))
  for year,name,art in [(1900,'1900 Brass Carriage','prewar_car'),(1964,'1960 Family Wagon','mustang')]:
   from native_v45.catalog45 import CARS
   c=next((c for c in CARS if c['model']==name),next(c for c in CARS if 1946<=c['start']<1975))if year!=1900 else next(c for c in CARS if c['model']==name)
   model=m.model45(c);value=m.routine42('integrity_native_car_image',{0:model});check(m.str(value)=='mayomods1107/props/'+art,'existing period model gets supplied artwork '+str(year))
  model=m.model45(dict(make='Bugatti',model='Chiron'));car=m.alloc();m.cars45[car]=model
  row=next(r for r in m.d['hooks']if r['name']=='integrity_native_car_badges');value=m.execute42(row['stub'],{0:car});check(m.str(value)=='mayomods1107/props/bugatti','original car emoji boundary returns supplied car sprite ID')
  for name in ['iphone','switch','ww1_plane','ww2_tank','vape']:
   key='mayomods1107/props/'+name;row=next(r for r in m.d['hooks']if r['name']=='integrity_supplied_sprite_resources');value=m.execute42(row['stub'],{0:m.managed(key)})
   check(value==m.texture55 and m.resources55[-1]==key,'typed sprite lookup '+name)
  for year,want in [(1916,'ww1_plane'),(1942,'ww2_plane')]:
   m.year45(year);key='mayomods1107/props/period_aircraft';value=m.execute42(row['stub'],{0:m.managed(key)})
   check(value==m.texture55 and m.resources55[-1]=='mayomods1107/props/'+want,'wartime aircraft artwork follows the actual year '+str(year))
  print('Native parser/resource/car checks passed at',hex(bias),flush=True)
 report=dict(passed=True,checks=len(checks),binary_sha256=hashlib.sha256(raw).hexdigest(),negative_control_actual_native_CSV_parser=True,managed_APIs_modeled=True,ART_tested=False,Unity_rendering_tested=False,phone_tested=False)
 Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
