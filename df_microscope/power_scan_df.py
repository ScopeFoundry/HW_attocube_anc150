from ScopeFoundry import Measurement
import numpy as np
import time
from ScopeFoundry import h5_io
from ScopeFoundry.helper_funcs import sibling_path
import pyqtgraph as pg

class PowerScanDF(Measurement):
    
    name = 'power_scan_df'
    
    def __init__(self, app):
        self.ui_filename = sibling_path(__file__, "power_scan_df.ui")
        print(self.ui_filename)
        Measurement.__init__(self, app)
        
    def setup(self):
        
        self.power_wheel_min = self.add_logged_quantity("power_wheel_min", 
                                                          dtype=int, unit='', initial=10, vmin=0, vmax=+3200, ro=False)
        self.power_wheel_max = self.add_logged_quantity("power_wheel_max", 
                                                          dtype=int, unit='', initial=10, vmin=0, vmax=+3200, ro=False)
        self.power_wheel_ndatapoints = self.add_logged_quantity("power_wheel_ndatapoints", 
                                                          dtype=int, unit='', initial=100, vmin=-3200, vmax=+3200, ro=False)
        
        self.collect_apd      = self.add_logged_quantity("collect_apd",      dtype=bool, initial=True)
        self.collect_spectrum = self.add_logged_quantity("collect_spectrum", dtype=bool, initial=False)
        #self.collect_lifetime = self.add_logged_quantity("collect_lifetime", dtype=bool, initial=True)
        
        self.up_and_down_sweep    = self.add_logged_quantity("up_and_down_sweep",dtype=bool, initial=True)

        
    
    def setup_figure(self):
        
        self.ui.start_pushButton.clicked.connect(self.start)
        self.ui.interrupt_pushButton.clicked.connect(self.interrupt)

        self.power_wheel_min.connect_bidir_to_widget(self.ui.powerwheel_min_doubleSpinBox)
        self.power_wheel_max.connect_bidir_to_widget(self.ui.powerwheel_max_doubleSpinBox)
        self.power_wheel_ndatapoints.connect_bidir_to_widget(self.ui.num_datapoints_doubleSpinBox)

        self.collect_apd.connect_bidir_to_widget(self.ui.collect_apd_checkBox)
        self.collect_spectrum.connect_bidir_to_widget(self.ui.collect_spectrum_checkBox)
        
        self.app.hardware.apd_counter.settings.int_time.connect_bidir_to_widget(
                                                                self.ui.apd_int_time_doubleSpinBox)
        self.app.hardware.WinSpecRemoteClient.settings.acq_time.connect_bidir_to_widget(
                                                                self.ui.spectrum_int_time_doubleSpinBox)


        # Plot
        
        if hasattr(self, 'graph_layout'):
            self.graph_layout.deleteLater() # see http://stackoverflow.com/questions/9899409/pyside-removing-a-widget-from-a-layout
            del self.graph_layout
        self.graph_layout=pg.GraphicsLayoutWidget(border=(100,100,100))
        self.ui.plot_groupBox.layout().addWidget(self.graph_layout)
        
        self.plot1 = self.graph_layout.addPlot(title="Power Scan")

        self.plot_line1 = self.plot1.plot([0])

    def update_display(self):
        
        if self.settings['collect_spectrum']:
            self.plot_line1.setData(self.pm_powers[:self.ii], self.integrated_spectra[:self.ii])
        


    def run(self):
        
        
        if self.settings['collect_apd']:
            self.apd_counter_hc = self.app.hardware.apd_counter
            self.apd_count_rate_lq = self.apd_counter_hc.settings.apd_count_rate     

        if self.settings['collect_spectrum']:
            self.winspec_readout = self.app.measurements.WinSpecRemoteReadout
        
        #####
        self.Np = Np = self.power_wheel_ndatapoints.val
        self.step_size = int( (self.power_wheel_max.val-self.power_wheel_min.val)/Np )
        
    
        if self.settings['up_and_down_sweep']:
            self.direction = np.ones(Np*2)
            self.direction[Np:] = -1
            Np = self.Np = 2*Np
        else:
            self.direction = np.ones(Np)
    
        # Create Data Arrays    
        self.power_wheel_position = np.zeros(Np)      
        
        self.pm_powers = np.zeros(Np, dtype=float)
        self.pm_powers_after = np.zeros(Np, dtype=float)

        if self.settings['collect_apd']:
            self.apd_count_rates = np.zeros(Np, dtype=float)
        if self.settings['collect_spectrum']:
            self.spectra = [] # don't know size of ccd until after measurement
            self.integrated_spectra = []
        
        ### Acquire data
        
        self.move_to_min_pos()
        
        self.ii = 0
        
        # loop through power wheel positions
        for ii in range(self.Np):
            self.ii = ii
            self.settings['progress'] = 100.*ii/self.Np
            
            if self.interrupt_measurement_called:
                break
            
            # record power wheel position
            self.power_wheel_position[ii] = self.power_wheel.read_encoder()
            
            # collect power meter value
            self.pm_powers[ii]=self.collect_pm_power_data()
            
            # read detectors
            if self.settings['collect_apd']:
                self.apd_count_rates[ii] = self.collect_apd_data()                
            if self.settings['collect_spectrum']:
                self.winspec_readout.run()
                spec = np.array(self.winspec_readout.data)
                self.spectra.append( spec )
                self.integrated_spectra.append(spec.sum())
                
            # collect power meter value after measurement
            self.pm_powers_after[ii]=self.collect_pm_power_data()

                            
            # move to new power wheel position
            self.power_wheel.write_steps_and_wait(self.step_size*self.direction[ii])
            time.sleep(2.0)

        # write data to data file disk
        
        self.t0 = time.time()
        self.fname = "%i_%s.h5" % (self.t0, self.name)
        self.h5_file = h5_io.h5_base_file(self.app, self.fname )
        self.h5_file.attrs['time_id'] = self.t0
        H = self.h5_meas_group  =  h5_io.h5_create_measurement_group(self, self.h5_file)
    
        #create h5 data arrays

        if self.settings['collect_apd']:
            H['apd_count_rates'] = self.apd_count_rates
        if self.settings['collect_spectrum']:
            H['wls'] = self.winspec_readout.wls
            H['spectra'] = np.squeeze(np.array(self.spectra))
            H['integrated_spectra'] = np.array(self.integrated_spectra)
        H['pm_powers'] = self.pm_powers
        H['pm_powers_after'] = self.pm_powers_after
        H['power_wheel_position'] = self.power_wheel_position
        H['direction'] = self.direction
        self.h5_file.close()
        
        print self.name, 'data saved', self.fname

            
            

    def move_to_min_pos(self):
        self.power_wheel = self.app.hardware.power_wheel_arduino.power_wheel
        self.power_wheel.read_status()
        
        stiep= self.power_wheel_min.val - self.power_wheel.encoder_pos
        if stiep != 0:
            #print 'moving to min pos'
            self.power_wheel.write_steps_and_wait(stiep)
            #print 'done moving to min pos'
            
    def collect_apd_data(self):
        apd = self.apd_counter_hc
        
        # collect data
        apd.apd_count_rate.read_from_hardware()
                                      
        # read data
        count_rate = apd.apd_count_rate.val
        
        return count_rate
    
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
                    pm_power = pm_power + self.app.hardware['thorlabs_powermeter'].power.read_from_hardware(send_signal=True)
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
