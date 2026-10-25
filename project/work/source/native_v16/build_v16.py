"""Competition artwork and opposition-only sports feedback on exact v15."""
import copy,csv,hashlib,io,json,os,struct,subprocess,sys,zipfile
from pathlib import Path
import UnityPy
from PIL import Image,ImageOps

ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
from build_prison_expansion import signature_entry,sha_file
from native_v16.native_sound import patch as patch_native
BUNDLE='assets/bin/Data/datapack.unity3d';DATA='assets/bin/Data/data.unity3d';LIB='lib/arm64-v8a/libil2cpp.so'
BASE_SHA='cf9442ac5585cfe7db028412228b28bc72532323ad579aacfbed36d5c9a7e6a5'
TOKENS={'v12_ChampionsLeague':'v16-champions','v12_EuropaLeague':'v12-europa','v12_ConferenceLeague':'v12-conference'}
def sha(b):return hashlib.sha256(b).hexdigest()
def key(o):return(o.assets_file.name,o.path_id)
def objects(env):return{key(o):sha(o.get_raw_data())for o in env.objects}
def run(args):return subprocess.run(list(map(str,args)),capture_output=True,text=True,check=True).stdout.strip()
def build(base,out):
    base=Path(base).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    assert sha_file(base)==BASE_SHA,'requires the exact delivered v15 APK'
    with zipfile.ZipFile(base)as z:
        env=UnityPy.load(z.read(BUNDLE));data=UnityPy.load(z.read(DATA));native,details=patch_native(z.read(LIB))
    native_report=json.loads((ROOT/'native_validation.json').read_text())
    assert native_report['binary_sha256']==sha(native)
    before=objects(env);before_data=objects(data);changed=set();added=set()
    textures={o.read().m_Name:o for o in env.objects if o.type.name=='Texture2D'}
    sprites={o.read().m_Name:o for o in env.objects if o.type.name=='Sprite'}
    texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'}
    template_tex=textures['a16_emoji-v12-europa'];template_spr=sprites['a16_emoji-v12-europa'];file=template_tex.assets_file
    rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree();original_rm=copy.deepcopy(tree)
    resource_id=next(v['m_FileID']for k,v in tree['m_Container']if k=='emoji/normal/a16_emoji-v12-europa')
    next_id=max(file.objects)+1;graphics={}
    for name,token in [('champions','v16-champions'),('europa','v12-europa'),('conference','v12-conference')]:
        full='a16_emoji-'+token;image=Image.open(ROOT/'assets'/f'{name}.png').convert('RGBA')
        fitted=ImageOps.contain(image,(128,128),Image.Resampling.LANCZOS);canvas=Image.new('RGBA',(128,128))
        canvas.paste(fitted,((128-fitted.width)//2,(128-fitted.height)//2))
        if name=='champions':
            txo=copy.copy(template_tex);txo.path_id=next_id;next_id+=1;txo.data=template_tex.get_raw_data();file.objects[txo.path_id]=txo;added.add(key(txo))
            spo=copy.copy(template_spr);spo.path_id=next_id;next_id+=1;spo.data=template_spr.get_raw_data();file.objects[spo.path_id]=spo;added.add(key(spo))
            st=spo.read_typetree();st['m_Name']=full;st['m_RD']['texture']=dict(m_FileID=0,m_PathID=txo.path_id)
            digest=hashlib.sha256(full.encode()).digest();st['m_RenderDataKey']=({f'data[{i}]':struct.unpack_from('<I',digest,i*4)[0]for i in range(4)},21300000)
            spo.save_typetree(st)
            for o in [txo,spo]:tree['m_Container'].append(('emoji/normal/'+full,dict(m_FileID=resource_id,m_PathID=o.path_id)))
        else:
            txo=textures[full];spo=sprites[full];changed.add(key(txo))
        tx=txo.read();tx.m_Name=full;tx.set_image(canvas,target_format=4);tx.save()
        graphics[full]=dict(texture=txo.path_id,sprite=spo.path_id,source=f'{name}.png',source_sha256=sha_file(ROOT/'assets'/f'{name}.png'),pixel_sha256=sha(canvas.tobytes()))
    menu=texts['genesis_v9_v12_soccer'];menu_data=json.loads(menu.read().m_Script);original_menu=copy.deepcopy(menu_data)
    for item in menu_data['Items']:
        if item['TileID']in TOKENS:item['Icon']=TOKENS[item['TileID']]
    comparison=copy.deepcopy(menu_data)
    for item,old in zip(comparison['Items'],original_menu['Items']):item['Icon']=old['Icon']
    assert comparison==original_menu
    a=menu.read();a.m_Script=json.dumps(menu_data,indent=2);a.save();changed.add(key(menu))
    scenes=texts['genesis_activities_v12'];rows=list(csv.DictReader(io.StringIO(scenes.read().m_Script)));original_rows=copy.deepcopy(rows)
    entries={'scenario.activitiesV12.enter1':'v16-champions','scenario.activitiesV12.enter2':'v12-europa','scenario.activitiesV12.enter3':'v12-conference'}
    for row in rows:
        if row['ScenarioID']in entries:row['EmojiString']=entries[row['ScenarioID']]
    check=copy.deepcopy(rows)
    for row,old in zip(check,original_rows):row['EmojiString']=old['EmojiString']
    assert check==original_rows
    buf=io.StringIO(newline='');writer=csv.DictWriter(buf,list(rows[0]),lineterminator='\r\n');writer.writeheader();writer.writerows(rows)
    a=scenes.read();a.m_Script=buf.getvalue().rstrip('\r\n');a.save();changed.add(key(scenes))
    tree['m_Container'].sort(key=lambda p:p[0]);rm.save_typetree(tree)
    bundle=next(iter(env.files.values())).save(packer='original');databytes=next(iter(data.files.values())).save(packer='original')
    reread=UnityPy.load(bundle);redata=UnityPy.load(databytes)
    assert len(list(reread.objects))==len(before)+2
    for o in reread.objects:
        if key(o)not in changed|added:assert sha(o.get_raw_data())==before[key(o)]
    reread_text={o.read().m_Name:o.read().m_Script for o in reread.objects if o.type.name=='TextAsset'}
    new_menu=json.loads(reread_text['genesis_v9_v12_soccer'])
    assert {it['TileID']:it['Icon']for it in new_menu['Items']if it['TileID']in TOKENS}==TOKENS
    new_rows={r['ScenarioID']:r for r in csv.DictReader(io.StringIO(reread_text['genesis_activities_v12']))}
    assert all(new_rows[id_]['EmojiString']==token for id_,token in entries.items())
    for full,g in graphics.items():
        tx=next(o for o in reread.objects if o.assets_file.name==file.name and o.path_id==g['texture']).read()
        sp=next(o for o in reread.objects if o.assets_file.name==file.name and o.path_id==g['sprite']).read()
        assert tx.m_Width==128 and tx.m_Height==128 and sha(tx.image.tobytes())==g['pixel_sha256']
        assert sp.m_Name==full and sp.m_Rect.width==128 and sp.m_Rect.height==128 and sp.m_RD.texture.path_id==g['texture']
    rr=next(o for o in redata.objects if o.type.name=='ResourceManager').read_typetree()
    check=copy.deepcopy(rr);check['m_Container']=[(k,v)for k,v in check['m_Container']if k!='emoji/normal/a16_emoji-v16-champions']
    expected=copy.deepcopy(original_rm);expected['m_Container'].sort(key=lambda p:p[0]);assert check==expected
    assert len(rr['m_Container'])==len(original_rm['m_Container'])+2
    for o in redata.objects:
        if key(o)!=key(rm):assert sha(o.get_raw_data())==before_data[key(o)]
    replacements={BUNDLE:bundle,DATA:databytes,LIB:native}
    unsigned=out/'v16-unsigned.tmp';signed=out/'v16-signed.tmp'
    with zipfile.ZipFile(base)as old,zipfile.ZipFile(unsigned,'w',allowZip64=False)as new:
        for entry in old.infolist():
            if signature_entry(entry.filename):continue
            info=copy.copy(entry);info.extra=b''
            if info.compress_type==zipfile.ZIP_STORED:
                align=16384 if info.filename.endswith('.so')else 4;position=new.fp.tell()+30+len(info.filename.encode())
                if position%align:
                    pad=(-position-4)%align
                    if pad<2:pad+=align
                    info.extra=struct.pack('<HHH',0xd935,pad,align)+b'\0'*(pad-2)
            new.writestr(info,replacements.get(entry.filename,old.read(entry.filename)),compresslevel=6)
    assert zipfile.ZipFile(unsigned).testzip()is None
    jar=SOURCE/'tools/apksig-8.7.3.jar'
    run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,signed,SOURCE/'signing/music-test-key.pem',SOURCE/'signing/music-test-cert.der'])
    signing={p:run(['java','-cp',jar,SOURCE/p,signed])for p in ['VerifyApk.java','VerifyNativeSigner.java']}
    assert all('verified=true'in result for result in signing.values())
    assert all(token in signing['VerifyApk.java']for token in ['v2=true','v3=true','errors=[]','warnings=[]'])
    with zipfile.ZipFile(base)as old,zipfile.ZipFile(signed)as new,signed.open('rb')as stream:
        assert new.testzip()is None and len(new.namelist())==len(set(new.namelist()))
        assert {x for x in old.namelist()if not signature_entry(x)}=={x for x in new.namelist()if not signature_entry(x)}
        for entry in new.infolist():
            if signature_entry(entry.filename):continue
            assert new.read(entry.filename)==replacements.get(entry.filename,old.read(entry.filename))
            if entry.compress_type==zipfile.ZIP_STORED:
                stream.seek(entry.header_offset+26);nm,ex=struct.unpack('<HH',stream.read(4))
                assert(entry.header_offset+30+nm+ex)%(16384 if entry.filename.endswith('.so')else 4)==0
    final=out/'BitLife_Native_Activities_v16.apk';signed.replace(final);unsigned.unlink()
    backup=out/'BitLife_Native_Activities_v16.zip'
    with zipfile.ZipFile(backup,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:z.write(final,final.name)
    with zipfile.ZipFile(backup)as z:assert sha(z.read(final.name))==sha_file(final)
    result=dict(apk=str(final),sha256=sha_file(final),size=final.stat().st_size,base_sha256=BASE_SHA,
                changed_apk_entries=list(replacements),graphics=graphics,menu_and_entry_icons_verified=True,
                original_gameplay_routes_preserved=True,unchanged_unity_objects=len(before)-len(changed),
                native_feedback_tests=native_report,suppressed_own_score_entry_points=details['suppressed_own_score_sites'],
                other_native_bytes_preserved=True,signing=signing,device_runtime_tested=False)
    (ROOT/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':build(*sys.argv[1:])
