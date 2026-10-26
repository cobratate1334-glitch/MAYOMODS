"""Typed lookup for the supplied military Sprite resources."""
from native_hooks import h
from native_v42.patch_native42 import ref,ref_init

def hooks(b):
 prefix='mayomods1108/military/'
 s='cbz x0,finish\nmov x27,x0\nldr w9,[x0,#16]\n'+f'cmp w9,#{len(prefix)+1}\nb.lt finish\n'
 for i,c in enumerate(prefix):s+=f'ldrh w9,[x27,#{20+2*i}]\ncmp w9,#{ord(c)}\nb.ne finish\n'
 s+=ref_init(0x5c56ad8)+'mov x0,x27\n'+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,finish\nstr x0,[sp]\nb return_custom'
 b.chain('military1108_typed_sprite_resources','integrity_supplied_sprite_resources',s,ret=True)
