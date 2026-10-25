"""Package verified v34 changes with the existing v33 certificate."""
import copy,hashlib,io,json,os,struct,subprocess,sys,zipfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
from build_prison_expansion import signature_entry,sha_file
from native_v27.manifest_version import bump_version
from native_v30.dex_startup30 import Dex
BASE_SHA='3eb3eb17a3584713327e2409641c1dedf53ebb59dcd83935abbd7d49bcc73ac9'
def sha(b):return hashlib.sha256(b).hexdigest()
def run(args):
    p=subprocess.run(list(map(str,args)),capture_output=True,text=True)
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    return p.stdout.strip()
def native_integrity(before,after,manifest):
    a,b=ELFFile(io.BytesIO(before)),ELFFile(io.BytesIO(after));assert a.header==b.header
    old,new=list(a.iter_segments()),list(b.iter_segments())
    def off(va):
        s=next(s for s in new if s['p_type']=='PT_LOAD'and s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz'])
        return s['p_offset']+va-s['p_vaddr']
    ranges=[(off(va),off(va)+n)for va,n,name in manifest['v34_changed_ranges']]
    lo,hi=manifest['v34_new_code_range'];ranges.append((off(lo),off(hi)))
    for i,(x,y)in enumerate(zip(old,new)):
        expected=dict(x.header)
        if x['p_vaddr']==manifest['segment_va']:
            expected.update(p_filesz=manifest['segment_size'],p_memsz=manifest['segment_size'])
            ranges.append((a['e_phoff']+i*56+32,a['e_phoff']+i*56+48))
        if x['p_vaddr']==0x6570000:
            expected['p_memsz']=0x40a0;assert x.data()==y.data()
            ranges.append((a['e_phoff']+i*56+40,a['e_phoff']+i*56+48))
        assert dict(y.header)==expected
    merged=[]
    for lo,hi in sorted(ranges):
        if merged and lo<=merged[-1][1]:merged[-1][1]=max(hi,merged[-1][1])
        else:merged.append([lo,hi])
    pos=0
    for lo,hi in merged:assert before[pos:lo]==after[pos:lo],(pos,lo);pos=hi
    assert before[pos:]==after[pos:] and len(before)==len(after)
    loads=[s for s in new if s['p_type']=='PT_LOAD']
    for page in [4096,16384]:
        assert all(s['p_offset']%page==s['p_vaddr']%page and s['p_filesz']<=s['p_memsz']and s['p_align']>=page for s in loads)
        assert all(x['p_vaddr']+x['p_memsz']<=y['p_vaddr']for x,y in zip(loads,loads[1:]))
    for section in ['.dynamic','.dynsym']:assert a.get_section_by_name(section).data()==b.get_section_by_name(section).data()
    return dict(passed=True,original_RW_payload_byte_identical=True,
        additional_GC_handles_in_loader_zeroed_BSS=True,dependencies_exports_preserved=True,
        load_layout_checked_for_4KB_and_16KB=True,permitted_modified_ranges=merged)

def build(base,native,datapack,out,key,cert):
    base,native,datapack,out,key,cert=map(Path,[base,native,datapack,out,key,cert]);out.mkdir(parents=True,exist_ok=True)
    assert sha_file(base)==BASE_SHA
    reports={name:json.loads((ROOT/(name+'_validation.json')).read_text())for name in ['native34','regressions34','content34','labels34']}
    manifest=json.loads((ROOT/'native_hooks.json').read_text());native_bytes=native.read_bytes()
    assert sha(native_bytes)==manifest['binary_sha256']==reports['native34']['binary_sha256']==reports['regressions34']['binary_sha256']
    assert reports['regressions34']['passed']and reports['content34']['passed']and reports['labels34']['passed']
    replacements={'classes13.dex':(ROOT/'classes13.dex').read_bytes(),
        'lib/arm64-v8a/libil2cpp.so':native_bytes,'assets/bin/Data/datapack.unity3d':datapack.read_bytes()}
    Dex(replacements['classes13.dex']);assert sha(replacements['classes13.dex'])==reports['labels34']['binary_sha256']
    assert sha(replacements['assets/bin/Data/datapack.unity3d'])==reports['content34']['sha256']
    with zipfile.ZipFile(base)as old:
        replacements['AndroidManifest.xml'],version=bump_version(old.read('AndroidManifest.xml'),old=1077,new=1078)
        integrity=native_integrity(old.read('lib/arm64-v8a/libil2cpp.so'),native_bytes,manifest)
    unsigned=out/'v34-unsigned.tmp';signed=out/'v34-signed.tmp'
    print('Packaging the verified v34 APK.',flush=True)
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
    jar=SOURCE/'tools/apksig-8.7.3.jar'
    run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,signed,key,cert])
    signing={name:run(['java','-cp',jar,SOURCE/name,signed])for name in ['VerifyApk.java','VerifyNativeSigner.java']}
    assert all('verified=true'in v for v in signing.values())
    assert all(v in signing['VerifyApk.java']for v in ['v2=true','v3=true','errors=[]','warnings=[]'])
    assert signing['VerifyNativeSigner.java']==run(['java','-cp',jar,SOURCE/'VerifyNativeSigner.java',base])
    changed=[];libraries={};aligned=0
    with zipfile.ZipFile(base)as old,zipfile.ZipFile(signed)as new,signed.open('rb')as f:
        assert new.testzip()is None and len(set(new.namelist()))==len(new.namelist())
        retained={n for n in old.namelist()if not signature_entry(n)}
        assert retained=={n for n in new.namelist()if not signature_entry(n)}
        for item in new.infolist():
            name=item.filename
            if signature_entry(name):continue
            before=old.read(name);after=new.read(name);assert after==replacements.get(name,before),name
            if before!=after:changed.append(name)
            if name.endswith('.so'):
                libraries[name]=sha(after)
                if name!='lib/arm64-v8a/libil2cpp.so':assert after==before
            if item.compress_type==zipfile.ZIP_STORED:
                f.seek(item.header_offset+26);n,e=struct.unpack('<HH',f.read(4))
                assert(item.header_offset+30+n+e)%(16384 if name.endswith('.so')else 4)==0
                if name.endswith('.so'):aligned+=1
        assert set(changed)==set(replacements)and len(libraries)==23
    final=out/'BitLife_MayoMods_v34.apk';signed.replace(final);unsigned.unlink()
    result=dict(version='v34',apk=str(final.resolve()),size=final.stat().st_size,sha256=sha_file(final),versionCode=1078,
        base_sha256=BASE_SHA,manifest_version=version,changed_apk_entries=changed,
        preserved_apk_entries=len(retained)-len(changed),signing=signing,existing_signer_retained=True,
        native_libraries=libraries,native_libraries_with_16KB_APK_alignment=aligned,
        all_other_22_native_libraries_byte_identical=True,native_integrity=integrity,validation=reports,
        other_Unity_objects_byte_identical=True,startup_and_crash_logging_code_preserved=True,
        native_StartCustomLife_and_stock_birth_paths_preserved=True,
        expansion_roadmap_is_pending_not_implemented=True,
        BlueStacks_v32_RocketGames_dlopen_failure_not_fixed_or_runtime_verified=True,
        ART_verifier_tested=False,BlueStacks_runtime_tested=False,device_runtime_tested=False)
    for p in [ROOT/'verification.json',out/'BitLife_MayoMods_v34_verification.json']:p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k]for k in ['apk','size','sha256','versionCode','existing_signer_retained']}),flush=True)

if __name__=='__main__':build(*sys.argv[1:])
