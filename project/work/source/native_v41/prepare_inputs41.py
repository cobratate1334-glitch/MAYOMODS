"""Extract pinned v40 inputs; authoring retains the full TextAsset snapshot."""
import hashlib,json,sys,zipfile
from pathlib import Path
import UnityPy
BASE_SHA='847d39d1fd4ff6fa63101638bf8b8b9c8436289e3ad39ce235d173bc9cb8fabb'
def prepare(base,out):
 base,out=Path(base),Path(out);out.mkdir(parents=True,exist_ok=True)
 assert hashlib.sha256(base.read_bytes()).hexdigest()==BASE_SHA
 with zipfile.ZipFile(base)as z:
  for src,dst in [('lib/arm64-v8a/libil2cpp.so','libil2cpp.so'),('assets/bin/Data/Managed/Metadata/global-metadata.dat','global-metadata.dat')]:
   (out/dst).write_bytes(z.read(src))
  env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'))
 assets={o.read().m_Name:o.read().m_Script for o in env.objects if o.type.name=='TextAsset'}
 Path('analysis').mkdir(exist_ok=True);Path('analysis/base_assets.json').write_text(json.dumps(assets,ensure_ascii=True)+'\n')
 print(json.dumps({'TextAssets':len(assets),'checked_base':True}))
if __name__=='__main__':prepare(*sys.argv[1:])
