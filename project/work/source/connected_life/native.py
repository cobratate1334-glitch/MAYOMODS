"""Hash-pinned repairs to the device-reported 1106; retain old code and add isolated RX/BSS."""
import copy,hashlib,io,json,struct,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(SOURCE),str(SOURCE/'native_v29')]
from native_hooks import Builder,h
from native_v55.patch_native55 import Patch as Previous

BASE='b6600573b50e8461d0f3fcf377c40940271105bf4d59be2b1a7c285677e587a5'
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
        new_mem=self.state+2048-rw['p_vaddr'];struct.pack_into('<Q',table,segments.index(rw)*56+40,new_mem)
        assert all(s is rw or s['p_type']!='PT_LOAD' or self.state+2048<=s['p_vaddr'] or self.state>=s['p_vaddr']+s['p_memsz'] for s in segments)
        blob[ph:ph+len(table)]=table;struct.pack_into('<H',blob,56,count)
        Builder.__init__(self,bytes(blob));self.before_native=raw
        self.manifest=copy.deepcopy(self.base);self.old={r['name']:r for r in self.base['hooks']+self.base['routines']}
        self.rxoff,self.rxva=self.added_off,self.added_va;self.tail=next(s for s in self.loads if s['p_vaddr']==self.added_va)
        self.cursor=self.code_start=self.added_va;self.strings=copy.deepcopy(self.base['strings']);self.strings_va=self.string_cursor=self.added_va+0x180000
        self.states=copy.deepcopy(self.base['states']);self.states['connected_life']=dict(va=self.state,size=2048)
        self.newlife24=self.states['newlife24']['va'];self.newlife31=self.states['newlife31']['va'];self.state52=self.states['ui52']['va']
        self.hooks=[];self.routines=[];self.changed=[];self.serial=0;self.snprintf=self.plt('snprintf');self.trace23=self.old['persist_new_life_checkpoint23']['stub'];self.journal55=self.old['v55_append_native_life_journal']['stub']
        self.program_ranges=[[56,2],[ph,len(table)]]
    def resolved(self,name):
        from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
        row=self.old[name];seen=set()
        while row['stub'] not in seen:
            seen.add(row['stub'])
            ins=next(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(bytes(self.blob[self.off(row['stub']):self.off(row['stub'])+4]),row['stub']))
            if ins.mnemonic!='b':break
            target=int(ins.op_str.lstrip('#'),16)
            records=self.routines+self.hooks+list(self.old.values())
            nxt=next((r for r in records if r['stub']==target),None)
            if nxt is None:break
            row=nxt
        return row
    def redirect(self,name,source):
        old=next((r for r in self.routines+self.hooks if r['name']==name),self.old.get(name))
        assert old is not None,name
        target=self.add_code(name+'_1110_'+str(len(self.routines)),source)
        self.write(old['stub'],f'b {target:#x}',name)
        for row in self.manifest['hooks']+self.manifest['routines']+self.routines+self.hooks:
            if row['stub']==old['stub']:row.update(source=f'b {target:#x}',length=4)
        return target
    def install(self,name,site,code,ret=False,custom_resume=None):
        from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
        ins=next(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(bytes(self.blob[self.off(site):self.off(site)+4]),site))
        original=ins.mnemonic+' '+ins.op_str
        source=h.save()+'\n'+code+'\nfinish:\n'+h.restore()+'\n'+original+f'\nb {site+4:#x}'
        if ret or custom_resume is not None:source+='\nreturn_custom:\n'+h.restore()+('\nret'if custom_resume is None else f'\nb {custom_resume:#x}')
        va=self.add_code(name,source);r=self.routines.pop();self.write(site,f'b {va:#x}',name)
        self.hooks.append(dict(name=name,site=site,stub=va,resume=site+4,original=original,source=r['source'],length=r['length'],custom_resume=custom_resume));self.changed.append([site,4,name])
    def finish(self,out):
        assert self.cursor<self.strings_va and self.string_cursor<self.added_va+self.added_size
        for s,va in self.strings.items():
            if s in self.base['strings']:continue
            raw=s.encode()+b'\0';p=self.off(va);assert self.blob[p:p+len(raw)]==b'\0'*len(raw);self.blob[p:p+len(raw)]=raw
        sites={r['site'] for r in self.hooks}
        for r in self.manifest['hooks']:
            if r['site']in sites and r['name']not in {x['name']for x in self.manifest['routines']}:self.manifest['routines'].append(r)
        self.manifest['hooks']=[r for r in self.manifest['hooks']if r['site']not in sites]+self.hooks;self.manifest['routines']+=self.routines
        self.manifest.update(binary_sha256=hashlib.sha256(self.blob).hexdigest(),strings=self.strings,states=self.states,connected_life_base=BASE,connected_life_rx=[self.added_off,self.added_va,self.added_size],connected_life_code=[self.code_start,self.cursor],connected_life_changes=self.changed,connected_life_headers=self.program_ranges)
        Path(out).write_text(json.dumps(self.manifest,indent=2)+'\n');return bytes(self.blob)


def hooks(b):
    from connected_life.repairs import hooks as repairs
    from connected_life.events import hooks as events
    from connected_life.integration import hooks as integration
    from connected_life.appearance import hooks as appearance
    repairs(b);integration(b);events(b);appearance(b)

if __name__=='__main__':
    b=Patch(Path(sys.argv[1]).read_bytes(),sys.argv[2]);hooks(b)
    Path(sys.argv[3]).write_bytes(b.finish(sys.argv[4]))
