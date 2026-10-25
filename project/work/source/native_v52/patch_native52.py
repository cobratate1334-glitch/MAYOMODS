"""Device-report repairs on the exact released v51 ARM64 engine.

Retain save identities and native screens. Every trampoline, literal and ELF
change is declared in the manifest; release tests bind to the resulting hash.
"""
import copy, hashlib, json, re, struct, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent; SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from native_v51.patch_native51 import Patch as Previous
from native_hooks import Builder,h
from native_v42.patch_native42 import body,ref,ref_init,compare_utf16
BASE_SHA='5b74ac2ac714fedb57098c8cf03b849ff4ab751460012e3d28733995be03b4c8'

class Patch(Previous):
 def __init__(self,raw):
  Builder.__init__(self,raw); assert hashlib.sha256(raw).hexdigest()==BASE_SHA
  self.base=json.loads((SOURCE/'native_v51/native_hooks.json').read_text())
  self.manifest=copy.deepcopy(self.base);self.old={r['name']:r for r in self.base['hooks']+self.base['routines']}
  self.rxoff,self.rxva,_=self.base['v49_new_rx'];self.tail=next(s for s in self.loads if s['p_vaddr']==self.rxva)
  self.cursor=self.code_start=self.rxva+0x50000
  self.strings_va=self.rxva+0xf0000;self.string_cursor=self.strings_va
  self.strings=copy.deepcopy(self.base['strings']);self.states=copy.deepcopy(self.base['states'])
  self.routines=[];self.hooks=[];self.changed=[];self.serial=0
  self.newlife24=self.states['newlife24']['va'];self.newlife31=self.states['newlife31']['va']
  self.trace23=self.old['persist_new_life_checkpoint23']['stub'];self.snprintf=self.plt('snprintf')
  self.state52=self.rxva+0x100020;self.states['ui52']=dict(va=self.state52,size=192)
  self.header_changes=[]
 def redirect(self,name,source):
  old=self.old[name];target=self.add_code(name+'_v52',source)
  self.blob[self.off(old['stub']):self.off(old['stub'])+4]=h.asm(f'b {target:#x}',old['stub'])
  for r in self.manifest['hooks']+self.manifest['routines']:
   if r['name']==name:r.update(source=f'b {target:#x}',length=4)
  self.changed.append([old['stub'],4,name]);return target
 def replace52(self,name,code):return self.redirect(name,h.save()+'\n'+code+'\nfinish:\n'+h.restore()+'\nret')
 def resolved(self,name):
  r=self.old[name]
  while r['source'].startswith('b 0x'):
   va=int(r['source'].split()[1],16);r=next(x for x in self.old.values()if x['stub']==va)
  return r
 def finish52(self):
  assert self.cursor<self.rxva+0xc0000 and self.string_cursor<self.rxva+0x100000
  for s,va in self.strings.items():
   if s in self.base['strings']:continue
   raw=s.encode()+b'\0';p=self.off(va);assert self.blob[p:p+len(raw)]==b'\0'*len(raw)
   self.blob[p:p+len(raw)]=raw;self.changed.append([va,len(raw),'literal'])
  # Extend only the existing final writable load's zero-filled BSS. There are
  # no new file-backed credentials, objects or pointers in this state area.
  rw=next(s for s in self.segs if s['p_vaddr']==self.rxva+0x100000)
  p=self.e['e_phoff']+self.segs.index(rw)*56+40
  struct.pack_into('<Q',self.blob,p,32+192);self.header_changes.append([p,8])
  sites={r['site']for r in self.hooks}
  self.manifest['hooks']=[r for r in self.manifest['hooks']if r['site']not in sites]+self.hooks
  self.manifest['routines']+=self.routines
  self.manifest.update(strings=self.strings,states=self.states,binary_sha256=hashlib.sha256(self.blob).hexdigest(),
    base_v51_sha256=BASE_SHA,v52_new_code_range=[self.code_start,self.cursor],v52_changed_ranges=self.changed,
    v52_program_header_ranges=self.header_changes)
  (ROOT/'native_hooks.json').write_text(json.dumps(self.manifest,indent=2)+'\n')
  return bytes(self.blob)

def journal(b):
 # v49 changed the displayed label to ASCII but left the v42 callback matching
 # the old emoji-prefixed string. Match the text actually shown on the button.
 old=b.old['v42_select_living_journal'];s=body(old)
 start=s.index('ldr w9,[x8,#0x10]');end=s.index('open_journal42:',start)
 s=s[:start]+compare_utf16('Life journal','open_journal42','finish')+'\n'+s[end:]
 b.redirect(old['name'],h.save()+'\n'+s+'\nfinish:\n'+h.restore()+'\n'+old['original']+f'\nb {old["resume"]:#x}\nreturn_custom:\n'+h.restore()+'\nret')

def regions(b):
 # Root +0x118 is GodModePersonConfig; GetCountry reads +0x140. v42
 # treated a person configuration as DataCountry, then read its type enum as
 # a managed string. This is the actual region-entry receiver correction.
 old=b.resolved('new_life_engine_button24_1');src=body(old)
 assert 'ldr x8,[x19,#0x118]'in src
 src=src.replace('ldr x8,[x19,#0x118]','ldr x8,[x19,#0x140]',1)
 b.replace52(old['name'],src)
 for i in range(20):
  old=b.old['v42_region_choice_'+str(i)];src=body(old)
  assert 'ldr x2,[x25,#0x118]'in src
  b.replace52(old['name'],src.replace('ldr x2,[x25,#0x118]','ldr x2,[x25,#0x140]',1))
 # The input is DataCountry.GetCitiesArray's ArrayList. Read its declared
 # storage directly, validate every bound, and classify only actual strings.
 # Never call an arbitrary virtual slot on an element or a CountryAndCity.
 classifier=b.resolved('v42_city_in_region')['stub']
 st=b.states['regions42']['va']
 s=f'cbz x0,finish\nmov x27,x0\nadr x28,{st:#x}\nldr w25,[x28]\ncbz w25,finish\ncmp w25,#19\nb.hi finish\n'
 s+='cbz x19,finish\nldr x8,[x19,#0x58]\ncbz x8,finish\nldr x8,[x8,#0x10]\ncbz x8,finish\n'+h.compare_key('United States','filter52','finish')+'\nfilter52:\n'
 s+='ldr w22,[x27,#0x18]\ncmp w22,#1\nb.lt finish\ncmp w22,#4095\nb.hi finish\nldr x23,[x27,#0x10]\ncbz x23,finish\nldr x9,[x23,#0x18]\ncmp x9,x22\nb.lo finish\n'
 s+=ref_init(0x5c24320)+ref(0x5c24320)+'bl 0x2237158\ncbz x0,finish\nmov x26,x0\nmov x1,xzr\nbl 0x4edba28\nmov w24,#0\ncity52_loop:\ncmp w24,w22\nb.hs city52_done\nadd x8,x23,#32\nldr x20,[x8,w24,uxtw #3]\nadd w24,w24,#1\ncmp x20,#0x10000\nb.lo city52_loop\ntst x20,#7\nb.ne city52_loop\n'
 # String's class is obtained from the native empty-string metadata reference.
 s+=ref_init(0x5c23368)+ref(0x5c23368,'x8')+'ldr x9,[x8]\nldr x8,[x20]\ncmp x8,x9\nb.ne city52_loop\nmov x0,x20\nmov w1,w25\n'+f'bl {classifier:#x}\ncbz w0,city52_loop\nmov x0,x26\nmov x1,x20\nldr x8,[x26]\nldr x9,[x8,#0x308]\nldr x2,[x8,#0x310]\nblr x9\nb city52_loop\ncity52_done:\nldr w9,[x26,#0x18]\ncbz w9,finish\nstr x26,[sp]\nb finish'
 old=b.old['v46_filter_native_city_choices']
 b.redirect(old['name'],h.save()+'\n'+s+'\nfinish:\n'+h.restore()+'\nb 0x2faa1a8')

def patch(raw):
 b=Patch(raw);journal(b);regions(b)
 for module in ['appearance52','newlife52','height52','calendar52','gameplay52','navigation52']:
  __import__(module).hooks(b)
 return b.finish52()

if __name__=='__main__':
 out=Path(sys.argv[2]);raw=patch(Path(sys.argv[1]).read_bytes());out.write_bytes(raw)
 assert hashlib.sha256(out.read_bytes()).digest()==hashlib.sha256(raw).digest()
 print('v52 native patch built',flush=True)
