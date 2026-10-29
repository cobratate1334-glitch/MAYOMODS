"""One supplied 1800s picture, confined to the original navigation header."""
import hashlib
from pathlib import Path
from PIL import Image,ImageOps
SOURCE=Path(__file__).resolve().parents[1]/'era_world/inputs/1800s/event_pictures/stagecoach_arrival.png'
def artwork():
 im=ImageOps.fit(Image.open(SOURCE).convert('RGBA'),(768,160),method=Image.Resampling.LANCZOS,centering=(.5,.42))
 yield 'native1120/header/1800',im,dict(kind='period-header',source='era_world/inputs/1800s/event_pictures/stagecoach_arrival.png',source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest())
