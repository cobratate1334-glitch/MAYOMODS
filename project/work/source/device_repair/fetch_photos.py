"""Download identified real photographs and retain attribution/checksums."""
import hashlib,html,io,json,re,urllib.request
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
PICKS={'london2005':0,'covid2020':1,'berlin':0,'gallipoli':0,'somme':1,'blitz':3,'pearl':0,'dday':0}
def run(candidates):
 data=json.loads(Path(candidates).read_text());out=[]
 for key,i in PICKS.items():
  row=data[key][i];meta=row['extmetadata'];license=meta['LicenseShortName']['value'];assert license in ['Public domain','CC BY-SA 4.0','CC BY 2.0','CC0']
  url=(row.get('thumburl')or row['url']).split('?')[0]
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MayoMods archive photo attribution/1.0'}),timeout=30)as r:raw=r.read()
  im=Image.open(io.BytesIO(raw)).convert('RGB');im.thumbnail((1100,900),Image.Resampling.LANCZOS);p=ROOT/'inputs/photos'/f'{key}.png';p.parent.mkdir(exist_ok=True,parents=True);im.save(p,optimize=True)
  clean=lambda s:html.unescape(re.sub('<[^>]*>',' ',s)).strip()
  out.append(dict(id=key,title=row['title'],source_url=row['descriptionurl'],image_url=url,author=clean(meta.get('Artist',{}).get('value','See source')),license=license,license_url=meta.get('LicenseUrl',{}).get('value','https://commons.wikimedia.org/wiki/Commons:Public_domain'),date=clean(meta.get('DateTimeOriginal',{}).get('value','See source')),source_sha256=hashlib.sha256(raw).hexdigest(),packaged_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),generated=False))
  print(key,license,flush=True)
 (ROOT/'references/photos.json').write_text(json.dumps(out,indent=2)+'\n')
 (ROOT/'references/ASSETS.md').write_text('# Added photographs\n\nOriginal school and military resource IDs are preserved. These are real photographs, resized for the game. No AI images were generated. London uses a photograph of the victims’ memorial, not an image claiming to show the attack.\n\n'+''.join(f'## {r["id"]}\n\n{r["title"]}\n\n{r["author"]} — {r["license"]}\n\n{r["source_url"]}\n\n{r["license_url"]}\n\n'for r in out))
if __name__=='__main__':
 import sys;run(sys.argv[1])
