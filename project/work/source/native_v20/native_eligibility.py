"""Use current native occupation and joined school teams for every entry check."""
import json
from native_hooks import h,ROOT
# Kind 1 soccer, 2 NBA, 3 NFL, 4 school, 5 college, 6 pro seasons,
# 7 student basketball, 8 current season, 9 Euros, 10 Copa, 11 adult, 12 social.
MARKERS={'v19-soccer':1,'v19-nba':2,'v19-nfl':3,'v19-highschool-basketball':4,'v19-college-basketball':5,'v19-pro-seasons':6,'v19-school-basketball':7,'v19-current-season':8,'v19-euros':9,'v19-copa':10,'v19-adult':11,'v19-social':12,'v20-basketball':13}
def routine(b):
 s='str xzr,[sp]\nmov w28,w0\n'
 s+=h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr w25,[x8,#0x20]\ncmp w28,#11\nb.eq adult19\ncmp w28,#12\nb.eq social19\ncmp w28,#8\nb.eq current_season19\nb occupation19\nadult19:\ncmp w25,#18\nb.lt finish\nb eligible19\nsocial19:\ncmp w25,#13\nb.lt finish\nb eligible19\ncurrent_season19:\n'+b.ctx('seasons_v18')+b.get('Level','w28')+'cmp w28,#1\nb.eq current_school19\ncmp w28,#2\nb.eq current_college19\ncmp w28,#3\nb.eq current_nba19\ncmp w28,#4\nb.ne finish\nmov w28,#3\nb occupation19\ncurrent_school19:\nmov w28,#4\nb occupation19\ncurrent_college19:\nmov w28,#5\nb occupation19\ncurrent_nba19:\nmov w28,#2\noccupation19:\n'
 s+=h.load_occupation()+'\nldr w9,[x8,#0x10]\ncmp w28,#13\nb.ne build_checked20\ncmp w9,#1\nb.eq build_student20\nmov w28,#2\nb build_checked20\nbuild_student20:\nmov w28,#7\nbuild_checked20:\ncmp w28,#4\nb.eq student19\ncmp w28,#5\nb.eq student19\ncmp w28,#7\nb.eq student19\ncmp w25,#18\nb.lt finish\ncmp w9,#6\nb.ne finish\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr w9,[x8,#0x10]\ncmp w9,#2\nb.ne finish\nmov x0,xzr\nmov x1,xzr\nbl 0x31542f0\ncmp w28,#2\nb.eq nba19\ncmp w28,#3\nb.eq nfl19\ncmp w28,#6\nb.eq pro19\ncmp w0,#5\nb.ne finish\ncmp w28,#9\nb.eq regional19\ncmp w28,#10\nb.eq regional19\nb eligible19\nnba19:\ncmp w0,#2\nb.ne finish\nb eligible19\nnfl19:\ncmp w0,#1\nb.ne finish\nb eligible19\npro19:\ncmp w0,#1\nb.eq eligible19\ncmp w0,#2\nb.ne finish\nb eligible19\nstudent19:\ncmp w9,#1\nb.ne finish\nldr w9,[x8,#0x30]\ncmp w28,#4\nb.eq highschool19\ncmp w28,#5\nb.eq college19\ncmp w9,#2\nb.eq team19\nb college19\nhighschool19:\ncmp w9,#2\nb.ne finish\nb team19\ncollege19:\ncmp w9,#11\nb.eq team19\ncmp w9,#12\nb.ne finish\nteam19:\nldr x8,[x8,#0x20]\ncbz x8,finish\nldr x26,[x8,#0x48]\ncbz x26,finish\nldr w27,[x26,#0x18]\ncbz w27,finish\nldr x26,[x26,#0x10]\ncbz x26,finish\nadd x26,x26,#0x20\nteam_loop19:\nldr x8,[x26],#8\ncbz x8,team_next19\nldr w9,[x8,#0x18]\ncmp w9,#1\nb.ne team_next19\nldr x8,[x8,#0x10]\ncbz x8,team_next19\n'
 s+=h.compare_key('Basketball','eligible19','check_basketball_team19')+'\ncheck_basketball_team19:\n'+h.compare_key('Basketball Team','eligible19','check_basketball_lower19')+'\ncheck_basketball_lower19:\n'+h.compare_key('basketball','eligible19','team_next19')+'\nteam_next19:\nsubs w27,w27,#1\nb.ne team_loop19\nb finish\nregional19:\n'+b.ctx('soccer_v12')+b.get('CountryChosen')+'cmp w24,#1\nb.ne finish\n'+b.get('CountryPool','w25',-1)
 from native_cups import EU,CA
 nations=json.loads((ROOT.parent/'native_v13/assets/pools.json').read_text())['nationalpool']
 s+='cmp w28,#9\nb.ne copa_region19\n'
 for i,(_,flag)in enumerate(nations):
  if flag.removeprefix('flag-')in EU:s+=f'cmp w25,#{i}\nb.eq eligible19\n'
 s+='b finish\ncopa_region19:\n'
 for i,(_,flag)in enumerate(nations):
  if flag.removeprefix('flag-')in CA:s+=f'cmp w25,#{i}\nb.eq eligible19\n'
 s+='b finish\neligible19:\nmov w9,#1\nstr x9,[sp]\nb finish\n'
 b.eligibility=b.routine('current_eligibility19',s)
def hooks(b):
 # Root entries are native ListItems. +0xd0 disables both visuals and clicks.
 groups={'cup_access18':1,'soccer_v12':1,'seasons_v18':6,'pro_sports18':6,'school_sports18':7,'careers_v18':11,'storm_career19':11,'manager_career19':11,'coach_career19':11,'racer_career19':11,'discord19':12,'reddit19':12}
 s='cbz x19,finish\ncbz x21,finish\nldr x8,[x19,#0x10]\ncbz x8,finish\n'
 for owner,kind in groups.items():s+=h.compare_key(owner,'entry_kind19_'+owner,'entry_next19_'+owner)+'\nentry_next19_'+owner+':\n'
 s+='b finish\n'
 for owner,kind in groups.items():s+='entry_kind19_'+owner+f':\nmov w0,#{kind}\nb entry_check19\n'
 s+=f'entry_check19:\nbl {b.eligibility:#x}\ncbnz w0,finish\nmov w9,#1\nstrb w9,[x21,#0xd0]\nb finish'
 b.install('v19_grey_entry_requirements',0x306180c,s)
 s='mov x8,x1\ncbz x8,finish\n'
 for marker,kind in MARKERS.items():s+=h.compare_key(marker,'marker19_'+str(kind),'marker_next19_'+str(kind))+'\nmarker_next19_'+str(kind)+':\n'
 s+='b finish\n'
 for marker,kind in MARKERS.items():s+=f'marker19_{kind}:\nmov w0,#{kind}\nb marker_check19\n'
 s+=f'marker_check19:\nbl {b.eligibility:#x}\nstr x0,[sp]\nb return_custom'
 b.install('v19_grey_nested_requirements',0x304b8ac,s,ret=True)
 # Earlier releases hid injected Special Careers below 18. Keep them visible,
 # and let the item checks above disable them until adulthood.
 s='mov x8,x1\ncbz x8,finish\n'+h.compare_key('SpecialCareers','visible_special19','finish')+'\nvisible_special19:\n'+h.restore()+'\nsub sp,sp,#0xd0\nb 0x30611d4'
 b.install('v19_visible_special_careers',h.INJECT,s)
def integrations(b):
 def inject(reg,key):return b.string(key)+f'mov x1,x0\nmov x0,{reg}\ncbz x0,finish\nmov x2,xzr\nbl {h.INJECT:#x}\nb finish'
 b.install('v19_native_social_tab',0x311b8c4,inject('x21','SocialMedia'))
 for i,site in [(2,0x3150000),(3,0x31508f4),(4,0x31519fc),(5,0x3152b20),(6,0x31535bc),(7,0x3152234),(8,0x3151250)]:
  b.install('v19_native_following_'+str(i),site,inject('x19','SocialFollowing'+str(i)))
 # Add a season action to the actual joined Basketball extracurricular profile.
 s='cbz x19,finish\ncbz x20,finish\nldr x8,[x19,#0x170]\ncbz x8,finish\nldr w9,[x8,#0x18]\ncmp w9,#1\nb.ne finish\nldr x8,[x8,#0x10]\ncbz x8,finish\n'+h.compare_key('Basketball','basketball_choice19','basketball_team_check19')+'\nbasketball_team_check19:\n'+h.compare_key('Basketball Team','basketball_choice19','finish')+'\nbasketball_choice19:\nldr x8,[x20,#0x10]\ncbz x8,finish\nldr x8,[x8,#0x20]\ncbz x8,finish\nldr x0,[x8]\ncbz x0,finish\nbl 0x2237158\ncbz x0,finish\nmov x22,x0\n'+b.string('Basketball season & games')+'mov x1,x0\nmov x0,x22\nmov w2,wzr\nmov w3,#1\nmov x4,xzr\nbl 0x2a1bcf0\nldr x8,[x20]\nldr x9,[x8,#0x308]\nldr x2,[x8,#0x310]\nmov x0,x20\nmov x1,x22\nblr x9\nb finish'
 b.install('v19_school_basketball_action',0x25ab130,s)
 s='cbz x0,finish\nmov x22,x0\nldr x8,[x0,#0x108]\ncbz x8,finish\nldr w9,[x8,#0x18]\nsub w9,w9,#1\ncmp w1,w9\nb.ne finish\ncmp w1,#0\nb.lt finish\nadd x8,x8,#0x20\nldr x8,[x8,w1,uxtw #3]\ncbz x8,finish\nldr x8,[x8,#0x10]\ncbz x8,finish\n'+h.compare_key('Basketball season & games','open_school_season19','finish')+'\nopen_school_season19:\n'+b.string('genesis_v18_school_sports18')+'mov w1,#1\nmov w2,#1\nmov x3,xzr\nmov x4,xzr\nbl 0x30838cc\nb return_custom'
 b.install('v19_school_basketball_select',0x25ab174,s,ret=True)
