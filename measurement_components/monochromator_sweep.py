import numpy as np
import time
from PySide import QtCore
import pyqtgraph as pg
import random

from ScopeFoundry import Measurement

class MonochromatorSweep(Measurement):
    
    name = 'monochromator_sweep'
    
    def setup(self):
        self.display_update_period = 0.1 #seconds

        self.wavelength_start = self.add_logged_quantity(
                                     "wavelength_start",
                                     dtype=float, vmin=0, vmax=2000, initial=800)
        
        self.wavelength_stop = self.add_logged_quantity(
                                     "wavelength_stop",
                                     dtype=float, vmin=0, vmax=2000, initial=800)
        
        self.step_count = self.add_logged_quantity(
                                       name='step_count',
                                       dtype=int, 
                                       vmin=1, vmax=10000, initial=10)

        self.stored_histogram_channels = self.add_logged_quantity(
                                      "stored_histogram_channels", 
                                     dtype=int, vmin=1, vmax=2**16, initial=2**16)
        
        self.collect_apd      = self.add_logged_quantity("collect_apd",      dtype=bool, initial=True)
        self.collect_lifetime = self.add_logged_quantity("collect_lifetime", dtype=bool, initial=True)

        self.use_shutter          = self.add_logged_quantity("use_shutter", dtype=bool, initial=False)

        #connect events
        #self.gui.ui.picoharp_acquire_one_pushButton.clicked.connect(self.start)
        #self.gui.ui.picoharp_interrupt_pushButton.clicked.connect(self.interrupt)
    
    def setup_figure(self):
        """self.fig = self.gui.add_figure("picoharp_live", self.gui.ui.picoharp_plot_widget)
                    
        self.ax = self.fig.add_subplot(111)
        self.plotline, = self.ax.semilogy([0,20], [1,65535])
        self.ax.set_ylim(1e-1,1e5)
        self.ax.set_xlabel("Time (ns)")
        self.ax.set_ylabel("Counts")
        """
        
        self.graph_layout=pg.GraphicsLayoutWidget(border=(100,100,100))
        self.graph_layout.show()
        self.graph_layout.setWindowTitle("monochromator_sweep")
        
        self.plot = self.graph_layout.addPlot(title="monochromator_sweep")
        self.plot_line = self.plot.plot([1,3,2,4,3,5])

    def update_display(self):
        self.plot_line.setData(self.wavelengths, self.apd_count_rates)
        self.gui.app.processEvents()
    
    
    def _run(self):
        
        # Hardware
        self.spec_hc = self.gui.acton_spec_hc
        
        if self.collect_apd.val:
            self.apd_counter_hc = self.gui.apd_counter_hc
            self.apd_count_rate = self.gui.apd_counter_hc.apd_count_rate     
                   
        if self.collect_lifetime.val:
            ph = self.picoharp = self.gui.picoharp_hc.picoharp
            self.ph_sleep_time = np.min(np.max(0.1*ph.Tacq*1e-3, 0.010), 0.100) # check every 1/10 of Tacq with limits of 10ms and 100ms
            #self.ph_hist_chan = ph.HISTCHAN

        # Use a shutter 
        if self.use_shutter.val:
            self.shutter = self.gui.shutter_servo_hc
            # Start with shutter closed.
            #self.shutter.shutter_open.update_value(False)


        # Create Data Arrays    
        N = self.step_count.val
        self.set_wavelengths = np.linspace(
                       self.wavelength_start.val, self.wavelength_stop.val, N, dtype=float)
        self.wavelengths = np.zeros(N, dtype=float)

        if self.collect_apd.val:
            self.apd_count_rates = np.zeros(N, dtype=float)
        if self.collect_lifetime.val:
            self.time_traces = np.zeros( (N, self.stored_histogram_channels.val), dtype=int )
            self.elapsed_times = np.zeros(N, dtype=float)
        
        
        # SCAN!!!
        try:
            
            if self.use_shutter.val:
                self.shutter.shutter_open.update_value(True)
                time.sleep(1.0) # wait for shutter to open

            for ii in range(N):
                self.set_progress((100.*ii)/N)
                if self.interrupt_measurement_called:
                    break
                
                print ii, self.set_wavelengths[ii]
                self.spec_hc.center_wl.update_value(self.set_wavelengths[ii])
                self.wavelengths[ii] = self.spec_hc.center_wl.val
                time.sleep(0.1)
                # Collect Data from detectors
                if self.collect_apd.val:
                    self.apd_count_rates[ii] = self.collect_apd_data()
                if self.collect_lifetime.val:
                    print self.picoharp.read_count_rate(0)/1e6, self.picoharp.read_count_rate(1)/1e3
                    time_trace, self.elapsed_times[ii] = self.collect_lifetime_data()
                    self.time_traces[ii,:] = time_trace[:self.stored_histogram_channels.val]

            if self.use_shutter.val:
                self.shutter.shutter_open.update_value(False)
                time.sleep(1.0) # wait for shutter to close
            
        finally:
            save_dict = {
                         'set_wavelengths': self.set_wavelengths,
                         'wavelengths': self.wavelengths,
                        }               
    
            if self.collect_apd.val:
                save_dict['apd_count_rates'] = self.apd_count_rates
                
            if self.collect_lifetime.val:
                save_dict['time_traces'] = self.time_traces
                save_dict['time_array' ] = 1e-3*self.picoharp.time_array[:self.stored_histogram_channels.val]
                save_dict['elapsed_times'] = self.elapsed_times
      
            for lqname,lq in self.gui.logged_quantities.items():
                save_dict[lqname] = lq.val
            
            for hc in self.gui.hardware_components.values():
                for lqname,lq in hc.logged_quantities.items():
                    save_dict[hc.name + "_" + lqname] = lq.val
            
            for lqname,lq in self.logged_quantities.items():
                save_dict[self.name +"_"+ lqname] = lq.val
    
            self.fname = "%i_%s.npz" % (time.time(), self.name)
            np.savez_compressed(self.fname, **save_dict)
            print self.name, "saved-->", self.fname

    def collect_apd_data(self):
        apd = self.apd_counter_hc
        
        # collect data
        apd.apd_count_rate.read_from_hardware()
                                      
        # read data
        count_rate = apd.apd_count_rate.val
        
        return count_rate
    
    def collect_lifetime_data(self):
        # collect data
        #print "sleep_time", self.sleep_time
        t0 = time.time()
        self.picoharp.start_histogram()
        while not self.picoharp.check_done_scanning():
            #ph.read_histogram_data()
            time.sleep(0.1) #self.sleep_time)  
        self.picoharp.stop_histogram()
        self.picoharp.read_histogram_data()
        elapsed_meas_time = self.picoharp.read_elapsed_meas_time()*1.0/1000 # convert to sec
        
        t1 = time.time()
        #print "time per pixel:", (t1-t0)
        return self.picoharp.histogram_data, elapsed_meas_time

               
