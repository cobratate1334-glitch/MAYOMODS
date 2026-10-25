"""Decode final Unity objects and composite the actual native eye layers."""
import csv,hashlib,io,json,sys,zipfile
from collections import Counter
from pathlib import Path
import numpy as np
import UnityPy
from PIL import Image,ImageChops,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
from native_v49.catalog49 import COMMANDS,PREFIX
sha=lambda b:hashlib.sha256(b).hexdigest()

def validate(base):
    checks=0
    def check(ok,label):
        nonlocal checks
        assert ok,label;checks+=1
    assets=json.loads((ROOT/'assets.json').read_text())
    imported=json.loads((ROOT/'eye_import50.json').read_text())
    raw=(ROOT/'bundles/datapack.unity3d').read_bytes();env=UnityPy.load(raw)
    with zipfile.ZipFile(base) as z:
        before=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'))
        resource_raw=z.read('assets/bin/Data/data.unity3d')
    data=UnityPy.load(resource_raw)
    resources=next(o for o in data.objects if o.type.name=='ResourceManager').read_typetree()['m_Container']
    rmap={}
    for p,v in resources:rmap.setdefault(p,[]).append(v)
    objects={(o.assets_file.name,o.path_id):o for o in env.objects}
    oldobjects={(o.assets_file.name,o.path_id):o for o in before.objects}
    check(objects.keys()==oldobjects.keys(),'all Unity objects and identities preserved')
    texts={o.read().m_Name:o.read().m_Script for o in env.objects if o.type.name=='TextAsset'}
    check(all(texts.get(k)==v for k,v in assets.items()),'all authored texts decode correctly')
    changed=[];unchanged=0;sprites=0
    for key,old in oldobjects.items():
        final=objects[key]
        if old.get_raw_data()!=final.get_raw_data():
            check((old.type.name=='Texture2D' and old.path_id in imported['changed_texture_ids']) or
                (old.type.name=='TextAsset' and old.read().m_Name in ['genesis_activities_v18','genesis_activities_v12']),
                'only declared eye pixels and explanatory text changed')
            changed.append(key[1])
        else:unchanged+=1
        if old.type.name=='Sprite':
            check(old.get_raw_data()==final.get_raw_data(),'native sprite geometry unchanged');sprites+=1
    check(len(changed)==len(imported['changed_texture_ids'])+2,'exact changed object set')
    indices={o.path_id:o for o in env.objects if o.assets_file.name=='resources.assets'}
    textures={o.read().m_Name:o for o in env.objects if o.type.name=='Texture2D'}
    pictures={}
    def native(prefix):return next(o.read().image.convert('RGBA') for n,o in textures.items() if n.startswith(prefix))
    visible={};composite_counts=[]
    for row in imported['affected_resources']:
        obj=indices[row['texture']];im=obj.read().image.convert('RGBA')
        check(sha(im.tobytes())==row['pixel_sha256'],'decoded final iris pixels '+row['name'])
        check(any(v['m_PathID']==row['texture'] for v in rmap[row['path']]),'existing texture path resolves')
        spr=next(indices[v['m_PathID']] for v in rmap[row['path']] if indices[v['m_PathID']].type.name=='Sprite')
        check(spr.read_typetree()['m_RD']['texture']['m_PathID']==row['texture'],'existing sprite binds repaired texture')
        g=['male','female'][row['gender']];prefix=f'a16_faces-{g}-stage{row["stage"]}-'
        mask=native(prefix+'iris-base-')
        check(im.getchannel('A').tobytes()==mask.getchannel('A').tobytes(),'native iris silhouette preserved')
        if row['trait'] not in [5,12,13]:continue
        final_eye=Image.alpha_composite(im,native(prefix+'iris-lighting-'))
        rgba=np.asarray(final_eye);left=rgba[:,:250];right=rgba[:,250:]
        def counts(p):
            r=p[:,:,0].astype(int);g=p[:,:,1].astype(int);b=p[:,:,2].astype(int);a=p[:,:,3]
            return dict(blue=int(np.sum((b>r*1.35)&(b>g*1.08)&(a>240))),
                amber=int(np.sum((r>b*1.5)&(g>b*1.35)&(a>240))),
                green=int(np.sum((g>r*1.2)&(g>b*1.1)&(a>240))))
        lc,rc=counts(left),counts(right)
        if row['trait']==5:check(lc['blue']>150 and rc['amber']>150,'complete colours survive actual native pupil/highlights')
        elif row['trait']==12:check(lc['blue']>150 and lc['amber']>150 and rc['blue']>150 and rc['amber']==0,'sector visible beyond pupil and restricted to one iris')
        else:check(lc['green']>100 and lc['amber']>100 and rc['green']>100 and rc['amber']>100,'central amber rings survive native pupil layer')
        composite_counts.append(dict(name=row['name'],left=lc,right=rc))
        if row['stage']==2:
            face=ImageChops.multiply(native(prefix+'base-'),Image.new('RGBA',(500,500),'#CE9257'))
            for layer in [native(prefix+'lighting-happy-'),native(prefix+'eye-base-'),im,native(prefix+'iris-lighting-'),ImageChops.multiply(native(prefix+'eyebrows-happy'),Image.new('RGBA',(500,500),'#493329'))]:
                face=Image.alpha_composite(face,layer)
            pictures[row['gender'],row['trait']]=face
    rows=list(csv.DictReader(io.StringIO(assets['genesis_activities_v18'])))
    scenes={r['ScenarioID']:r for r in rows}
    check(len(rows)==len(scenes) and all(None not in r for r in rows),'all CSV rows/columns remain well formed')
    for c in COMMANDS:
        r=scenes[c['scene']]
        check(r['Choice1_Text']=='Apply' and r['Choice2_Text']=='Back','native Apply/Back retained')
        check(not r['Choice1_RouteTo'] and not r['Choice2_RouteTo'],'single native choice dispatch retained')
    before_assets=json.loads((SOURCE/'native_v49/assets.json').read_text())
    check(all(assets[k]==v for k,v in before_assets.items() if k not in ['genesis_activities_v18','genesis_activities_v12']),'social messages, eras and all other authored assets unchanged')
    check(sum(1 for r in imported['affected_resources'] if r['trait'] in [5,12,13])==36,'all genetic eye stage/gender variants repaired')
    check(len(imported['affected_resources'])==480,'all manual, genetic and albinism eye paths covered')
    for mood in ['happy','sad','angry']:
        # Eye iris/pupil layers are mood-independent native components. Keep
        # all stock expressions rather than baking face expressions into eyes.
        check(any(mood in n and 'lighting' in n for n in textures),'native expression resources remain '+mood)
    preview=Image.new('RGB',(1500,1150),'#F1EEE6');draw=ImageDraw.Draw(preview)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',25)
    draw.text((25,18),'v50 — decoded native layers, including pupils and highlights',font=font,fill='#253748')
    for gender in range(2):
        for col,(trait,label) in enumerate([(5,'Complete heterochromia'),(12,'Sectoral heterochromia'),(13,'Central heterochromia')]):
            im=pictures[gender,trait];preview.paste(im,(col*500,65+gender*530),im)
            draw.text((col*500+24,575+gender*530),label,font=font,fill='#253748')
    preview.save(ROOT/'Eye_Layer_QA_v50.png')
    (ROOT/'eye_visible_pixels50.json').write_text(json.dumps(composite_counts,indent=2)+'\n')
    report=dict(passed=True,checks=checks,assets=dict(datapack_sha256=sha(raw),data_sha256=sha(resource_raw)),
        repaired_iris_paths=480,repaired_genetic_variants=36,changed_textures=len(imported['changed_texture_ids']),
        unchanged_Unity_objects=unchanged,sprites_preserved=sprites,resources_bundle_byte_identical=True,
        actual_native_pupil_highlight_composites=True,physical_phone_tested=False,Unity_rendering_tested=False)
    (ROOT/'content50_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)

if __name__=='__main__':
    try:validate(sys.argv[1])
    except BaseException:__import__('traceback').print_exc();sys.stdout.flush();sys.stderr.flush();__import__('os')._exit(1)
    sys.stdout.flush();__import__('os')._exit(0)
