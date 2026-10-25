"""Retained full preview/save/cancel and native website command regressions."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent;sys.path[:0]=[str(SOURCE)]
from life_rework.validate_native import Machine,prior

def navigation(binary,fixture):
 original=SOURCE/'native_v53/test_native53.py';source=original.read_text()
 before="['Face editor','Hair & facial hair','Skin & eye colours','Genetic features','Scars & eyepatches','Inherited abilities','Back to New Life']"
 after="['Face editor','Hair & facial hair','Skin & eye colours','Genetic features','Scars & eyepatches','Inherited abilities','Surprise me','Reset this look','Modding community','Back to New Life']"
 assert source.count(before)==1;source=source.replace(before,after)
 source=source.replace("  for n,(key,options,label,icon,off)in enumerate(CATEGORIES,101):","  m.w(d['states']['era44']['va']+bias,2026)\n  for n,(key,options,label,icon,off)in enumerate(CATEGORIES,101):")
 ns={'__file__':str(original),'__name__':'retained_navigation_1104'};exec(compile(source,str(original),'exec'),ns);ns['ROOT']=Path(fixture);ns['Machine']=Machine;prior.ROOT=Path(fixture);ns['validate'](binary)
if __name__=='__main__':navigation(*sys.argv[1:])
