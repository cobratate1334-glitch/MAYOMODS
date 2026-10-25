"""Era calendar, atomic accessory purchases, native portrait layers and UI.

Pinned to the released v43 ARM64 library. Persistent data lives in Genesis;
the only new BSS contains a New Life year and rooted temporary preview state.
"""
import copy,hashlib,json,re,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent
sys.path[:0]=[str(ROOT),str(SOURCE),str(SOURCE/'native_v29')]
from native_hooks import Builder,h
from native_v43.patch_native43 import Patch as Previous
from native_v42.patch_native42 import body
from native_v33.patch_native33 import root_guard
from catalog44 import ITEMS,ERAS,START_YEARS,REGIONS,STYLE_BASE,HEAD_TYPE,MOUTH_TYPE
BASE_SHA='c88b60926805a9edbaa567e61ab7b3e5e21c431a920a2e0215ef4a0228b22016'

class Patch(Previous):
 def __init__(self,raw):
  Builder.__init__(self,raw);assert hashlib.sha256(raw).hexdigest()==BASE_SHA
  self.base=json.loads((SOURCE/'native_v43/native_hooks.json').read_text());self.manifest=copy.deepcopy(self.base)
  self.tail=next(s for s in self.loads if s['p_vaddr']==self.base['segment_va'])
  self.cursor=0x6526800;self.code_start=self.cursor;self.strings_va=0x6540000
  self.strings=copy.deepcopy(self.base['strings']);self.string_cursor=max(v+len(s.encode())+1 for s,v in self.strings.items())
  self.states=copy.deepcopy(self.base['states']);self.routines=[];self.hooks=[];self.changed=[];self.serial=0
  self.old={r['name']:r for r in self.base['hooks']+self.base['routines']}
  self.newlife24=self.states['newlife24']['va'];self.newlife31=self.states['newlife31']['va']
  self.rw=next(s for s in self.loads if s['p_vaddr']==0x6570000)
  self.extra=(self.rw['p_vaddr']+self.rw['p_memsz']+15)&~15
  self.states['era44']=dict(va=self.extra,size=64)
 def replace(self,name,code):
  target=self.routine(name+'_v44',code);old=self.old[name]
  self.blob[self.off(old['stub']):self.off(old['stub'])+4]=h.asm(f'b {target:#x}',old['stub'])
  r=next(r for r in self.manifest['routines']if r['name']==name);r.update(source=f'b {target:#x}',length=4)
  self.changed.append([old['stub'],4,name]);return target
 def chain(self,name,old,code,ret=False):
  # A retained stub may itself already branch through another release's
  # hook. Preserve its actual entry instruction, including that branch.
  from capstone import Cs,CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN
  site=self.old[old]['stub']
  ins=next(Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN).disasm(bytes(self.blob[self.off(site):self.off(site)+4]),site))
  original=ins.mnemonic+' '+ins.op_str
  source=h.save()+'\n'+code+'\nfinish:\n'+h.restore()+'\n'+original+f'\nb {site+4:#x}'
  if ret:source+='\nreturn_custom:\n'+h.restore()+'\nret'
  va=self.add_code(name,source);r=self.routines.pop();self.blob[self.off(site):self.off(site)+4]=h.asm(f'b {va:#x}',site)
  self.hooks.append(dict(name=name,site=site,stub=va,resume=site+4,original=original,source=r['source'],length=r['length']))
  self.changed.append([site,4,name])
 def finish44(self):
  assert self.cursor<self.strings_va,hex(self.cursor)
  for s,va in self.strings.items():
   if s in self.base['strings']:continue
   data=s.encode()+b'\0';off=self.off(va);assert self.blob[off:off+len(data)]==b'\0'*len(data)
   self.blob[off:off+len(data)]=data;self.changed.append([va,len(data),'literal'])
  size=max(self.tail['p_filesz'],self.string_cursor-self.tail['p_vaddr']);assert self.tail['p_vaddr']+size<0x6570000
  p=self.e['e_phoff']+self.segs.index(self.tail)*56+32;struct.pack_into('<QQ',self.blob,p,size,size)
  q=self.e['e_phoff']+self.segs.index(self.rw)*56+40;struct.pack_into('<Q',self.blob,q,self.extra+64-self.rw['p_vaddr'])
  sites={r['site']for r in self.hooks};self.manifest['hooks']=[r for r in self.manifest['hooks']if r['site']not in sites]+self.hooks
  self.manifest['hooks'].sort(key=lambda r:(r['name']!='v18_saved_state',r['site']));self.manifest['routines']+=self.routines
  self.manifest.update(states=self.states,strings=self.strings,segment_size=size,binary_sha256=hashlib.sha256(self.blob).hexdigest(),base_v43_sha256=BASE_SHA,v44_new_code_range=[self.code_start,self.cursor],v44_changed_ranges=self.changed,v44_program_header_ranges=[[p,16],[q,8]])
  (ROOT/'native_hooks.json').write_text(json.dumps(self.manifest,indent=2)+'\n');return bytes(self.blob)

def custom_guard(reg='x0'):
 return f'cbz {reg},finish\nldr w9,[{reg},#0x14]\nmov w10,#{STYLE_BASE+1}\nsub w9,w9,w10\ncmp w9,#{len(ITEMS)}\nb.hs finish\n'

def portrait_hooks(b):
 # Accessory resources use ordinary native sprite loading. Unrelated stock
 # accessory IDs, type-specific positioning and palettes remain untouched.
 s=custom_guard()
 for i in ITEMS:
  s+=f'cmp w9,#{i["id"]-1}\nb.ne filename44_{i["id"]}\n'+b.string(f'a44_accessory_{i["id"]:02d}')+'str x0,[sp]\nb return_custom\n'+f'filename44_{i["id"]}:\n'
 s+='b finish';b.install('v44_accessory_filename',0x2f27738,s,ret=True)
 b.install('v44_accessory_folder',0x2f277c0,custom_guard()+b.string('emoji/voltron/accessories/era44')+'str x0,[sp]\nb return_custom',ret=True)
 b.install('v44_accessory_front_layer',0x2f28020,custom_guard()+'mov w9,#14\nstr x9,[sp]\nb return_custom',ret=True)
 # Reuse the native headwear hair mask and the native empty mask. Work on
 # the loaded enum register, without changing the accessory or its save ID.
 s='cbz x19,finish\nldr w9,[x19,#0x14]\nmov w10,#44001\nsub w9,w9,w10\ncmp w9,#27\nb.hs finish\ncmp w8,#6\nb.ne mouth_mask44\nstr xzr,[sp,#64]\nb finish\nmouth_mask44:\ncmp w8,#7\nb.ne finish\nmov w9,#3\nstr x9,[sp,#64]\nb finish'
 b.install('v44_accessory_native_hair_masks',0x2f280cc,s)
 anchors=json.loads((ROOT/'face_anchors44.json').read_text())
 def fp(value,slot):
  bits=struct.unpack('<I',struct.pack('<f',value))[0]
  return f'movz w9,#{bits&65535}\nmovk w9,#{bits>>16},lsl #16\nstr w9,[sp,#{slot}]\n'
 for mode,site in [('position',0x2f27b50),('scale',0x2f27dcc)]:
  s=custom_guard()+'cmp w1,#1\nb.hi finish\ncmp w2,#5\nb.hi finish\nldr w26,[x0,#0x10]\n'
  for n,a in enumerate(anchors):
   g=int(a['gender']=='female');stage=a['stage'];left,top,right,bottom=a['base'];scale=(right-left)/402
   s+=f'cmp w1,#{g}\nb.ne anchor44_{n}_{mode}\ncmp w2,#{stage}\nb.ne anchor44_{n}_{mode}\n'
   if mode=='scale':s+=fp(scale,256)+fp(scale,272)+'b return_custom\n'
   else:
    # Every headwear texture has its brim at y=320; mouth textures use the
    # adult portrait coordinate space. Positions are native fractions.
    y=(top+.23*(bottom-top)-70*scale)/500
    s+=f'cmp w26,#{MOUTH_TYPE}\nb.eq mouth_anchor44_{n}\n'+fp((left+right)/1000,256)+fp(y,272)+'b return_custom\n'
    s+=f'mouth_anchor44_{n}:\n'+fp(((left+right)/2+30*scale)/500,256)+fp((top+(250-52)*(bottom-top)/446+(90+14*g)*scale)/500,272)+'b return_custom\n'
   s+=f'anchor44_{n}_{mode}:\n'
  s+='b finish';b.install('v44_accessory_'+mode,site,s,ret=True)
 # Temporary previews never become the saved outfit. Serialization applies
 # the actual owned slots; only image requests may display the preview.
 s=f'adr x28,{b.extra:#x}\nldr x0,[x28,#16]\ncbz x0,no_preview_handle44\nbl 0x223e784\nno_preview_handle44:\nstr xzr,[x28,#16]\nstr wzr,[x28,#24]\nb finish'
 clear=b.routine('v44_clear_preview',s);b.clear_preview=clear
 s='str xzr,[sp]\ncbz x0,finish\nmov x27,x0\nmov w28,w1\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr x8,[x8,#0x80]\ncbz x8,finish\nldr x8,[x8,#0x30]\ncmp x8,x27\nb.ne finish\n'+b.ctx('era44')+b.get('Head','w25')+b.get('Mouth','w26')
 s+=f'cbz w28,saved_slots44\nadr x28,{b.extra:#x}\nldr w24,[x28,#24]\ncbz w24,saved_slots44\nldr x0,[x28,#16]\ncbz x0,saved_slots44\nbl 0x223e73c\nmov x22,x0\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncmp x8,x22\nb.ne saved_slots44\n'
 for item in ITEMS:
  s+=f'cmp w24,#{item["id"]}\nb.ne preview_slot44_{item["id"]}\nmov '+('w26'if item['slot']=='Mouth'else'w25')+f',w24\nb saved_slots44\npreview_slot44_{item["id"]}:\n'
 s+='saved_slots44:\ncmp w23,#18\ncsel w26,w26,wzr,ge\nmov w28,#0\n'
 # Temporarily replace any stock headwear, retaining its native style so
 # removing the mod hat restores it. No two hats overlap on the portrait.
 s+='cbz w25,restore_native_head44\n'+b.get('NativeHeadSaved','w24')+'cbnz w24,hide_native_head44\nmov x0,x27\nmov w1,#0\nmov x2,xzr\nbl 0x2f36824\nmov w24,w0\n'+b.put('NativeHead')+b.set('NativeHeadSaved',1)+'hide_native_head44:\nmov x0,x27\nmov w1,#0\nmov x2,xzr\nbl 0x2f36824\ncbz w0,native_head_done44\nmov x0,x27\nmov w1,#0\nmov w2,#0\nmov x3,xzr\nbl 0x2f36ae4\nmov w28,#1\nb native_head_done44\nrestore_native_head44:\n'+b.get('NativeHeadSaved','w24')+'cbz w24,native_head_done44\n'+b.get('NativeHead','w24')+'mov x0,x27\nmov w1,#0\nmov w2,w24\nmov x3,xzr\nbl 0x2f36ae4\n'+b.set('NativeHeadSaved',0)+'mov w28,#1\nnative_head_done44:\n'
 for slot,reg in [(HEAD_TYPE,'w25'),(MOUTH_TYPE,'w26')]:
  s+=f'cmp {reg},#27\nb.ls valid_slot44_{slot}\nmov {reg},#0\nvalid_slot44_{slot}:\nmov x0,x27\nmov w1,#{slot}\nmov x2,xzr\nbl 0x2f36824\nmov w22,w0\nmov w24,#0\ncbz {reg},desired_slot44_{slot}\nmov w24,#44000\nadd w24,w24,{reg}\ndesired_slot44_{slot}:\ncmp w22,w24\nb.eq next_slot44_{slot}\nmov x0,x27\nmov w1,#{slot}\nmov w2,w24\nmov x3,xzr\nbl 0x2f36ae4\nmov w28,#1\nnext_slot44_{slot}:\n'
 s+='str x28,[sp]\nb finish';apply=b.routine('v44_apply_wardrobe',s);b.apply_wardrobe=apply
 invalidate='bl 0x2f34138\ncbz x0,finish\nldr x1,[x27,#0x10]\nmov x2,xzr\nbl 0x2f4d2d8\n'
 for name,base_name,preview in [('save','v43_saved_appearance_before_data',0),('image','v43_appearance_before_cached_emoji',1)]:
  s='cbz x19,finish\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr x8,[x8,#0x80]\ncmp x8,x19\nb.ne finish\nldr x27,[x19,#0x30]\ncbz x27,finish\nmov x0,x27\n'+f'mov w1,#{preview}\nbl {apply:#x}\ncbz w0,finish\n'+invalidate+'b finish'
  b.chain('v44_wardrobe_before_'+name,base_name,s)
 # The shared lazy CSV dismiss handler is also used by the preview's X.
 b.install('v44_dismiss_ends_preview',0x2cb712c,f'bl {clear:#x}\nb finish')
 for n,site in enumerate([0x3086c6c,0x3086ef8]):
  s='cbz x0,finish\nmov x8,x0\n'+h.compare_key('scenario.activitiesV18.era44_preview','finish','clear_preview44')+f'\nclear_preview44:\nbl {clear:#x}\nb finish'
  # Chain v42's selected-relative refresh at its current stub.
  b.chain('v44_scene_ends_preview_'+str(n),'v42_relative_dialog_'+str(n),s)

def commerce(b):
 # Derive the calendar from the saved birth year and actual hero age. This
 # survives reloads and duplicate callbacks, and rewinds correctly with age.
 s=b.ctx('era44')+b.get('BirthYear','w25')+'cmp w25,#1\nb.ge birth_exists44\nmov w25,#2026\nsub w25,w25,w23\n'+b.put('BirthYear','w25')+'birth_exists44:\nadd w26,w25,w23\n'+b.put('Year','w26')+'mov w27,#0\ncmp w26,#1930\nb.lt era_ready44\nmov w27,#1\ncmp w26,#1960\nb.lt era_ready44\nmov w27,#2\ncmp w26,#1990\nb.lt era_ready44\nmov w27,#3\nera_ready44:\n'+b.put('Era','w27')
 descriptions=['Bowlers, top hats and newsboy caps in a traditional hat shop.','Fedoras, trilbies and berets in a quiet hat parlour.','Straw styles, pork pies and pillboxes in a colourful boutique.','Caps, beanies, bucket hats and everyday streetwear.']
 for e,(name,year,shop,icon)in enumerate(ERAS):
  s+=f'cmp w27,#{e}\nb.ne era_name44_{e}\n'+b.text('EraName',name)+b.text('ShopName',shop)+b.text('ShopDescription',descriptions[e])+f'b country44\nera_name44_{e}:\n'
 s+='country44:\n'+b.set('Regional',0)+h.load_game()+'\nldr x0,[x8,#0x28]\ncbz x0,offers44\nmov x1,xzr\nbl 0x2c38288\ncbz x0,offers44\nldr x22,[x0,#0x90]\ncbz x22,offers44\n'+b.textptr('Country')+'mov x8,x22\n'
 for n,country in enumerate(REGIONS):s+=h.compare_key(country,'regional44','country_next44_'+str(n))+'\ncountry_next44_'+str(n)+':\n'
 s+='b offers44\nregional44:\n'+b.set('Regional',1)+'offers44:\n'
 for item in ITEMS:
  i=item['id'];base=item['base_price'];origin=item['era'];vintage=not item['regional']
  s+=f'mov w24,#{base}\nlsl w25,w24,w27\nmov w28,#0\ncmp w27,#{origin}\nb.lt no_offer44_{i}\n'
  if item['regional']:s+=b.get('Regional','w28')
  else:
   s+=f'mov w28,#1\nb.eq no_offer44_{i}\nadd w9,w26,#{i}\nmov w10,#3\nudiv w11,w9,w10\nmsub w9,w11,w10,w9\ncmp w9,#0\ncset w28,eq\nadd w25,w25,w25,lsr #1\n'
  s+=f'no_offer44_{i}:\n'
  if item['slot']=='Mouth':s+='cmp w23,#18\ncsel w28,w28,wzr,ge\n'
  s+=b.put('Price'+str(i),'w25')+b.put('Available'+str(i),'w28')+b.get('Owned'+str(i),'w24')
  s+=f'cbnz w24,label_owned44_{i}\ncbz w28,label_unavailable44_{i}\n'+b.text('Label'+str(i),'In stock · '+('Regional collection'if item['regional']else'Vintage find'if origin<3 else'Current collection'))+f'b label_done44_{i}\nlabel_owned44_{i}:\n'+b.text('Label'+str(i),'Owned · Wear from your wardrobe')+f'b label_done44_{i}\nlabel_unavailable44_{i}:\n'+b.text('Label'+str(i),'Unavailable this year')+f'label_done44_{i}:\n'
 for slot in ['Head','Mouth']:
  s+=b.get(slot,'w25')+b.text(slot+'Name','None')
  for item in ITEMS:
   if item['slot']!=('Mouth'if slot=='Mouth'else'Headwear'):continue
   s+=f'cmp w25,#{item["id"]}\nb.ne name_{slot}44_{item["id"]}\n'+b.text(slot+'Name',item['name'])+f'b name_{slot}44_done\nname_{slot}44_{item["id"]}:\n'
  s+=f'name_{slot}44_done:\n'
 s+='b finish';sync=b.routine('v44_calendar_and_stock',s);b.sync=sync
 s=b.ctx('era44')+b.get('Selected','w19')
 for item in ITEMS:
  i=item['id'];s+=f'cmp w19,#{i}\nb.ne selected44_{i}\n'+b.text('ItemName',item['name'])+b.get('Price'+str(i))+b.put('Price')+b.get('Available'+str(i),'w25')+b.put('Available','w25')+b.get('Owned'+str(i),'w26')+b.put('Owned','w26')
  s+=f'cbnz w26,item_owned44_{i}\ncbz w25,item_unavailable44_{i}\n'+b.text('StockLabel','Available from this year’s collection. Buying debits your real game balance and adds it to your permanent wardrobe.')+f'b finish\nitem_owned44_{i}:\n'+b.text('StockLabel','You own this piece. Wear it free, in any era.')+f'b finish\nitem_unavailable44_{i}:\n'+b.text('StockLabel','This piece is not stocked this year. Check its original era, vintage rotation or regional collection. Mouth accessories are available from age 18.')+f'b finish\nselected44_{i}:\n'
 s+='b finish';select=b.routine('v44_selected_item',s)
 s=f'bl {sync:#x}\n'+b.ctx('era44')+b.get('Action','w20')+f'cmp w20,#100\nb.lt operation44\nsub w19,w20,#100\ncmp w19,#1\nb.lt finish\ncmp w19,#27\nb.hi finish\n'+b.put('Selected','w19')+f'bl {select:#x}\nb finish\noperation44:\ncmp w20,#1\nb.eq end_preview44\ncmp w20,#5\nb.eq end_preview44\ncmp w20,#2\nb.eq buy44\ncmp w20,#3\nb.eq equip44\ncmp w20,#4\nb.eq preview44\ncmp w20,#400\nb.eq remove_head44\ncmp w20,#401\nb.eq remove_mouth44\ncmp w20,#402\nb.eq remove_both44\n'
 # High numbered outfit commands are checked before the item selection range.
 # Their dispatcher entry below branches directly here.
 for n in range(1,4):
  s+=f'cmp w20,#{600+n}\nb.eq save_outfit44_{n}\ncmp w20,#{610+n}\nb.eq load_outfit44_{n}\n'
 s+='b finish\nend_preview44:\n'+f'bl {b.clear_preview:#x}\nb wardrobe_changed44\nremove_both44:\n'+b.set('Head',0)+b.set('Mouth',0)+'b wardrobe_changed44\nremove_head44:\n'+b.set('Head',0)+'b wardrobe_changed44\nremove_mouth44:\n'+b.set('Mouth',0)+'b wardrobe_changed44\n'
 for n in range(1,4):
  s+=f'save_outfit44_{n}:\n'+b.get('Head')+b.put(f'Outfit{n}Head')+b.get('Mouth')+b.put(f'Outfit{n}Mouth')+b.set(f'Outfit{n}Saved',1)+b.text('Result',f'Outfit {n} saved for this character.')+'b finish\n'
  s+=f'load_outfit44_{n}:\n'+b.get(f'Outfit{n}Saved')+'cbz w24,empty_outfit44\n'+b.get(f'Outfit{n}Head')+b.put('Head')+b.get(f'Outfit{n}Mouth')+b.put('Mouth')+b.text('Result',f'Wearing outfit {n}.')+'b wardrobe_changed44\n'
 s+='empty_outfit44:\n'+b.text('Result','That outfit slot is empty. Save your current outfit first.')+'b finish\npreview44:\n'+b.get('Selected','w19')+'cmp w19,#1\nb.lt finish\ncmp w19,#27\nb.hi finish\n'
 # Cosmetic preview can show unavailable headwear; adult mouth rule remains.
 s+='cmp w23,#18\nb.ge preview_age44\ncmp w19,#1\nb.eq preview_underage44\ncmp w19,#16\nb.eq preview_underage44\ncmp w19,#17\nb.eq preview_underage44\npreview_age44:\n'+f'bl {b.clear_preview:#x}\n'+h.load_game()+f'\nldr x0,[x8,#0x28]\nmov w1,#0\nbl 0x223e704\nadr x28,{b.extra:#x}\nstr x0,[x28,#16]\nstr w19,[x28,#24]\nb wardrobe_changed44\npreview_underage44:\n'+b.text('Result','Mouth accessories are available from age 18.')+'b finish\nbuy44:\nmov w28,#1\nb item_action44\nequip44:\nmov w28,#0\nitem_action44:\n'+b.get('Selected','w19')
 for item in ITEMS:
  i=item['id'];slot='Mouth'if item['slot']=='Mouth'else'Head'
  s+=f'cmp w19,#{i}\nb.ne item_action44_{i}\n'
  if item['slot']=='Mouth':s+='cmp w23,#18\nb.lt not_available44\n'
  s+=b.get('Owned'+str(i),'w25')+f'cbnz w25,wear_item44_{i}\ncbz w28,not_owned44\n'+b.get('Available'+str(i),'w25')+'cbz w25,not_available44\n'+b.get('Price'+str(i),'w25')+'cmp w25,#1\nb.lt not_available44\n'
  s+=h.load_game()+'\nldr x8,[x8,#0x20]\ncbz x8,finish\nldr x26,[x8,#0xe8]\ncbz x26,finish\nldr d0,[x26,#0x10]\nscvtf d1,w25\nfcmp d0,d1\nb.lt insufficient44\nb.vs insufficient44\nfneg d0,d1\nmov x0,x26\nmov x1,xzr\nbl 0x2a6eb5c\n'+b.set('Owned'+str(i),1)+f'wear_item44_{i}:\n'+b.put(slot,'w19')+b.text('Result','Now wearing '+item['name']+'. This piece remains in your wardrobe as the years pass.')+b.set('BuyStatus',1)+'b wardrobe_changed44\n'+f'item_action44_{i}:\n'
 s+='b finish\nnot_owned44:\n'+b.set('BuyStatus',2)+b.text('Result','You do not own this piece yet. Choose Buy & wear to purchase it.')+'b finish\nnot_available44:\n'+b.set('BuyStatus',3)+b.text('Result','This piece is not available here this year. Your balance was not charged.')+'b finish\ninsufficient44:\n'+b.set('BuyStatus',4)+b.text('Result','You do not have enough money for this purchase. Your balance was not charged.')+'b finish\nwardrobe_changed44:\n'+f'bl {sync:#x}\n'+h.load_game()+'\nldr x8,[x8,#0x28]\ncbz x8,finish\nldr x8,[x8,#0x80]\ncbz x8,finish\nldr x27,[x8,#0x30]\ncbz x27,finish\nmov x0,x27\nmov w1,#1\n'+f'bl {b.apply_wardrobe:#x}\ncbz w0,finish\nbl 0x2f34138\ncbz x0,finish\nldr x1,[x27,#0x10]\nmov x2,xzr\nbl 0x2f4d2d8\nb finish'
 # Commands 400+ are operations, while 101..127 choose catalogue entries.
 s=s.replace('cmp w20,#100\nb.lt operation44','cmp w20,#128\nb.ge operation44\ncmp w20,#100\nb.lt operation44')
 action=b.routine('v44_dealer_action',s)
 s='tbz w0,#0,finish\ncbz x19,finish\ncbz x21,finish\nldr x8,[x21,#0x10]\ncbz x8,finish\n'+h.compare_key('era44','owner44','finish')+'\nowner44:\nldr x8,[x19,#0x18]\ncbz x8,finish\n'+h.compare_key('Action','action44','finish')+f'\naction44:\ncmp w20,#0\nb.eq finish\nbl {action:#x}\nb finish'
 b.chain('v44_saved_dealer_commands','v41_saved_parole_pulses',s)
 b.chain('v44_yearly_calendar','v41_yearly_checkin_enforcement',f'bl {b.clear_preview:#x}\nbl {sync:#x}\nb finish')

def patch(raw):
 b=Patch(raw);portrait_hooks(b);commerce(b)
 from newlife44 import hooks
 hooks(b)
 return b.finish44()
if __name__=='__main__':Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()));print('v44 native era patch built',flush=True)
