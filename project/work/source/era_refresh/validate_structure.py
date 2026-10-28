"""Bind added code and every modified byte to the pinned native input."""
import hashlib,io,json,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent

def validate(base,binary,manifest,out):
 old=Path(base).read_bytes();raw=Path(binary).read_bytes();d=json.loads(Path(manifest).read_text());assert hashlib.sha256(old).hexdigest()==d['era_refresh_base'];assert hashlib.sha256(raw).hexdigest()==d['binary_sha256']
 e=ELFFile(io.BytesIO(raw));loads=[s for s in e.iter_segments()if s['p_type']=='PT_LOAD'];off=lambda a:next(s['p_offset']+a-s['p_vaddr']for s in loads if s['p_vaddr']<=a<s['p_vaddr']+s['p_filesz'])
 allowed=bytearray(len(old))
 for a,n,_ in d['era_refresh_changes']:
  x=off(a)
  if x<len(old):allowed[x:min(x+n,len(old))]=b'\1'*min(n,len(old)-x)
 for x,n in d['era_refresh_headers']:allowed[x:x+n]=b'\1'*n
 unexpected=[i for i,(a,b)in enumerate(zip(old,raw))if a!=b and not allowed[i]];assert not unexpected,unexpected[:12]
 assert all(s['p_flags']&3!=3 for s in loads)
 for i,s in enumerate(loads):
  assert s['p_offset']%16384==s['p_vaddr']%16384
  assert all(not(max(s['p_vaddr'],t['p_vaddr'])<min(s['p_vaddr']+s['p_memsz'],t['p_vaddr']+t['p_memsz']))for t in loads[i+1:])
 code0,code1=d['era_refresh_code'];_,va,n=d['era_refresh_rx'];assert va<=code0<code1<=va+n
 report=dict(passed=True,binary_sha256=d['binary_sha256'],unchanged_bytes_outside_declared_ranges=True,old_native_bytes_checked=len(old),new_RX_code_bytes=code1-code0,WX_pages=False,ELF_16KB_alignment=True,overlapping_load_segments=False);Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
