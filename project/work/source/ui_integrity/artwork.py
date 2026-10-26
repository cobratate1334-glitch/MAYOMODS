"""Exact typed sprite loading and real native car imagery/availability."""
from native_hooks import h
from native_v42.patch_native42 import ref_init,ref
from native_v45.catalog45 import CARS
from ui_integrity.catalog import ART,REAL_CARS


def hooks(b):
    s='cbz x0,finish\nmov x8,x0\n'
    for i,key in enumerate(ART):
        path='mayomods1107/props/'+key
        s+=h.compare_key(path,'prop1107_'+str(i),'prop1107_next_'+str(i))+f'\nprop1107_{i}:\n'+ref_init(0x5c56ad8)+b.string(path)+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,finish\nmov x27,x0\nmov x1,xzr\nmov x2,xzr\nbl 0x5575198\ncbz w0,finish\nstr x27,[sp]\nb return_custom\n'+f'prop1107_next_{i}:\n'
    for i,(alias,early,late)in enumerate([('period_aircraft','ww1_plane','ww2_plane'),('period_armour','ww1_tank','ww2_tank')]):
        s+='mov x8,x0\n'+h.compare_key('mayomods1107/props/'+alias,'period_art1107_'+str(i),'period_art1107_next_'+str(i))+f'\nperiod_art1107_{i}:\nbl {b.old["v45_current_year"]["stub"]:#x}\ncmp w0,#1918\nb.gt period_art1107_late_{i}\n'+b.string('mayomods1107/props/'+early)+f'b period_art1107_load_{i}\nperiod_art1107_late_{i}:\n'+b.string('mayomods1107/props/'+late)+f'period_art1107_load_{i}:\nmov x27,x0\n'+ref_init(0x5c56ad8)+'mov x0,x27\n'+ref(0x5c56ad8,'x1')+'bl 0x3ed1638\ncbz x0,finish\nstr x0,[sp]\nb return_custom\n'+f'period_art1107_next_{i}:\n'
    s+='b finish';b.chain('integrity_supplied_sprite_resources','repair_typed_activity_and_historical_art',s,ret=True)
    # Model-level helper reads DataCarModel, not a guessed SimCar layout.
    def model_cases(mode):
        s='str xzr,[sp]\ncbz x0,finish\nmov x27,x0\n'
        for i,(make,model,year,art)in enumerate(REAL_CARS):
            s+='ldr x8,[x27,#0x10]\ncbz x8,finish\n'+h.compare_key(make,'car1107_make_'+str(i),'car1107_next_'+str(i))+f'\ncar1107_make_{i}:\nldr x8,[x27,#0x18]\ncbz x8,finish\n'+h.compare_key(model,'car1107_match_'+str(i),'car1107_next_'+str(i))+f'\ncar1107_match_{i}:\n'
            s+=(f'mov w9,#{year}\nstr x9,[sp]\n'if mode=='year'else b.string('mayomods1107/props/'+art)+'str x0,[sp]\n')+'b finish\n'+f'car1107_next_{i}:\n'
        if mode=='image':
            s+='ldr x8,[x27,#0x10]\ncbz x8,finish\n'+h.compare_key('Mayo','car1107_period','finish')+'\ncar1107_period:\nldr x8,[x27,#0x18]\ncbz x8,finish\n'
            for i,c in enumerate(CARS):
                art='prewar_car'if c['start']<1946 else'mustang'if c['start']<1975 else'modern_car'
                if c['start']>=2005 and c['luxury']:art='bugatti'
                s+=h.compare_key(c['model'],'car1107_period_'+str(i),'car1107_period_next_'+str(i))+f'\ncar1107_period_{i}:\n'+b.string('mayomods1107/props/'+art)+'str x0,[sp]\nb finish\n'+f'car1107_period_next_{i}:\n'
        return s+'b finish'
    year=b.routine('integrity_real_car_first_year',model_cases('year'))
    image=b.routine('integrity_native_car_image',model_cases('image'))
    s='cbz x0,finish\nmov x1,xzr\nbl 0x2b0cfc4\n'+f'bl {image:#x}\ncbz x0,finish\nstr x0,[sp]\nb return_custom'
    b.chain('integrity_native_car_badges','v45_car_emoji',s,ret=True)
    old=b.resolved('v45_car_allowed');s=old['source'];marker='str xzr,[sp]\ncbz x0,finish';assert marker in s
    extra='mov x28,x0\n'+f'bl {year:#x}\ncbz w0,integrity_stock_car\nmov w27,w0\nbl {b.old["v45_current_year"]["stub"]:#x}\ncmp w0,w27\ncset w9,ge\nstr x9,[sp]\nb finish\nintegrity_stock_car:\nmov x0,x28\n'
    b.redirect(old['name'],s.replace(marker,extra+marker,1))
