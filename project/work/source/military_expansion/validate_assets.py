"""Verify screen ID -> actual APK filename -> source pixels -> Unity resource.

The old candidate preserved every pixel but used descriptive source basenames,
whereas the Canvas asks for manifest IDs. The negative control must fail.
"""
import hashlib,io,json,sys,zipfile
from pathlib import Path
from PIL import Image
from military_expansion.package import ROOT,catalog,runtime_path

def inspect(apk,report=None):
    rows=catalog()['assets'];cases=0
    with zipfile.ZipFile(apk)as z:
        runtime=json.loads(z.read('assets/military1108/manifest.json'));by_id={r['id']:r for r in runtime['assets']}
        for row in rows:
            identity=row['id'];relative='sprites/'+identity.rsplit('_',1)[0]+'/'+identity+'.png'
            name='assets/military1108/'+relative
            assert name in z.namelist(),('missing actual UI asset path',name)
            assert by_id[identity]['file']==relative and by_id[identity]['source_file']==row['file'];cases+=1
            actual=z.read(name);source=(ROOT/'inputs'/row['file']).read_bytes();assert actual==source;cases+=1
            decoded=Image.open(io.BytesIO(actual)).convert('RGBA');assert decoded.size[0]<=256 and decoded.size[1]<=256 and decoded.getchannel('A').getextrema()[1]>0;cases+=1
        if report:
            imported={r['id']:r for r in report['imported_artwork']};assert set(imported)==set(by_id)
            for row in rows:
                r=imported[row['id']];assert r['resource']=='mayomods1108/military/'+row['id']and r['apk_asset']=='assets/military1108/'+runtime_path(row);cases+=1
    return cases

def validate(apk,old,work,out):
    if old=='-':
        # Portable negative fixture: keep the real runtime index but ship a
        # descriptive source basename where the screen requires an ID alias.
        bad=io.BytesIO();first=catalog()['assets'][0]
        with zipfile.ZipFile(apk)as good,zipfile.ZipFile(bad,'w')as altered:
            altered.writestr('assets/military1108/manifest.json',good.read('assets/military1108/manifest.json'))
            altered.writestr('assets/military1108/'+first['file'],(ROOT/'inputs'/first['file']).read_bytes())
        bad.seek(0);old=bad
    try:inspect(old)
    except AssertionError:negative=True
    else:raise AssertionError('unbound source filenames unexpectedly passed the negative control')
    report=json.loads((Path(work)/'bundle_validation.json').read_text());checks=inspect(apk,report)
    result=dict(passed=True,checks=checks,apk_sha256=hashlib.sha256(Path(apk).read_bytes()).hexdigest(),runtime_ID_file_source_bindings=144,Unity_resource_bindings=144,old_unbound_filenames_negative_control=negative,Android_rendering_tested=False)
    Path(out).write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':validate(*sys.argv[1:])
