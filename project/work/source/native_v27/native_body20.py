"""Migrate retired mod portrait IDs to original stock layers."""
from native_hooks import h
def migration(b):
 # Only retired v18/v19 IDs migrate to a stock layer. Stock portrait IDs and UI are untouched.
 import json,re
 base=json.load(open('analysis/base_assets.json'))['a16_voltron_componentFilenames'].splitlines()
 mapping={}
 from pathlib import Path
 root=Path(__file__).resolve().parent
 for row in json.load(open(root/'hair_catalog.json'))+json.load(open(root/'genetic_catalog.json')):
  gender='male' if row['gender']==0 else 'female';stage=row['stage'];feature=row.get('feature','hair')
  pattern=rf'a16_faces-{gender}-stage{stage}-'+ ('hair-base' if feature=='hair' else 'iris-base-' if feature=='iris' else 'base-')
  candidates=[v for v in base if v.startswith(pattern)]
  if not candidates and feature=='iris':candidates=[v for v in base if v.startswith(f'a16_faces-{gender}-stage{stage}-eye-iris0-')]
  assert candidates,(feature,stage,gender)
  mapping[row['name'].rsplit('-',1)[1]]=candidates[0].removesuffix('.png').rsplit('-',1)[1]
 code='mov x8,x1\ncbz x8,finish\n'
 for i,(old,new)in enumerate(mapping.items()):code+=h.compare_key(old,'retired_portrait20_'+str(i),'portrait_next20_'+str(i))+'\nportrait_next20_'+str(i)+':\n'
 code+='b finish\n'
 for i,(old,new)in enumerate(mapping.items()):code+='retired_portrait20_'+str(i)+':\n'+b.string(new)+'str x0,[sp,#8]\nb finish\n'
 b.install('v20_retired_portrait_id_migration',0x2f3c738,code)
