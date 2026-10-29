"""Sign the exact validated era candidate with the existing app identity."""
import base64,hashlib,json,struct,subprocess,sys,zipfile
from pathlib import Path
from era_world.package import NATIVE,DEX,sha
CERT='bb8062953a3abe6ed051c29f4d39051d8266940c912323560baa3b795ddd92ef'
SOURCE=Path(__file__).resolve().parents[1]

def release(work,identity,java,aapt):
 work,identity=Path(work),Path(identity);staged=work/'MayoMods_1119_UNSIGNED_WORK.apk'
 stage=json.loads((work/'staging_report.json').read_text());tests=json.loads((work/'test_results.json').read_text())
 assert stage['staged']and stage['version_code']==1119
 assert tests['passed']and tests['tests_run']==45 and tests['native_sha256']==NATIVE
 assert sha(staged.read_bytes())==stage['apk_sha256']
 der=(identity/'mayomods-cert.der').read_bytes();assert sha(der)==CERT
 with zipfile.ZipFile(staged)as z:
  assert sha(z.read('classes13.dex'))==DEX and sha(z.read('lib/arm64-v8a/libil2cpp.so'))==NATIVE
  assert sha(z.read('lib/arm64-v8a/libmayo21.so'))=='93a6bedf5503db3e917c8e5d7e199fb9af07ab4ef828222a7191c4d5abbcacfc'
  assert z.read('classes12.dex').count(CERT.upper().encode())==1
  assert z.read('lib/arm64-v8a/libRocketGames.so')[0x4ff2d:0x4ff2d+28]==base64.b64encode(hashlib.sha1(der).digest())
 out=work/'signed';out.mkdir(exist_ok=True);target=out/'MayoMods_1119_Era_Themes_and_Mod_Creator.apk';assert not target.exists()
 jar=SOURCE/'tools/apksig-8.7.3.jar';assert sha(jar.read_bytes())=='c070ed1394629d74641aa0906f60b2ffa1ee77e6366a1f93437f59717b1aeb89'
 def run(program,*args):return subprocess.run([str(java),'-cp',str(jar),str(SOURCE/program),*map(str,args)],check=True,capture_output=True,text=True).stdout
 run('SignApk.java',staged,target,identity/'mayomods-key.pem',identity/'mayomods-cert.der')
 verification=run('VerifyApk.java',target);assert all(v in verification for v in ['verified=true','v2=true','v3=true','errors=[]','warnings=[]'])
 nativecheck=run('VerifyNativeSigner.java',target);assert 'verified=true'in nativecheck
 badging=subprocess.run([str(aapt),'dump','badging',str(target)],check=True,capture_output=True,text=True).stdout
 assert "versionCode='1119'"in badging and "package: name='com.candywriter.bitlife'"in badging
 with zipfile.ZipFile(staged)as before,zipfile.ZipFile(target)as after,target.open('rb')as stream:
  assert after.testzip()is None and len(after.namelist())==len(set(after.namelist()))
  assert all(after.read(n)==before.read(n)for n in before.namelist())
  for entry in after.infolist():
   if entry.compress_type!=zipfile.ZIP_STORED:continue
   stream.seek(entry.header_offset+26);n,extra=struct.unpack('<HH',stream.read(4))
   assert(entry.header_offset+30+n+extra)%(16384 if entry.filename.endswith('.so')else 4)==0
 report=dict(passed=True,apk_sha256=sha(target.read_bytes()),apk_md5=hashlib.md5(target.read_bytes()).hexdigest(),bytes=target.stat().st_size,native_sha256=NATIVE,dex_sha256=DEX,certificate_sha256=CERT,version_code=1119,package='com.candywriter.bitlife',same_development_signer=True,signatures=verification,native_signer_verification=nativecheck,aapt2_badging_passed=True,ZIP_CRC_16KB_alignment_passed=True,all_unsigned_payloads_preserved=True,ART_tested=False,phone_install_tested=False,Unity_rendering_tested=False)
 (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n');(out/'aapt_badging.txt').write_text(badging)
 print(target);print(json.dumps({k:report[k]for k in ['apk_sha256','bytes','version_code','passed']}))
if __name__=='__main__':release(*sys.argv[1:])
