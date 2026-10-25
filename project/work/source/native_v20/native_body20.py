"""A separate step before native Custom Life starts; no appearance/editor mutation."""
from native_hooks import h
def pending(b):return b.reserve('new_life_body20',32)

def handlers(b):
 PENDING=pending(b)
 commit=f'adr x28,{PENDING:#x}\nldr x27,[x28]\ncbz x27,finish\n'+b.get('Height','w25',178)+b.get('Weight','w26',72)+b.get('Reach','w24',2)+f'adr x28,{PENDING:#x}\nstr w25,[x28,#12]\nstr w26,[x28,#16]\nstr w24,[x28,#20]\nmov w9,#1\nstr w9,[x28,#8]\nmov x0,x27\nmov x1,xzr\nbl 0x2fa8524\nb finish'
 cancel=f'adr x8,{PENDING:#x}\nstr xzr,[x8]\nstr wzr,[x8,#8]\nb finish'
 return [('NativeBodyCommit20','newlife_body20','body_commit20',commit),('NativeBodyCancel20','newlife_body20','body_cancel20',cancel)]

def hooks(b):
 PENDING=pending(b)
 s=f'cbz x0,finish\nadr x8,{PENDING:#x}\nldr w9,[x8,#8]\ncbnz w9,finish\nmov x27,x0\n'+b.ctx('newlife_body20')+f'adr x8,{PENDING:#x}\nstr x27,[x8]\n'+b.set('Height',178)+b.set('Weight',72)+b.set('Reach',2)+b.string('genesis_v18_newlife_body20')+'mov w1,#1\nmov w2,#1\nmov x3,xzr\nmov x4,xzr\nbl 0x30838cc\nb return_custom'
 b.install('v20_custom_life_body_step',0x2fa8524,s,ret=True)
 s=f'adr x28,{PENDING:#x}\nldr w9,[x28,#8]\ncbz w9,finish\n'+b.ctx('life_v18')
 for offset,key,lo,hi in [(12,'AdultHeight',140,235),(16,'AdultWeight',40,180),(20,'Reach',-10,20)]:
  s+=f'ldr w24,[x28,#{offset}]\nmov w9,#{lo}\ncmp w24,w9\ncsel w24,w24,w9,ge\nmov w9,#{hi}\ncmp w24,w9\ncsel w24,w24,w9,le\n'+b.put(key)
 s+=b.set('BodyVersion20',20)+f'adr x8,{PENDING:#x}\nstr xzr,[x8]\nstr wzr,[x8,#8]\nb finish'
 b.install('v20_apply_new_life_body',0x2e06bbc,s)

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
