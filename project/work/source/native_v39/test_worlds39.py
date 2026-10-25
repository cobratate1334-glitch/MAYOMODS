"""Exercise authored progression using the retained ARM64 random bridge.

Genesis expressions, scene rendering, banking and save serialization remain
models. Tests cover independent economic and progression invariants.
"""
import copy,csv,hashlib,io,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native_v35'))
import test_content35 as old
old.ROOT=ROOT;old.test_native.ROOT=ROOT.parent/'native_v35'
class Model(old.Model):
 def __init__(self,binary,age=30,bank=10000000,country='Brazil'):
  self.smarts=75;self.fame=0
  super().__init__(binary,age=age,bank=bank,country=country)
  for owner,schemas in self.schemas.items():
   if owner not in self.props:self.props[owner]={k:int(r['value'])if r['type']=='int'else r['value']for k,r in schemas.items()}
 @property
 def q(self):return self.props['worlds39']
 def choose(self,key,index=1):
  row=self.rows['scenario.activitiesV18.w39_'+key];assert row[f'Choice{index}_Text'],(key,index)
  logic=row[f'Choice{index}_AdvancedLogic'];self.route(self.advanced(json.loads(logic))if logic else row[f'Choice{index}_RouteTo']);return self.scene.rsplit('.',1)[-1]
 def basechoose(self,key,index=1):return old.Model.choose(self,key,index)
 def condition(self,test):
  if 'filter'in test and 'hero.att_intelligence'in test['filter']:
   test={**test,'filter':test['filter'].replace('hero.att_intelligence',str(self.smarts))}
  if 'filter'in test and 'hero.att_fame'in test['filter']:
   test={**test,'filter':test['filter'].replace('hero.att_fame',str(self.fame))}
  return super().condition(test)
 def restore(self,data):
  self.age=data['age'];self.bank=data['bank'];self.props.clear();self.props.update(copy.deepcopy(data['props']));self.scene='';self.random=99
 def resolve_event(self):
  self.choose('resume');key=self.scene.rsplit('w39_',1)[-1];self.choose(key);return key

def validate(path):
 binary=Path(path).read_bytes();m=Model(binary);initial=m.snapshot();checks=0;groups={}
 def check(ok,label):
  nonlocal checks
  assert ok,label;checks+=1;groups[label.split(':',1)[0]]=groups.get(label.split(':',1)[0],0)+1
 def reset(age=30,bank=10000000,values=None):
  m.restore(initial);m.age=age;m.bank=bank;m.smarts=75;m.fame=0
  if values:m.q.update(values)
  return m
 def done(key,index=1,roll=99):
  m.random=roll;m.choose(key,index);check(m.q['Pending']==1,'chapter:started '+key);event=m.resolve_event();check(m.q['Pending']==0,'chapter:resolved '+event);return event
 baseline=json.loads((ROOT.parent/'native_v38/assets.json').read_text());report=json.loads((ROOT/'authoring39.json').read_text());rows=[r for r in m.rows.values()if r['ScenarioID'].startswith('scenario.activitiesV18.w39_')]
 check(len(rows)==report['new_scenarios'],'schema:scene count');oldrows=list(csv.DictReader(io.StringIO(baseline['genesis_activities_v18'])));check(list(m.rows.values())[:len(oldrows)]==oldrows,'preservation:all existing scenes')
 original=json.loads(baseline['genesis_v18_community35'])['Items'];current=json.loads(m.assets['genesis_v18_community35'])['Items'];check(current[:-1]==original,'preservation:community items');target=current[-1]['ActionList'][0]['ConditionList'][0]['ListID'];check(target=='genesis_v18_worlds39','navigation:registered entry')
 registry=next(r for r in csv.reader(io.StringIO(m.assets['genesis_feature_containers']))if r and r[0]=='worlds39');check(registry[3]=='genesis_v18_defaults_worlds39'and registry[13]==target,'navigation:defaults bound to container')
 def routes(row,n):
  if row[f'Choice{n}_AdvancedLogic']:
   data=json.loads(row[f'Choice{n}_AdvancedLogic']);return [c['then']['route_options'][0]['route_to']for c in data['cases']]+[data['else_when_no_matches']['route_options'][0]['route_to']]
  return [row[f'Choice{n}_RouteTo']]if row[f'Choice{n}_RouteTo']else[]
 starters={}
 native_filters={r['filter']for r in csv.DictReader(io.StringIO(json.load(open('analysis/base_assets.json'))['genesis_lookup_filter_set']))}
 native_icons={r['EmojiString']for r in csv.DictReader(io.StringIO(json.load(open('analysis/base_assets.json'))['genesis_lookup_emoji_visuals']))}
 for row in rows:
  check(row['HasDismissButton']=='true'and 1<=sum(bool(row[f'Choice{n}_Text'])for n in range(1,5))<=4,'schema:dismiss and choices')
  check(row['EmojiString']in native_icons,'schema:shipped scene icon')
  for owner,key in re.findall(r'<GFC\.([^.>]+)\.([^>]+)>',str(row)):check(key in m.schemas[owner],'schema:property '+owner+'.'+key)
  for fn in re.findall(r'<function:([^:<>]+):',str(row)):check(fn in {'add','sub','mul','div','clamp','max','min','abs'},'schema:original function '+fn)
  for n in range(1,5):
   if not row[f'Choice{n}_Text']:continue
   if row[f'Choice{n}_AdvancedLogic']:
    data=json.loads(row[f'Choice{n}_AdvancedLogic'])
    for case in data['cases']:
     m.condition(case['if'])
     if 'filter'in case['if']:
      for token in re.findall(r'(?:hero|finance)\.[A-Za-z_]+',case['if']['filter']):check(token in native_filters,'schema:shipped native filter')
   for route in routes(row,n):
    for kind in re.findall(r'BP_GFC_MODIFY_PROPERTY=worlds39:EventKind:=(\d+)>>',route):starters[int(kind)]=(row['ScenarioID'].rsplit('w39_',1)[-1],n)
    for part in m.split(route):
     if part.startswith('scenario.'):check(part in m.rows,'navigation:scene reference')
     elif part.startswith('BP_SHOW_LIST='):check(part.split('=',1)[1]in m.assets,'navigation:list reference')
     elif part.startswith('BP_GFC_'):
      owner,key=part.split('=',1)[1].split(':',2)[:2];check(key in m.schemas[owner],'schema:mutation target')
     else:check(part.startswith('BP_BANK_BALANCE='),'schema:blueprint')
 for name in report['new_assets']:
  if not name.startswith('genesis_v18_defaults_'):
   obj=json.loads(m.assets[name]);check(obj['ListID']==name and len({x['TileID']for x in obj['Items']})==len(obj['Items']),'navigation:list IDs')
   for item in obj['Items']:
    check(item['Icon']in native_icons,'schema:shipped menu icon')
    action=item['ActionList'][0]['ConditionList'][0];check(action.get('ScenarioID','')in m.rows or action.get('ListID','')in m.assets,'navigation:menu route')
 check(len(starters)==len(report['cached_events']),'chapter:every event has a start route')
 ready=dict(MilitaryRole=1,PoliceRole=1,IntelRole=1,MilitarySkill=80,PoliceSkill=80,IntelSkill=80,ScienceBranch=1,ScienceKnowledge=80,ScienceLab=80,ScienceContainment=80,
  MythSpecies=1,MythMoon=3,MythControl=80,MythPower=80,AlienRace=1,AlienState=1,DisasterCrisis=1,DisasterFood=100,DisasterTools=10,
  BioLab=1,BioState=1,BioRole=1,BioFunding=200000,BioStability=80,RacingSetup=2,CoachActive=1,CoachLicense=1,CoachTeam=1,CoachFormation=2,
  NationalRole=1,NationalTournament=1,ArchaeologyStudy=3,ArchaeologyMuseum=1,ArchaeologyArtifacts=5,CorpFounded=1,CorpCEO=1,CorpBranches=3,
  InfluencerCamera=1,InfluencerEditors=2,InfluencerQuality=80,LineageOriginSet=0,RoyalActive=1,RoyalRealm=1,RoyalWar=1,CourtStage=1,CourtTrialRound=2)
 for slot in range(3):ready.update({f'Plot{slot}Stage':3,f'Plot{slot}Type':1})
 # All 100 outcomes of every authored random chapter commit once, preserve the
 # saved outcome, and reject a second resolve. A smaller start set exercises
 # the actual ARM64 bridge rather than inventing random values in that bridge.
 for kind,info in report['cached_events'].items():
  kind=int(kind);key=info['key'];pre=info['prefix'];start,index=starters[kind]
  for roll in range(100):
   reset(age=2 if key=='Lineage_birth'else 30,values=ready);m.q.update(Pending=1,EventKind=kind,EventRoll=roll,EventThreshold=47)
   if key in ['Court_contraband','Court_escape']:m.q.update(CourtStage=3,CourtFaction=1,CourtRespect=60,CourtSentence=10)
   m.choose(key);check(m.q['Pending']==0,'outcomes:resolved '+key);after=m.snapshot();m.choose(key);check(m.snapshot()==after,'outcomes:duplicate blocked '+key)
   check(all(r['type']!='int'or int(r['minimum'])<=m.props[o][k]<=int(r['maximum'])for o,rr in m.schemas.items()for k,r in rr.items()),'outcomes:bounded saved stats')
  reset(age=2 if key=='Lineage_birth'else 30,values=ready);m.props['community35']['TVActive']=1
  if key in ['Court_contraband','Court_escape']:m.q.update(CourtStage=3,CourtFaction=1,CourtRespect=60,CourtSentence=10)
  m.random=53;m.choose(start,index);check(m.q['Pending']==1 and m.q['EventKind']==kind and m.q['EventRoll']==53,'ARM64:real roll '+key)
  saved=m.snapshot();threshold=m.q['EventThreshold'];m.props['careers_v18']['Roll']=0;m.props['community35']['TVMorale']=0;m.choose('resume');check(m.scene.endswith('w39_'+key)and m.q['EventRoll']==53 and m.q['EventThreshold']==threshold,'chapter:saved roll and threshold')
  m.restore(saved);m.choose(key);after=m.snapshot();m.choose(key);check(m.snapshot()==after,'chapter:reload duplicate blocked')
  reset(age=2 if key=='Lineage_birth'else 30,values=ready);m.props['community35']['TVActive']=1
  if key in ['Court_contraband','Court_escape']:m.q.update(CourtStage=3,CourtFaction=1,CourtRespect=60,CourtSentence=10)
  m.q[pre+'Actions']=8;before=m.snapshot();m.choose(start,index);check(m.snapshot()==before,'allowance:quota blocks chapter')
  if info['min_age']:
   m.q[pre+'Actions']=0;m.age=info['min_age']-1;before=m.snapshot();m.choose(start,index);check(m.snapshot()==before,'age:chapter gate')
 # Costs, prerequisites and story progression for each branch.
 reset(bank=0);before=m.snapshot();m.choose('Military_train');check(m.snapshot()==before,'economy:poor service course')
 reset();m.choose('Military_country');m.choose('Military_branches1',2);check(m.q['MilitaryRoleName'].startswith('GRUMEC'),'service:Brazil naval branch')
 for _ in range(2):m.choose('Military_train')
 for _ in range(2):done('Military_desk')
 m.choose('Military_train',2);check(m.q['MilitaryRank']==1,'service:promotion requires milestones')
 before=m.bank;m.choose('Military_pay');paid=m.bank;m.choose('Military_pay');check(paid>before and m.bank==paid,'economy:service income once')
 reset(values={'PoliceRegion':1,'PoliceRole':1,'PoliceRank':2});m.choose('Police_elite');check(m.q['PoliceRoleName'].startswith('BOPE'),'service:BOPE police only')
 reset(values={'PoliceRegion':1,'PoliceRole':2,'PoliceRank':2});m.choose('Police_elite');check(m.q['PoliceRoleName'].startswith('CORE'),'service:CORE civil police')
 reset();m.smarts=69;before=m.snapshot();m.choose('Intel_branches2');check(m.snapshot()==before,'service:actual smarts filter gate')
 m.smarts=70;m.choose('Intel_branches2');check(m.q['IntelRole']==1,'service:high-smarts intelligence application')
 reset();m.choose('Science_branch',2)
 for _ in range(3):m.choose('Science_lab')
 for _ in range(4):done('Science_desk')
 m.choose('Science_desk',2);check(m.q['ScienceDiscoveries']==1 and m.q['ScienceOutbreaks']==1 and m.q['ScienceProgress']==0,'science:completed public-health project')
 before=m.snapshot();m.choose('Science_desk',2);check(m.snapshot()==before,'science:no duplicate discovery')
 reset(values={'SciencePapers':10,'ScienceDiscoveries':3});m.choose('Science_record',2);before=m.snapshot();m.choose('Science_record',2);check(m.snapshot()==before and m.q['SciencePrize']==1,'science:prize once')
 reset();m.choose('Myth_choose');m.choose('Myth_train',2);done('Myth_quests',2);check(m.q['MythQuests']==1 and m.q['MythMoon']==1,'myth:quest and moon progression')
 m.q['MythMoon']=3;done('Myth_quests');check(m.q['MythMoon']==0,'myth:full moon wraps')
 reset(age=3);m.choose('Alien_race2');check(m.q['AlienRace']==2 and m.q['AlienPlanet']=='Thalassa','alien:early origin')
 m.age=18;m.q.update(AlienCamouflage=0,AlienPower=65);m.choose('Alien_capture');m.choose('Alien_exit');check(m.q['AlienState']==3,'alien:capture ending')
 reset(values={'ScienceAnomalies':2});m.choose('Alien_contact');m.choose('Alien_treaty');before=m.snapshot();m.choose('Alien_treaty');check(m.snapshot()==before and m.q['AlienTreaty']==1,'alien:treaty reward once')
 reset();m.choose('Disaster_supply');m.choose('Disaster_supply',2);m.choose('Disaster_start')
 for _ in range(4):done('Disaster_week')
 m.choose('Disaster_review',2);check(m.q['DisasterCompleted']==m.q['DisasterSurvived']==1 and m.q['DisasterWeek']==4,'disaster:four-week crisis')
 before=m.snapshot();m.choose('Disaster_review',2);m.choose('Disaster_start');check(m.snapshot()==before,'disaster:no duplicate ending or same-age restart')
 reset(values={'ScienceKnowledge':70});m.choose('Bio_lab');m.choose('Bio_lab',2);done('Bio_desk');check(m.q['BioFunding']==190000 and m.q['BioProjects']==1,'bio:project funding consumed')
 m.q['BioClassification']=20;m.choose('Bio_review',3);m.choose('Bio_leak');before=m.snapshot();m.choose('Bio_leak');check(m.snapshot()==before and m.q['BioLeak']==0,'bio:oversight reward once')
 reset(age=5);before=m.snapshot();m.choose('Racing_train');check(m.snapshot()==before,'age:karting gate')
 m.age=6;m.choose('Racing_train');m.choose('Racing_setup');done('Racing_desk');check(m.q['RacingRaces']==1 and m.q['RacingPoints']==12,'racing:child race progression')
 reset(age=21);m.choose('Coach_hire');m.choose('Coach_hire',2);m.choose('Coach_tactics',2)
 for _ in range(6):done('Coach_matchday',2)
 m.choose('Coach_board');check(m.q['CoachSeasons']==m.q['CoachTitles']==1 and m.q['CoachMatches']==0,'coach:season and board budget')
 before=m.snapshot();m.choose('Coach_hire',3);m.choose('Coach_board');check(m.snapshot()==before,'coach:no repeat appointment budget or season review')
 reset(age=18,values={'NationalSkill':75,'NationalSport':1});m.choose('National_callup',2);m.choose('National_games')
 for _ in range(3):done('National_games',2)
 m.choose('National_games',3);check(m.q['NationalMedals']==1 and m.q['NationalTournament']==0,'national:three-round gold medal')
 before=m.snapshot();m.choose('National_games',3);m.choose('National_games');check(m.snapshot()==before,'national:medal duplicate and four-age gate')
 m.age=22;m.q['NationalActions']=0;m.choose('National_games');check(m.q['NationalTournament']==1,'national:next event after four ages')
 reset(values={'NationalSport':2});m.props['community35']['SoccerSkill']=100;before=m.snapshot();m.choose('National_callup',2);check(m.snapshot()==before,'national:soccer skill cannot qualify basketball')
 reset()
 for _ in range(3):m.choose('Archaeology_study')
 for _ in range(3):done('Archaeology_desk')
 m.choose('Archaeology_museum');check(m.q['ArchaeologyMuseum']==1 and m.q['ArchaeologyArtifacts']==3,'archaeology:study to museum')
 before=m.bank;m.choose('Archaeology_record');paid=m.bank;m.choose('Archaeology_record');check(paid>before and m.bank==paid,'economy:museum income once')
 reset();m.choose('Corp_found')
 for n in range(3):m.choose('Corp_market'+str(n))
 m.choose('Corp_ipo');check(m.q['CorpIPO']==1 and m.q['CorpBranches']==3,'corporation:branches and IPO')
 before=m.snapshot();m.choose('Corp_ipo');m.choose('Corp_market1');check(m.snapshot()==before,'corporation:IPO and branch duplicates')
 m.choose('Corp_takeover');before=m.snapshot();m.choose('Corp_takeover');check(m.snapshot()==before and m.q['CorpBranches']==5,'corporation:takeover once')
 m.age=90;m.choose('Corp_found',2);check(m.q['CorpEra']==3,'corporation:era unlock after elapsed years')
 m.q.update(CorpShareholders=10);m.choose('Corp_ipo',3);before=m.snapshot();m.choose('Corp_pay');check(m.snapshot()==before and m.q['CorpCEO']==0,'corporation:CEO dismissal stops dividends')
 reset();m.choose('Property_plot0_plan');m.choose('Property_plot0_type',2);m.choose('Property_plot0_plan',3);m.choose('Property_plot0_build')
 for _ in range(4):done('Property_plot0_build',2)
 m.choose('Property_plot0_build',3);check(m.q['Plot0Stage']==4 and m.q['Plot0Rent']==4000 and m.q['Plot1Stage']==0,'property:independent plot construction')
 before=m.bank;m.choose('Property_plot0',4);paid=m.bank;m.choose('Property_plot0',4);check(paid>before and m.bank==paid,'economy:property income once')
 reset();m.choose('Influencer_studio');m.choose('Influencer_studio',2);m.choose('Influencer_studio',3);before=m.bank;done('Influencer_upload');check(m.q['InfluencerUploads']==1 and m.bank==before-200,'influencer:one upload wage charge')
 m.q['InfluencerFollowers']=60000;m.choose('Influencer_agency');m.choose('Influencer_creators');before=m.snapshot();m.choose('Influencer_creators');check(m.snapshot()==before and m.q['InfluencerCreators']==1,'influencer:creator signing once')
 reset(values={'Fame':60});m.choose('Sponsor_offers');m.choose('Sponsor'); # this opens offers without changing contract
 before=m.bank;m.choose('Sponsor',3);paid=m.bank;m.choose('Sponsor',3);check(paid>before and m.bank==paid,'economy:sponsor payout once')
 m.choose('Sponsor_review',2);m.choose('Sponsor_offers',2);m.choose('Sponsor',3);check(m.bank==paid-5000,'economy:switching brands cannot double payout')
 m.age=34;before=m.snapshot();m.choose('Sponsor',3);check(m.snapshot()==before,'sponsor:expired contract cannot pay')
 reset();m.fame=80;m.choose('Sponsor_offers');check(m.q['SponsorContract']==1,'sponsor:native famous careers qualify')
 reset(age=3);m.choose('Lineage_origin');check(m.q['LineageOrigin']==1 and m.q['Fame']==15,'lineage:celebrity origin')
 before=m.snapshot();m.choose('Lineage_origin',2);check(m.snapshot()==before,'lineage:origin once')
 m.age=18;m.choose('Lineage_media',3);before=m.snapshot();m.choose('Lineage_media',3);check(m.snapshot()==before,'lineage:support once')
 reset(age=30);m.choose('Lineage_grow');m.choose('Lineage_grow',2);m.choose('Lineage_grow',3);m.choose('Lineage_grow',3);check(m.q['LineageChildren']==2,'family:marriage and descendants')
 reset(age=0);before=m.snapshot();m.choose('Lineage_person14');check(m.snapshot()==before,'family:unborn nephew cannot visit')
 m.choose('Lineage_discover14');check(m.scene.endswith('w39_Lineage_undiscovered'),'family:unborn profile stays undiscovered')
 reset(age=70);before=m.snapshot();m.choose('Lineage_person6');check(m.snapshot()==before,'family:memorial parent cannot visit')
 m.choose('Lineage_discover6');check(m.scene.endswith('w39_Lineage_memorial'),'family:memorial discovery route')
 family=json.loads((ROOT/'family_tree39.json').read_text());check(len(family['nodes'])==20 and next(x for x in family['nodes']if x['id']=='child1')['parents']==['hero','partner'],'family:connected parent edges')
 reset();m.choose('Royal_realm');before=m.snapshot();m.choose('Royal_council',2);check(m.snapshot()==before,'royalty:constitutional parliamentary gate')
 m.choose('Royal_council');m.choose('Royal_council',2);check(m.q['RoyalLaws']==1 and m.q['RoyalTreasury']==450000,'royalty:law treasury cost')
 reset();m.choose('Court_case');m.choose('Court_case',2);m.choose('Court_trial');m.choose('Court_trial');done('Court_trial',2,roll=0);check(m.q['CourtStage']==3 and m.q['CourtSentence']>0,'court:conviction story')
 before=m.snapshot();m.choose('Court_case',2);check(m.snapshot()==before,'court:closed defense purchase blocked')
 m.ageup();before=m.q['CourtSentence'];m.choose('Court_clock');check(m.q['CourtSentence']==before-1,'court:elapsed sentence clock')
 before=m.snapshot();m.choose('Court_clock');check(m.snapshot()==before,'court:same-age sentence clock once')
 m.age=60;m.choose('Court_clock');check(m.q['CourtStage']==4 and m.q['CourtSentence']==0,'court:sentence ending saved')
 reset(age=18);m.props['community35'].update(MangaActive=0,MangaSales=100000,MangaRoyalty=5000);m.choose('Publishing_concept');check(m.props['community35']['MangaTitle']=='The Night Orchard'and m.props['community35']['MangaRoyalty']==5000 and m.q['PublishingArchivedCopies']==100000,'publishing:new title keeps royalties')
 reset(values={'Pending':1,'EventKind':1});before=m.snapshot();m.choose('Corp_found');check(m.snapshot()==before and m.scene.endswith('w39_resume'),'chapter:pending blocks other purchases')
 saved=m.snapshot();m.restore(saved);check(m.snapshot()==saved,'save:ordinary fields round trip');reset();check(m.q['CorpFounded']==0 and m.q['LineageOrigin']==0 and m.q['Pending']==0,'save:new character defaults independent')
 output=dict(passed=True,checks=checks,groups=groups,new_scenarios=len(rows),features=len(report['features']),cached_events=len(report['cached_events']),binary_sha256=hashlib.sha256(binary).hexdigest(),assets_sha256=hashlib.sha256((ROOT/'assets.json').read_bytes()).hexdigest(),
  author_source_sha256=hashlib.sha256((ROOT/'content39.py').read_bytes()).hexdigest(),features_source_sha256=hashlib.sha256((ROOT/'features39.py').read_bytes()).hexdigest(),test_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
  reserved_random_bridge_executed_in_ARM64=True,all_100_outcomes_per_new_event_checked=True,cached_thresholds_checked=True,duplicate_cost_rewards_and_income_checked=True,age_quotas_and_prerequisites_checked=True,
  Genesis_parser_banking_scene_rendering_save_reload_modeled=True,physical_device_tested=False,ART_tested=False)
 (ROOT/'worlds39_validation.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output),flush=True)
if __name__=='__main__':validate(sys.argv[1])
