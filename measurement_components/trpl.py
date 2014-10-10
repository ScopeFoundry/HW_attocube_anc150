# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 09:21:07 2014

@author: esbarnard
"""
import numpy as np
import time
from PySide import QtCore

from .measurement import Measurement 
from .base_3d_scan import Base3DScan
from .base_2d_scan import Base2DScan


class PicoHarpMeasurement(Measurement):    
    name = "picoharp_live"
    
    def setup(self):
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
        sleep_time = np.min((np.max(0.1*ph.Tacq*1e-3, 0.010), 0.100)) # check every 1/10 of Tacq with limits of 10ms and 100ms
        print "sleep_time", sleep_time, np.max(0.1*ph.Tacq*1e-3, 0.010)
        
        ph.start_histogram()
        while not ph.check_done_scanning():
            if self.interrupt_measurement_called:
                break
            ph.read_histogram_data()
            time.sleep(sleep_time)

        ph.stop_histogram()
        ph.read_histogram_data()
        
        save_dict = {
                     'time_histogram': ph.histogram_data,
                     'time_array': ph.time_array
                    }               

                    
        for lqname,lq in self.gui.logged_quantities.items():
            save_dict[lqname] = lq.val
            
        for lqname,lq in self.gui.picoharp_hc.logged_quantities.items():
            save_dict[self.gui.picoharp_hc.name + "_" + lqname] = lq.val
            
        for lqname,lq in self.logged_quantities.items():
            save_dict[self.name +"_"+ lqname] = lq.val

        self.fname = "%i_picoharp.npz" % time.time()
        np.savez_compressed(self.fname, **save_dict)
        print "TRPL Picoharp Saved", self.fname
                
        #is this right place to put this?
        self.measurement_state_changed.emit(False)
        if not self.interrupt_measurement_called:
            self.measurement_sucessfully_completed.emit()
        else:
            self.measurement_interrupted.emit()        

               
    @QtCore.Slot()
    def on_display_update_timer(self):
        try:
            ph = self.picoharp
            self.plotline.set_ydata(ph.histogram_data)
            self.fig.canvas.draw()
        finally:
            Measurement.on_display_update_timer(self)
        
 
class PicoHarpPowerWheelMeasurement(Measurement):
    
    name = "picoharp_power_wheel"
    
    def setup(self):
        self.display_update_period = 0.1 #seconds
        
        #connect events
        self.gui.ui.power_wheel_start_pushButton.clicked.connect(self.start)
        self.gui.ui.power_wheel_interrupt_pushButton.clicked.connect(self.interrupt)
        
        self.power_wheel_steps = self.add_logged_quantity("power_wheel_steps", dtype=int, unit='deg', vmin=0, vmax=+8000, ro=False)
        self.power_wheel_steps.connect_bidir_to_widget(self.gui.ui.power_wheel_steps_doubleSpinBox)

        self.power_wheel_delta = self.add_logged_quantity("power_wheel_delta", dtype=int, unit='', vmin=-8000, vmax=+8000, ro=False)
        self.power_wheel_steps.connect_bidir_to_widget(self.gui.ui.power_wheel_delta_doubleSpinBox)


        self.stored_histogram_channels = self.add_logged_quantity("stored_histogram_channels", dtype=int, vmin=1, vmax=2**16)
        self.stored_histogram_channels.connect_bidir_to_widget(
                                           self.gui.ui.power_wheel_channels_doubleSpinBox)
        
        self.stored_histogram_channels.update_value(1000)   
    
    def setup_figure(self):
        self.fig = self.gui.add_figure("picoharp_live", self.gui.ui.picoharp_plot_widget)
                    
        self.ax = self.fig.add_subplot(111)
        self.plotline, = self.ax.semilogy([0,20], [1,65535])
        self.ax.set_ylim(1e-1,1e5)
        self.ax.set_xlabel("Time (ns)")
        self.ax.set_ylabel("Counts")
    
    def _run(self):

        ph = self.picoharp = self.gui.picoharp_hc.picoharp

        pw = self.power_wheel = self.gui.power_wheel_arduino_hc.power_wheel_arduino_hc
        
        pw_steps = self.power_wheel_steps.val
        pw_delta = self.power_wheel_delta.val
        pw_motor_steps = pw_steps*pw_delta
        #: type: ph: PicoHarp300
        
        self.plotline.set_xdata(ph.time_array*1e-3)
        sleep_time = np.min((np.max(0.1*ph.Tacq*1e-3, 0.010), 0.100)) # check every 1/10 of Tacq with limits of 10ms and 100ms
        print "sleep_time", sleep_time, np.max(0.1*ph.Tacq*1e-3, 0.010)
        
                  
        # Allocated memory 
        N = self.stored_histogram_channels.val
        self.time_trace= np.zeros(pw_steps,N)
        self.time_array = ph.time_array[0:N]*1e-3
        
        self.powers = np.zeros(pw_steps)

        
        PM_SAMPLE_NUMBER = 1;
        
        for ii in range(pw_steps+1):
                
            # collect data
            # collect timetrace
            ph.start_histogram()
            while not ph.check_done_scanning():
                ph.read_histogram_data()
                time.sleep(sleep_time)  
            ph.stop_histogram()
            ph.read_histogram_data()
            
            
            # collect power

            self.ii = 0
            while not self.interrupt_measurement_called:
    
                # Sample the power at least one time from the power meter.
                samp_count = 0
                pm_power = 0.0
                for samp in range(0, PM_SAMPLE_NUMBER):
                    # Try at least 10 times before ultimately failing
                    try_count = 0
                    while True:
                        try:
                            pm_power = pm_power + self.gui.thorlabs_powermeter_hc.power.read_from_hardware(send_signal=True)
                            samp_count = samp_count + 1
                            break 
                        except Exception as err:
                            try_count = try_count + 1
                            if try_count > 9:
                                print "failed to collect power meter sample:", err
                                break
                            time.sleep(0.010)
                 
                if samp_count > 0:              
                    pm_power = pm_power/samp_count
                else:
                    print "  Failed to read power"
                    pm_power = 10000.  
                        
            # make a step
            pw.write_steps(pw_motor_steps)                                      
        
            # store in arrays
            self.time_trace[ii,:] = ph.histogram_data[0:N]
            self.pm_powers[ii]=pm_power
            self.time_array

            
            
                
        save_dict = {
                     'time_trace': self.time_trace,
                     'time_array': self.time_array,
                     'power': self.power
                     } 
    
                
                
            
                
                           

                    
        for lqname,lq in self.gui.logged_quantities.items():
            save_dict[lqname] = lq.val
            
        for hc in self.gui.hardware_components.values():
            for lqname,lq in hc.logged_quantities.items():
                save_dict[hc.name + "_" + lqname] = lq.val
            
        for lqname,lq in self.logged_quantities.items():
            save_dict[self.name +"_"+ lqname] = lq.val

        self.fname = "%i_picoharp.npz" % time.time()
        np.savez_compressed(self.fname, **save_dict)
        print "TRPL Picoharp Saved", self.fname
                
        #is this right place to put this?
        self.measurement_state_changed.emit(False)
        if not self.interrupt_measurement_called:
            self.measurement_sucessfully_completed.emit()
        else:
            self.measurement_interrupted.emit()        

               
    @QtCore.Slot()
    def on_display_update_timer(self):
        try:
            ph = self.picoharp
            self.plotline.set_ydata(ph.histogram_data)
            self.fig.canvas.draw()
        finally:
            Measurement.on_display_update_timer(self)
        
        

class TRPLScanMeasurement(Base2DScan):
    
    name = "trpl_scan"

    def scan_specific_setup(self):
        
        self.display_update_period = 0.1 #seconds
        
        self.stored_histogram_channels = self.add_logged_quantity(
                                      "stored_histogram_channels", 
                                     dtype=int, vmin=1, vmax=2**16, initial=4000)

        #connect events
        self.gui.ui.trpl_map_start_pushButton.clicked.connect(self.start)
        self.gui.ui.trpl_map_interrupt_pushButton.clicked.connect(self.interrupt)
        
        self.stored_histogram_channels.connect_bidir_to_widget(
                                           self.gui.ui.trpl_map_stored_channels_doubleSpinBox)
        
        self.stored_histogram_channels.update_value(1000)

    
    def setup_figure(self):
        print "TRPLSCan figure"
        self.fig = self.gui.add_figure("trpl_map", self.gui.ui.trpl_map_plot_widget)
        self.ax_time = self.fig.add_subplot(211)
        self.ax_time.set_xlabel("Time (ns)")
        self.time_trace_plotline, = self.ax_time.semilogy([0,20], [0,65535])
        self.ax_time.set_ylim(1e-1,1e5)
        
        #self.fig.canvas.draw()

        self.aximg = self.fig.add_subplot(212)
        self.aximg.set_xlim(0, 100)
        self.aximg.set_ylim(0, 100)

        #self.fig.canvas.draw()

    
    def pre_scan_setup(self):
        #hardware
        ph = self.picoharp = self.gui.picoharp_hc.picoharp
        
        # TRPL scan specific setup
        self.sleep_time = np.min(np.max(0.1*ph.Tacq*1e-3, 0.010), 0.100) # check every 1/10 of Tacq with limits of 10ms and 100ms

        #create data arrays
        self.integrated_count_map = np.zeros((self.Nv, self.Nh), dtype=int)
        self.time_trace_map = np.zeros( 
                                       (self.Nv, self.Nh, 
                                            self.stored_histogram_channels.val), 
                                       dtype=int)
        
        self.time_array = ph.time_array[0:self.stored_histogram_channels.val]*1e-3
        #update figure
        self.time_trace_plotline.set_xdata(self.time_array)

        self.imgplot = self.aximg.imshow(self.integrated_count_map, 
                                    origin='lower',
                                    vmin=1e4, vmax=1e5, interpolation='nearest', 
                                    extent=self.extent)

    def collect_pixel(self, i, j):
        ph = self.picoharp
        # collect data
        #print "sleep_time", self.sleep_time
        t0 = time.time()
        ph.start_histogram()
        while not ph.check_done_scanning():
            #ph.read_histogram_data()
            time.sleep(0.1) #self.sleep_time)  
        ph.stop_histogram()
        ph.read_histogram_data()
        
        t1 = time.time()
        
        #print "time per pixel:", (t1-t0)
        
        # store in arrays
        N = self.stored_histogram_channels.val
        self.time_trace_map[j,i,:] = ph.histogram_data[0:N]
        self.integrated_count_map[j,i] = np.sum(self.time_trace_map[j,i])

    def scan_specific_savedict(self):
        return dict( integrated_count_map=self.integrated_count_map,
                     time_trace_map = self.time_trace_map,
                     time_array = self.time_array,
                     )        

    
    def update_display(self):
        self.time_trace_plotline.set_ydata(1+self.picoharp.histogram_data[0:self.stored_histogram_channels.val])
        
        C = self.integrated_count_map
        self.imgplot.set_data(C)
        
        try:
            count_min =  np.min(C[np.nonzero(C)])
        except Exception:
            count_min = 0
        count_max = np.max(self.integrated_count_map)
        self.imgplot.set_clim(count_min, count_max + 1)
        
        self.fig.canvas.draw()
        
        
class TRPLScan3DMeasurement(Base3DScan):
    
    name = "trpl_scan3d"
    
    def scan_specific_setup(self):
        self.stored_histogram_channels = self.add_logged_quantity("stored_histogram_channels", dtype=int, vmin=1, vmax=2**16, initial=4000)
        
    def setup_figure(self):
        pass
    
    def pre_scan_setup(self):
        #hardware
        ph = self.picoharp = self.gui.picoharp_hc.picoharp
        
        # TRPL scan specific setup
        self.sleep_time = np.min(np.max(0.1*ph.Tacq*1e-3, 0.010), 0.100) # check every 1/10 of Tacq with limits of 10ms and 100ms

        #create data arrays
        self.integrated_count_map = np.zeros((self.Nz, self.Ny, self.Nx), dtype=int)
        print "size of time_trace_map %e" %  (self.Nx* self.Ny * self.Nz * self.stored_histogram_channels.val)

        self.time_trace_map = np.zeros( (self.Nz, self.Ny, self.Nx, self.stored_histogram_channels.val),dtype=np.uint16)
        
        self.time_array = ph.time_array[0:self.stored_histogram_channels.val]*1e-3
        #update figure
        #self.time_trace_plotline.set_xdata(self.time_array)    
        
        
    def collect_pixel(self, i, j, k):
        ph = self.picoharp
        # collect data
        #print "sleep_time", self.sleep_time
        t0 = time.time()
        ph.start_histogram()
        while not ph.check_done_scanning():
            #ph.read_histogram_data()
            time.sleep(0.1) #self.sleep_time)  
        ph.stop_histogram()
        ph.read_histogram_data()
        
        t1 = time.time()
        
        print "time per pixel:", (t1-t0)
        
        """
        try:
            save_dict = {
                         'x_array': self.x_array,
                         'y_array': self.y_array,
                         'z_array': self.z_array,
                         'Nx': self.Nx,
                         'Ny': self.Ny,
                         'Nz': self.Nz,
                         }               
    
            save_dict.update(self.scan_specific_savedict())

            for lqname,lq in self.gui.logged_quantities.items():
                save_dict[lqname] = lq.val
            
            for hc in self.gui.hardware_components.values():
                for lqname,lq in hc.logged_quantities.items():
                    save_dict[hc.name + "_" + lqname] = lq.val
            
            for lqname,lq in self.logged_quantities.items():
                save_dict[self.name +"_"+ lqname] = lq.val
            
            
            np.savez_compressed("incomplete_3dtrpl_scan.npz", **save_dict)
            print "saved"
        except:
            pass
        """
        # store in arrays
        N = self.stored_histogram_channels.val
        self.time_trace_map[k,j,i,:] = ph.histogram_data[0:N]
        self.integrated_count_map[k,j,i] = np.sum(self.time_trace_map[k,j,i])

    def scan_specific_savedict(self):
        return dict( integrated_count_map=self.integrated_count_map,
                     time_trace_map = self.time_trace_map,
                     time_array = self.time_array,
                     )
        
    def update_display(self):
        pass
