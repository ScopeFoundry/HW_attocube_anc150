import sys
from PySide import QtGui

from base_gui import BaseMicroscopeGUI

# Import Hardware Components
from hardware_components.apd_counter import APDCounterHardwareComponent

# Import Measurement Components
from measurement_components.apd_optimizer_simple import APDOptimizerMeasurement

class ExampleAPDMicroscopeGUI(BaseMicroscopeGUI):

    ui_filename = "base_gui.ui"

    def setup(self):
        #Add hardware components
        print "Adding Hardware Components"

        self.add_hardware_component(APDCounterHardwareComponent(self))

        #Add measurement components
        print "Create Measurement objects"
        self.add_measurement_component(APDOptimizerMeasurement(self))

        
        #set some default logged quantities
        self.hardware_components['apd_counter'].debug_mode.update_value(True)
        self.hardware_components['apd_counter'].dummy_mode.update_value(True)
        self.hardware_components['apd_counter'].connected.update_value(True)

        #Add additional logged quantities

        # Connect to custom gui



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("Example APD App")

    gui = ExampleAPDMicroscopeGUI(app)
    gui.show()

    sys.exit(app.exec_())
