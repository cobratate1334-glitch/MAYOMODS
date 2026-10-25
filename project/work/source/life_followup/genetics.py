"""Saved birth traits; the existing face editor remains authoritative."""
from life_rework.content import p,scene,menu,set_,seq

TRAITS=[
 ('No rare birth trait','No added rare birth trait.'),
 ('Rh-null blood','A rare blood type. Compatible transfusions can be difficult to find.'),
 ('Heterochromia','Your eyes have different colours. This also uses the existing native eye pattern.'),
 ('Supertaster','You notice stronger flavours and may be more sensitive to bitter foods.'),
 ('Chimerism','Some cells carry a different genetic pattern. Effects vary between people.'),
 ('High bone density · LRP5','A variant associated with denser bones. It is not protection from every injury.'),
 ('Hypertrichosis','More body or facial hair than usual. This does not change your personality.'),
 ('CCR5 variant','Reduced susceptibility to some strains of HIV. This is not complete immunity.'),
 ('Potential tetrachromacy','An inherited variation that may allow finer colour discrimination.'),
 ('Short-sleep trait · DEC2','You may naturally need less sleep. It is not a reason to skip rest when unwell.')]


def build(a,base):
    a.prop('BirthTrait1105',0,0,len(TRAITS)-1);a.prop('BirthTraitReady1105',0,0,1)
    a.string('BirthTraitName1105',TRAITS[0][0]);a.string('BirthTraitInfo1105',TRAITS[0][1])
    a.page('birth_trait1105','Your birth trait',p('BirthTraitInfo1105'),[('Family and ancestry',menu('genesis_v18_familytree39')),('Back to game','')],'brain',stats=[('Trait',p('BirthTraitName1105'))])
    from life_followup.family import build as family
    family(a,base)


def native(b):
    from native_hooks import h
    extra=b.newlife31;state=b.state;ui=b.state52
    add=b.old['newlife31_add_rounded_option']['stub'];rebuild=b.old['v53_rebuild_appearance_page']['stub']
    header=b.old['v53_appearance_page_header']['stub']
    def guard(mode=None):
        s=f'cbz x0,finish\nmov x19,x0\nadr x26,{extra:#x}\nldr w9,[x26,#64]\n'
        if mode is not None:s+=f'cmp w9,#{mode}\nb.ne finish\n'
        else:s+='cmp w9,#135\nb.lt finish\ncmp w9,#138\nb.gt finish\n'
        return s+'ldr x0,[x26,#72]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\nldr x27,[x19,#0x20]\ncbz x27,finish\nldr w9,[x27,#0xb4]\ncmp w9,#6\nb.ne finish\nldrb w9,[x27,#0x110]\ncbnz w9,finish\n'
    def mode(n):return f'adr x8,{extra:#x}\nmov w9,#{n}\nstr w9,[x8,#64]\nadr x8,{ui:#x}\nstr w9,[x8]\nmov x0,x19\nbl {rebuild:#x}\nb finish'
    pages={}
    for n in range(135,139):pages[n]=b.routine('followup_birth_trait_page_'+str(n),guard()+mode(n))
    open_=b.routine('followup_open_birth_traits',guard(130)+f'adr x8,{state:#x}\nldr w9,[x8,#48]\nstr w9,[x8,#52]\n'+mode(135))
    choices={}
    for value in range(-1,len(TRAITS)):
        choices[value]=b.routine('followup_select_birth_trait_'+str(value).replace('-','random'),guard()+f'adr x8,{state:#x}\nmov w9,#{value}\nstr w9,[x8,#52]\nmov x0,x19\nbl {header:#x}\nb finish')
    save=guard()+f'adr x8,{state:#x}\nldr w9,[x8,#52]\nstr w9,[x8,#48]\ncmp w9,#2\nb.ne birth_trait_eye_done\nadr x8,{b.newlife24:#x}\nmov w9,#5\nstr w9,[x8,#24]\nadr x8,{ui:#x}\nstr wzr,[x8,#44]\nbirth_trait_eye_done:\n'+mode(130)
    save=b.routine('followup_save_birth_trait',save);cancel=b.routine('followup_cancel_birth_trait',guard()+mode(130))
    old=b.resolved('v53_organized_appearance_setup');s=old['source'];assert 'cmp w24,#134' in s
    s=s.replace('cmp w24,#134','cmp w24,#138',1)
    marker='cmp w24,#130\nb.ne setup53_hub_next_130';assert marker in s
    code=''
    values=list(range(-1,len(TRAITS)))
    def button(label,callback):return b.string(label)+f'mov x1,x0\nmov x0,x19\nadr x2,{callback:#x}\nmov w3,#1\nbl {add:#x}\n'
    for n in range(135,139):
        code+=f'cmp w24,#{n}\nb.ne birth_setup_next_{n}\n'
        for v in values[(n-135)*3:(n-134)*3]:code+=button('Random at birth'if v==-1 else TRAITS[v][0],choices[v])
        if n<138:code+=button('More birth traits',pages[n+1])
        if n>135:code+=button('Previous birth traits',pages[n-1])
        code+=button('Save & back',save)+button('Back without saving',cancel)+f'b return_custom\nbirth_setup_next_{n}:\n'
    s=s.replace(marker,code+marker,1)
    # Add the one selector to the existing appearance root, before its back row.
    back=b.strings['Back to New Life'];needle=f'adrp x0, {back&~4095:#x}\nadd x0, x0, #{back&4095}\n'
    assert needle in s;s=s.replace(needle,button('Birth traits',open_)+needle,1);b.redirect(old['name'],s)
    old=b.resolved('v53_appearance_page_header');s=old['source'];marker=h.save()+'\n';assert s.startswith(marker)
    code=f'adr x8,{extra:#x}\nldr w9,[x8,#64]\ncmp w9,#135\nb.lt birth_header_original\ncmp w9,#138\nb.gt birth_header_original\nmov x19,x0\ncbz x19,finish\n'+b.string('Birth traits')+'mov x22,x0\n'
    code+=f'adr x8,{state:#x}\nldr w25,[x8,#52]\n'
    for v in values:
        label='Random at birth: a small chance of a rare trait.'if v==-1 else TRAITS[v][0]+'. '+TRAITS[v][1]
        code+=f'cmp w25,#{v}\nb.ne birth_header_next_{v+1}\n'+b.string(label)+f'mov x23,x0\nb birth_header_set\nbirth_header_next_{v+1}:\n'
    code+='b finish\nbirth_header_set:\nldr x0,[x19,#0x38]\ncbz x0,finish\nmov x1,x22\nmov x2,xzr\nbl 0x3024244\nldr x0,[x19,#0x68]\ncbz x0,finish\nmov x1,x23\nmov x2,xzr\nbl 0x3024244\nb finish\nbirth_header_original:\n'
    b.redirect(old['name'],marker+code+s[len(marker):])
    # Reset only a fresh draft. Merely reopening a page preserves its choice.
    old=b.resolved('v21_new_life_native_buttons');s=old['source'];marker='root_new31:\n';assert marker in s
    s=s.replace(marker,marker+f'adr x8,{state:#x}\nmov w9,#-1\nstr w9,[x8,#48]\nstr w9,[x8,#52]\nmov w9,#1\nstr w9,[x8,#60]\n',1);b.redirect(old['name'],s)
    # Actual birth consumes the committed selector and writes a normal GFC.
    s=b.ctx('life_rework')+f'adr x8,{state:#x}\nldr w25,[x8,#48]\nldr w9,[x8,#60]\nstr wzr,[x8,#60]\ncbnz w9,birth1105_draft_ready\nmov w25,#-1\nbirth1105_draft_ready:\ncmp w25,#0\nb.ge birth1105_chosen\n'
    s+=h.load_game()+'\nldr x0,[x8,#0x28]\n'+f'bl {b.old["v52_person_seed"]["stub"]:#x}\nmov w9,#500\nudiv w10,w0,w9\nmsub w9,w10,w9,w0\nmov w25,#0\ncbnz w9,birth1105_chosen\nmov w9,#9\nudiv w10,w0,w9\nmsub w25,w10,w9,w0\nadd w25,w25,#1\nbirth1105_chosen:\n'
    s+=b.put('BirthTrait1105','w25')+b.set('BirthTraitReady1105',1)
    for i,(name,info)in enumerate(TRAITS):s+=f'cmp w25,#{i}\nb.ne birth1105_next_{i}\n'+b.text('BirthTraitName1105',name)+b.text('BirthTraitInfo1105',info)+f'b finish\nbirth1105_next_{i}:\n'
    s+='b finish';birth=b.routine('followup_apply_saved_birth_trait',s)
    b.chain('followup_birth_trait_at_real_birth','v42_birth_genetics_and_portrait',f'bl {birth:#x}\nb finish')
    old=b.resolved('newlife31_add_rounded_option');s=old['source'];marker='mov x8,x22\n';assert marker in s
    glyphs=['brain','blood','eyes','tongue','brain','bone','man-haircut','blood','eye','face-sleeping']
    labels=[('Birth traits','brain'),('Random at birth','brain'),('More birth traits','books'),('Previous birth traits','books')]+[(name,glyphs[i])for i,(name,info)in enumerate(TRAITS)]
    code=''
    for i,(label,glyph)in enumerate(labels):
        code+=h.compare_key(label,'birth_icon1105_'+str(i),'birth_icon1105_next_'+str(i))+f'\nbirth_icon1105_{i}:\n'+b.string(glyph)+f'mov x20,x0\nb rework_icon_done\nbirth_icon1105_next_{i}:\n'
    b.redirect(old['name'],s.replace(marker,marker+code,1))
