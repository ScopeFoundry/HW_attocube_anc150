from __future__ import print_function, absolute_import, division

from ScopeFoundry import BaseMicroscopeApp



# Import Hardware Components
#from hardware_components.apd_counter_usb import APDCounterUSBHardwareComponent
#from hardware_components.dummy_xy_stage import DummyXYStage
#from ScopeFoundryHW.picam.picam import PicamHardware

from measurement_components.apd_confocal import APD_MCL_2DSlowScan


# Import Measurement Components
from measurement_components.simple_xy_scan import SimpleXYScan
from measurement_components.picam_readout import PicamReadoutMeasure
from ScopeFoundryHW.acton_spec.acton_spec import ActonSpectrometerHW
from hardware_components.sem_slowscan_vout import SEMSlowscanVoutStage
from Auger.sem_slowscan2d import SEMVoutDelaySlowScan


from attocube_interface_measure import AttocubeInterface

#from pl_img_linescan import PLImgLineScan

from hardware_components.winspec_remote_client import WinSpecRemoteClientHC
from df_microscope.winspec_remote_readout import WinSpecRemoteReadout

from hardware_components.power_wheel_arduino import PowerWheelArduinoHW
from df_microscope.power_scan_df import PowerScanDF

from measurement_components.powermeter_optimizer_new import PowerMeterOptimizerMeasurement

from picoharp_mcl_2d_slow_scan import Picoharp_MCL_2DSlowScan
from df_microscope.winspec_remote_2Dscan import WinSpecMCL2DSlowScan


class M3MicroscopeApp(BaseMicroscopeApp):

    name = "M3_Microscope"

    def setup(self):
        
        #Add hardware components
        print("Adding Hardware Components")
        from ScopeFoundryHW.apd_counter.apd_counter import APDCounterHW
        self.add_hardware_component(APDCounterHW(self))
        #self.add_hardware_component(DummyXYStage(self))
        
        from ScopeFoundryHW.mcl_stage.mcl_xyz_stage import MclXYZStageHW
        self.add_hardware_component(MclXYZStageHW(self))
        
        self.add_hardware_component(SEMSlowscanVoutStage(self)) 
        
        from ScopeFoundryHW.picoharp import PicoHarpHW
        self.add_hardware_component(PicoHarpHW(self))
        
        
        self.add_hardware_component(WinSpecRemoteClientHC(self))
        
        from ScopeFoundryHW.ascom_camera.ascom_camera_hc import ASCOMCameraHW
        self.add_hardware_component(ASCOMCameraHW(self))
        
        self.add_hardware_component(PowerWheelArduinoHW(self))
        self.add_hardware_component(ThorlabsPowerMeterHW(self))

        from ScopeFoundryHW.attocube_ecc100.attocube_xy_stage import AttoCubeXYStageHW
        self.add_hardware_component(AttoCubeXYStageHW(self))

        from ScopeFoundryHW.thorlabs import ThorlabsPowerMeterHW
        
        #Add measurement components
        print("Create Measurement objects")
        from ScopeFoundryHW.apd_counter.measure.apd_optimizer_simple import APDOptimizerMeasure
        self.add_measurement_component(APDOptimizerMeasure(self))
        
        self.add_measurement_component(APD_MCL_2DSlowScan(self))
        
        self.add_measurement_component(SEMVoutDelaySlowScan(self))
        
        self.add_measurement_component(AttocubeInterface(self))
        self.add_measurement_component(PLImgLineScan(self))
        
        from ScopeFoundryHW.ascom_camera import ASCOMCameraCaptureMeasure
        self.add_measurement_component(ASCOMCameraCaptureMeasure(self))


        self.add_measurement_component(WinSpecRemoteReadout(self))

        self.add_measurement_component(PowerScanDF(self))
        self.add_measurement_component(PowerMeterOptimizerMeasurement(self))
        
        self.add_measurement_component(Picoharp_MCL_2DSlowScan(self))
        self.add_measurement_component(WinSpecMCL2DSlowScan(self))

        
        #set some default logged quantities
        #self.hardware_components['apd_counter'].debug_mode.update_value(True)
        
        #Add additional app-wide logged quantities
        # 
        
        # Connect to custom gui
        
        # show gui
        self.ui.show()
        self.ui.activateWindow()
        
        # load default settings from file
        self.settings_load_ini("m3_settings.ini")


if __name__ == '__main__':
    import sys

    app = M3MicroscopeApp(sys.argv)
    
    sys.exit(app.exec_())