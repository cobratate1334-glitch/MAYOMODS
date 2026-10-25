"""Extract pinned 1104 build inputs into a private directory; never into Git."""
import hashlib,json,os,sys,zipfile
from pathlib import Path
import UnityPy
from life_followup.package import BASE
from life_followup.native import BASE as NATIVE

def extract(apk,out):
    apk=Path(apk);assert hashlib.sha256(apk.read_bytes()).hexdigest()==BASE
    out=Path(out);out.mkdir(exist_ok=True);os.umask(0o077)
    with zipfile.ZipFile(apk)as z:
        native=z.read('lib/arm64-v8a/libil2cpp.so');assert hashlib.sha256(native).hexdigest()==NATIVE
        (out/'base_1104.so').write_bytes(native)
        env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'))
        texts={o.read().m_Name:o.read().m_Script for o in env.objects if o.type.name=='TextAsset'}
        (out/'base_assets.json').write_text(json.dumps(texts))
    print('Extracted pinned native and',len(texts),'TextAssets')
if __name__=='__main__':extract(*sys.argv[1:])
