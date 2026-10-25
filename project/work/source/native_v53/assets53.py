"""Rename appearance labels without changing any portrait pixels or save IDs."""
import hashlib,json,sys,zipfile
from pathlib import Path
import UnityPy
ROOT=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest()

def build(base):
 a=json.loads((ROOT.parent/'native_v52/assets.json').read_text())
 for k,v in a.items():
  a[k]=v.replace('Genetics','Genetic appearances').replace('Appearance Studio','Genetic appearances').replace('Appearance studio','Genetic appearances')
 (ROOT/'assets.json').write_text(json.dumps(a,indent=2)+'\n')
 with zipfile.ZipFile(base)as z:old=z.read('assets/bin/Data/datapack.unity3d');data=z.read('assets/bin/Data/data.unity3d')
 env=UnityPy.load(old);original={o.path_id:(o.type.name,o.get_raw_data())for o in env.objects};changed=[]
 for o in env.objects:
  if o.type.name!='TextAsset':continue
  t=o.read()
  if t.m_Name in a and t.m_Script!=a[t.m_Name]:t.m_Script=a[t.m_Name];t.save();changed.append(t.m_Name)
 out=ROOT/'bundles';out.mkdir(exist_ok=True);raw=next(iter(env.files.values())).save(packer='original');(out/'datapack.unity3d').write_bytes(raw);(out/'data.unity3d').write_bytes(data)
 decoded=UnityPy.load(raw);checks=0;seen=set()
 for o in decoded.objects:
  typ,oldraw=original[o.path_id];seen.add(o.path_id)
  if oldraw!=o.get_raw_data():assert typ=='TextAsset'and o.read().m_Name in changed
  if typ=='TextAsset'and o.read().m_Name in a:assert o.read().m_Script==a[o.read().m_Name]
  checks+=1
 assert seen==original.keys()
 r=dict(passed=True,checks=checks,assets=dict(datapack_sha256=sha(raw),data_sha256=sha(data)),changed_text_assets=changed,all_prior_objects_retained=True,all_Sprites_and_Textures_byte_identical=True,no_new_resources=True,physical_phone_tested=False,Unity_rendering_tested=False)
 (ROOT/'content53_validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))

if __name__=='__main__':build(sys.argv[1])
