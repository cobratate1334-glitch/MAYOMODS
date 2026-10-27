"""Verify all retained school/era/news references and pixels in the staged APK."""
import hashlib,json,sys,zipfile
from pathlib import Path
from playable_repair.asset_contracts import verify_resources
from playable_repair.artwork import artwork as school_art
from connected_life.artwork import artwork as old_art
from device_repair.artwork import artwork as news_art

def validate(apk,work,out):
 work=Path(work);r=json.loads((work/'bundle_validation.json').read_text());expected=[]
 for resource,im,meta in list(school_art())+list(old_art()):
  if resource.startswith(('native1111/school/','native1110/era/','native1110/photos/')):expected.append(dict(resource=resource,canvas=list(im.size),pixel_sha256=hashlib.sha256(im.tobytes()).hexdigest()))
 for resource,im,meta in news_art():expected.append(dict(resource=resource,canvas=list(im.size),pixel_sha256=hashlib.sha256(im.tobytes()).hexdigest()))
 assert len(expected)==80 and not r['imported_artwork']
 with zipfile.ZipFile(apk)as z:
  checked=verify_resources(z.read('assets/bin/Data/datapack.unity3d'),z.read('assets/bin/Data/data.unity3d'),expected)
  assert hashlib.sha256(z.read('classes13.dex')).hexdigest()=='5a3ec377e8dc897f4c803041f710e03e116b4e62e162fa4623f6e34b8dafa7be'
 result=dict(passed=True,apk_sha256=hashlib.sha256(Path(apk).read_bytes()).hexdigest(),retained_resources=checked['resources'],new_artwork=0,serialized_file_identity_type_and_pixels=True,dex_preserved=True,phone_GPU_rendering_tested=False)
 Path(out).write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':validate(*sys.argv[1:])
