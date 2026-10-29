"""Add selected resources without changing old art, IDs or serialized objects."""
import copy,hashlib,json
import UnityPy
from era_world.content import build
from era_world.artwork import artwork
from life_rework.package import sprite_tree
from playable_repair.asset_contracts import verify_resources
from collections import Counter

sha=lambda b:hashlib.sha256(b).hexdigest()
def bundle(z):
 env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'));data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'));key=lambda o:(o.assets_file.name,o.path_id)
 before={key(o):o.get_raw_data()for o in env.objects};before_data={key(o):o.get_raw_data()for o in data.objects}
 texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'};base={k:o.read().m_Script for k,o in texts.items()};overlay=build(base)
 file=texts['genesis_feature_containers'].assets_file;next_id=max(file.objects)+1;changed=set()
 rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree();old_paths=copy.deepcopy(tree['m_Container']);rid=next(i+1 for i,e in enumerate(rm.assets_file.externals)if e.path=='resources.assets')
 for name,value in overlay.items():
  if name in texts:obj=texts[name]
  else:
   assert name=='genesis_v18_included1119',name
   template=texts['genesis_v18_community35'];obj=copy.copy(template);obj.path_id=next_id;next_id+=1;obj.data=template.get_raw_data();file.objects[obj.path_id]=obj;texts[name]=obj
   tree['m_Container'].append(('genesis_lists/'+name,dict(m_FileID=rid,m_PathID=obj.path_id)))
  d=obj.read();d.m_Name=name;d.m_Script=value;d.save();changed.add(key(obj))
 template=next(o for o in file.objects.values()if o.type.name=='Texture2D');sprite=next(o for o in file.objects.values()if o.type.name=='Sprite');images=[]
 for resource,im,meta in artwork():
  assert resource.startswith('native1119/')and not any(p==resource for p,_ in tree['m_Container'])
  texture=copy.copy(template);texture.path_id=next_id;next_id+=1;texture.data=template.get_raw_data();file.objects[texture.path_id]=texture
  d=texture.read();d.m_Name=resource;d.set_image(im,target_format=4);d.m_IsReadable=True;d.save()
  sp=copy.copy(sprite);sp.path_id=next_id;next_id+=1;sp.data=sprite.get_raw_data();file.objects[sp.path_id]=sp;sp.save_typetree(sprite_tree(sp,texture,im,resource))
  tree['m_Container'].append((resource,dict(m_FileID=rid,m_PathID=sp.path_id)))
  images.append(dict(meta,resource=resource,sprite_id=sp.path_id,texture_id=texture.path_id,canvas=list(im.size),pixel_sha256=sha(im.tobytes())))
 tree['m_Container'].sort(key=lambda r:r[0]);rm.save_typetree(tree)
 pack=next(iter(env.files.values())).save(packer='original');rawdata=next(iter(data.files.values())).save(packer='original')
 final={key(o):o for o in UnityPy.load(pack).objects};assert before.keys()<=final.keys()
 assert all(final[k].get_raw_data()==v for k,v in before.items()if k not in changed)
 assert all(final[key(texts[k])].read().m_Script==v for k,v in overlay.items())
 outer=UnityPy.load(rawdata);after={key(o):o for o in outer.objects};assert before_data.keys()==after.keys()
 assert all(after[k].get_raw_data()==v for k,v in before_data.items()if k!=key(rm))
 canonical=lambda rows:Counter((p,json.dumps(v,sort_keys=True))for p,v in rows)
 paths=next(o for o in outer.objects if o.type.name=='ResourceManager').read_typetree()['m_Container'];assert canonical(old_paths)<=canonical(paths)
 checked=verify_resources(pack,rawdata,images)
 alias=[v for p,v in paths if p=='genesis_lists/genesis_v18_included1119'];assert len(alias)==1
 assert alias[0]==dict(m_FileID=rid,m_PathID=texts['genesis_v18_included1119'].path_id)
 included=final[key(texts['genesis_v18_included1119'])];assert included.type.name=='TextAsset'and included.assets_file.name=='resources.assets'
 assert json.loads(included.read().m_Script)['ListID']=='genesis_v18_included1119'
 report=dict(passed=True,changed_text_assets=sorted(overlay),text_asset_sha256={k:sha(v.encode())for k,v in overlay.items()},unchanged_unrelated_unity_objects=len(before)-len(changed&before.keys()),all_old_artwork_identical=True,all_old_resource_aliases_preserved=True,resource_validation=checked,imported_artwork=images,datapack_sha256=sha(pack),data_sha256=sha(rawdata))
 return pack,rawdata,report
