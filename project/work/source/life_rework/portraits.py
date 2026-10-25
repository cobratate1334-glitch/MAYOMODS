"""Give the header its own validated texture, independent of cache destruction."""
from native_hooks import h

def hooks(b):
    state=b.state
    # State +0/+8 are GC handles for source/copy, +16 is a Life token;
    # +24 is a rooted header, +40 retry flag, +44 retry count. No raw roots.
    token=b.old['web_current_life_token']['stub']
    checker=b.old['v54_portrait_pixels_have_colour']['stub']
    s='str x0,[sp]\nmov x19,x0\n'+f'adr x28,{state:#x}\nbl {token:#x}\ncbz x0,finish\nmov x27,x0\nldr x9,[x28,#16]\ncmp x9,x27\nb.eq rework_header_owner_ready\n'
    s+='ldr x0,[x28,#8]\ncbz x0,rework_header_no_old_copy\nbl 0x223e73c\ncbz x0,rework_header_no_old_copy\nmov x1,xzr\nbl 0x557b2cc\nrework_header_no_old_copy:\n'
    for off in [0,8,24]:s+=f'ldr x0,[x28,#{off}]\ncbz x0,rework_header_release_{off}\nbl 0x223e784\nstr xzr,[x28,#{off}]\nrework_header_release_{off}:\n'
    s+='str x27,[x28,#16]\nstr wzr,[x28,#44]\nrework_header_owner_ready:\ncbz x19,rework_header_fallback\nmov x0,x19\nmov x1,xzr\nmov x2,xzr\nbl 0x5575198\ncbz w0,rework_header_fallback\nldr x0,[x28]\ncbz x0,rework_header_clone\nbl 0x223e73c\ncmp x0,x19\nb.ne rework_header_clone\nldr x0,[x28,#8]\ncbz x0,rework_header_clone\nbl 0x223e73c\ncbz x0,rework_header_clone\nstr x0,[sp]\nb finish\nrework_header_clone:\nmov x0,x19\nmov x1,xzr\nbl 0x5557b04\nmov w25,w0\nmov x0,x19\nmov x1,xzr\nbl 0x5557b40\nmov w26,w0\ncmp w25,#1\nb.lt rework_header_fallback\ncmp w26,#1\nb.lt rework_header_fallback\ncmp w25,#512\nb.gt rework_header_fallback\ncmp w26,#512\nb.gt rework_header_fallback\nmov x0,xzr\nbl 0x2f34138\ncbz x0,rework_header_fallback\nmov x1,x19\nmov w2,w25\nmov w3,w26\nmov x4,xzr\nbl 0x2f43414\ncbz x0,rework_header_fallback\nmov x26,x0\nmov x1,xzr\nbl 0x5559d18\n'+f'bl {checker:#x}\ncbz w0,rework_header_bad_copy\n'
    # Replace only our own retained copy. Destroy is deferred until Unity's
    # frame end, after the caller has installed the replacement texture.
    s+='ldr x0,[x28,#8]\ncbz x0,rework_header_save_copy\nmov x25,x0\nbl 0x223e73c\ncbz x0,rework_header_release_copy\nmov x1,xzr\nbl 0x557b2cc\nrework_header_release_copy:\nmov x0,x25\nbl 0x223e784\nrework_header_save_copy:\nmov x0,x26\nmov w1,#0\nbl 0x223e704\nstr x0,[x28,#8]\nldr x0,[x28]\ncbz x0,rework_header_save_source\nbl 0x223e784\nrework_header_save_source:\nmov x0,x19\nmov w1,#0\nbl 0x223e704\nstr x0,[x28]\nstr wzr,[x28,#40]\nstr wzr,[x28,#44]\nstr x26,[sp]\nb finish\nrework_header_bad_copy:\nmov x0,x26\nmov x1,xzr\nbl 0x557b2cc\nrework_header_fallback:\n'+f'adr x28,{state:#x}\nbl {token:#x}\ncbz x0,finish\nldr x9,[x28,#16]\ncmp x0,x9\nb.ne finish\nmov w9,#1\nstr w9,[x28,#40]\nldr x0,[x28,#8]\ncbz x0,finish\nbl 0x223e73c\ncbz x0,finish\nstr x0,[sp]\nb finish'
    safe=b.routine('life_rework_validated_header_texture',s)
    # This is the actual UIHeroBar.UpdateContent assignment, audited against
    # Sprite.get_texture and CandyImage.ApplyChanges in the original method.
    site=0x2fedcd4;assert bytes(b.blob[b.off(site):b.off(site)+4])==h.asm('str x0,[x8,#0x58]',site)
    s=f'bl {safe:#x}\nstr x0,[sp]\nadr x28,{state:#x}\nldr x0,[x28,#24]\ncbz x0,rework_header_bind\nbl 0x223e73c\ncmp x0,x19\nb.eq finish\nldr x0,[x28,#24]\nbl 0x223e784\nrework_header_bind:\nmov x0,x19\nmov w1,#0\nbl 0x223e704\nstr x0,[x28,#24]\nb finish'
    b.install('life_rework_header_owns_its_pixels',site,s)
    # A stale/bad shared image gets a bounded retry on Unity's frame pump.
    # The last validated header remains visible while the shared image rebuilds.
    s=f'adr x28,{state:#x}\nldr w9,[x28,#40]\ncbz w9,finish\nldr w9,[x28,#44]\ncmp w9,#2\nb.ge finish\nadd w9,w9,#1\nstr w9,[x28,#44]\nbl {token:#x}\nldr x9,[x28,#16]\ncmp x0,x9\nb.ne finish\nldr x0,[x28,#24]\ncbz x0,finish\nbl 0x223e73c\ncbz x0,finish\nmov x19,x0\nmov x1,xzr\nmov x2,xzr\nbl 0x5575198\ncbz w0,finish\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr x27,[x8,#0x80]\ncbz x27,finish\nldr x8,[x27,#0x30]\ncbz x8,finish\nldr x25,[x8,#16]\nmov x0,xzr\nbl 0x2f34138\ncbz x0,finish\nmov x1,x25\nmov x2,xzr\nbl 0x2f4d2d8\nmov x0,x27\nmov x1,xzr\nbl 0x2ca1024\ncbz x0,finish\nmov x1,xzr\nbl 0x2bad908\ncbz x0,finish\nmov x1,xzr\nbl 0x553b564\n'+f'bl {safe:#x}\ncbz x0,finish\nmov x1,x0\nmov x0,x19\nmov x2,xzr\nbl 0x2fede74\nb finish'
    retry=b.routine('life_rework_retry_header_on_unity_thread',s)
    b.chain('life_rework_header_frame_recovery','web_unity_thread_command_pump',f'bl {retry:#x}\nb finish')

def height(b):
    # Earlier family projections could be finalized before the birth/parent
    # pipeline completed. Migrate automatic estimates after a live header exists.
    family=b.old['v51_ensure_family_projection']['stub']
    s=b.ctx('life_v18')+b.get('HeightRevision1104')+'cmp w24,#1104\nb.eq finish\n'+b.get('HeightSource51')+'cmp w24,#2\nb.eq rework_height_explicit\n'+b.set('HeightModel52',0)+b.set('HeightSource51',1)+b.set('AdultHeight',178)+f'bl {family:#x}\n'+b.ctx('life_v18')+b.set('HeightRevision1104',1104)+f'bl {b.old["measurements_at_current_age21"]["stub"]:#x}\nb finish\nrework_height_explicit:\n'+b.set('HeightRevision1104',1104)+'b finish'
    fn=b.routine('life_rework_finalize_live_family_height',s)
    # UIHeroBar.UpdateContent begins only after the real life is shown. Keep
    # the original body and all registers/floating-point arguments intact.
    b.install('life_rework_height_after_life_creation',0x2fedafc,f'bl {fn:#x}\nb finish')
