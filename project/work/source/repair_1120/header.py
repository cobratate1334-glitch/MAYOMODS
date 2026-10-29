"""A small period banner on the existing navbar; no journal collage or new UI."""
from native_hooks import h
from native_v42.patch_native42 import ref,ref_init
def install(b):
 st=b.state+128;year=b.states['military_expansion']['va']+68
 # UINavBar.UpdateTheme keeps x19 until its last tail-call. +0x38 is its
 # original CandyImage background. GetTexture/SetTexture preserve stock state.
 s='cbz x0,finish\nldr x21,[x0,#0x38]\ncbz x21,finish\n'+f'adr x28,{st:#x}\nldr x0,[x28]\ncbz x0,new_header1120\nbl 0x223e73c\ncmp x0,x21\nb.eq header_ready1120\n'
 for off in [0,8]:s+=f'ldr x0,[x28,#{off}]\ncbz x0,header_free_next_{off}\nbl 0x223e784\nstr xzr,[x28,#{off}]\nheader_free_next_{off}:\n'
 s+='new_header1120:\nmov x0,x21\nmov w1,#0\nbl 0x223e704\nstr x0,[x28]\nmov x0,x21\nmov x1,xzr\nbl 0x3027fe0\ncbz x0,header_ready1120\nmov w1,#0\nbl 0x223e704\nstr x0,[x28,#8]\nheader_ready1120:\n'+f'adr x8,{year:#x}\nldr w9,[x8]\ncmp w9,#1800\nb.lt restore_header1120\ncmp w9,#1900\nb.ge restore_header1120\nldr x0,[x28,#16]\ncbz x0,load_header1120\nbl 0x223e73c\ncbnz x0,header_sprite_ready1120\nload_header1120:\n'+ref_init(0x5c56ad8)+b.string('native1120/header/1800')+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,restore_header1120\nmov x27,x0\nmov w1,#0\nbl 0x223e704\nstr x0,[x28,#16]\nmov x0,x27\nheader_sprite_ready1120:\nmov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3028114\nmov w9,#1\nstr w9,[x28,#24]\nb finish\nrestore_header1120:\nldr w9,[x28,#24]\ncbz w9,finish\nstr wzr,[x28,#24]\nldr x0,[x28,#8]\ncbz x0,restore_empty_header1120\nbl 0x223e73c\nb restore_texture1120\nrestore_empty_header1120:\nmov x0,xzr\nrestore_texture1120:\nmov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3028250\nb finish'
 helper=b.routine('repair1120_period_header',s)
 # At 0x3017c9c, the original receiver is still x19. The displaced LDR and
 # native tail colour call continue normally; no animation is interrupted.
 b.install('repair1120_header_after_stock_theme',0x3017c9c,f'mov x0,x19\nbl {helper:#x}\nb finish')
