"""School entry, valid icons and distinct save-backed fictional crew stories."""
import copy,csv,io,json
from life_rework.content import Author,csv_text,p,scene,seq,set_,inc,text,fun
from playable_repair.school_content import logic
from ui_integrity.content import repair_csv

JOBS=[
 (1,'Warehouse job',1880,100,1200,[
  ('Mixed messages','Mara and Ellis give Luca different roles. He needs one clear answer.','Let Luca choose','Decide for him','Luca speaks up','Luca picks a role he knows. Everyone agrees on the plan.','Luca feels ignored','You choose for Luca. He agrees but keeps his doubts.'),
  ('The wrong crate','The crew finds family keepsakes mixed into the expected haul.','Leave the keepsakes','Take everything','A small kindness','You leave the personal items. Mara respects the decision.','Mara objects','Mara is angry that you took a family’s keepsakes.'),
  ('A missing friend','Ellis is late to the meeting point. Luca wants to leave him.','Wait for Ellis','Leave him behind','All accounted for','Ellis arrives shaken. He thanks you for waiting.','A lasting grudge','Ellis gets back alone. He will remember being left behind.')]),
 (2,'Gallery job',1900,200,2600,[
  ('The collector','Your buyer demands an extra painting. It was never part of the deal.','Keep the agreement','Promise the extra piece','Mara backs you','You keep the original agreement. The crew knows where it stands.','A promise too far','Your new promise puts the whole crew under pressure.'),
  ('A young artist','Luca recognises a painting made by his former teacher.','Hear him out','Mock his concern','Luca feels heard','You listen to Luca. He settles down and stays with the crew.','Luca loses trust','Luca says you do not care about anyone but yourself.'),
  ('A broken frame','Ellis damages a frame. He asks you to blame Luca.','Tell Mara the truth','Cover for Ellis','The truth comes out','Ellis accepts the blame. Mara values your honesty.','The crew divides','Luca knows what happened. Your lie splits the crew.')]),
 (3,'Armoured delivery',1920,350,4500,[
  ('A changed plan','Ellis wants a bigger haul. Mara says the crew is not ready.','Back Mara','Back Ellis','A clear limit','The crew keeps the agreed target. Luca looks relieved.','The pressure rises','Ellis gets his way. The others struggle to keep up.'),
  ('An injured teammate','Luca twists his ankle. He tries to hide the pain.','Check on him','Tell him to keep up','Luca gets help','You share the load. Luca can finish without being left behind.','Luca falls behind','Luca says he cannot rely on you when things get difficult.'),
  ('An argument over money','Ellis wants a bonus before the job is over.','Keep the agreed split','Promise him more','The deal holds','Everyone keeps the same agreement. The crew stays together.','An unfair deal','Mara hears your promise. She expects a better explanation.')]),
 (4,'Casino job',1930,600,7000,[
  ('An old rival','Mara spots someone who betrayed her years ago.','Keep her focused','Encourage revenge','Mara stays calm','Mara puts the crew first. Her old rival never sees the argument.','Old anger returns','Mara loses focus. The crew draws unwanted attention.'),
  ('A costly distraction','Ellis spends part of his own share at a gaming table.','Bring him back','Join his game','Ellis returns','You get Ellis back to the crew. Luca thanks you.','The night gets worse','You both lose time. Mara is furious when you return.'),
  ('A frightened recruit','A new member admits this was a mistake.','Let them leave','Threaten them','A peaceful exit','The recruit leaves quietly. The remaining crew pulls together.','A new enemy','The recruit leaves angry and talks about your threats.')]),
 (5,'Rail payroll job',1880,250,3600,[
  ('The payroll','Luca learns that local workers are waiting on this money.','Hear his concerns','Brush him off','An honest discussion','The crew agrees to a limit. Luca feels able to speak again.','Luca goes quiet','Luca carries on but no longer trusts your judgement.'),
  ('A storm rolls in','Heavy rain leaves the crew tired and short-tempered.','Take a short break','Keep pushing','A calmer crew','Everyone catches their breath. Ellis apologises for snapping.','Tempers flare','Ellis and Luca argue. Mara struggles to keep them together.'),
  ('The final meeting','Mara wants a full account. Ellis wants everyone to leave.','Hear the report','Skip the discussion','Nothing left unsaid','You settle the disagreement before anyone leaves.','Questions remain','Luca leaves with doubts about the job and his share.')])]

def build(base):
 a=Author(base);a.rows=list(csv.DictReader(io.StringIO(base['genesis_life_rework'])));by={r['ScenarioID']:r for r in a.rows}
 def edit(k):return by[scene(k)]
 # New text fields use the existing saved life_rework schema, not a new system.
 schema=list(csv.DictReader(io.StringIO(base['genesis_rework_defaults'])));keys={r['key']for r in schema}
 def string(k,v=''):
  if k not in keys:schema.append(dict(key=k,type='string',value=v,reset_on_ageup='',minimum='',maximum=''));keys.add(k)
 for row in schema:
  if row['key']=='HeistJob1106':row['maximum']='5'
 string('HeistTitle1114','Crew job')
 for stage in range(1,4):
  for suffix in ['Title','Body','Choice1','Choice2','GoodTitle','GoodBody','BadTitle','BadBody']:string('Heist'+str(stage)+suffix+'1114','Crew job')
 for job,title,year,cost,loot,rounds in JOBS:
  if job<=3:offer=edit('heist_offer1106_'+str(job))
  else:
   offer=copy.deepcopy(edit('heist_offer1106_3'));offer['ScenarioID']=scene('heist_offer1106_'+str(job));a.rows.append(offer)
  # Clone the original typed guard tree and keep money/crew/annual checks.
  template=edit('heist_offer1106_3');route=template['Choice1_AdvancedLogic']
  # Rebuild by replacing exact job-specific preparation tokens only.
  route=route.replace('BP_BANK_BALANCE=-350','BP_BANK_BALANCE=-'+str(cost)).replace(':HeistJob1106:=3',':HeistJob1106:='+str(job)).replace(':HeistLoot1106:=4500',':HeistLoot1106:='+str(loot)).replace(' < 1920',' < '+str(year)).replace(' < 350',' < '+str(cost))
  route=route.replace('Armoured delivery in progress.',title+' in progress.')
  effects=[text('HeistTitle1114',title)]
  for stage,details in enumerate(rounds,1):
   for suffix,value in zip(['Title','Body','Choice1','Choice2','GoodTitle','GoodBody','BadTitle','BadBody'],details):effects.append(text('Heist'+str(stage)+suffix+'1114',value))
  # Every leaf that starts the job carries its own story before round one.
  target=scene('heist_round1106_1');route=route.replace(target,seq(*effects,target))
  offer.update(Title=title,Body='Preparation costs $'+str(cost)+'. The crew can earn $'+str(loot)+'. Police may catch you.',Choice1_AdvancedLogic=route,Choice1_RouteTo='')
  offer['Choice2_RouteTo']=scene('heist_jobs1106')
  if job<=3:offer['EmojiString']=['suitcase','film-frames','rescue-helmet'][job-1]
  else:offer['EmojiString']='suitcase'
 for stage in range(1,4):
  r=edit('heist_round1106_'+str(stage));r.update(Title=p('Heist'+str(stage)+'Title1114'),Body=p('Heist'+str(stage)+'Body1114'),Choice1_Text=p('Heist'+str(stage)+'Choice1'+'1114'),Choice2_Text=p('Heist'+str(stage)+'Choice2'+'1114'))
  for prefix,label in [('calm','Good'),('rush','Bad')]:
   r=edit('heist_'+prefix+'1106_'+str(stage)+'_result');r.update(Title=p('Heist'+str(stage)+label+'Title1114'),Body=p('Heist'+str(stage)+label+'Body1114'))
 # Keep current-job resume available while giving the offer page more variety.
 r=edit('heist_jobs1106');r.update(Body='Pick a job. Each crew has different problems. One job each year.',Choice1_Text='Warehouse',Choice2_Text='Gallery',Choice3_Text='More jobs',Choice3_RouteTo=scene('heist_more1114'),Choice3_AdvancedLogic='')
 a.page('heist_more1114','More crew jobs','Choose a job from your era.',[('Armoured delivery',scene('heist_offer1106_3')),('Casino',scene('heist_offer1106_4')),('Rail payroll',scene('heist_offer1106_5')),('Back',scene('heist_jobs1106'))],'suitcase');a.rows[-1]['ExteriorTitle']='Your crew'
 # A mixed result can earn half the pot. Existing repeat-payout guards remain.
 finish=edit('heist_finish1106');logic_=json.loads(finish['Choice1_AdvancedLogic']);failure=logic_['else_when_no_matches']['route_options'][0]['route_to']
 partial=seq(set_('HeistStage1106',0),set_('HeistPayout1111',1),set_('HeistMissionAge1106','<hero:age>'),inc('HeistJobs1106'),set_('HeistLoot1106',fun('div',p('HeistLoot1106'),2)),inc('HeistHeat1106',10),text('HeistLast1106','The crew escaped with half the haul.'),text('JournalMessage','My crew escaped with half the haul.'),inc('JournalSequence'),scene('heist_partial1114'))
 # Insert within the existing final failure leaf so all admission guards stay.
 # Native route strings cannot contain serialized nested logic. Use a typed
 # local decision card after the existing guards instead of nesting JSON.
 def swap(node):
  if isinstance(node,dict):
   for k,v in list(node.items()):
    if k=='route_to'and isinstance(v,str)and ':HeistFailed1111:'in v:node[k]=scene('heist_check_partial1114')
    else:swap(v)
  elif isinstance(node,list):
   for v in node:swap(v)
 swap(logic_);finish['Choice1_AdvancedLogic']=json.dumps(logic_)
 a.page('heist_check_partial1114','A close finish','The crew tries to get everyone home.',[('See what happened',logic([(f'({p("HeistStage1106")} != 4) || ({p("HeistMissionAge1106")} >= <hero:age>) || ({p("HeistAge1106")} != <hero:age>) || ({p("HeistCrew1106")} != 1) || ({p("NativeInPrison1105")} == 1) || (<hero:age> < 18)',scene('heist_current1111')),(f'({p("HeistScore1106")} == 1) && ({p("HeistSkill1106")} + {p("Roll")} > {p("HeistHeat1106")} + 20)',partial)],failure))],'suitcase');a.rows[-1]['ExteriorTitle']='Your crew'
 a.page('heist_partial1114','A narrow escape','The crew escapes with half the haul. Police attention rises. You still need to split the money.',[('Split the pot',scene('heist_split1106'))],'suitcase');a.rows[-1]['ExteriorTitle']='Your crew'
 a.assets['genesis_rework_defaults']=csv_text(schema);a.assets['genesis_life_rework']=csv_text(a.rows)
 # Register the existing canonical school hub in the real native School menu.
 value=base['genesis_feature_containers'];at=value.index('ContainerId,');rows=list(csv.DictReader(io.StringIO(value[at:])))
 if not any(r['ContainerId']=='school_life1114'for r in rows):
  row=dict.fromkeys(rows[0],'');row.update(ContainerId='school_life1114',DisplayName='School life',EntryMenu='School',EntryLabel='School Life',EntryEmoji='native1111/school/01_school_menu_icons_01',EntrySecondLine='Exams bullies clubs and friends',EntryOrder='-1',EntryListID='genesis_v18_school52');rows.append(row)
 for row in rows:
  if row.get('EntryEmoji')=='microphone':row['EntryEmoji']='scene1106-microphone'
 a.assets['genesis_feature_containers']=value[:at]+csv_text(rows)
 # Repair known missing glyphs; preserve native v13/v14/player logo providers.
 replacements={'microphone':'scene1106-microphone','left-arrow':'curved-down-arrow','framed-picture':'film-frames'}
 for name,value in sorted(base.items()):
  if name.startswith('genesis_')and value.startswith('{'):
   doc=json.loads(value);changed=False
   for it in doc.get('Items',[]):
    if it.get('Icon')in replacements:it['Icon']=replacements[it['Icon']];changed=True
   if doc.get('Title')=='Basketball court':doc['Title']='Basketball career';changed=True
   if changed:a.assets[name]=json.dumps(doc,indent=2)
 return repair_csv(a.assets,base)
