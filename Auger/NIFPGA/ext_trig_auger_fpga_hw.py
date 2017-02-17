from ScopeFoundry import HardwareComponent
from Auger.NIFPGA.ext_trig_auger_fpga import ExtTrigAugerFPGA

class ExtTrigAugerFPGA_HW(HardwareComponent):
    
    name = 'ext_trig_auger_fpga'
    
    def setup(self):
        
        self.settings.New('trigger_mode', dtype=str, initial='off', choices=('off', 'pxi', 'dio'))
        self.settings.New('overflow', dtype=bool, ro=True)

    def connect(self):
        
        self.ext_trig_dev = ExtTrigAugerFPGA(debug=self.settings['debug_mode'])
        
        self.fpga = self.ext_trig_counter.FPGA
        
        self.fpga.load_bitfile()
        self.fpga.reset()
        self.fpga.run()
        
        self.settings.trigger_mode.connect_to_hardware(
            write_func=self.ext_trig_dev.write_triggerMode
            )
        
        self.settings.overflow.connect_to_hardware(
            read_func=self.ext_trig_dev.read_overflow
            )
        
        self.ext_trig_dev.write_triggerMode(self.settings['trigger_mode'])
        self.read_from_hardware()
        
    def disconnect(self):
        

        if hasattr(self, 'fpga'):
            self.ext_trig_dev.write_triggerMode('off')
            self.ext_trig_dev.flush_fifo()
            self.fpga.close()
            del self.ext_trig_dev

    
    def read_fifo(self, n_transfers=-1):
        """
        if n_transfers < 0: read all available transfer blocks 
        defaults to read all
        """
        if n_transfers < 0:
            n_transfers = self.ext_trig_dev.read_num_transfers_in_fifo()
            
        return self.ext_trig_dev.read_fifo_parse(n_transfers, timeout=0)
    