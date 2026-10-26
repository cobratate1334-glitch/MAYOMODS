"""Saved action outcomes and native command boundaries; no Unity rendering."""
import copy
import csv
import io
import json
import unittest

from life_repair.content import Author
from life_rework.content import scene, csv_text
from playable_repair.action_content import build, refresh_annual_copies
from playable_repair.tests.test_school_content import BASE_PATH, Model


class ActionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(BASE_PATH.read_text())
        cls.author = Author(cls.base)
        build(cls.author, cls.base)
        refresh_annual_copies(cls.author, cls.base)
        cls.assets = {**cls.base, **cls.author.assets,
                      'genesis_life_rework': csv_text(cls.author.rows, list(cls.author.header)),
                      'genesis_rework_defaults': csv_text(cls.author.schema)}

    def model(self, age=25, **state):
        m = Model(self.assets, age)
        m.r.update(NativeBank1105=10000, Year=2026, **state)
        return m

    def begin_heist(self, m):
        m.choose('heist_crew1106', 1)
        m.choose('heist_offer1106_1')

    def complete_heist(self, m, choices=(1, 1, 1)):
        self.begin_heist(m)
        for stage, choice in enumerate(choices, 1):
            m.choose('heist_round1106_' + str(stage), choice)
        m.choose('heist_finish1106')

    def test_heist_cost_is_once_and_resume_keeps_every_stage(self):
        m = self.model()
        self.begin_heist(m)
        self.assertEqual(m.bank, 900)
        for stage in range(1, 4):
            before = copy.deepcopy(m.r)
            m.choose('heist_offer1106_2')
            self.assertEqual(m.bank, 900)
            self.assertEqual(m.r, before)
            m.choose('heist_current1111')
            self.assertEqual(m.scene, scene('heist_round1106_' + str(stage)))
            m.choose('heist_round1106_' + str(stage), 1)
        m.choose('heist_current1111')
        self.assertEqual(m.scene, scene('heist_finish1106'))

    def test_success_share_changes_real_bank_once(self):
        m = self.model()
        self.complete_heist(m)
        self.assertEqual(m.r['HeistPayout1111'], 1)
        self.assertEqual(m.scene, scene('heist_split1106'))
        m.choose('heist_split1106', 1)
        self.assertEqual(m.bank, 1200)  # $1,000 - $100 + 25% of $1,200.
        self.assertEqual(m.r['HeistLoot1106'], 0)
        self.assertEqual(m.r['HeistPayout1111'], 0)
        saved = copy.deepcopy(m.r)
        m.choose('heist_split1106', 2)
        self.assertEqual(m.bank, 1200)
        self.assertEqual(m.r, saved)
        m.choose('heist_offer1106_1')
        self.assertEqual(m.scene, scene('heist_wait1106'))

    def test_abort_and_failure_cannot_claim_planned_loot(self):
        m = self.model()
        self.begin_heist(m)
        m.choose('heist_round1106_1', 3)
        self.assertEqual(m.r['HeistLoot1106'], 0)
        saved = m.bank
        m.choose('heist_split1106', 1)
        self.assertEqual(m.bank, saved)
        m = self.model()
        self.complete_heist(m, (2, 2, 2))
        self.assertEqual(m.scene, scene('heist_arrest1106'))
        self.assertEqual(m.r['HeistLoot1106'], 0)
        self.assertEqual(m.r['HeistPayout1111'], 0)
        saved = m.bank
        m.choose('heist_split1106', 1)
        self.assertEqual(m.bank, saved)
        row = m.rows[scene('heist_arrest1106')]
        self.assertEqual(row['Choice1_RouteTo'], 'executable.blueprint.heroSendToPrison')
        self.assertEqual(json.loads(row['BlueprintPayloadForRoute'])['payload']['sentence_years'], '3')

    def test_unfinished_job_expires_and_payout_survives_ageup(self):
        m = self.model()
        self.begin_heist(m)
        m.age += 1
        m.choose('heist_current1111')
        self.assertEqual(m.scene, scene('heist_expired1111'))
        m.choose('heist_expired1111')
        self.assertEqual(m.r['HeistStage1106'], 0)
        self.assertEqual(m.r['HeistLoot1106'], 0)
        m = self.model()
        self.complete_heist(m)
        m.age += 1
        m.choose('heist_current1111')
        self.assertEqual(m.scene, scene('heist_split1106'))
        m.choose('heist_split1106')
        self.assertEqual(m.bank, 1200)

    def test_heist_age_period_membership_and_prison_guards(self):
        for m in [self.model(age=14), self.model(NativeInPrison1105=1)]:
            m.choose('heist_crew1106', 1)
            self.assertEqual(m.scene, scene('heist_locked1106'))
            self.assertEqual(m.r['HeistCrew1106'], 0)
        m = self.model()
        m.choose('heist_offer1106_1')
        self.assertEqual(m.scene, scene('heist_no_crew1106'))
        m.r.update(HeistCrew1106=1, Year=1900)
        m.choose('heist_offer1106_3')
        self.assertEqual(m.scene, scene('heist_period1106'))
        self.assertEqual(m.bank, 1000)

    def test_native_peer_support_owns_identity_quota_and_journal(self):
        m = self.model(NativeInPrison1105=1)
        m.choose('prison_programmes1110')
        self.assertIn(610, m.native)
        self.assertEqual(m.scene, scene('prison_support1110_result'))
        self.assertEqual(m.rows[m.scene]['Body'], '<GFC.life_rework.PeerReport1110>')
        self.assertEqual(m.r['PrisonSupport1110'], 0)  # No fabricated success.
        self.assertEqual(m.r['JournalSequence'], 0)  # 610 journals the native conversation.
        m = self.model()
        m.choose('prison_programmes1110')
        self.assertEqual(m.scene, scene('prison_closed1105'))
        self.assertNotIn(610, m.native)
        source = next(csv.DictReader(io.StringIO(self.assets['genesis_v8_inmate_support'])))
        self.assertEqual(source['Choice1_RouteTo'], 'BP_SHOW_LIST=genesis_v18_prison40')

    def test_course_has_question_and_real_native_conduct_effect(self):
        m = self.model(NativeInPrison1105=1)
        m.choose('prison_classroom1111', 1)
        self.assertEqual(m.r['PrisonCourse1110'], 1)
        self.assertIn(617, m.native)
        self.assertEqual(m.scene, scene('prison_course1110_result'))
        m.choose('prison_classroom1111', 2)
        self.assertEqual(m.r['PrisonCourse1110'], 1)
        self.assertEqual(m.scene, scene('prison_course_retry1111_result'))

    def test_research_is_playable_pays_once_and_resumes(self):
        for role, key in [(1, 'storm'), (2, 'tsunami'), (3, 'volcano')]:
            m = self.model(FieldRole=role)
            m.choose(key + '_survey', 1)
            self.assertEqual(m.scene, scene(key + '_conditions1111'))
            before = copy.deepcopy(m.r)
            m.choose(key + '_survey', 2)
            self.assertEqual(m.r, before)
            m.choose(key + '_conditions1111')
            self.assertEqual(m.r['FieldReportReady'], 1)
            self.assertEqual(m.r['FieldSurveyStage1111'], 2)
            m.choose(key + '_record', 1)
            self.assertEqual(m.bank, 1250)
            self.assertEqual(m.r['FieldPaidAge'], m.age)
            self.assertIn('$250', m.rows[m.scene]['Body'])
            m.choose(key + '_record', 1)
            self.assertEqual(m.bank, 1250)
            self.assertEqual(m.scene, scene(key + '_report_wait1106'))

    def test_research_training_abort_stale_and_cross_contract_guards(self):
        m = self.model(FieldRole=1)
        m.choose('storm_survey', 2)
        self.assertEqual(m.scene, scene('storm_need_training1111'))
        m.choose('storm_train')
        m.choose('storm_train')
        m.choose('storm_survey', 2)
        self.assertEqual(m.r['FieldSurveyPlan1111'], 2)
        m.choose('volcano_join')
        self.assertEqual(m.scene, scene('volcano_active1111'))
        self.assertEqual(m.r['FieldRole'], 1)
        m.choose('storm_conditions1111', 1)
        self.assertEqual(m.r['FieldData'], 24)
        m.choose('volcano_join')
        self.assertEqual(m.scene, scene('volcano_pending1111'))
        m.choose('volcano_pending1111')
        self.assertEqual(m.scene, scene('storm_record'))
        m.age += 1
        m.choose('storm_record')
        self.assertEqual(m.bank, 1000)
        m = self.model(FieldRole=1)
        m.choose('storm_survey', 1)
        m.choose('storm_conditions1111', 2)
        self.assertEqual(m.r['FieldReportReady'], 0)
        m.choose('storm_record')
        self.assertEqual(m.bank, 1000)

    def test_native_injury_and_prison_reject_field_work(self):
        m = self.model(FieldRole=1)
        m.choose('storm_survey', 3)
        self.assertIn(14, m.native)
        self.assertEqual(m.r['FieldInjuries'], 1)
        self.assertEqual(m.r['FieldReportReady'], 0)
        m = self.model(FieldRole=1, NativeInPrison1105=1)
        m.choose('storm_survey', 1)
        self.assertEqual(m.scene, scene('field_prison1111'))
        self.assertEqual(m.r['FieldSurveyStage1111'], 0)

    def test_annual_copies_and_no_duplicate_rows(self):
        live = {r['ScenarioID']: r for r in self.author.rows}
        self.assertEqual(len(live), len(self.author.rows))
        for name, value in self.author.assets.items():
            if not value.startswith('ScenarioID,'):
                continue
            rows = list(csv.DictReader(io.StringIO(value)))
            self.assertEqual(len(value.splitlines()), len(rows) + 1)
            for row in rows:
                key = row['ScenarioID']
                source = live.get(key) if key in self.author.playable_action_ids else None
                if key.startswith(scene('annual_prison1110_')):
                    source = live[key.replace('annual_prison1110_', 'prison_annual1110_')]
                if source is None:
                    continue
                for field in ['Title', 'Body'] + [f'Choice{i}_{suffix}' for i in range(1, 5) for suffix in ['Text', 'RouteTo', 'AdvancedLogic']]:
                    self.assertEqual(row[field], source[field], (name, key, field))


if __name__ == '__main__':
    unittest.main()
