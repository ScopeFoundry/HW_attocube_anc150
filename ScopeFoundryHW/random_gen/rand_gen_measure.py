'''
Created on Jan 11, 2017

@author: lab
'''

from ScopeFoundry import Measurement
from ScopeFoundry.helper_funcs import sibling_path, load_qt_ui_file
import pyqtgraph as pg
import numpy as np
import time
from ScopeFoundryHW.random_gen.random_gen_dev import RandomNumberGenDev

class RandomNumberGenOptimizerMeasure(Measurement):
    
    name = "random_gen_optimizer"
    
    def __init__(self, app):
        
        # Define ui file to be used.
        self.ui_filename = sibling_path(__file__, "rand_gen.ui")
        
        #Load ui file using ScopeFoundry helper function
        self.ui = load_qt_ui_file(self.ui_filename)
        
        # Do I really need to explain this one?
        self.ui.setWindowTitle(RandomNumberGenDev.name)
        
        # Run super class Measurement init method.
        Measurement.__init__(self, app)
        
    def setup(self):
        # Create empty numpy array to serve as a buffer object.
        self.buffer = np.zeros((120))
        
        # Definte how often to take measurements:
        self.display_update_period = 0.1 
        
        # Connect to hardware level module:
        self.randgen = self.app.hardware.random_gen
        
        # Set up graph_layout
        self.graph_layout=pg.GraphicsLayoutWidget(border=(100,100,100))
        self.ui.plot_groupBox.layout().addWidget(self.graph_layout)

        # Create PlotItem object
        self.plot = self.graph_layout.addPlot(title="Random Plot Generator")
        # Create PlotDataItem object
        self.optimize_plot_line = self.plot.plot([0])        

    
    def update_display(self):
        """Displays (plots) the numpy array self.buffer. This function runs repeatedly and automatically during measurement routine."""
        self.optimize_plot_line.setData(self.buffer) 
    
    def run(self):
        for i in range(np.size(self.buffer)):
            """Fills numpy array with random values"""
            self.buffer[i] = self.randgen.settings.y_data.read_from_hardware()
            time.sleep(0.1)
            if self.interrupt_measurement_called:
                """Listen for interrupt_measurement_called signal."""
                break
        
            