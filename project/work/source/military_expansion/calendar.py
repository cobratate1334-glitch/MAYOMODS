"""Apply the annual December-31 ceasefire boundary to retained native missions."""
from native_hooks import h

def hooks(b):
 old=b.resolved('life_rework_historical_context');source=old['source'];marker='\nfinish:\n';assert source.count(marker)==1
 cleanup=b.ctx('life_rework').replace(',finish',',history_done1108')+b.get('Year')+'cmp w24,#1918\nb.eq history_closed1108\ncmp w24,#1945\nb.ne history_done1108\nhistory_closed1108:\n'+b.set('War',0)+b.set('WarSide',0)+b.set('Deployed',0)+b.text('WarName','Postwar recovery')+b.text('Front','Combat assignments have closed. Review your service record and demobilisation notice.')+'history_done1108:\n'
 b.redirect(old['name'],source.replace(marker,marker+cleanup))
