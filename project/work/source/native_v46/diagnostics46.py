"""Update release labels without changing Android executable code."""
import hashlib,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
from native_v30.dex_startup30 import Dex,checksum
def build(apk):
 with zipfile.ZipFile(apk)as z:before=z.read('classes13.dex')
 old=Dex(before);out=bytearray(before);changes=[]
 for i,value in enumerate(old.strings):
  if b'v42'not in value:continue
  updated=value.replace(b'v42',b'v46');assert len(updated)==len(value)
  offset=old.u32(old.u32(60)+4*i);_,start=old.uleb(offset);assert out[start:start+len(value)]==value
  out[start:start+len(value)]=updated;changes.append(dict(index=i,offset=start,before=value.decode(),after=updated.decode()))
 after=checksum(out);new=Dex(after)
 assert old.types==new.types and old.protos==new.protos and old.method_ids==new.method_ids and old.methods==new.methods
 assert all(old.code(i)==new.code(i)for i in old.methods)
 assert new.strings==sorted(new.strings)and len(set(new.strings))==len(new.strings)
 restored=bytearray(after)
 for r in changes:restored[r['offset']:r['offset']+len(r['before'].encode())]=r['before'].encode()
 assert checksum(restored)==before and changes
 (ROOT/'classes13.dex').write_bytes(after)
 report=dict(passed=True,sha256=hashlib.sha256(after).hexdigest(),version_strings=changes,every_Dex_method_byte_identical=True,exact_inverse_verified=True)
 (ROOT/'diagnostics46_validation.json').write_text(json.dumps(report,indent=2)+'\n');print('Updated',len(changes),'diagnostic version labels',flush=True)
if __name__=='__main__':build(sys.argv[1])
