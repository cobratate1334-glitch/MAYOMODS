"""Build against Android's libc/libdl ABI via link-only symbol stubs.
Only libchance_expansion.so is shipped. Stub libraries never enter the APK.
"""
import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent
work=Path(sys.argv[1]).resolve();work.mkdir(parents=True,exist_ok=True)
for name in ('libc','libdl'):
 subprocess.run([sys.executable,'-m','ziglang','cc','-target','aarch64-linux-android','-shared','-nostdlib','-Wl,-soname,'+name+'.so',str(root/('import_'+name+'.c')),'-o',str(work/(name+'.so'))],check=True,capture_output=True)
subprocess.run([sys.executable,'-m','ziglang','cc','-target','aarch64-linux-android','-shared','-fPIC','-O2','-nostdlib','-fno-stack-protector','-Wl,-soname,libchance_expansion.so','-Wl,-z,max-page-size=16384',str(root/'bridge.c'),str(work/'libc.so'),str(work/'libdl.so'),'-o',str(work/'libchance_expansion.so')],check=True,capture_output=True)
