"""Patch the reported 1119 binary in its unused RX reserve and zero-filled RW."""
import copy,hashlib,json,sys
from pathlib import Path
from native_hooks import Builder
from era_world.native import Patch as Previous
BASE='707e53c828d1b49dfaddb54b9c028327a3f45a078a4b2aa0d09fe560fb5684d4'
class Patch(Previous):
 def __init__(self,raw,manifest):
  assert hashlib.sha256(raw).hexdigest()==BASE
  self.base=json.loads(Path(manifest).read_text());assert self.base['binary_sha256']==BASE
  Builder.__init__(self,raw);self.before_native=raw;self.manifest=copy.deepcopy(self.base)
  self.old={r['name']:r for r in self.base['hooks']+self.base['routines']}
  self.rxoff,self.rxva,self.added_size=self.base['era_world_rx'];self.tail=next(s for s in self.loads if s['p_vaddr']==self.rxva)
  self.cursor=self.code_start=(self.base['era_world_code'][1]+15)&~15
  self.strings=copy.deepcopy(self.base['strings']);self.string_cursor=max(va+len(s.encode())+1 for s,va in self.strings.items());self.strings_va=self.string_cursor
  self.states=copy.deepcopy(self.base['states']);self.state=self.states['era_world']['va']+40000;self.states['repair1120']=dict(va=self.state,size=4096)
  assert self.state+4096<=self.states['era_world']['va']+65536
  self.newlife24=self.states['newlife24']['va'];self.newlife31=self.states['newlife31']['va'];self.state52=self.states['ui52']['va']
  self.hooks=[];self.routines=[];self.changed=[];self.serial=0;self.snprintf=self.plt('snprintf');self.trace23=self.old['persist_new_life_checkpoint23']['stub'];self.journal55=self.old['v55_append_native_life_journal']['stub']
 def finish(self,out):
  assert self.cursor<min(va for s,va in self.base['strings'].items()if va>=self.rxva+0x180000)
  assert self.string_cursor<=self.rxva+self.added_size
  for s,va in self.strings.items():
   if s in self.base['strings']:continue
   data=s.encode()+b'\0';off=self.off(va);assert self.blob[off:off+len(data)]==b'\0'*len(data);self.blob[off:off+len(data)]=data;self.changed.append([va,len(data),'literal1120'])
  self.changed.append([self.code_start,self.cursor-self.code_start,'new code1120'])
  sites={r['site']for r in self.hooks};self.manifest['hooks']=[r for r in self.manifest['hooks']if r['site']not in sites]+self.hooks;self.manifest['routines']+=self.routines
  self.manifest.update(binary_sha256=hashlib.sha256(self.blob).hexdigest(),strings=self.strings,states=self.states,repair1120_base=BASE,repair1120_code=[self.code_start,self.cursor],repair1120_changes=self.changed,repair1120_headers=[])
  Path(out).write_text(json.dumps(self.manifest,indent=2)+'\n');return bytes(self.blob)
if __name__=='__main__':
 from repair_1120.fixes import hooks
 b=Patch(Path(sys.argv[1]).read_bytes(),sys.argv[2]);hooks(b);Path(sys.argv[3]).write_bytes(b.finish(sys.argv[4]))
