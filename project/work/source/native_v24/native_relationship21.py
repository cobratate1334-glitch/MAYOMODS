"""Details for the selected native relationship, independent of slot limits."""
from native_hooks import h
from native_profiles20 import PERSONALITIES,INTERESTS,BELIEFS,STORIES,PREFS
from native_ui21 import table_value,number
RELATIONS=[('Friend',0x30d6f4c,0x30d8a4c,'x19',1),('Parent',0x30d22ac,0x30d3af8,'x19',0),('Sibling',0x30d3b3c,0x30d5310,'x19',0),('LoverButOverrideProfileWithListItem',0x30dae8c,0x30dce44,'x19',0),('Child',0x30d5350,0x30d6f0c,'x19',0),('Grandchild',0x30d8a8c,0x30d9c94,'x20',0),('NieceNephew',0x30d9cd4,0x30dae4c,'x20',0),('ExLover',0x30dcf38,0x30ddbb8,'x20',0),('Classmate',0x3137928,0x313880c,'x20',0),('Teacher',0x3136434,0x31378e4,'x20',0),('Coworker',0x3138850,0x3139f58,'x20',0),('Bandmate',0x313a800,0x313b53c,'x20',0),('Costar',0x313ddc0,0x313eaf0,'x20',0),('StreetPerson',0x3140fd4,0x3141b28,'x20',0)]
# The two school profiles have an extra field before Person; the dealer
# profile contains a SimDealerStreetPerson wrapper, resolved through GetPerson.
PROFILE_SITES=[('Friend',0x37a7b30,0x170,1),('Parent',0x2552a54,0x170,0),('Sibling',0x2554290,0x170,0),('Lover',0x3932580,0x170,0),('Child',0x254e3fc,0x170,0),('Grandchild',0x254ff98,0x170,0),('NieceNephew',0x25516d4,0x170,0),('ExLover',0x394d684,0x170,0),('Classmate',0x25a0140,0x178,0),('Teacher',0x25d5780,0x178,0),('Coworker',0x2992570,0x170,0),('Bandmate',0x23f65c8,0x170,0),('Costar',0x33caa58,0x170,0),('StreetPerson',0x36ea9f8,0x178,0)]

def routines(b):
 s='cbz x0,finish\nmov x26,x0\nmov w28,w1\n'+b.ctx('relationship21')+'ldr w24,[x26,#0x20]\n'+b.put('Age')+'ldr s0,[x26,#0x118]\nfcvtzs w24,s0\n'+b.put('Connection')+b.put('IsFriend','w28')
 s+='cbz w28,not_friend21\nldr w24,[x26,#0x188]\n'+b.put('YearsFriends')+h.load_game()+'\nldr x8,[x8,#0x28]\nldr w9,[x8,#0x20]\nsub w24,w9,w24\ncmp w24,#0\ncsel w24,w24,wzr,ge\n'+b.put('FirstMetAge')+'b friend_ready21\nnot_friend21:\n'+b.set('YearsFriends',0)+b.set('FirstMetAge',0)+'friend_ready21:\nmov x0,x26\nmov x1,xzr\nbl 0x2c44914\ncbz x0,finish\nmov x25,x0\n'+b.textptr('Name','x25')+'ldr w11,[x25,#0x10]\nadd x12,x25,#0x14\nmov w23,#5381\nrelationship_hash21:\ncbz w11,relationship_hash_done21\nldrh w9,[x12],#2\nmov w10,#33\nmadd w23,w23,w10,w9\nsub w11,w11,#1\nb relationship_hash21\nrelationship_hash_done21:\nand w23,w23,#0x7fffffff\n'
 def choices(key,values,salt):
  out=f'mov w9,#{len(values)}\nmov w10,#{salt}\nadd w24,w23,w10\nand w24,w24,#0x7fffffff\nudiv w10,w24,w9\nmsub w28,w10,w9,w24\n'
  for n,value in enumerate(values):out+=f'cmp w28,#{n}\nb.ne detail21_{key}_{n}\n'+b.text(key,value)+f'b detail21_{key}_done\ndetail21_{key}_{n}:\n'
  return out+f'detail21_{key}_done:\n'
 s+=choices('Personality',PERSONALITIES,13)+choices('Hobby',[v[0]for v in INTERESTS],29)+choices('Ambition',[v[1]for v in INTERESTS],29)+choices('Clubs',[v[2]for v in INTERESTS],29)+choices('Belief',BELIEFS,71)+choices('Story',STORIES,43)+choices('Preference',PREFS,0)
 # A selected person's build is stable across views and grows with THEIR age.
 # No hero dimensions or hero age are copied into relationship profiles.
 for key,salt,div,base in [('AdultHeight',0,55,155),('AdultWeight',971,66,50),('Reach',1709,16,-4)]:
  s+=f'mov w9,#{salt}\nadd w24,w23,w9\nand w24,w24,#0x7fffffff\nmov w9,#{div}\nudiv w10,w24,w9\nmsub w24,w10,w9,w24\nmov w9,#{base}\nadd w24,w24,w9\n'+b.put(key)
 s+=b.get('AdultHeight','w25',178)+b.get('Age','w26')
 for age,base,fraction in [(0,50,0),(1,75,5),(2,86,10),(3,95,15),(4,103,20),(5,110,25),(6,116,30),(7,122,40),(8,128,50),(9,134,60),(10,139,70),(11,144,75),(12,149,80),(13,154,85),(14,160,88),(15,166,92),(16,171,96),(17,175,98)]:
  s+=f'cmp w26,#{age}\nb.ne npc_growth24_{age}\nsub w9,w25,#178\nmov w10,#{fraction}\nmul w9,w9,w10\nmov w10,#100\nsdiv w9,w9,w10\nmov w25,#{base}\nadd w25,w25,w9\nb npc_height24\nnpc_growth24_{age}:\n'
 s+='npc_height24:\n'+b.put('Height','w25')+b.get('Reach')+b.get('AdultHeight','w26',178)+'mul w24,w24,w25\nsdiv w24,w24,w26\nadd w24,w24,w25\n'+b.put('Wingspan')+b.get('AdultWeight','w25',72)+b.get('Age','w26')
 for age,base,fraction in [(0,3,0),(1,10,0),(2,12,0),(3,14,0),(4,16,2),(5,18,4),(6,21,8),(7,24,12),(8,27,18),(9,31,25),(10,35,35),(11,39,45),(12,44,55),(13,49,65),(14,55,75),(15,61,85),(16,66,92),(17,70,98)]:
  s+=f'cmp w26,#{age}\nb.ne npc_weight24_{age}\nsub w9,w25,#72\nmov w10,#{fraction}\nmul w9,w9,w10\nmov w10,#100\nsdiv w9,w9,w10\nmov w25,#{base}\nadd w25,w25,w9\nb npc_weight24\nnpc_weight24_{age}:\n'
 s+='npc_weight24:\n'+b.put('Weight','w25')
 # For children, social interests are age-appropriate and no romantic tastes
 # or settled religious history are asserted about babies.
 s+=b.get('Age')+'cmp w24,#6\nb.ge child_story_ready21\n'+b.text('Hobby','Learning, play and time with family')+b.text('Ambition','Still discovering their interests')+b.text('Clubs','No clubs yet')+b.text('Belief','Growing up; beliefs are not yet described')+b.text('Story','Their story is just beginning, with new milestones each year.')+'child_story_ready21:\n'+b.get('Age')+'cmp w24,#18\nb.ge finish\n'+b.text('Preference','Developing their own preferences as they grow')+'b finish'
 b.relationship21=b.routine('selected_relationship_details21',s)

def hooks(b):
 for label,entry,site,reg,isfriend in RELATIONS:
  s='mov x0,x1\n'
  if label=='StreetPerson':s+='cbz x0,finish\nmov x1,xzr\nbl 0x2c2e2fc\n'
  s+=f'mov w1,#{isfriend}\nbl {b.relationship21:#x}\nb finish'
  b.install('v21_relationship_snapshot_'+label,entry,s)
  s=b.string('PersonStory21')+f'mov x1,x0\nmov x0,{reg}\ncbz x0,finish\nmov x2,xzr\nbl {h.INJECT:#x}\nb finish'
  b.install('v21_relationship_story_menu_'+label,site,s)
 for label,site,person_offset,isfriend in PROFILE_SITES:
  s=f'mov x20,x19\ncbz x20,finish\nldr x0,[x20,#{person_offset:#x}]\ncbz x0,finish\n'
  if label=='StreetPerson':s+='mov x1,xzr\nbl 0x2c2e2fc\ncbz x0,finish\n'
  s+=f'mov w1,#{isfriend}\nbl {b.relationship21:#x}\n'+b.ctx('relationship21')
  for key,title,unit in [('Height','Height:',' cm'),('Weight','Weight:',' kg'),('Wingspan','Wingspan:',' cm')]:s+=b.get(key)+number(b,unit=unit)+table_value(b,'x20',title)
  for key,title in [('Personality','Personality:'),('Hobby','Free time:'),('Ambition','Future plans:'),('Clubs','Interests and clubs:'),('Belief','Beliefs:'),('Preference','Preferences:'),('Story','Life story:')]:s+=b.string(key)+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nmov x3,xzr\nbl 0x3059934\nmov x22,x0\n'+table_value(b,'x20',title)
  if isfriend:
   for key,title in [('YearsFriends','Years as friends:'),('FirstMetAge','Your age when you met:')]:s+=b.get(key)+number(b)+table_value(b,'x20',title)
  s+='b finish'
  b.install('v21_native_'+label.lower()+'_profile_story',site,s)
