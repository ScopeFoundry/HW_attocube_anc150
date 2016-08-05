import sys
from PySide import QtGui

from ScopeFoundry import BaseMicroscopeApp


# Import Hardware Components
from hardware_components.apd_counter import APDCounterHardwareComponent
#from hardware_components.dummy_xy_stage import DummyXYStage
from hardware_components.picam import PicamHardware
from hardware_components.mcl_xyz_stage import MclXYZStage
from hardware_components.apd_counter import APDCounterHardwareComponent

# Import Measurement Components
from measurement_components.apd_optimizer_simple import APDOptimizerMeasurement
from measurement_components.simple_xy_scan import SimpleXYScan
from measurement_components.picam_readout import PicamReadout
from hardware_components.acton_spec import ActonSpectrometerHardwareComponent

class M3MicroscopeApp(BaseMicroscopeApp):

    name = "M3_Microscope"

    #ui_filename = "base_gui.ui"

    def setup(self):
        
        #Add hardware components
        print "Adding Hardware Components"
        #self.add_hardware_component(APDCounterHardwareComponent(self))
        #self.add_hardware_component(DummyXYStage(self))
        self.add_hardware_component(MclXYZStage(self))
        #self.add_hardware_component(PicamHardware(self))
        #self.add_hardware_component(ActonSpectrometerHardwareComponent(self))

        self.add_hardware_component(APDCounterHardwareComponent(self))

        #Add measurement components
        print "Create Measurement objects"
        self.add_measurement_component(APDOptimizerMeasurement(self))
        #self.add_measurement_component(SimpleXYScan(self))
        #self.add_measurement_component(PicamReadout(self))
                
        #set some default logged quantities
        #self.hardware_components['apd_counter'].debug_mode.update_value(True)
        #self.hardware_components['apd_counter'].dummy_mode.update_value(True)
        #self.hardware_components['apd_counter'].connected.update_value(True)


        #Add additional logged quantities

        # Connect to custom gui
        
        self.ui.show()
        self.ui.activateWindow()


if __name__ == '__main__':

    app = M3MicroscopeApp(sys.argv)
    
    sys.exit(app.exec_())