from ScopeFoundry import HardwareComponent
from Auger.NIFPGA.Counter_DAC_VI import Counter_DAC_FPGA_VI


class Counter_DAC_FPGA_VI_HC(HardwareComponent):
    
    name = 'Counter_DAC_FPGA_VI_HC'
    
    
    def setup(self):
        
        # Settings
        self.ctr_fifo = self.add_logged_quantity(name="ctr_fifo", dtype=bool, initial=False, ro=False)
        #self.offset1 = self.add_logged_quantity(name="offset1", dtype=float, initial=0, fmt="%.2f", ro=False)
        #self.offset2 = self.add_logged_quantity(name="offset2", dtype=float, initial=0, fmt="%.2f", ro=False)
        #self.scale1 = self.add_logged_quantity(name="scale1", dtype=float, initial=100, fmt="%.2f", ro=False)
        #self.scale2 = self.add_logged_quantity(name="scale2", dtype=float, initial=100, fmt="%.2f", ro=False)
        #self.tick_rate = self.add_logged_quantity(name="tick_rate", dtype=float, initial=400, fmt="%.2f", ro=False)
        self.counter_ticks = self.add_logged_quantity(name="counter_ticks", dtype=int, initial=40000, ro=False)
        #self.ctr_elapsed = self.add_logged_quantity(name="ctr_elapsed", dtype=float, initial=0, fmt="%.2f", ro=True)
        #self.ctr_transfer = self.add_logged_quantity(name="ctr_transfer", dtype=float, initial=0, fmt="%.2f", ro=True)
        #self.ctr_overflow = self.add_logged_quantity(name="ctr_overflow", dtype=bool, initial=False, fmt="%.2f", ro=True)
        #self.dac1_readout = self.add_logged_quantity(name="dac1_readout", dtype=float, initial=0, fmt="%.2f", ro=True)
        #self.dac2_readout = self.add_logged_quantity(name="dac2_readout", dtype=float, initial=0, fmt="%.2f", ro=True)


    def connect(self):
        self.counter_dac = Counter_DAC_FPGA_VI(debug=self.settings['debug_mode'])
        self.fpga = self.counter_dac.FPGA
        self.fpga.connect()
        self.fpga.reset()
        self.fpga.run()       
        
        
        self.ctr_fifo.hardware_set_func = self.counter_dac.CtrFIFO
        self.counter_ticks.hardware_set_func = self.counter_dac.Counter_ticks
        
        #fpga.Start_Fifo(0)
        
    
    def disconnect(self):
        self.fpga.Stop_Fifo(0)
        self.fpga.disconnect()
        
        
        # disconnect hardware lq's
        # TODO
        
        del self.counter_dac, self.fpga