"""Advance diagnostic labels; retain every Android executable Dex body."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent;sys.path.insert(0,str(SOURCE))
from native_v48 import diagnostics48 as previous
source=Path(previous.__file__).read_text().replace("b'v47'","b'v49'").replace("b'v48');","b'v50');").replace("'diagnostics48_validation.json'","'diagnostics50_validation.json'")
source=source[:source.index("if __name__=='__main__'")]
namespace={'__file__':str(ROOT/'diagnostics50_generated.py'),'__name__':'diagnostics50_generator'}
exec(compile(source,namespace['__file__'],'exec'),namespace)
if __name__=='__main__':namespace['build'](sys.argv[1])
