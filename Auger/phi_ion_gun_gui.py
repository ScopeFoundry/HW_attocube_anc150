import sys
from PySide import QtGui

#There is an issue with import on certain systems. Works fine on PXI in 1211.
from ScopeFoundry.base_gui import BaseMicroscopeGUI  



# Import Hardware Components
from Auger.hardware.ion_gun import PhiIonGunHardwareComponent

# Import Measurement Components
from measurement.ion_gun import IonGunStatus

class PhiIonGunGUI(BaseMicroscopeGUI):
    """Class specifies which ui file to use and which hardware and measurement components 
    to load in :func:`setup()`
    """
    ui_filename = "../ScopeFoundry/base_gui.ui"

    def setup(self):
        """Loads hardware and measurement components into gui turning over control
        to the user in the form of a Graphical User Interface."""
        #Add hardware components
        print "Adding Hardware Components"

        self.phi_ion_gun = self.add_hardware_component(PhiIonGunHardwareComponent(self))

        #Add measurement components
        print "Create Measurement objects"
        
        self.ion_gun_status = self.add_measurement_component(IonGunStatus(self))

        
        #set some default logged quantities
        #self.hardware_components['apd_counter'].debug_mode.update_value(True)
        #self.hardware_components['apd_counter'].dummy_mode.update_value(True)
        #self.hardware_components['apd_counter'].connected.update_value(True)

        #self.hardware_components['phi_ion_gun'].debug_mode.update_value(True)
        #self.hardware_components['phi_ion_gun'].dummy_mode.update_value(True)
        #self.hardware_components['phi_ion_gun'].connected.update_value(True)

        #Add additional logged quantities

        # Connect to custom gui



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("Phi Ion Gun App")

    gui = PhiIonGunGUI(app)
    gui.show()

    sys.exit(app.exec_())
