"""Extend the stock Voltron layer catalogue with deterministic trait textures."""
import copy,hashlib,json,re,struct,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageChops
import UnityPy
ROOT=Path(__file__).resolve().parent
def author(baseapk):
 base=json.loads(Path('analysis/base_assets.json').read_text());names=base['a16_voltron_componentFilenames'].splitlines()
 with zipfile.ZipFile(baseapk)as z:env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'))
 textures={o.read().m_Name:o for o in env.objects if o.type.name=='Texture2D'}
 def stock(g,s,feature):
  prefix=f'a16_faces-{g}-stage{s}-{feature}-';filename=next(n for n in names if n.startswith(prefix));return textures[filename[:-4]].read().image.convert('RGBA')
 out=ROOT/'assets';out.mkdir(exist_ok=True);catalog=[]
 for gender,g in enumerate(['male','female']):
  for stage in range(6):
   face=stock(g,stage,'base');mask=face.getchannel('A');bbox=mask.getbbox();left,top,right,bottom=bbox;w=right-left;h=bottom-top
   iris=stock(g,stage,'iris-base');eyebox=iris.getchannel('A').getbbox();ex0,ey0,ex1,ey1=eyebox;ey=(ey0+ey1)/2
   for mood,m in enumerate(['happy','sad','angry']):
    lighting=stock(g,stage,'lighting-'+('happy'if mood==0 else m if stage==0 else'angry-sad'))
    for trait in [1,2,3,6]:
     overlay=Image.new('RGBA',(500,500));d=ImageDraw.Draw(overlay)
     if trait==1:
      for x,y,r in [(.22,0,2.8),(.29,.012,2.1),(.34,.04,2.5),(.26,.06,1.9),(.69,.02,2.7),(.74,.065,2.2),(.79,.035,2.4),(.48,.035,1.8),(.52,.06,2.2)]:
       cx=left+x*w;cy=ey+y*h+.065*h;r*=w/350;d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(119,67,43,180))
     elif trait==2:
      cx=left+.76*w;cy=ey+.105*h;r=.04*w;d.ellipse((cx-r,cy-r*.72,cx+r,cy+r*.72),fill=(124,62,62,170))
     elif trait==3:
      # Irregular patches on both cheeks and the chin; retain the underlying
      # skin and all native facial features. Their position follows each age.
      for cx,cy,rx,ry in [(left+.19*w,ey+.11*h,.09*w,.075*h),(left+.78*w,ey+.17*h,.095*w,.10*h),(left+.40*w,top+.90*h,.10*w,.055*h)]:
       pts=[(cx-rx,cy-ry*.35),(cx-rx*.65,cy-ry),(cx+rx*.10,cy-ry*.8),(cx+rx*.45,cy-ry),(cx+rx,cy-ry*.15),(cx+rx*.7,cy+ry*.4),(cx+rx*.85,cy+ry*.85),(cx,cy+ry),(cx-rx*.65,cy+ry*.55)]
       d.polygon(pts,fill=(255,238,218,242))
      overlay=overlay.filter(ImageFilter.GaussianBlur(1.6))
     elif trait==6:
      for x in [.23,.77]:
       cx=left+x*w;cy=ey+.20*h;r=.019*w;d.arc((cx-r,cy-r,cx+r,cy+r),75,270,fill=(139,84,57,140),width=max(1,int(w/150)))
     overlay.putalpha(ImageChops.multiply(overlay.getchannel('A'),mask));im=Image.alpha_composite(lighting,overlay)
     ident=90000+trait*1000+gender*100+stage*10+mood
     name=f'a16_faces-{g}-stage{stage}-lighting-{m}42-{ident:05d}';source=name+'.png';im.save(out/source)
     catalog.append(dict(name=name,source=source,id=f'{ident:05d}',trait=trait,stage=stage,gender=gender,mood=mood,feature=4,path=f'emoji/voltron/faces/face/stage {stage} {g}/'+name))
   # The exact stock iris alpha determines both eye positions and pupils.
   im=iris.copy();pixels=im.load()
   for y in range(im.height):
    for x in range(im.width):
     r,gc,bl,a=pixels[x,y]
     if a:
      color=(60,156,216)if x<250 else(202,143,57);shade=max(r,gc,bl)/255
      pixels[x,y]=tuple(round(c*shade)for c in color)+(a,)
   ident=95000+gender*100+stage*10
   name=f'a16_faces-{g}-stage{stage}-iris-base42-{ident:05d}';source=name+'.png';im.save(out/source)
   catalog.append(dict(name=name,source=source,id=f'{ident:05d}',trait=5,stage=stage,gender=gender,mood=-1,feature=1,path=f'emoji/voltron/faces/face/stage {stage} {g}/'+name))
 assert len(catalog)==156 and len({x['name']for x in catalog})==156
 (ROOT/'portrait42_catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
 return {**{'a16_voltron_componentFilenames':'\r\n'.join(names+[x['name']+'.png'for x in catalog])}}

def graphics(env,file,tree,resource_id,next_id):
 # Reuse the established texture/sprite writer, with every original object
 # left byte-for-byte intact. Newly allocated IDs and paths are unique.
 from native_v19 import hair_assets
 source=Path(hair_assets.__file__).read_text();start=source.index('  to=copy.copy(tex)');end=source.index(' return results,changed,next_id',start)
 # This shared encoder writes only new Texture2D/Sprite objects. Bind the
 # source directory and catalog here rather than old retired portrait IDs.
 encoder=source[start:end]
 encoder=encoder.replace("item.get('source',f'hair{item[\"style\"]+1}.png')","item['source']")
 scope={'copy':copy,'struct':struct,'hashlib':hashlib,'Image':Image}
 fn="def encode(env,file,tree,resources_id,next_id,catalog,root):\n tex=next(o for o in env.objects if o.type.name=='Texture2D'and o.read().m_Name=='a16_faces-male-stage2-hair-base1-00792')\n spr=next(o for o in env.objects if o.type.name=='Sprite'and o.read().m_Name=='a16_faces-male-stage2-hair-base1-00792')\n changed=set();results={}\n for item in catalog:\n  n=item['name'];im=Image.open(root/'assets'/item['source']).convert('RGBA')\n"+encoder+" return results,changed,next_id\n"
 exec(compile(fn,'portrait42_sprite_encoder','exec'),scope)
 return scope['encode'](env,file,tree,resource_id,next_id,json.loads((ROOT/'portrait42_catalog.json').read_text()),ROOT)
if __name__=='__main__':author(__import__('sys').argv[1]);print('Authored 156 native portrait layers',flush=True)
