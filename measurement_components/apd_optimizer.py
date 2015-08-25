from measurement import Measurement
import numpy as np
import pyqtgraph as pg
import time

class APDOptimizerMeasurement(Measurement):

    name = "apd_optimizer"

    ui_filename = "measurement_components/apd_optimizer.ui"

    def setup(self):        
        self.display_update_period = 0.1 #seconds

        self.OPTIMIZE_HISTORY_LEN = 500

        self.optimize_history = np.zeros(self.OPTIMIZE_HISTORY_LEN, dtype=np.float)        
        self.optimize_ii = 0

        #connect events
        self.gui.ui.apd_optimize_startstop_checkBox.stateChanged.connect(self.start_stop)
        self.measurement_state_changed[bool].connect(self.gui.ui.apd_optimize_startstop_checkBox.setChecked)
        
        self.ui.start_pushButton.clicked.connect(self.start)
        self.ui.interrupt_pushButton.clicked.connect(self.interrupt)
        self.gui.apd_counter_hc.int_time.connect_bidir_to_widget(self.ui.int_time_doubleSpinBox)

    def setup_figure(self):
        # APD Optimize Figure ########################
        self.fig_opt = self.gui.add_figure('opt', self.gui.ui.plot_optimize_widget)
        self.fig_opt.clf()
        
        self.ax_opt = self.fig_opt.add_subplot(111)
        
        self.optimize_ii = 0
        self.optimize_line, = self.ax_opt.plot(self.optimize_history)
        self.optimize_current_pos = self.ax_opt.axvline(self.optimize_ii, color='r')
        
        # ui window
        if hasattr(self, 'graph_layout'):
            self.graph_layout.deleteLater() # see http://stackoverflow.com/questions/9899409/pyside-removing-a-widget-from-a-layout
            del self.graph_layout
        self.graph_layout=pg.GraphicsLayoutWidget(border=(100,100,100))
        self.ui.plot_groupBox.layout().addWidget(self.graph_layout)


        self.graph_layout.addLabel('Long Vertical Label', angle=-90, rowspan=3)
        
        ## Add 3 plots into the first row (automatic position)
        self.p1 = self.graph_layout.addPlot(title="APD Optimizer")

        self.optimize_plot_line = self.p1.plot([1,3,2,4,3,5])




    def _run(self):
        self.display_update_period = 0.001 #seconds

        self.apd_counter_hc = self.gui.apd_counter_hc
        self.apd_count_rate = self.apd_counter_hc.apd_count_rate

        self.SAVE_DATA = True # TODO convert to LoggedQuantity

        if self.SAVE_DATA:
            self.full_optimize_history = []
            self.full_optimize_history_time = []
            self.t0 = time.time()

        while not self.interrupt_measurement_called:
            self.optimize_ii += 1
            self.optimize_ii %= self.OPTIMIZE_HISTORY_LEN

            self.apd_count_rate.read_from_hardware()            
            self.optimize_history[self.optimize_ii] = self.apd_count_rate.val    
            
            if self.SAVE_DATA:
                self.full_optimize_history.append(self.apd_count_rate.val  )
                self.full_optimize_history_time.append(time.time() - self.t0)
            # test code
            #time.sleep(0.001)
            #self.optimize_history[self.optimize_ii] = random.random()    
        
        #save data afterwards
        if self.SAVE_DATA:
            #save  data file
            save_dict = {
                     'optimize_history': self.full_optimize_history,
                     'optimize_history_time': self.full_optimize_history_time,
                        }               
                    
            for lqname,lq in self.gui.logged_quantities.items():
                save_dict[lqname] = lq.val
            
            for hc in self.gui.hardware_components.values():
                for lqname,lq in hc.logged_quantities.items():
                    save_dict[hc.name + "_" + lqname] = lq.val
            
            for lqname,lq in self.logged_quantities.items():
                save_dict[self.name +"_"+ lqname] = lq.val
    
            self.fname = "%i_%s.npz" % (time.time(), self.name)
            np.savez_compressed(self.fname, **save_dict)
            print self.name, "saved:", self.fname
            
            
        
        #is this right place to put this?
        self.measurement_state_changed.emit(False)
        if not self.interrupt_measurement_called:
            self.measurement_sucessfully_completed.emit()
        else:
            self.measurement_interrupted.emit()
    

    def update_display(self):        
        ii = self.optimize_ii
        #print "display update", ii, self.optimize_history[ii]

        """
        self.optimize_line.set_ydata(self.optimize_history)
        self.optimize_current_pos.set_xdata((ii,ii))
        if (ii % 2) == 0:
            self.ax_opt.relim()
            self.ax_opt.autoscale_view(scalex=False, scaley=True)
        
        self.fig_opt.canvas.draw()
        """
        # pyqtgraph
        #self.p1.plot(self.optimize_history)
        self.optimize_plot_line.setData(self.optimize_history)
        self.gui.app.processEvents()

        
