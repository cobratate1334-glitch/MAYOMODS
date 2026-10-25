"""Bounded native portrait, journal, resource and saved-action repairs."""
import copy,hashlib,io,json,struct,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from native_hooks import Builder,h
from native_v54.patch_native54 import Patch as Previous
from native_v42.patch_native42 import ref,ref_init

class Patch(Previous):
 def __init__(self,raw):
  self.base=json.loads((SOURCE/'native_v54/native_hooks.json').read_text());assert hashlib.sha256(raw).hexdigest()==self.base['binary_sha256']
  e=ELFFile(io.BytesIO(raw));segments=list(e.iter_segments());count=len(segments)+1
  self.added_off=0x6c40000;self.added_va=0x6c50000;self.added_size=0x60000
  data=bytearray(raw);data.extend(b'\0'*(self.added_off+self.added_size-len(data)))
  phoff=e['e_phoff'];table=bytearray(raw[phoff:phoff+len(segments)*56]);n=next(i for i,s in enumerate(segments)if s['p_type']=='PT_PHDR');struct.pack_into('<QQ',table,n*56+32,count*56,count*56)
  table+=struct.pack('<IIQQQQQQ',1,5,self.added_off,self.added_va,self.added_va,self.added_size,self.added_size,0x4000);assert phoff+len(table)<=self.base['v49_new_rx'][0]+0x1000
  data[phoff:phoff+len(table)]=table;struct.pack_into('<H',data,56,count)
  Builder.__init__(self,bytes(data));self.before_native=raw;self.program_ranges=[[56,2],[phoff,len(table)]]
  self.manifest=copy.deepcopy(self.base);self.old={r['name']:r for r in self.base['hooks']+self.base['routines']}
  self.rxoff,self.rxva=self.added_off,self.added_va;self.tail=next(s for s in self.loads if s['p_vaddr']==self.rxva);self.cursor=self.code_start=self.added_va
  self.strings=copy.deepcopy(self.base['strings']);self.strings_va=self.string_cursor=self.added_va+0x40000;self.states=copy.deepcopy(self.base['states']);self.state52=self.states['ui52']['va'];self.newlife24=self.states['newlife24']['va'];self.newlife31=self.states['newlife31']['va']
  self.hooks=[];self.routines=[];self.changed=[];self.serial=0;self.snprintf=self.plt('snprintf');self.trace23=self.old['persist_new_life_checkpoint23']['stub']
 def redirect(self,name,source):
  old=self.old[name];target=self.add_code(name+'_v55',source);self.write(old['stub'],f'b {target:#x}',name)
  for r in self.manifest['hooks']+self.manifest['routines']:
   if r['name']==name:r.update(source=f'b {target:#x}',length=4)
  return target
 def finish55(self):
  assert self.cursor<self.strings_va and self.string_cursor<self.added_va+self.added_size
  for s,va in self.strings.items():
   if s in self.base['strings']:continue
   raw=s.encode()+b'\0';p=self.off(va);assert self.blob[p:p+len(raw)]==b'\0'*len(raw);self.blob[p:p+len(raw)]=raw;self.changed.append([va,len(raw),'literal'])
  sites={r['site']for r in self.hooks}
  for r in self.manifest['hooks']:
   if r['site']in sites and not any(x['name']==r['name']for x in self.manifest['routines']):self.manifest['routines'].append(copy.deepcopy(r))
  self.manifest['hooks']=[r for r in self.manifest['hooks']if r['site']not in sites]+self.hooks;self.manifest['routines']+=self.routines
  self.manifest.update(binary_sha256=hashlib.sha256(self.blob).hexdigest(),base_v54_sha256=hashlib.sha256(self.before_native).hexdigest(),strings=self.strings,states=self.states,v55_new_code_range=[self.code_start,self.cursor],v55_changed_ranges=self.changed,v55_program_header_ranges=self.program_ranges,v55_added_rx=[self.added_off,self.added_va,self.added_size])
  (ROOT/'native_hooks.json').write_text(json.dumps(self.manifest,indent=2)+'\n');return bytes(self.blob)

def portraits(b):
 s='cmp w25,#1\nb.eq iris55_check\ncmp w25,#4\nb.ne finish\niris55_check:\nldr x0,[x19,#0x28]\ncbz x0,finish\nmov w1,w25\nmov x2,xzr\nbl 0x2f3b1d8\ncbz x0,finish\n'+f'bl {b.old["v49_current_component_id"]["stub"]:#x}\nbl {b.old["v52_parse_portrait_id"]["stub"]:#x}\nmov w9,#80000\ncmp w0,w9\nb.lo finish\nmov w9,#99999\ncmp w0,w9\nb.hi finish\nstr xzr,[sp]\nb finish'
 b.install('v55_preserve_coloured_portrait_pixels',0x2f3e6ac,s)
 s='cbz x1,finish\nmov x19,x1\nmov w20,w2\nmov w21,w3\ncmp w20,#1\nb.lt finish\ncmp w21,#1\nb.lt finish\ncmp w20,#512\nb.gt finish\ncmp w21,#512\nb.gt finish\nmov x0,x19\nmov x1,xzr\nbl 0x5558c70\ncbz w0,finish\nmov x0,x19\nmov x1,xzr\nbl 0x5557b04\nmov w24,w0\ncmp w24,#1\nb.lt finish\ncmp w24,#2048\nb.gt finish\nmov x0,x19\nmov x1,xzr\nbl 0x5557b40\nmov w25,w0\ncmp w25,#1\nb.lt finish\ncmp w25,#2048\nb.gt finish\nmov x0,x19\nmov x1,xzr\nbl 0x5559d18\ncbz x0,finish\nmov x23,x0\nmul w9,w24,w25\nldr x10,[x23,#24]\ncmp x10,x9\nb.lo finish\nldr x0,[x23]\nmul w1,w20,w21\nbl 0x223df80\ncbz x0,finish\nmov x26,x0\nmov w27,#0\nresize55_y:\nmul w9,w27,w25\nudiv w9,w9,w21\nmul w28,w9,w24\nmov w22,#0\nresize55_x:\nmul w9,w22,w24\nudiv w9,w9,w20\nadd w9,w9,w28\nadd x10,x23,#32\nldr w11,[x10,w9,uxtw #2]\nmadd w9,w27,w20,w22\nadd x10,x26,#32\nstr w11,[x10,w9,uxtw #2]\nadd w22,w22,#1\ncmp w22,w20\nb.lo resize55_x\nadd w27,w27,#1\ncmp w27,w21\nb.lo resize55_y\n'
 s+=ref_init(0x5c56ae0)+ref(0x5c56ae0)+'bl 0x2237158\nmov x27,x0\nmov w1,w20\nmov w2,w21\nmov x3,xzr\nbl 0x555a078\nmov x0,x27\nmov x1,x26\nmov x2,xzr\nmov x3,xzr\nbl 0x555a634\nmov x0,x27\nmov w1,#0\nmov w2,#0\nmov x3,xzr\nbl 0x555a4a8\nstr x27,[sp]\nb return_custom'
 b.install('v55_resize_readable_portrait_on_cpu',0x2f43414,s,ret=True)

def resources(b):
 names=['hair','beard','skin','eye','scar','patch','wardrobe','hospital','journal','handshake','health','brain','priest','bishop','cardinal','pope','basilica','conclave','community','smoke','gate','square','photographer','official']
 s='cbz x0,finish\nmov x8,x0\n'
 for n,name in enumerate(names):
  path='mayomods49/icons/49-'+name;s+=h.compare_key(path,f'owned55_{n}',f'owned55_next_{n}')+f'\nowned55_{n}:\n'+ref_init(0x5c56ad8)+b.string(path)+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,finish\nstr x0,[sp]\nb return_custom\n'+f'owned55_next_{n}:\n'
 s+='b finish';b.install('v55_full_owned_image_paths',0x2bad908,s,ret=True)
 aliases={'49-basilica':'basilica','49-gate':'seminary','49-community':'seminary','49-conclave':'conclave','49-cardinal':'conclave','49-smoke':'smoke','49-pope':'square','49-priest':'seminary','49-bishop':'basilica','49-handshake':'seminary','books':'seminary','scroll':'seminary','bread':'seminary','microphone':'seminary','musical-note':'seminary','speech-balloon':'seminary'}
 s='cbz x0,finish\nmov x8,x0\n'+h.compare_key('<GFC.gameplay52.ClergyImage>','banner55_dynamic','banner55_paths')+'\nbanner55_dynamic:\n'+b.ctx('gameplay52')+b.string('ClergyImage')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\ncbz x0,finish\nmov x8,x0\nbanner55_paths:\n'
 for n,(old,name)in enumerate(aliases.items()):s+=h.compare_key('mayomods49/icons/'+old,f'banner55_{n}',f'banner55_next_{n}')+f'\nbanner55_{n}:\n'+ref_init(0x5c56ad8)+b.string('mayomods55/church/'+name)+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,finish\nmov x1,xzr\nbl 0x553b564\nstr x0,[sp]\nb return_custom\n'+f'banner55_next_{n}:\n'
 s+='b finish';b.install('v55_supplied_church_story_images',0x2bad7a8,s,ret=True)

def journal(b):
 s='cbz x0,finish\nmov x19,x0\nldr w9,[x19,#16]\ncbz w9,finish\ncmp w9,#2048\nb.hi finish\n'+h.load_game()+'\nldr x0,[x8,#0x20]\ncbz x0,finish\nmov x1,xzr\nbl 0x327d194\ncbz x0,finish\nmov x20,x0\nmov x1,x19\nmov x2,xzr\nbl 0x335bca4\nmov x0,x19\n'+f'adr x1,{b.literal("journal outcome"):#x}\nbl {b.old["v54_log_game_label"]["stub"]:#x}\nb finish'
 b.journal55=b.routine('v55_append_native_life_journal',s)
 prior=b.resolved('v52_perform_community_activity')['stub']
 s='mov w19,w0\nmov w20,w1\n'+f'bl {b.old["v54_initialize_vocation_fields"]["stub"]:#x}\n'+b.ctx('gameplay52')+b.get('ActionsUsed','w25')+b.get('LastAge')+'cmp w24,w23\ncsel w25,w25,wzr,eq\n'+b.get('ClergyActions','w26')+b.get('ClergyAge')+'cmp w24,w23\ncsel w26,w26,wzr,eq\n'+b.get('ClergyRank','w27')+b.get('ElectionAge','w28')+f'mov w0,w19\nmov w1,w20\nbl {prior:#x}\nstr x0,[sp]\n'+b.ctx('gameplay52')+'cmp w19,#91\nb.ge log55_clergy_counts\n'+b.get('ActionsUsed')+'cmp w24,w25\nb.gt log55_activity\nb finish\nlog55_clergy_counts:\n'+b.get('ClergyActions')+'cmp w24,w26\nb.gt log55_church\n'+b.get('ClergyRank')+'cmp w24,w27\nb.ne log55_church\n'+b.get('ElectionAge')+'cmp w24,w28\nb.ne log55_church\nb finish\nlog55_church:\n'+b.string('ClergyStatus')+'b log55_read\nlog55_activity:\n'+b.string('Status')+'log55_read:\nmov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\n'+f'bl {b.journal55:#x}\nb finish'
 b.redirect('v52_perform_community_activity',h.save()+'\n'+s+'\nfinish:\n'+h.restore()+'\nret')
 s='cmp w0,#108\nb.ne finish\n'+b.ctx('gameplay52')+b.get('ParishFunds')+'cmp w24,#25\nb.ge finish\n'+b.text('ClergyEvent','Parish budget')+b.text('ClergyStatus','The parish needs at least 25 in funds for this decision. No money or annual action was spent.')+'mov w9,#1\nstr x9,[sp]\nb return_custom'
 b.chain('v55_check_parish_budget_before_action','v54_clergy_state_machine',s,ret=True)

def receipts(b):
 events=json.loads((ROOT/'receipts55.json').read_text());owners={e['owner']for e in events}
 s='str xzr,[sp]\ntbz w0,#0,finish\ncbz x19,finish\ncbz x21,finish\nldr x8,[x19,#0x18]\ncbz x8,finish\n'+h.compare_key('Receipt55','receipt55_owner','finish')+'\nreceipt55_owner:\nldr x8,[x21,#0x10]\ncbz x8,finish\n'
 for i,owner in enumerate(sorted(owners)):s+=h.compare_key(owner,'receipt55_'+owner,'receipt55_next_'+str(i))+'\nreceipt55_next_'+str(i)+':\n'
 s+='b finish\n'
 metrics={'f1_career':['Skill','Points','BonusDue'],'tv_host':['Preparation','Episodes','Audience'],'music_studio':['Progress','Quality','TotalReleases']}
 for owner in sorted(owners):
  s+='receipt55_'+owner+':\nmov w27,w20\n'
  for event in [e for e in events if e['owner']==owner]:s+=f'cmp w27,#{event["id"]}\nb.eq receipt55_event_{event["id"]}\n'
  s+='b finish\n'
 for event in events:
  owner=event['owner'];fields=metrics[owner];fmt=event['text'].replace('%','%%')+' Saved '+', '.join(k+' %d'for k in fields)+'.'
  s+=f'receipt55_event_{event["id"]}:\n'
  for j,k in enumerate(fields):s+=b.get(k,'w'+str(25+j))
  s+='sub sp,sp,#512\nmov x0,sp\nmov w1,#512\n'+f'adr x2,{b.literal(fmt):#x}\nmov w3,w25\nmov w4,w26\nmov w5,w27\nbl {b.snprintf:#x}\nmov x0,sp\nbl {h.NEW_STRING:#x}\nadd sp,sp,#512\nmov x28,x0\n'+f'bl {b.journal55:#x}\n'+b.ctx('gameplay52')+b.textptr('ResultBody55','x28')+'b finish\n'
 b.receipt55=b.routine('v55_successful_blueprint_receipt',s)
 b.chain('v55_receipt_after_accepted_write','v18_saved_state',f'bl {b.receipt55:#x}\nb finish')
 # Synchronize actual career employment and reset per-age work limits before
 # parsing the old dashboard. Only these three menu IDs are intercepted.
 s='cbz x0,finish\nmov x8,x0\n'
 for n,(owner,menu)in enumerate([('f1_career','genesis_v7_f1_career'),('tv_host','genesis_v7_tv_host'),('music_studio','genesis_music_studio_hub')]):
  s+=h.compare_key(menu,'menu55_'+owner,'menu55_next_'+str(n))+'\nmenu55_'+owner+':\n'+b.ctx(owner)+b.get('WorkAge55')+'cmp w24,w23\nb.eq menu55_synced_'+str(n)+'\n'+b.put('WorkAge55','w23')+b.set('WorkUsed',0)+'menu55_synced_'+str(n)+':\n'
  if owner!='music_studio':s+=b.set('NativeCareerSync',1)
  s+='b finish\nmenu55_next_'+str(n)+':\n'
 s+='b finish';b.chain('v55_sync_opened_career','v47_project_before_show',s)

def patch(raw):
 b=Patch(raw);portraits(b);resources(b);journal(b);receipts(b)
 from social55 import hooks
 hooks(b)
 return b.finish55()
if __name__=='__main__':Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()));print('v55 native built',flush=True)
