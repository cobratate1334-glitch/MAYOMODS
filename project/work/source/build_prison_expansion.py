"""Expand eight existing prison pools in the verified native-signature repair.

Preserves the 196 music entries, every original prison row, unrelated Unity
objects, all DEX/native code, manifest and the personal signing identity.
"""
import argparse, base64, collections, copy, csv, hashlib, io, json, re, struct, subprocess, zipfile
from pathlib import Path
import UnityPy

BASELINE_SHA256='cd8ede10fb75cb909cf2718ef7fe43eff97935af80bc2f95e3c05bb00e998c4b'
BUNDLE='assets/bin/Data/datapack.unity3d'
KEY=b'yst.odkzffq.zfshhs16'
EXPECTED_COUNTS={
 'a16_dumb-scenarios-prison-enc':80, 'a16_prison-parole-questions-enc':25,
 'a16_prison-bully-inbound-scenarios-enc':20, 'a16_prison-bully-outbound-scenarios-enc':20,
 'a16_prison-letters-enc':30, 'a16_prison-gifts-enc':25,
 'a16_prison-jobs-enc':20, 'a16_prison-nicknames-enc':30}

def sha(data):return hashlib.sha256(data).hexdigest()
def sha_file(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def signature_entry(name):
    return name.upper()=='META-INF/MANIFEST.MF' or bool(re.fullmatch(r'META-INF/[^/]+\.(SF|RSA|DSA|EC)',name,re.I))
def decode(script):
    text=base64.b64decode(script,validate=True).decode('utf8')
    return ''.join(chr(ord(c)^KEY[i%len(KEY)]) for i,c in enumerate(text))
def encode(text):
    return base64.b64encode(''.join(chr(ord(c)^KEY[i%len(KEY)]) for i,c in enumerate(text)).encode('utf8')).decode('ascii')
def records(text):
    rows=list(csv.reader(io.StringIO(text,newline='')))
    assert rows and len(set(rows[0]))==len(rows[0])
    assert all(len(row)==len(rows[0]) for row in rows[1:]),'Unequal CSV field counts'
    return rows

def validate(name,original,additions):
    header=original[0];tokens=set(re.findall(r'<[^<>]+>',str(original)))
    seen=set();old_rows={tuple(r) for r in original[1:]}
    for new in additions:
        assert set(new)<=set(header),'Unsupported field in '+name
        assert all(isinstance(v,str) for v in new.values()),'Non-string CSV value'
        assert set(re.findall(r'<[^<>]+>',str(new)))<=tokens,'Unsupported template token in '+name
        row=tuple(new.get(f,'') for f in header)
        assert row not in old_rows|seen,'Duplicate content row in '+name
        seen.add(row)
        for f,value in new.items():
            if 'Impact' in f:assert -4<=int(value)<=4,'Unsafe stat effect range'
        if name=='a16_dumb-scenarios-prison-enc':
            assert new['Hero Min Age']=='18' and not new.get('Hero Max Age')
            assert new['Title'].startswith('Prison+: ')
            for i in range(1,5):
                assert new.get(f'Choice {i}') and new.get(f'Narrative {i}')
        elif name=='a16_prison-parole-questions-enc':
            assert 1<=int(new['Commonness'])<=5
            for i in range(1,19):
                assert new.get(f'Choice {i}') and 1<=int(new[f'Choice {i} Score'])<=5
            assert not new.get('Choice 19') and not new.get('Choice 20')
        elif name=='a16_prison-jobs-enc':
            assert new['Daily Rate'] in {'$1','$2','$3','$4','$5'}
            assert 1<=int(new['Commonness Score'])<=5
        elif name=='a16_prison-gifts-enc':
            assert 1<=int(new['Confiscate Score'])<=5
        elif name=='a16_prison-letters-enc':
            assert new['Audience'] in {'All','Lover'}
            for f in ['Min Relationship Strength','Max Relationship Strength']:
                assert not new[f] or 0<=int(new[f])<=100
            if new['Min Relationship Strength'] and new['Max Relationship Strength']:
                assert int(new['Min Relationship Strength'])<=int(new['Max Relationship Strength'])
        elif name=='a16_prison-nicknames-enc':assert new['Gender']=='both'
        for f in ['Royal','Randomize Choices','Is Prefix','Is Plural','From Lover Only','Use Some Article','Will Do','Will Let','Hero Action','Bully Action']:
            if f in new:assert new[f] in {'','x'},f
    keyfields={'a16_dumb-scenarios-prison-enc':'Index','a16_prison-jobs-enc':'Job',
        'a16_prison-gifts-enc':'Name','a16_prison-nicknames-enc':'Nickname',
        'a16_prison-parole-questions-enc':'Question','a16_prison-letters-enc':'Topic',
        'a16_prison-bully-inbound-scenarios-enc':'Scenario','a16_prison-bully-outbound-scenarios-enc':'Scenario'}
    key=keyfields[name];idx=header.index(key);old={r[idx].casefold() for r in original[1:]}
    keys=[r[key].casefold() for r in additions]
    assert len(keys)==len(set(keys)) and not old.intersection(keys),'Duplicate identity in '+name

def build(apk,content_path,out,aapt2=None):
    root=Path(__file__).resolve().parent;apk=Path(apk).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    assert sha_file(apk)==BASELINE_SHA256,'Unsupported or incomplete input APK'
    content=json.loads(Path(content_path).read_text())
    assert {k:len(v) for k,v in content.items()}==EXPECTED_COUNTS
    with zipfile.ZipFile(apk) as src:env=UnityPy.load(src.read(BUNDLE))
    before={};modified=set();originals={};expected={};counts={};existing_global_ids=set()
    for obj in env.objects:
        before[obj.path_id]=sha(obj.get_raw_data())
        if obj.type.name!='TextAsset':continue
        asset=obj.read();name=asset.m_Name
        if name not in content:
            # Indexes can also be referenced by event history. Check other
            # indexed encrypted CSV pools before assigning the new IDs.
            if name.endswith('-enc'):
                try:
                    rows=records(decode(asset.m_Script))
                    if 'Index' in rows[0]:
                        i=rows[0].index('Index');existing_global_ids.update(r[i] for r in rows[1:] if r[i])
                except (ValueError,UnicodeError,AssertionError):pass
            continue
        assert name not in originals,'Duplicate target TextAsset'
        text=decode(asset.m_Script);assert encode(text)==asset.m_Script,'Encryption round trip failed'
        rows=records(text);validate(name,rows,content[name]);originals[name]=rows
        if 'Index' in rows[0]:
            i=rows[0].index('Index');existing_global_ids.update(r[i] for r in rows[1:] if r[i])
        tail=[[r.get(f,'') for f in rows[0]] for r in content[name]]
        expected[name]=rows+tail
        stream=io.StringIO(newline='');csv.writer(stream,lineterminator='\r\n').writerows(expected[name])
        asset.m_Script=encode(stream.getvalue());asset.save();modified.add(obj.path_id)
        counts[name]={'original':len(rows)-1,'added':len(tail),'total':len(rows)+len(tail)-1}
    assert set(originals)==set(content),'Missing target pool'
    new_ids={row['Index'] for row in content['a16_dumb-scenarios-prison-enc']}
    assert not new_ids.intersection(existing_global_ids),'Scenario ID collision with an existing pool'
    rebuilt_bytes=next(iter(env.files.values())).save(packer='original')
    rebuilt=UnityPy.load(rebuilt_bytes);inventory=set();verified=set()
    for obj in rebuilt.objects:
        inventory.add(obj.path_id)
        if obj.path_id in modified:
            asset=obj.read();assert records(decode(asset.m_Script))==expected[asset.m_Name]
            verified.add(asset.m_Name)
        else:assert sha(obj.get_raw_data())==before[obj.path_id],'Unrelated Unity object changed'
    assert inventory==set(before) and verified==set(content)
    # Explicitly check the music suffixes in the finished bundle too.
    music=json.loads((root/'music_content.json').read_text());music_checked=set()
    for obj in rebuilt.objects:
        if obj.type.name!='TextAsset':continue
        asset=obj.read()
        if asset.m_Name not in music:continue
        rows=records(decode(asset.m_Script));h=rows[0]
        added=[[r.get(f,'') for f in h] for r in music[asset.m_Name]]
        assert rows[-len(added):]==added;music_checked.add(asset.m_Name)
    assert music_checked==set(music)
    unsigned=out/'prison-expansion-unsigned.apk'
    with zipfile.ZipFile(apk) as src,zipfile.ZipFile(unsigned,'w',allowZip64=False) as dst:
        for entry in src.infolist():
            if signature_entry(entry.filename):continue
            info=copy.copy(entry);info.extra=b''
            if info.compress_type==zipfile.ZIP_STORED:
                alignment=16384 if info.filename.endswith('.so') else 4
                offset=dst.fp.tell()+30+len(info.filename.encode('utf8'))
                if offset%alignment:
                    pad=(-offset-4)%alignment;info.extra=struct.pack('<HH',0xd935,pad)+b'\0'*pad
            dst.writestr(info,rebuilt_bytes if info.filename==BUNDLE else src.read(info.filename),compresslevel=6)
        dst.comment=src.comment
    jar=root/'tools/apksig-8.7.3.jar'
    assert sha_file(jar)=='c070ed1394629d74641aa0906f60b2ffa1ee77e6366a1f93437f59717b1aeb89'
    target=out/'BitLife_Prison_Expansion_INSTALL_FIX.apk'
    subprocess.run(['java','--class-path',str(jar),str(root/'SignApk.java'),str(unsigned),str(target),str(root/'signing/music-test-key.pem'),str(root/'signing/music-test-cert.der')],check=True)
    checks={}
    for program in ['VerifyApk.java','VerifyNativeSigner.java']:
        result=subprocess.run(['java','--class-path',str(jar),str(root/program),str(target)],check=True,capture_output=True,text=True).stdout
        assert 'verified=true' in result;checks[program]=result.strip()
    changed=[]
    with zipfile.ZipFile(apk) as old,zipfile.ZipFile(target) as new,target.open('rb') as raw:
        assert new.testzip() is None and len(new.namelist())==len(set(new.namelist()))
        assert {n for n in old.namelist() if not signature_entry(n)}=={n for n in new.namelist() if not signature_entry(n)}
        for entry in new.infolist():
            name=entry.filename
            if not signature_entry(name) and old.read(name)!=new.read(name):changed.append(name)
            if entry.compress_type==zipfile.ZIP_STORED:
                raw.seek(entry.header_offset+26);fn,extra=struct.unpack('<HH',raw.read(4))
                assert (entry.header_offset+30+fn+extra)%(16384 if name.endswith('.so') else 4)==0,name
        assert changed==[BUNDLE],changed
        assert new.read(BUNDLE)==rebuilt_bytes
    with target.open('rb') as raw:
        raw.seek(-22,2);eocd=raw.read(22)
    end=struct.unpack('<4s4H2IH',eocd)
    assert end[0]==b'PK\x05\x06' and end[-1]==0,'Missing final ZIP end record'
    assert end[5]+end[6]+22==target.stat().st_size,'Central directory does not end at EOF'
    if aapt2 is None:aapt2=root.parent/'tools/aapt2'
    aapt2=Path(aapt2).resolve()
    badging=subprocess.run([str(aapt2),'dump','badging',str(target)],check=True,capture_output=True,text=True).stdout
    assert "package: name='com.candywriter.bitlife'" in badging
    assert "application: label='BitLife'" in badging
    (root/'prison_install_aapt2_badging.txt').write_text(badging)
    report={'build':'250-entry Prison+ content expansion over the user-confirmed startup repair',
        'input_sha256':BASELINE_SHA256,'output_sha256':sha_file(target),'output_bytes':target.stat().st_size,
        'prison_entries_added':sum(c['added'] for c in counts.values()),'tables':counts,
        'four_choice_prison_events':80,'new_event_response_options':320,'new_parole_questions':25,'new_parole_response_options':450,
        'new_prison_event_ids':sorted(new_ids,key=int),'new_ids_do_not_collide_with_existing_indexed_pools':True,
        'original_prison_rows_preserved':True,'music_entries_preserved':196,
        'unchanged_unrelated_unity_objects':len(before)-len(modified),'changed_apk_entries':changed,
        'dex_manifest_native_libraries_and_startup_fix_byte_identical_to_working_baseline':True,
        'same_package_and_personal_signing_identity':True,'apk_crc_and_stored_alignment':'passed','signature_checks':checks,
        'android_aapt2_badging':'passed; package, manifest, resource table and application identity readable',
        'zip_end_record':'present at EOF; central-directory bounds checked',
        'baseline_startup_phone_test':'User reported working on 2026-10-03',
        'prison_expansion_phone_runtime_tested':False,'new_content_selection_on_phone':'Not yet confirmed',
        'display':'Existing prison UI; new authored prison event titles begin Prison+: ',
        'eligibility':'New four-choice prison events are adult (18+) entries; existing selection rules remain intact',
        'limitations':'Adds content using existing pools. No new prison map, escape minigame, gang-war engine, or forced event selection.',
        'previous_delivery_failure':'The 250-entry APK saved in the previous turn is missing its ZIP end record and cannot be parsed. How this occurred after the previously reported checks is not established. This replacement is rebuilt from the valid working baseline.'}
    (root/'prison_expansion_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    unsigned.unlink();print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('apk');p.add_argument('--content',default=str(Path(__file__).with_name('prison_content.json')));p.add_argument('--out',default='output-prison');p.add_argument('--aapt2')
    a=p.parse_args();build(a.apk,a.content,a.out,a.aapt2)
