"""Tornado damage applies to a local owned home; videos have narrow scopes."""
from native_hooks import h

def routines(b):
 s=b.ctx('world20')+b.set('HouseDamaged21',0)+b.get('Event')+'cmp w24,#1\nb.ne finish\n'+f'bl {b.geography:#x}\n'+b.get('Tornado')+'cbz w24,finish\n'+b.rng(100)+'cmp w24,#25\nb.ge finish\n'+h.load_game()+'\nldr x27,[x8,#0x20]\nldr x0,[x8,#0x28]\ncbz x0,finish\nmov x1,xzr\nbl 0x2c38288\ncbz x0,finish\nmov x25,x0\nldr x8,[x27,#0x158]\ncbz x8,finish\nldr w28,[x8,#0x18]\ncbz w28,finish\nldr x26,[x8,#0x10]\ncbz x26,finish\nadd x26,x26,#0x20\nhome_loop21:\nldr x27,[x26],#8\ncbz x27,home_next21\nldr s0,[x27,#0x20]\nfcmp s0,#0.0\nb.le home_next21\nldr x23,[x27,#0x28]\ncbz x23,home_next21\nldr x0,[x25,#0x88]\nldr x1,[x23,#0x88]\n'+f'bl {b.streq21:#x}\ncbz w0,home_next21\nldr x0,[x25,#0x90]\nldr x1,[x23,#0x90]\nbl {b.streq21:#x}\ncbz w0,home_next21\nstr wzr,[x27,#0x20]\n'+b.set('HouseDamaged21',1)+h.load_game()+'\nldr x8,[x8,#0x28]\nldr w24,[x8,#0x20]\n'+b.put('HouseDamageAge21')+b.text('LastReport','A tornado destroyed the usable condition of your home. Your household reached shelter; your home needs repairs.')+'b finish\nhome_next21:\nsubs w28,w28,#1\nb.ne home_loop21\nb finish'
 b.house_damage21=b.routine('local_owned_home_tornado_damage21',s)

def handlers(b):
 # Viewing a report plays once per incident, not per score/property change.
 house=b.get('HouseDamaged21')+'cmp w24,#1\nb.ne finish\n'+b.get('HouseDamageAge21','w25',-1)+h.load_game()+'\nldr x8,[x8,#0x28]\nldr w9,[x8,#0x20]\ncmp w25,w9\nb.ne finish\n'+b.set('HouseDamaged21',0)+f'mov w0,#4\nbl {b.ui21:#x}\nb finish'
 storm=h.load_game()+'\nldr x8,[x8,#0x28]\nldr w9,[x8,#0x20]\ncmp w9,#18\nb.lt finish\n'+b.get('Role')+'cmp w24,#1\nb.ne finish\n'+b.get('Tours')+'cbz w24,finish\nmov w0,#3\n'+f'bl {b.ui21:#x}\nb finish'
 reconcile=f'bl {b.reconcile21:#x}\nb finish'
 return [('NativeHouseReplay21','world20','home_replay21',house),('NativeStormReplay21','careers_v18','storm_replay21',storm),('NativeSeasonReconcile21','seasons_v18','season_reconcile21',reconcile)]
