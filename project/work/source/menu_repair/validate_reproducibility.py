"""Prove native rebuild equality and independent-process content ordering."""
import hashlib,json,os,subprocess,sys
from pathlib import Path


def validate(base,work):
    work=Path(work);base=Path(base).resolve()
    code="import json,hashlib;from menu_repair.content import build;b=json.load(open("+repr(str(base))+"));print(hashlib.sha256(json.dumps(build(b),sort_keys=True).encode()).hexdigest())"
    hashes=[]
    for seed in ['1','17']:
        env=dict(os.environ,PYTHONHASHSEED=seed)
        result=subprocess.run([sys.executable,'-c',code],env=env,capture_output=True,text=True,check=True)
        hashes.append(result.stdout.strip())
    expected=json.loads((work/'content_validation.json').read_text())['authored_assets_sha256']
    assert len(set(hashes))==1 and hashes[0]==expected,(hashes,expected)
    report=dict(passed=True,hash_seeds=[1,17],authored_assets_sha256=expected)
    (work/'content_reproducibility.json').write_text(json.dumps(report,indent=2)+'\n')
    digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    a=digest(work/'libil2cpp.so');b=digest(work/'reproduced_libil2cpp.so');assert a==b,(a,b)
    native=dict(passed=True,binary_sha256=a,exact_native_rebuild=True,source_namespace='menu_repair',phone_tested=False)
    (work/'native_reproducibility.json').write_text(json.dumps(native,indent=2)+'\n');print(report)
if __name__=='__main__':validate(*sys.argv[1:])
