from native_hooks import h
from basketball20 import ATTRIBUTES,BUILDS,BADGES

def refresh(b):
 s='mov w26,#0\n'
 for k,_ in ATTRIBUTES:s+=b.get(k+'20','w24',45)+'add w26,w26,w24\n'
 s+='mov w9,#10\nsdiv w26,w26,w9\n'+b.put('Overall20','w26')
 for k,label in BADGES:
  s+=b.get(k+'20','w24',45)
  for i,(rating,tier)in enumerate([(90,'Elite'),(80,'Gold'),(70,'Silver'),(60,'Bronze')]):
   s+=f'cmp w24,#{rating}\nb.lt badge_next20_{k}_{i}\n'+b.text(k+'Badge20',tier+' '+label)+f'b badge_done20_{k}\nbadge_next20_{k}_{i}:\n'
  s+=b.text(k+'Badge20','Developing')+f'badge_done20_{k}:\n'
 return s

def handlers(b):
 gate=f'mov w0,#13\nbl {b.eligibility:#x}\ncbz w0,basket_ineligible20\n'
 select=b.set('BuildError20',0)+gate+b.get('BuildChosen20')+'cbnz w24,basket_locked20\n'
 for i,(label,vals)in enumerate(BUILDS,1):
  select+=f'cmp w20,#{i}\nb.ne basket_next20_{i}\n'
  for (k,_),v in zip(ATTRIBUTES,vals):select+=b.set(k+'20',v)
  select+=b.text('Archetype20',label)+b.set('BuildChosen20',1)+'b finish\n'+f'basket_next20_{i}:\n'
 select+='b finish\nbasket_locked20:\n'+b.set('BuildError20',1)+'b finish\nbasket_ineligible20:\n'+b.set('BuildError20',2)+'b finish'
 train=b.set('BuildError20',0)+gate+b.ctx('life_v18')+b.get('Hospital')+'cbnz w24,basket_hospital20\n'+b.ctx('seasons_v18')+b.get('Training')+'cmp w24,#6\nb.ge basket_limit20\ncmp w20,#1\nb.lt finish\ncmp w20,#10\nb.gt finish\n'+b.inc('Training')+b.inc('Skill')
 for i,(k,_)in enumerate(ATTRIBUTES,1):train+=f'cmp w20,#{i}\nb.ne train_next20_{i}\n'+b.get(k+'20','w24',45)+'add w24,w24,#3\nmov w9,#95\ncmp w24,w9\ncsel w24,w24,w9,lt\n'+b.put(k+'20')+'b finish\n'+f'train_next20_{i}:\n'
 train+='b finish\nbasket_ineligible20:\n'+b.set('BuildError20',2)+'b finish\nbasket_limit20:\n'+b.set('BuildError20',3)+'b finish\nbasket_hospital20:\n'+b.ctx('seasons_v18')+b.set('BuildError20',4)+'b finish'
 takeover=gate+b.get('TakeoverActive20')+'cbnz w24,finish\n'+b.get('TakeoverCharge20')+'cmp w24,#100\nb.lt finish\n'+b.set('TakeoverCharge20',0)+b.set('TakeoverActive20',1)+'b finish\nbasket_ineligible20:\nb finish'
 return [('NativeBuild20','seasons_v18','basket_choose20',select.replace('basket_ineligible20','build_ineligible20')),('NativeBasketTrain20','seasons_v18','basket_train20',train),('NativeBasketRefresh20','seasons_v18','basket_refresh20',refresh(b)+'b finish'),('NativeTakeover20','seasons_v18','basket_takeover20',takeover.replace('basket_ineligible20','takeover_ineligible20'))]
