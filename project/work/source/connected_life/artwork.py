"""Real archive photographs for backgrounds; supplied art only for game items."""
from pathlib import Path
from PIL import Image,ImageOps,ImageEnhance,ImageDraw
ROOT=Path(__file__).resolve().parent

def artwork():
 from connected_life.era_catalog import ERAS
 photos={f.stem:Image.open(f).convert('RGBA')for f in (ROOT/'inputs/photos').glob('*.png')}
 for key,im in photos.items():yield 'native1110/photos/'+key,im,dict(kind='historical-photograph',photo_id=key,generated=False)
 for year,label,key in ERAS:
  im=ImageOps.fit(photos[key],(900,150),centering=(.5,.4));overlay=Image.new('RGBA',im.size,(0,0,0,148));im=Image.alpha_composite(im,overlay)
  mask=Image.new('L',im.size);d=ImageDraw.Draw(mask);d.rounded_rectangle((0,0,899,149),radius=70,fill=255);im.putalpha(mask)
  d=ImageDraw.Draw(im);d.rounded_rectangle((3,3,896,146),radius=68,outline=(218,210,177,255),width=5)
  yield 'native1110/era/'+str(year),im,dict(kind='native-photo-era-button',photo_id=key,generated=False)
 panels={}
 for key,photo in [('ww1','ww1'),('post1','interwar'),('ww2','ww2'),('post2','postwar')]:
  im=ImageOps.fit(photos[photo],(512,768));im=ImageEnhance.Brightness(im).enhance(.24);panels[key]=im
  yield 'native1109/background/'+key,im,dict(kind='journal-photo-background',photo_id=photo,replaces_generated_background=True,generated=False)
  im=ImageOps.fit(photos[photo],(512,512));yield 'native1109/news/'+key,im,dict(kind='native-news-photograph',photo_id=photo,replaces_generated_background=True,generated=False)
 # Retain the original Unity animation and supplied transparent planes. Only
 # its background is replaced. It is explicitly an illustration over a photo.
 from military_expansion.package import catalog
 for war,key,identity in [(1,'ww1','03_aircraft_02'),(2,'ww2','03_aircraft_13')]:
  row=next(r for r in catalog()['assets']if r['id']==identity);plane=Image.open(ROOT.parent/'military_expansion/inputs'/row['file']).convert('RGBA');plane.thumbnail((160,110))
  for n in range(24):
   im=ImageOps.fit(photos[key],(384,384));im=ImageEnhance.Brightness(im).enhance(.7);im.alpha_composite(plane,(round(-160+n/23*600),48))
   yield f'native1109/flight{war}/{n}',im,dict(kind='unity-animation-frame',photo_id=key,supplied_asset=identity,generated=False)
 import json
 manifest=json.loads((ROOT/'inputs/extra_military/manifest.json').read_text())
 for row in manifest['assets']:
  image=Image.open(ROOT/'inputs/extra_military'/row['file']).convert('RGBA')
  yield 'native1110/extra/'+row['id'],image,dict(kind='supplied-game-illustration',canonical_id=row['id'],source_file=row['file'])
