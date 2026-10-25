"""Repair actual profile and age-up boundaries without replacing stock simulation."""
from native_hooks import h
from native_v42.patch_native42 import body


def hooks(b):
    # 1104 called LoadAndShowScenario with a RESOURCE NAME. That method parses
    # its first argument as CSV, creates/replaces the live ScenarioController,
    # and can strand the age-up spinner. AgeUpActionList is the engine's queue.
    old=b.old['life_rework_annual_context_events']
    s=old['source'];a=s.index('bl ');z=s.index('\nfinish:')
    refresh=b.old['life_rework_refresh_context']['stub']
    b.redirect(old['name'],s[:a]+f'bl {refresh:#x}\nb finish'+s[z:])

    # Ensure the registered container is active BEFORE native annual processing
    # enumerates active IDs. No UI creation, no replacement of a queue/controller.
    b.install('followup_activate_before_native_annual_queue',0x305e134,
              b.ctx('life_rework')+f'bl {refresh:#x}\nb finish')

    # A default 178 that an old draft mislabeled as explicit is not an actual
    # adult prediction. Preserve other old manual targets and new explicit 178.
    family=b.old['v51_ensure_family_projection']['stub']
    s=b.ctx('life_v18')+b.get('HeightRevision1105')+'cmp w24,#1105\nb.eq finish\n'
    s+=b.get('HeightManual1105')+'cbnz w24,followup_height_manual\n'
    s+=b.get('HeightSource51')+'cmp w24,#2\nb.ne followup_height_auto\n'
    s+=b.get('AdultHeight')+'cmp w24,#178\nb.ne followup_height_manual\n'
    s+='followup_height_auto:\n'+b.set('HeightModel52',0)+b.set('HeightSource51',1)
    s+=f'bl {family:#x}\n'+b.ctx('life_v18')+b.text('HeightSourceName51','Country, birth sex and parents')
    s+='followup_height_manual:\n'+b.set('HeightRevision1105',1105)+'b finish'
    fix=b.routine('followup_initialize_actual_profile_height',s)
    # All growth/profile consumers now pass this gate, including a newly born
    # hero whose header hasn't run. Do not recurse through measurements here.
    b.chain('followup_height_before_every_measurement','measurements_at_current_age21',f'bl {fix:#x}\nb finish')
    b.chain('followup_height_at_native_profile','v21_native_hero_profile_measurements',f'bl {fix:#x}\nb finish')
    b.chain('followup_height_at_live_header','life_rework_finalize_live_family_height',f'bl {fix:#x}\nb finish')
    # Copy the existing draft's explicit-choice bit only at actual birth.
    # Writing a live GFC from the picker would change the previous character.
    s=b.ctx('life_v18')+f'adr x8,{b.newlife24:#x}\nldr w24,[x8,#28]\n'
    s+='cmp w24,#1\ncset w24,eq\n'+b.put('HeightManual1105')+b.set('HeightRevision1105',0)+'b finish'
    b.chain('followup_capture_birth_height_provenance','v42_birth_genetics_and_portrait',s)
    # All NPC/profile/inheritance consumers share the same actual target for
    # a previously played parent. No guessed field is written into SimPerson.
    s='cbz x0,finish\nmov x19,x0\n'+h.load_game()+'\nldr x25,[x8,#0x20]\ncbz x25,finish\nldr x9,[x8,#0x28]\ncmp x19,x9\nb.eq height1105_current_hero\nldr x9,[x25,#0xa8]\ncmp x19,x9\nb.eq height1105_current_father\nldr x9,[x25,#0xb8]\ncmp x19,x9\nb.ne finish\nmov w20,#2\nb height1105_actual_target\nheight1105_current_father:\nmov w20,#1\nb height1105_actual_target\nheight1105_current_hero:\nmov w20,#0\nheight1105_actual_target:\n'+b.ctx('life_v18')
    s+='cmp w20,#1\nb.eq height1105_read_father\ncmp w20,#2\nb.eq height1105_read_mother\n'+b.get('AdultHeight')+'b height1105_target_ready\nheight1105_read_father:\n'+b.get('PlayedFatherHeight1105')+'b height1105_target_ready\nheight1105_read_mother:\n'+b.get('PlayedMotherHeight1105')+'height1105_target_ready:\ncmp w24,#120\nb.lt finish\nstr x24,[sp]\nb return_custom'
    b.chain('followup_shared_actual_played_parent_heights','v52_person_adult_height',s,ret=True)

    # Restore church's original native list. Roblox still opens its website.
    old=b.resolved('web_open_social_and_parish');s=old['source']
    start=s.index('mov w20,#2') if 'mov w20,#2' in s else s.index('mov w20, #2')
    end=s.index('\n',start)
    # Only the church match's dispatch is bypassed. Its existing native
    # initialization/callback/icon hooks remain reachable after this chain.
    s=s[:start]+'b finish'+s[end:];b.redirect(old['name'],s)

    # AssetShoppingArray must only build the list. Refreshing both complete
    # markets from its prologue introduces re-entrancy/side effects on a read.
    # Keep the country/year catalog gates at the actual dealer generation APIs.
    old=b.old['v45_refresh_shopping_market']
    b.write(old['site'],old['original'],'restore pure native shopping list construction')

    # Expose the actual projection source in the original profile table.
    from native_v24.native_ui21 import table_value
    s='mov x19,x28\ncbz x19,finish\n'+b.ctx('life_v18')
    s+=b.string('HeightSourceName51')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\nmov x22,x0\n'
    s+=table_value(b,'x19','Height estimate:')+b.string('1105')+'mov x22,x0\n'+table_value(b,'x19','MayoMods build:')+'b finish'
    b.chain('followup_profile_source_and_build','v21_native_hero_profile_measurements',s)

    # Give Unity frames to finish the age transition. Two consecutive retries
    # can both run before the replacement portrait is ready. Keep the owned
    # last-good texture; attempt at most eight recoveries, 16 frames apart.
    old_state=b.states['life_rework']['va'];new_state=b.state
    old=b.resolved('life_rework_retry_header_on_unity_thread');s=old['source']
    assert 'cmp w9,#2' in s;s=s.replace('cmp w9,#2','cmp w9,#8',1)
    marker=h.save()+'\n';assert s.startswith(marker)
    prefix=f'adr x8,{old_state:#x}\nldr w9,[x8,#40]\nadr x28,{new_state:#x}\ncbnz w9,portrait1105_frame_pending\nstr wzr,[x28,#80]\nb finish\nportrait1105_frame_pending:\nldr w9,[x28,#80]\nadd w9,w9,#1\nstr w9,[x28,#80]\nand w9,w9,#15\ncbnz w9,finish\n'
    b.redirect(old['name'],marker+prefix+s[len(marker):])
    old=b.resolved('life_rework_validated_header_texture');s=old['source'];assert s.startswith(marker)
    prefix=h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr w9,[x8,#0x20]\n'+f'adr x28,{new_state:#x}\nldr w10,[x28,#84]\ncmp w9,w10\nb.eq portrait1105_age_ready\nstr w9,[x28,#84]\nstr wzr,[x28,#80]\nadr x8,{old_state:#x}\nstr wzr,[x8,#44]\nportrait1105_age_ready:\n'
    b.redirect(old['name'],marker+prefix+s[len(marker):])
