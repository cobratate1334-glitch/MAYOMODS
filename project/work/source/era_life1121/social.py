"""Date-specific row themes on the existing native social platform screens."""
import struct
from native_hooks import h
from life_repair.bridges import allocate
from native_v45.patch_native45 import imm

def colors(platform,era,dark=False):
 if dark:return ['#242930','#f1f4f8','#bdcad9']
 back=['#e9e9e9','#ffffff','#f5f7fa'][era]
 primary=['#315d99','#2476ac','#d52222'][platform]
 if era==0:primary='#0645ad'
 return [back,primary,'#56616d']

def install(b,year):
 # ListItem.CustomTheme is a real CustomTheme reference at +120. Its native
 # three-argument ctor takes background/foreground COLOR_TYPE IDs and an icon.
 # New IDs are handled only here; no selected game or war palette is replaced.
 code='cmp w1,#-1\nb.ne finish\nmov w9,#9600\ncmp w0,w9\nb.lt finish\nmov w9,#9627\ncmp w0,w9\nb.ge finish\nmov w26,w0\n'+f'bl {b.old["v2_selected_dark_theme"]["stub"]:#x}\nmov w27,w0\n'
 def rgba(value):
  s=''
  for i,v in enumerate(bytes.fromhex(value[1:])+b'\xff'):
   n=struct.unpack('<I',struct.pack('<f',v/255))[0];s+=imm('w9',n)+f'str w9,[sp,#{256+i*16}]\n'
  return s+'b return_custom\n'
 for platform in range(3):
  for era in range(3):
   for role,value in enumerate(colors(platform,era)):
    n=9600+(platform*3+era)*3+role;code+=f'mov w9,#{n}\ncmp w26,w9\nb.ne social_color_next_{n}\ncbnz w27,social_color_dark_{n}\n'+rgba(value)+f'social_color_dark_{n}:\n'+rgba(colors(platform,era,True)[role])+f'social_color_next_{n}:\n'
 code+='b finish';b.install('era1121_native_social_color_categories',0x2f62f68,code,ret=True)
 # Only explicit Facebook/Twitter/YouTube item arrays get these references.
 # Original callbacks, scenarios, account IDs, ellipses and disabled gates stay.
 st=b.state+256
 s='cbz x0,finish\ncmp w1,#2\nb.hi finish\nmov x19,x0\nmov w20,w1\n'+f'bl {year:#x}\ncmp w0,#2010\nb.lt finish\nmov w22,#0\ncmp w0,#2013\nb.lt social_era_ready1121\nmov w22,#1\ncmp w0,#2020\nb.lt social_era_ready1121\nmov w22,#2\nsocial_era_ready1121:\nmov w9,#3\nmadd w22,w20,w9,w22\nadr x28,{st:#x}\nadd x28,x28,x22,lsl #3\nldr x0,[x28]\ncbz x0,new_social_theme1121\nbl 0x223e73c\ncbnz x0,social_theme_ready1121\nnew_social_theme1121:\n'+allocate(b,'CustomTheme')+'mov w9,#3\nmul w1,w22,w9\nmov w9,#9600\nadd w1,w1,w9\nadd w2,w1,#1\nmov x3,xzr\nmov x4,xzr\nbl 0x2ec2e44\nmov x0,x25\nmov w1,#0\nbl 0x223e704\nstr x0,[x28]\nmov x0,x25\nsocial_theme_ready1121:\nmov x27,x0\nldr x21,[x19,#0x18]\ncmp x21,#256\nb.hi finish\nmov w22,#0\nsocial_item_loop1121:\ncmp x22,x21\nb.hs finish\nadd x8,x19,#0x20\nldr x0,[x8,x22,lsl #3]\ncbz x0,social_item_next1121\nldr x8,[x0,#0x120]\ncbnz x8,social_item_next1121\nadd x1,x0,#0x120\nmov x2,x27\nbl 0x223e768\nsocial_item_next1121:\nadd w22,w22,#1\nb social_item_loop1121'
 apply=b.routine('era1121_style_native_social_array',s+'\nb finish')
 for name,site,platform in [('Facebook',0x3150024,0),('Twitter',0x3152b3c,1),('YouTube',0x31535d8,2)]:
  b.install('era1121_social_'+name+'_rows',site,f'mov w1,#{platform}\nbl {apply:#x}\nb finish')
