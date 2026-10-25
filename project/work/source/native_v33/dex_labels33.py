"""Update only equal-width version string data; preserve every DEX code item."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from native_v30.dex_startup30 import Dex,checksum

def build():
    before=(ROOT.parent/'native_v32/classes13.dex').read_bytes()
    old=Dex(before);out=bytearray(before);changes=[]
    for i,value in enumerate(old.strings):
        if b'v32' not in value:continue
        updated=value.replace(b'v32',b'v33');assert len(updated)==len(value)
        off=old.u32(old.u32(60)+4*i);_,start=old.uleb(off)
        assert bytes(out[start:start+len(value)])==value
        out[start:start+len(value)]=updated
        changes.append(dict(index=i,offset=start,before=value.decode(),after=updated.decode()))
    assert len(changes)==5
    after=checksum(out);new=Dex(after)
    assert old.types==new.types and old.protos==new.protos and old.method_ids==new.method_ids
    assert old.methods==new.methods and all(old.code(i)==new.code(i)for i in old.methods)
    assert new.strings==sorted(new.strings) and len(set(new.strings))==len(new.strings)
    restored=bytearray(after)
    for item in changes:
        value=item['before'].encode();restored[item['offset']:item['offset']+len(value)]=value
    assert checksum(restored)==before
    (ROOT/'classes13.dex').write_bytes(after)
    bridge=(ROOT.parent/'native_v32/classes14.dex').read_bytes();Dex(bridge)
    (ROOT/'classes14.dex').write_bytes(bridge)
    (ROOT/'launcher32_patch.json').write_bytes((ROOT.parent/'native_v32/launcher32_patch.json').read_bytes())
    result=dict(passed=True,changed_strings=changes,binary_sha256=hashlib.sha256(after).hexdigest(),bridge_sha256=hashlib.sha256(bridge).hexdigest(),
        every_method_code_item_byte_identical=True,identifiers_offsets_and_order_preserved=True,
        exact_inverse_verified=True,bridge_byte_identical=True)
    (ROOT/'labels33_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k!='changed_strings'}),flush=True)

if __name__=='__main__':build()
