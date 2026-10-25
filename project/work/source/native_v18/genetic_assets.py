"""Original vector portrait variants in the stock 500px Voltron coordinate space."""
import json
from pathlib import Path
import cairosvg
ROOT=Path(__file__).resolve().parent
FACE='M250 21 C130 21 49 113 49 220 L23 251 C10 279 21 337 67 371 C77 427 125 466 167 499 L333 499 C375 466 423 427 433 371 C479 337 490 279 477 251 L451 220 C451 113 370 21 250 21 Z'
def append(assets):
 lines=assets['a16_voltron_componentFilenames'].splitlines();definitions=[]
 for sty,label in enumerate(['Vitiligo','Freckles','Birthmark','Dimples','Heterochromia']):
  feature='base' if sty<4 else 'eye';version=str(sty+1) if sty<4 else '-base1'
  if sty==0:
   art=f'<path d="{FACE}" fill="#b3a7a0"/>'+''.join(f'<path d="{d}" fill="#fff7f0"/>' for d in ['M96 239 Q120 211 151 226 L181 260 Q166 290 147 280 Q111 293 95 268 Z','M286 215 Q315 226 338 211 Q363 211 374 232 L380 265 Q351 289 323 264 Q289 283 283 248 Z','M222 108 Q247 84 261 115 Q285 126 271 146 L235 155 Q211 140 222 108 Z','M185 349 Q222 333 249 350 Q287 329 316 352 L304 380 Q266 397 238 380 Q211 393 189 374 Z','M218 455 Q242 435 270 448 L281 475 L232 490 Z'])
  elif sty==1:
   art=f'<path d="{FACE}" fill="white"/>'
   for x,y,r in [(108,300,4),(125,310,3),(146,303,4),(163,316,3),(183,302,3),(199,317,4),(306,315,3),(323,301,4),(345,315,3),(362,303,4),(379,311,3),(396,300,4)]:art+=f'<circle cx="{x}" cy="{y}" r="{r}" fill="#946a4c"/>'
  elif sty==2:art=f'<path d="{FACE}" fill="white"/><path d="M328 289 Q348 274 366 295 L368 321 Q350 344 332 324 Z" fill="#937870"/>'
  elif sty==3:art=f'<path d="{FACE}" fill="white"/><path d="M164 349 Q150 361 164 373 M336 349 Q350 361 336 373" fill="none" stroke="#b39b88" stroke-width="7" stroke-linecap="round"/>'
  else:
   art=''
   for x,color in [(162,'#946639'),(338,'#6192a9')]:art+=f'<ellipse cx="{x}" cy="262" rx="64" ry="41" fill="white"/><circle cx="{x}" cy="262" r="33" fill="{color}"/><circle cx="{x}" cy="262" r="20" fill="#171411"/><circle cx="{x-9}" cy="253" r="9" fill="white"/>'
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500" viewBox="0 0 500 500">{art}</svg>';src=f'genetic{sty+1}'
  (ROOT/'assets'/f'{src}.svg').write_text(svg);cairosvg.svg2png(bytestring=svg.encode(),write_to=str(ROOT/'assets'/f'{src}.png'))
  for gender in range(2):
   for stage in range(6):
    id_=102000+sty*100+gender*10+stage;n=f'a16_faces-{["male","female"][gender]}-stage{stage}-{feature}{version}-{id_}'
    definitions.append(dict(name=n,stage=stage,gender=gender,feature=feature,style=sty,label=label,source=src+'.png',path=f'emoji/voltron/faces/{feature}/stage {stage} {["male","female"][gender]}/'+n));lines.append(n+'.png')
 assets['a16_voltron_componentFilenames']='\r\n'.join(lines);(ROOT/'genetic_catalog.json').write_text(json.dumps(definitions,indent=2));return definitions
