"""Retain v28 loader compatibility and update equal-width diagnostic labels."""
import hashlib,json,struct,sys,zipfile,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from native_v28.elf_compat28 import patch
BASE_SHA='b3c62262468e025b179f3293585867d30e634d3e7730d0a4645cb0a37195d751'
def sha(data):return hashlib.sha256(data).hexdigest()
def prepare(base,raw_path):
 assert sha(Path(base).read_bytes())==BASE_SHA
 raw=Path(raw_path).read_bytes();manifest=ROOT/'native_hooks.json';hooks=json.loads(manifest.read_text())
 assert hooks['binary_sha256']==sha(raw)
 native,report=patch(raw,'libil2cpp.so');(ROOT/'libil2cpp.so').write_bytes(native)
 hooks['unnormalized_sha256']=sha(raw);hooks['binary_sha256']=sha(native)
 hooks['loader_metadata']=report;manifest.write_text(json.dumps(hooks,indent=2)+'\n')
 (ROOT/'elf29_patch.json').write_text(json.dumps(report,indent=2)+'\n')
 known=json.loads((ROOT.parent/'native_v28/dex13_validation.json').read_text())['source_sha256']
 for path in sorted((ROOT.parent/'native_v28/java').rglob('*.java')):
  assert sha(path.read_bytes())==known[path.name]
  dest=ROOT/'java'/path.relative_to(ROOT.parent/'native_v28/java');dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_bytes(path.read_bytes().replace(b'v28',b'v29'))
 with zipfile.ZipFile(base)as z:dex=z.read('classes13.dex')
 assert sha(dex)=='b69ab2ea9ab34380fd4b864339aac753c2b83e62766d0948356b95a14dac9ed4'
 updated=bytearray(dex);changed=[];strings=[];allowed=set()
 count,table=struct.unpack_from('<II',dex,56)
 for i in range(count):
  start=struct.unpack_from('<I',dex,table+i*4)[0]
  while dex[start]&128:start+=1
  start+=1;end=dex.index(b'\0',start);old=dex[start:end];new=old.replace(b'v28',b'v29')
  assert len(old)==len(new)
  if old!=new:changed.append(i);updated[start:end]=new;allowed.update(range(start,end))
  strings.append(new)
 assert changed==[116,485,486,487,511]
 assert all(strings[i-1]<=strings[i]<=strings[i+1]for i in changed)
 assert {i for i in range(32,len(dex))if updated[i]!=dex[i]}<=allowed
 updated[12:32]=hashlib.sha1(updated[32:]).digest();struct.pack_into('<I',updated,8,zlib.adler32(updated[12:])&0xffffffff)
 (ROOT/'classes13.dex').write_bytes(updated)
 check=dict(original_sha256=sha(dex),binary_sha256=sha(updated),changed_string_ids=changed,
            all_code_items_and_offsets_preserved=True,string_sorting_preserved=True,
            only_equal_width_build_labels_and_DEX_checksums_changed=True,
            source_sha256={p.name:sha(p.read_bytes())for p in sorted((ROOT/'java').rglob('*.java'))})
 (ROOT/'dex29_validation.json').write_text(json.dumps(check,indent=2)+'\n')
 print(json.dumps(dict(native_sha256=sha(native),classes13_sha256=sha(updated),labels_changed=len(changed))),flush=True)
if __name__=='__main__':prepare(*sys.argv[1:])
