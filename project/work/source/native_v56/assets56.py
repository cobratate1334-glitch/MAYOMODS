"""Reimport the supplied scar/eyepatch sheet without replacing native faces."""
import hashlib, json, sys
from collections import deque
from pathlib import Path
import UnityPy
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageFilter

ROOT=Path(__file__).resolve().parent; SOURCE=ROOT.parent
sys.path[:0]=[str(SOURCE),str(SOURCE/'native_v29')]
sha=lambda b:hashlib.sha256(b).hexdigest()

# Bounds measured from the 12 + 10 connected sprites in the supplied sheet.
# The second row is not a uniform grid; the old 155px cuts clipped later pads.
PATCH_RECTS=[
 (18,686,139,756),(156,686,269,755),(290,688,408,756),(430,688,545,753),
 (564,683,694,756),(712,681,836,757),(856,683,990,756),(1010,684,1137,758),
 (1156,683,1289,761),(1315,675,1450,758),(1475,689,1610,756),(1632,696,1752,760),
 (18,775,146,852),(163,777,286,851),(306,778,423,851),(440,775,602,853),
 (623,777,767,853),(792,778,933,852),(957,773,1086,849),(1117,784,1256,855),
 (1283,780,1424,867),(1443,773,1619,858)]
SCAR_BOXES=[
 (145,188,185,239),(122,305,175,365),(122,305,183,367),(115,295,166,390),
 (142,185,194,237),(131,198,195,233),(121,313,164,358),(123,301,169,375),
 (332,313,379,364),(300,134,351,219),(234,400,270,438),(131,309,175,365)]


def isolate(raw):
 """Keep the connected sprite and its antialiased border from a sheet cell."""
 w,h=raw.size;alpha=raw.getchannel('A');pixels=alpha.load();seen=set();groups=[]
 for y in range(h):
  for x in range(w):
   if (x,y) in seen or pixels[x,y]<128:continue
   queue=deque([(x,y)]);seen.add((x,y));points=[]
   while queue:
    px,py=queue.popleft();points.append((px,py))
    for nx,ny in [(px-1,py),(px+1,py),(px,py-1),(px,py+1)]:
     if 0<=nx<w and 0<=ny<h and (nx,ny) not in seen and pixels[nx,ny]>=128:
      seen.add((nx,ny));queue.append((nx,ny))
   groups.append(points)
 if not groups:return raw
 main=max(groups,key=len);left=min(x for x,y in main);right=max(x for x,y in main)
 top=min(y for x,y in main);bottom=max(y for x,y in main)
 mask=Image.new('L',raw.size);draw=ImageDraw.Draw(mask)
 for points in groups:
  cx=sum(x for x,y in points)/len(points);cy=sum(y for x,y in points)/len(points)
  if points is main or left<=cx<=right and top<=cy<=bottom:
   for p in points:draw.point(p,fill=255)
 result=raw.copy();result.putalpha(ImageChops.multiply(alpha,mask.filter(ImageFilter.MaxFilter(3))))
 return result


def scar(sheet,index):
 rect=(max(0,(index-1)*140),10,min(1774,(index-1)*140+138),150) if index<=8 else [(10,440,125,572),(610,438,694,572),(0,570,120,674),(475,438,582,574)][index-9]
 piece=isolate(sheet.crop(rect)); piece=piece.crop(piece.getbbox())
 box=SCAR_BOXES[index-1]
 piece.thumbnail((box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS)
 result=Image.new('RGBA',(500,500));result.alpha_composite(piece,((box[0]+box[2]-piece.width)//2,(box[1]+box[3]-piece.height)//2))
 return result,dict(source_rect=rect,target_box=box,preserve_aspect_ratio=True)


def eyepatch(sheet,index,eye):
 x0,y0,x1,y1=PATCH_RECTS[index-1]
 rect=(max(0,x0-2),max(0,y0-2),min(1774,x1+2),min(887,y1+2))
 piece=isolate(sheet.crop(rect));piece=piece.crop(piece.getbbox())
 alpha=np.asarray(piece)[:,:,3];heights=(alpha>=128).sum(axis=0)
 core=np.flatnonzero(heights>=max(1,heights.max()*.65));assert len(core)
 ys,xs=np.where((alpha>=128)&np.isin(np.arange(alpha.shape[1])[None,:],core))
 cx=(xs.min()+xs.max())/2;cy=(ys.min()+ys.max())/2
 # Scale the pad to one eye, preserving the artwork's shape and straps.
 scale=eye['height']*1.65/max(1,ys.max()-ys.min()+1)
 size=(max(1,round(piece.width*scale)),max(1,round(piece.height*scale)))
 resized=piece.resize(size,Image.Resampling.LANCZOS)
 position=(round(eye['x']-cx*scale),round(eye['y']-cy*scale))
 result=Image.new('RGBA',(500,500));result.alpha_composite(resized,position)
 return result,dict(source_rect=rect,pad_centre=[float(cx),float(cy)],target_eye=eye,scale=scale,position=position,preserve_aspect_ratio=True)


def build(base_directory,sheet_path):
 env=UnityPy.load(str(Path(base_directory)/'datapack.unity3d'))
 textures={o.read().m_Name:o for o in env.objects if o.type.name=='Texture2D'}
 catalog=json.loads((SOURCE/'native_v55/portrait49_catalog.json').read_text())
 eye_row=next(r for r in catalog if r['kind']=='eyes'and r['left']==r['right']==1 and r['stage']==2 and r['gender']==0)
 iris=np.asarray(textures[eye_row['name']].read().image.convert('RGBA'))[:,:,3]
 yy,xx=np.where((iris>=128)&(np.arange(500)[None,:]>=250));assert len(xx)
 eye=dict(x=float((xx.min()+xx.max())/2),y=float((yy.min()+yy.max())/2),height=int(yy.max()-yy.min()+1))
 sheet_path=Path(sheet_path);sheet=Image.open(sheet_path).convert('RGBA');assert sheet.size==(1774,887)
 changed=[];original={o.path_id:(o.type.name,o.get_raw_data()) for o in env.objects}
 previews=ROOT/'review';previews.mkdir(exist_ok=True)
 for kind,count,base,fn in [('scar',12,49100,scar),('patch',22,49200,lambda s,i:eyepatch(s,i,eye))]:
  for index in range(1,count+1):
   ident=base+index;name=f'a49_{kind}_{ident}';obj=textures[name]
   image,geometry=fn(sheet,index);assert image.getbbox()
   value=obj.read();value.set_image(image,target_format=4);value.m_IsReadable=True;value.save()
   image.save(previews/(name+'.png'))
   changed.append(dict(name=name,texture=obj.path_id,id=ident,kind=kind,size=[500,500],rgba_sha256=sha(image.tobytes()),geometry=geometry))
 output=ROOT/'bundles';output.mkdir(exist_ok=True)
 raw=next(iter(env.files.values())).save(packer='original');(output/'datapack.unity3d').write_bytes(raw)
 after=UnityPy.load(raw);wanted={r['texture']:r for r in changed};checks=0
 for obj in after.objects:
  if obj.path_id in wanted:
   record=wanted[obj.path_id];tx=obj.read();assert tx.m_IsReadable and tx.m_TextureFormat==4
   assert sha(tx.image.convert('RGBA').tobytes())==record['rgba_sha256']
  else:assert original[obj.path_id]==(obj.type.name,obj.get_raw_data())
  checks+=1
 assert len(original)==checks
 report=dict(passed=True,checks=checks,changed_textures=changed,source_sheet_sha256=sha(sheet_path.read_bytes()),
  datapack_sha256=sha(raw),all_other_unity_objects_unchanged=True,resource_manager_unchanged=True,original_native_faces_preserved=True,
  physical_phone_tested=False,Unity_rendering_tested=False)
 (ROOT/'assets56_validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print({'passed':True,'changed_textures':len(changed),'checks':checks,'target_eye':eye},flush=True)


if __name__=='__main__':build(*sys.argv[1:])
