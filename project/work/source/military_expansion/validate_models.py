"""Compile and run the exact dependency-free rules and saved-state tests on a host JVM."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def validate(java,output):
 output=Path(output);output.mkdir(parents=True,exist_ok=True)
 files=[ROOT/'java/com/chance/bitlifediag'/n for n in ['ChessStrings.java','ChessGame.java','MilitaryModel.java']]+sorted((ROOT/'vendor').rglob('*.java'))+[ROOT/'tests/MilitaryModelTest.java']
 subprocess.run([java,'-m','jdk.compiler/com.sun.tools.javac.Main','-source','8','-target','8','-d',str(output),*map(str,files)],check=True,capture_output=True)
 result=subprocess.run([java,'-cp',str(output),'MilitaryModelTest'],check=True,capture_output=True,text=True);report=json.loads(result.stdout);report['sources_sha256']=hashlib.sha256(b''.join(str(f.relative_to(ROOT)).encode()+b'\0'+f.read_bytes()for f in files)).hexdigest();(output.parent/'model_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
