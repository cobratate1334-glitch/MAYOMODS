"""Overlay reviewed UI class families; retain other release DEX classes."""
import sys,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(SOURCE)]
from web_experience import build_dex as previous

def build(base,work,tools,java):
    # Reuse the verified DEX round-trip assembler, with one temporary source
    # tree containing the newest implementation of each dependency family.
    sandbox=Path(work).with_name(Path(work).name+'-sources');sandbox.mkdir(exist_ok=False)
    target=sandbox/'java/com/chance/bitlifediag';target.mkdir(parents=True)
    deps={}
    for name in ['native_v15','native_v21','native_v32','native_v37','native_v41','native_v42','native_v54','web_experience','life_rework','ui_integrity','military_expansion','native_immersion']:
        for f in (SOURCE/name/'java/com/chance/bitlifediag').glob('*.java'):deps[f.name]=f
    for f in (ROOT/'java/com/chance/bitlifediag').glob('*.java'):deps[f.name]=f
    # Dependencies compile but only the reviewed override families are
    # selected for replacement. The patch below supplies dependency sources to
    # the existing builder without editing historical build scripts.
    for f in (ROOT/'java/com/chance/bitlifediag').glob('*.java'):shutil.copyfile(f,target/f.name)
    source=Path(previous.__file__).read_text();start=source.index('    deps=list(');end=source.index('    run([java,',start)
    source=source.replace("return f.parent.name=='bitlifediag' and f.stem.split('$')[0]in families","return ('com/github/bhlangonijr/chesslib/' in str(f).replace(chr(92),'/')) or (f.parent.name=='bitlifediag' and f.stem.split('$')[0]in families)")
    source=source[:start]+"    deps=[Path(p) for p in DEPENDENCIES if Path(p).stem not in families]\n"+source[end:]
    ns={'__file__':str(sandbox/'build_dex.py'),'__name__':'military_dex_builder','DEPENDENCIES':[str(f)for f in deps.values()]+[str(f)for f in (SOURCE/'military_expansion/vendor').rglob('*.java')]}
    # SOURCE must remain the actual retained source root for DexTool.
    source=source.replace('ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent','ROOT=Path(__file__).resolve().parent;SOURCE=Path('+repr(str(SOURCE))+')')
    exec(compile(source,str(sandbox/'build_dex.py'),'exec'),ns);ns['build'](base,work,tools,java)
if __name__=='__main__':build(*sys.argv[1:])
