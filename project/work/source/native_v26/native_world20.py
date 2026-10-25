"""Current native residence, bounded once-per-age warnings, coastal filtering."""
from native_hooks import h
from geography20 import PROFILES,HAZARDS,EVENTS

def routines(b):
 s='str xzr,[sp]\n'+b.ctx('world20')+b.set('Mapped',0)+b.set('US',0)+b.text('Region','Outside mapped US regions')
 for k in HAZARDS:s+=b.set(k,0)
 s+=h.load_game()+'\nldr x0,[x8,#0x28]\ncbz x0,finish\nmov x1,xzr\nbl 0x2c38288\ncbz x0,finish\nmov x26,x0\nldr x25,[x26,#0x88]\ncbz x25,finish\n'+b.textptr('City','x25')+'ldr x22,[x26,#0x90]\ncbz x22,finish\n'+b.textptr('Country','x22')+'mov x8,x22\n'
 for i,name in enumerate(['US','USA','United States','United States of America']):s+=h.compare_key(name,'us_country20','us_country_next20_'+str(i))+'\nus_country_next20_'+str(i)+':\n'
 s+='b finish\nus_country20:\n'+b.set('US',1)+b.text('Region','US city without a mapped coastal hazard profile')+'mov x8,x25\n'
 for i,city in enumerate(PROFILES):s+=h.compare_key(city,'geo_city20_'+str(i),'geo_next20_'+str(i))+'\ngeo_next20_'+str(i)+':\n'
 s+='b finish\n'
 for i,(city,pr)in enumerate(PROFILES.items()):
  s+='geo_city20_'+str(i)+':\n'+b.set('Mapped',1)+b.text('Region',pr['region'])
  for k in HAZARDS:s+=b.set(k,pr[k])
  s+=f'mov w9,#{i+1}\nstr x9,[sp]\nb finish\n'
 b.geography=b.routine('current_residence20',s)
 s=b.ctx('world20')+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldrb w9,[x8,#0x18]\ncbz w9,finish\nldr w28,[x8,#0x20]\n'+b.get('LastAge','w24',-1)+'cmp w24,w28\nb.eq finish\n'+b.put('LastAge','w28')+b.set('Event',0)+b.set('Resolved',0)+f'bl {b.geography:#x}\ncbz w0,finish\n'+b.rng(1000,'w27')+'mov w26,#0\n'
 for i,k in enumerate(HAZARDS,1):s+=b.get(k)+'add w26,w26,w24\ncmp w27,w26\nb.lt warning20_'+str(i)+'\n'
 s+='b finish\n'
 for i,(title,_)in enumerate(EVENTS,1):s+=f'warning20_{i}:\n'+b.set('Event',i)+b.inc('Warnings')+b.text('LastReport',title+' near your home; awaiting your response.')+b.string('genesis_v20_disaster_events')+'mov w1,#1\nmov w2,#1\nmov x3,xzr\nmov x4,xzr\nbl 0x308480c\nb finish\n'
 b.age_warning=b.routine('annual_regional_warning20',s)

def handlers(b):
 sync=f'bl {b.geography:#x}\nb finish'
 resolve=b.get('Event')+'cbz w24,finish\n'+b.get('Resolved')+'cbnz w24,finish\ncmp w20,#1\nb.lt finish\ncmp w20,#3\nb.gt finish\nmov w27,w20\n'+b.set('Resolved',1)+b.get('Preparedness','w26')+'cmp w27,#3\nb.eq ignored_warning20\n'+b.text('LastReport','You followed the local warning and checked on the people close to you. Your household reached safety.')+'mov w25,#-2\ncbnz w26,impact_warning20\nmov w25,#-4\nb impact_warning20\nignored_warning20:\n'+b.text('LastReport','You ignored the local warning. The disruption left you shaken; consider preparing an emergency plan.')+'mov w25,#-8\nimpact_warning20:\n'+h.load_game()+'\nldr x0,[x8,#0x28]\ncbz x0,finish\nmov w1,w25\nmov x2,xzr\nbl 0x2a83910\n'+f'bl {b.house_damage21:#x}\n'+'b finish'
 return [('NativeWorldSync20','world20','world_sync20',sync),('NativeDisasterResolve20','world20','world_resolve20',resolve)]

def hooks(b):
 b.install('v20_residence_disaster_ageup',0x329a6c4,f'bl {b.age_warning:#x}\nb finish')
 # Country-wide landlord events must not assign coastal hazards to inland homes.
 s='cbz x0,finish\nmov x27,x0\n'+b.ctx('world20')+f'bl {b.geography:#x}\n'+b.get('US')+'cbz w24,finish\nldr x8,[x27,#0x10]\ncbz x8,finish\n'
 aliases={'Hurricane':['Hurricane','hurricane','Cyclone','cyclone','Tropical cyclone'],'Tsunami':['Tsunami','tsunami'],'Volcano':['Volcano','volcano','Volcanic eruption','volcanic eruption','Volcanic Eruption']}
 for k,values in aliases.items():
  for i,name in enumerate(values):s+=h.compare_key(name,'filter_'+k+'20','filter_next_'+k+str(i)+'20')+'\nfilter_next_'+k+str(i)+'20:\n'
 s+='b finish\n'
 for k in aliases:s+='filter_'+k+'20:\n'+b.get(k)+'cbnz w24,finish\nstr xzr,[sp]\nb finish\n'
 b.install('v20_native_landlord_coastal_filter',0x27559a4,s)
