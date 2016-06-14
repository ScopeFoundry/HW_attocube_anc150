import ctypes
#import time
from ctypes import windll
import csv
import numpy as np
from collections import OrderedDict


fpga_dll = windll.LoadLibrary('NIFpga.dll')
#test_array = np.array([1,0,1,1,1,0,0,0])
#test_array2 = np.array([1,0,0,0,0,0,0,1])
#size_4  = np.array([1,0,1,0])
#bitfilename = r"C:\Users\NIuser\Documents\Programs LV\R Series\builds\Omicron_R_1\Omicron Auger\data\NiFpga_CountertoDAC.lvbitx"
#signature = "146CFF8F04265BED0C2F87F8C0A0672A"
#resource = "RIO0"
###--------------End Basic Command Section----------------###

class NI_FPGA(object):        
    def __init__(self, bitfilename, signature, resource="RIO0"):
        self.session = ctypes.c_uint32(0)
        self.bitfilename = bitfilename
        self.signature = signature
        self.resource = resource
        self.fifo = ctypes.c_uint32(0)
        # NOTE: CounterFifo declared in last lines of
        #NiFpga_CountertoDAC.h as I32 datatype with value of 0
        #However, self.fifo argument warrants use of U32 type   (:c) <-- Disappointment.
        self.test_array = np.array([1,0,1,1,1,0,0,0])
        self.test_array2 = np.array([1,0,0,0,0,0,0,1])
        # Load error code information from csv file derived from header file
        self.err_code_list = []
        with open('nifpga_errorcodes_14.csv') as err_file:
            csv_read = csv.reader(err_file, quotechar='"') #np.array([])
            for row in csv_read:
                self.err_code_list.append(row)
                # np.concatenate((array1, row), axis=0)
            #result = np.reshape(array1,(49,3))
            #print(self.err_code_list)
        self.err_code_list = self.err_code_list[1:]
        self.err_bynum = OrderedDict()
        for code, name, description in self.err_code_list:
            num = int(code.replace('_','-'))
            self.err_bynum[num] = name + ": " + description 
            
            
    def handle_err(self, err_code):
        if err_code != 0:
            #print "Error {}. Consult FPGA Interface C API > API Reference > Errors using provided status code for more details ".format(err_code)
            #print "Error {}: {}".format(err_code, self.err_bynum[err_code])
            raise IOError("NI_FPGA Error {}: {}".format(err_code, self.err_bynum[err_code]))
        return err_code
    
    def connect(self):
        NiFpga_OpenAttribute_NoRun = 1 # from Nifpga.h
        attribute = NiFpga_OpenAttribute_NoRun
        session=self.session
        err = self.handle_err(fpga_dll.NiFpgaDll_Open(self.bitfilename, self.signature, self.resource, attribute, ctypes.byref(session)))
        print "Connection Status:" + str(err), self.session
        if err == 0:
            print "Connected, FPGA configured to automatically run."
            
    def unload(self):
        err = self.handle_err(fpga_dll.NiFpgaDll_Finalize())
        print "Unload Status:" + str(err), self.session
        if err == 0:
            print "FPGA Library unloaded (caveat: not thread safe)."
            
    def disconnect(self):
        err = self.handle_err(fpga_dll.NiFpgaDll_Close(self.session, 0))
        print "Disconnect Status:" + str(err)
        if err == 0:
            print "FPGA session disconnected (closed)."
        
    def run(self):
        self.attribute = 0
        err = self.handle_err(fpga_dll.NiFpgaDll_Run(self.session, self.attribute))
        print "Status:" + str(err)
        if err == 0:
            print "Running FPGA VI on target."
    #Runs the FPGA VI on the target. If you use 
    #NiFpga_RunAttribute_WaitUntilDone, 
    #NiFpga_Run blocks the thread until the FPGA finishes running.
    
    def abort(self):
        err = self.handle_err(fpga_dll.NiFpgaDll_Abort(self.session))
        print "Status:" + str(err)
        if err == 0:
            print "FPGA VI successfully aborted."
    #Aborts the FPGA VI.
    
    
    def reset(self):
        err = fpga_dll.NiFpgaDll_Reset(self.session)
        print "Status:" + str(err)
        if err == 0:
            print "FPGA VI successfully reset."
    #Resets the FPGA VI.
    
    
    def download(self):
            err = self.handle_err(fpga_dll.NiFpgaDll_Download(self.session))
            print "Status:" + str(err)
            if err == 0:
                print "FPGA VI successfully downloaded."
    #Redownloads FPGA to target.

###--------------End Basic Command Section----------------###

##### -----------Begin FIFO Functions ---------######

#NiFpgaDll_ConfigureFifo2
#NiFpgaDll_StopFifo
#NiFpgaDll_StartFifo

# NOTE: CounterFifo declared in last lines of
#       NiFpga_CountertoDAC.h as I32 datatype with value of 0

    def Configure_Fifo2(self, reqDepth=8000):
        self.requested_depth = ctypes.c_size_t(reqDepth)
        self.actual_depth = ctypes.c_size_t(0)
        err = fpga_dll.NiFpgaDll_ConfigureFifo2(self.session, self.fifo, self.requested_depth, self.actual_depth)
        print "FIFO Configure Status:" + str(err)
        if err == 0:
            print "FIFO Configured"
    
    ##Optional Method:  
    def Start_Fifo(self):
        err = fpga_dll.NiFpgaDll_StartFifo(self.session, self.fifo)
        print "Start FIFO Status:" + str(err)
        if err == 0:
            print "FIFO Started"

    def Read_Fifo(self, timeout=5000):
        self.data = ctypes.c_uint32(0)
        self.size = ctypes.c_size_t(8)
        self.timeout = ctypes.c_uint32(timeout)
        self.remaining = ctypes.c_size_t(0)
        err = fpga_dll.NiFpgaDll_ReadFifoU32(self.session, self.fifo, self.data, self.size, self.timeout, self.remaining)
        print "Read FIFO Status:" + str(err)
        if err == 0:
            print "FPGA FIFO Read."
        #Returns Data as "Last" I32

    ##Optional Method:
    def Stop_Fifo(self):
        err = fpga_dll.NiFpgaDll_StopFifo(self.session, self.fifo)
        print "Stop FIFO Status:" + str(err)
        if err == 0:
            print "FPGA VI successfully reset."

##### -----------End FIFO Functions ---------######
### -----------Begin Read/Write Functions ------###

    def Read_Bool(self, indicator):
        data = ctypes.c_char(0)
        err = fpga_dll.NiFpgaDll_ReadBool(self.session, indicator, ctypes.byref(data))
        return err, data.value

    def Read_I16(self, indicator):
        data = ctypes.c_int16(0)
        err = fpga_dll.NiFpgaDll_ReadI16(self.session, indicator, ctypes.byref(data))
        return err, data.value

    def Read_U16(self, indicator):
        data = ctypes.c_uint32(0)
        err = fpga_dll.NiFpgaDll_ReadU16(self.session, indicator, ctypes.byref(data))
        return err, data.value

    def Read_U32(self, indicator):
        data = ctypes.c_uint32(0)
        err = fpga_dll.NiFpgaDll_ReadU32(self.session, indicator, ctypes.byref(data))
        return err, data.value
    

    def Read_ArrayBool(self, indicator, size):
        self.data = np.zeros(shape=size, dtype=np.byte)
        pointer = self.data.ctypes.data_as(ctypes.POINTER(ctypes.c_char)) #  <-- Not sure if variable name is necessary
        err = fpga_dll.NiFpgaDll_ReadArrayBool(self.session, indicator, pointer, size)
        return err, self.data ## ** data.value could quite possibly be problematic due to structural reasons

    def Read_ArrayU32(self, indicator, size):
        self.data = np.zeros(shape=size, dtype=np.uint32)
        pointer = self.data.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)) #  <-- Not sure if variable name is necessary
        err = fpga_dll.NiFpgaDll_ReadArrayU32(self.session, indicator, pointer, size)
        return err, self.data

    
    def Write_ArrayBool(self, indicator, array, size):
        self.data = array #<-- We are writing array. This won't be overwritten. Needs to receive something to write 
        pointer = self.data.ctypes.data_as(ctypes.POINTER(ctypes.c_char))
        err = fpga_dll.NiFpgaDll_WriteArrayBool(self.session, indicator, pointer, size)
        return err


    def Write_Bool(self, indicator, value):
        self.data = value
        err = fpga_dll.NiFpgaDll_WriteBool(self.session, indicator, value)
        return err

    def Write_I16(self, indicator, value):
        self.data = value
        err = fpga_dll.NiFpgaDll_WriteI16(self.session, indicator, value)
        return err
        
    def Write_U32(self, indicator, value):
        self.data = value
        err = fpga_dll.NiFpgaDll_WriteU32(self.session, indicator, value)
        return err


### -----------End Read/Write Functions ------###



###--------------Begin Executable Section-----------------###

#if __name__ == '__main__':
    
    #array_gen()
    #print fpga.err_code_list


