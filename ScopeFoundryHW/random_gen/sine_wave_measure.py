'''
Created on Jan 20, 2017

@author: lab
'''

from ScopeFoundry import Measurement
from ScopeFoundry.helper_funcs import sibling_path, load_qt_ui_file
import pyqtgraph as pg
import numpy as np
import time

class SineWaveOptimizerMeasure(Measurement):
    
    name = "sine_wave_optimizer"

    def __init__(self, app):
        
        self.ui_filename = sibling_path(__file__, "sine_gen.ui")
        
        self.ui = load_qt_ui_file(self.ui_filename)
        
        self.ui.setWindowTitle(self.name)
        
        Measurement.__init__(self, app)
        
    def setup(self):
        self.buffer = np.zeros((120))
        
        self.display_update_period = 0.1
        
        self.randgen = self.app.hardware.random_gen
        
        self.graph_layout = pg.GraphicsLayoutWidget(border=(100,100,100))
        self.ui.plot_groupBox.layout().addWidget(self.graph_layout)
        
        self.plot = self.graph_layout.addPlot(title="Sine Wave Generator")
        self.optimize_plot_line = self.plot.plot([0])
    
    def update_display(self):
        self.optimize_plot_line.setData(self.buffer)
        
    def run(self):
        for i in range(np.size(self.buffer)):
            self.buffer[i] = self.randgen.settings.sine_data.read_from_hardware()
            time.sleep(0.1)
            if self.interrupt_measurement_called:
                break
            
            
            