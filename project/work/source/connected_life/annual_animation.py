"""Arm the existing Unity animation only while loading an outbreak news card."""
from native_hooks import h
from native_v42.patch_native42 import ref,ref_init

def hooks(b):
 st=b.states['native_immersion']['va']+512;year=b.old['v45_current_year']['stub']
 s='cbz x2,finish\nmov x8,x2\n'+h.compare_key('scenario.lifeRework.chronicle_notice1110','annual_flight1110','annual_flight_id_next1110')+'\nannual_flight_id_next1110:\n'+h.compare_key('scenario.lifeRework.annual_chronicle1110','annual_flight1110','finish')+'\nannual_flight1110:\n'+f'bl {year:#x}\ncmp w0,#1914\nb.eq annual_first_flight1110\ncmp w0,#1939\nb.ne finish\nmov w25,#2\nb annual_prepare_flight1110\nannual_first_flight1110:\nmov w25,#1\nannual_prepare_flight1110:\nadr x28,{st:#x}\nstr wzr,[x28]\n'
 for offset in [8,24]:s+=f'ldr x0,[x28,#{offset}]\ncbz x0,annual_no_root1110_{offset}\nbl 0x223e784\nstr xzr,[x28,#{offset}]\nannual_no_root1110_{offset}:\n'
 s+=b.ctx('life_rework')+'cmp w25,#1\nb.eq annual_first_path1110\n'+b.text('NewsImage1110','native1109/flight2/0')+b.string('native1109/flight2/')+'b annual_path_ready1110\nannual_first_path1110:\n'+b.text('NewsImage1110','native1109/flight1/0')+b.string('native1109/flight1/')+'annual_path_ready1110:\nmov w1,#0\nbl 0x223e704\nstr x0,[x28,#24]\n'+b.string('NewsImage1110')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\nmov x27,x0\n'+ref_init(0x5c56ad8)+'mov x0,x27\n'+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,finish\nmov x1,xzr\nbl 0x553b564\ncbz x0,finish\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nstr x0,[x28,#8]\nmov w9,#1\nstr w9,[x28]\nb finish'
 b.chain('connected_outbreak_uses_existing_unity_animation','v47_bind_native_scenario',s)
