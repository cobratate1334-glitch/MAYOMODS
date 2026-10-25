"""Native Career/Police/Prison v7 upgrade of exact Record Label v6 APK."""
import copy,csv,hashlib,io,json,os,struct,subprocess,sys,zipfile
from collections import Counter
from pathlib import Path
import UnityPy

ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE));sys.path.insert(0,str(SOURCE/'tests'))
from build_prison_expansion import signature_entry,sha_file,decode,encode,records
from native_hooks import patch
from test_native_hooks import validate as native_test
from dealer_guard_test import validate as guard_test
from community_loader_test import check_icon_patch
from native_v10.registry_format import repair as repair_registry
BUNDLE='assets/bin/Data/datapack.unity3d';DATA='assets/bin/Data/data.unity3d';LIB='lib/arm64-v8a/libil2cpp.so'
V6_SHA='fe235ded807265f3364a8d18b46581a2bb241b24c4c4e1e59d53a48f7eac03d9'
def sha(b):return hashlib.sha256(b).hexdigest()
def run(args):return subprocess.run(list(map(str,args)),capture_output=True,text=True,check=True).stdout.strip()
def csv_string(rows):
 f=io.StringIO(newline='');csv.writer(f,lineterminator='\r\n').writerows(rows);return f.getvalue().rstrip('\r\n')
def object_key(o):return(o.assets_file.name,o.path_id)
def objects(e):return{object_key(o):sha(o.get_raw_data())for o in e.objects}
def build(base,work,tools):
 base=Path(base).resolve();work=Path(work).resolve();tools=Path(tools).resolve();work.mkdir(exist_ok=True,parents=True)
 assert sha_file(base)==V6_SHA,'requires exact v6 APK'
 assets=json.loads((ROOT/'assets.json').read_text());original=json.loads((SOURCE/'native_studio/assets.json').read_text()) | json.loads((SOURCE/'native_label/assets.json').read_text())
 with zipfile.ZipFile(base)as z:
  env=UnityPy.load(z.read(BUNDLE));data=UnityPy.load(z.read(DATA));native=z.read(LIB)
 before=objects(env);before_data=objects(data)
 texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'}
 for name,value in original.items():assert texts[name].read().m_Script==value,'unexpected v6 content '+name
 registry_text=texts['genesis_feature_containers'].read().m_Script
 registry=list(csv.reader(io.StringIO(registry_text)));newrows=json.loads((ROOT/'registry_rows.json').read_text())
 # This registry has comment headers and an original optional short row.
 # Preserve its existing bytes; append complete 16-column definitions.
 assert all(len(r)==16 for r in newrows)
 assert not {r[0]for r in registry if r and not r[0].startswith('#')} & {r[0]for r in newrows}
 assets['genesis_feature_containers']=registry_text.rstrip('\r\n')+'\n'+csv_string(newrows)
 assets['genesis_feature_containers'],_=repair_registry(assets['genesis_feature_containers'])
 careers=records(decode(texts['a16_careers-enc'].read().m_Script));header=careers[0];career_templates={r[0]:dict(zip(header,r))for r in careers[1:]}
 for name,template,start,cap,attribute in [('F1 Driver','Race Engineer','$90,000.00','$3,000,000.00','Discipline'),('Reality TV Host','Reality TV Producer','$50,000.00','$500,000.00','Artistic')]:
  assert name not in career_templates
  r=career_templates[template].copy();r.update({'Career':name,'Required Education':'High School','Required Major':'','Required Working Years':'0','Seniority Track':name,'Can Skip Positions':'0','Seniority Track Years':'10','Starting Salary':start,'Salary Cap':cap,'Success Defining Attribute':attribute,'Commonness Score':'1','Min Age':'18','Min Intelligence':'','Min Appearance':'','Min Health':'','Too Old Age':'85','Unavailable':''})
  if name=='F1 Driver':r.update({'Requires Driving License':'x','Has Drug Tests':'x','Requires Clear Criminal Record':'x'})
  careers.append([r[f]for f in header])
 assets['a16_careers-enc']=encode(csv_string(careers))
 assert records(decode(assets['a16_careers-enc']))==careers
 assert not decode(assets['a16_careers-enc']).endswith(('\r','\n'))
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
 tree['m_Container'].sort(key=lambda p:p[0]);rm.save_typetree(tree)
 bundle=next(iter(env.files.values())).save(packer='original');databytes=next(iter(data.files.values())).save(packer='original')
 re=UnityPy.load(bundle);rd=UnityPy.load(databytes)
 for o in re.objects:
  if object_key(o)in changed or o.path_id in added.values():assert o.read().m_Script==assets[o.read().m_Name]
  else:assert sha(o.get_raw_data())==before[object_key(o)]
 assert len(list(re.objects))==len(before)+len(added)
 for o in rd.objects:
  if object_key(o)!=object_key(rm):assert sha(o.get_raw_data())==before_data[object_key(o)]
 final_rm=next(o for o in rd.objects if o.type.name=='ResourceManager').read_typetree()
 assert final_rm['m_DependentAssets']==olddeps
 oldcounts=Counter(json.dumps(p,sort_keys=True)for p in oldpaths);newcounts=Counter(json.dumps(p,sort_keys=True)for p in final_rm['m_Container'])
 assert not(oldcounts-newcounts)and len(final_rm['m_Container'])==len(oldpaths)+len(added)
 for name,path in added.items():assert any(v['m_PathID']==path and v['m_FileID']==resources_id for k,v in final_rm['m_Container'])
 # Verify every icon against actual registered game assets.
 valid_icons={p.split('/')[-1].removeprefix('a16_emoji-')for p,v in oldpaths if p.startswith('emoji/normal/')}
 # 'hero' is EmojiHub's dynamic character portrait token, used by working v5.
 valid_icons.add('hero')
 for name,text in assets.items():
  if text.startswith('{'):
   for section in json.loads(text)['Sections']:
    for item in section.get('Items',[]):assert item['Icon']in valid_icons,'unregistered icon '+item['Icon']
 native,hook_details=patch(native);new_hooks=native_test(native,hook_details)
 guards=guard_test(native,json.loads((SOURCE/'dealer_fix_details.json').read_text()));icons=check_icon_patch(native)
 replacements={BUNDLE:bundle,DATA:databytes,LIB:native}
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
 badging=run([tools/'aapt2','dump','badging',stage]);assert "name='com.candywriter.bitlife'"in badging and"versionCode='1062'"in badging
 assert stage.stat().st_size>260000000
 final=work/'BitLife_Native_Careers_Police_Prison_v7.apk';stage.replace(final);unsigned.unlink()
 backup=work/'BitLife_Native_Careers_Police_Prison_v7.zip'
 with zipfile.ZipFile(backup,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:z.write(final,final.name)
 with zipfile.ZipFile(backup)as z:assert sha(z.read(final.name))==sha_file(final)
 result=dict(apk=str(final),size=final.stat().st_size,sha256=sha_file(final),backup=str(backup),base_sha256=V6_SHA,changed_apk_entries=list(replacements),changed_existing_resources=sorted(name for name in assets if name in texts),new_resource_paths=added,preserved_resource_registrations=len(oldpaths),preserved_datapack_objects=len(before)-len(changed),preserved_data_objects=len(before_data)-1,dealer_tests=guards,prison_icon_tests=icons,native_menu_and_stat_tests=new_hooks,signing=signing,device_runtime_tested=False)
 (ROOT/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':build(*sys.argv[1:])
