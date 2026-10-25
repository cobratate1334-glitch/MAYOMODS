from content import *
import author_life,author_social,author_sports,author_careers,author_cups,author_organise,author_icons
from hair_assets import append
append(assets)
from genetic_assets import append as add_genetics
add_genetics(assets)
# All feature entry aliases have a real saved container, even when they share data.
for row in registry:
 if row[0] not in schemas:prop(row[0],'Version',18,hi=18)
for owner in schemas:
 if not any(r[0]==owner for r in registry):registry.append([owner,owner,"","genesis_v18_defaults_"+owner,"","content","","","","","","",0,"","",""])
finish()
print('Authored',len(rows),'scenarios and',len(assets),'assets')
