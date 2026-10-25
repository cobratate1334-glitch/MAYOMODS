"""Author a saved, offline Roblox creator simulation using existing Genesis fields."""
import csv
import io
import json

OWNER = 'roblox_social'
PREFIX = 'scenario.activitiesV18.roblox_'
SCENES = 'genesis_activities_v18'
DEFAULTS = 'genesis_v18_defaults_' + OWNER
HUB = 'genesis_v18_roblox_social'


def csv_text(rows, header=None):
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, header or list(rows[0]), lineterminator='\r\n')
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().rstrip('\r\n')


def p(key):
    return '<GFC.' + OWNER + '.' + key + '>'


def f(name, *args):
    return '<function:' + name + ':' + ':'.join(map(str, args)) + '>'


def set_(key, value):
    return 'BP_GFC_MODIFY_PROPERTY=' + OWNER + ':' + key + ':=' + str(value)


def inc(key, value=1):
    return set_(key, f('add', p(key), value))


def text(key, value):
    assert ':' not in value and '>>' not in value
    return 'BP_GFC_SET_STRING=' + OWNER + ':' + key + ':' + value


def scene(key):
    return PREFIX + key


def seq(*parts):
    return '>>'.join(parts)


def logic(cases, target):
    return dict(cases=[{'if': {'expression': expr},
                       'then': {'route_options': [{'route_to': route}]}}
                      for expr, route in cases],
                else_when_no_matches={'route_options': [{'route_to': target}]})


def build(base):
    """Return an additive overlay. Calling twice is rejected to avoid duplicates."""
    assert DEFAULTS not in base, 'Roblox is already registered'
    original = list(csv.DictReader(io.StringIO(base[SCENES])))
    header = list(original[0])
    assert 'Choice1_LogEntryLine1' in header
    rows, fields, assets = [], [], {}

    def field(key, value=0, maximum=100000000, minimum=0):
        fields.append(dict(key=key, type='string' if isinstance(value, str) else 'int',
                           value=value, reset_on_ageup='',
                           minimum='' if isinstance(value, str) else minimum,
                           maximum='' if isinstance(value, str) else maximum))

    for key, value, maximum, minimum in [
        ('Joined', 0, 1, 0), ('Robux', 0, 100000000, 0), ('Skill', 0, 100, 0),
        ('Actions', 0, 8, 0), ('ActionAge', -1, 999, -1),
        ('Genre', 0, 4, 0), ('Progress', 0, 100, 0), ('Quality', 0, 100, 0),
        ('Tested', 0, 1, 0), ('Published', 0, 1, 0), ('Games', 0, 10000, 0),
        ('Visits', 0, 100000000, 0), ('Fans', 0, 10000000, 0),
        ('Trust', 50, 100, 0), ('RevenueAge', -1, 999, -1),
        ('Club', 0, 3, 0), ('ClubAge', -1, 999, -1), ('ClubClaimAge', -1, 999, -1),
        ('CommunityAge', -1, 999, -1), ('Outfit', 0, 1, 0),
        ('LastCommunity', 0, 3, 0),
        ('LastIncome', 0, 1000000, 0), ('LastVisits', 0, 1000000, 0),
        ('JournalSequence', 0, 100000000, 0), ('JournalLogged', 0, 100000000, 0)]:
        field(key, value, maximum, minimum)
    for key, value in [('GenreName', 'No experience'), ('ClubName', 'Free account'),
                       ('Result', 'Create an account to begin.'),
                       ('LastEvent', 'No community decisions yet.'), ('JournalMessage', '')]:
        field(key, value)

    def page(key, title, body, choices, stats=None, icon='iphone'):
        row = dict.fromkeys(header, '')
        row.update(ScenarioID=scene(key), Style='normal', ExteriorTitle='MayoMods',
                   Title=title, Body=body, EmojiString=icon, HasDismissButton='true')
        if stats:
            row['TableRows'] = json.dumps([dict(row=i, key=label + ':', value=value)
                                          for i, (label, value) in enumerate(stats, 1)])
        for n, choice in enumerate(choices, 1):
            assert n <= 4
            label, route, *journal = choice
            row['Choice' + str(n) + '_Text'] = label
            row['Choice' + str(n) + '_ButtonStyle'] = 'normal'
            row['Choice' + str(n) + ('_AdvancedLogic' if isinstance(route, dict)
                                    else '_RouteTo')] = json.dumps(route) if isinstance(route, dict) else route
            if journal:
                row['Choice' + str(n) + '_LogEntryLine1'] = journal[0]
        rows.append(row)

    back = ('Back to Roblox', 'BP_SHOW_LIST=' + HUB)
    # Separate preparation/confirmation scenes ensure rejected actions do not
    # emit a completion journal line. Recheck on commit to reject stale scenes.
    def gate(target, *, account=True, cases=(), action=False):
        rules = [('(<hero:age> < 13)', scene('young'))]
        if account:
            rules.append(('(' + p('Joined') + ' == 0)', scene('account_required')))
        rules.extend(cases)
        if action:
            rules.append(('(' + p('ActionAge') + ' >= <hero:age>) && (' + p('Actions') + ' >= 8)', scene('quota')))
        return logic(rules, target)

    def spend_action():
        return [set_('Actions', f('add', f('mul', p('Actions'),
                                                    f('clamp', f('sub', 1, f('max', f('sub', '<hero:age>', p('ActionAge')), 0)), 0, 1)), 1)),
                set_('ActionAge', f('max', p('ActionAge'), '<hero:age>'))]

    def commit(key, title, description, operations, *, cases=(), action=False):
        final_ops = spend_action() if action else []
        final_ops += operations
        target = seq(*final_ops, text('Result', description),
                     text('JournalMessage', 'I ' + description[0].lower() + description[1:]),
                     inc('JournalSequence'), scene(key + '_done'))
        page(key, title, description, [('Confirm', gate(target, cases=cases, action=action)), back])
        page(key + '_done', title, p('Result'), [
            ('Continue', 'BP_SHOW_LIST=' + HUB)])

    for key, title, body in [
        ('young', 'Available from age 13', 'This offline social simulation opens at age 13.'),
        ('account_required', 'Create your account', 'Create a free account before developing or shopping.'),
        ('quota', 'A full year of projects', 'You used eight development activities at this age. Membership and your published work are retained.'),
        ('funds', 'Not enough Robux', 'Earn fictional Robux from your published experience. No real money or game bank balance was spent.'),
        ('prerequisite', 'Not ready yet', 'Check your project stage, progress, beta test and existing purchases. Nothing was spent.'),
        ('claimed', 'Already completed', 'This action was already completed at this age. Your saved balance and record are unchanged.')]:
        page(key, title, body, [back])

    page('account', 'Your Roblox account', 'An offline creator simulation. No real Roblox account or Robux purchases are involved.', [
        ('Create free account', gate(seq(set_('Joined', 1), set_('Robux', 100),
                                         text('Result', 'Created a Roblox account with 100 starter Robux.'),
                                         text('JournalMessage', 'I created an offline Roblox creator account.'),
                                         inc('JournalSequence'),
                                         scene('account_done')), account=False,
                                   cases=[('(' + p('Joined') + ' == 1)', scene('claimed'))])),
        back], stats=[('Robux', p('Robux')), ('Published games', p('Games')), ('Fans', p('Fans')),
                       ('Classic outfit owned (0 or 1)', p('Outfit'))])
    page('account_done', 'Welcome, builder', p('Result'), [
        ('Continue', 'BP_SHOW_LIST=' + HUB)])

    page('studio', 'Roblox Studio', 'Plan an experience, build it, beta test and publish. Eight work sessions per character age prevent endless reward grinding.', [
        ('Choose experience genre', gate(scene('genres'))),
        ('Build and beta test', gate(scene('work'))),
        ('Publish or update', gate(scene('release'))), back],
        stats=[('Experience', p('GenreName')), ('Progress', p('Progress')), ('Quality', p('Quality')),
               ('Coding skill', p('Skill'))])
    for idx, label in enumerate(['Obby', 'Tycoon', 'Roleplay town', 'Survival adventure'], 1):
        commit('genre' + str(idx), label, 'Planned a ' + label.lower() + ' experience.',
               [set_('Genre', idx), text('GenreName', label), set_('Progress', 0), set_('Quality', 10),
                set_('Tested', 0), set_('Published', 0)],
               cases=[('(' + p('Genre') + ' != 0) && (' + p('Published') + ' == 0)', scene('prerequisite'))])
    page('genres', 'Choose your next experience', 'Finish your active draft before starting another. Starting a new experience retains your career totals.',
         [(label, scene('genre' + str(idx))) for idx, label in enumerate(
             ['Obby', 'Tycoon', 'Roleplay town', 'Survival adventure'], 1)])
    draft = [('(' + p('Genre') + ' == 0) || (' + p('Published') + ' == 1)', scene('prerequisite'))]
    commit('build', 'Develop your experience', 'Developed the active Roblox experience and improved coding skill.',
           [inc('Progress', 35), inc('Quality', 12), inc('Skill', 5), set_('Tested', 0)], cases=draft, action=True)
    commit('test', 'Beta playtest', 'Beta-tested the experience and fixed player-reported issues.',
           [inc('Quality', 10), set_('Tested', 1)],
           cases=draft + [('(' + p('Progress') + ' < 100) || (' + p('Tested') + ' == 1)', scene('prerequisite'))], action=True)
    page('work', 'Build and test', 'Building adds 35 progress and 12 quality. A completed draft needs one beta test before release.', [
        ('Develop', scene('build')), ('Run beta playtest', scene('test')), ('Back to Studio', scene('studio'))])
    commit('publish', 'Publish your experience', 'Published a beta-tested Roblox experience.',
           [set_('Published', 1), inc('Games'), inc('Fans', f('add', p('Quality'), p('Skill')))],
           cases=draft + [('(' + p('Progress') + ' < 100) || (' + p('Tested') + ' == 0)', scene('prerequisite'))], action=True)
    # Income is applied on this guarded confirmation, once per age. Creating
    # another experience never resets the income claim marker.
    income = f('add', 60, f('mul', p('Quality'), 2), p('Fans'))
    visits = f('add', 100, f('mul', p('Quality'), 15), f('mul', p('Fans'), 2))
    commit('update', 'Ship an update and settle earnings', 'Released an experience update and saved its visits and Robux earnings.',
           [inc('Quality', 3), set_('LastIncome', income), set_('LastVisits', visits),
            inc('Robux', p('LastIncome')), inc('Visits', p('LastVisits')),
            inc('Fans', 20), set_('RevenueAge', '<hero:age>')],
           cases=[('(' + p('Published') + ' == 0)', scene('prerequisite')),
                  ('(' + p('RevenueAge') + ' >= <hero:age>)', scene('claimed'))], action=True)
    page('release', 'Publish and update', 'First publish requires full progress and a beta test. Earnings settle only once per character age across all experiences.', [
        ('Publish beta-tested experience', scene('publish')), ('Ship annual update', scene('update')),
        ('Creator analytics', scene('analytics')), ('Back to Studio', scene('studio'))])
    page('analytics', 'Creator analytics', 'Figures belong to this offline career. Visits and income are saved when you ship an update.', [back],
         stats=[('Career visits', p('Visits')), ('Fans', p('Fans')), ('Robux balance', p('Robux')),
                ('Last update visits', p('LastVisits')), ('Last update income', p('LastIncome'))])

    for tier, name, price, grant in [(1, 'Builders Club', 200, 100),
                                    (2, 'Turbo Builders Club', 500, 275),
                                    (3, 'Outrageous Builders Club', 1000, 600)]:
        commit('club' + str(tier), name, 'Joined ' + name + ' for one character year.',
               [inc('Robux', -price), set_('Club', tier), text('ClubName', name),
                set_('ClubAge', '<hero:age>')],
               cases=[('(' + p('ClubAge') + ' >= <hero:age>)', scene('claimed')),
                      ('(' + p('Robux') + ' < ' + str(price) + ')', scene('funds'))])
        commit('grant' + str(tier), name + ' stipend', 'Collected the annual ' + name + ' Robux stipend.',
               [inc('Robux', grant), set_('ClubClaimAge', '<hero:age>')],
               cases=[('(' + p('Club') + ' != ' + str(tier) + ') || (' + p('ClubAge') + ' != <hero:age>)', scene('prerequisite')),
                      ('(' + p('ClubClaimAge') + ' >= <hero:age>)', scene('claimed'))])
    page('clubs', 'Classic Builders Club', 'Optional nostalgic mode. Annual simulated passes cost 200, 500 or 1,000 Robux; stipends are 100, 275 or 600. No automatic renewal or real payment.', [
        ('Builders Club — 200', scene('club1')), ('Turbo — 500', scene('club2')),
        ('Outrageous — 1,000', scene('club3')), ('Membership and stipend', scene('membership'))])
    page('membership', 'Your membership', 'A pass is active only at its purchase age. An old membership name is retained as career history, without charging a renewal.', [
        ('Collect Builders Club stipend', scene('grant1')), ('Collect Turbo stipend', scene('grant2')),
        ('Collect Outrageous stipend', scene('grant3')), back],
        stats=[('Last membership', p('ClubName')), ('Purchased at age', p('ClubAge'))])
    commit('outfit', 'Classic builder outfit', 'Bought a classic outfit for the Roblox avatar inventory.',
           [inc('Robux', -75), set_('Outfit', 1)],
           cases=[('(' + p('Outfit') + ' == 1)', scene('claimed')),
                  ('(' + p('Robux') + ' < 75)', scene('funds'))])

    for event_id, (key, title, body, trust, fans) in enumerate([
        ('access', 'A player cannot finish the obby', 'A player asks for clearer checkpoints and accessible controls. You revise the experience after listening.', 8, 12),
        ('copy', 'A copied asset report', 'A player flags an uncredited model. You remove it, credit the source and replace it with original work.', 10, 5),
        ('scam', 'A suspicious Robux offer', 'Someone offers free currency for an account password. You report the message and publish a community warning.', 12, 3)], 1):
        commit('community_' + key, title, body,
               [inc('Trust', trust), inc('Fans', fans), text('LastEvent', title),
                set_('LastCommunity', event_id), set_('CommunityAge', '<hero:age>')],
               cases=[('(' + p('CommunityAge') + ' >= <hero:age>)', scene('claimed')),
                      ('(' + p('LastCommunity') + ' == ' + str(event_id) + ')', scene('claimed'))], action=True)
    page('community', 'Community and moderation', 'Choose one community project per character age. Consecutive projects must differ. Each has different trust and audience effects.', [
        ('Accessibility feedback', scene('community_access')), ('Asset credit dispute', scene('community_copy')),
        ('Report a Robux scam', scene('community_scam')), back],
        stats=[('Trust', p('Trust')), ('Latest project', p('LastEvent'))])

    wiki = [
        ('studio', 'Creator wiki — Studio', 'Choose one of four genres, complete three development sessions, then beta test and publish. Starting a new experience preserves total games, fans, visits and currency.'),
        ('robux', 'Creator wiki — Robux', 'Robux here are fictional. Create your account for a one-time 100 grant; published experiences earn more through a guarded annual update. No cash-out, real account or real purchase exists.'),
        ('club', 'Creator wiki — classic membership', 'Builders Club, Turbo and Outrageous are nostalgic names. These optional one-year passes are a game design, not current Roblox products or historical daily payout rates.'),
        ('safety', 'Creator wiki — community safety', 'Credit art and models, improve accessibility, and report suspicious currency offers. Each community project changes saved trust and audience counts.'),
        ('records', 'Creator wiki — saving and time', 'Each life owns its account state. Eight development activities refresh when the character ages. Income, membership stipends and community projects have independent age markers. Menus never grant rewards.')]
    for key, title, body in wiki:
        page('wiki_' + key, title, body, [('Back to wiki', 'BP_SHOW_LIST=genesis_v18_roblox_wiki'), back], icon='books')

    def menu(name, title, entries):
        assets[name] = json.dumps(dict(ListID=name, Title=title, PresentationMode='Normal', Items=[
            dict(Title=label, SecondLine=detail, Icon=icon, TileID=name + '_' + str(i),
                 ActionList=[dict(Index=0, ConditionList=[dict(ScenarioID=scene(key), ScenarioFile=SCENES)])])
            for i, (label, key, icon, detail) in enumerate(entries)]), indent=2)

    menu(HUB, 'Roblox', [
        ('My account', 'account', 'iphone', 'Robux; games and audience'),
        ('Roblox Studio', 'studio', 'books', 'Build; playtest; publish and update'),
        ('Classic Builders Club', 'clubs', 'suitcase', 'Builders Club; Turbo; Outrageous'),
        ('Community', 'community', 'speech-balloon', 'Accessibility; credits and moderation'),
        ('Classic outfit', 'outfit', 'iphone', '75 Robux; one inventory purchase'),
        ('Creator wiki', 'wiki_index', 'books', 'Offline guides and game rules')])
    menu('genesis_v18_roblox_wiki', 'Roblox creator wiki',
         [(title.replace('Creator wiki — ', ''), 'wiki_' + key, 'books', '') for key, title, _ in wiki])
    page('wiki_index', 'Roblox creator wiki', 'Browse the offline guide.', [
        ('Open wiki', 'BP_SHOW_LIST=genesis_v18_roblox_wiki'), back])

    assets[DEFAULTS] = csv_text(fields)
    assets[SCENES] = csv_text(original + rows, header)
    # Preserve registry preamble and all prior rows. Register exactly one Social entry.
    lines = base['genesis_feature_containers'].splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith('ContainerId,'))
    registry = list(csv.DictReader(io.StringIO('\n'.join(lines[start:]))))
    entry = dict.fromkeys(registry[0], '')
    entry.update(ContainerId=OWNER, DisplayName='Roblox', InitDataSheet=DEFAULTS,
                 AgeUpPriority='content', EntryMenu='SocialMedia', EntryLabel='Roblox',
                 EntryEmoji='iphone', EntrySecondLine='Studio; Robux; classic Builders Club',
                 EntryOrder='25', EntryListID=HUB)
    assets['genesis_feature_containers'] = '\r\n'.join(lines[:start]) + '\r\n' + csv_text(registry + [entry])
    return assets
