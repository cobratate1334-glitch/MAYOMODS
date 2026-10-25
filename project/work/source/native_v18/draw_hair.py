"""Extend the game's flat vector avatar style with twenty original hair layers."""
import math,random
from pathlib import Path
import cairosvg
ROOT=Path(__file__).resolve().parent/'assets';ROOT.mkdir(exist_ok=True)
dark='#ffffff';light='#d9d5d2';black='#ffffff';blond='#bb8849'
def path(d,color=dark,stroke=None,width=1):return f'<path d="{d}" fill="{color}" stroke="{stroke or color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'
def ellipse(x,y,rx,ry,color=dark):return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{color}"/>'
def coils(cx,cy,rx,ry,n,color=dark):
 rng=random.Random(n+int(cx));out=ellipse(cx,cy,rx,ry,color)
 for _ in range(n):
  a=rng.random()*math.tau;r=math.sqrt(rng.random());x=cx+math.cos(a)*rx*r;y=cy+math.sin(a)*ry*r
  out+=ellipse(round(x,1),round(y,1),rng.randrange(8,17),rng.randrange(8,16),color)
 return out
crown=path('M98 202 Q80 95 151 71 Q250 10 349 71 Q420 95 402 202 L377 192 Q351 111 250 125 Q150 114 122 199 Z')
for i in range(20):
 s=''
 if i==0:s=coils(250,116,173,108,140)
 elif i==1:s=coils(250,83,137,74,100)+path('M109 124 L124 200 L145 125 M391 124 L376 200 L355 125')
 elif i==2:s=coils(250,118,134,71,95)+path('M112 137 L127 205 L145 145 M388 137 L374 205 L355 145')
 elif i==3:s=crown+coils(250,110,133,53,70)
 elif i==4:s=crown+coils(111,100,82,75,80)+coils(389,100,82,75,80)
 elif i==5:s=crown+coils(250,63,87,59,70)
 elif i==6:
  s=path('M95 188 Q84 63 250 57 Q414 63 405 188 Q342 121 250 130 Q159 121 95 188 Z',light)
  for j in range(9):
   x=115+j*34;s+=path(f'M{x} 183 Q{150+j*24} 74 {210+j*10} 62','none',dark,17)
   for y in range(90,170,14):s+=path(f'M{x-6} {y} l12 9','none',light,3)
 elif i in [7,8,9]:
  s=crown
  for j in range(14):
   x=105+j*22;y=158+(j%3)*12;length=(230 if i==7 else 100 if i==8 else 255) if j<3 or j>10 else 63+(j%4)*18
   s+=path(f'M{x} {y} Q{x-15} {y+length//2} {x+6} {y+length}','none',dark,15 if i==7 else 12)
   for yy in range(y+12,y+length,16):s+=path(f'M{x-4} {yy} l8 7','none',light,2)
 elif i==10:
  s=crown
  for j in range(16):
   x=116+j*18;y=100+int(abs(j-7.5)*5);s+=ellipse(x,y,15,11,light)+path(f'M{x-7} {y-4} l12 8','none',dark,4)
 elif i in [11,12]:
  s=path('M93 215 Q85 54 250 53 Q417 54 405 215 L378 188 Q367 98 250 111 Q131 106 121 195 Z')
  if i==11:s=path('M335 133 Q456 157 433 344 Q421 422 374 468 Q424 287 347 219 Z')+s
  else:s=path('M273 70 Q429 42 432 191 Q441 306 366 410 Q416 229 317 146 Z')+s
 elif i==13:
  s=path('M87 390 L92 153 Q91 46 250 46 Q406 46 408 153 L414 390 L348 406 L364 176 L335 181 L319 139 L306 188 L274 169 L255 194 L218 151 L201 191 L167 153 L139 189 L148 404 Z')
 elif i==14:s=path('M91 284 Q49 119 112 86 Q237 18 364 84 Q450 119 409 284 L380 322 L335 301 Q379 173 343 153 Q231 84 139 153 Q116 207 161 304 L120 323 Z')
 elif i==15:
  s=path('M74 327 Q103 282 78 215 Q33 105 130 70 Q250 21 371 73 Q467 103 423 218 Q395 288 428 327 L366 393 L333 349 Q407 216 352 147 Q252 110 145 143 Q97 217 165 351 L132 393 Z')
  for x in [104,128,369,393]:s+=path(f'M{x} 153 Q{x-25} 234 {x+5} 303','none',light,5)
 elif i==16:s=path('M103 199 Q88 74 250 56 Q412 74 397 199 L369 159 Q249 104 131 159 Z',light)
 elif i==17:s=path('M97 208 Q54 113 131 69 Q265 0 387 104 L402 208 L374 176 Q331 112 257 111 Q159 150 122 210 Z')+path('M259 62 Q247 117 150 156','none',light,7)
 elif i==18:
  s=coils(250,115,156,95,115)
  s+=coils(153,107,63,76,70,blond)
 elif i==19:s=crown+ellipse(125,77,65,58)+ellipse(375,77,65,58)
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500" viewBox="0 0 500 500">{s}</svg>'
 (ROOT/f'hair{i+1}.svg').write_text(svg);cairosvg.svg2png(bytestring=svg.encode(),write_to=str(ROOT/f'hair{i+1}.png'))
print('Rendered 20 native hair styles')
