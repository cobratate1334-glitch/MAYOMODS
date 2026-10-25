"""Regress membership economics, public-place limits and continuing parish cases."""
import csv
import io
import json
import sys
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
from social_roblox.test_content import Model, OVERLAY, BASE
from community_refresh.content_refresh import TIERS, TERMS, IMAGE_PREFIX


class RefreshTests(unittest.TestCase):
    def member(self, tier=1, term=0, age=20):
        m = Model(age)
        m.join()
        m.choose('refresh_buy' + str(tier) + '_' + str(term))
        self.assertEqual(m.q['Club'], tier)
        return m

    def choose_church(self, m, scene, choice=1):
        row = m.rows['scenario.activitiesV18.church_refresh_' + scene]
        advanced = row[f'Choice{choice}_AdvancedLogic']
        m.route(m.advanced(json.loads(advanced)) if advanced else row[f'Choice{choice}_RouteTo'])

    def test_all_twelve_terms_use_game_money_and_correct_benefits(self):
        for tier, _, daily, places, groups, _, prices in TIERS:
            for term, ((_, days, lifetime), cents) in enumerate(zip(TERMS, prices)):
                with self.subTest(tier=tier, term=term):
                    m = self.member(tier, term)
                    self.assertAlmostEqual(m.bank, 1000 - cents / 100)
                    self.assertEqual(m.q['Robux'], 200)
                    self.assertEqual(m.q['DailyRobux'], daily)
                    self.assertEqual(m.q['PlaceLimit'], places)
                    self.assertEqual(m.q['GroupLimit'], groups)
                    self.assertEqual(m.q['DaysRemaining'], days)
                    self.assertEqual(m.q['Lifetime'], lifetime)
                    self.assertEqual(m.q['Hat' + str(tier)], 1)
                    state, bank = m.saved_state(), m.bank
                    m.choose('refresh_buy' + str(tier) + '_' + str(term))
                    self.assertEqual(m.saved_state(), state)
                    self.assertEqual(m.bank, bank)

    def test_poor_cancelled_and_underage_membership_never_debit(self):
        for age, bank in [(12, 1000), (20, 5.94), (20, 0)]:
            m = Model(age)
            m.bank = bank
            m.join()
            state = m.saved_state()
            m.choose('refresh_buy1_0')
            self.assertEqual(m.saved_state(), state)
            self.assertEqual(m.bank, bank)
        m = Model(20)
        m.join()
        state = m.saved_state()
        m.choose('refresh_buy1_0', 2)
        self.assertEqual(m.saved_state(), state)
        self.assertEqual(m.bank, 1000)

    def test_daily_allowances_expire_by_term_and_never_double_claim(self):
        for term, (_, days, lifetime) in enumerate(TERMS):
            m = self.member(2, term)
            m.age = 23
            m.sync_calendar()
            expected_days = 3 * 365 if lifetime else days
            self.assertEqual(m.q['Robux'], 200 + expected_days * 35)
            self.assertEqual(m.q['Club'], 2 if lifetime else 0)
            self.assertEqual(m.q['Hat2'], 1)
            # The explicit settle command can set its internal command flag
            # once; repeated calls must not alter any state or pay again.
            m.choose('refresh_membership')
            state, bank, journal = m.saved_state(), m.bank, list(m.journal)
            for _ in range(3):
                m.sync_calendar()
                m.choose('refresh_membership')
            self.assertEqual(m.saved_state(), state)
            self.assertEqual(m.bank, bank)
            self.assertEqual(m.journal, journal)
            m.age = 21
            m.sync_calendar()
            self.assertEqual(m.saved_state(), state)

    def test_first_membership_bonus_only_once_across_renewals(self):
        m = self.member(1, 0)
        m.ageup()
        m.sync_calendar()
        amount = m.q['Robux']
        m.choose('refresh_buy3_1')
        self.assertEqual(m.q['Club'], 3)
        self.assertEqual(m.q['Robux'], amount)

    def test_old_account_migrates_without_another_signing_bonus(self):
        m = Model(25)
        m.join()
        m.q.update(SchemaVersion=0, Club=2, ClubAge=25, Games=3, Robux=645,
                   PlaceLimit=0, GroupLimit=0)
        m.sync_calendar()
        self.assertEqual(m.q['Robux'], 645)
        self.assertEqual((m.q['DaysRemaining'], m.q['DailyRobux']), (365, 35))
        self.assertEqual((m.q['PlaceLimit'], m.q['GroupLimit']), (25, 20))
        self.assertEqual(m.q['SigningBonusGranted'], 1)
        self.assertEqual(m.q['ActivePlaces'], 3)

    def test_actual_place_capacity_and_archiving_survive_expiry(self):
        m = Model(20)
        m.join()
        m.publish()
        self.assertEqual(m.q['ActivePlaces'], 1)
        old_genre = m.q['Genre']
        m.choose('genre2')
        self.assertEqual(m.q['Genre'], old_genre)
        self.assertTrue(m.scene.endswith('refresh_manage_places'))
        m.choose('refresh_archive_all')
        self.assertEqual(m.q['ActivePlaces'], 0)
        self.assertEqual(m.q['Games'], 1)
        self.assertIn('Place 1', m.q['PlaceArchive'])
        m.ageup()
        m.sync_calendar()
        m.publish(2)
        self.assertEqual(m.q['ActivePlaces'], 1)
        self.assertEqual(m.q['Games'], 2)
        self.assertIn('Place 2', m.q['PlaceArchive'])

    def test_catalog_requires_real_owned_design_and_membership(self):
        m = Model(20)
        m.join()
        initial = m.saved_state()
        m.choose('refresh_sell')
        self.assertEqual(m.saved_state(), initial)
        m.choose('refresh_design_shirt')
        self.assertEqual(m.q['Designs'], 1)
        m.choose('refresh_buy1_0')
        before = m.q['Robux']
        m.choose('refresh_sell')
        self.assertGreater(m.q['Robux'], before)
        self.assertGreater(m.q['CatalogSales'], 0)
        state = m.saved_state()
        m.choose('refresh_sell')
        self.assertEqual(m.saved_state(), state)
        m.ageup()
        m.sync_calendar()
        state = m.saved_state()
        m.choose('refresh_sell')
        self.assertEqual(m.saved_state(), state)

    def test_creator_tasks_produce_different_results_and_feedback_is_consumed(self):
        outcomes = []
        for task in ['script', 'world', 'feedback']:
            m = Model(20)
            m.join()
            m.choose('genre1')
            m.choose('refresh_work_' + task)
            outcomes.append((m.q['Progress'], m.q['Quality'], m.q['Skill'], m.q['Feedback']))
        self.assertEqual(len(set(outcomes)), 3)
        m = Model(20)
        m.join()
        m.choose('genre1')
        state = m.saved_state()
        m.choose('refresh_fixbugs')
        self.assertEqual(m.saved_state(), state)
        m.choose('refresh_work_feedback')
        m.choose('refresh_fixbugs')
        self.assertEqual((m.q['Feedback'], m.q['Tested']), (0, 1))
        state = m.saved_state()
        m.choose('refresh_fixbugs')
        self.assertEqual(m.saved_state(), state)

    def test_club_art_is_registered_and_no_scenario_contains_physical_newlines(self):
        for row in csv.DictReader(io.StringIO(OVERLAY['genesis_activities_v18'])):
            for value in row.values():
                self.assertFalse('\n' in value or '\r' in value, row['ScenarioID'])
        for tier, _, _, _, _, asset, _ in TIERS:
            row = Model().rows['scenario.activitiesV18.roblox_refresh_tier' + str(tier)]
            self.assertEqual(row['BigImageString'], IMAGE_PREFIX + asset)

    def test_church_case_branches_have_distinct_saved_effects(self):
        outcomes = []
        for choice in [1, 2, 3]:
            m = Model(30)
            q = m.props['gameplay52']
            q.update(ClergyRank=3, ParishFunds=100)
            self.choose_church(m, 'pantry', choice)
            outcomes.append((q['ParishTrust'], q['Discipline'], q['Colleague'], q['ParishFunds']))
            self.assertEqual(q['CaseCompleted'], 1)
            self.assertEqual(q['CaseNumber'], 2)
            self.assertEqual(q['ClergyActions'], 1)
            state, messages = dict(q), list(m.journal)
            self.choose_church(m, 'pantry', choice)
            self.assertEqual(q, state)
            self.assertEqual(m.journal, messages)
        self.assertEqual(len(set(outcomes)), 3)

    def test_child_and_poor_parish_members_cannot_spend_priest_budget(self):
        for age, role, funds in [(4, 0, 100), (30, 3, 0), (30, 1, 100)]:
            m = Model(age)
            q = m.props['gameplay52']
            q.update(ClergyRank=role, ParishFunds=funds)
            before = dict(q)
            self.choose_church(m, 'pantry', 2)
            self.assertEqual(q, before)
        m = Model(4)
        self.choose_church(m, 'pantry', 1)
        self.assertEqual(m.props['gameplay52']['CaseCompleted'], 1)

    def test_parish_story_sequence_and_quota_are_not_reset_by_reopening(self):
        m = Model(30)
        q = m.props['gameplay52']
        for age, scene in [(30, 'pantry'), (31, 'welcome'), (32, 'disagreement'), (33, 'pantry')]:
            m.age = age
            self.choose_church(m, scene, 1)
            self.assertEqual(q['CaseAge'], age)
            self.assertEqual(q['ClergyActions'], 1)
        q.update(ClergyAge=34, ClergyActions=6)
        m.age = 34
        state = dict(q)
        self.choose_church(m, 'welcome', 1)
        self.assertEqual(q, state)
        m.age = 35
        self.choose_church(m, 'welcome', 1)
        self.assertEqual(q['ClergyActions'], 1)

    def test_church_root_uses_supplied_art_and_age_requirements(self):
        menu = json.loads(OVERLAY['genesis_v18_church52'])
        formation = next(x for x in menu['Items'] if x['Title'] == 'Seminary formation')
        self.assertEqual(formation['IsEnabled'], 'v19-adult')
        for row in csv.DictReader(io.StringIO(OVERLAY['genesis_activities_v18'])):
            if row['ScenarioID'].startswith('scenario.activitiesV18.church_refresh_'):
                self.assertTrue(row['BigImageString'].startswith('mayomods49/icons/'))


if __name__ == '__main__':
    unittest.main()
