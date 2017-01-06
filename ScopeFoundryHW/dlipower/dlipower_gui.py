import sys
from PySide import QtGui

from ScopeFoundry import BaseMicroscopeApp

# Import Hardware Components
from dlipower_hardware import DLI_HardwareComponent


# Import Measurement Components
#from measurement_components.apd_optimizer_simple import APDOptimizerMeasurement

class DLI_Test_App(BaseMicroscopeApp):
    name = "DLI_Test_App"

    #ui_filename = "base_gui.ui"

    def setup(self):
        
        #Add hardware components
        print "Adding Hardware Components"
        self.add_hardware_component(DLI_HardwareComponent(self))
        #self.add_hardware_component(DummyXYStage(self))
        #self.add_hardware_component(MclXYZStage(self))
        #Add measurement components
        print "Create Measurement objects"
        #self.add_measurement_component(HiPMicroscopeDualTemperature(self))
                
        #set some default logged quantities
        #self.hardware_components['apd_counter'].debug_mode.update_value(True)
        #self.hardware_components['apd_counter'].dummy_mode.update_value(True)
        #self.hardware_components['apd_counter'].connected.update_value(True)


        #Add additional logged quantities

        # Connect to custom gui
        
        self.ui.show()
        self.ui.activateWindow()


if __name__ == '__main__':

    app = DLI_Test_App(sys.argv)
    
    sys.exit(app.exec_())