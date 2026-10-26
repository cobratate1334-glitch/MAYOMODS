"""Explicit gameplay cohorts, not a claim to reproduce every historical exemption."""
# country, first year, last year inclusive, minimum age, maximum age.
DRAFTS=[('United Kingdom',1916,1917,18,41),('United Kingdom',1939,1944,18,41),('United States',1917,1917,21,30),('United States',1940,1940,21,35),('United States',1941,1941,21,45),('United States',1942,1944,18,45),('Germany',1914,1917,20,45),('Germany',1939,1944,18,45),('France',1914,1917,20,45),('France',1939,1939,20,45),('Canada',1917,1917,20,45),('Canada',1940,1944,20,40),('Australia',1942,1944,18,35),('New Zealand',1916,1917,20,45),('New Zealand',1940,1944,18,40),('Russia',1914,1917,21,40),('Russia',1941,1944,18,45),('Japan',1914,1917,20,40),('Japan',1939,1944,20,40),('Italy',1915,1917,18,40),('Italy',1940,1942,18,40)]
ENTRY={'United Kingdom':(1914,1939),'United States':(1917,1941),'Germany':(1914,1939),'France':(1914,1939),'Canada':(1914,1939),'Australia':(1914,1939),'New Zealand':(1914,1939),'Russia':(1914,1941),'Japan':(1914,1939),'Italy':(1915,1940),'India':(1914,1939)}
NOTES={
 'United Kingdom':'Britain used volunteers before its 1916 WWI draft. Ireland was excluded from WWI conscription; Northern Ireland was excluded in WWII.',
 'United States':'The US draft began in 1917 and returned in 1940. The 1940 call-up is for training before US wartime entry in December 1941.',
 'Germany':'Germany mobilised conscripts in both wars. This game models an adult cohort; emergency late-war measures and detailed exemptions are not reproduced.',
 'France':'France mobilised in both wars. After the 1940 armistice, service was divided between competing authorities; this game offers volunteering rather than a universal French draft in 1940–44.',
 'Canada':'WWI conscription began in 1917. WWII conscripts initially served in home defence; compulsory overseas service was introduced late in 1944.',
 'Australia':'WWI overseas service was voluntary. WWII Citizen Military Forces obligations had geographical limits; volunteering for the AIF was separate.',
 'New Zealand':'Conscription began in 1916 and returned in 1940. Medical fitness and real historical exemptions affected service.',
 'Russia':'WWI service was in the Russian Empire; WWII service was in the Soviet armed forces. This game uses simplified adult cohorts.',
 'Japan':'Japan had conscription and served on different sides in the two world wars. Branch, training and assignment remain separate.',
 'Italy':'Italy entered WWI in 1915 and WWII in 1940. The 1943 armistice split its armed forces; no single universal 1943–44 draft is imposed here.',
 'India':'British Indian forces used volunteers in both world wars. This game does not invent compulsory overseas conscription for India.'}

def eligible(country,year,age,sex,city=''):
 if sex!=0:return False
 if country=='United Kingdom'and any(t in city.lower()for t in ['belfast','dublin']):return False
 return any(c==country and lo<=year<=hi and amin<=age<=amax for c,lo,hi,amin,amax in DRAFTS)
