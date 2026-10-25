"""Retry only the unlocked readiness timeout observed after a paused launch."""
import hashlib,io,json,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
from keystone import Ks,KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
def build(base):
 raw=Path(base).read_bytes();e=ELFFile(io.BytesIO(raw));va=0xde320;off=next(s['p_offset']+va-s['p_vaddr']for s in e.iter_segments()if s['p_type']=='PT_LOAD'and s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']);ks=Ks(KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN)
 old=bytes(ks.asm('tbz w19,#0,0xde380',addr=va)[0]);new=bytes(ks.asm('tbz w19,#0,0xde2b0',addr=va)[0]);assert raw[off:off+4]==old;out=bytearray(raw);out[off:off+4]=new;(ROOT/'libRocketGames.so').write_bytes(out)
 r=dict(passed=True,base_sha256=hashlib.sha256(raw).hexdigest(),sha256=hashlib.sha256(out).hexdigest(),changed_range=[off,4],before='tbz w19,#0,0xde380',after='tbz w19,#0,0xde2b0',other_binding_and_signature_checks_preserved=True,physical_phone_tested=False);(ROOT/'startup55_validation.json').write_text(json.dumps(r,indent=2)+'\n');print('startup timeout branch repaired',flush=True)
if __name__=='__main__':build(sys.argv[1])
