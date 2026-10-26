"""Prepare data for separate native annual queues, with no UI during simulation."""
from native_hooks import h
from connected_life.history import EVENTS,PERIODS
from connected_life.cohorts import DRAFTS,NOTES

def hooks(b):
 s=f'bl {b.connected_service_sync:#x}\nbl {b.connected_roster:#x}\n'+b.ctx('life_rework')+b.get('NewsAge1110','w25')+'cmp w25,w23\nb.eq finish\n'+b.put('NewsAge1110','w23')+b.set('NewsFlag1110',0)+b.set('DraftFlag1110',0)+b.set('SchoolFlag1110',0)+b.set('SchoolStory1110',0)+b.set('PrisonStory1110',0)+b.set('EasterStory1110',0)+b.get('Year','w26')
 for year,(title,body,image)in sorted(EVENTS.items()):
  s+=f'cmp w26,#{year}\nb.ne chronicle_next_{year}\n'+b.text('NewsTitle1110',title)+b.text('NewsBody1110',body)+b.text('NewsImage1110','native1110/photos/'+image)+b.set('NewsFlag1110',1)+b.string(title)+f'bl {b.journal55:#x}\nb chronicle_draft\nchronicle_next_{year}:\n'
 for n,(lo,hi,title,body,image)in enumerate(PERIODS):
  s+=f'cmp w26,#{lo}\nb.lt period_next_{n}\ncmp w26,#{hi}\nb.gt period_next_{n}\n'+b.text('NewsTitle1110',title)+b.text('NewsBody1110',body)+b.text('NewsImage1110','native1110/photos/'+image)+b.set('NewsFlag1110',1)+b.string(title)+f'bl {b.journal55:#x}\nb chronicle_draft\nperiod_next_{n}:\n'
 s+='chronicle_draft:\n'+b.get('NativeInPrison1105')+'cbnz w24,chronicle_school\n'+b.get('NativeMilitary')+'cbnz w24,chronicle_school\n'+b.get('DraftNoticeAge1110','w25')+'sub w9,w23,w25\ncmp w9,#3\nb.lt chronicle_school\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,chronicle_school\nldr w9,[x8,#0xf8]\ncbnz w9,chronicle_school\n'+b.string('Country')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\ncbz x0,chronicle_school\nmov x27,x0\n'
 s+='mov x8,x27\n'+h.compare_key('United Kingdom','draft_uk_city1110','draft_city_ready1110')+'\ndraft_uk_city1110:\n'+h.load_game()+'\nldr x0,[x8,#0x28]\nmov x1,xzr\nbl 0x2c38288\ncbz x0,draft_city_ready1110\nmov x1,xzr\nbl 0x2a27240\ncbz x0,draft_city_ready1110\nmov x8,x0\n'+h.compare_key('Belfast','chronicle_school','draft_uk_not_belfast1110')+'\ndraft_uk_not_belfast1110:\n'+h.compare_key('Dublin','chronicle_school','draft_city_ready1110')+'\ndraft_city_ready1110:\n'
 for n,(country,lo,hi,amin,amax)in enumerate(DRAFTS+[("United States of America",lo,hi,amin,amax)for c,lo,hi,amin,amax in DRAFTS if c=="United States"]):
  s+=f'cmp w26,#{lo}\nb.lt cohort_next_{n}\ncmp w26,#{hi}\nb.gt cohort_next_{n}\ncmp w23,#{amin}\nb.lt cohort_next_{n}\ncmp w23,#{amax}\nb.gt cohort_next_{n}\nmov x8,x27\n'+h.compare_key(country,'cohort_yes_'+str(n),'cohort_next_'+str(n))+f'\ncohort_yes_{n}:\n'+b.text('DraftText1110',country+' is reviewing its service cohort. '+NOTES['United States'if country=='United States of America'else country]+'<br><br>Open Occupation → Military → Draft & service. Register or volunteer, attend a medical check, then accept induction. Training comes before deployment.')+b.set('DraftFlag1110',1)+b.put('DraftNoticeAge1110','w23')+'b chronicle_school\n'+f'cohort_next_{n}:\n'
 s+='chronicle_school:\n'+b.get('SchoolDiscipline1110')+'cbz w24,school_decay_done1110\nsub w24,w24,#1\n'+b.put('SchoolDiscipline1110')+'school_decay_done1110:\n'+b.get('Roll')+'tbnz w24,#0,chronicle_prison\n'+b.get('SchoolEligible')+'cbz w24,chronicle_prison\ncmp w23,#5\nb.lt chronicle_prison\ncmp w23,#19\nb.gt chronicle_prison\n'+b.get('Roll','w25')+'add w25,w25,w23\nmov w9,#10\nudiv w10,w25,w9\nmsub w24,w10,w9,w25\nadd w24,w24,#1\n'+b.put('SchoolStory1110')+b.set('SchoolFlag1110',1)+b.set('SchoolEvent1105',0)+'chronicle_prison:\n'+b.get('NativeInPrison1105')+'cbz w24,chronicle_easter\n'+b.get('Roll','w25')+'add w25,w25,w23\nand w24,w25,#3\nadd w24,w24,#1\n'+b.put('PrisonStory1110')+'chronicle_easter:\n'+b.get('Roll','w25')+'cmp w25,#5\nb.gt finish\n'
 for n in range(1,7):
  s+=f'cmp w25,#{n-1}\nb.ne egg_next_{n}\n'+b.get('EasterSeen1110_'+str(n))+f'cbnz w24,egg_next_{n}\n'
  if n==1:s+='cmp w26,#1914\nb.ne finish\n'+b.get('NativeMilitary')+'cbz w24,finish\n'
  elif n==2:s+=b.get('NativeMilitary')+'cbz w24,finish\n'
  elif n==3:s+='cmp w26,#1999\nb.lt finish\ncmp w26,#2000\nb.gt finish\n'
  elif n==4:s+=b.get('SchoolEligible')+'cbz w24,finish\ncmp w23,#10\nb.lt finish\n'
  elif n==5:s+='cmp w23,#18\nb.lt finish\n'
  elif n==6:s+=b.get('NativeInPrison1105')+'cbz w24,finish\n'
  s+=b.set('EasterStory1110',n)+f'b finish\negg_next_{n}:\n'
 s+='b finish'
 fn=b.routine('connected_prepare_native_annual_queues',s)
 # Append at the old routine's common epilogue, including its early exits.
 old=b.resolved('followup_prepare_native_annual_notices');source=old['source'];mark='\nfinish:\n';assert source.count(mark)==1
 b.redirect(old['name'],source.replace(mark,mark+f'bl {fn:#x}\n',1))
 # Original engine enumerates independent AgeUpActionList containers. Each
 # queue gets its context before enumeration, so school cannot crowd out news.
 activate=''
 for owner in ['chronicle1110','callup1110','school1110','service1110','prison1110','easter1110']:
  activate+=b.ctx(owner)
 activate+='b finish'
 b.chain('connected_activate_annual_containers','followup_activate_before_native_annual_queue',activate)
