import hashlib,json,os,shutil,struct,subprocess,sys,zipfile,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
def run(a):return subprocess.run(list(map(str,a)),capture_output=True,text=True,check=True).stdout.strip()
def build(apk,work,tools):
 work=Path(work);tools=Path(tools);work.mkdir(parents=True,exist_ok=True)
 classes=work/'classes';dex=work/'dex';newsmali=work/'new-smali';oldsmali=work/'merged-smali'
 for d in [classes,dex,newsmali,oldsmali]:shutil.rmtree(d,ignore_errors=True)
 classes.mkdir();dex.mkdir()
 new={f.name:f for f in (ROOT/'java/com/chance/bitlifediag').glob('*.java')}
 sources=[new.get(f.name,f)for f in (SOURCE/'diagnostic/src/com/chance/bitlifediag').glob('*.java')]+[f for n,f in new.items()if not(SOURCE/'diagnostic/src/com/chance/bitlifediag'/n).exists()]
 run(['java','-m','jdk.compiler/com.sun.tools.javac.Main','-source','8','-target','8','-cp',tools/'android.jar','-d',classes,*sources])
 run(['java','-cp',tools/'r8.jar','com.android.tools.r8.D8','--min-api','25','--lib',tools/'android.jar','--output',dex,*classes.rglob('*.class')])
 dexTool=SOURCE/'diagnostic/src/DexTool.java'
 run(['java','-cp',tools/'apktool.jar',dexTool,'disassemble',dex/'classes.dex',newsmali])
 with zipfile.ZipFile(apk)as z:(work/'original.dex').write_bytes(z.read('classes13.dex'))
 run(['java','-cp',tools/'apktool.jar',dexTool,'disassemble',work/'original.dex',oldsmali])
 families=['StartupActivity','RuntimeLogCapture','NamePackUI','PackCatalog','PackFormat','FloatingDisplay'];changed=[];preserved={}
 for f in oldsmali.rglob('*.smali'):
  if f.stem.split('$')[0]in families:f.unlink()
  else:preserved[str(f.relative_to(oldsmali))]=f.read_bytes()
 for f in newsmali.rglob('*.smali'):
  if f.stem.split('$')[0]in families:
   target=oldsmali/f.relative_to(newsmali);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,target);changed.append(str(f.relative_to(newsmali)))
 run(['java','-cp',tools/'apktool.jar',dexTool,'assemble',oldsmali,dex/'classes.dex'])
 payload=(dex/'classes.dex').read_bytes();assert payload[12:32]==hashlib.sha1(payload[32:]).digest();assert struct.unpack_from('<I',payload,8)[0]==zlib.adler32(payload[12:])&0xffffffff
 roundtrip=work/'roundtrip';shutil.rmtree(roundtrip,ignore_errors=True);run(['java','-cp',tools/'apktool.jar',dexTool,'disassemble',dex/'classes.dex',roundtrip])
 def norm(b):return[s.strip()for s in b.decode().splitlines()if s.strip()and not s.strip().startswith('#')]
 for f in oldsmali.rglob('*.smali'):assert norm(f.read_bytes())==norm((roundtrip/f.relative_to(oldsmali)).read_bytes())
 for p,b in preserved.items():assert norm(b)==norm((roundtrip/p).read_bytes()),p
 result=dict(changed_classes=changed,preserved_diagnostic_classes=list(preserved),roundtrip_verified=True,min_api=25)
 (ROOT/'dex_validation.json').write_text(json.dumps(result,indent=2));return payload
if __name__=='__main__':
 payload=build(*sys.argv[1:]);(ROOT/'classes13.dex').write_bytes(payload);print('Diagnostic DEX and display options verified')
