"""Compile and run the current journal with existing persistence regressions."""
import json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def run(args):return subprocess.run(list(map(str,args)),capture_output=True,text=True,check=True).stdout.strip()
def validate():
 out=ROOT/'log_test_classes';out.mkdir(exist_ok=True)
 source=ROOT/'java/com/chance/bitlifediag';previous=ROOT.parent/'native_v27/tests';old=ROOT.parent/'diagnostic/tests'
 sources=[source/(n+'.java')for n in ['RuntimeLogStore','CrashJournal','NativeCrashReader','TombstoneReader']]
 sources+=list(previous.rglob('*.java'))+list((ROOT/'tests').rglob('*.java'))+[old/'RuntimeLogStoreTest.java',old/'com/chance/bitlifediag/TombstoneReaderTest.java']
 run(['java','-m','jdk.compiler/com.sun.tools.javac.Main','-d',out,*sources]);results={}
 for name in ['RuntimeLogStoreTest','CrashJournalTest','TombstoneReaderTest','NativeCrashReaderTest','RecoveredLauncherJournalTest']:
  results[name]=run(['java','-cp',out,'com.chance.bitlifediag.'+name]);print(results[name],flush=True)
 result=dict(passed=True,tests=results,recovered_native_load_error_persisted=True,
             previous_sessions_and_API28_fallback_verified=True,checkpoint_trace_limit_chars=1800,
             Android_service_responses_mocked=True,device_runtime_tested=False)
 (ROOT/'logging28_validation.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':validate()
