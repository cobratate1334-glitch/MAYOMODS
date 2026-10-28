"""Restore original V1 soccer bindings without undoing verified menu fixes."""
import copy,csv,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def originals():
 p=json.loads((ROOT/'references/V1_PROVENANCE.json').read_text());out={}
 for name,digest in p['text_assets'].items():
  text=(ROOT/'v1'/(name+'.json')).read_text();assert hashlib.sha256(text.encode()).hexdigest()==digest
  out[name]=json.loads(text)
 return out

def build(base):
 out={};old=originals()
 for name in ['genesis_v9_v12_soccer','genesis_v18_stars18']:
  data=json.loads(base[name]);by={x['TileID']:x for x in old[name]['Items']}
  for tile in data['Items']:
   source=by.get(tile['TileID'])
   if source is None:continue
   # Later cleanup replaced all six original competition logos with trophy.
   # These are original V1 resource IDs, not new placeholder images.
   tile['Icon']=source['Icon']
   # V1 refreshes the real saved competition/player state before opening a
   # profile. Retain its typed file and exact synchronization command.
   if name=='genesis_v18_stars18':tile['ActionList']=copy.deepcopy(source['ActionList'])
  text=json.dumps(data,indent=2)
  if text!=base[name]:out[name]=text
 # Entry cards and player profiles also lost the same original art. Both
 # retained scenario files contain these IDs and must agree. Do not roll back
 # their routes, outcomes, manual-event filters or parent-return receipts.
 raw=(ROOT/'v1/scenario_icons.json').read_text()
 provenance=json.loads((ROOT/'references/V1_PROVENANCE.json').read_text())
 assert hashlib.sha256(raw.encode()).hexdigest()==provenance['scenario_icons_sha256']
 icons=json.loads(raw)
 for name in ['genesis_activities_v12','genesis_activities_v18']:
  reader=csv.DictReader(io.StringIO(base[name]));fields=reader.fieldnames;rows=list(reader);seen=set()
  for row in rows:
   if row['ScenarioID'] in icons:
    row['EmojiString']=icons[row['ScenarioID']];seen.add(row['ScenarioID'])
  assert seen==icons.keys(),(name,icons.keys()-seen)
  stream=io.StringIO();writer=csv.DictWriter(stream,fields,lineterminator='\n');writer.writeheader();writer.writerows(rows)
  text=stream.getvalue()
  # The game splits CSV on LF before parsing: never add physical newlines
  # inside a record, even though Python's CSV reader would accept them.
  assert len(text.splitlines())==len(rows)+1
  if text!=base[name]:out[name]=text
 return out
