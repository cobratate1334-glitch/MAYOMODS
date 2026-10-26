"""Native Sprite/Texture2D resource boundaries and owned picker art.

CandyButton.image (+0x30) is UnityEngine.UI.Image. Scenario BigImage is passed
raw from ScenarioDefinitionModel +0x110 to Scenario +0x40, then to the Texture2D
API at UIScenarioManager.SetupScenario +0x2f8c8ec. Resolve owned GFC image tags
at that boundary; a Sprite must never be returned from the Texture2D entry.
"""
from native_hooks import h
from native_v42.patch_native42 import ref, ref_init
from connected_life.era_catalog import ERAS


def prefix(value, yes, no):
    s = f'ldr w9,[x8,#16]\ncmp w9,#{len(value)}\nb.lt {no}\n'
    for i,c in enumerate(value):
        s += f'ldrh w9,[x8,#{20+2*i}]\ncmp w9,#{ord(c)}\nb.ne {no}\n'
    return s + f'b {yes}\n'


def hooks(b):
    # Load<Sprite> is the real generic method used in EmojiHub.ImageForEmojiString
    # at 0x2bade00. 0x5c56ad8 is its initialized MethodInfo metadata reference.
    # This helper returns only a Sprite, or NULL. It never touches portrait IDs.
    s = 'str xzr,[sp]\ncbz x0,finish\nmov x27,x0\nmov x8,x0\n'
    tags = [('<GFC.life_rework.NewsImage1110>','NewsImage1110'),
            ('[gfc.life_rework.NewsImage1110]','NewsImage1110'),
            ('<GFC.life_rework.MImage1109>','MImage1109'),
            ('[gfc.life_rework.MImage1109]','MImage1109')]
    for n,(tag,key) in enumerate(tags):
        s += h.compare_key(tag,'owned_tag_'+str(n),'owned_next_tag_'+str(n))
        s += f'\nowned_tag_{n}:\n'+b.ctx('life_rework')+b.string(key)
        s += 'mov x1,x0\nmov x0,x21\nmov x2,xzr\nbl 0x3059934\ncbz x0,finish\nmov x27,x0\nb owned_prefix\n'
        s += f'owned_next_tag_{n}:\n'
    s += 'owned_prefix:\nmov x8,x27\n'
    for n,p in enumerate(['native1109/','native1110/','native1111/']):
        s += prefix(p,'owned_load','owned_next_prefix_'+str(n))
        s += f'owned_next_prefix_{n}:\n'
    s += 'b finish\nowned_load:\n'+ref_init(0x5c56ad8)+'mov x0,x27\n'+ref(0x5c56ad8,'x1')
    s += 'bl 0x3ed1638\nstr x0,[sp]\nb finish'
    resolver = b.routine('playable_owned_sprite_resource',s)
    for name,site,is_texture in [('playable_sprite_provider',0x2bad908,False),('playable_texture_provider',0x2bad7a8,True)]:
        s = f'bl {resolver:#x}\ncbz x0,finish\n'
        if is_texture:
            s += 'mov x1,xzr\nbl 0x553b564\ncbz x0,finish\n'
        s += 'str x0,[sp]\nb return_custom'
        b.install(name,site,s,ret=True)
    # The old source put a photo on the scrolling journal. Keep all original
    # military palette hooks, but skip that single overlay on a fresh process.
    r=b.old['immersion1109_native_journal_background']
    b.redirect(r['name'],r['original']+f'\nb {r["resume"]:#x}')
    # Use the audited Sprite helper for era backgrounds. The actual native
    # original-image pointer and caption are retained until the option is added
    # to its layout, so this runs after parenting/layout initialization too.
    r=b.resolved('connected_style_owned_picker_buttons')
    s=r['source']
    old=ref_init(0x5c56ad8)+'mov x0,x27\n'+ref(0x5c56ad8,'x1')+'bl 0x3ed1638'
    # Manifest formatting has adrp/add expanded already; replace the exact
    # loading block by its stable labels rather than trying to match aliases.
    a=s.index('load_era_photo1110:\n')+len('load_era_photo1110:\n')
    z=s.index('\ncbz x0,genetic_style1110',a)
    s=s[:a]+f'mov x0,x27\nbl {resolver:#x}'+s[z:]
    b.redirect(r['name'],s)
    r=b.resolved('newlife31_add_rounded_option');s=r['source']
    marker='mov x25,x0\nmov x0,x25\nmov x1,x22\nbl '
    at=s.index(marker);end=s.index('\nldr x8,[x19,#0xa0]',at)
    s=s[:at]+'mov x25,x0\nstr x22,[sp,#0xf8]'+s[end:]
    at=s.rindex('\nb finish\nfinish:')
    style=b.resolved('connected_style_owned_picker_buttons')['stub']
    s=s[:at]+f'\nmov x0,x25\nldr x1,[sp,#0xf8]\nbl {style:#x}'+s[at:]
    b.redirect(r['name'],s)
