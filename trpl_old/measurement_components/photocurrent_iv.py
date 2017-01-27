'''
Created on Sep 8, 2014

@author: Edward Barnard and Benedikt Ursprung
'''

from ScopeFoundry  import Measurement, LQRange, h5_io
import time
import numpy as np
from PySide.QtGui import QWidget, QVBoxLayout

class PhotocurrentIVMeasurement(Measurement):
    
    name = "photocurrrent_iv"
    
    def setup(self):
        self.display_update_period = 0.1 #seconds
        
        
        # logged quantities
        self.source_voltage_min = self.add_logged_quantity("source_voltage_min", dtype=float, initial = -5, unit='V', vmin=-5, vmax=5, ro=False)
        self.source_voltage_max = self.add_logged_quantity("source_voltage_max", dtype=float, initial = +5, unit='V', vmin=-5, vmax=5, ro=False)
        self.source_voltage_delta = self.add_logged_quantity("source_voltage_delta", dtype=float, initial=0.1, unit='V', vmin=-5, vmax=5, ro=False)
        self.source_voltage_steps = self.add_logged_quantity("source_voltage_steps", dtype=int, initial = 10, vmin=1, vmax=1000, ro=False)
        
        self.voltage_range = LQRange(self.source_voltage_min, self.source_voltage_max, self.source_voltage_delta, self.source_voltage_steps)

        try:              
            self.source_voltage_min.connect_bidir_to_widget(self.gui.ui.photocurrent_iv_vmin_doubleSpinBox)
            self.source_voltage_max.connect_bidir_to_widget(self.gui.ui.photocurrent_iv_vmax_doubleSpinBox)
            self.source_voltage_steps.connect_bidir_to_widget(self.gui.ui.photocurrent_iv_steps_doubleSpinBox)
            #connect events
            self.gui.ui.photocurrent_iv_start_pushButton.clicked.connect(self.start)
        except Exception as err:
            print self.name, "could not connect to custom gui", err

    
    def setup_figure(self):
        self.ui = QWidget(None)

        self.ui.setLayout(QVBoxLayout())
        self.fig = self.gui.add_figure_mpl("photocurrent_iv", self.ui )

        self.ui.show()
                    
        self.ax = self.fig.add_subplot(111)
        self.plotline, = self.ax.plot([0,1], [0,0])
        #self.ax.set_ylim(1e-1,1e5)
        self.ax.set_xlabel("Voltage (V)")
        self.ax.set_ylabel("Current (Amps)")
    


    def _run(self):
        
        self.initial_scan_setup_plotting = True
        
        #Hardware
        self.keithley_hc = self.gui.keithley_sourcemeter_hc
        K1 = self.keithley = self.keithley_hc.keithley
        
        
        # h5 data file setup
        self.t0 = time.time()
        self.h5_file = h5_io.h5_base_file(self.gui, "%i_%s.h5" % (self.t0, self.name) )
        self.h5_file.attrs['time_id'] = self.t0
        H = self.h5_meas_group = self.h5_file.create_group(self.name)        
        h5_io.h5_save_measurement_settings(self, H)
        h5_io.h5_save_hardware_lq(self.gui, H)
        
        
        K1.resetA()
        K1.setAutoranges_A()
        K1.switchV_A_on()
        I,V = K1.measureIV_A(self.source_voltage_steps.val, 
                             Vmin=self.source_voltage_min.val, 
                             Vmax = self.source_voltage_max.val, 
                             KeithleyADCIntTime=1, delay=0)
        
        K1.switchV_A_off()
        
        print I
        print V
        
        self.Iarray = I
        self.Varray = V
        
        #save some data
        save_dict = {
                     'I': self.Iarray,
                     'V': self.Varray
                     }
        self.fname = "%i_photocurrent_iv.npz" % time.time()
        np.savez_compressed(self.fname, **save_dict)
        print "photocurrent_iv Saved", self.fname
        
        #create h5 data arrays
        H['I'] = self.Iarray
        H['V'] = self.Varray
        
        self.h5_file.close()

        
        
    def update_display(self):
        if self.initial_scan_setup_plotting:
            self.fig.clf()
            self.ax = self.fig.add_subplot(111)
            self.plotline, = self.ax.plot([0,1], [0,0])
            self.ax.set_xlabel("Voltage (V)")
            self.ax.set_ylabel("Current (Amps)")
            self.ax.axvline(0, color='k')
            self.ax.axhline(0, color='k')
            self.initial_scan_setup_plotting = False
        self.plotline.set_data(self.Varray,self.Iarray)
        self.ax.relim()
        self.ax.autoscale_view(scalex=True, scaley=True)            
        self.fig.canvas.draw()
