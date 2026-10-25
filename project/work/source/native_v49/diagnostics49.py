"""Preserve executable Dex bodies while advancing diagnostic labels to v49."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent;sys.path.insert(0,str(SOURCE))
from native_v48 import diagnostics48 as previous
source=Path(previous.__file__).read_text().replace("b'v47'","b'v48'").replace("b'v48');","b'v49');").replace("'diagnostics48_validation.json'","'diagnostics49_validation.json'")
# Use a controlled source copy with the current root, retaining every
# original byte/code/inverse assertion rather than rewriting the Dex parser.
source=source[:source.index("if __name__=='__main__'")]
namespace={'__file__':str(ROOT/'diagnostics49_generated.py'),'__name__':'diagnostics49_generator'}
exec(compile(source,namespace['__file__'],'exec'),namespace)
if __name__=='__main__':namespace['build'](sys.argv[1])
