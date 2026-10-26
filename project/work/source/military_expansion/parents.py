"""Bind parent actions to the actual parent closure, never the preview cache."""
from native_hooks import h

def hooks(b):
    state=b.state
    # In the original RelationshipItemArrayForParent, x20 is DisplayClass100_0;
    # its parent field +0x10 is assigned from the method's x1 at 0x30d26a0.
    # x19 has become the menu ArrayList by this boundary. Preserve both roles.
    s='ldr x26,[x20,#0x10]\ncbz x26,finish\n'+h.load_game()+'\nldr x27,[x8,#0x20]\ncbz x27,finish\nldr x25,[x8,#0x28]\ncbz x25,finish\nldr x9,[x27,#0xa8]\ncmp x26,x9\nb.eq father1108\nldr x9,[x27,#0xb8]\ncmp x26,x9\nb.ne finish\nmov w24,#1\nb parent_bound1108\nfather1108:\nmov w24,#0\nparent_bound1108:\n'
    s+=f'adr x28,{state:#x}\nadd x28,x28,w24,uxtw #4\n'
    for off in [0,8]:
        s+=f'ldr x0,[x28,#{off}]\ncbz x0,parent_release1108_{off}\nbl 0x223e784\nparent_release1108_{off}:\nstr xzr,[x28,#{off}]\n'
    s+='mov x0,x25\nmov w1,#0\nbl 0x223e704\nstr x0,[x28]\nmov x0,x26\nmov w1,#0\nbl 0x223e704\nstr x0,[x28,#8]\ncbnz w24,mother_key1108\n'+b.string('FatherStory1108')+'b parent_inject1108\nmother_key1108:\n'+b.string('MotherStory1108')+f'parent_inject1108:\nmov x1,x0\nmov x0,x19\nmov x2,xzr\nbl {h.INJECT:#x}\nb finish'
    # Replace only the old Parent injection at its site; sibling/friend routes
    # retain the previous implementation. Calling the old stub would duplicate it.
    b.write(0x30d3af8,'ldr x0,[x25]','replace shared parent story injection')
    # The overwritten instruction is verified against the retained original.
    old=b.old['v21_relationship_story_menu_Parent'];assert old['original'].replace(' ','')=='ldrx0,[x25]'
    b.install('military1108_parent_role_menu',0x30d3af8,s)
    # The route encodes the role, and both rooted receivers must match the
    # actual live native family before any values are generated.
    code='cbz x2,finish\nmov x8,x2\n'
    for role in [0,1]:
        code+=h.compare_key('scenario.lifeRework.parent_'+str(role)+'1108','parent_open1108_'+str(role),'parent_next1108_'+str(role))+'\nparent_next1108_'+str(role)+':\n'
    code+='b finish\n'
    for role,off in [(0,0xa8),(1,0xb8)]:
        code+=f'parent_open1108_{role}:\nadr x28,{state+role*16:#x}\n'+h.load_game()+'\nldr x27,[x8,#0x20]\ncbz x27,parent_unavailable1108\nldr x25,[x8,#0x28]\ncbz x25,parent_unavailable1108\nldr x0,[x28]\ncbz x0,parent_unavailable1108\nbl 0x223e73c\ncmp x0,x25\nb.ne parent_unavailable1108\nldr x0,[x28,#8]\ncbz x0,parent_unavailable1108\nbl 0x223e73c\ncbz x0,parent_unavailable1108\n'+f'ldr x9,[x27,#{off}]\ncmp x0,x9\nb.ne parent_unavailable1108\nmov x26,x0\nmov w1,#0\nbl {b.old["selected_relationship_details21"]["stub"]:#x}\n'
        code+=b.ctx('relationship21')+b.text('ParentAvailability1108','')
        for method,key in [(0x2c42324,'Discipline1108'),(0x2c423d4,'Loyalty1108'),(0x2c42384,'Generosity1108')]:
            code+=f'mov x0,x26\nmov x1,xzr\nbl {method:#x}\nfcvtzs w24,s0\n'+b.put(key)
        code+=b.get('Discipline1108')+f'cmp w24,#66\nb.ge parent_focused1108_{role}\ncmp w24,#33\nb.lt parent_spontaneous1108_{role}\n'+b.text('ParentCharacter1108','Balanced: comfortable with plans but willing to change them.')+f'b parent_character_done1108_{role}\nparent_focused1108_{role}:\n'+b.text('ParentCharacter1108','Focused: follows routines and prefers clear plans.')+f'b parent_character_done1108_{role}\nparent_spontaneous1108_{role}:\n'+b.text('ParentCharacter1108','Spontaneous: prefers flexibility to strict routines.')+f'parent_character_done1108_{role}:\n'
        code+='ldrb w9,[x26,#0x18]\ncbnz w9,parent_living1108_'+str(role)+'\n'+b.text('ParentAvailability1108','This is their saved life record. They have died; activities together are unavailable.')+'parent_living1108_'+str(role)+':\nb finish\n'
    code+='parent_unavailable1108:\n'+b.ctx('relationship21')+b.text('SelectedName1106','Parent record unavailable')+b.set('SelectedAge1106',0)+b.text('BirthCountry1106','Unavailable')+b.set('Connection',0)+b.text('ParentAvailability1108','This menu no longer belongs to the current life. Close it and open the parent again.')
    for key in ['Personality','Hobby','Ambition','Belief','Story','ParentCharacter1108']:code+=b.text(key,'Unavailable')
    for key in ['Discipline1108','Loyalty1108','Generosity1108']:code+=b.set(key,0)
    code+='b finish';b.chain('military1108_resolve_bound_parent','v47_bind_native_scenario',code)
