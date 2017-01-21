'''
Created on Jan 11, 2017

@author: lab
'''
import numpy as np
import time

class RandomNumberGenDev(object):
    
    name = 'random_gen_equipment'
    
    def __init__(self, start, stop, range):
        """Define some variables here from the get-go."""
        self.start = start
        self.stop = stop
        self.range = range
        
    def read_num(self):
        """Some other function"""
        read = np.linspace(self.start, self.stop, self.range)
        return read
    
    def rand_func(self):
        """Random number generator. Acts as our scientific device picking up a lot of noise."""
        y_data = np.random.ranf()
        return y_data
    
    def read_wave_data(self):
        #x = np.linspace(self.start, self.stop, self.range)
        data = np.sin(time.time())
        return data