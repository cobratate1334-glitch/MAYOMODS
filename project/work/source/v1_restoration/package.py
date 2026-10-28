"""Pinned 1116 -> 1117 content restoration. No native, DEX or art changes."""
import copy,hashlib,json,struct,sys,zipfile
from pathlib import Path
import UnityPy
from native_v27.manifest_version import bump_version
from native_v55.build_v55 import signature_entry
from v1_restoration.content import build

BASE='ed7c91880ce3c0260f60de26bc00caf2df81d516dc837c0063f3fb52cf2a919f'
NATIVE='b1e7e199ddfff3fc4de83e0c5da4dd888b661424cfac606453e17d32a663fac1'
DEX='1f6e55b2f1a40039b1ba3083753a18ad69f9e2d22067420719afe6222ee638dd'
sha=lambda b:hashlib.sha256(b).hexdigest()

def stage(base,work):
 base,work=Path(base),Path(work);work.mkdir(parents=True,exist_ok=True)
 assert sha(base.read_bytes())==BASE
 with zipfile.ZipFile(base) as z:
  assert sha(z.read('lib/arm64-v8a/libil2cpp.so'))==NATIVE
  assert sha(z.read('classes13.dex'))==DEX
  env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'))
  key=lambda o:(o.assets_file.name,o.path_id)
  before={key(o):o.get_raw_data()for o in env.objects}
  texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'}
  assets={k:o.read().m_Script for k,o in texts.items()};overlay=build(assets)
  assert set(overlay)=={'genesis_v9_v12_soccer','genesis_v18_stars18','genesis_activities_v12','genesis_activities_v18'}
  changed=set()
  for name,value in overlay.items():
   obj=texts[name];data=obj.read();data.m_Script=value;data.save();changed.add(key(obj))
  pack=next(iter(env.files.values())).save(packer='original')
  after={key(o):o for o in UnityPy.load(pack).objects}
  assert before.keys()==after.keys()
  assert all(after[k].get_raw_data()==v for k,v in before.items() if k not in changed)
  assert all(after[key(texts[n])].read().m_Script==t for n,t in overlay.items())
  android,_=bump_version(z.read('AndroidManifest.xml'),old=1116,new=1117)
  syms=json.loads(z.read('assets/mayomods54/native_symbols.json'))
  assert syms['native_sha256']==NATIVE
  syms.update(build='1117',version_code=1117)
  changes={'AndroidManifest.xml':android,'assets/bin/Data/datapack.unity3d':pack,'assets/mayomods54/native_symbols.json':json.dumps(syms,indent=2).encode()}
  target=work/'MayoMods_1117_UNSIGNED_WORK.apk';assert not target.exists()
  with zipfile.ZipFile(target,'x',allowZip64=False)as out:
   for entry in z.infolist():
    if signature_entry(entry.filename):continue
    info=copy.copy(entry);info.extra=b''
    if info.compress_type==zipfile.ZIP_STORED:
     align=16384 if info.filename.endswith('.so') else 4
     pos=out.fp.tell()+30+len(info.filename.encode())
     if pos%align:
      pad=(-pos-4)%align
      if pad<2:pad+=align
      info.extra=struct.pack('<HHH',0xd935,pad,align)+b'\0'*(pad-2)
    out.writestr(info,changes[entry.filename]if entry.filename in changes else z.read(entry.filename))
  with zipfile.ZipFile(target)as out:
   assert out.testzip()is None and len(out.namelist())==len(set(out.namelist()))
   assert set(out.namelist())=={n for n in z.namelist()if not signature_entry(n)}
   assert all(out.read(n)==changes.get(n,z.read(n))for n in out.namelist())
  report=dict(staged=True,signed=False,base_sha256=BASE,apk_sha256=sha(target.read_bytes()),native_sha256=NATIVE,dex_sha256=DEX,modified_entries=sorted(changes),changed_text_assets=sorted(overlay),text_asset_sha256={n:sha(t.encode())for n,t in overlay.items()},unchanged_unrelated_unity_objects=len(before)-len(changed),all_other_APK_entries_identical=True,all_artwork_and_resource_manager_identical=True,version_code=1117,phone_tested=False)
  (work/'staging_report.json').write_text(json.dumps(report,indent=2)+'\n')
  (work/'overlay.json').write_text(json.dumps(overlay))
  print(target)
if __name__=='__main__':stage(*sys.argv[1:])
