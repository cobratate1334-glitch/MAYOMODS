"""Repairs at original native boundaries; retain the confirmed menu transitions."""
from native_hooks import h


def hooks(b):
    # The shipped Unity module's 3-argument LoadImage takes ReadOnlySpan<byte>.
    # Its 2-argument overload accepts byte[] and constructs the span itself.
    # Passing a byte[] object as a boxed span gives the decoder invalid data.
    row=b.resolved('immersion1109_upload_owned_image');s=row['source']
    marker='mov w2,#3\nbl 0x223dff0';assert s.count(marker)==1
    s=s.replace(marker,'mov w2,#2\nbl 0x223dff0',1)
    marker='cbnz x9,finish\nstr wzr,[x28,#164]\nb finish';assert s.count(marker)==1
    s=s.replace(marker,'cbnz x9,image_decode_failed1116\ncbz x0,image_decode_failed1116\nldrb w9,[x0,#16]\ncbz w9,image_decode_failed1116\nstr wzr,[x28,#164]\nb finish\nimage_decode_failed1116:\nstr wzr,[x28,#164]\n'+b.ctx('life_rework')+b.text('MImage1109','')+'b finish',1)
    b.redirect(row['name'],s)

    # An unemployed Life can legitimately have a NULL occupation. The old
    # generic loader treated that as failure and never reached StartMilitary.
    row=b.resolved('military1108_construct_native_service_once');s=row['source']
    marker='ldr x8, [x8, #0x138]\n cbz x8, finish\n'
    assert s.count(marker)==1
    s=s.replace(marker,'ldr x8, [x8, #0x138]\n cbz x8, induct_unemployed1116\n',1)
    marker='mov w28,#1\nrework_find_army:';assert s.count(marker)==1
    s=s.replace(marker,'induct_unemployed1116:\n'+marker,1)
    b.redirect(row['name'],s)

    # Exit a committed era picker transaction explicitly. The stock manager
    # may reuse its root page; selection must not depend on a later rebuild.
    names=[r['name']for r in b.base['routines']if r['name'].startswith(('v44_year_choice_','connected_year_choice_'))]
    names+=['v52_apply_custom_year']
    done=set()
    for name in names:
        row=b.resolved(name)
        if row['stub']in done:continue
        done.add(row['stub']);s=row['source']
        mark='mov x0,x27\nmov w1,#5\n'
        if mark not in s:continue
        assert s.count(mark)==1
        s=s.replace(mark,f'adr x8,{b.newlife31:#x}\nstr wzr,[x8,#64]\n'+mark,1)
        b.redirect(name,s)

    # New Life's extra root buttons must forward gestures to the SAME real
    # ScrollRect as the stock country button. Without this, OnBeginDrag does
    # not call InputManager.UnClick and taps/drags interfere across the form.
    row=b.resolved('activate_and_register_newlife_button26');s=row['source']
    marker='mov x25,x1\nldr x24,[x25,#0x28]';assert s.count(marker)==1
    copy=(f'mov x25,x1\nadr x8,{b.newlife24:#x}\nldr x0,[x8,#32]\ncbz x0,root_scroll_ready1116\nbl 0x223e73c\ncbz x0,root_scroll_ready1116\nldr x8,[x0,#0xd0]\ncbz x8,root_scroll_ready1116\nldr x9,[x8,#0x90]\ncbz x9,root_scroll_ready1116\nstr x9,[x25,#0x90]\nroot_scroll_ready1116:\nldr x24,[x25,#0x28]')
    b.redirect(row['name'],s.replace(marker,copy,1))

    # Respect the game's audited THEME_NAME.DARK (1). Ordinary native dark
    # colours remain authoritative. War phases and their artwork still update.
    row=b.resolved('v46_native_era_theme_colors');s=row['source'];head=h.save()+'\n';assert s.startswith(head)
    pref='str xzr,[sp]\n'+h.load_game(end='finish')+'\nldr x8,[x8,#0x48]\ncbz x8,finish\nldr w9,[x8,#0x68]\ncmp w9,#1\ncset w9,eq\nstr x9,[sp]\nb finish'
    dark=b.routine('v2_selected_dark_theme',pref)
    b.redirect(row['name'],head+f'bl {dark:#x}\ncbnz w0,finish\nldr x0,[sp]\n'+s[len(head):])
