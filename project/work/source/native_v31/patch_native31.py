"""Native New Life controls using the game's existing rounded selectors.

Patch the exact v30 library. Reuse verified v29 state/engine routines and
existing Darkly prefab/scroller/collection cleanup; never intercept Start.
"""
import copy, hashlib, io, json, re, struct, sys
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parent
V29 = ROOT.parent / 'native_v29'
sys.path.insert(0, str(V29))
from native_hooks import Builder, h
from native_newlife24 import FIELDS, release_handles
from native_ui21 import TRAITS, PERSONALITIES, RARE, checkpoint, number

BASE_SHA = 'c84f04a89444dbc36b8a479353df1d00376c4dbadd7d94f100b1c57372c7206e'
LABELS = ['Adult height', 'Adult weight', 'Adult wingspan', 'Genetic trait', 'Personality', 'Appearance trait']
ICONS = ['running-shoe', 'balance-scale', 'running-shoe', 'light-bulb', 'handshake', 'face-nerd']
TRAIT_UI = ['Random', 'Genius', 'Athletic', 'Creative', 'Resilient', 'Empathetic', 'Curious', 'Determined']
PERSONALITY_UI = ['Random', 'Caring', 'Funny', 'Quiet', 'Outgoing', 'Patient', 'Competitive', 'Creative', 'Optimistic']
RARE_UI = ['None', *RARE[1:]]
OPTIONS = [
    [(v, f'{v} cm') for v in range(140, 236)],
    [(v, f'{v} kg') for v in range(40, 181)],
    [(v, f'{v:+} cm') for v in range(-10, 21)],
    list(enumerate(TRAIT_UI)), list(enumerate(PERSONALITY_UI)), list(enumerate(RARE_UI)),
]

class Patch(Builder):
    def __init__(self, native):
        super().__init__(native)
        self.base = json.loads((V29 / 'native_hooks.json').read_text())
        assert hashlib.sha256(native).hexdigest() == BASE_SHA
        self.tail = next(s for s in self.loads if s['p_vaddr'] == self.base['segment_va'])
        self.cursor = (max(r['stub'] + r['length'] for r in self.base['hooks'] + self.base['routines']) + 15) & ~15
        self.code_start = self.cursor
        self.strings_va = min(self.base['strings'].values())
        self.strings = copy.deepcopy(self.base['strings'])
        self.states = copy.deepcopy(self.base['states'])
        self.states['newlife31'] = dict(va=0x6570080, size=128)
        self.routines = []
        self.hooks = []
        self.imports = copy.deepcopy(self.base['imports'])
        self.newlife24 = self.states['newlife24']['va']
        self.newlife31 = self.states['newlife31']['va']
        self.old = {r['name']: r['stub'] for r in self.base['routines']}
        self.trace23 = self.old['persist_new_life_checkpoint23']
        self.layout26 = self.old['activate_and_register_newlife_button26']
        self.sync24 = self.old['new_life_pending_labels24']

    def install(self, name, site, body, ret=False, custom_resume=None):
        previous = next((r for r in self.base['hooks'] if r['site'] == site), None)
        if previous:
            original = previous['original']
        else:
            from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN
            ins = next(Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN).disasm(self.native[self.off(site):self.off(site)+4], site))
            original = ins.mnemonic + ' ' + ins.op_str.replace('#0x', '0x')
        source = h.save()+'\n'+body+'\nfinish:\n'+h.restore()+'\n'+original+f'\nb {site+4:#x}'
        if ret or custom_resume:
            source += '\nreturn_custom:\n'+h.restore()+'\n'+(f'b {custom_resume:#x}' if custom_resume else 'ret')
        source = re.sub(r'\badr (x\d+),\s*(0x[0-9a-f]+)', lambda m:f'adrp {m[1]}, {int(m[2],16)&~4095:#x}\nadd {m[1]}, {m[1]}, #{int(m[2],16)&4095}', source)
        code = h.asm(source, self.cursor)
        at = self.off(self.cursor)
        assert self.blob[at:at+len(code)] == b'\0'*len(code), 'new code must use empty reserved RX space'
        self.blob[at:at+len(code)] = code
        self.blob[self.off(site):self.off(site)+4] = h.asm(f'b {self.cursor:#x}',site)
        self.hooks.append(dict(name=name, site=site, stub=self.cursor, resume=site+4, original=original, source=source, length=len(code), custom_resume=custom_resume))
        self.cursor = (self.cursor+len(code)+15)&~15

    def finish31(self):
        assert self.cursor < self.strings_va, 'new code overlaps retained strings'
        new_strings = []
        for s, va in self.strings.items():
            if s in self.base['strings']: continue
            at = self.tail['p_offset']+va-self.tail['p_vaddr']
            value = s.encode()+b'\0'
            assert self.blob[at:at+len(value)] == b'\0'*len(value)
            self.blob[at:at+len(value)] = value
            new_strings.append((s,va))
        end = max(v+len(s.encode())+1 for s,v in self.strings.items())
        assert end < self.states['newlife31']['va']
        size = end-self.tail['p_vaddr']
        i = self.segs.index(self.tail)
        struct.pack_into('<QQ', self.blob, self.e['e_phoff']+i*56+32, size,size)
        d = copy.deepcopy(self.base)
        sites = {x['site'] for x in self.hooks}
        d['hooks'] = [x for x in d['hooks'] if x['site'] not in sites]+self.hooks
        # Keep the saved-state dispatcher first for inherited execution fixtures.
        d['hooks'].sort(key=lambda x:(x['name']!='v18_saved_state',x['site']))
        d['routines'] += self.routines
        d.update(strings=self.strings, states=self.states, segment_size=size, binary_sha256=hashlib.sha256(self.blob).hexdigest(), base_v30_sha256=BASE_SHA, v31_new_code_range=[self.code_start,self.cursor], v31_new_strings=new_strings)
        (ROOT/'native_hooks.json').write_text(json.dumps(d,indent=2)+'\n')
        return bytes(self.blob), d

def extra_release(b, include_selector=True):
    offsets = list(range(0,40,8)) + ([72] if include_selector else [])
    s=f'adr x26,{b.newlife31:#x}\n'
    for off in offsets:
        s += f'ldr x0,[x26,#{off}]\ncbz x0,free31_{off}\nbl 0x223e784\nfree31_{off}:\nstr xzr,[x26,#{off}]\n'
    return s+'str wzr,[x26,#64]\n'

def action(b, target, callback, button='x25'):
    return 'adr x8,0x5c2a0b0\nldr x8,[x8]\ncbz x8,finish\nldr x0,[x8]\ncbz x0,finish\nbl 0x2237158\ncbz x0,finish\nmov x22,x0\nadr x8,0x5c7a528\nldr x8,[x8]\ncbz x8,finish\nldr x2,[x8]\n'+f'mov x1,{target}\nmov x3,xzr\nbl 0x4ec64e4\nadr x8,{callback:#x}\nstr x8,[x22,#0x10]\nstr x8,[x22,#0x18]\nmov x0,{button}\nadd x1,{button},#0xa0\nmov x2,x22\nbl 0x223e768\n'

def stock_button(b, title='x22', subtitle='x23', icon='x20', color='w21', large=1):
    return 'sub sp,sp,#0x40\n'+f'stp {subtitle},xzr,[sp]\n'+'stp xzr,xzr,[sp,#16]\nstp xzr,xzr,[sp,#32]\nmov x0,x28\nmov x1,x25\nmov x2,x27\n'+f'mov w3,#{large}\nmov w4,{color}\nmov x5,{title}\nmov x6,xzr\nmov x7,{icon}\nbl 0x2f72230\nadd sp,sp,#0x40\ncbz x0,finish\nmov x25,x0\n'

def root_guard(b):
    return f'cbz x0,finish\nmov x19,x0\nadr x28,{b.newlife24:#x}\nldr w9,[x28,#56]\ncbz w9,finish\nldr x0,[x28,#32]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\nmov x0,x19\nmov x1,xzr\nmov x2,xzr\nbl 0x5575198\ncbz w0,finish\n'

def patch(native):
    b = Patch(native)
    state, extra = b.newlife24, b.newlife31
    # Numeric titles share the stock text formatting path and preserve callers.
    b.cm31=b.routine('newlife31_cm_title',number(b,reg='w0',unit=' cm')+'str x22,[sp]\nb finish')
    b.kg31=b.routine('newlife31_kg_title',number(b,reg='w0',unit=' kg')+'str x22,[sp]\nb finish')
    b.clear31=b.routine('newlife31_release_ui',f'adr x28,{state:#x}\nstr wzr,[x28,#56]\nstr wzr,[x28,#60]\n'+release_handles(state)+extra_release(b)+'b finish')

    # Main form callbacks transition to the existing CustomLifeSubGroup page.
    main_callbacks=[]
    for n in range(6):
        s=root_guard(b)+f'adr x26,{extra:#x}\nldr w9,[x26,#64]\ncbnz w9,finish\nldr w9,[x28,#60]\ncbnz w9,finish\nldr x27,[x19,#0x20]\ncbz x27,finish\nldr w9,[x27,#0xb4]\ncmp w9,#5\nb.ne finish\nmov w9,#{n+1}\nstr w9,[x26,#64]\nstr wzr,[x19,#0x10c]\nmov x0,x27\nmov w1,#6\nmov x2,xzr\nbl 0x2f731f8\n'+checkpoint(b,1130+n)+'b finish'
        main_callbacks.append(b.routine('newlife31_open_'+str(n),s))

    # Each closed Action has a fixed, bounded native value and validates its
    # owner/page before applying it. No raw object pointers survive transitions.
    choices=[]
    for n, opts in enumerate(OPTIONS):
        field=FIELDS[n][0]; row=[]
        for value,label in opts:
            s=f'cbz x0,finish\nmov x19,x0\nadr x28,{state:#x}\nldr w9,[x28,#56]\ncbz w9,finish\nadr x26,{extra:#x}\nldr w9,[x26,#64]\ncmp w9,#{n+1}\nb.ne finish\nldr x0,[x26,#72]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\nldr x27,[x19,#0x20]\ncbz x27,finish\nldr w9,[x27,#0xb4]\ncmp w9,#6\nb.ne finish\nmov w9,#{value}\nstr w9,[x28,#{field}]\nmov w9,#1\nstr w9,[x28]\nbl {b.sync24:#x}\nstr wzr,[x19,#0x54]\nmov x0,x27\nmov w1,#5\nmov x2,xzr\nbl 0x2f731f8\n'+checkpoint(b,1140+n)+'b finish'
            row.append((value,label,b.routine(f'newlife31_choice_{n}_{value}',s)))
        choices.append(row)

    # Add a selector pill using exactly the stock scroller, content list and
    # size fitter. Reset/DestroyContents owns cleanup, including our buttons.
    s='cbz x0,finish\nmov x19,x0\nmov x22,x1\nmov x24,x2\nmov w21,w3\nldr x28,[x19,#0x20]\ncbz x28,finish\nldr x27,[x19,#0x70]\ncbz x27,finish\nmov x25,xzr\nmov x23,xzr\nmov x20,xzr\n'+stock_button(b,large=0)
    s+='ldr x8,[x19,#0xa0]\ncbz x8,finish\nldr x8,[x8,#0x28]\nstr x8,[x25,#0x90]\n'
    # x24 callback address must survive Action construction; use dynamic helper.
    s+='adr x8,0x5c2a0b0\nldr x8,[x8]\nldr x0,[x8]\nbl 0x2237158\ncbz x0,finish\nmov x22,x0\nadr x8,0x5c7a528\nldr x8,[x8]\nldr x2,[x8]\nmov x1,x19\nmov x3,xzr\nbl 0x4ec64e4\nstr x24,[x22,#0x10]\nstr x24,[x22,#0x18]\nmov x0,x25\nadd x1,x25,#0xa0\nmov x2,x22\nbl 0x223e768\n'
    s+='mov x0,x25\nmov x1,xzr\nbl 0x55725ac\ncbz x0,finish\nmov x23,x0\nmov w1,#1\nmov x2,xzr\nbl 0x5575664\nldr x0,[x19,#0xe0]\ncbz x0,finish\nadr x8,0x5c6d1a8\nldr x8,[x8]\nldr x8,[x8]\nldr x8,[x8,#0x20]\nldr x8,[x8,#0xc0]\nldr x2,[x8,#0x70]\nmov x1,x23\nbl 0x49901a4\nldr x0,[x19,#0x90]\ncbz x0,finish\nldr x1,[x25,#0x28]\nmov x2,xzr\nbl 0x2f5bc48\nb finish'
    b.option31=b.routine('newlife31_add_rounded_option',s)

    # Stock UpdateDarklyLayout supplies the shared title; override only our
    # retained selector instance, leaving Gender/Country/City untouched.
    s=f'cbz x0,finish\nmov x19,x0\nadr x26,{extra:#x}\nldr w24,[x26,#64]\n'
    for n,label in enumerate(LABELS):
        s+=f'cmp w24,#{n+1}\nb.ne title31_{n}\n'+b.string(label)+'mov x22,x0\n'+b.string('Choose your adult build.' if n<2 else 'Choose your adult wingspan.' if n==2 else 'Choose an inherited trait.' if n==3 else 'Choose a personality.' if n==4 else 'Choose a rare trait.')+f'mov x23,x0\nb title31_ready\ntitle31_{n}:\n'
    s+='b finish\ntitle31_ready:\nldr x0,[x19,#0x38]\ncbz x0,finish\nmov x1,x22\nmov x2,xzr\nbl 0x3024244\nldr x0,[x19,#0x68]\ncbz x0,finish\nmov x1,x23\nmov x2,xzr\nbl 0x3024244\nb finish'
    b.title31=b.routine('newlife31_selector_title',s)
    guard=f'cbz x0,finish\nmov x19,x0\nadr x26,{extra:#x}\nldr w9,[x26,#64]\ncbz w9,finish\nldr x0,[x26,#72]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\n'
    b.install('v31_selector_layout',0x2fa9a1c,guard+f'mov x0,x19\nbl {b.title31:#x}\nb return_custom',ret=True)

    # Hook after the stock metadata initialization, then jump to the real
    # scroller/layout epilogue. Reset creates the required generic collections.
    s=f'adr x28,{state:#x}\nldr w9,[x28,#56]\ncbz w9,finish\nadr x26,{extra:#x}\nldr w24,[x26,#64]\ncbz w24,finish\ncmp w24,#6\nb.hi finish\nmov x0,x19\nbl 0x2fa97ac\nstr wzr,[x19,#0x54]\nldr x0,[x26,#72]\ncbz x0,selector_hold31\nbl 0x223e784\nstr xzr,[x26,#72]\nselector_hold31:\nmov x0,x19\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nstr x0,[x26,#72]\nmov x0,x19\nbl {b.title31:#x}\n'
    for n, opts in enumerate(choices):
        s+=f'cmp w24,#{n+1}\nb.ne selector_next31_{n}\n'
        for value,label,cb in opts:
            if n==2:
                s+=f'ldr w0,[x28,#4]\nmov w9,#{value}\nadd w0,w0,w9\nbl {b.cm31:#x}\n'
            else:s+=b.string(label)
            s+=f'mov x1,x0\nmov x0,x19\nadr x2,{cb:#x}\nldr w9,[x28,#{FIELDS[n][0]}]\nmov w10,#{value}\ncmp w9,w10\ncset w3,ne\nbl {b.option31:#x}\n'
        s+=f'b selector_done31\nselector_next31_{n}:\n'
    s+='selector_done31:\n'+checkpoint(b,1138)+'b return_custom'
    b.install('v31_native_rounded_selector_setup',0x2fa9fcc,s,custom_resume=0x2faaf34)

    # Replace the old two-button/table-page entry with six compact native
    # form fields and the existing map route. Reused roots always reset routes.
    s=checkpoint(b,1001)+f'cbz x19,finish\nldr x28,[x19,#0x20]\ncbz x28,finish\nadr x26,{state:#x}\nldr x0,[x26,#32]\ncbz x0,root_new31\nbl 0x223e73c\ncmp x0,x19\nb.eq root_ready31\nroot_new31:\n'+release_handles(state)+extra_release(b)
    s+=f'adr x26,{state:#x}\nmov x0,x19\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nstr x0,[x26,#32]\n'
    for off,key,default,lo,hi in FIELDS:s+=f'mov w9,#{default}\nstr w9,[x26,#{off}]\n'
    s+='mov w9,#1\nstr w9,[x26]\nroot_ready31:\nmov w9,#1\nstr w9,[x26]\nstr w9,[x26,#56]\nstr wzr,[x26,#60]\n'+f'adr x25,{extra:#x}\nstr wzr,[x25,#64]\nldr x0,[x25,#72]\ncbz x0,root_selector_released31\nbl 0x223e784\nstr xzr,[x25,#72]\nroot_selector_released31:\n'
    s+='ldr x0,[x19,#0xd0]\ncbz x0,finish\nmov x1,xzr\nbl 0x55724dc\ncbz x0,finish\nmov x25,x0\nmov x1,xzr\nbl 0x55844f4\nmov w24,w0\nmov x0,x25\nmov x1,xzr\nbl 0x5582ca4\ncbz x0,finish\nmov x27,x0\n'
    handle_sites=[(state,40)]+[(extra,n*8)for n in range(5)]+[(state,48)]
    for n,(handlebase,off)in enumerate(handle_sites):
        s+=f'adr x20,{handlebase:#x}\nldr x0,[x20,#{off}]\ncbz x0,root_no_button31_{n}\nbl 0x223e73c\nb root_button31_{n}\nroot_no_button31_{n}:\nmov x0,xzr\nroot_button31_{n}:\nmov x25,x0\n'
        if n<3:
            s+=f'ldr w0,[x26,#{FIELDS[n][0]}]\n'
            if n==2:s+='ldr w9,[x26,#4]\nadd w0,w0,w9\n'
            s+=f'bl {b.kg31 if n==1 else b.cm31:#x}\nmov x22,x0\n'
        elif n<6:
            s+=f'ldr w9,[x26,#{FIELDS[n][0]}]\n'
            for v,label in enumerate([TRAIT_UI,PERSONALITY_UI,RARE_UI][n-3]):
                s+=f'cmp w9,#{v}\nb.ne root_name31_{n}_{v}\n'+b.string(label)+f'mov x22,x0\nb root_name31_done_{n}\nroot_name31_{n}_{v}:\n'
            s+=b.string('Random')+f'mov x22,x0\nroot_name31_done_{n}:\n'
        else:s+=b.string('US Map')+'mov x22,x0\n'
        s+=b.string(LABELS[n]if n<6 else 'Regions')+'mov x23,x0\n'+b.string(ICONS[n]if n<6 else 'earth')+'mov x20,x0\n'
        # Use the same stock gender colors as the original Name/City fields.
        s+='ldr w9,[x19,#0x128]\nmov w21,#9\ncmp w9,#0\ncinc w21,w21,ne\n'+stock_button(b)
        s+=f'adr x20,{handlebase:#x}\nldr x23,[x20,#{off}]\ncbz x23,root_hold31_{n}\nmov x0,x23\nbl 0x223e73c\ncmp x0,x25\nb.eq root_held31_{n}\nroot_hold31_{n}:\nmov x0,x25\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nmov x22,x0\ncbz x23,root_replace31_{n}\nmov x0,x23\nbl 0x223e784\nroot_replace31_{n}:\nstr x22,[x20,#{off}]\nroot_held31_{n}:\n'
        s+=action(b,'x19',main_callbacks[n]if n<6 else b.old['new_life_engine_button24_1'])
        s+=f'mov x0,x25\nmov x1,xzr\nbl 0x55724dc\ncbz x0,finish\nadd w1,w24,#{n+1}\nmov x2,xzr\nbl 0x5584430\nmov x0,x27\nmov x1,x25\nbl {b.layout26:#x}\n'
    s+=f'bl {b.sync24:#x}\n'+checkpoint(b,1006)+'b finish'
    b.install('v21_new_life_native_buttons',0x2fa7b70,s)

    # A custom subtype deliberately has no stock Gender/City update. Refresh
    # the root before the stock 6 -> 5 transition for both a choice and Back.
    # RefreshSetup reuses the original draft's names/country/city, and Setup
    # clears the selector route and releases its retained GC handle.
    s=f'cbz x0,finish\nmov x27,x0\ncmp w1,#5\nb.ne finish\nldr w9,[x27,#0xb4]\ncmp w9,#6\nb.ne finish\nadr x28,{state:#x}\nldr w9,[x28,#56]\ncbz w9,finish\nadr x26,{extra:#x}\nldr w9,[x26,#64]\ncbz w9,finish\ncmp w9,#6\nb.hi finish\nldr x0,[x28,#32]\ncbz x0,finish\nbl 0x223e73c\ncbz x0,finish\nldr x9,[x0,#0x20]\ncmp x9,x27\nb.ne finish\nmov x1,xzr\nbl 0x2fa6cb4\nb finish'
    b.install('v31_refresh_root_on_selector_return',0x2f731f8,s)

    # A root X cancels this draft. Dismiss releases all UI roots, but retains
    # scalar pending genes if the stock Start has already requested birth.
    s=f'cbz x0,finish\nmov x27,x0\nldr w9,[x27,#0xb4]\ncmp w9,#5\nb.ne finish\nadr x28,{state:#x}\nldr w9,[x28,#56]\ncbz w9,finish\nldr x0,[x28,#32]\ncbz x0,finish\nbl 0x223e73c\ncbz x0,finish\nldr x9,[x0,#0x20]\ncmp x9,x27\nb.ne finish\nstr wzr,[x28]\nstr wzr,[x28,#56]\nstr wzr,[x28,#60]\nadr x26,{extra:#x}\nstr wzr,[x26,#64]\n'+checkpoint(b,1150)+'b finish'
    b.install('v31_cancel_newlife_draft',0x2f764b4,s)
    s=f'cbz x0,finish\nmov x27,x0\nadr x28,{state:#x}\nldr x0,[x28,#32]\ncbz x0,finish\nbl 0x223e73c\ncbz x0,cleanup31\nldr x9,[x0,#0x20]\ncmp x9,x27\nb.ne finish\ncleanup31:\nbl {b.clear31:#x}\n'+checkpoint(b,1002)+'b finish'
    b.install('v23_dismiss_android_setup_panel',0x2f770ec,s)
    # Clear selector-only roots when birth consumes the draft, without changing
    # the original genetic/profile engine or StartCustomLife implementation.
    previous=next(x for x in b.base['hooks']if x['name']=='v21_apply_body_after_hero_generation')
    s=extra_release(b)+f'b finish'
    # Chain through the retained v29 birth hook, including once-only genetics.
    b.install('v31_birth_release_selector_roots',previous['site'],s)
    hook=b.hooks[-1]
    hook['original']=f'b {previous["stub"]:#x}'
    # Regenerate this wrapper's continuation as a branch to the old full hook.
    source=hook['source'].replace(previous['original']+f'\nb {previous["site"]+4:#x}',hook['original']+f'\nb {previous["site"]+4:#x}')
    code=h.asm(source,hook['stub']);assert len(code)==hook['length'];b.blob[b.off(hook['stub']):b.off(hook['stub'])+len(code)]=code;hook['source']=source
    binary,manifest=b.finish31()
    (ROOT/'selector31_options.json').write_text(json.dumps(dict(labels=LABELS,options=[[(v,l,cb)for v,l,cb in r]for r in choices],main_callbacks=main_callbacks,handle_sites=handle_sites),indent=2)+'\n')
    return binary,manifest

if __name__=='__main__':
    result,m=patch(Path(sys.argv[1]).read_bytes());Path(sys.argv[2]).write_bytes(result)
    print(json.dumps(dict(sha256=m['binary_sha256'],code_bytes=m['v31_new_code_range'][1]-m['v31_new_code_range'][0],rounded_options=sum(map(len,OPTIONS)),StartCustomLife_untouched=True)),flush=True)
