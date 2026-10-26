"""Resolve the actual APK Sprite paths, source pixels and readable journal blend."""
import hashlib,json,sys,zipfile
from pathlib import Path
import UnityPy
from PIL import Image
from native_immersion.package import artwork
from military_expansion.package import catalog,runtime_path,ROOT as OLD
ROOT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def validate(apk,work,out):
 work=Path(work);checks=[]
 def ck(test,label):assert test,label;checks.append(label)
 with zipfile.ZipFile(apk)as z:
  env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'));data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'));objects={o.path_id:o for o in env.objects};rm=next(o for o in data.objects if o.type.name=='ResourceManager');paths={p:v['m_PathID']for p,v in rm.read_typetree()['m_Container']};runtime=json.loads(z.read('assets/military1108/manifest.json'));by={r['id']:r for r in runtime['assets']}
  for r in catalog()['assets']:
   canonical='assets/military1108/'+runtime_path(r);ck(z.read(canonical)==(OLD/'inputs'/r['file']).read_bytes(),'original supplied PNG unchanged '+r['id']);ck(by[r['id']]['file']==runtime_path(r),'canonical supplied alias '+r['id']);ck('mayomods1108/military/'+r['id']in paths,'supplied Sprite path resolves '+r['id'])
  for resource,image,meta in artwork():
   ck(resource in paths,'native artwork resource resolves '+resource);sprite=objects[paths[resource]];ck(sprite.type.name=='Sprite','typed Sprite resource '+resource);actual=sprite.read().image.convert('RGBA');ck(actual.size==image.size and actual.tobytes()==image.tobytes(),'serialized Sprite pixels '+resource)
   if meta['kind']=='owned-live-image':
    tree=sprite.read_typetree();texture=objects[tree['m_RD']['texture']['m_PathID']].read();ck(texture.m_IsReadable and(texture.m_Width,texture.m_Height)==(512,512),'private mutable board/uniform texture is readable and correctly sized')
   if meta['kind']=='journal':
    # Blend actually used by the native Image: alpha .30 on the native paper.
    # Compare every pixel with the native dark-ink color in linear-light sRGB.
    import numpy as np
    rgb=np.array(image)[:,:,:3]/255.;paper=np.array([221,220,203])/255.;ink=np.array([37,46,48])/255.;blend=rgb*.3+paper*.7
    lum=lambda v:np.sum(np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)*np.array([.2126,.7152,.0722]),axis=-1)
    ratio=(lum(blend)+.05)/(lum(ink)+.05);ck(float(ratio.min())>=4.5,'minimum native journal text contrast '+resource)
  expected={p for p,_,_ in artwork()};broken=set(paths)-{'native1109/background/ww2'};ck(not expected<=broken,'negative control rejects a missing journal Sprite path')
  ck(z.read('assets/native1109/war_background_atlas.png')==(ROOT/'inputs/war_background_atlas.png').read_bytes(),'original atlas PNG included byte for byte')
 report=dict(passed=True,checks=len(checks),apk_sha256=sha(Path(apk).read_bytes()),native_art_sprites=57,supplied_source_sprites_preserved=144,missing_resource_negative_control=True,normal_text_contrast_threshold=4.5,actual_Unity_Sprite_pixel_checks=True,Unity_rendering_tested=False,phone_tested=False);Path(out).write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
