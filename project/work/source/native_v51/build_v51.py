"""Package a pinned v50 sibling update and verify every changed entry."""
import copy,hashlib,io,json,os,struct,sys,zipfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent;sys.path.insert(0,str(SOURCE))
from native_v41.build_v41 import run,signature_entry
from native_v27.manifest_version import bump_version
from native_v48.build_v48 import file_sha
BASE_SHA='f1bba91bbc4059cd92dca49da85495e8ef44fb1b2853c87c99b81d6279798ccd'
sha=lambda b:hashlib.sha256(b).hexdigest()

def build(base,binary,work,out,private):
    base,binary,work,out,private=map(Path,[base,binary,work,out,private])
    work.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
    assert file_sha(base)==BASE_SHA
    reports={n:json.loads((ROOT/(n+'_validation.json')).read_text()) for n in ['native51','content51','retained51','diagnostics51','appearance51']}
    assert all(r['passed'] for r in reports.values())
    replacements={'lib/arm64-v8a/libil2cpp.so':binary.read_bytes(),
        'assets/bin/Data/datapack.unity3d':(ROOT/'bundles/datapack.unity3d').read_bytes(),
        'classes13.dex':(ROOT/'classes13.dex').read_bytes()}
    native=replacements['lib/arm64-v8a/libil2cpp.so'];digest=sha(native)
    assert reports['native51']['binary_sha256']==reports['retained51']['binary_sha256']==digest
    assert reports['appearance51']['binary_sha256']==digest
    assert sha(replacements['assets/bin/Data/datapack.unity3d'])==reports['content51']['assets']['datapack_sha256']
    assert sha(replacements['classes13.dex'])==reports['diagnostics51']['sha256']
    manifest=json.loads((ROOT/'native_hooks.json').read_text())
    loads=[s for s in ELFFile(io.BytesIO(native)).iter_segments() if s['p_type']=='PT_LOAD']
    off=lambda va:next(s['p_offset']+va-s['p_vaddr'] for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz'])
    with zipfile.ZipFile(base) as z:
        before=z.read('lib/arm64-v8a/libil2cpp.so')
        replacements['AndroidManifest.xml'],version=bump_version(z.read('AndroidManifest.xml'),old=1094,new=1095)
        assert sha(z.read('assets/bin/Data/data.unity3d'))==reports['content51']['assets']['data_sha256']
    allowed=bytearray(len(before))
    for va,n,label in manifest['v51_changed_ranges']:p=off(va);allowed[p:p+n]=b'\1'*n
    a,z=manifest['v51_new_code_range'];p=off(a);allowed[p:p+z-a]=b'\1'*(z-a)
    assert len(before)==len(native) and all(a==b or allowed[i] for i,(a,b) in enumerate(zip(before,native)))
    p,n=manifest['v48_file_changed_ranges'][0];assert native[p:p+n]==before[p:p+n]
    unsigned=work/'v51_unsigned.apk';signed=work/'v51_signed.apk'
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
            payload=replacements.get(entry.filename)
            if payload is None:payload=old.read(entry.filename)
            with new.open(info,'w') as stream:
                for i in range(0,len(payload),1048576):stream.write(payload[i:i+1048576])
            new.fp.flush();os.fsync(new.fp.fileno())
        new.comment=old.comment
    key=next(private.rglob('*.pem'));cert=next(private.rglob('*.der'));jar=SOURCE/'tools/apksig-8.7.3.jar'
    run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,signed,key,cert])
    signing=run(['java','-cp',jar,SOURCE/'VerifyApk.java',signed])
    assert all(x in signing for x in ['verified=true','v2=true','v3=true','errors=[]','warnings=[]'])
    assert run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',signed])==run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',base])
    changed=[];preserved=0;libraries=0
    with zipfile.ZipFile(base) as old,zipfile.ZipFile(signed) as new,signed.open('rb') as f:
        assert new.testzip() is None and len(new.namelist())==len(set(new.namelist()))
        assert {n for n in old.namelist() if not signature_entry(n)}=={n for n in new.namelist() if not signature_entry(n)}
        for entry in new.infolist():
            name=entry.filename
            if signature_entry(name):continue
            a,b=old.read(name),new.read(name);assert b==replacements.get(name,a),name
            if a!=b:changed.append(name)
            else:
                preserved+=1
                if name.endswith('.so'):libraries+=1
            if entry.compress_type==zipfile.ZIP_STORED:
                f.seek(entry.header_offset+26);length,extra=struct.unpack('<HH',f.read(4))
                assert (entry.header_offset+30+length+extra)%(16384 if name.endswith('.so') else 4)==0
        assert set(changed)==set(replacements) and libraries==22
    final=out/'BitLife_MayoMods_v51_Stability.apk'
    size=signed.stat().st_size;digest=file_sha(signed);signed.replace(final);unsigned.unlink()
    assert final.stat().st_size==size and file_sha(final)==digest
    report=dict(passed=True,version='v51',versionCode=1095,bytes=size,sha256=digest,
        binary_sha256=sha(native),base_v50_apk_sha256=BASE_SHA,changed_entries=changed,
        preserved_entries=preserved,other_22_native_libraries_byte_identical=True,
        existing_signer_retained=True,signature_verification=signing,
        zip_native_entry_alignment_16KB_verified=True,
        all_native_libraries_ELF_16KB_compatible=False,
        only_declared_native_edit_ranges=True,no_native_segment_growth=True,
        v48_crash_repair_retained=True,social_content_and_existing_tabs_preserved=True,
        atlanti_documents_imported=False,manifest_version=version,validation=reports,
        physical_phone_tested=False,ART_tested=False,Unity_rendering_tested=False)
    text=json.dumps(report,indent=2)+'\n';(ROOT/'verification.json').write_text(text)
    (out/'BitLife_MayoMods_v51_verification.json').write_text(text)
    print(json.dumps(dict(passed=True,bytes=size,sha256=digest)),flush=True)

if __name__=='__main__':build(*sys.argv[1:])
