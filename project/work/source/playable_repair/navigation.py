"""Open an authored parent list AFTER the original alert cleanup.

Both stock AcceptChoice virtual-call branches remove their current card after
running its Blueprint. Showing a list during that Blueprint lets RemoveAlert
hide/refresh the just-opened parent. Keep rooted arguments through that exact
native boundary. Other navigation retains its original behavior.
"""
from native_hooks import h


def hooks(b):
    state=b.states['playable_repair']['va']+512
    token=b.old['web_current_life_token']['stub']
    # Four roots/flags are private to this new owner. No raw managed pointer
    # survives an IL2CPP allocation or is stored in BSS.
    def adr():return f'adr x28,{state:#x}\n'
    cleanup=''
    for off in [0,8]:
        cleanup+=adr()+f'ldr x0,[x28,#{off}]\nstr xzr,[x28,#{off}]\ncbz x0,nav_free_{off}\nbl 0x223e784\nnav_free_{off}:\n'
    clear=b.routine('playable_clear_deferred_parent',cleanup+adr()+'str wzr,[x28,#32]\nstr wzr,[x28,#36]\nb finish')
    mark=f'bl {clear:#x}\nbl {token:#x}\n'+adr()+'str x0,[x28,#16]\nmov w9,#1\nstr w9,[x28,#32]\nb finish'
    # Mark only the calls that always reach RemoveAlert, avoiding early-return
    # branches elsewhere in AcceptChoice. Replay the exact original BLR.
    for n,site in enumerate([0x2f939dc,0x2f93a20]):
        b.install('playable_accept_choice_scope_'+str(n),site,mark)
    continuation=adr()+'ldr w9,[x28,#32]\ncbz w9,finish\nmov w9,#1\nstr w9,[x28,#36]\nb finish'
    b.install('playable_observe_original_scenario_continuation',0x2f79f5c,continuation)
    prefix='genesis_'
    s=adr()+'ldr w9,[x28,#32]\ncbz w9,finish\ncbz x0,finish\nmov x27,x0\nldr w9,[x27,#16]\n'+f'cmp w9,#{len(prefix)}\nb.lt finish\n'
    for i,ch in enumerate(prefix):s+=f'ldrh w9,[x27,#{20+i*2}]\ncmp w9,#{ord(ch)}\nb.ne finish\n'
    # Current choice owns these arguments. Preserve all four actual parameters.
    s+='mov x25,x1\nmov w26,w2\nmov w24,w3\n'+cleanup
    s+='mov x0,x27\nmov w1,#0\nbl 0x223e704\n'+adr()+'str x0,[x28]\ncbz x25,nav_no_controller\nmov x0,x25\nmov w1,#0\nbl 0x223e704\n'+adr()+'str x0,[x28,#8]\nnav_no_controller:\n'+adr()+'str w26,[x28,#24]\nstr w24,[x28,#28]\nmov w0,#1\nstr x0,[sp]\nb return_custom'
    b.chain('playable_defer_authored_parent_during_accept','v54_old_crime_routes_return_to_stock_menu',s,ret=True)
    s=adr()+'str wzr,[x28,#32]\nldr x9,[x28]\ncbz x9,finish\n'+f'bl {token:#x}\n'+adr()+'ldr x9,[x28,#16]\ncmp x0,x9\nb.ne nav_discard\n'
    # LaunchScenarioOrDarkly is observed before translation can defer its UI.
    # CurrentScenario itself is deliberately retained by RemoveAlert.
    s+=adr()+'ldr w9,[x28,#36]\ncbnz w9,nav_discard\n'
    s+=adr()+'ldr x0,[x28]\nbl 0x223e73c\ncbz x0,nav_discard\nmov x25,x0\n'+adr()+'ldr x0,[x28,#8]\ncbz x0,nav_flush_null_controller\nbl 0x223e73c\nnav_flush_null_controller:\nmov x1,x0\nmov x0,x25\n'+adr()+'ldr w2,[x28,#24]\nldr w3,[x28,#28]\nmov x4,xzr\nbl 0x3089aac\nnav_discard:\n'+f'bl {clear:#x}\nb finish'
    b.install('playable_parent_after_original_alert_cleanup',0x2f939e8,s)
