"""Keep launch diagnostics current without changing any startup bytecode."""
import hashlib,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from native_v30.dex_startup30 import Dex,checksum

HELP='In the game’s New Life page, edit adult height, weight, wingspan, genetic trait, personality and appearance trait. Tap a field to choose; Back keeps your changes. Your baby grows with age toward the selected adult targets. US Map shows regions.\n\nTap your name → Profile for current height, weight and wingspan. Relationships → a person → Profile shows their measurements and life story. Chasing careers are in Special Careers.'

def patch(raw):
    d=Dex(raw);out=bytearray(raw);changed=[]
    strings=[s.replace(b'v30',b'v31')for s in d.strings]
    info=next(i for i,s in enumerate(strings)if s.startswith('In the game’s New Life page,'.encode()))
    strings[info]=HELP.encode()
    assert strings==sorted(strings)
    for i,(old,new)in enumerate(zip(d.strings,strings)):
        if old==new:continue
        pos=d.u32(d.u32(60)+i*4);count,start=d.uleb(pos)
        assert len(old)==len(new)and count==len(new.decode().encode('utf-16-le'))//2,(i,len(old),len(new))
        out[start:start+len(new)]=new;changed.append(i)
    result=checksum(out);new=Dex(result)
    assert d.method_ids==new.method_ids and d.methods==new.methods
    assert all(d.code(i)==new.code(i)for i,(_,off)in d.methods.items()if off)
    report=dict(binary_sha256=hashlib.sha256(result).hexdigest(),changed_string_ids=changed,
        all_startup_and_logging_code_items_byte_identical=True,
        current_native_New_Life_instructions=True)
    (ROOT/'classes13.dex').write_bytes(result)
    (ROOT/'labels31_patch.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)

if __name__=='__main__':
    with zipfile.ZipFile(sys.argv[1])as z:patch(z.read('classes13.dex'))
