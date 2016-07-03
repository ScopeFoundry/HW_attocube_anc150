from ScopeFoundry import BaseMicroscopeApp
from auger_electron_analyzer import AugerElectronAnalyzerHC
from NIFPGA.Counter_DAC_VI_hc import Counter_DAC_FPGA_VI_HC
from auger_analyzer_channel_history import AugerAnalyzerChannelHistory
from auger_point_spectrum import AugerPointSpectrum
from analyzer_quad_optimizer import AugerQuadOptimizer

class AugerMicroscopeApp(BaseMicroscopeApp):
    
    name = 'AugerMicroscopeApp'
    
    def setup(self):
        
        self.add_hardware_component(AugerElectronAnalyzerHC(self))
        self.add_hardware_component(Counter_DAC_FPGA_VI_HC(self))
        
        self.add_measurement_component(AugerAnalyzerChannelHistory(self))
        self.add_measurement_component(AugerPointSpectrum(self))
        self.add_measurement_component(AugerQuadOptimizer(self))

        self.ui.show()
        
        
if __name__ == '__main__':
    app = AugerMicroscopeApp([])
    app.exec_()
