"""Contextual real photos; imported pictures retain their own aspect ratio."""
import hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent

def artwork():
 for row in json.loads((ROOT/'references/photos.json').read_text()):
  p=ROOT/'inputs/photos'/(row['id']+'.png');assert hashlib.sha256(p.read_bytes()).hexdigest()==row['packaged_sha256']
  im=Image.open(p).convert('RGBA')
  yield 'native1111/news1112/'+row['id'],im,dict(kind='archive-photograph',generated=False,source_url=row['source_url'],license=row['license'],source_id=row['id'])
