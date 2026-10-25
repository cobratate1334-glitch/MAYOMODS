"""Append 600 validated Life+ rows to the verified firearm/prison/music build."""
import argparse,copy,csv,io,json,os,re,struct,subprocess,zipfile
from pathlib import Path
import UnityPy
from build_prison_expansion import decode,encode,records,sha,sha_file,signature_entry

BASELINE='8c68bde6d5f956e025d150c4240fc9189f8e5b0579994eb2f579ba844da08b0d'
BUNDLE='assets/bin/Data/datapack.unity3d'
KEYS={'a16_dumb-scenarios-universal-enc':'Index','a16_careers-enc':'Career',
 'a16_part-time-jobs-enc':'Job','a16_school-activities-enc':'Index',
 'a16_backtoschool-field-trip-location-enc':'Location','a16_backtoschool-school-dance-theme-enc':'Theme'}

def validate(name,old,new):
    h=old[0];tokens=set(re.findall(r'<[^<>]+>',str(old)))
    before=set(map(tuple,old[1:]));seen=set()
    for row in new:
        assert set(row)==set(h),(name,'Field schema mismatch')
        assert all(isinstance(v,str) for v in row.values())
        assert set(re.findall(r'<[^<>]+>',str(row)))<=tokens,(name,'Unknown template token')
        t=tuple(row[f] for f in h);assert t not in before|seen,(name,'Duplicate row');seen.add(t)
        for f,v in row.items():
            assert '\x00' not in v and '\r' not in v and '\n' not in v
            if 'Impact' in f and v:assert -3<=int(v)<=3
            if (f.startswith('Min ') or f.startswith('Max ')) and f.split()[-1] in ['Health','Smarts','Athleticism','Looks','Popularity','Grades','Intelligence','Appearance','Happiness','Karma'] and v:
                assert 0<=int(v)<=100
        for f in ['Type','Company Type','Required Education','Success Defining Attribute','Focus','Theme']:
            if f in h and row[f] and name!='a16_backtoschool-school-dance-theme-enc':
                assert row[f] in {r[h.index(f)] for r in old[1:]},(name,f,row[f])
        if name=='a16_dumb-scenarios-universal-enc':
            assert row['Title'].startswith('Life+: ')
            assert 11<=int(row['Hero Min Age'])<=18
            if row['Student']=='x':assert row['Hero Max Age']=='25'
            if row['Job']=='x':assert row['Hero Min Age']=='18'
            for i in range(1,5):assert row[f'Choice {i}'] and row[f'Narrative {i}']
            assert len({row[f'Choice {i}'] for i in range(1,5)})==4
            assert len({tuple(row[f'{f} Impact {i}'] for f in ['Karma','Discipline','Happiness','Intelligence','Appearance']) for i in range(1,5)})>=2
        if name=='a16_careers-enc':
            assert row['Required Major'] in {r[h.index('Required Major')] for r in old[1:]}
            assert len(row['Seniority Track'].split(', '))==3
            for f in ['Starting Salary','Salary Cap']:assert re.fullmatch(r'\$[\d,]+\.\d\d',row[f])
        if name=='a16_part-time-jobs-enc':
            assert int(row['Min Age'])>=16
            assert 0<int(row['Min Weekly Hours'])<=int(row['Max Weekly Hours'])<=30
            for f in ['Min Hourly Rate','Max Hourly Rate']:assert re.fullmatch(r'\$\d+ ?',row[f])
        if name=='a16_school-activities-enc':
            assert row['Specific Countries']=='All' and row['Gender']=='both'
            assert row['Requires Tryouts']=='' and row['Track Performance']==''
    if name in KEYS:
        f=KEYS[name];original={r[h.index(f)].casefold() for r in old[1:]};ids=[r[f].casefold() for r in new]
        assert len(ids)==len(set(ids)) and not original.intersection(ids)

def build(apk,out,aapt2):
    root=Path(__file__).resolve().parent;apk=Path(apk).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    assert sha_file(apk)==BASELINE,'Unsupported baseline'
    content=json.loads((root/'life_content.json').read_text());assert sum(map(len,content.values()))==600
    with zipfile.ZipFile(apk) as z:env=UnityPy.load(z.read(BUNDLE))
    before={o.path_id:sha(o.get_raw_data()) for o in env.objects};modified=set();expected={};counts={};old_ids=set()
    for o in env.objects:
        if o.type.name!='TextAsset':continue
        a=o.read();name=a.m_Name
        if not name.endswith('-enc'):continue
        try:old=records(decode(a.m_Script))
        except (ValueError,UnicodeError,AssertionError):continue
        if 'Index' in old[0]:old_ids.update(r[old[0].index('Index')] for r in old[1:])
        if name not in content:continue
        assert name not in expected;assert encode(decode(a.m_Script))==a.m_Script
        new=content[name];validate(name,old,new)
        expected[name]=old+[[r[f] for f in old[0]] for r in new]
        s=io.StringIO(newline='');csv.writer(s,lineterminator='\r\n').writerows(expected[name])
        a.m_Script=encode(s.getvalue());a.save();modified.add(o.path_id)
        counts[name]={'original':len(old)-1,'added':len(new),'total':len(expected[name])-1}
    assert set(expected)==set(content)
    ids=[r['Index'] for rs in content.values() for r in rs if 'Index'in r]
    assert len(ids)==len(set(ids)) and not old_ids.intersection(ids),'Global Index collision'
    payload=next(iter(env.files.values())).save(packer='original');rebuilt=UnityPy.load(payload)
    assert {o.path_id for o in rebuilt.objects}==set(before)
    for o in rebuilt.objects:
        if o.path_id in modified:
            a=o.read();assert records(decode(a.m_Script))==expected[a.m_Name]
        else:assert sha(o.get_raw_data())==before[o.path_id],'Unrelated Unity object modified'
    # Preserve all previous content expansions, including the 18 firearm rows.
    retained={}
    for filename in ['music_content.json','prison_content.json','firearms_content.json']:
        c=json.loads((root/filename).read_text())
        for o in rebuilt.objects:
            if o.type.name!='TextAsset':continue
            a=o.read()
            if a.m_Name in c:
                old=records(decode(a.m_Script));tail=[[r.get(f,'') for f in old[0]] for r in c[a.m_Name]]
                assert old[-len(tail):]==tail;retained[a.m_Name]=len(tail)
        assert set(c)<=set(retained)
    assert sum(retained.values())==464
    unsigned=out/'life-unsigned.apk'
    with zipfile.ZipFile(apk) as src,zipfile.ZipFile(unsigned,'w',allowZip64=False) as dst:
        for entry in src.infolist():
            if signature_entry(entry.filename):continue
            info=copy.copy(entry);info.extra=b''
            if info.compress_type==zipfile.ZIP_STORED:
                alignment=16384 if info.filename.endswith('.so') else 4
                offset=dst.fp.tell()+30+len(info.filename.encode('utf8'))
                if offset%alignment:
                    pad=(-offset-4)%alignment;info.extra=struct.pack('<HH',0xd935,pad)+b'\0'*pad
            dst.writestr(info,payload if info.filename==BUNDLE else src.read(info.filename),compresslevel=6)
        dst.comment=src.comment
    jar=root/'tools/apksig-8.7.3.jar'
    assert sha_file(jar)=='c070ed1394629d74641aa0906f60b2ffa1ee77e6366a1f93437f59717b1aeb89'
    stage=out/'life-signed-staging.tmp'
    subprocess.run(['java','--class-path',str(jar),str(root/'SignApk.java'),str(unsigned),str(stage),str(root/'signing/music-test-key.pem'),str(root/'signing/music-test-cert.der')],check=True)
    checks={}
    for program in ['VerifyApk.java','VerifyNativeSigner.java']:
        r=subprocess.run(['java','--class-path',str(jar),str(root/program),str(stage)],capture_output=True,text=True,check=True)
        assert 'verified=true' in r.stdout;checks[program]=r.stdout.strip()
    changed=[]
    with zipfile.ZipFile(apk) as old,zipfile.ZipFile(stage) as new,stage.open('rb') as raw:
        assert new.testzip() is None and len(new.namelist())==len(set(new.namelist()))
        assert {n for n in old.namelist() if not signature_entry(n)}=={n for n in new.namelist() if not signature_entry(n)}
        for e in new.infolist():
            if not signature_entry(e.filename) and old.read(e.filename)!=new.read(e.filename):changed.append(e.filename)
            if e.compress_type==zipfile.ZIP_STORED:
                raw.seek(e.header_offset+26);fn,ex=struct.unpack('<HH',raw.read(4));assert (e.header_offset+30+fn+ex)%(16384 if e.filename.endswith('.so') else 4)==0
        assert changed==[BUNDLE]
        assert new.read(BUNDLE)==payload
    with stage.open('rb') as f:f.seek(-22,2);eocd=struct.unpack('<4s4H2IH',f.read(22))
    assert eocd[0]==b'PK\x05\x06' and eocd[-1]==0 and eocd[5]+eocd[6]+22==stage.stat().st_size
    badging=subprocess.run([str(Path(aapt2).resolve()),'dump','badging',str(stage)],capture_output=True,text=True,check=True).stdout
    assert "package: name='com.candywriter.bitlife'" in badging
    (root/'life_aapt2_badging.txt').write_text(badging)
    with stage.open('r+b') as f:f.flush();os.fsync(f.fileno())
    final=out/'BitLife_Life_School_Careers_Expansion.apk';stage.replace(final)
    with final.open('rb') as f:f.seek(-22,2);assert struct.unpack('<4s4H2IH',f.read(22))==eocd
    report={'input_sha256':BASELINE,'output_sha256':sha_file(final),'output_bytes':final.stat().st_size,
      'new_entries':600,'new_age_up_events':120,'new_choice_outcomes':480,'new_careers':40,
      'new_career_promotion_titles':120,'new_part_time_jobs':40,'new_school_clubs':30,
      'pool_counts':counts,'previous_content_preserved':retained,'unchanged_unity_objects':len(before)-len(modified),
      'changed_apk_entries':changed,'signature_checks':checks,'zip_crc_alignment_android_parse':'passed',
      'dex_native_manifest_startup_fix_and_firearm_resource_aliases_preserved':True,
      'phone_runtime_tested':False,'arms_dealer_buy_fix':'Unresolved; Buy-tap log required. No speculative native patch.',
      'limits':'Existing selection and access rules apply. Events are not forced every year. No new examination engine, menu, persistent buzz stat, or guaranteed promotion. New careers and clubs use existing generic icon fallbacks.'}
    (root/'life_expansion_verification.json').write_text(json.dumps(report,indent=2)+'\n');unsigned.unlink()
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('apk');p.add_argument('--out',default='output-life');p.add_argument('--aapt2',default=str(Path(__file__).resolve().parent.parent/'tools/aapt2'));a=p.parse_args();build(a.apk,a.out,a.aapt2)
