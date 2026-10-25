"""Exercise disk persistence/rotation and Android exit recovery on the JVM.

Android service responses are fixtures; crash protobuf parsing and file writes
are real. Compilation against Android 35 and DEX checks run separately.
"""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def run(args):return subprocess.run(list(map(str,args)),text=True,capture_output=True,check=True).stdout.strip()
def validate():
 out=ROOT/'log_test_classes';out.mkdir(exist_ok=True);source=ROOT/'java/com/chance/bitlifediag';old=ROOT.parent/'diagnostic/tests'
 sources=[source/(name+'.java')for name in ['RuntimeLogStore','CrashJournal','NativeCrashReader','TombstoneReader']]
 sources+=list((ROOT/'tests').rglob('*.java'))+[old/'RuntimeLogStoreTest.java',old/'com/chance/bitlifediag/TombstoneReaderTest.java']
 run(['java','-m','jdk.compiler/com.sun.tools.javac.Main','-d',out,*sources]);results={}
 for name in ['RuntimeLogStoreTest','CrashJournalTest','TombstoneReaderTest','NativeCrashReaderTest']:results[name]=run(['java','-cp',out,'com.chance.bitlifediag.'+name]);print(results[name],flush=True)
 result=dict(passed=True,tests=results,persistent_errors_and_previous_sessions=True,critical_checkpoints_flushed=True,logs_bounded_and_PID_filtered=True,native_trace_PID_process_validated=True,old_Android_fallback=True,Android_service_responses_mocked=True,device_runtime_tested=False)
 (ROOT/'logging23_validation.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':validate()
