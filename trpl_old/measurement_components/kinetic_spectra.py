from ScopeFoundry import Measurement
import time
import numpy as np
from measurement_components.andor_ccd_readout import pixel2wavelength

PM_SAMPLE_NUMBER = 5

class KineticSpectra(Measurement):

    name = "kinetic_spectra"
    
    def setup(self):        
        self.display_update_period = 0.100 #seconds

        self.frames = self.add_logged_quantity("frames", dtype=int, 
                                 vmin=1, vmax=1e6, initial=10)


        #connect events
        #self.gui.ui.andor_ccd_abort_bg_pushButton.clicked.connect(self.interrupt)
    def setup_figure(self):
        self.fig_ccd_image = self.gui.add_figure('ccd_image', self.gui.ui.plot_andor_ccd_widget)

    
    def _run(self):
        #hardware
        ccd = self.gui.andor_ccd_hc.andor_ccd
        

        
        width_px = ccd.Nx_ro
        height_px = ccd.Ny_ro

        self.wls  = pixel2wavelength(self.gui.acton_spec_hc.center_wl.val, 
                      np.arange(width_px), binning=ccd.get_current_hbin())

        
        do_bgsub = bool(self.gui.ui.andor_ccd_bgsub_checkBox.checkState())
        if do_bgsub:
            do_bgsub = self.gui.andor_ccd_hc.is_background_valid()
        
        if do_bgsub:
            bg = self.gui.andor_ccd_hc.background
        else:
            bg = None
                
        t_acq = self.gui.andor_ccd_hc.exposure_time.val #in seconds
        wait_time = np.min(1.0,np.max(0.05*t_acq, 0.05)) # limit update period to 50ms (in ms) or as slow as 1sec
        
        N = self.frames.val
        
        #create data arrays
        self.kinetic_spectra = np.zeros((N, width_px), dtype=float )
        self.kinetic_images = np.zeros((N, height_px, width_px), dtype=float)
        self.start_times = np.zeros(N, dtype=float)
        self.stop_times  = np.zeros(N, dtype=float)
        self.pm_powers = np.zeros(N, dtype=float)
    
    
        # figure
        self.fig_ccd_image.clf()
        #gs = gridspec.GridSpec(2,1,height_ratios=[1,4]) 
        self.ax_andor_ccd_spec = self.fig_ccd_image.add_subplot(111)
        #self.fig_ccd_image.add_subplot(gs[0])
        #self.ax_andor_ccd_image = self.fig_ccd_image.add_subplot(gs[1])
        self.andor_ccd_spec_line, = self.ax_andor_ccd_spec.plot( np.ones(width_px, dtype=np.int32), 'k-')
        self.ax_andor_ccd_spec.set_xlim(0,width_px)

        #start scan
        t0 = time.time()
        
        #Record ocean optics spectrum if the spectrometer is connected
        if self.gui.oceanoptics_spec_hc.connected.val:
            # Record laser spectrum from OO 
            oospectrometer = self.gui.oceanoptics_spec_hc.oo_spectrometer
            oospectrometer.acquire_spectrum()
            self.oo_spec = oospectrometer.spectrum.copy()
        
        use_pm = False
        """if hasattr(self.gui.thorlabs_powermeter_hc, 'power_meter'):
            use_pm = True
            power_meter = self.gui.thorlabs_powermeter_hc
        """    
    
        for ii in range(self.frames.val):
            if self.interrupt_measurement_called:
                break
            print "starting acq of frame", ii
            self.start_times[ii] = time.time() - t0
            ccd.start_acquisition()
            
            if use_pm:
                samp_count = 0
                pm_power = 0.
                for samp in range(0, PM_SAMPLE_NUMBER):
                    # Try at least 10 times before ultimately failing
                    try_count = 0
                    while True:
                        try:
                            pm_power = pm_power + power_meter.power.read_from_hardware(send_signal=True)
                            samp_count = samp_count + 1
                            break 
                        except Exception as err:
                            try_count = try_count + 1
                            if try_count > 9:
                                break
                            time.sleep(0.010)
                            print err
                if samp_count > 0:              
                    pm_power = pm_power/samp_count
                else:
                    print "  Failed to read power"
                    pm_power = 10000.    
                self.pm_powers[ii] = pm_power
            
            while not self.interrupt_measurement_called:
                stat = ccd.get_status()
                if stat == 'IDLE':
                    # grab data
                    self.stop_times[ii] = time.time() - t0
                    buffer_ = ccd.get_acquired_data()
                    if do_bgsub:
                        buffer_ = buffer_ - bg

                    spectrum_data = np.average(buffer_, axis=0)
                    self.kinetic_spectra[ii,:] = spectrum_data
                    self.kinetic_images[ii,:,:] = buffer_
                    #print buffer_.shape
                    break
                else:
                    time.sleep(0.001) #self.waittime        
            # while-loop is complete
            if self.interrupt_measurement_called:
                self.gui.andor_ccd_hc.interrupt_acquisition()
                self.spectrum = None
            else:
                self.spectrum = buffer_.copy()
                
        save_dict = {
                 'kinetic_spectra': self.kinetic_spectra,
                 'kinetic_images': self.kinetic_images,
                 'start_times': self.start_times,
                 't0': t0,
                 'pm_powers': self.pm_powers,
                 'wls': self.wls
                    }               
        
        if self.gui.oceanoptics_spec_hc.connected.val:
            save_dict['oo_spec'] = self.oo_spec
                
        for lqname,lq in self.gui.logged_quantities.items():
            save_dict[lqname] = lq.val
        
        for hc in self.gui.hardware_components.values():
            for lqname,lq in hc.logged_quantities.items():
                save_dict[hc.name + "_" + lqname] = lq.val
        
        for lqname,lq in self.logged_quantities.items():
            save_dict[self.name +"_"+ lqname] = lq.val

        self.fname = "%i_%s.npz" % (time.time(), self.name)
        np.savez_compressed(self.fname, **save_dict)
        print self.name, "saved:", self.fname
            

    
    def update_display(self):
        #print "Asdf"
        self.andor_ccd_spec_line.set_ydata(self.spectrum)
        #print np.max(self.spectrum)
        self.ax_andor_ccd_spec.relim()
        self.ax_andor_ccd_spec.autoscale_view(scalex=False, scaley=True)
        self.fig_ccd_image.canvas.draw()
        