"""Prepare data for native annual scenarios; never show a UI during simulation."""
from native_hooks import h


def hooks(b):
    s=b.ctx('life_rework')+b.get('AnnualAge1105','w25')+'cmp w25,w23\nb.ge finish\n'
    s+=b.put('AnnualAge1105','w23')+b.set('WarNews1105',0)+b.set('DraftEligible1105',0)+b.set('SchoolEvent1105',0)+b.set('CrowdEvent1105',0)+b.set('MarriageEvent1105',0)
    s+=b.get('Year','w26')+b.get('War','w27')+'cbnz w27,annual1105_war_active\n'+b.set('Deployed',0)+b.set('MissionStep',0)+'annual1105_war_active:\n'
    bulletins={
        1914:('World War I begins','World War I has begun in Europe. Austria-Hungary and Germany face Serbia, Russia, France and Britain. Countries enter at different times. Your country’s briefing explains whether you can be called up.'),
        1918:('The armistice of 1918','The fighting on the Western Front stops on 11 November. About 15–20 million people died during World War I, including civilians; estimates differ. Survivors return to a changed world.'),
        1939:('World War II begins','Nazi Germany invades Poland. Britain and France declare war. World War II has begun. Your country’s role and the chance of a call-up follow its entry into the war.'),
        1940:('War spreads across Europe','Nazi Germany occupies much of Western Europe. Britain faces air raids. Civilians, resistance groups and service personnel face growing danger. Your briefing follows your country.'),
        1941:('The war becomes global','Germany invades the Soviet Union. Japan attacks Pearl Harbor, and the United States enters the war. The Axis and Allied powers fight across several continents.'),
        1942:('A world at war','The war reaches a devastating scale. The Holocaust and other mass atrocities claim civilian lives. The Eastern Front, North Africa and the Pacific are major theatres.'),
        1943:('The tide turns','The Axis suffers defeats at Stalingrad and in North Africa. The Allies invade Italy. The war still takes a heavy toll on soldiers and civilians.'),
        1944:('D-Day and the final campaigns','On 6 June, Allied forces land in Normandy. Fighting continues in Europe and the Pacific. Your country and service role determine the missions available to you.'),
        1945:('World War II ends','Germany surrenders in May; Japan surrenders in August, with the formal ceremony in September. An estimated 70–85 million people died, including civilians. These historical estimates are separate from the fictional losses in your own unit.')}
    for year,(title,text)in bulletins.items():
        s+=f'cmp w26,#{year}\nb.ne news1105_next_{year}\n'+b.text('NewsTitle1105',title)+b.text('NewsBody1105',text)+b.set('WarNews1105',1)+f'b news1105_ready\nnews1105_next_{year}:\n'
    s+='cbz w27,news1105_ready\n'+b.text('NewsTitle1105','The war continues')+b.text('NewsBody1105','<GFC.life_rework.History>\n\nYour country: <GFC.life_rework.Country>. Front: <GFC.life_rework.Front>. Open the briefing for service, missions and the unit report.')+b.set('WarNews1105',1)
    s+='news1105_ready:\n'+b.get('WarNews1105')+'cbz w24,news1105_draft\n'+b.put('NewsYear1105','w26')
    # Log the headline through the real LifeLog. The popup is queued by the
    # engine later, alongside normal yearly events.
    s+=b.string('NewsTitle1105')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\n'+f'bl {b.journal55:#x}\n'
    s+='news1105_draft:\ncmp w23,#18\nb.lt news1105_school\ncmp w23,#45\nb.gt news1105_school\n'
    s+=b.get('WarSide')+'cbz w24,news1105_school\n'+b.get('Deployed')+'cbnz w24,news1105_school\n'
    s+=b.get('DraftAge')+'cmp w24,w23\nb.ge news1105_school\n'
    s+=h.load_occupation(end='news1105_school')+'\nldr w9,[x8,#0x10]\ncmp w9,#4\nb.eq news1105_school\n'
    s+=b.set('DraftEligible1105',1)
    s+='news1105_school:\n'+b.get('SchoolEligible')+'cbz w24,annual_social1105\n'+b.get('Roll','w25')
    # School cases with continuing follow-ups; no reduction in the stock game's random events.
    s+='mov w9,#3\nudiv w10,w25,w9\nmsub w24,w10,w9,w25\nadd w24,w24,#1\n'+b.put('SchoolEvent1105')
    s+=b.get('SchoolBullyStage','w25')
    for stage,event in [(1,6),(2,4),(3,5)]:s+=f'cmp w25,#{stage}\nb.ne school1105_stage_next_{stage}\n'+b.set('SchoolEvent1105',event)+f'b annual_social1105\nschool1105_stage_next_{stage}:\n'
    s+='cmp w25,#4\nb.lt annual_social1105\n'+b.get('SchoolEvent1105')+'cmp w24,#1\nb.ne annual_social1105\n'+b.set('SchoolEvent1105',2)
    s+='annual_social1105:\n'+b.get('Year')+'cmp w24,#1980\nb.lt annual_marriage1105\n'+b.get('CrowdRisk1105')+'cmp w24,#40\nb.lt annual_marriage1105\n'+b.get('Roll')+'cmp w24,#25\nb.hs annual_marriage1105\n'+b.set('CrowdEvent1105',1)
    s+='annual_marriage1105:\n'+b.get('Married1105')+'cbz w24,finish\n'+b.get('MarriageTrust1105')+'cmp w24,#30\nb.ge finish\n'+b.get('MarriageConflicts1105')+'cmp w24,#2\nb.lt finish\n'+b.set('MarriageEvent1105',1)+'b finish'
    annual=b.routine('followup_prepare_native_annual_notices',s)
    old=b.resolved('life_rework_refresh_context');source=old['source']
    marker='\nb finish\nfinish:';assert marker in source
    b.redirect(old['name'],source.replace(marker,f'\nbl {annual:#x}'+marker,1))
