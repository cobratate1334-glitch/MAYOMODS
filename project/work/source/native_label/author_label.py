"""Record Label v6: native lists, scenarios, saved contracts and real bank settlement.

Extends the v5 feature container without renaming or resetting its properties.
"""
import csv, io, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native_studio'))
import author_studio as s

base=json.loads((ROOT.parent/'native_studio/assets.json').read_text())
s.rows=[]
G,fn,mod,string,seq,logic,tables,bars=s.G,s.fn,s.mod,s.string,s.seq,s.logic,s.tables,s.bars
FILE='genesis_record_label'
HUB='genesis_record_label_hub'
HOME='BP_SHOW_LIST='+HUB
def scene(k):return s.scene('label'+k)
def add(k,title,body='',choices=(),**kw):
 r=s.add('label'+k,title,body,choices,**kw)
 r['ExteriorTitle']='Record Label';r['EmojiString']='cd'
 return r
props={}
def prop(k,v=0,lo=0,hi=100,t='int',reset=False):
 props[k]=dict(key=k,type=t,value=v,minimum=lo if t=='int' else '',maximum=hi if t=='int' else '',reset_on_ageup='true' if reset else '')
def textprop(k,v):prop(k,v,t='string')
def setn(k,v):return mod(k,'='+str(v))
def inc(k,v):return setn(k,fn('clamp',fn('add',G(k),v),props[k]['minimum'],props[k]['maximum']))
def spend(v):return seq('BP_BANK_BALANCE=-'+str(v),inc('LabelSpent',v))
def guard(target,cost=0,expression='',error='Unavailable'):
 cases=[]
 if expression:cases.append(({'expression':expression},scene(error)))
 if cost:cases.append(({'expression':f'(<hero:max_bank_balance capValue=2000000000> < {cost})'},scene('NoFunds')))
 return logic(cases,target)
def item(title,icon,k=None,subtitle='',visible='',graph=None,list_id=None):
 x={'Title':title,'Icon':icon,'SecondLine':subtitle,'ActionList':[{'Index':0,'ConditionList':[{'ScenarioID':scene(k),'ScenarioFile':FILE} if k else {'ListID':list_id}]}]}
 if visible:x['IsVisible']=visible
 if graph:x['BarGraph']={'Title':graph[0],'Value':G(graph[1]),'Style':'LOW_IS_RED'}
 return x
def menu(list_id,title,sections):return dict(ListID=list_id,Title=title,PresentationMode='Normal',Sections=sections)

prop('LabelStarted',hi=1);textprop('LabelName','Unnamed imprint')
prop('LabelReputation',10);prop('LabelSpent',hi=2000000000);prop('LabelIncome',hi=2000000000)
prop('LabelReleases',hi=1000000);prop('LabelLastPaidAge',-1,-1,999)
for k in ['LabelGross','LabelArtistPaid','LabelRecovered','LabelNet']:prop(k,hi=40000000)
artists=[('Nova Reed','Pop',35,600),('Miles Echo','Hip-hop',45,900),('Avery Static','Electronic',55,1400),('Jules Harbor','Indie',65,1800)]
for i,(name,genre,skill,fans) in enumerate(artists,1):
 p=f'Artist{i}'
 for k,v,lo,hi in [('Signed',0,0,1),('Years',0,0,3),('ContractAge',-1,-1,999),('Skill',skill,0,100),('Fans',fans,0,10000000),('Morale',70,0,100),('Share',50,0,100),('Advance',0,0,1000000),('Active',0,0,1),('Progress',0,0,100),('Quality',0,0,100),('Budget',0,0,15000),('Boost',0,0,100),('Campaign',0,0,1),('ReleaseAge',-1,-1,999),('Releases',0,0,1000000),('Gross',0,0,10000000),('Due',0,0,10000000),('Cut',0,0,10000000),('Recovered',0,0,1000000),('Net',0,0,10000000),('WorkUsed',0,0,6)]:
  prop(p+k,v,lo,hi,reset=k=='WorkUsed')
 for k,v in [('Name',name),('Genre',genre),('Project','Untitled'),('LastRelease','No releases yet')]:textprop(p+k,v)

add('NoFunds','Not enough money','Your bank balance cannot cover this expense. Your contract and project have not been changed.',[('Back to label',HOME)])
add('Unavailable','Activity unavailable','Check the contract, current project and yearly schedule. Each artist can release one project per age and has six development or production sessions.',[('Back to label',HOME)])
add('AlreadyPaid','Statement already collected','Your label has already settled at this age. New releases begin earning at the next age.',[('Back',HOME)])
add('Open','Start your record label','Open a small imprint for 1,000. Sign artists, finance their records and collect your share of catalogue royalties. Available from age 18.',[
 ('Open my label — 1,000',guard(seq(spend(1000),setn('LabelStarted',1),setn('LabelLastPaidAge','<hero:age>'),scene('Name')),1000,f'(<hero:age> < 18) || ({G("LabelStarted")} == 1)')),
 ('Back to studio','BP_SHOW_LIST=genesis_music_studio_hub')])
add('Name','Name your label','Choose the name shown on your label dashboard.',[(name,seq(string('LabelName',name),HOME)) for name in ['Afterlight Records','Northstar Audio','Open Door Music','Static House']])
add('Profile',G('LabelName'),tables=tables(Releases=G('LabelReleases'),Lifetime_label_income='<currency='+G('LabelIncome')+'>',Advances_and_budgets='<currency='+G('LabelSpent')+'>',Bank_balance='<hero:bank_balance>'),bars=bars(Label_reputation=G('LabelReputation'),Studio_skill=G('Skill')),choices=[('Rename label',scene('Name')),('Back',HOME)])

assets={}
for i,(name,genre,skill,fans) in enumerate(artists,1):
 p=f'Artist{i}';g=lambda k:G(p+k);k=lambda suffix:f'{i}{suffix}'
 owner=f'BP_SHOW_LIST=genesis_record_label_artist{i}'
 elig=f'({G("LabelStarted")} != 1) || ({g("Years")} == 0)'
 busy=f'({g("Active")} != 1) || ({g("Progress")} >= 100) || ({g("WorkUsed")} >= 6)'
 add(k('Scout'),name+' · '+genre,'An unsigned artist is looking for a three-year deal. Advances are paid now and recovered only from future artist royalties. A retained catalogue continues paying after the contract expires.',tables=tables(Audience=g('Fans'),Advance_unrecouped='<currency='+g('Advance')+'>'),bars=bars(Skill=g('Skill')),choices=[('Offer a contract',guard(scene(k('Contract')),expression=f'({G("LabelStarted")} != 1) || ({g("Years")} > 0)')),('Back','BP_SHOW_LIST=genesis_record_label_scout')])
 contracts=[]
 for label,advance,share in [('Equal partners — 1,000 advance / artist 50%',1000,50),('Artist-friendly — 5,000 advance / artist 70%',5000,70),('Label investment — 10,000 advance / artist 30%',10000,30)]:
  contracts.append((label,guard(seq(spend(advance),setn(p+'Signed',1),setn(p+'Years',3),setn(p+'ContractAge','<hero:age>'),setn(p+'Share',share),inc(p+'Advance',advance),setn(p+'Morale',70 if share==50 else 90 if share==70 else 50),owner),advance,f'({G("LabelStarted")} != 1) || ({g("Years")} > 0)')))
 add(k('Contract'),'Negotiate with '+name,'Three annual settlements complete the contract. Renewals apply the new royalty split to this artist’s retained catalogue. Unrecouped advances carry forward; they are never taken from your character twice.',contracts+[('Back',HOME)])
 add(k('Profile'),name,tables=tables(Genre=g('Genre'),Contract_years=g('Years'),Artist_share=g('Share')+'%',Unrecouped_advance='<currency='+g('Advance')+'>',Audience=g('Fans'),Catalogue_releases=g('Releases'),Gross_royalty_per_year='<currency='+g('Gross')+'>',Last_release=g('LastRelease')),bars=bars(Skill=g('Skill'),Morale=g('Morale')),choices=[('Manage artist',owner),('Renew expired contract',guard(scene(k('Contract')),expression=f'({g("Years")} > 0)')),('Back to label',HOME)])
 add(k('Develop'),'Artist development','Choose a session. Training and rehearsals improve later releases; morale affects record quality.',choices=[
  (label,guard(seq(spend(cost) if cost else '',inc(p+'Skill',boost),inc(p+'Morale',morale),inc(p+'WorkUsed',1),owner),cost,elig+f' || ({g("WorkUsed")} >= 6)'))
  for label,cost,boost,morale in [('Rehearse together',0,3,4),('Hire a vocal or production coach — 500',500,8,6),('Discuss creative direction',0,1,10)]])
 add(k('Fund'),'Fund the next record','One funded project and one release per artist per age. Budgets pay for recording and cannot be refunded if you shelve the project.',choices=[
  (label,guard(seq(spend(budget),setn(p+'Active',1),setn(p+'Progress',0),setn(p+'Budget',budget),setn(p+'Boost',boost),setn(p+'Quality',fn('clamp',fn('add',fn('avg',g('Skill'),g('Morale')),fn('mul',G('Equipment'),3)),0,100)),setn(p+'Campaign',0),string(p+'Project',name+' — '+title+' #'+fn('add',g('Releases'),1)),owner),budget,elig+f' || ({g("Active")} == 1) || ({g("ReleaseAge")} >= <hero:age>)'))
  for label,budget,boost,title in [('Debut single — 1,000',1000,10,'First Light'),('Studio EP — 5,000',5000,35,'New Horizon'),('Full album — 15,000',15000,70,'Chapter Two')]])
 add(k('Produce'),'Produce '+name+'’s record','Work with your studio equipment and skills. Every production session takes one of this artist’s six annual sessions.',bars=bars(Production=g('Progress'),Quality=g('Quality')),choices=[
  (label,guard(seq(inc(p+'Progress',progress),inc(p+'Quality',fn('add',quality,fn('div',G('Skill'),20))),inc(p+'WorkUsed',1),owner),expression=elig+' || '+busy))
  for label,progress,quality in [('Workshop the songs',35,4),('Direct recording sessions',40,3),('Mix and master',30,7)]])
 add(k('Promote'),'Promote the record','Choose one campaign per project. You pay campaign costs from your character’s bank account.',choices=[
  (label,guard(seq(spend(cost) if cost else '',inc(p+'Boost',boost),inc(p+'Fans',newfans),setn(p+'Campaign',1),owner),cost,elig+f' || ({g("Active")} != 1) || ({g("Campaign")} == 1)'))
  for label,cost,boost,newfans in [('Artist livestream and previews',0,5,150),('Pitch playlists — 500',500,15,500),('Music video and press — 2,000',2000,30,1800)]])
 # Every multiply stays within 32-bit integer range even at schema ceilings.
 newgross=fn('min',100000,fn('max',100,fn('mul',fn('div',fn('mul',fn('div',g('Fans'),100),fn('add',g('Quality'),g('Boost'),G('LabelReputation'))),10),fn('max',1,fn('div',g('Budget'),1000)))))
 add(k('Release'),'Release '+g('Project'),'Publish when production reaches 100%. Royalties join this artist’s retained catalogue and are settled once per age.',tables=tables(Budget='<currency='+g('Budget')+'>',Artist_share=g('Share')+'%'),bars=bars(Production=g('Progress'),Quality=g('Quality')),choices=[('Publish record',guard(seq(inc(p+'Gross',newgross),inc(p+'Releases',1),inc('LabelReleases',1),inc(p+'Fans',fn('mul',g('Quality'),10)),inc('LabelReputation',2),string(p+'LastRelease',g('Project')),setn(p+'Active',0),setn(p+'ReleaseAge','<hero:age>'),owner),expression=elig+f' || ({g("Active")} != 1) || ({g("Progress")} != 100) || ({g("ReleaseAge")} >= <hero:age>)')),('Keep working',owner)])
 add(k('Shelve'),'Shelve this project?','The record will be discarded. Advances, recording budgets and campaign expenses are not refunded.',[('Shelve it',guard(seq(setn(p+'Active',0),setn(p+'Progress',0),owner),expression=f'({g("Active")} != 1)')),('Keep working',owner)])
 add(k('Statement'),name+' · royalty breakdown','This shows the last settled statement. Artist payments are deducted before your label’s money reaches your bank.',tables=tables(Gross_receipts='<currency='+g('Due')+'>',Artist_royalty_before_recoupment='<currency='+g('Cut')+'>',Advance_recovered='<currency='+g('Recovered')+'>',Artist_cash_paid='<currency='+fn('sub',g('Cut'),g('Recovered'))+'>',Label_cash='<currency='+g('Net')+'>',Still_unrecouped='<currency='+g('Advance')+'>'),choices=[('Back',owner)])
 artistmenu=menu('genesis_record_label_artist'+str(i),name.upper(),[
  {'Items':[item(name,'hero',k('Profile'),genre+' · '+g('Years')+' contract years',graph=('Morale',p+'Morale'))]},
  {'Title':'Artist Activities','IsVisible':f'[gfc.music_studio.{p}Years>=1]','Items':[item('Artist Development','users',k('Develop'),'Coaching, rehearsals and creative direction'),item('Fund a Record','money-bag',k('Fund'),'Finance a single, EP or album',f'[gfc.music_studio.{p}Active=0]'),item(g('Project'),'cd',k('Produce'),'Direct production sessions',f'[gfc.music_studio.{p}Active=1]',('Production',p+'Progress')),item('Release Campaign','megaphone',k('Promote'),'Choose your promotion strategy',f'[gfc.music_studio.{p}Active=1]'),item('Publish Record','cd',k('Release'),'Release at 100% production',f'[gfc.music_studio.{p}Active=1]'),item('Shelve Project','hand-waving',k('Shelve'),'Discard the current record',f'[gfc.music_studio.{p}Active=1]')]},
  {'Title':'Business','Items':[item('Royalty Breakdown','chart-bar',k('Statement'),'Artist share, advance recovery and label income'),item('Renew Contract','handshake',k('Contract'),'Negotiate a new three-year deal',f'[gfc.music_studio.{p}Years=0]')]}
 ])
 assets[artistmenu['ListID']]=json.dumps(artistmenu,ensure_ascii=False,indent=2)

# Settlement is a forward-only native transaction. The age guard is set first.
# The schema advances defaults with saved v5 state; old fields are unchanged.
settlement=[setn('LabelLastPaidAge','<hero:age>')]
for key in ['LabelGross','LabelArtistPaid','LabelRecovered','LabelNet']:settlement.append(setn(key,0))
for i in range(1,5):
 p=f'Artist{i}';g=lambda k:G(p+k)
 settlement += [setn(p+'Due',g('Gross')),setn(p+'Cut',fn('div',fn('mul',g('Due'),g('Share')),100)),setn(p+'Recovered',fn('min',g('Advance'),g('Cut'))),setn(p+'Advance',fn('sub',g('Advance'),g('Recovered'))),setn(p+'Net',fn('add',fn('sub',g('Due'),g('Cut')),g('Recovered'))),inc('LabelGross',g('Due')),inc('LabelArtistPaid',fn('sub',g('Cut'),g('Recovered'))),inc('LabelRecovered',g('Recovered')),inc('LabelNet',g('Net')),
  # Decrement only after the signing age and only on a settled year.
  setn(p+'Years',fn('max',0,fn('sub',g('Years'),fn('clamp',fn('sub','<hero:age>',g('ContractAge')),0,1)))),setn(p+'ContractAge','<hero:age>')]
settlement += ['BP_BANK_BALANCE='+G('LabelNet'),inc('LabelIncome',G('LabelNet'))]
add('Paid','Label statement settled',tables=tables(Gross_receipts='<currency='+G('LabelGross')+'>',Artist_cash_paid='<currency='+G('LabelArtistPaid')+'>',Advances_recovered='<currency='+G('LabelRecovered')+'>',Paid_into_your_bank='<currency='+G('LabelNet')+'>',Bank_balance='<hero:bank_balance>'),choices=[('Back to label',HOME)],style='feedback')
claim=logic([({'expression':f'({G("LabelStarted")} != 1) || ({G("LabelLastPaidAge")} >= <hero:age>)'},scene('AlreadyPaid'))],seq(*settlement,scene('Paid')))
add('Royalties','Label royalty statement','Collect once per age. Recordings keep earning after contracts expire. The artist’s royalties first repay any advance; your label receives its share plus recovered advances.',tables=tables(Last_statement_net='<currency='+G('LabelNet')+'>',Label_lifetime_income='<currency='+G('LabelIncome')+'>'),choices=[('Settle this age',claim),('Back',HOME)])

hub=menu(HUB,'RECORD LABEL',[
 {'Items':[item('Start a Record Label','cd','Open','Open an imprint from age 18', '[gfc.music_studio.LabelStarted=0]'),item(G('LabelName'),'cd','Profile',G('LabelReleases')+' label releases','[gfc.music_studio.LabelStarted=1]',('Reputation','LabelReputation'))]},
 {'Title':'Label Business','IsVisible':'[gfc.music_studio.LabelStarted=1]','Items':[item('Scout Artists','users',list_id='genesis_record_label_scout',subtitle='Discover four artists or renew expired deals'),item('Royalty Statement','money-bag','Royalties','Settle artist shares and recoup advances')]},
 {'Title':'Signed Artists','IsVisible':'[gfc.music_studio.LabelStarted=1]','Items':[item(name,'hero',list_id='genesis_record_label_artist'+str(i),subtitle=genre+' · '+G(f'Artist{i}Years')+' contract years',visible=f'[gfc.music_studio.Artist{i}Signed=1]',graph=('Morale',f'Artist{i}Morale')) for i,(name,genre,skill,fans) in enumerate(artists,1)]}
])
scout=menu('genesis_record_label_scout','SCOUT ARTISTS',[{'Items':[item(name,'hero',str(i)+'Scout',genre+' · '+G(f'Artist{i}Fans')+' listeners',f'[gfc.music_studio.Artist{i}Years=0]',('Skill',f'Artist{i}Skill'))for i,(name,genre,skill,fans)in enumerate(artists,1)]}])
assets[HUB]=json.dumps(hub,ensure_ascii=False,indent=2);assets[scout['ListID']]=json.dumps(scout,ensure_ascii=False,indent=2)
assets[FILE]=s.csv_text(s.HEADER,s.rows)
defaultrows=list(csv.DictReader(io.StringIO(base['genesis_music_studio_defaults'])))
assert not(set(props)&{r['key']for r in defaultrows})
assets['genesis_music_studio_defaults']=s.csv_text(list(defaultrows[0]),defaultrows+list(props.values()))
studiohub=json.loads(base['genesis_music_studio_hub'])
studiohub['Sections'][-1]['Items'].append(item('Record Label','cd',list_id=HUB,subtitle='Sign artists, fund records and manage contracts'))
assets['genesis_music_studio_hub']=json.dumps(studiohub,ensure_ascii=False,indent=2)

# Preserve the existing yearly studio collection. Introduce one optional label
# settlement choice in the same native annual statement, then finish the panel.
annual=list(csv.DictReader(io.StringIO(base['genesis_music_studio_ageup'])))
annual[0]['Body']='Collect this age’s studio and record label income. Each account settles once per age, including when you already claimed one manually. Artist shares and advance recovery are calculated before the label pays your bank.'
annual[0]['Choice1_Text']='Collect studio and label royalties'
oldlogic=json.loads(annual[0]['Choice1_AdvancedLogic'])
studio_pay=oldlogic['else_when_no_matches']['route_options'][0]['route_to']
studio_done=f'({G("LastPaidAge")} >= <hero:age>)'
label_done=f'(({G("LabelStarted")} != 1) || ({G("LabelLastPaidAge")} >= <hero:age>))'
annual[0]['Choice1_AdvancedLogic']=json.dumps(logic([
 ({'expression':studio_done+' && '+label_done},''),
 ({'expression':studio_done},seq(*settlement)),
 ({'expression':label_done},studio_pay)
],seq(studio_pay,*settlement)),separators=(',',':'))
assets['genesis_music_studio_ageup']=s.csv_text(s.HEADER,annual)
for name,content in assets.items():
 (ROOT/(name+('.json'if name.startswith('genesis_record_label_')and name not in [FILE] or name=='genesis_music_studio_hub'else'.csv'))).write_text(content)
(ROOT/'assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2))
print(json.dumps({'label_scenarios':len(s.rows),'new_properties':len(props),'label_native_lists':6,'modified_studio_assets':3}))
