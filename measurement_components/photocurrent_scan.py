from __future__ import division
'''
Created on Sept 8, 2014

@author: Edward Barnard and Benedikt Ursprung
'''

from .base_2d_scan import Base2DScan
import numpy as np
import time

class Photocurrent2DMeasurement(Base2DScan):
    name = "photocurrent_scan2D"
    def scan_specific_setup(self):
        self.display_update_period = 0.1 #seconds
        
        # logged quantities
        self.source_voltage = self.add_logged_quantity("source_voltage", dtype=float, unit='V', vmin=-5, vmax=5, ro=False)
        
        self.source_voltage.connect_bidir_to_widget(self.gui.ui.photocurrent2D_source_voltage_doubleSpinBox)
        
        #connect events
        self.gui.ui.photocurrent2D_start_pushButton.clicked.connect(self.start)
        self.gui.ui.photocurrent2D_interrupt_pushButton.clicked.connect(self.interrupt)



    def setup_figure(self):
        self.fig = self.gui.add_figure("photocurrent2D_map", self.gui.ui.photocurrent2D_plot_groupBox)
        
        self.ax2d = self.fig.add_subplot(111)

        self.ax2d.set_xlim(0, 100)
        self.ax2d.set_ylim(0, 100)


    def pre_scan_setup(self):
        # hypserspectral scan specific setup

        #hardware
        self.keithley_hc = self.gui.keithley_sourcemeter_hc
        K1 = self.keithley = self.keithley_hc.keithley
        
        K1.resetA()
        K1.setAutoranges_A()
        K1.setV_A( self.source_voltage.val )
        K1.switchV_A_on()

        #create data arrays
        self.photocurrent_map = np.zeros((self.Nv, self.Nh), dtype=float)
        
        #update figure
        self.imgplot = self.ax2d.imshow(self.photocurrent_map, 
                                    origin='lower',
                                    interpolation='nearest', 
                                    extent=self.imshow_extent)
        
        
    def collect_pixel(self,i_h,i_v):

        # collect data
        i_array = self.keithley.measureI_A(N=10,KeithleyADCIntTime=1,delay=0)     
        avg_i = np.average(i_array)
        
        # store in arrays
        self.photocurrent_map[i_v, i_h] = avg_i
        print i_h, i_v, avg_i
        
    def scan_specific_savedict(self):
        save_dict = {
                     'photocurrent_map': self.photocurrent_map,
                     }
        return save_dict
    
    def update_display(self):    
                
        C = self.photocurrent_map
        self.imgplot.set_data(C)
        
        try:
            count_min =  np.min(C[np.nonzero(C)])
        except Exception:
            count_min = 0
        count_max = np.max(C)
        self.imgplot.set_clim(count_min, count_max )
        
        self.fig.canvas.draw()
