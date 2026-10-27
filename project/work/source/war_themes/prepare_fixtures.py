import shutil,sys
from pathlib import Path
if __name__=='__main__':
 old,manifest,out=map(Path,sys.argv[1:]);shutil.copytree(old,out,dirs_exist_ok=True);shutil.copyfile(manifest,out/'native_hooks.json')
