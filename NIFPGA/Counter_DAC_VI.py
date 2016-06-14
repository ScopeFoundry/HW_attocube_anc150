## Labview VI Functions 
from Alpha import NI_FPGA
import ctypes


class Counter_DAC(NI_FPGA):        
    
    bitfilename = r"C:\Users\NIuser\Documents\Programs LV\R Series\builds\Omicron_R_1\Omicron Auger\data\NiFpga_CountertoDAC.lvbitx"
    signature = "146CFF8F04265BED0C2F87F8C0A0672A"
    resource = "RIO0"
    session = ctypes.c_uint32(0)
    
    def __init__(self):
        NI_FPGA.__init__(self, Counter_DAC.bitfilename, Counter_DAC.signature, Counter_DAC.resource)

    FPGA = NI_FPGA(bitfilename, signature, resource) 
    #Scoping issue solved by taking this definition (FPGA shown above) out of init header. Yuss! :poop: :D 11/22/15
    
    def CtrElapsed(self):
        self.indicator = 0x8124
        err, value = self.FPGA.Read_U32(self.indicator)
        if err == 0:
            print "CtrElapsed Read:", value
        else:
            print "Status:" + str(err)

    def CtrTransfer(self):
        self.indicator = 0x8128
        err, value = self.FPGA.Read_U32(self.indicator)
        if err == 0:
            print "CtrTransfer Read:", value
        else:
            print "Status:" + str(err)

    def CtrOverflow(self):
        self.indicator = 0x812E
        err = self.FPGA.Read_Bool(self.indicator)
        print "Status:" + str(err)
        if err == 0:
            print "CtrOverflow Read"
    

    def Read_DAC1(self):
        self.indicator = 0x814A
        err, value = self.FPGA.Read_I16(self.indicator)     
        if err == 0:
            print "DAC1 Read:", value
        else:
            print "DAC1 Error:" + str(err)
            

        
    def Read_DAC2(self):
        self.indicator = 0x8146
        err, value = self.FPGA.Read_I16(self.indicator)
        if err == 0:
            print "DAC2 Read:", value
        else:
            print "DAC2 Error:" + str(err)

            #Current error 63195, invalid session.

    def Loop_Elapsed(self):
        self.indicator = 0x8142
        err, value = self.FPGA.Read_U16(self.indicator)
        if err == 0:
            print "Loop Elapsed:", value
        else:
            print "Loop Elapsed Error:" + str(err)


    def CtrFIFO(self, _bool="0"):
        self.control= ctypes.c_uint32(0x8132)
        self.value = ctypes.c_char(_bool)
        #
        err, value = self.FPGA.Write_Bool(self.control)        ###Update definitions in subordinate NI_FPGA python file###   
        #err = self.handle_err(fpga_dll.NiFpgaDll_WriteBool(self.session, self.control, self.value))
        print "Status:" + str(err)
        if err == 0:
            print "CtrFIFO Toggled"


    def Offset1(self, _Offset=0):
        self.control= ctypes.c_uint32(0x811E)
        self.value = ctypes.c_int16(_Offset)
        err = self.FPGA.Write_I16(self.control, self.value)
        print "Status:" + str(err)
        if err == 0:
            print "Offset1 Set"

    def Offset2(self, _Offset=0):
        self.control= ctypes.c_uint32(0x811A)
        self.value = ctypes.c_int16(_Offset)
        err = self.FPGA.Write_I16(self.control, self.value)
        print "Status:" + str(err)
        if err == 0:
            print "Offset2 Set"

    def Scale1(self, _scale=0):
        self.control= ctypes.c_uint32(0x8116)
        self.value = ctypes.c_int16(_scale)
        err = self.FPGA.Write_I16(self.control, self.value)
        print "Status:" + str(err)
        if err == 0:
            print "Scale1 Set"

    def Scale2(self, _scale=0):
        self.control= ctypes.c_uint32(0x8112)
        self.value = ctypes.c_int16(_scale)
        err = self.FPGA.Write_I16(self.control, self.value)
        print "Status:" + str(err)
        if err == 0:
            print "Scale1 Set"

    def Counter_ticks(self, _counterticks=40000):
        self.control= ctypes.c_uint32(0x8120)
        self.value = ctypes.c_uint32(_counterticks)
        err = self.FPGA.Write_U32(self.control, self.value)
        print "Status:" + str(err)
        if err == 0:
            print "Counter Ticks Set"


    def Rate(self, _rate=400):
        self.control= ctypes.c_uint32(0x810C)
        self.value = ctypes.c_uint32(_rate)
        err = self.FPGA.Write_U32(self.control, self.value)
        print "Status:" + str(err)
        if err == 0:
            print "Rate Set"


    def DIO811_Read(self):
        self.size = 4
        err, array = self.FPGA.Read_ArrayBool(0x813A, self.size)
        if err == 0:
            print "DIO811 Read:", array
        else:
            print "DIO811 Status:" + str(err)

## Lists cumulative counter hit number as a row of 8 integer vales, 
### each entry represents the counter value on each of 8 channels.
    def Counts(self):
        self.size = 8
        err, array = self.FPGA.Read_ArrayU32(0x813C, self.size)
        if err == 0:
            print "Counts Read:", array
        else:
            print "Counts Status:" + str(err)


## The following functions allow you to write a single row numpy array of boolean values to the counter to dac fpga vi
## If no errors arise, the function prints the input array for your verification.
    def DAC1_add(self, bool_array):
        self.array = bool_array
        self.indicator= ctypes.c_uint32(0x815A)
        self.size = 8
        err = self.FPGA.Write_ArrayBool(self.indicator, self.array, self.size)
        print "Status:" + str(err)
        if err == 0:
            print "\"DAC1 add\" array successfully written:", self.array

    def DAC1_sub(self, bool_array):
        self.array = bool_array
        self.indicator= ctypes.c_uint32(0x8156)
        self.size = 8
        err = self.FPGA.Write_ArrayBool(self.indicator, self.array, self.size)
        print "Status:" + str(err)
        if err == 0:
            print "\"DAC1 sub\" array successfully written:", self.array
            
    def DAC2_add(self, bool_array):
        self.array = bool_array
        self.indicator= ctypes.c_uint32(0x8152)
        self.size = 8
        err = self.FPGA.Write_ArrayBool(self.indicator, self.array, self.size)
        print "Status:" + str(err)
        if err == 0:
            print "\"DAC2 add\" array successfully written:", self.array

    def DAC2_sub(self, bool_array):
        self.array = bool_array
        self.indicator= ctypes.c_uint32(0x814E)
        self.size = 8
        err = self.FPGA.Write_ArrayBool(self.indicator, self.array, self.size)
        print "Status:" + str(err)
        if err == 0:
            print "\"DAC2 sub\" array successfully written:", self.array

    def DIO1215_Write(self, bool_array):
        self.array = bool_array
        self.indicator= ctypes.c_uint32(0x8136)
        self.size = 4
        err = self.FPGA.Write_ArrayBool(self.indicator, self.array, self.size)
        print "Status:" + str(err)
        if err == 0:
            print "\"DIO1215 Write\" array successfully written:", self.array
###--------------End Counter to DAC controls and indicators------------------###


if __name__ == '__main__':
    vi = Counter_DAC()
    fpga = Counter_DAC.FPGA
    fpga.connect()
    fpga.reset()
    fpga.run()
    vi.CtrElapsed()
    vi.Read_DAC1()
    vi.Read_DAC2()
    fpga.disconnect()