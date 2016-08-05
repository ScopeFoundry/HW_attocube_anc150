'''
Created on Jul 18, 2016

@author: NIuser
'''
from ScopeFoundry import HardwareComponent
try:
    from equipment.NI_Daq import Adc
except Exception as err:
    print "Cannot load NI_Daq Adc:", err
    
import time
import random

class SEMDualChanSignal(HardwareComponent):

    name = "sem_dualchan_signal"

    def setup(self):

        # Create logged quantities
        self.inLens_signal = self.add_logged_quantity(
                                name = 'inLens_signal', 
                                initial = 0,
                                dtype=float, fmt="%e", ro=True,
                                unit="V",
                                vmin=-100, vmax=100)
        self.signal_nsamples = self.add_logged_quantity(
                                name = 'signal_nsamples',
                                initial=1,
                                dtype=int, ro=False,
                                unit = "",
                                vmin = 1, vmax=10000)
        
        self.se2_signal = self.add_logged_quantity(
                                name = 'se2_signal', 
                                initial = 0,
                                dtype=float, fmt="%e", ro=True,
                                unit="V",
                                vmin=-100, vmax=100)


        self.dummy_mode = self.add_logged_quantity(name='dummy_mode', dtype=bool, initial=False, ro=False)
        
    def connect(self):
        if self.debug_mode.val: print "Connecting to NI_Dac Adc"
        
        # Open connection to hardware

        if not self.dummy_mode.val:
            # Normal APD:  "/Dev1/PFI0"
            # APD on monochromator: "/Dev1/PFI2"
            self.adc_InLens = Adc('X-6368/ai1')
            self.adc_SE2 = Adc('X-6368/ai0')
        else:
            if self.debug_mode.val: print "Connecting to NI_Dac Adc (Dummy Mode)"

        # connect logged quantities
        self.inLens_signal.hardware_read_func = self.read_inlens_signal
        self.se2_signal.hardware_read_func = self.read_se2_signal


    def disconnect(self):
        #disconnect hardware
        self.adc_InLens.close()
        self.adc_SE2.close()
        
        #disconnect logged quantities from hardware
        for lq in self.settings.as_dict().values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        
        # clean up hardware object
        del self.adc
        
    def read_inlens_signal(self):        
        #Sofia: return tuple
        if not self.dummy_mode.val:
                x = 0.0
                for i in range(self.signal_nsamples.val):  
                    x += self.adc_InLens.get()
                return x / self.signal_nsamples.val
        else:
            time.sleep(self.inLens_signal_nsamples.val * 20e-6)
            signal = random.random()
            if self.debug_mode.val: print self.name, "dummy read_count_rate", signal
            return signal
        
    def read_se2_signal(self):        
        #Sofia: return tuple
        if not self.dummy_mode.val:
                y = 0.0
                for i in range(self.signal_nsamples.val):
                    y += self.adc_SE2.get()
                return  y /self.signal_nsamples.val
        else:
            time.sleep(self.signal_nsamples.val * 20e-6)
            signal = random.random()
            if self.debug_mode.val: print self.name, "dummy read_count_rate", signal
            return signal
