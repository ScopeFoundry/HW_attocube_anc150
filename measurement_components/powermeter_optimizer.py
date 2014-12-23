'''
Created on Nov 9, 2014

@author: lab
'''

from .measurement import Measurement 
import numpy as np
import time

class PowerMeterOptimizerMeasurement(Measurement):

    name = "powermeter_optimizer"

    def setup(self):        
        self.display_update_period = 0.1 #seconds

        self.OPTIMIZE_HISTORY_LEN = 500

        self.optimize_history = np.zeros(self.OPTIMIZE_HISTORY_LEN, dtype=np.float)        
        self.optimize_ii = 0

        #connect events
        self.gui.ui.power_meter_acquire_cont_checkBox.stateChanged.connect(self.start_stop)
        #self.measurement_state_changed[bool].connect(self.gui.ui.apd_optimize_timer_checkBox.setChecked)
        self.measurement_state_changed[bool].connect(self.gui.ui.power_meter_acquire_cont_checkBox.setChecked)
        
        
        
    def setup_figure(self):
        # APD Optimize Figure ########################
        self.fig_opt = self.gui.add_figure('opt', self.gui.ui.plot_optimize_widget)
        self.ax_opt = self.fig_opt.add_subplot(111)
        
        self.optimize_ii = 0
        self.optimize_line, = self.ax_opt.plot(self.optimize_history)
        self.optimize_current_pos = self.ax_opt.axvline(self.optimize_ii, color='r')


    def _run(self):
        #self.apd_counter_hc = self.gui.apd_counter_hc
        #self.apd_count_rate = self.apd_counter_hc.apd_count_rate
        self.pm_analog_readout_hc = self.gui.thorlabs_powermeter_analog_readout_hc


        while not self.interrupt_measurement_called:
            self.optimize_ii += 1
            self.optimize_ii %= self.OPTIMIZE_HISTORY_LEN
            
            self.optimize_history[self.optimize_ii] = self.pm_analog_readout_hc.voltage.read_from_hardware()
            time.sleep(0.05)
    
    def update_display(self):        
        ii = self.optimize_ii
        #print "display update", ii, self.optimize_history[ii]

        self.optimize_line.set_ydata(self.optimize_history)
        self.optimize_current_pos.set_xdata((ii,ii))
        if (ii % 2) == 0:
            self.ax_opt.relim()
            self.ax_opt.autoscale_view(scalex=False, scaley=True)

        self.fig_opt.canvas.draw()