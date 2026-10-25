"""Repair saved eye-trait priority and enable bundled local feature gates.

Pinned to released v49. No new ELF load, heap state, purchase record, receipt,
billing callback, or Android permission is introduced.
"""
import copy, hashlib, json, os, struct, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent
sys.path[:0] = [str(SOURCE/'native_v49'), str(SOURCE), str(SOURCE/'native_v29')]
from native_v49.patch_native49 import Patch as Previous
from native_hooks import Builder, h

BASE_SHA = 'd17f9a0b9c68eb67226640d1a92ad1b834edfeec352408cebfc41d966e78959a'
ENUM_NAMES = ['SPECIAL_JOB_TYPE', 'EXPANSION_PACK_TYPE', 'DARKLY_ITEM_TYPE', 'BUNDLE_TYPE', 'IAP_TYPE']

class Patch(Previous):
    def __init__(self, raw):
        Builder.__init__(self, raw)
        assert hashlib.sha256(raw).hexdigest() == BASE_SHA
        self.base = json.loads((SOURCE/'native_v49/native_hooks.json').read_text())
        self.manifest = copy.deepcopy(self.base)
        self.old = {r['name']:r for r in self.base['hooks']+self.base['routines']}
        self.rxoff, self.rxva, size = self.base['v49_new_rx']
        self.tail = next(s for s in self.loads if s['p_vaddr'] == self.rxva)
        assert self.tail['p_flags'] == 5 and size == 0x100000
        self.cursor = self.code_start = self.rxva + 0x30000
        self.strings_va = self.rxva + 0xd0000
        assert self.base['v49_new_code_range'][1] < self.cursor
        assert max(v+len(s.encode())+1 for s,v in self.base['strings'].items()) < self.strings_va
        self.string_cursor = self.strings_va
        self.strings = copy.deepcopy(self.base['strings'])
        self.states = copy.deepcopy(self.base['states'])
        self.routines = []; self.hooks = []; self.changed = []; self.serial = 0
        self.access = []

    def redirect_query(self, method, target, kind):
        site = method['va']; p = self.off(site)
        assert not any(r[0] == site for r in self.changed)
        original = bytes(self.blob[p:p+4])
        self.blob[p:p+4] = h.asm(f'b {target:#x}', site)
        self.changed.append([site, 4, method['type']+'.'+method['name']])
        self.access.append(dict(name=method['name'], site=site, target=target,
                                kind=kind, original_hex=original.hex()))

    def finish50(self):
        assert self.cursor < self.strings_va and self.string_cursor < self.rxva+0x100000
        for s, va in self.strings.items():
            if s in self.base['strings']: continue
            data = s.encode()+b'\0'; p = self.off(va)
            assert self.blob[p:p+len(data)] == b'\0'*len(data)
            self.blob[p:p+len(data)] = data
            self.changed.append([va, len(data), 'literal'])
        assert len(self.blob) == len(self.native)
        sites = {r['site'] for r in self.hooks}
        self.manifest['hooks'] = [r for r in self.manifest['hooks'] if r['site'] not in sites]+self.hooks
        self.manifest['routines'] += self.routines
        self.manifest.update(binary_sha256=hashlib.sha256(self.blob).hexdigest(),
            base_v49_sha256=BASE_SHA, strings=self.strings, states=self.states,
            v50_new_code_range=[self.code_start,self.cursor], v50_changed_ranges=self.changed,
            v50_access_queries=self.access, v50_no_segment_growth=True,
            v50_eye_priority='Last explicit selection: genetic eyes or manual eye colours')
        (ROOT/'native_hooks.json').write_text(json.dumps(self.manifest,indent=2)+'\n')
        return bytes(self.blob)

def eyes(b):
    # Normalize existing saves and every cache/serialization entry. Only the
    # current hero is allowed to change the player's appearance properties.
    s = 'cbz x0,finish\nmov x27,x0\n'+h.load_game()+'\n'
    s += 'ldr x8,[x8,#0x28]\ncbz x8,finish\nldr x8,[x8,#0x80]\ncbz x8,finish\nldr x8,[x8,#0x30]\ncmp x8,x27\nb.ne finish\n'
    s += b.ctx('life_v18')+b.get('RareAppearance21','w19')
    s += 'cmp w19,#5\nb.eq genetic50_selected\ncmp w19,#12\nb.eq genetic50_selected\ncmp w19,#13\nb.ne finish\ngenetic50_selected:\n'
    s += b.ctx('custom49')
    for key in ['LeftEye','RightEye']:
        s += b.get(key,'w19')+f'cbz w19,eye50_keep_{key}\n'+b.set(key,0)+f'eye50_keep_{key}:\n'
    s += 'b finish'
    b.chain('v50_resolve_selected_genetic_eyes','v42_apply_current_hero_appearance_v49',s)
    # Explicit eye-colour Apply is the converse action. It leaves independent
    # skin marks, albinism, hair and accessories intact. Back never enters it.
    s = 'sub w19,w0,#600\ncmp w19,#6\nb.ls manual50_selected\nsub w19,w0,#700\ncmp w19,#6\nb.hi finish\nmanual50_selected:\n'
    s += b.ctx('life_v18')+b.get('RareAppearance21','w19')
    s += 'cmp w19,#5\nb.eq manual50_clear\ncmp w19,#12\nb.eq manual50_clear\ncmp w19,#13\nb.ne finish\nmanual50_clear:\n'
    s += b.set('RareAppearance21',0)+b.text('RareAppearanceName21','No rare appearance trait')+'b finish'
    b.chain('v50_explicit_eye_colour_selection','v49_apply_appearance_command',s)

def local_access(b):
    methods = json.loads((SOURCE.parents[1]/'analysis/game_methods31.json').read_text())
    meta = (SOURCE.parents[1]/'global-metadata.dat').read_bytes()
    enums = json.loads((ROOT/'product_enums.json').read_text())
    enums = {k:enums[k] for k in ENUM_NAMES}
    (ROOT/'product_enums.json').write_text(json.dumps(enums,indent=2)+'\n')
    allow = {k:sorted(v for v in values.values() if v>0) for k,values in enums.items()}
    # Consumables and live-service inventory remain owned by their real
    # transaction/server flows. This release grants permanent bundled access.
    allow['IAP_TYPE'] = [v for k,v in enums['IAP_TYPE'].items() if v>0 and not k.startswith('CONSUMABLE_')]
    true = b.add_code('v50_local_nonconsumable_access','cmp x0,#0\ncset w0,ne\nret')
    false = b.add_code('v50_no_ad_eligibility','mov w0,wzr\nret')
    targets = {}
    for kind, values in allow.items():
        source='cbz x0,local50_false\n'
        for value in values: source+=f'cmp w1,#{value}\nb.eq local50_true\n'
        source+='local50_false:\nmov w0,wzr\nret\nlocal50_true:\nmov w0,#1\nret'
        targets[kind] = b.add_code('v50_local_access_'+kind.lower(), source)
    enums_by_name = {
        'DoesUserOwnDarklyItem':'DARKLY_ITEM_TYPE',
        'DoesUserOwnSpecialCareer':'SPECIAL_JOB_TYPE','DoesUserHaveAccessToSpecialCareer':'SPECIAL_JOB_TYPE',
        'DoesUserOwnExpansionPack':'EXPANSION_PACK_TYPE','DoesUserHaveAccessToExpansionPack':'EXPANSION_PACK_TYPE',
        'DoesUserOwnBundle':'BUNDLE_TYPE','DoesUserHaveAccessToBundle':'BUNDLE_TYPE','OwnsIAP':'IAP_TYPE'}
    booleans = {'DoesUserOwnBitizenship','DoesUserOwnBossMode','DoesUserOwnGodMode',
        'DoesUserOwnBitizenshipAndGodMode','DoesUserOwnBitizenshipGodMode',
        'DoesUserOwnAtLeastOneSpecialCareer','UserOwnsStarter1Bundle','UserOwnsStarter2Bundle'}
    ads = {'CanHaveAds','HasInterstitialAds','DoesUserHaveBannerAds','DoesUserHaveRewardedVideoAds',
        'DoesUserHaveAnyAds','DoesUserHaveNewLifeInterstitialAds','DoesUserHavePeriodicPostScenarioInterstitialAds',
        'ShouldInsertBitizenshipPaywallBeforeGenerationLife'}
    for m in methods:
        if m['type']!='MonetizationVars' or not m['va']: continue
        name=m['name']; kind=None
        if name in enums_by_name: kind=enums_by_name[name]; target=targets[kind]
        elif name in ads: kind='ads_false'; target=false
        elif name in booleans or name.startswith('UserOwnsAtLeastOneOfThe') or (name.startswith('DoesUserHaveAccessTo') and name not in {'DoesUserHaveAccessToSpecialTalent','DoesUserHaveAccessToAtLeastOneSpecialTalent'}):
            kind='local_bool'; target=true
        if kind:
            flags,_,_,count=struct.unpack_from('<4H',meta,6323900+m['index']*30+22)
            assert not flags&0x10, (name,'expected instance receiver')
            assert count == (1 if kind in targets else 0), (name,count)
            b.redirect_query(m,target,kind)
    (ROOT/'local_access_policy.json').write_text(json.dumps(dict(allowlists=allow,
        no_purchase_record_writes=True, no_billing_callback_hooks=True,
        gameplay_and_age_requirements_preserved=True,consumable_inventory_unchanged=True),indent=2)+'\n')

def patch(raw):
    b=Patch(raw); eyes(b); local_access(b); return b.finish50()

if __name__=='__main__':
    output=Path(sys.argv[2]); data=patch(Path(sys.argv[1]).read_bytes())
    partial=output.with_suffix('.partial')
    with partial.open('wb') as f: f.write(data); f.flush(); os.fsync(f.fileno())
    partial.replace(output)
    print(json.dumps(dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())))
