"""1105 extensions to existing native lists, scenarios and saved containers."""
import copy,csv,io,json,re
csv.field_size_limit(16*1024*1024)
from life_rework.content import Author,csv_text,scene,menu,p,set_,inc,text,seq,logic,fun


class Extension(Author):
    def __init__(self,base):
        super().__init__(base)
        self.rows=list(csv.DictReader(io.StringIO(base['genesis_life_rework'])))
        for row in self.rows:
            if row['EmojiString']=='speech-balloon':row['EmojiString']='chat-bubble'
        self.schema=list(csv.DictReader(io.StringIO(base['genesis_rework_defaults'])))
        self.fields={r['key']for r in self.schema}

    def page(self,k,title,body,choices,icon='books',stats=None):
        icon={'heart':'heart-red','briefcase':'case-money','boxing-glove':'boxing','speech-balloon':'chat-bubble'}.get(icon,icon)
        return super().page(k,title,body,choices,icon,stats)

    def tile(self,label,route,icon='books',detail=''):
        icon={'heart':'heart-red','briefcase':'case-money','boxing-glove':'boxing','speech-balloon':'chat-bubble'}.get(icon,icon)
        sync='BP_GFC_MODIFY_PROPERTY=life_rework:NativeAction:=1>>'
        if route.startswith(sync):route=route[len(sync):]
        if route.startswith('BP_SHOW_LIST=')and'>>'not in route:
            tile=super().tile(label,scene('locked'),icon,detail)
            tile['ActionList'][0]['ConditionList'][0]={'ListID':route.split('=',1)[1]}
            return tile
        assert route.startswith('scenario.')and'>>'not in route,route
        return super().tile(label,route,icon,detail)

    def add_tile(self,name,label,target,icon='books',detail=''):
        d=json.loads(self.assets.get(name,self.base[name]));collection='Items'if 'Items'in d else'ListItems'
        d[collection].append(self.tile(label,target,icon,detail));self.assets[name]=json.dumps(d,indent=2)

    def filtered(self,filter_,yes,no):
        if filter_=='[hero.inPrison]':condition=f'({p("NativeInPrison1105")} == 1)'
        else:
            match=re.fullmatch(r'\[finance.bankBalance<([0-9]+)\]',filter_);assert match,filter_
            condition=f'({p("NativeBank1105")} < {match[1]})'
        return logic([(condition,yes)],no)

    def replace_page(self,key,**values):
        row=next(r for r in self.rows if r['ScenarioID']==scene(key));row.update(values);return row


def queue(a):
    for k,v,lo,hi in [('AnnualAge1105',-1,-1,999),('NewsYear1105',0,0,3999),('WarNews1105',0,0,1),('DraftEligible1105',0,0,1),('SchoolEvent1105',0,0,8),('CrowdEvent1105',0,0,1)]:a.prop(k,v,lo,hi)
    a.string('NewsTitle1105');a.string('NewsBody1105')
    a.page('world_news1105',p('NewsTitle1105'),p('NewsBody1105'),[('Continue','')],'newspaper')
    rows=[]
    def row(key,source,filter_):
        r=copy.deepcopy(next(r for r in a.rows if r['ScenarioID']==scene(source)))
        r.update(ScenarioID=scene(key),Filter=filter_,IsAgeUpScenario='true',HasDismissButton='false')
        rows.append(r)
    row('annual_world1105','world_news1105','[gfc.life_rework.WarNews1105=1]')
    enlist=a.gate(seq(set_('NativeAction',31),scene('annual_enlist_receipt1105')),adult=True,extra=((f'({p("DraftEligible1105")} != 1)',scene('locked')),))
    a.page('annual_enlist_receipt1105','Your call-up',p('WarReport'),[('Continue','')],'rescue-helmet')
    defer=a.outcome('annual_exemption1105','Requested an exemption from this year’s call-up. You kept your current job.', '',[set_('DraftAge','<hero:age>'),inc('WarMorale',-2)])
    a.page('annual_callup_prompt1105','A wartime call-up','Your country has entered '+p('WarName')+'. You have been called for service. Accepting may replace your current job with military service. You can find missions in the military duty menu.',[('Report for service',enlist),('Request an exemption',defer)],'rescue-helmet')
    row('annual_draft1105','annual_callup_prompt1105','[gfc.life_rework.DraftEligible1105=1]')
    cases=[
        ('Bullying at lunch','A student keeps taking another pupil’s lunch. What do you do?',[
            ('Tell a teacher','Asked a teacher to stop the bullying.',[set_('SchoolBullyStage',2),inc('SchoolSafety',12),inc('SchoolTrust',5)],10),
            ('Stand with the pupil','Supported a pupil who was being bullied.',[set_('SchoolBullyStage',1),inc('SchoolFriends',6)],112),
            ('Start a fight','Started a school fight and received a discipline warning.',[set_('SchoolBullyStage',3),inc('SchoolSuspensions'),inc('SchoolStress',10)],13)]),
        ('A new classmate',p('SchoolPeer1105')+' is sitting alone. You have room at your table.',[
            ('Invite them over','Invited a classmate to sit with you.',[inc('SchoolFriends',7),inc('SchoolStress',-3)],112),
            ('Keep to yourself','Kept to yourself at lunch.',[inc('SchoolStress',2)],0)]),
        ('A test is coming','Your teacher announces a test. How will you prepare?',[
            ('Make a study plan','Made a study plan before a school test.',[inc('SchoolPrep',12),inc('SchoolStress',-2)],10),
            ('Leave it until later','Put off preparing for a school test.',[inc('SchoolPrep',-5),inc('SchoolStress',7)],0)]),
        ('The teacher checks in','The teacher asks whether the bullying you reported has stopped.',[
            ('Thank the teacher','Thanked the teacher for following up on bullying.',[set_('SchoolBullyStage',4),inc('SchoolSafety',8),inc('SchoolTrust',6)],10),
            ('Report another incident','Reported another incident and asked for closer supervision.',[set_('SchoolBullyStage',2),inc('SchoolSafety',5)],10)]),
        ('After the school fight','Your teacher wants to discuss the fight and your behaviour.',[
            ('Apologize and accept help','Apologized for a school fight and accepted help.',[set_('SchoolBullyStage',4),inc('SchoolTrust',6),inc('SchoolStress',-4)],10),
            ('Refuse to discuss it','Refused to discuss a school fight.',[set_('SchoolBullyStage',4),inc('SchoolTrust',-8)],12)]),
        ('A familiar face','The pupil you supported asks to sit with you again.',[
            ('Make room','Made room for a classmate you had supported.',[set_('SchoolBullyStage',4),inc('SchoolFriends',8)],112),
            ('Find another table','Sat at another table this time.',[set_('SchoolBullyStage',4)],0)])]
    for index,(title,body,choices)in enumerate(cases,1):
        opts=[(label,a.outcome('annual_school_choice1105_'+str(index)+'_'+str(i),message,'',effects,native=native))for i,(label,message,effects,native)in enumerate(choices)]
        key='annual_school_prompt1105_'+str(index);a.page(key,title,body,opts,'chat-bubble')
        row('annual_school1105_'+str(index),key,f'[gfc.life_rework.SchoolEvent1105={index}]')
    a.page('annual_crowd_prompt1105','A rivalry reaches home','An old dispute has put your family under strain. A confrontation could leave someone hurt.',[
        ('Seek help and step away',a.outcome('annual_crowd_help1105','Sought help and stepped away from a dangerous rivalry.','',[inc('CrowdRisk1105',-30),inc('CrowdRival1105',-15)],native=111)),
        ('Stay involved',a.outcome('annual_crowd_hurt1105','Stayed involved in a rivalry and were hurt in a confrontation.','',[inc('CrowdRisk1105',10),inc('CrowdRival1105',10)],native=114))],'chat-bubble')
    row('annual_crowd1105','annual_crowd_prompt1105','[gfc.life_rework.CrowdEvent1105=1]')
    a.page('annual_marriage_prompt1105','Your spouse wants change',p('MarriageSpouse1105')+' says the repeated conflicts cannot continue.',[
        ('Promise to work on it',a.outcome('annual_marriage_listen1105','Agreed to work on your marriage.','',[inc('MarriageTrust1105',4),inc('MarriageConflicts1105',-1)],native=141)),
        ('Agree to a separation',a.outcome('annual_marriage_separate1105','Agreed to a separation while deciding what comes next.','',[set_('MarriagePhase1105',1),set_('MarriageFiledAge1105','<hero:age>')],native=143))],'heart-red')
    row('annual_marriage1105','annual_marriage_prompt1105','[gfc.life_rework.MarriageEvent1105=1]')
    # Every annual branch ends at a receipt with an empty Continue route. No
    # automatic event opens a list in the middle of the native age-up queue.
    a.assets['genesis_rework_annual1105']=csv_text(rows,list(a.header))


def eras(a):
    # Gate authored events as well as menu entries. Native random social pushes
    # are separately gated in era_native.py; text is never rewritten on display.
    starts=[(r'only\s*fans',2016),(r'tik\s*tok',2018),(r'instagram',2010),(r'facebook',2004),(r'you\s*tube',2005),(r'roblox',2006),(r'twitter',2006),(r'soundcloud',2007),(r'\btwitch\b',2011),(r'\bdiscord\b',2015),(r'\breddit\b',2005),(r'smartphone|iphone|android phone',2007),(r'\binternet\b|\bwebsite\b|\bemail\b|\be-mail\b',1991),(r'video game|gaming console',1972),(r'\btelevision\b|\bTV show\b',1936)]
    for name,value in a.base.items():
        value=a.assets.get(name,value)
        if not name.startswith('genesis_')or not value.startswith('ScenarioID,'):continue
        rows=list(csv.DictReader(io.StringIO(value)));changed=False
        if any(None in row for row in rows):continue
        for r in rows:
            visible=' '.join(v for k,v in r.items()if v and isinstance(v,str)and (k in ['Title','Body']or re.match(r'Choice\d_Text',k)))
            year=max((y for pattern,y in starts if re.search(pattern,visible,re.I)),default=0)
            if year:
                old=r.get('Filter','');gate=f'[gfc.era44.Year>={year}]'
                if gate not in old:r['Filter']=old+gate;changed=True
        if changed:a.assets[name]=csv_text(rows)


def build(base):
    a=Extension(base)
    for k in ['HeightRevision1105','HeightManual1105','PlayedFatherHeight1105','PlayedMotherHeight1105']:
        rows=list(csv.DictReader(io.StringIO(a.assets.get('genesis_v18_defaults_life_v18',base['genesis_v18_defaults_life_v18']))))
        rows.append(dict(key=k,type='int',value=0,reset_on_ageup='',minimum=0,maximum=1105 if 'Revision'in k else 250 if 'Played'in k else 1))
        a.assets['genesis_v18_defaults_life_v18']=csv_text(rows)
    a.prop('NativeAction',0,0,255)
    a.prop('NativeBank1105',0,0,2000000000);a.prop('NativeInPrison1105',0,0,1)
    next(r for r in a.schema if r['key']=='NativeAction')['maximum']='255'
    from life_followup.rap import build as rap
    from life_followup.school import build as school
    from life_followup.sports import build as sports
    from life_followup.prison import build as prison
    from life_followup.marriage import build as marriage
    from life_followup.genetics import build as genetics
    for f in [rap,school,sports,prison,marriage,genetics]:f(a,base)
    queue(a);eras(a)
    # Merge shared sheets AFTER all authors; no extra root tabs or second studios.
    a.assets['genesis_life_rework']=csv_text(a.rows,list(a.header))
    a.assets['genesis_rework_defaults']=csv_text(a.schema)
    lines=base['genesis_feature_containers'].splitlines();start=next(i for i,s in enumerate(lines)if s.startswith('ContainerId,'))
    rows=list(csv.DictReader(io.StringIO('\n'.join(lines[start:]))))
    for row in rows:
        if row['ContainerId']=='life_rework':row['AgeUpActionList']='genesis_rework_annual1105'
    a.assets['genesis_feature_containers']='\r\n'.join(lines[:start])+'\r\n'+csv_text(rows)
    return a.assets
