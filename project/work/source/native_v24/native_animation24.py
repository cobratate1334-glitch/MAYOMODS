"""Play the supplied transparent frames with Unity's shipped animator.

No Android movie/dialog, overlay, frame polling, or replacement update loop.
Only the matching report's CandyImage receives AnimationImageSequence.
"""
from native_hooks import h
from native_ui21 import number, checkpoint
PREFIX='v24-tornado-'
FRAME_COUNT=120
DURATION_MS=8400

def routines(b):
 state=b.reserve('tornado_animation24',32)
 s=f'adr x28,{state:#x}\nstr wzr,[x28]\nldr w0,[x28,#4]\ncbz w0,no_texture24\nbl 0x223e784\nstr wzr,[x28,#4]\nno_texture24:\n'+b.string(PREFIX+'0')+'mov x1,xzr\nbl 0x2bad908\ncbz x0,finish\nmov x1,xzr\nbl 0x553b564\ncbz x0,finish\nmov w1,#0\nbl 0x223e704\ncbz w0,finish\nstr w0,[x28,#4]\nmov w9,#1\nstr w9,[x28]\n'+checkpoint(b,1200)+'b finish'
 b.animation_prepare24=b.routine('prepare_native_tornado_report24',s)
 # Called after CandyImage has completed its ordinary construction. The exact
 # frame texture identifies the big report image; normal icons are untouched.
 s=f'cbz x0,finish\nmov x19,x0\nadr x28,{state:#x}\nldr w9,[x28]\ncbz w9,finish\nldr x27,[x19,#0x28]\ncbz x27,finish\nldr w0,[x28,#4]\ncbz w0,finish\nbl 0x223e73c\ncbz x0,finish\nldr x9,[x19,#0x58]\ncmp x9,x0\nb.ne finish\n'
 # A pooled report image can reuse its existing animator. New/replaced images
 # get one component and release the old root, including destroyed wrappers.
 s+='ldr w0,[x28,#8]\ncbz w0,new_animator24\nbl 0x223e73c\ncbz x0,new_animator24\nmov x25,x0\nmov x1,xzr\nmov x2,xzr\nbl 0x5575198\ncbz w0,new_animator24\nldr x9,[x25,#0x30]\ncmp x9,x27\nb.eq animator_ready24\nnew_animator24:\nmov x0,x27\nmov x1,xzr\nbl 0x55725ac\ncbz x0,finish\nmov x26,x0\nbl 0x223e48c\ncbz x0,finish\nadr x1,'+f'{b.literal("Assembly-CSharp.dll"):#x}'+'\nbl 0x223e490\ncbz x0,finish\nbl 0x223df90\ncbz x0,finish\nadr x1,'+f'{b.literal(""):#x}'+'\nadr x2,'+f'{b.literal("AnimationImageSequence"):#x}'+'\nbl 0x223dfc8\ncbz x0,finish\nbl 0x223e070\ncbz x0,finish\nbl 0x223e93c\ncbz x0,finish\nmov x1,x0\nmov x0,x26\nmov x2,xzr\nbl 0x5575330\ncbz x0,finish\nmov x25,x0\nmov w1,#0\nbl 0x223e704\ncbz w0,finish\nmov w24,w0\nldr w0,[x28,#8]\ncbz w0,keep_animator24\nbl 0x223e784\nkeep_animator24:\nstr w24,[x28,#8]\nanimator_ready24:\n'
 s+='mov x0,x25\nadd x1,x25,#0x30\nmov x2,x27\nbl 0x223e768\n'+b.string(PREFIX)+'mov x26,x0\nmov x0,x25\nadd x1,x25,#0x20\nmov x2,x26\nbl 0x223e768\n'
 s+=f'mov w9,#{FRAME_COUNT}\nstr w9,[x25,#0x28]\nmov w9,#{DURATION_MS}\nscvtf s0,w9\nmov w9,#1000\nscvtf s1,w9\nfdiv s0,s0,s1\nstr s0,[x25,#0x38]\nmov w9,#1\nstrb w9,[x25,#0x3d]\nstrb wzr,[x25,#0x3e]\nstr wzr,[x28]\nmov x0,x25\nmov x1,x26\nmov x2,xzr\nbl 0x2ec436c\n'+checkpoint(b,1201)+'b finish'
 b.animation_attach24=b.routine('attach_existing_unity_animator24',s)

def hooks(b):
 b.install('v24_native_tornado_image',0x30275ec,'mov x0,x19\n'+f'bl {b.animation_attach24:#x}\nb finish')
 # The stock animator resolves other sequences in UIImageHub. Our frames are
 # registered emoji sprites, so only this prefix uses the emoji asset cache.
 s='cbz x0,finish\nmov x19,x0\nmov w24,w1\nldr x8,[x19,#0x20]\ncbz x8,finish\n'+h.compare_key(PREFIX,'frame24','finish')+'\nframe24:\n'+f'cmp w24,#0\nb.lt frame24_no\ncmp w24,#{FRAME_COUNT}\nb.ge frame24_no\n'+number(b)+'mov x26,x22\nmov x0,[x19,#0x20]\n'
 s=s.replace('mov x0,[x19,#0x20]','ldr x0,[x19,#0x20]')
 s+='mov x1,x26\nmov x2,xzr\nbl 0x4df3450\nmov x1,xzr\nbl 0x2bad908\ncbz x0,frame24_no\nmov x25,x0\nldr x0,[x19,#0x30]\ncbz x0,frame24_no\nmov x1,x25\nmov x2,xzr\nbl 0x568af7c\n'
 # BitLife renders on demand. Match the stock SetFrame render request so the
 # changing Unity sprite appears even while the scenario is otherwise idle.
 s+=h.load_game().replace('finish','frame24_render_done')+'\nmov x0,x8\nmov x1,xzr\nbl 0x2e05ec4\nframe24_render_done:\nmov x9,#1\nstr x9,[sp]\nb return_custom\nframe24_no:\nstr xzr,[sp]\nb return_custom'
 b.install('v24_native_tornado_frame',0x2ec4108,s,ret=True)
