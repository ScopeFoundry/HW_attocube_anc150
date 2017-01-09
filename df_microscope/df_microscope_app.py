from __future__ import division, print_function
from ScopeFoundry import BaseMicroscopeApp

from hardware_components.apd_counter_usb import APDCounterUSBHW
from hardware_components.mcl_xyz_stage import MclXYZStage
from measurement_components.apd_confocal import APD_MCL_2DSlowScan
from measurement_components.apd_optimizer import APDOptimizerMeasurement

from hardware_components.winspec_remote_client import WinSpecRemoteClientHC
from winspec_remote_readout import WinSpecRemoteReadout
from winspec_remote_2Dscan import WinSpecMCL2DSlowScan

from hardware_components.power_wheel_arduino import PowerWheelArduinoHW

from hardware_components.thorlabs_powermeter import ThorlabsPowerMeterHW


from power_scan_df import PowerScanDF

class DFMicroscopeApp(BaseMicroscopeApp):

    name = 'DFMicroscopeApp'
    
    def setup(self):
        print("Adding Hardware Components")
        self.add_hardware_component(APDCounterUSBHW(self))
        #self.add_hardware_component(DummyXYStage(self))
        self.add_hardware_component(MclXYZStage(self))
        self.add_hardware_component(WinSpecRemoteClientHC(self))
        power_meter = self.add_hardware_component(ThorlabsPowerMeterHW(self))

        power_meter.settings['port'] = 'USB0::0x1313::0x8078::P0013111::INSTR'

        self.power_wheel = self.add_hardware_component(PowerWheelArduinoHW(self))

        self.power_wheel.settings['ser_port'] = 'COM5'

    
        print("Adding Measurement Components")
        self.add_measurement_component(APD_MCL_2DSlowScan(self))
        self.add_measurement_component(WinSpecRemoteReadout(self))
        self.add_measurement_component(WinSpecMCL2DSlowScan(self))
        self.add_measurement_component(APDOptimizerMeasurement(self))
        self.add_measurement_component(PowerScanDF(self))

        self.ui.show()
        self.ui.close()
        self.ui.show()

        #self.ui._raise()
        self.ui.activateWindow()
        
if __name__ == '__main__':
    import sys
    app = DFMicroscopeApp(sys.argv)
    sys.exit(app.exec_())