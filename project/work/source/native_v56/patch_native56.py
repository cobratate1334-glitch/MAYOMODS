"""Composite authored scar/patch textures into the final readable portrait.

The saved selections remain the existing native accessory records (8/9).
These two custom records use one deterministic bitmap path instead of relying
on the stock accessory scene's handling of out-of-enum accessory types.
"""
import copy, hashlib, io, json, struct, sys
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent
sys.path[:0] = [str(ROOT), str(SOURCE), str(SOURCE / 'native_v29')]
from native_hooks import Builder, h
from native_v55.patch_native55 import Patch as Previous
from native_v42.patch_native42 import ref, ref_init

BASE_SHA = '7a4a37615d9c60962d1e2658d86154199a868d84439026478171fcf0d2f3c288'


class Patch(Previous):
 def __init__(self, raw):
  self.base = json.loads((SOURCE/'native_v55/native_hooks.json').read_text())
  assert hashlib.sha256(raw).hexdigest() == self.base['binary_sha256']
  e = ELFFile(io.BytesIO(raw)); segments = list(e.iter_segments()); count = len(segments)+1
  self.added_off = (len(raw)+0x3fff)&~0x3fff
  self.added_va = (max(s['p_vaddr']+s['p_memsz'] for s in segments if s['p_type']=='PT_LOAD')+0x3fff)&~0x3fff
  self.added_size = 0x20000
  data = bytearray(raw); data.extend(b'\0'*(self.added_off+self.added_size-len(data)))
  phoff = e['e_phoff']; table = bytearray(raw[phoff:phoff+len(segments)*56])
  pi = next(i for i,s in enumerate(segments) if s['p_type']=='PT_PHDR')
  struct.pack_into('<QQ', table, pi*56+32, count*56, count*56)
  table += struct.pack('<IIQQQQQQ',1,5,self.added_off,self.added_va,self.added_va,self.added_size,self.added_size,0x4000)
  assert phoff+len(table) <= self.base['v49_new_rx'][0]+0x1000
  data[phoff:phoff+len(table)] = table; struct.pack_into('<H',data,56,count)
  Builder.__init__(self, bytes(data)); self.before_native = raw
  self.program_ranges = [[56,2],[phoff,len(table)]]
  self.manifest = copy.deepcopy(self.base)
  self.old = {r['name']:r for r in self.base['hooks']+self.base['routines']}
  self.rxoff,self.rxva = self.added_off,self.added_va
  self.tail = next(s for s in self.loads if s['p_vaddr']==self.rxva)
  self.cursor = self.code_start = self.added_va
  self.strings = copy.deepcopy(self.base['strings'])
  self.strings_va = self.string_cursor = self.added_va+0x18000
  self.states = copy.deepcopy(self.base['states'])
  self.hooks=[]; self.routines=[]; self.changed=[]; self.serial=0
  self.snprintf=self.plt('snprintf')

 def finish56(self):
  assert self.cursor < self.strings_va and self.string_cursor < self.added_va+self.added_size
  for value,va in self.strings.items():
   if value in self.base['strings']: continue
   raw=value.encode()+b'\0'; p=self.off(va)
   assert self.blob[p:p+len(raw)]==b'\0'*len(raw)
   self.blob[p:p+len(raw)]=raw; self.changed.append([va,len(raw),'literal'])
  sites={r['site'] for r in self.hooks}
  assert not sites & {r['site'] for r in self.manifest['hooks']}
  self.manifest['hooks']+=self.hooks; self.manifest['routines']+=self.routines
  self.manifest.update(binary_sha256=hashlib.sha256(self.blob).hexdigest(),
   base_v55_native_sha256=hashlib.sha256(self.before_native).hexdigest(),
   v56_new_code_range=[self.code_start,self.cursor],v56_changed_ranges=self.changed,
   v56_program_header_ranges=self.program_ranges,
   v56_added_rx=[self.added_off,self.added_va,self.added_size])
  (ROOT/'native_hooks.json').write_text(json.dumps(self.manifest,indent=2)+'\n')
  return bytes(self.blob)


def blender(b):
 # Inputs: Color32 data, destination W/H, source data/W/H, x/y offset,
 # drawn W/H in w8/w9. All arithmetic is bounded, straight-alpha RGBA.
 s='''str xzr,[sp]
cbz x0,finish
cbz x3,finish
cmp w1,#1
b.lt finish
cmp w1,#512
b.gt finish
cmp w2,#1
b.lt finish
cmp w2,#512
b.gt finish
cmp w4,#1
b.lt finish
cmp w4,#2048
b.gt finish
cmp w5,#1
b.lt finish
cmp w5,#2048
b.gt finish
cmp w8,#1
b.lt finish
cmp w8,#4096
b.gt finish
cmp w9,#1
b.lt finish
cmp w9,#4096
b.gt finish
mov x19,x0
mov w20,w1
mov w21,w2
mov x22,x3
mov w23,w4
mov w24,w5
mov w25,w6
mov w26,w7
mov w27,w8
mov w28,w9
mov w9,#0
mov w10,#0
blend56_row:
sub w0,w10,w26
cmp w0,#0
b.lt blend56_next_row
cmp w0,w28
b.ge blend56_next_row
mul w0,w0,w24
udiv w0,w0,w28
mul w12,w0,w23
mul w13,w10,w20
mov w11,#0
blend56_pixel:
sub w0,w11,w25
cmp w0,#0
b.lt blend56_next_pixel
cmp w0,w27
b.ge blend56_next_pixel
mul w0,w0,w23
udiv w0,w0,w27
add w0,w0,w12
ldr w14,[x22,w0,uxtw #2]
lsr w0,w14,#24
cbz w0,blend56_next_pixel
add w1,w13,w11
add x16,x19,w1,uxtw #2
cmp w0,#255
b.eq blend56_opaque
ldr w15,[x16]
lsr w1,w15,#24
mov w8,#255
sub w2,w8,w0
mul w1,w1,w2
mul w4,w0,w8
add w2,w4,w1
lsr w3,w2,#1
add w17,w2,#127
udiv w17,w17,w8
lsl w17,w17,#24
'''
 for shift in [0,8,16]:
  s+=f'''ubfx w5,w14,#{shift},#8
ubfx w6,w15,#{shift},#8
mul w5,w5,w4
madd w5,w6,w1,w5
add w5,w5,w3
udiv w5,w5,w2
orr w17,w17,w5,lsl #{shift}
'''
 s+='''str w17,[x16]
b blend56_record
blend56_opaque:
str w14,[x16]
blend56_record:
add w9,w9,#1
blend56_next_pixel:
add w11,w11,#1
cmp w11,w20
b.lo blend56_pixel
blend56_next_row:
add w10,w10,#1
cmp w10,w21
b.lo blend56_row
str x9,[sp]
b finish'''
 return b.routine('v56_blend_rgba_overlay',s)


def compositor(b, blend):
 s='''cbz x0,finish
cbz x1,finish
mov x19,x0
mov x20,x1
ldr x8,[x20,#0x20]
cbz x8,finish
mov x0,x20
mov w1,#8
mov x2,xzr
bl 0x2f36824
mov w21,w0
mov w9,#49101
sub w9,w21,w9
cmp w9,#11
csel w21,w21,wzr,ls
mov x0,x20
mov w1,#9
mov x2,xzr
bl 0x2f36824
mov w22,w0
mov w9,#49201
sub w9,w22,w9
cmp w9,#21
csel w22,w22,wzr,ls
orr w9,w21,w22
cbz w9,finish
sub sp,sp,#256
stp xzr,xzr,[sp]
stp xzr,xzr,[sp,#16]
str wzr,[sp,#104]
str w21,[sp,#56]
str w22,[sp,#60]
mov x0,x19
mov w1,#0
bl 0x223e704
str x0,[sp]
cbz x0,composite56_cleanup
mov x0,x19
mov x1,xzr
bl 0x5558c70
cbz w0,composite56_cleanup
mov x0,x19
mov x1,xzr
bl 0x5557b04
cmp w0,#1
b.lt composite56_cleanup
cmp w0,#512
b.gt composite56_cleanup
str w0,[sp,#40]
mov x0,x19
mov x1,xzr
bl 0x5557b40
cmp w0,#1
b.lt composite56_cleanup
cmp w0,#512
b.gt composite56_cleanup
str w0,[sp,#44]
mov x0,x20
mov x1,xzr
bl 0x2f3cd90
cmp w0,#5
b.hi composite56_cleanup
str w0,[sp,#48]
mov x0,x20
mov x1,xzr
bl 0x2f40a9c
cmp w0,#1
b.hi composite56_cleanup
str w0,[sp,#52]
mov x0,x19
mov x1,xzr
bl 0x5559d18
cbz x0,composite56_cleanup
ldr w9,[sp,#40]
ldr w10,[sp,#44]
mul w9,w9,w10
ldr x10,[x0,#24]
cmp x10,x9
b.lo composite56_cleanup
mov w1,#0
bl 0x223e704
str x0,[sp,#8]
cbz x0,composite56_cleanup
mov w28,#0
composite56_layer:
add x8,sp,#56
ldr w21,[x8,w28,uxtw #2]
cbz w21,composite56_next_layer
'''
 s+=ref_init(0x5c56ae0)
 s+='mov x0,sp\nadd x0,x0,#168\nmov w1,#88\n'+f'adr x2,{b.literal("emoji/voltron/accessories/custom49/a49_%05d"):#x}\nmov w3,w21\nbl {b.snprintf:#x}\n'
 s+='add x0,sp,#168\nbl 0x223e8cc\n'+ref(0x5c56ae0,'x1')+'bl 0x3ed1638\n'
 s+='''cbz x0,composite56_next_layer
mov x23,x0
mov w1,#0
bl 0x223e704
str x0,[sp,#16]
cbz x0,composite56_release_layer
mov x0,x23
mov x1,xzr
bl 0x5558c70
cbz w0,composite56_release_layer
mov x0,x23
mov x1,xzr
bl 0x5557b04
cmp w0,#1
b.lt composite56_release_layer
cmp w0,#2048
b.gt composite56_release_layer
str w0,[sp,#72]
mov x0,x23
mov x1,xzr
bl 0x5557b40
cmp w0,#1
b.lt composite56_release_layer
cmp w0,#2048
b.gt composite56_release_layer
str w0,[sp,#76]
mov x0,x23
mov x1,xzr
bl 0x5559d18
cbz x0,composite56_release_layer
ldr w9,[sp,#72]
ldr w10,[sp,#76]
mul w9,w9,w10
ldr x10,[x0,#24]
cmp x10,x9
b.lo composite56_release_layer
mov w1,#0
bl 0x223e704
str x0,[sp,#24]
cbz x0,composite56_release_layer
add x0,sp,#128
str w21,[x0,#0x14]
ldr w1,[sp,#52]
ldr w2,[sp,#48]
'''
 s+=f'bl {b.old["v49_accessory_scale"]["stub"]:#x}\nstr s0,[sp,#80]\nstr s1,[sp,#84]\nadd x0,sp,#128\nldr w1,[sp,#52]\nldr w2,[sp,#48]\nbl {b.old["v49_accessory_position"]["stub"]:#x}\n'
 s+='''ldr w9,[sp,#40]
ldr w10,[sp,#44]
scvtf s2,w9
scvtf s3,w10
ldr s4,[sp,#80]
ldr s5,[sp,#84]
fmul s4,s4,s2
fmul s5,s5,s3
fcvtns w9,s4
fcvtns w10,s5
str w9,[sp,#88]
str w10,[sp,#92]
scvtf s4,w9
scvtf s5,w10
fmov s6,#0.5
fmul s4,s4,s6
fmul s5,s5,s6
fmul s0,s0,s2
fsub s0,s0,s4
fmov s6,#1.0
fsub s1,s6,s1
fmul s1,s1,s3
fsub s1,s1,s5
fcvtns w9,s0
fcvtns w10,s1
str w9,[sp,#96]
str w10,[sp,#100]
ldr x0,[sp,#8]
bl 0x223e73c
cbz x0,composite56_release_layer
add x27,x0,#32
ldr x0,[sp,#24]
bl 0x223e73c
cbz x0,composite56_release_layer
add x3,x0,#32
mov x0,x27
ldr w1,[sp,#40]
ldr w2,[sp,#44]
ldr w4,[sp,#72]
ldr w5,[sp,#76]
ldr w6,[sp,#96]
ldr w7,[sp,#100]
ldr w8,[sp,#88]
ldr w9,[sp,#92]
'''
 s+=f'bl {blend:#x}\ncbz w0,composite56_release_layer\nldr w9,[sp,#104]\nadd w9,w9,#1\nstr w9,[sp,#104]\n'
 s+='''composite56_release_layer:
ldr x0,[sp,#24]
cbz x0,composite56_release_texture
bl 0x223e784
str xzr,[sp,#24]
composite56_release_texture:
ldr x0,[sp,#16]
cbz x0,composite56_next_layer
bl 0x223e784
str xzr,[sp,#16]
composite56_next_layer:
add w28,w28,#1
cmp w28,#2
b.lo composite56_layer
ldr w9,[sp,#104]
cbz w9,composite56_cleanup
ldr x0,[sp,#8]
bl 0x223e73c
mov x27,x0
cbz x27,composite56_cleanup
ldr x0,[sp]
bl 0x223e73c
mov x19,x0
cbz x19,composite56_cleanup
mov x1,x27
mov x2,xzr
mov x3,xzr
bl 0x555a634
mov x0,x19
mov w1,#1
mov w2,#0
mov x3,xzr
bl 0x555a4a8
composite56_cleanup:
'''
 for off in [24,16,8,0]:
  s+=f'ldr x0,[sp,#{off}]\ncbz x0,composite56_free_{off}\nbl 0x223e784\nstr xzr,[sp,#{off}]\ncomposite56_free_{off}:\n'
 s+='add sp,sp,#256\nb finish'
 return b.routine('v56_composite_saved_scar_and_eyepatch',s)


def patch(raw):
 b=Patch(raw); blend=blender(b); render=compositor(b,blend)
 # This is immediately after the stock container produced its portrait texture;
 # x19 still holds the exact CharacterFace, including draft accessory records.
 b.install('v56_finish_portrait_with_custom_overlays',0x2f3e13c,
  f'mov x1,x19\nbl {render:#x}\nb finish')
 # Avoid drawing either layer twice. Other custom slots and all stock items
 # continue through the original accessory renderer.
 s='''cbz x1,finish
ldr w9,[x1,#0x10]
ldr w10,[x1,#0x14]
cmp w9,#8
b.ne overlay56_patch
mov w11,#49101
sub w10,w10,w11
cmp w10,#11
b.ls return_custom
b finish
overlay56_patch:
cmp w9,#9
b.ne finish
mov w11,#49201
sub w10,w10,w11
cmp w10,#21
b.ls return_custom
b finish'''
 b.install('v56_render_custom_overlays_once',0x2f455b8,s,ret=True)
 return b.finish56()


if __name__=='__main__':
 Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()))
 print('v56 portrait compositor built',flush=True)
