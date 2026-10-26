"""Keep stock news frequency while replacing impossible technology stories."""
from native_hooks import h


def hooks(b):
    thresholds=[('airliner',1914),('jet ',1952),('helicopter',1939),('atomic bomb',1945),('nuclear power',1954),('space station',1971),('space shuttle',1981),('smartphone',2007),('iphone',2007),('internet',1991),('email',1991),('social media',2004),('Facebook',2004),('Twitter',2006),('TikTok',2018),('YouTube',2005),('OnlyFans',2016),('robotaxi',2020)]
    s='cbz x0,finish\nldr x27,[x0,#0x18]\ncbz x27,finish\n'+f'bl {b.old["v45_current_year"]["stub"]:#x}\nmov w26,w0\n'
    for i,(word,year)in enumerate(thresholds):
        s+=f'cmp w26,#{year}\nb.ge news1106_next_{i}\n'+b.string(word)+'mov x1,x0\nmov x0,x27\nmov x2,xzr\nbl 0x4e04a8c\ncbnz w0,news1106_replace\n'+f'news1106_next_{i}:\n'
    s+='b finish\nnews1106_replace:\nmov w0,#0\nmov w1,#4\nmov x2,xzr\nbl 0x2e0b54c\nmov w25,w0\n'
    stories=[(1914,['Newspapers report improvements to a regional railway. Travellers hope the new service will shorten journeys.','A town debates installing electric street lighting. Shopkeepers welcome the idea, while residents question the cost.','A new workshop opens and advertises for apprentices. Families discuss whether the work offers a secure future.','A severe storm interrupts telegraph traffic. Repair crews work to restore messages between towns.']),
             (1946,['Newspapers report shortages of fuel and raw materials. Families adapt their spending and repair what they already own.','Rail workers restore a damaged line. Local businesses hope deliveries will begin moving again.','A public health campaign encourages clean water and basic sanitation. Volunteers distribute advice in busy streets.','A local newspaper prints letters from families separated by events overseas. Relief groups help them keep in touch.']),
             (1991,['A new radio programme becomes a popular topic of conversation. Listeners debate its hosts and music.','A factory announces new machinery. Workers welcome safer equipment but worry about changes to their jobs.','A television report covers a dispute over housing. Families attend a public meeting to question the plans.','A severe storm interrupts telephone service. Engineers work through the night to reconnect homes.']),
             (9999,['A public transport project opens after delays. Commuters compare the new service with their old route.','A local science fair draws a crowd. Students explain their projects and answer questions from visitors.','A neighbourhood relief group asks for volunteers. Residents bring food and help organise deliveries.','A newspaper investigation leads to questions at a public meeting. Officials promise to release more information.'])]
    for e,(until,choices)in enumerate(stories):
        s+=f'cmp w26,#{until}\nb.ge news1106_era_next_{e}\n'
        for i,story in enumerate(choices):s+=f'cmp w25,#{i}\nb.ne news1106_story_next_{e}_{i}\n'+b.string(story)+f'str x0,[sp]\nb return_custom\nnews1106_story_next_{e}_{i}:\n'
        s+=f'news1106_era_next_{e}:\n'
    s+='b finish';b.install('repair_period_technology_in_world_news',0x25e8640,s,ret=True)
