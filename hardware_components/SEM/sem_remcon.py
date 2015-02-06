'''
Created on Feb 4, 2015

@author: Hao Wu
'''
from hardware_components import HardwareComponent
try:
    from equipment.SEM.zeiss_sem_remcon32 import ZeissSEMRemCon32

except Exception as err:
    print "could not load modules needed for ZeissSEMRemCon32:", err

REMCON_PORT='COM4'

class SEMRemCon(HardwareComponent):
     
    def setup(self):
        self.name='sem_remcon'
        self.debug='false'
        #create logged quantities
        self.magnification = self.add_logged_quantity('magnification', 
                                                   dtype=float,
                                                   ro=False,
                                                   vmin=5.0,
                                                   vmax=5.0e5,
                                                   unit='x')
        self.EHT = self.add_logged_quantity('EHT', 
                                                   dtype=float,
                                                   ro=False,
                                                   vmin=0.0,
                                                   vmax=40.0,
                                                   unit='kV')
        
        self.beam_blanking = self.add_logged_quantity('beam_blanking', 
                                                   dtype=int,
                                                   ro=False,
                                                   vmin=0,
                                                   vmax=1,
                                                   unit='',
                                                   choices=[('Off',0),('On',1)])
        #connect to GUI
        
    def connect(self):
        if self.debug: print "connecting to REMCON32"
        #connecting to hardware
        self.remcon=ZeissSEMRemCon32(REMCON_PORT)
        
        #connect logged quantity
        self.magnification.hardware_read_func= \
                self.remcon.read_magnification
        self.magnification.hardware_set_func= \
                self.remcon.write_magnification
        
        self.EHT.hardware_read_func= \
                self.remcon.read_EHT
        self.EHT.hardware_set_func= \
                self.remcon.write_EHT
        
        self.beam_blanking.hardware_read_func=\
                self.remcon.read_beam_blanking
        self.beam_blanking.hardware_set_func= \
                self.remcon.write_beam_blanking
    
    
    def disconnect(self):
        for lq in self.logged_quantities.values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
            
        self.remcon.close()
        
        del self.remcon