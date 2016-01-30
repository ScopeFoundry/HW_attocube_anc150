'''
Created on Oct 29, 2015

@author: NIuser
'''
from ScopeFoundry import HardwareComponent
from equipment.NI_Daq import Dac
import random



class SEMSlowscanVout(HardwareComponent):
    
    name = "sem_slowscan_vout"
    
    def setup(self):
        lq_params = dict(  dtype=float, ro=False,
                           initial = 0,
                           vmin=-10,
                           vmax=10,
                           si = False,
                           unit='V')
        self.x_position = self.add_logged_quantity("x_position", **lq_params)
        self.y_position = self.add_logged_quantity("y_position", **lq_params)       

        self.x_position.reread_from_hardware_after_write = False
        self.x_position.spinbox_decimals = 3
        
        self.y_position.reread_from_hardware_after_write = False
        self.y_position.spinbox_decimals = 3
        
#        self.x_chan = self.add_logged_quantity('x_chan', dtype=str, initial='/X')

    def connect(self):
        if self.debug_mode.val: print "connecting to NI Dac output task"

        # Open connection to hardware
        self.dac = Dac('X-6368/ao0:1','SEM_slowscan_dac_out')
        self.dac.start()

        # connect logged quantities
        self.x_position.hardware_set_func  = self.write_x
        self.y_position.hardware_set_func  = self.write_y

    def disconnect(self):
        if self.debug_mode.val: print "disconnecting from NI Dac output"
        
        #disconnect logged quantities from hardware
        for lq in self.logged_quantities.values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        
        #disconnect hardware
        self.dac.close()
        # clean up hardware object
        del self.dac


    def write_x(self,val):
        self.dac.set((val,self.y_position.val))

    def write_y(self,val):
        self.dac.set((self.x_position.val,val))