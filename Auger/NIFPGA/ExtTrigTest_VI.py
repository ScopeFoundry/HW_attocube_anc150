"""Written by Frank Ogletree, Ed Barnard, and Alan Buckley"""

## Labview VI Functions 

try:
    from NI_FPGA_dll import NI_FPGA
except Exception as err:
    print("failed to load NI_FIGA_dll")
    
from ScopeFoundry import HardwareComponent, LoggedQuantity
#this logged quantity system is archaic, need updated ScopeFoundry framework.
import numpy as np
import ctypes
import os
from cffi import FFI


fpga_vi_header = """
static const char* const NiFpga_ExtTrigTest_Signature = "3D5E5AAA8CD7800FE1A30B9CBE652434";

typedef enum
{
   NiFpga_ExtTrigTest_IndicatorBool_FIFOOverflow = 0x810E,
} NiFpga_ExtTrigTest_IndicatorBool;

typedef enum
{
   NiFpga_ExtTrigTest_ControlBool_FIFOflag = 0x8112,
} NiFpga_ExtTrigTest_ControlBool;

typedef enum
{
   NiFpga_ExtTrigTest_TargetToHostFifoU64_CounterFIFO = 0,
} NiFpga_ExtTrigTest_TargetToHostFifoU64;
"""


class ExtTrigTest_FPGA_VI(object):        
    
    #bitfilename = r"C:\Users\NIuser\Documents\Programs LV\R Series\builds\Omicron_R_1\Omicron Auger\data\NiFpga_CountertoDAC.lvbitx"
    #bitfilename = os.path.join(os.path.dirname(__file__),"Auger FPGA R2/FPGA Bitfiles/NiFpga_CountertoDAC.lvbitx")
    bitfilename = r"C:\Users\NIuser\Documents\Programs LV\Frank FPGA test\FPGA Bitfiles\NiFpga_ExtTrigTest.lvbitx"
    signature = "3D5E5AAA8CD7800FE1A30B9CBE652434"
    resource = "RIO0"
    session = ctypes.c_uint32(0)
    

    
    
    def __init__(self, debug=False):
        self.debug = debug
        self.FPGA = NI_FPGA(self.bitfilename, self.signature, self.resource, debug) 
        
        self.ffi = FFI()
        self.ffi.cdef(fpga_vi_header)
        self.C = self.ffi.dlopen(None)
        

    def read_FIFOOverflow(self):
        print "CtrOverflow"
        indicator = self.C.NiFpga_ExtTrigTest_IndicatorBool_FIFOOverflow
        err, data = self.FPGA.Read_Bool(indicator)
        if self.debug: print  "Status:" + str(err)
        print 'ctroverflow', err, data
        if err == 0:
            if self.debug: print  "FIFOOverflow Read"
            return data
        else:
            raise IOError("FIFOOverflow err {}".format(err))
    


    def write_FifoFlag(self, _bool=False):
        indicator = self.C.NiFpga_ExtTrigTest_ControlBool_FIFOflag
        err = self.FPGA.Write_Bool(indicator, _bool)
        if self.debug: print  "Status:" + str(err)
        if err == 0:
            if self.debug: print  "FIFOflag Toggled", _bool

        

    
    # FIFO FLAG
    
    
###--------------End Counter to DAC controls and indicators------------------###

def test1():
    import time
    
    vi = ExtTrigTest_FPGA_VI(debug=True)
    fpga = vi.FPGA
    fpga.connect()
    fpga.reset()
    fpga.run()
    
    vi.write_FifoFlag(False)
    
    print(vi.read_FIFOOverflow())
    print(vi.read_FIFOOverflow())
    print(vi.read_FIFOOverflow())
    print(vi.read_FIFOOverflow())
    print(vi.read_FIFOOverflow())
    print(vi.read_FIFOOverflow())
    print(vi.read_FIFOOverflow())
    time.sleep(10.0)
    print(vi.read_FIFOOverflow())

    vi.write_FifoFlag(False)
    
    fpga.disconnect()    

def test2():
    import time
    from equipment.NI_Daq import NI_SyncTaskSet
    
    # set up sync io on X-board with a pixel trigger on PXI_Trig0
    sync_analog_io = NI_SyncTaskSet(out_chan  = "X-6368/ao0:1",
                                       in_chan   = "X-6368/ai0:1",
                                       ctr_chans = [],  #self.counter_channel_addresses.val.split(','),
                                       ctr_terms = [], #self.counter_channel_terminals.val.split(','),
                                       clock_source = "",
                                       trigger_output_term = "/X-6368/PXI_Trig0",
                                       )
    sync_analog_io.setup(rate_out = 0.5e6,
                        count_out = 100, 
                        rate_in = 0.5e6,
                        count_in = 100, 
                           #pad = ?,
                          is_finite=True)

    sync_analog_io.write_output_data_to_buffer(np.ones(200,dtype=float))

    # setup fpga and activate
     
    vi = ExtTrigTest_FPGA_VI(debug=True)
    fpga = vi.FPGA
    fpga.connect()
    fpga.reset()
    fpga.run()
     
    vi.write_FifoFlag(True)
     

    # start triggers
    sync_analog_io.start()
    
    time.sleep(2.0)
    
    print fpga.Read_Fifo(fifo=0, numberOfElements=50, timeout=1000)
    
    sync_analog_io.stop()
    
    vi.write_FifoFlag(False)
    
    fpga.disconnect()
    
if __name__ == '__main__':
    test2()