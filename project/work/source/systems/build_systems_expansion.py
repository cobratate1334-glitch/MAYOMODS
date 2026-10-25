"""Community Systems v4: exact v3 baseline, new native bridge/UI and 60 scenes."""
import copy,csv,hashlib,io,json,os,shutil,struct,subprocess,sys,zipfile,zlib
from pathlib import Path
import UnityPy
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE));sys.path.insert(0,str(SOURCE/'tests'))
from build_prison_expansion import decode,encode,records,sha,sha_file,signature_entry
from build_community_expansion import validate_content
from community_loader_test import check_table,check_icon_patch
from dealer_guard_test import validate as guard
from patch_frame import patch
from test_frame import validate as frame_test
BASELINE='92bf5dd7373b764d1c80fc0035842736548f08ebc09c3486869debf4f97b5bef'
BUNDLE='assets/bin/Data/datapack.unity3d';LIB='lib/arm64-v8a/libil2cpp.so';BRIDGE='lib/arm64-v8a/libchance_expansion.so'
def run(cmd):return subprocess.run(list(map(str,cmd)),check=True,capture_output=True,text=True).stdout.strip()
def normal(p):return [s.strip()for s in p.read_text().splitlines()if s.strip()and not s.strip().startswith('#')]
def build(apk,work,tools):
 apk=Path(apk).resolve();work=Path(work).resolve();tools=Path(tools).resolve();work.mkdir(parents=True,exist_ok=True)
 assert sha_file(apk)==BASELINE
 for p,h in [(tools/'android.jar','4566663c3876e022b4fa4ced8c8697c4ab1688267f090114fd92d027b32e619b'),(tools/'apktool.jar','66cf4524a4a45a7f56567d08b2c9b6ec237bcdd78cee69fd4a59c8a0243aeafa'),(work/'r8.jar','badba8e0fd96dc9f41f53a0686f20fc08f1172a9816461fec13b6635b7c883fa')]:assert sha_file(p)==h
 classes=work/'classes';classes.mkdir(exist_ok=True)
 sources=sorted((SOURCE/'diagnostic/src/com/chance/bitlifediag').glob('*.java'))+sorted((ROOT/'java/com/chance/bitlifediag').glob('*.java'))
 run(['java','-m','jdk.compiler/com.sun.tools.javac.Main','-source','8','-target','8','-cp',tools/'android.jar','-d',classes,*sources])
 tests=work/'tests';tests.mkdir(exist_ok=True)
 run(['java','-m','jdk.compiler/com.sun.tools.javac.Main','-source','8','-target','8','-d',tests,ROOT/'java/com/chance/bitlifediag/ExpansionState.java',ROOT/'ExpansionStateTest.java'])
 state_result=run(['java','-cp',tests,'com.chance.bitlifediag.ExpansionStateTest'])
 run(['java','-m','jdk.compiler/com.sun.tools.javac.Main','-cp',classes,'-d',tests,SOURCE/'diagnostic/tests/RuntimeLogStoreTest.java'])
 log_result=run(['java','-cp',str(classes)+os.pathsep+str(tests),'com.chance.bitlifediag.RuntimeLogStoreTest'])
 dex=work/'dex';dex.mkdir(exist_ok=True)
 run(['java','-cp',work/'r8.jar','com.android.tools.r8.D8','--min-api','25','--lib',tools/'android.jar','--output',dex,*sorted(classes.rglob('*.class'))])
 original_smali=work/'original-smali';new_smali=work/'smali';roundtrip=work/'roundtrip-smali'
 for d in (original_smali,new_smali,roundtrip):shutil.rmtree(d,ignore_errors=True)
 with zipfile.ZipFile(apk)as z:(work/'original.dex').write_bytes(z.read('classes13.dex'))
 dex_tool=SOURCE/'diagnostic/src/DexTool.java'
 run(['java','-cp',tools/'apktool.jar',dex_tool,'disassemble',work/'original.dex',original_smali])
 run(['java','-cp',tools/'apktool.jar',dex_tool,'disassemble',dex/'classes.dex',new_smali])
 for name in ['NativeDiagnostics.smali','TombstoneReader.smali','TombstoneReader$Field.smali','TombstoneReader$Reader.smali']:
  path=Path('com/chance/bitlifediag')/name;shutil.copyfile(original_smali/path,new_smali/path)
 run(['java','-cp',tools/'apktool.jar',dex_tool,'assemble',new_smali,dex/'classes.dex'])
 dexbytes=(dex/'classes.dex').read_bytes();assert dexbytes[12:32]==hashlib.sha1(dexbytes[32:]).digest() and struct.unpack_from('<I',dexbytes,8)[0]==zlib.adler32(dexbytes[12:])&0xffffffff
 run(['java','-cp',tools/'apktool.jar',dex_tool,'disassemble',dex/'classes.dex',roundtrip])
 for p in new_smali.rglob('*.smali'):assert normal(p)==normal(roundtrip/p.relative_to(new_smali))
 assert (new_smali/'com/chance/bitlifediag/ExpansionHub.smali').is_file()
 bridge=(work/'libchance_expansion.so').read_bytes();be=ELFFile(io.BytesIO(bridge));assert be['e_machine']=='EM_AARCH64' and be['e_type']=='ET_DYN'
 deps=[t.needed for t in be.get_section_by_name('.dynamic').iter_tags()if t.entry.d_tag=='DT_NEEDED'];assert deps==['libc.so','libdl.so']
 assert all(s['p_align']>=16384 for s in be.iter_segments()if s['p_type']=='PT_LOAD')
 with zipfile.ZipFile(apk)as z:oldlib=z.read(LIB);env=UnityPy.load(z.read(BUNDLE))
 sym=ELFFile(io.BytesIO(oldlib)).get_section_by_name('.dynsym');assert sym.get_symbol_by_name('il2cpp_domain_get')[0]['st_value']==0x223e48c
 needed=['il2cpp_domain_get','il2cpp_domain_get_assemblies','il2cpp_assembly_get_image','il2cpp_image_get_name','il2cpp_class_from_name','il2cpp_class_get_field_from_name','il2cpp_field_static_get_value','il2cpp_field_get_value','il2cpp_object_get_class','il2cpp_class_get_method_from_name','il2cpp_runtime_invoke','il2cpp_object_unbox','il2cpp_string_length','il2cpp_string_chars']
 assert all(sym.get_symbol_by_name(n)for n in needed)
 native,details=patch(oldlib);(ROOT/'frame_patch_details.json').write_text(json.dumps(details,indent=2)+'\n')
 frame=frame_test(native);guards=guard(native,json.loads((SOURCE/'dealer_fix_details.json').read_text()));icons=check_icon_patch(native)
 content=json.loads((ROOT/'age_content.json').read_text());before={o.path_id:sha(o.get_raw_data())for o in env.objects};changed=set();expected={};counts={};all_ids=set()
 for o in env.objects:
  if o.type.name!='TextAsset':continue
  a=o.read()
  if not a.m_Name.endswith('-enc'):continue
  try:old=records(decode(a.m_Script))
  except:continue
  if 'Index'in old[0]:all_ids.update(r[old[0].index('Index')] for r in old[1:])
  if a.m_Name not in content:continue
  newrows=content[a.m_Name];validate_content(a.m_Name,old,newrows);expected[a.m_Name]=old+[[r[h]for h in old[0]]for r in newrows]
  stream=io.StringIO(newline='');csv.writer(stream,lineterminator='\n').writerows(expected[a.m_Name]);text=stream.getvalue().removesuffix('\n');check_table(decode(a.m_Script),text,expected[a.m_Name]);a.m_Script=encode(text);a.save();changed.add(o.path_id);counts[a.m_Name]={'preserved':len(old)-1,'added':len(newrows),'total':len(expected[a.m_Name])-1}
 ids=[r['Index']for rows in content.values()for r in rows];assert len(ids)==len(set(ids))and not(set(ids)&all_ids)
 bundle=next(iter(env.files.values())).save(packer='original');rebuilt=UnityPy.load(bundle)
 for o in rebuilt.objects:
  if o.path_id in changed:
   a=o.read();assert records(decode(a.m_Script))==expected[a.m_Name]
  else:assert sha(o.get_raw_data())==before[o.path_id]
 unsigned=work/'systems-unsigned.tmp';stage=work/'systems-signed.tmp'
 replacements={BUNDLE:bundle,LIB:native,'classes13.dex':dexbytes,BRIDGE:bridge}
 with zipfile.ZipFile(apk)as old,zipfile.ZipFile(unsigned,'w',allowZip64=False)as new:
  for item in old.infolist():
   if signature_entry(item.filename):continue
   info=copy.copy(item);info.extra=b''
   if info.compress_type==zipfile.ZIP_STORED:
    alignment=16384 if info.filename.endswith('.so')else 4;pos=new.fp.tell()+30+len(info.filename.encode('utf8'))
    if pos%alignment:
     pad=(-pos-4)%alignment
     if pad<2:pad+=alignment
     info.extra=struct.pack('<HHH',0xd935,pad,alignment)+b'\0'*(pad-2)
   new.writestr(info,replacements.get(item.filename,old.read(item.filename)),compresslevel=6)
  info=zipfile.ZipInfo(BRIDGE);info.compress_type=zipfile.ZIP_STORED;info.external_attr=0o100644<<16;pos=new.fp.tell()+30+len(BRIDGE)
  if pos%16384:
   pad=(-pos-4)%16384
   if pad<2:pad+=16384
   info.extra=struct.pack('<HHH',0xd935,pad,16384)+b'\0'*(pad-2)
  new.writestr(info,bridge)
 with unsigned.open('r+b')as f:f.flush();os.fsync(f.fileno())
 with zipfile.ZipFile(unsigned)as z:assert z.testzip()is None
 jar=SOURCE/'tools/apksig-8.7.3.jar';checks={}
 run(['java','-cp',jar,SOURCE/'SignApk.java',unsigned,stage,SOURCE/'signing/music-test-key.pem',SOURCE/'signing/music-test-cert.der'])
 for p in ('VerifyApk.java','VerifyNativeSigner.java'):checks[p]=run(['java','-cp',jar,SOURCE/p,stage]);assert 'verified=true'in checks[p]
 assert all(x in checks['VerifyApk.java']for x in ['v2=true','v3=true','errors=[]','warnings=[]'])
 changes=[]
 with zipfile.ZipFile(apk)as old,zipfile.ZipFile(stage)as new,stage.open('rb')as f:
  assert new.testzip()is None and len(new.namelist())==len(set(new.namelist()))
  assert {n for n in new.namelist()if not signature_entry(n)}=={n for n in old.namelist()if not signature_entry(n)}|{BRIDGE}
  for entry in new.infolist():
   if entry.filename in replacements:assert new.read(entry.filename)==replacements[entry.filename];changes.append(entry.filename)
   elif not signature_entry(entry.filename):assert new.read(entry.filename)==old.read(entry.filename)
   if entry.compress_type==zipfile.ZIP_STORED:
    f.seek(entry.header_offset+26);nm,ex=struct.unpack('<HH',f.read(4));assert(entry.header_offset+30+nm+ex)%(16384 if entry.filename.endswith('.so')else 4)==0
  f.seek(-22,2);end=struct.unpack('<4s4H2IH',f.read(22));assert end[0]==b'PK\x05\x06'and end[-1]==0 and end[5]+end[6]+22==stage.stat().st_size
 badging=run([tools/'aapt2','dump','badging',stage]);assert "name='com.candywriter.bitlife'"in badging and "versionCode='1062'"in badging and "minSdkVersion:'25'"in badging
 (ROOT/'aapt2_badging.txt').write_text(badging+'\n')
 assert stage.stat().st_size>260000000
 final=work/'BitLife_Community_Systems_v4.apk';stage.replace(final);unsigned.unlink()
 zipstage=work/'systems-backup.tmp';backup=work/'BitLife_Community_Systems_v4.zip'
 with zipfile.ZipFile(zipstage,'w',zipfile.ZIP_DEFLATED,compresslevel=1)as z:z.write(final,final.name)
 with zipfile.ZipFile(zipstage)as z:assert z.testzip()is None and sha(z.read(final.name))==sha_file(final)
 zipstage.replace(backup)
 report={'baseline_sha256':BASELINE,'output_sha256':sha_file(final),'output_bytes':final.stat().st_size,'zip_sha256':sha_file(backup),'zip_bytes':backup.stat().st_size,'age_scenes_added':len(ids),'tables':counts,'prior_1708_added_records_preserved':True,'state_simulation_test':state_result,'diagnostic_test':log_result,'frame_instruction_emulation':frame,'dealer_guard_emulation':guards,'prison_icon_emulation':icons,'unrelated_unity_objects_byte_preserved':len(before)-len(changed),'changed_or_added_apk_entries':changes,'other_apk_entries_byte_preserved':True,'signature_checks':checks,'dex_smali_roundtrip':'passed','crc_alignment_eocd':'passed','native_bridge_deps':deps,'systems':['Music studio and independent distribution','Social creator business','Work portfolios','School enrichment and adult study','Sports academy','Motorsport championships','Reality TV seasons','Luxury asset ledger and expansion tax','Annual decision queue'],'integration':'Native MOD+ hub; read-only game identity, age and occupation; addon saves and credits separate from base game. Original menus unchanged.','phone_runtime_tested':False}
 (ROOT/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':build(*sys.argv[1:])
