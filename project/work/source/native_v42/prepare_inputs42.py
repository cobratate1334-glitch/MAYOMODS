"""Extract exact released v41 inputs and refresh the complete Unity fixtures."""
import hashlib,json,sys,zipfile
from pathlib import Path
import UnityPy
BASE_SHA='24d02b5aaf9db8fa804db02a7cbb461d5f57306c78a98eaac7a0843b89f7028b'
def prepare(base,out):
 base,out=Path(base),Path(out);out.mkdir(parents=True,exist_ok=True)
 assert hashlib.sha256(base.read_bytes()).hexdigest()==BASE_SHA,'Supply the exact released v41 APK.'
 with zipfile.ZipFile(base)as z:
  for source,name in [('lib/arm64-v8a/libil2cpp.so','libil2cpp41.so'),('assets/bin/Data/Managed/Metadata/global-metadata.dat','global-metadata.dat')]:
   (out/name).write_bytes(z.read(source))
  env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'))
  data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'))
 assets={o.read().m_Name:o.read().m_Script for o in env.objects if o.type.name=='TextAsset'}
 resources=next(o for o in data.objects if o.type.name=='ResourceManager').read_typetree()
 analysis=Path('analysis');analysis.mkdir(exist_ok=True)
 (analysis/'base_assets.json').write_text(json.dumps(assets,ensure_ascii=True)+'\n')
 (analysis/'base_resources.json').write_text(json.dumps(resources,ensure_ascii=True)+'\n')
 print(json.dumps(dict(checked_base=True,TextAssets=len(assets),native_sha256=hashlib.sha256((out/'libil2cpp41.so').read_bytes()).hexdigest())),flush=True)
if __name__=='__main__':prepare(*sys.argv[1:])
