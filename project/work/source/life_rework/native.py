"""Hash-pinned follow-up to 1103; retain old code and add isolated RX/BSS."""
import copy,hashlib,io,json,struct,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(SOURCE),str(SOURCE/'native_v29')]
from native_hooks import Builder,h
from native_v55.patch_native55 import Patch as Previous

BASE='929c6be10ffa9f8295db06cca701feb38713d437a701c1cc8ec5a1b1bffc40ef'
class Patch(Previous):
    def __init__(self,raw,manifest):
        assert hashlib.sha256(raw).hexdigest()==BASE
        self.base=json.loads(Path(manifest).read_text());assert self.base['binary_sha256']==BASE
        e=ELFFile(io.BytesIO(raw));segments=list(e.iter_segments());count=len(segments)+1
        self.added_off=(len(raw)+0x3fff)&~0x3fff
        self.added_va=(max(s['p_vaddr']+s['p_memsz'] for s in segments if s['p_type']=='PT_LOAD')+0x3fff)&~0x3fff
        self.added_size=0x200000
        blob=bytearray(raw);blob.extend(b'\0'*(self.added_off+self.added_size-len(blob)))
        ph=e['e_phoff'];table=bytearray(raw[ph:ph+len(segments)*56]);pi=next(i for i,s in enumerate(segments)if s['p_type']=='PT_PHDR')
        struct.pack_into('<QQ',table,pi*56+32,count*56,count*56)
        table+=struct.pack('<IIQQQQQQ',1,5,self.added_off,self.added_va,self.added_va,self.added_size,self.added_size,0x4000)
        assert ph+len(table)<=self.base['v49_new_rx'][0]+0x1000
        # The new state contains scalar flags/GC handles, never managed pointers.
        rw=max((s for s in segments if s['p_type']=='PT_LOAD'and s['p_flags']&2),key=lambda s:s['p_vaddr'])
        self.state=(rw['p_vaddr']+rw['p_memsz']+15)&~15
        new_mem=self.state+128-rw['p_vaddr'];struct.pack_into('<Q',table,segments.index(rw)*56+40,new_mem)
        assert all(s is rw or s['p_type']!='PT_LOAD' or self.state+128<=s['p_vaddr'] or self.state>=s['p_vaddr']+s['p_memsz'] for s in segments)
        blob[ph:ph+len(table)]=table;struct.pack_into('<H',blob,56,count)
        Builder.__init__(self,bytes(blob));self.before_native=raw
        self.manifest=copy.deepcopy(self.base);self.old={r['name']:r for r in self.base['hooks']+self.base['routines']}
        self.rxoff,self.rxva=self.added_off,self.added_va;self.tail=next(s for s in self.loads if s['p_vaddr']==self.added_va)
        self.cursor=self.code_start=self.added_va;self.strings=copy.deepcopy(self.base['strings']);self.strings_va=self.string_cursor=self.added_va+0x180000
        self.states=copy.deepcopy(self.base['states']);self.states['life_rework']=dict(va=self.state,size=128)
        self.newlife24=self.states['newlife24']['va'];self.newlife31=self.states['newlife31']['va'];self.state52=self.states['ui52']['va']
        self.hooks=[];self.routines=[];self.changed=[];self.serial=0;self.snprintf=self.plt('snprintf');self.trace23=self.old['persist_new_life_checkpoint23']['stub'];self.journal55=self.old['v55_append_native_life_journal']['stub']
        self.program_ranges=[[56,2],[ph,len(table)]]
    def install(self,name,site,code,ret=False,custom_resume=None):
        from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
        ins=next(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(bytes(self.blob[self.off(site):self.off(site)+4]),site))
        original=ins.mnemonic+' '+ins.op_str
        source=h.save()+'\n'+code+'\nfinish:\n'+h.restore()+'\n'+original+f'\nb {site+4:#x}'
        if ret or custom_resume is not None:source+='\nreturn_custom:\n'+h.restore()+('\nret'if custom_resume is None else f'\nb {custom_resume:#x}')
        va=self.add_code(name,source);r=self.routines.pop();self.write(site,f'b {va:#x}',name)
        self.hooks.append(dict(name=name,site=site,stub=va,resume=site+4,original=original,source=r['source'],length=r['length'],custom_resume=custom_resume))
    def finish(self,out):
        assert self.cursor<self.strings_va and self.string_cursor<self.added_va+self.added_size
        for s,va in self.strings.items():
            if s in self.base['strings']:continue
            raw=s.encode()+b'\0';p=self.off(va);assert self.blob[p:p+len(raw)]==b'\0'*len(raw);self.blob[p:p+len(raw)]=raw
        sites={r['site'] for r in self.hooks}
        for r in self.manifest['hooks']:
            if r['site']in sites and r['name']not in {x['name']for x in self.manifest['routines']}:self.manifest['routines'].append(r)
        self.manifest['hooks']=[r for r in self.manifest['hooks']if r['site']not in sites]+self.hooks;self.manifest['routines']+=self.routines
        self.manifest.update(binary_sha256=hashlib.sha256(self.blob).hexdigest(),strings=self.strings,states=self.states,life_rework_base=BASE,life_rework_rx=[self.added_off,self.added_va,self.added_size],life_rework_code=[self.code_start,self.cursor],life_rework_changes=self.changed,life_rework_headers=self.program_ranges)
        Path(out).write_text(json.dumps(self.manifest,indent=2)+'\n');return bytes(self.blob)

def replace_text(b,name,replacements):
    r=b.resolved(name);s=r['source'];changed=False
    for old,new in replacements.items():
        if old not in b.strings:continue
        va=b.strings[old]
        for needle in [f'adrp x0, {va&~4095:#x}\nadd x0, x0, #{va&4095}',f'adr x0,{va:#x}',f'adr x0, {va:#x}']:
            if needle in s:s=s.replace(needle,f'adr x0,{b.literal(new):#x}');changed=True
    if changed:b.redirect(r['name'],s)

def eras(b):
    from native_v45.catalog45 import PLATFORMS
    year=b.old['v45_current_year']['stub']
    for name,start in PLATFORMS.items():
        old=b.old['v45_social_'+name];site=old['site']
        # v52 restored the original construction instruction at this exact site.
        assert bytes(b.blob[b.off(site):b.off(site)+4])==h.asm(old['original'],site)
        b.install('life_rework_social_'+name,site,f'bl {year:#x}\ncmp w0,#{start}\nb.lt return_custom\nb finish',custom_resume=old['custom_resume'])
    # Apply the same rules to the added platforms and direct Roblox callbacks.
    sites=[('discord19',2015),('reddit19',2005),('roblox_social',2006)]
    s='cbz x19,finish\ncbz x21,finish\nldr x8,[x19,#16]\ncbz x8,finish\n'
    for i,(owner,start)in enumerate(sites):
        s+=h.compare_key(owner,f'era_rework_{i}',f'era_rework_next_{i}')+f'\nera_rework_{i}:\nbl {year:#x}\ncmp w0,#{start}\nb.ge finish\nmov w9,#1\nstrb w9,[x21,#0xd0]\nb finish\nera_rework_next_{i}:\n'
    s+='b finish';b.chain('life_rework_added_platform_years','v19_grey_entry_requirements',s)

def genetics(b):
    # SetupDarklyButton's x7 is the native emoji name. Previously every
    # rounded choice deliberately passed null here, hiding its icon.
    old=b.resolved('newlife31_add_rounded_option');s=old['source'];needle='mov x20,xzr\n';assert s.count(needle)==1
    icons={'Face editor':'49-eye','Hair & facial hair':'49-hair','Skin & eye colours':'49-skin','Genetic features':'49-eye','Scars & eyepatches':'49-patch','Inherited abilities':'brain','Hairstyle':'49-hair','Hair colour':'49-hair','Facial hair':'49-beard','Facial hair colour':'49-beard','Skin tone':'49-skin','Eye colour':'49-eye','Eye patterns':'49-eye','Skin markings':'49-skin','Hair & face traits':'49-hair','Scars':'49-scar','Eyepatches':'49-patch','Save & back':'49-wardrobe','Back without saving':'49-gate','More choices':'books','Previous choices':'books','Surprise me':'49-hair','Reset this look':'49-wardrobe','Modding community':'mayomods1104/reddit','1880 · WWI adulthood':'calendar','1890 · WWI adulthood':'calendar'}
    code='mov x8,x22\n'
    for i,(label,icon)in enumerate(icons.items()):
        if icon.startswith('49-'):icon='mayomods49/icons/'+icon
        code+=h.compare_key(label,f'rework_icon_{i}',f'rework_icon_next_{i}')+f'\nrework_icon_{i}:\n'+b.string(icon)+'mov x20,x0\nb rework_icon_done\n'+f'rework_icon_next_{i}:\n'
    code+=b.string('mayomods49/icons/49-wardrobe')+'mov x20,x0\nrework_icon_done:\n'
    b.redirect(old['name'],s.replace(needle,code,1))
    # Keep rooted native controls and the exact isolated preview implementation.
    # Random/reset update the draft only; they never write the active life.
    st=b.state52;extra=b.newlife31;ns=b.newlife24
    guard=f'cbz x0,finish\nmov x19,x0\nadr x26,{extra:#x}\nldr w9,[x26,#64]\ncmp w9,#130\nb.ne finish\nldr x0,[x26,#72]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\n'
    callbacks=[]
    for random in [True,False]:
        s=guard+f'adr x28,{st:#x}\n'
        for off,n in [(32,16),(36,9),(40,9),(44,7),(48,1),(52,1),(56,7),(60,9)]:
            s+=(b.rng(n,'w24') if random and n>1 else 'mov w24,#0\n')+f'str w24,[x28,#{off}]\n'
        s+=f'adr x8,{b.states["era44"]["va"]:#x}\nldr w9,[x8]\ncmp w9,#1980\nb.ge random_style_year_ready\nmov w9,#9\nstr w9,[x28,#32]\nrandom_style_year_ready:\nadr x8,{ns:#x}\nstr wzr,[x8,#24]\nmov x0,x19\nbl {b.old["v53_appearance_page_header"]["stub"]:#x}\nb finish'
        callbacks.append(b.routine('life_rework_'+('random_draft'if random else'reset_draft'),s))
    old=b.resolved('v53_organized_appearance_setup');s=old['source'];marker='setup53_hub_next_130:';assert marker in s
    back=b.strings['Back to New Life'];before=s.index(f'adrp x0, {back&~4095:#x}\nadd x0, x0, #{back&4095}\n')
    add=b.old['newlife31_add_rounded_option']['stub'];buttons=''
    community=b.routine('life_rework_open_modding_community',guard+f'mov w0,#1901\nbl {b.trace23:#x}\nb finish')
    for label,callback in zip(['Surprise me','Reset this look','Modding community'],callbacks+[community]):buttons+=b.string(label)+f'mov x1,x0\nmov x0,x19\nadr x2,{callback:#x}\nmov w3,#1\nbl {add:#x}\n'
    b.redirect(old['name'],s[:before]+buttons+s[before:])
    replace_text(b,'v53_appearance_page_header',{'Choose a category.':'Pick a style. Changes stay in this new-life preview.','Preview your choice, then Save & back.':'Tap to preview. Save keeps it. Back cancels.'})
    # The extra circuit is removed; the original Fight Club lists remain.
    for name in ['intro','gym']:
        r=b.old['v52_fighter_circuit_in_native_'+name];b.write(r['site'],r['original'],'remove separate fighter circuit entry')

def hooks(b):
    eras(b);genetics(b)
    from life_rework.systems import hooks as systems
    systems(b)
    from life_rework.portraits import hooks as portrait_hooks,height
    portrait_hooks(b);height(b)
    from life_rework.era_genetics import hooks as era_genetics
    era_genetics(b)
    from life_rework.branding import hooks as branding
    branding(b)
    from life_rework.early_years import hooks as early_years
    early_years(b)

if __name__=='__main__':
    b=Patch(Path(sys.argv[1]).read_bytes(),sys.argv[2]);hooks(b);Path(sys.argv[3]).write_bytes(b.finish(sys.argv[4]))
