'''
Created on Nov 23, 2015

@author: lab
'''

from .measurement import Measurement 
import time
import numpy as np


class HiPMicroscopeDualTemperature(Measurement):
    name = 'hip_dual_temperature'
    ui_filename = 'measurement_components/hip_dual_temperature.ui'
    
    def setup(self):
        #logged quantities
        
        #GUI events
        #pid1 = self.gui.omega_pt_pid
        pid1 = self.gui.hardware_components['omega_pt_pid_controller']
        pid1.temp.connect_bidir_to_widget(self.ui.omega1_PV_doubleSpinBox)
        pid1.setpoint1.connect_bidir_to_widget(self.ui.omega1_SV_doubleSpinBox)
        pid1.run_mode.connect_bidir_to_widget(self.ui.omega1_run_mode_label)
        self.ui.omega1_run_pushButton.clicked.connect(pid1.run_mode_run)
        self.ui.omega1_stop_pushButton.clicked.connect(pid1.run_mode_stop)

    
    def _run(self):
        pid1 = self.gui.hardware_components['omega_pt_pid_controller']
        
        while not self.interrupt_measurement_called:
            pid1.read_from_hardware()
            time.sleep(0.1)


    def setup_figure(self):
        pass

    def update_display(self):
        pass
