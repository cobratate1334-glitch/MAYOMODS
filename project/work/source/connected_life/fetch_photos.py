"""Fetch attributed photographic sources; no image-generation service is used."""
import json,urllib.request,urllib.parse,hashlib,re,html,time,sys
from pathlib import Path
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parent
UA='MayoMods historical photo attribution/1.0'
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':UA}),timeout=30)as r:return r.read()
def search(query):
 p={'action':'query','format':'json','generator':'search','gsrsearch':query,'gsrnamespace':6,'gsrlimit':4,'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':960}
 d=json.loads(get('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(p)))
 return [{'title':p['title'],**p['imageinfo'][0]}for p in d.get('query',{}).get('pages',{}).values()if'imageinfo'in p]
def fetch(candidates):
 d=json.loads(Path(candidates).read_text());picks={'ww1':0,'interwar':0,'ww2':2,'coldwar':1,'retro':0,'millennium':2,'digital':0,'modern':0,'sept11':0}
 extra=Path(candidates).with_name('extra_photo_candidates.json')
 if extra.exists():d.update(json.loads(extra.read_text()))
 else:
  for name,query in [('postwar','intitle:"Kissing the War Goodbye" filetype:bitmap'),('early','intitle:"Broadway" intitle:"1900" filetype:bitmap'),('moon','intitle:"AS11-40-5903" filetype:bitmap')]:
   d[name]=search(query);time.sleep(1)
 picks.update(postwar=0,early=0,moon=0)
 reports=[]
 for name,index in picks.items():
  r=d[name][index];meta=r['extmetadata'];license=meta.get('LicenseShortName',{}).get('value','');assert license in ['Public domain','No restrictions','CC BY 2.0','CC BY-SA 4.0','CC0'],(name,license)
  assert all(x not in r['title'].lower()for x in ['.pdf','.djvu','digital render','collage','.ogg']),r['title']
  url=r.get('thumburl')or r['url'];url=url.split('?')[0];private=Path(candidates).parent/(name+'-original');raw=private.read_bytes()if private.exists()else get(url);private.write_bytes(raw)
  import io
  image=Image.open(io.BytesIO(raw)).convert('RGB');image.thumbnail((1100,900),Image.Resampling.LANCZOS);out=ROOT/'inputs/photos'/f'{name}.png';image.save(out,optimize=True)
  clean=lambda value:html.unescape(re.sub('<[^>]*>',' ',value)).strip()
  reports.append(dict(id=name,title=r['title'],source_url=r.get('descriptionurl')or 'https://commons.wikimedia.org/wiki/'+urllib.parse.quote(r['title'].replace(' ','_')),image_url=url,author=clean(meta.get('Artist',{}).get('value','Unknown; see source')),credit=clean(meta.get('Credit',{}).get('value','')),license=license,license_url=meta.get('LicenseUrl',{}).get('value','https://commons.wikimedia.org/wiki/Commons:Public_domain'),date=clean(meta.get('DateTimeOriginal',{}).get('value','See source')),source_sha256=hashlib.sha256(raw).hexdigest(),packaged_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),processing='Resized photograph for mobile game; layout crops are documented by the importer',generated=False))
  print(name,r['title'],license,flush=True);time.sleep(.5)
 (ROOT/'references/photos.json').write_text(json.dumps(reports,indent=2)+'\n')
 (ROOT/'inputs/photos/ATTRIBUTION.md').write_text('# Photographic sources\n\n'+''.join('## '+r['id']+'\n\n'+r['title']+'\n\n'+r['author']+' — '+r['license']+'\n\n'+r['source_url']+'\n\n'+r['license_url']+'\n\nResized/cropped for the game; photographs are not AI generated.\n\n'for r in reports))
if __name__=='__main__':fetch(sys.argv[1])
