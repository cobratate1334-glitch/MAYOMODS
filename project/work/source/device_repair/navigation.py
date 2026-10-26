"""One native list path and parent return after Unity destroys the old card."""
from native_hooks import h
from playable_repair.visuals import prefix


def hooks(b):
    state=b.states['device_repair']['va'];oldstate=b.states['playable_repair']['va']+512
    token=b.old['web_current_life_token']['stub']
    def adr(reg='x28',offset=0):return f'adr {reg},{state+offset:#x}\n'
    def oldadr():return f'adr x28,{oldstate:#x}\n'
    def free(offset):
        return adr()+f'ldr x0,[x28,#{offset}]\nstr xzr,[x28,#{offset}]\ncbz x0,free_{offset}\nbl 0x223e784\nfree_{offset}:\n'
    # The one-argument overload bypassed every mod pre-show/lifecycle hook.
    # Keep its native defaults, route through the same four-argument API.
    s='cbz x0,finish\nmov x8,x0\n'+prefix('genesis_','unify_owned','finish')+'unify_owned:\nmov x1,xzr\nmov w2,#0\nmov w3,#0\nmov x4,xzr\nbl 0x3089aac\nstr x0,[sp]\nb return_custom'
    b.install('device_unify_original_list_overload',0x30895ac,s,ret=True)

    # Remember the actual shown owner, including its native controller. Do
    # not replace it while a choice is only requesting a deferred menu return.
    s=oldadr()+'ldr w9,[x28,#32]\ncbnz w9,finish\ncbz x0,finish\nmov x19,x0\nmov x20,x1\nmov x8,x0\n'+prefix('genesis_','remember_owner','finish')+'remember_owner:\n'+free(16)+free(24)+'mov x0,x19\nmov w1,#0\nbl 0x223e704\n'+adr()+'str x0,[x28,#16]\ncbz x20,owner_no_controller\nmov x0,x20\nmov w1,#0\nbl 0x223e704\n'+adr()+'str x0,[x28,#24]\nowner_no_controller:\n'+f'bl {token:#x}\n'+adr()+'str x0,[x28,#32]\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr w9,[x8,#0x20]\n'+adr()+'str w9,[x28,#40]\nb finish'
    remember=b.routine('device_remember_actual_parent_menu',s)
    b.chain('device_remember_owner_at_list_entry','v47_project_before_show',f'bl {remember:#x}\nb finish')

    # Bind actual CSV instances to that owner. All registered mod namespaces
    # are known from exact APK data, not just the newest lifeRework namespace.
    import json,csv,io
    csv.field_size_limit(16*1024*1024)
    from pathlib import Path
    import os
    assets=json.loads(Path(os.environ.get('DEVICE_BASE_ASSETS','/workspace/build_work/device-repair/base_assets.json')).read_text())
    namespaces=sorted({'.'.join(r['ScenarioID'].split('.')[:2])+'.' for name,value in assets.items() if name.startswith('genesis_')and value.startswith('ScenarioID,') for r in csv.DictReader(io.StringIO(value)) if r.get('ScenarioID','').startswith(('scenario.activitiesV','scenario.careersV','scenario.lifeRework.','scenario.musicStudio.','scenario.paroleEvents41.'))})
    s='cbz x0,finish\ncbz x2,finish\nmov x19,x0\nmov x20,x1\nmov x27,x2\n'
    for i,ns in enumerate(namespaces):s+='mov x8,x27\n'+prefix(ns,'bind_owned','bind_next_'+str(i))+'bind_next_'+str(i)+':\n'
    s+='b finish\nbind_owned:\n'+free(48)+'mov x0,x19\nmov w1,#0\nbl 0x223e704\n'+adr()+'str x0,[x28,#48]\nb finish'
    bind=b.routine('device_bind_owned_scenario',s)
    b.chain('device_bind_owner_at_load','v47_bind_native_scenario',f'bl {bind:#x}\nb finish')

    # The old alert GameObject is destroyed at end-of-frame, AFTER RemoveAlert
    # has cleared its pointer. Root that object and wait for Unity's real null
    # comparison; a null CurrentCard alone does not mean cleanup has finished.
    capture=h.load_game()+'\nldr x8,[x8,#0x90]\ncbz x8,capture_parent\nldr x8,[x8,#0x80]\ncbz x8,capture_parent\nldr x0,[x8,#0x1c8]\ncbz x0,capture_parent\nmov w1,#0\nbl 0x223e704\n'+adr()+'str x0,[x28]\ncapture_parent:\n'+adr()+'ldr x0,[x28,#48]\ncbz x0,finish\nbl 0x223e73c\nldr x19,[sp]\ncmp x0,x19\nb.ne finish\n'+h.load_game()+'\nldr x8,[x8,#0x20]\ncbz x8,finish\nldrb w9,[x8,#0x20]\ncbnz w9,finish\n'+f'bl {token:#x}\n'+adr()+'ldr x9,[x28,#32]\ncmp x0,x9\nb.ne finish\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr w9,[x8,#0x20]\n'+adr()+'ldr w10,[x28,#40]\ncmp w9,w10\nb.ne finish\n'
    for source,dest in [(16,0),(24,8)]:
        capture+=adr()+f'ldr x0,[x28,#{source}]\ncbz x0,capture_skip_{source}\nbl 0x223e73c\ncbz x0,capture_skip_{source}\nmov w1,#0\nbl 0x223e704\n'+oldadr()+f'str x0,[x28,#{dest}]\ncapture_skip_{source}:\n'
    capture+=oldadr()+'str wzr,[x28,#24]\nstr wzr,[x28,#28]\nb finish';capture_fn=b.routine('device_capture_card_and_parent',capture)
    for name in ['playable_accept_choice_scope_0','playable_accept_choice_scope_1']:
        row=b.resolved(name);source=row['source'];mark='\nb finish\nfinish:';assert source.count(mark)==1
        b.redirect(row['name'],source.replace(mark,f'\nldr x0,[sp]\nbl {capture_fn:#x}'+mark))
    row=b.resolved('playable_clear_deferred_parent');source=row['source'];mark='\nfinish:\n';assert source.count(mark)==1
    extra=free(0)+adr()+'str wzr,[x28,#8]\n'
    b.redirect(row['name'],source.replace('b finish'+mark,extra+'b finish'+mark))
    # Move the original flush body into a normal callable helper. Its old hook
    # epilogue replays AcceptChoice's stack load and cannot run from Update.
    row=b.resolved('playable_parent_after_original_alert_cleanup');source=row['source'];start=source.index('str wzr,[x28,#32]');start=source.rfind('adrp ',0,start);end=source.index('\nfinish:\n')
    flush=b.routine('device_flush_original_parent',source[start:end])
    mark=source.index('\nfinish:\n');begin=source.index('\nadrp ')
    stage=oldadr()+'str wzr,[x28,#32]\nldr x9,[x28]\ncbz x9,device_no_parent\nldr w9,[x28,#36]\ncbnz w9,device_no_parent\n'+adr()+'mov w9,#1\nstr w9,[x28,#8]\nb finish\ndevice_no_parent:\n'+f'bl {b.resolved("playable_clear_deferred_parent")["stub"]:#x}\nb finish'
    b.redirect(row['name'],source[:begin+1]+stage+source[mark:])
    tick=adr()+'ldr w9,[x28,#8]\ncbz w9,finish\nldr x0,[x28]\ncbz x0,device_card_gone\nbl 0x223e73c\ncbz x0,device_card_gone\nmov x1,xzr\nmov x2,xzr\nbl 0x5575198\ncbnz w0,finish\ndevice_card_gone:\n'+f'bl {flush:#x}\nb finish'
    tickfn=b.routine('device_after_card_destruction',tick)
    b.chain('device_parent_on_unity_frame','web_unity_thread_command_pump',f'bl {tickfn:#x}\nb finish')
