"""Pinned reproduction, allowed native byte ranges and state/ELF boundaries."""
import hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
import io
from school_finance1125.native import Patch,BASE
from school_finance1125.fixes import hooks
W=Path('/workspace/build_work/school_finance1125')
def check():
 before=Path('/workspace/build_work/hotfix1124/libil2cpp.so').read_bytes();raw=(W/'libil2cpp.so').read_bytes();manifest=json.loads((W/'native.json').read_text());assert hashlib.sha256(before).hexdigest()==BASE;assert hashlib.sha256(raw).hexdigest()==manifest['binary_sha256'];assert len(raw)==len(before)==145358848
 a=ELFFile(io.BytesIO(before));b=ELFFile(io.BytesIO(raw));assert a.header==b.header;assert [dict(s.header)for s in a.iter_segments()]==[dict(s.header)for s in b.iter_segments()]
 segments=[dict(s.header)for s in b.iter_segments()if s['p_type']=='PT_LOAD'];allowed=[]
 for va,n,name in manifest['school1125_changes']:
  seg=next(s for s in segments if s['p_vaddr']<=va and va+n<=s['p_vaddr']+s['p_filesz']);assert seg['p_flags']==5,(name,seg['p_flags']);off=va-seg['p_vaddr']+seg['p_offset'];allowed.append((off,off+n))
 changed=[i for i,(x,y)in enumerate(zip(before,raw))if x!=y];assert all(any(lo<=i<hi for lo,hi in allowed)for i in changed)
 state=manifest['states']['school1125'];whole=manifest['states']['era_world'];assert whole['va']+64000==state['va']and state['va']+state['size']==whole['va']+whole['size'];assert state['va']>=manifest['states']['repair1123']['va']+manifest['states']['repair1123']['size']
 bld=Patch(before,'/workspace/build_work/hotfix1124/native.json');hooks(bld);repro=bld.finish(W/'reproduction_manifest.json');assert repro==raw
 report=dict(passed=True,native_sha256=hashlib.sha256(raw).hexdigest(),base_sha256=BASE,native_bytes=len(raw),changed_bytes=len(changed),ELF_headers_and_segments_identical=True,all_changes_within_declared_RX_ranges=True,new_RW_state=state,new_state_does_not_overlap_previous_states=True,byte_identical_reproduction=True,metadata_cell_1124=hex(manifest['hotfix1124_metadata_cell']),phone_tested=False)
 (W/'native_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':check()
