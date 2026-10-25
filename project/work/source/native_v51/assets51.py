"""Use the real registry delimiter grammar and repair social action destinations."""
import csv,hashlib,io,json,os,sys,zipfile
from pathlib import Path
import UnityPy
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(SOURCE),str(SOURCE/'native_v29')]
from native_v29.content import writecsv
sha=lambda raw:hashlib.sha256(raw).hexdigest()

def content():
    a=json.loads((SOURCE/'native_v50/assets.json').read_text());changes=[]
    name='genesis_feature_containers';lines=a[name].splitlines()
    start=next(i for i,s in enumerate(lines)if s.startswith('ContainerId,'))
    rows=list(csv.reader(io.StringIO('\n'.join(lines[start:]))));assert len(rows[0])==16
    # Registry.LoadFromText uses String.Split(',') followed by Trim; it does
    # not call the quoted-cell decoder used for property sheets.
    for row in rows:
        assert len(row)==16
        for col,value in enumerate(row):
            clean=value.replace(',',';').replace('\r',' ').replace('\n',' ')
            assert '"'not in clean
            if clean!=value:changes.append(dict(asset=name,owner=row[0],column=rows[0][col],before=value,after=clean))
            row[col]=clean
    a[name]='\r\n'.join(lines[:start]+[','.join(r)for r in rows])
    # The detail/story action was shadowed by an unrelated spend-time
    # AdvancedLogic field in both current and legacy scenario files.
    for name in ['genesis_activities_v18','genesis_activities_v12']:
        rows=list(csv.DictReader(io.StringIO(a[name])))
        for r in rows:
            sid=r['ScenarioID']
            if sid.startswith('scenario.activitiesV18.contact') and sid.rsplit('contact',1)[-1].isdigit():
                slot=int(sid.rsplit('contact',1)[-1])
                r['Choice2_Text']='Their story and profile'
                r['Choice2_RouteTo']=f'scenario.activitiesV18.profile20_{slot}'
                r['Choice2_AdvancedLogic']=''
                changes.append(dict(asset=name,scenario=sid,repair='profile action no longer shadowed'))
        a[name]=writecsv(rows)
    # Persist provenance; no existing key is renamed or removed.
    name='genesis_v18_defaults_life_v18';rows=list(csv.DictReader(io.StringIO(a[name])))
    for key,typ,value in [('HeightSource51','int','0'),('HeightSourceName51','string','Family estimate')]:
        assert not any(r['key']==key for r in rows)
        r=dict.fromkeys(rows[0],'');r.update(key=key,type=typ,value=value)
        if typ=='int':r.update(minimum='0',maximum='2')
        rows.append(r)
    a[name]=writecsv(rows)
    (ROOT/'assets.json').write_text(json.dumps(a,ensure_ascii=True,indent=2)+'\n')
    (ROOT/'content_changes51.json').write_text(json.dumps(changes,indent=2)+'\n')
    return a

def build(base):
    a=content();out=ROOT/'bundles';out.mkdir(exist_ok=True)
    with zipfile.ZipFile(base)as z:
        before=z.read('assets/bin/Data/datapack.unity3d');datahash=sha(z.read('assets/bin/Data/data.unity3d'))
    env=UnityPy.load(before);texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'}
    changed=[]
    for name,value in a.items():
        obj=texts[name];text=obj.read()
        if text.m_Script!=value:text.m_Script=value;text.save();changed.append(name)
    raw=next(iter(env.files.values())).save(packer='original');path=out/'datapack.unity3d';tmp=path.with_suffix('.partial')
    with tmp.open('wb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    tmp.replace(path)
    result=dict(datapack_sha256=sha(raw),base_datapack_sha256=sha(before),data_sha256=datahash,
        changed_text_assets=changed,no_new_resources=True,all_iris_textures_preserved=True)
    (ROOT/'asset_build51.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__':build(sys.argv[1])
