"""Stable, per-life cosmetic IDs. Colour variants are not separate styles."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent
OWNER='custom49'
PREFIX='scenario.activitiesV18.custom49_'
PAID_HAIR=['Silver tousle','Silver fringe','Silver waves','Silver bun','Long silver layers','Twin silver braids','Silver bob',
           'Short textured crop','Long centre part','Leather headband','Beaded braid','Bone headband','Side-bone braid','Bone crown','Feathered waves']
HAIR=['Natural hair']+PAID_HAIR
COLOURS=['Natural colour','Soft black','Espresso','Chestnut','Copper','Honey blond','Platinum','Silver','White']
HEX=['','252326','493329','79533A','B56A3F','E9C56F','EEE2C4','B8B7BB','F3F1ED']
EYES=['Natural eyes','Brown','Hazel','Green','Blue','Grey','Amber']
EYE_HEX=['','79502F','A48B45','548F65','4E9ECA','91A5B0','D1A044']
SKIN=['Natural skin','Porcelain','Ivory','Warm beige','Golden','Tan','Brown','Deep brown','Ebony']
SKIN_HEX=['','F5D8C8','EFC5A3','DDA875','CE9257','AA7347','865337','603C2C','3B2923']
BEARDS=['Natural facial hair','Clean shaven','Full beard','Goatee','Moustache','Stubble','Sideburns']
SCARS=['No added scar','Fine brow scar','Double cheek scar','Crossed cheek scar','Long cheek scar','Crossed brow scar','Arched brow scar','Short cheek scar','Stitched cheek scar','Star scar','Long forehead scar','Small chin scar','Healed cheek mark']
PATCHES=['No eyepatch','Classic black','Brown leather','Charcoal','Round black','Smooth grey','Crimson','White','Skull','Gold rim','Silver dome','Armoured black','Plain cloth','Cross','Chain','Red cross','Eyelets','Studded','Camouflage','Flame','Bandage','Fur','Red lens']
MARKS=['No rare appearance trait','Freckles','Birthmark','Vitiligo','Albinism','Heterochromia','Dimples','Curly hair texture','Dense freckles','Port-wine birthmark','Cafe-au-lait mark','Piebald patches','Sectoral heterochromia','Central heterochromia','Beauty spot']
CATEGORIES=[('Hair',HAIR,'Hairstyle','49-hair'),('HairColour',COLOURS,'Hair colour','49-hair'),('Beard',BEARDS,'Facial hair','49-beard'),('BeardColour',['Automatic colour']+COLOURS[1:],'Facial hair colour','49-beard'),('Skin',SKIN,'Skin tone','49-skin'),('LeftEye',EYES,'Left eye','49-eye'),('RightEye',EYES,'Right eye','49-eye'),('Mark',MARKS,'Genetic appearance','49-skin'),('Scar',SCARS,'Scars','49-scar'),('Patch',PATCHES,'Eyepatches','49-patch')]
FIELDS=[c[0] for c in CATEGORIES if c[0]!='Mark']
COMMANDS=[]
for group,(key,options,title,icon) in enumerate(CATEGORIES,1):
 for value,label in enumerate(options):
  COMMANDS.append(dict(code=group*100+value,key=key,value=value,label=label,list='genesis_v18_custom49_'+key.lower(),scene=PREFIX+str(group*100+value),icon=icon))
for slot in range(1,4):
 for op,base in [('Save',2000),('Load',2100)]:COMMANDS.append(dict(code=base+slot,key=op,value=slot,label=f'{op} look {slot}',list='genesis_v18_custom49_looks',scene=PREFIX+str(base+slot),icon='49-wardrobe'))
COMMANDS.append(dict(code=2200,key='Reset',value=0,label='Restore natural cosmetics',list='genesis_v18_custom49',scene=PREFIX+'2200',icon='49-wardrobe'))
# Native accessory records are an extensible list, not an indexed enum array.
# These independent slots leave the original glasses, headwear and v44 hats alone.
ACCESSORY_SLOTS={'Scar':8,'Patch':9,'Beard':10}
ACCESSORY_BASE={'Scar':49100,'Patch':49200,'Beard':49300}
