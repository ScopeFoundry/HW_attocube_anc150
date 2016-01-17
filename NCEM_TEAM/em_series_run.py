import sys
from PySide import QtGui

from base_gui import BaseMicroscopeGUI

# Import Hardware Components
from foundry_scope.hardware_components.em_hardware import EMHardwareComponent

# Import Measurement Components
from measurement_components.em_series import SeriesMeasurement

class EM_Acquisition(BaseMicroscopeGUI):

    ui_filename = "base_gui.ui"

    def setup(self):
        #Add hardware components
        print "Adding Hardware Components"
        self.add_hardware_component(EMHardwareComponent(self))

        #Add measurement components
        print "Create Measurement objects"
        self.add_measurement_component(SeriesMeasurement(self))

        #set some default logged quantities
        self.hardware_components['em_hardware'].debug_mode.update_value(True)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("EM Series Tool")

    gui = EM_Acquisition(app)
    gui.show()

    sys.exit(app.exec_())
