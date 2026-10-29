"""Append-only period catalog; prices are deliberately approximate game values."""
# make, model, first year, last showroom year, type, cost, sprite key
VEHICLES=[
 ('Mayo','1800 Passenger carriage',1800,1885,'Convertible',120,'native1119/1800s/icons/town_travel/stagecoach'),
 ('Benz','1886 Patent Motorwagen',1886,1907,'Convertible',600,'mayo45-car01'),
 ('Ford','1908 Model T',1908,1927,'Convertible',850,'mayo45-car02'),
 ('Ford','1927 Model A',1927,1940,'Sedan',500,'mayo45-car03'),
 ('Chevrolet','1936 Master',1936,1950,'Sedan',650,'mayo45-car04'),
 ('Willys','1941 MB',1941,1955,'4x4',1000,'mayo45-car05'),
 ('Volkswagen','1950 Beetle',1950,1975,'Coupe',1300,'mayo45-car06'),
 ('Ford','1964 Mustang',1964,1980,'Coupe',2400,'mayo45-car07'),
 ('Volvo','1974 240',1974,1995,'Wagon',6000,'mayo45-car08'),
 ('Volkswagen','1983 Golf',1983,2000,'Hatchback',9000,'mayo45-car09'),
 ('Toyota','1992 Camry',1992,2010,'Sedan',15000,'mayo45-car10'),
 ('Toyota','2000 Prius',2000,2020,'Hatchback',22000,'mayo45-car11'),
 ('Tesla','2012 Model S',2012,3999,'Sedan',60000,'mayo45-car12')]
# Period regular occupations join the existing interview, coworkers and pay code.
JOBS=[('Bounty Hunter',1800,1899,18000,30000,'Corporate'),
 ('Farmhand',1800,1910,18000,32000,'Corporate'),
 ('Typesetter',1800,1980,24000,48000,'Corporate'),
 ('Wheelwright',1800,1910,26000,50000,'Corporate'),
 ('Cooper',1800,1930,23000,45000,'Corporate'),
 ('Railway Porter',1830,1960,22000,42000,'Corporate'),
 ('Telegraph Operator',1844,1960,28000,54000,'Corporate'),
 ('Switchboard Operator',1880,1980,26000,47000,'Corporate'),
 ('Radio Technician',1920,1990,35000,72000,'Corporate')]
# All shipped careers receive an explicit rule. The default covers old trades;
# modern professions and fictional holiday jobs are dated below.
STARTS={
 'Actor':1895,'Singer':1800,'Disk Jockey':1935,'Model':1850,'Pornographer':1960,
 'Animator':1908,'Auto Mechanic':1886,'Baggage Handler':1919,'Biotechnologist':1973,
 'Brain Surgeon':1880,'Bus Driver':1895,'Business Analyst':1930,'Cashier':1879,
 'Chemical Engineer':1880,'Chiropractor':1895,'Computer Programmer':1945,
 'Database Administrator':1965,'Dental Hygienist':1913,'Detective':1840,
 'Driver':1886,'Electrician':1880,'Environmental Scientist':1960,
 'Fast Food Worker':1921,'Financial Analyst':1900,'Flight Attendant':1912,
 'Forensic Scientist':1900,'Graphic Designer':1920,'Internal Auditor':1900,
 'Lobbyist':1850,'Marriage Counselor':1930,'Microbiologist':1860,
 'Operations Analyst':1940,'Paralegal':1967,'Physical Therapist':1916,'Pilot':1909,
 'Policy Analyst':1940,'Psychiatrist':1850,'School Psychologist':1900,
 'Technical Support Specialist':1970,'Telemarketer':1960,'Travel Agent':1841,
 'Trucker':1910,'Fashion Designer':1850,'Wedding Planner':1900,'Nail Technician':1900,
 'Cameraman':1895,'Cat Behavior Consultant':1980,'Makeup Artist':1910,
 'Porn Set Janitor':1960,'Pornography Historian':1960,'Porta Potty Pumper':1940,
 'Roadkill Remover':1900,'Stuntman':1910,'Water Slide Tester':1970,
 'Plastic Surgeon':1917,'Set Designer':1895,'Mall Santa':1900,'Personal Trainer':1950,
 'Secret Shopper':1940,'PR Manager':1920,'Mall Cop':1950,'Game Designer':1970,
 'Game Quality Analyst':1980,'Cybersecurity Analyst':1980,'Cloud Systems Engineer':2006,
 'Data Analyst':1960,'User Experience Designer':1993,'Digital Illustrator':1984,
 'Motion Graphics Designer':1960,'Accessibility Specialist':1970,
 'Content Strategist':1995,'Community Manager':2000,'Sustainability Coordinator':1980,
 'Education Programme Coordinator':1920,'Student Services Officer':1900,
 'Audio Editor':1930,'Podcast Producer':2004,'Music Rights Coordinator':1900,
 'Live Sound Technician':1930,'Lighting Technician':1880,'Production Coordinator':1920,
 'Location Coordinator':1920,'Brand Designer':1920,'Market Research Analyst':1920,
 'Customer Experience Analyst':1980,'Quality Assurance Coordinator':1900,
 'Digital Archivist':1990,'Reality TV Producer':1948,'Race Engineer':1906,
 'Sports Physiotherapist':1930,'Community Moderator':1995,'F1 Driver':1950,
 'Reality TV Host':1948,'Train Driver':1825,'Mobile App Developer':2008,
 'Turkey Sexer':1925,'Cupid':3999,'Leprechaun':3999,'Easter Bunny':3999,
 'Vampire':3999,'Witch':3999,'Zombie':3999,'Pilgrim':3999,'Elf':3999,
 'Santa Claus':1880,'Reindeer Groomer':1880}
ENDS={'Chimney Sweep':1970,'Blacksmith':1980}
def career_window(name):
 for title,lo,hi,*_ in JOBS:
  if name==title:return lo,hi
 return STARTS.get(name,1800),ENDS.get(name,3999)
# Nominal purchasing power, not a claim to model every country's real inflation.
# Existing country pay multipliers still run. Linear interpolation avoids jumps.
PAY=[(1800,10),(1850,13),(1880,17),(1900,22),(1920,45),(1940,60),
     (1960,150),(1980,380),(2000,680),(2010,800),(2026,1000)]
def pay_factor(year):
 if year<=PAY[0][0]:return PAY[0][1]
 for (a,x),(b,y) in zip(PAY,PAY[1:]):
  if year<b:return x+(y-x)*(year-a)//(b-a)
 return 1000
# Price in cents, before the era multiplier; one purchase is one serving.
FOODS=[('Bread','bread',150),('Apples','apple',125),('Carrots','carrot',75),
       ('Eggs','egg',100),('Milk','glass-milk',125),('Corn','corn',75),
       ('Mushrooms','mushroom',150),('Peaches','peach',125)]
def food_cents(base,year):return max(1,base*pay_factor(year)//1000)
