"""Patch only nine existing music TextAssets; preserve all original content."""
import argparse
import base64
import collections
import copy
import csv
import hashlib
import io
import json
import re
import struct
import subprocess
import zipfile
from pathlib import Path
import UnityPy
from sign_apk import verify

BUNDLE='assets/bin/Data/datapack.unity3d'
KEY=b'yst.odkzffq.zfshhs16'
INPUT_SHA='60abca22a2a7e081264d6e14fd3b8a96e650294b587fdcd58e55a6b13b174df7'

def decode(text):
    cipher=base64.b64decode(text,validate=True).decode('utf8')
    return ''.join(chr(ord(c)^KEY[i%len(KEY)]) for i,c in enumerate(cipher))

def encode(text):
    # Existing assets encrypt Unicode characters, then UTF-8 encode the result.
    cipher=''.join(chr(ord(c)^KEY[i%len(KEY)]) for i,c in enumerate(text))
    return base64.b64encode(cipher.encode('utf8')).decode('ascii')

def records(text):
    rows=list(csv.reader(io.StringIO(text,newline='')))
    assert rows and len(set(rows[0]))==len(rows[0])
    assert all(len(r)==len(rows[0]) for r in rows[1:]), 'Unequal CSV field counts'
    return rows

def signature_entry(name):
    return name.upper()=='META-INF/MANIFEST.MF' or bool(re.fullmatch(r'META-INF/[^/]+\.(SF|RSA|DSA|EC)',name,re.I))

def run(apk,out,content_path):
    apk=Path(apk);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    assert hashlib.file_digest(apk.open('rb'),'sha256').hexdigest()==INPUT_SHA, 'Unsupported input APK'
    content=json.loads(Path(content_path).read_text())
    with zipfile.ZipFile(apk) as z: original_bundle=z.read(BUNDLE)
    env=UnityPy.load(original_bundle)
    originals={};raw_hashes={};counts={};modified_ids=set();assets={}
    for obj in env.objects:
        raw_hashes[obj.path_id]=hashlib.sha256(obj.get_raw_data()).hexdigest()
        if obj.type.name!='TextAsset':continue
        asset=obj.read()
        if asset.m_Name not in content:continue
        assert asset.m_Name not in assets, 'Ambiguous asset name'
        name=asset.m_Name;assets[name]=obj.path_id
        decoded=decode(asset.m_Script)
        assert encode(decoded)==asset.m_Script, 'Original encryption round trip failed'
        rows=records(decoded);header=rows[0];additions=content[name]
        originals[name]=rows
        existing_tokens=set(re.findall(r'<[^<>]+>',decoded))
        existing_ids={r[header.index('Index')] for r in rows[1:]} if 'Index' in header else set()
        seen=set()
        for new in additions:
            assert set(new)<=set(header), f'Unknown fields in {name}'
            assert set(re.findall(r'<[^<>]+>',str(new)))<=existing_tokens, f'Unsupported template token in {name}'
            if 'Index' in header and new.get('Index'):
                assert new['Index'] not in existing_ids|seen, 'Duplicate scenario index'
                seen.add(new['Index'])
            for field,value in new.items():
                if 'Impact' in field:
                    assert -4<=int(value)<=4
            if 'CTA' in header:
                for i in range(1,5):
                    assert new.get(f'Choice {i}') and new.get(f'Narrative {i}')
            if 'Solo' in header:assert new['Solo']==new['Band']=='x'
        stream=io.StringIO(newline='');writer=csv.writer(stream,lineterminator='\r\n')
        writer.writerows(rows)
        writer.writerows([[new.get(field,'') for field in header] for new in additions])
        result=stream.getvalue();assert records(result)[:len(rows)]==rows
        asset.m_Script=encode(result);assert decode(asset.m_Script)==result
        asset.save();modified_ids.add(obj.path_id)
        counts[name]={'original':len(rows)-1,'added':len(additions),'total':len(rows)-1+len(additions)}
    assert set(assets)==set(content), 'Missing target assets'
    bundle=next(iter(env.files.values())).save(packer='original')
    rebuilt=UnityPy.load(bundle)
    checked_ids=set()
    for obj in rebuilt.objects:
        checked_ids.add(obj.path_id)
        if obj.path_id not in modified_ids:
            assert hashlib.sha256(obj.get_raw_data()).hexdigest()==raw_hashes[obj.path_id], 'Unrelated object changed'
        else:
            asset=obj.read();name=asset.m_Name;rs=records(decode(asset.m_Script))
            orig=originals[name];assert rs[:len(orig)]==orig
            assert rs[len(orig):]==[[new.get(f,'') for f in orig[0]] for new in content[name]]
    assert checked_ids==set(raw_hashes), 'Bundle object inventory changed'
    (out/'expanded-datapack.unity3d').write_bytes(bundle)
    unsigned=out/'music-expansion-unsigned.apk'
    with zipfile.ZipFile(apk) as src,zipfile.ZipFile(unsigned,'w',allowZip64=False) as dst:
        for original in src.infolist():
            if signature_entry(original.filename):continue
            info=copy.copy(original);info.extra=b''
            if info.compress_type==zipfile.ZIP_STORED:
                offset=dst.fp.tell()+30+len(info.filename.encode('utf8'))
                alignment=16384 if info.filename.endswith('.so') else 4
                if offset%alignment:
                    pad=(-offset-4)%alignment;info.extra=struct.pack('<HH',0xd935,pad)+b'\x00'*pad
            dst.writestr(info,bundle if info.filename==BUNDLE else src.read(original.filename),compresslevel=6)
        dst.comment=src.comment
    target=out/'BitLife_Music_Expansion_SIGNING_FIX.apk'
    jar=Path(__file__).parent/'tools/apksig-8.7.3.jar'
    assert hashlib.file_digest(jar.open('rb'),'sha256').hexdigest()=='c070ed1394629d74641aa0906f60b2ffa1ee77e6366a1f93437f59717b1aeb89'
    from sign_apk import identity
    identity(out/'signing')
    subprocess.run(['java','--class-path',str(jar),str(Path(__file__).with_name('SignApk.java')),
      str(unsigned),str(target),str(out/'signing/music-test-key.pem'),str(out/'signing/music-test-cert.der')],check=True)
    official=subprocess.run(['java','--class-path',str(jar),str(Path(__file__).with_name('VerifyApk.java')),str(target)],
      check=True,capture_output=True,text=True).stdout
    assert 'verified=true' in official and 'v2=true' in official and 'v3=true' in official
    sigcheck=verify(target)
    with zipfile.ZipFile(apk) as old,zipfile.ZipFile(target) as new:
        assert new.testzip() is None
        assert len(new.namelist())==len(set(new.namelist()))
        assert {n for n in new.namelist() if not signature_entry(n)}=={n for n in old.namelist() if not signature_entry(n)}
        changed=[]
        for info in new.infolist():
            n=info.filename
            if signature_entry(n):continue
            if old.read(n)!=new.read(n):changed.append(n)
            if info.compress_type==zipfile.ZIP_STORED:
                with target.open('rb') as f:
                    f.seek(info.header_offset+26);fn,ex=struct.unpack('<HH',f.read(4))
                offset=info.header_offset+30+fn+ex
                assert offset%(16384 if n.endswith('.so') else 4)==0
        assert changed==[BUNDLE], 'Unexpected APK entry changes'
    report={'input_sha256':INPUT_SHA,'output_sha256':hashlib.file_digest(target.open('rb'),'sha256').hexdigest(),
      'output_bytes':target.stat().st_size,'added_content_entries':sum(x['added'] for x in counts.values()),
      'tables':counts,'changed_zip_entries':changed,'unchanged_bundle_objects_verified':len(raw_hashes)-len(modified_ids),
      'apk_zip_crc_passed':True,'stored_entry_alignment_passed':True,'signature':sigcheck,
      'google_apksig_verification':official,'signing_schemes_generated':['v1','v2','v3'],
      'android_phone_tested':False,'application_integrity_checks_unchanged':True,
      'compatibility':'Package, SDK requirements, DEX and native libraries unchanged. New test certificate cannot update original app.'}
    (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('apk');p.add_argument('--out',default='output')
    p.add_argument('--content',default=str(Path(__file__).with_name('music_content.json')))
    a=p.parse_args();run(a.apk,a.out,a.content)
