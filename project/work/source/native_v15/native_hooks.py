"""v15 single-pass ranks, shared scoring effect, and custom hair links."""
import io,json,struct,re,hashlib,importlib.util
from pathlib import Path
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('helpers15',ROOT.parent/'native_v8/native_hooks.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
asm,save,restore=h.asm,h.save,h.restore
STATE=0x6306200
SCORES={'soccer_v12':['LastFor','LastAgainst','PenFor','PenAgainst'],'soccer_v11':['LastFor','LastAgainst'],'football_v8':['Goals'],'basketball_v9':['shootScore'],'rugby_v9':['attackScore']}
def patch(native):
 e=ELFFile(io.BytesIO(native));segs=list(e.iter_segments());loads=[s for s in segs if s['p_type']=='PT_LOAD'];tail=loads[-1]
 blob=bytearray(native);cursor=(tail['p_vaddr']+len(native)-tail['p_offset']+4095)&~4095;strings_va=cursor+0x60000;strings={};hooks=[]
 def off(va):
  s=next(s for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']);return s['p_offset']+va-s['p_vaddr']
 def lit(s):
  if s not in strings:strings[s]=strings_va+sum(len(x.encode())+1 for x in strings)
  return strings[s]
 def string(s):return f'adr x0, {lit(s):#x}\nbl {h.NEW_STRING:#x}'
 def get(s,r):return string(s)+f'\nmov x1,x0\nmov x0,x21\nmov w2,#0\nmov x3,xzr\nbl 0x3059ee0\nmov {r},w0\n'
 def put(s,r):return f'str {r},[sp,#0xf8]\n'+string(s)+'\nmov x1,x0\nmov x0,x21\nldr w2,[sp,#0xf8]\nmov x3,xzr\nbl 0x3059f90\n'
 def install(n,site,body,skip=False,ret=False):
  nonlocal cursor
  raw=bytes(blob[off(site):off(site)+4]);ins=list(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(raw,site))[0];orig=ins.mnemonic+' '+ins.op_str.replace('#0x','0x')
  source=save()+'\n'+body+'\nfinish:\n'+restore()+'\n'+orig+f'\nb {site+4:#x}'
  if skip:source+='\nskip_original:\n'+restore()+f'\nb {site+4:#x}'
  if ret:source+='\nreturn_custom:\n'+restore()+'\nret'
  source=re.sub(r'cmp (w\d+), #(\d+)',lambda m:f'mov w10,#{m[2]}\ncmp {m[1]},w10'if int(m[2])>4095 else m[0],source)
  source=source.replace(",0x",", 0x");code=asm(source,cursor);p=tail['p_offset']+cursor-tail['p_vaddr'];blob.extend(b'\0'*max(0,p+len(code)-len(blob)));blob[p:p+len(code)]=code;blob[off(site):off(site)+4]=asm(f'b {cursor:#x}',site)
  hooks.append(dict(name=n,site=site,stub=cursor,resume=site+4,original=orig,source=source,length=len(code)));cursor=(cursor+len(code)+15)&~15
 # A separate already mapped RW page beside the dynamic table holds only UI
 # pointers and a short queue; executable memory remains read/execute.
 rw=next(s for s in loads if s['p_vaddr']==0x6306000);rwheader=e['e_phoff']+segs.index(rw)*56;assert rw['p_filesz']==0x1c0 and rw['p_memsz']==0x1c0;struct.pack_into('<Q',blob,rwheader+40,0x1000)
 install('remember_scenario_manager',0x2f89c0c,f'adr x8,{STATE:#x}\nstr x0,[x8]')
 body='tbz w0,#0,finish\ncbz x19,finish\ncbz x21,finish\nldr x8,[x19,#0x18]\ncbz x8,finish\n'+h.compare_key('NativeGroupRank','rank','scores')+'\nscores:\nldr x8,[x21,#0x10]\ncbz x8,finish\n'
 for j,(owner,keys)in enumerate(SCORES.items()):body+=h.compare_key(owner,'owner'+str(j),'o_next'+str(j))+'\no_next'+str(j)+':\n'
 body+='b finish\n'
 for j,(owner,keys)in enumerate(SCORES.items()):
  body+='owner'+str(j)+':\nldr x8,[x19,#0x18]\n'
  for k,key in enumerate(keys):body+=h.compare_key(key,f'score_{j}_{k}',f's_next_{j}_{k}')+f'\ns_next_{j}_{k}:\n'
  body+='b finish\n'
  for k,key in enumerate(keys):
   body+=f'score_{j}_{k}:\n'+get(key,'w24')+get('V15Sound_'+key,'w25')+put('V15Sound_'+key,'w24')+'''sub w26,w24,w25
 cmp w26,#0
 b.le finish
 cmp w26,#24
 mov w9,#24
 csel w26,w26,w9,le
 b enqueue
 '''
 body+='rank:\n'+get('Stage','w24')+'cmp w24,#1\nb.ne finish\n'+get('Phase','w24')+'cmp w24,#11\nb.lt finish\ncmp w24,#14\nb.gt finish\n'+get('T0P','w24')+get('T0GF','w25')+get('T0GA','w26')+'sub w26,w25,w26\nmov w27,#1\n'
 for i in range(1,4):
  body+=get(f'T{i}P','w28')+get(f'T{i}GF','w23')+get(f'T{i}GA','w22')+f'''cmp w28,w24
 b.gt higher{i}
 b.lt lower{i}
 sub w22,w23,w22
 cmp w22,w26
 b.gt higher{i}
 b.lt lower{i}
 cmp w23,w25
 b.lt lower{i}
 higher{i}:
 add w27,w27,#1
 lower{i}:
 '''
 body+=put('GroupRank','w27')+'mov w27,#14\n'+put('Phase','w27')+'b finish\nenqueue:\n'+f'adr x22,{STATE:#x}\nldr x23,[x22]\ncbz x23,finish\nldr w9,[x22,#16]\nadd w9,w9,w26\nmov w10,#96\ncmp w9,w10\ncsel w9,w9,w10,le\nstr w9,[x22,#16]\nldr x9,[x22,#8]\ncbnz x9,finish\nmov x0,x23\nmov w1,#1\nmov w2,#1\nmov x3,xzr\nbl 0x2f8abe0\ncbz x0,finish\nstr x0,[x22,#8]\nmov x1,x0\nldr w9,[x22,#16]\nsub w9,w9,#1\nstr w9,[x22,#16]\nmov x0,x23\nmov x2,xzr\nbl 0x5577470\nb finish'
 install('v15_saved_activity_pulses',0x321b46c,body)
 # Only our own RedAlert iterator repeats. Regular injury animations keep their
 # original behavior; no hero health, NPC health or damage stats are modified.
 body=f'adr x8,{STATE:#x}\nldr x9,[x8,#8]\ncmp x9,x19\nb.ne finish\nldr w9,[x8,#16]\ncbz w9,queue_empty\nsub w9,w9,#1\nstr w9,[x8,#16]\nstr wzr,[x19,#0x10]\nmov w9,#1\nstr x9,[sp,#0xa0]\nb skip_original\nqueue_empty:\nstr xzr,[x8,#8]\n'
 install('scoring_feedback_queue',0x2f97b18,body,skip=True)
 # Custom file IDs encode hairstyle, gender and age stage. Evolution and gender
 # swaps return a 100% link to the matching asset, while every stock ID falls
 # through to the original vendor link table.
 body='mov x8,x0\ncbz x8,finish\nmov w24,w1\n'
 for style in range(9):
  for gender in range(2):
   for stage in range(6):
    id_=98000+style*100+gender*10+stage;label='hair'+str(id_)
    body+=h.compare_key(str(id_),label,'next'+str(id_))+'\nnext'+str(id_)+':\n'
 body+='b finish\n'
 for style in range(9):
  for gender in range(2):
   for stage in range(6):
    id_=98000+style*100+gender*10+stage;ev=98000+style*100+gender*10+min(stage+1,5);swap=98000+style*100+(1-gender)*10+stage
    body+='hair'+str(id_)+':\n'+string(str(ev))+f'\ncbz w24,link_ready\n'+string(str(swap))+'\nb link_ready\n'
 body+='link_ready:\nmov x23,x0\nadrp x0,0x5c24000\nldr x0,[x0,#0x320]\nbl 0x2236f1c\nadrp x8,0x5c24000\nldr x8,[x8,#0x320]\nldr x0,[x8]\nbl 0x2237158\nmov x22,x0\nmov x1,xzr\nbl 0x4edba28\nmov x0,x23\nmov w1,#100\nmov x2,xzr\nbl 0x2f2c750\nmov x1,x0\nmov x0,x22\nldr x8,[x22]\nldr x2,[x8,#0x310]\nldr x9,[x8,#0x308]\nblr x9\nstr x22,[sp]\nb return_custom'
 install('custom_hair_evolution',0x2f2f9c4,body,ret=True)
 assert cursor<strings_va
 for s,va in strings.items():
  p=tail['p_offset']+va-tail['p_vaddr'];t=s.encode()+b'\0';blob.extend(b'\0'*max(0,p+len(t)-len(blob)));blob[p:p+len(t)]=t
 size=len(blob)-tail['p_offset'];header=e['e_phoff']+segs.index(tail)*56;struct.pack_into('<QQ',blob,header+32,size,size)
 allowed=set(range(header+32,header+48))|set(range(rwheader+40,rwheader+48))
 for x in hooks:allowed.update(range(off(x['site']),off(x['site'])+4))
 assert {i for i in range(len(native))if blob[i]!=native[i]}<=allowed
 d=dict(hooks=hooks,strings=strings,segment_va=tail['p_vaddr'],segment_offset=tail['p_offset'],segment_size=size,state_va=STATE,rw_header=rwheader,scores=SCORES,binary_sha256=hashlib.sha256(blob).hexdigest())
 (ROOT/'native_hooks.json').write_text(json.dumps(d,indent=2));return bytes(blob),d
if __name__=='__main__':
 import sys
 out,d=patch(Path(sys.argv[1]).read_bytes());Path(sys.argv[2]).write_bytes(out);print(d['binary_sha256'])
