"""Temporary native war palette; never overwrite the player's saved theme."""
import struct
from native_hooks import h
from native_v46.patch_native46 import COLOR_GROUPS

PALETTES=[
 dict(primary='#635c36',secondary='#777151',background='#f1e8ce',text='#393321'),
 dict(primary='#486257',secondary='#718573',background='#f5f0df',text='#303c32'),
 dict(primary='#344c45',secondary='#536572',background='#dddccb',text='#252e30'),
 dict(primary='#386579',secondary='#72988b',background='#f4eee0',text='#283b40')]

def hooks(b):
    # Match only the native theme item groups. Keep unlisted colors and all
    # neutral-country colors on the original selected theme implementation.
    old=b.resolved('v46_native_era_theme_colors');s=old['source']
    state=b.state+64
    head=f'adr x8,{state:#x}\nldr w25,[x8]\ncbz w25,war_theme_original1108\nmov w26,w0\n'
    aliases={'primary':'header','secondary':'accent','background':'background','text':'text'}
    for index,palette in enumerate(PALETTES,1):
        head+=f'cmp w25,#{index}\nb.ne war_palette_next1108_{index}\n'
        for group,ids in COLOR_GROUPS.items():
            for item in ids:head+=f'cmp w26,#{item}\nb.eq war_palette1108_{index}_{group}\n'
        head+='b war_theme_original1108\n'
        for group in COLOR_GROUPS:
            color=palette[{'paper':'background','cell':'background','alt':'background','ink':'text','secondary':'secondary','bar':'primary','light':'background','line':'secondary','accent':'primary'}[group]]
            head+=f'war_palette1108_{index}_{group}:\n'
            for k,ch in enumerate(bytes.fromhex(color[1:])+b'\xff'):
                bits=struct.unpack('<I',struct.pack('<f',ch/255))[0];head+=f'movz w9,#{bits&65535}\nmovk w9,#{bits>>16},lsl #16\nstr w9,[sp,#{256+k*16}]\n'
            head+='b return_custom\n'
        head+=f'war_palette_next1108_{index}:\n'
    head+='war_theme_original1108:\n'
    # Insert inside the full original hook frame; never enter its epilogue twice.
    marker=h.save()+'\n';assert s.startswith(marker)
    b.redirect(old['name'],s.replace(marker,marker+head,1))
    # This is on a frequent HUD boundary. Cache year and ISO country code;
    # never rebuild the history/sports/gameplay context here.
    from life_rework.history import WW1,WW2
    refresh='cbz x0,finish\nmov x27,x0\n'+f'bl {b.old["v45_current_year"]["stub"]:#x}\nmov w25,w0\n'+h.load_game()+'\nldr x0,[x8,#0x28]\ncbz x0,finish\nmov x1,xzr\nbl 0x2c38288\ncbz x0,finish\nmov x26,x0\nmov w20,#0\nldr x8,[x26,#0x90]\ncbz x8,country_cache1108\nldr w9,[x8,#16]\ncmp w9,#2\nb.ne country_cache1108\nldrh w20,[x8,#20]\nldrh w9,[x8,#22]\norr w20,w20,w9,lsl #16\ncountry_cache1108:\n'+f'adr x28,{state:#x}\nldr w9,[x28,#4]\ncmp w9,w25\nb.ne theme_recompute1108\nldr w9,[x28,#8]\ncmp w9,w20\nb.eq finish\ntheme_recompute1108:\nstr w25,[x28,#4]\nstr w20,[x28,#8]\nmov w19,#0\ncmp w25,#1914\nb.lt theme_phase_ready1108\ncmp w25,#1918\nb.lt phase_ww11108\ncmp w25,#1920\nb.le phase_after11108\ncmp w25,#1939\nb.lt theme_phase_ready1108\ncmp w25,#1945\nb.lt phase_ww21108\ncmp w25,#1947\nb.le phase_after21108\nb theme_phase_ready1108\nphase_ww11108:\nmov w19,#1\nb theme_country1108\nphase_after11108:\nmov w19,#2\nb theme_country1108\nphase_ww21108:\nmov w19,#3\nb theme_country1108\nphase_after21108:\nmov w19,#4\ntheme_country1108:\nmov x0,x26\nmov x1,xzr\nbl 0x2a27280\ncbz x0,theme_neutral1108\nmov x1,xzr\nbl 0x251f4a4\ncbz x0,theme_neutral1108\nmov x8,x0\n'
    for n,country in enumerate(sorted(set(WW1)|set(WW2))):
        refresh+=h.compare_key(country,'theme_country1108_'+str(n),'theme_next1108_'+str(n))+'\ntheme_country1108_'+str(n)+':\ncmp w19,#2\nb.gt theme_second1108_'+str(n)+'\n'
        if country in WW1:refresh+=f'cmp w25,#{WW1[country][0]}\nb.lt theme_neutral1108\nb theme_phase_ready1108\n'
        else:refresh+='b theme_neutral1108\n'
        refresh+='theme_second1108_'+str(n)+':\n'
        if country in WW2:refresh+=f'cmp w25,#{WW2[country][0]}\nb.lt theme_neutral1108\nb theme_phase_ready1108\n'
        else:refresh+='b theme_neutral1108\n'
        refresh+='theme_next1108_'+str(n)+':\n'
    refresh+='theme_neutral1108:\nmov w19,#0\ntheme_phase_ready1108:\nldr w9,[x28]\ncmp w9,w19\nb.eq finish\nstr w19,[x28]\nmov x0,x27\nmov x1,xzr\nbl 0x2f809bc\nb finish'
    fn=b.routine('military1108_refresh_theme',refresh)
    b.chain('military1108_theme_at_hud','v33_recover_hidden_top_menu_after_dialog',f'bl {fn:#x}\nb finish')
