"""Replace iris pixels only; retain v49 resource IDs and sprite geometry."""
import csv, hashlib, io, json, os, sys, zipfile
from pathlib import Path
import numpy as np
from PIL import Image
import UnityPy
ROOT=Path(__file__).resolve().parent; SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
from native_v29.content import writecsv
from native_v49.catalog49 import EYE_HEX, PREFIX
sha=lambda b:hashlib.sha256(b).hexdigest()

def eyes(iris,left,right,mode=0):
    # Iris-base is the native colour mask. Sclera, pupil and highlights have
    # their own stock layers. Painting white inside this mask shrank v49's
    # coloured region and obscured the sector under the stock pupil.
    alpha=np.asarray(iris.getchannel('A')); out=np.zeros((500,500,4),dtype=np.uint8)
    yy,xx=np.mgrid[:500,:500]
    for side,color in enumerate([left,right]):
        lo=side*250; box=iris.getchannel('A').crop((lo,0,lo+250,500)).getbbox(); assert box
        x0,y0,x1,y1=box; x0+=lo; x1+=lo
        cx=(x0+x1-1)/2; cy=(y0+y1-1)/2
        nx=(xx-cx)/((x1-x0)/2); ny=(yy-cy)/((y1-y0)/2)
        radius=np.sqrt(nx*nx+ny*ny)
        shade=np.clip(1.07-.31*radius,.66,1.)
        rgb=np.asarray(list(bytes.fromhex(color)),dtype=float)
        pixels=np.rint(shade[:,:,None]*rgb).astype(np.uint8)
        if mode==12 and side==0:
            # A full 120-degree sector extends beyond the pupil to the iris edge.
            angle=np.mod(np.degrees(np.arctan2(ny,nx)),360)
            sector=(angle>=300)|(angle<=60)
            amber=np.rint(shade[:,:,None]*np.array([220,164,63])).astype(np.uint8)
            pixels[sector]=amber[sector]
        if mode==13:
            centre=radius<.78
            amber=np.rint(shade[:,:,None]*np.array([215,159,61])).astype(np.uint8)
            pixels[centre]=amber[centre]
        out[:,lo:lo+250,:3]=pixels[:,lo:lo+250]
    out[:,:,3]=alpha
    return Image.fromarray(out)

def content():
    a=json.loads((SOURCE/'native_v49/assets.json').read_text())
    for name in ['genesis_activities_v18','genesis_activities_v12']:
        rows=list(csv.DictReader(io.StringIO(a[name])))
        for r in rows:
            if not r['ScenarioID'].startswith(PREFIX): continue
            code=int(r['ScenarioID'][len(PREFIX):])
            if code in [805,812,813]:
                description={805:'Different colours in the two eyes.',812:'A blue iris with a distinct amber sector in one eye.',813:'Green irises with amber around the pupils.'}[code]
                r['Body']=description+' Apply this genetic appearance? This replaces manual eye colours. Your other appearance choices stay in place. Choose Back to keep your current look.'
            elif 600<=code<=606 or 700<=code<=706:
                r['Body']='Apply this eye colour? Choosing manual eye colours replaces heterochromia. Hair, skin marks and accessories stay in place. Choose Back to keep your current look.'
        a[name]=writecsv(rows)
    (ROOT/'assets.json').write_text(json.dumps(a,ensure_ascii=True,indent=2)+'\n')
    return a

def build(base):
    a=content(); out=ROOT/'bundles'; out.mkdir(exist_ok=True)
    with zipfile.ZipFile(base) as z: env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'))
    textures={o.read().m_Name:o for o in env.objects if o.type.name=='Texture2D'}
    texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'}
    imports=json.loads((SOURCE/'native_v49/imports49.json').read_text())
    genetic=json.loads((SOURCE/'native_v49/portrait49_genetic_catalog.json').read_text())
    catalogue=json.loads((SOURCE/'native_v49/portrait49_catalog.json').read_text())
    byid={o.path_id:o for o in env.objects if o.assets_file.name=='resources.assets'}
    names=a['a16_voltron_componentFilenames'].splitlines()
    pending={}; affected=[]
    for row in genetic+[r for r in imports['imports'] if r['kind']=='eyes']:
        if row['feature']!=1: continue
        g=['male','female'][row['gender']]
        stock=next(n[:-4] for n in names if n.startswith(f'a16_faces-{g}-stage{row["stage"]}-iris-base-'))
        iris=textures[stock].read().image.convert('RGBA')
        mode=row.get('trait',0)
        colours=(EYE_HEX[row['left']],EYE_HEX[row['right']]) if row.get('kind')=='eyes' else ('4E9ECA','D1A044') if mode==5 else ('4E9ECA','4E9ECA') if mode==12 else ('548F65','548F65') if mode==13 else ('A8C9DC','A8C9DC')
        picture=eyes(iris,*colours,mode=mode)
        obj=byid[row['texture']] if 'texture'in row else textures[row['name']]
        fingerprint=sha(picture.tobytes())
        assert obj.path_id not in pending or pending[obj.path_id][1]==fingerprint, 'shared texture requires identical pixels'
        pending[obj.path_id]=(picture,fingerprint,obj.read().m_Name)
        row['pixel_sha256']=fingerprint
        affected.append(dict(name=row['name'],path=row['path'],texture=obj.path_id,
            trait=mode,stage=row['stage'],gender=row['gender'],pixel_sha256=fingerprint))
    for ident,(picture,fingerprint,name) in pending.items():
        obj=byid[ident];tex=obj.read();tex.set_image(picture,target_format=4);tex.save()
    hashes={r['name']:r['pixel_sha256'] for r in affected}
    for rows in [imports['imports'],catalogue,genetic]:
        for r in rows:
            if r['name'] in hashes:r['pixel_sha256']=hashes[r['name']]
    for name,value in a.items():
        obj=texts[name]
        if obj.read().m_Script!=value:tx=obj.read();tx.m_Script=value;tx.save()
    raw=next(iter(env.files.values())).save(packer='original')
    path=out/'datapack.unity3d';temporary=path.with_suffix('.partial')
    with temporary.open('wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    temporary.replace(path)
    for filename,value in [('imports49.json',imports),('portrait49_catalog.json',catalogue),('portrait49_genetic_catalog.json',genetic)]:
        (ROOT/filename).write_text(json.dumps(value,indent=2)+'\n')
    report=dict(affected_resources=affected,changed_texture_ids=sorted(pending),
        all_existing_resource_paths_preserved=True,no_new_sprite_or_texture_objects=True,
        native_pupil_and_highlight_layers_preserved=True,datapack_sha256=sha(raw))
    (ROOT/'eye_import50.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(affected_resources=len(affected),changed_textures=len(pending),datapack_sha256=sha(raw))),flush=True)

if __name__=='__main__':build(sys.argv[1])
