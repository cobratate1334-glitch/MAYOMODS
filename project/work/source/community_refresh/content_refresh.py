"""Illustrated classic memberships and parish stories built on saved native state."""
import csv
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'social_roblox'))
import roblox_content as r

TIERS = [
    (1, 'Builders Club', 15, 10, 10, '1080951', [595, 2995, 5795, 19995]),
    (2, 'Turbo Builders Club', 35, 25, 20, '11844853', [1195, 4495, 8595, 29995]),
    (3, 'Outrageous Builders Club', 60, 100, 100, '17408283', [1995, 6995, 12995, 34995]),
]
TERMS = [('Monthly', 30, 0), ('6 months', 180, 0), ('12 months', 365, 0), ('Lifetime', 0, 1)]
IMAGE_PREFIX = 'mayomods_refresh/roblox/'


def expand(base, overlay):
    assets = {**base, **overlay}
    result = dict(overlay)
    rows = list(csv.DictReader(io.StringIO(result[r.SCENES])))
    header = list(rows[0])
    existing = {x['ScenarioID']: x for x in rows}
    defaults = list(csv.DictReader(io.StringIO(result[r.DEFAULTS])))

    def field(key, value=0, maximum=100000000, minimum=0):
        if any(x['key'] == key for x in defaults):
            return
        defaults.append(dict(key=key, type='string' if isinstance(value, str) else 'int',
                             value=value, reset_on_ageup='',
                             minimum='' if isinstance(value, str) else minimum,
                             maximum='' if isinstance(value, str) else maximum))

    for key, val, hi in [('SchemaVersion', 0, 2), ('SyncCalendar', 0, 1),
                         ('CalendarAge', -1, 999), ('DaysRemaining', 0, 365),
                         ('Lifetime', 0, 1), ('DailyRobux', 0, 60), ('ActivePlaces', 0, 100),
                         ('PlaceLimit', 1, 100), ('GroupLimit', 0, 100),
                         ('SigningBonusGranted', 0, 1), ('LastAllowance', 0, 100000000),
                         ('LastAllowanceDays', 0, 365000), ('Hat1', 0, 1), ('Hat2', 0, 1),
                         ('Hat3', 0, 1), ('WornHat', 0, 3), ('Designs', 0, 1000),
                         ('CatalogSales', 0, 1000000), ('Groups', 0, 100), ('Feedback', 0, 10),
                         ('CatalogAge', -1, 999), ('GroupAge', -1, 999), ('MailRead', 0, 1)]:
        field(key, val, hi, -1 if val == -1 else 0)
    field('AvatarImage', '')
    field('DesignName', 'No clothing design')
    field('GroupName', 'No group')
    field('PlaceArchive', 'Your published experience history begins here.')
    p, f, seq = r.p, r.f, r.seq
    s = lambda key: r.scene('refresh_' + key)
    back = ('Back to Roblox', 'BP_SHOW_LIST=' + r.HUB)

    def logic(cases, target):
        return {'cases': [{'if': expr if isinstance(expr, dict) else {'expression': expr},
                           'then': {'route_options': [{'route_to': route}]}}
                          for expr, route in cases],
                'else_when_no_matches': {'route_options': [{'route_to': target}]}}

    def gate(target, cases=(), action=False):
        guards = [('(<hero:age> < 13)', r.scene('young')),
                  ('(' + p('Joined') + ' == 0)', r.scene('account_required')),
                  ('(' + p('CalendarAge') + ' < <hero:age>)', s('account'))]
        guards += list(cases)
        if action:
            guards.append(('(' + p('ActionAge') + ' >= <hero:age>) && (' + p('Actions') + ' >= 8)', r.scene('quota')))
        return logic(guards, target)

    def page(key, title, body, choices, stats=(), image=None):
        record = dict.fromkeys(header, '')
        record.update(ScenarioID=s(key), Style='normal', ExteriorTitle='ROBLOX',
                      Title=title, Body=body.replace('\n', '<br>'), EmojiString='iphone', HasDismissButton='true')
        if image:
            record['BigImageString'] = image
        if stats:
            record['TableRows'] = json.dumps([dict(row=i, key=k + ':', value=v)
                                            for i, (k, v) in enumerate(stats, 1)])
        for i, (label, route) in enumerate(choices, 1):
            assert i <= 4
            record[f'Choice{i}_Text'] = label
            record[f'Choice{i}_ButtonStyle'] = 'normal'
            record[f'Choice{i}_AdvancedLogic' if isinstance(route, dict) else f'Choice{i}_RouteTo'] = json.dumps(route) if isinstance(route, dict) else route
        assert record['ScenarioID'] not in existing
        rows.append(record)
        existing[record['ScenarioID']] = record

    def receipt(message):
        return [r.text('Result', message), r.text('JournalMessage', 'I ' + message[0].lower() + message[1:]), r.inc('JournalSequence')]

    def action(key, title, body, changes, cases=(), work=False, image=None):
        work_cost = []
        if work:
            work_cost = [r.set_('Actions', f('add', f('mul', p('Actions'),
                         f('clamp', f('sub', 1, f('max', f('sub', '<hero:age>', p('ActionAge')), 0)), 0, 1)), 1)),
                         r.set_('ActionAge', f('max', p('ActionAge'), '<hero:age>'))]
        target = seq(*work_cost, *changes, *receipt(body), s('result'))
        page(key, title, body, [('Confirm', gate(target, cases, work)), back], image=image)

    page('result', 'Your Roblox story', p('Result'), [back], stats=[('Robux', p('Robux')), ('Fans', p('Fans'))])
    page('bank_funds', 'Not enough money in your game bank', 'This membership uses the price shown from your character’s BitLife bank balance. No game money, Robux, term or activity was changed.', [back])
    page('account', 'My ROBLOX', 'Your account, creations and membership travel with this life. Open the dashboard to collect any daily allowance earned since your last visit.', [
        ('Open my dashboard', gate(seq(r.set_('SyncCalendar', 1), s('dashboard')))),
        ('Create free account', r.scene('account')), ('Builders Club', s('clubs')), back], image='<GFC.roblox_social.AvatarImage>')
    # This entry deliberately permits stale CalendarAge: its only operation is
    # the native settlement, which is idempotent and never charges money.
    existing[s('account')]['Choice1_AdvancedLogic'] = json.dumps(logic([
        ('(<hero:age> < 13)', r.scene('young')),
        ('(' + p('Joined') + ' == 0)', r.scene('account_required'))],
        seq(r.set_('SyncCalendar', 1), s('dashboard'))))
    page('dashboard', 'My ROBLOX', 'Build places, design clothing, manage a group and read your inbox. Daily allowance is calculated only from simulated time that actually elapsed.', [
        ('My places', r.scene('studio')), ('Catalog & trading', s('catalog')),
        ('Groups & inbox', s('social')), ('Builders Club', s('clubs'))],
        stats=[('Robux', p('Robux')), ('Membership', p('ClubName')), ('Active places', p('ActivePlaces')),
               ('Place allowance', p('PlaceLimit')), ('Last allowance', p('LastAllowance')),
               ('Allowance days', p('LastAllowanceDays'))], image='<GFC.roblox_social.AvatarImage>')
    page('clubs', 'Get More with Builders Club', 'Choose the classic membership you want to play. Prices are paid from your character’s game bank, never a real payment. A monthly pass lasts 30 simulated days; 6 months lasts 180; 12 months lasts 365. Classic terms are optional nostalgic game content.', [
        ('Builders Club', s('tier1')), ('Turbo Builders Club', s('tier2')),
        ('Outrageous Builders Club', s('tier3')), ('Membership record', s('membership'))],
        stats=[('Free account places', '1'), ('Free daily Robux', 'None'), ('First membership bonus', '100 R$ once')], image=IMAGE_PREFIX + '1080951')
    for tier, name, daily, places, groups, image_id, prices in TIERS:
        page('tier' + str(tier), name, 'Choose a term. Membership includes catalog selling, group creation, an ad-free Roblox account page and its classic hard hat. This purchase does not remove ads elsewhere in BitLife. You keep your hat and saved places after expiry; new creation uses the free account limit.', [
            (term + ' — $' + format(price / 100, '.2f'), s('buy' + str(tier) + '_' + str(i)))
            for i, ((term, _, _), price) in enumerate(zip(TERMS, prices))],
            stats=[('Active places', str(places)), ('Daily ROBUX', str(daily) + ' R$'),
                   ('Sell your creations', 'Yes'), ('Create groups', str(groups)),
                   ('Signing bonus', '100 R$ for your first membership')], image=IMAGE_PREFIX + image_id)
        for i, ((term, days, lifetime), price) in enumerate(zip(TERMS, prices)):
            changes = ['BP_BANK_BALANCE=-' + format(price / 100, '.2f'),
                       r.set_('Club', tier), r.text('ClubName', name), r.set_('ClubAge', '<hero:age>'),
                       r.set_('DaysRemaining', days), r.set_('Lifetime', lifetime), r.set_('DailyRobux', daily),
                       r.set_('PlaceLimit', places), r.set_('GroupLimit', groups),
                       r.set_('Hat' + str(tier), 1), r.set_('WornHat', tier),
                       r.text('AvatarImage', IMAGE_PREFIX + image_id),
                       r.inc('Robux', f('mul', 100, f('sub', 1, p('SigningBonusGranted')))),
                       r.set_('SigningBonusGranted', 1)]
            action('buy' + str(tier) + '_' + str(i), name + ' — ' + term,
                   'Purchased ' + name + ' (' + term.lower() + ') for $' + format(price / 100, '.2f') + ' from my game bank.',
                   changes, [('(' + p('DaysRemaining') + ' > 0) || (' + p('Lifetime') + ' == 1)', r.scene('claimed')),
                             ({'filter': '[finance.bankBalance<' + format(price / 100, '.2f') + ']'}, s('bank_funds'))], image=IMAGE_PREFIX + image_id)
        action('wear' + str(tier), 'Wear ' + name + ' hard hat', 'Equipped my ' + name + ' hard hat on the Roblox account page.',
               [r.set_('WornHat', tier), r.text('AvatarImage', IMAGE_PREFIX + image_id)],
               [('(' + p('Hat' + str(tier)) + ' == 0)', r.scene('prerequisite'))], image=IMAGE_PREFIX + image_id)
    page('membership', 'Membership record', 'Your remaining term, daily allowance and owned hats are saved. Terms never renew automatically. Lifetime membership continues while this character lives. You keep published places after a term expires.', [
        ('Settle accrued allowance', seq(r.set_('SyncCalendar', 1), s('dashboard'))),
        ('Choose membership', s('clubs')), ('My hard hats', s('hats')), back],
        stats=[('Membership', p('ClubName')), ('Days remaining', p('DaysRemaining')),
               ('Lifetime pass (0 or 1)', p('Lifetime')), ('Daily Robux', p('DailyRobux')),
               ('Last credited allowance', p('LastAllowance'))])
    page('hats', 'My classic hard hats', 'Membership hats remain yours after a pass expires.', [
        ('Builders Club hard hat', s('wear1')), ('Turbo hard hat', s('wear2')),
        ('Outrageous hard hat', s('wear3')), back])
    # Old saved destinations remain valid, but cannot buy the superseded
    # fictional-Robux membership or claim its old annual flat stipend.
    for tier in range(1, 4):
        for old in ['club' + str(tier), 'grant' + str(tier)]:
            record = existing[r.scene(old)]
            for n in range(1, 5):
                for suffix in ['Text', 'RouteTo', 'AdvancedLogic', 'LogEntryLine1', 'LogEntryLine2']:
                    record[f'Choice{n}_{suffix}'] = ''
            record.update(Title='Classic membership has moved', Body='Choose your term and inspect its benefits in the illustrated Builders Club page.',
                          Choice1_Text='Open membership', Choice1_ButtonStyle='normal', Choice1_RouteTo=s('tier' + str(tier)))
    for key, target in [('clubs', 'clubs'), ('membership', 'membership')]:
        record = existing[r.scene(key)]
        for n in range(1, 5):
            for suffix in ['Text', 'RouteTo', 'AdvancedLogic', 'LogEntryLine1', 'LogEntryLine2']:
                record[f'Choice{n}_{suffix}'] = ''
        record.update(Title='Classic Builders Club', Body='Compare the illustrated membership terms, daily Robux and saved benefits.',
                      Choice1_Text='Open membership page', Choice1_ButtonStyle='normal', Choice1_RouteTo=s(target))
    existing[r.scene('wiki_club')]['Body'] = 'Classic Builders Club has three tiers with 15, 35 or 60 daily Robux and 10, 25 or 100 active places. Choose a 30-day, 180-day, 365-day or lifetime term using only your character’s game bank. The 100 Robux joining bonus is once per life. Allowance is paid only for simulated days that elapsed within the purchased term; expiry never deletes owned hats or old places.'
    existing[r.scene('wiki_studio')]['Body'] = 'Scripting, world building and playtests improve different parts of your project. Fix feedback and complete beta testing before publishing. Your membership controls public-place capacity; archiving makes room without deleting your saved creator history. Eight work activities refresh with character age.'

    page('catalog', 'ROBLOX Catalog', 'Create clothing, earn sales from your audience and wear your classic membership hats.', [
        ('Design a shirt', s('design')), ('Sell my clothing', s('sell')), ('My hard hats', s('hats')), back],
        stats=[('Design', p('DesignName')), ('Designs', p('Designs')), ('Catalog sales', p('CatalogSales'))], image='<GFC.roblox_social.AvatarImage>')
    for k, title, extra in [('shirt', 'Brick-pattern shirt', 5), ('jacket', 'Builder work jacket', 8), ('jersey', 'Obby team jersey', 6)]:
        action('design_' + k, title, 'Published an original ' + title.lower() + ' design to my Roblox portfolio.',
               [r.text('DesignName', title), r.inc('Designs'), r.inc('Skill', extra)], work=True)
    page('design', 'Make something original', 'Different designs build different amounts of creator experience. Every design consumes a development activity.', [
        ('Brick-pattern shirt', s('design_shirt')), ('Builder work jacket', s('design_jacket')),
        ('Obby team jersey', s('design_jersey')), back])
    action('sell', 'Open my catalog shop', 'Sold my original Roblox clothing and saved its catalog receipts.',
           [r.inc('CatalogSales', f('add', 1, f('div', p('Fans'), 20))),
            r.inc('Robux', f('add', 10, f('div', p('Fans'), 5))), r.set_('CatalogAge', '<hero:age>')],
           [('(' + p('Club') + ' == 0) || (' + p('Designs') + ' == 0)', r.scene('prerequisite')),
            ('(' + p('CatalogAge') + ' >= <hero:age>)', r.scene('claimed'))], work=True)
    action('group', 'Create a builders group', 'Founded a Roblox builders group and began recruiting other creators.',
           [r.inc('Groups'), r.text('GroupName', 'Brick Builders Workshop'), r.inc('Trust', 5),
            r.set_('GroupAge', '<hero:age>')],
           [('(' + p('Club') + ' == 0) || (' + p('Groups') + ' >= ' + p('GroupLimit') + ')', r.scene('prerequisite')),
            ('(' + p('GroupAge') + ' >= <hero:age>)', r.scene('claimed'))], work=True)
    page('social', 'Groups & inbox', 'Your creative community includes builders, clothing designers and players. Group creation uses your membership’s actual saved allowance.', [
        ('My builders group', s('group')), ('Player feedback', r.scene('community')),
        ('Builders Club launch mail', s('launch_mail')), ('Roblox wiki', r.scene('wiki_index'))],
        stats=[('Group', p('GroupName')), ('Groups owned', p('Groups')), ('Group allowance', p('GroupLimit'))])
    page('launch_mail', 'Builders Club is Here!', 'ROBLOX archive · August 16, 2007.\n\nThe classic launch introduced a paid builders tier while keeping free accounts available. Members could keep ten active places, sell their own clothing, receive 15 Robux per day and wear the Builders Club hard hat.\n\nYour game membership page recreates these benefits as saved offline mechanics. Turbo and Outrageous add larger allowances.', [
        ('Compare membership benefits', s('clubs')), ('Read the creator wiki', r.scene('wiki_index')), back], image=IMAGE_PREFIX + '1080951')

    # Expand the actual creator loop while preserving saved genre/progress IDs.
    for key, title, progress, quality, skill in [('script', 'Script the game systems', 20, 8, 8),
                                               ('world', 'Build the world and checkpoints', 35, 12, 3),
                                               ('feedback', 'Host a friends-only playtest', 15, 6, 2)]:
        changes = [r.inc('Progress', progress), r.inc('Quality', quality), r.inc('Skill', skill), r.set_('Tested', 0)]
        if key == 'feedback':
            changes += [r.inc('Feedback', 2)]
        action('work_' + key, title, title + ' for my active Roblox experience.', changes,
               [('(' + p('Genre') + ' == 0) || (' + p('Published') + ' == 1)', r.scene('prerequisite'))], work=True)
    action('fixbugs', 'Resolve the playtest report', 'Fixed playtest issues and improved the quality of my Roblox experience.',
           [r.set_('Feedback', 0), r.inc('Quality', 20), r.inc('Progress', 15), r.inc('Skill', 5), r.set_('Tested', 1)],
           [('(' + p('Feedback') + ' == 0) || (' + p('Genre') + ' == 0) || (' + p('Published') + ' == 1)', r.scene('prerequisite'))], work=True)
    page('work', 'Make your place worth visiting', 'Write systems, build the world, listen to players and fix issues. The different tasks improve different skills and use your saved annual work allowance.', [
        ('Script systems', s('work_script')), ('World and checkpoints', s('work_world')),
        ('Invite playtesters', s('work_feedback')), ('Fix their reported issues', s('fixbugs'))],
        stats=[('Progress', p('Progress')), ('Quality', p('Quality')), ('Open feedback', p('Feedback'))])
    existing[r.scene('studio')]['Choice2_RouteTo'] = s('work')
    existing[r.scene('studio')]['Choice2_AdvancedLogic'] = ''
    existing[r.scene('studio')]['Choice4_Text'] = 'Manage public places'
    existing[r.scene('studio')]['Choice4_RouteTo'] = s('manage_places')
    for genre in range(1, 5):
        row = existing[r.scene('genre' + str(genre))]
        data = json.loads(row['Choice1_AdvancedLogic'])
        data['cases'].insert(0, {'if': {'expression': '(' + p('ActivePlaces') + ' >= ' + p('PlaceLimit') + ')'},
                                'then': {'route_options': [{'route_to': s('manage_places')}]}})
        row['Choice1_AdvancedLogic'] = json.dumps(data)
    publish = existing[r.scene('publish')]
    d = json.loads(publish['Choice1_AdvancedLogic'])
    d['cases'].insert(0, {'if': {'expression': '(' + p('ActivePlaces') + ' >= ' + p('PlaceLimit') + ')'},
                          'then': {'route_options': [{'route_to': r.scene('prerequisite')}]}})
    target = d['else_when_no_matches']['route_options'][0]['route_to']
    target = target.replace(r.set_('Published', 1), seq(r.set_('Published', 1), r.inc('ActivePlaces')))
    target = target.replace(r.inc('Games'), seq(r.inc('Games'),
                            r.text('PlaceArchive', '<GFC.roblox_social.PlaceArchive> | Place <GFC.roblox_social.Games> - <GFC.roblox_social.GenreName>')))
    d['else_when_no_matches']['route_options'][0]['route_to'] = target
    publish['Choice1_AdvancedLogic'] = json.dumps(d)
    archive_cases = [('(' + p('Published') + ' == 0)', r.scene('prerequisite'))]
    action('archive', 'Retire the current public place', 'Archived the current Roblox place while retaining my lifetime creator record.',
           [r.inc('ActivePlaces', -1), r.set_('Published', 0), r.set_('Genre', 0), r.set_('Progress', 0)], archive_cases)
    action('archive_all', 'Make my places private', 'Made my public Roblox places private while keeping my creator history.',
           [r.set_('ActivePlaces', 0), r.set_('Published', 0), r.set_('Genre', 0), r.set_('Progress', 0)],
           [('(' + p('ActivePlaces') + ' == 0)', r.scene('prerequisite'))])
    page('manage_places', 'My public places', 'Your membership sets how many places you can publish. Expiry never deletes old places; you can make them private to free capacity while keeping your lifetime record.', [
        ('Archive the current place', s('archive')), ('Make all my places private', s('archive_all')), back],
        stats=[('Active places', p('ActivePlaces')), ('Publishing allowance', p('PlaceLimit'))])
    existing[r.scene('analytics')]['Body'] = '<GFC.roblox_social.PlaceArchive>'
    # Replace the initial generic list with the actual account, places,
    # illustrated membership, catalog, social and archive destinations.
    menu = json.loads(result[r.HUB])
    entries = [('My ROBLOX', 'account', 'iphone', 'Account; avatar; visits and Robux'),
               ('Games & places', None, 'books', 'Build systems; playtest; publish; update'),
               ('Builders Club', 'clubs', IMAGE_PREFIX + '1080951', 'Monthly; 6 months; annual; lifetime'),
               ('Catalog & trading', 'catalog', IMAGE_PREFIX + '11844853', 'Original clothing; sales and owned hats'),
               ('Groups & inbox', 'social', 'speech-balloon', 'Builders; player feedback and archived news'),
               ('My published record', None, 'books', 'Visits; income and retained place history')]
    menu['Items'] = [dict(Title=t, SecondLine=detail, Icon=icon, TileID='refresh_roblox_' + str(i), IsEnabled='v19-social',
                         ActionList=[dict(Index=0, ConditionList=[dict(ScenarioID=s(key) if key else r.scene('studio' if i == 1 else 'analytics'), ScenarioFile=r.SCENES)])])
                     for i, (t, key, icon, detail) in enumerate(entries)]
    result[r.HUB] = json.dumps(menu, indent=2)
    # Publish still has its original main entry; expose archiving on the record.
    existing[r.scene('analytics')]['Choice2_Text'] = 'Archive current place'
    existing[r.scene('analytics')]['Choice2_ButtonStyle'] = 'normal'
    existing[r.scene('analytics')]['Choice2_RouteTo'] = s('archive')

    result[r.DEFAULTS] = r.csv_text(defaults)
    result[r.SCENES] = r.csv_text(rows, header)
    life_key = 'genesis_v18_defaults_life_v18'
    life_defs = list(csv.DictReader(io.StringIO(assets[life_key])))
    assert not any(row['key'] == 'PortraitCacheAge' for row in life_defs)
    life_defs.append(dict(key='PortraitCacheAge', type='int', value=-1,
                          reset_on_ageup='', minimum=-1, maximum=999))
    result[life_key] = r.csv_text(life_defs)
    return church(assets, result)


def church(assets, result):
    """Organize existing vocation actions around illustrated continuing stories."""
    key = 'genesis_v18_church52'
    menu = json.loads(assets[key])
    original = {x['Title']: x for x in menu['Items']}
    groups = [
        ('parish', 'Parish & family', ['Attend religious services', 'Charitable work', 'Community choir', 'Get to know a colleague']),
        ('formation', 'Seminary formation', ['Enter the seminary', 'Study theology', 'Study Church history', 'Study Latin', 'Meet your instructor', 'Public speaking']),
        ('ministry', 'Parish leadership', ['Organize parish work', 'Manage parish funds', 'Discuss a disagreement']),
        ('vocation', 'My vocation & progression', ['My vocation', 'Review progression', 'Attend a conclave', 'The Holy See', 'Leave formation or ministry']),
    ]
    for suffix, title, names in groups:
        name = 'genesis_v18_church_refresh_' + suffix
        items = [dict(original[n]) for n in names]
        for item in items:
            if suffix in ['formation', 'ministry'] or item['Title'] in ['Attend a conclave', 'Review progression']:
                item['IsEnabled'] = 'v19-adult'
        result[name] = json.dumps(dict(ListID=name, Title=title, PresentationMode='Normal', Items=items), indent=2)
    menu['Items'] = [dict(Title=title, SecondLine=detail, Icon=icon, TileID='church_refresh_' + suffix,
                         ActionList=[dict(Index=0, ConditionList=[dict(ListID='genesis_v18_church_refresh_' + suffix)])])
                     for suffix, title, detail, icon in [
                         ('parish', 'Parish & family', 'Services; choir; charitable work and familiar faces', 'mayomods49/icons/49-basilica'),
                         ('formation', 'Seminary formation', 'From age 18; theology; history; Latin and mentoring', 'mayomods49/icons/49-gate'),
                         ('ministry', 'Parish leadership', 'Budgets; community priorities and disagreements', 'mayomods49/icons/49-priest'),
                         ('vocation', 'My vocation & progression', 'Formation; ordination; appointments and conclave', 'mayomods49/icons/49-journal')]]
    for item in menu['Items'][1:3]:
        item['IsEnabled'] = 'v19-adult'
    result[key] = json.dumps(menu, indent=2)
    rows = list(csv.DictReader(io.StringIO(result[r.SCENES])))
    for record in rows:
        code = record['ScenarioID'].removeprefix('scenario.activitiesV18.action52_')
        if not code.isdigit() or not 91 <= int(code) <= 108:
            continue
        number = int(code)
        if number == 91:
            continue
        if number in [92, 93, 94, 96, 97, 98]:
            record['BigImageString'] = 'mayomods49/icons/49-gate'
            record['Choice1_Text'] = {92: 'Begin formation', 93: 'Work through the theology lesson',
                                     94: 'Discuss the history case', 96: 'Ask Father Reed for guidance',
                                     97: 'Deliver a practice homily', 98: 'Translate the study passage'}[number]
        elif number in [102, 103]:
            record['BigImageString'] = 'mayomods49/icons/49-conclave'
        else:
            record['BigImageString'] = 'mayomods49/icons/49-basilica'
        if number == 93:
            record['Body'] = 'A parish family asks how faith should guide a difficult decision. Study the passage, compare interpretations with your class, then explain your reasoning to Father Reed. Your theology result counts toward ordination. <GFC.gameplay52.ClergyStatus>'
        elif number == 94:
            record['Body'] = 'Your seminar group is studying a historical disagreement over community service. Compare what leaders decided with what parish families needed; discuss what you would change. <GFC.gameplay52.ClergyStatus>'
        elif number == 108:
            record['Body'] = 'The pantry needs supplies while the parish building needs repairs. You have <GFC.gameplay52.ParishFunds> in parish funds. Food relief improves trust; repairs strengthen discipline. Either decision spends 25 once. <GFC.gameplay52.ClergyStatus>'
    parish_stories(assets, result, rows)
    result[r.SCENES] = r.csv_text(rows)
    return result


def parish_stories(assets, result, rows):
    """Three continuing cases with mutually exclusive, saved consequences."""
    defaults_key = 'genesis_v18_defaults_gameplay52'
    defs = list(csv.DictReader(io.StringIO(result.get(defaults_key, assets[defaults_key]))))
    # The caller supplies the existing defaults separately to avoid creating a
    # competing church save container or replacing its established field IDs.
    if not defs:
        raise AssertionError('Existing church defaults are required')
    for key, value, hi in [('CaseNumber', 1, 3), ('CaseAge', -1, 999),
                           ('CaseCompleted', 0, 1000000), ('StoryJournalSequence', 0, 100000000),
                           ('StoryJournalLogged', 0, 100000000)]:
        defs.append(dict(key=key, type='int', value=value, reset_on_ageup='', minimum=-1 if value == -1 else 0, maximum=hi))
    for key, value in [('CaseOutcome', 'Your parish story begins with the next assignment.'), ('StoryJournalMessage', '')]:
        defs.append(dict(key=key, type='string', value=value, reset_on_ageup='', minimum='', maximum=''))
    result[defaults_key] = r.csv_text(defs)
    owner = 'gameplay52'
    p = lambda key: '<GFC.' + owner + '.' + key + '>'
    set_ = lambda key, value: 'BP_GFC_MODIFY_PROPERTY=' + owner + ':' + key + ':=' + str(value)
    text = lambda key, value: 'BP_GFC_SET_STRING=' + owner + ':' + key + ':' + value
    inc = lambda key, n: set_(key, r.f('add', p(key), n))
    s = lambda key: 'scenario.activitiesV18.church_refresh_' + key
    back = ('Back to parish', 'BP_SHOW_LIST=genesis_v18_church52')
    header = list(rows[0])

    def page(key, title, body, choices, image='mayomods49/icons/49-basilica'):
        row = dict.fromkeys(header, '')
        row.update(ScenarioID=s(key), Style='normal', ExteriorTitle='Church & Seminary',
                   Title=title, Body=body, BigImageString=image,
                   HasDismissButton='true', EmojiString='mayomods49/icons/49-priest')
        for i, (label, route) in enumerate(choices, 1):
            row[f'Choice{i}_Text'] = label
            row[f'Choice{i}_ButtonStyle'] = 'normal'
            row[f'Choice{i}_AdvancedLogic' if isinstance(route, dict) else f'Choice{i}_RouteTo'] = json.dumps(route) if isinstance(route, dict) else route
        rows.append(row)

    def logic(cases, target):
        return dict(cases=[{'if': c if isinstance(c, dict) else {'expression': c},
                            'then': {'route_options': [{'route_to': t}]}} for c, t in cases],
                    else_when_no_matches={'route_options': [{'route_to': target}]})

    def resolve(case, message, effects, prerequisites=()):
        guards = [('(' + p('CaseNumber') + ' != ' + str(case) + ') || (' + p('CaseAge') + ' >= <hero:age>)', s('record'))]
        guards += list(prerequisites)
        guards += [('(' + p('ClergyAge') + ' >= <hero:age>) && (' + p('ClergyActions') + ' >= 6)', s('busy'))]
        count = r.f('add', r.f('mul', p('ClergyActions'), r.f('clamp', r.f('sub', 1,
                    r.f('max', r.f('sub', '<hero:age>', p('ClergyAge')), 0)), 0, 1)), 1)
        target = r.seq(set_('ClergyActions', count), set_('ClergyAge', r.f('max', p('ClergyAge'), '<hero:age>')),
                       *effects, set_('CaseAge', '<hero:age>'), set_('CaseNumber', case % 3 + 1),
                       inc('CaseCompleted', 1), text('CaseOutcome', message),
                       text('StoryJournalMessage', 'I ' + message[0].lower() + message[1:]),
                       inc('StoryJournalSequence', 1), s('record'))
        return logic(guards, target)

    page('begin', 'A story in your parish', 'Father Reed, Brother Mateo and parish families remember your decisions. Resolve one case per character year; each case also uses one church activity. Cases continue in order rather than regenerating on every visit.', [
        ('Open the current case', logic([
            ('(' + p('CaseAge') + ' >= <hero:age>)', s('record')),
            ('(' + p('CaseNumber') + ' == 1)', s('pantry')),
            ('(' + p('CaseNumber') + ' == 2)', s('welcome'))], s('disagreement'))),
        ('My parish story', s('record')), back])
    page('record', 'Your parish story', p('CaseOutcome'), [
        ('Return to parish life', 'BP_SHOW_LIST=genesis_v18_church52'),
        ('Next assignment', s('begin'))])
    page('busy', 'Time to reflect', 'You have already used this year’s six church activities. Your current case and prior choices remain saved for a later year.', [back])
    page('requirements', 'This option is not available', 'Check your formation, parish funds or role. No case, money or church activity was spent.', [back])
    page('pantry', 'The pantry before winter', 'Several parish families need food, while the pantry’s roof needs repair. Father Reed asks you to choose a useful response with the resources you actually have.', [
        ('Organize family volunteers', resolve(1, 'Organized pantry volunteers; parish trust grew and relationships strengthened.', [inc('ParishTrust', 8), inc('Colleague', 4)])),
        ('Fund food relief — 25 parish funds', resolve(1, 'Funded food relief for parish families using 25 from the parish budget.', [inc('ParishFunds', -25), inc('ParishTrust', 12)],
             [('(' + p('ClergyRank') + ' < 3) || (' + p('ParishFunds') + ' < 25)', s('requirements'))])),
        ('Repair the pantry — 25 parish funds', resolve(1, 'Repaired the pantry roof using 25 parish funds; long-term readiness and discipline improved.', [inc('ParishFunds', -25), inc('Discipline', 10)],
             [('(' + p('ClergyRank') + ' < 3) || (' + p('ParishFunds') + ' < 25)', s('requirements'))])), back])
    page('welcome', 'A new family at the service', 'A newcomer feels out of place during a crowded service. Brother Mateo asks how you will help them find a place in the community.', [
        ('Introduce them to parish families', resolve(2, 'Welcomed a new family and helped them meet their parish neighbors.', [inc('ParishTrust', 9), inc('Colleague', 3)])),
        ('Prepare an inclusive service reading', resolve(2, 'Prepared a service reading that helped newcomers follow the service.', [inc('Theology', 6), inc('Speaking', 6)],
             [('(<hero:age> < 18) || (' + p('ClergyRank') + ' < 1)', s('requirements'))])),
        ('Invite them to the community choir', resolve(2, 'Introduced a new family to the community choir and built their confidence.', [inc('ParishTrust', 6), inc('Discipline', 4)])), back])
    page('disagreement', 'Brother Mateo’s disagreement', 'Mateo wants more parish time spent on visiting isolated families. Another colleague wants a larger public event. Choose how to handle the disagreement; each response leaves a different record.', [
        ('Listen and arrange shared visits', resolve(3, 'Listened to Mateo and organized shared family visits; trust and friendship improved.', [inc('Colleague', 10), inc('ParishTrust', 5)])),
        ('Present a structured compromise', resolve(3, 'Presented a compromise balancing family visits and public services.', [inc('Speaking', 8), inc('Discipline', 4)])),
        ('Insist on the public event', resolve(3, 'Insisted on a public parish event; public confidence grew but Mateo felt overlooked.', [inc('Speaking', 10), inc('Colleague', -6)])), back])
    menu = json.loads(result['genesis_v18_church52'])
    menu['Items'].insert(0, dict(Title='Your parish story', SecondLine='Continuing cases; remembered choices and visible consequences',
        Icon='mayomods49/icons/49-journal', TileID='church_refresh_story',
        ActionList=[dict(Index=0, ConditionList=[dict(ScenarioID=s('begin'), ScenarioFile=r.SCENES)])]))
    result['genesis_v18_church52'] = json.dumps(menu, indent=2)
