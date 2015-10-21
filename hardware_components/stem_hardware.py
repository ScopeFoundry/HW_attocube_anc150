from . import HardwareComponent
from equipment import NCEMscope

try:
    from equipment.NCEMscope import ScopeWrapper
except Exception as err:
    print "Cannot load required modules for em_hardware:", err

class STEMHardwareComponent(HardwareComponent):

    def setup(self):
        self.debug = True
        self.name = "stem_hardware"

        # Create logged quantities
        self.current_defocus = self.add_logged_quantity(
                                name = 'current_defocus',
                                dtype = float, fmt="%e", ro=True,
                                unit="Nm",
                                vmin=-100,vmax=100)
        self.current_binning = self.add_logged_quantity(
                                name = 'current_binning',
                                dtype = int, fmt="%e", ro=True,
                                unit=None,
                                vmin=1,vmax=None)
        self.current_dwell = self.add_logged_quantity(
                                name = 'current_dwell',
                                dtype = float, fmt="%e", ro=True,
                                unit="s",
                                vmin=0.01,vmax=100.0)

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
            if self.debug_mode.val: print "Connecting to Scope"
            self.wrapper = NCEMscope.ScopeWrapper(debug = self.debug_mode.val, mode='TEM')
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

            self.current_dwell.hardware_read_func = \
                self.wrapper.getDwellTime
            self.current_dwell.hardware_set_func = \
                self.wrapper.setDwellTime
            
        else:
            if self.debug_mode.val: print "Doing nothing (Dummy Mode)"

    def acquire(self):
        return self.wrapper.Acq.AcquireImages()

    def disconnect(self):
        #disconnect logged quantities from hardware
        for lq in self.logged_quantities.values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        self.wrapper = None        

