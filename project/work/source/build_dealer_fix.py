"""Guard the runtime-confirmed black-market weapon selection failure.

Keep valid weighted selection unchanged, retry an empty filtered pool using the
loaded weapon catalogue, clamp invalid indices, and let a truly missing stock
item be skipped by the vendor's existing null-item path. No save edits.
"""
from pathlib import Path
import argparse, copy, hashlib, io, json, os, struct, subprocess, zipfile
from elftools.elf.elffile import ELFFile
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN
from keystone import Ks, KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN
from build_prison_expansion import signature_entry, sha_file

ROOT = Path(__file__).resolve().parent
BASELINE = 'f2ced1723c507d737b2af58c953ac6e71127deb7c54b8c2a432c4e1802f4446c'
LIB = 'lib/arm64-v8a/libil2cpp.so'
INDEX_SITE = 0x277b194
INDEX_RESUME = 0x277b19c
COUNT_RETRY = 0x277b150
EMPTY_RETURN = 0x277b1dc
ITEM_SITE = 0x2a93598
ITEM_RESUME = 0x2a9359c
ITEM_RETURN = 0x2a936dc
ITEM_THROW = 0x2a936fc

def align(value, boundary=16384): return (value+boundary-1)//boundary*boundary
def assemble(code, address): return bytes(Ks(KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN).asm(code,addr=address)[0])
def patch_library(original):
    elf = ELFFile(io.BytesIO(original))
    assert elf['e_machine'] == 'EM_AARCH64' and elf['e_type'] == 'ET_DYN'
    segments = list(elf.iter_segments())
    loads = [s for s in segments if s['p_type']=='PT_LOAD']
    def offset(address):
        segment = next(s for s in loads if s['p_vaddr'] <= address < s['p_vaddr']+s['p_filesz'])
        return segment['p_offset']+address-segment['p_vaddr']
    # Check the original instructions and the vendor's existing null-item skip.
    assert original[offset(INDEX_SITE):offset(INDEX_SITE)+8] == assemble('ldr x8, [x19]; mov w1, w0',INDEX_SITE)
    assert original[offset(ITEM_SITE):offset(ITEM_SITE)+4] == assemble('cbz x22, 0x2a936fc',ITEM_SITE)
    assert original[offset(0x2a99c00):offset(0x2a99c00)+4] == assemble('cbz x0, 0x2a99c58',0x2a99c00)
    assert original[offset(INDEX_RESUME):offset(INDEX_RESUME)+4] == assemble('mov x0, x19',INDEX_RESUME)
    assert original[offset(COUNT_RETRY):offset(COUNT_RETRY)+4] == assemble('ldr x8, [x19]',COUNT_RETRY)
    assert original[offset(0x277af0c):offset(0x277af0c)+4] == assemble('ldr x0, [x8, #0xeb8]',0x277af0c)

    # Append a read/execute segment with a relocated program-header table.
    # Existing segments, sections, relocations and method addresses do not move.
    phoff, va = align(len(original)), align(max(s['p_vaddr']+s['p_memsz'] for s in loads))
    phnum, phentsize = elf['e_phnum']+1, elf['e_phentsize']
    assert phentsize == 56 and phnum == 12
    code_offset = align(phnum*phentsize,16)
    index_address = va+code_offset
    index_source = f'''
        cmp w20, #0
        b.gt valid
        adrp x8, 0x5c24000
        ldr x8, [x8, #0x318]
        cbz x8, empty
        ldr x8, [x8]
        cbz x8, empty
        ldr x8, [x8, #0xb8]
        cbz x8, empty
        ldr x8, [x8, #0xeb8]
        cbz x8, empty
        cmp x8, x19
        b.eq empty
        mov x19, x8
        b {COUNT_RETRY:#x}
    valid:
        mov w1, w0
        cmp w1, #0
        csel w1, w1, wzr, ge
        sub w8, w20, #1
        cmp w1, w20
        csel w1, w1, w8, lt
        ldr x8, [x19]
        b {INDEX_RESUME:#x}
    empty:
        mov x0, xzr
        b {EMPTY_RETURN:#x}
    '''
    index_bytes = assemble(index_source,index_address)
    item_address = align(index_address+len(index_bytes),16)
    item_source = f'''
        cbz x0, missing
        cbz x22, original_throw
        b {ITEM_RESUME:#x}
    original_throw:
        b {ITEM_THROW:#x}
    missing:
        mov x0, xzr
        b {ITEM_RETURN:#x}
    '''
    item_bytes = assemble(item_source,item_address)
    length = item_address+len(item_bytes)-va
    old_phoff = elf['e_phoff']
    phdrs = [bytearray(original[old_phoff+i*56:old_phoff+(i+1)*56]) for i in range(phnum-1)]
    assert struct.unpack_from('<I',phdrs[0])[0] == 6
    phdrs[0] = bytearray(struct.pack('<II6Q',6,4,phoff,va,va,phnum*56,phnum*56,8))
    phdrs.append(bytearray(struct.pack('<II6Q',1,5,phoff,va,va,length,length,16384)))
    patched = bytearray(original)+bytearray(phoff-len(original)+length)
    struct.pack_into('<Q',patched,32,phoff)
    struct.pack_into('<H',patched,56,phnum)
    patched[phoff:phoff+phnum*56] = b''.join(phdrs)
    patched[phoff+code_offset:phoff+code_offset+len(index_bytes)] = index_bytes
    item_file = phoff+item_address-va
    patched[item_file:item_file+len(item_bytes)] = item_bytes
    for site,target in [(INDEX_SITE,index_address),(ITEM_SITE,item_address)]:
        instruction = assemble(f'b {target:#x}',site)
        assert len(instruction) == 4
        patched[offset(site):offset(site)+4] = instruction
    allowed = set(range(32,40))|set(range(56,58))|set(range(offset(INDEX_SITE),offset(INDEX_SITE)+4))|set(range(offset(ITEM_SITE),offset(ITEM_SITE)+4))
    changed_offsets = [i for i in range(len(original)) if original[i] != patched[i]]
    assert set(changed_offsets) <= allowed
    rewritten = ELFFile(io.BytesIO(patched))
    new_segments = list(rewritten.iter_segments())
    for i in range(1,len(segments)): assert new_segments[i].header == segments[i].header
    assert [s.header for s in rewritten.iter_sections()] == [s.header for s in elf.iter_sections()]
    new_loads = [s for s in new_segments if s['p_type']=='PT_LOAD']
    assert [s['p_vaddr'] for s in new_loads] == sorted(s['p_vaddr'] for s in new_loads)
    assert all(s['p_filesz']<=s['p_memsz'] and s['p_offset']+s['p_filesz']<=len(patched) and s['p_vaddr']%s['p_align']==s['p_offset']%s['p_align'] for s in new_loads)
    assert new_loads[-1]['p_flags']==5 and new_loads[-1]['p_align']==16384
    assert new_segments[0]['p_vaddr']+new_segments[0]['p_filesz'] <= new_loads[-1]['p_vaddr']+new_loads[-1]['p_filesz']
    md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN)
    disassembly='\n'.join(f'{i.address:#x} {i.mnemonic} {i.op_str}' for i in md.disasm(index_bytes,index_address))
    disassembly+='\n\n'+'\n'.join(f'{i.address:#x} {i.mnemonic} {i.op_str}' for i in md.disasm(item_bytes,item_address))
    details={'index_stub_va':index_address,'item_stub_va':item_address,'segment_va':va,'segment_offset':phoff,'segment_size':length,
        'changed_original_byte_offsets':changed_offsets,'new_elf_program_headers':phnum,
        'all_original_section_addresses_and_non_phdr_segments_preserved':True,
        'index_stub_source':index_source,'item_stub_source':item_source,'stub_disassembly':disassembly}
    return bytes(patched),details

def validate_content(apk):
    import UnityPy
    from build_prison_expansion import decode,records
    with zipfile.ZipFile(apk) as z: env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'))
    found=[]
    for obj in env.objects:
        if obj.type.name=='TextAsset':
            asset=obj.read()
            if asset.m_Name=='a16_black-market-weapons-enc': found.append(records(decode(asset.m_Script)))
    assert len(found)==1
    fields=found[0][0];rows=[dict(zip(fields,row)) for row in found[0][1:]]
    assert len(rows)==60 and [int(r['ID']) for r in rows] == list(range(600,660))
    counts={}
    for fake in [False,True]:
        for rare in [False,True]:
            pool=[r for r in rows if (not fake or r['Can Be Fake']=='x') and (not rare or int(r['Commonness Score'])<=2)]
            size=sum(int(r['Commonness Score']) for r in pool)
            assert size>0
            counts[f'onlyFake={fake},mustBeRare={rare}']={'records':len(pool),'weighted_entries':size}
    return counts

def build(apk,work):
    apk,work=Path(apk).resolve(),Path(work).resolve();work.mkdir(parents=True,exist_ok=True)
    assert sha_file(apk)==BASELINE
    pools=validate_content(apk)
    with zipfile.ZipFile(apk) as z: original=z.read(LIB)
    replacement,details=patch_library(original)
    patched_library=work/'libil2cpp-fixed.so';patched_library.write_bytes(replacement)
    (ROOT/'dealer_fix_details.json').write_text(json.dumps(details,indent=2)+'\n')
    import sys
    sys.path.insert(0,str(ROOT/'tests'))
    from dealer_guard_test import validate
    test_result=validate(replacement,details)
    readelf=subprocess.run(['readelf','-lW',str(patched_library)],capture_output=True,text=True,check=True)
    assert not readelf.stderr,readelf.stderr
    (ROOT/'dealer_fix_elf_program_headers.txt').write_text(readelf.stdout)
    unsigned,signed=work/'dealer-unsigned.tmp',work/'dealer-signed.tmp'
    with zipfile.ZipFile(apk) as src,zipfile.ZipFile(unsigned,'w',allowZip64=False) as dst:
        for entry in src.infolist():
            if signature_entry(entry.filename):continue
            info=copy.copy(entry);info.extra=b''
            if info.compress_type==zipfile.ZIP_STORED:
                boundary=16384 if info.filename.endswith('.so') else 4
                position=dst.fp.tell()+30+len(info.filename.encode('utf8'))
                if position%boundary:
                    pad=(-position-4)%boundary;info.extra=struct.pack('<HH',0xd935,pad)+b'\0'*pad
            dst.writestr(info,replacement if entry.filename==LIB else src.read(entry.filename),compresslevel=6)
        dst.comment=src.comment
    with unsigned.open('r+b') as f:f.flush();os.fsync(f.fileno())
    with zipfile.ZipFile(unsigned) as z:assert z.testzip() is None
    jar=ROOT/'tools/apksig-8.7.3.jar'
    assert sha_file(jar)=='c070ed1394629d74641aa0906f60b2ffa1ee77e6366a1f93437f59717b1aeb89'
    subprocess.run(['java','-cp',str(jar),str(ROOT/'SignApk.java'),str(unsigned),str(signed),str(ROOT/'signing/music-test-key.pem'),str(ROOT/'signing/music-test-cert.der')],check=True,capture_output=True)
    checks={}
    for program in ['VerifyApk.java','VerifyNativeSigner.java']:
        checks[program]=subprocess.run(['java','-cp',str(jar),str(ROOT/program),str(signed)],check=True,capture_output=True,text=True).stdout.strip()
        assert 'verified=true' in checks[program]
    assert all(x in checks['VerifyApk.java'] for x in ['v2=true','v3=true','errors=[]','warnings=[]'])
    changed=[]
    with zipfile.ZipFile(apk) as old,zipfile.ZipFile(signed) as new,signed.open('rb') as f:
        assert new.testzip() is None and len(new.namelist())==len(set(new.namelist()))
        assert {n for n in old.namelist() if not signature_entry(n)}=={n for n in new.namelist() if not signature_entry(n)}
        for entry in new.infolist():
            if not signature_entry(entry.filename) and old.read(entry.filename)!=new.read(entry.filename):changed.append(entry.filename)
            if entry.compress_type==zipfile.ZIP_STORED:
                f.seek(entry.header_offset+26);name,extra=struct.unpack('<HH',f.read(4))
                assert (entry.header_offset+30+name+extra)%(16384 if entry.filename.endswith('.so') else 4)==0
        assert changed==[LIB]
        f.seek(-22,2);eocd=struct.unpack('<4s4H2IH',f.read(22))
        assert eocd[0]==b'PK\x05\x06' and eocd[-1]==0 and eocd[5]+eocd[6]+22==signed.stat().st_size
    with signed.open('r+b') as f:f.flush();os.fsync(f.fileno())
    final=work/'BitLife_Age_and_Dealer_Fix.apk';signed.replace(final);unsigned.unlink()
    report={'input_sha256':BASELINE,'output_sha256':sha_file(final),'output_bytes':final.stat().st_size,
        'observed_failure':'ArgumentOutOfRangeException in DataHub.GetRandomBlackMarketWeapon during SimBlackMarket.IncrementAge',
        'correction':'Bounds guard; empty filtered pool fallback; existing vendor null-item skip enabled safely',
        'source_of_invalid_runtime_index_or_empty_pool':'Not established by supplied stack alone',
        'changed_entries':changed,'weapon_pool_validation':pools,'weapons_retained':60,'new_firearms_retained':18,
        'all_gameplay_assets_manifest_dex_and_other_native_entries_byte_preserved':True,
        'arm64_emulation':test_result,'signature_checks':checks,'archive_crc_eocd_alignment':'passed',
        'existing_elf_section_and_load_addresses_preserved':True,'phone_runtime_tested':False,
        'limitation':'Addresses the identified selector failure; other gameplay bugs may require separate repair.'}
    (ROOT/'dealer_fix_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('apk');p.add_argument('work');a=p.parse_args();build(a.apk,a.work)
