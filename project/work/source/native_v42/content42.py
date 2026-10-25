"""Append v42 portrait resources while retaining every other Unity object."""
import copy,hashlib,json,sys,zipfile
from collections import Counter
from pathlib import Path
import UnityPy
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT.parent))
from portrait_assets42 import author,graphics
BASE_SHA='24d02b5aaf9db8fa804db02a7cbb461d5f57306c78a98eaac7a0843b89f7028b'
sha=lambda b:hashlib.sha256(b).hexdigest()
def build(base,out):
 assert sha(Path(base).read_bytes())==BASE_SHA
 changes=author(base);allbase=json.loads(Path('analysis/base_assets.json').read_text());assets={**allbase,**changes}
 (ROOT/'assets.json').write_text(json.dumps(assets,indent=2)+'\n')
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(base)as z:env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'));data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'))
 key=lambda o:(o.assets_file.name,o.path_id)
 before={key(o):sha(o.get_raw_data())for o in env.objects};bd={key(o):sha(o.get_raw_data())for o in data.objects}
 texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'};rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree();paths=copy.deepcopy(tree['m_Container']);deps=copy.deepcopy(tree['m_DependentAssets'])
 rid=next(n+1 for n,e in enumerate(rm.assets_file.externals)if e.path=='resources.assets');file=texts['a16_voltron_componentFilenames'].assets_file
 for n,value in changes.items():a=texts[n].read();a.m_Script=value;a.save()
 registered,added,next_id=graphics(env,file,tree,rid,max(file.objects)+1)
 assert not({(file.name,x)for x in added}&set(before))
 tree['m_Container'].sort(key=lambda x:x[0]);rm.save_typetree(tree)
 bundle=next(iter(env.files.values())).save(packer='original');db=next(iter(data.files.values())).save(packer='original');(out/'datapack.unity3d').write_bytes(bundle);(out/'data.unity3d').write_bytes(db)
 ae=UnityPy.load(bundle);ad=UnityPy.load(db);after={key(o):sha(o.get_raw_data())for o in ae.objects};afterd={key(o):sha(o.get_raw_data())for o in ad.objects}
 assert set(before)<=set(after)and{k for k in before if before[k]!=after[k]}=={key(texts['a16_voltron_componentFilenames'])}
 assert set(bd)==set(afterd)and{k for k in bd if bd[k]!=afterd[k]}=={key(rm)}
 reread=next(o for o in ad.objects if o.type.name=='ResourceManager').read_typetree()
 assert Counter((k,json.dumps(v,sort_keys=True))for k,v in paths)<=Counter((k,json.dumps(v,sort_keys=True))for k,v in reread['m_Container'])and reread['m_DependentAssets']==deps
 textures={o.read().m_Name:o for o in ae.objects if o.type.name=='Texture2D'};sprites={o.read().m_Name:o for o in ae.objects if o.type.name=='Sprite'}
 catalog=json.loads((ROOT/'portrait42_catalog.json').read_text())
 for item in catalog:
  n=item['name'];texture=textures[n].read();assert texture.m_Width==texture.m_Height==500
  assert sha(texture.image.convert('RGBA').tobytes())==registered[n]['pixel_sha256']
  st=sprites[n].read_typetree();assert st['m_RD']['texture']['m_PathID']==registered[n]['texture'] and st['m_Rect']['width']==500
  matches=[x for p,x in reread['m_Container']if p==item['path']];assert {x['m_PathID']for x in matches}=={registered[n]['texture'],registered[n]['sprite']}
 result=dict(passed=True,datapack_sha256=sha(bundle),data_sha256=sha(db),assets_sha256=sha((ROOT/'assets.json').read_bytes()),portrait_styles=156,new_Texture2D_and_Sprite_objects=312,all_unedited_Unity_objects_preserved=True,all_existing_resource_paths_preserved=True,portrait_texture_roundtrip_verified=True,device_runtime_tested=False)
 (ROOT/'content42_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':build(*sys.argv[1:])
