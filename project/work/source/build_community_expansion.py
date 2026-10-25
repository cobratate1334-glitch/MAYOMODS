"""Repair authored table terminators, supply a prison icon fallback and append Community+.

Exact baseline, preserved cells/objects, native physical-line regression checks,
real ARM64 guard emulation, complete staged APK and existing signer validation.
"""
import argparse,copy,csv,io,json,os,re,struct,subprocess,sys,zipfile
from pathlib import Path
import UnityPy
from elftools.elf.elffile import ELFFile
from build_prison_expansion import decode,encode,records,sha,sha_file,signature_entry
from build_dealer_fix import assemble

ROOT=Path(__file__).resolve().parent
BASELINE='70c185e1523eff0169655818b8ef4bd65b163f26c64e47f41494933db7438afe'
BUNDLE='assets/bin/Data/datapack.unity3d';LIB='lib/arm64-v8a/libil2cpp.so';ICON_SITE=0x2b899dc
sys.path.insert(0,str(ROOT/'tests'))
from community_loader_test import check_table,check_icon_patch
from dealer_guard_test import validate as validate_guard

def validate_content(name,old,new):
    header=old[0];tokens=set(re.findall(r'<[^<>]+>',str(old)))
    seen=set(map(tuple,old[1:]));keys=[]
    for row in new:
        assert set(row)==set(header),name
        assert all(isinstance(v,str) and not any(c in v for c in '\r\n\x00') for v in row.values()),name
        assert set(re.findall(r'<[^<>]+>',str(row)))<=tokens,(name,'unknown template token')
        ordered=tuple(row[h] for h in header);assert ordered not in seen,(name,'duplicate');seen.add(ordered)
        for f,v in row.items():
            if (' Impact ' in f or ' Impact Score' in f) and v:assert -3<=int(v)<=3,(name,f,v)
            if f in ('Commonness Score','Commonness','Appeal Score','Viral Score') and v:assert 1<=int(v)<=5
        for f in ('Company Type','Required Education','Required Major','Success Defining Attribute','Type','Theme','Project Type'):
            if f in header and row[f] and 'dance-theme' not in name and 'dumb-scenarios-career' not in name:
                assert row[f] in {r[header.index(f)] for r in old[1:]},(name,f,row[f])
        if 'Genre'in row and row['Genre']:
            known={p.strip() for r in old[1:] for p in r[header.index('Genre')].split(',') if p.strip()}
            assert set(p.strip() for p in row['Genre'].split(','))<=known
        if 'Choice 1'in header:
            choices=[row[f'Choice {i}'] for i in range(1,5)]
            assert all(choices) and len(set(choices))==4
            assert all(row[f'Narrative {i}'] for i in range(1,5))
        primary=next((f for f in ('Index','Career','Activity','Post Type','Feature','Beat','Vibe','Instrument','Sound','Name','Product') if f in header),None)
        if primary:keys.append((primary,row[primary]))
    if keys:
        assert len(set(keys))==len(keys)
        primary=keys[0][0];assert not {v.casefold() for _,v in keys}&{r[header.index(primary)].casefold() for r in old[1:]}

def patch_icon(original,metadata):
    elf=ELFFile(io.BytesIO(original));loads=[s for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
    def off(va):
        s=next(s for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']);return s['p_offset']+va-s['p_vaddr']
    assert original[off(ICON_SITE):off(ICON_SITE)+4]==assemble('csel x0,x8,x21,ne',ICON_SITE)
    # Metadata v39 stores literal offsets followed by packed UTF-8 literal data.
    assert struct.unpack_from('<II',metadata)==(0xfab11baf,39)
    literal_offset,_,_,literal_data=struct.unpack_from('<4I',metadata,8)
    rel={r['r_offset']:r['r_addend'] for r in elf.get_section_by_name('.rela.dyn').iter_relocations()}
    ptr=rel[0x5c611b8];encoded=struct.unpack_from('<Q',original,off(ptr))[0]
    assert encoded>>29==5
    index=(encoded&0x1fffffff)>>1
    start,end=struct.unpack_from('<II',metadata,literal_offset+index*4)
    literal=metadata[literal_data+start:literal_data+end].decode('utf8')
    assert literal=='factory',literal
    # The existing function initializes this slot, returns it for warehouse work,
    # and currently returns empty text for an unrecognized custom prison job.
    assert original[off(0x2b899d4):off(0x2b899d4)+4]==assemble('ldr x8,[x8,#0x1b8]',0x2b899d4)
    modified=bytearray(original);position=off(ICON_SITE)
    modified[position:position+4]=assemble('mov x0,x8',ICON_SITE)
    assert original[:position]==modified[:position] and original[position+4:]==modified[position+4:]
    return bytes(modified),{'site_va':hex(ICON_SITE),'file_offset':position,'changed_instruction_bytes':4,'fallback':literal}

def build(apk,out,aapt2):
    apk=Path(apk).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    assert sha_file(apk)==BASELINE,'Unsupported input APK'
    content=json.loads((ROOT/'community_content.json').read_text());assert sum(map(len,content.values()))==644
    previous={}
    for filename in ('music_content.json','prison_content.json','firearms_content.json','life_content.json'):
        for name,rows in json.loads((ROOT/filename).read_text()).items():previous.setdefault(name,[]).extend(rows)
    with zipfile.ZipFile(apk) as z:
        env=UnityPy.load(z.read(BUNDLE));original_lib=z.read(LIB)
        metadata=z.read('assets/bin/Data/Managed/Metadata/global-metadata.dat')
    before={o.path_id:sha(o.get_raw_data()) for o in env.objects}
    selected=set(content)|set(previous);modified=set();expected={};counts={};loader_checks={};old_ids=set();old_tables={}
    for o in env.objects:
        if o.type.name!='TextAsset':continue
        a=o.read()
        if not a.m_Name.endswith('-enc'):continue
        try:old=records(decode(a.m_Script))
        except (UnicodeError,AssertionError,ValueError):continue
        old_tables[a.m_Name]=old
        if 'Index' in old[0]:old_ids.update(r[old[0].index('Index')] for r in old[1:])
        if a.m_Name not in selected:continue
        name=a.m_Name;assert name not in expected
        text=decode(a.m_Script);assert encode(text)==a.m_Script
        additions=content.get(name,[]);validate_content(name,old,additions)
        # Previous expansions must survive as exact field values, including duplicates
        # that existed before this patch. No reset of valid save/game content.
        for row in previous.get(name,[]):assert [row.get(f,'') for f in old[0]] in old[1:],(name,'previous row missing')
        expected[name]=old+[[r[f] for f in old[0]] for r in additions]
        stream=io.StringIO(newline='');csv.writer(stream,lineterminator='\n').writerows(expected[name])
        result=stream.getvalue().removesuffix('\n')
        loader_checks[name]=check_table(text,result,expected[name])
        a.m_Script=encode(result);a.save();modified.add(o.path_id)
        counts[name]={'original':len(old)-1,'added':len(additions),'total':len(expected[name])-1}
    assert set(expected)==selected,(selected-set(expected))
    ids=[r['Index'] for rs in content.values() for r in rs if 'Index'in r]
    assert len(ids)==len(set(ids)) and not set(ids)&old_ids
    allcareers={r[0] for r in expected['a16_careers-enc'][1:]}
    jobscenarios=content['a16_dumb-scenarios-career-enc'];assert all(r['Type'] in allcareers for r in jobscenarios)
    custom=json.loads((ROOT/'life_content.json').read_text())['a16_careers-enc']+content['a16_careers-enc']
    assert all(sum(r['Type']==c['Career'] for r in jobscenarios)==4 for c in custom)
    weapon=expected['a16_black-market-weapons-enc'];h=weapon[0];wp=[dict(zip(h,r)) for r in weapon[1:]]
    assert len(wp)==60 and [int(r['ID']) for r in wp]==list(range(600,660))
    pools={}
    for fake in (False,True):
        for rare in (False,True):
            pool=[r for r in wp if (not fake or r['Can Be Fake']=='x') and (not rare or int(r['Commonness Score'])<=2)]
            assert pool;pools[f'fake={fake},rare={rare}']={'records':len(pool),'weight':sum(int(r['Commonness Score']) for r in pool)}
    payload=next(iter(env.files.values())).save(packer='original');rebuilt=UnityPy.load(payload)
    assert {o.path_id for o in rebuilt.objects}==set(before)
    for o in rebuilt.objects:
        if o.path_id in modified:
            a=o.read();assert records(decode(a.m_Script))==expected[a.m_Name]
            check_table(decode(a.m_Script),decode(a.m_Script),expected[a.m_Name])
        else:assert sha(o.get_raw_data())==before[o.path_id]
    replacement,icon_details=patch_icon(original_lib,metadata)
    icon_tests=check_icon_patch(replacement)
    guard_tests=validate_guard(replacement,json.loads((ROOT/'dealer_fix_details.json').read_text()))
    unsigned=out/'community-unsigned.tmp';stage=out/'community-signed.tmp'
    with zipfile.ZipFile(apk) as src,zipfile.ZipFile(unsigned,'w',allowZip64=False) as dst:
        for entry in src.infolist():
            if signature_entry(entry.filename):continue
            info=copy.copy(entry);info.extra=b''
            if info.compress_type==zipfile.ZIP_STORED:
                boundary=16384 if info.filename.endswith('.so') else 4
                position=dst.fp.tell()+30+len(info.filename.encode('utf8'))
                if position%boundary:
                    pad=(-position-4)%boundary;info.extra=struct.pack('<HH',0xd935,pad)+b'\0'*pad
            data=payload if entry.filename==BUNDLE else replacement if entry.filename==LIB else src.read(entry.filename)
            dst.writestr(info,data,compresslevel=6)
        dst.comment=src.comment
    with unsigned.open('r+b') as f:f.flush();os.fsync(f.fileno())
    with zipfile.ZipFile(unsigned) as z:assert z.testzip() is None
    jar=ROOT/'tools/apksig-8.7.3.jar'
    assert sha_file(jar)=='c070ed1394629d74641aa0906f60b2ffa1ee77e6366a1f93437f59717b1aeb89'
    subprocess.run(['java','-cp',str(jar),str(ROOT/'SignApk.java'),str(unsigned),str(stage),str(ROOT/'signing/music-test-key.pem'),str(ROOT/'signing/music-test-cert.der')],check=True,capture_output=True)
    checks={}
    for program in ('VerifyApk.java','VerifyNativeSigner.java'):
        checks[program]=subprocess.run(['java','-cp',str(jar),str(ROOT/program),str(stage)],capture_output=True,text=True,check=True).stdout.strip()
        assert 'verified=true'in checks[program]
    assert all(x in checks['VerifyApk.java'] for x in ('v2=true','v3=true','errors=[]','warnings=[]'))
    changed=[]
    with zipfile.ZipFile(apk) as old,zipfile.ZipFile(stage) as new,stage.open('rb') as f:
        assert new.testzip() is None and len(new.namelist())==len(set(new.namelist()))
        assert {n for n in old.namelist() if not signature_entry(n)}=={n for n in new.namelist() if not signature_entry(n)}
        for entry in new.infolist():
            if not signature_entry(entry.filename) and old.read(entry.filename)!=new.read(entry.filename):changed.append(entry.filename)
            if entry.compress_type==zipfile.ZIP_STORED:
                f.seek(entry.header_offset+26);nm,ex=struct.unpack('<HH',f.read(4))
                assert (entry.header_offset+30+nm+ex)%(16384 if entry.filename.endswith('.so') else 4)==0
        assert set(changed)=={BUNDLE,LIB};assert new.read(BUNDLE)==payload and new.read(LIB)==replacement
        f.seek(-22,2);eocd=struct.unpack('<4s4H2IH',f.read(22))
        assert eocd[0]==b'PK\x05\x06' and eocd[-1]==0 and eocd[5]+eocd[6]+22==stage.stat().st_size
    badging=subprocess.run([str(Path(aapt2).resolve()),'dump','badging',str(stage)],capture_output=True,text=True,check=True).stdout
    assert "package: name='com.candywriter.bitlife'" in badging and "versionCode='1062'"in badging
    (ROOT/'community_aapt2_badging.txt').write_text(badging)
    with stage.open('r+b') as f:f.flush();os.fsync(f.fileno())
    assert stage.stat().st_size>260000000
    final=out/'BitLife_Community_Expansion_v3.apk';stage.replace(final);unsigned.unlink()
    zipstage=out/'community-backup.tmp';backup=out/'BitLife_Community_Expansion_v3.zip'
    with zipfile.ZipFile(zipstage,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as z:z.write(final,final.name)
    with zipfile.ZipFile(zipstage) as z:
        assert z.testzip() is None and z.namelist()==[final.name] and sha(z.read(final.name))==sha_file(final)
    with zipstage.open('r+b') as f:f.flush();os.fsync(f.fileno())
    zipstage.replace(backup)
    report={'input_sha256':BASELINE,'output_sha256':sha_file(final),'output_bytes':final.stat().st_size,
      'backup_zip_sha256':sha_file(backup),'backup_zip_bytes':backup.stat().st_size,
      'new_records':644,'previous_additions_preserved':1064,'total_authored_additions':1708,
      'tables':counts,'native_physical_line_regressions':loader_checks,'weapon_pool_checks':pools,
      'prison_icon_patch':icon_details,'icon_instruction_emulation':icon_tests,'existing_age_guard_emulation':guard_tests,
      'unrelated_unity_objects_preserved':len(before)-len(modified),'changed_apk_entries':changed,
      'all_other_apk_entries_preserved':True,'signature_checks':checks,'crc_eocd_alignment_android_parse':'passed',
      'phone_runtime_tested':False,
      'limits':['Native menus retain existing access and eligibility rules.','Choice events remain probabilistic.',
        'New prison jobs use a generic factory fallback; original job icons are preserved.',
        'Reality TV, F1 and sports receive supporting careers/content, not full new simulation engines.',
        'Taxes receive decision-event content, not a new tax calculation system.',
        'No new face/hair asset system or paid entitlement changes.']}
    (ROOT/'community_expansion_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'apk':str(final),'zip':str(backup),'bytes':report['output_bytes'],'new_records':644,
      'physical_line_tables_checked':len(loader_checks),'prior_tables_failing_blank_record':sum(v['before']!='passed' for v in loader_checks.values()),
      'signature_checks':checks,'guard_emulation':guard_tests,'icon_emulation':icon_tests},indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('apk');p.add_argument('out');p.add_argument('--aapt2',required=True)
    a=p.parse_args();build(a.apk,a.out,a.aapt2)
