'''
Created on Jun 19, 2014

@author: Edward Barnard
'''
import numpy as np
import time
import threading

from .measurement import Measurement 

PM_SAMPLE_NUMBER = 1

# Optional amount of time to wait between measurement steps to let sample relax to
# ground state from one excitation energy to the next.  This only works if a shutter
# is installed.  Set to 0 to disable.  
WAIT_TIME_BETWEEN_STEPS = 1  # Units are seconds!

class PowerScanMotorized(Measurement):
    name = "power_scan_motorized"
    
    def setup(self):

        #logged Quantities
        self.power_wheel_steps = self.add_logged_quantity("power_wheel_steps", 
                                                          dtype=int, unit='', initial=90, vmin=0, vmax=+8000, ro=False)
        self.power_wheel_steps.connect_bidir_to_widget(self.gui.ui.power_scan_motorized_steps_doubleSpinBox)

        self.power_wheel_delta = self.add_logged_quantity("power_wheel_delta", 
                                                          dtype=float, unit='deg', initial=4, vmin=-360, vmax=+360, ro=False)
        self.power_wheel_delta.connect_bidir_to_widget(self.gui.ui.power_scan_motorized_delta_doubleSpinBox)

        self.collect_apd      = self.add_logged_quantity("collect_apd",      dtype=bool, initial=False)
        self.collect_lockin   = self.add_logged_quantity("collect_lockin",   dtype=bool, initial=False)
        self.collect_spectrum = self.add_logged_quantity("collect_spectrum", dtype=bool, initial=False)
        self.collect_lifetime = self.add_logged_quantity("collect_lifetime", dtype=bool, initial=False)
        
        self.use_shutter      = self.add_logged_quantity("use_shutter",
                                                         dtype=bool, initial=False)
        # Up and down sweeps 
        self.up_and_down_sweep = self.add_logged_quantity("up_and_down_sweep",
                                                          dtype=bool, initial=True)

        # GUI
        self.gui.ui.power_scan_motorized_start_pushButton.clicked.connect(self.start)
        self.gui.ui.power_scan_motorized_interrupt_pushButton.clicked.connect(self.interrupt)

        self.collect_apd.connect_bidir_to_widget(self.gui.ui.power_scan_motorized_collect_apd_checkBox)
        self.collect_lockin.connect_bidir_to_widget(self.gui.ui.power_scan_motorized_collect_lockin_checkBox)
        self.collect_spectrum.connect_bidir_to_widget(self.gui.ui.power_scan_motorized_collect_spectrum_checkBox)
        self.collect_lifetime.connect_bidir_to_widget(self.gui.ui.power_scan_motorized_collect_lifetime_checkBox)

        self.use_shutter.connect_bidir_to_widget(self.gui.ui.power_scan_motorized_use_shutter_checkBox)
        self.up_and_down_sweep.connect_bidir_to_widget(self.gui.ui.power_scan_motorized_up_and_down_sweep_checkBox)

    def setup_figure(self):
        self.fig = self.gui.add_figure('power_scan', self.gui.ui.power_scan_plot_widget)


    def _run(self):
        # Connect to hardware

        pw = self.power_wheel = self.gui.power_wheel_arduino_hc.power_wheel

        if self.collect_apd.val:
            self.apd_counter_hc = self.gui.apd_counter_hc
            self.apd_count_rate = self.gui.apd_counter_hc.apd_count_rate     
                   
        if self.collect_lockin.val:
            lockin = self.lockin = self.gui.srs_lockin_hc.srs
        if self.collect_spectrum.val:
            ccd = self.ccd = self.gui.andor_ccd_hc.andor_ccd        
            ccd_width_px = ccd.Nx_ro
            t_acq = self.gui.andor_ccd_hc.exposure_time.val #in seconds
            self.ccd_wait_time = np.min(1.0,np.max(0.05*t_acq, 0.05)) # limit update period to 50ms (in ms) or as slow as 1sec
            self.ccd_do_bgsub = bool(self.gui.ui.andor_ccd_bgsub_checkBox.checkState())
            if self.ccd_do_bgsub:
                self.ccd_do_bgsub = self.gui.andor_ccd_hc.is_background_valid()
            
            if self.ccd_do_bgsub:
                self.ccd_bg = self.gui.andor_ccd_hc.background
            else:
                self.ccd_bg = None
        if self.collect_lifetime.val:
            ph = self.picoharp = self.gui.picoharp_hc.picoharp
            self.ph_sleep_time = np.min(np.max(0.1*ph.Tacq*1e-3, 0.010), 0.100) # check every 1/10 of Tacq with limits of 10ms and 100ms
            self.ph_hist_chan = ph.HISTCHAN
            
        # Use a shutter if it is installed; NOTE:  shutter is assumed to be after the OO
        # and PM and only opens for data acquisition.
        if self.gui.shutter_servo_hc.connected.val and self.use_shutter.val:
            use_shutter = True
            shutter = self.gui.shutter_servo_hc
            #USE_SHUTTER =False
            # Start with shutter closed.
            shutter.shutter_open.update_value(False)
        else:
            use_shutter = False
            
        
        #Record ocean optics spectrum if the spectrometer is connected
        if self.gui.oceanoptics_spec_hc.connected.val:
            # Record laser spectrum from OO 
            oospectrometer = self.gui.oceanoptics_spec_hc.oo_spectrometer
            oospectrometer.acquire_spectrum()
            self.oo_spec = oospectrometer.spectrum.copy()
        
        # Data arrays
        pw_steps = self.power_wheel_steps.val
        pw_delta = self.power_wheel_delta.val
        
        
        pw_steps_per_delta = int((pw_delta*3200/360.))
        print 'steps per delta:', pw_steps_per_delta
    
        if self.up_and_down_sweep.val:
            direction = np.ones(pw_steps*2)
            direction[pw_steps:] = -1
            pw_steps = 2*pw_steps
        else:
            direction = np.ones(pw_steps)
    
        # Create Data Arrays    
        self.pw_phi = np.zeros(pw_steps)      
        
        self.pm_powers = np.zeros(pw_steps, dtype=float)
        self.pm_powers_after = np.zeros(pw_steps, dtype=float)

        if self.collect_apd.val:
            self.apd_count_rates = np.zeros(pw_steps, dtype=float)
        if self.collect_lockin.val:
            self.chopped_current = np.zeros(pw_steps, dtype=float)
        if self.collect_spectrum.val:
            self.spectra = np.zeros( (pw_steps, ccd_width_px), dtype=float )
        if self.collect_lifetime.val:
            self.time_traces = np.zeros( (pw_steps, self.ph_hist_chan), dtype=int )
            self.elapsed_times = np.zeros(pw_steps, dtype=float)
        
        # setup figure
        self.fig.clf()
        
        self.ax_power = self.fig.add_subplot(212)
        if self.collect_spectrum.val:
            self.ax_spec  = self.fig.add_subplot(211)
        
        self.power_plotline, = self.ax_power.plot([1],[1],'o-')
        if self.collect_spectrum.val:
            self.spec_plotline, = self.ax_spec.plot(np.arange(self.ccd.Nx_ro), np.zeros(self.ccd.Nx_ro))
        
        # SCAN!!!
        
        try:
            for ii in range(pw_steps):
                print ii, pw_steps
                
                self.ii = ii
                if self.interrupt_measurement_called: break
                
                # Move power wheel
                pw.write_steps(pw_steps_per_delta*direction[ii])
                self.pw_phi[ii] = ii*pw_steps_per_delta*360/3200
                
                # Sleep to give the powerwheel time to complete rotation
                time.sleep(2.0)
                #TODO check to see if powerwheel is finished moving
                
                # collect power meter value
                self.pm_powers[ii]=self.collect_pm_power_data()
                
                # Open shutter
                if use_shutter:
                    shutter.shutter_open.update_value(True)
                    time.sleep(1.0) # wait for shutter to open
                
                # Collect Data from detectors
                if self.collect_apd.val:
                    self.apd_count_rates[ii] = self.collect_apd_data()
                if self.collect_lockin.val:
                    #FIXME
                    self.chopped_current[ii] = self.collect_lifetime_data()
                if self.collect_spectrum.val:
                    self.spectra[ii,:] = self.collect_spectrum_data()
                if self.collect_lifetime.val:
                    self.time_traces[ii,:], self.elapsed_times[ii] = self.collect_lifetime_data()
                    
                # CLose shutter
                if use_shutter:
                    shutter.shutter_open.update_value(False)
                
                self.pm_powers_after[ii]=self.collect_pm_power_data()
                
                
                # Wait between steps if desired
                if use_shutter and WAIT_TIME_BETWEEN_STEPS > 0:
                    time.sleep(WAIT_TIME_BETWEEN_STEPS)

                #print self.name, 'measured ',  self.chopped_current[ii], 'at phi=', self.pw_phi[ii]


        finally:
            #save data file
            save_dict = {
                         'pm_powers': self.pm_powers,
                         'pm_powers_after': self.pm_powers_after,
                         'pw_phi': self.pw_phi,
                         'pw_steps_per_delta': pw_steps_per_delta,
                         }
            
            if self.gui.oceanoptics_spec_hc.connected.val:
                save_dict['oo_spec'] = self.oo_spec
            
            if self.collect_apd.val:
                save_dict['apd_count_rates'] = self.apd_count_rates
                pass
            if self.collect_lockin.val:
                save_dict['chopped_current'] = self.chopped_current
            
            if self.collect_spectrum.val:
                save_dict['spectra'] = self.spectra
                
            if self.collect_lifetime.val:
                save_dict['time_traces'] = self.time_traces
                save_dict['time_array' ] = self.picoharp.time_array
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
            print "Motorized Power Scan Saved", self.fname

            if not self.interrupt_measurement_called:
                self.measurement_sucessfully_completed.emit()
            else:
                pass
        
    
    def collect_apd_data(self):
        apd = self.apd_counter_hc
        
        # collect data
        apd.apd_count_rate.read_from_hardware()
                                      
        # read data
        count_rate = apd.apd_count_rate.val
        
        return count_rate
    
    def collect_lockin_data(self):
        sens_changed = self.lockin.auto_sensitivity()
        if sens_changed:
            time.sleep(0.5)
        return self.lockin.get_signal()        
    
    def collect_spectrum_data(self):
        ccd = self.ccd
        ccd.start_acquisition()
        while not self.interrupt_measurement_called:
            stat = ccd.get_status()
            if stat == 'IDLE':
                # grab data
                buffer_ = ccd.get_acquired_data()
                if self.ccd_do_bgsub:
                    buffer_ = buffer_ - self.ccd_bg
                #spectrum_data = np.average(buffer_, axis=0)
                break
            else:
                time.sleep(self.ccd_wait_time)            
        # while-loop is complete
        if self.interrupt_measurement_called:
            self.gui.andor_ccd_hc.interrupt_acquisition()
            self.spectrum = None
        else:
            self.spectrum = np.average(buffer_.copy(), axis=0)
        
        return self.spectrum  
    
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
        elapsed_meas_time = self.picoharp.read_elapsed_meas_time()
        
        t1 = time.time()
        #print "time per pixel:", (t1-t0)
        return self.picoharp.histogram_data, elapsed_meas_time
    
    def collect_pm_power_data(self):
        PM_SAMPLE_NUMBER = 10

        # Sample the power at least one time from the power meter.
        samp_count = 0
        pm_power = 0.0
        for samp in range(0, PM_SAMPLE_NUMBER):
            # Try at least 10 times before ultimately failing
            if self.interrupt_measurement_called: break
            try_count = 0
            #print "samp", ii, samp, try_count, samp_count, pm_power
            while not self.interrupt_measurement_called:
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

        
        return pm_power

    def update_display(self):
        if self.collect_apd.val:
            self.power_plotline.set_data(self.pm_powers[:self.ii], self.apd_count_rates[:self.ii])
        if self.collect_spectrum.val:
            self.power_plotline.set_data(self.pm_powers[:self.ii], np.sum(self.spectra[:self.ii,:],axis=1))
            #self.spec_plotline, = self.ax_spec.plot(np.arange(512), np.zeros(512))
            self.spec_plotline.set_ydata(self.spectra[self.ii,:])
            self.ax_spec.relim()
            self.ax_spec.autoscale_view(scalex=True, scaley=True)
        if self.collect_lockin.val:
            self.power_plotline.set_data(self.pm_powers[:,self.ii], self.chopped_current[:self.ii])
        if self.collect_lifetime.val:
            self.power_plotline.set_data(
                        self.pm_powers_after[:self.ii],
                        np.sum(self.time_traces[:self.ii,:],axis=1) / self.elapsed_times[:self.ii])
            self.ax_power.set_ylabel("kHz")
            self.ax_power.set_xlabel("Laser Power (W)")
            
        self.ax_power.relim()
        self.ax_power.autoscale_view(scalex=True, scaley=True)

        self.fig.canvas.draw()

class PowerScanContinuous(Measurement):
    
    name = "power_scan"
    
    def setup(self):
        
        self.display_update_period = 0.050 #seconds
        
        self.gui.ui.power_scan_cont_start_pushButton.clicked.connect(self.start)
        self.gui.ui.power_scan_interrupt_pushButton.clicked.connect(self.interrupt)
        
        # Data arrays
        self.pm_powers = []
        self.out_powers = []
        self.specs = []
        self.ii = 0
        
        self.bg_sub = True
        
        self.detector = 'CCD'


    def setup_figure(self):
        self.fig = self.gui.add_figure('power_scan', self.gui.ui.power_scan_plot_widget)
        self.fig.clf()
        
        self.ax_power = self.fig.add_subplot(212)
        self.ax_spec  = self.fig.add_subplot(211)
        
        self.power_plotline, = self.ax_power.plot([1],[1],'o-')
        if self.detector == 'CCD' and hasattr(self, 'andor_ccd'):
            self.spec_plotline, = self.ax_spec.plot(np.arange(self.andor_ccd.Nx_ro), np.zeros(self.andor_ccd.Nx_ro))
        
    def _run(self):

        self.detector = 'APD'
        #Setup hardware
        if self.detector == 'CCD':
            ccd = self.andor_ccd = self.gui.andor_ccd_hc.andor_ccd
        elif self.detector == 'APD':
            self.apd_counter_hc = self.gui.apd_counter_hc
            self.apd_count_rate = self.gui.apd_counter_hc.apd_count_rate


        t_acq = self.gui.andor_ccd_hc.exposure_time.val #in seconds
        wait_time = 0.05 # wait between check if ccd is done acquisition

    
        # Data arrays
        self.pm_powers = []
        self.out_powers = []
        self.specs = []
        
        try:
            self.ii = 0
            while not self.interrupt_measurement_called:
        
                if self.detector == 'CCD':
                    # start CCD measurement while power meter is acquiring
                    ccd.start_acquisition()

        
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
                    
                # Store in array  
                self.pm_powers.append(pm_power)
                
                
                # grab spectrum
                #ccd.start_acquisition()
                if self.detector == 'CCD':
                    stat = ccd.get_status()
                    print "stat", stat
                    while stat == 'ACQUIRING':
                        time.sleep(wait_time)            
                        stat = ccd.get_status()
                        if self.interrupt_measurement_called:
                            break
    
                    if stat == 'IDLE':
                        # grab spec data
                        buffer_ = ccd.get_acquired_data()
                        
                        if self.bg_sub:
                            bg = self.gui.andor_ccd_hc.background
                            if bg is not None:
                                if bg.shape == buffer_.shape:
                                    buffer_ = buffer_ - bg
                                else:
                                    print "Background not the correct shape", buffer_.shape, bg.shape
                            else:
                                print "No Background available, raw data shown"
                        self.spectrum_data = np.average(buffer_, axis=0)
                        
                    else:
                        raise ValueError("andor_ccd status should be 'IDLE', is '%s'" % stat)            
                            
                                      
                    # store spectrum in array
                    self.specs.append( self.spectrum_data )
                    self.out_powers.append( np.sum(self.spectrum_data)) 
                
                # grab apd count?
                elif self.detector == 'APD':
                    self.apd_count_rate.read_from_hardware()
                    self.out_powers.append( self.apd_count_rate.val )
                
                if self.ii % 10 == 0:
                    print self.ii, self.pm_powers[-1], self.out_powers[-1]
                
                self.ii += 1
        finally:
            #save data file
            save_dict = {
                         'pm_powers': self.pm_powers,
                         'out_powers': self.out_powers,
                         'N': self.ii,
                         'spectra': self.specs,
                         'bg_spec': self.gui.andor_ccd_hc.background,
                         'detector': self.detector,
                         }
            for lqname,lq in self.gui.logged_quantities.items():
                save_dict[lqname] = lq.val
            
            for hc in self.gui.hardware_components.values():
                for lqname,lq in hc.logged_quantities.items():
                    save_dict[hc.name + "_" + lqname] = lq.val
            
            for lqname,lq in self.logged_quantities.items():
                save_dict[self.name +"_"+ lqname] = lq.val

            self.fname = "%i_power_scan.npz" % time.time()
            np.savez_compressed(self.fname, **save_dict)
            print "Power Scan Saved", self.fname

            if not self.interrupt_measurement_called:
                self.measurement_sucessfully_completed.emit()
            else:
                pass
    
    
    def update_display(self):        
        #print "updating figure"
        self.power_plotline.set_data(self.pm_powers[:self.ii], self.out_powers[:self.ii])
        self.ax_power.relim()
        self.ax_power.autoscale_view(scalex=True, scaley=True)
        if self.detector == 'CCD':
            self.spec_plotline.set_ydata(self.specs[-1])
            self.ax_spec.relim()
            self.ax_spec.autoscale_view(scalex=False, scaley=True)

        self.fig.canvas.draw()
