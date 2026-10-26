"""Offline social-stream simulation inside the existing social-media menu."""
from life_rework.content import p,scene,menu,set_,inc,text,seq,logic

def build(a,base):
 home=menu('genesis_v18_social_v18')
 for key,value,maximum in [('LiveAudience1110',0,2000000000),('LiveQuality1110',20,100),('LiveFollowers1110',0,2000000000),('LiveDonated1110',0,2000000000),('LiveEarned1110',0,2000000000),('LiveHost1110',0,3),('LiveHost1Trust1110',30,100),('LiveHost2Trust1110',30,100),('LiveHost3Trust1110',30,100)]:a.prop(key,value,0,maximum)
 a.string('LivePlatform1110','YouTube');a.string('LiveReply1110','No stream yet.')
 closed=scene('social_closed1110');guard=((f'({p("Year")} < 2010) || (<hero:age> < 13) || ({p("NativeInPrison1105")} == 1)',closed),)
 def out(key,body,changes=(),native=0,quota=('Live1110',4),extra=()):return a.outcome(key,body,scene('live_home1110'),list(changes),native=native,quota=quota,extra=guard+extra)
 a.page('social_closed1110','Social media is not available','Social media opens from 2010 in this game, and you must be at least 13. Later services still wait for their launch year.',[('Back',home)],'phone')
 a.page('live_home1110','Live streams',p('LivePlatform1110')+'<br>Build an audience, visit other channels and respond to your viewers.',[
  ('Choose a platform',scene('live_platform1110')),('Go live',a.gate(scene('live_start1110'),extra=guard)),('Visit another streamer',a.gate(scene('live_directory1110'),extra=guard)),('My channel & record',scene('live_record1110'))],'phone',stats=[('Live followers',p('LiveFollowers1110')),('Stream quality',p('LiveQuality1110')),('Last audience',p('LiveAudience1110'))])
 options=[]
 for name,start in [('YouTube',2010),('Instagram',2010),('Twitch',2011),('TikTok',2016)]:
  options.append((name,out('live_platform1110_'+name.lower(),'Your next simulated broadcast will appear on '+name+'. Your saved audience stays with your channel.',[text('LivePlatform1110',name)],quota=None,extra=((f'({p("Year")} < {start})',closed),))))
 a.page('live_platform1110','Choose your platform','Each platform becomes available in its launch period. All social-media gameplay remains locked before 2010.',options,'phone')
 a.page('live_start1110','You are live','Viewers begin joining. How will you run the stream?',[
  ('Answer questions and include chat',out('live_chat1110','You greet viewers by name and answer questions. People stay longer, your audience grows and a few viewers donate. The donations reach your bank balance.',[inc('LiveQuality1110',5),inc('LiveFollowers1110',12),set_('LiveAudience1110',25),inc('LiveEarned1110',25),'BP_BANK_BALANCE=25'],650)),
  ('Share a prepared performance',out('live_show1110','You arrive with a plan and put on a clear performance. Viewers share the channel and some become regular followers.',[inc('LiveQuality1110',8),inc('LiveFollowers1110',18),set_('LiveAudience1110',40)],650)),
  ('Ignore chat and argue with critics',out('live_argument1110','The argument drives viewers away. Regulars ask you to handle criticism more calmly next time.',[inc('LiveQuality1110',-8),inc('LiveFollowers1110',-5),set_('LiveAudience1110',8)],651)),
  ('End the stream',out('live_end1110','You thank the viewers and end the broadcast. You keep your current followers and can prepare something new next year.',quota=None))],'mic-studio')
 a.page('live_directory1110','Live now','These fictional streamers have their own audiences and remember how you treat them.',[(name,seq(set_('LiveHost1110',n),scene('live_host1110_'+str(n))))for n,name in enumerate(['PixelPilot — games','MayaMakes — art','CoachRiver — sport'],1)]+[('Back',scene('live_home1110'))],'phone')
 for n,name in enumerate(['PixelPilot','MayaMakes','CoachRiver'],1):
  trust='LiveHost'+str(n)+'Trust1110'
  a.page('live_host1110_'+str(n),name+' is live','You join the chat. The streamer notices regular, respectful visitors.',[
   ('Say hello and ask a question',out('live_host_chat1110_'+str(n),name+' reads your message and answers. Other viewers join in, and you leave with a stronger connection to the channel.',[inc(trust,6),inc('LiveQuality1110',2)],quota=('LiveVisit1110',4))),
   ('Donate from my balance',scene('live_donate1110_'+str(n))),('Offer a friendly collaboration',logic([(f'({p(trust)} >= 45)',out('live_collab1110_'+str(n),name+' agrees to a shared stream. You introduce each other to your audiences and gain new regular viewers.',[inc('LiveFollowers1110',30),inc(trust,4)],650,('LiveCollab1110',1)))],out('live_collab_wait1110_'+str(n),name+' thanks you, but wants to get to know your channel first. Visit again and build trust.',quota=None))),('Back',scene('live_directory1110'))],'handshake',stats=[('Connection',p(trust))])
  choices=[]
  for amount in [5,25,100]:
   choices.append((str(amount),out(f'live_donation1110_{n}_{amount}',name+' thanks you for the donation. The amount leaves your bank balance, and your support stays on the channel record.',[f'BP_BANK_BALANCE=-{amount}',inc('LiveDonated1110',amount),inc(trust,3)],quota=('LiveDonation1110',3),extra=((f'({p("NativeBank1105")} < {amount})',scene('live_no_funds1110')),))))
  a.page('live_donate1110_'+str(n),'Support '+name,'Choose an in-game donation. The amount comes from your character’s balance.',choices+[('Back',scene('live_host1110_'+str(n)))],'money-bag')
 a.page('live_no_funds1110','Not enough money','You cannot afford that donation. Your balance and the channel record are unchanged.',[('Back',scene('live_directory1110'))],'money-bag')
 a.page('live_record1110','My live channel','Your broadcasts, donations and channel relationships remain saved with this life.',[('Back to live streams',scene('live_home1110')),('Back to social media',home)],'clipboard',stats=[('Followers',p('LiveFollowers1110')),('Money donated',p('LiveDonated1110')),('Donations received',p('LiveEarned1110')),('Quality',p('LiveQuality1110'))])
 a.add_tile('genesis_v18_social_v18','Live streams',scene('live_home1110'),'phone','Broadcast, chat, visit channels and give in-game donations')
