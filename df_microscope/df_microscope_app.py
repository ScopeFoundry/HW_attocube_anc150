from __future__ import division, print_function
from ScopeFoundry import BaseMicroscopeApp

from hardware_components.apd_counter import APDCounterHardwareComponent
from hardware_components.mcl_xyz_stage import MclXYZStage
from measurement_components.apd_confocal import APD_MCL_2DSlowScan

class DFMicroscopeApp(BaseMicroscopeApp):

    name = 'DFMicroscopeApp'
    
    def setup(self):
        print("Adding Hardware Components")
        self.add_hardware_component(APDCounterHardwareComponent(self))
        #self.add_hardware_component(DummyXYStage(self))
        self.add_hardware_component(MclXYZStage(self))
        
    
        print("Adding Measurement Components")
        self.add_measurement_component(APD_MCL_2DSlowScan(self))
        
        self.ui.show()
        self.ui.activateWindow()
        
if __name__ == '__main__':
    import sys
    app = DFMicroscopeApp(sys.argv)
    sys.exit(app.exec_())