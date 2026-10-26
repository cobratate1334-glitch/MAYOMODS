"""Actual parent bindings for the existing native relationship menus."""

GC_NEW=0x223e704
GC_TARGET=0x223e73c
GC_FREE=0x223e784
PARENT_CAPTURE=0x30d26a4
PARENT_INJECT=0x30d3af8


def build(a,base):
    from playable_repair.family_service_content import build as content
    content(a,base)


def replace_roots(address):
    """Each slot owns its own pointer-sized IL2CPP GC handles."""
    s=f'adr x28,{address:#x}\n'
    for offset in (0,8):
        s+=f'ldr x0,[x28,#{offset}]\ncbz x0,release_{address:x}_{offset}\nbl {GC_FREE:#x}\nrelease_{address:x}_{offset}:\nstr xzr,[x28,#{offset}]\n'
    return s+f'mov x0,x25\nmov w1,#0\nbl {GC_NEW:#x}\nstr x0,[x28]\nmov x0,x26\nmov w1,#0\nbl {GC_NEW:#x}\nstr x0,[x28,#8]\n'


def hooks(b):
    from native_hooks import h
    state=b.states['playable_repair']['va']
    legacy=b.states['military_expansion']['va']
    # Here x19 is the actual SimParent. Later native list construction changes
    # x20 from its closure to a ListItem, invalidating the former late read.
    capture=f'adr x28,{state:#x}\nstr wzr,[x28,#20]\nmov x26,x19\ncbz x26,finish\n'+h.load_game()+'\nldr x27,[x8,#0x20]\ncbz x27,finish\nldr x25,[x8,#0x28]\ncbz x25,finish\nldr x9,[x27,#0xa8]\ncmp x26,x9\nb.eq father1111\nldr x9,[x27,#0xb8]\ncmp x26,x9\nb.eq mother1111\nmov x0,x26\nmov x1,xzr\nbl 0x2c3f8c0\ncbz w0,finish\nmov w24,#2\nb parent_capture1111\nfather1111:\nmov w24,#0\nb parent_capture1111\nmother1111:\nmov w24,#1\nparent_capture1111:\n'
    capture+=replace_roots(state)+'str w24,[x28,#16]\nmov w9,#1\nstr w9,[x28,#20]\ncmp w24,#2\nb.eq finish\ncbnz w24,root_mother1111\n'
    capture+=replace_roots(legacy)+'b finish\nroot_mother1111:\n'+replace_roots(legacy+16)+'b finish'
    b.install('playable1111_capture_actual_parent',PARENT_CAPTURE,capture)

    inject=f'adr x28,{state:#x}\nldr w9,[x28,#20]\ncbz w9,finish\n'+h.load_game()+'\nldr x25,[x8,#0x28]\ncbz x25,finish\nldr x0,[x28]\ncbz x0,finish\n'+f'bl {GC_TARGET:#x}\ncmp x0,x25\nb.ne finish\nldr x0,[x28,#8]\ncbz x0,finish\nbl {GC_TARGET:#x}\ncbz x0,finish\nldr w24,[x28,#16]\ncbz w24,inject_father1111\ncmp w24,#1\nb.eq inject_mother1111\n'
    inject+=b.string('StepparentStory1111')+'b inject_parent1111\ninject_father1111:\n'+b.string('FatherStory1108')+'b inject_parent1111\ninject_mother1111:\n'+b.string('MotherStory1108')+f'inject_parent1111:\nmov x1,x0\nmov x0,x19\nmov x2,xzr\nbl {h.INJECT:#x}\nb finish'
    b.write(PARENT_INJECT,'ldr x0,[x25]','replace invalid late parent closure read')
    b.install('playable1111_inject_actual_parent',PARENT_INJECT,inject)

    # Biological routes keep their stable IDs and their established resolver.
    # A stepparent gets the same actual-person refresh through a rooted binding.
    code='cbz x2,finish\nmov x8,x2\n'+h.compare_key('scenario.lifeRework.stepparent1111','step_open1111','step_next1111')+'\nstep_next1111:\nb finish\nstep_open1111:\n'
    code+=f'adr x28,{state:#x}\nldr w9,[x28,#16]\ncmp w9,#2\nb.ne step_unavailable1111\n'+h.load_game()+'\nldr x25,[x8,#0x28]\ncbz x25,step_unavailable1111\nldr x0,[x28]\ncbz x0,step_unavailable1111\n'+f'bl {GC_TARGET:#x}\ncmp x0,x25\nb.ne step_unavailable1111\nldr x0,[x28,#8]\ncbz x0,step_unavailable1111\nbl {GC_TARGET:#x}\ncbz x0,step_unavailable1111\nmov x26,x0\nmov x1,xzr\nbl 0x2c3f8c0\ncbz w0,step_unavailable1111\nmov x0,x26\nmov w1,#0\nbl {b.old["selected_relationship_details21"]["stub"]:#x}\n'
    code+=b.ctx('relationship21')+b.text('ParentAvailability1108','')
    for method,key in [(0x2c42324,'Discipline1108'),(0x2c423d4,'Loyalty1108'),(0x2c42384,'Generosity1108')]:
        code+=f'mov x0,x26\nmov x1,xzr\nbl {method:#x}\nfcvtzs w24,s0\n'+b.put(key)
    code+=b.get('Discipline1108')+'cmp w24,#66\nb.ge step_focused1111\ncmp w24,#33\nb.lt step_spontaneous1111\n'+b.text('ParentCharacter1108','Easygoing. Likes a plan but can change it.')+'b step_character_done1111\nstep_focused1111:\n'+b.text('ParentCharacter1108','Focused. Likes routines and clear plans.')+'b step_character_done1111\nstep_spontaneous1111:\n'+b.text('ParentCharacter1108','Spontaneous. Likes freedom and surprises.')+'step_character_done1111:\nldrb w9,[x26,#0x18]\ncbnz w9,finish\n'+b.text('ParentAvailability1108','They have died. This is their life record.')+'b finish\nstep_unavailable1111:\n'+b.ctx('relationship21')+b.text('SelectedName1106','Parent record unavailable')+b.set('SelectedAge1106',0)+b.text('BirthCountry1106','Unknown')+b.text('ParentAvailability1108','Close this page. Open your parent again.')
    for key in ['Personality','Hobby','Ambition','Belief','Story','ParentCharacter1108']:code+=b.text(key,'Unavailable')
    for key in ['Discipline1108','Loyalty1108','Generosity1108']:code+=b.set(key,0)
    code+='b finish'
    b.chain('playable1111_resolve_stepparent','v47_bind_native_scenario',code)

    # Read only canonical integer fields from the versioned 1108 save string.
    # Bounds are checked before every UTF-16 match. A prefix inside another
    # key/value never matches, and malformed or missing data denies the permit.
    def number(key):
        s='str xzr,[sp]\ncbz x0,finish\nmov x26,x0\nldr w27,[x26,#16]\nmov w9,#8192\ncmp w27,w9\nb.hi finish\nmov w25,#0\nscan1111:\n'
        s+=f'add w9,w25,#{len(key)+1}\ncmp w9,w27\nb.hs finish\ncbz w25,match1111\nsub w9,w25,#1\nadd x10,x26,#20\nldrh w9,[x10,w9,uxtw #1]\ncmp w9,#38\nb.ne next1111\nmatch1111:\nadd x10,x26,#20\nadd x10,x10,w25,uxtw #1\n'
        for i,char in enumerate(key+'='):
            s+=f'ldrh w9,[x10,#{i*2}]\ncmp w9,#{ord(char)}\nb.ne next1111\n'
        s+=f'add w25,w25,#{len(key)+1}\nmov w24,#0\nmov w23,#0\ndigits1111:\ncmp w25,w27\nb.hs number_done1111\nadd x10,x26,#20\nldrh w9,[x10,w25,uxtw #1]\ncmp w9,#38\nb.eq number_done1111\nsub w9,w9,#48\ncmp w9,#9\nb.hi finish\nadd w23,w23,#1\ncmp w23,#6\nb.hi finish\nmov w10,#10\nmadd w24,w24,w10,w9\nadd w25,w25,#1\nb digits1111\nnumber_done1111:\ncbz w23,finish\nstr x24,[sp]\nb finish\nnext1111:\nadd w25,w25,#1\nb scan1111'
        return b.routine('playable1111_read_'+key,s)
    ready=number('fieldReady');ready_year=number('fieldReadyYear')
    getstate=b.string('MilitaryState1108')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\n'
    permit=b.ctx('life_rework')+b.set('FieldReady1111',0)+h.load_occupation()+'\ncbz x8,finish\nldr w9,[x8,#16]\ncmp w9,#3\nb.ne finish\n'+b.get('War')+'cbz w24,finish\n'+b.get('WarSide')+'cbz w24,finish\n'+getstate+f'bl {ready:#x}\ncmp w0,#1\nb.ne finish\n'+getstate+f'bl {ready_year:#x}\nmov w25,w0\n'+b.get('Year')+'cmp w25,w24\nb.ne finish\n'+b.set('FieldReady1111',1)+'b finish'
    permit_va=b.routine('playable1111_refresh_field_permit',permit)
    snapshot=b.resolved('military1108_snapshot');source=snapshot['source']
    marker='snapshot_end1108:\n';assert source.count(marker)==1
    b.redirect('military1108_snapshot',source.replace(marker,marker+f'bl {permit_va:#x}\n'))
