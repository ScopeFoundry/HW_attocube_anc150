'''
Created on Apr 3, 2015

@author: Hao Wu
'''

class RateConverter(object):
    '''
    classdocs
    '''

    def __init__(self,num_points,num_lines,sample_rate):
        '''
        all unit in ms
        '''
        self.name='rate_converter'
        self.num_points=num_points
        self.num_lines=num_lines
        '''
        hardware sample rate in Hz
        '''
        self.hardware_sample_rate=sample_rate
        self.ms_per_sample=1000.0/self.hardware_sample_rate
        self.num_pixels=self.num_lines*self.num_points
        self.sample_per_pixel=1
        
    def pixel_rate(self,ms_per_pixel):
        self.ms_per_pixel=ms_per_pixel
        self.sample_per_pixel=int(1.0*self.ms_per_pixel/self.ms_per_sample)
        if self.sample_per_pixel==0:
            self.sample_per_pixel=1
        self.update_rate()
        return self.sample_per_pixel
    
    def line_rate(self,ms_per_line):
        self.ms_per_line=ms_per_line
        return self.pixel_rate(1.0*self.ms_per_line/self.num_points)
    
    def frame_rate(self,ms_per_frame):
        self.ms_per_frame=ms_per_frame
        return self.line_rate(1.0*self.ms_per_frame/self.num_lines)
    
    def update_rate(self):
        self.ms_per_line=self.ms_per_pixel*self.num_pixels
        self.ms_per_frame=self.ms_per_line*self.num_lines
    
    def set_rate(self,ms_per_unit,unit=0):
        if unit==0:
            return self.pixel_rate(ms_per_unit)
        elif unit==1:
            return self.line_rate(ms_per_unit)
        elif unit==2:
            return self.line_rate(ms_per_unit)
        else:
            return self.pixel_rate(ms_per_unit)

if __name__=="__main__":
    rate_converter=RateConverter(512,512,2000000)
    print(rate_converter.set_rate(5.12,1))
        
        