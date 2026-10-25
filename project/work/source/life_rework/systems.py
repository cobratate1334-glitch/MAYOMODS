"""Native school grades, Fight Club stats, historical service and receipts."""
from native_hooks import h
from life_rework.history import context,WW1,WW2
from native_v42.patch_native42 import ref,ref_init

def stat(b,method,score):
    return h.load_game()+'\nldr x0,[x8,#0x28]\ncbz x0,finish\n'+f'mov w1,#{score}\nmov x2,xzr\nbl {method:#x}\n'

def hooks(b):
    owner='life_rework';year=b.old['v45_current_year']['stub']
    # Current residence supplies the actual country for historical events.
    s=b.ctx(owner)+b.text('Country','')+b.text('CountryCode','')+b.set('SchoolEligible',0)+b.set('NativeMilitary',0)+b.set('NativePresident',0)+b.set('FightJoined',0)
    s+=f'bl {year:#x}\nmov w26,w0\n'+b.put('Year','w26')
    s+=h.load_game()+'\nldr x27,[x8,#0x28]\ncbz x27,finish\nmov x0,x27\nmov x1,xzr\nbl 0x2c38288\ncbz x0,rework_country_done\nmov x26,x0\nldr x22,[x26,#0x90]\n'+b.textptr('CountryCode','x22')+'mov x0,x26\nmov x1,xzr\nbl 0x2a27280\ncbz x0,rework_country_done\nmov x1,xzr\nbl 0x251f4a4\nmov x22,x0\n'+b.textptr('Country','x22')+'rework_country_done:\n'
    s+=h.load_occupation(end='rework_occ_done')+'\nldr w9,[x8,#0x10]\ncmp w9,#1\nb.ne rework_occ_military\n'+b.set('SchoolEligible',1)+'b rework_occ_done\nrework_occ_military:\ncmp w9,#3\nb.ne rework_occ_president\n'+b.set('NativeMilitary',1)+'b rework_occ_done\nrework_occ_president:\ncmp w9,#6\nb.ne rework_occ_done\nldr x8,[x8,#0x28]\ncbz x8,rework_occ_done\nldr w9,[x8,#0x10]\ncmp w9,#1\nb.ne rework_occ_done\nldr w9,[x8,#0x20]\ncmp w9,#4\nb.ne rework_occ_done\n'+b.set('NativePresident',1)+'rework_occ_done:\n'
    # Verified Life.FightClub backing field; do not create a fighter on read.
    s+=h.load_game()+'\nldr x8,[x8,#0x20]\ncbz x8,finish\nldr x0,[x8,#0x6f0]\ncbz x0,rework_fight_done\nmov x1,xzr\nbl 0x2abfe88\nand w24,w0,#1\n'+b.put('FightJoined')+'rework_fight_done:\n'
    for kind in range(1,11):s+=f'mov w0,#{kind}\nbl {b.old["current_eligibility19"]["stub"]:#x}\nmov w24,w0\n'+b.put('SportsEligible'+str(kind))
    s+=f'mov w0,#2\nbl {b.old["current_eligibility19"]["stub"]:#x}\nmov w25,w0\nmov w0,#7\nbl {b.old["current_eligibility19"]["stub"]:#x}\norr w24,w25,w0\n'+b.put('SportsEligible11')
    s+=b.get('RollAge','w25')+'cmp w25,w23\nb.ge rework_snapshot_done\n'+b.rng(100,'w24')+b.put('Roll')+b.put('RollAge','w23')+'rework_snapshot_done:\nb finish'
    snap=b.routine('life_rework_snapshot',s)
    # The history dispatch uses current year and the real country name. Its
    # facts are data; it never gives a modern country fictional historical arms.
    countries=sorted(set(WW1)|set(WW2));s=b.ctx(owner)+b.get('Year','w25')+b.set('War',0)+b.set('WarSide',0)
    s+=b.string('Country')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\ncbz x0,finish\nmov x8,x0\n'
    for i,country in enumerate(countries):s+=h.compare_key(country,'rework_country_'+str(i),'rework_country_next_'+str(i))+'\nrework_country_next_'+str(i)+':\n'
    s+='b rework_history_neutral\n'
    for i,country in enumerate(countries):
        s+='rework_country_'+str(i)+':\n'
        for war,years in [(1,(1914,1918)),(2,(1939,1945))]:
            s+=f'cmp w25,#{years[0]}\nb.lt rework_history_{i}_{war}_next\ncmp w25,#{years[1]}\nb.gt rework_history_{i}_{war}_next\n'
            # Explicit annual rows handle entry dates, side changes and Normandy.
            for y in range(years[0],years[1]+1):
                row=context(y,country);s+=f'cmp w25,#{y}\nb.ne rework_history_{i}_{war}_{y}_next\n'
                for k,v in row.items():s+=b.set(k,v)if isinstance(v,int)else b.text(k,v)
                s+=f'b finish\nrework_history_{i}_{war}_{y}_next:\n'
            s+=f'rework_history_{i}_{war}_next:\n'
        s+='b rework_history_neutral\n'
    s+='rework_history_neutral:\n'
    for war,lo,hi in [(1,1914,1918),(2,1939,1945)]:
        s+=f'cmp w25,#{lo}\nb.lt neutral_war_{war}_next\ncmp w25,#{hi}\nb.gt neutral_war_{war}_next\n'
        for k,v in context(lo,'').items():s+=b.set(k,v)if isinstance(v,int)else b.text(k,v)
        s+=f'b finish\nneutral_war_{war}_next:\n'
    for k,v in context(2026,'').items():s+=b.set(k,v)if isinstance(v,int)else b.text(k,v)
    s+='b finish';history=b.routine('life_rework_historical_context',s)
    # The map hint and blocked lane are generated together, once from the
    # saved per-age roll, so reopening cannot change the puzzle answer.
    m=b.ctx(owner)+b.get('Roll','w25')
    for stage in range(1,4):
        m+=f'add w26,w25,#{stage}\nmov w9,#3\nudiv w10,w26,w9\nmsub w26,w10,w9,w26\n'+b.put('MapBlocked'+str(stage),'w26')
        for lane,label in enumerate(['left','centre','right']):m+=f'cmp w26,#{lane}\nb.ne map_hint_{stage}_{lane}\n'+b.text('MapWarning'+str(stage),'The radio warns: avoid the '+label+' lane.')+f'map_hint_{stage}_{lane}:\n'
    m+='b finish';map_hint=b.routine('life_rework_patrol_briefing',m)
    full=b.routine('life_rework_refresh_context',f'bl {snap:#x}\nbl {history:#x}\nbl {map_hint:#x}\nb finish')
    # Native list/scenario boundaries populate context before evaluating choices.
    menus=['genesis_v18_school52','genesis_v18_manager_career19','genesis_v18_coach_career19','genesis_v18_storm_career19','genesis_v18_tsunami_career21','genesis_v18_volcano_career21','genesis_rework_fight_camp','genesis_v9_v13_duty','genesis_v9_v13_government','genesis_v8_football_v8','genesis_v9_basketball_v9','genesis_v9_v12_soccer','genesis_v18_seasons_v18','genesis_v18_pro_sports18','genesis_v18_school_sports18','genesis_v18_start_season','genesis_v18_basket_build20']
    s='cbz x0,finish\nmov x8,x0\n'
    for i,k in enumerate(menus):s+=h.compare_key(k,'rework_refresh_open','rework_refresh_next_'+str(i))+'\nrework_refresh_next_'+str(i)+':\n'
    s+=f'b finish\nrework_refresh_open:\nbl {full:#x}\nb finish';b.chain('life_rework_before_existing_menu','v47_project_before_show',s)
    s='cbz x2,finish\nldr w9,[x2,#16]\ncmp w9,#20\nb.lt finish\nmov x8,x2\n'
    # Match a fixed prefix without reading beyond the managed string length.
    prefix='scenario.lifeRework.'
    for i,ch in enumerate(prefix):s+=f'ldrh w9,[x8,#{20+i*2}]\ncmp w9,#{ord(ch)}\nb.ne finish\n'
    s+=f'bl {full:#x}\nb finish';b.chain('life_rework_before_scenario','v47_bind_native_scenario',s)
    # Meaningful effects use the original native APIs and exact receivers.
    s='mov w19,w0\n'+b.ctx(owner)
    s+=f'cmp w19,#1\nb.eq rework_action_sync\ncmp w19,#10\nb.eq rework_action_study\ncmp w19,#11\nb.eq rework_action_pass\ncmp w19,#12\nb.eq rework_action_fail\ncmp w19,#13\nb.eq rework_action_school_fight\ncmp w19,#14\nb.eq rework_action_injury\ncmp w19,#16\nb.eq rework_action_home_health\ncmp w19,#21\nb.eq rework_action_pads\ncmp w19,#22\nb.eq rework_action_grapple\ncmp w19,#23\nb.eq rework_action_recover\ncmp w19,#24\nb.eq rework_action_scout\ncmp w19,#31\nb.eq rework_action_enlist\nb finish\n'
    s+=f'rework_action_sync:\nbl {full:#x}\nb finish\nrework_action_study:\n'+stat(b,0x2c46830,1)+stat(b,0x2c46584,2)+'mov w20,#1\nb rework_school_grade\nrework_action_pass:\n'+stat(b,0x2c46584,4)+'mov w20,#5\nb rework_school_grade\nrework_action_fail:\n'+stat(b,0x2c46584,-2)+'mov w20,#-3\nb rework_school_grade\nrework_action_school_fight:\n'+stat(b,0x2c46670,-6)+stat(b,0x2c46ad0,-5)+'mov w20,#-2\nrework_school_grade:\n'+h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#1\nb.ne finish\nmov x0,x8\nmov w1,w20\nmov x2,xzr\nbl 0x2b6eb28\nb finish\nrework_action_injury:\n'+stat(b,0x2c46670,-5)+'b finish\n'
    s+='rework_action_home_health:\n'+b.ctx('parole_v11')+b.get('Active')+'cmp w24,#1\nb.ne finish\n'+b.get('LastCheckAge')+'cmp w24,w23\nb.ne finish\n'+stat(b,0x2c46670,5)+'b finish\n'
    for name,actions in [('pads',[(0x2ac421c,3),(0x2ac41d4,2)]),('grapple',[(0x2ac4144,3),(0x2ac421c,2)]),('recover',[(0x2ac1a84,4)]),('scout',[(0x2ac421c,2),(0x2ac418c,2)])]:
        s+='rework_action_'+name+':\ncmp w23,#18\nb.lt finish\n'+h.load_game()+'\nldr x8,[x8,#0x20]\ncbz x8,finish\nldr x27,[x8,#0x6f0]\ncbz x27,finish\nmov x0,x27\nmov x1,xzr\nbl 0x2abfe88\ncbz w0,finish\nmov x0,x27\nmov x1,xzr\nbl 0x2abfe58\ncbz x0,finish\nmov x26,x0\n'
        for method,n in actions:s+=f'mov x0,x26\nmov w9,#{n}\nscvtf s0,w9\nmov x1,xzr\nbl {method:#x}\n'
        if name=='recover':s+=stat(b,0x2c46670,2)
        s+='b finish\n'
    # Actual enlistment is explicit. StartMilitary receives a real initialized
    # SimOccupationMilitary object, rather than an enum cast as an object.
    s+='rework_action_enlist:\ncmp w23,#18\nb.lt finish\ncmp w23,#45\nb.gt finish\n'+b.get('WarSide')+'cbz w24,finish\n'+b.get('DraftAge')+'cmp w24,w23\nb.ge finish\n'+h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#4\nb.eq finish\ncmp w9,#3\nb.eq rework_deploy_existing\n'
    # Resolve the class through IL2CPP's already audited assembly/class API.
    # Resolve the actual Army enum through the game's string API. Do not
    # guess a numeric branch or leave rank/title/salary uninitialized.
    s+='mov w28,#1\nrework_find_army:\nmov w0,w28\nmov x1,xzr\nbl 0x27fe4c4\ncbz x0,rework_army_next\nmov x8,x0\n'
    s+=h.compare_key('Army','rework_army_found','rework_army_lower')+'\nrework_army_lower:\n'+h.compare_key('army','rework_army_found','rework_army_next')+'\nrework_army_next:\nadd w28,w28,#1\ncmp w28,#5\nb.le rework_find_army\nb rework_enlist_unavailable\nrework_army_found:\nmov w27,w28\nmov w0,#1\nmov w1,#1\nmov x2,xzr\nbl 0x27fe124\ncbz x0,rework_enlist_unavailable\nmov x25,x0\n'
    s+='bl 0x223e48c\n'+f'adr x1,{b.literal("Assembly-CSharp"):#x}\nbl 0x223e490\ncbz x0,rework_enlist_unavailable\nbl 0x223df90\n'+f'adr x1,{b.literal(""):#x}\nadr x2,{b.literal("SimOccupationMilitary"):#x}\nbl 0x223dfc8\ncbz x0,rework_enlist_unavailable\nbl 0x2237158\ncbz x0,rework_enlist_unavailable\nmov x26,x0\nmov w1,#1\nmov x2,xzr\nbl 0x2b6affc\nmov x0,x26\nmov w1,w27\nmov x2,xzr\nbl 0x2b6af2c\nmov x0,x26\nldr w1,[x25,#0x14]\nmov x2,xzr\nbl 0x2b6af3c\nmov x0,x26\nldr w1,[x25,#0x10]\nmov x2,xzr\nbl 0x2b6af5c\nldr w0,[x25,#0x10]\nldr w1,[x25,#0x14]\nmov w2,w27\nmov w3,#0\nmov x4,xzr\nbl 0x27fe560\ncbz x0,rework_enlist_unavailable\nmov x1,x0\nmov x0,x26\nmov x2,xzr\nbl 0x2b6af6c\n'+h.load_game()+'\nldr x0,[x8,#0x28]\ncbz x0,rework_enlist_unavailable\nmov x1,xzr\nbl 0x2c38288\ncbz x0,rework_enlist_unavailable\nmov x1,xzr\nbl 0x2a27280\ncbz x0,rework_enlist_unavailable\nmov x1,x0\nmov x0,x26\nldr w9,[x25,#0x68]\nscvtf s0,w9\nmov x2,xzr\nbl 0x2b6b298\n'+h.load_game()+'\nldr x0,[x8,#0x28]\ncbz x0,rework_enlist_unavailable\nmov x1,x26\nmov x2,xzr\nbl 0x2a7dd40\nb rework_deploy_existing\nrework_enlist_unavailable:\n'+b.ctx(owner)+b.text('WarReport','No military post could be created. Your job was not changed. Use the original military application to review available service.')+'b finish\n'
    s+='rework_deploy_existing:\n'+h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#3\nb.ne finish\nmov x26,x8\nmov x0,x26\nmov x1,xzr\nbl 0x2b6af94\nadd w1,w0,#1\nmov x0,x26\nmov x2,xzr\nbl 0x2b6af9c\nmov x0,x26\nmov w1,w23\nmov x2,xzr\nbl 0x2b6afac\n'+b.ctx(owner)+b.put('DraftAge','w23')+b.set('Deployed',1)+b.set('NativeMilitary',1)+b.set('MissionStep',0)+b.set('Squad',8)+b.text('WarReport','You answered the call-up and began a military deployment. Your native service record was updated. Current employment may have changed to military service.')+b.text('JournalMessage','I answered a wartime call-up and began military service.')+b.inc('JournalSequence')+'b finish'
    perform=b.routine('life_rework_native_action',s)
    # Exactly one receipt for each successful content transaction.
    s='tbz w0,#0,finish\ncbz x19,finish\ncbz x21,finish\nldr x8,[x21,#16]\ncbz x8,finish\n'+h.compare_key(owner,'rework_owner','finish')+'\nrework_owner:\nldr x8,[x19,#24]\ncbz x8,finish\n'+h.compare_key('NativeAction','rework_action','rework_check_journal')+'\nrework_check_journal:\n'+h.compare_key('JournalSequence','rework_journal','finish')+f'\nrework_action:\nmov w0,w20\nbl {perform:#x}\nb rework_journal\nrework_journal:\n'+b.ctx(owner)+b.get('JournalSequence','w26')+b.get('JournalLogged')+'cmp w26,w24\nb.le finish\n'+b.put('JournalLogged','w26')+b.string('JournalMessage')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\n'+f'bl {b.journal55:#x}\nb finish'
    b.chain('life_rework_committed_effects_and_journal','v18_saved_state',s)
    # A real camp in the native gym replaces the removed circuit link.
    s='cbz x0,finish\nmov x27,x0\n'+b.string('FightCamp1104')+'mov x1,x0\nmov x0,x27\nmov x2,xzr\nbl 0x30611d0\nb finish'
    b.install('life_rework_inside_original_fight_gym',0x33518dc,s)
    annual=f'bl {full:#x}\n'+b.ctx(owner)+b.get('AnnualNoticeAge')+'cmp w24,w23\nb.ge finish\n'+b.put('AnnualNoticeAge','w23')+b.get('WarSide')+'cbz w24,rework_annual_school\ncmp w23,#18\nb.lt rework_annual_school\ncmp w23,#45\nb.gt rework_annual_school\n'+b.get('Deployed')+'cbnz w24,rework_annual_school\n'+b.get('DraftAge')+'cmp w24,w23\nb.ge rework_annual_school\n'+b.string('genesis_rework_event_callup')+'mov w1,#1\nmov w2,#1\nmov x3,xzr\nmov x4,xzr\nbl 0x308480c\nb finish\nrework_annual_school:\n'+b.get('SchoolEligible')+'cbz w24,finish\n'+b.get('Roll')+'cmp w24,#25\nb.hs finish\n'+b.string('genesis_rework_event_school')+'mov w1,#1\nmov w2,#1\nmov x3,xzr\nmov x4,xzr\nbl 0x308480c\nb finish'
    b.chain('life_rework_annual_context_events','v41_yearly_checkin_enforcement',annual)
