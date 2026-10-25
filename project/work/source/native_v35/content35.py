"""Community gameplay authored in the shipped Genesis routing/save schema."""
import copy,csv,hashlib,io,json,sys,zipfile
from collections import Counter
from pathlib import Path
import UnityPy
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native_v29'))
import content as d
from content import F,G,M,I,T,S,seq,logic,table,add,tile,child,menu,prop,text

RawF=F
def F(name,*args):
    # Use only function names present in the original game interpreter.
    if name=='equals':return RawF('clamp',RawF('sub',1,RawF('abs',RawF('sub',*args))),0,1)
    return RawF(name,*args)

OWNER='community35' 
p=lambda k:G(OWNER,k)
m=lambda k,v:M(OWNER,k,v)
i=lambda k,v=1:I(OWNER,k,v)
t=lambda k,v:T(OWNER,k,v)
H='BP_SHOW_LIST=genesis_v18_community35'
hub=lambda section:'BP_SHOW_LIST=genesis_v18_'+section+'35'
scene=lambda k:S('c35_'+k)
back=('Back',H)
def page(k,title,body='',choices=(),icon='memo',stats=None):
    return add('c35_'+k,title,body,choices,icon,tables=table(**stats)if stats else None)
def item(title,k,icon='memo',sub=''):return tile(title,scene(k),icon,sub)
def prop35(k,value=0,maximum=100,minimum=0,reset=False):prop(OWNER,k,value,minimum,maximum,reset)
def string35(k,value):text(OWNER,k,value)
def check(cases,success):return logic(cases,success)
def require(expr,fail,success):return check([(expr,scene(fail))],success)
def cost(amount,success):
    return {'cases':[{'if':{'filter':f'[finance.bankBalance<{amount}]'},'then':{'route_options':[{'route_to':scene('funds')}]}}],
        'else_when_no_matches':{'route_options':[{'route_to':seq(f'BP_BANK_BALANCE=-{amount}',success)}]}}
def adult(success):return check([('(<hero:age> < 18)',scene('adult'))],success)
def roll():return seq(M('careers_v18','NativeCupRoll',0),M('careers_v18','NativeCupRoll',1))
def sync():return seq(M('life_v18','NativeLifeSync',0),M('life_v18','NativeLifeSync',1),M('world20','NativeWorldSync20',0),M('world20','NativeWorldSync20',1))
def impact(value):return seq(M('life_v18','NativeWellbeing',0),M('life_v18','NativeWellbeing',value))
def trait_bonus(ids,extra,base):return F('add',base,*[F('mul',F('equals',p('Trait35'),x),extra)for x in ids])

def author():
    base=json.loads((ROOT.parent/'native_v34/assets.json').read_text())
    d.assets={};d.schemas={};d.rows=[];d.registry=[]
    page('funds','Not enough money','Your bank balance cannot cover this purchase. Nothing was bought.',[back],icon='money-bag')
    page('adult','Available from age 18','This activity unlocks in adulthood.',[back],icon='suitcase')
    page('limit','A full schedule','You have used this activity’s allowance for this age. Age up to refresh it.',[back],icon='calendar')
    page('paid','Income already collected','You have collected this account’s income at your current age.',[back],icon='money-bag')
    page('none','Nothing to collect yet','Build a catalogue or an operating business first.',[back],icon='money-bag')
    page('income','Income collected','The payment has been added to your game bank balance.',[back],icon='money-bag')
    for k in ['MangaPaidAge','TVPaidAge','BusinessPaidAge','FootagePaidAge']:prop35(k,-1,999,-1)
    prop35('Trait35',0,12);string35('TraitName35','No additional trait');string35('TraitDescription35','Choose an additional personality trait.')

    # Additional archetypes supplement the nine original personality IDs.
    traits=[('Ambitious','You pursue difficult goals and polish your public reputation.','Pitching manga earns more reputation.'),
      ('Bookish','You enjoy finding ideas in books and thoughtful conversations.','Story practice improves manga quality faster.'),
      ('Perfectionist','You refine small details until the work feels right.','Art practice produces a larger quality gain.'),
      ('Sociable','You feel comfortable bringing people into a conversation.','Making school friends builds stronger support.'),
      ('Reserved','You recharge through quiet time and a small trusted circle.','Quiet reflection restores more wellbeing.'),
      ('Family oriented','You make time for relatives and remember what matters to them.','Family visits strengthen connections more.'),
      ('Outdoorsy','You notice the weather and enjoy working outside.','Successful farm harvests earn a yield bonus.'),
      ('Creative','You look for unexpected ways to turn an idea into a story.','Manga art practice gains an extra quality boost.'),
      ('Practical','You plan around the resources and tools actually available.','Maintained farm machinery reduces weather losses further.'),
      ('Music lover','You seek music and notice the feeling a good performance creates.','Anime voice production receives a quality bonus.'),
      ('Patient','You can listen, wait and resolve tension without rushing.','Calm cast negotiations restore more TV morale.'),
      ('Competitive','You enjoy a clear challenge and tracking your improvement.','Campus campaign speeches attract more supporters.')]
    for n,(name,description,benefit)in enumerate(traits,1):
        page('trait'+str(n),name,description+' '+benefit,[('Choose this trait',seq(m('Trait35',n),t('TraitName35',name),t('TraitDescription35',description),scene('trait_profile'))),('Back',hub('traits'))],icon='face-thinking')
    page('trait_profile',p('TraitName35'),p('TraitDescription35'),[('Choose another trait',hub('traits')),back],icon='face-thinking')
    menu('traits35','Additional Personality Traits',[item(name,'trait'+str(n),'face-thinking',description)for n,(name,description,_)in enumerate(traits,1)])

    # Manga: separate pitch, preparation, deadlines, sales and adaptation.
    for k,v,hi in [('MangaGenre',0,2),('MangaConcept',0,2),('MangaActive',0,1),('MangaQuality',25,100),('MangaReputation',10,100),('MangaAssistants',0,3),('MangaWeek',0,1000000),('MangaSales',0,2000000000),('MangaFans',0,10000000),('MangaRoyalty',0,20000000),('AnimeStudio',0,3),('AnimeCast',0,3),('AnimeQuality',0,100),('AnimeActive',0,1),('AnimeEpisodes',0,12),('AnimeSeries',0,1000000)]:prop35(k,v,hi)
    prop35('MangaWork',0,8,reset=True);string35('MangaGenreName','Shonen');string35('MangaTitle','Clockwork City');string35('AnimeStudioName','No studio selected')
    manga_home=scene('manga')
    page('manga','Mangaka & Anime','Pitch an original series, meet chapter deadlines and grow an audience. Eight writing, art or chapter sessions are available per age.',
       [('Series concept & genre',scene('manga_concept')),('Publisher and weekly work',scene('manga_work')),('Anime adaptation',scene('anime')),('Catalogue & royalties',scene('manga_record'))],icon='notebook',stats={'Series':p('MangaTitle'),'Genre':p('MangaGenreName'),'Quality':p('MangaQuality'),'Copies_sold':p('MangaSales')})
    concepts=[('Clockwork City','A young mechanic discovers a city that rewinds every midnight.'),('Last Orbit','A stranded crew must save its home without losing each other.'),('After the Rain','Two rivals rebuild a community theatre and find a shared purpose.')]
    page('manga_concept','Choose your premise','Pick the story you want to develop.',[(name,require(f'({p("MangaActive")} == 1)','manga_locked',seq(m('MangaConcept',n),t('MangaTitle',name),scene('manga_genre'))))for n,(name,_)in enumerate(concepts)]+[('Back',manga_home)],icon='light-bulb')
    page('manga_genre','Choose a manga genre','Shonen: adventurous ensemble stories. Seinen: complex drama. Shoujo: relationships and personal growth.',[(name,seq(m('MangaGenre',n),t('MangaGenreName',name),scene('manga_pitch')))for n,name in enumerate(['Shonen','Seinen','Shoujo'])]+[('Back',manga_home)],icon='books')
    page('manga_locked','An active series','Finish or archive this series before replacing its concept.',[('Back',manga_home)],icon='notebook')
    page('manga_pitch','Publisher pitch','Develop quality to at least 35, then send your premise to a publisher. The editorial submission costs 250.',
      [('Pitch the series',check([('(<hero:age> < 16)',scene('manga_young')),(f'({p("MangaActive")} == 1)',scene('manga_locked')),(f'({p("MangaQuality")} < 35)',scene('manga_reject'))],cost(250,seq(m('MangaActive',1),i('MangaReputation',F('add',4,F('mul',F('equals',p('Trait35'),1),4))),scene('manga_accepted'))))),('Practice first',scene('manga_work')),('Back',manga_home)],icon='megaphone')
    page('manga_young','Keep developing your style','You can practice from age six. Publisher contracts become available from age sixteen.',[('Back',manga_home)],icon='books')
    page('manga_reject','Editorial feedback','The publisher sees promise, but the pitch needs stronger art and storytelling. Improve quality to 35.',[('Practice',scene('manga_work')),('Back',manga_home)],icon='notebook')
    page('manga_accepted','Your series was accepted','Your editor has agreed to serialize '+p('MangaTitle')+'. Assistants reduce deadline pressure but each published chapter includes their pay.',[('Start weekly work',scene('manga_work'))],icon='handshake')
    work_guard=lambda success:check([('(<hero:age> < 6)',scene('manga_young')),(f'({p("MangaWork")} >= 8)',scene('limit'))],success)
    art=F('add',4,F('mul',F('equals',p('Trait35'),3),3),F('mul',F('equals',p('Trait35'),8),3))
    story=F('add',4,F('mul',F('equals',p('Trait35'),2),4))
    page('manga_work','Your weekly schedule','Each practice or chapter uses one session. Strong quality and more readers increase the next chapter’s sales.',
      [('Practice art',work_guard(seq(i('MangaWork'),i('MangaQuality',art),scene('manga_work')))),('Develop the story',work_guard(seq(i('MangaWork'),i('MangaQuality',story),scene('manga_work')))),('Deadline & assistants',scene('manga_deadline')),('Back',manga_home)],icon='notebook',stats={'Sessions_this_age':p('MangaWork'),'Quality':p('MangaQuality'),'Assistants':p('MangaAssistants'),'Published_chapters':p('MangaWeek')})
    page('manga_deadline','Chapter deadline','One assistant costs 500 to hire, plus 200 per published chapter. Up to three assistants help protect quality under pressure.',
      [('Hire an assistant — 500',check([(f'({p("MangaAssistants")} >= 3)',scene('manga_assistants_full'))],cost(500,seq(i('MangaAssistants'),scene('manga_deadline'))))),('Prepare the next chapter',check([(f'({p("MangaActive")} != 1)',scene('manga_pitch')),(f'({p("MangaWork")} >= 8)',scene('limit'))],seq(roll(),scene('manga_publish')))),('Archive the active series',seq(m('MangaActive',0),scene('manga_record'))),('Back',scene('manga_work'))],icon='calendar')
    page('manga_assistants_full','Your studio is staffed','You already employ three assistants.',[('Back',scene('manga_deadline'))],icon='handshake')
    chapter_sales=F('clamp',F('add',F('mul',F('add',p('MangaQuality'),G('careers_v18','Roll')),250),F('mul',p('MangaFans'),2)),1000,2000000)
    publish=seq(i('MangaWork'),i('MangaWeek'),m('ChapterSales',chapter_sales),i('MangaSales',p('ChapterSales')),i('MangaFans',F('div',p('ChapterSales'),25)),i('MangaRoyalty',F('div',p('ChapterSales'),10)),i('MangaReputation',2),scene('manga_chapter'))
    prop35('ChapterSales',0,2000000)
    # Finance filter is evaluated on the exact assistant fee, then one payment.
    wages=F('mul',p('MangaAssistants'),200)
    fee={'cases':[{'if':{'filter':f'[finance.bankBalance<{wages}]'},'then':{'route_options':[{'route_to':scene('funds')}]}}],
      'else_when_no_matches':{'route_options':[{'route_to':seq('BP_BANK_BALANCE='+F('mul',wages,-1),publish)}]}}
    page('manga_publish','Submit this chapter','Commit the chapter now, or return to preparation. Rushed work loses quality; assistants help protect it.',
      [('Publish on time',check([(f'({p("MangaActive")} != 1)',scene('manga_pitch')),(f'({p("MangaWork")} >= 8)',scene('limit'))],fee)),('Request an extension',seq(i('MangaReputation',-2),scene('manga_work'))),('Back',scene('manga_work'))],icon='notebook')
    page('manga_chapter','A new chapter is out','Readers are responding to '+p('MangaTitle')+'. Your catalogue keeps earning after the series ends.',[('Continue',manga_home)],icon='books',stats={'Chapter_copies':p('ChapterSales'),'Lifetime_copies':p('MangaSales'),'Readers':p('MangaFans'),'Annual_royalties':p('MangaRoyalty')})
    page('manga_record','Manga catalogue','Collect once per age. Two million lifetime copies unlock a double-platinum anime adaptation.',
      [('Collect manga and anime royalties',check([(f'({p("MangaRoyalty")} < 1)',scene('none')),(f'({p("MangaPaidAge")} >= <hero:age>)',scene('paid'))],seq(m('MangaPaidAge','<hero:age>'),'BP_BANK_BALANCE='+p('MangaRoyalty'),scene('income')))),('Anime adaptation',scene('anime')),('Back',manga_home)],icon='money-bag',stats={'Chapters':p('MangaWeek'),'Copies':p('MangaSales'),'Anime_series':p('AnimeSeries'),'Annual_royalties':p('MangaRoyalty')})
    page('anime','Anime adaptation','Two million manga copies are required. Choose a studio and a voice cast, then produce a twelve-episode adaptation.',
      [('Choose animation studio',require(f'({p("MangaSales")} < 2000000)','anime_locked',scene('anime_studio'))),('Choose voice cast',scene('anime_cast')),('Produce the next episode',adult(check([(f'({p("AnimeStudio")} == 0)',scene('anime_studio')),(f'({p("AnimeCast")} == 0)',scene('anime_cast')),(f'({p("AnimeEpisodes")} >= 12)',scene('anime_complete')),(f'({p("MangaWork")} >= 8)',scene('limit'))],cost(15000,seq(i('MangaWork'),i('AnimeEpisodes'),m('AnimeActive',1),i('AnimeQuality',F('add',5,F('mul',F('equals',p('Trait35'),10),3))),i('MangaRoyalty',8000),scene('anime_episode')))))),('Back',manga_home)],icon='film-frames',stats={'Studio':p('AnimeStudioName'),'Episodes':p('AnimeEpisodes'),'Production_quality':p('AnimeQuality')})
    page('anime_locked','Build your audience first','The adaptation offer unlocks at two million lifetime manga copies.',[('Back',manga_home)],icon='books')
    page('anime_studio','Select a studio','A studio agreement funds the adaptation and cannot be bought twice for the same series.',
      [(name,adult(check([(f'({p("MangaSales")} < 2000000)',scene('anime_locked')),(f'({p("AnimeStudio")} != 0)',scene('anime'))],cost(price,seq(m('AnimeStudio',n),t('AnimeStudioName',name),m('AnimeQuality',quality),scene('anime'))))))for n,(name,price,quality)in enumerate([('Paper Moon',75000,30),('Aurora Animation',150000,45),('Orbit Pictures',250000,60)],1)]+[('Back',scene('anime'))],icon='film-frames')
    page('anime_cast','Voice cast','Cast new talent, experienced performers or established stars. Casting can be upgraded by paying the new fee.',
      [(name,adult(cost(price,seq(m('AnimeCast',n),i('AnimeQuality',boost),scene('anime')))))for n,(name,price,boost)in enumerate([('New talent',5000,3),('Experienced cast',15000,7),('Established stars',35000,12)],1)]+[('Back',scene('anime'))],icon='mic')
    page('anime_episode','An episode is finished','The episode joins your catalogue and increases recurring royalties.',[('Continue',scene('anime'))],icon='film-frames')
    page('anime_complete','Season complete','Your twelve-episode adaptation is finished. Its royalties remain in your catalogue.',[('Register this completed series',require(f'({p("AnimeActive")} != 1)','anime',seq(m('AnimeActive',0),i('AnimeSeries'),scene('manga_record')))),('Back',manga_home)],icon='trophy')

    # TV: contracts, episode budgets, morale, ratings and renewals.
    for k,v,hi in [('TVActive',0,1),('TVNetwork',0,3),('TVFormat',0,2),('TVSeason',1,1000),('TVEpisode',0,6),('TVQuality',35,100),('TVMorale',60,100),('TVRating',50,100),('TVRoyalty',0,20000000),('TVCompleted',0,1000000),('TVCanceled',0,1)]:prop35(k,v,hi)
    prop35('TVWork',0,8,reset=True);string35('TVTitle','Harbour Lights');string35('TVNetworkName','No network contract')
    page('tv','TV & Series Director','Produce six episodes per season. Networks consider ratings when renewing. Eight production or rehearsal sessions are available per age.',
      [('Pitch a series',scene('tv_pitch')),('Cast, rehearsal & drama',scene('tv_cast')),('Film the next episode',scene('tv_episode_plan')),('Network review & royalties',scene('tv_review'))],icon='film-frames',stats={'Series':p('TVTitle'),'Network':p('TVNetworkName'),'Season':p('TVSeason'),'Episode':p('TVEpisode'),'Ratings':p('TVRating')})
    page('tv_pitch','Your series format','Choose a drama, a miniseries or an original anime. A current series keeps its contract until review.',
      [(name,adult(require(f'({p("TVActive")} == 1)','tv',seq(m('TVFormat',n),t('TVTitle',title),scene('tv_network')))))for n,(name,title)in enumerate([('Drama series','Harbour Lights'),('Miniseries','The Quiet Signal'),('Original anime','Skybound')])]+[('Back',scene('tv'))],icon='light-bulb')
    page('tv_network','Network negotiation','Choose a contract. Better-funded networks demand stronger ratings at renewal.',
      [(name,adult(require(f'({p("TVActive")} == 1)','tv',cost(price,seq(m('TVNetwork',n),t('TVNetworkName',name),m('TVActive',1),m('TVCanceled',0),m('TVEpisode',0),m('TVSeason',1),m('TVQuality',quality),scene('tv'))))))for n,(name,price,quality)in enumerate([('Local broadcaster',10000,35),('National network',35000,45),('StreamWorld',75000,55)],1)]+[('Back',scene('tv'))],icon='clapboard')
    tv_guard=lambda success:adult(check([(f'({p("TVActive")} != 1)',scene('tv_pitch')),(f'({p("TVWork")} >= 8)',scene('limit'))],success))
    page('tv_cast','Cast & production','Rehearsals improve quality. Listening to cast concerns restores morale and protects ratings.',
      [('Rehearse — 1,000',tv_guard(cost(1000,seq(i('TVWork'),i('TVQuality',7),scene('tv_cast'))))),('Resolve cast tension',tv_guard(seq(i('TVWork'),i('TVMorale',F('add',8,F('mul',F('equals',p('Trait35'),11),5))),scene('tv_cast')))),('Pressure the cast',tv_guard(seq(i('TVWork'),i('TVQuality',4),i('TVMorale',-12),scene('tv_cast')))),('Back',scene('tv'))],icon='handshake',stats={'Quality':p('TVQuality'),'Cast_morale':p('TVMorale'),'Sessions':p('TVWork')})
    page('tv_episode_plan','Episode production','Choose the production budget. Each episode pays an immediate licensing fee, then joins your recurring royalty catalogue.',
      [(label,tv_guard(check([(f'({p("TVEpisode")} >= 6)',scene('tv_review'))],cost(price,seq(i('TVWork'),i('TVEpisode'),roll(),m('TVRating',F('clamp',F('add',F('div',p('TVQuality'),2),F('div',p('TVMorale'),3),F('div',G('careers_v18','Roll'),5),boost),0,100)),i('TVMorale',-5),i('TVRoyalty',F('mul',p('TVRating'),100)),f'BP_BANK_BALANCE={pay}',scene('tv_episode'))))))for label,price,boost,pay in [('Lean shoot — 2,000',2000,0,3500),('Balanced shoot — 6,000',6000,5,9000),('Premium shoot — 15,000',15000,10,22000)]]+[('Back',scene('tv'))],icon='clapboard')
    page('tv_episode','Episode broadcast','The audience has seen your latest episode. Ratings reflect production quality, cast morale and audience response.',[('Continue',scene('tv'))],icon='chart-bar',stats={'Episode':p('TVEpisode'),'Ratings':p('TVRating'),'Morale':p('TVMorale'),'Annual_royalty':p('TVRoyalty')})
    renewed=seq(i('TVCompleted'),i('TVSeason'),m('TVEpisode',0),i('TVMorale',10),scene('tv_renewed'))
    page('tv_review','Network review','Review a finished season. A miniseries ends after one season. Other series need ratings of 40, 50 or 60 for local, national or streaming renewal.',
      [('Review the season',check([(f'({p("TVActive")} != 1)',scene('tv_pitch')),(f'({p("TVEpisode")} < 6)',scene('tv_unfinished')),(f'({p("TVFormat")} == 1)',seq(i('TVCompleted'),m('TVActive',0),scene('tv_finished'))),(f'({p("TVRating")} < {F("add",30,F("mul",p("TVNetwork"),10))})',seq(i('TVCompleted'),m('TVActive',0),m('TVCanceled',1),scene('tv_canceled')))],renewed)),('Collect catalogue royalties',check([(f'({p("TVRoyalty")} < 1)',scene('none')),(f'({p("TVPaidAge")} >= <hero:age>)',scene('paid'))],seq(m('TVPaidAge','<hero:age>'),'BP_BANK_BALANCE='+p('TVRoyalty'),scene('income')))),('Back',scene('tv'))],icon='money-bag')
    for k,title,body in [('tv_unfinished','Finish the season','Film all six episodes before requesting renewal.'),('tv_renewed','Renewed for another season','The network has renewed your contract. A fresh six-episode season is ready.'),('tv_finished','Miniseries complete','Your story has reached its planned ending. The catalogue continues earning royalties.'),('tv_canceled','The network canceled your series','Ratings missed the network’s target. Your completed episodes still earn catalogue royalties; you can pitch a new series.')]:page(k,title,body,[('Continue',scene('tv'))],icon='film-frames')

    # Agriculture: native country baseline, local seasons, equipment and losses.
    for k,v,hi in [('FarmLand',0,1),('FarmClimate',0,3),('FarmHemisphere',0,1),('FarmRegionOverride',0,1),('FarmSeason',0,3),('FarmPlanted',0,2),('FarmCropStage',0,3),('FarmMachines',0,3),('FarmIrrigation',0,1),('FarmInsurance',0,1),('FarmWeather',50,99),('FarmRisk',0,100),('FarmHarvests',0,1000000),('FarmLosses',0,1000000),('FarmYield',0,2000000),('FarmDebt',0,2000000),('FarmBankrupt',0,1)]:prop35(k,v,hi)
    prop35('FarmTurns',0,4,reset=True);prop35('FarmPlantAge',-1,999,-1);string35('FarmCountry','No land');string35('FarmClimateName','Temperate');string35('FarmSeasonName','Local spring');string35('FarmReport','No crops planted yet.')
    farm=scene('farm')
    page('farm','Farming & Agriculture','Your farm keeps its own country and climate when you move. Climate, planting season, growing time and protection affect harvests. Four season advances are available per age.',
      [('Land, region & machinery',scene('farm_setup')),('Plant crops',scene('farm_plant')),('Advance season / harvest',scene('farm_calendar')),('Farm ledger',scene('farm_ledger'))],icon='seedling',stats={'Country':p('FarmCountry'),'Climate':p('FarmClimateName'),'Season':p('FarmSeasonName'),'Crop_stage':p('FarmCropStage'),'Debt':p('FarmDebt')})
    page('farm_setup','Land & equipment','The initial climate follows your game country. Choose a regional override for a farm in a different climate. Machinery and irrigation reduce loss risk.',
      [('Buy farmland — 50,000',adult(require(f'({p("FarmLand")} == 1)','farm',cost(50000,seq(m('FarmLand',1),m('FarmBankrupt',0),t('FarmCountry',G('world20','Country')),farm))))),('Choose farm region',scene('farm_region')),('Upgrade machinery — 8,000',adult(check([(f'({p("FarmLand")} != 1)',scene('farm_setup')),(f'({p("FarmMachines")} >= 3)',scene('farm_equipped'))],cost(8000,seq(i('FarmMachines'),farm))))),('Water & insurance',scene('farm_water'))],icon='seedling')
    page('farm_equipped','Fully equipped','Your farm already has a tractor, harvester and logistics truck.',[('Back',farm)],icon='tractor')
    page('farm_region','Regional climate','Choose the climate of this farm’s region. Local spring and autumn follow the selected hemisphere rather than a universal calendar.',
      [(name,seq(m('FarmClimate',n),m('FarmRegionOverride',1),t('FarmClimateName',name),scene('farm_hemisphere')))for n,name in enumerate(['Temperate','Tropical','Dry','Cold'])],icon='earth')
    page('farm_hemisphere','Farm hemisphere','Choose the hemisphere for local growing seasons.',[('Northern hemisphere',seq(m('FarmHemisphere',0),farm)),('Southern hemisphere',seq(m('FarmHemisphere',1),farm)),('Back',farm)],icon='earth')
    page('farm_water','Protect the harvest','Irrigation costs 5,000 once. Crop insurance costs 1,000 per crop and halves failed-harvest debt.',
      [('Install irrigation — 5,000',adult(check([(f'({p("FarmLand")} != 1)',scene('farm_setup')),(f'({p("FarmIrrigation")} == 1)',farm)],cost(5000,seq(m('FarmIrrigation',1),farm))))),('Insure this crop — 1,000',adult(check([(f'({p("FarmPlanted")} == 0)',scene('farm_plant')),(f'({p("FarmInsurance")} == 1)',farm)],cost(1000,seq(m('FarmInsurance',1),farm))))),('Back',farm)],icon='shield')
    suitable=F('add',F('mul',F('equals',p('FarmSeason'),0),1),F('mul',F('equals',p('FarmClimate'),1),1))
    plant=lambda crop:adult(check([(f'({p("FarmLand")} != 1)',scene('farm_setup')),(f'({p("FarmPlanted")} != 0)',scene('farm_busy'))],cost(2000 if crop==1 else 3000,seq(m('FarmPlanted',crop),m('FarmPlantAge','<hero:age>'),m('FarmCropStage',0),m('FarmInsurance',0),m('FarmRisk',F('clamp',F('sub',45 if crop==1 else 55,F('mul',suitable,25),F('mul',p('FarmMachines'),4),F('mul',p('FarmIrrigation'),10)),5,70)),roll(),m('FarmWeather',G('careers_v18','Roll')),t('FarmReport','Seeds are in the ground. Advance two local seasons before harvesting.'),farm))))
    page('farm_plant','Choose a crop','Corn costs 2,000; soy costs 3,000 and has greater weather sensitivity. Temperate, dry and cold farms favor local spring planting. Tropical farms have a wider window. A crop needs two season advances.',[('Plant corn',plant(1)),('Plant soy',plant(2)),('Back',farm)],icon='seedling')
    page('farm_busy','A crop is already growing','Harvest or abandon the current crop before planting again.',[('Back',farm)],icon='seedling')
    seasons=['Local spring','Local summer','Local autumn','Local winter']
    advances=check([(f'({p("FarmTurns")} >= 4)',scene('limit'))]+[(f'({p("FarmSeason")} == {n})',seq(i('FarmTurns'),m('FarmSeason',(n+1)%4),i('FarmCropStage'),roll(),m('FarmWeather',G('careers_v18','Roll')),scene('farm_weather')))for n in range(4)],farm)
    for n,name in enumerate(seasons):page('farm_season'+str(n),name,p('FarmReport'),[('Continue',farm)],icon='seedling')
    weather_risk=F('clamp',F('add',p('FarmRisk'),F('mul',F('equals',p('FarmClimate'),2),12),F('mul',F('equals',p('FarmSeason'),3),F('add',12,F('mul',F('equals',p('FarmClimate'),3),18)))),0,95)
    page('farm_weather','Seasonal forecast','Dry climates increase drought pressure. Local winter brings greater frost risk, especially in cold regions.',
      [('Continue',check([(f'({p("FarmSeason")} == {n})',seq(t('FarmSeasonName',name),t('FarmReport','Forecast updated. Check your crop stage and harvest risk.'),scene('farm_season'+str(n))))for n,name in enumerate(seasons)],farm))],icon='earth',stats={'Weather_roll':p('FarmWeather'),'Loss_risk_percent':weather_risk,'Crop_stage':p('FarmCropStage')})
    yield_value=F('add',9000,F('mul',p('FarmMachines'),3000),F('mul',F('equals',p('Trait35'),7),3000),F('mul',F('equals',p('FarmPlanted'),2),4000))
    success=seq(m('FarmYield',yield_value),'BP_BANK_BALANCE='+p('FarmYield'),i('FarmHarvests'),m('FarmPlanted',0),m('FarmCropStage',0),m('FarmInsurance',0),t('FarmReport','Your crop reached market. Machinery and suitable growing conditions supported the harvest.'),scene('farm_result'))
    failure=seq(i('FarmLosses'),i('FarmDebt',F('div',12000,F('add',1,p('FarmInsurance')))),m('FarmYield',0),m('FarmPlanted',0),m('FarmCropStage',0),m('FarmInsurance',0),t('FarmReport','Drought or frost damaged the harvest. Recovery costs were added to the farm ledger.'),scene('farm_debt'))
    risk=F('sub',weather_risk,F('mul',F('equals',p('Trait35'),9),F('mul',p('FarmMachines'),3)))
    bankrupt_failure=seq(failure.rsplit('>>',1)[0],m('FarmBankrupt',1),m('FarmLand',0),m('FarmMachines',0),m('FarmIrrigation',0),m('FarmDebt',0),t('FarmReport','Your farm became insolvent. Creditors took its land and equipment; you may rebuild later.'),scene('farm_bankruptcy'))
    page('farm_calendar','Growing calendar','Advance local seasons, then harvest. A crop left across an age-up loses its deadline and incurs recovery costs.',
      [('Advance one local season',adult(advances)),('Harvest now',adult(check([(f'({p("FarmPlanted")} == 0)',scene('farm_plant')),(f'(({p("FarmPlantAge")} < <hero:age>) && ({F("add",p("FarmDebt"),F("div",12000,F("add",1,p("FarmInsurance"))))} >= 30000))',bankrupt_failure),(f'({p("FarmPlantAge")} < <hero:age>)',failure),(f'({p("FarmCropStage")} < 2)',scene('farm_early')),(f'(({p("FarmWeather")} < {risk}) && ({F("add",p("FarmDebt"),F("div",12000,F("add",1,p("FarmInsurance"))))} >= 30000))',bankrupt_failure),(f'({p("FarmWeather")} < {risk})',failure)],success))),('Abandon the crop',seq(m('FarmPlanted',0),m('FarmCropStage',0),m('FarmInsurance',0),t('FarmReport','You cleared the field and lost the seed investment.'),farm)),('Back',farm)],icon='calendar')
    page('farm_early','The crop is still growing','Advance two local seasons from planting before harvesting.',[('Back',farm)],icon='seedling')
    page('farm_result','Harvest report',p('FarmReport'),[('Continue',farm)],icon='money-bag',stats={'Sale_income':p('FarmYield'),'Harvests':p('FarmHarvests'),'Failed_crops':p('FarmLosses')})
    page('farm_debt','Recovery costs',p('FarmReport'),[('Continue',check([(f'({p("FarmDebt")} >= 30000)',seq(m('FarmBankrupt',1),m('FarmLand',0),m('FarmMachines',0),m('FarmIrrigation',0),m('FarmDebt',0),t('FarmReport','Your farm became insolvent. Creditors took its land and equipment; you may rebuild later.'),scene('farm_bankruptcy')))],farm))],icon='money-bag',stats={'Debt':p('FarmDebt'),'Losses':p('FarmLosses')})
    page('farm_bankruptcy','Farm bankruptcy','Your farm’s recovery debt reached 30,000. The land and equipment were repossessed. Your other game assets remain subject to their own systems.',[('Continue',farm)],icon='money-bag')
    page('farm_ledger','Farm ledger','Settle the full recovery debt to protect your land. Sales and equipment purchases use your game bank balance.',
      [('Settle recovery debt',check([(f'({p("FarmDebt")} < 1)',farm)],{'cases':[{'if':{'filter':f'[finance.bankBalance<{p("FarmDebt")}]'},'then':{'route_options':[{'route_to':scene('funds')}]}}],'else_when_no_matches':{'route_options':[{'route_to':seq('BP_BANK_BALANCE='+F('mul',p('FarmDebt'),-1),m('FarmDebt',0),farm)}]}})),('Back',farm)],icon='clipboard',stats={'Country':p('FarmCountry'),'Harvests':p('FarmHarvests'),'Losses':p('FarmLosses'),'Debt':p('FarmDebt')})

    # School/campus: social support, appearance-influenced encounters, elections.
    for k,v,hi in [('SchoolSupport',20,100),('SchoolReputation',30,100),('SchoolStress',10,100),('SchoolIncidents',0,1000000),('SchoolWarnings',0,100),('SchoolEnrolled35',0,1),('CampusCampaign',0,1),('CampusVotes',15,100),('CampusPresident',0,1),('CampusProjects',0,1000000),('CampusBudget',0,1000000)]:prop35(k,v,hi)
    prop35('SchoolSessions',0,8,reset=True);prop35('CampusElectionAge',-1,999,-1);string35('SchoolReport','Your school story is just beginning.')
    school_guard=lambda success:check([('(<hero:age> < 6) || (<hero:age> > 24)',scene('school_age')),(f'({p("SchoolEnrolled35")} != 1)',scene('school_enroll')),(f'({p("SchoolSessions")} >= 8)',scene('limit'))],success)
    page('school_enroll','Enrollment required','Enroll in a school or university in the main game to take part in campus activities.',[back],icon='school')
    page('school_age','School and campus years','These activities are available from age six through twenty-four. Student-government elections require age fourteen.',[back],icon='school')
    page('school','School Life & Campus Politics','Friends, confidence, personality and appearance shape some peer reactions. Looks alone never determine how people treat you.',
      [('Friends & school life',scene('school_social')),('A hallway encounter',school_guard(seq(sync(),roll(),scene('school_encounter')))),('Student government',seq(m('CampusPresident',F('mul',p('CampusPresident'),F('equals',p('CampusElectionAge'),'<hero:age>'))),scene('campus'))),('School record',scene('school_record'))],icon='school',stats={'Support':p('SchoolSupport'),'Reputation':p('SchoolReputation'),'Stress':p('SchoolStress')})
    page('school_social','Build your circle','Choose how to spend your time at school.',
      [('Welcome someone new',school_guard(seq(i('SchoolSessions'),i('SchoolSupport',F('add',7,F('mul',F('equals',p('Trait35'),4),5))),i('SchoolReputation',3),impact(2),scene('school_social')))),('Study with friends',school_guard(seq(i('SchoolSessions'),I('school_v9','Knowledge',5),i('SchoolSupport',4),scene('school_social')))),('Quiet reflection',school_guard(seq(i('SchoolSessions'),i('SchoolStress',-8),impact(F('add',2,F('mul',F('equals',p('Trait35'),5),3))),scene('school_social')))),('Back',scene('school'))],icon='handshake')
    peer_risk=F('clamp',F('sub',35,F('div',p('SchoolSupport'),4),F('div',p('SchoolReputation'),5),F('div',G('life_v18','Looks'),10)),5,35)
    page('school_encounter','Between classes','Some classmates are laughing near your locker. Read the situation and choose your next move.',
      [('Approach them',school_guard(check([(f'({G("careers_v18","Roll")} < {peer_risk})',seq(i('SchoolSessions'),i('SchoolIncidents'),i('SchoolStress',8),scene('school_bully')))],seq(i('SchoolSessions'),i('SchoolSupport',5),i('SchoolReputation',2),t('SchoolReport','A friendly conversation turned an awkward moment into a new connection.'),scene('school_result'))))),('Join my friends instead',school_guard(seq(i('SchoolSessions'),i('SchoolSupport',4),scene('school_social')))),('Back',scene('school'))],icon='chat-bubble')
    page('school_bully','A classmate starts trouble','A classmate makes a cruel remark. You can stand up for yourself, get support or escalate the conflict.',
      [('Set a firm boundary',seq(i('SchoolReputation',4),i('SchoolStress',-3),t('SchoolReport','You told the classmate to stop and left with your dignity intact.'),scene('school_result'))),('Report it with a friend',seq(i('SchoolSupport',6),i('SchoolStress',-6),t('SchoolReport','You and a friend reported the incident. A staff member arranged support and follow-up.'),scene('school_result'))),('Start a fight',seq(i('SchoolWarnings'),i('SchoolStress',10),i('SchoolReputation',-6),impact(-6),t('SchoolReport','The fight ended with a minor injury and a disciplinary warning. Your friends can help you rebuild trust.'),scene('school_result'))),('Walk away',seq(i('SchoolStress',-2),t('SchoolReport','You left the confrontation and checked in with someone you trust.'),scene('school_result')))],icon='chat-bubble')
    page('school_result','School moment',p('SchoolReport'),[('Continue',scene('school'))],icon='school')
    page('school_record','Your school record',p('SchoolReport'),[('Back',scene('school'))],icon='clipboard',stats={'Friends_and_support':p('SchoolSupport'),'Incidents':p('SchoolIncidents'),'Warnings':p('SchoolWarnings'),'Projects':G('school_v9','Projects')})
    campaign=check([('(<hero:age> < 14) || (<hero:age> > 24)',scene('school_age')),(f'({p("SchoolEnrolled35")} != 1)',scene('school_enroll')),(f'({p("CampusPresident")} == 1)',scene('campus_projects'))],seq(m('CampusCampaign',1),scene('campus_campaign')))
    page('campus','Student Government','Run for student-body president, make speeches and turn support into projects. One election may be held per age.',
      [('Start / continue a campaign',campaign),('Hold the election',check([('(<hero:age> < 14) || (<hero:age> > 24)',scene('school_age')),(f'({p("SchoolEnrolled35")} != 1)',scene('school_enroll')),(f'({p("CampusCampaign")} != 1)',scene('campus_campaign')),(f'({p("CampusElectionAge")} >= <hero:age>)',scene('campus_done'))],seq(roll(),scene('campus_vote')))),('President’s projects',scene('campus_projects')),('Back',scene('school'))],icon='megaphone',stats={'Supporters':p('CampusVotes'),'President':p('CampusPresident'),'Completed_projects':p('CampusProjects')})
    page('campus_campaign','Your campaign','Speeches, realistic promises and listening to students build support. Each uses one school session.',
      [('Give a speech',school_guard(seq(i('SchoolSessions'),i('CampusVotes',F('add',8,F('mul',F('equals',p('Trait35'),12),5))),scene('campus_campaign')))),('Listen to student concerns',school_guard(seq(i('SchoolSessions'),i('CampusVotes',6),i('SchoolSupport',4),scene('campus_campaign')))),('Promise an impossible budget',school_guard(seq(i('SchoolSessions'),i('CampusVotes',4),i('SchoolReputation',-5),scene('campus_campaign')))),('Back',scene('campus'))],icon='megaphone')
    page('campus_vote','Election day','Commit the result. Support and school reputation influence turnout.',
      [('Count the votes',check([(f'({p("CampusElectionAge")} >= <hero:age>)',scene('campus_done')),(f'({G("careers_v18","Roll")} < {F("clamp",F("add",p("CampusVotes"),F("div",p("SchoolReputation"),4)),10,95)})',seq(m('CampusElectionAge','<hero:age>'),m('CampusCampaign',0),m('CampusPresident',1),m('CampusBudget',5000),scene('campus_win')))],seq(m('CampusElectionAge','<hero:age>'),m('CampusCampaign',0),i('SchoolReputation',2),scene('campus_loss')))),('Back',scene('campus'))],icon='ballot-box')
    for k,title,body in [('campus_win','You won the election','Your classmates elected you student-body president. You have a 5,000 campus project budget.'),('campus_loss','Election result','Another candidate won. You gained experience and may campaign again after aging up.'),('campus_done','Election complete','An election has already been held at your current age.')]:page(k,title,body,[('Continue',scene('campus'))],icon='school')
    project=lambda field:school_guard(check([(f'({p("CampusPresident")} != 1)',scene('campus_campaign')),(f'({p("CampusBudget")} < 1000)',scene('campus_empty'))],seq(i('SchoolSessions'),i('CampusBudget',-1000),i('CampusProjects'),i(field,8),I('school_v9','Projects'),t('SchoolReport','You negotiated with school staff and completed a student-led campus project.'),scene('school_result'))))
    page('campus_projects','President’s agenda','Negotiate a project with the principal. Each uses 1,000 of the campus budget, rather than your personal bank balance.',[('Anti-bullying support group',project('SchoolSupport')),('Arts and sports event',project('SchoolReputation')),('Study-space improvements',project('CampusVotes')),('Back',scene('campus'))],icon='school',stats={'Campus_budget':p('CampusBudget'),'Projects':p('CampusProjects')})
    page('campus_empty','Campus budget spent','You have used this term’s project funds. You can still support students through school activities.',[('Back',scene('school'))],icon='money-bag')

    # Extended relatives are persistent story records alongside native parents.
    relatives=[('Grandmother Nora',52,'Your mother’s mother loves sharing family stories.'),('Grandfather Victor',55,'Your father’s father enjoys fixing things and teaching practical skills.'),('Aunt Lena',25,'Your mother’s sister is creative and interested in your ambitions.'),('Uncle Daniel',31,'Your father’s brother likes sport and keeps up with family news.'),('Cousin Alex',3,'Your aunt’s child enjoys including you in family plans.'),('Cousin Sam',-2,'Your uncle’s child shares your curiosity and sense of adventure.')]
    prop35('FamilySessions',0,6,reset=True)
    for n,(_,_,_)in enumerate(relatives):prop35('Relative'+str(n)+'Connection',45,100);string35('Relative'+str(n)+'Memory','No shared activity yet.')
    family_items=[]
    for n,(name,gap,story)in enumerate(relatives):
        age=F('max',0,F('add','<hero:age>',gap));conn=p('Relative'+str(n)+'Connection');memory=p('Relative'+str(n)+'Memory')
        rel=scene('relative'+str(n));family_items.append(item(name,'relative'+str(n),'handshake'))
        usable=lambda target:check([(f'({F("add","<hero:age>",gap)} < 0)',scene('relative_unborn')),(f'({age} > 95)',scene('relative_memorial')),(f'({p("FamilySessions")} >= 6)',scene('limit'))],target)
        visit=F('add',7,F('mul',F('equals',p('Trait35'),6),5))
        page('relative'+str(n),name,story+' '+memory,
          [('Spend time together',usable(seq(i('FamilySessions'),i('Relative'+str(n)+'Connection',visit),t('Relative'+str(n)+'Memory','You spent time together and made a new family memory.'),impact(2),rel))),('Call and ask for advice',usable(seq(i('FamilySessions'),i('Relative'+str(n)+'Connection',4),t('Relative'+str(n)+'Memory','A thoughtful conversation helped you feel connected.'),impact(2),rel))),('Bring a gift — 25',usable(cost(25,seq(i('FamilySessions'),i('Relative'+str(n)+'Connection',10),t('Relative'+str(n)+'Memory','They appreciated the thought behind your gift.'),rel)))),('Back',hub('family'))],icon='handshake',stats={'Age':age,'Connection':conn,'Last_memory':memory})
    page('relative_unborn','This cousin has not been born yet','Their family story becomes available in a later year.',[('Back',hub('family'))],icon='seedling')
    page('relative_memorial','A family memory','This relative’s story has reached its memorial years. Remember the time you shared and keep the family connection alive.',[('Back',hub('family'))],icon='heart-red')
    menu('family35','Extended Family Stories',family_items)

    # Direct fictional dealers: inventory, ownership, consumption and consequences.
    prop35('DealerHeat',0,100);prop35('Dependence',0,100);prop35('ShopSessions',0,6,reset=True);string35('ShopReport','No recent purchase.')
    drugs=[('Cannabis',40,3),('Ecstasy',70,6),('Cocaine',120,10),('Psychedelic mushrooms',60,5)]
    weapons=[('Compact pistol',750),('Heavy revolver',1100),('Hunting rifle',1800),('Pump shotgun',1500),('Tactical carbine',3200),('Stun device',450)]
    for n in range(len(drugs)):prop35('Drug'+str(n),0,25)
    for n in range(len(weapons)):prop35('Weapon'+str(n),0,5)
    shop_guard=lambda success:adult(check([(f'({p("ShopSessions")} >= 6)',scene('limit'))],success))
    menu('drugshop35','Street Dealer',[item(name,'drug'+str(n),'memo',str(price)+' per purchase')for n,(name,price,_)in enumerate(drugs)]+[item('Inventory & recovery','drug_inventory','clipboard')])
    for n,(name,price,severity)in enumerate(drugs):
        stock='Drug'+str(n)
        page('drug'+str(n),name,'A direct fictional purchase. Possession and use build a saved risk record, and use reduces your character’s wellbeing.',
          [('Buy — '+str(price),shop_guard(check([(f'({p(stock)} >= 25)',scene('shop_full'))],cost(price,seq(i('ShopSessions'),i(stock),i('DealerHeat',3),t('ShopReport','You bought '+name+'.'),scene('shop_result')))))),('Use one from inventory',shop_guard(check([(f'({p(stock)} < 1)',scene('shop_empty'))],seq(i('ShopSessions'),i(stock,-1),i('Dependence',severity),i('DealerHeat',2),impact(-severity),t('ShopReport','You used '+name+'. Your wellbeing fell and dependency risk increased.'),scene('drug_consequence'))))),('Back',hub('drugshop'))],icon='memo',stats={'Owned':p(stock),'Dependency_risk':p('Dependence'),'Dealer_attention':p('DealerHeat')})
    page('drug_consequence','Aftereffects',p('ShopReport'),[('Continue',check([(f'({p("Dependence")} >= 60)',seq(impact(-8),t('ShopReport','Repeated use is affecting your wellbeing. You can seek support and work toward recovery.'),scene('drug_inventory')))],scene('shop_result')))],icon='heart-red')
    page('drug_inventory','Inventory & recovery','Taking a break and seeking support reduces the added dependency record. Each support appointment costs 200 and uses a shop session.',
      [('Seek support — 200',shop_guard(cost(200,seq(i('ShopSessions'),i('Dependence',-20),i('DealerHeat',-10),impact(4),t('ShopReport','You sought support and made progress toward recovery.'),scene('shop_result'))))),('Discard the inventory',seq(*[m('Drug'+str(n),0)for n in range(4)],i('DealerHeat',-5),t('ShopReport','You discarded the remaining substances.'),scene('shop_result'))),('Back',hub('drugshop'))],icon='clipboard',stats={name:p('Drug'+str(n))for n,(name,_,_)in enumerate(drugs)})
    menu('armshop35','Arms Dealer',[item(name,'weapon'+str(n),'memo',str(price)+' • saved ownership')for n,(name,price)in enumerate(weapons)]+[item('Collection record','weapon_record','clipboard')])
    for n,(name,price)in enumerate(weapons):
        k='Weapon'+str(n)
        page('weapon'+str(n),name,'Add this item to your saved collection. Purchases use your game bank balance. This collection does not replace the base game’s weapon-specific combat rules.',
          [('Buy — '+str(price),shop_guard(check([(f'({p(k)} >= 5)',scene('shop_full'))],cost(price,seq(i('ShopSessions'),i(k),i('DealerHeat',4),t('ShopReport','You added a '+name+' to your collection.'),scene('shop_result')))))),('Sell one — '+str(price//2),adult(check([(f'({p(k)} < 1)',scene('shop_empty'))],seq(i(k,-1),f'BP_BANK_BALANCE={price//2}',t('ShopReport','You sold a '+name+'.'),scene('shop_result'))))),('Back',hub('armshop'))],icon='memo',stats={'Owned':p(k),'Dealer_attention':p('DealerHeat')})
    page('weapon_record','Your collection','Ownership persists with this life.',[('Back',hub('armshop'))],icon='clipboard',stats={name:p('Weapon'+str(n))for n,(name,_)in enumerate(weapons)})
    page('shop_result','Dealer activity',p('ShopReport'),[('Street dealer',adult(hub('drugshop'))),('Arms dealer',adult(hub('armshop'))),back],icon='clipboard')
    for k,title,body in [('shop_full','Inventory limit','You already own the maximum number of this item.'),('shop_empty','Nothing in inventory','Buy an item before using or selling it.')]:page(k,title,body,[back],icon='clipboard')

    # Youth football: childhood training, saved scouting and youth matches.
    for k,v,hi in [('SoccerSkill',10,100),('SoccerStamina',20,100),('SoccerAcademy',0,1),('SoccerYouthCaps',0,1000000),('SoccerGoals',0,1000000),('SoccerScouts',0,100),('SoccerSigned',0,1)]:prop35(k,v,hi)
    prop35('SoccerAgreementAge',18,18,16);string35('SoccerYouthLevel','Under-8 development');prop35('SoccerSessions',0,6,reset=True);string35('SoccerReport','Join a local soccer school from age six.')
    soccer_guard=lambda success:check([('(<hero:age> < 6)',scene('soccer_young')),(f'({p("SoccerSessions")} >= 6)',scene('limit'))],success)
    page('soccer_young','Youth soccer','Local soccer school starts at age six. Academy scouting becomes available from age eight.',[back],icon='soccer-ball')
    page('soccer','Youth Soccer Academy','Build technique and fitness as a child, earn an academy place and play youth fixtures. This record accompanies the base game’s professional sports career.',
      [('Local soccer school',soccer_guard(seq(i('SoccerSessions'),i('SoccerSkill',7),i('SoccerStamina',5),M('sports_people_v14','NativeFitnessImpact',1),scene('soccer')))),('Academy scouting',check([('(<hero:age> < 8)',scene('soccer_young')),(f'({p("SoccerSkill")} < 25)',scene('soccer_develop')),(f'({p("SoccerAcademy")} == 1)',scene('soccer_academy'))],scene('soccer_offer'))),('Youth fixtures & scouts',scene('soccer_academy')),('Career record',scene('soccer_record'))],icon='soccer-ball',stats={'Age_group':p('SoccerYouthLevel'),'Technique':p('SoccerSkill'),'Stamina':p('SoccerStamina'),'Academy':p('SoccerAcademy'),'Youth_caps':p('SoccerYouthCaps')})
    page('soccer_develop','Keep developing','An academy scout wants to see technique of at least 25. Continue attending your local school.',[('Continue',scene('soccer'))],icon='soccer-ball')
    page('soccer_offer','An academy wants you','A professional youth academy has offered you a place after watching your development.',[('Accept and continue',check([('(<hero:age> < 8)',scene('soccer_young')),(f'({p("SoccerSkill")} < 25)',scene('soccer_develop'))],seq(m('SoccerAcademy',1),i('SoccerScouts',10),scene('soccer_academy'))))],icon='trophy')
    page('soccer_academy','Academy football','Age bands progress from under-8 development to under-12, under-15 and under-18 football. Scouts consider skill, stamina and performance.',
      [('Play a youth fixture',soccer_guard(check([(f'({p("SoccerAcademy")} != 1)',scene('soccer'))],seq(i('SoccerSessions'),roll(),i('SoccerYouthCaps'),m('SoccerMatchGoals',F('div',F('add',p('SoccerSkill'),G('careers_v18','Roll')),50)),i('SoccerGoals',p('SoccerMatchGoals')),i('SoccerScouts',F('add',1,p('SoccerMatchGoals'))),scene('soccer_match'))))),('Conditioning and teamwork',soccer_guard(seq(i('SoccerSessions'),i('SoccerStamina',8),i('SoccerSkill',3),M('sports_people_v14','NativeFitnessImpact',1),scene('soccer_academy')))),('Academy contract meeting',scene('soccer_contract')),('Back',scene('soccer'))],icon='soccer-ball')
    prop35('SoccerMatchGoals',0,4)
    page('soccer_match','Youth match report','Your fixture has been added to the academy record.',[('Continue',scene('soccer_academy'))],icon='soccer-ball',stats={'Goals_this_match':p('SoccerMatchGoals'),'Youth_caps':p('SoccerYouthCaps'),'Career_youth_goals':p('SoccerGoals'),'Scout_interest':p('SoccerScouts')})
    page('soccer_contract','Academy contract meeting','Your academy can offer a development agreement from age sixteen in Brazil. Other countries use eighteen as this expansion’s gameplay default. Direct promotion into native professional clubs is a separate system.',
      [('Sign development agreement',check([(f'(<hero:age> < {p("SoccerAgreementAge")})',scene('soccer_contract_young')),(f'({p("SoccerSigned")} == 1)',scene('soccer_record')),(f'({p("SoccerScouts")} < 25)',scene('soccer_develop'))],seq(m('SoccerSigned',1),'BP_BANK_BALANCE=10000',t('SoccerReport','Your academy awarded a development agreement and a one-time signing payment.'),scene('soccer_record')))),('Open football competitions','BP_SHOW_LIST=genesis_v9_v12_soccer'),('Back',scene('soccer_academy'))],icon='handshake')
    page('soccer_contract_young','Keep developing','Your current country’s academy age gate has not been reached. Keep training and building scout interest.',[('Back',scene('soccer'))],icon='soccer-ball')
    page('soccer_record','Academy record',p('SoccerReport'),[('Back',scene('soccer'))],icon='clipboard',stats={'Technique':p('SoccerSkill'),'Stamina':p('SoccerStamina'),'Youth_matches':p('SoccerYouthCaps'),'Youth_goals':p('SoccerGoals'),'Agreement':p('SoccerSigned')})

    # International franchises: independent branches and yearly operating income.
    for k,v,hi in [('BusinessBranches',0,15),('BusinessQuality',40,100),('BusinessSupply',60,100),('BusinessIncome',0,20000000),('BusinessCrises',0,1000000)]:prop35(k,v,hi)
    prop35('BusinessActions',0,6,reset=True);string35('BusinessReport','No branch opened yet.')
    branch_items=[]
    for n,country in enumerate(['United States','Brazil','United Kingdom','Japan','Australia']):
        for f,(kind,price,income)in enumerate([('Cafe',25000,8000),('Supermarket',75000,22000),('Fuel station',100000,28000)]):
            key='Branch'+str(n)+'_'+str(f);prop35(key,0,1);k='branch'+str(n)+'_'+str(f);branch_items.append(item(country+' • '+kind,k,'suitcase'))
            page(k,country+' '+kind,'Establish a branch in this market. This is a saved franchise account alongside the base game’s native business system.',
              [('Open branch — '+str(price),adult(check([(f'({p(key)} == 1)',scene('business')),(f'({p("BusinessBranches")} >= 15)',scene('business'))],cost(price,seq(m(key,1),i('BusinessBranches'),i('BusinessIncome',income),t('BusinessReport','You opened a '+kind+' franchise in '+country+'.'),scene('business')))))),('Back',hub('franchises'))],icon='suitcase')
    menu('franchises35','International Franchise Markets',branch_items)
    page('business','Global Franchises','Build branches across five markets. Supply resilience and service quality affect the annual income of this franchise account.',
      [('Open an international branch',adult(hub('franchises'))),('Supply chain & service',scene('business_operations')),('Collect annual income',adult(check([(f'({p("BusinessIncome")} < 1)',scene('none')),(f'({p("BusinessPaidAge")} >= <hero:age>)',scene('paid'))],seq(m('BusinessPaidAge','<hero:age>'),m('BusinessNet',F('div',F('mul',p('BusinessIncome'),F('add',p('BusinessSupply'),p('BusinessQuality'))),200)),'BP_BANK_BALANCE='+p('BusinessNet'),scene('business_paid'))))),back],icon='suitcase',stats={'Branches':p('BusinessBranches'),'Supply_resilience':p('BusinessSupply'),'Service_quality':p('BusinessQuality'),'Gross_annual_income':p('BusinessIncome')})
    prop35('BusinessNet',0,20000000)
    operations=lambda success:adult(check([(f'({p("BusinessActions")} >= 6)',scene('limit')),(f'({p("BusinessBranches")} < 1)',scene('business'))],success))
    page('business_operations','Branch operations','Invest in reliable suppliers, improve service or face a simulated supply crisis. Six operating actions are available per age.',
      [('Diversify suppliers — 2,000',operations(cost(2000,seq(i('BusinessActions'),i('BusinessSupply',10),scene('business_operations'))))),('Staff training — 1,500',operations(cost(1500,seq(i('BusinessActions'),i('BusinessQuality',10),scene('business_operations'))))),('Manage a supply crisis',operations(seq(i('BusinessActions'),roll(),scene('business_crisis')))),('Back',scene('business'))],icon='clipboard')
    page('business_crisis','Supply disruption','An international delivery is delayed. Choose how to protect your customers.',
      [('Pay for alternative freight — 3,000',adult(cost(3000,seq(i('BusinessSupply',8),i('BusinessQuality',3),i('BusinessCrises'),t('BusinessReport','Alternative freight kept your branches supplied.'),scene('business'))))),('Use local suppliers',seq(i('BusinessSupply',5),i('BusinessQuality',-3),i('BusinessCrises'),t('BusinessReport','Local suppliers kept the doors open with a smaller range.'),scene('business'))),('Wait without a backup',seq(i('BusinessSupply',-15),i('BusinessQuality',-10),i('BusinessCrises'),t('BusinessReport','Empty shelves damaged customer confidence.'),scene('business'))),('Back',scene('business'))],icon='suitcase')
    page('business_paid','Franchise statement',p('BusinessReport'),[('Continue',scene('business'))],icon='money-bag',stats={'Payment':p('BusinessNet'),'Branches':p('BusinessBranches'),'Supply_resilience':p('BusinessSupply')})

    # More storm fieldwork plus automatic playback of the existing Unity sequence.
    for k,v,hi in [('StormFootage',0,1000000),('StormRescues',0,1000000),('StormFootageIncome',0,20000000)]:prop35(k,v,hi)
    storm_guard=lambda success:adult(check([(f'({G("careers_v18","Role")} != 1)',S('storm')),(f'({G("careers_v18","Actions")} >= 8)',S('career_limit'))],success))
    page('storm','Storm Fieldwork','Prepare an observation route, coordinate assistance and license your footage. Successful original chase surveys now open their animated report automatically.',
      [('Scout a safe observation route',storm_guard(seq(I('careers_v18','Actions'),I('careers_v18','Forecast',4),I('careers_v18','Safety',5),scene('storm')))),('Coordinate a community rescue',storm_guard(seq(I('careers_v18','Actions'),i('StormRescues'),I('careers_v18','CrewTrust21',4),I('careers_v18','Reputation',3),scene('storm_rescue')))),('Film weather from a safe location',storm_guard(seq(I('careers_v18','Actions'),i('StormFootage'),i('StormFootageIncome',2500),I('careers_v18','Research',10),scene('storm_film')))),('Footage contract & main career',scene('storm_contract'))],icon='v18-storm',stats={'Recorded_surveys':p('StormFootage'),'Assistance_operations':p('StormRescues'),'Annual_licensing_income':p('StormFootageIncome')})
    page('storm_rescue','Community assistance','Your crew coordinated with responders and helped residents reach the designated shelter. The activity strengthened crew trust and your research reputation.',[('Continue',scene('storm'))],icon='handshake')
    page('storm_film','Weather footage recorded','Your camera footage and weather measurements have joined the licensing catalogue.',[('Continue',scene('storm'))],icon='film-frames')
    page('storm_contract','Footage contract','Collect the saved licensing income once per age, or return to the main Storm Chaser career.',
      [('Collect licensing income',storm_guard(check([(f'({p("StormFootageIncome")} < 1)',scene('none')),(f'({p("FootagePaidAge")} >= <hero:age>)',scene('paid'))],seq(m('FootagePaidAge','<hero:age>'),'BP_BANK_BALANCE='+p('StormFootageIncome'),scene('income'))))),('Open main Storm Chaser career',S('storm_hub')),('Replay the latest animated report',storm_guard(require(f'({G("careers_v18","Tours")} < 1)','storm',seq(M('careers_v18','NativeStormReplay21',0),M('careers_v18','NativeStormReplay21',1),S('tornado_storm24'))))),back],icon='v18-storm')

    menu(OWNER,'Community Expansions',[
      tile('Manga & Anime',seq(sync(),manga_home),'notebook','Publish chapters; studios; voice cast and royalties'),
      tile('TV & Series Director',scene('tv'),'film-frames','Networks; cast morale; ratings and renewals'),
      tile('Farming & Agriculture',seq(sync(),farm),'seedling','Country climates; local seasons; equipment and crop losses'),
      tile('School & Campus Politics',seq(sync(),scene('school')),'school','Friendships; bullying; elections and student projects'),
      child('Extended Family Stories','family35','handshake','Grandparents; aunt; uncle and cousins'),
      tile('Street Dealer',adult(hub('drugshop')),'memo','Direct fictional inventory and consequences'),
      tile('Arms Dealer',adult(hub('armshop')),'memo','Buy; collect and sell six weapon categories'),
      tile('Youth Soccer Academy',seq(sync(),scene('soccer')),'soccer-ball','Soccer school from six; academy from eight'),
      tile('Global Franchises',scene('business'),'suitcase','Branches in five international markets'),
      tile('Storm Fieldwork',scene('storm'),'v18-storm','Routes; assistance; footage and licensing'),
      child('Additional Personality Traits','traits35','face-thinking','Twelve original archetypes with gameplay effects')],entry='T2',icon='light-bulb',sub='Careers; school; family; farms and fictional shops')
    new_rows=d.rows
    assert not any(F('equals','a','b')in str(r)for r in new_rows)
    # Preserve the existing scenarios and IDs. Append new scenarios in one file.
    old=list(csv.DictReader(io.StringIO(base[d.FILE])));ids={r['ScenarioID']for r in old}
    assert not ids.intersection(r['ScenarioID']for r in new_rows)
    for row in old:
        if row['ScenarioID']==S('chase_plan'):
            for n in range(1,5):
                field=f'Choice{n}_AdvancedLogic'
                if row[field]:
                    data=json.loads(row[field])
                    for case in data['cases']:
                        route=case['then']['route_options'][0]['route_to']
                        if 'careers_v18:Tours:+1' in route:
                            case['then']['route_options'][0]['route_to']=route.replace(S('chase_report'),seq(M('careers_v18','NativeStormReplay21',0),M('careers_v18','NativeStormReplay21',1),S('tornado_storm24')))
                    row[field]=json.dumps(data,separators=(',',':'))
    d.assets[d.FILE]=d.writecsv(old+new_rows,d.HEADER)
    d.assets['genesis_v18_defaults_'+OWNER]=d.writecsv(list(d.schemas[OWNER].values()))
    registry=base['genesis_feature_containers'].splitlines();idx=next(n for n,s in enumerate(registry)if s.startswith('ContainerId,'))
    records=list(csv.reader(io.StringIO('\n'.join(registry[idx:]))));assert not any(r[0]==OWNER for r in records)
    records+=d.registry;stream=io.StringIO(newline='');csv.writer(stream,lineterminator='\r\n').writerows(records)
    d.assets['genesis_feature_containers']='\r\n'.join(registry[:idx])+'\r\n'+stream.getvalue()
    for name,extra in [('genesis_v9_school_v9',child('School & Campus Politics',OWNER,'school')),('genesis_v18_life_v18',child('Additional Personality Traits','traits35','face-thinking')),('genesis_v18_storm_career19',tile('Fieldwork & Footage',scene('storm'),'v18-storm'))]:
        value=json.loads(base[name]);extra['TileID']='community35_'+name;value['Items'].append(extra);d.assets[name]=json.dumps(value,indent=2)
    # The school shortcut should open its section rather than the whole hub.
    school=json.loads(d.assets['genesis_v9_school_v9']);school['Items'][-1]=tile('School & Campus Politics',seq(sync(),scene('school')),'school');school['Items'][-1]['TileID']='community35_school';d.assets['genesis_v9_school_v9']=json.dumps(school,indent=2)
    all_assets={**base,**d.assets};(ROOT/'assets.json').write_text(json.dumps(all_assets,indent=2)+'\n')
    (ROOT/'community35_schemas.json').write_text(json.dumps(d.schemas,indent=2)+'\n')
    report={'new_scenarios':len(new_rows),'new_assets':[n for n in d.assets if n not in base],'modified_assets':[n for n in d.assets if n in base],'trait_count':len(traits),'relative_count':len(relatives),'drug_count':len(drugs),'weapon_count':len(weapons),'franchise_markets':5,'old_scenario_IDs_retained':True}
    (ROOT/'community35_authoring.json').write_text(json.dumps(report,indent=2)+'\n');return all_assets,report

def build(base,out):
    assets,report=author();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(base)as z:env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'));data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'))
    key=lambda o:(o.assets_file.name,o.path_id);sha=lambda b:hashlib.sha256(b).hexdigest()
    snapshots={key(o):sha(o.get_raw_data())for o in env.objects};snapshot_data={key(o):sha(o.get_raw_data())for o in data.objects}
    texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'}
    rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree();paths=copy.deepcopy(tree['m_Container']);deps=copy.deepcopy(tree['m_DependentAssets'])
    resource_id=next(n+1 for n,e in enumerate(rm.assets_file.externals)if e.path=='resources.assets')
    file=texts[d.FILE].assets_file;next_id=max(file.objects)+1;changed=set();added={}
    baseline=json.loads((ROOT.parent/'native_v34/assets.json').read_text())
    for name,value in assets.items():
        if name in baseline and value==baseline[name]:continue
        if name in texts:obj=texts[name];changed.add(key(obj))
        else:
            obj=copy.copy(texts['genesis_test_feature_events']);obj.path_id=next_id;next_id+=1;obj.data=texts['genesis_test_feature_events'].get_raw_data();file.objects[obj.path_id]=obj;added[name]=obj.path_id
            path=('genesis_lists/'if value.startswith('{')else'genesis/')+name;assert path not in dict(tree['m_Container']);tree['m_Container'].append((path,dict(m_FileID=resource_id,m_PathID=obj.path_id)))
        asset=obj.read();asset.m_Name=name;asset.m_Script=value;asset.save()
    tree['m_Container'].sort(key=lambda x:x[0]);rm.save_typetree(tree)
    bundle=next(iter(env.files.values())).save(packer='original');data_bytes=next(iter(data.files.values())).save(packer='original')
    (out/'datapack.unity3d').write_bytes(bundle);(out/'data.unity3d').write_bytes(data_bytes)
    check_env=UnityPy.load(bundle);check_data=UnityPy.load(data_bytes);after={key(o):sha(o.get_raw_data())for o in check_env.objects};after_data={key(o):sha(o.get_raw_data())for o in check_data.objects}
    assert set(snapshots)<=set(after) and len(after)==len(snapshots)+len(added)
    assert {k for k in snapshots if snapshots[k]!=after[k]}==changed
    assert set(after_data)==set(snapshot_data) and {k for k in snapshot_data if snapshot_data[k]!=after_data[k]}=={key(rm)}
    reread=next(o for o in check_data.objects if o.type.name=='ResourceManager').read_typetree();new_paths=dict(reread['m_Container']);assert Counter((k,json.dumps(v,sort_keys=True))for k,v in paths)<=Counter((k,json.dumps(v,sort_keys=True))for k,v in reread['m_Container']);assert reread['m_DependentAssets']==deps
    for name,pathid in added.items():assert new_paths[('genesis_lists/'if assets[name].startswith('{')else'genesis/')+name]==dict(m_FileID=resource_id,m_PathID=pathid)
    text_values={o.read().m_Name:o.read().m_Script for o in check_env.objects if o.type.name=='TextAsset'}
    assert all(text_values[n]==v for n,v in assets.items())
    report.update(passed=True,datapack_sha256=sha(bundle),data_sha256=sha(data_bytes),added_TextAssets=added,preserved_Unity_objects=len(snapshots)-len(changed)+len(snapshot_data)-1,
      all_other_objects_byte_identical=True,original_resource_paths_preserved=True,original_scenarios_preserved=True,new_scenarios_in_shipped_genesis_schema=True)
    (ROOT/'content35_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

if __name__=='__main__':build(*sys.argv[1:])
