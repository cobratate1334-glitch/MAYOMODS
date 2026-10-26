"""Native job data and short, playable sports drills. Preserve existing IDs.

Jobs extend the original parsers, interviews, work schedule and pay system.
Sports use the existing team gates, season ratings and basketball badge engine.
No third-party game data, code, ratings or player assets are imported.
"""
import csv
import io
import json
from life_rework.content import p, scene, menu, set_, inc, text, seq, logic, fun, csv_text
from build_prison_expansion import decode, encode

# name, verified original career template, pay, cap, original emoji identifier.
CAREERS = [
    ('Civil Engineer', 'Mechanical Engineer', 41000, 113000, 'wrench'),
    ('Train Driver', 'Bus Driver', 31000, 72000, 'rescue-helmet'),
    ('Veterinary Assistant', 'Receptionist', 24000, 47000, 'dog'),
    ('Conservation Officer', 'Environmental Scientist', 35000, 85000, 'seedling'),
    ('Hotel Manager', 'Receptionist', 32000, 87000, 'hotel'),
    ('Court Clerk', 'Paralegal', 30000, 65000, 'clipboard'),
]
# name, native template, min/max hourly pay, min age, emoji.
PART_TIME = [
    ('Bakery Counter Assistant', 'Donut Maker', 9, 17, 16, 'bread'),
    ('Cinema Attendant', 'Usher', 9, 16, 16, 'ticket'),
    ('Hotel Breakfast Assistant', 'Hotel Front Desk Clerk', 10, 18, 16, 'hotel'),
    ('Bike Rental Assistant', 'Bike Shop Mechanic', 10, 20, 16, 'bicycle'),
    ('Garden Centre Assistant', 'Flower Shop Assistant', 10, 18, 16, 'seedling'),
    ('Recreation Assistant', 'Gym Receptionist', 10, 19, 16, 'basketball'),
]
FREELANCE = [
    ('Garden Weeder', 'Lawn Mower', 10, 22, 16, 'seedling'),
    ('House Cleaner', 'Window Cleaner', 12, 25, 18, 'broom'),
    ('Furniture Assembler', 'Handyman', 18, 35, 18, 'hammer'),
    ('Music Tutor', 'Tutor', 15, 32, 16, 'musical-note'),
    ('Proofreader', 'Tutor', 12, 28, 16, 'pencil'),
    ('Pet Care Helper', 'Pet Sitter', 10, 24, 16, 'dog'),
]

CAREER_ICONS = {r[0]: r[4] for r in CAREERS}
PART_TIME_ICONS = {r[0]: r[5] for r in PART_TIME + FREELANCE}


def job_data(base):
    """Append complete native records. Original rows and requirements survive."""
    out = {}
    name = 'a16_careers-enc'
    rows = list(csv.DictReader(io.StringIO(decode(base[name]))))
    old = {r['Career']: r for r in rows}
    assert len(old) == len(rows)
    for title, prototype, pay, cap, _ in CAREERS:
        assert title not in old, title
        row = dict(old[prototype])
        row.update(Career=title, **{
            'Seniority Track': f'Junior {title}, {title}, Senior {title}',
            'Seniority Track Years': '15', 'Can Skip Positions': '0',
            'Starting Salary': f'${pay:,.2f}', 'Salary Cap': f'${cap:,.2f}',
            'Required Working Years': '0', 'Min Age': '18', 'Max Age': '',
            'Commonness Score': '3', 'Holiday': '', 'Unavailable': '',
            'Exclude Third Persons': '', 'Social Media Fans': '', 'Max Fame': '',
        })
        # A manager is a later step rather than an unqualified teen hire.
        if title == 'Hotel Manager':
            row['Required Working Years'] = '3'
        if title == 'Veterinary Assistant':
            row['Company Type'] = old['Veterinarian']['Company Type']
            row['Requires Clear Criminal Record'] = 'x'
        rows.append(row)
    out[name] = encode(csv_text(rows))
    name = 'a16_part-time-jobs-enc'
    rows = list(csv.DictReader(io.StringIO(decode(base[name]))))
    old = {r['Job']: r for r in rows}
    for title, prototype, low, high, age, _ in PART_TIME + FREELANCE:
        assert title not in old, title
        row = dict(old[prototype])
        row.update(Job=title, **{
            'Min Hourly Rate': f'${low} ', 'Max Hourly Rate': f'${high} ',
            'Min Age': str(age), 'Max Age': '', 'Gender': '',
            'Min Weekly Hours': '4', 'Max Weekly Hours': '16',
            'Commonness Score': '3', 'Tiring Score': '2',
        })
        if title in {r[0] for r in FREELANCE}:
            row['Company Type'] = 'Freelance'
            row['Must Be Student'] = ''
        if title in {'Music Tutor', 'Proofreader'}:
            row['Min Intelligence'] = '40'
            row['Success Defining Attribute'] = 'Intelligence'
        # Assembly takes place at the customer; retain the original transport
        # requirements instead of pretending every teen can accept the work.
        rows.append(row)
    out[name] = encode(csv_text(rows))
    return out


# The answers follow the situation, not the name of a super-powered trait.
# Each tuple: clue; three (short label, clear feedback); correct answer index.
DRILLS = {
 'basket': [
  ('A second defender closes on you. Your teammate is alone in the corner.', [
   ('Pass to the corner', 'The open shooter gets a clean look.'),
   ('Shoot over both', 'Two defenders block your view. The shot misses.'),
   ('Keep dribbling', 'The trap closes. You lose the passing angle.')], 0),
  ('Your defender gives you space. Your feet are set behind the arc.', [
   ('Drive into traffic', 'Help defence cuts off the lane.'),
   ('Take the open three', 'You stay balanced and release the open shot.'),
   ('Throw a risky lob', 'The centre reads the pass and tips it away.')], 1),
  ('The defender rushes past you. The lane is clear.', [
   ('Force a fadeaway', 'You give up an easy path for a hard shot.'),
   ('Wait for help', 'The defence resets before you move.'),
   ('Drive to the rim', 'Your first step creates a clean finish.')], 2),
  ('Their guard drives toward the rim. Your centre is covering the paint.', [
   ('Leave the corner', 'Their corner shooter is now unmarked.'),
   ('Stay with your shooter', 'You deny the kick-out while your centre helps.'),
   ('Chase the ball', 'Both defenders chase one player. A pass beats you.')], 1),
  ('A shot goes up. A taller opponent is behind you.', [
   ('Box out first', 'You seal the opponent away from the rebound.'),
   ('Watch the ball', 'The opponent gets inside position.'),
   ('Start the fast break', 'Your team gives up a second chance.')], 0),
  ('The shooter catches the ball. You are one step away.', [
   ('Jump into them', 'You make contact and give away a foul.'),
   ('Ignore the shot', 'The shooter has an easy look.'),
   ('Close out under control', 'Your raised hand makes the shot harder.')], 2),
  ('Your team has a small lead. There is time left on the shot clock.', [
   ('Rush a deep three', 'The miss gives the other team a quick break.'),
   ('Run the set play', 'Your team uses the clock and finds a good shot.'),
   ('Hold past the buzzer', 'The shot clock expires.')], 1),
  ('A teammate misses twice. They are open again.', [
   ('Make the extra pass', 'You trust the open player and keep the attack moving.'),
   ('Shout at them', 'The argument breaks your team’s focus.'),
   ('Shoot while covered', 'A contested shot wastes the opening.')], 0),
  ('Their defence switches every screen. Your tall teammate has a small guard.', [
   ('Ignore the mismatch', 'The defence escapes the mismatch.'),
   ('Dribble into the trap', 'The double-team takes away your space.'),
   ('Feed the mismatch', 'Your teammate gets the ball in a strong position.')], 2),
 ],
 'soccer': [
  ('Their back line is high. Your forward starts a run between two defenders.', [
   ('Play the through ball', 'The pass reaches the runner before the gap closes.'),
   ('Shoot from halfway', 'The keeper has time to collect it.'),
   ('Turn toward your goal', 'The forward’s run goes unused.')], 0),
  ('You reach the edge of the box. A defender blocks your shot.', [
   ('Shoot through them', 'The defender blocks the attempt.'),
   ('Square the ball', 'Your free teammate gets a clear chance.'),
   ('Sprint into the tackle', 'The defender wins the ball.')], 1),
  ('The keeper charges out. You have space for one touch.', [
   ('Stop and wait', 'The keeper closes the angle.'),
   ('Blast at the keeper', 'The keeper blocks the shot.'),
   ('Place it past the keeper', 'You stay calm and use the open corner.')], 2),
  ('Their winger has the ball near the touchline. Your full-back needs time.', [
   ('Dive into a tackle', 'The winger slips past your lunge.'),
   ('Jockey and slow them', 'You hold your ground until support arrives.'),
   ('Leave them alone', 'The winger runs straight into space.')], 1),
  ('The opponent takes a heavy touch. A teammate covers behind you.', [
   ('Press the loose ball', 'You win the ball with cover behind you.'),
   ('Run away', 'The opponent recovers the loose ball.'),
   ('Foul from behind', 'The referee stops play and shows a card.')], 0),
  ('A cross is coming. Their striker waits at the far post.', [
   ('Watch only the ball', 'The striker gets behind you.'),
   ('Leave for a counter', 'The striker is left unmarked.'),
   ('Track the striker', 'You stay goal-side and challenge the cross.')], 2),
  ('Your side leads late. The passing lane ahead is blocked.', [
   ('Force a long pass', 'The pass gives possession away.'),
   ('Keep the ball', 'Short passes use time and protect your lead.'),
   ('Shoot from distance', 'The keeper starts a counterattack.')], 1),
  ('You lose the ball. Your teammates have moved forward.', [
   ('Recover your position', 'You close the gap before the counter develops.'),
   ('Argue with the referee', 'The opponent attacks the space you left.'),
   ('Stand and watch', 'Your defence faces an extra attacker.')], 0),
  ('The centre is crowded. Your winger is free near the touchline.', [
   ('Dribble into the crowd', 'You run out of space.'),
   ('Force a central pass', 'A defender cuts it out.'),
   ('Switch the play', 'The winger receives the ball with room to attack.')], 2),
 ],
 'football': [
  ('The defence shows a blitz. Your short receiver has space.', [
   ('Throw the quick pass', 'The ball leaves before the pressure arrives.'),
   ('Wait for a deep route', 'The blitz reaches the pocket.'),
   ('Run into the blitz', 'The unblocked defender stops you.')], 0),
  ('The pocket holds. Your first receiver is covered.', [
   ('Force the first read', 'The corner gets a hand on the pass.'),
   ('Check the next route', 'Your next receiver breaks open.'),
   ('Run backward', 'You give up safe ground in a clean pocket.')], 1),
  ('The receivers pull coverage deep. A clear running lane opens.', [
   ('Throw across the field', 'A safety reads the late throw.'),
   ('Keep waiting', 'The pocket starts to collapse.'),
   ('Take the open run', 'You gain yards and slide before contact.')], 2),
  ('Their receiver turns toward the sideline. You have safety help inside.', [
   ('Guess an inside route', 'The receiver gains space outside.'),
   ('Protect the outside', 'Your coverage funnels the receiver toward help.'),
   ('Leave to blitz', 'The receiver is wide open.')], 1),
  ('The runner heads toward you. Your teammate closes from the other side.', [
   ('Wrap up and contain', 'You stop the runner until support finishes the tackle.'),
   ('Try a wild hit', 'The runner slips past your shoulder.'),
   ('Chase the fake', 'You leave a lane behind you.')], 0),
  ('It is third and long. Their receiver catches a short pass.', [
   ('Dive for a pick', 'Your gamble leaves room after the catch.'),
   ('Give up the tackle', 'The receiver reaches the first-down marker.'),
   ('Tackle before the marker', 'You stop the drive short of a first down.')], 2),
  ('Your team leads late. The opponent has few timeouts.', [
   ('Force a deep throw', 'An incomplete pass stops the clock.'),
   ('Use a safe run', 'You keep possession and make them use a timeout.'),
   ('Hurry every snap', 'You leave the opponent extra time.')], 1),
  ('Your receiver signals that their defender is playing far off.', [
   ('Use the short route', 'You take the easy gain and keep the drive alive.'),
   ('Ignore the signal', 'You miss a simple opening.'),
   ('Force a crowded deep pass', 'The safety arrives before the ball.')], 0),
  ('Your team trails late. You need to save time after a catch.', [
   ('Stay in bounds', 'The clock keeps running.'),
   ('Argue about the spot', 'The clock runs while you argue.'),
   ('Reach the sideline', 'You gain yards and stop the clock.')], 2),
 ],
}

SPORTS = [
 ('basket', 'Basketball', 'genesis_v9_basketball_v9', 11, 'basketball',
  ['Floor general', 'Three-point specialist', 'Slasher', 'Rim protector']),
 ('soccer', 'Soccer', 'genesis_v8_football_v8', 1, 'soccer-ball',
  ['Playmaker', 'Pressing forward', 'Wide runner', 'Ball-winning defender']),
 ('football', 'American football', 'genesis_v18_pro_sports18', 3, 'football',
  ['Field general', 'Scrambler', 'Power runner', 'Lockdown defender']),
]


def _page(a, key, *args, **kwargs):
    # Author.page appends. Replace the retained 1105 scenes without duplicate IDs.
    a.rows[:] = [r for r in a.rows if r['ScenarioID'] != scene(key)]
    return a.page(key, *args, **kwargs)


def _modify(owner, key, value):
    return f'BP_GFC_MODIFY_PROPERTY={owner}:{key}:={value}'


def _pulse(owner, key, value):
    return seq(_modify(owner, key, 0), _modify(owner, key, value))


def sports(a, base):
    for sport, title, hub, kind, icon, styles in SPORTS:
        prefix = sport.title() + '1105'  # Old saves keep their style and record.
        root = scene(sport + '_style1105')
        guard = ((f'({p("SportsEligible" + str(kind))} != 1)', scene('sports_require_' + str(kind))),
                 ('(<GFC.life_v18.Hospital> == 1)', scene('sports_hospital1111')))
        a.prop(prefix + 'DrillTrack1111', 0, 0, 2)
        a.prop(prefix + 'Pending1111', 0, 0, 1)
        a.string(prefix + 'LastRead1111', 'Choose a practice plan.')
        _page(a, sport + '_style1105', title + ' practice',
              'Choose a role. Read the play. Your choices build skills for your team.', [
                  ('Choose my role', scene(sport + '_styles1105')),
                  ('Coach’s practice', scene(sport + '_drill_start1105')),
                  ('My progress', scene(sport + '_record1105')),
                  ('Back', menu(hub))], icon,
              stats=[('Role', p(prefix + 'StyleName'))])
        for page, indices in [(0, [1, 2, 3]), (1, [4])]:
            choices = []
            for index in indices:
                label = styles[index - 1]
                effects = [set_(prefix + 'Style', index), text(prefix + 'StyleName', label)]
                if sport == 'football':
                    effects.append(_modify('seasons_v18', 'Plan', [2, 1, 2, 3][index - 1]))
                receipt = sport + '_choose1105_' + str(index) + '_result'
                detail = {
                    'basket': ['Practice builds your passing rating.', 'Practice builds your three-point rating.', 'Practice builds your inside scoring.', 'Practice builds your paint defence.'],
                    'soccer': ['Good reads build extra vision.', 'Good reads build extra shooting.', 'Good reads build extra shooting.', 'Good reads build extra vision.'],
                    'football': ['Your season uses a balanced plan.', 'Your season uses an attacking plan. More scoring brings more risk.', 'Your season uses a balanced plan.', 'Your season uses a defensive plan. Both teams get fewer scoring chances.'],
                }[sport][index - 1]
                _page(a, receipt, 'Role saved', label + '. ' + detail, [('Continue', root)], icon)
                choices.append((label, a.gate(seq(*effects, scene(receipt)), extra=guard)))
            choices.append(('More roles' if page == 0 else 'Back', scene(sport + '_styles_more1105') if page == 0 else root))
            _page(a, sport + ('_styles1105' if page == 0 else '_styles_more1105'), 'My role', 'Choose how you help your team.', choices, icon)
        _page(a, sport + '_drill_start1105', 'Coach’s practice',
              'Three plays. Two good reads earn skill progress. One scored session per year.', [
                  ('Attack', scene(sport + '_start1111_0')),
                  ('Defence', scene(sport + '_start1111_1')),
                  ('Team play', scene(sport + '_start1111_2')),
                  ('Back', root)], icon)
        for track in range(3):
            start = seq(set_(prefix + 'DrillTrack1111', track), set_(prefix + 'DrillStep', 0),
                        set_(prefix + 'DrillPoints', 0), set_(prefix + 'DrillFocus', 0),
                        set_(prefix + 'Pending1111', 1), scene(sport + '_play1111_' + str(track * 3)))
            _page(a, sport + '_start1111_' + str(track), ['Attack practice', 'Defensive practice', 'Team practice'][track],
                  'Your coach runs three short plays. Read the situation before choosing.', [
                      ('Start', a.gate(start, extra=guard + ((f'({p(prefix + "Style")} == 0)', scene(sport + '_styles1105')),
                                                          (f'({p(prefix + "DrillAge")} >= <hero:age>)', scene(sport + '_done1111'))))),
                      ('Back', scene(sport + '_drill_start1105'))], icon)
        for play, (clue, options, correct) in enumerate(DRILLS[sport]):
            track, stage = divmod(play, 3)
            expected = ((f'({p(prefix + "Pending1111")} != 1) || ({p(prefix + "DrillTrack1111")} != {track}) || ({p(prefix + "DrillStep")} != {stage}) || ({p(prefix + "DrillAge")} >= <hero:age>)', scene(sport + '_done1111')),)
            choices = []
            for index, (label, feedback) in enumerate(options):
                key = sport + '_read1111_' + str(play) + '_' + str(index)
                effects = [set_(prefix + 'DrillStep', stage + 1), text(prefix + 'LastRead1111', feedback)]
                if index == correct:
                    effects.append(inc(prefix + 'DrillPoints'))
                next_scene = scene(sport + '_play1111_' + str(play + 1)) if stage < 2 else scene(sport + '_finish1105')
                _page(a, key, 'Good read' if index == correct else 'Coach’s feedback', feedback, [('Next play' if stage < 2 else 'Review practice', next_scene)], icon)
                choices.append((label, a.gate(seq(*effects, scene(key)), extra=guard + expected)))
            choices.append(('Leave practice', root))
            _page(a, sport + '_play1111_' + str(play), 'Play ' + str(stage + 1) + '/3', clue, choices, icon)
        # Preserve old drill IDs as entrances, rather than leaving stale saved
        # routes able to award points with the old three-question answer key.
        for stage in range(1, 4):
            _page(a, sport + '_drill' + str(stage) + '_1105', 'Practice has changed',
                  'Choose a new coach’s practice to continue.', [('Choose practice', scene(sport + '_drill_start1105'))], icon)
        _page(a, sport + '_done1111', 'Practice record', 'Your last score is saved. Start a fresh session after aging up.',
              [('My progress', scene(sport + '_record1105')), ('Back', root)], icon)
        completion = ((f'({p(prefix + "Pending1111")} != 1) || ({p(prefix + "DrillStep")} != 3) || ({p(prefix + "DrillAge")} >= <hero:age>)', scene(sport + '_done1111')),)
        common = [set_(prefix + 'DrillAge', '<hero:age>'), set_(prefix + 'Pending1111', 0),
                  inc(prefix + 'XP', fun('mul', p(prefix + 'DrillPoints'), 5))]
        passed = f'({p(prefix + "DrillPoints")} >= 2)'
        gain = fun('add', 1, p(prefix + 'DrillPoints'))
        effects = []
        if sport == 'basket':
            # Use the existing six-session training budget and native attribute
            # + badge refresh. Practice cannot refill Takeover or fake a win.
            practice = logic([
                (f'({p(prefix + "Style")} == {index})', _pulse('seasons_v18', 'NativeBasketTrain20', target))
                for index, target in enumerate([4, 2, 1, 6], 1)], _pulse('seasons_v18', 'NativeBasketTrain20', 4))
            rating_gate = [('(<GFC.seasons_v18.Training> >= 6)', scene('basket_limit1111'))]
            # Branch the native training pulse by role before the common receipt.
            # The choice interpreter accepts flat logic leaves only.
            for case in practice['cases']:
                case['then']['route_options'][0]['route_to'] = seq(case['then']['route_options'][0]['route_to'], _pulse('seasons_v18', 'NativeBasketRefresh20', 1))
            practice['else_when_no_matches']['route_options'][0]['route_to'] = seq(practice['else_when_no_matches']['route_options'][0]['route_to'], _pulse('seasons_v18', 'NativeBasketRefresh20', 1))
        elif sport == 'soccer':
            # Roles change the existing soccer ratings, not a cosmetic badge.
            vision_bonus = fun('clamp', fun('add', fun('sub', 1, fun('min', 1, fun('abs', fun('sub', p(prefix + 'Style'), 1)))), fun('sub', 1, fun('min', 1, fun('abs', fun('sub', p(prefix + 'Style'), 4))))), 0, 1)
            shot_bonus = fun('sub', 1, vision_bonus)
            effects = [_modify('football_v8', 'Vision', fun('clamp', fun('add', '<GFC.football_v8.Vision>', p(prefix + 'DrillPoints'), vision_bonus), 0, 100)),
                       _modify('football_v8', 'Shooting', fun('clamp', fun('add', '<GFC.football_v8.Shooting>', p(prefix + 'DrillPoints'), shot_bonus), 0, 100))]
        else:
            effects = [_modify('seasons_v18', 'Skill', fun('clamp', fun('add', '<GFC.seasons_v18.Skill>', gain), 0, 100))]
        success_key = sport + '_complete1105_result'
        failure_key = sport + '_retry1111'
        body = {'basket': 'Your role skill improved. Your badges are updated. This used one normal training session.',
                'soccer': 'Your shooting and vision improved. Your coach values the good reads.',
                'football': 'Your season skill improved. Your coach values the good reads.'}[sport]
        _page(a, success_key, 'Practice complete', body, [('Continue', root)], icon)
        _page(a, failure_key, 'Keep practising', 'You read fewer than two plays. Your score is saved. Skills did not improve this time.', [('Continue', root)], icon)
        journal_success = [text('JournalMessage', 'I finished ' + title.lower() + ' practice. ' + body), inc('JournalSequence')]
        success = seq(*common, *effects, _pulse('life_rework', 'NativeAction', 131), *journal_success, scene(success_key))
        if sport == 'basket':
            # Apply each leaf before the result. A full normal budget prevents
            # all new practice rewards instead of claiming a rating increase.
            def suffix(route):
                return seq(*common, route, _pulse('life_rework', 'NativeAction', 131), *journal_success, scene(success_key))
            for case in practice['cases']:
                case['then']['route_options'][0]['route_to'] = suffix(case['then']['route_options'][0]['route_to'])
            practice['else_when_no_matches']['route_options'][0]['route_to'] = suffix(practice['else_when_no_matches']['route_options'][0]['route_to'])
            success = logic(rating_gate, practice)
        failure = seq(*common, text('JournalMessage', 'I finished ' + title.lower() + ' practice. I need to work on reading the play.'), inc('JournalSequence'), scene(failure_key))
        _page(a, sport + '_finish1105', 'Coach’s review',
              'Good reads: ' + p(prefix + 'DrillPoints') + '/3. Two good reads earn a skill gain.',
              [('Finish practice', a.gate(logic([(passed, success)], failure), extra=guard + completion))], icon)
        progress = [('Role', p(prefix + 'StyleName')), ('Last score', p(prefix + 'DrillPoints') + '/3')]
        if sport == 'soccer':
            progress += [('Shooting', '<GFC.football_v8.Shooting>'), ('Vision', '<GFC.football_v8.Vision>')]
        else:
            progress += [('Season skill', '<GFC.seasons_v18.Skill>')]
        resume = logic(
            [(f'({p(prefix + "Pending1111")} != 1)', scene(sport + '_drill_start1105')),
             (f'({p(prefix + "DrillAge")} >= <hero:age>)', scene(sport + '_done1111')),
             (f'({p(prefix + "DrillStep")} == 3)', scene(sport + '_finish1105'))] +
            [(f'({p(prefix + "DrillTrack1111")} == {track}) && ({p(prefix + "DrillStep")} == {stage})', scene(sport + '_play1111_' + str(track * 3 + stage)))
             for track in range(3) for stage in range(3)], scene(sport + '_drill_start1105'))
        _page(a, sport + '_record1105', title + ' progress',
              'Good decisions improve the skills used by your team. You can score one coach’s practice each year.',
              [('Resume practice', a.gate(resume, extra=guard)), ('New practice', scene(sport + '_drill_start1105')), ('Back', root)], icon, stats=progress)
        # Retain the original list and its TileIDs. Give each sport its own icon.
        data = json.loads(a.assets.get(hub, base[hub]))
        for tile in data.get('Items', []):
            if tile.get('Title') == 'Playstyle and coach’s drills':
                tile.update(Title='My role and practice', Icon=icon, SecondLine='Read the play and build team skills')
                tile['ActionList'][0]['ConditionList'][0] = {'ScenarioID': scene(sport + '_style1105'), 'ScenarioFile': 'genesis_life_rework'}
        a.assets[hub] = json.dumps(data, indent=2)
    _page(a, 'sports_hospital1111', 'Recover first', 'You are in hospital. Train after you recover.', [('Back to sports', menu('genesis_v18_seasons_v18'))], 'hospital')
    _page(a, 'basket_limit1111', 'Training limit', 'You used all six basketball sessions this year. Age up before finishing another practice.', [('Back', scene('basket_style1105'))], 'basketball')


def build(a, base):
    icons = {r['EmojiString'] for r in csv.DictReader(io.StringIO(base['genesis_lookup_emoji_visuals']))}
    assert set(CAREER_ICONS.values()) | set(PART_TIME_ICONS.values()) <= icons
    a.assets.update(job_data(base))
    sports(a, base)
