'''
Created on Aug 18, 2014

@author: Frank Ogletree
'''
from __future__ import division
import numpy as np
import NI_Daq

class ScanDAC(object):
    ''' calculates raster scan for SEM  '''

    def __init__(self,channel = 'X-6368/ao0:1'):
        self.lines = self.pixels = 300       
        self.x_size = self.y_size = 10.0
        self.x_offset = self.y_offset = self.angle = 0.0
        self.stop_mode = 'center offset'
        self.clock_rate = 5e5       
        
        self.channel = channel
        self.dac = NI_Daq.NI_DacTask(self.channel, "SEM ext scan")
            
    def out_array(self):
        '''
        generate output buffer in voltage space, (x,y) pairs interlaced, return to (0,0)
        FIX add clipping, better get and set
        '''
        angle = np.radians( self.angle )
        end = np.zeros(2)
        #symmetric scan, sawtooth, other waveforms go here
        x = np.linspace( -0.5 * self.x_size, 0.5 * self.x_size, self.pixels )
        y = np.linspace( -0.5 * self.y_size, 0.5 * self.y_size, self.lines )
        X, Y, = np.meshgrid( x, y )
        #rotate then translate in DAC frame
        Xr = X * np.cos(angle) - Y*np.sin(angle) + self.x_offset
        Yr = X * np.sin(angle) + Y*np.cos(angle) + self.y_offset
        scan = np.dstack( (Xr, Yr) ).flatten()
        if self.stop_mode == 'center offset':
            end[0] = self.x_offset
            end[1] = self.y_offset
            self.out_buffer = np.append( (scan, end) )
        elif self.stop_mode == 'start':
            end[0] = scan[0]
            end[1] = scan[1]
            self.out_buffer = np.append( (scan, end) )
        else:
            self.out_buffer = scan
        self.sample_count = int(len(self.out_buffer) / 2)   #samples per channel, not total samples!!
        return self.out_buffer
    
    def dac_setup(self):
        '''
        calculate scan array and program dac
        '''
        self.out_array()
        self.dac.set_rate(self.clock_rate, self.sample_count)
        self.clock_rate = self.dac.get_rate()
        self.dac.load_buffer(self.out_buffer)
             
if __name__ == '__main__':
    import time

    myscan = ScanDAC()
    
    myscan.x_offset = 2.0
    myscan.y_offset = -1.5
    myscan.lines = 768
    myscan.pixels = 1024
    myscan.x_size = 10.0
    myscan.y_size = 0.75 * myscan.x_size 
    myscan.stop_mode = None
    myscan.clockRate = 1e6
    
    for i in range( 10 ):
        myscan.angle += 30
        myscan.dac_setup()
        myscan.dac.start()
        print 'scan {}'.format(i)
        myscan.dac.wait( 10.0 )
        myscan.dac.stop()
        print 'scan done'

            