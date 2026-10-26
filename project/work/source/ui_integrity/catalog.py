"""Sprite rectangles reference the supplied atlases without altering their pixels.

Rectangles use top-left source coordinates; Unity's package writer converts Y.
Dates describe availability, not a claim to simulate every country's retail law.
"""
TECH='a_high_resolution_flat_clean_rendered_icon_sheet.webp'
TRANSPORT='a_clean_high_resolution_illustration_sprite_she.webp'
WAR='a_large_high_resolution_dark_gray_background_col.webp'
FASHION='1000004164.webp'
ART={
 'iphone':(TECH,(450,905,50,105)), 'switch':(TECH,(635,925,110,80)),
 'ps5':(TECH,(747,907,100,105)), 'mobile':(TECH,(592,912,45,96)),
 'laptop':(TECH,(177,918,92,90)), 'vr':(TECH,(897,919,101,77)),
 'vape':(TECH,(936,375,44,103)), 'bugatti':(TECH,(1264,482,125,74)),
 'mustang':(TECH,(136,636,140,76)), 'beetle':(TRANSPORT,(742,302,115,66)),
 'rotary':(TRANSPORT,(2,766,79,72)), 'typewriter':(TRANSPORT,(536,834,58,78)),
 'radio':(TRANSPORT,(1400,702,70,61)), 'desktop':(TRANSPORT,(1,701,77,61)),
 'prewar_car':(WAR,(365,908,172,97)), 'modern_car':(TECH,(130,481,126,75)),
 'ww1_plane':(WAR,(0,583,163,62)), 'ww2_plane':(WAR,(1244,695,289,80)),
 'ww1_tank':(WAR,(146,505,158,68)), 'ww2_tank':(WAR,(440,504,164,66)),
 'rifle':(WAR,(5,349,259,34)), 'radio_field':(WAR,(1175,473,62,60)),
 'helmet':(WAR,(11,0,73,60)), 'medical':(WAR,(1450,350,78,80)),
 'bunker':(WAR,(387,782,151,82)), 'ship':(WAR,(15,829,293,75)),
 'trench':(WAR,(685,782,170,81)), 'gas_mask':(WAR,(145,62,87,73)),
 'vintage_hat':(FASHION,(35,85,325,227)),
 'retro_hat':(FASHION,(795,104,313,206)),
 'modern_hat':(FASHION,(1180,83,310,240)),
}
# key, label, first year, price, minimum age, short purchase/use description
ITEMS=[
 ('typewriter','Typewriter',1900,120,12,'Write stories and practise your typing.'),
 ('rotary','Home telephone',1900,90,16,'Call a relative and keep in touch.'),
 ('radio','Table radio',1920,75,10,'Listen to music and the news.'),
 ('desktop','Home computer',1981,1300,12,'Practise typing and work on a project.'),
 ('mobile','Mobile phone',1983,600,16,'Make calls while away from home.'),
 ('laptop','Laptop',1989,1200,12,'Work on a writing or coding project.'),
 ('iphone','iPhone',2007,699,13,'Take photographs or call a friend.'),
 ('vr','VR headset',2016,350,13,'Play a short virtual-reality game.'),
 ('switch','Nintendo Switch',2017,299,8,'Play a game and relax.'),
 ('ps5','PlayStation 5',2020,499,8,'Play a game at home.'),
 ('vintage_hat','Vintage cloche',1920,35,6,'Wear a vintage hat on an outing.'),
 ('retro_hat','Pillbox hat',1930,35,6,'Choose a classic look for an outing.'),
 ('modern_hat','Snapback cap',1990,30,6,'Wear your cap on an outing.'),
 ('vape','Vape',2007,25,18,'An adult nicotine product. Using it carries health risks.'),
]
REAL_CARS=[('Bugatti','Chiron',2016,'bugatti'),('Bugatti','Divo',2018,'bugatti'),
 ('Bugatti','Centodieci',2019,'bugatti'),('Bugatti','La Voiture Noire',2019,'bugatti'),
 ('Bugatti','57SC Atlantic',1936,'prewar_car'),('Volkswagen','Beetle',1938,'beetle'),
 ('Ford','Mustang',1964,'mustang'),('Ford','Mustang GT',1965,'mustang')]
