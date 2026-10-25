"""Portrait texture lifetime and custom menu age gates, using verified sites."""
from native_hooks import h


def hooks(b):
    # CopyTexture's Texture2D(width,height) creates a mip chain. The previous
    # CPU path uploaded only mip zero, leaving smaller levels uninitialized.
    record = next(r for r in b.hooks if r['name'] == 'v55_resize_readable_portrait_on_cpu')
    old = 'mov w1,#0\nmov w2,#0\nmov x3,xzr\nbl 0x555a4a8'
    new = 'mov w1,#1\nmov w2,#0\nmov x3,xzr\nbl 0x555a4a8'
    assert record['source'].count(old) == 1
    before = h.asm(record['source'], record['stub'])
    record['source'] = record['source'].replace(old, new)
    after = h.asm(record['source'], record['stub'])
    assert len(after) == len(before) == record['length']
    offset = b.off(record['stub'])
    assert bytes(b.blob[offset:offset + len(before)]) == before
    b.blob[offset:offset + len(after)] = after
    b.changed.append([record['stub'], len(after), 'CPU portrait copies regenerate mipmaps'])

    # The independent centered-header path previously discarded CPU pixels.
    # Keep these readable for the next cache/copy/age transition as well.
    site = 0x2f4cc68
    assert bytes(b.blob[b.off(site):b.off(site) + 4]) == h.asm('mov w2,#1', site)
    b.write(site, 'mov w2,wzr', 'centered portraits retain CPU pixel storage')
    age_cache(b)

    # Reuse the game's established native ListItem disabled byte and existing
    # eligibility routine; preserve all original crime choices and age rules.
    code = 'cbz x19,finish\ncbz x21,finish\nldr x8,[x19,#0x10]\ncbz x8,finish\n'
    for n, owner in enumerate(['crime_entry54_61', 'crime_entry54_62',
                               'crime_entry54_63', 'crime_entry54_64', 'roblox_social']):
        target = 'refresh_social' if owner == 'roblox_social' else 'refresh_adult'
        code += h.compare_key(owner, target, 'refresh_next_' + str(n))
        code += '\nrefresh_next_' + str(n) + ':\n'
    eligibility = b.old['current_eligibility19']['stub']
    code += ('b finish\nrefresh_adult:\nmov w0,#11\nb refresh_check\n'
             'refresh_social:\nmov w0,#12\nrefresh_check:\n'
             f'bl {eligibility:#x}\ncbnz w0,finish\nmov w9,#1\nstrb w9,[x21,#0xd0]\nb finish')
    b.chain('refresh_custom_menu_age_requirements', 'v19_grey_entry_requirements', code)
    calendar(b)
    images(b)
    story_journal(b)


def age_cache(b):
    """Evict the current hero's stale portrait once when its age changes."""
    code = 'cbz x19,finish\n' + h.load_game()
    code += ('\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr x8,[x8,#0x80]\n'
             'cmp x8,x19\nb.ne finish\nldr x27,[x19,#0x30]\ncbz x27,finish\n'
             'ldr x26,[x27,#0x10]\ncbz x26,finish\n')
    code += b.ctx('life_v18') + b.get('PortraitCacheAge', default=-1)
    code += 'cmp w24,w23\nb.eq finish\nmov x0,xzr\nbl 0x2f34138\ncbz x0,finish\nmov x25,x0\n'
    code += b.put('PortraitCacheAge', 'w23')
    code += 'mov x0,x25\nmov x1,x26\nmov x2,xzr\nbl 0x2f4d2d8\nb finish'
    routine = b.routine('refresh_current_hero_portrait_age', code)
    b.chain('refresh_age_before_cached_hero_portrait', 'v43_appearance_before_cached_emoji',
            f'bl {routine:#x}\nb finish')


def calendar(b):
    """Accrue membership allowance from actual elapsed character years only."""
    code = 'str xzr,[sp]\n' + b.ctx('roblox_social')
    code += b.get('SchemaVersion') + 'cmp w24,#2\nb.eq refresh_calendar_ready\n'
    code += b.set('SchemaVersion', 2) + b.put('CalendarAge', 'w23')
    code += b.set('PlaceLimit', 1) + b.set('GroupLimit', 0)
    code += b.get('Games') + b.put('ActivePlaces')
    code += b.get('Club', 'w25') + b.get('ClubAge')
    code += 'cmp w24,w23\nb.ne refresh_calendar_ready\ncbz w25,refresh_calendar_ready\n'
    code += b.set('DaysRemaining', 365) + b.set('SigningBonusGranted', 1)
    for tier, daily, places, groups in [(1, 15, 10, 10), (2, 35, 25, 20), (3, 60, 100, 100)]:
        code += f'cmp w25,#{tier}\nb.ne refresh_migrate_next_{tier}\n'
        code += b.set('DailyRobux', daily) + b.set('PlaceLimit', places) + b.set('GroupLimit', groups)
        code += b.set('Hat' + str(tier), 1) + f'refresh_migrate_next_{tier}:\n'
    code += 'refresh_calendar_ready:\n' + b.get('CalendarAge', 'w25')
    code += 'cmp w23,w25\nb.le finish\nsub w25,w23,w25\nmov w9,#365\nmul w25,w25,w9\n'
    code += b.get('Lifetime', 'w26') + b.get('DaysRemaining', 'w27')
    code += 'cbnz w26,refresh_credit_days\ncmp w25,w27\ncsel w25,w25,w27,le\n'
    code += 'refresh_credit_days:\n' + b.get('DailyRobux', 'w28')
    code += 'mul w28,w28,w25\n' + b.put('CalendarAge', 'w23')
    code += b.put('LastAllowance', 'w28') + b.put('LastAllowanceDays', 'w25')
    code += 'cbz w28,refresh_expire_check\n' + b.get('Robux') + 'add w24,w24,w28\n' + b.put('Robux')
    code += 'sub sp,sp,#192\nmov x0,sp\nmov w1,#192\n'
    code += f'adr x2,{b.literal("I received %d Roblox membership Robux for %d elapsed simulated days."):#x}\n'
    code += 'mov w3,w28\nmov w4,w25\n' + f'bl {b.snprintf:#x}\nmov x0,sp\nbl {h.NEW_STRING:#x}\nadd sp,sp,#192\n'
    code += f'bl {b.journal55:#x}\nrefresh_expire_check:\ncbnz w26,finish\nsub w27,w27,w25\n'
    code += b.put('DaysRemaining', 'w27') + 'cbnz w27,finish\n'
    code += b.set('Club', 0) + b.text('ClubName', 'Free account') + b.set('DailyRobux', 0)
    code += b.set('PlaceLimit', 1) + b.set('GroupLimit', 0) + 'b finish'
    routine = b.routine('refresh_roblox_calendar', code)
    callback = ('tbz w0,#0,finish\ncbz x19,finish\ncbz x21,finish\n'
                'ldr x8,[x19,#0x18]\ncbz x8,finish\n')
    callback += h.compare_key('SyncCalendar', 'refresh_sync_key', 'finish')
    callback += '\nrefresh_sync_key:\nldr x8,[x21,#0x10]\ncbz x8,finish\n'
    callback += h.compare_key('roblox_social', 'refresh_sync_owner', 'finish')
    callback += f'\nrefresh_sync_owner:\nbl {routine:#x}\nb finish'
    b.chain('refresh_calendar_after_explicit_sync', 'v18_saved_state', callback)
    # Entering the ordinary Social list settles the account without a separate
    # dashboard click; repeated list openings cannot repeat an allowance.
    code = 'cbz x0,finish\nmov x8,x0\n'
    code += h.compare_key('genesis_v18_roblox_social', 'refresh_sync_open', 'finish')
    code += f'\nrefresh_sync_open:\nbl {routine:#x}\nb finish'
    b.chain('refresh_calendar_before_roblox_list', 'v47_project_before_show', code)


def images(b):
    """Load art as Sprite; panel resolution returns that sprite's Texture2D."""
    # These two hooks were emitted earlier in this same build, after b.old's
    # frozen v54 manifest was loaded. Expose their actual entries to chain().
    for name in ['v55_full_owned_image_paths', 'v55_supplied_church_story_images']:
        b.old[name] = next(record for record in b.hooks if record['name'] == name)
    def code(sprite):
        text = 'cbz x0,finish\nmov x8,x0\n'
        text += h.compare_key('<GFC.roblox_social.AvatarImage>', 'refresh_avatar', 'refresh_image_paths')
        text += '\nrefresh_avatar:\n' + b.ctx('roblox_social') + b.string('AvatarImage')
        text += ('mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\n'
                 'cbz x0,refresh_image_empty\nldr w9,[x0,#16]\ncbz w9,refresh_image_empty\n'
                 'mov x8,x0\nb refresh_image_paths\nrefresh_image_empty:\nstr xzr,[sp]\nb return_custom\nrefresh_image_paths:\n')
        from native_v42.patch_native42 import ref, ref_init
        for i, asset_id in enumerate([1080951, 11844853, 17408283]):
            path = 'mayomods_refresh/roblox/' + str(asset_id)
            text += h.compare_key(path, 'refresh_image_' + str(i), 'refresh_image_next_' + str(i))
            text += '\nrefresh_image_' + str(i) + ':\n' + ref_init(0x5c56ad8) + b.string(path)
            text += ref(0x5c56ad8, 'x1') + 'bl 0x3ed1638\ncbz x0,finish\n'
            if sprite:
                text += 'mov x1,xzr\nbl 0x553b564\n'
            text += 'str x0,[sp]\nb return_custom\nrefresh_image_next_' + str(i) + ':\n'
        return text + 'b finish'
    b.chain('refresh_classic_club_icon_images', 'v55_full_owned_image_paths', code(False), ret=True)
    b.chain('refresh_classic_club_panel_images', 'v55_supplied_church_story_images', code(True), ret=True)


def story_journal(b):
    initialize = b.routine('refresh_initialize_parish_story', b.ctx('gameplay52') +
                          b.get('CaseNumber') + 'cbnz w24,finish\n' +
                          b.set('CaseNumber', 1) + b.set('CaseAge', -1) + 'b finish')
    entry = 'cbz x0,finish\nmov x8,x0\n' + h.compare_key('genesis_v18_church52', 'refresh_story_initialize', 'finish')
    entry += f'\nrefresh_story_initialize:\nbl {initialize:#x}\nb finish'
    b.chain('refresh_initialize_opened_parish', 'v47_project_before_show', entry)
    code = 'tbz w0,#0,finish\ncbz x19,finish\ncbz x21,finish\nldr x8,[x19,#0x18]\ncbz x8,finish\n'
    code += h.compare_key('StoryJournalSequence', 'refresh_story_key', 'finish')
    code += '\nrefresh_story_key:\nldr x8,[x21,#0x10]\ncbz x8,finish\n'
    code += h.compare_key('gameplay52', 'refresh_story_owner', 'finish')
    code += '\nrefresh_story_owner:\n' + b.ctx('gameplay52')
    code += b.get('StoryJournalSequence', 'w26') + b.get('StoryJournalLogged')
    code += 'cmp w26,w24\nb.le finish\n' + b.string('StoryJournalMessage')
    code += 'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\ncbz x0,finish\nmov x27,x0\n'
    code += b.put('StoryJournalLogged', 'w26') + f'mov x0,x27\nbl {b.journal55:#x}\nb finish'
    routine = b.routine('refresh_log_parish_story', code)
    b.chain('refresh_parish_story_after_commit', 'v18_saved_state', f'bl {routine:#x}\nb finish')
