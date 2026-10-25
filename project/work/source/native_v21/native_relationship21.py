"""Details for the selected native relationship, independent of slot limits."""
from native_hooks import h
from native_profiles20 import PERSONALITIES,INTERESTS,BELIEFS,STORIES,PREFS
from native_ui21 import table_value,number
RELATIONS=[('Friend',0x30d6f4c,0x30d8a4c,'x19',1),('Parent',0x30d22ac,0x30d3af8,'x19',0),('Sibling',0x30d3b3c,0x30d5310,'x19',0),('LoverButOverrideProfileWithListItem',0x30dae8c,0x30dce44,'x19',0),('Child',0x30d5350,0x30d6f0c,'x19',0),('Grandchild',0x30d8a8c,0x30d9c94,'x20',0),('NieceNephew',0x30d9cd4,0x30dae4c,'x20',0),('ExLover',0x30dcf38,0x30ddbb8,'x20',0),('Classmate',0x3137928,0x313880c,'x20',0),('Teacher',0x3136434,0x31378e4,'x20',0),('Coworker',0x3138850,0x3139f58,'x20',0),('Bandmate',0x313a800,0x313b53c,'x20',0),('Costar',0x313ddc0,0x313eaf0,'x20',0),('StreetPerson',0x3140fd4,0x3141b28,'x20',0)]

def routines(b):
 s='cbz x0,finish\nmov x26,x0\nmov w28,w1\n'+b.ctx('relationship21')+'ldr w24,[x26,#0x20]\n'+b.put('Age')+'ldr s0,[x26,#0x118]\nfcvtzs w24,s0\n'+b.put('Connection')+b.put('IsFriend','w28')
 s+='cbz w28,not_friend21\nldr w24,[x26,#0x188]\n'+b.put('YearsFriends')+h.load_game()+'\nldr x8,[x8,#0x28]\nldr w9,[x8,#0x20]\nsub w24,w9,w24\ncmp w24,#0\ncsel w24,w24,wzr,ge\n'+b.put('FirstMetAge')+'b friend_ready21\nnot_friend21:\n'+b.set('YearsFriends',0)+b.set('FirstMetAge',0)+'friend_ready21:\nmov x0,x26\nmov x1,xzr\nbl 0x2c44914\ncbz x0,finish\nmov x25,x0\n'+b.textptr('Name','x25')+'ldr w11,[x25,#0x10]\nadd x12,x25,#0x14\nmov w23,#5381\nrelationship_hash21:\ncbz w11,relationship_hash_done21\nldrh w9,[x12],#2\nmov w10,#33\nmadd w23,w23,w10,w9\nsub w11,w11,#1\nb relationship_hash21\nrelationship_hash_done21:\nand w23,w23,#0x7fffffff\n'
 def choices(key,values,salt):
  out=f'mov w9,#{len(values)}\nmov w10,#{salt}\nadd w24,w23,w10\nand w24,w24,#0x7fffffff\nudiv w10,w24,w9\nmsub w28,w10,w9,w24\n'
  for n,value in enumerate(values):out+=f'cmp w28,#{n}\nb.ne detail21_{key}_{n}\n'+b.text(key,value)+f'b detail21_{key}_done\ndetail21_{key}_{n}:\n'
  return out+f'detail21_{key}_done:\n'
 s+=choices('Personality',PERSONALITIES,13)+choices('Hobby',[v[0]for v in INTERESTS],29)+choices('Ambition',[v[1]for v in INTERESTS],29)+choices('Clubs',[v[2]for v in INTERESTS],29)+choices('Belief',BELIEFS,71)+choices('Story',STORIES,43)+choices('Preference',PREFS,0)
 # For children, social interests are age-appropriate and no romantic tastes
 # or settled religious history are asserted about babies.
 s+=b.get('Age')+'cmp w24,#6\nb.ge child_story_ready21\n'+b.text('Hobby','Learning, play and time with family')+b.text('Ambition','Still discovering their interests')+b.text('Clubs','No clubs yet')+b.text('Belief','Growing up; beliefs are not yet described')+b.text('Story','Their story is just beginning, with new milestones each year.')+'child_story_ready21:\n'+b.get('Age')+'cmp w24,#18\nb.ge finish\n'+b.text('Preference','Developing their own preferences as they grow')+'b finish'
 b.relationship21=b.routine('selected_relationship_details21',s)

def hooks(b):
 for label,entry,site,reg,isfriend in RELATIONS:
  s=f'mov x0,x1\nmov w1,#{isfriend}\nbl {b.relationship21:#x}\nb finish'
  b.install('v21_relationship_snapshot_'+label,entry,s)
  s=b.string('PersonStory21')+f'mov x1,x0\nmov x0,{reg}\ncbz x0,finish\nmov x2,xzr\nbl {h.INJECT:#x}\nb finish'
  b.install('v21_relationship_story_menu_'+label,site,s)
 for label,site,reg,isfriend in [('Friend',0x37a7b30,'x19',1),('Parent',0x2552a54,'x19',0),('Sibling',0x2554290,'x19',0),('Lover',0x3932580,'x19',0)]:
  s=f'mov x20,{reg}\ncbz x20,finish\nldr x0,[x20,#0x170]\ncbz x0,finish\nmov w1,#{isfriend}\nbl {b.relationship21:#x}\n'+b.ctx('relationship21')
  for key,title in [('Personality','Personality:'),('Hobby','Free time:'),('Ambition','Future plans:'),('Clubs','Interests and clubs:'),('Belief','Beliefs:'),('Preference','Preferences:'),('Story','Life story:')]:s+=b.string(key)+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nmov x3,xzr\nbl 0x3059934\nmov x22,x0\n'+table_value(b,'x20',title)
  if isfriend:
   for key,title in [('YearsFriends','Years as friends:'),('FirstMetAge','Your age when you met:')]:s+=b.get(key)+number(b)+table_value(b,'x20',title)
  s+='b finish'
  b.install('v21_native_'+label.lower()+'_profile_story',site,s)
