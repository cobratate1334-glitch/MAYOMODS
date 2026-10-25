"""Retain the existing import-free JNI bridge and add a bounded web mailbox."""
import importlib.util, json, struct, hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('web_previous_jni',ROOT.parent/'native_v54/jni_ui54.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
from schema import MAILBOX,TEXT_BASE,TEXT_WIDTH

def build(output):
    # The retained assembler source is adapted before execution. Every
    # replacement is asserted, and old function bodies remain byte-identical.
    source=(ROOT.parent/'native_v54/jni_ui54.py').read_text()
    extra=r'''
 put('Java_com_chance_bitlifediag_LifeSetupUI_webRead',adr('x8',0xc400)+'cmp w2,#0\nb.lt web_read_bad\ncmp w2,#699\nb.gt web_read_bad\nadd x8,x8,w2,uxtw #2\ndmb ish\nldar w0,[x8]\nret\nweb_read_bad:\nmov w0,#0\nret\n')
 put('Java_com_chance_bitlifediag_LifeSetupUI_webClose',adr('x8',0xc400)+'ldr w9,[x8]\ncmp w9,w2\nb.ne web_close_done\nstr wzr,[x8,#24]\nweb_close_done:\nret\n')
 put('Java_com_chance_bitlifediag_LifeSetupUI_webSubmit',adr('x8',0xc400)+'ldr w9,[x8]\ncmp w9,w2\nb.ne web_submit_bad\nldr w9,[x8,#24]\ncbz w9,web_submit_bad\nldr w9,[x8,#4]\nldr w10,[x8,#8]\ncmp w9,w10\nb.ne web_submit_bad\nadd w10,w10,#1\ncmp w3,w10\nb.ne web_submit_bad\ncmp w4,#1\nb.lt web_submit_bad\ncmp w4,#100\nb.gt web_submit_bad\nstr w4,[x8,#12]\nadd x8,x8,#4\nstlr w3,[x8]\nmov w0,#1\nret\nweb_submit_bad:\nmov w0,#0\nret\n')
 put('Java_com_chance_bitlifediag_LifeSetupUI_webText',pro()+'mov x19,x0\ncmp w2,#0\nb.lt web_text_bad\ncmp w2,#7\nb.gt web_text_bad\n'+adr('x1',0xd000)+'lsl x9,x2,#10\nadd x1,x1,x9\nmov w2,#0\nweb_text_length:\ncmp w2,#511\nb.hs web_text_return\nldrh w9,[x1,w2,uxtw #1]\ncbz w9,web_text_return\nadd w2,w2,#1\nb web_text_length\nweb_text_return:\nmov x0,x19\n'+jni(163)+'b web_text_end\nweb_text_bad:\nmov x0,xzr\nweb_text_end:\n'+epi())
'''
    needle=" exports={name:r['va'] for name,r in routines.items()};exports['mayo21_config']=CONFIG;exports['mayo54_year']=DATA+128"
    assert source.count(needle)==1
    source=source.replace(needle,extra+'\n'+needle+";exports['mayo_web']=0xc400")
    # Export's data section covers only the old config/year data. The new
    # independent section has its own section index and no executable pages.
    source=source.replace("name in ['mayo21_config','mayo54_year']","name in ['mayo21_config','mayo54_year','mayo_web']")
    source=source.replace("4 if name in ['mayo21_config','mayo54_year','mayo_web'] else 3","7 if name=='mayo_web' else 4 if name in ['mayo21_config','mayo54_year'] else 3")
    source=source.replace("12 if name=='mayo54_year' else 28 if name=='mayo21_config' else routines[name]['length']","0x3c00 if name=='mayo_web' else 12 if name=='mayo54_year' else 28 if name=='mayo21_config' else routines[name]['length']")
    source=source.replace("sections.append(('.shstrtab'", "sections.append(('.webdata',1,3,0xc400,0xc400,0x3c00,0,0,8,0));sections.append(('.shstrtab'")
    source=source.replace("[s[0]for s in sections]+['.shstrtab']", "[s[0]for s in sections]+['.webdata','.shstrtab']")
    source=source.replace('0xd000','0x11000').replace('shoff=0xd200','shoff=0x11200')
    # Restore string buffer address in the injected JNI function after the
    # section-table relocation replacement above.
    source=source.replace("adr('x1',0x11000)","adr('x1',0xd000)")
    source=source.replace('0x100+len(dyn),0x100+len(dyn),0x4000','0x4000,0x4000,0x4000')
    source=source.replace('len(sections),7)','len(sections),8)')
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    namespace={'__file__':str(output/'jni_web_generated.py'),'__name__':'web_jni_build'}
    exec(compile(source,str(output/'jni_web_generated.py'),'exec'),namespace)
    result=namespace['build']()
    meta=json.loads((output/'jni_ui21.json').read_text())
    assert meta['exports']['mayo_web']==MAILBOX
    from elftools.elf.elffile import ELFFile
    import io
    e=ELFFile(io.BytesIO(result))
    assert e.get_section_by_name('.webdata')['sh_addr']==MAILBOX
    assert all(not(s['p_flags']&1 and s['p_flags']&2)for s in e.iter_segments()if s['p_type']=='PT_LOAD')
    print('JNI bridge with bounded mailbox built:',len(result))
    return result

if __name__=='__main__':build(sys.argv[1])
