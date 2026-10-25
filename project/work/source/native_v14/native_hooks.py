"""v14 native expression expansion, saved cup draws, score attribution and career gates."""
import io,json,struct,importlib.util,csv,re
from pathlib import Path
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v14helpers',ROOT.parent/'native_v8/native_hooks.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
asm,save,restore=h.asm,h.save,h.restore

def patch(native):
 e=ELFFile(io.BytesIO(native));segments=list(e.iter_segments());loads=[s for s in segments if s['p_type']=='PT_LOAD'];tail=loads[-1];assert tail['p_vaddr']==0x6308000 and tail['p_flags']==5
 blob=bytearray(native);cursor=(tail['p_vaddr']+len(native)-tail['p_offset']+4095)&~4095;strings_va=cursor+0x40000;strings={};hooks=[]
 def off(va):
  s=next(s for s in loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz']);return s['p_offset']+va-s['p_vaddr']
 def lit(s):
  if s not in strings:strings[s]=strings_va+sum(len(t.encode())+1 for t in strings)
  return strings[s]
 def string(s):return f'adr x0, {lit(s):#x}\nbl {h.NEW_STRING:#x}'
 def put(s,reg):return f'str {reg}, [sp, #0xf8]\n'+string(s)+'\nmov x1, x0\nmov x0, x21\nldr w2, [sp, #0xf8]\nmov x3, xzr\nbl 0x3059f90'
 def get(s,reg,fallback=0):return string(s)+f'\nmov x1, x0\nmov x0, x21\nmov w2, #{fallback}\nmov x3, xzr\nbl 0x3059ee0\nmov {reg}, w0\n'
 def text(s,val):return string(val)+'\nmov x22, x0\n'+string(s)+'\nmov x1, x0\nmov x0, x21\nmov x2, x22\nmov x3, xzr\nbl 0x3059d08'
 def install(name,site,body,expect=None,return_tail=False):
  nonlocal cursor
  raw=bytes(blob[off(site):off(site)+4]);i=list(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(raw,site))[0];original=i.mnemonic+' '+i.op_str.replace('#0x','0x')
  if expect:assert raw==asm(expect,site),(name,original)
  source=save()+'\n'+body+'\nfinish:\n'+restore()+'\n'+original+f'\nb {site+4:#x}'
  if return_tail:source+='\nnative_return:\n'+restore()+'\nret'
  source=re.sub(r'cmp (w\d+), #(\d+)',lambda m:(f'mov w10, #{m[2]}\ncmp {m[1]}, w10'if int(m[2])>4095 else m[0]),source)
  (ROOT/'last_assembly.txt').write_text(source)
  code=asm(source,cursor);p=tail['p_offset']+cursor-tail['p_vaddr'];blob.extend(b'\0'*max(0,p+len(code)-len(blob)));blob[p:p+len(code)]=code;blob[off(site):off(site)+4]=asm(f'b {cursor:#x}',site)
  hooks.append(dict(name=name,site=site,stub=cursor,resume=site+4,original=original,source=source,length=len(code)));cursor=(cursor+len(code)+15)&~15
 # The decimal-condition scanner deliberately rejects nested <...> tokens and
 # tokens longer than 256 chars. Resolve the stock master tags first, as the
 # blueprint and display pipelines already do, then retain its decimal parser.
 install('resolve_condition_tags',0x3038d24,'mov x0, x19\nmov x1, x20\nbl 0x308c384\ncbz x0, finish\nstr x0, [sp, #0x98]','mov x0, x19')
 # GFC entry builder produces a normal ListItem; +0xd0 is its disabled flag.
 body='cbz x19, finish\ncbz x21, finish\nldr x8, [x19, #0x10]\ncbz x8, finish\n'+h.compare_key('music_studio','age_check','check_parole')+'\ncheck_parole:\n'+h.compare_key('parole_v11','age_check','finish')+'\nage_check:\n'+h.load_game()+'''\nldr x8, [x8, #0x28]
 cbz x8, finish
 ldr w9, [x8, #0x20]
 cmp w9, #18
 b.ge finish
 mov w9, #1
 strb w9, [x21, #0xd0]
 '''+string('Available from age 18')+'\nstr x0, [x21, #0x20]'
 install('adult_entry_grey',0x306180c,body,'cbz x20, 0x3061888')
 # Exact internal marker: visible nested adult activities grey out without
 # depending on undocumented bracket-filter syntax. Other filters are retained.
 body='mov x8, x1\ncbz x8, finish\n'+h.compare_key('v14-adult','nested_age','finish')+'\nnested_age:\n'+h.load_game()+'''\nldr x8, [x8, #0x28]
 cbz x8, finish
 ldr w9, [x8, #0x20]
 cmp w9, #18
 cset w9, ge
 str x9, [sp]
 b native_return
 '''
 install('adult_nested_grey',0x304b8ac,body,'str x30, [sp, #-0x30]!',True)
 def injection(reg,key):return string(key)+f'\nmov x1, x0\nmov x0, {reg}\ncbz x0, finish\nmov x2, xzr\nbl {h.INJECT:#x}'
 install('all_sports_people',0x30f8a3c,injection('x26','SportsPeople'))
 install('mafia_operations_menu',0x30fa640,injection('x19','MafiaOperations'),'adrp x8, 0x5c24000')
 install('music_people_menu',0x30f97d0,injection('x19','MusicPeople'),'adrp x8, 0x5c24000')
 install('workplace_roles_menu',0x30f7374,injection('x19','WorkplaceRoles'))
 pools=json.loads((ROOT.parent/'native_v13/assets/pools.json').read_text());clubs=pools['clubpool']+[['Madrid','flag-es'],['City FC','flag-gb'],['Paris Saint-Germain','flag-fr']];nation=pools['nationalpool']
 teams=list(csv.DictReader((ROOT.parent/'native_v13/assets/native_teams.csv').open()))
 ids=[next((int(t['Index'])for t in teams if re.sub(r'<([^<>]*)>',lambda m:m[1].split('/')[0],t['Name'])==name and'flag-'+t['Country Code']==flag),5999)for name,flag in clubs]
 logo_by_id={5115:'madrid',5012:'city',5999:'psg',5501:'arsenal',5506:'chelsea',5508:'city'}
 # Correct exact counterpart IDs using catalog names, independent of row order.
 for n,flag,logo in [('Arson Hall FC','flag-gb','arsenal'),('Blues FC','flag-gb','chelsea'),('Atletico','flag-es','atletico'),('Barcelona','flag-es','barcelona'),('Bianconeri','flag-it','juventus'),('Munich','flag-de','bayern')]:
  for id_,(name,f)in zip(ids,clubs):
   if (name,f)==(n,flag):logo_by_id[id_]=logo
 body='tbnz w0, #0, successful_write\nb finish\nsuccessful_write:\ncbz x19, finish\nldr x8, [x19, #0x18]\ncbz x8, finish\n'
 keys=[('NativeCupDraw','draw'),('NativeScoreDetails','details'),('NativeCupLabels','labels'),('NativePeopleSync','people'),('NativeMafiaSync','mafia'),('NativeMafiaImpact','mafia_impact'),('NativeOfficeSync','office'),('NativeCupCompletion','completion'),('NativeOfficeImpact','office_impact')]
 for j,(k,l)in enumerate(keys):body+=h.compare_key(k,l,'next'+str(j))+'\nnext'+str(j)+':\n'
 body+='b finish\noffice_impact:\n'+get('CompanyPerformance','w24')+h.load_occupation()+'''\nldr w9, [x8, #0x10]
 cmp w9, #2
 b.ne finish
 mov w1, #1
 cmp w24, #65
 b.lt office_weak
 mov w1, #2
 b office_apply
 office_weak:
 cmp w24, #40
 b.ge office_apply
 mov w1, #-1
 office_apply:
 mov x0, x8
 mov x2, xzr
 bl 0x2b6ae5c
 b finish
 '''
 body+='b finish\ncompletion:\n'+get('Stage','w24')+'cmp w24, #7\nb.ne completion_old\nmov w24, #0\n'+put('Stage','w24')+'\n'+put('Phase','w24')+'\ncompletion_old:\n'+h.load_game()+'''
 ldr x22, [x8, #0x20]
 cbz x22, finish
 ldr x23, [x8, #0x28]
 cbz x23, finish
 ldr w23, [x23, #0x20]
 '''+string('soccer_v11')+'''
 mov x1, x0
 mov x0, x22
 mov w2, w23
 mov x3, xzr
 bl 0x32800fc
 cbz x0, finish
 mov x21, x0
 '''+get('Stage','w24')+'cmp w24, #5\nb.ne finish\nmov w24, #0\n'+put('Stage','w24')+'\n'+put('Pending','w24')+'\nb finish\ndraw:\n'+get('Cup','w24')+get('Lookup','w25')+get('TeamPool','w26',-1)+get('TeamIndex','w23',-1)+'''
 cmp w24, #4
 b.eq draw_team_ready
 cmp w23, #5115
 b.ne draw_team_city
 mov w26, #63
 b draw_team_ready
 draw_team_city:
 cmp w23, #5012
 b.ne draw_team_ready
 mov w26, #64
 draw_team_ready:
 '''+put('TeamPool','w26')+'''\nmov w27, #1
 cmp w20, #1
 b.eq draw_loop
 mov w27, #0
 draw_loop:
 cmp w24, #4
 mov w9, #63
 mov w10, #66
 csel w28, w9, w10, eq
 sdiv w9, w25, w28
 msub w25, w9, w28, w25
 cmp w25, #0
 b.ge draw_positive
 add w25, w25, w28
 draw_positive:
 cmp w25, w26
 b.eq draw_skip
 '''+get('T1ID','w9',-1)+'''\ncmp w27, #1
 b.eq draw_pick
 cmp w25, w9
 b.eq draw_skip
 '''+get('T2ID','w9',-1)+'''\ncmp w27, #2
 b.eq draw_pick
 cmp w25, w9
 b.eq draw_skip
 '''+get('T3ID','w9',-1)+'''\ncmp w27, #3
 b.eq draw_pick
 cmp w25, w9
 b.eq draw_skip
 b draw_pick
 draw_skip:
 add w25, w25, #1
 b draw_loop
 draw_pick:
 '''+put('Lookup','w25')+'\n'+put('CurrentOpponentID','w25')+'\ncmp w24, #4\nb.eq draw_world\n'
 for i in range(len(clubs)):body+=f'cmp w25, #{i}\nb.eq draw_club{i}\n'
 body+='b finish\ndraw_world:\n'
 for i in range(len(nation)):body+=f'cmp w25, #{i}\nb.eq draw_nation{i}\n'
 body+='b finish\n'
 for typ,pool in [('club',clubs),('nation',nation)]:
  for i,(name,flag)in enumerate(pool):
   body+=f'draw_{typ}{i}:\n'+text('Opponent',name)+'\n'+text('OriginalOpponent',name)+'\n'+text('OpponentFlag',flag)+'\nb draw_assigned\n'
 body+='draw_assigned:\ncmp w27, #0\nb.eq draw_knockout_done\n'
 # Get and set managed strings without re-resolving content/function tags.
 def copy_text(src,dst):return string(src)+'\nmov x1, x0\nmov x0, x21\nmov x2, xzr\nmov x3, xzr\nbl 0x3059934\nmov x22, x0\n'+string(dst)+'\nmov x1, x0\nmov x0, x21\nmov x2, x22\nmov x3, xzr\nbl 0x3059d08'
 for j in range(1,4):body+=f'cmp w27, #{j}\nb.eq draw_save{j}\n'
 body+='b finish\n'
 for j in range(1,4):
  body+=f'draw_save{j}:\n'+put(f'T{j}ID','w25')+'\n'+copy_text('Opponent',f'T{j}Name')+'\n'+copy_text('Opponent',f'OriginalT{j}Name')+'\n'+copy_text('OpponentFlag',f'T{j}Flag')+'\nb draw_next\n'
 body+='draw_next:\nadd w25, w25, #17\nadd w27, w27, #1\ncmp w27, #4\nb.lt draw_loop\nmov w24, #0\n'+put('Phase','w24')+'\n'+put('Return','w24')+'\nb finish\ndraw_knockout_done:\nmov w24, #0\n'+put('Return','w24')+'\nb finish\ndetails:\n'
 counters=['PlayerGoals','TeammateGoals','OpponentGoals','OwnGoals','OpponentOwnGoals']
 body+='cmp w20, #0\nb.ne details_update\nmov w24, #0\n'+'\n'.join(put(k,'w24')for k in counters)+'\nb finish\ndetails_update:\n'
 body+=get('LastFor','w24')+get('LastAgainst','w25')+get('Roll','w26')
 # Counters are cumulative; resolving or reopening the same score is idempotent.
 body+=get('PlayerGoals','w27')+get('TeammateGoals','w28')+get('OpponentOwnGoals','w9')+'add w10, w27, w28\nadd w10, w10, w9\nsub w24, w24, w10\ncmp w24, #0\nb.le against_details\ncmp w26, #0\nb.ne normal_for\nadd w9, w9, #1\nsub w24, w24, #1\n'+put('OpponentOwnGoals','w9')+'\nnormal_for:\ntbz w26, #0, player_for\nadd w28, w28, w24\n'+put('TeammateGoals','w28')+'\nb against_details\nplayer_for:\nadd w27, w27, w24\n'+put('PlayerGoals','w27')+'\nagainst_details:\n'+get('OpponentGoals','w27')+get('OwnGoals','w28')+'add w10, w27, w28\nsub w25, w25, w10\ncmp w25, #0\nb.le finish\ncmp w26, #99\nb.ne normal_against\nadd w28, w28, #1\nsub w25, w25, #1\n'+put('OwnGoals','w28')+'\nnormal_against:\nadd w27, w27, w25\n'+put('OpponentGoals','w27')+'\nb finish\nlabels:\n'+get('Cup','w24')+'cmp w24, #4\nb.eq finish\n'
 for key,dest,poolmapped in [('TeamIndex','TeamFlag',False),('CurrentOpponentID','OpponentFlag',True)]+[(f'T{j}ID',f'T{j}Flag',True)for j in range(1,4)]:
  label='label_'+dest;body+=get(key,'w25',-1)
  if poolmapped:
   for i,(id_,(name,flag))in enumerate(zip(ids,clubs)):
    body+=f'cmp w25, #{i}\nb.eq {label}_{i}\n'
   body+=f'b {label}_done\n'
   for i,(id_,(name,flag))in enumerate(zip(ids,clubs)):
    body+=f'{label}_{i}:\ncmp w24, #4\nb.eq {label}_done\n'
    logo=logo_by_id.get(id_);icon='v14-'+logo if logo else flag
    if logo:body+=f'cmp w24, #1\nb.ne {label}_flag{i}\n'+text(dest,icon)+f'\nb {label}_done\n{label}_flag{i}:\n'
    body+=text(dest,flag)+f'\nb {label}_done\n'
  else:
   for id_,logo in logo_by_id.items():body+=f'cmp w25, #{id_}\nb.eq {label}_{id_}\n'
   body+=f'b {label}_done\n'
   for id_,logo in logo_by_id.items():
    flag=next((f for i,(n,f)in zip(ids,clubs)if i==id_),'flag-fr')
    body+=f'{label}_{id_}:\ncmp w24, #1\nb.ne {label}_flag{id_}\n'+text(dest,'v14-'+logo)+f'\nb {label}_done\n{label}_flag{id_}:\n'+text(dest,flag)+f'\nb {label}_done\n'
  body+=label+'_done:\n'
 # The retained v13 pack reader also serves the three newly added pool slots.
 reader=json.loads((ROOT.parent/'native_v13/native_hooks.json').read_text())['reader']
 for key,dest in [('CurrentOpponentID','Opponent')]+[(f'T{j}ID',f'T{j}Name')for j in range(1,4)]:
  label='alias_'+dest;body+=get(key,'w25',-1)
  for i in [63,64,65]:body+=f'cmp w25, #{i}\nb.eq {label}_{i}\n'
  body+=f'b {label}_done\n'
  for i in [63,64,65]:body+=f'{label}_{i}:\nmov w0, #{ids[i]}\nmov w1, #0\nbl {reader:#x}\ncbz x0, {label}_done\nmov x22, x0\n'+string(dest)+'\nmov x1, x0\nmov x0, x21\nmov x2, x22\nmov x3, xzr\nbl 0x3059d08\nb '+label+'_done\n'
  body+=label+'_done:\n'
 body+='b finish\npeople:\nmov w22, #0\nmov w23, #-1\n'+h.load_occupation(end='people_write')+'''\nldr w9, [x8, #0x10]
 cmp w9, #6
 b.ne people_write
 ldr x8, [x8, #0x28]
 cbz x8, people_write
 ldr w9, [x8, #0x10]
 cmp w9, #2
 b.ne people_write
 mov w22, #1
 ldr x8, [x8, #0x30]
 cbz x8, people_write
 ldr w23, [x8, #0x20]
 people_write:
 '''+put('Eligible','w22')+'\n'+put('CurrentTeam','w23')+'\nb finish\nmafia:\nmov w22, #0\nmov w23, #0\n'+h.load_occupation(end='mafia_write')+'''\nldr w9, [x8, #0x10]
 cmp w9, #6
 b.ne mafia_write
 ldr x8, [x8, #0x28]
 cbz x8, mafia_write
 ldr w9, [x8, #0x10]
 cmp w9, #4
 b.ne mafia_write
 mov w22, #1
 ldr w23, [x8, #0x28]
 mafia_write:
 '''+put('Eligible','w22')+'\n'+put('Rank','w23')+'\nb finish\nmafia_impact:\n'+h.load_occupation()+'''\nldr w9, [x8, #0x10]
 cmp w9, #6
 b.ne finish
 ldr x22, [x8, #0x28]
 cbz x22, finish
 ldr w9, [x22, #0x10]
 cmp w9, #4
 b.ne finish
 cmp w20, #-3
 b.lt finish
 cmp w20, #3
 b.gt finish
 mov x0, x22
 mov w1, w20
 mov x2, xzr
 bl 0x2bfa594
 ldr x0, [x22, #0x20]
 cbz x0, finish
 mov w1, w20
 mov x2, xzr
 bl 0x2bf6c7c
 b finish
 office:
 mov w22, #0
 mov w23, #-1
 '''+h.load_occupation(end='office_write')+'''\nldr w9, [x8, #0x10]
 cmp w9, #2
 b.ne office_write
 mov w22, #1
 ldr x8, [x8, #0x40]
 cbz x8, office_write
 ldr w23, [x8, #0x10]
 office_write:
 '''+put('Eligible','w22')+'\n'+put('CurrentCareer','w23')+'\nb finish'
 install('v14_saved_activity_pulses',0x321b46c,body)
 assert cursor<strings_va,(hex(cursor),hex(strings_va))
 for s,va in strings.items():
  p=tail['p_offset']+va-tail['p_vaddr'];data=s.encode()+b'\0';blob.extend(b'\0'*max(0,p+len(data)-len(blob)));blob[p:p+len(data)]=data
 size=len(blob)-tail['p_offset'];header=e.header['e_phoff']+segments.index(tail)*e.header['e_phentsize'];struct.pack_into('<QQ',blob,header+32,size,size)
 allowed=set(range(header+32,header+48))
 for x in hooks:allowed.update(range(off(x['site']),off(x['site'])+4))
 assert {i for i in range(len(native))if blob[i]!=native[i]}<=allowed
 details=dict(hooks=hooks,strings=strings,segment_va=tail['p_vaddr'],segment_offset=tail['p_offset'],segment_size=size,pool_ids=ids,clubs=clubs,national=nation,logo_by_id=logo_by_id)
 (ROOT/'native_hooks.json').write_text(json.dumps(details,indent=2));return bytes(blob),details
