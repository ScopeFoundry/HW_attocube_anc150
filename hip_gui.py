import sys
from PySide import QtGui

from base_gui import BaseMicroscopeGUI

# Import Hardware Components
from hardware_components.apd_counter import APDCounterHardwareComponent
from hardware_components.dummy_xy_stage import DummyXYStage
from hardware_components.picam import PicamHardware
from hardware_components.mcl_xyz_stage import MclXYZStage

# Import Measurement Components
from measurement_components.apd_optimizer_simple import APDOptimizerMeasurement
from measurement_components.simple_xy_scan import SimpleXYScan
from measurement_components.picam_readout import PicamReadout
from hardware_components.acton_spec import ActonSpectrometerHardwareComponent


class HiPMicroscopeGUI(BaseMicroscopeGUI):

    ui_filename = "base_gui.ui"

    def setup(self):
        #Add hardware components
        print "Adding Hardware Components"
        #self.add_hardware_component(APDCounterHardwareComponent(self))
        #self.add_hardware_component(DummyXYStage(self))
        self.add_hardware_component(MclXYZStage(self))
        self.add_hardware_component(PicamHardware(self))
        self.add_hardware_component(ActonSpectrometerHardwareComponent(self))

        #Add measurement components
        print "Create Measurement objects"
        #self.add_measurement_component(APDOptimizerMeasurement(self))
        #self.add_measurement_component(SimpleXYScan(self))
        self.add_measurement_component(PicamReadout(self))
                
        #set some default logged quantities
        #self.hardware_components['apd_counter'].debug_mode.update_value(True)
        #self.hardware_components['apd_counter'].dummy_mode.update_value(True)
        #self.hardware_components['apd_counter'].connected.update_value(True)


        #Add additional logged quantities

        # Connect to custom gui


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("Example XY slowscan App")

    gui = HiPMicroscopeGUI(app)
    gui.show()

    sys.exit(app.exec_())
