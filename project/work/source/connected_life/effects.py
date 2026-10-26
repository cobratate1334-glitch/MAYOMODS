"""Typed school, prison, mood and item effects on the original life."""
from native_hooks import h
from life_rework.systems import stat
from connected_life.metadata import enum


def hooks(b):
 # Bound inmate support: find the actual person in the current prison roster.
 # A generic programme request chooses a current living inmate; the original
 # profile button passes its exact selected person. No shared preview cache.
 s='mov x19,x0\n'+b.ctx('life_rework')+b.text('PeerName1110','A fellow prisoner')+b.text('PeerReport1110','No fellow prisoner is available for that conversation right now. Try again from a current inmate profile.')+h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#4\nb.ne finish\nmov x20,x8\nmov x0,x20\nmov x1,xzr\nbl 0x2b6b540\ncbz x0,finish\nmov x1,xzr\nbl 0x2b368e0\ncbz x0,finish\nldr w25,[x0,#0x18]\ncbz w25,finish\ncmp w25,#512\nb.hi finish\nldr x26,[x0,#0x10]\ncbz x26,finish\nadd x26,x26,#0x20\nmov w27,#0\nsupport_scan1110:\ncmp w27,w25\nb.ge finish\nldr x21,[x26,w27,uxtw #3]\nadd w27,w27,#1\ncbz x21,support_scan1110\nldrb w9,[x21,#0x18]\ncbz w9,support_scan1110\ncbz x19,support_found1110\ncmp x21,x19\nb.ne support_scan1110\nsupport_found1110:\nmov x27,x21\nmov x0,x27\nmov x1,xzr\nbl 0x2c44914\nmov x28,x0\n'+b.ctx('life_rework')+b.textptr('PeerName1110','x28')+b.get('PeerSupportAge1110')+'cmp w24,w23\nb.eq support_quota_ready1110\n'+b.put('PeerSupportAge1110','w23')+b.set('PeerSupportCount1110',0)+'support_quota_ready1110:\n'+b.get('PeerSupportCount1110')+'cmp w24,#3\nb.lt support_converse1110\n'+b.text('PeerReport1110','You have already checked in several times this year. Give people time to respond and return next year; no further relationship or conduct reward is added.')+'b finish\nsupport_converse1110:\n'+b.inc('PeerSupportCount1110')+'mov x0,x27\nmov x1,xzr\nbl 0x2c42384\nfcvtzs w25,s0\ncmp w25,#30\nb.lt support_space1110\nmov x0,x27\nmov w1,#2\nmov x2,xzr\nbl 0x2c48a44\nmov x0,x20\nmov w1,#1\nmov x2,xzr\nbl 0x2b6cb40\n'+b.text('PeerReport1110','They listen, then thank you for checking in. You let them speak without offering favours. Your relationship improves and staff note your supportive conduct.')+'b support_journal1110\nsupport_space1110:\n'+b.text('PeerReport1110','They say they need some space today. You respect the answer and leave the door open for another conversation. You do not pressure them or claim a friendship they have not offered.')+'support_journal1110:\n'+b.string('I offered peer support to ')+'mov x1,x28\nmov x2,xzr\nbl 0x4df3450\n'+f'bl {b.journal55:#x}\nb finish'
 support=b.routine('connected_support_actual_inmate',s);b.connected_support=support
 # The old hook opened feedback then returned the old scenario. Return the new
 # Scenario to the ORIGINAL choice caller, which owns its presentation.
 s='cbz x0,finish\nmov x22,x0\nldr x8,[x22,#0x108]\ncbz x8,finish\nldr w9,[x8,#0x18]\nsub w9,w9,#1\ncmp w1,w9\nb.ne finish\ncmp w1,#0\nb.lt finish\nldr x8,[x8,#0x10]\ncbz x8,finish\nadd x8,x8,#0x20\nldr x8,[x8,w1,uxtw #3]\ncbz x8,finish\nldr x8,[x8,#0x10]\ncbz x8,finish\n'+h.compare_key('Offer peer support','peer_selected1110','finish')+'\npeer_selected1110:\n'+h.load_occupation()+'\nldr x9,[x22,#0x170]\ncmp x9,x8\nb.ne finish\nldr x0,[x22,#0x180]\ncbz x0,finish\n'+f'bl {support:#x}\n'+b.string('genesis_v8_inmate_support')+'mov x1,xzr\nmov x2,xzr\nbl 0x3084c00\nstr x0,[sp]\nb return_custom'
 b.install('connected_return_inmate_support_scenario',0x24de6e4,s,ret=True)
 # Actual primitive APIs are audited against the exact metadata/disassembly.
 # Grades: 2b6eb28; popularity: 2b6e59c (they are not interchangeable).
 s='mov w19,w0\n'
 for code,label in [(610,'support'),(611,'study'),(612,'warning'),(614,'school_sport'),(616,'library'),(617,'course'),(618,'mediate'),(626,'training_good'),(627,'training_bad'),(628,'reading'),(642,'range'),(643,'cannabis'),(644,'pills'),(645,'stimulants'),(646,'hallucinogens'),(650,'live_good'),(651,'live_bad')]:s+=f'cmp w19,#{code}\nb.eq effect1110_{label}\n'
 s+='b finish\neffect1110_support:\nmov x0,xzr\n'+f'bl {support:#x}\nb finish\n'
 def school(delta,method):return h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#1\nb.ne finish\nmov x0,x8\n'+f'mov w1,#{delta}\nmov x2,xzr\nbl {method:#x}\n'
 s+='effect1110_study:\n'+school(3,0x2b6eb28)+'b finish\neffect1110_school_sport:\n'+school(3,0x2b6e59c)+stat(b,0x2c46670,1)+stat(b,0x2c46584,2)+'b finish\neffect1110_warning:\n'+school(-2,0x2b6e59c)+school(-1,0x2b6eb28)+b.ctx('life_rework')+b.get('SchoolDiscipline1110')+'cmp w24,#3\nb.lt finish\n'+b.put('SchoolSuspendedAge1110','w23')+b.string('The principal suspended me for the rest of this school year after repeated misconduct.')+f'bl {b.journal55:#x}\nb finish\n'
 for label,score in [('library',1),('course',2),('mediate',2)]:
  s+='effect1110_'+label+':\n'+h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#4\nb.ne finish\nmov x0,x8\n'+f'mov w1,#{score}\nmov x2,xzr\nbl 0x2b6cb40\n'
  if label in ['library','course']:s+=stat(b,0x2c46830,1 if label=='library'else 2)
  if label=='mediate':s+=stat(b,0x2c46584,2)
  s+='b finish\n'
 for label,delta in [('training_good',3),('training_bad',-2)]:
  s+='effect1110_'+label+':\n'+h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#3\nb.ne finish\nmov x0,x8\n'+f'mov w1,#{delta}\nmov x2,xzr\nbl 0x2b6b318\nb finish\n'
 s+='effect1110_reading:\n'+stat(b,0x2c46584,3)+'b finish\neffect1110_range:\n'+stat(b,0x2c46830,1)+'b finish\n'
 for label,health,mood in [('cannabis',-1,2),('pills',-4,3),('stimulants',-6,4),('hallucinogens',-3,3)]:
  s+='effect1110_'+label+':\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr w9,[x8,#0x20]\ncmp w9,#18\nb.lt finish\n'+stat(b,0x2c46670,health)+stat(b,0x2c46584,mood)+'b finish\n'
 for label,delta in [('live_good',2),('live_bad',-3)]:s+='effect1110_'+label+':\n'+f'bl {b.old["v45_current_year"]["stub"]:#x}\ncmp w0,#2010\nb.lt finish\n'+stat(b,0x2c46584,delta)+'b finish\n'
 perform=b.routine('connected_perform_typed_life_action',s)
 b.chain('connected_extend_original_life_actions','life_rework_native_action',f'cmp w0,#610\nb.lt finish\ncmp w0,#651\nb.gt finish\nbl {perform:#x}\nb finish')
 # A completed stock fight is handled once, after damage/retaliation. Keep its
 # existing popularity reward for defending a pupil; subtract for provocation.
 s=b.ctx('life_rework')+b.get('SchoolCombatAge1106')+'cmp w24,w23\nb.ne finish\n'+b.get('SchoolCombatDoneAge1106')+'cmp w24,w23\nb.ge finish\n'+b.inc('SchoolDiscipline1110',2)+b.get('SchoolFightReason1110')+'cmp w24,#2\nb.ne school_fight_warning1110\n'+school(-10,0x2b6e59c)+b.ctx('life_rework')+b.inc('SchoolReputation1106',-10)+b.put('SchoolSuspendedAge1110','w23')+'b finish\nschool_fight_warning1110:\n'+b.get('SchoolDiscipline1110')+'cmp w24,#3\nb.lt finish\n'+b.put('SchoolSuspendedAge1110','w23')+'b finish'
 b.chain('connected_record_fight_consequences','repair_record_actual_school_fight_popularity',s)
