"""Game-defined availability and fictional period inventory. Prices are game values."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ROAD=[
 (1900,'Brass Carriage','Convertible',900,'car01',5),
 (1910,'Open Tourer','Convertible',1400,'car02',11),
 (1920,'Regent Saloon','Sedan',1900,'car03',3),
 (1930,'Streamline','Sedan',2400,'car04',9),
 (1940,'Workshop Pickup','Truck',2900,'car05',15),
 (1950,'Coastline','Convertible',3700,'car06',19),
 (1960,'Thunder Coupe','Coupe',5200,'car07',12),
 (1970,'Family Estate','Wagon',6800,'car08',21),
 (1980,'Metro Hatch','Hatchback',9000,'car09',3),
 (1990,'Everyday Sedan','Sedan',15000,'car10',17),
 (2000,'Horizon SUV','SUV',27000,'car11',17),
 (2010,'Current EV','Hatchback',36000,'car12',20),
]
CARS=[]
for year,name,typ,price,art,color in ROAD:
 for luxury in [False,True]:
  CARS.append(dict(id=len(CARS)+1,make='Mayo',model=f'{year} {name}'+(' Grand' if luxury else ''),type=typ,price=price*(3 if luxury else 1),start=year,end=year+39 if year<1990 else 9999,art=art,color=color,luxury=luxury,race_only=False,racing_class='B' if luxury else 'C'))
# Every class has an eligible circuit and stock model in every playable year.
# Early circuit variants use carriage art; later variants have their own bodies.
for typ,epochs in [('Formula',[(1900,1949,'Carriage Circuit','car01',5),(1950,9999,'Heritage Open Racer','car13',15)]),('Stock Car',[(1900,1959,'Carriage Stock Special','car01',5),(1960,9999,'Classic Stock Racer','car07',12)])]:
 for year,end,name,art,color in epochs:
  for cls in 'CBAS':
   CARS.append(dict(id=len(CARS)+1,make='Mayo',model=f'{year} {name} {cls}',type=typ,price=(12000 if year==1900 else 65000)*('CBAS'.index(cls)+1),start=year,end=end,art=art,color=color,luxury=False,race_only=True,racing_class=cls))
HOUSES=[
 dict(name='workers terrace',year=1900,art='house01',beds=(2,3),baths=(1,2),price=2,desc='brick, practical, compact'),
 dict(name='Edwardian townhome',year=1910,art='house01',beds=(3,5),baths=(2,3),price=3,desc='ornate, elegant, spacious'),
 dict(name='deco duplex',year=1930,art='house02',beds=(2,4),baths=(1,3),price=3,desc='geometric, stylish, bright'),
 dict(name='streamline villa',year=1940,art='house02',beds=(3,5),baths=(2,4),price=4,desc='curved, refined, airy'),
 dict(name='midcentury ranch',year=1960,art='house03',beds=(2,4),baths=(1,3),price=3,desc='low-slung, open-plan, sunny'),
 dict(name='garden split-level',year=1970,art='house03',beds=(3,5),baths=(2,4),price=4,desc='leafy, spacious, relaxed'),
 dict(name='smart townhouse',year=2000,art='house04',beds=(2,4),baths=(2,3),price=4,desc='connected, efficient, bright'),
 dict(name='solar villa',year=2010,art='house04',beds=(3,6),baths=(2,5),price=5,desc='solar-powered, sustainable, spacious'),
]
# Availability is a gameplay rule, not a claim about a style's invention date.
HOUSE_YEARS={'trailer':1930,'manufactured home':1950,'loft':1900,'tiny house':1990,'condo':1960,'houseboat':1900,'bungalow':1900,'rambler':1940,'duplex':1900,'chalet':1900,'craftsman':1900,'contemporary':1970,'pueblo':1900,'midcentury':1950,'colonial':1800,'Victorian':1800,'art deco':1920,'acreage':1900,'equestrian property':1900,'geodesic':1950,'mansion':1800,'estate':1700,'palace':1000,'castle':1000,'storybook':1400,'penthouse':1920,'villa':1600,'futuristic':2030,'vampire castle':1}
HOUSE_YEARS.update({x['name']:x['year'] for x in HOUSES})
# TikTok uses its 2018 worldwide release for this globally playable game.
PLATFORMS={'Facebook':2004,'Instagram':2010,'OnlyFans':2016,'TikTok':2018,'Twitch':2011,'Twitter':2006,'SoundCloud':2007,'YouTube':2005}
ART_KEYS=[f'car{i:02d}' for i in range(1,14)]+[f'house{i:02d}' for i in range(1,5)]
CAR_TYPES={'Hatchback':1,'Coupe':2,'Convertible':3,'Sedan':4,'Wagon':5,'SUV':6,'Minivan':7,'Truck':8,'Exotic':9,'4x4':10,'Hearse':11,'Stock Car':12,'Formula':13}
def type_supported(year,typ,luxury=False,race_class='',race_type=0):
 if not typ or year>=2026:return True
 race=bool(race_type or race_class)
 return any(car_allowed(c,year)and CAR_TYPES[c['type']]==typ and c['luxury']==luxury and (not c['race_only']if not race else c['racing_class'].casefold()==race_class.casefold())for c in CARS)
def car_allowed(item,year):return year>=2026 if item is None else item['start']<=year<=item['end']
def house_allowed(name,year):return year>=HOUSE_YEARS.get(name,2026)
def fnv(value):
 h=2166136261
 for c in value:h=((h^ord(c))*16777619)&0xffffffff
 return h
assert len({x['model'] for x in CARS})==len(CARS)==40
assert len({fnv(x['model']) for x in CARS})==len(CARS)
