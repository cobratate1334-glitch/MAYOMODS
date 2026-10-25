"""Repair map return and fresh Custom Life entry on the exact delivered v32.

RevealDarkly selects darklies[Count-1], not currentDarklyIndex. A cached
Country/City subgroup can therefore be revealed above the retained root.
Restore the verified root explicitly, settle interrupted slides, and discard
obsolete UI at both stock New Life entry points. Keep Start/birth intact.
"""
import copy, hashlib, json, re, sys
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
sys.path.insert(0, str(ROOT.parent / 'native_v29'))
from native_hooks import Builder, h
from native_newlife24 import FIELDS, show_list
from native_ui21 import checkpoint
from native_v31.patch_native31 import LABELS, OPTIONS

BASE_SHA = '1ca76ea9c4b7e187a9845ff2fb2361544bbcccf1e681ebe59b89fa2a87d6060f'

class Patch(Builder):
    def __init__(self, native):
        super().__init__(native)
        assert hashlib.sha256(native).hexdigest() == BASE_SHA
        self.base = json.loads((ROOT.parent / 'native_v32/native_hooks.json').read_text())
        self.manifest = copy.deepcopy(self.base)
        self.tail = next(s for s in self.loads if s['p_vaddr'] == self.base['segment_va'])
        self.cursor = (max(r['stub'] + r['length'] for r in self.base['hooks'] + self.base['routines']) + 15) & ~15
        self.code_start = self.cursor
        self.strings = copy.deepcopy(self.base['strings'])
        self.strings_va = min(self.strings.values())
        self.states = copy.deepcopy(self.base['states'])
        self.newlife24 = self.states['newlife24']['va']
        self.newlife31 = self.states['newlife31']['va']
        self.routines = []; self.hooks = []; self.changed = []
        self.old = {r['name']: r for r in self.base['routines'] + self.base['hooks']}
        self.trace23 = self.old['persist_new_life_checkpoint23']['stub']
        self.clear31 = self.old['newlife31_release_ui']['stub']

    def add_code(self, name, source):
        source = re.sub(r'\badr (x\d+),\s*(0x[0-9a-f]+)', lambda m: f'adrp {m[1]}, {int(m[2],16)&~4095:#x}\nadd {m[1]}, {m[1]}, #{int(m[2],16)&4095}', source)
        va = self.cursor; code = h.asm(source, va); off = self.off(va)
        assert va + len(code) < self.strings_va
        assert self.blob[off:off+len(code)] == b'\0' * len(code)
        self.blob[off:off+len(code)] = code
        self.routines.append(dict(name=name, stub=va, length=len(code), source=source))
        self.cursor = (va + len(code) + 15) & ~15
        return va

    def routine(self, name, body):
        return self.add_code(name, h.save() + '\n' + body + '\nfinish:\n' + h.restore() + '\nret')

    def update_record(self, name, source):
        record = next(r for r in self.manifest['hooks'] + self.manifest['routines'] if r['name'] == name)
        before = h.asm(record['source'], record['stub']); after = h.asm(source, record['stub'])
        off = self.off(record['stub'])
        assert bytes(self.blob[off:off+len(before)]) == before
        assert len(before) == len(after) == record['length']
        self.blob[off:off+len(after)] = after; record['source'] = source
        self.changed.append([record['stub'], record['length'], name])

    def replace_routine(self, name, body):
        target = self.routine(name + '_v33', body)
        old = self.old[name]; code = h.asm(f'b {target:#x}', old['stub'])
        off = self.off(old['stub']); self.blob[off:off+4] = code
        record = next(r for r in self.manifest['routines'] if r['name'] == name)
        record.update(source=f'b {target:#x}', length=4)
        self.changed.append([old['stub'], 4, name])
        return target

    def install(self, name, site, body, ret=False):
        previous = next((r for r in self.base['hooks'] if r['site'] == site), None)
        original = previous['original'] if previous else next(Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN).disasm(self.native[self.off(site):self.off(site)+4], site))
        if not isinstance(original, str): original = original.mnemonic + ' ' + original.op_str
        source = h.save() + '\n' + body + '\nfinish:\n' + h.restore() + '\n' + original + f'\nb {site+4:#x}'
        if ret: source += '\nreturn_custom:\n' + h.restore() + '\nret'
        va = self.add_code(name, source); compiled = self.routines.pop()
        code = h.asm(f'b {va:#x}', site); off = self.off(site); self.blob[off:off+4] = code
        self.hooks.append(dict(name=name, site=site, stub=va, resume=site+4, original=original, source=compiled['source'], length=compiled['length']))
        self.changed.append([site, 4, name])

    def finish33(self):
        sites = {r['site'] for r in self.hooks}
        self.manifest['hooks'] = [r for r in self.manifest['hooks'] if r['site'] not in sites] + self.hooks
        self.manifest['hooks'].sort(key=lambda r: (r['name'] != 'v18_saved_state', r['site']))
        self.manifest['routines'] += self.routines
        self.manifest.update(binary_sha256=hashlib.sha256(self.blob).hexdigest(), base_v32_sha256=BASE_SHA,
            v33_new_code_range=[self.code_start,self.cursor], v33_changed_ranges=self.changed,
            map_return_reveals_current_root_not_last_cached_picker=True,
            fresh_New_Life_entry_clears_obsolete_screens=True, startup_and_StartCustomLife_untouched=True,
            age_zero_and_deceased_main_menu_entry_clears_obsolete_UI=True,
            hidden_top_menu_recovery_on_settled_UI_refresh=True)
        assert self.strings == self.base['strings'] and self.states == self.base['states']
        (ROOT / 'native_hooks.json').write_text(json.dumps(self.manifest, indent=2) + '\n')
        (ROOT / 'selector33_options.json').write_bytes((ROOT.parent / 'native_v32/selector32_options.json').read_bytes())
        return bytes(self.blob), self.manifest

def root_guard(b):
    return f'adr x28,{b.newlife24:#x}\nldr w9,[x28,#56]\ncbz w9,finish\nldr x0,[x28,#32]\ncbz x0,finish\nbl 0x223e73c\ncbz x0,finish\nmov x19,x0\nmov x1,xzr\nmov x2,xzr\nbl 0x5575198\ncbz w0,finish\nldr x27,[x19,#0x20]\ncbz x27,finish\nldr w9,[x27,#0xb4]\ncmp w9,#5\nb.ne finish\n'

def clear_lists_body():
    return h.load_game() + '\nldr x8,[x8,#0x90]\ncbz x8,finish\nldr x26,[x8,#0x60]\ncbz x26,finish\nldr x9,[x26,#0x30]\ncbz x9,finish\nldr x9,[x26,#0x38]\ncbz x9,finish\nldr x9,[x26,#0x88]\ncbz x9,finish\nmov x0,x26\nmov x1,xzr\nbl 0x55779e0\nldr x0,[x26,#0x30]\nmov x1,xzr\nbl 0x55779e0\nldr x0,[x26,#0x38]\nmov x1,xzr\nbl 0x55779e0\nmov x0,x26\nmov x1,xzr\nbl 0x2f7c898\nb finish'

def patch(native):
    b = Patch(native); state=b.newlife24; extra=b.newlife31
    clear_lists=b.routine('newlife33_clear_external_lists',clear_lists_body())

    # Finish a canceled slide without selecting the last cached Darkly. Locate
    # the retained root in the real List<UIDarkly>, leave the cache intact, and
    # deactivate every other cached page. Only verified type-5 owners qualify.
    s='str xzr,[sp]\ncbz x0,finish\ncbz x1,finish\nmov x27,x0\nmov x19,x1\nldr w9,[x27,#0xb4]\ncmp w9,#5\nb.ne finish\nldr x8,[x27,#0xc8]\ncbz x8,finish\nldr w20,[x8,#0x18]\ncmp w20,#1\nb.lt finish\ncmp w20,#256\nb.hi finish\nldr x23,[x8,#0x10]\ncbz x23,finish\nldr x9,[x23,#0x18]\ncmp x9,x20\nb.lo finish\nmov w24,#0\nfind_root33:\ncmp w24,w20\nb.hs finish\nadd x8,x23,#0x20\nldr x9,[x8,x24,lsl #3]\ncmp x9,x19\nb.eq found_root33\nadd w24,w24,#1\nb find_root33\nfound_root33:\nstr w24,[x27,#0xbc]\nstr w24,[x27,#0xc0]\nmov w9,#5\nstr w9,[x27,#0xb8]\nmov x0,x27\nmov x1,xzr\nbl 0x55779e0\nmov w24,#0\nhide_other33:\ncmp w24,w20\nb.hs settled33\nadd x8,x23,#0x20\nldr x0,[x8,x24,lsl #3]\nadd w24,w24,#1\ncbz x0,hide_other33\ncmp x0,x19\nb.eq hide_other33\nmov x1,xzr\nbl 0x55725ac\ncbz x0,hide_other33\nmov w1,#0\nmov x2,xzr\nbl 0x5575664\nb hide_other33\nsettled33:\nmov x0,x19\nmovi d0,#0\nfmov s1,#-5.0\nmovi d2,#0\nmov x1,xzr\nbl 0x2f99f14\nmov w9,#1\nstr x9,[sp]\nb finish'
    settle=b.routine('newlife33_settle_root',s)

    # Rebuild shared title/X/shuffle state for the root, rather than invoking
    # RevealDarkly (whose Count-1 lookup is the reproducible wrong-page bug).
    s='str xzr,[sp]\ncbz x0,finish\ncbz x1,finish\nmov x27,x0\nmov x19,x1\n'+f'bl {settle:#x}\ncbz w0,finish\n'
    for reg,offset in [('x27',0x38),('x27',0x40)]:
        s+=f'ldr x0,[{reg},#{offset}]\ncbz x0,finish\nmov x1,xzr\nbl 0x55725ac\ncbz x0,finish\nmov w1,#1\nmov x2,xzr\nbl 0x5575664\n'
    s+='mov x0,x19\nmov x1,xzr\nbl 0x55725ac\ncbz x0,finish\nmov w1,#1\nmov x2,xzr\nbl 0x5575664\nldr x0,[x27,#0x38]\nfmov s0,#1.0\nmov x1,xzr\nbl 0x5881294\nldr x0,[x27,#0x48]\ncbz x0,finish\nldr s0,[x27,#0xdc]\nldr s1,[x27,#0xe0]\nfmov s2,#-5.0\nfadd s1,s1,s2\nmov x1,xzr\nbl 0x2f5fb20\nmov x0,x27\nmov w1,#5\nmov w2,#5\nmov x3,xzr\nmovi d0,#0\nmovi d1,#0\nmovi d2,#0\nbl 0x2f758a0\nmov w9,#1\nstr x9,[sp]\nb finish'
    restore=b.routine('newlife33_restore_root',s)

    # Return succeeds once. A late return after death/replacement never
    # resurrects the old draft or consumes the stock Back handler.
    s='str xzr,[sp]\n'+root_guard(b)+f'ldr w9,[x28,#60]\ncbz w9,finish\nstr wzr,[x28,#60]\nbl {clear_lists:#x}\nmov x0,x27\nmov x1,x19\nbl {restore:#x}\ncbz w0,finish\n'+checkpoint(b,1021)+'mov w9,#1\nstr x9,[sp]\nb finish'
    ret=b.replace_routine('return_from_newlife_editor27',s)

    for n,target in enumerate(['genesis_v18_newlife24','genesis_v18_newlife_map24']):
        s='cbz x0,finish\nmov x25,x0\n'+root_guard(b)+f'cmp x19,x25\nb.ne finish\nldr w9,[x28,#60]\ncbnz w9,finish\nadr x26,{extra:#x}\nldr w9,[x26,#64]\ncbnz w9,finish\nldrb w9,[x27,#0x110]\ncbnz w9,finish\nmov x0,x27\nmov x1,x19\nbl {settle:#x}\ncbz w0,finish\n'+b.ctx('newlife24')
        for off,key,*_ in FIELDS:s+=f'ldr w24,[x28,#{off}]\n'+b.put(key)
        s+=b.set('NativeStage24',0)+b.set('NativeReturn24',0)+f'mov w9,#{n+1}\nstr w9,[x28,#60]\nmov x0,x19\nmov x1,xzr\nbl 0x55725ac\ncbz x0,open_failed33\nmov w1,#0\nmov x2,xzr\nbl 0x5575664\nldr x0,[x27,#0x38]\ncbz x0,open_failed33\nmov x1,xzr\nbl 0x55725ac\ncbz x0,open_failed33\nmov w1,#0\nmov x2,xzr\nbl 0x5575664\n'+show_list(b,target)+f'cbz w0,open_failed33\n'+checkpoint(b,1010+n)+f'b finish\nopen_failed33:\nbl {ret:#x}\nb finish'
        b.replace_routine('new_life_engine_button24_'+str(n),s)

    # All three exits (row, top-left Back, animated Close) share restoration.
    for name in ['v27_editor_root_back','v27_editor_root_close']:
        old=b.old[name]['source']; marker='bl 0x6401d00\nb return_custom'
        assert old.count(marker)==1
        body=old[len(h.save())+1:old.index('\nfinish:')]
        b.install(name,b.old[name]['site'],body.replace(marker,f'bl {ret:#x}\ncbnz w0,return_custom\nb finish'),ret=True)

    # Stock TransitionDarklies declines requests while translation is pending.
    # Reject before changing the custom mode or genes, for every choice.
    for r in b.base['routines']:
        if not (r['name'].startswith('newlife31_open_') or r['name'].startswith('newlife31_choice_')):continue
        ins=list(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(native[b.off(r['stub']):b.off(r['stub'])+r['length']],r['stub']))
        found=[]
        for i,t in enumerate(ins[:-3]):
            if t.mnemonic=='ldr' and t.op_str=='w9, [x27, #0xb4]':
                branch=ins[i+2]; write=ins[i+3]
                assert branch.mnemonic=='b.ne' and write.mnemonic=='mov' and write.op_str.startswith('w9, #')
                finish=int(branch.op_str[1:],16)
                guard=b.add_code(r['name']+'_busy_guard33',f'ldrb w9,[x27,#0x110]\ncbnz w9,{finish:#x}\n{write.mnemonic} {write.op_str}\nb {write.address+4:#x}')
                value=write.op_str.split('#')[1]; value=str(int(value,0))
                mode=5 if r['name'].startswith('newlife31_open_') else 6
                marker=f'cmp w9,#{mode}\nb.ne finish\nmov w9,#{value}\n'
                assert r['source'].count(marker)==1,(r['name'],marker)
                b.update_record(r['name'],r['source'].replace(marker,f'cmp w9,#{mode}\nb.ne finish\nb {guard:#x}\n'))
                found.append(write.address)
        assert len(found)==1,r['name']
    r=b.old['v31_refresh_root_on_selector_return']; marker='mov x1,xzr\nbl 0x2fa6cb4'
    # Same-size replacement is unnecessary here: chain the old hook only once
    # the native request is accepted by the stock manager.
    s='cbz x0,finish\nldrb w9,[x0,#0x110]\ncbz w9,finish\nb return_custom'
    b.install('v33_guard_transition_before_native_refresh',r['site'],s,ret=True)
    new=b.hooks[-1]; new['original']=f'b {r["stub"]:#x}'
    source=new['source'].replace(r['original']+f'\nb {r["site"]+4:#x}',new['original']+f'\nb {r["site"]+4:#x}')
    code=h.asm(source,new['stub']);assert len(code)==new['length'];b.blob[b.off(new['stub']):b.off(new['stub'])+len(code)]=code;new['source']=source

    # A new draft always begins on a clean, visible layer. Main-menu action 1
    # at age zero or after death calls ShowDarklyWithScenario(NULL, 5), rather
    # than ShowDarklyCustomLife. Both entries require the same reset. Restrict
    # the second hook to that exact signature; preserve other scenario types,
    # stock save confirmation, construction, advertisements and Start.
    s='cbz x0,finish\nmov x27,x0\nmov x1,xzr\nbl 0x55779e0\n'+f'bl {clear_lists:#x}\nmov x0,x27\nmov x1,xzr\nbl 0x2f770ec\nmov x0,x27\nbl 0x2f77290\nstrb wzr,[x27,#0x110]\nadr x28,{state:#x}\nstr wzr,[x28]\nldr x0,[x27,#0x38]\ncbz x0,finish\nmov x1,xzr\nbl 0x55725ac\ncbz x0,finish\nmov w1,#1\nmov x2,xzr\nbl 0x5575664\n'+checkpoint(b,1160)+'b finish'
    b.install('v33_fresh_custom_life_clears_obsolete_UI',0x2f77a70,s)
    b.install('v33_fresh_main_menu_newlife_entry',0x2f77cb8,
              'cmp w2,#5\nb.ne finish\ncbnz x1,finish\n'+s)

    # Translation callbacks may finish after Back or a new draft. Verify the
    # captured GameObject is still the current cached page before stock work.
    for name,site,manageroff,pageoff,typeoff in [('transition',0x2f78ecc,0x10,0x30,0x1c),('reveal',0x2f79bd4,0x18,0x10,None)]:
        s='cbz x0,finish\nmov x19,x0\n'+f'ldr x27,[x19,#{manageroff}]\ncbz x27,finish\n'
        if typeoff is not None:
            s+=f'ldr w24,[x19,#{typeoff}]\ncmp w24,#5\nb.eq validate_callback33\ncmp w24,#6\nb.ne finish\nvalidate_callback33:\nldr w9,[x27,#0xb4]\ncmp w9,w24\nb.ne return_custom\n'
        else:s+='ldr x8,[x19,#0x28]\ncbz x8,finish\nldr w24,[x8,#0x40]\ncmp w24,#5\nb.eq validate_callback33\ncmp w24,#6\nb.ne finish\nvalidate_callback33:\nldr w9,[x27,#0xb4]\ncmp w9,w24\nb.ne return_custom\n'
        s+=f'ldr x23,[x19,#{pageoff}]\ncbz x23,return_custom\nldr x8,[x27,#0xc8]\ncbz x8,return_custom\nldr w9,[x8,#0x18]\nldr w24,[x27,#0xbc]\ncmp w24,w9\nb.hs return_custom\nldr x8,[x8,#0x10]\ncbz x8,return_custom\nldr x9,[x8,#0x18]\ncmp x9,x24\nb.ls return_custom\nadd x8,x8,#0x20\nldr x0,[x8,x24,lsl #3]\ncbz x0,return_custom\nmov x1,xzr\nbl 0x55725ac\ncmp x0,x23\nb.ne return_custom\nadr x28,{state:#x}\nldr w9,[x28,#56]\ncbz w9,finish\nldr w9,[x28,#60]\ncbnz w9,return_custom\nb finish'
        b.install('v33_ignore_obsolete_'+name+'_callback',site,s,ret=True)

    # HeroBarSwap toggles the actual navigation GameObject. Recover a hidden
    # bar only after a dialog has closed and outside a menu list or Darkly.
    # RemoveAlert clears currentCard at +0x1c8 before LifeInterface.RefreshUI;
    # therapist choices also reach this shared refresh. Preserve the original
    # RefreshUI body, including normal hero-bar layout and button updates.
    # Checking activeSelf makes repeated refreshes idempotent; do not toggle.
    s='cbz x0,finish\nmov x27,x0\nldr x24,[x27,#0xa0]\ncbz x24,finish\nldr x8,[x24,#0xc8]\ncbz x8,finish\nldr w9,[x8,#0x18]\ncbnz w9,finish\nldrb w9,[x24,#0x110]\ncbnz w9,finish\nldr x8,[x27,#0x80]\ncbz x8,finish\nldr x9,[x8,#0x1c8]\ncbnz x9,finish\nmov x0,x27\nmov x1,xzr\nbl 0x2f838cc\ncbnz w0,finish\nldr x19,[x27,#0x38]\ncbz x19,finish\nmov x0,x19\nmov x1,xzr\nmov x2,xzr\nbl 0x5575198\ncbz w0,finish\nmov x0,x19\nmov x1,xzr\nbl 0x55725ac\ncbz x0,finish\nmov x25,x0\nmov x1,xzr\nbl 0x5575728\ncbnz w0,finish\nmov x0,x25\nmov w1,#1\nmov x2,xzr\nbl 0x5575664\nmov x0,xzr\nmov x1,xzr\nbl 0x2e87cec\ncbz w0,finish\nmov x0,x27\nmov w1,#1\nmov x2,xzr\nbl 0x2f7e424\nb finish'
    b.install('v33_recover_hidden_top_menu_after_dialog',0x2f83be8,s)
    return b.finish33()

if __name__=='__main__':
    raw,manifest=patch(Path(sys.argv[1]).read_bytes());Path(sys.argv[2]).write_bytes(raw)
    print(json.dumps(dict(binary_sha256=manifest['binary_sha256'],new_code_range=manifest['v33_new_code_range'],modified_ranges=len(manifest['v33_changed_ranges']))),flush=True)
