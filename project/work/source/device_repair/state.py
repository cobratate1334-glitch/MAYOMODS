"""Use current native membership, selected people and actual choice contracts."""
from native_hooks import h
from playable_repair.visuals import prefix


def hooks(b):
    # A joined middle-school team is SCHOOL_TYPE.MIDDLE=101. The old generic
    # team guard incorrectly accepted only high school and college.
    row=b.resolved('current_eligibility19');s=row['source']
    old='cmp w9,#2\nb.eq team19\nb college19\nhighschool19:'
    new='cmp w9,#1\nb.eq team19\ncmp w9,#101\nb.eq team19\ncmp w9,#2\nb.eq team19\nb college19\nhighschool19:'
    assert s.count(old)==1;s=s.replace(old,new)
    old='highschool19:\ncmp w9,#2\nb.ne finish'
    assert s.count(old)==1;s=s.replace(old,'highschool19:\ncmp w9,#1\nb.eq team19\ncmp w9,#101\nb.eq team19\ncmp w9,#2\nb.ne finish')
    b.redirect(row['name'],s)

    # Legacy menus used cached prison/sport flags. Refresh snapshots at the
    # actual owned-menu and CSV-choice boundaries, never in the HUD loop.
    refresh=b.old['life_rework_refresh_context']['stub']
    s='cbz x0,finish\nmov x8,x0\n'+prefix('genesis_','owned_context','finish')+f'owned_context:\nbl {refresh:#x}\nb finish'
    b.chain('device_current_context_before_owned_menu','v47_project_before_show',s)
    s=f'cbz x0,finish\nldr x8,[x0,#0x190]\ncbz x8,finish\nbl {refresh:#x}\nb finish'
    for n in [0,1]:b.chain('device_current_context_before_choice_'+str(n),'v54_record_scenario_choice_'+str(n),s)

    # Original AcceptChoice ignores ChoiceSelectedAtIndex's x0 return. It reads
    # currentScenario.NextScenario during RemoveAlert. Queue the result there.
    row=b.resolved('connected_return_inmate_support_scenario');s=row['source']
    old='bl 0x3084c00\nstr x0,[sp]\nb return_custom'
    new='bl 0x3084c00\ncbz x0,finish\nmov x1,x0\nmov x0,x22\nmov x2,xzr\nbl 0x2a21414\nb return_custom'
    assert s.count(old)==1;b.redirect(row['name'],s.replace(old,new))

    # Native relationship tables do not recursively expand saved GFC strings.
    # Store a concrete story after the actual person has been finalized.
    row=b.resolved('selected_relationship_details21');s=row['source']
    marker='\nb finish\nfinish:';assert s.count(marker)==1
    concrete=b.ctx('relationship21')+b.string('Story')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\ncbz x0,finish\nbl 0x308ddb0\nbl 0x308ddb0\nmov x22,x0\n'+b.textptr('Story')
    b.redirect(row['name'],s.replace(marker,'\n'+concrete+marker))

    # Grey the real native ListItem outside the two campaigns. Do not hide the
    # stock Military menu, or allow an empty modern-year command hub to open.
    s='cbz x19,finish\ncbz x21,finish\nldr x8,[x19,#0x10]\ncbz x8,finish\n'+h.compare_key('recruit1110','war_dates','finish')+'\nwar_dates:\n'+f'bl {b.old["v45_current_year"]["stub"]:#x}\ncmp w0,#1914\nb.lt war_closed\ncmp w0,#1918\nb.le finish\ncmp w0,#1939\nb.lt war_closed\ncmp w0,#1945\nb.le finish\nwar_closed:\nmov w9,#1\nstrb w9,[x21,#0xd0]\nb finish'
    b.chain('device_grey_world_war_entry_outside_dates','v19_grey_entry_requirements',s)
