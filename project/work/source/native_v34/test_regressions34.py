"""Execute interrupted returns, relative interleaving and expanded cups.

Unity rendering, prefab setup, GC and coroutine scheduling are modeled API
boundaries. Actual ARM64 Actions and patched state handlers run with ASLR.
"""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from test_native34 import NewLife31,test_native,X
from test_navigation34 import Navigation
from test_entry34 import Entry
from patch_native34 import ICONS

def validate(binary):
    test_native.ROOT=ROOT;checks=0
    countries=json.loads((ROOT/'countries34.json').read_text())
    for bias in [0,0x1000000000]:
        for missing in [0x38,0x48]:
            m=Navigation(binary,bias);root,other=m.begin();m.map_open()
            state=m.d['states']['newlife24']['va']+bias
            saved=m.rq(m.manager+missing);m.q(m.manager+missing,0)
            assert m.run_routine('return_from_newlife_editor27',{})==0
            assert m.rw(state+60)==2 and not m.active[root+0x400];checks+=1
            m.q(m.manager+missing,saved)
            assert m.run_routine('return_from_newlife_editor27',{})==1
            assert m.rw(state+60)==0 and m.active[root+0x400]and not m.active[other+0x400];checks+=1
        for absent in [0x30,0x38,0x88]:
            m=Navigation(binary,bias);root,other=m.begin();m.map_open()
            pointer=m.rq(m.list_manager+absent);m.q(m.list_manager+absent,0)
            m.back();state=m.d['states']['newlife24']['va']+bias
            assert m.rw(state+60)==0 and m.active[root+0x400];checks+=1
            for off in [0x30,0x38]:
                if off!=absent:assert m.collections[m.rq(m.list_manager+off)]==[];checks+=1
            assert m.stock_cleanup_calls==0 and not m.rw(m.list_manager+0x80);checks+=1
        m=Navigation(binary,bias);root,other=m.begin();m.map_open();m.q(m.manager+0x40,0);m.back()
        assert m.active[root+0x400]and not m.rw(m.d['states']['newlife24']['va']+bias+60);checks+=1
        # Normal top-left Back, Close and row exit remain repeatable.
        for route in ['back','close','row']:
            m=Navigation(binary,bias);root,other=m.begin()
            for repeat in range(10):
                m.map_open()
                if route=='row':m.run('NativeReturn24',1,'newlife24')
                else:m.back(route)
                assert m.active[root+0x400]and not m.active[other+0x400]
                assert not m.rw(m.d['states']['newlife24']['va']+bias+60);checks+=1
        # Actual main-menu entry body after surrender/interrupted map.
        m=Entry(binary,bias)
        for reason in ['surrender','map_back','root_close','deceased']:
            stale=m.interrupted();m.main_newlife();item=m.prefabs[-1]
            assert item['cached_before']==[] and item['pending_before']==0 and item['canvas_active_before']==1;checks+=1
            assert not any(m.active.get(p+0x400,0)for p in stale);checks+=1
            m.root(item['page']);m.click(m.buttons[-7][0]);assert m.transitions[-1]==6;checks+=1
        # Profile data can be written by a different preview without changing
        # the selected MENU recipient. Opening the story refreshes it again.
        m=NewLife31(binary,bias);adult=m.alloc();child=m.alloc()
        m.names[adult]='Parent Example';m.names[child]='Child Example';m.w(adult+0x20,47);m.w(child+0x20,9)
        m.stub('v21_relationship_snapshot_Parent',{1:adult})
        context=m.d['states']['relationship34']['va']+bias
        assert len(m.handles)==2 and m.handles[m.rq(context)]==adult;checks+=1
        profile=m.alloc();m.table(profile);m.q(profile+0x170,child)
        m.stub('v21_native_child_profile_story',{19:profile})
        assert m.props['relationship21']['Age']==9;checks+=1
        m.stub('v34_refresh_selected_relative_on_story_open',{0:m.managed('genesis_v18_relationship21')})
        p=m.props['relationship21'];assert p['Age']==47 and p['Name']=='Parent Example'and 155<=p['Height']<=209;checks+=1
        for age in [0,3,9,16,18,42,89]:
            m.w(child+0x20,age);m.stub('v21_relationship_snapshot_Child',{1:child})
            assert len(m.handles)==2 and m.props['relationship21']['Age']==age;checks+=1
            m.stub('v34_refresh_selected_relative_on_story_open',{0:m.managed('genesis_v18_relationship21')})
            assert m.props['relationship21']['Age']==age and m.props['relationship21']['Name']=='Child Example';checks+=1
        replacement=m.alloc();m.w(replacement+0x20,0);m.q(m.game+0x28,replacement)
        m.stub('v34_refresh_selected_relative_on_story_open',{0:m.managed('genesis_v18_relationship21')})
        assert not m.handles and m.props['relationship21']['Name']=='Unavailable';checks+=1
        # Every selector's header receives its own valid game icon texture.
        m=NewLife31(binary,bias);c=m.root()
        for n,icon in enumerate(ICONS):
            m.click(m.buttons[n][0]);group=m.picker()
            image=m.rq(group+0x60)
            assert m.rq(image+0x58)==m.textures[m.sprites[icon]]and m.active[image+0x400]==1;checks+=1
            m.root(c)
        # Every game country can enter World Cup, with a unique group excluding
        # the player's team. Regional entry rules also cover appended IDs.
        m=NewLife31(binary,bias);m.professional(5,20);p=m.props['soccer_v12']
        for i,(name,flag)in enumerate(countries['nations']):
            p.update(Stage=0,Playing=1,CountryChosen=1,CountryPool=i,CountryName=name,CountryFlag=flag,LastWorld18=-4)
            m.rolls=[i];m.run('NativeCupStart18',4)
            assert p['EntryError18']==0 and p['TeamName']==name and p['TeamFlag']==flag;checks+=1
            ids=[p[f'T{j}ID']for j in range(1,4)];assert len(set(ids))==3 and i not in ids and all(0<=j<102 for j in ids);checks+=1
            for j in range(1,4):assert p[f'T{j}Name']==countries['nations'][p[f'T{j}ID']][0];checks+=1
            for kind,region,cooldown in [(5,'europe','LastEuro18'),(6,'copa','LastCopa18')]:
                p.update(Stage=0,Playing=1);p[cooldown]=-4;m.rolls=[i];m.run('NativeCupStart18',kind)
                if flag[5:] in countries[region]:
                    assert p['EntryError18']==0;checks+=1
                    assert all(countries['nations'][p[f'T{j}ID']][1][5:]in countries[region]for j in range(1,4));checks+=1
                else:assert p['EntryError18']==4;checks+=1
                m.rolls=[]
        # Tournament and match behavior outside nationality extension survives.
        p.update(Stage=0,Playing=1,LastClub18=-1,ClubPool18=1)
        m.run('NativeCupStart18',1);assert p['EntryError18']==0 and p['Stage']==1;checks+=1
        m.run('NativeMatchPlan',2);m.rolls=[0,99,0,99];m.run('NativeSoccerHalf',1)
        assert p['Phase']==1 and p['LastFor']==2 and p['LastAgainst']==0;checks+=1
    result=dict(passed=True,arm64_cases=checks,binary_sha256=hashlib.sha256(binary).hexdigest(),
        interrupted_return_retry=True,partial_list_cleanup=True,selected_relative_interleaving=True,
        new_life_context_replacement=True,all_102_game_countries=True,stable_existing_country_IDs=True,
        native_icon_texture_assignment=True,aslr_biases=[0,0x1000000000],
        Unity_GC_prefabs_and_rendering_modeled=True,device_runtime_tested=False)
    (ROOT/'regressions34_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)

if __name__=='__main__':validate(Path(sys.argv[1]).read_bytes())
