"""Author native Genesis lists and scenarios; retain all v46 assets."""
import copy,csv,hashlib,io,json,sys,zipfile
from pathlib import Path
import UnityPy
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from catalog47 import *
from native_v29.content import writecsv
G=lambda k:'<GFC.comments47.'+k+'>'
def item(title,n,sub='',visible=None):
 r=dict(Title=title,Icon='iphone',SecondLine=sub,TileID='social47_'+str(n),ActionList=[dict(Index=0,ConditionList=[dict(ScenarioID=scene(n),ScenarioFile='genesis_activities_v18')])])
 if visible:r['IsVisible']=visible
 return r
def author():
 a=json.loads((SOURCE/'native_v46/assets.json').read_text());schemas=json.loads((SOURCE/'native_v46/schemas.json').read_text());schema={}
 def prop(k,v=0,hi=2147483647):schema[k]=dict(key=k,type='string'if isinstance(v,str)else'int',value=v,reset_on_ageup='',minimum=''if isinstance(v,str)else 0,maximum=''if isinstance(v,str)else hi)
 prop('Enabled',1,1)
 for k in ['Total','Head','Count','SelectedSlot','SelectedId','SelectedComment','PendingSource','PendingThread']:prop(k)
 prop('Filter',10,10);prop('PlayerName','')
 for platform in range(10):
  for topic in range(32):prop(key(100+platform,topic,'Cursor'))
 for k in ['CurrentTitle','CurrentBody','CommentName','CommentBody','LikeLabel','Status']:prop(k,'')
 for k in ['CommentLikes']:prop(k)
 for platform in range(10):prop(key(0,platform,'Seen'))
 for slot in range(1,HISTORY+1):
  for k in ['Id','Platform','Age','Year','Count','Followers','Source']:prop(key(slot,0,k))
  
  for k in ['Title','Caption','RootName','RootText','ThreadId','Topic','Event']:prop(key(slot,0,k),'')
  for c in range(1,COMMENTS+1):
   for k in ['Name','Text','Preview','MessageId','ParentId','Topic','Scenario','Event','Mood']:prop(key(slot,c,k),'')
   for k in ['Liked','Likes','Hidden','Reply','Parent','Timestamp']:prop(key(slot,c,k))
   schema[key(slot,c,'Timestamp')].update(value=-1,minimum=-1)
  for k in ['Slot','Id','Age','Year','Count','Visible']:prop(key(slot,7,k))
  prop(key(slot,7,'Title'),'')
 for c in range(1,COMMENTS+1):
  prop(key(0,c,'ViewName'),'');prop(key(0,c,'ViewText'),'');prop(key(0,c,'Visible'))
 a['genesis_v18_defaults_comments47']=writecsv(list(schema.values()));schemas['comments47']=schema
 posts=[item('About comments',1,'Your posts, character replies and saved conversations')]
 for n in range(1,HISTORY+1):posts.append(item(G(key(n,7,'Title')),100+n,'Age '+G(key(n,7,'Age'))+' · '+G(key(n,7,'Year'))+' · '+G(key(n,7,'Count'))+' comments',f'[gfc.comments47.{key(n,7,"Visible")}=1]'))
 a['genesis_v18_comments47']=json.dumps(dict(ListID='genesis_v18_comments47',Title='POSTS & COMMENTS',PresentationMode='Normal',Items=posts),indent=2)
 thread=[item('Post details',2,G('CurrentTitle'))]+[item(G(key(0,c,'ViewName')),200+c,G(key(0,c,'ViewText')),f'[gfc.comments47.{key(0,c,"Visible")}=1]')for c in range(1,COMMENTS+1)]
 a['genesis_v18_comment_thread47']=json.dumps(dict(ListID='genesis_v18_comment_thread47',Title='COMMENTS',PresentationMode='Normal',Items=thread),indent=2)
 definitions={
  1:('Post comments','New posts receive replies from characters and simulated followers. Open a post to read, like, reply to or hide a comment. The latest 24 posts and discussions save with this life. Posts made before this update have no recorded thread.',[('Recent posts',0)]),
  2:(G('CurrentTitle'),G('CurrentBody'),[('Read comments',0),('Restore hidden comments',0),('Recent posts',0)]),
  3:(G('CommentName'),G('CommentBody'),[(G('LikeLabel'),0),('Reply',0),('Hide comment',0),('Back to comments',0)]),
  4:('Reply to '+G('CommentName'),'Choose a reply. Your reply and their response will stay in this thread.',[('Thanks for the support!',0),('Share more context',0),('Respectfully disagree',0),('Back',0)]),
  5:('Post unavailable','That post is no longer in your recent history. New posts replace the oldest thread once 24 posts are stored.',[('Recent posts',0)]),
  6:('Posting unavailable',G('Status'),[('Recent posts',0)]),
 }
 for platform in range(2):definitions[10+platform]=(PLATFORMS[platform]+' profile',G('Status'),[('Post about my interests',0),('Post about school or my team',0),('My posts & comments',0),('Back',0)])
 for n in range(1,HISTORY+1):definitions[100+n]=definitions[2]
 for n in range(1,COMMENTS+1):definitions[200+n]=definitions[3]
 for platform in [0,1,6,8,9]:definitions[401+platform]=definitions[2]
 for sheet in ['genesis_activities_v18','genesis_activities_v12']:
  rows=list(csv.DictReader(io.StringIO(a[sheet])));header=list(rows[0])
  for n,(title,body,choices)in definitions.items():
   r=dict.fromkeys(header,'');r.update(ScenarioID=scene(n),Style='normal',ExteriorTitle='Social Media',Title=title,Body=body,EmojiString='iphone',HasDismissButton='true')
   if n==3 or 201<=n<=218:r['TableRows']=json.dumps([dict(row=1,key='Likes:',value=G('CommentLikes'))])
   for i,(label,_)in enumerate(choices,1):r[f'Choice{i}_Text']=label;r[f'Choice{i}_ButtonStyle']='normal';r[f'Choice{i}_RouteTo']='BP_SHOW_LIST=genesis_v18_comments47'
   rows.append(r)
  a[sheet]=writecsv(rows)
 for owner in ['discord19','reddit19']:
  doc=json.loads(a['genesis_v18_'+owner]);doc['Items'].append(dict(Title='Posts & comments',Icon='iphone',SecondLine='Read and reply to comments on your posts',TileID='comments47_'+owner,ActionList=[dict(Index=0,ConditionList=[dict(ListID='genesis_v18_comments47_'+str(int(owner=='reddit19')).zfill(2))])]))
  if owner in ['discord19','reddit19']:
   doc['Items'][0]['ActionList'][0]['ConditionList']=[dict(ScenarioID=scene(10+int(owner=='reddit19')),ScenarioFile='genesis_activities_v18')]
  a['genesis_v18_'+owner]=json.dumps(doc,indent=2)
 lines=a['genesis_feature_containers'].splitlines();start=next(i for i,l in enumerate(lines)if l.startswith('ContainerId,'));rr=list(csv.DictReader(io.StringIO('\n'.join(lines[start:]))))
 row=dict.fromkeys(rr[0],'');row.update(ContainerId='comments47',DisplayName='Post comments',InitDataSheet='genesis_v18_defaults_comments47',AgeUpPriority='content');rr.append(row)
 # Add a direct action beside the existing follow entry in each native
 # platform account menu. Keep the original follow list definition intact.
 for platform in range(2,9):
  owner='comment_entry47_'+str(platform);row=dict.fromkeys(rr[0],'');row.update(ContainerId=owner,DisplayName='Post comments',InitDataSheet='genesis_v18_defaults_comment_entry47',AgeUpPriority='content',EntryMenu='SocialFollowing'+str(platform),EntryLabel='Posts & comments',EntryEmoji='iphone',EntrySecondLine='Read and reply to comments on this account',EntryOrder='30',EntryListID='genesis_v18_comments47_'+str(platform).zfill(2));rr.append(row)
  schemas[owner]={'Enabled':dict(key='Enabled',type='int',value=1,reset_on_ageup='',minimum=0,maximum=1)}
 a['genesis_v18_defaults_comment_entry47']='key,type,value,reset_on_ageup,minimum,maximum\r\nEnabled,int,1,,0,1'
 row=dict.fromkeys(rr[0],'');row.update(ContainerId='following47_9',DisplayName='SoundCloud comments',InitDataSheet='genesis_v18_defaults_following47_9',AgeUpPriority='content',EntryMenu='SocialFollowing9',EntryLabel='Posts & comments',EntryEmoji='iphone',EntrySecondLine='Track discussions and replies',EntryOrder='30',EntryListID='genesis_v18_comments47_09');rr.append(row)
 a['genesis_v18_defaults_following47_9']='key,type,value,reset_on_ageup,minimum,maximum\r\nEnabled,int,1,,0,1';schemas['following47_9']={'Enabled':dict(key='Enabled',type='int',value=1,reset_on_ageup='',minimum=0,maximum=1)}
 a['genesis_feature_containers']='\r\n'.join(lines[:start])+'\r\n'+writecsv(rr)
 for platform,name in enumerate(PLATFORMS):
  doc=json.loads(a['genesis_v18_comments47']);doc['ListID']='genesis_v18_comments47_'+str(platform).zfill(2);doc['Title']=name.upper()+' POSTS & COMMENTS'
  if platform in [0,1,6,8,9]:doc['Items'].insert(1,item('Community discussion',401+platform,'Read a conversation and leave a reply'))
  a[doc['ListID']]=json.dumps(doc,indent=2)
 (ROOT/'assets.json').write_text(json.dumps(a,indent=2)+'\n');(ROOT/'schemas.json').write_text(json.dumps(schemas,indent=2)+'\n');return a
def build(base,out):
 a=author();out=Path(out);out.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(base)as z:env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'));data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'))
 sha=lambda b:hashlib.sha256(b).hexdigest();key=lambda o:(o.assets_file.name,o.path_id)
 before={key(o):sha(o.get_raw_data())for o in env.objects};beforedata={key(o):sha(o.get_raw_data())for o in data.objects}
 texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'};rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree();original=list(tree['m_Container']);rid=next(n+1 for n,e in enumerate(rm.assets_file.externals)if e.path=='resources.assets')
 file=texts['genesis_activities_v18'].assets_file;nextid=max(file.objects)+1;changed=set();added=[]
 for name,value in a.items():
  if name in texts and texts[name].read().m_Script==value:continue
  if name in texts:obj=texts[name];changed.add(key(obj))
  else:
   obj=copy.copy(texts['genesis_test_feature_events']);obj.path_id=nextid;nextid+=1;obj.data=obj.get_raw_data();file.objects[obj.path_id]=obj;added.append(name)
   path=('genesis_lists/'if value.startswith('{')else'genesis/')+name;assert path not in dict(tree['m_Container']);tree['m_Container'].append((path,dict(m_FileID=rid,m_PathID=obj.path_id)))
  v=obj.read();v.m_Name=name;v.m_Script=value;v.save()
 tree['m_Container'].sort(key=lambda x:x[0]);rm.save_typetree(tree)
 bundle=next(iter(env.files.values())).save(packer='original');db=next(iter(data.files.values())).save(packer='original')
 for name,payload in [('datapack.unity3d',bundle),('data.unity3d',db)]:
  destination=out/name
  with destination.open('wb')as stream:
   for offset in range(0,len(payload),1024*1024):stream.write(payload[offset:offset+1024*1024])
  assert sha(destination.read_bytes())==sha(payload)
 ae=UnityPy.load(bundle);ad=UnityPy.load(db);after={key(o):sha(o.get_raw_data())for o in ae.objects};afterdata={key(o):sha(o.get_raw_data())for o in ad.objects}
 assert set(before)<=set(after)and{k for k in before if before[k]!=after[k]}==changed
 assert set(beforedata)==set(afterdata)and{k for k in beforedata if beforedata[k]!=afterdata[k]}=={key(rm)}
 from collections import Counter
 canonical=lambda rows:Counter((path,json.dumps(value,sort_keys=True))for path,value in rows)
 final_paths=next(o for o in ad.objects if o.type.name=='ResourceManager').read_typetree()['m_Container']
 assert not(canonical(original)-canonical(final_paths))
 vals={o.read().m_Name:o.read().m_Script for o in ae.objects if o.type.name=='TextAsset'};assert all(vals[k]==v for k,v in a.items())
 report=dict(passed=True,modified_TextAssets=len(changed),added_TextAssets=added,unedited_Unity_objects_preserved=True,existing_resource_paths_preserved=True,datapack_sha256=sha(bundle),data_sha256=sha(db))
 (ROOT/'assets47_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':build(*sys.argv[1:])
