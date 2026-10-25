from content import *
from basketball20 import ATTRIBUTES,BUILDS,BADGES
c='seasons_v18';p=lambda k:G(c,k)
for k,v,lo,hi in [('NativeBuild20',0,0,6),('NativeBasketTrain20',0,0,10),('NativeBasketRefresh20',0,0,1),('NativeTakeover20',0,0,1),('BuildChosen20',0,0,1),('BuildError20',0,0,4),('Overall20',45,25,95),('TakeoverCharge20',0,0,100),('TakeoverActive20',0,0,1),('Performance20',0,0,100)]:prop(c,k,v,lo,hi)
for k,label in ATTRIBUTES:prop(c,k+'20',45,25,95)
text(c,'Archetype20','Unchosen balanced prospect')
for k,label in BADGES:text(c,k+'Badge20','Developing')
menu('basket_build20','My Basketball Build',[tile('Attributes and badges',seq(M('life_v18','NativeLifeSync',1),M(c,'NativeBasketRefresh20',1),S('basket_attributes20')),'basketball'),child('Choose play style','basket_archetypes20','basketball'),child('Targeted training','basket_training20','running-shoe'),tile('Takeover',S('basket_takeover20'),'trophy')])
add('basket_attributes20',p('Archetype20'),'Your ratings influence the added school, college and NBA games. Inside scoring and shooting affect points and percentages; playmaking affects assists; defense affects stops, steals and blocks; strength, reach and rebounding affect boards. Speed and stamina affect scoring and conditioning.',[('Badges',S('basket_badges20')),('Training',home('basket_training20')),('Takeover',S('basket_takeover20')),('Back',home('basket_build20'))],icon='basketball',tables=table(**{'Overall':p('Overall20'),**{label.replace(' ','_'):p(k+'20')for k,label in ATTRIBUTES}}))
add('basket_badges20','Basketball badges','A badge develops with its attribute: Bronze 60, Silver 70, Gold 80, Elite 90. Your underlying rating drives the effect, so the same bonus is not counted twice.',[('Back',S('basket_attributes20'))],icon='trophy',tables=table(**{label.replace(' ','_'):p(k+'Badge20')for k,label in BADGES}))
menu('basket_archetypes20','Play Style Archetypes',[tile(label,S('basket_build20_'+str(i)),'basketball')for i,(label,vals)in enumerate(BUILDS,1)])
for i,(label,vals)in enumerate(BUILDS,1):
 add('basket_build20_'+str(i),label,'Choose one starting build for this life. Strengths come with tradeoffs; after choosing, improve the build through training rather than resetting its ratings.',[('Choose this build',seq(M(c,'NativeBuild20',i),S('basket_build_review20'))),('Back',home('basket_archetypes20'))],icon='basketball',tables=table(**{label.replace(' ','_'):str(v)for (_,label),v in zip(ATTRIBUTES,vals)}))
add('basket_build_review20','Build selection',choices=[('Continue',logic([(f'({p("BuildError20")} == 1)',S('basket_locked20')),(f'({p("BuildError20")} == 2)',S('basket_required20'))],seq(M(c,'NativeBasketRefresh20',1),S('basket_attributes20'))))],icon='basketball')
add('basket_locked20','Build already chosen','Your play style is saved for this life. Develop any attribute through targeted practice.',[('Training',home('basket_training20')),('Back',home('basket_build20'))],icon='basketball')
add('basket_required20','Basketball team required','Join your school or college basketball team, or become a professional basketball player, to develop a build.',[('Back','')],icon='basketball')
menu('basket_training20','Targeted Basketball Practice',[tile(label,seq(M(c,'NativeBasketTrain20',i),M(c,'NativeBasketRefresh20',1),S('basket_train_review20')),'running-shoe')for i,(k,label)in enumerate(ATTRIBUTES,1)])
add('basket_train_review20','Practice review',choices=[('Continue',logic([(f'({p("BuildError20")} == 2)',S('basket_required20')),(f'({p("BuildError20")} == 3)',S('practice_limit')),(f'({p("BuildError20")} == 4)',S('sports_hospital'))],S('basket_attributes20')))],icon='running-shoe')
add('basket_takeover20','Takeover','Completed basketball games build takeover energy. At 100, activate a temporary boost for your next full game. It expires after that game and cannot stack or refill by reopening the menu.',[('Activate for next game',seq(M(c,'NativeTakeover20',1),S('basket_attributes20'))),('Back',home('basket_build20'))],icon='trophy',tables=table(Charge=p('TakeoverCharge20'),Active_for_next_game=p('TakeoverActive20')))
for row in rows:
 if row['ScenarioID']==S('playoffs'):
  key='Choice1_AdvancedLogic';old=M(c,'NativePlayoffAdvance',1);row[key]=row[key].replace(old,seq(M(c,'NativeBasketRefresh20',1),old))
# Keep this inside existing school/pro basketball entrances, with current team gates.
for name in ['genesis_v18_seasons_v18','genesis_v18_school_sports18','genesis_v18_pro_sports18']:
 d=json.loads(assets[name]);it=child('My Basketball Build','basket_build20','basketball');it['IsEnabled']='v20-basketball';it['TileID']='v20_'+name+'_build';d['Items'].append(it);assets[name]=json.dumps(d,indent=2)
for name in ['genesis_v18_basket_build20','genesis_v18_basket_archetypes20','genesis_v18_basket_training20']:
 d=json.loads(assets[name]);
 for it in d['Items']:it['IsEnabled']='v20-basketball'
 assets[name]=json.dumps(d,indent=2)
# Basketball practice opens attributes; the existing NFL practice is retained.
for row in rows:
 if row['ScenarioID']==S('sports_train'):
  row['Choice1_Text']='Basketball skill training';row['Choice1_RouteTo']='';row['Choice1_AdvancedLogic']=json.dumps(logic([(f'({p("Level")} != 4)',home('basket_training20'))],logic([(f'({p("Training")} >= 6)',S('practice_limit')),(f'({G("life_v18","Hospital")} == 1)',S('sports_hospital'))],seq(I(c,'Training'),I(c,'Skill',3),S('season')))))
  row['Choice2_Text']='My Basketball Build';row['Choice2_RouteTo']=home('basket_build20');row['Choice2_AdvancedLogic']=''
  row['Choice3_Text']='NFL conditioning / teamwork';row['Choice3_RouteTo']='';row['Choice3_AdvancedLogic']=json.dumps(logic([(f'({p("Level")} != 4)',S('basket_required20')),(f'({p("Training")} >= 6)',S('practice_limit')),(f'({G("life_v18","Hospital")} == 1)',S('sports_hospital'))],seq(I(c,'Training'),I(c,'Skill',3),M('sports_people_v14','NativeFitnessImpact',1),S('season'))))
