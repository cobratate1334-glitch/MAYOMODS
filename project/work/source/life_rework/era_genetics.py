"""Period-aware draft/NPC hair and one-time native NPC health variation."""
from native_hooks import h
STARTS=[0,1980,1960,1920,1900,1960,1900,1920,1940,1,1960,1900,1,1,1,1970]

def hooks(b):
    # These are availability choices for the supplied hairstyles, not dates
    # claiming that braids, buns or naturally textured hair were invented.
    s='mov w9,#1\nstr x9,[sp]\ncmp w0,#15\nb.hi finish\n'
    for style,year in enumerate(STARTS):
        s+=f'cmp w0,#{style}\nb.ne hair_era_next_{style}\ncmp w1,#{year}\ncset w9,ge\nstr x9,[sp]\nb finish\nhair_era_next_{style}:\n'
    s+='b finish';allowed=b.routine('life_rework_hair_available_in_year',s)
    era=b.states['era44']['va']
    for i in range(1,16):
        r=b.resolved('v52_preview_Hair_'+str(i));s=r['source'];needle=h.save()+'\n'
        check=f'adr x8,{era:#x}\nldr w1,[x8]\ncmp w1,#1\nmov w9,#2026\ncsel w1,w1,w9,ge\nmov w0,#{i}\nbl {allowed:#x}\ncbnz w0,hair_era_preview_ok_{i}\nmov w0,#1940\nbl {b.trace23:#x}\nb finish\nhair_era_preview_ok_{i}:\nldr x0,[sp]\n'
        b.redirect(r['name'],s.replace(needle,needle+check,1))
    # Changing the starting year after browsing hair must not commit a future
    # hairstyle. Run the same availability rule at the real birth boundary.
    r=b.resolved('v52_commit_newlife_appearance');source=r['source'];check=f'adr x28,{b.state52:#x}\nldr w0,[x28,#32]\nadr x8,{era:#x}\nldr w1,[x8]\ncmp w1,#1\nmov w9,#2026\ncsel w1,w1,w9,ge\nbl {allowed:#x}\ncbnz w0,hair_birth_period_ok\nmov w9,#9\nstr w9,[x28,#32]\nhair_birth_period_ok:\n'
    b.redirect(r['name'],source.replace(h.save()+'\n',h.save()+'\n'+check,1))
    r=b.resolved('v52_npc_assets_before_native_serialization');s=r['source'].replace('cmp w26,#220','cmp w26,#85').replace('cmp w26,#120','cmp w26,#35')
    check=f'bl {b.old["v45_current_year"]["stub"]:#x}\nmov w1,w0\nmov w0,w26\nbl {allowed:#x}\ncbnz w0,npc_hair_era_ok\nmov w26,#9\nnpc_hair_era_ok:\n'
    needle='add w26,w26,#1\nmov x0,x27';assert needle in s;s=s.replace(needle,'add w26,w26,#1\n'+check+'mov x0,x27',1);b.redirect(r['name'],s)
    # Script.SetupForPerson's successful tail owns a real SimThirdPersonScript
    # in x20 and SimPerson in x19. It runs when that person's script is made,
    # after native disease destiny, and is not a per-profile reroll hook.
    seed=b.old['v52_person_seed']['stub']
    s=f'cbz x19,finish\ncbz x20,finish\nldr w9,[x19,#0x20]\ncmp w9,#4\nb.lt finish\nmov x0,x19\nbl {seed:#x}\nmov w9,#400\nudiv w10,w0,w9\nmsub w9,w10,w9,w0\ncbnz w9,finish\n'
    s+=b.string('sickle cell disease')+'mov x1,xzr\nbl 0x26d23a0\ncbz x0,finish\nmov x26,x0\nmov x0,x20\nmov x1,x26\nmov x2,xzr\nbl 0x2c5d484\ncbnz w0,finish\nmov x0,x20\nmov x1,x26\nldr w2,[x19,#0x20]\nmov x3,xzr\nbl 0x2c5ca40\nb finish'
    b.install('life_rework_npc_native_genetic_condition',0x2c4aa14,s)
    # Keep serialized era IDs and owned wardrobe slots. Offer dates and short
    # era labels use the calendar directly rather than the old four labels.
    r=b.resolved('v44_calendar_and_stock');source=r['source'];tail='b finish\nfinish:';assert tail in source
    code=b.ctx('era44')+b.get('Year','w25')
    for year,name,description in [(2020,'2020s','Electric cars, short videos and current streetwear.'),(2010,'2010s','Smartphones, streaming and relaxed streetwear.'),(2000,'2000s','Mobile phones, early social sites and digital recording.'),(1980,'1980s','Home computers, cassettes and sportswear.'),(1960,'1960s','Television, vinyl, bobs and bright fashion.'),(1940,'1940s','Radio, utility clothing and service caps.'),(1900,'1900s','Print, early motorcars and formal hats.')]:
        code+=f'cmp w25,#{year}\nb.lt wardrobe_era_next_{year}\n'+b.text('EraName',name)+b.text('ShopDescription',description)+f'b wardrobe_era_done\nwardrobe_era_next_{year}:\n'
    code+='wardrobe_era_done:\n'
    for ident,start in [(6,1914),(19,1996),(20,1980),(21,1980),(22,1980),(24,1910),(27,2000)]:
        code+=f'cmp w25,#{start}\nb.ge wardrobe_item_exists_{ident}\n'+b.set('Available'+str(ident),0)+b.text('Label'+str(ident),'Available from '+str(start))+f'b wardrobe_item_done_{ident}\nwardrobe_item_exists_{ident}:\n'
        if ident in [20,21,22]:code+=b.set('Available'+str(ident),1)+b.text('Label'+str(ident),'In stock · Everyday styles')
        code+=f'wardrobe_item_done_{ident}:\n'
    b.redirect(r['name'],source.replace(tail,code+tail,1))
    # A website left open across a calendar change must obey the same rule as
    # its social-media row. All website mutations still execute on Unity's thread.
    from web_experience.schema import definitions
    _,_,commands,_=definitions();last=max(c['id']for c in commands if not c['key'].startswith('church_'))
    r=b.resolved('web_execute_authored_command');source=r['source'];guard=f'cmp w20,#1\nb.lt finish\ncmp w20,#{last}\nb.gt web_era_available\nbl {b.old["v45_current_year"]["stub"]:#x}\ncmp w0,#2006\nb.ge web_era_available\nmov w9,#5\nstr w9,[x28,#28]\nb finish\nweb_era_available:\n'
    b.redirect(r['name'],source.replace(h.save()+'\n',h.save()+'\n'+guard,1))
