'''
Created on Sep 23, 2014

@author: Benedikt 
'''
from . import HardwareComponent

try:
    from equipment.power_wheel_arduino import PowerWheelArduino
except Exception as err:
    print "Cannot load required modules for arduino power wheel:", err


PowerWheelArduinoPort = 'COM1'

class PowerWheelArduinoComponent(HardwareComponent): #object-->HardwareComponent
    
    name = 'power wheel arduino'
    debug = False
    
    def setup(self):
        self.debug = True
        
        self.phi = self.add_logged_quantity('phi', dtype=float, unit='', ro=True)
        
        
    def connect(self):
        if self.debug: print "connecting to arduino power wheel"
        
        # Open connection to hardware
        self.power_wheel = PowerWheelArduino(port=PowerWheelArduinoPort, debug=True)
        
        # connect logged quantities
        self.phi.hardware_set_func = \
             self.power_wheel.write_steps


        print 'connected to ',self.name
    

    def disconnect(self):

        # disconnect logged quantities from hardware
        # ///\
    
        #disconnect hardware
        self.power_wheel.close()
        
        # clean up hardware object
        del self.power_wheel
        
        print 'disconnected ',self.name
        
        
        
        

        
