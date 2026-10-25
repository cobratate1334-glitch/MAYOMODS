"""Replace only the setup UI families; preserve every other original DEX class."""
import hashlib,json,shutil,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE))
from native_v54.build_dex54 import run,norm

def build(base,work,tools,java):
    work=Path(work);tools=Path(tools);work.mkdir(parents=True,exist_ok=False)
    cls=work/'classes';dex=work/'dex';cls.mkdir();dex.mkdir()
    overrides=list((ROOT/'java/com/chance/bitlifediag').glob('*.java'))
    families={p.stem for p in overrides}
    deps=list((SOURCE/'native_v54/java/com/chance/bitlifediag').glob('*.java'))
    deps=[p for p in deps if p.stem not in families]
    names=families|{p.stem for p in deps}
    deps += [p for p in (SOURCE/'native_v32/java/com/chance/bitlifediag').glob('*.java') if p.stem not in names|{'LauncherIcon','FloatingDisplay'}]
    deps += [SOURCE/'native_v15/java/com/chance/bitlifediag'/f for f in ['NamePackUI.java','PackCatalog.java','PackFormat.java']]
    deps += [SOURCE/'native_v37/java/com/chance/bitlifediag'/f for f in ['LauncherIcon.java','LauncherMotion.java','FloatingDisplay.java']]
    run([java,'-m','jdk.compiler/com.sun.tools.javac.Main','-source','8','-target','8','-cp',tools/'android.jar','-d',cls,*overrides,*deps])
    run([java,'-cp',tools/'r8.jar','com.android.tools.r8.D8','--min-api','25','--lib',tools/'android.jar','--output',dex,*cls.rglob('*.class')])
    dt=SOURCE/'diagnostic/src/DexTool.java';new=work/'new';smali=work/'original'
    run([java,'-cp',tools/'apktool.jar',dt,'disassemble',dex/'classes.dex',new])
    with zipfile.ZipFile(base)as z:(work/'old.dex').write_bytes(z.read('classes13.dex'))
    run([java,'-cp',tools/'apktool.jar',dt,'disassemble',work/'old.dex',smali])
    before={str(f.relative_to(smali)):f.read_text() for f in smali.rglob('*.smali')}
    def selected(f):return f.parent.name=='bitlifediag' and f.stem.split('$')[0]in families
    for f in smali.rglob('*.smali'):
        if selected(f):f.unlink()
    for f in new.rglob('*.smali'):
        if selected(f):
            dst=smali/f.relative_to(new);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dst)
    unchanged=[p for p,t in before.items()if not selected(Path(p))]
    assert all(norm(before[p])==norm((smali/p).read_text()) for p in unchanged)
    target=work/'classes13.dex';run([java,'-cp',tools/'apktool.jar',dt,'assemble',smali,target])
    rt=work/'roundtrip';run([java,'-cp',tools/'apktool.jar',dt,'disassemble',target,rt])
    for f in smali.rglob('*.smali'):assert norm(f.read_text())==norm((rt/f.relative_to(smali)).read_text())
    report=dict(passed=True,binary_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),preserved_classes=len(unchanged),changed_families=sorted(families),smali_roundtrip=True,min_api=25,ART_tested=False)
    (work/'dex_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':build(*sys.argv[1:])
