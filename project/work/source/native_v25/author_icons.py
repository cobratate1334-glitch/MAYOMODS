"""Use the game's established emoji catalogue with topic-specific artwork."""
from content import *
interest=['face-monocle','film-frames','musical-note','basketball','soccer-ball','books','video-game','earth','man-artist','microscope','running-shoe','t-shirt','pan-of-food','airplane','face-smile','flag-checkered']
personalities=['face-hug','face-thinking','face-smile','face-quiet','face-monocle','chart-up','party-face','beating-heart','man-artist','face-cool','sports-medal','earth']
traits=['face-nerd','sports-medal','thought','heart-growing','running-shoe','books','megaphone','musical-notes','eyes','medal-first']
platform=['headphones','chat-bubble','iphone','camera','musical-note','megaphone','camera-movie','video-game','camera']
exact={'My Identity':'face-thinking','Personality & Traits':'face-nerd','Likes & Dislikes':'beating-heart','Height, Weight & Wingspan':'running-shirt','Mental Health & Support':'hospital','Height':'running-shirt','Weight':'balance-scale','Wingspan':'hand-raised','Storm Chaser':'v18-storm','Sports Manager':'chart-bar','Sports Coach':'man-teacher','Race Car Driver':'flag-checkered','Career Record':'chart-up','Season Dashboard':'basketball','Start a Season':'calendar','Play Next Game':'running-shirt','Season Statistics':'chart-bar','Team Records':'chart-up','Teammate Statistics':'sports-medal','Train':'running-shoe','Playoffs':'trophy','School Therapist':'man-teacher','Therapist':'chat-bubble','Mental Hospital':'hospital','Conditions':'brain','Support Record':'notebook','Classmate Crush Gossip':'chat-bubble','Relationship Agreements':'handshake','Multiple Relationships':'heart-revolving','Friends & Family':'family','Refresh Contacts':'handshake','Euros':'v19-euros','Copa América':'v19-copa','World Cup':'v12-worldcup','World Cup & Competitions':'v12-worldcup','Open World Cup & Competitions':'v12-worldcup','Choose My Nation':'earth','International Players':'sports-medal'}
# Registered tokens are validated before build; keep an available equivalent.
paths=json.loads(Path('analysis/base_resources.json').read_text());paths=paths.get('m_Container',paths)if isinstance(paths,dict)else paths
valid={p[0].split('/')[-1].removeprefix('a16_emoji-')for p in paths if p[0].startswith('emoji/normal/')}
valid|={'v21-chase-minivan','hero','v19-euros','v19-copa','v18-storm','v18-champions','v18-europa','v18-conference','v18-vinicius','v18-haaland','v18-bellingham','v19-messi','v19-ronaldo','v19-mbappe','v19-neymar','v19-yamal','v19-lingard'}
alias={'face-quiet':'face-thinking','hand-raised':'handshake','video-game':'joystick','camera-movie':'film-frames'}
def norm(icon):
 icon=alias.get(icon,icon)
 return icon if icon in valid else {'brain':'thought','joystick':'computer','family':'handshake'}.get(icon,'memo')
def topic(title,icon):
 if title in exact:return norm(exact[title])
 if title in ['Discord','Reddit','Facebook','Instagram','TikTok','Twitter','YouTube','Twitch','OnlyFans']:return norm(platform[['Discord','Reddit','Facebook','Instagram','TikTok','Twitter','YouTube','Twitch','OnlyFans'].index(title)])
 if icon not in ['memo','clipboard','busts-silhouette','heart','heart-red','books','lightbulb','whistle','race-car']:return norm(icon)
 key=title.lower()
 for terms,new in [('cybersecurity cloud computer software game designer','keyboard'),('artist illustrator art creative','man-artist'),('science research lab','microscope'),('coach training fitness sports','running-shoe'),('school college teacher education educator student literacy library','books'),('music musical podcast sound audio','headphones'),('movie film video actor drama production location lighting reality','film-frames'),('manager leadership recruiting recruitment event operations coordinator planner','chart-bar'),('data analyst quality assurance','chart-up'),('writer editor content','notebook'),('sustainability','earth'),('accessibility','handshake'),('museum exhibition archive archivist','classical-building'),('family parents friend partner','family'),('therapy concentration support anxiety depression adhd bipolar autism ocd ptsd dyslexia','chat-bubble'),('record statistics chart','chart-bar'),('social contact gossip follow community moderator','handshake'),('race racing driver car','flag-checkered')]:
  if any(t in key for t in terms.split()):return norm(new)
 return norm(icon)
for row in rows:
 k=row['ScenarioID'].split('.')[-1];icon=None
 for prefix,icons in [('interest',interest),('personality',personalities),('trait',traits)]:
  if k.startswith(prefix)and k[len(prefix):].isdigit():
   j=int(k[len(prefix):])-(1 if prefix=='personality'else 0);icon=icons[j]if j<len(icons)else None
 row['EmojiString']=norm(icon)if icon else topic(row['Title'],row['EmojiString'])
for name,raw in list(assets.items()):
 if not raw.startswith('{'):continue
 d=json.loads(raw)
 for it in d.get('Items',[])+sum([sec.get('Items',[])for sec in d.get('Sections',[])],[]):
  it['Icon']=topic(it['Title'],it.get('Icon','memo'))
  if name=='genesis_v18_interests':it['Icon']=norm(interest[d['Items'].index(it)])
  if name=='genesis_v18_personality':
   j=d['Items'].index(it);it['Icon']=norm((personalities+traits)[j])
 assets[name]=json.dumps(d,indent=2)
for reg in registry:reg[10]=topic(reg[9],reg[10])
# Give older added job/activity lists the same topic-specific treatment.
registry_text=BASE['genesis_feature_containers'];old=list(csv.reader(io.StringIO(registry_text)))
for r in old:
 if len(r)==16 and not r[0].startswith(('#','ContainerId')):r[10]=topic(r[9],r[10])
# content.finish applies the old entry icon mapping without touching identifiers.
ENTRY_ICONS={r[0]:topic(r[9],r[10])for r in old if len(r)==16 and not r[0].startswith(('#','ContainerId'))}
