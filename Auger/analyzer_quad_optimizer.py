from __future__ import division, print_function
from ScopeFoundry import Measurement
import pyqtgraph as pg
from PySide import QtGui
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
        self.settings.New('Quad_X1_Tol', initial=0.1, dtype=float, ro=False, unit='%', vmin=0)
        
        self.settings.New('Quad_Y1_Min', initial=-10, **lq_quad)
        self.settings.New('Quad_Y1_Max', initial=10, **lq_quad)
        self.settings.New('Quad_Y1_Tol', initial=0.1, dtype=float, ro=False, unit='%', vmin=0)
        
        self.settings.New('Max_Iterations', initial=5, dtype=int, ro=False, vmin=0)
        
        self.settings.New('Dwell_time', initial=0.05, dtype=float, ro=False, vmin=0, unit='s')
        
        # Required Hardware objects
        self.e_analyzer = self.app.hardware['auger_electron_analyzer']
        self.counter_dac_hc = self.app.hardware['Counter_DAC_FPGA_VI_HC']
        
        
    def setup_figure(self):
        
        self.ui = QtGui.QWidget()
        self.layout = QtGui.QGridLayout()
        self.ui.setLayout(self.layout)
        self.start_button= QtGui.QPushButton("Start")
        self.layout.addWidget(self.start_button)
        self.stop_button= QtGui.QPushButton("Stop")
        self.layout.addWidget(self.stop_button)
        
        self.start_button.clicked.connect(self.start)
        self.stop_button.clicked.connect(self.interrupt)
        
        
        quad_names = ['quad_'+x for x in ['X1', 'X2', 'Y1', 'Y2']]
        
        self.spinboxes = dict()
        for quad_name in quad_names:
            sb = self.spinboxes[quad_name] = QtGui.QDoubleSpinBox()
            self.e_analyzer.settings.get_lq(quad_name).connect_bidir_to_widget(sb)
            self.layout.addWidget(sb)
            
        self.graph_layout=pg.GraphicsLayoutWidget(border=(100,100,100))
        
        self.layout.addWidget(self.graph_layout)
        
        self.ui.show()
        self.ui.setWindowTitle("AugerQuadOptimizer")
        
        """## Create window with ImageView widget
        self.graph_layout = pg.ImageView()
        self.graph_layout.show()
        self.graph_layout.setWindowTitle('Quadrupole Optimization')"""
        
        # Plot view window
        labelStyle = {'color': '#A9A9A9', 'font-size': '11pt'}
        
        quad_labels = ['X1', 'X2', 'Y1', 'Y2']
        rows = [0, 1, 0, 1]
        cols = [0, 0, 1, 1]
        
        self.plots = {}
        self.plot_lines = {}
        self.axis_vert = {}
        self.axis_horz = {}
        self.plot_data = {}
        self.plot_horz = {}
        
        for ii in range(len(quad_labels)):
            ql = quad_labels[ii]
            self.plots[ql] = self.graph_layout.addPlot(title=ql + ' Optimizer',
                                                                    row=rows[ii],col=cols[ii])
            self.plot_lines[ql] = self.plots[ql].plot([0], pen=pg.intColor(ii))
            self.axis_vert[ql] = self.plots[ql].getAxis('left')
            self.axis_vert[ql].setLabel(text='Intensity (counts/s)', **labelStyle)
            self.axis_horz[ql] = self.plots[ql].getAxis('bottom')
            self.axis_horz[ql].setLabel(text=ql + ' Value (%)', **labelStyle)
            
            #Initialize data to be plotted
            self.plot_data[ql] = [0]
            self.plot_horz[ql] = [0]
        
    def run(self):
        print("="*80)

        

        
        #self.counter_dac = self.counter_dac_hc.fpga
        #self.counter_dac = self.app.hardware['Counter_DAC_self.fpga_VI'] #works!
        
        # Line Sampling Walk Maximization Algorithm: Three-Stage Optimization
        # Assumes x1/x2 and y1/y2 pair movements are independent of each other,
        # but optimum x1 depends on y1
        
        #Initialize xy
        x0 = (self.settings['Quad_X1_Max']+self.settings['Quad_X1_Min'])/2
        y0 = (self.settings['Quad_Y1_Max']+self.settings['Quad_Y1_Min'])/2
        numSteps = 20
        extents = (self.settings['Quad_X1_Max']-x0,
                    self.settings['Quad_Y1_Max']-y0)
        xTol = 0.5
        yTol = 0.5
        
        self.e_analyzer.settings['quad_X2'] = 0.
        self.e_analyzer.settings['quad_Y2'] = 0.
        time.sleep(0.015)
        
        dwell=self.settings['Dwell_time']
        
        self.counter_dac_hc.engage_FIFO()
        
        #Stage One: Find optimum at x2 = 0, y2 = 0
#         xy1 = self.line_sample_walk_2D(xy0, pStep, pExtents, xTol, yTol,
#                                        self.quad_intensity,
#                                        maxIter=self.settings['Max_Iterations'])
        xy1 = self.octopole_maximization_walk_2D(x0, y0, numSteps, extents, xTol, yTol, 
                                                 maxIter=self.settings['Max_Iterations'],
                                                 dwell=dwell)
        
        #Applying limits in case optimal values are outside the scope of
        #the octopole's movement
        if xy1[0] > 49:
            X1 = 49
            print('Optimal X1 > 49: X1 coerced to 49')
        elif xy1[0] < -49:
            X1 = -49
        else:
            X1 = xy1[0]
            
        if xy1[1] > 49:
            Y1 = 49
        elif xy1[1] < -49:
            Y1 = -49
        else:
            Y1 = xy1[1]

        print('Optimal X1/Y1:' + str(X1) + ', ' + str(Y1))

        #Stage Two: Move x1 and x2 as a pair until maximum is achieved
        
        
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
        
        self.opt_var = 'X2'
        
        if not(self.interrupt_measurement_called):
            octoMax= self.find_max_octopole_line(xMin, xMax, yMin, yMax, numSteps, dwell=dwell, consoleMode=False)
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
        
        self.opt_var = 'Y2'
        
        if not(self.interrupt_measurement_called):
            octo_optimal = self.find_max_octopole_line(xMin, xMax, yMin, yMax, numSteps, dwell=dwell, consoleMode=False)         
            
            if not(self.interrupt_measurement_called):
                print('Optimal Octo:' + str(octo_optimal))
                
                #Automatically set the quad to optimal
                self.e_analyzer.settings['quad_X1'] = octo_optimal[0]
                self.e_analyzer.settings['quad_X2'] = octo_optimal[1]
                self.e_analyzer.settings['quad_Y1'] = octo_optimal[2]
                self.e_analyzer.settings['quad_Y2'] = octo_optimal[3]
            
        else:
            print('Optimization Interrupted')
        
        self.counter_dac_hc.disengage_FIFO()
        
    ###################### OCTOPOLE ALIGNMENT FUNCTIONS #########################################    
    
    def octopole_maximization_walk_2D(self, x0, y0, numSteps, extents, xTol, yTol, maxIter = 10, dwell=0.05):
            
            x = x0
            y = y0
            
            fevs = 0
            for iMax in range(2*maxIter):
                
                if iMax%2 == 0:
                    #scan x-direction on even iterations (0, 2...)
                    self.opt_var = 'X1'
                    
                    #determine scan range
                    xMin = x - extents[0]
                    xMax = x + extents[0]
                    #apply limits
                    if xMax > 49:
                        xMax = 49
                    if xMin < -49:
                        xMin = -49
                    
                    yMin = yMax = y
                    
                    #store initial values for comparison
                    x0 = x
                    y0 = y
                else:
                    #then scan in y on odd (1, 3...)
                    self.opt_var = 'Y1'
                    
                    #determine scan range
                    yMin = y - extents[0]
                    yMax = y + extents[0]
                    #apply limits
                    if yMax > 49:
                        yMax = 49
                    if yMin < -49:
                        yMin = -49
                    
                    xMin = xMax = x
                
                octoMax, junk, junk2 = self.find_gauss_max_octopole_line((xMin,0), (xMax, 0), (yMin,0), (yMax,0), numSteps, dwell=dwell, consoleMode=False) 
                
                fevs += numSteps
                
                #Coerce optimal values to within octopole range of motion
                octoCoerced = []
                for ii in (0, 2):
                    octoCoerced.append(octoMax[ii])
                    if octoCoerced[-1] > 49:
                        octoCoerced[-1] = 49
                        print('Optimal value outside of octopole bounds: coerced to within range')
                    elif octoCoerced[-1] < -49:
                        octoCoerced[-1] = -49
                        print('Optimal value outside of octopole bounds: coerced to within range')
                
                x = octoCoerced[0]
                y = octoCoerced[1]
        
                if iMax%2 == 1:
                    resX = abs(x - x0)
                    resY = abs(y - y0)
                    print('Current Alignment: X = ' + str(x0) + ', Y = ' + str(y0))
                    print('Residuals: ' + str(resX) + ', ' + str(resY) + '\n')
                    if resX < xTol and resY < yTol:
                        print('Optimization completed in ' + str(fevs) + ' measurements!' + '\n')
                        return (x, y)
                        break
                
                if iMax == 2*maxIter-1:
                    print('Optimization Failed')
                    return (x, y)
    
    def scan_octopole_line(self, xMin, xMax, yMin, yMax, numSteps, dwell=0.1, consoleMode=True):
        #Scans the octopole along a line in 4D parameter space, X1, X2, Y1, Y2, and gives intensities.
        #xMin, xMax, yMin, and yMax are tuples, e.g. xMin = (x1Min, x2Min)
        #numSteps dictates how many points at which to take images
        varDict = {}
        varDict['X1'] = np.linspace(xMin[0],xMax[0],numSteps)
        varDict['X2'] = np.linspace(xMin[1],xMax[1],numSteps)
        varDict['Y1'] = np.linspace(yMin[0],yMax[0],numSteps)
        varDict['Y2'] = np.linspace(yMin[1],yMax[1],numSteps)
        
        out = np.zeros(numSteps)
        
        if consoleMode:
            self.counter_dac_hc.engage_FIFO()
        
        for iStep in range(numSteps):
            if self.interrupt_measurement_called:
                break
            
            quad_labels = ['X1', 'X2', 'Y1', 'Y2']
        
            for quad_label in quad_labels:
                self.e_analyzer.settings['quad_' + quad_label] = varDict[quad_label][iStep]

            time.sleep(0.015)
            
            self.counter_dac_hc.flush_FIFO()
            time.sleep(dwell)
            
            buf_reshaped = self.counter_dac_hc.read_FIFO()
            
            out[iStep] = np.sum(buf_reshaped[0:7,:])/dwell
            
            self.plot_data[self.opt_var] = out
            self.plot_horz[self.opt_var] = varDict[self.opt_var]
            
        
        if consoleMode:
            self.counter_dac_hc.disengage_FIFO()
        
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

    
    def gauss(self, x, mean, stdDev, area=1):
            return (area*(np.sqrt(2*np.pi)*stdDev)**-1 
            * np.exp(((x-mean)**2)/(-2*stdDev**2)))

    def residual(self, p, yData, xData, fun):
            return yData - fun(xData, p[0], p[1], p[2])
    
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
    
###################### OLD METHODS FOR 2D VISUALIZATION ######################################    
        
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
                
                time.sleep(0.015)
    
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
    
    def quad_intensity(self, x, y, dwell=0.04):
        #print((x, y))
        self.e_analyzer.settings['quad_X1'] = x
        self.e_analyzer.settings['quad_Y1'] = y
        time.sleep(0.015)
        
        self.counter_dac_hc.flush_FIFO()
        time.sleep(dwell)
    
        buf_reshaped = self.counter_dac_hc.read_FIFO()
        
        out = np.sum(buf_reshaped)
        
        #print(out)
        return out
 
####### FUNCTIONS TO RUN FROM CONSOLE FOR TESTING OCTOPOLE MOVEMENT SPEED ################ 
    
    def octopole_speed_test(self, consoleMode=True, numIter=20):
        #Initialize octopole positions at zero
        self.e_analyzer.settings['quad_X1'] = 0
        self.e_analyzer.settings['quad_X2'] = 0
        self.e_analyzer.settings['quad_Y1'] = 0
        self.e_analyzer.settings['quad_Y2'] = 0
        
        if consoleMode:
            self.counter_dac_hc.engage_FIFO()
        
        time_step = 0.001
        time_data = time_step*np.arange(1, 20, 1)
        
        #Test X1
        self.plot_horz_x1 = time_data
        self.plot_data_x1 = np.zeros(len(time_data))
        err_count = np.zeros(len(time_data))
        
        for jj in range(numIter):
            
            #print('Iteration: ' + str(jj))
            self.e_analyzer.settings['quad_X1'] = -50
            time.sleep(0.05)
            self.counter_dac_hc.flush_FIFO()
            
            self.e_analyzer.settings['quad_X1'] = 30
            err_count = 0
            for ii in range(len(time_data)):
                time.sleep(time_step)
                buf_reshaped, read_elements = self.counter_dac_hc.read_FIFO(return_read_elements=True)
                if read_elements == 0:
                    err_count[ii] += 1
                else:
                    counts = np.sum(np.mean(buf_reshaped[0:7,:],axis=1))
                    n = (ii + 1)  - err_count[ii]
                    self.plot_data_x1[ii] = ((n-1)*self.plot_data_x1[ii] + counts)/n
                print('Read elements: ' + str(read_elements))
           
            self.update_display()
        
        #Test Y1
        self.e_analyzer.settings['quad_X1'] = 0
        time.sleep(0.05)
        self.e_analyzer.settings['quad_Y1'] = -50
        time.sleep(0.05)
              
        self.plot_horz_y1 = time_data
        self.plot_data_y1 = np.zeros(len(time_data))
        
        for jj in range(numIter):
            
            #print('Iteration: ' + str(jj))
            self.e_analyzer.settings['quad_Y1'] = -50
            time.sleep(0.05)
            self.counter_dac_hc.flush_FIFO()
            
            self.e_analyzer.settings['quad_Y1'] = 30
            for ii in range(len(time_data)):
                time.sleep(time_step)
                buf_reshaped, read_elements = self.counter_dac_hc.read_FIFO(return_read_elements=True)
                counts = np.sum(np.mean(buf_reshaped[0:7,:],axis=1))
                self.plot_data_y1[ii] += counts
                #print('Read elements: ' + str(read_elements))
            
            self.update_display()
        
        #Test X2
        self.e_analyzer.settings['quad_Y1'] = 0
        time.sleep(0.05)
        self.e_analyzer.settings['quad_X2'] = -50
        time.sleep(0.05)
        
        self.plot_horz_x2 = time_data
        self.plot_data_x2 = np.zeros(len(time_data))
        
        for jj in range(numIter):
            
            #print('Iteration: ' + str(jj))
            self.e_analyzer.settings['quad_X2'] = -50
            time.sleep(0.05)
            self.counter_dac_hc.flush_FIFO()
            
            self.e_analyzer.settings['quad_X2'] = 30
            for ii in range(len(time_data)):
                time.sleep(time_step)
                buf_reshaped, read_elements = self.counter_dac_hc.read_FIFO(return_read_elements=True)
                counts = np.sum(np.mean(buf_reshaped[0:7,:],axis=1))
                self.plot_data_x2[ii] += counts
                #print('Read elements: ' + str(read_elements))
            
            self.update_display()
        
        #Test Y2
        self.e_analyzer.settings['quad_X2'] = 0
        time.sleep(0.05)
        self.e_analyzer.settings['quad_Y2'] = -50
        time.sleep(0.05)
        
        self.plot_horz_y2 = time_data
        self.plot_data_y2 = np.zeros(len(time_data))
        
        for jj in range(numIter):
            
            #print('Iteration: ' + str(jj))
            self.e_analyzer.settings['quad_Y2'] = -50
            time.sleep(0.05)
            self.counter_dac_hc.flush_FIFO()
            
            self.e_analyzer.settings['quad_Y2'] = 30
            for ii in range(len(time_data)):
                time.sleep(time_step)
                buf_reshaped, read_elements = self.counter_dac_hc.read_FIFO(return_read_elements=True)
                counts = np.sum(np.mean(buf_reshaped[0:7,:],axis=1))
                self.plot_data_y2[ii] += counts
                #print('Read elements: ' + str(read_elements))
            
            self.update_display()
        
        if consoleMode:
            self.counter_dac_hc.disengage_FIFO()
                            
    def octopole_speed_test2(self):

        quad_names = ['quad_'+x for x in ['X1', 'X2', 'Y1', 'Y2']]
        
        for quad_name in quad_names:
            self.e_analyzer.settings[quad_name] = 20
        
        time.sleep(0.1)
        self.counter_dac_hc.engage_FIFO()
        time.sleep(0.1)
        for quad_name in quad_names:
            self.e_analyzer.settings[quad_name] = 0
        time.sleep(0.1)

        buf = self.counter_dac_hc.read_FIFO()
        
        chan_hist_meas = self.app.measurements['AugerAnalyzerChannelHistory']

        for i in range(9):
            chan_hist_meas.plot_lines[i].setData(buf[i,:])

        chan_hist_meas.plot_lines[8].setData(buf[0:7,:].sum(axis=0))

        self.counter_dac_hc.disengage_FIFO()
        
        np.savetxt("octopole_speed_test2_{:d}.csv".format(int(time.time())), buf.T,  fmt='%i', delimiter=',')

    
            
    def update_display(self):
        ## Display the data
        
        quad_labels = ['X1', 'X2', 'Y1', 'Y2']
        
        for ql in quad_labels:
            self.plot_lines[ql].setData(self.plot_horz[ql], self.plot_data[ql])
        
        self.app.qtapp.processEvents()
