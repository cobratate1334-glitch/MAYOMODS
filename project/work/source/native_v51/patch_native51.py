"""Repair menu self-cancellation and persist family-linked adult height.

Pinned v50 sibling update. Existing objects, save containers, resource IDs,
Android permissions and ELF load segments remain in place.
"""
import copy, hashlib, json, os, sys
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent; SOURCE=ROOT.parent
sys.path[:0]=[str(SOURCE),str(SOURCE/'native_v29')]
from native_v50.patch_native50 import Patch as Previous
from native_hooks import Builder,h
from native_v42.patch_native42 import body
BASE_SHA='728562b275a81a67126039c6979c84aab77a652e40c36730fd7b91d88ec94405'

class Patch(Previous):
    def __init__(self,raw):
        Builder.__init__(self,raw)
        assert hashlib.sha256(raw).hexdigest()==BASE_SHA
        self.base=json.loads((SOURCE/'native_v50/native_hooks.json').read_text())
        self.manifest=copy.deepcopy(self.base)
        self.old={r['name']:r for r in self.base['hooks']+self.base['routines']}
        self.rxoff,self.rxva,size=self.base['v49_new_rx']
        self.tail=next(s for s in self.loads if s['p_vaddr']==self.rxva)
        self.cursor=self.code_start=self.rxva+0x40000
        self.strings_va=self.rxva+0xe0000; self.string_cursor=self.strings_va
        self.strings=copy.deepcopy(self.base['strings']); self.states=copy.deepcopy(self.base['states'])
        self.routines=[]; self.hooks=[]; self.changed=[]; self.serial=0
        assert self.base['v50_new_code_range'][1]<self.cursor

    def redirect(self,name,source):
        old=self.old[name]; target=self.add_code(name+'_v51',source)
        self.blob[self.off(old['stub']):self.off(old['stub'])+4]=h.asm(f'b {target:#x}',old['stub'])
        for r in self.manifest['hooks']+self.manifest['routines']:
            if r['name']==name:r.update(source=f'b {target:#x}',length=4)
        self.changed.append([old['stub'],4,name]); return target

    def replace51(self,name,code):
        return self.redirect(name,h.save()+'\n'+code+'\nfinish:\n'+h.restore()+'\nret')

    def finish51(self):
        assert self.cursor<self.strings_va
        for s,va in self.strings.items():
            if s in self.base['strings']:continue
            raw=s.encode()+b'\0';p=self.off(va)
            assert self.blob[p:p+len(raw)]==b'\0'*len(raw)
            self.blob[p:p+len(raw)]=raw; self.changed.append([va,len(raw),'literal'])
        assert self.string_cursor<self.rxva+0x100000 and len(self.blob)==len(self.native)
        sites={r['site']for r in self.hooks}
        self.manifest['hooks']=[r for r in self.manifest['hooks']if r['site']not in sites]+self.hooks
        self.manifest['routines']+=self.routines
        self.manifest.update(binary_sha256=hashlib.sha256(self.blob).hexdigest(),strings=self.strings,
            base_v50_sha256=BASE_SHA,v51_new_code_range=[self.code_start,self.cursor],
            v51_changed_ranges=self.changed,v51_no_segment_growth=True,
            v51_internal_dismiss_preserves_running_coroutines=True,
            v51_height_source_codes={'0':'uninitialized','1':'family estimate','2':'explicit selection'},
            v51_height_draft_flag_offset=28)
        (ROOT/'native_hooks.json').write_text(json.dumps(self.manifest,indent=2)+'\n')
        return bytes(self.blob)

def navigation(b):
    # DismissAllLists is called INSIDE RemoveNormalListAnimation.MoveNext.
    # Stopping its owner here cancels the parent before its yielded
    # ShowLowerPanel is executed. A dismissal is cleanup of the current
    # presentation. Keep invalidating old deferred translation callbacks,
    # while allowing this owner's current close to finish its own cleanup.
    old=b.old['v41_dismiss_invalidates_pending_presentations']
    src=body(old)
    marker='mov x0,x27\nmov x1,xzr\nbl 0x55779e0'
    assert marker in src
    epoch_only=src[:src.index(marker)]+'b finish'
    b.redirect(old['name'],h.save()+'\n'+epoch_only+'\nfinish:\n'+h.restore()+'\n'+old['original']+f'\nb {old["resume"]:#x}')
    # Retain the quiescence checks, typed v48 script receiver, native group
    # activation and lower-panel recovery. Repair the cancellation trigger
    # without changing the native visual/accessibility activation policy.
    src=body(b.old['v46_restore_native_hud'])
    # v48 corrected the source instruction too; fail the build if it regresses.
    assert 'mov x0,x23\ncbz x0,finish\nmov x1,xzr\nbl 0x55779e0' in src

def height(b):
    # Derive the same parent adult-height value already used by the shipped
    # native relationship profile. Do not silently change an existing parent.
    # x0 is a live SimPerson; no pointer survives this call.
    s='str xzr,[sp]\ncbz x0,finish\nmov x1,xzr\nbl 0x2c44914\ncbz x0,finish\nldr w11,[x0,#0x10]\nadd x12,x0,#0x14\nmov w13,#5381\nheight51_hash:\ncbz w11,height51_hashed\nldrh w9,[x12],#2\nmov w10,#33\nmadd w13,w13,w10,w9\nsub w11,w11,#1\nb height51_hash\nheight51_hashed:\nand w13,w13,#0x7fffffff\nmov w9,#55\nudiv w10,w13,w9\nmsub w0,w10,w9,w13\nadd w0,w0,#155\nstr x0,[sp]\nb finish'
    parent=b.routine('v51_parent_adult_height',s)
    # Social profiles used a second (different) name-to-height formula. Keep
    # their dating/body data consistent with the native relationship view.
    s=b.ctx('social_v18')
    for slot in range(1,25):
        q=f'C{slot}';s+=b.get(q+'Present','w19')+f'cbz w19,height51_contact_{slot}\n'+b.get(q+'ProfileId20','w19')
        s+='mov w9,#55\nudiv w10,w19,w9\nmsub w24,w10,w9,w19\nadd w24,w24,#155\n'+b.put(q+'AdultHeight20')+f'height51_contact_{slot}:\n'
    s+='b finish';contacts=b.routine('v51_consistent_contact_heights',s)
    # Independently locate the completion of the old social-sync handler by
    # a same-width assembly probe. This retains all its native NPC collection,
    # follow cleanup, school staff and relationship integration logic.
    old=b.old['v18_saved_state'];needle='end_role24:\nb finish'
    assert old['source'].count(needle)==1
    a=h.asm(old['source'],old['stub'])
    z=h.asm(old['source'].replace(needle,'end_role24:\nbr x15',1),old['stub'])
    diff=[i for i,(x,y)in enumerate(zip(a,z))if x!=y]
    assert len(diff)==4 and max(diff)//4==min(diff)//4
    site=old['stub']+(min(diff)//4)*4
    assert bytes(b.blob[b.off(site):b.off(site)+4])==a[site-old['stub']:site-old['stub']+4]
    b.install('v51_social_sync_height_consistency',site,f'bl {contacts:#x}\nb finish')
    # Persist a single projection per life. This is a game model, not a
    # clinical prediction. Both known biological parents contribute; a
    # missing parent contributes a neutral baseline. Variation is stable.
    s=b.ctx('life_v18')+b.get('HeightSource51','w19')+'cbnz w19,finish\n'+b.get('AdultHeight','w19',178)
    s+='cmp w19,#178\nb.eq family51_default\n'+b.set('HeightSource51',2)+'b finish\nfamily51_default:\n'
    s+=h.load_game()+'\nldr x27,[x8,#0x20]\ncbz x27,finish\nldr x26,[x8,#0x28]\ncbz x26,finish\nldr x0,[x27,#0xa8]\n'+f'bl {parent:#x}\nmov w19,#178\ncmp w0,#0\ncsel w19,w0,w19,ne\n'
    s+='ldr x0,[x27,#0xb8]\n'+f'bl {parent:#x}\nmov w20,#165\ncmp w0,#0\ncsel w20,w0,w20,ne\nadd w19,w19,w20\n'
    # Native SimPerson.GenderAtBirth getter; do not infer it from names.
    s+='mov x0,x26\nmov x1,xzr\nbl 0x2c42454\ncbnz w0,family51_female\nadd w19,w19,#13\nb family51_mean\nfamily51_female:\nsub w19,w19,#13\nfamily51_mean:\nmov w9,#2\nsdiv w19,w19,w9\n'
    s+='mov x0,x26\nmov x1,xzr\nbl 0x2c44914\ncbz x0,family51_clamp\nldr w11,[x0,#0x10]\nadd x12,x0,#0x14\nmov w13,#5381\nfamily51_hash:\ncbz w11,family51_variation\nldrh w9,[x12],#2\nmov w10,#33\nmadd w13,w13,w10,w9\nsub w11,w11,#1\nb family51_hash\nfamily51_variation:\nand w13,w13,#0x7fffffff\nmov w9,#13\nudiv w10,w13,w9\nmsub w9,w10,w9,w13\nsub w9,w9,#6\nadd w19,w19,w9\nfamily51_clamp:\nmov w9,#140\ncmp w19,w9\ncsel w19,w19,w9,ge\nmov w9,#235\ncmp w19,w9\ncsel w19,w19,w9,le\n'
    s+=b.ctx('life_v18')+b.put('AdultHeight','w19')+b.set('HeightSource51',1)+b.text('HeightSourceName51','Family estimate')+'b finish'
    family=b.routine('v51_ensure_family_projection',s)
    # All profile refreshes use the persisted target. Calling this repeatedly
    # does not reroll growth, including after saving/reloading or Age Up.
    b.chain('v51_family_before_measurements','measurements_at_current_age21',f'bl {family:#x}\nb finish')
    # +0x1c is a verified unused alignment gap in the existing 64-byte
    # scalar draft. Clear it for a fresh draft; preserve it on picker return.
    st=b.states['newlife24']['va']
    s=f'adr x28,{st:#x}\nldr w9,[x28,#56]\ncbnz w9,finish\nstr wzr,[x28,#28]\nb finish'
    b.chain('v51_fresh_height_draft','v21_new_life_native_buttons',s)
    s=f'adr x9,{b.literal("Height: "):#x}\ncmp x1,x9\nb.ne finish\nadr x28,{st:#x}\nldr w9,[x28,#28]\ncbnz w9,finish\n'
    s+=b.string('Height: Family estimate')+'str x0,[sp]\nb return_custom'
    b.chain('v51_family_height_label','newlife34_compact_label',s,ret=True)
    # Explain the default in the existing height picker, without adding a tab.
    extra=b.states['newlife31']['va']
    s=f'cbz x0,finish\nmov x19,x0\nadr x26,{extra:#x}\nldr w9,[x26,#64]\ncmp w9,#1\nb.ne finish\n'
    s+=b.string('Unselected height uses a family estimate. Tap a number to choose an exact adult target.')
    s+='mov x1,x0\nldr x0,[x19,#0x68]\ncbz x0,finish\nmov x2,xzr\nbl 0x3024244\nb finish'
    # Run after the original title routine so its stock detail cannot win.
    title=b.old['newlife31_selector_title_v34_v42']
    before_finish=h.save()+'\n'+body(title)
    detail=b.routine('v51_height_picker_detail',s)
    # Existing jumps to finish must pass through the post-step too.
    b.redirect(title['name'],before_finish+'\nfinish:\nldr x0,[sp]\n'+f'bl {detail:#x}\n'+h.restore()+'\nret')
    # Mark only a validated, explicit height choice. Back never enters these
    # closed callbacks, and another field does not claim the height.
    names=[n for n in b.old if n.startswith('newlife31_choice_0_') and n.rsplit('_',1)[-1].isdigit()]
    assert len(names)==96
    for name in names:
        old=b.old[name];p=b.off(old['stub'])
        ins=list(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(bytes(b.blob[p:p+old['length']]),old['stub']))
        sites=[i.address for i in ins if i.mnemonic=='str'and i.op_str=='w9, [x28, #4]']
        assert len(sites)==1
        # v33 has a busy guard that returns to this precise store. Hook the
        # store, keeping both validation branches and that return address.
        b.install('v51_manual_height_'+name.rsplit('_',1)[-1],sites[0],
            'mov w10,#1\nstr w10,[x28,#28]\nb finish')
    # Birth reaches this instruction after the prior body/genetics hook.
    # The original portrait and native birth implementation remain chained.
    s=f'adr x28,{st:#x}\nldr w19,[x28,#28]\nstr wzr,[x28,#28]\n'+b.ctx('life_v18')+b.set('HeightSource51',0)
    s+='cbz w19,birth51_family\n'+b.set('HeightSource51',2)+b.text('HeightSourceName51','Selected height')+'b birth51_measure\nbirth51_family:\n'
    s+=b.set('AdultHeight',178)+f'bl {family:#x}\nbirth51_measure:\nbl {b.old["measurements_at_current_age21"]["stub"]:#x}\nb finish'
    b.chain('v51_birth_height_provenance','v42_birth_genetics_and_portrait',s)

def patch(raw):
    b=Patch(raw);navigation(b);height(b);return b.finish51()

if __name__=='__main__':
    output=Path(sys.argv[2]);raw=patch(Path(sys.argv[1]).read_bytes())
    tmp=output.with_suffix('.partial')
    with tmp.open('wb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    tmp.replace(output);print(json.dumps(dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())))
