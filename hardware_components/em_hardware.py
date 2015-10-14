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
                                dtype = float, fmt="%e", ro=False,
                                unit="Nm",
                                vmin=None,vmax=None)
        self.current_binning = self.add_logged_quantity(
                                name = 'current_binning',
                                dtype = int, fmt="%e", ro=False,
                                unit=None,
                                vmin=None,vmax=None)
        self.exposure_time = self.add_logged_quantity(
                                name = 'exposure_time',
                                dtype = float, fmt="%e", ro=True,
                                unit="us",
                                vmin=None,vmax=None)
        self.dwell_time = self.add_logged_quantity(
                                name = 'dwell_time',
                                dtype = float, fmt="%e", ro=True,
                                unit="ns",
                                vmin=None,vmax=None)

        self.dummy_mode = self.add_logged_quantity(name='dummy_mode',
                            dtype=bool, initial=False, ro=False)
        

        # connect to gui
        try:
            self.current_binning.connect_bidir_to_widget(self.gui.ui.inBin)
        except Exception as err:
            print "EMHardwareComponent: could not connect to custom GUI", err
        self.connect()
    def connect(self):        
        if not self.dummy_mode.val:
            if self.debug_mode.val: print "Connecting to Scope (Dummy Mode)"
            self.wrapper = NCEMscope.ScopeWrapper(debug = self.debug_mode.val, mode='STEM')
            self.wrapper.Connect()
            self.Scope = self.wrapper.Scope
            self.TIA = self.wrapper.TIA
            self.Acq = self.wrapper.Acq
            self.Ill = self.wrapper.Ill
            self.Proj = self.wrapper.Proj
        else:
            if self.debug_mode.val: print "Connecting to Scope (Dummy Mode)"

        # connect logged quantities

    def setup4Stem(self):
        self.Acq.RemoveAllAcqDevices() #just to be sure....      
        self.detector0 = self.Acq.Detectors(0)
        self.Acq.AddAcqDevice(self.detector0)
        print '-----set up for stem-----'
    def setup4Tem(self):
        self.Acq.RemoveAllAcqDevices() #just to be sure....      
        self.camera0 = self.Acq.Cameras(0)
        self.Acq.AddAcqDevice(self.camera0)
        self.xPIX = self.camera0.Info.Width
        self.yPIX = self.camera0.Info.Height  
        print '-----set up for tem-----'
    def disconnect(self):
        #disconnect logged quantities from hardware
        for lq in self.logged_quantities.values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        self.wrapper = None        

