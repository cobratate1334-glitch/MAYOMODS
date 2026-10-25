"""Apply saved appearance traits to the current hero's native face components."""
import json
from pathlib import Path
from native_hooks import h
from patch_native42 import body
BENEFITS={1:'Smarts starts at least 95; extra learning as you age.',2:'Athleticism starts at least 85; discipline at least 70.',3:'Smarts at least 75; music aptitude at least 80.',4:'Willpower at least 80; health at least 85.',5:'Generosity at least 80; loyalty and charisma at least 75.',6:'Smarts at least 80; discipline at least 75.',7:'Willpower at least 90; discipline at least 85.'}
def hooks(b):
 catalog=json.loads((Path(__file__).parent/'portrait42_catalog.json').read_text())
 # Resolve styles by their game IDs, not unstable ArrayList positions.
 # Store the valid style on one component without synchronizing unrelated
 # skin/eye layers; custom marks must preserve the player's original skin.
 s='str xzr,[sp]\ncbz x0,finish\nmov x27,x0\nmov w25,w1\nmov x26,x2\nbl 0x2f34138\ncbz x0,finish\nmov x28,x0\nmov x0,x27\nmov x1,xzr\nbl 0x2f3cd90\nmov w24,w0\nmov x0,x27\nmov x1,xzr\nbl 0x2f40a9c\nmov w3,w0\nmov x0,x28\nmov w1,w24\nmov w2,w25\nmov x4,x26\nmov x5,xzr\nbl 0x2f3bf74\ncmp w0,#0\nb.lt finish\nmov w24,w0\nmov x0,x27\nmov w1,w25\nmov x2,xzr\nbl 0x2f3b1d8\ncbz x0,finish\nstr w24,[x0,#0x14]\nmov w9,#1\nstr x9,[sp]\nb finish'
 style=b.routine('v42_set_portrait_style_by_id',s)
 s='cbz x0,finish\nmov x27,x0\n'+h.load_game()+'\nldr x26,[x8,#0x28]\ncbz x26,finish\nldr x8,[x26,#0x80]\ncbz x8,finish\nldr x8,[x8,#0x30]\ncmp x8,x27\nb.ne finish\n'+b.ctx('life_v18')+b.get('RareAppearance21','w25')+'cbz w25,finish\ncmp w25,#7\nb.hi finish\nmov x0,x27\nmov x1,xzr\nbl 0x2f3cd90\nmov w26,w0\ncmp w26,#5\nb.hi finish\nmov x0,x27\nmov x1,xzr\nbl 0x2f40a9c\nmov w28,w0\ncmp w28,#1\nb.hi finish\nmov x0,x27\nmov x1,xzr\nbl 0x2f3f3c4\nmov w24,w0\ncmp w24,#2\nb.ls mood42\nmov w24,#0\nmood42:\n'
 for n,item in enumerate(catalog):
  s+=f'cmp w25,#{item["trait"]}\nb.ne portrait_next42_{n}\ncmp w26,#{item["stage"]}\nb.ne portrait_next42_{n}\ncmp w28,#{item["gender"]}\nb.ne portrait_next42_{n}\n'
  if item['mood']>=0:s+=f'cmp w24,#{item["mood"]}\nb.ne portrait_next42_{n}\n'
  s+=b.string(item['id'])+f'mov x2,x0\nmov x0,x27\nmov w1,#{item["feature"]}\nbl {style:#x}\ncbz w0,finish\n'+b.string('FFFFFF')+f'mov x1,x0\nmov x0,x27\nmov w2,#{item["feature"]}\nmov x3,xzr\nbl 0x2f3e068\nb finish\nportrait_next42_{n}:\n'
 s+='cmp w25,#4\nb.ne curly42\n'
 for feature,color in [(3,'FFF0E3'),(8,'FFF5DF'),(5,'E9DFC9'),(6,'E9DFC9'),(1,'A8C9DC')]:
  s+=b.string(color)+f'mov x1,x0\nmov x0,x27\nmov w2,#{feature}\nmov x3,xzr\nbl 0x2f3e068\n'
 s+='b finish\ncurly42:\ncmp w25,#7\nb.ne finish\nldr x8,[x27,#0x20]\ncbz x8,finish\nmov w9,#1\nstr w9,[x8,#0x20]\nb finish'
 apply=b.routine('v42_apply_current_hero_appearance',s)
 b.install('v42_native_portrait_render_traits',0x2f4284c,f'bl {apply:#x}\nb finish')
 # This is after the existing birth hook has copied the chosen genetics into
 # the new life. Boost once at this creation point, never every profile view.
 s=b.ctx('life_v18')+b.get('InheritedTrait21','w25')+h.load_game()+'\nldr x27,[x8,#0x28]\ncbz x27,finish\n'
 boosts={2:[(0x98,70)],3:[(0xd0,80)],4:[(0x8c,85)],5:[(0xc4,75),(0xcc,75)],6:[(0x98,75)],7:[(0x98,85)]}
 for trait,attrs in boosts.items():
  s+=f'cmp w25,#{trait}\nb.ne boost42_{trait}\n'
  for offset,value in attrs:s+=f'mov w9,#{value}\nscvtf s0,w9\nldr s1,[x27,#{offset}]\nfmax s0,s0,s1\nstr s0,[x27,#{offset}]\n'
  s+=f'boost42_{trait}:\n'
 s+='ldr x26,[x27,#0x80]\ncbz x26,finish\nmov x0,x26\nmov x1,xzr\nbl 0x2c9dfa4\nldr x27,[x26,#0x30]\ncbz x27,finish\nmov x0,x27\n'+f'bl {apply:#x}\n'+b.get('RareAppearance21','w25')+'cmp w25,#7\nb.ne render_birth42\nmov x0,x27\nmov x1,xzr\nbl 0x2f3efbc\nrender_birth42:\nmov x0,x27\nmov w1,#1\nmov x2,xzr\nbl 0x2f4284c\nmov x0,x26\nmov x1,xzr\nbl 0x2c9dfa4\nstr x0,[x26,#0x28]\nb finish'
 b.install('v42_birth_genetics_and_portrait',0x2e06bc0,s)
 # Explain effects in the native profile table rather than inventing an IQ
 # field that the stock game does not expose.
 from native_ui21 import table_value
 s='mov x19,x28\ncbz x19,finish\n'+b.ctx('life_v18')+b.get('InheritedTrait21','w24')
 for trait,description in BENEFITS.items():s+=f'cmp w24,#{trait}\nb.ne benefit42_{trait}\n'+b.string(description)+f'mov x22,x0\nb benefit_ready42\nbenefit42_{trait}:\n'
 s+=b.string('No added inherited stat bonus.')+'mov x22,x0\nbenefit_ready42:\n'+table_value(b,'x19','Genetic effects:')+'b finish'
 journal=next(r for r in b.hooks if r['name']=='v42_living_journal_profile_button')
 b.install('v42_trait_profile_effects',journal['stub'],s)
