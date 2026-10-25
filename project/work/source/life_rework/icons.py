"""Replace unresolved old icon aliases with existing bundled glyphs."""
import json
ALIASES={'speech-balloon':'mayomods49/icons/49-community','v18-storm':'cloud-thunder','v13-diplomacy':'handshake','v13-world-war':'earth','v12-worldcup':'trophy','v19-euros':'trophy','v19-copa':'trophy','v18-champions':'trophy','v18-europa':'trophy','v18-conference':'trophy'}
def fix(a,base):
 for row in a.rows:row['EmojiString']=ALIASES.get(row['EmojiString'],row['EmojiString'])
 for name,value in {**base,**a.assets}.items():
  if not name.startswith('genesis')or not value.lstrip().startswith('{'):continue
  d=json.loads(value);changed=False
  def visit(x):
   nonlocal changed
   if isinstance(x,dict):
    if x.get('Icon')in ALIASES:x['Icon']=ALIASES[x['Icon']];changed=True
    for v in x.values():visit(v)
   elif isinstance(x,list):
    for v in x:visit(v)
  visit(d)
  if changed:a.assets[name]=json.dumps(d,indent=2)
