"""Decode final bundles, resolve every added resource, retain all prior objects."""
import csv,hashlib,io,json,re,sys,zipfile
from pathlib import Path
from collections import Counter
import UnityPy
csv.field_size_limit(16*1024*1024)
ROOT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()

def validate(base):
 checks=[]
 def check(ok,label):assert ok,label;checks.append(label)
 assets=json.loads((ROOT/'assets.json').read_text());prior=json.loads((ROOT.parent/'native_v51/assets.json').read_text());info=json.loads((ROOT/'asset_build52.json').read_text())
 pack=(ROOT/'bundles/datapack.unity3d').read_bytes();data_raw=(ROOT/'bundles/data.unity3d').read_bytes()
 check(sha(pack)==info['datapack_sha256']and sha(data_raw)==info['data_sha256'],'frozen final Unity bundle hashes')
 with zipfile.ZipFile(base)as z:before=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'));beforedata=UnityPy.load(z.read('assets/bin/Data/data.unity3d'))
 after=UnityPy.load(pack);afterdata=UnityPy.load(data_raw)
 objs=lambda e:{(o.assets_file.name,o.path_id):o for o in e.objects}
 old,new=objs(before),objs(after);check(old.keys()<=new.keys(),'all previous Unity object identities retained')
 changed=[];hair={r['texture']:r for r in info['hair_changes']};text_changes=set(info['changed_text_assets']);sprites=0
 for key,obj in old.items():
  n=new[key]
  if obj.get_raw_data()!=n.get_raw_data():
   check((obj.type.name=='TextAsset'and obj.read().m_Name in text_changes)or(obj.type.name=='Texture2D'and obj.path_id in hair),'only declared text and hair pixels changed '+str(key));changed.append(key)
  if obj.type.name=='Sprite':check(obj.get_raw_data()==n.get_raw_data(),'sprite geometry and texture references retained');sprites+=1
 texts={o.read().m_Name:o.read().m_Script for o in after.objects if o.type.name=='TextAsset'}
 for k,v in assets.items():check(texts[k]==v,'authored text roundtrip '+k)
 check(prior.keys()<=assets.keys(),'all v51 text assets retained')
 oldpaths=next(o for o in beforedata.objects if o.type.name=='ResourceManager').read_typetree()['m_Container'];paths=next(o for o in afterdata.objects if o.type.name=='ResourceManager').read_typetree()['m_Container']
 enc=lambda p:Counter((k,json.dumps(v,sort_keys=True))for k,v in p)
 check(enc(oldpaths)<=enc(paths),'previous ResourceManager multiset preserved')
 bypath={p:v for p,v in paths};indices={o.path_id:o for o in after.objects if o.assets_file.name=='resources.assets'}
 for r in info['new_resources']:
  check(r['path']in bypath and bypath[r['path']]['m_PathID']==r['path_id'],'new resource path '+r['path'])
  check(indices[r['path_id']].type.name=='TextAsset'and indices[r['path_id']].read().m_Name==r['name'],'new path resolves correct TextAsset')
 for path_id,row in hair.items():
  im=indices[path_id].read().image.convert('RGBA');check(im.size==(500,500)and sha(im.tobytes())==row['pixel_sha256'],'decoded final hair pixels '+str(path_id))
 registry=assets['genesis_feature_containers'].splitlines();start=next(i for i,l in enumerate(registry)if l.startswith('ContainerId,'));header=registry[start].split(',');owners={}
 for line in registry[start+1:]:
  parts=line.split(',');check(len(parts)==16 and '"'not in line,'native delimiter grammar');r=dict(zip(header,parts));owners[r['ContainerId']]=r
  if r['EntryListID']:check(r['EntryListID']in assets,'registry list destination')
 check(owners['gameplay52']['EntryMenu']=='T4','church belongs in Activities')
 scenarios={};sheets={};inherited_shapes=[]
 for name,value in assets.items():
  if value.startswith('ScenarioID,'):
   rows=list(csv.reader(io.StringIO(value)))
   if name in text_changes:check(all(len(r)==len(rows[0])for r in rows),'complete authored scenario cells '+name)
   elif any(len(r)!=len(rows[0])for r in rows):inherited_shapes.append(name)
   if len(rows[0])==32:check(rows[0][-1]=='RandomSelection','legacy final column uses native schema')
   # Native scenario loader splits physical lines before parsing cells.
   if name in ['genesis_activities_v18','genesis_activities_v12','genesis_music_studio']:
    check(len(value.splitlines())==len(rows),'no physical multiline fields '+name)
   records=list(csv.DictReader(io.StringIO(value)));sheets[name]=records
   if name=='genesis_activities_v18':scenarios={r['ScenarioID']:r for r in records}
 for slot in range(1,25):
  r=scenarios[f'scenario.activitiesV18.contact{slot}'];check(r['Choice2_RouteTo']==f'scenario.activitiesV18.profile20_{slot}'and not r['Choice2_AdvancedLogic'],'social profile route retained')
 def walk(v):
  if isinstance(v,list):
   for x in v:walk(x)
  if isinstance(v,dict):
   for k,x in v.items():
    if k=='ListID':check(x in assets,'menu destination '+x)
    if k=='ScenarioID'and isinstance(x,str):
     last=x.split('>>')[-1]
     if last.startswith('scenario.activitiesV18.'):
      check(last in scenarios and v.get('ScenarioFile')=='genesis_activities_v18','explicit menu scenario target')
     if last.startswith('BP_SHOW_LIST='):check(last.partition('=')[2]in assets,'blueprint menu destination')
    walk(x)
 for k,v in assets.items():
  if k.startswith('genesis_v18_')and v.startswith('{'):walk(json.loads(v))
 for n in range(102):check(f'scenario.activitiesV18.nation18_{n}'in scenarios,'nation chooser retained')
 platforms=json.loads(assets['genesis_v18_platforms'])['Items'];check({'YouTube','OnlyFans','Facebook','Instagram','TikTok','Twitter','Twitch','Discord','Reddit'}<={r['Title']for r in platforms},'all nine following platforms retained')
 ordinary=json.loads(assets['genesis_v18_custom49'])['Items'];check(sum(r['Title']=='Eye colour'for r in ordinary)==1 and not any(r['Title']=='Right eye'for r in ordinary),'one ordinary eye-colour control')
 schools=[scenarios['scenario.activitiesV18.action52_'+str(i)]for i in range(1,13)]
 check(len({r['Body']for r in schools})==12 and len({r['Choice1_Text']for r in schools})==12,'twelve distinct school situations and approaches')
 for r in schools:check(all(r[f'Choice{i}_Text']for i in range(1,5)),'complete school choices including Back')
 # Exact source binding separates measured national means from simulated
 # individual spread. Confidence intervals are never used as individual SDs.
 model=json.loads((ROOT/'country_height_model52.json').read_text());check(sha((ROOT/'country_height_source.csv').read_bytes())==model['source_sha256']and model['source_countries']==200,'primary population dataset bound')
 result=dict(passed=True,checks=len(checks),cases=checks,assets=info,prior_Unity_objects=len(old),changed_prior_objects=len(changed),all_existing_Sprites_byte_identical=sprites,new_objects=len(new)-len(old),all_v51_text_assets_retained=True,inherited_unmodified_scenario_shape_variations=inherited_shapes,physical_phone_tested=False,Unity_rendering_tested=False)
 (ROOT/'content52_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=len(checks),new_objects=len(new)-len(old))),flush=True)

if __name__=='__main__':validate(sys.argv[1])
