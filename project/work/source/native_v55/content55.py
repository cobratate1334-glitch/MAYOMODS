"""Repair existing menus and attach receipts only to successful effect routes."""
import csv,io,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path.insert(0,str(SOURCE/'native_v29'))
from content import writecsv
OWNERS={'f1_career':('genesis_v7_defaults_f1_career','genesis_careers_v7','genesis_v7_f1_career'), 'tv_host':('genesis_v7_defaults_tv_host','genesis_careers_v7','genesis_v7_tv_host'), 'music_studio':('genesis_music_studio_defaults','genesis_music_studio','genesis_music_studio_hub')}

def build():
 a=json.loads((SOURCE/'native_v54/assets.json').read_text());schemas=json.loads((SOURCE/'native_v54/schemas.json').read_text());events=[];audit={'plain_scene_routes':0,'icons':0,'enabled_controls':0,'receipts':0,'journal_choices':0}
 for k,v in list(a.items()):a[k]=v.replace('Compiled by Atlanti','MayoMods')
 def icon(title,old):
  title=title.lower()
  for words,new in [(['cardinal'],'49-cardinal'),(['bishop'],'49-bishop'),(['pope','holy see'],'49-pope'),(['seminary','formation'],'49-gate'),(['conclave'],'49-conclave'),(['church','parish','religious service'],'49-basilica'),(['race','driver','qualif'],'race-car'),(['episode','television','on-camera','show format','ratings','broadcast'],'tv'),(['rehearsal','filming'],'movie-camera'),(['study','homework','research'],'books'),(['collaborat','colleague','producer','team development'],'handshake'),(['recording','speaking','studio','vocal'],'microphone'),(['music','song','single','choir'],'musical-note'),(['injury','nurse','health','therapy'],'49-health'),(['journal','record','profile'],'49-journal'),(['bonus','royalt','earnings'],'money-bag'),(['comment','reply','discussion','post'],'speech-balloon')]:
   if any(w in title for w in words):return 'mayomods49/icons/'+new if new.startswith('49-')else new
  return 'mayomods49/icons/'+old if old.startswith('49-')else old
 def walk(v):
  if isinstance(v,list):
   for x in v:walk(x)
  elif isinstance(v,dict):
   for k,x in list(v.items()):
    if k=='ScenarioID'and isinstance(x,str)and x.startswith('BP_')and '>>scenario.'in x:v[k]=x.rsplit('>>',1)[1];audit['plain_scene_routes']+=1
    elif k=='IsEnabled'and isinstance(x,str)and x.startswith('v14-')and current_menu.startswith('genesis_music_studio'):v.pop(k);audit['enabled_controls']+=1
    else:walk(x)
   if 'Icon'in v:
    old=v['Icon'];v['Icon']=icon(str(v.get('Title','')),old);audit['icons']+=int(old!=v['Icon'])
 for key,val in list(a.items()):
  if val.startswith('{'):
   try:d=json.loads(val)
   except ValueError:continue
   current_menu=key;walk(d);a[key]=json.dumps(d,indent=2)
 # The work counters reset explicitly when opening the affected career,
 # including old saves whose authored age-up sheet was missing.
 for owner,(defaults,dataset,hub)in OWNERS.items():
  defs=list(csv.DictReader(io.StringIO(a[defaults])))
  for name,typ,value,lo,hi in [('Receipt55','int',0,0,5000),('WorkAge55','int',-1,-1,999)]:
   if not any(r['key']==name for r in defs):defs.append(dict(key=name,type=typ,value=value,reset_on_ageup='',minimum=lo,maximum=hi))
  a[defaults]=writecsv(defs);schemas[owner]={r['key']:r for r in defs}
 rows_by={k:list(csv.DictReader(io.StringIO(a[k])))for k in ['genesis_careers_v7','genesis_music_studio']}
 for owner,(defaults,dataset,hub)in OWNERS.items():
  rows=rows_by[dataset]
  result_scene='scenario.musicStudio.result55'if owner=='music_studio'else'scenario.careersV7.result55_'+owner
  for row in rows:
   scene=row.get('ScenarioID','')
   if owner!='music_studio'and not scene.startswith('scenario.careersV7.'+owner):continue
   for n in range(1,5):
    field='Choice'+str(n);label=row.get(field+'_Text','');event_id=len(events)+1
    if not label:continue
    title=re.sub('<[^>]+>','project',row.get('Title','Activity')).replace('·','-')
    msg='I completed '+title[:65]+': '+re.sub('<[^>]+>','my project',label)[:90]+'.'
    changed=[False]
    def receipt(route):
     if not isinstance(route,str)or '>>'not in route:return route
     mutations=re.findall(r'BP_GFC_(?:MODIFY_PROPERTY|SET_STRING)='+re.escape(owner)+r':([^:=]+)',route)
     if not mutations or all(k.startswith(('NativeCareerSync','ExpectedCareer','NativeHire','NativeWorkImpact'))for k in mutations):return route
     head,target=route.rsplit('>>',1)
     if target.startswith('BP_')and not target.startswith('BP_SHOW_LIST='):return route
     changed[0]=True;audit['receipts']+=1
     target=result_scene if target=='BP_SHOW_LIST='+hub or target.endswith(('.sessionDone','.releaseDone','.royaltyDone'))else target
     return head+'>>BP_GFC_MODIFY_PROPERTY='+owner+':Receipt55:='+str(event_id)+'>>'+target
    route=row.get(field+'_RouteTo','')
    if route:row[field+'_RouteTo']=receipt(route)
    logic=row.get(field+'_AdvancedLogic','')
    if logic:
     try:d=json.loads(logic)
     except ValueError:continue
     def visit(v):
      if isinstance(v,list):
       for x in v:visit(x)
      elif isinstance(v,dict):
       for k,x in list(v.items()):
        if k=='route_to':v[k]=receipt(x)
        elif k=='cases'and isinstance(x,list):v[k]=[c for c in x if 'if'in c];visit(v[k])
        else:visit(x)
     visit(d);row[field+'_AdvancedLogic']=json.dumps(d,separators=(',',':'))
    if changed[0]:events.append(dict(id=event_id,owner=owner,text=msg,scene=scene,choice=n-1))
  template=rows[0];r=dict.fromkeys(template,'');r.update(ScenarioID=result_scene,Style='normal',ExteriorTitle='MayoMods',Title='Activity complete',HasDismissButton='true',EmojiString={'f1_career':'race-car','tv_host':'tv','music_studio':'microphone'}[owner],Body='<GFC.gameplay52.ResultBody55>',Choice1_Text='Continue',Choice1_ButtonStyle='normal',Choice1_RouteTo='BP_SHOW_LIST='+hub);rows.append(r)
 for key,rows in rows_by.items():a[key]=writecsv(rows)
 # Compact church panels use real supplied scenes, with only the central
 # status values visible; the detailed progression menu stays accessible.
 for key in ['genesis_activities_v18','genesis_activities_v12']:
  rows=list(csv.DictReader(io.StringIO(a[key])));unique={r['ScenarioID']:r for r in rows}
  for r in unique.values():
   if r['ScenarioID']=='scenario.activitiesV18.action52_91':
    r['ExteriorTitle']='Church & Seminary';r['TableRows']=json.dumps([dict(row=i,key=k+':',value='<GFC.gameplay52.'+v+'>')for i,(k,v)in enumerate([('Role','ClergyRankName'),('Theology','Theology'),('Discipline','Discipline'),('Community trust','ParishTrust')],1)])
   if r.get('EmojiString','').startswith('49-'):r['EmojiString']='mayomods49/icons/'+r['EmojiString']
   for n in range(1,5):
    p='Choice'+str(n);route=r.get(p+'_RouteTo','');label=r.get(p+'_Text','')
    if route and not r.get(p+'_AdvancedLogic')and not r.get(p+'_LogEntryLine1')and 'BP_GFC_MODIFY_PROPERTY='in route and not any(w in route for w in ['Sync','Roll','Action:','Native','Selected','Filter']):
     if not any(w in label.lower()for w in ['back','view','show','refresh','close','continue','cancel','help']):r[p+'_LogEntryLine1']='I '+re.sub('<[^>]+>','my activity',r.get('Title','took part in an activity'))[:90]+': '+re.sub('<[^>]+>','my choice',label)[:110]+'.';audit['journal_choices']+=1
  a[key]=writecsv(list(unique.values()))
 defs=list(csv.DictReader(io.StringIO(a['genesis_v18_defaults_gameplay52'])));defs.append(dict(key='ResultBody55',type='string',value='Complete an activity to see its saved outcome.',reset_on_ageup='',minimum='',maximum=''));a['genesis_v18_defaults_gameplay52']=writecsv(defs);schemas['gameplay52']={r['key']:r for r in defs}
 (ROOT/'assets.json').write_text(json.dumps(a,indent=2)+'\n');(ROOT/'schemas.json').write_text(json.dumps(schemas,indent=2)+'\n');(ROOT/'receipts55.json').write_text(json.dumps(events,indent=2)+'\n');(ROOT/'content_changes55.json').write_text(json.dumps(audit,indent=2)+'\n');print(audit,flush=True)
if __name__=='__main__':build()
