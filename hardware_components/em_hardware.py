from . import HardwareComponent

try:
    from equipment.NCEMscope import ScopeWrapper
except Exception as err:
    print "Cannot load required modules for em_hardware:", err
    
#-------------------------------------------------------------------------------
class EMHardwareComponent(HardwareComponent):
    
    #---------------------------------------------------------------------------
    def setup(self):
        self.debug = self.debug_mode.val
        self.name = "em_hardware"

        self.current_defocus = self.add_logged_quantity(
                                name = 'current_defocus',
                                dtype = float, fmt="%e", ro=False,
                                unit="Nm",
                                vmin=-100,vmax=100)
        self.current_binning = self.add_logged_quantity(
                                name = 'current_binning',
                                dtype = int, fmt="%e", ro=False,
                                unit=None,
                                vmin=1,vmax=None)
        self.current_exposure = self.add_logged_quantity(
                        name = 'current_exposure',
                        dtype = float, fmt="%e", ro=False,
                        unit="s",
                        vmin=-1.0,vmax=100.0) 
        self.current_dwell = self.add_logged_quantity(
                        name = 'current_dwell',
                        dtype = float, fmt="%e", ro=False,
                        unit="s",
                        vmin=-1.0,vmax=100.0)
        self.dummy_mode = self.add_logged_quantity(name='dummy_mode',
                            dtype=bool, initial=False, ro=False)    
                       
    #---------------------------------------------------------------------------
    def connect(self):        
        if not self.dummy_mode.val:
            if self.debug_mode.val: print "Connecting to Scope"
            self.wrapper = ScopeWrapper(debug = self.debug_mode.val)
            self.wrapper.Connect()
            
            #handy to have these references
            self.Scope = self.wrapper.Scope
            self.Acq = self.wrapper.Acq
            self.Ill = self.wrapper.Ill
            self.Proj = self.wrapper.Proj
            self.Stage = self.wrapper.Stage
             
            self.current_defocus.hardware_read_func = \
                self.wrapper.getDefocus
            self.current_defocus.hardware_set_func = \
                self.wrapper.setDefocus
                
            self.current_binning.hardware_read_func = \
                self.wrapper.getBinning
            self.current_binning.hardware_set_func = \
                self.wrapper.setBinning  
            self.current_exposure.hardware_read_func = \
                self.wrapper.getExposure
            self.current_exposure.hardware_set_func = \
                self.wrapper.setExposure
            self.current_dwell.hardware_read_func = \
                self.wrapper.getDwellTime
            self.current_dwell.hardware_set_func = \
                self.wrapper.setDwellTime
             
            if self.wrapper.getMode() == 'TEM': self.temSetup()
            if self.wrapper.getMode() == 'STEM': self.stemSetup()
            
            self.read_from_hardware()

        else:
            if self.debug_mode.val: print "em_hardware: not connecting, dummy"
    #---------------------------------------------------------------------------
    def disconnect(self):
        #disconnect logged quantities from hardware
        for lq in self.logged_quantities.values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        self.wrapper = None 
     
    #---------------------------------------------------------------------------      
    def acquire(self):
        return self.wrapper.Acq.AcquireImages()
    
    #---------------------------------------------------------------------------      
    def setTemAcqVals(self,binning,exp):
        myCcdAcqParams = self.Acq.Cameras(0).AcqParams
        myCcdAcqParams.Binning = int(binning)
        myCcdAcqParams.ExposureTime = float(exp)
        myCcdAcqParams.ImageCorrection = self.wrapper.ACQIMAGECORRECTION_UNPROCESSED #this has to be unprocessed. Not sure if it affects data from the micoscope itself
        myCcdAcqParams.ImageSize = self.wrapper.ACQIMAGESIZE_FULL
        self.Acq.Cameras(0).AcqParams = myCcdAcqParams
        print '-----set TEM vals-----'

    #---------------------------------------------------------------------------
    def setStemAcqVals(self,binning,dwell):
        self.myStemAcqParams = self.Acq.Detectors.AcqParams
        self.myStemAcqParams.Binning = int(bin)
        self.myStemAcqParams.DwellTime = float(dwell)
        self.Acq.Detectors.AcqParams = self.myStemAcqParams
        print '-----set STEM vals-----'
        
    #---------------------------------------------------------------------------
    def stemSetup(self):
        self.mode = 'STEM'
        print 'em_hardware: stemSetup'
        self.Det = self.wrapper.Det
        
    #---------------------------------------------------------------------------
    def temSetup(self):
        self.mode = 'TEM'
        print 'em_hardware: temSetup'
        self.Cam = self.wrapper.Cam
        
    #---------------------------------------------------------------------------
    def setAlphaTilt(self,alpha):
        self.wrapper.setAlphaTilt(alpha)
        
    #---------------------------------------------------------------------------
    def getAlphaTilt(self):
        return self.wrapper.getAlphaTilt()
    
    #---------------------------------------------------------------------------
    def moveStageXY(self,x,y):
        self.wrapper.setStageXY(x,y)    
        
    #---------------------------------------------------------------------------  
    def getStageXY(self):
        return self.wrapper.getStageXY()
    
    #---------------------------------------------------------------------------
    def getBinnings(self):
        if self.mode == 'TEM': return self.Cam.Info.Binnings
        if self.mode == 'STEM': return self.Det.Info.Binnings
        
    #---------------------------------------------------------------------------
    def setDefocus(self,defocus):
        self.wrapper.setDefocus(defocus)
        
    #---------------------------------------------------------------------------
    def getDefocus(self):
        return self.wrapper.getDefocus
    #---------------------------------------------------------------------------


