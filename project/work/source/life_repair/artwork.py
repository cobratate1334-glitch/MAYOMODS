"""Typed, exact resource lookups and date-aware flag IDs, without cache mutation."""
from native_hooks import h
from native_v42.patch_native42 import ref_init,ref,compare_utf16
ICONS=['art','pet','microphone','school','trench','aircraft','crew','storm']
FLAGS=['de_nazi','de_imperial','jp_naval','jp','it_royal','us48','uk','fr','ru_imperial','ussr']


def hooks(b):
    mapping={**{'scene1106-'+n:'emoji/normal/scene1106-'+n for n in ICONS},**{'mayomods1106/flags/'+n:'mayomods1106/flags/'+n for n in FLAGS},**{'scene1106-flag-'+n:'mayomods1106/inlineflags/'+n for n in FLAGS}}
    s='cbz x0,finish\nmov x8,x0\n'
    for i,(key,path)in enumerate(mapping.items()):
        s+=h.compare_key(key,'art1106_'+str(i),'art1106_next_'+str(i))+f'\nart1106_{i}:\n'+ref_init(0x5c56ad8)+b.string(path)+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,finish\nmov x27,x0\nmov x1,xzr\nmov x2,xzr\nbl 0x5575198\ncbz w0,finish\nstr x27,[sp]\nb return_custom\n'+f'art1106_next_{i}:\n'
    s+='b finish';b.chain('repair_typed_activity_and_historical_art','v55_full_owned_image_paths',s,ret=True)
    # This API normally returns an emoji-cache ID. Return a registered image ID
    # for historical flags directly: never put shared asset textures inside the
    # mutable composite cache, which owns and destroys its generated images.
    s='cbz x1,finish\nmov x27,x1\n'+f'bl {b.old["v45_current_year"]["stub"]:#x}\nmov w26,w0\n'
    rules=[('de',['🇩🇪','flag-de','flag-DE','DE'],[(1871,1918,'de_imperial'),(1933,1934,'de_imperial'),(1935,1945,'de_nazi')]),('it',['🇮🇹','flag-it','flag-IT','IT'],[(1861,1946,'it_royal')]),('us',['🇺🇸','flag-us','flag-US','US'],[(1912,1959,'us48')]),('ru',['🇷🇺','flag-ru','flag-RU','RU'],[(1922,1991,'ussr')])]
    for i,(key,aliases,years)in enumerate(rules):
        for j,alias in enumerate(aliases):s+='mov x8,x27\n'+compare_utf16(alias,'flag1106_country_'+str(i),'flag1106_next_'+str(i)+'_'+str(j))+f'\nflag1106_next_{i}_{j}:\n'
        s+=f'b flag1106_country_done_{i}\nflag1106_country_{i}:\n'
        for n,(lo,hi,name)in enumerate(years):s+=f'cmp w26,#{lo}\nb.lt flag1106_year_next_{i}_{n}\ncmp w26,#{hi}\nb.gt flag1106_year_next_{i}_{n}\n'+b.string('scene1106-flag-'+name)+f'str x0,[sp]\nb return_custom\nflag1106_year_next_{i}_{n}:\n'
        s+=f'b finish\nflag1106_country_done_{i}:\n'
    s+='b finish';b.install('repair_header_flags_follow_calendar',0x2e01bf4,s,ret=True)
