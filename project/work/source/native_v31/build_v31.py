"""Build the narrow New Life and creator-link update on the delivered v30."""
import copy,hashlib,io,json,os,struct,subprocess,sys,zipfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
from build_prison_expansion import signature_entry,sha_file
from native_v27.manifest_version import bump_version
from native_v30.dex_startup30 import Dex
BASE_SHA='c790518c1564b4be8d6baf8e508f2fe8f069677ed5d58e9b91aaf1fc740049b4'
def sha(b):return hashlib.sha256(b).hexdigest()
def run(args):
    p=subprocess.run(list(map(str,args)),capture_output=True,text=True)
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    return p.stdout.strip()
def report(name):return json.loads((ROOT/name).read_text())

def native_integrity(before,after):
    m=report('native_hooks.json');assert sha(after)==m['binary_sha256']
    a,b=ELFFile(io.BytesIO(before)),ELFFile(io.BytesIO(after))
    assert a.header==b.header
    segs=list(a.iter_segments());newsegs=list(b.iter_segments());tail=next(i for i,s in enumerate(segs)if s['p_vaddr']==m['segment_va'])
    ranges=[(a.header.e_phoff+tail*56+32,a.header.e_phoff+tail*56+48)]
    def off(va):
        s=next(s for s in newsegs if s['p_type']=='PT_LOAD'and s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz'])
        return s['p_offset']+va-s['p_vaddr']
    for h in m['hooks']:
        if h['name'].startswith('v31_')or h['name']in ['v21_new_life_native_buttons','v23_dismiss_android_setup_panel']:
            ranges.append((off(h['site']),off(h['site'])+4))
    ranges.append(tuple(off(v)for v in m['v31_new_code_range']))
    ranges.extend((off(v),off(v)+len(s.encode())+1)for s,v in m['v31_new_strings'])
    merged=[]
    for lo,hi in sorted(ranges):
        if merged and lo<=merged[-1][1]:merged[-1][1]=max(hi,merged[-1][1])
        else:merged.append([lo,hi])
    pos=0
    for lo,hi in merged:assert before[pos:lo]==after[pos:lo],(pos,lo);pos=hi
    assert before[pos:]==after[pos:]
    assert len(before)==len(after)
    for i,(old,new)in enumerate(zip(segs,newsegs)):
        expected=dict(old.header)
        if i==tail:expected.update(p_filesz=m['segment_size'],p_memsz=m['segment_size'])
        assert dict(new.header)==expected
    for page in [4096,16384]:
        loads=[s for s in newsegs if s['p_type']=='PT_LOAD']
        assert all(s['p_offset']%page==s['p_vaddr']%page and s['p_filesz']<=s['p_memsz']and s['p_align']>=page for s in loads)
        assert all(x['p_vaddr']+x['p_memsz']<=y['p_vaddr']for x,y in zip(loads,loads[1:]))
    assert a.get_section_by_name('.dynamic').data()==b.get_section_by_name('.dynamic').data()
    assert a.get_section_by_name('.dynsym').data()==b.get_section_by_name('.dynsym').data()
    return dict(passed=True,exact_changed_native_ranges=merged,dependencies_exports_and_loader_metadata_preserved=True,
                original_StartCustomLife_methods_byte_identical=True,load_layout_checked_for_4KB_and_16KB=True)

def build(base,out):
    base=Path(base).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    assert sha_file(base)==BASE_SHA
    checks=report('native31_validation.json');social=report('social31_validation.json');labels=report('labels31_patch.json');effects=report('effects31_validation.json')
    assert checks['arm64_cases']>=1068 and effects['passed']and effects['arm64_cases']>=432 and social['passed']and labels['all_startup_and_logging_code_items_byte_identical']
    replacements={name:(ROOT/name).read_bytes()for name in ['classes12.dex','classes13.dex']}
    for name,data in replacements.items():
        Dex(data);assert sha(data)==(social if name=='classes12.dex'else labels)['binary_sha256']
    replacements['lib/arm64-v8a/libil2cpp.so']=(ROOT/'libil2cpp.so').read_bytes()
    assert sha(replacements['lib/arm64-v8a/libil2cpp.so'])==checks['binary_sha256']
    with zipfile.ZipFile(base)as old:
        manifest,version=bump_version(old.read('AndroidManifest.xml'),old=1074,new=1075)
        integrity=native_integrity(old.read('lib/arm64-v8a/libil2cpp.so'),replacements['lib/arm64-v8a/libil2cpp.so'])
    replacements['AndroidManifest.xml']=manifest
    unsigned=out/'v31-unsigned.tmp';signed=out/'v31-signed.tmp'
    print('Packaging checked native New Life fields and Mod-menu social links.',flush=True)
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
        new.comment=old.comment
    with unsigned.open('r+b')as f:f.flush();os.fsync(f.fileno())
    print('Signing with the existing certificate; checking native signer pin.',flush=True)
    jar=SOURCE/'tools/apksig-8.7.3.jar'
    run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,signed,SOURCE/'signing/music-test-key.pem',SOURCE/'signing/music-test-cert.der'])
    signing={name:run(['java','-cp',jar,SOURCE/name,signed])for name in ['VerifyApk.java','VerifyNativeSigner.java']}
    assert all('verified=true'in v for v in signing.values())
    assert all(s in signing['VerifyApk.java']for s in ['v2=true','v3=true','errors=[]','warnings=[]'])
    assert signing['VerifyNativeSigner.java']==run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',base])
    print('Verifying APK entries, alignment and unchanged game assets.',flush=True)
    changed=[];libraries={};aligned=0
    with zipfile.ZipFile(base)as old,zipfile.ZipFile(signed)as new,signed.open('rb')as file:
        assert new.testzip()is None and len(set(new.namelist()))==len(new.namelist())
        retained={n for n in old.namelist()if not signature_entry(n)}
        assert retained=={n for n in new.namelist()if not signature_entry(n)}
        for entry in new.infolist():
            name=entry.filename
            if signature_entry(name):continue
            before,after=old.read(name),new.read(name)
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
    final=out/'BitLife_MayoMods_v31.apk';signed.replace(final);unsigned.unlink()
    result=dict(version='v31',apk=str(final),size=final.stat().st_size,sha256=sha_file(final),versionCode=1075,
        base_sha256=BASE_SHA,manifest_version=version,changed_apk_entries=changed,
        preserved_apk_entries=len(retained)-len(changed),signing=signing,existing_signer_retained=True,
        native_libraries=libraries,native_libraries_with_16KB_APK_alignment=aligned,
        all_other_22_native_libraries_and_all_Unity_assets_byte_identical=True,
        native_checks=checks,personality_and_Profile_checks=effects,native_integrity=integrity,social_links_checks=social,launcher_label_checks=labels,
        six_body_and_trait_fields_directly_in_New_Life=True,selectors_use_stock_rounded_buttons=True,
        Back_and_choices_refresh_original_New_Life_draft=True,short_labels=True,
        root_close_cancels_draft_and_reopen_rearms_it=True,
        retained_v30_startup_and_crash_logging_bytecode=True,
        ART_verifier_tested=False,BlueStacks_runtime_tested=False,device_runtime_tested=False,
        startup_emulator_dlopen_compatibility_not_established=True)
    for p in [ROOT/'verification.json',out/'BitLife_MayoMods_v31_verification.json']:p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k]for k in ['apk','size','sha256','versionCode','existing_signer_retained']}),flush=True)
    return final

if __name__=='__main__':build(*sys.argv[1:])
