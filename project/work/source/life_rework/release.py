"""Sign the validated follow-up with the existing development identity only."""
import base64,hashlib,json,struct,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
CERT='bb8062953a3abe6ed051c29f4d39051d8266940c912323560baa3b795ddd92ef'
def sha(b):return hashlib.sha256(b).hexdigest()
def release(work,identity,java,aapt):
 work=Path(work);identity=Path(identity);staged=work/'MayoMods_1104_UNSIGNED_WORK.apk';s=json.loads((work/'staging_report.json').read_text());assert sha(staged.read_bytes())==s['apk_sha256']
 for name in ['native_validation.json','web_native_validation.json','structure_validation.json','early_validation.json']:
  r=json.loads((work/name).read_text());assert r['passed']and r['binary_sha256']==s['native_sha256']
 r=json.loads((work/'fixtures/native53_validation.json').read_text());assert r['passed']and r['binary_sha256']==s['native_sha256']
 r=json.loads((work/'ui/ui_validation.json').read_text());assert r['passed'];actual={f.relative_to(work/'site').as_posix():sha(f.read_bytes())for f in (work/'site').rglob('*')if f.is_file()};assert actual==r['source_sha256']
 der=(identity/'mayomods-cert.der').read_bytes();assert sha(der)==CERT
 with zipfile.ZipFile(staged)as z:
  assert z.read('classes12.dex').count(CERT.upper().encode())==1
  assert z.read('lib/arm64-v8a/libRocketGames.so')[0x4ff2d:0x4ff2d+28]==base64.b64encode(hashlib.sha1(der).digest())
 out=work/'signed';out.mkdir(exist_ok=True);target=out/'MayoMods_1104_Life_Rework.apk';assert not target.exists()
 jar=SOURCE/'tools/apksig-8.7.3.jar';assert sha(jar.read_bytes())=='c070ed1394629d74641aa0906f60b2ffa1ee77e6366a1f93437f59717b1aeb89'
 def run(program,*args):return subprocess.run([str(java),'-cp',str(jar),str(SOURCE/program),*map(str,args)],check=True,capture_output=True,text=True).stdout
 run('SignApk.java',staged,target,identity/'mayomods-key.pem',identity/'mayomods-cert.der');verification=run('VerifyApk.java',target);assert all(v in verification for v in ['verified=true','v2=true','v3=true','errors=[]','warnings=[]'])
 nativecheck=run('VerifyNativeSigner.java',target);assert 'verified=true'in nativecheck
 badging=subprocess.run([str(aapt),'dump','badging',str(target)],check=True,capture_output=True,text=True).stdout;assert "versionCode='1104'"in badging and "package: name='com.candywriter.bitlife'"in badging
 with zipfile.ZipFile(staged)as before,zipfile.ZipFile(target)as after,target.open('rb')as stream:
  assert after.testzip()is None;assert len(after.namelist())==len(set(after.namelist()))
  assert all(after.read(n)==before.read(n)for n in before.namelist())
  for x in after.infolist():
   if x.compress_type!=zipfile.ZIP_STORED:continue
   stream.seek(x.header_offset+26);n,extra=struct.unpack('<HH',stream.read(4));assert(x.header_offset+30+n+extra)%(16384 if x.filename.endswith('.so')else 4)==0
 report=dict(passed=True,apk_sha256=sha(target.read_bytes()),apk_md5=hashlib.md5(target.read_bytes()).hexdigest(),bytes=target.stat().st_size,native_sha256=s['native_sha256'],certificate_sha256=CERT,version_code=1104,package='com.candywriter.bitlife',same_development_signer=True,signatures=verification,native_signer_verification=nativecheck,aapt2_badging_passed=True,ZIP_CRC_16KB_alignment_passed=True,all_unsigned_payloads_preserved=True,ART_tested=False,phone_install_tested=False,Unity_rendering_tested=False)
 (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n');(out/'aapt_badging.txt').write_text(badging);print(str(target));print(json.dumps({k:report[k]for k in ['apk_sha256','bytes','version_code','passed']}))
if __name__=='__main__':release(*sys.argv[1:])
