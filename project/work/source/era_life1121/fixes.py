"""Audited native Life tracker, catalog selection, pay and bounded transactions."""
from native_hooks import h
from native_v45.patch_native45 import hash_dispatch
from era_life1121.catalog import VEHICLES,JOBS,career_window,PAY,FOODS

def hooks(b):
 # Stock ScenarioSchoolBully reads Game.Life (+20).Tracker (+70). Hero (+28)
 # has no such tracker. The old double had fabricated one on the hero.
 r=b.resolved('repair_original_school_combat_and_minefield');s=r['source'];bad='ldr x8,[x8,#0x28]\ncbz x8,finish\nldr x8,[x8,#0x70]';assert s.count(bad)==1
 assert s.count('cmp w23,#6\nb.lt finish')==1
 b.redirect(r['name'],s.replace(bad,bad.replace('#0x28','#0x20'),1).replace('cmp w23,#6\nb.lt finish','cmp w23,#5\nb.lt finish',1))
 # One new native JSON list; CSV sheets can never become parent UI lists.
 r=b.resolved('menu_valid_list_definition_resource');s=r['source'];head=h.save()+'\n';assert s.startswith(head)
 check='cbz x0,previous_shop1121\nmov x8,x0\n'+h.compare_key('genesis_era_shops1121','valid_shop1121','food_shop1121')+'\nfood_shop1121:\n'+h.compare_key('genesis_era_food1121','valid_shop1121','previous_shop1121')+'\nvalid_shop1121:\nmov w9,#1\nstr x9,[sp]\nb finish\nprevious_shop1121:\n'
 b.redirect(r['name'],head+check+s[len(head):])
 icons=['native1119/1800s/icons/outfits/bounty_hunter_outfit','native1119/1800s/icons/jobs/farmhand','native1119/1800s/icons/jobs/printer','native1119/1800s/icons/outfits/carpenter_outfit','native1119/1800s/icons/outfits/carpenter_outfit','native1119/1800s/icons/outfits/railway_worker_outfit','native1118/1900s/telegraph_machine','native1118/1920s/candlestick_phone','native1118/1940s/valve_radio']
 s='cbz x0,finish\nmov x8,x0\n'
 for i,(job,icon)in enumerate(zip(JOBS,icons)):
  s+=h.compare_key(job[0],f'career_icon1121_{i}',f'career_icon_next1121_{i}')+f'\ncareer_icon1121_{i}:\n'+b.string(icon)+'str x0,[sp]\nb return_custom\n'+f'career_icon_next1121_{i}:\n'
 b.install('era1121_period_job_icons',0x2b824cc,s+'b finish',ret=True)
 year=cached_calendar(b)
 # An upgraded life can have a SAME-AGE market/job cache made by 1120. Rebuild
 # offers once on first access; never rewrite an owned vehicle or occupation.
 r=b.resolved('v45_ensure_place_market');s=r['source'];marker='mov x21,x0\n';assert s.count(marker)==1
 revision=b.get('CatalogRevision1121')+'cmp w24,#1121\nb.eq market_revision_ready1121\n'+b.set('CatalogRevision1121',1121)+'b rebuild45_place\nmarket_revision_ready1121:\n'
 b.redirect(r['name'],s.replace(marker,marker+revision,1))
 s=b.ctx('life_rework')+b.get('JobCatalogRevision1121')+'cmp w24,#1121\nb.eq finish\n'+b.set('JobCatalogRevision1121',1121)+'mov w9,#1\nstr x9,[sp,#8]\nb finish'
 b.install('era1121_refresh_existing_job_offers_once',0x2a2b5c0,s)
 # Keep the original 41 model names for saved garages. Append new make/model
 # identities, and route them through the SAME dealership/garage code.
 old_id=b.resolved('v45_model_id');prefix='str xzr,[sp]\ncbz x0,finish\nmov x27,x0\n'
 s=prefix
 for i,(make,model,*_)in enumerate(VEHICLES,101):
  s+='ldr x8,[x27,#0x10]\ncbz x8,finish\n'+h.compare_key(make,f'make_{i}',f'next_{i}')+f'\nmake_{i}:\nldr x8,[x27,#0x18]\ncbz x8,finish\n'+h.compare_key(model,f'model_{i}',f'next_{i}')+f'\nmodel_{i}:\nmov w9,#{i}\nstr x9,[sp]\nb finish\nnext_{i}:\n'
 s+='ldr x8,[x27,#0x10]\n'+h.compare_key('Mayo','legacy_make1121','previous_models1121')+'\nlegacy_make1121:\nldr x8,[x27,#0x18]\ncbz x8,finish\n'+h.compare_key('1880 Road carriage','legacy_carriage1121','previous_models1121')+'\nlegacy_carriage1121:\nmov w9,#199\nstr x9,[sp]\nb finish\nprevious_models1121:\n'
 # Fall through to the previous complete model dispatcher, preserving every
 # previously saved Mayo identity and its artwork.
 original=old_id['source'];assert original.startswith(h.save()+'\n')
 b.redirect(old_id['name'],h.save()+'\n'+s+original[len(h.save())+1:])
 idva=old_id['stub']
 r=b.resolved('v45_car_allowed');s=r['source'];pos=s.index('period45_model:\n')+len('period45_model:\n');extra=''
 for i,(_,_,lo,hi,*_)in enumerate(VEHICLES,101):extra+=f'cmp w25,#{i}\nb.ne allowed_next1121_{i}\ncmp w26,#{lo}\nb.lt finish\ncmp w26,#{hi}\nb.gt finish\nmov w9,#1\nstr x9,[sp]\nb finish\nallowed_next1121_{i}:\n'
 b.redirect(r['name'],s[:pos]+extra+s[pos:])
 # A later generic make-badge hook masked the older dated car pictures. Put
 # known period models ahead of that hook; keep its normal stock-brand path.
 from native_v45.catalog45 import CARS
 s='str xzr,[sp]\ncbz x0,finish\nmov x1,xzr\nbl 0x2b0cfc4\n'+f'bl {idva:#x}\nmov w25,w0\n'
 artrows=[(c['id'],'mayo45-'+c['art'])for c in CARS]+[(i,v[-1])for i,v in enumerate(VEHICLES,101)]+[(199,VEHICLES[0][-1])]
 for i,art in artrows:s+=f'cmp w25,#{i}\nb.ne emoji_next1121_{i}\n'+b.string(art)+'str x0,[sp]\nb finish\n'+f'emoji_next1121_{i}:\n'
 art=b.routine('era1121_period_vehicle_art',s+'b finish')
 b.install('era1121_restore_period_vehicle_pictures',0x2b86684,f'bl {art:#x}\ncbz x0,finish\nstr x0,[sp]\nb return_custom',ret=True)
 # Empty category pools must return a loaded period record, including luxury
 # and gift requests. Do not send an 1890 life back to a horse carriage.
 s='cbnz w0,finish\n'+f'bl {year:#x}\nmov w25,w0\n'
 for i,(make,model,lo,hi,*_)in reversed(list(enumerate(VEHICLES))):
  s+=f'cmp w25,#{lo}\nb.lt fallback_next1121_{i}\n'+b.string(make)+'mov x26,x0\n'+b.string(model)+f'b fallback_lookup1121\nfallback_next1121_{i}:\n'
 s+='b finish\nfallback_lookup1121:\nmov x1,x0\nmov x0,x26\nmov x2,xzr\nbl 0x2800d7c\nstr x0,[sp]\nb return_custom'
 # Install at the original count check; the ordinary nonempty path still
 # executes its displaced branch and the stock weighted selector.
 b.install('era1121_empty_vehicle_category',0x27ffadc,s,custom_resume=0x27ffb48)
 # Every native pool gets the same date rule BEFORE adding to its weighted
 # list. Lookups of owned jobs are deliberately unchanged.
 allow=career_rules(b,year)
 for name,site,reg,resume in [('all',0x27fbd38,'x8',0x27fbd5c),('random',0x27f964c,'x21',0x27f969c),('company',0x27fae64,'x22',0x27faea8),('appearance',0x27fa990,'x8',0x27fa9b4),('school',0x27f9b48,'x8',0x27f9b6c),('education',0x27fc5e4,'x8',0x27fc608)]:
  b.install('era1121_career_'+name,site,f'mov x0,{reg}\nbl {allow:#x}\ncbz w0,return_custom\nb finish',custom_resume=resume)
 factor=make_factor(b,year)
 # W0 is the fully computed native offer, after country/company/experience.
 # Only the return value changes; repeated views do not mutate saved salaries.
 scale=b.routine('era1121_scale_offer',f'mov w25,w0\nstr x0,[sp]\ncmp w25,#0\nb.le finish\nbl {factor:#x}\numull x9,w25,w0\nmov x10,#1000\nudiv x9,x9,x10\nmov x10,#1\ncmp x9,#1\ncsel x9,x9,x10,ge\nstr x9,[sp]\nb finish')
 b.install('era1121_native_job_offer_pay',0x2b20aac,f'bl {scale:#x}\nstr x0,[sp]\nb finish')
 # Annual preparation has no reason to build the military roster repeatedly
 # in the same age. Manual service snapshot/action paths still call the service sync. New
 # coworkers retain the original construction-time age/rank normalization.
 r=b.resolved('connected_prepare_native_annual_queues');s=r['source'];calls='bl 0x78b2870\nbl 0x78b6570\n';assert calls in s
 s=s.replace(calls,'',1);needle='cmp w25,w23\nb.eq finish\n';assert s.count(needle)==1
 b.redirect(r['name'],s.replace(needle,needle+calls,1))
 from era_life1121.transactions import install
 install(b,year,factor)
 from era_life1121.social import install as social
 social(b,year)

def cached_calendar(b):
 st=b.state
 # Fixed names are rooted once. A Life/GFC pair uses handles, released when
 # identity changes. Read the live BirthYear every time: edits and rewinds
 # cannot be hidden by a stale scalar year cache.
 def intern(name,slot):
  return (f'adr x28,{st+slot:#x}\nldr x0,[x28]\ncbz x0,new_string_{slot}\nbl 0x223e73c\ncbnz x0,string_ready_{slot}\nnew_string_{slot}:\n'+b.string(name)+f'mov x27,x0\nmov w1,#0\nbl 0x223e704\nstr x0,[x28]\nmov x0,x27\nstring_ready_{slot}:\n')
 owner=b.routine('era1121_calendar_owner_string',intern('era44',16)+'str x0,[sp]\nb finish')
 key=b.routine('era1121_calendar_birth_string',intern('BirthYear',24)+'str x0,[sp]\nb finish')
 s='mov w9,#2026\nstr x9,[sp]\n'+h.load_game()+'\nldr x22,[x8,#0x20]\ncbz x22,finish\nldr x23,[x8,#0x28]\ncbz x23,finish\nldr w23,[x23,#0x20]\n'+f'adr x26,{st:#x}\nldr x0,[x26]\ncbz x0,new_life1121\nbl 0x223e73c\ncmp x0,x22\nb.ne new_life1121\nldr w9,[x26,#32]\ncmp w9,w23\nb.ne new_life1121\nldr x0,[x26,#8]\ncbz x0,new_life1121\nbl 0x223e73c\ncbnz x0,calendar_ready1121\nnew_life1121:\n'
 for slot in [0,8]:s+=f'ldr x0,[x26,#{slot}]\ncbz x0,freed1121_{slot}\nbl 0x223e784\nstr xzr,[x26,#{slot}]\nfreed1121_{slot}:\n'
 s+=f'bl {owner:#x}\nmov x1,x0\nmov x0,x22\nmov w2,w23\nmov x3,xzr\nbl 0x32800fc\ncbz x0,finish\nmov x21,x0\nmov w1,#0\nbl 0x223e704\nstr x0,[x26,#8]\nmov x0,x22\nmov w1,#0\nbl 0x223e704\nstr x0,[x26]\nstr w23,[x26,#32]\nmov x0,x21\ncalendar_ready1121:\nmov x21,x0\nbl {key:#x}\nmov x1,x0\nmov x0,x21\nmov w2,#0\nmov x3,xzr\nbl 0x3059ee0\ncmp w0,#1\nb.lt finish\nadd w0,w0,w23\nstr x0,[sp]\nb finish'
 r=b.resolved('v45_current_year');b.redirect(r['name'],h.save()+'\n'+s+'\nfinish:\n'+h.restore()+'\nret');return r['stub']

def make_factor(b,year):
 s=f'bl {year:#x}\nmov w25,w0\n'
 for i,((a,x),(z,y))in enumerate(zip(PAY,PAY[1:])):
  s+=f'cmp w25,#{z}\nb.ge pay_next_{i}\nsub w9,w25,#{a}\nmov w10,#0\ncmp w9,#0\ncsel w9,w9,w10,ge\nmov w10,#{y-x}\nmul w9,w9,w10\nmov w10,#{z-a}\nudiv w9,w9,w10\nadd w9,w9,#{x}\nstr x9,[sp]\nb finish\npay_next_{i}:\n'
 s+='mov w9,#1000\nstr x9,[sp]\nb finish';return b.routine('era1121_nominal_pay_factor',s)

def career_rules(b,year):
 from era_life1121.catalog import STARTS,ENDS
 from native_v45.catalog45 import fnv
 from native_v45.patch_native45 import imm
 names=sorted(set(STARTS)|set(ENDS)|{j[0]for j in JOBS});bounds=sorted({(1800,3999)}|{career_window(n)for n in names});ids={x:i+1 for i,x in enumerate(bounds)}
 # Balanced hash tree: O(log N) comparisons, then full UTF-16 equality.
 prefix=hash_dispatch([],ids[(1800,3999)]).rsplit('b finish',1)[0]
 def tree(rows):
  if not rows:return 'b finish\n'
  mid=len(rows)//2;hashed,name=rows[mid];tag='career_hash_'+str(hashed)
  return imm('w14',hashed)+f'cmp w11,w14\nb.lo {tag}_left\nb.hi {tag}_right\n'+h.compare_key(name,tag+'_found','finish')+f'\n{tag}_found:\nmov w9,#{ids[career_window(name)]}\nstr x9,[sp]\nb finish\n{tag}_left:\n'+tree(rows[:mid])+f'{tag}_right:\n'+tree(rows[mid+1:])
 pairs=sorted((fnv(n),n)for n in names);assert len({n for n,_ in pairs})==len(pairs)
 dispatch=b.routine('era1121_career_window_id','cbz x0,finish\nldr x8,[x0,#0x10]\n'+prefix+tree(pairs))
 s='str xzr,[sp]\ncbz x0,finish\n'+f'bl {dispatch:#x}\nmov w25,w0\nbl {year:#x}\nmov w26,w0\n'
 for bounds_,i in ids.items():
  lo,hi=bounds_;s+=f'cmp w25,#{i}\nb.ne job_next_{i}\ncmp w26,#{lo}\nb.lt finish\ncmp w26,#{hi}\nb.gt finish\n'
  if bounds_==(1800,1899):
   s+=h.load_game()+'\nldr x0,[x8,#0x28]\ncbz x0,finish\nmov x1,xzr\nbl 0x2c38288\ncbz x0,finish\nmov x1,xzr\nbl 0x2a27280\ncbz x0,finish\nldr x8,[x0,#0x10]\ncbz x8,finish\n'+h.compare_key('United States','bounty_country1121','bounty_country_alias1121')+'\nbounty_country_alias1121:\n'+h.compare_key('United States of America','bounty_country1121','finish')+'\nbounty_country1121:\n'
  s+=f'mov w9,#1\nstr x9,[sp]\nb finish\njob_next_{i}:\n'
 return b.routine('era1121_career_allowed',s+'b finish')
