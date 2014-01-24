import ctypes
from ctypes import c_int, c_uint, c_byte, c_ubyte, c_short, c_double, c_float, c_long
from ctypes import pointer, byref, windll, cdll
import time
import numpy as np
import os

andorlibpath = str(os.path.join(os.path.dirname(__file__),"atmcd32d.dll"))
print andorlibpath
andorlib = windll.LoadLibrary(andorlibpath)

import andor_ccd_consts as consts

EM_MODE_I = 0 # 0 is electron mulitplication, 1 is conventional
DEFAULT_TEMPERATURE = -80    
    

class AndorCCD(object):
    
    def __init__(self, debug = False):
    
        if debug: print "AndorCCD initializing"

        self.debug = debug
        

        if andorlib.Initialize("") != consts.DRV_SUCCESS :
            print "Initialization failed"
        else :
            print "Initialization Successful"
        
        headModel = ctypes.create_string_buffer('Hello', consts.MAX_PATH)
        if andorlib.GetHeadModel(headModel) != consts.DRV_SUCCESS :
            print "Error Getting head model"
        else:
            self.headModel = str(headModel.raw).strip('\x00')
            print "Head model: ", repr(self.headModel)

        serialNumber = c_int(-1)
        retval = andorlib.GetCameraSerialNumber(byref(serialNumber)) 
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        self.serialNumber = serialNumber.value
        if debug: print 'Serial Number: ', self.serialNumber

        HW = [ c_int(i) for i in range(6) ] 
        retval = andorlib.GetHardwareVersion( *[ byref(h) for h in HW ] )
        if retval != consts.DRV_SUCCESS :
            print "Error Getting Hardware Version."
        else: 
            self.hardware_version = tuple([ h.value for h in HW])
            if debug: print 'Hardware information: ', self.hardware_version

        SW = [ c_int(i) for i in range(6) ] 
        retval = andorlib.GetSoftwareVersion( *[byref(s) for s in SW] )
        if retval != consts.DRV_SUCCESS :
            print "Error Getting Software Version."
        else: 
            self.software_version = tuple([ s.value for s in SW ])
            print 'Software information: ', self.software_version
            
            
        pixelsX = c_int(1)
        pixelsY = c_int(1)
        
        retval = andorlib.GetDetector(byref(pixelsX), byref(pixelsY))
        if retval != consts.DRV_SUCCESS :
            print "Couldn't get dimensions."
        else :
            self.Nx = pixelsX.value
            self.Ny = pixelsY.value
            print "Dimensions: ", self.Nx, self.Ny
            
        
        numADChan = c_int(-1)
        retval = andorlib.GetNumberADChannels(byref(numADChan)) 
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval    
        self.numADChan = numADChan.value
        if debug: print '# of AD channels [expecting one]: ', self.numADChan
        
        self.set_ad_channel() #set default AD channel
        
        ampNum = c_int(-1)
        retval = andorlib.GetNumberAmp(byref(ampNum))
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        self.ampNum = ampNum.value
        if debug: print 'Number of output amplifiers: ', self.ampNum
        
        #shift speeds
        self.read_shift_speeds()

        self.set_hs_speed()
        self.set_vs_speed()

        # gains

        numGains = c_int(-1)
        retval = andorlib.GetNumberPreAmpGains(pointer(numGains))
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        print '# of gains: ', numGains.value
        self.numGains = numGains.value
        self.preamp_gains = []
        gain = c_float(-1)
        for i in range(numGains.value) :
            retval = andorlib.GetPreAmpGain(i, byref(gain)) 
            assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
            self.preamp_gains.append(gain.value)
        print 'Preamp gains available: ', self.preamp_gains
        
        self.set_preamp_gain()
        

        # EM gain
        self.get_EM_gain_range()
        self.get_EMCCD_gain()

        # temperature
        
        self.get_temperature_range()
        self.get_temperature()

        self.set_temperature(DEFAULT_TEMPERATURE)

        
        self.set_cooler_on()    
    
    #####
    
    def set_ad_channel(self,chan_i=0):
        retval = andorlib.SetADChannel(int(chan_i))
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        self.ad_chan = chan_i
        return self.ad_chan
    
    ##### ReadOut Modes #######################
    def set_ro_full_vertical_binning(self):
        self.ro_mode = 'FULL_VERTICAL_BINNING'
        retval = andorlib.SetReadMode(0)
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        self.outputHeight = 1

    def set_ro_single_track(self, center, width = 1):
        self.ro_mode = 'SINGLE_TRACK'
        retval = andorlib.SetReadMode(3)
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        
        retval =  andorlib.SetSingleTrack(c_int(center), c_int(width)) 
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        #self.outputHeight = ?
        
        
    def set_ro_multi_track(self, number, height, offset):
        # NOT YET IMPLEMENTED
        # SetReadMode(1)
        # SetMulitTrack
        pass
        #returns bottom, gap
        
    def set_ro_random_track(self, positions):
        # NOT YET IMPLEMENTED
        # SetReadMode(2)
        #SetRandomTracks(numberoftracks, positionarray)
        pass
    
    def set_ro_image_mode(self,hbin=1,vbin=1,hstart=0,hend=None,vstart=0,vend=None):
        self.ro_mode = 'IMG'
        retval = andorlib.SetReadMode(4)
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        
        if hend is None:
            hend = self.Nx
        if vend is None:
            vend = self.Ny
        
        self.hbin = hbin
        self.vbin = vbin
        
        self.hstart = hstart
        self.hend   = hend
        
        self.vstart = vstart
        self.vend   = vend
        
        retval = andorlib.SetImage(c_int(hbin),   c_int(vbin), 
                          c_int(hstart+1), c_int(hend),
                          c_int(vstart+1), c_int(vend) )
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        
        self.Nx_ro = int((self.hend-self.hstart)/self.hbin)                
        self.Ny_ro = int((self.vend-self.vstart)/self.vbin)

        self.buffer = np.zeros( shape=(self.Nx_ro, self.Ny_ro), dtype=np.int32 )

        
    
    ##### Acquisition Modes #####
    def set_aq_single_scan(self, exposure=None):
        retval = andorlib.SetAcquisitionMode(1)
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        
        if exposure is not None:
            retval = andorlib.SetExposureTime(c_float(exposure))
            assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        
    def set_aq_accumulate_scan(self, exposure_time=None, num_accumulations=1, cycle_time=None):
        retval = andorlib.SetAcquisitionMode(2)
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval

        if exposure_time is not None:
            retval = andorlib.SetExposureTime(c_float(exposure_time))
            assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
            
        retval = andorlib.SetNumberAccumulations(num_accumulations)
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval

        # cycle_time only valid with internal trigger
        if cycle_time is not None:
            retval = andorlib.SetAccumulationCycleTime(cycle_time)
            assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval

    def set_aq_kinetic_scan(self):
        # NOT YET IMPLEMENTED
        # SetAcquistionMode(3)
        raise NotImplementedError()
        
    def set_aq_run_till_abort_scan(self):
        # NOT YET IMPLEMENTED
        #SetAcquistionMode(5) SetExposureTime(0.3) SetKineticCycleTime(0)
        raise NotImplementedError()
        
    def set_aq_fast_kinetic_scan(self):
        # NOT YET IMPLEMENTED
        raise NotImplementedError()
                
    def set_aq_frame_transfer_scan(self):
        # NOT YET IMPLEMENTED
        raise NotImplementedError()
                
    
    ##### Triggering ##########
    trigger_modes = dict(
                     internal = 0,
                     external = 1,
                     external_start = 6,
                     external_exposure = 7,
                     external_fvb_em = 9,
                     software = 10)
    

    def set_trigger_mode(self, mode):
        mode = mode.lower()
        retval = andorlib.SetTriggerMode(self.trigger_modes[mode])
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
    
    ####### Shift Speeds and Gain ##########
    
    def read_shift_speeds(self):
        # h speeds
        numHSSpeeds = c_int(-1)
        self.numHSSpeeds = []
        for chan_i in range(self.numADChan):
            retval = andorlib.GetNumberHSSpeeds(chan_i, EM_MODE_I, byref(numHSSpeeds)) # EM mode
            assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
            self.numHSSpeeds.append( numHSSpeeds.value )

        print '# of horizontal speeds: ', self.numHSSpeeds
        
        self.HSSpeeds = []
        speed = c_float(0)
        for chan_i in range(self.numADChan):
            self.HSSpeeds.append([])
            hsspeeds = self.HSSpeeds[chan_i]
            for i in range(self.numHSSpeeds[chan_i]):
                retval = andorlib.GetHSSpeed(chan_i, EM_MODE_I, i, byref(speed)) # EM mode
                assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
                hsspeeds.append(speed.value)

        print 'Horizontal speeds [MHz]: ', self.HSSpeeds
        
        #Vertical  speeds
        numVSSpeeds = c_int(-1)
        retval = andorlib.GetNumberVSSpeeds(byref(numVSSpeeds))
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        self.numVSSpeeds = numVSSpeeds.value

        self.VSSpeeds = []
        speed = c_float(0)
        for i in range(self.numVSSpeeds):
            retval = andorlib.GetVSSpeed(i, byref(speed))
            assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
            self.VSSpeeds.append(speed.value)
        print 'Vertical speeds [microseconds per pixel shift]: ', self.VSSpeeds

    
    def set_hs_speed(self,speed_index=0):
        #if typ == "standard": typ = 0
        #elif typ == "EM":     typ = 1
        #assert typ in [0,1]
        assert 0 <= speed_index < self.numHSSpeeds[self.ad_chan]
        retval = andorlib.SetHSSpeed(EM_MODE_I, speed_index) # 0 = default speed (fastest)
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval

    def set_vs_speed(self, speed_index=0):
        assert 0 <= speed_index < self.numVSSpeeds
        retval = andorlib.SetVSSpeed(speed_index)
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
    
    def set_preamp_gain(self, gain_i = 0):
        retval = andorlib.SetPreAmpGain(gain_i)
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        self.preamp_gain_i = gain_i
        #print 'Preamp gain set to  = ', self.preamp_gain[ind]
        

    ####### Image Rotate and Flip ###########
    # done in Andor SDK (not on camera)
    
    def get_image_flip(self):
        hflip, vflip = c_int(-1), c_int(-1)
        retval = andorlib.GetImageFlip(byref(hflip), byref(vflip))
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        self.hflip = bool(hflip.value)
        self.vflip = bool(vflip.value)
        return self.hflip, self.vflip
    
    def set_image_flip(self, hflip=True, vflip=False):
        retval = andorlib.SetImageFlip( c_int(bool(hflip)), c_int(bool(vflip)))
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
    
    def set_image_rotate(self, rotate=0):
        # 0 - No rotation
        # 1 - Rotate 90 degrees clockwise
        # 2 - Rotate 90 degrees anti-clockwise
        assert rotate in [0,1,2]
        retval = andorlib.SetImageRotation(c_int(rotate))        
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        
    
    ####### Shutter Control ##########
    
    def set_shutter_auto(self):
        retval = andorlib.SetShutter(0, 0, 0, 0)
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval

    def set_shutter_open(self):
        retval = andorlib.SetShutter(0, 1, 0, 0)
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval

    def set_shutter_close(self):
        retval = andorlib.SetShutter(0, 2, 0, 0)
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
    
    ####### Temperature Control ###########
    
    def set_cooler_on(self):
        retval = andorlib.CoolerON()
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
    def set_cooler_off(self):
        retval = andorlib.CoolerOFF()
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval

    def get_temperature_range(self):
        min_t, max_t = c_int(0), c_int(0)
        retval = andorlib.GetTemperatureRange( byref(min_t), byref(max_t) )
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        self.min_temp = min_t.value
        self.max_temp = max_t.value 
        return self.min_temp, self.max_temp

    def set_temperature(self, new_temp):
        retval = andorlib.SetTemperature(c_int(new_temp))
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        self.get_temperature()

    def get_temperature(self):
        lastTemp = c_int(0)
        retval = andorlib.GetTemperature(byref(lastTemp))
        if retval in [consts.DRV_NOT_INITIALIZED, consts.DRV_ERROR_ACK]:
            raise IOError, "Andor DRV Failure %i" % retval
        if retval == consts.DRV_ACQUIRING:
            raise IOError, "Camera busy acquiring"
        self.temperature = lastTemp.value
        self.temperature_status = retval
        return self.temperature


    #### Acquire ####
    
    # StartAcquisition() --> GetStatus() --> GetAcquiredData()
    
    def start_acquisition(self):
        retval = andorlib.StartAcquisition()
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval

    _status_name_dict = {
        consts.DRV_IDLE: "IDLE",
        consts.DRV_TEMPCYCLE: "TEMPCYCLE",
        consts.DRV_ACQUIRING: "ACQUIRING",
        consts.DRV_ACCUM_TIME_NOT_MET: "ACCUM_TIME_NOT_MET",
        consts.DRV_KINETIC_TIME_NOT_MET: "KINETIC_TIME_NOT_MET",
        consts.DRV_ERROR_ACK: "ERROR_ACK",
        consts.DRV_ACQ_BUFFER: "ACQ_BUFFER",
        consts.DRV_SPOOLERROR: "SPOOLERROR",
    }
    def get_status(self):
        status = c_int(-1)
        retval = andorlib.GetStatus(byref(status))
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        self.status_id   = status.value
        self.status_name = self._status_name_dict[self.status_id]
        return self.status_id, self.status_name            

    
    def get_acquired_data(self):
        retval = andorlib.GetAcquiredData(self.buffer.ctypes.data_as(ctypes.POINTER(c_long)), c_uint(self.buffer.size))
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        return self.buffer

    
    #### Acquisition Timings #####################
    
    def get_acquisition_timings(self):
        exposure = c_float(-1)
        accum   = c_float(-1)
        kinetic = c_float(-1)
        
        retval = andorlib.GetAcquisitionTimings(byref(exposure), byref(accum), byref(kinetic))
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        
        self.exposure_time = exposure.value
        self.accumulation_time = accum.value
        self.kinetic_cycle_time = kinetic.value
        
        return self.exposure_time, self.accumulation_time, self.kinetic_cycle_time  
        
    
    def set_exposure_time(self, dt):
        retval = andorlib.SetExposureTime(c_float(dt)) 
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        self.get_acquisition_timings()
        if self.debug : print 'set exposure to: ', self.exposure_time    
        return self.exposure_time
    
    
    ###### Electron Multiplication Mode (EM) ########
    def set_EM_advanced(self, state=True):
        retval = andorlib.GetEMGainRange(c_int(state))
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        
    def get_EM_gain_range(self):
        low, high = c_int(-1), c_int(-1)
        retval = andorlib.GetEMGainRange(byref(low),byref(high))
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        self.em_gain_range = (low.value, high.value)
        return self.em_gain_range
    
    def get_EMCCD_gain(self):
        gain = c_int(-1)
        retval = andorlib.GetEMCCDGain(byref(gain))
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        self.em_gain = gain.value
        return self.em_gain
    
    def set_EMCCD_gain(self, gain):
        low,high = self.em_gain_range
        assert low <= gain <= high
        retval = andorlib.SetEMCCDGain(c_int(gain))
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval


if __name__ == '__main__':
    import time
    
    cam = AndorCCD(debug=True)
    
    cam.set_ro_image_mode()
    cam.set_trigger_mode('internal')
    cam.set_exposure(1.0)
    cam.set_shutter_open()
    cam.start_acquisition()
    stat = "ACQUIRING",
    while stat != "IDLE":
        time.sleep(0.1)
        stati, stat = cam.get_status()
    cam.get_acquired_data()
    cam.set_shutter_close()

    import pylab as pl
    pl.imshow(cam.buffer, interpolation='nearest', origin='lower')
    pl.show()
    


