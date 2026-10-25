"""Stable accessory identities and cosmetic-era rules for the v44 save format."""
ERAS = [
    ('Vintage', 1900, 'Mayo’s Millinery', 'top-hat'),
    ('Noir', 1930, 'Mayo’s Hat Parlour', 'top-hat'),
    ('Retro', 1960, 'Mayo’s Style Boutique', 'sun'),
    ('Modern', 1990, 'Mayo’s Streetwear', 'shopping-bags'),
]
START_YEARS = list(range(1900, 2030, 10)) + [2026]
# id, original timestamp/generated name, display name, first era, base price,
# slot, regional collection. IDs are permanent; do not reorder saves.
ROWS = [
 (1,'20261013045637','Cigarette',0,2,'Mouth',False),
 (2,'20261013045725','Feathered Fedora',1,18,'Headwear',False),
 (3,'20261013045847','Vintage Captain Cap',0,12,'Headwear',False),
 (4,'20261013045921','Classic Fedora',1,14,'Headwear',False),
 (5,'20261013050214','Brown Newsboy Cap',0,5,'Headwear',False),
 (6,'20261013050452','Service Cap',0,9,'Headwear',False),
 (7,'20261013050826','Bowler Hat',0,10,'Headwear',False),
 (8,'20261013051244','Black Trilby',1,13,'Headwear',False),
 (9,'20261013051640','Top Hat',0,25,'Headwear',False),
 (10,'20261013052103','Straw Fedora',2,9,'Headwear',False),
 (11,'20261013052357','Black Beret',1,8,'Headwear',False),
 (12,'20261013071533','Cream Fedora',2,12,'Headwear',False),
 (13,'20261013072028','Black Cowboy Hat',0,23,'Headwear',True),
 (14,'20261013072345','Grey Flat Cap',0,7,'Headwear',False),
 (15,'20261013072710','Tan Cowboy Hat',0,20,'Headwear',True),
 (16,'20261014215042','Cigar',0,4,'Mouth',False),
 (17,'20261014215048','Pipe',0,10,'Mouth',False),
 (18,'20261014220009','Pork Pie Hat',2,11,'Headwear',False),
 (19,'20261015083955','NY Baseball Cap',3,8,'Headwear',False),
 (20,'20261015084612','Cream Baseball Cap',3,7,'Headwear',False),
 (21,'20261015115051','Grey Beanie',3,6,'Headwear',False),
 (22,'20261015115439','Olive Bucket Hat',3,8,'Headwear',False),
 (23,'20261015115740','Charcoal Fedora',3,15,'Headwear',False),
 (24,'cloche','Burgundy Cloche',0,15,'Headwear',False),
 (25,'homburg','Navy Homburg',1,20,'Headwear',False),
 (26,'pillbox','Mustard Pillbox',2,14,'Headwear',False),
 (27,'snapback','Burgundy Snapback',3,9,'Headwear',False),
]
ITEMS = [dict(id=i,source=s,name=n,era=e,base_price=p,slot=slot,regional=r)
         for i,s,n,e,p,slot,r in ROWS]
REGIONS = ['United States','US','Australia','Canada','Mexico','Brazil','Argentina']
STYLE_BASE = 44000
HEAD_TYPE, MOUTH_TYPE = 6, 7

def era_for_year(year):
    return 3 if year >= 1990 else 2 if year >= 1960 else 1 if year >= 1930 else 0

def offer(item, year, age, regional):
    era = era_for_year(year)
    vintage = item['era'] < era
    available = item['era'] <= era and (not vintage or (year+item['id'])%3 == 0)
    if item['regional']: available = regional
    if item['slot'] == 'Mouth' and age < 18: available = False
    price = item['base_price'] * [1,2,4,8][era]
    if vintage and not item['regional']: price = price * 3 // 2
    return int(available), price
