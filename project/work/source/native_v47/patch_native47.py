"""Native post receipts and per-life comment threads on the pinned v46 engine.

All strings and numbers persist in Genesis. Only the exact visible scenario
is rooted in BSS; no NPC or post pointers are persisted. Existing entry hooks
are chained from their actual instructions, retaining v46's UI repairs.
"""
import copy,hashlib,json,struct,sys
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from native_hooks import Builder,h
from native_v46.patch_native46 import Patch as Previous
from catalog47 import *
BASE_SHA='659e6329eab8e38286a248a6ec591a030a44908f3a13a9cbc0664fc80fcd16a5'
class Patch(Previous):
 def __init__(self,raw):
  Builder.__init__(self,raw);assert hashlib.sha256(raw).hexdigest()==BASE_SHA
  self.base=json.loads((SOURCE/'native_v46/native_hooks.json').read_text());self.manifest=copy.deepcopy(self.base)
  self.tail=next(s for s in self.loads if s['p_vaddr']==self.base['segment_va'])
  self.cursor=0x655e000;self.code_start=self.cursor;self.strings_va=0x6569000;self.string_cursor=0x656b000
  self.strings=copy.deepcopy(self.base['strings']);self.states=copy.deepcopy(self.base['states']);self.routines=[];self.hooks=[];self.changed=[];self.serial=0
  self.old={r['name']:r for r in self.base['hooks']+self.base['routines']};self.rw=next(s for s in self.loads if s['p_vaddr']==0x6570000)
  self.root47=ROOT
  self.state47=(self.rw['p_vaddr']+self.rw['p_memsz']+15)&~15;self.states['comments47']=dict(va=self.state47,size=16)
  self.snprintf=self.plt('snprintf')
 def install(self,name,site,body,ret=False):
  ins=next(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(bytes(self.blob[self.off(site):self.off(site)+4]),site));orig=ins.mnemonic+' '+ins.op_str
  source=h.save()+'\n'+body+'\nfinish:\n'+h.restore()+'\n'+orig+f'\nb {site+4:#x}'
  if ret:source+='\nreturn_custom:\n'+h.restore()+'\nret'
  va=self.add_code(name,source);r=self.routines.pop();self.blob[self.off(site):self.off(site)+4]=h.asm(f'b {va:#x}',site)
  self.hooks.append(dict(name=name,site=site,stub=va,resume=site+4,original=orig,source=r['source'],length=r['length']));self.changed.append([site,4,name])
 def field(self,slot,comment,field,op='geti',value=None,out=None):
  def arg(reg,value):return f'mov {reg},{value}\n'if isinstance(value,str)else f'mov {reg},#{value}\n'
  s=arg('w0',slot)+arg('w1',comment)+f'adr x2,{self.literal(field):#x}\n'
  if value is not None:s+=arg('x3'if op=='sets'else'w3',value)
  s+=f'bl {self.ops[op]:#x}\n'
  if out:s+=f'mov {out},{"w0"if out.startswith("w")else"x0"}\n'
  return s
 def finish47(self):
  assert self.cursor<self.strings_va,hex(self.cursor)
  for s,va in self.strings.items():
   if s in self.base['strings']:continue
   data=s.encode()+b'\0';o=self.off(va);assert self.blob[o:o+len(data)]==b'\0'*len(data)
   self.blob[o:o+len(data)]=data;self.changed.append([va,len(data),'literal'])
  assert self.string_cursor<0x6570000
  bank=(ROOT/'social_bank47.bin').read_bytes();bank_offset=self.rw['p_offset']+0x8000
  assert len(self.blob)<bank_offset and self.state47+16<self.rw['p_vaddr']+0x8000
  self.blob.extend(b'\0'*(bank_offset-len(self.blob)));self.blob.extend(bank)
  rw_size=len(self.blob)-self.rw['p_offset'];self.manifest['v47_appended_data_range']=[len(self.native),len(self.blob)]
  size=max(self.tail['p_filesz'],self.string_cursor-self.tail['p_vaddr']);p=self.e['e_phoff']+self.segs.index(self.tail)*56+32;struct.pack_into('<QQ',self.blob,p,size,size)
  q=self.e['e_phoff']+self.segs.index(self.rw)*56+32;struct.pack_into('<QQ',self.blob,q,rw_size,rw_size)
  sites={r['site']for r in self.hooks};self.manifest['hooks']=[r for r in self.manifest['hooks']if r['site']not in sites]+self.hooks;self.manifest['routines']+=self.routines
  self.manifest.update(strings=self.strings,states=self.states,segment_size=size,binary_sha256=hashlib.sha256(self.blob).hexdigest(),base_v46_sha256=BASE_SHA,v47_new_code_range=[self.code_start,self.cursor],v47_changed_ranges=self.changed,v47_program_header_ranges=[[p,16],[q,16]],bank_data_va=0x6578000,bank_data_bytes=len(bank),comments_history=HISTORY,comments_per_post=COMMENTS)
  (ROOT/'native_hooks.json').write_text(json.dumps(self.manifest,indent=2)+'\n');return bytes(self.blob)

def primitives(b):
 # Format keys on a bounded stack buffer, then immediately create a managed
 # string. The formatter is resolved from this ELF's actual libc import.
 s='sub sp,sp,#128\nmov w3,w0\nmov w4,w1\nmov x5,x2\nmov x0,sp\nmov w1,#128\n'+f'adr x2,{b.literal("P%dC%d%s"):#x}\nbl {b.snprintf:#x}\nmov x0,sp\nbl {h.NEW_STRING:#x}\nadd sp,sp,#128\nstr x0,[sp]\nb finish'
 keyfn=b.routine('v47_property_key',s);b.ops={}
 for op,api in [('geti',0x3059ee0),('seti',0x3059f90),('gets',0x3059934),('sets',0x3059d08)]:
  s=f'bl {keyfn:#x}\nmov x1,x0\nmov x0,x21\n'
  s+=('mov w2,w3\n'if op=='seti'else'mov x2,x3\n')if op.startswith('set')else'mov x2,xzr\n'
  s+=f'mov x3,xzr\nbl {api:#x}\nstr x0,[sp]\nb finish';b.ops[op]=b.routine('v47_'+op,s)
 # Numeric metadata does not pass strings through printf format specifiers.
 s='sub sp,sp,#192\nmov w5,w2\nmov w4,w1\nmov w3,w0\nmov x0,sp\nmov w1,#192\n'+f'adr x2,{b.literal("Posted at age %d in %d.\n%d comments. Choose Read comments to open the thread."):#x}\nbl {b.snprintf:#x}\nmov x0,sp\nbl {h.NEW_STRING:#x}\nadd sp,sp,#192\nstr x0,[sp]\nb finish'
 b.meta=b.routine('v47_post_metadata',s)
 s='sub sp,sp,#96\nmov w9,#60\nudiv w3,w0,w9\nmsub w4,w3,w9,w0\nmov x0,sp\nmov w1,#96\n'+f'adr x2,{b.literal("%d:%02d · "):#x}\nbl {b.snprintf:#x}\nmov x0,sp\nbl {h.NEW_STRING:#x}\nadd sp,sp,#96\nstr x0,[sp]\nb finish'
 b.timestamp=b.routine('v47_comment_timestamp',s)
 # Exact-length UTF-16 prefix and decimal suffix; no unbounded string reads.
 prefix=PREFIX.encode();s='str xzr,[sp]\ncbz x0,finish\nldr w9,[x0,#16]\n'+f'cmp w9,#{len(prefix)+3}\nb.ne finish\nadd x11,x0,#20\nadr x12,{b.literal(PREFIX):#x}\nmov w13,#{len(prefix)}\nparse47_prefix:\nldrh w9,[x11],#2\nldrb w10,[x12],#1\ncmp w9,w10\nb.ne finish\nsubs w13,w13,#1\nb.ne parse47_prefix\nmov w14,#0\nmov w13,#3\nmov w15,#10\nparse47_digits:\nldrh w9,[x11],#2\nsub w9,w9,#48\ncmp w9,#9\nb.hi finish\nmadd w14,w14,w15,w9\nsubs w13,w13,#1\nb.ne parse47_digits\nstr x14,[sp]\nb finish'
 b.decode=b.routine('v47_decode_scene',s)
 # Topic lookup uses the saved native post-type identifier. Hash collisions
 # here can only select another generic reaction group, never a memory index.
 s='str xzr,[sp]\ncbz x0,finish\nldr w12,[x0,#16]\ncmp w12,#1\nb.lt finish\ncmp w12,#128\nb.hi finish\nadd x13,x0,#20\nmovz w11,#40389\nmovk w11,#33052,lsl #16\nmovz w14,#403\nmovk w14,#256,lsl #16\ntopic47_loop:\nldrh w9,[x13],#2\neor w11,w11,w9\nmul w11,w11,w14\nsubs w12,w12,#1\nb.ne topic47_loop\n'
 for topic,names in TOPICS.items():
  for name in names:
   v=fnv(name);s+=f'movz w9,#{v&65535}\nmovk w9,#{v>>16},lsl #16\ncmp w11,w9\nb.eq topic47_{topic}\n'
 s+='b finish\n'
 for topic in TOPICS:s+=f'topic47_{topic}:\nmov w9,#{topic}\nstr x9,[sp]\nb finish\n'
 b.topic=b.routine('v47_post_topic',s)
 # One eligible native friend may appear in each thread. Scan only validated
 # ArrayList storage and live age-appropriate people; otherwise use a follower.
 s='str xzr,[sp]\nmov w25,w0\n'+h.load_game()+'\nldr x8,[x8,#0x20]\ncbz x8,finish\nldr x8,[x8,#0x198]\ncbz x8,finish\nldr w26,[x8,#0x18]\ncmp w26,#1\nb.lt finish\ncmp w26,#1024\nb.hi finish\nldr x27,[x8,#0x10]\ncbz x27,finish\nldr x9,[x27,#0x18]\ncmp x9,x26\nb.lo finish\nmov w28,#0\nfriend47_loop:\ncmp w28,w26\nb.hs finish\ncmp w28,#8\nb.hs finish\nadd x8,x27,#32\nldr x19,[x8,w28,uxtw #3]\nadd w28,w28,#1\ncbz x19,friend47_loop\nldrb w9,[x19,#0x18]\ncbz w9,friend47_loop\nldr w9,[x19,#0x20]\nmov w10,#13\ncmp w25,#8\nmov w11,#18\ncsel w10,w11,w10,eq\ncmp w9,w10\nb.lt friend47_loop\nmov x0,x19\nmov x1,xzr\nbl 0x2c44914\nstr x0,[sp]\nb finish'
 b.friend=b.routine('v47_friend_comment_name',s)

def record(b):
 f=b.field
 # Inputs: platform, caption, native post number, follower count, topic.
 s='str xzr,[sp]\ncmp w0,#9\nb.hi finish\ncbz x1,finish\ncmp w2,#1\nb.lt finish\ncmp w5,#1\nb.hi finish\nmov w24,w5\nmov w19,w0\nmov x20,x1\nmov w26,w2\nmov w27,w3\nmov w28,w4\n'+b.ctx(OWNER)+b.put('PendingSource')+'cbnz w24,record47_pending_ready\n'+b.set('PendingThread',0)+'record47_pending_ready:\n'
 s+='cmp w19,#8\nb.ne record47_age_ok\ncmp w23,#18\nb.lt finish\nrecord47_age_ok:\n'+b.get('PendingSource','w24')+'cbnz w24,record47_no_watermark\n'+f(0,'w19','Seen',out='w24')+'cmp w24,w26\nb.eq finish\n'+f(0,'w19','Seen','seti','w26')+'record47_no_watermark:\n'
 s+=h.load_game()+'\nldr x0,[x8,#0x28]\nmov x1,xzr\nbl 0x2c44914\nmov x22,x0\n'+b.textptr('PlayerName')
 s+=b.get('Head','w25')+'add w25,w25,#1\ncmp w25,#24\nmov w9,#1\ncsel w25,w25,w9,le\n'+b.put('Head','w25')+b.get('Total','w26')+'add w26,w26,#1\ntbnz w26,#31,finish\n'+b.put('Total','w26')+b.get('Count')+'add w24,w24,#1\nmov w9,#24\ncmp w24,w9\ncsel w24,w24,w9,le\n'+b.put('Count')
 s+=b.string('')+'mov x22,x0\n'+''.join(f('w25',0,k,'sets','x22')for k in ['RootText','RootName','ThreadId','Topic','Event'])
 s+=f('w25',0,'Id','seti','w26')+f('w25',0,'Platform','seti','w19')+f('w25',0,'Age','seti','w23')+f('w25',0,'Followers','seti','w27')+f('w25',0,'Caption','sets','x20')
 s+=f'bl {b.old["v45_current_year"]["stub"]:#x}\nmov w24,w0\n'+f('w25',0,'Year','seti','w24')
 for i,name in enumerate(PLATFORMS):s+=f'cmp w19,#{i}\nb.ne platform47_next_{i}\n'+b.string(name)+f'b platform47_ready\nplatform47_next_{i}:\n'
 s+='platform47_ready:\nmov x22,x0\n'+b.string(' · ')+'mov x1,x0\nmov x0,x22\nmov x2,x20\nmov x3,xzr\nbl 0x4e00114\nmov x22,x0\n'+f('w25',0,'Title','sets','x22')
 s+='mov w24,#3\ncmp w27,#100\nb.lt count47_ready\nmov w24,#4\nmov w9,#10000\ncmp w27,w9\nb.lt count47_ready\nmov w24,#5\nmovz w9,#16960\nmovk w9,#15,lsl #16\ncmp w27,w9\nb.lt count47_ready\nmov w24,#6\ncount47_ready:\n'+f('w25',0,'Count','seti','w24')
 s+=b.put('SelectedSlot','w25')+b.put('SelectedId','w26')+'mov w26,w24\n'+b.rng(len(USERNAMES),'w23')+b.rng(6,'w24')+'mov w20,w24\nmov w19,#1\ncomment47_loop:\ncmp w19,w26\nb.gt recorded47\n'
 s+=f('w25','w19','Parent','seti',0)+f('w25','w19','Timestamp','seti',-1)
 s+=f('w25','w19','Liked','seti',0)+f('w25','w19','Hidden','seti',0)+f('w25','w19','Reply','seti',0)
 s+='cmp w19,#1\nb.ne follower47_name\n'+f('w25',0,'Platform',out='w0')+f'bl {b.friend:#x}\ncbnz x0,name47_ready\nfollower47_name:\nadd w9,w23,w19\nsub w9,w9,#1\nmov w10,#24\nudiv w11,w9,w10\nmsub w9,w11,w10,w9\n'
 for i,name in enumerate(USERNAMES):s+=f'cmp w9,#{i}\nb.ne username47_next_{i}\n'+b.string(name)+f'b name47_ready\nusername47_next_{i}:\n'
 s+='name47_ready:\nmov x22,x0\n'+f('w25','w19','Name','sets','x22')+'cmp w28,#10\nmov w9,#0\ncsel w28,w28,w9,ls\nadd w24,w20,w19\nsub w24,w24,#1\nmov w10,#6\nudiv w11,w24,w10\nmsub w24,w11,w10,w24\n'
 for topic,texts in enumerate(REACTIONS):
  s+=f'cmp w28,#{topic}\nb.ne reaction47_topic_{topic}\n'
  for i,text in enumerate(texts):s+=f'cmp w24,#{i}\nb.ne reaction47_{topic}_{i}\n'+b.string(text)+f'b reaction47_ready\nreaction47_{topic}_{i}:\n'
  s+=f'reaction47_topic_{topic}:\n'
 s+='reaction47_ready:\nmov x22,x0\n'+f('w25','w19','Text','sets','x22')+f('w25','w19','Preview','sets','x22')+b.rng(20)+'mov w9,#100\nsdiv w10,w27,w9\nadd w24,w24,w10\nmovz w9,#34464\nmovk w9,#1,lsl #16\ncmp w24,w9\ncsel w24,w24,w9,le\ncmp w24,#0\ncsel w24,w24,wzr,ge\n'+f('w25','w19','Likes','seti','w24')+'add w19,w19,#1\nb comment47_loop\nrecorded47:\nmov w0,w25\nmov w1,w28\n'+f'bl {b.attach:#x}\n'+b.get('SelectedId','w0')+'str x0,[sp]\nb finish'
 b.record=b.routine('v47_record_post',s)
 # Execute only at the successful stock completion epilogue. Failed joins,
 # canceled posts and merely opening a platform cannot create a receipt.
 s='cbz x19,finish\nmov x27,x19\nldr x20,[x27,#0x170]\ncbz x20,finish\nldr w25,[x20,#0x10]\ncmp w25,#1\nb.lt finish\ncmp w25,#7\nb.hi finish\nldr x26,[x27,#0x178]\ncbz x26,finish\nldr x0,[x26,#0x10]\n'+f'bl {b.topic:#x}\nmov w28,w0\nmov x0,x26\nmov w1,w25\nmov x2,xzr\nbl 0x25eda3c\ncbz x0,finish\nmov x1,x0\nadd w0,w25,#1\nldr w2,[x20,#0x1c]\nldr w3,[x20,#0x20]\nmov w4,w28\nmov w5,#0\n'+f'bl {b.record:#x}\ncbz w0,finish\n'
 s+=b.string('\n\nRead comments in Assets > Social Media > Posts & comments.')+'mov x1,x0\nldr x0,[x27,#0x48]\nmov x2,xzr\nmov x3,xzr\nbl 0x4e00114\nmov x2,x0\nmov x0,x27\nadd x1,x27,#0x48\nbl 0x223e768\nb finish'
 b.install('v47_native_post_completed',0x265506c,s)
 # Deleting/rejoining a native account restarts its count. Reset only that
 # platform's receipt watermark; historical comment threads stay available.
 s='cmp w1,#1\nb.lt finish\ncmp w1,#7\nb.hi finish\nadd w19,w1,#1\n'+b.ctx(OWNER)+f(0,'w19','Seen','seti',0)+'b finish'
 b.install('v47_native_account_deleted',0x2c6fbcc,s)

def projection(b):
 f=b.field
 s=b.ctx(OWNER)+b.get('Count','w25')+b.get('Head','w26')+b.get('Filter','w27')+'mov w19,#1\nview47_loop:\ncmp w19,#24\nb.gt finish\n'+f('w19',7,'Visible','seti',0)+'cmp w19,w25\nb.gt view47_next\nsub w20,w26,w19\nadd w20,w20,#1\ncmp w20,#1\nb.ge view47_slot\nadd w20,w20,#24\nview47_slot:\ncmp w20,#1\nb.lt view47_next\ncmp w20,#24\nb.gt view47_next\n'+f('w20',0,'Platform',out='w24')+'cmp w27,#10\nb.eq view47_platform_ok\ncmp w24,w27\nb.ne view47_next\nview47_platform_ok:\ncmp w24,#8\nb.ne view47_age_ok\ncmp w23,#18\nb.lt view47_next\nview47_age_ok:\n'
 for field in ['Id','Age','Year','Count']:s+=f('w20',0,field,out='w24')+f('w19',7,field,'seti','w24')
 s+=f('w20',0,'Title','gets',out='x22')+f('w19',7,'Title','sets','x22')+f('w19',7,'Slot','seti','w20')+f('w19',7,'Visible','seti',1)+'view47_next:\nadd w19,w19,#1\nb view47_loop'
 b.project=b.routine('v47_project_recent_posts',s)
 # Returns 1 only when the selected ID still occupies its ring slot.
 s='str xzr,[sp]\n'+b.ctx(OWNER)+b.get('SelectedSlot','w25')+b.get('SelectedId','w26')+'cmp w25,#1\nb.lt finish\ncmp w25,#24\nb.gt finish\ncmp w26,#1\nb.lt finish\n'+f('w25',0,'Id',out='w24')+'cmp w24,w26\nb.ne finish\n'+f('w25',0,'Platform',out='w24')+'cmp w24,#8\nb.ne valid47_age\ncmp w23,#18\nb.lt finish\nvalid47_age:\nmov w9,#1\nstr x9,[sp]\nb finish'
 b.valid=b.routine('v47_selected_post_valid',s)
 s='str xzr,[sp]\n'+f'bl {b.valid:#x}\ncbz w0,invalid47_post\n'+b.ctx(OWNER)+b.get('SelectedSlot','w25')+f('w25',0,'Count',out='w26')+f('w25',0,'Title','gets',out='x22')+b.textptr('CurrentTitle')+f('w25',0,'Age',out='w19')+f('w25',0,'Year',out='w20')+f('w25',0,'Count',out='w2')+'mov w0,w19\nmov w1,w20\n'+f'bl {b.meta:#x}\nmov x20,x0\n'+f('w25',0,'RootText','gets',out='x22')+b.string('\n\n')+'mov x1,x0\nmov x0,x22\nmov x2,x20\nmov x3,xzr\nbl 0x4e00114\nmov x22,x0\n'+b.textptr('CurrentBody')+'mov w19,#1\nthread47_loop:\ncmp w19,#18\nb.gt thread47_ready\n'+f(0,'w19','Visible','seti',0)+'cmp w19,w26\nb.gt thread47_next\n'+f('w25','w19','Hidden',out='w24')+'cbnz w24,thread47_next\n'+f('w25','w19','Name','gets',out='x22')+f(0,'w19','ViewName','sets','x22')+f('w25','w19','Preview','gets',out='x22')+f(0,'w19','ViewText','sets','x22')+f(0,'w19','Visible','seti',1)+'thread47_next:\nadd w19,w19,#1\nb thread47_loop\nthread47_ready:\nmov w9,#1\nstr x9,[sp]\nb finish\ninvalid47_post:\n'+b.ctx(OWNER)+''.join(f(0,c,'Visible','seti',0)for c in range(1,19))+b.text('CurrentTitle','Post no longer stored')+b.text('CurrentBody','Choose Recent posts. This thread has been replaced by a newer post.')+'b finish'
 b.thread=b.routine('v47_prepare_thread',s)
 s='str xzr,[sp]\n'+f'bl {b.valid:#x}\ncbz w0,finish\n'+b.ctx(OWNER)+b.get('SelectedSlot','w25')+b.get('SelectedComment','w19')+'cmp w19,#1\nb.lt finish\ncmp w19,#18\nb.gt finish\n'+f('w25',0,'Count',out='w24')+'cmp w19,w24\nb.gt finish\n'+f('w25','w19','Hidden',out='w24')+'cbnz w24,finish\n'+f('w25','w19','Name','gets',out='x22')+b.textptr('CommentName')+f('w25','w19','Liked',out='w26')+f('w25','w19','Likes',out='w24')+'add w24,w24,w26\n'+b.put('CommentLikes')+'cbnz w26,liked47_label\n'+b.text('LikeLabel','Like comment')+'b liked47_done\nliked47_label:\n'+b.text('LikeLabel','Unlike comment')+'liked47_done:\n'+f('w25','w19','Text','gets',out='x20')+f('w25','w19','Timestamp',out='w24')+'tbnz w24,#31,timestamp47_done\nmov w0,w24\n'+f'bl {b.timestamp:#x}\nmov x1,x20\nmov x2,xzr\nmov x3,xzr\nbl 0x4e00114\nmov x20,x0\ntimestamp47_done:\n'+f('w25','w19','Parent',out='w26')+'cbz w26,parent47_done\n'+f('w25','w26','Name','gets',out='x22')+b.string('In reply to ')+'mov x1,x22\nmov x2,xzr\nmov x3,xzr\nbl 0x4e00114\nmov x22,x0\n'+b.string('\n\n')+'mov x1,x0\nmov x0,x22\nmov x2,x20\nmov x3,xzr\nbl 0x4e00114\nmov x20,x0\nparent47_done:\n'+f('w25','w19','Reply',out='w26')+'cmp w26,#1\nb.lt no_reply47\ncmp w26,#3\nb.gt no_reply47\n'
 for i,reply in enumerate(REPLIES,1):
  s+=f'cmp w26,#{i}\nb.ne reply47_next_{i}\n'+b.string('\n\nYou: '+reply+'\n\n'+FOLLOWUPS[i-1])+'mov x1,x0\nmov x0,x20\nmov x2,xzr\nmov x3,xzr\nbl 0x4e00114\nmov x20,x0\nb no_reply47\n'+f'reply47_next_{i}:\n'
 s+='no_reply47:\nmov x22,x20\n'+b.textptr('CommentBody')+'mov w9,#1\nstr x9,[sp]\nb finish'
 b.comment=b.routine('v47_prepare_comment',s)

def custom_accounts(b):
 # Existing Discord/Reddit counters and age-up quota remain the source of
 # truth. A successful custom post uses the same receipt recorder as stock.
 s='str xzr,[sp]\ncmp w0,#1\nb.hi finish\nmov w19,w0\nmov w20,w1\n'+b.ctx(OWNER)+b.text('Status','This account is available from age 13, after its platform launches.')+'cmp w23,#13\nb.lt finish\n'+f'bl {b.old["v45_current_year"]["stub"]:#x}\nmov w9,#2015\ncbz w19,custom47_year\nmov w9,#2005\ncustom47_year:\ncmp w0,w9\nb.lt finish\n'+b.ctx('social_v18')+b.get('PostsUsed','w24')+'cmp w24,#12\nb.ge custom47_limit\nadd w24,w24,#1\n'+b.put('PostsUsed')
 for platform in range(2):
  s+=f'cmp w19,#{platform}\nb.ne custom47_next_{platform}\n'+b.set(f'P{platform}Active',1)+b.inc(f'P{platform}Posts')+b.get(f'P{platform}Posts','w26')+b.get(f'P{platform}Followers','w27')+'add w27,w27,#20\n'+b.put(f'P{platform}Followers','w27')+f'b custom47_caption\ncustom47_next_{platform}:\n'
 s+='custom47_caption:\ncbnz w20,custom47_school\n'+b.string('An update about my interests')+'mov w28,#0\nb custom47_record\ncustom47_school:\n'+b.string('An update about school or my team')+'mov w28,#7\ncustom47_record:\nmov x1,x0\nmov w0,w19\nmov w2,w26\nmov w3,w27\nmov w4,w28\nmov w5,#0\n'+f'bl {b.record:#x}\nstr x0,[sp]\nb finish\ncustom47_limit:\n'+b.ctx(OWNER)+b.text('Status','You have used twelve updates at this age. Age up to refresh your posting schedule.')+'b finish'
 b.custom=b.routine('v47_custom_post',s)

def ui(b):
 f=b.field;st=b.state47
 release=f'adr x28,{st:#x}\nldr x0,[x28]\ncbz x0,released47\nbl 0x223e784\nreleased47:\nstr xzr,[x28]\nstr wzr,[x28,#8]\nb finish';b.release=b.routine('v47_release_scenario',release)
 s='cbz x0,finish\ncbz x2,finish\nmov x19,x0\nmov x0,x2\n'+f'bl {b.decode:#x}\ncbz w0,finish\nmov w25,w0\ncmp w25,#401\nb.lt bind47_not_ambient\ncmp w25,#410\nb.gt finish\nsub w0,w25,#401\nbl AMBIENT47\ncbz w0,bind47_community_blocked\nmov w25,#2\nbl THREAD47\nb bind47_lease\nbind47_community_blocked:\nmov w25,#6\n'+b.ctx(OWNER)+b.text('Status','This community opens when your character reaches the platform age and launch year.')+'b bind47_lease\nbind47_not_ambient:\ncmp w25,#101\nb.lt bind47_small\ncmp w25,#124\nb.le bind47_post\ncmp w25,#201\nb.lt finish\ncmp w25,#218\nb.gt finish\nsub w26,w25,#200\nmov w25,#3\n'+b.ctx(OWNER)+b.put('SelectedComment','w26')+f'bl {b.comment:#x}\nb bind47_lease\nbind47_post:\nsub w26,w25,#100\n'+b.ctx(OWNER)+f('w26',7,'Visible',out='w24')+'cbnz w24,bind47_visible_post\n'+b.set('SelectedSlot',0)+b.set('SelectedId',0)+'b bind47_post_ready\nbind47_visible_post:\n'+f('w26',7,'Slot',out='w24')+b.put('SelectedSlot')+f('w26',7,'Id',out='w24')+b.put('SelectedId')+'bind47_post_ready:\nmov w25,#2\n'+f'bl {b.thread:#x}\nb bind47_lease\nbind47_small:\ncmp w25,#1\nb.lt finish\ncmp w25,#6\nb.le bind47_standard\ncmp w25,#10\nb.lt finish\ncmp w25,#11\nb.gt finish\n'+b.ctx(OWNER)+'sub w26,w25,#10\n'+b.put('Filter','w26')+b.text('Status','Publish an update and people can leave comments. Accounts require age 13 and the platform launch year. Twelve custom updates are available at each age.')+'b bind47_lease\nbind47_standard:\ncmp w25,#2\nb.ne bind47_comment\n'+f'bl {b.thread:#x}\nb bind47_lease\nbind47_comment:\ncmp w25,#3\nb.ne bind47_lease\n'+f'bl {b.comment:#x}\nbind47_lease:\nbl {b.release:#x}\nmov x0,x19\nmov w1,#0\nbl 0x223e704\ncbz x0,finish\nadr x28,{st:#x}\nstr x0,[x28]\nstr w25,[x28,#8]\nb finish'
 s=s.replace('bl AMBIENT47',f'bl {b.ambient:#x}').replace('bl THREAD47',f'bl {b.thread:#x}');b.install('v47_bind_native_scenario',0x2ca3658,s)
 # Rebuild projections before the engine parses GFC-backed list labels.
 s='cbz x0,finish\nmov x8,x0\n'
 for platform in range(10):
  s+=h.compare_key('genesis_v18_comments47_'+str(platform).zfill(2),f'filter47_{platform}',f'filter47_next_{platform}')+f'\nfilter47_{platform}:\n'+b.ctx(OWNER)+b.set('Filter',platform)+f'bl {b.project:#x}\nb finish\nfilter47_next_{platform}:\n'
 s+=h.compare_key('genesis_v18_comments47','show47_posts','show47_checkthread')+'\nshow47_checkthread:\n'+h.compare_key('genesis_v18_comment_thread47','show47_thread','finish')+f'\nshow47_posts:\nbl {b.project:#x}\nb finish\nshow47_thread:\nbl {b.thread:#x}\nb finish'
 for name,site in [('show',0x3089aac),('load',0x304e5b8)]:b.install('v47_project_before_'+name,site,s)
 def next_scene(n):
  return b.string(scene(n))+'mov x1,x0\nldr x0,[x19,#0x190]\ncbz x0,done47\nmov x2,xzr\nbl 0x30a2278\ncbz x0,done47\nmov x1,x0\nmov x0,x19\nmov x2,xzr\nbl 0x2a21414\nb done47\n'
 def show(name):return b.string(name)+'ldr x1,[x19,#0x190]\nmov w2,#0\nmov w3,#1\nmov x4,xzr\nbl 0x3089aac\nb done47\n'
 posts=show('genesis_v18_comments47');thread=show('genesis_v18_comment_thread47')
 s='str xzr,[sp]\ncbz x0,finish\nmov x19,x0\nmov w20,w1\ncmp w20,#0\nb.lt finish\ncmp w20,#3\nb.gt finish\n'+f'adr x28,{st:#x}\nldr x0,[x28]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\nldr w26,[x28,#8]\ncbz w26,finish\nbl {b.release:#x}\ncmp w26,#2\nb.eq choice47_post\ncmp w26,#3\nb.eq choice47_comment\ncmp w26,#4\nb.eq choice47_reply\ncmp w26,#10\nb.eq choice47_account\ncmp w26,#11\nb.eq choice47_account\n'+posts
 s+='choice47_post:\n'+f'bl {b.valid:#x}\ncbz w0,invalid47_choice\ncbz w20,show47_thread_choice\ncmp w20,#1\nb.ne show47_posts_choice\n'+b.ctx(OWNER)+b.get('SelectedSlot','w25')+'mov w27,#1\nrestore47_loop:\ncmp w27,#18\nb.gt show47_thread_choice\n'+f('w25','w27','Hidden','seti',0)+'add w27,w27,#1\nb restore47_loop\n'
 s+='choice47_comment:\n'+f'bl {b.comment:#x}\ncbz w0,invalid47_choice\n'+b.ctx(OWNER)+b.get('SelectedSlot','w25')+b.get('SelectedComment','w27')+'cbz w20,toggle47_like\ncmp w20,#1\nb.eq reply47_open\ncmp w20,#2\nb.ne show47_thread_choice\n'+f('w25','w27','Hidden','seti',1)+'b show47_thread_choice\ntoggle47_like:\n'+f('w25','w27','Liked',out='w24')+'eor w24,w24,#1\n'+f('w25','w27','Liked','seti','w24')+next_scene(3)+'reply47_open:\n'+next_scene(4)
 s+='choice47_reply:\n'+f'bl {b.comment:#x}\ncbz w0,invalid47_choice\ncmp w20,#3\nb.eq reply47_back\n'+b.ctx(OWNER)+b.get('SelectedSlot','w25')+b.get('SelectedComment','w27')+'add w24,w20,#1\n'+f('w25','w27','Reply','seti','w24')+'reply47_back:\n'+next_scene(3)
 s+='choice47_account:\ncmp w20,#2\nb.eq show47_posts_choice\ncmp w20,#3\nb.eq account47_back\nsub w0,w26,#10\nmov w1,w20\n'+f'bl {b.custom:#x}\ncbz w0,blocked47_post\n'+next_scene(2)+'blocked47_post:\n'+next_scene(6)+'account47_back:\ncmp w26,#10\nb.ne account47_reddit\n'+show('genesis_v18_discord19')+'account47_reddit:\n'+show('genesis_v18_reddit19')
 s+='invalid47_choice:\n'+next_scene(5)+'show47_thread_choice:\n'+thread+'show47_posts_choice:\n'+posts+'done47:\nmov w9,#1\nstr x9,[sp]\nb finish'
 b.dispatch=b.routine('v47_native_comment_choice',s)
 for n,site in enumerate([0x2cb228c,0x2cb3bd0]):b.install('v47_native_choice_entry_'+str(n),site,f'bl {b.dispatch:#x}\ncbnz w0,return_custom\nb finish',ret=True)
 s='cbz x0,finish\nmov x19,x0\n'+f'adr x28,{st:#x}\nldr x0,[x28]\ncbz x0,finish\nbl 0x223e73c\ncmp x0,x19\nb.ne finish\nbl {b.release:#x}\nb finish'
 b.install('v47_native_comment_dismiss',0x2cb58e4,s)

def patch(raw):
 b=Patch(raw);primitives(b)
 import bank47
 bank47.primitives(b);bank47.attach(b);record(b);projection(b);custom_accounts(b);bank47.ambient(b);bank47.soundcloud(b);ui(b);return b.finish47()
if __name__=='__main__':
 output=Path(sys.argv[2]);result=patch(Path(sys.argv[1]).read_bytes())
 with output.open('wb')as stream:
  for offset in range(0,len(result),1024*1024):
   chunk=memoryview(result)[offset:offset+1024*1024]
   while chunk:
    written=stream.write(chunk);assert written;chunk=chunk[written:]
  stream.flush();__import__('os').fsync(stream.fileno())
 assert output.stat().st_size==len(result)and hashlib.sha256(output.read_bytes()).digest()==hashlib.sha256(result).digest()
 print('v47 native comments built and read-back verified',flush=True)

