from content import *
c='social_v18';p=lambda k:G(c,k)
for j in range(1,25):
 for k,v,lo,hi in [('Age',0,0,999),('YearsFriends',0,0,999),('ProfileId20',0,0,2147483647),('AdultHeight20',178,140,235),('HeightPref20',0,0,2),('DateBonus20',0,-8,8)]:prop(c,f'C{j}'+k,v,lo,hi)
 for k in ['Personality20','Hobby20','Ambition20','Clubs20','Belief20','Story20','Preference20']:text(c,f'C{j}'+k,'Not yet known')
 if j<=22:
  add('profile20_'+str(j),p(f'C{j}Name'),'Personality: '+p(f'C{j}Personality20')+'. In their free time they enjoy '+p(f'C{j}Hobby20')+'. They hope to '+p(f'C{j}Ambition20')+'. '+p(f'C{j}Story20'),[('Talk about their future',seq(M(c,'NativeContactImpact',j),S('contact'+str(j)))),('Back',S('contact'+str(j)))],icon='handshake',tables=table(Age=p(f'C{j}Age'),Known_as=p(f'C{j}Role'),Years_as_friends=p(f'C{j}YearsFriends'),Connection=p(f'C{j}Connection'),Interests_and_clubs=p(f'C{j}Clubs20'),Beliefs=p(f'C{j}Belief20'),Dating_preference=p(f'C{j}Preference20')))
# Distinct lives stay in the existing contact menu, without another root entrance.
for row in rows:
 sid=row['ScenarioID']
 for j in range(1,23):
  if sid==S('contact'+str(j)):
   row['Body']='Personality: '+p(f'C{j}Personality20')+'. Enjoys '+p(f'C{j}Hobby20')+'. Goal: '+p(f'C{j}Ambition20')+'. '+p(f'C{j}Story20')
   row['Choice2_Text']='Their story / spend time';row['Choice2_RouteTo']=S('profile20_'+str(j))
   row['TableRows']=json.dumps(table(Role=p(f'C{j}Role'),Age=p(f'C{j}Age'),Connection=p(f'C{j}Connection'),Years_as_friends=p(f'C{j}YearsFriends')),separators=(',',':'))
  if sid==S('date'+str(j)):
   height=G('life_v18','Height');pref=p(f'C{j}HeightPref20');other=p(f'C{j}AdultHeight20')
   expr=logic([(f'({pref} == 1) && ({height} < {other})',M(c,f'C{j}DateBonus20',8)),(f'({pref} == 2) && ({height} > {other})',M(c,f'C{j}DateBonus20',8)),(f'({pref} != 0)',M(c,f'C{j}DateBonus20',-4))],M(c,f'C{j}DateBonus20',0))
   # A preparatory scene keeps the condition grammar native and typed.
   add('date_height20_'+str(j),'Relationship choices',choices=[('Continue',logic([(case['if']['expression'],seq(case['then']['route_options'][0]['route_to'],S('date_ready20_'+str(j))))for case in expr['cases']],seq(M(c,f'C{j}DateBonus20',0),S('date_ready20_'+str(j)))))],icon='heart')
   ready=dict(row);ready['ScenarioID']=S('date_ready20_'+str(j));ready['Body']='Every person has their own preferences. Height gives a small individual modifier; connection and their choice matter more.';rows.append(ready)
   row.update(Choice1_Text='Review dating choices',Choice1_RouteTo=seq(M('life_v18','NativeLifeSync',1),S('date_height20_'+str(j))),Choice1_AdvancedLogic='',Choice2_Text='',Choice2_RouteTo='',Choice2_AdvancedLogic='',Choice3_Text='Back to contact',Choice3_RouteTo=S('contact'+str(j)),Choice4_Text='',Choice4_RouteTo='')
  if sid in [S('askdate'+str(j)),S('secretdate'+str(j))]:
   raw=row['Choice1_AdvancedLogic'];old=F('add',30,F('div',p(f'C{j}Connection'),2));new=F('add',p(f'C{j}DateBonus20'),old);row['Choice1_AdvancedLogic']=raw.replace(old,new)
# Refresh body information whenever contacts refresh; profile generation is stable.
for name,value in list(assets.items()):assets[name]=value.replace(M(c,'NativeSocialSync',1),seq(M('life_v18','NativeLifeSync',1),M(c,'NativeSocialSync',1)))
