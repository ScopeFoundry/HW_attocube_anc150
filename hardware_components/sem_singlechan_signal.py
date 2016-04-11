from ScopeFoundry import HardwareComponent
try:
    from equipment.NI_Daq import Adc
except Exception as err:
    print "Cannot load NI_Daq Adc:", err
    
import time
import random

class SEMSingleChanSignal(HardwareComponent):

    name = "sem_singlechan_signal"

    def setup(self):

        # Create logged quantities
        self.sem_signal = self.add_logged_quantity(
                                name = 'sem_signal', 
                                initial = 0,
                                dtype=float, fmt="%e", ro=True,
                                unit="V",
                                vmin=-100, vmax=100)
        self.sem_signal_nsamples = self.add_logged_quantity(
                                name = 'sem_signal_nsamples',
                                initial=1,
                                dtype=int, ro=False,
                                unit = "",
                                vmin = 1, vmax=10000)

        self.dummy_mode = self.add_logged_quantity(name='dummy_mode', dtype=bool, initial=False, ro=False)
        
    def connect(self):
        if self.debug_mode.val: print "Connecting to NI_Dac Adc"
        
        # Open connection to hardware

        if not self.dummy_mode.val:
            # Normal APD:  "/Dev1/PFI0"
            # APD on monochromator: "/Dev1/PFI2"
            self.adc = Adc('X-6368/ai1')
        else:
            if self.debug_mode.val: print "Connecting to NI_Dac Adc (Dummy Mode)"

        # connect logged quantities
        self.sem_signal.hardware_read_func = self.read_signal


    def disconnect(self):
        #disconnect hardware
        self.adc.close()
        
        #disconnect logged quantities from hardware
        for lq in self.logged_quantities.values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        
        # clean up hardware object
        del self.adc
        
    def read_signal(self):
        if not self.dummy_mode.val:
            x = 0.0
            for i in range(self.sem_signal_nsamples.val):
                x += self.adc.get()
            return x / self.sem_signal_nsamples.val
        else:
            time.sleep(self.sem_signal_nsamples.val * 20e-6)
            signal = random.random()
            if self.debug_mode.val: print self.name, "dummy read_count_rate", signal
            return signal
