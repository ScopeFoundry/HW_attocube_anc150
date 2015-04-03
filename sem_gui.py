import sys
from PySide import QtGui

from base_gui import BaseMicroscopeGUI

# Import Hardware Components
#from hardware_components.picoharp import PicoHarpHardwareComponent

# Import Measurement Components
#from measurement_components.powermeter_optimizer import PowerMeterOptimizerMeasurement
from measurement_components.SEM.sem_raster_singlescan import SemRasterSingleScan
from measurement_components.SEM.sem_raster_repscan import SemRasterRepScan
from hardware_components.SEM.sem_remcon import SEMRemCon
from hardware_components.SEM.sem_raster_scanner import SemRasterScanner


class SEMMicroscopeGUI(BaseMicroscopeGUI):
    
    ui_filename = "sem_gui.ui"
    
    def setup(self):
        #Add hardware components
        print "Adding Hardware Components"
        
        #self.picoharp_hc = self.add_hardware_component(PicoHarpHardwareComponent(self))

        #Add measurement components
        print "Create Measurement objects"
        #self.apd_optimizer_measure = self.add_measurement_component(APDOptimizerMeasurement(self))
        self.sem_raster_scanner=self.add_hardware_component(SemRasterScanner(self))
        self.sem_raster_singlescan = self.add_measurement_component(SemRasterSingleScan(self))
        self.sem_raster_repscan = self.add_measurement_component(SemRasterRepScan(self))
        self.sem_remcon=self.add_hardware_component(SEMRemCon(self))
        

        #Add additional logged quantities

        # Connect to custom gui



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("Example SEM Foundry Scope App")
    
    gui = SEMMicroscopeGUI()
    gui.show()

    sys.exit(app.exec_())