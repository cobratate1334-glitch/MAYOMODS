"""Run the authored native Android Views under Robolectric native Skia (not ART).

Prepare dependency jars using tests/pom.xml and Maven dependency:copy-dependencies;
extract classes.jar from both monitor and espresso AARs into that dependency folder.
Provide android-all-instrumented SDK 9/13/15 jars with the i7 suffix there as well.
"""
import hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def run(classes,dependencies,output):
    classes,dependencies,output=map(lambda p:Path(p).resolve(),[classes,dependencies,output]);output.mkdir(parents=True,exist_ok=True)
    jars=[p for p in dependencies.glob('*.jar')if not p.name.startswith('android-all-instrumented-')]
    assert jars and (classes/'com/chance/bitlifediag/StartupActivity.class').exists()
    testclasses=output/'classes';testclasses.mkdir(exist_ok=True)
    cp=os.pathsep.join(map(str,jars+[classes]))
    compile_result=subprocess.run(['java','-m','jdk.compiler/com.sun.tools.javac.Main','-cp',cp,'-d',str(testclasses),str(ROOT/'tests/LauncherUITest.java')],capture_output=True,text=True)
    assert compile_result.returncode==0,compile_result.stdout+compile_result.stderr
    screenshot=output/'MayoMods_v36_Launcher.png'
    result=subprocess.run(['java','-Drobolectric.dependency.dir='+str(dependencies),'-Dlauncher.screenshot='+str(screenshot),'-cp',str(testclasses)+os.pathsep+cp,'org.junit.runner.JUnitCore','com.chance.bitlifediag.LauncherUITest'],capture_output=True,text=True)
    (output/'result.txt').write_text(result.stdout+result.stderr)
    assert result.returncode==0 and 'OK (4 tests)'in result.stdout,result.stdout+result.stderr
    report=dict(passed=True,tests=4,Android_API_levels=[28,33],framework='Robolectric 4.14.1',graphics='native Skia',actual_Android_views_executed=True,layout_widths=[280,360,600],large_font_scale=1.6,
        settings_back_and_persistent_toggles=True,interrupted_animation_and_lifecycle_recovery=True,
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in (ROOT/'java/com/chance/bitlifediag').glob('*.java')},
        tests_sha256=hashlib.sha256((ROOT/'tests/LauncherUITest.java').read_bytes()).hexdigest(),screenshot_sha256=hashlib.sha256(screenshot.read_bytes()).hexdigest(),ART_tested=False,device_tested=False,BlueStacks_tested=False)
    (ROOT/'ui36_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':run(*sys.argv[1:])
