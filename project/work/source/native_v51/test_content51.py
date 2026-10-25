"""Verify the final Unity bundle and every affected native registry/menu route."""
import csv,hashlib,io,json,sys,zipfile
from pathlib import Path
import UnityPy
ROOT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def validate(base):
    checks=0
    def check(ok,label):
        nonlocal checks
        assert ok,label;checks+=1
    a=json.loads((ROOT/'assets.json').read_text());before=json.loads((ROOT.parent/'native_v50/assets.json').read_text())
    info=json.loads((ROOT/'asset_build51.json').read_text());raw=(ROOT/'bundles/datapack.unity3d').read_bytes()
    check(sha(raw)==info['datapack_sha256'],'frozen Unity bundle')
    with zipfile.ZipFile(base)as z:old=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'));data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'))
    new=UnityPy.load(raw)
    objs=lambda env:{(o.assets_file.name,o.path_id):o for o in env.objects}
    original,final=objs(old),objs(new);check(original.keys()==final.keys(),'all Unity objects retained')
    changed=[]
    for key,obj in original.items():
        if obj.get_raw_data()!=final[key].get_raw_data():
            check(obj.type.name=='TextAsset','only TextAssets changed')
            changed.append(obj.read().m_Name)
        else:checks+=1
    check(set(changed)==set(info['changed_text_assets']),'exact authored TextAsset changes')
    texts={o.read().m_Name:o.read().m_Script for o in new.objects if o.type.name=='TextAsset'}
    for name,value in a.items():check(texts[name]==value,'TextAsset roundtrip '+name)
    paths={p for p,_ in next(o for o in data.objects if o.type.name=='ResourceManager').read_typetree()['m_Container']}
    registry=a['genesis_feature_containers'].splitlines();registry=registry[next(i for i,s in enumerate(registry)if s.startswith('ContainerId,')):]
    headers=registry[0].split(',');owners={}
    for line in registry[1:]:
        row=dict(zip(headers,line.split(',')));owners[row['ContainerId']]=row
        check(len(line.split(','))==16 and '"'not in line,'native registry grammar '+row['ContainerId'])
        if row['EntryListID']:check(row['EntryListID']in a,'registry destination '+row['ContainerId'])
    check(owners['expansions46']['EntryListID']=='genesis_v18_expansions46','Expansions hub destination')
    check(owners['expansions46']['EntryMenu']=='T4','existing Activities entry retained')
    check(len(a)==len(before)and a.keys()==before.keys(),'no new menu or resource assets')
    current={r['ScenarioID']:r for r in csv.DictReader(io.StringIO(a['genesis_activities_v18']))}
    for slot in range(1,25):
        sid=f'scenario.activitiesV18.contact{slot}';r=current[sid]
        check(r['Choice2_RouteTo']==f'scenario.activitiesV18.profile20_{slot}'and not r['Choice2_AdvancedLogic'],'social story action '+str(slot))
    direct=0;chains=0
    def walk(value):
        nonlocal direct,chains
        if isinstance(value,list):
            for item in value:walk(item)
        elif isinstance(value,dict):
            for key,v in value.items():
                if key=='ListID':check(v in a,'nested list destination '+str(v))
                elif key=='ScenarioID'and isinstance(v,str):
                    end=v.split('>>')[-1]
                    if end.startswith('scenario.activitiesV18.'):
                        check(end in current,'menu scenario destination '+end)
                        check(value.get('ScenarioFile')=='genesis_activities_v18','explicit current scenario resource')
                        direct+=int(v==end);chains+=int(v!=end)
                    elif end.startswith('BP_SHOW_LIST='):check(end.partition('=')[2]in a,'blueprint list destination')
                walk(v)
    for name in a:
        if name.startswith('genesis_v18_')and a[name].startswith('{'):walk(json.loads(a[name]))
    for code in [1,2,3,4,5,6,10,11]+list(range(101,125))+list(range(201,219))+[401,402,407,409,410]:
        check(f'scenario.activitiesV18.comments47_{code:03}'in current,'comment lifecycle scenario '+str(code))
    # Every authored change is bounded; all graphics, events and custom
    # themes outside the four declared sheets are byte-for-byte retained.
    for name in a:
        if name not in changed:check(a[name]==before[name],'prior content retained '+name)
    result=dict(passed=True,checks=checks,assets=info,unchanged_Unity_objects=len(original)-len(changed),
        changed_TextAssets=changed,direct_menu_scenarios=direct,blueprint_menu_chains=chains,
        comments_and_social_routes_present=True,no_new_tabs=True,
        all_v50_portrait_pixels_and_resource_ids_identical=True,physical_phone_tested=False)
    (ROOT/'content51_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=checks,unchanged_Unity_objects=result['unchanged_Unity_objects'])))
if __name__=='__main__':validate(sys.argv[1])
