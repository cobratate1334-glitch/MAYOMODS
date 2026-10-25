"""Package verified v36 changes with the existing certificate."""
import copy,hashlib,io,json,os,struct,subprocess,sys,zipfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
from build_prison_expansion import signature_entry,sha_file
from native_v27.manifest_version import bump_version
from native_v30.dex_startup30 import Dex
BASE_SHA='5922cd2e3dbcbbf2118b309b48b1f343371dcb25fc1a3d887aa46e9e99c753c0'
def sha(b):return hashlib.sha256(b).hexdigest()
def run(args):
    p=subprocess.run(list(map(str,args)),capture_output=True,text=True)
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    return p.stdout.strip()
def build(base,out,key,cert):
    base,out,key,cert=map(Path,[base,out,key,cert]);out.mkdir(parents=True,exist_ok=True);assert sha_file(base)==BASE_SHA
    reports={name:json.loads((ROOT/(name+'_validation.json')).read_text())for name in ['dex36','ui36']};assert all(r['passed']for r in reports.values())
    for p in (ROOT/'java/com/chance/bitlifediag').glob('*.java'):
        assert sha(p.read_bytes())==reports['dex36']['source_sha256'][p.name]==reports['ui36']['source_sha256'][p.name]
    assert sha((ROOT/'tests/LauncherUITest.java').read_bytes())==reports['ui36']['tests_sha256']
    replacements={'classes13.dex':(ROOT/'classes13.dex').read_bytes()};Dex(replacements['classes13.dex']);assert sha(replacements['classes13.dex'])==reports['dex36']['binary_sha256']
    with zipfile.ZipFile(base)as old:replacements['AndroidManifest.xml'],version=bump_version(old.read('AndroidManifest.xml'),old=1079,new=1080)
    unsigned=out/'v36-unsigned.tmp';signed=out/'v36-signed.tmp';print('Packaging v36 with the reference launcher layout.',flush=True)
    with zipfile.ZipFile(base)as old,zipfile.ZipFile(unsigned,'w',allowZip64=False)as new:
        for entry in old.infolist():
            if signature_entry(entry.filename):continue
            info=copy.copy(entry);info.extra=b''
            if info.compress_type==zipfile.ZIP_STORED:
                align=16384 if info.filename.endswith('.so')else 4;pos=new.fp.tell()+30+len(info.filename.encode())
                if pos%align:
                    pad=(-pos-4)%align
                    if pad<2:pad+=align
                    info.extra=struct.pack('<HHH',0xd935,pad,align)+b'\0'*(pad-2)
            new.writestr(info,replacements.get(entry.filename,old.read(entry.filename)),compresslevel=6)
        new.comment=old.comment
    jar=SOURCE/'tools/apksig-8.7.3.jar';run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,signed,key,cert])
    signing={name:run(['java','-cp',jar,SOURCE/name,signed])for name in ['VerifyApk.java','VerifyNativeSigner.java']}
    assert all('verified=true'in v for v in signing.values())
    assert all(v in signing['VerifyApk.java']for v in ['v2=true','v3=true','errors=[]','warnings=[]'])
    assert signing['VerifyNativeSigner.java']==run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',base])
    changed=[];libraries={};aligned=0;assets={}
    with zipfile.ZipFile(base)as old,zipfile.ZipFile(signed)as new,signed.open('rb')as f:
        assert new.testzip()is None and len(set(new.namelist()))==len(new.namelist())
        retained={n for n in old.namelist()if not signature_entry(n)};assert retained=={n for n in new.namelist()if not signature_entry(n)}
        for item in new.infolist():
            name=item.filename
            if signature_entry(name):continue
            before=old.read(name);after=new.read(name);assert after==replacements.get(name,before),name
            if before!=after:changed.append(name)
            if name.endswith('.so'):assert after==before;libraries[name]=sha(after)
            if name in ['assets/bin/Data/data.unity3d','assets/bin/Data/datapack.unity3d']:assert before==after;assets[name]=sha(after)
            if item.compress_type==zipfile.ZIP_STORED:
                f.seek(item.header_offset+26);n,e=struct.unpack('<HH',f.read(4));assert(item.header_offset+30+n+e)%(16384 if name.endswith('.so')else 4)==0
                if name.endswith('.so'):aligned+=1
        assert set(changed)==set(replacements)and len(libraries)==23
    final=out/'BitLife_MayoMods_v36.apk';signed.replace(final);unsigned.unlink()
    previous=json.loads((SOURCE/'native_v35/verification.json').read_text());assert previous['sha256']==BASE_SHA
    assert libraries==previous['native_libraries']
    retained_reports={n:previous['validation'][n]for n in ['retained_selectors35','retained_regressions35','country35','gameplay35','content35']}
    result=dict(version='v36',apk=str(final.resolve()),size=final.stat().st_size,sha256=sha_file(final),versionCode=1080,base_sha256=BASE_SHA,manifest_version=version,
        changed_apk_entries=changed,preserved_apk_entries=len(retained)-len(changed),signing=signing,existing_signer_retained=True,
        native_libraries=libraries,native_libraries_with_16KB_APK_alignment=aligned,all_23_native_libraries_byte_identical=True,
        gameplay_bundles_byte_identical=True,gameplay_bundle_sha256=assets,new_validation=reports,
        retained_v35_validation=retained_reports,retained_checks_not_rerun_because_native_and_game_assets_are_byte_identical=True,
        original_game_launch_and_crash_logging_code_preserved=True,reference_launcher_layout_restored=True,
        main_page_display_toggles_and_position_resets=True,expanded_session_panel_by_default=True,existing_v35_gameplay_preserved=True,
        Android_UI_tested_in_JVM_native_Skia=True,ART_verifier_tested=False,device_runtime_tested=False,BlueStacks_runtime_tested=False,RocketGames_loading_error_unresolved=True)
    for p in [ROOT/'verification.json',out/'BitLife_MayoMods_v36_verification.json']:p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k]for k in ['apk','size','sha256','versionCode','existing_signer_retained']}),flush=True)
if __name__=='__main__':build(*sys.argv[1:])
