import ctypes
from ctypes import create_string_buffer, c_int, c_char, c_char_p, c_byte, c_ubyte, c_short, c_double, cdll, pointer, byref
import time
import numpy

phlib = ctypes.WinDLL("phlib.dll")

print phlib


class PicoHarp300(object):

    MODE_HIST = 0
    HISTCHAN  = 65536

    def __init__(self, devnum=0, debug=False):
        self.debug = debug
        self.devnum = devnum
        self.lib_version = create_string_buffer(8)
        phlib.PH_GetLibraryVersion(self.lib_version);
        if self.debug: print "PHLib Version: '%s'" % self.lib_version.value #% str(self.lib_version.raw).strip()
        self.lib_version = self.lib_version.value
        
        self.hw_serial = create_string_buffer(8)
        retcode = phlib.PH_OpenDevice(self.devnum, self.hw_serial) 
        if(retcode==0):
            self.hw_serial = self.hw_serial.value
            if self.debug: print "Device %i Found, serial %s" % (self.devnum, self.hw_serial)
        else:
            print "failed to find device %i" % self.devnum
            error_string = create_string_buffer(40)
            phlib.PH_GetErrorString(error_string, retcode)
            print "print Error: %s" % error_string.value
        
        if self.debug:  print "Initializing the device..."
        retcode = phlib.PH_Initialize(self.devnum, self.MODE_HIST)
        if retcode < 0:
            print "PH init error %i. Aborted." % retcode

        self.hw_model   = create_string_buffer(8)
        self.hw_version = create_string_buffer(16)
        retcode = phlib.PH_GetHardwareVersion(self.devnum,self.hw_model,self.hw_version); #/*this is only for information*/
        if retcode < 0:
            print "PH_GetHardwareVersion error %d. Aborted." % retcode
        else:
            self.hw_model   = self.hw_model.value
            self.hw_version = self.hw_version.value
            print "Found Model %s Version %s" % (self.hw_model, self.hw_version)
        
        if self.debug: print "Calibrating..."
        retcode = phlib.PH_Calibrate(self.devnum);
        if retcode < 0:
            print "PH_Calibrate error %i" % retcode

    def setup_experiment(self, 
            Range=0, Offset=0, 
            Tacq=1000, #Measurement time in millisec, you can change this
            SyncDivider = 8, 
            CFDZeroCross0=10, CFDLevel0=100, 
            CFDZeroCross1=10, CFDLevel1=100):

        self.Tacq = int(Tacq)

        self.SyncDivider = int(SyncDivider)
        retcode = phlib.PH_SetSyncDiv(self.devnum, self.SyncDivider)
        if retcode < 0: print "PH_SetSyncDiv error %i" % retcode
        
        self.CFDLevel0 = int(CFDLevel0)
        retcode = phlib.PH_SetCFDLevel(self.devnum, 0, self.CFDLevel0)
        if retcode < 0: print "PH_SetCFDLevel error %i" % retcode

        self.CFDZeroCross0 = int(CFDZeroCross0)
        retcode = phlib.PH_SetCFDZeroCross(self.devnum,0, self.CFDZeroCross0)
        if retcode < 0: print "PH_SetCFDZeroCross error %i" % retcode

        self.CFDLevel1 = int(CFDLevel1)
        retcode = phlib.PH_SetCFDLevel(self.devnum, 1, self.CFDLevel1)
        if retcode < 0: print "PH_SetCFDLevel error %i" % retcode

        self.CFDZeroCross1 = int(CFDZeroCross1)
        retcode = phlib.PH_SetCFDZeroCross(self.devnum,1, self.CFDZeroCross1)
        if retcode < 0: print "PH_SetCFDZeroCross error %i" % retcode
        
        self.Range = int(Range)
        retcode = phlib.PH_SetRange(self.devnum, self.Range)
        if retcode < 0: print "PH_SetRange error %i" % retcode
        
        self.Offset = int(Offset)
        retcode = phlib.PH_SetOffset(self.devnum, self.Offset)
        if retcode < 0: print "PH_SetOffset error %i" % retcode
        
        self.Resolution = phlib.PH_GetResolution(self.devnum)
        
        #Note: after Init or SetSyncDiv you must allow 100 ms for valid new count rate readings
        time.sleep(0.2);
        self.Countrate0 = phlib.PH_GetCountRate(self.devnum,0);
        self.Countrate1 = phlib.PH_GetCountRate(self.devnum,1);

        if self.debug: print "Resolution=%1dps Countrate0=%1d/s Countrate1=%1d/s" % (self.Resolution, self.Countrate0, self.Countrate1)

        phlib.PH_SetStopOverflow(self.devnum,1,65535)
        
    def read_count_rates(self):
        self.Countrate0 = phlib.PH_GetCountRate(self.devnum,0);
        self.Countrate1 = phlib.PH_GetCountRate(self.devnum,1);
        return self.Countrate0, self.Countrate1
        
    def start_histogram(self, Tacq=None):
        if self.debug: print "Starting Histogram"
        phlib.PH_ClearHistMem(self.devnum, 0) # always use Block 0 if not Routing
        
        # set a new acquisition time if given
        if Tacq:
            self.Tacq = int(Tacq)
            
        retcode = phlib.PH_StartMeas(self.devnum, self.Tacq)
        if retcode < 0: "PH_StartMeas error %i" % retcode
        
        return
    
    def check_done_scanning(self):
        status = phlib.PH_CTCStatus(self.devnum)
        if status == 0: # not done
            return False
        else: # scanning done
            return True
            
    def stop_histogram(self):
        if self.debug: print "Stop Histogram"
        retcode = phlib.PH_StopMeas(self.devnum)
        if retcode < 0: "PH_StopMeas error %i" % retcode
        
    def read_histogram_data(self):
        if self.debug: print "Read Histogram Data"
        
        #unsigned int counts[HISTCHAN];
        self.hist_data = numpy.zeros(self.HISTCHAN, dtype=numpy.uint32)
        
        retcode = phlib.PH_GetBlock(self.devnum, self.hist_data.ctypes.data, 0) # grab block 0
        if retcode < 0: "PH_GetBlock error %i" % retcode

        return self.hist_data


if __name__ == '__main__':
    
    import pylab as pl
    
    ph = PicoHarp300(debug=True)
    ph.setup_experiment()#Range, Offset, Tacq, SyncDivider, CFDZeroCross0, CFDLevel0, CFDZeroCross1, CFDLevel1)
    ph.start_histogram(Tacq=2300)
    t0 = time.time()
    while not ph.check_done_scanning():
        print "acquiring", time.time() - t0, "sec"
        time.sleep(0.1)
    ph.stop_histogram()
    ph.read_histogram_data()
    
    pl.figure(1)
    pl.plot(ph.hist_data)
    pl.show()