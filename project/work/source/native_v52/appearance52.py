"""Explicit genetic eyes, stage-safe IDs and shared native NPC/draft layers."""
import json,sys
from pathlib import Path
from collections import defaultdict
from native_hooks import h
from native_v42.patch_native42 import body
from native_v49.catalog49 import EYE_HEX,HEX,SKIN_HEX
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent

def hooks(b):
 idstr=b.old['v49_managed_style_id']['stub'];cid=b.old['v49_current_component_id']['stub']
 style=b.old['v43_set_component_id_colour_if_changed']['stub'];colour=b.old['v43_set_colour_if_changed']['stub']
 genetic=json.loads((SOURCE/'native_v49/portrait49_genetic_catalog.json').read_text())
 catalog=json.loads((SOURCE/'native_v49/portrait49_catalog.json').read_text())
 # Rebind the semantic style to the destination stage/gender. Native nearest
 # numeric ID is not an evolution rule for our independently imported layers.
 groups=defaultdict(dict);reverse={}
 for r in genetic:
  key=('trait',r['trait'],r['feature'],r.get('mood',-1))
  groups[key][r['gender'],r['stage']]=r['id'];reverse[r['id']]=key
 for r in catalog:
  if r['kind']=='hair':key=('hair',r['style'])
  elif r['kind']=='eyes':key=('eyes',r['left'],r['right'])
  else:continue
  groups[key][r['gender'],r['stage']]=r['id'];reverse[r['id']]=key
 numeric={int(ident):n for n,(ident,key)in enumerate(sorted(reverse.items()),1)}
 group_numbers={k:i for i,k in enumerate(groups,1)}
 # Parse exactly five decimal UTF-16 units. No managed pointer is retained.
 s='str xzr,[sp]\ncbz x0,finish\nldr w9,[x0,#16]\ncmp w9,#5\nb.ne finish\nadd x10,x0,#20\nmov w11,#0\nmov w12,#5\nmov w13,#10\nid52_parse:\nldrh w9,[x10],#2\nsub w9,w9,#48\ncmp w9,#9\nb.hi finish\nmadd w11,w11,w13,w9\nsubs w12,w12,#1\nb.ne id52_parse\nstr x11,[sp]\nb finish'
 parse=b.routine('v52_parse_portrait_id',s);b.parse52=parse
 s='str xzr,[sp]\nmov w19,w1\nmov w20,w2\n'+f'bl {parse:#x}\nmov w21,w0\n'
 # Group by numeric ranges where possible; exact IDs remain the allowlist.
 for i,(key,variants)in enumerate(groups.items(),1):
  ids=sorted(set(map(int,variants.values())));s+='\n'.join(f'cmp w21,#{v}\nb.eq id52_group_{i}'for v in ids)+'\n'
 s+='b finish\n'
 for i,(key,variants)in enumerate(groups.items(),1):
  s+=f'id52_group_{i}:\n'
  for (gender,stage),ident in variants.items():s+=f'cmp w19,#{stage}\nb.ne id52_next_{i}_{gender}_{stage}\ncmp w20,#{gender}\nb.ne id52_next_{i}_{gender}_{stage}\nmov w0,#{int(ident)}\nbl {idstr:#x}\nstr x0,[sp]\nb finish\nid52_next_{i}_{gender}_{stage}:\n'
  s+='b finish\n'
 remap=b.routine('v52_portrait_id_for_stage',s);b.remap52=remap
 s=f'cbz x4,finish\ncmp w1,#5\nb.hi finish\ncmp w3,#1\nb.hi finish\nmov x0,x4\nmov w2,w3\nbl {remap:#x}\ncbz x0,finish\nstr x0,[sp,#32]\nb finish'
 b.install('v52_preserve_style_across_age_and_gender',0x2f3bf74,s)
 # Retired v18 IDs overlap 36 currently authored mark IDs. Active resources
 # must win. The original retirement bridge remains for genuinely old IDs.
 active=set(reverse);retired=json.loads((SOURCE/'native_v29/hair_catalog.json').read_text())+json.loads((SOURCE/'native_v29/genetic_catalog.json').read_text())
 overlap=sorted(active&{r['name'].rsplit('-',1)[1]for r in retired})
 old=b.old['v20_retired_portrait_id_migration'];s='mov x8,x1\ncbz x8,finish\n'
 for n,ident in enumerate(overlap):s+=h.compare_key(ident,'finish',f'live52_next_{n}')+f'\nlive52_next_{n}:\n'
 # If active, skip the old migration and enter the displaced native prologue.
 s=s.replace("b finish\nlive52_next_", "b return_custom\nlive52_next_")
 s+='b finish'
 b.install('v52_active_ids_precede_retirement',old['stub'],s,ret=True)
 # The short skip stub has its own explicit return to the original entry.
 rec=b.hooks[-1];assert rec['source'].endswith('\nret')
 src=rec['source'][:-4]+'\n'+old['original']+f'\nb {old["resume"]:#x}'
 code=h.asm(src,rec['stub']);b.blob[b.off(rec['stub']):b.off(rec['stub'])+len(code)]=code;rec.update(source=src,length=len(code));b.cursor=(rec['stub']+len(code)+15)&~15
 # Ordinary custom-palette eye pairs are normalized to one iris colour.
 # The three explicit genetic eye styles retain their different patterns.
 s='str xzr,[sp]\ncbz x0,finish\nmov x27,x0\nmov w1,#1\nmov x2,xzr\nbl 0x2f3b1d8\ncbz x0,finish\n'+f'bl {cid:#x}\nbl {parse:#x}\nmov w19,w0\nmov w9,#80000\nsub w19,w19,w9\ncmp w19,#431\nb.hi finish\nmov w9,#12\nudiv w20,w19,w9\nmsub w22,w20,w9,w19\nmov w9,#6\nudiv w21,w20,w9\nmsub w23,w21,w9,w20\ncmp w21,w23\nb.eq finish\nmul w20,w21,w9\nadd w20,w20,w21\nmov w9,#12\nmul w20,w20,w9\nadd w20,w20,w22\nmov w9,#80000\nadd w0,w20,w9\n'+f'bl {idstr:#x}\nmov x23,x0\n'+b.string('FFFFFF')+f'mov x3,x0\nmov x2,x23\nmov x0,x27\nmov w1,#1\nbl {style:#x}\nstr x0,[sp]\nb finish'
 normal=b.routine('v52_match_ordinary_irises',s);b.normal52=normal
 # UpdateImage is also called for preview clones and NPCs. SetStyle helpers
 # are idempotent; normalization does not recursively render another portrait.
 old=b.old['v42_native_portrait_render_traits']
 src=body(old).replace('b finish',f'bl {normal:#x}\nb finish')
 b.redirect(old['name'],h.save()+'\n'+src+'\nfinish:\n'+h.restore()+'\n'+old['original']+f'\nb {old["resume"]:#x}')
 # Cache and serialization callers also invoke the hero apply routine
 # directly. Normalize at its successful tail, before its changed-bit return.
 priority=body(b.old['v50_resolve_selected_genetic_eyes'])
 # Keep the selected-genetic priority when relocating the underlying v49
 # body: its entry already contained a v50 trampoline. Also persist ordinary
 # equal-colour preferences so repeated cache reads do not toggle styles.
 end=priority.rindex('b finish')
 priority=priority[:end]+priority[end:]
 marker='cmp w19,#13\nb.ne finish';assert marker in priority
 priority=priority.replace(marker,'cmp w19,#13\nb.ne ordinary52_preferences',1)
 priority+='\nordinary52_preferences:\n'+b.ctx('custom49')+b.get('LeftEye','w19')+b.get('RightEye','w24')+'cbnz w19,ordinary52_left_ready\nmov w19,w24\nordinary52_left_ready:\ncbz w19,finish\n'+b.put('LeftEye','w19')+b.put('RightEye','w19')+'b finish'
 before=b.routine('v52_reconcile_saved_eye_preferences',priority)
 s='sub w19,w0,#600\ncmp w19,#6\nb.ls ordinary52_command\nsub w19,w0,#700\ncmp w19,#6\nb.hi finish\nordinary52_command:\n'+b.ctx('custom49')+b.put('LeftEye','w19')+b.put('RightEye','w19')+'b finish'
 b.chain('v52_single_ordinary_eye_colour_command','v49_apply_appearance_command',s)
 old=next(r for r in b.old.values()if 'baselines49_ready:'in r['source'])
 src=old['source'];tail='str x20,[sp]\nb finish';assert src.count(tail)==1
 src=src.replace(h.save()+'\n',h.save()+f'\nbl {before:#x}\n',1)
 src=src.replace(tail,f'mov x0,x27\nbl {normal:#x}\norr w20,w20,w0\n'+tail,1)
 b.redirect(old['name'],src)
 # Explicit trait renderer accepts any validated native face, including the
 # New Life preview and NPCs, without borrowing the hero's saved preferences.
 s='str xzr,[sp]\ncbz x0,finish\nmov x27,x0\nmov w25,w1\ncmp w25,#14\nb.hi finish\nmov x1,xzr\nbl 0x2f3cd90\nmov w26,w0\ncmp w26,#5\nb.hi finish\nmov x0,x27\nmov x1,xzr\nbl 0x2f40a9c\nmov w28,w0\ncmp w28,#1\nb.hi finish\nmov x0,x27\nmov x1,xzr\nbl 0x2f3f3c4\nmov w24,w0\ncmp w24,#2\nb.ls trait52_mood\nmov w24,#0\ntrait52_mood:\n'
 for n,r in enumerate(genetic):
  s+=f'cmp w25,#{r["trait"]}\nb.ne trait52_next_{n}\ncmp w26,#{r["stage"]}\nb.ne trait52_next_{n}\ncmp w28,#{r["gender"]}\nb.ne trait52_next_{n}\n'
  if r.get('mood',-1)>=0:s+=f'cmp w24,#{r["mood"]}\nb.ne trait52_next_{n}\n'
  s+=b.string(r['id'])+'mov x23,x0\n'+b.string('FFFFFF')+f'mov x3,x0\nmov x2,x23\nmov x0,x27\nmov w1,#{r["feature"]}\nbl {style:#x}\nstr x0,[sp]\nb finish\ntrait52_next_{n}:\n'
 # Albinism includes the native skin and hair layers, independently of the
 # hero-only preference container. The baseline preview restores these when
 # browsing another trait.
 albi='cmp w25,#7\nb.ne trait52_albinism\nldr x8,[x27,#0x20]\ncbz x8,finish\nmov w9,#1\nstr w9,[x8,#0x20]\nmov x0,x27\nmov x1,xzr\nbl 0x2f3efbc\nmov w9,#1\nstr x9,[sp]\nb finish\ntrait52_albinism:\ncmp w25,#4\nb.ne trait52_palette_done\n'
 for feature,c in [(3,'F5ECE5'),(5,'EAE2D0'),(6,'EAE2D0'),(8,'EAE2D0')]:albi+=b.string(c)+f'mov x2,x0\nmov x0,x27\nmov w1,#{feature}\nbl {colour:#x}\n'
 albi+='trait52_palette_done:\n'
 marker='trait52_mood:\n';assert marker in s;s=s.replace(marker,marker+albi,1)
 s+='b finish';b.trait52=b.routine('v52_apply_explicit_genetic_layer',s)
 # A controlled subset of NPCs receive authored assets once at creation;
 # their native emoji data, including scars, is saved with that person.
 # Creation from saved data uses a different constructor and is untouched.
 s=f'adr x8,{b.state52:#x}\nldr w9,[x8,#72]\ncbnz w9,finish\ncbz w21,finish\ncbz x25,finish\nmov x27,x25\n'+b.rng(1000,'w26')+'cmp w26,#220\nb.hs npc52_hair\nmov w9,#14\nudiv w10,w26,w9\nmsub w1,w10,w9,w26\nadd w1,w1,#1\nmov x0,x27\n'+f'bl {b.trait52:#x}\nnpc52_hair:\n'
 s+=b.rng(100,'w26')+'cmp w26,#20\nb.hs npc52_scar\nmov w9,#15\nudiv w10,w26,w9\nmsub w26,w10,w9,w26\nadd w26,w26,#1\nmov x0,x27\nmov x1,xzr\nbl 0x2f3cd90\nmov w24,w0\nmov x0,x27\nmov x1,xzr\nbl 0x2f40a9c\nmov w9,#12\nmul w26,w26,w9\nmov w9,#6\nmadd w26,w0,w9,w26\nadd w26,w26,w24\nmov w9,#78000\nadd w0,w26,w9\n'+f'bl {idstr:#x}\nmov x23,x0\n'+b.string('FFFFFF')+f'mov x3,x0\nmov x2,x23\nmov x0,x27\nmov w1,#8\nbl {style:#x}\nnpc52_scar:\nmov x0,x27\nmov x1,xzr\nbl 0x2f3cd90\ncmp w0,#2\nb.lt npc52_done\n'+b.rng(1000,'w26')+'cmp w26,#120\nb.hs npc52_done\nmov w9,#12\nudiv w10,w26,w9\nmsub w2,w10,w9,w26\nmov w9,#49101\nadd w2,w2,w9\nmov x0,x27\nmov w1,#8\nmov x3,xzr\nbl 0x2f36ae4\nnpc52_done:\nb finish'
 b.install('v52_npc_assets_before_native_serialization',0x2c9dbac,s)
 b.manifest['v52_active_retired_id_collisions']=overlap
 b.manifest['v52_custom_style_groups']=len(groups)
