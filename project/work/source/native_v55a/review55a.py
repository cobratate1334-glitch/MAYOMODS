"""Off-device placement checks against v55's original native face layers."""
import json,sys
from pathlib import Path
import numpy as np
import UnityPy
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent
def review(base):
    env=UnityPy.load(str(Path(base)/'datapack.unity3d'))
    textures={o.read().m_Name:o for o in env.objects if o.type.name=='Texture2D'}
    def layer(prefix,tint=None):
        name=next(n for n in textures if n.startswith(prefix))
        im=textures[name].read().image.convert('RGBA')
        if tint:
            a=np.array(im);a[:,:,:3]=(a[:,:,:3].astype(np.uint16)*np.array(tint,dtype=np.uint16)//255).astype(np.uint8)
            im=Image.fromarray(a)
        return im
    face=Image.new('RGBA',(500,500))
    for prefix,tint in [('a16_faces-male-stage2-base-',(235,187,147)),
                        ('a16_faces-male-stage2-lighting-happy-',None),
                        ('a16_faces-male-stage2-eye-base-',None)]:
        face.alpha_composite(layer(prefix,tint))
    catalog=json.loads((ROOT.parent/'native_v55/portrait49_catalog.json').read_text())
    eye=next(r for r in catalog if r['kind']=='eyes'and r['left']==1 and r['right']==4 and r['stage']==2 and r['gender']==0)
    face.alpha_composite(textures[eye['name']].read().image.convert('RGBA'))
    face.alpha_composite(layer('a16_faces-male-stage2-iris-lighting-'))
    face.alpha_composite(layer('a16_faces-male-stage2-eyebrows-happy2-',(82,49,27)))
    sheet=Image.new('RGB',(810,670),'#f5efdf');d=ImageDraw.Draw(sheet)
    d.text((20,12),'v55 artwork placement checks - off-device, not an Android screenshot',fill='#543b2d')
    for n,(label,scar,patch)in enumerate([('Original',0,0),('Brow scar',49101,0),('Black eyepatch',0,49201),
                                       ('Red lens',0,49222),('Cheek scar + skull patch',49112,49208),('Removed',0,0)]):
        im=face.copy()
        for kind,ident in [('scar',scar),('patch',patch)]:
            if ident:im.alpha_composite(Image.open(ROOT/'review'/f'a49_{kind}_{ident}.png').convert('RGBA'))
        im=im.resize((260,260),Image.Resampling.LANCZOS)
        x=5+(n%3)*270;y=35+(n//3)*310
        sheet.paste(im,(x,y),im);d.text((x+12,y+266),label,fill='#543b2d')
    sheet.save(ROOT/'review/V55_Artwork_Check.png')
    print('Six v55 off-device placement checks rendered.',flush=True)

if __name__=='__main__':review(sys.argv[1])
