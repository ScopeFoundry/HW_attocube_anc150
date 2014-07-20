from __future__ import division
'''
Created on May 29, 2014

@author: Edward Barnard
'''
from .measurement import Measurement 
import numpy as np
import time
from PySide import QtCore

class SpectrumScan2DMeasurement(Measurement):
    
    def __init__(self, gui):
        Measurement.__init__(self, gui, "spec_scan")
        
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
        

    def _run(self):
        # hardware
        self.nanodrive = self.gui.nanodrive
        self.andor_ccd_hc = self.gui.andor_ccd_hc
        ccd = self.andor_ccd = self.andor_ccd_hc.andor_ccd
        
        self.N_spec = ccd.Nx_ro
        
        #get scan parameters:
        self.h0 = self.gui.ui.h0_doubleSpinBox.value()
        self.h1 = self.gui.ui.h1_doubleSpinBox.value()
        self.v0 = self.gui.ui.v0_doubleSpinBox.value()
        self.v1 = self.gui.ui.v1_doubleSpinBox.value()
    
        self.dh = 1e-3*self.gui.ui.dh_spinBox.value()
        self.dv = 1e-3*self.gui.ui.dv_spinBox.value()

        self.h_array = np.arange(self.h0, self.h1, self.dh, dtype=float)
        self.v_array = np.arange(self.v0, self.v1, self.dv, dtype=float)
        
        self.Nh = len(self.h_array)
        self.Nv = len(self.v_array)
        
        self.range_extent = [self.h0, self.h1, self.v0, self.v1]

        self.corners =  [self.h_array[0], self.h_array[-1], self.v_array[0], self.v_array[-1]]
        
        self.imshow_extent = [self.h_array[ 0] - 0.5*self.dh,
                              self.h_array[-1] + 0.5*self.dh,
                              self.v_array[ 0] - 0.5*self.dv,
                              self.v_array[-1] + 0.5*self.dv]
        
        
        # hypserspectral scan specific setup

        t_acq = self.gui.andor_ccd_hc.exposure_time.val #in seconds
        #wait_time = np.min(1.0,np.max(0.05*t_acq, 0.05)) # limit update period to 50ms (in ms) or as slow as 1sec
        wait_time = 0.05
        
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
        try:
            start_pos = [None, None,None]
            start_pos[self.gui.VAXIS_ID-1] = self.v_array[0]
            start_pos[self.gui.HAXIS_ID-1] = self.h_array[0]
            
            self.nanodrive.set_pos_slow(*start_pos)
            
            # Scan!            
            line_time0 = time.time()
            
            for i_v in range(self.Nv):
                self.v_pos = self.v_array[i_v]
                self.nanodrive.set_pos_ax(self.v_pos, self.gui.VAXIS_ID)
                #self.read_stage_position()       
    
                if i_v % 2: #odd lines
                    h_line_indicies = range(self.Nh)[::-1]
                else:       #even lines -- traverse in opposite direction
                    h_line_indicies = range(self.Nh)            
    
                for i_h in h_line_indicies:
                    if self.interrupt_measurement_called:
                        break
    
                    print i_h, i_v
    
                    self.h_pos = self.h_array[i_h]
                    self.nanodrive.set_pos_ax(self.h_pos, self.gui.HAXIS_ID)    
                    
                    # collect data
                    ccd.start_acquisition()
                    stat = ccd.get_status()
                    print "stat", stat
                    while stat == 'ACQUIRING':
                        time.sleep(wait_time)            
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
    
                print "line time:", time.time() - line_time0
                print "pixel time:", float(time.time() - line_time0)/self.Nh
                line_time0 = time.time()
                
        #scanning done
        #except Exception as err:
        #    self.interrupt()
        #    raise err
        finally:
            #save  data file
            save_dict = {
                     'spec_map': self.spec_map,
                     'integrated_count_map': self.integrated_count_map,
                     'background_data': self.background_data,
                     'bg_sub': self.bg_sub,
                     'h_array': self.h_array,
                     'v_array': self.v_array,
                     'dh': self.dh,
                     'dv': self.dv,
                     'Nv': self.Nv,
                     'Nh': self.Nh,
                     'N_spec': self.N_spec,
                     'range_extent': self.range_extent,
                     'corners': self.corners,
                     'imshow_extent': self.imshow_extent,
                     
                    }               

                    
            for lqname,lq in self.gui.logged_quantities.items():
                save_dict[lqname] = lq.val
                
            for lqname,lq in self.gui.andor_ccd_hc.logged_quantities.items():
                save_dict[self.gui.andor_ccd_hc.name + "_" + lqname] = lq.val
                
            for lqname,lq in self.logged_quantities.items():
                save_dict[self.name +"_"+ lqname] = lq.val
    
            self.fname = "%i_spec_map.npz" % time.time()
            np.savez_compressed(self.fname, **save_dict)
            print "Hyper-spectral Scan Saved", self.fname

            if not self.interrupt_measurement_called:
                self.measurement_sucessfully_completed.emit()
            else:
                pass        

    @QtCore.Slot()
    def on_display_update_timer(self):
        # update figure
        try:
            
            self.spec_plotline.set_ydata(self.spectra_data)
            
            self.ax_spec.relim()
            self.ax_spec.autoscale_view(scalex=False, scaley=True)
            
            C = self.integrated_count_map
            self.imgplot.set_data(C)
            
            try:
                count_min =  np.min(C[np.nonzero(C)])
            except Exception:
                count_min = 0
            count_max = np.max(self.integrated_count_map)
            self.imgplot.set_clim(count_min, count_max + 1)
            
            self.fig.canvas.draw()
        finally:
            Measurement.on_display_update_timer(self)            
            