"""Extend the proven import-free mailbox. No Java thread enters IL2CPP."""
import hashlib,io,json,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'web_experience'))
from elftools.elf.elffile import ELFFile
from keystone import Ks,KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN
from web_experience.jni_web import build as prior
from native_v54.jni_ui54 import adr,pro as old_pro,epi as old_epi,jni
def pro():return old_pro()+'stp x28,x27,[sp,#0x70]\n'
def epi():return 'ldp x28,x27,[sp,#0x70]\n'+old_epi()

BOX=0x14000
TEXT=[0x15000,0x15400,0x15800,0x15c00,0x16000,0x16400,0x16800,0x16c00,0x18000,0x20000,0x28000,0x30000,0x38000,0x40000]
WIDTH=[512]*8+[16384,16384,2048,16384,16384,2048]
PNG=0x48000;END=0x180000

def build(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);raw=prior(out/'previous')
    old=json.loads((out/'previous/jni_ui21.json').read_text());e=ELFFile(io.BytesIO(raw))
    code=dict(old['routines']);exports=dict(old['exports']);blob=bytearray(raw);ks=Ks(KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN)
    cursor=(max(r['va']+r['length']for r in code.values())+15)&~15
    def put(name,source):
        nonlocal cursor
        data=bytes(ks.asm(source,addr=cursor)[0]);blob[cursor:cursor+len(data)]=data
        code[name]=dict(va=cursor,source=source,length=len(data));exports[name]=cursor;cursor=(cursor+len(data)+15)&~15
    pre='Java_com_chance_bitlifediag_MilitaryBridge_'
    put(pre+'read',adr('x8',BOX)+'cmp w2,#0\nb.lt read_bad1108\ncmp w2,#127\nb.gt read_bad1108\nadd x8,x8,w2,uxtw #2\nldar w0,[x8]\nret\nread_bad1108:\nmov w0,#0\nret')
    source=pro()+'mov x19,x0\n'
    for i,(address,width)in enumerate(zip(TEXT,WIDTH)):
        source+=f'cmp w2,#{i}\nb.ne text_next1108_{i}\n'+adr('x1',address)+f'mov w20,#{width-1}\nb text_length1108\ntext_next1108_{i}:\n'
    source+='mov x0,xzr\nb text_end1108\ntext_length1108:\nmov w2,#0\ntext_loop1108:\ncmp w2,w20\nb.hs text_return1108\nldrh w9,[x1,w2,uxtw #1]\ncbz w9,text_return1108\nadd w2,w2,#1\nb text_loop1108\ntext_return1108:\nmov x0,x19\n'+jni(163)+'text_end1108:\n'+epi();put(pre+'text',source)
    # Static submit(env,klass,epoch,serial,command,state,chess,journal). Java
    # has one UI writer; Unity acknowledges before another write is accepted.
    source=pro()+'mov x19,x0\nmov x20,x5\nmov x21,x6\nmov x22,x7\nmov w23,w3\nmov w24,w4\n'+adr('x25',BOX)+'ldr w9,[x25]\ncmp w9,w2\nb.ne submit_bad1108\nldr w9,[x25,#24]\ncbz w9,submit_bad1108\nldr w9,[x25,#4]\nldr w10,[x25,#8]\ncmp w9,w10\nb.ne submit_bad1108\nadd w10,w10,#1\ncmp w23,w10\nb.ne submit_bad1108\ncmp w24,#1\nb.lt submit_bad1108\ncmp w24,#5\nb.gt submit_bad1108\n'
    for i,(reg,address,limit)in enumerate(zip(['x20','x21','x22'],TEXT[11:14],WIDTH[11:14])):
        source+=f'mov x0,x19\nmov x1,{reg}\ncbz x1,submit_bad1108\n'+jni(164)+f'cmp w0,#{limit-1}\nb.hi submit_bad1108\n'
        # >4095 immediate is rewritten below. Copy through GetStringChars and
        # release before any next JNI operation; no Java pointer is retained.
        source+=f'mov w26,w0\nmov x0,x19\nmov x1,{reg}\nmov x2,xzr\n'+jni(165)+'cbz x0,submit_bad1108\nmov x27,x0\n'+adr('x9',address)+f'mov w10,#0\nsubmit_copy1108_{i}:\ncmp w10,w26\nb.hs submit_copy_end1108_{i}\nldrh w11,[x27,w10,uxtw #1]\nstrh w11,[x9,w10,uxtw #1]\nadd w10,w10,#1\nb submit_copy1108_{i}\nsubmit_copy_end1108_{i}:\nstrh wzr,[x9,w10,uxtw #1]\nmov x0,x19\nmov x1,{reg}\nmov x2,x27\n'+jni(166)
    source+='str w24,[x25,#12]\nadd x9,x25,#4\nstlr w23,[x9]\nmov w0,#1\nb submit_end1108\nsubmit_bad1108:\nmov w0,#0\nsubmit_end1108:\n'+epi()
    import re
    source=re.sub(r'cmp w0,#(\d+)',lambda m:'mov w9,#'+m[1]+'\ncmp w0,w9'if int(m[1])>4095 else m[0],source)
    put(pre+'submit',source)
    put(pre+'close',adr('x8',BOX)+'ldr w9,[x8]\ncmp w9,w2\nb.ne close_done1108\nstr wzr,[x8,#24]\nclose_done1108:\nret')
    put(pre+'portrait',pro()+'mov x19,x0\n'+adr('x20',BOX)+'ldr w21,[x20,#72]\ncbz w21,portrait_bad1108\nmov w9,#0x80000\ncmp w21,w9\nb.hi portrait_bad1108\nmov w1,w21\n'+jni(176)+'cbz x0,portrait_bad1108\nmov x22,x0\nmov x0,x19\nmov x1,x22\nmov w2,#0\nmov w3,w21\n'+adr('x4',PNG)+jni(208)+'mov x0,x22\nb portrait_end1108\nportrait_bad1108:\nmov x0,xzr\nportrait_end1108:\n'+epi())

    # New data staging never creates a Window/View or calls a Unity API.
    stage=pro()+'mov x19,x0\nmov w20,w2\nmov w21,w3\nmov w22,w4\nmov w23,w5\nmov x24,x6\n'+adr('x25',BOX)+'ldr w9,[x25]\ncmp w9,w20\nb.ne stage_bad1109\nldr w9,[x25,#24]\ncbz w9,stage_bad1109\nldr w9,[x25,#4]\nldr w10,[x25,#8]\ncmp w9,w10\nb.ne stage_bad1109\nadd w9,w10,#1\ncmp w21,w9\nb.ne stage_bad1109\ncbz x24,stage_bad1109\nmov x0,x19\nmov x1,x24\n'+jni(164)+'mov w9,#32760\ncmp w0,w9\nb.hi stage_bad1109\nmov w26,w0\nmov x0,x19\nmov x1,x24\nmov x2,xzr\n'+jni(165)+'cbz x0,stage_bad1109\nmov x27,x0\n'
    stage+=adr('x9',0xc9000)+'mov w10,#0\nmov w11,#0\nmov w12,#0\nstage_loop1109:\ncmp w10,w26\nb.hs stage_done1109\nldrh w13,[x27,w10,uxtw #1]\nadd w10,w10,#1\ncmp w13,#31\nb.eq stage_field_end1109\nmov w14,#4095\ncmp w12,w14\nb.hs stage_truncate1109\nstrh w13,[x9,w12,uxtw #1]\nadd w12,w12,#1\nb stage_loop1109\nstage_truncate1109:\nb stage_loop1109\nstage_field_end1109:\nstrh wzr,[x9,w12,uxtw #1]\nadd w11,w11,#1\ncmp w11,#8\nb.hs stage_done1109\nadd x9,x9,#2,lsl #12\nmov w12,#0\nb stage_loop1109\nstage_done1109:\ncmp w11,#8\nb.hs stage_release1109\nstrh wzr,[x9,w12,uxtw #1]\nadd w11,w11,#1\nstage_zero1109:\ncmp w11,#8\nb.hs stage_release1109\nadd x9,x9,#2,lsl #12\nstrh wzr,[x9]\nadd w11,w11,#1\nb stage_zero1109\nstage_release1109:\nmov x0,x19\nmov x1,x24\nmov x2,x27\n'+jni(166)+'str w22,[x25,#148]\nstr w23,[x25,#156]\nadd x9,x25,#144\nstlr w21,[x9]\nmov w0,#1\nb stage_return1109\nstage_bad1109:\nmov w0,#0\nstage_return1109:\n'+epi()
    put(pre+'stage',stage)
    upload=pro()+'mov x19,x0\nmov w20,w2\nmov w21,w3\nmov x22,x4\n'+adr('x23',BOX)+'ldr w9,[x23]\ncmp w9,w20\nb.ne upload_bad1109\ncbz x22,upload_bad1109\nmov x1,x22\n'+jni(171)+'mov w24,w0\nmov w9,#0x80000\ncmp w24,w9\nb.hi upload_bad1109\ncbz w24,upload_bad1109\nmov x0,x19\nmov x1,x22\nmov w2,#0\nmov w3,w24\n'+adr('x4',0xe0000)+jni(200)+'mov x0,x19\n'+jni(228)+'cbnz w0,upload_clear1109\nstr w24,[x23,#164]\nstr w21,[x23,#160]\nmov w0,#1\nb upload_done1109\nupload_clear1109:\nmov x0,x19\n'+jni(17)+'upload_bad1109:\nmov w0,#0\nupload_done1109:\n'+epi()
    put(pre+'upload',upload)
    assert cursor<0xc000
    exports['mayo_military']=BOX
    dynstr=bytearray(b'\0');names={}
    for name in exports:names[name]=len(dynstr);dynstr+=name.encode()+b'\0'
    soname=len(dynstr);dynstr+=b'libmayo21.so\0';strva=0x800;symva=(strva+len(dynstr)+15)&~15;sym=bytearray(24)
    data_names=['mayo21_config','mayo54_year','mayo_web','mayo_military']
    for name,va in exports.items():
        index=8 if name=='mayo_military'else 7 if name=='mayo_web'else 4 if name in data_names else 3
        size=END-BOX if name=='mayo_military'else 0x3c00 if name=='mayo_web'else 12 if name=='mayo54_year'else 28 if name=='mayo21_config'else code[name]['length']
        sym+=struct.pack('<IBBHQQ',names[name],0x11 if name in data_names else 0x12,0,index,va,size)
    count=len(exports)+1;hashva=(symva+len(sym)+15)&~15;hashdata=struct.pack('<II',1,count)+struct.pack('<I',1)+struct.pack('<'+str(count)+'I',0,*range(2,count),0)
    assert hashva+len(hashdata)<0x2000
    blob[strva:strva+len(dynstr)]=dynstr;blob[symva:symva+len(sym)]=sym;blob[hashva:hashva+len(hashdata)]=hashdata
    dyn=b''.join(struct.pack('<QQ',t,v)for t,v in [(4,hashva),(5,strva),(6,symva),(10,len(dynstr)),(11,24),(14,soname),(0,0)])
    blob[0xc100:0xc100+len(dyn)]=dyn
    # New, separate 16KB-aligned writable mapping. Old web/config locations and
    # every old executable routine remain exactly where existing patches expect.
    ph=list(e.iter_segments());ph.append(dict(p_type='PT_LOAD',p_flags=6,p_offset=BOX,p_vaddr=BOX,p_paddr=BOX,p_filesz=END-BOX,p_memsz=END-BOX,p_align=0x4000))
    shoff=END+0x400;blob.extend(b'\0'*(shoff+640-len(blob)))
    struct.pack_into('<Q',blob,40,shoff);struct.pack_into('<H',blob,56,7);struct.pack_into('<H',blob,60,10);struct.pack_into('<H',blob,62,9)
    types={'PT_PHDR':6,'PT_LOAD':1,'PT_DYNAMIC':2,'PT_GNU_STACK':0x6474e551}
    for i,s in enumerate(ph):
        size=7*56 if s['p_type']=='PT_PHDR'else s['p_filesz'];mem=7*56 if s['p_type']=='PT_PHDR'else s['p_memsz']
        struct.pack_into('<IIQQQQQQ',blob,64+i*56,types[s['p_type']],s['p_flags'],s['p_offset'],s['p_vaddr'],s['p_paddr'],size,mem,s['p_align'])
    sections=[('',0,0,0,0,0,0,0,0,0),('.dynstr',3,2,strva,strva,len(dynstr),0,0,1,0),('.dynsym',11,2,symva,symva,len(sym),1,1,8,24),('.text',1,6,0x4000,0x4000,cursor-0x4000,0,0,16,0),('.data',1,3,0xc000,0xc000,140,0,0,8,0),('.dynamic',6,3,0xc100,0xc100,len(dyn),1,0,8,16),('.hash',5,2,hashva,hashva,len(hashdata),2,0,4,4),('.webdata',1,3,0xc400,0xc400,0x3c00,0,0,8,0),('.military',1,3,BOX,BOX,END-BOX,0,0,8,0)]
    strings=bytearray(b'\0');offsets={}
    for name in [x[0]for x in sections]+['.shstrtab']:offsets[name]=len(strings);strings+=name.encode()+b'\0'
    sections.append(('.shstrtab',3,0,0,END,len(strings),0,0,1,0));blob[END:END+len(strings)]=strings
    for i,(name,*values)in enumerate(sections):struct.pack_into('<IIQQQQIIQQ',blob,shoff+i*64,offsets[name],*values)
    for name,r in old['routines'].items():assert blob[r['va']:r['va']+r['length']]==raw[r['va']:r['va']+r['length']]
    result=bytes(blob);(out/'libmayo21.so').write_bytes(result);(out/'jni.json').write_text(json.dumps(dict(routines=code,exports=exports,sha256=hashlib.sha256(result).hexdigest(),preserved_old_routines=True),indent=2)+'\n');return result

if __name__=='__main__':build(sys.argv[1])
