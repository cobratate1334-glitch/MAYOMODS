"""Pinned 1115 -> 1116 repair candidate; keep every unrelated APK entry/object."""
import copy,hashlib,json,struct,sys,zipfile
from pathlib import Path
import UnityPy
from v2_repair.content import build
from native_v27.manifest_version import bump_version
from native_v55.build_v55 import signature_entry,symbols
BASE='5f760cc31653060139f97614f90fb1f8222a2a6b3df94da6c373155ab5d1b20b'
sha=lambda b:hashlib.sha256(b).hexdigest()
def stage(base,work):
 base,work=Path(base),Path(work);assert sha(base.read_bytes())==BASE
 native=(work/'libil2cpp.so').read_bytes();manifest=json.loads((work/'native.json').read_text());assert sha(native)==manifest['binary_sha256']
 dex=(work/'dex2/classes13.dex').read_bytes();d=json.loads((work/'dex2/dex_validation.json').read_text());assert d['passed'] and sha(dex)==d['binary_sha256'] and d['changed_families']==['LauncherIcon','StartupActivity']
 with zipfile.ZipFile(base) as z:
  env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'));key=lambda o:(o.assets_file.name,o.path_id)
  before={key(o):o.get_raw_data() for o in env.objects};texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'}
  assets={k:o.read().m_Script for k,o in texts.items()};overlay=build(assets);changed=set()
  for name,value in overlay.items():
   obj=texts[name];data=obj.read();data.m_Script=value;data.save();changed.add(key(obj))
  pack=next(iter(env.files.values())).save(packer='original');after={key(o):o for o in UnityPy.load(pack).objects}
  assert before.keys()==after.keys()
  assert all(after[k].get_raw_data()==v for k,v in before.items() if k not in changed)
  for name,value in overlay.items():assert after[key(texts[name])].read().m_Script==value
  android,_=bump_version(z.read('AndroidManifest.xml'),old=1115,new=1116)
  syms=symbols(native,manifest);syms.update(build='1116',version_code=1116)
  changes={'AndroidManifest.xml':android,'classes13.dex':dex,'lib/arm64-v8a/libil2cpp.so':native,'assets/bin/Data/datapack.unity3d':pack,'assets/mayomods54/native_symbols.json':json.dumps(syms,indent=2).encode()}
  target=work/'MayoMods_1116_UNSIGNED_WORK.apk';assert not target.exists()
  with zipfile.ZipFile(target,'x',allowZip64=False) as out:
   for entry in z.infolist():
    if signature_entry(entry.filename):continue
    info=copy.copy(entry);info.extra=b''
    if info.compress_type==zipfile.ZIP_STORED:
     align=16384 if info.filename.endswith('.so') else 4;pos=out.fp.tell()+30+len(info.filename.encode())
     if pos%align:
      pad=(-pos-4)%align
      if pad<2:pad+=align
      info.extra=struct.pack('<HHH',0xd935,pad,align)+b'\0'*(pad-2)
    out.writestr(info,changes[info.filename] if info.filename in changes else z.read(info.filename))
  with zipfile.ZipFile(target) as out:
   assert out.testzip() is None and len(out.namelist())==len(set(out.namelist()))
   assert set(out.namelist())=={n for n in z.namelist() if not signature_entry(n)}
   assert all(out.read(n)==v for n,v in changes.items())
   assert all(out.read(n)==z.read(n) for n in out.namelist() if n not in changes)
  report=dict(staged=True,signed=False,base_sha256=BASE,apk_sha256=sha(target.read_bytes()),native_sha256=sha(native),dex_sha256=sha(dex),modified_entries=sorted(changes),changed_text_assets=sorted(overlay),unchanged_unrelated_unity_objects=len(before)-len(changed),all_other_APK_entries_identical=True,all_artwork_and_resource_manager_identical=True,version_code=1116,phone_tested=False)
  (work/'staging_report.json').write_text(json.dumps(report,indent=2)+'\n');print(target)
if __name__=='__main__':stage(*sys.argv[1:])
