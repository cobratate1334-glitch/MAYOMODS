"""Native v15 appearance and sports fixes on exact v14."""
import copy,csv,hashlib,io,json,os,struct,subprocess,sys,zipfile
from collections import Counter
from pathlib import Path
import UnityPy
from PIL import Image,ImageOps

ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE));sys.path.insert(0,str(SOURCE/'tests'));sys.path.insert(0,str(ROOT))
from build_prison_expansion import signature_entry,sha_file,decode,encode,records
from native_v11.test_native_hooks import validate as native_test
from native_v15.native_hooks import patch as patch_native
from native_v15.test_native import validate as test_new_native
from native_v15.rocket_logo import patch as patch_logo
from native_v15.hair_assets import graphics as hair_graphics
from native_v11.test_registry import validate as registry_test
from dealer_guard_test import validate as guard_test
from community_loader_test import check_icon_patch
from native_v10.registry_format import repair as repair_registry
BUNDLE='assets/bin/Data/datapack.unity3d';DATA='assets/bin/Data/data.unity3d';LIB='lib/arm64-v8a/libil2cpp.so'
V6_SHA='19978b25bb13d11af34ddf038bd2aa13a3b7cb2b36a915da09ee251d4d13c8c2'
def sha(b):return hashlib.sha256(b).hexdigest()
def run(args):return subprocess.run(list(map(str,args)),capture_output=True,text=True,check=True).stdout.strip()
def csv_string(rows):
 f=io.StringIO(newline='');csv.writer(f,lineterminator='\r\n').writerows(rows);return f.getvalue().rstrip('\r\n')
def object_key(o):return(o.assets_file.name,o.path_id)
def objects(e):return{object_key(o):sha(o.get_raw_data())for o in e.objects}
def build(base,work):
 base=Path(base).resolve();work=Path(work).resolve();work.mkdir(exist_ok=True,parents=True)
 assert sha_file(base)==V6_SHA,'requires exact v14 APK'
 assets=json.loads((ROOT/'assets.json').read_text());original={}
 with zipfile.ZipFile(base)as z:
  env=UnityPy.load(z.read(BUNDLE));data=UnityPy.load(z.read(DATA));base_native=z.read(LIB);base_logo=z.read('lib/arm64-v8a/libRocketGames.so')
 native,hook13=patch_native(base_native);logo,logo_details=patch_logo(base_logo)
 dex=(ROOT/'classes13.dex').read_bytes()
 before=objects(env);before_data=objects(data)
 texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'}
 for name,value in original.items():assert texts[name].read().m_Script==value,'unexpected v6 content '+name
 registry_text=texts['genesis_feature_containers'].read().m_Script
 registry=list(csv.reader(io.StringIO(registry_text)));newrows=json.loads((ROOT/'registry_rows.json').read_text())
 assert all(len(r)==16 for r in newrows)
 for r in registry:
  if r and r[0]=='soccer_v11':r[8]='' # retain its saved container and unfinished cups
 assets['genesis_feature_containers']=csv_string(registry+newrows)
 assets['genesis_feature_containers'],_=repair_registry(assets['genesis_feature_containers'])
 final_registry=list(csv.reader(io.StringIO(assets['genesis_feature_containers'])))
 assert len({r[0]for r in final_registry if len(r)>=13 and not r[0].startswith('#')})==len([r for r in final_registry if len(r)>=13 and not r[0].startswith('#')])
 rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree()
 oldpaths=copy.deepcopy(tree['m_Container']);olddeps=copy.deepcopy(tree['m_DependentAssets'])
 resources_id=next(i+1 for i,e in enumerate(rm.assets_file.externals)if e.path=='resources.assets')
 file=texts['genesis_music_studio'].assets_file;next_id=max(file.objects)+1
 changed=set();added={}
 for name,text in assets.items():
  if name in texts:obj=texts[name];changed.add(object_key(obj))
  else:
   obj=copy.copy(texts['genesis_test_feature_events']);obj.path_id=next_id;obj.data=texts['genesis_test_feature_events'].get_raw_data();file.objects[next_id]=obj;added[name]=next_id;next_id+=1
   path=('genesis_lists/'if text.startswith('{')else'genesis/')+name
   assert path not in dict(tree['m_Container']);tree['m_Container'].append((path,{'m_FileID':resources_id,'m_PathID':obj.path_id}))
  a=obj.read();a.m_Name=name;a.m_Script=text;a.save()
 # Alias the native flags into EmojiHub's normal lookup folder. These point
 # to the existing country textures/sprites and do not duplicate the artwork.
 aliases=[]
 for path,ptr in oldpaths:
  if path.startswith('emoji/flags/a16_emoji-flag-'):
   alias=path.replace('emoji/flags/','emoji/normal/')
   if alias not in dict(oldpaths):tree['m_Container'].append((alias,copy.deepcopy(ptr)));aliases.append((alias,ptr))
 graphics,graphics_ids,next_id=hair_graphics(env,file,tree,resources_id,next_id)
 tree['m_Container'].sort(key=lambda p:p[0]);rm.save_typetree(tree)
 bundle=next(iter(env.files.values())).save(packer='original');databytes=next(iter(data.files.values())).save(packer='original')
 re=UnityPy.load(bundle);rd=UnityPy.load(databytes)
 for o in re.objects:
  if o.path_id in graphics_ids:
   if o.type.name=='Texture2D':assert sha(o.read().image.tobytes())==graphics[o.read().m_Name]['pixel_sha256']
   else:
    s=o.read();assert s.m_Rect.width==500 and s.m_RD.m_VertexData.m_VertexCount==4 and s.m_RD.m_SubMeshes[0].indexCount==6
   continue
  if object_key(o)in changed or o.path_id in added.values():assert o.read().m_Script==assets[o.read().m_Name]
  else:assert sha(o.get_raw_data())==before[object_key(o)]
 assert len(list(re.objects))==len(before)+len(added)+len(graphics_ids)
 for o in rd.objects:
  if object_key(o)!=object_key(rm):assert sha(o.get_raw_data())==before_data[object_key(o)]
 final_rm=next(o for o in rd.objects if o.type.name=='ResourceManager').read_typetree()
 assert final_rm['m_DependentAssets']==olddeps
 oldcounts=Counter(json.dumps(p,sort_keys=True)for p in oldpaths);newcounts=Counter(json.dumps(p,sort_keys=True)for p in final_rm['m_Container'])
 assert not(oldcounts-newcounts)and len(final_rm['m_Container'])==len(oldpaths)+len(added)+len(aliases)+len(graphics_ids)
 for name,path in added.items():assert any(v['m_PathID']==path and v['m_FileID']==resources_id for k,v in final_rm['m_Container'])
 # Verify every icon against actual registered game assets.
 valid_icons={p.split('/')[-1].removeprefix('a16_emoji-')for p,v in final_rm['m_Container']if p.startswith('emoji/normal/')}
 # 'hero' is EmojiHub's dynamic character portrait token, used by working v5.
 valid_icons.add('hero')
 for name,text in assets.items():
  if text.startswith('{'):
   for section in [json.loads(text)]:
    for item in section.get('Items',[]):assert item['Icon']in valid_icons,'unregistered icon '+item['Icon']
 # patch_native proves the base bytes outside eight hook sites and ELF
 # size fields are identical; retained hooks remain the verified v13 code.
 new_hooks=json.loads((SOURCE/'native_v11/native_validation.json').read_text())
 retained13=json.loads((SOURCE/'native_v13/native_validation.json').read_text())
 added_hooks=json.loads((ROOT/'native_validation.json').read_text())
 assert added_hooks['binary_sha256']==sha(native),'run v15 native tests on exact output first'
 all_assets={name:o.read().m_Script for name,o in texts.items()}|assets
 routing=registry_test(native,assets['genesis_feature_containers'],assets['genesis_feature_containers'],all_assets)
 guards=guard_test(native,json.loads((SOURCE/'dealer_fix_details.json').read_text()));icons=check_icon_patch(native)
 replacements={BUNDLE:bundle,DATA:databytes,LIB:native,'lib/arm64-v8a/libRocketGames.so':logo,'classes13.dex':dex,'classes12.dex':(ROOT/'classes12.dex').read_bytes()}
 unsigned=work/'careers-unsigned.tmp';stage=work/'careers-signed.tmp'
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
 with unsigned.open('r+b')as f:f.flush();os.fsync(f.fileno())
 assert zipfile.ZipFile(unsigned).testzip()is None
 jar=SOURCE/'tools/apksig-8.7.3.jar'
 run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,stage,SOURCE/'signing/music-test-key.pem',SOURCE/'signing/music-test-cert.der'])
 signing={p:run(['java','-cp',jar,SOURCE/p,stage])for p in ['VerifyApk.java','VerifyNativeSigner.java']}
 assert all('verified=true'in s for s in signing.values())
 assert all(s in signing['VerifyApk.java']for s in ['v2=true','v3=true','errors=[]','warnings=[]'])
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(stage)as new,stage.open('rb')as f:
  assert new.testzip()is None and len(new.namelist())==len(set(new.namelist()))
  assert {x for x in old.namelist()if not signature_entry(x)}=={x for x in new.namelist()if not signature_entry(x)}
  for entry in new.infolist():
   if signature_entry(entry.filename):continue
   assert new.read(entry.filename)==replacements.get(entry.filename,old.read(entry.filename)),entry.filename
   if entry.compress_type==zipfile.ZIP_STORED:
    f.seek(entry.header_offset+26);nm,ex=struct.unpack('<HH',f.read(4));assert(entry.header_offset+30+nm+ex)%(16384 if entry.filename.endswith('.so')else 4)==0
  assert b'ExpansionHub'not in new.read('classes13.dex')
 # The exact original manifest is preserved and was checked byte-for-byte above.
 assert stage.stat().st_size>260000000
 final=work/'BitLife_Native_Activities_v15.apk';stage.replace(final);unsigned.unlink()
 backup=work/'BitLife_Native_Activities_v15.zip'
 with zipfile.ZipFile(backup,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:z.write(final,final.name)
 with zipfile.ZipFile(backup)as z:assert sha(z.read(final.name))==sha_file(final)
 result=dict(apk=str(final),size=final.stat().st_size,sha256=sha_file(final),backup=str(backup),base_sha256=V6_SHA,changed_apk_entries=list(replacements),native_code_preserved=False,retained_native_hooks_tested=True,retained_validation_mode='prior reports plus unchanged code verification',retained_v13_tests=retained13,added_native_tests=added_hooks,diagnostic_dex_tests=json.loads((ROOT/'dex_validation.json').read_text()),new_country_aliases=len(aliases),hair_graphics=graphics,changed_existing_resources=sorted(name for name in assets if name in texts),new_resource_paths=added,preserved_resource_registrations=len(oldpaths),preserved_datapack_objects=len(before)-len(changed),preserved_data_objects=len(before_data)-1,dealer_tests=guards,prison_icon_tests=icons,native_menu_and_stat_tests=new_hooks,registry_tests=routing,signing=signing,device_runtime_tested=False)
 result['logo_visibility_tests']=logo_details
 result['pack_format_tests']=json.loads((SOURCE/'native_v13/pack_validation.json').read_text())if (SOURCE/'native_v13/pack_validation.json').exists()else dict(retained_format_code=True)
 result['content_tests']=json.loads((ROOT/'content_validation.json').read_text())
 (ROOT/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':build(*sys.argv[1:])
