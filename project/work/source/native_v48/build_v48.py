"""Package the one-instruction v47 crash repair with the existing signer."""
import copy, hashlib, json, os, struct, sys, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
from native_v41.build_v41 import run,signature_entry
from native_v27.manifest_version import bump_version

BASE_SHA='31c192334dcd57fbe15db8743f1d99754e14a3992a5a97aec6f212131672acfc'
sha=lambda data:hashlib.sha256(data).hexdigest()
def file_sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()

def build(base,binary,work,out,private_directory):
    base,binary,work,out,private_directory=map(Path,[base,binary,work,out,private_directory])
    out.mkdir(parents=True,exist_ok=True)
    assert file_sha(base)==BASE_SHA
    reports={name:json.loads((ROOT/(name+'_validation.json')).read_text())
             for name in ['native48','retained48','diagnostics48']}
    assert all(r['passed'] for r in reports.values())
    replacement={'lib/arm64-v8a/libil2cpp.so':binary.read_bytes(),
                 'classes13.dex':(ROOT/'classes13.dex').read_bytes()}
    for name in ['native48','retained48']:
        assert sha(replacement['lib/arm64-v8a/libil2cpp.so'])==reports[name]['binary_sha256']
    assert sha(replacement['classes13.dex'])==reports['diagnostics48']['sha256']
    manifest=json.loads((ROOT/'native_hooks.json').read_text())
    with zipfile.ZipFile(base) as z:
        old=z.read('lib/arm64-v8a/libil2cpp.so');new=replacement['lib/arm64-v8a/libil2cpp.so']
        allowed=set()
        for offset,count in manifest['v48_file_changed_ranges']:allowed.update(range(offset,offset+count))
        assert len(old)==len(new) and all(a==b or i in allowed for i,(a,b) in enumerate(zip(old,new)))
        replacement['AndroidManifest.xml'],version=bump_version(z.read('AndroidManifest.xml'),old=1091,new=1092)
    unsigned=work/'v48_unsigned.apk';signed=work/'v48_signed.apk'
    with zipfile.ZipFile(base) as old,zipfile.ZipFile(unsigned,'w',allowZip64=False) as new:
        for entry in old.infolist():
            if signature_entry(entry.filename):continue
            info=copy.copy(entry);info.extra=b''
            if info.compress_type==zipfile.ZIP_STORED:
                alignment=16384 if info.filename.endswith('.so') else 4
                position=new.fp.tell()+30+len(info.filename.encode())
                if position%alignment:
                    pad=(-position-4)%alignment
                    if pad<2:pad+=alignment
                    info.extra=struct.pack('<HHH',0xd935,pad,alignment)+b'\0'*(pad-2)
            payload=replacement[entry.filename] if entry.filename in replacement else old.read(entry.filename)
            with new.open(info,'w') as stream:
                for offset in range(0,len(payload),1048576):
                    stream.write(payload[offset:offset+1048576])
                    new.fp.flush();os.fsync(new.fp.fileno())
            new.fp.flush();os.fsync(new.fp.fileno())
        new.comment=old.comment
    key=next(private_directory.rglob('*.pem'));cert=next(private_directory.rglob('*.der'))
    jar=SOURCE/'tools/apksig-8.7.3.jar'
    run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,signed,key,cert])
    signing=run(['java','-cp',jar,SOURCE/'VerifyApk.java',signed])
    assert all(value in signing for value in ['verified=true','v2=true','v3=true','errors=[]','warnings=[]'])
    assert run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',signed])==run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',base])
    changed=[];preserved=0;native_preserved=0
    with zipfile.ZipFile(base) as old,zipfile.ZipFile(signed) as new,signed.open('rb') as stream:
        assert new.testzip() is None
        assert len(new.namelist())==len(set(new.namelist()))
        assert {n for n in old.namelist() if not signature_entry(n)}=={n for n in new.namelist() if not signature_entry(n)}
        for entry in new.infolist():
            name=entry.filename
            if signature_entry(name):continue
            before,after=old.read(name),new.read(name)
            assert after==replacement.get(name,before),name
            if before!=after:changed.append(name)
            else:
                preserved+=1
                if name.endswith('.so'):native_preserved+=1
            if entry.compress_type==zipfile.ZIP_STORED:
                stream.seek(entry.header_offset+26);length,extra=struct.unpack('<HH',stream.read(4))
                assert (entry.header_offset+30+length+extra)%(16384 if name.endswith('.so') else 4)==0
        assert set(changed)==set(replacement) and native_preserved==22
    final=out/'BitLife_MayoMods_v48_Menu_Crash_Fix.apk'
    expected_size=signed.stat().st_size;expected_sha=file_sha(signed)
    signed.replace(final);unsigned.unlink()
    assert final.stat().st_size==expected_size and file_sha(final)==expected_sha
    with zipfile.ZipFile(final) as z:assert z.testzip() is None
    report=dict(passed=True,version='v48',versionCode=1092,bytes=expected_size,sha256=expected_sha,
                base_v47_sha256=BASE_SHA,changed_entries=changed,preserved_entries=preserved,
                existing_signer_retained=True,signature_verification=signing,
                other_22_native_libraries_preserved=True,all_Unity_bundles_byte_identical=True,
                social_message_pack_byte_identical=True,all_menu_content_byte_identical=True,
                one_native_instruction_changed=True,stored_entry_alignment_verified=True,
                manifest_version=version,repair=manifest['v48_crash_repair'],validation=reports,
                physical_phone_tested=False,ART_tested=False,Unity_rendering_tested=False)
    text=json.dumps(report,indent=2)+'\n'
    (ROOT/'verification.json').write_text(text)
    (out/'BitLife_MayoMods_v48_verification.json').write_text(text)
    print(json.dumps({k:report[k] for k in ['passed','bytes','sha256','versionCode']}),flush=True)

if __name__=='__main__':build(*sys.argv[1:])
