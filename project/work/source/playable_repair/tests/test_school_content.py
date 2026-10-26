"""School progression and stale-choice checks; route model, not phone Unity.

Run with SCHOOL_BASE_ASSETS pointing to the private exact 1110 asset extraction.
No uploaded logs or game APK are stored in this source tree.
"""
import copy
import csv
import io
import json
import os
from pathlib import Path
import re
import unittest

from life_repair.content import Author
from life_rework.content import scene, csv_text
from life_rework.validate_content import Model as RouteModel
from social_roblox.test_content import Model as OriginalModel
from playable_repair.school_content import build, refresh_annual_copies, ART, HOME, MANUAL_FILTER


BASE_PATH = Path(os.environ.get('SCHOOL_BASE_ASSETS', '/workspace/build_work/playable-repair/base_assets.json'))


class Model(RouteModel):
    def __init__(self, assets, age=13, student=True, peer=True):
        OriginalModel.__init__(self, age)
        self.assets.update(assets)
        self.rows = {}
        for value in self.assets.values():
            if value.startswith('ScenarioID,'):
                # Use the main sheet as the source in this route model.  Annual
                # copy equality is checked independently below.
                self.rows.update({r['ScenarioID']: r for r in csv.DictReader(io.StringIO(value))})
        self.rows.update({r['ScenarioID']: r for r in csv.DictReader(io.StringIO(assets['genesis_life_rework']))})
        defs = {r['key']: r for r in csv.DictReader(io.StringIO(assets['genesis_rework_defaults']))}
        self.schemas['life_rework'] = defs
        self.props['life_rework'] = {k: int(r['value']) if r['type'] == 'int' else r['value'] for k, r in defs.items()}
        self.r.update(SchoolEligible=int(student), SchoolPeerPresent1105=int(peer), SchoolPeer1105='Jordan', Roll=0)
        self.native = []


class SchoolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(BASE_PATH.read_text())
        cls.author = Author(cls.base)
        build(cls.author, cls.base)
        refresh_annual_copies(cls.author, cls.base)
        cls.assets = {**cls.base, **cls.author.assets,
                      'genesis_life_rework': csv_text(cls.author.rows, list(cls.author.header)),
                      'genesis_rework_defaults': csv_text(cls.author.schema)}

    def model(self, *args, **kwargs):
        return Model(self.assets, *args, **kwargs)

    def test_single_hub_with_distinct_supplied_icons(self):
        root = json.loads(self.assets['genesis_v18_school52'])
        rows = root.get('Items', root.get('ListItems'))
        self.assertEqual([r['Title'] for r in rows], ['Exams', 'Bullying', 'Classmates', 'Clubs', 'School sports', 'My year'])
        self.assertEqual(len({r['Icon'] for r in rows}), 6)
        self.assertTrue(all(r['Icon'].startswith(ART) for r in rows))
        self.assertTrue(all(len(r['SecondLine']) <= 35 for r in rows))
        self.assertEqual(len({r['ScenarioID'] for r in self.author.rows}), len(self.author.rows))

    def test_annual_manual_copies_match_live_choices(self):
        live = {r['ScenarioID']: r for r in self.author.rows}
        rows = list(csv.DictReader(io.StringIO(self.assets['genesis_rework_annual1105'])))
        seen = set()
        for old in rows:
            key = old['ScenarioID']
            source = live.get(key) if key in self.author.playable_school_ids else None
            if key.startswith(scene('annual_school1110_')):
                source = live[key.replace('annual_school1110_', 'school_story1110_')]
            if source is None:
                continue
            seen.add(source['ScenarioID'])
            for col in ['Title', 'Body', 'EmojiString', 'BigImageString'] + [f'Choice{i}_{suffix}' for i in range(1, 5) for suffix in ['Text', 'RouteTo', 'AdvancedLogic']]:
                self.assertEqual(old[col], source[col], (key, col))
            if old.get('IsAgeUpScenario', '').lower() != 'true':
                self.assertEqual(old['Filter'], MANUAL_FILTER)
        self.assertTrue(self.author.playable_school_ids.issubset(seen))

    def test_no_church_icons_and_every_route_is_registered(self):
        m = self.model()
        manifest = json.loads(next((Path(__file__).parents[1] / 'inputs' / 'school').rglob('manifest.json')).read_text())
        records = manifest if isinstance(manifest, list) else manifest.get('assets', manifest.get('items', []))
        # The supplied archive schema is checked by the asset importer too.
        known = {r['id'] for r in records}
        for row in self.author.rows:
            if row['ScenarioID'] not in self.author.playable_school_ids:
                continue
            for field in ['EmojiString', 'BigImageString']:
                if row[field]:
                    self.assertTrue(row[field].startswith(ART), (row['ScenarioID'], field))
                    self.assertIn(row[field][len(ART):], known)
            for index in range(1, 5):
                label = row[f'Choice{index}_Text']
                if not label:
                    continue
                advanced = row[f'Choice{index}_AdvancedLogic']
                tree = json.loads(advanced) if advanced else None
                routes = [row[f'Choice{index}_RouteTo']] if tree is None else [c['then']['route_options'][0]['route_to'] for c in tree['cases']] + [tree['else_when_no_matches']['route_options'][0]['route_to']]
                if tree:
                    for case in tree['cases']:
                        m.condition(case['if'])
                for route in routes:
                    self.assertIsInstance(route, str)
                    for part in m.split(route):
                        if part.startswith('scenario.'):
                            self.assertIn(part, m.rows)
                        if part.startswith('BP_SHOW_LIST='):
                            self.assertIn(part.split('=', 1)[1], self.assets)
                        if part.startswith('BP_GFC_'):
                            owner, field = part.split('=', 1)[1].split(':', 2)[:2]
                            self.assertIn(field, m.schemas[owner])

    def test_infants_and_nonstudents_cannot_get_school_rewards(self):
        for m in [self.model(age=2), self.model(student=False)]:
            before = copy.deepcopy(m.r)
            m.choose('school_study', 1)
            self.assertEqual(m.scene, scene('school_closed'))
            self.assertEqual(m.r, before)
            m.choose('school_story1110_3', 3)
            self.assertEqual(m.scene, scene('school_closed'))
            self.assertEqual(m.r, before)
            m.choose('school_cheer_start1111')
            self.assertEqual(m.scene, scene('school_closed'))

    def test_bully_teacher_followup_has_progress_and_cannot_replay(self):
        m = self.model()
        m.choose('school_bully_entry')
        self.assertEqual(m.scene, scene('school_bully'))
        m.choose('school_bully', 1)
        self.assertEqual(m.r['SchoolBullyStage'], 2)
        m.choose('school_report1111_result')
        self.assertEqual(m.scene, scene('school_bully_teacher1111'))
        before = m.r['SchoolSafety']
        m.choose('school_bully_teacher1111', 1)
        self.assertEqual(m.r['SchoolBullyStage'], 4)
        self.assertGreater(m.r['SchoolSafety'], before)
        saved = copy.deepcopy(m.r)
        m.choose('school_bully_teacher1111', 1)
        self.assertEqual(m.r, saved)
        self.assertEqual(m.scene, scene('school_bully_entry'))
        self.assertGreaterEqual(m.r['JournalSequence'], 2)

    def test_bully_friend_can_follow_up_with_teacher(self):
        m = self.model()
        m.choose('school_bully_entry')
        m.choose('school_bully', 2)
        self.assertEqual(m.r['SchoolBullyStage'], 1)
        m.choose('school_stand1111_result')
        m.choose('school_bully_friend1111', 2)
        self.assertEqual(m.r['SchoolBullyStage'], 2)
        self.assertEqual(m.scene, scene('school_report1111_result'))

    def test_fight_routes_to_original_bridge_and_suspension_blocks_it(self):
        m = self.model()
        m.choose('school_bully', 3)
        self.assertEqual(m.r['SchoolFightReason1110'], 1)
        m.choose('school_fight1106', 1)
        self.assertEqual(m.r['SchoolNativeFight1106'], 1)
        m = self.model()
        m.r['SchoolSuspendedAge1110'] = m.age
        m.choose('school_fight1106', 1)
        self.assertEqual(m.r['SchoolNativeFight1106'], 0)
        self.assertEqual(m.scene, scene('school_suspended1110'))
        m = self.model(peer=False)
        m.choose('school_fight1106', 1)
        self.assertEqual(m.scene, scene('school_no_fight1106'))

    def test_current_peer_relationship_command_is_guarded(self):
        m = self.model()
        m.choose('school_peer1105', 1)
        self.assertIn(112, m.native)
        self.assertGreater(m.r['SchoolPeerTrust1105'], 40)
        self.assertIn('Jordan', m.rows[m.scene]['Body'].replace('<GFC.life_rework.SchoolPeer1105>', m.r['SchoolPeer1105']))
        m = self.model(peer=False)
        before = copy.deepcopy(m.r)
        m.choose('school_peer1105', 1)
        self.assertEqual(m.scene, scene('school_no_peer1111'))
        self.assertEqual(m.r, before)

    def test_project_choices_change_grade_and_no_stale_reward(self):
        m = self.model()
        m.choose('school_project1105')
        m.choose('school_project_plan1111', 1)
        m.choose('school_project_present1111', 1)
        self.assertIn(611, m.native)
        self.assertEqual(m.r['SchoolProjectStep1111'], 3)
        snapshot = copy.deepcopy(m.r)
        m.choose('school_project_present1111', 1)
        self.assertEqual(m.r, snapshot)
        m = self.model()
        m.choose('school_project1105')
        m.choose('school_project_plan1111', 3)
        m.choose('school_project_present1111', 2)
        self.assertIn(612, m.native)
        self.assertEqual(m.r['SchoolDiscipline1110'], 1)

    def test_exam_pause_keeps_answers_and_last_question_resumes_at_mark(self):
        m = self.model(age=9)
        m.choose('exam_start1105')
        self.assertEqual(m.scene, scene('exam_1_1105'))
        m.choose('exam_1_1105', 1)
        first = m.r['ExamPoints1105']
        m.choose('exam_2_1105', 4)
        m.choose('exam_pause1111')
        self.assertEqual(m.scene, scene('exam_2_1105'))
        self.assertEqual(m.r['ExamPoints1105'], first)
        m.choose('exam_2_1105', 1)
        m.choose('exam_3_1105', 1)
        self.assertEqual(m.r['ExamStep1105'], 3)
        m.choose('exam_start1105')
        self.assertEqual(m.scene, scene('exam_mark1105'))
        m.choose('exam_mark1105')
        self.assertEqual(m.r['ExamAge1105'], 9)
        self.assertIn(m.native[-1], [11, 12])
        after = copy.deepcopy(m.r)
        m.choose('exam_mark1105')
        self.assertEqual(m.r, after)
        m.choose('school_exam')
        self.assertEqual(m.scene, scene('exam_done1105'))

    def test_exam_chooses_age_forms_and_old_year_choices_are_rejected(self):
        for age, roll, form in [(7, 0, 0), (7, 80, 1), (15, 0, 2), (15, 80, 3), (22, 0, 4), (22, 80, 5)]:
            m = self.model(age=age)
            m.r['Roll'] = roll
            m.choose('exam_start1105')
            self.assertEqual(m.r['ExamForm1105'], form)
            before = copy.deepcopy(m.r)
            wrong = 'exam_1_form1_1105' if form == 0 else 'exam_1_1105'
            m.choose(wrong)
            self.assertEqual(m.r, before)
            m.age += 1
            m.choose('exam_1_1105')
            self.assertEqual(m.scene, scene('exam_start1105'))
            self.assertEqual(m.r, before)

    def test_cheer_trial_is_playable_and_resumes_at_every_step(self):
        m = self.model()
        m.choose('school_cheer_start1111')
        for step in range(3):
            self.assertEqual(m.scene, scene('school_cheer_round' + str(step) + '1111'))
            before = copy.deepcopy(m.r)
            m.choose('school_cheer_start1111')
            self.assertEqual(m.r, before)
            m.choose('school_cheer_round' + str(step) + '1111', 1)
        m.choose('school_cheer_start1111')
        self.assertEqual(m.scene, scene('school_cheer_finish1111'))
        m.choose('school_cheer_finish1111')
        self.assertIn(614, m.native)
        self.assertEqual(m.r['SchoolCheerDoneAge1111'], m.age)
        after = copy.deepcopy(m.r)
        m.choose('school_cheer_finish1111')
        self.assertEqual(m.r, after)
        m = self.model(age=8)
        m.choose('school_cheer_start1111')
        self.assertEqual(m.scene, scene('school_cheer_young1111'))

    def test_match_requires_current_year_practice_and_has_loss_path(self):
        m = self.model()
        m.r.update(SchoolTeamPractice1110=90, SchoolTeam1110Used=4, SchoolTeam1110Age=12, SchoolPracticeAge1111=12)
        m.choose('school_match_start1111')
        self.assertEqual(m.scene, scene('school_match_train1111'))
        m.choose('school_practice1111', 1)
        m.choose('school_practice1111', 1)
        self.assertEqual(m.r['SchoolTeam1110Used'], 2)
        m.choose('school_match_start1111')
        for step in range(3):
            m.choose('school_match_round' + str(step) + '1111', 2)
        m.choose('school_match_start1111')
        self.assertEqual(m.scene, scene('school_match_finish1111'))
        m.choose('school_match_finish1111')
        self.assertEqual(m.scene, scene('school_match_loss1111_result'))
        self.assertEqual(m.r['SchoolMatchDoneAge1111'], m.age)
        self.assertIn('loses', m.rows[m.scene]['Body'])

    def test_session_limit_stops_reward_and_logs_each_completed_action(self):
        m = self.model()
        for _ in range(12):
            m.choose('school_social1110', 1)
        self.assertEqual(m.r['JournalSequence'], 12)
        self.assertEqual(m.r['SchoolSession1111Used'], 12)
        snapshot = copy.deepcopy(m.r)
        m.choose('school_social1110', 1)
        self.assertEqual(m.scene, scene('school_session_full1111'))
        self.assertEqual(m.r, snapshot)
        m.age += 1
        m.choose('school_social1110', 1)
        self.assertEqual(m.r['SchoolSession1111Used'], 1)
        self.assertEqual(m.r['JournalSequence'], 13)

    def test_all_csv_records_remain_one_physical_line(self):
        for value in self.author.assets.values():
            if value.startswith('ScenarioID,'):
                self.assertEqual(len(value.splitlines()), len(list(csv.DictReader(io.StringIO(value)))) + 1)


if __name__ == '__main__':
    unittest.main()
