"""Reuse exactly the four earlier illustrated atlas panels the owner selected."""
from pathlib import Path
from PIL import Image
ATLAS=Path(__file__).resolve().parents[1]/'native_immersion/inputs/war_background_atlas.png'
def artwork():
    atlas=Image.open(ATLAS).convert('RGBA')
    for i,name in enumerate(['ww1','post1','ww2','post2']):
        x=i%2*512;y=i//2*768
        yield 'native1109/background/'+name,atlas.crop((x,y,x+512,y+768)),dict(kind='restored-original-illustration',atlas_rect=[x,y,512,768],original_asset='native_immersion/inputs/war_background_atlas.png')
