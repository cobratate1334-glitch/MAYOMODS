"""Rare contextual encounters; each keeps a visible result and a once-per-life flag."""
import copy
from life_rework.content import p,scene,menu,set_,inc,text,seq,logic

EGGS=[('A football at camp','A camp letter describes the local Christmas truces on the Western Front. Someone nearby brings out a football.','Join a quiet game','You join a friendly game and share a calmer moment with the section. The story stays in your service journal.','soccer',628),('A note in the radio case','An old radio case contains a handwritten note: “Morgan still owes me a chess game.”','Keep the note','You keep the note and ask around camp. A squadmate laughs and offers a game when duty is over.','books',628),('The misplaced clock','A second-hand shop’s display clock insists it is still 1999. The owner has given up arguing with it.','Help set the clock','You help the owner fix the clock and leave with a funny story. Your mood improves.','clock',628),('A map behind the locker','Behind a loose locker panel is a hand-drawn map to the school’s oldest tree.','Look with a friend','You and a friend find a small tin with old club badges. You show a teacher, who adds them to the school display. Your friendship improves.','school',112),('A stranger at the station','A person sleeping near the station asks whether you can spare money for food.','Give five','You give five from your balance. They thank you and head toward a nearby café.','money-bag',111),('A handwritten chess puzzle','A library book contains a small handwritten chess problem and a note: “Leave something for the next reader.”','Add a friendly note','You add a friendly note and put the book back. Another reader smiles when they find it.','books',616)]

def build(a,base):
 rows=[]
 for n,(title,body,label,result,icon,native)in enumerate(EGGS,1):
  flag='EasterSeen1110_'+str(n);a.prop(flag,0,0,1)
  effects=[set_(flag,1)]
  guard=((f'({p(flag)} == 1)',scene('easter_already1110')),)
  if n==5:effects+=['BP_BANK_BALANCE=-5'];guard+=((f'({p("NativeBank1105")} < 5)',scene('dealer_unavailable1110')),)
  dest=a.outcome('easter_result1110_'+str(n),result,'',effects,native=native,extra=guard)
  decline=seq(set_(flag,1))
  a.page('easter1110_'+str(n),title,body,[(label,dest),('Keep going',decline)],icon)
  r=copy.deepcopy(a.edit('easter1110_'+str(n)));r.update(ScenarioID=scene('annual_easter1110_'+str(n)),Filter=f'[gfc.life_rework.EasterStory1110={n}]',IsAgeUpScenario='true',HasDismissButton='false');rows.append(r)
 a.page('easter_already1110','A familiar memory','You have already followed this little story. The memory remains in your journal.',[('Continue','')],'books')
 a.connected_easter_rows=rows
