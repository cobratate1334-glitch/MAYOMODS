"""Register nine integrated styles for every existing face stage and gender."""
import json,re,io,copy,struct,hashlib
from pathlib import Path
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parent
NAMES=['Rounded afro','Curly high top','Curly taper','Short coils','Double afro puffs','High curly bun','Cornrows','Box braids','Short twists','Long twists','Braided crown','Low ponytail','High ponytail','Long straight fringe','Wavy bob','Layered waves','Buzz fade','Side-part fade','Two-tone curls','Space buns']
def append(assets):
 base=json.loads(Path('analysis/base_assets.json').read_text())['a16_voltron_componentFilenames'];lines=base.splitlines()
 definitions=[]
 for i,label in enumerate(NAMES):
  for gender in range(2):
   for stage in range(6):
    n=f'a16_faces-{["male","female"][gender]}-stage{stage}-hair-base{58+i}-{98900+i*100+gender*10+stage}'
    lines.append(n+'.png');definitions.append(dict(name=n,stage=stage,gender=gender,style=i,label=label,path=f'emoji/voltron/faces/hair/stage {stage} {["male","female"][gender]}/'+n))
 assert len(lines)==len(set(lines));assets['a16_voltron_componentFilenames']='\r\n'.join(lines)
 (ROOT/'hair_catalog.json').write_text(json.dumps(definitions,indent=2));return definitions

def graphics(env,file,tree,resources_id,next_id):
 catalog=json.loads((ROOT/'hair_catalog.json').read_text())+json.loads((ROOT/'genetic_catalog.json').read_text());changed=set();results={}
 tex=next(o for o in env.objects if o.type.name=='Texture2D'and o.read().m_Name=='a16_faces-male-stage2-hair-base1-00792')
 spr=next(o for o in env.objects if o.type.name=='Sprite'and o.read().m_Name=='a16_faces-male-stage2-hair-base1-00792')
 rendered={}
 for i in range(len(NAMES)):
  raw=Image.open(ROOT/'assets'/f'hair{i+1}.png').convert('RGBA')
  # Same 500px canvas and crown position as the stock Voltron hair layer.
  fit=ImageOps.contain(raw,(475,445),Image.Resampling.LANCZOS);im=Image.new('RGBA',(500,500));im.paste(fit,((500-fit.width)//2,2));rendered[i]=im;im.save(ROOT/'assets'/f'hair{i+1}_layer.png')
 for item in catalog:
  n=item['name'];im=Image.open(ROOT/'assets'/item['source']).convert('RGBA') if 'source' in item else rendered[item['style']]
  to=copy.copy(tex);to.path_id=next_id;next_id+=1;to.data=tex.get_raw_data();file.objects[to.path_id]=to
  tx=to.read();tx.m_Name=n;tx.set_image(im,target_format=4);tx.save();changed.add(to.path_id)
  so=copy.copy(spr);so.path_id=next_id;next_id+=1;so.data=spr.get_raw_data();file.objects[so.path_id]=so
  st=so.read_typetree();st['m_Name']=n;digest=hashlib.sha256(n.encode()).digest();st['m_RenderDataKey']=({f'data[{i}]':struct.unpack_from('<I',digest,i*4)[0]for i in range(4)},21300000)
  st['m_Rect']=dict(x=0.,y=0.,width=500.,height=500.);st['m_Offset']=dict(x=0.,y=0.);st['m_Pivot']=dict(x=.5,y=.5);st['m_PixelsToUnits']=100.;st['m_IsPolygon']=False;st['m_AtlasTags']=[];st['m_SpriteAtlas']=dict(m_FileID=0,m_PathID=0);st['m_PhysicsShape']=[]
  rd=st['m_RD'];rd['texture']=dict(m_FileID=0,m_PathID=to.path_id);rd['alphaTexture']=dict(m_FileID=0,m_PathID=0);rd['secondaryTextures']=[];rd['textureRect']=dict(x=0.,y=0.,width=500.,height=500.);rd['textureRectOffset']=dict(x=0.,y=0.);rd['atlasRectOffset']=dict(x=0.,y=0.);rd['settingsRaw']=64;rd['uvTransform']=dict(x=100.,y=250.,z=100.,w=250.);rd['downscaleMultiplier']=1.
  rd['m_IndexBuffer']=struct.pack('<6H',0,1,2,0,2,3);rd['m_SubMeshes']=[dict(firstByte=0,indexCount=6,topology=0,baseVertex=0,firstVertex=0,vertexCount=4,localAABB=dict(m_Center=dict(x=0.,y=0.,z=0.),m_Extent=dict(x=2.5,y=2.5,z=0.)))]
  vd=rd['m_VertexData'];vd['m_VertexCount']=4
  for c in vd['m_Channels']:c.update(stream=0,offset=0,format=0,dimension=0)
  vd['m_Channels'][0].update(stream=0,offset=0,format=0,dimension=3);vd['m_Channels'][4].update(stream=1,offset=0,format=0,dimension=2)
  vd['m_DataSize']=struct.pack('<20f',-2.5,-2.5,0,-2.5,2.5,0,2.5,2.5,0,2.5,-2.5,0,0,0,0,1,1,1,1,0)
  so.save_typetree(st);changed.add(so.path_id)
  for obj in [to,so]:tree['m_Container'].append((item['path'],dict(m_FileID=resources_id,m_PathID=obj.path_id)))
  results[n]=dict(texture=to.path_id,sprite=so.path_id,source=item.get('source',f'hair{item["style"]+1}.png'),pixel_sha256=hashlib.sha256(im.tobytes()).hexdigest())
 return results,changed,next_id
if __name__=='__main__':
 p=ROOT/'assets.json';assets=json.loads(p.read_text());catalog=append(assets);p.write_text(json.dumps(assets,indent=2,ensure_ascii=True));print('Prepared',len(catalog),'registered hair layers')
