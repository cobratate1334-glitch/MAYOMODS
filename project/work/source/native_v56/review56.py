"""Off-device visual checks using native face layers and emitted ARM64 output."""
import json,sys
from pathlib import Path
import numpy as np
import UnityPy
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from test_native56 import Machine
ROOT=Path(__file__).resolve().parent


def build(base_directory):
 env=UnityPy.load(str(Path(base_directory)/'datapack.unity3d'))
 textures={o.read().m_Name:o for o in env.objects if o.type.name=='Texture2D'}
 native=ROOT/'libil2cpp.so';machine=Machine(native.read_bytes(),0);machine.prepare49()
 def layer(prefix,colour=None):
  name=next(n for n in textures if n.startswith(prefix));im=textures[name].read().image.convert('RGBA')
  if colour:
   a=np.array(im);rgb=np.array(colour,dtype=np.uint16);a[:,:,:3]=(a[:,:,:3].astype(np.uint16)*rgb//255).astype(np.uint8);im=Image.fromarray(a)
  return im
 def pixels(im):return np.flipud(np.asarray(im)).copy().view('<u4').reshape(-1).tolist()
 def picture(values,size):return Image.fromarray(np.flipud(np.asarray(values,dtype='<u4').reshape(size,size).view(np.uint8).reshape(size,size,4)).copy())
 portrait=Image.new('RGBA',(500,500))
 for prefix,colour in [('a16_faces-male-stage2-base-',(235,187,147)),('a16_faces-male-stage2-lighting-happy-',None),('a16_faces-male-stage2-eye-base-',None)]:portrait.alpha_composite(layer(prefix,colour))
 catalog=json.loads((ROOT/'portrait49_catalog.json').read_text());eye=next(r for r in catalog if r['kind']=='eyes'and r['left']==1 and r['right']==4 and r['stage']==2 and r['gender']==0)
 portrait.alpha_composite(textures[eye['name']].read().image.convert('RGBA'))
 portrait.alpha_composite(layer('a16_faces-male-stage2-iris-lighting-',None));portrait.alpha_composite(layer('a16_faces-male-stage2-eyebrows-happy2-',(82,49,27)))
 sheet=Image.new('RGB',(800,670),'#f5efdf');draw=ImageDraw.Draw(sheet);draw.text((22,12),'Off-device artwork checks - not an Android screenshot',fill='#543b2d')
 checks=[]
 for index,(title,scar,patch)in enumerate([('Base',0,0),('Scar',49101,0),('Black patch',0,49201),('Red lens',0,49222),('Scar + patch',49112,49208),('Removed',0,0)]):
  machine.acc[(machine.face,8)]=scar;machine.acc[(machine.face,9)]=patch
  for ident in [scar,patch]:
   if not ident or ident in machine.sources56:continue
   kind='scar'if ident<49200 else'patch';im=Image.open(ROOT/'review'/f'a49_{kind}_{ident}.png').convert('RGBA');machine.sources56[ident]=machine.texture56(500,500,pixels(im))
  size=96;tex=machine.texture56(size,size,pixels(portrait.resize((size,size),Image.Resampling.LANCZOS)))
  machine.run56('v56_composite_saved_scar_and_eyepatch',{0:tex,1:machine.face})
  image=picture(machine.textures56[tex]['pixels'],size);image.save(ROOT/'review'/('portrait_'+str(index)+'.png'))
  x=(index%3)*266;y=40+(index//3)*310;sheet.paste(image.resize((266,266),Image.Resampling.NEAREST),(x,y),image.resize((266,266),Image.Resampling.NEAREST));draw.text((x+12,y+270),title,fill='#543b2d')
  checks.append(dict(title=title,scar=scar,patch=patch,width=size,height=size))
 sheet.save(ROOT/'review/Portrait_Artwork_Checks.png')
 (ROOT/'review56.json').write_text(json.dumps(dict(emitted_arm64=True,Android_screenshot=False,physical_device_tested=False,cases=checks),indent=2)+'\n')
 print('Six off-device portrait checks rendered through emitted ARM64.',flush=True)


if __name__=='__main__':
 try:build(sys.argv[1])
 except BaseException:
  __import__('traceback').print_exc();sys.stdout.flush();sys.stderr.flush();__import__('os')._exit(1)
 sys.stdout.flush();sys.stderr.flush();__import__('os')._exit(0)
