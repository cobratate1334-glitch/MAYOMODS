"""Replace team badge lookup and only the exact original community CTA."""
import json
from pathlib import Path
from native_hooks import h
ROOT=Path(__file__).resolve().parent

def hooks(b):
    rows=json.loads((ROOT/'references/teams.json').read_text())
    # EmojiForSportsTeam is static, x0 is SimSportsTeam. Its native getter
    # returns DataSportsTeam; Index at +0x10 is verified independently from the
    # original data getter/CSV. Unknown/new teams keep the stock renderer.
    s='cbz x0,finish\nmov x1,xzr\nbl 0x2bcb384\ncbz x0,finish\nldr w25,[x0,#0x10]\n'
    for i,r in enumerate(rows):s+=f'cmp w25,#{r["index"]}\nb.ne badge_next_{i}\n'+b.string('mayomods1104/teams/'+str(r['index']))+'str x0,[sp]\nb return_custom\nbadge_next_'+str(i)+':\n'
    s+='b finish';b.install('life_rework_real_team_badges',0x2b8b6e0,s,ret=True)
    from native_v42.patch_native42 import ref,ref_init
    s='cbz x0,finish\nmov x19,x0\nldr w9,[x0,#16]\ncmp w9,#13\nb.lt finish\n'
    for i,ch in enumerate('mayomods1104/'):
        s+=f'ldrh w9,[x19,#{20+i*2}]\ncmp w9,#{ord(ch)}\nb.ne finish\n'
    s+=ref_init(0x5c56ad8)+'mov x0,x19\n'+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,finish\nstr x0,[sp]\nb return_custom'
    b.chain('life_rework_registered_offline_sprites','v55_full_owned_image_paths',s,ret=True)
    # CandyText.SetText receives a managed UTF-16 string in x1. Match only the
    # known CTA prefix, preserving every other journal, menu and text control.
    prefix='BitLife Community';s='cbz x1,finish\nldr w9,[x1,#16]\ncmp w9,#'+str(len(prefix))+'\nb.lt finish\n'
    for i,c in enumerate(prefix):s+=f'ldrh w9,[x1,#{20+2*i}]\ncmp w9,#{ord(c)}\nb.ne finish\n'
    s+=b.string('Modding community')+'str x0,[sp,#8]\nb finish';b.install('life_rework_home_community_label',0x3024244,s)
    # Redirect the original community endpoint, never arbitrary reddit/web links.
    s='cbz x0,finish\nmov x8,x0\n'
    for i,url in enumerate(['https://www.bitlifeapp.com/community','https://bitlifeapp.com/community','https://www.reddit.com/r/BitLifeApp/','https://www.reddit.com/r/BitLifeApp']):s+=h.compare_key(url,'community_redirect','community_next_'+str(i))+'\ncommunity_next_'+str(i)+':\n'
    s+='b finish\ncommunity_redirect:\n'+b.string('https://www.reddit.com/r/BitlifeModdingScene/')+'str x0,[sp]\nb finish';b.install('life_rework_community_url',0x553d724,s)
    # In the exact ButtonPress switch, field +0x44 == 0 calls
    # MainMenuManager.GetCommunityList (case 1 heirloom, 2 prayer, 3 custom
    # people). Replace that one proven case; preserve all other button types.
    s='cbz x0,finish\nldr w9,[x0,#0x44]\ncbnz w9,finish\n'+b.string('https://www.reddit.com/r/BitlifeModdingScene/')+'mov x1,xzr\nbl 0x553d724\nb return_custom'
    b.install('life_rework_home_community_opens_reddit',0x30158ac,s,ret=True)
