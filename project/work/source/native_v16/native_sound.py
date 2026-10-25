"""Suppress the v15 own-team score callbacks; retain opposition callbacks."""
import copy, hashlib, io, json
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN
from elftools.elf.elffile import ELFFile
from native_v15.native_hooks import asm, restore

ROOT=Path(__file__).resolve().parent
V15_SHA='811cb5f7aa53d977ef7011582ebade814cf319940855512c7473aa521194bae6'
def patch(native):
    assert hashlib.sha256(native).hexdigest()==V15_SHA
    d=json.loads((ROOT.parent/'native_v15/native_hooks.json').read_text())
    loads=[s for s in ELFFile(io.BytesIO(native)).iter_segments()if s['p_type']=='PT_LOAD']
    def off(va):
        s=next(s for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz'])
        return s['p_offset']+va-s['p_vaddr']
    h=next(h for h in d['hooks']if h['name']=='v15_saved_activity_pulses')
    raw=native[off(h['stub']):off(h['stub'])+h['length']]
    restore_bytes=asm(restore(),0)
    assert raw.count(restore_bytes)==1
    finish=h['stub']+raw.index(restore_bytes)
    literals={d['strings'][k]for k in ['LastFor','PenFor','Goals','shootScore','attackScore']}
    sites=[];result=bytearray(native)
    instructions=list(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(raw,h['stub']))
    for index,i in enumerate(instructions):
        target=None
        if i.mnemonic=='adr'and i.op_str.startswith('x0, #0x'):
            target=int(i.op_str.split('#')[1],16)
        elif i.mnemonic=='adrp'and i.op_str.startswith('x0, #0x'):
            following=instructions[index+1]
            if following.mnemonic=='add'and following.op_str.startswith('x0, x0, #'):
                target=int(i.op_str.split('#')[1],16)+int(following.op_str.split('#')[1],0)
        if target in literals:
            at=off(i.address);result[at:at+4]=asm(f'b {finish:#x}',i.address)
            sites.append(dict(va=i.address,file_offset=at,old=i.op_str,new_target=finish))
    assert len(sites)==6
    allowed={p for s in sites for p in range(s['file_offset'],s['file_offset']+4)}
    assert {i for i,(a,b)in enumerate(zip(native,result))if a!=b}<=allowed
    assert len(result)==len(native)
    d.update(binary_sha256=hashlib.sha256(result).hexdigest(),suppressed_own_score_sites=sites,
             feedback_keys={'soccer_v12':['LastAgainst','PenAgainst'],'soccer_v11':['LastAgainst']})
    (ROOT/'native_hooks.json').write_text(json.dumps(d,indent=2))
    return bytes(result),d
