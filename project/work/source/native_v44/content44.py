"""Author the in-game era dealer using the shipped Genesis menu schema."""
import copy,csv,io,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent; SOURCE=ROOT.parent
sys.path[:0]=[str(SOURCE),str(SOURCE/'native_v29')]
from native_v29 import content as d
from catalog44 import ITEMS,ERAS
OWNER='era44'
p=lambda k:d.G(OWNER,k)
command=lambda v:d.seq(d.M(OWNER,'Action',0),d.M(OWNER,'Action',v))
scene=lambda k:d.S('era44_'+k)
go=lambda k:d.seq(command(1),scene(k))
HOME=go('home')

def author():
    base=json.loads((SOURCE/'native_v43/assets.json').read_text())
    d.BASE=base;d.ROOT=ROOT;d.assets={};d.schemas={};d.rows=[];d.registry=[]
    for k,v,lo,hi in [('BirthYear',0,0,3000),('Year',2026,1900,4000),('Era',3,0,3),
                      ('Action',0,0,999),('Head',0,0,27),('Mouth',0,0,27),
                      ('Selected',0,0,27),('Price',0,0,1000000),('Available',0,0,1),
                      ('Owned',0,0,1),('BuyStatus',0,0,6),('Regional',0,0,1),
                      ('NativeHead',0,0,1000000),('NativeHeadSaved',0,0,1)]:
        d.prop(OWNER,k,v,lo,hi)
    for k,v in [('EraName','Modern'),('ShopName','Mayo’s Streetwear'),
                ('ShopDescription','Caps, beanies and everyday streetwear.'),
                ('ItemName','Choose an accessory'),('StockLabel',''),('Country',''),
                ('HeadName','None'),('MouthName','None'),('Result','Welcome to Mayo’s Wardrobe.')]:d.text(OWNER,k,v)
    for item in ITEMS:
        for k,v,hi in [('Owned',0,1),('Price',0,1000000),('Available',0,1)]:d.prop(OWNER,k+str(item['id']),v,0,hi)
        d.text(OWNER,'Label'+str(item['id']),'Browse this item')
    for slot in range(1,4):
        for k in ['Head','Mouth']:d.prop(OWNER,f'Outfit{slot}{k}',0,0,27)
        d.prop(OWNER,f'Outfit{slot}Saved',0,0,1)

    def page(k,title,body,choices,icon='top-hat',stats=None):
        return d.add('era44_'+k,title,body,choices,icon,tables=d.table(**stats)if stats else None)
    route=d.logic([(f'({p("Era")} == {e})','BP_SHOW_LIST=genesis_v18_era44_stock'+str(e))for e in range(3)],'BP_SHOW_LIST=genesis_v18_era44_stock3')
    vintage=d.logic([(f'({p("Era")} == {e})','BP_SHOW_LIST=genesis_v18_era44_vintage'+str(e))for e in range(3)],'BP_SHOW_LIST=genesis_v18_era44_vintage3')
    page('home',p('ShopName'),p('ShopDescription')+' Purchased pieces stay yours as the years change.',[
        ('Browse current collection',route),('Vintage finds & regional collection',scene('vintage')),
        ('My wardrobe',go('wardrobe')),('Calendar & era',go('calendar'))],stats={'Year':p('Year'),'Era':p('EraName'),'Headwear':p('HeadName'),'Mouth':p('MouthName')})
    page('vintage','Vintage finds & regional styles','Older designs return on a three-year rotation. Cowboy hats are stocked in the US, Australia, Canada, Mexico, Brazil and Argentina.',[
        ('Browse vintage finds',vintage),('Regional cowboy collection','BP_SHOW_LIST=genesis_v18_era44_regional'),('Back',HOME)],stats={'Year':p('Year'),'Country':p('Country')})
    page('calendar','Your calendar','The calendar advances with your character’s age. Choose a starting year on the New Life screen. This calendar controls the accessory collections; the game’s other careers and events retain their existing rules.',[
        ('Back to the dealer',HOME)],icon='calendar',stats={'Year':p('Year'),'Birth_year':p('BirthYear'),'Era':p('EraName')})
    page('wardrobe','Mayo’s Wardrobe','Choose any owned item to wear it, even after its era has ended. Headwear and mouth accessories use separate slots.',[
        ('Owned accessories','BP_SHOW_LIST=genesis_v18_era44_owned'),('Remove accessories',scene('remove')),
        ('Saved outfits',scene('outfits')),('Back',HOME)],stats={'Headwear':p('HeadName'),'Mouth':p('MouthName')})
    page('remove','Remove accessories','Choose which slot to clear.',[
        ('Remove headwear',d.seq(command(400),go('wardrobe'))),('Remove mouth accessory',d.seq(command(401),go('wardrobe'))),('Remove both',d.seq(command(402),go('wardrobe'))),('Back',go('wardrobe'))])
    page('outfits','Saved outfits','Save three combinations for this character. Loading an empty slot leaves your current outfit in place.',[
        ('Outfit 1',scene('outfit1')),('Outfit 2',scene('outfit2')),('Outfit 3',scene('outfit3')),('Back',go('wardrobe'))])
    for n in range(1,4):
        page('outfit'+str(n),'Outfit '+str(n),'Save your current headwear and mouth accessory together, or wear the saved combination.',[
            ('Save current outfit',d.seq(command(600+n),scene('result'))),('Wear saved outfit',d.seq(command(610+n),scene('result'))),('Back',scene('outfits'))])
    for e,(name,year,shop,icon)in enumerate(ERAS):
        current=[i for i in ITEMS if i['era']==e and not i['regional']]
        older=[i for i in ITEMS if i['era']<e and not i['regional']]
        def tile(i,owned=False):
            row=d.tile(i['name'],d.seq(command(100+i['id']),scene('item')), 'top-hat'if i['slot']=='Headwear'else'face-thinking',p('Label'+str(i['id'])))
            row['IsVisible']='[gfc.era44.'+('Owned'if owned else'Available')+str(i['id'])+'=1]'
            return row
        d.menu('era44_stock'+str(e),name.upper()+' COLLECTION',[tile(i)for i in current]+[d.tile('Back to dealer',HOME,'left-arrow')])
        d.menu('era44_vintage'+str(e),'VINTAGE FINDS',[tile(i)for i in older]+[d.tile('Back to dealer',HOME,'left-arrow')])
    d.menu('era44_regional','REGIONAL COLLECTION',[tile(i)for i in ITEMS if i['regional']]+[d.tile('Back',HOME,'left-arrow')])
    # The game's existing GFC visibility filters hide all unowned pieces.
    d.menu('era44_owned','YOUR ACCESSORIES',[tile(i,owned=True)for i in ITEMS]+[d.tile('Back',go('wardrobe'),'left-arrow')])
    purchase=d.seq(command(2),scene('result'))
    equip=d.seq(command(3),scene('result'))
    try_on=d.logic([(f'(<hero:age> < 18) && (({p("Selected")} == 1) || ({p("Selected")} == 16) || ({p("Selected")} == 17))',scene('adult'))],d.seq(command(4),scene('preview')))
    page('item',p('ItemName'),p('StockLabel'),[
        ('Try on',try_on),('Buy & wear — '+p('Price'),purchase),('Wear owned item',equip),('Back',HOME)],stats={'Price':p('Price'),'Owned':p('Owned'),'Available':p('Available'),'Year':p('Year')})
    page('adult','Adult collection','Mouth accessories are available from age 18.',[('Back',HOME)])
    page('preview','Trying on: '+p('ItemName'),'This is a free preview. Your saved outfit is restored when you leave the preview.',[
        ('Buy & wear — '+p('Price'),purchase),('Wear owned item',equip),('Finish preview',d.seq(command(5),HOME))],icon='hero')
    page('result','Mayo’s Wardrobe',p('Result'),[('Continue',d.seq(command(5),HOME))],stats={'Headwear':p('HeadName'),'Mouth':p('MouthName')})
    # Activities entry points to the synchronising scenario rather than a
    # stale list. The native filter refreshes the entry on every open.
    d.menu('era44','ACCESSORIES DEALER',[d.tile('Enter '+p('ShopName'),HOME,'top-hat','Era collections, vintage finds and your wardrobe')],entry='T2',icon='top-hat',sub='Era collections; wardrobe; saved outfits')
    d.finish()
    generated=d.assets
    merged={**base,**generated}
    # d.finish emits the newly authored rows. Append them to the current v43
    # sheet so police, sports, family and other existing scenarios survive.
    for key in [d.FILE,'genesis_activities_v12']:
        old=list(csv.DictReader(io.StringIO(base[key])));new=list(csv.DictReader(io.StringIO(generated[key])))
        known={r['ScenarioID']for r in old};merged[key]=d.writecsv(old+[r for r in new if r['ScenarioID']not in known],d.HEADER)
    (ROOT/'assets.json').write_text(json.dumps(merged,indent=2)+'\n')
    (ROOT/'content44_changes.json').write_text(json.dumps({k:v for k,v in merged.items()if base.get(k)!=v},indent=2)+'\n')
    (ROOT/'catalog44.json').write_text(json.dumps(ITEMS,indent=2)+'\n')
    return merged
if __name__=='__main__':
    a=author();print('Authored era dealer; preserved prior scenarios:',len(a),flush=True)
