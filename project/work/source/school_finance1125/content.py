"""School crushes, suspension receipts, era stories and a finance/exchange desk."""
import copy,csv,io,json,re
from life_repair.content import Author
from life_rework.content import csv_text,scene,p,seq,set_,inc,text,logic
from connected_life.content import closure
from school_finance1125.catalog import CURRENCIES,ART
MANUAL='[gfc.life_rework.AnnualContinuation1106=1]'

def build(base):
 a=Author(base);oldids={r['ScenarioID']for r in a.rows}
 for k,v,lo,hi in [('SchoolDisciplineDoneAge1125',-1,-1,999),('CrushAvailable1125',0,0,1),('CrushNoticeAge1125',-1,-1,999),('CrushResponseAge1125',-1,-1,999),('SchoolSuspensions1125',0,0,999),('EraEvent1125',0,0,16),('EraAnsweredAge1125',-1,-1,999),('WantedSuggestionAge1125',-1,-1,999),('WantedReward1125',0,0,999999),('FXSelected1125',0,0,19),('FinCurrency1125',1,1,99),('FinIncomeBar1125',0,0,100),('FinExpenseBar1125',0,0,100)]:a.prop(k,v,lo,hi)
 for n,iso,*_ in CURRENCIES:
  a.prop('FXWallet1125_'+str(n),0,0,2000000000);a.string('FXWalletText1125_'+str(n),iso+' 0.00')
 for k,v in [('CrushImage1125','native1125/school/picnic1880'),('CrushName1125','A classmate'),('CrushResult1125','Choose how to respond.'),('SchoolStatus1125','No suspension this school year.'),('WantedName1125','An unidentified suspect'),('WantedCharge1125','robbery'),('WantedImage1125','native1125/wanted/0'),('FinUnit1125','USD'),('FinIncomeText1125','0.00'),('FinExpenseText1125','0.00'),('FinStatus1125','Review your finances.'),('FXQuote1125',''),('FXBuyText1125',''),('FXStatus1125','Choose an exchange.'),('FXBalance1125','No travel cash yet.')]:a.string(k,v)
 def command(n,target):return seq(set_('NativeAction',0),set_('NativeAction',n),scene(target))
 school='BP_SHOW_LIST=genesis_v18_school52'
 def page(k,title,body,choices,icon='memo',picture=None,ext=None):
  a.page(k,title,body,choices,icon);r=a.rows[-1]
  if picture:r['BigImageString']=picture
  if ext:r['ExteriorTitle']=ext
  return r
 gate=((f'({p("SchoolEligible")} != 1)',scene('school_closed')),(f'({p("SchoolSuspendedAge1110")} >= <hero:age>)',scene('school_suspended1110')))
 page('school_crush_entry1125','A note from a classmate','See whether someone in your class wants to get to know you.',[('Read the note',a.gate(command(992,'school_crush1125'),extra=gate)),('Back',school)],'envelope')
 reply=[]
 for n,label in [(993,'I like you too'),(994,'Let’s be friends'),(995,'Politely say no')]:reply.append((label,command(n,'school_crush_result1125')))
 page('school_crush1125','Someone has a crush on you',p('CrushName1125')+' passes you a note asking to spend break together. How do you feel?',reply,'heart-red',p('CrushImage1125'),'School life')
 page('school_crush_result1125','Your classmate responds',p('CrushResult1125'),[('Continue','')],'chat-bubble',p('CrushImage1125'),'School life')
 page('school_crush_unavailable1125','No current invitation','There is no current invitation from a classmate. Return to school next year.',[('Back',school)],'envelope')
 # Entry checks the freshly refreshed classmate availability, rather than
 # displaying a stale name after leaving school or loading another life.
 page('school_crush_check1125','Your school messages','Check for a note from someone in your present class.',[('Read the note',logic([(f'({p("CrushAvailable1125")} != 1)',scene('school_crush_unavailable1125'))],scene('school_crush1125'))),('Back',school)],'envelope')
 r=a.edit('school_crush_entry1125');r['Choice1_AdvancedLogic']=json.dumps(a.gate(command(992,'school_crush_check1125'),extra=gate));r['Choice1_RouteTo']=''
 a.add_tile('genesis_v18_school52','Crushes & invitations',scene('school_crush_entry1125'),'envelope','Someone in your class may want to know you better')
 a.add_tile('genesis_v18_school52','Conduct & suspensions',scene('school_record1125'),'memo','Review your school record and return plan')
 page('school_record1125','Your conduct record','Recorded suspensions: '+p('SchoolSuspensions1125')+'<br>A completed fight carries a suspension for that school year. School-life activities resume next year. The principal can help you plan your return.',[('Meet the principal',logic([(f'({p("SchoolSuspendedAge1110")} >= <hero:age>)',scene('school_suspended1110'))],scene('school_clear'))),('Back',school)],'memo',ext='School life')
 r=a.edit('school_suspended1110');r['Choice2_Text']='Review my conduct record';r['Choice2_RouteTo']=scene('school_record1125');r['Choice2_AdvancedLogic']='';r['Body']='You are suspended for the remainder of this school year after fighting or repeated misconduct. Your conduct record is saved. You can meet the principal to agree on a return plan. School-life activities reopen next year.'
 # Copy the changed suspension page into every annual closure that contains it.
 annualschool=list(csv.DictReader(io.StringIO(base['genesis_school1110'])))
 crush=copy.deepcopy(a.edit('school_crush1125'));crush.update(ScenarioID=scene('annual_crush1125'),Filter='[gfc.life_rework.CrushAvailable1125=1][gfc.life_rework.Roll<25]',HeroAge='8-18',IsAgeUpScenario='true',HasDismissButton='false');annualschool.append(crush)
 a.assets['genesis_school1110']=csv_text(closure([r for r in annualschool if r.get('IsAgeUpScenario')=='true'],annualschool+a.rows))
 # One separate, original-engine annual container. Continuations remain
 # impossible to select randomly. No list opens during simulation.
 entries=[]
 def annual(n,key,title,body,opts,icon,pic=None,extra_filter=''):
  choices=[]
  for i,(label,result,effect)in enumerate(opts):
   changes=[set_('EraAnsweredAge1125','<hero:age>')]+effect
   route=a.outcome('era_result1125_'+str(n)+'_'+str(i),(result[2:]if result.startswith('I ')else result),'',changes,extra=((f'({p("EraAnsweredAge1125")} >= <hero:age>)',scene('era_already1125')),))
   a.rows[-1]['EmojiString']=icon;a.rows[-1]['ExteriorTitle']='Life in your era'
   if pic:a.rows[-1]['BigImageString']=pic
   choices.append((label,route))
  r=page(key,title,body,choices,icon,pic,'Life in your era');r.update(Filter=f'[gfc.life_rework.EraEvent1125={n}]'+extra_filter,IsAgeUpScenario='true',HeroAge='18-130',HasDismissButton='false');entries.append(r)
 page('era_already1125','Already settled','You have already made this year’s decision.',[('Continue','')])
 annual(1,'era_wanted1125','WANTED · '+p('WantedName1125'),p('WantedName1125')+' is wanted for '+p('WantedCharge1125')+'.<br><br>Reward offered: $'+p('WantedReward1125')+', alive only.<br><br>The sheriff needs reliable leads. A bounty hunter may accept this notice from Wanted & bounty notices.',[('Keep the notice','I kept a wanted notice and noted the sheriff’s suggested bounty. It is an offer, not a payment.',[]),('Leave it for the sheriff','I left a wanted notice to the sheriff and stayed out of the hunt.',[])],'memo',p('WantedImage1125'),'[gfc.life_rework.Country=United States]')
 stories=[
 (2,'The village reading room','A neighbour offers to lend you a newly printed book.','Share a reading','I joined neighbours to read aloud and discuss a book.',['SchoolTrust',1],'native1119/1800s/event_pictures/printing_workshop'),
 (3,'The harvest gathering','Families are gathering to bring in the harvest before bad weather.','Lend a hand','I helped neighbours bring in the harvest. We shared supper afterwards.',['SchoolFriends',1],'native1119/1800s/event_pictures/harvest_day'),
 (4,'A letter at the coaching inn','A traveller brings a letter from a distant friend.','Write back','I wrote a letter to a distant friend and sent it with the next coach.',['SchoolFriends',1],'native1119/1800s/event_pictures/stagecoach_arrival'),
 (5,'The first motor bus','A new bus route is drawing a crowd on the high street.','Watch it arrive','I watched the new motor bus arrive and talked about how travel was changing.',[],'native1119/eras/1900s/event_pictures/frontier_main_street'),
 (6,'An evening at the picture house','Friends invite you to a silent picture screening.','Join your friends','I spent an evening with friends watching a silent picture.',[],'native1125/era/cinema1920'),
 (7,'The wireless set','Neighbours have gathered to hear a radio broadcast.','Listen together','I listened to the wireless with neighbours and discussed the news.',[],'native1118/1940s/valve_radio'),
 (8,'A community garden','Your neighbours are pooling seeds for a community garden.','Help plant','I helped neighbours plant a community garden and share the work.',[],ART+'garden1930'),
 (9,'A record to remember','A friend wants you to hear a new record.','Listen together','I listened to a record with a friend and discovered a favourite song.',[],'native1118/1960s/record_player'),
 (10,'A handwritten invitation','A friend invites you to a local dance.','Go along','I went to a local dance and caught up with friends.',[],'native1118/school/event_pictures/1960s_school_dance.png'),
 (11,'A neighbourhood project','Neighbours are gathering to repair a shared fence.','Bring your tools','I helped neighbours repair a shared fence and shared a meal afterwards.',[],ART+'science1950'),
 (12,'Home computer evening','A friend shows you a home computer and a simple game.','Try it together','I tried a home computer with a friend and learned something new.',[],'native1118/1980s/home_computer'),
 (13,'An old photo turns up','A friend has found a photograph from years ago.','Share the memory','I shared an old photograph with a friend and caught up on our lives.',[],None),
 (14,'A neighbourhood cleanup','Neighbours are planning to clean up a nearby park.','Volunteer','I joined a neighbourhood cleanup and enjoyed meeting people.',[],None),
 (15,'A digital family album','Your family wants to collect old photos into an album.','Help organise it','I helped organise family photographs into a digital album.',[],None),
 (16,'A friend needs a hand','A friend is moving and asks for help packing.','Help them pack','I helped a friend pack for a move and made the day easier.',[],None)]
 for n,title,body,label,result,_,pic in stories:annual(n,'era_story1125_'+str(n),title,body,[(label,result,[]),('Wish them well','I wished my neighbours well and carried on with my plans.',[])],'handshake',pic)
 # Prevent date leaks within the half-century groups.
 for n,lo,hi in [(5,1900,1949),(6,1900,1929),(7,1920,1949),(8,1900,1949),(9,1950,1999),(10,1950,1999),(11,1950,1999),(12,1981,1999)]:
  r=next(r for r in entries if r['ScenarioID']==scene('era_story1125_'+str(n)));r['Filter']+=f'[gfc.life_rework.Year>={lo}][gfc.life_rework.Year<={hi}]'
 # Dynamic pictures on this new hub retain the new period-specific resources.
 finance=scene('finance_entry1125');review=scene('finance_report1125');wallet=scene('finance_wallet1125')
 page('finance_entry1125','Money & exchange','See your projected income and expenses or prepare travel cash in the local currency.',[('Income & expense graph',command(996,'finance_report1125')),('Travel currency wallet',command(999,'finance_wallet1125')),('Back','')],'money-bag',ext='Finances')
 r=page('finance_report1125','Income & expenses',p('FinStatus1125')+'<br><br>Annual income: '+p('FinUnit1125')+' '+p('FinIncomeText1125')+'<br>Annual expenses: '+p('FinUnit1125')+' '+p('FinExpenseText1125'),[('Refresh graph',command(996,'finance_report1125')),('Travel wallet',command(999,'finance_wallet1125')),('Back',finance)],'chart-bar',ext='Finances')
 r['BarGraphs']=json.dumps([dict(row=1,key='Income · '+p('FinIncomeText1125'),value=p('FinIncomeBar1125'),bar_graph_style='ALL_GREEN'),dict(row=2,key='Expenses · '+p('FinExpenseText1125'),value=p('FinExpenseBar1125'),bar_graph_style='ALL_RED')])
 page('finance_wallet1125','Travel money',p('FXStatus1125')+'<br><br>Your local wallet: '+p('FXBalance1125')+'<br>'+p('FXQuote1125')+'<br>Buy amount: '+p('FXBuyText1125')+'<br><br> Both buying and selling charge 2%. Rates are fixed offline game rates, so they differ from real-world quotes. Each currency keeps its own balance across travel.',[('Buy local travel cash',command(997,'finance_wallet_result1125')),('Sell local travel cash',command(998,'finance_wallet_result1125')),('Choose a currency','BP_SHOW_LIST=genesis_currencies1125'),('Back',finance)],'money-bag',ext='Currency exchange')
 page('finance_wallet_result1125','Your exchange',p('FXStatus1125')+'<br><br>'+p('FXBalance1125'),[('Continue',wallet),('Finances',finance)],'money-bag',ext='Currency exchange')
 a.add_tile('genesis_v18_era44','Money & exchange',finance,'money-bag','Local currencies, travel cash and an income/expense graph')
 currencies=copy.deepcopy(json.loads(base['genesis_era_shops1121']));currencies.update(ListID='genesis_currencies1125',Title='CURRENCY WALLETS');currencies['Items']=[a.tile('Follow my country',scene('fx_local1125'),'money-bag','Use the currency of your present residence')]
 page('fx_local1125','Your local currency','Follow the currency used in your present country.',[('Open wallet',seq(set_('FXSelected1125',0),command(999,'finance_wallet_result1125'))),('Back',finance)],'money-bag')
 page('fx_not_yet1125','Currency not introduced','This currency has not been introduced in your current year. Your existing balances were kept.',[('Other currencies','BP_SHOW_LIST=genesis_currencies1125'),('Back',finance)],'money-bag')
 for n,iso,symbol,rate,countries,lo in CURRENCIES:
  route=logic([(f'({p("Year")} < {lo})',scene('fx_not_yet1125'))],seq(set_('FXSelected1125',n),command(999,'finance_wallet_result1125')))
  page('fx_currency1125_'+str(n),iso+' travel wallet',p('FXWalletText1125_'+str(n))+'<br>Introduced by '+str(lo)+'. Review the current quote before exchanging.',[('Open balance & quote',route),('Back','BP_SHOW_LIST=genesis_currencies1125')],'money-bag')
  currencies['Items'].append(a.tile(iso+' · '+symbol,scene('fx_currency1125_'+str(n)),'money-bag',p('FXWalletText1125_'+str(n))))
 a.assets['genesis_currencies1125']=json.dumps(currencies,indent=2)
 # Registry entry uses the existing menu contract and one simple typed list.
 template=json.loads(base['genesis_era_shops1121']);template.update(ListID='genesis_finance1125',Title='MONEY & EXCHANGE');template['Items']=[a.tile('Income & expenses',finance,'money-bag','Your projected household finances'),a.tile('Travel wallet',scene('finance_entry1125'),'money-bag','Currency units and exchange costs')];a.assets['genesis_finance1125']=json.dumps(template,indent=2)
 registry=base['genesis_feature_containers'];prefix=registry[:registry.index('ContainerId,')];regs=list(csv.DictReader(io.StringIO(registry[len(prefix):])))
 r=dict.fromkeys(regs[0],'');r.update(ContainerId='finance1125',DisplayName='Money and exchange',InitDataSheet='genesis_v18_defaults_comment_entry47',EntryMenu='T2',EntryLabel='Money & exchange',EntryEmoji='money-bag',EntrySecondLine='Income, expenses and travel currency',EntryOrder='2',EntryListID='genesis_finance1125');regs.append(r)
 r=copy.deepcopy(next(r for r in regs if r['ContainerId']=='chronicle1110'));r.update(ContainerId='era_events1125',DisplayName='Life in your era',AgeUpActionList='genesis_era_events1125',AgeUpPriority='content',EntryMenu='',EntryListID='',EntryLabel='');regs.append(r)
 a.assets['genesis_feature_containers']=prefix+csv_text(regs)
 # Reduce flat repeatable town work from $8-12 to $1-2 a shift, still capped at
 # three visits per year. Existing bank balances/contracts are never revalued.
 for r in a.rows:
  if 'town_done1119_'in r['ScenarioID'] or 'town_event1119_'in r['ScenarioID']:
   for k,v in r.items():
    if isinstance(v,str):
     for old,new in [('BP_BANK_BALANCE=12','BP_BANK_BALANCE=2'),('BP_BANK_BALANCE=10','BP_BANK_BALANCE=2'),('BP_BANK_BALANCE=8','BP_BANK_BALANCE=1'),('$12','$2'),('$10','$2'),('$8','$1')]:v=v.replace(old,new)
     r[k]=v
 # Re-check suspension on every mod school action, including old saved cards.
 # Back/navigation and the principal's return-plan meeting remain available.
 def suspension_guards(rows):
  for r in rows:
   ident=r['ScenarioID'].lower()
   if not any(t in ident for t in ['school','exam111','cheer111'])or any(t in ident for t in ['school_suspended','school_suspension_talk','school_record1125']):continue
   for i in range(1,5):
    k=f'Choice{i}_AdvancedLogic';route=r.get(k)or r.get(f'Choice{i}_RouteTo','')
    if 'BP_GFC_MODIFY_PROPERTY=' not in route:continue
    target=json.loads(route)if r.get(k)else route
    r[k]=json.dumps(logic([(f'({p("SchoolSuspendedAge1110")} >= <hero:age>)',scene('school_suspended1110'))],target));r[f'Choice{i}_RouteTo']=''
 suspension_guards(a.rows)
 for name in ['genesis_school1110','genesis_rework_annual1105']:
  rows=list(csv.DictReader(io.StringIO(a.assets.get(name,base[name]))));suspension_guards(rows)
  # The native annual loader needs all reachable new suspension continuations.
  master={r['ScenarioID']:r for r in a.rows};master.update({r['ScenarioID']:r for r in rows})
  a.assets[name]=csv_text(closure([r for r in rows if r.get('IsAgeUpScenario')=='true'],list(master.values())))
 # Manual appended pages cannot steal annual draw slots.
 for r in a.rows:
  if r['ScenarioID']not in oldids and r not in entries:r.update(Filter=MANUAL,IsAgeUpScenario='false')
 a.assets['genesis_life_rework']=csv_text(a.rows,list(a.header));a.assets['genesis_rework_defaults']=csv_text(a.schema)
 a.assets['genesis_era_events1125']=csv_text(closure(entries,a.rows))
 return a.assets
