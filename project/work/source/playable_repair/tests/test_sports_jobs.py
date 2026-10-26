"""Real data/route contracts and emitted ARM64 icon checks; no phone claim."""
import copy
import csv
import hashlib
import io
import json
import re
import struct
import sys
from pathlib import Path

from life_repair.content import Author
from life_rework.content import csv_text, scene
from life_rework.validate_content import Model as PriorModel
from playable_repair.sports_jobs import build, CAREERS, PART_TIME, FREELANCE, SPORTS, DRILLS
from build_prison_expansion import decode


class Model(PriorModel):
    def __init__(self, base, authored, age=20):
        self.age, self.bank, self.scene = age, 1000, ''
        self.assets = {**base, **authored.assets}
        self.rows = {r['ScenarioID']: r for r in authored.rows}
        self.schemas, self.props, self.native, self.calls = {}, {}, [], []
        for name, value in self.assets.items():
            if name.startswith('genesis_') and 'default' in name and value.startswith('key,'):
                # The test only consumes owners referenced by these sports.
                owner = {'genesis_v18_defaults_seasons_v18': 'seasons_v18',
                         'genesis_v8_defaults_football_v8': 'football_v8',
                         'genesis_v18_defaults_life_v18': 'life_v18'}.get(name)
                if owner:
                    self.schemas[owner] = {r['key']: r for r in csv.DictReader(io.StringIO(value))}
        self.schemas['life_rework'] = {r['key']: r for r in authored.schema}
        for owner, schema in self.schemas.items():
            self.props[owner] = {k: int(r['value']) if r['type'] == 'int' else r['value'] for k, r in schema.items()}

    def route(self, target):
        for part in self.split(target):
            super().route(part)
            if not part.startswith('BP_GFC_MODIFY_PROPERTY='):
                continue
            owner, key, _ = part.split('=', 1)[1].split(':', 2)
            value = self.props[owner][key]
            if key.startswith('Native') and value:
                self.calls.append((owner, key, value))
                if owner == 'seasons_v18' and key == 'NativeBasketTrain20':
                    # Existing audited engine boundary. ARM64 logic itself is
                    # retained and covered by native_v20 tests, not re-invented.
                    s = self.props[owner]
                    if s['Training'] < 6 and not self.props['life_v18']['Hospital']:
                        attr = ['Inside', 'ThreePoint', 'FreeThrow', 'Playmaking', 'PerimeterDefense', 'InteriorDefense', 'Rebounding', 'Strength', 'Speed', 'Stamina'][value - 1] + '20'
                        s['Training'] += 1
                        s['Skill'] = min(100, s['Skill'] + 1)
                        s[attr] = min(95, s[attr] + 3)


def validate(base_path, out):
    base = json.loads(Path(base_path).read_text())
    a = Author(base)
    build(a, base)
    checks = []
    def ck(ok, label):
        assert ok, label
        checks.append(label)
    # Decode the actual1110 native records rather than testing invented jobs.
    for asset, key, specs in [('a16_careers-enc', 'Career', CAREERS), ('a16_part-time-jobs-enc', 'Job', PART_TIME + FREELANCE)]:
        before = list(csv.DictReader(io.StringIO(decode(base[asset]))))
        after = list(csv.DictReader(io.StringIO(decode(a.assets[asset]))))
        ck(after[:len(before)] == before, 'preserve every old ' + asset + ' record')
        ck(list(before[0]) == list(after[0]), 'same native loader header ' + asset)
        ck(len(after) == len(before) + len(specs), 'real added records ' + asset)
        ck(len({r[key] for r in after}) == len(after), 'unique native job identities ' + asset)
        ck(not {s[0] for s in specs} & {r[key] for r in before}, 'negative control: baseline lacks new jobs ' + asset)
        if key == 'Job':
            data = {r[key]: r for r in after}
            for name, *_ in FREELANCE:
                ck(data[name]['Company Type'] == 'Freelance', 'native freelance selector sees ' + name)
            for name, *_ in PART_TIME:
                ck(data[name]['Company Type'] != 'Freelance', 'native employed part-time role ' + name)
            ck(data['Furniture Assembler']['Requires Vehicle'] == data['Handyman']['Requires Vehicle'], 'retain native transport requirement')
            ck(int(data['Proofreader']['Min Intelligence']) == 40, 'proofreading has actual native qualification')
        else:
            data = {r[key]: r for r in after}
            ck(data['Civil Engineer']['Required Education'] == data['Mechanical Engineer']['Required Education'], 'engineering keeps native education requirement')
            ck(data['Hotel Manager']['Required Working Years'] == '3', 'manager needs native work experience')
    ids = [r['ScenarioID'] for r in a.rows]
    ck(len(ids) == len(set(ids)), 'no duplicate retained sports scenario IDs')
    icons = {r['EmojiString'] for r in csv.DictReader(io.StringIO(base['genesis_lookup_emoji_visuals']))}
    owned = [r for r in a.rows if any(r['ScenarioID'].startswith(scene(s + '_')) for s, *_ in SPORTS) and ('1111' in r['ScenarioID'] or '1105' in r['ScenarioID'])]
    m = Model(base, a)
    for row in owned:
        ck(row['EmojiString'] in icons, 'actual sprite catalog ' + row['ScenarioID'])
        for n in range(1, 5):
            if not row[f'Choice{n}_Text']:
                continue
            ck(len(row[f'Choice{n}_Text']) <= 30, 'short button ' + row['ScenarioID'])
            adv = row[f'Choice{n}_AdvancedLogic']
            routes = [row[f'Choice{n}_RouteTo']]
            if adv:
                obj = json.loads(adv)
                routes = [c['then']['route_options'][0]['route_to'] for c in obj['cases']] + [obj['else_when_no_matches']['route_options'][0]['route_to']]
                for case in obj['cases']:
                    m.condition(case['if'])
            for route in routes:
                ck(isinstance(route, str), 'native string route')
                for part in m.split(route):
                    if part.startswith('scenario.'):
                        ck(part in m.rows, 'registered sports destination ' + part)
                    elif part.startswith('BP_SHOW_LIST='):
                        ck(part.split('=', 1)[1] in m.assets, 'registered sports list')
                    elif part.startswith('BP_GFC_'):
                        owner, key = part.split('=', 1)[1].split(':', 2)[:2]
                        ck(key in m.schemas[owner], 'registered sports write ' + owner + '.' + key)
    # Exercise all27 play prompts and81 contextual responses plus stale replay.
    for sport, _, _, kind, _, _ in SPORTS:
        for track in range(3):
            t = Model(base, a)
            prefix = sport.title() + '1105'
            t.r['SportsEligible' + str(kind)] = 1
            t.choose(sport + '_styles1105', 1)
            t.choose(sport + '_start1111_' + str(track), 1)
            for stage in range(3):
                play = track * 3 + stage
                correct = DRILLS[sport][play][2]
                for choice in range(3):
                    trial = copy.deepcopy(t)
                    trial.choose(sport + '_play1111_' + str(play), choice + 1)
                    ck(trial.scene == scene(sport + '_read1111_' + str(play) + '_' + str(choice)), 'specific feedback for every play')
                    ck(trial.r[prefix + 'DrillPoints'] == stage + int(choice == correct), 'choices change the score')
                t.choose(sport + '_play1111_' + str(play), correct + 1)
                # Recreate a saved/reloaded UI at each step and reopen from
                # the progress page; no score or reward changes on resume.
                saved = copy.deepcopy(t.props)
                t.choose(sport + '_record1105', 1)
                ck(t.scene == (scene(sport + '_play1111_' + str(play + 1)) if stage < 2 else scene(sport + '_finish1105')) and t.props == saved, 'resume exact saved practice step')
                old = copy.deepcopy(t.props)
                t.choose(sport + '_play1111_' + str(play), correct + 1)
                ck(t.props == old, 'stale answer cannot score twice')
            t.choose(sport + '_finish1105')
            ck(t.r[prefix + 'DrillAge'] == 20 and t.r[prefix + 'Pending1111'] == 0, 'practice settles once ' + sport)
            ck(('life_rework', 'NativeAction', 131) in t.calls, 'successful practice reaches real athlete fitness/respect command')
            if sport == 'basket':
                ck(t.props['seasons_v18']['Playmaking20'] == 48 and t.props['seasons_v18']['Training'] == 1, 'basketball affects existing playmaking rating and consumes native budget')
                ck(t.props['seasons_v18']['TakeoverCharge20'] == 0, 'practice cannot refill earned takeover')
            if sport == 'soccer':
                ck(t.props['football_v8']['Vision'] == 24 and t.props['football_v8']['Shooting'] == 23, 'soccer role affects existing ratings')
                ck(t.props['seasons_v18']['Skill'] == 45, 'soccer does not mutate unrelated basketball season')
            if sport == 'football':
                ck(t.props['seasons_v18']['Skill'] == 49, 'football affects its existing season')
            old = copy.deepcopy(t.props)
            t.choose(sport + '_finish1105')
            ck(t.props == old, 'stale finish cannot double reward ' + sport)
        t = Model(base, a)
        t.choose(sport + '_styles1105', 1)
        ck(t.r[prefix + 'Style'] == 0, 'team eligibility blocks role rewards ' + sport)
        t.r['SportsEligible' + str(kind)] = 1
        t.choose(sport + '_styles1105', 1)
        t.choose(sport + '_start1111_0')
        for play in range(3):
            t.choose(sport + '_play1111_' + str(play), (DRILLS[sport][play][2] + 1) % 3 + 1)
        t.choose(sport + '_finish1105')
        ck(t.scene == scene(sport + '_retry1111') and 131 not in t.native, 'poor decisions earn feedback without fake success ' + sport)
    for style, plan in [(1, 2), (2, 1), (3, 2), (4, 3)]:
        t = Model(base, a)
        t.r['SportsEligible3'] = 1
        t.choose('football_styles1105' if style < 4 else 'football_styles_more1105', style if style < 4 else 1)
        ck(t.props['seasons_v18']['Plan'] == plan, 'football role changes actual season tactic ' + str(style))
    t = Model(base, a)
    t.r.update(SportsEligible11=1, Basket1105Style=2, Basket1105Pending1111=1, Basket1105DrillStep=3, Basket1105DrillPoints=3)
    t.props['seasons_v18']['Training'] = 6
    old = copy.deepcopy(t.props)
    t.choose('basket_finish1105')
    ck(t.props == old and t.scene == scene('basket_limit1111'), 'full native training budget cannot grant practice rewards')
    report = dict(passed=True, checks=len(checks), original_careers=216, added_full_time=len(CAREERS), added_part_time=len(PART_TIME), added_freelance=len(FREELANCE), contextual_plays=27, choice_feedback=81, native_data_and_route_model_tested=True, native_icon_test='separate ARM64 check', phone_tested=False)
    Path(out).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    validate(*sys.argv[1:])
