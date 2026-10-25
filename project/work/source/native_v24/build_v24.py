"""Package v24's native game integration, preserving the exact old signer."""
import copy,hashlib,io,json,os,struct,subprocess,sys,zipfile
from collections import Counter
from pathlib import Path
import UnityPy
from PIL import Image,ImageOps
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
from build_prison_expansion import signature_entry,sha_file
from manifest_version import bump_version
from native_v10.registry_format import repair as repair_registry
from native_animation24 import FRAME_COUNT,PREFIX
BUNDLE='assets/bin/Data/datapack.unity3d';DATA='assets/bin/Data/data.unity3d';LIB='lib/arm64-v8a/libil2cpp.so'
BASE_SHA='b63744c39d6fff4d8226412ebf85f3a58bc3a9b67f7a310884ce7799ba429608'
NATIVE_BASE_SHA='bd0c21d3dbbc12e710b174d4c4551938512fb7a3b65fdd165ca15cfd472c2425'
def sha(v):return hashlib.sha256(v).hexdigest()
def key(o):return o.assets_file.name,o.path_id
def snapshots(env):return {key(o):sha(o.get_raw_data())for o in env.objects}
def run(args):return subprocess.run(list(map(str,args)),capture_output=True,text=True,check=True).stdout.strip()
def build(base,out,native_path,original_native_path):
 base=Path(base).resolve();out=Path(out).resolve();out.mkdir(exist_ok=True,parents=True)
 assert sha_file(base)==BASE_SHA,'Use the delivered v23 APK, retaining its package and signing certificate.'
 native=Path(native_path).read_bytes();original=Path(original_native_path).read_bytes();assert sha(original)==NATIVE_BASE_SHA
 names=['native_validation.json','eligibility_validation.json','registry_validation.json','engine24_validation.json','inherited21_validation.json','startup24_validation.json']
 reports={name:json.loads((ROOT/name).read_text())for name in names};hooks=json.loads((ROOT/'native_hooks.json').read_text())
 assert all(v['binary_sha256']==sha(native)for v in[hooks,*reports.values()]),'Validate the exact native output.'
 elf=ELFFile(io.BytesIO(original));loads=[s for s in elf.iter_segments()if s['p_type']=='PT_LOAD'];permitted=set(range(32,40))|set(range(56,58))
 for hook in hooks['hooks']:
  segment=next(s for s in loads if s['p_vaddr']<=hook['site']<s['p_vaddr']+s['p_filesz']);offset=segment['p_offset']+hook['site']-segment['p_vaddr'];permitted.update(range(offset,offset+4))
 differences={i for i in range(len(original))if original[i]!=native[i]};assert differences<=permitted
 dex=json.loads((ROOT/'dex_validation.json').read_text());assert dex['12']['byte_for_byte_preserved']and dex['13']['persistent_crash_capture']and all(v['roundtrip']for v in dex.values())
 sources=list((ROOT/'java/com/chance/bitlifediag').glob('*.java'))+[SOURCE/'native_v15/java/com/chance/bitlifediag'/n for n in ['NamePackUI.java','PackCatalog.java','PackFormat.java']]
 assert dex['13']['source_sha256']=={p.name:sha(p.read_bytes())for p in sources}
 logging=json.loads((ROOT/'logging23_validation.json').read_text());assert logging['passed']and logging['persistent_errors_and_previous_sessions']
 assets=json.loads((ROOT/'assets.json').read_text());assets['genesis_feature_containers'],_=repair_registry(assets['genesis_feature_containers'])
 assert 'a16_voltron_componentFilenames'not in assets
 with zipfile.ZipFile(base)as z:
  env=UnityPy.load(z.read(BUNDLE));data=UnityPy.load(z.read(DATA));manifest,manifest_change=bump_version(z.read('AndroidManifest.xml'),old=1067,new=1068)
  assert z.read('classes12.dex')==(ROOT/'classes12.dex').read_bytes()
  original_JNI_sha=sha(z.read('lib/arm64-v8a/libmayo21.so'))
 print('Updating native game resources and importing transparent tornado frames.',flush=True)
 before=snapshots(env);before_data=snapshots(data)
 texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'};textures={o.read().m_Name:o for o in env.objects if o.type.name=='Texture2D'};sprites={o.read().m_Name:o for o in env.objects if o.type.name=='Sprite'}
 rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree();oldpaths=copy.deepcopy(tree['m_Container']);olddeps=copy.deepcopy(tree['m_DependentAssets'])
 resources_id=next(i+1 for i,e in enumerate(rm.assets_file.externals)if e.path=='resources.assets')
 file=texts['genesis_music_studio'].assets_file;next_id=max(file.objects)+1;changed=set();added={};new_objects=set()
 for name,text in assets.items():
  if name in texts:obj=texts[name];changed.add(key(obj))
  else:
   obj=copy.copy(texts['genesis_test_feature_events']);obj.path_id=next_id;next_id+=1;obj.data=texts['genesis_test_feature_events'].get_raw_data();file.objects[obj.path_id]=obj;new_objects.add(key(obj));added[name]=obj.path_id
   path=('genesis_lists/'if text.startswith('{')else'genesis/')+name;assert path not in dict(tree['m_Container']);tree['m_Container'].append((path,dict(m_FileID=resources_id,m_PathID=obj.path_id)))
  value=obj.read();value.m_Name=name;value.m_Script=text;value.save()
 tx_template=textures['a16_emoji-v12-europa'];sp_template=sprites['a16_emoji-v12-europa'];dimension=256;graphics={};gifpath=ROOT/'media/tornado_house.gif'
 with Image.open(gifpath)as gif:
  assert gif.n_frames==FRAME_COUNT
  for frame in range(FRAME_COUNT):
   gif.seek(frame);im=gif.convert('RGBA');assert im.getchannel('A').getextrema()==(0,255)
   fit=ImageOps.contain(im,(dimension,dimension),Image.Resampling.LANCZOS);canvas=Image.new('RGBA',(dimension,dimension));canvas.paste(fit,((dimension-fit.width)//2,(dimension-fit.height)//2))
   full='a16_emoji-'+PREFIX+str(frame);assert full not in textures and full not in sprites
   txo=copy.copy(tx_template);txo.path_id=next_id;next_id+=1;txo.data=tx_template.get_raw_data();file.objects[txo.path_id]=txo
   spo=copy.copy(sp_template);spo.path_id=next_id;next_id+=1;spo.data=sp_template.get_raw_data();file.objects[spo.path_id]=spo;new_objects.update([key(txo),key(spo)])
   st=spo.read_typetree();st['m_Name']=full;st['m_RD']['texture']=dict(m_FileID=0,m_PathID=txo.path_id);digest=hashlib.sha256(full.encode()).digest();st['m_RenderDataKey']=({f'data[{i}]':struct.unpack_from('<I',digest,i*4)[0]for i in range(4)},21300000)
   st['m_Rect']['width']=st['m_Rect']['height']=dimension;st['m_RD']['textureRect']['width']=st['m_RD']['textureRect']['height']=dimension;st['m_RD']['uvTransform']['y']=st['m_RD']['uvTransform']['w']=dimension/2
   vertices=bytearray(st['m_RD']['m_VertexData']['m_DataSize'])
   for vertex in range(4):
    for axis in range(2):
     offset=vertex*12+axis*4;struct.pack_into('<f',vertices,offset,struct.unpack_from('<f',vertices,offset)[0]*dimension/128)
   st['m_RD']['m_VertexData']['m_DataSize']=bytes(vertices);spo.save_typetree(st)
   tx=txo.read();tx.m_Name=full;tx.set_image(canvas,target_format=4);tx.save()
   for obj in [txo,spo]:tree['m_Container'].append(('emoji/normal/'+full,dict(m_FileID=resources_id,m_PathID=obj.path_id)))
   graphics[full]=dict(texture=txo.path_id,sprite=spo.path_id,pixel_sha256=sha(canvas.tobytes()),duration_ms=gif.info.get('duration',70))
 tree['m_Container'].sort(key=lambda p:p[0]);rm.save_typetree(tree)
 bundle=next(iter(env.files.values())).save(packer='original');databytes=next(iter(data.files.values())).save(packer='original')
 print('Checking Unity round trip, ordered resource registration and preservation.',flush=True)
 check_env=UnityPy.load(bundle);check_data=UnityPy.load(databytes);objects={key(o):o for o in check_env.objects}
 assert len(objects)==len(before)+len(new_objects)
 for k,obj in objects.items():
  if k not in changed|new_objects:assert sha(obj.get_raw_data())==before[k],k
 checktexts={o.read().m_Name:o.read().m_Script for o in check_env.objects if o.type.name=='TextAsset'}
 for name,text in assets.items():assert checktexts[name]==text
 for name,record in graphics.items():
  tx=objects[(file.name,record['texture'])].read();sp=objects[(file.name,record['sprite'])].read();assert sha(tx.image.tobytes())==record['pixel_sha256'];assert tx.image.getchannel('A').getextrema()==(0,255)
  assert tx.m_Width==tx.m_Height==dimension and sp.m_Name==name and sp.m_RD.texture.path_id==record['texture']
  assert sp.m_Rect.width==sp.m_Rect.height==sp.m_RD.textureRect.width==sp.m_RD.textureRect.height==dimension
  assert sp.m_RD.m_VertexData.m_VertexCount==4 and sp.m_RD.m_SubMeshes[0].indexCount==6
 for obj in check_data.objects:
  if key(obj)!=key(rm):assert sha(obj.get_raw_data())==before_data[key(obj)]
 final_rm=next(o for o in check_data.objects if o.type.name=='ResourceManager').read_typetree();assert final_rm['m_DependentAssets']==olddeps
 oldcounts=Counter(json.dumps(p,sort_keys=True)for p in oldpaths);newcounts=Counter(json.dumps(p,sort_keys=True)for p in final_rm['m_Container']);assert not(oldcounts-newcounts)
 assert len(final_rm['m_Container'])==len(oldpaths)+len(added)+FRAME_COUNT*2
 valid={p.split('/')[-1].removeprefix('a16_emoji-')for p,_ in final_rm['m_Container']if p.startswith('emoji/normal/')}|{'hero'}
 for text in assets.values():
  if text.startswith('{'):
   for item in json.loads(text).get('Items',[]):assert item['Icon']in valid,item['Icon']
 for i in range(FRAME_COUNT):assert PREFIX+str(i)in valid
 dex13=(ROOT/'classes13.dex').read_bytes();assert b'chance_new_life_tools23'not in dex13 and b'Body & Genetics'not in dex13
 replacements={BUNDLE:bundle,DATA:databytes,LIB:native,'AndroidManifest.xml':manifest,'classes13.dex':dex13}
 unsigned=out/'v24-unsigned.tmp';stage=out/'v24-signed.tmp'
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
 with unsigned.open('r+b')as stream:stream.flush();os.fsync(stream.fileno())
 with zipfile.ZipFile(unsigned)as z:assert z.testzip()is None
 print('Signing and checking the APK with the existing update certificate.',flush=True)
 jar=SOURCE/'tools/apksig-8.7.3.jar';run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,stage,SOURCE/'signing/music-test-key.pem',SOURCE/'signing/music-test-cert.der'])
 signing={p:run(['java','-cp',jar,SOURCE/p,stage])for p in ['VerifyApk.java','VerifyNativeSigner.java']}
 assert all('verified=true'in v for v in signing.values())and all(t in signing['VerifyApk.java']for t in ['v2=true','v3=true','errors=[]','warnings=[]'])
 assert run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',base])==signing['VerifyNativeSigner.java']
 with zipfile.ZipFile(base)as old,zipfile.ZipFile(stage)as new,stage.open('rb')as stream:
  assert new.testzip()is None and len(new.namelist())==len(set(new.namelist()));kept={n for n in old.namelist()if not signature_entry(n)};assert kept=={n for n in new.namelist()if not signature_entry(n)};entry_differences=[]
  for entry in new.infolist():
   if signature_entry(entry.filename):continue
   previous=old.read(entry.filename);current=new.read(entry.filename);assert current==replacements.get(entry.filename,previous),entry.filename
   if current!=previous:entry_differences.append(entry.filename)
   if entry.compress_type==zipfile.ZIP_STORED:
    stream.seek(entry.header_offset+26);nm,ex=struct.unpack('<HH',stream.read(4));assert(entry.header_offset+30+nm+ex)%(16384 if entry.filename.endswith('.so')else 4)==0
  assert set(entry_differences)==set(replacements)and sha(new.read('lib/arm64-v8a/libmayo21.so'))==original_JNI_sha
 final=out/'BitLife_MayoMods_v24.apk';stage.replace(final);unsigned.unlink();backup=out/'BitLife_MayoMods_v24.zip'
 with zipfile.ZipFile(backup,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:z.write(final,final.name)
 with zipfile.ZipFile(backup)as z:assert z.testzip()is None and sha(z.read(final.name))==sha_file(final)
 report=dict(version='v24',apk=str(final),size=final.stat().st_size,sha256=sha_file(final),base_sha256=BASE_SHA,versionCode=1068,manifest_version=manifest_change,changed_apk_entries=entry_differences,preserved_apk_entries=len(kept)-len(entry_differences),existing_signer_retained=True,stock_appearance_assets_preserved=True,native_New_Life_controls=True,separate_Android_New_Life_panel_removed=True,player_and_relationship_Profile_measurements=True,genetic_traits_native_attributes=True,stock_Start_methods_unhooked=True,transparent_tornado_Unity_animation=True,tornado_frames=FRAME_COUNT,tornado_duration_ms=sum(v['duration_ms']for v in graphics.values()),animation_source_sha256=sha_file(gifpath),native_changes_outside_listed_sites=False,new_text_assets=len(added),preserved_Unity_objects=len(before)-len(changed),persistent_LOG=True,native_checks=reports,content_checks=json.loads((ROOT/'content_validation.json').read_text()),dex_checks=dex,logging_checks=logging,graphics=graphics,signing=signing,device_runtime_tested=False)
 (ROOT/'verification.json').write_text(json.dumps(report,indent=2)+'\n');(out/'BitLife_MayoMods_v24_verification.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:report[k]for k in['apk','size','sha256','versionCode','existing_signer_retained','device_runtime_tested']}),flush=True)
if __name__=='__main__':build(*sys.argv[1:])
