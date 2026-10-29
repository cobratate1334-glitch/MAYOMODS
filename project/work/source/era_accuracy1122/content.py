"""Keep stable IDs and the original annual pools; add explicit era fields only."""
import csv,io,json
from life_rework.content import csv_text
from era_accuracy1122.catalog import ROOT_WINDOWS
def build(base):
 out={}
 for name,key in [('genesis_rework_defaults','JobCatalogRevision1122'),('genesis_v18_defaults_era45','CatalogRevision1122')]:
  rows=list(csv.DictReader(io.StringIO(base[name])));assert key not in {r['key']for r in rows}
  rows.append(dict(key=key,type='int',value='0',reset_on_ageup='',minimum='0',maximum='1122'));out[name]=csv_text(rows)
 # Native constructor filtering applies to parsed authored and stock lists;
 # existing callback IDs, annual pools and serialized tables stay identical.
 from life_repair.content import Author
 from life_rework.content import scene
 a=Author(base);town=json.loads(base['genesis_era_shops1121']);town.update(ListID='genesis_era_town1122',Title='TOWN LIFE')
 town['Items']=[a.tile('Around town',scene('town1119'),'native1119/1800s/icons/town_travel/general_store','Visit period places and take day work'),a.tile('Food & drink',scene('market_entry1121'),'bread','Food from your local market'),a.tile('Wanted & bounty notices',scene('wanted_entry1121'),'memo','Local cases and the sheriff’s notice board')]
 out['genesis_era_town1122']=json.dumps(town,indent=2)
 s=base['genesis_feature_containers'];prefix=s[:s.index('ContainerId,')];rows=list(csv.DictReader(io.StringIO(s[len(prefix):])));r=dict.fromkeys(rows[0],'');r.update(ContainerId='town_entry1122',DisplayName='Town life',InitDataSheet='genesis_v18_defaults_comment_entry47',AgeUpPriority='content',EntryMenu='Activities',EntryLabel='Town life',EntryEmoji='native1119/1800s/icons/town_travel/general_store',EntrySecondLine='1800s places, markets and day work',EntryOrder='2',EntryListID='genesis_era_town1122');rows.append(r);out['genesis_feature_containers']=prefix+csv_text(rows)
 return out
