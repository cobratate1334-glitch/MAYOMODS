"""Repair native CSV framing and put expansion entries in their real menus."""
import csv,io,json,sys,hashlib,zipfile
from pathlib import Path
import UnityPy
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(SOURCE),str(SOURCE/'native_v29')]
from native_v45.assets45 import codec
from native_v29.content import writecsv
def author():
 a=json.loads((SOURCE/'native_v45/assets.json').read_text());decode,encode=codec()
 original44=json.loads((SOURCE/'native_v44/assets.json').read_text())
 for key in ['genesis_activities_v18','genesis_activities_v12']:
  # v45 replaced prose inside already serialized CSV; newly inserted commas
  # shifted the calendar row into the choice columns. Rebuild that whole row.
  old=next(r for r in csv.DictReader(io.StringIO(original44[key]))if r['ScenarioID']=='scenario.activitiesV18.era44_calendar')
  old['Body']='The calendar advances with your character’s age. Choose a starting year in New Life. It changes accessory collections, vehicle stock, house styles and social platforms.'
  rows=list(csv.DictReader(io.StringIO(a[key])))
  rows=[old if r['ScenarioID']==old['ScenarioID']else r for r in rows]
  assert all(None not in r for r in rows)
  item=next(r for r in rows if r['ScenarioID']=='scenario.activitiesV18.era44_item')
  for n in range(1,28):
   alias=dict(item);alias['ScenarioID']='scenario.activitiesV18.era46_item_'+str(n);rows.append(alias)
  a[key]=writecsv(rows)
 # List actions open exact scenario IDs. Selection is applied by the native
 # ScenarioBase load hook, so no blueprint chain can swallow an item click.
 import re
 for key,value in list(a.items()):
  if not key.startswith('genesis_v18_era44')or not value.startswith('{'):continue
  def rewrite(v):
   if isinstance(v,dict):
    for field,text in list(v.items()):
     if field=='ScenarioID'and isinstance(text,str):
      match=re.search(r'Action:=(10[1-9]|11\d|12[0-7])>>scenario\.activitiesV18\.era44_item$',text)
      if match:v[field]='scenario.activitiesV18.era46_item_'+str(int(match[1])-100)
      elif text.endswith('scenario.activitiesV18.era44_home'):v[field]='scenario.activitiesV18.era44_home'
      elif text.endswith('scenario.activitiesV18.era44_wardrobe'):v[field]='scenario.activitiesV18.era44_wardrobe'
     else:rewrite(text)
   elif isinstance(v,list):
    for item in v:rewrite(item)
  doc=json.loads(value);rewrite(doc);a[key]=json.dumps(doc,indent=2)
 for k in ['a16_car-models-enc','a16_house-types-enc']:
  text=decode(a[k]);rr=list(csv.DictReader(io.StringIO(text)))
  # The game splits on LF without removing empty entries. No final blank row.
  fixed=writecsv(rr);assert not fixed.endswith(('\r','\n'))
  assert len(fixed.split('\n'))==len(rr)+1
  a[k]=encode(fixed);(ROOT/(k.replace('-enc','')+'.csv')).write_bytes(fixed.encode())
 text=a['genesis_feature_containers'];lines=text.splitlines();i=next(n for n,l in enumerate(lines)if l.startswith('ContainerId,'))
 rr=list(csv.DictReader(io.StringIO('\n'.join(lines[i:]))))
 for r in rr:
  owner=r['ContainerId']
  if r['EntryMenu']=='T2':
   r['EntryMenu']='T3' if owner=='social_v18' else 'Shopping' if owner=='era44' else 'T4'
  if owner=='era44':r['EntrySecondLine']='Era collections, vintage finds and your wardrobe'
 a['genesis_feature_containers']='\r\n'.join(lines[:i])+'\r\n'+writecsv(rr)
 # Keep the dealer one native shopping entry, and collect optional story hubs.
 groups=['community35','stalker38','worlds39']
 for r in rr:
  if r['ContainerId']in groups:r['EntryMenu']='Expansions46'
 rr.append(dict(zip(rr[0],['expansions46','Expansions','','genesis_v18_defaults_expansions46','','content','','','T4','Expansions','index-cards','Community, worlds and saved stories','0','genesis_v18_expansions46','',''])))
 a['genesis_feature_containers']='\r\n'.join(lines[:i])+'\r\n'+writecsv(rr)
 items=[]
 for owner in groups:
  r=next(x for x in rr if x['ContainerId']==owner)
  items.append(dict(Title=r['EntryLabel'],Icon=r['EntryEmoji'],SecondLine=r['EntrySecondLine'],TileID='v46_'+owner,ActionList=[dict(Index=0,ConditionList=[dict(ListID=r['EntryListID'])])]))
 a['genesis_v18_expansions46']=json.dumps(dict(ListID='genesis_v18_expansions46',Title='EXPANSIONS',PresentationMode='Normal',Items=items),indent=2)
 a['genesis_v18_defaults_expansions46']='key,type,value,reset_on_ageup,minimum,maximum\r\nEnabled,int,1,,0,1'
 (ROOT/'assets.json').write_text(json.dumps(a,ensure_ascii=True,indent=2)+'\n')
 schemas=json.loads((SOURCE/'native_v45/schemas.json').read_text());schemas['expansions46']={'Enabled':dict(key='Enabled',type='int',value=1,reset_on_ageup='',minimum=0,maximum=1)}
 (ROOT/'schemas.json').write_text(json.dumps(schemas,indent=2)+'\n')
 return a
def build(base,out):
 a=author();out=Path(out);out.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(base)as z:
  env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'));data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'))
 sha=lambda b:hashlib.sha256(b).hexdigest();key=lambda o:(o.assets_file.name,o.path_id)
 before={key(o):sha(o.get_raw_data())for o in env.objects};beforedata={key(o):sha(o.get_raw_data())for o in data.objects}
 texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'}
 rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree();original=list(tree['m_Container'])
 rid=next(n+1 for n,e in enumerate(rm.assets_file.externals)if e.path=='resources.assets')
 file=texts['genesis_activities_v18'].assets_file;nextid=max(file.objects)+1;changed=set();added=[]
 import copy
 for name,value in a.items():
  if name in texts and texts[name].read().m_Script==value:continue
  if name in texts:obj=texts[name];changed.add(key(obj))
  else:
   obj=copy.copy(texts['genesis_test_feature_events']);obj.path_id=nextid;nextid+=1;obj.data=obj.get_raw_data();file.objects[obj.path_id]=obj;added.append(name)
   path=('genesis_lists/'if value.startswith('{')else'genesis/')+name
   assert path not in dict(tree['m_Container']);tree['m_Container'].append((path,dict(m_FileID=rid,m_PathID=obj.path_id)))
  v=obj.read();v.m_Name=name;v.m_Script=value;v.save()
 tree['m_Container'].sort(key=lambda x:x[0]);rm.save_typetree(tree)
 bundle=next(iter(env.files.values())).save(packer='original');db=next(iter(data.files.values())).save(packer='original')
 (out/'datapack.unity3d').write_bytes(bundle);(out/'data.unity3d').write_bytes(db)
 ae=UnityPy.load(bundle);ad=UnityPy.load(db)
 after={key(o):sha(o.get_raw_data())for o in ae.objects};afterdata={key(o):sha(o.get_raw_data())for o in ad.objects}
 assert set(before)<=set(after)and{k for k in before if before[k]!=after[k]}==changed
 assert set(beforedata)==set(afterdata)and{k for k in beforedata if beforedata[k]!=afterdata[k]}=={key(rm)}
 rt=next(o for o in ad.objects if o.type.name=='ResourceManager').read_typetree()
 assert all(x in rt['m_Container']for x in original)
 vals={o.read().m_Name:o.read().m_Script for o in ae.objects if o.type.name=='TextAsset'};assert all(vals[k]==v for k,v in a.items())
 report=dict(passed=True,modified_TextAssets=len(changed),added_TextAssets=added,unedited_Unity_objects_preserved=True,existing_resource_paths_preserved=True,datapack_sha256=sha(bundle),data_sha256=sha(db))
 (ROOT/'assets46_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':build(*sys.argv[1:])
