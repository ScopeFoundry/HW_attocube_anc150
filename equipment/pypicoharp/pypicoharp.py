import ctypes
from ctypes import create_string_buffer, c_int, c_double, byref
import time
import numpy
import platform

if platform.architecture()[0] == '64bit':
    phlib = ctypes.WinDLL("phlib64.dll")
else:
    phlib = ctypes.WinDLL("phlib.dll")

# updated for phlib v3.0 2014-04-02

class PicoHarp300(object):

    MODE_HIST = 0
    HISTCHAN  = 65536

    def __init__(self, devnum=0, debug=False):
        self.debug = debug
        self.devnum = devnum
        self.Countrate    = [None,None]
        self.CFDLevel     = [None,None]
        self.CFDZeroCross = [None, None]
        self.histogram_data = numpy.zeros(self.HISTCHAN, dtype=numpy.uint32) #unsigned int counts[HISTCHAN];
        self.time_array = numpy.arange(self.HISTCHAN, dtype=float)

        self._err_buffer = create_string_buffer(40)
        
        lib_version = create_string_buffer(8)
        self.handle_err(phlib.PH_GetLibraryVersion(lib_version))
        self.lib_version = lib_version.value
        if self.debug: print "PHLib Version: '%s'" % self.lib_version
        assert self.lib_version == "3.0"
        
        hw_serial = create_string_buffer(8)
        self.handle_err(phlib.PH_OpenDevice(self.devnum, hw_serial)) 
        self.hw_serial = hw_serial.value
        if self.debug: print "Device %i Found, serial %s" % (self.devnum, self.hw_serial)

        
        if self.debug:  print "Initializing PicoHarp device..."
        self.handle_err(phlib.PH_Initialize(self.devnum, self.MODE_HIST))
        
        hw_model   = create_string_buffer(16)
        hw_partnum = create_string_buffer(8)
        hw_version = create_string_buffer(8)
        self.handle_err(phlib.PH_GetHardwareInfo(
                                self.devnum,hw_model,hw_partnum, hw_version))
        self.hw_model   = hw_model.value
        self.hw_partnum = hw_partnum.value
        self.hw_version = hw_version.value
        if self.debug: 
            print "Found Model %s PartNum %s Version %s" % (self.hw_model, self.hw_partnum, self.hw_version)
        
        if self.debug: print "PicoHarp Calibrating..."
        self.handle_err( phlib.PH_Calibrate(self.devnum) )
            
        # automatically stops acquiring a histogram when a bin is filled to 2**16
        self.handle_err(phlib.PH_SetStopOverflow(self.devnum,1,65535)) 
    
    def handle_err(self, retcode):
        if retcode < 0:
            phlib.PH_GetErrorString(self._err_buffer, retcode)
            self.err_message = self._err_buffer.value
            raise IOError(self.err_message)
        return retcode

    def setup_experiment(self, 
            Tacq=1000, #Measurement time in millisec, you can change this
            Binning=0, SyncOffset=0, 
            SyncDivider = 8, 
            CFDZeroCross0=10, CFDLevel0=100, 
            CFDZeroCross1=10, CFDLevel1=100):

        self.Tacq = self.set_Tacq(Tacq)
        
        self.write_Binning(Binning)
        self.write_SyncOffset(SyncOffset)
        self.write_SyncDivider(SyncDivider)
        self.write_InputCFD(0, CFDLevel0, CFDZeroCross0)
        self.write_InputCFD(1, CFDLevel1, CFDZeroCross1)

        self.read_count_rates()
        if self.debug: print "Resolution=%1dps Countrate0=%1d/s Countrate1=%1d/s" % (self.Resolution, self.Countrate0, self.Countrate1)

    def set_Tacq(self, Tacq):
        self.Tacq = int(Tacq)
        return self.Tacq

    def write_SyncDivider(self, SyncDivider):
        self.SyncDivider = int(SyncDivider)
        if self.debug: print "write_SyncDivider", self.SyncDivider
        self.handle_err(phlib.PH_SetSyncDiv(self.devnum, self.SyncDivider))
        #Note: after Init or SetSyncDiv you must allow 100 ms for valid new count rate readings
        time.sleep(0.11)

    
    def write_InputCFD(self, chan, level, zerocross):
        self.CFDLevel[chan] = int(level)
        self.CFDZeroCross[chan] = int(zerocross)
        if self.debug: print "write_InputCFD", chan, level, zerocross
        self.handle_err(phlib.PH_SetInputCFD(self.devnum, chan, int(level), int(zerocross)))
        
    def write_CFDLevel0(self, level):
        self.write_InputCFD(0, level, self.CFDZeroCross[0])
        
    def write_CFDLevel1(self, level):
        self.write_InputCFD(1, level, self.CFDZeroCross[1])

    def write_CFDZeroCross0(self, zerocross):
        self.write_InputCFD(0, self.CFDLevel[0], zerocross)
    
    def write_CFDZeroCross1(self, zerocross):
        self.write_InputCFD(1, self.CFDLevel[1], zerocross)
        
        
    def write_Binning(self, Binning):
        self.Binning = int(Binning)
        self.handle_err(phlib.PH_SetBinning(self.devnum, self.Binning))
        self.read_Resolution()
        self.time_array = numpy.arange(self.HISTCHAN, dtype=float)*self.Resolution
        
    def read_Resolution(self):
        r = c_double(0)
        self.handle_err(phlib.PH_GetResolution(self.devnum, byref(r)))
        self.Resolution = r.value
        return self.Resolution

    def write_SyncOffset(self, SyncOffset):
        """
        :param SyncOffset: time offset in picoseconds
        :type SyncOffset: int
        """     
        self.SyncOffset = int(SyncOffset)
        self.handle_err(phlib.PH_SetOffset(self.devnum, self.SyncOffset))

    def read_count_rate(self, chan):
        cr = c_int(-1)
        self.handle_err(phlib.PH_GetCountRate(self.devnum, chan, byref(cr)))
        self.Countrate[chan] = cr.value
        return cr.value
    
    def read_count_rate0(self):
        self.Countrate0 = self.read_count_rate(0)
        return self.Countrate0
    
    def read_count_rate1(self):
        self.Countrate1 = self.read_count_rate(1)
        return self.Countrate1

    def read_count_rates(self):
        self.read_count_rate0()
        self.read_count_rate1()
        return self.Countrate0, self.Countrate1
        
    def start_histogram(self, Tacq=None):
        if self.debug: print "Starting Histogram"

        self.handle_err(phlib.PH_ClearHistMem(self.devnum, 0))
        # always use Block 0 if not Routing
        
        # set a new acquisition time if given
        if Tacq:
            self.set_Tacq(Tacq)
            
        self.handle_err(phlib.PH_StartMeas(self.devnum, self.Tacq))        

    
    def check_done_scanning(self):
        status = c_int()
        self.handle_err(phlib.PH_CTCStatus(self.devnum, byref(status)))
        if status.value == 0: # not done
            return False
        else: # scanning done
            return True
            
    def stop_histogram(self):
        if self.debug: print "Stop Histogram"
        self.handle_err(phlib.PH_StopMeas(self.devnum))
        
    def read_histogram_data(self):
        if self.debug: print "Read Histogram Data"
        self.handle_err(phlib.PH_GetHistogram(self.devnum, self.histogram_data.ctypes.data, 0)) # grab block 0
        return self.histogram_data
    
    def write_stop_overflow(self, stop_on_overflow=True, stopcount=65535):
        """
        This setting determines if a measurement run will stop if any channel 
        reaches the maximum set by stopcount. If stop_ofl is 0
        the measurement will continue but counts above 65,535 in any bin will be clipped.
        """
        
        if stop_on_overflow:
            overflow_int = 1
        else:
            overflow_int = 0
        
        self.handle_err(phlib.PH_SetStopOverflow(self.devnum, overflow_int, stopcount))
        
    def read_elapsed_meas_time(self):
        elapsed_time = ctypes.c_double()
        self.handle_err(phlib.PH_GetElapsedMeasTime(self.devnum, byref(elapsed_time)))
    
        self.elapsed_time = elapsed_time.value
        return self.elapsed_time
    
    def close(self):
        return self.handle_err(phlib.PH_CloseDevice(self.devnum))
    

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
    pl.plot(ph.histogram_data)
    pl.show()