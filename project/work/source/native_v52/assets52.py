"""Update declared text resources and fit hair to native scalp/face anchors."""
import copy,hashlib,json,os,sys,zipfile
from pathlib import Path
from collections import Counter
import UnityPy
from PIL import Image,ImageChops,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(SOURCE),str(SOURCE/'native_v29')]
from native_v49.catalog49 import PAID_HAIR
from native_v49.assets49 import fit,isolate
sha=lambda b:hashlib.sha256(b).hexdigest()

def build(base,qa_only=False):
 assets=json.loads((ROOT/'assets.json').read_text());imports=json.loads((SOURCE/'native_v49/imports49.json').read_text())
 with zipfile.ZipFile(base)as z:oldpack=z.read('assets/bin/Data/datapack.unity3d');olddata=z.read('assets/bin/Data/data.unity3d')
 env=UnityPy.load(oldpack);data=UnityPy.load(olddata)
 texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'};textures={o.read().m_Name:o for o in env.objects if o.type.name=='Texture2D'}
 file=texts['a16_voltron_componentFilenames'].assets_file;indices=file.objects
 def native(prefix):return next(o.read().image.convert('RGBA')for n,o in textures.items()if n.startswith(prefix))
 def face(stage=2,gender=0):
  p=f'a16_faces-{"female"if gender else"male"}-stage{stage}-';out=ImageChops.multiply(native(p+'base-'),Image.new('RGBA',(500,500),'#CE9257'))
  layers=[native(p+'lighting-happy-'),native(p+'eye-base-')]
  eye=next(r for r in imports['imports']if r['kind']=='eyes'and r['stage']==stage and r['gender']==gender and r['left']==r['right']==1);layers.append(indices[eye['texture']].read().image.convert('RGBA'))
  layers.append(native(p+'iris-lighting-'));layers.append(ImageChops.multiply(native(p+'eyebrows-happy'),Image.new('RGBA',(500,500),'#493329')))
  for layer in layers:out=Image.alpha_composite(out,layer)
  return out
 def sheet(path,images,title):
  w=1250;tile=250;out=Image.new('RGB',(w,60+3*285),'#F3F0E9');d=ImageDraw.Draw(out);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
  d.text((15,15),title,font=font,fill='#23344A')
  for n,im in enumerate(images):
   im=Image.alpha_composite(face(),im).resize((tile,tile),Image.Resampling.LANCZOS);x=n%5*tile;y=55+n//5*285;out.paste(im,(x,y),im);d.text((x+10,y+252),PAID_HAIR[n],font=font,fill='#23344A')
  out.save(path)
 hair=[r for r in imports['imports']if r['kind']=='hair'];adult=[next(r for r in hair if(r['style'],r['stage'],r['gender'])==(i,2,0))for i in range(1,16)]
 sheet(ROOT/'Hair_Before52.png',[indices[r['texture']].read().image.convert('RGBA')for r in adult],'Decoded v51 hair layers on the native face — asset inspection')
 sheets={int(p.name[:2]):Image.open(p).convert('RGBA')for p in (SOURCE/'native_v49/inputs').glob('*.png')};cuts={};refit={};hair_changes=[]
 for r in hair:
  if r['texture']in refit:continue
  key=(r['source_sheet'],tuple(r['source_rect']))
  if key not in cuts:
   raw=isolate(sheets[key[0]].crop(key[1]));cuts[key]=raw.crop(raw.getbbox())
  raw=cuts[key];a=next(a for a in imports['anchors']if(a['gender'],a['stage'])==(r['gender'],r['stage']));l,t,right,bot=a['bbox'];fw=right-l;fh=bot-t
  long=r['style']in [3,5,6,7,9,10,11,12,13,14,15]
  margin=.15 if long else .06;height=fh*(1.05 if long else .58);top=max(0,t-.22*fh)
  im=fit(raw,(l-margin*fw,top,right+margin*fw,top+height));refit[r['texture']]=im
  hair_changes.append(dict(texture=r['texture'],style=r['style'],canonical_stage=r['stage'],canonical_gender=r['gender'],source_rect=r['source_rect'],target_box=[l-margin*fw,top,right+margin*fw,top+height],pixel_sha256=sha(im.tobytes())))
 sheet(ROOT/'Hair_After52.png',[refit[r['texture']]for r in adult],'v52 hair fitting — shorter vertical stretch and scalp-width alignment; asset inspection')
 if qa_only:return
 for path_id,im in refit.items():t=indices[path_id].read();t.set_image(im,target_format=4);t.save()
 changed=[];new=[];nextid=max(file.objects)+1
 rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree();beforepaths=copy.deepcopy(tree['m_Container']);rid=next(n+1 for n,e in enumerate(rm.assets_file.externals)if e.path=='resources.assets')
 for name,value in assets.items():
  if name in texts:
   obj=texts[name];t=obj.read()
   if t.m_Script==value:continue
  else:
   obj=copy.copy(texts['genesis_test_feature_events']);obj.path_id=nextid;nextid+=1;obj.data=obj.get_raw_data();file.objects[obj.path_id]=obj;t=obj.read();t.m_Name=name
   path=('genesis_lists/'if value.startswith('{')else'genesis/')+name
   assert not any(p==path for p,v in tree['m_Container']);tree['m_Container'].append((path,dict(m_FileID=rid,m_PathID=obj.path_id)));new.append(dict(name=name,path=path,path_id=obj.path_id))
  t.m_Script=value;t.save();changed.append(name)
 tree['m_Container'].sort(key=lambda x:x[0]);rm.save_typetree(tree)
 assert Counter((p,json.dumps(v,sort_keys=True))for p,v in beforepaths)<=Counter((p,json.dumps(v,sort_keys=True))for p,v in tree['m_Container'])
 out=ROOT/'bundles';out.mkdir(exist_ok=True)
 for name,e in [('datapack',env),('data',data)]:
  raw=next(iter(e.files.values())).save(packer='original');p=out/(name+'.unity3d');tmp=p.with_suffix('.partial')
  with tmp.open('wb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
  tmp.replace(p)
 report=dict(passed=True,base_datapack_sha256=sha(oldpack),base_data_sha256=sha(olddata),datapack_sha256=sha((out/'datapack.unity3d').read_bytes()),data_sha256=sha((out/'data.unity3d').read_bytes()),changed_text_assets=changed,new_resources=new,hair_changes=hair_changes,hair_layers=180,existing_resource_multiset_preserved=True,physical_phone_tested=False)
 (ROOT/'asset_build52.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=True,changed=len(changed),new=len(new))),flush=True)

if __name__=='__main__':build(sys.argv[1],'--qa-only'in sys.argv)
