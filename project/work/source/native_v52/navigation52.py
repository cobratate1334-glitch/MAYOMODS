"""Preserve close ownership while rejecting obsolete deferred presentations."""
from native_hooks import h
from native_v42.patch_native42 import body

def hooks(b):
 # A custom birth year should not silently remove the user's social menu.
 # Restore the eight stock platform construction blocks. Their normal native
 # age/account requirements remain; calendar-driven cars/houses/themes remain.
 restored=[]
 for name in ['Facebook','Instagram','OnlyFans','TikTok','Twitch','Twitter','SoundCloud','YouTube']:
  r=b.old['v45_social_'+name];site=r['site'];b.blob[b.off(site):b.off(site)+4]=h.asm(r['original'],site);b.changed.append([site,4,'restore visible social platform '+name]);restored.append(name)
 b.manifest['v52_restored_stock_social_platforms']=restored
 # The generation guards already invalidate stale work. StopAllCoroutines on
 # the owner also cancels the live close that called ShowList/RemoveList.
 # Retain the epoch advance; let every current parent finish its cleanup.
 for name in ['v41_new_list_cancels_obsolete_work','v41_close_list_cancels_obsolete_work']:
  old=b.old[name];src=body(old);p=src.index('mov x0,x27\nmov x1,xzr\nbl 0x55779e0')
  src=src[:p]+'b finish'
  b.redirect(name,h.save()+'\n'+src+'\nfinish:\n'+h.restore()+'\n'+old['original']+f'\nb {old["resume"]:#x}')
 # Existing quiescence checks remain the gate for restoring native UI.
 # Re-enable accessibility groups even if their GameObjects stayed active
 # during the transition. Visual activation and accessibility are independent.
 old=b.resolved('v46_restore_native_hud');src=body(old)
 for n in range(4):src=src.replace(f'cbnz w0,group46_{n}',f'cbnz w0,activate52_group_{n}')
 for n,method in enumerate([0x2f7e424,0x2f8144c,0x2f7e530,0x2f7e5a0]):
  marker=f'mov x0,x27\nmov w1,#1\nmov x2,xzr\nbl {method:#x}'
  assert marker in src;src=src.replace(marker,f'activate52_group_{n}:\n'+marker,1)
 b.replace52(old['name'],src)
