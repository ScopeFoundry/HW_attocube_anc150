'''Ed Barnard, Alan Buckley'''

from __future__ import division
from ScopeFoundry import Measurement
from Auger.NIFPGA.Counter_DAC_VI_R2 import Counter_DAC_FPGA_VI
from PySide import QtGui
import pyqtgraph as pg
import numpy as np
import time

class AugerAnalyzerChannelHistory(Measurement):
    
    name = "AugerAnalyzerChannelHistory"
    
   
    
    def setup(self):
        
        self.settings.New('chan_history_len', dtype=int, initial=5000,vmin=1)
        
        self.ui = QtGui.QWidget()
        self.layout = QtGui.QGridLayout()
        self.ui.setLayout(self.layout)
        self.start_button= QtGui.QPushButton("Start")
        self.layout.addWidget(self.start_button)
        self.stop_button= QtGui.QPushButton("Stop")
        self.layout.addWidget(self.stop_button)
        
        self.start_button.clicked.connect(self.start)
        self.stop_button.clicked.connect(self.interrupt)
        
        
        self.graph_layout=pg.GraphicsLayoutWidget(border=(100,100,100))
        
        self.layout.addWidget(self.graph_layout)
        
        self.ui.show()
        self.ui.setWindowTitle("AugerAnalyzerChannelHistory")
        
        self.counter_dac_hc = self.app.hardware['Counter_DAC_FPGA_VI_HC']
        NUM_CHANS = self.counter_dac_hc.NUM_CHANS
        
        self.plots = []
        for i in range(NUM_CHANS):
            plot = self.graph_layout.addPlot(title="Channel %i" % i)
            self.graph_layout.nextRow()
            self.plots.append(plot)
            
        self.plot_lines = []
        for i in range(NUM_CHANS):
            color = pg.intColor(i)
            plot_line = self.plots[i].plot([0], pen=color)
            self.plot_lines.append(plot_line)
        
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.plots[0].addItem(self.vLine)
        
        self.CHAN_HIST_LEN = 8000
        self.history_i = 0
        
    def run(self):
        print(self.name, 'run')
        
        NUM_CHANS = self.counter_dac_hc.NUM_CHANS

        self.counter_dac_hc.engage_FIFO()
        
        self.CHAN_HIST_LEN = self.settings['chan_history_len']
        
        self.chan_history = np.zeros( (NUM_CHANS, self.CHAN_HIST_LEN), dtype=np.uint32 )
        self.chan_history_Hz = np.zeros( (NUM_CHANS, self.CHAN_HIST_LEN) )
        
        self.history_i = 0
         
        while not self.interrupt_measurement_called:

            self.dwell_time = self.app.hardware['Counter_DAC_FPGA_VI_HC'].settings['counter_ticks']/40e6

            buf_reshaped = self.counter_dac_hc.read_FIFO()
            
            depth = buf_reshaped.shape[1]

            if depth >0:
                
                ring_buf_index_array = (self.history_i + np.arange(depth, dtype=int)) % self.CHAN_HIST_LEN
                
                self.chan_history[:, ring_buf_index_array] = buf_reshaped
                self.chan_history_Hz[:,ring_buf_index_array] = buf_reshaped / self.dwell_time
                
                self.history_i = ring_buf_index_array[-1]
            
            time.sleep(0.1)
        
        self.counter_dac_hc.disengage_FIFO()
            
    def update_display(self):
        #print("chan_history shape", self.chan_history.shape)
        
        NUM_CHANS = self.counter_dac_hc.NUM_CHANS
        
        self.vLine.setPos(self.history_i)
        for i in range(NUM_CHANS-1):
            self.plot_lines[i].setData(self.chan_history_Hz[i,:])
        self.plot_lines[NUM_CHANS-1].setData(np.bitwise_and(self.chan_history[NUM_CHANS-1,:], 0x7FFFFFFF))
        
        self.app.qtapp.processEvents()
