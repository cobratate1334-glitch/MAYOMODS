"""Economic and navigation regressions using the retained Genesis route model.

The route evaluator and save format here are models, not Android execution.
The native journal hook has a separate instruction-emulation regression.
"""
import copy
import csv
import io
import json
import random
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import roblox_content as content
sys.path.insert(0, str(ROOT.parent / 'native_v35'))
from test_content35 import Model as GenesisModel

BASE = json.loads((ROOT.parent / 'native_v55/assets.json').read_text())
OVERLAY = content.build(BASE)


class Model(GenesisModel):
    def __init__(self, age=13):
        self.age, self.bank, self.scene = age, 1000, ''
        self.assets = {**BASE, **OVERLAY}
        self.rows = {r['ScenarioID']: r for r in csv.DictReader(io.StringIO(self.assets[content.SCENES]))}
        self.schemas = {}
        self.props = {}
        for owner, name in [(content.OWNER, content.DEFAULTS), ('gameplay52', 'genesis_v18_defaults_gameplay52')]:
            self.schemas[owner] = {r['key']: r for r in csv.DictReader(io.StringIO(self.assets[name]))}
            self.props[owner] = {k: int(r['value']) if r['type'] == 'int' else r['value'] for k, r in self.schemas[owner].items()}
        self.journal = []
        self.sync_calendar()

    @property
    def q(self):
        return self.props[content.OWNER]

    def route(self, target):
        for part in self.split(target):
            if part.startswith('BP_BANK_BALANCE='):
                self.bank += self.number(part.split('=', 1)[1])
            else:
                super().route(part)
            if part.startswith('BP_GFC_MODIFY_PROPERTY=roblox_social:SyncCalendar:'):
                self.sync_calendar()
        # This is a modeled boundary, separately tested with emitted ARM64.
        if self.q['JournalSequence'] > self.q['JournalLogged']:
            self.journal.append(self.q['JournalMessage'])
            self.q['JournalLogged'] = self.q['JournalSequence']
        church = self.props['gameplay52']
        if church['StoryJournalSequence'] > church['StoryJournalLogged']:
            self.journal.append(church['StoryJournalMessage'])
            church['StoryJournalLogged'] = church['StoryJournalSequence']

    def sync_calendar(self):
        q = self.q
        if q['SchemaVersion'] != 2:
            q.update(SchemaVersion=2, CalendarAge=self.age, PlaceLimit=1, GroupLimit=0,
                     ActivePlaces=min(q['Games'], 100))
            if q['Club'] and q['ClubAge'] == self.age:
                daily, places, groups = {1: (15, 10, 10), 2: (35, 25, 20), 3: (60, 100, 100)}[q['Club']]
                q.update(DaysRemaining=365, SigningBonusGranted=1, DailyRobux=daily,
                         PlaceLimit=places, GroupLimit=groups)
                q['Hat' + str(q['Club'])] = 1
        if self.age <= q['CalendarAge']:
            return
        days = 365 * (self.age - q['CalendarAge'])
        if not q['Lifetime']:
            days = min(days, q['DaysRemaining'])
        amount = days * q['DailyRobux']
        q.update(CalendarAge=self.age, LastAllowance=amount, LastAllowanceDays=days)
        q['Robux'] = min(100000000, q['Robux'] + amount)
        if amount:
            self.journal.append(f'I received {amount} Roblox membership Robux for {days} elapsed simulated days.')
        if not q['Lifetime']:
            q['DaysRemaining'] -= days
            if q['DaysRemaining'] == 0:
                q.update(Club=0, ClubName='Free account', DailyRobux=0, PlaceLimit=1, GroupLimit=0)

    def choose(self, key, index=1):
        row = self.rows[content.scene(key)]
        advanced = row['Choice' + str(index) + '_AdvancedLogic']
        target = self.advanced(json.loads(advanced)) if advanced else row['Choice' + str(index) + '_RouteTo']
        assert row['Choice' + str(index) + '_Text']
        self.route(target)

    def join(self):
        self.choose('account')

    def publish(self, genre=1):
        self.choose('genre' + str(genre))
        for _ in range(3):
            self.choose('build')
        self.choose('test')
        self.choose('publish')

    def ageup(self):
        self.age += 1

    def saved_state(self):
        return copy.deepcopy(self.q)


class ContentTests(unittest.TestCase):
    def test_registration_and_preservation(self):
        prior = list(csv.DictReader(io.StringIO(BASE[content.SCENES])))
        current = list(csv.DictReader(io.StringIO(OVERLAY[content.SCENES])))
        revised = {'scenario.activitiesV18.action52_' + str(n) for n in range(92, 109)}
        for before, after in zip(prior, current):
            if before['ScenarioID'] not in revised:
                self.assertTrue(before == after, before['ScenarioID'])
        self.assertEqual(len({r['ScenarioID'] for r in current}), len(current))
        registry = OVERLAY['genesis_feature_containers']
        lines = registry.splitlines()
        start = next(i for i, line in enumerate(lines) if line.startswith('ContainerId,'))
        entries = list(csv.DictReader(io.StringIO('\n'.join(lines[start:]))))
        self.assertEqual(sum(r['ContainerId'] == content.OWNER for r in entries), 1)
        self.assertEqual(entries[-1]['EntryMenu'], 'SocialMedia')
        self.assertEqual(entries[-1]['EntryListID'], content.HUB)
        with self.assertRaises(AssertionError):
            content.build({**BASE, **OVERLAY})

    def test_all_routes_properties_and_icons_resolve(self):
        m = Model()
        icons = {r['EmojiString'] for r in csv.DictReader(io.StringIO(BASE['genesis_lookup_emoji_visuals']))}
        for key, row in m.rows.items():
            if not key.startswith(content.PREFIX):
                continue
            self.assertIn(row['EmojiString'], icons)
            for owner, field in re.findall(r'<GFC\.([^.>]+)\.([^>]+)>', str(row)):
                self.assertIn(field, m.schemas[owner])
            for n in range(1, 5):
                direct = row[f'Choice{n}_RouteTo']
                advanced = row[f'Choice{n}_AdvancedLogic']
                routes = [direct] if direct else []
                if advanced:
                    d = json.loads(advanced)
                    routes += [c['then']['route_options'][0]['route_to'] for c in d['cases']]
                    routes += [d['else_when_no_matches']['route_options'][0]['route_to']]
                    for case in d['cases']:
                        m.condition(case['if'])
                for target in routes:
                    for part in m.split(target):
                        if part.startswith('scenario.'):
                            self.assertIn(part, m.rows)
                        elif part.startswith('BP_SHOW_LIST='):
                            self.assertIn(part.split('=', 1)[1], m.assets)
                        elif part.startswith('BP_GFC_'):
                            owner, field, _ = part.split('=', 1)[1].split(':', 2)
                            self.assertIn(field, m.schemas[owner])
                        elif not part.startswith('BP_BANK_BALANCE='):
                            self.fail('Unsupported route ' + part)
                self.assertFalse(row[f'Choice{n}_LogEntryLine1'], 'Continuations must not duplicate journal receipts')

    def test_account_age_gate_and_no_repeat_starter_currency(self):
        m = Model(12)
        before = m.saved_state()
        m.join()
        self.assertEqual(m.saved_state(), before)
        self.assertTrue(m.scene.endswith('young'))
        m.ageup()
        m.join()
        self.assertEqual(m.q['Robux'], 100)
        self.assertEqual(len(m.journal), 1)
        for _ in range(3):
            m.join()
            m.choose('account_done')
        self.assertEqual(m.q['Robux'], 100)
        self.assertEqual(len(m.journal), 1)

    def test_project_requires_build_beta_and_single_publication(self):
        m = Model()
        m.join()
        m.choose('genre1')
        for key in ['publish', 'test', 'update', 'genre2']:
            before = m.saved_state()
            m.choose(key)
            self.assertEqual(m.saved_state(), before)
        for _ in range(3):
            m.choose('build')
        m.choose('publish')
        self.assertEqual(m.q['Games'], 0)
        m.choose('test')
        m.choose('publish')
        self.assertEqual(m.q['Games'], 1)
        state, journal = m.saved_state(), list(m.journal)
        m.choose('publish')
        m.choose('publish_done')
        self.assertEqual(m.saved_state(), state)
        self.assertEqual(m.journal, journal)

    def test_earnings_once_per_age_across_projects_and_reload(self):
        m = Model()
        m.join()
        m.publish()
        m.choose('update')
        self.assertGreater(m.q['Robux'], 100)
        self.assertGreater(m.q['Visits'], 0)
        restored = Model(m.age)
        restored.props[content.OWNER] = json.loads(json.dumps(m.q))
        before = restored.saved_state()
        restored.choose('update')
        self.assertEqual(restored.saved_state(), before)
        restored.ageup()
        restored.choose('update')
        self.assertGreater(restored.q['Robux'], before['Robux'])
        self.assertEqual(restored.q['Actions'], 1)
        # A new project must never reset the shared income marker.
        restored.choose('genre2')
        self.assertEqual(restored.q['RevenueAge'], restored.age)

    def test_quota_prevents_grinding_and_survives_reload(self):
        m = Model()
        m.join()
        m.choose('genre1')
        for _ in range(8):
            m.choose('build')
        state = m.saved_state()
        m.choose('test')
        self.assertEqual(m.saved_state(), state)
        self.assertTrue(m.scene.endswith('quota'))
        m.ageup()
        m.choose('test')
        self.assertEqual(m.q['Actions'], 1)
        self.assertEqual(m.q['Tested'], 1)

    def test_legacy_membership_destinations_cannot_charge_or_award(self):
        for tier in range(1, 4):
            m = Model()
            m.join()
            state = m.saved_state()
            m.choose('club' + str(tier))
            self.assertEqual(m.saved_state(), state)
            m.choose('grant' + str(tier))
            self.assertEqual(m.saved_state(), state)
            self.assertEqual(m.bank, 1000)

    def test_outfit_is_owned_and_not_billed_twice(self):
        m = Model()
        m.join()
        m.choose('outfit')
        self.assertEqual((m.q['Outfit'], m.q['Robux']), (1, 25))
        state = m.saved_state()
        m.choose('outfit')
        self.assertEqual(m.saved_state(), state)

    def test_age_rewind_without_state_restore_cannot_reset_limits(self):
        m = Model(20)
        m.join()
        m.publish()
        m.choose('update')
        m.age = 19
        state = m.saved_state()
        m.choose('update')
        self.assertEqual(m.saved_state(), state)
        m.choose('refresh_archive_all')
        m.choose('genre2')
        for _ in range(2):
            m.choose('build')
        self.assertEqual(m.q['Actions'], 8)
        self.assertEqual(m.q['ActionAge'], 20)
        state = m.saved_state()
        m.choose('build')
        self.assertEqual(m.saved_state(), state)

    def test_consecutive_community_projects_must_differ(self):
        m = Model()
        m.join()
        m.choose('community_access')
        m.ageup()
        state = m.saved_state()
        m.choose('community_access')
        self.assertEqual(m.saved_state(), state)
        m.choose('community_copy')
        self.assertEqual(m.q['LastCommunity'], 2)

    def test_moderation_outcomes_differ_and_are_limited(self):
        outcomes = []
        for key in ['access', 'copy', 'scam']:
            m = Model()
            m.join()
            m.choose('community_' + key)
            outcomes.append((m.q['Trust'], m.q['Fans']))
            state = m.saved_state()
            for other in ['access', 'copy', 'scam']:
                m.choose('community_' + other)
            self.assertEqual(m.saved_state(), state)
            self.assertEqual(len(m.journal), 2)
        self.assertEqual(len(set(outcomes)), 3)

    def test_reads_never_change_economy_or_journal(self):
        m = Model()
        m.join()
        state = m.saved_state()
        journal = list(m.journal)
        for key in ['analytics', 'wiki_studio', 'wiki_robux', 'wiki_club', 'wiki_safety', 'wiki_records']:
            for _ in range(3):
                m.choose(key)
        self.assertEqual(m.saved_state(), state)
        self.assertEqual(m.journal, journal)

    def test_long_life_random_actions_remain_bounded(self):
        rng = random.Random(149)
        m = Model()
        m.join()
        actions = ['genre1', 'genre2', 'build', 'test', 'publish', 'update', 'outfit',
                   'club1', 'club2', 'club3', 'grant1', 'grant2', 'grant3',
                   'community_access', 'community_copy', 'community_scam']
        for age in range(13, 90):
            m.age = age
            for _ in range(24):
                m.choose(rng.choice(actions))
                for k, r in m.schemas[content.OWNER].items():
                    if r['type'] == 'int':
                        self.assertGreaterEqual(m.q[k], int(r['minimum']))
                        self.assertLessEqual(m.q[k], int(r['maximum']))
            self.assertEqual(m.bank, 1000)


if __name__ == '__main__':
    unittest.main()
