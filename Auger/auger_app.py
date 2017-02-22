from ScopeFoundry import BaseMicroscopeApp
#from auger_electron_analyzer import AugerElectronAnalyzerHC
#from NIFPGA.Counter_DAC_VI_hc import Counter_DAC_FPGA_VI_HC
#from auger_point_spectrum import AugerPointSpectrum
#from analyzer_quad_optimizer import AugerQuadOptimizer

#from auger_slow_map import AugerSlowMap

#from Auger.hardware.ion_gun import PhiIonGunHardwareComponent
#from Auger.measurement.ion_gun import IonGunStatus

#from SEM.measurements.sem_raster_singlescan import SemRasterSingleScan
#from SEM.hardware.sem_raster_scanner import SemRasterScanner
#from SEM.hardware.sem_remcon import SEMRemCon


#from SEM.measurements.sem_raster_scan import SemRasterScan
#from Auger.sem_sync_raster_measure import SemSyncRasterScan
#from Auger.auger_sync_scan import AugerSyncScan

# SEM Measurement Components
#from SEM.sem_slowscan_single_chan import SEMSlowscanSingleChan

import logging
logging.basicConfig(level='DEBUG')
logging.getLogger('').setLevel(logging.DEBUG)
logging.getLogger("ipykernel").setLevel(logging.WARNING)
logging.getLogger('PyQt4').setLevel(logging.WARNING)
logging.getLogger('ScopeFoundry.logged_quantity.LoggedQuantity').setLevel(logging.WARNING)

class AugerMicroscopeApp(BaseMicroscopeApp):
    
    name = 'AugerMicroscopeApp'
    
    def setup(self):
        
#        self.add_hardware_component(AugerElectronAnalyzerHC(self))
#        self.add_hardware_component(Counter_DAC_FPGA_VI_HC(self))
         
        # SEM Hardware Components
        from Auger.NIFPGA.ext_trig_auger_fpga_hw import AugerFPGA_HW
        self.add_hardware(AugerFPGA_HW(self))

        
        #from ScopeFoundryHW.sem_analog.sem_singlechan_signal import SEMSingleChanSignal
        #self.add_hardware_component(SEMSingleChanSignal(self))
        from ScopeFoundryHW.sem_analog.sem_dualchan_signal import SEMDualChanSignal
        self.add_hardware_component(SEMDualChanSignal(self))
        from ScopeFoundryHW.sem_analog.sem_slowscan_vout import SEMSlowscanVoutStage
        self.add_hardware_component(SEMSlowscanVoutStage(self)) 
         
        ##self.add_hardware_component(SEMRemCon(self))
        #self.add_hardware_component(SemRasterScanner(self))       
        from Auger.sem_sync_raster_hardware import SemSyncRasterDAQ
        self.add_hardware_component(SemSyncRasterDAQ(self))
        

        
        #self.add_measurement_component(SemRasterScan(self))
        from Auger.auger_analyzer_channel_history import AugerAnalyzerChannelHistory
        self.add_measurement_component(AugerAnalyzerChannelHistory(self))
#        self.add_measurement_component(AugerPointSpectrum(self))
#        self.add_measurement_component(AugerQuadOptimizer(self))
 
        #self.add_measurement_component(SEMSlowscanSingleChan(self))
        from Auger.sem_slowscan2d import SEMSlowScan
        self.add_measurement_component(SEMSlowScan(self))
#        self.add_measurement_component(AugerSlowMap(self))
        from Auger.sem_sync_raster_measure import SemSyncRasterScan
        self.add_measurement_component(SemSyncRasterScan(self))
#        self.add_measurement_component(AugerSyncScan(self))


#        self.phi_ion_gun = self.add_hardware_component(PhiIonGunHardwareComponent(self))
#        self.ion_gun_status = self.add_measurement_component(IonGunStatus(self))



        self.settings_load_ini('auger_fast_scan_settings.ini')

        self.ui.show()
        
        
if __name__ == '__main__':
    app = AugerMicroscopeApp([])
    app.exec_()
