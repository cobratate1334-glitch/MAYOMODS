"""Calendar/country context; historical losses are separate from game unit losses."""
WW1={'Germany':(1914,2,'Kaiser Wilhelm II'),'Austria':(1914,2,'Franz Joseph I / Charles I'),'Hungary':(1914,2,'Franz Joseph I / Charles I'),'Turkey':(1914,2,'Ottoman wartime government'),'Bulgaria':(1915,2,'Ferdinand I'),'United Kingdom':(1914,1,'British wartime government'),'France':(1914,1,'French wartime government'),'Belgium':(1914,1,'Albert I'),'Russia':(1914,1,'Nicholas II / provisional government'),'Serbia':(1914,1,'Serbian wartime government'),'Italy':(1915,1,'Italian wartime government'),'Portugal':(1916,1,'Portuguese wartime government'),'Romania':(1916,1,'Ferdinand I'),'United States':(1917,1,'Woodrow Wilson'),'Japan':(1914,1,'Japanese wartime government'),'Australia':(1914,1,'Australian wartime government'),'Canada':(1914,1,'Canadian wartime government'),'New Zealand':(1914,1,'New Zealand wartime government'),'India':(1914,1,'British Indian administration'),'Brazil':(1917,1,'Brazilian wartime government')}
WW2={'Germany':(1939,2,'Adolf Hitler; Nazi Germany'),'Italy':(1940,2,'Benito Mussolini; Fascist Italy'),'Japan':(1939,2,'Japanese wartime government'),'United Kingdom':(1939,1,'Chamberlain / Churchill wartime governments'),'France':(1939,1,'French and Free French leadership'),'Poland':(1939,1,'Polish government and government-in-exile'),'United States':(1941,1,'Franklin D. Roosevelt / Harry S. Truman'),'Russia':(1941,1,'Joseph Stalin; Soviet Union'),'China':(1939,1,'Chinese wartime governments'),'Australia':(1939,1,'Australian wartime government'),'Canada':(1939,1,'Canadian wartime government'),'New Zealand':(1939,1,'New Zealand wartime government'),'India':(1939,1,'British Indian administration'),'Brazil':(1942,1,'Brazilian wartime government'),'Netherlands':(1940,1,'Dutch government-in-exile'),'Belgium':(1940,1,'Belgian government-in-exile'),'Norway':(1940,1,'Norwegian government-in-exile'),'Greece':(1940,1,'Greek wartime government'),'Finland':(1939,3,'Finnish wartime government'),'Hungary':(1940,2,'Hungarian wartime government'),'Romania':(1940,2,'Romanian wartime government'),'Bulgaria':(1941,2,'Bulgarian wartime government'),'South Africa':(1939,1,'South African wartime government')}

def context(year,country):
    war=1 if 1914<=year<=1918 else 2 if 1939<=year<=1945 else 0
    source=WW1 if war==1 else WW2
    joined,side,leader=source.get(country,(9999,0,'National government'))
    if year<joined:side=0
    if war==2 and country in ['Italy','Romania','Bulgaria']and year>=1944:side=1
    name={0:'Peacetime',1:'World War I',2:'World War II'}[war]
    history={0:'No world-war campaign is active in this calendar year.',1:'1914–1918. The Allies and Central Powers fought across several fronts. Military and civilian deaths are commonly estimated at about 20 million. Unit losses in your game are tracked separately.',2:'1939–1945. The Allies fought the Axis powers. Nazi Germany occupied much of Europe and carried out the Holocaust. Global military and civilian deaths are estimated at roughly 70–85 million. Game unit losses are separate.'}[war]
    front='Home front: your country is not currently a belligerent in this campaign.'
    if side:
        if war==1:front='Western Front: supply routes, trenches and field hospitals.'if country in ['Germany','France','United Kingdom','United States','Belgium','Canada','Australia','New Zealand']else'Eastern and regional fronts: supply duties, reconnaissance and casualty evacuation.'
        else:
            front='Pacific theatre: island supply routes, coastal observation and field hospitals.'if country in ['Japan','China','Australia','New Zealand','India']else'European theatre: supply routes, reconnaissance and casualty evacuation.'
            if year==1944 and country in ['United States','United Kingdom','Canada','France']:front='Normandy, June 1944: D-Day and the Allied campaign in France. Prepare a convoy and evacuation mission.'
            if year==1944 and country=='Germany':front='Western Front, 1944: Allied forces have landed in Normandy. Your unit faces disrupted supply routes and civilian evacuations.'
    equipment='Field telephones, rail supply, early aircraft and medical stretchers.'if war==1 else'Field radios, propeller aircraft, armoured vehicles and medical jeeps.'if war==2 else'Civilian equipment for the current year.'
    return dict(War=war,WarSide=side,WarName=name,WarLeader=leader,Front=front,History=history,WarEquipment=equipment)

REFERENCES=[
    'https://www.iwm.org.uk/history/first-world-war',
    'https://www.iwm.org.uk/history/second-world-war',
    'https://www.nam.ac.uk/explore/d-day',
    'https://encyclopedia.ushmm.org/content/en/article/world-war-ii-in-europe',
    'https://www.nationalww2museum.org/students-teachers/student-resources/research-starters/research-starters-worldwide-deaths-world-war',
]
