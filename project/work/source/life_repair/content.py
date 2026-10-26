"""Native scenario pages, contextual receipts and connected existing menus."""
import copy,csv,io,json,re
from life_followup.content import Extension as Previous
from life_rework.content import p,scene,menu,set_,inc,text,seq,logic,csv_text


def context(key):
    for terms,label in [('school exam bully classmate club','School life'),('war trench flight mine cabinet campaign invasion command','Wartime'),('prison inmate yard sentence','Prison life'),('heist crew crime','Crime'),('storm tsunami volcano field','Field research'),('rap studio music album','Music'),('fight camp fighter weigh','Fight Club'),('family ancestry marriage birth trait','Family'),('basket soccer football sports coach manager','Sport'),('church seminary clergy','Church')]:
        if any(t in key.lower()for t in terms.split()):return label
    return 'Your life'


class Author(Previous):
    def page(self,key,title,body,choices,icon='books',stats=None):
        target=super().page(key,title,body,choices,icon,stats);self.rows[-1]['ExteriorTitle']=context(key)
        return target
    def outcome(self,key,*args,**kwargs):
        result=super().outcome(key,*args,**kwargs)
        self.rows[-1]['Title']={'School life':'What happened next','Crime':'The crew responds','Wartime':'Mission update','Prison life':'In the yard','Field research':'Research office','Music':'The scene reacts'}.get(context(key),'What happened next')
        return result
    def edit(self,key):return next(r for r in self.rows if r['ScenarioID']==scene(key))
    def choices(self,key,choices):
        row=self.edit(key)
        for i in range(1,5):
            for name in ['Text','ButtonStyle','RouteTo','AdvancedLogic']:row['Choice'+str(i)+'_'+name]=''
        for i,(label,route)in enumerate(choices,1):
            row['Choice'+str(i)+'_Text']=label;row['Choice'+str(i)+'_ButtonStyle']='normal';row['Choice'+str(i)+('_AdvancedLogic'if isinstance(route,dict)else'_RouteTo')]=json.dumps(route)if isinstance(route,dict)else route


def build(base):
    a=Author(base)
    for key in ['SchoolNativeFight1106','NativeMinefield1106']:a.prop(key,0,0,1)
    a.prop('SchoolReputation1106',40,0,100);a.prop('WarNativeMissionAge1106',-1,-1,999)
    a.prop('MissionBriefAge1106',-1,-1,999)
    a.prop('AnnualContinuation1106',0,0,0)
    a.prop('SchoolCombatAge1106',-1,-1,999);a.prop('SchoolCombatDoneAge1106',-1,-1,999)
    from life_repair.intelligence import build as intelligence
    a.string('PeerResponse1106','A cellmate seems worried. Ask whether they want to talk.')
    for r in a.schema:
        if r['key']=='SchoolEvent1105':r['maximum']='24'
    from life_repair.school import build as school
    from life_repair.heist import build as heist
    from life_repair.war import build as war
    school(a,base);heist(a,base);war(a,base);intelligence(a,base)
    # Report errors must show a NEW response rather than trying to re-open the
    # exact scenario the engine has just removed after AcceptChoice.
    for kind in ['storm','tsunami','volcano']:
        home=menu({'storm':'genesis_v18_storm_career19','tsunami':'genesis_v18_tsunami_career21','volcano':'genesis_v18_volcano_career21'}[kind])
        a.page(kind+'_report_wait1106','Nothing ready to submit','Finish a field survey this year before delivering a report. If you already submitted it, your payment is recorded.',[('Back to research',home)],'memo')
        r=a.edit(kind+'_record');r['Choice1_AdvancedLogic']=r['Choice1_AdvancedLogic'].replace(scene(kind+'_record'),scene(kind+'_report_wait1106'))
        paid=a.edit(kind+'_paid');paid['Title']='Report accepted';paid['ExteriorTitle']='Research office';paid['Body']='The research office accepts your findings and pays the agreed fee. Your report is added to this year’s archive. Plan a new survey after aging up.'
    # A genuine, explicit response in the old inmate support workflow. Retain
    # the original action's native relationship effect, and preserve navigation.
    for name in ['genesis_activities_v8','genesis_v8_inmate_support']:
        rows=list(csv.DictReader(io.StringIO(base[name])))
        for row in rows:
            if row['ScenarioID']=='scenario.activitiesV8.inmateSupport':
                row.update(ExteriorTitle='Prison yard',Title='A cellmate opens up',EmojiString='handshake',Body='They listen for a moment, then admit they have been struggling. “Thanks for hearing me out.” Offering support improved your bond; it does not erase a long-standing rivalry.',Choice1_Text='Back to prison',Choice1_RouteTo=menu('genesis_v18_prison40'))
        a.assets[name]=csv_text(rows)
    # A training entrance for the SAME existing fighter, without passing the
    # fighting game's typed list into an ArrayList-only Genesis injector.
    lines=base['genesis_feature_containers'].splitlines();start=next(i for i,s in enumerate(lines)if s.startswith('ContainerId,'));registry=list(csv.DictReader(io.StringIO('\n'.join(lines[start:]))))
    for row in registry:
        if row['ContainerId']=='fight_camp_entry':row.update(EntryMenu='T4',EntryLabel='Fight Club training',EntrySecondLine='Training for your existing fighter; join the original scene first')
        if row['ContainerId']=='crime_entry54_62':row.update(EntryLabel='Heists & crew',EntrySecondLine='Plan a job; manage your crew and review consequences',EntryListID='genesis_heists1106')
        if row['ContainerId']=='crime_entry54_64':row['EntryMenu']=''
        if row['ContainerId']=='life_rework':row['DisplayName']='Life events'
    relative=list(csv.DictReader(io.StringIO(base['genesis_v18_defaults_relationship21'])));relative += [{'key':'SelectedAge1106','type':'int','value':'0','reset_on_ageup':'','minimum':'0','maximum':'999'},{'key':'SelectedName1106','type':'string','value':'Unavailable','reset_on_ageup':'','minimum':'','maximum':''}];relative.append({'key':'BirthCountry1106','type':'string','value':'Unrecorded','reset_on_ageup':'','minimum':'','maximum':''});a.assets['genesis_v18_defaults_relationship21']=csv_text(relative)
    a.assets['genesis_feature_containers']='\n'.join(lines[:start])+'\n'+csv_text(registry)
    annual_followups(a)
    # All native custom pages get useful category titles and same-file receipts.
    a.assets['genesis_life_rework']=csv_text(a.rows,list(a.header));a.assets['genesis_rework_defaults']=csv_text(a.schema)
    feedback(a,base)
    stories(a,base)
    # Keep the annual controller's explicit continuations current after every
    # subsystem has added pages. LoadGfcFilteredScenarios selects by the raw
    # Filter column, NOT IsAgeUpScenario. Give manual continuations a genuinely
    # impossible filter on a schema-clamped constant; LoadScenario still finds
    # them by ID when the player makes a choice.
    annual=list(csv.DictReader(io.StringIO(a.assets['genesis_rework_annual1105'])))
    regular=list(csv.DictReader(io.StringIO(a.assets['genesis_life_rework'])));latest={r['ScenarioID']:r for r in regular}
    annual=[r for r in annual if r.get('IsAgeUpScenario','').lower()=='true']
    annual += [dict(r,IsAgeUpScenario='false',Filter='[gfc.life_rework.AnnualContinuation1106=1]')for r in regular]
    a.assets['genesis_rework_annual1105']=csv_text(annual)
    # Resolve every icon against the actual shipped catalog, retaining dedicated
    # original artwork where present rather than inventing unsupported aliases.
    icons={r['EmojiString']for r in csv.DictReader(io.StringIO(base['genesis_lookup_emoji_visuals']))}
    aliases={'paint-palette':'art','hamster':'paw','soccer-ball':'soccer','lock':'padlock','microphone':'mic-studio'}
    for name,value in list(a.assets.items()):
        if value.startswith('ScenarioID,'):
            rows=list(csv.DictReader(io.StringIO(value)))
            for r in rows:
                icon=r.get('EmojiString','')
                if icon and icon not in icons and not icon.startswith(('mayomods49/','mayomods1104/')):r['EmojiString']=next((x for x in [aliases.get(icon,''),'memo']if x in icons),'books')
            a.assets[name]=csv_text(rows)
    # Register original SVG artwork through the game's real emoji catalog.
    glyphs=list(csv.DictReader(io.StringIO(base['genesis_lookup_emoji_visuals'])));index=max(int(r['Index'])for r in glyphs)
    for n,name in enumerate(['art','pet','microphone','school','trench','aircraft','crew','storm'],1):glyphs.append({'Index':str(index+n),'EmojiString':'scene1106-'+name,'Preview':'','Asset Name':'scene1106-'+name})
    a.assets['genesis_lookup_emoji_visuals']=csv_text(glyphs)
    for name,value in list(a.assets.items()):
        if not value.startswith('ScenarioID,'):continue
        rows=list(csv.DictReader(io.StringIO(value)))
        for r in rows:
            key=r['ScenarioID'];icon=None
            if 'trench'in key:icon='trench'
            elif 'flight'in key:icon='aircraft'
            elif 'heist'in key:icon='crew'
            elif 'storm'in key:icon='storm'
            elif 'school_case1106_7'in key:icon='art'
            elif 'school_case1106_12'in key:icon='pet'
            elif 'school_case1106_10'in key:icon='microphone'
            elif 'school_case1106_'in key:icon='school'
            if icon:r['EmojiString']='scene1106-'+icon
        a.assets[name]=csv_text(rows)
    # A parser may still request a model before the motor-car period. Keep a
    # real non-motor carriage record available for that fallback.
    from native_v45.assets45 import codec
    decode,encode=codec();cars=list(csv.DictReader(io.StringIO(decode(base['a16_car-models-enc']))))
    old=list(cars);car=next(dict(r)for r in cars if r['Make']=='Mayo');car.update(Model='1880 Road carriage',Cost='$200',**{'Luxury Only':'','Race Car Dealership Only':'','Racing Class':'C'});cars.append(car)
    assert cars[:-1]==old;a.assets['a16_car-models-enc']=encode(csv_text(cars))
    return a.assets


def annual_followups(a):
    # The native selector returns one match per container. During a war make
    # its headline the entry, then explicitly continue into an eligible call-up,
    # extra historical bulletin and school story. Otherwise these competed in
    # a lottery and a war-start notice could be skipped entirely.
    school=[]
    for n in range(1,25):
        key='annual_school1105_'if n<7 else'annual_school1106_'
        school.append((f'({p("SchoolEligible")} == 1) && ({p("SchoolEvent1105")} == {n})',scene(key+str(n))))
    historical=(f'({p("WarExtraNews1106")} > 0)',scene('war_extra_news1106'))
    after_news=logic([(f'({p("DraftEligible1105")} == 1)',scene('annual_callup_prompt1105')),historical]+school,'')
    after_draft=logic([historical]+school,'');after_history=logic(school,'')
    for key in ['annual_enlist_receipt1105','annual_exemption1105_result']:
        row=a.edit(key);row['Choice1_RouteTo']='';row['Choice1_AdvancedLogic']=json.dumps(after_draft)
    row=a.edit('war_extra_news1106');row['Choice1_RouteTo']='';row['Choice1_AdvancedLogic']=json.dumps(after_history)
    rows=list(csv.DictReader(io.StringIO(a.assets['genesis_rework_annual1105'])))
    for row in rows:
        if row.get('IsAgeUpScenario','').lower()!='true':continue
        if row['ScenarioID']==scene('annual_world1105'):
            row['Choice1_RouteTo']='';row['Choice1_AdvancedLogic']=json.dumps(after_news)
        else:row['Filter']+='[gfc.life_rework.WarNews1105=0]'
    a.assets['genesis_rework_annual1105']=csv_text(rows)


def feedback(a,base):
    """Audit all mod CSV choices; put an acknowledgement before a menu return."""
    for name,value in {**base,**a.assets}.items():
        if not name.startswith('genesis_')or not value.startswith('ScenarioID,'):continue
        rows=list(csv.DictReader(io.StringIO(value)))
        if any(None in row for row in rows):continue
        additions=[];changed=False
        for row in rows:
            if 'mayomods'in row.get('ExteriorTitle','').lower():row['ExteriorTitle']=context(row['ScenarioID']+' '+row.get('Title',''));changed=True
            for i in range(1,5):
                label=row.get(f'Choice{i}_Text','')
                if not label or re.search(r'\b(back|close|continue|cancel|return)\b',label,re.I):continue
                column=f'Choice{i}_AdvancedLogic';advanced=row.get(column,'');routes=[]
                if advanced:
                    data=json.loads(advanced);routes=[c['then']['route_options'][0]for c in data.get('cases',[])]+data.get('else_when_no_matches',{}).get('route_options',[])
                else:routes=[{'route_to':row.get(f'Choice{i}_RouteTo','')}]
                for index,route in enumerate(routes):
                    target=route.get('route_to','')
                    # Only mod transactions that end by dismissing a menu or
                    # showing their own page; existing explicit receipts stay.
                    if not isinstance(target,str):continue
                    mutates=any(t in target for t in ['BP_GFC_MODIFY_PROPERTY=','BP_BANK_BALANCE=','BP_GFC_SET_STRING='])
                    tail=target.rsplit('>>',1)[-1]
                    if not mutates or not(tail.startswith('BP_SHOW_LIST=')or tail=='BP_DISMISS_ALL_LISTS'or tail==row['ScenarioID']):continue
                    key=row['ScenarioID'].rsplit('.',1)[0]+'.receipt1106_'+re.sub('[^A-Za-z0-9_]','_',row['ScenarioID'])+'_'+str(i)+'_'+str(index)
                    receipt=dict.fromkeys(row,'');parent=tail if tail.startswith('BP_SHOW_LIST=')else menu('genesis_v18_prison40')if 'prison'in(name+target).lower()else''
                    report=row.get(f'Choice{i}_LogEntryLine1','')or label.rstrip('.')+'. Your choice has been recorded.'
                    receipt.update(ScenarioID=key,Style='normal',ExteriorTitle=context(row['ScenarioID']),Title=label,Body=report,EmojiString=row.get('EmojiString')or'memo',HasDismissButton='true',Choice1_Text='Continue',Choice1_ButtonStyle='normal',Choice1_RouteTo=parent)
                    additions.append(receipt);route['route_to']=target[:-len(tail)]+key;changed=True
                if advanced:row[column]=json.dumps(data)
                else:row[f'Choice{i}_RouteTo']=routes[0]['route_to']
        if changed:a.assets[name]=csv_text(rows+additions)


def stories(a,base):
    for name in ['genesis_activities_v18']:
        rows=list(csv.DictReader(io.StringIO(a.assets.get(name,base[name]))))
        for r in rows:
            if r['ScenarioID'].endswith(('person_story21','friend_story21')):
                r['ExteriorTitle']='Someone you know';r['Title']='<GFC.relationship21.SelectedName1106>'
                r['Body']='Personality: <GFC.relationship21.Personality>.\n\nInterests: <GFC.relationship21.Hobby>.\n\nPlans: <GFC.relationship21.Ambition>.\n\n<GFC.relationship21.Story>'
                r['TableRows']='';r['Choice1_Text']='Back to their details';r['Choice1_RouteTo']=''
        a.assets[name]=csv_text(rows)
