"""Check real serialized Sprite/Texture identities and photo pixels in the APK."""
import csv,hashlib,io,json,sys,zipfile
from pathlib import Path
import UnityPy
from playable_repair.asset_contracts import verify_resources
from playable_repair.artwork import artwork as school_art
from connected_life.artwork import artwork as old_art

def validate(apk,work,out):
 work=Path(work);r=json.loads((work/'bundle_validation.json').read_text());expected=[]
 for resource,im,meta in list(school_art())+list(old_art()):
  if resource.startswith(('native1111/school/','native1110/era/','native1110/photos/')):expected.append(dict(resource=resource,canvas=list(im.size),pixel_sha256=hashlib.sha256(im.tobytes()).hexdigest()))
 assert len(expected)==72
 with zipfile.ZipFile(apk)as z:
  pack=z.read('assets/bin/Data/datapack.unity3d');data=z.read('assets/bin/Data/data.unity3d');old=verify_resources(pack,data,expected);new=verify_resources(pack,data,r['imported_artwork']);assert new['resources']==8
  env=UnityPy.load(data);paths={p for p,v in next(o for o in env.objects if o.type.name=='ResourceManager').read_typetree()['m_Container']}
  assert all('native1111/news1112/'+row['id']in paths for row in json.loads(Path('work/source/device_repair/references/photos.json').read_text()))
  assert z.read('classes13.dex')==zipfile.ZipFile('/workspace/build_work/playable-repair/signed/MayoMods_1111_Playable_Repair.apk').read('classes13.dex')
 result=dict(passed=True,apk_sha256=hashlib.sha256(Path(apk).read_bytes()).hexdigest(),retained_resources=old['resources'],new_real_photos=new['resources'],serialized_file_identity_type_and_pixels=True,dex_preserved=True,phone_GPU_rendering_tested=False)
 Path(out).write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':validate(*sys.argv[1:])
