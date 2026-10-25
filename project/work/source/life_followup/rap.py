"""EGGUVOID's rapper idea, connected to the existing record catalogue and bank."""
import csv,io,json
from life_rework.content import p,scene,menu,set_,inc,text,seq,logic,fun,csv_text

SKILLS=['Lyrics','Production','Voice','Vocabulary','Flow','Freestyle','Diss']
PEERS=['Mica Vale','Kestrel','Juno North','Dante Reed']

def build(a,base):
    home=scene('rap_home1105');studio=menu('genesis_music_studio_hub')
    for k,v,hi in [('RapActive',0,1),('RapRole',0,3),('RapRep',10,100),('RapConnections',0,100),('RapEvidence',0,100),('RapSingles',0,100000),('RapAlbums',0,100000),('RapWeek',0,52),('RapReleaseAge',-1,999),('RapAlbumYear',0,12),('RapNeighborhood',50,100),('RapLabel',0,3)]:a.prop(k,v,-1 if v==-1 else 0,hi)
    for k in SKILLS:a.prop('Rap'+k,15,0,100)
    for i in range(4):a.prop('RapPeer'+str(i),40,0,100)
    a.string('RapRoleName','Artist');a.string('RapGenre','Old-school hip-hop');a.string('RapLabelName','Independent');a.string('RapLatest','No record released yet.')
    a.prop('RapLastRelease1105',0,0,1000000);a.prop('RapIsAlbum1105',0,0,1)
    # Hooks snapshot era and real music progress when the existing studio opens.
    enter=logic([('(<hero:age> < 8)',scene('rap_young1105')),(f'({p("Year")} < 1973)',scene('rap_era1105'))],seq(set_('RapActive',1),home))
    a.page('rap_entry1105','Your voice','Write bars, make beats and release records. Your skills and choices shape your sound. Community idea: EGGUVOID.',[('Start / continue',enter),('Back to studio',studio)],'mic-studio')
    a.page('rap_young1105','Still finding your voice','Start writing now. The rapper path opens at age 8; early label offers need strong skills and connections.',[('Back',studio)],'mic-studio')
    a.page('rap_era1105','Before hip-hop','This path opens from 1973. Your era’s recording and performance options remain in the studio.',[('Back',studio)],'calendar')
    a.page('rap_home1105','Rapper life','Your sound: '+p('RapGenre')+'. Role: '+p('RapRoleName')+'. '+p('RapLabelName')+'. Your records stay in the studio catalogue.',[
        ('Sound and practice',scene('rap_practice1105')),('Records and deals',scene('rap_business1105')),('Rappers and home life',scene('rap_people1105')),('Back to studio',studio)],'mic-studio',stats=[('Respect',p('RapRep')),('Connections',p('RapConnections')),('Singles',p('RapSingles')),('Albums',p('RapAlbums'))])
    a.page('rap_practice1105','Find your sound','Each skill supports a different part of your records and battles.',[('Choose your role',scene('rap_role1105')),('Choose a subgenre',scene('rap_genres1105')),('Train a skill',scene('rap_skills1105')),('Back',home)],'musical-notes')
    a.page('rap_role1105','Your role','You can change direction as your career develops.',[(label,a.outcome('rap_role1105_'+str(i),'Chose to work as a '+label.lower()+'.',home,[set_('RapRole',i),text('RapRoleName',label)],extra=((f'({p("RapActive")} != 1)',scene('rap_entry1105')),)))for i,label in enumerate(['Lyricist','Producer','Rapper and producer'],1)]+[('Back',scene('rap_practice1105'))],'mic-studio')
    genres=[('Old-school hip-hop',1973),('Boom bap',1980),('Trap',1990),('Conscious hip-hop',1980),('Drill',2000),('Cloud rap',2010)]
    for page in range(2):
        opts=[]
        for n,(name,year)in enumerate(genres[page*3:page*3+3],page*3):
            dest=a.outcome('rap_genre1105_'+str(n),'Changed your sound to '+name+'.',home,[text('RapGenre',name),'BP_GFC_SET_STRING=music_studio:Genre:Hip-hop'],extra=((f'({p("Year")} < {year})',scene('rap_genre_wait1105')),))
            opts.append((name,dest))
        opts.append(('More styles'if page==0 else'Back',scene('rap_genres_more1105')if page==0 else scene('rap_practice1105')))
        a.page('rap_genres1105'if page==0 else'rap_genres_more1105','Choose your sound','Subgenres open as the calendar advances.',opts,'musical-notes')
    a.page('rap_genre_wait1105','A sound for a later era','That style has not emerged yet. Choose an earlier sound.',[('Back',scene('rap_genres1105'))],'calendar')
    # Training improves the existing studio too. Production is optional.
    for page in range(3):
        opts=[]
        for k in SKILLS[page*3:page*3+3]:
            dest=a.outcome('rap_train1105_'+k,'Practised '+k.lower()+' and improved your studio craft.',scene('rap_skills1105'),[inc('Rap'+k,5),inc('RapRep')],native=161,quota=('RapPractice1105',52))
            opts.append((k,dest))
        opts.append(('More skills'if page<2 else'Back',scene('rap_skills'+str(page+1)+'1105')if page<2 else home))
        a.page('rap_skills1105'if page==0 else'rap_skills'+str(page)+'1105','Practice','Practice supports actual song quality. Your current levels are saved.',opts,'books',stats=[(k,p('Rap'+k))for k in SKILLS[page*3:page*3+3]])
    a.page('rap_business1105','Records and deals','Use the existing studio to write, record and publish. You can release weekly singles and several albums in a year. Labels trade royalty share for reach.',[('Make a record',studio),('Choose a label',scene('rap_labels1105')),('Release history',scene('rap_records1105')),('Back',home)],'mic-studio')
    labelopts=[]
    for i,(name,share,reach,rep)in enumerate([('Independent',90,100,0),('Sidewalk Records',80,140,20),('Northstar Music',65,190,45)]):
        guard=((f'({p("RapRep")} < {rep})',scene('rap_deal_wait1105')),)
        if i:guard+=((f'(<hero:age> < 18) && ({p("RapConnections")} < 65)',scene('rap_deal_wait1105')),)
        dest=a.outcome('rap_label1105_'+str(i),'Agreed a '+name+' distribution deal. Future records use the new royalty share and reach.',home,[set_('RapLabel',i),text('RapLabelName',name),'BP_GFC_SET_STRING=music_studio:Distribution:'+name,'BP_GFC_MODIFY_PROPERTY=music_studio:Share:='+str(share),'BP_GFC_MODIFY_PROPERTY=music_studio:ReachMultiplier:='+str(reach)],extra=guard)
        labelopts.append((name,dest))
    a.page('rap_labels1105','Choose a deal','Independent: 90% share, normal reach. Sidewalk: 80%, wider reach, respect 20. Northstar: 65%, broad reach, respect 45. Under 18 also needs connections 65.',labelopts+[('Back',home)],'briefcase')
    a.page('rap_deal_wait1105','Build your name','This label wants more respect or, for a child artist, stronger connections. No contract was signed.',[('Back',scene('rap_labels1105'))],'briefcase')
    a.page('rap_records1105','Your records',p('RapLatest'),[('Open the full catalogue',menu('genesis_music_studio_catalog')),('Back',home)],'musical-notes',stats=[('Weekly releases this year',p('RapWeek')),('Albums this year',p('RapAlbumYear')),('All singles',p('RapSingles')),('All albums',p('RapAlbums'))])
    a.page('rap_people1105','Your circle','Fictional artists remember support, collaborations and public disputes. Your home choices also affect family ties and reputation.',[('Meet other rappers',scene('rap_peers1105')),('Your neighbourhood',scene('rap_home_life1105')),('Back',home)],'handshake')
    for page in range(2):
        opts=[]
        for i,name in enumerate(PEERS[page*3:page*3+3],page*3):
            key='rap_peer1105_'+str(i);opts.append((name,scene(key)))
            support=a.outcome(key+'_support','Supported '+name+' at a local show. Your connection grew.',scene(key),[inc('RapPeer'+str(i),10),inc('RapConnections',6),inc('RapRep',2)],quota=('RapSocial1105',12))
            freestyle=a.outcome(key+'_freestyle','Traded freestyle verses with '+name+'. Your delivery earned respect and strengthened the connection.',scene(key),[inc('RapPeer'+str(i),10),inc('RapConnections',6),inc('RapRep',4)],extra=((f'({p("RapFreestyle")} < 45) || ({p("RapFlow")} < 35)',scene(key)),),quota=('RapSocial1105',12))
            collab=a.outcome(key+'_collab','Recorded a guest verse with '+name+'. The current studio project gained quality and a collaborator.',studio,[inc('RapPeer'+str(i),3),inc('RapConnections',4),'BP_GFC_MODIFY_PROPERTY=music_studio:Collaborator:=1','BP_GFC_MODIFY_PROPERTY=music_studio:Quality:=<function:add:<GFC.music_studio.Quality>:8>'],extra=((f'({p("RapPeer"+str(i))} < 55)',scene('rap_collab_wait1105')),),quota=('RapSocial1105',12))
            diss=a.outcome(key+'_diss','Released a diss aimed at '+name+'. The dispute gained attention but damaged your relationship.',home,[inc('RapPeer'+str(i),-20),inc('RapRep',-3),inc('RapDiss',3),'BP_GFC_MODIFY_PROPERTY=music_studio:Fans:=<function:add:<GFC.music_studio.Fans>:25>'],quota=('RapSocial1105',12))
            sharp=a.outcome(key+'_sharp_diss','Released a sharp diss aimed at '+name+'. Your writing gained fans and respect, but deepened the feud.',home,[inc('RapPeer'+str(i),-20),inc('RapRep',4),'BP_GFC_MODIFY_PROPERTY=music_studio:Fans:=<function:add:<GFC.music_studio.Fans>:150>'],quota=('RapSocial1105',12))
            battle=logic([(f'({p("RapDiss")} >= 50) && ({p("RapVocabulary")} >= 35)',sharp)],diss)
            connect=logic([(f'({p("RapFreestyle")} >= 45) && ({p("RapFlow")} >= 35)',freestyle)],support)
            a.page(key,name,'Trade verses or support their show. Freestyle 45 and flow 35 earn more respect; a strong diss needs diss skill 50 and vocabulary 35.',[('Trade verses / show support',connect),('Ask for a guest verse',collab),('Release a diss',battle),('Back',scene('rap_peers1105'))],'mic-studio',stats=[('Relationship',p('RapPeer'+str(i)))])
        opts.append(('More artists'if page==0 else'Back',scene('rap_peers_more1105')if page==0 else home))
        a.page('rap_peers1105'if page==0 else'rap_peers_more1105','Other rappers','These are fictional artists in your local scene.',opts,'mic-studio')
    a.page('rap_collab_wait1105','Not yet','Build your relationship to 55 before asking for a guest verse.',[('Back',scene('rap_peers1105'))],'handshake')
    a.page('rap_home_life1105','Where you came from','Fame does not erase your friendships or your choices at home.',[
        ('Help a local youth show',a.outcome('rap_youth1105','Helped a local youth show. Your neighbourhood standing and family ties improved.',home,[inc('RapNeighborhood',8),inc('RapRep',4)],native=111,quota=('RapHome1105',4))),
        ('Spend time with the wrong crowd',scene('wrong_crowd1105')),('Back',home)],'house')
    a.add_tile('genesis_music_studio_hub','Rapper life',scene('rap_entry1105'),'mic-studio','Skills, subgenres, artists and record deals')
    # Remove the old six-session bottleneck, retaining normal progress/quality.
    defaults=list(csv.DictReader(io.StringIO(base['genesis_music_studio_defaults'])))
    for r in defaults:
        if r['key']=='WorkUsed':r['maximum']='312'
    a.assets['genesis_music_studio_defaults']=csv_text(defaults)
    rows=list(csv.DictReader(io.StringIO(base['genesis_music_studio'])))
    for row in rows:
        for k,v in row.items():
            if isinstance(v,str):
                import re
                row[k]=re.sub(r'(<GFC.music_studio.WorkUsed>\s*>=\s*)6\b',r'\g<1>312',v).replace('six studio sessions','a full year of studio sessions')
        if row['ScenarioID']=='scenario.musicStudio.release':
            advanced=json.loads(row['Choice1_AdvancedLogic'])
            checks=[f'({p("RapActive")} == 1) && ({p("RapReleaseAge")} == <hero:age>) && ({p("RapWeek")} >= 52)',f'({p("RapActive")} == 1) && ({p("RapReleaseAge")} == <hero:age>) && ({p("RapAlbumYear")} >= 12) && ({p("RapIsAlbum1105")} == 1)']
            advanced['cases']=[{'if':{'expression':condition},'then':{'route_options':[{'route_to':scene('rap_release_limit1105')}]}}for condition in checks]+advanced['cases']
            row['Choice1_AdvancedLogic']=json.dumps(advanced)
        if row['ScenarioID']=='scenario.musicStudio.open':
            advanced=json.loads(row['Choice1_AdvancedLogic'])
            for case in advanced['cases']:
                if case.get('if',{}).get('expression')=='(<hero:age> < 16)':
                    case['if']['expression']=f'(<hero:age> < 16) && (({p("RapActive")} != 1) || (<hero:age> < 8) || ({p("RapConnections")} < 65))'
            row['Choice1_AdvancedLogic']=json.dumps(advanced)
    a.assets['genesis_music_studio']=csv_text(rows)
    a.page('rap_release_limit1105','Your release schedule is full','You can publish up to 52 records and 12 albums per year. Keep practising or age up before your next release.',[('Back to studio',studio)],'calendar')
