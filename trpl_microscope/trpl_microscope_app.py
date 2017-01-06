from __future__ import division, print_function
from ScopeFoundry import BaseMicroscopeApp

from hardware_components.apd_counter_usb import APDCounterUSBHW

from hardware_components.picoharp import PicoHarpHardwareComponent
from hardware_components.apd_counter import APDCounterHardwareComponent
from hardware_components.andor_ccd import AndorCCDHW
from hardware_components.acton_spec import ActonSpectrometerHW
from hardware_components.flip_mirror import FlipMirrorHardwareComponent
from hardware_components.thorlabs_powermeter import ThorlabsPowerMeter
from hardware_components.thorlabs_powermeter_analog_readout import ThorlabsPowerMeterAnalogReadOut
from hardware_components.oceanoptics_spec import OceanOpticsSpectrometerHC
from hardware_components.mcl_xyz_stage import MclXYZStage
from hardware_components.keithley_sourcemeter import KeithleySourceMeterComponent
from hardware_components.srs_lockin import SRSLockinComponent
from hardware_components.thorlabs_optical_chopper import ThorlabsOpticalChopperComponent
from hardware_components.power_wheel_arduino import PowerWheelArduinoComponent
from hardware_components.crystaltech_aotf import CrystalTechAOTF
from hardware_components.shutter_servo_arduino import ShutterServoHardwareComponent

from measurement_components.apd_confocal import APD_MCL_2DSlowScan
from measurement_components.apd_optimizer import APDOptimizerMeasurement
from ScopeFoundry.helper_funcs import sibling_path, load_qt_ui_file

#from hardware_components.winspec_remote_client import WinSpecRemoteClientHC
#from winspec_remote_readout import WinSpecRemoteReadout
#from winspec_remote_2Dscan import WinSpecMCL2DSlowScan


class TRPLMicroscopeApp(BaseMicroscopeApp):

    name = 'TRPLMicroscopeApp'
    
    def setup(self):
        
        self.add_quickbar(load_qt_ui_file(sibling_path(__file__, 'trpl_quick_access.ui')))
        
        print("Adding Hardware Components")
        self.picoharp_hc = self.add_hardware_component(PicoHarpHardwareComponent(self))
        self.apd_counter_hc = self.add_hardware_component(APDCounterHardwareComponent(self))
        self.andor_ccd_hc = self.add_hardware_component(AndorCCDHW(self))
        self.acton_spec_hc = self.add_hardware_component(ActonSpectrometerHW(self))
        self.flip_mirror_hc = self.add_hardware_component(FlipMirrorHardwareComponent(self))
        self.thorlabs_powermeter_hc = self.add_hardware_component(ThorlabsPowerMeter(self))
        self.thorlabs_powermeter_analog_readout_hc = self.add_hardware_component(ThorlabsPowerMeterAnalogReadOut(self))
        self.mcl_xyz_stage_hc = self.add_hardware_component(MclXYZStage(self))
        self.keithley_sourcemeter_hc = self.add_hardware_component(KeithleySourceMeterComponent(self))
        self.srs_lockin_hc = self.add_hardware_component(SRSLockinComponent(self))  
        self.thorlabs_optical_chopper_hc = self.add_hardware_component(ThorlabsOpticalChopperComponent(self))        
        self.power_wheel_arduino_hc = self.add_hardware_component(PowerWheelArduinoComponent(self))    
        self.oceanoptics_spec_hc = self.add_hardware_component(OceanOpticsSpectrometerHC(self))
        self.crystaltech_aotf_hc = self.add_hardware_component(CrystalTechAOTF(self))
        self.shutter_servo_hc = self.add_hardware_component(ShutterServoHardwareComponent(self))


    
        print("Adding Measurement Components")
        self.apd_optimizer_measure = self.add_measurement_component(APDOptimizerMeasurement(self))        
        self.add_measurement_component(APD_MCL_2DSlowScan(self))
        
        
        #self.add_measurement_component(WinSpecRemoteReadout(self))
        #self.add_measurement_component(WinSpecMCL2DSlowScan(self))


        self.ui.show()
        self.ui.close()
        self.ui.show()

        #self.ui._raise()
        self.ui.activateWindow()
        
if __name__ == '__main__':
    import sys
    app = TRPLMicroscopeApp(sys.argv)
    sys.exit(app.exec_())