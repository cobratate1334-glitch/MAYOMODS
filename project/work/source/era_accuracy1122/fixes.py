"""Fix the missed native Golden Resume path and original era/appearance boundaries."""
from native_hooks import h
from native_v42.patch_native42 import ref,ref_init
from native_v45.patch_native45 import hash_dispatch,imm
from native_v45.catalog45 import fnv
from era_accuracy1122.catalog import STARTS,ENDS,JOBS,career_window,PART_STARTS,part_window,ROOT_WINDOWS,ROOT_ENDS,ROOT_TITLES,SPECIAL_YEAR

def named_minimum(b,name,values,default=1800):
 rows=sorted((fnv(key),key)for key in values);assert len({v for v,_ in rows})==len(rows)
 prefix=hash_dispatch([],default).rsplit('b finish',1)[0]
 def tree(rows):
  if not rows:return 'b finish\n'
  mid=len(rows)//2;hashed,key=rows[mid];tag=name+'_'+str(hashed)
  return imm('w14',hashed)+f'cmp w11,w14\nb.lo {tag}_left\nb.hi {tag}_right\n'+h.compare_key(key,tag+'_found','finish')+f'\n{tag}_found:\nmov w9,#{values[key]}\nstr x9,[sp]\nb finish\n{tag}_left:\n'+tree(rows[:mid])+f'{tag}_right:\n'+tree(rows[mid+1:])
 return b.routine(name,'mov x8,x0\n'+prefix+tree(rows))

def hooks(b):
 year=b.old['v45_current_year']['stub']
 # Parents are generated before the old Game.Life is replaced. Scope the
 # actual synchronous creation, never a preview. StartLife closes this scope;
 # the next Unity frame clears an abandoned scope after a managed exception.
 st=b.state
 for name,site in [('random',0x2e06574),('custom',0x2e069a4)]:
  b.install('era1122_birth_scope_'+name,site,f'adr x8,{st+16:#x}\nmov w9,#1\nstr w9,[x8]\nb finish')
 b.install('era1122_birth_scope_end',0x2e06908,f'adr x8,{st+16:#x}\nstr wzr,[x8]\nb finish')
 r=b.resolved('web_unity_thread_command_pump');s=r['source'];head=h.save()+'\n';assert s.startswith(head)
 b.redirect(r['name'],head+f'adr x8,{st+16:#x}\nstr wzr,[x8]\n'+s[len(head):])
 # Before the new birth has installed era44.BirthYear, native parents/NPCs
 # are already being created. Use the selected year ONLY for a newborn with
 # a missing birth year. Existing saved lives always retain their own year.
 r=b.resolved('v45_current_year');s=r['source'];needle='cmp w0,#1\nb.lt finish\nadd w0,w0,w23'
 assert s.count(needle)==1
 replacement=f'cmp w0,#1\nb.ge calendar_has_birth1122\ncbnz w23,finish\nadr x8,{b.states["era44"]["va"]:#x}\nldr w0,[x8]\ncmp w0,#1800\nb.lt finish\ncmp w0,#3999\nb.gt finish\ncalendar_has_birth1122:\nadd w0,w0,w23'
 s=s.replace(needle,replacement,1)
 birth=f'adr x8,{st+16:#x}\nldr w9,[x8]\ncbz w9,saved_calendar1122\nadr x8,{b.states["era44"]["va"]:#x}\nldr w9,[x8]\ncmp w9,#1800\nb.lt saved_calendar1122\ncmp w9,#3999\nb.gt saved_calendar1122\nstr x9,[sp]\nb finish\nsaved_calendar1122:\n'
 assert s.startswith(head);b.redirect(r['name'],head+birth+s[len(head):])
 # Extend the dates and replace all earlier callers through one stable stub.
 minimum=named_minimum(b,'era1122_career_minimum',STARTS)
 maximum=named_minimum(b,'era1122_career_maximum',ENDS,3999)
 s='str xzr,[sp]\ncbz x0,finish\nmov x27,x0\nldr x0,[x27,#0x10]\n'+f'bl {minimum:#x}\nmov w25,w0\nldr x0,[x27,#0x10]\nbl {maximum:#x}\nmov w26,w0\n'
 for title,lo,hi,*_ in JOBS:
  s+='ldr x8,[x27,#0x10]\n'+h.compare_key(title,'period_'+str(lo)+'_'+str(hi)+'_'+str(len(s)),'next_'+str(len(s)))+f'\nperiod_{lo}_{hi}_{len(s)}:\nmov w25,#{lo}\nmov w26,#{hi}\nb career_bounds1122\nnext_{len(s)}:\n'
 s+=f'career_bounds1122:\nbl {year:#x}\ncmp w0,w25\nb.lt finish\ncmp w0,w26\nb.gt finish\n'
 # Preserve the audited actual-country rule for Bounty Hunter.
 s+='ldr x8,[x27,#0x10]\n'+h.compare_key('Bounty Hunter','bounty_country1122','career_ok1122')+'\nbounty_country1122:\n'+h.load_game()+'\nldr x0,[x8,#0x28]\ncbz x0,finish\nmov x1,xzr\nbl 0x2c38288\ncbz x0,finish\nmov x1,xzr\nbl 0x2a27280\ncbz x0,finish\nldr x8,[x0,#0x10]\n'+h.compare_key('United States','career_ok1122','bounty_alias1122')+'\nbounty_alias1122:\n'+h.compare_key('United States of America','career_ok1122','finish')+'\ncareer_ok1122:\nmov w9,#1\nstr x9,[sp]\nb finish'
 allowed=b.routine('era1122_career_allowed',s)
 r=b.old['era1121_career_allowed'];b.redirect(r['name'],f'b {allowed:#x}')
 job=b.routine('era1122_job_allowed','str xzr,[sp]\ncbz x0,finish\nmov x1,xzr\nbl 0x2b1e1f4\n'+f'bl {allowed:#x}\nstr x0,[sp]\nb finish')
 # Golden Resume has TWO independently built lists. Neither went through
 # the previous six pool gates. Gate actual SimJob rows before allocating
 # their application Scenario; cached jobs are rechecked too.
 for name,site,reg,skip in [('golden_qualified',0x312cc90,'x21',0x312cf24),('golden_other',0x312d168,'x21',0x312d3fc),('ordinary',0x312d9ec,'x20',0x312dc84)]:
  b.install('era1122_visible_jobs_'+name,site,f'mov x0,{reg}\nbl {job:#x}\ncbz w0,return_custom\nb finish',custom_resume=skip)
 # A stale apply/event cannot create a future career either.
 b.install('era1122_start_job_guard',0x2a7e098,f'mov x0,x1\nbl {job:#x}\ncbnz w0,finish\nstr xzr,[sp]\nb return_custom',ret=True)
 r=b.resolved('era1121_refresh_existing_job_offers_once');s=r['source'];assert 'JobCatalogRevision1121'in b.strings
 va=b.strings['JobCatalogRevision1121'];needle=f'adrp x0, {va&~4095:#x}\nadd x0, x0, #{va&4095}\nbl 0x223e8cc'
 assert s.count(needle)==2;s=s.replace(needle,b.string('JobCatalogRevision1122').rstrip()).replace('#1121','#1122');b.redirect(r['name'],s)
 # The new final UI gates work on all upgraded same-age Golden Resume caches;
 # no current employee, parent job, owned asset or salary contract is deleted.
 partmin=named_minimum(b,'era1122_part_time_minimum',PART_STARTS)
 part=b.routine('era1122_part_time_allowed','str xzr,[sp]\ncbz x0,finish\nldr x0,[x0,#0x10]\n'+f'bl {partmin:#x}\nmov w25,w0\nbl {year:#x}\ncmp w0,w25\ncset w9,ge\nstr x9,[sp]\nb finish')
 partjob=b.routine('era1122_part_time_job_allowed','str xzr,[sp]\ncbz x0,finish\nmov x1,xzr\nbl 0x2b2e214\n'+f'bl {part:#x}\nstr x0,[sp]\nb finish')
 b.install('era1122_visible_part_time_jobs',0x312e474,f'mov x0,x21\nbl {partjob:#x}\ncbz w0,return_custom\nb finish',custom_resume=0x312e568)
 b.install('era1122_start_part_time_guard',0x2a7efb0,f'mov x0,x1\nbl {partjob:#x}\ncbnz w0,finish\nstr xzr,[sp]\nb return_custom',ret=True)
 # Final fresh-offer float after the native country's cost-of-living work.
 # Fractional historical hourly rates stay floats; getters and current owned
 # part-time contracts are not multiplied again when a menu is reopened.
 factor=b.old['era1121_nominal_pay_factor']['stub']
 scale=b.routine('era1122_scale_fresh_part_time_rate',f'bl {factor:#x}\nscvtf s1,w0\nmov w9,#1000\nscvtf s2,w9\nfdiv s1,s1,s2\nfmul s0,s0,s1\nstr s0,[sp,#256]\nb finish')
 b.install('era1122_part_time_offer_pay',0x2a2f2d0,f'bl {scale:#x}\nstr s0,[sp,#256]\nb finish')
 empty=b.routine('era1122_empty_item_array',ref_init(0x5c24320)+ref(0x5c24320)+'bl 0x2237158\ncbz x0,finish\nmov x25,x0\nmov x1,xzr\nbl 0x4edba28\nstr x25,[sp]\nb finish')
 for name,site in [('special',0x312e768),('producer_special',0x335a8ac),('freelance',0x312c47c)]:
  b.install('era1122_modern_'+name,site,f'bl {year:#x}\ncmp w0,#{SPECIAL_YEAR}\nb.ge finish\nbl {empty:#x}\nstr x0,[sp]\nb return_custom',ret=True)
 for name,site,floor in [('special_start',0x2a7e894,SPECIAL_YEAR),('freelance_accept',0x385cc44,SPECIAL_YEAR),('social_signup',0x2c6f83c,2010)]:
  b.install('era1122_guard_'+name,site,f'bl {year:#x}\ncmp w0,#{floor}\nb.ge finish\nstr xzr,[sp]\nb return_custom',ret=True)
 install_list_rules(b,year)
 r=b.resolved('menu_valid_list_definition_resource');s=r['source'];head=h.save()+'\n';assert s.startswith(head)
 check='cbz x0,previous_town1122\nmov x8,x0\n'+h.compare_key('genesis_era_town1122','valid_town1122','previous_town1122')+'\nvalid_town1122:\nmov w9,#1\nstr x9,[sp]\nb finish\nprevious_town1122:\n'
 b.redirect(r['name'],head+check+s[len(head):])
 from era_accuracy1122.portraits import install
 install(b,year)
 from era_accuracy1122.visuals import install
 install(b,year)

def install_list_rules(b,year):
 """Filter UI row copies through actual ArrayList APIs, never saved inventories."""
 symbols=b.e.get_section_by_name('.dynsym');sym=lambda n:symbols.get_symbol_by_name(n)[0]['st_value']
 floor=named_minimum(b,'era1122_menu_item_minimum',ROOT_WINDOWS)
 ceiling=named_minimum(b,'era1122_menu_item_maximum',ROOT_ENDS,3999)
 # Resolve the actual collection's RemoveAt. This avoids another guessed
 # vtable slot; System.Collections and generic collection layouts differ.
 remove=b.routine('era1122_remove_actual_list_row','str xzr,[sp]\ncbz x0,finish\nmov x25,x0\nmov w26,w1\n'+f'bl {sym("il2cpp_object_get_class"):#x}\ncbz x0,finish\nadr x1,{b.literal("RemoveAt"):#x}\nmov w2,#1\nbl {sym("il2cpp_class_get_method_from_name"):#x}\ncbz x0,finish\nsub sp,sp,#32\nstr w26,[sp,#8]\nadd x9,sp,#8\nstr x9,[sp]\nstr xzr,[sp,#16]\nmov x1,x25\nmov x2,sp\nadd x3,sp,#16\nbl {sym("il2cpp_runtime_invoke"):#x}\nldr x9,[sp,#16]\nadd sp,sp,#32\ncbnz x9,finish\nmov w9,#1\nstr x9,[sp]\nb finish')
 s='cbz x1,finish\ncbz x2,finish\nmov x27,x2\nmov w26,#0\nmov x8,x1\n'
 for i,title in enumerate(ROOT_TITLES):s+=h.compare_key(title,'filter_special_scope1122'if title in ['SPECIAL CAREERS','Special Careers']else'filter_rows1122','scope_next_'+str(i))+'\nscope_next_'+str(i)+':\n'
 s+='b finish\nfilter_special_scope1122:\nmov w26,#2000\nfilter_rows1122:\n'+f'bl {year:#x}\nmov w28,w0\nldr w22,[x27,#0x18]\ncmp w22,#256\nb.hi finish\ncbz w22,finish\n'
 s+='filter_row_loop1122:\nsubs w22,w22,#1\nb.mi finish\nldr x8,[x27,#0x10]\ncbz x8,finish\nldr x9,[x8,#0x18]\ncmp x9,x22\nb.ls finish\ncmp w28,w26\nb.lt remove_row1122\nadd x8,x8,#0x20\nldr x0,[x8,w22,uxtw #3]\ncbz x0,filter_row_loop1122\nldr x23,[x0,#0x10]\nmov x0,x23\n'+f'bl {floor:#x}\ncmp w28,w0\nb.lt remove_row1122\nmov x0,x23\nbl {ceiling:#x}\ncmp w28,w0\nb.le filter_row_loop1122\nremove_row1122:\nmov x0,x27\nmov w1,w22\nbl {remove:#x}\ncbz w0,finish\nb filter_row_loop1122'
 filtering=b.routine('era1122_filter_native_menu_rows',s)
 b.install('era1122_filter_original_list_constructor',0x33aaa80,f'bl {filtering:#x}\nb finish')
 # Parsed Genesis lists use the default constructor. At this audited return
 # boundary x0 is the actual List data, before its visual rows are created.
 # Keep all 1113 ownership/transition work after the pure row filtering.
 r=b.resolved('menu_bind_actual_built_UIList');s=r['source'];head=h.save()+'\n';assert s.startswith(head)
 prefix=f'cbz x0,finish\nldr x1,[x0,#0x10]\nldr x2,[x0,#0x20]\nbl {filtering:#x}\nldr x0,[sp]\n'
 b.redirect(r['name'],head+prefix+s[len(head):])
