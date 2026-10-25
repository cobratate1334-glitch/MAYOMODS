"""Repair exact v9 menu registry without changing native code or save schemas."""
import copy, hashlib, io, json, os, struct, subprocess, sys, zipfile
from pathlib import Path
import UnityPy
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE));sys.path.insert(0,str(ROOT))
from build_prison_expansion import signature_entry,sha_file
from registry_format import repair,native_rows
from test_registry import validate
BUNDLE='assets/bin/Data/datapack.unity3d'
BASE_SHA='c84bb61476e34dc87a47c74ce5e5950f99bd29951217a0c5d0e8074fb845f7d0'
def sha(b):return hashlib.sha256(b).hexdigest()
def run(args):return subprocess.run(list(map(str,args)),capture_output=True,text=True,check=True).stdout.strip()
def key(o):return o.assets_file.name,o.path_id

def build(base,work):
    base=Path(base).resolve();work=Path(work).resolve();work.mkdir(parents=True,exist_ok=True)
    assert sha_file(base)==BASE_SHA,'requires exact delivered v9 APK'
    with zipfile.ZipFile(base)as z:
        e=UnityPy.load(z.read(BUNDLE));binary=z.read('lib/arm64-v8a/libil2cpp.so')
    before={key(o):sha(o.get_raw_data())for o in e.objects}
    texts={o.read().m_Name:o for o in e.objects if o.type.name=='TextAsset'}
    obj=texts['genesis_feature_containers'];asset=obj.read();old=asset.m_Script
    fixed,changes=repair(old);assert len(changes)==12
    assert repair(fixed)==(fixed,[]),'repair must be idempotent'
    assets={name:o.read().m_Script for name,o in texts.items()}
    routing=validate(binary,old,fixed,assets)
    asset.m_Script=fixed;asset.save()
    bundle=next(iter(e.files.values())).save(packer='original')
    re=UnityPy.load(bundle)
    assert len(list(re.objects))==len(before)
    for o in re.objects:
        if key(o)==key(obj):assert o.read().m_Script==fixed
        else:assert sha(o.get_raw_data())==before[key(o)]
    # The device failure happened before resource loading. Verify the corrected
    # destinations against the actual preserved ResourceManager registrations.
    with zipfile.ZipFile(base)as z:data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'))
    rm=next(o for o in data.objects if o.type.name=='ResourceManager')
    resources=dict(rm.read_typetree()['m_Container'])
    for path in routing['correct_resource_paths']:
        assert path in resources,path
        name=path.split('/',1)[1]
        assert resources[path]['m_PathID']==texts[name].path_id
        external=rm.assets_file.externals[resources[path]['m_FileID']-1]
        assert external.path==texts[name].assets_file.name
    unsigned=work/'v10-unsigned.tmp';signed=work/'v10-signed.tmp'
    with zipfile.ZipFile(base)as oldzip,zipfile.ZipFile(unsigned,'w',allowZip64=False)as new:
        for entry in oldzip.infolist():
            if signature_entry(entry.filename):continue
            info=copy.copy(entry);info.extra=b''
            if info.compress_type==zipfile.ZIP_STORED:
                align=16384 if info.filename.endswith('.so')else 4
                position=new.fp.tell()+30+len(info.filename.encode())
                if position%align:
                    pad=(-position-4)%align
                    if pad<2:pad+=align
                    info.extra=struct.pack('<HHH',0xd935,pad,align)+b'\0'*(pad-2)
            new.writestr(info,bundle if info.filename==BUNDLE else oldzip.read(info.filename),compresslevel=6)
    with unsigned.open('r+b')as f:f.flush();os.fsync(f.fileno())
    assert zipfile.ZipFile(unsigned).testzip()is None
    jar=SOURCE/'tools/apksig-8.7.3.jar'
    run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,signed,SOURCE/'signing/music-test-key.pem',SOURCE/'signing/music-test-cert.der'])
    signing={p:run(['java','-cp',jar,SOURCE/p,signed])for p in ['VerifyApk.java','VerifyNativeSigner.java']}
    assert all('verified=true'in s for s in signing.values())
    assert all(s in signing['VerifyApk.java']for s in ['v2=true','v3=true','errors=[]','warnings=[]'])
    with zipfile.ZipFile(base)as oldzip,zipfile.ZipFile(signed)as new,signed.open('rb')as f:
        assert new.testzip()is None and len(new.namelist())==len(set(new.namelist()))
        assert {x for x in oldzip.namelist()if not signature_entry(x)}=={x for x in new.namelist()if not signature_entry(x)}
        for entry in new.infolist():
            if signature_entry(entry.filename):continue
            assert new.read(entry.filename)==(bundle if entry.filename==BUNDLE else oldzip.read(entry.filename)),entry.filename
            if entry.compress_type==zipfile.ZIP_STORED:
                f.seek(entry.header_offset+26);nm,ex=struct.unpack('<HH',f.read(4))
                assert(entry.header_offset+30+nm+ex)%(16384 if entry.filename.endswith('.so')else 4)==0
    apk=work/'BitLife_Native_Activities_v10_Button_Fix.apk';signed.replace(apk);unsigned.unlink()
    backup=work/'BitLife_Native_Activities_v10_Button_Fix.zip'
    with zipfile.ZipFile(backup,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:z.write(apk,apk.name)
    with zipfile.ZipFile(backup)as z:assert sha(z.read(apk.name))==sha_file(apk)
    result=dict(apk=str(apk),size=apk.stat().st_size,sha256=sha_file(apk),backup=str(backup),base_sha256=BASE_SHA,
                changed_apk_entries=[BUNDLE],changed_unity_objects=[key(obj)],
                corrected_descriptions=changes,routing_tests=routing,signing=signing,
                native_library_unchanged=True,save_schemas_unchanged=True,device_runtime_tested=False)
    (ROOT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'genesis_feature_containers.csv').write_text(fixed)
    print(json.dumps(result,indent=2))
if __name__=='__main__':build(*sys.argv[1:])
