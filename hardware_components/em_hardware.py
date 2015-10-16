from . import HardwareComponent
from equipment import NCEMscope

try:
    from equipment.NCEMscope import ScopeWrapper
except Exception as err:
    print "Cannot load required modules for em_hardware:", err


class EMHardwareComponent(HardwareComponent):

    def setup(self):
        self.debug = False
        self.name = "em_acquirer"

        # Create logged quantities
        self.current_defocus = self.add_logged_quantity(
                                name = 'current_defocus',
                                dtype = float, fmt="%e", ro=True,
                                unit="Nm",
                                vmin=None,vmax=None)
        self.current_binning = self.add_logged_quantity(
                                name = 'current_binning',
                                dtype = int, fmt="%e", ro=True,
                                unit=None,
                                vmin=None,vmax=None)
        self.current_exposure = self.add_logged_quantity(
                                name = 'current_exposure',
                                dtype = float, fmt="%e", ro=True,
                                unit="us",
                                vmin=None,vmax=None)
        self.current_dwell = self.add_logged_quantity(
                                name = 'current_dwell',
                                dtype = float, fmt="%e", ro=True,
                                unit="ns",
                                vmin=None,vmax=None)

        self.dummy_mode = self.add_logged_quantity(name='dummy_mode',
                            dtype=bool, initial=False, ro=False)

        # connect to gui
        try:
            self.current_binning.connect_bidir_to_widget(self.gui.ui.bin)
        except Exception as err:
            print "EMHardwareComponent: could not connect to custom GUI", err
        self.connect()
    def connect(self):        
        if not self.dummy_mode.val:
            if self.debug_mode.val: print "Connecting to Scope"
            self.wrapper = NCEMscope.ScopeWrapper(debug = self.debug_mode.val, mode='STEM')
            self.wrapper.Connect()
            self.Scope = self.wrapper.Scope
            self.Acq = self.wrapper.Acq
            self.Ill = self.wrapper.Ill
            self.Proj = self.wrapper.Proj
                        
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
            
        else:
            if self.debug_mode.val: print "Doing nothing (Dummy Mode)"

        # connect logged quantities

    def setup4Stem(self):
        self.wrapper.STEMMODE()
        print '-----set up for stem-----'
    def setup4Tem(self):
        self.wrapper.TEMMODE()
        print '-----set up for tem-----'
    def acquire(self):
        return self.wrapper.Acq.AcquireImages()
    def setTemAcqVals(self,binning,exposure):
        myCcdAcqParams = self.wrapper.Cam.AcqParams
        myCcdAcqParams.Binning = int(binning)
        myCcdAcqParams.ExposureTime = float(exposure)
        myCcdAcqParams.ImageCorrection = self.wrapper.ACQIMAGECORRECTION_UNPROCESSED #this has to be unprocessed. Not sure if it affects data from the micoscope itself
        myCcdAcqParams.ImageSize = self.wrapper.ACQIMAGESIZE_FULL  
        self.wrapper.Cam.AcqParams = myCcdAcqParams
        print '-----set TEM vals-----'
    def setStemAcqVals(self,binning,dwell):
        self.myStemAcqParams = self.Acq.Detectors.AcqParams
        self.myStemAcqParams.Binning = int(binning)
        self.myStemAcqParams.DwellTime = float(dwell)
        self.Acq.Detectors.AcqParams = self.myStemAcqParams
        print '-----set STEM vals-----'
    def disconnect(self):
        #disconnect logged quantities from hardware
        for lq in self.logged_quantities.values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        self.wrapper = None        

