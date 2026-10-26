"""Guard old saved routes and native invitations, not just added buttons."""
from native_hooks import h

def hooks(b):
 year=b.old['v45_current_year']['stub']
 for name in ['facebook','twitter','youtube']:
  old=b.old['followup_random_invitation_'+name]
  b.install('connected_random_social_2010_'+name,old['site'],f'bl {year:#x}\ncmp w0,#2010\nb.lt return_custom\nb finish',custom_resume=old['custom_resume'])
 for name in ['life_rework_added_platform_years','web_execute_authored_command_v55']:
  row=b.resolved(name);s=row['source'].replace('cmp w0,#2006','cmp w0,#2010').replace('cmp w0,#2005','cmp w0,#2010');b.redirect(row['name'],s)
 # Rewrite the native list identifier before the original site callback.
 s='cbz x0,finish\nmov x27,x0\nmov x8,x0\n'
 for n,name in enumerate(['genesis_v18_roblox_social','genesis_v18_social_v18']):
  s+=h.compare_key(name,'early_social_list1110','early_social_next1110_'+str(n))+f'\nearly_social_next1110_{n}:\n'
 s+='b finish\nearly_social_list1110:\n'+f'bl {year:#x}\ncmp w0,#2010\nb.ge finish\n'+b.string('genesis_social_locked1110')+'str x0,[sp]\nb finish'
 b.chain('connected_lock_original_social_list_before_2010','web_open_social_and_parish',s)
 # Reject war archives outside their periods and direct access by prisoners.
 s='cbz x2,finish\nmov x27,x2\nmov x8,x2\n'
 routes=[('scenario.lifeRework.war_magazines1110',0),('scenario.lifeRework.magazine_ww11110',1),('scenario.lifeRework.magazine_ww21110',2)]
 for n,(name,war)in enumerate(routes):
  s+=h.compare_key(name,'check_war_archive1110_'+str(n),'war_archive_next1110_'+str(n))+f'\ncheck_war_archive1110_{n}:\nbl {year:#x}\n'
  if war in [0,1]:s+='cmp w0,#1914\nb.lt archive_try_second1110_'+str(n)+'\ncmp w0,#1918\nb.le finish\narchive_try_second1110_'+str(n)+':\n'
  if war in [0,2]:s+='cmp w0,#1939\nb.lt archive_closed1110\ncmp w0,#1945\nb.le finish\n'
  s+='b archive_closed1110\n'+f'war_archive_next1110_{n}:\n'
 s+='b finish\narchive_closed1110:\n'+b.string('scenario.lifeRework.military_peace1110')+'str x0,[sp,#16]\nb finish'
 b.chain('connected_direct_period_archive_gate','v47_bind_native_scenario',s)

 s='cbz x2,finish\nmov x8,x2\n'+h.compare_key('scenario.lifeRework.school_fight1106','suspended_fight1110','finish')+'\nsuspended_fight1110:\n'+b.ctx('life_rework')+b.get('SchoolSuspendedAge1110')+'cmp w24,w23\nb.lt finish\n'+b.string('scenario.lifeRework.school_suspended1110')+'str x0,[sp,#16]\nb finish'
 b.chain('connected_saved_school_fight_suspension','v47_bind_native_scenario',s)
