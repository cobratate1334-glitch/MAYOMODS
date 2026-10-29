"""Original school art and explicit simulated exchange-rate data."""
ART='native1125/school/'
SCHOOL_ART=[(1800,1899,[ART+'schoolyard1830',ART+'lesson1850',ART+'picnic1880']),
 (1900,1919,[ART+'library1910',ART+'lesson1850',ART+'picnic1880']),
 (1920,1939,[ART+'library1910',ART+'garden1930']),
 (1940,1959,[ART+'garden1930',ART+'science1950']),
 (1960,1979,[ART+'science1950','native1118/school/event_pictures/1960s_school_dance.png'])]
# game currency ID, ISO, symbol, units per USD x 10,000, countries, first year.
# Offline game rates: explicitly not a live or historically certified FX feed.
CURRENCIES=[
 (1,'USD','$',10000,['United States','United States of America'],1800),
 (2,'GBP','£',7800,['United Kingdom','Britain'],1800),
 (3,'EUR','€',9200,['France','Germany','Spain','Italy','Netherlands','Ireland','Finland','Portugal','Austria','Belgium'],1999),
 (4,'JPY','¥',1500000,['Japan'],1871),
 (5,'INR','₹',830000,['India'],1800),
 (6,'AUD','A$',15000,['Australia'],1966),
 (7,'CAD','C$',13500,['Canada'],1858),
 (8,'BRL','R$',50000,['Brazil'],1994),
 (9,'CNY','CN¥',72000,['China'],1948),
 (10,'KRW','₩',13300000,['South Korea'],1962),
 (11,'MXN','Mex$',170000,['Mexico'],1993),
 (12,'CHF','CHF ',8800,['Switzerland'],1850),
 (13,'SEK','kr ',104000,['Sweden'],1873),
 (14,'NZD','NZ$',16500,['New Zealand'],1967),
 (15,'ZAR','R ',185000,['South Africa'],1961),
 (16,'FRF','F ',60350,['France'],1800),
 (17,'DEM','DM ',17994,['Germany'],1871),
 (18,'AUDp','A£',3900,['Australia'],1910),
 (19,'BRR','CR$',10000,['Brazil'],1942)]
