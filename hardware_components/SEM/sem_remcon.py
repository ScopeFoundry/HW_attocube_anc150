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
        
        self.stigmatorX = self.add_logged_quantity('stigmatorX', 
                                                   dtype=float,
                                                   ro=False,
                                                   vmin=-100.0,
                                                   vmax=100.0,
                                                   unit='%')
         
        self.stigmatorY = self.add_logged_quantity('stigmatorY', 
                                                   dtype=float,
                                                   ro=False,
                                                   vmin=-100.0,
                                                   vmax=100.0,
                                                   unit='%')
          
        self.WD = self.add_logged_quantity('WD', 
                                                   dtype=float,
                                                   ro=False,
                                                   vmin=0.0,
                                                   vmax=121.0,
                                                   unit='mm')
        
#         self.probe_current = self.add_logged_quantity('probe_current', 
#                                                    dtype=float,
#                                                    ro=False,
#                                                    vmin=1.0e-14,
#                                                    vmax=2.0e-5,
#                                                    unit='A')
#         
#         
#         aperture_choices=list([('[1] 60.00 um',1),
#                                ('[2] 20.00 um',2),
#                                ('[3] 30.00 um',3),
#                                ('[4] 75.00 um',4),
#                                ('[5] 90.00 um',5),
#                                ('[6] 120.00 um',6)])
        
#         self.select_aperture = self.add_logged_quantity('select_aperture', 
#                                                    dtype=int,
#                                                    ro=True,
#                                                    vmin=1,
#                                                    vmax=6,
#                                                    unit='',
#                                                    choices=aperture_choices)
        
        self.external_scan = self.add_logged_quantity('external_scan', 
                                                   dtype=int,
                                                   ro=False,
                                                   vmin=0,
                                                   vmax=1,
                                                   unit='',
                                                   choices=[('Off',0),('On',1)])
        
        self.magnification.connect_bidir_to_widget(self.gui.ui.sem_magnification_doubleSpinBox)
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
        
        self.stigmatorX.hardware_read_func=\
                self.remcon.read_stigmatorX
        self.stigmatorX.hardware_set_func= \
                self.remcon.write_stigmatorX
                
        self.stigmatorY.hardware_read_func=\
                self.remcon.read_stigmatorY
        self.stigmatorY.hardware_set_func= \
                self.remcon.write_stigmatorY
                
        self.WD.hardware_read_func=\
                self.remcon.read_WD
        self.WD.hardware_set_func= \
                self.remcon.write_WD
                
#         self.probe_current.hardware_read_func=\
#                 self.remcon.read_probe_current
#         self.probe_current.hardware_set_func= \
#                 self.remcon.write_probe_current
                
#         self.select_aperture.hardware_read_func=\
#                 self.remcon.read_select_aperture
#         self.select_aperture.hardware_set_func= \
#                 self.remcon.write_select_aperture
                
        self.external_scan.hardware_read_func=\
                self.remcon.read_external_scan
        self.external_scan.hardware_set_func= \
                self.remcon.write_external_scan
        
        
    
    def disconnect(self):
        for lq in self.logged_quantities.values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
            
        self.remcon.close()
        
        del self.remcon