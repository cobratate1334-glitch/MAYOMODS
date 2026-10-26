"""Preserve the aspect of mod-owned BigImage textures in stock scenario cards."""
from native_hooks import h
from playable_repair.visuals import prefix


def hooks(b):
    # UIScenarioManager constructs CandyImageOptions(texture,width,height).
    # The stock caller supplies 360 x 360 for ANY picture. Our imported news
    # photos are wide; those arguments made them square on the owner's phone.
    # Change just these two scalar arguments for owned art, not stock images,
    # icons, portraits, caches or any shared Texture/Sprite pixels.
    s='cbz x22,finish\ncbz x23,finish\nldr x8,[x22,#0x40]\ncbz x8,finish\n'
    for n,p in enumerate(['native1109/','native1110/','native1111/','native1112/','<GFC.life_rework.NewsImage1110>','<GFC.life_rework.MImage1109>']):
        s+=prefix(p,'owned_card_size','size_next_'+str(n))+'size_next_'+str(n)+':\n'
    s+='b finish\nowned_card_size:\nmov x0,x23\nmov x1,xzr\nbl 0x5557b04\nmov w19,w0\ncmp w19,#1\nb.lt finish\nmov x0,x23\nmov x1,xzr\nbl 0x5557b40\ncmp w0,#1\nb.lt finish\nscvtf s2,w19\nscvtf s3,w0\nmov w9,#640\nscvtf s0,w9\nfdiv s1,s3,s2\nfmul s1,s1,s0\nmov w9,#440\nscvtf s4,w9\nfcmp s1,s4\nb.le owned_size_ready\nfdiv s0,s4,s1\nmov w9,#640\nscvtf s2,w9\nfmul s0,s0,s2\nfmov s1,s4\nowned_size_ready:\nstr s0,[sp,#0x100]\nstr s1,[sp,#0x110]\nb finish'
    b.install('device_owned_image_aspect_at_original_card_constructor',0x2f8c974,s)
    # If the owned image cannot resolve, skip the image item entirely. Do not
    # leave a square of blank space or return a Sprite from a Texture2D API.
    s='cbnz x0,finish\ncbz x22,finish\nldr x8,[x22,#0x40]\ncbz x8,finish\n'
    for n,p in enumerate(['native1109/','native1110/','native1111/','<GFC.life_rework.NewsImage1110>','<GFC.life_rework.MImage1109>']):
        s+=prefix(p,'missing_owned_image','missing_next_'+str(n))+'missing_next_'+str(n)+':\n'
    s+='b finish\nmissing_owned_image:\nb return_custom'
    b.install('device_skip_missing_owned_big_image',0x2f8c8f0,s,custom_resume=0x2f8c9d4)
    years={1914:'native1110/photos/ww1',1915:'native1111/news1112/gallipoli',1916:'native1111/news1112/somme',1918:'native1110/photos/interwar',1939:'native1110/photos/ww2',1940:'native1111/news1112/blitz',1941:'native1111/news1112/pearl',1944:'native1111/news1112/dday',1945:'native1110/photos/postwar',1969:'native1110/photos/moon',1989:'native1111/news1112/berlin',1999:'native1110/photos/millennium',2000:'native1110/photos/millennium',2001:'native1110/photos/sept11',2005:'native1111/news1112/london2005',2020:'native1111/news1112/covid2020'}
    s=b.ctx('life_rework')+b.get('NewsFlag1110')+'cmp w24,#1\nb.ne finish\n'+b.get('Year','w25')
    for year,path in sorted(years.items()):s+=f'cmp w25,#{year}\nb.eq news_photo_{year}\n'
    s+=b.text('NewsImage1110','')+'b finish\n'
    for year,path in sorted(years.items()):s+=f'news_photo_{year}:\n'+b.text('NewsImage1110',path)+'b finish\n'
    fn=b.routine('device_picture_for_actual_news_year',s)
    row=b.resolved('connected_prepare_native_annual_queues');s=row['source'];mark='\nfinish:\n';assert s.count(mark)==1
    b.redirect(row['name'],s.replace(mark,mark+f'bl {fn:#x}\n'))
