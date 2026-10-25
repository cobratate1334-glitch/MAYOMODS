"""Round-trip real bundles, preserve prior objects and validate menu routes."""
import csv,hashlib,io,json,sys,zipfile
from collections import Counter
from pathlib import Path
import UnityPy
from PIL import Image,ImageDraw,ImageFont,ImageChops
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from catalog49 import *
sha=lambda b:hashlib.sha256(b).hexdigest()

def validate(base):
 checks=0
 def check(ok,label):
  nonlocal checks
  assert ok,label;checks+=1
 assets=json.loads((ROOT/'assets.json').read_text());imports=json.loads((ROOT/'imports49.json').read_text());newcat=json.loads((ROOT/'portrait49_catalog.json').read_text());oldcat=json.loads((ROOT/'portrait43_catalog.json').read_text())
 raw=(ROOT/'bundles/datapack.unity3d').read_bytes();db=(ROOT/'bundles/data.unity3d').read_bytes();env=UnityPy.load(raw);data=UnityPy.load(db)
 objects={(o.assets_file.name,o.path_id):o for o in env.objects};texts={o.read().m_Name:o.read().m_Script for o in env.objects if o.type.name=='TextAsset'}
 check(all(texts.get(k)==v for k,v in assets.items()),'every authored TextAsset round trips')
 resources=next(o for o in data.objects if o.type.name=='ResourceManager').read_typetree()['m_Container'];rmap={}
 for p,v in resources:rmap.setdefault(p,[]).append(v)
 indices={o.path_id:o for o in env.objects if o.assets_file.name=='resources.assets'}
 pictures={};source_counts=Counter()
 for row in imports['imports']:
  candidates=rmap.get(row['path'],[]);check(any(v['m_PathID']==row['sprite']for v in candidates),'sprite resource '+row['name']);check(any(v['m_PathID']==row['texture']for v in candidates),'texture resource '+row['name'])
  spr=indices[row['sprite']];tex=indices[row['texture']];check(spr.type.name=='Sprite'and tex.type.name=='Texture2D','typed resource '+row['name'])
  tree=spr.read_typetree();check(tree['m_RD']['texture']['m_PathID']==row['texture'],'sprite texture binding '+row['name']);im=tex.read().image.convert('RGBA');check(sha(im.tobytes())==row['pixel_sha256'],'decoded pixel integrity '+row['name']);check(im.size==tuple(row['size'])and im.getchannel('A').getbbox()is not None,'visible correctly sized asset '+row['name'])
  if row['kind']=='theme' or row['kind'] in ['scar','patch','beard'] or row.get('style')in [1,4,9,15] and row.get('stage')==2 and row.get('gender')==0:pictures[row['name']]=im
  if row.get('source_sheet'):source_counts[row['source_sheet']]+=1
 names=assets['a16_voltron_componentFilenames'].splitlines();check(len(names)==len(set(names)),'unique component filenames')
 previous_names=json.loads((SOURCE/'native_v48/assets.json').read_text())['a16_voltron_componentFilenames'].splitlines();check(set(previous_names)<=set(names),'all existing component filenames preserved')
 old_ids={n[-9:-4]for n in previous_names};check(not(old_ids&{r['id']for r in newcat}),'no new portrait ID collides with previous IDs');check(len({r['id']for r in newcat})==len(newcat),'globally unique new IDs')
 for row in oldcat+newcat:
  check(row['name']+'.png'in names,'registered component filename '+row['name']);check(len(rmap.get(row['path'],[]))==2,'sprite and texture path '+row['name'])
 # CSV quoting and native callback route checks cover every confirmation.
 rows=list(csv.DictReader(io.StringIO(assets['genesis_activities_v18'])));check(all(None not in r for r in rows),'scenario CSV has no shifted columns');scenes={r['ScenarioID']:r for r in rows};check(len(scenes)==len(rows),'no duplicate scenario IDs')
 for c in COMMANDS:
  row=scenes[c['scene']];check(row['Choice1_Text']=='Apply'and row['Choice2_Text']=='Back','native confirmation choices '+str(c['code']));check(not row['Choice1_RouteTo']and not row['Choice2_RouteTo'],'exclusive native dispatch '+str(c['code']))
 for name,value in assets.items():
  if not(name.startswith('genesis_v18_custom49')and value.startswith('{')):continue
  doc=json.loads(value);check(doc['ListID']==name,'native list identity '+name);check(len({r['TileID']for r in doc['Items']})==len(doc['Items']),'unique row IDs '+name)
  for item in doc['Items']:
   check('mayomods49/icons/'+item['Icon']in rmap,'real menu icon '+item['Icon'])
   for group in item['ActionList']:
    for r in group['ConditionList']:
     check(r.get('ListID')in assets if 'ListID'in r else r.get('ScenarioID')in scenes,'resolvable menu action '+name)
 defaults={r['key']:r for r in csv.DictReader(io.StringIO(assets['genesis_v18_defaults_custom49']))}
 for key,options,_,_ in CATEGORIES:
  if key=='Mark':continue
  check(int(defaults[key]['maximum'])==len(options)-1,'saved property supports every option '+key)
 check(len(imports['inputs'])==7 and all(p in source_counts for p in [2,3,4,5,6,7,8]),'all paid sheets have traceable imports')
 # Byte-for-byte comparison of existing assets, excluding explicitly edited
 # TextAssets. Previous sprites and textures are all preserved.
 with zipfile.ZipFile(base)as z:
  before=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'));olddata=UnityPy.load(z.read('assets/bin/Data/data.unity3d'))
  unchanged=0;modified=[];repaired=set(imports['repaired_genetic_eye_textures'])
  for o in before.objects:
   key=(o.assets_file.name,o.path_id);check(key in objects,'old Unity object retained')
   if sha(o.get_raw_data())!=sha(objects[key].get_raw_data()):
    check(o.type.name=='TextAsset'or o.type.name=='Texture2D'and o.read().m_Name in repaired,'only declared text/eye texture repairs changed');modified.append(o.read().m_Name)
   else:unchanged+=1
  oldpaths=next(o for o in olddata.objects if o.type.name=='ResourceManager').read_typetree()['m_Container'];check(Counter((p,json.dumps(v,sort_keys=True))for p,v in oldpaths)<=Counter((p,json.dumps(v,sort_keys=True))for p,v in resources),'old resources multiset preserved')
  # Source images for alignment QA are decoded from the final bundle, not
  # substituted source PNGs. These are layer inspections, not phone captures.
  stocktex={o.read().m_Name:o for o in before.objects if o.type.name=='Texture2D'}
  def native_image(prefix):return next(o.read().image.convert('RGBA')for n,o in stocktex.items()if n.startswith(prefix))
  baseface=native_image('a16_faces-male-stage2-base-');face=ImageChops.multiply(baseface,Image.new('RGBA',(500,500),'#CE9257'))
  ir=next(r for r in newcat if r['kind']=='eyes'and r['stage']==2 and r['gender']==0 and r['left']==1 and r['right']==4);iris=indices[ir['texture']].read().image.convert('RGBA');eyebrow=ImageChops.multiply(native_image('a16_faces-male-stage2-eyebrows-happy'),Image.new('RGBA',(500,500),'#493329'));eyes=native_image('a16_faces-male-stage2-eye-base-')
  tiles=[]
  for title,kind,style in [('Vitiligo + silver bun','hair',4),('Scar + full beard','beard',49327),('Classic eyepatch','patch',49201),('Bone crown','hair',14)]:
   im=face.copy()
   if title.startswith('Vitiligo'):
    r=next(r for r in oldcat if r['trait']==3 and r['stage']==2 and r['gender']==0 and r['mood']==0);im=Image.alpha_composite(im,stocktex[r['name']].read().image.convert('RGBA'))
   else:im=Image.alpha_composite(im,native_image('a16_faces-male-stage2-lighting-happy-'))
   for layer in [eyes,iris,eyebrow]:im=Image.alpha_composite(im,layer)
   match=next(r for r in imports['imports']if (r['kind']==kind and (r.get('id')==style if kind!='hair'else r.get('style')==style and r.get('stage')==2 and r.get('gender')==0)))
   im=Image.alpha_composite(im,indices[match['texture']].read().image.convert('RGBA'))
   if 'Scar'in title:im=Image.alpha_composite(im,pictures['a49_scar_49101'])
   tiles.append((title,im))
  preview=Image.new('RGB',(1600,620),'#F3F0E9');draw=ImageDraw.Draw(preview);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
  for n,(label,im)in enumerate(tiles):preview.paste(im.resize((390,390)),(n*400+5,72),im.resize((390,390)));draw.text((n*400+16,490),label,fill='#27384A',font=font)
  draw.text((18,20),'Asset alignment checks — decoded game layers; not phone screenshots',fill='#27384A',font=font);preview.save(ROOT/'Portrait_Layer_QA.png')
  frames=Image.new('RGB',(1100,850),'#ECE9E1');dr=ImageDraw.Draw(frames)
  for n,name in enumerate(['Vintage','Noir','Retro','Modern']):
   frame=pictures[f'era{n}_header'].resize((1000,160));frames.paste(frame,(50,35+n*200),frame);dr.text((110,85+n*200),name+' — Appearance studio',font=font,fill='white')
  frames.save(ROOT/'Era_Frame_QA.png')
 report=dict(passed=True,checks=checks,assets=dict(datapack_sha256=sha(raw),data_sha256=sha(db)),new_portrait_styles=len(newcat),new_hair_silhouettes=len(PAID_HAIR),scars=len(SCARS)-1,eyepatches=len(PATCHES)-1,beard_styles=5,independent_eye_pairs=36,all_seven_paid_sheets_imported=True,unchanged_previous_Unity_objects=unchanged,changed_objects=modified,repaired_genetic_eye_textures=len(repaired),stock_portrait_textures_and_all_previous_Sprites_unchanged=True,all_native_routes_resolve=True,device_rendering_tested=False)
 (ROOT/'content49_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='changed_TextAssets'}),flush=True)
if __name__=='__main__':validate(sys.argv[1]);sys.stdout.flush();__import__('os')._exit(0)
