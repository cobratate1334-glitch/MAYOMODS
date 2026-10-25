"""Command IDs and snapshots shared by the website and its Unity-thread bridge."""
import csv, io, json, sys, re
from pathlib import Path
SOURCE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(SOURCE), str(SOURCE / 'social_roblox')]
from social_roblox import roblox_content

MAILBOX = 0xc400
WORDS = 32
TEXT_BASE = 0xd000
TEXT_WIDTH = 512
TEXTS = [('roblox_social', 'Result'), ('gameplay52', 'ClergyStatus'),
         ('gameplay52', 'ClergyEvent'), ('gameplay52', 'CaseOutcome'),
         ('roblox_social', 'ClubName'), ('roblox_social', 'GenreName'),
         ('roblox_social', 'DesignName'), ('roblox_social', 'GroupName')]

def definitions():
    base = json.loads((SOURCE / 'native_v55/assets.json').read_text())
    assets = {**base, **roblox_content.build(base)}
    rows = {x['ScenarioID']: x for x in csv.DictReader(io.StringIO(assets['genesis_activities_v18']))}
    schemas = {}
    for owner in ['roblox_social', 'gameplay52']:
        schemas[owner] = {x['key']: x for x in csv.DictReader(io.StringIO(assets['genesis_v18_defaults_' + owner]))}
    commands = []
    def add(key, scene, choice=1, title=None):
        row = rows[scene]
        commands.append(dict(id=len(commands) + 1, key=key, title=title or row['Title'],
                             logic=json.loads(row[f'Choice{choice}_AdvancedLogic']) if row[f'Choice{choice}_AdvancedLogic'] else None,
                             route=row[f'Choice{choice}_RouteTo']))
    pre = 'scenario.activitiesV18.roblox_'
    add('join', pre + 'account')
    for i in range(1, 5): add('genre' + str(i), pre + 'genre' + str(i))
    for key in ['work_script', 'work_world', 'work_feedback', 'fixbugs', 'archive_all', 'sell', 'group']:
        add(key, pre + 'refresh_' + key)
    for key in ['publish', 'update']:
        add(key, pre + key)
    for tier in range(1, 4):
        for term in range(4): add(f'buy{tier}_{term}', pre + f'refresh_buy{tier}_{term}')
        add('wear' + str(tier), pre + 'refresh_wear' + str(tier))
    for key in ['shirt', 'jacket', 'jersey']: add('design_' + key, pre + 'refresh_design_' + key)
    for key in ['access', 'copy', 'scam']: add('community_' + key, pre + 'community_' + key)
    for key in ['pantry', 'welcome', 'disagreement']:
        for n in range(1, 4): add(f'church_{key}_{n}', 'scenario.activitiesV18.church_refresh_' + key, n)
    for code, label in [(92,'Enter the seminary'),(93,'Study theology'),(94,'Study history'),(95,'Attend services'),
                        (96,'Meet Father Reed'),(97,'Practice a homily'),(98,'Study Latin'),(99,'Charitable work'),
                        (100,'Review progression'),(101,'Leave formation'),(102,'Attend conclave'),(104,'Choir'),(105,'Meet Mateo')]:
        add('church_' + str(code), 'scenario.activitiesV18.action52_' + str(code), title=label)
    fields = [(o,k) for o, defs in schemas.items() for k,r in defs.items() if r['type']=='int']
    assert len(fields) + WORDS < 700
    return assets, schemas, commands, fields

def result_pages(assets,commands):
    rows={r['ScenarioID']:r for r in csv.DictReader(io.StringIO(assets['genesis_activities_v18']))}
    routes=' '.join(json.dumps(c) for c in commands)
    names=sorted(set(re.findall(r'scenario\.[A-Za-z0-9_.]+',routes)))
    return {name:dict(id=i+1,title=rows[name]['Title'],body=rows[name]['Body']) for i,name in enumerate(names)}

def manifest():
    assets,_,commands,fields=definitions()
    return dict(commands={x['key']: x['id'] for x in commands},
                fields=[o+'.'+k for o,k in fields], texts=[o+'.'+k for o,k in TEXTS],
                results={r['id']:r for r in result_pages(assets,commands).values()})

if __name__=='__main__':
    Path(sys.argv[1]).write_text(json.dumps(manifest(),indent=2)+'\n')
