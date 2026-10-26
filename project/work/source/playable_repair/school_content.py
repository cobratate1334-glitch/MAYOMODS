"""Playable school choices in the existing Genesis school list.

The original school, classmate and combat objects remain authoritative.  This
overlay owns sessions and story progress, never stock team membership.  Native
commands 10/11/12/112/611/612/614 apply the original grade, relationship,
popularity and health changes; SchoolNativeFight1106 opens the original fight.
"""
import copy
import csv
import io
import json

from life_rework.content import p, scene, menu, set_, inc, text, seq, fun, csv_text

HOME = menu('genesis_v18_school52')
ART = 'native1111/school/'
MANUAL_FILTER = '[gfc.life_rework.AnnualContinuation1106=1]'


def logic(cases, target):
    """Flatten ordered first-match branches without exponential negations.

    Genesis stops at its first matching case.  A nested branch's fallback is
    guarded by its ancestor and comes before the next sibling.  Repeating every
    preceding condition as ``== false`` is unnecessary and makes the resumed
    six-form exam overflow the engine's row/field budget.
    """
    leaves = []

    def walk(route, ancestors):
        if isinstance(route, str):
            leaves.append((ancestors, route))
            return
        for case in route['cases']:
            walk(case['then']['route_options'][0]['route_to'], ancestors + [case['if']['expression']])
        walk(route['else_when_no_matches']['route_options'][0]['route_to'], ancestors)

    tree = {'cases': [{'if': {'expression': condition}, 'then': {'route_options': [{'route_to': route}]}}
                      for condition, route in cases],
            'else_when_no_matches': {'route_options': [{'route_to': target}]}}
    walk(tree, [])
    return {'cases': [{'if': {'expression': ' && '.join('(' + c + ')' for c in conditions)},
                       'then': {'route_options': [{'route_to': route}]}} for conditions, route in leaves[:-1]],
            'else_when_no_matches': {'route_options': [{'route_to': leaves[-1][1]}]}}


def icon(number):
    return ART + '01_school_menu_icons_' + str(number).zfill(2)


def picture(number):
    return ART + '02_school_events_' + str(number).zfill(2)


def activity(number):
    return ART + '03_cheer_sports_clubs_' + str(number).zfill(2)


def refresh_annual_copies(a, base):
    """Refresh manual school continuations in each original CSV controller.

    Annual controllers have their own Scenario dictionaries.  Updating only the
    main sheet leaves old choices live after an annual event.  Preserve selector
    metadata on annual entries and replace the manual school copies verbatim.
    Call again after other content modules if they regenerate annual sheets.
    """
    current = {row['ScenarioID']: row for row in a.rows}
    owned = getattr(a, 'playable_school_ids', set())
    for name, value in sorted({**base, **a.assets}.items()):
        if not value.startswith('ScenarioID,') or name == 'genesis_life_rework':
            continue
        rows = list(csv.DictReader(io.StringIO(value)))
        touched = False
        existing = set()
        for index, old in enumerate(rows):
            key = old['ScenarioID']
            existing.add(key)
            source = current.get(key) if key in owned else None
            if key.startswith(scene('annual_school1110_')):
                source = current.get(key.replace('annual_school1110_', 'school_story1110_'))
            if not source:
                continue
            fresh = copy.deepcopy(source)
            # These values control random annual selection, not presentation.
            for column in ['ScenarioID', 'Filter', 'IsAgeUpScenario', 'HasDismissButton', 'HeroAge', 'DrawFilter']:
                fresh[column] = old.get(column, '')
            if old.get('IsAgeUpScenario', '').lower() != 'true':
                fresh.update(Filter=MANUAL_FILTER, IsAgeUpScenario='false')
            rows[index] = fresh
            touched = True
        if touched and ('annual' in name or any(r.get('IsAgeUpScenario', '').lower() == 'true' for r in rows)):
            for key in sorted(owned - existing):
                rows.append(dict(copy.deepcopy(current[key]), Filter=MANUAL_FILTER, IsAgeUpScenario='false'))
        if touched:
            a.assets[name] = csv_text(rows)


def build(a, base):
    """Overlay exact 1110 Author state; return modified asset names.

    Root must refresh the live native pupil/peer fields before school entry and
    annual selection.  Native story 4 needs age >= 10; story 10 requires age >=
    12 and current-year practice.  Every authored choice repeats these checks.
    """
    owned = set()
    a.playable_school_ids = owned
    for key, initial, maximum in [
        ('ExamStartedAge1111', -1, 999), ('SchoolBullyAge1111', -1, 999),
        ('SchoolProjectAge1111', -1, 999), ('SchoolProjectStep1111', 0, 3),
        ('SchoolProjectPoints1111', 0, 3), ('SchoolCheerAge1111', -1, 999),
        ('SchoolCheerDoneAge1111', -1, 999), ('SchoolCheerStep1111', 0, 3),
        ('SchoolCheerPoints1111', 0, 3), ('SchoolPracticeAge1111', -1, 999),
        ('SchoolMatchAge1111', -1, 999), ('SchoolMatchStep1111', 0, 3),
        ('SchoolMatchPoints1111', 0, 3), ('SchoolMatchDoneAge1111', -1, 999),
    ]:
        a.prop(key, initial, -1 if initial < 0 else 0, maximum)

    def page(key, title, body, choices, glyph=24, image=None, stats=None):
        ident = scene(key)
        # Keep old IDs without appending a second definition of the same page.
        a.rows[:] = [r for r in a.rows if r['ScenarioID'] != ident]
        a.page(key, title, body, choices, icon(glyph), stats)
        row = a.rows[-1]
        row.update(ExteriorTitle='School life', BigImageString=image or '')
        owned.add(ident)
        return ident

    closed = (f'({p("SchoolEligible")} != 1) || (<hero:age> < 5)', scene('school_closed'))
    suspended = (f'({p("SchoolSuspendedAge1110")} >= <hero:age>)', scene('school_suspended1110'))

    def guard(target, extra=(), on_campus=True):
        return logic([closed] + ([suspended] if on_campus else []) + list(extra), target)

    def receipt(key, title, body, effects=(), native=0, back=HOME, glyph=8,
                image=None, extra=(), quota=('SchoolSession1111', 12), on_campus=True):
        a.rows[:] = [r for r in a.rows if r['ScenarioID'] != scene(key + '_result')]
        route = a.outcome(key, body, back, list(effects), native=native,
                          extra=(closed,) + ((suspended,) if on_campus else ()) + tuple(extra), quota=quota)
        row = a.edit(key + '_result')
        row.update(Title=title, ExteriorTitle='School life', EmojiString=icon(glyph), BigImageString=image or '')
        owned.add(row['ScenarioID'])
        # The inherited outcome helper assumes a first-person fragment. These
        # school responses are complete sentences with 'You' or a peer's name.
        # Keep their grammar intact in both literal and guarded route leaves.
        before = text('JournalMessage', 'I ' + body[0].lower() + body[1:])
        after = text('JournalMessage', 'At school. ' + body)
        def clean(value):
            if isinstance(value, str):
                return value.replace(before, after)
            if isinstance(value, list):
                return [clean(item) for item in value]
            if isinstance(value, dict):
                return {key: clean(item) for key, item in value.items()}
            return value
        return clean(route)

    def journal(message, *effects):
        return seq(*effects, text('JournalMessage', message), inc('JournalSequence'))

    page('school_closed', 'Not in school', 'Join a school to use School life.', [('Back', '')])
    page('school_session_full1111', 'School day over', 'Your work is saved. There is more to do next year.', [('My year', scene('school_record')), ('Back', HOME)], 8)
    # Use a school-specific cap receipt; other systems keep their own limits.
    page('school_suspended1110', 'Suspended', 'You cannot attend activities this year. Meet the head or study at home.', [
        ('Meet the head', receipt('school_return1111', 'A return plan',
            'The head agrees to a fresh start next year. This year’s suspension stays.',
            [inc('SchoolDiscipline1110', -2), inc('SchoolTrust', 8)],
            quota=('SchoolReturn1111', 1), on_campus=False, glyph=23, image=picture(11))),
        ('Study at home', scene('school_study')), ('Back', HOME)], 23, picture(12))

    # Six useful doors.  Old tile IDs survive in their original relative order.
    original = json.loads(base['genesis_v18_school52'])
    collection = 'Items' if 'Items' in original else 'ListItems'
    old_tiles = original[collection]
    entries = [
        ('Exams', scene('school_study'), 1, 'Study and take a test'),
        ('Bullying', scene('school_bully_entry'), 3, 'Get help or face the bully'),
        ('Classmates', scene('school_peer1105'), 7, 'Friends and group work'),
        ('Clubs', scene('school_clubs1105'), 11, 'Art drama music and chess'),
        ('School sports', scene('school_sports1110'), 17, 'Practice and cheer trials'),
        ('My year', scene('school_record'), 8, 'Results and conduct'),
    ]
    original[collection] = []
    for n, (label, destination, art, detail) in enumerate(entries):
        tile = a.tile(label, destination, icon(art), detail)
        if n < len(old_tiles):
            tile['TileID'] = old_tiles[n]['TileID']
        original[collection].append(tile)
    a.assets['genesis_v18_school52'] = json.dumps(original, indent=2)
    # Legacy nested entrance now leads to the same hub without a recursive tile.
    page('school_life1110', 'School life', 'Choose what to do at school.', [
        ('Exams', scene('school_study')), ('Classmates', scene('school_peer1105')),
        ('School sports', scene('school_sports1110')), ('Back', HOME)], 24)
    page('school_record', 'My year', 'Your school progress stays with this life.', [('Back', HOME)], 8, image=activity(12),
         stats=[('Test score', p('SchoolExam')), ('Friends', p('SchoolFriends')),
                ('Safety', p('SchoolSafety')), ('Warnings', p('SchoolDiscipline1110')),
                ('Practice', p('SchoolTeamPractice1110'))])

    # The three-question exam already exists.  Preserve question IDs and age
    # forms while making leave/resume and stale submissions safe.
    page('school_study', 'Exams', 'Study first or take this year’s three-question test.', [
        ('Revise', receipt('school_revise1111', 'Ready for the test',
            'You finish a short revision session. Your grade and preparation improve.',
            [inc('SchoolPrep', 15), inc('SchoolStress', -3)], native=10,
            glyph=9, image=picture(8), on_campus=False)),
        ('Rest', receipt('school_rest1111', 'A clear head',
            'You put your books away and get some sleep. You feel less stressed.',
            [inc('SchoolStress', -12), inc('SchoolPrep', 4)], glyph=2, on_campus=False)),
        ('Take the test', guard(scene('exam_start1105'), on_campus=False)), ('Back', HOME)], 1,
         stats=[('Preparation', p('SchoolPrep')), ('Stress', p('SchoolStress'))])
    forms = []
    for form in range(6):
        keys = ['exam_' + str(step) + ('_form' + str(form) if form else '') + '_1105' for step in range(1, 4)]
        forms.append(keys)
        for step, key in enumerate(keys):
            row = a.edit(key)
            row.update(Title='Question ' + str(step + 1) + ' of 3', EmojiString=icon(1), BigImageString='', ExteriorTitle='Exam')
            row['Choice4_Text'] = 'Pause test'
            row['Choice4_RouteTo'] = scene('exam_pause1111')
            row['Choice4_AdvancedLogic'] = ''
            # Old question routes already check ExamStep; also prevent old-year
            # callbacks from consuming a fresh paper before it has started.
            for index in range(1, 4):
                advanced = row['Choice' + str(index) + '_AdvancedLogic']
                target = json.loads(advanced) if advanced else row['Choice' + str(index) + '_RouteTo']
                row['Choice' + str(index) + '_RouteTo'] = ''
                row['Choice' + str(index) + '_AdvancedLogic'] = json.dumps(guard(target, [
                    (f'({p("ExamStartedAge1111")} != <hero:age>)', scene('exam_start1105')),
                    (f'({p("ExamForm1105")} != {form})', scene('exam_pause1111')),
                ], on_campus=False))
            owned.add(row['ScenarioID'])
    resume = logic([
        (f'({p("ExamForm1105")} == {form}) && ({p("ExamStep1105")} == {step})', scene(keys[step]))
        for form, keys in enumerate(forms) for step in range(3)
    ], scene('exam_mark1105'))
    form_cases = []
    for form, expression in [(0, '(<hero:age> < 12) && (' + p('Roll') + ' < 50)'),
                             (1, '(<hero:age> < 12)'),
                             (2, '(<hero:age> < 18) && (' + p('Roll') + ' < 50)'),
                             (3, '(<hero:age> < 18)'), (4, '(' + p('Roll') + ' < 50)')]:
        form_cases.append((expression, seq(set_('ExamForm1105', form), scene(forms[form][0]))))
    begin = seq(set_('ExamStartedAge1111', '<hero:age>'), set_('ExamStep1105', 0), set_('ExamPoints1105', 0))
    choose_form = logic([(condition, seq(begin, target)) for condition, target in form_cases],
                        seq(begin, set_('ExamForm1105', 5), scene(forms[5][0])))
    start = guard(logic([(f'({p("ExamAge1105")} >= <hero:age>)', scene('exam_done1105')),
                         (f'({p("ExamStartedAge1111")} == <hero:age>)', resume)], choose_form), on_campus=False)
    page('exam_start1105', 'School test', 'Three questions. One result each school year. You can pause and return.',
         [('Start or resume', start), ('Back', scene('school_study'))], 1, picture(7))
    page('exam_pause1111', 'Test paused', 'Your answers are saved.', [('Resume', start), ('Back', HOME)], 2)
    mark_guard = [(f'({p("ExamAge1105")} >= <hero:age>)', scene('exam_done1105')),
                  (f'({p("ExamStep1105")} != 3) || ({p("ExamStartedAge1111")} != <hero:age>)', scene('exam_start1105'))]
    common = [set_('ExamAge1105', '<hero:age>'), set_('SchoolExam', fun('div', fun('mul', p('ExamPoints1105'), 100), 3))]
    passed = receipt('exam_pass1105', 'Test passed', 'You got ' + p('ExamPoints1105') + ' out of 3. Your grade rises.',
                     common + [inc('SchoolExamsPassed'), inc('SchoolStress', -5)], native=11,
                     glyph=8, image=picture(9), extra=mark_guard, quota=None, on_campus=False)
    failed = receipt('exam_fail1105', 'Try again next year', 'You got ' + p('ExamPoints1105') + ' out of 3. Your grade falls. Your teacher helps you plan your study.',
                     common + [inc('SchoolStress', 5)], native=12,
                     glyph=8, image=picture(10), extra=mark_guard, quota=None, on_campus=False)
    page('exam_mark1105', 'Hand in your paper', 'Your answers are ready.', [
        ('Get my result', logic([(f'({p("ExamPoints1105")} >= 2)', passed)], failed)),
        ('Pause', scene('exam_pause1111'))], 1)
    page('exam_done1105', 'Test complete', 'You have one test result this year.', [('My year', scene('school_record')), ('Back', HOME)], 8,
         stats=[('Score', p('SchoolExam'))])
    # The old automatic exam must not offer a second annual grade reward.
    page('school_exam', 'School test', 'Answer three questions for this year’s result.', [('Take the test', start), ('Back', HOME)], 1)
    page('school_exam_done', 'Test complete', 'Your result is saved.', [('My year', scene('school_record')), ('Back', HOME)], 8)

    # Bullying continues after the first click.  The next scene remembers the
    # teacher/friend route, rather than recycling the same result.
    fresh_bully = seq(set_('SchoolBullyAge1111', '<hero:age>'), set_('SchoolBullyStage', 0), scene('school_bully'))
    review = guard(logic([
        (f'({p("SchoolBullyAge1111")} != <hero:age>)', fresh_bully),
        (f'({p("SchoolBullyStage")} == 2)', scene('school_bully_teacher1111')),
        (f'({p("SchoolBullyStage")} == 1)', scene('school_bully_friend1111')),
        (f'({p("SchoolBullyStage")} >= 3)', scene('school_bully_settled1111')),
    ], scene('school_bully')))
    page('school_bully_entry', 'Bullying', 'A pupil has been taking someone’s lunch. Check what happened.', [('Open the case', review), ('Back', HOME)], 3, picture(1))
    report = receipt('school_report1111', 'A teacher steps in',
        'The teacher stops the bullying. They ask you to check in tomorrow.',
        [set_('SchoolBullyAge1111', '<hero:age>'), set_('SchoolBullyStage', 2), inc('SchoolSafety', 10), inc('SchoolTrust', 5)],
        back=scene('school_bully_teacher1111'), glyph=5, image=picture(3), quota=None,
        extra=[(f'({p("SchoolBullyAge1111")} == <hero:age>) && ({p("SchoolBullyStage")} >= 2)', scene('school_bully_entry'))])
    stand = receipt('school_stand1111', 'You stand together',
        'You stay beside the pupil. The bully backs off but glares at you after class.',
        [set_('SchoolBullyAge1111', '<hero:age>'), set_('SchoolBullyStage', 1), inc('SchoolSafety', 5), inc('SchoolFriends', 5)],
        back=scene('school_bully_friend1111'), glyph=4, image=picture(2), quota=None,
        extra=[(f'({p("SchoolBullyAge1111")} == <hero:age>) && ({p("SchoolBullyStage")} != 0)', scene('school_bully_entry'))])
    fight_defend = guard(seq(set_('SchoolFightReason1110', 1), set_('SchoolBullyStage', 3), scene('school_fight1106')))
    page('school_bully', 'Trouble at lunch', 'A pupil grabs someone’s lunch and shoves their bag.', [
        ('Get a teacher', report), ('Stand with them', stand), ('Fight', fight_defend),
        ('Walk away', receipt('school_ignore1111', 'Lunch ends badly',
            'The pupil eats alone. They avoid you after class.',
            [set_('SchoolBullyStage', 4), set_('SchoolBullyAge1111', '<hero:age>'), inc('SchoolFriends', -3), inc('SchoolSafety', -5)],
            glyph=3, image=picture(1), quota=None,
            extra=[(f'({p("SchoolBullyAge1111")} == <hero:age>) && ({p("SchoolBullyStage")} != 0)', scene('school_bully_entry'))]))], 3, picture(1))
    teacher_extra = [(f'({p("SchoolBullyStage")} != 2) || ({p("SchoolBullyAge1111")} != <hero:age>)', scene('school_bully_entry'))]
    page('school_bully_teacher1111', 'The next day', 'The teacher checks in. The bully has stopped taking lunches but keeps staring at you.', [
        ('Tell the whole story', receipt('school_followup1111', 'A safer lunch break',
            'Staff move the seats and watch the lunch area. The bullying stops.',
            [set_('SchoolBullyStage', 4), inc('SchoolSafety', 12), inc('SchoolTrust', 5), inc('SchoolStress', -5)],
            glyph=5, image=picture(3), extra=teacher_extra, quota=None)),
        ('Ask for a calm talk', receipt('school_amends1111', 'A tense apology',
            'With a teacher nearby the bully apologises. You agree to leave each other alone.',
            [set_('SchoolBullyStage', 4), inc('SchoolSafety', 8), inc('SchoolStress', -7)],
            glyph=4, image=picture(5), extra=teacher_extra, quota=None)),
        ('Back', HOME)], 5, picture(3))
    friend_extra = [(f'({p("SchoolBullyStage")} != 1) || ({p("SchoolBullyAge1111")} != <hero:age>)', scene('school_bully_entry'))]
    page('school_bully_friend1111', 'After class', 'The pupil waits by the gate. The bully is nearby.', [
        ('Walk home together', receipt('school_safe_walk1111', 'Nobody walks alone',
            'You leave as a group. The bully stays behind. Other pupils respect your support.',
            [set_('SchoolBullyStage', 4), inc('SchoolSafety', 8), inc('SchoolFriends', 8)], native=614,
            glyph=4, image=picture(2), extra=friend_extra, quota=None)),
        ('Get a teacher', guard(report, friend_extra)),
        ('Face the bully', guard(seq(set_('SchoolFightReason1110', 1), set_('SchoolBullyStage', 3), scene('school_fight1106')), friend_extra)),
        ('Back', HOME)], 4, picture(2))
    page('school_bully_settled1111', 'Case closed for now', 'Your choices are saved. Speak up if the problem returns next year.', [('My year', scene('school_record')), ('Back', HOME)], 4, picture(5))
    # Original attack scene: no imitation damage screen or fake fight choices.
    no_fight = scene('school_no_fight1106')
    fight = guard(set_('SchoolNativeFight1106', 1), [
        (f'({p("SchoolPeerPresent1105")} != 1) || ({p("SchoolCombatAge1106")} >= <hero:age>)', no_fight)])
    page('school_fight1106', 'School fight', 'Things are getting heated. Choose whether to fight or leave.', [
        ('Fight', fight), ('Walk away', receipt('school_walk_away1106', 'You walk away',
            'You leave before anyone is hurt. The teacher helps keep you apart.',
            [inc('SchoolSafety', 5), inc('SchoolStress', -3)], glyph=4, image=picture(5)))], 6, picture(4))
    page('school_no_fight1106', 'No fight started', 'You need a current classmate. You can use this encounter once a year.',
         [('Classmates', scene('school_peer1105')), ('Back', HOME)], 6)

    # One actual classmate snapshot owns all direct relationship changes.
    peer_guard = [(f'({p("SchoolPeerPresent1105")} != 1)', scene('school_no_peer1111'))]
    page('school_no_peer1111', 'No classmate found', 'Visit your class first. A current classmate is needed for this activity.', [('Back', HOME)], 7)
    study_peer = receipt('school_peer_study1111', 'You help each other',
        p('SchoolPeer1105') + ' thanks you for the study session. Your friendship grows.',
        [inc('SchoolPeerTrust1105', 6), inc('SchoolPrep', 10), inc('SchoolFriends', 4)], native=112,
        glyph=7, image=picture(8), extra=peer_guard)
    page('school_peer1105', 'Classmates', p('SchoolPeer1105') + ' is in your class.', [
        ('Study together', study_peer), ('Group project', guard(scene('school_project1105'), peer_guard)),
        ('Lunch break', guard(scene('school_social1110'), peer_guard)), ('Back', HOME)], 7, picture(6))
    page('school_friends', 'Meet a classmate', 'Spend time with someone in your class.', [('Classmates', guard(scene('school_peer1105'), peer_guard)), ('Back', HOME)], 7, picture(6))
    page('school_social1110', 'Lunch break', 'Your class is sharing stories at lunch.', [
        ('Tell a kind joke', receipt('school_joke1110', 'The table laughs',
            'Your classmates laugh with you. More pupils stop to say hello.',
            [inc('SchoolClown1110', 6), inc('SchoolFriends', 4)], native=614, glyph=12, image=picture(6))),
        ('Invite ' + p('SchoolPeer1105'), receipt('school_lunch1111', 'Room at your table',
            p('SchoolPeer1105') + ' sits with you. You find something you both enjoy.',
            [inc('SchoolPeerTrust1105', 7), inc('SchoolFriends', 5)], native=112, glyph=7, image=picture(6), extra=peer_guard)),
        ('Mock a pupil', receipt('school_mock1111', 'That hurt',
            'The pupil leaves the table. Your teacher records a warning and your popularity falls.',
            [inc('SchoolFriends', -5), inc('SchoolDiscipline1110'), inc('SchoolTrust', -5)], native=612,
            glyph=23, image=picture(12))), ('Back', HOME)], 7)

    project_resume = logic([(f'({p("SchoolProjectStep1111")} == 1)', scene('school_project_plan1111')),
                            (f'({p("SchoolProjectStep1111")} == 2)', scene('school_project_present1111'))], scene('school_project_done1111'))
    project_start = guard(logic([(f'({p("SchoolProjectAge1111")} == <hero:age>)', project_resume)],
        seq(set_('SchoolProjectAge1111', '<hero:age>'), set_('SchoolProjectStep1111', 1), set_('SchoolProjectPoints1111', 0), scene('school_project_plan1111'))), peer_guard)
    page('school_project1105', 'Group project', 'Build a class display with ' + p('SchoolPeer1105') + '.', [('Start or resume', project_start), ('Back', HOME)], 10, activity(7))
    def project_choice(points):
        return guard(seq(inc('SchoolProjectPoints1111', points), set_('SchoolProjectStep1111', 2), scene('school_project_present1111')),
                     peer_guard + [(f'({p("SchoolProjectAge1111")} != <hero:age>) || ({p("SchoolProjectStep1111")} != 1)', scene('school_project1105'))])
    page('school_project_plan1111', 'Share the work', p('SchoolPeer1105') + ' asks who should build the display.', [
        ('Split the tasks', project_choice(2)), ('Do it all alone', project_choice(1)), ('Leave it to them', project_choice(0)), ('Pause', HOME)], 10, activity(7))
    project_extra = peer_guard + [(f'({p("SchoolProjectAge1111")} != <hero:age>) || ({p("SchoolProjectStep1111")} != 2)', scene('school_project1105'))]
    project_good = receipt('school_project_good1111', 'A proud moment',
        'Your display works. The teacher praises your work and ' + p('SchoolPeer1105') + ' trusts you more.',
        [set_('SchoolProjectStep1111', 3), inc('SchoolProject1105', 15), inc('SchoolPeerTrust1105', 8)], native=611,
        glyph=10, image=activity(7), extra=project_extra, quota=None)
    project_bad = receipt('school_project_bad1111', 'An awkward talk',
        'Your display is unfinished. The teacher lowers your grade and asks you both to explain.',
        [set_('SchoolProjectStep1111', 3), inc('SchoolTrust', -5), inc('SchoolPeerTrust1105', -5)], native=12,
        glyph=10, image=picture(10), extra=project_extra, quota=None)
    project_credit = receipt('school_project_credit1111', 'Your partner objects',
        p('SchoolPeer1105') + ' shows who did the work. You get a warning and lose popularity.',
        [set_('SchoolProjectStep1111', 3), inc('SchoolDiscipline1110'), inc('SchoolPeerTrust1105', -10)], native=612,
        glyph=23, image=picture(12), extra=project_extra, quota=None)
    page('school_project_present1111', 'Show your work', 'The teacher asks how you made the display.', [
        ('Present together', logic([(f'({p("SchoolProjectPoints1111")} >= 1)', project_good)], project_bad)),
        ('Take all the credit', project_credit), ('Pause', HOME)], 10, activity(7))
    page('school_project_done1111', 'Project complete', 'Your result is saved. There is a new project next year.', [('Back', HOME)], 10)

    # Short club sessions are honestly labelled sessions.  They do not set the
    # native school team's membership or overwrite an original activity list.
    page('school_clubs1105', 'Clubs', 'Pick a session after class.', [
        ('Drama', scene('school_drama1111')), ('Music', scene('school_music1111')),
        ('Art and chess', scene('school_clubs_more1111')), ('Back', HOME)], 11)
    page('school_clubs_more1111', 'Art and chess', 'Try something new after class.', [
        ('Art', scene('school_art1111')), ('Chess', scene('school_chess1111')), ('Back', scene('school_clubs1105'))], 11)
    for key, title, body, art, image, choices in [
        ('drama', 'Drama session', 'The school play needs help. Where do you fit?', 21, 8,
         [('Take a small role', 'You deliver your line clearly. The cast cheers for you.', [('SchoolFriends', 5)], 614),
          ('Work backstage', 'Your quick set change saves the scene. The cast thanks you.', [('SchoolTrust', 6)], 611)]),
        ('music', 'Music session', 'The group keeps missing the same beat.', 22, 9,
         [('Slow the song down', 'You practise the hard part together. The final run sounds much better.', [('SchoolFriends', 5), ('RapVoice', 3)], 614),
          ('Help a beginner', 'You explain the rhythm. The teacher notices your patience.', [('SchoolTrust', 5), ('RapFlow', 3)], 611)]),
        ('art', 'Art session', 'The class mural needs one final idea.', 20, 10,
         [('Add your own design', 'Your design ties the mural together. Your classmates praise it.', [('SchoolFriends', 5)], 614),
          ('Mix colours for others', 'You help everyone finish on time. The teacher praises your effort.', [('SchoolTrust', 5)], 611)]),
        ('chess', 'Chess session', 'Your opponent threatens your queen. Think before you move.', 19, 11,
         [('Move the queen to safety', 'You save your queen and win a close game. Your friends ask for a rematch.', [('SchoolPrep', 5)], 611),
          ('Ignore the threat', 'You lose your queen. Your opponent shows you the move you missed.', [('SchoolPrep', 2), ('SchoolStress', -2)], 0)]),
    ]:
        routes = [(label, receipt('school_' + key + str(i) + '_1111', title,
                   message, [inc(field, value) for field, value in effects], native=native,
                   glyph=art, image=activity(image), back=scene('school_clubs1105'), quota=('SchoolClubSession1111', 4)))
                  for i, (label, message, effects, native) in enumerate(choices)]
        page('school_' + key + '1111', title, body, routes + [('Back', scene('school_clubs1105'))], art, activity(image))

    # Cheer trial and practice match are bounded three-decision games.  They
    # record progress immediately and resume at hand-in after the final choice.
    page('school_sports1110', 'School sports', 'Train for a practice match or try a cheer routine. Join official teams from your school activities.', [
        ('Practice', scene('school_practice1111')), ('Cheer trial', scene('school_cheer_start1111')),
        ('Practice match', scene('school_match_start1111')), ('Back', HOME)], 17)
    practice = []
    for label, art in [('Basketball', 17), ('Soccer', 15), ('Football', 18)]:
        practice.append((label, receipt('school_practice_' + label.lower() + '1111', 'A good practice',
            'You work on the basics with classmates. You feel fitter and more confident.',
            [text('SchoolTeam1110', label), inc('SchoolTeamPractice1110', 10), set_('SchoolPracticeAge1111', '<hero:age>')],
            native=614, glyph=art, image=activity(4), quota=('SchoolTeam1110', 4))))
    page('school_practice1111', 'Practice', 'Choose a sport. These are practice sessions.', practice + [('Back', scene('school_sports1110'))], 17)
    young_cheer = (f'(<hero:age> < 10)', scene('school_cheer_young1111'))
    young_match = (f'(<hero:age> < 12)', scene('school_match_young1111'))
    page('school_cheer_young1111', 'Cheer trial at 10', 'Try school sports practice for now.', [('Practice', scene('school_practice1111')), ('Back', HOME)], 13)
    page('school_match_young1111', 'Match at 12', 'Practise the basics for now.', [('Practice', scene('school_practice1111')), ('Back', HOME)], 17)
    page('school_match_train1111', 'Train first', 'Complete two practice sessions this year before the match.', [('Practice', scene('school_practice1111')), ('Back', HOME)], 17)
    for prefix, title, age_guard, extra, questions, good_body, bad_body, good_image, bad_image in [
        ('cheer', 'Cheer trial', young_cheer, [], [
            ('Hear the beat', 'The music begins faster than you expected.', ['Count the first bars', 'Rush into the routine', 'Watch the leader'], [1, 0, 1]),
            ('A missed step', 'A teammate loses their place.', ['Help them find the beat', 'Keep pushing them aside', 'Stop and reset together'], [1, 0, 1]),
            ('The final count', 'The group is ready for its last move.', ['Finish together', 'Show off alone', 'Keep a steady count'], [1, 0, 1]),
        ], 'You finish the routine together. The squad cheers and your school popularity rises.',
           'You lose the beat. The coach gives you a practice plan for next year.', 3, 2),
        ('match', 'Practice match', young_match, [
            (f'({p("SchoolPracticeAge1111")} != <hero:age>) || ({p("SchoolTeam1110Age")} != <hero:age>) || ({p("SchoolTeam1110Used")} < 2)', scene('school_match_train1111'))], [
            ('First play', 'The other team leaves a teammate open.', ['Pass to the open player', 'Try to beat everyone alone', 'Call for support'], [1, 0, 1]),
            ('Under pressure', 'Your team falls behind.', ['Keep the plan', 'Blame a teammate', 'Encourage the team'], [1, 0, 1]),
            ('Last chance', 'There is time for one last play.', ['Use the play you practised', 'Ignore the team', 'Work the ball into space'], [1, 0, 1]),
        ], 'Your team wins the practice match. Your classmates cheer and your popularity rises.',
           'Your team loses a close practice match. You agree to work on teamwork next year.', 6, 5),
    ]:
        cap = prefix.title()
        age_key = 'School' + cap + 'Age1111'
        done_key = 'School' + cap + 'DoneAge1111'
        step_key = 'School' + cap + 'Step1111'
        point_key = 'School' + cap + 'Points1111'
        gates = [age_guard] + extra
        resume_round = logic([(f'({p(step_key)} == {step})', scene('school_' + prefix + '_round' + str(step) + '1111')) for step in range(3)], scene('school_' + prefix + '_finish1111'))
        start_round = guard(logic([(f'({p(done_key)} >= <hero:age>)', scene('school_' + prefix + '_done1111')),
                                  (f'({p(age_key)} == <hero:age>)', resume_round)],
                                 seq(set_(age_key, '<hero:age>'), set_(step_key, 0), set_(point_key, 0), scene('school_' + prefix + '_round01111'))), gates)
        page('school_' + prefix + '_start1111', title, 'Three choices. Your teamwork decides the result.', [('Start or resume', start_round), ('Back', scene('school_sports1110'))], 13 if prefix == 'cheer' else 17, activity(1 if prefix == 'cheer' else 4))
        for step, (heading, body, labels, points) in enumerate(questions):
            choices = []
            for label, score in zip(labels, points):
                target = seq(inc(point_key, score), set_(step_key, step + 1), scene('school_' + prefix + ('_round' + str(step + 1) if step < 2 else '_finish') + '1111'))
                checks = gates + [(f'({p(age_key)} != <hero:age>) || ({p(step_key)} != {step}) || ({p(done_key)} >= <hero:age>)', scene('school_' + prefix + '_start1111'))]
                choices.append((label, guard(target, checks)))
            page('school_' + prefix + '_round' + str(step) + '1111', heading, body, choices + [('Pause', HOME)], (16 if step == 2 else 14) if prefix == 'cheer' else 17, activity(2 if prefix == 'cheer' else 4))
        finish_checks = gates + [(f'({p(age_key)} != <hero:age>) || ({p(step_key)} != 3) || ({p(done_key)} >= <hero:age>)', scene('school_' + prefix + '_start1111'))]
        effects = [set_(done_key, '<hero:age>')]
        win = receipt('school_' + prefix + '_win1111', 'Routine complete' if prefix == 'cheer' else 'Match won', good_body,
            effects + [inc('SchoolFriends', 6), inc('SchoolCheer1110', 10 if prefix == 'cheer' else 0)], native=614,
            glyph=15, image=activity(good_image), extra=finish_checks, quota=None)
        loss = receipt('school_' + prefix + '_loss1111', 'More practice next time', bad_body,
            effects + [inc('SchoolStress', 3), inc('SchoolCheer1110', 3 if prefix == 'cheer' else 0)],
            glyph=13 if prefix == 'cheer' else 17, image=activity(bad_image), extra=finish_checks, quota=None)
        page('school_' + prefix + '_finish1111', 'The result', 'The group waits for the result.', [('See the result', logic([(f'({p(point_key)} >= 2)', win)], loss)), ('Pause', HOME)], 15)
        page('school_' + prefix + '_done1111', 'Finished this year', 'Your result is saved. Try again next year.', [('Back', scene('school_sports1110'))], 15)

    # Context-sensitive annual stories: the source native selector additionally
    # requires a live student, ages and practice, never merely a cached label.
    stories = [
        ('The class clown', 'Your teacher turns round just as you begin a joke.', 12, picture(6), [('Save it for lunch', scene('school_social1110')), ('Keep interrupting', receipt('school_disrupt1111', 'A warning', 'The teacher stops the lesson. You get a warning and lose popularity.', [inc('SchoolDiscipline1110'), inc('SchoolClown1110', 2)], native=612, glyph=23, image=picture(12))), ('Apologise', receipt('school_apology1111', 'Lesson back on track', 'Your teacher accepts the apology. You finish your work.', [inc('SchoolTrust', 4)], native=611, glyph=5))]),
        ('Picked last', 'The team captains leave you until last.', 17, activity(4), [('Ask to practise', scene('school_practice1111')), ('Make a kind joke', scene('school_social1110')), ('Talk to the teacher', scene('school_bully_entry'))]),
        ('Trouble at lunch', 'A pupil shoves a bag and takes someone’s lunch.', 3, picture(1), [('Get help', report), ('Stand with them', stand), ('Fight', fight_defend)]),
        ('Cheer trial', 'The cheer squad is holding a trial.', 13, activity(1), [('Try the routine', guard(scene('school_cheer_start1111'), [young_cheer])), ('Watch with friends', receipt('school_cheer_watch1111', 'You cheer them on', 'The squad waves as you cheer. You feel closer to your classmates.', [inc('SchoolFriends', 5)], native=614, glyph=13, image=activity(2)))]),
        ('A surprise quiz', 'The teacher puts three questions on your desk.', 1, picture(7), [('Take the quiz', start), ('Revise first', scene('school_study'))]),
        ('A rumour', 'A pupil is spreading a story about you.', 7, picture(6), [('Ask for support', scene('school_peer1105')), ('Tell a teacher', report), ('Start a fight', guard(seq(set_('SchoolFightReason1110', 2), scene('school_fight1106'))))]),
        ('Sports day', 'Your class needs help on sports day.', 17, activity(4), [('Join a practice', scene('school_practice1111')), ('Help keep score', receipt('school_score1111', 'A fair game', 'You keep a clear score. Players thank you for helping.', [inc('SchoolFriends', 4), inc('SchoolTrust', 3)], native=614, glyph=15))]),
        ('The head’s office', 'The head wants to discuss your conduct.', 23, picture(11), [('Listen and make a plan', receipt('school_head_plan1111', 'A fresh start', 'You agree to finish your work and avoid trouble. Your warning record improves.', [inc('SchoolDiscipline1110', -1), inc('SchoolTrust', 5)], glyph=5, image=picture(11))), ('Dismiss the warning', receipt('school_head_ignore1111', 'Another warning', 'The head records your reply. Another warning may lead to suspension.', [inc('SchoolDiscipline1110')], native=612, glyph=23, image=picture(12)))]),
        ('An empty seat', 'Your classmate is eating alone.', 7, picture(6), [('Invite them over', guard(study_peer, peer_guard)), ('Sit with them', scene('school_peer1105'))]),
        ('Practice match', 'Your classmates are ready to test what you practised.', 17, activity(4), [('Play the match', guard(scene('school_match_start1111'), [young_match])), ('Check the plan', scene('school_sports1110'))]),
    ]
    for n, (title, body, glyph, image, choices) in enumerate(stories, 1):
        page('school_story1110_' + str(n), title, body,
             [(label, guard(route)) for label, route in choices], glyph, image)

    # All surviving school pages use supplied school icons.  Also replace old
    # annual school images so a legacy story cannot show a church building.
    for row in a.rows:
        key = row['ScenarioID'].split('.')[-1]
        if not (key.startswith(('school_', 'annual_school', 'exam_'))):
            continue
        if row['ScenarioID'] not in owned:
            row['EmojiString'] = icon(1 if 'exam' in key else 24)
            row['BigImageString'] = ''
            row['ExteriorTitle'] = 'School life'
            owned.add(row['ScenarioID'])
    # Replace the generic cap page only in school-session action routes.
    for ident in owned:
        row = next(r for r in a.rows if r['ScenarioID'] == ident)
        for index in range(1, 5):
            field = 'Choice' + str(index) + '_AdvancedLogic'
            if 'SchoolSession1111Used' in row[field] or 'SchoolClubSession1111Used' in row[field]:
                row[field] = row[field].replace(scene('rest'), scene('school_session_full1111'))
    refresh_annual_copies(a, base)
    return sorted(a.assets)
