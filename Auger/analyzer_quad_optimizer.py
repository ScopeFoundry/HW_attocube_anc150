from __future__ import division, print_function
from ScopeFoundry import Measurement
import pyqtgraph as pg
import numpy as np
import time
import scipy.optimize as opt


class AugerQuadOptimizer(Measurement):
    
    name = "AugerQuadOptimizer"

    def setup(self):
        
        """#Settings for quad optimization over energy range
        lq_settings = dict(dtype=float, ro=False, vmin=0, vmax=2200, unit='V')
        self.settings.New('Energy_min', initial=0, **lq_settings)
        self.settings.New('Energy_max', initial=2000, **lq_settings)
        self.settings.New('Energy_step', **lq_settings)
        self.settings.New('Energy_num_steps', initial=10, dtype=int)
        S = self.settings
        
        self.energy_range = LQRange(S.Energy_min, S.Energy_max, 
                                    S.Energy_step, S.Energy_num_steps)"""
        
        #Settings for quad optimization parameters
        lq_quad = dict(dtype=float, ro=False, vmin=-50, vmax=50, unit='%')
        self.settings.New('Quad_X1_Min', initial=-10, **lq_quad)
        self.settings.New('Quad_X1_Max', initial=10, **lq_quad)
        self.settings.New('Quad_X1_Tol', initial=0.1, dtype=float, ro=False, unit='%')
        
        self.settings.New('Quad_Y1_Min', initial=-10, **lq_quad)
        self.settings.New('Quad_Y1_Max', initial=10, **lq_quad)
        self.settings.New('Quad_Y1_Tol', initial=0.1, dtype=float, ro=False, unit='%')
        
        self.settings.New('Max_Iterations', initial=5, dtype=int, ro=False)
        
        """## Create window with ImageView widget
        self.graph_layout = pg.ImageView()
        self.graph_layout.show()
        self.graph_layout.setWindowTitle('Quadrupole Optimization')"""
        
        # Plot view window
        self.graph_layout=pg.GraphicsLayoutWidget(border=(100,100,100))
        self.graph_layout.show()
        self.graph_layout.setWindowTitle("AugerQuadOptimizer")
        
        #X1 plot
        self.plot_x1 = self.graph_layout.addPlot(title="X1 Line Plot",
                                                 row=0,col=0)
        self.plot_line_x1 = self.plot_x1.plot([0], pen=pg.intColor(0))
        
        #Y1 plot
        self.plot_y1 = self.graph_layout.addPlot(title="Y1 Line Plot",
                                                 row=0,col=1)
        self.plot_line_y1 = self.plot_y1.plot([0], pen=pg.intColor(1))

        #X2 plot
        self.plot_x2 = self.graph_layout.addPlot(title="X1/X2 Pair Optimize",
                                                 row=1,col=0)
        self.plot_line_x2 = self.plot_x2.plot([0], pen=pg.intColor(2))

        #Y2 plot
        self.plot_y2 = self.graph_layout.addPlot(title="Y1/Y2 Pair Optimize",
                                                 row=1,col=1)
        self.plot_line_y2 = self.plot_y2.plot([0], pen=pg.intColor(3))           
        
        
    def run(self):
        print("="*80)

        
        self.e_analyzer = self.app.hardware['auger_electron_analyzer']
        
        #self.counter_dac = self.app.hardware['Counter_DAC_FPGA_VI']
        
        #self.counter_dac = self.counter_dac_hc.fpga
        #self.counter_dac = self.app.hardware['Counter_DAC_self.fpga_VI'] #works!
        
        # Line Sampling Walk Maximization Algorithm: Three-Stage Optimization
        # Assumes x1/x2 and y1/y2 pair movements are independent of each other,
        # but optimum x1 depends on y1
        
        #Initialize xy
        x0 = (self.settings['Quad_X1_Max']+self.settings['Quad_X1_Min'])/2
        y0 = (self.settings['Quad_Y1_Max']+self.settings['Quad_Y1_Min'])/2
        xy0 = (x0, y0)
        pStep = 1
        pExtents = (self.settings['Quad_X1_Max']-x0,
                    self.settings['Quad_Y1_Max']-y0)
        xTol = 0.5
        yTol = 0.5
        
        self.e_analyzer.settings['quad_X2'] = 0.
        self.e_analyzer.settings['quad_Y2'] = 0.
        
        #Initialize plot data
        self.plot_data_x1 = [0]
        self.plot_data_x2 = [0]
        self.plot_data_y1 = [0]
        self.plot_data_y2 = [0]
        
        #Initialize independent variables
        self.plot_horz_x1 = [0]
        self.plot_horz_x2 = [0]
        self.plot_horz_y1 = [0]
        self.plot_horz_y2 = [0]
        
        self.engage_FIFO()
        
        #Stage One: Find optimum at x2 = 0, y2 = 0
        xy1 = self.line_sample_walk_2D(xy0, pStep, pExtents, xTol, yTol,
                                       self.quad_intensity,
                                       maxIter=self.settings['Max_Iterations'])
        #Stage Two
#         quad_optimal = self.line_sample_walk_2D(xy1, 0.2, (1, 1), 
#                                                 self.settings['Quad_X1_Tol'],
#                                                 self.settings['Quad_Y1_Tol'], 
#                                                 self.quad_intensity,
#                                                 maxIter=self.settings['Max_Iterations']) 
        #Stage Two: Move x1 and x2 as a pair until maximum is achieved
        X1 = xy1[0]
        Y1 = xy1[1]
        print('Optimal X1/Y1:' + str(X1) + ', ' + str(Y1))
        
        #Determine limits to check based on coupling constant
        xCouple = -0.52  #x1/x2
        #Want to span entire x2 range if possible
        x2Min = -49
        x2Max = 49
        x1Min = xCouple*x2Min + X1
        x1Max = xCouple*x2Max + X1
        if x1Min < -49:
            x1Min = -49
            x2Min = (x1Min - X1)/xCouple
        if x1Max > 49:
            x1Max = 49
            x2Max = (x1Max - X1)/xCouple
        xMin = (x1Min, x2Min)
        xMax = (x1Max, x2Max)
        yMin = (Y1, 0)
        yMax = (Y1, 0)
        
        numSteps = 40
        
        self.opt_var = 'x2'
        
        if not(self.interrupt_measurement_called):
            octoMax= self.find_max_octopole_line(xMin, xMax, yMin, yMax, numSteps, dwell=0.15, consoleMode=False)
        else:
            octoMax = (X1, 0, Y1, 0)
        #Stage Three: Move y1 and y2 as a pair until maximum is achieved
        
        X1 = octoMax[0]
        X2 = octoMax[1]
        Y1 = octoMax[2]
        
        #Determine limits to check based on coupling constant
        yCouple = -0.52  #y1/y2
        #Want to span entire y2 range if possible
        y2Min = -49
        y2Max = 49
        y1Min = yCouple*y2Min + Y1
        y1Max = yCouple*y2Max + Y1
        if y1Min < -49:
            y1Min = -49
            y2Min = (y1Min - Y1)/yCouple
        if y1Max > 49:
            y1Max = 49
            y2Max = (y1Max - Y1)/yCouple
        yMin = (y1Min, y2Min)
        yMax = (y1Max, y2Max)
        xMin = (X1, X2)
        xMax = (X1, X2)
        
        numSteps = 40
        
        self.opt_var = 'y2'
        
        if not(self.interrupt_measurement_called):
            octo_optimal = self.find_max_octopole_line(xMin, xMax, yMin, yMax, numSteps, dwell=0.15, consoleMode=False)         
            
            if not(self.interrupt_measurement_called):
                print('Optimal Octo:' + str(octo_optimal))
                
                #Automatically set the quad to optimal
                self.e_analyzer.settings['quad_X1'] = octo_optimal[0]
                time.sleep(0.025)
                self.e_analyzer.settings['quad_X2'] = octo_optimal[1]
                time.sleep(0.025)
                self.e_analyzer.settings['quad_Y1'] = octo_optimal[2]
                time.sleep(0.025)
                self.e_analyzer.settings['quad_Y2'] = octo_optimal[3]
                time.sleep(0.025)
            
        else:
            print('Optimization Interrupted')
            self.disengage_FIFO()
        
        
    def flush_FIFO(self):   
        ## (I verified this in the ScopeFoundry console)
        self.counter_dac_hc = self.app.hardware['Counter_DAC_FPGA_VI_HC']
        self.counter_dac = self.counter_dac_hc.counter_dac
        self.fpga = self.counter_dac.FPGA
        
        #Let the buffer run once to allow for system warm up(?)
        remaining, buf = self.fpga.Read_Fifo(numberOfElements=0)
        read_elements = (remaining - (remaining % 8))
        remaining, buf = self.fpga.Read_Fifo(numberOfElements=read_elements)
                
        #print('->', buf.shape, len(buf)/8)
        #print('-->',  buf.reshape(-1,8).shape, buf.reshape(-1,8).mean(axis=0) ) #,  buf.reshape(-1,8))
    
    def engage_FIFO(self):
        ## (I verified this in the ScopeFoundry console)
        self.counter_dac_hc = self.app.hardware['Counter_DAC_FPGA_VI_HC']
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
        
        self.flush_FIFO()
        
        time.sleep(0.2)
        
        self.flush_FIFO()
        
    
    def disengage_FIFO(self):
        self.fpga.Stop_Fifo(0)
        remaining, buf = self.fpga.Read_Fifo(numberOfElements=0)
        print("left in buffer after scan", remaining)
        
    def gauss(self, x, mean, stdDev, area=1):
            return (area*(np.sqrt(2*np.pi)*stdDev)**-1 
            * np.exp(((x-mean)**2)/(-2*stdDev**2)))

    def residual(self, p, yData, xData, fun):
            return yData - fun(xData, p[0], p[1], p[2])

    def get_max_on_line_2D(self, pMin, pMax, pStep, q0, sampFun, qdir='y'):
            #p is the axis of maximization, q0 is the fixed value on the other axis
            #qdir is axis of q, e.g. 'x', 'y', 'z'.
            err = False
            p = np.arange(pMin,pMax,pStep)
            
            #Need to move octopole to initial position and then flush because
            #adjusting takes a finite amount of time!
            
            if qdir == 'y':
                x0 = pMin
                y0 = q0
            else:
                x0 = q0
                y0 = pMin
            
            self.e_analyzer.settings['quad_X1'] = x0
            time.sleep(0.025)
            self.e_analyzer.settings['quad_Y1'] = y0
            time.sleep(0.025)
            self.flush_FIFO()
            
            if qdir == 'y':
                pData = []
                for iP in range(len(p)):
                    if self.interrupt_measurement_called:
                        err = True
                        break
                    pData.append(sampFun(p[iP], q0))
                    self.plot_data_x1 = pData
                    self.plot_horz_x1 = p[0:len(pData)]
                if err:
                    return 'Error'
                else:
                    g0 = [(pMax+pMin)/2, 1, (pMax-pMin)*max(pData)]
                    gPars = opt.leastsq(self.residual, g0, args = (pData, p, self.gauss))
                    pMax = gPars[0][0]
                    return (pMax, q0)
            elif qdir == 'x':
                pData = []
                for iP in range(len(p)):
                    if self.interrupt_measurement_called:
                        err = True
                        break
                    pData.append(sampFun(q0, p[iP]))
                    self.plot_data_y1 = pData
                    self.plot_horz_y1 = p[0:len(pData)]
                if err:
                    return 'Error'
                else:
                    g0 = [(pMax+pMin)/2, 1, (pMax-pMin)*max(pData)]
                    gPars = opt.leastsq(self.residual, g0, args = (pData, p, self.gauss))
                    pMax = gPars[0][0]
                    print('Maximum Intensity = '
                          + str(self.gauss(pMax, gPars[0][0], gPars[0][1], gPars[0][2])))
                    return (q0, pMax)

    def line_sample_walk_2D(self, xy0, pStep, pExtents, xTol, yTol, sampFun, maxIter = 10):
            
            # Loop through fixed number of iterations of line maxima
            pq = xy0
            fevs = 0
            for iMax in range(2*maxIter):
                
        
                pInd = iMax % 2 #Switch average direction each iteration
                qInd = int(not(pInd)) #Switch fixed direction each iteration
                if qInd == 1:
                    qdir = 'y'
                    pq0 = pq #Store original pq position for comparison every other iteration
                else:
                    qdir = 'x'
        
                pMin = pq[pInd] - pExtents[pInd]
                pMax = pq[pInd] + pExtents[pInd]
        
                pq = self.get_max_on_line_2D(pMin, pMax, pStep, pq[qInd], sampFun, qdir)
                
                if type(pq)==type(''):
                    print('Optimization Interrupted')
                    return xy0
                    break
        
                fevs = fevs + len(np.arange(pMin, pMax, pStep))
        
                if qInd == 0:
                    resX = abs(pq[0] - pq0[0])
                    resY = abs(pq[1] - pq0[1])
                    print('Current Alignment: X = ' + str(pq[0]) + ', Y = ' + str(pq[1]))
                    print('Residuals: ' + str(resX) + ', ' + str(resY) + '\n')
                    if resX < xTol and resY < yTol:
                        print(pq)
                        print('Optimization completed in ' + str(fevs) + ' measurements!' + '\n')
                        return pq
                        break
                
                if iMax == 2*maxIter-1:
                    print('Optimization Failed')
                    return pq
        
    def map_quad_intensity(self, pMin, pMax, pStep, fpga):
        #Mapping Method
        quad_vals = np.arange(pMin, pMax, pStep)
        N = len(quad_vals)
        self.chan_spectra = np.zeros((N, N, 8), dtype=float)
        self.summed_spectra = np.zeros((N, N), dtype=float)
        
        print(self.e_analyzer.settings['quad_X1'])
        self.e_analyzer.settings['quad_X1'] = quad_vals[0]
        
        print(self.e_analyzer.settings['quad_Y1'])
        self.e_analyzer.settings['quad_Y1'] = quad_vals[0]
        
        #Loop over quad positions
        for ii in range(N):
            self.e_analyzer.settings['quad_X1'] = quad_vals[ii]
            for jj in range(N):
                if self.interrupt_measurement_called:
                    break
                
                self.e_analyzer.settings['quad_Y1'] = quad_vals[jj]
                
                time.sleep(0.1)
    
                remaining, buf = self.fpga.Read_Fifo(numberOfElements=0)
                read_elements = (remaining - (remaining % 8))
                remaining, buf = self.fpga.Read_Fifo(numberOfElements=read_elements)
                
                print('->', buf.shape, len(buf)/8)
                print('-->',  buf.reshape(-1,8).shape, buf.reshape(-1,8).mean(axis=0) ) #,  buf.reshape(-1,8))
                
                self.chan_spectra[ii, jj, :] = buf.reshape(-1,8).mean(axis=0)
                self.summed_spectra[ii, jj] = np.sum(self.chan_spectra[ii, jj, :])
                print(self.summed_spectra[ii, jj])
            
                self.settings['progress'] = 100.*((ii/N)+(jj/N**2))
        
        #Output the optimum value
        max_ind = np.unravel_index(self.summed_spectra.argmax(), self.summed_spectra.shape)
        return (quad_vals(max_ind[0]), quad_vals(max_ind[1]))
        #Generate the image (not sure how to update in real time yet)
        self.graph_layout.setImage(self.summed_spectra)
    
    def quad_intensity(self, x, y, dwell=0.05):
        #print((x, y))
        self.fpga = self.counter_dac.FPGA
        self.e_analyzer.settings['quad_X1'] = x
        time.sleep(dwell/2)
        self.e_analyzer.settings['quad_Y1'] = y
        time.sleep(dwell/2)
    
        remaining, buf = self.fpga.Read_Fifo(numberOfElements=0)
        read_elements = (remaining - (remaining % 8))
        remaining, buf = self.fpga.Read_Fifo(numberOfElements=read_elements)
                
        #print('->', buf.shape, len(buf)/8)
        #print('-->',  buf.reshape(-1,8).shape, buf.reshape(-1,8).mean(axis=0) ) #,  buf.reshape(-1,8))
        
        out = np.sum(buf.reshape(-1,8).mean(axis=0))
        
        #print(out)
        return out
    
    def scan_octopole_line(self, xMin, xMax, yMin, yMax, numSteps, dwell=0.1, consoleMode=True):
        #Scans the octopole along a line in 4D parameter space, X1, X2, Y1, Y2, and gives intensities.
        #xMin, xMax, yMin, and yMax are tuples, e.g. xMin = (x1Min, x2Min)
        #numSteps dictates how many points at which to take images
        X1 = np.linspace(xMin[0],xMax[0],numSteps)
        X2 = np.linspace(xMin[1],xMax[1],numSteps)
        Y1 = np.linspace(yMin[0],yMax[0],numSteps)
        Y2 = np.linspace(yMin[1],yMax[1],numSteps)
        
        out = np.zeros(numSteps)
        
        if consoleMode:
            self.engage_FIFO()
        
        for iStep in range(numSteps):
            if self.interrupt_measurement_called:
                break
            self.e_analyzer.settings['quad_X1'] = X1[iStep]
            time.sleep(dwell/4)
            self.e_analyzer.settings['quad_X2'] = X2[iStep]
            time.sleep(dwell/4)
            self.e_analyzer.settings['quad_Y1'] = Y1[iStep]
            time.sleep(dwell/4)
            self.e_analyzer.settings['quad_Y2'] = Y2[iStep]
            time.sleep(dwell/4)
            
            self.flush_FIFO()
            time.sleep(dwell)
            
            remaining, buf = self.fpga.Read_Fifo(numberOfElements=0)
            read_elements = (remaining - (remaining % 8))
            remaining, buf = self.fpga.Read_Fifo(numberOfElements=read_elements)
            
            out[iStep] = np.sum(buf.reshape(-1,8).mean(axis=0))
            
            if self.opt_var == 'x2':
                self.plot_data_x2 = out
                self.plot_horz_x2 = X2
            elif self.opt_var == 'y2':
                self.plot_data_y2 = out
                self.plot_horz_y2 = Y2
            
        
        if consoleMode:
            self.disengage_FIFO()
        
        return out
    
    def find_max_octopole_line(self, xMin, xMax, yMin, yMax, numSteps, dwell=0.1, consoleMode=True):
        #Scans the octopole along a line in 4D parameter space, X1, X2, Y1, Y2, fits a gaussian,
        #and gives the estimated location of maximum value.
        #xMin, xMax, yMin, and yMax are tuples, e.g. xMin = (x1Min, x2Min)
        #numSteps dictates how many points at which to take images
        X1 = np.linspace(xMin[0],xMax[0],numSteps)
        X2 = np.linspace(xMin[1],xMax[1],numSteps)
        Y1 = np.linspace(yMin[0],yMax[0],numSteps)
        Y2 = np.linspace(yMin[1],yMax[1],numSteps)
        
        #Get the data
        pData = self.scan_octopole_line(xMin, xMax, yMin, yMax, numSteps, dwell, consoleMode)
        pMax = np.argmax(pData)
        
        return (X1[pMax], X2[pMax], Y1[pMax], Y2[pMax])

    
    def find_gauss_max_octopole_line(self, xMin, xMax, yMin, yMax, numSteps, dwell=0.1, consoleMode=True):
        #Scans the octopole along a line in 4D parameter space, X1, X2, Y1, Y2, fits a gaussian,
        #and gives the estimated location of maximum value.
        #xMin, xMax, yMin, and yMax are tuples, e.g. xMin = (x1Min, x2Min)
        #numSteps dictates how many points at which to take images
        X1 = np.linspace(xMin[0],xMax[0],numSteps)
        X2 = np.linspace(xMin[1],xMax[1],numSteps)
        Y1 = np.linspace(yMin[0],yMax[0],numSteps)
        Y2 = np.linspace(yMin[1],yMax[1],numSteps)
        
        #p-space is parameterized distance along the line in terms of index
        p = np.arange(numSteps)
        pMax = numSteps-1
        pMin = 0
        
        #Get the data
        pData = self.scan_octopole_line(xMin, xMax, yMin, yMax, numSteps, dwell, consoleMode)
        
        #Make initial guess for gaussian at center of distribution
        g0 = [(pMax+pMin)/2, 1, (pMax-pMin)*max(pData)]
        
        gPars = opt.leastsq(self.residual, g0, args = (pData, p, self.gauss))
        pMax = gPars[0][0]
        
        #Convert back from parameter space to octopole space
        X1_max = X1[0] + (pMax/numSteps)*(X1[-1]-X1[0])
        X2_max = X2[0] + (pMax/numSteps)*(X2[-1]-X2[0])
        Y1_max = Y1[0] + (pMax/numSteps)*(Y1[-1]-Y1[0])
        Y2_max = Y2[0] + (pMax/numSteps)*(Y2[-1]-Y2[0])
        
        octoMax = (X1_max, X2_max, Y1_max, Y2_max)
        
        return octoMax, gPars[0], (p, pData)
            
    def update_display(self):
        ## Display the data
        
        self.plot_line_x1.setData(self.plot_horz_x1, self.plot_data_x1)
        self.plot_line_y1.setData(self.plot_horz_y1, self.plot_data_y1)
        self.plot_line_x2.setData(self.plot_horz_x2, self.plot_data_x2)
        self.plot_line_y2.setData(self.plot_horz_y2, self.plot_data_y2)

        
        self.app.qtapp.processEvents()
