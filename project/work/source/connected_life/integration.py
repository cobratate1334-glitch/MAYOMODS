"""Native integration entry points; every effect targets an audited receiver."""
from native_hooks import h
from native_v42.patch_native42 import ref,ref_init
from native_v45.catalog45 import PLATFORMS

def hooks(b):
 # Period photo and extra-equipment resources are typed Unity Sprites.
 s='cbz x0,finish\nmov x27,x0\nmov x8,x0\n'+h.compare_key('<GFC.life_rework.NewsImage1110>','news_image1110','resource_prefix1110')+'\nnews_image1110:\n'+b.ctx('life_rework')+b.string('NewsImage1110')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\ncbz x0,finish\nmov x27,x0\nresource_prefix1110:\nldr w9,[x27,#16]\ncmp w9,#11\nb.lt finish\n'
 for i,c in enumerate('native1110/'):s+=f'ldrh w9,[x27,#{20+2*i}]\ncmp w9,#{ord(c)}\nb.ne finish\n'
 s+=ref_init(0x5c56ad8)+'mov x0,x27\n'+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,finish\nstr x0,[sp]\nb return_custom'
 b.chain('connected_typed_photo_and_equipment_resources','immersion1109_typed_sprite_resources',s,ret=True)
 # The original return address belongs to the containing menu method, not a
 # stand-alone function. Reuse each audited custom_resume for pre-2010 exits.
 year=b.old['v45_current_year']['stub']
 for name in PLATFORMS:
  old=b.old['life_rework_social_'+name];assert old.get('custom_resume')
  b.install('connected_social_2010_floor_'+name,old['site'],f'bl {year:#x}\ncmp w0,#2010\nb.lt return_custom\nb finish',custom_resume=old['custom_resume'])
 # Direct routes and old saved continuations are gated too, not just the menu.
 prefix='scenario.lifeRework.live_';s='cbz x2,finish\nmov x27,x2\nldr w9,[x27,#16]\n'+f'cmp w9,#{len(prefix)}\nb.lt finish\n'
 for i,c in enumerate(prefix):s+=f'ldrh w9,[x27,#{20+2*i}]\ncmp w9,#{ord(c)}\nb.ne finish\n'
 s+=f'bl {year:#x}\ncmp w0,#2010\nb.lt social_locked1110\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,social_locked1110\nldr w9,[x8,#0x20]\ncmp w9,#13\nb.ge finish\nsocial_locked1110:\n'+b.string('scenario.lifeRework.social_closed1110')+'str x0,[sp,#16]\nb finish'
 b.chain('connected_saved_live_route_gate','v47_bind_native_scenario',s)
 # Typed gameplay, benefits and original scenario returns are installed after
 # their helper routines have been defined.
 from connected_life.effects import hooks as effects
 from connected_life.service import hooks as service
 effects(b);service(b)
 from connected_life.entry_gates import hooks as gates
 gates(b)
 from connected_life.annual_animation import hooks as animations
 animations(b)
