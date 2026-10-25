"""Import paid sprite sheets into ordinary Voltron and menu resources.

Atlas cuts retain the supplied pixels. Coordinate fitting is an import step;
no complete face is pasted over the player's native face. Reproduction needs
only the included input sheets and the released v48 APK.
"""
import copy,csv,hashlib,io,json,math,shutil,struct,sys,zipfile
from pathlib import Path
from collections import Counter
from collections import deque
from PIL import Image,ImageDraw,ImageFilter,ImageChops,ImageFont
import UnityPy
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from catalog49 import *
from native_v29.content import writecsv
sha=lambda b:hashlib.sha256(b).hexdigest()

def content():
 a=json.loads((SOURCE/'native_v48/assets.json').read_text());schemas=json.loads((SOURCE/'native_v48/schemas.json').read_text())
 defaults=[]
 for key,options,_,_ in CATEGORIES:
  if key!='Mark':defaults.append(dict(key=key,type='int',value=0,reset_on_ageup='',minimum=0,maximum=len(options)-1))
 for key in ['AlbinismApplied','LastTrait','LastHairColour','LastSkin']:defaults.append(dict(key=key,type='int',value=0,reset_on_ageup='',minimum=0,maximum=14))
 for key in ['OriginalHairType','HairTypeSaved']:defaults.append(dict(key=key,type='int',value=0,reset_on_ageup='',minimum=0,maximum=32))
 for stage in range(6):
  for gender in range(2):defaults.append(dict(key=f'ReadyF0S{stage}G{gender}',type='int',value=0,reset_on_ageup='',minimum=0,maximum=1))
 for feature in [1,3,4,5,6,8]:
  for stage in range(6):
   for gender in range(2):
    for prefix in ['ID','Color']:defaults.append(dict(key=f'{prefix}F{feature}S{stage}G{gender}',type='string',value='',reset_on_ageup='',minimum='',maximum=''))
 for slot in range(1,4):
  for key in FIELDS+['Mark','Saved']:defaults.append(dict(key=f'Look{slot}{key}',type='int',value=0,reset_on_ageup='',minimum=0,maximum=100))
 for key,value in [('Title','Appearance studio'),('Status','Select a category. Your face, eyes, marks and accessories use the native portrait renderer.')]:defaults.append(dict(key=key,type='string',value=value,reset_on_ageup='',minimum='',maximum=''))
 a['genesis_v18_defaults_custom49']=writecsv(defaults);schemas[OWNER]={r['key']:r for r in defaults}
 # This is an existing Life & Identity submenu, also reachable from the
 # existing accessories wardrobe. It creates no bottom navigation tab.
 def item(title,icon,listid=None,scene=None,detail=''):
  route=dict(ListID=listid) if listid else dict(ScenarioID=scene,ScenarioFile='genesis_activities_v18')
  return dict(Title=title,Icon=icon,SecondLine=detail,TileID='v49_'+str(len(title))+('_'+scene.rsplit('_',1)[-1] if scene else'_'+listid),ActionList=[dict(Index=0,ConditionList=[route])])
 def menu(name,title,items):a[name]=json.dumps(dict(ListID=name,Title=title,PresentationMode='Normal',Items=items),indent=2)
 root=[]
 for key,options,title,icon in CATEGORIES:
  name='genesis_v18_custom49_'+key.lower();root.append(item(title,icon,name,detail=f'{len(options)-1} choices plus natural appearance'))
  commands=[c for c in COMMANDS if c['key']==key]
  menu(name,title.upper(),[item(c['label'],icon,scene=c['scene'],detail='Confirm to apply; Back keeps your current look')for c in commands])
 root.append(item('Saved looks','49-wardrobe','genesis_v18_custom49_looks',detail='Three complete looks saved for this character'))
 reset=next(c for c in COMMANDS if c['key']=='Reset');root.append(item(reset['label'],'49-wardrobe',scene=reset['scene'],detail='Restore your original hair, eyes, skin and extra layers'))
 menu('genesis_v18_custom49','APPEARANCE STUDIO',root)
 menu('genesis_v18_custom49_looks','SAVED LOOKS',[item(c['label'],c['icon'],scene=c['scene'])for c in COMMANDS if c['key']in ['Save','Load']])
 for name in ['genesis_v18_life_v18','genesis_v18_era44_owned']:
  doc=json.loads(a[name]);doc['Items'].insert(0,item('Appearance studio','49-hair','genesis_v18_custom49',detail='Hair, eyes, skin, scars, eyepatches and saved looks'));a[name]=json.dumps(doc,indent=2)
 # Reuse the existing feature registration format without an entry menu.
 lines=a['genesis_feature_containers'].splitlines();start=next(i for i,l in enumerate(lines)if l.startswith('ContainerId,'));rr=list(csv.DictReader(io.StringIO('\n'.join(lines[start:]))));template=next(r for r in rr if r['ContainerId']=='era44');new={k:''for k in template}
 new.update(ContainerId=OWNER,DisplayName='Appearance',InitDataSheet='genesis_v18_defaults_custom49',EntryMenu='')
 # Field spellings are taken from this exact engine's shipped schema.
 for k,v in template.items():
  if v=='genesis_v18_defaults_era44':new[k]='genesis_v18_defaults_custom49'
  elif k not in ['ContainerId','EntryMenu','EntryLabel','EntryListID','EntryEmoji','EntrySecondLine','DefaultProperties','ContainerLabel']and v in ['content','0']:new[k]=v
 rr.append(new);a['genesis_feature_containers']='\r\n'.join(lines[:start])+'\r\n'+writecsv(rr)
 base_rows=list(csv.DictReader(io.StringIO(a['genesis_activities_v18'])));template=next(r for r in base_rows if r['ScenarioID']=='scenario.activitiesV18.era44_home');rows=[]
 for c in COMMANDS:
  row={k:''for k in template};row.update(ScenarioID=c['scene'],Style='normal',ExteriorTitle='Appearance studio',Title=c['label'],HasDismissButton='true',EmojiString='hero',Body='Apply this selection to your character? Hair, eye colours, skin marks, scars and eyepatches can be combined. Your current look stays in place when you choose Back.',Choice1_Text='Apply',Choice1_ButtonStyle='normal',Choice2_Text='Back',Choice2_ButtonStyle='normal')
  if c['key']=='Load':row['Body']='Load this character’s saved look. An empty slot leaves your appearance unchanged.'
  if c['key']=='Save':row['Body']='Save your complete current appearance, including genetic marks, hair, eyes, skin and extra layers, into this slot.'
  rows.append(row)
 for name in ['genesis_activities_v18','genesis_activities_v12']:
  old=list(csv.DictReader(io.StringIO(a[name])));a[name]=writecsv(old+rows)
 # The journal choice is plain text; its old Unicode book glyph is absent
 # from the game's button font. Icons elsewhere use actual sprite resources.
 # Replace generic icons only where the existing action has the same meaning.
 replacements={'hospital':'49-hospital','index-cards':'49-journal','brain':'49-brain','handshake':'49-handshake','running-shoe':'49-health'}
 for name,value in list(a.items()):
  if not name.startswith('genesis_v18_')or not value.startswith('{'):continue
  doc=json.loads(value)
  for row in doc.get('Items',[]):
   icon=row.get('Icon','')
   if icon in replacements:row['Icon']=replacements[icon]
  a[name]=json.dumps(doc,indent=2)
 (ROOT/'assets.json').write_text(json.dumps(a,ensure_ascii=True,indent=2)+'\n');(ROOT/'schemas.json').write_text(json.dumps(schemas,indent=2)+'\n')
 return a

def fit(raw,box,size=(500,500)):
 out=Image.new('RGBA',size);piece=raw.resize((max(1,round(box[2]-box[0])),max(1,round(box[3]-box[1]))),Image.Resampling.LANCZOS);out.alpha_composite(piece,(round(box[0]),round(box[1])));return out

def isolate(raw):
 # A few supplied cells overlap their neighbours. Import the main connected
 # sprite, plus details inside its bounds, instead of including another cut.
 w,h=raw.size;a=raw.getchannel('A');pixels=a.load();seen=set();groups=[]
 for y in range(h):
  for x in range(w):
   if (x,y)in seen or pixels[x,y]<128:continue
   q=deque([(x,y)]);seen.add((x,y));points=[]
   while q:
    px,py=q.popleft();points.append((px,py))
    for nx,ny in [(px-1,py),(px+1,py),(px,py-1),(px,py+1)]:
     if 0<=nx<w and 0<=ny<h and (nx,ny)not in seen and pixels[nx,ny]>=128:seen.add((nx,ny));q.append((nx,ny))
   groups.append(points)
 if not groups:return raw
 main=max(groups,key=len);l=min(x for x,y in main);r=max(x for x,y in main);t=min(y for x,y in main);b=max(y for x,y in main);keep=Image.new('L',raw.size);d=ImageDraw.Draw(keep)
 for points in groups:
  cx=sum(x for x,y in points)/len(points);cy=sum(y for x,y in points)/len(points)
  if points is main or l<=cx<=r and t<=cy<=b:
   for p in points:d.point(p,fill=255)
 keep=keep.filter(ImageFilter.MaxFilter(3));result=raw.copy();result.putalpha(ImageChops.multiply(a,keep));return result

def eyes(iris,left,right,mode=0):
 # A precoloured iris needs a pupil and highlight of its own. Leaving the
 # stock white tint mask in custom resources produced blank-looking eyes.
 out=Image.new('RGBA',iris.size);alpha=iris.getchannel('A');d=ImageDraw.Draw(out)
 for side,color in enumerate([left,right]):
  offset=side*250;box=alpha.crop((offset,0,offset+250,500)).getbbox();assert box
  x0,y0,x1,y1=box;x0+=offset;x1+=offset;cx=(x0+x1)/2;cy=(y0+y1)/2;radius=min((x1-x0)*.32,(y1-y0)*.47)
  d.rectangle((offset,0,offset+250,500),fill=(248,248,246,255));rgb=tuple(bytes.fromhex(color))
  for n in range(40,0,-1):
   r=radius*n/40;shade=.48+.52*(1-n/40);c=tuple(round(v*shade)for v in rgb);d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=c+(255,))
  if mode==12 and side==0:d.pieslice((cx-radius,cy-radius,cx+radius,cy+radius),320,40,fill=(192,130,46,255))
  if mode==13:
   r=radius*.63;d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(188,134,55,255))
  r=radius*.43;d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(24,26,28,255));r=radius*.17;d.ellipse((cx-radius*.27-r,cy-radius*.32-r,cx-radius*.27+r,cy-radius*.32+r),fill=(255,255,255,255))
 out.putalpha(alpha);return out

def pattern(era,kind):
 # These code-native patterns have no text, so titles remain accessible and
 # localizable CandyText. Quiet centres keep every label legible.
 w,h=(1000,160)if kind=='header'else(1000,280);pal=[('#513B2B','#D5B67A'),('#20262A','#BC343A'),('#176A69','#E7A341'),('#085F9D','#42D8CE')][era]
 im=Image.new('RGBA',(w,h),pal[0]);d=ImageDraw.Draw(im)
 if era==0:
  for inset in [8,14]:d.rectangle((inset,inset,w-inset-1,h-inset-1),outline=pal[1],width=2)
  for x,flip in [(28,1),(w-28,-1)]:
   for y in range(25,h-20,12):d.arc((x-14,y-10,x+14,y+10),90 if flip==1 else 270,270 if flip==1 else 450,fill=pal[1],width=2)
  for x in range(80,w-80,12):d.point((x,20),fill=pal[1]);d.point((x,h-21),fill=pal[1])
 elif era==1:
  d.rectangle((0,0,w,8),fill='#E4DDCC');d.rectangle((0,h-9,w,h),fill=pal[1]);d.line((28,20,28,h-20),fill='#A49D8C',width=3);d.line((w-28,20,w-28,h-20),fill='#A49D8C',width=3)
  for y in range(24,h-20,7):d.line((44,y,130,y),fill='#4D5050',width=1);d.line((w-130,y,w-44,y),fill='#4D5050',width=1)
 elif era==2:
  for n,col in enumerate(['#F0CB70','#E98B45','#B84B30']):d.polygon([(0,h-n*17),(180,h),(0,h-130-n*17)],fill=col);d.polygon([(w,n*17),(w-180,0),(w,130+n*17)],fill=col)
  d.rounded_rectangle((12,10,w-12,h-10),radius=28,outline='#F7E6BD',width=4)
 else:
  d.rounded_rectangle((12,10,w-12,h-10),radius=24,outline='#58B1DD',width=2)
  for x in range(28,110,14):d.ellipse((x,26,x+4,30),fill=pal[1]);d.ellipse((w-x-4,h-30,w-x,h-26),fill=pal[1])
 return im

def build(base,out,inputs):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);inp=ROOT/'inputs';inp.mkdir(exist_ok=True)
 for p in Path(inputs).glob('*.png'):
  if p.name[:2]in ['02','03','04','05','06','07','08']and p.resolve()!=(inp/p.name).resolve():shutil.copyfile(p,inp/p.name)
 a=content();sheets={int(p.name[:2]):Image.open(p).convert('RGBA')for p in inp.glob('*.png')}
 with zipfile.ZipFile(base)as z:env=UnityPy.load(z.read('assets/bin/Data/datapack.unity3d'));data=UnityPy.load(z.read('assets/bin/Data/data.unity3d'))
 texts={o.read().m_Name:o for o in env.objects if o.type.name=='TextAsset'};textures={o.read().m_Name:o for o in env.objects if o.type.name=='Texture2D'}
 rm=next(o for o in data.objects if o.type.name=='ResourceManager');tree=rm.read_typetree();original=copy.deepcopy(tree['m_Container']);rid=next(n+1 for n,e in enumerate(rm.assets_file.externals)if e.path=='resources.assets');file=texts['a16_voltron_componentFilenames'].assets_file;nextid=max(file.objects)+1
 tex_template=textures['a16_faces-male-stage2-hair-base1-00792'];spr_template=next(o for o in env.objects if o.type.name=='Sprite'and o.read().m_Name=='a16_faces-male-stage2-hair-base1-00792')
 catalogue=[];imports=[];newpaths=set();emitted={}
 def register(name,path,im,meta=None):
  nonlocal nextid
  assert path not in newpaths;newpaths.add(path)
  # Keep the native 500px portrait coordinate space. Voltron assigns a
  # Sprite to its Unity Image; an atlas crop alone loses layer positioning.
  # Shared identical canvases reuse one Texture2D to control memory usage.
  fingerprint=(im.size,sha(im.tobytes()))
  if fingerprint in emitted:to=emitted[fingerprint]
  else:
   to=copy.copy(tex_template);to.path_id=nextid;nextid+=1;to.data=tex_template.get_raw_data();file.objects[to.path_id]=to
   tx=to.read();tx.m_Name=name;tx.set_image(im,target_format=4);tx.save();emitted[fingerprint]=to
  so=copy.copy(spr_template);so.path_id=nextid;nextid+=1;so.data=spr_template.get_raw_data();file.objects[so.path_id]=so
  st=so.read_typetree();st['m_Name']=name;digest=hashlib.sha256(name.encode()).digest();st['m_RenderDataKey']=({f'data[{i}]':struct.unpack_from('<I',digest,i*4)[0]for i in range(4)},21300000)
  w,h=im.size;st.update(m_Rect=dict(x=0.,y=0.,width=float(w),height=float(h)),m_Offset=dict(x=0.,y=0.),m_Pivot=dict(x=.5,y=.5),m_PixelsToUnits=100.,m_IsPolygon=False,m_AtlasTags=[],m_SpriteAtlas=dict(m_FileID=0,m_PathID=0),m_PhysicsShape=[])
  rd=st['m_RD'];rd.update(texture=dict(m_FileID=0,m_PathID=to.path_id),alphaTexture=dict(m_FileID=0,m_PathID=0),secondaryTextures=[],textureRect=dict(x=0.,y=0.,width=float(w),height=float(h)),textureRectOffset=dict(x=0.,y=0.),atlasRectOffset=dict(x=0.,y=0.),settingsRaw=64,uvTransform=dict(x=100.,y=w/2,z=100.,w=h/2),downscaleMultiplier=1.)
  rd['m_IndexBuffer']=struct.pack('<6H',0,1,2,0,2,3);rd['m_SubMeshes']=[dict(firstByte=0,indexCount=6,topology=0,baseVertex=0,firstVertex=0,vertexCount=4,localAABB=dict(m_Center=dict(x=0.,y=0.,z=0.),m_Extent=dict(x=w/200,y=h/200,z=0.)))];vd=rd['m_VertexData'];vd['m_VertexCount']=4
  for c in vd['m_Channels']:c.update(stream=0,offset=0,format=0,dimension=0)
  vd['m_Channels'][0].update(dimension=3);vd['m_Channels'][4].update(stream=1,dimension=2);vd['m_DataSize']=struct.pack('<20f',-w/200,-h/200,0,-w/200,h/200,0,w/200,h/200,0,w/200,-h/200,0,0,0,0,1,1,1,1,0);so.save_typetree(st)
  for o in [to,so]:tree['m_Container'].append((path,dict(m_FileID=rid,m_PathID=o.path_id)))
  row=dict(name=name,path=path,texture=to.path_id,sprite=so.path_id,pixel_sha256=fingerprint[1],size=list(im.size),**(meta or{}));imports.append(row);return row
 names=a['a16_voltron_componentFilenames'].splitlines()
 # Input rectangles are explicit and reviewable; no faces or skin are in
 # these hair cuts. They include nine supplied long/braided/headband styles.
 haircuts=[(2,(65,635,365,837)),(2,(410,635,720,868)),(2,(750,635,1063,886)),(2,(1115,608,1385,893)),(2,(60,835,380,1086)),(2,(415,853,708,1086)),(2,(1100,868,1395,1086))]
 haircuts += [(3,(x,578,x+150,700))for x in [0]]
 haircuts += [(3,r)for r in [(24,802,164,973),(628,799,745,994),(1056,797,1170,958),(770,800,895,994),(911,792,1034,986),(1190,795,1328,985),(1343,798,1502,1008)]]
 assert len(haircuts)==len(PAID_HAIR)
 anchors=[]
 for gender,g in enumerate(['male','female']):
  for stage in range(6):
   face=next(n[:-4]for n in names if n.startswith(f'a16_faces-{g}-stage{stage}-base-'));bbox=textures[face].read().image.getchannel('A').getbbox();anchors.append(dict(gender=gender,stage=stage,bbox=list(bbox)))
   left,top,right,bottom=bbox;fw=right-left;fh=bottom-top
   for i,(sheet,rect)in enumerate(haircuts,1):
    raw=isolate(sheets[sheet].crop(rect));raw=raw.crop(raw.getbbox());long=i in [3,5,6,7,9,10,11,12,13,14,15];height=fh*(1.35 if long else .60);margin=.25 if long else .09
    im=fit(raw,(left-margin*fw,max(0,top-.22*fh),right+margin*fw,max(0,top-.22*fh)+height));ident=78000+i*12+gender*6+stage;name=f'a16_faces-{g}-stage{stage}-hair-base{100+i}-{ident:05d}'
    row=register(name,f'emoji/voltron/faces/hair/stage {stage} {g}/'+name,im,dict(kind='hair',id=f'{ident:05d}',style=i,gender=gender,stage=stage,feature=8,source_sheet=sheet,source_rect=list(rect)));catalogue.append(row);names.append(name+'.png')
   irisname=next(n[:-4]for n in names if n.startswith(f'a16_faces-{g}-stage{stage}-iris-base-'));iris=textures[irisname].read().image.convert('RGBA');alpha=iris.getchannel('A');boxes=[alpha.crop((x,0,x+250,500)).getbbox()for x in [0,250]]
   for l in range(1,7):
    for r in range(1,7):
     im=eyes(iris,EYE_HEX[l],EYE_HEX[r])
     pair=(l-1)*6+r-1;ident=80000+pair*12+gender*6+stage;name=f'a16_faces-{g}-stage{stage}-iris-base{100+pair}-{ident:05d}'
     row=register(name,f'emoji/voltron/faces/face/stage {stage} {g}/'+name,im,dict(kind='eyes',id=f'{ident:05d}',left=l,right=r,gender=gender,stage=stage,feature=1));catalogue.append(row);names.append(name+'.png')
   ident=88800+gender*6+stage;name=f'a16_faces-{g}-stage{stage}-iris-base149-{ident:05d}';row=register(name,f'emoji/voltron/faces/face/stage {stage} {g}/'+name,eyes(iris,'A8C9DC','A8C9DC'),dict(kind='genetic_eyes',id=f'{ident:05d}',trait=4,gender=gender,stage=stage,mood=-1,feature=1));names.append(name+'.png')
 # Repair the existing genetic-eye artwork without changing any saved ID,
 # resource key, stock portrait, or sprite geometry.
 genetic=json.loads((SOURCE/'native_v48/portrait43_catalog.json').read_text());repaired=[]
 for row in genetic:
  if row['trait']not in [5,12,13]:continue
  g=['male','female'][row['gender']];prefix=f'a16_faces-{g}-stage{row["stage"]}-iris-base-';stock=next(n[:-4]for n in names if n.startswith(prefix));original_iris=textures[stock].read().image.convert('RGBA');colors=('4E9ECA','D1A044')if row['trait']==5 else('4E9ECA','4E9ECA')if row['trait']==12 else('548F65','548F65');im=eyes(original_iris,*colors,mode=row['trait']);tex=textures[row['name']].read();tex.set_image(im,target_format=4);tex.save();repaired.append(row['name'])
 (ROOT/'portrait49_genetic_catalog.json').write_text(json.dumps(genetic+[r for r in imports if r['kind']=='genetic_eyes'],indent=2)+'\n')
 # Full beards use the supplied transparent beard layers. Other styles are
 # vector silhouettes authored in this import code, with an independent tint.
 beardcols=[1,0,0,8,3,3,9,9]
 for style in range(1,len(BEARDS)):
  for color in range(1,9):
   im=Image.new('RGBA',(500,500));d=ImageDraw.Draw(im);c='#'+HEX[color]
   if style==2:
    x=beardcols[color-1]*153;piece=sheets[3].crop((x+4,698,min(x+150,1536),788));im=fit(piece,(92,325,408,474))
   elif style==3:d.polygon([(213,372),(287,372),(280,445),(250,464),(221,445)],fill=c);d.rounded_rectangle((218,346,282,360),6,fill=c)
   elif style==4:d.polygon([(174,352),(227,339),(250,345),(273,339),(326,352),(292,365),(250,356),(208,365)],fill=c)
   elif style==5:
    for n in range(310):
     x=110+(n*47)%280;y=330+(n*31)%125
     if ((x-250)/145)**2+((y-345)/120)**2<1:d.ellipse((x,y,x+2,y+3),fill=c)
   elif style==6:d.rounded_rectangle((94,263,124,375),12,fill=c);d.rounded_rectangle((376,263,406,375),12,fill=c)
   # Clean-shaven uses the native no-added-layer path and needs no art.
   if style==1:continue
   ident=49300+style*10+color;register('a49_beard_'+str(ident),'emoji/voltron/accessories/custom49/a49_'+str(ident),im,dict(kind='beard',style=style,color=color,id=ident))
 for i in range(1,len(SCARS)):
  rect=(max(0,(i-1)*140),10,min(1774,(i-1)*140+138),150) if i<=8 else [(10,440,125,572),(610,438,694,572),(0,570,120,674),(475,438,582,574)][i-9]
  piece=sheets[5].crop(rect);im=fit(piece,(145,220,203,312)if i!=11 else(270,365,308,407));ident=49100+i;register('a49_scar_'+str(ident),'emoji/voltron/accessories/custom49/a49_'+str(ident),im,dict(kind='scar',style=i,id=ident,source_sheet=5,source_rect=list(rect)))
 for i in range(1,len(PATCHES)):
  row=0 if i<=12 else 1;col=i-1 if row==0 else i-13;x=col*(1774/12 if row==0 else 155);y=674 if row==0 else 774;rect=(round(x),y,min(1774,round(x+(1774/12 if row==0 else 155))),771 if row==0 else 887);im=fit(isolate(sheets[5].crop(rect)),(146,246,454,331));ident=49200+i;register('a49_patch_'+str(ident),'emoji/voltron/accessories/custom49/a49_'+str(ident),im,dict(kind='patch',style=i,id=ident,source_sheet=5,source_rect=list(rect)))
 # Readable sprite-backed icons replace missing font glyphs. All seven
 # sheets have concrete in-engine resources, with provenance in imports.json.
 icons={'49-hair':(2,(70,635,370,845)),'49-beard':(3,(5,697,151,790)),'49-skin':(3,(1370,20,1536,205)),'49-eye':(3,(15,405,165,568)),'49-scar':(5,(10,10,145,150)),'49-patch':(5,(0,674,149,784)),
        '49-wardrobe':(6,(13,824,179,959)),'49-hospital':(6,(925,677,1080,815)),'49-journal':(6,(477,680,625,813)),'49-handshake':(6,(351,824,533,964)),'49-health':(6,(183,680,326,815)),'49-brain':(4,(875,630,950,713)),
        '49-priest':(8,(205,178,414,461)),'49-bishop':(8,(411,95,622,461)),'49-cardinal':(8,(807,102,1018,461)),'49-pope':(8,(1015,51,1254,461)),
        '49-photographer':(8,(502,915,774,1235)),'49-official':(8,(887,902,1192,1235)),
        '49-basilica':(7,(0,0,650,590)),'49-conclave':(7,(650,168,1254,564)),'49-community':(7,(0,586,845,935)),'49-smoke':(7,(850,590,1254,945)),'49-gate':(7,(0,928,648,1254)),'49-square':(7,(648,928,1254,1254))}
 for name,(sheet,rect)in icons.items():
  raw=sheets[sheet].crop(rect);im=Image.new('RGBA',(500,500));raw.thumbnail((470,470),Image.Resampling.LANCZOS);im.alpha_composite(raw,((500-raw.width)//2,(500-raw.height)//2));register(name,'mayomods49/icons/'+name,im,dict(kind='icon',source_sheet=sheet,source_rect=list(rect)))
 for era in range(4):
  for kind in ['header','panel']:register(f'era{era}_{kind}',f'mayomods49/themes/era{era}_{kind}',pattern(era,kind),dict(kind='theme',era=era))
 # Existing careers/places pick the supplied assets by semantic role, never
 # by replacing the player's face or altering unrelated career behaviour.
 semantic=[('photograph','49-photographer'),('cardinal','49-cardinal'),('bishop','49-bishop'),('priest','49-priest'),('pope','49-pope'),('basilica','49-basilica'),('conclave','49-conclave'),('vatican','49-square')]
 uses=[]
 for key,value in list(a.items()):
  if key.startswith('genesis_v18_') and value.startswith('{'):
   doc=json.loads(value)
   for row in doc.get('Items',[]):
    title=str(row.get('Title','')).lower()
    for word,icon in semantic:
     if word in title:row['Icon']=icon;uses.append([key,row.get('Title'),icon]);break
   a[key]=json.dumps(doc,indent=2)
 a['a16_voltron_componentFilenames']='\r\n'.join(names)
 # Write changed/new TextAssets through the same ResourceManager as stock.
 for name,value in a.items():
  if name in texts and texts[name].read().m_Script==value:continue
  if name in texts:obj=texts[name]
  else:
   obj=copy.copy(texts['genesis_test_feature_events']);obj.path_id=nextid;nextid+=1;obj.data=obj.get_raw_data();file.objects[obj.path_id]=obj
   tree['m_Container'].append((('genesis_lists/'if value.startswith('{')else'genesis/')+name,dict(m_FileID=rid,m_PathID=obj.path_id)))
  v=obj.read();v.m_Name=name;v.m_Script=value;v.save()
 tree['m_Container'].sort(key=lambda x:x[0]);rm.save_typetree(tree)
 (ROOT/'assets.json').write_text(json.dumps(a,ensure_ascii=True,indent=2)+'\n');(ROOT/'portrait49_catalog.json').write_text(json.dumps(catalogue,indent=2)+'\n');(ROOT/'imports49.json').write_text(json.dumps(dict(inputs=[dict(file=p.name,sha256=sha(p.read_bytes()))for p in inp.glob('*.png')],imports=imports,anchors=anchors,semantic_uses=uses,repaired_genetic_eye_textures=repaired),indent=2)+'\n')
 for name,e in [('datapack',env),('data',data)]:
  raw=next(iter(e.files.values())).save(packer='original');(out/(name+'.unity3d')).write_bytes(raw)
 # Preserve the complete previous resource multiset, including legitimate
 # duplicate Texture2D/Sprite resource paths.
 assert Counter((p,json.dumps(v,sort_keys=True))for p,v in original)<=Counter((p,json.dumps(v,sort_keys=True))for p,v in tree['m_Container'])
 print(json.dumps(dict(passed=True,portraits=len(catalogue),imports=len(imports),unique_textures=len(emitted),paid_sheets=len(sheets),semantic_uses=len(uses))),flush=True)

if __name__=='__main__':build(*sys.argv[1:])
