"""Update text resources; preserve every existing sprite, texture and ID."""
import copy,hashlib,json,sys,zipfile
from pathlib import Path
from collections import Counter
import UnityPy
ROOT=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest()

def build(base):
 a=json.loads((ROOT/'assets.json').read_text())
 with zipfile.ZipFile(base)as z:pack=z.read('assets/bin/Data/datapack.unity3d');data=z.read('assets/bin/Data/data.unity3d')
 env=UnityPy.load(pack);dataenv=UnityPy.load(data);original={o.path_id:(o.type.name,o.get_raw_data())for o in env.objects};texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'}
 file=texts['genesis_feature_containers'].assets_file;nextid=max(file.objects)+1
 rm=next(o for o in dataenv.objects if o.type.name=='ResourceManager');tree=rm.read_typetree();beforepaths=copy.deepcopy(tree['m_Container']);rid=next(i+1 for i,e in enumerate(rm.assets_file.externals)if e.path=='resources.assets');changed=[];new=[]
 for name,value in a.items():
  if name in texts:
   obj=texts[name];t=obj.read()
   if t.m_Script==value:continue
  else:
   obj=copy.copy(texts['genesis_test_feature_events']);obj.path_id=nextid;nextid+=1;obj.data=obj.get_raw_data();file.objects[obj.path_id]=obj;t=obj.read();t.m_Name=name
   resource=('genesis_lists/'if value.startswith('{')else'genesis/')+name
   assert not any(p==resource for p,v in tree['m_Container']);tree['m_Container'].append((resource,dict(m_FileID=rid,m_PathID=obj.path_id)));new.append(name)
  t.m_Script=value;t.save();changed.append(name)
 tree['m_Container'].sort(key=lambda x:x[0]);rm.save_typetree(tree);assert Counter((p,json.dumps(v,sort_keys=True))for p,v in beforepaths)<=Counter((p,json.dumps(v,sort_keys=True))for p,v in tree['m_Container'])
 out=ROOT/'bundles';out.mkdir(exist_ok=True)
 raw=next(iter(env.files.values())).save(packer='original');newdata=next(iter(dataenv.files.values())).save(packer='original');(out/'datapack.unity3d').write_bytes(raw);(out/'data.unity3d').write_bytes(newdata)
 decoded=UnityPy.load(raw);checks=0;seen=set()
 for o in decoded.objects:
  if o.path_id not in original:assert o.type.name=='TextAsset'and o.read().m_Name in new;continue
  typ,oldraw=original[o.path_id];seen.add(o.path_id)
  if oldraw!=o.get_raw_data():assert typ=='TextAsset'and o.read().m_Name in changed
  if typ=='TextAsset'and o.read().m_Name in a:assert o.read().m_Script==a[o.read().m_Name]
  checks+=1
 assert seen==original.keys()
 # Every narrative image points to an existing supplied asset.
 resources={p for p,v in tree['m_Container']}
 for name in ['49-basilica','49-gate','49-priest','49-bishop','49-cardinal','49-conclave','49-smoke','49-pope','49-handshake','49-community']:
  assert 'mayomods49/icons/'+name in resources;checks+=1
 report=dict(passed=True,checks=checks,datapack_sha256=sha(raw),data_sha256=sha(newdata),changed_text_assets=changed,new_resources=new,all_prior_objects_retained=True,all_Sprites_and_Textures_byte_identical=True,existing_resource_multiset_preserved=True,physical_phone_tested=False,Unity_rendering_tested=False)
 (ROOT/'content54_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=checks,changed=len(changed),new=len(new))),flush=True)

if __name__=='__main__':build(sys.argv[1])
