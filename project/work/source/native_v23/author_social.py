from content import *
c='social_v18';p=lambda k:G(c,k);m=lambda k,v:M(c,k,v)
for k,v,lo,hi in [('NativeSocialSync',0,0,1),('NativeContactImpact',0,-24,24),('NativeBetrayal',0,0,1),('NativeCrushes',0,0,1),('NativeCupRoll',0,0,1),('Roll',0,0,99),('Selected',0,0,24),('Platform',0,0,9),('Consent',0,0,1),('GossipAge',-1,-1,999),('DatesUsed',0,0,6),('PostsUsed',0,0,12),('MainPartnerId',0,0,2147483647)]:prop(c,k,v,lo,hi,reset=k in ['DatesUsed','PostsUsed'])
text(c,'SelectedName','Choose a contact');text(c,'ConsentName','Exclusive')
platforms=['Discord','Reddit','Facebook','Instagram','TikTok','Twitter','YouTube','Twitch','OnlyFans']
for i,label in enumerate(platforms):
 for k,v,hi in [('Active',0,1),('Followers',0,10000000),('Posts',0,1000000),('Following',0,1000)]:prop(c,f'P{i}{k}',v,hi=hi)
for j in range(1,25):
 for key,v,hi in [('Id',0,2147483647),('Present',0,1),('Connection',50,100),('FamilyIntroduced',0,1),('FamilyTrust',30,100),('Crush',0,1)]:prop(c,f'C{j}{key}',v,hi=hi)
 for key,label in [('Name','No contact'),('Role','Contact')]:text(c,f'C{j}{key}',label)
 for i in range(len(platforms)):prop(c,f'C{j}Follow{i}',0,hi=1)
for j in range(1,5):
 for key,v,hi in [('Id',0,2147483647),('Active',0,1),('Trust',50,100),('Cheating',0,1)]:prop(c,f'Partner{j}{key}',v,hi=hi)
 text(c,f'Partner{j}Name','Empty')
items=[tile('Refresh Contacts',seq(m('NativeSocialSync',1),home('contacts')),'handshake'),child('Friends & Family','contacts','handshake'),tile('Relationship Agreements',seq(m('NativeSocialSync',1),S('agreements')),'heart'),tile('Multiple Relationships',S('partners'),'heart'),tile('Classmate Crush Gossip',seq(m('NativeSocialSync',1),m('NativeCrushes',1),S('gossip')),'busts-silhouette')]
menu(c,'Social Connections',items,'T2','handshake','Follow contacts; meet family; relationships and gossip')
menu('platforms','Choose Social Platform',[tile(label,seq(m('Platform',i),T(c,'PlatformName',label),S('selected_follow19')),'iphone') for i,label in enumerate(platforms)])
text(c,'PlatformName','Discord')
add('selected_follow19','Follow a contact',choices=[('Continue',logic([(f'({p("Selected")} == {j}) && ({p("Platform")} == {i})',S(f'follow{j}_{i}')) for j in range(1,25) for i in range(9)],home('contacts')))],icon='handshake')
for i,label in enumerate(platforms):
 guard=lambda dest:logic([('(<hero:age> < 13)',S('social_young'))]+([('(<hero:age> < 18)',S('social_adult'))] if label=='OnlyFans' else []),dest)
 back=home(label.lower()+'19') if i<2 else home('contacts')
 add('platform'+str(i),label,'Build a community, publish updates and follow people you know. These profiles save with this life.',[('Create / open account',guard(seq(m(f'P{i}Active',1),S('account'+str(i))))),('Following list',seq(m('NativeSocialSync',1),home('contacts'))),('Back',back)],icon='busts-silhouette',tables=table(Followers=p(f'P{i}Followers'),Posts=p(f'P{i}Posts'),Following=p(f'P{i}Following')))
 post=logic([(f'({p(f"P{i}Active")} != 1)',S('platform'+str(i))),(f'({p("PostsUsed")} >= 12)',S('social_limit'))],seq(I(c,'PostsUsed'),I(c,f'P{i}Posts'),I(c,f'P{i}Followers',F('add',20,F('div',G('life_v18','Looks'),2))),S('posted'+str(i))))
 add('account'+str(i),label+' profile','Choose an update for your community.',[('Post about my interests',guard(post)),('Post about my team or school',guard(post)),('Follow people I know',seq(m('Platform',i),T(c,'PlatformName',label),m('NativeSocialSync',1),home('contacts'))),('Back',back)],icon='busts-silhouette',tables=table(Followers=p(f'P{i}Followers'),Posts=p(f'P{i}Posts')))
 add('posted'+str(i),'Update posted','Your community responded to your update.',[('Continue',S('account'+str(i)))],icon='busts-silhouette')
add('social_young','Social media','These accounts become available at age 13.',[('Back',home(c))],icon='busts-silhouette')
add('social_adult','Adult account','This platform becomes available at age 18.',[('Back',home(c))],icon='busts-silhouette')
add('social_limit','Posting schedule','You have used twelve updates at this age. Age up to refresh your posting schedule.',[('Back',home('platforms'))],icon='calendar')
items=[]
for j in range(1,25):
 key='contact'+str(j);items.append(tile(p(f'C{j}Name'),seq(m('Selected',j),T(c,'SelectedName',p(f'C{j}Name')),S(key)),'handshake',p(f'C{j}Role')))
 guard=lambda dest:logic([(f'({p(f"C{j}Present")} != 1)',S('contact_absent'))],dest)
 follow=logic([(f'({p("Platform")} == {i})',S(f'follow{j}_{i}')) for i in range(len(platforms))],home('platforms'))
 add(key,p(f'C{j}Name'),'Spend time with this contact, manage follows, or meet their family.',[('Follow / unfollow on '+p('PlatformName'),guard(follow)),('Talk and spend time',guard(seq(m('NativeContactImpact',j),I(c,f'C{j}Connection',5),S(key)))),('Meet their family',guard(S('family'+str(j)))),('Relationships / back',S('date'+str(j)))],icon='handshake',tables=table(Role=p(f'C{j}Role'),Connection=p(f'C{j}Connection'),Family_trust=p(f'C{j}FamilyTrust')))
 for i,label in enumerate(platforms):
  add(f'follow{j}_{i}',label+' · '+p(f'C{j}Name'),'Follow or unfollow this contact on the selected platform.',[('Follow',guard(logic([(f'({p(f"C{j}Follow{i}")} == 1)',S(key))]+([('(<hero:age> < 18)',S('social_adult'))] if label=='OnlyFans' else [])+[('(<hero:age> < 13)',S('social_young'))],seq(m(f'P{i}Active',1),m(f'C{j}Follow{i}',1),I(c,f'P{i}Following'),S(key))))),('Unfollow',guard(logic([(f'({p(f"C{j}Follow{i}")} == 0)',S(key))],seq(m(f'C{j}Follow{i}',0),I(c,f'P{i}Following',-1),S(key))))),('Change platform',seq(m('Selected',j),home('platforms'))),('Back',S(key))],icon='handshake')
  # I() with negative values is normalized below to the engine's signed syntax.
 add('family'+str(j),'Family of '+p(f'C{j}Name'),'Ask your friend or partner to introduce you to their parents. Introductions and family trust save separately for each contact.',[('Ask for an introduction',guard(seq(m(f'C{j}FamilyIntroduced',1),I(c,f'C{j}FamilyTrust',10),S('familyvisit'+str(j))))),('Visit their family',guard(logic([(f'({p(f"C{j}FamilyIntroduced")} != 1)',S('family'+str(j)))],S('familyvisit'+str(j))))),('Back',S(key))],icon='house',tables=table(Introduced=p(f'C{j}FamilyIntroduced'),Family_trust=p(f'C{j}FamilyTrust')))
 add('familyvisit'+str(j),'Family visit','You spend time with '+p(f'C{j}Name')+' and their parents.',[('Have dinner and get to know them',seq(I(c,f'C{j}FamilyTrust',8),I(c,f'C{j}Connection',3),S(key))),('Ask about their family stories',seq(I(c,f'C{j}FamilyTrust',6),M('life_v18','NativeWellbeing',1),S(key))),('Back',S(key))],icon='house')
 restrictions=[('(<hero:age> < 16)',S('dating_young'))]
 if j<=4 or j in [19,20,21,22,23,24]:restrictions.append(('True',S('dating_not_contact')))
 add('date'+str(j),'Relationship choices','Start an additional romantic relationship only after considering your existing agreement.',[('Ask to date openly',logic(restrictions,seq(m('NativeCupRoll',1),S('askdate'+str(j))))),('Date secretly / cheat',logic(restrictions,seq(m('NativeCupRoll',1),S('secretdate'+str(j))))),('Back to contact',S(key)),('Back to contacts',home('contacts'))],icon='heart')
 for mode in ['ask','secret']:
  key2=mode+'date'+str(j);blocked=[(f'({p("DatesUsed")} >= 6)',S('date_limit'))]
  if mode=='ask':blocked += [(f'({p("Consent")} != 1) && ({p("MainPartnerId")} != 0)',S('agreements'))]
  blocked += [(f'({p("Roll")} >= {F("add",30,F("div",p(f"C{j}Connection"),2))})',S('date_declined'))]
  duplicate=[(f'({p(f"Partner{q}Active")} == 1) && ({p(f"Partner{q}Id")} == {p(f"C{j}Id")})',S('partners')) for q in range(1,5)]
  empty=[(f'({p(f"Partner{q}Active")} == 0)',seq(m(f'Partner{q}Active',1),m(f'Partner{q}Id',p(f'C{j}Id')),T(c,f'Partner{q}Name',p(f'C{j}Name')),m(f'Partner{q}Trust',60),m(f'Partner{q}Cheating',int(mode=='secret')),I(c,'DatesUsed'),m('NativeBetrayal',1) if mode=='secret' else '',S('partners'))) for q in range(1,5)]
  add(key2,'Ask to date' if mode=='ask' else 'Secret relationship','A contact can decline. Secret dating can damage your existing relationship; agreed non-exclusive dating keeps the agreement clear.',[('Continue',logic(duplicate+blocked+empty,S('partner_full'))),('Back',S('contact'+str(j)))],icon='heart')
menu('contacts','People I Know',items)
add('contact_absent','Contact unavailable','Refresh the contact list. This slot does not currently contain a living person from your life.',[('Refresh contacts',seq(m('NativeSocialSync',1),home('contacts'))),('Back',home(c))],icon='handshake')
add('dating_not_contact','Relationship choices','This contact is a relative, teacher or coach. Choose a friend or classmate for romantic dating.',[('Back',home('contacts'))],icon='heart')
add('dating_young','Dating','The added relationship agreement system becomes available at age 16.',[('Back',home(c))],icon='heart')
add('date_limit','Dating schedule','You have used six dating attempts at this age.',[('Back',S('partners'))],icon='calendar')
add('date_declined','They declined','They are not interested in dating right now.',[('Continue',home('contacts'))],icon='heart')
add('partner_full','Relationship slots','You already have four added romantic relationships. End one before starting another.',[('Back',S('partners'))],icon='heart')
add('agreements','Relationship agreements','Ask your current partner about a non-exclusive relationship. They can agree or decline; dating secretly remains a separate choice.',[('Ask for a non-exclusive agreement',seq(m('NativeCupRoll',1),S('consent_result'))),('Agree to be exclusive',seq(m('Consent',0),T(c,'ConsentName','Exclusive'),S('partners'))),('Back',home(c))],icon='heart')
add('consent_result','Your partner’s answer','An agreement changes only if your partner agrees.',[('Continue',logic([(f'({p("MainPartnerId")} == 0) || ({p("Roll")} < 65)',seq(m('Consent',1),T(c,'ConsentName','Agreed non-exclusive'),S('partners')))],seq(m('Consent',0),T(c,'ConsentName','Exclusive; request declined'),S('partners'))))],icon='heart')
add('partners','My relationships','Your native main partner and up to four added relationships are tracked separately. Each additional partner has their own trust and secrecy record.',[('Manage additional partners',home('partner_slots')),('Review agreement',S('agreements')),('Meet someone',seq(m('NativeSocialSync',1),home('contacts'))),('Back',home(c))],icon='heart',tables=table(Agreement=p('ConsentName'),Partner_1=p('Partner1Name'),Partner_2=p('Partner2Name'),Partner_3=p('Partner3Name'),Partner_4=p('Partner4Name')))
menu('partner_slots','My Additional Partners',[tile(p(f'Partner{q}Name'),S('partner'+str(q)),'heart') for q in range(1,5)])
for q in range(1,5):
 add('partner'+str(q),p(f'Partner{q}Name'),'Spend time with this partner or end the relationship.',[('Go on a date',logic([(f'({p(f"Partner{q}Active")} != 1)',S('partners'))],seq(I(c,f'Partner{q}Trust',8),M('life_v18','NativeWellbeing',2),S('partners')))),('End relationship',seq(m(f'Partner{q}Active',0),m(f'Partner{q}Id',0),T(c,f'Partner{q}Name','Empty'),S('partners'))),('Back',S('partners'))],icon='heart',tables=table(Trust=p(f'Partner{q}Trust'),Secret=p(f'Partner{q}Cheating')))
add('gossip','Classmate crush gossip','Classmates share who may have a crush on you. Higher looks increase the chance of a crush. Rumours are not guarantees, and every classmate can still decline a date.',[('Who has a crush on me?',home('crushes')),('Talk to classmates',seq(m('NativeSocialSync',1),home('contacts'))),('Back',home(c))],icon='busts-silhouette')
menu('crushes','Classmate Crushes',[tile(p(f'C{j}Name'),S('crush'+str(j)),'heart') for j in range(11,19)])
for j in range(11,19):
 add('crush'+str(j),p(f'C{j}Name'),'Gossip about this classmate.',[('Listen to the gossip',logic([(f'({p(f"C{j}Present")} != 1)',S('contact_absent')),(f'({p(f"C{j}Crush")} == 1)',S('crush_yes'+str(j)))],S('crush_no'+str(j)))),('Back',home('crushes'))],icon='heart')
 add('crush_yes'+str(j),'A classmate’s crush','You heard that '+p(f'C{j}Name')+' may have a crush on you.',[('Talk to them',S('contact'+str(j))),('Back',home('crushes'))],icon='heart')
 add('crush_no'+str(j),'No crush rumour','You have not heard a crush rumour about this classmate.',[('Back',home('crushes'))],icon='busts-silhouette')

# Extend the existing Social Media tab, keeping its seven native accounts.
for i,label in enumerate(platforms[:2]):
 owner=label.lower()+'19';prop(owner,'Version',19,hi=19)
 menu(owner,label,[tile('My '+label+' account',seq(m('Platform',i),T(c,'PlatformName',label),S('platform'+str(i))),'iphone'),tile('Follow people I know',seq(m('Platform',i),T(c,'PlatformName',label),m('NativeSocialSync',1),home('contacts')),'handshake')],'SocialMedia','iphone','Posts; community and people you follow')
for i,label in enumerate(platforms[2:],2):
 owner='following19_'+str(i);prop(owner,'Version',19,hi=19)
 menu(owner,'People I Follow',[tile('Follow / unfollow contacts',seq(m('Platform',i),T(c,'PlatformName',label),m('NativeSocialSync',1),home('contacts')),'handshake')],'SocialFollowing'+str(i),'handshake','Family; friends; teachers; coaches and teammates')
