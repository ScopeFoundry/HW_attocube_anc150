'''
Created on Feb 4, 2015

@author: NIuser
'''
from hardware_components import HardwareComponent
try:
    from equipment.SEM.zeiss_sem_remcon32 import ZeissSEMRemCon32

except Exception as err:
    print "could not load modules needed for ZeissSEMRemCon32:", err


class SemRemCon(HardwareComponent):
    
    name='sem_remcon'
    
    def setup(self):
        #create logged quantities
        self.port = self.add_logged_quantity('port', 
                                                   dtype=int,
                                                   ro=False,
                                                   vmin=1,
                                                   vmax=7,
                                                   unit='')