"""Simple native editor, saved library, share-code transport and playable stories."""
import csv,io,json
from life_rework.content import p,scene,seq,set_,inc,text,logic,csv_text
from era_world.creator_native import FIELDS,META,SLOTS
def build(a,base):
 def act(n):return seq(set_('NativeAction',1),set_('CreatorAction1119',n),set_('NativeAction',0),set_('NativeAction',912))
 def page(key,title,body,choices,icon='memo',stats=None):
  icon={'pencil':'native1119/eras/school/icons/art_portfolio','arrow-up':'memo','arrow-down':'books'}.get(icon,icon)
  a.page('creator_'+key,title,body,choices,icon,stats);a.rows[-1]['ExteriorTitle']='Mod Creator'
 def go(key):return scene('creator_'+key)
 home='BP_SHOW_LIST=genesis_v18_community35';draft=go('draft1119');result=go('result1119')
 for key in ['CreatorAction1119','CreatorSlot1119','CreatorSuccess1119','CreatorPlayEffectA1119','CreatorPlayEffectB1119','CreatorPlayMinAge1119','CreatorPlayMaxAge1119','CreatorPlayMinYear1119','CreatorPlayMaxYear1119']:a.prop(key,0,0,3999)
 a.prop('CreatorPlayedAge1119',-1,-1,999);a.prop('CreatorPlayCount1119',0,0,1000000)
 for prefix,suffix in [('CreatorDraft','1119'),('CreatorPlay','1119')]+[('CreatorS'+str(n)+'_','')for n in range(1,SLOTS+1)]:
  for key in FIELDS:a.string(prefix+key+suffix,'Empty slot'if key=='Title'and prefix.startswith('CreatorS')else'')
  for key,value in zip(META,[0,130,1,3999,1,0]):a.prop(prefix+key+suffix,value,0,3999)
  if prefix.startswith('CreatorS'):a.prop(prefix+'Used',0,0,1)
 for k,v in [('CreatorCode1119',''),('CreatorShare1119',''),('CreatorStatus1119','Create a story or open your saved scenarios.')]:a.string(k,v)
 import copy
 menu=json.loads(base['genesis_v18_community35']);legacy=copy.deepcopy(menu);legacy.update(Title='INCLUDED ACTIVITIES',ListID='genesis_v18_included1119');a.assets['genesis_v18_included1119']=json.dumps(legacy,indent=2)
 key='Items'if'Items'in menu else'ListItems'
 menu['Title']='MOD CREATOR';menu[key]=[
  a.tile('New scenario',go('new1119'),'native1119/eras/school/icons/art_portfolio','Write a story with two choices'),
  a.tile('Saved scenarios',go('library1119'),'books','Twelve slots kept across your lives'),
  a.tile('Import',go('import1119'),'books','Paste a shared scenario code'),
  a.tile('Export draft',go('export1119'),'memo','Copy a code to share'),
  a.tile('How it works',go('help1119'),'light-bulb','A short guide'),
  a.tile('Included activities','BP_SHOW_LIST=genesis_v18_included1119','books','Keep using the included game additions')]
 a.assets['genesis_v18_community35']=json.dumps(menu,indent=2)
 parent=json.loads(base['genesis_v18_expansions46'])
 for tile in parent.get('Items',parent.get('ListItems',[])):
   if tile['Title']=='Community Expansions':tile.update(Title='Mod Creator',SecondLine='Create and share your own scenarios',Icon='native1119/eras/school/icons/art_portfolio')
 a.assets['genesis_v18_expansions46']=json.dumps(parent,indent=2)
 # This feature declaration can also supply the visible entry. Rename both
 # declarations so runtime menu population cannot re-add the old label.
 lines=base['genesis_feature_containers'].splitlines(keepends=True);columns=None
 for i,line in enumerate(lines):
  if line.startswith('ContainerId,'):columns=next(csv.reader([line]))
  if line.startswith('community35,'):
   row=next(csv.reader([line]));assert columns
   for key,value in [('DisplayName','Mod Creator'),('EntryLabel','Mod Creator'),('EntryEmoji','native1119/eras/school/icons/art_portfolio'),('EntrySecondLine','Create and share your own scenarios')]:row[columns.index(key)]=value
   out=io.StringIO();csv.writer(out,lineterminator='').writerow(row);lines[i]=out.getvalue()+('\r\n'if line.endswith('\r\n')else'\n')
 a.assets['genesis_feature_containers']=''.join(lines)
 for name in ['genesis_activities_v12','genesis_activities_v18']:
  rows=list(csv.DictReader(io.StringIO(base[name])));changed=False
  for row in rows:
   for n in range(1,5):
    if row.get(f'Choice{n}_Text')=='Community Expansions':
     row[f'Choice{n}_Text']='Included activities';row[f'Choice{n}_RouteTo']=row[f'Choice{n}_RouteTo'].replace('BP_SHOW_LIST=genesis_v18_community35','BP_SHOW_LIST=genesis_v18_included1119');changed=True
  if changed:a.assets[name]=csv_text(rows)
 def template(title,body,choice_a,result_a,choice_b,result_b,school=False):
  values=[text('CreatorDraft'+key+'1119',value)for key,value in zip(FIELDS,[title,body,choice_a,result_a,choice_b,result_b])]
  if school:values+=[set_('CreatorDraftMinAge1119',6),set_('CreatorDraftMaxAge1119',18)]
  return seq(act(1),*values,draft)
 page('new1119','New scenario','Start a draft or change one of these examples. Your saved scenarios stay in the library.',[
  ('Blank draft',seq(act(1),draft)),
  ('School art project',template('School art project','Your class is making a display. A classmate has no paints. What do you do?','Share your paints','You finish the display together. Your classmate thanks you.','Work on your own','You finish your part and pack your things.',True)),
  ('Neighbourhood project',template('Neighbourhood project','Your neighbours are planting a small garden. They ask you to join them.','Help with the planting','You spend the afternoon together and enjoy seeing the garden take shape.','Wish them luck','You stop for a quick chat before heading home.')),
  ('Back',home)],'pencil')
 page('draft1119',p('CreatorDraftTitle1119'),p('CreatorDraftBody1119'),[('Edit story',go('story1119')),('Edit choices',go('choices1119')),('Rules and effects',go('rules1119')),('Save or export',go('save1119'))],'pencil')
 page('story1119','Your story','Tap a field. Type your own words. Keep it short and clear.',[('Title',go('edit1119_Title')),('Story text',go('edit1119_Body')),('Back',draft)],'memo')
 page('choices1119','Two choices','Each choice has a label and a result. Set its effect in Rules and effects.',[(label,go('edit1119_'+field))for label,field in [('Choice A','ChoiceA'),('Result A','ResultA'),('Choice B','ChoiceB'),('Result B','ResultB')]],'chat-bubble')
 for field in FIELDS:
  page('edit1119_'+field,{'Title':'Scenario title','Body':'What happens?','ChoiceA':'First choice','ChoiceB':'Second choice','ResultA':'First result','ResultB':'Second result'}[field],'Type below. Titles and choices can use 80 characters. Stories and results can use 600.',[('Keep text',draft),('Cancel',draft)],'pencil')
 page('rules1119','Rules and effects','Choose when this story can be played. Effects are limited to keep choices clear.',[('Age rules',go('age1119')),('Year rules',go('year1119')),('Choice effects',go('effects1119')),('Back',draft)],'calendar', [('Minimum age',p('CreatorDraftMinAge1119')),('Maximum age',p('CreatorDraftMaxAge1119')),('First year',p('CreatorDraftMinYear1119')),('Last year',p('CreatorDraftMaxYear1119'))])
 page('age1119','Who can play?','These limits apply when you play the saved story.',[(label,seq(set_('CreatorDraftMinAge1119',lo),set_('CreatorDraftMaxAge1119',hi),go('rules1119')))for label,lo,hi in [('All ages',0,130),('School ages',6,18),('Adults',18,130)]]+[('Back',go('rules1119'))],'calendar')
 page('year1119','Choose an era','Year limits apply to the current year in the life.',[(label,seq(set_('CreatorDraftMinYear1119',lo),set_('CreatorDraftMaxYear1119',hi),go('rules1119')))for label,lo,hi in [('1800s',1800,1899),('1900–1999',1900,1999),('Modern years',2000,3999)]]+[('Any year',seq(set_('CreatorDraftMinYear1119',1),set_('CreatorDraftMaxYear1119',3999),go('rules1119')))],'calendar')
 page('effects1119','Choice effects','A choice can change a stat or money. You can complete one custom story per age.',[('First choice',go('effectA1119')),('Second choice',go('effectB1119')),('Back',go('rules1119'))],'heart-red')
 for side in ['A','B']:
  effects=[('Story only',0),('Happiness +2',1),('Health -5',2)]
  page('effect'+side+'1119','Effect for choice '+side,'Choose a small consequence.',[(label,seq(set_('CreatorDraftEffect'+side+'1119',value),go('effects1119')))for label,value in effects]+[('Money effects',go('money'+side+'1119'))],'heart-red')
  page('money'+side+'1119','Money effect','Money comes from or goes to the actual bank balance.',[('Receive $100',seq(set_('CreatorDraftEffect'+side+'1119',3),go('effects1119'))),('Pay $100',seq(set_('CreatorDraftEffect'+side+'1119',4),go('effects1119'))),('Back',go('effects1119'))],'money-bag')
 page('save1119','Save or share','The draft stays here until you replace it. Saved stories stay across New Life.',[('Save in a slot',go('save_slots1119_0')),('Copy share code',seq(act(5),result)),('Back',draft),('Mod Creator',home)],'books')
 for group in range(4):
  choices=[('Slot '+str(n),seq(set_('CreatorSlot1119',n),go('confirm_save1119')))for n in range(group*3+1,group*3+4)]
  choices.append(('More',go('save_slots1119_'+str(group+1)))if group<3 else('Back',go('save1119')))
  page('save_slots1119_'+str(group),'Choose a save slot','Saving replaces only the slot you choose.',choices,'books')
  saved=[(p('CreatorS'+str(n)+'_Title'),seq(set_('CreatorSlot1119',n),go('slot1119')))for n in range(group*3+1,group*3+4)]
  saved.append(('More',go('saved1119_'+str(group+1)))if group<3 else('Back',home))
  page('saved1119_'+str(group),'Saved scenarios','Choose a story. Empty slots can be filled from your draft.',saved,'books')
 page('confirm_save1119','Save this draft?','This replaces the selected slot. Other stories stay saved.',[('Save',seq(act(2),result)),('Back',go('save1119'))],'books',[('Slot',p('CreatorSlot1119'))])
 page('library1119','Saved scenarios','Load your library from this device.',[('Open library',seq(act(12),go('saved1119_0'))),('Back',home)],'books')
 page('slot1119','Your scenario','Play it or load it into the editor. An empty slot must be saved first.',[('Play',seq(act(8),go('ready1119'))),('Edit',seq(act(3),go('loaded1119'))),('Delete',go('delete1119')),('Back',go('saved1119_0'))],'books',[('Slot',p('CreatorSlot1119'))])
 page('loaded1119','Your draft',p('CreatorStatus1119'),[('Continue',logic([(f'({p("CreatorSuccess1119")} == 1)',draft)],result)),('Back',home)],'pencil')
 page('delete1119','Delete this scenario?','Only the selected slot will be cleared.',[('Delete',seq(act(4),result)),('Keep it',go('slot1119'))],'memo')
 page('import1119','Import a scenario','Paste a share code. Import fills your draft. Review it before saving.',[('Paste from clipboard',seq(act(7),result)),('Type or paste code',go('edit1119_Code')),('Back',home)],'books')
 page('edit1119_Code','Scenario code','Paste the complete code. Invalid codes keep your draft and library unchanged.',[('Import',seq(act(6),result)),('Cancel',home)],'memo')
 page('export1119','Export draft','Copy your draft as a share code. To export a saved story load it with Edit first.',[('Copy share code',seq(act(5),result)),('Saved scenarios',go('library1119')),('Back',home)],'books')
 page('result1119','Mod Creator',p('CreatorStatus1119'),[('Draft',draft),('Saved scenarios',go('library1119')),('Mod Creator',home)],'memo')
 page('help1119','Make a story','Create a draft. Write a title and story. Add two choices with results. Set rules and effects. Save in a slot. Play from Saved scenarios. Copy a share code to send it to someone. They can import it here. Codes are data. They do not run scripts.',[('Create',go('new1119')),('Back',home)],'books')
 eligible=logic([(f'({p("CreatorSuccess1119")} != 1)',result),(f'(<hero:age> < {p("CreatorPlayMinAge1119")}) || (<hero:age> > {p("CreatorPlayMaxAge1119")}) || ({p("Year")} < {p("CreatorPlayMinYear1119")}) || ({p("Year")} > {p("CreatorPlayMaxYear1119")})',go('ineligible1119'))],go('play1119'))
 page('ready1119','Play this story?',p('CreatorStatus1119'),[('Play',eligible),('Back',go('slot1119'))],'books')
 page('ineligible1119','Not available in this life','This story has age or year limits. No choice or money was used.',[('Back',go('slot1119'))],'calendar')
 routes=[]
 for side in ['A','B']:
  outcome=go('outcome'+side+'1119');once=(f'({p("CreatorPlayedAge1119")} >= <hero:age>)',go('played1119'))
  mark=[set_('CreatorPlayedAge1119','<hero:age>'),inc('CreatorPlayCount1119'),text('JournalMessage',p('CreatorPlayResult'+side+'1119')),inc('JournalSequence')]
  effects=[]
  for value,steps in [(1,[set_('NativeAction',911)]),(2,[set_('NativeAction',14)]),(3,['BP_BANK_BALANCE=100']),(4,['BP_BANK_BALANCE=-100'])]:
   target=seq(*mark,*steps,outcome)
   if value==4:target=logic([(f'({p("NativeBank1105")} < 100)',scene('funds'))],target)
   effects.append((f'({p(f"CreatorPlayEffect{side}1119")} == {value})',target))
  routes.append(a.gate(logic(effects,seq(*mark,outcome)),extra=(once,)))
  page('outcome'+side+'1119',p('CreatorPlayTitle1119'),p('CreatorPlayResult'+side+'1119'),[('Continue',go('slot1119'))],'memo')
 page('play1119',p('CreatorPlayTitle1119'),p('CreatorPlayBody1119'),[(p('CreatorPlayChoiceA1119'),routes[0]),(p('CreatorPlayChoiceB1119'),routes[1])],'books')
 page('played1119','Story completed','You have completed a custom scenario at this age. Age up to play another. Your library stays saved.',[('Back',home)],'calendar')
