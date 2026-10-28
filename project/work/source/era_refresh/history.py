"""Short nineteenth-century headlines; the annual calendar resolves at year end."""
# Contemporary event photographs/archival prints are visual references, not AI.
EVENTS={
1804:('Napoleon becomes emperor','Napoleon is crowned emperor in Paris on 2 December. Europe faces years of war and political change.','1800'),
1807:('Britain bans the slave trade','Britain passes the Slave Trade Act. This bans the British trade in enslaved people. It does not yet abolish slavery across the empire.','1800'),
1815:('Waterloo and a new settlement','Napoleon is defeated at Waterloo on 18 June. The Congress of Vienna reshapes Europe after years of war.','1800'),
1825:('A new railway opens','The Stockton and Darlington Railway opens in England. Steam transport begins to change travel and trade.','1820'),
1830:('Steam links Liverpool and Manchester','The Liverpool and Manchester Railway opens. Scheduled passenger trains help connect two growing cities.','1820'),
1833:('Abolition across much of the British Empire','Britain passes the Slavery Abolition Act. It takes effect in 1834 with major limits and exceptions. The struggle against slavery continues.','1820'),
1837:('Victoria takes the throne','Victoria becomes queen of the United Kingdom. Industry and growing cities shape the new reign.','1840'),
1844:('A telegraph message travels','Samuel Morse sends a message between Washington and Baltimore. Long-distance electrical communication takes another step forward.','1820'),
1848:('Revolutions sweep Europe','Protests and uprisings spread across Europe. People demand political reform and better living conditions.','revolutions'),
1851:('The Great Exhibition','The Great Exhibition opens in London. Visitors see machinery and products from around the world.','1840'),
1859:('On the Origin of Species','Charles Darwin publishes On the Origin of Species. His account of evolution sparks wide debate.','1840'),
1861:('Civil war begins in the United States','Fighting begins at Fort Sumter in April. The war brings enormous suffering to soldiers and civilians.','1860'),
1863:('The Emancipation Proclamation','The proclamation declares freedom for enslaved people in areas still in rebellion against the United States. It does not end slavery everywhere.','1860'),
1865:('War ends and slavery is abolished','The American Civil War ends. The Thirteenth Amendment abolishes slavery in the United States except as punishment for crime.','1860'),
1869:('New routes across land and sea','The first transcontinental railroad is completed in the United States. The Suez Canal also opens this year.','1860'),
1876:('The telephone moves forward','Alexander Graham Bell receives a telephone patent in the United States. Inventors continue to develop electrical communication.','1880'),
1879:('Electric light draws a crowd','Thomas Edison demonstrates a practical incandescent lighting system. Earlier inventors also helped develop electric light.','1880'),
1883:('Krakatoa erupts','Krakatoa erupts in the Dutch East Indies. Tsunamis devastate nearby coasts and tens of thousands of people die.','1880'),
1886:('A motorcar is patented','Carl Benz patents his petrol-powered motorcar. Cars are rare and costly. Most people still rely on walking and animal or public transport.','1880'),
1889:('The Eiffel Tower opens','The Eiffel Tower opens for the Paris world fair. It becomes a striking symbol of engineering.','1880'),
1895:('X-rays reveal a hidden view','Wilhelm Röntgen discovers X-rays. Doctors soon explore their use in medical imaging.','1880'),
1896:('The modern Olympics begin','Athens hosts the first modern Olympic Games. Athletes compete in a revived international event.','1880')}
PERIODS=[(1800,1819,'Life in the early 1800s','Letters and printed newspapers carry news. Travel is slow. Local markets and family ties shape everyday life.','1800'),
 (1820,1839,'Steam and growing towns','Factories and steam transport expand in some regions. Their benefits and hardships reach people unevenly.','1820'),
 (1840,1859,'A changing world','Railways and telegraph lines spread. Newspapers report political change while many families still work on the land.','1840'),
 (1860,1879,'Railways and reform','Cities and transport networks grow. Campaigns for rights and political reform continue around the world.','1860'),
 (1880,1899,'An age of new inventions','Electric lighting and telephones spread in some cities. Most families still have no car. News arrives on paper.','1880')]

def select(year):
 if year in EVENTS:return EVENTS[year]
 return next((r[2:]for r in PERIODS if r[0]<=year<=r[1]),None)
