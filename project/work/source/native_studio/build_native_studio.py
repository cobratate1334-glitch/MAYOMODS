"""Build integrated studio on v4 content, restoring the v3 native/diagnostic base."""
import copy,csv,hashlib,io,json,os,struct,subprocess,sys,zipfile
from pathlib import Path
import UnityPy

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE));sys.path.insert(0,str(SOURCE/'tests'))
from build_prison_expansion import signature_entry,sha_file
from dealer_guard_test import validate as guard_test
from community_loader_test import check_icon_patch
BUNDLE='assets/bin/Data/datapack.unity3d'
DATA='assets/bin/Data/data.unity3d'
LIB='lib/arm64-v8a/libil2cpp.so'
BRIDGE='lib/arm64-v8a/libchance_expansion.so'
V4_SHA='c937876ebd518ce6a4c5095439f37bd22b496b4e97b0988166af5a199073dd8f'
V3_SHA='92bf5dd7373b764d1c80fc0035842736548f08ebc09c3486869debf4f97b5bef'
def sha(b):return hashlib.sha256(b).hexdigest()
def run(args):return subprocess.run(list(map(str,args)),capture_output=True,text=True,check=True).stdout.strip()
def object_key(o):return (o.assets_file.name,o.path_id)
def objects(env):return {object_key(o):sha(o.get_raw_data())for o in env.objects}
def build(v4,v3,work,tools):
 v4=Path(v4).resolve();v3=Path(v3).resolve();work=Path(work).resolve();tools=Path(tools).resolve();work.mkdir(exist_ok=True,parents=True)
 assert sha_file(v4)==V4_SHA and sha_file(v3)==V3_SHA
 assets=json.loads((ROOT/'assets.json').read_text())
 with zipfile.ZipFile(v4)as z:env=UnityPy.load(z.read(BUNDLE));data=UnityPy.load(z.read(DATA))
 before=objects(env);before_data=objects(data)
 texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'}
 assert not(set(assets)&set(texts))
 registry=texts['genesis_feature_containers'];r=registry.read();old_registry=r.m_Script
 if isinstance(old_registry,bytes):old_registry=old_registry.decode()
 stream=io.StringIO(newline='');csv.writer(stream,lineterminator='\n').writerow(['music_studio','Music Studio','','genesis_music_studio_defaults','genesis_music_studio_ageup','content','','','T1','Music Studio','mic-studio','Produce and release your own music',0,'genesis_music_studio_hub','',''])
 r.m_Script=old_registry.rstrip('\r\n')+'\n'+stream.getvalue().rstrip('\n');r.save()
 file=registry.assets_file
 next_id=max(file.objects)+1
 added={}
 for name,text in assets.items():
  clone=copy.copy(texts['genesis_test_feature_events']);clone.path_id=next_id;clone.data=texts['genesis_test_feature_events'].get_raw_data();file.objects[next_id]=clone
  a=clone.read();a.m_Name=name;a.m_Script=text;a.save();added[name]=next_id;next_id+=1
 rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree()
 original_container=copy.deepcopy(tree['m_Container']);original_dependents=copy.deepcopy(tree['m_DependentAssets'])
 resources_id=next(i+1 for i,x in enumerate(rm.assets_file.externals)if x.path=='resources.assets')
 for name,path in added.items():
  resource=('genesis_lists/'if name in ['genesis_music_studio_hub','genesis_music_studio_project','genesis_music_studio_catalog']else'genesis/')+name
  assert resource not in dict(tree['m_Container']);tree['m_Container'].append((resource,{'m_FileID':resources_id,'m_PathID':path}))
 tree['m_Container'].sort(key=lambda p:p[0]);rm.save_typetree(tree)
 bundle=next(iter(env.files.values())).save(packer='original');databytes=next(iter(data.files.values())).save(packer='original')
 re=UnityPy.load(bundle);rd=UnityPy.load(databytes)
 for o in re.objects:
  if o.path_id==registry.path_id:assert o.read().m_Script==r.m_Script
  elif o.path_id in added.values():assert o.read().m_Script==assets[o.read().m_Name]
  else:assert sha(o.get_raw_data())==before[object_key(o)]
 assert len(list(re.objects))==len(before)+len(added)
 for o in rd.objects:
  if object_key(o)!=object_key(rm):assert sha(o.get_raw_data())==before_data[object_key(o)]
 final_rm=next(o for o in rd.objects if o.type.name=='ResourceManager').read_typetree()
 assert final_rm['m_DependentAssets']==original_dependents
 from collections import Counter
 old_counts=Counter(json.dumps(pair,sort_keys=True)for pair in original_container)
 new_counts=Counter(json.dumps(pair,sort_keys=True)for pair in final_rm['m_Container'])
 assert not(old_counts-new_counts)
 assert len(final_rm['m_Container'])==len(original_container)+len(added)
 for name,path in added.items():assert any(v['m_PathID']==path and v['m_FileID']==resources_id for k,v in final_rm['m_Container'])
 with zipfile.ZipFile(v3)as z:native=z.read(LIB);dex=z.read('classes13.dex')
 guards=guard_test(native,json.loads((SOURCE/'dealer_fix_details.json').read_text()));icons=check_icon_patch(native)
 assert b'ExpansionHub'not in dex and b'RuntimeLogCapture'in dex
 replacements={BUNDLE:bundle,DATA:databytes,LIB:native,'classes13.dex':dex}
 unsigned=work/'native-unsigned.tmp';stage=work/'native-signed.tmp'
 with zipfile.ZipFile(v4)as old,zipfile.ZipFile(unsigned,'w',allowZip64=False)as new:
  for item in old.infolist():
   if signature_entry(item.filename)or item.filename==BRIDGE:continue
   info=copy.copy(item);info.extra=b''
   if info.compress_type==zipfile.ZIP_STORED:
    align=16384 if info.filename.endswith('.so')else 4;position=new.fp.tell()+30+len(info.filename.encode())
    if position%align:
     pad=(-position-4)%align
     if pad<2:pad+=align
     info.extra=struct.pack('<HHH',0xd935,pad,align)+b'\0'*(pad-2)
   new.writestr(info,replacements.get(item.filename,old.read(item.filename)),compresslevel=6)
 with unsigned.open('r+b')as f:f.flush();os.fsync(f.fileno())
 assert zipfile.ZipFile(unsigned).testzip()is None
 jar=SOURCE/'tools/apksig-8.7.3.jar'
 run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,stage,SOURCE/'signing/music-test-key.pem',SOURCE/'signing/music-test-cert.der'])
 checks={p:run(['java','-cp',jar,SOURCE/p,stage])for p in ['VerifyApk.java','VerifyNativeSigner.java']}
 assert all('verified=true'in s for s in checks.values())
 assert all(s in checks['VerifyApk.java']for s in ['v2=true','v3=true','errors=[]','warnings=[]'])
 changes=[]
 with zipfile.ZipFile(v4)as old,zipfile.ZipFile(stage)as new,stage.open('rb')as f:
  assert new.testzip()is None and len(new.namelist())==len(set(new.namelist()))
  assert {x for x in old.namelist()if not signature_entry(x)}-{BRIDGE}=={x for x in new.namelist()if not signature_entry(x)}
  for item in new.infolist():
   if signature_entry(item.filename):continue
   if item.filename in replacements:assert new.read(item.filename)==replacements[item.filename];changes.append(item.filename)
   else:assert new.read(item.filename)==old.read(item.filename)
   if item.compress_type==zipfile.ZIP_STORED:
    f.seek(item.header_offset+26);nm,ex=struct.unpack('<HH',f.read(4));assert(item.header_offset+30+nm+ex)%(16384 if item.filename.endswith('.so')else 4)==0
 badging=run([tools/'aapt2','dump','badging',stage]);assert"name='com.candywriter.bitlife'"in badging and"versionCode='1062'"in badging
 assert stage.stat().st_size>260000000
 final=work/'BitLife_Native_Music_Studio_v5.apk';stage.replace(final);unsigned.unlink()
 backup=work/'BitLife_Native_Music_Studio_v5.zip'
 with zipfile.ZipFile(backup,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:z.write(final,final.name)
 with zipfile.ZipFile(backup)as z:assert sha(z.read(final.name))==sha_file(final)
 result={'apk':str(final),'size':final.stat().st_size,'sha256':sha_file(final),'backup':str(backup),'changed_entries':changes,'removed_entries':[BRIDGE],'new_resource_paths':added,'preserved_resource_paths':len(original_container),'preserved_datapack_objects':len(before)-1,'preserved_data_objects':len(before_data)-1,'dealer_tests':guards,'prison_icon_tests':icons,'signing':checks,'device_runtime_tested':False}
 (ROOT/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':build(*sys.argv[1:])
