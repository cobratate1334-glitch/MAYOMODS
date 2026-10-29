"""Mechanical sprite extraction from two original generated atlases."""
import hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
SCHOOL=['schoolyard1830','lesson1850','picnic1880','library1910','garden1930','science1950']
def artwork():
 for filename,names,rows,columns in [('school_atlas.png',SCHOOL,3,2),('wanted_atlas.png',[str(i)for i in range(4)],2,2)]:
  p=ROOT/'inputs'/filename;im=Image.open(p).convert('RGBA');bounds=[0,341,680,1024]if filename.startswith('school')else[0,im.height//2,im.height]
  for n,name in enumerate(names):
   x=n%columns;y=n//columns;cell=im.crop((x*im.width//columns,bounds[y],(x+1)*im.width//columns,bounds[y+1]));cell.thumbnail((640,400)if filename.startswith('school')else(512,512),Image.Resampling.LANCZOS)
   yield 'native1125/'+('school/'if filename.startswith('school')else'wanted/')+name,cell,dict(kind='original-generated-illustration',source_atlas=filename,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),grid_column=x,grid_row=y,not_an_archive_photograph=True)
 p=ROOT/'inputs/cinema1920.png';im=Image.open(p).convert('RGBA');im.thumbnail((640,400),Image.Resampling.LANCZOS)
 yield 'native1125/era/cinema1920',im,dict(kind='supplied-illustration',source_file=p.name,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
