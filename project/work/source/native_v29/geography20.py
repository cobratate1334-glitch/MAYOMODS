"""Game-balance regional warning weights per 1,000 age-ups, not hazard forecasts.
US location matching is conservative: unknown or inland cities never gain coastal hazards.
"""
PROFILES={}
def group(cities,region,tornado=5,hurricane=0,tsunami=0,volcano=0,flood=15,wildfire=0,heat=10):
 for city in cities.split('|'):PROFILES[city]=dict(region=region,Tornado=tornado,Hurricane=hurricane,Tsunami=tsunami,Volcano=volcano,Flood=flood,Wildfire=wildfire,Heat=heat)
group('Oklahoma City|Tulsa|Norman|Wichita|Topeka|Kansas City|Lincoln|Omaha|Des Moines|Sioux Falls','Central Plains',80,flood=20,heat=15)
group('Dallas|Fort Worth|Austin|San Antonio|Lubbock|Amarillo|Waco','Texas interior / Southern Plains',60,flood=25,heat=30)
group('Memphis|Nashville|Birmingham|Huntsville|Jackson|Little Rock|Shreveport|Baton Rouge|St. Louis|Saint Louis|Springfield','Lower Mississippi / Southeast',60,flood=30,heat=20)
group('Houston|Galveston|Corpus Christi|New Orleans|Mobile|Biloxi|Gulfport','Gulf Coast',35,hurricane=35,flood=30,heat=25)
group('Miami|Tampa|Fort Myers|Key West|Jacksonville|Pensacola|St. Petersburg|Saint Petersburg','Florida coast',20,hurricane=40,flood=25,heat=20)
group('Charleston|Savannah|Wilmington|Virginia Beach|Norfolk','Atlantic coast',15,hurricane=25,flood=25,heat=10)
group('New York|New York City|Boston|Atlantic City|Providence','Northeast Atlantic coast',5,hurricane=8,flood=20,heat=10)
group('Orlando|Tallahassee|Atlanta|Raleigh|Charlotte|Columbia|Greenville','Southeastern interior',25,flood=35,heat=20)
group('Phoenix|Tucson|Mesa|Scottsdale|Flagstaff','Arizona interior',3,flood=20,wildfire=20,heat=60)
group('Las Vegas|Reno|Salt Lake City|Denver|Albuquerque|Santa Fe|Boise|Colorado Springs|El Paso','Western interior',5,flood=15,wildfire=25,heat=30)
group('Los Angeles|San Diego|San Francisco|Santa Barbara|Santa Cruz|Monterey|Long Beach|Oakland','Pacific coast',3,tsunami=2,flood=15,wildfire=25,heat=10)
group('Seattle|Tacoma|Olympia|Astoria|Eureka','Pacific coast / Cascades',3,tsunami=3,volcano=3,flood=20,wildfire=10,heat=5)
group('Portland|Salem|Bend|Redding|Vancouver','Cascades interior / volcanic ash region',3,volcano=3,flood=15,wildfire=25,heat=10)
group('Sacramento|Fresno|Bakersfield|Spokane','Pacific inland',3,flood=20,wildfire=30,heat=20)
group('Honolulu','Oahu coast',3,hurricane=10,tsunami=5,flood=25,heat=10)
group('Hilo|Kailua-Kona|Kona','Hawaii Island coast / active volcanic region',3,hurricane=10,tsunami=5,volcano=8,flood=25,heat=10)
group('Anchorage|Kodiak|Seward|Juneau','Alaska coast / regional volcanic ash',2,tsunami=5,volcano=3,flood=15,heat=0)
group('Fairbanks','Alaska interior',2,flood=15,wildfire=10,heat=0)
group('Chicago|Indianapolis|Columbus|Cleveland|Detroit|Milwaukee|Minneapolis|Madison|Louisville|Cincinnati|Pittsburgh|Buffalo|Philadelphia|Baltimore|Washington|Washington D.C.|Washington DC','Eastern / northern interior',20,flood=20,heat=15)
HAZARDS=['Tornado','Hurricane','Tsunami','Volcano','Flood','Wildfire','Heat']
EVENTS=[('Tornado warning','A tornado warning has been issued near your home. Your region has an elevated severe-storm risk.'),('Hurricane warning','A tropical cyclone threatens your coastal region. Local officials have issued an evacuation warning for exposed neighborhoods.'),('Tsunami warning','An offshore earthquake has triggered a coastal tsunami warning. Only low-lying coastal evacuation zones are at risk.'),('Volcanic activity alert','Monitoring stations report volcanic unrest or airborne ash in your region. Follow local ash and evacuation guidance; the entire city is not covered in lava.'),('Flash-flood warning','Intense local rainfall threatens flooding near your home. Avoid flooded roads and low-lying areas.'),('Wildfire alert','A nearby wildfire threatens air quality and some neighborhoods. Officials are monitoring evacuation zones.'),('Extreme heat warning','A period of extreme heat affects your city. Check on friends, use cooling spaces and reduce outdoor exertion.')]
