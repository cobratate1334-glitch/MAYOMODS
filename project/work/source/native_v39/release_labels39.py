"""Change only equal-width component release labels; preserve every DEX instruction."""
import hashlib,json,struct,sys,zipfile,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from native_v30.dex_startup30 import Dex,checksum
def patch(base):
 with zipfile.ZipFile(base)as z:b=z.read('classes13.dex')
 old=Dex(b);out=bytearray(b);labels=[]
 for n,value in enumerate(old.strings):
  if b'v38'not in value:continue
  updated=value.replace(b'v38',b'v39');assert len(updated)==len(value)
  offset=old.u32(old.u32(60)+4*n);_,start=old.uleb(offset)
  out[start:start+len(value)]=updated;labels.append(dict(before=value.decode(),after=updated.decode()))
 assert labels
 result=checksum(out);new=Dex(result)
 assert old.types==new.types and old.protos==new.protos and old.method_ids==new.method_ids and old.methods==new.methods
 assert all(old.code(i)==new.code(i)for i in old.methods)
 assert new.strings==sorted(new.strings)and len(set(new.strings))==len(new.strings)
 assert result[12:32]==hashlib.sha1(result[32:]).digest()and struct.unpack_from('<I',result,8)[0]==zlib.adler32(result[12:])&0xffffffff
 (ROOT/'classes13.dex').write_bytes(result)
 report=dict(passed=True,sha256=hashlib.sha256(result).hexdigest(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),release_label_updates=labels,every_code_item_byte_identical=True,original_Play_method_and_callbacks_preserved=True,DEX_string_order_checksums_and_metadata_checked=True,ART_tested=False)
 (ROOT/'labels39_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':patch(sys.argv[1])
