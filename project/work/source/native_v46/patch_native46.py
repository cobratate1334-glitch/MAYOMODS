"""Focused v46 native engine repairs, pinned to the signed v45 binary."""
import copy,csv,hashlib,io,json,struct,sys,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from native_hooks import Builder,h
from native_v45.patch_native45 import Patch as Previous
from native_v42.patch_native42 import ref,ref_init,body
BASE_SHA='1b7dc16cda4e8133a711d4d5bc982e1641368db313af0dc55bfcff180cf6a83d'
class Patch(Previous):
 def __init__(self,raw):
  Builder.__init__(self,raw);assert hashlib.sha256(raw).hexdigest()==BASE_SHA
  self.base=json.loads((SOURCE/'native_v45/native_hooks.json').read_text());self.manifest=copy.deepcopy(self.base)
  self.tail=next(s for s in self.loads if s['p_vaddr']==self.base['segment_va'])
  self.cursor=0x6550000;self.code_start=self.cursor;self.strings_va=0x656a000;self.string_cursor=self.strings_va
  self.strings=copy.deepcopy(self.base['strings']);self.states=copy.deepcopy(self.base['states']);self.routines=[];self.hooks=[];self.changed=[];self.serial=0
  self.old={r['name']:r for r in self.base['hooks']+self.base['routines']}
  self.newlife24=self.states['newlife24']['va'];self.newlife31=self.states['newlife31']['va']
  self.rw=next(s for s in self.loads if s['p_vaddr']==0x6570000);self.extra=self.states['era44']['va']
  self.state46=(self.rw['p_vaddr']+self.rw['p_memsz']+15)&~15;self.states['ui46']=dict(va=self.state46,size=32)
 def replace(self,name,code):
  target=self.routine(name+'_v46',code);old=self.old[name]
  self.blob[self.off(old['stub']):self.off(old['stub'])+4]=h.asm(f'b {target:#x}',old['stub'])
  r=next(r for r in self.manifest['routines']if r['name']==name);r.update(source=f'b {target:#x}',length=4)
  self.changed.append([old['stub'],4,name]);return target
 def finish46(self):
  assert self.cursor<self.strings_va
  for s,va in self.strings.items():
   if s in self.base['strings']:continue
   data=s.encode()+b'\0';o=self.off(va);assert self.blob[o:o+len(data)]==b'\0'*len(data)
   self.blob[o:o+len(data)]=data;self.changed.append([va,len(data),'literal'])
  size=max(self.tail['p_filesz'],self.cursor-self.tail['p_vaddr'],self.string_cursor-self.tail['p_vaddr']);assert self.tail['p_vaddr']+size<0x6570000
  p=self.e['e_phoff']+self.segs.index(self.tail)*56+32;struct.pack_into('<QQ',self.blob,p,size,size)
  q=self.e['e_phoff']+self.segs.index(self.rw)*56+40;struct.pack_into('<Q',self.blob,q,self.state46+32-self.rw['p_vaddr'])
  sites={r['site']for r in self.hooks};self.manifest['hooks']=[r for r in self.manifest['hooks']if r['site']not in sites]+self.hooks;self.manifest['routines']+=self.routines
  self.manifest.update(states=self.states,strings=self.strings,segment_size=size,binary_sha256=hashlib.sha256(self.blob).hexdigest(),base_v45_sha256=BASE_SHA,v46_new_code_range=[self.code_start,self.cursor],v46_changed_ranges=self.changed,v46_program_header_ranges=[[p,16],[q,8]])
  (ROOT/'native_hooks.json').write_text(json.dumps(self.manifest,indent=2)+'\n');return bytes(self.blob)

def city_repair(b):
 # Only classify actual, aligned managed strings. Keep the original ArrayList
 # and use its native virtual accessors rather than indexing private storage.
 src=body(b.old['v42_city_in_region'])
 guard='str xzr,[sp]\ncbz x0,finish\nmov x8,x0\n'
 assert src.startswith(guard)
 safe='str xzr,[sp]\nmov x8,x0\ncmp x8,#0x10000\nb.lo finish\ntst x8,#7\nb.ne finish\nlsr x9,x8,#48\ncbnz x9,finish\nldr w9,[x8,#0x10]\ncmp w9,#1\nb.lt finish\ncmp w9,#128\nb.hi finish\n'
 classify=b.replace('v42_city_in_region',src.replace(guard,safe,1))
 # x25, not x24, owns the live CountryAndCity configuration at this site.
 s=f'cbz x0,finish\nmov x27,x0\nadr x28,{b.states["regions42"]["va"]:#x}\nldr w25,[x28]\ncbz w25,finish\ncmp w25,#19\nb.hi finish\n'
 # Read country from the subgroup's native configuration already attached at
 # +0x58. This does not depend on a caller-saved register after GetCitiesArray.
 s+='cbz x19,finish\nldr x8,[x19,#0x58]\ncbz x8,finish\nldr x8,[x8,#0x10]\ncbz x8,finish\n'+h.compare_key('United States','filter46','finish')+'\nfilter46:\nldr x8,[x27]\nmov x0,x27\nldr x9,[x8,#0x298]\nldr x1,[x8,#0x2a0]\nblr x9\nmov w22,w0\ncmp w22,#1\nb.lt finish\ncmp w22,#4095\nb.hi finish\nldr x8,[x27,#0x10]\ncbz x8,finish\nldr x9,[x8,#0x18]\ncmp x9,x22\nb.lo finish\n'+ref_init(0x5c24320)+ref(0x5c24320)+'bl 0x2237158\ncbz x0,finish\nmov x26,x0\nmov x1,xzr\nbl 0x4edba28\nmov w24,#0\ncity_loop46:\ncmp w24,w22\nb.hs filtered46\nmov x0,x27\nmov w1,w24\nldr x8,[x27]\nldr x9,[x8,#0x2e8]\nldr x2,[x8,#0x2f0]\nblr x9\nmov x20,x0\nmov w1,w25\n'+f'bl {classify:#x}\ncbz w0,next_city46\nmov x0,x26\nmov x1,x20\nldr x8,[x26]\nldr x9,[x8,#0x308]\nldr x2,[x8,#0x310]\nblr x9\nnext_city46:\nadd w24,w24,#1\nb city_loop46\nfiltered46:\nldr w9,[x26,#0x18]\ncbz w9,finish\nstr x26,[sp]\nb finish'
 b.install('v46_filter_native_city_choices',b.old['v42_filter_native_city_choices']['site'],s)
 # The stock displaced instruction jumps to the common ArrayList conversion.
 r=b.hooks[-1];assert r['original'].startswith('b ')
 # Replace the old branch in the new trampoline, so the broken v42 filter is
 # never entered again. Both paths return an ArrayList to the original code.
 old=r['original']+f'\nb {r["site"]+4:#x}';new='b 0x2faa1a8'
 source=r['source'].replace(old,new);code=h.asm(source,r['stub']);assert len(code)<=r['length']
 b.blob[b.off(r['stub']):b.off(r['stub'])+len(code)]=code;r.update(source=source,length=len(code),original='b 0x2faa1a8')

def icons(b):
 keys=['calendar','earth','brain','eye','chart-up','flex','running-shoe','handshake','index-cards','top-hat']
 s='cbz x0,finish\nmov x8,x0\n'
 for i,key in enumerate(keys):
  s+=h.compare_key(key,f'icon46_{i}',f'icon46_next_{i}')+f'\nicon46_{i}:\n'+ref_init(0x5c56ad8)+b.string('emoji/normal/a16_emoji-'+key)+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,finish\nstr x0,[sp]\nb return_custom\n'+f'icon46_next_{i}:\n'
 # Chain on the v45 sprite stub. Replacing the shared public entry with the
 # base displaced prologue would silently bypass car/house artwork lookup.
 s+='b finish';b.chain('v46_native_menu_icon_resources','v45_custom_asset_sprite',s,ret=True)
 def title(name,heading,detail,icon):
  s='cbz x0,finish\nmov x19,x0\n'+b.string(heading)+'mov x1,x0\nldr x0,[x19,#0x38]\ncbz x0,finish\nmov x2,xzr\nbl 0x3024244\n'+b.string(detail)+'mov x1,x0\nldr x0,[x19,#0x68]\ncbz x0,finish\nmov x2,xzr\nbl 0x3024244\nldr x0,[x19,#0x68]\nfmov s0,#18.0\nmov x1,xzr\nbl 0x30247c8\n'+b.string(icon)+'mov x1,xzr\nbl 0x2bad908\ncbz x0,missing_icon46\nmov x1,xzr\nbl 0x553b564\ncbz x0,missing_icon46\nmov x22,x0\nldr x25,[x19,#0x60]\ncbz x25,finish\nmov x0,x25\nadd x1,x25,#0x58\nmov x2,x22\nbl 0x223e768\nmov x0,x25\nmov x1,xzr\nbl 0x3023ba8\nmov w24,#1\nb icon_visible46\nmissing_icon46:\nldr x25,[x19,#0x60]\ncbz x25,finish\nmov w24,#0\nicon_visible46:\nmov x0,x25\nmov x1,xzr\nbl 0x55725ac\ncbz x0,finish\nmov w1,w24\nmov x2,xzr\nbl 0x5575664\nb finish'
  b.replace(name,s)
 title('v44_starting_year_title','Starting year','Choose your birth year. The world changes as you age.','calendar')
 title('v42_regions_title','US Regions','Choose a region, then a city. Back keeps your draft.','earth')

def dealer(b):
 """Route real ScenarioBase choices, the class the current engine instantiates.

 Older tests exercised ScenarioLazyCsvBase, which GenesisController no longer
 creates for these menus. A rooted lease binds routes to the exact native
 scenario. Native NextScenario and Genesis list presentation own transitions.
 """
 assets=json.loads((ROOT/'assets.json').read_text());rr=[r for r in csv.DictReader(io.StringIO(assets['genesis_activities_v18']))if r['ScenarioID'].startswith('scenario.activitiesV18.era44_')]
 rows={r['ScenarioID']:r for r in rr};state=b.state46;action=b.old['v44_dealer_action']['stub']
 release=f'adr x28,{state:#x}\nldr x0,[x28]\ncbz x0,lease_clear46\nbl 0x223e784\nlease_clear46:\nstr xzr,[x28]\nstr wzr,[x28,#8]\nb finish'
 free=b.routine('v46_release_dealer_lease',release)
 capture='cbz x0,finish\ncbz x2,finish\nmov x19,x0\nmov x8,x2\nmov w27,#0\n'
 for n,row in enumerate(rr,1):capture+=h.compare_key(row['ScenarioID'],f'capture46_{n}',f'capture46_next_{n}')+f'\ncapture46_{n}:\nmov w25,#{n}\nb capture46\ncapture46_next_{n}:\n'
 item_index=next(n for n,r in enumerate(rr,1)if r['ScenarioID'].endswith('era44_item'))
 home_index=next(n for n,r in enumerate(rr,1)if r['ScenarioID'].endswith('era44_home'))
 for n in range(1,28):
  capture+=h.compare_key('scenario.activitiesV18.era46_item_'+str(n),f'capture46_item_{n}',f'capture46_item_next_{n}')+f'\ncapture46_item_{n}:\nmov w25,#{item_index}\nmov w27,#{100+n}\nb capture46\ncapture46_item_next_{n}:\n'
 capture+='b finish\ncapture46:\n'+f'bl {free:#x}\nmov x0,x19\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nadr x28,{state:#x}\nstr x0,[x28]\nstr w25,[x28,#8]\ncbnz w27,capture46_select\ncmp w25,#{home_index}\nb.ne finish\nmov w27,#1\ncapture46_select:\n'+b.ctx('era44')+b.put('Action','w27')+f'bl {action:#x}\nb finish'
 b.install('v46_bind_native_dealer_scenario',0x2ca3658,capture)
 serial=0
 def route(text):
  nonlocal serial
  out=''
  for step in text.split('>>'):
   if step.startswith('BP_GFC_MODIFY_PROPERTY=era44:Action:='):
    val=int(step.rsplit(':=',1)[1]);out+=b.ctx('era44')+f'mov w24,#{val}\n'+b.put('Action')
    if val:out+=f'bl {action:#x}\n'
   elif step.startswith('scenario.'):
    assert step in rows,step
    out+=b.string(step)+'mov x1,x0\nldr x0,[x19,#0x190]\ncbz x0,finish\nmov x2,xzr\nbl 0x30a2278\ncbz x0,finish\nmov x1,x0\nmov x0,x19\nmov x2,xzr\nbl 0x2a21414\n'
   elif step.startswith('BP_SHOW_LIST='):
    key=step.split('=',1)[1];assert key in assets
    out+=b.string(key)+'ldr x1,[x19,#0x190]\nmov w2,#0\nmov w3,#1\nmov x4,xzr\nbl 0x3089aac\n'
   else:raise AssertionError(step)
  return out+'b done_choice46\n'
 def advanced(raw):
  nonlocal serial
  serial+=1;k=serial;logic=json.loads(raw);out=b.ctx('era44')
  for n,case in enumerate(logic['cases']):
   expr=case['if']['expression'];skip=f'case46_{k}_{n}'
   if 'Era' in expr:
    era=int(re.search(r'== (\d+)',expr)[1]);out+=b.get('Era','w25')+f'cmp w25,#{era}\nb.ne {skip}\n'
   else:
    assert '<hero:age> < 18' in expr and 'Selected' in expr
    out+='cmp w23,#18\nb.ge '+skip+'\n'+b.get('Selected','w25')
    out+=f'cmp w25,#1\nb.eq adult46_{k}\ncmp w25,#16\nb.eq adult46_{k}\ncmp w25,#17\nb.ne {skip}\nadult46_{k}:\n'
   out+=route(case['then']['route_options'][0]['route_to'])+skip+':\n'
  return out+route(logic['else_when_no_matches']['route_options'][0]['route_to'])
 s='str xzr,[sp]\ncbz x0,finish\nmov x19,x0\nmov w20,w1\n'+f'adr x28,{state:#x}\nldr x0,[x28]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\nldr w26,[x28,#8]\ncbz w26,finish\ncmp w20,#0\nb.lt finish\ncmp w20,#3\nb.hi finish\n'+f'bl {free:#x}\n'
 for n,row in enumerate(rr,1):
  s+=f'cmp w26,#{n}\nb.ne scene46_{n}\n'
  for i in range(1,5):
   if not row.get(f'Choice{i}_Text'):continue
   s+=f'cmp w20,#{i-1}\nb.ne choice46_{n}_{i}\n'
   raw=row.get(f'Choice{i}_AdvancedLogic');s+=advanced(raw)if raw else route(row[f'Choice{i}_RouteTo'])
   s+=f'choice46_{n}_{i}:\n'
  s+='b finish\n'+f'scene46_{n}:\n'
 s+='b finish\ndone_choice46:\nmov w9,#1\nstr x9,[sp]\nb finish';dispatch=b.routine('v46_native_dealer_choice',s)
 for n,site in enumerate([0x2cb228c,0x2cb3bd0]):b.install('v46_native_choice_entry_'+str(n),site,f'bl {dispatch:#x}\ncbnz w0,return_custom\nb finish',ret=True)
 # The visible popup uses ScenarioBase.DismissSelected, too.
 s='cbz x0,finish\nmov x19,x0\n'+f'adr x28,{state:#x}\nldr x0,[x28]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\nbl {free:#x}\nbl {b.old["v44_clear_preview"]["stub"]:#x}\nb finish'
 b.install('v46_native_dealer_dismiss',0x2cb58e4,s)
 (ROOT/'dealer_routes46.json').write_text(json.dumps([dict(id=r['ScenarioID'],choices=[r[f'Choice{i}_Text']for i in range(1,5)if r.get(f'Choice{i}_Text')])for r in rr],indent=2)+'\n')

PALETTES=[
 dict(name='Vintage',paper='#F5EDDB',cell='#FFF9EC',alt='#E9DCC3',ink='#3C281D',secondary='#70533E',accent='#795032',bar='#573822',light='#FFF8E9',line='#BAA078'),
 dict(name='Noir',paper='#22272D',cell='#2D333B',alt='#3C444D',ink='#F6EFE0',secondary='#D2C7B6',accent='#E2B37A',bar='#15191E',light='#F6EFE0',line='#69717B'),
 dict(name='Retro',paper='#FFF2DB',cell='#FFF9ED',alt='#F3DFC2',ink='#193D3C',secondary='#52635A',accent='#A3421D',bar='#17676A',light='#FFF7E8',line='#C2A98B'),
 dict(name='Modern',paper='#FFFFFF',cell='#FFFFFF',alt='#E5EDF5',ink='#075C93',secondary='#376780',accent='#075C93',bar='#075D9F',light='#FFFFFF',line='#9CAFBF')]
COLOR_GROUPS={
 'paper':[7,27,92,96,102,108], 'cell':[3,5,107,115], 'alt':[2,15,17,80],
 'ink':[8,9,14,16,84,88,90,93,99,100,101],
 'secondary':[10,11,25,26,85,89],
 'bar':[6,18,19,77,106], 'light':[12,20,21,22,23,24,78], 'line':[13,97], 'accent':[116]}
def themes(b):
 st=b.state46
 # Native Color returns four floats in s0..s3. Preserve the full ABI frame.
 s=f'cmp w1,#-1\nb.ne finish\nadr x8,{st:#x}\nldr w25,[x8,#20]\ncbz w25,finish\nmov w26,w0\n'
 for index,p in enumerate(PALETTES,1):
  s+=f'cmp w25,#{index}\nb.ne palette46_next_{index}\n'
  for group,ids in COLOR_GROUPS.items():
   for item in ids:s+=f'cmp w26,#{item}\nb.eq palette46_{index}_{group}\n'
  s+='b finish\n'
  for group in COLOR_GROUPS:
   v=bytes.fromhex(p[group][1:])+b'\xff';s+=f'palette46_{index}_{group}:\n'
   for k,ch in enumerate(v):
    bits=struct.unpack('<I',struct.pack('<f',ch/255))[0];s+=f'movz w9,#{bits&65535}\nmovk w9,#{bits>>16},lsl #16\nstr w9,[sp,#{256+k*16}]\n'
   s+='b return_custom\n'
  s+=f'palette46_next_{index}:\n'
 s+='b finish';b.install('v46_native_era_theme_colors',0x2f62f68,s,ret=True)
 s='cbz x0,finish\nmov x27,x0\n'+f'bl {b.old["v45_current_year"]["stub"]:#x}\nmov w25,#1\ncmp w0,#1930\nb.lt era46_ready\nmov w25,#2\ncmp w0,#1960\nb.lt era46_ready\nmov w25,#3\ncmp w0,#1990\nb.lt era46_ready\nmov w25,#4\nera46_ready:\nadr x28,{st:#x}\nldr w9,[x28,#20]\ncmp w9,w25\nb.eq finish\nstr w25,[x28,#20]\nmov x0,x27\nmov x1,xzr\nbl 0x2f809bc\nb finish'
 update=b.routine('v46_refresh_era_theme',s);b.theme_update=update
 (ROOT/'era_palettes46.json').write_text(json.dumps(dict(palettes=PALETTES,theme_color_groups=COLOR_GROUPS),indent=2)+'\n')

def navigation(b):
 # Recover the native lower panel after interrupted close animations. The
 # game stores panel position separately from whether child objects are active.
 s='cbz x0,finish\nmov x27,x0\nldr x24,[x27,#0xa0]\ncbz x24,finish\nldrb w9,[x24,#0x110]\ncbnz w9,finish\nldr x8,[x24,#0xc8]\ncbz x8,finish\nldr w9,[x8,#0x18]\ncbnz w9,finish\nldr x8,[x27,#0x80]\ncbz x8,finish\nldr x9,[x8,#0x1c8]\ncbnz x9,finish\nldr x23,[x27,#0x60]\ncbz x23,finish\nldrb w9,[x23,#0x80]\ncbnz w9,finish\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldrb w9,[x8,#0x18]\ncbz w9,finish\n'+f'adr x28,{b.state46:#x}\nadr x8,{b.states["menu_generation41"]["va"]:#x}\nldr w26,[x8]\nldr w9,[x28,#24]\ncmp w9,w26\nb.ne settle_panel46\nldrb w9,[x23,#0x81]\ncbnz w9,panel46_shown\nsettle_panel46:\nstr w26,[x28,#24]\n'+'ldr x0,[x23,#0x20]\ncbz x0,finish\nmov x1,xzr\nbl 0x55779e0\nmov x0,x23\nmovi d0,#0\nmov x1,xzr\nbl 0x2f7db1c\ncbz x0,finish\nmov x1,x0\nmov x0,x23\nmov x2,xzr\nbl 0x5577470\npanel46_shown:\n'
 # Explicitly activate only hidden native groups. The UAP/native activation
 # methods maintain their own input accessibility state.
 for n,(off,method)in enumerate([(0x38,0x2f7e424),(0x40,0x2f8144c),(0x68,0x2f7e530),(0x70,0x2f7e5a0)]):
  s+=f'ldr x0,[x27,#{off}]\ncbz x0,group46_{n}\nmov x1,xzr\nbl 0x55725ac\ncbz x0,group46_{n}\nmov x25,x0\nmov x1,xzr\nbl 0x5575728\ncbnz w0,group46_{n}\nmov x0,x25\nmov w1,#1\nmov x2,xzr\nbl 0x5575664\nmov x0,x27\nmov w1,#1\nmov x2,xzr\nbl {method:#x}\ngroup46_{n}:\n'
 s+='b finish';recover=b.routine('v46_restore_native_hud',s)
 # Both normal refresh and the native final-close coroutine run the same
 # guarded restoration. Never activate the HUD over a real list or darkly.
 b.chain('v46_theme_and_hud_on_refresh','v33_recover_hidden_top_menu_after_dialog',f'bl {b.theme_update:#x}\nbl {recover:#x}\nb finish')
 for name in ['RemoveMenuListAnimation','RemoveMenuListNoAnimation','RemoveNormalListAnimation','RemoveNormalListAnimationNoReturn','RemoveNormalListNoAnimation','RemoveNormalListNoAnimationNoReturn']:
  old=b.old['v41_guard_'+name];target=old['stub']
  s=f'bl {target:#x}\nstr x0,[sp]\ncbnz w0,finish\n'+h.load_game()+f'\nldr x0,[x8,#0x90]\nbl {recover:#x}\nb finish'
  wrapper=b.routine('v46_complete_'+name,s)
  record=b.routines[-1]
  site=old['site'];b.blob[b.off(site):b.off(site)+4]=h.asm(f'b {wrapper:#x}',site);b.changed.append([site,4,'complete_'+name])
  b.hooks.append(dict(name='v46_native_completion_'+name,site=site,stub=wrapper,resume=site+4,original=f'b {target:#x}',source=record['source'],length=record['length']))
 # Stop stale lower-panel moves from finishing after a different presentation.
 epoch=b.states['menu_generation41']['va']
 for name,site,guard in [('show',0x2f7db74,0x2f7f540),('hide',0x2f7d954,0x2f7ed88)]:
  b.install('v46_stamp_lower_'+name,site,f'cbz x20,finish\nadr x28,{epoch:#x}\nldr w9,[x28]\nstr w9,[x20,#0x14]\nb finish')
  s=f'cbz x0,finish\nadr x28,{epoch:#x}\nldr w9,[x28]\nldr w10,[x0,#0x14]\ncmp w9,w10\nb.eq finish\nmov w9,#-1\nstr w9,[x0,#0x10]\nstr xzr,[x0,#0x18]\nstr xzr,[sp]\nb return_custom'
  b.install('v46_guard_lower_'+name,guard,s,ret=True)

def patch(raw):
 b=Patch(raw);city_repair(b);icons(b);dealer(b);themes(b);navigation(b);return b.finish46()
if __name__=='__main__':Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()));print('v46 native repair patch built',flush=True)
