"""Small, typed bridges into existing relationships, grades, prison and sports."""
from native_hooks import h
from life_rework.systems import stat


def get_string(b,key,register='x22'):
    return b.string(key)+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\nmov '+register+',x0\n'


def hooks(b):
    owner='life_rework'
    s='mov w28,w0\n'+h.load_game()+'\nldr x25,[x8,#0x20]\ncbz x25,finish\n'
    for i,offset in enumerate([0xa8,0xb8,0xd8]):
        s+=f'ldr x0,[x25,#{offset}]\ncbz x0,family_impact_skip_{i}\nmov w1,w28\nmov x2,xzr\nbl 0x2c48a44\nfamily_impact_skip_{i}:\n'
    s+='mov x0,x25\nmov x1,xzr\nbl 0x327d45c\ncbz x0,finish\nldr w26,[x0,#0x18]\nldr x25,[x0,#0x10]\ncbz x25,finish\nadd x25,x25,#0x20\nmov w27,#0\nfamily_impact_children:\ncmp w27,w26\nb.ge finish\nldr x0,[x25,w27,uxtw #3]\ncbz x0,family_impact_child_next\nmov w1,w28\nmov x2,xzr\nbl 0x2c48a44\nfamily_impact_child_next:\nadd w27,w27,#1\nb family_impact_children'
    family=b.routine('followup_impact_actual_family_relationships',s)

    s='str xzr,[sp]\n'+h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#1\nb.ne finish\nldr x0,[x8,#0x20]\ncbz x0,finish\nmov x1,xzr\nbl 0x2b388b0\ncbz x0,finish\nldr w9,[x0,#0x18]\ncbz w9,finish\nldr x8,[x0,#0x10]\ncbz x8,finish\nldr x0,[x8,#0x20]\nstr x0,[sp]\nb finish'
    classmate=b.routine('followup_first_actual_classmate',s)

    s='mov w19,w0\n'+b.ctx(owner)
    for action,label in [(111,'family_good'),(112,'peer'),(113,'family_bad'),(114,'crowd_injury'),(121,'prison_good'),(122,'prison_visit'),(123,'prison_rest'),(124,'prison_bad'),(125,'prison_setup'),(126,'prison_fight'),(127,'prison_recruit'),(128,'prison_leader'),(131,'sports'),(141,'spouse_good'),(143,'spouse_bad'),(144,'children'),(145,'children'),(146,'support_set'),(147,'support_pay'),(151,'tree'),(152,'ancestor'),(161,'rap_craft')]:s+=f'cmp w19,#{action}\nb.eq effect1105_{label}\n'
    s+='b finish\neffect1105_family_good:\nmov w0,#2\n'+f'bl {family:#x}\n'+stat(b,0x2c46584,2)+'b finish\neffect1105_family_bad:\nmov w0,#-2\n'+f'bl {family:#x}\nb finish\neffect1105_crowd_injury:\nmov w0,#-3\nbl {family:#x}\n'+stat(b,0x2c46670,-15)+'b finish\n'
    s+=f'effect1105_peer:\nbl {classmate:#x}\ncbz x0,finish\nmov w1,#2\nmov x2,xzr\nbl 0x2c48a44\n'+h.load_occupation()+'\nmov x0,x8\nmov w1,#2\nmov x2,xzr\nbl 0x2b6eb28\nb finish\n'
    for label,delta in [('prison_good',1),('prison_visit',1),('prison_rest',1),('prison_bad',-1),('prison_setup',-3),('prison_fight',-2)]:
        s+='effect1105_'+label+':\n'+h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#4\nb.ne finish\nmov x27,x8\nmov x0,x27\n'+f'mov w1,#{delta}\nmov x2,xzr\nbl 0x2b6cb40\n'
        if label=='prison_visit':s+=f'mov w0,#2\nbl {family:#x}\n'+stat(b,0x2c46584,3)
        elif label=='prison_rest':s+=stat(b,0x2c46670,4)
        elif label=='prison_fight':s+=stat(b,0x2c46670,-10)
        elif label=='prison_setup':s+='mov x0,x27\nmov x1,xzr\nbl 0x2b6b788\ncmp w0,#0\nb.lt finish\nadd w1,w0,#1\nmov x0,x27\nmov x2,xzr\nbl 0x2b6b790\n'
        if label in ['prison_setup','prison_fight']:
            s+='mov x0,x27\nmov x1,xzr\nbl 0x2b6b540\ncbz x0,finish\nmov x26,x0\nmov x1,xzr\nbl 0x2b3697c\ncmp w0,#3\nb.ge finish\nadd w0,w0,#72\nmov x1,xzr\nmov x2,xzr\nbl 0x35f1608\ncbz x0,finish\nmov x1,x0\nmov x0,x26\nmov x2,xzr\nbl 0x2b367bc\n'
        s+='b finish\n'
    s+='effect1105_prison_leader:\n'+h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#4\nb.ne finish\n'+h.load_game()+'\nldr x0,[x8,#0x28]\nmov x1,xzr\nbl 0x2c44914\nmov x22,x0\n'+b.textptr('PrisonMember1_1105')+'b finish\n'
    s+='effect1105_prison_recruit:\n'+h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#4\nb.ne finish\nmov x0,x8\nmov x1,xzr\nbl 0x2b6b540\ncbz x0,finish\nmov x1,xzr\nbl 0x2b368e0\ncbz x0,finish\nldr w26,[x0,#0x18]\ncbz w26,finish\nldr x27,[x0,#0x10]\ncbz x27,finish\n'+b.get('PrisonRecruits1105','w25')+'sub w9,w25,#2\nmov w10,#0\ncmp w9,#0\ncsel w9,w9,w10,ge\nudiv w10,w9,w26\nmsub w9,w10,w26,w9\nadd x27,x27,#0x20\nldr x0,[x27,w9,uxtw #3]\ncbz x0,finish\nmov x1,xzr\nbl 0x2c44914\nmov x22,x0\n'
    for index in range(2,13):s+=f'cmp w25,#{index}\nb.ne prison_member_next_{index}\n'+b.textptr('PrisonMember'+str(index)+'_1105')+f'b finish\nprison_member_next_{index}:\n'
    s+='b finish\n'
    s+='effect1105_sports:\n'+h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#6\nb.ne effect1105_sports_school\nldr x0,[x8,#0x28]\ncbz x0,finish\nldr w9,[x0,#0x10]\ncmp w9,#2\nb.ne finish\nmov x1,xzr\nbl 0x2bc2fa4\ncbz x0,finish\nmov x27,x0\nmov w1,#1\nmov x2,xzr\nbl 0x2bc2cd4\nmov x0,x27\nmov w1,#1\nmov x2,xzr\nbl 0x2bc2d7c\nb finish\neffect1105_sports_school:\nldr w9,[x8,#0x10]\ncmp w9,#1\nb.ne finish\n'+stat(b,0x2c46584,2)+'b finish\n'
    for label,score in [('spouse_good',2),('spouse_bad',-2)]:
        s+='effect1105_'+label+':\n'+h.load_game()+'\nldr x8,[x8,#0x20]\ncbz x8,finish\nldr x0,[x8,#0xd8]\ncbz x0,finish\n'+f'mov w1,#{score}\nmov x2,xzr\nbl 0x2c48a44\n'
        if score>0:s+=b.ctx(owner)+b.put('MarriagePositiveAge1105','w23')
        s+='b finish\n'
    s+=f'effect1105_children:\nmov w0,#2\nbl {family:#x}\nb finish\neffect1105_tree:\nbl {b.family_initialize:#x}\nbl {b.family_select:#x}\nb finish\n'
    s+=f'effect1105_ancestor:\nbl {b.family_archive:#x}\nb finish\n'
    s+='effect1105_rap_craft:\n'+b.get('RapActive')+'cbz w24,finish\n'+b.get('RapRole','w25')+'mov w26,#0\n'
    for key,weight in [('Lyrics',2),('Vocabulary',1),('Flow',1),('Voice',1)]:s+=b.get('Rap'+key)+f'mov w9,#{weight}\nmadd w26,w24,w9,w26\n'
    s+='cmp w25,#3\nb.ne rap_craft_producer_check\nmov w26,#0\n'
    for key in ['Lyrics','Production','Vocabulary','Flow','Voice']:s+=b.get('Rap'+key)+'add w26,w26,w24\n'
    s+='b rap_craft_mean\nrap_craft_producer_check:\ncmp w25,#2\nb.ne rap_craft_mean\nmov w26,#0\n'
    for key,weight in [('Production',3),('Flow',1),('Voice',1)]:s+=b.get('Rap'+key)+f'mov w9,#{weight}\nmadd w26,w24,w9,w26\n'
    s+='rap_craft_mean:\nmov w9,#5\nsdiv w26,w26,w9\n'+b.ctx('music_studio')+b.put('Skill','w26')+'b finish\n'
    # Configure support from actual living children under 18. Snapshot refresh
    # fills the count; payments recheck balance and once-per-age at commitment.
    s+='effect1105_support_set:\n'+b.get('MarriageMinorChildren1105','w25')+'mov w9,#500\nmul w25,w25,w9\nmov w9,#10000\ncmp w25,w9\ncsel w25,w25,w9,le\n'+b.put('MarriageSupport1105','w25')+'b finish\n'
    s+='effect1105_support_pay:\n'+b.get('MarriageSupportAge1105')+'cmp w24,w23\nb.ge finish\n'+b.get('MarriageSupport1105','w25')+'cmp w25,#0\nb.le finish\n'+h.load_game()+'\nldr x8,[x8,#0x20]\ncbz x8,finish\nldr x27,[x8,#0xe8]\ncbz x27,finish\nldr d0,[x27,#0x10]\nscvtf d1,w25\nfcmp d0,d1\nb.lt effect1105_support_funds\nfneg d0,d1\nmov x0,x27\nmov x1,xzr\nbl 0x2a6eb5c\n'+b.ctx(owner)+b.put('MarriageSupportAge1105','w23')+b.text('MarriagePaymentReport1105','Your support payment was taken from your bank balance. Your family relationships improved.')+f'mov w0,#2\nbl {family:#x}\n'+b.string('I paid the agreed yearly support to my family.')+f'bl {b.journal55:#x}\nb finish\neffect1105_support_funds:\n'+b.ctx(owner)+b.text('MarriagePaymentReport1105','You could not afford the payment. Your balance and payment record stayed unchanged.')+'b finish'
    perform=b.routine('followup_perform_typed_game_action',s)
    # Dispatch only new actions, preserving all 1104 operations and receipts.
    b.chain('followup_extend_existing_native_actions','life_rework_native_action',
            f'cmp w0,#100\nb.lt finish\nbl {perform:#x}\nb finish')
    b.followup_family_impact=family;b.followup_classmate=classmate
    snapshot_hooks(b)
    divorce_bridge(b)


def snapshot_hooks(b):
    owner='life_rework'
    s=b.ctx(owner)+b.set('NativeInPrison1105',0)+h.load_occupation(end='snapshot1105_bank')+'\nldr w9,[x8,#0x10]\ncmp w9,#4\nb.ne snapshot1105_bank\nmov x27,x8\n'+b.set('NativeInPrison1105',1)+'mov x0,x27\nmov x1,xzr\nbl 0x2b6b540\ncbz x0,snapshot1105_bank\nmov x27,x0\nmov x1,xzr\nbl 0x2b3697c\nmov w24,w0\n'+b.put('PrisonSecurity1105')+'mov x0,x27\nmov x1,xzr\nbl 0x2b368e0\ncbz x0,snapshot1105_bank\nldr w24,[x0,#0x18]\nadd w24,w24,#1\n'+b.put('PrisonRecruitCap1105')+'snapshot1105_bank:\n'+h.load_game()+'\nldr x8,[x8,#0x20]\ncbz x8,finish\nldr x8,[x8,#0xe8]\ncbz x8,finish\nldr d0,[x8,#0x10]\nfcvtzs x24,d0\nmov w9,#2000000000\ncmp x24,x9\ncsel x24,x24,x9,le\n'+b.put('NativeBank1105')
    s+=b.set('SchoolPeerPresent1105',0)+f'bl {b.followup_classmate:#x}\ncbz x0,snapshot1105_no_peer\nmov x1,xzr\nbl 0x2c44914\nmov x22,x0\n'+b.textptr('SchoolPeer1105')+b.set('SchoolPeerPresent1105',1)+'snapshot1105_no_peer:\n'
    s+=b.set('Married1105',0)+b.set('MarriageMinorChildren1105',0)+h.load_game()+'\nldr x25,[x8,#0x20]\ncbz x25,finish\nldr x27,[x25,#0xd8]\ncbz x27,snapshot1105_children\nmov x0,x27\nmov x1,xzr\nbl 0x2c32748\ncmp w0,#3\nb.ne snapshot1105_children\n'
    s+=b.set('Married1105',1)+'mov x0,x27\nmov x1,xzr\nbl 0x2c44914\nmov x28,x0\n'+get_string(b,'MarriageSpouseToken1105','x22')+'mov x0,x28\nmov x1,x22\nmov x2,xzr\nbl 0x4dfe080\ncbnz w0,snapshot1105_same_spouse\n'
    s+=b.textptr('MarriageSpouseToken1105','x28')+b.textptr('MarriageSpouse1105','x28')+b.set('MarriagePhase1105',0)+b.set('MarriageTrust1105',65)+b.set('MarriageSatisfaction1105',65)+b.set('MarriageConflicts1105',0)+b.put('MarriagePositiveAge1105','w23')+'snapshot1105_same_spouse:\n'
    s+=b.get('MarriageLastAge1105')+'cmp w24,w23\nb.ge snapshot1105_children\n'+b.put('MarriageLastAge1105','w23')+b.get('MarriagePositiveAge1105')+'sub w9,w23,w24\ncmp w9,#2\nb.le snapshot1105_cheating\n'+b.inc('MarriageTrust1105',-3)+b.inc('MarriageSatisfaction1105',-4)+'snapshot1105_cheating:\n'
    s+='mov x0,x25\nmov x1,xzr\nbl 0x327dddc\nmov w28,w0\n'+b.get('MarriageCheatCount1105')+'cmp w24,#0\nb.lt snapshot1105_cheat_saved\ncmp w28,w24\nb.le snapshot1105_cheat_saved\n'+b.inc('MarriageTrust1105',-25)+b.inc('MarriageSatisfaction1105',-20)+b.inc('MarriageConflicts1105',2)+'mov x0,x27\nmov w1,#-3\nmov x2,xzr\nbl 0x2c48a44\nsnapshot1105_cheat_saved:\n'+b.put('MarriageCheatCount1105','w28')
    s+='snapshot1105_children:\nmov x0,x25\nmov x1,xzr\nbl 0x327d45c\ncbz x0,snapshot1105_done_children\nldr w26,[x0,#0x18]\nldr x25,[x0,#0x10]\ncbz x25,snapshot1105_done_children\nadd x25,x25,#0x20\nmov w27,#0\nmov w28,#0\nsnapshot1105_child_loop:\ncmp w27,w26\nb.ge snapshot1105_child_count\nldr x8,[x25,w27,uxtw #3]\ncbz x8,snapshot1105_child_next\nldrb w9,[x8,#0x18]\ncbz w9,snapshot1105_child_next\nldr w9,[x8,#0x20]\ncmp w9,#18\ncinc w28,w28,lt\nsnapshot1105_child_next:\nadd w27,w27,#1\nb snapshot1105_child_loop\nsnapshot1105_child_count:\n'+b.put('MarriageMinorChildren1105','w28')+'snapshot1105_done_children:\n'+b.ctx('music_studio')+get_string(b,'Format','x28')+b.ctx(owner)+'mov x8,x28\n'+h.compare_key('Album','snapshot1105_album','snapshot1105_single')+'\nsnapshot1105_album:\n'+b.set('RapIsAlbum1105',1)+'b finish\nsnapshot1105_single:\n'+b.set('RapIsAlbum1105',0)+'b finish'
    snap=b.routine('followup_snapshot_actual_school_and_marriage',s)
    old=b.resolved('life_rework_snapshot');source=old['source'];marker='\nb finish\nfinish:';assert marker in source
    b.redirect(old['name'],source.replace(marker,f'\nbl {snap:#x}'+marker,1))

    # A completed release is counted once at the existing saved-state boundary.
    s='tbz w0,#0,finish\ncbz x19,finish\ncbz x21,finish\nldr x8,[x21,#16]\ncbz x8,finish\n'+h.compare_key('music_studio','rap1105_owner','finish')+'\nrap1105_owner:\nldr x8,[x19,#24]\ncbz x8,finish\n'+h.compare_key('TotalReleases','rap1105_release','finish')+'\nrap1105_release:\nmov w28,w20\n'+b.ctx(owner)+b.get('RapActive')+'cbz w24,finish\n'+b.get('RapLastRelease1105')+'cmp w28,w24\nb.le finish\n'+b.put('RapLastRelease1105','w28')+b.get('RapReleaseAge')+'cmp w24,w23\nb.eq rap1105_release_same_year\n'+b.set('RapWeek',0)+b.set('RapAlbumYear',0)+b.put('RapReleaseAge','w23')+'rap1105_release_same_year:\n'+b.inc('RapWeek')
    s+=b.ctx('music_studio')+get_string(b,'LastFormat','x28')+get_string(b,'LastTitle','x27')+'mov x8,x28\n'+h.compare_key('Album','rap1105_album','rap1105_single')+'\nrap1105_album:\n'+b.ctx(owner)+b.inc('RapAlbums')+b.inc('RapAlbumYear')+'b rap1105_label\nrap1105_single:\n'+b.ctx(owner)+b.inc('RapSingles')+'rap1105_label:\n'+b.textptr('RapLatest','x27')+b.inc('RapRep',2)+'b finish'
    b.chain('followup_rapper_tracks_existing_releases','v18_saved_state',s)


def divorce_bridge(b):
    # Use the existing blueprint's Scenario return slot, rather than launching
    # another UI while Genesis is processing a choice. The native constructor
    # expects a real SimLover. It retains the stock asset settlement and exes.
    s='cbz x19,finish\ncbz x21,finish\nldr x8,[x21,#16]\ncbz x8,finish\n'+h.compare_key('life_rework','divorce1105_owner','finish')+'\ndivorce1105_owner:\nldr x8,[x19,#24]\ncbz x8,finish\n'+h.compare_key('NativeDivorce1105','divorce1105_requested','finish')+'\ndivorce1105_requested:\n'
    s+=h.load_game()+'\nldr x8,[x8,#0x20]\ncbz x8,finish\nldr x27,[x8,#0xd8]\ncbz x27,finish\nmov x0,x27\nmov x1,xzr\nbl 0x2c32748\ncmp w0,#3\nb.ne finish\n'
    s+=b.ctx('life_rework')+b.get('MarriagePhase1105')+'cmp w24,#2\nb.lt finish\n'+b.get('MarriageFiledAge1105')+'cmp w24,w23\nb.ge finish\n'
    s+='bl 0x223e48c\n'+f'adr x1,{b.literal("Assembly-CSharp"):#x}\nbl 0x223e490\ncbz x0,finish\nbl 0x223df90\nadr x1,{b.literal(""):#x}\nadr x2,{b.literal("ScenarioLoverDivorce"):#x}\nbl 0x223dfc8\ncbz x0,finish\nbl 0x2237158\ncbz x0,finish\nmov x25,x0\nmov x1,x27\nmov x2,xzr\nbl 0x3911584\nstr x25,[sp]\nb return_custom'
    b.chain('followup_original_divorce_scenario_return','v40_stock_police_application',s,ret=True)
    # This runs only after the original divorce has moved the actual lover
    # to exes, immediately after the audited AddCurrentLoverToExes call.
    s=b.ctx('life_rework')+get_string(b,'MarriageSpouse1105')+b.textptr('MarriageEx1105')+b.set('MarriagePhase1105',4)+b.set('Married1105',0)+'b finish'
    b.install('followup_record_completed_native_divorce',0x3911864,s)
