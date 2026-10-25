import json,subprocess,zipfile,hashlib,shutil,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
def run(x):return subprocess.run(list(map(str,x)),check=True,capture_output=True,text=True).stdout
with zipfile.ZipFile('final/BitLife_Native_Activities_v14.apk')as z:
 b=z.read('classes12.dex');Path('analysis/logo12-original.dex').write_bytes(b)
s=Path('analysis/logo12');shutil.rmtree(s,ignore_errors=True)
run(['java','-cp','toolchain/apktool.jar',SOURCE/'diagnostic/src/DexTool.java','disassemble','analysis/logo12-original.dex',s])
p=s/'com/android/support/Menu.smali';t=p.read_text();line='    iput-object v5, v0, Lcom/android/support/Menu;->startimage:Landroid/widget/ImageView;';assert t.count(line)==1
originals={str(f.relative_to(s)):hashlib.sha256(f.read_bytes()).hexdigest()for f in s.rglob('*.smali')}
p.write_text(t.replace(line,line+'\n\n    invoke-static {v5}, Lcom/chance/bitlifediag/FloatingDisplay;->registerLogo(Landroid/view/View;)V'))
run(['java','-cp','toolchain/apktool.jar',SOURCE/'diagnostic/src/DexTool.java','assemble',s,ROOT/'classes12.dex'])
r=Path('analysis/logo12-roundtrip');shutil.rmtree(r,ignore_errors=True);run(['java','-cp','toolchain/apktool.jar',SOURCE/'diagnostic/src/DexTool.java','disassemble',ROOT/'classes12.dex',r])
def norm(t):return '\n'.join(x.strip()for x in t.splitlines()if x.strip()and not x.strip().startswith('#'))
for f in s.rglob('*.smali'):assert norm(f.read_text())==norm((r/f.relative_to(s)).read_text())
for q,v in originals.items():
 if q=='com/android/support/Menu.smali':continue
 assert hashlib.sha256((s/q).read_bytes()).hexdigest()==v
(ROOT/'logo_dex_validation.json').write_text(json.dumps(dict(changed_class='com.android.support.Menu',unchanged_classes=len(originals)-1,roundtrip_verified=True,change='Register the existing logo ImageView for the display toggle'),indent=2))
print('Logo display binding verified')
