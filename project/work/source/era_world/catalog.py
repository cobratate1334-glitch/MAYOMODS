"""Distinct supplied scenes for actual journal eras; World War phases win."""
THEMES=[
 (1800,'Town and countryside','1800s/event_pictures/town_market','#67472f','#f1e4cb','#352b21'),
 (1820,'Sail and steam','1800s/event_pictures/naval_departure','#3e5962','#e8e7d6','#293a3e'),
 (1840,'Print and industry','1800s/event_pictures/printing_workshop','#784c3a','#f3e5ce','#382b24'),
 (1860,'Harvest and rail','1800s/event_pictures/harvest_day','#5b633e','#eee7ce','#303821'),
 (1880,'Trade and invention','1800s/event_pictures/bank_deposit','#715e34','#f3e9d3','#372f21'),
 (1900,'Early 1900s','eras/1900s/event_pictures/frontier_main_street','#75462f','#f7e9d4','#3d2b23'),
 (1920,'Jazz age','eras/1920s/event_pictures/jazz_city_night','#344754','#f0e6d1','#28343d'),
 (1940,'Radio age','eras/1940s/event_pictures/radio_evening','#4b604f','#eee8d8','#2b392f'),
 (1960,'Records and colour','eras/1960s/event_pictures/record_store_visit','#246b68','#eff0d9','#203f3e'),
 (1980,'Arcade era','eras/1980s/event_pictures/arcade_night','#57486e','#eee5f0','#352a43'),
 (2000,'Internet era','eras/2000s/event_pictures/internet_cafe','#365e83','#e9eef3','#27394d'),
 (2010,'Connected life','eras/2010s/event_pictures/festival_selfie','#574c81','#eeeaf5','#352f49'),
 (2020,'Modern city','eras/2020s/event_pictures/city_everyday','#34596b','#e6edf0','#243c47'),
 (2026,'Creative life','eras/2026/event_pictures/creative_workshop','#435a86','#ebedf5','#2a3750')]
def theme(year):return next((r for r in reversed(THEMES)if year>=r[0]),None)
def art(key):return 'native1119/'+key

# Distinct illustrations for ordinary nineteenth-century yearly context.
# Historical headlines use separate event-specific archival art instead.
PERIOD_SCENES=['town_market','stagecoach_arrival','printing_workshop','fishing_trip','harvest_day','bank_deposit','naval_departure','forest_wildlife','livestock_market','mine_workday','prospector_find','sheriff_office_job']
PERIOD_NEWS=[
 ('Market day','Markets bring farmers and townspeople together. Prices and a good harvest can shape a family’s year.'),
 ('News arrives by road','Travellers and postal coaches carry letters and news. Long journeys can still take days or weeks.'),
 ('The printed page','Printers publish books and newspapers. More readers follow stories from beyond their own town.'),
 ('Life by the river','Rivers support travel and livelihoods. Fishing and trade remain part of daily life in many places.'),
 ('Harvest season','A good harvest helps families through the coming months. Bad weather can make food more costly.'),
 ('Trade and savings','Banks and trading houses support growing markets. Many families still rely on small savings and local credit.'),
 ('Ships connect distant places','Sailing ships carry people and goods over long distances. Life at sea can be difficult and dangerous.'),
 ('Beyond the town','Many people still live and work in the countryside. Growing towns change the land around them.'),
 ('Livestock and livelihoods','Animals support farms and transport. Traders gather to buy and sell livestock at local markets.'),
 ('Work and industry','Mines and workshops supply growing industries. Work is often hard and safety protections are limited.'),
 ('A search for opportunity','Families seek work and new opportunities. For many people travel means leaving familiar places behind.'),
 ('Life in a growing town','Town offices handle records and public notices. Local institutions change as communities grow.')]
