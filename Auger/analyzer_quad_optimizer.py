from __future__ import division, print_function
from ScopeFoundry import Measurement, LQRange
import pyqtgraph as pg
import numpy as np
import time
#import scipy
import scipy.optimize as opt

class AugerQuadOptimizer(Measurement):
    
    name = "AugerQuadOptimizer"

    def setup(self):
        
        #Settings for quad optimization over energy range
        lq_settings = dict(dtype=float, ro=False, vmin=0, vmax=2200, unit='V')
        self.settings.New('Energy_min', initial=0, **lq_settings)
        self.settings.New('Energy_max', initial=2000, **lq_settings)
        self.settings.New('Energy_step', **lq_settings)
        self.settings.New('Energy_num_steps', initial=10, dtype=int)
        S = self.settings
        
        self.energy_range = LQRange(S.Energy_min, S.Energy_max, 
                                    S.Energy_step, S.Energy_num_steps)
        
        ## Create window with ImageView widget
        self.graph_layout = pg.ImageView()
        self.graph_layout.show()
        self.graph_layout.setWindowTitle('Quadrupole Optimization')      
        
    def run(self):
        print("="*80)

        
        self.e_analyzer = self.app.hardware['auger_electron_analyzer']
        self.counter_dac_hc = self.app.hardware['Counter_DAC_FPGA_VI']
        
        #self.counter_dac = self.counter_dac_hc.FPGA
        #self.counter_dac = self.app.hardware['Counter_DAC_FPGA_VI'] #works!
        #self.counter = self.counter_dac_hc.counter_dac #doesn't work for whatever reasons!
        ## (I verified this in the ScopeFoundry console)
        self.counter_dac = self.counter_dac_hc.counter_dac        
        fpga = self.counter_dac.FPGA
        
        fpga.Stop_Fifo(0)
        remaining, buf = fpga.Read_Fifo(numberOfElements=0)
        #print("remaining", remaining, remaining%8)
        remaining, buf = fpga.Read_Fifo(numberOfElements=remaining)
        print("read ofter stop", remaining, len(buf))

        fpga.Start_Fifo(0)
        self.counter_dac.CtrFIFO(True)
        #self.counter_dac_hc.CtrFIFO(True)
        
        quad_vals = np.linspace(-10., 10., 10)
        N = len(quad_vals)
        self.chan_spectra = np.zeros((N, N, 8), dtype=float)
        self.summed_spectra = np.zeros((N, N), dtype=float)
        
        print(self.e_analyzer.settings['quad_X1'])
        self.e_analyzer.settings['quad_X1'] = quad_vals[0]
        
        print(self.e_analyzer.settings['quad_Y1'])
        self.e_analyzer.settings['quad_Y1'] = quad_vals[0]
        
        #Let the buffer run once to allow for system warm up(?)
        remaining, buf = fpga.Read_Fifo(numberOfElements=0)
        read_elements = (remaining - (remaining % 8))
        remaining, buf = fpga.Read_Fifo(numberOfElements=read_elements)
                
        print('->', buf.shape, len(buf)/8)
        print('-->',  buf.reshape(-1,8).shape, buf.reshape(-1,8).mean(axis=0) ) #,  buf.reshape(-1,8))
        
        time.sleep(0.1)
        
        #Try an optimization algorithm to minimize the quadrupole
        quad_optimal = opt.fmin(self.negative_quad_intensity, np.array((-1, 1)),
                               maxfun=50)
        
        print('Optimal Quad:' + str(quad_optimal))
        
        #Mapping method
        for ii in range(N):
            self.e_analyzer.settings['quad_X1'] = quad_vals[ii]
            for jj in range(N):
                if self.interrupt_measurement_called:
                    break
                
                self.e_analyzer.settings['quad_Y1'] = quad_vals[jj]
                
                time.sleep(0.1)
    
                remaining, buf = fpga.Read_Fifo(numberOfElements=0)
                read_elements = (remaining - (remaining % 8))
                remaining, buf = fpga.Read_Fifo(numberOfElements=read_elements)
                
                print('->', buf.shape, len(buf)/8)
                print('-->',  buf.reshape(-1,8).shape, buf.reshape(-1,8).mean(axis=0) ) #,  buf.reshape(-1,8))
                
                self.chan_spectra[ii, jj, :] = buf.reshape(-1,8).mean(axis=0)
                self.summed_spectra[ii, jj] = np.sum(self.chan_spectra[ii, jj, :])
                print(self.summed_spectra[ii, jj])
            
                self.settings['progress'] = 100.*((ii/N)+(jj/N**2))
        
        fpga.Stop_Fifo(0)
        remaining, buf = fpga.Read_Fifo(numberOfElements=0)
        print("left in buffer after scan", remaining)
        
        #Set the quad to the found optimum value
        max_ind = np.unravel_index(self.summed_spectra.argmax(), self.summed_spectra.shape)
        self.e_analyzer.settings['quad_X1'] = quad_vals[max_ind[0]]
        self.e_analyzer.settings['quad_Y1'] = quad_vals[max_ind[1]]
        
        #Generate the image (not sure how to update in real time yet)
        self.graph_layout.setImage(self.summed_spectra)
    
    def negative_quad_intensity(self, p):
        print(p)
        fpga = self.counter_dac.FPGA
        self.e_analyzer.settings['quad_X1'] = p[0]
        self.e_analyzer.settings['quad_Y1'] = p[1]
        
        time.sleep(0.1)
    
        remaining, buf = fpga.Read_Fifo(numberOfElements=0)
        read_elements = (remaining - (remaining % 8))
        remaining, buf = fpga.Read_Fifo(numberOfElements=read_elements)
                
        print('->', buf.shape, len(buf)/8)
        print('-->',  buf.reshape(-1,8).shape, buf.reshape(-1,8).mean(axis=0) ) #,  buf.reshape(-1,8))
        
        out = 0-np.sum(buf.reshape(-1,8).mean(axis=0))
        
        print(out)
        return out       
            
    def update_display(self):
        ## Display the data
        
        self.app.qtapp.processEvents()
