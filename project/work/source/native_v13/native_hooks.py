"""Native cosmetic name lookup and national-office/military state bridges."""
import io,json,struct,importlib.util
from pathlib import Path
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v13helpers',ROOT.parent/'native_v8/native_hooks.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
asm,save,restore=h.asm,h.save,h.restore
def patch(native):
 e=ELFFile(io.BytesIO(native));segments=list(e.iter_segments());loads=[s for s in segments if s['p_type']=='PT_LOAD'];tail=loads[-1]
 assert tail['p_vaddr']==0x6308000 and tail['p_flags']==5
 blob=bytearray(native);cursor=(tail['p_vaddr']+len(native)-tail['p_offset']+4095)&~4095;strings_va=cursor+0x20000;strings={};hooks=[]
 def off(va):
  s=next(s for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']);return s['p_offset']+va-s['p_vaddr']
 def lit(s):
  if s not in strings:strings[s]=strings_va+sum(len(t.encode())+1 for t in strings)
  return strings[s]
 def string(s):return f'adr x0, {lit(s):#x}\nbl {h.NEW_STRING:#x}'
 def put(s,reg):return string(s)+f'\nmov x1, x0\nmov x0, x21\nmov w2, {reg}\nmov x3, xzr\nbl 0x3059f90'
 def get(s,reg,fallback=0):return string(s)+f'\nmov x1, x0\nmov x0, x21\nmov w2, #{fallback}\nmov x3, xzr\nbl 0x3059ee0\nmov {reg}, w0\n'
 def text(s,reg):return string(s)+f'\nmov x1, x0\nmov x0, x21\nmov x2, {reg}\nmov x3, xzr\nbl 0x3059d08'
 def get_text(s,reg):return string(s)+f'\nmov x1, x0\nmov x0, x21\nmov x2, xzr\nmov x3, xzr\nbl 0x3059934\nmov {reg}, x0'
 def code_at(source,va):
  (ROOT/'last_assembly.txt').write_text(source)
  b=asm(source,va);p=tail['p_offset']+va-tail['p_vaddr'];blob.extend(b'\0'*max(0,p+len(b)-len(blob)));blob[p:p+len(b)]=b;return len(b)
 def install(name,site,body,expect=None):
  nonlocal cursor
  raw=bytes(blob[off(site):off(site)+4]);ins=list(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(raw,site))[0];original=ins.mnemonic+' '+ins.op_str.replace('#0x','0x')
  if expect:assert raw==asm(expect,site)
  else:assert ins.mnemonic=='b'
  source=save()+'\n'+body+'\nfinish:\n'+restore()+'\n'+original+f'\nb {site+4:#x}\nreturn_name:\n'+restore()+'\nret'
  length=code_at(source,cursor);blob[off(site):off(site)+4]=asm(f'b {cursor:#x}',site)
  hooks.append(dict(name=name,site=site,stub=cursor,resume=site+4,original=original,source=source));cursor=(cursor+length+15)&~15
 got={'fopen':0x5d1b7c8,'fseek':0x5d1b7d0,'fread':0x5d1b388,'fclose':0x5d1b7d8}
 def call(n):return f'adrp x16, {got[n]&~4095:#x}\nldr x16, [x16, #{got[n]&4095}]\nblr x16'
 # Each read has its own FILE descriptor; atomic activation cannot expose a
 # half-written pack. No writable executable memory or process-global cache.
 reader=cursor
 source=f'''stp x29, x30, [sp, #-0x140]!
 stp x19, x20, [sp, #0x10]
 stp x21, x22, [sp, #0x20]
 mov x21, xzr
 cmp w0, #1
 b.lt done
 mov w8, #9999
 cmp w0, w8
 b.gt done
 cmp w1, #2
 b.hi done
 mov w8, #10000
 madd w20, w1, w8, w0
 lsl w20, w20, #8
 add w20, w20, #32
 adr x0, {lit('/data/data/com.candywriter.bitlife/files/namepack-active.bin'):#x}
 adr x1, {lit('rb'):#x}
 {call('fopen')}
 cbz x0, done
 mov x19, x0
 add x0, sp, #0x40
 mov x1, #1
 mov x2, #32
 mov x3, x19
 {call('fread')}
 cmp x0, #32
 b.ne close
 ldr x8, [sp, #0x40]
 movz x9, #0x5042
 movk x9, #0x414e, lsl #16
 movk x9, #0x454d, lsl #32
 movk x9, #0x3331, lsl #48
 cmp x8, x9
 b.ne close
 ldr w8, [sp, #0x48]
 cmp w8, #1
 b.ne close
 ldr w8, [sp, #0x4c]
 cmp w8, #256
 b.ne close
 mov x0, x19
 uxtw x1, w20
 mov w2, #0
 {call('fseek')}
 cbnz w0, close
 add x0, sp, #0x40
 mov x1, #1
 mov x2, #256
 mov x3, x19
 {call('fread')}
 cmp x0, #256
 b.ne close
 ldrb w8, [sp, #0x40]
 cbz w8, close
 ldrb w8, [sp, #0x13f]
 cbnz w8, close
 add x0, sp, #0x40
 bl {h.NEW_STRING:#x}
 mov x21, x0
 close:
 mov x0, x19
 {call('fclose')}
 done:
 mov x0, x21
 ldp x21, x22, [sp, #0x20]
 ldp x19, x20, [sp, #0x10]
 ldp x29, x30, [sp], #0x140
 ret'''
 length=code_at(source,cursor);cursor=(cursor+length+15)&~15
 # Preserve the raw saved-name getter (0x2bcb690). Serialization must keep
 # stock names, so disabling a cosmetic pack never leaves aliases in a save.
 for name,site,offset,kind,expected in [('team_display_name',0x2bcb9a4,0x20,0,'str x30, [sp, #-0x20]!'),('team_database_name',0x25eec30,0x10,0,'ldr x0, [x0, #0x20]'),('league_database_name',0x25ee560,0x10,1,'ldr x0, [x0, #0x20]')]:
  install(name,site,f'cbz x0, finish\nldr w0, [x0, #{offset}]\nmov w1, #{kind}\nbl {reader:#x}\ncbz x0, finish\nstr x0, [sp]\nb return_name',expected)
 def president(end='gov_write'):
  return h.load_occupation(end=end)+f'''\nldr w9, [x8, #0x10]
 cmp w9, #6
 b.ne {end}
 ldr x26, [x8, #0x28]
 cbz x26, {end}
 ldr w9, [x26, #0x10]
 cmp w9, #1
 b.ne {end}
 ldr w25, [x26, #0x20]
 cmp w25, #4
 b.ne {end}'''
 body='tbz w0, #0, finish\ncbz x19, finish\nldr x8, [x19, #0x18]\ncbz x8, finish\n'
 for key,label,nextlabel in [('NativeGovernmentSync','government','next1'),('NativeGovApproval','approval','next2'),('NativeWarSync','war_sync','next3'),('NativePackNames','pack_names','next4')]:body+=h.compare_key(key,label,nextlabel)+'\n'+nextlabel+':\n'
 body+='b finish\ngovernment:\nmov w22, #0\nmov w23, #-1\nmov w24, #0\nmov w25, #0\n'+president()+'''
 mov w22, #1
 mov x0, x26
 mov x1, xzr
 bl 0x2c1ffa8
 mov w24, w0
 cmp w24, #0
 csel w24, w24, wzr, ge
 mov w9, #100
 cmp w24, w9
 csel w24, w24, w9, le
 mov x0, x26
 mov x1, xzr
 bl 0x2c1c4e0
 cbz x0, gov_write
 mov x1, xzr
 bl 0x2a27250
 cbz x0, gov_write
 mov x8, x0
 '''
 countries=json.loads((ROOT/'assets/pools.json').read_text())['countries']
 for i,x in enumerate(countries):body+=h.compare_key(x['code'],'country'+str(i),'country_next'+str(i))+'\ncountry_next'+str(i)+':\n'
 body+='b gov_write\n'
 for i,x in enumerate(countries):body+='country'+str(i)+f':\nmov w23, #{i}\nb gov_write\n'
 body+='gov_write:\n'+'\n'.join(put(k,r)for k,r in [('President','w22'),('HomeCountry','w23'),('NativeApproval','w24'),('Office','w25')])+'\nb finish\napproval:\n'+president('finish')+'''
 cmp w20, #-3
 b.lt finish
 cmp w20, #3
 b.gt finish
 mov x0, x26
 mov w1, w20
 mov x2, xzr
 bl 0x2c21704
 b finish
 war_sync:
 '''+h.load_game()+'''
 ldr x22, [x8, #0x20]
 cbz x22, finish
 ldr x23, [x8, #0x28]
 cbz x23, finish
 ldr w23, [x23, #0x20]
 '''+string('government_v13')+'''
 mov x1, x0
 mov x0, x22
 mov w2, w23
 mov x3, xzr
 bl 0x32800fc
 cbz x0, finish
 mov x22, x0
 '''+string('WarOpponent')+'''
 mov x1, x0
 mov x0, x22
 mov w2, #-1
 mov x3, xzr
 bl 0x3059ee0
 mov w24, w0
 '''+string('WarProgress')+'''
 mov x1, x0
 mov x0, x22
 mov w2, #0
 mov x3, xzr
 bl 0x3059ee0
 mov w25, w0
 '''+put('WarOpponent','w24')+'\n'+put('WarProgress','w25')+'\nb finish\npack_names:\n'+get('Cup','w24')+f'''
 cmp w24, #1
 b.lt pack_teams
 cmp w24, #4
 b.gt pack_teams
 mov w0, w24
 mov w1, #2
 bl {reader:#x}
 cbz x0, pack_teams
 mov x22, x0
 '''+text('Competition','x22')+'''
 pack_teams:
 cmp w24, #4
 b.eq finish
 '''
 pool=json.loads((ROOT/'assets/pools.json').read_text())['clubpool'];teamrows=list(__import__('csv').DictReader((ROOT/'assets/native_teams.csv').open()))
 import re
 pool_ids=[next(int(t['Index'])for t in teamrows if re.sub(r'<([^<>]*)>',lambda m:m[1].split('/')[0],t['Name'])==name and'flag-'+t['Country Code']==flag)for name,flag in pool]
 keys=[('TeamIndex','TeamName',False),('Lookup','Opponent',True)]+[(f'T{i}ID',f'T{i}Name',True)for i in [1,2,3]]
 for j,(key,label,mapped)in enumerate(keys):
  body+='\n'+get(key,'w0',-1)
  if mapped:
   for idx,id_ in enumerate(pool_ids):body+=f'cmp w0, #{idx}\nb.eq pool_{j}_{idx}\n'
   body+=f'b pack_next{j}\n'
   for idx,id_ in enumerate(pool_ids):body+=f'pool_{j}_{idx}:\nmov w0, #{id_}\nb pool_ready{j}\n'
   body+=f'pool_ready{j}:\n'
  body+=f'mov w1, #0\nbl {reader:#x}\ncbz x0, pack_next{j}\nmov x22, x0\n'+text(label,'x22')+f'\npack_next{j}:\n'
 body+='b finish'
 # Keep original saved names so restoring the base pack also restores added
 # tournament labels, without changing participant IDs or pending draws.
 restore_names=''
 for j,key in enumerate(['TeamName','Opponent','T1Name','T2Name','T3Name']):
  restore_names+=get_text('Original'+key,'x22')+f'\ncbz x22, backup{j}\nldr w9, [x22, #0x10]\ncbnz w9, reset_name{j}\nbackup{j}:\n'+get_text(key,'x22')+f'\ncbz x22, name_next{j}\n'+text('Original'+key,'x22')+f'\nb name_next{j}\nreset_name{j}:\n'+text(key,'x22')+f'\nname_next{j}:\n'
 cup_names=''
 for cup,n in enumerate(['Champions League','Europa League','Conference League','World Cup'],1):
  cup_names+=string(n)+'\nmov x22, x0\n'+text('CupName'+str(cup),'x22')+f'\nmov w0, #{cup}\nmov w1, #2\nbl {reader:#x}\ncbz x0, cup_next{cup}\nmov x22, x0\n'+text('CupName'+str(cup),'x22')+f'\ncup_next{cup}:\n'
 cup_names+='\n'+get('Cup','w24')+'\n'
 for cup in range(1,5):cup_names+=f'cmp w24, #{cup}\nb.eq selected_cup{cup}\n'
 cup_names+='b selected_cup_done\n'
 for cup in range(1,5):cup_names+=f'selected_cup{cup}:\n'+get_text('CupName'+str(cup),'x22')+'\n'+text('Competition','x22')+'\nb selected_cup_done\n'
 cup_names+='selected_cup_done:\n'
 # Existing selected-cup alias reads remain harmless and use the same file.
 body=body.replace('pack_names:\n','pack_names:\n'+cup_names+restore_names)
 body=body.replace(get('Lookup','w0',-1),get('CurrentOpponentID','w0',-1))
 install('government_and_pack_pulses',0x321b46c,body)
 assert cursor<strings_va,(hex(cursor),hex(strings_va))
 for s,va in strings.items():
  p=tail['p_offset']+va-tail['p_vaddr'];data=s.encode()+b'\0';blob.extend(b'\0'*max(0,p+len(data)-len(blob)));blob[p:p+len(data)]=data
 size=len(blob)-tail['p_offset'];header=e.header['e_phoff']+segments.index(tail)*e.header['e_phentsize'];struct.pack_into('<QQ',blob,header+32,size,size)
 allowed=set(range(header+32,header+48))
 for x in hooks:allowed.update(range(off(x['site']),off(x['site'])+4))
 assert {i for i in range(len(native))if blob[i]!=native[i]}<=allowed
 details=dict(hooks=hooks,reader=reader,reader_source=source,got=got,strings=strings,segment_va=tail['p_vaddr'],segment_offset=tail['p_offset'],segment_size=size,pool_ids=pool_ids,countries=countries)
 (ROOT/'native_hooks.json').write_text(json.dumps(details,indent=2));return bytes(blob),details
