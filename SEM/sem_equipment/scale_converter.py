'''
Created on Apr 30, 2015

@author: Hao
'''

class ScaleConverter(object):
    
    def __init__(self,coeff=1.00):
        """
        Window_size(nm)=C/Magnification
        """
        C=114220000
        self.C=C*coeff
    
    def read_magnification(self,mag=1000):
        self.magnification=mag
        
    def read_window_size(self):
        self.window_size=self.C/self.magnification
    
    def set_percent_x(self,x=1.0):
        self.percent_x=x
        
    def set_percent_y(self,y=1.0):
        self.percent_y=y
    
    def read_window_size_x(self):
        self.window_size_x=self.window_size*self.percent_x
        
    def read_window_size_y(self):
        self.window_size_y=self.window_size*self.percent_y
        
    def read_numpix_x(self,x=512):
        self.numpix_x=x
    
    def read_numpix_y(self,y=512):
        self.numpix_y=y
        
    def read_pixsize_x(self):
        self.pixsize_x=self.window_size_x/self.numpix_x
        
    def read_pixsize_y(self):
        self.pixsize_y=self.window_size_y/self.numpix_y
        
    def read_parameters(self,magnification=1000,percent_x=1.0,percent_y=1.0,x_pix=512,y_pix=512):
        self.read_magnification(magnification)
        self.read_window_size()
        self.set_percent_x(percent_x)
        self.set_percent_y(percent_y)
        self.read_window_size_x()
        self.read_window_size_y()
        self.read_numpix_x(x_pix)
        self.read_numpix_y(y_pix)
        self.read_pixsize_x()
        self.read_pixsize_y()
        
    def get_pixsize_x(self):
        return self.pixsize_x
    
    def get_pixsize_y(self):
        return self.pixsize_y