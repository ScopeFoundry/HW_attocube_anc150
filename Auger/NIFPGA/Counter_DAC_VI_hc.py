from ScopeFoundry import HardwareComponent
from Auger.NIFPGA.Counter_DAC_VI_R2 import Counter_DAC_FPGA_VI
import time

class Counter_DAC_FPGA_VI_HC(HardwareComponent):
    
    name = 'Counter_DAC_FPGA_VI_HC'
    
    NUM_CHANS = 9
    
    
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
        self.ext_trig_enable = self.add_logged_quantity(name='ext_trig_enable', dtype=bool, ro=False, initial=False ) 


    def connect(self):
        self.counter_dac = Counter_DAC_FPGA_VI(debug=self.settings['debug_mode'])
        self.fpga = self.counter_dac.FPGA
        self.fpga.connect()
        self.fpga.reset()
        self.fpga.run()       
        
        
        self.ctr_fifo.hardware_set_func = self.counter_dac.CtrFIFO
        self.counter_ticks.hardware_set_func = self.counter_dac.Counter_ticks
        self.ext_trig_enable.hardware_set_func = self.counter_dac.write_ExtTrigEnable
        
        #fpga.Start_Fifo(0)
        
    
    def disconnect(self):
        self.fpga.Stop_Fifo(0)
        self.fpga.disconnect()
        
        
        # disconnect hardware lq's
        # TODO
        
        del self.counter_dac, self.fpga


    def flush_FIFO(self):
        remaining, buf = self.fpga.Read_Fifo(numberOfElements=0)
        remaining, buf = self.fpga.Read_Fifo(numberOfElements=remaining)
        if self.settings['debug_mode']: print("flush", remaining, len(buf))
        return remaining, buf

    def read_FIFO(self,reshape=True,return_read_elements=False):           
        #Let the buffer run once to allow for system warm up(?)
        remaining, buf = self.fpga.Read_Fifo(numberOfElements=0)
        read_elements = (remaining - (remaining % self.NUM_CHANS))
        remaining, buf = self.fpga.Read_Fifo(numberOfElements=read_elements)

        #depth = (len(buf))/8
        buf_reshaped = buf.reshape((self.NUM_CHANS,-1), order='F')
   
        if reshape:
            out = buf_reshaped
        else:
            out = buf
        
        if return_read_elements:
            return out, read_elements
        else:
            return out
        
        if self.settings['debug_mode']: print('->', buf.shape, len(buf)/self.NUM_CHANS)
        #if self.settings['debug_mode']: print('-->',  buf.reshape(-1,).shape, buf.reshape(-1,8).mean(axis=0) ) #,  buf.reshape(-1,8))
    
    def engage_FIFO(self):
        
        self.fpga.Stop_Fifo(0)
        self.flush_FIFO()
        self.fpga.Start_Fifo(0)
        #self.counter_dac.CtrFIFO(True)
        self.settings['ctr_fifo'] = True
        #self.counter_dac_hc.CtrFIFO(True)
        #self.flush_FIFO()
        
        #time.sleep(0.2)
        
        #self.flush_FIFO()
        
    
    def disengage_FIFO(self):
        self.fpga.Stop_Fifo(0)
        remaining, buf = self.fpga.Read_Fifo(numberOfElements=0)
        self.settings['ctr_fifo'] = False
        if self.settings['debug_mode']: print("left in buffer after scan", remaining)
        