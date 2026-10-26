"""Main-thread snapshots, life-scoped mailbox and save-backed native actions."""
from native_hooks import h
from military_expansion.jni import BOX,TEXT,WIDTH,PNG

def hooks(b):
    resolve=b.old['resolve_ui_export21']['stub'];owner=b.old['web_current_life_token']['stub'];year=b.old['v45_current_year']['stub']
    box=f'adr x0,{b.literal("mayo_military"):#x}\nbl {resolve:#x}\ncbz x0,finish\nmov x28,x0\n'
    # Pointer arithmetic is based on a resolved export, never a link-time ASLR
    # address. All text buffers have explicit UTF-16 bounds and terminators.
    serial=[0]
    def dest(index,reg='x10'):
        return f'mov w9,#{TEXT[index]-BOX}\nadd {reg},x28,x9\n'
    def copy_string(index):
        serial[0]+=1;n=serial[0];return dest(index)+f'mov w11,#0\ncbz x0,copy_end1108_{n}\nldr w12,[x0,#16]\nmov w13,#{WIDTH[index]-1}\ncmp w12,w13\ncsel w12,w12,w13,lo\nadd x0,x0,#20\ncopy_loop1108_{n}:\ncmp w11,w12\nb.hs copy_end1108_{n}\nldrh w13,[x0,w11,uxtw #1]\nstrh w13,[x10,w11,uxtw #1]\nadd w11,w11,#1\nb copy_loop1108_{n}\ncopy_end1108_{n}:\nstrh wzr,[x10,w11,uxtw #1]\n'
    def getstr(key):return b.string(key)+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\n'
    snap=f'bl {b.old["life_rework_snapshot"]["stub"]:#x}\n'+box+'ldr w9,[x28,#60]\nadd w9,w9,#1\nstr w9,[x28,#60]\ndmb ishst\n'+f'bl {year:#x}\nstr w0,[x28,#32]\n'+h.load_game()+'\nldr x26,[x8,#0x28]\ncbz x26,snapshot_end1108\nldr w9,[x26,#0x20]\nstr w9,[x28,#36]\nldr w9,[x26,#0xf8]\nstr w9,[x28,#40]\nldrb w9,[x26,#0x18]\nstr w9,[x28,#76]\nldr x8,[x8,#0x48]\nmov w9,#0\ncbz x8,sound_done1108\nldrb w9,[x8,#0x5e]\nsound_done1108:\nstr w9,[x28,#64]\nmov x0,x26\nmov x1,xzr\nbl 0x2c44914\n'+copy_string(0)
    snap+='mov x0,x26\nmov x1,xzr\nbl 0x2c38288\ncbz x0,no_city1108\nmov x1,xzr\nbl 0x2a27240\nb city_ready1108\nno_city1108:\nmov x0,xzr\ncity_ready1108:\n'+copy_string(3)
    for method,offset in [(0x2c422f4,48),(0x2c42304,52)]:snap+=f'mov x0,x26\nmov x1,xzr\nbl {method:#x}\nfcvtzs w9,s0\nstr w9,[x28,#{offset}]\n'
    snap+=b.ctx('life_rework')+b.get('NativeMilitary')+'str w24,[x28,#44]\n'+getstr('Country')+copy_string(1)
    snap+=f'mov x0,x26\nbl {b.old["v52_person_birth_country_name"]["stub"]:#x}\n'+copy_string(2)
    snap+=b.ctx('life_rework')+getstr('MilitaryState1108')+copy_string(8)+getstr('ChessState1108')+copy_string(9)
    # Parent chess uses the same native family record and a life token, not the
    # unrelated shared story preview. Deceased/missing parents cannot be played.
    snap+='str wzr,[x28,#80]\nstr wzr,[x28,#84]\nmov x0,xzr\n'+copy_string(4)+'ldr w9,[x28,#68]\ncmp w9,#1\nb.lt snapshot_end1108\ncmp w9,#2\nb.gt snapshot_end1108\n'+h.load_game()+'\nldr x8,[x8,#0x20]\ncbz x8,snapshot_end1108\nldr w9,[x28,#68]\ncmp w9,#1\nldr x26,[x8,#0xa8]\nb.eq chess_parent_ready1108\nldr x26,[x8,#0xb8]\nchess_parent_ready1108:\ncbz x26,snapshot_end1108\nldrb w9,[x26,#0x18]\nstr w9,[x28,#80]\nldr w9,[x26,#0x20]\nstr w9,[x28,#84]\nmov x0,x26\nmov x1,xzr\nbl 0x2c44914\n'+copy_string(4)+'snapshot_end1108:\nldr w9,[x28,#60]\nadd w9,w9,#1\nadd x10,x28,#60\nstlr w9,[x10]\nb finish'
    snapshot=b.routine('military1108_snapshot',snap)
    # Export a COPY of the already-validated live face for the uniform bust.
    # The game image and its cache are never replaced by this display operation.
    ps=b.states['life_rework']['va'];portrait=box+'str wzr,[x28,#72]\n'+f'bl {owner:#x}\nadr x26,{ps:#x}\nldr x9,[x26,#16]\ncmp x0,x9\nb.ne finish\nldr x0,[x26,#8]\ncbz x0,finish\nbl 0x223e73c\ncbz x0,finish\nmov x25,x0\n'+f'bl 0x223e48c\nadr x1,{b.literal("UnityEngine.ImageConversionModule"):#x}\nbl 0x223e490\ncbz x0,finish\nbl 0x223df90\nadr x1,{b.literal("UnityEngine"):#x}\nadr x2,{b.literal("ImageConversion"):#x}\nbl 0x223dfc8\ncbz x0,finish\nadr x1,{b.literal("EncodeToPNG"):#x}\nmov w2,#1\nbl 0x223dff0\ncbz x0,finish\nsub sp,sp,#32\nstr x25,[sp]\nstr xzr,[sp,#16]\nmov x1,xzr\nmov x2,sp\nadd x3,sp,#16\nbl 0x223e8b0\nldr x9,[sp,#16]\nadd sp,sp,#32\ncbnz x9,finish\ncbz x0,finish\nldr x25,[x0,#24]\ncbz x25,finish\nmov w9,#0x80000\ncmp x25,x9\nb.hi finish\nadd x26,x0,#32\nmov w9,#{PNG-BOX}\nadd x27,x28,x9\nmov x9,#0\nportrait_copy1108:\ncmp x9,x25\nb.hs portrait_ready1108\nldrb w10,[x26,x9]\nstrb w10,[x27,x9]\nadd x9,x9,#1\nb portrait_copy1108\nportrait_ready1108:\nstr w25,[x28,#72]\nb finish'
    photo=b.routine('military1108_copy_live_face',portrait)
    # Reuse the audited original military object construction, without the old
    # immediate deployment increment. Training/assignment is now a later state.
    old=b.old['life_rework_native_action']['source'];start=old.index('rework_action_enlist:\n');end=old.index('rework_deploy_existing:\n',start)
    body=old[start:end].replace('rework_deploy_existing','finish')
    body=body[body.index('ldr w9,[x8,#0x10]'):]
    enlist=b.ctx('life_rework')+'cmp w23,#18\nb.lt finish\ncmp w23,#45\nb.gt finish\n'+h.load_occupation()+'\n'+body+'b finish'
    service=b.routine('military1108_construct_native_service_once',enlist)
    # Input state and chess strings commit on Unity only. Epoch, actual Life
    # owner, exact request sequence and actual year are checked before mutation.
    poll=box+'add x9,x28,#4\nldar w19,[x9]\nldr w10,[x28,#8]\ncmp w19,w10\nb.eq finish\n'+f'bl {owner:#x}\ncbz x0,military_stale1108\nldr x9,[x28,#16]\ncmp x0,x9\nb.ne military_stale1108\nbl {year:#x}\nldr w9,[x28,#32]\ncmp w0,w9\nb.ne military_stale1108\nldr w20,[x28,#12]\nmov w9,#1\nstr w9,[x28,#28]\n'
    # Native enlistment guard is independent of visible buttons. These are the
    # supported jurisdictions; unverified countries retain original applications.
    poll+=h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,military_stale1108\nldrb w9,[x8,#0x18]\ncbz w9,military_stale1108\n'
    poll+='cmp w20,#2\nb.ne military_save1108\n'+b.ctx('life_rework')+'cmp w23,#18\nb.lt military_rejected1108\ncmp w23,#45\nb.gt military_rejected1108\n'+b.get('Year','w25')+getstr('Country')+'cbz x0,military_rejected1108\nmov x8,x0\n'
    for name,label in [('United States','us'),('United States of America','us'),('United Kingdom','gb'),('Australia','au')]:poll+=h.compare_key(name,'enlist_'+label+'1108','enlist_next_'+str(len(poll)))+'\nenlist_next_'+str(len(poll))+':\n'
    poll+='b military_rejected1108\nenlist_us1108:\ncmp w25,#1917\nb.lt military_rejected1108\ncmp w25,#1918\nb.lt enlist_ok1108\ncmp w25,#1940\nb.lt military_rejected1108\ncmp w25,#1945\nb.ge military_rejected1108\nb enlist_ok1108\nenlist_gb1108:\nenlist_au1108:\ncmp w25,#1914\nb.lt military_rejected1108\ncmp w25,#1918\nb.lt enlist_ok1108\ncmp w25,#1939\nb.lt military_rejected1108\ncmp w25,#1945\nb.ge military_rejected1108\nenlist_ok1108:\n'+f'bl {service:#x}\nbl {snapshot:#x}\nldr w9,[x28,#44]\ncbz w9,military_rejected1108\n'
    poll+='military_save1108:\n'+b.ctx('life_rework')
    # Empty strings are valid. NewString(ptr,length) is the exact existing
    # IL2CPP UTF-16 API. Its result remains rooted by the saved GFC dictionary.
    for index,key in [(11,'MilitaryState1108'),(12,'ChessState1108')]:
        poll+=dest(index,'x26')+f'mov w27,#0\nstate_len1108_{index}:\nldrh w9,[x26,w27,uxtw #1]\ncbz w9,state_ready1108_{index}\nadd w27,w27,#1\nmov w9,#{WIDTH[index]-1}\ncmp w27,w9\nb.lo state_len1108_{index}\nstate_ready1108_{index}:\nmov x0,x26\nmov w1,w27\nbl 0x223e8d4\nmov x22,x0\n'+b.textptr(key)
    # Small, real native consequences. The model settles the mission/match
    # before sending a request; the mailbox prevents the same serial applying twice.
    poll+='cmp w20,#3\nb.ne no_wound1108\n'+h.load_game()+'\nldr x0,[x8,#0x28]\nmov w1,#-8\nmov x2,xzr\nbl 0x2c46670\nno_wound1108:\ncmp w20,#4\nb.ne no_chess1108\n'+h.load_game()+'\nldr x0,[x8,#0x28]\nmov w1,#1\nmov x2,xzr\nbl 0x2c46830\nno_chess1108:\n'
    poll+=dest(13,'x26')+'ldrh w9,[x26]\ncbz w9,no_journal1108\nmov w27,#0\njournal_len1108:\nldrh w9,[x26,w27,uxtw #1]\ncbz w9,journal_ready1108\nadd w27,w27,#1\ncmp w27,#2047\nb.lo journal_len1108\njournal_ready1108:\nmov x0,x26\nmov w1,w27\nbl 0x223e8d4\n'+f'bl {b.journal55:#x}\nno_journal1108:\nbl {snapshot:#x}\ncmp w20,#5\nb.ne military_ack1108\nbl {photo:#x}\nb military_ack1108\nmilitary_rejected1108:\nmov w9,#2\nstr w9,[x28,#28]\nb military_ack1108\nmilitary_stale1108:\nmov w9,#3\nstr w9,[x28,#28]\nstr wzr,[x28,#24]\nmilitary_ack1108:\nadd x9,x28,#8\nstlr w19,[x9]\nb finish'
    pump=b.routine('military1108_execute_mailbox',poll)
    b.chain('military1108_unity_thread_pump','web_unity_thread_command_pump',f'bl {pump:#x}\nb finish')
    # Opening is a native game action. Android Canvas/dialogs stay inside the
    # activity window; no WebView, site, intent or server is used by this module.
    opening='mov w19,w0\ncmp w19,#501\nb.lt finish\ncmp w19,#504\nb.gt finish\n'+box+f'bl {owner:#x}\ncbz x0,finish\nstr x0,[x28,#16]\nldr w9,[x28]\nadd w9,w9,#1\nstr w9,[x28]\nstr wzr,[x28,#4]\nstr wzr,[x28,#8]\nmov w9,#1\nstr w9,[x28,#24]\nsub w9,w19,#501\nstr w9,[x28,#56]\nsub w9,w19,#502\ncmp w9,#1\ncsel w9,w9,wzr,ge\nstr w9,[x28,#68]\nbl {snapshot:#x}\nbl {photo:#x}\nmov w0,#2201\nbl {b.trace23:#x}\nb return_custom'
    b.chain('military1108_open_native_panel','life_rework_native_action',opening,ret=True)
    # Detect year/owner changes only after the native HUD has a real life. Java
    # first persists the timeline ledger, then presents queued dated news.
    auto=box+f'bl {owner:#x}\ncbz x0,finish\nmov x26,x0\nbl {year:#x}\nmov w25,w0\nldr x9,[x28,#104]\ncmp x9,x26\nb.ne military_year_changed1108\nldr w9,[x28,#112]\ncmp w9,w25\nb.eq finish\nmilitary_year_changed1108:\nstr wzr,[x28,#72]\nstr x26,[x28,#104]\nstr w25,[x28,#112]\nstr x26,[x28,#16]\nldr w9,[x28]\nadd w9,w9,#1\nstr w9,[x28]\nstr wzr,[x28,#4]\nstr wzr,[x28,#8]\nmov w9,#1\nstr w9,[x28,#24]\nstr wzr,[x28,#56]\nstr wzr,[x28,#68]\nbl {snapshot:#x}\nmov w0,#2200\nbl {b.trace23:#x}\nb finish'
    b.chain('military1108_year_boundary_news','v33_recover_hidden_top_menu_after_dialog',auto)
