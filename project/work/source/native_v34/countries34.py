"""Extend tournaments with the 102 countries already shipped in game data.

Append to the existing IDs so saved nationality and active brackets survive.
The game country pool is a simulation pool, not a claim of FIFA membership.
"""
import json
from pathlib import Path
from native_hooks import h
from native_cups import EU, CA

ROOT = Path(__file__).resolve().parent

def pools():
    old=json.loads((ROOT.parent/'native_v13/assets/pools.json').read_text())
    nations=list(old['nationalpool']); names={n for n,f in nations}
    for country in old['countries']:
        if country['name'] not in names:
            nations.append([country['name'],'flag-'+country['code']])
    assert len(nations)==102 and nations[:63]==old['nationalpool']
    return nations

def address(record,label):
    lines=record['source'].splitlines();indices=[i for i,l in enumerate(lines)if l.strip()==label+':']
    assert len(indices)==1,(label,indices)
    return record['stub']+4*sum(bool(l.strip())and not l.strip().endswith(':')for l in lines[:indices[0]])

def patch(b):
    nations=pools(); europe=EU|{'ad','ee','mc'}
    record=next(r for r in b.manifest['hooks']if r['name']=='v18_saved_state')
    finish=address(record,'finish');loop=address(record,'draw_loop18')
    ready=address(record,'region_ready');invalid=address(record,'entry_region')
    # Preserve the existing club seed/pool. National seeds cover all 102 IDs.
    seed=b.routine('cup34_national_seed_bound',
        'mov w9,#63\nmov w10,#102\ncmp w28,#4\ncsel w9,w9,w10,lt\nstr x9,[sp,#8]\nb finish')
    regions=[]
    for name,accepted in [('euro',europe),('copa',CA)]:
        s=''
        for i,(nation,flag) in enumerate(nations):
            if flag[5:] in accepted:s+=f'cmp w25,#{i}\nb.eq {ready:#x}\n'
        s+=f'b {invalid:#x}'
        regions.append(b.add_code('cup34_'+name+'_entry_region',s))
    # Enter with the same registers as the retained draw loop, and leave
    # through its original saved-state epilogue. Existing club drawing stays.
    s=f'cmp w28,#4\nb.lt {loop+4:#x}\n'
    for i,(nation,flag) in enumerate(nations):s+=f'cmp w25,#{i}\nb.eq nation34_{i}\n'
    s+='b next34\n'
    for i,(nation,flag) in enumerate(nations):
        s+=f'nation34_{i}:\n'
        if flag[5:] not in europe:s+='cmp w28,#5\nb.eq next34\n'
        if flag[5:] not in CA:s+='cmp w28,#6\nb.eq next34\n'
        s+='cmp w25,w26\nb.eq next34\n'
        for j in range(1,4):
            s+=f'cmp w27,#{j}\nb.eq accepted34_{i}\n'+b.get(f'T{j}ID',default=-1)+'cmp w25,w24\nb.eq next34\n'
        s+=f'accepted34_{i}:\n'+b.text('Opponent',nation)+b.text('OriginalOpponent',nation)+b.text('OpponentFlag',flag)+'b selected34\n'
    s+='next34:\nadd w25,w25,#1\nmov w9,#102\nudiv w10,w25,w9\nmsub w25,w10,w9,w25\n'+f'b {loop:#x}\nselected34:\n'+b.put('CurrentOpponentID','w25')+'cbz w27,done34\n'
    for j in range(1,4):
        s+=f'cmp w27,#{j}\nb.ne store_next34_{j}\n'+b.put(f'T{j}ID','w25')+b.copy('Opponent',f'T{j}Name')+b.copy('OpponentFlag',f'T{j}Flag')+f'b stored34\nstore_next34_{j}:\n'
    s+='stored34:\nadd w27,w27,#1\nadd w25,w25,#1\nmov w9,#102\nudiv w10,w25,w9\nmsub w25,w10,w9,w25\ncmp w27,#4\n'+f'b.lt {loop:#x}\n'+b.copy('T1Name','Opponent')+b.copy('T1Flag','OpponentFlag')+b.get('T1ID')+b.put('CurrentOpponentID')+'done34:\n'+b.set('Phase',0)+f'b {finish:#x}'
    draw=b.add_code('cup34_draw_all_game_nations',s)
    source=record['source']
    old='cmp w25,#0\nb.lt entry_nation\ncmp w25,#63\nb.ge entry_nation'
    assert source.count(old)==1;source=source.replace(old,old.replace('#63','#102'))
    source=source.replace('region_euro:\ncmp w25,#2','region_euro:\nb '+hex(regions[0]),1)
    source=source.replace('region_copa:\ncmp w25,#0','region_copa:\nb '+hex(regions[1]),1)
    marker='mov w0,#0\nmov w1,#63\nmov x2,xzr\nbl 0x2e0b54c\nmov w25,w0\nmov w27,#0'
    assert source.count(marker)==1;source=source.replace(marker,marker.replace('mov w1,#63',f'bl {seed:#x}'))
    source=source.replace('draw_loop18:\ncmp w28,#4','draw_loop18:\nb '+hex(draw),1)
    b.update_record('v18_saved_state',source)
    (ROOT/'countries34.json').write_text(json.dumps(dict(nations=nations,europe=sorted(europe),copa=sorted(CA)),indent=2)+'\n')
