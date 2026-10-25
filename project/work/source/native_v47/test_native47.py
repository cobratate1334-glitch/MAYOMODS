"""Execute comment ARM64 with hostile managed/Unity API boundary mocks.

These checks exercise the actual assembled hook and callback instructions at
two load addresses. They do not claim Android or Unity rendering coverage.
"""
import copy,hashlib,json,shutil,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from catalog47 import *
from native_v46 import test_native46 as old
from test_native import X
for mod in list(sys.modules.values()):
 if str(getattr(mod,'__file__','')).startswith(str(SOURCE))and'test_'in str(getattr(mod,'__file__',''))and hasattr(mod,'ROOT'):mod.ROOT=ROOT
for name in ['portrait42_catalog.json','portrait43_catalog.json','selector34_options.json','dealer_routes46.json']:
 if not(ROOT/name).exists():shutil.copyfile(SOURCE/'native_v46'/name,ROOT/name)
LIVE_ENGINES=[]
class Machine(old.Machine):
 def __init__(self,raw,bias):
  LIVE_ENGINES.append(self);super().__init__(raw,bias);self.new47={0x59c70c0,0x4e0240c,0x25eda3c,0x224ce70,0x4dfff50,0x30611d0};self.post_receipts=[];self.injected47=[]
  for a in self.new47:self.map(a+bias,4)
  for a,n in [(0x4e00114,0xc0),(0x4df3450,0xac)]:self.map(a+bias,n);self.u.mem_write(a+bias,self.load(a,n))
  if 'bank_data_va'in self.d:
   a=self.d['bank_data_va'];n=self.d['bank_data_bytes'];self.map(a+bias,n);self.u.mem_write(a+bias,self.load(a,n))
 def cstr(self,a):
  out=bytearray()
  while True:
   ch=bytes(self.u.mem_read(a+len(out),1))
   if ch==b'\0':return out.decode()
   out+=ch;assert len(out)<20000
 def mock(self,u,pc,size,data):
  va=pc-self.bias
  if va==0x30a2278:
   a=[u.reg_read(r)for r in X[:3]];name=self.str(a[1])
   if name.startswith(PREFIX):
    assert a[0]==self.controller46 and a[2]==0;value=self.alloc();self.next_scenes.append((value,name));self.finish_api(u.reg_read(X[30]),value);return
  if va not in getattr(self,'new47',set()):return super().mock(u,pc,size,data)
  a=[u.reg_read(r)for r in X[:8]];lr=u.reg_read(X[30])
  if va==0x59c70c0:
   fmt=self.cstr(a[2]);args=(a[3]&0xffffffff,a[4]&0xffffffff,self.cstr(a[5]))if fmt=='P%dC%d%s'else tuple(a[i]&0xffffffff for i in ([3,4]if fmt=='%d:%02d · 'else[3,4,5]));text=fmt%args;payload=text.encode();assert len(payload)<a[1];u.mem_write(a[0],payload+b'\0');value=len(payload)
  elif va==0x4e0240c:assert a[3]==0;value=self.managed(self.str(a[0]).replace(self.str(a[1]),self.str(a[2])))
  elif va==0x224ce70:value=self.alloc(a[0]*2+32);self.w(value+16,a[0])
  elif va==0x4dfff50:
   text=self.str(a[2]);assert a[1]+len(text.encode('utf-16-le'))//2<=self.rw(a[0]+16);u.mem_write(a[0]+20+2*a[1],text.encode('utf-16-le'));value=0
  elif va==0x30611d0:self.injected47.append((a[0],self.str(a[1])));assert a[2]==0;value=0
  elif va==0x25eda3c:assert 1<=a[1]<=7 and a[2]==0;value=self.managed(self.str(self.rq(a[0]+16)).title())
  self.finish_api(lr,value)
 def social_scene(self,n):
  obj=self.alloc();self.q(obj+0x190,self.controller46);self.hook42('v47_bind_native_scenario',{0:obj,2:self.managed(scene(n))});return obj
 def social_choose(self,obj,index,entry=0):
  r=next(r for r in self.d['hooks']if r['name']=='v47_native_choice_entry_'+str(entry));return self.execute42(r['stub'],{0:obj,1:index})
 def post(self,platform=2,count=1,followers=80,topic=0,caption='An update'):
  return self.routine42('v47_record_post',{0:platform,1:self.managed(caption),2:count,3:followers,4:topic,5:0})
 def posts(self):self.routine42('v47_project_recent_posts');return self.props[OWNER]
 def open_latest(self):self.posts();return self.social_scene(101)
 def native_post(self,channel,count,topic='selfie',followers=100):
  obj=self.alloc();native=self.alloc();typ=self.alloc();self.q(typ+16,self.managed(topic));self.w(native+16,channel);self.w(native+28,count);self.w(native+32,followers);self.q(obj+0x170,native);self.q(obj+0x178,typ);self.q(obj+0x48,self.managed('The native post result.'))
  self.hook42('v47_native_post_completed',{19:obj});return obj

def validate(binary,before):
 raw=Path(binary).read_bytes();base=Path(before).read_bytes();d=json.loads((ROOT/'native_hooks.json').read_text());checks=0
 def check(ok,label):
  nonlocal checks
  assert ok,label;checks+=1
 check(hashlib.sha256(raw).hexdigest()==d['binary_sha256'],'binary binding');check(hashlib.sha256(base).hexdigest()==d['base_v46_sha256'],'input binding')
 for bias in [0,0x1000000000]:
  m=Machine(raw,bias);p=m.props[OWNER];m.year45(2026)
  check(m.routine42('v47_decode_scene',{0:m.managed(scene(101))})==101,'exact managed scenario parser')
  for text in [PREFIX+'1',PREFIX+'1000',PREFIX+'a01','other.'+scene(101),scene(101)+'x','',PREFIX+'-01']:
   check(m.routine42('v47_decode_scene',{0:m.managed(text)})==0,'malformed scenario rejected '+text)
  for n in [0,1,6,10]:
   for name in TOPICS.get(n,[]):check(m.routine42('v47_post_topic',{0:m.managed(name)})==n,'native post-type topic '+name)
  m.posts();check(p['Count']==0 and all(p[key(i,7,'Visible')]==0 for i in range(1,25)),'old save has an honest empty history')
  # Successful native callback for all seven native social channels, including
  # actual channel IDs, post counts, topic and native body write barrier.
  for channel in range(1,8):
   obj=m.native_post(channel,10+channel);slot=p['Head']
   check(p[key(slot,0,'Platform')]==channel+1 and p[key(slot,0,'Caption')]=='Selfie','native receipt platform '+str(channel))
   check('Read comments'in m.str(m.rq(obj+0x48)),'stock completion retains body and points to comments')
  total=p['Total'];m.native_post(7,17);check(p['Total']==total,'same native receipt is idempotent')
  m.hook42('v47_native_account_deleted',{1:7});m.native_post(7,1);check(p['Total']==total+1,'recreated native account gets a fresh thread')
  # The real SoundCloud publication callback sees the committed native track.
  activity=m.alloc();account=m.alloc();track=m.alloc();m.q(track+16,m.managed('Studio weekend'));m.q(account+0x38,m.list([track]));m.w(account+0x28,2000);m.q(activity+0x78,account);m.q(activity+0x40,track)
  m.hook42('v47_soundcloud_track_published',{19:activity});slot=p['Head'];check(p[key(slot,0,'Platform')]==9 and p[key(slot,0,'Caption')]=='Studio weekend','actual SoundCloud upload callback')
  total=p['Total'];m.hook42('v47_soundcloud_track_published',{19:activity});check(p['Total']==total+1,'SoundCloud publish remains valid when an account reuses the same track count');slot=p['Head']
  listobj=m.list([]);m.hook42('v47_soundcloud_existing_account_actions',{19:listobj});check(m.injected47[-1]==(listobj,'SocialFollowing9'),'existing SoundCloud account list injection')
  m.posts();m.social_scene(101);p[key(slot,1,'Timestamp')]=84;m.social_scene(201);check('1:24 · 'in p['CommentBody'],'timed SoundCloud comment formatter')
  # One live friend can comment; deceased/minor friends are skipped.
  dead=m.alloc();young=m.alloc();friend=m.alloc();m.w(dead+24,0);m.w(young+24,1);m.w(young+32,12);m.w(friend+24,1);m.w(friend+32,22);m.q(m.life+0x198,m.list([dead,young,friend]))
  check(m.post(2,40,80,7,'School update')>0,'fallback receipt');slot=p['Head']
  check(p[key(slot,1,'Name')]=='Contact '+str(friend),'live age-appropriate native friend name')
  check(p[key(slot,0,'Count')]==3,'small community gets three saved comments')
  check(len({p[key(slot,c,'Name')]for c in range(1,4)})==3,'unique visible authors')
  check(all(p[key(slot,c,'Text')]in REACTIONS[7]for c in range(1,4)),'reactions match post content')
  # All NPC strings and per-comment actions persist as values, never pointers.
  obj=m.open_latest();check(p['CurrentTitle']=='Facebook · School update','post alias opens the selected saved post')
  m.social_choose(obj,0);check(m.shown_lists[-1]=='genesis_v18_comment_thread47','native Read comments button')
  comment=m.social_scene(201);check(p['CommentName']==p[key(slot,1,'Name')],'native comment alias selects correct author')
  m.social_choose(comment,0,1);check(p[key(slot,1,'Liked')]==1 and m.next_scenes[-1][1]==scene(3),'like native overload two')
  again=m.social_scene(3);m.social_choose(again,0);check(p[key(slot,1,'Liked')]==0,'unlike native overload one')
  comment=m.social_scene(3);m.social_choose(comment,1);check(m.next_scenes[-1][1]==scene(4),'reply menu opens')
  reply=m.social_scene(4);m.social_choose(reply,1);check(p[key(slot,1,'Reply')]==2,'reply choice persisted')
  m.social_scene(3);check(REPLIES[1]in p['CommentBody']and FOLLOWUPS[1]in p['CommentBody'],'thread includes player and NPC replies')
  comment=m.social_scene(3);m.social_choose(comment,2);check(p[key(slot,1,'Hidden')]==1,'hide saves moderation state')
  m.routine42('v47_prepare_thread');check(p[key(0,1,'Visible')]==0,'hidden comment removed from visible list')
  details=m.social_scene(2);m.social_choose(details,1);m.routine42('v47_prepare_thread');check(p[key(slot,1,'Hidden')]==0 and p[key(0,1,'Visible')]==1,'restore hidden comments works')
  stale=m.social_scene(201);m.social_scene(202);beforep=copy.deepcopy(p);check(m.routine42('v47_native_comment_choice',{0:stale,1:0})==0 and p==beforep,'replaced popup cannot mutate another comment')
  dismiss=m.social_scene(3);m.hook42('v47_native_comment_dismiss',{0:dismiss});check(m.rq(d['states'][OWNER]['va']+bias)==0,'dismiss releases rooted scenario')
  # Every supplied platform uses its own linked conversation. Direct replies
  # refer to the real player root; nested replies retain the pack parent ID.
  for platform,prefix in [(0,'DSC-'),(1,'RDT-'),(6,'YTB-'),(8,'OFS-'),(9,'SCD-')]:
   m.post(platform,200+platform,5000,3,'My actual upload');slot=p['Head'];count=p[key(slot,0,'Count')]
   check(1<=count<=18 and p[key(slot,0,'ThreadId')].startswith(prefix),'correct platform pack')
   for c in range(1,count+1):
    parent=p[key(slot,c,'Parent')];check(0<=parent<c,'parents precede their nested replies')
    check(p[key(slot,c,'ParentId')]==p[key(slot,0,'ThreadId')]if parent==0 else p[key(slot,c,'ParentId')]==p[key(slot,parent,'MessageId')],'exact saved parent message ID')
    check('{{'not in p[key(slot,c,'Text')]and p[key(slot,c,'MessageId')].startswith(prefix),'expanded text and platform identity')
   used=[m.routine42('v47_pick_pack_thread',{0:platform,1:0,2:0})for _ in range(12)];check(len(used)==len(set(used)),'per-save thread cursor prevents repeats')
   seen=p[key(0,platform,'Seen')];obj=m.social_scene(401+platform);check(p[key(p['Head'],0,'Source')]==1 and p[key(p['Head'],0,'RootText')],'ambient roots remain community posts')
   check(p[key(0,platform,'Seen')]==seen,'ambient conversations preserve native post watermark')
   m.posts();m.social_scene(101);nested=next((c for c in range(1,p[key(p['Head'],0,'Count')]+1)if p[key(p['Head'],c,'Parent')]),None)
   if nested:
    m.social_scene(200+nested);check('In reply to 'in p['CommentBody'],'nested reply context rendered')
  total=p['Total'];m.year45(2026,17);check(m.post(8,999,1000,0)==0 and p['Total']==total,'adult character gate on native receipt')
  check(m.routine42('v47_pick_pack_thread',{0:8,1:0,2:0})==0,'adult character gate on indexed pack')
  m.year45(2026,30)
  for platform in range(10):
   m.hook42('v47_project_before_show',{0:m.managed('genesis_v18_comments47_'+str(platform).zfill(2))});check(p['Filter']==platform,'existing account sets its own filter')
   for rank in range(1,25):
    if p.get(key(rank,7,'Visible')):check(p[key(p[key(rank,7,'Slot')],0,'Platform')]==platform,'platform list has no cross-wired posts')
  p['Filter']=10
  # Real custom account posting, quota and historical platform boundaries.
  for platform,launch in [(0,2015),(1,2005)]:
   m.props['social_v18']['PostsUsed']=0;m.year45(launch,13);obj=m.social_scene(10+platform);m.social_choose(obj,0);check(m.next_scenes[-1][1]==scene(2),'custom account creates post and opens its thread')
   check(m.props['social_v18'][f'P{platform}Posts']>=1,'existing custom post count retained')
   total=p['Total'];m.year45(launch-1,13);obj=m.social_scene(10+platform);m.social_choose(obj,0);check(p['Total']==total and m.next_scenes[-1][1]==scene(6),'platform unavailable before launch')
   m.year45(launch,12);obj=m.social_scene(10+platform);m.social_choose(obj,0);check(p['Total']==total,'under-13 cannot post')
  m.year45(2026,20);m.props['social_v18']['PostsUsed']=12;total=p['Total'];obj=m.social_scene(10);m.social_choose(obj,1);check(p['Total']==total and'twelve'in p['Status'],'posting quota cannot be bypassed')
  m.props['social_v18']['PostsUsed']=0;obj=m.social_scene(11);m.social_choose(obj,1);check(p[key(p['Head'],0,'Caption')]=='An update about school or my team','school post has its own caption')
  # Repeated posting wraps a bounded ring. Saved selections carry immutable
  # post IDs, so a slot reused during navigation cannot target the new post.
  m.posts();oldslot=p['Head'];oldid=p['SelectedId']
  for i in range(1,31):m.post(2,100+i,1000000,2,'Game post '+str(i))
  check(p['Count']==24 and p['Head']in range(1,25),'bounded ring wraps')
  p['Filter']=10;m.posts();ids=[p[key(i,7,'Id')]for i in range(1,25)];check(ids==list(range(p['Total'],p['Total']-24,-1)),'recent posts ordered newest first')
  check(all(p[key(i,7,'Visible')]==1 for i in range(1,25)),'24 valid native list rows')
  p['SelectedSlot']=oldslot;p['SelectedId']=oldid;check(m.routine42('v47_selected_post_valid')==0,'evicted post identity rejected')
  m.open_latest();saved=copy.deepcopy(m.props);selected=(p['SelectedSlot'],p['SelectedId']);del m
  m=Machine(raw,bias);m.props=copy.deepcopy(saved);p=m.props[OWNER];check(m.routine42('v47_selected_post_valid')==1 and(selected==(p['SelectedSlot'],p['SelectedId'])),'new process resolves saved ID without pointers')
  m.routine42('v47_prepare_thread');check(p[key(0,1,'Visible')]==1 and p['Count']==24,'saved comments rebuild after restart')
  obj=m.social_scene(201);m.social_choose(obj,3);check(m.shown_lists[-1]=='genesis_v18_comment_thread47','back button uses native list')
  # Distinct lives have isolated container values even in the same process.
  p.update(SelectedSlot=0,SelectedId=0);check(m.routine42('v47_selected_post_valid')==0,'empty new life cannot reuse a previous selection')
 # Pinned retained code and declared edit boundaries are independently checked.
 m=Machine(raw,0);allowed=bytearray(len(raw));a,z=d['v47_new_code_range'];allowed[m.off47(a):m.off47(z-1)+1]=b'\1'*(z-a)
 for a,n,_ in d['v47_changed_ranges']:allowed[m.off47(a):m.off47(a)+n]=b'\1'*n
 for a,n in d['v47_program_header_ranges']:allowed[a:a+n]=b'\1'*n
 check(len(raw)>len(base)and all(a==z or allowed[i]for i,(a,z)in enumerate(zip(raw,base))),'only declared native changes')
 report=dict(passed=True,checks=checks,binary_sha256=hashlib.sha256(raw).hexdigest(),native_post_channels=8,custom_post_channels=2,pack_records=17955,real_native_String_Concat_executed=True,aslr_biases=[0,0x1000000000],volatile_registers_clobbered=True,saved_threads_reloaded=True,bounded_history=24,stale_clicks_rejected=True,physical_phone_tested=False,Unity_rendering_tested=False)
 (ROOT/'native47_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
def off47(self,va):return next(s['p_offset']+va-s['p_vaddr']for s in self.loads if s['p_vaddr']<=va<s['p_vaddr']+s['p_filesz'])
Machine.off47=off47
if __name__=='__main__':validate(*sys.argv[1:]);sys.stdout.flush();__import__('os')._exit(0)
