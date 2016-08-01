from ScopeFoundry import BaseMicroscopeApp
from auger_electron_analyzer import AugerElectronAnalyzerHC
from NIFPGA.Counter_DAC_VI_hc import Counter_DAC_FPGA_VI_HC
from auger_analyzer_channel_history import AugerAnalyzerChannelHistory
from auger_point_spectrum import AugerPointSpectrum
from analyzer_quad_optimizer import AugerQuadOptimizer
from sem_slowscan2d import SEMSlowScan
from auger_slow_map import AugerSlowMap
#from SEM.measurements.sem_raster_singlescan import SemRasterSingleScan
from SEM.hardware.sem_raster_scanner import SemRasterScanner
from SEM.hardware.sem_remcon import SEMRemCon

# SEM Hardware Components
from hardware_components.sem_singlechan_signal import SEMSingleChanSignal
from hardware_components.sem_dualchan_signal import SEMDualChanSignal
from hardware_components.sem_slowscan_vout import SEMSlowscanVoutStage

from SEM.measurements.sem_raster_scan import SemRasterScan

# SEM Measurement Components
#from SEM.sem_slowscan_single_chan import SEMSlowscanSingleChan


class AugerMicroscopeApp(BaseMicroscopeApp):
    
    name = 'AugerMicroscopeApp'
    
    def setup(self):
        
#         self.add_hardware_component(AugerElectronAnalyzerHC(self))
#         self.add_hardware_component(Counter_DAC_FPGA_VI_HC(self))
#         
#         self.add_hardware_component(SEMDualChanSignal(self))
#         self.add_hardware_component(SEMSingleChanSignal(self))
#         self.add_hardware_component(SEMSlowscanVoutStage(self)) 
#         
        self.add_hardware_component(SEMRemCon(self))
        self.add_hardware_component(SemRasterScanner(self))       
        
        self.add_measurement_component(SemRasterScan(self))
#         self.add_measurement_component(AugerAnalyzerChannelHistory(self))
#         self.add_measurement_component(AugerPointSpectrum(self))
#         self.add_measurement_component(AugerQuadOptimizer(self))
# 
#         #self.add_measurement_component(SEMSlowscanSingleChan(self))
#         self.add_measurement_component(SEMSlowScan(self))
#         self.add_measurement_component(AugerSlowMap(self))
#         #self.add_measurement_component(SemRasterSingleScan(self))
        

        self.ui.show()
        
        
if __name__ == '__main__':
    app = AugerMicroscopeApp([])
    app.exec_()
