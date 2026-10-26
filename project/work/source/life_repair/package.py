"""Pinned 1105 -> 1106 build. Preserve old resource and package identities."""
import copy,hashlib,io,json,struct,sys,zipfile
from pathlib import Path
import UnityPy
from PIL import Image
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent;sys.path[:0]=[str(SOURCE)]
from life_repair.content import build
from life_rework.package import sprite_tree
from native_v27.manifest_version import bump_version
from native_v55.build_v55 import signature_entry,symbols
BASE='cdff6bc415263e4ebd37c1180949096f5391fc3cbd0fda2149f5152f55b62fde'
sha=lambda value:hashlib.sha256(value).hexdigest()


def bundles(z):
    env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'));data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'))
    key=lambda obj:(obj.assets_file.name,obj.path_id)
    before={key(o):o.get_raw_data()for o in env.objects};before_data={key(o):o.get_raw_data()for o in data.objects}
    texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'}
    base={name:o.read().m_Script for name,o in texts.items()};overlay=build(base)
    file=texts['genesis_feature_containers'].assets_file;next_id=max(file.objects)+1;changed=set()
    rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree();paths=copy.deepcopy(tree['m_Container'])
    rid=next(i+1 for i,entry in enumerate(rm.assets_file.externals)if entry.path=='resources.assets')
    for name,value in overlay.items():
        if name in texts:obj=texts[name]
        else:
            obj=copy.copy(texts['genesis_test_feature_events']);obj.path_id=next_id;next_id+=1;obj.data=obj.get_raw_data();file.objects[obj.path_id]=obj
            resource=('genesis_lists/'if value.startswith('{')else'genesis/')+name
            assert not any(p==resource for p,_ in tree['m_Container']);tree['m_Container'].append((resource,dict(m_FileID=rid,m_PathID=obj.path_id)))
        decoded=obj.read();decoded.m_Name=name;decoded.m_Script=value;decoded.save();changed.add(key(obj))
    images=[]
    template=next(o for o in env.objects if o.type.name=='Texture2D');sprite_template=next(o for o in env.objects if o.type.name=='Sprite'and o.read().m_Name=='49-basilica')
    flags=['de_nazi','de_imperial','jp_naval','jp','it_royal','us48','uk','fr','ru_imperial','ussr']
    inputs=[('mayomods1106/flags/'+n,ROOT/'inputs'/(n+'.png'))for n in flags]
    inputs += [('mayomods1106/inlineflags/'+n,ROOT/'inputs'/('inline_'+n+'.png'))for n in flags]
    inputs += [('emoji/normal/scene1106-'+n,ROOT/'inputs'/('icon_'+n+'.png'))for n in ['art','pet','microphone','school','trench','aircraft','crew','storm']]
    for resource,path in inputs:
        canvas=Image.open(path).convert('RGBA');texture=copy.copy(template);texture.path_id=next_id;next_id+=1;texture.data=template.get_raw_data();file.objects[texture.path_id]=texture
        decoded=texture.read();decoded.m_Name=resource.rsplit('/',1)[1];decoded.set_image(canvas,target_format=4);decoded.save()
        sprite=copy.copy(sprite_template);sprite.path_id=next_id;next_id+=1;sprite.data=sprite_template.get_raw_data();file.objects[sprite.path_id]=sprite;sprite.save_typetree(sprite_tree(sprite,texture,canvas,decoded.m_Name))
        assert not any(p==resource for p,_ in tree['m_Container'])
        for obj in [texture,sprite]:tree['m_Container'].append((resource,dict(m_FileID=rid,m_PathID=obj.path_id)))
        if resource.startswith('emoji/normal/'):
            for obj in [texture,sprite]:tree['m_Container'].append((resource.replace('/normal/','/small/'),dict(m_FileID=rid,m_PathID=obj.path_id)))
        images.append(dict(resource=resource,sprite_id=sprite.path_id,texture_id=texture.path_id,canvas=list(canvas.size),pixel_sha256=sha(canvas.tobytes())))
    tree['m_Container'].sort(key=lambda item:item[0]);rm.save_typetree(tree)
    pack=next(iter(env.files.values())).save(packer='original');rawdata=next(iter(data.files.values())).save(packer='original')
    final=UnityPy.load(pack);objects={key(o):o for o in final.objects};assert before.keys()<=objects.keys()
    assert all(objects[k].get_raw_data()==value for k,value in before.items()if k not in changed)
    for name,value in overlay.items():
        assert next(o.read().m_Script for o in final.objects if o.type.name=='TextAsset'and o.read().m_Name==name)==value
    by_id={o.path_id:o for o in final.objects}
    for row in images:
        image=by_id[row['sprite_id']].read().image.convert('RGBA');assert image.size==tuple(row['canvas'])and sha(image.tobytes())==row['pixel_sha256']
    finaldata=UnityPy.load(rawdata);objects_data={key(o):o for o in finaldata.objects}
    assert before_data.keys()==objects_data.keys()and all(objects_data[k].get_raw_data()==value for k,value in before_data.items()if k!=key(rm))
    from collections import Counter
    canonical=lambda rows:Counter((p,json.dumps(v,sort_keys=True))for p,v in rows)
    assert canonical(paths)<=canonical(next(o for o in finaldata.objects if o.type.name=='ResourceManager').read_typetree()['m_Container'])
    return pack,rawdata,dict(passed=True,authored_assets_sha256=sha(json.dumps(overlay,sort_keys=True).encode()),changed_text_assets=len(overlay),preserved_objects=len(before)-len(changed&before.keys()),old_resources_preserved=True,imported_artwork=images,datapack_sha256=sha(pack),data_sha256=sha(rawdata))


def stage(base,work):
    base=Path(base);work=Path(work);assert sha(base.read_bytes())==BASE
    native=(work/'libil2cpp.so').read_bytes();manifest=json.loads((work/'native.json').read_text());assert sha(native)==manifest['binary_sha256']
    for name in ['native_validation.json','content_validation.json','structure_validation.json']:
        report=json.loads((work/name).read_text());assert report['passed']
        if name!='content_validation.json':assert report['binary_sha256']==sha(native)
    dex=(work/'dex1106-final/classes13.dex').read_bytes();report=json.loads((work/'dex1106-final/dex_validation.json').read_text());assert report['passed']and report['binary_sha256']==sha(dex)
    with zipfile.ZipFile(base)as z:
        pack,data,report=bundles(z);(work/'bundle_validation.json').write_text(json.dumps(report,indent=2)+'\n')
        assert report['authored_assets_sha256']==json.loads((work/'content_validation.json').read_text())['authored_assets_sha256']
        android,_=bump_version(z.read('AndroidManifest.xml'),old=1105,new=1106)
        diagnostic_symbols=symbols(native,manifest);diagnostic_symbols.update(build='1106',version_code=1106)
        changes={'lib/arm64-v8a/libil2cpp.so':native,'classes13.dex':dex,'assets/bin/Data/datapack.unity3d':pack,'assets/bin/Data/data.unity3d':data,'AndroidManifest.xml':android,'assets/mayomods54/native_symbols.json':json.dumps(diagnostic_symbols,indent=2).encode()}
        extras={'assets/mayomods1106/sfx/'+f.name:f.read_bytes()for f in (ROOT/'inputs/sfx').glob('*.wav')}
        extras['assets/mayomods1106/ATTRIBUTION.txt']=(ROOT/'ATTRIBUTION.txt').read_bytes()
        target=work/'MayoMods_1106_UNSIGNED_WORK.apk';assert not target.exists()
        with zipfile.ZipFile(target,'x',allowZip64=False)as out:
            for entry in z.infolist():
                if signature_entry(entry.filename):continue
                info=copy.copy(entry);info.extra=b''
                if info.compress_type==zipfile.ZIP_STORED:
                    alignment=16384 if info.filename.endswith('.so')else 4;position=out.fp.tell()+30+len(info.filename.encode())
                    if position%alignment:
                        pad=(-position-4)%alignment
                        if pad<2:pad+=alignment
                        info.extra=struct.pack('<HHH',0xd935,pad,alignment)+b'\0'*(pad-2)
                out.writestr(info,changes.get(info.filename,z.read(info.filename)))
            for name,value in extras.items():
                info=zipfile.ZipInfo(name);info.compress_type=zipfile.ZIP_STORED;position=out.fp.tell()+30+len(name.encode());pad=(-position-4)%4
                if position%4:
                    if pad<2:pad+=4
                    info.extra=struct.pack('<HHH',0xd935,pad,4)+b'\0'*(pad-2)
                out.writestr(info,value)
        with zipfile.ZipFile(target)as final:
            assert final.testzip()is None and len(set(final.namelist()))==len(final.namelist())
            assert set(final.namelist())=={n for n in z.namelist()if not signature_entry(n)}|set(extras)
            assert all(final.read(n)==v for n,v in extras.items())
            assert all(final.read(n)==value for n,value in changes.items())
            assert all(final.read(n)==z.read(n)for n in z.namelist()if n not in changes and not signature_entry(n))
        report=dict(staged=True,signed=False,base_sha256=BASE,apk_sha256=sha(target.read_bytes()),native_sha256=sha(native),modified_entries=sorted(changes),added_entries=sorted(extras),version_code=1106,phone_tested=False)
        (work/'staging_report.json').write_text(json.dumps(report,indent=2)+'\n');print(target)


if __name__=='__main__':stage(*sys.argv[1:])
