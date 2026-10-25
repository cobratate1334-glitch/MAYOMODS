"""Append original period sprites and native inventory rows, preserving other objects."""
import ast,base64,copy,csv,hashlib,io,json,struct,sys,zipfile
from collections import Counter
from pathlib import Path
from PIL import Image
import UnityPy
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE)]
from catalog45 import CARS,HOUSES,ART_KEYS
sha=lambda b:hashlib.sha256(b).hexdigest()
def codec():
 tree=ast.parse((SOURCE/'build_expansion.py').read_text())
 nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['decode','encode'] or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='KEY' for t in n.targets)]
 ns={'base64':base64};exec(compile(ast.Module(body=nodes,type_ignores=[]),'retained_catalog_codec','exec'),ns);return ns['decode'],ns['encode']
def rows(text):return list(csv.DictReader(io.StringIO(text)))
def author():
 assets=json.loads((SOURCE/'native_v44/assets.json').read_text());decode,encode=codec()
 for key,items in [('a16_car-models-enc',CARS),('a16_house-types-enc',HOUSES)]:
  before=rows(decode(assets[key]));fields=list(before[0]);new=[]
  for item in items:
   r={k:'' for k in fields}
   if 'Make' in fields:
    r.update({'Make':item['make'],'Model':item['model'],'Type':item['type'],'Cost':f"${item['price']:,}",'Depreciation Score':'3','Reliability Score':'4','Longevity Score':'4','Cool Score':'5' if item['luxury'] or item['race_only'] else '3','Ease of Theft Score':'3','Luxury Only':'x' if item['luxury'] else '', 'Race Car Dealership Only':'x' if item['race_only'] else '', 'Race Type Whitelist':'street, demolition, circuit','Racing Class':item['racing_class'],'Durability Score':'80' if item['race_only'] else '65'})
   else:
    r.update({'Type':item['name'],'Emoji':'mayo45-'+item['art'],'Descriptors':item['desc'],'Minimum Bedrooms':str(item['beds'][0]),'Maximum Bedrooms':str(item['beds'][1]),'Minimum Bathrooms':str(item['baths'][0]),'Maximum Bathrooms':str(item['baths'][1]),'Minimum Age':'0','Maximum Age':'80','Appreciates':'x','Price Score':str(item['price']),'Commonness Score':'3','Maximum Pets':'5','Has Garden':'x','Haunted Score':'0','Street Type':'Residential'})
   new.append(r)
  out=io.StringIO();w=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(before+new)
  assets[key]=encode(out.getvalue());after=rows(decode(assets[key]));assert after==before+new
  (ROOT/(key.replace('-enc','')+'.csv')).write_text(out.getvalue())
 # Register persistent cache properties with Genesis. No menu entry is
 # emitted: these values support the existing native shopping screens.
 defaults='key,type,value,reset_on_ageup,minimum,maximum\n'
 schema={}
 for key in ['MarketYear','LuxuryYear','RacingYear']:
  defaults+=f'{key},int,0,,0,9999\n';schema[key]=dict(key=key,type='int',value=0,reset_on_ageup='',minimum=0,maximum=9999)
 for key in ['MarketCity','MarketCountry']:
  defaults+=f'{key},string,,,,\n';schema[key]=dict(key=key,type='string',value='',reset_on_ageup='',minimum='',maximum='')
 assets['genesis_v18_defaults_era45']=defaults
 reg=assets['genesis_feature_containers'];assert '\nera45,'not in reg
 reg+=(''if reg.endswith('\n')else'\n')+'era45,Era World,,genesis_v18_defaults_era45,,content,,,,,,,0,,,\n'
 assets['genesis_feature_containers']=reg
 old='This calendar controls the accessory collections; the game’s other careers and events retain their existing rules.'
 new='This calendar controls accessory collections, vehicle stock, house styles and social-platform availability. Careers, events and the wider economy retain their existing rules.'
 for key in ['genesis_activities_v18','genesis_activities_v12']:
  assert old in assets[key];assets[key]=assets[key].replace(old,new)
 schemas=json.loads((SOURCE/'native_v44/schemas.json').read_text());schemas['era45']=schema
 (ROOT/'schemas.json').write_text(json.dumps(schemas,indent=2)+'\n')
 (ROOT/'assets.json').write_text(json.dumps(assets,ensure_ascii=True,indent=2)+'\n');return assets

def artwork():
 out=ROOT/'assets';out.mkdir(exist_ok=True);catalog=[]
 for key in ART_KEYS:
  source=Image.open(ROOT/'originals'/(key+'.png')).convert('RGBA')
  assert source.getextrema()[3][0]==0 and source.getbbox(),key
  art=source.crop(source.getbbox());art.thumbnail((460,430),Image.Resampling.LANCZOS)
  im=Image.new('RGBA',(500,500));im.alpha_composite(art,((500-art.width)//2,(500-art.height)//2))
  n='a16_emoji-mayo45-'+key;im.save(out/(n+'.png'))
  catalog.append(dict(name=n,source=n+'.png',path='emoji/normal/'+n,key='mayo45-'+key,pixel_sha256=sha(im.tobytes())))
 (ROOT/'world45_art_catalog.json').write_text(json.dumps(catalog,indent=2)+'\n');return catalog

def graphics(env,file,tree,rid,next_id,catalog):
    # Same established quad encoder as v19/v42/v43, with fresh object IDs.
    from native_v19 import hair_assets
    source=Path(hair_assets.__file__).read_text();start=source.index('  to=copy.copy(tex)');end=source.index(' return results,changed,next_id',start)
    encoder=source[start:end].replace("item.get('source',f'hair{item[\"style\"]+1}.png')","item['source']")
    scope={'copy':copy,'struct':struct,'hashlib':hashlib,'Image':Image}
    fn="def encode(env,file,tree,resources_id,next_id,catalog,root):\n tex=next(o for o in env.objects if o.type.name=='Texture2D'and o.read().m_Name=='a16_faces-male-stage2-hair-base1-00792')\n spr=next(o for o in env.objects if o.type.name=='Sprite'and o.read().m_Name=='a16_faces-male-stage2-hair-base1-00792')\n changed=set();results={}\n for item in catalog:\n  n=item['name'];im=Image.open(root/'assets'/item['source']).convert('RGBA')\n"+encoder+" return results,changed,next_id\n"
    exec(compile(fn,'world45_sprite_encoder','exec'),scope)
    return scope['encode'](env,file,tree,rid,next_id,catalog,ROOT)

def build(base,out):
    assert sha(Path(base).read_bytes())=='27628db7928ad64f492d61e4da0e42d59594cedd279a6c24dc049b4c34389bff'
    assets=author();catalog=artwork();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(base)as z:
        env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'));data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'))
    key=lambda o:(o.assets_file.name,o.path_id)
    before={key(o):sha(o.get_raw_data())for o in env.objects};bd={key(o):sha(o.get_raw_data())for o in data.objects}
    texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'}
    rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree();paths=copy.deepcopy(tree['m_Container']);deps=copy.deepcopy(tree['m_DependentAssets'])
    rid=next(n+1 for n,e in enumerate(rm.assets_file.externals)if e.path=='resources.assets')
    file=texts['genesis_activities_v18'].assets_file;next_id=max(file.objects)+1;changed=set();added={}
    for name,value in assets.items():
        if name in texts and texts[name].read().m_Script==value:continue
        if name in texts:obj=texts[name];changed.add(key(obj))
        else:
            original=texts['genesis_test_feature_events'];obj=copy.copy(original);obj.path_id=next_id;next_id+=1;obj.data=original.get_raw_data();file.objects[obj.path_id]=obj;added[name]=obj.path_id
            path=('genesis_lists/'if value.startswith('{')else'genesis/')+name
            assert path not in dict(tree['m_Container']);tree['m_Container'].append((path,dict(m_FileID=rid,m_PathID=obj.path_id)))
        asset=obj.read();asset.m_Name=name;asset.m_Script=value;asset.save()
    registered,ids,_=graphics(env,file,tree,rid,next_id,catalog)
    tree['m_Container'].sort(key=lambda x:x[0]);rm.save_typetree(tree)
    # Save fully before reloading; no dependent packager runs on partial files.
    bundle=next(iter(env.files.values())).save(packer='original');db=next(iter(data.files.values())).save(packer='original')
    (out/'datapack.unity3d').write_bytes(bundle);(out/'data.unity3d').write_bytes(db)
    ae=UnityPy.load(bundle);ad=UnityPy.load(db)
    after={key(o):sha(o.get_raw_data())for o in ae.objects};afterd={key(o):sha(o.get_raw_data())for o in ad.objects}
    assert set(before)<=set(after)and{k for k in before if before[k]!=after[k]}==changed
    assert set(bd)==set(afterd)and{k for k in bd if bd[k]!=afterd[k]}=={key(rm)}
    rt=next(o for o in ad.objects if o.type.name=='ResourceManager').read_typetree()
    assert Counter((p,json.dumps(v,sort_keys=True))for p,v in paths)<=Counter((p,json.dumps(v,sort_keys=True))for p,v in rt['m_Container'])
    assert rt['m_DependentAssets']==deps
    vals={o.read().m_Name:o.read().m_Script for o in ae.objects if o.type.name=='TextAsset'}
    assert all(vals[n]==v for n,v in assets.items())
    textures={o.read().m_Name:o for o in ae.objects if o.type.name=='Texture2D'};sprites={o.read().m_Name:o for o in ae.objects if o.type.name=='Sprite'}
    for item in catalog:
        n=item['name'];im=textures[n].read().image.convert('RGBA');assert im.size==(500,500)and sha(im.tobytes())==item['pixel_sha256']
        paths_for_name=[x for p,x in rt['m_Container']if p==item['path']]
        assert {x['m_PathID']for x in paths_for_name}=={registered[n]['texture'],registered[n]['sprite']}
        assert sprites[n].read_typetree()['m_RD']['texture']['m_PathID']==registered[n]['texture']
    report=dict(passed=True,road_models=24,racing_variants=16,new_house_types=8,new_artwork=17,new_Texture2D_and_Sprite_objects=34,added_TextAssets=added,modified_TextAssets=len(changed),all_unedited_Unity_objects_preserved=True,all_existing_resource_paths_preserved=True,all_asset_texture_pixel_roundtrips_verified=True,datapack_sha256=sha(bundle),data_sha256=sha(db),device_rendering_tested=False)
    (ROOT/'content45_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':build(*sys.argv[1:])
