"""Invalidate obsolete list animations and translation callbacks.

Pinned to the delivered v40 binary/metadata. A 32-bit generation occupies the
verified alignment gap at +0x14, between the state/bool at +0x10 and the first
managed reference at +0x18. No managed reference or declared field is replaced.
The only new static value is loader-zeroed BSS. Native scene content is retained.
"""
import copy,hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE));sys.path.insert(0,str(SOURCE/'native_v29'))
from native_hooks import Builder,h
from native_v33.patch_native33 import Patch as Previous
BASE_SHA='6b300f00ccdbfb466c4098443abb586d4712482253185f79a1ced328f038a9ff'
class Patch(Previous):
 def __init__(self,raw):
  Builder.__init__(self,raw);assert hashlib.sha256(raw).hexdigest()==BASE_SHA
  self.base=json.loads((SOURCE/'native_v40/native_hooks.json').read_text());self.manifest=copy.deepcopy(self.base)
  self.tail=next(s for s in self.loads if s['p_vaddr']==self.base['segment_va'])
  self.cursor=(max(r['stub']+r['length']for r in self.base['hooks']+self.base['routines'])+15)&~15;self.code_start=self.cursor
  self.strings=copy.deepcopy(self.base['strings']);self.strings_va=min(self.strings.values());self.states=copy.deepcopy(self.base['states'])
  self.string_cursor=max(v+len(s.encode())+1 for s,v in self.strings.items())
  self.routines=[];self.hooks=[];self.changed=[]
  self.rw=next(s for s in self.loads if s['p_vaddr']==0x6570000)
  self.epoch=(self.rw['p_vaddr']+self.rw['p_memsz']+15)&~15
  self.states['menu_generation41']=dict(va=self.epoch,size=16)
 def literal(self,s):
  if s not in self.strings:self.strings[s]=self.string_cursor;self.string_cursor+=len(s.encode())+1
  return self.strings[s]
 def finish41(self):
  for s,va in self.strings.items():
   if s in self.base['strings']:continue
   data=s.encode()+b'\0';off=self.tail['p_offset']+va-self.tail['p_vaddr'];assert self.blob[off:off+len(data)]==b'\0'*len(data)
   self.blob[off:off+len(data)]=data;self.changed.append([va,len(data),'literal'])
  size=max(self.tail['p_filesz'],self.string_cursor-self.tail['p_vaddr']);assert self.tail['p_vaddr']+size<self.rw['p_vaddr']
  struct.pack_into('<QQ',self.blob,self.e['e_phoff']+self.segs.index(self.tail)*56+32,size,size)
  self.manifest['segment_size']=size
  self.manifest['v41_RX_program_header_offset']=self.e['e_phoff']+self.segs.index(self.tail)*56+32
  end=self.epoch+16-self.rw['p_vaddr'];index=self.segs.index(self.rw)
  struct.pack_into('<Q',self.blob,self.e['e_phoff']+index*56+40,end)
  self.manifest['hooks']+=self.hooks;self.manifest['routines']+=self.routines
  self.manifest.update(states=self.states,strings=self.strings,binary_sha256=hashlib.sha256(self.blob).hexdigest(),base_v40_sha256=BASE_SHA,
   v41_new_code_range=[self.code_start,self.cursor],v41_changed_ranges=self.changed,
   v41_BSS_program_header_offset=self.e['e_phoff']+index*56+40,obsolete_menu_callbacks_invalidated=True)
  (ROOT/'native_hooks.json').write_text(json.dumps(self.manifest,indent=2)+'\n');return bytes(self.blob)

def patch(raw):
 b=Patch(raw);bind=json.loads((ROOT/'native_bindings41.json').read_text())
 # A new presentation/close invalidates older deferred work. Cancel separately
 # scheduled transform slides on both containers, preserving original methods.
 cancel='cbz x0,finish\nmov x27,x0\n'+f'adr x28,{b.epoch:#x}\nldr w9,[x28]\nadd w9,w9,#1\ncbnz w9,generation_nonzero41\nmov w9,#1\ngeneration_nonzero41:\nstr w9,[x28]\nmov x0,x27\nmov x1,xzr\nbl 0x55779e0\n'
 for off in [0x30,0x38]:
  cancel+=f'ldr x0,[x27,#{off}]\ncbz x0,cancel_next41_{off}\nmov x1,xzr\nbl 0x55779e0\ncancel_next41_{off}:\n'
 cancel+='b finish'
 b.install('v41_new_list_cancels_obsolete_work',0x2f7cce8,cancel)
 old=next(r for r in b.base['hooks']if r['name']=='v27_editor_root_close')
 # Chain the prior New Life Back/Close guard instead of replacing its entry.
 b.install('v41_close_list_cancels_obsolete_work',old['stub'],cancel)
 b.install('v41_dismiss_invalidates_pending_presentations',0x2f7c898,cancel)
 # Capture before a coroutine can be queued. Delayed first execution is also
 # rejected; stamping only during MoveNext would incorrectly accept that case.
 for n,r in enumerate(bind['iterators']):
  reg=r['iterator_register'];stamp=f'cbz {reg},finish\nadr x28,{b.epoch:#x}\nldr w9,[x28]\nstr w9,[{reg},#0x14]\nb finish'
  b.install('v41_stamp_'+r['name'],r['stamp_site'],stamp)
  assert b.hooks[-1]['original']==r['stamp_original']
  guard=f'cbz x0,finish\nadr x28,{b.epoch:#x}\nldr w9,[x28]\nldr w10,[x0,#0x14]\ncmp w9,w10\nb.eq finish\nmov w9,#-1\nstr w9,[x0,#0x10]\nstr xzr,[x0,#0x18]\nstr xzr,[sp]\nb return_custom'
  b.install('v41_guard_'+r['name'],r['guard_site'],guard,ret=True)
 # Translation completion/timeout actions belong to the captured presentation,
 # rather than the manager's newly selected container.
 b.install('v41_stamp_translation',0x2f7cdb8,f'cbz x20,finish\nadr x28,{b.epoch:#x}\nldr w9,[x28]\nstr w9,[x20,#0x14]\nb finish')
 for n,site in enumerate([0x2f7dce0,0x2f7dd4c,0x2f7ddc4,0x2f7dea8,0x2f7e76c]):
  guard=f'cbz x0,finish\nadr x28,{b.epoch:#x}\nldr w9,[x28]\nldr w10,[x0,#0x14]\ncmp w9,w10\nb.eq finish\nstr xzr,[sp]\nb return_custom'
  b.install('v41_guard_translation_'+str(n),site,guard,ret=True)
 from native_gameplay41 import hooks
 hooks(b)
 return b.finish41()
if __name__=='__main__':Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()));print('v41 menu transition patch built')
