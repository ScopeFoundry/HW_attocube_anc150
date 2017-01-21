'''
Created on Jan 11, 2017

@author: lab
'''

from ScopeFoundry import HardwareComponent
from ScopeFoundryHW.random_gen.random_gen_dev import RandomNumberGenDev


class RandomNumberGenHW(HardwareComponent):
    
    name = 'random_gen'
    
    def setup(self):
        # Define your logged quantities here. These are slots which can be updated and read by all parties.
        self.settings.New(name='y_data', initial=0, dtype=float, ro=True)
        self.settings.New(name="sine_data", initial=0, dtype=float, ro=True)
    
    def connect(self):
        # Open connection to hardware:
        self.randgendev = RandomNumberGenDev(start=10,stop=50,range=40)
        
        
        # Connect logged quantity to hardware:
        self.settings.y_data.hardware_read_func = self.randgendev.rand_func
        self.settings.sine_data.hardware_read_func = self.randgendev.read_wave_data
        #Take an inital sample of the data.
        self.read_from_hardware()
        
    def disconnect(self):
        # Don't just stare at it, clean up your objects when you're done!
        #del self.randgendev
        pass