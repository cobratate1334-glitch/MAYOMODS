"""Native wartime missions, country briefings and constrained command decisions."""
import copy,csv,io,json
from life_rework.content import p,scene,menu,set_,inc,text,seq,logic


def build(a,base):
    for k,v,hi in [('WarFatal1106',0,1),('WarExtraNews1106',0,4),('CommandActive1106',0,1),('CommandBudget1106',100,1000),('CommandIndustry1106',30,100),('CommandReadiness1106',25,100),('CommandLogistics1106',30,100),('CommandStability1106',60,100),('CommandCivilianHarm1106',0,1000000),('CommandTurnAge1106',-1,999),('CommandBuildAge1106',-1,999),('CommandTerritories1106',0,20),('CommandTarget1106',0,8),('CommandCompleted1106',0,255),('WorldEncounter1106',0,2),('WarMagazine1106',5,10),('WarAmmo1106',5,10)]:a.prop(k,v,-1 if v==-1 else 0,hi)
    for key,val in [('WarFlag1106',''),('WarSideName','Neutral'),('WarKit1106','No wartime deployment.'),('WarGovernment1106','Civil government'),('WarLeader1106',''),('WarCommandReport1106','No campaign ordered.'),('WarHeadline1106',''),('WarExtraBody1106','')]:a.string(key,val)
    home=scene('war_hub1106');duty=menu('genesis_v9_v13_duty')
    a.page('war_hub1106',p('WarName'),p('History')+'\n\nYour country: '+p('Country')+'. Front: '+p('Front')+'.',[
        ('Service and missions',scene('war_service1106')),('Country, equipment and news',scene('war_country1106')),('Government and command',scene('command_home1106')),('Back to military duties',duty)],'v13-world-war',stats=[('Year',p('Year')),('Side',p('WarSideName')),('Unit losses',p('Casualties'))])
    a.edit('war_hub1106')['BigImageString']=p('WarFlag1106')
    a.page('war_country1106','Your country at war',p('WarGovernment1106')+'. '+p('WarLeader1106')+'\n\n'+p('WarKit1106')+'\n\nThe country briefings follow historical entry dates. Your decisions during a campaign can create a different outcome.',[
        ('Recruitment and propaganda',scene('war_propaganda1106')),('Historical headlines',scene('war_news1106')),('Back',home)],'newspaper')
    a.edit('war_country1106')['BigImageString']=p('WarFlag1106')
    a.page('war_news1106',p('NewsTitle1105'),p('NewsBody1105'),[('Country briefing',scene('war_country1106')),('Back',home)],'newspaper')
    eligible=((f'({p("War")} == 0) || ({p("WarSide")} == 0)',scene('war_peace')),(f'({p("NativeInPrison1105")} == 1)',scene('locked')))
    mine=a.gate(set_('NativeMinefield1106',1),adult=True,extra=eligible+((f'({p("NativeMilitary")} != 1) || ({p("WarNativeMissionAge1106")} >= <hero:age>)',scene('war_mine_wait1106')),))
    a.page('war_service1106','Service at the front','Accept a call-up to enter real military service. Original military deployments include the game’s playable minefield, with injury and death risks. The added trench and flight missions keep ammunition, supplies and losses.',[
        ('Answer the call-up',scene('war_draft')),('Play the original minefield',mine),('Trench or air mission',scene('war_missions1106')),('Back',home)],'rescue-helmet')
    a.page('war_mine_wait1106','No deployment available','You must be serving in your country’s military during an active war. You can request one native minefield deployment per age.',[('Back to service',scene('war_service1106'))],'rescue-helmet')
    a.page('war_missions1106','Choose a mission','These missions use native game popups. Read the changing briefing, manage ammunition and protect your unit. An exposed position can leave you wounded or killed.',[
        ('Trench patrol',scene('trench_start1106')),('Aircraft sortie',scene('flight_start1106')),('Existing patrol map',scene('map_start')),('Back',home)],'rescue-helmet')
    def mission_gate(target,mode,extra=()):
        return a.gate(target,adult=True,extra=eligible+((f'({p("Deployed")} != 1) || ({p("NativeMilitary")} != 1)',scene('war_draft')),)+tuple(extra))
    for mode,title in [('trench','Trench patrol'),('flight','Aircraft sortie')]:
        for key,v,hi in [('Stage',0,3),('Score',0,3),('Age',-1,999)]:a.prop(mode.title()+key+'1106',v,-1 if v==-1 else 0,hi)
        for step in range(1,4):a.prop(mode.title()+'Safe'+str(step)+'1106',0,0,2)
        if mode=='trench':body='Your unit must cross three positions. The briefing identifies the dangerous lane. Your rifle, magazine and field equipment follow your country and year.'
        else:body='Take off in a period aircraft. Choose a safe flight path from the observer’s report, keep fuel in reserve and bring your crew home. These are propeller aircraft, not modern jets.'
        start=mission_gate(seq(set_(mode.title()+'Stage1106',0),set_(mode.title()+'Score1106',0),set_(mode.title()+'Age1106','<hero:age>'),set_('WarAmmo1106',p('WarMagazine1106')),scene(mode+'_round1106_1')),mode,((f'({p(mode.title()+"Age1106")} >= <hero:age>)',scene('war_mission_wait1106')),))
        a.page(mode+'_start1106',title,body,[('Read the briefing and begin',start),('Back',scene('war_missions1106'))],'rescue-helmet',stats=[('Equipment',p('WarKit1106')),('Supplies',p('WarSupplies'))])
        for stage in range(1,4):
            safe=p(mode.title()+'Safe'+str(stage)+'1106');next_=scene(mode+'_round1106_'+str(stage+1))if stage<3 else scene(mode+'_debrief1106')
            options=[]
            guard=((f'({p(mode.title()+"Stage1106")} != {stage-1}) || ({p(mode.title()+"Age1106")} != <hero:age>)',scene('war_mission_wait1106')),)
            for lane,label in enumerate(['Left approach','Centre approach','Right approach']):
                changes=[set_(mode.title()+'Stage1106',stage),inc('WarSupplies',-3)]
                if mode=='trench':changes+=[inc('WarAmmo1106',-2),set_('NativeAction',201)]
                else:changes+=[set_('NativeAction',203)]
                success=a.outcome(mode+'_safe1106_'+str(stage)+'_'+str(lane),'Your unit used the clear approach and reached cover. The crew stayed together.',next_,changes+[inc(mode.title()+'Score1106'),inc('WarIntel',2)],extra=guard)
                injury=a.outcome(mode+'_hit1106_'+str(stage)+'_'+str(lane),'Incoming fire caught the exposed approach. You were wounded and one member of your unit was lost. The survivors reached cover.',next_,changes+[inc('Squad',-1),inc('Casualties')],native=14,extra=guard)
                fatal=seq(*changes,inc('Casualties'),scene('war_fatal1106'))
                danger=logic([(f'({p("Roll")} < 4) || (({p("Roll")} < 8) && ({p("WarTraining")} < 60))',fatal)],injury)
                options.append((label,mission_gate(logic([(f'({safe} == {lane})',success)],danger),mode,guard+(((f'({p("WarAmmo1106")} < 2)',scene(mode+'_pause1106_'+str(stage))),)if mode=='trench'else()))))
            retreat=a.outcome(mode+'_withdraw1106_'+str(stage),'Withdrew the unit before further losses. Supplies already used were not recovered.',home,[set_(mode.title()+'Stage1106',0)],extra=guard)
            if mode=='trench':
                pause=mode+'_pause1106_'+str(stage);reload_=a.outcome('trench_reload1106_'+str(stage),'Reloaded your period rifle while the unit covered you. The ammunition came from your supplies.',scene(mode+'_round1106_'+str(stage)),[set_('WarAmmo1106',p('WarMagazine1106')),inc('WarSupplies',-2)],extra=guard+((f'({p("WarSupplies")} < 2)',scene('war_mission_wait1106')),),quota=('TrenchReload1106',3))
                a.page(pause,'Behind cover','Reload from your supplies or withdraw. Reloading costs two supply points and does not advance your position.',[('Reload',reload_),('Withdraw',retreat),('Return to position',scene(mode+'_round1106_'+str(stage)))],'rescue-helmet');options.append(('Reload or withdraw',scene(pause)))
            else:options.append(('Withdraw and return',retreat))
            a.page(mode+'_round1106_'+str(stage),title+' · '+str(stage)+'/3',p(mode.title()+'Hint'+str(stage)+'1106')+'\n\nRead the observer’s report before choosing. A wrong approach risks injury or death.',options,'rescue-helmet',stats=[('Unit members',p('Squad')),('Ammunition',p('WarAmmo1106')),('Supplies',p('WarSupplies'))])
            a.string(mode.title()+'Hint'+str(stage)+'1106','The observer has not reported yet.')
        a.page(mode+'_debrief1106','Back from the mission','Your unit returns with the outcome of all three positions. Losses remain on the service record.',[
            ('File the mission report',a.outcome(mode+'_finish1106','Filed the mission report. Your training, survivors and losses were recorded in your service history.',home,[set_(mode.title()+'Stage1106',0),inc('WarTour'),inc('WarTraining',3),inc('WarMedals','<function:clamp:<function:sub:'+p(mode.title()+'Score1106')+':2>:0:1>')],extra=((f'({p(mode.title()+"Stage1106")} != 3)',scene('war_mission_wait1106')),)))],'memo',stats=[('Clear approaches',p(mode.title()+'Score1106')),('Unit losses',p('Casualties'))])
    a.page('war_mission_wait1106','Mission record closed','This mission is already underway or has been used this year. You cannot replay an old choice for another reward.',[('Back',home)],'memo')
    a.page('war_fatal1106','Killed during the mission','Your unit came under heavy fire. Your wounds were fatal. Continue to the game’s original death and legacy screens.',[('Continue',set_('WarFatal1106',1))],'rescue-helmet');a.edit('war_fatal1106')['HasDismissButton']='false'
    a.page('war_propaganda1106','The home front','Recruitment posters, newspapers and broadcasts try to shape public opinion. Nazi and fascist propaganda also spread racism, censorship and claims of inevitable victory. Imperial Japan’s government demands sacrifice. Allied broadcasts promote enlistment, rationing and resistance. Check claims against the situation on your own front.',[
        ('Verify a report with other sources',a.outcome('war_verify1106','Compared the claims with reports from the front. You found exaggerated successes and improved the quality of your briefing.',home,[inc('WarIntel',7),inc('WarTraining',2)],quota=('WarNews1106',2))),
        ('Help with civilian relief',a.outcome('war_relief1106','Helped families affected by fighting and rationing. Your community trusted you more, but the relief effort used supplies.',home,[inc('WarSupplies',-5),inc('WarMorale',5)],native=111,quota=('WarRelief1106',2))),('Back',home)],'newspaper')
    command(a,home)
    for name in ['genesis_v9_v13_duty','genesis_v9_v13_government']:
        a.add_tile(name,'Wartime country and campaigns',home,'v13-world-war','Country briefings, missions and command decisions')
    # Historical news is a retrospective for the reached year, not a claim
    # that fictional campaign choices rewrite recorded real-world death counts.
    a.page('war_extra_news1106',p('WarHeadline1106'),p('WarExtraBody1106'),[('Continue','')],'newspaper');a.edit('war_extra_news1106')['BigImageString']=p('WarFlag1106')
    annual=list(csv.DictReader(io.StringIO(a.assets['genesis_rework_annual1105'])))
    r=copy.deepcopy(a.edit('war_extra_news1106'));r.update(ScenarioID=scene('annual_war_extra1106'),Filter='[gfc.life_rework.WarExtraNews1106>0]',IsAgeUpScenario='true',HasDismissButton='false');annual.append(r)
    a.assets['genesis_rework_annual1105']=__import__('life_rework.content',fromlist=['csv_text']).csv_text(annual)
    encounters(a,home)


def command(a,home):
    a.page('command_home1106',p('WarGovernment1106'),'Command role: '+p('WarLeader1106')+'.\n\nManage production, readiness and supply before ordering an offensive. This is an alternate-history command record for your country; your ordinary life and job remain available.',[
        ('Take command / review resources',scene('command_start1106')),('Economy and mobilisation',scene('command_economy1106')),('Campaign map',scene('command_targets1106')),('Back',home)],'classical-building',stats=[('Treasury',p('CommandBudget1106')),('Readiness',p('CommandReadiness1106')),('Logistics',p('CommandLogistics1106')),('Public stability',p('CommandStability1106'))])
    guard=((f'({p("War")} == 0) || ({p("WarSide")} == 0) || (<hero:age> < 18) || ({p("NativeInPrison1105")} == 1)',scene('locked')),)
    a.page('command_start1106','Your wartime command','Taking command starts a saved strategic campaign. Your leader’s title, available offensives and equipment follow your country and the current year. Failed offensives cost forces, supplies and public stability.',[
        ('Take command',a.outcome('command_accept1106','Took responsibility for a wartime command. Your cabinet now expects you to manage production and protect the civilian population.',scene('command_home1106'),[set_('CommandActive1106',1)],extra=guard+((f'({p("CommandActive1106")} == 1)',scene('command_already1106')),))),('Back',home)],'classical-building')
    a.page('command_already1106','Your cabinet is waiting','You already hold this command. Review resources or choose a campaign.',[('Command office',scene('command_home1106'))],'classical-building')
    a.page('command_economy1106','Build the war effort','Each plan takes a year of cabinet work. Industry helps production; readiness and logistics determine whether an army can sustain an offensive. Treasury is your campaign budget, separate from personal savings.',[
        ('Invest in production · 20',a.outcome('command_industry1106','Funded production and worker training. Industry and the next year’s income improved.',scene('command_home1106'),[inc('CommandBudget1106',-20),inc('CommandIndustry1106',15)],extra=((f'({p("CommandActive1106")} != 1) || ({p("CommandBudget1106")} < 20)',scene('command_short1106')),),quota=('CommandPlan1106',2))),
        ('Train and supply units · 20',a.outcome('command_train1106','Funded training, transport and maintenance. Your units became more ready to serve and easier to supply.',scene('command_home1106'),[inc('CommandBudget1106',-20),inc('CommandReadiness1106',12),inc('CommandLogistics1106',15)],extra=((f'({p("CommandActive1106")} != 1) || ({p("CommandBudget1106")} < 20)',scene('command_short1106')),),quota=('CommandPlan1106',2))),
        ('Civilian food and hospitals · 15',a.outcome('command_relief1106','Protected food supplies and hospitals. Civilian suffering eased and public stability improved.',scene('command_home1106'),[inc('CommandBudget1106',-15),inc('CommandStability1106',12)],extra=((f'({p("CommandActive1106")} != 1) || ({p("CommandBudget1106")} < 15)',scene('command_short1106')),),quota=('CommandPlan1106',2))),('Back',scene('command_home1106'))],'money-bag')
    a.page('command_short1106','The cabinet cannot approve this','Take command first and check the budget. Your treasury or preparation is too low for the order.',[('Back to command',scene('command_home1106'))],'memo')
    targets=[('Poland',1939,'Germany',1,45),('France',1940,'Germany',2,60),('North Africa',1940,'Italy',3,50),('Pacific campaign',1941,'Japan',4,65),('Normandy liberation',1944,'United States',5,60),('Normandy liberation',1944,'United Kingdom',5,60),('Eastern Front',1941,'Russia',6,70),('Eastern Front',1941,'Germany',8,70),('Western Front',1914,'Germany',7,45),('Western Front',1914,'France',7,45),('Western Front',1914,'United Kingdom',7,45)]
    options=[]
    for idx,(target,year,country,code,difficulty)in enumerate(targets):
        bit=1<<code;a.prop('CommandWon'+str(code)+'1106',0,0,1)
        key='command_offer1106_'+str(idx);options.append((target,scene(key),country,year))
        checks=((f'({p("CommandActive1106")} != 1) || ({p("CommandBudget1106")} < 25) || ({p("CommandReadiness1106")} < {difficulty}) || ({p("CommandLogistics1106")} < {difficulty-10})',scene('command_short1106')),(f'({p("Year")} < {year}) || ({p("CommandTurnAge1106")} >= <hero:age>) || ({p("CommandWon"+str(code)+"1106")} == 1)',scene('command_wait1106')),(f'({p("War")} == 0)',scene('war_peace')))
        win=a.outcome(key+'_win','The operation achieved its objective, at a cost. Your forces now hold '+target+'. Casualties and civilian harm were added to the campaign record.',scene('command_home1106'),[set_('CommandTurnAge1106','<hero:age>'),set_('CommandWon'+str(code)+'1106',1),inc('CommandTerritories1106'),inc('CommandBudget1106',-25),inc('CommandReadiness1106',-15),inc('CommandLogistics1106',-12),inc('CommandCivilianHarm1106',120),inc('Casualties',60),text('WarCommandReport1106','Objective secured: '+target+'. Forces need rest and resupply before the next operation.'),set_('NativeAction',202)],extra=checks)
        lose=a.outcome(key+'_loss','The offensive stalled. Your forces withdrew from '+target+' after heavy losses. The cabinet faced public criticism.',scene('command_home1106'),[set_('CommandTurnAge1106','<hero:age>'),inc('CommandBudget1106',-25),inc('CommandReadiness1106',-25),inc('CommandLogistics1106',-20),inc('CommandStability1106',-15),inc('CommandCivilianHarm1106',180),inc('Casualties',140),text('WarCommandReport1106','Failed offensive: '+target+'. Public stability and readiness fell.'),set_('NativeAction',202)],extra=checks)
        launch=logic([(f'({p("CommandReadiness1106")} + {p("CommandLogistics1106")} + {p("WarIntel")} / 4 + {p("Roll")} >= {difficulty*2+25})',win)],lose)
        a.page(key,target,'This operation requires readiness '+str(difficulty)+', logistics '+str(difficulty-10)+' and treasury 25. Operations are limited to one per year. It can fail, cause casualties and harm civilians.',[('Authorize the operation',a.gate(launch,adult=True,extra=guard)),('Back',scene('command_targets1106'))],'v13-world-war')
    # Country/year filtering happens on the native menu/scenario entry, not by
    # exposing every nation's invasions to one character.
    for page in range(4):
        choices=[]
        for label,target,country,year in options[page*3:page*3+3]:choices.append((label,a.gate(target,adult=True,extra=((f'({p("Year")} < {year})',scene('command_wait1106')),))))
        choices.append(('More fronts'if page<3 else'Back',scene('command_targets1106_'+str(page+1))if page<3 else scene('command_home1106')))
        a.page('command_targets1106'if page==0 else'command_targets1106_'+str(page),'Campaign map',p('WarCommandReport1106')+'\n\nYour country only authorizes its own historical fronts. Preparation and the outcome are saved.',choices,'earth')
        for i,(_,target,country,year)in enumerate(options[page*3:page*3+3],1):
            # String equality is handled by the native country permit bridge;
            # avoid putting unsupported string comparisons in numeric expressions.
            key=target.rsplit('.',1)[1];a.prop('CommandPermit'+str(page*3+i-1)+'1106',0,0,1)
            row=a.edit('command_targets1106'if page==0 else'command_targets1106_'+str(page));d=json.loads(row['Choice'+str(i)+'_AdvancedLogic']);d['cases'].insert(0,{'if':{'expression':'('+p('CommandPermit'+str(page*3+i-1)+'1106')+' != 1)'},'then':{'route_options':[{'route_to':scene('command_country1106')}]}});row['Choice'+str(i)+'_AdvancedLogic']=json.dumps(d)
            offer=a.edit(key)
            # Defense in depth: an old offer cannot authorize another country's front.
            d=json.loads(offer['Choice1_AdvancedLogic']);d['cases'].insert(0,{'if':{'expression':'('+p('CommandPermit'+str(page*3+i-1)+'1106')+' != 1)'},'then':{'route_options':[{'route_to':scene('command_country1106')}]}});offer['Choice1_AdvancedLogic']=json.dumps(d)
    for key,title,body in [('command_country1106','A different country’s front','That operation belongs to a different country. Your own fronts follow your current country and the year.'),('command_wait1106','No operation approved','That operation has not opened, has already been completed or you have already ordered an offensive this year. Use this time to rebuild and resupply.')]:a.page(key,title,body,[('Back to command',scene('command_home1106'))],'memo')


def encounters(a,home):
    a.page('world_encounter1106','At the edge of the street','A man asks whether you can spare money for food. He looks exhausted and unsure whether you will stop.',[
        ('Give 5 for a meal',a.filtered('[finance.bankBalance<5]',scene('funds'),a.outcome('world_meal1106','Gave the man money for a meal. He thanked you and headed towards a nearby food stall.','',['BP_BANK_BALANCE=-5'],native=111))),
        ('Point him towards local help',a.outcome('world_help1106','Helped the man find a local relief service. He thanked you for taking the time.','',[],native=111)),('Walk past',a.outcome('world_pass1106','Walked past without stopping. The man continued asking passers-by.','',[]))],'bread')
    a.page('world_hate_group1106','A disturbing procession','Men in white hoods are gathering nearby. You recognise the Ku Klux Klan. Neighbours are frightened; some people are trying to get children indoors.',[
        ('Alert the authorities and leave',a.outcome('world_report_hate1106','Reported the threatening gathering and moved away with neighbours. Your family appreciated your concern for their safety.','',[],native=111)),
        ('Help neighbours reach safety',a.outcome('world_neighbours1106','Helped neighbours get away from the gathering. You stayed with the people who were frightened until the street was clear.','',[],native=111)),('Leave the area',a.outcome('world_leave_hate1106','Left the area before the threatening procession reached your street.','',[]))],'newspaper')
    annual=list(csv.DictReader(io.StringIO(a.assets['genesis_rework_annual1105'])))
    for event,key in [(1,'world_encounter1106'),(2,'world_hate_group1106')]:
        r=copy.deepcopy(a.edit(key));r.update(ScenarioID=scene('annual_world_encounter1106_'+str(event)),Filter='[gfc.life_rework.WorldEncounter1106='+str(event)+']',IsAgeUpScenario='true',HasDismissButton='false');annual.append(r)
    a.assets['genesis_rework_annual1105']=__import__('life_rework.content',fromlist=['csv_text']).csv_text(annual)
