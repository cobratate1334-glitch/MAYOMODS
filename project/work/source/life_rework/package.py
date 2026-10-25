"""Hash-pinned 1103 -> 1104 APK; preserve every other payload and resource."""
import copy,csv,hashlib,io,json,struct,sys,zipfile
from pathlib import Path
import UnityPy
from PIL import Image
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent;sys.path[:0]=[str(SOURCE)]
from life_rework.content import build,csv_text
from native_v45.assets45 import codec
from native_v27.manifest_version import bump_version
from native_v55.build_v55 import signature_entry,symbols
BASE='3604ad2010155202727ede62ae368bbd25e8ede658de4e02544f7b4551d46f32'
def sha(b):return hashlib.sha256(b).hexdigest()

def sprite_tree(sprite,texture,image,name):
 st=sprite.read_typetree();w,h=image.size;st['m_Name']=name
 digest=hashlib.sha256(('1104/'+name).encode()).digest();st['m_RenderDataKey']=({f'data[{i}]':struct.unpack_from('<I',digest,i*4)[0]for i in range(4)},21300000)
 st.update(m_Rect=dict(x=0.,y=0.,width=float(w),height=float(h)),m_Offset=dict(x=0.,y=0.),m_Pivot=dict(x=.5,y=.5),m_PixelsToUnits=100.,m_IsPolygon=False,m_AtlasTags=[],m_SpriteAtlas=dict(m_FileID=0,m_PathID=0),m_PhysicsShape=[])
 rd=st['m_RD'];rd.update(texture=dict(m_FileID=0,m_PathID=texture.path_id),alphaTexture=dict(m_FileID=0,m_PathID=0),secondaryTextures=[],textureRect=dict(x=0.,y=0.,width=float(w),height=float(h)),textureRectOffset=dict(x=0.,y=0.),atlasRectOffset=dict(x=0.,y=0.),settingsRaw=64,uvTransform=dict(x=100.,y=w/2,z=100.,w=h/2),downscaleMultiplier=1.)
 rd['m_IndexBuffer']=struct.pack('<6H',0,1,2,0,2,3);rd['m_SubMeshes']=[dict(firstByte=0,indexCount=6,topology=0,baseVertex=0,firstVertex=0,vertexCount=4,localAABB=dict(m_Center=dict(x=0.,y=0.,z=0.),m_Extent=dict(x=w/200,y=h/200,z=0.)))]
 v=rd['m_VertexData'];v['m_VertexCount']=4
 for c in v['m_Channels']:c.update(stream=0,offset=0,format=0,dimension=0)
 v['m_Channels'][0].update(dimension=3);v['m_Channels'][4].update(stream=1,dimension=2);v['m_DataSize']=struct.pack('<20f',-w/200,-h/200,0,-w/200,h/200,0,w/200,h/200,0,w/200,-h/200,0,0,0,0,1,1,1,1,0)
 return st

def bundles(z):
 env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'));data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'))
 key=lambda o:(o.assets_file.name,o.path_id)
 before={key(o):o.get_raw_data()for o in env.objects};before_data={key(o):o.get_raw_data()for o in data.objects}
 texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'};base={n:o.read().m_Script for n,o in texts.items()};overlay=build(base)
 decode,encode=codec();teams=json.loads((ROOT/'references/teams.json').read_text());by={r['index']:r for r in teams};rows=list(csv.DictReader(io.StringIO(decode(base['a16_sports-teams-enc']))));original=[dict(r)for r in rows]
 for r in rows:r['Name']=by[int(r['Index'])]['name']
 assert all({k:v for k,v in x.items()if k!='Name'}=={k:v for k,v in y.items()if k!='Name'}for x,y in zip(original,rows));overlay['a16_sports-teams-enc']=encode(csv_text(rows))
 file=texts['genesis_feature_containers'].assets_file;next_id=max(file.objects)+1
 rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree();paths=copy.deepcopy(tree['m_Container']);rid=next(i+1 for i,e in enumerate(rm.assets_file.externals)if e.path=='resources.assets');changed=set()
 for name,value in overlay.items():
  if name in texts:o=texts[name]
  else:
   o=copy.copy(texts['genesis_test_feature_events']);o.path_id=next_id;next_id+=1;o.data=o.get_raw_data();file.objects[o.path_id]=o
   path=('genesis_lists/'if value.startswith('{')else'genesis/')+name;assert not any(p==path for p,_ in tree['m_Container']);tree['m_Container'].append((path,dict(m_FileID=rid,m_PathID=o.path_id)))
  v=o.read();v.m_Name=name;v.m_Script=value;v.save();changed.add(key(o))
 tt=next(o for o in env.objects if o.type.name=='Texture2D');sp=next(o for o in env.objects if o.type.name=='Sprite'and o.read().m_Name=='49-basilica');imported=[];icons={}
 for name,path in [('reddit',ROOT/'inputs/reddit.png'),('ufc',ROOT/'inputs/ufc.png')]+[('teams/'+str(r['index']),ROOT/'inputs/teams'/f'{r["index"]}.png')for r in teams]:
  image=Image.open(path).convert('RGBA');image.thumbnail((192,192));texture=copy.copy(tt);texture.path_id=next_id;next_id+=1;texture.data=tt.get_raw_data();file.objects[texture.path_id]=texture;v=texture.read();v.m_Name='1104_'+name;v.set_image(image,target_format=4);v.save()
  sprite=copy.copy(sp);sprite.path_id=next_id;next_id+=1;sprite.data=sp.get_raw_data();file.objects[sprite.path_id]=sprite;sprite.save_typetree(sprite_tree(sprite,texture,image,v.m_Name));resource='mayomods1104/'+name
  assert not any(p==resource for p,_ in tree['m_Container']);tree['m_Container']+=[(resource,dict(m_FileID=rid,m_PathID=o.path_id))for o in [texture,sprite]];icons[name]=(texture,image)
  imported.append(dict(resource=resource,texture_id=texture.path_id,sprite_id=sprite.path_id,source_sha256=sha(path.read_bytes()),pixel_sha256=sha(image.tobytes())))
 # Retain the original CTA's resource IDs; replace only its icon's sprite
 # geometry/texture reference. Shared packed atlases remain untouched.
 for o in list(env.objects):
  if o.type.name=='Sprite'and o.read().m_Name in ['community_button_icon','a16_multiPurposeCommunityIcon']:
   texture,image=icons['reddit'];o.save_typetree(sprite_tree(o,texture,image,o.read().m_Name));changed.add(key(o))
 tree['m_Container'].sort(key=lambda x:x[0]);rm.save_typetree(tree)
 pack=next(iter(env.files.values())).save(packer='original');rawdata=next(iter(data.files.values())).save(packer='original')
 final=UnityPy.load(pack);objects={key(o):o for o in final.objects};assert before.keys()<=objects.keys();assert all(objects[k].get_raw_data()==raw for k,raw in before.items()if k not in changed)
 actual={o.read().m_Name:o.read().m_Script for k,o in objects.items()if k in changed and o.type.name=='TextAsset'};assert actual==overlay
 by_id={o.path_id:o for o in final.objects}
 for r in imported:
  assert sha(by_id[r['texture_id']].read().image.convert('RGBA').tobytes())==r['pixel_sha256'];assert sha(by_id[r['sprite_id']].read().image.convert('RGBA').tobytes())==r['pixel_sha256']
 finaldata=UnityPy.load(rawdata);objects_data={key(o):o for o in finaldata.objects};assert objects_data.keys()==before_data.keys();assert all(objects_data[k].get_raw_data()==raw for k,raw in before_data.items()if k!=key(rm))
 from collections import Counter
 canonical=lambda rows:Counter((p,json.dumps(v,sort_keys=True))for p,v in rows)
 assert canonical(paths)<=canonical(next(o for o in finaldata.objects if o.type.name=='ResourceManager').read_typetree()['m_Container'])
 return pack,rawdata,dict(passed=True,content_assets=len(overlay),teams=len(teams),imported_images=imported,preserved_objects=len(before)-len(changed&before.keys()),changed_objects=len(changed&before.keys()),old_resources_preserved=True,datapack_sha256=sha(pack),data_sha256=sha(rawdata))

def stage(base,work):
 work=Path(work);base=Path(base);assert sha(base.read_bytes())==BASE
 native=(work/'libil2cpp.so').read_bytes();manifest=json.loads((work/'native.json').read_text());assert sha(native)==manifest['binary_sha256']
 for n in ['native_validation.json','content_validation.json']:
  r=json.loads((work/n).read_text());assert r['passed'];assert n!='native_validation.json'or r['binary_sha256']==sha(native)
 dex=(work/'dex1104/classes13.dex').read_bytes();r=json.loads((work/'dex1104/dex_validation.json').read_text());assert r['passed']and sha(dex)==r['binary_sha256']
 with zipfile.ZipFile(base)as z:
  pack,data,report=bundles(z);(work/'bundle_validation.json').write_text(json.dumps(report,indent=2)+'\n')
  rocket=z.read('lib/arm64-v8a/libRocketGames.so');old=b'Occupation: Modder\nLocation: Backrooms';new=b'MayoMods\n.gg/mayomods';assert rocket.count(old)==1 and len(new)<=len(old);rocket=rocket.replace(old,new+b'\0'*(len(old)-len(new)))
  metadata_name='assets/bin/Data/Managed/Metadata/global-metadata.dat';metadata=z.read(metadata_name);assert metadata.count(b'BitLife Community')==4;metadata=metadata.replace(b'BitLife Community',b'Modding community');assert len(metadata)==len(z.read(metadata_name))
  android,_=bump_version(z.read('AndroidManifest.xml'),old=1103,new=1104)
  changes={'lib/arm64-v8a/libil2cpp.so':native,'lib/arm64-v8a/libRocketGames.so':rocket,'classes13.dex':dex,'assets/bin/Data/datapack.unity3d':pack,'assets/bin/Data/data.unity3d':data,metadata_name:metadata,'AndroidManifest.xml':android,'assets/mayomods54/native_symbols.json':json.dumps(symbols(native,manifest),indent=2).encode()}
  for f in (work/'site').rglob('*'):
   if f.is_file():changes['assets/mayoweb/'+f.relative_to(work/'site').as_posix()]=f.read_bytes()
  target=work/'MayoMods_1104_UNSIGNED_WORK.apk';assert not target.exists()
  with zipfile.ZipFile(target,'x',allowZip64=False)as w:
   for entry in z.infolist():
    if signature_entry(entry.filename):continue
    info=copy.copy(entry);info.extra=b''
    if info.compress_type==zipfile.ZIP_STORED:
     alignment=16384 if info.filename.endswith('.so')else 4;pos=w.fp.tell()+30+len(info.filename.encode())
     if pos%alignment:
      pad=(-pos-4)%alignment
      if pad<2:pad+=alignment
      info.extra=struct.pack('<HHH',0xd935,pad,alignment)+b'\0'*(pad-2)
    w.writestr(info,changes.get(info.filename,z.read(info.filename)))
  with zipfile.ZipFile(target)as final:
   assert final.testzip()is None and len(set(final.namelist()))==len(final.namelist());assert {n for n in final.namelist()if not signature_entry(n)}=={n for n in z.namelist()if not signature_entry(n)}
   assert all(final.read(n)==raw for n,raw in changes.items());assert all(final.read(n)==z.read(n)for n in z.namelist()if n not in changes and not signature_entry(n))
  (work/'staging_report.json').write_text(json.dumps(dict(staged=True,signed=False,base_sha256=BASE,apk_sha256=sha(target.read_bytes()),native_sha256=sha(native),modified_entries=sorted(changes),version_code=1104,physical_phone_tested=False),indent=2)+'\n');print(target)
if __name__=='__main__':stage(*sys.argv[1:])
