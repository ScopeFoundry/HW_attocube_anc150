from __future__ import division, print_function
from serial import Serial
import struct
import time
from _ast import Add

class AugerElectronAnalyzer(object):
    
    "Omicron EAC2200 NanoSAM 570" "Electron Analyser Control"
    "Omicron Multiplier Supplies 1127"
    "Omicron Mulit-channel receiver 538"
    
    def __init__(self, debug=True):
        
        self.debug=debug
        
        self.work_function = 4.5
        
        # prologix usb-gpib
        self.ser = Serial("COM8", )
        
    def write_ser(self, x):
        print( "write_ser", repr(x))
        self.ser.write(x)
        
    def write_cmd(self, address, cmd_num, value):
        print("address", address)
        print("cmd", hex(cmd_num))
        print('value', hex(value))
        # GPIB commands of the form:
        # 0x83|00|1A
        # 3 bytes:
        # first byte is command
        # commands of form with 0b 100x xxxx
        # 2nd,3d bytes contain value
        # except for 0x80 and 0x8000 bits (8, 16)
        # These bits get moved to MSB of the command byte
        # 0000 0000 | p000 0000 | q000 0000
        # to
        # 0pq0 0000 | 0000 0000 | 0000 0000
                
                
    
        cmd_bytes = (
            (cmd_num<<16) + value)
            # move 0x80 bit to 0x200000
            #((value & (1<<7 )) << (22-8 )) - (value & (1<<7 )) + 
            # move 0x8000 bit to 0x400000
            #((value & (1<<15)) << (23-16)) - (value & (1<<15))
            #((value & (1<<7 )) << (22-8 ))  +  ((value & (1<<15)) << (23-16)) + (value ^ ((1<<15) + (1<<7 )))
            #)
        
        
        print(hex(cmd_bytes))
        
        _bytes = [(cmd_bytes >> i & 0xff) for i in (16,8,0)]   
        
        # prologix usb-gpib
        self.write_ser("++addr%i\n" % address)
        esc_bytes = []
        for byte in _bytes:
            if byte in (13,10,27,43):
                esc_bytes.append(27)
            esc_bytes.append(byte)
        print("cmd_bytes" , (hex(cmd_bytes)))
        print("bytes", repr(bytes))
        print("esc", repr(esc_bytes))
        print(bytes(esc_bytes))
        self.write_ser(bytes(esc_bytes))
        
        #self.dev[address].write(cmd_bytes)
        
        
    def get_work_function(self):
        return self.work_function
    
    def set_work_function(self, wf):
        self.work_function = float(wf)
    
    def write_KE(self, ke_v):
        assert 0 <= ke_v <= 2200
        self.KE_V = float(ke_v)
        ke_int = int((ke_v-self.work_function/2200.)*65535)
        if self.retarding_mode == 'CRR':
            self.resolution_eV = self.KE_V/self.crr_ratio * 0.02
        self.write_cmd(1, 0x82, ke_int)
    
    def get_KE(self):
        return self.KE_V
    
    retarding_modes = dict(CAE=0, CRR=1)

    def write_state(self, multiplier_state, retarding_mode='CAE'):
        self.multiplier_state = bool(multiplier_state)
        assert retarding_mode in self.retarding_modes.keys()
        self.retarding_mode = retarding_mode
        val = 0x04*bool(multiplier_state) + 0x02*self.retarding_modes[retarding_mode]
        self.write_cmd(1, 0x85, val)

    def write_multiplier_state(self, state):
        return self.write_state(state, self.retarding_mode)

    def get_multiplier_state(self):
        return self.multiplier_state

    def write_retarding_mode(self, retarding_mode):
        return self.write_mode(self.multiplier_state, retarding_mode)
    
    def get_retarding_mode(self):
        return self.retarding_mode


    # CAE 
    def write_pass_energy(self, epass):
        assert 5.0 <= epass <= 500
        self.pass_energy = float(epass)
        val = int(float(epass)*44.69)
        self.resolution_eV = 0.02*epass
        self.write_cmd(1, 0x84, val)
    
    def get_pass_energy(self):
        return self.pass_energy
    
    # CRR
    def write_crr_ratio(self, crr_ratio):
        assert 1.5 <= crr_ratio <= 20.0
        self.crr_ratio = self.crr_ratio
        val = int(crr_ratio*3276.8)
        self.resolution_eV = self.KE_V/self.crr_ratio * 0.02
        self.write_cmd(1, 0x84, val)
    
    def get_crr_ratio(self):
        return self.crr_ratio
    
    def get_resolution(self):
        return self.resolution_eV
 
    ####  Quadrupole
    
    quad_cmds = dict(X1=0x81, Y1=0x82, X2=0x83, Y2=0x84)
    
    def write_Quad(self, quad, val):
        assert quad in self.quad_cmds.keys()
        assert -0.5 <= val <= 0.5
        val_int = int((val + 0.5)*65535)
        self.write_cmd(3,self.quad_cmds[quad], val_int)
    
    
    # setup procedure
    """
    write multipliers and mode
    set epass or crr_ratio
    set quadrupoles
    set KE
    set Fraction (for sweeps)
    set span (for sweeps)
    """
    
from ScopeFoundry import HardwareComponent

class AugerElectronAnalyzerHC(HardwareComponent):
    
    name = 'auger_electron_analyzer'
    
    def setup(self):
        self.settings.New("mode", dtype=str, choices=('CAE', 'CRR'))
        self.settings.New("multiplier", dtype=bool)
        self.settings.New("KE", dtype=float, unit='V', min=0, max=2200)
        self.settings.New("work_function", dtype=float, unit='eV', min=0, max=10, initial=4.5)
        self.settings.New("pass_energy", dtype=float, unit='V', min=5, max=500)
        self.settings.New("crr_ratio", dtype=float, min=1.5, max=20)
        self.settings.New("resolution", dtype=float, ro=True, unit='eV')
    
    def connect(self):
        E = self.e_analyzer = AugerElectronAnalyzer(debug=self.debug_mode.val)
        
        self.settings.mode.hardware_read_func = E.get_retarding_mode
        self.settings.mode.hardware_set_func = E.write_retarding_mode
        
        self.settings.multiplier.hardware_read_func = E.get_multiplier_state
        self.settings.multiplier.hardware_set_func = E.write_multiplier_state
        
        self.settings.KE.hardware_read_func = E.get_KE
        self.settings.KE.hardware_set_func  = E.write_KE

        self.settings.work_function.hardware_read_func = E.get_work_function
        self.settings.work_function.hardware_set_func = E.set_work_function
        
        self.settings.pass_energy.hardware_read_func = E.get_pass_energy
        self.settings.pass_energy.hardware_set_func = E.write_pass_energy
        
        self.settings.crr_ratio.hardware_read_func = E.get_crr_ratio
        self.settings.crr_ratio.hardware_set_func = E.write_crr_ratio

        self.settings.resolution.hardware_read_func = E.get_resolution
        
        for lqname in ['KE', 'pass_energy', 'crr_ratio']:
            getattr(self.settings, lqname).updated_value[None].connect(self.settings.resolution.read_from_hardware)
    
    def disconnect(self):
        self.e_analyzer.close()
        
        # disconnect lq's
        # TODO
        
        del self.e_analyzer
        

"""from ScopeFoundry import Measurement

class AugerElectronAnalyzerViewer(Measurement):"""

def set_address_gpib(port, address=1):
    port.write('++addr {:d}\n'.format(address))

def set_config_gpib(port):
    '''configure prologix usb GPIB for Omicron'''
    #no automatic read after write
    port.write("++auto 0\n")
    #assert gpib EOI after write
    port.write("++eoi 1\n")
    #no CR, LF after write
    port.write("++eos 3\n")
    #be controller, send to omicron
    port.write("++mode 1\n")
    #no CR, LF with read
    port.write("++eos 3\n")

def get_config_gpib(port):
    ''' get prologix gpib configuration'''
    port.write('++ver\n')
    print( port.readline())
    port.write("++auto\n")
    print( 'auto '+port.readline())
    port.write("++eoi\n")
    print( 'eoi '+port.readline())
    port.write("++eos\n")
    print( 'eos '+port.readline())
    port.write("++mode\n")
    print( 'mode '+port.readline())
    port.write("++addr\n")
    print( 'address '+port.readline())
    
def set_mode_omicron( mult=True, crr=True ):
    cmd = '\x85'
    val = 0
    if mult: val |= 0b100
    if crr: val |= 0b10
    s = b'' + cmd + chr(val)
    return s

def debug_omicron(s):
    print( " ".join("{:02x}".format(ord(c)) for c in s))
    print( " ".join("{:08b}".format(ord(c)) for c in s))

def gpib_string( s ):
    ''' prevent binary data from being interpreted
    as prologix configuration commands, add lf'''
    esc = chr(27)
    lf = '\n'
    cr = chr(0xd)
    plus = '+'
    
    out = b''
    for c in s:
        if c in (esc, lf, cr, plus ):
            out += esc
        out += c
    out += lf
    return out

def write_gpib( port, s ):
    out = gpib_string( s )
    debug_omicron(out)
    port.write( out )
    
def omicron_cmd_value( cmd, val ):
    '''cmd is command number, val is uint 16, format for omicron '''
    cmd &= 0x8f #commands are 0x8#
    v1 = (val & 0xff00)>>8
    v2 = val & 0xff
    if v1 & 0x80:
        cmd |= 0x40
        v1  &= 0x7f
    if v2 & 0x80:
        cmd |= 0x20
        v2  &= 0x7f
    s = b'' + chr(cmd) + chr(v1) + chr(v2)
    return s    

def set_omicron_volts( v ):
    max = 2200.0
    range = 0xffff
    cmd = 0x82
    if v > max: v = max
    if v < 0: v = 0
    val = int( v*range/max)
    return omicron_cmd_value( cmd, val )
    
if __name__ == '__main__':
    #a = AugerElectronAnalyzer()
    
    #a.write_state(True, 'CAE')
    
    #a.ser.close()
    
    port = Serial("COM8")
    set_config_gpib(port)
    set_address_gpib(port,1)
    get_config_gpib(port)
    write_gpib( port, set_mode_omicron(True, False) )
    write_gpib( port, set_omicron_volts( 1500 ))
    write_gpib( port, set_omicron_volts( 37.5 ))
    write_gpib( port, set_omicron_volts( 137.5 ))
    write_gpib( port, set_omicron_volts( 2200 ))
    time.sleep(10)
    write_gpib( port, set_mode_omicron(mult=False) )
    
    port.close()
    