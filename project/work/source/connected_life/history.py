"""Dated, factual headlines; year-end resolution matches the existing annual game."""
# The image is an era illustration; captions/provenance identify its real date.
EVENTS={
 1900:('A new century','Electric trams, newspapers and steamships connect growing cities. There are no social-media services.','early'),
 1914:('World War I begins','28 July: Austria-Hungary declares war on Serbia. Germany, Russia, France and Britain enter the conflict in the following days. Check Occupation → Military for your country’s service rules.','ww1'),
 1915:('A widening war','Italy joins the Allies in May. Fighting continues on the Western Front, at Gallipoli and on the Eastern Front. Rationing, letters and casualty reports affect life at home.','ww1'),
 1916:('Verdun and the Somme','The battles of Verdun and the Somme bring enormous losses. Britain introduces conscription; French and German armies are already mobilised. Canadian and Australian overseas forces follow different recruitment rules.','ww1'),
 1917:('The United States enters the war','6 April: the United States declares war on Germany. Russia experiences two revolutions. Recruitment, training and deployment remain separate steps.','ww1'),
 1918:('The armistice','11 November: the Western Front armistice takes effect. Other fronts have separate armistices. An estimated 15–20 million military personnel and civilians died during World War I. Recovery and demobilisation take time.','interwar'),
 1919:('A difficult peace','The Treaty of Versailles is signed on 28 June. Veterans return to a world changed by war and the influenza pandemic.','interwar'),
 1920:('The interwar years','Radio broadcasting grows while families rebuild after the war. Cars and clothing follow this period; modern digital services are unavailable.','interwar'),
 1929:('The Wall Street crash','Share prices collapse in October. The crash becomes part of a wider economic crisis; its effects differ between countries.','interwar'),
 1939:('World War II begins','1 September: Nazi Germany invades Poland. Britain and France declare war on 3 September. Your country’s entry date determines call-ups and military assignments.','ww2'),
 1940:('The war spreads across Europe','Germany invades Denmark, Norway and Western Europe. France signs an armistice in June. The Battle of Britain and the Blitz put civilians and aircrew in danger.','ww2'),
 1941:('The war becomes global','22 June: Germany invades the Soviet Union. 7 December: Japan attacks Pearl Harbor. The United States enters the war. These events do not instantly qualify a new recruit for combat.','ww2'),
 1942:('A world at war','Fighting intensifies in the Pacific, North Africa and the Soviet Union. Atrocities, including the Holocaust, devastate civilian communities. Unit losses in this game remain separate from historical death tolls.','ww2'),
 1943:('The tide turns','Germany’s forces surrender at Stalingrad. Axis forces surrender in North Africa, and the Allies invade Italy. Italy’s armistice in September divides the country and its armed forces.','ww2'),
 1944:('D-Day and liberation','6 June: Allied forces land in Normandy. Fighting continues across Europe and the Pacific. In the United States, the GI Bill is signed into law on 22 June.','ww2'),
 1945:('World War II ends','Germany surrenders in May. Atomic bombs devastate Hiroshima and Nagasaki in August. Japan announces surrender on 15 August and signs the formal instrument on 2 September. Estimates of total wartime deaths are roughly 70–85 million, mostly civilians.','postwar'),
 1946:('Homecoming and rebuilding','Demobilisation continues. Families reunite, shortages persist and veterans begin new work or education. Returning home does not erase service records or injuries.','postwar'),
 1948:('The Berlin airlift','The Soviet blockade of West Berlin leads to an Allied airlift. Aircraft carry food, fuel and other supplies to the city.','coldwar'),
 1957:('Sputnik reaches orbit','4 October: the Soviet Union launches Sputnik 1, the first artificial satellite. The space race becomes a major Cold War story.','coldwar'),
 1960:('Cold War tensions','The U-2 incident disrupts relations between the United States and the Soviet Union. Television, radio and newspapers carry the news; online social media does not exist.','coldwar'),
 1961:('The Berlin Wall','Construction of the Berlin Wall begins in August. East and West Berlin become symbols of the Cold War. A tank standoff follows at Checkpoint Charlie in October.','coldwar'),
 1962:('The Cuban Missile Crisis','In October, Soviet missiles in Cuba bring the United States and Soviet Union close to nuclear war. A negotiated settlement ends the immediate crisis.','coldwar'),
 1963:('A year of change and loss','The March on Washington takes place in August. President John F. Kennedy is assassinated in Dallas on 22 November. Communities respond with grief and uncertainty.','coldwar'),
 1965:('War and civil rights','The Vietnam War escalates. In the United States, the Voting Rights Act becomes law after a major civil-rights campaign.','coldwar'),
 1969:('People walk on the Moon','20 July: Apollo 11 lands on the Moon. Neil Armstrong and Buzz Aldrin walk on its surface while Michael Collins remains in lunar orbit.','moon'),
 1973:('The oil crisis','An oil embargo and supply disruptions bring rising fuel prices and shortages to many countries. Families adjust travel and spending.','retro'),
 1979:('Portable music','The first Sony Walkman goes on sale in Japan. Cassette players become part of everyday culture; smartphones and streaming apps are still in the future.','retro'),
 1980:('A changing media world','CNN begins broadcasting as a 24-hour television news channel. Home computers, arcades, cassettes and broadcast television shape the decade.','retro'),
 1981:('The personal-computer era','IBM introduces its personal computer. Computers become more common at work and in homes, without today’s social-media networks.','retro'),
 1983:('Cold War anxiety','The NATO exercise Able Archer takes place amid strained East–West relations. Television coverage and public debate reflect fears about nuclear conflict.','retro'),
 1985:('A serial-killer suspect is arrested','Richard Ramirez is arrested in Los Angeles in August after a series of violent crimes. News coverage focuses on public safety, victims and the investigation. This report gives no reward or fame for the crimes.','retro'),
 1987:('A speech in Berlin','President Ronald Reagan speaks at the Brandenburg Gate on 12 June, calling for the Berlin Wall to come down. The border remains in place for another two years.','retro'),
 1989:('The Berlin Wall opens','9 November: East Germany opens border crossings after weeks of protests. Crowds celebrate and families reunite.','coldwar'),
 1991:('The Soviet Union dissolves','The Soviet Union dissolves in December. Independent states emerge and the Cold War’s political order changes.','coldwar'),
 1995:('The web reaches more homes','Commercial internet access and the World Wide Web spread. This game’s social-media activities remain locked until 2010, as requested.','millennium'),
 1999:('Preparing for the millennium','Businesses and governments check computer systems for the Y2K date problem. Cities prepare for New Year celebrations.','millennium'),
 2000:('The turn of the millennium','Crowds welcome the year 2000. Home internet, mobile phones, CDs and DVDs are common in many places; availability still depends on country and income.','millennium'),
 2001:('September 11 attacks','11 September: hijacked aircraft strike the World Trade Center and the Pentagon; another crashes near Shanksville, Pennsylvania. Nearly 3,000 victims die. Communities mourn and support survivors and responders.','sept11'),
 2004:('Indian Ocean tsunami','26 December: a powerful earthquake near Sumatra triggers a tsunami across the Indian Ocean. More than 200,000 people die, and relief efforts reach devastated communities.','millennium'),
 2008:('The global financial crisis','Bank failures and a financial crisis bring job losses and economic hardship. The effects vary between countries and families.','millennium'),
 2010:('The digital age','Smartphones and online platforms become more prominent. Social-media activities now unlock in this game; each service can still have its own later launch date.','digital'),
 2011:('Livestreaming grows','Twitch launches in June as a gaming-focused livestreaming service. Online creators gain new ways to meet an audience.','digital'),
 2016:('Short videos and live audiences','Mobile video and live broadcasts become a larger part of online culture. What you post and how you treat viewers affect your reputation.','digital'),
 2020:('A global pandemic','COVID-19 disrupts schools, work and travel around the world. Communities adapt with public-health measures, remote learning and support for vulnerable neighbours.','modern'),
 2024:('The modern era','Digital communication, electric vehicles and rapid technological change shape daily life. Old items remain in the world, but current shops follow the year.','modern')}

# Fill otherwise-quiet war years and Cold War/retro decades with dated context,
# without inventing a specific historical incident or replaying an old headline.
PERIODS=[(1914,1917,'World War I continues','Letters, rationing and casualty lists bring the war into everyday life. Service options depend on your country, age and medical assessment.','ww1'),(1939,1944,'World War II continues','Newspaper reports, shortages and mobilisation shape the year. Check your country’s military briefing for service and home-front choices.','ww2'),(1960,1969,'Life during the Cold War','Space exploration, nuclear anxiety and changing popular culture appear in this year’s news. Local experiences differ by country.','coldwar'),(1980,1989,'The 1980s','Broadcast news, cassettes, home computers and changing fashions fill everyday life. This year also brings ordinary family, school and work choices.','retro')]

def headline(year):
 if year in EVENTS:return EVENTS[year]
 return next(((title,body,image)for lo,hi,title,body,image in PERIODS if lo<=year<=hi),None)

# Distinct annual stories avoid repeating a generic decade paragraph.
EVENTS.update({
 1964:('The Civil Rights Act','The United States Civil Rights Act is signed on 2 July. The law prohibits major forms of discrimination, following years of civil-rights organising.','coldwar'),
 1966:('Gemini and the space race','NASA completes the Gemini programme, developing the rendezvous and spaceflight experience used for Apollo. The space race remains a major news story.','moon'),
 1967:('A medical milestone','In December, a surgical team in Cape Town performs the first human-to-human heart transplant. Medicine continues to change, with difficult questions about care and risk.','coldwar'),
 1968:('A year of upheaval','Protests and political change affect many countries. Martin Luther King Jr. and Robert F. Kennedy are assassinated in the United States. Apollo 8 orbits the Moon in December.','moon'),
 1982:('The Falklands War','Argentina and Britain fight over the Falkland Islands in the South Atlantic. The conflict ends in June, leaving military personnel and civilians facing its consequences.','retro'),
 1984:('The Los Angeles Olympics','Los Angeles hosts the Summer Olympics. Athletes compete amid political tensions and a boycott led by the Soviet Union.','retro'),
 1986:('The Chernobyl disaster','An explosion and fire at the Chernobyl nuclear power plant cause a major disaster in April. Evacuations and radioactive contamination affect surrounding communities.','retro'),
 1988:('The Seoul Olympics','Seoul hosts the Summer Olympics. The event brings together athletes and viewers from around the world.','retro'),
 2002:('Euro notes and coins','Euro banknotes and coins enter circulation in participating European countries. Shops and households adjust to the new cash.','millennium'),
 2003:('The Human Genome Project','The Human Genome Project is declared complete in April. Its work helps researchers study human biology and inherited variation.','millennium'),
 2005:('London bombings','Bomb attacks on London’s transport system kill 52 victims on 7 July. Communities mourn and emergency services support survivors.','millennium'),
 2006:('Pluto is reclassified','The International Astronomical Union adopts a new planet definition. Pluto is classified as a dwarf planet, prompting public debate and renewed interest in astronomy.','millennium'),
 2007:('The smartphone changes','Apple introduces the iPhone. Touchscreen smartphones become more prominent, while the game’s social-media activities still wait until 2010.','digital'),
 2009:('A new influenza pandemic','The H1N1 influenza pandemic leads to public-health responses around the world. Communities and health services adapt to the outbreak.','millennium')})
