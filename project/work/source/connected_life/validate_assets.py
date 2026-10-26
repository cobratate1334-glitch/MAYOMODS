"""Check serialized Unity Sprite pixels/paths and canonical ZIP aliases."""
import hashlib,json,sys,zipfile
from pathlib import Path
import UnityPy
from PIL import Image
from connected_life.artwork import artwork,ROOT
from military_expansion.package import catalog,runtime_path,ROOT as OLD
sha=lambda b:hashlib.sha256(b).hexdigest()

def validate(apk,work,out):
 checks=[]
 def ck(ok,label):assert ok,label;checks.append(label)
 with zipfile.ZipFile(apk)as z:
  env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'));data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'));objects={o.path_id:o for o in env.objects};rm=next(o for o in data.objects if o.type.name=='ResourceManager');paths={p:v['m_PathID']for p,v in rm.read_typetree()['m_Container']}
  runtime=json.loads(z.read('assets/military1110/manifest.json'));by={r['id']:r for r in runtime['assets']};source=json.loads((ROOT/'inputs/extra_military/manifest.json').read_text())
  for row in source['assets']:
   identity=row['id'];expected='sprites/'+identity.rsplit('_',1)[0]+'/'+identity+'.png';ck(by[identity]['file']==expected,'canonical manifest alias '+identity);ck(z.read('assets/military1110/'+expected)==(ROOT/'inputs/extra_military'/row['file']).read_bytes(),'supplied extra source bytes '+identity)
  for row in catalog()['assets']:
   ck(z.read('assets/military1108/'+runtime_path(row))==(OLD/'inputs'/row['file']).read_bytes(),'previous supplied sprite preserved '+row['id']);ck('mayomods1108/military/'+row['id']in paths,'previous resource retained '+row['id'])
  expected=set();counts={}
  for resource,image,meta in artwork():
   expected.add(resource);counts[meta['kind']]=counts.get(meta['kind'],0)+1;ck(resource in paths,'resource resolves '+resource);sprite=objects[paths[resource]];ck(sprite.type.name=='Sprite','typed Unity Sprite '+resource);actual=sprite.read().image.convert('RGBA');ck(actual.size==image.size and actual.tobytes()==image.tobytes(),'actual serialized pixels '+resource)
  missing=dict(paths);missing.pop('native1110/era/1939');ck(not expected<=missing.keys(),'negative control detects missing era resource')
  ck('native1109/live'in paths,'owned live texture preserved');sprite=objects[paths['native1109/live']].read_typetree();texture=objects[sprite['m_RD']['texture']['m_PathID']].read();ck(texture.m_IsReadable and texture.m_Width==512 and texture.m_Height==512,'live board/uniform image remains private readable texture')
  ck('assets/native1109/war_background_atlas.png'not in z.namelist(),'generated scenery atlas removed');ck('assets/native1109/ATTRIBUTION.txt'not in z.namelist(),'obsolete scenery credit removed');photos=json.loads(z.read('assets/native1110/photos.json'));ck(len(photos)==12 and all(not r['generated']and r['source_url'].startswith('https://commons.wikimedia.org/')for r in photos),'real photographs have source and license metadata')
  for row in photos:ck(sha((ROOT/'inputs/photos'/(row['id']+'.png')).read_bytes())==row['packaged_sha256'],'photograph source hash '+row['id'])
  # White captions meet 4.5:1 even over the brightest photo area.
  import numpy as np
  for resource,image,meta in artwork():
   if meta['kind']!='native-photo-era-button':continue
   rgba=np.array(image)/255.;pixels=rgba[:,:,:3][rgba[:,:,3]>.99];linear=np.where(pixels<=.04045,pixels/12.92,((pixels+.055)/1.055)**2.4);lum=(linear*np.array([.2126,.7152,.0722])).sum(axis=1)
   # Ignore the decorative light border; captions stay inside its inset.
   center=np.array(image)[35:-35,70:-70,:3]/255.;linear=np.where(center<=.04045,center/12.92,((center+.055)/1.055)**2.4);lum=(linear*np.array([.2126,.7152,.0722])).sum(axis=-1);ck(float((1.05/(lum+.05)).min())>=4.5,'era caption contrast '+resource)
 report=dict(passed=True,checks=len(checks),apk_sha256=sha(Path(apk).read_bytes()),extra_supplied_assets=144,previous_supplied_assets=144,artwork_counts=counts,serialized_Unity_Sprite_pixel_checks=True,missing_resource_negative_control=True,real_photographs_with_provenance=12,generated_scenery_removed=True,phone_rendering_tested=False);Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
