"""Rebuild the standalone read-only install reader with Android SDK tools."""
import argparse,hashlib,json,subprocess,zipfile
from pathlib import Path

def build(tools,signing_source,apksig,key,cert,output):
    root=Path(__file__).resolve().parent
    tools,signing_source,apksig,key,cert,output=map(Path,[tools,signing_source,apksig,key,cert,output])
    for d in [root/'classes',root/'dex',output]:d.mkdir(parents=True,exist_ok=True)
    def run(args):
        r=subprocess.run(list(map(str,args)),capture_output=True,text=True,check=True,timeout=60)
        return r.stdout+r.stderr
    run(['java','com.sun.tools.javac.Main','--release','8','-classpath',tools/'android.jar',
         '-d',root/'classes',root/'src/com/chance/mayoinstallcheck/MainActivity.java'])
    with zipfile.ZipFile(root/'classes.jar','w')as z:
        for p in (root/'classes').rglob('*.class'):z.write(p,p.relative_to(root/'classes').as_posix())
    run(['java','-Xmx512m','-cp',tools/'r8.jar','com.android.tools.r8.D8','--min-api','26',
         '--lib',tools/'android.jar','--output',root/'dex',root/'classes.jar'])
    run([tools/'aapt2_64','link','-I',tools/'android.jar','--manifest',root/'AndroidManifest.xml',
         '-o',root/'resources.apk'])
    with zipfile.ZipFile(root/'resources.apk')as old,zipfile.ZipFile(root/'unsigned.apk','w',
            compression=zipfile.ZIP_DEFLATED,allowZip64=False)as z:
        for i in old.infolist():z.writestr(i,old.read(i.filename))
        for p in (root/'dex').glob('*.dex'):z.write(p,p.name)
    final=output/'MayoMods_Install_Reader_v1.apk'
    run(['java','-cp',apksig,signing_source/'SignApk.java',root/'unsigned.apk',final,key,cert])
    signature=run(['java','-cp',apksig,signing_source/'VerifyApk.java',final,'33','33'])
    assert 'verified=true'in signature and 'errors=[]'in signature
    badging=run([tools/'aapt2_64','dump','badging',final])
    assert "name='com.chance.mayoinstallcheck'"in badging and 'uses-permission:'not in badging
    report=dict(passed=True,apk=final.name,bytes=final.stat().st_size,
                sha256=hashlib.file_digest(final.open('rb'),'sha256').hexdigest(),
                signature_android13=signature,android_package_parser_passed=True,
                requested_permissions=[],physical_device_tested=False,
                root_access_on_phone_tested=False)
    (root/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    (root/'aapt_badging.txt').write_text(badging)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for arg in ['tools','signing-source','apksig','key','cert','output']:p.add_argument('--'+arg,required=True)
    print(json.dumps(build(**{k.replace('-','_'):v for k,v in vars(p.parse_args()).items()})))
