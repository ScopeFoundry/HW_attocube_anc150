'''
Created on Oct 29, 2015

@author: NIuser
'''
import sys
from PySide import QtGui

from ScopeFoundry import BaseMicroscopeGUI


# Import Hardware Components
from hardware_components.sem_singlechan_signal import SEMSingleChanSignal
from hardware_components.sem_slowscan_vout import SEMSlowscanVout

# Import Measurement Components
#from measurement_components.apd_optimizer_simple import APDOptimizerMeasurement
from SEM.sem_slowscan_single_chan import SEMSlowscanSingleChan


class SEMSlowscanGUI(BaseMicroscopeGUI):

    ui_filename = "../ScopeFoundry/base_gui.ui"

    def setup(self):
        #Add hardware components
        print "Adding Hardware Components"
        self.add_hardware_component(SEMSingleChanSignal(self))
        self.add_hardware_component(SEMSlowscanVout(self))

        #Add measurement components
        print "Create Measurement objects"
        #self.add_measurement_component(APDOptimizerMeasurement(self))
        self.add_measurement_component(SEMSlowscanSingleChan(self))
        
        #set some default logged quantities
        #self.hardware_components['apd_counter'].debug_mode.update_value(True)
        #self.hardware_components['apd_counter'].dummy_mode.update_value(True)
        #self.hardware_components['apd_counter'].connected.update_value(True)

        #Add additional logged quantities

        # Connect to custom gui



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("Example XY slowscan App")

    gui = SEMSlowscanGUI(app)
    gui.show()

    sys.exit(app.exec_())
