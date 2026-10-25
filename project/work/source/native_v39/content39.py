"""Worlds and careers authored in the shipped saved Genesis format.

Bank transfers are native blueprint commands. Jobs, relatives and speculative
worlds are saved story systems; they do not replace stock engine entities.
"""
import copy,csv,hashlib,io,json,sys,zipfile
from collections import Counter
from pathlib import Path
import UnityPy
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native_v29'))
import content as d
from content import F,G,M,I,T,S,seq,logic,table,add,tile,child,menu,prop,text
OWNER='worlds39';BASE_SHA='600ec209600b2784efa024cb7a24fced71d3b34b77c499bccf1eac4b320cbc87'
p=lambda k:G(OWNER,k);m=lambda k,v:M(OWNER,k,v);i=lambda k,v=1:I(OWNER,k,v);t=lambda k,v:T(OWNER,k,v)
s=lambda k:S('w39_'+k);H='BP_SHOW_LIST=genesis_v18_worlds39';BACK=('Back to Worlds & Careers',H)
EVENTS={};FEATURES=[];MUTATIONS=[];COUNTRY=G('world20','Country')
def field(k,v=0,hi=100,lo=0,reset=False):prop(OWNER,k,v,lo,hi,reset)
def string(k,v):text(OWNER,k,v)
def page(k,title,body='',choices=(),icon='memo',stats=None):
 return add('w39_'+k,title,body,choices,icon,tables=table(**stats)if stats else None)
def cash(v):return 'BP_BANK_BALANCE='+str(v)
def cost(v,success):
 return {'cases':[{'if':{'filter':f'[finance.bankBalance<{v}]'},'then':{'route_options':[{'route_to':s('funds')}]}}],
  'else_when_no_matches':{'route_options':[{'route_to':seq(cash(F('mul',v,-1)),success)}]}}
def smarts(success,minimum=70):
 return {'cases':[{'if':{'filter':f'[hero.att_intelligence<{minimum}]'},'then':{'route_options':[{'route_to':s('prereq')}]}}],
  'else_when_no_matches':{'route_options':[{'route_to':success}]}}
def gate(success,age=18,cases=(),pending=False):
 return logic(([('(<hero:age> < '+str(age)+')',s('young'))]if age else[])+([]if pending else[(f'({p("Pending")} == 1)',s('resume'))])+list(cases),success)
def limit(prefix,success,age=18,cases=(),n=8):
 return gate(success,age,[(f'({p(prefix+"Actions")} >= {n})',s('limit'))]+list(cases))
def act(prefix,*effects,age=18,cases=(),n=8):return limit(prefix,seq(i(prefix+'Actions'),*effects),age,cases,n)
def skill(prefix,k='Skill',v=25):field(prefix+k,v)
def common(prefix):field(prefix+'Actions',0,8,reset=True);string(prefix+'Report','No chapter completed.');field(prefix+'PaidAge',-1,999,-1)
def income(prefix,amount,success,cases=(),age=18):
 return gate(seq(m(prefix+'PaidAge','<hero:age>'),cash(amount),success),age,[(f'({p(prefix+"PaidAge")} >= <hero:age>)',s('paid'))]+list(cases))
def feature(prefix,title,subtitle,icon='memo'):
 FEATURES.append(dict(prefix=prefix,title=title,subtitle=subtitle,icon=icon,home='w39_'+prefix))
def event(prefix,key,title,body,success,failure,threshold=45,price=0,age=18,cases=(),yes='Resolve this chapter',extra=()):
 """A cost and action slot commit before rolling; the cached result resumes."""
 kind=len(EVENTS)+1;EVENTS[kind]=dict(key=key,prefix=prefix,min_age=age)
 commit=seq(i(prefix+'Actions'),m('EventKind',kind),m('EventThreshold',threshold),m('Pending',1),M('careers_v18','NativeCupRoll',0),M('careers_v18','NativeCupRoll',1),m('EventRoll',G('careers_v18','Roll')),s(key))
 start=limit(prefix,cost(price,commit)if price else commit,age,cases)
 def finish(effects,report):return seq(m('Pending',0),t(prefix+'Report',report),*effects,s(prefix+'_result'))
 outcome=logic([(f'({p("EventRoll")} < {p("EventThreshold")})',finish(failure[0],failure[1]))],finish(success[0],success[1]))
 resolve=gate(outcome,age,[(f'({p("Pending")} != 1) || ({p("EventKind")} != {kind})',s(prefix))],pending=True)
 page(key,title,body+' The result is saved until you resolve this chapter.',[(yes,resolve)]+list(extra),stats={'Saved_roll':p('EventRoll')})
 return start
def result(prefix,title,icon='memo'):
 page(prefix+'_result',title,p(prefix+'Report'),[('Continue',s(prefix))],icon)
def sync():return seq(M('world20','NativeWorldSync20',0),M('world20','NativeWorldSync20',1))

def services():
 for pre,title in [('Military','Military & Special Forces'),('Police','Police & Investigations'),('Intel','Intelligence Agencies')]:
  feature(pre,title,'Training; branches; promotions; saved missions','suitcase');common(pre)
  for k,v,hi in [('Role',0,3),('Region',0,3),('Rank',0,5),('Skill',25,100),('Fitness',30,100),('Trust',50,100),('XP',0,1000),('Completed',0,10000),('Failed',0,10000)]:field(pre+k,v,hi)
  string(pre+'RoleName','No branch selected');string(pre+'RegionName','International story setting')
  locked=[(f'({p(pre+"Role")} == 0)',s(pre+'_branch'))]
  page(pre,title,'Your saved career has its own training, service record and pay. Open recruitment to select a jurisdiction.',[
   ('Recruitment & branches',seq(sync(),s(pre+'_country'))),('Training & promotion',s(pre+'_train')),('Mission desk',s(pre+'_desk')),('Service pay & record',s(pre+'_pay'))],icon='suitcase',stats={'Branch':p(pre+'RoleName'),'Rank':p(pre+'Rank'),'Skill':p(pre+'Skill'),'Trust':p(pre+'Trust'),'Completed':p(pre+'Completed')})
  page(pre+'_country','Choose the story jurisdiction','Current country: '+COUNTRY+'. Brazil, US and UK profiles are the first jurisdiction sets. This selector changes the career setting.',[
   (name,gate(seq(m(pre+'Region',n),t(pre+'RegionName',name),s(pre+'_branch')),cases=[(f'({p(pre+"Role")} != 0)',s(pre+'_branch'))]))for n,name in enumerate(['Brazil','United States','United Kingdom'],1)]+[('International profile',gate(seq(m(pre+'Region',0),t(pre+'RegionName','International story setting'),s(pre+'_branch')),cases=[(f'({p(pre+"Role")} != 0)',s(pre+'_branch'))]))],icon='earth')
  # Separate Brazil's navy from its state police. Jurisdictions are selected,
  # not falsely inferred from a city name or presented as legal hiring rules.
  choices={
   'Military':{0:['International service','Maritime special operations','Expeditionary service'],1:['Brazilian Armed Forces story','GRUMEC — Brazilian Navy','Brazilian Army special forces story'],2:['US military service story','Navy SEALs story','US special operations story'],3:['British military service story','SAS Reserve story','British maritime service story']},
   'Police':{0:['Street patrol','Criminal investigation','Special response'],1:['Polícia Militar — patrol','Polícia Civil — investigations','Rio de Janeiro elite desk'],2:['Local police — patrol','Federal investigation — FBI','US special response desk'],3:['Local police — patrol','Detective branch','Special response desk']},
   'Intel':{0:['Strategic analysis service','Diplomatic intelligence story','Research protection story'],1:['ABIN — strategic analysis','ABIN — counterintelligence story','ABIN — research protection story'],2:['CIA — foreign intelligence','CIA — analysis story','CIA — research liaison story'],3:['UK intelligence analysis story','UK diplomatic liaison story','UK research protection story']}}
  for region,names in choices[pre].items():
   page(pre+'_branches'+str(region),p(pre+'RegionName')+' branches','A first fictional progression profile. Real recruitment, citizenship, ranks and training requirements vary.',[
    (name,gate(smarts(seq(m(pre+'Role',n),t(pre+'RoleName',name),s(pre)))if pre=='Intel'else seq(m(pre+'Role',n),t(pre+'RoleName',name),s(pre)),cases=[(f'({p(pre+"Role")} != 0)',s(pre))]))for n,name in enumerate(names,1)]+[('Back',s(pre))],icon='suitcase')
  page(pre+'_branch','Recruitment desk','Select a story branch once. Skill and successful service unlock promotion.'+(' Intelligence recruitment also requires native Smarts 70.'if pre=='Intel'else''),[
   ('View available branches',gate(logic([(f'({p(pre+"Region")} == {n})',s(pre+'_branches'+str(n)))for n in [1,2,3]],s(pre+'_branches0')))),
   ('Elite police units',s(pre+'_elite')if pre=='Police'else s(pre+'_train')),('Back',s(pre))],icon='suitcase')
  if pre=='Police':
   page(pre+'_elite','Elite police desk','Brazil profiles here model Rio de Janeiro. BOPE is a Military Police unit; CORE belongs to Civil Police. US profiles distinguish local SWAT from FBI HRT.',[
    ('Rio BOPE / CORE selection',gate(logic([(f'({p(pre+"Role")} == 1)',seq(t(pre+'RoleName','BOPE — Rio Military Police story'),s(pre))),(f'({p(pre+"Role")} == 2)',seq(t(pre+'RoleName','CORE — Rio Civil Police story'),s(pre)))],s(pre+'_branch')),cases=[(f'({p(pre+"Region")} != 1) || ({p(pre+"Rank")} < 2)',s('prereq'))])),
    ('US SWAT / FBI HRT selection',gate(logic([(f'({p(pre+"Role")} == 1)',seq(t(pre+'RoleName','SWAT — local police story'),s(pre))),(f'({p(pre+"Role")} == 2)',seq(t(pre+'RoleName','FBI HRT — federal story'),s(pre)))],s(pre+'_branch')),cases=[(f'({p(pre+"Region")} != 2) || ({p(pre+"Rank")} < 2)',s('prereq'))])),('Back',s(pre))],icon='clipboard')
  page(pre+'_train','Training and progression','Each course uses one of eight service slots per age. Two successful chapters and skill 45 unlock promotion; each next rank needs more experience.',[
   ('Professional course — 1,000',limit(pre,cost(1000,seq(i(pre+'Actions'),i(pre+'Skill',10),i(pre+'Fitness',8),i(pre+'Trust',3),s(pre))),cases=locked)),
   ('Apply for promotion',gate(seq(i(pre+'Rank'),i(pre+'Trust',5),s(pre)),cases=locked+[(f'({p(pre+"Rank")} >= 5) || ({p(pre+"Skill")} < 45) || ({p(pre+"Completed")} < {F("mul",F("add",p(pre+"Rank"),1),2)})',s('prereq'))])),
   ('Study and fitness practice',act(pre,i(pre+'Skill',4),i(pre+'Fitness',6),s(pre),cases=locked)),('Back',s(pre))],icon='school')
  mission_names={'Military':['Coastal rescue mission','Civilian evacuation','Joint relief operation'],'Police':['Missing-person inquiry','Community crisis response','Organized-crime case review'],'Intel':['International crisis assessment','Undercover diplomatic story','Sensitive research review']}[pre]
  desk=[]
  for n,name in enumerate(mission_names):
   threshold=F('clamp',F('sub',65,F('div',p(pre+'Skill'),3),F('div',p(pre+'Trust'),10)),5,80)
   route=event(pre,pre+'_mission'+str(n),name,'Choose a broad story priority. Outcomes depend on training and public trust; action scenes occur offscreen.',
    ([i(pre+'Completed'),i(pre+'XP',20),i(pre+'Trust',6)],'Your team completed the chapter, protected civilians and earned a strong service review.'),
    ([i(pre+'Failed'),i(pre+'Trust',-12)],'The operation was interrupted. A public review identified setbacks, and the team returned for training.'),threshold,age=18,cases=locked+([(f'({p(pre+"Skill")} < 60)',s('prereq'))]if pre=='Intel'else[]))
   desk.append((name,route))
  page(pre+'_desk','Mission desk','Eight training or mission slots per age. Intelligence assignments require skill 60. Each mission has a persistent service outcome.',desk+[('Back',s(pre))],icon='clipboard')
  page(pre+'_pay','Service record','Collect your saved career stipend once per age after completing a mission. These story posts have no stock employer record.',[
   ('Collect annual service stipend',income(pre,F('mul',F('add',p(pre+'Rank'),1),12000),s(pre),cases=locked+[(f'({p(pre+"Completed")} < 1)',s('prereq'))])),BACK],stats={'Rank':p(pre+'Rank'),'Completed':p(pre+'Completed'),'Setbacks':p(pre+'Failed'),'Latest_chapter':p(pre+'Report')})
  result(pre,'Service review','clipboard')

def science():
 pre='Science';feature(pre,'Science & Cosmic Research','Academic; public health; space; invented forbidden projects','light-bulb');common(pre)
 for k,v,hi in [('Branch',0,4),('Knowledge',25,100),('Lab',30,100),('Containment',60,100),('Progress',0,100),('Papers',0,10000),('Discoveries',0,1000),('Prize',0,1),('Outbreaks',0,1000),('Anomalies',0,1000)]:field(pre+k,v,hi)
 string(pre+'Specialty','Physics')
 page(pre,'Science & Cosmic Research','Build knowledge, choose a research branch and complete projects. Public-health and speculative projects use abstract progress and safety meters.',[
  ('Choose branch & specialty',s(pre+'_branch')),('Laboratory & study',s(pre+'_lab')),('Project desk',s(pre+'_desk')),('Papers, awards & grants',s(pre+'_record'))],icon='light-bulb',stats={'Knowledge':p(pre+'Knowledge'),'Lab_quality':p(pre+'Lab'),'Safety':p(pre+'Containment'),'Project_progress':p(pre+'Progress'),'Discoveries':p(pre+'Discoveries')})
 page(pre+'_branch','Research branches','Native Smarts 60 qualifies you for research. Finish the current project before switching. Branch four concerns an invented star-core anomaly.',[(name,gate(smarts(seq(m(pre+'Branch',n),s(pre)),60),cases=[(f'({p(pre+"Progress")} > 0)',s('prereq'))]))for n,name in enumerate(['Academic science','Public-health research','Astrobiology & space','Forbidden star-core fiction'],1)],icon='books')
 page(pre+'_specialty','Academic specialty','Choose your project’s narrative field.',[(name,gate(seq(t(pre+'Specialty',name),s(pre))))for name in ['Organic chemistry','Marine biology','Physics']]+[('Back',s(pre))],icon='books')
 page(pre+'_lab','Laboratory and learning','Study raises knowledge. Equipment improves results; an independent safety review restores containment.',[
  ('Study a research module',act(pre,i(pre+'Knowledge',10),s(pre))),('Upgrade laboratory — 5,000',limit(pre,cost(5000,seq(i(pre+'Actions'),i(pre+'Lab',15),s(pre))),cases=[(f'({p(pre+"Lab")} >= 100)',s('prereq'))])),
  ('Safety review — 1,000',limit(pre,cost(1000,seq(i(pre+'Actions'),i(pre+'Containment',20),s(pre))),cases=[(f'({p(pre+"Containment")} >= 100)',s('prereq'))])),('Academic specialty',s(pre+'_specialty'))],icon='clipboard')
 project=event(pre,pre+'_experiment','A research milestone','Your laboratory evaluates an abstract project milestone. No laboratory procedures are supplied.',
  ([i(pre+'Progress',25),i(pre+'Papers'),i(pre+'Containment',-4)],'A peer-reviewed milestone advanced the project. Your team recorded a new paper.'),
  ([i(pre+'Progress',8),i(pre+'Containment',-18)],'A failed simulation required a pause and a safety review. The project gained a small amount of knowledge.'),
  F('clamp',F('sub',75,F('div',p(pre+'Knowledge'),3),F('div',p(pre+'Lab'),5),F('div',p(pre+'Containment'),10)),5,85),price=1500,cases=[(f'({p(pre+"Branch")} == 0) || ({p(pre+"Knowledge")} < 50) || ({p(pre+"Containment")} < 25) || ({p(pre+"Progress")} >= 100)',s('prereq'))])
 finalize=gate(logic([(f'({p(pre+"Branch")} == 2)',seq(i(pre+'Outbreaks'),i(pre+'Discoveries'),m(pre+'Progress',0),t(pre+'Report','The fictional public-health program completed its evaluation and helped the affected communities.'),s(pre+'_result'))),(f'({p(pre+"Branch")} == 3)',seq(i(pre+'Anomalies'),i(pre+'Discoveries'),m(pre+'Progress',0),t(pre+'Report','The space program catalogued an alien-world anomaly and advanced its exploration proposal.'),s(pre+'_result')))],seq(i(pre+'Discoveries'),m(pre+'Progress',0),t(pre+'Report','A major research project was completed and added to your permanent catalogue.'),s(pre+'_result'))),cases=[(f'({p(pre+"Progress")} < 100)',s('prereq'))])
 page(pre+'_desk','Research project desk','Knowledge 50, an equipped lab and safety 25 are required. Four successful milestones can finish a project.',[('Run a milestone — 1,500',project),('Submit completed project',finalize),('Alien first contact',s('Alien_contact')),('Back',s(pre))],icon='light-bulb')
 page(pre+'_record','Research catalogue','A fictional international science award requires ten papers and three discoveries. Project grants pay once per age.',[
  ('Collect project grants',income(pre,F('mul',p(pre+'Discoveries'),15000),s(pre),cases=[(f'({p(pre+"Discoveries")} < 1)',s('prereq'))])),
  ('Apply for an international science prize',gate(seq(m(pre+'Prize',1),i('Fame',25),cash(100000),s(pre)),cases=[(f'({p(pre+"Prize")} == 1) || ({p(pre+"Papers")} < 10) || ({p(pre+"Discoveries")} < 3)',s('prereq'))])),('Cybernetic projects',s('Bio')),BACK],icon='trophy',stats={'Field':p(pre+'Specialty'),'Papers':p(pre+'Papers'),'Discoveries':p(pre+'Discoveries'),'Public_health_projects':p(pre+'Outbreaks'),'Space_anomalies':p(pre+'Anomalies')})
 result(pre,'Research milestone','light-bulb')

def author():
 base=json.loads((ROOT.parent/'native_v38/assets.json').read_text());d.assets={};d.schemas={};d.rows=[];d.registry=[];EVENTS.clear();FEATURES.clear()
 for k,v,hi in [('Pending',0,1),('EventKind',0,1000),('EventRoll',0,99),('EventThreshold',0,99),('Fame',0,100),('Reputation',50,100)]:field(k,v,hi)
 for k,title,body in [('funds','Not enough money','Your balance cannot cover this purchase. No payment was taken.'),('young','Age requirement','This activity has not unlocked at your current age. Return when its stated age requirement is met.'),('limit','A full schedule','You have used this branch’s activity slots at this age. Age up to refresh them.'),('paid','Income already collected','This account has already paid you at your current age.'),('prereq','More preparation needed','Review the requirements on the branch page. This choice made no purchase or progress change.')]:page(k,title,body,[BACK])
 services();science()
 from features39 import worlds,careers,economy,legacy
 worlds(sys.modules[__name__]);careers(sys.modules[__name__]);economy(sys.modules[__name__]);legacy(sys.modules[__name__])
 page('resume','Continue your pending chapter','Finish the saved chapter before starting another activity. Its result survives closing this card or aging.',[
  ('Continue saved chapter',logic([(f'({p("Pending")} == 1) && ({p("EventKind")} == {kind})',s(info['key']))for kind,info in EVENTS.items()],H)),BACK],icon='calendar')
 menu(OWNER,'Worlds & Careers',[tile(f['title'],s(f['prefix']),f['icon'],f['subtitle'])for f in FEATURES]+[tile('Resume saved chapter',s('resume'),'calendar','Continue a chapter with a cached outcome')],entry='T2',icon='earth',sub='Expanded careers; family stories; worlds; business and sports')
 d.assets['genesis_v18_defaults_'+OWNER]=d.writecsv(list(d.schemas[OWNER].values()))
 old=list(csv.DictReader(io.StringIO(base[d.FILE])));ids={r['ScenarioID']for r in old};newids=[r['ScenarioID']for r in d.rows];assert not ids.intersection(newids)and len(newids)==len(set(newids))
 d.assets[d.FILE]=base[d.FILE]+(''if base[d.FILE].endswith('\n')else'\r\n')+d.writecsv(d.rows,d.HEADER).split('\r\n',1)[1]
 registry=io.StringIO(newline='');csv.writer(registry,lineterminator='\r\n').writerows(d.registry)
 d.assets['genesis_feature_containers']=base['genesis_feature_containers']+(''if base['genesis_feature_containers'].endswith('\n')else'\r\n')+registry.getvalue()
 community=json.loads(base['genesis_v18_community35']);entry=child('Worlds & Careers',OWNER,'earth','Careers; supernatural worlds; relatives; corporations and national sports');entry['TileID']='worlds39_entry';community['Items'].append(entry);d.assets['genesis_v18_community35']=json.dumps(community,indent=2)
 assets={**base,**d.assets};(ROOT/'assets.json').write_text(json.dumps(assets,indent=2)+'\n');(ROOT/'schemas39.json').write_text(json.dumps(d.schemas,indent=2)+'\n')
 report=dict(new_scenarios=len(d.rows),new_assets=[n for n in d.assets if n not in base],modified_assets=[n for n in d.assets if n in base],owner=OWNER,new_saved_properties=len(d.schemas[OWNER]),features=FEATURES,cached_events=EVENTS,stock_entities_unchanged=True)
 (ROOT/'authoring39.json').write_text(json.dumps(report,indent=2)+'\n');return assets,report

def build(base,out):
 assert hashlib.sha256(Path(base).read_bytes()).hexdigest()==BASE_SHA
 assets,report=author();out=Path(out);out.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(base)as z:env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'));data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'))
 key=lambda o:(o.assets_file.name,o.path_id);sha=lambda b:hashlib.sha256(b).hexdigest()
 snapshots={key(o):sha(o.get_raw_data())for o in env.objects};snapshot_data={key(o):sha(o.get_raw_data())for o in data.objects}
 texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'};rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree();paths=copy.deepcopy(tree['m_Container']);deps=copy.deepcopy(tree['m_DependentAssets'])
 resource_id=next(n+1 for n,e in enumerate(rm.assets_file.externals)if e.path=='resources.assets');file=texts[d.FILE].assets_file;next_id=max(file.objects)+1;changed=set();added={};baseline=json.loads((ROOT.parent/'native_v38/assets.json').read_text())
 for name,value in baseline.items():assert texts[name].read().m_Script==value,name
 for name,value in assets.items():
  if name in baseline and value==baseline[name]:continue
  if name in texts:obj=texts[name];changed.add(key(obj))
  else:
   obj=copy.copy(texts['genesis_test_feature_events']);obj.path_id=next_id;next_id+=1;obj.data=texts['genesis_test_feature_events'].get_raw_data();file.objects[obj.path_id]=obj;added[name]=obj.path_id
   path=('genesis_lists/'if value.startswith('{')else'genesis/')+name;assert path not in dict(tree['m_Container']);tree['m_Container'].append((path,dict(m_FileID=resource_id,m_PathID=obj.path_id)))
  asset=obj.read();asset.m_Name=name;asset.m_Script=value;asset.save()
 tree['m_Container'].sort(key=lambda x:x[0]);rm.save_typetree(tree);bundle=next(iter(env.files.values())).save(packer='original');data_bytes=next(iter(data.files.values())).save(packer='original');(out/'datapack.unity3d').write_bytes(bundle);(out/'data.unity3d').write_bytes(data_bytes)
 after_env=UnityPy.load(bundle);after_data=UnityPy.load(data_bytes);after={key(o):sha(o.get_raw_data())for o in after_env.objects};after_d={key(o):sha(o.get_raw_data())for o in after_data.objects}
 assert set(snapshots)<=set(after)and len(after)==len(snapshots)+len(added);assert{k for k in snapshots if snapshots[k]!=after[k]}==changed;assert set(after_d)==set(snapshot_data)and{k for k in snapshot_data if snapshot_data[k]!=after_d[k]}=={key(rm)}
 reread=next(o for o in after_data.objects if o.type.name=='ResourceManager').read_typetree();assert Counter((k,json.dumps(v,sort_keys=True))for k,v in paths)<=Counter((k,json.dumps(v,sort_keys=True))for k,v in reread['m_Container']);assert reread['m_DependentAssets']==deps
 for name,pathid in added.items():assert dict(reread['m_Container'])[('genesis_lists/'if assets[name].startswith('{')else'genesis/')+name]==dict(m_FileID=resource_id,m_PathID=pathid)
 values={o.read().m_Name:o.read().m_Script for o in after_env.objects if o.type.name=='TextAsset'};assert all(values[n]==v for n,v in assets.items());assert list(csv.DictReader(io.StringIO(baseline[d.FILE])))==list(csv.DictReader(io.StringIO(values[d.FILE])))[:len(list(csv.DictReader(io.StringIO(baseline[d.FILE]))))]
 report.update(passed=True,datapack_sha256=sha(bundle),data_sha256=sha(data_bytes),assets_sha256=sha((ROOT/'assets.json').read_bytes()),added_TextAssets=added,modified_TextAssets=len(changed),all_other_Unity_objects_byte_identical=True,all_original_resource_paths_preserved=True,all_original_scenario_rows_preserved=True,physical_device_tested=False,Unity_rendering_modeled=True)
 (ROOT/'content39_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['passed','new_scenarios','new_saved_properties','modified_TextAssets','added_TextAssets','assets_sha256']}),flush=True)
if __name__=='__main__':build(*sys.argv[1:])
