"""Concrete native crime, prison and research actions on the exact 1110 data.

No new root tabs.  Existing identifiers, real money blueprints, native inmate
effects and the original prison-sentence payload are retained.
"""
import copy
import csv
import io
import json

from life_rework.content import p, scene, menu, set_, inc, text, seq, fun, csv_text
from playable_repair.school_content import logic, MANUAL_FILTER


def refresh_annual_copies(a, base):
    current = {r['ScenarioID']: r for r in a.rows}
    owned = getattr(a, 'playable_action_ids', set())
    for name, value in sorted({**base, **a.assets}.items()):
        if name == 'genesis_life_rework' or not value.startswith('ScenarioID,'):
            continue
        rows = list(csv.DictReader(io.StringIO(value)))
        changed = False
        existing = {r['ScenarioID'] for r in rows}
        for index, old in enumerate(rows):
            key = old['ScenarioID']
            source = current.get(key) if key in owned else None
            if key.startswith(scene('annual_prison1110_')):
                source = current.get(key.replace('annual_prison1110_', 'prison_annual1110_'))
            if source is None:
                continue
            row = copy.deepcopy(source)
            for field in ['ScenarioID', 'Filter', 'IsAgeUpScenario', 'HasDismissButton', 'HeroAge', 'DrawFilter']:
                row[field] = old.get(field, '')
            if old.get('IsAgeUpScenario', '').lower() != 'true':
                row.update(Filter=MANUAL_FILTER, IsAgeUpScenario='false')
            rows[index] = row
            changed = True
        if changed and ('annual' in name or any(r.get('IsAgeUpScenario', '').lower() == 'true' for r in rows)):
            rows.extend(dict(copy.deepcopy(current[key]), Filter=MANUAL_FILTER, IsAgeUpScenario='false')
                        for key in sorted(owned - existing))
        if changed:
            a.assets[name] = csv_text(rows)


def build(a, base):
    owned = set()
    a.playable_action_ids = owned
    registered = {r['EmojiString'] for r in csv.DictReader(io.StringIO(base['genesis_lookup_emoji_visuals']))}

    def glyph(name):
        return name if name in registered else 'memo'

    def page(key, title, body, choices, icon='memo', context='Your life', stats=None):
        ident = scene(key)
        a.rows[:] = [r for r in a.rows if r['ScenarioID'] != ident]
        a.page(key, title, body, choices, glyph(icon), stats)
        a.rows[-1].update(ExteriorTitle=context, BigImageString='')
        owned.add(ident)
        return ident

    def outcome(key, title, body, back, changes=(), native=0, checks=(), quota=None,
                icon='memo', context='Your life', journal=True):
        page(key + '_result', title, body, [('Continue', back)], icon, context)
        effects = list(changes)
        guards = list(checks)
        if quota:
            prefix, limit = quota
            a.prop(prefix + 'Age', -1, -1, 999)
            a.prop(prefix + 'Used', 0, 0, limit)
            # Same stable annual accounting as original content.  Reopen and
            # stale callbacks cannot reset the session allowance.
            effects[:0] = [set_(prefix + 'Used', fun('add', fun('mul', p(prefix + 'Used'), fun('clamp', fun('sub', 1, fun('max', fun('sub', '<hero:age>', p(prefix + 'Age')), 0)), 0, 1)), 1)),
                           set_(prefix + 'Age', '<hero:age>')]
            wait = 'heist_break1111' if context == 'Your crew' else 'prison_break1111' if context == 'Prison life' else 'field_break1111'
            guards.append((f'({p(prefix + "Age")} >= <hero:age>) && ({p(prefix + "Used")} >= {limit})', scene(wait)))
        if native:
            effects.append(set_('NativeAction', native))
        if journal:
            effects += [text('JournalMessage', context + ': ' + body), inc('JournalSequence')]
        return logic(guards, seq(*effects, scene(key + '_result')))

    def replace_list(name, title, entries):
        old = json.loads(a.assets.get(name, base[name]))
        collection = 'Items' if 'Items' in old else 'ListItems'
        previous = old[collection]
        old['Title'] = title
        old[collection] = []
        for index, (label, target, icon, detail) in enumerate(entries):
            item = a.tile(label, target, glyph(icon), detail)
            if index < len(previous):
                item['TileID'] = previous[index]['TileID']
            old[collection].append(item)
        a.assets[name] = json.dumps(old, indent=2)

    # HEISTS: one crime entry owns crew, missions and history.  Payout is an
    # explicit earned state, never inferred from the planned amount of loot.
    home = menu('genesis_heists1106')
    a.prop('HeistPayout1111', 0, 0, 1)
    a.prop('HeistFailed1111', 0, 0, 100000)
    heist_checks = [('(<hero:age> < 18)', scene('heist_locked1106')),
                    (f'({p("NativeInPrison1105")} == 1)', scene('heist_locked1106'))]

    def heist(target, extra=()):
        return logic(heist_checks + list(extra), target)

    def heist_out(key, title, body, changes=(), back=home, checks=(), quota=None, icon='suitcase'):
        return outcome(key, title, body, back, changes, checks=heist_checks + list(checks),
                       quota=quota, context='Your crew', icon=icon)

    for name in ['genesis_heists1106', 'genesis_v18_crime52_62']:
        replace_list(name, 'Heists and crew', [
            ('Plan a heist', scene('heist_jobs1106'), 'suitcase', 'Choose a job or resume one'),
            ('Your crew', scene('heist_crew1106'), 'handshake', 'Join train or leave'),
            ('Job history', scene('heist_record1106'), 'memo', 'Results and police attention')])
    # The original redundant Leave crew category remains a valid saved link,
    # but no longer appears as a separate crime row in the feature registry.
    replace_list('genesis_v18_crime52_64', 'Your crew', [
        ('Your crew', scene('heist_crew1106'), 'handshake', 'Membership and trust')])
    page('heist_locked1106', 'Not available', 'You need to be 18 and out of prison.', [('Back', home)], 'padlock', 'Your crew')
    page('heist_break1111', 'Enough for this year', 'Your crew needs a break. Come back next year.', [('Back', home)], 'calendar', 'Your crew')
    page('heist_period1106', 'Not in this era', 'That job is not available yet. Pick a job from your time.', [('Jobs', scene('heist_jobs1106'))], 'calendar', 'Your crew')
    page('heist_no_crew1106', 'Join a crew first', 'Mara has a place open. Speak to the crew before choosing a job.', [('Meet the crew', scene('heist_crew1106')), ('Back', home)], 'handshake', 'Your crew')
    page('heist_already1106', 'You are in', 'The crew already knows you. Train or choose a job.', [('Your crew', scene('heist_crew1106')), ('Jobs', scene('heist_jobs1106'))], 'handshake', 'Your crew')
    page('heist_wait1106', 'Job finished this year', p('HeistLast1106'), [('Job history', scene('heist_record1106')), ('Your crew', scene('heist_crew1106'))], 'suitcase', 'Your crew')
    member = [(f'({p("HeistCrew1106")} != 1)', scene('heist_no_crew1106'))]
    join = heist_out('heist_join1106', 'Mara welcomes you', 'Mara gives you a place in the crew. Luca wants to know if you can be trusted.',
        [set_('HeistCrew1106', 1)], checks=[(f'({p("HeistCrew1106")} == 1)', scene('heist_already1106'))])
    train = heist_out('heist_train1106', 'The crew finds its rhythm', 'You practise together. Mara trusts you more and your team skill rises.',
        [inc('HeistSkill1106', 8), inc('HeistTrust1106', 5)], checks=member, quota=('HeistPractice1106', 3))
    page('heist_crew1106', 'Your crew', 'Mara is careful. Ellis takes risks. Luca values loyalty.', [
        ('Join', join), ('Train together', train), ('Crew dispute', heist(scene('heist_dispute1111'), member)),
        ('Leave or go back', scene('heist_leave1106'))], 'handshake', 'Your crew',
         [('Trust', p('HeistTrust1106')), ('Skill', p('HeistSkill1106')), ('Police attention', p('HeistHeat1106'))])
    page('heist_dispute1111', 'Ellis wants more', 'Ellis says the others are holding him back. Luca looks ready to leave.', [
        ('Hear both sides', heist_out('heist_dispute1106', 'Luca stays', 'You let everyone speak. Ellis accepts a compromise and the crew settles down.',
             [inc('HeistTrust1106', 6), inc('HeistHeat1106', -3)], checks=member, quota=('HeistDiscussion1106', 2))),
        ('Back Ellis', heist_out('heist_back_ellis1111', 'Luca feels pushed out', 'Ellis smiles but Luca walks away from the talk. The crew trusts you less.',
             [inc('HeistTrust1106', -8)], checks=member, quota=('HeistDiscussion1106', 2))),
        ('Back', home)], 'handshake', 'Your crew')
    exit_checks = member + [(f'({p("HeistPayout1111")} == 1)', scene('heist_split1106'))]
    page('heist_leave1106', 'Leave the crew?', 'Leaving ends an unfinished job. The preparation fee is not returned.', [
        ('Leave', heist_out('heist_exit1106', 'You leave the crew', 'Mara accepts your choice. Ellis says the next job will go ahead without you.',
             [set_('HeistCrew1106', 0), set_('HeistStage1106', 0), set_('HeistLoot1106', 0), set_('HeistPayout1111', 0)], checks=exit_checks)),
        ('Back', home)], 'door', 'Your crew')
    resume = logic([(f'({p("HeistPayout1111")} == 1)', scene('heist_split1106'))] + [
        (f'({p("HeistStage1106")} == {stage}) && ({p("HeistAge1106")} == <hero:age>)', scene('heist_round1106_' + str(stage)) if stage < 4 else scene('heist_finish1106'))
        for stage in range(1, 5)
    ] + [(f'({p("HeistStage1106")} > 0)', scene('heist_expired1111'))], scene('heist_no_job1111'))
    page('heist_current1111', 'Current job', 'Resume your decisions or check the result.', [('Resume', heist(resume, member)), ('Back', home)], 'suitcase', 'Your crew')
    page('heist_no_job1111', 'No job in progress', 'Choose a job first. The crew will keep your progress until the year ends.', [('Choose a job', scene('heist_jobs1106')), ('Back', home)], 'suitcase', 'Your crew')
    page('heist_expired1111', 'The job fell through', 'Too much time passed. The preparation fee is gone.', [
        ('Close the old job', heist_out('heist_expire1111', 'Old job closed', 'You close the unfinished job. The crew is ready to discuss another one.',
            [set_('HeistStage1106', 0), set_('HeistLoot1106', 0), set_('HeistPayout1111', 0),
             text('HeistLast1106', 'An unfinished job expired. The preparation fee was lost.')],
            checks=[(f'({p("HeistAge1106")} == <hero:age>) || ({p("HeistStage1106")} == 0)', scene('heist_current1111'))])),
        ('Back', home)], 'calendar', 'Your crew')
    page('heist_jobs1106', 'Crew jobs', 'One job each year. Every job has three decisions.', [
        ('Depot', scene('heist_offer1106_1')), ('Gallery', scene('heist_offer1106_2')),
        ('Armoured delivery', scene('heist_offer1106_3')), ('Current job', scene('heist_current1111'))], 'suitcase', 'Your crew')
    for job, title, year, cost, loot in [(1, 'Depot job', 1880, 100, 1200), (2, 'Gallery job', 1900, 200, 2600), (3, 'Armoured delivery', 1920, 350, 4500)]:
        checks = member + [(f'({p("HeistPayout1111")} == 1) || ({p("HeistStage1106")} > 0)', scene('heist_current1111')),
                           (f'({p("HeistMissionAge1106")} >= <hero:age>)', scene('heist_wait1106')),
                           (f'({p("Year")} < {year})', scene('heist_period1106')),
                           (f'({p("NativeBank1105")} < {cost})', scene('funds'))]
        start = heist(seq('BP_BANK_BALANCE=-' + str(cost), set_('HeistJob1106', job), set_('HeistStage1106', 1),
                          set_('HeistScore1106', 0), set_('HeistLoot1106', loot), set_('HeistPayout1111', 0),
                          set_('HeistAge1106', '<hero:age>'), text('HeistLast1106', title + ' in progress.'), scene('heist_round1106_1')), checks)
        page('heist_offer1106_' + str(job), title, 'Preparation costs $' + str(cost) + '. A completed job has a $' + str(loot) + ' pot to split. You could be sent to prison.',
             [('Take the job', start), ('Back', scene('heist_jobs1106'))], 'suitcase', 'Your crew')
    stages = [
        ('The briefing', 'Ellis wants to skip the meeting. Luca is unsure of his role.',
         'Hear everyone out', 'Luca feels ready', 'You hear each person out. Luca relaxes and Mara backs your plan.',
         'Rush the meeting', 'The crew feels rushed', 'Ellis likes your pace. Luca leaves with doubts and the crew draws attention.'),
        ('A member freezes', 'The job is under way but Luca wants to stop.',
         'Check on Luca', 'Luca regains focus', 'You give Luca time to speak. He decides to stay and the crew works together.',
         'Dismiss his doubts', 'Trust breaks down', 'Luca goes quiet. Ellis pushes ahead and the job attracts more attention.'),
        ('A close call', 'The crew is tired. Ellis wants to take another risk.',
         'Stick with the crew', 'Everyone stays together', 'Mara backs your decision. You finish the last stage as a team.',
         'Back Ellis', 'One risk too many', 'The extra risk upsets Mara. The crew becomes harder to keep together.'),
    ]
    for stage, (title, body, good_label, good_title, good_body, bad_label, bad_title, bad_body) in enumerate(stages, 1):
        valid = member + [(f'({p("HeistStage1106")} != {stage}) || ({p("HeistAge1106")} != <hero:age>)', scene('heist_current1111'))]
        next_ = scene('heist_round1106_' + str(stage + 1)) if stage < 3 else scene('heist_finish1106')
        good = heist_out('heist_calm1106_' + str(stage), good_title, good_body,
            [set_('HeistStage1106', stage + 1), inc('HeistScore1106'), inc('HeistTrust1106', 2)], back=next_, checks=valid)
        bad = heist_out('heist_rush1106_' + str(stage), bad_title, bad_body,
            [set_('HeistStage1106', stage + 1), inc('HeistHeat1106', 8), inc('HeistTrust1106', -5)], back=next_, checks=valid)
        abort = heist_out('heist_abort1106_' + str(stage), 'You call it off',
            'The crew leaves the job. The fee is lost but nobody is arrested.',
            [set_('HeistStage1106', 0), set_('HeistLoot1106', 0), set_('HeistPayout1111', 0),
             set_('HeistMissionAge1106', '<hero:age>'), text('HeistLast1106', 'The job was called off. No payout.')], checks=valid)
        page('heist_round1106_' + str(stage), title, body, [(good_label, good), (bad_label, bad), ('Call it off', abort), ('Pause', home)], 'suitcase', 'Your crew')
    finish_checks = member + [(f'({p("HeistStage1106")} != 4) || ({p("HeistAge1106")} != <hero:age>) || ({p("HeistMissionAge1106")} >= <hero:age>)', scene('heist_current1111'))]
    success = seq(set_('HeistStage1106', 0), set_('HeistPayout1111', 1), set_('HeistMissionAge1106', '<hero:age>'),
                  inc('HeistJobs1106'), text('HeistLast1106', 'The crew finished the job. The pot is ready to split.'), scene('heist_split1106'))
    failure = seq(set_('HeistStage1106', 0), set_('HeistPayout1111', 0), set_('HeistLoot1106', 0),
                  set_('HeistMissionAge1106', '<hero:age>'), inc('HeistFailed1111'), inc('HeistHeat1106', 20),
                  text('HeistLast1106', 'The job failed. Police caught you and no loot was paid.'),
                  text('JournalMessage', 'The crew job failed. Police caught me after the job.'), inc('JournalSequence'), scene('heist_arrest1106'))
    page('heist_finish1106', 'The job ends', 'Your choices and crew skill decide the result.', [
        ('See the result', heist(logic([(f'({p("HeistScore1106")} >= 2) && ({p("HeistTrust1106")} >= 35) && ({p("HeistSkill1106")} + {p("Roll")} > {p("HeistHeat1106")})', success)], failure), finish_checks)),
        ('Pause', home)], 'suitcase', 'Your crew')
    payout_checks = member + [(f'({p("HeistPayout1111")} != 1) || ({p("HeistStage1106")} != 0) || ({p("HeistLoot1106")} <= 0) || ({p("HeistMissionAge1106")} != {p("HeistAge1106")})', scene('heist_record1106'))]
    shares = []
    for key, percent, trust, title, body in [
        ('fair', 25, 12, 'An equal share', 'Mara thanks you for sharing fairly. Your share is in the bank and the crew trusts you more.'),
        ('greedy', 50, -25, 'Luca challenges you', 'You take half the pot. Luca says you broke the deal. Your bank grows but crew trust falls.'),
    ]:
        value = fun('div', fun('mul', p('HeistLoot1106'), percent), 100)
        shares.append(('Take ' + str(percent) + '%', heist_out('heist_split_' + key + '1106', title, body,
            ['BP_BANK_BALANCE=' + value, inc('HeistTrust1106', trust), inc('HeistHeat1106', 5),
             text('HeistLast1106', body), set_('HeistLoot1106', 0), set_('HeistPayout1111', 0)], checks=payout_checks, icon='money-bag')))
    page('heist_split1106', 'Split the pot', 'The job is complete. Choose your share.', shares, 'money-bag', 'Your crew', [('Pot', p('HeistLoot1106'))])
    # Preserve the real sentencing route and exact payload; only shorten text.
    arrest = a.edit('heist_arrest1106')
    arrest.update(Title='Caught after the job', Body='Police caught you. You have a three-year sentence. Continue to prison.', ExteriorTitle='The police', EmojiString=glyph('police-car'))
    owned.add(arrest['ScenarioID'])
    page('heist_record1106', 'Job history', p('HeistLast1106'), [('Jobs', scene('heist_jobs1106')), ('Back', home)], 'memo', 'Your crew',
         [('Jobs completed', p('HeistJobs1106')), ('Jobs failed', p('HeistFailed1111')), ('Trust', p('HeistTrust1106')), ('Police attention', p('HeistHeat1106'))])

    # PRISON: 610 selects a real current inmate, binds their identity, records
    # their own response and enforces the native support cap.  It also journals
    # the conversation, so do not add another made-up friendship or journal.
    prison_home = menu('genesis_v18_prison40')
    prison_check = [(f'({p("NativeInPrison1105")} != 1)', scene('prison_closed1105'))]

    def prison_out(key, title, body, changes=(), native=0, back=prison_home, quota=('PrisonProgramme1110', 4), checks=()):
        return outcome(key, title, body, back, changes, native, prison_check + list(checks), quota, context='Prison life')

    page('prison_break1111', 'No session left', 'Your progress is saved. There are more sessions next year.', [('Prison day', scene('prison_programmes1110')), ('Back', prison_home)], 'calendar', 'Prison life')
    support = logic(prison_check, seq(set_('NativeAction', 610), scene('prison_support1110_result')))
    page('prison_support1110_result', p('PeerName1110'), p('PeerReport1110'), [
        ('Give them space', scene('prison_space1111')), ('Prison day', scene('prison_programmes1110')), ('Back', prison_home)], 'handshake', 'Prison life')
    page('prison_space1111', 'You give them space', 'You let them return to their day. They can speak to you when they are ready.',
         [('Prison day', scene('prison_programmes1110')), ('Back', prison_home)], 'handshake', 'Prison life')
    page('prison_programmes1110', 'Prison day', 'Choose what to do today.', [
        ('Check on an inmate', support), ('Learning', scene('prison_learning1110')),
        ('Visits and disputes', scene('prison_connections1110')), ('Back', prison_home)], 'books', 'Prison life',
         [('Course sessions', p('PrisonCourse1110')), ('Support this year', p('PeerSupportCount1110')), ('Conduct reports', p('PrisonDiscipline1105'))])
    for name in ['genesis_activities_v8', 'genesis_v8_inmate_support']:
        rows = list(csv.DictReader(io.StringIO(a.assets.get(name, base[name]))))
        for row in rows:
            if row['ScenarioID'] == 'scenario.activitiesV8.inmateSupport':
                row.update(Title=p('PeerName1110'), Body=p('PeerReport1110'), ExteriorTitle='Prison life',
                           Choice1_Text='Back to prison', Choice1_RouteTo=prison_home, Choice1_AdvancedLogic='')
        a.assets[name] = csv_text(rows)
    page('prison_learning1110', 'Learning', 'A quiet session can help you settle. Your course does not shorten your sentence.', [
        ('Read with the group', prison_out('prison_library1110', 'A good discussion',
            'You discuss a book with the group. Your smarts improve and staff note your calm conduct.',
            [inc('PrisonLibrary1110'), inc('PrisonRespect1105', 2)], 616, back=scene('prison_learning1110'))),
        ('Classroom', scene('prison_classroom1111')), ('My progress', scene('prison_learning_record1110')),
        ('Back', scene('prison_programmes1110'))], 'books', 'Prison life')
    correct = prison_out('prison_course1110', 'The tutor smiles',
        'You get the answer right and finish the worksheet. Your course advances and your good conduct is recorded.',
        [inc('PrisonCourse1110'), inc('PrisonDiscipline1105', -1)], 617, back=scene('prison_learning1110'))
    retry = prison_out('prison_course_retry1111', 'The tutor helps',
        'The tutor divides the problem into small steps. You understand the answer but need more practice.',
        [inc('PrisonLibrary1110')], back=scene('prison_learning1110'))
    page('prison_classroom1111', 'A short lesson', 'The tutor asks: 20 books go into four equal piles. How many books go in each pile?',
         [('5', correct), ('4', retry), ('6', retry), ('Back', scene('prison_learning1110'))], 'books', 'Prison life')
    page('prison_learning_record1110', 'My progress', 'Staff can see your course work and conduct. Release still follows your sentence and parole rules.',
         [('Back', scene('prison_learning1110'))], 'memo', 'Prison life',
         [('Course sessions', p('PrisonCourse1110')), ('Library sessions', p('PrisonLibrary1110')), ('Respect', p('PrisonRespect1105'))])
    page('prison_connections1110', 'Visits and disputes', 'Keep in touch or ask for help with a dispute.', [
        ('Family visit', prison_out('prison_family_visit1110', 'A visit from home',
            'Your family talks about life outside. The visit keeps your family bonds strong.',
            [inc('PrisonVisits1105')], 122, quota=('PrisonVisit1110', 2))),
        ('Ask staff to mediate', prison_out('prison_mediate1110', 'The dispute cools',
            'An officer hears both sides. The rivalry eases and staff note your good conduct.',
            [inc('PrisonMediation1110'), inc('PrisonRival1105', -10)], 618, quota=('PrisonMediate1110', 2))),
        ('Rivals and crew', scene('prison_combat1105')), ('Back', scene('prison_programmes1110'))], 'handshake', 'Prison life')
    # Annual entries inherit the same short choices and guarded native effects.
    annual = [('A classroom place', 'The tutor has room for one more learner.', 'Try the lesson', scene('prison_classroom1111')),
              ('A letter from home', 'Your family asks how you are coping.', 'Write back', prison_out('prison_annual_result1110_2', 'A letter sent', 'You write about your day and ask about home. Your family bonds grow stronger.', [inc('PrisonVisits1105')], 122, quota=('PrisonAnnual1110', 1))),
              ('An argument', 'Two inmates are arguing by the tables.', 'Ask staff to help', prison_out('prison_annual_result1110_3', 'The shouting stops', 'An officer separates them. Staff note your calm response.', [inc('PrisonMediation1110'), inc('PrisonRival1105', -5)], 618, quota=('PrisonAnnual1110', 1))),
              ('The library cart', 'A book you wanted is finally here.', 'Borrow it', prison_out('prison_annual_result1110_4', 'A quiet afternoon', 'You enjoy the book. Your smarts and conduct improve.', [inc('PrisonLibrary1110')], 616, quota=('PrisonAnnual1110', 1)))]
    for number, (title, body, label, destination) in enumerate(annual, 1):
        page('prison_annual1110_' + str(number), title, body, [(label, logic(prison_check, destination)), ('Keep my routine', '')], 'books', 'Prison life')

    # RESEARCH: choose a plan -> react to changing conditions -> deliver a real
    # report.  Current contract/year guards prevent stale or cross-role pay.
    a.prop('FieldSurveyAge1111', -1, -1, 999)
    a.prop('FieldSurveyRole1111', 0, 0, 3)
    a.prop('FieldSurveyStage1111', 0, 0, 2)
    a.prop('FieldSurveyPlan1111', 0, 0, 3)
    page('field_break1111', 'Training done for now', 'Your progress is saved. Return next year for more training.', [('Back', '')], 'calendar', 'Field research')
    page('field_prison1111', 'Not while in prison', 'Field work takes place outside prison. Return after your release.', [('Back', '')], 'padlock', 'Field research')
    data = [
        (1, 'storm', 'Storm observer', 'genesis_v18_storm_career19', 'cloud-thunder',
         'A storm is changing course. Your team needs useful readings from a safe site.',
         'The storm turns towards your observation area.', 'Move to the marked shelter', 'The team reaches shelter. Your earlier readings are safe.',
         'A storm report is accepted. Your readings help the local warning team.'),
        (2, 'tsunami', 'Tsunami scientist', 'genesis_v18_tsunami_career21', 'earth',
         'An offshore quake has triggered a warning. Work from the safe area.',
         'A new alert closes the coast. The team is still at the safe site.', 'Stay in the safe area', 'You stay clear of the closed coast. The remote readings are saved.',
         'A tsunami report is accepted. Your readings help the coastal warning team.'),
        (3, 'volcano', 'Volcano observer', 'genesis_v18_volcano_career21', 'fire',
         'Tremors are rising. Your observatory needs a safe set of readings.',
         'The observatory raises the alert. Access to the field site is closed.', 'Return to the observatory', 'Everyone returns safely. The remote sensors keep the useful readings.',
         'A volcano report is accepted. Your readings help the observatory.'),
    ]
    for role, key, title, list_id, art, intro, change, safe_label, safe_body, paid_body in data:
        field_home = menu(list_id)
        checks = [('(<hero:age> < 18)', scene('adult')),
                  (f'({p("NativeInPrison1105")} == 1)', scene('field_prison1111')),
                  (f'({p("FieldRole")} != {role})', scene(key + '_join'))]
        contract_guard = [('(<hero:age> < 18)', scene('adult')),
                          (f'({p("NativeInPrison1105")} == 1)', scene('field_prison1111')),
                          (f'({p("FieldReportReady")} == 1) && ({p("FieldMissionAge")} == <hero:age>)', scene(key + '_pending1111')),
                          (f'({p("FieldSurveyStage1111")} == 1) && ({p("FieldSurveyAge1111")} == <hero:age>)', scene(key + '_active1111'))]
        join = outcome(key + '_contract1111', 'Contract accepted', 'The research office adds you to the team. Start with training or plan a field survey.', field_home,
                       [set_('FieldRole', role), text('FieldTitle', title)], checks=contract_guard, context='Field research', icon=art)
        page(key + '_join', title, 'Take a research contract. A completed report pays $250.', [('Take the contract', join), ('Back', field_home)], art, 'Field research')
        current_report = logic([(f'({p("FieldRole")} == {n})', scene(k + '_record')) for n, k in [(1, 'storm'), (2, 'tsunami'), (3, 'volcano')]], field_home)
        current_survey = logic([(f'({p("FieldRole")} == {n})', scene(k + '_survey')) for n, k in [(1, 'storm'), (2, 'tsunami'), (3, 'volcano')]], field_home)
        page(key + '_pending1111', 'Deliver your report first', 'You have a report waiting with your current research team. Finish it before changing contracts.', [('Current team', current_report), ('Back', field_home)], art, 'Field research')
        page(key + '_active1111', 'A survey is in progress', 'Return to your current research team to finish or end the survey.', [('Current survey', current_survey), ('Back', field_home)], art, 'Field research')
        train = outcome(key + '_train', 'Training pays off', 'You learn the instruments and practise a safe field plan. Your skill and safety improve.', field_home,
                        [inc('FieldSkill', 9), inc('FieldSafety', 8)], checks=checks,
                        quota=('FieldTraining', 5), context='Field research', icon=art)
        page(key + '_train', 'Field training', 'Learn the instruments before a survey.', [('Train', train), ('Back', field_home)], art, 'Field research',
             [('Skill', p('FieldSkill')), ('Safety', p('FieldSafety'))])
        resume_checks = [(f'({p("FieldSurveyStage1111")} == 1) && ({p("FieldSurveyAge1111")} == <hero:age>) && ({p("FieldSurveyRole1111")} == {role})', scene(key + '_conditions1111')),
                         (f'({p("FieldMissionAge")} >= <hero:age>)', scene(key + '_record'))]
        plans = []
        for plan, label in [(1, 'Use the safe site'), (2, 'Use remote instruments')]:
            extra = [(f'({p("FieldSkill")} < 35)', scene(key + '_need_training1111'))] if plan == 2 else []
            start = logic(checks + resume_checks + extra,
                          seq(set_('FieldSurveyAge1111', '<hero:age>'), set_('FieldSurveyRole1111', role), set_('FieldSurveyStage1111', 1),
                              set_('FieldSurveyPlan1111', plan), set_('FieldReportReady', 0), scene(key + '_conditions1111')))
            plans.append((label, start))
        abort_checks = checks + [(f'({p("FieldMissionAge")} >= <hero:age>)', scene(key + '_record'))]
        unsafe = outcome(key + '_survey3', 'The survey is stopped',
            'You ignore the closed area. The team pulls you out. You are hurt and lose equipment. There is no report to sell.', field_home,
            [set_('FieldSurveyStage1111', 2), set_('FieldMissionAge', '<hero:age>'), set_('FieldReportReady', 0), inc('FieldSafety', -15),
             inc('FieldTrust', -8), inc('FieldInjuries'), inc('FieldBudget', -60), text('FieldReport', 'The survey was stopped after an unsafe decision.')],
            native=14, checks=abort_checks, context='Field research', icon=art)
        page(key + '_survey', 'Field survey', intro, plans + [('Ignore the closed area', unsafe), ('Back', field_home)], art, 'Field research')
        page(key + '_need_training1111', 'More training needed', 'You need skill 35 for remote instruments. Training improves your skill.', [('Training', scene(key + '_train')), ('Back', field_home)], 'books', 'Field research')
        valid = checks + [(f'({p("FieldSurveyAge1111")} != <hero:age>) || ({p("FieldSurveyRole1111")} != {role}) || ({p("FieldSurveyStage1111")} != 1)', scene(key + '_survey')),
                          (f'({p("FieldMissionAge")} >= <hero:age>)', scene(key + '_record'))]
        complete_effects = [set_('FieldSurveyStage1111', 2), set_('FieldMissionAge', '<hero:age>'), inc('FieldVisits')]
        safe = outcome(key + '_survey1', 'Readings saved', safe_body + ' A report is ready to deliver.', scene(key + '_record'),
            complete_effects + [set_('FieldReportReady', 1), inc('FieldData', 14), inc('FieldSafety', 5), inc('FieldTrust', 4), text('FieldReport', safe_body)],
            checks=valid, context='Field research', icon=art)
        remote = outcome(key + '_survey2', 'Remote data saved', 'You keep the team in the safe area. The remote instruments return a full set of readings. Your report is ready.', scene(key + '_record'),
            complete_effects + [set_('FieldReportReady', 1), inc('FieldData', 24), inc('FieldSafety', 2), inc('FieldTrust', 6), text('FieldReport', 'Remote instruments returned a full set of readings.')],
            checks=valid + [(f'({p("FieldSurveyPlan1111")} != 2)', scene(key + '_conditions1111'))], context='Field research', icon=art)
        retreat = outcome(key + '_retreat1111', 'Everyone gets home', 'You end the survey before anyone is hurt. The office accepts your decision. No report fee is due.', field_home,
            complete_effects + [set_('FieldReportReady', 0), inc('FieldSafety', 8), text('FieldReport', 'The team ended the survey safely. No report was sold.')],
            checks=valid, context='Field research', icon=art)
        page(key + '_conditions1111', 'Conditions change', change, [
            (safe_label, logic([(f'({p("FieldSurveyPlan1111")} == 2)', remote)], safe)),
            ('End the survey', retreat), ('Pause', field_home)], art, 'Field research')
        delivery_checks = checks + [(f'({p("FieldMissionAge")} != <hero:age>) || ({p("FieldReportReady")} != 1) || ({p("FieldPaidAge")} >= <hero:age>)', scene(key + '_report_wait1106'))]
        deliver = outcome(key + '_deliver1111', 'Report accepted', paid_body + ' $250 is paid into your bank.', field_home,
            ['BP_BANK_BALANCE=250', set_('FieldPaidAge', '<hero:age>'), set_('FieldReportReady', 0), inc('FieldTrust', 3)],
            checks=delivery_checks, context='Field research', icon=art)
        page(key + '_record', title, p('FieldReport'), [('Deliver report', deliver), ('Field survey', scene(key + '_survey')), ('Back', field_home)], art, 'Field research',
             [('Skill', p('FieldSkill')), ('Safety', p('FieldSafety')), ('Readings', p('FieldData')), ('Trust', p('FieldTrust'))])
        page(key + '_report_wait1106', 'No report to deliver', 'Finish a survey this year first. A report can be paid once each year.', [('Field survey', scene(key + '_survey')), ('Back', field_home)], art, 'Field research')
        page(key + '_paid', 'Report accepted', 'Your $250 payment is recorded. Plan another survey next year.', [('Back', field_home)], 'money-bag', 'Field research')
        replace_list(list_id, title, [('Contract', scene(key + '_join'), 'suitcase', 'Join the research team'),
                                    ('Training', scene(key + '_train'), 'books', 'Learn the instruments'),
                                    ('Field survey', scene(key + '_survey'), art, 'React to changing conditions'),
                                    ('Reports', scene(key + '_record'), 'memo', 'Deliver this year’s report')])

    # Specific titles for preserved legacy outcomes.  Preserve their original
    # native effect routes and caps; these are still valid saved links.
    old_titles = {'prison_visit1105_result': 'A visit from home', 'prison_train1105_result': 'Training complete',
                  'prison_rest1105_result': 'Care and rest', 'prison_peace1105_result': 'A quiet day',
                  'prison_contraband1105_result': 'A risky deal', 'prison_setup1105_result': 'The guard set you up',
                  'prison_refuse1105_result': 'You refuse the offer', 'prison_recruit1105_result': 'A new crew member',
                  'prison_promote1105_result': 'A crew member steps up', 'prison_settle1105_result': 'The argument settles',
                  'prison_group1105_result': 'Staff break up the fight', 'prison_withdraw1105_result': 'You step away',
                  'prison_win1105_result': 'You win the fight', 'prison_lose1105_result': 'You are hurt'}
    for key, title in old_titles.items():
        row = a.edit(key)
        row.update(Title=title, ExteriorTitle='Prison life')
        owned.add(row['ScenarioID'])
    refresh_annual_copies(a, base)
    return sorted(a.assets)
