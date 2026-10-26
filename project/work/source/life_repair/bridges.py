"""Return original game scenarios through its existing blueprint result slot."""
from native_hooks import h
from life_rework.systems import stat


def allocate(b,name):
    return 'bl 0x223e48c\n'+f'adr x1,{b.literal("Assembly-CSharp"):#x}\nbl 0x223e490\ncbz x0,finish\nbl 0x223df90\nadr x1,{b.literal(""):#x}\nadr x2,{b.literal(name):#x}\nbl 0x223dfc8\ncbz x0,finish\nbl 0x2237158\ncbz x0,finish\nmov x25,x0\n'


def hooks(b):
    s='cbz x19,finish\ncbz x21,finish\nldr x8,[x21,#16]\ncbz x8,finish\n'+h.compare_key('life_rework','bridge1106_owner','finish')+'\nbridge1106_owner:\nldr x8,[x19,#24]\ncbz x8,finish\n'
    for key,label in [('SchoolNativeFight1106','school'),('NativeMinefield1106','minefield'),('WarFatal1106','fatal')]:s+=h.compare_key(key,'bridge1106_'+label,'bridge1106_next_'+label)+'\nbridge1106_next_'+label+':\n'
    s+='b finish\nbridge1106_school:\n'+b.ctx('life_rework')+'cmp w23,#6\nb.lt finish\n'+b.get('SchoolCombatAge1106')+'cmp w24,w23\nb.ge finish\n'
    s+=f'bl {b.old["followup_first_actual_classmate"]["stub"]:#x}\ncbz x0,finish\nmov x27,x0\n'+allocate(b,'ScenarioCustomAttack')+'mov x1,x27\nmov x2,xzr\nbl 0x3833b6c\n'
    # Same flag and constructor used by ScenarioSchoolBully's stock fight choice.
    s+=h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr x8,[x8,#0x70]\ncbz x8,finish\nmov w9,#1\nstrb w9,[x8,#0x639]\n'+b.ctx('life_rework')+b.put('SchoolCombatAge1106','w23')+b.set('SchoolBullyStage',3)+'str x25,[sp]\nb return_custom\n'
    s+='bridge1106_minefield:\n'+b.ctx('life_rework')+b.get('War')+'cbz w24,finish\n'+b.get('WarSide')+'cbz w24,finish\n'+b.get('WarNativeMissionAge1106')+'cmp w24,w23\nb.ge finish\n'
    s+=h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#3\nb.ne finish\n'+allocate(b,'ScenarioMilitaryDeployment')+'mov x1,xzr\nbl 0x39a09d4\n'+b.ctx('life_rework')+b.put('WarNativeMissionAge1106','w23')+'str x25,[sp]\nb return_custom'
    s+='\nbridge1106_fatal:\n'+b.ctx('life_rework')+b.get('War')+'cbz w24,finish\n'+b.get('WarSide')+'cbz w24,finish\n'+h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w9,#3\nb.ne finish\n'
    s+=allocate(b,'DEATH_TYPE').replace('bl 0x2237158\ncbz x0,finish\nmov x25,x0\n','')+f'adr x1,{b.literal("MILITARY_DEPLOYMENT"):#x}\nbl 0x223dfe8\ncbz x0,finish\nadd x1,sp,#0xf8\nbl 0x223e680\nldr w27,[sp,#0xf8]\n'
    s+=allocate(b,'BluePrintHeroDeath')+'mov x1,xzr\nbl 0x3209d28\nstr w27,[x25,#0x1c]\n'+b.string('You were killed by incoming fire during a wartime military mission.')+'mov x2,x0\nmov x0,x25\nadd x1,x25,#0x20\nbl 0x223e768\nmov x0,x25\nmov x1,xzr\nbl 0x3209f1c\ncbz x0,finish\nstr x0,[sp]\nb return_custom'
    b.chain('repair_original_school_combat_and_minefield','v40_stock_police_application',s,ret=True)

    # Stock school combat already grants FIVE real popularity points here.
    # Record the same completed event for the added school overview/follow-up.
    s=b.ctx('life_rework')+b.get('SchoolCombatAge1106')+'cmp w24,w23\nb.ne finish\n'+b.get('SchoolCombatDoneAge1106')+'cmp w24,w23\nb.ge finish\n'+b.put('SchoolCombatDoneAge1106','w23')+b.inc('SchoolReputation1106',5)+'b finish'
    b.install('repair_record_actual_school_fight_popularity',0x383ae88,s)

    # Audio runs through the retained game-to-Java UI event bridge. Respect the
    # original game sound setting checked by AudioManager.PlaySoundWithFileName.
    s='cmp w0,#172\nb.eq school_peer1106_bad\ncmp w0,#174\nb.eq school_peer1106_good\ncmp w0,#201\nb.lt finish\ncmp w0,#203\nb.gt finish\nmov w19,w0\n'+h.load_game()+'\nldr x8,[x8,#0x48]\ncbz x8,finish\nldrb w9,[x8,#0x5e]\ncbz w9,finish\nadd w0,w19,#1609\n'+f'bl {b.old["dispatch_android_ui21"]["stub"]:#x}\nb return_custom'
    s+='\nschool_peer1106_bad:\nmov w19,#-3\nb school_peer1106_apply\nschool_peer1106_good:\nmov w19,#3\nschool_peer1106_apply:\n'+f'bl {b.old["followup_first_actual_classmate"]["stub"]:#x}\ncbz x0,return_custom\nmov w1,w19\nmov x2,xzr\nbl 0x2c48a44\nb return_custom'
    b.chain('repair_native_battle_audio','life_rework_native_action',s,ret=True)
