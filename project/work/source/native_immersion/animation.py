"""Use BitLife's AnimationImageSequence on its own report image.
No Android window, input surface, Handler polling or foreign render loop.
"""
from native_hooks import h
from native_v42.patch_native42 import ref,ref_init
from native_ui21 import number
FRAME_COUNT=24
DURATION_MS=7000

def routines(b):
 state=b.state+512
 s=f'adr x28,{state:#x}\nstr wzr,[x28]\n'
 # Preparation is called only on the Unity thread after a projected page.
 for offset in [8,24]:
  s+=f'ldr x0,[x28,#{offset}]\ncbz x0,root_clear1109_{offset}\nbl 0x223e784\nstr xzr,[x28,#{offset}]\nroot_clear1109_{offset}:\n'
 s+=b.immersion_box+'ldr w9,[x28,#148]\ntbz w9,#6,finish\n'+f'adr x28,{state:#x}\n'+b.ctx('life_rework')+b.string('MImage1109')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\ncbz x0,finish\nmov x27,x0\n'
 for n in [1,2]:
  s+='mov x8,x27\n'+h.compare_key('native1109/flight'+str(n)+'/0','prepare_flight1109_'+str(n),'next_flight1109_'+str(n))+f'\nprepare_flight1109_{n}:\n'+b.string('native1109/flight'+str(n)+'/')+'mov w1,#0\nbl 0x223e704\nstr x0,[x28,#24]\nb flight_ready1109\n'+f'next_flight1109_{n}:\n'
 s+='b finish\nflight_ready1109:\n'+ref_init(0x5c56ad8)+'mov x0,x27\n'+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,finish\nmov x1,xzr\nbl 0x553b564\ncbz x0,finish\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nstr x0,[x28,#8]\nmov w9,#1\nstr w9,[x28]\nb finish'
 b.animation_prepare1109=b.routine('immersion1109_prepare_native_flight',s)
 # Called after CandyImage has completed its ordinary construction. The exact
 # frame texture identifies the big report image; normal icons are untouched.
 s=f'cbz x0,finish\nmov x19,x0\nadr x28,{state:#x}\nldr w9,[x28]\ncbz w9,finish\nldr x27,[x19,#0x28]\ncbz x27,finish\nldr x0,[x28,#8]\ncbz x0,finish\nbl 0x223e73c\ncbz x0,finish\nldr x9,[x19,#0x58]\ncmp x9,x0\nb.ne finish\n'
 # A pooled report image can reuse its existing animator. New/replaced images
 # get one component and release the old root, including destroyed wrappers.
 s+='ldr x0,[x28,#16]\ncbz x0,new_animator1109\nbl 0x223e73c\ncbz x0,new_animator1109\nmov x25,x0\nmov x1,xzr\nmov x2,xzr\nbl 0x5575198\ncbz w0,new_animator1109\nldr x9,[x25,#0x30]\ncmp x9,x27\nb.eq animator_ready1109\nnew_animator1109:\nmov x0,x27\nmov x1,xzr\nbl 0x55725ac\ncbz x0,finish\nmov x26,x0\nbl 0x223e48c\ncbz x0,finish\nadr x1,'+f'{b.literal("Assembly-CSharp.dll"):#x}'+'\nbl 0x223e490\ncbz x0,finish\nbl 0x223df90\ncbz x0,finish\nadr x1,'+f'{b.literal(""):#x}'+'\nadr x2,'+f'{b.literal("AnimationImageSequence"):#x}'+'\nbl 0x223dfc8\ncbz x0,finish\nbl 0x223e070\ncbz x0,finish\nbl 0x223e93c\ncbz x0,finish\nmov x1,x0\nmov x0,x26\nmov x2,xzr\nbl 0x5575330\ncbz x0,finish\nmov x25,x0\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nmov x24,x0\nldr x0,[x28,#16]\ncbz x0,keep_animator1109\nbl 0x223e784\nkeep_animator1109:\nstr x24,[x28,#16]\nanimator_ready1109:\n'
 s+='mov x0,x25\nadd x1,x25,#0x30\nmov x2,x27\nbl 0x223e768\n'+'ldr x0,[x28,#24]\ncbz x0,finish\nbl 0x223e73c\ncbz x0,finish\n'+'mov x26,x0\nmov x0,x25\nadd x1,x25,#0x20\nmov x2,x26\nbl 0x223e768\n'
 s+=f'mov w9,#{FRAME_COUNT}\nstr w9,[x25,#0x28]\nmov w9,#{DURATION_MS}\nscvtf s0,w9\nmov w9,#1000\nscvtf s1,w9\nfdiv s0,s0,s1\nstr s0,[x25,#0x38]\nmov w9,#1\nstrb w9,[x25,#0x3d]\nstrb wzr,[x25,#0x3e]\nstr wzr,[x28]\nmov x0,x25\nmov x1,x26\nmov x2,xzr\nbl 0x2ec436c\n'+'b finish'
 b.animation_attach1109=b.routine('attach_existing_unity_animator1109',s)

def hooks(b):
 b.install('immersion1109_native_aircraft_image',0x30275ec,'mov x0,x19\n'+f'bl {b.animation_attach1109:#x}\nb finish')
 s='cbz x0,finish\nmov x19,x0\nmov w24,w1\nldr x8,[x19,#0x20]\ncbz x8,finish\n'
 for n in [1,2]:s+=h.compare_key('native1109/flight'+str(n)+'/','frame1109','next_prefix1109_'+str(n))+'\nnext_prefix1109_'+str(n)+':\n'
 s+='b finish\nframe1109:\ncmp w24,#0\nb.lt frame_no1109\ncmp w24,#24\nb.ge frame_no1109\n'+number(b)+'mov x26,x22\nldr x0,[x19,#0x20]\nmov x1,x26\nmov x2,xzr\nbl 0x4df3450\nmov x27,x0\n'+ref_init(0x5c56ad8)+'mov x0,x27\n'+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,frame_no1109\nmov x25,x0\nldr x0,[x19,#0x30]\ncbz x0,frame_no1109\nmov x1,x25\nmov x2,xzr\nbl 0x568af7c\n'+h.load_game().replace('finish','render_done1109')+'\nmov x0,x8\nmov x1,xzr\nbl 0x2e05ec4\nrender_done1109:\nmov x9,#1\nstr x9,[sp]\nb return_custom\nframe_no1109:\nstr xzr,[sp]\nb return_custom'
 # Chain the first instruction so the original tornado animator remains live.
 b.chain('immersion1109_native_aircraft_frame','v24_native_tornado_frame',s,ret=True)
