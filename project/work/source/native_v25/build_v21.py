"""Build and verify v21 against the exact v16 base, retaining unrelated bytes."""
import copy,csv,hashlib,io,json,os,struct,subprocess,sys,zipfile
from collections import Counter
from pathlib import Path
import UnityPy
from PIL import Image,ImageOps

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
sys.path.insert(0,str(ROOT))
from build_prison_expansion import signature_entry,sha_file
from manifest_version import bump_version
from native_v10.registry_format import repair as repair_registry
BUNDLE='assets/bin/Data/datapack.unity3d'
DATA='assets/bin/Data/data.unity3d'
LIB='lib/arm64-v8a/libil2cpp.so'
BASE_SHA='89be86661928ecdd8b88a1f5286b513f5af64c89cbb470b484292626d1abbc75'

def sha(value):return hashlib.sha256(value).hexdigest()
def key(obj):return(obj.assets_file.name,obj.path_id)
def objects(env):return{key(o):sha(o.get_raw_data())for o in env.objects}
def run(args):return subprocess.run(list(map(str,args)),capture_output=True,text=True,check=True).stdout.strip()
def message(value):print(value,flush=True)

def build(base,out,native_path):
 base=Path(base).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
 assert sha_file(base)==BASE_SHA,'requires the exact delivered v16 base'
 native=Path(native_path).read_bytes()
 tests=json.loads((ROOT/'native_validation.json').read_text())
 hooks=json.loads((ROOT/'native_hooks.json').read_text())
 eligibility_tests=json.loads((ROOT/'eligibility_validation.json').read_text())
 release_tests=json.loads((ROOT/'release21_validation.json').read_text())
 registry_tests=json.loads((ROOT/'registry_validation.json').read_text())
 inherited_tests=json.loads((ROOT/'inherited21_validation.json').read_text())
 assert tests['binary_sha256']==hooks['binary_sha256']==eligibility_tests['binary_sha256']==release_tests['binary_sha256']==registry_tests['binary_sha256']==inherited_tests['binary_sha256']==sha(native),'validate exact native output first'
 assets=json.loads((ROOT/'assets.json').read_text())
 assert not any('appearance_trait' in q['name'] or 'skin_traits' in q['name'] or 'albinism' in q['name'] or 'hair_evolution' in q['name'] for q in hooks['hooks'])
 assert 'a16_voltron_componentFilenames' not in assets
 assets['genesis_feature_containers'],_=repair_registry(assets['genesis_feature_containers'])
 with zipfile.ZipFile(base)as old:
  env=UnityPy.load(old.read(BUNDLE));data=UnityPy.load(old.read(DATA));original_native=old.read(LIB)
  manifest,manifest_change=bump_version(old.read('AndroidManifest.xml'))
 # The bridges touch their listed instruction sites and the ELF size fields.
 from elftools.elf.elffile import ELFFile
 elf=ELFFile(io.BytesIO(original_native));segments=list(elf.iter_segments());loads=[s for s in segments if s['p_type']=='PT_LOAD']
 tail=loads[-1];header=elf['e_phoff']+segments.index(tail)*56
 permitted=set(range(32,40))|set(range(56,58))
 for hook in hooks['hooks']:
  segment=next(s for s in loads if s['p_vaddr']<=hook['site']<s['p_vaddr']+s['p_filesz'])
  off=segment['p_offset']+hook['site']-segment['p_vaddr'];permitted.update(range(off,off+4))
 changed_native={i for i in range(len(original_native))if original_native[i]!=native[i]}
 assert changed_native<=permitted
 message('Native output verified; loading content and original appearance assets')
 before=objects(env);before_data=objects(data)
 texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'}
 textures={o.read().m_Name:o for o in env.objects if o.type.name=='Texture2D'}
 sprites={o.read().m_Name:o for o in env.objects if o.type.name=='Sprite'}
 rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree()
 oldpaths=copy.deepcopy(tree['m_Container']);olddeps=copy.deepcopy(tree['m_DependentAssets'])
 resources_id=next(i+1 for i,e in enumerate(rm.assets_file.externals)if e.path=='resources.assets')
 file=texts['genesis_music_studio'].assets_file;next_id=max(file.objects)+1
 changed=set();added={};new_objects=set()
 for name,text in assets.items():
  if name in texts:obj=texts[name];changed.add(key(obj))
  else:
   obj=copy.copy(texts['genesis_test_feature_events']);obj.path_id=next_id;next_id+=1
   obj.data=texts['genesis_test_feature_events'].get_raw_data();file.objects[obj.path_id]=obj
   new_objects.add(key(obj));added[name]=obj.path_id
   path=('genesis_lists/'if text.startswith('{')else'genesis/')+name
   assert path not in dict(tree['m_Container']);tree['m_Container'].append((path,dict(m_FileID=resources_id,m_PathID=obj.path_id)))
  value=obj.read();value.m_Name=name;value.m_Script=text;value.save()
 portraits={};portrait_ids=[] # Original portrait assets stay byte-for-byte intact.
 new_objects.update((file.name,id_)for id_ in portrait_ids)
 tx_template=textures['a16_emoji-v12-europa'];sp_template=sprites['a16_emoji-v12-europa']
 inputs={
  'v18-champions':Path('release-input/logos/1000002283.jpg'),
  'v18-europa':Path('release-input/logos/1000002285.png'),
  'v18-conference':Path('release-input/logos/1000002284.png'),
  'v18-storm':Path('upload/04-1000002328.png'),
  'v18-truck':Path('upload/03-1000002329.jpg'),
  'v18-vinicius':Path('upload/01-1000002880.jpg'),
  'v18-haaland':Path('upload/02-1000002878.jpg'),
  'v18-bellingham':Path('upload/03-1000002427.jpg'),
  'v19-euros':Path('upload/01-1000002323.png'),
  'v19-copa':Path('upload/02-1000002322.jpg'),
  'v19-yamal':Path('upload/05-1000002324.jpg'),
  'v19-ronaldo':Path('upload/06-1000002325.png'),
  'v19-neymar':Path('upload/07-1000002326.png'),
  'v19-messi':Path('upload/08-1000002327.png'),
  'v19-mbappe':Path('upload/09-1000002399.png'),
  'v19-lingard':Path('upload/10-1000002405.png'),
  'v20-us-map':ROOT/'media/us_map.jpg','v21-chase-minivan':ROOT/'media/chase_minivan.jpg'}
 icons={}
 legacy={'v18-champions':'v16-champions','v18-europa':'v12-europa','v18-conference':'v12-conference'}
 for token,path in inputs.items():
  full='a16_emoji-'+token;im=Image.open(path).convert('RGBA');dimension=512 if token=='v20-us-map' else 128;fit=ImageOps.contain(im,(dimension,dimension),Image.Resampling.LANCZOS)
  canvas=Image.new('RGBA',(dimension,dimension));canvas.paste(fit,((dimension-fit.width)//2,(dimension-fit.height)//2))
  txo=copy.copy(tx_template);txo.path_id=next_id;next_id+=1;txo.data=tx_template.get_raw_data();file.objects[txo.path_id]=txo
  spo=copy.copy(sp_template);spo.path_id=next_id;next_id+=1;spo.data=sp_template.get_raw_data();file.objects[spo.path_id]=spo
  new_objects.update([key(txo),key(spo)])
  st=spo.read_typetree();st['m_Name']=full;st['m_RD']['texture']=dict(m_FileID=0,m_PathID=txo.path_id)
  digest=hashlib.sha256(full.encode()).digest();st['m_RenderDataKey']=({f'data[{i}]':struct.unpack_from('<I',digest,i*4)[0]for i in range(4)},21300000)
  if dimension!=128:
   st['m_Rect']['width']=st['m_Rect']['height']=dimension
   st['m_RD']['textureRect']['width']=st['m_RD']['textureRect']['height']=dimension
   st['m_RD']['uvTransform']['y']=st['m_RD']['uvTransform']['w']=dimension/2
   vertices=bytearray(st['m_RD']['m_VertexData']['m_DataSize'])
   for vertex in range(4):
    for axis in range(2):
     offset=vertex*12+axis*4;value=struct.unpack_from('<f',vertices,offset)[0];struct.pack_into('<f',vertices,offset,value*dimension/128)
   st['m_RD']['m_VertexData']['m_DataSize']=bytes(vertices)
  spo.save_typetree(st)
  tx=txo.read();tx.m_Name=full;tx.set_image(canvas,target_format=4);tx.save()
  for obj in[txo,spo]:tree['m_Container'].append(('emoji/normal/'+full,dict(m_FileID=resources_id,m_PathID=obj.path_id)))
  icons[full]=dict(texture=txo.path_id,sprite=spo.path_id,source=str(path),source_sha256=sha_file(path),pixel_sha256=sha(canvas.tobytes()))
  # Keep earlier entry dialogs consistent with the replacement full logos.
  if token in legacy:
   oldfull='a16_emoji-'+legacy[token];obj=textures[oldfull];tx=obj.read();tx.set_image(canvas,target_format=4);tx.save();changed.add(key(obj))
   icons[oldfull]=dict(texture=obj.path_id,sprite=sprites[oldfull].path_id,source=str(path),source_sha256=sha_file(path),pixel_sha256=sha(canvas.tobytes()))
 tree['m_Container'].sort(key=lambda p:p[0]);rm.save_typetree(tree)
 message('Saving game data; checking all untouched Unity objects')
 bundle=next(iter(env.files.values())).save(packer='original');databytes=next(iter(data.files.values())).save(packer='original')
 check_env=UnityPy.load(bundle);check_data=UnityPy.load(databytes)
 assert len(list(check_env.objects))==len(before)+len(new_objects)
 objmap={key(o):o for o in check_env.objects}
 for obj in check_env.objects:
  if key(obj)not in changed|new_objects:assert sha(obj.get_raw_data())==before[key(obj)],key(obj)
 for name,text in assets.items():
  obj=next(o for o in check_env.objects if o.type.name=='TextAsset'and o.read().m_Name==name)
  assert obj.read().m_Script==text
 for name,record in (portraits|icons).items():
  tx=objmap[(file.name,record['texture'])].read();sp=objmap[(file.name,record['sprite'])].read()
  assert sha(tx.image.tobytes())==record['pixel_sha256'],name
  assert tx.m_Width==tx.m_Height==(512 if name=='a16_emoji-v20-us-map' else 128)
  assert sp.m_Name==name and sp.m_RD.texture.path_id==record['texture']
  assert sp.m_Rect.width==sp.m_Rect.height==tx.m_Width
  assert sp.m_RD.textureRect.width==sp.m_RD.textureRect.height==tx.m_Width
  assert sp.m_RD.m_VertexData.m_VertexCount==4 and sp.m_RD.m_SubMeshes[0].indexCount==6
 for obj in check_data.objects:
  if key(obj)!=key(rm):assert sha(obj.get_raw_data())==before_data[key(obj)]
 final_rm=next(o for o in check_data.objects if o.type.name=='ResourceManager').read_typetree()
 assert final_rm['m_DependentAssets']==olddeps
 oldcounts=Counter(json.dumps(p,sort_keys=True)for p in oldpaths);newcounts=Counter(json.dumps(p,sort_keys=True)for p in final_rm['m_Container'])
 assert not(oldcounts-newcounts)
 assert len(final_rm['m_Container'])==len(oldpaths)+len(added)+len(portrait_ids)+len(inputs)*2
 valid_icons={p.split('/')[-1].removeprefix('a16_emoji-')for p,v in final_rm['m_Container']if p.startswith('emoji/normal/')}|{'hero'}
 for text in assets.values():
  if text.startswith('{'):
   for item in json.loads(text).get('Items',[]):assert item['Icon']in valid_icons,item['Icon']
 message('Content preservation passed; packaging APK')
 replacements={BUNDLE:bundle,DATA:databytes,LIB:native,'classes12.dex':(ROOT/'classes12.dex').read_bytes(),'classes13.dex':(ROOT/'classes13.dex').read_bytes(),'AndroidManifest.xml':manifest}
 additions={'lib/arm64-v8a/libmayo21.so':(ROOT/'libmayo21.so').read_bytes(),'assets/mayo21/us_map.jpg':(ROOT/'media/us_map.jpg').read_bytes(),'assets/mayo21/tornado_house.gif':(ROOT/'media/tornado_house.gif').read_bytes()}
 unsigned=out/'v21-unsigned.tmp';stage=out/'v21-signed.tmp'
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(unsigned,'w',allowZip64=False)as new:
  for entry in old.infolist():
   if signature_entry(entry.filename):continue
   info=copy.copy(entry);info.extra=b''
   if info.compress_type==zipfile.ZIP_STORED:
    align=16384 if info.filename.endswith('.so')else 4;position=new.fp.tell()+30+len(info.filename.encode())
    if position%align:
     pad=(-position-4)%align
     if pad<2:pad+=align
     info.extra=struct.pack('<HHH',0xd935,pad,align)+b'\0'*(pad-2)
   new.writestr(info,replacements.get(entry.filename,old.read(entry.filename)),compresslevel=6)
  for name,payload in additions.items():
   info=zipfile.ZipInfo(name);info.compress_type=zipfile.ZIP_STORED;info.date_time=(2026,10,9,0,0,0)
   align=16384 if name.endswith('.so')else 4;position=new.fp.tell()+30+len(name.encode())
   if position%align:
    pad=(-position-4)%align
    if pad<2:pad+=align
    info.extra=struct.pack('<HHH',0xd935,pad,align)+b'\0'*(pad-2)
   new.writestr(info,payload)
 with unsigned.open('r+b')as stream:stream.flush();os.fsync(stream.fileno())
 assert zipfile.ZipFile(unsigned).testzip()is None
 jar=SOURCE/'tools/apksig-8.7.3.jar'
 run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,stage,SOURCE/'signing/music-test-key.pem',SOURCE/'signing/music-test-cert.der'])
 signing={p:run(['java','-cp',jar,SOURCE/p,stage])for p in['VerifyApk.java','VerifyNativeSigner.java']}
 assert all('verified=true'in value for value in signing.values())
 assert all(token in signing['VerifyApk.java']for token in['v2=true','v3=true','errors=[]','warnings=[]'])
 baseline_signer=run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',base])
 assert baseline_signer==signing['VerifyNativeSigner.java'],'existing update signer must be retained'
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(stage)as new,stage.open('rb')as stream:
  assert new.testzip()is None and len(new.namelist())==len(set(new.namelist()))
  assert{x for x in old.namelist()if not signature_entry(x)}=={x for x in new.namelist()if not signature_entry(x)}-set(additions)
  for entry in new.infolist():
   if signature_entry(entry.filename):continue
   assert new.read(entry.filename)==(additions[entry.filename]if entry.filename in additions else replacements.get(entry.filename,old.read(entry.filename))),entry.filename
   if entry.compress_type==zipfile.ZIP_STORED:
    stream.seek(entry.header_offset+26);nm,ex=struct.unpack('<HH',stream.read(4));assert(entry.header_offset+30+nm+ex)%(16384 if entry.filename.endswith('.so')else 4)==0
 final=out/'BitLife_MayoMods_v21.apk';stage.replace(final);unsigned.unlink()
 backup=out/'BitLife_MayoMods_v21.zip'
 with zipfile.ZipFile(backup,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:z.write(final,final.name)
 with zipfile.ZipFile(backup)as z:assert sha(z.read(final.name))==sha_file(final)
 result=dict(apk=str(final),size=final.stat().st_size,sha256=sha_file(final),backup=str(backup),base_sha256=BASE_SHA,changed_apk_entries=list(replacements),native_original_bytes_changed=len(changed_native),retained_v16_hooks=True,public_launcher=True,manifest_version=manifest_change,original_rocket_library_preserved=True,preserved_resource_registrations=len(oldpaths),new_text_assets=len(added),new_portrait_layers=len(portraits),new_icons=len(inputs),preserved_datapack_objects=len(before)-len(changed),preserved_data_objects=len(before_data)-1,graphics=icons,content_tests=json.loads((ROOT/'content_validation.json').read_text()),native_tests=tests,dex_tests=json.loads((ROOT/'dex_validation.json').read_text()),signing=signing,existing_signer_retained=True,device_runtime_tested=False)
 result['registry_tests']=registry_tests
 result['eligibility_tests']=eligibility_tests
 result['release21_tests']=release_tests
 result['inherited21_tests']=inherited_tests
 result['original_appearance_restored']=True
 result['new_life_native_buttons']=True
 result['new_life_start_interception_removed']=True
 result['profile_measurements']=True
 result['direct_relationship_stories']=True
 result['retired_ineligible_seasons']=True
 result['scoped_transparent_tornado_animation']=True
 result['added_apk_entries']=list(additions)
 result['jni_tests']=json.loads((ROOT/'jni_validation.json').read_text())
 assert result['jni_tests']['sha256']==sha(additions['lib/arm64-v8a/libmayo21.so'])
 result['current_residence_disasters']=True
 (ROOT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
 (out/'BitLife_MayoMods_v21_verification.json').write_text(json.dumps(result,indent=2)+'\n')
 message(json.dumps({k:result[k]for k in['apk','size','sha256','new_portrait_layers','new_icons','existing_signer_retained','device_runtime_tested']}))

if __name__=='__main__':build(*sys.argv[1:])
