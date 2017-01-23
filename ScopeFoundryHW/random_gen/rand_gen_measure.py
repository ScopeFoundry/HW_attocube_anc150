'''
Created on Jan 11, 2017

@author: lab
'''

from ScopeFoundry import Measurement
from ScopeFoundry.helper_funcs import sibling_path, load_qt_ui_file
import pyqtgraph as pg
import numpy as np
import time

class RandomNumberGenOptimizerMeasure(Measurement):
    
    name = "random_gen_optimizer"
    
    def __init__(self, app):
        
        # Define ui file to be used.
        self.ui_filename = sibling_path(__file__, "rand_gen_optimizer.ui")
        
        #Load ui file using ScopeFoundry helper function
        self.ui = load_qt_ui_file(self.ui_filename)
        
        # set Measurement UI window title
        self.ui.setWindowTitle(self.name)
        
        # Run super class Measurement init method.
        Measurement.__init__(self, app)
        
    def setup(self):
        # Create empty numpy array to serve as a buffer object.
        self.buffer = np.zeros((120))
        
        # Define how often to take update display
        self.display_update_period = 0.1 
        
        # Quick reference to the HardwareComponent
        self.randgen = self.app.hardware['random_gen']


    def setup_figure(self):
        # connect ui widgets to measurement settings or functions
        self.ui.start_pushButton.clicked.connect(self.start)
        self.ui.interrupt_pushButton.clicked.connect(self.interrupt)
        
        # Set up pyqtgraph graph_layout in the UI
        self.graph_layout=pg.GraphicsLayoutWidget(border=(100,100,100))
        self.ui.plot_groupBox.layout().addWidget(self.graph_layout)

        # Create PlotItem object (a set of axes)  
        self.plot = self.graph_layout.addPlot(title="Random Plot Generator")
        # Create PlotDataItem object ( a data set )
        self.optimize_plot_line = self.plot.plot([0])        

    
    def update_display(self):
        """Displays (plots) the numpy array self.buffer. 
        This function runs repeatedly and automatically during measurement routine.
        its update frequency is defined by self.display_update_period
        """
        self.optimize_plot_line.setData(self.buffer) 
    
    def run(self):
        """
        Runs when measurement is started. Runs in a separate thread from GUI.
        Will run forever until interrupt is called.
        """
        i = 0
        while not self.interrupt_measurement_called:
            i %= len(self.buffer)
            # Set progress bar
            self.settings['progress'] = i * 100./len(self.buffer)
            
            # Fills buffer (numpy array) with random values
            self.buffer[i] = self.randgen.settings.rand_data.read_from_hardware()
            # wait between readings (100ms)
            time.sleep(0.1)
            if self.interrupt_measurement_called:
                # Listen for interrupt_measurement_called flag.
                # This is critical to do, if you don't the measurement will
                # never stop.
                # The interrupt button is a polite request to the 
                # Measurement thread. We must periodically check for
                # an interrupt request
                break
            i += 1