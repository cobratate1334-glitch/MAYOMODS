"""Run the controller/model class files emitted by the reviewed DEX build."""
import hashlib,json,os,re,subprocess,sys
from pathlib import Path


def run(dex_folder,out,java_bin=None):
    dex_folder=Path(dex_folder);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    java_bin=Path(java_bin or '/workspace/toolchains/java/usr/lib/jvm/java-21-openjdk-amd64/bin')
    source=Path(__file__).resolve().parent
    report=json.loads((dex_folder/'dex_validation.json').read_text())
    dex=(dex_folder/'classes13.dex').read_bytes()
    assert report['passed']and report['binary_sha256']==hashlib.sha256(dex).hexdigest()
    assert set(report['changed_families'])=={'MilitaryModel','NativeMilitary'}
    classes=dex_folder/'classes';host=out/'classes';host.mkdir(exist_ok=True)
    files=sorted((source/'service_controller').rglob('*.java'))+[source/'WorldWarServiceTest.java']
    subprocess.run([str(java_bin/'javac'),'-encoding','UTF-8','-cp',str(classes),'-d',str(host),*map(str,files)],check=True)
    cp=os.pathsep.join([str(host),str(classes)]);results={}
    for test in ['WorldWarServiceTest','NativeMenuTest']:
        result=subprocess.run([str(java_bin/'java'),'-cp',cp,test],capture_output=True,text=True,check=True)
        print(result.stdout.strip());results[test]=result.stdout.strip()
    summary=dict(passed=True,dex_sha256=report['binary_sha256'],model_checks=int(re.search(r'(\d+) checks',results['WorldWarServiceTest'])[1]),controller=json.loads(results['NativeMenuTest']),compiled_candidate_class_files_executed=True,JNI_and_graphics_modeled=True,ART_tested=False,phone_tested=False)
    (out/'service_controller_report.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary

if __name__=='__main__':run(*sys.argv[1:])
