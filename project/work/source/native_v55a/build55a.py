"""Package the v55 cosmetic fix; only the native stub and 34 textures change."""
import copy, hashlib, json, struct, subprocess, sys, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent
sys.path.insert(0,str(ROOT))
from patch55a import BASE_APK_SHA

sha=lambda b:hashlib.sha256(b).hexdigest()
def signing_entry(n):
    n=n.upper()
    return n=='META-INF/MANIFEST.MF' or (n.startswith('META-INF/') and
           (n.endswith(('.SF','.RSA','.DSA','.EC')) or n.startswith('META-INF/SIG-')))


def build(base,output,key,cert):
    base,output,key,cert=map(Path,[base,output,key,cert])
    output.mkdir(parents=True,exist_ok=True)
    assert sha(base.read_bytes())==BASE_APK_SHA
    native=(ROOT/'libil2cpp.so').read_bytes()
    report=json.loads((ROOT/'patch55a.json').read_text())
    tests=json.loads((ROOT/'native55a_validation.json').read_text())
    artwork=json.loads((ROOT/'assets55a_validation.json').read_text())
    assert tests['passed'] and tests['negative_v55_reproduced']
    assert sha(native)==tests['binary_sha256']==report['binary_sha256']
    bundle=(ROOT/'bundles/datapack.unity3d').read_bytes()
    assert artwork['passed'] and sha(bundle)==artwork['datapack_sha256']
    assert len(artwork['changed_textures'])==34 and artwork['all_other_unity_objects_unchanged']
    changes={'lib/arm64-v8a/libil2cpp.so':native,
             'assets/bin/Data/datapack.unity3d':bundle}
    unsigned=output/'v55_cosmetic_unsigned.apk'
    with zipfile.ZipFile(base)as old,zipfile.ZipFile(unsigned,'w',allowZip64=False)as new:
        for item in old.infolist():
            if signing_entry(item.filename):continue
            info=copy.copy(item);info.extra=b''
            if info.compress_type==zipfile.ZIP_STORED:
                alignment=16384 if info.filename.endswith('.so')else 4
                position=new.fp.tell()+30+len(info.filename.encode())
                if position%alignment:
                    pad=(-position-4)%alignment
                    if pad<2:pad+=alignment
                    info.extra=struct.pack('<HHH',0xd935,pad,alignment)+b'\0'*(pad-2)
            new.writestr(info,changes.get(item.filename,old.read(item.filename)))
        new.comment=old.comment
    final=output/'BitLife_MayoMods_v55_Scar_Eyepatch_Fix.apk'
    jar=SOURCE/'tools/apksig-8.7.3.jar'
    def java(tool,*args):
        r=subprocess.run(['java','-cp',str(jar),str(SOURCE/tool),*map(str,args)],
                         check=True,capture_output=True,text=True)
        return r.stdout
    java('SignApk.java',unsigned,final,key,cert)
    signature=java('VerifyApk.java',final,33,33)
    assert 'verified=true' in signature and 'v3=true' in signature and 'errors=[]' in signature
    assert java('VerifyNativeSigner.java',final)==java('VerifyNativeSigner.java',base)
    preserved=0
    with zipfile.ZipFile(base)as old,zipfile.ZipFile(final)as new,final.open('rb')as f:
        assert new.testzip()is None
        assert len(new.namelist())==len(set(new.namelist()))
        assert {n for n in old.namelist()if not signing_entry(n)}=={n for n in new.namelist()if not signing_entry(n)}
        for i in new.infolist():
            name=i.filename
            if signing_entry(name):continue
            payload=new.read(name);previous=old.read(name)
            assert payload==changes.get(name,previous),name
            if name not in changes:preserved+=1
            if i.compress_type==zipfile.ZIP_STORED:
                f.seek(i.header_offset+26);nl,el=struct.unpack('<HH',f.read(4))
                assert (i.header_offset+30+nl+el)%(16384 if name.endswith('.so')else 4)==0,name
        # Preserve the actual installed v55 package identity, version and DEX.
        assert old.read('AndroidManifest.xml')==new.read('AndroidManifest.xml')
        dex=[n for n in old.namelist()if n.endswith('.dex')]
        assert all(old.read(n)==new.read(n)for n in dex)
        before=old.read('lib/arm64-v8a/libil2cpp.so')
        a=report['file_offset'];b=a+report['new_length']
        assert len(before)==len(native) and before[:a]==native[:a] and before[b:]==native[b:]
        assert old.read('lib/arm64-v8a/libRocketGames.so')==new.read('lib/arm64-v8a/libRocketGames.so')
    unsigned.unlink()
    verification=dict(passed=True,build='v55 scar and eyepatch fix',base_apk_sha256=BASE_APK_SHA,
                      apk=final.name,bytes=final.stat().st_size,sha256=sha(final.read_bytes()),
                      changed_payloads=list(changes),unchanged_payloads=preserved,
                      manifest_and_version_unchanged=True,all_dex_unchanged=True,
                      original_signer_verified=True,signature_android13=signature,
                      elf_headers_and_length_unchanged=True,
                      native_repair=report,artwork=artwork,native_checks=tests,
                      physical_phone_tested=False,installation_on_phone_tested=False,
                      ART_tested=False,Unity_rendering_tested=False)
    (ROOT/'verification55a.json').write_text(json.dumps(verification,indent=2)+'\n')
    (output/'MayoMods_v55_Scar_Eyepatch_Verification.json').write_text(json.dumps(verification,indent=2)+'\n')
    print({'passed':True,'apk':str(final),'bytes':verification['bytes'],
           'changed_payloads':list(changes),'original_v55_identity':True},flush=True)


if __name__=='__main__':build(*sys.argv[1:])
