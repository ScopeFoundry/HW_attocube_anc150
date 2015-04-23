from __future__ import division
'''
Created on May 29, 2014

@author: Edward Barnard
'''
#from .measurement import Measurement 
from .base_2d_scan import Base2DScan
import numpy as np
import time

def pixel2wavelength(grating_position, pixel_index, binning = 1):
    # Wavelength calibration based off of work on 4/30/2014
    # changed 3/20/2015 after apd alignement offset = -5.2646 #nm
    offset = -4.2810
    focal_length = 293.50 #mm
    delta = 0.0704  #radians
    gamma = 0.6222  # radian
    grating_spacing = 1/150.  #mm
    pixel_size = 16e-3  #mm   #Binning!
    m_order = 1 #diffraction order

    wl_center = (grating_position + offset)*1e-6
    px_from_center = pixel_index*binning +binning/2. - 256
    
    psi = np.arcsin(m_order* wl_center / (2*grating_spacing*np.cos(gamma/2)))
    
    eta = np.arctan(px_from_center*pixel_size*np.cos(delta) /
    (focal_length+px_from_center*pixel_size*np.sin(delta)))
    
    return 1e6*((grating_spacing/m_order)
                    *(np.sin(psi-0.5*gamma)
                      + np.sin(psi+0.5*gamma+eta)))


class SpectrumScan2DMeasurement(Base2DScan):
    
    name = "spec_scan"

    def scan_specific_setup(self):
        self.display_update_period = 0.1 #seconds
        
        # logged quantities
        self.bg_subtract = self.add_logged_quantity("bg_subtract", dtype=bool, ro=False)
        
        self.bg_subtract.connect_bidir_to_widget(self.gui.ui.spec_map_bg_subtract_checkBox)
        
        #connect events
        self.gui.ui.spec_map_start_pushButton.clicked.connect(self.start)
        self.gui.ui.spec_map_interrupt_pushButton.clicked.connect(self.interrupt)

    def setup_figure(self):
        self.fig = self.gui.add_figure("spec_map", self.gui.ui.spec_map_plot_groupBox)
        
        self.ax_spec = self.fig.add_subplot(211)
        self.spec_plotline, = self.ax_spec.plot(np.zeros(512))
        self.spectra_data = np.zeros(512)
        
        self.ax2d = self.fig.add_subplot(212)
        

    def pre_scan_setup(self):
        # hypserspectral scan specific setup
        self.display_update_period = 0.10 #seconds

        #hardware
        self.andor_ccd_hc = self.gui.andor_ccd_hc
        self.andor_ccd = self.andor_ccd_hc.andor_ccd
        
        self.N_spec = self.andor_ccd.Nx_ro


        self.t_acq = self.gui.andor_ccd_hc.exposure_time.val #in seconds
        #wait_time = np.min(1.0,np.max(0.05*t_acq, 0.05)) # limit update period to 50ms (in ms) or as slow as 1sec
        self.wait_time = 0.05
        
        #create data arrays
        self.integrated_count_map = np.zeros((self.Nv, self.Nh), dtype=int)
        self.spec_map = np.zeros( (self.Nv, self.Nh, self.N_spec), dtype=int)

        self.background_data = None 
        
        self.bg_sub = self.bg_subtract.val
        if self.bg_sub:
            self.background_data = self.andor_ccd_hc.background
        
        #TODO disable bg checkbox during run
        #TODO need to store background
        
        #update figure
        self.imgplot = self.ax2d.imshow(self.integrated_count_map, 
                                    origin='lower',
                                    vmin=1e4, vmax=1e5, interpolation='nearest', 
                                    extent=self.imshow_extent)
        
        print "Hyperspectral map 2D scanning"
        self.t_scan_start = time.time()
        
    def collect_pixel(self,i_h,i_v):
        t0 = time.time()
        # collect data
        ccd = self.andor_ccd
        ccd.start_acquisition()
        stat = ccd.get_status()
        #print "stat", stat
        while stat == 'ACQUIRING':
            #time.sleep(self.wait_time)            
            time.sleep(0.001)
            stat = ccd.get_status()
            if self.interrupt_measurement_called:
                break
        
        
        if stat == 'IDLE':
            # grab data
            
            buffer_ = ccd.get_acquired_data()
            
            if self.bg_sub:
                bg = self.background_data
                if bg is not None:
                    if bg.shape == buffer_.shape:
                        buffer_ = buffer_ - bg
                    else:
                        print "Background not the correct shape", buffer_.shape, bg.shape
                else:
                    print "No Background available, raw data shown"
            self.spectra_data = np.average(buffer_, axis=0)
            
        else:
            raise ValueError("andor_ccd status should be 'IDLE', is '%s'" % stat)            
                
                          
        # store in arrays
        self.spec_map[i_v,i_h,:] = self.spectra_data
        self.integrated_count_map[i_v,i_h] = np.sum(self.spectra_data)
        print self.integrated_count_map[i_v,i_h]

        if True:
            t1 = time.time()
            T_pixel=(t1-t0)
            total_px = self.Nv*self.Nh
            print "time per pixel:", T_pixel, '| estimated total time (h)', total_px*T_pixel/3600,'| Nh, Nv:', self.Nh, self.Nv,
            Time_finish = time.localtime(total_px*T_pixel+self.t_scan_start)
            print '| scan finishes at: {}:{}'.format(Time_finish.tm_hour,Time_finish.tm_min)
 
        
    def scan_specific_savedict(self):
        save_dict = {
                     'spec_map': self.spec_map,
                     'integrated_count_map': self.integrated_count_map,
                     'background_data': self.background_data,
                     'bg_sub': self.bg_sub,
                     'N_spec': self.N_spec,                     
                     }
        return save_dict

    def update_display(self):     
        wls = pixel2wavelength(self.gui.acton_spec_hc.center_wl.val, np.arange(self.N_spec))

        self.spec_plotline.set_xdata(wls)
        self.spec_plotline.set_ydata(self.spectra_data)
        
        self.ax_spec.set_xlim(wls[0], wls[-1])
        #self.ax_spec.relim()
        #self.ax_spec.autoscale_view(scalex=False, scaley=True)
        
        C = self.integrated_count_map
        #C = np.argmax(self.spec_map, axis=2)
        #self.imgplot.set_data(np.ma.array(C, mask=C==0))
        self.imgplot.set_data(C)
        
        try:
            count_min =  np.min(C[np.nonzero(C)])
        except Exception:
            count_min = 0
        count_max = np.max(C)
        self.imgplot.set_clim(count_min, count_max )
        #self.imgplot.set_clim(200,300)
        
        self.fig.canvas.draw()
