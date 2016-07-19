from __future__ import division, print_function
from ScopeFoundry import Measurement, LQRange
import pyqtgraph as pg
import numpy as np
import time

class AugerPointSpectrum(Measurement):
    
    name = "AugerPointSpectrum"

    def setup(self):
        
        
        # settings
        lq_settings = dict(dtype=float, ro=False, vmin=0, vmax=2200, unit='V')
        self.settings.New('Energy_min', initial=0, **lq_settings)
        self.settings.New('Energy_max', initial=2000, **lq_settings)
        self.settings.New('Energy_step', **lq_settings)
        self.settings.New('Energy_num_steps', initial=10, dtype=int)
        S = self.settings
        
        self.energy_range = LQRange(S.Energy_min, S.Energy_max, 
                                    S.Energy_step, S.Energy_num_steps)
        
        
        
        self.graph_layout=pg.GraphicsLayoutWidget(border=(100,100,100))
        self.graph_layout.show()
        self.graph_layout.setWindowTitle("AugerPointSpectrum")
        
        self.plot = self.graph_layout.addPlot(title="AugerPointSpectrum")
        
        self.plot_lines = []
        for i in range(8):
            color = pg.intColor(i)
            plot_line = self.plot.plot([0], pen=color)
            self.plot_lines.append(plot_line)
        
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.plot.addItem(self.vLine)
        
    def run(self):
        print("="*80)

        
        self.e_analyzer = self.app.hardware['auger_electron_analyzer']
        self.counter_dac_hc = self.app.hardware['Counter_DAC_FPGA_VI_HC']
        
        #self.counter_dac = self.counter_dac_hc.FPGA
        #self.counter_dac = self.app.hardware['Counter_DAC_FPGA_VI'] #works!
        #self.counter = self.counter_dac_hc.counter_dac #doesn't work for whatever reasons!
        ## (I verified this in the ScopeFoundry console)
        self.counter_dac = self.counter_dac_hc.counter_dac        
        self.fpga = self.counter_dac.FPGA
        
        self.fpga.Stop_Fifo(0)
        remaining, buf = self.fpga.Read_Fifo(numberOfElements=0)
        #print("remaining", remaining, remaining%8)
        remaining, buf = self.fpga.Read_Fifo(numberOfElements=remaining)
        print("read after stop", remaining, len(buf))

        self.fpga.Start_Fifo(0)
        self.counter_dac.CtrFIFO(True)
        #self.counter_dac_hc.CtrFIFO(True)
        
        N = self.settings["Energy_num_steps"]
        self.chan_spectra = np.zeros((N, 8), dtype=float)
        
        for ii in range(N):
            if self.interrupt_measurement_called:
                break
            
            energy = self.energy_range.array[ii]
            self.e_analyzer.settings['KE'] = energy 
            
            time.sleep(0.1)

            remaining, buf = self.fpga.Read_Fifo(numberOfElements=0)
            read_elements = (remaining - (remaining % 8))
            remaining, buf = self.fpga.Read_Fifo(numberOfElements=read_elements)
            
            print('->', buf.shape, len(buf)/8)
            print('-->',  buf.reshape(-1,8).shape, buf.reshape(-1,8).mean(axis=0) ) #,  buf.reshape(-1,8))
            
            self.settings['progress'] = 100.*(ii/N)
        
            self.chan_spectra[ii, :] = buf.reshape(-1,8).mean(axis=0)
            
        self.fpga.Stop_Fifo(0)
        remaining, buf = self.fpga.Read_Fifo(numberOfElements=0)
        print("left in buffer after scan", remaining)

            
    def update_display(self):
        self.vLine.setPos(self.e_analyzer.settings['KE'])
            
        for i in range(8):
            self.plot_lines[i].setData(self.energy_range.array, 0*i + self.chan_spectra[:,i])
        self.app.qtapp.processEvents()
