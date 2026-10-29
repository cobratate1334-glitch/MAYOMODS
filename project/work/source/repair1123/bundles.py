"""Stage-aware placement of the nine original imported hair layers; stable IDs."""
import hashlib,json
from pathlib import Path
import UnityPy
from PIL import Image
sha=lambda x:hashlib.sha256(x).hexdigest()
ROOT=Path(__file__).resolve().parents[1]
def head_anchor(im):
 a=im.convert('RGBA').getchannel('A');box=a.getbbox();assert im.size==(500,500)and box
 # Crown width excludes ears, jewellery and the lower chin. It also detects
 # the different baby/child/adult head silhouettes on the common canvas.
 left,top,right,bottom=box;y=round(top+(bottom-top)*.20);xs=[x for x in range(500)if a.getpixel((x,y))>=128];assert xs
 return (min(xs),top,max(xs)+1,bottom)
def place(im,reference,target):
 l,t,r,b=reference;L,T,R,B=target;xs=[0,l,r,500];ys=[0,t,b,500];X=[0,L,R,500];Y=[0,T,B,500];mesh=[]
 # Keep the canvas edges fixed as the crown moves. A whole-canvas affine
 # translation would clip the tall loc tips on an adult head. The nine-cell
 # mesh preserves those tips while moving the crown/side/length anchors.
 for y in range(3):
  for x in range(3):
   if X[x+1]<=X[x]or Y[y+1]<=Y[y]:continue
   mesh.append(((X[x],Y[y],X[x+1],Y[y+1]),(xs[x],ys[y],xs[x],ys[y+1],xs[x+1],ys[y+1],xs[x+1],ys[y])))
 return im.transform((500,500),Image.Transform.MESH,mesh,Image.Resampling.BICUBIC)
def bundle(z):
 original=z.read('assets/bin/Data/datapack.unity3d');env=UnityPy.load(original);key=lambda o:(o.assets_file.name,o.path_id)
 before={key(o):o.get_raw_data()for o in env.objects};sprites={o.read().m_Name:o for o in env.objects if o.type.name=='Sprite'};textures={o.read().m_Name:o for o in env.objects if o.type.name=='Texture2D'};objects={key(o):o for o in env.objects}
 catalog=json.loads((ROOT/'native_v15/hair_catalog.json').read_text());anchors={}
 for g,gender in enumerate(['male','female']):
  for stage in range(6):
   name=next(n for n in sprites if n.startswith(f'a16_faces-{gender}-stage{stage}-base-'))
   # Stock Sprite.image is tightly trimmed (e.g. 406x450). The original
   # Voltron layer coordinates are in its full 500x500 Texture2D canvas.
   anchors[g,stage]=head_anchor(textures[name].read().image)
 ref=anchors[0,2];changed=set();placements=[];sources={}
 for row in catalog:
  if row['style']not in sources:
   n=next(r['name']for r in catalog if r['style']==row['style']and r['stage']==2 and r['gender']==0);sources[row['style']]=sprites[n].read().image.convert('RGBA')
 for row in catalog:
  sp=sprites[row['name']];tree=sp.read_typetree();texture=objects[sp.assets_file.name,tree['m_RD']['texture']['m_PathID']];d=texture.read();im=place(sources[row['style']],ref,anchors[row['gender'],row['stage']]);d.set_image(im,target_format=4);d.save();changed.add(key(texture))
  placements.append(dict(name=row['name'],gender=row['gender'],stage=row['stage'],style=row['style'],texture_id=texture.path_id,sprite_id=sp.path_id,reference_crown=list(ref),destination_crown=list(anchors[row['gender'],row['stage']]),pixel_sha256=sha(im.tobytes())))
 pack=next(iter(env.files.values())).save(packer='original');out=UnityPy.load(pack);final={key(o):o for o in out.objects};assert before.keys()==final.keys()
 assert all(final[k].get_raw_data()==v for k,v in before.items()if k not in changed)
 for row in placements:
  sp=next(o for o in final.values()if o.type.name=='Sprite'and o.path_id==row['sprite_id']);assert sha(sp.read().image.convert('RGBA').tobytes())==row['pixel_sha256']
 # No resource aliases, sprites, filenames, TextAssets, original stock head
 # textures, DEX or scene objects change. Only these legacy texture canvases.
 rawdata=z.read('assets/bin/Data/data.unity3d')
 report=dict(passed=True,changed_text_assets=[],text_asset_sha256={},unchanged_unrelated_unity_objects=len(before)-len(changed),stock_portraits_and_other_artwork_identical=True,existing_resource_aliases_and_IDs_preserved=True,existing_Sprite_objects_identical=True,legacy_hair_textures=len(changed),hair_placements=placements,resource_validation=dict(resources=0),datapack_sha256=sha(pack),data_sha256=sha(rawdata),phone_rendering_tested=False)
 return pack,rawdata,report
