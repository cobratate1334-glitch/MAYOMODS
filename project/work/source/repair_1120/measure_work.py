"""Count actual native redraw work with explicit API doubles, never claim FPS."""
import csv,io,json,hashlib,sys
from pathlib import Path
from repair_1120.tests.machine import Machine,W,prior
from repair_1120.content import build
from repair_1120.package import NATIVE
def measure(work):
 w=Path(work);assert w==W;prior.ROOT=w/'fixtures';raw=(w/'libil2cpp.so').read_bytes();assert hashlib.sha256(raw).hexdigest()==NATIVE
 old=Path('/workspace/build_work/era-world-1119/libil2cpp.so').read_bytes();assert hashlib.sha256(old).hexdigest()=='707e53c828d1b49dfaddb54b9c028327a3f45a078a4b2aa0d09fe560fb5684d4'
 redraw={}
 for label,data in [('1119',old),('1120',raw)]:
  redraw[label]={}
  for mode,phase,year in [('modern',0,2026),('war',1,1915)]:
   m=Machine(data);m.at(year);log=m.alloc();scroller=m.alloc();image=m.alloc(512);original=m.alloc();m.q(log+0x30,scroller);m.q(scroller+0x30,image);m.q(image+0xd8,original)
   m.resource('native1119/background/2026');m.resource('native1109/background/ww1');m.w(m.d['states']['military_expansion']['va']+64,phase)
   for _ in range(12):m.execute42(0x2ff35a8,{19:log},end=0x2ff35ac)
   redraw[label][mode]=dict(refreshes=12,Sprite_resource_load_calls=m.resource_loads,Image_set_sprite_calls=len(m.image_changes))
 assert redraw['1119']['modern']['Sprite_resource_load_calls']==12 and redraw['1120']['modern']['Sprite_resource_load_calls']==0
 assert redraw['1119']['war']['Sprite_resource_load_calls']==12 and redraw['1120']['war']['Sprite_resource_load_calls']==1
 assert redraw['1120']['modern']['Image_set_sprite_calls']==0 and redraw['1120']['war']['Image_set_sprite_calls']==1
 base=json.loads((w/'base_assets.json').read_text());overlay=build(base);tables={}
 for name in ['genesis_rework_annual1105','genesis_school1110','genesis_prison1110']:
  tables[name]={variant:dict(rows=len(list(csv.DictReader(io.StringIO(text)))),bytes=len(text.encode()))for variant,text in [('1119',base[name]),('1120',overlay[name])]}
 report=dict(passed=True,native_sha256=NATIVE,redraw_API_counts=redraw,annual_table_sizes=tables,actual_ARM64=True,managed_Unity_API_doubles=True,phone_FPS_measured=False,phone_age_up_latency_measured=False)
 (w/'work_reduction.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':measure(*sys.argv[1:])
