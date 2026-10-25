"""Extend native portrait resources, preserving stock sprites and save IDs."""
import copy, hashlib, json, math, sys, zipfile
from collections import Counter
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops, ImageFilter
import UnityPy
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT.parent),str(ROOT.parent/'native_v42')]
from traits43 import TRAITS
from native_v42 import portrait_assets42 as encoder
sha=lambda b:hashlib.sha256(b).hexdigest()

def polygon(draw,cx,cy,rx,ry,color,phase=0):
 points=[]
 for n in range(28):
  t=n*math.tau/28;scale=1+.12*math.sin(t*5+phase)+.07*math.cos(t*9-phase)
  points.append((cx+math.cos(t)*rx*scale,cy+math.sin(t)*ry*scale))
 draw.polygon(points,fill=color)

def face_marks(face,iris,trait):
 mask=face.getchannel('A');left,top,right,bottom=mask.getbbox();w=right-left;h=bottom-top
 _,ey0,_,ey1=iris.getchannel('A').getbbox();ey=(ey0+ey1)/2
 out=Image.new('RGBA',face.size);d=ImageDraw.Draw(out)
 if trait==3:
  # Large, irregular pale patches similar to the supplied reference. The
  # original skin is a separate native layer and stays visible beneath them.
  for x,y,rx,ry in [(.22,.14,.13,.075),(.60,.23,.085,.13),(.66,.54,.115,.075),(.22,.68,.15,.11),(.73,.81,.085,.08),(.39,.48,.055,.08)]:
   polygon(d,left+x*w,top+y*h,rx*w,ry*h,(255,238,217,245),x*8)
 elif trait==8:
  for n in range(55):
   x=.17+((n*37)%67)/100;y=.06+((n*17)%13)/100
   cx=left+x*w;cy=ey+y*h;r=(1.5+(n%4)*.6)*w/350
   d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(105,57,33,190))
 elif trait==9:
  polygon(d,left+.77*w,top+.56*h,.15*w,.20*h,(148,42,68,180),2)
 elif trait==10:
  polygon(d,left+.26*w,top+.29*h,.135*w,.10*h,(121,72,34,128),4)
 elif trait==11:
  polygon(d,left+.49*w,top+.18*h,.105*w,.18*h,(255,243,224,248),2)
  polygon(d,left+.17*w,top+.66*h,.07*w,.095*h,(255,243,224,248),3)
 elif trait==14:
  cx=left+.73*w;cy=ey+.16*h;r=.012*w
  d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(65,39,29,230))
 else:raise ValueError(trait)
 out=out.filter(ImageFilter.GaussianBlur(.65))
 out.putalpha(ImageChops.multiply(out.getchannel('A'),mask))
 return out

def coloured_iris(iris,trait):
 out=iris.copy();alpha=iris.getchannel('A');boxes=[]
 # Native iris alpha determines the exact positions at each age and gender.
 for start,end in [(0,250),(250,500)]:
  box=alpha.crop((start,0,end,500)).getbbox()
  boxes.append((start+box[0],box[1],start+box[2],box[3]))
 p=out.load()
 for side,(x0,y0,x1,y1) in enumerate(boxes):
  cx=(x0+x1)/2;cy=(y0+y1)/2;rx=(x1-x0)/2;ry=(y1-y0)/2
  for y in range(y0,y1):
   for x in range(x0,x1):
    r,g,b,a=p[x,y]
    if not a:continue
    nx=(x-cx)/rx;ny=(y-cy)/ry
    if trait==12:
     color=(203,139,52)if side==0 and -.8<math.atan2(ny,nx)<.8 else(68,148,187)
    else:color=(203,139,52)if nx*nx+ny*ny<.34 else(75,155,117)
    shade=max(r,g,b)/255
    p[x,y]=tuple(round(c*shade)for c in color)+(a,)
 return out

def build(base,out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);(ROOT/'assets').mkdir(exist_ok=True)
 with zipfile.ZipFile(base)as z:
  env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'))
  data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'))
 textures={o.read().m_Name:o for o in env.objects if o.type.name=='Texture2D'}
 texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'}
 old_catalog=json.loads((ROOT.parent/'native_v42/portrait42_catalog.json').read_text())
 names=texts['a16_voltron_componentFilenames'].read().m_Script.splitlines()
 def stock(g,s,f):
  prefix=f'a16_faces-{g}-stage{s}-{f}-'
  name=next(n[:-4]for n in names if n.startswith(prefix)and not n.split('-')[-1].startswith('9'))
  return textures[name].read().image.convert('RGBA')
 key=lambda o:(o.assets_file.name,o.path_id)
 before={key(o):sha(o.get_raw_data())for o in env.objects}
 before_data={key(o):sha(o.get_raw_data())for o in data.objects}
 updated=[];new=[]
 for gender,g in enumerate(['male','female']):
  for stage in range(6):
   face=stock(g,stage,'base');iris=stock(g,stage,'iris-base')
   for mood,m in enumerate(['happy','sad','angry']):
    light=stock(g,stage,'lighting-'+('happy'if mood==0 else m if stage==0 else'angry-sad'))
    for trait in [3,8,9,10,11,14]:
     im=Image.alpha_composite(light,face_marks(face,iris,trait))
     if trait==3:
      item=next(i for i in old_catalog if(i['trait'],i['gender'],i['stage'],i['mood'])==(trait,gender,stage,mood))
      tex=textures[item['name']].read();tex.image=im;tex.save();updated.append(key(textures[item['name']]))
     else:
      ident=87000+(trait-8)*200+gender*60+stage*3+mood
      name=f'a16_faces-{g}-stage{stage}-lighting-{m}43-{ident:05d}'
      item=dict(name=name,source=name+'.png',id=f'{ident:05d}',trait=trait,stage=stage,gender=gender,mood=mood,feature=4,path=f'emoji/voltron/faces/face/stage {stage} {g}/'+name)
      new.append(item)
     im.save(ROOT/'assets'/item['source'])
   for trait in [12,13]:
    ident=88500+(trait-12)*100+gender*40+stage
    name=f'a16_faces-{g}-stage{stage}-iris-base43-{ident:05d}'
    item=dict(name=name,source=name+'.png',id=f'{ident:05d}',trait=trait,stage=stage,gender=gender,mood=-1,feature=1,path=f'emoji/voltron/faces/face/stage {stage} {g}/'+name)
    coloured_iris(iris,trait).save(ROOT/'assets'/item['source']);new.append(item)
 assert len(new)==204 and len({i['id']for i in old_catalog+new})==360
 assert not({i['id']for i in new}&{n[-9:-4]for n in names}), 'new IDs must be globally unique, including custom hair'
 (ROOT/'portrait42_catalog.json').write_text(json.dumps(new,indent=2)+'\n')
 (ROOT/'portrait43_catalog.json').write_text(json.dumps(old_catalog+new,indent=2)+'\n')
 changes={'a16_voltron_componentFilenames':'\r\n'.join(names+[i['source']for i in new])}
 for name in ['genesis_v18_defaults_life_v18','genesis_v18_defaults_newlife24']:
  value=texts[name].read().m_Script
  assert 'RareAppearance21,int,0,,0,7' in value
  changes[name]=value.replace('RareAppearance21,int,0,,0,7','RareAppearance21,int,0,,0,14')
 changed_text=set()
 for name,value in changes.items():
  obj=texts[name].read();obj.m_Script=value;obj.save();changed_text.add(key(texts[name]))
 assets=json.loads((ROOT.parent/'native_v42/assets.json').read_text());assets.update(changes)
 (ROOT/'assets.json').write_text(json.dumps(assets,indent=2)+'\n')
 rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree();oldpaths=copy.deepcopy(tree['m_Container'])
 rid=next(n+1 for n,e in enumerate(rm.assets_file.externals)if e.path=='resources.assets')
 file=texts['a16_voltron_componentFilenames'].assets_file
 encoder.ROOT=ROOT
 registered,added,_=encoder.graphics(env,file,tree,rid,max(file.objects)+1)
 tree['m_Container'].sort(key=lambda x:x[0]);rm.save_typetree(tree)
 for name,e in [('datapack',env),('data',data)]:
  (out/(name+'.unity3d')).write_bytes(next(iter(e.files.values())).save(packer='original'))
 reread=UnityPy.load((out/'datapack.unity3d').read_bytes());rd=UnityPy.load((out/'data.unity3d').read_bytes())
 after={key(o):sha(o.get_raw_data())for o in reread.objects};after_data={key(o):sha(o.get_raw_data())for o in rd.objects}
 assert{k for k in before if before[k]!=after[k]}==set(updated)|changed_text
 assert{k for k in before_data if before_data[k]!=after_data[k]}=={key(rm)}
 paths=next(o for o in rd.objects if o.type.name=='ResourceManager').read_typetree()['m_Container']
 assert Counter((p,json.dumps(v,sort_keys=True))for p,v in oldpaths)<=Counter((p,json.dumps(v,sort_keys=True))for p,v in paths)
 rt={o.read().m_Name:o for o in reread.objects if o.type.name=='Texture2D'}
 for item in old_catalog+new:
  assert item['name']in rt
  if item in new:assert sha(rt[item['name']].read().image.convert('RGBA').tobytes())==registered[item['name']]['pixel_sha256']
 report=dict(passed=True,new_portrait_styles=204,total_portrait_styles=360,vitiligo_layers_revised=36,trait_choices=15,all_other_Unity_objects_preserved=True,existing_resource_paths_preserved=True,new_texture_pixel_roundtrips_verified=True,datapack_sha256=sha((out/'datapack.unity3d').read_bytes()),data_sha256=sha((out/'data.unity3d').read_bytes()),device_rendering_tested=False)
 (ROOT/'content43_validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report),flush=True)
if __name__=='__main__':build(*sys.argv[1:])
