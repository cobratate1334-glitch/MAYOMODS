"""Existing supervision and studio flows, and a short fictional mission puzzle."""
def build(a,base):
    from life_rework.content import p,scene,menu,seq,set_,inc,text,logic
    # Keep the real parole officer/check-in/warrant actions, not a second sentence.
    parole=menu('genesis_v9_v11_parole_v11')
    a.page('parole_plan','Life under supervision','Check in with your officer before aging up. Home study and exercise use your existing supervision programme. A missed check-in can trigger the normal arrest and court process.',[
      ('Officer and check-in','BP_GFC_MODIFY_PROPERTY=parole_v11:NativeParoleSync41:=0>>BP_GFC_MODIFY_PROPERTY=parole_v11:NativeParoleSync41:=1>>scenario.activitiesV18.w41_parole_status'),
      ('Home study and exercise','scenario.activitiesV18.w41_home'),('Home health visit',scene('parole_travel')),('Back',parole)],'house',stats=[('Years remaining','<GFC.parole_v11.Remaining>'),('Last check-in age','<GFC.parole_v11.LastCheckAge>'),('Warrant','<GFC.parole_v11.Warrant41>')])
    a.prop('TravelPermitAge',-1,-1,999)
    permit=a.outcome('parole_permission','Had an approved home health visit. Your health improved and supervision continues.',parole,[set_('TravelPermitAge','<hero:age>')],native=16,extra=(('(<GFC.parole_v11.Active> != 1)',scene('parole_inactive')),('(<GFC.parole_v11.Warrant41> == 1) || (<GFC.parole_v11.LastCheckAge> != <hero:age>)',scene('parole_check_first'))),quota=('SupervisionRequest',1))
    a.page('parole_travel','Ask for a home health visit','Your officer checks your current check-in and warrant record before arranging an approved home health visit.',[('Ask the officer',permit),('Back',scene('parole_plan'))],'police-car')
    a.page('parole_inactive','No active supervision','You do not have an active supervision order.',[('Back',parole)],'house')
    a.page('parole_check_first','Speak to your officer','Complete your check-in and resolve any warrant before requesting permission.',[('Officer and check-in','scenario.activitiesV18.w41_parole_status'),('Back',parole)],'police-car')
    import json
    d=json.loads(base['genesis_v9_v11_parole_v11']);d['Title']='Parole and home supervision';d['Items'].insert(0,a.tile('My supervision plan','parole_plan','house','Check-ins, home routines and appointments'));a.assets['genesis_v9_v11_parole_v11']=json.dumps(d,indent=2)
    # The existing studio retains native projects, record releases and royalties.
    studio=menu('genesis_music_studio_hub')
    for k,v in [('StudioPractice',0),('StudioStress',20)]:a.prop(k,v)
    for key,label,body,skill,stress in [('rehearse','Rehearse with the band','Rehearsed the arrangement. Your next session will be better prepared.',12,3),('listen','Review the mix','Listened to the mix and wrote clear revision notes.',8,-2),('rest','Rest your voice','Rested your voice and came back calmer.',2,-12)]:
        route=a.outcome('studio_'+key,body,studio,[inc('StudioPractice',skill),inc('StudioStress',stress),'BP_GFC_MODIFY_PROPERTY=music_studio:Skill:=<function:add:<GFC.music_studio.Skill>:3>','BP_GFC_MODIFY_PROPERTY=music_studio:Quality:=<function:add:<GFC.music_studio.Quality>:'+str(skill)+'>'],native=10,adult=True,extra=(('(<GFC.music_studio.Started> != 1)',scene('locked')),),quota=('StudioWork',5))
        # No invented bridge property: practice uses the existing native studio
        # panel for recording; this preparation is explicitly separate.
        route=json.loads(json.dumps(route).replace('BP_GFC_MODIFY_PROPERTY=music_studio:NativeStudioApply:=1>>',''))
        a.page('studio_'+key,label,'Prepare here, then record and release through your existing studio.',[('Do this',route),('Back',studio)],'musical-notes')
    a.page('studio_sessions','Between recording sessions','Prepare, listen and rest. Your records, royalty payments and recording work stay in the original studio.',[('Rehearse',scene('studio_rehearse')),('Review the mix',scene('studio_listen')),('Rest your voice',scene('studio_rest')),('Back to studio',studio)],'musical-notes')
    d=json.loads(a.assets.get('genesis_music_studio_hub',base['genesis_music_studio_hub']));d['Items'].append(a.tile('Between sessions','studio_sessions','musical-notes','Preparation and recovery'));a.assets['genesis_music_studio_hub']=json.dumps(d,indent=2)
    # A small map puzzle, kept in the original deployment hub. The saved roll
    # chooses a blocked lane; cover/intel/supplies have real costs and injuries.
    a.prop('MapStage',0,0,3);a.prop('MapAge',-1,-1,999);a.prop('MapScore',0,0,3)
    guard=((f'({p("War")} == 0) || ({p("WarSide")} == 0) || ({p("Deployed")} != 1) || (({p("NativeMilitary")} != 1) && ({p("NativePresident")} != 1))',scene('war_draft')),(f'({p("MapAge")} >= <hero:age>)',scene('war_record')))
    for stage in range(1,4):
        a.prop('MapBlocked'+str(stage),0,0,2);a.string('MapWarning'+str(stage),'Read the briefing again.')
        choices=[]
        for lane,label in enumerate(['Left lane','Centre lane','Right lane']):
            hit=f'({p("MapBlocked"+str(stage))} == {lane})'
            parent=scene('map_'+str(stage+1))if stage<3 else scene('map_result')
            effects=[set_('MapStage',stage),inc('WarSupplies',-5)]
            if stage==3:effects+=[set_('MapAge','<hero:age>'),inc('WarTour')]
            safe=a.outcome(f'map_{stage}_{lane}_safe','Crossed a clear lane and brought the patrol to cover.',parent,effects+[inc('MapScore'),inc('WarIntel',3)],adult=True,extra=guard+((f'({p("MapStage")} != {stage-1})',scene('war_record')),))
            bad=a.outcome(f'map_{stage}_{lane}_hit','The patrol met incoming fire and withdrew. One unit member was lost and you were injured.',parent,effects+[inc('Squad',-1),inc('Casualties')],native=14,adult=True,extra=guard+((f'({p("MapStage")} != {stage-1})',scene('war_record')),))
            choices.append((label,logic([(hit,bad)],safe)))
        a.page('map_'+str(stage),'Patrol map · '+str(stage)+'/3','Choose a lane to reach cover. '+p('MapWarning'+str(stage))+' A wrong choice costs supplies and can cause an injury.',choices+[('Withdraw',scene('war_record'))],'rescue-helmet',stats=[('Supplies',p('WarSupplies')),('Patrol members',p('Squad'))])
    a.page('map_start','A patrol under fire','A short, fictional map challenge. Read each briefing, choose a lane and get the patrol to cover. Losses and supplies carry into your service record.',[('Begin patrol',a.gate(seq(set_('MapStage',0),set_('MapScore',0),scene('map_1')),adult=True,extra=guard)),('Back',scene('war_briefing'))],'rescue-helmet')
    a.page('map_result','Patrol debrief','Your patrol is back. Clear crossings, casualties and supplies are saved in your service record.',[('Continue',scene('war_record'))],'rescue-helmet',stats=[('Clear crossings',p('MapScore')),('Unit casualties',p('Casualties'))])
    d=json.loads(a.assets['genesis_v9_v13_duty']);d['Items'].append(a.tile('Patrol map','map_start','rescue-helmet','Three rounds; saved losses and supplies'));a.assets['genesis_v9_v13_duty']=json.dumps(d,indent=2)
    d=json.loads(base['genesis_v9_v13_government']);d['Items'].insert(0,a.tile('Wartime cabinet','war_cabinet','classical-building','Relief, diplomacy and deployments'));d['Items'].append(a.tile('Your era','era_guide','calendar','Technology, style and history'));a.assets['genesis_v9_v13_government']=json.dumps(d,indent=2)
