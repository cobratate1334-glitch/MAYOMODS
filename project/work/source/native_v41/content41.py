"""Repair legacy entry routes and add decisions inside the existing prison tab."""
import copy,csv,hashlib,io,json,sys,zipfile
from collections import Counter
from pathlib import Path
import UnityPy
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native_v29'))
import content as d
from content import G,M,I,T,S,seq,logic,table,add,tile
from native_v40.content40 import filt,choices
BASE_SHA='847d39d1fd4ff6fa63101638bf8b8b9c8436289e3ad39ce235d173bc9cb8fabb'
REHAB='BP_SHOW_LIST=genesis_v7_prison';PAROLE='BP_SHOW_LIST=genesis_v9_v11_parole_v11'
p=lambda k:G('prison_plus_v7',k);q=lambda k:G('parole_v11',k);s=lambda k:S('w41_'+k)
PSYNC=seq(M('parole_v11','NativeParoleSync41',0),M('parole_v11','NativeParoleSync41',1))
SYNC=seq(M('prison_plus_v7','NativePrisonSync',0),M('prison_plus_v7','NativePrisonSync',1))
WSYNC=seq(M('worlds39','NativeSync40',0),M('worlds39','NativeSync40',1))
def pulse(owner,key,value=1):return seq(M(owner,key,0),M(owner,key,value))
def page(k,title,body,cs,icon='clipboard',stats=None,dismiss=True):return add('w41_'+k,title,body,cs,icon,tables=table(**stats)if stats else None,dismiss=dismiss)
def prison(dest):return filt('[!hero.inPrison]',s('released'),dest)
def parole(dest):return logic([(f'({q("Active")} != 1)',s('parole_locked'))],dest)

def author():
 base=json.loads((ROOT.parent/'native_v40/assets.json').read_text());allbase=json.loads(Path('analysis/base_assets.json').read_text());allbase.update(base)
 assets=copy.deepcopy(base);d.assets={};d.rows=[];d.schemas={};d.registry=[]
 page('released','Prison activities unavailable','Your character is out of prison. Rehabilitation sessions cannot change a released character’s prison conduct.',[('Parole status',seq(PSYNC,s('parole_status'))),('Back to game','')],icon='memo')
 page('case','Case File & Rehabilitation','This record reads your current prison sentence and conduct. Use the normal library, exercise, appeal and parole-board screens, or work through a rehabilitation programme. Six programme sessions are available each age.',[
  ('Choose a rehabilitation programme',prison(REHAB)),('Appeal the actual sentence',prison(M('worlds39','NativePrisonAppeal40',1))),('Parole board',prison(s('parole_prep'))),('Back to rehabilitation',REHAB)],icon='ball-chain',stats={'Years_remaining':p('YearsRemaining'),'Actual_conduct':p('NativeBehavior'),'Education_progress':p('Education'),'Rehabilitation':p('Rehabilitation'),'Family_support':p('Support'),'Sessions_this_age':p('WorkUsed')})
 page('limit','Your programme schedule is full','You have completed six rehabilitation sessions at this age. Age up to continue. Your record, legal appeal, library and exercise remain available.',[('Read case file',seq(SYNC,s('case'))),('Back',REHAB)],icon='calendar')
 def session(dest):return prison(logic([(f'({p("WorkUsed")} >= 6)',s('limit'))],dest))
 def finish(kind,education=0,rehab=0,support=0,conduct=1):
  effects=[I('prison_plus_v7','WorkUsed'),T('prison_plus_v7','Report41',kind)]
  for key,value in [('Education',education),('Rehabilitation',rehab),('Support',support)]:
   if value:effects.append(I('prison_plus_v7',key,value))
  if conduct:effects.append(pulse('worlds39','NativePrisonConduct40',conduct))
  return session(seq(*effects,SYNC,s('result')))
 page('result','Programme session completed',p('Report41'),[('Review your record',seq(SYNC,s('case'))),('Choose another programme',REHAB)],stats={'Actual_conduct':p('NativeBehavior'),'Education':p('Education'),'Rehabilitation':p('Rehabilitation'),'Family_support':p('Support'),'Sessions_this_age':p('WorkUsed')})
 page('vocational','Vocational workshop','Choose a practical learning project for your release portfolio. Completing a session records skills and improves your actual prison conduct.',[
  ('Practice repair and maintenance',session(s('vocational_repair'))),('Plan a small catering service',session(s('vocational_catering'))),('Review a completed portfolio',prison(logic([(f'({p("Education")} < 60) || ({p("LastCertAge")} >= <hero:age>)',s('portfolio_wait'))],seq(M('prison_plus_v7','LastCertAge','<hero:age>'),I('prison_plus_v7','Certifications'),s('portfolio'))))),('Back',REHAB)],icon='tools')
 page('vocational_repair','Workshop assignment','A repair estimate has missing materials. Your supervisor asks how you will finish the project.',[('Check the plan and request the missing items',finish('You completed a carefully checked maintenance project. Your skills portfolio and prison conduct improved.',education=10,rehab=4)),('Ask a peer to review your estimate',finish('You learned from a peer review and completed the project together.',education=7,support=5)),('Back',REHAB)],icon='tools')
 page('vocational_catering','Catering assignment','Your planned menu is over budget. Revise the plan before presenting it.',[('Simplify the menu and check costs',finish('You prepared a workable catering plan and added it to your skills portfolio.',education=10)),('Work with the class on a revised plan',finish('Your group completed a realistic catering plan.',education=7,rehab=5)),('Back',REHAB)],icon='school')
 page('portfolio_wait','Portfolio review requirements','Reach education progress 60. A portfolio can be reviewed once per age. Programme portfolios are saved separately from the game’s formal degrees.',[('Back',REHAB)],icon='memo')
 page('portfolio','Portfolio reviewed','Your learning portfolio has been recorded for your release plan. Continue your education through the game’s normal school and job systems after release.',[('Back',REHAB)],icon='clipboard',stats={'Portfolios_completed':p('Certifications')})
 for key,title,body,actions in [
  ('counselling','Counselling session','A difficult memory is affecting your routine. Choose a focus for this session.', [('Discuss triggers and ask for support',dict(rehab=10)),('Practice a calm response to frustration',dict(rehab=7,support=4))]),
  ('mediation','Supervised mediation','Another participant disagrees with your account. The facilitator asks you to choose your next response.', [('Listen and acknowledge their concerns',dict(rehab=8,support=8)),('Request a pause and a guided conversation',dict(rehab=6,support=6))]),
  ('work','Work programme','Your assigned team is behind schedule. Choose how you will help.', [('Organise tasks with your supervisor',dict(education=6,rehab=7)),('Support a teammate who needs training',dict(education=4,support=8))]),
  ('family','Family support plan','Plan a constructive conversation for your next contact with family. This programme improves your support plan; actual relatives remain in Relationships.', [('Talk about rebuilding trust over time',dict(rehab=5,support=10)),('Prepare an education and employment plan',dict(education=5,support=8))])]:
  page(key,title,body,[(label,finish('You completed '+title.lower()+'. Your programme record and actual prison conduct improved.',**eff))for label,eff in actions]+[('Back',REHAB)],icon='handshake')
 page('parole_prep','Parole preparation','The board uses the game’s normal questions and release decision. Good conduct helps, but release is not guaranteed. A successful release unlocks supervision: check in once at each age before aging again. Missing a check-in issues a warrant.',[
  ('Attend the normal parole board',prison(s('parole_board_gate'))),('Review conduct and sentence',seq(SYNC,s('case'))),('Back',REHAB)],icon='clipboard')
 page('parole_board_gate','Parole board availability','Availability follows the game’s sentence length, years remaining, conduct and country rules. Death-row and life-sentence prisoners cannot use this board.',[
  ('Check eligibility and attend',prison(seq(pulse('worlds39','NativePrisonParole41'),s('board_not_ready')))),('Back',REHAB)],icon='balance-scale')
 page('board_not_ready','Parole board not yet available','Your current sentence, remaining time, conduct or country rules do not qualify for the normal board, or you have already attended at this age. Continue serving your sentence and improving conduct.',[('Back to rehabilitation',REHAB)],icon='clipboard')
 # The original list identity is retained so existing menu links and saves work.
 items=[tile('Current case file',seq(SYNC,s('case')),'clipboard','Actual sentence and conduct'),tile('Vocational workshop',s('vocational'),'tools','Projects and a release skills portfolio'),tile('Education & library',prison(M('worlds39','NativePrisonLibrary40',1)),'books','The game’s normal prison library'),tile('Counselling',s('counselling'),'handshake','Guided decisions and actual conduct'),tile('Supervised mediation',s('mediation'),'handshake','Resolve disagreements constructively'),tile('Work programme',s('work'),'suitcase','Teamwork and learning'),tile('Family support plan',s('family'),'family','Prepare for life after release'),tile('Exercise',prison(M('worlds39','NativePrisonWorkout40',1)),'man-lifting-weights','The game’s normal prison workout'),tile('Parole preparation',s('parole_prep'),'clipboard','Normal board and supervision rules')]
 for n,item in enumerate(items):item['TileID']='v41_rehab_'+str(n)
 assets['genesis_v7_prison']=json.dumps(dict(ListID='genesis_v7_prison',Title='CASE FILE & REHABILITATION',PresentationMode='Normal',Items=items),indent=2)
 page('parole_locked','Parole & House Arrest locked','This menu unlocks after a successful release from the game’s parole board. It is unavailable while you are in prison or after supervision ends.',[('Back to game','')],icon='house')
 page('parole_status','Parole & House Arrest','Check in once at your current age before tapping Age Up. Missing that check-in issues a warrant at the next age, including the last year of supervision. Home sessions are optional. A late check-in cannot clear a warrant: resolve it through the officer and the normal arrest/court process.',[
  ('Check in with your parole officer',parole(pulse('parole_v11','NativeCheckin41')+'>>'+s('check_result'))),('Officer / warrant status',seq(PSYNC,s('warrant'))),('Home activity programme',parole(s('home'))),('Back',PAROLE)],icon='house',stats={'Supervision_active':q('Active'),'Years_remaining':q('Remaining'),'Ending_age':q('EndAge'),'Last_checkin_age':q('LastCheckAge'),'Warrant_issued':q('Warrant41'),'Checkins_completed':q('CheckIns')})
 page('check_result','Officer check-in', 'Review your check-in status. Completed check-ins are saved once per age.', [('Continue',logic([(f'({q("CheckStatus41")} == 1)',s('checked')),(f'({q("CheckStatus41")} == 2)',s('duplicate')),(f'({q("CheckStatus41")} == 3)',s('warrant'))],s('parole_locked')))],icon='clipboard')
 page('checked','Check-in complete','Your officer has recorded this age’s check-in. You can now age up without a missed-check-in warrant. Return to the officer at your next age if supervision continues.',[('Back to supervision',seq(PSYNC,s('parole_status')))],icon='clipboard')
 page('duplicate','Already checked in','Your check-in is already saved at this age. Reopening this page awards no extra progress.',[('Back',seq(PSYNC,s('parole_status')))],icon='clipboard')
 page('warrant','Officer & warrant status','A missed check-in creates a warrant that survives closing this screen and saving the game. Contact the officer to resolve an active warrant through the normal arrest, lawyer and court screens. The outcome is decided by the game.',[
  ('Resolve active warrant with the officer',logic([(f'({q("Warrant41")} != 1)',seq(PSYNC,s('parole_status')))],pulse('parole_v11','NativeWarrantHearing41'))),('Read supervision record',seq(PSYNC,s('parole_status'))),('Back',PAROLE)],icon='police-car',stats={'Warrant_issued':q('Warrant41'),'Missed_checkin_at_age':q('MissedAge41'),'Notice_issued_at_age':q('WarningAge41')})
 def home_finish(label,field,value):return parole(logic([(f'({q("Warrant41")} == 1)',s('warrant')),(f'({q("Sessions")} >= 3)',s('home_limit'))],seq(I('parole_v11','Sessions'),I('parole_v11',field,value),s('home_done'))))
 page('home','Home activity programme','Three optional sessions are available each age. Home activities do not replace your officer check-in.',[
  ('Plan a study session',s('home_study')),('Build a daily routine',s('home_routine')),('Exercise at home',s('home_exercise')),('Back',seq(PSYNC,s('parole_status')))],icon='house')
 for key,title,body,label,field,value,stat in [('study','Study at home','Choose a subject and make a focused study plan.','Complete your study plan','Education',8,'att_smarts'),('routine','Daily routine','Prepare a realistic schedule for appointments and home responsibilities.','Follow your home routine','Discipline',8,'att_happiness'),('exercise','Home exercise','Make time for a gentle exercise session appropriate to your character.','Complete a home exercise session','Discipline',5,'att_health')]:
  r=page('home_'+key,title,body,[(label,home_finish(label,field,value)),('Back',s('home'))],icon='house')
  data=json.loads(r['Choice1_AdvancedLogic']);data['else_when_no_matches']['route_options'][0]['impacts']=[dict(impact_type='hero_stat',stat_id=stat,amount_min=1,amount_max=1)];r['Choice1_AdvancedLogic']=json.dumps(data,separators=(',',':'))
 page('home_limit','Home sessions complete','You have used all three sessions at this age. Check in with your officer, then age up to refresh your home programme.',[('Officer check-in',seq(PSYNC,s('parole_status')))],icon='calendar')
 page('home_done','Home session complete','Your activity is saved and your character’s relevant stat improved. Remember to check in with your officer before aging.',[('Back',seq(PSYNC,s('parole_status')))],icon='house')
 plist=json.loads(allbase['genesis_v9_v11_parole_v11']);plist['Items']=[tile('Supervision record',seq(PSYNC,s('parole_status')),'clipboard','Check in once per age before aging'),tile('Parole officer',seq(PSYNC,s('parole_status')),'police-car','Check in or resolve a warrant'),tile('Home programme',seq(PSYNC,s('home')),'house','Study, routine and exercise'),tile('Warrant status',seq(PSYNC,s('warrant')),'police-car','Missed check-ins have consequences')]
 for n,item in enumerate(plist['Items']):item['IsEnabled']='v41-parole';item['TileID']='v41_parole_'+str(n)
 assets['genesis_v9_v11_parole_v11']=json.dumps(plist,indent=2)
 d.text('prison_plus_v7','Report41','No programme session completed yet.')
 for key,value,lo,hi in [('NativeParoleSync41',0,0,1),('NativeCheckin41',0,0,1),('NativeWarrantHearing41',0,0,1),('Warrant41',0,0,1),('MissedAge41',-1,-1,999),('WarningAge41',-1,-1,999),('Hearing41',0,0,1),('CheckStatus41',0,0,3)]:d.prop('parole_v11',key,value,lo,hi)
 d.prop('worlds39','NativePrisonParole41',0,0,1)
 d.prop('worlds39','BoardAge41',-1,-1,999)
 assets[d.FILE]=d.writecsv(list(csv.DictReader(io.StringIO(base[d.FILE])))+d.rows,d.HEADER)
 # Repair every older entry, including saved dialogs opened before upgrading.
 aliases=[]
 for name,prefix,mapping in [('genesis_careers_v7','scenario.careersV7.prison_plus_v7',dict(refresh='case',certificate='vocational',education='case',therapy='counselling',mediation='mediation',work='work',support='family',parole='parole_prep')),('genesis_activities_v11','scenario.activitiesV11.parole_',dict(status='parole_status',inactive='parole_locked',checkin='parole_status',checked='checked',study='home_study',routine='home_routine',exercise='home_exercise',done='home_done'))]:
  rr=list(csv.DictReader(io.StringIO(allbase[name])))
  for r in rr:
   suffix=r['ScenarioID'].removeprefix(prefix)
   if not r['ScenarioID'].startswith(prefix)or suffix not in mapping:continue
   target=seq(SYNC if name.endswith('v7')else PSYNC,s(mapping[suffix]));r['Title']='Case File & Rehabilitation'if name.endswith('v7')else'Parole & House Arrest';r['Body']='Continue to your current record and available actions.';r['TableRows']='';choices(r,[('Continue',target)]);aliases.append(r['ScenarioID'])
  assets[name]=d.writecsv(rr)
 for owner,fields in d.schemas.items():
  name=next(k for k in allbase if k.startswith('genesis_v')and'_defaults_'in k and k.split('_defaults_',1)[1]==owner)
  rows=list(csv.DictReader(io.StringIO(allbase[name])));assert not set(fields)&{r['key']for r in rows};assets[name]=d.writecsv(rows+list(fields.values()))
 notice=copy.deepcopy(next(r for r in d.rows if r['ScenarioID']==s('warrant')));notice.update(ScenarioID='scenario.paroleEvents41.missed',Title='Missed parole check-in',Body='You aged without completing your required officer check-in. A warrant has been issued. Contact the officer to begin the normal arrest and court process. The warrant remains saved until you resolve it.');choices(notice,[('Contact the officer',s('warrant')),('Review supervision record',seq(PSYNC,s('parole_status')))])
 assets['genesis_v41_parole_events']=d.writecsv([notice],d.HEADER)
 # Put the native military, police and court entries first in the original hub.
 hub=json.loads(assets['genesis_v18_worlds39'])
 for item in hub['Items']:
  if item['Title']=='Judicial & Prison':item['SecondLine']='Native court and prison; rehabilitation; parole check-ins'
 assets['genesis_v18_worlds39']=json.dumps(hub,indent=2)
 (ROOT/'assets.json').write_text(json.dumps(assets,indent=2)+'\n')
 (ROOT/'authoring41.json').write_text(json.dumps(dict(new_scenarios=len(d.rows)+1,repaired_legacy_scene_ids=aliases,rehabilitation_sessions_per_age=6,home_sessions_per_age=3,original_list_identities_retained=True,successful_native_release_required=True,missed_checkin_queues_warrant=True,warrant_resolution_uses_native_arrest=True),indent=2)+'\n')
 return assets

def build(base,out):
 assert hashlib.sha256(Path(base).read_bytes()).hexdigest()==BASE_SHA
 assets=author();out=Path(out);out.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(base)as z:env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'));data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'))
 key=lambda o:(o.assets_file.name,o.path_id);sha=lambda b:hashlib.sha256(b).hexdigest()
 snapshots={key(o):sha(o.get_raw_data())for o in env.objects};sd={key(o):sha(o.get_raw_data())for o in data.objects}
 texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'};rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree();paths=copy.deepcopy(tree['m_Container']);deps=copy.deepcopy(tree['m_DependentAssets'])
 resource_id=next(n+1 for n,e in enumerate(rm.assets_file.externals)if e.path=='resources.assets');file=texts[d.FILE].assets_file;next_id=max(file.objects)+1;changed=set();added={}
 for name,value in assets.items():
  if name in texts and texts[name].read().m_Script==value:continue
  if name in texts:obj=texts[name];changed.add(key(obj))
  else:
   obj=copy.copy(texts['genesis_test_feature_events']);obj.path_id=next_id;next_id+=1;obj.data=texts['genesis_test_feature_events'].get_raw_data();file.objects[obj.path_id]=obj;added[name]=obj.path_id
   path=('genesis_lists/'if value.startswith('{')else'genesis/')+name;assert path not in dict(tree['m_Container']);tree['m_Container'].append((path,dict(m_FileID=resource_id,m_PathID=obj.path_id)))
  asset=obj.read();asset.m_Name=name;asset.m_Script=value;asset.save()
 tree['m_Container'].sort(key=lambda x:x[0]);rm.save_typetree(tree)
 bundle=next(iter(env.files.values())).save(packer='original');db=next(iter(data.files.values())).save(packer='original');(out/'datapack.unity3d').write_bytes(bundle);(out/'data.unity3d').write_bytes(db)
 ae=UnityPy.load(bundle);ad=UnityPy.load(db);after={key(o):sha(o.get_raw_data())for o in ae.objects};afterd={key(o):sha(o.get_raw_data())for o in ad.objects}
 assert set(snapshots)<=set(after)and{k for k in snapshots if snapshots[k]!=after[k]}==changed
 assert set(sd)==set(afterd)and{k for k in sd if sd[k]!=afterd[k]}=={key(rm)}
 reread=next(o for o in ad.objects if o.type.name=='ResourceManager').read_typetree();assert Counter((k,json.dumps(v,sort_keys=True))for k,v in paths)<=Counter((k,json.dumps(v,sort_keys=True))for k,v in reread['m_Container']);assert reread['m_DependentAssets']==deps
 values={o.read().m_Name:o.read().m_Script for o in ae.objects if o.type.name=='TextAsset'};assert all(values[n]==v for n,v in assets.items())
 result=dict(passed=True,datapack_sha256=sha(bundle),data_sha256=sha(db),assets_sha256=sha((ROOT/'assets.json').read_bytes()),added_TextAssets=added,modified_TextAssets=len(changed),all_unedited_Unity_objects_preserved=True,resource_paths_preserved=True,device_runtime_tested=False)
 (ROOT/'content41_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':build(*sys.argv[1:])
