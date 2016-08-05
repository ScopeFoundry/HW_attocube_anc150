'''
Created on Jan 30, 2015

@author: Frank Ogletree LBNL
'''
from __future__ import division
import numpy as np
from math import pi as pi

class RasterGenerator(object):
    '''
    generates xy coordinates for SEM and related image scanning
    '''
    def __init__(self, **set_param ):
        '''
        call with dict values to override default params
        '''
        self.param = dict(points=1024, lines=768,
                          xmin=-10.0, xmax = 10.0, ymin = -10.0, ymax = 10.0,
                          xoffset = 0.0, yoffset = 0.0,
                          xsize = 100.0, ysize = 100.0,
                          angle = 0.0,
                          mode = 'raster', clip = True)
        
        for k, v in set_param.iteritems():
            self.param[k] = v  
        self.xrange= self.param['xmax']-self.param['xmin']
        self.yrange= self.param['ymax']-self.param['ymin']       
        self.clip()
        
    def clip(self):
        '''
        validate parameters, clip to fit max min
        '''
        self.param['points'] = max(1,self.param['points'])
        self.param['lines'] = max(1,self.param['lines'])     
            
        #other validation here
        #xy size scaled to allow rotation with aspect ratio
        #offset clipped to allow size...other methods possible

        xsize = 0.5*self.param['xsize']*self.xrange/100
        ysize = 0.5*self.param['ysize']*self.yrange/100
        angle = self.param['angle']/180.0*pi
        xmax = self.param['xmax']
        ymax = self.param['ymax']
        xx = abs(xsize*np.cos(angle)) + abs(ysize*np.sin(angle))
        yy = abs(xsize*np.sin(angle)) + abs(ysize*np.cos(angle))
        
        scale = max(xx/xmax, yy/ymax)
        if scale >= 1.0:
            self.param['xsize'] = 2.0 * xsize/self.xrange / scale *100.0
            self.param['ysize'] = 2.0 * ysize/self.yrange / scale *100.0
            xx /= scale
            yy /= scale
        self.param['xoffset'] = np.clip(self.param['xoffset']*self.xrange, -xmax + xx, xmax - xx)/self.xrange
        self.param['yoffset'] = np.clip(self.param['yoffset']*self.yrange, -ymax + yy, ymax - yy)/self.yrange
                   
        #other validation here
        #clipping goes here, check values
        #xy size scaled to allow rotation with aspect ratio
        #offset clipped to allow size...our use clipping function
                  
    def count(self):
        #points in raster scan
        return self.param['points'] * self.param['lines']
    
    def shape(self):
        return (self.param['lines'], self.param['points'])
    
    def data(self):
        '''
        generates interleaved xy coordinate array suitable for DAQmx output
        scan is rotated around center then translated to offsets in orginal frame
        flipping sign of size reverses scan direction
        single line scan has lines, ysize set to 1
        '''
        points = self.param['points']
        lines = self.param['lines']
        angle = self.param['angle']/180.0*pi
        pixels = points * lines
        xsize = self.param['xsize']*self.xrange/100
        ysize = self.param['ysize']*self.yrange/100
            
        x = np.zeros(pixels)
        y = np.zeros(pixels)
        buff_out = np.zeros(2*pixels)
        
        #print 'scan x y', xsize, ysize
        
        xramp = np.linspace(-0.5*xsize, 0.5*xsize, points)
        yramp = np.linspace(-0.5*ysize, 0.5*ysize, lines)
        
        for i in range(lines):
            x[i*points:(i+1)*points] = xramp
            y[i*points:(i+1)*points] = yramp[i]
        
        if angle != 0.0:
            x1 = np.copy(x)
            y1 = np.copy(y)
            x = x1*np.cos(angle) - y1*np.sin(angle)
            y = x1*np.sin(angle) + y1*np.cos(angle)
        
        x += self.param['xoffset']*self.xrange    
        y += self.param['yoffset']*self.yrange
        
        buff_out[::2] = x
        buff_out[1::2] = y   
        return buff_out
        
        
        