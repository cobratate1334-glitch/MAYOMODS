"""Preserve selected layers before age serialization and invalidate retained header copies."""
import json,re
from pathlib import Path
from native_hooks import h

def install(b,year):
 st=b.state
 # The header's retained copy was keyed solely by Texture2D identity. The
 # original renderer can update the same source object's pixels. A completed
 # hero render advances a scalar revision; an unchanged HUD read still reuses
 # its retained copy. No new per-frame pixel scan or unconditional clone.
 hero='cbz x0,finish\nmov x27,x0\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr x8,[x8,#0x80]\ncbz x8,finish\nldr x8,[x8,#0x30]\ncmp x8,x27\nb.ne finish\n'
 bump=b.routine('era1122_completed_hero_render_revision',hero+f'adr x8,{st:#x}\nldr w9,[x8]\nadd w9,w9,#1\nstr w9,[x8]\nb finish')
 b.install('era1122_header_after_actual_render',0x2f428f8,f'mov x0,x21\nbl {bump:#x}\nb finish')
 r=b.resolved('life_rework_validated_header_texture');s=r['source']
 needle='cmp x0,x19\nb.ne rework_header_clone\n';assert s.count(needle)==1
 check=f'adr x8,{st:#x}\nldp w9,w10,[x8]\ncmp w9,w10\nb.ne rework_header_clone\n'
 s=s.replace(needle,needle+check,1)
 marker='str x26,[sp]\nb finish\nrework_header_bad_copy:';assert s.count(marker)==1
 s=s.replace(marker,f'adr x8,{st:#x}\nldr w9,[x8]\nstr w9,[x8,#4]\n'+marker,1);b.redirect(r['name'],s)
 # SetAgeWithImageUpdate(false) bypasses UpdateImage and directly serializes
 # the evolved container. Reapply saved choices BEFORE that GetData call and
 # evict the hero's old native image. Keep original age evolution and save IDs.
 apply=b.old['v42_apply_current_hero_appearance']['stub']
 s=hero+f'mov x0,x27\nbl {apply:#x}\nmov x0,xzr\nbl 0x2f34138\ncbz x0,finish\nldr x1,[x27,#0x10]\nmov x2,xzr\nbl 0x2f4d2d8\nb finish'
 retain=b.routine('era1122_apply_before_age_serialization',s)
 b.install('era1122_age_save_keeps_genetic_layers',0x2c9eaec,f'mov x0,x19\ncbz x0,finish\nldr x0,[x0,#0x30]\nbl {retain:#x}\nb finish')
 era_hair=period_hair(b,year)
 # Normalize actual saved/rendered faces, not a separate portrait overlay.
 # Draft transactions and explicitly selected hero styles are excluded.
 r=b.resolved('v42_native_portrait_render_traits');s=r['source'];head=h.save()+'\n';assert s.startswith(head)
 b.redirect(r['name'],head+f'bl {era_hair:#x}\n'+s[len(head):])
 for name in ['v43_saved_appearance_before_data','v43_appearance_before_cached_emoji']:
  r=b.resolved(name);s=r['source'];head=h.save()+'\n';assert s.startswith(head)
  s=head+f'cbz x19,finish\nldr x0,[x19,#0x30]\nbl {era_hair:#x}\n'+s[len(head):];b.redirect(r['name'],s)
 r=b.resolved('v52_npc_assets_before_native_serialization');s=r['source'];needle='npc52_done:\nb finish';assert s.count(needle)==1
 s=s.replace(needle,f'npc52_done:\nmov x0,x25\nbl {era_hair:#x}\nb finish',1);b.redirect(r['name'],s)

def period_hair(b,year):
 """Choose from inspected existing stock components, retaining natural colour/texture."""
 names=json.loads((Path(__file__).resolve().parents[1]/'native_v49/assets.json').read_text())['a16_voltron_componentFilenames'].splitlines()
 rows={}
 for gender,g in enumerate(['male','female']):
  for stage in range(1,6):
   choices={}
   for n in names:
    m=re.fullmatch(r'a16_faces-'+g+r'-stage'+str(stage)+r'-hair-base(\d+)-(\d{5})\.png',n)
    if m and int(m[2])<78000:choices[int(m[1])]=m[2]
   rows[gender,stage]=choices
 assert all(3 in d if g==0 else 21 in d for (g,_),d in rows.items())
 early={0:[1,3,5,7,12,13,15,18,21,24,25],1:[11,21,22,24,25,26,27,29,30,31]}
 later={0:early[0]+[6,16,19,20,23],1:early[1]+[8,9,12,13,16,18,19,20,23,28]}
 catalog=[]
 s='str xzr,[sp]\ncbz x0,finish\nmov x27,x0\n'+f'adr x8,{b.state52:#x}\nldr x0,[x8,#24]\ncbz x0,no_draft_face1122\nbl 0x223e73c\ncbz x0,no_draft_face1122\nldr x8,[x0,#0x30]\ncmp x8,x27\nb.eq finish\nno_draft_face1122:\nbl {year:#x}\ncmp w0,#1960\nb.ge finish\nmov w28,w0\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr x8,[x8,#0x80]\ncbz x8,hair_person1122\nldr x8,[x8,#0x30]\ncmp x8,x27\nb.ne hair_person1122\n'+b.ctx('custom49')+b.get('Hair')+'cbnz w24,finish\nhair_person1122:\nmov x0,x27\nmov x1,xzr\nbl 0x2f3cd90\nmov w25,w0\ncmp w25,#1\nb.lt finish\ncmp w25,#5\nb.gt finish\nmov x0,x27\nmov x1,xzr\nbl 0x2f40a9c\nmov w26,w0\ncmp w26,#1\nb.hi finish\nmov x0,x27\nmov w1,#8\nmov x2,xzr\nbl 0x2f3b1d8\ncbz x0,finish\nmov x22,x0\n'+f'bl {b.old["v49_current_component_id"]["stub"]:#x}\nbl {b.old["v52_parse_portrait_id"]["stub"]:#x}\nmov w24,w0\n'
 for (gender,stage),d in rows.items():
  tag=f'hair_period_{gender}_{stage}'
  s+=f'cmp w26,#{gender}\nb.ne {tag}_next\ncmp w25,#{stage}\nb.ne {tag}_next\n'
  ids=[d[n]for n in early[gender]if n in d];laterids=[d[n]for n in later[gender]if n in d]
  for ident in ids:s+=f'mov w9,#{int(ident)}\ncmp w24,w9\nb.eq finish\n'
  s+=f'cmp w28,#1920\nb.lt {tag}_fallback\n'
  for ident in sorted(set(laterids)-set(ids)):s+=f'mov w9,#{int(ident)}\ncmp w24,w9\nb.eq finish\n'
  # HairType=1 is the original game's curly type. Preserve that texture;
  # otherwise use a centre/side part, never a hair-colour or skin rewrite.
  s+=f'{tag}_fallback:\nldr x8,[x27,#0x20]\ncbz x8,finish\nldr w9,[x8,#0x20]\ncmp w9,#1\nb.ne {tag}_straight\n'+b.string(d.get(1 if gender==0 else 27,d[3 if gender==0 else 21]))+f'b hair_period_set1122\n{tag}_straight:\n'+b.string(d[3 if gender==0 else 21])+f'b hair_period_set1122\n{tag}_next:\n'
  catalog.append(dict(gender=gender,stage=stage,early=ids,later=laterids,fallback=d[3 if gender==0 else 21],curly=d.get(1 if gender==0 else 27,d[3 if gender==0 else 21])))
 s+='b finish\nhair_period_set1122:\nmov x2,x0\nldr x3,[x22,#0x18]\ncbz x3,finish\nmov x0,x27\nmov w1,#8\n'+f'bl {b.old["v43_set_component_id_colour_if_changed"]["stub"]:#x}\nstr x0,[sp]\nb finish'
 b.manifest['era1122_hair_catalog']=catalog
 return b.routine('era1122_period_native_hair',s)
