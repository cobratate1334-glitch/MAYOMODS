"""Validate the supplied JSON-line message pack and build a native offset index."""
import collections,hashlib,json,re,struct,sys,zipfile,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PLATFORM_IDS={'Discord':0,'Reddit':1,'YouTube':6,'OnlyFans':8,'SoundCloud':9}
BANK_VA=0x6578000
def topic_id(text):
 s=text.lower()
 for n,words in [(3,['music','song','track','beat','mix','album','instrument','piano','guitar','lo-fi','synth','bass','vocal','remix','demo','producer','electronic','folk','hip-hop','jazz','ambient','orchestral']), (2,['game','gaming','esports']), (4,['learn','tutorial','tech','support','resource','study']), (5,['food','cook','coffee','recipe']), (8,['fitness','sport','training']), (1,['photo','travel']), (9,['art','creative','design','showcase','workspace','workflow','fashion']), (10,['stream','live','chat','hangout','party']), (7,['school','weekend','life','progress'])]:
  if any(w in s for w in words):return n
 return 0
def build(path):
 path=Path(path);records=[];roots=[]
 with zipfile.ZipFile(path)as z:
  manifest=json.loads(z.read('manifest.json'));guide=z.read('IMPORT_GUIDE.txt').decode()
  for platform in PLATFORM_IDS:
   part=[json.loads(l)for l in z.read(platform+'_messages.txt').decode().splitlines()if l.startswith('{')]
   assert part and all(r['platform']==platform for r in part);records+=part
 ids={r['id']:r for r in records};assert len(ids)==len(records)==17955
 groups=collections.defaultdict(list)
 for r in records:
  assert r['age_gate']==(18 if r['platform']=='OnlyFans'else 0)
  assert isinstance(r['text'],str)and'\0'not in r['text'] and len(r['text'].encode())<8192
  if r['parent_id'] is not None:
   parent=ids[r['parent_id']];assert parent['platform']==r['platform']and parent['thread_id']==r['thread_id']
  else:assert r['id']==r['thread_id'];roots.append(r)
  groups[r['thread_id']].append(r)
 # Layout: pools[10 platforms * 11 topics * 2 sources], pool thread indices,
 # thread records (32 bytes), message records (48 bytes), NUL-ended UTF-8.
 threads=[];ordered=[];details=[]
 for root in roots:
  rr=groups[root['id']];children=collections.defaultdict(list)
  for r in rr:
   if r['parent_id']:children[r['parent_id']].append(r)
  order=[];seen=set()
  def visit(r):
   assert r['id']not in seen;seen.add(r['id']);order.append(r)
   for child in children[r['id']]:visit(child)
  visit(root);assert len(order)==len(rr)<=19
  ordinal={r['id']:i for i,r in enumerate(order)};start=len(ordered);ordered+=order
  threads.append((root,start,len(order)-1));details.append(dict(id=root['id'],platform=root['platform'],topic=root['topic'],topic_id=topic_id(root['topic']),player=bool(root.get('template_anchor')),records=[dict(id=r['id'],parent=r['parent_id'],ordinal=i,parent_ordinal=ordinal.get(r['parent_id'],0))for i,r in enumerate(order)]))
 pool_count=10*11*2;pool_entries=[];indices=[]
 for platform in range(10):
  for topic in range(11):
   for source in range(2):
    matched=[i for i,(r,_,_)in enumerate(threads)if PLATFORM_IDS[r['platform']]==platform and bool(r.get('template_anchor'))==(source==0)and(topic==0 or topic_id(r['topic'])==topic)]
    pool_entries.append((len(indices),len(matched)));indices+=matched
 pools_offset=0;indices_offset=pool_count*8;threads_offset=(indices_offset+len(indices)*4+15)&~15;records_offset=threads_offset+len(threads)*32;strings_offset=records_offset+len(ordered)*48
 blob=bytearray(strings_offset);strings={};
 def string(s):
  s=''if s is None else str(s)
  if s not in strings:strings[s]=len(blob);blob.extend(s.encode()+b'\0')
  return strings[s]
 for i,(start,count)in enumerate(pool_entries):struct.pack_into('<II',blob,i*8,indices_offset+start*4,count)
 for i,index in enumerate(indices):struct.pack_into('<I',blob,indices_offset+i*4,index)
 for i,(root,start,count)in enumerate(threads):
  struct.pack_into('<8I',blob,threads_offset+i*32,records_offset+start*48,count,PLATFORM_IDS[root['platform']],topic_id(root['topic']),int(bool(root.get('template_anchor'))),string(root['id']),string(root.get('title')),string(root['trigger']))
 for i,r in enumerate(ordered):
  # Parent ordinal is relative to the root and matches the saved comment slot.
  thread=next(t for t in details if t['id']==r['thread_id']);parent=next(x['parent_ordinal']for x in thread['records']if x['id']==r['id'])
  preview=re.sub(r'\{\{[^}]+\}\}','you',r['text']);preview=preview[:110]+('…'if len(preview)>110 else'')
  values=[string(r['id']),string(r['parent_id']),string(r['username']),string(r['text']),string(r['topic']),string(r['scenario']),string(r['trigger']),string(r['sentiment']),0xffffffff if r['timestamp_seconds']is None else int(r['timestamp_seconds']),int(r['like_count']),parent,string(preview)]
  struct.pack_into('<12I',blob,records_offset+i*48,*values)
 assert sum(len(re.findall(r"\b\w+(?:['’-]\w+)*\b",r['text']))for r in records)==702249
 out=ROOT/'message_pack';out.mkdir(exist_ok=True);shutil.copyfile(path,out/'MayoMods_Social_Message_Pack_700k.zip');(out/'IMPORT_GUIDE.txt').write_text(guide)
 (ROOT/'social_bank47.bin').write_bytes(blob)
 report=dict(passed=True,input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bank_sha256=hashlib.sha256(blob).hexdigest(),bank_va=BANK_VA,bytes=len(blob),records=len(records),words=702249,threads=len(threads),player_threads=sum(t['player']for t in details),pools=pool_count,threads_offset=threads_offset,records_offset=records_offset,strings_offset=strings_offset,platforms=PLATFORM_IDS,max_thread_records=max(len(t['records'])for t in details),root_parent_platform_links_valid=True)
 (ROOT/'message_pack47_validation.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'message_index47.json').write_text(json.dumps(details,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':build(sys.argv[1])
