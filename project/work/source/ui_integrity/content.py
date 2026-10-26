"""Repair physical-record CSV contracts and connect period retail to native menus."""
import csv,io,json,re
from life_repair.content import Author
from life_rework.content import csv_text,p,scene,menu,logic,seq,set_,inc
from ui_integrity.catalog import ITEMS


def build(base):
    a=Author(base)
    home=scene('period_shop1107')
    for key,label,year,cost,age,body in ITEMS:
        owned='Owned1107_'+key;a.prop(owned,0,0,1)
        a.prop('Use1107_'+key+'Age',-1,-1,999);a.prop('Use1107_'+key+'Used',0,0,1)
        unavailable=scene('period_unavailable1107')
        guard=((f'({p("Year")} < {year}) || (<hero:age> < {age})',unavailable),)
        bought=a.outcome('purchase1107_'+key,'Bought '+label+' for $'+str(cost)+'. It is now in your personal collection.',scene('item1107_'+key),['BP_BANK_BALANCE=-'+str(cost),set_(owned,1)],extra=guard+((f'({p(owned)} == 1)',scene('period_owned1107')),(f'({p("NativeBank1105")} < {cost})',scene('funds'))))
        use=a.outcome('use1107_'+key,('Used the vape. The nicotine made you feel unwell; your health fell.'if key=='vape'else'Used your '+label+'. '+body),scene('item1107_'+key),[],native=14 if key=='vape'else 111,extra=guard+((f'({p(owned)} != 1)',scene('period_not_owned1107')),),quota=('Use1107_'+key,1))
        a.page('item1107_'+key,label,body+' Available from '+str(year)+', age '+str(age)+'. Price: $'+str(cost)+'.',[("Buy · $"+str(cost),bought),('Use it',use),('Back to shop',home)],'mayomods1107/props/'+key,stats=[('Owned',p(owned))])
        a.edit('item1107_'+key)['BigImageString']='mayomods1107/props/'+key
    # Paginated era-filtered offers: locked pages give an explanation, and all
    # actual mutations independently recheck year, age, money and ownership.
    buckets=[(1900,['typewriter','rotary']),(1920,['radio','typewriter','rotary']),(1981,['desktop','radio','rotary']),(1983,['mobile','desktop','radio']),(1989,['laptop','mobile','desktop']),(2007,['iphone','laptop','mobile']),(2016,['vr','iphone','laptop']),(2017,['switch','iphone','vr']),(2020,['ps5','switch','iphone'])]
    a.page('period_shop1107','Technology & style','Browse objects available in your current year. Purchases use your bank balance. Your collection survives aging up.',[
        ('Devices and games',logic([(f'({p("Year")} >= {year})',scene('device_shelf1107_'+str(year)))for year,_ in reversed(buckets)],scene('period_unavailable1107'))),
        ('Fashion',logic([(f'({p("Year")} >= 1990)',scene('item1107_modern_hat')),(f'({p("Year")} >= 1930)',scene('item1107_retro_hat')),(f'({p("Year")} >= 1920)',scene('item1107_vintage_hat'))],scene('period_unavailable1107'))),
        ('Adult counter',logic([(f'({p("Year")} < 2007) || (<hero:age> < 18)',scene('period_unavailable1107'))],scene('item1107_vape'))),
        ('Back to shopping',menu('genesis_v8_shopping_v8'))],'mayomods1107/props/iphone',stats=[('Year',p('Year'))])
    for first,keys in buckets:
        items=[next(row for row in ITEMS if row[0]==key)for key in keys]
        choices=[]
        for key,label,year,cost,age,body in items:
            choices.append((label,logic([(f'({p("Year")} < {year}) || (<hero:age> < {age})',scene('period_unavailable1107'))],scene('item1107_'+key))))
        choices.append(('Back to shop',home))
        a.page('device_shelf1107_'+str(first),'Devices and games','The shelf follows the current year. Select an item to see its price and age requirement.',choices,'mayomods1107/props/'+keys[0],stats=[('Year',p('Year'))])
    for key,title,body in [('period_unavailable1107','Unavailable in this life','This item has not been introduced yet, or you are below its minimum age. No money was spent.'),('period_owned1107','Already in your collection','You already own this item. You can use it once each year.'),('period_not_owned1107','You do not own this item','Buy it first. No money or progress changed.')]:
        a.page(key,title,body,[('Back to shop',home)],'memo')
    a.add_tile('genesis_v8_shopping_v8','Technology & style',home,'mayomods1107/props/iphone','Phones, games and accessories for your year')
    a.add_tile('genesis_v18_era44','Technology & style',home,'mayomods1107/props/iphone','Browse objects available in your current year')
    # These hubs must reject an out-of-period or childhood entry as well as
    # guarding the individual actions; no 2026 infant gets wartime commands.
    locked=scene('war_unavailable1107')
    a.page('war_unavailable1107','No wartime posting','World-war service opens during 1914–1918 or 1939–1945, for adults in a participating country. Your current life has no posting in those campaigns.',[('Back to game','')],'memo')
    names={'war_hub1106','war_service1106','war_missions1106','command_home1106','command_start1106','command_economy1106','command_targets1106','command_targets1106_1','command_targets1106_2','command_targets1106_3','war_briefing','war_draft'}
    for row in a.rows:
        key=row['ScenarioID'].rsplit('.',1)[-1]
        if key not in names:continue
        for i in range(1,5):
            if not row.get(f'Choice{i}_Text')or re.search(r'\b(back|close|return)\b',row[f'Choice{i}_Text'],re.I):continue
            old=row.get(f'Choice{i}_AdvancedLogic','');target=json.loads(old)if old else row.get(f'Choice{i}_RouteTo','')
            row[f'Choice{i}_RouteTo']='';row[f'Choice{i}_AdvancedLogic']=json.dumps(logic([(f'({p("War")} == 0) || ({p("WarSide")} == 0) || (<hero:age> < 18)',locked)],target))
    # Contextual historical equipment art belongs to service, not a modern life.
    for row in a.rows:
        key=row['ScenarioID'].rsplit('.',1)[-1];art=None
        if 'trench_'in key:art='trench'
        elif 'flight_'in key:art='period_aircraft'
        elif key.startswith('command_offer1106_'):art='period_armour'
        elif key in ['war_service1106','war_record']:art='helmet'
        elif key=='war_country1106':art='rifle'
        elif key in ['war_propaganda1106','spy_briefing1106']:art='radio_field'
        if art:row['EmojiString']='mayomods1107/props/'+art;row['BigImageString']='mayomods1107/props/'+art
    a.assets['genesis_life_rework']=csv_text(a.rows,list(a.header));a.assets['genesis_rework_defaults']=csv_text(a.schema)
    # Annual controllers need their continuations locally; keep all manual
    # entries under the schema-clamped impossible filter.
    annual=list(csv.DictReader(io.StringIO(base['genesis_rework_annual1105'])))
    entry=[r for r in annual if r.get('IsAgeUpScenario','').lower()=='true']
    a.assets['genesis_rework_annual1105']=csv_text(entry+[dict(r,IsAgeUpScenario='false',Filter='[gfc.life_rework.AnnualContinuation1106=1]')for r in a.rows])
    return repair_csv({**base,**a.assets},base)


def repair_csv(assets,base):
    """The native reader splits at LF BEFORE parsing quoted columns.

    Preserve paragraphs as the game's existing <br> markup. Do not serialize
    literal LF inside a quoted field, even though Python's csv module accepts it.
    """
    out={k:v for k,v in assets.items()if k not in base or v!=base[k]}
    for name,value in assets.items():
        if name=='genesis_entity_defs':
            start=next(i for i,line in enumerate(value.splitlines())if line.startswith('EntityType,Kind,AutoFillMin,DeathScenarioFile,'));value='\n'.join(value.splitlines()[start:])
        elif not value.startswith('ScenarioID,'):continue
        rows=list(csv.DictReader(io.StringIO(value)));header=list(rows[0])
        if name=='genesis_entity_defs':rows=[r for r in rows if not str(r.get('EntityType','')).lstrip().startswith(('#','//'))]
        for row in rows:
            assert None not in row,(name,'malformed field count')
            for k,v in row.items():
                row[k]=(v or '').replace('\r\n','\n').replace('\r','\n').replace('\n','<br>')
        normalized=csv_text(rows,header)
        if name=='genesis_entity_defs':normalized=normalized.split('\n',1)[1]
        if normalized!=base.get(name):out[name]=normalized
    return out
