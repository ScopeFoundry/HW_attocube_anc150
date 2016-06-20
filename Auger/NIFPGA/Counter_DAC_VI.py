## Labview VI Functions 
from NI_FPGA_dll import NI_FPGA
import ctypes
import os

class Counter_DAC(object):        
    
    #bitfilename = r"C:\Users\NIuser\Documents\Programs LV\R Series\builds\Omicron_R_1\Omicron Auger\data\NiFpga_CountertoDAC.lvbitx"
    bitfilename = os.path.join(os.path.dirname(__file__),"OmicronR1_FPGATarget_CountertoDAC_DtX8ivVB-f4.lvbitx")
    signature = "146CFF8F04265BED0C2F87F8C0A0672A"
    resource = "RIO0"
    session = ctypes.c_uint32(0)
    
    def __init__(self, debug=False):
        self.debug = debug
        self.FPGA = NI_FPGA(self.bitfilename, self.signature, self.resource, debug) 
    
    def CtrElapsed(self):
        self.indicator = 0x8124
        err, value = self.FPGA.Read_U32(self.indicator)
        if err == 0:
            if self.debug: print  "CtrElapsed Read:", value
        else:
            if self.debug: print  "Status:" + str(err)

    def CtrTransfer(self):
        self.indicator = 0x8128
        err, value = self.FPGA.Read_U32(self.indicator)
        if err == 0:
            if self.debug: print  "CtrTransfer Read:", value
        else:
            if self.debug: print  "Status:" + str(err)

    def CtrOverflow(self):
        self.indicator = 0x812E
        err = self.FPGA.Read_Bool(self.indicator)
        if self.debug: print  "Status:" + str(err)
        if err == 0:
            if self.debug: print  "CtrOverflow Read"
    

    def Read_DAC1(self):
        self.indicator = 0x814A
        err, value = self.FPGA.Read_I16(self.indicator)     
        if err == 0:
            if self.debug: print  "DAC1 Read:", value
        else:
            if self.debug: print  "DAC1 Error:" + str(err)
        return value
            

        
    def Read_DAC2(self):
        self.indicator = 0x8146
        err, value = self.FPGA.Read_I16(self.indicator)
        if err == 0:
            if self.debug: print  "DAC2 Read:", value
        else:
            if self.debug: print  "DAC2 Error:" + str(err)
            #Current error 63195, invalid session.
        return value
    
    def Loop_Elapsed(self):
        self.indicator = 0x8142
        err, value = self.FPGA.Read_U16(self.indicator)
        if err == 0:
            if self.debug: print  "Loop Elapsed:", value
        else:
            if self.debug: print  "Loop Elapsed Error:" + str(err)


    def CtrFIFO(self, _bool=False):
        indicator = ctypes.c_uint32(0x8132)
        #
        err = self.FPGA.Write_Bool(indicator, _bool)        ###Update definitions in subordinate NI_FPGA python file###   
        #err = self.handle_err(fpga_dll.NiFpgaDll_WriteBool(self.session, self.control, self.value))
        if self.debug: print  "Status:" + str(err)
        if err == 0:
            if self.debug: print  "CtrFIFO Toggled"


    def Offset1(self, _Offset=0):
        self.control= ctypes.c_uint32(0x811E)
        self.value = ctypes.c_int16(_Offset)
        err = self.FPGA.Write_I16(self.control, self.value)
        if self.debug: print  "Status:" + str(err)
        if err == 0:
            if self.debug: print  "Offset1 Set"

    def Offset2(self, _Offset=0):
        self.control= ctypes.c_uint32(0x811A)
        self.value = ctypes.c_int16(_Offset)
        err = self.FPGA.Write_I16(self.control, self.value)
        if self.debug: print  "Status:" + str(err)
        if err == 0:
            if self.debug: print  "Offset2 Set"

    def Scale1(self, _scale=0):
        self.control= ctypes.c_uint32(0x8116)
        self.value = ctypes.c_int16(_scale)
        err = self.FPGA.Write_I16(self.control, self.value)
        if self.debug: print  "Status:" + str(err)
        if err == 0:
            if self.debug: print  "Scale1 Set"

    def Scale2(self, _scale=0):
        self.control= ctypes.c_uint32(0x8112)
        self.value = ctypes.c_int16(_scale)
        err = self.FPGA.Write_I16(self.control, self.value)
        if self.debug: print  "Status:" + str(err)
        if err == 0:
            if self.debug: print  "Scale1 Set"

    def Counter_ticks(self, _counterticks=40000):
        self.control= ctypes.c_uint32(0x8120)
        self.value = ctypes.c_uint32(_counterticks)
        err = self.FPGA.Write_U32(self.control, self.value)
        if self.debug: print  "Status:" + str(err)
        if err == 0:
            if self.debug: print  "Counter Ticks Set"


    def Rate(self, _rate=400):
        self.control= ctypes.c_uint32(0x810C)
        self.value = ctypes.c_uint32(_rate)
        err = self.FPGA.Write_U32(self.control, self.value)
        if self.debug: print  "Status:" + str(err)
        if err == 0:
            if self.debug: print  "Rate Set"


    def DIO811_Read(self):
        self.size = 4
        err, array = self.FPGA.Read_ArrayBool(0x813A, self.size)
        if err == 0:
            if self.debug: print  "DIO811 Read:", array
        else:
            if self.debug: print  "DIO811 Status:" + str(err)

## Lists cumulative counter hit number as a row of 8 integer vales, 
### each entry represents the counter value on each of 8 channels.
    def Counts(self):
        self.size = 8
        err, array = self.FPGA.Read_ArrayU32(0x813C, self.size)
        if err == 0:
            if self.debug: print  "Counts Read:", array
        else:
            if self.debug: print  "Counts Status:" + str(err)


## The following functions allow you to write a single row numpy array of boolean values to the counter to dac fpga vi
## If no errors arise, the function if self.debug: print s the input array for your verification.
    def DAC1_add(self, bool_array):
        self.array = bool_array
        self.indicator= ctypes.c_uint32(0x815A)
        self.size = 8
        err = self.FPGA.Write_ArrayBool(self.indicator, self.array, self.size)
        if self.debug: print  "Status:" + str(err)
        if err == 0:
            if self.debug: print  "\"DAC1 add\" array successfully written:", self.array

    def DAC1_sub(self, bool_array):
        self.array = bool_array
        self.indicator= ctypes.c_uint32(0x8156)
        self.size = 8
        err = self.FPGA.Write_ArrayBool(self.indicator, self.array, self.size)
        if self.debug: print  "Status:" + str(err)
        if err == 0:
            if self.debug: print  "\"DAC1 sub\" array successfully written:", self.array
            
    def DAC2_add(self, bool_array):
        self.array = bool_array
        self.indicator= ctypes.c_uint32(0x8152)
        self.size = 8
        err = self.FPGA.Write_ArrayBool(self.indicator, self.array, self.size)
        if self.debug: print  "Status:" + str(err)
        if err == 0:
            if self.debug: print  "\"DAC2 add\" array successfully written:", self.array

    def DAC2_sub(self, bool_array):
        self.array = bool_array
        self.indicator= ctypes.c_uint32(0x814E)
        self.size = 8
        err = self.FPGA.Write_ArrayBool(self.indicator, self.array, self.size)
        if self.debug: print  "Status:" + str(err)
        if err == 0:
            if self.debug: print  "\"DAC2 sub\" array successfully written:", self.array

    def DIO1215_Write(self, bool_array):
        self.array = bool_array
        self.indicator= ctypes.c_uint32(0x8136)
        self.size = 4
        err = self.FPGA.Write_ArrayBool(self.indicator, self.array, self.size)
        if self.debug: print  "Status:" + str(err)
        if err == 0:
            if self.debug: print  "\"DIO1215 Write\" array successfully written:", self.array
###--------------End Counter to DAC controls and indicators------------------###


def test1():
    vi = Counter_DAC(debug=True)
    fpga = vi.FPGA
    fpga.connect()
    fpga.reset()
    fpga.run()
    vi.CtrElapsed()
    vi.Read_DAC1()
    vi.Read_DAC2()
    fpga.disconnect()    

def test2():
    import time
    "plot DAC1, DAC2"
    vi = Counter_DAC(debug=True)
    fpga = vi.FPGA
    fpga.connect()
    fpga.reset()
    fpga.run()
    
    try:
        dac0_data = []
        dac1_data = []
        time_data = []
        
        def update_fig(ax):
            
            time_data.append(time.time())
            vi.CtrElapsed()
            dac0_data.append(vi.Read_DAC1())
            dac1_data.append(vi.Read_DAC2())
            dac0_plotline.set_data(time_data, dac0_data)        
            dac1_plotline.set_data(time_data, dac1_data)
            ax.autoscale_view(True,True,True)
            ax.set_xlim(time_data[0], time_data[-1])
            ax.set_ylim(0, max(dac0_data))
            ax.figure.canvas.draw()     
        
        import matplotlib.pyplot as plt
        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        
        dac0_plotline, = ax.plot([0],[0])
        dac1_plotline, = ax.plot([0],[0])
        
        timer = fig.canvas.new_timer(interval=100)
        
        timer.add_callback(update_fig, ax)
        timer.start()
        
        plt.show()
    finally:
        fpga.disconnect()
        
def test3():
    "FIFO Test"
    import matplotlib.pyplot as plt
    
    vi = Counter_DAC(debug=True)
    fpga = vi.FPGA
    try:
        fpga.connect()
        fpga.reset()
        fpga.run()
        
        vi.CtrFIFO(True)
        fpga.Start_Fifo()
        
        buf =fpga.Read_Fifo(numberOfElements=10000)
        for i in range(8):
            plt.subplot(8,1,i+1)
            plt.plot(buf[i::8])
        
        fpga.Stop_Fifo()
        
        plt.show()
        
    finally:
        fpga.disconnect()
        
def test4():
    "FIFO Test live"
    import matplotlib.pyplot as plt
    import numpy  as np
    
    vi = Counter_DAC(debug=True)
    fpga = vi.FPGA
    try:
        fpga.connect()
        fpga.reset()
        fpga.run()
        
        vi.Counter_ticks(40000)
        fpga.Start_Fifo()
        vi.CtrFIFO(True)
        
        N_elements = 500*8

        x_array  = np.arange(N_elements)

        fig = plt.figure()
        
        chan_plotlines = []
        for i in range(8):
            ax = fig.add_subplot(8,1,i+1)
            chan_plotlines.append(ax.plot(x_array, x_array)[0])
        
        def update_fig(ax):
            print "update fig"
            
            remaining, buf = fpga.Read_Fifo(numberOfElements=0)
            #buf =fpga.Read_Fifo(numberOfElements=N_elements)
            remaining, buf = fpga.Read_Fifo(numberOfElements=remaining)
            #fpga.ReleaseFifoElements(N_elements)
            print "done with data acq"
            for i in range(8):
                chan_data =buf[i::8]
                chan_plotlines[i].set_data(x_array[:len(chan_data)], chan_data)
                chan_plotlines[i].axes.set_ylim(0,np.max(buf))
                
            ax.autoscale_view(True,True,True)
            ax.figure.canvas.draw()     
            
        timer = fig.canvas.new_timer(interval=10)
        timer.add_callback(update_fig, ax)
        timer.start()
        
        
        plt.show()
        

        
    finally:
        print "finally"
        fpga.Stop_Fifo()
        fpga.disconnect()




if __name__ == '__main__':
    test4()