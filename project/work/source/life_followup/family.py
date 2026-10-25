"""Country ancestry and family pages backed by actual native relatives."""
import json
from pathlib import Path
from life_rework.content import p,scene,menu,set_,inc,text,seq

SOURCE=Path(__file__).resolve().parents[1]
MODEL=json.loads((SOURCE/'native_v52/country_height_model52.json').read_text())['countries']
COUNTRIES=[('UNK','Unrecorded')]+sorted({r['iso']:(r['iso'],r.get('source_country',r['country']))for r in reversed(MODEL)}.values())
INDEX={iso:i for i,(iso,name)in enumerate(COUNTRIES)}
ALIASES={r['country']:INDEX[r['iso']]for r in MODEL}


def build(a,base):
    for k,v,hi in [('AncestryReady1105',0,1),('FamilyGenerations1105',1,100000),('FamilyFamous1105',0,100000),('FamilyKind1105',0,5),('FamilyIndex1105',0,100000),('FamilyCount1105',0,100000),('FamilyAge1105',0,999),('FamilyHeight1105',0,250),('FamilyWealth1105',0,2000000000)]:a.prop(k,v,0,hi)
    for iso,name in COUNTRIES:a.prop('Ancestor_'+iso,0,0,1000000)
    a.prop('FamilyArchiveIndex1105',0,0,100000);a.prop('FamilyArchiveCount1105',0,0,100000)
    a.string('FamilyArchiveSelected1105','No earlier generation has been recorded.')
    for k,v in [('Ancestry1105','No ancestry recorded yet.'),('FamilyName1105','No relative selected'),('FamilyRelation1105',''),('FamilyCountry1105',''),('FamilyHistory1105',''),('FamilyAncestors1105','No earlier played generations have been recorded.'),('FamilyLastHero1105',''),('FamilyWealthText1105','0'),('FamilyState1105','')]:a.string(k,v)
    for kind,label in [(0,'You'),(1,'Father'),(2,'Mother'),(3,'Children'),(4,'Siblings'),(5,'Grandchildren')]:
        route=seq(set_('FamilyKind1105',kind),set_('FamilyIndex1105',0),set_('NativeAction',151),scene('family_person1105'))
        a.page('family_branch1105_'+str(kind),label,'Browse actual people in this branch of your saved family.',[
            ('Open this branch',route),('Back',menu('genesis_v18_familytree39'))],'handshake')
    a.replace_menu('genesis_v18_familytree39','Family tree',[
        ('Your ancestry',scene('ancestry1105'),'earth','Recorded country ancestry'),
        ('Parents',scene('family_parents1105'),'handshake','Your actual father and mother'),
        ('Children',scene('family_branch1105_3'),'house','Browse your actual children'),
        ('Siblings',scene('family_branch1105_4'),'handshake','Browse your actual siblings'),
        ('Grandchildren',scene('family_branch1105_5'),'house','Browse your actual grandchildren'),
        ('Family legacy',scene('family_legacy1105'),'books','Played generations and ancestry history'),
        ('Birth trait',scene('birth_trait1105'),'brain','Your saved rare trait'),
        ('Marriage and family',scene('marriage_home1105'),'heart','Trust, separation, care and support')])
    # Old links now reach real branches too. No invented grandparents are shown.
    for old in ['genesis_v18_family35','genesis_v18_familybranch039','genesis_v18_familybranch139','genesis_v18_familybranch239','genesis_v18_familybranch339']:
        if old in base:a.replace_menu(old,'Family tree',[('Open your actual family',scene('family_parents1105'),'handshake','Parents and relatives from your save'),('Family legacy',scene('family_legacy1105'),'books','Recorded played generations')])
    a.page('family_parents1105','Your parents','These are the parent records in your current life.',[
        ('Father',seq(set_('FamilyKind1105',1),set_('FamilyIndex1105',0),set_('NativeAction',151),scene('family_person1105'))),
        ('Mother',seq(set_('FamilyKind1105',2),set_('FamilyIndex1105',0),set_('NativeAction',151),scene('family_person1105'))),('Back',menu('genesis_v18_familytree39'))],'handshake')
    a.page('family_person1105',p('FamilyName1105'),'Relation: '+p('FamilyRelation1105')+'. '+p('FamilyState1105')+'. Birth country: '+p('FamilyCountry1105')+'.',[
        ('Previous person',seq(inc('FamilyIndex1105',-1),set_('NativeAction',151),scene('family_person1105'))),
        ('Next person',seq(inc('FamilyIndex1105'),set_('NativeAction',151),scene('family_person1105'))),
        ('My ancestry',scene('ancestry1105')),('Back to family',menu('genesis_v18_familytree39'))],'handshake',stats=[('Age',p('FamilyAge1105')),('Adult height estimate',p('FamilyHeight1105')),('People in branch',p('FamilyCount1105'))])
    a.page('ancestry1105','Your country ancestry',p('Ancestry1105')+'\n\nEach recorded parent contributes half. Founders use recorded birth countries; this is family heritage, not a DNA test. It stays with you when you continue as a child.',[('Family tree',menu('genesis_v18_familytree39')),('Earlier generations',scene('family_legacy1105'))],'earth')
    a.page('family_legacy1105','Family legacy','Browse the people you played in earlier generations. Recorded net worth includes you and living parents, spouse, siblings, children and grandchildren. Joint assets can appear in both spouses’ base-game records.',[('Browse earlier generations',seq(set_('NativeAction',152),scene('family_archive1105'))),('My ancestry',scene('ancestry1105')),('Family tree',menu('genesis_v18_familytree39'))],'books',stats=[('Played generations',p('FamilyGenerations1105')),('Famous played ancestors',p('FamilyFamous1105')),('Recorded family net worth',p('FamilyWealthText1105'))])
    a.page('family_archive1105','An earlier generation',p('FamilyArchiveSelected1105'),[
        ('Previous person',seq(inc('FamilyArchiveIndex1105',-1),set_('NativeAction',152),scene('family_archive1105'))),
        ('Next person',seq(inc('FamilyArchiveIndex1105'),set_('NativeAction',152),scene('family_archive1105'))),('Back',scene('family_legacy1105'))],'books',stats=[('Recorded ancestors',p('FamilyArchiveCount1105'))])


def native(b):
    from native_hooks import h
    owner='life_rework';country=b.old['v52_person_birth_country_name']['stub']
    s='str xzr,[sp]\ncbz x0,finish\n'+f'bl {country:#x}\ncbz x0,finish\nmov x8,x0\n'
    for i,(name,index)in enumerate(ALIASES.items()):s+=h.compare_key(name,'family_country_'+str(i),'family_country_next_'+str(i))+'\nfamily_country_next_'+str(i)+':\n'
    s+='b finish\n'
    for i,(name,index)in enumerate(ALIASES.items()):s+=f'family_country_{i}:\nmov w9,#{index}\nstr x9,[sp]\nb finish\n'
    country_index=b.routine('followup_person_ancestry_country_index',s)

    # Format the saved integer millionths. No floating point or rounding drift
    # changes the inherited values; the UI uses up to four decimal places.
    s='mov x21,x0\ncbz x21,finish\n'+b.string('')+'mov x27,x0\n'
    for i,(iso,name)in enumerate(COUNTRIES):
        s+=b.get('Ancestor_'+iso,'w25')+f'cbz w25,ancestry_format_next_{i}\n'
        s+='mov w9,#10000\nudiv w26,w25,w9\nmsub w25,w26,w9,w25\n'
        s+=f'cbnz w25,ancestry_fraction_{i}\nadr x28,{b.literal("%s: %d%%\n"):#x}\nb ancestry_format_{i}\nancestry_fraction_{i}:\n'
        for digits,div in [(1,1000),(2,100),(3,10),(4,1)]:
            s+=f'mov w9,#{div}\nudiv w10,w25,w9\nmsub w9,w10,w9,w25\ncbnz w9,ancestry_digits_next_{i}_{digits}\nmov w25,w10\nadr x28,{b.literal("%s: %d.%0"+str(digits)+"d%%\n"):#x}\nb ancestry_format_{i}\nancestry_digits_next_{i}_{digits}:\n'
        s+=f'ancestry_format_{i}:\nsub sp,sp,#256\nmov x0,sp\nmov w1,#256\nmov x2,x28\nadr x3,{b.literal(name):#x}\nmov w4,w26\nmov w5,w25\nbl {b.snprintf:#x}\nmov x0,sp\nbl {h.NEW_STRING:#x}\nadd sp,sp,#256\nmov x1,x0\nmov x0,x27\nmov x2,xzr\nbl 0x4df3450\nmov x27,x0\n'
        s+=f'ancestry_format_next_{i}:\n'
    s+='str x27,[sp]\nb finish';format_=b.routine('followup_format_country_ancestry',s)

    s=b.ctx(owner)+b.get('AncestryReady1105')+'cbnz w24,finish\n'+h.load_game()+'\nldr x26,[x8,#0x20]\ncbz x26,finish\nldr x0,[x26,#0xa8]\n'+f'bl {country_index:#x}\nmov w27,w0\nldr x0,[x26,#0xb8]\nbl {country_index:#x}\nmov w28,w0\n'+b.ctx(owner)
    for i,(iso,name)in enumerate(COUNTRIES):
        s+=f'cmp w27,#{i}\ncset w25,eq\ncmp w28,#{i}\ncset w24,eq\nadd w24,w24,w25\nmov w9,#500000\nmul w24,w24,w9\n'+b.put('Ancestor_'+iso)
    s+='mov x0,x21\n'+f'bl {format_:#x}\nmov x22,x0\n'+b.textptr('Ancestry1105')+b.set('AncestryReady1105',1)+'b finish'
    initialize=b.routine('followup_initialize_native_family_ancestry',s)

    # Actual selected relatives. Native Array properties are List<T>, not raw
    # Il2CppArray pointers: Count +0x18, backing array +0x10, values +0x20.
    s=b.ctx(owner)+b.get('FamilyKind1105','w27')+b.get('FamilyIndex1105','w28')+b.set('FamilyCount1105',0)+b.set('FamilyAge1105',0)+b.set('FamilyHeight1105',0)+b.text('FamilyName1105','No relative in this branch')+b.text('FamilyCountry1105','Unrecorded')+b.text('FamilyState1105','No saved person')
    s+=h.load_game()+'\nldr x26,[x8,#0x20]\ncbz x26,finish\ncmp w27,#0\nb.ne family_not_hero\nldr x25,[x8,#0x28]\n'+b.text('FamilyRelation1105','You')+'b family_selected\nfamily_not_hero:\n'
    for kind,off,label in [(1,0xa8,'Father'),(2,0xb8,'Mother')]:s+=f'cmp w27,#{kind}\nb.ne family_not_parent_{kind}\nldr x25,[x26,#{off}]\n'+b.text('FamilyRelation1105',label)+f'b family_selected\nfamily_not_parent_{kind}:\n'
    for kind,getter,label in [(3,0x327d45c,'Child'),(4,0x327d938,'Sibling'),(5,0x329a720,'Grandchild')]:
        s+=f'cmp w27,#{kind}\nb.ne family_not_list_{kind}\n'+b.text('FamilyRelation1105',label)+f'mov x0,x26\nmov x1,xzr\nbl {getter:#x}\nb family_list_ready\nfamily_not_list_{kind}:\n'
    s+='b finish\nfamily_list_ready:\ncbz x0,finish\nldr w25,[x0,#0x18]\ncbz w25,finish\nldr x26,[x0,#0x10]\ncbz x26,finish\nudiv w9,w28,w25\nmsub w28,w9,w25,w28\n'+b.put('FamilyCount1105','w25')+b.put('FamilyIndex1105','w28')+'add x26,x26,#0x20\nldr x25,[x26,w28,uxtw #3]\nfamily_selected:\ncbz x25,finish\n'
    s+='cmp w27,#2\nb.gt family_single_count_done\n'+b.set('FamilyCount1105',1)+'family_single_count_done:\nldrb w9,[x25,#0x18]\ncbz w9,family_selected_deceased\n'+b.text('FamilyState1105','Alive')+'b family_selected_state_done\nfamily_selected_deceased:\n'+b.text('FamilyState1105','Deceased')+'family_selected_state_done:\n'
    s+='mov x0,x25\nmov x1,xzr\nbl 0x2c44914\nmov x22,x0\n'+b.textptr('FamilyName1105')+'ldr w24,[x25,#0x20]\n'+b.put('FamilyAge1105')+f'mov x0,x25\nbl {b.old["v52_person_adult_height"]["stub"]:#x}\nmov w24,w0\n'+b.put('FamilyHeight1105')+f'mov x0,x25\nbl {country:#x}\ncbz x0,finish\nmov x22,x0\n'+b.textptr('FamilyCountry1105')+'b finish'
    select=b.routine('followup_select_actual_family_person',s)
    b.family_initialize=initialize;b.family_format=format_;b.family_select=select;b.family_country_index=country_index

    # Every real tree entry and actual profile initializes ancestry. The
    # family UI never changes a biological parent or creates a fictional NPC.
    s='cbz x0,finish\nmov x8,x0\n'
    keys=['genesis_v18_familytree39','genesis_v18_family35']+['genesis_v18_familybranch'+str(i)+'39'for i in range(4)]
    for i,key in enumerate(keys):s+=h.compare_key(key,'family_open1105','family_next1105_'+str(i))+'\nfamily_next1105_'+str(i)+':\n'
    s+=f'b finish\nfamily_open1105:\nbl {initialize:#x}\nbl {b.old["life_rework_refresh_context"]["stub"]:#x}\nb finish'
    b.chain('followup_real_family_before_existing_tree','v47_project_before_show',s)
    from native_v24.native_ui21 import table_value
    s=f'bl {initialize:#x}\nmov x19,x28\ncbz x19,finish\n'+b.ctx(owner)
    for key,label in [('Ancestry1105','Country ancestry:'),('BirthTraitName1105','Birth trait:')]:s+=b.string(key)+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\nmov x22,x0\n'+table_value(b,'x19',label)
    s+='b finish';b.chain('followup_native_profile_ancestry_and_trait','v21_native_hero_profile_measurements',s)
    wealth_hooks(b)
    archive_hooks(b)
    transfer_hooks(b)


def archive_hooks(b):
    from native_hooks import h
    # Actual exported IL2CPP API, verified in the pinned ELF dynsym:
    # il2cpp_string_new_utf16 = 0x223e8d4 (UTF-16 pointer, code-unit count).
    s='mov w25,w1\nmov x20,x0\nstr xzr,[sp]\nstr xzr,[sp,#8]\ncbz x20,finish\nldr w26,[x20,#16]\ncbz w26,finish\nadd x27,x20,#20\nmov w19,#0\nmov w28,#0\narchive_count1105:\ncmp w28,w26\nb.ge archive_counted1105\nldrh w9,[x27,w28,uxtw #1]\ncmp w9,#30\ncinc w19,w19,eq\nadd w28,w28,#1\nb archive_count1105\narchive_counted1105:\ncmp w9,#30\ncinc w19,w19,ne\ncbz w19,finish\nstr x19,[sp,#8]\nudiv w9,w25,w19\nmsub w25,w9,w19,w25\nmov w28,#0\nmov w19,#0\nmov w24,#0\narchive_find1105:\ncmp w28,w26\nb.ge archive_end1105\nldrh w9,[x27,w28,uxtw #1]\ncmp w9,#30\nb.ne archive_char1105\ncmp w19,w25\nb.eq archive_end1105\nadd w19,w19,#1\nadd w24,w28,#1\narchive_char1105:\nadd w28,w28,#1\nb archive_find1105\narchive_end1105:\nsub w1,w28,w24\nadd x0,x27,w24,uxtw #1\nbl 0x223e8d4\nstr x0,[sp]\nb finish'
    parse=b.routine('followup_read_one_recorded_ancestor',s)
    s=b.ctx('life_rework')+b.get('FamilyArchiveIndex1105','w25')+b.string('FamilyHistory1105')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\nmov w1,w25\n'+f'bl {parse:#x}\nmov w26,w1\ncbz x0,archive_empty1105\nmov x22,x0\n'+b.textptr('FamilyArchiveSelected1105')+b.put('FamilyArchiveCount1105','w26')+'b finish\narchive_empty1105:\n'+b.text('FamilyArchiveSelected1105','No earlier generation has been recorded yet. Continue as a child to begin this archive.')+b.set('FamilyArchiveCount1105',0)+'b finish'
    b.family_archive=b.routine('followup_refresh_selected_ancestor',s)


def wealth_hooks(b):
    from native_hooks import h
    s='str xzr,[sp]\ncbz x0,finish\nldrb w9,[x0,#0x18]\ncbz w9,finish\nldr x0,[x0,#0x70]\ncbz x0,finish\nmov x1,xzr\nbl 0x2c642f4\nfcvtzs x9,d0\nstr x9,[sp]\nb finish'
    value=b.routine('followup_actual_relative_net_worth',s)
    s=b.ctx('life_rework')+h.load_game()+'\nldr x25,[x8,#0x20]\ncbz x25,finish\nldr x0,[x25,#0xe8]\ncbz x0,finish\nmov x1,xzr\nbl 0x2a6a854\nfcvtzs x19,d0\n'
    for offset in [0xa8,0xb8,0xd8]:s+=f'ldr x0,[x25,#{offset}]\nbl {value:#x}\nadd x19,x19,x0\n'
    for i,getter in enumerate([0x327d45c,0x327d938,0x329a720]):
        s+=f'mov x0,x25\nmov x1,xzr\nbl {getter:#x}\ncbz x0,wealth_list_done_{i}\nldr w26,[x0,#0x18]\nldr x27,[x0,#0x10]\ncbz x27,wealth_list_done_{i}\nadd x27,x27,#0x20\nmov w28,#0\nwealth_list_loop_{i}:\ncmp w28,w26\nb.ge wealth_list_done_{i}\nldr x0,[x27,w28,uxtw #3]\nbl {value:#x}\nadd x19,x19,x0\nadd w28,w28,#1\nb wealth_list_loop_{i}\nwealth_list_done_{i}:\n'
    s+='sub sp,sp,#64\nmov x0,sp\nmov w1,#64\n'+f'adr x2,{b.literal("%lld"):#x}\nmov x3,x19\nbl {b.snprintf:#x}\nmov x0,sp\nbl {h.NEW_STRING:#x}\nadd sp,sp,#64\nmov x22,x0\n'+b.textptr('FamilyWealthText1105')+'b finish'
    wealth=b.routine('followup_sum_actual_family_records',s)
    b.chain('followup_family_wealth_before_tree','v47_project_before_show',
            'cbz x0,finish\nmov x8,x0\n'+h.compare_key('genesis_v18_familytree39','family_wealth_open','finish')+f'\nfamily_wealth_open:\nbl {wealth:#x}\nb finish')


def context_at(b,life,age,owner='life_rework'):
    return b.string(owner)+f'mov x1,x0\nmov x0,{life}\nmov w2,{age}\nmov x3,xzr\nbl 0x32800fc\ncbz x0,finish\n'


def transfer_hooks(b):
    from native_hooks import h
    state=b.state;country=b.family_country_index
    # The audited signature is this=new Life, child, old Life, d0/d1 finances.
    # Root only managed objects; replacement/error paths release prior handles.
    s=f'adr x28,{state:#x}\n'
    for offset in [0,8,16]:s+=f'ldr x0,[x28,#{offset}]\ncbz x0,family_old_handle_{offset}\nbl 0x223e784\nstr xzr,[x28,#{offset}]\nfamily_old_handle_{offset}:\n'
    s+=f'bl {b.family_initialize:#x}\n'
    for offset,reg in [(0,2),(8,0),(16,1)]:
        s+=f'ldr x0,[sp,#{reg*8}]\ncbz x0,family_handle_new_{offset}\nmov w1,#0\nbl 0x223e704\nstr x0,[x28,#{offset}]\nfamily_handle_new_{offset}:\n'
    s+='b finish';b.install('followup_capture_real_generation_transition',0x3282e04,s)
    s=f'adr x28,{state:#x}\nldr x0,[x28]\ncbz x0,finish\nbl 0x223e73c\ncbz x0,finish\nmov x25,x0\nldr x0,[x28,#8]\ncbz x0,finish\nbl 0x223e73c\ncbz x0,finish\nmov x26,x0\n'
    # Identify the previous played parent by native full name in the new Life.
    # The new Life already contains native father/mother records at this tail.
    s+='mov x0,x25\nmov x1,xzr\nbl 0x327d39c\ncbz x0,finish\nmov x19,x0\nmov x1,xzr\nbl 0x2c44914\nmov x20,x0\n'+f'adr x8,{state:#x}\nstr wzr,[x8,#92]\n'+'ldr x0,[x26,#0xa8]\ncbz x0,family_other_is_mother\nmov x1,xzr\nbl 0x2c44914\nmov x1,x20\nmov x2,xzr\nbl 0x4dfe080\ncbnz w0,family_other_is_mother\nldr x0,[x26,#0xa8]\nb family_other_ready\nfamily_other_is_mother:\n'+f'adr x8,{state:#x}\nmov w9,#1\nstr w9,[x8,#92]\n'+'ldr x0,[x26,#0xb8]\nfamily_other_ready:\n'
    s+=f'bl {country:#x}\nmov w28,w0\nldr w24,[x19,#0x20]\n'+context_at(b,'x25','w24','life_v18')+'mov x21,x0\n'+b.get('AdultHeight','w20',178)
    s+='mov x0,x26\nmov x1,xzr\nbl 0x327d39c\ncbz x0,finish\nldr w24,[x0,#0x20]\n'+context_at(b,'x26','w24','life_v18')+'mov x21,x0\n'
    s+=f'adr x8,{state:#x}\nldr w9,[x8,#92]\ncbz w9,family_played_mother_height\n'+b.put('PlayedFatherHeight1105','w20')+'b family_played_height_done\nfamily_played_mother_height:\n'+b.put('PlayedMotherHeight1105','w20')+'family_played_height_done:\n'+b.set('HeightRevision1105',0)+b.set('HeightModel52',0)+b.set('HeightSource51',1)
    s+='ldr w24,[x19,#0x20]\n'+context_at(b,'x25','w24')+'mov x27,x0\n'
    s+='mov x0,x26\nmov x1,xzr\nbl 0x327d39c\ncbz x0,finish\nldr w24,[x0,#0x20]\n'+context_at(b,'x26','w24')+'mov x26,x0\n'
    s+='mov w20,#0\n'
    for index,(iso,name)in enumerate(COUNTRIES):
        s+='mov x21,x27\n'+b.get('Ancestor_'+iso)+'add w24,w24,w20\nand w20,w24,#1\nlsr w24,w24,#1\n'+f'cmp w28,#{index}\nmov w9,#500000\ncsel w9,w9,wzr,eq\nadd w24,w24,w9\nmov x21,x26\n'+b.put('Ancestor_'+iso)
    s+='mov x21,x27\n'+b.get('FamilyGenerations1105')+'add w24,w24,#1\nmov x21,x26\n'+b.put('FamilyGenerations1105')
    s+='mov x21,x27\n'+b.get('FamilyFamous1105','w24')+'mov w25,w24\nmov x0,x19\nmov x1,xzr\nbl 0x2c42394\nfcvtzs w9,s0\ncmp w9,#60\ncinc w25,w25,ge\nmov x21,x26\n'+b.put('FamilyFamous1105','w25')
    s+='mov x21,x26\n'+b.set('AncestryReady1105',1)+'mov x0,x26\n'+f'bl {b.family_format:#x}\nmov x22,x0\n'+b.textptr('Ancestry1105')
    # The archive records every played ancestor, without inventing earlier
    # grandparents for a save that never contained those people.
    def read(key,ctx):return f'mov x0,{ctx}\n'+b.string(key)+'mov x1,x0\n'+f'mov x0,{ctx}\nmov x2,xzr\nbl 0x3059934\n'
    s+=read('FamilyHistory1105','x27')+'mov x25,x0\nmov x0,x19\nmov x1,xzr\nbl 0x2c44914\nmov x1,x0\nmov x0,x25\nmov x2,xzr\nbl 0x4df3450\nmov x25,x0\n'+b.string('\n')+'mov x1,x0\nmov x0,x25\nmov x2,xzr\nbl 0x4df3450\nmov x25,x0\n'
    s+=read('Ancestry1105','x27')+'mov x1,x0\nmov x0,x25\nmov x2,xzr\nbl 0x4df3450\nmov x25,x0\n'+b.string('\x1e')+'mov x1,x0\nmov x0,x25\nmov x2,xzr\nbl 0x4df3450\nmov x22,x0\nmov x21,x26\n'+b.textptr('FamilyHistory1105')
    for offset in [0,8,16]:s+=f'adr x28,{state:#x}\nldr x0,[x28,#{offset}]\ncbz x0,family_release_{offset}\nbl 0x223e784\nstr xzr,[x28,#{offset}]\nfamily_release_{offset}:\n'
    s+='b finish';transfer=b.routine('followup_inherit_actual_parent_country_ancestry',s)
    # The only normal return is preceded by the original callee-save epilogue.
    b.install('followup_save_ancestry_after_child_becomes_hero',0x328efe4,f'bl {transfer:#x}\nb finish')
