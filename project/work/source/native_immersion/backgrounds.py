"""Illustration on UILifeLog's existing background Image; no extra UI layer."""
from native_hooks import h
from native_v42.patch_native42 import ref,ref_init

def hooks(b):
 st=b.state+256;phase=b.states['military_expansion']['va']+64
 # Runs after the original log scroller background color has been applied.
 # The original Image and Sprite are GC-rooted separately. A new scroller
 # captures its own original Sprite; outside dated themes it is restored.
 s='ldr x20,[x19,#0x30]\ncbz x20,finish\nldr x21,[x20,#0x30]\ncbz x21,finish\n'+f'adr x28,{st:#x}\nldr x0,[x28]\ncbz x0,capture_background1109\nbl 0x223e73c\ncmp x0,x21\nb.eq background_ready1109\nldr x0,[x28]\nbl 0x223e784\nstr xzr,[x28]\nldr x0,[x28,#8]\ncbz x0,capture_background1109\nbl 0x223e784\nstr xzr,[x28,#8]\ncapture_background1109:\nmov x0,x21\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nstr x0,[x28]\nldr x0,[x21,#0xd8]\ncbz x0,background_ready1109\nmov w1,#0\nbl 0x223e704\nstr x0,[x28,#8]\nbackground_ready1109:\nadr x8,{phase:#x}\nldr w25,[x8]\ncbz w25,restore_background1109\n'
 for i,name in enumerate(['ww1','post1','ww2','post2'],1):
  s+=f'cmp w25,#{i}\nb.ne next_background1109_{i}\n'+b.string('native1109/background/'+name)+'b load_background1109\n'+f'next_background1109_{i}:\n'
 s+='b restore_background1109\nload_background1109:\nmov x27,x0\n'+ref_init(0x5c56ad8)+'mov x0,x27\n'+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,restore_background1109\nmov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x568af7c\n'
 # White keeps the supplied artwork's colors. Alpha lets the light paper
 # underlay preserve contrast under scrolling text, even at detailed edges.
 s+='mov x0,x20\nfmov s0,#1.0\nfmov s1,#1.0\nfmov s2,#1.0\nmovz w9,#0x999a\nmovk w9,#0x3e99,lsl #16\nfmov s3,w9\nmov x1,xzr\nbl 0x30274b0\nb finish\nrestore_background1109:\nldr x0,[x28,#8]\ncbz x0,empty_background1109\nbl 0x223e73c\nb restore_sprite1109\nempty_background1109:\nmov x0,xzr\nrestore_sprite1109:\nmov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x568af7c\nb finish'
 b.install('immersion1109_native_journal_background',0x2ff35a8,s)
