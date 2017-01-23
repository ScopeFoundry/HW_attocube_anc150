'''
Created on Jan 11, 2017

@author: lab
'''
import numpy as np
import time

class RandomNumberGenDev(object):
    """
    This is the low level dummy device object.
    Typically when instantiated it will connect to the real-world
    Methods allow for device read and write functions
    """
        
    def __init__(self, amplitude=1.0):
        """We would connect to the real-world here
        if this were a real device
        """
        self.write_amp(amplitude)
    
    def write_amp(self, amplitude):
        """
        A write function to change the device's amplitude
        normally this would talk to the real-world to change
        a setting on the device
        """
        self._amplitude = amplitude
            
    def read_rand_num(self):
        """Random number generator. 
        Acts as our scientific device picking up a lot of noise."""
        rand_data = np.random.ranf() * self._amplitude
        return rand_data
    
    def read_sine_wave(self):
        """ Acts like the device is generating a 1Hz sine wave
        with an amplitude set by write_amp
        """
        sine_data = np.sin(time.time()) * self._amplitude
        return sine_data
    
    