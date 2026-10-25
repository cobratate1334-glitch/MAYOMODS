"""Small import-free, position-independent ARM64 JNI bridge.

The bridge owns writable settings. It does not store Unity controller pointers,
call back into New Life, or introduce an Android activity or permission.
"""
import struct,json,hashlib
from pathlib import Path
from keystone import Ks,KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
ks=Ks(KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN)
DATA=0xc000;CONFIG=DATA+32
def adr(reg,va):return f'adrp {reg},{va&~4095:#x}\nadd {reg},{reg},#{va&4095}\n'
def pro():return 'sub sp,sp,#0x80\nstp x29,x30,[sp,#0x20]\nstp x20,x19,[sp,#0x30]\nstp x22,x21,[sp,#0x40]\nstp x24,x23,[sp,#0x50]\nstp x26,x25,[sp,#0x60]\n'
def epi():return 'ldp x26,x25,[sp,#0x60]\nldp x24,x23,[sp,#0x50]\nldp x22,x21,[sp,#0x40]\nldp x20,x19,[sp,#0x30]\nldp x29,x30,[sp,#0x20]\nadd sp,sp,#0x80\nret\n'
def jni(index):return f'ldr x8,[x19]\nldr x8,[x8,#{index*8}]\nblr x8\n'
def build():
 strings={};string_cursor=0x2000
 def string(value):
  nonlocal string_cursor
  if value not in strings:strings[value]=string_cursor;string_cursor+=len(value.encode())+1
  return strings[value]
 class_name=string('com/chance/bitlifediag/LifeSetupUI');method_name=string('dispatch');signature=string('(I)V')
 routines={};cursor=0x4000;code={}
 def put(name,source):
  nonlocal cursor
  encoded=bytes(ks.asm(source,addr=cursor)[0]);routines[name]=dict(va=cursor,source=source,length=len(encoded));code[cursor]=encoded;cursor=(cursor+len(encoded)+15)&~15
 # Loading on the app main thread gives FindClass the correct dex class loader.
 load=pro()+adr('x25',DATA)+'str x0,[x25]\nmov x20,x0\nldr x8,[x20]\nldr x8,[x8,#48]\nadd x1,sp,#8\nmov w2,#6\nmovk w2,#1,lsl #16\nblr x8\ncbnz w0,load_fail\nldr x19,[sp,#8]\ncbz x19,load_fail\nmov x0,x19\n'+adr('x1',class_name)+jni(6)+'cbz x0,load_exception\nmov x21,x0\nmov x1,x0\nmov x0,x19\n'+jni(21)+'cbz x0,load_exception\nstr x0,[x25,#8]\nmov x1,x21\nmov x0,x19\n'+jni(23)+'mov x0,x19\nldr x1,[x25,#8]\n'+adr('x2',method_name)+adr('x3',signature)+jni(113)+'str x0,[x25,#16]\ncbz x0,load_exception\nmov w0,#6\nmovk w0,#1,lsl #16\nb load_done\nload_exception:\nmov x0,x19\n'+jni(17)+'load_fail:\nmov w0,#-1\nload_done:\n'+epi()
 put('JNI_OnLoad',load)
 ui=pro()+'mov w24,w0\n'+adr('x25',DATA)+'ldr x20,[x25]\ncbz x20,ui_done\nldr x8,[x25,#8]\ncbz x8,ui_done\nldr x8,[x25,#16]\ncbz x8,ui_done\nmov x0,x20\nldr x8,[x20]\nldr x8,[x8,#48]\nadd x1,sp,#8\nmov w2,#6\nmovk w2,#1,lsl #16\nblr x8\nmov w26,#0\ncbz w0,ui_env\nmov x0,x20\nldr x8,[x20]\nldr x8,[x8,#32]\nadd x1,sp,#8\nmov x2,xzr\nblr x8\ncbnz w0,ui_done\nmov w26,#1\nui_env:\nldr x19,[sp,#8]\ncbz x19,ui_detach\nstr xzr,[sp]\nstr w24,[sp]\nmov x0,x19\nldr x1,[x25,#8]\nldr x2,[x25,#16]\nmov x3,sp\n'+jni(143)+'mov x0,x19\n'+jni(228)+'cbz w0,ui_detach\nmov x0,x19\n'+jni(17)+'ui_detach:\ncbz w26,ui_done\nmov x0,x20\nldr x8,[x20]\nldr x8,[x8,#40]\nblr x8\nui_done:\n'+epi()
 put('mayo21_ui',ui)
 # Static JNI methods: x0 env, x1 class, w2 first argument.
 read=adr('x8',CONFIG)+'cmp w2,#0\nb.lt read_bad\ncmp w2,#6\nb.gt read_bad\nldr w0,[x8,w2,uxtw #2]\nret\nread_bad:\nmov w0,#0\nret\n'
 put('Java_com_chance_bitlifediag_LifeSetupUI_read',read)
 configure=adr('x8',CONFIG)
 for reg,offset,low,high in [('w2',4,140,235),('w3',8,40,180),('w4',12,-10,20),('w5',16,0,7),('w6',20,0,8),('w7',24,0,7)]:configure+=f'mov w9,#{low}\ncmp {reg},w9\ncsel {reg},{reg},w9,ge\nmov w9,#{high}\ncmp {reg},w9\ncsel {reg},{reg},w9,le\nstr {reg},[x8,#{offset}]\n'
 configure+='mov w9,#1\nstr w9,[x8]\nret\n';put('Java_com_chance_bitlifediag_LifeSetupUI_configure',configure)
 put('mayo21_reset',adr('x8',CONFIG)+'str wzr,[x8]\nmov w9,#178\nstr w9,[x8,#4]\nmov w9,#72\nstr w9,[x8,#8]\nmov w9,#2\nstr w9,[x8,#12]\nstr wzr,[x8,#16]\nstr wzr,[x8,#20]\nstr wzr,[x8,#24]\nret\n')
 put('Java_com_chance_bitlifediag_LifeSetupUI_submitBirthYear',adr('x8',DATA+128)+'str w2,[x8]\nstr w3,[x8,#4]\nret\n')
 exports={name:r['va'] for name,r in routines.items()};exports['mayo21_config']=CONFIG;exports['mayo54_year']=DATA+128
 dynstr=bytearray(b'\0');name_offsets={}
 for name in exports:name_offsets[name]=len(dynstr);dynstr+=name.encode()+b'\0'
 soname=len(dynstr);dynstr+=b'libmayo21.so\0';dynstr_va=0x800
 sym_va=(dynstr_va+len(dynstr)+15)&~15;sym=bytearray(24)
 for name,va in exports.items():sym+=struct.pack('<IBBHQQ',name_offsets[name],0x11 if name in ['mayo21_config','mayo54_year'] else 0x12,0,4 if name in ['mayo21_config','mayo54_year'] else 3,va,12 if name=='mayo54_year' else 28 if name=='mayo21_config' else routines[name]['length'])
 count=len(exports)+1;hash_va=(sym_va+len(sym)+15)&~15
 # One bucket is enough for seven exports; Android's linker follows the chain.
 hash_table=struct.pack('<II',1,count)+struct.pack('<I',1)+struct.pack('<'+str(count)+'I',0,*range(2,count),0)
 dynamic=[(4,hash_va),(5,dynstr_va),(6,sym_va),(10,len(dynstr)),(11,24),(14,soname),(0,0)]
 dyn=bytes().join(struct.pack('<QQ',tag,value)for tag,value in dynamic)
 sections=[('',0,0,0,0,0,0,0,0,0),('.dynstr',3,2,dynstr_va,dynstr_va,len(dynstr),0,0,1,0),('.dynsym',11,2,sym_va,sym_va,len(sym),1,1,8,24),('.text',1,6,0x4000,0x4000,cursor-0x4000,0,0,16,0),('.data',1,3,DATA,DATA,140,0,0,8,0),('.dynamic',6,3,DATA+0x100,DATA+0x100,len(dyn),1,0,8,16),('.hash',5,2,hash_va,hash_va,len(hash_table),2,0,4,4)]
 shstr=bytearray(b'\0');shnames={}
 for name in [s[0]for s in sections]+['.shstrtab']:
  if name:shnames[name]=len(shstr);shstr+=name.encode()+b'\0'
 sections.append(('.shstrtab',3,0,0,0xd000,len(shstr),0,0,1,0));shoff=0xd200
 blob=bytearray(shoff+64*len(sections))
 ident=b'\x7fELF\x02\x01\x01'+b'\0'*9
 blob[:64]=struct.pack('<16sHHIQQQIHHHHHH',ident,3,183,1,0,64,shoff,0,64,56,6,64,len(sections),7)
 phdrs=[(6,4,64,64,64,6*56,6*56,8),(1,4,0,0,0,0x4000,0x4000,0x4000),(1,5,0x4000,0x4000,0x4000,0x8000,0x8000,0x4000),(1,6,DATA,DATA,DATA,0x100+len(dyn),0x100+len(dyn),0x4000),(2,6,DATA+0x100,DATA+0x100,DATA+0x100,len(dyn),len(dyn),8),(0x6474e551,6,0,0,0,0,0,16)]
 for n,row in enumerate(phdrs):blob[64+n*56:64+(n+1)*56]=struct.pack('<IIQQQQQQ',*row)
 blob[dynstr_va:dynstr_va+len(dynstr)]=dynstr;blob[sym_va:sym_va+len(sym)]=sym;blob[hash_va:hash_va+len(hash_table)]=hash_table
 for value,va in strings.items():blob[va:va+len(value.encode())+1]=value.encode()+b'\0'
 for va,encoded in code.items():blob[va:va+len(encoded)]=encoded
 blob[CONFIG:CONFIG+28]=struct.pack('<7i',0,178,72,2,0,0,0);blob[DATA+0x100:DATA+0x100+len(dyn)]=dyn;blob[0xd000:0xd000+len(shstr)]=shstr
 for n,(name,*section)in enumerate(sections):blob[shoff+n*64:shoff+(n+1)*64]=struct.pack('<IIQQQQIIQQ',shnames.get(name,0),*section)
 result=bytes(blob);(ROOT/'libmayo21.so').write_bytes(result)
 (ROOT/'jni_ui21.json').write_text(json.dumps(dict(routines=routines,exports=exports,data=DATA,config=CONFIG,sha256=hashlib.sha256(result).hexdigest()),indent=2))
 return result
if __name__=='__main__':print(len(build()))
