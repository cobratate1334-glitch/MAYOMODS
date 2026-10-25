"""Playstyle choices inside the existing basketball, soccer and football hubs."""
from life_rework.content import p,scene,menu,set_,inc,text,seq,logic,fun

SPORTS=[
 ('basket','Basketball','genesis_v9_basketball_v9',11,['Floor general','Three-point specialist','Slasher','Rim protector'],['Pass to the open teammate','Take the open jump shot','Drive into the gap'],[1,0,2],'The help defender steps into the lane. An outside teammate is open.'),
 ('soccer','Soccer','genesis_v8_football_v8',1,['Playmaker','Pressing forward','Wide runner','Ball-winning defender'],['Recycle possession','Play the through ball','Press the receiver'],[1,2,0],'The defence holds a high line. A runner is moving into space.'),
 ('football','American football','genesis_v18_pro_sports18',3,['Field general','Scrambler','Power runner','Lockdown defender'],['Quick pass','Keep the ball and run','Protect the pocket'],[0,2,1],'The defence shows a blitz. The short receiver is uncovered.')]

def build(a,base):
    for sport,title,hub,kind,styles,plays,answers,hint in SPORTS:
        root=scene(sport+'_style1105');back=menu(hub);prefix=sport.title()+'1105'
        for suffix,v,hi in [('Style',0,4),('DrillStep',0,3),('DrillPoints',0,3),('DrillFocus',0,3),('DrillAge',-1,999),('XP',0,100000)]:a.prop(prefix+suffix,v,-1 if v==-1 else 0,hi)
        a.string(prefix+'StyleName','Choose a playstyle')
        guard=((f'({p("SportsEligible"+str(kind))} != 1)',scene('sports_require_'+str(kind))),)
        a.page(sport+'_style1105',title+' playstyle','Choose how you play. Focus drills improve the skills used by your existing sports season.',[
            ('Choose a playstyle',scene(sport+'_styles1105')),('Read the play',scene(sport+'_drill_start1105')),('Training record',scene(sport+'_record1105')),('Back',back)],'trophy',stats=[('Playstyle',p(prefix+'StyleName')),('Training XP',p(prefix+'XP'))])
        for page in range(2):
            options=[]
            for i,name in enumerate(styles[page*3:page*3+3],page*3+1):
                options.append((name,a.outcome(sport+'_choose1105_'+str(i),'Chose the '+name.lower()+' playstyle.',root,[set_(prefix+'Style',i),text(prefix+'StyleName',name)],extra=guard)))
            options.append(('More styles'if page==0 else'Back',scene(sport+'_styles_more1105')if page==0 else root))
            a.page(sport+'_styles1105'if page==0 else sport+'_styles_more1105',title+' · your role','Each role changes the focus of your practice.',options,'trophy')
        a.page(sport+'_drill_start1105','Read the play','Three short plays. Read each clue and choose a response. Your score earns progress in the existing season, once per year.',[
            ('Start drill',a.gate(seq(set_(prefix+'DrillStep',0),set_(prefix+'DrillPoints',0),set_(prefix+'DrillFocus',0),scene(sport+'_drill1_1105')),extra=guard+((f'({p(prefix+"DrillAge")} >= <hero:age>)',scene(sport+'_record1105')),))),('Back',root)],'trophy')
        hints=[hint,
               {'basket':'A defender is closing down the shooter. Your teammate cuts into open space.','soccer':'The opponent receives a loose pass near the touchline. Support is close.','football':'The first receiver is covered. Your blockers still hold the pocket.'}[sport],
               {'basket':'The defender overcommits to the perimeter. The lane opens.','soccer':'The forward run is covered. Keep the ball and rebuild the attack.','football':'Coverage follows the receivers downfield. A running lane is open.'}[sport]]
        for stage in range(1,4):
            options=[]
            for choice,label in enumerate(plays):
                destination=scene(sport+'_drill'+str(stage+1)+'_1105')if stage<3 else scene(sport+'_finish1105')
                effects=[set_(prefix+'DrillStep',stage)]
                if choice==answers[stage-1]:effects.append(inc(prefix+'DrillPoints'))
                route=seq(*effects,destination)
                if choice==answers[stage-1]:
                    focus_moves={'basket':[0,1,2,0],'soccer':[1,2,1,2],'football':[0,1,1,2]}[sport]
                    matches=[index for index,move in enumerate(focus_moves,1)if move==choice]
                    if matches:
                        condition=' || '.join(f'({p(prefix+"Style")} == {index})'for index in matches)
                        route=logic([(condition,seq(*effects,inc(prefix+'DrillFocus'),destination))],route)
                options.append((label,a.gate(route,extra=guard+((f'({p(prefix+"DrillStep")} != {stage-1})',scene(sport+'_record1105')),))))
            options.append(('Leave drill',root))
            a.page(sport+'_drill'+str(stage)+'_1105','Play '+str(stage)+'/3',hints[stage-1],options,'trophy')
        gain=fun('add',fun('add',1,p(prefix+'DrillPoints')),p(prefix+'DrillFocus'))
        effects=[set_(prefix+'DrillAge','<hero:age>'),inc(prefix+'XP',fun('mul',p(prefix+'DrillPoints'),5)),
                 'BP_GFC_MODIFY_PROPERTY=seasons_v18:Skill:='+fun('add','<GFC.seasons_v18.Skill>',gain)]
        # The original basketball build, badges and takeover remain authoritative.
        if sport=='basket':
            effects+=['BP_GFC_MODIFY_PROPERTY=seasons_v18:TakeoverCharge20:='+fun('add','<GFC.seasons_v18.TakeoverCharge20>',fun('mul',p(prefix+'DrillPoints'),10))]
        complete=a.outcome(sport+'_complete1105','Finished the '+title.lower()+' drill. Your score improved your existing season skill.',root,effects,native=131,extra=guard+((f'({p(prefix+"DrillStep")} != 3) || ({p(prefix+"DrillAge")} >= <hero:age>)',scene(sport+'_record1105')),))
        a.page(sport+'_finish1105','Coach’s feedback','You read '+p(prefix+'DrillPoints')+' of three plays correctly. Plays matching your chosen style earned '+p(prefix+'DrillFocus')+' extra training points.',[('Finish drill',complete)],'trophy')
        a.page(sport+'_record1105',title+' training record','Your existing season uses the skill gained here. You can complete one full drill each year.',[('Back',root)],'clipboard',stats=[('Playstyle',p(prefix+'StyleName')),('Last score',p(prefix+'DrillPoints')),('Training XP',p(prefix+'XP')),('Season skill','<GFC.seasons_v18.Skill>')])
        a.add_tile(hub,'Playstyle and coach’s drills',seq(set_('NativeAction',1),root),'trophy','Choose a role; practise reading real game situations')
    # Keep the native NBA-style build and badge/takeover controls in that hub.
    a.add_tile('genesis_v9_basketball_v9','My player build',menu('genesis_v18_basket_build20'),'trophy','Attributes, badges and takeover')
