"""Import supplied game art and readable portrait journal surfaces."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageOps
from era_world.catalog import THEMES
ROOT=Path(__file__).resolve().parent
def artwork():
 source={}
 for row in json.loads((ROOT/'references/supplied_assets.json').read_text()):
  p=ROOT/'inputs'/row['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['source_sha256']
  im=Image.open(p).convert('RGBA');source[row['resource']]=im
  if row['kind']=='icon':
   icon=im.crop(im.getbbox());icon.thumbnail((232,232),Image.Resampling.LANCZOS);im=Image.new('RGBA',(256,256));im.alpha_composite(icon,((256-icon.width)//2,(256-icon.height)//2))
  yield row['resource'],im,row
 for year,label,key,header,paper,ink in THEMES:
  im=source['native1119/'+key];canvas=Image.new('RGBA',(512,768),paper)
  # Preserve the supplied 2:1 scene. A quiet paper centre keeps journal text
  # legible; the full-width scene sits at the bottom with a softened header.
  scene=ImageOps.contain(im,(512,256));canvas.alpha_composite(scene,(0,768-scene.height))
  top=scene.copy();top.putalpha(top.getchannel('A').point(lambda v:v//4));canvas.alpha_composite(top,(0,0))
  yield 'native1119/background/'+str(year),canvas,dict(kind='journal-surface',source=key,year=year)
 for row in json.loads((ROOT/'references/photos.json').read_text()):
  p=ROOT/'inputs/photos'/(row['id']+'.png');assert hashlib.sha256(p.read_bytes()).hexdigest()==row['packaged_sha256']
  yield 'native1119/photos/'+row['id'],Image.open(p).convert('RGBA'),dict(kind='archive-media',**row)
