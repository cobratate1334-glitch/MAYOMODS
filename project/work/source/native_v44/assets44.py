"""Fit transparent artwork and append native textures, sprites and menus."""
import copy,hashlib,io,json,struct,sys,zipfile
from collections import Counter
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import UnityPy
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE)]
from catalog44 import ITEMS
from content44 import author
sha=lambda b:hashlib.sha256(b).hexdigest()

def artwork():
    out=ROOT/'assets';out.mkdir(exist_ok=True);catalog=[]
    with zipfile.ZipFile(ROOT/'originals/User_Accessories.zip')as z:
        for item in ITEMS:
            if item['id']<=23:
                name=next(n for n in z.namelist()if item['source']in n and n.endswith('.png'))
                source=Image.open(io.BytesIO(z.read(name))).convert('RGBA')
            else:source=Image.open(ROOT/'originals'/(item['source']+'.png')).convert('RGBA')
            assert source.getextrema()[3][0]==0 and source.getbbox()
            crop=source.crop(source.getbbox())
            if item['slot']=='Headwear':
                width=480 if item['regional']else 390 if any(w in item['name']for w in ['Baseball','Beanie','Snapback'])else 440
                height=round(crop.height*width/crop.width)
                if height>315:width=round(width*315/height);height=315
                art=crop.resize((width,height),Image.Resampling.LANCZOS)
                center=art.getchannel('A').crop((max(0,width//2-3),0,min(width,width//2+4),height)).getbbox()
                assert center
                # Anchor the front of the brim. Curved bucket/cowboy brims
                # extend below that point at their sides and must not float.
                xy=((500-width)//2,320-center[3])
            else:
                art=crop.resize((round(crop.width*500/700),round(crop.height*500/700)),Image.Resampling.LANCZOS)
                xy=(280,300)
            im=Image.new('RGBA',(500,500));im.alpha_composite(art,xy)
            assert im.getbbox()and max(im.getbbox())<=500
            name=f'a44_accessory_{item["id"]:02d}';im.save(out/(name+'.png'))
            catalog.append(dict(name=name,source=name+'.png',path='emoji/voltron/accessories/era44/'+name,item=item['id'],slot=item['slot'],pixel_sha256=sha(im.tobytes())))
    (ROOT/'accessory44_catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
    return catalog

def graphics(env,file,tree,rid,next_id,catalog):
    # Same established quad encoder as v19/v42/v43, with fresh object IDs.
    from native_v19 import hair_assets
    source=Path(hair_assets.__file__).read_text();start=source.index('  to=copy.copy(tex)');end=source.index(' return results,changed,next_id',start)
    encoder=source[start:end].replace("item.get('source',f'hair{item[\"style\"]+1}.png')","item['source']")
    scope={'copy':copy,'struct':struct,'hashlib':hashlib,'Image':Image}
    fn="def encode(env,file,tree,resources_id,next_id,catalog,root):\n tex=next(o for o in env.objects if o.type.name=='Texture2D'and o.read().m_Name=='a16_faces-male-stage2-hair-base1-00792')\n spr=next(o for o in env.objects if o.type.name=='Sprite'and o.read().m_Name=='a16_faces-male-stage2-hair-base1-00792')\n changed=set();results={}\n for item in catalog:\n  n=item['name'];im=Image.open(root/'assets'/item['source']).convert('RGBA')\n"+encoder+" return results,changed,next_id\n"
    exec(compile(fn,'accessory44_sprite_encoder','exec'),scope)
    return scope['encode'](env,file,tree,rid,next_id,catalog,ROOT)

def build(base,out):
    assert sha(Path(base).read_bytes())=='9bc2beed4310a678f85dcc53592e12c6864668976bed3bc18df3c0d4631bf697'
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
    report=dict(passed=True,accessories=len(catalog),user_assets=23,new_original_assets=4,new_Texture2D_and_Sprite_objects=54,added_TextAssets=added,modified_TextAssets=len(changed),all_unedited_Unity_objects_preserved=True,all_existing_resource_paths_preserved=True,all_accessory_texture_pixel_roundtrips_verified=True,datapack_sha256=sha(bundle),data_sha256=sha(db),device_rendering_tested=False)
    (ROOT/'content44_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':build(*sys.argv[1:])
