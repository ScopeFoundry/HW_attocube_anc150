from __future__ import absolute_import, print_function
import ctypes
from ctypes import c_int, c_uint, c_byte, c_ubyte, c_short, c_double, c_float, c_long
from ctypes import pointer, byref, windll, cdll
import time
import numpy as np
import os

import platform
import logging

from enum import Enum

from . import andor_ccd_consts as consts


logger = logging.getLogger(__name__)


if platform.architecture()[0] == '64bit':
    andorlibpath = str(os.path.join(os.path.dirname(__file__),"atmcd64d.dll"))
else:
    andorlibpath = str(os.path.join(os.path.dirname(__file__),"atmcd32d.dll"))
#print andorlibpath

andorlib = windll.LoadLibrary(andorlibpath)


DEFAULT_TEMPERATURE = -80
DEFAULT_EM_GAIN = 10
DEFAULT_OUTPUT_AMP = 0  # 0 is electron multitplication, 1 is conventional    


# Read modes for the EMCCD:
class AndorReadMode(Enum):
    FullVerticalBinning = 0
    MultiTrack = 1
    RandomTrack = 2
    SingleTrack = 3
    Image = 4


class AndorCCD(object):
    
    def __init__(self, debug = False):
    
        self.debug = debug
        
        if self.debug:  logger.debug("AndorCCD initializing")
            
        retval = andorlib.Initialize("") 
        
        if retval != consts.DRV_SUCCESS:
            raise IOError( "Andor CCD: Initialization failed %i" % retval)
        else :
            if self.debug: logger.debug("Andor CCD Initialization Successful")
        
        headModel = ctypes.create_string_buffer(consts.MAX_PATH)
        if andorlib.GetHeadModel(headModel) != consts.DRV_SUCCESS :
            raise IOError( "Andor CCD: Error Getting head model")
        else:
            self.headModel = str(headModel.raw).strip('\x00')
            if self.debug: logger.debug("Head model: "+ repr(self.headModel))

        serialNumber = c_int(-1)
        retval = andorlib.GetCameraSerialNumber(byref(serialNumber)) 
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        self.serialNumber = serialNumber.value
        if self.debug: logger.debug('Serial Number: %g' % self.serialNumber)

        HW = [ c_int(i) for i in range(6) ] 
        retval = andorlib.GetHardwareVersion( *[ byref(h) for h in HW ] )
        if retval != consts.DRV_SUCCESS :
            raise IOError( "Andor CCD: Error Getting Hardware Version.")
        else: 
            self.hardware_version = tuple([ h.value for h in HW])
            if self.debug: logger.debug('Hardware information: {}'.format( repr(self.hardware_version)))

        SW = [ c_int(i) for i in range(6) ] 
        retval = andorlib.GetSoftwareVersion( *[byref(s) for s in SW] )
        if retval != consts.DRV_SUCCESS :
            raise IOError( "Andor CCD: Error Getting Software Version.")
        else: 
            self.software_version = tuple([ s.value for s in SW ])
            if self.debug: logger.debug('Software information: %s' % repr(self.software_version))
            
            
        pixelsX = c_int(1)
        pixelsY = c_int(1)
        
        retval = andorlib.GetDetector(byref(pixelsX), byref(pixelsY))
        if retval != consts.DRV_SUCCESS :
            raise IOError( "Andor CCD: Couldn't get dimensions.")
        else :
            self.Nx = pixelsX.value
            self.Ny = pixelsY.value
            if self.debug: logger.debug("Dimensions: {} {}".format( self.Nx, self.Ny ))
            
        
        numADChan = c_int(-1)
        retval = andorlib.GetNumberADChannels(byref(numADChan)) 
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval    
        self.numADChan = numADChan.value
        if debug: logger.debug( '# of AD channels [expecting one]: %g' % self.numADChan )
        
        self.set_ad_channel() #set default AD channel
        
        ampNum = c_int(-1)
        retval = andorlib.GetNumberAmp(byref(ampNum))
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        self.ampNum = ampNum.value
        if debug: logger.debug( 'Number of output amplifiers: %g' % self.ampNum ) 
        
        #shift speeds
        self.read_shift_speeds()
        self.set_hs_speed_em()
        self.set_hs_speed_conventional()
        self.set_vs_speed()

        # gains

        numGains = c_int(-1)
        retval = andorlib.GetNumberPreAmpGains(pointer(numGains))
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        if self.debug: logger.debug('# of gains: %g '% numGains.value)
        self.numGains = numGains.value
        self.preamp_gains = []
        gain = c_float(-1)
        for i in range(numGains.value) :
            retval = andorlib.GetPreAmpGain(i, byref(gain)) 
            assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
            self.preamp_gains.append(gain.value)
        if self.debug: logger.debug('Preamp gains available: %s' % self.preamp_gains)

        self.set_preamp_gain()
        

        # EM gain
        self.get_EM_gain_range()
        self.get_EMCCD_gain()

        # temperature        
        self.get_temperature_range()
        self.get_temperature()

        self.set_temperature(DEFAULT_TEMPERATURE)
        self.set_cooler_on()
        
        # Initialize the camera
        self.set_shutter_open(False)             # Shutter closed
        self.set_output_amp(DEFAULT_OUTPUT_AMP)  # Default output amplifier
        self.set_EMCCD_gain(DEFAULT_EM_GAIN)     # Default EM Gain
        
    
    #####
    
    
    
    
    def set_ad_channel(self,chan_i=0):
        assert chan_i in range(0,self.numADChan)
        retval = andorlib.SetADChannel(int(chan_i))
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        self.ad_chan = chan_i
        return self.ad_chan
    
    ##### ReadOut Modes #######################
    def set_readout_mode(self, ro_mode):
        if (ro_mode == AndorReadMode.FullVerticalBinning):
            self.set_ro_full_vertical_binning()
        elif (ro_mode == AndorReadMode.Image):
            self.set_ro_image_mode()
        elif (ro_mode == AndorReadMode.MultiTrack):
            raise NotImplementedError()
        elif (ro_mode == AndorReadMode.RandomTrack):
            raise NotImplementedError()
        elif (ro_mode == AndorReadMode.SingleTrack):
            self.set_ro_single_track(256, 20)
    
    def set_ro_full_vertical_binning(self, hbin=1):
        self.ro_mode = 'FULL_VERTICAL_BINNING'
        retval = andorlib.SetReadMode(0) # sets to FVB
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        self.ro_fvb_hbin = hbin
        retval = andorlib.SetFVBHBin(self.ro_fvb_hbin)
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        #self.outputHeight = 1
        self.Nx_ro = int(self.Nx/hbin)              
        self.Ny_ro = 1
        self.buffer = np.zeros(shape=(self.Ny_ro, self.Nx_ro), dtype=np.int32 )       

    def set_ro_single_track(self, center, width = 1, hbin = 1):
        self.ro_mode = 'SINGLE_TRACK'
        retval = andorlib.SetReadMode(3)
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        
        retval =  andorlib.SetSingleTrack(c_int(center), c_int(width)) 
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        #self.outputHeight = ?
        #not tested...
    
        retval =  andorlib.SetSingleTrackHBin(c_int(hbin)) 
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        
        self.ro_st_hbin = hbin
        self.Nx_ro = int(self.Nx/hbin)              
        self.Ny_ro = 1

        self.ro_single_track_center = center
        self.ro_single_track_width = width
        self.buffer = np.zeros(shape=(self.Ny_ro, self.Nx_ro), dtype=np.int32 )
        
        
    def set_ro_multi_track(self, number, height, offset):
        # NOT YET IMPLEMENTED
        # SetReadMode(1)
        # SetMulitTrack
        raise NotImplementedError
        #returns bottom, gap
        
    def set_ro_random_track(self, positions):
        # NOT YET IMPLEMENTED
        # SetReadMode(2)
        #SetRandomTracks(numberoftracks, positionarray)
        raise NotImplementedError
    
    def set_ro_image_mode(self,hbin=1,vbin=1,hstart=1,hend=None,vstart=1,vend=None):
        self.ro_mode = 'IMG'
        retval = andorlib.SetReadMode(4)
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        
        if hend is None:
            hend = self.Nx
        if vend is None:
            vend = self.Ny
        
        assert hend > hstart
        assert vend > vstart
        
        self.hbin = hbin
        self.vbin = vbin
        
        self.hstart = hstart
        self.hend   = hend
        
        self.vstart = vstart
        self.vend   = vend
        
        retval = andorlib.SetImage(c_int(hbin),   c_int(vbin), 
                          c_int(hstart), c_int(hend),
                          c_int(vstart), c_int(vend) )
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        
        self.Nx_ro = int((self.hend-self.hstart+1)/self.hbin)                
        self.Ny_ro = int((self.vend-self.vstart+1)/self.vbin)
        
        logger.debug("self.Nx_ro: {}, self.Ny_ro: {}".format( self.Nx_ro, self.Ny_ro )) 

        self.buffer = np.zeros(shape=(self.Ny_ro, self.Nx_ro), dtype=np.int32 )

    ### Function to return the binning based on the current readout mode ####
    def get_current_hbin(self):
        if self.ro_mode == 'IMG':
            return self.hbin
        elif self.ro_mode == 'SINGLE_TRACK':
            return self.ro_st_hbin
        elif self.ro_mode == 'FULL_VERTICAL_BINNING':
            return self.ro_fvb_hbin
    
    
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
    

    def set_trigger_mode(self, mode='internal'):
        mode = mode.lower()
        retval = andorlib.SetTriggerMode(self.trigger_modes[mode])
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
    
    ####### Shift Speeds and Gain ##########
    
    def read_shift_speeds(self):
        # h speeds
        numHSSpeeds = c_int(-1)
        self.numHSSpeeds_EM = []
        self.numHSSpeeds_Conventional = []
        for chan_i in range(self.numADChan):
            retval = andorlib.GetNumberHSSpeeds(chan_i, 0, byref(numHSSpeeds)) # EM mode
            assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
            self.numHSSpeeds_EM.append(numHSSpeeds.value)
            retval = andorlib.GetNumberHSSpeeds(chan_i, 1, byref(numHSSpeeds)) # conventional mode mode
            assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
            self.numHSSpeeds_Conventional.append(numHSSpeeds.value)
            

        logger.debug('# of horizontal speeds EM: {}'.format(self.numHSSpeeds_EM))
        logger.debug('# of horizontal speeds Conventional: {}'.format(self.numHSSpeeds_Conventional))
        
        self.HSSpeeds_EM = []
        self.HSSpeeds_Conventional = []
        speed = c_float(0)
        for chan_i in range(self.numADChan):
            self.HSSpeeds_EM.append([])
            hsspeeds = self.HSSpeeds_EM[chan_i]
            for i in range(self.numHSSpeeds_EM[chan_i]):
                retval = andorlib.GetHSSpeed(chan_i, 0, i, byref(speed)) # EM mode
                assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
                hsspeeds.append(speed.value)
            self.HSSpeeds_Conventional.append([])
            hsspeeds = self.HSSpeeds_Conventional[chan_i]
            for i in range(self.numHSSpeeds_Conventional[chan_i]):
                #print chan_i, i
                retval = andorlib.GetHSSpeed(chan_i,  1, i, byref(speed)) # Conventional mode
                assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
                hsspeeds.append(speed.value)
            

        logger.debug('EM Horizontal speeds: {} MHz'.format(self.HSSpeeds_EM))
        logger.debug('Conventional Horizontal speeds: {} MHz'.format(self.HSSpeeds_Conventional))        
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
        if self.debug: logger.debug( 'Vertical speeds [microseconds per pixel shift]: %s' % self.VSSpeeds)
    
    def get_hs_speed_val_conventional(self, speed_index):
        pass

    def set_hs_speed_em(self,speed_index=0):
        logger.debug("set_hs_speed_em {}".format(speed_index))
        assert 0 <= speed_index < self.numHSSpeeds_EM[self.ad_chan]
        retval = andorlib.SetHSSpeed(0, speed_index) # 0 = default speed (fastest), #arg0 -> EM mode = 0
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval

    def set_hs_speed_conventional(self,speed_index=0):
        assert 0 <= speed_index < self.numHSSpeeds_Conventional[self.ad_chan]
        retval = andorlib.SetHSSpeed(1, speed_index) # 0 = default speed (fastest), #arg0 -> conventional = 1
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
    
    def get_image_hflip(self):
        return self.get_image_flip()[0]
    
    def set_image_hflip(self, hflipNew):
        hflipOld, vflipOld = self.get_image_flip()
        self.set_image_flip(hflipNew, vflipOld)
        logger.debug( "set_image_hflip: {}".format(hflipNew)) 
    
    def get_image_vflip(self):
        return self.get_image_flip()[1]
    
    def set_image_vflip(self, vflipNew):
        hflipOld, vflipOld = self.get_image_flip()
        self.set_image_flip(hflipOld, vflipNew)
        logger.debug(  "set_image_vflip: {}".format( vflipNew ))
        
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

    def set_shutter_open(self, open=True):
        if open:
            retval = andorlib.SetShutter(0, 1, 0, 0)
            assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        else:
            self.set_shutter_close()
            
    def set_shutter_close(self):
        retval = andorlib.SetShutter(0, 2, 0, 0)
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
    
    
    ####### Temperature Control ###########
    
    def set_cooler_on(self):
        retval = andorlib.CoolerON()
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        self.cooler_on = True
        
    def set_cooler_off(self):
        retval = andorlib.CoolerOFF()
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        self.cooler_on = False
        
    def set_cooler(self, coolerOn):
        if coolerOn:
            self.set_cooler_on()
        else:
            self.set_cooler_off()

    def get_cooler(self):
        return self.cooler_on 


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
            raise IOError( "Andor DRV Failure %i" % retval)
        if retval == consts.DRV_ACQUIRING:
            raise IOError( "Camera busy acquiring" )
        self.temperature = lastTemp.value
        self.temperature_status = retval
        return self.temperature

    """
    @property
    def temperature_status_str(self):
        DRV_TEMP_STABILIZED 
        DRV_TEMP_NOT_REACHED 
        DRV_TEMP_DRIFT 
        DRV_TEMP_NOT_STABILIZED        

    def is_temperature_stable(self):
        "call get_temperature first"
        if self.temperature_status == consts.
    """    

        
    
    
    #### Acquire ####
    
    # StartAcquisition() --> GetStatus() --> GetAcquiredData()
    
    def start_acquisition(self):
        retval = andorlib.StartAcquisition()
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval

    def abort_acquisition(self):
        retval = andorlib.AbortAcquisition()
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
        return self.status_name            

    
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
        if self.debug : logger.debug( 'set exposure to: {}'.format( self.exposure_time))    
        return self.exposure_time
    
    def get_exposure_time(self):
        return self.get_acquisition_timings()[0]
    
    
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
    
    def set_output_amp(self, amp):
        retval = andorlib.SetOutputAmplifier(c_int(amp))
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
        self.output_amp = amp
        
    def get_output_amp(self):
        return self.output_amp
    
    def close(self):
        retval = andorlib.ShutDown()
        assert retval == consts.DRV_SUCCESS, "Andor DRV Failure %i" % retval
    
    
if __name__ == '__main__':
    import time
    
    cam = AndorCCD(debug=True)
    
    cam.set_ro_image_mode()
    cam.set_trigger_mode('internal')
    cam.set_exposure_time(1.0)
    #cam.set_shutter_open()
    andorlib.SetOutputAmplifier(0) # EMCCD
    
    cam.read_shift_speeds()
    
    andorlib.SetOutputAmplifier(1) # Conventional
    
    #cam.set_hs_speed(1)
    andorlib.SetEMGainMode(1)
    print("EM_gain_range", cam.get_EM_gain_range())
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
    


