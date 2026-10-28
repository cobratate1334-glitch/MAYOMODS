"""Selected supplied PNGs and attributed archive media. No generated history."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parent

def artwork():
 for row in json.loads((ROOT/'references/supplied_assets.json').read_text()):
  p=ROOT/'inputs'/row['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['source_sha256']
  im=Image.open(p).convert('RGBA')
  if row['kind']=='icon':
   icon=im.crop(im.getbbox());icon.thumbnail((232,232),Image.Resampling.LANCZOS)
   im=Image.new('RGBA',(256,256));im.alpha_composite(icon,((256-icon.width)//2,(256-icon.height)//2))
  yield row['resource'],im,dict(row)
 for row in json.loads((ROOT/'references/photos.json').read_text()):
  p=ROOT/'inputs/photos'/(row['id']+'.png');assert hashlib.sha256(p.read_bytes()).hexdigest()==row['packaged_sha256']
  im=Image.open(p).convert('RGBA');yield 'native1118/photos/'+row['id'],im,dict(kind='archive-media',**row)
  if row['id']in ['1800','1820','1840','1860','1880']:
   panel=ImageOps.fit(im,(900,150),centering=(.5,.4));panel=Image.alpha_composite(panel,Image.new('RGBA',panel.size,(0,0,0,148)))
   mask=Image.new('L',panel.size);ImageDraw.Draw(mask).rounded_rectangle((0,0,899,149),radius=70,fill=255);panel.putalpha(mask)
   ImageDraw.Draw(panel).rounded_rectangle((3,3,896,146),radius=68,outline=(218,210,177,255),width=5)
   yield 'native1118/era/'+row['id'],panel,dict(kind='archive-era-panel',source_id=row['id'],generated=False)
