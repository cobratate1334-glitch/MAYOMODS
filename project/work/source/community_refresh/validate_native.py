"""Run portrait, menu-age, allowance and story boundaries in emitted ARM64.

Mip generation and Unity/managed APIs are explicit models; these are not phone
rendering tests. The previous native copy supplies the portrait negative control.
"""
import csv
import hashlib
import io
import json
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(SOURCE), str(SOURCE / 'social_roblox'), str(SOURCE / 'native_v29')]
from native_v55 import test_native55 as prior
from social_roblox.test_native import Machine as RobloxMachine
from social_roblox import roblox_content
from test_native import X


class Machine(RobloxMachine):
    def __init__(self, raw, bias, schema=None):
        base = json.loads((prior.ROOT / 'assets.json').read_text())
        self.overlay = roblox_content.build(base)
        rows = csv.DictReader(io.StringIO(self.overlay[roblox_content.DEFAULTS]))
        schema = schema or {r['key']: r for r in rows}
        super().__init__(raw, bias, schema)
        rows = csv.DictReader(io.StringIO(self.overlay['genesis_v18_defaults_gameplay52']))
        self.schema55['gameplay52'] = {r['key']: r for r in rows}
        self.ctx('gameplay52')
        for key, r in self.schema55['gameplay52'].items():
            self.props['gameplay52'].setdefault(key, int(r['value']) if r['type'] == 'int' else r['value'])
        self.apply_flags = []
        self.smallest_mip = 0

    def mock(self, u, pc, size, data):
        if pc - self.bias == 0x3059f90:
            a = [u.reg_read(x) for x in X[:3]]
            if a[0] == self.contexts.get('life_v18') and self.str(a[1]) == 'PortraitCacheAge':
                value = a[2] & 0xffffffff
                value = value if value < 0x80000000 else value - 0x100000000
                self.props['life_v18']['PortraitCacheAge'] = max(-1, min(999, value))
                self.finish_api(u.reg_read(X[30]), 1)
                return
        if pc - self.bias == 0x555a4a8:
            a = [u.reg_read(x) for x in X[:4]]
            self.apply_flags.append(a[1:])
            assert a[1] in [0, 1] and a[2:] == [0, 0]
            # A fresh mip-chain texture begins with uninitialized lower levels.
            # Apply(updateMipmaps=true) builds them from uploaded mip-zero data.
            self.smallest_mip = self.cpu_pixels[0] if a[1] and self.cpu_pixels else 0
            self.finish_api(u.reg_read(X[30]), 0)
            return
        return super().mock(u, pc, size, data)


def validate(binary, previous, root):
    prior.ROOT = Path(root)
    raw, old = Path(binary).read_bytes(), Path(previous).read_bytes()
    cases = []

    def check(value, message):
        assert value, message
        cases.append(message)

    for bias in [0, 0x1000000000]:
        m = Machine(raw, bias)
        old_m = Machine(old, bias)
        cpu = next(r for r in m.d['hooks'] if r['name'] == 'v55_resize_readable_portrait_on_cpu')['stub']
        old_m.execute42(cpu, {1: old_m.texture55, 2: 3, 3: 2})
        check(old_m.apply_flags == [[0, 0, 0]] and old_m.smallest_mip == 0,
              'negative control: previous resize leaves reduced mip data uninitialized')
        m.execute42(cpu, {1: m.texture55, 2: 3, 3: 2})
        check(m.apply_flags == [[1, 0, 0]] and m.smallest_mip != 0,
              'repaired CPU copy regenerates reduced levels and retains CPU storage')
        from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN
        ins = next(Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN).disasm(m.load(0x2f4cc68, 4), 0x2f4cc68))
        check(ins.mnemonic == 'mov' and ins.op_str == 'w2, wzr',
              'centered header image does not discard readable pixels')
        m.q(m.face + 16, m.managed('hero-age-portrait'))
        m.ctx('life_v18')
        m.props['life_v18']['PortraitCacheAge'] = -1
        m.w(m.hero + 32, 9)
        before_cache = len(m.cache_removed)
        m.routine42('refresh_current_hero_portrait_age', {19: m.emoji})
        check(len(m.cache_removed) == before_cache + 1 and m.props['life_v18']['PortraitCacheAge'] == 9,
              'first age-specific header request invalidates only the actual hero cache ID')
        m.routine42('refresh_current_hero_portrait_age', {19: m.emoji})
        check(len(m.cache_removed) == before_cache + 1, 'repeated header reads at the same age reuse the cache')
        m.w(m.hero + 32, 18)
        m.routine42('refresh_current_hero_portrait_age', {19: m.emoji})
        check(len(m.cache_removed) == before_cache + 2, 'age-up invalidates the stale hero portrait before its next lookup')
        npc = m.alloc()
        m.q(npc + 48, m.face)
        m.routine42('refresh_current_hero_portrait_age', {19: npc})
        check(len(m.cache_removed) == before_cache + 2, 'NPC reads do not invalidate the hero portrait')
        for age in [0, 4, 12, 13, 17, 18, 25]:
            m.w(m.hero + 32, age)
            for owner in ['crime_entry54_61', 'crime_entry54_62', 'crime_entry54_63', 'crime_entry54_64', 'roblox_social']:
                container, item = m.alloc(64), m.alloc(512)
                m.q(container + 16, m.managed(owner))
                m.hook42('refresh_custom_menu_age_requirements', {19: container, 21: item})
                disabled = m.u.mem_read(item + 0xd0, 1)[0]
                check(disabled == int(age < (13 if owner == 'roblox_social' else 18)),
                      f'native menu availability {owner} at age {age}')
        # Exercise action handlers as well as visibility. Opening a disabled
        # crime by an old route must never charge money or award crew effects.
        for age in [0, 4, 13, 17]:
            m.w(m.hero + 32, age)
            for action in [61, 62, 63, 64]:
                q = m.props['gameplay52']
                q.update(ActionsUsed=0, LastAge=age, Heat=30, CrewTrust=50)
                bank = m.balance
                m.activity(action)
                check(m.balance == bank and q['ActionsUsed'] == 0 and q['Heat'] == 30 and q['CrewTrust'] == 50,
                      f'underage direct crime callback {action} at age {age} has no economic effects')

        p = m.props['roblox_social']
        m.w(m.hero + 32, 14)
        p.update(SchemaVersion=2, CalendarAge=13, Robux=100, Club=1,
                 DailyRobux=15, DaysRemaining=30, Lifetime=0, Hat1=1)
        before = len(m.native_journal)
        m.routine42('refresh_roblox_calendar')
        check(p['Robux'] == 550 and p['DaysRemaining'] == 0 and p['Club'] == 0,
              'monthly membership credits only its actual 30-day term then expires')
        check(p['PlaceLimit'] == 1 and p['Hat1'] == 1 and len(m.native_journal) == before + 1,
              'expired membership retains owned hat and logs the allowance once')
        m.routine42('refresh_roblox_calendar')
        check(p['Robux'] == 550 and len(m.native_journal) == before + 1,
              'reopening account cannot duplicate daily allowance')
        m.w(m.hero + 32, 13)
        m.routine42('refresh_roblox_calendar')
        check(p['Robux'] == 550 and p['CalendarAge'] == 14,
              'rewinding age without restoring state cannot duplicate allowance')
        p.update(CalendarAge=14, Club=3, DailyRobux=60, DaysRemaining=0, Lifetime=1)
        m.w(m.hero + 32, 16)
        m.routine42('refresh_roblox_calendar')
        check(p['Robux'] == 550 + 2 * 365 * 60 and p['Club'] == 3,
              'lifetime membership pays elapsed years without expiring')
        m.w(m.hero + 32, 25)
        p.update(SchemaVersion=0, CalendarAge=-1, Robux=645, Club=2, ClubAge=25,
                 Lifetime=0, DaysRemaining=0, DailyRobux=0, Games=3, PlaceLimit=0, GroupLimit=0)
        m.routine42('refresh_roblox_calendar')
        check(p['Robux'] == 645 and p['DaysRemaining'] == 365 and p['DailyRobux'] == 35
              and p['PlaceLimit'] == 25 and p['ActivePlaces'] == 3 and p['SigningBonusGranted'] == 1,
              'existing club and place record migrate without another signing bonus')

        p['AvatarImage'] = 'mayomods_refresh/roblox/11844853'
        hook = next(r for r in m.d['hooks'] if r['name'] == 'refresh_classic_club_panel_images')
        m.execute42(hook['stub'], {0: m.managed('<GFC.roblox_social.AvatarImage>')})
        check(m.resources55[-1] == p['AvatarImage'], 'actual Turbo artwork resolves with Texture2D type')
        q = m.props['gameplay52']
        q.update(CaseNumber=0, CaseAge=0)
        m.routine42('refresh_initialize_parish_story')
        check(q['CaseNumber'] == 1 and q['CaseAge'] == -1,
              'old saves initialize the first parish case without resetting progress')
        q.update(StoryJournalSequence=1, StoryJournalLogged=0, StoryJournalMessage='I organized winter pantry volunteers.')
        prop = m.alloc()
        m.q(prop + 24, m.managed('StoryJournalSequence'))
        args = {0: 1, 19: prop, 21: m.contexts['gameplay52']}
        before = len(m.native_journal)
        m.routine42('refresh_log_parish_story', args)
        m.routine42('refresh_log_parish_story', args)
        check(len(m.native_journal) == before + 1 and q['StoryJournalLogged'] == 1,
              'parish case appends one contextual LifeLog entry despite repeated callback')
        print('Refresh portrait, ages, allowances and parish journal passed at ' + hex(bias), flush=True)
    return dict(passed=True, checks=len(cases), cases=cases,
                binary_sha256=hashlib.sha256(raw).hexdigest(), physical_phone_tested=False,
                Unity_rendering_tested=False, mip_generation_modeled=True, ART_tested=False)


def retained(binary, root):
    # Historical tests assert pixel output and native boundaries; use the
    # updated Apply model for the deliberately corrected mip-generation flag.
    prior.ROOT = Path(root)
    prior.Machine = Machine
    prior.validate(binary)
    from native_v53 import test_native53 as nav
    from native_v54 import test_native54 as integration
    nav.ROOT = integration.ROOT = Path(root)
    nav.Machine = integration.Machine = Machine
    nav.validate(binary)
    (Path(root) / 'retained53_validation55.json').write_bytes((Path(root) / 'native53_validation.json').read_bytes())
    integration.validate(binary)
    (Path(root) / 'retained54_validation55.json').write_bytes((Path(root) / 'native54_validation.json').read_bytes())


if __name__ == '__main__':
    report = validate(sys.argv[1], sys.argv[2], sys.argv[3])
    Path(sys.argv[4]).write_text(json.dumps(report, indent=2) + '\n')
    print({'passed': True, 'checks': report['checks']}, flush=True)
    if '--retained' in sys.argv:
        retained(sys.argv[1], sys.argv[3])
