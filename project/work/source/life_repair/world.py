"""Country/year data for native briefings and stable per-year mission puzzles."""
from native_hooks import h

COUNTRIES={
 'Germany':('de_imperial','German Empire','Kaiser Wilhelm II','de_nazi','Nazi Germany','Adolf Hitler'),
 'Japan':('jp','Empire of Japan','Imperial government','jp','Empire of Japan','Imperial cabinet; Hideki Tojo from 1941 to 1944'),
 'Italy':('it_royal','Kingdom of Italy','Royal government','it_royal','Kingdom of Italy','Benito Mussolini until 1943; successor governments thereafter'),
 'United States':('us48','United States','Woodrow Wilson','us48','United States','Franklin D. Roosevelt; Harry S. Truman from 1945'),
 'United Kingdom':('uk','United Kingdom','Wartime cabinet','uk','United Kingdom','Neville Chamberlain; Winston Churchill from 1940'),
 'France':('fr','French Republic','Wartime government','fr','France under occupation; Free French resistance','French and Free French authorities'),
 'Russia':('ru_imperial','Russian Empire; revolutionary governments from 1917','Imperial and successor governments','ussr','Soviet Union','Joseph Stalin')}
TARGETS=[('Germany',1939,2),('Germany',1940,2),('Italy',1940,2),('Japan',1941,2),('United States',1944,2),('United Kingdom',1944,2),('Russia',1941,2),('Germany',1941,2),('Germany',1914,1),('France',1914,1),('United Kingdom',1914,1)]


def hooks(b):
    s=b.ctx('life_rework')+b.set('WarExtraNews1106',0)+b.set('WorldEncounter1106',0)+b.text('WarSideName','Neutral')+b.text('WarFlag1106','')+b.text('WarGovernment1106','Civil government')+b.text('WarLeader1106','')
    s+=b.get('War','w25')+b.get('Year','w26')+b.get('WarSide','w27')
    for n,label in [(1,'Allied powers'),(2,'Central powers'),(3,'Axis powers')]:s+=f'cmp w27,#{n}\nb.ne side1106_next_{n}\n'+b.text('WarSideName',label)+f'side1106_next_{n}:\n'
    s+='cmp w25,#2\nb.ne side1106_adjust_done\ncmp w27,#2\nb.ne side1106_adjust_done\n'+b.text('WarSideName','Axis powers')+'side1106_adjust_done:\ncmp w25,#1\nb.ne kit1106_ww2\n'+b.text('WarKit1106','Bolt-action rifles, early aircraft, machine guns and field telephones. Five-round ammunition supply; no jets, drones or modern body armour.')+b.set('WarMagazine1106',5)+'b kit1106_done\nkit1106_ww2:\ncmp w25,#2\nb.ne kit1106_peace\n'+b.text('WarKit1106','Period rifles, machine guns, radios, tanks and propeller aircraft. Ammunition capacity follows the country’s service rifle. No modern drones or guided strike systems.')+b.set('WarMagazine1106',5)+'b kit1106_done\nkit1106_peace:\n'+b.text('WarKit1106','No world-war deployment is active in this year.')+'kit1106_done:\n'
    s+=b.string('Country')+'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\nmov x28,x0\n'
    for i,(country,values)in enumerate(COUNTRIES.items()):
        s+='mov x8,x28\n'+h.compare_key(country,'country1106_'+str(i),'country1106_next_'+str(i))+'\ncountry1106_next_'+str(i)+':\n'
    s+='b country1106_done\n'
    for i,(country,(flag1,gov1,leader1,flag2,gov2,leader2))in enumerate(COUNTRIES.items()):
        s+=f'country1106_{i}:\ncmp w25,#1\nb.ne nation1106_ww2_{i}\n'+b.text('WarFlag1106','mayomods1106/flags/'+flag1)+b.text('WarGovernment1106',gov1)+b.text('WarLeader1106',leader1)+f'b nation1106_extra_{i}\nnation1106_ww2_{i}:\ncmp w25,#2\nb.ne country1106_done\n'+b.text('WarFlag1106','mayomods1106/flags/'+flag2)+b.text('WarGovernment1106',gov2)+b.text('WarLeader1106',leader2)+f'nation1106_extra_{i}:\n'
        if country=='United Kingdom':s+=b.set('WarMagazine1106',10)
        if country=='United States':
            s+='cmp w25,#2\nb.ne us1106_ammo_done\n'+b.set('WarMagazine1106',8)+'us1106_ammo_done:\n'
        if country in ['Japan','United States']:
            s+=f'cmp w26,#1941\nb.ne pearl1106_done_{i}\n'+b.set('WarExtraNews1106',1)+b.text('WarHeadline1106','1941: Pearl Harbor')+b.text('WarExtraBody1106','On 7 December, Japanese forces attack the US Pacific Fleet at Pearl Harbor. More than 2,400 Americans are killed. The United States enters the war against Japan; Germany and Italy declare war on the United States shortly afterwards.')+f'pearl1106_done_{i}:\n'
        if country=='Japan':s+=f'cmp w26,#1945\nb.ne nuclear1106_done_{i}\n'+b.set('WarExtraNews1106',2)+b.text('WarHeadline1106','1945: Hiroshima and Nagasaki')+b.text('WarExtraBody1106','The United States drops an atomic bomb on Hiroshima on 6 August and Nagasaki on 9 August. Tens of thousands die immediately; many more die from burns, injuries and radiation. Japan announces surrender on 15 August. Civilian losses are part of the historical toll, separate from your fictional unit report.')+f'nuclear1106_done_{i}:\n'
        if country=='United States':s+='cmp w26,#1900\nb.lt encounter1106_us_done\ncmp w26,#1970\nb.gt encounter1106_us_done\n'+b.get('Roll')+'cbnz w24,encounter1106_us_done\ncmp w23,#8\nb.lt encounter1106_us_done\n'+b.set('WorldEncounter1106',2)+'encounter1106_us_done:\n'
        s+='b country1106_done\n'
    s+='country1106_done:\n'+b.get('WorldEncounter1106')+'cbnz w24,encounter1106_done\ncmp w23,#8\nb.lt encounter1106_done\n'+b.get('Roll')+'cmp w24,#3\nb.ne encounter1106_done\n'+b.set('WorldEncounter1106',1)+'encounter1106_done:\n'
    for i,(country,first,war)in enumerate(TARGETS):
        s+=b.set('CommandPermit'+str(i)+'1106',0)+'mov x8,x28\n'+h.compare_key(country,'permit1106_'+str(i),'permit1106_next_'+str(i))+f'\npermit1106_{i}:\ncmp w26,#{first}\nb.lt permit1106_next_{i}\ncmp w25,#{war}\nb.ne permit1106_next_{i}\n'+b.set('CommandPermit'+str(i)+'1106',1)+f'permit1106_next_{i}:\n'
    s+=b.get('CommandActive1106')+'cbz w24,command1106_income_done\ncbz w25,command1106_end\n'+b.get('CommandBuildAge1106')+'cmp w24,w23\nb.ge command1106_income_done\n'+b.put('CommandBuildAge1106','w23')+b.get('CommandIndustry1106','w24')+'mov w9,#5\nudiv w24,w24,w9\nadd w26,w24,#10\n'+b.get('CommandBudget1106')+'add w24,w24,w26\n'+b.put('CommandBudget1106')+'b command1106_income_done\ncommand1106_end:\n'+b.set('CommandActive1106',0)+'command1106_income_done:\n'
    s+=b.get('MissionBriefAge1106')+'cmp w24,w23\nb.ge finish\n'+b.put('MissionBriefAge1106','w23')
    for mode in ['Trench','Flight']:
        for stage in range(1,4):
            s+=b.rng(3,'w27')+b.put(mode+'Safe'+str(stage)+'1106','w27')
            for lane,label in enumerate(['left','centre','right']):s+=f'cmp w27,#{lane}\nb.ne hint1106_next_{mode}_{stage}_{lane}\n'+b.text(mode+'Hint'+str(stage)+'1106','The observer reports that the '+label+' approach is clear. Other approaches are exposed to incoming fire.')+f'hint1106_next_{mode}_{stage}_{lane}:\n'
    s+='b finish';world=b.routine('repair_context_for_country_year_and_missions',s)
    old=b.resolved('life_rework_refresh_context');s=old['source'];marker='\nb finish\nfinish:';assert marker in s;b.redirect(old['name'],s.replace(marker,f'\nbl {world:#x}'+marker,1))
    # Age buckets contain six distinct stories each; continuing bullying cases
    # retain their existing reserved follow-up IDs 4, 5 and 6.
    old=b.resolved('followup_prepare_native_annual_notices');s=old['source'];needle='mov w9,#3\nudiv w10,w25,w9\nmsub w24,w10,w9,w25\nadd w24,w24,#1\n';assert needle in s
    replacement='mov w9,#6\nudiv w10,w25,w9\nmsub w24,w10,w9,w25\nadd w24,w24,#7\ncmp w23,#12\nb.lt school1106_bucket_ready\nadd w24,w24,#6\ncmp w23,#18\nb.lt school1106_bucket_ready\nadd w24,w24,#6\nschool1106_bucket_ready:\n'
    b.redirect(old['name'],s.replace(needle,replacement,1))
