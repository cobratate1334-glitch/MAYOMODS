"""Consolidate New Life appearance on the exact released v52 engine."""
import copy,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from native_hooks import Builder,h
from native_v52.patch_native52 import Patch as Previous
from native_v42.patch_native42 import body
from native_v33.patch_native33 import root_guard
from native_v52.newlife52 import CATEGORIES

BASE_SHA='b8c8686867d5fd2ba4e29623f061e7a0e837656312a842defe4fc03854a6e5a8'
HUBS={130:('Genetic appearances',[("Face editor",'native'),('Hair & facial hair',131),('Skin & eye colours',132),('Genetic features',133),('Scars & eyepatches',134),('Inherited abilities','inherited')]),
      131:('Hair & facial hair',[('Hairstyle',101),('Hair colour',102),('Facial hair',107),('Facial hair colour',108)]),
      132:('Skin & eye colours',[('Skin tone',103),('Eye colour',104)]),
      133:('Genetic features',[('Eye patterns',('marks',1)),('Skin markings',('marks',2)),('Hair & face traits',('marks',3))]),
      134:('Scars & eyepatches',[('Scars',105),('Eyepatches',106)])}
MARK_GROUPS={1:('Eye patterns',[0,5,12,13]),2:('Skin markings',[0,1,8,2,9,10,14,3,4,11]),3:('Hair & face traits',[0,6,7])}
PAGE=4

class Patch(Previous):
 def __init__(self,raw):
  Builder.__init__(self,raw);assert hashlib.sha256(raw).hexdigest()==BASE_SHA
  self.base=json.loads((SOURCE/'native_v52/native_hooks.json').read_text());self.manifest=copy.deepcopy(self.base)
  self.old={r['name']:r for r in self.base['hooks']+self.base['routines']}
  self.rxoff,self.rxva,_=self.base['v49_new_rx'];self.tail=next(s for s in self.loads if s['p_vaddr']==self.rxva)
  self.cursor=self.code_start=0x6be0000;self.strings=copy.deepcopy(self.base['strings'])
  self.string_cursor=max(v+len(k.encode())+1 for k,v in self.strings.items());self.strings_va=0x6c30000
  self.states=copy.deepcopy(self.base['states']);self.newlife24=self.states['newlife24']['va'];self.newlife31=self.states['newlife31']['va'];self.state52=self.states['ui52']['va']
  self.hooks=[];self.routines=[];self.changed=[];self.serial=0
 def redirect(self,name,source):
  old=self.old[name];target=self.add_code(name+'_v53',source)
  self.blob[self.off(old['stub']):self.off(old['stub'])+4]=h.asm(f'b {target:#x}',old['stub'])
  for r in self.manifest['hooks']+self.manifest['routines']:
   if r['name']==name:r.update(source=f'b {target:#x}',length=4)
  self.changed.append([old['stub'],4,name]);return target
 def finish53(self):
  assert self.cursor<0x6c30000 and self.string_cursor<0x6c40000
  for s,va in self.strings.items():
   if s in self.base['strings']:continue
   raw=s.encode()+b'\0';off=self.off(va);assert self.blob[off:off+len(raw)]==b'\0'*len(raw)
   self.blob[off:off+len(raw)]=raw;self.changed.append([va,len(raw),'literal'])
  sites={r['site']for r in self.hooks};self.manifest['hooks']=[r for r in self.manifest['hooks']if r['site']not in sites]+self.hooks;self.manifest['routines']+=self.routines
  self.manifest.update(strings=self.strings,states=self.states,binary_sha256=hashlib.sha256(self.blob).hexdigest(),base_v52_sha256=BASE_SHA,v53_new_code_range=[self.code_start,self.cursor],v53_changed_ranges=self.changed,v53_program_header_ranges=[],v53_BSS_growth=0)
  (ROOT/'native_hooks.json').write_text(json.dumps(self.manifest,indent=2)+'\n');return bytes(self.blob)

def patch(raw):
 b=Patch(raw);st=b.state52;extra=b.newlife31;ns=b.newlife24;add=b.old['newlife31_add_rounded_option']['stub']
 # Reuse four previously unused scalar slots; no new managed roots/save fields.
 # +8 parent hub, +12 page, +68 genetic group, +76 native-editor entry flag.
 def guard(mode=None):
  return 'cbz x0,finish\nmov x19,x0\n'+f'adr x26,{extra:#x}\nldr w9,[x26,#64]\n'+(f'cmp w9,#{mode}\nb.ne finish\n'if mode else'')+'ldr x0,[x26,#72]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\nldr x27,[x19,#0x20]\ncbz x27,finish\nldr w9,[x27,#0xb4]\ncmp w9,#6\nb.ne finish\nldrb w9,[x27,#0x110]\ncbnz w9,finish\n'
 # Rebuild the existing rooted subgroup and its native scroller in place.
 rebuild=b.routine('v53_rebuild_appearance_page','cbz x0,finish\nmov w1,#0\nldr x2,[x0,#0x58]\nldr w3,[x0,#0xb0]\nldr x4,[x0,#0xc0]\nmov x5,xzr\nbl 0x2fa9d40\nb finish')
 def mode(n):return f'adr x28,{st:#x}\nmov w9,#{n}\nstr w9,[x28]\nadr x26,{extra:#x}\nstr w9,[x26,#64]\n'
 def to_page(n):return mode(n)+f'mov x0,x19\nbl {rebuild:#x}\nb finish'
 opens={}
 for n in HUBS:
  opens[n]=b.routine('v53_open_hub_'+str(n),guard()+f'adr x28,{st:#x}\nstr wzr,[x28,#12]\n'+to_page(n))
 # Main root uses its stock Appearance button; its caption and action are
 # changed, preserving the native config and all four face-editor categories.
 s='cbz x0,finish\nmov x25,x0\n'+root_guard(b)+'cmp x19,x25\nb.ne finish\n'+mode(130)+f'adr x28,{st:#x}\nstr wzr,[x28,#12]\nstr wzr,[x28,#68]\nstr wzr,[x28,#76]\nmov w9,#130\nstr w9,[x28,#8]\nstr wzr,[x19,#0x10c]\nmov x0,x27\nmov w1,#6\nmov x2,xzr\nbl 0x2f731f8\nb finish'
 openroot=b.routine('v53_open_genetic_appearances_from_newlife',s)
 s=f'adr x8,{st:#x}\nldr w9,[x8,#76]\ncbnz w9,native53_delegate\nmov x25,x0\n'+root_guard(b)+f'mov x0,x25\nbl {openroot:#x}\nb return_custom\nnative53_delegate:\nstr wzr,[x8,#76]\nb finish'
 b.install('v53_stock_appearance_opens_unified_hub',0x2fa8a8c,s,ret=True)
 b.install('v53_unified_stock_appearance_caption',0x2fa7a80,b.string('Genetic appearances')+'str x0,[sp,#40]\nb finish')
 # Native editor entry returns to the existing New Life form on Save/Back.
 s=guard(130)+mode(0)+'mov x0,x27\nmov w1,#5\nmov x2,xzr\nbl 0x2f731f8\n'+f'adr x28,{ns:#x}\nldr x0,[x28,#32]\ncbz x0,finish\nbl 0x223e73c\ncbz x0,finish\nadr x8,{st:#x}\nmov w9,#1\nstr w9,[x8,#76]\nmov x1,xzr\nbl 0x2fa8a8c\nb finish'
 native=b.routine('v53_open_integrated_native_face_editor',s)
 inherited=b.routine('v53_open_inherited_abilities',guard(130)+mode(0)+f'adr x26,{extra:#x}\nmov w9,#4\nstr w9,[x26,#64]\nmov x0,x19\nbl {rebuild:#x}\nb finish')
 rootback=b.routine('v53_back_to_newlife',guard(130)+mode(0)+'mov x0,x27\nmov w1,#5\nmov x2,xzr\nbl 0x2f731f8\nb finish')
 # Consolidate ten custom root rows into the stock unified Appearance row.
 old=b.resolved('v21_new_life_native_buttons');src=old['source']
 def start(label):
  at=src.index('cbz x0,'+label);return src.rfind('adrp x20,',0,at)
 for first,last in [('root_no_button52_0',None),('root_no_button31_5','root_no_button31_6'),('root_no_button31_3','root_no_button31_4')]:
  a=start(first)
  if last:z=start(last)
  else:z=src.index(f'adrp x8, {st&~4095:#x}\nadd x8, x8, #{st&4095}\nstr wzr,[x8]\n',a)
  src=src[:a]+src[z:]
 # The remaining body controls, personality, Regions and year are contiguous.
 for before,after in [('add w1,w24,#5','add w1,w24,#4'),('add w1,w24,#7','add w1,w24,#5'),('add w1,w24,#8','add w1,w24,#6')]:src=src.replace(before,after)
 src=src.replace('root_new31:\n',f'root_new31:\nadr x8,{st:#x}\nstr xzr,[x8,#8]\nstr wzr,[x8,#68]\nstr wzr,[x8,#76]\n',1)
 b.redirect(old['name'],src)
 # Inherited stat bonuses have a distinct name; they are accessed in the hub.
 old=b.resolved('newlife31_selector_title');src=old['source']
 a=b.strings['Genetic trait'];v=b.literal('Inherited abilities')
 needle=f'adrp x0, {a&~4095:#x}\nadd x0, x0, #{a&4095}'
 assert needle in src;src=src.replace(needle,f'adr x0,{v:#x}')
 b.redirect(old['name'],src)
 # Every picker is paged. Existing stable option IDs, draft rendering and
 # commit semantics stay intact; only their presentation/return path changes.
 editor_open={};rows={};page_callbacks={}
 for n,(key,options,label,icon,off)in enumerate(CATEGORIES,101):
  parent=131 if n in [101,102,107,108] else 132 if n in [103,104] else 134 if n in [105,106] else 133
  s=guard(parent)+mode(n)+f'adr x28,{st:#x}\nmov w9,#{parent}\nstr w9,[x28,#8]\nstr wzr,[x28,#12]\n'
  s+=(f'adr x8,{ns:#x}\nldr w9,[x8,#24]\n'if n==109 else f'ldr w9,[x28,#{off}]\n')+'str w9,[x28,#4]\n'+f'mov x0,x19\nbl {rebuild:#x}\nb finish'
  editor_open[n]=b.routine('v53_open_picker_'+key,s)
  apply=body(b.resolved('v52_apply_draft_'+key));tail='str wzr,[x28]\nstr wzr,[x26,#64]\nmov x0,x27\nmov w1,#5\nmov x2,xzr\nbl 0x2f731f8\nb finish'
  assert tail in apply;apply=apply.replace(tail,to_page(parent));save=b.routine('v53_save_picker_'+key,apply)
  back=b.routine('v53_cancel_picker_'+key,guard(n)+to_page(parent))
  if n!=109:rows[n]=dict(title=label,values=list(range(len(options))),options=options,save=save,back=back)
  else:
   for group,(title,values)in MARK_GROUPS.items():rows[(109,group)]=dict(title=title,values=values,options=options,save=save,back=back)
 for group in MARK_GROUPS:
  s=guard(133)+f'adr x8,{st:#x}\nmov w9,#{group}\nstr w9,[x8,#68]\n'+f'mov x0,x19\nbl {editor_open[109]:#x}\nb finish'
  opens['marks',group]=b.routine('v53_open_mark_group_'+str(group),s)
 # Fixed callback addresses for page navigation, guarded against stale owners.
 for key,r in rows.items():
  n=key[0]if isinstance(key,tuple)else key;count=(len(r['values'])+PAGE-1)//PAGE
  for page in range(count):
   s=guard(n)+f'adr x8,{st:#x}\nmov w9,#{page}\nstr w9,[x8,#12]\nmov x0,x19\nbl {rebuild:#x}\nb finish'
   page_callbacks[key,page]=b.routine('v53_page_'+str(key).replace(' ','').replace('(','').replace(')','').replace(',','_')+'_'+str(page),s)
 # Header preview and short contextual description; the option list no longer
 # pushes fifteen large genetic buttons beneath the title in one long page.
 s='cbz x0,finish\nmov x19,x0\n'+f'adr x28,{st:#x}\nldr w24,[x28]\n'
 title_cases=[(n,None,t)for n,(t,_)in HUBS.items()]+[(n,None,r['title'])for n,r in rows.items()if isinstance(n,int)]+[(109,g,'Genetic appearances')for g in MARK_GROUPS]
 for i,(n,g,t)in enumerate(title_cases):
  s+=f'cmp w24,#{n}\nb.ne title53_next_{i}\n'
  if g:s+=f'ldr w9,[x28,#68]\ncmp w9,#{g}\nb.ne title53_next_{i}\n'
  s+=b.string(t)+'mov x22,x0\n'+b.string(MARK_GROUPS[g][0]+' · Preview then Save & back.'if g else'Choose a category.'if n in HUBS else'Preview your choice, then Save & back.')+f'mov x23,x0\nb title53_ready\ntitle53_next_{i}:\n'
 s+='b finish\ntitle53_ready:\nldr x0,[x19,#0x38]\ncbz x0,finish\nmov x1,x22\nmov x2,xzr\nbl 0x3024244\nldr x0,[x19,#0x68]\ncbz x0,finish\nmov x1,x23\nmov x2,xzr\nbl 0x3024244\n'+f'adr x8,{ns:#x}\nldr x0,[x8,#32]\ncbz x0,finish\nbl 0x223e73c\nbl {b.old["v52_render_newlife_preview"]["stub"]:#x}\ncbz x0,finish\nmov x1,x0\nldr x0,[x19,#0x60]\ncbz x0,finish\nmov x2,xzr\nbl 0x3028114\nldr x0,[x19,#0x60]\nmov x1,xzr\nbl 0x55724dc\ncbz x0,finish\nmov w9,#0x42c00000\nfmov s0,w9\nfmov s1,s0\nmov x1,xzr\nbl 0x5581f90\nb finish'
 title=b.routine('v53_appearance_page_header',s);b.replace52('v52_draft_picker_title_and_preview',f'bl {title:#x}\nb finish')
 def pill(label,cb,selected=None):
  s=b.string(label)+f'mov x1,x0\nmov x0,x19\nadr x2,{cb:#x}\nmov w3,#1\n'
  if selected is not None:s+=f'adr x8,{st:#x}\nldr w9,[x8,#4]\nmov w10,#{selected}\ncmp w9,w10\ncset w3,ne\n'
  return s+f'bl {add:#x}\n'
 # Setup owns only our new appearance modes. Country/regions/year and all
 # other native subgroups continue through the retained setup chain.
 s=f'adr x26,{extra:#x}\nldr w24,[x26,#64]\ncmp w24,#101\nb.lt finish\ncmp w24,#109\nb.le setup53_begin\ncmp w24,#130\nb.lt finish\ncmp w24,#134\nb.gt finish\nsetup53_begin:\nmov x0,x19\nbl 0x2fa97ac\nstr wzr,[x19,#0x54]\nldr x0,[x26,#72]\ncbz x0,setup53_no_old\nbl 0x223e784\nsetup53_no_old:\nmov x0,x19\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nstr x0,[x26,#72]\nmov x0,x19\nbl {title:#x}\n'
 for n,(t,items)in HUBS.items():
  s+=f'cmp w24,#{n}\nb.ne setup53_hub_next_{n}\n'
  for label,target in items:
   cb=native if target=='native'else inherited if target=='inherited'else opens[target]if target in opens else editor_open[target]
   s+=pill(label,cb)
  s+=pill('Back to New Life'if n==130 else'Back to Genetic appearances',rootback if n==130 else opens[130])+f'b return_custom\nsetup53_hub_next_{n}:\n'
 for i,(key,r)in enumerate(rows.items()):
  n=key[0]if isinstance(key,tuple)else key
  s+=f'cmp w24,#{n}\nb.ne setup53_row_next_{i}\nadr x28,{st:#x}\n'
  if isinstance(key,tuple):s+=f'ldr w9,[x28,#68]\ncmp w9,#{key[1]}\nb.ne setup53_row_next_{i}\n'
  s+=pill('Save & back',r['save']);count=(len(r['values'])+PAGE-1)//PAGE
  s+=f'adr x28,{st:#x}\nldr w9,[x28,#12]\n'
  for page in range(count):
   s+=f'cmp w9,#{page}\nb.ne setup53_page_next_{i}_{page}\n'
   for v in r['values'][page*PAGE:(page+1)*PAGE]:
    cb=b.old[f'v52_preview_{CATEGORIES[n-101][0]}_{v}']['stub'];s+=pill('None'if n==109 and v==0 else r['options'][v],cb,v)
   if page:s+=pill('Previous choices',page_callbacks[key,page-1])
   if page+1<count:s+=pill('More choices',page_callbacks[key,page+1])
   s+=pill('Back without saving',r['back'])+f'b return_custom\nsetup53_page_next_{i}_{page}:\n'
  s+=f'b return_custom\nsetup53_row_next_{i}:\n'
 s+='b finish';b.chain('v53_organized_appearance_setup','v31_native_rounded_selector_setup',s,ret=True)
 r=b.hooks[-1];src=r['source'];assert src.endswith('\nret');src=src[:-4]+'\nb 0x2faaf34';code=h.asm(src,r['stub']);b.blob[b.off(r['stub']):b.off(r['stub'])+len(code)]=code;r.update(source=src,length=len(code))
 s=guard()+f'adr x28,{st:#x}\nldr w9,[x28]\ncmp w9,#101\nb.lt finish\ncmp w9,#109\nb.le layout53\ncmp w9,#130\nb.lt finish\ncmp w9,#134\nb.gt finish\nlayout53:\nmov x0,x19\nbl {title:#x}\nb return_custom'
 b.chain('v53_organized_appearance_layout','v31_selector_layout',s,ret=True)
 (ROOT/'organization53.json').write_text(json.dumps(dict(hubs={str(k):v for k,v in HUBS.items()},mark_groups=MARK_GROUPS,choices_per_page=PAGE,maximum_picker_buttons=8,root_custom_buttons=6,stock_face_editor_reused=True),indent=2)+'\n')
 return b.finish53()

if __name__=='__main__':Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()));print('v53 native organization built')
