"""Repairs tied to the two supplied 1105 crash bundles."""
from native_hooks import h
from native_v24.native_ui21 import table_value


def hooks(b):
    # The weighted ArrayList can be empty after an era/category intersection.
    # Pick an actual loaded period record before the original random indexing;
    # keep the original frame epilogue and every non-empty path unchanged.
    year=b.old['v45_current_year']['stub']
    s='cbnz w0,finish\n'+f'bl {year:#x}\nmov w25,w0\n'
    from native_v45.catalog45 import CARS
    road=sorted([r for r in CARS if not r['race_only']and not r['luxury']],key=lambda r:r['start'],reverse=True)
    for r in road:
        s+=f'cmp w25,#{r["start"]}\nb.lt empty_car_next_{r["id"]}\n'+b.string(r['model'])+f'b empty_car_lookup\nempty_car_next_{r["id"]}:\n'
    s+=b.string('1880 Road carriage')+'empty_car_lookup:\nmov x26,x0\n'+b.string('Mayo')+'mov x1,x26\nmov x2,xzr\nbl 0x2800d7c\nstr x0,[sp]\nb return_custom'
    b.install('repair_empty_period_car_pool',0x27ffadc,s,custom_resume=0x27ffb48)

    # FightClubGymListItems returns List<FightClubGymListItem>. The injector
    # expects its original ArrayList menu representation. Never pass the typed
    # fighting-game list through that injector. Keep its exact original epilogue.
    old=b.old['life_rework_inside_original_fight_gym']
    b.write(old['site'],old['original'],'remove incompatible Genesis injection from typed fight gym list')

    # Refresh using the selected object, and preserve the original friend bit
    # across property reads. UI previews are allowed to rebuild other people.
    old=b.resolved('selected_relationship_details21');s=old['source']
    # The original code reuses w28 while generating personality variants; it
    # must not be reused as the selected relationship kind by later consumers.
    # Live age/name are finalized at the end, after derived profiles are built.
    marker='\nb finish\nfinish:';assert marker in s
    repair='ldr x26,[sp]\n'+b.ctx('relationship21')+'ldr w24,[x26,#0x20]\n'+b.put('Age')+b.put('SelectedAge1106')+'mov x0,x26\nmov x1,xzr\nbl 0x2c44914\nmov x22,x0\n'+b.textptr('Name')+b.textptr('SelectedName1106')
    repair+=f'mov x0,x26\nbl {b.old["v52_person_birth_country_name"]["stub"]:#x}\nmov x22,x0\n'+b.textptr('BirthCountry1106')+b.text('Story','<GFC.relationship21.SelectedName1106> is <GFC.relationship21.SelectedAge1106>. Birth country: <GFC.relationship21.BirthCountry1106>. Your current connection is <GFC.relationship21.Connection>/100.')
    # The retained child-only preference adjustment exits early for adults.
    # Both the adult and child success paths must finalize the selected person.
    assert s.count('cmp w24,#18\nb.ge finish')==1
    s=s.replace('cmp w24,#18\nb.ge finish','cmp w24,#18\nb.ge selected_finalize1106')
    b.redirect(old['name'],s.replace(marker,'\nselected_finalize1106:\n'+repair+marker,1))

    # Native ResolveAllTags performs GFC expansion once. A GFC string can
    # itself contain another GFC value. Re-expand only that pure tag stage,
    # twice, without creating a parser, changing focus or rerunning RNG.
    b.install('repair_nested_saved_text_before_display',0x308c458,
              'cbz x0,finish\nbl 0x308ddb0\nbl 0x308ddb0\nstr x0,[sp]\nb finish')

    # Replace only mod additions at the final native profile boundary. Stock
    # gender/age/occupation/illness/location rows were already built by the game.
    # Do not add build IDs, duplicated adult height or seven empty trait rows.
    s='mov x19,x28\ncbz x19,finish\n'+f'bl {b.old["followup_initialize_actual_profile_height"]["stub"]:#x}\nbl {b.old["measurements_at_current_age21"]["stub"]:#x}\n'+b.ctx('life_v18')
    from native_v24.native_ui21 import number
    for key,title,unit in [('Height','Height:',' cm'),('Wingspan','Wingspan:',' cm'),('Weight','Weight:',' kg')]:
        s+=b.get(key)+number(b,unit=unit)+table_value(b,'x19',title)
    s+='cmp w23,#18\nb.ge profile1106_growth_done\n'+b.get('AdultHeight')+number(b,unit=' cm')+table_value(b,'x19','Adult height estimate:')+'profile1106_growth_done:\n'
    # Preserve the original living-journal option and its existing callback.
    journal=b.old['v42_living_journal_profile_button']['source']
    a=journal.index('mov x26,x28');z=journal.index('\nfinish:')
    body=journal[a:z];assert 'journal_choices_ready'in body
    s+=body+'\nb finish'
    b.write(0x37c100c,'ldp x20,x19,[sp,#0xa0]','replace old mod-only profile additions')
    b.install('repair_compact_native_profile',0x37c100c,s)
