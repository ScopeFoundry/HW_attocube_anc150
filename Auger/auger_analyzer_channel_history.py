'''Ed Barnard, Alan Buckley'''

from __future__ import division
from ScopeFoundry import Measurement
import pyqtgraph as pg
import numpy as np
import time

class AugerAnalyzerChannelHistory(Measurement):
    
    name = "AugerAnalyzerChannelHistory"
    
   
    
    def setup(self):
        
        self.settings.New('chan_history_len', dtype=int, initial=5000,vmin=1)
        
        self.graph_layout=pg.GraphicsLayoutWidget(border=(100,100,100))
        self.graph_layout.show()
        self.graph_layout.setWindowTitle("AugerAnalyzerChannelHistory")
        
        self.plots = []
        for i in range(8):
            plot = self.graph_layout.addPlot(title="Channel %i" % i)
            self.graph_layout.nextRow()
            self.plots.append(plot)
            
        self.plot_lines = []
        for i in range(8):
            color = pg.intColor(i)
            plot_line = self.plots[i].plot([0], pen=color)
            self.plot_lines.append(plot_line)
        
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.plots[0].addItem(self.vLine)
        
        self.CHAN_HIST_LEN = 8000
        self.history_i = 0
        
    def run(self):
        print(self.name, 'run')
        
        self.counter_dac_hc = self.app.hardware['Counter_DAC_FPGA_VI']
        self.counter_dac = self.counter_dac_hc.counter_dac
        fpga = self.counter_dac.FPGA
        
        fpga.Start_Fifo(0)
        self.counter_dac.CtrFIFO(True)
        
        self.CHAN_HIST_LEN = self.settings['chan_history_len']
        
        self.chan_history = np.zeros( (8, self.CHAN_HIST_LEN) )
        self.chan_history_Hz = np.zeros( (8, self.CHAN_HIST_LEN) )
        
        self.history_i = 0
         
        while not self.interrupt_measurement_called:

            dwell_time = self.app.hardware['Counter_DAC_FPGA_VI'].settings['counter_ticks']/40e6

            #print(self.name, 'run')
            

            remaining, buf = fpga.Read_Fifo(numberOfElements=0)
            #print("remaining", remaining, remaining%8)
            read_elements = min((self.CHAN_HIST_LEN-1)*8, remaining - (remaining%8))
            remaining, buf = fpga.Read_Fifo(numberOfElements=read_elements)
            
            depth = (len(buf))/8

            if depth >0:
                #if (self.history_i + len(buf)) > (self.CHAN_HIST_LEN -1):
                #    print("history_i reset", len(buf))
                #    self.history_i = 0
                
                #_, newoffset = append_fifo_data_to_array(buf, self.history_i, self.chan_history)
                
                #chan_data = np.zeros((8,depth))
                buf_reshaped = buf.reshape((8,depth), order='F')
    
                #newoffset = self.history_i + depth
                #self.chan_history[:,self.history_i:newoffset] = buf_reshaped
                #self.chan_history_Hz[:,self.history_i:newoffset] = buf_reshaped / dwell_time
                
                ring_buf_index_array = (self.history_i + np.arange(depth, dtype=int)) % self.CHAN_HIST_LEN
                
                self.chan_history[:, ring_buf_index_array] = buf_reshaped
                self.chan_history_Hz[:,ring_buf_index_array] = buf_reshaped / dwell_time
                
                #self.history_i = newoffset 
                #self.history_i %= self.CHAN_HIST_LEN
                
                self.history_i = ring_buf_index_array[-1]
            
            time.sleep(0.1)
            

    def update_display(self):
        #print("chan_history shape", self.chan_history.shape)
        
        dwell_time = self.app.hardware['Counter_DAC_FPGA_VI'].settings['counter_ticks']/40e6
        
        self.vLine.setPos(self.history_i)
        for i in range(8):
            self.plot_lines[i].setData(self.chan_history_Hz[i,:])
        self.app.qtapp.processEvents()

        
def append_fifo_data_to_array(buff, col_offset, memory):
    
        #buf_read = np.array(buff)#function reads buffer object and 
        
        #separates elements into their respective rows and outputs an (8 x n) block
        
        #returns the integer depth of the block, then the data block itself.
    
        depth = (len(buff))/8
            
        chan_data = np.zeros((8,depth))
        
        for i in range(8):
            #reads every 8th element, places elements in their respective rows
            chan_data[i,:] = buff[i::8]
        #new_block = np.array(chan_data, dtype=int) #this data processing method also OK
        #depth = np.shape(new_block)[1] #this data processing method also OK
        memory[:,col_offset:col_offset+depth] = chan_data # new_block[:,:]
        col_offset += depth
        return memory, col_offset
