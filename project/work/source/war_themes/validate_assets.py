"""Match the actual APK's four restored panels to the exact original atlas."""
import hashlib,json,sys,zipfile
from pathlib import Path
from playable_repair.asset_contracts import verify_resources
from playable_repair.artwork import artwork as school_art
from connected_life.artwork import artwork as other_art
from device_repair.artwork import artwork as news_art
from war_themes.artwork import artwork

def validate(apk,work,out):
 w=Path(work);bundle=json.load(open(w/'bundle_validation.json'));restored=bundle['imported_artwork'];assert len(restored)==4 and bundle['changed_text_assets']==0 and bundle['replaced_generated_objects']==8
 expected=[]
 for resource,im,meta in list(school_art())+list(other_art()):
  if resource.startswith(('native1111/school/','native1110/era/','native1110/photos/')):expected.append(dict(resource=resource,canvas=list(im.size),pixel_sha256=hashlib.sha256(im.tobytes()).hexdigest()))
 for resource,im,meta in news_art():expected.append(dict(resource=resource,canvas=list(im.size),pixel_sha256=hashlib.sha256(im.tobytes()).hexdigest()))
 exact=[dict(resource=n,canvas=list(im.size),pixel_sha256=hashlib.sha256(im.tobytes()).hexdigest())for n,im,_ in artwork()]
 assert len(expected)==80
 # The later replacement photographs are not the requested illustrated panels.
 photos={n:hashlib.sha256(im.tobytes()).hexdigest()for n,im,_ in other_art()if n.startswith('native1109/background/')}
 assert all(photos[r['resource']]!=r['pixel_sha256']for r in exact)
 with zipfile.ZipFile(apk)as z:
  pack=z.read('assets/bin/Data/datapack.unity3d');data=z.read('assets/bin/Data/data.unity3d');verify_resources(pack,data,expected);verify_resources(pack,data,exact)
 r=dict(passed=True,apk_sha256=hashlib.sha256(Path(apk).read_bytes()).hexdigest(),retained_resources=80,restored_original_atlas_panels=4,restored_pixels_match_original_atlas=True,later_photo_negative_control=True,Sprite_file_identity_and_types_checked=True,gameplay_TextAssets_changed=0,phone_GPU_rendering_tested=False)
 Path(out).write_text(json.dumps(r,indent=2)+'\n');print(r)
if __name__=='__main__':validate(*sys.argv[1:])
