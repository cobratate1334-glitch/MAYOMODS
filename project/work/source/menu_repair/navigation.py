"""Let original transitions finish; return only to the actual menu that was tapped."""
import csv,io,json,os
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
from native_hooks import h


def hooks(b):
 st=b.states['menu_repair']['va'];ds=b.states['device_repair']['va'];old=b.states['playable_repair']['va']+512;epoch=b.states['menu_generation41']['va']
 adr=lambda reg='x28',off=0:f'adr {reg},{st+off:#x}\n'
 # Preserve every chained feature/theme hook. Skip ONLY the original v33
 # recovery body, whose force-SetActive races HeroBarSwap's later toggle.
 r=b.old['v33_recover_hidden_top_menu_after_dialog'];at=r['stub']+len(h.asm(h.save(),r['stub']))
 ins=next(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(bytes(b.blob[b.off(at):b.off(at)+4]),at));assert ins.mnemonic=='cbz'and ins.op_str.startswith('x0, #0x'),ins
 target=int(ins.op_str.split('#')[1],16);b.write(at,f'b {target:#x}','skip premature shared navigation activation')
 for record in b.manifest['hooks']+b.manifest['routines']:
  if record['stub']==r['stub']:record['source']=record['source'].replace('cbz x0,finish','b finish',1)
 # The later recovery helper cancels all UIListManager coroutines while a
 # legitimate close/slide can still be running. Keep stock completion paths.
 b.write(b.old['v46_restore_native_hud']['stub'],'ret','remove competing HUD coroutine recovery')
 for record in b.manifest['hooks']+b.manifest['routines']:
  if record['stub']==b.old['v46_restore_native_hud']['stub']:record.update(source='ret',length=4)

 assets=json.loads(Path(os.environ.get('MENU_BASE_ASSETS','/workspace/build_work/menu-1113/base_assets.json')).read_text())
 names=sorted(k for k,v in assets.items()if k.startswith('genesis_')and v.startswith('{'))
 def hash_(s):
  value=2166136261
  for c in s:value=((value^ord(c))*16777619)&0xffffffff
  return value
 hashes={hash_(s):s for s in names};assert len(hashes)==len(names)
 s='str xzr,[sp]\ncbz x0,finish\nldr w19,[x0,#16]\ncbz w19,finish\ncmp w19,#192\nb.hi finish\nadd x20,x0,#20\nmov w24,#2166136261\nmov w21,#16777619\nvalid_hash_loop:\nldrh w9,[x20],#2\neor w24,w24,w9\nmul w24,w24,w21\nsubs w19,w19,#1\nb.ne valid_hash_loop\n'
 for value in sorted(hashes):s+=f'cmp w24,#{value}\nb.eq valid_list_resource\n'
 s+='b finish\nvalid_list_resource:\nmov w9,#1\nstr x9,[sp]\nb finish';valid=b.routine('menu_valid_list_definition_resource',s)
 # Remember only real list definitions. A CSV sheet is never a menu ID.
 s=f'adr x28,{old:#x}\nldr w9,[x28,#32]\ncbnz w9,finish\n'+adr()+'str wzr,[x28,#32]\n'+f'bl {valid:#x}\ncbz w0,finish\n'+adr()+'mov w9,#1\nstr w9,[x28,#32]\nldr x0,[sp]\nldr x1,[sp,#8]\n'+f'bl {b.old["device_remember_actual_parent_menu"]["stub"]:#x}\nb finish'
 remember=b.routine('menu_remember_real_definition',s)
 r=b.resolved('device_remember_owner_at_list_entry');s=r['source'];before=f'bl {b.old["device_remember_actual_parent_menu"]["stub"]:#x}';assert before in s;b.redirect(r['name'],s.replace(before,f'bl {remember:#x}'))
 # Retain bounded actual List -> name/controller ownership for native Back.
 # The original stack may reveal an older List without rebuilding it.
 ring=768;capacity=16
 s='cbz x0,finish\nmov x19,x0\n'+adr()+'ldr w9,[x28,#32]\ncbz w9,finish\nldr w20,[x28,#48]\nand w20,w20,#15\nadd w9,w20,#1\nstr w9,[x28,#48]\n'+adr('x21',ring)+'add x21,x21,x20,lsl #6\n'
 for off in [0,8,16]:s+=f'ldr x0,[x21,#{off}]\nstr xzr,[x21,#{off}]\ncbz x0,record_free_{off}\nbl 0x223e784\nrecord_free_{off}:\n'
 s+='mov x0,x19\nmov w1,#0\nbl 0x223e704\nstr x0,[x21]\n'
 for field,off in [(16,8),(24,16)]:
  s+=f'adr x28,{ds:#x}\nldr x0,[x28,#{field}]\ncbz x0,record_no_{field}\nbl 0x223e73c\ncbz x0,record_no_{field}\nmov w1,#0\nbl 0x223e704\nstr x0,[x21,#{off}]\nrecord_no_{field}:\n'
 s+=f'adr x28,{ds:#x}\nldr x9,[x28,#32]\nstr x9,[x21,#24]\nldr w9,[x28,#40]\nstr w9,[x21,#32]\nb finish'
 b.install('menu_bind_actual_built_UIList',0x30898cc,s)
 s='str xzr,[sp]\ncbz x0,finish\nmov x19,x0\n'+f'bl {b.old["web_current_life_token"]["stub"]:#x}\nmov x23,x0\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr w24,[x8,#0x20]\n'+adr('x21',ring)+f'mov w22,#{capacity}\nowner_slot_loop:\nldr x9,[x21,#24]\ncmp x9,x23\nb.ne owner_slot_next\nldr w9,[x21,#32]\ncmp w9,w24\nb.ne owner_slot_next\nldr x0,[x21]\ncbz x0,owner_slot_next\nbl 0x223e73c\ncmp x0,x19\nb.ne owner_slot_next\nldr x0,[x21,#8]\ncbz x0,finish\nbl 0x223e73c\ncbz x0,finish\nmov x25,x0\nmov x26,xzr\nldr x0,[x21,#16]\ncbz x0,owner_controller_ready\nbl 0x223e73c\nmov x26,x0\nowner_controller_ready:\nmov x0,x25\nmov x1,x26\nbl {b.old["device_remember_actual_parent_menu"]["stub"]:#x}\nmov w9,#1\nstr x9,[sp]\nb finish\nowner_slot_next:\nadd x21,x21,#64\nsubs w22,w22,#1\nb.ne owner_slot_loop\nb finish'
 displayed=b.routine('menu_restore_actual_displayed_owner',s)
 # Bind a CSV chain only if a real menu is currently open and is that exact
 # built UIList. Children inherit ownership only during their parent's choice.
 r=b.resolved('device_bind_owned_scenario');s=r['source'];at=s.index('cbz x0,finish')
 gate=f'adr x28,{old:#x}\nldr w9,[x28,#32]\ncbz w9,bind_from_list\n'+adr()+'ldr w9,[x28,#16]\ncbnz w9,bind_owner_ready\nb finish\nbind_from_list:\n'+h.load_game()+'\nldr x8,[x8,#0x90]\ncbz x8,finish\nldr x0,[x8,#0x60]\ncbz x0,finish\nldrb w9,[x0,#0x80]\ncbz w9,finish\nldr x8,[x0,#0x78]\ncbz x8,finish\nmov x1,xzr\nbl 0x2f7d268\ncbz x0,finish\n'+f'bl {displayed:#x}\ncbz w0,finish\nbind_owner_ready:\nldr x0,[sp]\nldr x1,[sp,#8]\nldr x2,[sp,#16]\n'
 b.redirect(r['name'],s[:at]+gate+s[at:])
 r=b.resolved('device_capture_card_and_parent');s=r['source'];at=s.index('adrp ')
 # Every choice captures its actual age, including explicit navigation from a
 # stock card. A new annual event cannot inherit a remembered manual menu.
 start=adr()+'str wzr,[x28,#16]\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr w9,[x8,#0x20]\n'+adr()+'str w9,[x28,#40]\n'
 s=s[:at]+start+s[at:];mark='cmp x0,x19\nb.ne finish\n';assert s.count(mark)==1;s=s.replace(mark,mark+adr()+'mov w9,#1\nstr w9,[x28,#16]\n');b.redirect(r['name'],s)

 # Observe the REAL stock MoveNext call and returned yield flag, including
 # nested list-container slides. No timers or guessed frame counts.
 rows=json.loads((Path(__file__).resolve().parents[1]/'native_v41/native_bindings41.json').read_text())['iterators']
 rows+= [dict(name='ShowLowerPanel',guard_site=0x2f7f540),dict(name='HideLowerPanel',guard_site=0x2f7ed88)]
 for index,row in enumerate(rows):
  site=row['guard_site'];ins=next(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(bytes(b.blob[b.off(site):b.off(site)+4]),site));assert ins.mnemonic=='b',row
  previous=int(ins.op_str.lstrip('#'),16);slot=256+index*32
  # Two separate slots for normal/menu UIListContainer animations.
  choose=''
  if row['name']in ['HideListPanel','ShowListPanel']:
   choose='ldr x8,[x19,#0x20]\ncbz x8,track_slot_ready\nldr w9,[x8,#0xe4]\ncmp w9,#1\nb.ne track_slot_ready\nadd x22,x22,#16\n'
  s='mov x19,x0\nmov w21,#0\ncbz x0,track_run\n'+f'adr x28,{epoch:#x}\nldr w20,[x28]\nldr w9,[x0,#0x14]\ncmp w9,w20\nb.ne track_run\nmov w21,#1\n'+adr('x22',slot)+choose+'track_slot_ready:\nstr w21,[x22]\nstr w20,[x22,#4]\ntrack_run:\n'+f'bl {previous:#x}\nstr x0,[sp]\ncbz w21,track_done\n'+f'adr x28,{epoch:#x}\nldr w9,[x28]\ncmp w9,w20\nb.ne track_done\nstr w20,[x22,#4]\nstr w0,[x22]\ntrack_done:\nb return_custom'
  b.install('menu_observe_'+row['name'],site,s,ret=True)
 # Disable only 1112's pre-Exec drain. Other mailbox, portrait and military
 # hooks stay in place. Flush after Unity has run this frame's queued work.
 b.write(b.old['device_after_card_destruction']['stub'],'ret','remove pre-Unity-work parent drain')
 for record in b.manifest['hooks']+b.manifest['routines']:
  if record['stub']==b.old['device_after_card_destruction']['stub']:record.update(source='ret',length=4)
 token=b.old['web_current_life_token']['stub'];clear=b.old['playable_clear_deferred_parent']['stub'];flush=b.old['device_flush_original_parent']['stub']
 s=f'adr x28,{ds:#x}\nldr w9,[x28,#8]\ncbz w9,finish\n'+adr()+'ldr w9,[x28]\ncbnz w9,finish\n'+f'bl {token:#x}\nadr x28,{old:#x}\nldr x9,[x28,#16]\ncmp x0,x9\nb.ne discard_parent\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,discard_parent\nldr w9,[x8,#0x20]\n'+adr()+'ldr w10,[x28,#40]\ncmp w9,w10\nb.ne discard_parent\n'
 s+=h.load_game()+'\nldr x8,[x8,#0x90]\ncbz x8,finish\nldr x8,[x8,#0x80]\ncbz x8,finish\nldr x0,[x8,#0x1c8]\ncbnz x0,finish\n'+f'adr x28,{ds:#x}\nldr x0,[x28]\ncbz x0,old_card_gone\nbl 0x223e73c\ncbz x0,old_card_gone\nmov x1,xzr\nmov x2,xzr\nbl 0x5575198\ncbnz w0,finish\nold_card_gone:\nadr x28,{epoch:#x}\nldr w20,[x28]\n'
 for index in range(len(rows)*2):
  s+=adr('x28',256+index*16)+f'ldr w9,[x28]\ncbz w9,transition_next_{index}\nldr w9,[x28,#4]\ncmp w9,w20\nb.eq finish\ntransition_next_{index}:\n'
 s+=adr()+'mov w9,#1\nstr w9,[x28]\n'+f'bl {flush:#x}\n'+adr()+'str wzr,[x28]\nb finish\ndiscard_parent:\n'+f'bl {clear:#x}\nb finish'
 drain=b.routine('menu_drain_after_real_UI_transitions',s)
 b.install('menu_after_Unity_synchronization_work',0x557cc4c,f'bl {drain:#x}\nb finish')
