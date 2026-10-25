"""Country/cohort baselines with stable individual spread and parent inheritance.

NCD-RisC supplies population means, not individual predictions. The simulation's
spread and rare tails are explicitly chosen gameplay parameters, not the data's
95% uncertainty intervals. Existing explicitly selected heights are preserved.
"""
import csv,hashlib,json,re
from pathlib import Path
from native_hooks import h
from native_v42.patch_native42 import body
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
ALIASES={'United States':'United States of America','Russia':'Russian Federation','South Korea':'Republic of Korea','North Korea':"Democratic People's Republic of Korea",'Czech Republic':'Czechia','Democratic Republic of the Congo':'DR Congo','Congo':'Congo','Taiwan':'Taiwan','Vietnam':'Viet Nam','Iran':'Iran','Syria':'Syrian Arab Republic','Laos':"Lao People's Democratic Republic",'Bolivia':'Bolivia','Venezuela':'Venezuela','Moldova':'Republic of Moldova','Tanzania':'United Republic of Tanzania','Turkey':'Turkey','Ivory Coast':"Cote d'Ivoire",'The Gambia':'Gambia','Cape Verde':'Cabo Verde','Swaziland':'Eswatini'}

def data():
 rows=list(csv.DictReader((ROOT/'country_height_source.csv').open()));out={}
 for r in rows:
  year=int(r['Year of birth'])
  if year not in [1900,1950,1996]:continue
  country=r['Country'];sex=0 if r['Sex']=='Men'else 1
  out.setdefault(country,{'country':country,'iso':r['ISO'],'means_cm':{}})['means_cm'][f'{sex}:{year}']=round(float(r['Mean height (cm)']),3)
 # Alias only an actual source name; missing aliases retain the neutral global
 # fallback instead of borrowing a guessed country's measurements.
 for name,source in ALIASES.items():
  if source in out and name not in out:out[name]={**out[source],'country':name,'source_country':source}
 report=dict(source_url='https://www.ncdrisc.org/downloads/height/NCD_RisC_eLife_2016_height_age18_countries.csv',
   source_sha256=hashlib.sha256((ROOT/'country_height_source.csv').read_bytes()).hexdigest(),
   attribution='NCD Risk Factor Collaboration (NCD-RisC). A century of trends in adult human height. eLife 2016;5:e13410. https://doi.org/10.7554/eLife.13410',
   source_countries=len({r['ISO']for r in rows}),cohorts=[1900,1950,1996],
   simulation=dict(sd_cm={'male':6.8,'female':6.3},rare_tail_rate=0.002,bounds_cm=[120,250],
      parents='85% sex-adjusted midparent mean plus 15% cohort mean, stable child variation',
      outside_observed_cohorts='Nearest endpoint; no invented historical or future country statistics'),countries=list(out.values()))
 (ROOT/'country_height_model52.json').write_text(json.dumps(report,indent=2)+'\n');return out

def expand(s):
 return re.sub(r'\badr (x\d+),\s*(0x[0-9a-f]+)',lambda m:f'adrp {m[1]}, {int(m[2],16)&~4095:#x}\nadd {m[1]}, {m[1]}, #{int(m[2],16)&4095}',s)

def hooks(b):
 countries=data()
 # One avalanche function prevents the old simple modulo from correlating
 # hobbies, physical measurements and every partner preference.
 s='mov w9,#0x352d\nmovk w9,#0x7feb,lsl #16\neor w0,w0,w0,lsr #16\nmul w0,w0,w9\nmov w9,#0xa68b\nmovk w9,#0x846c,lsl #16\neor w0,w0,w0,lsr #15\nmul w0,w0,w9\neor w0,w0,w0,lsr #16\nand w0,w0,#0x7fffffff\nstr x0,[sp]\nb finish'
 mix=b.routine('v52_mix_character_seed',s);b.mix52=mix
 s='str xzr,[sp]\ncbz x0,finish\nmov x1,xzr\nbl 0x2c44914\ncbz x0,finish\nldr w11,[x0,#16]\nadd x12,x0,#20\nmov w13,#5381\nheight52_hash:\ncbz w11,height52_hashed\nldrh w9,[x12],#2\nmov w10,#33\nmadd w13,w13,w10,w9\nsub w11,w11,#1\nb height52_hash\nheight52_hashed:\nmov w0,w13\n'+f'bl {mix:#x}\nstr x0,[sp]\nb finish'
 seed=b.routine('v52_person_seed',s);b.seed52=seed
 # SimPlace +0x90 is a COUNTRY CODE, not its display name. Resolve through
 # the native SimPlace.Country and DataCountry.Name getters. This is covered
 # by executing both getters in tests with different code/name fixtures.
 s='str xzr,[sp]\ncbz x0,finish\nmov x27,x0\nmov x1,xzr\nbl 0x2c3e7ac\ncbnz x0,country52_place_ready\nmov x0,x27\nmov x1,xzr\nbl 0x2c38288\ncountry52_place_ready:\ncbz x0,finish\nmov x1,xzr\nbl 0x2a27280\ncbz x0,finish\nmov x1,xzr\nbl 0x251f4a4\nstr x0,[sp]\nb finish'
 country=b.routine('v52_person_birth_country_name',s)
 # Repair an impossible living-parent age through the game's own setter.
 # Plausible ages and deceased parents remain unchanged. The correction is
 # stable per person and persists in the existing native life save.
 s=h.load_game()+'\nldr x27,[x8,#0x20]\ncbz x27,finish\nldr x26,[x8,#0x28]\ncbz x26,finish\nldr w25,[x26,#0x20]\n'
 for i,off in enumerate([0xa8,0xb8]):s+=f'ldr x26,[x27,#{off}]\ncbz x26,parent52_next_{i}\nldrb w9,[x26,#0x18]\ncbz w9,parent52_next_{i}\nldr w9,[x26,#0x20]\nadd w10,w25,#12\ncmp w9,w10\nb.ge parent52_next_{i}\nmov x0,x26\nbl {seed:#x}\nmov w9,#20\nudiv w10,w0,w9\nmsub w1,w10,w9,w0\nadd w1,w1,#18\nadd w1,w1,w25\nmov x0,x26\nmov x2,xzr\nbl 0x2c420f4\nparent52_next_{i}:\n'
 s+='b finish';repair=b.routine('v52_repair_impossible_parent_ages',s)
 b.chain('v52_parent_age_before_profile','measurements_at_current_age21',f'bl {repair:#x}\nb finish')
 # x0 country display name; w1 birth sex; w2 birth year. Return tenths of cm.
 s='mov w19,w1\nmov w20,w2\nmov w9,#1710\ncmp w19,#1\nmov w10,#1580\ncsel w9,w10,w9,eq\nstr x9,[sp]\ncbz x0,finish\nmov x8,x0\n'
 for i,(name,row)in enumerate(countries.items()):s+=h.compare_key(name,f'country52_{i}',f'country52_next_{i}')+f'\ncountry52_next_{i}:\n'
 s+='b finish\n'
 for i,(name,row)in enumerate(countries.items()):
  s+=f'country52_{i}:\n'
  for sex in [0,1]:
   m=[round(row['means_cm'][f'{sex}:{y}']*10)for y in [1900,1950,1996]]
   s+=f'cmp w19,#{sex}\nb.ne country52_{i}_{sex}_next\nmov w9,#{m[0]}\nmov w10,#{m[1]}\nmov w11,#{m[2]}\nb country52_interpolate\ncountry52_{i}_{sex}_next:\n'
  s+='b finish\n'
 s+='country52_interpolate:\ncmp w20,#1900\nb.le country52_low\ncmp w20,#1996\nb.ge country52_high\ncmp w20,#1950\nb.ge country52_recent\nsub w12,w20,#1900\nsub w10,w10,w9\nmul w10,w10,w12\nmov w12,#50\nsdiv w10,w10,w12\nadd w9,w9,w10\nb country52_low\ncountry52_recent:\nsub w12,w20,#1950\nsub w11,w11,w10\nmul w11,w11,w12\nmov w12,#46\nsdiv w11,w11,w12\nadd w9,w10,w11\nb country52_low\ncountry52_high:\nmov w9,w11\ncountry52_low:\nstr x9,[sp]\nb finish'
 mean=b.routine('v52_country_cohort_mean',s);b.mean52=mean
 # Actual native person getters supply age, sex and birthplace. The current
 # residence is used only if no birthplace is available.
 s='str xzr,[sp]\ncbz x0,finish\nmov x27,x0\n'+f'bl {seed:#x}\nmov w26,w0\nmov x0,x27\nmov x1,xzr\nbl 0x2c42454\nmov w25,w0\n'+f'bl {b.old["v45_current_year"]["stub"]:#x}\nldr w9,[x27,#0x20]\nsub w24,w0,w9\nmov x0,x27\nbl {country:#x}\nmov w1,w25\nmov w2,w24\n'+f'bl {mean:#x}\nmov w23,w0\n'
 # Sum six independently mixed uniforms; its bell-shaped spread is a
 # deterministic simulation parameter. Rare tails stay possible everywhere.
 s+='mov w22,#0\nmov w21,#0\nheight52_spread:\nmov w0,w26\nadd w0,w0,w21\n'+f'bl {mix:#x}\nmov w9,#201\nudiv w10,w0,w9\nmsub w9,w10,w9,w0\nsub w9,w9,#100\nadd w22,w22,w9\nadd w21,w21,#1\ncmp w21,#6\nb.lt height52_spread\nmov w9,#68\nmov w10,#63\ncmp w25,#1\ncsel w9,w10,w9,eq\nmul w22,w22,w9\nmov w9,#142\nsdiv w22,w22,w9\nadd w23,w23,w22\nmov w9,#1000\nudiv w10,w26,w9\nmsub w9,w10,w9,w26\ncmp w9,#2\nb.hs height52_bound\ncmp w9,#0\nmov w10,#280\ncsneg w10,w10,w10,ne\nadd w23,w23,w10\nheight52_bound:\nadd w23,w23,#5\nmov w9,#10\nsdiv w23,w23,w9\nmov w9,#120\ncmp w23,w9\ncsel w23,w23,w9,ge\nmov w9,#250\ncmp w23,w9\ncsel w23,w23,w9,le\nstr x23,[sp]\nb finish'
 sample=b.routine('v52_person_adult_height',s);b.height52=sample
 b.replace52('v51_parent_adult_height',f'bl {sample:#x}\nstr x0,[sp]\nb finish')
 # v51's explicit-selection provenance is retained. Recompute a legacy
 # automatic estimate once; subsequent profiles and ages reuse the result.
 old=b.resolved('v51_ensure_family_projection')
 s=b.ctx('life_v18')+b.get('HeightModel52','w19')+'cmp w19,#52\nb.eq finish\n'+b.get('HeightSource51','w19')+'cmp w19,#2\nb.eq explicit52_height\ncmp w19,#0\nb.ne family52_build\n'+b.get('AdultHeight','w19',178)+'cmp w19,#178\nb.eq family52_build\n'+b.set('HeightSource51',2)+'b explicit52_height\nfamily52_build:\n'
 s+=h.load_game()+'\nldr x27,[x8,#0x20]\ncbz x27,finish\nldr x26,[x8,#0x28]\ncbz x26,finish\nmov x0,x26\nmov x1,xzr\nbl 0x2c42454\nmov w28,w0\n'
 # Use the child's birth country/cohort as the missing-parent prior. No
 # guessed second parent or deterministic national ceiling is introduced.
 s+=f'bl {b.old["v45_current_year"]["stub"]:#x}\nldr w9,[x26,#0x20]\nsub w24,w0,w9\nmov x0,x26\nbl {country:#x}\nmov w1,w28\nmov w2,w24\nbl {mean:#x}\nmov w9,#10\nsdiv w22,w0,w9\nmov w19,w22\nmov w20,w22\ncbz w28,family52_male_prior\nadd w19,w19,#13\nb family52_parents\nfamily52_male_prior:\nsub w20,w20,#13\nfamily52_parents:\nldr x0,[x27,#0xa8]\nbl {sample:#x}\ncmp w0,#0\ncsel w19,w0,w19,ne\nldr x0,[x27,#0xb8]\nbl {sample:#x}\ncmp w0,#0\ncsel w20,w0,w20,ne\nadd w19,w19,w20\ncbnz w28,family52_female\nadd w19,w19,#13\nb family52_mean\nfamily52_female:\nsub w19,w19,#13\nfamily52_mean:\nmov w9,#2\nsdiv w19,w19,w9\nmov w9,#85\nmul w19,w19,w9\nmov w9,#15\nmadd w19,w22,w9,w19\nmov w9,#100\nsdiv w19,w19,w9\nmov x0,x26\nbl {seed:#x}\nmov w9,#15\nudiv w10,w0,w9\nmsub w9,w10,w9,w0\nsub w9,w9,#7\nadd w19,w19,w9\nmov w9,#120\ncmp w19,w9\ncsel w19,w19,w9,ge\nmov w9,#250\ncmp w19,w9\ncsel w19,w19,w9,le\n'
 s+=b.ctx('life_v18')+b.put('AdultHeight','w19')+b.set('HeightSource51',1)+b.text('HeightSourceName51','Family and country estimate')+b.set('HeightModel52',52)+'b finish\nexplicit52_height:\n'+b.set('HeightModel52',52)+'b finish'
 b.replace52(old['name'],s)
 # Repair the selected NPC's measurement BEFORE the existing growth curve.
 old=b.resolved('selected_relationship_details21');s=body(old)
 start=s.index('mov w9,#0\nadd w24,w23,w9\nand w24,w24,#0x7fffffff\nmov w9,#55\n')
 end=s.index(expand(b.get('AdultHeight','w25',178)),start)
 original=s[start:end]
 height_end=original.index(expand(b.put('AdultHeight')))+len(expand(b.put('AdultHeight')))
 remaining=original[height_end:]
 s=s[:start]+f'mov x0,x26\nbl {sample:#x}\nmov w24,w0\n'+b.put('AdultHeight')+remaining+s[end:]
 # Mix the seed before the independent preference/hobby selections.
 marker='relationship_hash_done21:\nand w23,w23,#0x7fffffff\n';assert marker in s
 s=s.replace(marker,marker+f'mov w0,w23\nbl {mix:#x}\nmov w23,w0\n',1)
 b.replace52(old['name'],s)
 # Refresh actual social contacts while their live SimPerson is available.
 # The old final sync loop used only a name hash and lost country/sex/age.
 prefs=['No height preference; connection matters most','Prefers a partner shorter than them','Prefers a partner taller than them','Values shared interests more than height','Values kindness and reliability more than height','Values ambition and creativity more than height']
 s='cbz x0,finish\nmov x26,x0\nmov w19,w1\n'+f'bl {repair:#x}\nmov x0,x26\nbl {sample:#x}\nmov w25,w0\nmov x0,x26\nbl {seed:#x}\nmov w27,w0\n'+b.ctx('social_v18')
 for slot in range(1,23):
  s+=f'cmp w19,#{slot}\nb.ne contact52_next_{slot}\nldr w24,[x26,#0x20]\n'+b.put(f'C{slot}Age')+b.put(f'C{slot}AdultHeight20','w25')+'mov w9,#6\nudiv w10,w27,w9\nmsub w28,w10,w9,w27\ncmp w28,#2\ncsel w24,w28,wzr,ls\n'+b.put(f'C{slot}HeightPref20')
  for n,pref in enumerate(prefs):s+=f'cmp w28,#{n}\nb.ne contact52_pref_{slot}_{n}\n'+b.text(f'C{slot}Preference20',pref)+f'b contact52_pref_done_{slot}\ncontact52_pref_{slot}_{n}:\n'
  s+=f'contact52_pref_done_{slot}:\nb finish\ncontact52_next_{slot}:\n'
 s+='b finish';refresh=b.routine('v52_consistent_live_contact_profile',s)
 b.replace52('v51_consistent_contact_heights','b finish')
 old=b.old['v18_saved_state'];s=old['source'];probe=s
 for slot in range(1,23):
  marker=f'profile_ready20_{slot}:\nmov w24,#1';assert s.count(marker)==1
  probe=probe.replace(marker,f'profile_ready20_{slot}:\nbr x15',1)
 a=h.asm(s,old['stub']);z=h.asm(probe,old['stub']);sites=sorted({i//4*4 for i,(x,y)in enumerate(zip(a,z))if x!=y});assert len(sites)==22
 for slot,off in enumerate(sites,1):b.install(f'v52_contact_country_height_{slot}',old['stub']+off,f'mov x0,x26\nmov w1,#{slot}\nbl {refresh:#x}\nb finish')
 b.manifest['v52_country_height_source']='country_height_model52.json'
