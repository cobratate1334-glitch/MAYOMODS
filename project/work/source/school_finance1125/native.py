"""Extend hash-pinned 1124 in unused RX and isolated zero-filled RW."""
import copy,hashlib,json,sys
from pathlib import Path
from native_hooks import Builder,h
from era_world.native import Patch as Previous
BASE='cd36b55b64ce393f9d5d62d52fc72f966daf9f600e630db8e503cb236ed6e8b5'
class Patch(Previous):
 def __init__(self,raw,manifest):
  assert hashlib.sha256(raw).hexdigest()==BASE
  self.base=json.loads(Path(manifest).read_text());assert self.base['binary_sha256']==BASE
  Builder.__init__(self,raw);self.before_native=raw;self.manifest=copy.deepcopy(self.base)
  self.old={r['name']:r for r in self.base['hooks']+self.base['routines']}
  self.rxoff,self.rxva,self.added_size=self.base['era_world_rx'];self.tail=next(s for s in self.loads if s['p_vaddr']==self.rxva)
  self.cursor=self.code_start=(self.base['repair1123_code'][1]+15)&~15
  self.strings=copy.deepcopy(self.base['strings']);self.string_cursor=max(va+len(s.encode())+1 for s,va in self.strings.items());self.strings_va=self.string_cursor
  self.states=copy.deepcopy(self.base['states']);self.state=self.states['era_world']['va']+64000;self.states['school1125']=dict(va=self.state,size=1536)
  assert self.state+1536<=self.states['era_world']['va']+65536
  self.newlife24=self.states['newlife24']['va'];self.newlife31=self.states['newlife31']['va'];self.state52=self.states['ui52']['va']
  self.hooks=[];self.routines=[];self.changed=[];self.serial=0;self.snprintf=self.plt('snprintf');self.trace23=self.old['persist_new_life_checkpoint23']['stub'];self.journal55=self.old['v55_append_native_life_journal']['stub']
 def routine(self,name,body):
  # Locals and snprintf buffers have their own 256 bytes below the preserved
  # register frame. Retain input x0/x1/x2/x3 for argument-slot lookups.
  source=h.save()+'\nsub sp,sp,#256\nstp x0,x1,[sp]\nstp x2,x3,[sp,#16]\n'+body+'\nfinish:\nldr x0,[sp]\nadd sp,sp,#256\nstr x0,[sp]\n'+h.restore()+'\nret'
  return self.add_code(name,source)
 def finish(self,out):
  assert self.cursor<min(va for s,va in self.base['strings'].items()if va>=self.rxva+0x180000)
  assert self.string_cursor<=self.rxva+self.added_size
  for s,va in self.strings.items():
   if s in self.base['strings']:continue
   data=s.encode()+b'\0';off=self.off(va);assert self.blob[off:off+len(data)]==b'\0'*len(data);self.blob[off:off+len(data)]=data;self.changed.append([va,len(data),'literal1125'])
  self.changed.append([self.code_start,self.cursor-self.code_start,'new code1125'])
  sites={r['site']for r in self.hooks};self.manifest['hooks']=[r for r in self.manifest['hooks']if r['site']not in sites]+self.hooks;self.manifest['routines']+=self.routines
  self.manifest.update(binary_sha256=hashlib.sha256(self.blob).hexdigest(),strings=self.strings,states=self.states,school1125_base=BASE,school1125_code=[self.code_start,self.cursor],school1125_changes=self.changed,school1125_headers=[])
  Path(out).write_text(json.dumps(self.manifest,indent=2)+'\n');return bytes(self.blob)
if __name__=='__main__':
 from school_finance1125.fixes import hooks
 b=Patch(Path(sys.argv[1]).read_bytes(),sys.argv[2]);hooks(b);Path(sys.argv[3]).write_bytes(b.finish(sys.argv[4]))
