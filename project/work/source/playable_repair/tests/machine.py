"""ARM64 boundary runner. Managed allocations are typed API doubles, not ART."""
from connected_life.validate_native import Machine as Previous,prior,X

class Machine(Previous):
    def __init__(self,raw,bias):
        super().__init__(raw,bias)
        if 'playable_repair_rx' in self.d:
            off,va,size=self.d['playable_repair_rx'];self.map(va+bias,size);self.u.mem_write(va+bias,raw[off:off+size])
        # Older isolated runners mark original hook resumes as stop traps.
        # This suite executes the method entry AND its actual original RET.
        self.map(0x321b4bc+bias,8);self.u.mem_write(0x321b4bc+bias,self.load(0x321b4bc,8))
    def blueprint(self,key,owner='life_rework',operation='=1',parsed=True):
        self.blueprint_model=True
        bp=self.alloc(0x100);self.q(bp+0x10,self.managed(owner));self.q(bp+0x18,self.managed(key));self.q(bp+0x20,self.managed(operation));self.u.mem_write(bp+0x30,bytes([bool(parsed)]));return bp
