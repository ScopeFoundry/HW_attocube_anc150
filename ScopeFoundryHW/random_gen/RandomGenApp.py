'''
Created on Jan 11, 2017

@author: Alan Buckley, Ed Barnard
'''

from ScopeFoundry.base_app import BaseMicroscopeApp
from ScopeFoundryHW.random_gen.rand_gen_measure import RandomNumberGenOptimizerMeasure
from ScopeFoundryHW.random_gen.rand_gen_hw import RandomNumberGenHW
from ScopeFoundryHW.random_gen.sine_wave_measure import SineWaveOptimizerMeasure
from ScopeFoundry.helper_funcs import sibling_path, load_qt_ui_file

class FancyMicroscopeApp(BaseMicroscopeApp):
    
    name = 'fancy_microscope'
    
    def setup(self):
        # Order ScopeFoundry to load your hardware module.
        self.add_hardware_component(RandomNumberGenHW(self))
        # Order ScopeFoundry to load your measurement module.
        self.rand_measure = self.add_measurement_component(RandomNumberGenOptimizerMeasure(self))
        self.sine_measure = self.add_measurement_component(SineWaveOptimizerMeasure(self))
        
        # Initialize ui.
        self.ui.show()
        self.ui.activateWindow()
        #self.ui.mdiArea.addSubWindow(self.rand_measure.ui)
        #self.ui.mdiArea.addSubWindow(self.sine_measure.ui)
        
        self.side_ui_filename = sibling_path(__file__, "df_sidepanel.ui")
        
        self.add_quickbar( load_qt_ui_file(self.side_ui_filename) )
        
        
if __name__ == '__main__':
    
    import sys
    app = FancyMicroscopeApp(sys.argv)
    sys.exit(app.exec_())
    