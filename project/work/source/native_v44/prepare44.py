"""Extract the two pinned native test inputs without printing signing data."""
import hashlib,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def prepare(base43,base42,out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 for path,expected,version in [(base43,'9bc2beed4310a678f85dcc53592e12c6864668976bed3bc18df3c0d4631bf697',43),(base42,'7638ab770b307d3846a5f2e02072cf423f66fb7cd2be724545e93a6b70fa80ed',42)]:
  path=Path(path);assert hashlib.sha256(path.read_bytes()).hexdigest()==expected
  with zipfile.ZipFile(path)as z:
   raw=z.read('lib/arm64-v8a/libil2cpp.so');(out/f'libil2cpp{version}.so').write_bytes(raw)
   if version==42:(ROOT.parents[2]/'libil2cpp42.so').write_bytes(raw)
   else:(out/'global-metadata.dat').write_bytes(z.read('assets/bin/Data/Managed/Metadata/global-metadata.dat'))
 print('Verified v44 inputs prepared.',flush=True)
if __name__=='__main__':prepare(*sys.argv[1:])
