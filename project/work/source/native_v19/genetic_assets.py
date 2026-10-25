"""Original vector portrait variants in the stock 500px Voltron coordinate space."""
import json
from pathlib import Path
import cairosvg
ROOT=Path(__file__).resolve().parent
FACE='M250 39 C121 39 30 114 30 255 L3 285 C-10 313 14 348 64 382 L176 500 L324 500 L436 382 C486 348 510 313 497 285 L470 255 C470 114 379 39 250 39 Z'
def append(assets):
 lines=assets['a16_voltron_componentFilenames'].splitlines();definitions=[]
 for sty,label in enumerate(['Vitiligo','Freckles','Birthmark','Dimples','Heterochromia','Albinism']):
  feature='iris' if sty==4 else 'base'
  version='-base1' if sty==4 else str(5 if sty==5 else sty+1)
  if sty==0:
   art=f'<path d="{FACE}" fill="#b3a7a0"/>'+''.join(f'<path d="{d}" fill="#fff7f0"/>' for d in ['M96 239 Q120 211 151 226 L181 260 Q166 290 147 280 Q111 293 95 268 Z','M286 215 Q315 226 338 211 Q363 211 374 232 L380 265 Q351 289 323 264 Q289 283 283 248 Z','M222 108 Q247 84 261 115 Q285 126 271 146 L235 155 Q211 140 222 108 Z','M185 349 Q222 333 249 350 Q287 329 316 352 L304 380 Q266 397 238 380 Q211 393 189 374 Z','M218 455 Q242 435 270 448 L281 475 L232 490 Z'])
  elif sty==1:
   art=f'<path d="{FACE}" fill="white"/>'
   for x,y,r in [(108,300,4),(125,310,3),(146,303,4),(163,316,3),(183,302,3),(199,317,4),(306,315,3),(323,301,4),(345,315,3),(362,303,4),(379,311,3),(396,300,4)]:art+=f'<circle cx="{x}" cy="{y}" r="{r}" fill="#946a4c"/>'
  elif sty==2:art=f'<path d="{FACE}" fill="white"/><path d="M328 289 Q348 274 366 295 L368 321 Q350 344 332 324 Z" fill="#937870"/>'
  elif sty==3:art=f'<path d="{FACE}" fill="white"/><path d="M164 349 Q150 361 164 373 M336 349 Q350 361 336 373" fill="none" stroke="#b39b88" stroke-width="7" stroke-linecap="round"/>'
  elif sty==4:
   art=''
   # Include pupils and highlights so the added style renders fully even when
   # the stock iris-lighting family has no matching style index.
   iris='M169 239 Q184 239 196 253 L219 277 Q238 296 223 316 L197 343 Q181 359 169 359 Q156 359 142 345 L119 322 Q102 307 110 285 L144 249 Q155 239 169 239 Z'
   for offset,color in [(0,'#c28e52'),(160,'#8ec6ed')]:
    art+=f'<g transform="translate({offset},0)"><path d="{iris}" fill="{color}"/><circle cx="169" cy="299" r="24" fill="#191b20"/><circle cx="156" cy="286" r="10" fill="white"/></g>'
  else:art=f'<path d="{FACE}" fill="white"/>'
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500" viewBox="0 0 500 500">{art}</svg>';src=f'genetic{sty+1}'
  (ROOT/'assets'/f'{src}.svg').write_text(svg);cairosvg.svg2png(bytestring=svg.encode(),write_to=str(ROOT/'assets'/f'{src}.png'))
  for gender in range(2):
   for stage in range(6):
    id_=87000+sty*100+gender*10+stage;n=f'a16_faces-{["male","female"][gender]}-stage{stage}-{feature}{version}-{id_:05d}'
    definitions.append(dict(name=n,stage=stage,gender=gender,feature=feature,style=sty,selectable_style=1 if sty==4 else 5 if sty==5 else sty+1,label=label,source=src+'.png',path=f'emoji/voltron/faces/face/stage {stage} {["male","female"][gender]}/'+n));lines.append(n+'.png')
 assets['a16_voltron_componentFilenames']='\r\n'.join(lines);(ROOT/'genetic_catalog.json').write_text(json.dumps(definitions,indent=2));return definitions
