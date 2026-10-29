"""Classmate invitations and deterministic annual queues without invented relatives."""
from native_hooks import h
from life_rework.systems import stat

def install(b):
 # Scope the chosen peer to the current annual refresh. A handle owns the person;
 # numeric saved notice age/outcome survives saves. Responses re-find the peer
 # in the actual roster and require the same school and hero age.
 st=b.state
 code='mov x25,x0\nmov x26,x1\nstr xzr,[sp]\n'
 for off,reg in [(8,'x25'),(16,'x26')]:code+=f'adr x8,{st+off:#x}\nldr x0,[x8]\ncbz x0,new_scope1125\nbl 0x223e73c\ncmp x0,{reg}\nb.ne new_scope1125\n'
 code+='b finish\nnew_scope1125:\n'
 for off in [0,8,16]:code+=f'adr x28,{st+off:#x}\nldr x0,[x28]\ncbz x0,scope_free1125_{off}\nbl 0x223e784\nstr xzr,[x28]\nscope_free1125_{off}:\n'
 for off,reg in [(8,'x25'),(16,'x26')]:code+=f'mov x0,{reg}\nmov w1,#0\nbl 0x223e704\nadr x8,{st+off:#x}\nstr x0,[x8]\n'
 code+='mov w9,#1\nstr x9,[sp]\nb finish'
 scope=b.routine('school1125_invitation_scope',code)
 code=''
 for off in [0,8,16]:code+=f'adr x28,{st+off:#x}\nldr x0,[x28]\ncbz x0,invitation_free1125_{off}\nbl 0x223e784\nstr xzr,[x28]\ninvitation_free1125_{off}:\n'
 release=b.routine('school1125_free_invitation_scope',code+'b finish')
 code=b.ctx('life_rework')+b.set('CrushAvailable1125',0)+h.load_occupation(end='crush_unavailable1125')+'\nldr w9,[x8,#0x10]\ncmp w9,#1\nb.ne crush_unavailable1125\nmov x27,x8\nmov x0,x22\nldr x1,[x27,#0x20]\ncbz x1,crush_unavailable1125\n'+f'bl {scope:#x}\ncbz w0,crush_scope_ready1125\n'+b.set('CrushNoticeAge1125',-1)+'crush_scope_ready1125:\nldr x0,[x27,#0x20]\ncbz x0,finish\ncmp w23,#8\nb.lt crush_unavailable1125\ncmp w23,#18\nb.gt crush_unavailable1125\n'+b.get('SchoolSuspendedAge1110')+'cmp w24,w23\nb.ge finish\n'+b.get('CrushNoticeAge1125')+'cmp w24,w23\nb.eq crush_keep1125\n'+f'adr x28,{st:#x}\nldr x0,[x28]\ncbz x0,crush_no_old1125\nbl 0x223e784\nstr xzr,[x28]\ncrush_no_old1125:\nldr x0,[x27,#0x20]\ncbz x0,finish\nmov x1,xzr\nbl 0x2b388b0\ncbz x0,finish\nmov x26,x0\nldr w25,[x26,#0x18]\ncmp w25,#1\nb.lt finish\ncmp w25,#512\nb.hi finish\nmov w0,#0\nmov w1,w25\nmov x2,xzr\nbl 0x2e0b54c\nmov w28,w0\nldr x26,[x26,#0x10]\ncbz x26,finish\nmov w20,#0\ncrush_scan1125:\ncmp w20,w25\nb.ge finish\nadd w9,w20,w28\nudiv w10,w9,w25\nmsub w9,w10,w25,w9\nadd x8,x26,#0x20\nldr x19,[x8,w9,uxtw #3]\nadd w20,w20,#1\ncbz x19,crush_scan1125\nldrb w9,[x19,#0x18]\ncbz w9,crush_scan1125\nldr w9,[x19,#0x20]\nsub w9,w9,w23\nadd w9,w9,#1\ncmp w9,#2\nb.hi crush_scan1125\nmov x0,x19\nmov w1,#0\nbl 0x223e704\nadr x8,{st:#x}\nstr x0,[x8]\nmov x0,x19\nmov x1,xzr\nbl 0x2c44914\nmov x28,x0\n'+b.ctx('life_rework')+b.textptr('CrushName1125','x28')+b.put('CrushNoticeAge1125','w23')+'crush_keep1125:\n'+b.set('CrushAvailable1125',1)+'b finish'
 # Occupation.GetSchool audited original getter is resolved below at generation.
 code=code.replace('crush_keep1125:\n', f'crush_keep1125:\nadr x8,{st:#x}\nldr x0,[x8]\ncbz x0,crush_unavailable1125\nbl 0x223e73c\ncbz x0,crush_unavailable1125\nldrb w9,[x0,#0x18]\ncbz w9,crush_unavailable1125\n'+f'bl {b.old["v45_current_year"]["stub"]:#x}\ncmp w0,#1900\nb.lt crush_early_art1125\ncmp w0,#1960\nb.lt crush_middle_art1125\n'+b.text('CrushImage1125','native1119/eras/school/event_pictures/lunch_invitation')+'b crush_art_ready1125\ncrush_middle_art1125:\n'+b.text('CrushImage1125','native1125/school/library1910')+'b crush_art_ready1125\ncrush_early_art1125:\n'+b.text('CrushImage1125','native1125/school/picnic1880')+'crush_art_ready1125:\n')
 code+=f'\ncrush_unavailable1125:\nbl {release:#x}\nb finish'
 prepare=b.routine('school1125_prepare_classmate_notice',code)
 # Context refresh does not create cards. It only prepares saved fields/roots.
 # Actual annual delivery uses the original school's age-up container.
 r=b.resolved('connected_prepare_native_annual_queues');s=r['source'];mark='\nfinish:\n';assert s.count(mark)==1
 extra=f'bl {prepare:#x}\n'+b.ctx('life_rework')+b.set('EraEvent1125',0)+b.get('NativeInPrison1105')+'cbnz w24,era_notice_done1125\ncmp w23,#18\nb.lt era_notice_done1125\n'+b.get('Year','w26')+b.get('Roll','w25')+'add w25,w25,w23\nmov w9,#4\nudiv w10,w25,w9\nmsub w25,w10,w9,w25\n'
 for lo,hi,first in [(1800,1899,1),(1900,1949,5),(1950,1999,9),(2000,3999,13)]:
  extra+=f'cmp w26,#{lo}\nb.lt era_next1125_{lo}\ncmp w26,#{hi}\nb.gt era_next1125_{lo}\nadd w24,w25,#{first}\n'+b.put('EraEvent1125')+f'b era_notice_done1125\nera_next1125_{lo}:\n'
 extra+='era_notice_done1125:\n'
 b.redirect(r['name'],s.replace(mark,mark+extra,1))
 # A command validates that its chosen classmate still belongs to the roster.
 code='mov w20,w0\n'+b.ctx('life_rework')+b.get('CrushAvailable1125')+'cmp w24,#1\nb.ne crush_gone1125\n'+b.get('CrushNoticeAge1125')+'cmp w24,w23\nb.ne crush_gone1125\n'+b.get('CrushResponseAge1125')+'cmp w24,w23\nb.ge crush_already1125\n'+b.get('SchoolSuspendedAge1110')+'cmp w24,w23\nb.ge crush_gone1125\n'+h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#1\nb.ne crush_gone1125\nldr x0,[x8,#0x20]\ncbz x0,crush_gone1125\nmov x1,xzr\nbl 0x2b388b0\ncbz x0,crush_gone1125\nmov x26,x0\n'+f'adr x8,{st:#x}\nldr x0,[x8]\ncbz x0,crush_gone1125\nbl 0x223e73c\ncbz x0,crush_gone1125\nmov x27,x0\nldrb w9,[x27,#0x18]\ncbz w9,crush_gone1125\nldr w25,[x26,#0x18]\ncmp w25,#512\nb.hi crush_gone1125\nldr x26,[x26,#0x10]\ncbz x26,crush_gone1125\nmov w19,#0\ncrush_check1125:\ncmp w19,w25\nb.ge crush_gone1125\nadd x8,x26,#0x20\nldr x9,[x8,w19,uxtw #3]\nadd w19,w19,#1\ncmp x9,x27\nb.ne crush_check1125\n'+b.put('CrushResponseAge1125','w23')+'cmp w20,#993\nb.eq crush_kind1125\ncmp w20,#994\nb.eq crush_friend1125\n'+b.text('CrushResult1125','You politely say you do not feel the same. Your classmate thanks you for being honest. You both keep your boundaries.')+'b crush_journal1125\ncrush_kind1125:\nmov x0,x27\nmov w1,#4\nmov x2,xzr\nbl 0x2c48a44\n'+b.inc('SchoolFriends',4)+stat(b,0x2c46584,2)+b.text('CrushResult1125','You say you like spending time together and arrange to sit together at break. Your bond improves. You can keep getting to know each other at school.')+'b crush_journal1125\ncrush_friend1125:\nmov x0,x27\nmov w1,#2\nmov x2,xzr\nbl 0x2c48a44\n'+b.inc('SchoolFriends',2)+b.text('CrushResult1125','You suggest being friends. Your classmate accepts, and you spend break together without pressure.')+'crush_journal1125:\n'+b.string('A classmate told me they had a crush on me. I responded thoughtfully and respected their feelings.')+f'bl {b.journal55:#x}\nb finish\ncrush_already1125:\n'+b.text('CrushResult1125','You already answered this invitation. Give the friendship time to grow; there is no repeat reward.')+'b finish\ncrush_gone1125:\n'+b.text('CrushResult1125','That invitation is no longer current. Return to school next year to meet your present classmates.')+'b finish'
 respond=b.routine('school1125_classmate_response',code)
 r=b.resolved('life_rework_native_action');s=r['source'];head=h.save()+'\n';assert s.startswith(head)
 b.redirect(r['name'],head+f'cmp w0,#993\nb.lt old_school_action1125\ncmp w0,#995\nb.gt old_school_action1125\nbl {respond:#x}\nb finish\nold_school_action1125:\n'+s[len(head):])
 # Manual invitation refresh. Only an actual current classmate can be selected.
 r=b.resolved('life_rework_native_action');s=r['source'];head=h.save()+'\n'
 b.redirect(r['name'],head+f'cmp w0,#992\nb.ne older_invite_action1125\nbl {prepare:#x}\nb finish\nolder_invite_action1125:\n'+s[len(head):])
 # Register the new independent native annual container with existing ones.
 b.chain('school1125_activate_era_queue','connected_activate_annual_containers',b.ctx('era_events1125')+'b finish')
 # Generate one dated suggestion; do not replace an accepted contract or pay
 # anything for opening a poster. The normal job/lead/arrest gates still apply.
 names=[('Caleb "Dusty" Bell',0),('Rosa "Red" Vega',1),('Elias "Whiskey" Reed',2),('Jun "Long Trail" Chen',3),('Samuel "Coyote" Brooks',0),('Clara "Prairie" Ward',1),('Jonah "Snake-Eye" Pike',2),('Wei "Silver" Lin',3)]
 code=b.ctx('life_rework')+b.get('WantedSuggestionAge1125')+'cmp w24,w23\nb.eq finish\n'+b.put('WantedSuggestionAge1125','w23')+b.get('Roll','w25')+'add w25,w25,w23\nand w25,w25,#7\n'
 for i,(name,portrait)in enumerate(names):code+=f'cmp w25,#{i}\nb.ne wanted_next1125_{i}\n'+b.text('WantedName1125',name)+b.text('WantedImage1125','native1125/wanted/'+str(portrait))+f'b wanted_charge1125\nwanted_next1125_{i}:\n'
 code+='wanted_charge1125:\n'+b.get('Roll','w25')+'and w25,w25,#3\n'
 for i,charge in enumerate(['horse theft','stagecoach robbery','cattle rustling','escaping lawful custody']):code+=f'cmp w25,#{i}\nb.ne charge_next1125_{i}\n'+b.text('WantedCharge1125',charge)+f'b wanted_reward1125\ncharge_next1125_{i}:\n'
 code+='wanted_reward1125:\n'+f'bl {b.old["era1121_nominal_pay_factor"]["stub"]:#x}\nmov w25,w0\n'+b.get('Roll')+'mov w9,#40\nmul w24,w24,w9\nadd w24,w24,#2000\nmul w24,w24,w25\nmov w9,#1000\nudiv w24,w24,w9\n'+b.put('WantedReward1125')+'b finish'
 wanted=b.routine('school1125_wanted_suggestion',code)
 r=b.resolved('connected_prepare_native_annual_queues');s=r['source'];mark='era_notice_done1125:\n';assert s.count(mark)==1;b.redirect(r['name'],s.replace(mark,mark+f'bl {wanted:#x}\n',1))
 # A matching current-year poster becomes the actual hunt when accepted at the
 # existing board. Saved contracts, completed-year lock and payout guards stay.
 from connected_life.appearance import marker
 r=b.resolved('era1121_bounty_contract');s=r['source'];at=marker(b,s,'BountyReward1121');end=s.index('bl 0x3059f90\n',at)+len('bl 0x3059f90\n')
 extra=b.get('WantedSuggestionAge1125')+'cmp w24,w23\nb.ne fallback_wanted1125\n'+b.copy('WantedName1125','BountyName1121')+b.get('WantedReward1125')+b.put('BountyReward1121')+b.text('BountyText1121','<GFC.life_rework.BountyName1121> is wanted for <GFC.life_rework.WantedCharge1125>. Reward: <GFC.life_rework.BountyReward1121>, alive only. Confirm the witness statement and trail, then request the sheriff’s backup.')+'b finish\nfallback_wanted1125:\n'
 b.redirect(r['name'],s[:end]+extra+s[end:])
