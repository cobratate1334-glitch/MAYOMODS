"""Focused v34 navigation, compact controls and selected-relative context.

Requires the exact v33 native library. No original startup or birth methods
are changed. Newly retained objects use GC handles in loader-zeroed BSS.
"""
import copy, hashlib, json, struct, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
sys.path.insert(0, str(ROOT.parent / 'native_v29'))
from native_hooks import Builder, h
from native_v33.patch_native33 import Patch as PreviousPatch, root_guard
from native_v31.patch_native31 import LABELS, OPTIONS, ICONS
from native_relationship21 import RELATIONS

BASE_SHA = '99d70c773b40587f2b6fb357308f57e1ed0a143ad4661a90bc328cffc2cf2374'

class Patch(PreviousPatch):
    def __init__(self, native):
        Builder.__init__(self, native)
        assert hashlib.sha256(native).hexdigest() == BASE_SHA
        self.base = json.loads((ROOT.parent / 'native_v33/native_hooks.json').read_text())
        self.manifest = copy.deepcopy(self.base)
        self.tail = next(s for s in self.loads if s['p_vaddr'] == self.base['segment_va'])
        self.cursor = (max(r['stub'] + r['length'] for r in self.base['hooks'] + self.base['routines']) + 15) & ~15
        self.code_start = self.cursor
        self.strings = copy.deepcopy(self.base['strings'])
        self.strings_va = min(self.strings.values())
        self.string_cursor = max(v + len(s.encode()) + 1 for s, v in self.strings.items())
        self.states = copy.deepcopy(self.base['states'])
        self.states['relationship34'] = dict(va=0x6574080, size=32)
        self.newlife24 = self.states['newlife24']['va']
        self.newlife31 = self.states['newlife31']['va']
        self.routines = []; self.hooks = []; self.changed = []
        self.old = {r['name']: r for r in self.base['routines'] + self.base['hooks']}
        self.trace23 = self.old['persist_new_life_checkpoint23']['stub']
        self.clear31 = self.old['newlife31_release_ui']['stub']

    def literal(self, value):
        if value not in self.strings:
            self.strings[value] = self.string_cursor
            self.string_cursor += len(value.encode()) + 1
        return self.strings[value]

    def replace(self, name, body):
        target = self.routine(name + '_v34', body)
        old = self.old[name]
        self.blob[self.off(old['stub']):self.off(old['stub'])+4] = h.asm(f'b {target:#x}', old['stub'])
        record = next(r for r in self.manifest['routines'] if r['name'] == name)
        record.update(source=f'b {target:#x}', length=4)
        self.changed.append([old['stub'], 4, name])
        return target

    def rewrite_hook(self, name, body):
        record = self.old[name]
        self.install(name, record['site'], body)

    def finish34(self):
        for value, va in self.strings.items():
            if value in self.base['strings']: continue
            data = value.encode() + b'\0'; off = self.off(va) if va < self.tail['p_vaddr'] + self.tail['p_filesz'] else self.tail['p_offset'] + va - self.tail['p_vaddr']
            assert self.blob[off:off+len(data)] == b'\0' * len(data)
            self.blob[off:off+len(data)] = data
            self.changed.append([va, len(data), 'new_literal'])
        size = max(self.tail['p_filesz'], self.string_cursor - self.tail['p_vaddr'])
        assert self.tail['p_vaddr'] + size < 0x6570000
        i = self.segs.index(self.tail)
        struct.pack_into('<QQ', self.blob, self.e['e_phoff']+i*56+32, size, size)
        rw = next(s for s in self.loads if s['p_vaddr'] == 0x6570000)
        i = self.segs.index(rw)
        assert self.states['relationship34']['va'] >= rw['p_vaddr'] + rw['p_filesz']
        struct.pack_into('<Q', self.blob, self.e['e_phoff']+i*56+40, 0x40a0)
        sites = {r['site'] for r in self.hooks}
        self.manifest['hooks'] = [r for r in self.manifest['hooks'] if r['site'] not in sites] + self.hooks
        self.manifest['hooks'].sort(key=lambda r: (r['name'] != 'v18_saved_state', r['site']))
        self.manifest['routines'] += self.routines
        self.manifest.update(strings=self.strings, states=self.states, segment_size=size,
            binary_sha256=hashlib.sha256(self.blob).hexdigest(), base_v33_sha256=BASE_SHA,
            v34_new_code_range=[self.code_start, self.cursor], v34_changed_ranges=self.changed,
            return_flag_consumed_only_after_visible_root=True,
            compact_icon_controls=True, selected_relative_context_rooted=True)
        (ROOT/'native_hooks.json').write_text(json.dumps(self.manifest, indent=2)+'\n')
        (ROOT/'selector34_options.json').write_bytes((ROOT.parent/'native_v33/selector33_options.json').read_bytes())
        return bytes(self.blob), self.manifest

def body_of(record):
    return record['source'][len(h.save())+1:record['source'].index('\nfinish:')]

def patch(native):
    b = Patch(native); state = b.newlife24; rel = b.states['relationship34']['va']

    # Stock DismissAllLists dereferences both containers and breadcrumbs. Run
    # it for a complete manager; independently clear the available containers
    # during interrupted construction, without dereferencing absent children.
    s=h.load_game()+'\nldr x8,[x8,#0x90]\ncbz x8,finish\nldr x26,[x8,#0x60]\ncbz x26,finish\nmov x0,x26\nmov x1,xzr\nbl 0x55779e0\n'
    for off in [0x30, 0x38]:
        s+=f'ldr x0,[x26,#{off}]\ncbz x0,stop_next_{off}\nmov x1,xzr\nbl 0x55779e0\nstop_next_{off}:\n'
    for off in [0x30, 0x38, 0x88]: s+=f'ldr x9,[x26,#{off}]\ncbz x9,partial_lists34\n'
    s+='mov x0,x26\nmov x1,xzr\nbl 0x2f7c898\nb finish\npartial_lists34:\nstrb wzr,[x26,#0x80]\n'
    for off in [0x30, 0x38]:
        s+=f'ldr x25,[x26,#{off}]\ncbz x25,clear_next_{off}\nmov x0,x25\nmov x1,xzr\nbl 0x2ffb090\nmov x0,x25\nmov x1,xzr\nbl 0x2ff7e38\nclear_next_{off}:\n'
    s+='ldr x25,[x26,#0x88]\ncbz x25,finish\nldp w2,w9,[x25,#0x18]\nadd w9,w9,#1\nstp wzr,w9,[x25,#0x18]\ncbz w2,finish\nldr x0,[x25,#0x10]\ncbz x0,finish\nmov w1,#0\nmov x3,xzr\nbl 0x4f5a490\nb finish'
    clear_lists = b.replace('newlife33_clear_external_lists', s)

    # Validate the required root/canvas/controls before changing cached pages.
    # A missing optional shade does not block the whole restoration.
    previous = body_of(b.old['newlife33_restore_root'])
    previous = previous.replace('mov x19,x1\n', 'mov x19,x1\nldr x9,[x27,#0x38]\ncbz x9,finish\nldr x9,[x27,#0x48]\ncbz x9,finish\n', 1)
    marker='ldr x0,[x27,#64]\ncbz x0,finish\nmov x1,xzr\nbl 0x55725ac\ncbz x0,finish\nmov w1,#1\nmov x2,xzr\nbl 0x5575664\n'
    assert marker in previous
    previous=previous.replace(marker, marker.replace('cbz x0,finish', 'cbz x0,shade_done34')+'shade_done34:\n')
    restore = b.replace('newlife33_restore_root', previous)
    oldreturn='return_from_newlife_editor27_v33'
    s='str xzr,[sp]\n'+root_guard(b)+f'ldr w9,[x28,#60]\ncbz w9,finish\nmov x0,x27\nmov x1,x19\nbl {restore:#x}\ncbz w0,finish\nbl {clear_lists:#x}\nstr wzr,[x28,#60]\nmov w9,#1\nstr x9,[sp]\nb finish'
    b.replace(oldreturn, s)

    # The compact prefab has one text line. Combine the field label and value
    # in a bounded ASCII buffer, rather than silently hiding its subtitle.
    s='str xzr,[sp]\ncbz x0,finish\ncbz x1,finish\nmov x26,x0\nmov x27,x1\nsub sp,sp,#0x80\nmov x25,sp\nmov w24,#0\ncopy_prefix34:\nldrb w9,[x27],#1\ncbz w9,value_begin34\ncmp w24,#96\nb.hs combined_done34\nstrb w9,[x25],#1\nadd w24,w24,#1\nb copy_prefix34\nvalue_begin34:\nldr w20,[x26,#0x10]\nadd x26,x26,#0x14\ncmp w20,#48\nb.hi combined_done34\ncopy_value34:\ncbz w20,combined_done34\ncmp w24,#96\nb.hs combined_done34\nldrh w9,[x26],#2\ncmp w9,#127\nb.hi combined_done34\nstrb w9,[x25],#1\nadd w24,w24,#1\nsub w20,w20,#1\nb copy_value34\ncombined_done34:\nstrb wzr,[x25]\nmov x0,sp\nbl 0x223e8cc\nadd sp,sp,#0x80\nstr x0,[sp]\nb finish'
    combine=b.routine('newlife34_compact_label',s)
    record=b.old['v21_new_life_native_buttons'];source=body_of(record)
    marker='ldr w9,[x19,#0x128]\nmov w21,#9\ncmp w9,#0\ncinc w21,w21,ne\nsub sp,sp,#0x40\n'
    assert source.count(marker)==7
    prefixes=['Height: ','Weight: ','Wingspan: ','Genetic trait: ','Personality: ','Appearance: ','Regions: ']
    # Each replacement removes the subtitle and chooses a shared neutral
    # stock color, preserving the actual button Action and size fitter.
    pieces=source.split(marker);source=pieces[0]
    for prefix,piece in zip(prefixes,pieces[1:]):
        source+=f'mov x0,x22\nadr x1,{b.literal(prefix):#x}\nbl {combine:#x}\ncbz x0,finish\nmov x22,x0\nmov x23,xzr\nmov w21,#11\nsub sp,sp,#0x40\n'+piece.replace('mov w3,#1\n','mov w3,#0\n',1)
    b.rewrite_hook('v21_new_life_native_buttons',source)

    # The stock subgroup header image is +0x60. The old custom early return
    # skipped its texture assignment, leaving a white rectangle.
    title=body_of(b.old['newlife31_selector_title'])
    title=title.removesuffix('b finish')
    title+='ldr x25,[x19,#0x60]\ncbz x25,finish\n'
    for n,icon in enumerate(ICONS):
        title+=f'cmp w24,#{n+1}\nb.ne icon_next34_{n}\n'+b.string(icon)+f'b icon_ready34\nicon_next34_{n}:\n'
    title+='b finish\nicon_ready34:\nmov x1,xzr\nbl 0x2bad908\ncbz x0,hide_icon34\nmov x1,xzr\nbl 0x553b564\ncbz x0,hide_icon34\nmov x22,x0\nmov x0,x25\nadd x1,x25,#0x58\nmov x2,x22\nbl 0x223e768\nmov x0,x25\nmov x1,xzr\nbl 0x3023ba8\nmov w24,#1\nb set_icon_active34\nhide_icon34:\nmov w24,#0\nset_icon_active34:\nmov x0,x25\nmov x1,xzr\nbl 0x55725ac\ncbz x0,finish\nmov w1,w24\nmov x2,xzr\nbl 0x5575664\nb finish'
    b.replace('newlife31_selector_title',title)

    # The last relationship MENU selection is distinct from profile rendering.
    # Keep selected person and current hero rooted; later profile previews can
    # refresh their own tables without changing this menu's story recipient.
    s=f'adr x28,{rel:#x}\n'
    for off in [0,8]:s+=f'ldr x0,[x28,#{off}]\ncbz x0,release_rel34_{off}\nbl 0x223e784\nrelease_rel34_{off}:\nstr xzr,[x28,#{off}]\n'
    s+='str wzr,[x28,#16]\nb finish'
    release=b.routine('relationship34_release_context',s)
    s='mov x26,x0\nmov w27,w1\n'+f'bl {release:#x}\ncbz x26,finish\n'+h.load_game()+'\nldr x25,[x8,#0x28]\ncbz x25,finish\nmov x0,x26\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nmov x24,x0\nmov x0,x25\nmov w1,#0\nbl 0x223e704\ncbz x0,hold_hero_failed34\n'+f'adr x28,{rel:#x}\nstr x24,[x28]\nstr x0,[x28,#8]\nstr w27,[x28,#16]\nb finish\nhold_hero_failed34:\nmov x0,x24\nbl 0x223e784\nb finish'
    capture=b.routine('relationship34_capture_menu_person',s)
    for label,entry,site,reg,isfriend in RELATIONS:
        old=b.old['v21_relationship_snapshot_'+label];body=body_of(old)
        marker=f'mov w1,#{isfriend}\n'
        assert body.count(marker)==1
        body=body.replace(marker,marker+f'bl {capture:#x}\n')
        b.rewrite_hook(old['name'],body)

    # Only refresh the story panel's exact ID. Check hero identity first so an
    # old callback cannot transfer a relative's details into a replacement life.
    panel='genesis_v18_relationship21'
    s='cbz x0,finish\nmov x8,x0\n'+h.compare_key(panel,'refresh_selected34','finish')+'\nrefresh_selected34:\n'+h.load_game()+'\nldr x26,[x8,#0x28]\ncbz x26,invalid_rel34\n'+f'adr x28,{rel:#x}\nldr x0,[x28,#8]\ncbz x0,invalid_rel34\nbl 0x223e73c\ncmp x0,x26\nb.ne invalid_rel34\nldr x0,[x28]\ncbz x0,invalid_rel34\nbl 0x223e73c\ncbz x0,invalid_rel34\nldr w1,[x28,#16]\nbl {b.old["selected_relationship_details21"]["stub"]:#x}\nb finish\ninvalid_rel34:\nbl {release:#x}\n'+b.ctx('relationship21')+b.text('Name','Unavailable')+b.set('Age',0)+b.text('Story','Open a current relationship to view their story.')+'b finish'
    b.install('v34_refresh_selected_relative_on_story_open',0x3089aac,s)
    # Birth releases old context, then continues the existing selector/genetics
    # hook unchanged. No person pointer or GC handle is serialized into a save.
    old=b.old['v31_birth_release_selector_roots']
    b.install('v34_birth_releases_relationship_context',old['site'],f'bl {release:#x}\nb finish')
    new=b.hooks[-1];new['original']=f'b {old["stub"]:#x}'
    source=new['source'].replace(old['original']+f'\nb {old["site"]+4:#x}',new['original']+f'\nb {old["site"]+4:#x}')
    code=h.asm(source,new['stub']);assert len(code)==new['length'];b.blob[b.off(new['stub']):b.off(new['stub'])+len(code)]=code;new['source']=source
    from countries34 import patch as country_patch
    country_patch(b)
    return b.finish34()

if __name__=='__main__':
    raw,m=patch(Path(sys.argv[1]).read_bytes());Path(sys.argv[2]).write_bytes(raw)
    print(json.dumps(dict(sha256=m['binary_sha256'],code_bytes=m['v34_new_code_range'][1]-m['v34_new_code_range'][0])),flush=True)
