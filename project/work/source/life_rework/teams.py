"""Real club identities and offline badges, retaining every native team index."""
import csv,io,json,re,sys,urllib.request,concurrent.futures,hashlib,difflib,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parent
LEAGUES={'1000':'nfl','2000':'nba','2100':'wnba','3000':'mlb','4000':'nhl','5000':'epl','5100':'laliga','5200':'seriea','5300':'bundesliga','5310':'brazil','5400':'nwsl','5500':'wsl','6000':'nrl'}
SUPER=['Castleford Tigers','Catalans Dragons','Huddersfield Giants','Hull F.C.','Hull Kingston Rovers','Leeds Rhinos','Salford Red Devils','St Helens R.F.C.','Wakefield Trinity','Warrington Wolves','Wigan Warriors']
VOLLEY=['Loyola Chicago','St. John\'s','UCLA','Arizona State','Penn State','SMU','Miami','Tulane','Stanford','Michigan','Colorado','Portland','Washington','Georgia Tech','Utah','Marquette','Maryland','Boston College','Cleveland State','Georgetown','Pittsburgh','Minnesota','Houston','UTSA','San Diego','UNLV','Hawai\'i','Pumas UNAM','Toronto Varsity Blues','UBC Thunderbirds','Alaska Anchorage','Southern Miss']
ALIASES={'Brooklyn':'Brooklyn Nets','New York (A)':'New York Yankees','New York (N)':'New York Mets','Los Angeles (A)':'Los Angeles Angels','Los Angeles (N)':'Los Angeles Dodgers','New Jersey FC':'Gotham FC','Tacoma FC':'Seattle Reign FC','North Carolina FC':'North Carolina Courage','Utah FC':'Utah Royals','Canterbury-Bankstown':'Canterbury-Bankstown Bulldogs','Manly Warringah':'Manly Warringah Sea Eagles','St. George Illawarra':'St. George Illawarra Dragons'}
BY_INDEX={1016:'Los Angeles Chargers',1017:'Los Angeles Rams',1023:'New York Giants',1024:'New York Jets',2020:'LA Clippers',2021:'Los Angeles Lakers',3005:'Chicago White Sox',3006:'Chicago Cubs',3018:'New York Yankees',3019:'New York Mets',4004:'New York Islanders',4005:'New York Rangers',3020:'Athletics',4025:'Utah Mammoth',4031:'Vegas Golden Knights'}
BY_INDEX.update({5001: 'Arsenal', 5002: 'Aston Villa', 5003: 'Sunderland', 5004: 'Queens Park Rangers', 5005: 'Chelsea', 5006: 'Crystal Palace', 5007: 'Everton', 5008: 'Derby County F.C.', 5009: 'Leeds United', 5010: 'Leicester City', 5011: 'Liverpool', 5012: 'Manchester City', 5013: 'Manchester United', 5014: 'Newcastle United', 5015: 'Norwich City', 5016: 'Southampton', 5017: 'Tottenham Hotspur', 5018: 'Nottingham Forest', 5019: 'West Ham United', 5020: 'Wolverhampton Wanderers', 5101: 'Real Zaragoza', 5102: 'Athletic Club', 5103: 'Atlético Madrid', 5104: 'Barcelona', 5105: 'Celta Vigo', 5106: 'Espanyol', 5107: 'SD Eibar', 5108: 'Deportivo de La Coruña', 5109: 'Getafe', 5110: 'Granada CF', 5111: 'Mallorca', 5112: 'Levante', 5113: 'Osasuna', 5114: 'Real Betis', 5115: 'Real Madrid', 5116: 'Real Sociedad', 5117: 'Real Valladolid', 5118: 'Sevilla', 5119: 'Valencia', 5120: 'Villarreal', 5201: 'Atalanta', 5202: 'Benevento Calcio', 5203: 'Bologna', 5204: 'Cagliari', 5205: 'Catania FC', 5206: 'Fiorentina', 5207: 'Genoa', 5208: 'Internazionale', 5209: 'Juventus', 5210: 'Lazio', 5211: 'AC Milan', 5212: 'Napoli', 5213: 'Parma', 5214: 'AS Roma', 5215: 'Sampdoria', 5216: 'Sassuolo', 5217: 'Spezia Calcio', 5218: 'Torino', 5219: 'Udinese', 5220: 'Hellas Verona', 5301: 'Bayern Munich', 5302: 'Borussia Dortmund', 5303: 'RB Leipzig', 5304: 'Borussia Mönchengladbach', 5305: 'Bayer Leverkusen', 5306: 'TSG Hoffenheim', 5307: 'VfL Wolfsburg', 5308: 'SC Freiburg', 5309: 'Eintracht Frankfurt', 5310: 'Hertha BSC', 5311: 'Union Berlin', 5312: 'Schalke 04', 5313: 'Mainz', 5314: 'FC Cologne', 5315: 'FC Augsburg', 5316: 'Werder Bremen', 5317: 'Hamburg SV', 5318: 'VfB Stuttgart', 5401: 'Chicago Stars FC', 5402: 'Houston Dash', 5403: 'North Carolina Courage', 5404: 'Seattle Reign FC', 5405: 'Orlando Pride', 5406: 'Portland Thorns FC', 5407: 'Gotham FC', 5408: 'Utah Royals', 5409: 'Washington Spirit', 5501: 'Arsenal Women', 5502: 'Aston Villa Women', 5503: 'Birmingham City W.F.C.', 5504: 'Brighton & Hove Albion Women', 5505: 'Bristol City W.F.C.', 5506: 'Chelsea Women', 5507: 'Everton Women', 5508: 'Manchester City Women', 5509: 'Manchester United Women', 5510: 'Reading F.C. Women', 5511: 'Tottenham Hotspur Women', 5512: 'West Ham United Women', 5601: 'Athletico Paranaense', 5602: 'Atlético Goianiense', 5603: 'Atlético Mineiro', 5604: 'Bahia', 5605: 'Botafogo', 5606: 'Ceará Sporting Club', 5607: 'Corinthians', 5608: 'Coritiba', 5609: 'Fortaleza', 5610: 'Flamengo', 5611: 'Fluminense', 5612: 'Grêmio', 5613: 'Goiás Esporte Clube', 5614: 'Internacional', 5615: 'Palmeiras', 5616: 'Red Bull Bragantino', 5617: 'Santos', 5618: 'São Paulo', 5619: 'Sport Club do Recife', 5620: 'Vasco da Gama'})
BY_LEAGUE={
 '5000':{'Derby':'Derby County F.C.','Norwich':'Norwich City F.C.','Queens':'Queens Park Rangers','Blues FC':'Chelsea','Palace FC':'Crystal Palace','City FC':'Manchester City','West Ham':'West Ham United'},
 '5100':{'Zaragoza':'Real Zaragoza','Bilbao':'Athletic Club','Atletico':'Atlético Madrid','Vigo':'Celta Vigo','Español de Fútbol':'Espanyol','La Coruña':'Deportivo La Coruña','Pamplona':'Osasuna','Betis':'Real Betis','La Sociedad':'Real Sociedad','Valladolid':'Real Valladolid'},
 '5200':{'Bergamo':'Atalanta','Firenze':'Fiorentina','Catania':'Catania FC','Milan':'AC Milan','Roma':'AS Roma','La Spezia':'Spezia Calcio','Verona':'Hellas Verona'},
 '5300':{'Dortmund':'Borussia Dortmund','Leipzig':'RB Leipzig','Mönchengladbach':'Borussia Mönchengladbach','Leverkusen':'Bayer Leverkusen','Hoffenheim':'TSG Hoffenheim','Wolfsburg':'VfL Wolfsburg','Freiburg':'SC Freiburg','Frankfurt':'Eintracht Frankfurt','Berlin':'Hertha BSC','Köpenick':'Union Berlin','Köln':'FC Cologne','Bremen':'Werder Bremen','Hamburg':'Hamburg SV','Stuttgart':'VfB Stuttgart'},
 '5310':{'Atlético':'Athletico Paranaense','Galo':'Atlético Mineiro','Sport Club Paulista':'Corinthians','Curitiba':'Coritiba','Flamingos':'Flamengo','Porto Alegre':'Internacional','Goiás':'Goiás Esporte Clube','Esportiva Perdizes':'Palmeiras','Bragança Paulista':'Red Bull Bragantino','Recife':'Sport Club do Recife'},
 '5400':{'Chicago FC':'Chicago Stars FC','Houston FC':'Houston Dash','Orlando FC':'Orlando Pride','Portland FC':'Portland Thorns FC','New Jersey FC':'Gotham FC','Washington FC':'Washington Spirit'},
 '5500':{'Birmingham':'Birmingham City W.F.C.','Brighton':'Brighton & Hove Albion W.F.C.','Bristol':'Bristol City W.F.C.','Blues FC':'Chelsea F.C. Women','City FC':'Manchester City W.F.C.','Reading':'Reading F.C. Women','West Ham':'West Ham United F.C. Women'},
}
def norm(s):
    s=re.sub(r'\\([0-7]{3})',lambda m:chr(int(m[1],8)),s)
    return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
def fetch_json(url):
    req=urllib.request.Request(url,headers={'User-Agent':'MayoMods reference research/1.0'})
    with urllib.request.urlopen(req,timeout=25)as r:return json.load(r)
def wiki(name):
    cache=ROOT/'references/wiki';cache.mkdir(exist_ok=True);path=cache/(norm(name)+'.json')
    if path.exists():data=json.loads(path.read_text())
    else:
        data=fetch_json('https://en.wikipedia.org/api/rest_v1/page/summary/'+urllib.parse.quote(name.replace(' ','_')));path.write_text(json.dumps(data))
    image=data.get('thumbnail',{}).get('source');assert image,name
    return {'id':'wiki-'+norm(name),'displayName':data.get('title',name),'location':name,'logos':[{'href':image}],'reference':data.get('content_urls',{}).get('desktop',{}).get('page','')}

def build(assets,out):
    sys.path[:0]=[str(ROOT.parent),str(ROOT.parent/'native_v45')]
    from assets45 import codec
    decode,encode=codec();rows=list(csv.DictReader(io.StringIO(decode(assets['a16_sports-teams-enc']))))
    source={key:json.loads((ROOT/'references'/f'{name}.json').read_text())for key,name in LEAGUES.items()}
    for league,name in [('5000','epl2'),('5100','laliga2'),('5200','seriea2'),('5300','bundesliga2'),('5310','brazil2')]:
        source[league]+=json.loads((ROOT/'references'/f'{name}.json').read_text())
    cities={'289195':'Brisbane Broncos','289197':'Canterbury-Bankstown Bulldogs','289202':'North Queensland Cowboys','289209':'St George Illawarra Dragons','289194':'Parramatta Eels','289207':'Newcastle Knights','289199':'Penrith Panthers','289205':'South Sydney Rabbitohs','289198':'Canberra Raiders','289204':'Sydney Roosters','289196':'Manly Warringah Sea Eagles','289203':'Cronulla-Sutherland Sharks','289208':'Melbourne Storm','289206':'Gold Coast Titans','289201':'New Zealand Warriors','289200':'Wests Tigers'}
    for t in source['6000']:
        if t['id']in cities:t['displayName']=cities[t['id']]
        loc=t.get('location','')
        if loc and not norm(t['displayName']).startswith(norm(loc)):t['displayName']=loc+' '+t['displayName']
    volleyball=json.loads((ROOT/'references/volleyball.json').read_text());special={}
    missing=[]
    for name in SUPER+['Pumas UNAM','Toronto Varsity Blues','UBC Thunderbirds','Alaska Anchorage Seawolves']:
        try:special[name]=wiki(name)
        except Exception as e:missing.append({'name':name,'reason':str(e)})
    used={};mapping=[]
    for row in rows:
        league=row['League Index'];pool=source.get(league,volleyball if league=='7000'else[])
        stem=re.sub(r'\\([0-7]{3})',lambda m:chr(int(m[1],8)),row['Name'].split('<')[0].strip())
        wanted=BY_INDEX.get(int(row['Index']),BY_LEAGUE.get(league,{}).get(stem,ALIASES.get(stem,stem)))
        direct=None
        if league=='6100':direct=special.get(SUPER[int(row['Index'])-6100])
        if league=='7000':
            wanted=VOLLEY[int(row['Index'])-7000];direct=special.get(wanted)or special.get(wanted+' Seawolves')
        taken=used.setdefault(league,set())
        def score(t):
            n=norm(wanted);name=norm(t['displayName']);loc=norm(t.get('location',''))
            if league=='5500':
                n=n.removesuffix('women').removesuffix('wfc');name=name.removesuffix('women').removesuffix('wfc');loc=loc.removesuffix('women').removesuffix('wfc')
            return (100 if n==name else 70 if n==loc else 55 if name.startswith(n)else 40 if n in name else 0)+10*difflib.SequenceMatcher(None,n,name).ratio()
        candidates=[t for t in pool if t['id']not in taken]
        picked=direct or max(candidates,key=score,default=None)
        if not direct and (picked is None or score(picked)<40):
            errors=[]
            if league=='5500':
                n=norm(wanted).removesuffix('women').removesuffix('wfc');mens=[t for t in source['5000']if norm(t['displayName']).startswith(n)]
                if mens:picked={**mens[0],'displayName':wanted,'id':'women-'+mens[0]['id']};direct=picked
            for search in [wanted,wanted+' F.C.',wanted+' W.F.C.']:
                if direct:break
                try:picked=wiki(search);break
                except Exception as e:errors.append(str(e))
            else:raise ValueError(f'Cannot verify {row["Index"]} {wanted}: {errors}')
        if not picked:raise ValueError('No real team mapping for '+row['Index'])
        taken.add(picked['id']);new=copy_row=dict(row);copy_row['Name']=picked['displayName']
        mapping.append(dict(index=int(row['Index']),league=int(league),name=picked['displayName'],old_name=row['Name'],source_id=picked['id'],badge_url=picked.get('logos',[{}])[0].get('href'),reference=picked.get('reference','ESPN public team API'),matching_score=score(picked)))
    out=Path(out);out.mkdir(parents=True,exist_ok=True);logo_dir=out/'logos';logo_dir.mkdir(exist_ok=True)
    def download(item):
        try:
            assert item['badge_url']
            req=urllib.request.Request(item['badge_url'],headers={'User-Agent':'MayoMods reference research/1.0'})
            with urllib.request.urlopen(req,timeout=30)as r:raw=r.read(2000000)
            from PIL import Image
            im=Image.open(io.BytesIO(raw)).convert('RGBA');im.thumbnail((192,192));target=logo_dir/(str(item['index'])+'.png');im.save(target)
            return {**item,'image_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'pixel_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'size':list(im.size)}
        except Exception as e:return {**item,'error':str(e)}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8)as ex:result=list(ex.map(download,mapping))
    (out/'teams.json').write_text(json.dumps(result,indent=2)+'\n');(out/'lookup_failures.json').write_text(json.dumps(missing,indent=2)+'\n')
    print('Teams',len(result),'badges',sum('error'not in r for r in result),'failures',sum('error'in r for r in result),flush=True)
    return result

if __name__=='__main__':build(json.loads(Path(sys.argv[1]).read_text()),sys.argv[2])
