"""Offset-indexed UTF-8 pack: native selection, tokens, parents and upload hooks."""
import json
from catalog47 import *
from native_hooks import h
from import_pack47 import BANK_VA
def primitives(b):
 f=b.field;b.bank_info=json.loads((b.root47/'message_pack47_validation.json').read_text())
 # The exact mscorlib module resolves String.Replace(String,String) to this
 # function; String.Concat(String,String,String) is 0x4e00114, not Format.
 s='str x0,[sp]\ncbz x0,finish\nmov x19,x0\n'+b.ctx(OWNER)
 s+=b.string('PlayerName')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nmov x3,xzr\nbl 0x3059934\nmov x20,x0\n'
 s+=b.get('SelectedSlot','w25')+f('w25',0,'Caption','gets',out='x26')
 for token,value in [('PLAYER_NAME','name'),('CREATOR_NAME','name'),('VIDEO_TITLE','caption'),('STREAM_TITLE','caption'),('TRACK_TITLE','caption'),('PLAYLIST_NAME','caption'),('SERVER_NAME','community')]:
  s+=b.string('{{'+token+'}}')+'mov x1,x0\n'
  if value=='community':s+=b.string('My community')+'mov x22,x0\n'+b.string('{{'+token+'}}')+'mov x1,x0\nmov x2,x22\n'
  else:s+='mov x2,'+('x20'if value=='name'else'x26')+'\n'
  s+='mov x0,x19\nmov x3,xzr\nbl 0x4e0240c\nmov x19,x0\n'
 s+='str x19,[sp]\nb finish';b.expand=b.routine('v47_expand_pack_tokens',s)
 # Pool cursors save the next index. Every thread in a matched pool is used
 # once before cycling. A missing topic falls back within the same platform.
 s='str xzr,[sp]\ncmp w0,#9\nb.hi finish\ncmp w1,#10\nb.hi finish\ncmp w2,#1\nb.hi finish\nmov w19,w0\nmov w20,w1\nmov w25,w2\n'+b.ctx(OWNER)+'cmp w23,#13\nb.lt finish\n'+f'bl {b.old["v45_current_year"]["stub"]:#x}\n'+''.join(f'cmp w19,#{i}\nb.ne bank47_year_{i}\ncmp w0,#{year}\nb.lt finish\nbank47_year_{i}:\n'for i,year in enumerate(LAUNCH))+'cmp w19,#8\nb.ne select47_age_ok\ncmp w23,#18\nb.lt finish\nselect47_age_ok:\n'+f'adr x27,{BANK_VA:#x}\nselect47_pool:\nmov w9,#11\nmadd w9,w19,w9,w20\nlsl w9,w9,#1\nadd w9,w9,w25\nadd x28,x27,w9,uxtw #3\nldr w26,[x28,#4]\ncbnz w26,select47_cursor\ncbz w20,finish\nmov w20,#0\nb select47_pool\nselect47_cursor:\nadd w23,w19,#100\nadd w22,w20,w25,lsl #4\n'+f('w23','w22','Cursor',out='w24')+'cmp w24,#1\nb.lt select47_random\ncmp w24,w26\nb.le select47_have\nselect47_random:\nmov w0,#0\nmov w1,w26\nmov x2,xzr\nbl 0x2e0b54c\nadd w24,w0,#1\nselect47_have:\nmov w20,w24\nadd w24,w24,#1\ncmp w24,w26\nmov w9,#1\ncsel w24,w24,w9,le\n'+f('w23','w22','Cursor','seti','w24')+'ldr w9,[x28]\nadd x9,x27,w9,uxtw\nsub w20,w20,#1\nldr w9,[x9,w20,uxtw #2]\nadd w9,w9,#1\nstr x9,[sp]\nb finish'
 b.pick=b.routine('v47_pick_pack_thread',s)

def attach(b):
 f=b.field;info=b.bank_info
 s='mov w25,w0\nmov w26,w1\n'+b.ctx(OWNER)+b.get('PendingSource','w20')+b.get('PendingThread','w24')+'mov w27,w24\n'+b.set('PendingSource',0)+b.set('PendingThread',0)+f('w25',0,'Source','seti','w20')+'cbnz w27,bank47_have\n'+f('w25',0,'Platform',out='w0')+'mov w1,w26\nmov w2,w20\n'+f'bl {b.pick:#x}\nmov w27,w0\nbank47_have:\ncbz w27,finish\ncmp w27,#{info["threads"]}\nb.hi finish\nsub w27,w27,#1\n'+f'adr x23,{BANK_VA:#x}\nmov w9,#{info["threads_offset"]}\nadd x24,x23,x9\nlsl x9,x27,#5\nadd x24,x24,x9\nldr w9,[x24]\nadd x28,x23,w9,uxtw\nldr w27,[x24,#8]\n'+f('w25',0,'Platform',out='w0')+'cmp w27,w0\nb.ne finish\nldr w27,[x24,#16]\nmov w9,#1\nsub w9,w9,w20\ncmp w27,w9\nb.ne finish\nldr w26,[x24,#4]\ncmp w26,#18\nb.hi finish\n'+f('w25',0,'Count','seti','w26')
 # Root metadata is retained even when the player-authored root substitutes
 # for the template. World-feed roots retain their own author and body.
 for off,field in [(0,'ThreadId'),(16,'Topic'),(24,'Event')]:
  s+=f'ldr w0,[x28,#{off}]\nadd x0,x23,w0,uxtw\nbl {h.NEW_STRING:#x}\nmov x22,x0\n'+f('w25',0,field,'sets','x22')
 s+='cbz w20,bank47_player_root\n'
 for off,field in [(8,'RootName'),(12,'RootText')]:
  s+=f'ldr w0,[x28,#{off}]\nadd x0,x23,w0,uxtw\nbl {h.NEW_STRING:#x}\nbl {b.expand:#x}\nmov x22,x0\n'+f('w25',0,field,'sets','x22')
 s+='b bank47_children\nbank47_player_root:\n'+f('w25',0,'RootName','sets','xzr')+f('w25',0,'RootText','sets','xzr')+'bank47_children:\nadd x28,x28,#48\nmov w19,#1\nbank47_comment_loop:\ncmp w19,w26\nb.gt finish\n'
 for off,field in [(0,'MessageId'),(4,'ParentId'),(8,'Name'),(12,'Text'),(16,'Topic'),(20,'Scenario'),(24,'Event'),(28,'Mood'),(44,'Preview')]:
  s+=f'ldr w0,[x28,#{off}]\nadd x0,x23,w0,uxtw\nbl {h.NEW_STRING:#x}\nbl {b.expand:#x}\nmov x22,x0\n'+f('w25','w19',field,'sets','x22')
 for off,field in [(32,'Timestamp'),(36,'Likes'),(40,'Parent')]:s+=f'ldr w24,[x28,#{off}]\n'+f('w25','w19',field,'seti','w24')
 for field in ['Liked','Hidden','Reply']:s+=f('w25','w19',field,'seti',0)
 s+='add x28,x28,#48\nadd w19,w19,#1\nb bank47_comment_loop'
 b.attach=b.routine('v47_attach_pack_thread',s)

def ambient(b):
 f=b.field;info=b.bank_info
 # Ambient roots are separate from player post counters and watermarks.
 s='str xzr,[sp]\nmov w19,w0\n'+b.ctx(OWNER)+'cmp w23,#13\nb.lt finish\n'+f'bl {b.old["v45_current_year"]["stub"]:#x}\n'+''.join(f'cmp w19,#{i}\nb.ne bank47_year_{i}\ncmp w0,#{year}\nb.lt finish\nbank47_year_{i}:\n'for i,year in enumerate(LAUNCH))+'cmp w19,#8\nb.ne ambient47_age_ok\ncmp w23,#18\nb.lt finish\nambient47_age_ok:\nmov w0,w19\nmov w1,#0\nmov w2,#1\n'+f'bl {b.pick:#x}\ncbz w0,finish\nmov w27,w0\n'+b.put('PendingThread','w27')+b.set('PendingSource',1)+'sub w27,w27,#1\n'+f'adr x28,{BANK_VA:#x}\nmov w9,#{info["threads_offset"]}\nadd x9,x28,x9\nlsl x10,x27,#5\nadd x9,x9,x10\nldr w0,[x9,#24]\nadd x0,x28,w0,uxtw\nbl {h.NEW_STRING:#x}\nmov x1,x0\nmov w0,w19\nmov w2,#1\nmov w3,#100\nmov w4,#0\nmov w5,#1\n'+f'bl {b.record:#x}\nstr x0,[sp]\nb finish'
 b.ambient=b.routine('v47_open_community_thread',s)

def soundcloud(b):
 # The upload activity has just committed its actual track to SimSoundCloud.
 # This site covers both native AddTrack storage paths and preserves the
 # activity's existing reception, royalties, collaborations and follower gain.
 s='cbz x19,finish\nldr x20,[x19,#0x78]\ncbz x20,finish\nldr x22,[x19,#0x40]\ncbz x22,finish\nldr x21,[x20,#0x38]\ncbz x21,finish\nldr w2,[x21,#0x18]\ncmp w2,#1\nb.lt finish\nldr x26,[x22,#0x10]\ncbz x26,finish\nldr w27,[x20,#0x28]\n'+b.ctx(OWNER)+b.field(0,9,'Seen',out='w25')+'add w25,w25,#1\nmov x1,x26\nmov w0,#9\nmov w2,w25\nmov w3,w27\nmov w4,#3\nmov w5,#0\n'+f'bl {b.record:#x}\nb finish'
 b.install('v47_soundcloud_track_published',0x2664a18,s)
 # Insert actions into the existing SoundCloud account menu's ArrayList.
 s='cbz x19,finish\n'+b.string('SocialFollowing9')+'mov x1,x0\nmov x0,x19\nmov x2,xzr\nbl 0x30611d0\nb finish'
 # x19 is the ArrayList at the final stock List construction boundary.
 b.install('v47_soundcloud_existing_account_actions',0x31ac000,s)
