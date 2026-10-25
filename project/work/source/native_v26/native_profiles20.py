"""Stable fictional profile traits; native age and friendship duration are factual."""
PERSONALITIES=['Funny and warm','Loving and caring','Thoughtful and reserved','Outgoing and curious','Patient and supportive','Competitive and determined','Creative and independent','Playful and optimistic']
INTERESTS=[('Drawing','Become an animator','Art club and sketching'),('Chess','Become a researcher','Chess club'),('Soccer','Coach a youth team','Soccer team'),('Basketball','Play college basketball','Basketball team'),('Music','Compose film scores','School band'),('Science','Study engineering','Science club'),('Writing','Publish a novel','Creative writing club'),('Nature','Work in conservation','Hiking group'),('Cooking','Open a restaurant','Cooking with family'),('Dance','Perform on stage','Dance club'),('Gaming','Design video games','Game design club'),('Community work','Become a teacher','Volunteer group')]
BELIEFS=['Christian','Muslim','Jewish','Hindu','Buddhist','Atheist','Agnostic','Still exploring their beliefs']
STORIES=['Their family encourages their plans, and they are building confidence.','They are balancing family expectations with the future they want.','They recently moved neighborhoods and are finding a sense of belonging.','They have been helping a younger relative with homework.','They are saving for a course that matters to them.','They sometimes feel misunderstood at home, and value friends who listen.','They are proud of learning something difficult after months of practice.','They hope to travel and learn about other cultures.']
PREFS=['No height preference; connection matters most','Prefers a partner shorter than them','Prefers a partner taller than them']
def contact(b,j):
 q=f'C{j}';s='ldr w24,[x26,#0x20]\n'+b.put(q+'Age')
 if 5<=j<=10:s+='ldr w24,[x26,#0x188]\n'+b.put(q+'YearsFriends')
 else:s+=b.set(q+'YearsFriends',0)
 s+=b.get(q+'ProfileId20')+f'cmp w24,w23\nb.eq profile_ready20_{j}\n'+b.put(q+'ProfileId20','w23')
 def choices(key,values,salt):
  out=f'mov w9,#{len(values)}\nmov w10,#{salt}\nadd w24,w23,w10\nands w24,w24,#0x7fffffff\nudiv w10,w24,w9\nmsub w24,w10,w9,w24\n'
  for i,value in enumerate(values):out+=f'cmp w24,#{i}\nb.ne profile_next20_{j}_{key}_{i}\n'+b.text(q+key,value)+f'b profile_done20_{j}_{key}\nprofile_next20_{j}_{key}_{i}:\n'
  return out+f'profile_done20_{j}_{key}:\n'
 s+=choices('Personality20',PERSONALITIES,13)+choices('Hobby20',[v[0]for v in INTERESTS],29)+choices('Ambition20',[v[1]for v in INTERESTS],29)+choices('Clubs20',[v[2]for v in INTERESTS],29)+choices('Belief20',BELIEFS,71)+choices('Story20',STORIES,43)
 s+='mov w9,#65\nudiv w10,w23,w9\nmsub w24,w10,w9,w23\nadd w24,w24,#145\n'+b.put(q+'AdultHeight20')+'mov w9,#3\nudiv w10,w23,w9\nmsub w24,w10,w9,w23\n'+b.put(q+'HeightPref20')+choices('Preference20',PREFS,0)+f'profile_ready20_{j}:\n'
 # A stable preference offers only a small dating modifier, never a universal advantage.
 return s
