"""Verify assets in the actual staged APK, including retained real year photos."""
import hashlib,json,sys,zipfile,csv,io
from pathlib import Path
import UnityPy
from playable_repair.asset_contracts import verify_resources
from connected_life.artwork import artwork as retained_artwork


def validate(apk,work,out):
 work=Path(work);report=json.loads((work/'bundle_validation.json').read_text())
 with zipfile.ZipFile(apk)as z:
  pack=z.read('assets/bin/Data/datapack.unity3d');data=z.read('assets/bin/Data/data.unity3d')
  imported=report['imported_artwork'];assert len(imported)==48
  supplied=verify_resources(pack,data,imported)
  expected=[]
  for resource,image,meta in retained_artwork():
   if resource.startswith(('native1110/era/','native1110/photos/')):
    expected.append(dict(resource=resource,canvas=list(image.size),pixel_sha256=hashlib.sha256(image.tobytes()).hexdigest()))
  assert len(expected)==24
  retained=verify_resources(pack,data,expected)
  objects=UnityPy.load(pack);outer=UnityPy.load(data);paths={p for p,_ in next(o for o in outer.objects if o.type.name=='ResourceManager').read_typetree()['m_Container']}
  referenced=set()
  for o in objects.objects:
   if o.type.name!='TextAsset':continue
   decoded=o.read()
   if not decoded.m_Name.startswith('genesis_'):continue
   text=decoded.m_Script
   if text.startswith('ScenarioID,'):
    for row in csv.DictReader(io.StringIO(text)):
     for key in ['EmojiString','BigImageString']:
      if row.get(key,'').startswith('native1111/'):referenced.add(row[key])
   elif text.startswith('{'):
    document=json.loads(text)
    for tile in document.get('Items',document.get('ListItems',[])):
     if tile.get('Icon','').startswith('native1111/'):referenced.add(tile['Icon'])
  assert referenced<=paths,sorted(referenced-paths)
  assert len(referenced)==48,(len(referenced),sorted(paths-referenced)[:2])
 result=dict(passed=True,apk_sha256=hashlib.sha256(Path(apk).read_bytes()).hexdigest(),new_school_resources=supplied['resources'],retained_real_photo_resources=retained['resources'],school_resources_used=len(referenced),file_identity_and_type_checked=True,actual_serialized_pixels_checked=True,phone_GPU_rendering_tested=False)
 Path(out).write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':validate(*sys.argv[1:])
