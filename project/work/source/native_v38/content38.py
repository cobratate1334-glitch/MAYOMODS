"""Fictional noir story progression in the game's existing saved Genesis schema."""
import copy,csv,hashlib,io,json,sys,zipfile
from collections import Counter
from pathlib import Path
import UnityPy
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native_v29'))
import content as d
from content import F,G,M,I,T,S,seq,logic,table,add,tile,child,menu,prop,text

OWNER='stalker38';p=lambda k:G(OWNER,k);m=lambda k,v:M(OWNER,k,v);i=lambda k,v=1:I(OWNER,k,v);t=lambda k,v:T(OWNER,k,v)
s=lambda k:S('s38_'+k);HOME=s('entry');BACK=('Back to story',HOME)
def page(k,title,body='',choices=(),icon='clipboard',stats=None):return add('s38_'+k,title,body,choices,icon,tables=table(**stats)if stats else None)
def number(k,v=0,hi=100,lo=0,reset=False):prop(OWNER,k,v,lo,hi,reset)
def guard(target,states=(1,),limited=False,pending=False):
 cases=[('(<hero:age> < 18)',s('young'))]
 disallowed=' && '.join(f'({p("Stage")} != {v})'for v in states)
 cases.append((disallowed,HOME))
 if not pending and 1 in states:cases.append((f'({p("Pending")} == 1)',s('resolve')))
 if limited:cases.extend([(f'({p("Evidence")} >= 100)',seq(m('Stage',3),s('custody'))),(f'({p("Sessions")} >= 3)',s('limit'))])
 if pending:cases.append((f'({p("Pending")} != 1)',HOME))
 return logic(cases,target)

def dispatch():
 return logic([('(<hero:age> < 18)',s('young')),(f'({p("Stage")} == 0)',s('intro')),
   (f'({p("Pending")} == 1)',s('resolve')),(f'({p("Stage")} >= 4)',s('ending')),
   (f'({p("Stage")} == 3)',s('custody')),
   (f'({p("Evidence")} >= 100)',seq(m('Stage',3),t('Report','Detective Ada Mercer obtained enough corroboration to close the story investigation. Your character entered fictional custody.'),s('custody'))),
   (f'(({p("Evidence")} >= 65) || ({p("Panic")} >= 70)) && ({p("Taskforce")} == 0)',seq(m('Taskforce',1),s('manhunt'))),
   (f'({p("Stage")} == 2)',s('retired'))],s('home'))

def author():
 base=json.loads((ROOT.parent/'native_v35/assets.json').read_text())
 d.assets={};d.schemas={};d.rows=[];d.registry=[]
 for k,v,hi,lo,reset in [('Stage',0,4,0,False),('Cases',0,1000,0,False),('Evidence',0,100,0,False),('Panic',0,100,0,False),('Profile',0,100,0,False),
  ('LabNorth',0,100,0,False),('LabHarbor',0,100,0,False),('Witnesses',0,1000,0,False),('Clippings',0,1000,0,False),('Taskforce',0,1,0,False),
  ('Counsel',0,1,0,False),('Sentence',0,40,0,False),('Pending',0,1,0,False),('EventRoll',0,99,0,False),('LastAge',-1,999,-1,False),
  ('ElapsedYears',0,100,0,False),('Sessions',0,3,0,True)]:number(k,v,hi,lo,reset)
 for k,v in [('Alias','Unchosen'),('Motif','Unchosen'),('Location','No chapter selected'),('Report','No story incidents have occurred.')]:text(OWNER,k,v)

 page('young','Available in adulthood','This fictional noir story unlocks at age eighteen.',[('Community Expansions','BP_SHOW_LIST=genesis_v18_community35')],icon='memo')
 page('entry','The Stalker Path','Open your saved story. Investigation time catches up when you return after aging.',[
  ('Open story',logic([('(<hero:age> < 18)',s('young')),
   (f'(({p("Stage")} == 1) || ({p("Stage")} == 2)) && (<hero:age> > {p("LastAge")})',s('clock'))],dispatch())),
  ('Community Expansions','BP_SHOW_LIST=genesis_v18_community35')],icon='face-thinking')
 page('intro','A dark fiction branch','A noir story about an offender, a frightened community and a detective pursuing accountability. Violence happens offscreen. Evidence accumulates; ending the path does not erase the case.',[
  (name,guard(seq(t('Alias',name),s('motif')),states=(0,)))for name in ['The Hollow Echo','The Ash Rook','The Midnight Visitor']]+[('Leave this story','BP_SHOW_LIST=genesis_v18_community35')],icon='face-thinking')
 page('motif','Choose a story motif','Choose a symbolic recurring detail for the fictional case file. This determines your narrative profile.',[
  (name,guard(seq(t('Motif',name),m('Stage',1),m('LastAge','<hero:age>'),t('Report','The story began. No incidents have occurred.'),s('home')),states=(0,)))for name in ['A stopped clock','A paper star','A glass bird']]+[('Back',s('intro'))],icon='memo')
 status={'Alias':p('Alias'),'Story_incidents':p('Cases'),'Evidence_0_to_100':p('Evidence'),'Public_panic_0_to_100':p('Panic'),'Profile_progress':p('Profile'),'Chapters_this_age':p('Sessions')}
 page('home','The Stalker Path','Each chapter advances a fictional offscreen incident and the investigation. You have three chapter slots per age. There is no way to erase accumulated evidence.',[
  ('Next story chapter',guard(s('locations'),limited=True)),('Investigation & clippings',s('casefile')),('End the offender path',guard(s('retire_confirm'))),('Back',HOME)],icon='face-thinking',stats=status)
 locations=[('The Old Warehouse','Rain drums on an empty roof as the next noir chapter opens.'),('The Pinewood Forest','Wind moves through the trees; the town waits for news.'),('The Lantern Alley','A flickering lamp frames the next chapter in the city story.')]
 page('locations','Choose a chapter setting','These are atmosphere choices. Every setting uses the same story risk rules.',[
  (name,guard(seq(t('Location',name),s('confirm')),limited=True))for name,_ in locations]+[BACK],icon='memo')
 page('confirm',p('Location'),'Continue this offscreen fiction chapter? It will consume one slot and create lasting story consequences. Canceling here creates no incident.',[
  ('Continue the chapter',guard(seq(i('Sessions'),m('Pending',1),M('careers_v18','NativeCupRoll',0),M('careers_v18','NativeCupRoll',1),m('EventRoll',G('careers_v18','Roll')),s('resolve')),limited=True)),BACK],icon='memo')
 def result(witness=False,review=False):
  report='A fictional victim died offscreen. The community mourned, and investigators connected another chapter to the case.'
  if witness:report+=' A surviving witness gave Ada Mercer a new lead.'
  if review:report+=' The Northbridge and Harbor review teams independently corroborated a story detail.'
  return seq(m('Pending',0),i('Cases'),i('Clippings'),i('Evidence',F('add',12,F('div',p('EventRoll'),8),18 if witness else 8 if review else 0)),
   i('Panic',F('add',10,F('div',p('EventRoll'),12))),i('Profile',14 if witness else 10),i('LabNorth',10),i('LabHarbor',14 if review else 8),
   i('Witnesses',1 if witness else 0),t('Report',report),s('aftermath'))
 page('resolve','Chapter aftermath','The offscreen chapter is pending. Its result is saved; closing this card cannot reroll it or start another chapter.',[
  ('Read the aftermath',guard(logic([(f'({p("EventRoll")} < 25)',result(witness=True)),(f'({p("EventRoll")} >= 75)',result(review=True))],result()),pending=True))],icon='memo')
 page('aftermath','The city responds',p('Report'),[('Review the case',dispatch())],icon='clipboard',stats={'Evidence':p('Evidence'),'Public_panic':p('Panic'),'Witnesses':p('Witnesses')})
 page('clock','Time moves the case forward','Aging gives the investigators more time. Evidence and the profile advance even after the offender path ends.',[
  ('Review the updated case',guard(logic([(f'(<hero:age> <= {p("LastAge")})',dispatch())],seq(m('ElapsedYears',F('clamp',F('sub','<hero:age>',p('LastAge')),0,100)),
   i('Evidence',F('mul',p('ElapsedYears'),F('min',p('Cases'),1),6)),i('Profile',F('mul',p('ElapsedYears'),F('min',p('Cases'),1),8)),
   i('Panic',F('mul',p('ElapsedYears'),-3)),m('LastAge','<hero:age>'),s('clock_result'))),states=(1,2)))],icon='calendar')
 page('clock_result','Updated case file','The saved investigation clock has advanced once for the elapsed years.',[('Continue',dispatch())],icon='clipboard')
 page('casefile','Ada Mercer’s case file','Lead detective: Ada Mercer. The fictional Northbridge and Harbor teams compete to connect story clues; their records persist with this life.',[
  ('Psychological story profile',s('profile')),('Newspaper clippings',s('clippings')),('Legal story support',s('counsel')),BACK],icon='clipboard',stats={'Evidence':p('Evidence'),'Public_panic':p('Panic'),'Northbridge_review':p('LabNorth'),'Harbor_review':p('LabHarbor'),'Witness_accounts':p('Witnesses')})
 page('profile','A recurring story pattern','Ada Mercer is connecting the fictional motif '+p('Motif')+' to '+p('Alias')+'. This is a narrative profile, not a diagnosis. '+p('Report'),[BACK],icon='face-thinking',stats={'Profile_progress':p('Profile'),'Story_motif':p('Motif')})
 page('clippings','Newspaper archive','The archive records the city’s response. One clipping is retained for each resolved chapter; reviewing it gives no reward or new incident.',[BACK],icon='memo',stats={'Archived_clippings':p('Clippings'),'Latest_story':p('Report')})
 page('limit','The next chapter must wait','You have used all three chapter slots at this age. Age up to refresh the slots; the investigation will also advance.',[BACK],icon='calendar')
 page('manhunt','The Nightingale task force','Rising evidence or public panic brought the fictional Nightingale task force into the case. A national bulletin and detective encounter now form part of the story.',[
  ('Read the case file',s('casefile')),('Seek legal story support',s('counsel')),('Surrender in the story',guard(seq(m('Stage',3),t('Report','Your character surrendered to the fictional task force. The case moved to a hearing.'),s('custody')),states=(1,2))),BACK],icon='clipboard',stats={'Evidence':p('Evidence'),'Public_panic':p('Panic')})
 page('retire_confirm','End the offender path?','No new incidents will be available. The existing case and witness accounts remain, and investigators can still conclude the story later.',[
  ('End this path',guard(seq(m('Stage',2),t('Report','The offender path ended. The community began recovering, while Ada Mercer kept the existing case open.'),s('retired')))),BACK],icon='memo')
 page('retired','An open case remains',p('Report'),[('Review investigation',s('casefile')),('Surrender in the story',guard(seq(m('Stage',3),s('custody')),states=(2,))),BACK],icon='clipboard',stats={'Evidence':p('Evidence'),'Public_panic':p('Panic')})
 counsel_route=guard(logic([(f'({p("Counsel")} == 1)',s('counsel_done'))],{
  'cases':[{'if':{'filter':'[finance.bankBalance<1000]'},'then':{'route_options':[{'route_to':s('funds')}]}}],
  'else_when_no_matches':{'route_options':[{'route_to':seq('BP_BANK_BALANCE=-1000',m('Counsel',1),s('counsel_done'))}]}}),states=(1,2,3))
 page('counsel','Legal story support','A fictional representation option costs 1,000 from your game balance, once for this story. It affects the story hearing; it does not remove evidence.',[('Arrange representation — 1,000',counsel_route),BACK],icon='suitcase')
 page('counsel_done','Representation arranged','Your story counsel is recorded. Reopening this option cannot charge you again.',[BACK],icon='handshake')
 page('funds','Not enough money','No representation was bought and no payment was taken.',[BACK],icon='money-bag')
 page('custody','The case reaches a hearing',p('Report')+' This is the story’s custody record.',[
  ('Attend the story hearing',guard(seq(m('Sentence',F('clamp',F('sub',F('add',6,F('mul',p('Cases'),2)),F('mul',p('Counsel'),3)),3,40)),m('Stage',4),t('Report','The story hearing ended with accountability. The community’s archive remains, and this offender path is closed.'),s('ending')),states=(3,))),
  ('Legal story support',s('counsel')),('Review case',s('casefile')),BACK],icon='clipboard')
 page('ending','The Stalker Path: epilogue',p('Report')+' The saved ending cannot be reset by reopening a card. The sentence is part of this fictional story, separate from the stock prison system.',[
  ('Review archive',s('clippings')),('Review detective profile',s('profile')),('Community Expansions','BP_SHOW_LIST=genesis_v18_community35')],icon='memo',stats={'Story_sentence_years':p('Sentence'),'Story_incidents':p('Cases'),'Evidence':p('Evidence')})

 menu(OWNER,'The Stalker Path',[tile('Open your story',HOME,'face-thinking','A fictional noir branch with investigation consequences')],entry='T2',icon='face-thinking',sub='Saved noir story; detective case file and public panic')
 d.assets['genesis_v18_defaults_'+OWNER]=d.writecsv(list(d.schemas[OWNER].values()))
 old=list(csv.DictReader(io.StringIO(base[d.FILE])));ids={r['ScenarioID']for r in old}
 assert not ids.intersection(r['ScenarioID']for r in d.rows)
 d.assets[d.FILE]=base[d.FILE]+('' if base[d.FILE].endswith('\n')else'\r\n')+d.writecsv(d.rows,d.HEADER).split('\r\n',1)[1]
 registry=io.StringIO(newline='');csv.writer(registry,lineterminator='\r\n').writerows(d.registry)
 assert OWNER not in [r[0]for r in csv.reader(io.StringIO(base['genesis_feature_containers']))if r]
 d.assets['genesis_feature_containers']=base['genesis_feature_containers']+(''if base['genesis_feature_containers'].endswith('\n')else'\r\n')+registry.getvalue()
 community=json.loads(base['genesis_v18_community35']);entry=child('The Stalker Path',OWNER,'face-thinking','Fictional case file; evidence; public panic and a saved ending');entry['TileID']='stalker38_entry';community['Items'].append(entry)
 d.assets['genesis_v18_community35']=json.dumps(community,indent=2)
 assets={**base,**d.assets}
 (ROOT/'assets.json').write_text(json.dumps(assets,indent=2)+'\n')
 (ROOT/'schemas38.json').write_text(json.dumps(d.schemas,indent=2)+'\n')
 report=dict(new_scenarios=len(d.rows),new_assets=[n for n in d.assets if n not in base],modified_assets=[n for n in d.assets if n in base],owner=OWNER,new_saved_properties=len(d.schemas[OWNER]),adult_only=True,abstract_fiction=True,existing_scenarios_preserved=True)
 (ROOT/'authoring38.json').write_text(json.dumps(report,indent=2)+'\n');return assets,report

def build(base,out):
 assert hashlib.sha256(Path(base).read_bytes()).hexdigest()=='01fcbf77e9898ee2f71b698d86d6d1eba992e963a670f984d90acbebfcbe2bb3'
 assets,report=author();out=Path(out);out.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(base)as z:env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'));data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'))
 key=lambda o:(o.assets_file.name,o.path_id);sha=lambda b:hashlib.sha256(b).hexdigest()
 snapshots={key(o):sha(o.get_raw_data())for o in env.objects};snapshot_data={key(o):sha(o.get_raw_data())for o in data.objects}
 texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'}
 rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree();paths=copy.deepcopy(tree['m_Container']);deps=copy.deepcopy(tree['m_DependentAssets'])
 resource_id=next(n+1 for n,e in enumerate(rm.assets_file.externals)if e.path=='resources.assets')
 file=texts[d.FILE].assets_file;next_id=max(file.objects)+1;changed=set();added={}
 baseline=json.loads((ROOT.parent/'native_v35/assets.json').read_text())
 for name,value in baseline.items():assert texts[name].read().m_Script==value,name
 for name,value in assets.items():
  if name in baseline and value==baseline[name]:continue
  if name in texts:obj=texts[name];changed.add(key(obj))
  else:
   obj=copy.copy(texts['genesis_test_feature_events']);obj.path_id=next_id;next_id+=1;obj.data=texts['genesis_test_feature_events'].get_raw_data();file.objects[obj.path_id]=obj;added[name]=obj.path_id
   path=('genesis_lists/'if value.startswith('{')else'genesis/')+name;assert path not in dict(tree['m_Container']);tree['m_Container'].append((path,dict(m_FileID=resource_id,m_PathID=obj.path_id)))
  asset=obj.read();asset.m_Name=name;asset.m_Script=value;asset.save()
 tree['m_Container'].sort(key=lambda x:x[0]);rm.save_typetree(tree)
 bundle=next(iter(env.files.values())).save(packer='original');data_bytes=next(iter(data.files.values())).save(packer='original')
 (out/'datapack.unity3d').write_bytes(bundle);(out/'data.unity3d').write_bytes(data_bytes)
 after_env=UnityPy.load(bundle);after_data=UnityPy.load(data_bytes);after={key(o):sha(o.get_raw_data())for o in after_env.objects};after_d={key(o):sha(o.get_raw_data())for o in after_data.objects}
 assert set(snapshots)<=set(after)and len(after)==len(snapshots)+len(added)
 assert {k for k in snapshots if snapshots[k]!=after[k]}==changed
 assert set(after_d)==set(snapshot_data)and{k for k in snapshot_data if snapshot_data[k]!=after_d[k]}=={key(rm)}
 reread=next(o for o in after_data.objects if o.type.name=='ResourceManager').read_typetree()
 assert Counter((k,json.dumps(v,sort_keys=True))for k,v in paths)<=Counter((k,json.dumps(v,sort_keys=True))for k,v in reread['m_Container'])
 assert reread['m_DependentAssets']==deps
 for name,pathid in added.items():assert dict(reread['m_Container'])[('genesis_lists/'if assets[name].startswith('{')else'genesis/')+name]==dict(m_FileID=resource_id,m_PathID=pathid)
 values={o.read().m_Name:o.read().m_Script for o in after_env.objects if o.type.name=='TextAsset'}
 assert all(values[n]==v for n,v in assets.items())
 old_rows=list(csv.DictReader(io.StringIO(baseline[d.FILE])));new_rows=list(csv.DictReader(io.StringIO(values[d.FILE])))
 assert old_rows==new_rows[:len(old_rows)]
 report.update(passed=True,datapack_sha256=sha(bundle),data_sha256=sha(data_bytes),assets_sha256=sha((ROOT/'assets.json').read_bytes()),added_TextAssets=added,modified_TextAssets=len(changed),all_other_Unity_objects_byte_identical=True,all_original_resource_paths_preserved=True,all_original_scenario_rows_preserved=True,physical_device_tested=False,Unity_rendering_modeled=True)
 (ROOT/'content38_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

if __name__=='__main__':build(*sys.argv[1:])
