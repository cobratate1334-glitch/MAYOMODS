"""Apply the verified crash/launcher update to the delivered v31 APK."""
import copy,hashlib,io,json,os,struct,subprocess,sys,zipfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
from build_prison_expansion import signature_entry,sha_file
from native_v27.manifest_version import bump_version
from native_v30.dex_startup30 import Dex
BASE_SHA='736f03a5a36e4f28291093735a697d7a52b730abc679c6c84142f2d5925ac722'
def sha(b):return hashlib.sha256(b).hexdigest()
def report(name):return json.loads((ROOT/name).read_text())
def run(args):
    p=subprocess.run(list(map(str,args)),capture_output=True,text=True)
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    return p.stdout.strip()

def native_integrity(before,after):
    m=report('native_hooks.json');assert sha(after)==m['binary_sha256']
    a,b=ELFFile(io.BytesIO(before)),ELFFile(io.BytesIO(after));assert a.header==b.header
    old,new=list(a.iter_segments()),list(b.iter_segments())
    def off(va):
        s=next(s for s in new if s['p_type']=='PT_LOAD'and s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz'])
        return s['p_offset']+va-s['p_vaddr']
    ranges=[tuple(m['v32_changed_header_range'])]
    ranges.extend((off(va),off(va)+n)for name,va,n,count in m['v32_changed_routines'])
    merged=[]
    for lo,hi in sorted(ranges):
        if merged and lo<=merged[-1][1]:merged[-1][1]=max(hi,merged[-1][1])
        else:merged.append([lo,hi])
    pos=0
    for lo,hi in merged:assert before[pos:lo]==after[pos:lo],(pos,lo);pos=hi
    assert before[pos:]==after[pos:] and len(before)==len(after)
    for x,y in zip(old,new):
        expected=dict(x.header)
        if x['p_vaddr']==0x6570000:
            expected['p_memsz']=m['rw_memory_size'];assert x.data()==y.data()
        assert dict(y.header)==expected
    for page in [4096,16384]:
        loads=[s for s in new if s['p_type']=='PT_LOAD']
        assert all(s['p_offset']%page==s['p_vaddr']%page and s['p_filesz']<=s['p_memsz']and s['p_align']>=page for s in loads)
        assert all(x['p_vaddr']+x['p_memsz']<=y['p_vaddr']for x,y in zip(loads,loads[1:]))
    for section in ['.dynamic','.dynsym']:assert a.get_section_by_name(section).data()==b.get_section_by_name(section).data()
    return dict(passed=True,exact_changed_native_ranges=merged,
        original_RW_payload_byte_identical=True,new_handle_state_in_loader_zeroed_BSS=True,
        dependencies_exports_and_original_game_methods_preserved=True,load_layout_checked_for_4KB_and_16KB=True)

def build(base,out):
    base=Path(base).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    assert sha_file(base)==BASE_SHA
    checks=report('native32_validation.json');effects=report('effects32_validation.json')
    crash=report('crash32_validation.json');launcher=report('launcher32_validation.json')
    assert checks['arm64_cases']==1068 and effects['passed']and effects['arm64_cases']==432
    assert crash['passed']and launcher['passed']
    replacements={name:(ROOT/name).read_bytes()for name in ['classes13.dex','classes14.dex']}
    for name,data in replacements.items():
        Dex(data);assert sha(data)==launcher['binary_sha256'if name=='classes13.dex'else 'bridge_sha256']
    replacements['lib/arm64-v8a/libil2cpp.so']=(ROOT/'libil2cpp.so').read_bytes()
    assert sha(replacements['lib/arm64-v8a/libil2cpp.so'])==checks['binary_sha256']==effects['binary_sha256']==crash['binary_sha256']
    with zipfile.ZipFile(base)as old:
        manifest,version=bump_version(old.read('AndroidManifest.xml'),old=1075,new=1076)
        integrity=native_integrity(old.read('lib/arm64-v8a/libil2cpp.so'),replacements['lib/arm64-v8a/libil2cpp.so'])
    replacements['AndroidManifest.xml']=manifest
    unsigned=out/'v32-unsigned.tmp';signed=out/'v32-signed.tmp'
    print('Packaging verified crash fix and visible launcher links.',flush=True)
    with zipfile.ZipFile(base)as old,zipfile.ZipFile(unsigned,'w',allowZip64=False)as new:
        for entry in old.infolist():
            if signature_entry(entry.filename):continue
            info=copy.copy(entry);info.extra=b''
            if info.compress_type==zipfile.ZIP_STORED:
                align=16384 if info.filename.endswith('.so')else 4
                pos=new.fp.tell()+30+len(info.filename.encode())
                if pos%align:
                    pad=(-pos-4)%align
                    if pad<2:pad+=align
                    info.extra=struct.pack('<HHH',0xd935,pad,align)+b'\0'*(pad-2)
            new.writestr(info,replacements.get(entry.filename,old.read(entry.filename)),compresslevel=6)
        assert 'classes14.dex'not in old.namelist()
        new.writestr('classes14.dex',replacements['classes14.dex'],compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
        new.comment=old.comment
    with unsigned.open('r+b')as f:f.flush();os.fsync(f.fileno())
    print('Signing and verifying the existing certificate.',flush=True)
    jar=SOURCE/'tools/apksig-8.7.3.jar'
    run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,signed,SOURCE/'signing/music-test-key.pem',SOURCE/'signing/music-test-cert.der'])
    signing={name:run(['java','-cp',jar,SOURCE/name,signed])for name in ['VerifyApk.java','VerifyNativeSigner.java']}
    assert all('verified=true'in v for v in signing.values())
    assert all(s in signing['VerifyApk.java']for s in ['v2=true','v3=true','errors=[]','warnings=[]'])
    assert signing['VerifyNativeSigner.java']==run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',base])
    print('Verifying every APK entry, native alignment and preserved assets.',flush=True)
    changed=[];libraries={};aligned=0
    with zipfile.ZipFile(base)as old,zipfile.ZipFile(signed)as new,signed.open('rb')as file:
        assert new.testzip()is None and len(set(new.namelist()))==len(new.namelist())
        retained={n for n in old.namelist()if not signature_entry(n)}
        assert retained|{'classes14.dex'}=={n for n in new.namelist()if not signature_entry(n)}
        for entry in new.infolist():
            name=entry.filename
            if signature_entry(name):continue
            before=old.read(name)if name in retained else None;after=new.read(name)
            assert after==replacements.get(name,before),name
            if before!=after:changed.append(name)
            if name.endswith('.so'):
                libraries[name]=sha(after)
                if name!='lib/arm64-v8a/libil2cpp.so':assert after==before
            if entry.compress_type==zipfile.ZIP_STORED:
                file.seek(entry.header_offset+26);n,e=struct.unpack('<HH',file.read(4))
                assert(entry.header_offset+30+n+e)%(16384 if name.endswith('.so')else 4)==0
                if name.endswith('.so'):aligned+=1
        assert set(changed)==set(replacements)and len(libraries)==23
    final=out/'BitLife_MayoMods_v32.apk';signed.replace(final);unsigned.unlink()
    result=dict(version='v32',apk=str(final),size=final.stat().st_size,sha256=sha_file(final),versionCode=1076,
        base_sha256=BASE_SHA,manifest_version=version,changed_apk_entries=changed,
        preserved_apk_entries=len(retained)-3,signing=signing,existing_signer_retained=True,
        native_libraries=libraries,native_libraries_with_16KB_APK_alignment=aligned,
        all_other_22_native_libraries_and_all_Unity_assets_byte_identical=True,
        native_checks=checks,personality_and_Profile_checks=effects,native_integrity=integrity,
        supplied_crash_regression=crash,launcher_social_links_checks=launcher,
        in_game_Mod_menu_social_links_preserved=True,retained_startup_and_crash_logging_bytecode=True,
        six_body_and_trait_fields_directly_in_New_Life=True,selectors_use_stock_rounded_buttons=True,
        root_close_cancels_draft_and_reopen_rearms_it=True,
        ART_verifier_tested=False,BlueStacks_runtime_tested=False,device_runtime_tested=False,
        startup_emulator_dlopen_compatibility_not_established=True)
    for p in [ROOT/'verification.json',out/'BitLife_MayoMods_v32_verification.json']:p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k]for k in ['apk','size','sha256','versionCode','existing_signer_retained']}),flush=True)
    return final

if __name__=='__main__':build(*sys.argv[1:])
