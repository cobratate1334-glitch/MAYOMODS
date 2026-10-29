"""Explicit retail/work windows. Dates are conservative game rules, not a global census."""
from era_life1121.catalog import STARTS as OLD_STARTS, ENDS, JOBS
STARTS={**OLD_STARTS,'Technical Writer':1940,'Insurance Agent':1800,
 'Singer':1889,'Film Director':1895,'Film Producer':1895,'TV Producer':1948,
 'Firefighter':1800,'Photographer':1840,'Dentist':1800,'Veterinarian':1800,
 'Psychologist':1879,'Acupuncturist':1800,'Stockbroker':1800,
 'Casino Worker':1863,'Private Investigator':1833,'Marine Biologist':1850,
 'Interior Designer':1900,'Receptionist':1850,'Pet Groomer':1870,
 'Financial Advisor':1900,'Male Stripper':1900,'Exotic Dancer':1900,
 'Event Coordinator':1920,'Research Coordinator':1920,'Museum Educator':1900,
 'Archive Technician':1900,'Literacy Coordinator':1900,'Learning Support Officer':1950,
 'Library Programme Coordinator':1900,'Operations Coordinator':1920,
 'Recruitment Coordinator':1900,'Training Coordinator':1920,'Logistics Planner':1900,
 'Exhibition Coordinator':1900,'Luxury Asset Manager':1980,
 'Independent Music Promoter':1900,'Conservation Officer':1850}
SPECIAL_YEAR=2000
ROOT_ENDS={'Town life':1899}
ROOT_WINDOWS={
 'Special Careers':SPECIAL_YEAR,'Special careers':SPECIAL_YEAR,
 'Freelance Gigs':SPECIAL_YEAR,'Freelance gigs':SPECIAL_YEAR,
 'Social Media':2010,'Social media':2010,'Roblox':2006,
 'Luxury':2000,'Race Car Garage':1950,'Race car garage':1950,
 'Zoo':1828,'Casino':1863,'Cryptocurrency':2009,'Crypto':2009,
 'Air Force':1909,'Air force':1909,'Space Force':2019,
 'Online Dating':1995,'Online dating':1995,'Dating App':2000,
 'Plastic Surgery':1917,'Plastic surgery':1917,'Surrogacy':1985,
 'IVF':1978,'DNA Test':1985,'DNA test':1985,'Internet':1991,
 'Driving License':1903,'Driving licence':1903,'Driver’s License':1903,
 'Pilots License':1909,'Pilot’s License':1909,'Boat License':1900,
 'Go Viral':2010,'Streaming':2011,'Fame':1900,
 'Casino Owner':2000,'Secret Agent':2000,'Astronaut':2000,
 'Model':2000,'Dealer':2000,'Street Hustler':2000,
}
ROOT_TITLES=['ASSETS','Assets','ACTIVITIES','Activities','OCCUPATION','Occupation',
 'OCCUPATIONS','Occupations','MILITARY','Military','LICENSES','Licenses',
 'MIND & BODY','Mind & Body','LOVE','Love','INVESTMENTS','Investments',
 'SPECIAL CAREERS','Special Careers','SHOPPING','Shopping']
PART_STARTS={
 'Amusement Park Attendant':1890,'Arcade Assistant':1970,'Armpit Sniffer':1950,
 'Barista':1901,'Barnyard Sperm Extractor':1930,'Beverage Cart Attendant':1950,
 'Bike Shop Mechanic':1860,'Bowling Alley Assistant':1900,'Brand Ambassador':1950,
 'Cafeteria Worker':1890,'Camp Counselor':1880,'Campus Tour Guide':1900,
 'Car Wash Attendant':1914,'Chicken Sexer':1925,'Collections Specialist':1900,
 'Crossing Guard':1920,'Delivery Driver':1900,'Department Store Associate':1850,
 'Donut Maker':1847,'Fitness Instructor':1950,'Flower Shop Assistant':1830,
 'Go-Go Dancer':1964,'Grocery Bagger':1916,'Gym Receptionist':1950,
 'Hotel Front Desk Clerk':1850,'Ice Cream Scooper':1850,'Lab Assistant':1850,
 'Laser Tag Assistant':1984,'Lawn Mower':1830,'Lifeguard':1890,
 'Mall Kiosk Worker':1950,'Mall Santa':1900,'Movie Theater Cashier':1905,
 'Mystery Shopper':1940,'Newspaper Delivery Person':1833,'Office Assistant':1850,
 'Personal Trainer':1950,'Pool Cleaner':1900,'Pool Towel Attendant':1900,
 'Product Tester':1920,'Research Assistant':1850,'Resident Assistant':1900,
 'School Bus Driver':1910,'Social Media Manager':2006,'Valet':1900,
 'Video Game Tester':1980,'Yoga Receptionist':1960,'Homework Club Assistant':1900,
 'Campus Media Assistant':1950,'Student Helpdesk Assistant':1980,
 'Research Survey Assistant':1920,'Digital Archive Assistant':1990,
 'Board Game Cafe Assistant':1990,'Recording Studio Runner':1930,
 'Podcast Editing Assistant':2004,'Festival Information Assistant':1900,
 'Community Centre Receptionist':1900,'Charity Shop Assistant':1890,
 'Repair Cafe Assistant':2009,'Aquarium Visitor Assistant':1853,
 'Mobile Device Setup Assistant':2000,'Photo Booth Attendant':1925,
 'Sports Centre Attendant':1900,'Homework Resource Assistant':1900,
 'Campus Accessibility Assistant':1970,'Cinema Attendant':1905,
 'Bike Rental Assistant':1869,'Garden Centre Assistant':1900,
}
def career_window(name):
 for title,lo,hi,*_ in JOBS:
  if name==title:return lo,hi
 return STARTS.get(name,1800),ENDS.get(name,3999)
def part_window(name):return PART_STARTS.get(name,1800),3999
