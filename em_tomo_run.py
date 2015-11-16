import sys
from PySide import QtGui

from base_gui import BaseMicroscopeGUI

# Import Hardware Components
from foundry_scope.hardware_components.em_hardware import EMHardwareComponent

# Import Measurement Components
from measurement_components.em_tomo_series import EMTomographySeries

class EM_Acquisition(BaseMicroscopeGUI):

    ui_filename = "base_gui.ui"

    def setup(self):
        app.setWindowIcon(QtGui.QIcon('./icons/favicon.png'))

        #Add hardware components
        print "Adding Hardware Components"
        self.add_hardware_component(EMHardwareComponent(self))
        self.hardware = self.hardware_components['em_hardware']
        self.hardware.connected.update_value(True)
        self.hardware.current_binning.update_value(4)
        self.hardware.current_exposure.update_value(0.1)

        #Add measurement components
        print "Create Measurement objects"
        self.add_measurement_component(EMTomographySeries(self))
        self.hardware_components['em_hardware'].debug_mode.update_value(True)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("EM Tomo Series Tool")

    gui = EM_Acquisition(app)
    gui.show()

    sys.exit(app.exec_())
