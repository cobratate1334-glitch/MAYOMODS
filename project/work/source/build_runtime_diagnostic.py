"""Enable Unity Full logging for Error and Exception; preserve game content."""
import copy, json, os, struct, subprocess, zipfile
from pathlib import Path
import UnityPy
from build_prison_expansion import sha, sha_file, signature_entry

ROOT = Path(__file__).resolve().parent
BASELINE = 'e46e80a007e63441dcbb87772b187c2c08e826577f466fa002b147f31c93b22a'
BUNDLE = 'assets/bin/Data/data.unity3d'

def build(apk, out):
    apk, out = Path(apk).resolve(), Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    assert sha_file(apk) == BASELINE
    with zipfile.ZipFile(apk) as z:
        env = UnityPy.load(z.read(BUNDLE))
    def key(obj):
        return obj.assets_file.name, obj.path_id
    before = {key(o): sha(o.get_raw_data()) for o in env.objects}
    settings = [o for o in env.objects if o.type.name == 'PlayerSettings']
    assert len(settings) == 1
    o = settings[0]
    # The bundled UnityPy type tree omits four trailing bytes in Unity 6000.3.
    # Read only to identify this early field; preserve the whole raw object.
    old_tree = o.read_typetree(check_read=False)
    assert old_tree['m_StackTraceTypes'] == [1] * 6
    raw = o.get_raw_data()
    needle = struct.pack('<9i', 6, 1, 1, 1, 1, 1, 1, -1, -1)
    assert raw.count(needle) == 1
    offset = raw.index(needle) + 4
    changed = bytearray(raw)
    for index in [0, 4]:
        struct.pack_into('<i', changed, offset + index * 4, 2)
    expected = bytes(changed)
    assert len(expected) == len(raw)
    assert [i for i, (a, b) in enumerate(zip(raw, expected)) if a != b] == [offset, offset + 16]
    o.set_raw_data(expected)
    payload = next(iter(env.files.values())).save(packer='original')
    rebuilt = UnityPy.load(payload)
    assert {key(x) for x in rebuilt.objects} == set(before)
    for x in rebuilt.objects:
        assert x.get_raw_data() == expected if key(x) == key(o) else sha(x.get_raw_data()) == before[key(x)]
        if key(x) == key(o):
            new_tree = x.read_typetree(check_read=False)
            assert new_tree['m_StackTraceTypes'] == [2, 1, 1, 1, 2, 1]
            assert {k:v for k,v in new_tree.items() if k != 'm_StackTraceTypes'} == {k:v for k,v in old_tree.items() if k != 'm_StackTraceTypes'}
    unsigned, stage = out/'runtime-unsigned.tmp', out/'runtime-signed.tmp'
    with zipfile.ZipFile(apk) as src, zipfile.ZipFile(unsigned, 'w', allowZip64=False) as dst:
        for entry in src.infolist():
            if signature_entry(entry.filename):
                continue
            info = copy.copy(entry)
            info.extra = b''
            if info.compress_type == zipfile.ZIP_STORED:
                alignment = 16384 if info.filename.endswith('.so') else 4
                position = dst.fp.tell() + 30 + len(info.filename.encode('utf8'))
                if position % alignment:
                    pad = (-position - 4) % alignment
                    info.extra = struct.pack('<HH', 0xd935, pad) + b'\0' * pad
            dst.writestr(info, payload if info.filename == BUNDLE else src.read(info.filename), compresslevel=6)
        dst.comment = src.comment
    with unsigned.open('r+b') as f:
        f.flush()
        os.fsync(f.fileno())
    with zipfile.ZipFile(unsigned) as z:
        assert z.testzip() is None
    jar = ROOT/'tools/apksig-8.7.3.jar'
    assert sha_file(jar) == 'c070ed1394629d74641aa0906f60b2ffa1ee77e6366a1f93437f59717b1aeb89'
    subprocess.run(['java','--class-path',str(jar),str(ROOT/'SignApk.java'),str(unsigned),str(stage),str(ROOT/'signing/music-test-key.pem'),str(ROOT/'signing/music-test-cert.der')], check=True)
    checks = {}
    for program in ['VerifyApk.java', 'VerifyNativeSigner.java']:
        result = subprocess.run(['java','--class-path',str(jar),str(ROOT/program),str(stage)],capture_output=True,text=True,check=True)
        assert 'verified=true' in result.stdout
        checks[program] = result.stdout.strip()
    changed_entries = []
    with zipfile.ZipFile(apk) as old, zipfile.ZipFile(stage) as new, stage.open('rb') as handle:
        assert new.testzip() is None
        assert len(new.namelist()) == len(set(new.namelist()))
        assert {n for n in old.namelist() if not signature_entry(n)} == {n for n in new.namelist() if not signature_entry(n)}
        for entry in new.infolist():
            if not signature_entry(entry.filename) and old.read(entry.filename) != new.read(entry.filename):
                changed_entries.append(entry.filename)
            if entry.compress_type == zipfile.ZIP_STORED:
                handle.seek(entry.header_offset + 26)
                fn, ex = struct.unpack('<HH', handle.read(4))
                assert (entry.header_offset + 30 + fn + ex) % (16384 if entry.filename.endswith('.so') else 4) == 0
        assert changed_entries == [BUNDLE]
        assert old.read('AndroidManifest.xml') == new.read('AndroidManifest.xml')
    with stage.open('rb') as f:
        f.seek(-22,2)
        eocd = struct.unpack('<4s4H2IH',f.read(22))
    assert eocd[0] == b'PK\x05\x06' and eocd[-1] == 0
    assert eocd[5] + eocd[6] + 22 == stage.stat().st_size
    with stage.open('r+b') as f:
        f.flush()
        os.fsync(f.fileno())
    final = out/'BitLife_Runtime_Diagnostic.apk'
    stage.replace(final)
    report = {'input_sha256':BASELINE, 'output_sha256':sha_file(final), 'output_bytes':final.stat().st_size,
        'status':'Diagnostic only; age-up and dealer bugs unresolved',
        'stack_trace_types_before':[1]*6, 'stack_trace_types_after':[2,1,1,1,2,1],
        'player_settings_raw_byte_changes':[offset,offset+16], 'changed_apk_entries':changed_entries,
        'unrelated_unity_objects_preserved':len(before)-1, 'all_content_dex_native_manifest_preserved':True,
        'signature_checks':checks, 'zip_crc_eocd_alignment':'passed', 'phone_runtime_tested':False,
        'limitation':'Full engine logging may provide native addresses; missing compiled exception stack information may remain unavailable.'}
    (ROOT/'runtime_diagnostic_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    unsigned.unlink()
    print(json.dumps(report,indent=2))

if __name__ == '__main__':
    import sys
    build(sys.argv[1],sys.argv[2])
