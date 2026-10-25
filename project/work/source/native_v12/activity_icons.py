"""Use existing native artwork with distinct, relevant icons per activity menu."""
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
base=json.load(open(sys.argv[1]));paths=json.load(open(sys.argv[2]));assets=json.loads((ROOT/'assets.json').read_text())
icons=set(p.rsplit('/',1)[-1].removeprefix('a16_emoji-')for p,v in paths if p.startswith('emoji/normal/'))
rules=[('back|return','left-arrow'),('record|profile|status|case|review','clipboard'),('study|education|class|tutor|homework','book'),('catalog|release','cd'),('studio|recording|vocal','mic-studio'),('song|write|lyric','musical-notes'),('mix|master|produce','headphones'),('concert|show|host|audience','microphone'),('artist|scout|cast','bust-silhouette'),('contract|offer|deal|sign','scroll'),('finance|income|salary|account','bank'),('season|standings|league|results','chart-bar'),('train|practice|exercise|fitness','running-shoe'),('match|play|fixture|soccer','soccer-ball'),('basketball','basketball'),('rugby','rugby-ball'),('race|drive|formula|f1','flag-checkered'),('qualify|speed|lap','stopwatch'),('setup|upgrade|repair|workshop','gear'),('navy|sea|ocean','anchor'),('air|fly|pilot','airplane'),('army|marines|combat|firefight','shield'),('mission|operation|deploy','map'),('duty|branch|service','medal-military'),('bomb|mine','bomb'),('tactic|strategy|command','compass'),('award|trophy|medal|champion','trophy'),('home|house|routine','house'),('parole|check.in','balance-scale'),('rehabilitation|therapy|health','heart'),('police|investigate|detective','magnifying-glass'),('computer|code|engineer|software','computer'),('design|art','paintbrush'),('project|build|work','hammer'),('plan|schedule','calendar'),('career|job|apply','briefcase')]
fallback=['memo','notebook','books','pencil','pen','fountain-pen','chart-up','chart-down','index-cards','file-cabinet','calendar','clock','compass','map','gear','hammer','toolbox','lightbulb','brain','shield','medal-first','sports-medal','trophy','stadium','running-shirt','running-shoe','bar-chart','scroll','joystick','camera','musical-score','keyboard','alarm-clock','balance-scale','earth','star','rocket','seedling','house','computer','briefcase','school','backpack','yearbook','musical-keyboard','musical-note','movie-camera','camera-no-flash','headphones']
changes={}
for n,t in base.items():
 if not n.startswith(('genesis_v7','genesis_v8','genesis_v9','genesis_music','genesis_record'))or not t.startswith('{'):continue
 try:d=json.loads(t)
 except ValueError:continue
 if 'ListID'not in d or 'Items'not in d:continue
 if n in assets:continue
 used=set();before=[]
 for it in d['Items']:
  old=it['Icon'];label=it.get('Title','')+' '+it.get('SecondLine','')
  candidates=[icon for exp,icon in rules if re.search(exp,label,re.I)]+[old]+fallback
  pick=next((x for x in candidates if x in icons and x not in used),None)
  assert pick,'insufficient icons '+n
  it['Icon']=pick;used.add(pick)
  if old!=pick:before.append(dict(title=it['Title'],before=old,after=pick))
 if before:assets[n]=json.dumps(d,ensure_ascii=False,indent=2);changes[n]=before
for n,t in assets.items():
 if t.startswith('{'):(ROOT/(n+'.json')).write_text(t+'\n')
(ROOT/'assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2))
(ROOT/'icon_changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2))
print(json.dumps(dict(menus=len(changes),changed_activity_icons=sum(map(len,changes.values())))))
