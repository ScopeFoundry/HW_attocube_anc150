import sys
from PySide import QtGui

from ScopeFoundry import BaseMicroscopeGUI

# Import Hardware Components
from hardware_components.keithley_sourcemeter import KeithleySourceMeterComponent

# Import Measurement Components
from measurement_components.photocurrent_iv import PhotocurrentIVMeasurement


class IVelectricalGUI(BaseMicroscopeGUI):

    ui_filename = "ScopeFoundry/base_gui.ui"

    def setup(self):
        #Add hardware components
        print "Adding Hardware Components"
        self.keithley_sourcemeter_hc = self.add_hardware_component(KeithleySourceMeterComponent(self))

        #Add measurement components
        print "Create Measurement objects"
        self.iv_measure = self.add_measurement_component(PhotocurrentIVMeasurement(self))
                
        #set some default logged quantities
        #self.hardware_components['apd_counter'].debug_mode.update_value(True)
        #self.hardware_components['apd_counter'].dummy_mode.update_value(True)
        #self.hardware_components['apd_counter'].connected.update_value(True)


        #Add additional logged quantities

        # Connect to custom gui


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("IV App")

    gui = IVelectricalGUI(app)
    gui.show()

    sys.exit(app.exec_())
