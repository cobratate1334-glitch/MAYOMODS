"""Retain the Genius smarts trait; appearance modifications are removed."""
from native_hooks import h
def handlers(b):
 genius=h.load_game()+'\nldr x0,[x8,#0x28]\ncbz x0,finish\ncmp w20,#0\nb.le finish\ncmp w20,#3\nb.gt finish\nmov w1,w20\nmov x2,xzr\nbl 0x2a83d1c\nb finish\n'
 return [('NativeGenius','life_v18','genius18',genius)]
