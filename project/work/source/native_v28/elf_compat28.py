"""Place ELF program headers in the first load segment for older native bridges.

All instructions, symbols, relocations, library dependencies and native checks
stay intact. Metadata overlapped by the conventional header location moves to
already mapped data: Rocket's notes use its old header slot; IL2CPP's GNU hash
extends the final RW data segment. This is a compatibility candidate, not a
confirmed diagnosis of BlueStacks' generic `dlopen failed` message.
"""
import hashlib, io, json, struct, sys, zipfile
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parent
BASE_SHA = '82c5d1ae84d1ebf94aea511291fcfed1ab818c5df4fda01a7a0b6ce6a93abfb2'
NAMES = ['libRocketGames.so', 'libil2cpp.so']

def sha(data): return hashlib.sha256(data).hexdigest()
def pack_phdr(row):
    return struct.pack('<II6Q', *row)
def rows(data):
    off = struct.unpack_from('<Q', data, 32)[0]
    count = struct.unpack_from('<H', data, 56)[0]
    return [list(struct.unpack_from('<II6Q', data, off+i*56)) for i in range(count)]

def patch(data, name):
    elf = ELFFile(io.BytesIO(data))
    assert elf.header.e_machine == 'EM_AARCH64' and elf.elfclass == 64
    old_phoff = elf.header.e_phoff
    table = rows(data); header_end = 64 + len(table)*56
    assert table[0][0] == 6 and old_phoff > 1024*1024
    assert next(p for p in table if p[0] == 1)[2:4] == [0, 0]
    assert not any(p[0] == 1 and p[3] < header_end and p[2] != 0 for p in table)
    out = bytearray(data); allowed = set(range(32, 40)) | set(range(64, header_end))
    moves = []
    def move_section(section, file_offset, virtual_address):
        start, size = section['sh_offset'], section['sh_size']
        # Allocatable content is preserved exactly at its new mapped location.
        assert bytes(out[file_offset:file_offset+size]) == data[start:start+size]
        index = next(i for i, s in enumerate(elf.iter_sections()) if s.name == section.name)
        p = elf.header.e_shoff + index*elf.header.e_shentsize
        struct.pack_into('<QQ', out, p+16, virtual_address, file_offset)
        allowed.update(range(p+16, p+32))
        moves.append(dict(section=section.name, from_file=start, to_file=file_offset,
                          from_vaddr=section['sh_addr'], to_vaddr=virtual_address, size=size))

    if name == 'libRocketGames.so':
        note = next(p for p in table if p[0] == 4)
        old_note_file, old_note_va, size = note[2], note[3], note[5]
        assert old_note_file < header_end and size == 188
        slot = next(p for p in table if p[0] == 1 and p[2] <= old_phoff < p[2]+p[5])
        new_va = slot[3] + old_phoff - slot[2]
        assert old_phoff+size <= old_phoff+len(table)*56
        out[old_phoff:old_phoff+size] = data[old_note_file:old_note_file+size]
        allowed.update(range(old_phoff, old_phoff+size))
        for section in elf.iter_sections():
            if section['sh_type'] == 'SHT_NOTE' and old_note_file <= section['sh_offset'] < old_note_file+size:
                rel = section['sh_offset'] - old_note_file
                move_section(section, old_phoff+rel, new_va+rel)
        note[2:5] = [old_phoff, new_va, new_va]
    elif name == 'libil2cpp.so':
        section = elf.get_section_by_name('.gnu.hash')
        assert section['sh_offset'] < header_end < section['sh_offset']+section['sh_size']
        last = max((p for p in table if p[0] == 1), key=lambda p:p[3])
        assert last[1] == 6 and last[5] == last[6] == 128
        new_off = last[2]+last[5]; new_va = last[3]+last[5]
        assert new_off == len(data)
        payload = section.data(); out.extend(payload)
        last[5] += len(payload); last[6] = last[5]
        assert last[5] <= 16384
        move_section(section, new_off, new_va)
        dynamic = elf.get_section_by_name('.dynamic')
        position = next(dynamic['sh_offset']+i*16+8 for i,t in enumerate(dynamic.iter_tags())
                        if t.entry.d_tag == 'DT_GNU_HASH')
        assert struct.unpack_from('<Q', data, position)[0] == section['sh_addr']
        struct.pack_into('<Q', out, position, new_va); allowed.update(range(position, position+8))
    else: raise AssertionError(name)
    table[0][2:7] = [64, 64, 64, len(table)*56, len(table)*56]
    out[64:header_end] = b''.join(pack_phdr(p) for p in table)
    struct.pack_into('<Q', out, 32, 64)
    assert {i for i in range(len(data)) if data[i] != out[i]} <= allowed
    new = ELFFile(io.BytesIO(out))
    assert new.header.e_phoff == 64 and new.header.e_phnum == elf.header.e_phnum
    for section in elf.iter_sections():
        if section.name in ['.note.android.ident', '.note.gnu.build-id', '.gnu.hash']:
            assert section.data() == new.get_section_by_name(section.name).data()
    report = dict(original_sha256=sha(data), binary_sha256=sha(out), name=name,
                  old_phoff=old_phoff, new_phoff=64, program_header_count=len(table),
                  metadata_moves=moves, bytes_added=len(out)-len(data),
                  only_ELF_headers_and_metadata_changed=True,
                  dependencies_and_native_checks_retained=True,
                  older_native_bridge_layout_candidate=True, BlueStacks_runtime_tested=False)
    return bytes(out), report

def prepare(apk_path, analysis_path):
    apk_path, analysis_path = Path(apk_path), Path(analysis_path)
    assert sha(apk_path.read_bytes()) == BASE_SHA
    analysis_path.mkdir(parents=True, exist_ok=True); reports = []
    with zipfile.ZipFile(apk_path) as apk:
        for name in NAMES:
            original = apk.read('lib/arm64-v8a/'+name)
            patched, report = patch(original, name)
            (analysis_path / (name+'.v27')).write_bytes(original)
            (ROOT / name).write_bytes(patched); reports.append(report)
    (ROOT / 'elf28_patch.json').write_text(json.dumps(reports, indent=2)+'\n')
    print(json.dumps(reports), flush=True)

if __name__ == '__main__': prepare(*sys.argv[1:])
