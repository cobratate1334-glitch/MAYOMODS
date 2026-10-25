"""Import tightly bounded illustrations from the original supplied church sheet."""
import copy,hashlib,json,struct,sys,zipfile
from pathlib import Path
from collections import Counter
from PIL import Image
import UnityPy
ROOT=Path(__file__).resolve().parent;sha=lambda raw:hashlib.sha256(raw).hexdigest()

def build(base):
 a=json.loads((ROOT/'assets.json').read_text())
 with zipfile.ZipFile(base)as z:env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'));data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'))
 original={o.path_id:(o.type.name,o.get_raw_data())for o in env.objects};texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'}
 textures={o.read().m_Name:o for o in env.objects if o.type.name=='Texture2D'};file=texts['genesis_feature_containers'].assets_file;nextid=max(file.objects)+1
 rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree();oldpaths=copy.deepcopy(tree['m_Container']);rid=next(n+1 for n,e in enumerate(rm.assets_file.externals)if e.path=='resources.assets')
 changed=[];added=[]
 for name,value in a.items():
  assert name in texts,name
  ob=texts[name];t=ob.read()
  if t.m_Script!=value:t.m_Script=value;t.save();changed.append(name)
 template=textures['49-basilica'];sprite=next(o for o in env.objects if o.type.name=='Sprite'and o.read().m_Name=='49-basilica')
 sheetpath=ROOT.parent/'native_v49/inputs/07-1000006258.png';sheet=Image.open(sheetpath).convert('RGBA');assert sha(sheetpath.read_bytes())=='828f3f629f3ced2b0b09f77753bca02ba3945db69e266965623d8e66c8f3550f'
 rects={'basilica':(0,0,650,590),'conclave':(650,168,1254,564),'seminary':(0,586,845,935),'smoke':(850,590,1254,945),'gate':(0,928,648,1254),'square':(648,928,1254,1254)}
 for name,rect in rects.items():
  im=sheet.crop(rect);im=im.crop(im.getbbox());w,h=im.size;path='mayomods55/church/'+name
  txo=copy.copy(template);txo.path_id=nextid;nextid+=1;txo.data=template.get_raw_data();file.objects[txo.path_id]=txo;tx=txo.read();tx.m_Name='mayomods55_church_'+name;tx.set_image(im,target_format=4);tx.save()
  so=copy.copy(sprite);so.path_id=nextid;nextid+=1;so.data=sprite.get_raw_data();file.objects[so.path_id]=so;st=so.read_typetree();st['m_Name']=tx.m_Name;digest=hashlib.sha256(path.encode()).digest();st['m_RenderDataKey']=({f'data[{i}]':struct.unpack_from('<I',digest,i*4)[0]for i in range(4)},21300000)
  st.update(m_Rect=dict(x=0.,y=0.,width=float(w),height=float(h)),m_Offset=dict(x=0.,y=0.),m_Pivot=dict(x=.5,y=.5),m_PixelsToUnits=100.,m_IsPolygon=False,m_AtlasTags=[],m_SpriteAtlas=dict(m_FileID=0,m_PathID=0),m_PhysicsShape=[])
  rd=st['m_RD'];rd.update(texture=dict(m_FileID=0,m_PathID=txo.path_id),alphaTexture=dict(m_FileID=0,m_PathID=0),secondaryTextures=[],textureRect=dict(x=0.,y=0.,width=float(w),height=float(h)),textureRectOffset=dict(x=0.,y=0.),atlasRectOffset=dict(x=0.,y=0.),settingsRaw=64,uvTransform=dict(x=100.,y=w/2,z=100.,w=h/2),downscaleMultiplier=1.)
  rd['m_IndexBuffer']=struct.pack('<6H',0,1,2,0,2,3);rd['m_SubMeshes']=[dict(firstByte=0,indexCount=6,topology=0,baseVertex=0,firstVertex=0,vertexCount=4,localAABB=dict(m_Center=dict(x=0.,y=0.,z=0.),m_Extent=dict(x=w/200,y=h/200,z=0.)))];vd=rd['m_VertexData'];vd['m_VertexCount']=4
  for c in vd['m_Channels']:c.update(stream=0,offset=0,format=0,dimension=0)
  vd['m_Channels'][0].update(dimension=3);vd['m_Channels'][4].update(stream=1,dimension=2);vd['m_DataSize']=struct.pack('<20f',-w/200,-h/200,0,-w/200,h/200,0,w/200,h/200,0,w/200,-h/200,0,0,0,0,1,1,1,1,0);so.save_typetree(st)
  for ob in [txo,so]:tree['m_Container'].append((path,dict(m_FileID=rid,m_PathID=ob.path_id)))
  added.append(dict(name=name,texture=txo.path_id,sprite=so.path_id,size=[w,h],pixel_sha256=sha(im.tobytes())))
 tree['m_Container'].sort(key=lambda x:x[0]);rm.save_typetree(tree);assert Counter((p,json.dumps(v,sort_keys=True))for p,v in oldpaths)<=Counter((p,json.dumps(v,sort_keys=True))for p,v in tree['m_Container'])
 out=ROOT/'bundles';out.mkdir(exist_ok=True);raw=next(iter(env.files.values())).save(packer='original');rawdata=next(iter(data.files.values())).save(packer='original');(out/'datapack.unity3d').write_bytes(raw);(out/'data.unity3d').write_bytes(rawdata)
 final=UnityPy.load(raw);seen=set();new={x['texture']:x for x in added};checks=0
 for ob in final.objects:
  if ob.path_id in original:
   typ,old=original[ob.path_id];assert old==ob.get_raw_data()or typ=='TextAsset'and ob.read().m_Name in changed;seen.add(ob.path_id);checks+=1
  elif ob.path_id in new:
   tx=ob.read();r=new[ob.path_id];assert sha(tx.image.convert('RGBA').tobytes())==r['pixel_sha256'];checks+=1
  else:assert ob.type.name=='Sprite'and ob.path_id in {x['sprite']for x in added}
 assert seen==original.keys()
 report=dict(passed=True,checks=checks,datapack_sha256=sha(raw),data_sha256=sha(rawdata),illustrations=added,source_sheet_sha256=sha(sheetpath.read_bytes()),changed_text_assets=changed,all_previous_sprites_and_textures_byte_identical=True,all_previous_resources_retained=True,physical_phone_tested=False,Unity_rendering_tested=False)
 (ROOT/'content55_validation.json').write_text(json.dumps(report,indent=2)+'\n');print({'passed':True,'checks':checks,'illustrations':len(added)},flush=True)
if __name__=='__main__':build(sys.argv[1])
