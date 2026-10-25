"""Native Genesis music studio; no Java UI and no independent currency ledger."""
import csv, io, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
C = 'music_studio'
FILE = 'genesis_music_studio'
HUB = 'genesis_music_studio_hub'
G = lambda key: f'<GFC.{C}.{key}>'
def fn(name, *args): return '<function:' + name + ':' + ':'.join(map(str,args)) + '>'
def mod(key, value): return f'BP_GFC_MODIFY_PROPERTY={C}:{key}:{value}'
def string(key, value): return f'BP_GFC_SET_STRING={C}:{key}:{value}'
def route(*parts): return '>>'.join(parts)
def scene(key): return 'scenario.musicStudio.' + key
def opts(target): return {'route_options':[{'route_to':target}]}
def logic(cases, fallback):
    return {'cases':[{'if':condition, 'then':opts(target)} for condition,target in cases], 'else_when_no_matches':opts(fallback)}

HEADER = ['ScenarioID','Style','Filter','HeroAge','ExteriorTitle','Title','HasDismissButton','FocusPerson','EmojiString','BigImageString','Body','RewardsGranted','Dropdowns','TableRows','Sliders','BarGraphs']
for i in range(1,5): HEADER += [f'Choice{i}_{k}' for k in ['Text','ButtonStyle','RouteTo','Impacts','LogEntryLine1','LogEntryLine2','AdvancedLogic','ConfirmationString']]
HEADER += ['BlueprintPayloadForRoute','ChoiceCurrencyCost','IsAgeUpScenario','EntityObjectDataFocusTag','DrawFilter']
rows = []
def add(key, title, body='', choices=(), tables=None, bars=None, sliders=None, filt='', style='normal', dismiss=True):
    r = dict.fromkeys(HEADER,'')
    r.update(ScenarioID=scene(key),Style=style,Filter=filt,ExteriorTitle='Music Studio',Title=title,HasDismissButton=str(dismiss).lower(),EmojiString='mic-studio',Body=body)
    for field,value in [('TableRows',tables),('BarGraphs',bars),('Sliders',sliders)]:
        if value: r[field]=json.dumps(value,separators=(',',':'))
    for i,ch in enumerate(choices,1):
        r[f'Choice{i}_Text']=ch[0];r[f'Choice{i}_ButtonStyle']='normal'
        if isinstance(ch[1],dict):r[f'Choice{i}_AdvancedLogic']=json.dumps(ch[1],separators=(',',':'))
        else:r[f'Choice{i}_RouteTo']=ch[1]
        if len(ch)>2:r[f'Choice{i}_LogEntryLine1']=ch[2]
    rows.append(r);return r
def tables(**items):return [{'row':i,'key':key.replace('_',' ')+':','value':value}for i,(key,value)in enumerate(items.items(),1)]
def bars(**items):return [{'row':i,'key':key.replace('_',' '),'value':value,'bar_graph_style':'LOW_IS_RED'}for i,(key,value)in enumerate(items.items(),1)]
HOME = f'BP_SHOW_LIST={HUB}'
active = f'[gfc.{C}.Active=1]'
def guard(target, cost=0, working=False, require=None):
    cases=[]
    if require:cases.append(({'expression':require},scene('notReady')))
    if working:cases.append(({'filter':f'[gfc.{C}.WorkUsed>=6]'},scene('rest')))
    if cost:cases.append(({'expression':f'(<hero:max_bank_balance capValue=2000000000> < {cost})'},scene('noFunds')))
    return logic(cases,target)
def pay(cost):return f'BP_BANK_BALANCE=-{cost}' if cost else ''
def seq(*parts):return route(*(p for p in parts if p))

properties = {
 'Started':('int',0,0,1), 'Active':('int',0,0,1), 'Skill':('int',20,0,100),
 'Reputation':('int',10,0,100), 'Fans':('int',100,0,10000000), 'Progress':('int',0,0,100),
 'Quality':('int',20,0,100), 'Promotion':('int',0,0,100), 'Collaborator':('int',0,0,1),
 'Tracks':('int',1,1,10), 'Share':('int',90,25,100), 'GuestShare':('int',0,0,20), 'ReachMultiplier':('int',100,100,250), 'TotalReleases':('int',0,0,1000000),
 'LifetimeIncome':('int',0,0,2000000000), 'LifetimeSpent':('int',0,0,2000000000),
 'AnnualRoyalty':('int',0,0,20000000), 'LastPaidAge':('int',-1,-1,999),
 'ReleaseStreams':('int',0,0,2000000000), 'ReleaseRoyalty':('int',0,0,20000000),
 'WorkUsed':('int',0,0,6), 'Equipment':('int',0,0,3), 'PromotionUsed':('int',0,0,1),
 'Genre':('string','Indie','',''), 'Format':('string','Single','',''),
 'ProjectTitle':('string','Untitled','',''), 'Distribution':('string','Independent','',''),
 'LastTitle':('string','No releases yet','',''), 'LastGenre':('string','Indie','',''),
 'LastFormat':('string','Single','',''), 'LastQuality':('int',0,0,100),
}
for slot in range(1,9):
    for key,t,initial,lo,hi in [('Title','string','Unreleased', '', ''),('Genre','string','Indie', '', ''),('Format','string','Single', '', ''),('Quality','int',0,0,100),('Streams','int',0,0,2000000000),('Royalty','int',0,0,20000000)]:
        properties[f'Catalog{slot}{key}']=(t,initial,lo,hi)

add('noFunds','Insufficient funds','Your character does not have enough money for this activity.',[('Back to studio',HOME)])
add('notReady','Activity unavailable','Check your project stage. Recording needs a draft, mixing needs a recording, and release needs 100% production. A collaborator, campaign or equipment upgrade can only be chosen once.',[('Back to studio',HOME)])
add('rest','Studio schedule full','You have used your six studio work sessions this year. Age up to refresh your schedule.',[('Back to studio',HOME)])
add('tooYoung','Music Studio','You can open a studio from age 16.',[('Close','')])
add('open','Open your studio','Start an independent production career. Your studio audience and catalogue belong to this character.',[
 ('Start in my bedroom — free',logic([({'expression':'(<hero:age> < 16)'},scene('tooYoung'))],seq(mod('Started','=1'),mod('LastPaidAge','=<hero:age>'),HOME))),
 ('Build a home studio — 1,000',logic([({'expression':'(<hero:age> < 16)'},scene('tooYoung'))],guard(seq(pay(1000),mod('Started','=1'),mod('Equipment','=1'),mod('LifetimeSpent','+1000'),mod('LastPaidAge','=<hero:age>'),HOME),1000)['else_when_no_matches']['route_options'][0]['route_to']))
])
# The second setup choice uses one flat decision object; affordability cannot be bypassed.
rows[-1]['Choice2_AdvancedLogic']=json.dumps(logic([({'expression':'(<hero:age> < 16)'},scene('tooYoung')),({'expression':'(<hero:max_bank_balance capValue=2000000000> < 1000)'},scene('noFunds'))],seq(pay(1000),mod('Started','=1'),mod('Equipment','=1'),mod('LifetimeSpent','+1000'),mod('LastPaidAge','=<hero:age>'),HOME)),separators=(',',':'))
add('profile','Studio profile',tables=tables(Audience=G('Fans'),Releases=G('TotalReleases'),Royalty_per_year='<currency='+G('AnnualRoyalty')+'>',Lifetime_income='<currency='+G('LifetimeIncome')+'>',Studio_spending='<currency='+G('LifetimeSpent')+'>',Sessions_left=fn('sub',6,G('WorkUsed')),Bank_balance='<hero:bank_balance>'),bars=bars(Production_skill=G('Skill'),Reputation=G('Reputation')),choices=[('Back',HOME)])
add('new','Choose your next project','Pick a release format. Larger projects earn more streams but require more work.',[
 (title,guard(seq(mod('Active','=1'),mod('Tracks','='+str(tracks)),string('Format',label),mod('Progress','=0'),mod('Quality','='+fn('max',10,fn('div',G('Skill'),2))),mod('Promotion','=0'),mod('PromotionUsed','=0'),mod('Collaborator','=0'),mod('GuestShare','=0'),scene('genre')),require=f'({G("Active")} == 1)'))
 for title,label,tracks in [('Single','Single',1),('Five-track EP','EP',5),('Ten-track album','Album',10)]
])
add('genre','Choose a sound','Your release will keep this genre in the catalogue.',[(genre,seq(string('Genre',genre),scene('title')))for genre in ['Pop','Hip-hop','Electronic','Indie']])
add('title','Name your project','Choose a working title. Release numbers distinguish projects in your catalogue.',[(title,seq(string('ProjectTitle',title+' #'+fn('add',G('TotalReleases'),1)),HOME))for title in ['After Hours','New Beginnings','City Lights','No Signal']])

def activity(key,title,body,options,min_progress=0):
    choices=[]
    for label,cost,progress,quality,skill in options:
        steps=[pay(cost),mod('LifetimeSpent','+'+str(cost)),mod('Progress','+'+str(progress)),mod('Quality','+'+str(quality)),mod('Skill','+'+str(skill)),mod('WorkUsed','+1'),scene('sessionDone')]
        require=f'({G("Active")} != 1) || ({G("Progress")} < {min_progress})'
        choices.append((label,guard(seq(*steps),cost,True,require),f'I worked on {title.lower()} for my independent music project.'))
    add(key,title,body,choices,bars=bars(Production=G('Progress'),Quality=G('Quality')))
activity('write','Songwriting','Build the hook, lyrics and arrangement. Every choice uses one studio session.',[
 ('Write from personal experience',0,20,8,2),('Experiment with a new arrangement',0,15,12,3),('Book a co-writing session — 300',300,30,16,3),('Chase a trend',0,25,3,1)])
activity('record','Recording','Record your project once you have a draft. Longer releases move more slowly.',[
 ('Record at home',0,20,5,2),('Hire a studio — 750',750,35,14,3),('Book an engineer — 1,500',1500,40,20,4),('Capture a live take',0,25,7,2)],20)
activity('mix','Mix and master','Balance the sound and polish the finished recording.',[
 ('Mix it myself',0,20,8,3),('Hire a mixing engineer — 500',500,30,15,2),('Professional mastering — 1,000',1000,35,20,2),('Test it on several speakers',0,15,12,3)],40)
# Scale progress per project size through the native arithmetic helper.
for r in rows:
 if r['ScenarioID'] in map(scene,['write','record','mix']):
  for i in range(1,5):
   k=f'Choice{i}_AdvancedLogic';data=json.loads(r[k]);target=data['else_when_no_matches']['route_options'][0]['route_to']
   import re
   target=re.sub(r'BP_GFC_MODIFY_PROPERTY=music_studio:Progress:\+(\d+)',lambda m:mod('Progress','+'+fn('max',5,fn('div',int(m[1])*2,fn('add',1,G('Tracks'))))),target)
   data['else_when_no_matches']['route_options'][0]['route_to']=target;r[k]=json.dumps(data,separators=(',',':'))
add('sessionDone','Session complete',tables=tables(Project=G('ProjectTitle'),Sessions_remaining=fn('sub',6,G('WorkUsed'))),bars=bars(Production=G('Progress'),Quality=G('Quality')),choices=[('Continue',HOME)],style='feedback')
add('collaborate','Choose a collaborator','A guest feature brings new listeners. Work with one collaborator per project.',[
 (label,guard(seq(pay(cost),mod('LifetimeSpent','+'+str(cost)),mod('Collaborator','=1'),mod('Quality','+'+str(quality)),mod('Fans','+'+str(fans)),mod('GuestShare','='+str(share)),mod('WorkUsed','+1'),scene('sessionDone')),cost,True, f'({G("Active")} != 1) || ({G("Collaborator")} == 1)'))
 for label,cost,quality,fans,share in [('Swap verses with a newcomer',0,8,100,5),('Hire a session musician — 400',400,15,250,10),('Book an established guest — 2,000',2000,20,1200,20)]
])
add('promote','Plan your campaign','Choose one campaign for this project. Promotion affects release streams and the studio audience.',[
 (label,guard(seq(pay(cost),mod('LifetimeSpent','+'+str(cost)),mod('Promotion','+'+str(score)),mod('Fans','+'+str(fans)),mod('PromotionUsed','=1'),scene('campaignDone')),cost,False,f'({G("Active")} != 1) || ({G("PromotionUsed")} == 1)'))
 for label,cost,score,fans in [('Post behind-the-scenes clips',0,15,100),('Pitch blogs and playlists — 250',250,30,350),('Run a targeted campaign — 1,000',1000,55,1200),('Film a music video — 3,000',3000,80,2500)]
])
add('campaignDone','Campaign launched',tables=tables(Project=G('ProjectTitle'),Audience=G('Fans')),bars=bars(Promotion=G('Promotion')),choices=[('Continue',HOME)],style='feedback')
add('equipment','Upgrade your studio','Equipment improves the quality of future releases. Choose an upgrade you do not already own.',[
 (label,guard(seq(pay(cost),mod('LifetimeSpent','+'+str(cost)),mod('Equipment','='+str(level)),mod('Skill','+'+str(boost)),HOME),cost,False,f'({G("Equipment")} >= {level})'))
 for label,cost,level,boost in [('Home recording setup — 1,000',1000,1,5),('Professional production room — 5,000',5000,2,10),('Commercial studio — 20,000',20000,3,15)]
])
add('distribution','Release rights','Choose how to distribute future projects. Agreements cannot be changed during an active project.',[
 (label,guard(seq(mod('Share','='+str(share)),mod('ReachMultiplier','='+str(reach)),string('Distribution',name),HOME),require=f'({G("Active")} == 1)'))
 for label,name,share,reach in [('Stay independent — 90%, normal reach','Independent',90,100),('Distribution partner — 70%, 1.65× reach','Distribution partner',70,165),('Label-backed — 55%, 2.5× reach','Label-backed distribution',55,250)]
])
add('abandon','Shelve this project?',G('ProjectTitle')+' will be discarded. Money already spent will not be returned.',[('Shelve it',seq(mod('Active','=0'),mod('Progress','=0'),HOME)),('Keep working',HOME)])

streams=fn('min',2000000000,fn('mul',fn('div',fn('add',fn('mul',G('Fans'),G('Tracks'),fn('max',1,fn('div',G('Quality'),10))),fn('mul',G('Promotion'),G('Quality'),G('Tracks'),40)),100),G('ReachMultiplier')))
royalty=fn('min',2000000,fn('div',fn('mul',fn('div',G('ReleaseStreams'),250),fn('sub',G('Share'),G('GuestShare'))),100))
release_steps=[mod('ReleaseStreams','='+streams),mod('ReleaseRoyalty','='+royalty)]
for i in range(8,1,-1):
 for k in ['Title','Genre','Format','Quality','Streams','Royalty']:
  release_steps.append(string(f'Catalog{i}{k}',G(f'Catalog{i-1}{k}')) if k in ['Title','Genre','Format'] else mod(f'Catalog{i}{k}','='+G(f'Catalog{i-1}{k}')))
for k,source in [('Title','ProjectTitle'),('Genre','Genre'),('Format','Format'),('Quality','Quality'),('Streams','ReleaseStreams'),('Royalty','ReleaseRoyalty')]:
 release_steps.append(string('Catalog1'+k,G(source)) if k in ['Title','Genre','Format'] else mod('Catalog1'+k,'='+G(source)))
release_steps += [string('LastTitle',G('ProjectTitle')),string('LastGenre',G('Genre')),string('LastFormat',G('Format')),mod('LastQuality','='+G('Quality')),mod('TotalReleases','+1'),mod('AnnualRoyalty','+'+G('ReleaseRoyalty')),mod('Fans','+'+fn('mul',G('Quality'),10)),mod('Reputation','='+fn('clamp',fn('avg',G('Reputation'),G('Quality')),0,100)),mod('Active','=0'),scene('releaseDone')]
add('release','Release your project',tables=tables(Title=G('ProjectTitle'),Format=G('Format'),Genre=G('Genre'),Revenue_share=fn('sub',G('Share'),G('GuestShare'))+'%'),bars=bars(Production=G('Progress'),Quality=G('Quality'),Promotion=G('Promotion')),choices=[('Publish project',guard(seq(*release_steps),require=f'({G("Active")} != 1) || ({G("Progress")} < 100)')),('Keep working',HOME)])
add('releaseDone','Your release is live',tables=tables(Title=G('LastTitle'),Launch_streams=G('ReleaseStreams'),New_annual_royalty='<currency='+G('ReleaseRoyalty')+'>',Catalogue_royalty_per_year='<currency='+G('AnnualRoyalty')+'>'),bars=bars(Audience_reception=G('LastQuality')),choices=[('Continue',HOME,'I released an independent music project.')],style='feedback')

for i in range(1,9):
 add('catalog'+str(i),G(f'Catalog{i}Title'),tables=tables(Format=G(f'Catalog{i}Format'),Genre=G(f'Catalog{i}Genre'),Launch_streams=G(f'Catalog{i}Streams'),Annual_royalty_at_release='<currency='+G(f'Catalog{i}Royalty')+'>'),bars=bars(Reception=G(f'Catalog{i}Quality')),choices=[('Back to catalogue','BP_SHOW_LIST=genesis_music_studio_catalog')])
add('paid','Annual royalties collected',tables=tables(Collected='<currency='+G('AnnualRoyalty')+'>',Bank_balance='<hero:bank_balance>'),choices=[('Continue','')],style='feedback')
add('alreadyPaid','Already collected','You have already collected studio royalties at this age.',[('Back to studio',HOME)],style='feedback')
collection=logic([({'expression':f'({G("LastPaidAge")} >= <hero:age>)'},scene('alreadyPaid'))],seq(mod('LastPaidAge','=<hero:age>'),f'BP_BANK_BALANCE={G("AnnualRoyalty")}',mod('LifetimeIncome','+'+G('AnnualRoyalty')),scene('paid')))
add('royalties','Annual studio statement','Catalogue royalties are paid into this character’s bank balance once per age.',tables=tables(Releases=G('TotalReleases'),Royalty_due='<currency='+G('AnnualRoyalty')+'>',Audience=G('Fans')),choices=[('Collect royalties',collection),('Back to studio',HOME)])

def item(title,icon,key=None,subtitle='',visible='',graph=None,list_id=None):
 x={'Title':title,'Icon':icon,'SecondLine':subtitle,'ActionList':[{'Index':0,'ConditionList':[{'ScenarioID':scene(key),'ScenarioFile':FILE}]}] if key else [{'Index':0,'ConditionList':[{'ListID':list_id}]}]}
 if visible:x['IsVisible']=visible
 if graph:x['BarGraph']={'Title':graph[0],'Value':graph[1],'Style':'LOW_IS_RED'}
 return x
started=f'[gfc.{C}.Started=1]';not_started=f'[gfc.{C}.Started=0]';inactive=f'[gfc.{C}.Active=0]'
hub={'ListID':HUB,'Title':'MUSIC STUDIO','PresentationMode':'Normal','Sections':[
 {'Items':[item('Open Music Studio','mic-studio','open','Start an independent production career',not_started),item('Studio Profile','hero','profile',G('Fans')+' fans · '+G('TotalReleases')+' releases',started,('Reputation',G('Reputation')))]},
 {'Title':'Projects','IsVisible':started,'Items':[item('New Project','cd','new','Create a single, EP or album',inactive),item(G('ProjectTitle'),'cd',None,G('Format')+' · '+G('Genre'),active,('Production',G('Progress')),list_id='genesis_music_studio_project'),item('Release Catalogue','cd',None,'Browse your eight most recent releases',f'[gfc.{C}.TotalReleases>=1]',list_id='genesis_music_studio_catalog')]},
 {'Title':'Studio Business','IsVisible':started,'Items':[item('Distribution','handshake','distribution',G('Distribution')+' · '+G('Share')+'% share'),item('Equipment','imac','equipment','Upgrade your recording space'),item('Royalties','money-bag','royalties','Annual income: <currency='+G('AnnualRoyalty')+'>')]}
]}
project={'ListID':'genesis_music_studio_project','Title':'CURRENT PROJECT','PresentationMode':'Normal','Sections':[
 {'Items':[item(G('ProjectTitle'),'cd','release',G('Format')+' · '+G('Genre'),graph=('Production',G('Progress')))]},
 {'Title':'Production','Items':[item('Songwriting','memo','write','Develop lyrics, hooks and arrangements'),item('Recording','mic','record','Record the finished songs'),item('Mix and Master','headphones','mix','Polish the sound'),item('Collaborator','users','collaborate','Book a guest or session musician',f'[gfc.{C}.Collaborator=0]')]},
 {'Title':'Release Plan','Items':[item('Promotion','megaphone','promote','Launch a campaign',f'[gfc.{C}.PromotionUsed=0]'),item('Publish Project','cd','release','Release when production reaches 100%'),item('Shelve Project','hand-waving','abandon','Discard your current project')]}
]}
catalog={'ListID':'genesis_music_studio_catalog','Title':'RELEASE CATALOGUE','PresentationMode':'Normal','Sections':[{'Items':[item(G(f'Catalog{i}Title'),'cd','catalog'+str(i),G(f'Catalog{i}Format')+' · '+G(f'Catalog{i}Genre'),f'[gfc.{C}.TotalReleases>={i}]',('Reception',G(f'Catalog{i}Quality')))for i in range(1,9)]}]}

def csv_text(header,data):
 s=io.StringIO(newline='');csv.DictWriter(s,fieldnames=header,lineterminator='\n').writeheader()
 w=csv.DictWriter(s,fieldnames=header,lineterminator='\n');w.writerows(data);return s.getvalue().removesuffix('\n')
defaults=csv_text(['key','type','value','reset_on_ageup','minimum','maximum'],[dict(key=k,type=t,value=v,reset_on_ageup='true' if k=='WorkUsed' else '',minimum=lo,maximum=hi)for k,(t,v,lo,hi)in properties.items()])
annual=next(dict(r)for r in rows if r['ScenarioID']==scene('royalties'));annual['ScenarioID']=scene('annual');annual['Filter']=started;annual['HasDismissButton']='false';annual['Choice2_Text']='';annual['Choice2_RouteTo']=''
# Only the annual row lives here; other rows are in the primary scenario resource.
# Its collect route finishes in the same resource to avoid cross-file scenario lookup.
annual['Choice1_AdvancedLogic']=json.dumps(logic([({'expression':f'({G("LastPaidAge")} >= <hero:age>)'},'')],seq(mod('LastPaidAge','=<hero:age>'),f'BP_BANK_BALANCE={G("AnnualRoyalty")}',mod('LifetimeIncome','+'+G('AnnualRoyalty')))),separators=(',',':'))
# Keep every numeric write within the engine's declared schema limits.
# This also protects long careers and repeated production sessions.
def bounded(value):
 import re
 parts=[];depth=0;start=0;i=0
 while i<len(value):
  if value[i]=='<':depth+=1
  elif value[i]=='>' and depth:depth-=1
  elif value[i:i+2]=='>>' and not depth:
   parts.append(value[start:i]);i+=2;start=i;continue
  i+=1
 parts.append(value[start:])
 for i,part in enumerate(parts):
  m=re.fullmatch(r'BP_GFC_MODIFY_PROPERTY=music_studio:([A-Za-z0-9]+):([+-])(.*)',part)
  if m:
   key,op,operand=m.groups();t,initial,lo,hi=properties[key]
   calc=fn('add' if op=='+' else 'sub',G(key),operand)
   parts[i]=mod(key,'='+fn('clamp',calc,lo,hi))
 return route(*parts)
for r in rows+[annual]:
 for i in range(1,5):
  k=f'Choice{i}_AdvancedLogic'
  if r[k]:
   x=json.loads(r[k])
   def visit(o):
    if isinstance(o,dict):
     for key,val in o.items():
      if key=='route_to':o[key]=bounded(val)
      else:visit(val)
    elif isinstance(o,list):
     for val in o:visit(val)
   visit(x);r[k]=json.dumps(x,separators=(',',':'))
  k=f'Choice{i}_RouteTo';r[k]=bounded(r[k])
assets={FILE:csv_text(HEADER,rows),'genesis_music_studio_ageup':csv_text(HEADER,[annual]),'genesis_music_studio_defaults':defaults,HUB:json.dumps(hub,ensure_ascii=False,indent=2),'genesis_music_studio_project':json.dumps(project,ensure_ascii=False,indent=2),'genesis_music_studio_catalog':json.dumps(catalog,ensure_ascii=False,indent=2)}
for name,text in assets.items():(ROOT/(name+('.json' if name in [HUB,'genesis_music_studio_project','genesis_music_studio_catalog'] else '.csv'))).write_text(text)
(ROOT/'assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2))
print(f'Authored {len(rows)} native scenarios, three menus and {len(properties)} character properties.')
