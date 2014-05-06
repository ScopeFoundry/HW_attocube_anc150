# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 10:46:23 2014

@author: lab
"""

import numpy as np
import time
import threading
from PySide import QtCore

class ScanningPLEMeasurement(object):
    
    pass


ROW0 = 241
ROW1 = 271

PM_SAMPLE_NUMBER = 3

UP_AND_DOWN_SWEEP = True

class PLEPointMeasurement(QtCore.QObject):
    
    measurement_sucessfully_completed = QtCore.Signal(()) # signal sent when full measurement is complete


    def __init__(self, gui):
        QtCore.QObject.__init__(self)
        
        self.gui= gui
        self.name = "ple_point"        
        
        # This is a "brilliant" hack to make the autocompletion work in the Spyder 
        # IDE.  This does not serve any functional purpose!
        if 0:        
            from microscope_gui import MicroscopeGUI
            self.gui = MicroscopeGUI(gui)
            
        self.display_update_timer = QtCore.QTimer(self.gui.ui)
        self.display_update_timer.timeout.connect(self.on_display_update_timer)

    
    def setup_figure(self):
        # AOTF Point Scan Figure ####
        self.fig_aotf_point_scan = self.gui.add_figure('aotf_point_scan', self.gui.ui.aotf_point_scan_plot_groupBox)
        
        self.ax_excite_power = self.fig_aotf_point_scan.add_subplot(221)
        self.ax_excite_power.set_ylabel("power (W)")

        self.ax_laser_spec = self.fig_aotf_point_scan.add_subplot(222)
        self.ax_laser_spec.set_xlabel("wavelenth (nm)")
        
        self.ax_emission_intensity = self.fig_aotf_point_scan.add_subplot(223)
        self.ax_emission_intensity.set_ylabel("Counts")
        
        self.ax_result = self.fig_aotf_point_scan.add_subplot(224)
        self.ax_result.set_xlabel("wavelength (nm)")
        self.ax_result.set_ylabel("intensity 'a.u.'")
        
        for ax in [self.ax_excite_power, self.ax_emission_intensity]:
            ax.set_xlabel("frequency (MHz)")
        
    
    def _run(self):    
        # Local objects used for measurement
        oospectrometer = self.gui.oo_spectrometer
        ccd = self.gui.andor_ccd
       
        # Turn the AOTF modulation on.
        self.gui.aotf_modulation.update_value(True)        

        # CCD setup/initialization               
        self.gui.andor_ccd_shutter_open.update_value(True)
        
        # Wavelengths from the OceanOptics
        self.oo_wavelengths = oospectrometer.wavelengths

        # read current stage position        
        self.gui.read_stage_position()


  
        # List of frequency steps to take based on min, max and step size specified 
        # in the GUI
        freqs1 = np.arange(self.gui.ui.aotf_freq_start_doubleSpinBox.value(),
                          self.gui.ui.aotf_freq_stop_doubleSpinBox.value(),
                          self.gui.ui.aotf_freq_step_doubleSpinBox.value())
        
        # Sweep the frequencies up and down or just up?
        if UP_AND_DOWN_SWEEP:            
            freqs2 = np.flipud(freqs1)
            self.freqs = np.concatenate((freqs1,freqs2))
        else:
            self.freqs = freqs1

        # Define a local variable for quicker reference.
        freqs = self.freqs
                          
        # Data recorded from the measurement
        self.oo_specs = np.zeros( (len(freqs), len(self.oo_wavelengths)), dtype=int)
        self.ccd_specs = np.zeros( (len(freqs), self.gui.andor_ccd.Nx_ro), dtype=int)
        self.oo_wl_maxs = np.zeros( len(freqs), dtype=float)
        self.pm_powers = np.ones( len(freqs), dtype=float)*1e-9
        self.total_emission_intensity = np.zeros( len(freqs), dtype=int)
        

        # setup figure plotlines
        for ax in [self.ax_excite_power, self.ax_laser_spec, self.ax_emission_intensity, self.ax_result]:
            ax.lines = []
            
        self.excite_power_plotline, = self.ax_excite_power.plot(freqs, np.zeros_like(freqs))                       
        self.laser_spec_plotline, = self.ax_laser_spec.plot(self.oo_wavelengths, 
                                                            np.zeros_like(self.oo_wavelengths, dtype=int))                       
        self.emission_intensity_plotline, = self.ax_emission_intensity.plot(freqs, np.zeros_like(freqs))                       
        self.result_plotline, = self.ax_result.plot(np.zeros_like(freqs), np.zeros_like(freqs))                       
 
        self.spec_wl = 0                 
                 
        # Setup complete... start sweep and perform the measurement!
        for ii, freq in enumerate(freqs):
            print ii, freq
            if self.interrupt_measurement_called:
                break
            self.gui.aotf_freq.update_value(freq)
            time.sleep(0.1)
            oospectrometer.acquire_spectrum()
            
            oo_spectrum = oospectrometer.spectrum.copy()
            self.oo_specs[ii] = (oo_spectrum)
            
            #compute wavelength of laser
            max_i = oo_spectrum[10:-10].argmax() + 10
            wl = self.oo_wavelengths[max_i]
            self.oo_wl_maxs[ii] = wl
            
            try_count = 0
            while True:
                try:
                    self.gui.power_meter_wavelength.update_value(wl)
                    break
                except (ValueError, IOError):
                    try_count = try_count + 1
                    if try_count > 9:
                        break
                    time.sleep(0.010)
                    print "  Trying to set wavelength again..."
            
            time.sleep(0.150)
            
            samp_count = 0
            pm_power = 0.
            for samp in range(0, PM_SAMPLE_NUMBER):
                try_count = 0
                while True:
                    try:
                        pm_power = pm_power + self.gui.laser_power.read_from_hardware(send_signal=True)
                        samp_count = samp_count + 1
                        break 
                    except (ValueError, IOError):
                        try_count = try_count + 1
                        if try_count > 9:
                            break
                        time.sleep(0.010)
             
            if samp_count > 0:              
                pm_power = pm_power/samp_count
            else:
                print "  Failed to read power"
                pm_power = 10000.
                
            self.pm_powers[ii] = pm_power
            
            ccd.start_acquisition()
            stat = "ACQUIRING"
            while stat!= "IDLE":
                time.sleep(ccd.exposure_time * 0.25)
                stati, stat = ccd.get_status()
            ccd.get_acquired_data()
        
            spectrum = np.sum(ccd.buffer[ROW0:ROW1,:], axis=0)
            
            self.ccd_specs[ii] = spectrum

            self.total_emission_intensity[ii] = spectrum.sum() 
            
            self.ii = ii
        
        
        save_dict = {
                     'oo_specs': self.oo_specs,
                     'ccd_specs': self.ccd_specs,
                     'freqs': freqs,
                     'spec_wl': self.spec_wl,
                     'oo_wavelengths': self.oo_wavelengths,
                     'oo_wl_max': self.oo_wl_maxs,
                     'pm_powers': self.pm_powers
                    }               
                    
        
        for key in self.gui.logged_quantities.keys():
            save_dict[key] = self.gui.logged_quantities[key].val
            
        np.savez_compressed("%i_aotf_spec_scan.npz" % time.time(), **save_dict)
                    
        self.gui.andor_ccd_shutter_open.update_value(False)
        
        if not self.interrupt_measurement_called:
            self.measurement_sucessfully_completed.emit()
        else:
            pass
        

    
    @QtCore.Slot()
    def start(self):
        self.interrupt_measurement_called = False
        self.acq_thread = threading.Thread(target=self._run)
        self.acq_thread.start()
        self.t_start = time.time()
        self.display_update_timer.start(100)
    
    @QtCore.Slot()
    def interrupt(self):
        self.interrupt_measurement_called = True
        #Make sure display is up to date        
        self.on_display_update_timer() 

    def is_measuring(self):
        return self.acq_thread.is_alive()
        
    
    @QtCore.Slot()
    def on_display_update_timer(self):
        #update figure
        
        self.excite_power_plotline.set_ydata(self.pm_powers)
                       
        self.laser_spec_plotline.set_ydata(self.oo_specs[self.ii])
                      
        self.emission_intensity_plotline.set_ydata(self.total_emission_intensity)
        
        self.result_plotline.set_data(self.oo_wl_maxs, self.total_emission_intensity/self.pm_powers)    
        
        for ax in self.fig_aotf_point_scan.axes:
            ax.relim()
            ax.autoscale_view()
        
        self.fig_aotf_point_scan.canvas.draw()
        
        if not self.is_measuring():
            self.display_update_timer.stop()

            
    


    