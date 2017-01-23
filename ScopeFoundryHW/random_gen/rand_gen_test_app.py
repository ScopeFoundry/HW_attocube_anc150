'''
Created on Jan 11, 2017

@author: Alan Buckley, Ed Barnard
'''

from ScopeFoundry.base_app import BaseMicroscopeApp
#from ScopeFoundry.helper_funcs import sibling_path, load_qt_ui_file

class RandomGenTestMicroscopeApp(BaseMicroscopeApp):
    
    name = 'random_gen_test_microscope'
    
    def setup(self):
        # Order ScopeFoundry to load your hardware module.
        
        from ScopeFoundryHW.random_gen.rand_gen_hw import RandomNumberGenHW
        self.add_hardware_component(RandomNumberGenHW(self))
        
        
        # Order ScopeFoundry to load your measurement module.
        
        from ScopeFoundryHW.random_gen.rand_gen_measure import RandomNumberGenOptimizerMeasure
        self.rand_measure = self.add_measurement_component(RandomNumberGenOptimizerMeasure(self))
        
        from ScopeFoundryHW.random_gen.sine_wave_measure import SineWaveOptimizerMeasure
        self.sine_measure = self.add_measurement_component(SineWaveOptimizerMeasure(self))

        #self.side_ui_filename = sibling_path(__file__, "test_quickbar.ui")        
        #self.add_quickbar( load_qt_ui_file(self.side_ui_filename) )

        # Initialize ui
        self.ui.show()
        self.ui.activateWindow()
        
        
if __name__ == '__main__':
    
    import sys
    app = RandomGenTestMicroscopeApp(sys.argv)
    sys.exit(app.exec_())
    