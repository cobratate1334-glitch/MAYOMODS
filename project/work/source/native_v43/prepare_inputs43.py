"""Extract only verified native inputs from the released v42 APK."""
import hashlib,sys,zipfile
from pathlib import Path
def prepare(base,out):
 base=Path(base);out=Path(out);out.mkdir(parents=True,exist_ok=True)
 assert hashlib.sha256(base.read_bytes()).hexdigest()=='7638ab770b307d3846a5f2e02072cf423f66fb7cd2be724545e93a6b70fa80ed'
 with zipfile.ZipFile(base)as z:
  for source,target in [('lib/arm64-v8a/libil2cpp.so','libil2cpp42.so'),('assets/bin/Data/Managed/Metadata/global-metadata.dat','global-metadata.dat')]:
   (out/target).write_bytes(z.read(source))
 print('Verified v42 inputs prepared.',flush=True)
if __name__=='__main__':prepare(*sys.argv[1:])
