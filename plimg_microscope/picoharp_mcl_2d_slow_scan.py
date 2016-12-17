from measurement_components.mcl_stage_slowscan import MCLStage2DSlowScan

import numpy as np
import time
import pyqtgraph as pg
from PySide import QtGui
from ScopeFoundry.data_browser import DataBrowserView


class Picoharp_MCL_2DSlowScan(MCLStage2DSlowScan):
    
    name = 'Picoharp_MCL_2DSlowScan'
    
    def pre_scan_setup(self):
        #hardware 
        self.picoharp_hc = self.app.hardware['picoharp']
        ph = self.picoharp_hc.picoharp # low level hardware
        
        #scan specific setup
        
        # create data arrays
        
        cr0 = self.picoharp_hc.settings.count_rate0.read_from_hardware()
        rep_period_s = 1.0/cr0
        time_bin_resolution = self.picoharp_hc.settings['Resolution']*1e-12
        self.num_hist_chans = int(np.ceil(rep_period_s/time_bin_resolution))

        time_trace_map_shape = self.scan_shape + (self.num_hist_chans,)
        self.time_trace_map = np.zeros(time_trace_map_shape, dtype=float)
        self.time_trace_map_h5 = self.h5_meas_group.create_dataset('time_trace_map', 
                                                                   shape=time_trace_map_shape,
                                                                   dtype=float, 
                                                                   compression='gzip')
        
        self.time_array = self.h5_meas_group['time_array'] = ph.time_array[0:self.num_hist_chans]*1e-3
        self.elapsed_time = self.h5_meas_group['elapsed_time'] = np.zeros(self.scan_shape, dtype=float)
        
        #self.app.settings_auto_save()
        

        # pyqt graph
        self.initial_scan_setup_plotting = True


        # set up experiment
        # experimental parameters already connected via LoggedQuantities
        
        # open shutter 
        # self.gui.shutter_servo_hc.shutter_open.update_value(True)
        # time.sleep(0.5)
        

        
    def post_scan_cleanup(self):
        # close shutter 
        #self.gui.shutter_servo_hc.shutter_open.update_value(False)
        pass
    
    def collect_pixel(self, pixel_num, k, j, i):
        ph = self.picoharp_hc.picoharp
        
        # collect data
        print(pixel_num, k, j, i)
        t0 = time.time()
        
        ph.start_histogram()

        while not ph.check_done_scanning():
            if self.picoharp_hc.settings['Tacq'] > 200:
                ph.read_histogram_data()
            time.sleep(0.005) #self.sleep_time)  
        ph.stop_histogram()
        #ta = time.time()
        ph.read_histogram_data()

        print ph.histogram_data

        # store in arrays
        self.time_trace_map[k,j,i, :] = ph.histogram_data[0:self.num_hist_chans]
        self.time_trace_map_h5[k,j,i, :] = ph.histogram_data[0:self.num_hist_chans]
        
        print "asdf"
        self.elapsed_time[k,j,i] = ph.read_elapsed_meas_time()
        print "asdf2"

        # display count-rate
        self.display_image_map[k,j,i] = ph.histogram_data[0:self.num_hist_chans].sum() * 1.0/self.elapsed_time[k,j,i]
        
        print 'pixel done'
        
    def update_display(self):
        MCLStage2DSlowScan.update_display(self)
        
        # setup lifetime window
        if not hasattr(self, 'lifetime_graph_layout'):
            self.lifetime_graph_layout = pg.GraphicsLayoutWidget()
            self.lifetime_plot = self.lifetime_graph_layout.addPlot()
            self.lifetime_plotdata = self.lifetime_plot.plot()
            self.lifetime_plot.setLogMode(False, True)
        self.lifetime_graph_layout.show()
        
        kk, jj, ii = self.current_scan_index
        ph = self.picoharp_hc.picoharp
        self.lifetime_plotdata.setData(self.time_array,  1+ph.histogram_data[0:self.num_hist_chans])
        

import h5py

class Picoharp_MCL_2DSlowScan_View(DataBrowserView):
    
    name = 'Picoharp_MCL_2DSlowScan_View'
    
    def setup(self):
        
        self.ui = QtGui.QWidget()
        self.ui.setLayout(QtGui.QVBoxLayout())
        self.imview = pg.ImageView()
        self.imview.getView().invertY(False) # lower left origin
        self.ui.layout().addWidget(self.imview)
        self.graph_layout = pg.GraphicsLayoutWidget()
        self.ui.layout().addWidget(self.graph_layout)

        self.plot = self.graph_layout.addPlot()
        self.rect_plotdata = self.plot.plot()
        self.point_plotdata = self.plot.plot(pen=(0,9))
        
        
        # Rectangle ROI
        self.rect_roi = pg.RectROI([20, 20], [20, 20], pen=(0,9))
        self.rect_roi.addTranslateHandle((0.5,0.5))        
        self.imview.getView().addItem(self.rect_roi)        
        self.rect_roi.sigRegionChanged.connect(self.on_change_rect_roi)
        
        # Point ROI
        self.circ_roi = pg.CircleROI( (0,0), (2,2) , movable=True, pen=(0,9))
        #self.circ_roi.removeHandle(self.circ_roi.getHandles()[0])
        h = self.circ_roi.addTranslateHandle((0.5,.5))
        h.pen = pg.mkPen('r')
        h.update()
        self.imview.getView().addItem(self.circ_roi)
        self.circ_roi.removeHandle(0)
        self.circ_roi_plotline = pg.PlotCurveItem([0], pen=(0,9))
        self.imview.getView().addItem(self.circ_roi_plotline) 
        self.circ_roi.sigRegionChanged.connect(self.on_update_circ_roi)
        
        self.plot.setLogMode(False, True)
        
    def is_file_supported(self, fname):
        return "Picoharp_MCL_2DSlowScan.h5" in fname
    
    def on_change_data_filename(self, fname):

        try:
            self.dat = h5py.File(fname, 'r')
            self.time_trace_map = np.array(self.dat['/measurement/Picoharp_MCL_2DSlowScan/time_trace_map'])
            # pyqtgraph axes are x,y, but data is stored in (frame, y,x, time), so we need to transpose
            self.imview.setImage(self.time_trace_map[0].sum(axis=2).T)
        except Exception as err:
            self.imview.setImage(np.zeros((10,10)))
            self.databrowser.ui.statusbar.showMessage("failed to load %s:\n%s" %(fname, err))
            raise(err)
        
    def on_change_rect_roi(self):
        # pyqtgraph axes are x,y, but data is stored in (frame, y,x, time)
        roi_slice, roi_tr = self.rect_roi.getArraySlice(self.time_trace_map[0], self.imview.getImageItem(), axes=(1,0)) 
        
        print "roi_slice", roi_slice
        self.rect_plotdata.setData(self.time_trace_map[0,:,:,:][roi_slice].mean(axis=(0,1))+1)
        
    def on_update_circ_roi(self, roi):
        self.plot.setLogMode(False, True)

        roi_state = roi.saveState()
        #print roi_state
        #xc, y
        x0, y0 = roi_state['pos']
        xc = x0 + 1
        yc = y0 + 1
        
        
        # CHECK IF X, Y, I, J ARE SWAPPED!!!!
        
        Nframe, Ny, Nx, Nt = self.time_trace_map.shape 
        print 'Nframe, Ny, Nx, Nt', Nframe, Ny, Nx, Nt, 
        
        i = max(0, min(int(xc),  Nx-1))
        j = max(0, min(int(yc),  Ny-1))
        
        print "xc,yc,i,j", xc,yc, i,j
        
        self.circ_roi_plotline.setData([xc, i+0.5], [yc, j + 0.5])        
        
        self.point_plotdata.setData(self.time_trace_map[0,j,i,:] +1)
        

        