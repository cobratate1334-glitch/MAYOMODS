"""Compile current diagnostic Java and run persistence/filtering regressions."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def run(args):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout.strip()
def validate():
 out=ROOT/'log_test_classes';out.mkdir(exist_ok=True)
 source=ROOT/'java/com/chance/bitlifediag'
 sources=[source/(n+'.java')for n in ['RuntimeLogStore','CrashJournal','NativeCrashReader','TombstoneReader']]
 sources+=list((ROOT/'tests').rglob('*.java'))
 sources.append(ROOT.parent/'diagnostic/tests/com/chance/bitlifediag/TombstoneReaderTest.java')
 run(['java','-m','jdk.compiler/com.sun.tools.javac.Main','-d',out,*sources])
 results={}
 for name in ['RuntimeLogStoreTest','CrashJournalTest','TombstoneReaderTest','NativeCrashReaderTest','RecoveredLauncherJournalTest','NativeFatalJournalTest']:
  results[name]=run(['java','-cp',out,'com.chance.bitlifediag.'+name]);print(results[name],flush=True)
 report=dict(passed=True,tests=results,own_process_fatal_lines_preserved=True,
             native_fatal_recovered_without_Android11_exit_history=True,
             preflight_library_error_persisted=True,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in source.glob('*.java')},
             Android_service_responses_mocked=True,device_runtime_tested=False)
 (ROOT/'logging30_validation.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':validate()
