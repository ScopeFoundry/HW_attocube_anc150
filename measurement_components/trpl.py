# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 09:21:07 2014

@author: esbarnard
"""
import numpy as np
import time
from PySide import QtCore
import h5py

from ScopeFoundry import Measurement 
from .base_3d_scan import Base3DScan
from .base_2d_scan import Base2DScan


class PicoHarpMeasurement(Measurement):    
    name = "picoharp_live"
    
    def setup(self):
        self.display_update_period = 0.1 #seconds

        
        self.stored_histogram_channels = self.add_logged_quantity(
                                      "stored_histogram_channels", 
                                     dtype=int, vmin=1, vmax=2**16, initial=2**16)
        self.stored_histogram_channels.connect_bidir_to_widget(
                                           self.gui.ui.trpl_live_stored_channels_doubleSpinBox)
        
        
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
        
        #FIXME
        #self.plotline.set_xdata(ph.time_array*1e-3)
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
        #FIXME
        #self.plotline.set_ydata(ph.histogram_data)

        #print "elasped_meas_time (final):", ph.read_elapsed_meas_time()
        
        save_dict = {
                     'time_histogram': ph.histogram_data,
                     'time_array': ph.time_array,
                     'elapsed_meas_time': ph.read_elapsed_meas_time()
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
            self.plotline.set_data(ph.time_array*1e-3, ph.histogram_data)
            self.fig.canvas.draw()
        finally:
            Measurement.on_display_update_timer(self)
        
        
        
class PicoHarpTTTR(Measurement):

    name = "picoharp_tttr"

    def setup(self):
        self.display_update_period = 0.1 #seconds

        #logged quantities

        #connect events

    def setup_figure(self):
        pass

    def _run(self):
        ph = self.picoharp = self.gui.picoharp_hc.picoharp

        # create data array
        self.records = np.zeros(60*1024*1024, dtype=np.uint32) #FIXME this should not be a fixed size
        self.record_i = 0

        try:
            self.fname = "%i_%s.h5" % (time.time(), self.name)
            self.dat_file = h5py.File(self.fname)
    
            meas_group = self.dat_file.create_group(self.name)
            h5_records = meas_group.create_dataset("records", shape=(ph.TTREADMAX,), maxshape=(None,), dtype=np.uint32)
    
            gui_group = self.dat_file.create_group("gui")
            for lqname,lq in self.gui.logged_quantities.items():
                gui_group.attrs[lqname] = lq.val
    
            hardware_group = self.dat_file.create_group("hardware")
            for hc in self.gui.hardware_components.values(): 
                hc_group = hardware_group.create_group(hc.name)   
                for lqname,lq in hc.logged_quantities.items():
                    hc_group.attrs[lqname] = lq.val
    
            for lqname,lq in self.logged_quantities.items():
                meas_group.attrs[lqname] = lq.val
                
            self.dat_file.flush()
            
            ph.start_measure()
            while not ph.check_done_scanning():
                print "tttr"
                if self.interrupt_measurement_called:
                    break
                N, fifo_buffer = ph.read_fifo()
                self.records[self.record_i:self.record_i+N] = fifo_buffer[0:N]
                h5_records.resize( (self.record_i + N,) )
                h5_records[self.record_i:self.record_i+N] = fifo_buffer[0:N]
                
                self.record_i += N
                time.sleep(0.01)            
            
        finally:
            ph.stop_measure()

            # close data file
            self.dat_file.close()
            
            print self.name, "done:", self.fname

            if not self.interrupt_measurement_called:
                self.measurement_sucessfully_completed.emit()
            else:
                pass


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

        self.initial_scan_setup_plotting = False
    
    def setup_figure(self):
        print "TRPLSCan figure"
        self.fig = self.gui.add_figure("trpl_map", self.gui.ui.trpl_map_plot_widget)
        self.fig.clf()
        self.ax_time = self.fig.add_subplot(211)
        self.ax_time.set_xlabel("Time (ns)")
        self.time_trace_plotline, = self.ax_time.semilogy([0,20], [0,65535])
        self.ax_time.set_ylim(1e-1,1e5)
        
        #self.fig.canvas.draw()

        self.aximg = self.fig.add_subplot(212)
        self.aximg.set_xlim(0, 100)
        self.aximg.set_ylim(0, 100)

        #self.fig.canvas.draw()

    def post_scan_cleanup(self):
        if self.record_power:
            self.gui.thorlabs_powermeter_hc.power.read_from_hardware()
            self.powermeter_final_power = self.gui.thorlabs_powermeter_hc.power.val
    
    
    def pre_scan_setup(self):
        
        #hardware
        ph = self.picoharp = self.gui.picoharp_hc.picoharp
        
        self.record_power = False
        if self.gui.thorlabs_powermeter_analog_readout_hc.connected.val and self.gui.thorlabs_powermeter_hc.connected.val:
            self.record_power = True
            self.pm_analog_readout = self.gui.thorlabs_powermeter_analog_readout_hc
            self.gui.thorlabs_powermeter_hc.read_from_hardware()
            self.powermeter_initial_power = self.gui.thorlabs_powermeter_hc.power.val
            
        else:
            #raise IOError("power meter not connected")
            print "power meter not connected"
        
        # TRPL scan specific setup
        self.sleep_time = np.min(np.max(0.1*ph.Tacq*1e-3, 0.010), 0.100) # check every 1/10 of Tacq with limits of 10ms and 100ms

        #create data arrays
        if self.record_power:
            self.powermeter_analog_volt_map = np.zeros((self.Nv, self.Nh), dtype=float)
        self.integrated_count_map = np.zeros((self.Nv, self.Nh), dtype=int)
        self.time_trace_map = np.zeros( 
                                       (self.Nv, self.Nh, 
                                            self.stored_histogram_channels.val), 
                                       dtype=int)
        
        self.time_array = ph.time_array[0:self.stored_histogram_channels.val]*1e-3
        self.elapsed_time_array = np.zeros((self.Nv, self.Nh), dtype=float)
        
        self.initial_scan_setup_plotting = True
        
        self.t_scan_start = time.time()

    def collect_pixel(self, i, j):
        ph = self.picoharp
        # collect data
        #print "sleep_time", self.sleep_time
        t0 = time.time()
        ph.start_histogram()

        while not ph.check_done_scanning():
            if self.gui.picoharp_hc.logged_quantities['Tacq'].val > 200:
                ph.read_histogram_data()
            time.sleep(0.005) #self.sleep_time)  
        ph.stop_histogram()
        #ta = time.time()
        ph.read_histogram_data()
        #print "read_histogram_data time", 1000*(time.time() - ta)
        #print "pixel time", 1000*(time.time() - t0)

        if self.record_power:
            if self.gui.laser_power_feedback_control.is_measuring():
                self.pm_power_v = self.pm_analog_readout.voltage.val
            else:
                self.pm_power_v = self.pm_analog_readout.voltage.read_from_hardware()
        
        #print total time
        if True:
            t1 = time.time()
            T_pixel=(t1-t0)
            total_px = self.Nv*self.Nh
            print "time per pixel:", T_pixel, '| estimated total time (h)', total_px*T_pixel/3600,'| Nh, Nv:', self.Nh, self.Nv,
            Time_finish = time.localtime(total_px*T_pixel+self.t_scan_start)
            print '| scan finishes at: {}:{}'.format(Time_finish.tm_hour,Time_finish.tm_min)
            
        
        # store in arrays
        N = self.stored_histogram_channels.val
        self.time_trace_map[j,i,:] = ph.histogram_data[0:N]
        self.integrated_count_map[j,i] = np.sum(self.time_trace_map[j,i])
        if self.record_power:
            self.powermeter_analog_volt_map[j,i] = self.pm_power_v
        self.elapsed_time_array[j,i] = ph.read_elapsed_meas_time()
        
        self.current_index = (i,j)

    def scan_specific_savedict(self):
        savedict = dict( integrated_count_map=self.integrated_count_map,
                     time_trace_map = self.time_trace_map,
                     time_array = self.time_array,
                     elapsed_time_array = self.elapsed_time_array,
                     )
        if self.record_power:
            savedict['powermeter_analog_volt_map'] = self.powermeter_analog_volt_map 
            savedict['powermeter_initial_power'] = self.powermeter_initial_power
            savedict['powermeter_final_power'] = self.powermeter_final_power
        return savedict
    
    def update_display(self):
        
    
        if self.initial_scan_setup_plotting:
            #update figure
            self.time_trace_plotline.set_xdata(self.time_array)
            
            self.imgplot = self.aximg.imshow(self.integrated_count_map, 
                                        origin='lower',
                                        vmin=1e4, vmax=1e5, interpolation='nearest', 
                                        extent=self.imshow_extent)

            self.initial_scan_setup_plotting = False
        #if self.record_power:
        #    print "power_meter analog voltage", self.pm_power_v
        
        #self.ax_time.axhline(2**16)
        
        self.time_trace_plotline.set_ydata(1+self.picoharp.histogram_data[0:self.stored_histogram_channels.val])
        #i,j = self.current_index
        #self.time_trace_plotline.set_ydata(1+self.time_trace_map[j,i-1:])
        
        # integrated map
        map_type = 'lifetime'
        
        if map_type == 'int':
            C = (self.integrated_count_map)
            self.imgplot.set_data(C)         
            try:
                count_min =  np.min(C[np.nonzero(C)])
            except Exception:
                count_min = 0
            count_max = np.max(C)
            self.imgplot.set_clim(count_min, count_max + 1)
            
        # lifetime 
        if map_type == 'lifetime':
            x=1-0.36787944117
            #kk_start = 10#kk_bg_max+50/2
            kk_start = self.time_trace_map[0,0,:].argmax()
            kk_bg_max = int(0.80*kk_start) #100/2
            kk_final = self.stored_histogram_channels.val
            bg_slice = slice(0,kk_bg_max)
            bg = np.average(self.time_trace_map[:,:,bg_slice], axis=2).reshape(self.Nv*1,self.Nh*1,1)
            t  = self.time_trace_map[:,:,kk_start:kk_final]-bg
            C = self.time_array[np.argmin(np.abs(np.cumsum(t, axis=2)/np.sum(t, axis=2).reshape(self.Nv*1,self.Nh*1,1)-x), axis=2)]
            # 
            self.imgplot.set_data(C)
            c0,c1 = np.percentile(C,10), np.percentile(C,90)
            c0,c1 = 0.0,0.5
        
        
            self.imgplot.set_clim(c0, c1)
            self.imgplot.set_cmap('hot')
            self.aximg.set_title("color range: {} -> {} ns".format(c0,c1))
            #self.imgplot.colorbar()
            
        # Gated integrated map
        if  map_type=='gated':
            t_start = 3.5
            kk_start = np.searchsorted(self.time_array, t_start) #np.argmin(np.abs(self.time_array - t_start))
            C = self.time_trace_map[:,:,kk_start:].sum(axis=2)
            c0,c1 = np.percentile(C,67), np.percentile(C,99)
            self.imgplot.set_data(C)
            self.imgplot.set_clim(c0, c1)
            self.imgplot.set_cmap('gist_heat')
            
            
        self.fig.canvas.draw()
        
        
class TRPLScan3DMeasurement(Base3DScan):
    
    name = "trpl_scan3d"
    
    def scan_specific_setup(self):
        self.stored_histogram_channels = self.add_logged_quantity("stored_histogram_channels", dtype=int, vmin=1, vmax=2**16, initial=4000)
        self.initial_scan_setup_plotting = True
        
    def setup_figure(self):
        pass
    
    def pre_scan_setup(self):
        #hardware
        ph = self.picoharp = self.gui.picoharp_hc.picoharp
        
        
        self.record_power = False
        if self.gui.thorlabs_powermeter_analog_readout_hc.connected.val and self.gui.thorlabs_powermeter_hc.connected.val:
            self.record_power = True
            self.pm_analog_readout = self.gui.thorlabs_powermeter_analog_readout_hc
            self.gui.thorlabs_powermeter_hc.read_from_hardware()
        else:
            print self.gui.thorlabs_powermeter_analog_readout_hc.connected.val, self.gui.thorlabs_powermeter_hc.connected.val
            raise IOError("power meter not connected")
        
        # TRPL scan specific setup
        self.sleep_time = np.min(np.max(0.1*ph.Tacq*1e-3, 0.010), 0.100) # check every 1/10 of Tacq with limits of 10ms and 100ms

        #create data arrays
        if self.record_power:
            self.powermeter_analog_volt_map = np.zeros((self.Nz, self.Ny, self.Nx), dtype=float)
        self.integrated_count_map = np.zeros((self.Nz, self.Ny, self.Nx), dtype=int)
        print "size of time_trace_map %e" %  (self.Nx* self.Ny * self.Nz * self.stored_histogram_channels.val)

        self.time_trace_map = np.zeros( (self.Nz, self.Ny, self.Nx, self.stored_histogram_channels.val),dtype=np.uint16)
        
        self.time_array = ph.time_array[0:self.stored_histogram_channels.val]*1e-3
        self.elapsed_time_array = np.zeros((self.Nz, self.Ny, self.Nx), dtype=float)
        
        
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
            time.sleep(0.01) #self.sleep_time)  
        ph.stop_histogram()
        ph.read_histogram_data()
        
        t1 = time.time()
        T_pixel=(t1-t0)
        total_px = self.Nx*self.Ny*self.Nz
        print "time per pixel:", T_pixel, '| estimated total time (h)', total_px*T_pixel/3600, self.Nx, self.Ny, self.Nz

        if self.record_power:
            self.pm_power_v = self.pm_analog_readout.voltage.read_from_hardware()       

        # store in arrays
        N = self.stored_histogram_channels.val
        self.time_trace_map[k,j,i,:] = ph.histogram_data[0:N]
        self.integrated_count_map[k,j,i] = np.sum(self.time_trace_map[k,j,i])
        if self.record_power:
            self.powermeter_analog_volt_map[k,j,i] = self.pm_power_v
        self.elapsed_time_array[k,j,i] = ph.read_elapsed_meas_time()


    def scan_specific_savedict(self):
        savedict=dict( integrated_count_map=self.integrated_count_map,
                     time_trace_map = self.time_trace_map,
                     time_array = self.time_array,
                     elapsed_time_array = self.elapsed_time_array,
                     )
        if self.record_power:
            savedict['powermeter_analog_volt_map'] = self.powermeter_analog_volt_map  
        return savedict
          
    def update_display(self):
        return
        #self.initial_scan_setup_plotting =True
        if self.initial_scan_setup_plotting:

            self.fig = self.gui.trpl_scan_measure.fig
            self.time_trace_plotline = self.gui.trpl_scan_measure.time_trace_plotline
            
            visual_slice = [np.s_[:], np.s_[:], np.s_[:]]
            visual_slice[self.slow_axis_id] = 0
            print self.integrated_count_map.shape
            print visual_slice
            print self.integrated_count_map[visual_slice[::-1]].shape
            self.imgplot = self.gui.trpl_scan_measure.aximg.imshow( self.integrated_count_map[visual_slice[::-1]],
                                                                    origin='lower',
                                                                    interpolation='none',
                                                                    extent = self.fast_imshow_extent)    
            self.initial_scan_setup_plotting = False
                
        self.time_trace_plotline.set_ydata(1+self.picoharp.histogram_data[0:self.stored_histogram_channels.val]) # FIXME
        
        visual_slice = [np.s_[:], np.s_[:], np.s_[:]]
        visual_slice[self.slow_axis_id] = self.ijk[self.slow_axis_id]

        
        #integrated count map
        if True:
            #CT= np.log10(self.integrated_count_map[visual_slice[::-1]])
            C = (self.integrated_count_map[visual_slice[::-1]])
            self.imgplot.set_data(C)
            #self.imgplot.set_cmap('hot')
            
            #print self.fast_imshow_extent
            
            try:
                count_min =  -1 #np.min(C[np.nonzero(C)])
            except Exception:
                count_min = 0
            count_max = np.max(C)
            self.imgplot.set_clim(count_min, count_max + 1)
        
        
        # lifetime 
        if False:
            x=1-0.36787944117
            kk_bg_max = 50
            kk_start = kk_bg_max+25
            kk_final = 400
            bg_slice = np.s_[0:kk_bg_max]
            #bg_full_slice = visual_slice[::-1] + [bg_slice,]
            print "A"
            bg = np.average(self.time_trace_map[:,:,:,bg_slice], axis=3).reshape(self.Nz,self.Ny, self.Nx,1)
            print "B"
            #fit_slice = visual_slice[::-1] + [np.s_[kk_start:kk_final],]
            t  = self.time_trace_map[:,:,:,kk_start:kk_final ]-bg
            print "C"
            C = self.time_array[np.argmin(np.abs(np.cumsum(t, axis=3)/np.sum(t, axis=3).reshape(self.Nz,self.Ny, self.Nx,1)-x), axis=3)]
            # 
            self.imgplot.set_data(C[visual_slice[::-1]])
            self.imgplot.set_clim(0,4)

        
        
        self.fig.canvas.draw()
        
        pass
        
