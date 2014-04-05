# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 09:21:07 2014

@author: esbarnard
"""
import numpy as np
import time
import threading
from PySide import QtCore

from .measurement import Measurement 
 
 
class PicoHarpMeasurement(Measurement):
    
    def __init__(self, gui):
        Measurement.__init__(self, gui)

        self.display_update_period = 0.1 #seconds
        
        #connect events
        self.gui.ui.picoharp_acquire_one_pushButton.clicked.connect(self.start)
        self.gui.ui.picoharp_interrupt_pushButton.clicked.connect(self.interrupt)
    
    def setup_figure(self):
        self.fig = self.gui.add_figure("picoharp_live", self.gui.ui.picoharp_plot_widget)
                    
        self.ax = self.fig.add_subplot(111)
        self.plotline, = self.ax.semilogy([0,20], [1,65535])
        self.ax.set_ylim(1e-1,1e5)
        self.ax.set_xlabel("Time (ns)")
        self.ax.set_ylabel("Counts")
    
    def _run(self):
        ph = self.picoharp = self.gui.picoharp_hc.picoharp
        #: type: ph: PicoHarp300
        
        self.plotline.set_xdata(ph.time_array*1e-3)
        sleep_time = np.min(np.max(0.1*ph.Tacq*1e-3, 0.010), 0.100) # check every 1/10 of Tacq with limits of 10ms and 100ms
        
        ph.start_histogram()
        while not ph.check_done_scanning():
            if self.interrupt_measurement_called:
                break
            ph.read_histogram_data()
            time.sleep(sleep_time)

        ph.stop_histogram()
        ph.read_histogram_data()
        

               
    @QtCore.Slot()
    def on_display_update_timer(self):
        ph = self.picoharp
        self.plotline.set_ydata(ph.histogram_data)
        self.fig.canvas.draw()
        Measurement.on_display_update_timer(self)
        
        
class TRPLPointMeasurement(Measurement):
     
    def setup_figure(self):
        pass
        
    def _run(self):
        pass
         
    def on_display_update_timer(self):
        #update figure
                
        if not self.is_measuring():
            self.display_update_timer.stop()

class TRPLScanMeasurement(Measurement):
    
    def __init__(self, gui):
        Measurement.__init__(self, gui)
        
        self.name = "trpl_scan"

        self.display_update_period = 0.1 #seconds
        
        #connect events
        self.gui.ui.trpl_map_start_pushButton.clicked.connect(self.start)
        self.gui.ui.trpl_map_interrupt_pushButton.clicked.connect(self.interrupt)
        
        self.stored_histogram_channels = self.add_logged_quantity("stored_histogram_channels", dtype=int, vmin=1, vmax=2**16)
        self.stored_histogram_channels.connect_bidir_to_widget(
                                           self.gui.ui.trpl_map_stored_channels_doubleSpinBox)
        
        self.stored_histogram_channels.update_value(1000)
    
    def setup_figure(self):
        self.fig = self.gui.add_figure("trpl_map", self.gui.ui.trpl_map_plot_groupBox)
        self.ax_time = self.fig.add_subplot(211)
        self.ax_time.set_xlabel("Time (ns)")
        self.time_trace_plotline, = self.ax_time.semilogy([0,20], [0,65535])
        self.ax_time.set_ylim(1e-1,1e5)
        
        self.aximg = self.fig.add_subplot(212)
        self.aximg.set_xlim(0, self.gui.hmax)
        self.aximg.set_ylim(0, self.gui.vmax)

    
    def _run(self):
        # Setup try-block
        #hardware
        self.nanodrive = self.gui.nanodrive
        ph = self.picoharp = self.gui.picoharp_hc.picoharp

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
        
        self.extent = [self.h0, self.h1, self.v0, self.v1]

        # TRPL scan specific setup
        sleep_time = np.min(np.max(0.1*ph.Tacq*1e-3, 0.010), 0.100) # check every 1/10 of Tacq with limits of 10ms and 100ms

        
        #create data arrays
        self.integrated_count_map = np.zeros((self.Nv, self.Nh), dtype=int)
        self.time_trace_map = np.zeros( (self.Nv, self.Nh, self.stored_histogram_channels.val), dtype=int)
        
        self.time_array = ph.time_array[0:self.stored_histogram_channels.val]*1e-3
        #update figure
        self.time_trace_plotline.set_xdata(self.time_array)

        self.imgplot = self.aximg.imshow(self.integrated_count_map, 
                                    origin='lower',
                                    vmin=1e4, vmax=1e5, interpolation='nearest', 
                                    extent=[self.h0, self.h1, self.v0, self.v1])

        # set up experiment
        # experimental parameters already connected via LoggedQuantities
        
        # TODO Stop other timers?!

        print "scanning"
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
                    ph.start_histogram()
                    while not ph.check_done_scanning():
                        ph.read_histogram_data()
                        time.sleep(sleep_time)  
                    ph.stop_histogram()
                    ph.read_histogram_data()
                                      
                    # store in arrays
                    N = self.stored_histogram_channels.val
                    self.time_trace_map[i_v,i_h,:] = ph.histogram_data[0:N]
                    self.integrated_count_map[i_v,i_h] = np.sum(self.time_trace_map[i_v,i_h])
    
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
                     'time_trace_map': self.time_trace_map,
                     'integrated_count_map': self.integrated_count_map,
                     'h_array': self.h_array,
                     'v_array': self.v_array,
                     'dh': self.dh,
                     'dv': self.dv,
                     'Nv': self.Nv,
                     'Nh': self.Nh,
                     'extent': self.extent,
                     'time_array': self.time_array
                    }               

                    
            for lqname,lq in self.gui.logged_quantities.items():
                save_dict[lqname] = lq.val
                
            for lqname,lq in self.gui.picoharp_hc.logged_quantities.items():
                save_dict[self.gui.picoharp_hc.name + "_" + lqname] = lq.val
                
            for lqname,lq in self.logged_quantities.items():
                save_dict[self.name +"_"+ lqname] = lq.val
    
            self.fname = "%i_trpl_map.npz" % time.time()
            np.savez_compressed(self.fname, **save_dict)
            print "TRPL Scan Saved", self.fname

            if not self.interrupt_measurement_called:
                self.measurement_sucessfully_completed.emit()
            else:
                pass

    
    @QtCore.Slot()
    def on_display_update_timer(self):
        # update figure
        try:
            self.time_trace_plotline.set_ydata(self.picoharp.histogram_data[0:self.stored_histogram_channels.val])
            
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