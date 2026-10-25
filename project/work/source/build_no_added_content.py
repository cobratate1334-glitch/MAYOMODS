"""Controlled comparison against the V4 native-collector experiment.

Remove the exact appended music rows, not arbitrary game content. The original
untouched bundle is unavailable: CSV is reserialized, so this is not an exact
binary restoration of the working original APK.
"""
import argparse, copy, csv, hashlib, io, json, struct, subprocess, zipfile
from pathlib import Path
import UnityPy
from build_expansion import BUNDLE, decode, encode, records, signature_entry

EXPECTED='06340597e06c9b7087d838bcafa07f97239e9b65528e02e84fe2ca56ce7481f8'

def sha(data):return hashlib.sha256(data).hexdigest()

def run(apk,out):
    root=Path(__file__).resolve().parent;apk=Path(apk).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    assert hashlib.file_digest(apk.open('rb'),'sha256').hexdigest()==EXPECTED,'Unsupported or incomplete comparison input'
    authored=json.loads((root/'music_content.json').read_text())
    prior=json.loads((root/'verification.json').read_text())['tables']
    with zipfile.ZipFile(apk) as z:env=UnityPy.load(z.read(BUNDLE))
    before={obj.path_id:sha(obj.get_raw_data()) for obj in env.objects}
    expected_rows={};modified=set();counts={}
    for obj in env.objects:
        if obj.type.name!='TextAsset':continue
        asset=obj.read();name=asset.m_Name
        if name not in authored:continue
        assert name not in expected_rows,'Duplicate target asset'
        rows=records(decode(asset.m_Script));header=rows[0]
        tail=[[entry.get(f,'') for f in header] for entry in authored[name]]
        assert len(rows)-1==prior[name]['total'],'Unexpected row count'
        assert rows[-len(tail):]==tail,'Authored suffix differs; refusing destructive removal'
        kept=rows[:-len(tail)]
        assert len(kept)-1==prior[name]['original']
        s=io.StringIO(newline='');csv.writer(s,lineterminator='\r\n').writerows(kept)
        asset.m_Script=encode(s.getvalue());assert records(decode(asset.m_Script))==kept
        asset.save();expected_rows[name]=kept;modified.add(obj.path_id)
        counts[name]={'remaining_original_rows':len(kept)-1,'removed_authored_rows':len(tail)}
    assert set(expected_rows)==set(authored)
    rebuilt_bytes=next(iter(env.files.values())).save(packer='original')
    rebuilt=UnityPy.load(rebuilt_bytes);seen=set();verified=set()
    for obj in rebuilt.objects:
        seen.add(obj.path_id)
        if obj.path_id in modified:
            asset=obj.read();assert records(decode(asset.m_Script))==expected_rows[asset.m_Name];verified.add(asset.m_Name)
        else:assert sha(obj.get_raw_data())==before[obj.path_id],'Unrelated Unity object changed'
    assert seen==set(before) and verified==set(authored)
    unsigned=out/'no-added-content-unsigned.apk'
    with zipfile.ZipFile(apk) as src,zipfile.ZipFile(unsigned,'w',allowZip64=False) as dst:
        for entry in src.infolist():
            if signature_entry(entry.filename):continue
            info=copy.copy(entry);info.extra=b''
            if info.compress_type==zipfile.ZIP_STORED:
                alignment=16384 if info.filename.endswith('.so') else 4
                offset=dst.fp.tell()+30+len(info.filename.encode('utf8'))
                if offset%alignment:
                    pad=(-offset-4)%alignment;info.extra=struct.pack('<HH',0xd935,pad)+b'\x00'*pad
            dst.writestr(info,rebuilt_bytes if entry.filename==BUNDLE else src.read(entry.filename),compresslevel=6)
        dst.comment=src.comment
    target=out/'BitLife_NO_ADDED_CONTENT_TEST.apk';jar=root/'tools/apksig-8.7.3.jar'
    assert sha(jar.read_bytes())=='c070ed1394629d74641aa0906f60b2ffa1ee77e6366a1f93437f59717b1aeb89'
    subprocess.run(['java','--class-path',str(jar),str(root/'SignApk.java'),str(unsigned),str(target),str(root/'signing/music-test-key.pem'),str(root/'signing/music-test-cert.der')],check=True)
    verifier=subprocess.run(['java','--class-path',str(jar),str(root/'VerifyApk.java'),str(target)],check=True,capture_output=True,text=True).stdout
    assert 'verified=true' in verifier and 'v2=true' in verifier and 'v3=true' in verifier
    changed=[]
    with zipfile.ZipFile(apk) as old,zipfile.ZipFile(target) as new:
        assert new.testzip() is None and len(new.namelist())==len(set(new.namelist()))
        assert {n for n in new.namelist() if not signature_entry(n)}=={n for n in old.namelist() if not signature_entry(n)}
        for entry in new.infolist():
            name=entry.filename
            if not signature_entry(name) and old.read(name)!=new.read(name):changed.append(name)
            if entry.compress_type==zipfile.ZIP_STORED:
                with target.open('rb') as f:f.seek(entry.header_offset+26);fn,extra=struct.unpack('<HH',f.read(4))
                assert (entry.header_offset+30+fn+extra)%(16384 if name.endswith('.so') else 4)==0,'Misaligned stored file'
        assert changed==[BUNDLE],changed
    report={'test':'remove exactly the authored rows from V4; keep other variables as in V4',
      'input_sha256':EXPECTED,'output_sha256':hashlib.file_digest(target.open('rb'),'sha256').hexdigest(),
      'output_bytes':target.stat().st_size,'removed_entries':sum(v['removed_authored_rows'] for v in counts.values()),'tables':counts,
      'unchanged_unrelated_unity_objects':len(before)-len(modified),'changed_apk_entries':changed,
      'dex_native_libraries_manifest_protection_checks_unchanged':True,'same_package_and_personal_test_signing_identity':True,
      'embrace_native_collector_setting':'disabled as in V4; not changed by this test',
      'diagnostic_screen':'V4 labels retained to keep DEX identical',
      'original_game_rows_preserved':True,'original_apk_or_bundle_byte_for_byte_restored':False,
      'limitation':'Original untouched bundle unavailable; remaining CSV rows were reserialized. A failed test cannot exclude bundle serialization or other changes.',
      'apk_crc_and_alignment':'passed','official_signature_verifier':verifier,'phone_runtime_tested':False,'game_crash_fixed':'not established'}
    assert report['removed_entries']==196
    (root/'no_added_content_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('apk');p.add_argument('--out',default='output-no-added-content')
    a=p.parse_args();run(a.apk,a.out)
