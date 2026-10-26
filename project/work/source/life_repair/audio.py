"""Original procedural game effects; deterministic, mono PCM16, no recordings."""
import math,random,struct,wave
from pathlib import Path

def build(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);rate=22050
    for label,length in [('rifle',.34),('artillery',.9),('airraid',1.4)]:
        rng=random.Random(label);values=[];low=0.
        for i in range(int(rate*length)):
            t=i/rate;noise=rng.uniform(-1,1);low=.92*low+.08*noise
            if label=='rifle':v=.52*noise*math.exp(-t*65)+.2*math.sin(2*math.pi*105*t)*math.exp(-t*18)
            elif label=='artillery':v=(.6*low+.14*noise)*math.exp(-t*6)*(1-math.exp(-t*200))
            else:
                frequency=420+180*math.sin(t*math.pi*2);v=.12*math.sin(2*math.pi*frequency*t)*min(t*10,1,(length-t)*8)
            values.append(struct.pack('<h',round(max(-1,min(1,v))*32767)))
        with wave.open(str(out/(label+'.wav')),'wb')as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(b''.join(values))
if __name__=='__main__':build(__import__('sys').argv[1])
