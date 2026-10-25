"""Execute authored native routes with the reference economy, not Android."""
import copy,csv,io,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native_studio'))
import test_studio as t

assets=json.loads((ROOT/'assets.json').read_text())
baseline=json.loads((ROOT.parent/'native_studio/assets.json').read_text())
combined=baseline|assets
oldprops=copy.deepcopy(t.properties)
t.rows.clear();t.lists.clear();t.properties.clear()
for name,content in combined.items():
 if name.endswith('_defaults'):
  t.properties.update({r['key']:r for r in csv.DictReader(io.StringIO(content))})
 elif content.startswith('{'):
  d=json.loads(content);t.lists[d['ListID']]=d
 else:
  raw=list(csv.reader(io.StringIO(content)))
  if raw[0][0]=='ScenarioID':
   assert all(len(r)==53 for r in raw),'invalid native scenario row width'
   for r in csv.DictReader(io.StringIO(content)):
    assert r['ScenarioID']not in t.rows;t.rows[r['ScenarioID']]=r
for k,v in oldprops.items():t.check(v==t.properties[k],'v5 property schema preserved '+k)
for name,content in combined.items():
 for key in re.findall(r'<GFC\.music_studio\.([A-Za-z0-9]+)>',content):t.check(key in t.properties,'unknown property tag '+key)
 for key in re.findall(r'gfc\.music_studio\.([A-Za-z0-9]+)(?:>=|<=|!=|=|>|<)',content):t.check(key in t.properties,'unknown filter property '+key)
 if name.endswith('_defaults'):continue
 if content.startswith('{'):continue
 for row in csv.DictReader(io.StringIO(content)):
  for fld in ['TableRows','BarGraphs','Sliders']:
   if row[fld]:json.loads(row[fld])
  for i in range(1,5):
   values=list(t.routes(json.loads(row[f'Choice{i}_AdvancedLogic']))) if row[f'Choice{i}_AdvancedLogic'] else [row[f'Choice{i}_RouteTo']]
   for value in values:
    for part in t.split_route(value):
     if not part:continue
     if part.startswith('scenario.'):t.check(part in t.rows,'unresolved scenario '+part)
     elif part.startswith('BP_SHOW_LIST='):t.check(part.split('=',1)[1]in t.lists,'unresolved list')
     elif part.startswith(('BP_GFC_MODIFY_PROPERTY=','BP_GFC_SET_STRING=')):
      c,k,v=part.split('=',1)[1].split(':',2);t.check(c=='music_studio'and k in t.properties,'invalid write target')
     else:t.check(part.startswith('BP_BANK_BALANCE='),'unsupported blueprint')
for d in t.lists.values():
 for section in d['Sections']:
  for item in section.get('Items',[]):
   t.check(bool(item.get('Icon')),'menu icon missing')
   for act in item['ActionList']:
    for c in act['ConditionList']:t.check(c.get('ScenarioID')in t.rows or c.get('ListID')in t.lists,'menu route unresolved')

M=t.Model
def choose(m,k,i=1):return m.choose('label'+k,i)
def snapshot(m):return (m.money,copy.deepcopy(m.props))
def make(money=1000000):
 m=M(age=18,money=money);m.choose('open');choose(m,'Open');choose(m,'Name');return m
m=M(age=17,money=10000);m.choose('open');before=snapshot(m)
t.check(choose(m,'Open')=='scenario.musicStudio.labelUnavailable'and snapshot(m)==before,'label age gate is atomic')
m=M(age=18,money=999);m.choose('open');before=snapshot(m)
t.check(choose(m,'Open')=='scenario.musicStudio.labelNoFunds'and snapshot(m)==before,'unfunded label launch unchanged')
m=make();t.check(m.money==999000 and m.props['LabelStarted']==1,'launch pays real bank')
before=snapshot(m);choose(m,'Open');t.check(snapshot(m)==before,'duplicate launch blocked')
for i in range(1,5):choose(m,str(i)+'Contract',i%3+1)
t.check(all(m.props[f'Artist{i}Years']==3 for i in range(1,5)),'four contracts persisted')
for i in range(1,5):
 before=snapshot(m);choose(m,str(i)+'Contract');t.check(snapshot(m)==before,'duplicate signing blocked')
before=snapshot(m);m.money=0;before=snapshot(m);choose(m,'1Fund',3);t.check(snapshot(m)==before,'unfunded album is atomic')
m.money=1000000
choose(m,'1Fund',3);t.check(m.props['Artist1Budget']==15000,'album funding paid')
before=snapshot(m);choose(m,'1Release');t.check(snapshot(m)==before,'unfinished release blocked')
choose(m,'1Develop',2);choose(m,'1Produce');choose(m,'1Produce',2);choose(m,'1Produce',3)
t.check(m.props['Artist1Progress']==100,'native production reaches release stage')
choose(m,'1Promote',3);before=snapshot(m);choose(m,'1Promote',3);t.check(snapshot(m)==before,'campaign charged once')
choose(m,'1Release');t.check(m.props['Artist1Releases']==1 and m.props['Artist1Gross']>0,'release contributes catalogue income')
before=snapshot(m);choose(m,'1Release');choose(m,'1Fund');t.check(snapshot(m)==before,'one release per artist per age')
before=snapshot(m);choose(m,'Royalties');t.check(snapshot(m)==before,'label pays starting next age')
m.props['AnnualRoyalty']=12345;m.age_up();bank=m.money
m.choose('annual');t.check(m.money==bank+12345+m.props['LabelNet'],'annual statement pays studio and label together')
t.check(m.props['LabelGross']==m.props['LabelArtistPaid']+m.props['LabelNet'],'money conserved across all artist shares')
t.check(m.props['Artist1Recovered']<=m.props['Artist1Cut'] and m.props['Artist1Advance']>=0,'advance recoupment capped to artist royalty')
before=snapshot(m);m.choose('annual');choose(m,'Royalties');m.choose('royalties');t.check(snapshot(m)==before,'all repeated claims blocked')
t.check(m.props['Artist1WorkUsed']==0 and m.props['Artist1Years']==2,'age resets sessions and settles contract year')
# The two independent manual claims cannot duplicate the combined age statement.
for order in ['label_first','studio_first','both_first','none_first']:
 x=make();choose(x,'1Contract');x.props.update(Artist1Gross=20000,AnnualRoyalty=4000);x.age_up();bank=x.money
 if order in ['label_first','both_first']:choose(x,'Royalties')
 if order in ['studio_first','both_first']:x.choose('royalties')
 x.choose('annual');t.check(x.money-bank==15000,'manual/annual settlement order '+order)
 t.check(x.props['Artist1Cut']==10000 and x.props['Artist1Recovered']==1000 and x.props['Artist1Advance']==0,'artist gets 9000 after recoupment')
# Expiry retains catalogue, blocks new projects; renewing costs an advance once.
x=make();choose(x,'1Contract');x.props['Artist1Gross']=20000
for yr in range(3):x.age_up();choose(x,'Royalties')
t.check(x.props['Artist1Years']==0 and x.props['Artist1Gross']==20000,'expired deal retains catalogue')
before=snapshot(x);choose(x,'1Fund');choose(x,'1Develop');t.check(snapshot(x)==before,'expired deal blocks new work')
x.age_up();bank=x.money;choose(x,'Royalties');t.check(x.money==bank+10000,'expired catalogue still pays')
choose(x,'1Contract',2);t.check(x.props['Artist1Years']==3 and x.props['Artist1Share']==70 and x.props['Artist1Advance']==5000,'renewal replaces split and records advance')
before=snapshot(x);choose(x,'1Contract',2);t.check(snapshot(x)==before,'renewal charged once')
# Repeated missed collection doesn't retroactively duplicate pay; suspended project is retained.
x.age_up();choose(x,'1Fund');choose(x,'1Shelve');t.check(x.props['Artist1Active']==0,'project shelving state')
for yr in range(3):x.age_up()
choose(x,'Royalties');t.check(x.props['Artist1Years']==2,'one settlement equals one contract year')
# Studio ceiling and longest simulated label careers preserve schema and arithmetic safety.
for i in range(1,5):
 p=f'Artist{i}';x.props.update({p+'Gross':10000000,p+'Share':100,p+'Advance':1000000,p+'Years':3,p+'Fans':10000000,p+'Quality':100,p+'Boost':100})
 x.props['LabelReputation']=100
for year in range(25):
 x.age_up();x.choose('annual');before=snapshot(x);x.choose('annual');t.check(snapshot(x)==before,'long career settlement idempotence')
t.check(x.props['LabelIncome']<=2000000000 and x.props['LabelGross']==40000000,'label numeric caps')
y=make();choose(y,'1Contract');choose(y,'1Fund',3)
y.props.update(Artist1Fans=10000000,Artist1Progress=100,Artist1Quality=100,Artist1Boost=100,LabelReputation=100)
choose(y,'1Release');t.check(y.props['Artist1Gross']==100000,'max audience release formula bounded')
# Round-trip reference persisted state, including outstanding advances and active records.
restored=M(age=x.age,money=x.money);restored.props=json.loads(json.dumps(x.props))
t.check(restored.props==x.props,'all studio/label properties survive reference serialization')
result=dict(content_assertions=t.checks,native_scenarios=len(t.rows),native_lists=len(t.lists),typed_properties=len(t.properties),android_runtime_tested=False)
(ROOT/'content_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
