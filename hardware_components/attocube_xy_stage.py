'''
Created on Jul 24, 2014

@author: Edward Barnard
'''
from . import HardwareComponent
from equipment.attocube_ecc100 import AttoCubeECC100


X_AXIS = 0
Y_AXIS = 1
DEVICE_NUM = 0

class AttoCubeXYStage(HardwareComponent):

    def setup(self):
        self.name = 'attocube_xy_stage'
        self.debug = False
        
        # Created logged quantities
        self.x_position = self.add_logged_quantity("x_position", 
                                                   dtype=float,
                                                   ro=False,
                                                   vmin=-100e6,
                                                   vmax=100e6,
                                                   unit='nm'
                                                   )
        self.y_position = self.add_logged_quantity("y_position", 
                                                   dtype=float,
                                                   ro=False,
                                                   vmin=-100e6,
                                                   vmax=100e6,
                                                   unit='nm'
                                                   )
        
        self.x_step_voltage = self.add_logged_quantity("x_step_volatage",
                                                       dtype=float,
                                                       ro=False)
        
        # need enable boolean lq's
        
        # connect GUI
        # no custom gui yet
        
    def connect(self):
        if self.debug: print "connecting to attocube_xy_stage"
        
        # Open connection to hardware
        self.ecc100 = AttoCubeECC100(device_num=DEVICE_NUM, debug=self.debug)
        
        # connect logged quantities
        self.x_position.hardware_read_func = lambda:  self.ecc100.read_position_axis(X_AXIS)
        #self.x_position.hardware_set_func  = lambda x: self.ecc100.set_position_axis(X_AXIS, x)
        
        self.y_position.hardware_read_func = lambda:  self.ecc100.read_position_axis(Y_AXIS)
        #self.y_position.hardware_set_func  = lambda y: self.ecc100.set_position_axis(Y_AXIS, y)
        
    def disconnect(self):
        

        #disconnect logged quantities from hardware
        for lq in self.logged_quantities.values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        
        #disconnect hardware
        self.ecc100.close()
        
        # clean up hardware object
        del self.ecc100
        
        