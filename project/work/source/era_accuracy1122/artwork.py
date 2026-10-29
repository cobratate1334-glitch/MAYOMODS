"""One original countryside banner, confined to the existing 1800s navbar."""
import hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parent
def artwork():
 p=ROOT/'inputs/countryside.png';im=ImageOps.fit(Image.open(p).convert('RGBA'),(768,160),method=Image.Resampling.LANCZOS,centering=(.5,.65))
 yield 'native1122/header/1800',im,dict(kind='period-header',source='era_accuracy1122/inputs/countryside.png',source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),AI_generated=True)
 # Plain vector UI geometry, not a repainted stock/game/owner image.
 im=Image.new('RGBA',(512,512));d=ImageDraw.Draw(im);d.ellipse((4,4,507,507),fill='#a47551',outline='#fff8eb',width=12)
 yield 'native1122/age_circle',im,dict(kind='native-control-geometry',source='programmatic circle',AI_generated=False)
