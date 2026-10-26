"""Read audited enum literals from the pinned v39 metadata, never ordinal guesses."""
import hashlib,json,struct,sys
from pathlib import Path
from native_v27.inspect_game27 import Game
ROOT=Path(__file__).resolve().parent

def compressed(data,offset):
 first=data[offset]
 if first<128:value=first
 elif first&0xc0==0x80:value=((first&0x3f)<<8)|data[offset+1]
 elif first&0xe0==0xc0:value=((first&0x1f)<<24)|(data[offset+1]<<16)|(data[offset+2]<<8)|data[offset+3]
 elif first==0xf0:value=struct.unpack_from('<I',data,offset+1)[0]
 elif first==0xfe:return 2147483647
 elif first==0xff:return -2147483648
 else:raise ValueError('Invalid compressed metadata literal')
 return -(value>>1)-1 if value&1 else value>>1

def extract(lib,meta):
 g=Game(lib,meta);assert struct.unpack_from('<I',g.meta,4)[0]==39
 defaults={fi:(ti,di)for fi,ti,di in (struct.unpack_from('<IHI',g.meta,10846652+i*10)for i in range(21045))}
 names=['MILITARY_DISCHARGE_TYPE','MILITARY_STATUS','MILITARY_BRANCH','SCHOOL_TYPE','SCHOOL_FUND_SOURCE','WORKPLACE_TYPE','OCCUPATION_TYPE']
 result={}
 for name in names:
  t=next(t for t in g.types if t['name']==name);rows={}
  for field in g.field_list(t):
   if field['name']=='value__':continue
   ty,offset=defaults[field['index']];assert ty==26375
   rows[field['name']]=compressed(g.meta,11057104+offset)
  result[name]=rows
 out=dict(metadata_sha256=hashlib.sha256(g.meta).hexdigest(),method='v39 field-default records and compressed signed literals',enums=result)
 (ROOT/'references/enums.json').write_text(json.dumps(out,indent=2)+'\n');return out

def enum(name,key):return json.loads((ROOT/'references/enums.json').read_text())['enums'][name][key]
if __name__=='__main__':print(json.dumps(extract(*sys.argv[1:])))
