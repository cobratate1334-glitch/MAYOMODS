"""Append country selection scenes and improve profile prose in existing assets."""
import copy,csv,hashlib,io,json,sys,zipfile
from pathlib import Path
import UnityPy
ROOT=Path(__file__).resolve().parent

def csv_text(rows,fields):
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=fields,lineterminator='\r\n');writer.writeheader();writer.writerows(rows);return out.getvalue()

def author():
    assets=json.loads((ROOT.parent/'native_v33/assets.json').read_text())
    nations=json.loads((ROOT/'countries34.json').read_text())['nations']
    rr=list(csv.DictReader(io.StringIO(assets['genesis_activities_v18'])));fields=list(rr[0]);byid={r['ScenarioID']:r for r in rr}
    prototype=byid['scenario.activitiesV18.nation18_0'];menu=json.loads(assets['genesis_v18_nations18'])
    for i,(name,flag)in enumerate(nations):
        key=f'scenario.activitiesV18.nation18_{i}'
        if key not in byid:
            row=copy.deepcopy(prototype);row.update(ScenarioID=key,Title=name,EmojiString=flag,Choice1_Text='Represent '+name,
                Choice1_RouteTo=f'BP_GFC_MODIFY_PROPERTY=soccer_v12:CountryChosen:=1>>BP_GFC_MODIFY_PROPERTY=soccer_v12:CountryPool:={i}>>BP_GFC_SET_STRING=soccer_v12:CountryName:{name}>>BP_GFC_SET_STRING=soccer_v12:CountryFlag:{flag}>>BP_SHOW_LIST=genesis_v9_v12_soccer')
            rr.append(row)
            tile=copy.deepcopy(menu['Items'][0]);tile.update(Title=name,Icon=flag,TileID=f'v18_nations18_{i}')
            tile['ActionList'][0]['ConditionList'][0]['ScenarioID']=key;menu['Items'].append(tile)
    for suffix in ['person_story21','friend_story21']:
        row=byid['scenario.activitiesV18.'+suffix]
        row['Body']='Personality: <GFC.relationship21.Personality>. Interests: <GFC.relationship21.Hobby>. Goals: <GFC.relationship21.Ambition>. <GFC.relationship21.Story>'
    assets['genesis_activities_v18']=csv_text(rr,fields)
    assets['genesis_v18_nations18']=json.dumps(menu,indent=2,ensure_ascii=False)
    name='genesis_v12_defaults_soccer_v12';defaults=list(csv.DictReader(io.StringIO(assets[name])))
    for row in defaults:
        if row['key']in ['CountryPool','TeamPool','CurrentOpponentID','T1ID','T2ID','T3ID']:
            row['maximum']=str(max(101,int(row.get('maximum')or 0)))
    assets[name]=csv_text(defaults,list(defaults[0]))
    assert len(menu['Items'])==102 and len({i['Title']for i in menu['Items']})==102
    assert all(byid[f'scenario.activitiesV18.nation18_{i}']['Title']==name for i,(name,flag)in enumerate(nations[:63]))
    (ROOT/'assets.json').write_text(json.dumps(assets,indent=2)+'\n')
    return assets

def build(base,out):
    assets=author();entry='assets/bin/Data/datapack.unity3d'
    with zipfile.ZipFile(base)as z:before=z.read(entry)
    env=UnityPy.load(before)
    key=lambda o:(o.assets_file.name,o.path_id)
    sha=lambda b:hashlib.sha256(b).hexdigest()
    snapshots={key(o):sha(o.get_raw_data())for o in env.objects}
    targets={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'}
    changed_names=['genesis_activities_v18','genesis_v18_nations18','genesis_v12_defaults_soccer_v12']
    changed_ids=set()
    for name in changed_names:
        obj=targets[name];value=obj.read();value.m_Script=assets[name];value.save();changed_ids.add(key(obj))
    result=next(iter(env.files.values())).save(packer='original');Path(out).write_bytes(result)
    check=UnityPy.load(result);after={key(o):sha(o.get_raw_data())for o in check.objects}
    assert set(after)==set(snapshots)
    actual={k for k in snapshots if snapshots[k]!=after[k]};assert actual==changed_ids
    text_check={o.read().m_Name:o.read().m_Script for o in check.objects if o.type.name=='TextAsset'and o.read().m_Name in changed_names}
    assert all(text_check[n]==assets[n]for n in changed_names)
    report=dict(passed=True,sha256=sha(result),modified_TextAssets=changed_names,
        preserved_object_count=len(snapshots)-len(actual),all_other_Unity_objects_byte_identical=True,
        existing_63_country_IDs_preserved=True,game_country_count=102,added_country_count=39)
    (ROOT/'content34_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

if __name__=='__main__':build(*sys.argv[1:])
